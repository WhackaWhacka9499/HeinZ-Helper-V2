"""Standalone Last Z Windows Unity Game Engine Manager.

Downloads, updates, imports, and provisions lightweight isolated account slots
from `<engine>/Game/` using ReadyGo's official PC CDN protocol.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

try:
    import requests
    from requests.adapters import HTTPAdapter
except Exception:
    requests = None  # type: ignore[assignment]
    HTTPAdapter = None  # type: ignore[assignment]

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

VERSION_URL = (
    "https://gvr-lm.florereapps.com/gameservice/getversion.php"
    "?packageName=com.readygo.barrel.windows&type=game&gm="
)
MANIFEST_URL = (
    "https://gvr-lm.florereapps.com/gameservice/getversiondetail.php"
    "?packageName=com.readygo.barrel.windows&type=game&gm="
)
CDN_BASE_URL = "https://cdn-lm.omnilojo.app/hotupdate/com.readygo.barrel.windows"

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

ENGINE_METADATA_FILE = "engine metadata.json"
SLOT_METADATA_FILE = "slot metadata.json"
USER_AGENT = "HeinZ-EngineManager/2.0"

REQUIRED_GAME_FILES: tuple[str, ...] = (
    "Survival.exe",
    "GameAssembly.dll",
    "Survival_Data/globalgamemanagers",
)

ALLOWED_MASTER_EXES: frozenset[str] = frozenset({
    "survival.exe",
    "unitycrashhandler64.exe",
    "unitycrashhandler32.exe",
})

SHARED_TOP_LEVEL_DIRS: tuple[str, ...] = (
    "config",
    "LastZ_BurstDebugInformation_DoNotShip",
)

PRIVATE_SURVIVAL_DATA_FILES: frozenset[str] = frozenset({
    "app.info",
    "globalgamemanagers",
})

KNOWN_MARKERS: tuple[bytes, ...] = (
    b"LastZ",
    b"FarmZ",
    *(f"Alt{i}Z".encode("ascii") for i in range(2, 10)),
    *(f"Hz{i:02d}Z".encode("ascii") for i in range(1, 100)),
    *(f"Ac{i:02d}Z".encode("ascii") for i in range(1, 100)),
)

_MD5_HEX_RE = re.compile(r"^[0-9a-f]{32}$")
_DRIVE_PREFIX_RE = re.compile(r"^[A-Za-z]:")
_INVALID_WIN_CHARS_RE = re.compile(r'[\x00-\x1f<>:"|?*]')
_READYGO_EXACT_PREFIX = b"ReadyGo\x00\x05\x00\x00\x00"


def _hidden_subproc_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {
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


def _is_writable_dir(path: Path) -> bool:
    """Test whether `path` (or its existing parent if not yet created) is writable."""
    try:
        if path.exists():
            if not path.is_dir():
                return False
            probe = path / f".heinz-write-probe-{os.getpid()}-{threading.get_ident()}"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return True
        parent = path.parent
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent
        if not parent.is_dir():
            return False
        probe = parent / f".heinz-write-probe-{os.getpid()}-{threading.get_ident()}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _same_path(a: Path, b: Path) -> bool:
    try:
        return str(a.resolve()).lower() == str(b.resolve()).lower()
    except OSError:
        return str(a).lower() == str(b).lower()


def _is_reparse_or_junction(path: Path) -> bool:
    """Return True if `path` is an NTFS junction, directory symlink, or reparse point."""
    try:
        isjunction = getattr(os.path, "isjunction", None)
        if callable(isjunction) and isjunction(path):
            return True
    except OSError:
        pass
    try:
        if os.path.islink(path):
            return True
    except OSError:
        pass
    try:
        st = os.lstat(path)
        attrs = getattr(st, "st_file_attributes", 0)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
        return bool(attrs & reparse_flag)
    except OSError:
        return False


def _remove_dir_or_junction(path: Path) -> None:
    """Safely remove a directory or NTFS junction without traversing junction targets."""
    if not path.exists() and not _is_reparse_or_junction(path):
        return
    if _is_reparse_or_junction(path):
        os.rmdir(path)
        return
    if path.is_file():
        path.unlink(missing_ok=True)
        return
    # Walk bottom-up so any nested junctions are removed with os.rmdir cleanly
    for root, dirs, files in os.walk(path, topdown=False, followlinks=False):
        root_p = Path(root)
        for fname in files:
            fpath = root_p / fname
            try:
                fpath.unlink()
            except PermissionError:
                os.chmod(fpath, stat.S_IWRITE)
                fpath.unlink()
        for dname in dirs:
            dpath = root_p / dname
            if _is_reparse_or_junction(dpath):
                os.rmdir(dpath)
            else:
                try:
                    os.rmdir(dpath)
                except OSError:
                    shutil.rmtree(dpath, ignore_errors=False)
    os.rmdir(path)


def _atomic_write_bytes(dst: Path, payload: bytes) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(f"{dst.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        tmp.write_bytes(payload)
        os.replace(tmp, dst)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _atomic_write_text(dst: Path, content: str, encoding: str = "utf-8") -> None:
    _atomic_write_bytes(dst, content.encode(encoding))


def _atomic_copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(f"{dst.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _file_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def _create_cdn_session(pool_size: int = 32):
    """Build a pooled HTTP Keep-Alive session for high-throughput ReadyGo CDN downloads."""
    if requests is None or HTTPAdapter is None:
        return None
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "identity",
    })
    adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess


def _same_file_contents(src: Path, dst: Path) -> bool:
    if not dst.is_file():
        return False
    try:
        s_st = src.stat()
        d_st = dst.stat()
        if s_st.st_size != d_st.st_size:
            return False
    except OSError:
        return False
    return _file_md5(src) == _file_md5(dst)


def resolve_engine_root() -> Path:
    """Resolve the standalone engine root directory.

    Priority:
    1. `HEINZ_ENGINE_DIR` environment variable if set and non-empty.
    2. Frozen build (`sys.frozen`): `<exe_dir>/engine` if writable,
       else `%LOCALAPPDATA%/HeinZ V2/engine`.
    3. Source checkout: `<REPO_ROOT>/engine`.
    """
    env_dir = os.environ.get("HEINZ_ENGINE_DIR", "").strip()
    if env_dir:
        return Path(env_dir)

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        portable = exe_dir / "engine"
        if _is_writable_dir(portable):
            return portable
        local_app = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(local_app) / "HeinZ V2" / "engine"

    return REPO_ROOT / "engine"


def resolve_engine_game_dir(engine_root: Path | None = None) -> Path:
    """Return `<engine_root>/Game`."""
    root = Path(engine_root) if engine_root is not None else resolve_engine_root()
    return root / "Game"


def resolve_accounts_root(engine_root: Path | None = None) -> Path:
    """Return `<engine_root>/accounts`."""
    root = Path(engine_root) if engine_root is not None else resolve_engine_root()
    return root / "accounts"


def build_cdn_file_url(cdn_base: str, version: str, rel_path: str) -> str:
    """Construct an official ReadyGo CDN download URL with safely encoded path segments."""
    clean_base = str(cdn_base).rstrip("/")
    clean_ver = urllib.parse.quote(str(version).strip(), safe="")
    clean_rel = validate_manifest_rel_path(rel_path)
    encoded_rel = "/".join(urllib.parse.quote(seg, safe="-._~") for seg in clean_rel.split("/"))
    return f"{clean_base}/Game_{clean_ver}/{encoded_rel}"


def validate_manifest_rel_path(rel_path: Any) -> str:
    """Validate a relative manifest file path and reject any path-traversal or unsafe path."""
    if not isinstance(rel_path, str):
        raise ValueError(f"Manifest path must be a string, got {type(rel_path).__name__}")
    if not rel_path or not rel_path.strip():
        raise ValueError("Manifest path must not be empty")
    if "\x00" in rel_path:
        raise ValueError(f"Manifest path contains null byte: {rel_path!r}")
    if "\\" in rel_path:
        raise ValueError(f"Manifest path must not contain backslashes: {rel_path!r}")
    if rel_path.startswith("/"):
        raise ValueError(f"Manifest path must not be absolute: {rel_path!r}")
    if _DRIVE_PREFIX_RE.match(rel_path) or ":" in rel_path:
        raise ValueError(f"Manifest path must not contain a drive letter or colon: {rel_path!r}")
    if _INVALID_WIN_CHARS_RE.search(rel_path):
        raise ValueError(f"Manifest path contains illegal characters: {rel_path!r}")

    parts = rel_path.split("/")
    for seg in parts:
        if not seg or seg in (".", ".."):
            raise ValueError(f"Manifest path contains unsafe segment {seg!r}: {rel_path!r}")
        if seg.endswith(" ") or seg.endswith("."):
            raise ValueError(f"Manifest path segment has trailing space or dot: {rel_path!r}")
    return rel_path


def read_engine_version(game_dir: Path) -> str:
    """Read `config/Game_version.txt` cleanly, returning empty string if missing."""
    try:
        vf = Path(game_dir) / "config" / "Game_version.txt"
        if not vf.is_file():
            return ""
        return vf.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return ""


def is_valid_game_dir(game_dir: Path) -> bool:
    """Verify Survival.exe, GameAssembly.dll, and Survival_Data/globalgamemanagers exist and are non-empty."""
    gd = Path(game_dir)
    try:
        if not gd.is_dir():
            return False
        for rel in REQUIRED_GAME_FILES:
            fp = gd / Path(*rel.split("/"))
            if not fp.is_file() or fp.stat().st_size <= 0:
                return False
        return True
    except OSError:
        return False


def _load_client_discovery_module():
    cd_path = TOOLS_DIR / "client discovery.py"
    if not cd_path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("heinz_gem_client_discovery", str(cd_path))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _label_for_local_install(game_dir: Path) -> str:
    parent = game_dir.parent
    local_app = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app:
        try:
            if str(game_dir.resolve()).lower().startswith(str(Path(local_app).resolve()).lower()):
                return f"LocalAppData ({parent.name})"
        except OSError:
            pass
    return f"{parent.name} ({parent})"


def detect_existing_local_installs(engine_root: Path | None = None) -> list[dict[str, str]]:
    """Find existing local Last Z `Game/` installations, excluding our managed engine directory."""
    engine_game_dir = resolve_engine_game_dir(engine_root)
    candidates: list[Path] = []

    local_app = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app:
        candidates.append(Path(local_app) / "Last Z" / "Game")
    else:
        expanded = Path(os.path.expandvars(r"%LOCALAPPDATA%\Last Z\Game"))
        if "%" not in str(expanded):
            candidates.append(expanded)

    candidates.extend([
        Path(r"G:\Last Z\Game"),
        Path(r"G:\Last Z_AppData\Game"),
        Path(r"C:\Program Files\Last Z\Game"),
    ])

    cd_mod = _load_client_discovery_module()
    if cd_mod is not None and hasattr(cd_mod, "detect_vanilla_base_install"):
        try:
            vanilla = cd_mod.detect_vanilla_base_install()
            if isinstance(vanilla, dict) and vanilla.get("found") and vanilla.get("game_dir"):
                candidates.append(Path(str(vanilla["game_dir"])))
        except Exception:
            pass

    results: list[dict[str, str]] = []
    seen_keys: set[str] = set()

    for cand in candidates:
        if _same_path(cand, engine_game_dir):
            continue
        try:
            norm_key = str(cand.resolve()).lower()
        except OSError:
            norm_key = str(cand).lower()
        if norm_key in seen_keys:
            continue
        seen_keys.add(norm_key)
        if not is_valid_game_dir(cand):
            continue
        results.append({
            "game_dir": str(cand),
            "version": read_engine_version(cand),
            "label": _label_for_local_install(cand),
        })

    return results


def fetch_remote_engine_version(version_url: str = VERSION_URL, timeout: float = 8.0) -> str:
    """GET remote Last Z Windows game version string (e.g. '582')."""
    req = urllib.request.Request(version_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="ignore").strip().strip('"').strip("'")
    if not raw:
        raise ValueError("Remote engine version endpoint returned empty response")
    if any(bad in raw for bad in ("/", "\\", "..", "\x00", "\r", "\n")):
        raise ValueError(f"Remote engine version contains unsafe characters: {raw!r}")
    return raw


def fetch_remote_manifest(
    manifest_url: str = MANIFEST_URL,
    timeout: float = 15.0,
) -> list[tuple[str, str, int]]:
    """GET and validate the remote JSON file manifest `[rel_path, md5_hex, size_bytes]`."""
    req = urllib.request.Request(manifest_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw_text = resp.read().decode("utf-8", errors="replace")

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Remote manifest is not valid JSON: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError(f"Remote manifest must be a JSON array, got {type(payload).__name__}")

    entries: list[tuple[str, str, int]] = []
    seen_paths: set[str] = set()

    for idx, item in enumerate(payload):
        if not isinstance(item, (list, tuple)) or len(item) < 3:
            raise ValueError(f"Manifest entry #{idx} must be [rel_path, md5_hex, size_bytes]")
        rel_path = validate_manifest_rel_path(item[0])
        md5_hex = str(item[1]).strip().lower()
        if not _MD5_HEX_RE.fullmatch(md5_hex):
            raise ValueError(f"Manifest entry #{idx} ({rel_path}) has invalid MD5: {item[1]!r}")
        raw_size = item[2]
        if isinstance(raw_size, bool):
            raise ValueError(f"Manifest entry #{idx} ({rel_path}) has invalid boolean size")
        try:
            size_bytes = int(raw_size)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Manifest entry #{idx} ({rel_path}) has non-integer size: {raw_size!r}") from exc
        if size_bytes < 0:
            raise ValueError(f"Manifest entry #{idx} ({rel_path}) has negative size: {size_bytes}")

        low_key = rel_path.lower()
        if low_key in seen_paths:
            continue
        seen_paths.add(low_key)
        entries.append((rel_path, md5_hex, size_bytes))

    return entries


def _read_engine_metadata(engine_root: Path) -> dict[str, Any]:
    meta_path = engine_root / ENGINE_METADATA_FILE
    if not meta_path.is_file():
        return {}
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_engine_metadata(
    engine_root: Path,
    version: str,
    source: str,
    file_count: int,
    total_bytes: int,
    source_type: str = "cdn",
) -> None:
    payload = {
        "version": str(version or ""),
        "source": str(source or ""),
        "source_type": source_type,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "file_count": int(file_count),
        "total_bytes": int(total_bytes),
    }
    _atomic_write_text(
        engine_root / ENGINE_METADATA_FILE,
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def _fast_estimate_dir_bytes(game_dir: Path, time_budget_sec: float = 0.25) -> int:
    """Estimate directory byte size quickly via iterative os.scandir with a strict time cap."""
    total = 0
    deadline = time.monotonic() + max(0.05, time_budget_sec)
    stack: list[Path] = [game_dir]
    visited_entries = 0

    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for entry in it:
                    visited_entries += 1
                    if (visited_entries & 127) == 0 and time.monotonic() >= deadline:
                        return total
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            if not _is_reparse_or_junction(Path(entry.path)):
                                stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue

    return total


def get_engine_status(
    check_remote: bool = False,
    engine_root: Path | None = None,
    version_url: str = VERSION_URL,
) -> dict[str, Any]:
    """Inspect local engine installation status and optionally check remote CDN version."""
    root = Path(engine_root) if engine_root is not None else resolve_engine_root()
    game_dir = resolve_engine_game_dir(root)
    installed = is_valid_game_dir(game_dir)
    local_version = read_engine_version(game_dir) if installed else ""

    remote_version = ""
    remote_error = ""
    if check_remote:
        try:
            remote_version = fetch_remote_engine_version(version_url=version_url)
        except Exception as exc:
            remote_error = str(exc)

    update_available = bool(installed and remote_version and (local_version != remote_version))

    size_mb = 0.0
    if installed:
        meta = _read_engine_metadata(root)
        cached_bytes = meta.get("total_bytes")
        cached_ver = str(meta.get("version") or "")
        if (
            isinstance(cached_bytes, (int, float))
            and cached_bytes >= 0
            and cached_ver == local_version
            and (cached_bytes > 0 or meta.get("file_count", 0) > 0)
        ):
            size_mb = round(float(cached_bytes) / (1024.0 * 1024.0), 2)
        else:
            est_bytes = _fast_estimate_dir_bytes(game_dir)
            size_mb = round(float(est_bytes) / (1024.0 * 1024.0), 2)

    detected_local = detect_existing_local_installs(engine_root=root)
    return {
        "ok": True,
        "installed": installed,
        "engine_root": str(root),
        "engine_game_dir": str(game_dir),
        "local_version": local_version,
        "remote_version": remote_version,
        "update_available": update_available,
        "size_mb": size_mb,
        "detected_local_installs": detected_local,
        "remote_error": remote_error,
    }


def patch_unity_identity(game_dir: Path, unity_profile: str) -> bool:
    """Patch Survival_Data/app.info and Survival_Data/globalgamemanagers to `unity_profile`.

    Always writes atomically via temp file + `os.replace`, so existing hardlinks
    are never mutated in place.
    """
    if not isinstance(unity_profile, str) or len(unity_profile) != 5 or not unity_profile.isascii():
        raise ValueError(f"Unity profile name must be exactly 5 ASCII characters (got {unity_profile!r}).")

    gd = Path(game_dir)
    survival_data = gd / "Survival_Data"
    if not survival_data.is_dir():
        raise FileNotFoundError(f"Missing Survival_Data folder in {gd}")

    app_info = survival_data / "app.info"
    ggm = survival_data / "globalgamemanagers"
    target_bytes = unity_profile.encode("ascii")

    markers: list[bytes] = list(KNOWN_MARKERS)
    if app_info.is_file():
        lines = [
            ln.strip()
            for ln in app_info.read_text(encoding="utf-8", errors="ignore").splitlines()
            if ln.strip()
        ]
        if len(lines) >= 2 and len(lines[1]) == 5 and lines[1].isascii():
            prev_b = lines[1].encode("ascii")
            if prev_b not in markers:
                markers.insert(0, prev_b)

    _atomic_write_text(app_info, f"ReadyGo\n{unity_profile}", encoding="utf-8")

    if ggm.is_file():
        data = bytearray(ggm.read_bytes())
        already_exact = (_READYGO_EXACT_PREFIX + target_bytes) in data
        if not already_exact:
            replaced = False
            # 1. Exact Unity PlayerSettings record: ReadyGo\x00\x05\x00\x00\x00<marker>
            for marker in markers:
                exact_pat = _READYGO_EXACT_PREFIX + marker
                e_idx = data.find(exact_pat)
                if e_idx >= 0:
                    start = e_idx + len(_READYGO_EXACT_PREFIX)
                    data[start : start + 5] = target_bytes
                    replaced = True
                    break

            # 2. Length-prefixed marker within 256 bytes of ReadyGo\x00
            readygo_pos = data.find(b"ReadyGo\x00")
            if not replaced and readygo_pos >= 0:
                if data.find(b"\x05\x00\x00\x00" + target_bytes, readygo_pos, readygo_pos + 256) >= 0:
                    replaced = True
                else:
                    for marker in markers:
                        lp_idx = data.find(b"\x05\x00\x00\x00" + marker, readygo_pos, readygo_pos + 256)
                        if lp_idx >= 0:
                            start = lp_idx + 4
                            data[start : start + 5] = target_bytes
                            replaced = True
                            break

            # 3. Fallback scan for known marker if target not already present
            if not replaced:
                if target_bytes in data:
                    replaced = True
                else:
                    for marker in markers:
                        idx = data.find(marker, readygo_pos if readygo_pos >= 0 else 0)
                        if idx < 0:
                            idx = data.find(marker)
                        if idx >= 0:
                            data[idx : idx + 5] = target_bytes
                            replaced = True
                            break

            if not replaced:
                raise RuntimeError(f"Could not find ReadyGo profile marker in {ggm}")

            _atomic_write_bytes(ggm, bytes(data))
        else:
            # Ensure private non-hardlinked copy even when bytes already matched target
            try:
                if ggm.stat().st_nlink > 1:
                    _atomic_write_bytes(ggm, bytes(data))
            except OSError:
                pass

    return True


def _emit_progress(
    progress_cb: Callable[[dict[str, Any]], None] | None,
    *,
    stage: str,
    done_files: int,
    total_files: int,
    done_bytes: int,
    total_bytes: int,
    current_file: str,
    start_ts: float,
) -> None:
    if progress_cb is None:
        return
    elapsed = max(0.001, time.monotonic() - start_ts)
    speed_mbps = round((done_bytes / (1024.0 * 1024.0)) / elapsed, 2)
    if total_bytes > 0:
        pct = min(100.0, round((done_bytes * 100.0) / total_bytes, 2))
    elif total_files > 0:
        pct = min(100.0, round((done_files * 100.0) / total_files, 2))
    else:
        pct = 100.0 if stage == "done" else 0.0
    try:
        progress_cb({
            "stage": stage,
            "done_files": int(done_files),
            "total_files": int(total_files),
            "done_bytes": int(done_bytes),
            "total_bytes": int(total_bytes),
            "pct": float(pct),
            "current_file": str(current_file),
            "speed_mbps": float(speed_mbps),
        })
    except Exception:
        pass


def _should_skip_import_top_entry(entry_name: str, is_dir: bool) -> bool:
    low = entry_name.lower()
    if low == "_heinz_backup":
        return True
    if is_dir:
        if low.endswith("_data") and low != "survival_data":
            return True
        return False
    if low.endswith(".exe") and low not in ALLOWED_MASTER_EXES:
        return True
    return False


def _collect_import_files(src_dir: Path) -> list[tuple[Path, Path, int]]:
    """Collect all clean game files from `src_dir`, filtering backups, custom exes, and alt *_Data dirs."""
    files: list[tuple[Path, Path, int]] = []
    for root, dirs, filenames in os.walk(src_dir, topdown=True, followlinks=True):
        root_p = Path(root)
        rel_root = root_p.relative_to(src_dir)
        is_top = len(rel_root.parts) == 0

        kept_dirs: list[str] = []
        for dname in dirs:
            if dname.lower() == "_heinz_backup":
                continue
            if is_top and _should_skip_import_top_entry(dname, is_dir=True):
                continue
            kept_dirs.append(dname)
        dirs[:] = sorted(kept_dirs, key=str.lower)

        for fname in sorted(filenames, key=str.lower):
            if is_top and _should_skip_import_top_entry(fname, is_dir=False):
                continue
            low = fname.lower()
            if low.endswith(".tmp") or low.endswith(".part"):
                continue
            src_fp = root_p / fname
            rel_fp = rel_root / fname
            try:
                sz = src_fp.stat().st_size
            except OSError:
                continue
            files.append((src_fp, rel_fp, sz))
    return files


def import_local_engine(
    source_game_dir: str | Path,
    engine_root: Path | None = None,
    progress_cb: Callable[[dict[str, Any]], None] | None = None,
    use_hardlinks: bool = False,
) -> dict[str, Any]:
    """Import an existing local Last Z `Game/` install into our standalone master engine directory."""
    src_dir = Path(source_game_dir)
    root = Path(engine_root) if engine_root is not None else resolve_engine_root()
    dst_dir = resolve_engine_game_dir(root)

    if not is_valid_game_dir(src_dir):
        return {
            "ok": False,
            "engine_game_dir": str(dst_dir),
            "local_version": "",
            "copied_files": 0,
            "total_bytes": 0,
            "message": f"Invalid Last Z game directory: {src_dir}",
        }

    if _same_path(src_dir, dst_dir):
        patch_unity_identity(dst_dir, "LastZ")
        ver = read_engine_version(dst_dir)
        est = _fast_estimate_dir_bytes(dst_dir, time_budget_sec=2.0)
        return {
            "ok": True,
            "engine_game_dir": str(dst_dir),
            "local_version": ver,
            "copied_files": 0,
            "total_bytes": est,
            "message": f"Engine directory is already at {dst_dir} (v{ver or 'unknown'})",
        }

    start_ts = time.monotonic()
    _emit_progress(
        progress_cb,
        stage="scanning",
        done_files=0,
        total_files=0,
        done_bytes=0,
        total_bytes=0,
        current_file="",
        start_ts=start_ts,
    )

    items = _collect_import_files(src_dir)
    total_files = len(items)
    total_bytes = sum(sz for _, _, sz in items)

    dst_dir.mkdir(parents=True, exist_ok=True)
    expected_rel_set = {rel.as_posix().lower() for _, rel, _ in items}

    # Remove stale files/dirs in engine_game_dir that do not belong to clean import
    for cur_root, cur_dirs, cur_files in os.walk(dst_dir, topdown=False, followlinks=False):
        cur_p = Path(cur_root)
        rel_parent = cur_p.relative_to(dst_dir)
        for fname in cur_files:
            rel_key = (rel_parent / fname).as_posix().lower()
            if rel_key not in expected_rel_set:
                try:
                    (cur_p / fname).unlink(missing_ok=True)
                except OSError:
                    pass
        for dname in cur_dirs:
            dp = cur_p / dname
            if _is_reparse_or_junction(dp):
                try:
                    os.rmdir(dp)
                except OSError:
                    pass
            else:
                try:
                    if not any(dp.iterdir()):
                        dp.rmdir()
                except OSError:
                    pass

    done_files = 0
    done_bytes = 0
    same_drive = src_dir.resolve().drive.lower() == dst_dir.resolve().drive.lower()

    for src_fp, rel_fp, sz in items:
        dst_fp = dst_dir / rel_fp
        dst_fp.parent.mkdir(parents=True, exist_ok=True)

        rel_posix_low = rel_fp.as_posix().lower()
        is_private_identity = rel_posix_low in (
            "survival_data/app.info",
            "survival_data/globalgamemanagers",
        )

        # Always unlink target first so we never write through a pre-existing hardlink
        if dst_fp.exists() or os.path.islink(dst_fp):
            try:
                dst_fp.unlink()
            except PermissionError:
                os.chmod(dst_fp, stat.S_IWRITE)
                dst_fp.unlink()

        linked = False
        if use_hardlinks and same_drive and not is_private_identity:
            try:
                os.link(src_fp, dst_fp)
                linked = True
            except OSError:
                linked = False
        if not linked:
            shutil.copy2(src_fp, dst_fp)

        done_files += 1
        done_bytes += sz
        _emit_progress(
            progress_cb,
            stage="copying",
            done_files=done_files,
            total_files=total_files,
            done_bytes=done_bytes,
            total_bytes=total_bytes,
            current_file=rel_fp.as_posix(),
            start_ts=start_ts,
        )

    # Reset master engine identity cleanly back to vanilla LastZ
    patch_unity_identity(dst_dir, "LastZ")
    local_version = read_engine_version(dst_dir)

    _write_engine_metadata(
        root,
        version=local_version,
        source=str(src_dir),
        file_count=done_files,
        total_bytes=total_bytes,
        source_type="local_import",
    )

    _emit_progress(
        progress_cb,
        stage="done",
        done_files=done_files,
        total_files=total_files,
        done_bytes=total_bytes,
        total_bytes=total_bytes,
        current_file="",
        start_ts=start_ts,
    )

    size_mb = total_bytes / (1024.0 * 1024.0)
    return {
        "ok": True,
        "engine_game_dir": str(dst_dir),
        "local_version": local_version,
        "copied_files": done_files,
        "total_bytes": total_bytes,
        "message": f"Imported Last Z engine v{local_version or 'unknown'} ({done_files} files, {size_mb:.1f} MB)",
    }


def _wait_cancel_aware(cancel_event: Any, seconds: float) -> bool:
    """Sleep up to `seconds`, waking immediately if `cancel_event` is triggered. Returns True if cancelled."""
    if cancel_event is None:
        time.sleep(seconds)
        return False
    wait_fn = getattr(cancel_event, "wait", None)
    if callable(wait_fn):
        return bool(wait_fn(seconds))
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if cancel_event.is_set():
            return True
        time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
    return bool(cancel_event.is_set())


def download_or_update_engine(
    engine_root: Path | None = None,
    progress_cb: Callable[[dict[str, Any]], None] | None = None,
    cancel_event: Any = None,
    max_workers: int = 16,
    version_url: str = VERSION_URL,
    manifest_url: str = MANIFEST_URL,
    cdn_base: str = CDN_BASE_URL,
    range_threshold_bytes: int = 8 * 1024 * 1024,
    range_streams: int = 8,
) -> dict[str, Any]:
    """Download or differentially update the standalone Last Z engine from ReadyGo's official CDN.

    Uses HTTP Keep-Alive connection pooling (`requests.Session`), multi-threaded local MD5
    pre-verification, and parallel HTTP Range chunking for large binaries (`>= 8 MB`) to
    saturate gigabit connections while maintaining strict per-file MD5 integrity.
    """
    root = Path(engine_root) if engine_root is not None else resolve_engine_root()
    engine_game_dir = resolve_engine_game_dir(root)
    engine_game_dir.mkdir(parents=True, exist_ok=True)
    resolved_game_root = engine_game_dir.resolve()
    start_ts = time.monotonic()

    def _is_cancelled() -> bool:
        return bool(cancel_event is not None and cancel_event.is_set())

    if _is_cancelled():
        return {
            "ok": False,
            "engine_game_dir": str(engine_game_dir),
            "version": "",
            "downloaded_files": 0,
            "skipped_files": 0,
            "downloaded_bytes": 0,
            "failed_files": [],
            "cancelled": True,
            "message": "Engine download cancelled before start",
        }

    _emit_progress(
        progress_cb,
        stage="fetching_manifest",
        done_files=0,
        total_files=0,
        done_bytes=0,
        total_bytes=0,
        current_file="",
        start_ts=start_ts,
    )

    remote_version = fetch_remote_engine_version(version_url=version_url)
    manifest = fetch_remote_manifest(manifest_url=manifest_url)

    if _is_cancelled():
        return {
            "ok": False,
            "engine_game_dir": str(engine_game_dir),
            "version": remote_version,
            "downloaded_files": 0,
            "skipped_files": 0,
            "downloaded_bytes": 0,
            "failed_files": [],
            "cancelled": True,
            "message": "Engine download cancelled after fetching manifest",
        }

    _emit_progress(
        progress_cb,
        stage="verifying",
        done_files=0,
        total_files=len(manifest),
        done_bytes=0,
        total_bytes=0,
        current_file="",
        start_ts=start_ts,
    )

    # First pass: validate containment synchronously so path-traversal errors raise immediately
    validated_entries: list[tuple[str, str, int, Path]] = []
    total_manifest_bytes = 0
    for rel_path, expected_md5, expected_size in manifest:
        if _is_cancelled():
            return {
                "ok": False,
                "engine_game_dir": str(engine_game_dir),
                "version": remote_version,
                "downloaded_files": 0,
                "skipped_files": 0,
                "downloaded_bytes": 0,
                "failed_files": [],
                "cancelled": True,
                "message": "Engine download cancelled during verification",
            }
        total_manifest_bytes += expected_size
        dst = engine_game_dir / Path(*rel_path.split("/"))
        resolved_dst = dst.resolve()
        if not resolved_dst.is_relative_to(resolved_game_root):
            raise ValueError(f"Resolved target escapes engine directory: {rel_path!r}")
        validated_entries.append((rel_path, expected_md5, expected_size, dst))

    # Second pass: fast size check + multi-threaded MD5 verification across matching files
    to_download: list[tuple[str, str, int, Path]] = []
    candidates_to_hash: list[tuple[str, str, int, Path]] = []
    skipped_files = 0

    for item in validated_entries:
        rel_path, expected_md5, expected_size, dst = item
        if dst.is_file():
            try:
                if dst.stat().st_size == expected_size:
                    candidates_to_hash.append(item)
                    continue
            except OSError:
                pass
        to_download.append(item)

    if candidates_to_hash:
        def _verify_one(item: tuple[str, str, int, Path]) -> tuple[bool, tuple[str, str, int, Path]]:
            if _is_cancelled():
                return (False, item)
            _, expected_md5, _, dst = item
            try:
                return (_file_md5(dst) == expected_md5, item)
            except OSError:
                return (False, item)

        hash_workers = max(1, min(12, os.cpu_count() or 4, len(candidates_to_hash)))
        if hash_workers == 1:
            for item in candidates_to_hash:
                if _is_cancelled():
                    break
                matched, _ = _verify_one(item)
                if matched:
                    skipped_files += 1
                else:
                    to_download.append(item)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=hash_workers) as vpool:
                for matched, item in vpool.map(_verify_one, candidates_to_hash):
                    if _is_cancelled():
                        break
                    if matched:
                        skipped_files += 1
                    else:
                        to_download.append(item)

    if _is_cancelled():
        return {
            "ok": False,
            "engine_game_dir": str(engine_game_dir),
            "version": remote_version,
            "downloaded_files": 0,
            "skipped_files": skipped_files,
            "downloaded_bytes": 0,
            "failed_files": [],
            "cancelled": True,
            "message": "Engine download cancelled during verification",
        }

    # Start largest files first so big binaries do not trail behind small files at the end
    if len(to_download) > 1 and int(max_workers) > 1:
        to_download.sort(key=lambda item: item[2], reverse=True)

    total_dl_files = len(to_download)
    total_dl_bytes = sum(sz for _, _, sz, _ in to_download)

    state_lock = threading.Lock()
    done_files = 0
    done_bytes = 0
    downloaded_files = 0
    downloaded_bytes = 0
    failed_files: list[dict[str, str]] = []
    cancelled = False
    last_live_emit = [0.0]
    read_chunk_size = 524288  # 512 KB read buffer for high-speed streaming

    eff_workers = max(1, int(max_workers))
    eff_range_streams = max(2, min(12, int(range_streams)))
    session_pool_size = max(32, eff_workers + eff_range_streams * 2)
    cdn_session = _create_cdn_session(pool_size=session_pool_size)

    def _add_progress_bytes(delta: int, rel_path: str) -> None:
        nonlocal done_bytes
        if delta <= 0:
            return
        now = time.monotonic()
        should_emit = False
        with state_lock:
            done_bytes += delta
            cur_done_files = done_files
            cur_done_bytes = done_bytes
            if progress_cb is not None and (now - last_live_emit[0]) >= 0.2:
                last_live_emit[0] = now
                should_emit = True
        if should_emit:
            _emit_progress(
                progress_cb,
                stage="downloading",
                done_files=cur_done_files,
                total_files=total_dl_files,
                done_bytes=cur_done_bytes,
                total_bytes=total_dl_bytes,
                current_file=rel_path,
                start_ts=dl_start_ts,
            )

    def _download_single_stream(url: str, part_path: Path, rel_path: str) -> tuple[int, str]:
        """Download a file on one pooled keep-alive stream (or urllib fallback)."""
        attempt_bytes = 0
        h = hashlib.md5()
        try:
            if cdn_session is not None:
                with cdn_session.get(url, stream=True, timeout=(10.0, 30.0)) as resp:
                    resp.raise_for_status()
                    with open(part_path, "wb") as out_fh:
                        for chunk in resp.iter_content(chunk_size=read_chunk_size):
                            if _is_cancelled():
                                raise InterruptedError("Download cancelled")
                            if not chunk:
                                continue
                            out_fh.write(chunk)
                            h.update(chunk)
                            clen = len(chunk)
                            attempt_bytes += clen
                            _add_progress_bytes(clen, rel_path)
            else:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=30.0) as resp, open(part_path, "wb") as out_fh:
                    while True:
                        if _is_cancelled():
                            raise InterruptedError("Download cancelled")
                        chunk = resp.read(read_chunk_size)
                        if not chunk:
                            break
                        out_fh.write(chunk)
                        h.update(chunk)
                        clen = len(chunk)
                        attempt_bytes += clen
                        _add_progress_bytes(clen, rel_path)
            return attempt_bytes, h.hexdigest().lower()
        except BaseException:
            if attempt_bytes > 0:
                with state_lock:
                    done_bytes = max(0, done_bytes - attempt_bytes)
            raise

    def _download_ranged_parallel(
        url: str,
        part_path: Path,
        rel_path: str,
        expected_size: int,
    ) -> tuple[int, str]:
        """Download a large file via parallel HTTP Range streams with zero-waste 200 OK fallback."""
        assert cdn_session is not None
        part_count = min(eff_range_streams, max(2, expected_size // max(1, range_threshold_bytes // 2)))
        part_size = (expected_size + part_count - 1) // part_count
        ranges: list[tuple[int, int]] = []
        pos = 0
        while pos < expected_size:
            end = min(expected_size - 1, pos + part_size - 1)
            ranges.append((pos, end))
            pos = end + 1

        if len(ranges) < 2:
            return _download_single_stream(url, part_path, rel_path)

        total_written = 0
        written_lock = threading.Lock()
        first_start, first_end = ranges[0]

        try:
            # Probe & fetch slice 0 in a single request (avoids an extra HEAD round-trip)
            with cdn_session.get(
                url,
                headers={"Range": f"bytes={first_start}-{first_end}"},
                stream=True,
                timeout=(10.0, 30.0),
            ) as resp0:
                resp0.raise_for_status()
                if resp0.status_code != 206:
                    # Server ignored Range header and sent full 200 OK body: consume directly
                    h_full = hashlib.md5()
                    with open(part_path, "wb") as out_fh:
                        for chunk in resp0.iter_content(chunk_size=read_chunk_size):
                            if _is_cancelled():
                                raise InterruptedError("Download cancelled")
                            if not chunk:
                                continue
                            out_fh.write(chunk)
                            h_full.update(chunk)
                            clen = len(chunk)
                            total_written += clen
                            _add_progress_bytes(clen, rel_path)
                    return total_written, h_full.hexdigest().lower()

                # Server supports 206 Partial Content: pre-allocate file and write slice 0
                with open(part_path, "wb") as init_fh:
                    init_fh.truncate(expected_size)
                    init_fh.seek(first_start)
                    slice0_bytes = 0
                    for chunk in resp0.iter_content(chunk_size=read_chunk_size):
                        if _is_cancelled():
                            raise InterruptedError("Download cancelled")
                        if not chunk:
                            continue
                        init_fh.write(chunk)
                        clen = len(chunk)
                        slice0_bytes += clen
                        with written_lock:
                            total_written += clen
                        _add_progress_bytes(clen, rel_path)
                    expected_slice0 = first_end - first_start + 1
                    if slice0_bytes != expected_slice0:
                        raise ValueError(
                            f"Range slice 0 length mismatch for {rel_path}: got {slice0_bytes}, expected {expected_slice0}"
                        )

            def _fetch_slice(bounds: tuple[int, int]) -> None:
                nonlocal total_written
                r_start, r_end = bounds
                expected_len = r_end - r_start + 1
                if _is_cancelled():
                    raise InterruptedError("Download cancelled")
                with cdn_session.get(
                    url,
                    headers={"Range": f"bytes={r_start}-{r_end}"},
                    stream=True,
                    timeout=(10.0, 30.0),
                ) as resp:
                    resp.raise_for_status()
                    if resp.status_code != 206:
                        raise ValueError(f"Expected 206 Partial Content for {rel_path}, got {resp.status_code}")
                    got_len = 0
                    with open(part_path, "r+b") as fh:
                        fh.seek(r_start)
                        for chunk in resp.iter_content(chunk_size=read_chunk_size):
                            if _is_cancelled():
                                raise InterruptedError("Download cancelled")
                            if not chunk:
                                continue
                            fh.write(chunk)
                            clen = len(chunk)
                            got_len += clen
                            with written_lock:
                                total_written += clen
                            _add_progress_bytes(clen, rel_path)
                    if got_len != expected_len:
                        raise ValueError(
                            f"Range slice {r_start}-{r_end} mismatch for {rel_path}: got {got_len}, expected {expected_len}"
                        )

            sub_workers = min(len(ranges) - 1, eff_range_streams)
            with concurrent.futures.ThreadPoolExecutor(max_workers=sub_workers) as rpool:
                rfuts = [rpool.submit(_fetch_slice, b) for b in ranges[1:]]
                for rf in concurrent.futures.as_completed(rfuts):
                    rf.result()

            actual_md5 = _file_md5(part_path)
            return total_written, actual_md5
        except BaseException:
            if total_written > 0:
                with state_lock:
                    done_bytes = max(0, done_bytes - total_written)
            raise

    def _download_one(item: tuple[str, str, int, Path]) -> tuple[str, str, int, str]:
        rel_path, expected_md5, expected_size, dst = item
        if _is_cancelled():
            return ("cancelled", rel_path, 0, "")

        dst.parent.mkdir(parents=True, exist_ok=True)
        url = build_cdn_file_url(cdn_base, remote_version, rel_path)
        last_err = ""

        for attempt in range(1, 4):
            if _is_cancelled():
                return ("cancelled", rel_path, 0, "")

            part_path = dst.with_name(f"{dst.name}.{os.getpid()}.{threading.get_ident()}.part")
            try:
                use_ranged = (
                    attempt == 1
                    and cdn_session is not None
                    and eff_workers > 1
                    and range_threshold_bytes > 0
                    and expected_size >= range_threshold_bytes
                )
                if use_ranged:
                    attempt_bytes, actual_md5 = _download_ranged_parallel(url, part_path, rel_path, expected_size)
                else:
                    attempt_bytes, actual_md5 = _download_single_stream(url, part_path, rel_path)

                if attempt_bytes != expected_size:
                    with state_lock:
                        done_bytes = max(0, done_bytes - attempt_bytes)
                    raise ValueError(
                        f"Size mismatch for {rel_path}: got {attempt_bytes}, expected {expected_size}"
                    )
                if actual_md5 != expected_md5:
                    with state_lock:
                        done_bytes = max(0, done_bytes - attempt_bytes)
                    raise ValueError(
                        f"MD5 mismatch for {rel_path}: got {actual_md5}, expected {expected_md5}"
                    )

                os.replace(part_path, dst)
                return ("ok", rel_path, attempt_bytes, "")
            except InterruptedError:
                part_path.unlink(missing_ok=True)
                return ("cancelled", rel_path, 0, "")
            except Exception as exc:
                part_path.unlink(missing_ok=True)
                last_err = str(exc)
                if attempt < 3:
                    if _wait_cancel_aware(cancel_event, 0.2 * attempt):
                        return ("cancelled", rel_path, 0, "")

        return ("failed", rel_path, 0, last_err)

    dl_start_ts = time.monotonic()
    try:
        if to_download:
            worker_count = max(1, min(eff_workers, total_dl_files))
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as pool:
                futures = [pool.submit(_download_one, item) for item in to_download]
                for fut in concurrent.futures.as_completed(futures):
                    if fut.cancelled():
                        cancelled = True
                        continue
                    try:
                        status, rel_path, byte_count, err_msg = fut.result()
                    except concurrent.futures.CancelledError:
                        cancelled = True
                        continue
                    with state_lock:
                        if status == "ok":
                            downloaded_files += 1
                            downloaded_bytes += byte_count
                            done_files += 1
                        elif status == "cancelled":
                            cancelled = True
                        else:
                            failed_files.append({"file": rel_path, "error": err_msg})
                            done_files += 1
                        cur_done_files = done_files
                        cur_done_bytes = done_bytes

                    _emit_progress(
                        progress_cb,
                        stage="downloading",
                        done_files=cur_done_files,
                        total_files=total_dl_files,
                        done_bytes=cur_done_bytes,
                        total_bytes=total_dl_bytes,
                        current_file=rel_path,
                        start_ts=dl_start_ts,
                    )

                    if _is_cancelled():
                        cancelled = True
                        for pending in futures:
                            pending.cancel()
    finally:
        if cdn_session is not None:
            try:
                cdn_session.close()
            except Exception:
                pass

    if _is_cancelled():
        cancelled = True

    ok = (not cancelled) and (len(failed_files) == 0)

    if ok:
        if read_engine_version(engine_game_dir) != remote_version:
            ver_file = engine_game_dir / "config" / "Game_version.txt"
            _atomic_write_text(ver_file, remote_version, encoding="utf-8")

        _write_engine_metadata(
            root,
            version=remote_version,
            source=cdn_base,
            file_count=len(manifest),
            total_bytes=total_manifest_bytes,
            source_type="cdn",
        )

    final_stage = "cancelled" if cancelled else ("done" if ok else "error")
    _emit_progress(
        progress_cb,
        stage=final_stage,
        done_files=done_files,
        total_files=total_dl_files,
        done_bytes=done_bytes,
        total_bytes=total_dl_bytes,
        current_file="",
        start_ts=dl_start_ts,
    )

    if cancelled:
        msg = f"Download cancelled for v{remote_version} ({downloaded_files}/{total_dl_files} files completed)"
    elif failed_files:
        msg = f"Downloaded v{remote_version} with {len(failed_files)} failed file(s)"
    elif downloaded_files == 0:
        msg = f"Engine v{remote_version} is already up to date ({skipped_files} files verified)"
    else:
        dl_mb = downloaded_bytes / (1024.0 * 1024.0)
        msg = (
            f"Updated engine to v{remote_version} "
            f"({downloaded_files} downloaded, {skipped_files} skipped, {dl_mb:.1f} MB)"
        )

    return {
        "ok": ok,
        "engine_game_dir": str(engine_game_dir),
        "version": remote_version,
        "downloaded_files": downloaded_files,
        "skipped_files": skipped_files,
        "downloaded_bytes": downloaded_bytes,
        "failed_files": failed_files,
        "cancelled": cancelled,
        "message": msg,
    }


def _link_or_copy_file(src: Path, dst: Path, force_resync: bool = False) -> str:
    """Share read-only file via NTFS hardlink when possible, else copy. Returns 'hardlink' or 'copy'."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not force_resync and dst.is_file():
        try:
            if os.path.samefile(src, dst):
                return "hardlink"
        except OSError:
            pass

    if dst.exists() or os.path.islink(dst):
        try:
            dst.unlink()
        except PermissionError:
            os.chmod(dst, stat.S_IWRITE)
            dst.unlink()

    try:
        os.link(src, dst)
        return "hardlink"
    except OSError:
        _atomic_copy_file(src, dst)
        return "copy"


def _ensure_dir_junction_or_copy(src_dir: Path, dst_dir: Path, force_resync: bool = False) -> str:
    """Share a read-only directory via NTFS directory junction, with copy fallback.

    Returns 'junction' or 'copy'.
    """
    src_resolved = src_dir.resolve()

    if dst_dir.exists() or _is_reparse_or_junction(dst_dir):
        if _is_reparse_or_junction(dst_dir):
            try:
                if not force_resync and dst_dir.resolve() == src_resolved:
                    return "junction"
            except OSError:
                pass
            os.rmdir(dst_dir)
        else:
            _remove_dir_or_junction(dst_dir)

    dst_dir.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/j", str(dst_dir), str(src_resolved)],
            capture_output=True,
            text=True,
            **_hidden_subproc_kwargs(),
        )
        if res.returncode == 0 and dst_dir.exists():
            return "junction"

    shutil.copytree(src_resolved, dst_dir, dirs_exist_ok=True)
    return "copy"


def _read_slot_metadata(slot_parent: Path) -> dict[str, Any]:
    meta_path = slot_parent / SLOT_METADATA_FILE
    if not meta_path.is_file():
        return {}
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_slot_metadata(slot_parent: Path, payload: dict[str, Any]) -> None:
    _atomic_write_text(
        slot_parent / SLOT_METADATA_FILE,
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def ensure_account_slot(
    unity_profile: str,
    exe_name: str,
    engine_root: Path | None = None,
    source_game_dir: str | Path | None = None,
    force_resync: bool = False,
) -> dict[str, Any]:
    """Provision or synchronize a lightweight isolated account slot from the master engine."""
    if (
        not isinstance(unity_profile, str)
        or len(unity_profile) != 5
        or not unity_profile.isascii()
        or not unity_profile.isalnum()
    ):
        raise ValueError(
            f"unity_profile must be exactly 5 ASCII alphanumeric characters (got {unity_profile!r})"
        )

    if not isinstance(exe_name, str) or not exe_name.strip():
        raise ValueError("exe_name must be a non-empty .exe filename")
    clean_exe = exe_name.strip()
    if any(sep in clean_exe for sep in ("/", "\\", ":", "..")) or Path(clean_exe).suffix.lower() != ".exe":
        raise ValueError(f"exe_name must be a safe .exe filename (got {exe_name!r})")
    exe_stem = Path(clean_exe).stem
    if not exe_stem or exe_stem.startswith("."):
        raise ValueError(f"exe_name must have a non-empty stem (got {exe_name!r})")

    root = Path(engine_root) if engine_root is not None else resolve_engine_root()
    master_dir: Path | None = None
    if source_game_dir is not None:
        cand = Path(source_game_dir)
        if is_valid_game_dir(cand):
            master_dir = cand
    if master_dir is None:
        master_dir = resolve_engine_game_dir(root)

    if not is_valid_game_dir(master_dir):
        return {
            "ok": False,
            "unity_profile": unity_profile,
            "game_dir": "",
            "exe_path": "",
            "exe_name": clean_exe,
            "version": "",
            "shared_mode": "copy",
            "message": f"Master game directory is missing or invalid: {master_dir}",
        }

    master_dir = master_dir.resolve()
    master_ver = read_engine_version(master_dir)
    accounts_root = resolve_accounts_root(root)
    slot_root = accounts_root / unity_profile
    slot_game_dir = slot_root / "Game"
    slot_game_dir.mkdir(parents=True, exist_ok=True)

    used_shared = False
    used_copy_fallback = False

    # 1. Copy Survival.exe -> <exe_name> (and keep Survival.exe linked/copied)
    master_surv = master_dir / "Survival.exe"
    slot_exe = slot_game_dir / clean_exe
    if force_resync or not _same_file_contents(master_surv, slot_exe):
        _atomic_copy_file(master_surv, slot_exe)

    if clean_exe.lower() != "survival.exe":
        mode = _link_or_copy_file(master_surv, slot_game_dir / "Survival.exe", force_resync=force_resync)
        if mode == "hardlink":
            used_shared = True
        else:
            used_copy_fallback = True

    # 2. Share heavy read-only top-level files (GameAssembly.dll, UnityPlayer.dll, baselib.dll, UnityCrashHandler64.exe, etc.)
    for entry in sorted(master_dir.iterdir(), key=lambda p: p.name.lower()):
        name_low = entry.name.lower()
        if entry.is_file():
            if name_low == "survival.exe":
                continue
            if name_low.endswith(".exe") and name_low not in ALLOWED_MASTER_EXES:
                continue
            mode = _link_or_copy_file(entry, slot_game_dir / entry.name, force_resync=force_resync)
            if mode == "hardlink":
                used_shared = True
            else:
                used_copy_fallback = True
        elif entry.is_dir():
            if name_low == "survival_data" or name_low == "_heinz_backup" or name_low.endswith("_data"):
                continue
            mode = _ensure_dir_junction_or_copy(entry, slot_game_dir / entry.name, force_resync=force_resync)
            if mode == "junction":
                used_shared = True
            else:
                used_copy_fallback = True

    # 3. Provision Survival_Data as a real directory with shared read-only subdirs/files + private identity files
    master_sd = master_dir / "Survival_Data"
    slot_sd = slot_game_dir / "Survival_Data"
    if _is_reparse_or_junction(slot_sd):
        os.rmdir(slot_sd)
    slot_sd.mkdir(parents=True, exist_ok=True)

    for entry in sorted(master_sd.iterdir(), key=lambda p: p.name.lower()):
        name_low = entry.name.lower()
        if entry.is_dir():
            if name_low == "_heinz_backup":
                continue
            mode = _ensure_dir_junction_or_copy(entry, slot_sd / entry.name, force_resync=force_resync)
            if mode == "junction":
                used_shared = True
            else:
                used_copy_fallback = True
        elif entry.is_file():
            if name_low in PRIVATE_SURVIVAL_DATA_FILES:
                continue
            mode = _link_or_copy_file(entry, slot_sd / entry.name, force_resync=force_resync)
            if mode == "hardlink":
                used_shared = True
            else:
                used_copy_fallback = True

    # 4. Always maintain PRIVATE real copies of Survival_Data/app.info and Survival_Data/globalgamemanagers
    master_app_info = master_sd / "app.info"
    master_ggm = master_sd / "globalgamemanagers"
    slot_app_info = slot_sd / "app.info"
    slot_ggm = slot_sd / "globalgamemanagers"

    master_ggm_md5 = _file_md5(master_ggm)
    prev_meta = _read_slot_metadata(slot_root)

    need_refresh_ggm = (
        force_resync
        or not slot_ggm.is_file()
        or prev_meta.get("master_ggm_md5") != master_ggm_md5
        or prev_meta.get("unity_profile") != unity_profile
    )
    if not need_refresh_ggm:
        try:
            if os.path.samefile(master_ggm, slot_ggm) or slot_ggm.stat().st_nlink > 1:
                need_refresh_ggm = True
        except OSError:
            need_refresh_ggm = True
    if not need_refresh_ggm:
        try:
            raw_slot_ggm = slot_ggm.read_bytes()
            if (_READYGO_EXACT_PREFIX + unity_profile.encode("ascii")) not in raw_slot_ggm and unity_profile.encode("ascii") not in raw_slot_ggm:
                need_refresh_ggm = True
        except OSError:
            need_refresh_ggm = True

    if need_refresh_ggm:
        _atomic_copy_file(master_ggm, slot_ggm)

    need_refresh_app = force_resync or not slot_app_info.is_file()
    if not need_refresh_app and master_app_info.is_file():
        try:
            if os.path.samefile(master_app_info, slot_app_info) or slot_app_info.stat().st_nlink > 1:
                need_refresh_app = True
        except OSError:
            need_refresh_app = True
    if need_refresh_app and master_app_info.is_file():
        _atomic_copy_file(master_app_info, slot_app_info)

    patch_unity_identity(slot_game_dir, unity_profile)

    # 5. Create <ExeStem>_Data NTFS directory junction -> slot's own Survival_Data
    if exe_stem.lower() != "survival":
        custom_data = slot_game_dir / f"{exe_stem}_Data"
        mode = _ensure_dir_junction_or_copy(slot_sd, custom_data, force_resync=force_resync)
        if mode == "junction":
            used_shared = True
        else:
            used_copy_fallback = True

    shared_mode = "junction_hardlink" if (used_shared and not used_copy_fallback) else (
        "junction_hardlink" if used_shared else "copy"
    )

    _write_slot_metadata(
        slot_root,
        {
            "unity_profile": unity_profile,
            "exe_name": clean_exe,
            "master_dir": str(master_dir),
            "master_version": master_ver,
            "master_ggm_md5": master_ggm_md5,
            "shared_mode": shared_mode,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )

    return {
        "ok": True,
        "unity_profile": unity_profile,
        "game_dir": str(slot_game_dir),
        "exe_path": str(slot_exe),
        "exe_name": clean_exe,
        "version": master_ver,
        "shared_mode": shared_mode,
        "message": (
            f"Provisioned isolated slot {unity_profile} ({clean_exe}, "
            f"v{master_ver or 'unknown'}, {shared_mode})"
        ),
    }


def _cli_main(argv: list[str]) -> int:
    cmd = argv[1].lower() if len(argv) > 1 else "status"
    if cmd == "status":
        check_remote = "--remote" in argv[2:]
        print(json.dumps(get_engine_status(check_remote=check_remote), indent=2))
        return 0
    if cmd == "import" and len(argv) >= 3:
        res = import_local_engine(argv[2])
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1
    if cmd == "download":
        res = download_or_update_engine()
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1
    if cmd == "slot" and len(argv) >= 4:
        res = ensure_account_slot(argv[2], argv[3])
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1
    print("Usage: game engine manager.py [status [--remote] | import <GameDir> | download | slot <Profile5> <ExeName.exe>]")
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli_main(sys.argv))
