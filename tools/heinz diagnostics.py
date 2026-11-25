"""Heavy pre-flight diagnostic & redacted crash-report utility for HeinZ Command Hub.

Designed so anyone on a clean/test Windows PC can run `HeinZ.exe --diagnose`
(or `Run Diagnostics.bat`) and share the resulting Desktop report with zero
personal details (Windows username, profile path, PC name, emails, UIDs, or tokens).
"""

from __future__ import annotations

import ctypes
import datetime as _dt
import importlib
import importlib.util
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import traceback
from typing import Any

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_UID_JSON_RE = re.compile(
    r'("(?:uid|playerUid|targetUid|alId|allianceId|fightAllianceId|owner_uid)"\s*:\s*")([^"]+)(")',
    re.IGNORECASE,
)
_UID_KV_RE = re.compile(r"\b(uid\s*[:=]\s*)(\d{6,20})\b", re.IGNORECASE)
_LONG_DIGIT_RE = re.compile(r"\b\d{12,20}\b")
_SETOKEN_RE = re.compile(r"(SeToken[^\s:=]*\s*[:=]\s*)(\S+)", re.IGNORECASE)
_USERS_WIN_RE = re.compile(r"([A-Za-z]:\\+Users\\+)([^\\/:*?\"<>|\r\n]+)", re.IGNORECASE)
_USERS_POSIX_RE = re.compile(r"([A-Za-z]:/Users/)([^/:*?\"<>|\r\n]+)", re.IGNORECASE)


def _norm_tokens() -> list[tuple[str, str]]:
    """Return ordered (sensitive_literal, replacement) pairs, longest first."""
    pairs: list[tuple[str, str]] = []
    env_map = [
        ("LOCALAPPDATA", "<LOCALAPPDATA>"),
        ("APPDATA", "<APPDATA>"),
        ("OneDriveCommercial", "<ONEDRIVE>"),
        ("OneDriveConsumer", "<ONEDRIVE>"),
        ("OneDrive", "<ONEDRIVE>"),
        ("USERPROFILE", "<USERPROFILE>"),
        ("HOME", "<USERPROFILE>"),
    ]
    for key, repl in env_map:
        val = (os.environ.get(key) or "").strip()
        if val and len(val) >= 4:
            pairs.append((val, repl))
            pairs.append((val.replace("\\", "\\\\"), repl))
            pairs.append((val.replace("\\", "/"), repl))

    win32_user = ""
    try:
        ubuf = ctypes.create_unicode_buffer(257)
        ulen = ctypes.c_uint32(257)
        if ctypes.windll.advapi32.GetUserNameW(ubuf, ctypes.byref(ulen)):
            win32_user = ubuf.value
    except Exception:
        pass
    names: set[str] = set()
    for cand in (
        os.environ.get("USERNAME", ""),
        win32_user,
    ):
        c = (cand or "").strip()
        if len(c) >= 3:
            names.add(c)
    # Also capture leaf of USERPROFILE in case USERNAME differs
    up = (os.environ.get("USERPROFILE") or "").strip().rstrip("\\/")
    if up:
        leaf = os.path.basename(up)
        if len(leaf) >= 3:
            names.add(leaf)
    for n in sorted(names, key=len, reverse=True):
        pairs.append((n, "<USER>"))

    hosts: set[str] = set()
    for cand in (
        os.environ.get("COMPUTERNAME", ""),
        os.environ.get("USERDOMAIN", ""),
        socket.gethostname(),
    ):
        c = (cand or "").strip()
        if len(c) >= 3 and c.lower() not in {"workgroup", "nt authority", "localhost"}:
            hosts.add(c)
    for h in sorted(hosts, key=len, reverse=True):
        pairs.append((h, "<PC>"))

    # Longest literal first, deduplicated
    seen: set[str] = set()
    ordered: list[tuple[str, str]] = []
    for lit, repl in sorted(pairs, key=lambda item: len(item[0]), reverse=True):
        low = lit.lower()
        if low in seen:
            continue
        seen.add(low)
        ordered.append((lit, repl))
    return ordered


def redact_text(text: str) -> str:
    """Scrub usernames, hostnames, home paths, emails, UIDs, and tokens from diagnostic output."""
    if not text:
        return ""
    out = str(text)
    out = _USERS_WIN_RE.sub(lambda m: f"{m.group(1)}<USER>", out)
    out = _USERS_POSIX_RE.sub(lambda m: f"{m.group(1)}<USER>", out)
    for lit, repl in _norm_tokens():
        out = re.compile(re.escape(lit), re.IGNORECASE).sub(repl, out)
    out = _EMAIL_RE.sub("<EMAIL_REDACTED>", out)
    out = _SETOKEN_RE.sub(r"\1<TOKEN_REDACTED>", out)
    out = _UID_JSON_RE.sub(r"\1<UID_REDACTED>\3", out)
    out = _UID_KV_RE.sub(r"\1<UID_REDACTED>", out)
    out = _LONG_DIGIT_RE.sub("<ID_REDACTED>", out)
    return out


def resolve_desktop_dir() -> str:
    """Find the active Windows Desktop folder (handles OneDrive folder redirection)."""
    try:
        buf = ctypes.create_unicode_buffer(32768)
        # CSIDL_DESKTOPDIRECTORY = 0x0010
        hr = ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf)
        if hr == 0 and buf.value and os.path.isdir(buf.value):
            return buf.value
    except Exception:
        pass
    home = os.path.expanduser("~")
    for cand in (
        os.path.join(home, "Desktop"),
        os.path.join(home, "OneDrive", "Desktop"),
    ):
        if os.path.isdir(cand):
            return cand
    return tempfile.gettempdir()


def _dir_writable(path: str) -> tuple[bool, str]:
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, f".heinz_diag_write_{os.getpid()}")
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("ok")
        os.remove(probe)
        return True, "writable"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _scan_zone_identifiers(roots: list[str]) -> tuple[int, list[str]]:
    """Return (blocked_count, sample_relative_paths) for .exe/.dll/.pyd files with :Zone.Identifier."""
    try:
        k32 = ctypes.windll.kernel32
        gfa = k32.GetFileAttributesW
        gfa.argtypes = [ctypes.c_wchar_p]
        gfa.restype = ctypes.c_uint32
        INVALID = 0xFFFFFFFF
    except Exception:
        return -1, ["kernel32.GetFileAttributesW unavailable"]

    blocked: list[str] = []
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for dp, _, fs in os.walk(root):
            for fn in fs:
                low = fn.lower()
                if not low.endswith((".exe", ".dll", ".pyd")):
                    continue
                full = os.path.join(dp, fn)
                if gfa(full + ":Zone.Identifier") != INVALID:
                    blocked.append(os.path.relpath(full, root))
    return len(blocked), blocked[:15]


def _netfx_info() -> tuple[bool, str]:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full") as k:
            rel, _ = winreg.QueryValueEx(k, "Release")
            rel_int = int(rel)
            try:
                ver, _ = winreg.QueryValueEx(k, "Version")
            except OSError:
                ver = "?"
        ok = rel_int >= 461808
        return ok, f"Release={rel_int}, Version={ver} (requires >= 461808 / 4.7.2)"
    except Exception as exc:
        return False, f"Registry lookup failed: {type(exc).__name__}: {exc}"


def _webview2_info() -> tuple[bool, str]:
    try:
        import winreg
    except Exception as exc:
        return False, f"winreg unavailable: {exc}"
    client_guid = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
    candidates = [
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{client_guid}"),
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{client_guid}"),
        (winreg.HKEY_CURRENT_USER, rf"Software\Microsoft\EdgeUpdate\Clients\{client_guid}"),
    ]
    for hive, sub in candidates:
        try:
            with winreg.OpenKey(hive, sub) as k:
                pv, _ = winreg.QueryValueEx(k, "pv")
                if pv and str(pv).strip() and str(pv).strip() != "0.0.0.0":
                    return True, f"pv={pv}"
        except OSError:
            continue
    return False, "Edge WebView2 Runtime registry key not found"


def _repo_or_bundle_root() -> str:
    if getattr(sys, "frozen", False):
        meipass = str(getattr(sys, "_MEIPASS", "") or "")
        if meipass and os.path.isdir(os.path.join(meipass, "tools")):
            return meipass
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        for cand in (os.path.join(exe_dir, "_internal"), exe_dir):
            if os.path.isdir(os.path.join(cand, "tools")):
                return cand
        return exe_dir
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _resolve_data_dir() -> str:
    ov = os.environ.get("HEINZ_DATA_DIR", "").strip()
    if ov:
        return os.path.abspath(ov)
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        portable = os.path.join(exe_dir, "data")
        if os.path.isdir(portable):
            return portable
        local_root = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return os.path.join(local_root, "HeinZ", "data")
    return os.path.join(_repo_or_bundle_root(), "data")


def _load_mod(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_heavy_diagnostics(
    write_desktop: bool = True,
    quiet: bool = False,
    unblocked_at_startup: int | None = None,
) -> tuple[bool, str, str]:
    """Run all non-destructive clean-PC diagnostic probes and save a redacted Desktop report."""
    started = _dt.datetime.now()
    bundle_root = _repo_or_bundle_root()
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    meipass = str(getattr(sys, "_MEIPASS", exe_dir))
    data_dir = _resolve_data_dir()
    tools_dir = os.path.join(bundle_root, "tools")
    for p in (tools_dir, os.path.join(bundle_root, "api"), os.path.join(bundle_root, "daemon")):
        if os.path.isdir(p) and p not in sys.path:
            sys.path.append(p)

    results: list[tuple[str, str, str]] = []  # (status, name, detail)

    def record(status: str, name: str, detail: str) -> None:
        results.append((status, name, detail))

    # 1. OS & Environment
    try:
        import platform

        is_64 = sys.maxsize > 2**32
        admin = _is_admin()
        pf_prefixes = [
            p.lower()
            for p in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"))
            if p
        ]
        in_pf = any(exe_dir.lower().startswith(p) for p in pf_prefixes)
        data_ok, data_msg = _dir_writable(data_dir)
        sys32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")
        ps_fallback = os.path.join(sys32, "WindowsPowerShell", "v1.0", "powershell.exe")
        ps_path = (
            shutil.which("powershell.exe")
            or shutil.which("pwsh.exe")
            or (ps_fallback if os.path.exists(ps_fallback) else "")
        )
        st_fallback = os.path.join(sys32, "schtasks.exe")
        schtasks_path = shutil.which("schtasks.exe") or (st_fallback if os.path.exists(st_fallback) else "")
        detail = (
            f"OS={platform.platform()} | Arch={'x64' if is_64 else 'x86'} | "
            f"Python={sys.version.split()[0]} | Frozen={getattr(sys, 'frozen', False)} | "
            f"Admin={admin} | ExeInProgramFiles={in_pf}\n"
            f"  ExePath={sys.executable}\n"
            f"  BundleRoot={bundle_root}\n"
            f"  DataDir={data_dir} ({data_msg})\n"
            f"  PowerShell={'OK' if ps_path else 'MISSING'} | schtasks={'OK' if schtasks_path else 'MISSING'}"
        )
        record("PASS" if (is_64 and data_ok and ps_path) else "WARN", "OS & Environment", detail)
    except Exception as exc:
        record("FAIL", "OS & Environment", traceback.format_exc() or str(exc))

    # 2. Mark-of-the-Web (:Zone.Identifier)
    try:
        roots = [meipass] if meipass == exe_dir else [meipass, exe_dir]
        cnt, samples = _scan_zone_identifiers(roots)
        startup_note = (
            f"unblocked_at_startup={unblocked_at_startup}"
            if unblocked_at_startup is not None
            else "unblocked_at_startup=n/a"
        )
        if cnt == 0:
            record("PASS", "Mark-of-the-Web (Zone.Identifier)", f"remaining_blocked=0 ({startup_note})")
        elif cnt > 0:
            record(
                "FAIL",
                "Mark-of-the-Web (Zone.Identifier)",
                f"remaining_blocked={cnt} ({startup_note}) samples={samples}",
            )
        else:
            record("WARN", "Mark-of-the-Web (Zone.Identifier)", f"check skipped: {samples}")
    except Exception:
        record("FAIL", "Mark-of-the-Web (Zone.Identifier)", traceback.format_exc())

    # 3. .NET Framework 4.7.2+
    try:
        ok, msg = _netfx_info()
        record("PASS" if ok else "FAIL", ".NET Framework 4.7.2+", msg)
    except Exception:
        record("FAIL", ".NET Framework 4.7.2+", traceback.format_exc())

    # 4. Edge WebView2 Runtime
    try:
        ok, msg = _webview2_info()
        record("PASS" if ok else "FAIL", "Microsoft Edge WebView2 Runtime", msg)
    except Exception:
        record("FAIL", "Microsoft Edge WebView2 Runtime", traceback.format_exc())

    # 5. Native DLLs (VC++ Runtime, Python.Runtime, ClrLoader, WebView2Loader, _frida)
    try:
        dll_checks: list[str] = []
        dll_failed: list[str] = []
        for sys_dll in ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"):
            try:
                ctypes.WinDLL(sys_dll)
                dll_checks.append(f"{sys_dll}=OK")
            except OSError as exc:
                dll_checks.append(f"{sys_dll}=FAIL({exc})")
                dll_failed.append(sys_dll)
        rel_bins = [
            os.path.join("pythonnet", "runtime", "Python.Runtime.dll"),
            os.path.join("clr_loader", "ffi", "dlls", "amd64", "ClrLoader.dll"),
            os.path.join("webview", "lib", "Microsoft.Web.WebView2.Core.dll"),
            os.path.join("webview", "lib", "Microsoft.Web.WebView2.WinForms.dll"),
            os.path.join("webview", "lib", "runtimes", "win-x64", "native", "WebView2Loader.dll"),
            os.path.join("frida", "_frida.pyd"),
        ]
        for rel in rel_bins:
            full = os.path.join(bundle_root, rel)
            if not os.path.exists(full):
                # Non-frozen check fallback via importlib location
                mod_name = rel.split(os.sep)[0]
                spec = importlib.util.find_spec(mod_name)
                if spec and spec.submodule_search_locations:
                    cand = os.path.join(spec.submodule_search_locations[0], *rel.split(os.sep)[1:])
                    full = cand
            exists = os.path.exists(full)
            dll_checks.append(f"{os.path.basename(rel)}={'OK' if exists else 'MISSING'}")
            if not exists and getattr(sys, "frozen", False):
                dll_failed.append(rel)
        record(
            "FAIL" if dll_failed else "PASS",
            "VC++ & Bundled Native Binaries",
            " | ".join(dll_checks),
        )
    except Exception:
        record("FAIL", "VC++ & Bundled Native Binaries", traceback.format_exc())

    # 6. Core Python Dependencies & Frida Smoke Test
    try:
        mod_notes: list[str] = []
        mod_errs: list[str] = []
        for name in ("psutil", "requests", "openpyxl", "frida", "bottle", "proxy_tools", "winreg"):
            try:
                m = importlib.import_module(name)
                ver = getattr(m, "__version__", "builtin")
                mod_notes.append(f"{name}={ver}")
            except Exception as exc:
                mod_errs.append(f"{name}: {type(exc).__name__}: {exc}")

        # Test frida process enumeration via local device
        try:
            import frida as _frida

            procs = _frida.get_local_device().enumerate_processes()
            mod_notes.append(f"frida.enumerate_processes={len(procs)}")
        except Exception as exc:
            mod_errs.append(f"frida.enumerate_processes: {type(exc).__name__}: {exc}")

        record(
            "FAIL" if mod_errs else "PASS",
            "Core Bundled Python Deps & Frida",
            f"loaded=[{', '.join(mod_notes)}]" + (f"\n  errors={mod_errs}" if mod_errs else ""),
        )
    except Exception:
        record("FAIL", "Core Bundled Python Deps & Frida", traceback.format_exc())

    # 7. Python.NET + WinForms + WebView2 Core Initialization
    try:
        import clr  # noqa: F401
        import pythonnet
        import webview.platforms.winforms as wf
        import webview.platforms.edgechromium as ec

        rt_info = repr(pythonnet.get_runtime_info())
        wv2_core_ver = ""
        try:
            wv2_dll = os.path.join(bundle_root, "webview", "lib", "Microsoft.Web.WebView2.Core.dll")
            if not os.path.exists(wv2_dll):
                import webview as _wv
                wv2_dll = os.path.join(os.path.dirname(_wv.__file__), "lib", "Microsoft.Web.WebView2.Core.dll")
            clr.AddReference(wv2_dll)
            from Microsoft.Web.WebView2.Core import CoreWebView2Environment  # type: ignore

            wv2_core_ver = str(CoreWebView2Environment.GetAvailableBrowserVersionString(None) or "")
        except Exception as exc:
            wv2_core_ver = f"ERR:{type(exc).__name__}:{exc}"

        ok = (
            getattr(wf, "BrowserView", None) is not None
            and getattr(ec, "EdgeChrome", None) is not None
            and bool(wv2_core_ver)
            and not wv2_core_ver.startswith("ERR:")
        )
        record(
            "PASS" if ok else "FAIL",
            "Python.NET / WinForms / WebView2 Bindings",
            f"runtime={rt_info} | BrowserView={wf.BrowserView is not None} | "
            f"EdgeChrome={ec.EdgeChrome is not None} | CoreWebView2Version={wv2_core_ver}",
        )
    except Exception:
        record("FAIL", "Python.NET / WinForms / WebView2 Bindings", traceback.format_exc())

    # 8. OpenPyXL Workbook Roundtrip & Non-Admin NTFS Junction (mklink /j)
    try:
        import openpyxl

        with tempfile.TemporaryDirectory(prefix="heinz_diag_") as tmp:
            xlsx_path = os.path.join(tmp, "diag_test.xlsx")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Diag"
            ws.append(["Status", "Value"])
            ws.append(["OK", 123])
            wb.save(xlsx_path)
            wb2 = openpyxl.load_workbook(xlsx_path)
            val = wb2["Diag"]["B2"].value
            if val != 123:
                raise AssertionError(f"Expected 123 from workbook, got {val!r}")

            j_src = os.path.join(tmp, "src dir with space")
            j_dst = os.path.join(tmp, "dst junction with space")
            os.makedirs(j_src, exist_ok=True)
            with open(os.path.join(j_src, "probe.txt"), "w", encoding="utf-8") as fh:
                fh.write("junction_ok")
            proc = subprocess.run(
                f'mklink /j "{j_dst}" "{j_src}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if proc.returncode != 0:
                raise RuntimeError(f"mklink /j failed (rc={proc.returncode}): {proc.stdout} {proc.stderr}")
            with open(os.path.join(j_dst, "probe.txt"), "r", encoding="utf-8") as fh:
                j_read = fh.read().strip()
            subprocess.run(
                f'rmdir "{j_dst}"',
                shell=True,
                capture_output=True,
                timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if j_read != "junction_ok":
                raise AssertionError(f"Junction read mismatch: {j_read!r}")

        record(
            "PASS",
            "OpenPyXL & NTFS Junction (mklink /j)",
            "Workbook write/read=OK | Non-admin space-quoted mklink /j create/read/remove=OK",
        )
    except Exception:
        record("FAIL", "OpenPyXL & NTFS Junction (mklink /j)", traceback.format_exc())

    # 9. UI Assets Integrity Check
    try:
        ui_html = os.path.join(bundle_root, "web", "index.html")
        if not os.path.exists(ui_html):
            ui_html = os.path.join(bundle_root, "launcher", "web", "index.html")
        icon_path = os.path.join(bundle_root, "assets", "heinz.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(bundle_root, "launcher", "assets", "heinz.ico")
        if os.path.exists(ui_html):
            size = os.path.getsize(ui_html)
            record(
                "PASS",
                "UI Assets (web/index.html & icon)",
                f"index.html={size} bytes | icon={'OK' if os.path.exists(icon_path) else 'MISSING'}",
            )
        else:
            record("FAIL", "UI Assets (web/index.html & icon)", f"Missing index.html under {bundle_root}")
    except Exception:
        record("FAIL", "UI Assets (web/index.html & icon)", traceback.format_exc())

    # 10. Last Z Vanilla Install, ReadyGo Registry & Running Processes (Redacted Read-Only)
    try:
        cd_path = os.path.join(tools_dir, "client discovery.py")
        sfc_path = os.path.join(tools_dir, "sync farm clients.py")
        if not os.path.exists(cd_path):
            record("FAIL", "Last Z Discovery & Registry (Redacted)", f"Missing client discovery.py in {tools_dir}")
        else:
            cd = _load_mod("diag_cd", cd_path)
            vanilla = cd.detect_vanilla_base_install()
            lines: list[str] = []
            found_vanilla = bool(isinstance(vanilla, dict) and vanilla.get("found"))
            if found_vanilla:
                gdir = str(vanilla.get("game_dir") or "")
                pf_low = (os.environ.get("ProgramFiles") or "").lower()
                in_pf_game = bool(pf_low and gdir.lower().startswith(pf_low))
                has_exe = os.path.exists(os.path.join(gdir, "Survival.exe"))
                has_ga = os.path.exists(os.path.join(gdir, "GameAssembly.dll"))
                has_launcher = bool(vanilla.get("has_launcher"))
                has_backup = os.path.exists(
                    os.path.join(gdir, "Survival_Data", "_heinz_backup", "globalgamemanagers.orig")
                )
                lines.append(
                    f"VanillaBase={gdir} | Version={vanilla.get('version') or '?'} | "
                    f"UnityProfile={vanilla.get('unity_profile') or '?'} | "
                    f"Survival.exe={has_exe} | GameAssembly={has_ga} | "
                    f"Launcher.exe={has_launcher} | BackupExists={has_backup} | InProgramFiles={in_pf_game}"
                )
            else:
                lines.append("VanillaBase=NOT_FOUND (install vanilla Last Z PC client to use Setup)")

            if os.path.exists(sfc_path):
                try:
                    sfc = _load_mod("diag_sfc", sfc_path)
                    st = sfc.inspect_setup_status() or {}
                    lines.append(
                        f"SetupStatus: base_found={bool(st.get('base_found'))}, "
                        f"main_registered={bool(st.get('main_registered'))}, "
                        f"gpu_pref_ok={bool(st.get('gpu_pref_ok'))}, "
                        f"bot_config_ok={bool(st.get('bot_config_ok'))}, "
                        f"backup_ok={bool(st.get('backup_ok'))}, "
                        f"multi_instance_ready={bool(st.get('multi_instance_ready'))}, "
                        f"clone_count={st.get('clone_count', 0)}"
                    )
                except Exception as exc:
                    lines.append(f"SetupStatus=ERROR({type(exc).__name__}: {exc})")

            try:
                reg_profiles = cd.read_readygo_registry() or {}
                lines.append(f"ReadyGoRegistryProfiles={len(reg_profiles)}")
                for prof_name, meta in sorted(reg_profiles.items()):
                    lines.append(
                        f"  Profile[{prof_name}]: uid_present={bool(meta.get('uid'))}, "
                        f"has_token={bool(meta.get('has_token'))}, known_uids={meta.get('known_uids', 0)}"
                    )
            except Exception as exc:
                lines.append(f"ReadyGoRegistryProfiles=ERROR({type(exc).__name__}: {exc})")

            try:
                discovered = cd.discover_clients(save_cache=False) or []
                lines.append(f"DiscoveredClients={len(discovered)}")
                for c in discovered:
                    exe_p = c.get("exe_path") or c.get("game_dir") or "?"
                    lines.append(
                        f"  Client[{c.get('label') or c.get('id') or '?'}]: "
                        f"profile={c.get('unity_profile') or '?'}, role={c.get('role') or '?'}, "
                        f"has_token={bool(c.get('has_token'))}, path={exe_p}"
                    )
            except Exception as exc:
                lines.append(f"DiscoveredClients=ERROR({type(exc).__name__}: {exc})")

            try:
                running = cd.find_running_processes() or []
                lines.append(f"RunningLastZProcesses={len(running)}")
                for rp in running:
                    xlua_ok = cd._xlua_loaded(int(rp["pid"])) if rp.get("pid") else False
                    lines.append(
                        f"  Proc: exe={rp.get('exe_name') or '?'}, pid={rp.get('pid')}, "
                        f"profile={rp.get('unity_profile') or '?'}, xlua_loaded={xlua_ok}"
                    )
            except Exception as exc:
                lines.append(f"RunningLastZProcesses=ERROR({type(exc).__name__}: {exc})")

            record("PASS" if found_vanilla else "WARN", "Last Z Discovery & Registry (Redacted)", "\n  ".join(lines))
    except Exception:
        record("FAIL", "Last Z Discovery & Registry (Redacted)", traceback.format_exc())

    # 11. Frozen --run-script IPC Subprocess Verification
    try:
        mcb_path = os.path.join(tools_dir, "multi client bot.py")
        if not os.path.exists(mcb_path):
            record("FAIL", "Subprocess --run-script Runner", f"Missing {mcb_path}")
        else:
            cmd = (
                [sys.executable, "--run-script", mcb_path, "--status"]
                if getattr(sys, "frozen", False)
                else [sys.executable, mcb_path, "--status"]
            )
            env = dict(os.environ)
            env["HEINZ_DATA_DIR"] = data_dir
            env["PYTHONIOENCODING"] = "utf-8"
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=20,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            snippet = (proc.stdout or proc.stderr or "").strip().splitlines()[:6]
            if proc.returncode == 0:
                record(
                    "PASS",
                    "Subprocess --run-script Runner",
                    f"rc=0 | sample_lines={snippet}",
                )
            else:
                record(
                    "FAIL",
                    "Subprocess --run-script Runner",
                    f"rc={proc.returncode} | stdout={proc.stdout[:400]!r} | stderr={proc.stderr[:400]!r}",
                )
    except Exception:
        record("FAIL", "Subprocess --run-script Runner", traceback.format_exc())

    # Build report text
    pass_n = sum(1 for s, _, _ in results if s == "PASS")
    warn_n = sum(1 for s, _, _ in results if s == "WARN")
    fail_n = sum(1 for s, _, _ in results if s == "FAIL")

    lines_out = [
        "========================================================================",
        "HeinZ Command Hub - Clean-PC Diagnostic Report (Privacy Redacted)",
        f"Timestamp : {started.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Summary   : PASS={pass_n}  WARN={warn_n}  FAIL={fail_n}",
        "========================================================================",
        "",
        "SUMMARY MATRIX:",
    ]
    for status, name, _ in results:
        lines_out.append(f"  [{status:4s}] {name}")
    lines_out.append("")
    lines_out.append("DETAILED CHECKS:")
    for status, name, detail in results:
        lines_out.append(f"\n--- [{status}] {name} ---")
        lines_out.append(detail)
    lines_out.append("")

    redacted = redact_text("\n".join(lines_out))
    report_path = ""
    if write_desktop:
        desk = resolve_desktop_dir()
        fname = f"HeinZ_Diagnostic_Report_{started.strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(desk, fname)
        try:
            with open(report_path, "w", encoding="utf-8") as fh:
                fh.write(redacted)
        except OSError:
            fallback = os.path.join(tempfile.gettempdir(), fname)
            with open(fallback, "w", encoding="utf-8") as fh:
                fh.write(redacted)
            report_path = fallback

    if not quiet and sys.stdout is not None:
        try:
            sys.stdout.write(redacted + "\n")
            if report_path:
                sys.stdout.write(f"\nSaved redacted report to: {redact_text(report_path)}\n")
            sys.stdout.flush()
        except Exception:
            pass

    return (fail_n == 0), report_path, redacted


def write_desktop_crash_report(
    context: str,
    err: Any,
    extra: dict[str, Any] | None = None,
) -> str:
    """Write a redacted crash report directly onto the Windows Desktop so testers can share it."""
    now = _dt.datetime.now()
    net_ok, net_msg = _netfx_info()
    wv_ok, wv_msg = _webview2_info()
    tb_str = traceback.format_exc()
    if tb_str.strip() == "NoneType: None":
        tb_str = ""
    if isinstance(err, BaseException) and not tb_str:
        tb_str = "".join(traceback.format_exception(type(err), err, err.__traceback__))

    lines = [
        "========================================================================",
        "HeinZ Command Hub - Crash Report (Privacy Redacted)",
        f"Timestamp : {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Context   : {context}",
        f"Frozen    : {getattr(sys, 'frozen', False)}",
        f"ExePath   : {sys.executable}",
        f".NET 4.7+ : {net_ok} ({net_msg})",
        f"WebView2  : {wv_ok} ({wv_msg})",
    ]
    if extra:
        for k, v in extra.items():
            lines.append(f"{k}: {v}")
    lines.extend([
        "",
        f"Error     : {type(err).__name__}: {err}" if isinstance(err, BaseException) else f"Error     : {err}",
        "",
        "Traceback:",
        tb_str or "(no traceback available)",
        "",
        "TIP: Run 'Run Diagnostics.bat' (next to HeinZ.exe) for a full 11-point pre-flight report.",
    ])
    redacted = redact_text("\n".join(lines))
    desk = resolve_desktop_dir()
    fname = f"HeinZ_Crash_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    out_path = os.path.join(desk, fname)
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(redacted)
        return out_path
    except OSError:
        fallback = os.path.join(tempfile.gettempdir(), fname)
        try:
            with open(fallback, "w", encoding="utf-8") as fh:
                fh.write(redacted)
            return fallback
        except OSError:
            return ""


if __name__ == "__main__":
    no_popup = "--no-popup" in sys.argv or "--quiet" in sys.argv
    ok, path, _ = run_heavy_diagnostics(write_desktop=True, quiet=False)
    if not no_popup:
        try:
            status_word = "PASSED" if ok else "FOUND ISSUES (see FAIL lines)"
            ctypes.windll.user32.MessageBoxW(
                None,
                f"HeinZ Diagnostics {status_word}.\n\nRedacted report saved to your Desktop:\n{path}",
                "HeinZ Diagnostics",
                0x40 if ok else 0x30,
            )
        except Exception:
            pass
    sys.exit(0 if ok else 1)
