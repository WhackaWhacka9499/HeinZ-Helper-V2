import base64
import ctypes
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
import winreg
from pathlib import Path

import psutil

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent


_CD_SINGLETON_NAME = "heinz_client_discovery_singleton"
_READYGO_EXACT_PREFIX = b"ReadyGo\x00\x05\x00\x00\x00"


def _load_module(name: str, file_path: Path):
    if file_path.name == "client discovery.py":
        existing = sys.modules.get(_CD_SINGLETON_NAME)
        if existing is not None:
            return existing
    spec = importlib.util.spec_from_file_location(name, str(file_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if file_path.name == "client discovery.py":
        sys.modules.setdefault(_CD_SINGLETON_NAME, mod)
    return mod


cd = _load_module("client_discovery", TOOLS_DIR / "client discovery.py")

KNOWN_MARKERS = [
    b"LastZ", b"FarmZ", b"Alt2Z", b"Alt3Z", b"Alt4Z",
    b"Alt5Z", b"Alt6Z", b"Alt7Z", b"Alt8Z", b"Alt9Z",
]


def file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def get_main_client(clients=None):
    clients = clients if clients is not None else cd.discover_clients(save_cache=False)
    for c in clients:
        if c.get("role") == "main" or c.get("unity_profile") == "LastZ":
            return c
    return clients[0] if clients else None


def client_needs_sync(main_client: dict, target_client: dict) -> tuple[bool, str]:
    if not main_client or not target_client:
        return False, "Missing client info"
    if Path(main_client["game_dir"]).resolve() == Path(target_client["game_dir"]).resolve():
        return False, "Target is Main client"

    m_ver = str(main_client.get("version") or "").strip()
    t_ver = str(target_client.get("version") or "").strip()
    if m_ver and t_ver and m_ver != t_ver:
        return True, f"Version mismatch (Main={m_ver}, Target={t_ver})"

    main_surv = Path(main_client["game_dir"]) / "Survival.exe"
    target_exe = Path(target_client["exe_path"])
    if main_surv.exists():
        if not target_exe.exists():
            return True, f"Missing target executable {target_exe.name}"
        if file_sha256(main_surv) != file_sha256(target_exe):
            return True, "Executable hash differs from Main"

    ggm = Path(target_client["game_dir"]) / "Survival_Data" / "globalgamemanagers"
    prof = target_client.get("unity_profile", "").encode("ascii", errors="ignore")
    if ggm.exists() and len(prof) == 5:
        raw = ggm.read_bytes()
        if prof not in raw:
            return True, f"Profile identity {target_client['unity_profile']} missing in globalgamemanagers"

    return False, "Up to date"


def _files_differ(src_path: Path, dst_path: Path) -> bool:
    try:
        sa = src_path.stat()
        sb = dst_path.stat()
    except OSError:
        return True
    if sa.st_size != sb.st_size:
        return True
    return file_sha256(src_path) != file_sha256(dst_path)


def _atomic_write_text_file(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        tmp.write_text(text, encoding=encoding)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass


def patch_unity_identity(game_dir: Path, unity_profile: str):
    """Apply Unity ReadyGo profile isolation to app.info and globalgamemanagers safely."""
    if not unity_profile or len(unity_profile.encode("ascii", errors="ignore")) != 5:
        raise ValueError(f"Unity profile name must be exactly 5 ASCII characters (got '{unity_profile}').")

    survival_data = game_dir / "Survival_Data"
    app_info = survival_data / "app.info"
    ggm = survival_data / "globalgamemanagers"

    markers = list(KNOWN_MARKERS)
    desired_app_text = f"ReadyGo\n{unity_profile}"
    if app_info.exists():
        raw_app = app_info.read_text(encoding="utf-8", errors="ignore")
        lines = [ln.strip() for ln in raw_app.splitlines() if ln.strip()]
        if len(lines) >= 2 and len(lines[1].encode("ascii", errors="ignore")) == 5:
            prev_b = lines[1].encode("ascii", errors="ignore")
            if prev_b not in markers:
                markers.insert(0, prev_b)
        try:
            app_nlink = app_info.stat().st_nlink
        except OSError:
            app_nlink = 1
        if raw_app != desired_app_text or app_nlink > 1:
            _atomic_write_text_file(app_info, desired_app_text, encoding="utf-8")

    if ggm.exists():
        data = bytearray(ggm.read_bytes())
        target_bytes = unity_profile.encode("ascii")
        already_exact = (_READYGO_EXACT_PREFIX + target_bytes) in data
        if not already_exact:
            replaced = False
            # Prefer exact ReadyGo productName record (`ReadyGo\x00\x05\x00\x00\x00<marker>`)
            # before scanning backwards/globally, so an unrelated string match never corrupts headers.
            readygo_pos = data.find(b"ReadyGo\x00")
            for marker in markers:
                exact_pat = _READYGO_EXACT_PREFIX + marker
                e_idx = data.find(exact_pat)
                if e_idx >= 0:
                    start = e_idx + len(_READYGO_EXACT_PREFIX)
                    data[start:start + 5] = target_bytes
                    replaced = True
                    break
                if readygo_pos >= 0:
                    lp_idx = data.find(b"\x05\x00\x00\x00" + marker, readygo_pos, readygo_pos + 256)
                    if lp_idx >= 0:
                        start = lp_idx + 4
                        data[start:start + 5] = target_bytes
                        replaced = True
                        break
            if not replaced and readygo_pos >= 0 and data.find(b"\x05\x00\x00\x00" + target_bytes, readygo_pos, readygo_pos + 256) >= 0:
                replaced = True
            if not replaced:
                if target_bytes in data:
                    replaced = True
                else:
                    for marker in markers:
                        idx = data.find(marker, readygo_pos if readygo_pos >= 0 else 0)
                        if idx < 0:
                            idx = data.find(marker)
                        if idx >= 0:
                            data[idx:idx + 5] = target_bytes
                            replaced = True
                            break
            if not replaced:
                raise RuntimeError(f"Could not find ReadyGo profile marker in {ggm}")
            tmp = ggm.with_name(f"{ggm.name}.{os.getpid()}.{threading.get_ident()}.tmp")
            tmp.write_bytes(data)
            os.replace(tmp, ggm)
        else:
            try:
                if ggm.stat().st_nlink > 1:
                    tmp = ggm.with_name(f"{ggm.name}.{os.getpid()}.{threading.get_ident()}.tmp")
                    tmp.write_bytes(data)
                    os.replace(tmp, ggm)
            except OSError:
                pass
    return True


def _hidden_subproc_kwargs() -> dict:
    kwargs: dict = {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
        "stdin": subprocess.DEVNULL,
    }
    si_cls = getattr(subprocess, "STARTUPINFO", None)
    if si_cls is not None:
        si = si_cls()
        si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        si.wShowWindow = 0
        kwargs["startupinfo"] = si
    return kwargs


def ensure_data_junction(game_dir: Path, exe_stem: str):
    """Ensure <ExeStem>_Data links via NTFS directory junction to Survival_Data."""
    if exe_stem.lower() == "survival":
        return
    survival_data = game_dir / "Survival_Data"
    custom_data = game_dir / f"{exe_stem}_Data"
    if not survival_data.exists():
        raise FileNotFoundError(f"Missing Survival_Data in {game_dir}")

    hidden_kw = _hidden_subproc_kwargs()
    if custom_data.exists():
        try:
            if custom_data.resolve() == survival_data.resolve():
                return
        except OSError:
            pass
        is_reparse = False
        try:
            if hasattr(os.path, "isjunction") and os.path.isjunction(custom_data):
                is_reparse = True
            else:
                st_l = os.lstat(custom_data)
                if getattr(st_l, "st_file_attributes", 0) & 0x0400:
                    is_reparse = True
        except OSError:
            pass
        if is_reparse or os.path.islink(custom_data):
            return
        if custom_data.is_dir():
            res = subprocess.run(
                ["cmd", "/c", "fsutil", "reparsepoint", "query", str(custom_data)],
                capture_output=True,
                text=True,
                **hidden_kw,
            )
            if res.returncode == 0:
                return
            raise RuntimeError(
                f"Expected NTFS junction at {custom_data}, found non-junction directory."
            )
    else:
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/j", str(custom_data), str(survival_data)],
            capture_output=True,
            text=True,
            **hidden_kw,
        )
        if res.returncode != 0:
            err_txt = (res.stderr or res.stdout or "").strip()
            raise RuntimeError(
                f"Failed to link {custom_data} -> {survival_data} ({err_txt or f'exit {res.returncode}'}). "
                "Make sure the target drive is formatted as NTFS (not exFAT/FAT32)."
            )


def is_client_running(client: dict):
    exe_path = str(Path(client["exe_path"]).resolve()).lower() if Path(client["exe_path"]).exists() else client["exe_path"].lower()
    exe_name = client["exe_name"].lower()
    for p in cd.find_running_processes():
        p_exe = p.get("exe_path", "")
        try:
            p_res = str(Path(p_exe).resolve()).lower() if p_exe else ""
        except OSError:
            p_res = p_exe.lower()
        if (p_res and p_res == exe_path) or (p["exe_name"].lower() == exe_name):
            return p["pid"]
    return None


def sync_client(target_client: dict, main_client: dict = None, force: bool = False) -> tuple[bool, str]:
    """Mirror updated game files from Main install to a farm/alt install and restore profile isolation."""
    clients = cd.discover_clients(save_cache=False)
    main_client = main_client or get_main_client(clients)
    if not main_client:
        return False, "Could not locate Main Last Z installation"

    src_dir = Path(main_client["game_dir"])
    dst_dir = Path(target_client["game_dir"])
    if _same_dir(src_dir, dst_dir):
        return True, "Main client is the source of truth"

    running_pid = is_client_running(target_client)
    if running_pid:
        return False, f"Cannot sync {target_client['label']} while {target_client['exe_name']} is running (PID {running_pid})"

    needs, reason = client_needs_sync(main_client, target_client)
    if not force and not needs:
        heal_res = heal_farm_launcher(target_client, main_client=main_client, all_clients=clients)
        heal_note = f"; {heal_res['message']}" if heal_res.get("healed") else ""
        return True, f"{target_client['label']} is already up to date (v{target_client.get('version')}){heal_note}"

    dst_dir.mkdir(parents=True, exist_ok=True)
    exe_stem = Path(target_client["exe_path"]).stem
    exclude_dirs = ["_heinz_backup"]
    if exe_stem.lower() != "survival":
        exclude_dirs.append(f"{exe_stem}_Data")

    cmd = [
        "robocopy",
        str(src_dir),
        str(dst_dir),
        "/MIR",
        "/MT:16",
        "/COPY:DAT",
        "/R:2",
        "/W:1",
        "/NDL",
        "/NFL",
        "/NJH",
        "/NJS",
    ]
    if exclude_dirs:
        cmd.append("/XD")
        cmd.extend(exclude_dirs)

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", **_hidden_subproc_kwargs())
    if res.returncode >= 8:
        return False, f"robocopy failed (exit {res.returncode}): {res.stderr or res.stdout}"

    surv_copy = dst_dir / "Survival.exe"
    target_exe = Path(target_client["exe_path"])
    if surv_copy.exists() and target_exe.name.lower() != "survival.exe":
        shutil.copy2(surv_copy, target_exe)

    ensure_data_junction(dst_dir, exe_stem)
    patch_unity_identity(dst_dir, target_client["unity_profile"])

    heal_res = heal_farm_launcher(target_client, main_client=main_client, all_clients=clients)
    heal_note = f"; {heal_res['message']}" if heal_res.get("healed") else ""

    new_ver = cd._read_game_version(dst_dir)
    return True, f"Synced {target_client['label']} ({target_client['exe_name']}) to v{new_ver} [{reason}]{heal_note}"


def _same_dir(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return str(a).lower() == str(b).lower()


# ------------------------------------------------------------------
# Farm Launcher Auto-Heal Guard (Post-Update Rotation Recovery)
# ------------------------------------------------------------------
FARM_HOOK_EXE_NAME = "FarmLauncherHook.exe"
KNOWN_HOOK_EXE_NAMES = (
    "FarmGame.exe",
    "Alt2Game.exe",
    "Alt3Game.exe",
    "Alt4Game.exe",
    "Alt5Game.exe",
    "Alt6Game.exe",
    "Alt7Game.exe",
    "Alt8Game.exe",
    "Alt9Game.exe",
)
KNOWN_PROFILE_NAMES = (
    "LastZ",
    "FarmZ",
    "Alt2Z",
    "Alt3Z",
    "Alt4Z",
    "Alt5Z",
    "Alt6Z",
    "Alt7Z",
    "Alt8Z",
    "Alt9Z",
)


def _atomic_write_text(dst: Path, content: str, encoding: str = "utf-8") -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(f"{dst.name}.{os.getpid()}.tmp")
    tmp.write_text(content, encoding=encoding)
    os.replace(tmp, dst)


def _atomic_write_bytes(dst: Path, payload: bytes) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(f"{dst.name}.{os.getpid()}.tmp")
    tmp.write_bytes(payload)
    os.replace(tmp, dst)


def _atomic_copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(f"{dst.name}.{os.getpid()}.tmp")
    shutil.copy2(src, tmp)
    os.replace(tmp, dst)


def _client_install_root(client: dict) -> Path | None:
    raw = str(client.get("game_dir") or "").strip()
    if not raw:
        return None
    gd = Path(raw)
    return gd.parent if gd.name.lower() == "game" else gd


def _find_rotated_launcher_dirs(inst_root: Path) -> list[Path]:
    """Find Last Z auto-updater rotated directories (`launcher_old_*`), newest first."""
    if not inst_root.is_dir():
        return []
    found: list[tuple[float, Path]] = []
    try:
        for entry in inst_root.iterdir():
            if entry.is_dir() and entry.name.lower().startswith("launcher_old_"):
                try:
                    mt = entry.stat().st_mtime
                except OSError:
                    mt = 0.0
                found.append((mt, entry))
    except OSError:
        return []
    found.sort(key=lambda item: item[0], reverse=True)
    return [p for _, p in found]


def _detect_launcher_prefix_and_exe(
    client: dict,
    launcher_dir: Path,
    backup_dir: Path,
    rotated_dirs: list[Path],
) -> tuple[str, str]:
    """Detect exact wrapper prefix (`Farm`, `Third`, etc.) and patched launcher exe name."""
    search_dirs = [launcher_dir, backup_dir, *rotated_dirs]
    found_prefix = ""
    found_launcher_exe = ""

    for d in search_dirs:
        if not d.is_dir():
            continue
        try:
            for item in sorted(d.iterdir(), key=lambda p: p.name.lower()):
                if not item.is_file():
                    continue
                nm = item.name
                low = nm.lower()
                if not found_prefix and low.endswith("launcherwrapper.vbs"):
                    found_prefix = nm[: -len("LauncherWrapper.vbs")]
                elif not found_prefix and low.endswith("launcherwrapper.ps1"):
                    found_prefix = nm[: -len("LauncherWrapper.ps1")]
                if not found_launcher_exe and low.startswith("launcher_") and low.endswith(".exe"):
                    found_launcher_exe = nm
        except OSError:
            continue
        if found_prefix and found_launcher_exe:
            break

    prof = str(client.get("unity_profile") or "").strip()
    label = str(client.get("label") or "").strip()
    if not found_prefix:
        if prof.lower() == "farmz" or label.lower() == "farm":
            found_prefix = "Farm"
        elif prof.lower() == "alt3z" or label.lower() == "third":
            found_prefix = "Third"
        else:
            clean = "".join(ch for ch in (label or prof or "Farm") if ch.isalnum())
            found_prefix = clean or "Farm"

    if not found_launcher_exe:
        if found_prefix.lower() == "third" or prof.lower() == "alt3z":
            found_launcher_exe = "Launcher_Third.exe"
        else:
            found_launcher_exe = "Launcher_Patched.exe"

    return found_prefix, found_launcher_exe


def _hook_binary_matches_identity(hook_path: Path, exe_name: str, unity_profile: str) -> bool:
    """Verify FarmLauncherHook.exe contains UTF-16LE markers for target exe_name and unity_profile."""
    if not hook_path.is_file():
        return False
    try:
        raw = hook_path.read_bytes()
    except OSError:
        return False
    if len(raw) < 1024:
        return False
    exe_b = str(exe_name or "").encode("utf-16le")
    prof_b = str(unity_profile or "").encode("utf-16le")
    return bool(exe_b and prof_b and (exe_b in raw) and (prof_b in raw))


def _patch_hook_binary_bytes(raw: bytes, target_exe: str, target_profile: str) -> bytes | None:
    """Patch a healthy sibling FarmLauncherHook.exe with exact same-length UTF-16LE exe & profile markers."""
    if not raw or len(raw) < 1024:
        return None
    tgt_exe_b = str(target_exe or "").encode("utf-16le")
    tgt_prof_b = str(target_profile or "").encode("utf-16le")
    if not tgt_exe_b or len(str(target_profile or "").encode("ascii", errors="ignore")) != 5:
        return None

    patched = raw
    exe_ok = tgt_exe_b in patched
    if not exe_ok:
        for cand_exe in KNOWN_HOOK_EXE_NAMES:
            cand_b = cand_exe.encode("utf-16le")
            if len(cand_b) == len(tgt_exe_b) and cand_b in patched:
                patched = patched.replace(cand_b, tgt_exe_b)
                exe_ok = True
                break

    prof_ok = tgt_prof_b in patched
    if not prof_ok:
        for cand_prof in KNOWN_PROFILE_NAMES:
            cand_b = cand_prof.encode("utf-16le")
            if len(cand_b) == len(tgt_prof_b) and cand_b in patched:
                patched = patched.replace(cand_b, tgt_prof_b)
                prof_ok = True
                break

    if not (exe_ok and prof_ok):
        return None
    if tgt_exe_b not in patched or tgt_prof_b not in patched:
        return None
    return patched


def _find_sibling_hook_binary(all_clients: list[dict] | None, exclude_root: Path) -> Path | None:
    """Locate any healthy FarmLauncherHook.exe from sibling farm installs to patch from."""
    for c in (all_clients or []):
        if str(c.get("role") or "").lower() == "main":
            continue
        root = _client_install_root(c)
        if root is None or _same_dir(root, exclude_root):
            continue
        cands = [
            root / "launcher" / FARM_HOOK_EXE_NAME,
            root / "launcher_backup" / FARM_HOOK_EXE_NAME,
        ]
        for rd in _find_rotated_launcher_dirs(root):
            cands.append(rd / FARM_HOOK_EXE_NAME)
        for p in cands:
            try:
                if p.is_file() and p.stat().st_size >= 1024:
                    return p
            except OSError:
                continue
    return None


def _ps_single_quote(val: str) -> str:
    return str(val).replace("'", "''")


def _render_wrapper_vbs(ps1_path: Path) -> str:
    ps1_str = str(ps1_path).replace('"', '""')
    return (
        'Set objShell = CreateObject("WScript.Shell")\r\n'
        f'objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""{ps1_str}""", 0, False\r\n'
    )


def _render_profile_identity_ps1(prefix: str, unity_profile: str) -> str:
    fn_name = f"Set-{prefix}ProfileIdentity"
    known_ps = ", ".join(f"'{p}'" for p in KNOWN_PROFILE_NAMES)
    prof_q = _ps_single_quote(unity_profile)
    return (
        f"function {fn_name} {{\n"
        "    [CmdletBinding()]\n"
        "    param(\n"
        "        [Parameter(Mandatory)]\n"
        "        [string]$GlobalManagersPath,\n"
        "\n"
        "        [Parameter(Mandatory)]\n"
        "        [string]$AppInfoPath\n"
        "    )\n"
        "\n"
        f"    $targetName = '{prof_q}'\n"
        f"    $knownNames = @({known_ps})\n"
        "    $bytes = [IO.File]::ReadAllBytes($GlobalManagersPath)\n"
        "    $text = [Text.Encoding]::ASCII.GetString($bytes)\n"
        "    $matches = @(\n"
        "        foreach ($name in $knownNames) {\n"
        "            $offset = 0\n"
        "            while (($index = $text.IndexOf($name, $offset, [StringComparison]::Ordinal)) -ge 0) {\n"
        "                [pscustomobject]@{ Name = $name; Index = $index }\n"
        "                $offset = $index + $name.Length\n"
        "            }\n"
        "        }\n"
        "    )\n"
        "    if ($matches.Count -ne 1) {\n"
        '        throw "Expected exactly one known Last Z profile marker; found $($matches.Count)."\n'
        "    }\n"
        "\n"
        "    $replacement = [Text.Encoding]::ASCII.GetBytes($targetName)\n"
        "    [Array]::Copy($replacement, 0, $bytes, $matches[0].Index, $replacement.Length)\n"
        "\n"
        "    $managerTemp = $GlobalManagersPath + '.farm-' + [Guid]::NewGuid().ToString('N')\n"
        "    $appInfoTemp = $AppInfoPath + '.farm-' + [Guid]::NewGuid().ToString('N')\n"
        "    $managerBackup = $GlobalManagersPath + '.backup-' + [Guid]::NewGuid().ToString('N')\n"
        "    $appInfoBackup = $AppInfoPath + '.backup-' + [Guid]::NewGuid().ToString('N')\n"
        "    try {\n"
        "        [IO.File]::WriteAllBytes($managerTemp, $bytes)\n"
        '        [IO.File]::WriteAllText($appInfoTemp, "ReadyGo`n$targetName", [Text.UTF8Encoding]::new($false))\n'
        "        [IO.File]::Replace($managerTemp, $GlobalManagersPath, $managerBackup)\n"
        "        [IO.File]::Replace($appInfoTemp, $AppInfoPath, $appInfoBackup)\n"
        "    }\n"
        "    finally {\n"
        "        if ([IO.File]::Exists($managerTemp)) { [IO.File]::Delete($managerTemp) }\n"
        "        if ([IO.File]::Exists($appInfoTemp)) { [IO.File]::Delete($appInfoTemp) }\n"
        "        if ([IO.File]::Exists($managerBackup)) { [IO.File]::Delete($managerBackup) }\n"
        "        if ([IO.File]::Exists($appInfoBackup)) { [IO.File]::Delete($appInfoBackup) }\n"
        "    }\n"
        "}\n"
    )


def _render_wrapper_ps1(
    prefix: str,
    source_game_dir: Path,
    inst_root: Path,
    exe_name: str,
    unity_profile: str,
    launcher_exe_name: str,
) -> str:
    exe_stem = Path(exe_name).stem
    data_dir_name = f"{exe_stem}_Data"
    src_q = _ps_single_quote(str(source_game_dir))
    root_q = _ps_single_quote(str(inst_root))
    exe_q = _ps_single_quote(exe_name)
    prof_q = _ps_single_quote(unity_profile)
    pref_q = _ps_single_quote(prefix)
    l_exe_q = _ps_single_quote(launcher_exe_name)
    data_q = _ps_single_quote(data_dir_name)
    return (
        "$ErrorActionPreference = 'Stop'\n"
        "\n"
        f"$sourceGame = '{src_q}'\n"
        f"$instRoot = '{root_q}'\n"
        "$instGame = Join-Path $instRoot 'Game'\n"
        "$instLauncher = Join-Path $instRoot 'launcher'\n"
        f"$errorLog = Join-Path $instLauncher '{pref_q}LauncherWrapper.error.log'\n"
        "\n"
        "try {\n"
        f"    if ([IO.Path]::GetFullPath($instRoot) -ne '{root_q}') {{\n"
        '        throw "Unexpected farm-instance target: $instRoot"\n'
        "    }\n"
        "\n"
        f"    & robocopy $sourceGame $instGame /MIR /MT:16 /XD {data_q} /XF {exe_q} /COPY:DAT /DCOPY:DAT /R:2 /W:1 /NDL /NFL /NJH /NJS | Out-Null\n"
        "    $robocopyExitCode = $LASTEXITCODE\n"
        "    if ($robocopyExitCode -ge 8) {\n"
        '        throw "Could not refresh the Last Z instance (robocopy code $robocopyExitCode)."\n'
        "    }\n"
        "\n"
        f"    Copy-Item (Join-Path $instGame 'Survival.exe') (Join-Path $instGame '{exe_q}') -Force\n"
        "\n"
        f"    . (Join-Path $instLauncher '{pref_q}ProfileIdentity.ps1')\n"
        "    $survivalData = Join-Path $instGame 'Survival_Data'\n"
        f"    Set-{prefix}ProfileIdentity `\n"
        "        -GlobalManagersPath (Join-Path $survivalData 'globalgamemanagers') `\n"
        "        -AppInfoPath (Join-Path $survivalData 'app.info')\n"
        "\n"
        "    if (Test-Path -LiteralPath $errorLog) { Remove-Item -LiteralPath $errorLog -Force }\n"
        "\n"
        "    try {\n"
        f"        $regKey = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Software\\ReadyGo\\{prof_q}', $true)\n"
        "        if ($null -ne $regKey) {\n"
        "            $repaired = $false\n"
        "            foreach ($k in @('Screenmanager Window Position X_h4088080503', 'Screenmanager Window Position Y_h4088080502', 'WindowX_h2353518033', 'WindowY_h2353518032')) {\n"
        "                $raw = $regKey.GetValue($k, $null)\n"
        "                if ($raw -is [int] -or $raw -is [long] -or $raw -is [uint32]) {\n"
        "                    $sval = [BitConverter]::ToInt32([BitConverter]::GetBytes([uint32]([long]$raw -band 0xFFFFFFFFL)), 0)\n"
        "                    if ($sval -lt -100 -or $sval -gt 10000) {\n"
        "                        $regKey.SetValue($k, 80, [Microsoft.Win32.RegistryValueKind]::DWord)\n"
        "                        $repaired = $true\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "            if ($repaired) {\n"
        "                $regKey.SetValue('Screenmanager Fullscreen mode_h3630240806', 3, [Microsoft.Win32.RegistryValueKind]::DWord)\n"
        "            }\n"
        "            $regKey.Close()\n"
        "        }\n"
        "    } catch {}\n"
        "\n"
        f"    $launcherExe = Join-Path $instLauncher '{l_exe_q}'\n"
        "    if (-not (Test-Path -LiteralPath $launcherExe)) {\n"
        "        $launcherExe = Join-Path $instLauncher 'Launcher.exe'\n"
        "    }\n"
        "    Start-Process $launcherExe -WorkingDirectory $instLauncher\n"
        "}\n"
        "catch {\n"
        "    [IO.File]::WriteAllText(\n"
        "        $errorLog,\n"
        '        "$(Get-Date -Format o) $($_.Exception.GetType().Name): $($_.Exception.Message)",\n'
        "        [Text.UTF8Encoding]::new($false))\n"
        "    exit 1\n"
        "}\n"
    )


def inspect_farm_launcher_health(
    target_client: dict,
    main_client: dict | None = None,
    all_clients: list[dict] | None = None,
) -> dict:
    """Inspect whether a Farm/Alt instance's launcher/ wrapper scripts and hooks are intact."""
    label = str(target_client.get("label") or target_client.get("unity_profile") or "Farm")
    prof = str(target_client.get("unity_profile") or "").strip()
    exe_name = str(target_client.get("exe_name") or Path(str(target_client.get("exe_path") or "")).name).strip()
    if str(target_client.get("role") or "").lower() == "main" or prof.lower() == "lastz":
        return {
            "label": label,
            "unity_profile": prof,
            "skipped": True,
            "has_launcher_layout": False,
            "healthy": True,
            "needs_heal": False,
            "missing_files": [],
            "backup_missing": [],
            "rotated_dirs": [],
        }

    inst_root = _client_install_root(target_client)
    if inst_root is None or (main_client and _same_dir(Path(main_client["game_dir"]), Path(target_client["game_dir"]))):
        return {
            "label": label,
            "unity_profile": prof,
            "skipped": True,
            "has_launcher_layout": False,
            "healthy": True,
            "needs_heal": False,
            "missing_files": [],
            "backup_missing": [],
            "rotated_dirs": [],
        }

    launcher_dir = inst_root / "launcher"
    backup_dir = inst_root / "launcher_backup"
    rotated_dirs = _find_rotated_launcher_dirs(inst_root)
    has_layout = launcher_dir.is_dir() or backup_dir.is_dir() or bool(rotated_dirs)
    prefix, launcher_exe_name = _detect_launcher_prefix_and_exe(target_client, launcher_dir, backup_dir, rotated_dirs)

    if not has_layout:
        return {
            "label": label,
            "unity_profile": prof,
            "skipped": True,
            "has_launcher_layout": False,
            "healthy": True,
            "needs_heal": False,
            "prefix": prefix,
            "launcher_exe_name": launcher_exe_name,
            "launcher_dir": str(launcher_dir),
            "backup_dir": str(backup_dir),
            "missing_files": [],
            "backup_missing": [],
            "rotated_dirs": [],
        }

    script_names = [
        f"{prefix}LauncherWrapper.vbs",
        f"{prefix}LauncherWrapper.ps1",
        f"{prefix}ProfileIdentity.ps1",
    ]
    missing_scripts = [fn for fn in script_names if not (launcher_dir / fn).is_file() or (launcher_dir / fn).stat().st_size == 0]

    missing_binaries: list[str] = []
    if not (launcher_dir / launcher_exe_name).is_file() or (launcher_dir / launcher_exe_name).stat().st_size == 0:
        missing_binaries.append(launcher_exe_name)

    hook_path = launcher_dir / FARM_HOOK_EXE_NAME
    hook_identity_ok = _hook_binary_matches_identity(hook_path, exe_name, prof)
    if not hook_path.is_file() or not hook_identity_ok:
        missing_binaries.append(FARM_HOOK_EXE_NAME)

    all_managed = script_names + [launcher_exe_name, FARM_HOOK_EXE_NAME]
    backup_missing: list[str] = []
    for fn in all_managed:
        src_p = launcher_dir / fn
        bak_p = backup_dir / fn
        if src_p.is_file():
            if not bak_p.is_file() or _files_differ(src_p, bak_p):
                backup_missing.append(fn)
        elif not bak_p.is_file():
            backup_missing.append(fn)

    missing_files = missing_scripts + missing_binaries
    healthy = len(missing_files) == 0
    return {
        "label": label,
        "unity_profile": prof,
        "exe_name": exe_name,
        "skipped": False,
        "has_launcher_layout": True,
        "healthy": healthy,
        "needs_heal": not healthy,
        "prefix": prefix,
        "launcher_exe_name": launcher_exe_name,
        "launcher_dir": str(launcher_dir),
        "backup_dir": str(backup_dir),
        "rotated_dirs": [str(p) for p in rotated_dirs],
        "missing_scripts": missing_scripts,
        "missing_binaries": missing_binaries,
        "missing_files": missing_files,
        "hook_identity_ok": hook_identity_ok,
        "backup_missing": backup_missing,
    }


def heal_farm_launcher(
    target_client: dict,
    main_client: dict | None = None,
    all_clients: list[dict] | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Auto-heal a Farm/Alt launcher folder if Last Z's auto-updater rotated or wiped wrapper files."""
    clients = all_clients if all_clients is not None else cd.discover_clients(save_cache=False)
    main_c = main_client or get_main_client(clients)
    health = inspect_farm_launcher_health(target_client, main_client=main_c, all_clients=clients)
    label = health["label"]
    prof = health["unity_profile"]

    if health.get("skipped") and not (force and str(target_client.get("role") or "").lower() != "main"):
        return {
            "ok": True,
            "label": label,
            "unity_profile": prof,
            "skipped": True,
            "healed": False,
            "dry_run": bool(dry_run),
            "restored_files": [],
            "regenerated_files": [],
            "patched_files": [],
            "backed_up_files": [],
            "warnings": [],
            "message": f"{label}: no launcher wrapper layout to guard",
        }

    inst_root = _client_install_root(target_client)
    assert inst_root is not None
    launcher_dir = inst_root / "launcher"
    backup_dir = inst_root / "launcher_backup"
    rotated_dirs = _find_rotated_launcher_dirs(inst_root)
    prefix, launcher_exe_name = _detect_launcher_prefix_and_exe(target_client, launcher_dir, backup_dir, rotated_dirs)
    exe_name = str(target_client.get("exe_name") or Path(str(target_client.get("exe_path") or "")).name).strip()
    source_game_dir = Path(main_c["game_dir"]) if (main_c and main_c.get("game_dir")) else Path(target_client["game_dir"])

    restored_files: list[str] = []
    regenerated_files: list[str] = []
    patched_files: list[str] = []
    backed_up_files: list[str] = []
    warnings: list[str] = []

    vbs_name = f"{prefix}LauncherWrapper.vbs"
    ps1_name = f"{prefix}LauncherWrapper.ps1"
    id_name = f"{prefix}ProfileIdentity.ps1"
    script_templates = {
        vbs_name: _render_wrapper_vbs(launcher_dir / ps1_name),
        ps1_name: _render_wrapper_ps1(prefix, source_game_dir, inst_root, exe_name, prof, launcher_exe_name),
        id_name: _render_profile_identity_ps1(prefix, prof),
    }

    def _find_recovery_source(filename: str) -> Path | None:
        for cand_dir in (backup_dir, *rotated_dirs):
            cand = cand_dir / filename
            try:
                if cand.is_file() and cand.stat().st_size > 0:
                    return cand
            except OSError:
                continue
        return None

    # 1. Heal wrapper scripts (.vbs, .ps1, ProfileIdentity.ps1)
    for fn, generated_txt in script_templates.items():
        dst = launcher_dir / fn
        needs_fix = force or (not dst.is_file()) or (dst.stat().st_size == 0)
        if not needs_fix:
            continue
        src = None if force else _find_recovery_source(fn)
        if src is not None:
            if not dry_run:
                _atomic_copy_file(src, dst)
            restored_files.append(fn)
        else:
            if not dry_run:
                enc = "ascii" if fn.lower().endswith(".vbs") else "utf-8"
                _atomic_write_text(dst, generated_txt, encoding=enc)
            regenerated_files.append(fn)

    # 2. Heal patched Launcher executable (`Launcher_Patched.exe` / `Launcher_Third.exe`)
    l_dst = launcher_dir / launcher_exe_name
    if force or not l_dst.is_file() or l_dst.stat().st_size == 0:
        l_src = _find_recovery_source(launcher_exe_name)
        if l_src is not None:
            if not dry_run:
                _atomic_copy_file(l_src, l_dst)
            restored_files.append(launcher_exe_name)
        else:
            warnings.append(f"{launcher_exe_name} not found in launcher_backup or launcher_old_* (wrapper will fall back to Launcher.exe)")

    # 3. Heal or cross-patch `FarmLauncherHook.exe` with verified UTF-16LE exe + profile identity
    hook_dst = launcher_dir / FARM_HOOK_EXE_NAME
    hook_ok = (not force) and _hook_binary_matches_identity(hook_dst, exe_name, prof)
    if not hook_ok:
        recovered_hook = False
        for cand_dir in (backup_dir, *rotated_dirs):
            cand = cand_dir / FARM_HOOK_EXE_NAME
            if _hook_binary_matches_identity(cand, exe_name, prof):
                if not dry_run:
                    _atomic_copy_file(cand, hook_dst)
                restored_files.append(FARM_HOOK_EXE_NAME)
                recovered_hook = True
                break
        if not recovered_hook:
            # Try patching an existing wrong-identity hook in place, or a sibling farm hook binary
            patch_sources: list[Path] = []
            if hook_dst.is_file():
                patch_sources.append(hook_dst)
            for cand_dir in (backup_dir, *rotated_dirs):
                cand = cand_dir / FARM_HOOK_EXE_NAME
                if cand.is_file():
                    patch_sources.append(cand)
            sibling = _find_sibling_hook_binary(clients, inst_root)
            if sibling is not None:
                patch_sources.append(sibling)

            for psrc in patch_sources:
                try:
                    patched_bytes = _patch_hook_binary_bytes(psrc.read_bytes(), exe_name, prof)
                except OSError:
                    patched_bytes = None
                if patched_bytes is not None:
                    if not dry_run:
                        _atomic_write_bytes(hook_dst, patched_bytes)
                    patched_files.append(FARM_HOOK_EXE_NAME)
                    recovered_hook = True
                    break
        if not recovered_hook:
            warnings.append(f"Could not recover or patch {FARM_HOOK_EXE_NAME} for {exe_name}/{prof}")

    # 4. Proactively mirror all healthy managed launcher files to `<inst_root>/launcher_backup/`
    managed_files = [vbs_name, ps1_name, id_name, launcher_exe_name, FARM_HOOK_EXE_NAME]
    for fn in managed_files:
        src_p = launcher_dir / fn
        bak_p = backup_dir / fn
        if not src_p.is_file():
            continue
        if fn == FARM_HOOK_EXE_NAME and not _hook_binary_matches_identity(src_p, exe_name, prof):
            continue
        if not bak_p.is_file() or _files_differ(src_p, bak_p):
            if not dry_run:
                _atomic_copy_file(src_p, bak_p)
            backed_up_files.append(fn)

    healed = bool(restored_files or regenerated_files or patched_files)
    parts: list[str] = []
    if restored_files:
        parts.append(f"restored {len(restored_files)} ({', '.join(restored_files)})")
    if regenerated_files:
        parts.append(f"regenerated {len(regenerated_files)} ({', '.join(regenerated_files)})")
    if patched_files:
        parts.append(f"patched {len(patched_files)} ({', '.join(patched_files)})")
    if backed_up_files:
        parts.append(f"backed up {len(backed_up_files)}")
    if warnings:
        parts.append(f"warnings: {'; '.join(warnings)}")

    if not parts:
        msg = f"{label} launcher healthy"
    else:
        prefix_word = "[DRY-RUN] " if dry_run else ""
        msg = f"{prefix_word}{label} launcher: " + "; ".join(parts)

    post_ok = (not warnings) or bool(restored_files or regenerated_files or patched_files) or health.get("healthy", False)
    return {
        "ok": post_ok,
        "label": label,
        "unity_profile": prof,
        "skipped": False,
        "healed": healed,
        "dry_run": bool(dry_run),
        "prefix": prefix,
        "launcher_dir": str(launcher_dir),
        "backup_dir": str(backup_dir),
        "rotated_dirs": [str(p) for p in rotated_dirs],
        "restored_files": restored_files,
        "regenerated_files": regenerated_files,
        "patched_files": patched_files,
        "backed_up_files": backed_up_files,
        "warnings": warnings,
        "message": msg,
    }


def heal_all_farm_launchers(
    clients: list[dict] | None = None,
    main_client: dict | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Verify and auto-heal launcher wrappers & hooks across every non-main Last Z client."""
    all_clients = clients if clients is not None else cd.discover_clients(save_cache=False)
    main_c = main_client or get_main_client(all_clients)
    results: list[dict] = []
    healed_count = 0
    healthy_count = 0
    backed_up_count = 0
    failed_count = 0

    for c in all_clients:
        if str(c.get("role") or "").lower() == "main":
            continue
        if main_c and _same_dir(Path(main_c["game_dir"]), Path(c["game_dir"])):
            continue
        res = heal_farm_launcher(c, main_client=main_c, all_clients=all_clients, dry_run=dry_run, force=force)
        results.append(res)
        if res.get("skipped"):
            continue
        if res.get("healed"):
            healed_count += 1
        elif res.get("ok"):
            healthy_count += 1
        if res.get("backed_up_files"):
            backed_up_count += 1
        if not res.get("ok"):
            failed_count += 1

    checked = len([r for r in results if not r.get("skipped")])
    if healed_count > 0:
        summary = f"Auto-healed {healed_count}/{checked} farm launcher(s)"
    elif backed_up_count > 0:
        summary = f"All {checked} farm launcher(s) healthy (refreshed {backed_up_count} backup(s))"
    elif checked > 0:
        summary = f"All {checked} farm launcher(s) healthy"
    else:
        summary = "No farm launcher folders found"

    return {
        "ok": failed_count == 0,
        "checked": checked,
        "healed_count": healed_count,
        "healthy_count": healthy_count,
        "backed_up_count": backed_up_count,
        "failed_count": failed_count,
        "dry_run": bool(dry_run),
        "summary": summary,
        "results": results,
    }


def sync_all_clients(force: bool = False):
    clients = cd.discover_clients(save_cache=True)
    main_client = get_main_client(clients)
    results = []
    for c in clients:
        if _same_dir(Path(c["game_dir"]), Path(main_client["game_dir"])):
            results.append({"label": c["label"], "ok": True, "message": f"Main source client v{c.get('version')}"})
            continue
        ok, msg = sync_client(c, main_client=main_client, force=force)
        results.append({"label": c["label"], "ok": ok, "message": msg})
    cd.discover_clients(save_cache=True)
    return results


GPU_PREF_KEY = r"Software\Microsoft\DirectX\UserGpuPreferences"


def check_gpu_high_performance(exe_path: Path) -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, GPU_PREF_KEY) as k:
            val, _ = winreg.QueryValueEx(k, str(exe_path))
            return "GpuPreference=2" in str(val)
    except OSError:
        return False


def apply_gpu_high_performance(exe_paths: list[Path]) -> list[str]:
    applied: list[str] = []
    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, GPU_PREF_KEY, 0, winreg.KEY_SET_VALUE) as k:
            for ep in exe_paths:
                if ep and ep.exists():
                    winreg.SetValueEx(k, str(ep), 0, winreg.REG_SZ, "GpuPreference=2;")
                    applied.append(ep.name)
    except OSError:
        pass
    return applied


def ensure_base_backup(game_dir: Path) -> bool:
    survival_data = game_dir / "Survival_Data"
    backup_dir = survival_data / "_heinz_backup"
    if not survival_data.exists():
        return False
    backup_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in (("app.info", "app.info.orig"), ("globalgamemanagers", "globalgamemanagers.orig")):
        src = survival_data / src_name
        dst = backup_dir / dst_name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    return (backup_dir / "globalgamemanagers.orig").exists()


def _resolve_desktop_dir() -> Path | None:
    """Resolve user's real Desktop directory (handles OneDrive folder redirection)."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as k:
            val, _ = winreg.QueryValueEx(k, "Desktop")
            if val:
                p = Path(os.path.expandvars(str(val)))
                if p.exists():
                    return p
    except OSError:
        pass
    for env_cand in (r"%USERPROFILE%\OneDrive\Desktop", r"%USERPROFILE%\Desktop"):
        p = Path(os.path.expandvars(env_cand))
        if p.exists():
            return p
    return None


def _is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / f".heinz_probe_{os.getpid()}_{threading.get_ident()}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def create_account_shortcut(label: str, game_exe: Path) -> tuple[bool, str]:
    """Create a Windows Desktop shortcut that launches this Last Z account with multi-instance token."""
    desktop = _resolve_desktop_dir()
    if desktop is None or not desktop.exists():
        return False, "Desktop folder not found"
    safe_label = "".join(ch for ch in str(label or "Alt") if ch not in r'\/:*?"<>|').strip() or "Alt"
    lnk_path = desktop / f"Last Z ({safe_label}).lnk"

    heinz_candidates = [
        Path(sys.executable) if getattr(sys, "frozen", False) else None,
        Path(os.path.expandvars(r"%USERPROFILE%\Downloads\HeinZ\HeinZ\HeinZ.exe")),
        REPO_ROOT / "dist" / "HeinZ" / "HeinZ.exe",
    ]
    heinz_exe = next((p for p in heinz_candidates if p and p.exists() and p.name.lower() == "heinz.exe"), None)

    if heinz_exe is not None:
        target_path = str(heinz_exe)
        args = f'--launch-client "{safe_label}"'
        work_dir = str(heinz_exe.parent)
    else:
        py_exe = Path(sys.executable)
        if py_exe.name.lower() == "python.exe":
            pyw = py_exe.with_name("pythonw.exe")
            if pyw.exists():
                py_exe = pyw
        target_path = str(py_exe)
        args = f'"{Path(__file__).resolve()}" launch "{safe_label}" windowed'
        work_dir = str(REPO_ROOT)

    ps_script = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{str(lnk_path).replace(chr(39), chr(39)*2)}'); "
        f"$s.TargetPath = '{target_path.replace(chr(39), chr(39)*2)}'; "
        f"$s.Arguments = '{args.replace(chr(39), chr(39)*2)}'; "
        f"$s.WorkingDirectory = '{work_dir.replace(chr(39), chr(39)*2)}'; "
        f"$s.IconLocation = '{str(game_exe).replace(chr(39), chr(39)*2)},0'; "
        f"$s.Description = 'Launch Last Z ({safe_label})'; "
        "$s.Save()"
    )
    res = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True,
        **_hidden_subproc_kwargs(),
    )
    if res.returncode == 0 and lnk_path.exists():
        return True, str(lnk_path)
    return False, (res.stderr or res.stdout or "Shortcut creation failed").strip()


def _suggest_next_account(clients: list[dict], base_dir: Path | None, preferred_name: str | None = None) -> dict:
    used_profiles = {str(c.get("unity_profile") or "").upper() for c in clients}
    used_labels = {str(c.get("label") or "").strip().lower() for c in clients}
    used_exes = {str(c.get("exe_name") or "").strip().lower() for c in clients}

    import re as _re
    base_clean = _re.sub(r"[\s\d²³⁴]+$", "", str(preferred_name or "").strip()).strip()
    if base_clean.lower() in ("", "player", "offline", "client", "unknown"):
        base_clean = "Account"

    num = max(2, len(clients) + 1)
    while num < 99:
        prof = f"Alt{num}Z" if num <= 9 else f"Ac{num:02d}Z"
        exe_name = f"Alt{num}Game.exe"
        lbl = f"{base_clean} {num}"
        if (
            len(prof) == 5
            and prof.upper() not in used_profiles
            and exe_name.lower() not in used_exes
            and lbl.lower() not in used_labels
        ):
            break
        num += 1

    # Prefer placing beside existing farm clones if present, else beside base Last Z install
    parent_base = None
    for c in clients:
        if c.get("role") != "main" and c.get("game_dir"):
            gd = Path(c["game_dir"])
            inst_root = gd.parent if gd.name.lower() == "game" else gd
            parent_base = inst_root.parent
            break
    if parent_base is None and base_dir is not None:
        inst_root = base_dir.parent if base_dir.name.lower() == "game" else base_dir
        parent_base = inst_root.parent
    # Never default clones into read-only system locations like C:\Program Files
    if parent_base is not None:
        pb_low = str(parent_base).lower()
        if "program files" in pb_low or not _is_writable_dir(parent_base):
            parent_base = None
    if parent_base is None:
        parent_base = Path(os.path.expandvars(r"%LOCALAPPDATA%"))

    return {
        "slot_number": num,
        "label": lbl,
        "unity_profile": prof,
        "exe_name": exe_name,
        "root_dir": str(parent_base / f"Last Z_Alt{num}"),
    }


def inspect_setup_status(explicit_base_dir: str | None = None, preferred_name: str | None = None) -> dict:
    """Inspect whether base Last Z installation is detected and prepped for multi-instance."""
    base_info = cd.detect_vanilla_base_install(explicit_base_dir)
    clients = cd.discover_clients(save_cache=False)
    base_dir = Path(base_info["game_dir"]) if base_info.get("found") else None

    reg_lastz_ok = False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\ReadyGo\LastZ"):
            reg_lastz_ok = True
    except OSError:
        reg_lastz_ok = False

    gpu_ok = bool(base_dir and check_gpu_high_performance(base_dir / "Survival.exe"))
    backup_ok = bool(base_dir and (base_dir / "Survival_Data" / "_heinz_backup" / "globalgamemanagers.orig").exists())
    bot_cfg_ok = (cd.DATA_DIR / "bot config.json").exists()
    main_registered = any(c.get("role") == "main" for c in clients)

    clones = []
    main_client = get_main_client(clients)
    for c in clients:
        if c.get("role") == "main":
            continue
        needs, reason = client_needs_sync(main_client, c) if main_client else (False, "")
        l_health = inspect_farm_launcher_health(c, main_client=main_client, all_clients=clients)
        clones.append({
            "label": c.get("label"),
            "unity_profile": c.get("unity_profile"),
            "game_dir": c.get("game_dir"),
            "exe_name": c.get("exe_name"),
            "version": c.get("version"),
            "needs_sync": needs,
            "sync_reason": reason,
            "launcher_healthy": bool(l_health.get("healthy", True)),
            "launcher_missing": list(l_health.get("missing_files") or []),
        })

    return {
        "base_found": bool(base_info.get("found")),
        "base_game_dir": base_info.get("game_dir", ""),
        "base_root_dir": base_info.get("root_dir", ""),
        "base_version": base_info.get("version", ""),
        "base_profile": base_info.get("unity_profile", ""),
        "backup_ok": backup_ok,
        "gpu_pref_ok": gpu_ok,
        "reg_profile_ok": reg_lastz_ok,
        "bot_config_ok": bot_cfg_ok,
        "main_registered": main_registered,
        "multi_instance_ready": bool(base_info.get("found") and gpu_ok and bot_cfg_ok and main_registered),
        "clone_count": len(clones),
        "clones": clones,
        "suggested_next": _suggest_next_account(clients, base_dir, preferred_name=preferred_name),
    }


def setup_base_installation(explicit_base_dir: str | None = None) -> tuple[bool, dict]:
    """Turn a vanilla Last Z installation into the HeinZ multi-instance & performance-tuned setup."""
    base_info = cd.detect_vanilla_base_install(explicit_base_dir)
    if not base_info.get("found"):
        return False, {"error": "Could not locate Last Z (Survival.exe). Please Browse to your Last Z folder."}

    base_dir = Path(base_info["game_dir"])
    try:
        backup_created = ensure_base_backup(base_dir)

        _, cur_prof = cd._read_app_info(base_dir)
        if cur_prof != "LastZ":
            patch_unity_identity(base_dir, "LastZ")
    except PermissionError as exc:
        return False, {
            "error": (
                f"Permission denied writing to {base_dir}\\Survival_Data ({exc}). "
                "If Last Z is installed in Program Files, right-click HeinZ.exe -> Run as administrator once to patch the base install, "
                "or close Last Z / Launcher.exe if it is open."
            )
        }
    except OSError as exc:
        return False, {"error": f"Could not update {base_dir}\\Survival_Data ({exc}). Close Last Z / Launcher.exe and retry."}

    exe_targets = [
        base_dir / "Survival.exe",
        base_dir.parent / "Last Z.exe",
        base_dir.parent / "launcher" / "Launcher.exe",
    ]
    # Also ensure existing clones carry High-Perf GPU prefs
    clients = cd.discover_clients(save_cache=False)
    for c in clients:
        ep = Path(str(c.get("exe_path") or ""))
        if ep.exists():
            exe_targets.append(ep)
    gpu_applied = apply_gpu_high_performance(exe_targets)

    repair_info = repair_unity_window_position("LastZ")

    main_shortcut_ok = False
    main_shortcut_msg = ""
    try:
        desktop = _resolve_desktop_dir()
        if desktop is not None:
            main_lnk = desktop / "Last Z (Main).lnk"
            if not main_lnk.exists():
                main_shortcut_ok, main_shortcut_msg = create_account_shortcut("Main", base_dir / "Survival.exe")
            else:
                main_shortcut_ok, main_shortcut_msg = True, str(main_lnk)
    except Exception as exc:
        main_shortcut_msg = str(exc)

    try:
        mcb = _load_module("multi_client_bot", TOOLS_DIR / "multi client bot.py")
        mcb.load_config()
    except Exception:
        pass

    # Register/persist discovered clients so Main + clones appear immediately
    refreshed = cd.discover_clients(save_cache=True)
    status_after = inspect_setup_status(str(base_dir))
    return True, {
        "base_game_dir": str(base_dir),
        "version": base_info.get("version", ""),
        "backup_ok": backup_created,
        "gpu_applied": gpu_applied,
        "window_repaired": repair_info.get("repaired", []),
        "main_shortcut_ok": main_shortcut_ok,
        "main_shortcut": main_shortcut_msg,
        "client_count": len(refreshed),
        "setup": status_after,
    }


def provision_new_client(
    unity_profile: str,
    target_root: str,
    exe_name: str,
    label: str = None,
    main_game_dir: str = None,
    launch_after: bool = False,
    create_shortcut: bool = True,
):
    """Create a fresh isolated Last Z clone folder (e.g. for an extra account)."""
    if len(unity_profile.encode("ascii", errors="ignore")) != 5:
        return False, "unity_profile must be exactly 5 ASCII characters (e.g., Alt2Z, Alt3Z, FarmZ)"
    if not exe_name.lower().endswith(".exe"):
        exe_name = f"{exe_name}.exe"

    clients = cd.discover_clients(save_cache=False)
    main_client = None
    if main_game_dir and (Path(main_game_dir) / "Survival.exe").exists():
        mg = Path(main_game_dir)
        main_client = {
            "id": "lastz",
            "label": "Main",
            "role": "main",
            "unity_profile": "LastZ",
            "game_dir": str(mg),
            "exe_path": str(mg / "Survival.exe"),
            "exe_name": "Survival.exe",
            "version": cd._read_game_version(mg),
        }
    if not main_client:
        main_client = get_main_client(clients)
    if not main_client:
        base_info = cd.detect_vanilla_base_install()
        if base_info.get("found"):
            setup_base_installation(base_info["game_dir"])
            clients = cd.discover_clients(save_cache=False)
            main_client = get_main_client(clients)
    if not main_client:
        return False, "Could not locate base Last Z installation. Run Setup & Auto-Detect first."

    ensure_base_backup(Path(main_client["game_dir"]))

    game_dir = Path(target_root) / "Game"
    try:
        game_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        return False, f"Folder '{target_root}' is not writable ({exc}). Pick a folder inside %LOCALAPPDATA% or your user drive."
    clean_label = (label or unity_profile).strip()
    client = {
        "id": unity_profile.lower(),
        "label": clean_label,
        "role": "farm",
        "unity_profile": unity_profile,
        "game_dir": str(game_dir),
        "exe_path": str(game_dir / exe_name),
        "exe_name": exe_name,
        "bot_enabled": True,
        "launch_mode": "windowed",
    }
    ok, msg = sync_client(client, main_client=main_client, force=True)
    if ok:
        apply_gpu_high_performance([game_dir / exe_name, game_dir / "Survival.exe"])
        repair_unity_window_position(unity_profile, force_reset=True)
        saved = cd.load_saved_profiles()
        existing = [
            x for x in saved.get("clients", [])
            if x.get("unity_profile") != unity_profile and str(x.get("game_dir", "")).lower() != str(game_dir).lower()
        ]
        # Ensure Main client is also saved cleanly
        if not any(x.get("role") == "main" for x in existing):
            existing.insert(0, main_client)
        existing.append(client)
        cd.save_profiles({"updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "clients": existing})
        cd.discover_clients(save_cache=True)

        extra_notes = []
        if create_shortcut:
            sc_ok, sc_res = create_account_shortcut(clean_label, game_dir / exe_name)
            if sc_ok:
                extra_notes.append(f"Shortcut: {Path(sc_res).name}")
        if launch_after:
            l_ok, l_info = launch_client(clean_label, mode="windowed", auto_sync=False)
            if l_ok:
                extra_notes.append(f"Launched PID {l_info.get('pid')}")
            else:
                extra_notes.append(f"Launch note: {l_info.get('error')}")
        if extra_notes:
            msg = f"{msg} ({'; '.join(extra_notes)})"
    return ok, msg


def _signed_dword(val: int) -> int:
    return struct.unpack("i", struct.pack("I", val & 0xFFFFFFFF))[0]


def repair_unity_window_position(unity_profile: str, force_reset: bool = False) -> dict:
    """Reset off-screen/minimized (-32000) Unity & AspectRatioController registry coordinates."""
    if not unity_profile:
        return {"profile": unity_profile, "repaired": [], "error": "empty profile"}
    subkey = f"Software\\ReadyGo\\{unity_profile}"
    repaired = []
    pos_keys = (
        ("Screenmanager Window Position X_h4088080503", 80),
        ("Screenmanager Window Position Y_h4088080502", 80),
        ("WindowX_h2353518033", 80),
        ("WindowY_h2353518032", 80),
    )
    dim_keys = (
        ("Screenmanager Resolution Width_h182942802", 1280),
        ("Screenmanager Resolution Window Width_h2524650974", 1280),
        ("WindowWidth_h1980486703", 1280),
        ("Screenmanager Resolution Height_h2627697771", 720),
        ("Screenmanager Resolution Window Height_h1684712807", 720),
        ("WindowHeight_h3880833654", 720),
    )
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE)
    except OSError as e:
        return {"profile": unity_profile, "repaired": [], "error": str(e)}

    try:
        with key:
            for name, default_val in pos_keys:
                try:
                    cur, typ = winreg.QueryValueEx(key, name)
                    sval = _signed_dword(cur) if (typ == winreg.REG_DWORD and isinstance(cur, int)) else -99999
                except FileNotFoundError:
                    sval = None
                if force_reset or sval is None or sval < -100 or sval > 10000:
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, default_val)
                    repaired.append(f"{name}:{sval}->{default_val}")

            for name, default_val in dim_keys:
                try:
                    cur, typ = winreg.QueryValueEx(key, name)
                    sval = _signed_dword(cur) if (typ == winreg.REG_DWORD and isinstance(cur, int)) else 0
                except FileNotFoundError:
                    continue
                if sval <= 0 or sval > 7680:
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, default_val)
                    repaired.append(f"{name}:{sval}->{default_val}")

            if repaired:
                try:
                    winreg.SetValueEx(key, "Screenmanager Fullscreen mode_h3630240806", 0, winreg.REG_DWORD, 3)
                except OSError:
                    pass
    except OSError as e:
        return {"profile": unity_profile, "repaired": repaired, "error": str(e)}

    return {"profile": unity_profile, "repaired": repaired}


def show_process_windows(pid: int) -> int:
    """Restore any hidden/minimized/off-screen top-level UnityWndClass windows for pid."""
    import ctypes.wintypes as wt
    user32 = ctypes.windll.user32

    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    enum_cb_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    restored = 0

    def callback(hwnd, _):
        nonlocal restored
        proc_id = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
        if proc_id.value != pid:
            return True
        cls_buf = ctypes.create_unicode_buffer(128)
        user32.GetClassNameW(hwnd, cls_buf, 128)
        cls_name = cls_buf.value
        # Strictly target ONLY the real Unity game window ("UnityWndClass").
        # Never show/resize Win32 system helper windows (Default IME, MSCTFIME UI, GDI+ Window) which are WS_DISABLED and block clicks!
        if cls_name == "UnityWndClass":
            user32.EnableWindow(hwnd, True)
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.ShowWindow(hwnd, 5)  # SW_SHOW
            rect = RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                if rect.left < -100 or rect.top < -100 or rect.left > 10000 or (rect.bottom - rect.top) > 1600 or (rect.right - rect.left) <= 100:
                    # SWP_NOZORDER | SWP_SHOWWINDOW
                    user32.SetWindowPos(hwnd, 0, 100, 80, 1280, 720, 0x0004 | 0x0040)
            try:
                user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
            restored += 1
        elif cls_name in ("IME", "MSCTFIME UI", "GDI+ Hook Window Class") and user32.IsWindowVisible(hwnd):
            user32.ShowWindow(hwnd, 0)  # Hide any accidentally shown disabled IME/GDI overlay
        return True

    user32.EnumWindows(enum_cb_type(callback), 0)
    return restored


def hide_process_windows(pid: int):
    import ctypes.wintypes as wt
    user32 = ctypes.windll.user32
    enum_cb_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    def callback(hwnd, _):
        proc_id = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
        if proc_id.value == pid:
            cls_buf = ctypes.create_unicode_buffer(128)
            user32.GetClassNameW(hwnd, cls_buf, 128)
            if cls_buf.value == "UnityWndClass":
                user32.ShowWindow(hwnd, 0)
        return True

    user32.EnumWindows(enum_cb_type(callback), 0)


def generate_launcher_arg() -> str:
    now = int(time.time())
    token = base64.b64encode(f"{now}|LZ".encode("utf-8")).decode("utf-8")
    return f"--from-launcher={token}"


def launch_client(target: str, mode: str = "windowed", auto_sync: bool = True, wait_xlua: bool = False):
    """Launch any client by id, label, unity_profile, or exe name using direct launcher token."""
    clients = cd.discover_clients(save_cache=False)
    main_client = get_main_client(clients)
    target_low = target.lower()

    selected = None
    for c in clients:
        if target_low in (
            c["id"].lower(),
            c["label"].lower(),
            c["unity_profile"].lower(),
            c["exe_name"].lower(),
            Path(c["exe_path"]).stem.lower(),
        ):
            selected = c
            break
    if not selected:
        return False, {"error": f"Client '{target}' not found"}

    repair_info = repair_unity_window_position(selected["unity_profile"])

    existing_pid = is_client_running(selected)
    if existing_pid:
        if mode == "windowed":
            show_process_windows(existing_pid)
        elif mode == "hidden":
            hide_process_windows(existing_pid)
        return True, {
            "pid": existing_pid,
            "already_running": True,
            "label": selected["label"],
            "exe": selected["exe_name"],
            "repaired": repair_info.get("repaired", []),
        }

    sync_msg = "Main"
    if auto_sync and main_client and not _same_dir(Path(main_client["game_dir"]), Path(selected["game_dir"])):
        ok_sync, sync_msg = sync_client(selected, main_client=main_client, force=False)
        if not ok_sync:
            return False, {"error": sync_msg}

    exe_path = Path(selected["exe_path"])
    work_dir = Path(selected["game_dir"])
    env = os.environ.copy()
    env["__COMPAT_LAYER"] = "DISABLEDXMAXIMIZEDWINDOWEDMODE"

    args = [str(exe_path), generate_launcher_arg()]
    startupinfo = None

    if mode == "hidden":
        args.extend(["-screen-width", "640", "-screen-height", "360", "-screen-fullscreen", "0"])
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
    elif mode == "eco":
        args.extend(["-screen-width", "960", "-screen-height", "540", "-screen-fullscreen", "0"])
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 1  # SW_SHOWNORMAL (compact visible window instead of invisible minimized)
    else:
        args.extend(["-screen-width", "1280", "-screen-height", "720", "-screen-fullscreen", "0"])
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 1  # SW_SHOWNORMAL (override parent SW_HIDE inheritance)

    base_flags = subprocess.CREATE_NEW_PROCESS_GROUP
    breakaway_flag = getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000)
    popen_kwargs = dict(
        cwd=str(work_dir),
        env=env,
        startupinfo=startupinfo,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    try:
        proc = subprocess.Popen(args, creationflags=base_flags | breakaway_flag, **popen_kwargs)
    except OSError:
        proc = subprocess.Popen(args, creationflags=base_flags, **popen_kwargs)

    if mode == "hidden":
        for _ in range(10):
            time.sleep(0.5)
            hide_process_windows(proc.pid)
            if proc.poll() is not None:
                return False, {"error": f"{selected['exe_name']} exited early with code {proc.returncode}"}
    else:
        # Wait briefly for Unity to create its main window, then ensure it is visible and on-screen
        for _ in range(8):
            time.sleep(0.45)
            if proc.poll() is not None:
                return False, {"error": f"{selected['exe_name']} exited early with code {proc.returncode}"}
            if show_process_windows(proc.pid) > 0:
                break

    if wait_xlua:
        deadline = time.time() + 30.0
        while time.time() < deadline:
            if proc.poll() is not None:
                return False, {"error": f"{selected['exe_name']} exited early with code {proc.returncode}"}
            if cd._xlua_loaded(proc.pid):
                break
            if mode == "hidden":
                hide_process_windows(proc.pid)
            time.sleep(1.0)

    return True, {
        "pid": proc.pid,
        "already_running": False,
        "label": selected["label"],
        "exe": selected["exe_name"],
        "profile": selected["unity_profile"],
        "sync": sync_msg,
        "mode": mode,
    }


def stop_client(target: str):
    target_low = target.lower()
    if target_low in ("all", "farms", "all_farms"):
        running = cd.find_running_processes()
        if target_low in ("farms", "all_farms"):
            targets = [p for p in running if str(p.get("role") or "").lower() != "main"]
        else:
            targets = list(running)
        if not targets:
            return True, f"No matching {'farm ' if 'farm' in target_low else ''}clients running"
        msgs = []
        ok_all = True
        for proc_info in targets:
            pid = int(proc_info["pid"])
            lbl = proc_info.get("label") or proc_info.get("exe_name") or f"PID {pid}"
            try:
                psutil.Process(pid).terminate()
                msgs.append(f"Terminated {lbl} ({proc_info.get('exe_name')}, PID {pid})")
            except Exception as e:
                ok_all = False
                msgs.append(f"Failed {lbl} (PID {pid}): {e}")
        return ok_all, "; ".join(msgs)

    clients = cd.discover_clients(save_cache=False)
    for c in clients:
        if target_low in (
            c["id"].lower(),
            c["label"].lower(),
            c["unity_profile"].lower(),
            c["exe_name"].lower(),
        ):
            pid = is_client_running(c)
            if not pid:
                return True, f"{c['label']} is not running"
            try:
                psutil.Process(pid).terminate()
                return True, f"Terminated {c['label']} ({c['exe_name']}, PID {pid})"
            except Exception as e:
                return False, str(e)
    return False, f"Client '{target}' not found"


if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action == "sync":
        force = "--force" in sys.argv
        print(json.dumps(sync_all_clients(force=force), indent=2, ensure_ascii=False))
    elif action == "launch" and len(sys.argv) >= 3:
        target = sys.argv[2]
        mode = sys.argv[3] if len(sys.argv) >= 4 else "windowed"
        ok, info = launch_client(target, mode=mode, wait_xlua="--wait" in sys.argv)
        print(json.dumps({"ok": ok, **info}, indent=2, ensure_ascii=False))
        sys.exit(0 if ok else 1)
    elif action == "stop" and len(sys.argv) >= 3:
        ok, msg = stop_client(sys.argv[2])
        print(msg)
        sys.exit(0 if ok else 1)
    elif action == "provision" and len(sys.argv) >= 5:
        ok, msg = provision_new_client(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
        print(msg)
        sys.exit(0 if ok else 1)
    elif action == "repair-windows":
        target = sys.argv[2].lower() if len(sys.argv) >= 3 else "farms"
        clients = cd.discover_clients(save_cache=False)
        results = []
        for c in clients:
            if target == "all" or (target == "farms" and c["role"] != "main") or target in (c["id"].lower(), c["label"].lower(), c["unity_profile"].lower()):
                info = repair_unity_window_position(c["unity_profile"], force_reset="--force" in sys.argv)
                pid = is_client_running(c)
                if pid:
                    info["windows_restored"] = show_process_windows(pid)
                results.append(info)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        sys.exit(0)
    elif action == "inspect-setup":
        base_arg = sys.argv[2] if len(sys.argv) >= 3 else None
        print(json.dumps(inspect_setup_status(base_arg), indent=2, ensure_ascii=False))
        sys.exit(0)
    elif action == "setup-base":
        base_arg = sys.argv[2] if len(sys.argv) >= 3 else None
        ok, info = setup_base_installation(base_arg)
        print(json.dumps({"ok": ok, **info}, indent=2, ensure_ascii=False))
        sys.exit(0 if ok else 1)
    elif action == "heal-launchers":
        dry_run = "--dry-run" in sys.argv
        force = "--force" in sys.argv
        report = heal_all_farm_launchers(dry_run=dry_run, force=force)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0 if report.get("ok") else 1)
    else:
        clients = cd.discover_clients(save_cache=True)
        main_c = get_main_client(clients)
        report = []
        for c in clients:
            needs, reason = client_needs_sync(main_c, c)
            report.append({
                "label": c["label"],
                "profile": c["unity_profile"],
                "version": c["version"],
                "uid": c["uid"],
                "server_id": c["server_id"],
                "needs_sync": needs,
                "sync_reason": reason,
                "running_pid": is_client_running(c),
            })
        print(json.dumps(report, indent=2, ensure_ascii=False))
