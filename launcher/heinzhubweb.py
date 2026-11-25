"""HeinZ Helper - Modern Dark-Glass Desktop UI powered by pywebview.

Replaces raw Tkinter widgets with a native Edge WebView2 Chromium shell while
preserving 100% of the Last Z fleet orchestration, map intel, export tools, and
28-module automation runner.
"""

from __future__ import annotations

import base64
import copy
import glob
import importlib.util
import inspect
import json
import math
import os
import re
import runpy
import shutil
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from typing import Any


def _dir_is_writable(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, f".heinz_write_probe_{os.getpid()}")
        with open(probe, "w", encoding="utf-8") as fh:
            fh.write("ok")
        os.remove(probe)
        return True
    except OSError:
        return False


def _resolve_data_dir() -> str:
    """Pick a writable per-user data folder.

    * Explicit override: HEINZ_DATA_DIR environment variable.
    * Source checkout (not frozen): <repo>/data (unchanged developer behaviour).
    * Frozen HeinZ.exe: portable `<exe folder>/data` if it already exists and is writable,
      otherwise %LOCALAPPDATA%/HeinZ/data (always writable, survives HeinZ updates,
      works even when HeinZ is unzipped into a read-only folder like Program Files).
    """
    override = os.environ.get("HEINZ_DATA_DIR", "").strip()
    if override:
        os.makedirs(override, exist_ok=True)
        return os.path.abspath(override)
    if not getattr(sys, "frozen", False):
        return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    portable = os.path.join(exe_dir, "data")
    if os.path.isdir(portable) and _dir_is_writable(portable):
        return portable
    local_root = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    target = os.path.join(local_root, "HeinZ", "data")
    os.makedirs(target, exist_ok=True)
    return target


def _migrate_legacy_data(target: str) -> None:
    """One-time copy of an existing source-checkout data folder (dev PC upgrade path only)."""
    if not getattr(sys, "frozen", False):
        return
    if any(os.path.exists(os.path.join(target, n)) for n in ("bot config.json", "client profiles.json")):
        return
    legacy = os.path.join(os.path.expanduser("~"), "Desktop", "LastZ-PC-Master-Overhaul", "data")
    if not os.path.isdir(legacy) or os.path.abspath(legacy) == os.path.abspath(target):
        return
    try:
        shutil.copytree(legacy, target, dirs_exist_ok=True)
    except Exception:
        pass


HEINZ_DATA_DIR = _resolve_data_dir()
os.environ["HEINZ_DATA_DIR"] = HEINZ_DATA_DIR
_migrate_legacy_data(HEINZ_DATA_DIR)


def _ensure_std_streams() -> None:
    """Windowed (console=False) builds get sys.stdout/stderr = None when launched without
    redirected handles (Task Scheduler, shortcuts, Start-Process). Many tool scripts call
    sys.stdout.reconfigure()/print -> give them a real sink so they never crash."""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        log_dir = os.path.join(HEINZ_DATA_DIR, "logs")
        try:
            os.makedirs(log_dir, exist_ok=True)
            sys.stderr = open(os.path.join(log_dir, "run-script-stderr.log"), "a", encoding="utf-8")
        except OSError:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")


def _maybe_run_bundled_script() -> None:
    """When invoked as `HeinZ.exe --run-script <script.py> [args...]`, execute the script in-process."""
    if "--run-script" not in sys.argv:
        return
    _ensure_std_streams()
    idx = sys.argv.index("--run-script")
    if idx + 1 >= len(sys.argv):
        sys.stderr.write("Usage: --run-script <script_path> [args...]\n")
        raise SystemExit(2)
    raw_arg = sys.argv[idx + 1]
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    bundle_root = str(
        getattr(
            sys,
            "_MEIPASS",
            os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")),
        )
    )
    candidates = [
        os.path.abspath(raw_arg),
        os.path.join(bundle_root, raw_arg),
        os.path.join(exe_dir, "_internal", raw_arg),
        os.path.join(exe_dir, raw_arg),
        os.path.join(bundle_root, "tools", os.path.basename(raw_arg)),
        os.path.join(exe_dir, "_internal", "tools", os.path.basename(raw_arg)),
    ]
    target = next((c for c in candidates if os.path.isfile(c)), None)
    if not target or not os.path.exists(target):
        sys.stderr.write(f"Script not found: {raw_arg}\n")
        raise SystemExit(2)
    for p in (
        os.path.dirname(target),
        os.path.join(bundle_root, "tools"),
        os.path.join(bundle_root, "api"),
        os.path.join(bundle_root, "daemon"),
        bundle_root,
    ):
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
    sys.argv = [target, *sys.argv[idx + 2 :]]
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    try:
        runpy.run_path(target, run_name="__main__")
    except SystemExit:
        raise
    except BaseException:
        tb = traceback.format_exc()
        try:
            sys.stderr.write(tb)
            log_dir = os.path.join(HEINZ_DATA_DIR, "logs")
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, "run-script-errors.log"), "a", encoding="utf-8") as fh:
                fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {target} {sys.argv[1:]}\n{tb}\n")
        except Exception:
            pass
        raise SystemExit(1)
    raise SystemExit(0)


def _unblock_bundle_zone_identifiers() -> int:
    """Strip Windows Mark-of-the-Web (:Zone.Identifier) from extracted bundle files before
    pythonnet / .NET Framework loads Python.Runtime.dll, WebView2 DLLs, or _frida.pyd."""
    if not getattr(sys, "frozen", False):
        return 0
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        DeleteFileW = k32.DeleteFileW
        DeleteFileW.argtypes = [ctypes.c_wchar_p]
        DeleteFileW.restype = ctypes.c_bool
        GetFileAttributesW = k32.GetFileAttributesW
        GetFileAttributesW.argtypes = [ctypes.c_wchar_p]
        GetFileAttributesW.restype = ctypes.c_uint32
        INVALID = 0xFFFFFFFF
    except Exception:
        return 0

    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    meipass = str(getattr(sys, "_MEIPASS", exe_dir))
    sentinels = (
        os.path.join(meipass, "pythonnet", "runtime", "Python.Runtime.dll"),
        os.path.join(meipass, "clr_loader", "ffi", "dlls", "amd64", "ClrLoader.dll"),
        os.path.join(meipass, "webview", "lib", "Microsoft.Web.WebView2.Core.dll"),
        os.path.join(meipass, "webview", "lib", "Microsoft.Web.WebView2.WinForms.dll"),
        os.path.join(meipass, "webview", "lib", "runtimes", "win-x64", "native", "WebView2Loader.dll"),
        os.path.join(meipass, "frida", "_frida.pyd"),
        os.path.abspath(sys.executable),
    )
    needs_sweep = any(
        os.path.exists(p) and GetFileAttributesW(f"{p}:Zone.Identifier") != INVALID
        for p in sentinels
    )
    if not needs_sweep:
        return 0

    removed = 0
    seen_roots = []
    for root in (meipass, exe_dir):
        rp = os.path.abspath(root)
        if os.path.isdir(rp) and rp not in seen_roots:
            seen_roots.append(rp)
    for root in seen_roots:
        for dp, _, fs in os.walk(root):
            for fn in fs:
                ads = os.path.join(dp, fn) + ":Zone.Identifier"
                if GetFileAttributesW(ads) != INVALID:
                    if DeleteFileW(ads):
                        removed += 1
    return removed


def _diagnostics_module():
    roots = []
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            roots.append(str(getattr(sys, "_MEIPASS")))
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        roots.extend([os.path.join(exe_dir, "_internal"), exe_dir])
    else:
        roots.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    for root in roots:
        cand = os.path.join(root, "tools", "heinz diagnostics.py")
        if os.path.exists(cand):
            spec = importlib.util.spec_from_file_location("heinz_diagnostics", cand)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
    return None


def _write_redacted_desktop_crash(context: str, err: Any, extra: dict[str, Any] | None = None) -> str:
    try:
        diag = _diagnostics_module()
        if diag is not None and hasattr(diag, "write_desktop_crash_report"):
            return str(diag.write_desktop_crash_report(context, err, extra=extra) or "")
    except Exception:
        pass
    # Minimal fallback if heinz_diagnostics could not be loaded
    try:
        import ctypes
        import tempfile

        buf = ctypes.create_unicode_buffer(32768)
        desk = ""
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf) == 0 and os.path.isdir(buf.value):
            desk = buf.value
        else:
            desk = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.isdir(desk):
                desk = tempfile.gettempdir()
        user_name = os.environ.get("USERNAME", "")
        user_prof = os.environ.get("USERPROFILE", "")
        pc_name = os.environ.get("COMPUTERNAME", "")
        text = f"HeinZ Crash ({context}) @ {time.strftime('%Y-%m-%d %H:%M:%S')}\n{err}\n{traceback.format_exc()}"
        for lit, repl in ((user_prof, "<USERPROFILE>"), (user_name, "<USER>"), (pc_name, "<PC>")):
            if lit and len(lit) >= 3:
                text = re.compile(re.escape(lit), re.IGNORECASE).sub(repl, text)
        out = os.path.join(desk, f"HeinZ_Crash_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
        return out
    except Exception:
        return ""


def _maybe_run_diagnostics(unblocked_count: int) -> None:
    if "--diagnose" not in sys.argv:
        return
    no_popup = "--no-popup" in sys.argv or "--quiet" in sys.argv
    try:
        diag = _diagnostics_module()
        if diag is None:
            raise RuntimeError("Bundled tools/heinz diagnostics.py not found")
        ok, report_path, _ = diag.run_heavy_diagnostics(
            write_desktop=True,
            quiet=False,
            unblocked_at_startup=unblocked_count,
        )
        if not no_popup:
            try:
                import ctypes
                word = "PASSED" if ok else "FOUND ISSUES (check FAIL entries)"
                ctypes.windll.user32.MessageBoxW(
                    None,
                    f"HeinZ Diagnostics {word}.\n\n"
                    f"Redacted report saved to your Desktop:\n{report_path}\n\n"
                    "Personal paths, usernames, PC name, emails, UIDs, and tokens were automatically stripped.",
                    "HeinZ Diagnostics",
                    0x40 if ok else 0x30,
                )
            except Exception:
                pass
        sys.exit(0 if ok else 1)
    except SystemExit:
        raise
    except Exception as exc:
        crash_file = _write_redacted_desktop_crash("diagnostics_runner", exc)
        if not no_popup:
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    None,
                    f"HeinZ Diagnostics hit an error:\n{type(exc).__name__}: {exc}\n\nCrash report saved to Desktop:\n{crash_file}",
                    "HeinZ Diagnostics Error",
                    0x10,
                )
            except Exception:
                pass
        sys.exit(1)


_UNBLOCKED_AT_STARTUP = 0
if getattr(sys, "frozen", False):
    _ensure_std_streams()
    _UNBLOCKED_AT_STARTUP = _unblock_bundle_zone_identifiers()
_maybe_run_diagnostics(_UNBLOCKED_AT_STARTUP)
_maybe_run_bundled_script()

try:
    import psutil
    import webview
except Exception as _early_exc:
    _crash_file = _write_redacted_desktop_crash("early_import", _early_exc)
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            None,
            f"HeinZ failed during startup imports:\n{type(_early_exc).__name__}: {_early_exc}\n\n"
            f"Redacted crash report saved to Desktop:\n{_crash_file}",
            "HeinZ Startup Error",
            0x10,
        )
    except Exception:
        pass
    sys.exit(1)


def _resource_root() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return str(sys._MEIPASS)  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def _resolve_repo_root() -> str:
    exe_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    if getattr(sys, "frozen", False):
        candidates = [
            os.environ.get("LASTZ_REPO_ROOT", "").strip(),
            _resource_root(),
            exe_dir,
            os.path.abspath(os.path.join(exe_dir, "..")),
            os.getcwd(),
        ]
    else:
        candidates = [
            os.environ.get("LASTZ_REPO_ROOT", "").strip(),
            os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")),
            exe_dir,
            os.getcwd(),
            _resource_root(),
        ]
    for cand in candidates:
        if not cand:
            continue
        tools_cand = os.path.join(cand, "tools")
        if os.path.isdir(tools_cand) and os.path.exists(os.path.join(tools_cand, "client discovery.py")):
            return os.path.abspath(cand)
    return os.path.abspath(_resource_root() if getattr(sys, "frozen", False) else os.path.join(exe_dir, ".."))


def _resolve_python_cli() -> str:
    if not getattr(sys, "frozen", False):
        exe = sys.executable or "python"
        if os.path.basename(exe).lower() == "pythonw.exe":
            console_exe = os.path.join(os.path.dirname(exe), "python.exe")
            if os.path.exists(console_exe):
                return console_exe
        return exe

    # When running frozen, always prefer bundled `--run-script` mode via _build_script_cmd().
    return sys.executable


def _build_script_cmd(script_path: str, extra_args: list[str] | None = None, utf8: bool = True) -> list[str]:
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "--run-script", script_path]
    else:
        cmd = [PYTHON_CLI_EXE]
        if utf8:
            cmd.extend(["-X", "utf8"])
        cmd.append(script_path)
    if extra_args:
        cmd.extend(extra_args)
    return cmd


REPO_ROOT = _resolve_repo_root()
RES_ROOT = _resource_root()
PYTHON_CLI_EXE = _resolve_python_cli()
NO_WINDOW_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
API_DIR = os.path.join(REPO_ROOT, "api")
DAEMON_DIR = os.path.join(REPO_ROOT, "daemon")
DATA_DIR = HEINZ_DATA_DIR
os.makedirs(DATA_DIR, exist_ok=True)
BRACKET_DIR = os.path.join(DATA_DIR, "bracket states")
_ENV_SCRATCH = os.environ.get("HEINZ_SCRATCH_DIR", "").strip()
SCRATCH_DIR = os.path.abspath(_ENV_SCRATCH) if (_ENV_SCRATCH and os.path.isdir(_ENV_SCRATCH)) else DATA_DIR
if not os.path.exists(BRACKET_DIR):
    _alt_bracket = os.path.join(SCRATCH_DIR, "bracket_xlsx_perfect")
    if os.path.isdir(_alt_bracket):
        BRACKET_DIR = _alt_bracket

CRASH_LOG = os.path.join(DATA_DIR, "logs", "crash.log")
try:
    os.makedirs(os.path.dirname(CRASH_LOG), exist_ok=True)
except OSError:
    pass

ROSTER_SHEET_URL = "https://script.google.com/macros/s/AKfycbwMVcm76RExNGoxHzWR4afOhHDIVyz--A4m4cG8IJ6PVrYofuPl5cbdS4ADFvXyoqYDdg/exec"

for _p in (TOOLS_DIR, API_DIR, DAEMON_DIR, SCRATCH_DIR):
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.append(_p)

_USER_WIN_PATH_RE = re.compile(r"([A-Za-z]:\\+Users\\+)([^\\/:*?\"<>|\r\n]+)", re.IGNORECASE)
_USER_POSIX_PATH_RE = re.compile(r"([A-Za-z]:/Users/)([^/:*?\"<>|\r\n]+)", re.IGNORECASE)
_TOKEN_SCRUB_RE = re.compile(r"(SeToken[^\s:=]*\s*[:=]\s*)(\S+)", re.IGNORECASE)
_UID_SCRUB_RE = re.compile(r"\b\d{12,20}\b")


def _redact_text(text: Any) -> str:
    """Scrub local OS usernames, user profile paths, auth tokens, and long UIDs from logs."""
    raw = str(text or "")
    hd = globals().get("heinz_diagnostics")
    if hd is not None and hasattr(hd, "redact_text"):
        try:
            raw = hd.redact_text(raw)
        except Exception:
            pass
    raw = _USER_WIN_PATH_RE.sub(r"\1<USER>", raw)
    raw = _USER_POSIX_PATH_RE.sub(r"\1<USER>", raw)
    raw = _TOKEN_SCRUB_RE.sub(r"\1<REDACTED>", raw)
    raw = _UID_SCRUB_RE.sub("<ID>", raw)
    return raw


_JSON_MEM_LOCK = threading.RLock()
_JSON_MEM_CACHE_MAX = 64
_JSON_MEM_CACHE: dict[str, tuple[tuple[int, int, int, int], Any]] = {}
_CONSOLE_FILE_LOCK = threading.Lock()
_LIVE_CONSOLE_MAX_BYTES = 5 * 1024 * 1024
_HEX_TIP_FILTER_RE = re.compile(r"^#?[0-9A-Fa-f]{6,8}(?:\s*\(#?[0-9A-Fa-f]{6,8}\))?$")


def _stat_sig_from_stat(st: os.stat_result) -> tuple[int, int, int, int]:
    """Build a collision-resistant file signature (mtime_ns, birthtime_ns, size, ino) consistent across stat()/fstat()."""
    mtime_ns = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000)))
    birth_ns = int(getattr(st, "st_birthtime_ns", getattr(st, "st_ctime_ns", int(st.st_ctime * 1_000_000_000))))
    return (mtime_ns, birth_ns, int(st.st_size), int(getattr(st, "st_ino", 0)))


_TIP_ERR_RE = re.compile(
    r"\b(?:error|exception|invalid|failed\s+to|server\s+error)\b|e100\d+",
    re.IGNORECASE,
)
_TIP_WARN_RE = re.compile(
    r"\b(?:cannot|can't|not\s+enough|insufficient|lack(?:ing)?|full|limit(?:ed|s)?|cooldown|locked|"
    r"unable|unavailable|no\s+available|war\s+fever|under\s+attack|defeat(?:ed)?|occupied|"
    r"exceed(?:ed|s)?|already\s+in|blocked|requirement|reach\s+lv|need\s+\w+|too\s+strong|march\s+slot)\b",
    re.IGNORECASE,
)


def _classify_in_game_tip(tip: str) -> tuple[str, str, str]:
    """Classify an in-game toast as (category, level, label) using word-boundary rules so normal toasts stay [DETAIL]."""
    s = str(tip or "").strip()
    if _TIP_ERR_RE.search(s):
        return "ERR", "err", "Server Error"
    if _TIP_WARN_RE.search(s):
        return "WARN", "warn", "In-game warning"
    return "DETAIL", "detail", "In-game toast"


def _as_list(val: Any, *, dicts_only: bool = False) -> list[Any]:
    """Normalize Lua/JSON array fields safely (treating rapidjson empty {} as [] and sparse integer tables as lists)."""
    if isinstance(val, (list, tuple)):
        return [x for x in val if isinstance(x, dict)] if dicts_only else list(val)
    if isinstance(val, dict):
        if not val:
            return []
        vals = list(val.values())
        return [x for x in vals if isinstance(x, dict)] if dicts_only else vals
    return []


def _as_dict(val: Any) -> dict[str, Any]:
    """Normalize Lua/JSON object fields safely (treating rapidjson empty [] as {})."""
    return dict(val) if isinstance(val, dict) else {}


def _filter_in_game_tips(tips: Any) -> list[str]:
    """Filter out Unity RichText hex color strings (e.g. E000000) and deduplicate consecutive/repeated tips."""
    seq = _as_list(tips) if isinstance(tips, (list, tuple, dict)) else []
    if not seq:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in seq:
        if isinstance(item, (dict, list, tuple)):
            continue
        s = str(item or "").strip()
        if not s or _HEX_TIP_FILTER_RE.match(s) or s.upper() == "E000000":
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _safe_load_json_file(path: str, default: Any = None) -> Any:
    """Load JSON file safely, auto-recovering and repairing trailing extra data if present."""
    if not path or not os.path.isfile(path):
        return default
    raw = ""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            stripped = raw.lstrip()
            if stripped:
                obj, _ = json.JSONDecoder().raw_decode(stripped)
                _atomic_write_json(path, obj)
                return obj
        except Exception:
            pass
        return default
    except Exception:
        return default


def _load_json_cached(path: str, default: Any = None) -> Any:
    """Load and cache parsed JSON keyed by (normpath, mtime_ns, ctime_ns, size, ino), returning safe copies."""
    if not path or not os.path.isfile(path):
        return copy.deepcopy(default)
    ap = os.path.abspath(path)
    norm_ap = os.path.normcase(ap)
    try:
        sig = _stat_sig_from_stat(os.stat(ap))
    except OSError:
        return copy.deepcopy(default)
    with _JSON_MEM_LOCK:
        hit = _JSON_MEM_CACHE.get(norm_ap)
        if hit is not None and hit[0] == sig:
            return copy.deepcopy(hit[1])
    data = _safe_load_json_file(ap, default=None)
    if data is not None:
        try:
            post_sig = _stat_sig_from_stat(os.stat(ap))
        except OSError:
            post_sig = None
        if post_sig == sig:
            with _JSON_MEM_LOCK:
                if norm_ap not in _JSON_MEM_CACHE and len(_JSON_MEM_CACHE) >= _JSON_MEM_CACHE_MAX:
                    _JSON_MEM_CACHE.pop(next(iter(_JSON_MEM_CACHE)), None)
                _JSON_MEM_CACHE[norm_ap] = (sig, copy.deepcopy(data))
        return copy.deepcopy(data)
    return copy.deepcopy(default)


def _atomic_write_json(path: str, payload: Any) -> bool:
    """Write JSON atomically via a PID-and-timestamp-unique temporary sibling file + retry os.replace."""
    norm_ap = os.path.normcase(os.path.abspath(path)) if path else ""
    tmp = f"{path}.{os.getpid()}.{time.time_ns()}.tmp"
    try:
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        for attempt in range(5):
            try:
                os.replace(tmp, path)
                if norm_ap:
                    with _JSON_MEM_LOCK:
                        _JSON_MEM_CACHE.pop(norm_ap, None)
                return True
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05)
        if norm_ap:
            with _JSON_MEM_LOCK:
                _JSON_MEM_CACHE.pop(norm_ap, None)
        return True
    except Exception:
        if norm_ap:
            with _JSON_MEM_LOCK:
                _JSON_MEM_CACHE.pop(norm_ap, None)
        return False
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass


_INITIAL_DATA_DIR = DATA_DIR
_INITIAL_HEINZ_DATA_DIR = HEINZ_DATA_DIR
_MAP_INDEX_LOCK = threading.RLock()
_MAP_INDEX_SEQ = 0
_WORLD_MAP_INDEX_CACHE: dict[Any, Any] = {}
_ROSTER_POWER_MAP_CACHE: dict[tuple[str, tuple[tuple[str, int, int, int, int], ...]], dict[tuple[int, str], dict[str, Any]]] = {}
_TOOL_MODULE_LOCK = threading.RLock()
_TOOL_MODULE_CACHE: dict[tuple[str, str], Any] = {}
_GATHER_TABLE_LOCK = threading.RLock()
_GATHER_TABLE_CACHE: tuple[tuple[str, int, int, int, int] | None, dict[int, tuple[int, int, int, bool]]] | None = None
_WORLD_MAPS_LOCK = threading.RLock()
_WORLD_MAPS_CACHE: dict[str, Any] = {
    "manifest": None,
    "webp": {},
}
_WORLD_SEASON_ENUM_MAP: dict[int, str] = {
    0: "pre_season_1",
    1: "season_2",
    2: "season_3",
    3: "season_4",
    4: "season_5",
    5: "season_6",
}
_DEFAULT_WORLD_MAPS_MANIFEST: dict[str, Any] = {
    "version": 1,
    "y_origin": "top",
    "default_map_key": "pre_season_1",
    "season_enum_map": {str(k): v for k, v in _WORLD_SEASON_ENUM_MAP.items()},
    "zones_overlay": {
        "file": "zones overlay.webp",
        "width": 1024,
        "height": 1024,
        "grid_size": 1000,
    },
    "major_cities": [
        {"id": 1, "x": 500, "y": 500, "level": 7, "name": "Capital"},
    ],
    "maps": [
        {
            "key": "pre_season_1",
            "label": "Pre-Season 1 / S1 (Wasteland)",
            "short_label": "S1 Wasteland",
            "world_season_ids": [0],
            "grid_size": 1000,
            "file": "pre season 1.webp",
            "width": 1024,
            "height": 1024,
            "y_origin": "top",
            "source_kind": "satellite_4k",
            "supports_zones": True,
        },
        {
            "key": "season_2",
            "label": "Season 2 (Wastes Watcher)",
            "short_label": "S2 Desert",
            "world_season_ids": [1],
            "grid_size": 1000,
            "file": "season 2.webp",
            "width": 1024,
            "height": 1024,
            "y_origin": "top",
            "source_kind": "topology_biome",
            "supports_zones": True,
        },
        {
            "key": "season_3",
            "label": "Season 3 (Everfrost Era)",
            "short_label": "S3 Everfrost",
            "world_season_ids": [2],
            "grid_size": 1000,
            "file": "season 3.webp",
            "width": 1024,
            "height": 1024,
            "y_origin": "top",
            "source_kind": "satellite_4k",
            "supports_zones": True,
        },
        {
            "key": "season_4",
            "label": "Season 4 (Dinosaur Origin)",
            "short_label": "S4 Dinosaur",
            "world_season_ids": [3],
            "grid_size": 1000,
            "file": "season 4.webp",
            "width": 1024,
            "height": 1024,
            "y_origin": "top",
            "source_kind": "satellite_4k",
            "supports_zones": True,
        },
        {
            "key": "season_5",
            "label": "Season 5 (Moonlit Elegy)",
            "short_label": "S5 Moonlit",
            "world_season_ids": [4],
            "grid_size": 1000,
            "file": "season 5.webp",
            "width": 1024,
            "height": 1024,
            "y_origin": "top",
            "source_kind": "topology_biome",
            "supports_zones": True,
        },
        {
            "key": "season_6",
            "label": "Season 6 (Archipelago 1600)",
            "short_label": "S6 Archipelago",
            "world_season_ids": [5],
            "grid_size": 1600,
            "file": "season 6.webp",
            "width": 1024,
            "height": 1024,
            "y_origin": "top",
            "source_kind": "topology_biome",
            "supports_zones": False,
        },
    ],
}


def _world_maps_dir(maps_dir: str | None = None) -> str:
    """Resolve launcher/assets/world maps directory."""
    if maps_dir:
        return os.path.abspath(str(maps_dir))
    return os.path.abspath(os.path.join(RES_ROOT, "assets", "world maps"))


def _load_world_maps_manifest(maps_dir: str | None = None) -> dict[str, Any]:
    """Load and cache assets/world maps/manifest.json keyed by absolute path and stat signature."""
    base_dir = _world_maps_dir(maps_dir)
    manifest_path = os.path.abspath(os.path.join(base_dir, "manifest.json"))
    norm_path = os.path.normcase(manifest_path)
    sig: tuple[int, int, int, int] | None = None
    if os.path.isfile(manifest_path):
        try:
            sig = _stat_sig_from_stat(os.stat(manifest_path))
        except OSError:
            sig = None

    with _WORLD_MAPS_LOCK:
        cached = _WORLD_MAPS_CACHE.get("manifest")
        if (
            isinstance(cached, tuple)
            and len(cached) == 3
            and cached[0] == norm_path
            and cached[1] == sig
            and isinstance(cached[2], dict)
        ):
            return copy.deepcopy(cached[2])

    parsed: dict[str, Any] | None = None
    if sig is not None:
        raw = _safe_load_json_file(manifest_path, default=None)
        if isinstance(raw, dict) and isinstance(raw.get("maps"), list) and raw.get("maps"):
            parsed = raw
    data = parsed if parsed is not None else copy.deepcopy(_DEFAULT_WORLD_MAPS_MANIFEST)

    if sig is not None and parsed is not None:
        try:
            post_sig = _stat_sig_from_stat(os.stat(manifest_path))
        except OSError:
            post_sig = None
        if post_sig == sig:
            with _WORLD_MAPS_LOCK:
                _WORLD_MAPS_CACHE["manifest"] = (norm_path, sig, copy.deepcopy(data))
    return copy.deepcopy(data)


def _world_maps_by_key(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index manifest map entries by lowercase season key."""
    out: dict[str, dict[str, Any]] = {}
    for entry in (manifest.get("maps") or []):
        if isinstance(entry, dict):
            key = str(entry.get("key") or "").strip().lower()
            if key:
                out[key] = entry
    return out


def _world_season_enum_from_manifest(manifest: dict[str, Any]) -> dict[int, str]:
    """Build int->season_key map from manifest with _WORLD_SEASON_ENUM_MAP baseline."""
    enum_map = dict(_WORLD_SEASON_ENUM_MAP)
    raw = manifest.get("season_enum_map")
    if isinstance(raw, dict):
        for k, v in raw.items():
            ik = _safe_int(k, None)
            sv = str(v or "").strip().lower()
            if ik is not None and sv:
                enum_map[ik] = sv
    return enum_map


def _format_available_world_maps(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Build compact available_maps list for UI dropdowns and overview RPC."""
    out: list[dict[str, Any]] = []
    for entry in (manifest.get("maps") or []):
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key") or "").strip()
        if not key:
            continue
        ws_ids = [_safe_int(x, 0) for x in (entry.get("world_season_ids") or []) if _safe_int(x, None) is not None]
        out.append({
            "key": key,
            "label": str(entry.get("label") or key),
            "short_label": str(entry.get("short_label") or entry.get("label") or key),
            "world_season_ids": ws_ids,
            "grid_size": _safe_int(entry.get("grid_size"), 1000),
            "supports_zones": bool(entry.get("supports_zones", False)),
            "source_kind": str(entry.get("source_kind") or ""),
        })
    return out


def _load_world_map_webp_data_uri(filename: str, maps_dir: str | None = None) -> str:
    """Lazily read and cache a world_maps WebP file as a base64 data URI keyed by path + stat signature."""
    clean_name = os.path.basename(str(filename or "").strip())
    if not clean_name or not clean_name.lower().endswith(".webp"):
        return ""
    base_dir = _world_maps_dir(maps_dir)
    file_path = os.path.abspath(os.path.join(base_dir, clean_name))
    norm_path = os.path.normcase(file_path)
    if not os.path.isfile(file_path):
        return ""
    try:
        sig = _stat_sig_from_stat(os.stat(file_path))
    except OSError:
        return ""

    with _WORLD_MAPS_LOCK:
        webp_cache = _WORLD_MAPS_CACHE.setdefault("webp", {})
        hit = webp_cache.get(norm_path)
        if isinstance(hit, tuple) and len(hit) == 2 and hit[0] == sig and isinstance(hit[1], str):
            return hit[1]

    try:
        with open(file_path, "rb") as fh:
            f_sig = _stat_sig_from_stat(os.fstat(fh.fileno()))
            raw_bytes = fh.read()
        if not raw_bytes:
            return ""
        b64 = base64.b64encode(raw_bytes).decode("ascii")
        uri = f"data:image/webp;base64,{b64}"
    except OSError:
        return ""

    if f_sig == sig:
        with _WORLD_MAPS_LOCK:
            webp_cache = _WORLD_MAPS_CACHE.setdefault("webp", {})
            webp_cache[norm_path] = (sig, uri)
    return uri


class _IndexedHQList(list):
    """List subclass carrying monotonic _index_seq to avoid CPython id() ABA collisions."""

    _index_seq: int | None = None

_SPECIAL_EVENT_RESOURCE_IDS = frozenset({1206, 1605, 1608, 1707, 1708})

_RESOURCE_TYPE_LABELS: dict[int, str] = {
    1: "Food",
    2: "Wood",
    11: "Water",
    12: "Electricity",
    14: "Zent",
    15: "Diamond",
    9003: "Battlefield Points",
    9004: "Lava Energy",
}

_RESOURCE_TYPE_ALIASES: dict[str, int] = {
    "1": 1, "food": 1, "metal": 1, "stone": 1, "farmland": 1, "mine": 1, "mine (metal)": 1,
    "2": 2, "wood": 2, "lumber": 2, "lumberyard": 2, "lumberyard (wood)": 2,
    "11": 11, "water": 11,
    "12": 12, "electricity": 12, "power": 12, "windmill": 12, "windmill (electricity)": 12, "power plant": 12,
    "14": 14, "zent": 14, "money": 14, "cash": 14, "zent mine": 14, "farm": 14, "farm (food)": 14,
    "15": 15, "diamond": 15, "diamonds": 15, "gold": 15,
    "9003": 9003, "battlefield points": 9003, "battlefield": 9003, "dragon": 9003,
    "9004": 9004, "lava energy": 9004, "lava": 9004, "volcano": 9004,
}

# Embedded 121-row aps gather resource.json lookup: resourceId -> (resource_type, level, reserve, is_event_node)
_DEFAULT_GATHER_RESOURCE_TABLE: dict[int, tuple[int, int, int, bool]] = {
    1: (1, 1, 100000, False), 2: (1, 2, 300000, False), 3: (1, 3, 600000, False), 4: (1, 4, 1200000, False),
    5: (1, 5, 2000000, False), 6: (1, 6, 3000000, False), 7: (1, 7, 4500000, False), 8: (1, 8, 6000000, False),
    9: (1, 9, 8000000, False), 10: (1, 10, 10000000, False),
    101: (11, 1, 120, False), 102: (11, 2, 200, False), 103: (11, 3, 500, False), 104: (11, 4, 750, False),
    105: (11, 5, 1250, False), 106: (11, 6, 2000, False), 107: (11, 7, 3000, False), 108: (11, 8, 4000, False),
    109: (11, 9, 5000, False), 110: (11, 10, 6000, False),
    201: (14, 1, 60000, False), 202: (14, 2, 180000, False), 203: (14, 3, 360000, False), 204: (14, 4, 720000, False),
    205: (14, 5, 1200000, False), 206: (14, 6, 1800000, False), 207: (14, 7, 2700000, False), 208: (14, 8, 3600000, False),
    209: (14, 9, 4800000, False), 210: (14, 10, 6000000, False),
    301: (15, 1, 12, False), 302: (15, 2, 20, False), 303: (15, 3, 50, False), 304: (15, 4, 75, False),
    305: (15, 5, 125, False), 306: (15, 6, 200, False), 307: (15, 7, 300, False), 308: (15, 8, 400, False),
    309: (15, 9, 500, False), 310: (15, 10, 600, False), 311: (15, 11, 350, False), 312: (15, 12, 500, False),
    313: (15, 13, 750, False), 314: (15, 14, 900, False), 315: (15, 15, 1200, False),
    401: (2, 1, 100000, False), 402: (2, 2, 300000, False), 403: (2, 3, 600000, False), 404: (2, 4, 1200000, False),
    405: (2, 5, 2000000, False), 406: (2, 6, 3000000, False), 407: (2, 7, 4500000, False), 408: (2, 8, 6000000, False),
    409: (2, 9, 8000000, False), 410: (2, 10, 10000000, False),
    501: (12, 1, 100000, False), 502: (12, 2, 300000, False), 503: (12, 3, 600000, False), 504: (12, 4, 1200000, False),
    505: (12, 5, 2000000, False), 506: (12, 6, 3000000, False), 507: (12, 7, 4500000, False), 508: (12, 8, 6000000, False),
    509: (12, 9, 8000000, False), 510: (12, 10, 10000000, False),
    601: (9003, 1, 300, False),
    701: (9004, 1, 10000000, False), 702: (9004, 1, 10000000, False), 703: (9004, 1, 120, False),
    704: (9004, 1, 120, False), 705: (9004, 1, 120, False),
    1001: (2, 1, 288000, True), 1002: (2, 2, 672000, True), 1003: (2, 3, 1152000, True), 1004: (2, 4, 1728000, True),
    1005: (2, 5, 2400000, True), 1006: (2, 5, 3600000, True), 1007: (2, 5, 4320000, True), 1008: (2, 5, 5040000, True),
    1009: (2, 5, 6048000, True), 1010: (2, 5, 7056000, True),
    1201: (1, 1, 288000, True), 1202: (1, 2, 672000, True), 1203: (1, 3, 1152000, True), 1204: (1, 4, 1728000, True),
    1205: (1, 5, 2400000, True), 1206: (1, 5, 3600000, True), 1207: (1, 5, 4320000, True), 1208: (1, 5, 5040000, True),
    1209: (1, 5, 6048000, True), 1210: (1, 5, 7056000, True),
    1501: (12, 1, 288000, True), 1502: (12, 2, 672000, True), 1503: (12, 3, 1152000, True), 1504: (12, 4, 1728000, True),
    1505: (12, 5, 2400000, True), 1506: (12, 5, 3600000, True), 1507: (12, 5, 4320000, True), 1508: (12, 5, 5040000, True),
    1509: (12, 5, 6048000, True), 1510: (12, 5, 7056000, True),
    1601: (14, 1, 172800, True), 1602: (14, 2, 403200, True), 1603: (14, 3, 691200, True), 1604: (14, 4, 1036800, True),
    1605: (14, 5, 1440000, True), 1606: (14, 5, 2160000, True), 1607: (14, 5, 2592000, True), 1608: (14, 5, 3024000, True),
    1609: (14, 5, 3628800, True), 1610: (14, 5, 4233600, True),
    1701: (15, 1, 30, True), 1702: (15, 2, 35, True), 1703: (15, 3, 40, True), 1704: (15, 4, 45, True),
    1705: (15, 5, 50, True), 1706: (15, 5, 60, True), 1707: (15, 5, 70, True), 1708: (15, 5, 80, True),
    1709: (15, 5, 90, True), 1710: (15, 5, 100, True),
}


def _resolve_map_data_dir() -> str:
    """Resolve map cache data dir honoring monkeypatched DATA_DIR / HEINZ_DATA_DIR or env override."""
    cur_data_dir = globals().get("DATA_DIR", HEINZ_DATA_DIR)
    if cur_data_dir != _INITIAL_DATA_DIR:
        return os.path.abspath(str(cur_data_dir))
    cur_heinz = globals().get("HEINZ_DATA_DIR", _INITIAL_HEINZ_DATA_DIR)
    if cur_heinz != _INITIAL_HEINZ_DATA_DIR:
        return os.path.abspath(str(cur_heinz))
    env_override = os.environ.get("HEINZ_DATA_DIR", "").strip()
    if env_override:
        return os.path.abspath(env_override)
    return os.path.abspath(str(cur_data_dir))


def _safe_int(val: Any, default: Any = 0) -> Any:
    """Safely coerce a value to int, returning `default` for None, bool, empty/non-numeric strings, or NaN/Inf."""
    if val is None or isinstance(val, bool):
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        if not math.isfinite(val):
            return default
        return int(val)
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return default
        try:
            return int(s)
        except ValueError:
            try:
                f = float(s)
                return int(f) if math.isfinite(f) else default
            except ValueError:
                return default
    try:
        return int(val)
    except (TypeError, ValueError, OverflowError):
        return default


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely coerce a value to finite float, returning `default` on invalid/non-finite inputs."""
    if val is None or isinstance(val, bool):
        return default
    if isinstance(val, (int, float)):
        f = float(val)
        return f if math.isfinite(f) else default
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return default
        try:
            f = float(s)
            return f if math.isfinite(f) else default
        except ValueError:
            return default
    try:
        f = float(val)
        return f if math.isfinite(f) else default
    except (TypeError, ValueError, OverflowError):
        return default


def _fast_index_to_xy(point_index: int, tile_count_x: int = 1000) -> tuple[int, int]:
    """Convert 1-based world map pointIndex to (x, y) coordinates."""
    idx = _safe_int(point_index, 0)
    if idx <= 0:
        return (0, 0)
    z = idx - 1
    y = z // tile_count_x
    x = z - y * tile_count_x
    return (x, y)


def _normalize_rss_type_filter(val: Any) -> int | None:
    """Normalize resource type filter string/ID (supporting Food/Metal, Wood/Lumber, Zent/Money, Diamond/Gold, etc.)."""
    s = str(val if val is not None else "").strip().lower()
    if not s or s in ("all", "any", "0"):
        return None
    if s in _RESOURCE_TYPE_ALIASES:
        return _RESOURCE_TYPE_ALIASES[s]
    try:
        num = int(s)
        return num if num > 0 else None
    except ValueError:
        return -1


def _get_gather_resource_table() -> dict[int, tuple[int, int, int, bool]]:
    """Return aps_gather_resource mapping, optionally overridden by megamind XML table in dev mode."""
    global _GATHER_TABLE_CACHE
    xml_path = os.path.join(REPO_ROOT, "megamind", "raw", "xml tables", "aps gather resource.json")
    sig: tuple[str, int, int, int, int] | None = None
    if os.path.isfile(xml_path):
        try:
            st = os.stat(xml_path)
            sig = (os.path.abspath(xml_path), *_stat_sig_from_stat(st))
        except OSError:
            sig = None
    with _GATHER_TABLE_LOCK:
        if _GATHER_TABLE_CACHE is not None and _GATHER_TABLE_CACHE[0] == sig:
            return dict(_GATHER_TABLE_CACHE[1])
        table = dict(_DEFAULT_GATHER_RESOURCE_TABLE)
        if sig is not None:
            raw = _safe_load_json_file(xml_path, default=None)
            rows = raw.get("rows") if isinstance(raw, dict) else None
            if isinstance(rows, dict):
                for k, v in rows.items():
                    if not isinstance(v, (list, tuple)) or len(v) < 5:
                        continue
                    try:
                        rid = int(k)
                        rtype = int(v[1])
                        lvl = int(v[3])
                        reserve = int(v[4])
                        is_ev = bool(len(v) > 15 and str(v[15] or "").strip()) or (rid in _SPECIAL_EVENT_RESOURCE_IDS)
                        table[rid] = (rtype, lvl, reserve, is_ev)
                    except Exception:
                        continue
        _GATHER_TABLE_CACHE = (sig, dict(table))
        return dict(table)


_MIN_WORLD_MAP_CACHE_BYTES = 5


def _discover_world_map_caches(data_dir: str, cache_file: str = "") -> tuple[list[str], list[dict[str, Any]]]:
    """Discover world_map_cache_s*.json files (falling back to world_map_cache.json) and expose file metadata."""
    cache_dir = os.path.join(data_dir, "cache")
    if not os.path.isdir(cache_dir):
        return [], []
    server_files = sorted(glob.glob(os.path.join(cache_dir, "world_map_cache_s*.json")))
    fallback_file = os.path.join(cache_dir, "world_map_cache.json")
    fallback_abs = os.path.abspath(fallback_file)
    all_candidates = list(server_files)
    if os.path.isfile(fallback_file) and fallback_abs not in {os.path.abspath(p) for p in all_candidates}:
        all_candidates.append(fallback_file)

    now_ts = time.time()
    available_meta: list[dict[str, Any]] = []
    for p in all_candidates:
        try:
            st = os.stat(p)
            available_meta.append({
                "name": os.path.basename(p),
                "path": os.path.abspath(p),
                "size": int(st.st_size),
                "mtime": float(st.st_mtime),
                "age_sec": max(0.0, round(now_ts - float(st.st_mtime), 1)),
            })
        except OSError:
            continue
    available_meta.sort(key=lambda item: item["mtime"], reverse=True)

    req_file = str(cache_file or "").strip()
    if req_file:
        matched = [
            m["path"]
            for m in available_meta
            if m["name"].lower() == os.path.basename(req_file).lower() or os.path.abspath(req_file) == m["path"]
        ]
        return matched, available_meta

    server_meta = [m for m in available_meta if m["path"] != fallback_abs]
    fallback_meta = [m for m in available_meta if m["path"] == fallback_abs]

    # Prefer populated (>= _MIN_WORLD_MAP_CACHE_BYTES) server caches, then populated fallback,
    # so empty/tiny `{}` server stubs never shadow a real cache; fall back cleanly if only tiny files exist.
    populated_servers = [m["path"] for m in server_meta if m["size"] >= _MIN_WORLD_MAP_CACHE_BYTES]
    if populated_servers:
        return populated_servers, available_meta
    populated_fallback = [m["path"] for m in fallback_meta if m["size"] >= _MIN_WORLD_MAP_CACHE_BYTES]
    if populated_fallback:
        return populated_fallback, available_meta
    if server_meta:
        return [m["path"] for m in server_meta], available_meta
    if fallback_meta:
        return [m["path"] for m in fallback_meta], available_meta
    return [], available_meta


def _load_roster_power_map(
    data_dir: str,
) -> tuple[tuple[tuple[str, int, int, int, int], ...], dict[tuple[int, str], dict[str, Any]]]:
    """Load top10_alliance_rosters.json across states keyed by (server_id, uid), cached safely by stat sig."""
    abs_data_dir = os.path.abspath(data_dir)
    pattern = os.path.join(abs_data_dir, "json cache", "bracket data", "state_*", "top10_alliance_rosters.json")
    paths = sorted(glob.glob(pattern))
    sig_parts: list[tuple[str, int, int, int, int]] = []
    expected_sigs: dict[str, tuple[int, int, int, int]] = {}
    valid_paths: list[str] = []
    had_read_error = False
    for p in paths:
        try:
            st = os.stat(p)
            ap = os.path.abspath(p)
            fsig = _stat_sig_from_stat(st)
            sig_parts.append((ap, *fsig))
            expected_sigs[ap] = fsig
            valid_paths.append(ap)
        except OSError:
            had_read_error = True
            continue
    sig_tuple = tuple(sig_parts)
    cache_key = (abs_data_dir, sig_tuple)
    if not had_read_error:
        with _MAP_INDEX_LOCK:
            cached_map = _ROSTER_POWER_MAP_CACHE.get(cache_key)
            if cached_map is not None:
                return sig_tuple, {k: dict(v) for k, v in cached_map.items()}

    roster_map: dict[tuple[int, str], dict[str, Any]] = {}
    for ap in valid_paths:
        parent_name = os.path.basename(os.path.dirname(ap))
        dir_sid = _safe_int(parent_name[6:], 0) if parent_name.startswith("state_") else 0
        try:
            with open(ap, "rb") as fh:
                f_sig = _stat_sig_from_stat(os.fstat(fh.fileno()))
                raw_text = fh.read().decode("utf-8", errors="replace")
            if f_sig != expected_sigs.get(ap):
                had_read_error = True
            data = json.loads(raw_text)
        except Exception:
            had_read_error = True
            continue
        if not isinstance(data, list):
            had_read_error = True
            continue
        for al in data:
            if not isinstance(al, dict):
                continue
            al_rank = _safe_int(al.get("rank"), 0)
            members = al.get("members") or []
            if not isinstance(members, list):
                continue
            for m in members:
                if not isinstance(m, dict):
                    continue
                try:
                    uid = str(m.get("uid") or "").strip()
                    if not uid:
                        continue
                    cur_sid = _safe_int(m.get("curServerId") or m.get("serverId") or dir_sid, dir_sid)
                    pwr_val = _safe_int(m.get("power"), None)
                    info = {
                        "power": pwr_val,
                        "army_kill": _safe_int(m.get("armyKill"), 0),
                        "online": bool(m.get("online", False)),
                        "roster_rank": al_rank or _safe_int(m.get("rank"), 0),
                    }
                    if dir_sid > 0:
                        roster_map[(dir_sid, uid)] = dict(info)
                    if cur_sid > 0 and (cur_sid, uid) not in roster_map:
                        roster_map[(cur_sid, uid)] = dict(info)
                except (TypeError, ValueError):
                    continue
    if not had_read_error:
        with _MAP_INDEX_LOCK:
            if len(_ROSTER_POWER_MAP_CACHE) >= 8:
                _ROSTER_POWER_MAP_CACHE.clear()
            _ROSTER_POWER_MAP_CACHE[cache_key] = {k: dict(v) for k, v in roster_map.items()}
    return sig_tuple, {k: dict(v) for k, v in roster_map.items()}


def _get_world_map_index(data_dir: str, dedup_by_uid: bool = True, cache_file: str = "") -> dict[str, Any]:
    """Parse and cache indexed HQs, RSS tiles, seasonal tiles, and roster power enrichment."""
    global _MAP_INDEX_SEQ
    req_cache_file = str(cache_file or "").strip()
    selected_paths, available_meta = _discover_world_map_caches(data_dir, cache_file=req_cache_file)

    stat_targets = (
        selected_paths
        if req_cache_file
        else sorted({m["path"] for m in available_meta} | {os.path.abspath(p) for p in selected_paths})
    )
    cache_sig_list: list[tuple[str, int, int, int, int]] = []
    expected_sigs: dict[str, tuple[int, int, int, int]] = {}
    had_read_error = False
    for p in stat_targets:
        try:
            ap = os.path.abspath(p)
            fsig = _stat_sig_from_stat(os.stat(ap))
            cache_sig_list.append((ap, *fsig))
            expected_sigs[ap] = fsig
        except OSError:
            had_read_error = True
            continue
    cache_sig = tuple(cache_sig_list)

    roster_sig, roster_map = _load_roster_power_map(data_dir)
    mem_key = (os.path.abspath(data_dir), req_cache_file.lower(), cache_sig, roster_sig, bool(dedup_by_uid))
    if not had_read_error:
        with _MAP_INDEX_LOCK:
            hit = _WORLD_MAP_INDEX_CACHE.get(mem_key)
            if hit is not None:
                hit["available_files"] = available_meta
                return hit

    gather_tbl = _get_gather_resource_table()

    def _parse_map_files(paths_to_read: list[str]) -> tuple[
        dict[tuple[int, str], tuple[tuple[int, int, bool, int], dict[str, Any]]],
        list[dict[str, Any]],
        dict[tuple[int, int], tuple[int, dict[str, Any]]],
        dict[tuple[int, int], tuple[int, dict[str, Any]]],
        int,
        int,
        float,
        set[int],
        bool,
        dict[int, int],
        int,
        int,
    ]:
        hq_dedup_local: dict[tuple[int, str], tuple[tuple[int, int, bool, int], dict[str, Any]]] = {}
        hq_all_local: list[dict[str, Any]] = []
        rss_best_local: dict[tuple[int, int], tuple[int, dict[str, Any]]] = {}
        seasonal_best_local: dict[tuple[int, int], tuple[int, dict[str, Any]]] = {}
        tot_raw = 0
        raw_hqs = 0
        newest_mt = 0.0
        srvs_local: set[int] = set()
        read_err = False
        pt_counts_local: dict[int, int] = {}
        max_coord_local = 0
        max_point_index_local = 0

        for ap in paths_to_read:
            abs_ap = os.path.abspath(ap)
            try:
                with open(abs_ap, "rb") as fh:
                    f_st = os.fstat(fh.fileno())
                    f_sig = _stat_sig_from_stat(f_st)
                    newest_mt = max(newest_mt, float(f_st.st_mtime))
                    raw_text = fh.read().decode("utf-8", errors="replace")
                exp_sig = expected_sigs.get(abs_ap)
                if exp_sig is not None and f_sig != exp_sig:
                    read_err = True
                raw_obj = json.loads(raw_text)
            except Exception:
                read_err = True
                continue
            if not isinstance(raw_obj, dict):
                read_err = True
                continue
            tot_raw += len(raw_obj)
            for k, entry in raw_obj.items():
                try:
                    if not isinstance(entry, dict) or entry.get("test"):
                        continue
                    pt = _safe_int(entry.get("pointType") or entry.get("PointType"), 0)
                    if pt > 0:
                        pt_counts_local[pt] = pt_counts_local.get(pt, 0) + 1
                    p_idx_val = _safe_int(entry.get("pointIndex"), 0)
                    m_idx_val = _safe_int(entry.get("mainIndex"), 0)
                    cand_idx = m_idx_val if m_idx_val > p_idx_val else p_idx_val
                    if cand_idx <= 0:
                        cand_idx = _safe_int(k, 0)
                    if cand_idx > max_point_index_local:
                        max_point_index_local = cand_idx
                    ex_raw = entry.get("x")
                    if ex_raw is not None:
                        ex_val = _safe_int(ex_raw, -1)
                        if ex_val > max_coord_local:
                            max_coord_local = ex_val
                    ey_raw = entry.get("y")
                    if ey_raw is not None:
                        ey_val = _safe_int(ey_raw, -1)
                        if ey_val > max_coord_local:
                            max_coord_local = ey_val
                    srv_raw = entry.get("serverId")
                    if pt == 6:
                        bi = entry.get("buildInfo")
                        if not isinstance(bi, dict):
                            continue
                        if _safe_int(bi.get("buildId"), 0) != 400000:
                            continue
                        server_id = _safe_int(srv_raw, None)
                        if server_id is None:
                            continue
                        owner_uid = str(bi.get("ownerUid") or "").strip()
                        if not owner_uid:
                            continue
                        raw_idx = entry.get("mainIndex") or entry.get("pointIndex") or k
                        idx = _safe_int(raw_idx, None)
                        if idx is None or idx < 0:
                            continue
                        srvs_local.add(server_id)
                        raw_hqs += 1
                        x, y = _fast_index_to_xy(idx)
                        if x > max_coord_local:
                            max_coord_local = x
                        if y > max_coord_local:
                            max_coord_local = y
                        k_int = _safe_int(k, 0)
                        main_idx = _safe_int(entry.get("mainIndex") or -1, -1)
                        aoi_ver = _safe_int(entry.get("aoiVersion"), 0)
                        last_hp_t = _safe_int(bi.get("lastHpTime"), 0)
                        tie_score = (aoi_ver, last_hp_t, k_int == main_idx, k_int)

                        r_info = roster_map.get((server_id, owner_uid))
                        pwr_val = r_info["power"] if r_info is not None else None
                        al_abbr = str(bi.get("alAbbr") or "").strip()
                        pname = str(bi.get("name") or "").strip() or f"Player #{owner_uid[-6:]}"
                        rec = {
                            "kind": "base",
                            "uid": owner_uid,
                            "name": pname,
                            "tag": al_abbr,
                            "alliance": al_abbr,
                            "alliance_id": str(bi.get("allianceId") or "").strip(),
                            "level": _safe_int(bi.get("level"), 0),
                            "x": x,
                            "y": y,
                            "server_id": server_id,
                            "protect_end_time": _safe_int(bi.get("protectEndTime"), 0),
                            "build_state": _safe_int(bi.get("buildState"), 0),
                            "current_hp": _safe_int(bi.get("currentHp"), 0),
                            "fire_end_time": _safe_int(bi.get("fireEndTime"), 0),
                            "aoi_version": aoi_ver,
                            "power": pwr_val,
                            "known_power": pwr_val is not None,
                            "army_kill": r_info["army_kill"] if r_info is not None else None,
                            "online": r_info["online"] if r_info is not None else None,
                            "roster_rank": r_info["roster_rank"] if r_info is not None else None,
                            "_search_hay": f"{pname} {al_abbr} {owner_uid} {x} {y} ({x},{y}) s{server_id}".lower(),
                        }
                        dkey = (server_id, owner_uid)
                        prev = hq_dedup_local.get(dkey)
                        if prev is None or tie_score > prev[0]:
                            hq_dedup_local[dkey] = (tie_score, rec)
                        if not dedup_by_uid:
                            hq_all_local.append(rec)
                    elif pt == 7:
                        ri = entry.get("resourceInfo")
                        if not isinstance(ri, dict):
                            continue
                        server_id = _safe_int(srv_raw, 0)
                        raw_idx = entry.get("mainIndex") or entry.get("pointIndex") or k
                        idx = _safe_int(raw_idx, None)
                        if idx is None or idx < 0:
                            continue
                        if server_id > 0:
                            srvs_local.add(server_id)
                        x, y = _fast_index_to_xy(idx)
                        if x > max_coord_local:
                            max_coord_local = x
                        if y > max_coord_local:
                            max_coord_local = y
                        rid = _safe_int(ri.get("resourceId"), 0)
                        rtype, r_lvl, r_reserve, tbl_ev = gather_tbl.get(rid, (0, 0, 0, False))
                        gather_uuid = _safe_int(ri.get("gatherUuid"), 0)
                        rss_owner = str(ri.get("ownerUid") or "").strip()
                        occupied = (gather_uuid != 0) or (rss_owner not in ("", "0"))
                        event_id = str(ri.get("eventId") or "").strip()
                        is_event_node = bool(tbl_ev or (rid in _SPECIAL_EVENT_RESOURCE_IDS) or event_id)
                        r_name = _RESOURCE_TYPE_LABELS.get(rtype, f"Resource #{rid}")
                        aoi_ver = _safe_int(entry.get("aoiVersion"), 0)
                        rss_rec = {
                            "kind": "rss",
                            "uid": f"rss:{server_id}:{idx}",
                            "name": f"Lv.{r_lvl} {r_name}" + (" (Event)" if is_event_node else ""),
                            "tag": "EVENT" if is_event_node else r_name,
                            "alliance": "Occupied" if occupied else "Open",
                            "level": r_lvl,
                            "x": x,
                            "y": y,
                            "server_id": server_id,
                            "resource_id": rid,
                            "resource_type": rtype,
                            "resource_name": r_name,
                            "reserve": r_reserve,
                            "occupied": occupied,
                            "gather_uuid": gather_uuid,
                            "owner_uid": rss_owner,
                            "event_id": event_id,
                            "is_event_node": is_event_node,
                            "has_shield": False,
                            "power": None,
                            "known_power": False,
                            "_search_hay": f"Lv.{r_lvl} {r_name} {x} {y} ({x},{y}) s{server_id}".lower(),
                        }
                        rkey = (server_id, idx)
                        prev_r = rss_best_local.get(rkey)
                        if prev_r is None or aoi_ver > prev_r[0]:
                            rss_best_local[rkey] = (aoi_ver, rss_rec)
                    elif pt in (11, 15, 16, 29, 32):
                        server_id = _safe_int(srv_raw, 0)
                        raw_idx = entry.get("mainIndex") or entry.get("pointIndex") or k
                        idx = _safe_int(raw_idx, None)
                        if idx is None or idx < 0:
                            continue
                        x, y = _fast_index_to_xy(idx)
                        if x > max_coord_local:
                            max_coord_local = x
                        if y > max_coord_local:
                            max_coord_local = y
                        aoi_ver = _safe_int(entry.get("aoiVersion"), 0)
                        skey = (server_id, idx)
                        prev_s = seasonal_best_local.get(skey)
                        if prev_s is None or aoi_ver > prev_s[0]:
                            seasonal_best_local[skey] = (aoi_ver, {
                                "kind": "seasonal",
                                "uid": f"hub:{server_id}:{idx}",
                                "name": f"Map Hub Type {pt}",
                                "tag": f"T{pt}",
                                "alliance": "",
                                "level": 0,
                                "x": x,
                                "y": y,
                                "server_id": server_id,
                                "has_shield": False,
                                "power": None,
                                "known_power": False,
                            })
                except (TypeError, ValueError):
                    continue

        return (
            hq_dedup_local,
            hq_all_local,
            rss_best_local,
            seasonal_best_local,
            tot_raw,
            raw_hqs,
            newest_mt,
            srvs_local,
            read_err,
            pt_counts_local,
            max_coord_local,
            max_point_index_local,
        )

    (
        hq_dedup,
        hq_all,
        rss_best,
        seasonal_best,
        total_raw_entries,
        raw_hq_count,
        newest_mtime,
        servers_set,
        parse_err,
        point_type_counts,
        max_coord,
        max_point_index,
    ) = _parse_map_files(selected_paths)
    had_read_error = had_read_error or parse_err

    valid_entry_count = raw_hq_count + len(rss_best) + len(seasonal_best)
    if valid_entry_count == 0 and not req_cache_file:
        fallback_abs = os.path.abspath(os.path.join(data_dir, "cache", "world_map_cache.json"))
        avail_paths = {m["path"] for m in available_meta}
        sel_abs_set = {os.path.abspath(p) for p in selected_paths}
        if fallback_abs in avail_paths and fallback_abs not in sel_abs_set:
            (
                fb_hq_dedup,
                fb_hq_all,
                fb_rss_best,
                fb_seasonal_best,
                fb_tot_raw,
                fb_raw_hqs,
                fb_newest_mt,
                fb_srvs,
                fb_err,
                fb_pt_counts,
                fb_max_coord,
                fb_max_pidx,
            ) = _parse_map_files([fallback_abs])
            had_read_error = had_read_error or fb_err
            fb_valid = fb_raw_hqs + len(fb_rss_best) + len(fb_seasonal_best)
            if fb_valid > 0 or (not point_type_counts and fb_pt_counts):
                hq_dedup = fb_hq_dedup
                hq_all = fb_hq_all
                rss_best = fb_rss_best
                seasonal_best = fb_seasonal_best
                total_raw_entries = fb_tot_raw
                raw_hq_count = fb_raw_hqs
                newest_mtime = fb_newest_mt
                servers_set = fb_srvs
                selected_paths = [fallback_abs]
                valid_entry_count = fb_valid
                point_type_counts = fb_pt_counts
                max_coord = fb_max_coord
                max_point_index = fb_max_pidx

    with _MAP_INDEX_LOCK:
        _MAP_INDEX_SEQ += 1
        index_seq = _MAP_INDEX_SEQ

    dedup_hqs = _IndexedHQList(item[1] for item in hq_dedup.values())
    dedup_hqs._index_seq = index_seq
    hqs_list = dedup_hqs if dedup_by_uid else hq_all
    rss_list = [item[1] for item in rss_best.values()]
    seasonal_list = [item[1] for item in seasonal_best.values()]
    hqs_by_uid = {hq["uid"]: hq for hq in dedup_hqs}
    hqs_by_server: dict[int, list[dict[str, Any]]] = {}
    for hq in hqs_list:
        hqs_by_server.setdefault(int(hq.get("server_id") or 0), []).append(hq)
    rss_by_server: dict[int, list[dict[str, Any]]] = {}
    for r in rss_list:
        rss_by_server.setdefault(int(r.get("server_id") or 0), []).append(r)

    result = {
        "_index_seq": index_seq,
        "has_world_cache": bool(selected_paths and valid_entry_count > 0),
        "selected_files": [os.path.basename(p) for p in selected_paths],
        "available_files": available_meta,
        "newest_mtime": newest_mtime,
        "total_raw_entries": total_raw_entries,
        "raw_hq_count": raw_hq_count,
        "deduped_hq_count": len(dedup_hqs),
        "collapsed_duplicates": max(0, raw_hq_count - len(dedup_hqs)),
        "dedup_hqs": dedup_hqs,
        "hqs": hqs_list,
        "hqs_by_server": hqs_by_server,
        "rss": rss_list,
        "rss_by_server": rss_by_server,
        "seasonal": seasonal_list,
        "hqs_by_uid": hqs_by_uid,
        "servers": sorted(servers_set),
        "roster_matched_count": sum(1 for hq in dedup_hqs if hq["known_power"]),
        "point_type_counts": dict(point_type_counts),
        "max_coord": max_coord,
        "max_point_index": max_point_index,
    }
    if not had_read_error:
        with _MAP_INDEX_LOCK:
            if len(_WORLD_MAP_INDEX_CACHE) >= 8:
                _WORLD_MAP_INDEX_CACHE.clear()
            _WORLD_MAP_INDEX_CACHE[mem_key] = result
    return result


def _infer_world_season_from_map_cache(
    data_dir: str,
    index: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Infer world season offline from cached world_map_cache PointType/coordinate signatures."""
    idx_data = index if isinstance(index, dict) else _get_world_map_index(data_dir, dedup_by_uid=True)
    if not isinstance(idx_data, dict):
        return None
    pt_counts_raw = idx_data.get("point_type_counts")
    pt_counts: dict[int, int] = {}
    if isinstance(pt_counts_raw, dict):
        for k, v in pt_counts_raw.items():
            ik = _safe_int(k, None)
            iv = _safe_int(v, 0)
            if ik is not None and iv > 0:
                pt_counts[ik] = iv
    max_coord = _safe_int(idx_data.get("max_coord"), 0)
    max_pidx = _safe_int(idx_data.get("max_point_index"), 0)

    if max_coord >= 1000 or max_pidx >= 1_000_000:
        return {
            "world_season_id": 5,
            "season_key": _WORLD_SEASON_ENUM_MAP[5],
            "source": "world_map_cache",
            "signal": "coord_1600",
            "max_coord": max_coord,
            "max_point_index": max_pidx,
        }
    s5_hits = pt_counts.get(35, 0) + pt_counts.get(36, 0)
    if s5_hits > 0:
        return {
            "world_season_id": 4,
            "season_key": _WORLD_SEASON_ENUM_MAP[4],
            "source": "world_map_cache",
            "signal": "point_type_35_36",
            "matched_count": s5_hits,
        }
    s4_hits = pt_counts.get(38, 0)
    if s4_hits > 0:
        return {
            "world_season_id": 3,
            "season_key": _WORLD_SEASON_ENUM_MAP[3],
            "source": "world_map_cache",
            "signal": "point_type_38",
            "matched_count": s4_hits,
        }
    s3_hits = pt_counts.get(26, 0) + pt_counts.get(29, 0)
    if s3_hits > 0:
        return {
            "world_season_id": 2,
            "season_key": _WORLD_SEASON_ENUM_MAP[2],
            "source": "world_map_cache",
            "signal": "point_type_26_29",
            "matched_count": s3_hits,
        }
    return None


_ALLIANCE_CLUSTER_CACHE: dict[tuple[Any, ...], list[dict[str, Any]]] = {}


def _cluster_matches_search(c: dict[str, Any], q: str) -> bool:
    if not q:
        return True
    hay = (
        f"{c.get('name', '')} {c.get('tag', '')} {c.get('x', '')} {c.get('y', '')} "
        f"({c.get('x', '')},{c.get('y', '')}) ({c.get('x', '')}, {c.get('y', '')}) "
        f"{c.get('cx', '')} {c.get('cy', '')} s{c.get('server_id', '')} {c.get('server_id', '')}"
    ).lower()
    return q in hay


def _compute_alliance_clusters(
    dedup_hqs: list[dict[str, Any]],
    now_ts: float,
    cluster_radius: float = 45.0,
    min_members: int = 5,
    server_id: int = 0,
    min_hq: int = 1,
    unshielded_only: bool = False,
    search: str = "",
    origin_x: int | None = None,
    origin_y: int | None = None,
    *,
    alliance: str = "",
    index_seq: int | None = None,
) -> list[dict[str, Any]]:
    """Iterative Dense-Core Hive Extraction grouped by (server_id, al_abbr) with squared-dist + monotonic seq memoization."""
    radius = round(max(5.0, 45.0 if cluster_radius is None else _safe_float(cluster_radius, 45.0)), 2)
    min_cnt = max(2, 5 if min_members is None else _safe_int(min_members, 5))
    srv_filter = max(0, 0 if server_id is None else _safe_int(server_id, 0))
    hq_floor = max(1, 1 if min_hq is None else _safe_int(min_hq, 1))
    q = str(search or "").strip().lower()
    al_filter = str(alliance or "").strip().lower()

    seq_tag = index_seq if index_seq is not None else getattr(dedup_hqs, "_index_seq", None)
    cache_key = None
    base_clusters: list[dict[str, Any]] | None = None
    if seq_tag is not None and len(dedup_hqs) > 20:
        cache_key = (
            int(seq_tag),
            len(dedup_hqs),
            int(now_ts // 30.0),
            radius,
            min_cnt,
            srv_filter,
            hq_floor,
            bool(unshielded_only),
            al_filter,
            origin_x,
            origin_y,
        )
        with _MAP_INDEX_LOCK:
            cached_clusters = _ALLIANCE_CLUSTER_CACHE.get(cache_key)
            if cached_clusters is not None:
                base_clusters = [dict(c) for c in cached_clusters]

    if base_clusters is None:
        r2 = radius * radius
        groups: dict[tuple[int, str], list[dict[str, Any]]] = {}
        for hq in dedup_hqs:
            tag = str(hq.get("tag") or "").strip()
            if not tag:
                continue
            sid = int(hq.get("server_id") or 0)
            if srv_filter > 0 and sid != srv_filter:
                continue
            if al_filter and al_filter not in tag.lower():
                continue
            groups.setdefault((sid, tag), []).append(hq)

        clusters: list[dict[str, Any]] = []
        for (sid, tag), members in groups.items():
            if len(members) < min_cnt:
                continue
            rem = list(members)
            hive_idx = 0
            while len(rem) >= min_cnt:
                best_nbrs: list[dict[str, Any]] = []
                best_len = 0
                for anchor in rem:
                    ax, ay = anchor["x"], anchor["y"]
                    nbrs = [
                        m for m in rem
                        if ((m["x"] - ax) * (m["x"] - ax) + (m["y"] - ay) * (m["y"] - ay)) <= r2
                    ]
                    if len(nbrs) > best_len:
                        best_nbrs = nbrs
                        best_len = len(nbrs)
                if best_len < min_cnt:
                    break
                cx = sum(m["x"] for m in best_nbrs) / best_len
                cy = sum(m["y"] for m in best_nbrs) / best_len
                core = [
                    m for m in rem
                    if ((m["x"] - cx) * (m["x"] - cx) + (m["y"] - cy) * (m["y"] - cy)) <= r2
                ]
                if len(core) < min_cnt:
                    core = best_nbrs
                n_core = len(core)
                cx = sum(m["x"] for m in core) / n_core
                cy = sum(m["y"] for m in core) / n_core

                dists = sorted(math.hypot(m["x"] - cx, m["y"] - cy) for m in core)
                med_r = dists[n_core // 2]
                p80_idx = min(n_core - 1, int(0.8 * (n_core - 1)))
                p80_r = dists[p80_idx]
                max_r = dists[-1]

                unshielded_cnt = sum(1 for m in core if int(m.get("protect_end_time") or 0) <= now_ts)
                avg_hq = sum(int(m.get("level") or 0) for m in core) / n_core
                max_hq_val = max(int(m.get("level") or 0) for m in core)
                hq_25_cnt = sum(1 for m in core if int(m.get("level") or 0) >= 25)
                known_powers = [int(m["power"]) for m in core if m.get("power") is not None]
                known_power_cnt = len(known_powers)
                total_known_pwr = sum(known_powers)
                avg_known_pwr = round(total_known_pwr / known_power_cnt) if known_power_cnt > 0 else None

                hive_idx += 1
                passes_post = True
                if unshielded_only and unshielded_cnt <= 0:
                    passes_post = False
                if hq_floor > 1 and max_hq_val < hq_floor:
                    passes_post = False

                if passes_post:
                    dist_origin = (
                        round(math.hypot(cx - origin_x, cy - origin_y), 1)
                        if (origin_x is not None and origin_y is not None)
                        else None
                    )
                    clusters.append({
                        "kind": "cluster",
                        "uid": f"cluster:{sid}:{tag}:{hive_idx}",
                        "name": f"[{tag}] Hive" + (f" #{hive_idx}" if hive_idx > 1 else ""),
                        "tag": tag,
                        "alliance": tag,
                        "server_id": sid,
                        "hive_index": hive_idx,
                        "cx": round(cx, 1),
                        "cy": round(cy, 1),
                        "x": int(round(cx)),
                        "y": int(round(cy)),
                        "core_count": n_core,
                        "member_count": len(members),
                        "unshielded_count": unshielded_cnt,
                        "hq_25_count": hq_25_cnt,
                        "med_r": round(med_r, 1),
                        "p80_r": round(p80_r, 1),
                        "max_r": round(max_r, 1),
                        "avg_hq": round(avg_hq, 2),
                        "max_hq": max_hq_val,
                        "level": max_hq_val,
                        "known_power_count": known_power_cnt,
                        "total_known_power": total_known_pwr,
                        "avg_known_power": avg_known_pwr,
                        "power": total_known_pwr if known_power_cnt > 0 else None,
                        "has_shield": unshielded_cnt == 0,
                        "distance": dist_origin,
                    })

                core_uids = {m["uid"] for m in core}
                rem = [m for m in rem if m["uid"] not in core_uids]

        clusters.sort(key=lambda c: (-c["unshielded_count"], -c["core_count"], -c["avg_hq"], c["med_r"]))
        if cache_key is not None:
            with _MAP_INDEX_LOCK:
                if len(_ALLIANCE_CLUSTER_CACHE) >= 64:
                    _ALLIANCE_CLUSTER_CACHE.clear()
                _ALLIANCE_CLUSTER_CACHE[cache_key] = [dict(c) for c in clusters]
        base_clusters = clusters

    if q:
        return [c for c in base_clusters if _cluster_matches_search(c, q)]
    return base_clusters


_LUA_JSON_SER = r"""
local _rjson = package and package.loaded and package.loaded.rapidjson
local _ARR_MT = { __jsontype = "array" }
local _OBJ_MT = { __jsontype = "object" }
local function _jarr(t)
    t = t or {}
    if _rjson and type(_rjson.array) == "function" then
        local okA, arr = pcall(_rjson.array, t)
        if okA and type(arr) == "table" then return arr end
    end
    return setmetatable(t, _ARR_MT)
end
local function _jobj(t)
    t = t or {}
    if _rjson and type(_rjson.object) == "function" then
        local okO, obj = pcall(_rjson.object, t)
        if okO and type(obj) == "table" then return obj end
    end
    return setmetatable(t, _OBJ_MT)
end
local function _ser_fallback(v, depth)
    depth = depth or 0
    if depth > 6 then return "null" end
    local t = type(v)
    if t == "number" then
        if v ~= v or v == math.huge or v == -math.huge then return "null" end
        return tostring(v)
    elseif t == "boolean" then return tostring(v)
    elseif t == "string" then
        local s = v:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\b', '\\b'):gsub('\f', '\\f'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t')
        s = s:gsub('[%z\1-\31]', function(c) return string.format('\\u%04x', string.byte(c)) end)
        return '"' .. s .. '"'
    elseif t == "table" then
        local mt = getmetatable(v)
        local jtype = type(mt) == "table" and mt.__jsontype or nil
        local isArr, maxI, cnt = true, 0, 0
        for k, _ in pairs(v) do
            cnt = cnt + 1
            if type(k) ~= "number" or k <= 0 or math.floor(k) ~= k then isArr = false
            elseif k > maxI then maxI = k end
        end
        if cnt == 0 then
            if jtype == "object" then return "{}" end
            return "[]"
        end
        if jtype ~= "object" and isArr and maxI == cnt then
            local p = {}
            for i = 1, cnt do p[i] = _ser_fallback(v[i], depth + 1) end
            return "[" .. table.concat(p, ",") .. "]"
        else
            local p = {}
            for k, val in pairs(v) do table.insert(p, _ser_fallback(tostring(k), depth + 1) .. ":" .. _ser_fallback(val, depth + 1)) end
            return "{" .. table.concat(p, ",") .. "}"
        end
    end
    return '""'
end
local function ser(v, depth)
    if depth == nil and _rjson and _rjson.encode then
        local okJ, encJ = pcall(_rjson.encode, v)
        if okJ and type(encJ) == "string" then return encJ end
    end
    return _ser_fallback(v, depth)
end
"""


def log_crash(err: Any) -> None:
    try:
        if os.path.isfile(CRASH_LOG) and os.path.getsize(CRASH_LOG) > 512 * 1024:
            old = CRASH_LOG + ".1"
            try:
                os.replace(CRASH_LOG, old)
            except OSError:
                pass
        msg = _redact_text(err)
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
            if isinstance(err, BaseException):
                f.write(_redact_text(traceback.format_exc()) + "\n")
    except Exception:
        pass


def _hidden_startupinfo():
    si_cls = getattr(subprocess, "STARTUPINFO", None)
    if si_cls is None:
        return None
    si = si_cls()
    si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
    si.wShowWindow = 0
    return si


_CANONICAL_TOOL_SINGLETONS: dict[str, str] = {
    "client_discovery": "heinz_client_discovery_singleton",
    "bot_actions": "heinz_bot_actions_singleton",
}


def _load_tool_module(mod_name: str, rel_path: str):
    full_path = os.path.abspath(os.path.join(REPO_ROOT, rel_path))
    if not os.path.exists(full_path):
        return None
    cache_key = (full_path, str(mod_name))
    singleton_key = _CANONICAL_TOOL_SINGLETONS.get(str(mod_name))
    with _TOOL_MODULE_LOCK:
        cached = _TOOL_MODULE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        if singleton_key and singleton_key in sys.modules:
            existing = sys.modules[singleton_key]
            if getattr(existing, "__file__", None) and os.path.normcase(os.path.abspath(existing.__file__)) == os.path.normcase(full_path):
                _TOOL_MODULE_CACHE[cache_key] = existing
                return existing
        spec = importlib.util.spec_from_file_location(mod_name, full_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        registered_singleton = False
        if singleton_key and singleton_key not in sys.modules:
            sys.modules[singleton_key] = mod
            registered_singleton = True
        try:
            spec.loader.exec_module(mod)
        except BaseException:
            if registered_singleton and sys.modules.get(singleton_key) is mod:
                sys.modules.pop(singleton_key, None)
            raise
        if singleton_key and singleton_key in sys.modules:
            mod = sys.modules[singleton_key]
        _TOOL_MODULE_CACHE[cache_key] = mod
        return mod


try:
    _env_mod = _load_tool_module("auto_detect_environment", os.path.join("tools", "auto detect environment.py"))
    detect_environment = _env_mod.detect_environment if _env_mod else None
except Exception:
    detect_environment = None

if detect_environment is None:
    def detect_environment(pid=None):
        return {"isLive": False, "serverId": 694, "fightServerId": 697, "bracketId": 16, "bracketServers": list(range(689, 705))}

try:
    client_discovery = _load_tool_module("client_discovery", os.path.join("tools", "client discovery.py"))
except Exception:
    client_discovery = None

try:
    multi_client_bot = _load_tool_module("multi_client_bot", os.path.join("tools", "multi client bot.py"))
except Exception:
    multi_client_bot = None

try:
    bot_actions = _load_tool_module("bot_actions", os.path.join("tools", "bot actions.py"))
except Exception:
    bot_actions = None

try:
    sync_farm_clients = _load_tool_module("sync_farm_clients", os.path.join("tools", "sync farm clients.py"))
except Exception:
    sync_farm_clients = None


TASK_CATALOG: list[dict[str, str]] = [
    {
        "key": "alliance_daily",
        "title": "Alliance Red Packets & Tasks",
        "category": "Daily Care & Alliance",
        "tag": "Packets + Task Boxes",
        "desc": "Grabs alliance Red Packets and collects finished alliance task & contribution milestone boxes. (Alliance Tech Auto-Donate & Both Gift Tabs run in the Always-On Automation panel.)",
    },
    {
        "key": "radar_events",
        "title": "Radar Events",
        "category": "Daily Care & Alliance",
        "tag": "Scan + All 4 Types",
        "desc": "Triggers the Radar scan first, claims finished rewards, and completes all 4 Radar Event types: Ally Help, Gather/Dig, NPC/Skull Attack, and Radar Exploration (Auto-Skip).",
    },
    {
        "key": "daily_tasks_complete",
        "title": "Daily Tasks (Complete All)",
        "category": "Daily Care & Alliance",
        "tag": "Auto-Complete + Chests",
        "desc": "Scans your live Daily Tasks popup and completes all actionable tasks in one go (Post Likes, Hero EXP, Recruitment Ticket, Building Upgrade, Tech Research, Troop Training, Speedup, Alliance Help/Donate, Radar, Bounty Missions, Intercity Trade Trucks, Arena, Boomer Rallies, Gathering), then claims every task & milestone chest (30-150). Safely skips paid packs & PvP HQ attacks.",
    },
    {
        "key": "daily_claims",
        "title": "Daily Claims & Event Passes",
        "category": "Daily Care & Alliance",
        "tag": "Rewards + Passes",
        "desc": "Claims all completed Daily Tasks, Daily Activity Milestone Chests (1-6), Achievements, Chapter Tasks, and all active Battle Passes & Event Passes.",
    },
    {
        "key": "vip_store_rewards",
        "title": "VIP & Store Freebies",
        "category": "Daily Care & Alliance",
        "tag": "Daily Freebies",
        "desc": "Collects your daily VIP login points, VIP freebies chest, and the free reward in the 2nd tab of the Store.",
    },
    {
        "key": "war_safety",
        "title": "War Safety & Peace Shield",
        "category": "Protection & War",
        "tag": "Shield + Recall",
        "desc": "Watches for incoming enemy marches on your Headquarters or resource tiles, recalls exposed gathering squads, and activates a Peace Shield when safe from War Fever.",
    },
    {
        "key": "rf_hq_under_attack",
        "title": "Reinforce Attacked Allies",
        "category": "Protection & War",
        "tag": "Ally HQ Defense",
        "desc": "Sends reinforcement troops to alliance members or protected accounts when their Headquarters comes under attack.",
    },
    {
        "key": "arena",
        "title": "Arena",
        "category": "Combat & Events",
        "tag": "x5 • 70%+ Win Odds",
        "desc": "Builds 1v1 or 3v3 pure-faction top-5 hero lineups, skips tough fights, and only challenges opponents when win odds exceed 70%.",
    },
    {
        "key": "hero_battlefield",
        "title": "Hero Battlefield",
        "category": "Combat & Events",
        "tag": "Quick Fight • Auto-Skip",
        "desc": "Uses Quick Fight where unlocked across Blood Rose, Wings of Dawn, and Guard of Order battlefields, auto-fills strongest matching-faction heroes, and skips stage battles automatically.",
    },
    {
        "key": "area_exploration",
        "title": "Regional Exploration",
        "category": "Combat & Events",
        "tag": "HQ Explore • Auto-Skip",
        "desc": "Collects idle exploration chest rewards, advances unlocked stages, and runs solo Regional Exploration battles with automatic in-battle Skip enabled.",
    },
    {
        "key": "furylord",
        "title": "Furylord",
        "category": "Combat & Events",
        "tag": "03:00 • Squad 1 x4",
        "desc": "Targets the scheduled 03:00 Furylord window using Squad 1 so all daily boss damage rewards are secured automatically.",
    },
    {
        "key": "tyrant_event",
        "title": "The Tyrant",
        "category": "Combat & Events",
        "tag": "Squad 1 Host + Join",
        "desc": "Claims free Tyrant rewards, hosts a Squad 1 team-up rally against The Tyrant, joins open alliance Tyrant rallies with extra squads, and repeats smoothly.",
    },
    {
        "key": "boomer_runs",
        "title": "Boomer Rallies",
        "category": "Combat & Events",
        "tag": "Join + Host",
        "desc": "Joins open alliance Boomer rallies or starts new team-up rallies within your stamina reserve for Hero EXP and Boomer Spoils.",
    },
    {
        "key": "mining_event",
        "title": "Gold & XP Event Mines (Mon / Tue)",
        "category": "Combat & Events",
        "tag": "Lv7 Empty Nodes",
        "desc": "Finds unoccupied Gold or XP event mines on Mondays and Tuesdays so accounts gather event rewards safely without hitting other players.",
    },
    {
        "key": "treasure_helicopter",
        "title": "Treasure Dig (Crashed Helicopter)",
        "category": "Progression & Farming",
        "tag": "Map Dig + Drops",
        "desc": "Claims crashed helicopter supply drops and dispatches squads to active alliance Treasure Dig spots nearby.",
    },
    {
        "key": "research_queue",
        "title": "Tech Research Queue",
        "category": "Progression & Farming",
        "tag": "Lab + Free Speedup",
        "desc": "Collects completed research, starts recommended or priority technologies automatically, uses free speedups, and requests Alliance Help.",
    },
    {
        "key": "free_recruits",
        "title": "Free Hero Recruits & Safe Chests",
        "category": "Progression & Farming",
        "tag": "Free Timer + Drops",
        "desc": "Uses strictly free timer Hero Recruits and opens safe non-choice drop chests in your bag without touching choice boxes, speedups, or Peace Shields.",
    },
    {
        "key": "garage_upgrades",
        "title": "Mod Vehicle Upgrades (Monday)",
        "category": "Progression & Farming",
        "tag": "Mondays Only",
        "desc": "Every Monday, equips stronger Mod Vehicle parts, merges matching components, and performs free refits for event points.",
    },
    {
        "key": "hero_progression",
        "title": "Hero Progression (VS Hero Day)",
        "category": "Progression & Farming",
        "tag": "VS Day 4 • Gear + Skills + EXP",
        "desc": "Upgrades hero levels, breakthroughs, stars (respecting Universal Shard reserves), skills (Badges), auto-equips best gear, and enhances gear with Alloy while honoring VS Hero Day guards.",
    },
    {
        "key": "full_preparedness",
        "title": "Full Preparedness",
        "category": "Progression & Farming",
        "tag": "Phase Boxes",
        "desc": "Collects Full Preparedness phase & activity milestone chests and aligns timed progression actions with active 4-hour themes.",
    },
    {
        "key": "speedups",
        "title": "Free Speedups",
        "category": "Progression & Farming",
        "tag": "Main: Free Only",
        "desc": "Hits free speedup buttons as soon as timers enter the free window; on farms, optionally spends small speedups during Full Preparedness.",
    },
    {
        "key": "troop_training",
        "title": "Troop Training",
        "category": "Progression & Farming",
        "tag": "All Camps • Event Zoom",
        "desc": "Collects finished troops, trains your highest unlocked tier across all training camps, and automatically speed-zooms with Training Speedups when Full Preparedness or Alliance Duel scores troop training.",
    },
    {
        "key": "building_upgrades",
        "title": "HQ & Building Upgrades",
        "category": "Progression & Farming",
        "tag": "HQ Priority",
        "desc": "Harvests camp resources, upgrades Headquarters or required prerequisite buildings when builders are free, and requests Alliance Help.",
    },
    {
        "key": "bounties",
        "title": "Bounty Missions",
        "category": "Progression & Farming",
        "tag": "Lock Orange + Assist + Plunder",
        "desc": "3-in-1 Bounty Missions automation: locks Orange missions before refreshing, dispatches Orange missions, assists allies' Orange missions, and plunders cross-state Lv5+ Orange missions.",
    },
    {
        "key": "trucks",
        "title": "Intercity Trade Trucks",
        "category": "Progression & Farming",
        "tag": "Claim + Roll Orange + Plunder",
        "desc": "Claims finished Intercity Trade trucks first, rolls for Orange trucks, dispatches open slots, and plunders weaker cross-state trucks.",
    },
]

_DIALOG_CACHE: dict[str, str] | None = None

def _get_dialog_dict() -> dict[str, str]:
    global _DIALOG_CACHE
    if _DIALOG_CACHE is not None:
        return _DIALOG_CACHE
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(os.path.join(meipass, "assets", "english-dialog.txt"))
        candidates.append(os.path.join(meipass, "launcher", "assets", "english-dialog.txt"))
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    candidates.append(os.path.join(exe_dir, "assets", "english-dialog.txt"))
    candidates.append(os.path.join(exe_dir, "_internal", "assets", "english-dialog.txt"))
    candidates.append(os.path.join(REPO_ROOT, "launcher", "assets", "english-dialog.txt"))
    candidates.append(os.path.join(REPO_ROOT, "assets", "english-dialog.txt"))
    cand = next((p for p in candidates if os.path.isfile(p)), None)
    d: dict[str, str] = {}
    if cand:
        try:
            with open(cand, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        d[k.strip()] = v.strip()
        except Exception:
            pass
    _DIALOG_CACHE = d
    return _DIALOG_CACHE

FALLBACK_ITEM_NAMES: dict[int, str] = {
    210110: "5-min Speedup",
    210112: "1-hr Speedup",
    210119: "5-min Building Speedup",
    210120: "1-hr Building Speedup",
    210122: "8-hr Building Speedup",
    210129: "1-min Speedup",
    210163: "1-hr Research Speedup",
    200210: "Transporters",
    200211: "Unlock Infantry Barracks",
    200212: "Shooter Camp",
    200213: "Unlock Tank Plant",
    200221: "Unlock Oil Refinery",
    200222: "Metal Furnace",
    200223: "Power Plant Generator",
    200230: "Food Farm Expansion",
    200231: "Water Filtration Plant",
    200232: "Gas Tank",
    200233: "Medical Station",
    200240: "Catalyst I",
    200241: "Catalyst II",
    200243: "Catalyst IV",
}

def _parse_speedup_info(name: str, item_id: int) -> tuple[int, str]:
    nl = name.lower()
    stype = "Universal"
    if "build" in nl or "construct" in nl:
        stype = "Building"
    elif "research" in nl or "tech" in nl:
        stype = "Research"
    elif "train" in nl or "recruit" in nl:
        stype = "Training"
    elif "heal" in nl or "hospital" in nl:
        stype = "Healing"

    mins = 0
    m = re.search(r"(\d+)\s*-\s*min", nl)
    if m:
        mins = int(m.group(1))
    else:
        m = re.search(r"(\d+)\s*-\s*hr", nl)
        if m:
            mins = int(m.group(1)) * 60
        else:
            m = re.search(r"(\d+)\s*-\s*d(?:ay)?", nl)
            if m:
                mins = int(m.group(1)) * 1440
            else:
                m = re.search(r"(\d+)d\b", nl)
                if m:
                    mins = int(m.group(1)) * 1440
                else:
                    m = re.search(r"(\d+)h\b", nl)
                    if m:
                        mins = int(m.group(1)) * 60
                    else:
                        m = re.search(r"(\d+)m\b", nl)
                        if m:
                            mins = int(m.group(1))

    if mins == 0 and ("speedup" in nl or item_id in (210110, 210112, 210119, 210120, 210122, 210129, 210163)):
        if item_id in (210110, 210119):
            mins = 5
        elif item_id in (210112, 210120, 210163):
            mins = 60
        elif item_id == 210122:
            mins = 480
        elif item_id == 210129:
            mins = 1
    return mins, stype

def _format_duration_mins(mins: int) -> str:
    if mins <= 0:
        return "0m"
    days = mins // 1440
    rem = mins % 1440
    hours = rem // 60
    m = rem % 60
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if m > 0 and days == 0:
        parts.append(f"{m}m")
    return " ".join(parts) if parts else "<1m"

def _format_count_num(num: int) -> str:
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B".replace(".0B", "B")
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M".replace(".0M", "M")
    if num >= 10_000:
        return f"{num / 1_000:.1f}K".replace(".0K", "K")
    return f"{num:,}"

def _parse_resource_amount(name: str) -> tuple[str, int]:
    nl = name.lower()
    res_type = ""
    if "food" in nl:
        res_type = "Food"
    elif "wood" in nl:
        res_type = "Wood"
    elif "metal" in nl:
        res_type = "Metal"
    elif "electricity" in nl:
        res_type = "Electricity"
    elif any(x in nl for x in ("zent", "mineral", "water", "fuel")):
        res_type = "Zents"
    elif "diamond" in nl:
        res_type = "Diamonds"
    if not res_type:
        return ("", 0)
    cleaned = name.replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([KkMmBb])\b", cleaned)
    if m:
        num = float(m.group(1))
        unit = m.group(2).upper()
        mul = {"K": 1000, "M": 1000000, "B": 1000000000}.get(unit, 1)
        return (res_type, int(num * mul))
    m = re.search(r"\b(\d+)\b", cleaned)
    if m:
        val = int(m.group(1))
        if val >= 100:
            return (res_type, val)
    return (res_type, 0)

def _deduce_category_and_rarity(name: str, item_type: int, quality: int, item_id: int) -> tuple[str, str, int]:
    nl = name.lower()
    qlty = int(quality or 1)
    if "speedup" in nl or item_type == 3 or item_id in (210110, 210112, 210119, 210120, 210122, 210129, 210163):
        cat = "speedups"
    elif item_type == 204 or any(w in nl for w in ("chest", "crate", "box", "bundle", "pack", "supply", "food", "wood", "metal", "electricity", "mineral", "water", "fuel", "zent", "diamond", "alloy")):
        cat = "chests"
    elif item_type in (62, 91, 93, 507) or any(w in nl for w in ("hero", "fragment", "refugee", "selena", "nyx", "starlight", "barbie", "skill book", "tome")):
        cat = "heroes"
    elif item_type in (120, 129, 211) or any(w in nl for w in ("badge", "wings", "guard", "rose", "equipment", "core", "wrench", "stone", "blueprint", "decor")):
        cat = "gear"
    else:
        cat = "other"

    if qlty <= 1:
        if any(w in nl for w in ("mythic", "gold", "legendary", "orange")):
            qlty = 5
        elif any(w in nl for w in ("epic", "purple")):
            qlty = 4
        elif any(w in nl for w in ("rare", "blue", "silver")):
            qlty = 3
        elif any(w in nl for w in ("uncommon", "green", "bronze")):
            qlty = 2
        else:
            qlty = 1

    rarity_map = {1: "common", 2: "uncommon", 3: "rare", 4: "epic", 5: "legendary", 6: "mythic"}
    return cat, rarity_map.get(qlty, "common"), qlty


class HubBackend:
    """Thread-safe controller backing the HeinZ web UI."""

    def __init__(self, defer_enhanced: bool = False) -> None:
        self._lock = threading.RLock()
        self._defer_enhanced: bool = bool(defer_enhanced)
        self._enhanced_active: bool = not bool(defer_enhanced)
        self._monitors_started: bool = False
        self._heinz_auth_session: dict[str, Any] = {
            "signed_in": bool(not defer_enhanced),
            "mode": "enhanced_cli" if not defer_enhanced else "",
            "identifier": "",
        }
        self._engine_task_lock = threading.RLock()
        self._engine_cancel_ev = threading.Event()
        self._engine_task_state: dict[str, Any] = {
            "running": False,
            "action": "",
            "stage": "idle",
            "pct": 0.0,
            "done_files": 0,
            "total_files": 0,
            "done_bytes": 0,
            "total_bytes": 0,
            "speed_mbps": 0.0,
            "current_file": "",
            "ok": True,
            "message": "",
            "error": "",
        }
        self._log_seq = 0
        self._log_epoch = 0
        self._logs_cleared_seq = 0
        self.logs: list[dict[str, Any]] = []
        self.is_monitoring = True
        self._window: Any = None

        self.target_pid: int | None = None
        self.selected_client_pid: int | None = None
        self.selected_client_label: str | None = None
        self.discovered_clients: list[dict[str, Any]] = []
        self.running_clients: list[dict[str, Any]] = []
        self._live_info_by_pid: dict[int, dict[str, Any]] = {}
        self._uid_name_cache: dict[str, str] = {}
        self._active_actions: set[str] = set()
        self._last_env_pid: int | None = None
        self._last_env_ts = 0.0
        self._live_sync_ts: dict[str, float] = {}
        self._world_season_live_cache: dict[str, tuple[float, int | None, dict[str, Any]]] = {}
        self._hotkey_thread: threading.Thread | None = None
        self._hotkey_thread_id: int | None = None
        self._daemon_proc: Any = None
        self._config_snapshot_cache: tuple[str, tuple[int, int, int, int] | None, int, dict[str, Any]] | None = None
        self._last_good_config_snapshot: tuple[int, dict[str, Any]] | None = None
        self._config_version: int = 1
        self._log_dir_ready: bool = False

        self.is_online = False
        self.status_text = "Scanning running Last Z clients..."
        self.fps_text = "Checking"
        self.dropdown_values = ["Auto"]
        self.selected_dropdown = "Auto"
        self.finder_status = {
            "text": "Choose a resource and level, then click Jump in Game or Auto-March Squad.",
            "tone": "muted",
        }
        self.env: dict[str, Any] = {
            "isLive": False,
            "serverId": 0,
            "fightServerId": 0,
            "playerName": "Player",
            "allianceTag": "",
            "allianceName": "",
            "allianceMembers": 0,
            "bracketId": 0,
            "bracketServers": [],
            "hqLv": 0,
        }
        self.setup_status: dict[str, Any] = {
            "base_found": False,
            "multi_instance_ready": False,
            "clone_count": 0,
            "suggested_next": {
                "slot_number": 2,
                "label": "Account 2",
                "unity_profile": "Alt2Z",
                "exe_name": "Alt2Game.exe",
                "root_dir": os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"), "Last Z_Alt2"),
            },
        }
        self.fleet_state: dict[str, Any] = {
            "summary": "Scanning clients...",
            "daemon_running": False,
            "win_task_text": "Checking...",
            "last_cycle_text": "Never",
            "clients": [],
        }

        self._always_on_daemon_enabled: bool = True
        self._always_on_daemon_state: str = "watching"
        self._always_on_wake = threading.Event()
        self._always_on_gen: int = 0
        self._always_on_thread_started: bool = False
        self._always_on_due_reset: set[str] = set()

        self._hospital_watcher_enabled: bool = False
        self._hospital_watcher_state: str = "off"
        self._hospital_watcher_target: str = "all"
        self._hospital_watcher_wake = self._always_on_wake
        self._hospital_watcher_gen: int = 0
        self._hospital_watcher_reset_flag: bool = False
        self._hospital_watcher_thread_started: bool = False
        self._hospital_watcher_dry_run: bool = False
        self._hospital_watcher_last_summary: dict[str, Any] = {
            "wounded_total": 0,
            "in_treatment_total": 0,
            "untreated_total": 0,
            "queued_troops": 0,
            "batches_chained": 0,
            "cross_client_helps_triggered": 0,
            "updated_at": 0.0,
        }

        self._alliance_help_watcher_enabled: bool = True
        self._alliance_help_watcher_state: str = "watching"
        self._alliance_help_interval_sec: float = 15.0
        self._alliance_help_wake = self._always_on_wake
        self._alliance_help_gen: int = 0
        self._alliance_help_thread_started: bool = False
        self._alliance_help_stats: dict[str, Any] = {
            "enabled": True,
            "interval_seconds": 15,
            "total_allies_helped": 0,
            "total_help_requests_sent": 0,
            "total_chests_tab1": 0,
            "total_chests_tab2": 0,
            "total_chests_claimed": 0,
            "last_allies_helped": 0,
            "last_help_requests_sent": 0,
            "last_chests_tab1": 0,
            "last_chests_tab2": 0,
            "last_chests_claimed": 0,
            "cycles_run": 0,
            "clients_checked": 0,
            "last_action_summary": "",
            "last_action_at": 0.0,
            "updated_at": 0.0,
        }

        self._alliance_tech_watcher_enabled: bool = True
        self._alliance_tech_watcher_state: str = "watching"
        self._alliance_tech_interval_sec: float = 45.0
        self._alliance_tech_stats: dict[str, Any] = {
            "enabled": True,
            "interval_seconds": 45,
            "total_tech_donations": 0,
            "last_tech_donations": 0,
            "last_tech_id": 0,
            "cycles_run": 0,
            "clients_checked": 0,
            "last_action_summary": "",
            "last_action_at": 0.0,
            "updated_at": 0.0,
        }

        self._farm_loop_lock = threading.RLock()
        self._farm_loop_seq: int = 0
        self._farm_loops: dict[int, dict[str, Any]] = {}
        self._last_farm_loop_summary: dict[str, dict[str, Any]] = {
            "rss": self._default_farm_category_summary("rss"),
            "kills": self._default_farm_category_summary("kills"),
        }
        self._last_kill_detection: dict[str, Any] = {}
        # Per-PID safety state: detection snapshots, stop summaries, worker exec serialization & persisted claims
        self._last_kill_detection_by_pid: dict[int, dict[str, Any]] = {}
        self._last_farm_loop_summary_by_pid: dict[int, dict[str, dict[str, Any]]] = {}
        self._farm_pid_exec_locks: dict[int, threading.Lock] = {}
        self._farm_pid_state: dict[int, dict[str, Any]] = {}

        self._load_cached_state()
        self._load_always_on_daemon_config()
        if not self._defer_enhanced:
            self._start_always_on_daemon()
            self.log("HeinZ Helper initialized and ready (Unified Always-On Automation daemon active).", "ok")
        else:
            self.log("HeinZ Standalone Launcher ready (waiting for Vanilla or Enhanced mode selection - 0 hooks attached).", "info")

    def set_window(self, win: Any) -> None:
        self._window = win

    def _load_cached_state(self) -> None:
        try:
            status_cache = os.path.join(DATA_DIR, "bot status.json")
            if os.path.exists(status_cache):
                sdata = _safe_load_json_file(status_cache, default={})
                if isinstance(sdata, dict):
                    cached_clients = sdata.get("clients") or (sdata.get("last_cycle", {}) or {}).get("clients", [])
                    for lc_item in cached_clients:
                        if not isinstance(lc_item, dict):
                            continue
                        snap = lc_item.get("snapshot") or {}
                        suid = str(snap.get("uid") or "").strip()
                        sname = str(snap.get("name") or "").strip()
                        if suid and sname:
                            self._uid_name_cache[suid] = sname
            for cname in ("client profiles.json", "clients.json"):
                cache_clients = os.path.join(DATA_DIR, cname)
                if os.path.exists(cache_clients):
                    cdata = _safe_load_json_file(cache_clients, default=None)
                    self.discovered_clients = (
                        cdata if isinstance(cdata, list) else (cdata.get("clients", []) if isinstance(cdata, dict) else [])
                    )
                    if self.discovered_clients:
                        break
            env_candidates = [
                os.path.join(DATA_DIR, "detected_environment.json"),
                os.path.join(DATA_DIR, "json cache", "detected_environment.json"),
            ]
            if not getattr(sys, "frozen", False):
                env_candidates.extend([
                    os.path.join(TOOLS_DIR, "detected_environment.json"),
                    os.path.join(SCRATCH_DIR, "detected_environment.json"),
                ])
            for env_cache in env_candidates:
                if os.path.exists(env_cache):
                    cached = _safe_load_json_file(env_cache, default=None)
                    if isinstance(cached, dict) and cached:
                        self.env.update(cached)
                        break
            self.running_clients = self._discover_running_clients(query_lua=False)
            self._update_dropdown_values(self.running_clients)
            self._refresh_setup_status()
            self._refresh_fleet_state()
        except Exception as exc:
            self.log(f"Startup cache note: {exc}", "warn")

    _LOG_RING_MAX = 1000

    def log(
        self,
        msg: str,
        kind: str = "info",
        category: str | None = None,
        is_tip: bool = False,
    ) -> None:
        clean_msg = _redact_text(msg)
        raw_kind = str(kind or "info").strip().lower()
        norm_kind = raw_kind if raw_kind in ("stage", "step", "detail", "ok", "warn", "err", "info") else "info"
        norm_cat = str(category).strip().upper() if category else ""
        detected_tip = bool(is_tip)

        probe = clean_msg.lstrip()
        if not norm_cat:
            if probe.startswith("[STAGE ") or probe.startswith("[STAGE]"):
                norm_kind, norm_cat = "stage", "STAGE"
            elif probe.startswith("[BOT_STEP]") or probe.startswith("[STEP]"):
                norm_kind, norm_cat = "step", "STEP"
            elif probe.startswith("[BOT_DETAIL]") or probe.startswith("[DETAIL]"):
                norm_kind, norm_cat = "detail", "DETAIL"
            elif probe.startswith("[BOT_ERR]") or probe.startswith("[ERR]"):
                norm_kind, norm_cat = "err", "ERR"
            elif probe.startswith("[BOT_TIP]") or probe.startswith("[BOT_MODAL]"):
                detected_tip = True
                if "error" in probe.lower():
                    norm_kind, norm_cat = "err", "ERR"
                else:
                    norm_kind, norm_cat = "warn", "WARN"
            elif probe.startswith("[WARN]"):
                norm_kind, norm_cat = "warn", "WARN"
            elif probe.startswith("[OK]"):
                norm_kind, norm_cat = "ok", "OK"
            else:
                norm_cat = norm_kind.upper()
        if "in-game tip" in probe.lower() or "popped modal" in probe.lower() or "server error" in probe.lower():
            detected_tip = True

        fps_val = getattr(self, "current_fps", None)
        fps_tag = f"[FPS: {fps_val}] " if (fps_val and norm_kind not in ("detail", "stage")) else ""
        # Avoid redundant "[DETAIL] [DETAIL] ..." in log file & console
        tag_prefix = f"[{norm_cat}] "
        body_msg = clean_msg[len(tag_prefix):] if clean_msg.startswith(tag_prefix) else clean_msg
        formatted_msg = f"{fps_tag}{body_msg}" if fps_tag and not body_msg.startswith("[FPS:") else body_msg
        time_str = time.strftime("%H:%M:%S")
        entry = {
            "id": 0,
            "time": time_str,
            "msg": formatted_msg,
            "kind": norm_kind,
            "cat": norm_cat,
            "is_tip": detected_tip,
        }
        with self._lock:
            self._log_seq += 1
            entry["id"] = self._log_seq
            self.logs.append(entry)
            if len(self.logs) > self._LOG_RING_MAX:
                self.logs = self.logs[-self._LOG_RING_MAX:]

        diag_line = f"[{time_str}] [{norm_cat}] {formatted_msg}\n"
        try:
            sys.stdout.write(diag_line)
            sys.stdout.flush()
        except Exception:
            pass
        try:
            with _CONSOLE_FILE_LOCK:
                if not getattr(self, "_log_dir_ready", False):
                    os.makedirs(DATA_DIR, exist_ok=True)
                    self._log_dir_ready = True
                log_path = os.path.join(DATA_DIR, "heinz_live_console.log")
                if os.path.isfile(log_path) and os.path.getsize(log_path) > _LIVE_CONSOLE_MAX_BYTES:
                    try:
                        os.replace(log_path, log_path + ".1")
                    except OSError:
                        pass
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(diag_line)
        except Exception:
            pass

    def _resolve_client_context(self, pid: int | None = None) -> tuple[list[dict[str, Any]], int | None, dict[str, Any] | None, str, str]:
        """Resolve active running process, display label, and sanitized cache stem cleanly."""
        running = self._discover_running_clients()
        with self._lock:
            sel_pid = self.selected_client_pid
            tgt_pid = self.target_pid
            sel_lbl = self.selected_client_label
        explicit_pid: int | None = None
        if pid is not None:
            try:
                explicit_pid = int(pid)
            except Exception:
                explicit_pid = -1
            target_pid = explicit_pid if explicit_pid > 0 else None
        else:
            target_pid = sel_pid or tgt_pid
        proc = next((p for p in running if int(p.get("pid") or 0) == target_pid), None) if target_pid else None
        if explicit_pid is None and proc is None and running and sel_pid is None:
            proc = next((p for p in running if str(p.get("role", "")).lower() == "main"), running[0])
            target_pid = int(proc["pid"])
        account_label = self._client_display_name(proc) if proc else (sel_lbl or "" if explicit_pid is None else "")
        clean_label = re.sub(r"[^a-zA-Z0-9_\-]", "_", account_label.lower()).strip("_") if account_label else ""
        return running, target_pid, proc, account_label, clean_label

    def clear_logs(self) -> dict[str, Any]:
        with self._lock:
            self.logs.clear()
            self._log_epoch = int(getattr(self, "_log_epoch", 0)) + 1
            self._logs_cleared_seq = int(getattr(self, "_log_seq", 0))
            epoch = self._log_epoch
        return {"ok": True, "log_epoch": epoch}

    def _prewarm_map_index_bg(self) -> None:
        """Low-priority startup warm-up of world_map_cache_*.json so Map Rip opens instantaneously."""
        time.sleep(2.5)
        if not self.is_monitoring:
            return
        try:
            data_dir = _resolve_map_data_dir()
            _get_world_map_index(data_dir, dedup_by_uid=True)
        except Exception:
            pass

    def _ensure_translator_bg(self) -> None:
        if not self.is_monitoring:
            return
        try:
            mod = self._load_translator_mod()
            if mod is not None:
                mod.ensure_server_running()
        except Exception:
            pass

    def _heal_farm_launchers_bg(self) -> None:
        if not self.is_monitoring or sync_farm_clients is None:
            return
        if not hasattr(sync_farm_clients, "heal_all_farm_launchers"):
            return
        try:
            rep = sync_farm_clients.heal_all_farm_launchers(dry_run=False, force=False)
            if isinstance(rep, dict) and rep.get("healed_count", 0) > 0:
                details = "; ".join(
                    str(r.get("message") or "")
                    for r in (rep.get("results") or [])
                    if r.get("healed") or not r.get("ok")
                )
                self.log(f"Farm Launcher Auto-Heal: {rep.get('summary')} ({details})", "ok")
        except Exception:
            pass

    def start_monitors(self) -> None:
        with self._lock:
            if self._monitors_started:
                return
            self._monitors_started = True
            self._enhanced_active = True
        threading.Thread(target=self._poll_loop, daemon=True).start()
        threading.Thread(target=self.ensure_daemon_running, daemon=True).start()
        hk_thread = threading.Thread(target=self._global_hotkey_loop, daemon=True, name="GlobalHotkeyLoop")
        self._hotkey_thread = hk_thread
        hk_thread.start()
        threading.Thread(target=self._prewarm_map_index_bg, daemon=True).start()
        threading.Thread(target=self._ensure_translator_bg, daemon=True, name="LiveTranslatorWarmup").start()
        threading.Thread(target=self._heal_farm_launchers_bg, daemon=True, name="FarmLauncherAutoHeal").start()
        self._start_always_on_daemon()

    def set_launcher_window_mode(self, view_mode: str = "login_step") -> dict[str, Any]:
        """Resize and center the native window cleanly between compact standalone popup pages and full Enhanced Hub."""
        win = getattr(self, "_window", None)
        mode = str(view_mode or "login_step").strip().lower()
        presets: dict[str, tuple[int, int, str]] = {
            "login_step": (440, 450, "HeinZ Login"),
            "launcher_step": (540, 540, "HeinZ Launcher"),
            "mode_step": (540, 540, "HeinZ Launcher"),
            "accounts_step": (540, 540, "HeinZ Launcher"),
            "hub": (1240, 840, "HeinZ Helper"),
        }
        target_w, target_h, target_title = presets.get(mode, presets["launcher_step"])
        if win is None:
            return {"ok": True, "mode": mode, "width": target_w, "height": target_h, "resized": False}
        try:
            sw, sh = _get_primary_screen_size()
            if sw > 0 and sh > 0:
                target_w = min(target_w, max(420, sw - 40))
                target_h = min(target_h, max(380, sh - 60))
                tx = max(0, (sw - target_w) // 2)
                ty = max(0, (sh - target_h) // 2)
            else:
                tx, ty = 120, 120
            if hasattr(win, "set_title"):
                win.set_title(target_title)
            if hasattr(win, "resize"):
                win.resize(int(target_w), int(target_h))
            if hasattr(win, "move"):
                win.move(int(tx), int(ty))
            return {"ok": True, "mode": mode, "width": target_w, "height": target_h, "resized": True}
        except Exception as exc:
            return {"ok": False, "mode": mode, "error": str(exc)}

    def activate_enhanced_mode(self) -> dict[str, Any]:
        """Activate Enhanced mode lazily (starts monitors, 180 FPS daemon, live translator & Always-On automation)."""
        was_active = bool(getattr(self, "_enhanced_active", False) and getattr(self, "_monitors_started", False))
        self.start_monitors()
        self.set_launcher_window_mode("hub")
        if not was_active:
            self.log("Enhanced Mode activated - HeinZ Helper, 180 FPS Daemon & Smart Translator active.", "ok")
        return {"ok": True, "enhanced_active": True}

    def shutdown(self) -> None:
        """Cleanly stop background loops, wake blocking hotkey & watcher threads, and terminate owned daemon."""
        self.is_monitoring = False
        try:
            self._stop_farm_loops_internal(pid=None, category=None, reason="shutdown", join_timeout=1.0, log_stop=False)
        except Exception:
            pass
        wake_ev = getattr(self, "_always_on_wake", None)
        if wake_ev is not None:
            try:
                wake_ev.set()
            except Exception:
                pass
        tid = getattr(self, "_hotkey_thread_id", None)
        if os.name == "nt" and tid:
            try:
                import ctypes
                from ctypes import wintypes

                u32 = ctypes.WinDLL("user32", use_last_error=True)
                u32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
                u32.PostThreadMessageW.restype = wintypes.BOOL
                WM_QUIT = 0x0012
                u32.PostThreadMessageW(int(tid), WM_QUIT, 0, 0)
            except Exception:
                pass
        hk_thread = getattr(self, "_hotkey_thread", None)
        if hk_thread is not None and hk_thread.is_alive() and hk_thread is not threading.current_thread():
            try:
                hk_thread.join(timeout=1.5)
            except Exception:
                pass
        with self._lock:
            dp = getattr(self, "_daemon_proc", None)
            self._daemon_proc = None
        if dp is not None:
            try:
                if dp.poll() is None:
                    dp.terminate()
            except Exception:
                pass

    def _global_hotkey_loop(self) -> None:
        """Listen for Windows global hotkey Ctrl+Shift+M using kernel-blocking GetMessageW (0 idle wakeups/sec)."""
        if os.name != "nt":
            return
        user32: Any = None
        registered = False
        HOTKEY_ID = 0x485A  # 'HZ'
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.GetCurrentThreadId.argtypes = []
            kernel32.GetCurrentThreadId.restype = wintypes.DWORD
            user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
            user32.RegisterHotKey.restype = wintypes.BOOL
            user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
            user32.GetMessageW.restype = ctypes.c_int
            user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
            user32.UnregisterHotKey.restype = wintypes.BOOL

            if not self.is_monitoring:
                return
            self._hotkey_thread_id = int(kernel32.GetCurrentThreadId())
            MOD_CONTROL = 0x0002
            MOD_SHIFT = 0x0004
            MOD_NOREPEAT = 0x4000
            VK_M = 0x4D
            WM_HOTKEY = 0x0312

            registered = bool(user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_M))
            if not registered or not self.is_monitoring:
                return
            self.log("Global Hotkey registered: Ctrl+Shift+M triggers Full Map Load (or F6 inside Last Z).", "info")
            msg = wintypes.MSG()
            last_fire = 0.0
            while self.is_monitoring:
                ret = int(user32.GetMessageW(ctypes.byref(msg), None, 0, 0))
                if ret <= 0:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    now = time.time()
                    if (now - last_fire) >= 1.5:
                        last_fire = now
                        self.log("[Hotkey Ctrl+Shift+M] Triggering Full Map Load...", "info")
                        self.run_action("full_map_load", {})
        except Exception:
            pass
        finally:
            self._hotkey_thread_id = None
            if registered and user32 is not None:
                try:
                    user32.UnregisterHotKey(None, HOTKEY_ID)
                except Exception:
                    pass

    def _hospital_config_path(self) -> str:
        if multi_client_bot is not None and getattr(multi_client_bot, "CONFIG_PATH", None):
            return str(multi_client_bot.CONFIG_PATH)
        return os.path.join(DATA_DIR, "bot config.json")

    def _is_manual_bot_busy_locked(self) -> bool:
        return (
            "bot_cycle" in self._active_actions
            or any(k.startswith("single_task:") for k in self._active_actions)
        )

    def _recompute_always_on_state_locked(self, now_ts: float | None = None) -> None:
        now = time.time() if now_ts is None else float(now_ts)
        master_on = bool(self._always_on_daemon_enabled)
        ah_on = bool(self._alliance_help_watcher_enabled)
        hh_on = bool(self._hospital_watcher_enabled)
        at_on = bool(self._alliance_tech_watcher_enabled)

        self._alliance_help_stats["enabled"] = ah_on
        self._alliance_help_stats["interval_seconds"] = int(round(self._alliance_help_interval_sec))
        self._alliance_tech_stats["enabled"] = at_on
        self._alliance_tech_stats["interval_seconds"] = int(round(self._alliance_tech_interval_sec))

        if not master_on:
            self._always_on_daemon_state = "paused"
            self._alliance_help_watcher_state = "paused"
            self._hospital_watcher_state = "paused" if hh_on else "off"
            self._alliance_tech_watcher_state = "paused"
            return

        if not ah_on:
            self._alliance_help_watcher_state = "paused"
        else:
            last_ah = float(self._alliance_help_stats.get("last_action_at") or 0.0)
            self._alliance_help_watcher_state = "active" if (last_ah > 0 and (now - last_ah) < 35.0) else "watching"

        if not hh_on:
            self._hospital_watcher_state = "off"
        elif self._hospital_watcher_state != "healing":
            self._hospital_watcher_state = "dormant"

        if not at_on:
            self._alliance_tech_watcher_state = "paused"
        else:
            last_at = float(self._alliance_tech_stats.get("last_action_at") or 0.0)
            self._alliance_tech_watcher_state = "active" if (last_at > 0 and (now - last_at) < 45.0) else "watching"

        if not (ah_on or hh_on or at_on):
            self._always_on_daemon_state = "idle"
        elif hh_on and self._hospital_watcher_state == "healing":
            self._always_on_daemon_state = "healing"
        elif self._alliance_help_watcher_state == "active" or self._alliance_tech_watcher_state == "active":
            self._always_on_daemon_state = "active"
        else:
            self._always_on_daemon_state = "watching"

    def _build_always_on_snapshot_locked(self) -> dict[str, Any]:
        return {
            "enabled": self._always_on_daemon_enabled,
            "state": self._always_on_daemon_state,
            "auto_help_enabled": self._alliance_help_watcher_enabled,
            "auto_help_state": self._alliance_help_watcher_state,
            "hospital_enabled": self._hospital_watcher_enabled,
            "hospital_state": self._hospital_watcher_state,
            "alliance_tech_enabled": self._alliance_tech_watcher_enabled,
            "alliance_tech_state": self._alliance_tech_watcher_state,
            "counters": {
                "allies_helped": int(self._alliance_help_stats.get("total_allies_helped", 0)),
                "help_requests": int(self._alliance_help_stats.get("total_help_requests_sent", 0)),
                "tab1_gifts": int(self._alliance_help_stats.get("total_chests_tab1", 0)),
                "tab2_chests": int(self._alliance_help_stats.get("total_chests_tab2", 0)),
                "total_chests": int(self._alliance_help_stats.get("total_chests_claimed", 0)),
                "hospital_wounded": int(self._hospital_watcher_last_summary.get("wounded_total", 0)),
                "hospital_in_treatment": int(self._hospital_watcher_last_summary.get("in_treatment_total", 0)),
                "hospital_queued": int(self._hospital_watcher_last_summary.get("queued_troops", 0)),
                "tech_donations": int(self._alliance_tech_stats.get("total_tech_donations", 0)),
                "last_tech_id": int(self._alliance_tech_stats.get("last_tech_id", 0)),
            },
            "intervals": {
                "auto_help_sec": int(round(self._alliance_help_interval_sec)),
                "hospital_active_sec": 5,
                "hospital_dormant_sec": 10,
                "alliance_tech_sec": int(round(self._alliance_tech_interval_sec)),
            },
        }

    def _always_on_toggle_response_locked(self) -> dict[str, Any]:
        return {
            "ok": True,
            "always_on_daemon_enabled": self._always_on_daemon_enabled,
            "always_on_daemon_state": self._always_on_daemon_state,
            "always_on_daemon": self._build_always_on_snapshot_locked(),
            "hospital_watcher_enabled": self._hospital_watcher_enabled,
            "hospital_watcher_state": self._hospital_watcher_state,
            "hospital_watcher_summary": dict(self._hospital_watcher_last_summary),
            "target": self._hospital_watcher_target,
            "alliance_help_watcher_enabled": self._alliance_help_watcher_enabled,
            "alliance_help_watcher_state": self._alliance_help_watcher_state,
            "alliance_help_stats": dict(self._alliance_help_stats),
            "alliance_tech_watcher_enabled": self._alliance_tech_watcher_enabled,
            "alliance_tech_watcher_state": self._alliance_tech_watcher_state,
            "alliance_tech_stats": dict(self._alliance_tech_stats),
        }

    def _load_always_on_daemon_config(self) -> None:
        try:
            cfg_path = self._hospital_config_path()
            cfg = _safe_load_json_file(cfg_path, default={})
            if not isinstance(cfg, dict):
                cfg = {}
            main_def = ((cfg.get("client_defaults") or {}).get("main") or {})

            # 1) Master Always-On Daemon
            aod_top = cfg.get("always_on_daemon")
            master_val = aod_top.get("enabled") if isinstance(aod_top, dict) and "enabled" in aod_top else None
            master_enabled = bool(master_val) if master_val is not None else True

            # 2) Auto-Help Alliance & Both Gift Tabs (default ON)
            ah_top = cfg.get("auto_help")
            ah_val = None
            ah_interval = 15.0
            if isinstance(ah_top, dict):
                if "always_on" in ah_top:
                    ah_val = ah_top.get("always_on")
                raw_int = ah_top.get("interval_seconds", ah_top.get("interval_sec"))
                if raw_int is not None:
                    try:
                        ah_interval = float(raw_int)
                    except Exception:
                        ah_interval = 15.0
            if ah_val is None:
                ah_main = main_def.get("auto_help")
                if isinstance(ah_main, dict) and "always_on" in ah_main:
                    ah_val = ah_main.get("always_on")
            ah_enabled = bool(ah_val) if ah_val is not None else True
            ah_interval = max(5.0, min(300.0, ah_interval))

            # 3) Hospital Auto-Heal (default OFF unless explicitly enabled)
            hh_top = cfg.get("hospital_heal")
            hh_val = None
            if isinstance(hh_top, dict) and "persistent_watcher_enabled" in hh_top:
                hh_val = hh_top.get("persistent_watcher_enabled")
            if hh_val is None:
                hh_main = main_def.get("hospital_heal")
                if isinstance(hh_main, dict) and "persistent_watcher_enabled" in hh_main:
                    hh_val = hh_main.get("persistent_watcher_enabled")
            hh_enabled = bool(hh_val) if hh_val is not None else False

            # 4) Alliance Tech Auto-Donate (default ON)
            ad_top = cfg.get("alliance_daily")
            at_val = None
            at_interval = 45.0
            if isinstance(ad_top, dict):
                if "auto_tech_always_on" in ad_top:
                    at_val = ad_top.get("auto_tech_always_on")
                raw_at_int = ad_top.get("auto_tech_interval_seconds")
                if raw_at_int is not None:
                    try:
                        at_interval = float(raw_at_int)
                    except Exception:
                        at_interval = 45.0
            if at_val is None:
                ad_main = main_def.get("alliance_daily")
                if isinstance(ad_main, dict) and "auto_tech_always_on" in ad_main:
                    at_val = ad_main.get("auto_tech_always_on")
            at_enabled = bool(at_val) if at_val is not None else True
            at_interval = max(15.0, min(600.0, at_interval))

            with self._lock:
                self._always_on_daemon_enabled = master_enabled
                self._alliance_help_watcher_enabled = ah_enabled
                self._alliance_help_interval_sec = ah_interval
                self._hospital_watcher_enabled = hh_enabled
                self._hospital_watcher_state = "dormant" if hh_enabled else "off"
                self._alliance_tech_watcher_enabled = at_enabled
                self._alliance_tech_interval_sec = at_interval
                self._recompute_always_on_state_locked()

            if (master_val is None or ah_val is None or at_val is None) and os.path.isfile(cfg_path):
                self._persist_always_on_config()
        except Exception:
            with self._lock:
                self._always_on_daemon_enabled = True
                self._alliance_help_watcher_enabled = True
                self._alliance_help_interval_sec = 15.0
                self._hospital_watcher_enabled = False
                self._alliance_tech_watcher_enabled = True
                self._alliance_tech_interval_sec = 45.0
                self._recompute_always_on_state_locked()

    def _persist_always_on_config(self) -> None:
        try:
            with self._lock:
                cfg_path = self._hospital_config_path()
                cfg: dict[str, Any] = {}
                if multi_client_bot is not None:
                    try:
                        loaded = multi_client_bot.load_config()
                        if isinstance(loaded, dict):
                            cfg = loaded
                    except Exception:
                        cfg = {}
                if not cfg:
                    loaded_raw = _safe_load_json_file(cfg_path, default={})
                    if isinstance(loaded_raw, dict):
                        cfg = loaded_raw

                master_on = bool(self._always_on_daemon_enabled)
                ah_on = bool(self._alliance_help_watcher_enabled)
                ah_int = int(round(self._alliance_help_interval_sec))
                hh_on = bool(self._hospital_watcher_enabled)
                at_on = bool(self._alliance_tech_watcher_enabled)
                at_int = int(round(self._alliance_tech_interval_sec))

                aod_top = cfg.setdefault("always_on_daemon", {})
                if isinstance(aod_top, dict):
                    aod_top["enabled"] = master_on

                ah_top = cfg.setdefault("auto_help", {})
                if isinstance(ah_top, dict):
                    ah_top["always_on"] = ah_on
                    ah_top.setdefault("interval_seconds", ah_int)
                    ah_top.setdefault("claim_both_gift_tabs", True)

                hh_top = cfg.setdefault("hospital_heal", {})
                if isinstance(hh_top, dict):
                    hh_top["persistent_watcher_enabled"] = hh_on

                ad_top = cfg.setdefault("alliance_daily", {})
                if isinstance(ad_top, dict):
                    ad_top["auto_tech_always_on"] = at_on
                    ad_top.setdefault("auto_tech_interval_seconds", at_int)

                defs = cfg.setdefault("client_defaults", {})
                if isinstance(defs, dict):
                    for role_key in ("main", "farm"):
                        rc = defs.setdefault(role_key, {})
                        if not isinstance(rc, dict):
                            continue
                        ah_role = rc.setdefault("auto_help", {})
                        if isinstance(ah_role, dict):
                            ah_role["always_on"] = ah_on
                            ah_role.setdefault("interval_seconds", ah_int)
                            ah_role.setdefault("claim_both_gift_tabs", True)
                        hh_role = rc.setdefault("hospital_heal", {})
                        if isinstance(hh_role, dict):
                            hh_role["persistent_watcher_enabled"] = hh_on
                        ad_role = rc.setdefault("alliance_daily", {})
                        if isinstance(ad_role, dict):
                            ad_role["auto_tech_always_on"] = at_on
                            ad_role.setdefault("auto_tech_interval_seconds", at_int)

                if multi_client_bot is not None and hasattr(multi_client_bot, "save_config"):
                    multi_client_bot.save_config(cfg)
                else:
                    _atomic_write_json(cfg_path, cfg)
                if multi_client_bot is not None:
                    cfg_cache = getattr(multi_client_bot, "_CONFIG_CACHE", None)
                    cfg_lock = getattr(multi_client_bot, "_CONFIG_LOCK", None)
                    if isinstance(cfg_cache, dict):
                        if cfg_lock is not None:
                            with cfg_lock:
                                cfg_cache.clear()
                        else:
                            cfg_cache.clear()
                self._config_snapshot_cache = None
        except Exception as exc:
            self.log(f"[Always-On Daemon] Failed to persist toggle state: {exc}", "warn")

    def _start_always_on_daemon(self) -> None:
        with self._lock:
            if self._always_on_thread_started:
                return
            self._always_on_thread_started = True
            self._hospital_watcher_thread_started = True
            self._alliance_help_thread_started = True
        threading.Thread(
            target=self._always_on_daemon_loop,
            daemon=True,
            name="AlwaysOnWatcherDaemon",
        ).start()

    def _start_hospital_watcher(self) -> None:
        self._start_always_on_daemon()

    def _start_alliance_help_watcher(self) -> None:
        self._start_always_on_daemon()

    def toggle_always_on_daemon(self, enabled: bool | None = None) -> dict[str, Any]:
        with self._lock:
            new_enabled = (not self._always_on_daemon_enabled) if enabled is None else bool(enabled)
            self._always_on_daemon_enabled = new_enabled
            self._always_on_gen += 1
            if new_enabled:
                if self._alliance_help_watcher_enabled:
                    self._always_on_due_reset.add("auto_help")
                if self._hospital_watcher_enabled:
                    self._always_on_due_reset.add("hospital_heal")
                    self._hospital_watcher_reset_flag = True
                if self._alliance_tech_watcher_enabled:
                    self._always_on_due_reset.add("alliance_tech")
            self._recompute_always_on_state_locked()
            resp = self._always_on_toggle_response_locked()
        self._persist_always_on_config()
        if new_enabled:
            active_subs = [
                lbl for lbl, on in (
                    ("Auto-Help & Gifts", self._alliance_help_watcher_enabled),
                    ("Hospital Auto-Heal", self._hospital_watcher_enabled),
                    ("Alliance Tech", self._alliance_tech_watcher_enabled),
                ) if on
            ]
            sub_str = ", ".join(active_subs) if active_subs else "none selected yet"
            self.log(f"[Always-On Daemon] Master watcher turned ON ({sub_str}).", "ok")
        else:
            self.log("[Always-On Daemon] Master watcher PAUSED (all background watchers suspended).", "info")
        self._always_on_wake.set()
        return resp

    def toggle_hospital_watcher(
        self,
        target: str | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            new_enabled = (not self._hospital_watcher_enabled) if enabled is None else bool(enabled)
            self._hospital_watcher_enabled = new_enabled
            if target is not None and str(target).strip():
                self._hospital_watcher_target = str(target).strip()
            self._hospital_watcher_gen += 1
            self._always_on_gen += 1
            self._hospital_watcher_reset_flag = True
            if new_enabled:
                self._always_on_due_reset.add("hospital_heal")
            else:
                self._hospital_watcher_state = "off"
                self._hospital_watcher_last_summary = {
                    "wounded_total": 0,
                    "in_treatment_total": 0,
                    "untreated_total": 0,
                    "queued_troops": 0,
                    "batches_chained": 0,
                    "cross_client_helps_triggered": 0,
                    "updated_at": time.time(),
                }
            self._recompute_always_on_state_locked()
            resp = self._always_on_toggle_response_locked()
        self._persist_always_on_config()
        if new_enabled:
            suffix = "" if self._always_on_daemon_enabled else " (Master Always-On switch is currently paused)"
            self.log(
                f"[Always-On Daemon] Hospital Auto-Heal turned ON: auto-heals wounded in alliance-help batches and stays dormant when 0 wounded{suffix}.",
                "ok",
            )
        else:
            self.log("[Always-On Daemon] Hospital Auto-Heal turned OFF.", "info")
        self._always_on_wake.set()
        return resp

    def toggle_alliance_help_watcher(self, enabled: bool | None = None) -> dict[str, Any]:
        with self._lock:
            new_enabled = (not self._alliance_help_watcher_enabled) if enabled is None else bool(enabled)
            self._alliance_help_watcher_enabled = new_enabled
            self._alliance_help_gen += 1
            self._always_on_gen += 1
            self._alliance_help_stats["enabled"] = new_enabled
            self._alliance_help_stats["updated_at"] = time.time()
            if new_enabled:
                self._always_on_due_reset.add("auto_help")
            self._recompute_always_on_state_locked()
            resp = self._always_on_toggle_response_locked()
        self._persist_always_on_config()
        if new_enabled:
            suffix = "" if self._always_on_daemon_enabled else " (Master Always-On switch is currently paused)"
            self.log(
                f"[Always-On Daemon] Auto-Help & Both Gift Tabs turned ON (every {int(self._alliance_help_interval_sec)}s across all running clients){suffix}.",
                "ok",
            )
        else:
            self.log("[Always-On Daemon] Auto-Help & Both Gift Tabs PAUSED.", "info")
        self._always_on_wake.set()
        return resp

    def toggle_alliance_tech_watcher(self, enabled: bool | None = None) -> dict[str, Any]:
        with self._lock:
            new_enabled = (not self._alliance_tech_watcher_enabled) if enabled is None else bool(enabled)
            self._alliance_tech_watcher_enabled = new_enabled
            self._always_on_gen += 1
            self._alliance_tech_stats["enabled"] = new_enabled
            self._alliance_tech_stats["updated_at"] = time.time()
            if new_enabled:
                self._always_on_due_reset.add("alliance_tech")
            self._recompute_always_on_state_locked()
            resp = self._always_on_toggle_response_locked()
        self._persist_always_on_config()
        if new_enabled:
            suffix = "" if self._always_on_daemon_enabled else " (Master Always-On switch is currently paused)"
            self.log(
                f"[Always-On Daemon] Alliance Tech Auto-Donate turned ON (every {int(self._alliance_tech_interval_sec)}s across all running clients){suffix}.",
                "ok",
            )
        else:
            self.log("[Always-On Daemon] Alliance Tech Auto-Donate PAUSED.", "info")
        self._always_on_wake.set()
        return resp

    def _resolve_hospital_watcher_clients(self, running: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not running:
            return []
        with self._lock:
            tgt = str(self._hospital_watcher_target or "all").strip()
            sel_pid = self.selected_client_pid
            sel_lbl = self.selected_client_label
        tgt_low = tgt.lower()
        if tgt_low in ("", "all", "auto", "all running"):
            return list(running)
        if tgt_low in ("farms", "farms only"):
            return [c for c in running if str(c.get("role") or "").lower() != "main"]
        if tgt_low in ("main", "main only"):
            mains = [c for c in running if str(c.get("role") or "").lower() == "main"]
            return mains if mains else [c for c in running if str(c.get("label") or "").lower() == "main"]
        if tgt_low == "selected client":
            if sel_pid is not None:
                matched = [c for c in running if int(c.get("pid") or 0) == int(sel_pid)]
                if matched:
                    return matched
            if sel_lbl:
                matched = [c for c in running if str(c.get("label") or "").lower() == sel_lbl.lower()]
                if matched:
                    return matched
            return list(running)
        m_pid = re.search(r"\(PID\s+(\d+)\)\s*$", tgt)
        pid_val = int(m_pid.group(1)) if m_pid else (int(tgt) if tgt.isdigit() else None)
        if pid_val is not None:
            matched = [c for c in running if int(c.get("pid") or 0) == pid_val]
            if matched:
                return matched
        prefix = tgt.split(" (PID ", 1)[0].strip().lower()
        matched = [
            c for c in running
            if str(c.get("label") or "").lower() == prefix
            or self._client_display_name(c).lower() == prefix
        ]
        return matched

    def _run_hospital_watcher_once(self, dry_run: bool | None = None, held_lock: bool = False) -> dict[str, Any]:
        is_dry = self._hospital_watcher_dry_run if dry_run is None else bool(dry_run)
        acquired_lock = False
        if not held_lock:
            with self._lock:
                busy = (
                    self._is_manual_bot_busy_locked()
                    or "always_on_daemon_tick" in self._active_actions
                    or "hospital_watcher_tick" in self._active_actions
                    or "alliance_help_tick" in self._active_actions
                )
                if busy:
                    return {"skipped": True, "reason": "busy"}
                self._active_actions.add("hospital_watcher_tick")
                acquired_lock = True
        try:
            running: list[dict[str, Any]] = []
            if client_discovery is not None:
                try:
                    running = list(client_discovery.find_running_processes() or [])
                except Exception:
                    running = []
            if not running:
                with self._lock:
                    running = list(self.running_clients)
            targets = self._resolve_hospital_watcher_clients(running)
            if not targets:
                with self._lock:
                    self._hospital_watcher_last_summary.update({
                        "wounded_total": 0,
                        "in_treatment_total": 0,
                        "untreated_total": 0,
                        "queued_troops": 0,
                        "batches_chained": 0,
                        "cross_client_helps_triggered": 0,
                        "updated_at": time.time(),
                    })
                return {"skipped": False, "all_dormant": True, "no_clients": True, "results": []}

            cfg_root: dict[str, Any] = {}
            if multi_client_bot is not None:
                try:
                    loaded = multi_client_bot.load_config()
                    if isinstance(loaded, dict):
                        cfg_root = loaded
                except Exception:
                    cfg_root = {}

            results: list[dict[str, Any]] = []
            any_active = False
            tot_wounded = 0
            tot_in_treat = 0
            tot_untreated = 0
            tot_queued = 0
            tot_batches = 0
            tot_cross_helps = 0

            for proc in targets:
                if not self._hospital_watcher_enabled and dry_run is None:
                    break
                c_pid = int(proc.get("pid") or 0)
                if c_pid <= 0:
                    continue
                c_label = str(proc.get("label") or f"PID {c_pid}")
                c_role = str(proc.get("role") or "farm")
                c_disp = self._client_display_name(proc) or c_label
                if multi_client_bot is not None and hasattr(multi_client_bot, "resolve_client_config"):
                    try:
                        c_cfg = multi_client_bot.resolve_client_config(cfg_root, c_label, c_role)
                    except Exception:
                        c_cfg = cfg_root
                else:
                    c_cfg = cfg_root

                res: dict[str, Any] | None = None
                if bot_actions is not None and client_discovery is not None:
                    try:
                        res = bot_actions.run_hospital_heal(
                            client_discovery,
                            c_pid,
                            {},
                            c_cfg,
                            dry_run=is_dry,
                        )
                    except Exception as exc:
                        res = {"ok": False, "task": "hospital_heal", "dormant": False, "error": str(exc)}
                else:
                    extra = ["--cycle", "--tasks", "hospital_heal", "--target", str(c_pid)]
                    if is_dry:
                        extra.append("--dry-run")
                    proc_res = self._run_tool("multi client bot.py", extra, timeout=60)
                    if proc_res.stdout:
                        for raw_ln in proc_res.stdout.splitlines():
                            ln = raw_ln.strip()
                            if ln.startswith('{"ok":'):
                                try:
                                    parsed = json.loads(ln)
                                    c_list = parsed.get("clients") or []
                                    if c_list and isinstance(c_list[0], dict):
                                        res = (c_list[0].get("tasks") or {}).get("hospital_heal")
                                        break
                                except Exception:
                                    pass
                if not isinstance(res, dict):
                    continue
                if not res.get("ok", False):
                    results.append({"pid": c_pid, "label": c_disp, "res": res, "dormant": True})
                    continue

                w = int(res.get("wounded_total") or 0)
                in_t = int(res.get("in_treatment_total") or 0)
                untr = int(res.get("untreated_total") or 0)
                queued = int(res.get("total_queued_troops", res.get("queued_troops", 0)) or 0)
                batches = int(res.get("batches_chained") or 0)
                cross_h = int(res.get("cross_client_helps_triggered") or 0)
                collected = bool(res.get("collected", False))
                c_dormant = bool(res.get("dormant", (w == 0 and in_t == 0 and untr == 0 and not collected and queued == 0)))
                if (not c_dormant) or w > 0 or queued > 0 or collected:
                    any_active = True
                    c_dormant = False

                tot_wounded += w
                tot_in_treat += in_t
                tot_untreated += untr
                tot_queued += queued
                tot_batches += batches
                tot_cross_helps += cross_h
                results.append({"pid": c_pid, "label": c_disp, "res": res, "dormant": c_dormant})

            with self._lock:
                self._hospital_watcher_last_summary = {
                    "wounded_total": tot_wounded,
                    "in_treatment_total": tot_in_treat,
                    "untreated_total": tot_untreated,
                    "queued_troops": tot_queued,
                    "batches_chained": tot_batches,
                    "cross_client_helps_triggered": tot_cross_helps,
                    "updated_at": time.time(),
                }

            return {
                "skipped": False,
                "all_dormant": not any_active,
                "no_clients": False,
                "results": results,
                "totals": dict(self._hospital_watcher_last_summary),
            }
        finally:
            if acquired_lock:
                self._end_action("hospital_watcher_tick")

    @staticmethod
    def _extract_count(val: Any) -> int:
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, (int, float)):
            return max(0, int(val))
        if isinstance(val, (list, tuple, set, dict)):
            return len(val)
        return 0

    def _run_alliance_auto_help_once(self, force_log: bool = False, held_lock: bool = False) -> dict[str, Any]:
        acquired_lock = False
        if not held_lock:
            with self._lock:
                busy = (
                    self._is_manual_bot_busy_locked()
                    or "always_on_daemon_tick" in self._active_actions
                    or "hospital_watcher_tick" in self._active_actions
                    or "alliance_help_tick" in self._active_actions
                )
                if busy:
                    return {"skipped": True, "reason": "busy"}
                self._active_actions.add("alliance_help_tick")
                acquired_lock = True
        try:
            running: list[dict[str, Any]] = []
            if client_discovery is not None:
                try:
                    running = list(client_discovery.find_running_processes() or [])
                except Exception:
                    running = []
            if not running:
                with self._lock:
                    running = list(self.running_clients)

            if not running:
                with self._lock:
                    self._alliance_help_stats["clients_checked"] = 0
                    self._alliance_help_stats["updated_at"] = time.time()
                    if self._alliance_help_watcher_enabled:
                        self._alliance_help_watcher_state = "watching"
                if force_log:
                    self.log("[Auto-Help Daemon] No running Last Z clients detected right now.", "info")
                return {"skipped": False, "had_action": False, "clients_checked": 0}

            cfg_root: dict[str, Any] = {}
            if multi_client_bot is not None:
                try:
                    loaded = multi_client_bot.load_config()
                    if isinstance(loaded, dict):
                        cfg_root = loaded
                except Exception:
                    cfg_root = {}

            tick_helped = 0
            tick_reqs = 0
            tick_tab1 = 0
            tick_tab2 = 0
            tick_chests = 0
            tick_had_action = False
            action_summaries: list[str] = []
            checked_cnt = 0

            for proc in running:
                if (not force_log) and ((not self._always_on_daemon_enabled) or (not self._alliance_help_watcher_enabled)):
                    break
                c_pid = int(proc.get("pid") or 0)
                if c_pid <= 0:
                    continue
                checked_cnt += 1
                c_label = str(proc.get("label") or f"PID {c_pid}")
                c_role = str(proc.get("role") or "farm")
                c_disp = self._client_display_name(proc) or c_label

                if multi_client_bot is not None and hasattr(multi_client_bot, "resolve_client_config"):
                    try:
                        c_cfg = multi_client_bot.resolve_client_config(cfg_root, c_label, c_role)
                    except Exception:
                        c_cfg = dict(cfg_root)
                else:
                    c_cfg = dict(cfg_root)
                if isinstance(c_cfg, dict):
                    ah_cfg = c_cfg.setdefault("auto_help", {})
                    if isinstance(ah_cfg, dict):
                        ah_cfg.setdefault("claim_both_gift_tabs", True)

                res: dict[str, Any] | None = None
                if bot_actions is not None and client_discovery is not None:
                    try:
                        res = bot_actions.run_auto_help(
                            client_discovery,
                            c_pid,
                            {},
                            c_cfg,
                            dry_run=False,
                        )
                    except Exception as exc:
                        res = {"ok": False, "task": "auto_help", "error": str(exc)}
                else:
                    extra = ["--cycle", "--tasks", "auto_help", "--target", str(c_pid)]
                    proc_res = self._run_tool("multi client bot.py", extra, timeout=45)
                    if proc_res.stdout:
                        for raw_ln in proc_res.stdout.splitlines():
                            ln = raw_ln.strip()
                            if ln.startswith('{"ok":'):
                                try:
                                    parsed = json.loads(ln)
                                    c_list = parsed.get("clients") or []
                                    if c_list and isinstance(c_list[0], dict):
                                        res = (c_list[0].get("tasks") or {}).get("auto_help")
                                        break
                                except Exception:
                                    pass

                if not isinstance(res, dict):
                    continue

                helped_n = self._extract_count(res.get("ally_help_num"))
                if res.get("helped_all") and helped_n == 0:
                    helped_n = 1
                reqs_n = self._extract_count(res.get("call_helps"))
                tab1_n = (
                    self._extract_count(res.get("tab1_gifts_claimed"))
                    or self._extract_count(res.get("chests_tab1"))
                    or self._extract_count(res.get("tab1_claimed"))
                    or self._extract_count(res.get("normal_gifts_claimed"))
                    or self._extract_count(res.get("normal_chests_claimed"))
                )
                tab2_n = (
                    self._extract_count(res.get("tab2_chests_claimed"))
                    or self._extract_count(res.get("chests_tab2"))
                    or self._extract_count(res.get("tab2_claimed"))
                    or self._extract_count(res.get("rare_chests_claimed"))
                    or self._extract_count(res.get("rare_gifts_claimed"))
                    or self._extract_count(res.get("alliance_chests_claimed"))
                )
                gifts_n = (
                    self._extract_count(res.get("gifts_claimed"))
                    or self._extract_count(res.get("total_chests_claimed"))
                    or self._extract_count(res.get("chests_claimed"))
                )
                chests_n = max(gifts_n, tab1_n + tab2_n)

                tips = _filter_in_game_tips(res.get("in_game_tips") or res.get("tips") or [])
                modals = [str(m).strip() for m in _as_list(res.get("popped_modals") or res.get("modals")) if str(m).strip()]
                errs: list[str] = []
                for ek in ("send_errors", "errors"):
                    ev = res.get(ek)
                    if isinstance(ev, (list, tuple, dict)):
                        errs.extend(str(x).strip() for x in _as_list(ev) if str(x).strip())
                if not res.get("ok", True) and res.get("error"):
                    errs.append(str(res.get("error")).strip())

                client_did_work = helped_n > 0 or reqs_n > 0 or chests_n > 0
                if client_did_work:
                    tick_had_action = True
                    tick_helped += helped_n
                    tick_reqs += reqs_n
                    tick_tab1 += tab1_n
                    tick_tab2 += tab2_n
                    tick_chests += chests_n

                    bits: list[str] = []
                    if helped_n > 0:
                        bits.append(f"helped {helped_n} ally/allies")
                    if reqs_n > 0:
                        bits.append(f"requested help for {reqs_n} queue(s)")
                    if chests_n > 0:
                        if tab1_n > 0 or tab2_n > 0:
                            bits.append(f"claimed {chests_n} alliance chest(s) (Tab 1: {tab1_n}, Tab 2: {tab2_n})")
                        else:
                            bits.append(f"claimed {chests_n} alliance chest(s)")
                    c_summary = ", ".join(bits)
                    action_summaries.append(f"{c_disp}: {c_summary}")
                    self.log(f"[Auto-Help Daemon] [{c_disp}] {c_summary}", "ok")
                    for dl in _as_list(res.get("detail_lines")):
                        ds = str(dl or "").strip()
                        if ds:
                            self.log(f"[DETAIL] [Auto-Help] [{c_disp}] {ds}", "detail", category="DETAIL")

                if client_did_work or errs or tips or modals or force_log:
                    for tip in tips:
                        is_err = "error" in tip.lower()
                        self.log(
                            f"[Auto-Help Daemon] [{c_disp}] In-game tip: {tip}",
                            "err" if is_err else "warn",
                            category="ERR" if is_err else "WARN",
                            is_tip=True,
                        )
                    for mod in modals:
                        self.log(
                            f"[Auto-Help Daemon] [{c_disp}] Popped modal: {mod}",
                            "warn",
                            category="WARN",
                            is_tip=True,
                        )
                    for err_s in errs:
                        self.log(f"[Auto-Help Daemon] [{c_disp}] Send error: {err_s}", "err", category="ERR")

            now_ts = time.time()
            with self._lock:
                st = self._alliance_help_stats
                st["enabled"] = self._alliance_help_watcher_enabled
                st["interval_seconds"] = int(round(self._alliance_help_interval_sec))
                st["cycles_run"] = int(st.get("cycles_run", 0)) + 1
                st["clients_checked"] = checked_cnt
                st["last_allies_helped"] = tick_helped
                st["last_help_requests_sent"] = tick_reqs
                st["last_chests_tab1"] = tick_tab1
                st["last_chests_tab2"] = tick_tab2
                st["last_chests_claimed"] = tick_chests
                st["updated_at"] = now_ts
                if tick_had_action:
                    st["total_allies_helped"] = int(st.get("total_allies_helped", 0)) + tick_helped
                    st["total_help_requests_sent"] = int(st.get("total_help_requests_sent", 0)) + tick_reqs
                    st["total_chests_tab1"] = int(st.get("total_chests_tab1", 0)) + tick_tab1
                    st["total_chests_tab2"] = int(st.get("total_chests_tab2", 0)) + tick_tab2
                    st["total_chests_claimed"] = int(st.get("total_chests_claimed", 0)) + tick_chests
                    st["last_action_summary"] = "; ".join(action_summaries)
                    st["last_action_at"] = now_ts
                self._recompute_always_on_state_locked(now_ts)

            if force_log and not tick_had_action:
                self.log(
                    f"[Always-On Daemon] [Auto-Help] Checked {checked_cnt} client(s): 0 pending helps or alliance chests on either tab.",
                    "info",
                )

            return {
                "skipped": False,
                "had_action": tick_had_action,
                "clients_checked": checked_cnt,
                "helped": tick_helped,
                "tab1": tick_tab1,
                "tab2": tick_tab2,
                "chests": tick_chests,
            }
        finally:
            if acquired_lock:
                self._end_action("alliance_help_tick")

    def _run_alliance_tech_once(self, force_log: bool = False, held_lock: bool = False) -> dict[str, Any]:
        acquired_lock = False
        if not held_lock:
            with self._lock:
                busy = (
                    self._is_manual_bot_busy_locked()
                    or "always_on_daemon_tick" in self._active_actions
                    or "alliance_tech_tick" in self._active_actions
                )
                if busy:
                    return {"skipped": True, "reason": "busy"}
                self._active_actions.add("alliance_tech_tick")
                acquired_lock = True
        try:
            running: list[dict[str, Any]] = []
            if client_discovery is not None:
                try:
                    running = list(client_discovery.find_running_processes() or [])
                except Exception:
                    running = []
            if not running:
                with self._lock:
                    running = list(self.running_clients)

            if not running:
                with self._lock:
                    self._alliance_tech_stats["clients_checked"] = 0
                    self._alliance_tech_stats["updated_at"] = time.time()
                    self._recompute_always_on_state_locked()
                if force_log:
                    self.log("[Always-On Daemon] [Alliance Tech] No running Last Z clients detected right now.", "info")
                return {"skipped": False, "had_action": False, "clients_checked": 0, "tech_donated": 0}

            cfg_root: dict[str, Any] = {}
            if multi_client_bot is not None:
                try:
                    loaded = multi_client_bot.load_config()
                    if isinstance(loaded, dict):
                        cfg_root = loaded
                except Exception:
                    cfg_root = {}

            tick_donated = 0
            tick_last_tech_id = 0
            tick_had_action = False
            action_summaries: list[str] = []
            checked_cnt = 0

            run_daily_fn = getattr(bot_actions, "run_alliance_daily", None) if bot_actions is not None else None
            supports_tech_only_kw = False
            if callable(run_daily_fn):
                try:
                    supports_tech_only_kw = "tech_only" in inspect.signature(run_daily_fn).parameters
                except Exception:
                    supports_tech_only_kw = False

            for proc in running:
                if (not force_log) and ((not self._always_on_daemon_enabled) or (not self._alliance_tech_watcher_enabled)):
                    break
                c_pid = int(proc.get("pid") or 0)
                if c_pid <= 0:
                    continue
                checked_cnt += 1
                c_label = str(proc.get("label") or f"PID {c_pid}")
                c_role = str(proc.get("role") or "farm")
                c_disp = self._client_display_name(proc) or c_label

                if multi_client_bot is not None and hasattr(multi_client_bot, "resolve_client_config"):
                    try:
                        c_cfg = multi_client_bot.resolve_client_config(cfg_root, c_label, c_role)
                    except Exception:
                        c_cfg = dict(cfg_root)
                else:
                    c_cfg = dict(cfg_root)

                tech_cfg = dict(c_cfg) if isinstance(c_cfg, dict) else {}
                ad_cfg = dict(tech_cfg.get("alliance_daily") or {})
                ad_cfg.update({
                    "donate_tech": True,
                    "tech_only": True,
                    "claim_gifts": False,
                    "claim_red_packets": False,
                    "claim_tasks": False,
                    "help_allies": False,
                })
                tech_cfg["alliance_daily"] = ad_cfg

                res: dict[str, Any] | None = None
                if callable(run_daily_fn) and client_discovery is not None:
                    try:
                        if supports_tech_only_kw:
                            res = run_daily_fn(
                                client_discovery,
                                c_pid,
                                {},
                                tech_cfg,
                                dry_run=False,
                                tech_only=True,
                            )
                        else:
                            res = run_daily_fn(
                                client_discovery,
                                c_pid,
                                {},
                                tech_cfg,
                                dry_run=False,
                            )
                    except Exception as exc:
                        res = {"ok": False, "task": "alliance_daily", "error": str(exc)}
                else:
                    extra = ["--cycle", "--tasks", "alliance_daily", "--target", str(c_pid)]
                    proc_res = self._run_tool("multi client bot.py", extra, timeout=45)
                    if proc_res.stdout:
                        for raw_ln in proc_res.stdout.splitlines():
                            ln = raw_ln.strip()
                            if ln.startswith('{"ok":'):
                                try:
                                    parsed = json.loads(ln)
                                    c_list = parsed.get("clients") or []
                                    if c_list and isinstance(c_list[0], dict):
                                        res = (c_list[0].get("tasks") or {}).get("alliance_daily")
                                        break
                                except Exception:
                                    pass

                if not isinstance(res, dict):
                    continue

                donated_n = self._extract_count(res.get("tech_donated"))
                tech_id = int(res.get("tech_id") or 0)
                tips = _filter_in_game_tips(res.get("in_game_tips") or res.get("tips") or [])
                modals = [str(m).strip() for m in _as_list(res.get("popped_modals") or res.get("modals")) if str(m).strip()]
                errs: list[str] = []
                for ek in ("send_errors", "errors"):
                    ev = res.get(ek)
                    if isinstance(ev, (list, tuple, dict)):
                        errs.extend(str(x).strip() for x in _as_list(ev) if str(x).strip())
                if not res.get("ok", True) and res.get("error"):
                    errs.append(str(res.get("error")).strip())

                if donated_n > 0:
                    tick_had_action = True
                    tick_donated += donated_n
                    if tech_id > 0:
                        tick_last_tech_id = tech_id
                    c_summary = f"donated x{donated_n} to Alliance Tech" + (f" #{tech_id}" if tech_id > 0 else "")
                    action_summaries.append(f"{c_disp}: {c_summary}")
                    self.log(f"[Always-On Daemon] [Alliance Tech] [{c_disp}] {c_summary}", "ok")
                    for dl in _as_list(res.get("detail_lines")):
                        ds = str(dl or "").strip()
                        if ds:
                            self.log(f"[DETAIL] [Alliance Tech] [{c_disp}] {ds}", "detail", category="DETAIL")

                if donated_n > 0 or errs or tips or modals or force_log:
                    for tip in tips:
                        is_err = "error" in tip.lower()
                        self.log(
                            f"[Always-On Daemon] [Alliance Tech] [{c_disp}] In-game tip: {tip}",
                            "err" if is_err else "warn",
                            category="ERR" if is_err else "WARN",
                            is_tip=True,
                        )
                    for mod in modals:
                        self.log(
                            f"[Always-On Daemon] [Alliance Tech] [{c_disp}] Popped modal: {mod}",
                            "warn",
                            category="WARN",
                            is_tip=True,
                        )
                    for err_s in errs:
                        self.log(f"[Always-On Daemon] [Alliance Tech] [{c_disp}] Send error: {err_s}", "err", category="ERR")

            now_ts = time.time()
            with self._lock:
                st = self._alliance_tech_stats
                st["enabled"] = self._alliance_tech_watcher_enabled
                st["interval_seconds"] = int(round(self._alliance_tech_interval_sec))
                st["cycles_run"] = int(st.get("cycles_run", 0)) + 1
                st["clients_checked"] = checked_cnt
                st["last_tech_donations"] = tick_donated
                if tick_last_tech_id > 0:
                    st["last_tech_id"] = tick_last_tech_id
                st["updated_at"] = now_ts
                if tick_had_action:
                    st["total_tech_donations"] = int(st.get("total_tech_donations", 0)) + tick_donated
                    st["last_action_summary"] = "; ".join(action_summaries)
                    st["last_action_at"] = now_ts
                self._recompute_always_on_state_locked(now_ts)

            if force_log and not tick_had_action:
                self.log(
                    f"[Always-On Daemon] [Alliance Tech] Checked {checked_cnt} client(s): 0 pending tech donations available.",
                    "info",
                )

            return {
                "skipped": False,
                "had_action": tick_had_action,
                "clients_checked": checked_cnt,
                "tech_donated": tick_donated,
                "tech_id": tick_last_tech_id,
            }
        finally:
            if acquired_lock:
                self._end_action("alliance_tech_tick")

    def _run_always_on_sweep_now(self) -> dict[str, Any]:
        with self._lock:
            run_help = bool(self._alliance_help_watcher_enabled)
            run_hosp = bool(self._hospital_watcher_enabled)
            run_tech = bool(self._alliance_tech_watcher_enabled)
            if not (run_help or run_hosp or run_tech):
                self.log("[Always-On Daemon] All 3 sub-toggles are OFF - enable at least one to sweep.", "warn")
                return {"ok": True, "skipped": True, "reason": "none_enabled"}
            if self._is_manual_bot_busy_locked() or "always_on_daemon_tick" in self._active_actions:
                if run_help:
                    self._always_on_due_reset.add("auto_help")
                if run_hosp:
                    self._always_on_due_reset.add("hospital_heal")
                if run_tech:
                    self._always_on_due_reset.add("alliance_tech")
                self._always_on_wake.set()
                self.log("[Always-On Daemon] Busy with another task - queued immediate sweep.", "warn")
                return {"ok": True, "skipped": True, "reason": "busy"}
            self._active_actions.add("always_on_daemon_tick")

        enabled_names = [
            nm for nm, on in (
                ("Auto-Help & Gifts", run_help),
                ("Hospital Auto-Heal", run_hosp),
                ("Alliance Tech", run_tech),
            ) if on
        ]
        self.log(f"[Always-On Daemon] Running immediate sequential sweep ({', '.join(enabled_names)})...", "info")
        out: dict[str, Any] = {"ok": True}
        try:
            if run_help:
                out["auto_help"] = self._run_alliance_auto_help_once(force_log=True, held_lock=True)
            if run_hosp:
                tick_h = self._run_hospital_watcher_once(held_lock=True)
                out["hospital_heal"] = tick_h
                with self._lock:
                    if not tick_h.get("skipped"):
                        self._hospital_watcher_state = "dormant" if tick_h.get("all_dormant", True) else "healing"
                        self._recompute_always_on_state_locked()
                if tick_h.get("all_dormant", True):
                    self.log("[Always-On Daemon] [Hospital] Checked clients: 0 wounded troops (dormant).", "info")
                else:
                    totals = tick_h.get("totals") or {}
                    self.log(
                        f"[Always-On Daemon] [Hospital] Active batch healing: wounded={totals.get('wounded_total', 0)}, queued={totals.get('queued_troops', 0)}, in_treatment={totals.get('in_treatment_total', 0)}.",
                        "ok",
                    )
            if run_tech:
                out["alliance_tech"] = self._run_alliance_tech_once(force_log=True, held_lock=True)
        finally:
            self._end_action("always_on_daemon_tick")
            with self._lock:
                self._recompute_always_on_state_locked()
        return out

    def _always_on_daemon_loop(self) -> None:
        # Short settle wait at startup so client discovery finishes cleanly
        self._always_on_wake.wait(3.5)
        self._always_on_wake.clear()

        next_help_ts = 0.0
        next_hosp_ts = 0.0
        next_tech_ts = 0.0

        prev_hosp_mode: str | None = None
        last_hosp_sig: dict[int, tuple[Any, ...]] = {}
        last_hosp_ts: dict[int, float] = {}

        while self.is_monitoring:
            try:
                with self._lock:
                    gen_before = self._always_on_gen
                    master_on = self._always_on_daemon_enabled
                    ah_on = self._alliance_help_watcher_enabled
                    hh_on = self._hospital_watcher_enabled
                    at_on = self._alliance_tech_watcher_enabled
                    ah_interval = self._alliance_help_interval_sec
                    at_interval = self._alliance_tech_interval_sec

                    if self._hospital_watcher_reset_flag:
                        self._hospital_watcher_reset_flag = False
                        prev_hosp_mode = None
                        last_hosp_sig.clear()
                        last_hosp_ts.clear()

                    due_resets = set(self._always_on_due_reset)
                    self._always_on_due_reset.clear()

                if "auto_help" in due_resets:
                    next_help_ts = 0.0
                if "hospital_heal" in due_resets:
                    next_hosp_ts = 0.0
                if "alliance_tech" in due_resets:
                    next_tech_ts = 0.0

                if (not master_on) or (not (ah_on or hh_on or at_on)):
                    if not hh_on and prev_hosp_mode is not None:
                        prev_hosp_mode = None
                        last_hosp_sig.clear()
                        last_hosp_ts.clear()
                    with self._lock:
                        self._recompute_always_on_state_locked()
                    if self._always_on_gen == gen_before:
                        self._always_on_wake.wait(1.0)
                        self._always_on_wake.clear()
                    continue

                now = time.time()
                due_hosp = hh_on and now >= next_hosp_ts
                due_help = ah_on and now >= next_help_ts
                due_tech = at_on and now >= next_tech_ts

                if not (due_hosp or due_help or due_tech):
                    with self._lock:
                        self._recompute_always_on_state_locked(now)
                    soonest_list: list[float] = []
                    if hh_on:
                        soonest_list.append(next_hosp_ts)
                    if ah_on:
                        soonest_list.append(next_help_ts)
                    if at_on:
                        soonest_list.append(next_tech_ts)
                    soonest = min(soonest_list) if soonest_list else (now + 2.0)
                    wait_s = max(0.5, min(5.0, soonest - now))
                    if self._always_on_gen == gen_before:
                        self._always_on_wake.wait(wait_s)
                        self._always_on_wake.clear()
                    continue

                with self._lock:
                    if (
                        self._is_manual_bot_busy_locked()
                        or "always_on_daemon_tick" in self._active_actions
                        or "hospital_watcher_tick" in self._active_actions
                        or "alliance_help_tick" in self._active_actions
                        or "alliance_tech_tick" in self._active_actions
                    ):
                        is_busy = True
                    else:
                        self._active_actions.add("always_on_daemon_tick")
                        is_busy = False

                if is_busy:
                    if self._always_on_gen == gen_before:
                        self._always_on_wake.wait(2.0)
                        self._always_on_wake.clear()
                    continue

                try:
                    # 1) Hospital Auto-Heal (sequential inside single daemon lock)
                    if due_hosp and self._always_on_daemon_enabled and self._hospital_watcher_enabled:
                        with self._lock:
                            abort_manual = self._is_manual_bot_busy_locked()
                        if not abort_manual:
                            tick_h = self._run_hospital_watcher_once(held_lock=True)
                            if self._always_on_daemon_enabled and self._hospital_watcher_enabled and not tick_h.get("skipped"):
                                if tick_h.get("all_dormant", True):
                                    with self._lock:
                                        self._hospital_watcher_state = "dormant"
                                        self._recompute_always_on_state_locked()
                                    if prev_hosp_mode != "dormant":
                                        prev_hosp_mode = "dormant"
                                        last_hosp_sig.clear()
                                        last_hosp_ts.clear()
                                        self.log(
                                            "[Always-On Daemon] [Hospital] No injured troops detected (0 wounded) - staying dormant and watching...",
                                            "info",
                                        )
                                    next_hosp_ts = time.time() + 10.0
                                else:
                                    if prev_hosp_mode == "dormant":
                                        self.log(
                                            "[Always-On Daemon] [Hospital] Detected injured troops! Waking from dormant state and starting batch healing...",
                                            "info",
                                        )
                                    with self._lock:
                                        self._hospital_watcher_state = "healing"
                                        self._recompute_always_on_state_locked()
                                    prev_hosp_mode = "healing"

                                    log_now = time.time()
                                    for entry in tick_h.get("results") or []:
                                        if entry.get("dormant"):
                                            continue
                                        r = entry.get("res") or {}
                                        c_lbl = str(entry.get("label") or f"PID {entry.get('pid')}")
                                        c_pid = int(entry.get("pid") or 0)
                                        queued = int(r.get("total_queued_troops", r.get("queued_troops", 0)) or 0)
                                        in_treat = int(r.get("in_treatment_total") or 0)
                                        untreated = int(r.get("untreated_total") or 0)
                                        rem_sec = int(r.get("queue_remaining_sec") or 0)
                                        batches = int(r.get("batches_chained") or 0)
                                        cross_h = int(r.get("cross_client_helps_triggered") or 0)
                                        collected = bool(r.get("collected", False))
                                        help_req = bool(r.get("help_requested") or r.get("is_helped"))
                                        action_str = str(r.get("action") or "healing")
                                        sig = (action_str, queued, in_treat, untreated, help_req, collected)
                                        should_log = (
                                            queued > 0
                                            or collected
                                            or batches > 0
                                            or cross_h > 0
                                            or sig != last_hosp_sig.get(c_pid)
                                            or (log_now - last_hosp_ts.get(c_pid, 0.0)) >= 20.0
                                        )
                                        if should_log:
                                            extra_bits: list[str] = []
                                            if batches > 0:
                                                extra_bits.append(f"batches={batches}")
                                            if cross_h > 0:
                                                extra_bits.append(f"cross_helps={cross_h}")
                                            if rem_sec > 0:
                                                extra_bits.append(f"remaining={rem_sec}s")
                                            extra_txt = f" ({', '.join(extra_bits)})" if extra_bits else ""
                                            self.log(
                                                f"[Always-On Daemon] [Hospital] [{c_lbl}] {action_str}: queued_troops={queued}, in_treatment_total={in_treat}, untreated_total={untreated}, alliance_help={'requested' if help_req else 'pending'}{extra_txt}",
                                                "ok" if (queued > 0 or collected) else "info",
                                            )
                                            for tip in _filter_in_game_tips(r.get("in_game_tips") or r.get("tips") or []):
                                                self.log(f"[Always-On Daemon] [Hospital] [{c_lbl}] In-game tip: {tip}", "info")
                                            last_hosp_sig[c_pid] = sig
                                            last_hosp_ts[c_pid] = log_now
                                    next_hosp_ts = time.time() + 5.0

                    # 2) Auto-Help Alliance & Both Gift Tabs
                    if due_help and self._always_on_daemon_enabled and self._alliance_help_watcher_enabled:
                        with self._lock:
                            abort_manual = self._is_manual_bot_busy_locked()
                        if not abort_manual:
                            self._run_alliance_auto_help_once(force_log=False, held_lock=True)
                            next_help_ts = time.time() + ah_interval

                    # 3) Alliance Tech Auto-Donate
                    if due_tech and self._always_on_daemon_enabled and self._alliance_tech_watcher_enabled:
                        with self._lock:
                            abort_manual = self._is_manual_bot_busy_locked()
                        if not abort_manual:
                            self._run_alliance_tech_once(force_log=False, held_lock=True)
                            next_tech_ts = time.time() + at_interval
                finally:
                    self._end_action("always_on_daemon_tick")
                    with self._lock:
                        self._recompute_always_on_state_locked()
            except Exception as exc:
                self.log(f"[Always-On Daemon] Background loop error: {exc}", "warn")
                self._always_on_wake.wait(5.0)
                self._always_on_wake.clear()

    def _begin_action(self, key: str) -> bool:
        with self._lock:
            if key in self._active_actions:
                return False
            self._active_actions.add(key)
            return True

    def _end_action(self, key: str) -> None:
        with self._lock:
            self._active_actions.discard(key)

    def _resolve_hero_progression_pids(self, target: str) -> list[int]:
        running = self._discover_running_clients()
        if multi_client_bot is not None and hasattr(multi_client_bot, "_matches_target"):
            pids = [
                int(p["pid"])
                for p in running
                if p.get("pid") and multi_client_bot._matches_target(p, target)
            ]
            if pids:
                return sorted(set(pids))
        t = str(target or "").strip()
        if t.isdigit() and int(t) > 0:
            return [int(t)]
        return []

    def _begin_hero_progression_lock(self, pids: list[int] | None = None, *, check_bot_cycle: bool = True) -> list[str] | None:
        """Atomically acquire per-PID hero_progression locks (or wildcard 'hero_progression:all')."""
        with self._lock:
            if check_bot_cycle and "bot_cycle" in self._active_actions:
                return None
            if "hero_progression:all" in self._active_actions:
                return None
            if not pids:
                if any(k.startswith("hero_progression:") for k in self._active_actions):
                    return None
                self._active_actions.add("hero_progression:all")
                return ["hero_progression:all"]
            keys = [f"hero_progression:{int(p)}" for p in pids]
            if any(k in self._active_actions for k in keys):
                return None
            for k in keys:
                self._active_actions.add(k)
            return keys

    def _end_hero_progression_lock(self, keys: list[str] | None) -> None:
        if not keys:
            return
        with self._lock:
            for k in keys:
                self._active_actions.discard(k)

    def _subprocess_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        if self.target_pid:
            env["LASTZ_TARGET_PID"] = str(self.target_pid)
        else:
            env.pop("LASTZ_TARGET_PID", None)
        return env

    def _pid_args(self) -> list[str]:
        return ["--pid", str(self.target_pid)] if self.target_pid else []

    def _subproc_run(self, args: list[str], timeout: int = 20, env: dict[str, str] | None = None):
        if env is None:
            env = self._subprocess_env()
        return subprocess.run(
            args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=REPO_ROOT,
            env=env,
            creationflags=NO_WINDOW_FLAGS,
            startupinfo=_hidden_startupinfo(),
        )

    def _subproc_popen(self, args: list[str], env: dict[str, str] | None = None):
        if env is None:
            env = self._subprocess_env()
        return subprocess.Popen(
            args,
            cwd=REPO_ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=NO_WINDOW_FLAGS,
            startupinfo=_hidden_startupinfo(),
        )

    def find_script(self, name: str) -> str:
        candidates = [
            os.path.join(TOOLS_DIR, name),
            os.path.join(TOOLS_DIR, name.replace("_", " ")),
            os.path.join(TOOLS_DIR, name.replace(" ", "_")),
            os.path.join(REPO_ROOT, "daemon", name),
            os.path.join(REPO_ROOT, "daemon", name.replace("_", " ")),
            os.path.join(REPO_ROOT, "daemon", name.replace(" ", "_")),
            os.path.join(REPO_ROOT, "api", name),
            os.path.join(REPO_ROOT, "api", name.replace("_", " ")),
            os.path.join(REPO_ROOT, "api", name.replace(" ", "_")),
            os.path.join(SCRATCH_DIR, name),
            os.path.join(SCRATCH_DIR, name.replace("_", " ")),
            os.path.join(SCRATCH_DIR, name.replace(" ", "_")),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return os.path.join(TOOLS_DIR if os.path.isdir(TOOLS_DIR) else DATA_DIR, name)

    def find_file(self, name: str) -> str:
        candidates = [
            os.path.join(DATA_DIR, name),
            os.path.join(DATA_DIR, name.replace("_", " ")),
            os.path.join(DATA_DIR, name.replace(" ", "_")),
            os.path.join(SCRATCH_DIR, name),
            os.path.join(SCRATCH_DIR, name.replace("_", " ")),
            os.path.join(SCRATCH_DIR, name.replace(" ", "_")),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return os.path.join(DATA_DIR, name)

    def _run_tool(self, script_name: str, extra_args: list[str] | None = None, timeout: int = 30, env=None, utf8: bool = True):
        script = self.find_script(script_name)
        if not script or not os.path.exists(script):
            raise FileNotFoundError(f"Script not found in {REPO_ROOT}: {script_name}")
        cmd = _build_script_cmd(script, extra_args=extra_args, utf8=utf8)
        return self._subproc_run(cmd, timeout=timeout, env=env)

    def _stream_tool(
        self,
        script_name: str,
        extra_args: list[str] | None = None,
        timeout: int = 180,
        env: dict[str, str] | None = None,
        utf8: bool = True,
        on_line: Any = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a tool script via subprocess.Popen and stream stdout/stderr line-by-line in real time."""
        script = self.find_script(script_name)
        if not script or not os.path.exists(script):
            raise FileNotFoundError(f"Script not found in {REPO_ROOT}: {script_name}")
        cmd = _build_script_cmd(script, extra_args=extra_args, utf8=utf8)
        run_env = dict(env) if env is not None else self._subprocess_env()
        run_env["PYTHONUNBUFFERED"] = "1"
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=REPO_ROOT,
            env=run_env,
            creationflags=NO_WINDOW_FLAGS,
            startupinfo=_hidden_startupinfo(),
        )
        out_chunks: list[str] = []
        err_chunks: list[str] = []

        def _pump(pipe: Any, sink: list[str], is_err: bool) -> None:
            if pipe is None:
                return
            try:
                for raw_line in iter(pipe.readline, ""):
                    sink.append(raw_line)
                    if on_line is not None:
                        try:
                            on_line(raw_line, is_err)
                        except Exception:
                            pass
            finally:
                try:
                    pipe.close()
                except Exception:
                    pass

        t_out = threading.Thread(target=_pump, args=(proc.stdout, out_chunks, False), daemon=True)
        t_err = threading.Thread(target=_pump, args=(proc.stderr, err_chunks, True), daemon=True)
        t_out.start()
        t_err.start()

        timed_out = False
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            rc = -1

        t_out.join(timeout=3.0)
        t_err.join(timeout=3.0)
        if timed_out:
            self.log(f"[ERR] Tool '{script_name}' timed out after {timeout}s.", "err", category="ERR")
        return subprocess.CompletedProcess(cmd, rc, "".join(out_chunks), "".join(err_chunks))

    @staticmethod
    def _norm_log_dedup(text: str) -> str:
        return re.sub(r"\s+", " ", str(text or "").strip().lower())

    def _make_bot_stream_handler(self):
        """Build a live line-by-line parser for multi client bot.py stdout/stderr."""
        state: dict[str, Any] = {
            "payload": None,
            "streamed_norm": set(),
        }

        def _record(txt: str) -> None:
            n = self._norm_log_dedup(txt)
            if n:
                state["streamed_norm"].add(n)

        def _on_line(raw_ln: str, is_stderr: bool) -> None:
            ln = raw_ln.rstrip("\r\n").strip()
            if not ln:
                return
            if is_stderr:
                low = ln.lower()
                if "traceback" in low or "error" in low or "exception" in low:
                    self.log(f"[ERR] [stderr] {ln}", "err", category="ERR")
                elif "warn" in low:
                    self.log(f"[WARN] [stderr] {ln}", "warn", category="WARN")
                else:
                    self.log(f"[DETAIL] [stderr] {ln}", "detail", category="DETAIL")
                _record(ln)
                return

            if ln.startswith('{"ok":'):
                try:
                    obj = json.loads(ln)
                    if isinstance(obj, dict):
                        state["payload"] = obj
                        return
                except Exception:
                    pass

            if ln.startswith("[STAGE "):
                self.log(ln, "stage", category="STAGE")
                _record(ln)
            elif ln.startswith("[BOT_STEP]"):
                body = ln[len("[BOT_STEP]"):].strip()
                self.log(f"[STEP] {body}", "step", category="STEP")
                _record(body)
            elif ln.startswith("[BOT_DETAIL]"):
                body = ln[len("[BOT_DETAIL]"):].strip()
                self.log(f"[DETAIL] {body}", "detail", category="DETAIL")
                _record(body)
            elif ln.startswith("[BOT_TIP]"):
                body = ln[len("[BOT_TIP]"):].strip()
                # Preserve client/task prefix while filtering hex spam
                tip_text = body.split(":", 1)[1].strip() if ":" in body else body
                if _filter_in_game_tips([tip_text]):
                    cat, lvl, lbl = _classify_in_game_tip(tip_text)
                    self.log(
                        f"[{cat}] {lbl} {body}",
                        lvl,
                        category=cat,
                        is_tip=(cat in ("ERR", "WARN")),
                    )
                    _record(tip_text)
                    _record(body)
            elif ln.startswith("[BOT_MODAL]"):
                body = ln[len("[BOT_MODAL]"):].strip()
                self.log(f"[WARN] Popped modal {body}", "warn", category="WARN", is_tip=True)
                _record(body)
            elif ln.startswith("[BOT_ERR]"):
                body = ln[len("[BOT_ERR]"):].strip()
                self.log(f"[ERR] {body}", "err", category="ERR")
                _record(body)
            elif ln.startswith("[CYCLE_SUMMARY]"):
                body = ln[len("[CYCLE_SUMMARY]"):].strip()
                self.log(f"[OK] {body}", "ok", category="OK")
                _record(body)
            elif not ln.startswith(("{", "}", "[", "]")):
                self.log(ln, "info")
                _record(ln)

        return _on_line, state

    def _extract_before_after_deltas(self, t_res: dict[str, Any]) -> list[str]:
        """Extract human-readable before->after delta lines from any task dict."""
        deltas: list[str] = []
        raw_ba = t_res.get("before_after") or t_res.get("deltas")
        if isinstance(raw_ba, dict):
            for k, v in raw_ba.items():
                if isinstance(v, dict) and "before" in v and "after" in v:
                    if v["before"] != v["after"]:
                        deltas.append(f"{k}: {v['before']} -> {v['after']}")
                elif isinstance(v, (list, tuple)) and len(v) == 2 and v[0] != v[1]:
                    deltas.append(f"{k}: {v[0]} -> {v[1]}")
                elif v not in (None, "", 0, False):
                    deltas.append(f"{k}: {v}")
        elif isinstance(raw_ba, list):
            for item in raw_ba:
                s = str(item or "").strip()
                if s:
                    deltas.append(s)

        b_dict = t_res.get("before")
        a_dict = t_res.get("after")
        if isinstance(b_dict, dict) and isinstance(a_dict, dict):
            all_keys = list(dict.fromkeys([*b_dict.keys(), *a_dict.keys()]))
            for k in all_keys:
                bv = b_dict.get(k)
                av = a_dict.get(k)
                if bv != av:
                    deltas.append(f"{k}: {bv} -> {av}")

        for k, v in t_res.items():
            if not isinstance(k, str):
                continue
            if k.endswith("_before"):
                stem = k[:-7]
                ak = f"{stem}_after"
                if ak in t_res and t_res[ak] != v:
                    deltas.append(f"{stem}: {v} -> {t_res[ak]}")
            elif k.startswith("before_") and k != "before_after":
                stem = k[7:]
                ak = f"after_{stem}"
                if ak in t_res and t_res[ak] != v:
                    deltas.append(f"{stem}: {v} -> {t_res[ak]}")
        return deltas

    def _log_task_deep_details(
        self,
        c_lbl: str,
        t_name: str,
        t_res: dict[str, Any],
        streamed_norm: set[str],
    ) -> None:
        """Emit any deep diagnostic details (detail_lines, deltas, tips, modals, send_errors) not yet streamed."""
        if not isinstance(t_res, dict):
            return

        def _was_seen(text: str) -> bool:
            nt = self._norm_log_dedup(text)
            if not nt:
                return True
            if nt in streamed_norm:
                return True
            for existing in streamed_norm:
                if nt in existing:
                    return True
            return False

        # 1. Structured detail_lines
        for dl in _as_list(t_res.get("detail_lines")):
            ds = str(dl or "").strip()
            if ds and not _was_seen(ds):
                self.log(f"[DETAIL] [{c_lbl}] ({t_name}) {ds}", "detail", category="DETAIL")
                streamed_norm.add(self._norm_log_dedup(ds))

        # 2. Before -> after deltas
        for delta_s in self._extract_before_after_deltas(t_res):
            if delta_s and not _was_seen(delta_s):
                self.log(f"[DETAIL] [{c_lbl}] ({t_name}) Delta: {delta_s}", "detail", category="DETAIL")
                streamed_norm.add(self._norm_log_dedup(delta_s))

        # 3. In-game tips (filtered against hex color spam & classified cleanly so normal toasts aren't [WARN])
        tips = _filter_in_game_tips(t_res.get("in_game_tips") or t_res.get("tips") or [])
        for tip in tips:
            if not _was_seen(tip):
                cat, lvl, lbl = _classify_in_game_tip(tip)
                self.log(
                    f"[{cat}] [{c_lbl}] ({t_name}) {lbl}: {tip}",
                    lvl,
                    category=cat,
                    is_tip=(cat in ("ERR", "WARN")),
                )
                streamed_norm.add(self._norm_log_dedup(tip))

        # 4. Popped modals
        for m in _as_list(t_res.get("popped_modals") or t_res.get("modals")):
            ms = str(m or "").strip()
            if ms and not _was_seen(ms):
                self.log(
                    f"[WARN] [{c_lbl}] ({t_name}) Popped modal: {ms}",
                    "warn",
                    category="WARN",
                    is_tip=True,
                )
                streamed_norm.add(self._norm_log_dedup(ms))

        # 5. RPC / send_errors / errors
        raw_errs: list[str] = []
        for ek in ("send_errors", "errors"):
            ev = t_res.get(ek)
            if isinstance(ev, (list, tuple, dict)):
                raw_errs.extend(str(x).strip() for x in _as_list(ev) if str(x).strip())
            elif isinstance(ev, str) and ev.strip():
                raw_errs.append(ev.strip())
        if not t_res.get("ok", True) and t_res.get("error"):
            raw_errs.append(str(t_res.get("error")).strip())
        for es in raw_errs:
            if es and not _was_seen(es):
                self.log(f"[ERR] [{c_lbl}] ({t_name}) RPC/Send Error: {es}", "err", category="ERR")
                streamed_norm.add(self._norm_log_dedup(es))

    def _open_output_file(self, path: str) -> None:
        if path and os.path.exists(path) and not os.environ.get("HEINZ_NO_STARTFILE"):
            os.startfile(path)

    def _client_display_name(self, proc: dict[str, Any] | None) -> str:
        if not proc:
            return "Client"
        pid = int(proc["pid"]) if proc.get("pid") is not None else None
        reg_uid = str(proc.get("uid") or proc.get("reg_uid") or "").strip()
        with self._lock:
            live = dict(self._live_info_by_pid.get(pid) or {}) if pid is not None else {}
            cached_uid_name = self._uid_name_cache.get(reg_uid, "") if reg_uid else ""
        name = str(proc.get("name") or live.get("name") or "").strip()
        if name:
            return name
        if cached_uid_name:
            return cached_uid_name
        return str(proc.get("label") or proc.get("unity_profile") or "Client")

    def _discover_running_clients(self, query_lua: bool = False, force_pids: list[int] | None = None):
        if client_discovery is not None:
            running = client_discovery.find_running_processes()
        else:
            running = []
            exe_roles = {"survival.exe": ("Main", "main"), "farmgame.exe": ("Farm", "farm"), "alt3game.exe": ("Third", "farm")}
            for proc in psutil.process_iter(["pid", "name"]):
                nm = str(proc.info.get("name") or "")
                if nm.lower() in exe_roles:
                    lbl, role = exe_roles[nm.lower()]
                    running.append({"pid": int(proc.info["pid"]), "exe_name": nm, "label": lbl, "role": role})

        active_pids = {int(c["pid"]) for c in running}
        with self._lock:
            for dead_pid in list(self._live_info_by_pid.keys()):
                if dead_pid not in active_pids:
                    self._live_info_by_pid.pop(dead_pid, None)

        force_set = set(force_pids or [])
        for item in running:
            pid = int(item["pid"])
            with self._lock:
                cached_live = dict(self._live_info_by_pid[pid]) if pid in self._live_info_by_pid else None
            need_query = query_lua and (cached_live is None or not cached_live.get("loggedIn") or pid in force_set)
            if need_query and client_discovery is not None:
                try:
                    if client_discovery._xlua_loaded(pid):
                        ok, out = client_discovery.frida_eval_lua(pid, client_discovery.LUA_QUICK_STATUS)
                        if ok:
                            data = json.loads(out)
                            if isinstance(data, dict):
                                uid_str = str(data.get("uid") or "").strip()
                                nm_str = str(data.get("name") or "").strip()
                                with self._lock:
                                    self._live_info_by_pid[pid] = data
                                    if uid_str and nm_str:
                                        self._uid_name_cache[uid_str] = nm_str
                except Exception:
                    pass
            with self._lock:
                live = dict(self._live_info_by_pid.get(pid) or {})
            if live:
                for lk in ("loggedIn", "name", "uid", "serverId", "selfServerId", "allianceTag", "hqLv"):
                    if live.get(lk) not in (None, ""):
                        item[lk] = live[lk]
        return running

    def _refresh_setup_status(self, base_dir: str | None = None) -> dict[str, Any]:
        if sync_farm_clients is None:
            with self._lock:
                return copy.deepcopy(self.setup_status)
        try:
            with self._lock:
                pref_name = str(self.env.get("playerName") or "")
            st = sync_farm_clients.inspect_setup_status(
                base_dir or None,
                preferred_name=pref_name,
            )
            if isinstance(st, dict):
                with self._lock:
                    self.setup_status = st
        except Exception as exc:
            self.log(f"Setup scan note: {exc}", "warn")
        with self._lock:
            return copy.deepcopy(self.setup_status)

    def inspect_setup(self, base_dir: str = "") -> dict[str, Any]:
        return self._refresh_setup_status(base_dir or None)

    def _update_dropdown_values(self, running: list[dict[str, Any]]) -> None:
        with self._lock:
            running_opts = [f"{self._client_display_name(c)} (PID {c['pid']})" for c in running]
            running_labels = {str(c.get("label") or "").lower() for c in running}
            stopped_opts = []
            for client in self.discovered_clients:
                lbl = str(client.get("label") or "").strip()
                if lbl and lbl.lower() not in running_labels:
                    stopped_opts.append(f"Launch: {lbl}")
            values = ["Auto"] + running_opts + stopped_opts
            self.dropdown_values = values
            matched = None
            if self.selected_client_pid is not None:
                matched = next((v for v in running_opts if v.endswith(f"(PID {self.selected_client_pid})")), None)
            if matched is None and self.selected_client_label:
                lbl_proc = next((c for c in running if str(c.get("label") or "") == self.selected_client_label), None)
                if lbl_proc is not None:
                    self.selected_client_pid = int(lbl_proc["pid"])
                    matched = next((v for v in running_opts if v.endswith(f"(PID {self.selected_client_pid})")), None)
            if matched:
                self.selected_dropdown = matched
            elif self.selected_client_pid is None and self.selected_client_label is None:
                self.selected_dropdown = "Auto"

    def _invalidate_bot_task_status_cache(self) -> None:
        if multi_client_bot is None:
            return
        inv_fn = getattr(multi_client_bot, "_invalidate_task_status_cache", None)
        if callable(inv_fn):
            try:
                inv_fn()
                return
            except Exception:
                pass
        lock_obj = getattr(multi_client_bot, "_TASK_STATUS_LOCK", None)
        cache_obj = getattr(multi_client_bot, "_TASK_STATUS_CACHE", None)
        if isinstance(cache_obj, dict):
            if lock_obj is not None:
                with lock_obj:
                    cache_obj.clear()
            else:
                cache_obj.clear()

    def _refresh_fleet_state(self, live_snapshots: dict[str, Any] | None = None, status_data: dict[str, Any] | None = None) -> None:
        if status_data is None:
            try:
                status_data = multi_client_bot.get_status(skip_discovery=True) if multi_client_bot is not None else {}
            except Exception:
                status_data = {}

        with self._lock:
            last_by_label: dict[str, Any] = {}
            last_cycle = status_data.get("last_cycle") or {}
            for c in last_cycle.get("clients", []):
                if isinstance(c, dict):
                    last_by_label[str(c.get("label") or "")] = c

            running_by_label = {str(r.get("label") or ""): r for r in self.running_clients}
            snap_by_label = live_snapshots or {}
            discovered = list(self.discovered_clients) or list(self.running_clients)

            cards = []
            summary_parts = []
            for client in discovered:
                lbl = str(client.get("label") or client.get("unity_profile") or "Client")
                role = str(client.get("role") or "farm")
                run_info = running_by_label.get(lbl)
                pid = int(run_info["pid"]) if run_info else None
                pid_txt = f"PID {pid}" if pid else "Stopped"
                summary_parts.append(f"{lbl}: {pid_txt}")
                snap = snap_by_label.get(lbl) or (last_by_label.get(lbl, {}).get("snapshot") or {})
                live = (self._live_info_by_pid.get(pid) if pid else None) or {}
                now_sec = time.time()

                shield_end = int(live.get("shieldEndTime") or snap.get("shieldEndTime") or snap.get("shield_end_time") or 0)
                is_shielded = (shield_end > now_sec) or bool(snap.get("shielded"))
                shield_sec = max(0, int(shield_end - now_sec)) if shield_end > now_sec else 0
                if is_shielded and shield_sec > 0:
                    h = shield_sec // 3600
                    m = (shield_sec % 3600) // 60
                    shield_text = f"{h}h {m}m" if h > 0 else f"{m}m"
                elif is_shielded:
                    shield_text = "Shield Active"
                else:
                    shield_text = "UNSHIELDED"

                power_val = live.get("power") or snap.get("power") or 0
                hq_val = live.get("hqLevel") or snap.get("hqLv") or (run_info.get("hqLv") if run_info else None)
                stamina_val = live.get("stamina") if live.get("stamina") is not None else snap.get("stamina")
                diamond_val = live.get("diamond") if live.get("diamond") is not None else snap.get("diamond")
                free_f = live.get("freeFormations") if live.get("freeFormations") is not None else snap.get("freeFormations")
                total_f = live.get("totalFormations") if live.get("totalFormations") is not None else snap.get("unlockFormations")
                under_attack = bool(live.get("underAttack") or snap.get("underAttack"))
                incoming_attacks = int(live.get("incomingAttacks") or snap.get("incomingAttacks") or 0)
                active_marches = int(live.get("activeMarches") or snap.get("activeMarches") or 0)
                server_id_val = live.get("selfServerId") or live.get("serverId") or snap.get("serverId") or client.get("server_id")
                display_name = live.get("name") or snap.get("name") or (self._client_display_name(run_info) if run_info else lbl)
                alliance_tag = live.get("allianceTag") or snap.get("allianceTag") or ""

                cards.append({
                    "label": lbl,
                    "role": role,
                    "running": bool(run_info),
                    "pid": pid,
                    "exe_name": client.get("exe_name") or "",
                    "name": display_name,
                    "allianceTag": alliance_tag,
                    "hqLv": hq_val,
                    "serverId": server_id_val,
                    "powerM": round(int(power_val) / 1_000_000, 1) if power_val else None,
                    "stamina": stamina_val,
                    "diamond": diamond_val,
                    "freeFormations": free_f,
                    "unlockFormations": total_f,
                    "activeMarches": active_marches,
                    "shielded": is_shielded,
                    "shieldEndTime": shield_end,
                    "shieldSec": shield_sec,
                    "shieldText": shield_text,
                    "underAttack": under_attack,
                    "incomingAttacks": incoming_attacks,
                })

            sched_root = status_data.get("schedule") or {}
            primary = sched_root.get("primary") or {}
            if primary.get("skipped"):
                prev_win_txt = str((getattr(self, "fleet_state", None) or {}).get("win_task_text") or "").strip()
                sched_txt = prev_win_txt if prev_win_txt else "Checking..."
            elif primary.get("exists"):
                next_run = "Scheduled"
                for line in str(primary.get("raw") or "").splitlines():
                    if line.startswith("Next Run Time:"):
                        next_run = line.split(":", 1)[1].strip()
                        break
                sched_txt = f"Installed ({next_run})"
            else:
                sched_txt = "Not Registered"

            fin_txt = last_cycle.get("finished_at", "Never")
            if isinstance(fin_txt, str) and len(fin_txt) > 19:
                fin_txt = fin_txt[:19].replace("T", " ")

            self.fleet_state = {
                "summary": " • ".join(summary_parts) if summary_parts else "No clients found yet",
                "daemon_running": bool(status_data.get("daemon_running")),
                "win_task_text": sched_txt,
                "last_cycle_text": fin_txt,
                "clients": cards,
            }

    def _poll_loop(self) -> None:
        loop_idx = 0
        while self.is_monitoring:
            try:
                with self._lock:
                    refresh_all_pids = [int(c["pid"]) for c in self.running_clients] if (loop_idx % 5 == 0) else None
                    need_disc = client_discovery is not None and (loop_idx % 12 == 0 or not self.discovered_clients)
                running = self._discover_running_clients(query_lua=True, force_pids=refresh_all_pids)
                disc_res = client_discovery.discover_clients(save_cache=False) if need_disc and client_discovery is not None else None
                with self._lock:
                    self.running_clients = running
                    if disc_res is not None:
                        self.discovered_clients = (
                            disc_res if isinstance(disc_res, list) else (disc_res.get("clients", []) if isinstance(disc_res, dict) else [])
                        )

                    active_proc = None
                    if running:
                        if self.selected_client_pid is not None:
                            active_proc = next((c for c in running if int(c["pid"]) == self.selected_client_pid), None)
                        if active_proc is None and self.selected_client_label:
                            active_proc = next((c for c in running if str(c.get("label")) == self.selected_client_label), None)
                        if active_proc is None:
                            mains = [c for c in running if str(c.get("role", "")).lower() == "main"]
                            active_proc = mains[0] if mains else running[0]

                    self._update_dropdown_values(running)

                if active_proc is not None:
                    pid = int(active_proc["pid"])
                    with self._lock:
                        self.target_pid = pid
                        live = dict(self._live_info_by_pid.get(pid) or {})
                    os.environ["LASTZ_TARGET_PID"] = str(pid)
                    disp_name = self._client_display_name(active_proc)
                    smooth_fps = live.get("smoothFps") or live.get("fps") or 0
                    fps_cap = live.get("fpsCap") or 0
                    if smooth_fps > 0:
                        self.current_fps = smooth_fps
                        fps_display = f"{smooth_fps} FPS" if (fps_cap <= 0 or fps_cap == smooth_fps) else f"{smooth_fps} FPS (Cap: {fps_cap})"
                    else:
                        fps_display = "180 FPS: Locked"
                    with self._lock:
                        self.is_online = True
                        self.status_text = f"{len(running)} Online • {disp_name} (PID {pid})"
                        self.fps_text = fps_display
                    if loop_idx % 5 == 0 and live.get("loggedIn"):
                        sc_id = live.get("sceneId", 0)
                        sc_name = "City" if sc_id == 1 else ("World" if sc_id == 2 else f"Scene {sc_id}")
                        p_power = live.get("power", 0)
                        p_stamina = live.get("stamina", 0)
                        self.log(f"Diagnostic Heartbeat: {disp_name} | Scene: {sc_name} | Power: {p_power:,} | Stamina: {p_stamina:.0f}", "info")
                    now = time.time()
                    if pid != self._last_env_pid or (now - self._last_env_ts) >= 25.0:
                        try:
                            env = detect_environment(pid)
                            self._last_env_pid = pid
                            self._last_env_ts = now
                            if isinstance(env, dict):
                                pname = str(env.get("playerName") or "").strip()
                                puid = str(env.get("playerUid") or "").strip()
                                with self._lock:
                                    self.env.update(env)
                                    if pname:
                                        self._live_info_by_pid.setdefault(pid, {}).update({"loggedIn": True, "name": pname, "uid": puid})
                                        if puid:
                                            self._uid_name_cache[puid] = pname
                                    self._update_dropdown_values(self.running_clients)
                        except Exception:
                            pass
                else:
                    os.environ.pop("LASTZ_TARGET_PID", None)
                    with self._lock:
                        self.target_pid = None
                        self.is_online = False
                        self.status_text = "No Client Running"
                        self.fps_text = "Offline"

                if loop_idx % 3 == 0:
                    bot_status = {}
                    if multi_client_bot is not None:
                        try:
                            bot_status = multi_client_bot.get_status(
                                skip_discovery=True,
                                skip_running=True,
                                include_schedule=(loop_idx % 18 == 0),
                            )
                        except TypeError:
                            try:
                                bot_status = multi_client_bot.get_status(skip_discovery=True)
                            except Exception:
                                bot_status = {}
                        except Exception:
                            bot_status = {}
                    if loop_idx % 12 == 0:
                        self._refresh_setup_status()
                    with self._lock:
                        self._refresh_fleet_state(status_data=bot_status)
            except Exception:
                pass
            loop_idx += 1
            time.sleep(3.0 if self.is_online else 5.0)

    def ensure_daemon_running(self) -> None:
        if not self.is_monitoring:
            return
        running = False
        # Filter by process name first before reading cmdline (~30x faster than scanning all ~350 processes).
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = (proc.info.get("name") or "").lower()
                if not (pname.startswith("python") or pname.startswith("heinz")):
                    continue
                if int(proc.info.get("pid") or 0) == os.getpid():
                    continue
                cmd = " ".join(proc.cmdline() or [])
                if "lastz auto engine daemon" in cmd or "lastz_auto_engine_daemon" in cmd:
                    running = True
                    break
            except Exception:
                pass
        if not running and self.is_monitoring:
            daemon_script = self.find_script("lastz auto engine daemon.py")
            if daemon_script and os.path.exists(daemon_script):
                try:
                    cmd = _build_script_cmd(daemon_script, ["--parent-pid", str(os.getpid())])
                    spawned = self._subproc_popen(cmd)
                    with self._lock:
                        if not self.is_monitoring:
                            try:
                                spawned.terminate()
                            except Exception:
                                pass
                            return
                        self._daemon_proc = spawned
                    self.log("Auto-started background engine daemon.", "info")
                except Exception:
                    pass

    _RULE_KEYS = (
        "trucks", "furylord", "bounties", "bounty_steal", "mining_event",
        "vip_store_rewards", "area_exploration", "hero_battlefield", "arena",
        "war_safety", "hospital_heal", "auto_help", "alliance_daily", "always_on_daemon",
        "research_queue", "radar_events", "free_recruits", "garage_upgrades", "hero_progression", "daily_tasks_complete",
    )

    def _build_config_snapshot(self) -> tuple[int, dict[str, Any]]:
        if multi_client_bot is None:
            return (0, {})
        with self._lock:
            try:
                cfg_path = str(getattr(multi_client_bot, "CONFIG_PATH", "") or "")
                file_sig: tuple[int, int, int, int] | None = None
                if cfg_path and os.path.isfile(cfg_path):
                    file_sig = _stat_sig_from_stat(os.stat(cfg_path))
                    cached = getattr(self, "_config_snapshot_cache", None)
                    if cached is not None and cached[0] == cfg_path and cached[1] == file_sig:
                        return (cached[2], copy.deepcopy(cached[3]))
                cfg = multi_client_bot.load_config()
                if not isinstance(cfg, dict):
                    raise ValueError("Invalid config payload")
                if cfg_path and os.path.isfile(cfg_path):
                    file_sig = _stat_sig_from_stat(os.stat(cfg_path))
            except Exception:
                last_good = getattr(self, "_last_good_config_snapshot", None)
                if last_good is not None:
                    return (last_good[0], copy.deepcopy(last_good[1]))
                cached_fb = getattr(self, "_config_snapshot_cache", None)
                if cached_fb is not None:
                    return (cached_fb[2], copy.deepcopy(cached_fb[3]))
                return (0, {})

            defs = cfg.get("client_defaults") or {}
            main_cfg = defs.get("main") or {}
            farm_cfg = defs.get("farm") or {}
            snap = {
                "cycle_interval_seconds": int(cfg.get("cycle_interval_seconds", 180)),
                "task_interval_minutes": int((cfg.get("schedule") or {}).get("interval_minutes", 15)),
                "auto_launch_stopped_clients": bool(cfg.get("auto_launch_stopped_clients", False)),
                "auto_launch_mode": str(cfg.get("auto_launch_mode", "eco")).lower(),
                "main_enabled": bool(main_cfg.get("enabled", True)),
                "farm_tasks": dict(farm_cfg.get("tasks") or {}),
                "main_tasks": dict(main_cfg.get("tasks") or {}),
                "rules": {
                    k: copy.deepcopy(main_cfg.get(k) or farm_cfg.get(k) or cfg.get(k) or {})
                    for k in self._RULE_KEYS
                },
            }
            ver = int(getattr(self, "_config_version", 1)) + 1
            self._config_version = ver
            snap_copy = copy.deepcopy(snap)
            self._last_good_config_snapshot = (ver, snap_copy)
            if cfg_path and file_sig is not None:
                self._config_snapshot_cache = (cfg_path, file_sig, ver, copy.deepcopy(snap))
            return (ver, snap)

    # ------------------------------------------------------------------
    # Continuous Repeat Farming & Map Kills Loop Engine
    # ------------------------------------------------------------------
    _VALID_RSS_LOOP_MODES = ("diamonds", "electricity", "zent", "wood", "food", "priority_queue")
    _VALID_KILL_LOOP_MODES = ("boomers", "standalone_npc", "saga", "tyrant", "furylord", "all_chain")
    _RSS_CANONICAL_NAMES: dict[str, str] = {
        "diamonds": "Diamonds",
        "diamond": "Diamonds",
        "gold": "Diamonds",
        "15": "Diamonds",
        "electricity": "Electricity",
        "power": "Electricity",
        "power plant": "Electricity",
        "12": "Electricity",
        "zent": "Zent",
        "money": "Zent",
        "cash": "Zent",
        "14": "Zent",
        "wood": "Wood",
        "lumber": "Wood",
        "lumberyard": "Wood",
        "2": "Wood",
        "food": "Food",
        "metal": "Food",
        "oil": "Food",
        "farm": "Food",
        "farmland": "Food",
        "mine": "Food",
        "1": "Food",
    }
    _KILL_CHAIN_ALIASES: dict[str, str] = {
        "boomers": "boomers",
        "boomer": "boomers",
        "boomer_runs": "boomers",
        "standalone_npc": "standalone_npc",
        "npc": "standalone_npc",
        "zombies": "standalone_npc",
        "saga": "saga",
        "saga_boss": "saga",
        "tyrant": "tyrant",
        "tyrant_event": "tyrant",
        "furylord": "furylord",
    }
    _CONDITIONAL_KILL_BOSSES = frozenset({"saga", "tyrant", "furylord"})

    @staticmethod
    def _default_farm_category_summary(category: str) -> dict[str, Any]:
        return {
            "loop_id": "",
            "pid": None,
            "account_label": "",
            "category": str(category or ""),
            "mode": "",
            "running": False,
            "state": "idle",
            "started_at": 0.0,
            "updated_at": 0.0,
            "iterations": 0,
            "total_dispatched": 0,
            "by_target": {},
            "last_message": "",
            "stop_reason": "",
            "stamina": None,
            "free_formations": 0,
            "active_marches": 0,
            "total_formations": 0,
            "options": {},
        }

    @staticmethod
    def _default_kill_detection_dict() -> dict[str, Any]:
        return {
            "ok": False,
            "pid": None,
            "account_label": "",
            "updated_at": 0.0,
            "stamina": None,
            "free_formations": 0,
            "active_marches": 0,
            "total_formations": 0,
            "in_alliance": False,
            "max_npc_level": 0,
            "max_boomer_level": 0,
            "rest_boomer_kills": 0,
            "boomers": {"detected": False, "open_rallies": 0, "viewport_count": 0},
            "standalone_npc": {"detected": False, "viewport_count": 0, "max_level": 0},
            "saga": {"detected": False, "active": False, "act_id": 0, "boss_count": 0, "difficulty_selected": False},
            "tyrant": {"detected": False, "is_open": False, "in_battle": False, "boss_point_id": 0},
            "furylord": {"detected": False, "is_open": False, "in_act": False, "boss_count": 0, "reward_count": 0, "max_reward_count": 4},
        }

    def _ensure_farm_loop_attrs(self) -> threading.RLock:
        """Guarantee loop state attributes exist even if HubBackend.__new__ was used in unit tests."""
        lock = getattr(self, "_farm_loop_lock", None)
        if lock is None:
            base_lock = getattr(self, "_lock", None)
            if base_lock is not None:
                with base_lock:
                    lock = getattr(self, "_farm_loop_lock", None)
                    if lock is None:
                        lock = threading.RLock()
                        self._farm_loop_lock = lock
            else:
                lock = threading.RLock()
                self._farm_loop_lock = lock
        with lock:
            if not hasattr(self, "_farm_loop_seq"):
                self._farm_loop_seq = 0
            if not hasattr(self, "_farm_loops") or not isinstance(self._farm_loops, dict):
                self._farm_loops = {}
            if not hasattr(self, "_last_farm_loop_summary") or not isinstance(self._last_farm_loop_summary, dict):
                self._last_farm_loop_summary = {
                    "rss": self._default_farm_category_summary("rss"),
                    "kills": self._default_farm_category_summary("kills"),
                }
            else:
                for cat in ("rss", "kills"):
                    if cat not in self._last_farm_loop_summary or not isinstance(self._last_farm_loop_summary[cat], dict):
                        self._last_farm_loop_summary[cat] = self._default_farm_category_summary(cat)
            if not hasattr(self, "_last_kill_detection") or not isinstance(self._last_kill_detection, dict):
                self._last_kill_detection = {}
            for attr_name in (
                "_last_kill_detection_by_pid",
                "_last_farm_loop_summary_by_pid",
                "_farm_pid_exec_locks",
                "_farm_pid_state",
            ):
                if not isinstance(getattr(self, attr_name, None), dict):
                    setattr(self, attr_name, {})
        return lock

    # Farm loop safety tuning (seconds)
    _FARM_CLAIM_TTL_SEC: dict[str, float] = {"gather": 180.0, "npc": 90.0, "boomer": 120.0, "saga": 120.0}
    _FARM_BLACKLIST_TTL_SEC = 300.0
    _FARM_PHANTOM_WINDOW_SEC = 15.0
    _FARM_MAX_REJECTS = 3
    _SAGA_SUMMON_COOLDOWN_SEC = 60.0
    _CHAIN_EXHAUSTED_COOLDOWN_SEC = 60.0
    _FARM_CLAIM_CTX_KEYS: dict[str, str] = {
        "gather": "claimed_gather_points",
        "npc": "claimed_npc_points",
        "boomer": "claimed_boomer_points",
        "saga": "claimed_saga_points",
    }

    def _get_farm_pid_exec_lock(self, pid: int) -> threading.Lock:
        """Return the per-PID worker execution lock (serializes Frida step execution across old/new workers)."""
        flock = self._ensure_farm_loop_attrs()
        with flock:
            lk = self._farm_pid_exec_locks.get(int(pid))
            if lk is None:
                lk = threading.Lock()
                self._farm_pid_exec_locks[int(pid)] = lk
            return lk

    def _get_farm_pid_state(self, pid: int) -> dict[str, Any]:
        """Return persisted per-PID farm state (claims, blacklist, saga summon cooldown) surviving loop replacement."""
        flock = self._ensure_farm_loop_attrs()
        with flock:
            st = self._farm_pid_state.get(int(pid))
            if not isinstance(st, dict):
                st = {}
                self._farm_pid_state[int(pid)] = st
            for k in ("gather", "npc", "boomer", "saga", "blacklist"):
                if not isinstance(st.get(k), dict):
                    st[k] = {}
            st.setdefault("last_saga_summon_ts", None)
            return st

    def _acquire_farm_exec_lock(self, pid: int, stop_ev: threading.Event) -> threading.Lock | None:
        """Acquire per-PID exec lock, aborting promptly if the loop is stopped or the Hub shuts down."""
        lk = self._get_farm_pid_exec_lock(pid)
        while True:
            if lk.acquire(timeout=0.25):
                if stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                    lk.release()
                    return None
                return lk
            if stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                return None

    def _build_farm_client_state(self, pid: int, account_label: str) -> dict[str, Any]:
        """Build a real per-account client_state so daily counters are keyed by playerUid/label, not ephemeral PID."""
        puid = ""
        base_lock = getattr(self, "_lock", None)
        try:
            if base_lock is not None:
                with base_lock:
                    live = dict((getattr(self, "_live_info_by_pid", {}) or {}).get(int(pid)) or {})
                    env_pid = getattr(self, "_last_env_pid", None)
                    env = dict(getattr(self, "env", {}) or {})
            else:
                live = dict((getattr(self, "_live_info_by_pid", {}) or {}).get(int(pid)) or {})
                env_pid = getattr(self, "_last_env_pid", None)
                env = dict(getattr(self, "env", {}) or {})
            puid = str(live.get("uid") or live.get("playerUid") or "").strip()
            if not puid and env_pid is not None and int(env_pid) == int(pid):
                puid = str(env.get("playerUid") or "").strip()
        except Exception:
            puid = ""
        lbl = str(account_label or "").strip()
        acct_key = puid or (re.sub(r"[^a-zA-Z0-9_\-]", "_", lbl.lower()).strip("_") if lbl else f"pid_{int(pid)}")
        cs: dict[str, Any] = {"pid": int(pid), "label": lbl or f"PID {int(pid)}", "playerUid": puid, "account_key": acct_key}
        if puid:
            cs["uid"] = puid
        return cs

    @staticmethod
    def _prepare_claims_context(pid_state: dict[str, Any], kinds: tuple[str, ...], now_mono: float) -> dict[str, Any]:
        """Prune persisted claims/blacklist and return the context fragment passed into a bot_actions step."""
        ctx: dict[str, Any] = {}
        for kind in kinds:
            ttl = HubBackend._FARM_CLAIM_TTL_SEC.get(kind, 90.0)
            ctx[HubBackend._FARM_CLAIM_CTX_KEYS[kind]] = HubBackend._prune_timed_claims(pid_state[kind], now_mono, ttl_sec=ttl)
        ctx["blacklisted_points"] = HubBackend._prune_timed_claims(
            pid_state["blacklist"], now_mono, ttl_sec=HubBackend._FARM_BLACKLIST_TTL_SEC
        )
        return ctx

    @staticmethod
    def _record_claims_context(pid_state: dict[str, Any], kinds: tuple[str, ...], step_ctx: dict[str, Any], raw_res: Any, now_mono: float) -> None:
        for kind in kinds:
            HubBackend._record_timed_claims(pid_state[kind], step_ctx.get(HubBackend._FARM_CLAIM_CTX_KEYS[kind]), raw_res, now_mono)

    @classmethod
    def _extract_dispatch_pairs(cls, raw_res: Any, default_target: str = "") -> list[dict[str, Any]]:
        """Extract (formation_uuid, target ids, by_target key) for each dispatch reported by a bot_actions step."""
        out: list[dict[str, Any]] = []
        if not isinstance(raw_res, dict):
            return out
        items: list[dict[str, Any]] = []
        disp = raw_res.get("dispatched")
        if isinstance(disp, list):
            items.extend(i for i in disp if isinstance(i, dict))
        elif isinstance(disp, dict) and disp:
            items.append(disp)
        if not items:
            for k in ("started_rally", "hosted", "marched"):
                v = raw_res.get(k)
                if isinstance(v, dict) and v:
                    items.append(v)
            joined = raw_res.get("joined")
            if isinstance(joined, list):
                items.extend(j for j in joined if isinstance(j, dict))
            elif isinstance(joined, dict) and joined:
                items.append(joined)
        for it in items:
            fu = str(it.get("formationUuid") or it.get("formation_uuid") or it.get("formation") or "").strip()
            if not fu or fu in ("0", "nil"):
                continue
            tkeys: list[str] = []
            for tk in ("pointId", "targetPoint", "point_id", "warUuid", "claimKey"):
                tv = it.get(tk)
                if tv is None:
                    continue
                ts_ = str(tv).strip()
                if ts_ and ts_ not in ("0", "nil") and ts_ not in tkeys:
                    tkeys.append(ts_)
            rt_raw = str(it.get("resourceType") or it.get("resource_type") or it.get("target") or default_target or "").strip().lower()
            canon = cls._RSS_CANONICAL_NAMES.get(rt_raw)
            bt_key = canon.lower() if canon else (rt_raw or default_target)
            out.append({"formation": fu, "targets": tkeys, "bt_key": bt_key})
        return out

    def _check_phantom_dispatch(
        self,
        entry: dict[str, Any],
        tracker: dict[str, Any],
        pid_state: dict[str, Any],
        raw_res: Any,
        norm: dict[str, Any],
        default_target: str,
    ) -> dict[str, Any]:
        """Detect server/client-rejected dispatches (same formation re-picked immediately), blacklist targets, correct counters.

        Returns {"phantoms": int, "targets": list[str], "consecutive": int}; mutates `norm` so phantom
        dispatches are never counted as successes.
        """
        now_m = time.monotonic()
        result = {"phantoms": 0, "targets": [], "consecutive": int(tracker.get("consecutive") or 0)}
        if norm.get("status") != "dispatched":
            return result
        pairs = self._extract_dispatch_pairs(raw_res, default_target)
        last: dict[str, dict[str, Any]] = tracker.setdefault("last", {})
        for k in [k for k, v in last.items() if (now_m - float(v.get("ts") or 0.0)) > self._FARM_PHANTOM_WINDOW_SEC]:
            last.pop(k, None)
        act_now = norm.get("active_marches")
        phantom_pairs: list[dict[str, Any]] = []
        for p in pairs:
            prev = last.get(p["formation"])
            if prev is None:
                continue
            prev_act = prev.get("active_marches")
            same_target = bool(set(p["targets"]) & set(prev.get("targets") or []))
            not_advanced = act_now is None or prev_act is None or int(act_now) <= int(prev_act)
            if same_target or not_advanced:
                phantom_pairs.append({**p, "prev_targets": list(prev.get("targets") or []), "prev_counted": bool(prev.get("counted", True))})
        phantom_fus = {p["formation"] for p in phantom_pairs}
        for p in pairs:
            last[p["formation"]] = {
                "targets": list(p["targets"]),
                "ts": now_m,
                "active_marches": act_now,
                "counted": p["formation"] not in phantom_fus,
            }

        if not phantom_pairs:
            if int(norm.get("dispatched_count") or 0) > 0:
                tracker["consecutive"] = 0
                result["consecutive"] = 0
            return result

        rejected: list[str] = []
        for p in phantom_pairs:
            for t in list(p["targets"]) + list(p["prev_targets"]):
                if t and t not in rejected:
                    rejected.append(t)
                    pid_state["blacklist"][t] = now_m
        n_ph = len(phantom_pairs)
        tracker["consecutive"] = int(tracker.get("consecutive") or 0) + 1
        result.update({"phantoms": n_ph, "targets": rejected, "consecutive": int(tracker["consecutive"])})

        # Never count the phantom as a success; also roll back the earlier (fake) success for that formation
        new_cnt = max(0, int(norm.get("dispatched_count") or 0) - n_ph)
        tcounts = dict(norm.get("target_counts") or {})
        for p in phantom_pairs:
            bk = p.get("bt_key") or default_target
            if bk in tcounts:
                tcounts[bk] = max(0, int(tcounts[bk]) - 1)
                if tcounts[bk] == 0:
                    tcounts.pop(bk, None)
        norm["dispatched_count"] = new_cnt
        norm["target_counts"] = tcounts if new_cnt > 0 else {}
        if new_cnt == 0:
            norm["status"] = "rejected"
        rollback = [p for p in phantom_pairs if p.get("prev_counted")]
        flock = self._ensure_farm_loop_attrs()
        with flock:
            entry["total_dispatched"] = max(0, int(entry.get("total_dispatched") or 0) - len(rollback))
            bt = entry.setdefault("by_target", {})
            for p in rollback:
                bk = str(p.get("bt_key") or default_target)
                if bk in bt:
                    bt[bk] = max(0, int(bt[bk]) - 1)
        return result

    @staticmethod
    def _serialize_farm_loop_entry(entry: dict[str, Any]) -> dict[str, Any]:
        """Serialize a farm loop entry to a pure JSON-safe dict (stripping Event/Thread objects)."""
        raw_opts = entry.get("options")
        clean_opts = {
            str(k): copy.deepcopy(v)
            for k, v in (raw_opts.items() if isinstance(raw_opts, dict) else ())
            if not str(k).startswith("_")
        }
        stam_raw = entry.get("stamina")
        stamina_val = _safe_int(stam_raw, None) if stam_raw is not None else None
        return {
            "loop_id": str(entry.get("loop_id") or ""),
            "pid": _safe_int(entry.get("pid"), None) if entry.get("pid") is not None else None,
            "account_label": str(entry.get("account_label") or ""),
            "category": str(entry.get("category") or ""),
            "mode": str(entry.get("mode") or ""),
            "running": bool(entry.get("running", False)),
            "state": str(entry.get("state") or "idle"),
            "started_at": float(entry.get("started_at") or 0.0),
            "updated_at": float(entry.get("updated_at") or 0.0),
            "iterations": int(entry.get("iterations") or 0),
            "total_dispatched": int(entry.get("total_dispatched") or 0),
            "by_target": {str(k): int(v) for k, v in (entry.get("by_target") or {}).items()},
            "last_message": str(entry.get("last_message") or ""),
            "stop_reason": str(entry.get("stop_reason") or ""),
            "stamina": stamina_val,
            "free_formations": int(entry.get("free_formations") or 0),
            "active_marches": int(entry.get("active_marches") or 0),
            "total_formations": int(entry.get("total_formations") or 0),
            "options": clean_opts,
        }

    def _build_farm_loops_snapshot_locked(self) -> dict[str, Any]:
        """Build fast, tiny JSON-safe snapshot of active farm loops, per-category summaries, and live detection.

        `rss` / `kills` / `detection` are scoped to the currently selected client PID. When the target is
        Auto (`selected_client_pid is None`), the resolved target PID is used, falling back to the sole active
        loop of that category. `active_loops` always lists every running loop across all PIDs.
        """
        flock = self._ensure_farm_loop_attrs()
        sel_raw = getattr(self, "selected_client_pid", None)
        tgt_raw = getattr(self, "target_pid", None)
        sel_pid = _safe_int(sel_raw, None) if sel_raw not in (None, "", 0) else None
        tgt_pid = _safe_int(tgt_raw, None) if tgt_raw not in (None, "", 0) else None
        explicit = sel_pid is not None and sel_pid > 0
        scope_pid = sel_pid if explicit else (tgt_pid if tgt_pid and tgt_pid > 0 else None)
        with flock:
            active_entries = [
                e for e in self._farm_loops.values()
                if isinstance(e, dict) and e.get("running")
            ]
            active_entries.sort(key=lambda x: (int(x.get("pid") or 0), float(x.get("started_at") or 0.0)))
            active_loops = [self._serialize_farm_loop_entry(e) for e in active_entries]

            cat_out: dict[str, dict[str, Any]] = {}
            for cat in ("rss", "kills"):
                picked: dict[str, Any] | None = None
                if scope_pid is not None:
                    cand = self._farm_loops.get(int(scope_pid))
                    if isinstance(cand, dict) and cand.get("running") and cand.get("category") == cat:
                        picked = cand
                if picked is None and not explicit:
                    matching = [e for e in active_entries if e.get("category") == cat]
                    if len(matching) == 1 or (matching and scope_pid is None):
                        matching.sort(key=lambda x: float(x.get("started_at") or 0.0), reverse=True)
                        picked = matching[0]
                if picked is not None:
                    cat_out[cat] = self._serialize_farm_loop_entry(picked)
                    continue
                last_sum: Any = None
                if scope_pid is not None:
                    last_sum = (self._last_farm_loop_summary_by_pid.get(int(scope_pid)) or {}).get(cat)
                elif not explicit:
                    last_sum = self._last_farm_loop_summary.get(cat)
                if isinstance(last_sum, dict) and last_sum:
                    cat_out[cat] = self._serialize_farm_loop_entry(last_sum)
                else:
                    dflt = self._default_farm_category_summary(cat)
                    if scope_pid is not None and isinstance(dflt, dict):
                        dflt["pid"] = int(scope_pid)
                    cat_out[cat] = dflt

            det_src: Any = None
            det_pid = scope_pid
            if det_pid is None and len({int(e.get("pid") or 0) for e in active_entries}) == 1:
                det_pid = int(active_entries[0].get("pid") or 0) or None
            if det_pid is not None:
                det_src = self._last_kill_detection_by_pid.get(int(det_pid))
            elif not explicit:
                det_src = self._last_kill_detection
            det_copy = copy.deepcopy(det_src) if isinstance(det_src, dict) else {}

        return {
            "active_loops": active_loops,
            "selected_pid": sel_pid if explicit else None,
            "scope_pid": scope_pid,
            "rss": cat_out["rss"],
            "kills": cat_out["kills"],
            "detection": det_copy,
        }

    def get_farm_loops_state(self) -> dict[str, Any]:
        """Return live continuous farming & map kills loop state (WebView2 JSON-safe)."""
        base_lock = getattr(self, "_lock", None)
        if base_lock is not None:
            with base_lock:
                return self._build_farm_loops_snapshot_locked()
        return self._build_farm_loops_snapshot_locked()

    @staticmethod
    def _format_farm_stop_message(
        category: str,
        mode: str,
        stop_reason: str,
        total_dispatched: int,
        stamina: int | None = None,
        detail: str = "",
    ) -> str:
        reason = str(stop_reason or "").strip().lower()
        disp_word = "dispatch" if total_dispatched == 1 else "dispatches"
        if reason == "user_stopped":
            return f"Stopped by user after {total_dispatched} {disp_word}."
        if reason in ("replaced", "replaced_by_new_loop"):
            return f"Switched loop after {total_dispatched} {disp_word}."
        if reason == "shutdown":
            return f"Stopped on Hub shutdown after {total_dispatched} {disp_word}."
        if reason == "out_of_stamina":
            stam_note = f" ({stamina} left)" if stamina is not None else ""
            return f"Stopped: Out of stamina{stam_note} after {total_dispatched} {disp_word}."
        if reason == "no_troops_or_formations":
            return f"Stopped: No usable squads or troops available at base after {total_dispatched} {disp_word}."
        if reason == "not_in_alliance":
            return f"Stopped: Account is not in an alliance after {total_dispatched} {disp_word}."
        if reason == "not_detected":
            return f"Stopped: Target event/boss not currently detected on map after {total_dispatched} {disp_word}."
        if reason == "event_ended":
            return f"Stopped: Event battle window ended after {total_dispatched} {disp_word}."
        if reason == "daily_limit_reached":
            return f"Stopped: Daily reward/attack limit reached after {total_dispatched} {disp_word}."
        if reason == "no_targets_found":
            target_kind = "unoccupied resource tiles" if category == "rss" else "targets"
            return f"Stopped: No matching {target_kind} found on map after {total_dispatched} {disp_word}."
        if reason == "client_offline":
            return f"Stopped: Game client disconnected or closed after {total_dispatched} {disp_word}."
        if reason == "dispatch_rejected":
            return (
                f"Stopped: The game rejected the same march {HubBackend._FARM_MAX_REJECTS} times in a row "
                f"(target locked, taken or not unlocked yet) after {total_dispatched} {disp_word}."
            )
        if reason == "dry_run_complete":
            return f"Dry run finished one full sweep ({total_dispatched} simulated {disp_word}); nothing was sent."
        if reason == "consecutive_errors":
            base_msg = f"Stopped: 3 errors in a row after {total_dispatched} {disp_word}."
            clean_d = str(detail or "").strip()
            return f"{base_msg} Last error: {clean_d}" if clean_d else base_msg
        if reason == "event_not_in_battle":
            return f"Stopped: Event is open but its battle phase has not started ({total_dispatched} {disp_word})."
        if reason == "automation_unavailable":
            return f"Stopped: Automation modules unavailable after {total_dispatched} {disp_word}."
        clean_detail = str(detail or "").strip()
        if clean_detail:
            return f"Stopped ({stop_reason or 'ended'}): {clean_detail} ({total_dispatched} {disp_word})."
        return f"Stopped ({stop_reason or 'ended'}) after {total_dispatched} {disp_word}."

    def _record_farm_summary_locked(self, entry: dict[str, Any], snap: dict[str, Any]) -> None:
        """Persist the final loop snapshot globally (per category) and per PID (caller holds the farm lock)."""
        cat_key = str(entry.get("category") or "")
        if cat_key not in ("rss", "kills"):
            return
        self._last_farm_loop_summary[cat_key] = snap
        pid_v = _safe_int(entry.get("pid"), None)
        if pid_v is not None:
            self._last_farm_loop_summary_by_pid.setdefault(int(pid_v), {})[cat_key] = snap

    def _detach_farm_loop_locked(self, t_pid: int, reason: str, now_ts: float) -> tuple[dict[str, Any], Any, dict[str, Any]] | None:
        """Signal stop on the loop registered for t_pid, record its summary and unregister it (caller holds the farm lock)."""
        entry = self._farm_loops.get(int(t_pid))
        if not isinstance(entry, dict):
            return None
        ev = entry.get("stop_event")
        if ev is not None:
            try:
                ev.set()
            except Exception:
                pass
        entry["running"] = False
        entry["state"] = "stopped"
        entry["stop_reason"] = str(reason or "user_stopped")
        entry["updated_at"] = now_ts
        entry["last_message"] = self._format_farm_stop_message(
            str(entry.get("category") or ""),
            str(entry.get("mode") or ""),
            entry["stop_reason"],
            int(entry.get("total_dispatched") or 0),
            entry.get("stamina"),
        )
        snap = self._serialize_farm_loop_entry(entry)
        self._record_farm_summary_locked(entry, snap)
        self._farm_loops.pop(int(t_pid), None)
        return entry, entry.get("thread"), snap

    def _stop_farm_loops_internal(
        self,
        pid: int | None = None,
        category: str | None = None,
        reason: str = "user_stopped",
        join_timeout: float = 0.4,
        log_stop: bool = True,
    ) -> list[dict[str, Any]]:
        """Signal stop_event on matching farm loop(s), record summary, and optionally join worker threads."""
        flock = self._ensure_farm_loop_attrs()
        to_join: list[tuple[dict[str, Any], Any, dict[str, Any]]] = []
        now_ts = time.time()

        with flock:
            target_pids = [int(pid)] if pid is not None else list(self._farm_loops.keys())
            for t_pid in target_pids:
                entry = self._farm_loops.get(t_pid)
                if not isinstance(entry, dict):
                    continue
                if category is not None and str(entry.get("category") or "") != category:
                    continue
                detached = self._detach_farm_loop_locked(t_pid, reason, now_ts)
                if detached is not None:
                    to_join.append(detached)

        cur_thread = threading.current_thread()
        for _entry, th, snap in to_join:
            if th is not None and th is not cur_thread and getattr(th, "is_alive", lambda: False)():
                if join_timeout > 0:
                    try:
                        th.join(timeout=join_timeout)
                    except Exception:
                        pass
            if log_stop:
                cat_lbl = "RSS Gather" if snap.get("category") == "rss" else "Map Kills"
                acct = snap.get("account_label") or f"PID {snap.get('pid')}"
                self.log(f"[{cat_lbl}] [{acct}] ({snap.get('mode')}) {snap.get('last_message')}", "info")

        return [item[2] for item in to_join]

    def _finalize_farm_loop_worker(
        self,
        entry: dict[str, Any],
        stop_reason: str,
        final_state: str = "stopped",
        detail_msg: str = "",
    ) -> dict[str, Any] | None:
        """Finalize a loop entry from inside its worker thread if it has not already been replaced."""
        flock = self._ensure_farm_loop_attrs()
        pid = int(entry["pid"])
        now_ts = time.time()
        snap_to_log: dict[str, Any] | None = None
        with flock:
            cur = self._farm_loops.get(pid)
            if cur is not entry:
                # Already stopped or replaced externally by stop_* / start_*
                return None
            entry["running"] = False
            entry["state"] = final_state
            entry["stop_reason"] = str(stop_reason or "stopped")
            entry["updated_at"] = now_ts
            entry["last_message"] = self._format_farm_stop_message(
                str(entry.get("category") or ""),
                str(entry.get("mode") or ""),
                entry["stop_reason"],
                int(entry.get("total_dispatched") or 0),
                entry.get("stamina"),
                detail=detail_msg,
            )
            snap = self._serialize_farm_loop_entry(entry)
            self._record_farm_summary_locked(entry, snap)
            self._farm_loops.pop(pid, None)
            snap_to_log = snap

        if snap_to_log is not None:
            cat_lbl = "RSS Gather" if snap_to_log.get("category") == "rss" else "Map Kills"
            acct = snap_to_log.get("account_label") or f"PID {pid}"
            rsn = str(snap_to_log.get("stop_reason") or "")
            kind = "ok" if rsn in ("daily_limit_reached", "out_of_stamina") and int(snap_to_log.get("total_dispatched") or 0) > 0 else (
                "warn" if rsn not in ("user_stopped", "replaced", "replaced_by_new_loop", "shutdown", "dry_run_complete") else "info"
            )
            self.log(f"[{cat_lbl}] [{acct}] ({snap_to_log.get('mode')}) {snap_to_log.get('last_message')}", kind)
        return snap_to_log

    def _load_farm_client_config(self, account_label: str, role: str) -> dict[str, Any]:
        """Resolve per-client bot configuration safely without mutating global config caches."""
        cfg_root: dict[str, Any] = {}
        if multi_client_bot is not None and hasattr(multi_client_bot, "load_config"):
            try:
                loaded = multi_client_bot.load_config()
                if isinstance(loaded, dict):
                    cfg_root = loaded
            except Exception:
                cfg_root = {}
        if multi_client_bot is not None and hasattr(multi_client_bot, "resolve_client_config"):
            try:
                resolved = multi_client_bot.resolve_client_config(cfg_root, account_label, role)
                if isinstance(resolved, dict):
                    return copy.deepcopy(resolved)
            except Exception:
                pass
        defs = cfg_root.get("client_defaults") if isinstance(cfg_root, dict) else None
        role_cfg = (defs or {}).get(role) if isinstance(defs, dict) else None
        if isinstance(role_cfg, dict):
            return copy.deepcopy(role_cfg)
        return copy.deepcopy(cfg_root) if isinstance(cfg_root, dict) else {}

    @classmethod
    def _normalize_farm_step_result(cls, raw: Any, default_target: str = "") -> dict[str, Any]:
        """Normalize standardized or legacy step return dicts into uniform loop control fields."""
        if not isinstance(raw, dict):
            return {
                "ok": False,
                "status": "error",
                "stop_reason": "invalid_response",
                "dispatched_count": 0,
                "target_counts": {},
                "free_formations": None,
                "usable_formations": None,
                "active_marches": None,
                "total_formations": None,
                "stamina": None,
                "searched_level": None,
                "message": "Invalid step response",
            }

        ok_flag = bool(raw.get("ok", True))
        raw_status = str(raw.get("status") or "").strip().lower()
        raw_stop = str(raw.get("stop_reason") or "").strip()
        raw_reason = str(raw.get("reason") or "").strip()
        raw_err = str(raw.get("error") or "").strip()

        # Count dispatches across standardized and legacy fields
        disp_cnt = _safe_int(raw.get("dispatched_count"), None)
        target_counts: dict[str, int] = {}
        dispatched_field = raw.get("dispatched")
        if isinstance(dispatched_field, list):
            if disp_cnt is None:
                disp_cnt = len(dispatched_field)
            for item in dispatched_field:
                if isinstance(item, dict):
                    rt_raw = str(item.get("resourceType") or item.get("resource_type") or item.get("target") or default_target or "").strip().lower()
                    canon_rss = cls._RSS_CANONICAL_NAMES.get(rt_raw)
                    t_key = canon_rss.lower() if canon_rss else (rt_raw or default_target)
                    if t_key:
                        target_counts[t_key] = target_counts.get(t_key, 0) + 1
        elif isinstance(dispatched_field, dict) and dispatched_field:
            if disp_cnt is None:
                disp_cnt = 1

        if disp_cnt is None:
            m_uuids = raw.get("marched_uuids")
            if isinstance(m_uuids, list) and len(m_uuids) > 0:
                disp_cnt = len(m_uuids)
            else:
                legacy_cnt = 0
                if isinstance(raw.get("hosted"), dict) and raw["hosted"]:
                    legacy_cnt += 1
                joined_val = raw.get("joined")
                if isinstance(joined_val, list):
                    legacy_cnt += len([j for j in joined_val if j])
                elif isinstance(joined_val, dict) and joined_val:
                    legacy_cnt += 1
                if isinstance(raw.get("started_rally"), dict) and raw["started_rally"]:
                    legacy_cnt += 1
                if legacy_cnt == 0 and isinstance(raw.get("marched"), dict) and raw["marched"]:
                    legacy_cnt = 1
                disp_cnt = legacy_cnt

        disp_cnt = max(0, int(disp_cnt or 0))
        if disp_cnt > 0 and not target_counts and default_target:
            target_counts[default_target] = disp_cnt

        free_f = _safe_int(raw.get("free_formations", raw.get("freeFormations")), None)
        usable_f = _safe_int(raw.get("usable_formations"), None)
        total_f = _safe_int(raw.get("total_formations", raw.get("unlockFormations")), None)
        active_m = _safe_int(raw.get("active_marches", raw.get("activeMarches")), None)
        if active_m is None and total_f is not None and free_f is not None and total_f >= free_f:
            active_m = max(0, total_f - free_f)
        stam = _safe_int(raw.get("stamina"), None) if raw.get("stamina") is not None else None
        searched_lv = _safe_int(raw.get("searched_level", raw.get("max_level")), None)

        # Resolve status & stop_reason (supporting both standardized contract and legacy returns)
        status = raw_status
        stop_reason = raw_stop

        if not ok_flag and status not in ("physical_limit", "waiting_for_squad", "searching", "dispatched"):
            probe_err = f"{raw_stop} {raw_reason} {raw_err}".lower()
            if any(tok in probe_err for tok in ("client_offline", "not running", "no process", "process exited", "detached", "session closed", "target process")):
                status = "physical_limit"
                stop_reason = "client_offline"
            else:
                status = "error"
                stop_reason = raw_stop or raw_err or raw_reason or "step_error"
        elif status not in ("dispatched", "waiting_for_squad", "searching", "physical_limit", "error"):
            if disp_cnt > 0:
                status = "dispatched"
                stop_reason = ""
            else:
                r_low = (raw_stop or raw_reason or str(raw.get("action") or "")).strip().lower()
                if r_low in ("below_min_stamina", "out_of_stamina", "insufficient_stamina"):
                    status = "physical_limit"
                    stop_reason = "out_of_stamina"
                elif r_low == "not_in_alliance":
                    status = "physical_limit"
                    stop_reason = "not_in_alliance"
                elif r_low in ("daily_4x_limit_reached", "daily_limit_reached"):
                    status = "physical_limit"
                    stop_reason = "daily_limit_reached"
                elif r_low in ("event_ended",):
                    status = "physical_limit"
                    stop_reason = "event_ended"
                elif r_low in ("event_not_active", "outside_0300_window", "not_detected", "roaming_boss_manager_unavailable"):
                    status = "physical_limit"
                    stop_reason = "not_detected"
                elif r_low in ("no_troops_or_formations", "client_offline", "no_targets_found"):
                    status = "physical_limit"
                    stop_reason = r_low
                elif r_low in (
                    "no_boomer_in_viewport_requested_scan",
                    "no_matching_unoccupied_tile_in_viewport",
                    "no_furylord_target",
                    "searching",
                ) or bool(raw.get("summoned")):
                    status = "searching"
                    stop_reason = ""
                elif r_low in ("f1_busy_waiting_return", "all_squads_busy", "waiting_for_squad"):
                    status = "waiting_for_squad"
                    stop_reason = ""
                elif r_low == "no_free_formation_above_reserve":
                    if active_m is not None and active_m == 0:
                        status = "physical_limit"
                        stop_reason = "no_troops_or_formations"
                    else:
                        status = "waiting_for_squad"
                        stop_reason = ""
                elif "is_open" in raw:
                    if not raw.get("is_open") or ("in_battle" in raw and not raw.get("in_battle")):
                        status = "physical_limit"
                        stop_reason = "not_detected"
                    else:
                        status = "waiting_for_squad"
                        stop_reason = ""
                else:
                    status = "physical_limit"
                    stop_reason = raw_stop or raw_reason or "no_targets_found"

        if status == "physical_limit" and not stop_reason:
            stop_reason = raw_reason or "no_targets_found"
        elif status not in ("physical_limit", "error"):
            stop_reason = ""

        msg = str(raw.get("message") or raw.get("msg") or "").strip()
        if not msg:
            if status == "dispatched":
                msg = f"Dispatched {disp_cnt} squad(s)."
            elif status == "waiting_for_squad":
                msg = "All usable squads are marching - waiting for a squad to return..."
            elif status == "searching":
                lv_note = f" (Lv{searched_lv})" if searched_lv else ""
                msg = f"Scanning world map for targets{lv_note}..."
            elif status == "error":
                msg = raw_err or stop_reason or "Step execution error"
            else:
                msg = stop_reason.replace("_", " ").capitalize()

        return {
            "ok": ok_flag,
            "status": status,
            "stop_reason": stop_reason,
            "dispatched_count": disp_cnt,
            "target_counts": target_counts,
            "free_formations": free_f,
            "usable_formations": usable_f,
            "active_marches": active_m,
            "total_formations": total_f,
            "stamina": stam,
            "searched_level": searched_lv,
            "message": msg,
        }

    @staticmethod
    def _next_step_down_level(cur_lv: int, min_lv: int, empty_searches: int, max_empty: int = 4) -> int:
        if cur_lv <= min_lv:
            return min_lv
        rem = max(1, max_empty - empty_searches)
        drop = max(1, math.ceil((cur_lv - min_lv) / rem))
        return max(min_lv, cur_lv - drop)

    @staticmethod
    def _prune_timed_claims(claims_map: dict[str, float], now_ts: float, ttl_sec: float = 90.0) -> list[str]:
        expired = [k for k, ts in list(claims_map.items()) if (now_ts - ts) > ttl_sec]
        for k in expired:
            claims_map.pop(k, None)
        if len(claims_map) > 96:
            oldest = sorted(list(claims_map.items()), key=lambda kv: kv[1])[: len(claims_map) - 96]
            for k, _ in oldest:
                claims_map.pop(k, None)
        return list(claims_map.keys())

    @staticmethod
    def _record_timed_claims(claims_map: dict[str, float], ctx_list: Any, raw_res: Any, now_ts: float) -> None:
        if isinstance(ctx_list, list):
            for k in ctx_list:
                ks = str(k or "").strip()
                if ks and ks not in claims_map:
                    claims_map[ks] = now_ts
        if isinstance(raw_res, dict) and isinstance(raw_res.get("dispatched"), list):
            for item in raw_res["dispatched"]:
                if isinstance(item, dict):
                    ck = str(item.get("claimKey") or "").strip()
                    if ck and ck not in claims_map:
                        claims_map[ck] = now_ts

    def _update_farm_loop_telemetry(
        self,
        entry: dict[str, Any],
        norm_res: dict[str, Any],
        *,
        new_state: str,
        message: str | None = None,
    ) -> int:
        """Thread-safely update loop counters and squad/stamina telemetry from a normalized step result."""
        flock = self._ensure_farm_loop_attrs()
        now_ts = time.time()
        disp_cnt = int(norm_res.get("dispatched_count") or 0)
        with flock:
            entry["iterations"] = int(entry.get("iterations") or 0) + 1
            entry["updated_at"] = now_ts
            entry["state"] = new_state
            if disp_cnt > 0:
                entry["total_dispatched"] = int(entry.get("total_dispatched") or 0) + disp_cnt
                bt = entry.setdefault("by_target", {})
                for tk, tv in (norm_res.get("target_counts") or {}).items():
                    bt[str(tk)] = int(bt.get(str(tk), 0)) + int(tv)
            if norm_res.get("stamina") is not None:
                entry["stamina"] = int(norm_res["stamina"])
            if norm_res.get("free_formations") is not None:
                entry["free_formations"] = int(norm_res["free_formations"])
            if norm_res.get("active_marches") is not None:
                entry["active_marches"] = int(norm_res["active_marches"])
            if norm_res.get("total_formations") is not None:
                entry["total_formations"] = int(norm_res["total_formations"])
            if message is not None:
                entry["last_message"] = str(message)
            elif norm_res.get("message"):
                entry["last_message"] = str(norm_res["message"])
            return int(entry.get("total_dispatched") or 0)

    @staticmethod
    def _coerce_optional_pid(pid: Any) -> Any:
        """Normalize empty/zero/'auto' PID inputs to None while preserving explicit PIDs for strict validation."""
        if pid is None or pid == "" or pid == 0:
            return None
        if isinstance(pid, str) and pid.strip().lower() in ("", "0", "auto", "none", "null"):
            return None
        return pid

    def start_rss_gather_loop(
        self,
        resource_type: str = "diamonds",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Start continuous repeat-until-can't RSS gathering on the target Last Z client."""
        norm_mode = str(resource_type or "diamonds").strip().lower()
        if norm_mode not in self._VALID_RSS_LOOP_MODES:
            return {
                "ok": False,
                "error": f"Invalid resource_type '{resource_type}'. Expected one of: {', '.join(self._VALID_RSS_LOOP_MODES)}.",
            }

        opts = dict(options) if isinstance(options, dict) else {}
        raw_pid = self._coerce_optional_pid(opts.get("pid"))
        _, target_pid, proc, account_label, _ = self._resolve_client_context(raw_pid)
        if not target_pid or proc is None:
            return {"ok": False, "error": "No running Last Z client found."}
        if bot_actions is None or client_discovery is None:
            return {"ok": False, "error": "Automation modules unavailable."}

        min_lv = max(1, min(15, _safe_int(opts.get("min_level"), 1)))
        max_lv = max(1, min(15, _safe_int(opts.get("max_level"), 15)))
        if min_lv > max_lv:
            min_lv, max_lv = max_lv, min_lv
        max_dist = max(10.0, min(2000.0, _safe_float(opts.get("max_distance"), 150.0)))
        reserve = max(0, min(10, _safe_int(opts.get("reserve"), 0)))
        dry_run = bool(opts.get("dry_run", False))

        default_prio = ["Diamonds", "Electricity", "Zent", "Wood", "Food"]
        raw_prio = opts.get("priority")
        clean_prio: list[str] = []
        if raw_prio is None:
            clean_prio = list(default_prio)
        else:
            if isinstance(raw_prio, str):
                seq_prio = [x.strip() for x in raw_prio.split(",") if x.strip()]
            elif isinstance(raw_prio, (list, tuple)):
                seq_prio = [str(x).strip() for x in raw_prio if str(x).strip()]
            else:
                seq_prio = []
            for item in seq_prio:
                canon = self._RSS_CANONICAL_NAMES.get(item.lower())
                if canon and canon not in clean_prio:
                    clean_prio.append(canon)
            if norm_mode == "priority_queue" and not clean_prio:
                return {"ok": False, "error": "Select at least one valid resource for Priority Queue."}
            if not clean_prio:
                clean_prio = list(default_prio)

        clean_opts: dict[str, Any] = {
            "min_level": min_lv,
            "max_level": max_lv,
            "max_distance": max_dist,
            "reserve": reserve,
            "priority": clean_prio,
            "dry_run": dry_run,
        }
        for delay_k in ("_dispatch_delay_sec", "_wait_squad_delay_sec", "_search_delay_sec", "_exhausted_backoff_sec"):
            if delay_k in opts:
                clean_opts[delay_k] = max(0.0, _safe_float(opts.get(delay_k), 0.0))

        pid_int = int(target_pid)
        acct_lbl = str(account_label or proc.get("label") or f"PID {pid_int}")
        role = str(proc.get("role") or "farm").lower()

        flock = self._ensure_farm_loop_attrs()
        stop_ev = threading.Event()
        now_ts = time.time()
        mode_desc = f"Priority Queue ({' -> '.join(clean_prio)})" if norm_mode == "priority_queue" else self._RSS_CANONICAL_NAMES[norm_mode]

        # Atomically signal/replace any existing loop on this PID AND register the new loop under ONE lock
        replaced: tuple[dict[str, Any], Any, dict[str, Any]] | None = None
        with flock:
            replaced = self._detach_farm_loop_locked(pid_int, "replaced", now_ts)
            self._farm_loop_seq += 1
            loop_id = f"rss-{self._farm_loop_seq}"
            entry: dict[str, Any] = {
                "loop_id": loop_id,
                "pid": pid_int,
                "account_label": acct_lbl,
                "role": role,
                "category": "rss",
                "mode": norm_mode,
                "running": True,
                "state": "running",
                "started_at": now_ts,
                "updated_at": now_ts,
                "iterations": 0,
                "total_dispatched": 0,
                "by_target": {},
                "last_message": f"Starting {mode_desc} gathering (Lv{min_lv}-{max_lv}, dist<={int(max_dist)})...",
                "stop_reason": "",
                "stamina": None,
                "free_formations": 0,
                "active_marches": 0,
                "total_formations": 0,
                "options": clean_opts,
                "stop_event": stop_ev,
                "thread": None,
            }
            worker = threading.Thread(
                target=self._rss_gather_loop_worker,
                args=(entry,),
                daemon=True,
                name=f"FarmLoop-RSS-{pid_int}-{self._farm_loop_seq}",
            )
            entry["thread"] = worker
            self._farm_loops[pid_int] = entry
            loop_snap = self._serialize_farm_loop_entry(entry)

        replaced_snap = self._finish_farm_loop_replacement(replaced, "RSS Gather", acct_lbl)
        # New worker serializes on the per-PID exec lock, so it can never overlap a slow old worker's Frida step
        worker.start()
        self.log(
            f"[RSS Gather] [{acct_lbl}] Started continuous repeat gathering: {mode_desc} (Lv{min_lv}-{max_lv}, reserve={reserve}).",
            "ok",
        )
        return {
            "ok": True,
            "loop_id": loop_id,
            "pid": pid_int,
            "account_label": acct_lbl,
            "category": "rss",
            "mode": norm_mode,
            "loop": loop_snap,
            "replaced_loop": replaced_snap,
            "farm_loops": self.get_farm_loops_state(),
        }

    def _finish_farm_loop_replacement(
        self,
        replaced: tuple[dict[str, Any], Any, dict[str, Any]] | None,
        new_cat_lbl: str,
        acct_lbl: str,
    ) -> dict[str, Any] | None:
        """Briefly join a replaced worker (outside the farm lock) and log which loop was switched off."""
        if replaced is None:
            return None
        _old_entry, old_th, old_snap = replaced
        if old_th is not None and old_th is not threading.current_thread() and getattr(old_th, "is_alive", lambda: False)():
            try:
                old_th.join(timeout=0.8)
            except Exception:
                pass
        old_cat = "RSS Gather" if old_snap.get("category") == "rss" else "Map Kills"
        self.log(
            f"[{new_cat_lbl}] [{acct_lbl}] Replaced running {old_cat} loop ({old_snap.get('mode')}) on this account "
            f"after {int(old_snap.get('total_dispatched') or 0)} dispatch(es) - one loop per account.",
            "info",
        )
        return old_snap

    def _rss_gather_loop_worker(self, entry: dict[str, Any]) -> None:
        """Background daemon worker repeating RSS gathering until physically unable or stopped."""
        pid = int(entry["pid"])
        acct_lbl = str(entry.get("account_label") or f"PID {pid}")
        role = str(entry.get("role") or "farm")
        mode = str(entry.get("mode") or "diamonds")
        opts = dict(entry.get("options") or {})
        stop_ev: threading.Event = entry["stop_event"]

        min_lv = int(opts.get("min_level", 1))
        max_lv = int(opts.get("max_level", 15))
        max_dist = float(opts.get("max_distance", 150.0))
        reserve = int(opts.get("reserve", 0))
        dry_run = bool(opts.get("dry_run", False))
        dispatch_delay = float(opts.get("_dispatch_delay_sec", 2.0))
        wait_squad_delay = float(opts.get("_wait_squad_delay_sec", 5.0))
        search_delay = float(opts.get("_search_delay_sec", 2.5))
        exhausted_backoff = float(opts.get("_exhausted_backoff_sec", 60.0))

        queue: list[str] = (
            list(opts.get("priority") or ["Diamonds", "Electricity", "Zent", "Wood", "Food"])
            if mode == "priority_queue"
            else [self._RSS_CANONICAL_NAMES.get(mode, "Diamonds")]
        )
        q_idx = 0
        cur_search_lv = max_lv
        empty_searches = 0
        consecutive_errors = 0
        exhausted_in_wave: set[str] = set()
        pid_state = self._get_farm_pid_state(pid)
        reject_tracker: dict[str, Any] = {"last": {}, "consecutive": 0}
        client_state: dict[str, Any] = self._build_farm_client_state(pid, acct_lbl)
        logged_waiting = False
        dry_steps = 0
        last_active_marches = 0

        stop_reason = "user_stopped"
        detail_msg = ""

        def _advance_queue() -> bool:
            """Mark current resource exhausted; move to next. Returns False when the whole wave is exhausted."""
            nonlocal q_idx, cur_search_lv, empty_searches
            exhausted_in_wave.add(queue[q_idx % len(queue)])
            cur_search_lv = max_lv
            empty_searches = 0
            if len(exhausted_in_wave) >= len(queue):
                return False
            for offset in range(1, len(queue) + 1):
                cand_idx = (q_idx + offset) % len(queue)
                if queue[cand_idx] not in exhausted_in_wave:
                    q_idx = cand_idx
                    break
            return True

        try:
            ccfg = self._load_farm_client_config(acct_lbl, role)
            while not stop_ev.is_set() and getattr(self, "is_monitoring", True):
                ba = bot_actions
                cd = client_discovery
                if ba is None or cd is None:
                    stop_reason = "automation_unavailable"
                    detail_msg = "Automation modules unavailable"
                    break

                cur_res = queue[q_idx % len(queue)]
                cur_res_key = cur_res.lower()

                step_cfg = copy.deepcopy(ccfg)
                step_cfg["formation_reserve"] = reserve
                ag_cfg = dict(step_cfg.get("auto_gather") or {})
                ag_cfg.update({
                    "resource_priority": [cur_res],
                    "min_level": min_lv,
                    "max_level": max_lv,
                    "max_distance": max_dist,
                })
                step_cfg["auto_gather"] = ag_cfg

                # Per-PID exec lock: a rapid Stop->Start can never run two workers' Frida steps concurrently
                exec_lock = self._acquire_farm_exec_lock(pid, stop_ev)
                if exec_lock is None:
                    break
                try:
                    step_ctx: dict[str, Any] = self._prepare_claims_context(pid_state, ("gather",), time.monotonic())
                    try:
                        step_fn = getattr(ba, "run_rss_gather_step", None)
                        if callable(step_fn):
                            raw_res = step_fn(
                                cd,
                                pid,
                                client_state,
                                step_cfg,
                                resource_type=cur_res,
                                min_level=min_lv,
                                max_level=max_lv,
                                max_distance=max_dist,
                                reserve=reserve,
                                search_level=cur_search_lv,
                                dry_run=dry_run,
                                context=step_ctx,
                            )
                        else:
                            legacy_fn = getattr(ba, "run_auto_gather", None)
                            if not callable(legacy_fn):
                                stop_reason = "automation_unavailable"
                                detail_msg = "run_rss_gather_step unavailable"
                                break
                            raw_res = legacy_fn(cd, pid, client_state, step_cfg, dry_run=dry_run, context=step_ctx)
                    except Exception as exc:
                        raw_res = {"ok": False, "status": "error", "error": str(exc)}
                    if not dry_run:
                        self._record_claims_context(pid_state, ("gather",), step_ctx, raw_res, time.monotonic())
                finally:
                    exec_lock.release()

                norm = self._normalize_farm_step_result(raw_res, default_target=cur_res_key)
                if stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                    stop_reason = "user_stopped" if stop_ev.is_set() else "shutdown"
                    break
                rej = self._check_phantom_dispatch(entry, reject_tracker, pid_state, raw_res, norm, cur_res_key) if not dry_run else {"phantoms": 0}
                st = norm["status"]
                rsn = norm["stop_reason"]
                if norm.get("active_marches") is not None:
                    last_active_marches = int(norm["active_marches"])

                if dry_run:
                    dry_steps += 1

                if int(rej.get("phantoms") or 0) > 0:
                    n_rej = int(rej.get("consecutive") or 0)
                    tgt_note = ", ".join(str(t) for t in (rej.get("targets") or [])[:3]) or "target"
                    rej_msg = (
                        f"Game rejected march to {cur_res} ({tgt_note}) - same squad still idle. "
                        f"Blacklisted target for {int(self._FARM_BLACKLIST_TTL_SEC // 60)} min ({n_rej}/{self._FARM_MAX_REJECTS})."
                    )
                    self.log(f"[RSS Gather] [{acct_lbl}] {rej_msg}", "warn")
                    if n_rej >= self._FARM_MAX_REJECTS:
                        self._update_farm_loop_telemetry(entry, norm, new_state="running", message=rej_msg)
                        stop_reason = "dispatch_rejected"
                        detail_msg = rej_msg
                        break
                    if st == "rejected":
                        self._update_farm_loop_telemetry(entry, norm, new_state="searching", message=rej_msg)
                        if stop_ev.wait(search_delay):
                            break
                        continue

                if st == "dispatched":
                    consecutive_errors = 0
                    empty_searches = 0
                    cur_search_lv = max_lv
                    logged_waiting = False
                    disp_n = int(norm["dispatched_count"])
                    tot_disp = self._update_farm_loop_telemetry(
                        entry,
                        norm,
                        new_state="running",
                        message=norm.get("message") or f"Dispatched {disp_n} squad(s) to {cur_res}.",
                    )
                    self.log(
                        f"[RSS Gather] [{acct_lbl}] {'[DRY RUN] Would dispatch' if dry_run else 'Dispatched'} {disp_n} squad(s) to {cur_res} (session total: {tot_disp}).",
                        "ok",
                    )
                    if dry_run:
                        if dry_steps >= len(queue) or not _advance_queue():
                            stop_reason = "dry_run_complete"
                            break
                        continue
                    if stop_ev.wait(dispatch_delay):
                        break
                    continue

                if st == "waiting_for_squad":
                    consecutive_errors = 0
                    empty_searches = 0
                    cur_search_lv = max_lv
                    # Reset queue priority so when a squad returns home, highest-priority resources are checked first
                    q_idx = 0
                    exhausted_in_wave.clear()
                    act_m = norm.get("active_marches")
                    tot_f = norm.get("total_formations")
                    occ_note = f" ({act_m}/{tot_f} marching)" if (act_m is not None and tot_f) else ""
                    wait_msg = f"All usable squads busy{occ_note} - waiting for a squad to return..."
                    self._update_farm_loop_telemetry(entry, norm, new_state="waiting_for_squad", message=wait_msg)
                    if not logged_waiting:
                        logged_waiting = True
                        self.log(f"[RSS Gather] [{acct_lbl}] {wait_msg}", "info")
                    if dry_run:
                        stop_reason = "dry_run_complete"
                        break
                    if stop_ev.wait(wait_squad_delay):
                        break
                    continue

                exhausted_now = False
                if st == "searching":
                    consecutive_errors = 0
                    logged_waiting = False
                    empty_searches += 1
                    if dry_run and dry_steps >= len(queue):
                        stop_reason = "dry_run_complete"
                        break
                    if empty_searches == 4:
                        # 4th (min level) search was just sent: wait for it to land, then run ONE verification scan
                        verify_msg = f"Final Lv{cur_search_lv} search sent for {cur_res} - verifying results before giving up..."
                        self._update_farm_loop_telemetry(entry, norm, new_state="searching", message=verify_msg)
                        if stop_ev.wait(max(2.5, search_delay)):
                            break
                        continue
                    if empty_searches > 4:
                        exhausted_now = True
                    else:
                        next_lv = self._next_step_down_level(cur_search_lv, min_lv, empty_searches, max_empty=4)
                        search_msg = f"Searching for unoccupied {cur_res} tiles (Lv{cur_search_lv} -> Lv{next_lv}, scan {empty_searches}/4)..."
                        cur_search_lv = next_lv
                        self._update_farm_loop_telemetry(entry, norm, new_state="searching", message=search_msg)
                        if stop_ev.wait(search_delay):
                            break
                        continue

                if st == "physical_limit" and rsn == "no_targets_found":
                    exhausted_now = True

                if exhausted_now:
                    if mode == "priority_queue" and _advance_queue():
                        next_res = queue[q_idx % len(queue)]
                        self._update_farm_loop_telemetry(
                            entry,
                            norm,
                            new_state="searching",
                            message=f"No open {cur_res} tiles found - advancing priority queue to {next_res}...",
                        )
                        continue
                    if dry_run:
                        stop_reason = "dry_run_complete"
                        break
                    act_now = norm.get("active_marches")
                    act_now = last_active_marches if act_now is None else int(act_now)
                    if act_now > 0:
                        # Never stop while squads are still out: wait for them, then re-run the full search cycle
                        q_idx = 0
                        exhausted_in_wave.clear()
                        cur_search_lv = max_lv
                        empty_searches = 0
                        wait_msg = (
                            f"No open tiles found right now - {act_now} squad(s) still out. "
                            f"Waiting for squads to return, re-searching in {int(exhausted_backoff)}s..."
                        )
                        self._update_farm_loop_telemetry(entry, norm, new_state="waiting_for_squad", message=wait_msg)
                        self.log(f"[RSS Gather] [{acct_lbl}] {wait_msg}", "info")
                        if stop_ev.wait(exhausted_backoff):
                            break
                        continue
                    self._update_farm_loop_telemetry(entry, norm, new_state="running")
                    stop_reason = "no_targets_found"
                    break

                if st == "physical_limit":
                    self._update_farm_loop_telemetry(entry, norm, new_state="running")
                    stop_reason = rsn or "no_targets_found"
                    detail_msg = str(norm.get("message") or "")
                    break

                # Error handling: up to 3 consecutive errors before stopping
                consecutive_errors += 1
                err_txt = str(norm.get("message") or rsn or "RPC error")
                self._update_farm_loop_telemetry(
                    entry,
                    norm,
                    new_state="running",
                    message=f"Retry {consecutive_errors}/3 after error: {err_txt}",
                )
                if consecutive_errors >= 3:
                    stop_reason = rsn or "consecutive_errors"
                    detail_msg = err_txt
                    break
                if stop_ev.wait(search_delay):
                    break
        finally:
            if stop_ev.is_set() and stop_reason not in ("replaced", "replaced_by_new_loop", "shutdown"):
                stop_reason = "user_stopped"
            elif not getattr(self, "is_monitoring", True):
                stop_reason = "shutdown"
            self._finalize_farm_loop_worker(entry, stop_reason=stop_reason, final_state="stopped", detail_msg=detail_msg)

    def stop_rss_gather_loop(self, pid: int | None = None) -> dict[str, Any]:
        """Stop active RSS gathering repeat loop (for explicit PID or all active RSS loops)."""
        norm_pid = self._coerce_optional_pid(pid)
        explicit_pid = _safe_int(norm_pid, -1) if norm_pid is not None else None
        stopped = self._stop_farm_loops_internal(
            pid=explicit_pid,
            category="rss",
            reason="user_stopped",
            join_timeout=0.5,
            log_stop=True,
        )
        return {
            "ok": True,
            "stopped": len(stopped) > 0,
            "stopped_pids": [int(s["pid"]) for s in stopped if s.get("pid") is not None],
            "farm_loops": self.get_farm_loops_state(),
        }

    def _normalize_kill_detection_payload(
        self,
        raw: Any,
        pid: int,
        account_label: str,
    ) -> dict[str, Any]:
        base = self._default_kill_detection_dict()
        base["pid"] = int(pid)
        base["account_label"] = str(account_label or f"PID {pid}")
        base["updated_at"] = time.time()
        if not isinstance(raw, dict):
            base["ok"] = False
            base["error"] = "Invalid detection response"
            return base
        if not raw.get("ok", True):
            base["ok"] = False
            base["error"] = str(raw.get("error") or raw.get("reason") or "Detection failed")
            return base

        base["ok"] = True
        if raw.get("stamina") is not None:
            base["stamina"] = _safe_int(raw.get("stamina"), 0)
        free_f = _safe_int(raw.get("free_formations", raw.get("freeFormations")), 0)
        tot_f = _safe_int(raw.get("total_formations", raw.get("unlockFormations")), 0)
        act_m = _safe_int(raw.get("active_marches", raw.get("activeMarches")), None)
        if act_m is None and tot_f >= free_f:
            act_m = max(0, tot_f - free_f)
        base["free_formations"] = free_f
        base["total_formations"] = tot_f
        base["active_marches"] = int(act_m or 0)
        base["in_alliance"] = bool(raw.get("in_alliance", raw.get("inAlliance", False)))
        base["max_npc_level"] = _safe_int(raw.get("max_npc_level"), 0)
        base["max_boomer_level"] = _safe_int(raw.get("max_boomer_level"), 0)
        base["rest_boomer_kills"] = _safe_int(raw.get("rest_boomer_kills"), 0)

        b_in = _as_dict(raw.get("boomers"))
        base["boomers"] = {
            "detected": bool(b_in.get("detected", base["in_alliance"])),
            "open_rallies": _safe_int(b_in.get("open_rallies"), 0),
            "viewport_count": _safe_int(b_in.get("viewport_count"), 0),
        }
        n_in = _as_dict(raw.get("standalone_npc"))
        npc_max = _safe_int(n_in.get("max_level"), base["max_npc_level"])
        base["standalone_npc"] = {
            "detected": bool(n_in.get("detected", True)),
            "viewport_count": _safe_int(n_in.get("viewport_count"), 0),
            "max_level": npc_max,
        }
        s_in = _as_dict(raw.get("saga"))
        s_active = bool(s_in.get("active", False))
        s_bosses = _safe_int(s_in.get("boss_count"), 0)
        base["saga"] = {
            "detected": bool(s_in.get("detected", s_active or s_bosses > 0)),
            "active": s_active,
            "act_id": _safe_int(s_in.get("act_id"), 0),
            "boss_count": s_bosses,
            "difficulty_selected": bool(s_in.get("difficulty_selected", False)),
        }
        t_in = _as_dict(raw.get("tyrant"))
        t_open = bool(t_in.get("is_open", False))
        t_battle = bool(t_in.get("in_battle", False))
        base["tyrant"] = {
            "detected": bool(t_in.get("detected", t_open and t_battle)),
            "is_open": t_open,
            "in_battle": t_battle,
            "boss_point_id": _safe_int(t_in.get("boss_point_id"), 0),
        }
        f_in = _as_dict(raw.get("furylord"))
        f_open = bool(f_in.get("is_open", False))
        f_act = bool(f_in.get("in_act", False))
        f_bosses = _safe_int(f_in.get("boss_count"), 0)
        base["furylord"] = {
            "detected": bool(f_in.get("detected", f_open or f_act or f_bosses > 0)),
            "is_open": f_open,
            "in_act": f_act,
            "boss_count": f_bosses,
            "reward_count": _safe_int(f_in.get("reward_count"), 0),
            "max_reward_count": _safe_int(f_in.get("max_reward_count"), 4),
        }
        return base

    def probe_map_kills_status(
        self,
        pid: int | None = None,
        max_age_sec: float = 0.0,
    ) -> dict[str, Any]:
        """Probe live read-only Map Kills target availability, stamina, and squad counts."""
        flock = self._ensure_farm_loop_attrs()
        norm_pid = self._coerce_optional_pid(pid)
        _, target_pid, proc, account_label, _ = self._resolve_client_context(norm_pid)
        if not target_pid or proc is None:
            offline = self._default_kill_detection_dict()
            offline["ok"] = False
            offline["updated_at"] = time.time()
            offline["error"] = "No running Last Z client found."
            off_pid = _safe_int(norm_pid if norm_pid is not None else target_pid, None)
            if off_pid is not None and off_pid > 0:
                offline["pid"] = int(off_pid)
            with flock:
                self._last_kill_detection = copy.deepcopy(offline)
                if off_pid is not None and off_pid > 0:
                    self._last_kill_detection_by_pid[int(off_pid)] = copy.deepcopy(offline)
            return offline

        pid_int = int(target_pid)
        acct_lbl = str(account_label or proc.get("label") or f"PID {pid_int}")
        if max_age_sec > 0.0:
            with flock:
                cached = self._last_kill_detection_by_pid.get(pid_int)
                if (
                    isinstance(cached, dict)
                    and cached.get("ok")
                    and _safe_int(cached.get("pid"), 0) == pid_int
                    and (time.time() - float(cached.get("updated_at") or 0.0)) <= max_age_sec
                ):
                    return copy.deepcopy(cached)

        ba = bot_actions
        cd = client_discovery
        if ba is None or cd is None:
            err_res = self._default_kill_detection_dict()
            err_res["pid"] = pid_int
            err_res["account_label"] = acct_lbl
            err_res["ok"] = False
            err_res["updated_at"] = time.time()
            err_res["error"] = "Automation modules unavailable."
            with flock:
                self._last_kill_detection = copy.deepcopy(err_res)
                self._last_kill_detection_by_pid[pid_int] = copy.deepcopy(err_res)
            return err_res

        raw_det: Any = None
        det_fn = getattr(ba, "detect_map_kill_targets", None)
        try:
            if callable(det_fn):
                raw_det = det_fn(cd, pid_int)
            else:
                snap_fn = getattr(ba, "snapshot_client", None)
                if callable(snap_fn):
                    raw_det = snap_fn(cd, pid_int)
                else:
                    raw_det = {"ok": False, "error": "detect_map_kill_targets unavailable"}
        except Exception as exc:
            raw_det = {"ok": False, "error": str(exc)}

        clean_det = self._normalize_kill_detection_payload(raw_det, pid_int, acct_lbl)
        with flock:
            self._last_kill_detection = copy.deepcopy(clean_det)
            self._last_kill_detection_by_pid[pid_int] = copy.deepcopy(clean_det)
            if len(self._last_kill_detection_by_pid) > 16:
                for old_pid in sorted(
                    self._last_kill_detection_by_pid,
                    key=lambda p: float((self._last_kill_detection_by_pid.get(p) or {}).get("updated_at") or 0.0),
                )[: len(self._last_kill_detection_by_pid) - 16]:
                    self._last_kill_detection_by_pid.pop(old_pid, None)
            cur_loop = self._farm_loops.get(pid_int)
            if isinstance(cur_loop, dict) and clean_det.get("ok"):
                if clean_det.get("stamina") is not None:
                    cur_loop["stamina"] = clean_det["stamina"]
                cur_loop["free_formations"] = int(clean_det.get("free_formations") or 0)
                cur_loop["active_marches"] = int(clean_det.get("active_marches") or 0)
                cur_loop["total_formations"] = int(clean_det.get("total_formations") or 0)
        return clean_det

    def start_map_kills_loop(
        self,
        mode: str = "boomers",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Start continuous repeat-until-can't Map Kills hunting on the target Last Z client."""
        norm_mode = str(mode or "boomers").strip().lower()
        if norm_mode not in self._VALID_KILL_LOOP_MODES:
            return {
                "ok": False,
                "error": f"Invalid mode '{mode}'. Expected one of: {', '.join(self._VALID_KILL_LOOP_MODES)}.",
            }

        opts = dict(options) if isinstance(options, dict) else {}
        raw_pid = self._coerce_optional_pid(opts.get("pid"))
        _, target_pid, proc, account_label, _ = self._resolve_client_context(raw_pid)
        if not target_pid or proc is None:
            return {"ok": False, "error": "No running Last Z client found."}
        if bot_actions is None or client_discovery is None:
            return {"ok": False, "error": "Automation modules unavailable."}

        min_stamina = max(0, min(5000, _safe_int(opts.get("min_stamina"), 0)))
        reserve = max(0, min(10, _safe_int(opts.get("reserve"), 0)))
        max_dist = max(10.0, min(2000.0, _safe_float(opts.get("max_distance"), 150.0)))
        boomer_min = max(1, min(20, _safe_int(opts.get("boomer_min_level", opts.get("min_level", 1)), 1)))
        boomer_max = max(1, min(20, _safe_int(opts.get("boomer_max_level", opts.get("max_level", 5)), 5)))
        if boomer_min > boomer_max:
            boomer_min, boomer_max = boomer_max, boomer_min
        npc_min = max(0, min(60, _safe_int(opts.get("npc_min_level"), 0)))
        npc_max = max(0, min(60, _safe_int(opts.get("npc_max_level"), 0)))
        if npc_max > 0 and npc_min > npc_max:
            npc_min = npc_max
        allow_summon_saga = bool(opts.get("allow_summon_saga", opts.get("allow_summon", True)))
        prioritize_bosses = bool(opts.get("prioritize_detected_bosses", False))
        dry_run = bool(opts.get("dry_run", False))

        default_chain = ["boomers", "standalone_npc", "saga", "tyrant", "furylord"]
        raw_chain = opts.get("chain")
        clean_chain: list[str] = []
        if raw_chain is None:
            clean_chain = list(default_chain)
        else:
            if isinstance(raw_chain, str):
                seq_chain = [x.strip() for x in raw_chain.split(",") if x.strip()]
            elif isinstance(raw_chain, (list, tuple)):
                seq_chain = [str(x).strip() for x in raw_chain if str(x).strip()]
            else:
                seq_chain = []
            for item in seq_chain:
                canon_m = self._KILL_CHAIN_ALIASES.get(item.lower())
                if canon_m and canon_m not in clean_chain:
                    clean_chain.append(canon_m)
            if norm_mode == "all_chain" and not clean_chain:
                return {"ok": False, "error": "Select at least one target mode for the Map Kills chain."}
            if not clean_chain:
                clean_chain = list(default_chain)

        clean_opts: dict[str, Any] = {
            "min_stamina": min_stamina,
            "reserve": reserve,
            "max_distance": max_dist,
            "boomer_min_level": boomer_min,
            "boomer_max_level": boomer_max,
            "npc_min_level": npc_min,
            "npc_max_level": npc_max,
            "allow_summon_saga": allow_summon_saga,
            "chain": clean_chain,
            "prioritize_detected_bosses": prioritize_bosses,
            "dry_run": dry_run,
        }
        for delay_k in ("_dispatch_delay_sec", "_wait_squad_delay_sec", "_search_delay_sec", "_probe_interval_sec", "_exhausted_backoff_sec"):
            if delay_k in opts:
                clean_opts[delay_k] = max(0.0, _safe_float(opts.get(delay_k), 0.0))

        pid_int = int(target_pid)
        acct_lbl = str(account_label or proc.get("label") or f"PID {pid_int}")
        role = str(proc.get("role") or "farm").lower()

        flock = self._ensure_farm_loop_attrs()
        stop_ev = threading.Event()
        now_ts = time.time()
        mode_labels = {
            "boomers": "Boomers (Rallies)",
            "standalone_npc": "Standalone NPC",
            "saga": "Saga Zombies",
            "tyrant": "The Tyrant",
            "furylord": "Furylord",
            "all_chain": f"Priority Chain ({' -> '.join(clean_chain)})",
        }
        mode_desc = mode_labels.get(norm_mode, norm_mode)

        # Atomically signal/replace any existing loop on this PID AND register the new loop under ONE lock
        replaced: tuple[dict[str, Any], Any, dict[str, Any]] | None = None
        with flock:
            replaced = self._detach_farm_loop_locked(pid_int, "replaced", now_ts)
            self._farm_loop_seq += 1
            loop_id = f"kills-{self._farm_loop_seq}"
            entry: dict[str, Any] = {
                "loop_id": loop_id,
                "pid": pid_int,
                "account_label": acct_lbl,
                "role": role,
                "category": "kills",
                "mode": norm_mode,
                "running": True,
                "state": "running",
                "started_at": now_ts,
                "updated_at": now_ts,
                "iterations": 0,
                "total_dispatched": 0,
                "by_target": {},
                "last_message": f"Starting {mode_desc} hunting (min stamina={min_stamina}, reserve={reserve})...",
                "stop_reason": "",
                "stamina": None,
                "free_formations": 0,
                "active_marches": 0,
                "total_formations": 0,
                "options": clean_opts,
                "stop_event": stop_ev,
                "thread": None,
            }
            worker = threading.Thread(
                target=self._map_kills_loop_worker,
                args=(entry,),
                daemon=True,
                name=f"FarmLoop-Kills-{pid_int}-{self._farm_loop_seq}",
            )
            entry["thread"] = worker
            self._farm_loops[pid_int] = entry
            loop_snap = self._serialize_farm_loop_entry(entry)

        replaced_snap = self._finish_farm_loop_replacement(replaced, "Map Kills", acct_lbl)
        worker.start()
        self.log(
            f"[Map Kills] [{acct_lbl}] Started continuous hunting: {mode_desc} (min_stamina={min_stamina}, reserve={reserve}).",
            "ok",
        )
        return {
            "ok": True,
            "loop_id": loop_id,
            "pid": pid_int,
            "account_label": acct_lbl,
            "category": "kills",
            "mode": norm_mode,
            "loop": loop_snap,
            "replaced_loop": replaced_snap,
            "farm_loops": self.get_farm_loops_state(),
        }

    def _execute_single_kill_step(
        self,
        ba: Any,
        cd: Any,
        pid: int,
        target_mode: str,
        client_state: dict[str, Any],
        base_cfg: dict[str, Any],
        opts: dict[str, Any],
        npc_claims_ts: dict[str, float] | None,
        npc_search_lv: int | None,
        boomer_search_lv: int | None = None,
        pid_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute one atomic step for a specific Map Kills mode and return normalized telemetry.

        Claims (npc/boomer/saga) and the rejected-target blacklist are persisted in `pid_state` with TTL
        pruning so the same boomer/boss is never double-rallied before the server confirms the first rally.
        The returned dict carries the raw step result under `_raw` (used for phantom-dispatch detection).
        """
        min_stamina = int(opts.get("min_stamina", 0))
        reserve = int(opts.get("reserve", 0))
        max_dist = float(opts.get("max_distance", 150.0))
        boomer_min = int(opts.get("boomer_min_level", 1))
        boomer_max = int(opts.get("boomer_max_level", 5))
        npc_min = int(opts.get("npc_min_level", 0))
        npc_max = int(opts.get("npc_max_level", 0))
        allow_summon_opt = bool(opts.get("allow_summon_saga", True))
        dry_run = bool(opts.get("dry_run", False))

        if not isinstance(pid_state, dict):
            pid_state = {"gather": {}, "npc": {}, "boomer": {}, "saga": {}, "blacklist": {}, "last_saga_summon_ts": None}
        if isinstance(npc_claims_ts, dict):
            pid_state["npc"] = npc_claims_ts
        for k in ("npc", "boomer", "saga", "blacklist"):
            if not isinstance(pid_state.get(k), dict):
                pid_state[k] = {}

        claim_kinds: tuple[str, ...] = ("npc", "boomer", "saga")
        step_cfg = copy.deepcopy(base_cfg)
        step_cfg["formation_reserve"] = reserve
        step_ctx: dict[str, Any] = self._prepare_claims_context(pid_state, claim_kinds, time.monotonic())
        step_ctx.update({
            "min_stamina_override": min_stamina,
            "min_level_override": boomer_min,
            "max_level_override": boomer_max,
            "reserve_override": reserve,
        })

        # Saga summon cooldown (per PID): never re-summon within 60s of the last summon
        last_summon = pid_state.get("last_saga_summon_ts")
        summon_cooling = last_summon is not None and (time.monotonic() - float(last_summon)) < self._SAGA_SUMMON_COOLDOWN_SEC
        allow_summon = bool(allow_summon_opt and not summon_cooling)
        step_ctx["summon_cooldown_active"] = bool(summon_cooling)

        raw_res: Any = None
        try:
            if target_mode == "boomers":
                bm_cfg = dict(step_cfg.get("boomer_runs") or {})
                bm_cfg.update({
                    "join_open_rallies": True,
                    "auto_start_rally": True,
                    "min_level": boomer_min,
                    "max_level": boomer_max,
                    "min_stamina": min_stamina,
                })
                step_cfg["boomer_runs"] = bm_cfg
                if boomer_search_lv is not None:
                    step_ctx["search_level"] = max(boomer_min, min(boomer_max, int(boomer_search_lv)))
                fn = getattr(ba, "run_boomer_runs", None)
                if not callable(fn):
                    return self._normalize_farm_step_result({"ok": False, "error": "run_boomer_runs unavailable"}, target_mode)
                raw_res = fn(cd, pid, client_state, step_cfg, dry_run=dry_run, context=step_ctx)

            elif target_mode == "standalone_npc":
                fn = getattr(ba, "run_standalone_npc_step", None)
                if not callable(fn):
                    return self._normalize_farm_step_result({"ok": False, "error": "run_standalone_npc_step unavailable"}, target_mode)
                raw_res = fn(
                    cd,
                    pid,
                    client_state,
                    step_cfg,
                    min_level=npc_min,
                    max_level=npc_max,
                    max_distance=max_dist,
                    reserve=reserve,
                    min_stamina=min_stamina,
                    stamina_cost=10,
                    search_level=npc_search_lv,
                    dry_run=dry_run,
                    context=step_ctx,
                )

            elif target_mode == "saga":
                fn = getattr(ba, "run_saga_kill_step", None)
                if not callable(fn):
                    return self._normalize_farm_step_result({"ok": False, "error": "run_saga_kill_step unavailable"}, target_mode)
                raw_res = fn(
                    cd,
                    pid,
                    client_state,
                    step_cfg,
                    reserve=reserve,
                    min_stamina=min_stamina,
                    stamina_cost=10,
                    allow_summon=allow_summon,
                    dry_run=dry_run,
                    context=step_ctx,
                )
                if isinstance(raw_res, dict) and raw_res.get("summoned") and not dry_run:
                    pid_state["last_saga_summon_ts"] = time.monotonic()

            elif target_mode == "tyrant":
                fn = getattr(ba, "run_tyrant_event", None)
                if not callable(fn):
                    return self._normalize_farm_step_result({"ok": False, "error": "run_tyrant_event unavailable"}, target_mode)
                raw_res = fn(cd, pid, client_state, step_cfg, dry_run=dry_run, context=step_ctx)

            elif target_mode == "furylord":
                step_ctx["force_furylord"] = True
                fn = getattr(ba, "run_furylord", None)
                if not callable(fn):
                    return self._normalize_farm_step_result({"ok": False, "error": "run_furylord unavailable"}, target_mode)
                raw_res = fn(cd, pid, client_state, step_cfg, dry_run=dry_run, context=step_ctx)

            else:
                raw_res = {"ok": False, "error": f"Unknown kill mode: {target_mode}"}
        except Exception as exc:
            raw_res = {"ok": False, "status": "error", "error": str(exc)}

        if not dry_run:
            self._record_claims_context(pid_state, claim_kinds, step_ctx, raw_res, time.monotonic())
        norm = self._normalize_farm_step_result(raw_res, default_target=target_mode)
        norm["_raw"] = raw_res
        return norm

    @staticmethod
    def _pick_chain_stop_reason(mode_reasons: dict[str, str]) -> str:
        """Select the most informative stop_reason when every mode in all_chain hits a physical limit."""
        vals = [str(v).strip() for v in mode_reasons.values() if str(v).strip()]
        if not vals:
            return "no_targets_found"
        priority = (
            "client_offline",
            "dispatch_rejected",
            "no_troops_or_formations",
            "out_of_stamina",
            "daily_limit_reached",
            "no_targets_found",
            "not_in_alliance",
            "event_not_in_battle",
            "event_ended",
            "not_detected",
        )
        for p in priority:
            if p in vals:
                return p
        return vals[0]

    def _run_kill_step_serialized(
        self,
        pid: int,
        stop_ev: threading.Event,
        *step_args: Any,
        **step_kwargs: Any,
    ) -> dict[str, Any] | None:
        """Run `_execute_single_kill_step` under the per-PID exec lock; returns None if the loop was stopped meanwhile."""
        exec_lock = self._acquire_farm_exec_lock(pid, stop_ev)
        if exec_lock is None:
            return None
        try:
            return self._execute_single_kill_step(*step_args, **step_kwargs)
        finally:
            exec_lock.release()

    def _handle_kill_phantom(
        self,
        entry: dict[str, Any],
        tracker: dict[str, Any],
        pid_state: dict[str, Any],
        norm: dict[str, Any],
        mode_lbl: str,
        acct_lbl: str,
        dry_run: bool,
    ) -> tuple[bool, bool]:
        """Run phantom detection for a kill step. Returns (handled_as_rejected, must_stop)."""
        if dry_run:
            return False, False
        rej = self._check_phantom_dispatch(entry, tracker, pid_state, norm.get("_raw"), norm, mode_lbl)
        if int(rej.get("phantoms") or 0) <= 0:
            return False, False
        n_rej = int(rej.get("consecutive") or 0)
        tgt_note = ", ".join(str(t) for t in (rej.get("targets") or [])[:3]) or "target"
        rej_msg = (
            f"[{mode_lbl}] Game rejected march ({tgt_note}) - same squad still idle. "
            f"Blacklisted target for {int(self._FARM_BLACKLIST_TTL_SEC // 60)} min ({n_rej}/{self._FARM_MAX_REJECTS})."
        )
        self.log(f"[Map Kills] [{acct_lbl}] {rej_msg}", "warn")
        if n_rej >= self._FARM_MAX_REJECTS:
            self._update_farm_loop_telemetry(entry, norm, new_state="running", message=rej_msg)
            return True, True
        if norm.get("status") == "rejected":
            self._update_farm_loop_telemetry(entry, norm, new_state="searching", message=rej_msg)
            return True, False
        return False, False

    def _map_kills_loop_worker(self, entry: dict[str, Any]) -> None:
        """Background daemon worker repeating Map Kills (single mode or priority chain) until physically unable."""
        pid = int(entry["pid"])
        acct_lbl = str(entry.get("account_label") or f"PID {pid}")
        role = str(entry.get("role") or "farm")
        mode = str(entry.get("mode") or "boomers")
        opts = dict(entry.get("options") or {})
        stop_ev: threading.Event = entry["stop_event"]

        npc_min = int(opts.get("npc_min_level", 0))
        npc_max = int(opts.get("npc_max_level", 0))
        boomer_min = int(opts.get("boomer_min_level", 1))
        boomer_max = int(opts.get("boomer_max_level", 5))
        reserve = int(opts.get("reserve", 0))
        dry_run = bool(opts.get("dry_run", False))
        prioritize_bosses = bool(opts.get("prioritize_detected_bosses", False))
        dispatch_delay = float(opts.get("_dispatch_delay_sec", 2.0))
        wait_squad_delay = float(opts.get("_wait_squad_delay_sec", 5.0))
        search_delay = float(opts.get("_search_delay_sec", 2.5))
        probe_interval = float(opts.get("_probe_interval_sec", 30.0))
        exhausted_backoff = float(opts.get("_exhausted_backoff_sec", self._CHAIN_EXHAUSTED_COOLDOWN_SEC))

        pid_state = self._get_farm_pid_state(pid)
        reject_tracker: dict[str, Any] = {"last": {}, "consecutive": 0}
        client_state: dict[str, Any] = self._build_farm_client_state(pid, acct_lbl)
        consecutive_errors = 0
        logged_waiting = False
        stop_reason = "user_stopped"
        detail_msg = ""

        def _step_down(m: str, norm_res: dict[str, Any], cur: int | None, n_empty: int) -> int | None:
            if m == "standalone_npc":
                cur_lv = _safe_int(norm_res.get("searched_level"), cur or 0)
                if cur_lv and cur_lv > 1:
                    eff_min = max(1, npc_min) if npc_min > 0 else 1
                    return self._next_step_down_level(cur_lv, eff_min, n_empty, max_empty=4)
                return cur
            if m == "boomers":
                cur_lv = _safe_int(norm_res.get("searched_level"), cur or boomer_max) or boomer_max
                cur_lv = max(boomer_min, min(boomer_max, int(cur_lv)))
                return self._next_step_down_level(cur_lv, boomer_min, n_empty, max_empty=4)
            return cur

        def _reset_lv(m: str) -> int | None:
            if m == "standalone_npc":
                return npc_max if npc_max > 0 else None
            if m == "boomers":
                return boomer_max
            return None

        try:
            ccfg = self._load_farm_client_config(acct_lbl, role)

            if mode != "all_chain":
                empty_searches = 0
                search_lv: int | None = _reset_lv(mode)
                last_active_marches = 0
                while not stop_ev.is_set() and getattr(self, "is_monitoring", True):
                    ba = bot_actions
                    cd = client_discovery
                    if ba is None or cd is None:
                        stop_reason = "automation_unavailable"
                        detail_msg = "Automation modules unavailable"
                        break

                    norm = self._run_kill_step_serialized(
                        pid, stop_ev,
                        ba, cd, pid, mode, client_state, ccfg, opts, pid_state["npc"],
                        search_lv if mode == "standalone_npc" else None,
                        boomer_search_lv=search_lv if mode == "boomers" else None,
                        pid_state=pid_state,
                    )
                    if norm is None:
                        break
                    st = norm["status"]
                    rsn = norm["stop_reason"]
                    if norm.get("active_marches") is not None:
                        last_active_marches = int(norm["active_marches"])

                    if stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                        stop_reason = "user_stopped" if stop_ev.is_set() else "shutdown"
                        break

                    handled, must_stop = self._handle_kill_phantom(entry, reject_tracker, pid_state, norm, mode, acct_lbl, dry_run)
                    if must_stop:
                        stop_reason = "dispatch_rejected"
                        detail_msg = str(entry.get("last_message") or "")
                        break
                    if handled:
                        if stop_ev.wait(search_delay):
                            break
                        continue
                    st = norm["status"]

                    if st == "dispatched":
                        consecutive_errors = 0
                        empty_searches = 0
                        search_lv = _reset_lv(mode)
                        logged_waiting = False
                        disp_n = int(norm["dispatched_count"])
                        tot_disp = self._update_farm_loop_telemetry(
                            entry,
                            norm,
                            new_state="running",
                            message=norm.get("message") or f"Dispatched {disp_n} squad(s) ({mode}).",
                        )
                        self.log(
                            f"[Map Kills] [{acct_lbl}] ({mode}) {'[DRY RUN] Would dispatch' if dry_run else 'Dispatched'} {disp_n} squad(s) (session total: {tot_disp}).",
                            "ok",
                        )
                        if dry_run:
                            stop_reason = "dry_run_complete"
                            break
                        if stop_ev.wait(dispatch_delay):
                            break
                        continue

                    if st == "waiting_for_squad":
                        consecutive_errors = 0
                        empty_searches = 0
                        search_lv = _reset_lv(mode)
                        act_m = norm.get("active_marches")
                        tot_f = norm.get("total_formations")
                        occ_note = f" ({act_m}/{tot_f} marching)" if (act_m is not None and tot_f) else ""
                        wait_msg = f"All usable squads busy{occ_note} - waiting for a squad to return..."
                        self._update_farm_loop_telemetry(entry, norm, new_state="waiting_for_squad", message=wait_msg)
                        if not logged_waiting:
                            logged_waiting = True
                            self.log(f"[Map Kills] [{acct_lbl}] ({mode}) {wait_msg}", "info")
                        if dry_run:
                            stop_reason = "dry_run_complete"
                            break
                        if stop_ev.wait(wait_squad_delay):
                            break
                        continue

                    if st == "physical_limit" and rsn == "event_not_in_battle" and not dry_run:
                        # Event open but battle phase not started yet: keep polling instead of stopping
                        consecutive_errors = 0
                        pre_msg = f"[{mode}] Event open - waiting for its battle phase to start (re-checking every {int(probe_interval)}s)..."
                        self._update_farm_loop_telemetry(entry, norm, new_state="waiting_for_squad", message=pre_msg)
                        if not logged_waiting:
                            logged_waiting = True
                            self.log(f"[Map Kills] [{acct_lbl}] {pre_msg}", "info")
                        if stop_ev.wait(max(5.0, probe_interval)):
                            break
                        continue

                    exhausted_now = False
                    if st == "searching":
                        consecutive_errors = 0
                        logged_waiting = False
                        empty_searches += 1
                        if dry_run:
                            stop_reason = "dry_run_complete"
                            break
                        if empty_searches == 4:
                            verify_msg = f"[{mode}] Final search sent - verifying results before giving up..."
                            self._update_farm_loop_telemetry(entry, norm, new_state="searching", message=verify_msg)
                            if stop_ev.wait(max(2.5, search_delay)):
                                break
                            continue
                        if empty_searches > 4:
                            exhausted_now = True
                        else:
                            search_lv = _step_down(mode, norm, search_lv, empty_searches)
                            lv_note = f", next Lv{search_lv}" if search_lv else ""
                            search_msg = norm.get("message") or f"Searching map for {mode} targets ({empty_searches}/4{lv_note})..."
                            self._update_farm_loop_telemetry(entry, norm, new_state="searching", message=search_msg)
                            if stop_ev.wait(search_delay):
                                break
                            continue

                    if st == "physical_limit" and rsn == "no_targets_found":
                        exhausted_now = True

                    if exhausted_now:
                        if dry_run:
                            stop_reason = "dry_run_complete"
                            break
                        act_now = norm.get("active_marches")
                        act_now = last_active_marches if act_now is None else int(act_now)
                        if act_now > 0:
                            empty_searches = 0
                            search_lv = _reset_lv(mode)
                            wait_msg = (
                                f"[{mode}] No targets found right now - {act_now} squad(s) still out. "
                                f"Waiting for squads, re-searching in {int(exhausted_backoff)}s..."
                            )
                            self._update_farm_loop_telemetry(entry, norm, new_state="waiting_for_squad", message=wait_msg)
                            self.log(f"[Map Kills] [{acct_lbl}] {wait_msg}", "info")
                            if stop_ev.wait(exhausted_backoff):
                                break
                            continue
                        self._update_farm_loop_telemetry(entry, norm, new_state="running")
                        stop_reason = "no_targets_found"
                        break

                    if st == "physical_limit":
                        self._update_farm_loop_telemetry(entry, norm, new_state="running")
                        stop_reason = rsn or "no_targets_found"
                        detail_msg = str(norm.get("message") or "")
                        break

                    consecutive_errors += 1
                    err_txt = str(norm.get("message") or rsn or "RPC error")
                    self._update_farm_loop_telemetry(
                        entry,
                        norm,
                        new_state="running",
                        message=f"Retry {consecutive_errors}/3 after error: {err_txt}",
                    )
                    if consecutive_errors >= 3:
                        stop_reason = rsn or "consecutive_errors"
                        detail_msg = err_txt
                        break
                    if dry_run:
                        stop_reason = "dry_run_complete"
                        break
                    if stop_ev.wait(search_delay):
                        break
            else:
                # all_chain mode: probe conditional bosses periodically, skip undetected bosses, skip exhausted modes
                # (60s cooldown or until all squads return), repeat until every enabled mode hits a physical limit
                base_chain: list[str] = list(opts.get("chain") or ["boomers", "standalone_npc", "saga", "tyrant", "furylord"])
                last_probe_ts = 0.0
                has_det_fn = callable(getattr(bot_actions, "detect_map_kill_targets", None))
                detected_boss_map: dict[str, bool] = {"saga": not has_det_fn, "tyrant": not has_det_fn, "furylord": not has_det_fn}
                empty_by_mode: dict[str, int] = {}
                exhausted_modes: dict[str, float] = {}
                capped_modes: set[str] = set()
                search_lv_by_mode: dict[str, int | None] = {m: _reset_lv(m) for m in base_chain}
                last_active_marches = 0
                prev_active_marches = 0

                while not stop_ev.is_set() and getattr(self, "is_monitoring", True):
                    ba = bot_actions
                    cd = client_discovery
                    if ba is None or cd is None:
                        stop_reason = "automation_unavailable"
                        detail_msg = "Automation modules unavailable"
                        break

                    now_ts = time.time()
                    has_det_fn = callable(getattr(ba, "detect_map_kill_targets", None))
                    if has_det_fn and (last_probe_ts == 0.0 or (now_ts - last_probe_ts) >= probe_interval):
                        exec_lock = self._acquire_farm_exec_lock(pid, stop_ev)
                        if exec_lock is None:
                            break
                        try:
                            det = self.probe_map_kills_status(pid=pid, max_age_sec=5.0 if last_probe_ts == 0.0 else 0.0)
                        finally:
                            exec_lock.release()
                        last_probe_ts = time.time()
                        if det.get("ok"):
                            detected_boss_map = {
                                "saga": bool(_as_dict(det.get("saga")).get("detected")),
                                "tyrant": bool(_as_dict(det.get("tyrant")).get("detected")),
                                "furylord": bool(_as_dict(det.get("furylord")).get("detected")),
                            }
                            if det.get("active_marches") is not None:
                                last_active_marches = int(det.get("active_marches") or 0)

                    # All squads came home -> exhausted modes may have new targets: retry them immediately
                    now_m = time.monotonic()
                    if prev_active_marches > 0 and last_active_marches == 0 and exhausted_modes:
                        exhausted_modes.clear()
                    prev_active_marches = last_active_marches
                    for m_ex in [k for k, ts in exhausted_modes.items() if (now_m - ts) >= exhausted_backoff]:
                        exhausted_modes.pop(m_ex, None)

                    runnable: list[str] = []
                    cooling: list[str] = []
                    mode_stop_reasons: dict[str, str] = {}
                    for m in base_chain:
                        if m in capped_modes:
                            mode_stop_reasons[m] = "daily_limit_reached"
                            continue
                        if m in self._CONDITIONAL_KILL_BOSSES and has_det_fn and not detected_boss_map.get(m, False):
                            mode_stop_reasons[m] = "not_detected"
                            continue
                        if m in exhausted_modes:
                            mode_stop_reasons[m] = "no_targets_found"
                            cooling.append(m)
                            continue
                        runnable.append(m)

                    if prioritize_bosses and runnable:
                        boss_order = [m for m in ("tyrant", "furylord", "saga") if m in runnable]
                        rest_order = [m for m in runnable if m not in ("tyrant", "furylord", "saga")]
                        runnable = boss_order + rest_order

                    if not runnable:
                        if cooling and last_active_marches > 0 and not dry_run:
                            nxt = min(max(0.0, exhausted_backoff - (now_m - exhausted_modes.get(m, now_m))) for m in cooling)
                            wait_s = max(wait_squad_delay, min(exhausted_backoff, nxt or wait_squad_delay))
                            wait_chain_msg = (
                                f"[Chain] All enabled targets exhausted - {last_active_marches} squad(s) still out. "
                                f"Re-searching in {int(wait_s)}s or when squads return..."
                            )
                            with self._ensure_farm_loop_attrs():
                                entry["state"] = "waiting_for_squad"
                                entry["last_message"] = wait_chain_msg
                                entry["updated_at"] = time.time()
                            if not logged_waiting:
                                logged_waiting = True
                                self.log(f"[Map Kills] [{acct_lbl}] {wait_chain_msg}", "info")
                            if stop_ev.wait(wait_s):
                                break
                            continue
                        stop_reason = "dry_run_complete" if dry_run else self._pick_chain_stop_reason(mode_stop_reasons)
                        break

                    dispatched_in_pass = False
                    saw_waiting = False
                    saw_searching = False
                    saw_error = False
                    abort_chain = False

                    for m in runnable:
                        if stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                            abort_chain = True
                            break

                        norm = self._run_kill_step_serialized(
                            pid, stop_ev,
                            ba,
                            cd,
                            pid,
                            m,
                            client_state,
                            ccfg,
                            opts,
                            pid_state["npc"],
                            search_lv_by_mode.get(m) if m == "standalone_npc" else None,
                            boomer_search_lv=search_lv_by_mode.get(m) if m == "boomers" else None,
                            pid_state=pid_state,
                        )
                        if norm is None:
                            abort_chain = True
                            break
                        if stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                            abort_chain = True
                            break
                        if norm.get("active_marches") is not None:
                            last_active_marches = int(norm["active_marches"])

                        handled, must_stop = self._handle_kill_phantom(entry, reject_tracker, pid_state, norm, m, acct_lbl, dry_run)
                        if must_stop:
                            stop_reason = "dispatch_rejected"
                            detail_msg = str(entry.get("last_message") or "")
                            abort_chain = True
                            break
                        if handled:
                            saw_searching = True
                            continue
                        st = norm["status"]
                        rsn = norm["stop_reason"]

                        if st == "dispatched":
                            consecutive_errors = 0
                            empty_by_mode[m] = 0
                            exhausted_modes.pop(m, None)
                            search_lv_by_mode[m] = _reset_lv(m)
                            logged_waiting = False
                            dispatched_in_pass = True
                            disp_n = int(norm["dispatched_count"])
                            tot_disp = self._update_farm_loop_telemetry(
                                entry,
                                norm,
                                new_state="running",
                                message=norm.get("message") or f"[Chain: {m}] Dispatched {disp_n} squad(s).",
                            )
                            self.log(
                                f"[Map Kills] [{acct_lbl}] [Chain -> {m}] {'[DRY RUN] Would dispatch' if dry_run else 'Dispatched'} {disp_n} squad(s) (session total: {tot_disp}).",
                                "ok",
                            )
                            if dry_run:
                                continue
                            break

                        if st == "waiting_for_squad":
                            saw_waiting = True
                            free_now = norm.get("free_formations")
                            # If only Formation 1 is busy (e.g. Furylord) while other formations are still free, let remaining modes run!
                            if free_now is not None and free_now <= reserve:
                                self._update_farm_loop_telemetry(
                                    entry,
                                    norm,
                                    new_state="waiting_for_squad",
                                    message="All usable squads marching - waiting for a squad to return...",
                                )
                                break
                            continue

                        if st == "searching":
                            cnt_s = empty_by_mode.get(m, 0) + 1
                            empty_by_mode[m] = cnt_s
                            if cnt_s <= 4:
                                # cnt_s == 4: final search sent -> one more verification scan on the next pass
                                saw_searching = True
                                if cnt_s < 4:
                                    search_lv_by_mode[m] = _step_down(m, norm, search_lv_by_mode.get(m), cnt_s)
                                scan_note = "verifying final search" if cnt_s == 4 else f"{cnt_s}/4"
                                self._update_farm_loop_telemetry(
                                    entry,
                                    norm,
                                    new_state="searching",
                                    message=f"[Chain: {m}] Scanning map ({scan_note})...",
                                )
                            else:
                                # Exhausted: stop sending FindMonster for this mode until cooldown / squads return
                                exhausted_modes[m] = time.monotonic()
                                empty_by_mode[m] = 0
                                search_lv_by_mode[m] = _reset_lv(m)
                                mode_stop_reasons[m] = "no_targets_found"
                            continue

                        if st == "physical_limit":
                            self._update_farm_loop_telemetry(entry, norm, new_state="running")
                            if rsn == "client_offline":
                                stop_reason = rsn
                                detail_msg = str(norm.get("message") or "")
                                abort_chain = True
                                break
                            mode_stop_reasons[m] = rsn or "no_targets_found"
                            if rsn == "no_troops_or_formations":
                                # Mode-specific shortage (e.g. Furylord F1) must not abort the whole chain
                                exhausted_modes[m] = time.monotonic()
                            elif rsn == "daily_limit_reached":
                                capped_modes.add(m)
                            elif rsn in ("not_detected", "event_ended", "event_not_in_battle") and m in self._CONDITIONAL_KILL_BOSSES:
                                detected_boss_map[m] = False
                            elif rsn == "no_targets_found":
                                exhausted_modes[m] = time.monotonic()
                                empty_by_mode[m] = 0
                            continue

                        # Error in mode m
                        saw_error = True
                        detail_msg = str(norm.get("message") or rsn or "RPC error")

                    if abort_chain or stop_ev.is_set() or not getattr(self, "is_monitoring", True):
                        if stop_ev.is_set():
                            stop_reason = "user_stopped"
                        elif not getattr(self, "is_monitoring", True):
                            stop_reason = "shutdown"
                        break

                    if dry_run:
                        stop_reason = "dry_run_complete"
                        break

                    if dispatched_in_pass:
                        if stop_ev.wait(dispatch_delay):
                            break
                        continue

                    if saw_searching:
                        consecutive_errors = 0
                        logged_waiting = False
                        with self._ensure_farm_loop_attrs():
                            entry["state"] = "searching"
                            entry["updated_at"] = time.time()
                        if stop_ev.wait(search_delay):
                            break
                        continue

                    if saw_waiting:
                        consecutive_errors = 0
                        # NOTE: never reset other modes' search counters just because one mode is waiting
                        wait_chain_msg = "All usable squads busy - waiting for a squad to return..."
                        with self._ensure_farm_loop_attrs():
                            entry["state"] = "waiting_for_squad"
                            entry["last_message"] = wait_chain_msg
                            entry["updated_at"] = time.time()
                        if not logged_waiting:
                            logged_waiting = True
                            self.log(
                                f"[Map Kills] [{acct_lbl}] [Chain] {wait_chain_msg}",
                                "info",
                            )
                        if stop_ev.wait(wait_squad_delay):
                            break
                        continue

                    if saw_error:
                        consecutive_errors += 1
                        if consecutive_errors >= 3:
                            stop_reason = "consecutive_errors"
                            break
                        if stop_ev.wait(search_delay):
                            break
                        continue

                    # Every runnable mode hit a limit this pass. Keep waiting (not stopping) while squads are out
                    # and some modes are merely exhausted/cooling, unless an account-wide hard limit was hit.
                    hard_limits = {"out_of_stamina", "not_in_alliance", "client_offline"}
                    if exhausted_modes and last_active_marches > 0 and not (set(mode_stop_reasons.values()) & hard_limits):
                        if stop_ev.wait(wait_squad_delay):
                            break
                        continue
                    stop_reason = self._pick_chain_stop_reason(mode_stop_reasons)
                    break
        finally:
            if stop_ev.is_set() and stop_reason not in ("replaced", "replaced_by_new_loop", "shutdown"):
                stop_reason = "user_stopped"
            elif not getattr(self, "is_monitoring", True):
                stop_reason = "shutdown"
            self._finalize_farm_loop_worker(entry, stop_reason=stop_reason, final_state="stopped", detail_msg=detail_msg)

    def stop_map_kills_loop(self, pid: int | None = None) -> dict[str, Any]:
        """Stop active Map Kills repeat loop (for explicit PID or all active Map Kills loops)."""
        norm_pid = self._coerce_optional_pid(pid)
        explicit_pid = _safe_int(norm_pid, -1) if norm_pid is not None else None
        stopped = self._stop_farm_loops_internal(
            pid=explicit_pid,
            category="kills",
            reason="user_stopped",
            join_timeout=0.5,
            log_stop=True,
        )
        return {
            "ok": True,
            "stopped": len(stopped) > 0,
            "stopped_pids": [int(s["pid"]) for s in stopped if s.get("pid") is not None],
            "farm_loops": self.get_farm_loops_state(),
        }

    def stop_all_farm_loops(self) -> dict[str, Any]:
        """Stop all active RSS Gathering and Map Kills loops across all clients."""
        stopped = self._stop_farm_loops_internal(
            pid=None,
            category=None,
            reason="user_stopped",
            join_timeout=0.8,
            log_stop=True,
        )
        return {
            "ok": True,
            "stopped": len(stopped) > 0,
            "stopped_pids": [int(s["pid"]) for s in stopped if s.get("pid") is not None],
            "farm_loops": self.get_farm_loops_state(),
        }

    def get_state(
        self,
        since_log_id: int | None = None,
        known_cfg_ver: int | None = None,
        include_catalog: bool = True,
        since_log_epoch: int | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            cfg_ver, cfg_snap = self._build_config_snapshot()
            self._recompute_always_on_state_locked()
            cur_epoch = int(getattr(self, "_log_epoch", 0))
            cleared_seq = int(getattr(self, "_logs_cleared_seq", 0))
            req_epoch = _safe_int(since_log_epoch, None) if since_log_epoch is not None else None
            epoch_mismatch = since_log_epoch is not None and req_epoch != cur_epoch

            sid: int | None = None
            if since_log_id is not None:
                coerced_sid = _safe_int(since_log_id, 0)
                sid = coerced_sid if coerced_sid is not None else 0

            if epoch_mismatch or (sid is not None and 0 < sid <= cleared_seq):
                logs_payload = list(self.logs)
                logs_reset = True
            elif sid is not None:
                if self.logs and int(self.logs[-1].get("id") or 0) < sid:
                    logs_payload = list(self.logs)
                    logs_reset = True
                elif not self.logs and sid > 0:
                    logs_payload = []
                    logs_reset = True
                else:
                    logs_payload = [e for e in self.logs if int(e.get("id") or 0) > sid]
                    logs_reset = False
            else:
                logs_payload = list(self.logs)
                logs_reset = False

            fleet_copy = dict(self.fleet_state)
            if isinstance(fleet_copy.get("clients"), list):
                fleet_copy["clients"] = [dict(c) for c in fleet_copy["clients"] if isinstance(c, dict)]

            out: dict[str, Any] = {
                "is_online": self.is_online,
                "status_text": self.status_text,
                "fps_text": self.fps_text,
                "dropdown_values": list(self.dropdown_values),
                "selected_dropdown": self.selected_dropdown,
                "env": dict(self.env),
                "fleet": fleet_copy,
                "setup": copy.deepcopy(self.setup_status),
                "finder_status": dict(self.finder_status),
                "logs": logs_payload,
                "logs_delta": since_log_id is not None,
                "logs_reset": logs_reset,
                "log_head_id": int(self._log_seq),
                "log_epoch": cur_epoch,
                "active_actions": sorted(self._active_actions),
                "always_on_daemon_enabled": self._always_on_daemon_enabled,
                "always_on_daemon_state": self._always_on_daemon_state,
                "always_on_daemon": self._build_always_on_snapshot_locked(),
                "hospital_watcher_enabled": self._hospital_watcher_enabled,
                "hospital_watcher_state": self._hospital_watcher_state,
                "hospital_watcher_summary": dict(self._hospital_watcher_last_summary),
                "alliance_help_watcher_enabled": self._alliance_help_watcher_enabled,
                "alliance_help_watcher_state": self._alliance_help_watcher_state,
                "alliance_help_stats": dict(self._alliance_help_stats),
                "alliance_tech_watcher_enabled": self._alliance_tech_watcher_enabled,
                "alliance_tech_watcher_state": self._alliance_tech_watcher_state,
                "alliance_tech_stats": dict(self._alliance_tech_stats),
                "farm_loops": self._build_farm_loops_snapshot_locked(),
                "config_ver": cfg_ver,
            }
            if include_catalog:
                out["task_catalog"] = TASK_CATALOG
            known_ver_int = _safe_int(known_cfg_ver, None) if known_cfg_ver is not None else None
            if known_ver_int is None or known_ver_int != cfg_ver:
                out["config"] = cfg_snap
            return out

    def select_target_client(self, choice: str) -> dict[str, Any]:
        c = str(choice or "Auto").strip()
        if c == "Auto":
            with self._lock:
                self.selected_client_pid = None
                self.selected_client_label = None
                self.selected_dropdown = "Auto"
            self.log("Target client set to Auto (prefers Main).", "info")
            return {"ok": True}
        if c.startswith("Launch: "):
            lbl = c[len("Launch: "):].strip()
            with self._lock:
                self.selected_client_pid = None
                self.selected_client_label = lbl or None
            self.log(f"Launching '{lbl}' from top menu...", "info")
            self.run_action("launch_single_client", {"label": lbl, "mode": "windowed"})
            return {"ok": True, "launching": lbl}
        m = re.search(r"\(PID\s+(\d+)\)\s*$", c)
        picked_pid = int(m.group(1)) if m else None
        with self._lock:
            running = list(self.running_clients)
            proc = next((p for p in running if int(p["pid"]) == picked_pid), None) if picked_pid is not None else None
            if proc is None:
                prefix = c.split(" (PID ", 1)[0].strip()
                proc = next((p for p in running if prefix in (self._client_display_name(p), str(p.get("label") or ""))), None)
            if proc is not None:
                self.selected_client_pid = int(proc["pid"])
                self.selected_client_label = str(proc.get("label") or "") or None
                self.target_pid = self.selected_client_pid
                os.environ["LASTZ_TARGET_PID"] = str(self.target_pid)
            else:
                self.selected_client_pid = picked_pid
                self.selected_client_label = c.split(" (PID ", 1)[0].strip() or None
                if picked_pid is not None:
                    self.target_pid = picked_pid
                    os.environ["LASTZ_TARGET_PID"] = str(picked_pid)
            self.selected_dropdown = c
        self._last_env_ts = 0.0
        self.log(f"Target client switched to {choice}.", "info")
        return {"ok": True}

    def save_bot_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        if multi_client_bot is None:
            return {"ok": False, "error": "multi_client_bot unavailable"}
        try:
            with self._lock:
                cfg = multi_client_bot.load_config()
                defaults = cfg.setdefault("client_defaults", {})
                role_target = str(payload.get("role") or "farm").lower()
                tasks_map = dict(payload.get("tasks") or {})
                # Backward-compatible mirror: unified 3-in-1 Gold Bounties also keeps bounty_steal aligned
                if "bounties" in tasks_map and "bounty_steal" not in tasks_map:
                    tasks_map["bounty_steal"] = bool(tasks_map["bounties"])

                if role_target == "main":
                    main_t = defaults.setdefault("main", {}).setdefault("tasks", {})
                    for k, v in tasks_map.items():
                        main_t[str(k)] = bool(v)
                else:
                    cfg.setdefault("enabled_tasks", {})
                    farm_t = defaults.setdefault("farm", {}).setdefault("tasks", {})
                    main_t = defaults.setdefault("main", {}).setdefault("tasks", {})
                    prev_farm = dict(farm_t)
                    for k, v in tasks_map.items():
                        val = bool(v)
                        sk = str(k)
                        cfg["enabled_tasks"][sk] = val
                        farm_t[sk] = val
                        if (not val) or (val != bool(prev_farm.get(sk, True))):
                            main_t[sk] = val

                if "auto_launch_stopped_clients" in payload:
                    cfg["auto_launch_stopped_clients"] = bool(payload["auto_launch_stopped_clients"])
                if "main_enabled" in payload:
                    defaults.setdefault("main", {})["enabled"] = bool(payload["main_enabled"])
                if "cycle_interval_seconds" in payload:
                    cfg["cycle_interval_seconds"] = max(30, int(payload["cycle_interval_seconds"]))
                if "task_interval_minutes" in payload:
                    cfg.setdefault("schedule", {})["interval_minutes"] = max(1, int(payload["task_interval_minutes"]))
                if "auto_launch_mode" in payload:
                    cfg["auto_launch_mode"] = str(payload["auto_launch_mode"]).strip().lower() or "eco"

                multi_client_bot.save_config(cfg)
                self._config_snapshot_cache = None
            if not payload.get("quiet", False):
                self.log(f"Saved {role_target.capitalize()} automation settings.", "ok")
            return {"ok": True}
        except Exception as exc:
            self.log(f"Save Config Error: {exc}", "err")
            return {"ok": False, "error": str(exc)}

    def save_event_rules(self, rules_payload: dict[str, Any]) -> dict[str, Any]:
        if multi_client_bot is None:
            return {"ok": False, "error": "multi_client_bot unavailable"}
        try:
            with self._lock:
                cur = multi_client_bot.load_config()
                defs = cur.setdefault("client_defaults", {})
                for role_key in ("main", "farm"):
                    rc = defs.setdefault(role_key, {})
                    for section, vals in (rules_payload or {}).items():
                        if isinstance(vals, dict):
                            rc.setdefault(section, {}).update(vals)
                multi_client_bot.save_config(cur)
                self._config_snapshot_cache = None
            self.log("Saved all Event & Bot Rules.", "ok")
            return {"ok": True}
        except Exception as exc:
            self.log(f"Save Rules Error: {exc}", "err")
            return {"ok": False, "error": str(exc)}

    def browse_folder(self) -> str:
        try:
            if self._window is not None:
                res = self._window.create_file_dialog(webview.FileDialog.FOLDER)
                if res and len(res) > 0:
                    return str(res[0])
        except Exception:
            pass
        return ""

    def _detect_world_season(
        self,
        pid: int | None = None,
        force_live: bool = False,
        index: dict[str, Any] | None = None,
        _allow_live_query: bool = True,
    ) -> dict[str, Any]:
        """Resolve active Last Z world/seasonal map via 4-tier fallback: live Lua -> account cache -> map cache -> default."""
        manifest = _load_world_maps_manifest()
        maps_by_key = _world_maps_by_key(manifest)
        enum_map = _world_season_enum_from_manifest(manifest)
        available_maps = _format_available_world_maps(manifest)
        default_key = str(manifest.get("default_map_key") or "pre_season_1").strip().lower()
        if default_key not in maps_by_key:
            default_key = "pre_season_1"

        def _build_payload(
            season_key: str,
            world_season_id: int | None,
            source: str,
            is_live: bool,
            season_show_name: str = "",
        ) -> dict[str, Any]:
            sk = str(season_key or "").strip().lower()
            if sk not in maps_by_key and world_season_id is not None:
                sk = enum_map.get(int(world_season_id), default_key)
            if sk not in maps_by_key:
                sk = default_key
            entry = maps_by_key.get(sk) or next(iter(maps_by_key.values()))
            ws_ids = entry.get("world_season_ids") or [0]
            if (
                world_season_id is not None
                and int(world_season_id) in enum_map
                and enum_map[int(world_season_id)] == sk
            ):
                resolved_ws_id = int(world_season_id)
            else:
                resolved_ws_id = _safe_int(ws_ids[0], 0)
            return {
                "season_key": str(entry.get("key") or sk),
                "world_season_id": int(resolved_ws_id),
                "label": str(entry.get("label") or sk),
                "short_label": str(entry.get("short_label") or entry.get("label") or sk),
                "grid_size": _safe_int(entry.get("grid_size"), 1000),
                "y_origin": str(entry.get("y_origin") or manifest.get("y_origin") or "top"),
                "supports_zones": bool(entry.get("supports_zones", False)),
                "source": str(source),
                "is_live": bool(is_live),
                "season_show_name": str(season_show_name or ""),
                "available_maps": [dict(m) for m in available_maps],
            }

        def _extract_persisted(obj: Any) -> tuple[str, int, str] | None:
            if not isinstance(obj, dict):
                return None
            ws_val = _safe_int(obj.get("world_season_id"), None)
            if ws_val is None:
                ws_val = _safe_int(obj.get("world_season"), None)
            skey = str(obj.get("season_key") or "").strip().lower()
            show_nm = str(obj.get("season_show_name") or "").strip()
            if ws_val is not None and ws_val in enum_map:
                resolved_sk = skey if (skey and skey in maps_by_key) else enum_map[ws_val]
                return (resolved_sk, int(ws_val), show_nm)
            if skey and skey in maps_by_key:
                ws_ids = maps_by_key[skey].get("world_season_ids") or [0]
                return (skey, _safe_int(ws_ids[0], 0), show_nm)
            return None

        target_pid: int | None = None
        proc: dict[str, Any] | None = None
        account_label = ""
        clean_label = ""
        try:
            _, target_pid, proc, account_label, clean_label = self._resolve_client_context(pid)
        except Exception:
            with self._lock:
                sel_pid = getattr(self, "selected_client_pid", None)
                tgt_pid = getattr(self, "target_pid", None)
                sel_lbl = getattr(self, "selected_client_label", None)
            target_pid = _safe_int(pid, None) if pid is not None else (sel_pid or tgt_pid)
            if target_pid is not None and target_pid <= 0:
                target_pid = None
            account_label = str(sel_lbl or "") if pid is None else ""
            clean_label = re.sub(r"[^a-zA-Z0-9_\-]", "_", account_label.lower()).strip("_") if account_label else ""

        raw_clean = clean_label if clean_label and clean_label != "client" else ""
        sync_key = f"wseason:{raw_clean or (f'pid_{target_pid}' if target_pid else 'none')}"
        data_dir = _resolve_map_data_dir()
        cache_dir = os.path.join(data_dir, "json cache")
        now_ts = time.time()

        with self._lock:
            live_sync_ts = getattr(self, "_live_sync_ts", None)
            if live_sync_ts is None:
                live_sync_ts = {}
                self._live_sync_ts = live_sync_ts
            live_cache = getattr(self, "_world_season_live_cache", None)
            if live_cache is None:
                live_cache = {}
                self._world_season_live_cache = live_cache
            last_sync = float(live_sync_ts.get(sync_key, 0.0))
            mem_entry = live_cache.get(sync_key)

        cache_fresh = (now_ts - last_sync) < 60.0
        if (
            not force_live
            and cache_fresh
            and proc is not None
            and isinstance(mem_entry, tuple)
            and len(mem_entry) == 3
            and (now_ts - float(mem_entry[0])) < 60.0
            and mem_entry[1] == target_pid
            and isinstance(mem_entry[2], dict)
        ):
            ext_mem = _extract_persisted(mem_entry[2])
            if ext_mem is not None:
                return _build_payload(ext_mem[0], ext_mem[1], "live", True, ext_mem[2])

        # Tier 1: Live Last Z client query via xLua
        if (
            _allow_live_query
            and (force_live or not cache_fresh)
            and client_discovery is not None
            and target_pid
            and proc is not None
        ):
            try:
                if client_discovery._xlua_loaded(target_pid):
                    lua_season = _LUA_JSON_SER + r"""
                    local world_season = nil
                    local season = nil
                    local config_season = nil
                    local is_using_season_asset = nil
                    local season_show_name = ""
                    local server_id = 0
                    pcall(function()
                        local sdm = DataCenter and DataCenter.SeasonDataManager
                        if sdm then
                            if type(sdm.GetWorldSeason) == "function" then
                                local okW, vW = pcall(sdm.GetWorldSeason, sdm)
                                if okW and vW ~= nil then world_season = tonumber(vW) end
                            end
                            if world_season == nil and sdm.world_season ~= nil then
                                world_season = tonumber(sdm.world_season)
                            end
                            if type(sdm.GetSeason) == "function" then
                                local okS, vS = pcall(sdm.GetSeason, sdm)
                                if okS and vS ~= nil then season = tonumber(vS) end
                            elseif sdm.season ~= nil then
                                season = tonumber(sdm.season)
                            end
                            if type(sdm.GetConfigSeason) == "function" then
                                local okC, vC = pcall(sdm.GetConfigSeason, sdm)
                                if okC and vC ~= nil then config_season = tonumber(vC) end
                            end
                            if type(sdm.IsUsingSeasonAsset) == "function" then
                                local okA, vA = pcall(sdm.IsUsingSeasonAsset, sdm)
                                if okA and vA ~= nil then is_using_season_asset = not not vA end
                            end
                            if type(sdm.GetSeasonShowName) == "function" then
                                local okN, vN = pcall(sdm.GetSeasonShowName, sdm)
                                if okN and vN ~= nil then season_show_name = tostring(vN) end
                            end
                        end
                    end)
                    pcall(function()
                        local am = DataCenter and DataCenter.AccountManager
                        if am then
                            local s = am.curServerId or am.serverId
                            if s ~= nil and tonumber(s) and tonumber(s) > 0 then
                                server_id = tonumber(s)
                            end
                        end
                        if server_id <= 0 then
                            local p = LuaEntry and LuaEntry.Player
                            if p then
                                local okS, s = pcall(function() return (p.GetCurServerId and p:GetCurServerId()) or p.serverId end)
                                if okS and s ~= nil and tonumber(s) and tonumber(s) > 0 then
                                    server_id = tonumber(s)
                                end
                            end
                        end
                        if world_season == nil and am and server_id > 0 and type(am.GetWorldSeasonByServerId) == "function" then
                            local okWS, vWS = pcall(am.GetWorldSeasonByServerId, am, server_id)
                            if okWS and vWS ~= nil then world_season = tonumber(vWS) end
                        end
                    end)
                    local payload = _jobj({
                        world_season = world_season,
                        season = season,
                        config_season = config_season,
                        is_using_season_asset = is_using_season_asset,
                        season_show_name = season_show_name,
                        server_id = server_id,
                    })
                    return ser(payload)
                    """
                    ok, res = client_discovery.frida_eval_lua(target_pid, lua_season, timeout=5.0)
                    if ok and res:
                        parsed = json.loads(res)
                        if isinstance(parsed, dict):
                            ws_raw = parsed.get("world_season")
                            if ws_raw is None:
                                ws_raw = parsed.get("world_season_id")
                            ws_id = _safe_int(ws_raw, None)
                            if ws_id is not None and ws_id in enum_map:
                                resolved_key = enum_map[ws_id]
                                show_name = str(parsed.get("season_show_name") or "").strip()
                                live_srv = _safe_int(parsed.get("server_id"), 0)
                                if live_srv <= 0 and isinstance(proc, dict):
                                    live_srv = _safe_int(proc.get("serverId") or proc.get("selfServerId"), 0)
                                persisted = {
                                    "timestamp": round(now_ts, 3),
                                    "world_season_id": int(ws_id),
                                    "season_key": resolved_key,
                                    "season_show_name": show_name,
                                    "server_id": int(live_srv),
                                    "account_label": str(account_label or ""),
                                    "season": _safe_int(parsed.get("season"), None),
                                    "config_season": _safe_int(parsed.get("config_season"), None),
                                    "is_using_season_asset": parsed.get("is_using_season_asset"),
                                }
                                write_acct = (
                                    os.path.join(cache_dir, f"{raw_clean}_world_season.json")
                                    if raw_clean
                                    else (os.path.join(cache_dir, f"pid_{target_pid}_world_season.json") if target_pid else None)
                                )
                                if write_acct:
                                    _atomic_write_json(write_acct, persisted)
                                _atomic_write_json(os.path.join(cache_dir, "world_season_last.json"), persisted)
                                with self._lock:
                                    self._live_sync_ts[sync_key] = now_ts
                                    self._world_season_live_cache[sync_key] = (now_ts, target_pid, dict(persisted))
                                return _build_payload(resolved_key, ws_id, "live", True, show_name)
            except Exception as exc:
                try:
                    self.log(f"World season live check skipped; using cached/offline season ({exc})", "warn")
                except Exception:
                    pass

        # Tier 2: Per-account persisted cache (strictly isolated per account) or matching world_season_last.json
        acct_candidates: list[str] = []
        if raw_clean:
            acct_candidates.append(os.path.join(cache_dir, f"{raw_clean}_world_season.json"))
        if target_pid:
            acct_candidates.append(os.path.join(cache_dir, f"pid_{target_pid}_world_season.json"))
        for cand in acct_candidates:
            if not os.path.isfile(cand):
                continue
            cdata = _load_json_cached(cand, default=None)
            ext = _extract_persisted(cdata)
            if ext is not None:
                return _build_payload(ext[0], ext[1], "account_cache", False, ext[2])

        last_path = os.path.join(cache_dir, "world_season_last.json")
        idx_resolved = index
        if os.path.isfile(last_path):
            ldata = _load_json_cached(last_path, default=None)
            ext_last = _extract_persisted(ldata)
            if ext_last is not None and isinstance(ldata, dict):
                last_srv = _safe_int(ldata.get("server_id"), 0)
                last_acct = str(ldata.get("account_label") or "").strip()
                last_clean = re.sub(r"[^a-zA-Z0-9_\-]", "_", last_acct.lower()).strip("_") if last_acct else ""
                account_conflict = bool(raw_clean and last_clean and raw_clean != last_clean)

                expected_servers: set[int] = set()
                if isinstance(proc, dict):
                    for sk_field in ("serverId", "selfServerId"):
                        sv = _safe_int(proc.get(sk_field), 0)
                        if sv > 0:
                            expected_servers.add(sv)
                if not account_conflict and pid is None:
                    with self._lock:
                        env_srv = _safe_int(self.env.get("serverId"), 0)
                    if env_srv > 0:
                        expected_servers.add(env_srv)
                    det_path = os.path.join(data_dir, "detected_environment.json")
                    if os.path.isfile(det_path):
                        det = _load_json_cached(det_path, default={})
                        if isinstance(det, dict):
                            dsrv = _safe_int(det.get("serverId"), 0)
                            if dsrv > 0:
                                expected_servers.add(dsrv)
                    if idx_resolved is None and not expected_servers and last_srv > 0:
                        idx_resolved = _get_world_map_index(data_dir, dedup_by_uid=True)
                    if isinstance(idx_resolved, dict):
                        for sv in (idx_resolved.get("servers") or []):
                            sv_i = _safe_int(sv, 0)
                            if sv_i > 0:
                                expected_servers.add(sv_i)

                server_matches = (not expected_servers) or (last_srv <= 0) or (last_srv in expected_servers)
                if not account_conflict and server_matches:
                    return _build_payload(ext_last[0], ext_last[1], "account_cache", False, ext_last[2])

        # Tier 3: Offline world_map_cache PointType/coordinate signature inference
        inferred = _infer_world_season_from_map_cache(data_dir, index=idx_resolved)
        if isinstance(inferred, dict):
            return _build_payload(
                str(inferred.get("season_key") or default_key),
                _safe_int(inferred.get("world_season_id"), None),
                "world_map_cache",
                False,
                "",
            )

        # Tier 4: Default fallback (Pre-Season 1 / Wasteland)
        return _build_payload(default_key, 0, "default", False, "")

    def _active_map_grid_size(
        self,
        index: dict[str, Any] | None = None,
        grid_size: int | None = None,
        season_key: str = "",
        pid: int | None = None,
    ) -> int:
        """Resolve active map grid_size (1000 for S1-S5, 1600 for S6) without issuing a live Frida RPC."""
        req_gs = _safe_int(grid_size, None)
        if req_gs is not None and req_gs >= 1000:
            return min(req_gs, 1600)
        req_sk = str(season_key or "").strip().lower()
        if req_sk:
            maps_by_key = _world_maps_by_key(_load_world_maps_manifest())
            if req_sk in maps_by_key:
                return _safe_int(maps_by_key[req_sk].get("grid_size"), 1000)
        if isinstance(index, dict):
            if _safe_int(index.get("max_coord"), 0) >= 1000 or _safe_int(index.get("max_point_index"), 0) >= 1_000_000:
                return 1600
        season_info = self._detect_world_season(pid=pid, force_live=False, index=index, _allow_live_query=False)
        return _safe_int(season_info.get("grid_size"), 1000)

    def get_world_map_backdrop(
        self,
        season_key: str = "auto",
        include_zones: bool = True,
        pid: int | None = None,
        force_live: bool = False,
    ) -> dict[str, Any]:
        """Lazily serve cached WebP world map backdrop and optional province/city overlay for the Map Rip radar."""
        manifest = _load_world_maps_manifest()
        maps_by_key = _world_maps_by_key(manifest)
        detected = self._detect_world_season(pid=pid, force_live=bool(force_live))

        req_raw = str(season_key or "").strip()
        req_norm = req_raw.lower()
        is_manual = bool(req_norm and req_norm != "auto" and req_norm in maps_by_key)
        default_key = str(manifest.get("default_map_key") or "pre_season_1").strip().lower()
        resolved_key = req_norm if is_manual else str(detected.get("season_key") or default_key).strip().lower()
        map_entry = maps_by_key.get(resolved_key) or maps_by_key.get(default_key) or next(iter(maps_by_key.values()))

        grid_size = _safe_int(map_entry.get("grid_size"), 1000)
        supports_zones = bool(map_entry.get("supports_zones", False))
        map_file = str(map_entry.get("file") or f"{resolved_key}.webp")
        image_data_uri = _load_world_map_webp_data_uri(map_file)

        zones_data_uri = ""
        if bool(include_zones) and supports_zones:
            zones_meta = manifest.get("zones_overlay") if isinstance(manifest.get("zones_overlay"), dict) else {}
            zones_file = str(zones_meta.get("file") or "zones overlay.webp")
            zones_data_uri = _load_world_map_webp_data_uri(zones_file)

        major_cities = (
            [dict(c) for c in (manifest.get("major_cities") or []) if isinstance(c, dict)]
            if grid_size == 1000
            else []
        )
        ws_ids = map_entry.get("world_season_ids") or [0]
        ws_id = _safe_int(ws_ids[0], 0) if is_manual else _safe_int(detected.get("world_season_id"), _safe_int(ws_ids[0], 0))

        payload: dict[str, Any] = {
            "ok": bool(image_data_uri),
            "requested_key": req_raw if req_raw else "auto",
            "season_key": str(map_entry.get("key") or resolved_key),
            "world_season_id": int(ws_id),
            "label": str(map_entry.get("label") or resolved_key),
            "short_label": str(map_entry.get("short_label") or map_entry.get("label") or resolved_key),
            "grid_size": int(grid_size),
            "y_origin": str(map_entry.get("y_origin") or manifest.get("y_origin") or "top"),
            "width": _safe_int(map_entry.get("width"), 1024),
            "height": _safe_int(map_entry.get("height"), 1024),
            "supports_zones": supports_zones,
            "source": "manual" if is_manual else str(detected.get("source") or "default"),
            "is_live": bool(detected.get("is_live", False)),
            "detected_season": detected,
            "image_data_uri": image_data_uri,
            "zones_data_uri": zones_data_uri,
            "major_cities": major_cities,
            "available_maps": list(detected.get("available_maps") or _format_available_world_maps(manifest)),
        }
        if not image_data_uri:
            payload["error"] = f"World map backdrop asset missing: {map_file}"
        return payload

    def _resolve_map_origin(
        self,
        index: dict[str, Any],
        origin_x: int | None = None,
        origin_y: int | None = None,
        grid_size: int | None = None,
    ) -> dict[str, Any]:
        """Resolve distance origin from explicit coords, live/detected playerUid HQ, or map center."""
        gsize = self._active_map_grid_size(index=index, grid_size=grid_size)
        max_coord = max(999, gsize - 1)
        if origin_x is not None and origin_y is not None:
            try:
                ox, oy = int(origin_x), int(origin_y)
                if 0 <= ox <= max_coord and 0 <= oy <= max_coord:
                    return {"x": ox, "y": oy, "server_id": 0, "source": "custom", "label": f"Custom ({ox}, {oy})"}
            except (TypeError, ValueError):
                pass

        with self._lock:
            puid = str(self.env.get("playerUid") or "").strip()
            env_srv = _safe_int(self.env.get("serverId"), 0)
        if not puid:
            det_path = os.path.join(_resolve_map_data_dir(), "detected_environment.json")
            det = _load_json_cached(det_path, default={})
            if isinstance(det, dict):
                puid = str(det.get("playerUid") or "").strip()
                env_srv = env_srv or _safe_int(det.get("serverId"), 0)

        if puid:
            hq = (index.get("hqs_by_uid") or {}).get(puid)
            if isinstance(hq, dict):
                return {
                    "x": int(hq["x"]),
                    "y": int(hq["y"]),
                    "server_id": int(hq.get("server_id") or env_srv or 0),
                    "source": "player_hq",
                    "label": str(hq.get("name") or "Player HQ"),
                }
        center = gsize // 2
        return {"x": center, "y": center, "server_id": env_srv, "source": "map_center", "label": f"Map Center ({center}, {center})"}

    @staticmethod
    def _build_cache_meta(index: dict[str, Any], now_ts: float) -> dict[str, Any]:
        newest_mtime = float(index.get("newest_mtime") or 0.0)
        age_sec = max(0.0, round(now_ts - newest_mtime, 1)) if newest_mtime > 0 else None
        selected = list(index.get("selected_files") or [])
        avail_fresh = [
            {
                **m,
                "age_sec": max(0.0, round(now_ts - float(m.get("mtime") or 0.0), 1)),
            }
            for m in (index.get("available_files") or [])
            if isinstance(m, dict)
        ]
        return {
            "has_world_cache": bool(index.get("has_world_cache")),
            "selected_files": selected,
            "newest_file": selected[0] if selected else "",
            "available_files": avail_fresh,
            "cache_mtime": newest_mtime,
            "cache_age_sec": age_sec,
            "total_raw_entries": int(index.get("total_raw_entries") or 0),
            "raw_hq_count": int(index.get("raw_hq_count") or 0),
            "deduped_hq_count": int(index.get("deduped_hq_count") or 0),
            "collapsed_duplicates": int(index.get("collapsed_duplicates") or 0),
            "roster_matched_count": int(index.get("roster_matched_count") or 0),
            "servers": list(index.get("servers") or []),
        }

    def get_map_rip_overview(self) -> dict[str, Any]:
        """Return world_map_cache metadata, KPI counts, server/alliance lists, origin, world_season, and schema defaults."""
        data_dir = _resolve_map_data_dir()
        index = _get_world_map_index(data_dir, dedup_by_uid=True)
        now_ts = time.time()
        cache_meta = self._build_cache_meta(index, now_ts)
        world_season = self._detect_world_season(index=index)
        grid_size = _safe_int(world_season.get("grid_size"), 1000)
        origin = self._resolve_map_origin(index, grid_size=grid_size)

        dedup_hqs: list[dict[str, Any]] = index.get("dedup_hqs") or []
        rss_list: list[dict[str, Any]] = index.get("rss") or []

        unshielded_hqs = 0
        shielded_hqs = 0
        hq_20_unsh = 0
        hq_25_unsh = 0
        hq_30_unsh = 0
        al_counts: dict[str, int] = {}

        for hq in dedup_hqs:
            is_sh = int(hq.get("protect_end_time") or 0) > now_ts
            lv = int(hq.get("level") or 0)
            if is_sh:
                shielded_hqs += 1
            else:
                unshielded_hqs += 1
                if lv >= 20:
                    hq_20_unsh += 1
                if lv >= 25:
                    hq_25_unsh += 1
                if lv >= 30:
                    hq_30_unsh += 1
            tag = str(hq.get("tag") or "").strip()
            if tag:
                al_counts[tag] = al_counts.get(tag, 0) + 1

        rss_unocc = 0
        rss_lv6 = 0
        rss_lv6_unocc = 0
        rss_special = 0
        for r in rss_list:
            occ = bool(r.get("occupied"))
            lv = int(r.get("level") or 0)
            if not occ:
                rss_unocc += 1
            if lv >= 6:
                rss_lv6 += 1
                if not occ:
                    rss_lv6_unocc += 1
            if r.get("is_event_node"):
                rss_special += 1

        clusters = _compute_alliance_clusters(
            dedup_hqs,
            now_ts=now_ts,
            cluster_radius=45.0,
            min_members=5,
            origin_x=origin["x"],
            origin_y=origin["y"],
            index_seq=index.get("_index_seq"),
        )

        top_alliances = [
            {"tag": tag, "count": cnt}
            for tag, cnt in sorted(al_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:60]
        ]

        return {
            "ok": True,
            "has_world_cache": bool(index.get("has_world_cache")),
            "cache_meta": cache_meta,
            "counts": {
                "deduped_hqs": len(dedup_hqs),
                "unshielded_hqs": unshielded_hqs,
                "shielded_hqs": shielded_hqs,
                "hq_20_unshielded": hq_20_unsh,
                "hq_25_unshielded": hq_25_unsh,
                "hq_30_unshielded": hq_30_unsh,
                "rss_total": len(rss_list),
                "rss_unoccupied": rss_unocc,
                "rss_lv6_plus": rss_lv6,
                "rss_lv6_unoccupied": rss_lv6_unocc,
                "rss_special_nodes": rss_special,
                "clusters_count": len(clusters),
                "roster_matched_count": int(index.get("roster_matched_count") or 0),
            },
            "servers": list(index.get("servers") or []),
            "alliances": top_alliances,
            "top_clusters": clusters[:10],
            "player_origin": origin,
            "world_season": world_season,
            "schema_defaults": {
                "min_hq": 25,
                "unshielded_only": True,
                "rss_min_level": 6,
                "unoccupied_only": True,
                "cluster_radius": 45.0,
                "min_members": 5,
                "dedup_by_uid": True,
            },
        }

    def get_map_rip_clusters(
        self,
        cluster_radius: float = 45.0,
        min_members: int = 5,
        server_id: int = 0,
        min_hq: int = 1,
        unshielded_only: bool = False,
        search: str = "",
        origin_x: int | None = None,
        origin_y: int | None = None,
    ) -> dict[str, Any]:
        """Compute Dense-Core Hive Extraction alliance clusters over deduplicated HQs."""
        data_dir = _resolve_map_data_dir()
        index = _get_world_map_index(data_dir, dedup_by_uid=True)
        now_ts = time.time()
        ox_arg = _safe_int(origin_x, None)
        oy_arg = _safe_int(origin_y, None)
        origin = self._resolve_map_origin(index, origin_x=ox_arg, origin_y=oy_arg)
        clamped_radius = max(5.0, 45.0 if cluster_radius is None else _safe_float(cluster_radius, 45.0))
        clamped_min_members = max(2, 5 if min_members is None else _safe_int(min_members, 5))
        srv_val = max(0, 0 if server_id is None else _safe_int(server_id, 0))
        hq_val = max(1, 1 if min_hq is None else _safe_int(min_hq, 1))
        clusters = _compute_alliance_clusters(
            index.get("dedup_hqs") or [],
            now_ts=now_ts,
            cluster_radius=clamped_radius,
            min_members=clamped_min_members,
            server_id=srv_val,
            min_hq=hq_val,
            unshielded_only=bool(unshielded_only),
            search=str(search or ""),
            origin_x=origin["x"],
            origin_y=origin["y"],
            index_seq=index.get("_index_seq"),
        )
        return {
            "ok": True,
            "clusters": clusters,
            "count": len(clusters),
            "cluster_radius": clamped_radius,
            "min_members": clamped_min_members,
            "origin": origin,
            "cache_meta": self._build_cache_meta(index, now_ts),
        }

    def query_map_rip_targets(self, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Unified Map Rip target query returning filtered HQs, RSS, alliance clusters, and radar points."""
        f = dict(filters or {})
        mode = str(f.get("mode") or "all").strip().lower()
        search = str(f.get("search") or "").strip().lower()
        srv_raw = f.get("server_id", 0)
        if str(srv_raw).strip().lower() in ("", "all", "0", "none"):
            server_id = 0
        else:
            server_id = max(0, _safe_int(srv_raw, 0))
        alliance_q = str(f.get("alliance") or "").strip().lower()

        shield_state = str(f.get("shield_state") or "").strip().lower()
        if "unshielded_only" in f and not shield_state:
            unshielded_only = bool(f.get("unshielded_only"))
            shield_state = "unshielded" if unshielded_only else "all"
        elif not shield_state:
            shield_state = "unshielded" if mode == "unshielded" else "all"

        min_hq = max(0, _safe_int(f.get("min_hq"), 25))
        max_hq = max(0, _safe_int(f.get("max_hq"), 99))
        min_power = max(0, int(_safe_float(f.get("min_power"), 0.0)))
        max_power = max(0, int(_safe_float(f.get("max_power"), 0.0)))
        known_power_only = bool(f.get("known_power_only", False))
        include_unknown_power = bool(f.get("include_unknown_power", False))

        rss_type_id = _normalize_rss_type_filter(f.get("rss_type"))
        rss_min_level = max(0, _safe_int(f.get("rss_min_level"), 6))
        unoccupied_only = bool(f.get("unoccupied_only", True))

        cluster_radius = max(5.0, _safe_float(f.get("cluster_radius"), 45.0))
        min_members = max(2, _safe_int(f.get("min_members"), 5))
        dedup_by_uid = bool(f.get("dedup_by_uid", True))
        cache_file = str(f.get("cache_file") or "").strip()

        ox_arg = _safe_int(f.get("origin_x"), None)
        oy_arg = _safe_int(f.get("origin_y"), None)
        max_distance = max(0.0, _safe_float(f.get("max_distance"), 0.0))

        sort_by_raw = str(f.get("sort_by") or "level").strip().lower()
        sort_dir = str(f.get("sort_dir") or "desc").strip().lower()
        if sort_by_raw.endswith("_desc"):
            sort_by = sort_by_raw[:-5]
            sort_dir = "desc"
        elif sort_by_raw.endswith("_asc"):
            sort_by = sort_by_raw[:-4]
            sort_dir = "asc"
        else:
            sort_by = sort_by_raw
        if sort_by == "hq":
            sort_by = "level"
        elif sort_by == "dist":
            sort_by = "distance"
        if sort_dir not in ("asc", "desc"):
            sort_dir = "desc"

        raw_limit = _safe_int(f.get("limit"), 250)
        limit = max(1, min(250 if raw_limit == 0 else raw_limit, 2000))
        include_radar_points = bool(f.get("include_radar_points", True))
        include_clusters = bool(f.get("include_clusters", False))

        data_dir = _resolve_map_data_dir()
        index = _get_world_map_index(data_dir, dedup_by_uid=dedup_by_uid, cache_file=cache_file)
        now_ts = time.time()
        grid_size = self._active_map_grid_size(
            index=index,
            grid_size=f.get("grid_size"),
            season_key=str(f.get("season_key") or ""),
        )
        origin = self._resolve_map_origin(index, origin_x=ox_arg, origin_y=oy_arg, grid_size=grid_size)
        ox, oy = int(origin["x"]), int(origin["y"])

        # Store lightweight tuples during filtering/sorting; defer dict() copies & math.sqrt until after slicing [:limit] / [:max_radar]
        matched_hqs: list[tuple[int, dict[str, Any], bool, int, int]] = []
        unshielded_hq_count = 0
        skip_hq_scan = (mode == "rss")
        hq_source = (
            (index.get("hqs_by_server") or {}).get(server_id, [])
            if (server_id > 0 and isinstance(index.get("hqs_by_server"), dict))
            else (index.get("hqs") or [])
        )
        max_dist_sq = max_distance * max_distance if max_distance > 0 else 0.0
        if not skip_hq_scan:
            for hq in hq_source:
                sid = int(hq.get("server_id") or 0)
                if server_id > 0 and sid != server_id:
                    continue
                lv = int(hq.get("level") or 0)
                if lv < min_hq or (max_hq > 0 and lv > max_hq):
                    continue
                pe = int(hq.get("protect_end_time") or 0)
                is_shielded = pe > now_ts
                if shield_state == "unshielded" and is_shielded:
                    continue
                if shield_state == "shielded" and not is_shielded:
                    continue

                tag = str(hq.get("tag") or "")
                if alliance_q and alliance_q not in tag.lower():
                    continue

                pwr = hq.get("power")
                if known_power_only and pwr is None:
                    continue
                if min_power > 0:
                    if pwr is None:
                        if not include_unknown_power:
                            continue
                    elif pwr < min_power:
                        continue
                if max_power > 0 and pwr is not None and pwr > max_power:
                    continue

                dx = hq["x"] - ox
                dy = hq["y"] - oy
                dist_sq = dx * dx + dy * dy
                if max_dist_sq > 0.0 and dist_sq > max_dist_sq:
                    continue

                if search:
                    hay = hq.get("_search_hay") or f"{hq.get('name', '')} {tag} {hq.get('uid', '')} {hq['x']} {hq['y']} ({hq['x']},{hq['y']}) s{sid}".lower()
                    if search not in hay:
                        continue

                if not is_shielded:
                    unshielded_hq_count += 1
                matched_hqs.append((0, hq, is_shielded, pe, dist_sq))

        matched_rss: list[tuple[int, dict[str, Any], bool, int, int]] = []
        skip_rss_for_hq_filters = (
            mode in ("hqs", "unshielded")
            or (
                mode != "rss"
                and (
                    bool(alliance_q)
                    or known_power_only
                    or min_power > 0
                    or shield_state == "shielded"
                )
            )
        )
        if not skip_rss_for_hq_filters:
            rss_source = (
                (index.get("rss_by_server") or {}).get(server_id, [])
                if (server_id > 0 and isinstance(index.get("rss_by_server"), dict))
                else (index.get("rss") or [])
            )
            for r in rss_source:
                sid = int(r.get("server_id") or 0)
                if server_id > 0 and sid != server_id:
                    continue
                lv = int(r.get("level") or 0)
                if lv < rss_min_level:
                    continue
                if unoccupied_only and r.get("occupied"):
                    continue
                if rss_type_id is not None:
                    if rss_type_id < 0 or int(r.get("resource_type") or 0) != rss_type_id:
                        continue

                dx = r["x"] - ox
                dy = r["y"] - oy
                dist_sq = dx * dx + dy * dy
                if max_dist_sq > 0.0 and dist_sq > max_dist_sq:
                    continue

                if search:
                    hay = r.get("_search_hay") or f"{r.get('name', '')} {r.get('resource_name', '')} {r['x']} {r['y']} ({r['x']},{r['y']}) s{sid}".lower()
                    if search not in hay:
                        continue

                matched_rss.append((1, r, False, 0, dist_sq))

        if include_clusters or mode in ("clusters", "all"):
            clusters = _compute_alliance_clusters(
                index.get("dedup_hqs") or [],
                now_ts=now_ts,
                cluster_radius=cluster_radius,
                min_members=min_members,
                server_id=server_id,
                min_hq=max(1, min_hq) if mode == "clusters" else 1,
                unshielded_only=(shield_state == "unshielded") if mode == "clusters" else False,
                search=search if mode == "clusters" else "",
                alliance=alliance_q,
                origin_x=ox,
                origin_y=oy,
                index_seq=index.get("_index_seq"),
            )
            if max_distance > 0:
                clusters = [c for c in clusters if c.get("distance") is None or c["distance"] <= max_distance]
        else:
            clusters = []

        desc = sort_dir == "desc"
        if mode == "clusters":
            def _sort_cluster_key(item: dict[str, Any]) -> Any:
                if sort_by == "power":
                    p = item.get("power")
                    return (p is None, -(p or 0) if desc else (p or 0), -int(item.get("level") or 0))
                if sort_by == "distance":
                    d = item.get("distance")
                    return (d is None, -(d or 0.0) if desc else (d or 0.0), -int(item.get("level") or 0))
                if sort_by == "shield":
                    sh = 1 if item.get("has_shield") else 0
                    return (-sh if desc else sh, -int(item.get("level") or 0))
                if sort_by == "reserve":
                    rv = int(item.get("reserve") or 0)
                    return -rv if desc else rv
                if sort_by == "members":
                    mc = int(item.get("core_count") or item.get("member_count") or 0)
                    return -mc if desc else mc
                lv = int(item.get("level") or 0)
                dist_v = float(item.get("distance") if item.get("distance") is not None else 99999.0)
                return (-lv if desc else lv, dist_v)

            if sort_by == "name":
                pool_sorted = sorted(clusters, key=lambda item: str(item.get("name") or "").lower(), reverse=desc)
            elif sort_by == "alliance":
                pool_sorted = sorted(clusters, key=lambda item: str(item.get("tag") or "").lower(), reverse=desc)
                pool_sorted.sort(key=lambda item: str(item.get("tag") or "") == "")
            else:
                pool_sorted = sorted(clusters, key=_sort_cluster_key)
            total_matching = len(pool_sorted)
            targets = pool_sorted[:limit]
        else:
            if mode in ("hqs", "unshielded"):
                raw_pool = matched_hqs
            elif mode == "rss":
                raw_pool = matched_rss
            else:
                raw_pool = matched_hqs + matched_rss

            def _sort_raw_key(tup: tuple[int, dict[str, Any], bool, int, int]) -> Any:
                kind_flag, item, is_sh, _pe, dist_sq = tup
                if sort_by == "power":
                    p = item.get("power")
                    return (p is None, -(p or 0) if desc else (p or 0), -int(item.get("level") or 0))
                if sort_by == "distance":
                    return (False, -dist_sq if desc else dist_sq, -int(item.get("level") or 0))
                if sort_by == "shield":
                    sh = 1 if (is_sh if kind_flag == 0 else item.get("has_shield")) else 0
                    return (-sh if desc else sh, -int(item.get("level") or 0))
                if sort_by == "reserve":
                    rv = int(item.get("reserve") or 0)
                    return -rv if desc else rv
                if sort_by == "members":
                    mc = int(item.get("core_count") or item.get("member_count") or 0)
                    return -mc if desc else mc
                lv = int(item.get("level") or 0)
                return (-lv if desc else lv, dist_sq)

            if sort_by == "name":
                raw_sorted = sorted(raw_pool, key=lambda t: str(t[1].get("name") or "").lower(), reverse=desc)
            elif sort_by == "alliance":
                raw_sorted = sorted(raw_pool, key=lambda t: str(t[1].get("tag") or "").lower(), reverse=desc)
                raw_sorted.sort(key=lambda t: str(t[1].get("tag") or "") == "")
            else:
                raw_sorted = sorted(raw_pool, key=_sort_raw_key)

            total_matching = len(raw_sorted)
            targets = []
            for kind_flag, obj, is_sh, pe, dist_sq in raw_sorted[:limit]:
                row = dict(obj)
                row.pop("_search_hay", None)
                row["distance"] = round(math.sqrt(dist_sq), 1)
                if kind_flag == 0:
                    row["has_shield"] = is_sh
                    row["shield_left_sec"] = max(0, int(pe - now_ts)) if is_sh else 0
                targets.append(row)

        radar_points: list[dict[str, Any]] = []
        radar_truncated = False
        if include_radar_points:
            max_radar = 3000
            if mode == "rss":
                hq_for_radar: list[tuple[int, dict[str, Any], bool, int, int]] = []
                rss_for_radar = sorted(matched_rss, key=lambda t: (-int(t[1].get("level") or 0), t[4]))
            elif mode in ("hqs", "unshielded"):
                hq_for_radar = sorted(matched_hqs, key=lambda t: (1 if t[2] else 0, -int(t[1].get("level") or 0), t[4]))
                rss_for_radar = []
            else:
                hq_for_radar = sorted(matched_hqs, key=lambda t: (1 if t[2] else 0, -int(t[1].get("level") or 0), t[4]))
                if len(hq_for_radar) >= max_radar:
                    rss_for_radar = []
                    if matched_rss:
                        radar_truncated = True
                else:
                    rss_for_radar = sorted(matched_rss, key=lambda t: (-int(t[1].get("level") or 0), t[4]))

            if not rss_for_radar:
                combined_radar = hq_for_radar
            elif not hq_for_radar:
                combined_radar = rss_for_radar
            else:
                combined_radar = hq_for_radar + rss_for_radar
            if len(combined_radar) > max_radar:
                radar_truncated = True
                combined_radar = combined_radar[:max_radar]
            for kind_flag, pt, is_sh, _pe, dist_sq in combined_radar:
                radar_points.append({
                    "kind": pt["kind"],
                    "uid": pt["uid"],
                    "name": pt["name"],
                    "tag": pt.get("tag") or "",
                    "level": int(pt.get("level") or 0),
                    "x": int(pt["x"]),
                    "y": int(pt["y"]),
                    "server_id": int(pt.get("server_id") or 0),
                    "has_shield": bool(is_sh) if kind_flag == 0 else bool(pt.get("has_shield")),
                    "power": pt.get("power"),
                    "resource_type": pt.get("resource_type"),
                    "resource_name": pt.get("resource_name") or "",
                    "reserve": pt.get("reserve") or 0,
                    "occupied": bool(pt.get("occupied", False)),
                    "is_event_node": bool(pt.get("is_event_node", False)),
                    "distance": round(math.sqrt(dist_sq), 1),
                })

        return {
            "ok": True,
            "mode": mode,
            "targets": targets,
            "total_matching": total_matching,
            "counts": {
                "all": len(matched_hqs) + len(matched_rss),
                "unshielded": unshielded_hq_count,
                "hqs": len(matched_hqs),
                "rss": len(matched_rss),
                "clusters": len(clusters),
            },
            "radar_points": radar_points,
            "radar_truncated": radar_truncated,
            "clusters": clusters,
            "origin": origin,
            "cache_meta": self._build_cache_meta(index, now_ts),
            "servers": list(index.get("servers") or []),
        }

    def search_map_players(
        self,
        query: str = "",
        limit: int = 12,
        server_id: int = 0,
    ) -> dict[str, Any]:
        """Fast unfiltered player/coordinate lookup across all deduplicated cached HQs for the on-map quick-snap bar."""
        raw_q = str(query or "").strip()
        q = raw_q.lower()
        lim = max(1, min(_safe_int(limit, 12), 50))
        srv_filter = max(0, _safe_int(server_id, 0))

        data_dir = _resolve_map_data_dir()
        index = _get_world_map_index(data_dir, dedup_by_uid=True)
        now_ts = time.time()
        grid_size = self._active_map_grid_size(index=index)
        max_coord = max(999, grid_size - 1)
        origin = self._resolve_map_origin(index, grid_size=grid_size)
        ox, oy = int(origin["x"]), int(origin["y"])

        results: list[dict[str, Any]] = []
        if not q:
            return {
                "ok": True,
                "query": raw_q,
                "count": 0,
                "total_matched": 0,
                "grid_size": grid_size,
                "results": results,
            }

        # Support direct coordinate queries like "214, 554", "(214,554)", or "214 554"
        coord_match = re.fullmatch(r"\(?\s*(\d{1,4})\s*[,:\s;/]+\s*(\d{1,4})\s*\)?", raw_q)
        coord_xy: tuple[int, int] | None = None
        if coord_match:
            cx, cy = int(coord_match.group(1)), int(coord_match.group(2))
            if 0 <= cx <= max_coord and 0 <= cy <= max_coord:
                coord_xy = (cx, cy)

        hqs: list[dict[str, Any]] = (
            (index.get("hqs_by_server") or {}).get(srv_filter, [])
            if (srv_filter > 0 and isinstance(index.get("hqs_by_server"), dict))
            else (index.get("dedup_hqs") or index.get("hqs") or [])
        )

        # Strip optional leading/trailing brackets so "[WARG] Hay" matches smoothly
        q_clean = q.replace("[", "").replace("]", "").strip()
        scored: list[tuple[int, int, int, str, dict[str, Any]]] = []
        for hq in hqs:
            hx = int(hq.get("x") or 0)
            hy = int(hq.get("y") or 0)
            name = str(hq.get("name") or "")
            tag = str(hq.get("tag") or "")
            uid = str(hq.get("uid") or "")
            name_l = name.lower()
            tag_l = tag.lower()
            full_l = f"{tag_l} {name_l}".strip() if tag_l else name_l
            bracket_l = f"[{tag_l}] {name_l}".strip() if tag_l else name_l

            rank: int | None = None
            if coord_xy is not None:
                dist_c = math.hypot(hx - coord_xy[0], hy - coord_xy[1])
                if hx == coord_xy[0] and hy == coord_xy[1]:
                    rank = 0
                elif dist_c <= 8.0:
                    rank = 2
            else:
                if name_l == q or name_l == q_clean:
                    rank = 0
                elif bracket_l == q or full_l == q_clean:
                    rank = 1
                elif name_l.startswith(q) or (q_clean and name_l.startswith(q_clean)):
                    rank = 2
                elif q in name_l or (q_clean and q_clean in name_l):
                    rank = 3
                elif q_clean and (q_clean in full_l or q in bracket_l):
                    rank = 4
                elif tag_l and (tag_l == q_clean or tag_l.startswith(q_clean) or q_clean in tag_l):
                    rank = 5
                elif uid and q in uid.lower():
                    rank = 6

            if rank is None:
                continue
            lv = int(hq.get("level") or 0)
            pwr = int(hq.get("power") or 0)
            scored.append((rank, -lv, -pwr, name_l, hq))

        scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        total_matched = len(scored)

        # If user typed explicit coordinates and no HQ is directly on that exact tile, include a direct coordinate jump entry first
        has_exact_coord_hq = coord_xy is not None and any(t[0] == 0 for t in scored)
        if coord_xy is not None and not has_exact_coord_hq:
            cx, cy = coord_xy
            results.append(
                {
                    "kind": "coord",
                    "uid": f"coord:{cx}:{cy}",
                    "name": f"Coordinates ({cx}, {cy})",
                    "tag": "",
                    "level": 0,
                    "x": cx,
                    "y": cy,
                    "server_id": srv_filter or _safe_int(origin.get("server_id"), 0),
                    "has_shield": False,
                    "shield_left_sec": 0,
                    "power": None,
                    "distance": round(math.hypot(cx - ox, cy - oy), 1),
                    "match_rank": 0,
                }
            )

        for rank, _neg_lv, _neg_pwr, _nm, hq in scored[: max(0, lim - len(results))]:
            pe = int(hq.get("protect_end_time") or 0)
            is_sh = pe > now_ts
            row = {
                "kind": "hq",
                "uid": str(hq.get("uid") or ""),
                "name": str(hq.get("name") or "Player"),
                "tag": str(hq.get("tag") or ""),
                "alliance_name": str(hq.get("alliance_name") or ""),
                "level": int(hq.get("level") or 0),
                "x": int(hq["x"]),
                "y": int(hq["y"]),
                "server_id": int(hq.get("server_id") or 0),
                "has_shield": is_sh,
                "shield_left_sec": max(0, int(pe - now_ts)) if is_sh else 0,
                "power": hq.get("power"),
                "distance": round(math.hypot(hq["x"] - ox, hq["y"] - oy), 1),
                "match_rank": rank,
            }
            results.append(row)

        return {
            "ok": True,
            "query": raw_q,
            "count": len(results),
            "total_matched": total_matched + (1 if (coord_xy is not None and not has_exact_coord_hq) else 0),
            "grid_size": grid_size,
            "results": results,
        }

    # ------------------------------------------------------------------
    # Shield-Drop Watchlist & Countdown Pins
    # ------------------------------------------------------------------
    def _watchlist_path(self) -> str:
        return os.path.join(_resolve_map_data_dir(), "json cache", "shield watchlist.json")

    def _load_watchlist_raw(self) -> dict[str, Any]:
        path = self._watchlist_path()
        raw = _load_json_cached(path, default=None)
        if not isinstance(raw, dict):
            return {"players": {}, "alliances": []}
        players = raw.get("players")
        alliances = raw.get("alliances")
        clean_players: dict[str, dict[str, Any]] = {}
        if isinstance(players, dict):
            for k, v in players.items():
                sk = str(k or "").strip()
                if sk and isinstance(v, dict):
                    clean_players[sk] = dict(v)
        clean_alliances: list[str] = []
        seen_a: set[str] = set()
        if isinstance(alliances, list):
            for a in alliances:
                sa = str(a or "").strip()
                if sa and sa.lower() not in seen_a:
                    seen_a.add(sa.lower())
                    clean_alliances.append(sa)
        return {"players": clean_players, "alliances": clean_alliances}

    def _save_watchlist_raw(self, data: dict[str, Any]) -> None:
        path = self._watchlist_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

    def get_shield_watchlist(self) -> dict[str, Any]:
        """Return live-enriched pinned players & alliances sorted by soonest shield expiry."""
        data_dir = _resolve_map_data_dir()
        index = _get_world_map_index(data_dir, dedup_by_uid=True)
        now_ts = time.time()
        cache_meta = self._build_cache_meta(index, now_ts)
        origin = self._resolve_map_origin(index)
        ox, oy = int(origin["x"]), int(origin["y"])

        with self._lock:
            wl = self._load_watchlist_raw()
        pinned_players: dict[str, dict[str, Any]] = wl["players"]
        pinned_alliances: list[str] = wl["alliances"]
        pinned_al_low = {a.lower() for a in pinned_alliances}

        hqs_by_uid: dict[str, dict[str, Any]] = index.get("hqs_by_uid") or {}
        dedup_hqs: list[dict[str, Any]] = index.get("dedup_hqs") or []

        combined: dict[str, dict[str, Any]] = {}
        sources: dict[str, set[str]] = {}

        # 1. Add all explicitly pinned player UIDs (preferring live cache entry when present)
        for uid, saved in pinned_players.items():
            sources.setdefault(uid, set()).add("player")
            live_hq = hqs_by_uid.get(uid)
            if isinstance(live_hq, dict):
                combined[uid] = live_hq
            else:
                combined[uid] = {
                    "uid": uid,
                    "name": str(saved.get("name") or "Player"),
                    "tag": str(saved.get("tag") or ""),
                    "alliance_name": str(saved.get("alliance_name") or ""),
                    "level": _safe_int(saved.get("level"), 0),
                    "x": _safe_int(saved.get("x"), 0),
                    "y": _safe_int(saved.get("y"), 0),
                    "server_id": _safe_int(saved.get("server_id"), 0),
                    "protect_end_time": _safe_int(saved.get("protect_end_time"), 0),
                    "power": saved.get("power"),
                    "_stale_only": True,
                }

        # 2. Add all members of pinned alliance tags
        if pinned_al_low:
            for hq in dedup_hqs:
                tag = str(hq.get("tag") or "").strip()
                if tag and tag.lower() in pinned_al_low:
                    uid = str(hq.get("uid") or "").strip()
                    if not uid:
                        continue
                    sources.setdefault(uid, set()).add("alliance")
                    combined[uid] = hq

        items: list[dict[str, Any]] = []
        counts = {"total": 0, "critical": 0, "soon": 0, "shielded": 0, "dropped": 0}
        for uid, hq in combined.items():
            pe = _safe_int(hq.get("protect_end_time"), 0)
            left_sec = max(0, int(pe - now_ts)) if pe > now_ts else 0
            has_shield = left_sec > 0
            if not has_shield:
                status = "dropped"
                rank = 3
            elif left_sec <= 600:
                status = "critical"
                rank = 0
            elif left_sec <= 1800:
                status = "soon"
                rank = 1
            else:
                status = "shielded"
                rank = 2
            counts["total"] += 1
            counts[status] += 1

            src_set = sources.get(uid, set())
            pin_src = "both" if len(src_set) >= 2 else ("player" if "player" in src_set else "alliance")
            hx = _safe_int(hq.get("x"), 0)
            hy = _safe_int(hq.get("y"), 0)
            items.append(
                {
                    "kind": "hq",
                    "uid": uid,
                    "name": str(hq.get("name") or "Player"),
                    "tag": str(hq.get("tag") or ""),
                    "alliance_name": str(hq.get("alliance_name") or ""),
                    "level": _safe_int(hq.get("level"), 0),
                    "x": hx,
                    "y": hy,
                    "server_id": _safe_int(hq.get("server_id"), 0),
                    "protect_end_time": pe,
                    "has_shield": has_shield,
                    "shield_left_sec": left_sec,
                    "status": status,
                    "pin_source": pin_src,
                    "power": hq.get("power"),
                    "distance": round(math.hypot(hx - ox, hy - oy), 1),
                    "in_cache": not bool(hq.get("_stale_only")),
                    "_sort_rank": rank,
                }
            )

        # Sort soonest active expiry first (critical -> soon -> shielded -> dropped), tie-break by shield_left_sec asc then HQ level desc
        items.sort(key=lambda r: (r["_sort_rank"], r["shield_left_sec"] if r["has_shield"] else 0, -r["level"], r["name"].lower()))
        for r in items:
            r.pop("_sort_rank", None)

        return {
            "ok": True,
            "pinned_uids": sorted(pinned_players.keys()),
            "pinned_alliances": list(pinned_alliances),
            "items": items[:300],
            "total_items": len(items),
            "counts": counts,
            "cache_age_sec": cache_meta.get("cache_age_sec"),
            "server_time": int(now_ts),
        }

    def toggle_watchlist_player(self, uid: str = "", item: dict[str, Any] | None = None) -> dict[str, Any]:
        """Pin or unpin a player UID in the Shield-Drop Watchlist."""
        uid_s = str(uid or (item.get("uid") if isinstance(item, dict) else "") or "").strip()
        if not uid_s:
            return {"ok": False, "error": "Player UID is required to pin."}
        with self._lock:
            wl = self._load_watchlist_raw()
            if uid_s in wl["players"]:
                wl["players"].pop(uid_s, None)
                action = "unpinned"
            else:
                meta = dict(item) if isinstance(item, dict) else {}
                wl["players"][uid_s] = {
                    "uid": uid_s,
                    "name": str(meta.get("name") or "Player"),
                    "tag": str(meta.get("tag") or ""),
                    "level": _safe_int(meta.get("level"), 0),
                    "x": _safe_int(meta.get("x"), 0),
                    "y": _safe_int(meta.get("y"), 0),
                    "server_id": _safe_int(meta.get("server_id"), 0),
                    "protect_end_time": _safe_int(meta.get("protect_end_time"), 0),
                    "power": meta.get("power"),
                    "pinned_at": int(time.time()),
                }
                action = "pinned"
            self._save_watchlist_raw(wl)
        res = self.get_shield_watchlist()
        res["action"] = action
        res["uid"] = uid_s
        return res

    def toggle_watchlist_alliance(self, tag: str = "") -> dict[str, Any]:
        """Pin or unpin an alliance tag in the Shield-Drop Watchlist."""
        tag_s = str(tag or "").strip().strip("[]")
        if not tag_s:
            return {"ok": False, "error": "Alliance tag is required."}
        with self._lock:
            wl = self._load_watchlist_raw()
            existing = [a for a in wl["alliances"] if a.lower() == tag_s.lower()]
            if existing:
                wl["alliances"] = [a for a in wl["alliances"] if a.lower() != tag_s.lower()]
                action = "unpinned"
            else:
                wl["alliances"].append(tag_s)
                action = "pinned"
            self._save_watchlist_raw(wl)
        res = self.get_shield_watchlist()
        res["action"] = action
        res["tag"] = tag_s
        return res

    def clear_shield_watchlist(self) -> dict[str, Any]:
        """Remove all pinned players and alliances from the Shield-Drop Watchlist."""
        with self._lock:
            self._save_watchlist_raw({"players": {}, "alliances": []})
        res = self.get_shield_watchlist()
        res["action"] = "cleared"
        return res

    def verify_shield_watchlist(self, limit: int = 6) -> dict[str, Any]:
        """Step live in-game camera across soonest-expiring pinned coords so AOI refreshes protect_end_time."""
        wl = self.get_shield_watchlist()
        items = list(wl.get("items") or [])
        if not items:
            return {**wl, "verified": 0, "message": "No pinned targets in watchlist to verify."}

        lim = max(1, min(_safe_int(limit, 6), 12))
        targets = items[:lim]
        checked = 0
        last_err = ""
        for it in targets:
            res = self.jump_to_coordinate(int(it["x"]), int(it["y"]), int(it.get("server_id") or 0))
            if not res.get("ok"):
                last_err = str(res.get("error") or "No live game client connected.")
                break
            checked += 1
            time.sleep(0.45)

        if checked == 0:
            return {
                **wl,
                "ok": False,
                "verified": 0,
                "error": last_err or "Launch Last Z first to live-verify pinned shields.",
            }
        # Force cache index reload after AOI sweep
        with _MAP_INDEX_LOCK:
            _WORLD_MAP_INDEX_CACHE.clear()
        fresh = self.get_shield_watchlist()
        fresh["verified"] = checked
        fresh["message"] = f"Verified {checked} pinned target(s) in-game."
        return fresh

    # ------------------------------------------------------------------
    # Multi-Language Hub UI Locales (All 18 Official Last Z Languages)
    # ------------------------------------------------------------------
    def _locales_dir(self) -> str:
        return os.path.abspath(os.path.join(RES_ROOT, "assets", "locales"))

    def _get_saved_ui_language(self) -> str:
        if multi_client_bot is not None:
            try:
                cfg = multi_client_bot.load_config()
                if isinstance(cfg, dict):
                    lang = str(cfg.get("ui_language") or "").strip()
                    if lang:
                        return lang
            except Exception:
                pass
        pref = _load_json_cached(os.path.join(HEINZ_DATA_DIR, "json cache", "ui preferences.json"), default={})
        if isinstance(pref, dict) and pref.get("ui_language"):
            return str(pref["ui_language"]).strip()
        return "en"

    def get_ui_locales(self) -> dict[str, Any]:
        """Return manifest and full translation dictionary for all 18 official Last Z languages."""
        ldir = self._locales_dir()
        man_path = os.path.join(ldir, "manifest.json")
        tr_path = os.path.join(ldir, "translations.json")
        manifest = _load_json_cached(man_path, default={})
        translations = _load_json_cached(tr_path, default={})
        languages = manifest.get("languages") if isinstance(manifest, dict) else []
        if not isinstance(languages, list) or not languages:
            languages = [{"code": "en", "game_id": 14, "native_name": "English", "english_name": "English", "rtl": False, "translate_code": "en"}]
        valid_codes = {str(l.get("code") or "") for l in languages if isinstance(l, dict)}
        cur = self._get_saved_ui_language()
        if cur not in valid_codes:
            cur = "en"
        return {
            "ok": True,
            "current_language": cur,
            "languages": languages,
            "translations": translations if isinstance(translations, dict) else {},
        }

    def set_ui_language(self, lang_code: str = "en", sync_translator: bool = False) -> dict[str, Any]:
        """Persist selected Hub UI language (and optionally sync in-game auto-translator target language)."""
        loc = self.get_ui_locales()
        langs = loc.get("languages") or []
        by_code = {str(l.get("code") or ""): l for l in langs if isinstance(l, dict)}
        code = str(lang_code or "en").strip()
        if code not in by_code:
            return {"ok": False, "error": f"Unsupported language code: {code}"}

        saved = False
        if multi_client_bot is not None:
            try:
                with self._lock:
                    cfg = multi_client_bot.load_config()
                    cfg["ui_language"] = code
                    multi_client_bot.save_config(cfg)
                    self._config_snapshot_cache = None
                saved = True
            except Exception:
                pass
        if not saved:
            pref_path = os.path.join(HEINZ_DATA_DIR, "json cache", "ui preferences.json")
            try:
                os.makedirs(os.path.dirname(pref_path), exist_ok=True)
                with open(pref_path, "w", encoding="utf-8") as fh:
                    json.dump({"ui_language": code}, fh, indent=2)
            except OSError:
                pass

        if sync_translator:
            tcode = str(by_code[code].get("translate_code") or code)
            try:
                self.save_translator_config({"target_lang": tcode, "quiet": True})
            except Exception:
                pass

        return {
            "ok": True,
            "current_language": code,
            "language": by_code[code],
        }

    # ------------------------------------------------------------------
    # Live In-Game Auto-Translator Bridge & Controls
    # ------------------------------------------------------------------
    def _load_translator_mod(self) -> Any:
        cached = getattr(self, "_translator_mod_cache", None)
        if cached is not None:
            return cached
        try:
            tr_path = os.path.join(TOOLS_DIR, "live translator server.py")
            if not os.path.isfile(tr_path):
                tr_path = os.path.join(REPO_ROOT, "tools", "live translator server.py")
            if not os.path.isfile(tr_path):
                return None
            spec = importlib.util.spec_from_file_location("heinz_live_translator_server", tr_path)
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._translator_mod_cache = mod
            return mod
        except Exception as exc:
            self.log(f"Translator module load note: {exc}", "warn")
            return None

    def get_translator_status(self) -> dict[str, Any]:
        """Return live status, config, and metrics for the always-on Last Z in-game auto-translator."""
        mod = self._load_translator_mod()
        if mod is None:
            return {
                "ok": False,
                "running": False,
                "enabled": False,
                "error": "Live translator module unavailable.",
            }
        try:
            cfg = mod.load_translator_config()
            info = mod.ensure_server_running()
            stats = mod.get_stats()
            return {
                "ok": True,
                "running": bool(info.get("running", False)),
                "port": int(info.get("port") or 18765),
                "url": str(info.get("url") or f"http://127.0.0.1:{int(info.get('port') or 18765)}/client.php"),
                "enabled": bool(cfg.get("enabled", True)),
                "auto_translate_chat": bool(cfg.get("auto_translate_chat", True)),
                "target_lang": str(cfg.get("target_lang") or "auto"),
                "has_deepl_key": bool(str(cfg.get("deepl_api_key") or "").strip()),
                "has_gemini_key": bool(str(cfg.get("gemini_api_key") or "").strip()),
                "stats": stats,
            }
        except Exception as exc:
            return {"ok": False, "running": False, "error": str(exc)}

    def save_translator_config(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Save translator preferences and immediately update Lua hooks on all running Last Z clients."""
        mod = self._load_translator_mod()
        if mod is None:
            return {"ok": False, "error": "Live translator module unavailable."}
        data = dict(payload or {})
        quiet = bool(data.pop("quiet", False))
        try:
            cfg = mod.load_translator_config()
            if "enabled" in data:
                cfg["enabled"] = bool(data["enabled"])
            if "auto_translate_chat" in data:
                cfg["auto_translate_chat"] = bool(data["auto_translate_chat"])
            if "target_lang" in data:
                cfg["target_lang"] = str(data["target_lang"] or "auto").strip() or "auto"
            if "deepl_api_key" in data and data["deepl_api_key"] is not None:
                val = str(data["deepl_api_key"]).strip()
                if val != "__KEEP__":
                    cfg["deepl_api_key"] = val
            if "gemini_api_key" in data and data["gemini_api_key"] is not None:
                val = str(data["gemini_api_key"]).strip()
                if val != "__KEEP__":
                    cfg["gemini_api_key"] = val
            mod.save_translator_config(cfg)
            info = mod.ensure_server_running()
            port = int(info.get("port") or 18765)

            # Immediately sync hook onto all running Last Z clients
            hooked_pids: list[int] = []
            if client_discovery is not None:
                try:
                    lua_hook = mod.build_translator_lua_hook(
                        port=port,
                        enabled=bool(cfg.get("enabled", True)),
                        target_lang=str(cfg.get("target_lang") or "auto"),
                        auto_translate_chat=bool(cfg.get("auto_translate_chat", True)),
                    )
                    for proc in (self._discover_running_clients() or []):
                        pid = _safe_int(proc.get("pid"), 0)
                        if pid > 0 and client_discovery._xlua_loaded(pid):
                            ok_eval, _ = client_discovery.frida_eval_lua(pid, lua_hook, timeout=4.0)
                            if ok_eval:
                                hooked_pids.append(pid)
                except Exception:
                    pass

            if not quiet:
                st_lbl = "Enabled" if cfg.get("enabled", True) else "Disabled"
                self.log(
                    f"In-Game Auto-Translator {st_lbl} (target={cfg.get('target_lang', 'auto')}, port={port}, live clients updated={len(hooked_pids)}).",
                    "ok",
                )
            res = self.get_translator_status()
            res["hooked_pids"] = hooked_pids
            return res
        except Exception as exc:
            self.log(f"Translator config error: {exc}", "err")
            return {"ok": False, "error": str(exc)}

    def test_live_translator(
        self,
        text: str = "",
        target_lang: str = "en",
        source_lang: str = "",
    ) -> dict[str, Any]:
        """Run a live test translation through the multi-provider HeinZ translator cascade."""
        mod = self._load_translator_mod()
        if mod is None:
            return {"ok": False, "error": "Live translator module unavailable."}
        src_text = str(text or "").strip()
        if not src_text:
            return {"ok": False, "error": "Enter sample text to translate."}
        try:
            cfg = mod.load_translator_config()
            tl = str(target_lang or cfg.get("target_lang") or "en").strip()
            if tl == "auto":
                tl = self._get_saved_ui_language() or "en"
            res = mod.translate_text(src_text, target_lang=tl, source_lang=str(source_lang or ""), config=cfg)
            return {"ok": True, **res}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Standalone Launcher Gate, Real Game Engine Manager & Account Vault
    # ------------------------------------------------------------------
    def _load_engine_manager_mod(self) -> Any:
        cached = getattr(self, "_engine_manager_mod_cache", None)
        if cached is not None:
            return cached
        try:
            em_path = os.path.join(TOOLS_DIR, "game engine manager.py")
            if not os.path.isfile(em_path):
                em_path = os.path.join(REPO_ROOT, "tools", "game engine manager.py")
            if not os.path.isfile(em_path):
                return None
            spec = importlib.util.spec_from_file_location("heinz_game_engine_manager", em_path)
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._engine_manager_mod_cache = mod
            return mod
        except Exception as exc:
            self.log(f"Engine manager load note: {exc}", "warn")
            return None

    def _load_account_vault_mod(self) -> Any:
        cached = getattr(self, "_account_vault_mod_cache", None)
        if cached is not None:
            return cached
        try:
            av_path = os.path.join(TOOLS_DIR, "account launcher vault.py")
            if not os.path.isfile(av_path):
                av_path = os.path.join(REPO_ROOT, "tools", "account launcher vault.py")
            if not os.path.isfile(av_path):
                return None
            spec = importlib.util.spec_from_file_location("heinz_account_launcher_vault", av_path)
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._account_vault_mod_cache = mod
            return mod
        except Exception as exc:
            self.log(f"Account vault load note: {exc}", "warn")
            return None

    def _heinz_login_prefs_path(self) -> str:
        base_dir = os.environ.get("HEINZ_DATA_DIR") or HEINZ_DATA_DIR
        return os.path.join(base_dir, "json cache", "heinz login prefs.json")

    def _read_heinz_login_prefs(self) -> dict[str, Any]:
        path = self._heinz_login_prefs_path()
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                if isinstance(raw, dict):
                    return {
                        "remember": bool(raw.get("remember", True)),
                        "identifier": str(raw.get("identifier") or "").strip()[:120],
                    }
        except Exception:
            pass
        return {"remember": True, "identifier": ""}

    def _write_heinz_login_prefs(self, remember: bool, identifier: str) -> None:
        """Persist only non-secret display identifier preference (NEVER stores passwords or tokens)."""
        path = self._heinz_login_prefs_path()
        payload = {
            "remember": bool(remember),
            "identifier": str(identifier or "").strip()[:120] if remember else "",
        }
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = f"{path}.{os.getpid()}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            os.replace(tmp, path)
        except OSError:
            pass

    def authenticate_heinz_account(
        self,
        identifier: str = "",
        password: str = "",
        remember: bool = True,
        skip: bool = False,
    ) -> dict[str, Any]:
        """Future-ready HeinZ account login gate (stores zero passwords; allows local/guest entry)."""
        del password  # Intentionally never stored or logged; ready to forward to future auth API.
        if bool(skip):
            with self._lock:
                self._heinz_auth_session = {"signed_in": True, "mode": "guest", "identifier": "Guest"}
            return {"ok": True, "signed_in": True, "mode": "guest", "identifier": "Guest"}

        clean_id = str(identifier or "").strip()[:120]
        if not clean_id:
            return {"ok": False, "error": "Enter your email or username, or click Continue as Guest."}
        self._write_heinz_login_prefs(bool(remember), clean_id)
        with self._lock:
            self._heinz_auth_session = {"signed_in": True, "mode": "local", "identifier": clean_id}
        return {"ok": True, "signed_in": True, "mode": "local", "identifier": clean_id}

    def sign_out_heinz_account(self) -> dict[str, Any]:
        """Return the standalone popup to the Login To Account screen."""
        with self._lock:
            self._heinz_auth_session = {"signed_in": False, "mode": "", "identifier": ""}
        return {"ok": True, "signed_in": False}

    def get_launcher_boot_state(self, check_remote: bool = False) -> dict[str, Any]:
        """Return standalone launcher boot status, auth state, game engine state, and bound accounts (zero hooks attached)."""
        em = self._load_engine_manager_mod()
        av = self._load_account_vault_mod()
        engine_status: dict[str, Any] = {"ok": False, "installed": False, "detected_local_installs": []}
        if em is not None:
            try:
                engine_status = em.get_engine_status(check_remote=bool(check_remote))
            except Exception as exc:
                engine_status = {"ok": False, "installed": False, "error": str(exc), "detected_local_installs": []}
        accounts: list[dict[str, Any]] = []
        if av is not None:
            try:
                accounts = av.list_bound_accounts(sync_discovered=True)
            except Exception:
                accounts = []
        with self._engine_task_lock:
            task_copy = dict(self._engine_task_state)
        prefs = self._read_heinz_login_prefs()
        with self._lock:
            auth_copy = dict(getattr(self, "_heinz_auth_session", {"signed_in": False, "mode": "", "identifier": ""}))
        auth_copy["remember"] = bool(prefs.get("remember", True))
        auth_copy["remembered_identifier"] = str(prefs.get("identifier") or "")
        return {
            "ok": True,
            "enhanced_active": bool(getattr(self, "_enhanced_active", False)),
            "auth_state": auth_copy,
            "engine_status": engine_status,
            "engine_task": task_copy,
            "accounts": accounts,
        }

    def get_engine_task_progress(self) -> dict[str, Any]:
        with self._engine_task_lock:
            return {"ok": True, **dict(self._engine_task_state)}

    def cancel_engine_task(self) -> dict[str, Any]:
        self._engine_cancel_ev.set()
        with self._engine_task_lock:
            self._engine_task_state["stage"] = "cancelling"
        return {"ok": True, "cancelling": True}

    def start_engine_import(self, source_game_dir: str = "") -> dict[str, Any]:
        """Import an existing local Last Z Game/ folder into HeinZ's standalone engine/Game/ directory."""
        em = self._load_engine_manager_mod()
        if em is None:
            return {"ok": False, "error": "Game Engine Manager module unavailable."}
        with self._engine_task_lock:
            if self._engine_task_state.get("running"):
                return {"ok": False, "error": "An engine task is already running."}
            src = str(source_game_dir or "").strip()
            if not src:
                local_list = em.detect_existing_local_installs() or []
                if local_list:
                    src = str(local_list[0].get("game_dir") or "")
            if not src:
                return {"ok": False, "error": "No existing Last Z installation found. Use Download Official Engine instead."}
            self._engine_cancel_ev.clear()
            self._engine_task_state.update({
                "running": True,
                "action": "import",
                "stage": "importing",
                "pct": 0.0,
                "done_files": 0,
                "total_files": 0,
                "done_bytes": 0,
                "total_bytes": 0,
                "speed_mbps": 0.0,
                "current_file": "Preparing local engine import...",
                "ok": True,
                "message": "",
                "error": "",
            })

        def _worker() -> None:
            def _cb(p: dict[str, Any]) -> None:
                with self._engine_task_lock:
                    self._engine_task_state.update(p)
            try:
                res = em.import_local_engine(src, progress_cb=_cb)
                with self._engine_task_lock:
                    self._engine_task_state.update({
                        "running": False,
                        "stage": "done" if res.get("ok") else "error",
                        "pct": 100.0 if res.get("ok") else self._engine_task_state.get("pct", 0.0),
                        "ok": bool(res.get("ok")),
                        "message": str(res.get("message") or "Engine imported."),
                        "error": str(res.get("error") or ""),
                    })
            except Exception as exc:
                with self._engine_task_lock:
                    self._engine_task_state.update({
                        "running": False,
                        "stage": "error",
                        "ok": False,
                        "error": str(exc),
                    })

        threading.Thread(target=_worker, daemon=True, name="EngineImportWorker").start()
        return {"ok": True, "started": True, "source_game_dir": src}

    def start_engine_download(self) -> dict[str, Any]:
        """Download or differentially update the official Last Z Windows game engine from ReadyGo's CDN."""
        em = self._load_engine_manager_mod()
        if em is None:
            return {"ok": False, "error": "Game Engine Manager module unavailable."}
        with self._engine_task_lock:
            if self._engine_task_state.get("running"):
                return {"ok": False, "error": "An engine task is already running."}
            self._engine_cancel_ev.clear()
            self._engine_task_state.update({
                "running": True,
                "action": "download",
                "stage": "manifest",
                "pct": 0.0,
                "done_files": 0,
                "total_files": 0,
                "done_bytes": 0,
                "total_bytes": 0,
                "speed_mbps": 0.0,
                "current_file": "Checking official Last Z manifest...",
                "ok": True,
                "message": "",
                "error": "",
            })

        def _worker() -> None:
            def _cb(p: dict[str, Any]) -> None:
                with self._engine_task_lock:
                    self._engine_task_state.update(p)
            try:
                res = em.download_or_update_engine(progress_cb=_cb, cancel_event=self._engine_cancel_ev)
                with self._engine_task_lock:
                    self._engine_task_state.update({
                        "running": False,
                        "stage": "cancelled" if res.get("cancelled") else ("done" if res.get("ok") else "error"),
                        "pct": 100.0 if (res.get("ok") and not res.get("cancelled")) else self._engine_task_state.get("pct", 0.0),
                        "ok": bool(res.get("ok")),
                        "message": str(res.get("message") or ""),
                        "error": str(res.get("error") or ""),
                    })
            except Exception as exc:
                with self._engine_task_lock:
                    self._engine_task_state.update({
                        "running": False,
                        "stage": "error",
                        "ok": False,
                        "error": str(exc),
                    })

        threading.Thread(target=_worker, daemon=True, name="EngineDownloadWorker").start()
        return {"ok": True, "started": True}

    def bind_email_account(self, email: str = "", label: str = "", window_style: str = "borderless") -> dict[str, Any]:
        av = self._load_account_vault_mod()
        if av is None:
            return {"ok": False, "error": "Account Vault module unavailable."}
        try:
            res = av.bind_new_account(email=email, label=label, window_style=window_style)
            res["accounts"] = av.list_bound_accounts(sync_discovered=True)
            return res
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def update_bound_account(
        self,
        account_id: str = "",
        email: str | None = None,
        label: str | None = None,
        window_style: str | None = None,
    ) -> dict[str, Any]:
        av = self._load_account_vault_mod()
        if av is None:
            return {"ok": False, "error": "Account Vault module unavailable."}
        try:
            res = av.update_account(account_id=account_id, email=email, label=label, window_style=window_style)
            res["accounts"] = av.list_bound_accounts(sync_discovered=True)
            return res
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def remove_bound_account(self, account_id: str = "", clear_session: bool = False) -> dict[str, Any]:
        av = self._load_account_vault_mod()
        if av is None:
            return {"ok": False, "error": "Account Vault module unavailable."}
        try:
            res = av.unbind_account(account_id=account_id, clear_session=bool(clear_session))
            res["accounts"] = av.list_bound_accounts(sync_discovered=True)
            return res
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def reset_bound_account_code(self, account_id: str = "") -> dict[str, Any]:
        av = self._load_account_vault_mod()
        if av is None:
            return {"ok": False, "error": "Account Vault module unavailable."}
        try:
            res = av.reset_account_verification(account_id=account_id)
            res["accounts"] = av.list_bound_accounts(sync_discovered=True)
            return res
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _exit_for_vanilla_bg(self) -> None:
        time.sleep(1.3)
        try:
            win = getattr(self, "_window", None)
            if win is not None and hasattr(win, "destroy"):
                win.destroy()
        except Exception:
            pass
        time.sleep(0.6)
        try:
            self.shutdown()
        except Exception:
            pass
        os._exit(0)

    def launch_from_launcher_gate(
        self,
        account_id: str = "",
        mode: str = "vanilla",
        window_style: str = "borderless",
    ) -> dict[str, Any]:
        """Launch a bound account in Pure Vanilla (0 hooks, exits HeinZ) or Enhanced (opens Hub + full engine)."""
        av = self._load_account_vault_mod()
        if av is None:
            return {"ok": False, "error": "Account Vault module unavailable."}
        norm_mode = str(mode or "vanilla").strip().lower()
        if norm_mode not in ("vanilla", "enhanced"):
            return {"ok": False, "error": f"Invalid launch mode: {mode}"}

        try:
            res = av.launch_bound_account(account_id=account_id, mode=norm_mode, window_style=window_style)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        if not res.get("ok"):
            return res

        if norm_mode == "vanilla":
            # Pure Vanilla: NEVER activate Enhanced monitors, NEVER attach Frida, exit HeinZ cleanly!
            threading.Thread(target=self._exit_for_vanilla_bg, daemon=True, name="VanillaCleanExit").start()
            return {**res, "enhanced_active": False, "exiting_heinz": True}

        # Enhanced mode: activate full Hub + 180 FPS daemon + Live Translator + Always-On automation
        self.activate_enhanced_mode()
        lbl = str(res.get("label") or "").strip()
        if lbl:
            with self._lock:
                self.selected_client_label = lbl
                if res.get("pid"):
                    self.selected_client_pid = int(res["pid"])
        return {**res, "enhanced_active": True, "exiting_heinz": False}

    def enter_enhanced_hub_only(self) -> dict[str, Any]:
        """Activate Enhanced Mode and open the Command Hub UI directly without launching a game window yet."""
        self.activate_enhanced_mode()
        return {"ok": True, "enhanced_active": True}

    def query_map_targets(self, search: str = "", category: str = "all", max_results: int = 50, **kwargs: Any) -> dict[str, Any]:
        """Search world_map_cache_*.json (or CSV fallback) for instant UI display."""
        data_dir = _resolve_map_data_dir()
        index = _get_world_map_index(data_dir, dedup_by_uid=bool(kwargs.get("dedup_by_uid", True)))
        q = (search or "").strip().lower()
        cat = str(category or "all").strip().lower()
        raw_max_res = _safe_int(max_results, 50)
        limit = max(1, min(50 if raw_max_res == 0 else raw_max_res, 500))

        if index.get("has_world_cache"):
            now_ts = time.time()
            origin = self._resolve_map_origin(index)
            ox, oy = int(origin["x"]), int(origin["y"])
            cache_meta = self._build_cache_meta(index, now_ts)
            results: list[dict[str, Any]] = []

            def _hq_matches(hq: dict[str, Any], unsh_only: bool = False) -> bool:
                pe = int(hq.get("protect_end_time") or 0)
                is_sh = pe > now_ts
                if unsh_only and is_sh:
                    return False
                if not q:
                    return True
                hay = f"{hq.get('name', '')} {hq.get('tag', '')} {hq.get('uid', '')} {hq['x']} {hq['y']} ({hq['x']},{hq['y']})".lower()
                return q in hay

            def _fmt_hq(hq: dict[str, Any]) -> dict[str, Any]:
                pe = int(hq.get("protect_end_time") or 0)
                is_sh = pe > now_ts
                row = dict(hq)
                row.pop("_search_hay", None)
                row["has_shield"] = is_sh
                row["shield_left_sec"] = max(0, int(pe - now_ts)) if is_sh else 0
                row["distance"] = round(math.hypot(hq["x"] - ox, hq["y"] - oy), 1)
                return row

            if cat in ("all", "bases", "hqs", "unshielded"):
                unsh_only = cat == "unshielded"
                hqs_sorted = sorted(
                    (hq for hq in (index.get("hqs") or []) if _hq_matches(hq, unsh_only=unsh_only)),
                    key=lambda h: (-int(h.get("level") or 0), math.hypot(h["x"] - ox, h["y"] - oy)),
                )
                for hq in hqs_sorted[:limit]:
                    results.append(_fmt_hq(hq))

            if cat in ("rss", "resources") or (cat == "all" and len(results) < limit and q):
                rss_sorted = sorted(
                    (
                        r for r in (index.get("rss") or [])
                        if not q or q in f"{r.get('name', '')} {r.get('resource_name', '')} {r['x']} {r['y']}".lower()
                    ),
                    key=lambda r: (bool(r.get("occupied")), -int(r.get("level") or 0), math.hypot(r["x"] - ox, r["y"] - oy)),
                )
                for r in rss_sorted[: max(0, limit - len(results))]:
                    row = dict(r)
                    row.pop("_search_hay", None)
                    row["distance"] = round(math.hypot(r["x"] - ox, r["y"] - oy), 1)
                    results.append(row)

            if cat == "clusters":
                clusters = _compute_alliance_clusters(
                    index.get("dedup_hqs") or [],
                    now_ts=now_ts,
                    cluster_radius=45.0 if kwargs.get("cluster_radius") is None else _safe_float(kwargs.get("cluster_radius"), 45.0),
                    min_members=5 if kwargs.get("min_members") is None else _safe_int(kwargs.get("min_members"), 5),
                    search=q,
                    origin_x=ox,
                    origin_y=oy,
                    index_seq=index.get("_index_seq"),
                )
                results = clusters[:limit]

            if cat in ("all", "seasonal") and len(results) < limit:
                for s_item in (index.get("seasonal") or []):
                    hay = f"{s_item.get('name', '')} {s_item.get('tag', '')} {s_item['x']} {s_item['y']}".lower()
                    if not q or q in hay:
                        row = dict(s_item)
                        row.pop("_search_hay", None)
                        row["distance"] = round(math.hypot(s_item["x"] - ox, s_item["y"] - oy), 1)
                        results.append(row)
                        if len(results) >= limit:
                            break

            return {
                "ok": True,
                "results": results,
                "count": len(results),
                "search": search,
                "source": "world_map_cache",
                "has_world_cache": True,
                "has_bases_file": True,
                "has_seasonal_file": bool(index.get("seasonal")),
                "cache_meta": cache_meta,
            }

        import csv
        bases_csv = os.path.join(data_dir, "map all bases.csv")
        if not os.path.exists(bases_csv):
            bases_csv = os.path.join(data_dir, "map_all_bases.csv")
        seasonal_csv = os.path.join(data_dir, "map all seasonal structures.csv")
        if not os.path.exists(seasonal_csv):
            seasonal_csv = os.path.join(data_dir, "map_all_seasonal_structures.csv")

        results = []
        if cat in ("all", "bases", "hqs", "unshielded") and os.path.exists(bases_csv):
            try:
                with open(bases_csv, "r", encoding="utf-8-sig") as f:
                    for row in csv.DictReader(f):
                        name = str(row.get("name") or "")
                        tag = str(row.get("alliance_tag") or "")
                        aname = str(row.get("alliance_name") or "")
                        x = str(row.get("x") or "")
                        y = str(row.get("y") or "")
                        has_shield = str(row.get("has_shield") or "").lower() in ("true", "1")
                        if cat == "unshielded" and has_shield:
                            continue
                        hay = f"{name} {tag} {aname} {x} {y}".lower()
                        if not q or q in hay:
                            results.append({
                                "kind": "base",
                                "name": name or "Unknown Player",
                                "tag": tag,
                                "alliance": aname,
                                "level": int(row.get("level") or 0),
                                "x": int(row.get("x") or 0),
                                "y": int(row.get("y") or 0),
                                "has_shield": has_shield,
                                "server_id": int(row.get("server_id") or 0),
                            })
                            if len(results) >= limit:
                                break
            except Exception as exc:
                self.log(f"Map query error (bases): {exc}", "warn")

        if cat in ("all", "seasonal") and os.path.exists(seasonal_csv) and len(results) < limit:
            try:
                with open(seasonal_csv, "r", encoding="utf-8-sig") as f:
                    for row in csv.DictReader(f):
                        name = str(row.get("name") or "")
                        tag = str(row.get("alliance_tag") or "")
                        x = str(row.get("x") or "")
                        y = str(row.get("y") or "")
                        hay = f"{name} {tag} {x} {y}".lower()
                        if not q or q in hay:
                            results.append({
                                "kind": "seasonal",
                                "name": name or "Seasonal Structure",
                                "tag": tag,
                                "alliance": "",
                                "level": int(row.get("level") or 0),
                                "x": int(row.get("x") or 0),
                                "y": int(row.get("y") or 0),
                                "has_shield": False,
                                "server_id": 0,
                            })
                            if len(results) >= limit:
                                break
            except Exception as exc:
                self.log(f"Map query error (seasonal): {exc}", "warn")

        return {
            "ok": True,
            "results": results,
            "count": len(results),
            "search": search,
            "source": "csv",
            "has_world_cache": False,
            "has_bases_file": os.path.exists(bases_csv),
            "has_seasonal_file": os.path.exists(seasonal_csv),
        }

    def jump_to_coordinate(self, x: int, y: int, server_id: int = 0, grid_size: int | None = None) -> dict[str, Any]:
        """Snap in-game camera to specific map coordinates in the active Last Z client."""
        gsize = self._active_map_grid_size(grid_size=grid_size)
        max_coord = max(999, gsize - 1)
        tx = _safe_int(x, None)
        ty = _safe_int(y, None)
        if tx is None or ty is None or not (0 <= tx <= max_coord) or not (0 <= ty <= max_coord):
            return {"ok": False, "error": f"Invalid map coordinates ({x!r}, {y!r}); expected 0..{max_coord}."}
        srv = _safe_int(server_id, 0)
        if srv is None or srv < 0:
            srv = 0
        self.log(f"Snapping camera to ({tx}, {ty}) in-game...", "info")
        script = self.find_script("jump to target.py")
        extra = [str(tx), str(ty)]
        if srv > 0:
            extra.extend(["--server", str(srv)])
        extra.extend(self._pid_args())
        try:
            res = self._subproc_run(_build_script_cmd(script, extra), timeout=12, env=self._subprocess_env())
        except subprocess.TimeoutExpired:
            err = "Jump command timed out"
            self.log(f"Jump camera note: {err}", "warn")
            return {"ok": False, "error": err}
        out = ((res.stdout or "") + "\n" + (res.stderr or "")).strip()
        if "JUMP_OK" in out or "Navigated to" in out:
            msg = f"Camera snapped to ({tx}, {ty})" + (f" on State #{srv}" if srv > 0 else "")
            self.log(msg, "ok")
            return {"ok": True, "message": msg}
        err = out or "Failed to jump camera in-game."
        self.log(f"Jump camera note: {err}", "warn")
        return {"ok": False, "error": err}

    def get_account_inventory(self, pid: int | None = None, force_live: bool = False) -> dict[str, Any]:
        """Fetch and return categorized, visually formatted inventory items for target client."""
        _, target_pid, proc, account_label, clean_label = self._resolve_client_context(pid)
        raw_clean = clean_label if clean_label and clean_label != "client" else ""
        sync_key = f"inv:{raw_clean or (f'pid_{target_pid}' if target_pid else 'none')}"
        cache_dir = os.path.join(HEINZ_DATA_DIR, "json cache")
        cache_candidates = [
            os.path.join(cache_dir, f"{raw_clean}_inventory.json") if raw_clean else None,
            os.path.join(cache_dir, f"pid_{target_pid}_inventory.json") if target_pid else None,
            os.path.join(cache_dir, f"{clean_label}_inventory.json") if clean_label == "client" else None,
        ]
        cached_path = next((c for c in cache_candidates if c and os.path.isfile(c)), None)
        write_cache_path = (
            os.path.join(cache_dir, f"{raw_clean}_inventory.json")
            if raw_clean
            else (os.path.join(cache_dir, f"pid_{target_pid}_inventory.json") if target_pid else None)
        )

        raw_items: list[dict[str, Any]] = []
        is_live = False
        loaded_cached = False
        with self._lock:
            last_sync = self._live_sync_ts.get(sync_key, 0.0)
        cache_fresh = bool(cached_path and (time.time() - last_sync) < 60.0)

        if not force_live and cache_fresh and cached_path:
            cdata = _load_json_cached(cached_path)
            if isinstance(cdata, (list, dict)):
                raw_items = _as_list(cdata, dicts_only=True)
                loaded_cached = True

        if (not loaded_cached or force_live) and client_discovery is not None and target_pid and proc is not None:
            try:
                if client_discovery._xlua_loaded(target_pid):
                    lua_inv = _LUA_JSON_SER + r"""
                    local items = _jarr()
                    pcall(function()
                        local idata = DataCenter and DataCenter.ItemData
                        local itmMgr = DataCenter and DataCenter.ItemTemplateManager
                        local itmDic = itmMgr and itmMgr.itemDic
                        local getTplFn = itmMgr and itmMgr.GetItemTemplate
                        local loc = Localization
                        local locTbl = loc and loc.id_to_string
                        local locGet = loc and loc.GetString
                        if idata and idata.ItemInfos then
                            for uuid, itm in pairs(idata.ItemInfos) do
                                pcall(function()
                                    if type(itm) ~= "table" then return end
                                    local iId = tonumber(itm.itemId or itm.id or 0) or 0
                                    local cnt = tonumber(itm.count or itm.num or itm.itemNum or 0) or 0
                                    if cnt > 0 and iId > 0 then
                                        local tpl = itmDic and itmDic[iId]
                                        if not tpl and getTplFn then
                                            local okT, tVal = pcall(getTplFn, itmMgr, iId)
                                            if okT then tpl = tVal end
                                        end
                                        local nm = tpl and (tpl.name or tpl.itemName)
                                        local rawNm = nm and tostring(nm) or ""
                                        local locNm = rawNm
                                        if rawNm ~= "" and loc then
                                            local direct = locTbl and locTbl[rawNm]
                                            if direct and direct ~= "" then
                                                locNm = tostring(direct)
                                            elseif locGet then
                                                local okL, s = pcall(locGet, loc, rawNm)
                                                if okL and s and s ~= "" then locNm = tostring(s) end
                                            end
                                        end
                                        local dsc = tpl and (tpl.desc or tpl.itemDesc)
                                        local rawDsc = dsc and tostring(dsc) or ""
                                        local locDsc = rawDsc
                                        if rawDsc ~= "" and loc then
                                            local direct = locTbl and locTbl[rawDsc]
                                            if direct and direct ~= "" then
                                                locDsc = tostring(direct)
                                            elseif locGet then
                                                local okL, s = pcall(locGet, loc, rawDsc)
                                                if okL and s and s ~= "" then locDsc = tostring(s) end
                                            end
                                        end
                                        local itype = tpl and (tpl.itemType or tpl.type) or (itm.type or 0)
                                        local qlty = tpl and (tpl.quality or tpl.itemQuality) or 1
                                        local prm = tpl and tpl.param or ""
                                        table.insert(items, {
                                            itemId = iId,
                                            uuid = tostring(uuid),
                                            count = cnt,
                                            name = locNm,
                                            rawName = rawNm,
                                            desc = locDsc,
                                            type = tonumber(itype) or 0,
                                            quality = tonumber(qlty) or 1,
                                            icon = tostring(tpl and (tpl.icon or tpl.itemIcon) or ""),
                                            param = tostring(prm)
                                        })
                                    end
                                end)
                            end
                        end
                    end)
                    return ser(items)
                    """
                    ok, res = client_discovery.frida_eval_lua(target_pid, lua_inv, timeout=6.0)
                    if ok and res:
                        parsed = json.loads(res)
                        if isinstance(parsed, (list, dict)):
                            raw_items = _as_list(parsed, dicts_only=True)
                            is_live = True
                            loaded_cached = True
                            with self._lock:
                                self._live_sync_ts[sync_key] = time.time()
                            if write_cache_path:
                                _atomic_write_json(write_cache_path, raw_items)
            except Exception as exc:
                self.log(f"Game client busy during vault sync; using cached snapshot ({exc})", "warn")

        if not is_live and not loaded_cached and cached_path:
            cdata = _load_json_cached(cached_path)
            if isinstance(cdata, (list, dict)):
                raw_items = _as_list(cdata, dicts_only=True)
                loaded_cached = True

        with self._lock:
            has_sel_lbl = bool(self.selected_client_label)
        is_linked = bool(is_live or (loaded_cached and (proc is not None or (has_sel_lbl and clean_label))))

        if not is_linked or not raw_items:
            return {
                "ok": True,
                "is_linked": is_linked,
                "account_label": account_label or "",
                "pid": target_pid,
                "is_live": is_live,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "stats": {
                    "total_items": 0,
                    "total_count": 0,
                    "chests_count": 0,
                    "chests_count_fmt": "0",
                    "hero_shards_count": 0,
                    "hero_shards_count_fmt": "0",
                    "categories": {"all": 0, "speedups": 0, "chests": 0, "heroes": 0, "gear": 0, "other": 0},
                    "speedups": {
                        "total_mins": 0, "total_fmt": "0m",
                        "building_mins": 0, "building_fmt": "0m",
                        "research_mins": 0, "research_fmt": "0m",
                        "training_mins": 0, "training_fmt": "0m",
                        "healing_mins": 0, "healing_fmt": "0m",
                        "universal_mins": 0, "universal_fmt": "0m",
                    },
                },
                "items": [],
            }

        dialog = _get_dialog_dict()
        processed_items: list[dict[str, Any]] = []
        speedup_stats = {
            "total_mins": 0, "building_mins": 0, "research_mins": 0,
            "training_mins": 0, "healing_mins": 0, "universal_mins": 0,
        }
        chests_count = 0
        hero_shards_count = 0
        cat_counts = {"all": 0, "speedups": 0, "chests": 0, "heroes": 0, "gear": 0, "other": 0}

        for it in raw_items:
            iid = int(it.get("itemId") or 0)
            cnt = int(it.get("count") or 0)
            if cnt <= 0:
                continue

            name_id = str(it.get("nameId") or "")
            alt_id = str(it.get("altNameId") or "")
            raw_name = str(it.get("name") or "").strip()
            if not raw_name or raw_name == f"Item_{iid}":
                raw_name = dialog.get(name_id) or dialog.get(alt_id) or dialog.get(str(iid)) or FALLBACK_ITEM_NAMES.get(iid) or f"Item #{iid}"

            param = str(it.get("param") or "").strip()
            if "{0}" in raw_name:
                p_sub = param
                if not p_sub:
                    if iid in (210110, 210119): p_sub = "5"
                    elif iid in (210112, 210120, 210163, 210129): p_sub = "1"
                    elif iid == 210122: p_sub = "8"
                    elif "fragment" in raw_name.lower(): p_sub = "Hero"
                    else: p_sub = "1"
                raw_name = raw_name.replace("{0}", p_sub)

            raw_desc = str(it.get("desc") or "").strip()
            if not raw_desc:
                raw_desc = dialog.get(str(it.get("descId") or "")) or ""
            clean_desc = re.sub(r"<color=[^>]+>", "", raw_desc).replace("</color>", "").replace(r"\n", " ").strip()

            itype = int(it.get("type") or it.get("itemType") or 0)
            qlty = int(it.get("quality") or 1)
            cat, rarity, qlty = _deduce_category_and_rarity(raw_name, itype, qlty, iid)

            sp_mins, sp_type = _parse_speedup_info(raw_name, iid)
            sp_total_fmt = ""
            if sp_mins > 0:
                total_m = sp_mins * cnt
                speedup_stats["total_mins"] += total_m
                sp_key = {
                    "Building": "building_mins",
                    "Research": "research_mins",
                    "Training": "training_mins",
                    "Healing": "healing_mins",
                }.get(sp_type, "universal_mins")
                speedup_stats[sp_key] += total_m
                sp_total_fmt = _format_duration_mins(total_m)

            if cat == "chests" or itype == 204 or any(w in raw_name.lower() for w in ("chest", "crate", "box")):
                chests_count += cnt

            if cat == "heroes" and ("fragment" in raw_name.lower() or "shard" in raw_name.lower()):
                hero_shards_count += cnt

            cat_counts["all"] += 1
            if cat in cat_counts:
                cat_counts[cat] += 1

            processed_items.append({
                "id": iid,
                "uuid": str(it.get("uuid") or ""),
                "name": raw_name,
                "count": cnt,
                "count_fmt": _format_count_num(cnt),
                "category": cat,
                "quality": qlty,
                "rarity": rarity,
                "type": itype,
                "desc": clean_desc,
                "speedup_mins": sp_mins,
                "speedup_type": sp_type,
                "speedup_total_fmt": sp_total_fmt,
            })

        processed_items.sort(key=lambda x: (x["quality"], x["count"]), reverse=True)

        return {
            "ok": True,
            "is_linked": True,
            "account_label": account_label,
            "pid": target_pid,
            "is_live": is_live,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "total_items": len(processed_items),
                "total_count": sum(x["count"] for x in processed_items),
                "chests_count": chests_count,
                "chests_count_fmt": _format_count_num(chests_count),
                "hero_shards_count": hero_shards_count,
                "hero_shards_count_fmt": _format_count_num(hero_shards_count),
                "categories": cat_counts,
                "speedups": {
                    "total_mins": speedup_stats["total_mins"],
                    "total_fmt": _format_duration_mins(speedup_stats["total_mins"]),
                    "building_mins": speedup_stats["building_mins"],
                    "building_fmt": _format_duration_mins(speedup_stats["building_mins"]),
                    "research_mins": speedup_stats["research_mins"],
                    "research_fmt": _format_duration_mins(speedup_stats["research_mins"]),
                    "training_mins": speedup_stats["training_mins"],
                    "training_fmt": _format_duration_mins(speedup_stats["training_mins"]),
                    "healing_mins": speedup_stats["healing_mins"],
                    "healing_fmt": _format_duration_mins(speedup_stats["healing_mins"]),
                    "universal_mins": speedup_stats["universal_mins"],
                    "universal_fmt": _format_duration_mins(speedup_stats["universal_mins"]),
                },
            },
            "items": processed_items,
        }

    def _find_asset(self, filename: str) -> str:
        candidates = []
        if getattr(sys, "frozen", False):
            if hasattr(sys, "_MEIPASS"):
                candidates.append(os.path.join(str(getattr(sys, "_MEIPASS")), "assets", filename))
                candidates.append(os.path.join(str(getattr(sys, "_MEIPASS")), filename))
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            candidates.append(os.path.join(exe_dir, "_internal", "assets", filename))
            candidates.append(os.path.join(exe_dir, "assets", filename))
        here = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(here, "assets", filename))
        candidates.append(os.path.join(here, "..", "launcher", "assets", filename))
        candidates.append(os.path.join(here, "..", "data", filename))
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return os.path.join(here, "assets", filename)

    @staticmethod
    def _read_cached_badges_in_bag(
        cache_dir: str,
        raw_clean: str,
        target_pid: int | None,
        allow_legacy_global: bool,
    ) -> int:
        """Read item 200034 (Research Badge) count from the account's cached inventory snapshot."""
        inv_candidates: list[str] = []
        if raw_clean:
            inv_candidates.append(os.path.join(cache_dir, f"{raw_clean}_inventory.json"))
        if target_pid:
            inv_candidates.append(os.path.join(cache_dir, f"pid_{target_pid}_inventory.json"))
        if allow_legacy_global:
            inv_candidates.extend([
                os.path.join(cache_dir, "all_inventory_with_tpl.json"),
                next((p for p in (os.path.join(DATA_DIR, "json cache", "all inventory with tpl.json"), os.path.join(DATA_DIR, "json cache", "all_inventory_with_tpl.json")) if os.path.isfile(p)), os.path.join(DATA_DIR, "json cache", "all inventory with tpl.json")),
                next((p for p in (os.path.join(DATA_DIR, "all inventory with tpl.json"), os.path.join(DATA_DIR, "all_inventory_with_tpl.json")) if os.path.isfile(p)), os.path.join(DATA_DIR, "all inventory with tpl.json")),
            ])

        def _item_cnt(entry: dict[str, Any]) -> int:
            raw_cnt = entry.get("count")
            if raw_cnt is None:
                raw_cnt = entry.get("num")
            if raw_cnt is None:
                raw_cnt = entry.get("itemNum")
            return max(0, _safe_int(raw_cnt, 0))

        for cand in inv_candidates:
            if not os.path.isfile(cand):
                continue
            inv_data = _load_json_cached(cand)
            if not isinstance(inv_data, (list, dict)):
                continue
            total = 0
            if isinstance(inv_data, dict) and isinstance(inv_data.get("items"), (list, dict)):
                for it in _as_list(inv_data.get("items"), dicts_only=True):
                    raw_iid = it.get("itemId") if it.get("itemId") is not None else it.get("id")
                    if _safe_int(raw_iid, 0) == 200034:
                        total += _item_cnt(it)
                return total
            if isinstance(inv_data, list):
                for it in inv_data:
                    if not isinstance(it, dict):
                        continue
                    raw_iid = it.get("itemId") if it.get("itemId") is not None else it.get("id")
                    if _safe_int(raw_iid, 0) == 200034:
                        total += _item_cnt(it)
                return total
            for k, v in inv_data.items():
                if isinstance(v, dict):
                    raw_iid = v.get("itemId")
                    if raw_iid is None:
                        raw_iid = v.get("id")
                    if raw_iid is None:
                        raw_iid = k
                    if _safe_int(raw_iid, 0) == 200034:
                        total += _item_cnt(v)
                elif not isinstance(v, bool) and _safe_int(k, 0) == 200034:
                    total += max(0, _safe_int(v, 0))
            return total
        return 0

    def get_tech_calculator_data(self, pid: int | None = None, force_live: bool = False) -> dict[str, Any]:
        """Calculate invested and remaining badges per tier and whole tree, with live client sync."""
        _, target_pid, proc, account_label, clean_label = self._resolve_client_context(pid)
        raw_clean = clean_label if clean_label and clean_label != "client" else ""
        account_label = account_label or (f"PID {target_pid}" if target_pid else "Account")
        sync_key = f"sci:{raw_clean or (f'pid_{target_pid}' if target_pid else 'none')}"
        cache_dir = os.path.join(HEINZ_DATA_DIR, "json cache")
        cache_candidates: list[str] = []
        if raw_clean:
            cache_candidates.append(os.path.join(cache_dir, f"{raw_clean}_tech_progress.json"))
            cache_candidates.append(os.path.join(cache_dir, f"{raw_clean}_tech_tree_progress.json"))
        if target_pid:
            cache_candidates.append(os.path.join(cache_dir, f"pid_{target_pid}_tech_progress.json"))
        allow_legacy_global = (
            pid is None
            and (proc is None or str(proc.get("role") or "").lower() == "main")
            and (not raw_clean or raw_clean == "main")
        )
        if allow_legacy_global:
            cache_candidates.extend([
                os.path.join(cache_dir, "tech_tree_progress.json"),
                os.path.join(DATA_DIR, "json cache", "tech_tree_progress.json"),
                os.path.join(DATA_DIR, "tech_tree_progress.json"),
            ])
        write_cache_path = (
            os.path.join(cache_dir, f"{raw_clean}_tech_progress.json")
            if raw_clean
            else (os.path.join(cache_dir, f"pid_{target_pid}_tech_progress.json") if target_pid else None)
        )

        def _extract_levels(c_data: Any) -> dict[str, int]:
            out_lv: dict[str, int] = {}
            if isinstance(c_data, dict):
                if "levels" in c_data and isinstance(c_data.get("levels"), dict):
                    c_data = c_data["levels"]
                if "trees" in c_data:
                    for t in _as_list(c_data.get("trees"), dicts_only=True):
                        nodes_src = _as_list(t.get("nodes"), dicts_only=True)
                        if not nodes_src and "tiers" in t:
                            for tr in _as_list(t.get("tiers"), dicts_only=True):
                                nodes_src.extend(_as_list(tr.get("nodes"), dicts_only=True))
                        for n in nodes_src:
                            tid = n.get("tech_id")
                            if tid is None:
                                tid = n.get("id")
                            if tid is not None:
                                lv_raw = n.get("level")
                                if lv_raw is None:
                                    lv_raw = n.get("current_level")
                                out_lv[str(tid)] = max(0, _safe_int(lv_raw, 0))
                else:
                    for k, v in c_data.items():
                        if isinstance(v, bool):
                            continue
                        iv = _safe_int(v, None)
                        if iv is not None and iv >= 0:
                            out_lv[str(k)] = iv
            return out_lv

        user_levels: dict[str, int] = {}
        researching_raw: set[str] = set()
        live_badges_in_bag: int | None = None
        is_live = False
        loaded_cached = False
        with self._lock:
            last_sync = self._live_sync_ts.get(sync_key, 0.0)
        cache_fresh = (time.time() - last_sync) < 60.0

        if not force_live and cache_fresh:
            for cand in cache_candidates:
                if not os.path.isfile(cand):
                    continue
                cdata = _load_json_cached(cand)
                if isinstance(cdata, (dict, list)):
                    user_levels = _extract_levels(cdata)
                    loaded_cached = True
                    break

        if (not loaded_cached or force_live) and client_discovery is not None and target_pid and proc is not None:
            try:
                if client_discovery._xlua_loaded(target_pid):
                    lua_sci = _LUA_JSON_SER + r"""
                    local levels = _jobj()
                    local researching = _jarr()
                    local badges_in_bag = -1
                    pcall(function()
                        if DataCenter and DataCenter.ScienceDataManager and DataCenter.ScienceDataManager.allScience then
                            for id, s in pairs(DataCenter.ScienceDataManager.allScience) do
                                local lv = (type(s) == "table" and (s.level or s.lv)) or (type(s) == "number" and s) or 0
                                levels[tostring(id)] = tonumber(lv) or 0
                            end
                        end
                    end)
                    local seen_res = {}
                    local function _add_res_id(raw)
                        if raw == nil then return end
                        local s = tostring(raw)
                        if s == "" or s == "0" then return end
                        local n = tonumber(raw)
                        if n ~= nil and n <= 0 then return end
                        if not seen_res[s] then
                            seen_res[s] = true
                            table.insert(researching, s)
                        end
                    end
                    local function _pick_sid(entry)
                        local keys = { "scienceId", "techId", "itemId", "id" }
                        for _, k in ipairs(keys) do
                            local v = entry[k]
                            if v ~= nil then
                                local s = tostring(v)
                                local n = tonumber(v)
                                if s ~= "" and s ~= "0" and (n == nil or n > 0) then
                                    return v
                                end
                            end
                        end
                        return nil
                    end
                    local function _inspect_q(entry)
                        local et = type(entry)
                        if et == "number" or et == "string" then
                            _add_res_id(entry)
                            return
                        end
                        if et ~= "table" then return end
                        local st = entry.state
                        if st ~= nil then
                            local stn = tonumber(st)
                            if stn ~= nil and stn == 0 then return end
                        end
                        local sid = _pick_sid(entry)
                        if sid ~= nil then
                            _add_res_id(sid)
                        end
                    end
                    pcall(function()
                        local sm = DataCenter and DataCenter.ScienceManager
                        if sm and type(sm.GetScienceQueue) == "function" then
                            local okQ, qRes = pcall(sm.GetScienceQueue, sm)
                            if okQ and qRes ~= nil then
                                if type(qRes) == "table" then
                                    if qRes.scienceId ~= nil or qRes.techId ~= nil or qRes.itemId ~= nil or qRes.id ~= nil or qRes.uuid ~= nil or qRes.state ~= nil then
                                        _inspect_q(qRes)
                                    else
                                        for _, item in pairs(qRes) do
                                            _inspect_q(item)
                                        end
                                    end
                                else
                                    _inspect_q(qRes)
                                end
                            end
                        end
                    end)
                    if #researching == 0 then
                        pcall(function()
                            local qm = DataCenter and DataCenter.QueueDataManager
                            if qm and type(qm.GetAllQueueByType) == "function" then
                                local qType = (NewQueueType and tonumber(NewQueueType.Science)) or 6
                                local okQ, qs = pcall(qm.GetAllQueueByType, qm, qType)
                                if okQ and type(qs) == "table" then
                                    for _, q in pairs(qs) do
                                        if type(q) == "table" then
                                            local st = tonumber(q.state or 0) or 0
                                            if st == 2 or st == 3 then
                                                _inspect_q(q)
                                            end
                                        end
                                    end
                                end
                            end
                        end)
                    end
                    local function _scan_bag_table(tbl)
                        local total = 0
                        for k, itm in pairs(tbl) do
                            if type(itm) == "table" then
                                local iid = tonumber(itm.itemId) or 0
                                if iid <= 0 then iid = tonumber(itm.id) or 0 end
                                if iid <= 0 then iid = tonumber(k) or 0 end
                                if iid == 200034 then
                                    local cnt = tonumber(itm.count) or tonumber(itm.num) or tonumber(itm.itemNum) or 0
                                    if cnt > 0 then total = total + math.floor(cnt) end
                                end
                            elseif tonumber(k) == 200034 then
                                local cnt = tonumber(itm) or 0
                                if cnt > 0 then total = total + math.floor(cnt) end
                            end
                        end
                        return total
                    end
                    pcall(function()
                        local im = DataCenter and DataCenter.ItemManager
                        if im then
                            if type(im.GetItemNum) == "function" then
                                local okN, num = pcall(im.GetItemNum, im, 200034)
                                local v = okN and tonumber(num) or nil
                                if v ~= nil and v >= 0 then
                                    badges_in_bag = math.floor(v)
                                end
                            end
                            if badges_in_bag < 0 and type(im.allItems) == "table" then
                                badges_in_bag = _scan_bag_table(im.allItems)
                            end
                        end
                        if badges_in_bag < 0 then
                            local idata = DataCenter and DataCenter.ItemData
                            if idata then
                                if type(idata.GetItemCount) == "function" then
                                    local okN, num = pcall(idata.GetItemCount, idata, 200034)
                                    local v = okN and tonumber(num) or nil
                                    if v ~= nil and v >= 0 then
                                        badges_in_bag = math.floor(v)
                                    end
                                end
                                if badges_in_bag < 0 and type(idata.ItemInfos) == "table" then
                                    badges_in_bag = _scan_bag_table(idata.ItemInfos)
                                end
                            end
                        end
                    end)
                    local payload = _jobj({
                        levels = levels,
                        researching = researching,
                        badges_in_bag = badges_in_bag,
                    })
                    return ser(payload)
                    """
                    ok, res = client_discovery.frida_eval_lua(target_pid, lua_sci, timeout=6.0)
                    if ok and res:
                        parsed = json.loads(res)
                        if isinstance(parsed, dict) and (
                            "levels" in parsed or "researching" in parsed or "badges_in_bag" in parsed
                        ):
                            raw_levels = parsed.get("levels")
                            if isinstance(raw_levels, (dict, list)):
                                user_levels = _extract_levels(_as_dict(raw_levels))
                            else:
                                user_levels = {}
                            for rid in _as_list(parsed.get("researching")):
                                s_rid = str(rid).strip()
                                if s_rid and s_rid != "0":
                                    researching_raw.add(s_rid)
                            raw_bag = _safe_int(parsed.get("badges_in_bag"), None)
                            if raw_bag is not None and raw_bag >= 0:
                                live_badges_in_bag = raw_bag
                            is_live = True
                            loaded_cached = True
                            with self._lock:
                                self._live_sync_ts[sync_key] = time.time()
                            if write_cache_path:
                                _atomic_write_json(write_cache_path, user_levels)
                        elif isinstance(parsed, (dict, list)):
                            norm_sci = _as_dict(parsed)
                            user_levels = _extract_levels(norm_sci)
                            is_live = True
                            loaded_cached = True
                            with self._lock:
                                self._live_sync_ts[sync_key] = time.time()
                            if write_cache_path:
                                _atomic_write_json(write_cache_path, user_levels)
            except Exception as exc:
                self.log(f"Game client busy during research sync; using cached levels ({exc})", "warn")

        if not is_live and not loaded_cached:
            for cand in cache_candidates:
                if not os.path.isfile(cand):
                    continue
                cdata = _load_json_cached(cand)
                if isinstance(cdata, (dict, list)):
                    user_levels = _extract_levels(cdata)
                    loaded_cached = True
                    break

        badges_in_bag = (
            live_badges_in_bag
            if live_badges_in_bag is not None
            else self._read_cached_badges_in_bag(cache_dir, raw_clean, target_pid, allow_legacy_global)
        )

        matrix_file = self._find_asset("tech badge matrix.json")
        matrix = _load_json_cached(matrix_file)
        if not isinstance(matrix, dict):
            return {"ok": False, "error": "Research matrix asset (tech badge matrix.json) is missing."}

        known_node_ids: set[str] = set()
        for tree in matrix.get("trees", []):
            for tr in tree.get("tiers", []):
                for node in tr.get("nodes", []):
                    known_node_ids.add(str(node["id"]))

        researching_ids: set[str] = set()
        for rid in researching_raw:
            if rid in known_node_ids:
                researching_ids.add(rid)
            elif rid.isdigit():
                base_id = str((int(rid) // 100) * 100)
                researching_ids.add(base_id if base_id in known_node_ids else rid)
            else:
                researching_ids.add(rid)

        overall_invested = 0
        overall_remaining = 0
        overall_total = 0
        overall_levels_done = 0
        overall_levels_total = 0
        trees_maxed = 0
        trees_with_badges_count = 0
        all_trees_maxed_count = 0
        calculated_trees = []

        for tree in matrix.get("trees", []):
            t_id = tree["tab_id"]
            t_name = tree["tree_name"]

            tree_invested = 0
            tree_remaining = 0
            nodes_done = 0
            nodes_total = 0
            levels_done = 0
            levels_total = 0

            calc_tiers = []
            for tr in tree.get("tiers", []):
                tier_num = tr["tier"]
                tier_invested = 0
                tier_remaining = 0
                tier_levels_done = 0
                tier_levels_total = 0
                tier_nodes_done = 0
                tier_nodes_total = 0
                calc_nodes = []

                for node in tr.get("nodes", []):
                    nid = str(node["id"])
                    max_lv = max(0, _safe_int(node.get("max_level"), 0))
                    cur_lv = max(0, min(max_lv, _safe_int(user_levels.get(nid, 0), 0)))
                    raw_costs = [max(0, _safe_int(c, 0)) for c in _as_list(node.get("badge_costs"))]
                    if len(raw_costs) < max_lv:
                        costs = raw_costs + [0] * (max_lv - len(raw_costs))
                    elif len(raw_costs) > max_lv:
                        costs = raw_costs[:max_lv]
                    else:
                        costs = raw_costs

                    n_inv = sum(costs[:cur_lv])
                    n_rem = sum(costs[cur_lv:])
                    n_tot = n_inv + n_rem
                    node_is_maxed = (max_lv > 0 and cur_lv >= max_lv)

                    tier_invested += n_inv
                    tier_remaining += n_rem
                    tier_nodes_total += 1
                    if node_is_maxed:
                        tier_nodes_done += 1
                    tier_levels_done += cur_lv
                    tier_levels_total += max_lv

                    nodes_total += 1
                    if node_is_maxed:
                        nodes_done += 1
                    levels_done += cur_lv
                    levels_total += max_lv

                    next_badge = costs[cur_lv] if cur_lv < max_lv and cur_lv < len(costs) else 0

                    calc_nodes.append({
                        "id": nid,
                        "name": node["name"],
                        "current_level": cur_lv,
                        "max_level": max_lv,
                        "col": node["col"],
                        "badge_costs": costs,
                        "total_badges": n_tot,
                        "has_badges": n_tot > 0,
                        "badges_invested": n_inv,
                        "badges_remaining": n_rem,
                        "is_maxed": node_is_maxed,
                        "next_level_badges": next_badge,
                        "is_researching": nid in researching_ids,
                        "can_afford_next": (not node_is_maxed and next_badge > 0 and badges_in_bag >= next_badge),
                    })

                tr_tot = tier_invested + tier_remaining
                tier_is_maxed = (tier_levels_total > 0 and tier_levels_done >= tier_levels_total)
                tr_pct = (
                    round((tier_invested / tr_tot) * 100, 1)
                    if tr_tot > 0
                    else (round((tier_levels_done / tier_levels_total) * 100, 1) if tier_levels_total > 0 else 0.0)
                )
                tree_invested += tier_invested
                tree_remaining += tier_remaining

                calc_tiers.append({
                    "tier": tier_num,
                    "total_badges": tr_tot,
                    "badges_invested": tier_invested,
                    "badges_remaining": tier_remaining,
                    "has_badges": tr_tot > 0,
                    "progress_pct": tr_pct,
                    "is_maxed": tier_is_maxed,
                    "levels_done": tier_levels_done,
                    "levels_total": tier_levels_total,
                    "nodes_done": tier_nodes_done,
                    "nodes_total": tier_nodes_total,
                    "nodes": calc_nodes,
                })

            tree_tot = tree_invested + tree_remaining
            is_tree_maxed = (levels_total > 0 and levels_done >= levels_total)
            tree_pct = (
                round((tree_invested / tree_tot) * 100, 1)
                if tree_tot > 0
                else (round((levels_done / levels_total) * 100, 1) if levels_total > 0 else 0.0)
            )

            overall_levels_done += levels_done
            overall_levels_total += levels_total
            if is_tree_maxed:
                all_trees_maxed_count += 1

            if tree_tot > 0:
                trees_with_badges_count += 1
                if is_tree_maxed:
                    trees_maxed += 1
                overall_invested += tree_invested
                overall_remaining += tree_remaining
                overall_total += tree_tot

            calculated_trees.append({
                "tab_id": t_id,
                "tree_name": t_name,
                "order": tree.get("order", 99),
                "total_badges": tree_tot,
                "badges_invested": tree_invested,
                "badges_remaining": tree_remaining,
                "has_badges": tree_tot > 0,
                "net_badges_deficit": max(0, tree_remaining - badges_in_bag),
                "can_max_now": (tree_remaining > 0 and badges_in_bag >= tree_remaining),
                "progress_pct": tree_pct,
                "is_maxed": is_tree_maxed,
                "nodes_done": nodes_done,
                "nodes_total": nodes_total,
                "levels_done": levels_done,
                "levels_total": levels_total,
                "tiers": calc_tiers,
            })

        overall_levels_pct = (
            round((overall_levels_done / overall_levels_total) * 100, 1)
            if overall_levels_total > 0
            else 0.0
        )
        overall_pct = (
            round((overall_invested / overall_total) * 100, 1)
            if overall_total > 0
            else overall_levels_pct
        )

        return {
            "ok": True,
            "is_live": is_live,
            "account_label": account_label,
            "overall": {
                "total_badges_invested": overall_invested,
                "total_badges_remaining": overall_remaining,
                "total_badges_whole_game": overall_total,
                "overall_percentage": overall_pct,
                "trees_maxed_count": trees_maxed,
                "trees_with_badges_count": trees_with_badges_count,
                "trees_total_count": len(calculated_trees),
                "all_trees_maxed_count": all_trees_maxed_count,
                "overall_levels_done": overall_levels_done,
                "overall_levels_total": overall_levels_total,
                "overall_levels_percentage": overall_levels_pct,
                "badges_in_bag": badges_in_bag,
                "net_badges_deficit": max(0, overall_remaining - badges_in_bag),
            },
            "trees": calculated_trees,
        }

    def get_migration_calculator_data(self, state_id: int = 694, player_query: str = "") -> dict[str, Any]:
        """Return migration score, pass costs, tier matrix, and top alliance rosters for target state."""
        def _tier_info(mp: int):
            mp = int(mp or 0)
            if mp <= 0:
                return ("Unknown", "N/A", 0, "No combat data recorded", "#94A3B8")
            if mp <= 20000000:
                return ("Regular", "Che1", 10, "Unlimited standard state migration capacity", "#34D399")
            elif mp <= 35000000:
                return ("Mid Tier", "Che2", 20, "Standard active combatant tier", "#38BDF8")
            elif mp <= 50000000:
                return ("Advanced", "Che3", 35, "High combatant tier, requires careful state planning", "#F59E0B")
            else:
                return ("Elite", "Che4", 50, "Requires President Approval (Strict 3-Slot State Cap)", "#EF4444")

        def _build_player_entry(p: dict[str, Any]) -> dict[str, Any]:
            mp = p.get("migratePower") or p.get("power") or 0
            t_name, t_code, passes, desc, col = _tier_info(mp)
            return {
                "name": p.get("name"),
                "uid": str(p.get("uid") or ""),
                "power": p.get("power", 0),
                "migratePower": mp,
                "serverId": p.get("serverId", 0),
                "allianceName": p.get("allianceName", ""),
                "tag": p.get("abbr", ""),
                "tier_name": t_name,
                "tier_code": t_code,
                "passes": passes,
                "desc": desc,
                "color": col,
            }

        profiles_file = next((p for p in (os.path.join(HEINZ_DATA_DIR, "json cache", "all players profile cache.json"), os.path.join(HEINZ_DATA_DIR, "json cache", "all_players_profile_cache.json")) if os.path.isfile(p)), os.path.join(HEINZ_DATA_DIR, "json cache", "all players profile cache.json"))
        if not os.path.exists(profiles_file):
            profiles_file = os.path.join(DATA_DIR, "json cache", "all_players_profile_cache.json")

        matched_players = []
        target_player = None

        all_p = _load_json_cached(profiles_file)
        if isinstance(all_p, dict):
            q = str(player_query or "").strip().lower()
            if q:
                for p in all_p.values():
                    name = str(p.get("name") or "").lower()
                    uid = str(p.get("uid") or "")
                    if q in name or q == uid:
                        matched_players.append(_build_player_entry(p))
                        if len(matched_players) >= 8:
                            break
            if matched_players:
                target_player = matched_players[0]
            elif not q:
                with self._lock:
                    env = dict(self.env or {})
                pname = str(env.get("playerName") or "").strip()
                if pname and pname not in ("Player", "Offline", "Unknown"):
                    for p in all_p.values():
                        if str(p.get("name", "")).lower() == pname.lower():
                            target_player = _build_player_entry(p)
                            break

        if not target_player:
            with self._lock:
                env = dict(self.env or {})
            live_name = str(env.get("playerName") or "").strip()
            if live_name and live_name not in ("Player", "Offline", "Unknown"):
                live_pw = int(env.get("playerPower") or 0)
                t_name, t_code, passes, desc, col = _tier_info(live_pw)
                target_player = {
                    "name": live_name,
                    "uid": str(env.get("playerUid") or ""),
                    "power": live_pw,
                    "migratePower": live_pw,
                    "serverId": int(env.get("serverId") or 0),
                    "allianceName": str(env.get("allianceName") or ""),
                    "tag": str(env.get("allianceTag") or ""),
                    "tier_name": t_name,
                    "tier_code": t_code,
                    "passes": passes,
                    "desc": desc,
                    "color": col,
                }

        st_num = int(state_id or (self.env or {}).get("serverId") or 694)
        roster_candidates = [
            os.path.join(HEINZ_DATA_DIR, "json cache", "bracket data", f"state_{st_num}", "top10_alliance_rosters.json"),
            os.path.join(DATA_DIR, "json cache", "bracket data", f"state_{st_num}", "top10_alliance_rosters.json"),
        ]
        roster_file = next((c for c in roster_candidates if os.path.exists(c)), None)

        alliances_data = []
        total_state_passes = 0
        total_elite_imports = 0

        alliances = _load_json_cached(roster_file) if roster_file else None
        if isinstance(alliances, list):
            try:
                for al in alliances:
                    tag = al.get("abbr") or al.get("tag") or ""
                    name = al.get("name") or al.get("allianceName") or tag
                    leader = al.get("leader") or "N/A"
                    members = al.get("members") or []

                    al_passes = 0
                    che1, che2, che3, che4 = 0, 0, 0, 0
                    elites = []

                    for m in members:
                        mp = m.get("migratePower") or m.get("power", 0)
                        t_n, t_c, pass_cnt, d, col = _tier_info(mp)
                        al_passes += pass_cnt
                        if t_c == "Che1": che1 += 1
                        elif t_c == "Che2": che2 += 1
                        elif t_c == "Che3": che3 += 1
                        elif t_c == "Che4":
                            che4 += 1
                            elites.append({
                                "name": m.get("name"),
                                "power": m.get("power", 0),
                                "migratePower": mp,
                                "passes": pass_cnt,
                            })

                    total_state_passes += al_passes
                    total_elite_imports += che4

                    alliances_data.append({
                        "tag": tag,
                        "name": name,
                        "leader": leader,
                        "member_count": len(members),
                        "total_passes": al_passes,
                        "che1": che1,
                        "che2": che2,
                        "che3": che3,
                        "che4": che4,
                        "elite_members": elites,
                    })
            except Exception as exc:
                self.log(f"State #{st_num} roster parsing note: {exc}", "warn")

        rules = [
            {"code": "Che1", "name": "Regular", "range": "≤ 20,000,000 Power", "passes": 10, "rules": "Unlimited standard state migration capacity", "color": "#34D399"},
            {"code": "Che2", "name": "Mid Tier", "range": "20,000,001 - 35,000,000", "passes": 20, "rules": "Standard active combatant tier", "color": "#38BDF8"},
            {"code": "Che3", "name": "Advanced", "range": "35,000,001 - 50,000,000", "passes": 35, "rules": "High combatant tier, requires careful state planning", "color": "#F59E0B"},
            {"code": "Che4", "name": "Elite", "range": "> 50,000,000 Power", "passes": 50, "rules": "Requires President Approval (Strict 3-Slot State Cap)", "color": "#EF4444"},
        ]

        return {
            "ok": True,
            "target_player": target_player,
            "matched_players": matched_players,
            "state_id": st_num,
            "total_state_passes": total_state_passes,
            "total_elite_imports": total_elite_imports,
            "alliances": alliances_data,
            "rules": rules,
        }

    def quick_shield(self, pid: int | None = None) -> dict[str, Any]:
        """Activate a peace shield immediately from bag using passive Lua invocation."""
        target_pid = _safe_int(pid, None) if pid is not None else None
        if not target_pid:
            with self._lock:
                clients_snap = list(self.running_clients)
                sel_pid = self.selected_client_pid or self.target_pid
            if sel_pid and any(int(c.get("pid") or 0) == int(sel_pid) for c in clients_snap):
                target_pid = int(sel_pid)
            else:
                for c in clients_snap:
                    if c.get("pid"):
                        target_pid = int(c["pid"])
                        break
        if not target_pid:
            return {"ok": False, "msg": "No active game client found to shield."}

        if client_discovery is None or not client_discovery._xlua_loaded(target_pid):
            return {"ok": False, "msg": f"Client PID {target_pid} is not ready or xlua is not loaded."}

        lua_shield = _LUA_JSON_SER + r"""
        local dc = DataCenter
        local idata = dc and dc.ItemData
        local itm = dc and dc.ItemTemplateManager
        local used = false
        local usedName = ""
        local usedId = 0
        pcall(function()
            if idata and idata.ItemInfos then
                for uuid, info in pairs(idata.ItemInfos) do
                    if type(info) == "table" then
                        local cnt = tonumber(info.count or info.num or 0) or 0
                        if cnt > 0 then
                            local tmpl = info.template
                            if not tmpl and itm and itm.GetItemTemplate then
                                pcall(function() tmpl = itm:GetItemTemplate(tonumber(info.itemId)) end)
                            end
                            local rawNm = tmpl and tmpl.name
                            local nm = ""
                            if Localization and Localization.GetString and rawNm then
                                pcall(function() nm = Localization:GetString(tostring(rawNm)) or "" end)
                            end
                            nm = tostring((nm ~= "" and nm) or rawNm or ""):lower()
                            if nm:find("shield") or nm:find("peace") or nm:find("truce") then
                                if idata.UseTool then
                                    local okU = pcall(function() idata:UseTool(tonumber(info.itemId), 1) end)
                                    if okU then
                                        used = true
                                        usedName = nm
                                        usedId = tonumber(info.itemId) or 0
                                        break
                                    end
                                elseif MsgDefines and MsgDefines.ItemUse and SFSNetwork then
                                    local okS = pcall(function() SFSNetwork.SendMessage(MsgDefines.ItemUse, {uuid = tostring(uuid), num = 1}) end)
                                    if okS then
                                        used = true
                                        usedName = nm
                                        usedId = tonumber(info.itemId) or 0
                                        break
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end)
        local res = _jobj({
            ok = used,
            itemId = usedId,
            itemName = usedName,
            msg = used and "Peace shield deployed successfully." or "No peace shield items found in your bag."
        })
        return ser(res)
        """
        try:
            ok, out = client_discovery.frida_eval_lua(target_pid, lua_shield)
            if ok:
                data = _as_dict(json.loads(out))
                if data.get("ok"):
                    self.log(f"Quick Shield [PID {target_pid}]: Deployed peace shield successfully.", "ok")
                else:
                    self.log(f"Quick Shield [PID {target_pid}]: {data.get('msg', 'No shield found.')}", "warn")
                refreshed = self._discover_running_clients(query_lua=True, force_pids=[int(target_pid)])
                with self._lock:
                    self.running_clients = refreshed
                self._update_dropdown_values(refreshed)
                self._refresh_fleet_state()
                return data
            return {"ok": False, "msg": f"Frida evaluation failed: {out}"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def quick_recall(self, pid: int | None = None) -> dict[str, Any]:
        """Recall all gathering or field marches back to base immediately."""
        target_pid = _safe_int(pid, None) if pid is not None else None
        if not target_pid:
            with self._lock:
                clients_snap = list(self.running_clients)
                sel_pid = self.selected_client_pid or self.target_pid
            if sel_pid and any(int(c.get("pid") or 0) == int(sel_pid) for c in clients_snap):
                target_pid = int(sel_pid)
            else:
                for c in clients_snap:
                    if c.get("pid"):
                        target_pid = int(c["pid"])
                        break
        if not target_pid:
            return {"ok": False, "msg": "No active game client found to recall."}

        if client_discovery is None or not client_discovery._xlua_loaded(target_pid):
            return {"ok": False, "msg": f"Client PID {target_pid} is not ready or xlua is not loaded."}

        lua_recall = _LUA_JSON_SER + r"""
        local recalled = 0
        pcall(function()
            local p = LuaEntry and LuaEntry.Player
            local uid = p and (p.uid or (p.GetUid and p:GetUid())) or ""
            local mu = package.loaded['SlgEngine.Util.MarchUtil.MarchUtil'] or package.loaded['Util.MarchUtil_SLG']
            local wmdm = DataCenter and DataCenter.WorldMarchDataManager
            if wmdm and wmdm.allMarches and mu and mu.OnBackHome then
                for _, m in pairs(wmdm.allMarches) do
                    if type(m) == 'table' and tostring(m.uid) == tostring(uid) then
                        local uuid = tostring(m.uuid or m.marchUuid or '')
                        if uuid ~= '' then
                            local okR = pcall(function() mu.OnBackHome(uuid) end)
                            if okR then recalled = recalled + 1 end
                        end
                    end
                end
            end
        end)
        return ser(_jobj({
            ok = true,
            recalled = recalled,
            msg = string.format("Recalled %d squads back to base.", recalled)
        }))
        """
        try:
            ok, out = client_discovery.frida_eval_lua(target_pid, lua_recall)
            if ok:
                data = _as_dict(json.loads(out))
                rc = int(data.get("recalled", 0) or 0)
                self.log(f"Quick Recall [PID {target_pid}]: Recalled {rc} squads back to base.", "ok")
                refreshed = self._discover_running_clients(query_lua=True, force_pids=[int(target_pid)])
                with self._lock:
                    self.running_clients = refreshed
                self._update_dropdown_values(refreshed)
                self._refresh_fleet_state()
                return data
            return {"ok": False, "msg": f"Frida evaluation failed: {out}"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    @staticmethod
    def _normalize_troops_payload(raw: dict[str, Any], fallback_name: str = "Account") -> dict[str, Any]:
        d = dict(raw)
        tc_in = _as_dict(d.get("typeCounts"))
        d["typeCounts"] = {
            "infantry": _safe_int(tc_in.get("infantry"), 0),
            "rider": _safe_int(tc_in.get("rider"), 0),
            "vehicle": _safe_int(tc_in.get("vehicle"), 0),
            "other": _safe_int(tc_in.get("other"), 0),
        }
        tier_in = _as_dict(d.get("tierCounts"))
        d["tierCounts"] = {str(k): _safe_int(v, 0) for k, v in tier_in.items()}
        d["armies"] = _as_list(d.get("armies"), dicts_only=True)
        d["wounded"] = _as_list(d.get("wounded"), dicts_only=True)
        d["totalTroops"] = _safe_int(d.get("totalTroops"), 0)
        d["totalPower"] = _safe_int(d.get("totalPower"), 0)
        d["woundedTotal"] = _safe_int(d.get("woundedTotal"), 0)
        d["formationCapacity"] = _safe_int(d.get("formationCapacity"), 180000)
        d["hospitalCapacity"] = _safe_int(d.get("hospitalCapacity"), 200000)
        d["estHealSec"] = _safe_int(d.get("estHealSec"), 0)
        d["estHealHours"] = round(_safe_float(d.get("estHealHours"), 0.0), 1)
        acct_nm = str(d.get("account_name") or "").strip()
        d["account_name"] = acct_nm if acct_nm and acct_nm != "Player" else (fallback_name or acct_nm or "Account")
        return d

    def get_troops_overview(self, pid: int | None = None, force_live: bool = False) -> dict[str, Any]:
        """Extract or retrieve per-account cached drill ground troops, formations, and hospital wounded status."""
        _, target_pid, proc, account_label, clean_label = self._resolve_client_context(pid)
        raw_clean = clean_label if clean_label and clean_label != "client" else ""
        fallback_name = account_label or (f"PID {target_pid}" if target_pid else "Account")
        sync_key = f"troops:{raw_clean or (f'pid_{target_pid}' if target_pid else 'none')}"

        cache_dir = os.path.join(HEINZ_DATA_DIR, "json cache")
        data_cache_dir = os.path.join(DATA_DIR, "json cache")
        cache_candidates: list[str] = []
        if raw_clean:
            cache_candidates.append(os.path.join(cache_dir, f"{raw_clean}_troops_overview.json"))
            if data_cache_dir != cache_dir:
                cache_candidates.append(os.path.join(data_cache_dir, f"{raw_clean}_troops_overview.json"))
        if target_pid:
            cache_candidates.append(os.path.join(cache_dir, f"pid_{target_pid}_troops_overview.json"))
        allow_legacy_global = (
            pid is None
            and (proc is None or str(proc.get("role") or "").lower() == "main")
            and (not raw_clean or raw_clean == "main")
        )
        if allow_legacy_global:
            cache_candidates.append(os.path.join(cache_dir, "latest_troops_overview.json"))
            if data_cache_dir != cache_dir:
                cache_candidates.append(os.path.join(data_cache_dir, "latest_troops_overview.json"))

        cached_path = next((c for c in cache_candidates if c and os.path.isfile(c)), None)
        write_cache_path = (
            os.path.join(cache_dir, f"{raw_clean}_troops_overview.json")
            if raw_clean
            else (os.path.join(cache_dir, f"pid_{target_pid}_troops_overview.json") if target_pid else None)
        )

        with self._lock:
            last_sync = self._live_sync_ts.get(sync_key, 0.0)
        cache_fresh = bool(cached_path and (time.time() - last_sync) < 30.0)
        can_query_live = bool(
            target_pid
            and proc is not None
            and client_discovery is not None
            and client_discovery._xlua_loaded(target_pid)
        )

        if can_query_live and not force_live and cache_fresh and cached_path:
            cdata = _load_json_cached(cached_path)
            if isinstance(cdata, dict) and cdata.get("ok"):
                norm_fresh = self._normalize_troops_payload(cdata, fallback_name=fallback_name)
                norm_fresh["is_live"] = True
                norm_fresh["pid"] = int(target_pid)
                return norm_fresh

        if can_query_live and (force_live or not cache_fresh or not cached_path):
            lua_troops = _LUA_JSON_SER + r"""
            local p = LuaEntry and LuaEntry.Player
            local playerName = p and tostring(p.name or "Player") or "Player"
            local dc = DataCenter
            local am = dc and dc.ArmyManager
            local atm = dc and dc.ArmyTemplateManager
            local atmGet = atm and atm.GetArmyTemplate
            local hm = dc and dc.HospitalManager
            local afm = dc and dc.ArmyFormationDataManager
            local loc = Localization
            local locTbl = loc and loc.id_to_string
            local locGet = loc and loc.GetString

            local armies = _jarr()
            local totalTroops = 0
            local totalPower = 0
            local typeCounts = _jobj({ infantry = 0, rider = 0, vehicle = 0, other = 0 })
            local tierCounts = _jobj({ T1 = 0, T2 = 0, T3 = 0, T4 = 0, T5 = 0, T6 = 0, T7 = 0, T8 = 0, T9 = 0, T10 = 0, T11 = 0 })

            pcall(function()
                if am and am.allArmy then
                    for k, a in pairs(am.allArmy) do
                        pcall(function()
                            if type(a) == "table" then
                                local aid = tostring(a.id or a.armyId or k or "")
                                local cnt = tonumber(a.count or a.num or a.armyNum or 0) or 0
                                if cnt > 0 then
                                    local tmpl = nil
                                    if atmGet then
                                        local okT, tVal = pcall(atmGet, atm, aid)
                                        if okT then tmpl = tVal end
                                    end
                                    local lv = tonumber(a.level or a.lv or (tmpl and tmpl.level) or 1) or 1
                                    local atype = tonumber(a.type or a.armyType or (tmpl and tmpl.type) or 0) or 0
                                    local rawNm = tmpl and tmpl.name or a.name or ("Unit " .. aid)
                                    local name = tostring(rawNm)
                                    if tmpl and tmpl.name then
                                        local key = tostring(tmpl.name)
                                        local direct = locTbl and locTbl[key]
                                        if direct and direct ~= "" then
                                            name = tostring(direct)
                                        elseif locGet then
                                            local okL, s = pcall(locGet, loc, key)
                                            if okL and s and s ~= "" then name = tostring(s) end
                                        end
                                    end
                                    local unitPwr = tonumber((tmpl and tmpl.power) or (lv * 20)) or 20
                                    totalTroops = totalTroops + cnt
                                    totalPower = totalPower + (cnt * unitPwr)

                                    local cat = "other"
                                    if atype == 1 then cat = "infantry"
                                    elseif atype == 2 then cat = "rider"
                                    elseif atype == 3 then cat = "vehicle"
                                    end
                                    typeCounts[cat] = (typeCounts[cat] or 0) + cnt
                                    local tKey = "T" .. tostring(lv)
                                    tierCounts[tKey] = (tierCounts[tKey] or 0) + cnt

                                    table.insert(armies, {
                                        id = aid,
                                        name = name,
                                        count = cnt,
                                        tier = lv,
                                        type = atype,
                                        category = cat,
                                        power = unitPwr * cnt
                                    })
                                end
                            end
                        end)
                    end
                end
            end)

            local wounded = _jarr()
            local woundedTotal = 0
            local estHealSec = 0
            pcall(function()
                local injuredList = nil
                if hm and hm.GetAllHospital then
                    local okH, hVal = pcall(hm.GetAllHospital, hm)
                    if okH then injuredList = hVal end
                end
                injuredList = injuredList or (hm and hm.allHospital) or {}
                if type(injuredList) == "table" then
                    for k, entry in pairs(injuredList) do
                        pcall(function()
                            if type(entry) == "table" then
                                local aid = tostring(entry.armyId or entry.id or k or "")
                                local cnt = math.floor(tonumber(entry.dead or entry.num or entry.injured or entry.count or entry.hurt or 0) or 0)
                                if cnt > 0 then
                                    woundedTotal = woundedTotal + cnt
                                    local tmpl = nil
                                    if atmGet then
                                        local okT, tVal = pcall(atmGet, atm, aid)
                                        if okT then tmpl = tVal end
                                    end
                                    local rawNm = tmpl and tmpl.name or ("Unit " .. aid)
                                    local name = tostring(rawNm)
                                    if tmpl and tmpl.name then
                                        local key = tostring(tmpl.name)
                                        local direct = locTbl and locTbl[key]
                                        if direct and direct ~= "" then
                                            name = tostring(direct)
                                        elseif locGet then
                                            local okL, s = pcall(locGet, loc, key)
                                            if okL and s and s ~= "" then name = tostring(s) end
                                        end
                                    end
                                    local t = tonumber(tmpl and (tmpl.treat_time or tmpl.cure_time or tmpl.heal_time or tmpl.time) or 3) or 3
                                    estHealSec = estHealSec + (cnt * t)
                                    table.insert(wounded, {
                                        id = aid,
                                        name = name,
                                        count = cnt,
                                        healSec = cnt * t
                                    })
                                end
                            end
                        end)
                    end
                end
            end)

            local formationCap = 0
            pcall(function()
                if afm and afm.ArmyFormationList then
                    for _, f in pairs(afm.ArmyFormationList) do
                        if type(f) == "table" and f.maxSoldierNum then
                            formationCap = math.max(formationCap, tonumber(f.maxSoldierNum) or 0)
                        end
                    end
                end
            end)

            return ser(_jobj({
                ok = true,
                is_live = true,
                account_name = playerName,
                totalTroops = totalTroops,
                totalPower = totalPower,
                formationCapacity = formationCap > 0 and formationCap or 192000,
                hospitalCapacity = 220000,
                typeCounts = typeCounts,
                tierCounts = tierCounts,
                armies = armies,
                woundedTotal = woundedTotal,
                wounded = wounded,
                estHealSec = estHealSec,
                estHealHours = math.ceil((estHealSec / 3600) * 10) / 10,
                status_msg = "Live drill ground & hospital sync active."
            }))
            """
            try:
                ok, out = client_discovery.frida_eval_lua(target_pid, lua_troops)
                if ok and out:
                    parsed_live = json.loads(out)
                    if isinstance(parsed_live, dict) and parsed_live.get("ok"):
                        live_data = self._normalize_troops_payload(parsed_live, fallback_name=fallback_name)
                        live_data["ok"] = True
                        live_data["is_live"] = True
                        live_data["pid"] = int(target_pid)
                        with self._lock:
                            self._live_sync_ts[sync_key] = time.time()
                        if write_cache_path:
                            _atomic_write_json(write_cache_path, live_data)
                        return live_data
            except Exception as e:
                self.log(f"Live troop query error: {e}", "warn")

        # Fallback to per-account cache
        if cached_path and os.path.isfile(cached_path):
            cdata = _load_json_cached(cached_path)
            if isinstance(cdata, dict):
                cached = self._normalize_troops_payload(cdata, fallback_name=fallback_name)
                cached["ok"] = True
                cached["is_live"] = False
                cached["pid"] = int(target_pid) if target_pid else None
                cached["status_msg"] = "Game client offline • Showing cached drill ground & hospital records."
                return cached

        return {
            "ok": True,
            "is_live": False,
            "pid": int(target_pid) if target_pid else None,
            "account_name": fallback_name,
            "totalTroops": 0,
            "totalPower": 0,
            "formationCapacity": 180000,
            "hospitalCapacity": 200000,
            "typeCounts": {"vehicle": 0, "infantry": 0, "rider": 0, "other": 0},
            "tierCounts": {},
            "armies": [],
            "woundedTotal": 0,
            "wounded": [],
            "estHealSec": 0,
            "estHealHours": 0.0,
            "status_msg": "No troop records found. Connect game client to sync drill ground."
        }

    @staticmethod
    def _sanitize_hero_progression_rules(rules: dict[str, Any] | None) -> dict[str, Any]:
        raw = dict(rules) if isinstance(rules, dict) else {}
        base: dict[str, Any] = {}
        if multi_client_bot is not None and hasattr(multi_client_bot, "default_config"):
            try:
                base = dict(((multi_client_bot.default_config().get("client_defaults") or {}).get("main") or {}).get("hero_progression") or {})
            except Exception:
                base = {}
        defaults: dict[str, Any] = {
            "only_hero_day": True,
            "target_scope": "formation_1",
            "min_rarity": 4,
            "pinned_hero_ids": [],
            "max_actions_per_cycle": 15,
            "upgrade_levels": True,
            "allow_breakthrough": True,
            "target_level_cap": 0,
            "exp_reserve_millions": 0,
            "upgrade_stars": True,
            "use_universal_shards": False,
            "universal_shard_reserve": 50,
            "upgrade_skills": True,
            "skill_book_reserve": 0,
            "auto_equip_best": True,
            "upgrade_gear": True,
            "min_gear_quality": 5,
            "alloy_reserve": 0,
            "allow_gear_promote": False,
            "power_core_reserve": 0,
            "use_replacement_equip": False,
            "allow_sp_equip": False,
            "use_universal_sp_shards": False,
        }
        defaults.update(base)
        merged = dict(defaults)
        for k, v in raw.items():
            if k in defaults:
                merged[k] = v

        def _b(key: str, default: bool) -> bool:
            val = merged.get(key, default)
            if val is None:
                return bool(default)
            if isinstance(val, str):
                return val.strip().lower() in ("1", "true", "yes", "on")
            return bool(val)

        def _i(key: str, default: int, lo: int = 0, hi: int = 1_000_000) -> int:
            raw_v = merged.get(key, default)
            if raw_v is None or raw_v == "" or isinstance(raw_v, bool):
                n = default
            else:
                try:
                    n = int(raw_v)
                except Exception:
                    n = default
            return max(lo, min(hi, n))

        scope = str(merged.get("target_scope") or "formation_1").strip().lower()
        if scope not in ("formation_1", "all_formations", "pinned", "all_orange", "all"):
            scope = "formation_1"

        raw_pinned = merged.get("pinned_hero_ids")
        if isinstance(raw_pinned, str):
            raw_pinned = [x.strip() for x in raw_pinned.split(",") if x.strip()]
        elif not isinstance(raw_pinned, (list, tuple, set)):
            raw_pinned = []
        pinned_ids: list[int] = []
        seen_pins: set[int] = set()
        for item in raw_pinned:
            if isinstance(item, bool):
                continue
            try:
                hid = int(item)
            except Exception:
                continue
            if hid > 0 and hid not in seen_pins:
                seen_pins.add(hid)
                pinned_ids.append(hid)

        return {
            "only_hero_day": _b("only_hero_day", True),
            "target_scope": scope,
            "min_rarity": _i("min_rarity", 4, 1, 5),
            "pinned_hero_ids": pinned_ids,
            "max_actions_per_cycle": _i("max_actions_per_cycle", 15, 1, 100),
            "upgrade_levels": _b("upgrade_levels", True),
            "allow_breakthrough": _b("allow_breakthrough", True),
            "target_level_cap": _i("target_level_cap", 0, 0, 500),
            "exp_reserve_millions": _i("exp_reserve_millions", 0, 0, 100_000),
            "upgrade_stars": _b("upgrade_stars", True),
            "use_universal_shards": _b("use_universal_shards", False),
            "universal_shard_reserve": _i("universal_shard_reserve", 50, 0, 100_000),
            "upgrade_skills": _b("upgrade_skills", True),
            "skill_book_reserve": _i("skill_book_reserve", 0, 0, 100_000),
            "auto_equip_best": _b("auto_equip_best", True),
            "upgrade_gear": _b("upgrade_gear", True),
            "min_gear_quality": _i("min_gear_quality", 5, 1, 6),
            "alloy_reserve": _i("alloy_reserve", 0, 0, 1_000_000),
            "allow_gear_promote": _b("allow_gear_promote", False),
            "power_core_reserve": _i("power_core_reserve", 0, 0, 1_000_000),
            "use_replacement_equip": _b("use_replacement_equip", False),
            "allow_sp_equip": _b("allow_sp_equip", False),
            "use_universal_sp_shards": _b("use_universal_sp_shards", False),
        }

    def get_heroes_overview(self, pid: int | None = None, force_live: bool = False) -> dict[str, Any]:
        """Return live or cached hero roster, upgrade materials, VS Hero Day status, and automation rules."""
        _, target_pid, proc, account_label, clean_label = self._resolve_client_context(pid)
        role = str((proc or {}).get("role") or "main").lower()

        cfg_root: dict[str, Any] = {}
        if multi_client_bot is not None:
            try:
                cfg_root = multi_client_bot.load_config()
            except Exception:
                cfg_root = {}
        defs = cfg_root.get("client_defaults") or {}
        main_cfg = defs.get("main") or {}
        farm_cfg = defs.get("farm") or {}
        main_tasks = main_cfg.get("tasks") or {}
        farm_tasks = farm_cfg.get("tasks") or {}
        auto_run_main = bool(main_tasks.get("hero_progression", False))
        auto_run_farm = bool(farm_tasks.get("hero_progression", True))
        auto_run = auto_run_farm if role == "farm" else auto_run_main
        raw_rules = (defs.get(role) or main_cfg or farm_cfg).get("hero_progression") or {}
        clean_rules = self._sanitize_hero_progression_rules(raw_rules)

        cache_dir = os.path.join(HEINZ_DATA_DIR, "json cache")
        cache_candidates: list[str | None] = [
            os.path.join(cache_dir, f"{clean_label}_heroes_overview.json") if clean_label else None,
            os.path.join(cache_dir, f"pid_{target_pid}_heroes_overview.json") if target_pid else None,
        ]
        if pid is None and not clean_label and not target_pid:
            cache_candidates.append(os.path.join(cache_dir, "main_heroes_overview.json"))
            if os.path.isdir(cache_dir):
                try:
                    extra_caches = [
                        os.path.join(cache_dir, fn)
                        for fn in os.listdir(cache_dir)
                        if fn.endswith("_heroes_overview.json")
                    ]
                    extra_caches.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                    cache_candidates.extend(extra_caches)
                except Exception:
                    pass
        cached_path = next((c for c in cache_candidates if c and os.path.isfile(c)), None)
        write_cache_path = cache_candidates[0] or cache_candidates[1]

        sync_key = f"heroes:{clean_label or target_pid or 'none'}"
        with self._lock:
            last_sync = self._live_sync_ts.get(sync_key, 0.0)
        cache_fresh = bool(cached_path and (time.time() - last_sync) < 30.0)

        can_query_live = bool(
            target_pid
            and proc is not None
            and client_discovery is not None
            and bot_actions is not None
            and client_discovery._xlua_loaded(target_pid)
        )

        payload: dict[str, Any] | None = None
        is_live = False
        loaded_from_cache = False

        if can_query_live and (force_live or not cache_fresh or not cached_path):
            try:
                live_res = bot_actions.inspect_hero_progression(client_discovery, int(target_pid), include_probe=True)
                if isinstance(live_res, dict) and live_res.get("ok"):
                    payload = dict(live_res)
                    is_live = True
                    with self._lock:
                        self._live_sync_ts[sync_key] = time.time()
                    if write_cache_path:
                        to_cache = dict(payload)
                        if account_label:
                            to_cache["account_name"] = account_label
                        _atomic_write_json(write_cache_path, to_cache)
            except Exception as exc:
                self.log(f"Hero overview live sync note: {exc}", "warn")

        if payload is None and cached_path:
            cdata = _load_json_cached(cached_path)
            if isinstance(cdata, dict) and cdata.get("ok", True):
                payload = dict(cdata)
                loaded_from_cache = True

        if payload is None:
            payload = {
                "ok": True,
                "server_wday": 0,
                "server_day_name": "",
                "hq_max_hero_level": 0,
                "materials": {
                    "hero_exp_total": 0,
                    "hero_exp_items": [],
                    "skill_books": {"orange": 0, "purple": 0, "blue": 0, "total": 0},
                    "universal_shards": {"orange": 0, "purple": 0, "blue": 0, "total": 0, "by_color": {}},
                    "enhancement_alloy_total": 0,
                    "enhancement_alloy_exp_total": 0,
                    "enhancement_alloy_items": [],
                    "power_cores": 0,
                    "universal_equip_materials": 0,
                    "universal_sp_shards": 0,
                    "universal_break_minerals": 0,
                    "zent": 0,
                },
                "heroes": [],
                "summary": {
                    "total_heroes": 0,
                    "orange_heroes": 0,
                    "upgradable_level": 0,
                    "upgradable_star_own": 0,
                    "upgradable_star_uni": 0,
                    "upgradable_skills": 0,
                    "upgradable_gear": 0,
                    "better_gear_heroes": 0,
                    "upgradable_sp": 0,
                },
                "event_status": {
                    "hero_day_active": False,
                    "reason": "offline",
                    "active_theme": "",
                    "server_day_name": "",
                },
            }

        resolved_name = account_label
        if not resolved_name and loaded_from_cache and cached_path:
            cached_nm = str(payload.get("account_name") or "").strip()
            if cached_nm and cached_nm not in ("Offline", "Account"):
                resolved_name = cached_nm
            else:
                stem = os.path.basename(cached_path).replace("_heroes_overview.json", "")
                if stem == "main":
                    resolved_name = "Main"
                elif stem.startswith("pid_"):
                    resolved_name = f"PID {stem[4:]}"
                elif stem:
                    resolved_name = stem

        norm_heroes: list[dict[str, Any]] = []
        for raw_h in _as_list(payload.get("heroes"), dicts_only=True):
            h = dict(raw_h)
            h["skills"] = _as_list(h.get("skills"), dicts_only=True)
            h["gear"] = _as_list(h.get("gear"), dicts_only=True)
            h["suggestGearUuids"] = [str(u) for u in _as_list(h.get("suggestGearUuids")) if u is not None]
            sp = h.get("spEquip")
            h["spEquip"] = dict(sp) if isinstance(sp, dict) and sp else (sp if isinstance(sp, dict) else None)
            norm_heroes.append(h)
        payload["heroes"] = norm_heroes

        mats = _as_dict(payload.get("materials"))
        mats["hero_exp_items"] = _as_list(mats.get("hero_exp_items"), dicts_only=True)
        mats["enhancement_alloy_items"] = _as_list(mats.get("enhancement_alloy_items"), dicts_only=True)
        mats["skill_books"] = _as_dict(mats.get("skill_books"))
        uni_sh = _as_dict(mats.get("universal_shards"))
        uni_sh["by_color"] = _as_dict(uni_sh.get("by_color"))
        mats["universal_shards"] = uni_sh
        payload["materials"] = mats
        payload["summary"] = _as_dict(payload.get("summary"))
        payload["event_status"] = _as_dict(payload.get("event_status"))

        payload["ok"] = True
        payload["is_linked"] = bool((proc is not None and target_pid) or loaded_from_cache)
        payload["is_live"] = is_live
        payload["pid"] = int(target_pid) if target_pid else None
        payload["role"] = role
        payload["account_name"] = resolved_name or ("Account" if proc else "Offline")
        payload["rules"] = clean_rules
        payload["auto_run"] = auto_run
        payload["auto_run_main"] = auto_run_main
        payload["auto_run_farm"] = auto_run_farm
        return payload

    def save_hero_progression_rules(self, rules: dict[str, Any] | None = None) -> dict[str, Any]:
        """Validate and persist Hero Progression automation rules safely to bot config."""
        if multi_client_bot is None:
            return {"ok": False, "error": "multi_client_bot unavailable"}
        try:
            if rules is not None and not isinstance(rules, dict):
                return {"ok": False, "error": "Invalid rules payload: expected dict."}
            raw = dict(rules or {})
            clean_rules = self._sanitize_hero_progression_rules(raw)
            with self._lock:
                cur = multi_client_bot.load_config()
                defs = cur.setdefault("client_defaults", {})
                for role_key in ("main", "farm"):
                    rc = defs.setdefault(role_key, {})
                    rc["hero_progression"] = dict(clean_rules)
                main_t = defs.setdefault("main", {}).setdefault("tasks", {})
                farm_t = defs.setdefault("farm", {}).setdefault("tasks", {})
                if "auto_run_main" in raw:
                    main_t["hero_progression"] = bool(raw["auto_run_main"])
                if "auto_run_farm" in raw:
                    farm_t["hero_progression"] = bool(raw["auto_run_farm"])
                if "auto_run" in raw and "role" in raw:
                    rk = str(raw["role"]).strip().lower()
                    if rk == "main":
                        main_t["hero_progression"] = bool(raw["auto_run"])
                    elif rk == "farm":
                        farm_t["hero_progression"] = bool(raw["auto_run"])
                multi_client_bot.save_config(cur)
                self._config_snapshot_cache = None
                auto_run_main = bool(main_t.get("hero_progression", False))
                auto_run_farm = bool(farm_t.get("hero_progression", True))
            self.log("Saved Hero Progression rules.", "ok")
            return {
                "ok": True,
                "rules": clean_rules,
                "auto_run_main": auto_run_main,
                "auto_run_farm": auto_run_farm,
            }
        except Exception as exc:
            self.log(f"Save Hero Rules Error: {exc}", "err")
            return {"ok": False, "error": str(exc)}

    def run_hero_progression_now(
        self,
        pid: int | None = None,
        dry_run: bool = False,
        hero_uuid: str = "",
        only_module: str = "",
        force_ignore_day_guard: bool = False,
    ) -> dict[str, Any]:
        """Execute a live or dry-run Hero Progression pass (full sweep, single hero, or single module)."""
        clean_mod = str(only_module or "").strip().lower()
        if clean_mod not in ("", "level", "star", "skill", "gear", "gear_promote", "sp_equip"):
            return {"ok": False, "error": f"Unknown only_module: {clean_mod}"}
        if bot_actions is None or client_discovery is None or multi_client_bot is None:
            return {"ok": False, "error": "Automation modules unavailable"}

        explicit_pid: int | None = None
        if pid is not None:
            try:
                explicit_pid = int(pid)
            except Exception:
                return {"ok": False, "error": f"Requested client PID {pid} is not running or not XLua-ready."}
            if explicit_pid <= 0:
                return {"ok": False, "error": f"Requested client PID {pid} is not running or not XLua-ready."}

        _, target_pid, proc, account_label, _ = self._resolve_client_context(pid)
        if explicit_pid is not None:
            if proc is None or int(target_pid or 0) != explicit_pid or not client_discovery._xlua_loaded(explicit_pid):
                return {"ok": False, "error": f"Requested client PID {pid} is not running or not XLua-ready."}
        elif not target_pid or proc is None or not client_discovery._xlua_loaded(target_pid):
            return {"ok": False, "error": "No connected game client with XLua ready."}

        hp_locks = self._begin_hero_progression_lock([int(target_pid)])
        if hp_locks is None:
            return {"ok": False, "error": "Hero progression is already running for this client."}

        try:
            cfg_root = multi_client_bot.load_config()
            role = str((proc or {}).get("role") or "farm").lower()
            if hasattr(multi_client_bot, "resolve_client_config"):
                ccfg = multi_client_bot.resolve_client_config(cfg_root, account_label, role)
            else:
                ccfg = dict((cfg_root.get("client_defaults") or {}).get(role) or {})
            ctx = {
                "hero_uuid": str(hero_uuid or "").strip(),
                "only_module": clean_mod,
                "force_ignore_day_guard": bool(force_ignore_day_guard),
            }
            res = bot_actions.run_hero_progression(
                client_discovery,
                int(target_pid),
                {},
                ccfg,
                dry_run=bool(dry_run),
                context=ctx,
            )
            c_lbl = account_label or f"PID {target_pid}"
            if isinstance(res, dict):
                self._log_task_deep_details(c_lbl, "hero_progression", res, set())
                mode_lbl = "Dry-Run" if dry_run else "Live"
                total_act = int(res.get("total_actions") or 0)
                self.log(
                    f"[Heroes] [{mode_lbl}] {c_lbl}: action={res.get('action', 'done')}, total_actions={total_act}",
                    "ok" if res.get("ok", True) else "err",
                )
            return {
                "ok": bool((res or {}).get("ok", True)),
                "pid": int(target_pid),
                "account_label": c_lbl,
                "dry_run": bool(dry_run),
                "result": res,
            }
        except Exception as exc:
            self.log(f"Hero progression error: {exc}", "err")
            return {"ok": False, "error": str(exc)}
        finally:
            self._end_hero_progression_lock(hp_locks)

    def get_alliance_deltas(self, state_id: int = 694, force_snapshot: bool = False) -> dict[str, Any]:
        """Compute power deltas, member shifts, and rank movements across state alliances."""
        st_num = int(state_id)
        st_dir = os.path.join(DATA_DIR, "json cache", "bracket data", f"state_{st_num}")
        alliances_file = os.path.join(st_dir, "top10_alliances.json")
        rosters_file = os.path.join(st_dir, "top10_alliance_rosters.json")
        history_dir = os.path.join(st_dir, "history")
        os.makedirs(history_dir, exist_ok=True)
        baseline_file = os.path.join(history_dir, "baseline_top10.json")

        if not os.path.exists(alliances_file):
            return {"ok": False, "msg": f"State {st_num} data not found."}

        try:
            with open(alliances_file, "r", encoding="utf-8") as f:
                curr_alliances = json.load(f)
        except Exception as e:
            return {"ok": False, "msg": f"Failed to load alliances: {e}"}

        curr_rosters = []
        if os.path.exists(rosters_file):
            try:
                with open(rosters_file, "r", encoding="utf-8") as f:
                    curr_rosters = json.load(f)
            except Exception:
                curr_rosters = []

        rosters_by_tag = {str(r.get("abbr") or ""): r.get("members", []) for r in curr_rosters}

        if force_snapshot or not os.path.exists(baseline_file):
            snap = {
                "timestamp": time.time(),
                "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "alliances": curr_alliances,
                "rosters": {k: [{"uid": m.get("uid"), "name": m.get("name"), "power": m.get("power", 0)} for m in v] for k, v in rosters_by_tag.items()}
            }
            _atomic_write_json(baseline_file, snap)
            base_alliances = curr_alliances
            base_rosters = snap["rosters"]
            base_time = snap["formatted_time"]
            self.log(f"Captured fresh delta baseline for State {st_num}.", "ok")
        else:
            try:
                with open(baseline_file, "r", encoding="utf-8") as f:
                    snap = json.load(f)
                base_alliances = snap.get("alliances", [])
                base_rosters = snap.get("rosters", {})
                base_time = snap.get("formatted_time", "Prior Scan")
            except Exception:
                base_alliances = curr_alliances
                base_rosters = {}
                base_time = "Prior Scan"

        base_by_tag = {str(a.get("abbr") or ""): a for a in base_alliances}
        results = []
        tot_curr_pwr = 0
        tot_base_pwr = 0
        tot_members = 0

        for a in curr_alliances:
            tag = str(a.get("abbr") or "")
            cur_pwr = int(a.get("fightpower") or 0)
            tot_curr_pwr += cur_pwr
            base_a = base_by_tag.get(tag, {})
            base_pwr = int(base_a.get("fightpower") or cur_pwr)
            tot_base_pwr += base_pwr
            pwr_delta = cur_pwr - base_pwr

            cur_rank = int(a.get("rank") or 0)
            base_rank = int(base_a.get("rank") or cur_rank)
            rank_delta = base_rank - cur_rank

            cur_m = int(a.get("curMember") or 0)
            base_m = int(base_a.get("curMember") or cur_m)
            m_delta = cur_m - base_m
            tot_members += cur_m

            cur_members = rosters_by_tag.get(tag, [])
            cur_uids = {str(m.get("uid")): str(m.get("name") or "Player") for m in cur_members if m.get("uid")}
            base_members = base_rosters.get(tag, [])
            base_uids = {str(m.get("uid")): str(m.get("name") or "Player") for m in base_members if m.get("uid")}

            joined = [cur_uids[uid] for uid in cur_uids if uid not in base_uids][:5]
            left = [base_uids[uid] for uid in base_uids if uid not in cur_uids][:5]

            p_sign = "+" if pwr_delta > 0 else ""
            m_sign = "+" if m_delta > 0 else ""

            results.append({
                "rank": cur_rank,
                "rank_delta": rank_delta,
                "tag": tag,
                "name": str(a.get("alliancename") or tag),
                "leader": str(a.get("leader") or "Unknown"),
                "power": cur_pwr,
                "power_fmt": f"{cur_pwr / 1_000_000_000:.2f} B",
                "power_delta": pwr_delta,
                "power_delta_fmt": f"{p_sign}{pwr_delta / 1_000_000:.1f} M" if pwr_delta != 0 else "0 M",
                "cur_members": cur_m,
                "max_members": int(a.get("maxMember") or 100),
                "members_delta": m_delta,
                "members_delta_fmt": f"{m_sign}{m_delta}" if m_delta != 0 else "0",
                "joined": joined,
                "left": left,
            })

        state_delta = tot_curr_pwr - tot_base_pwr
        s_sign = "+" if state_delta > 0 else ""

        return {
            "ok": True,
            "state_id": st_num,
            "total_power": tot_curr_pwr,
            "total_power_fmt": f"{tot_curr_pwr / 1_000_000_000:.2f} B",
            "state_delta_power": state_delta,
            "state_delta_power_fmt": f"{s_sign}{state_delta / 1_000_000:.1f} M" if state_delta != 0 else "0 M",
            "total_members": tot_members,
            "baseline_time": base_time,
            "alliances": results,
        }

    def get_presets(self) -> dict[str, Any]:
        """Load saved automation presets from data/bot_presets.json."""
        p_path = os.path.join(DATA_DIR, "bot_presets.json")
        if not os.path.exists(p_path):
            return {"ok": True, "presets": {}}
        try:
            with open(p_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"ok": True, "presets": data}
        except Exception as e:
            return {"ok": False, "error": str(e), "presets": {}}

    def save_preset(self, name: str, tasks: dict[str, Any], desc: str = "") -> dict[str, Any]:
        """Save current task configuration as a named preset."""
        clean_name = str(name or "").strip()
        if not clean_name:
            return {"ok": False, "error": "Preset name cannot be empty."}
        p_path = os.path.join(DATA_DIR, "bot_presets.json")
        presets = {}
        if os.path.exists(p_path):
            try:
                with open(p_path, "r", encoding="utf-8") as f:
                    presets = json.load(f)
            except Exception:
                presets = {}
        presets[clean_name] = {
            "desc": desc or f"Custom preset saved on {time.strftime('%Y-%m-%d %H:%M')}",
            "tasks": tasks or {}
        }
        if _atomic_write_json(p_path, presets):
            self.log(f"Saved automation preset '{clean_name}'.", "ok")
            return {"ok": True, "name": clean_name}
        return {"ok": False, "error": "Failed to save presets atomically."}

    def delete_preset(self, name: str) -> dict[str, Any]:
        """Delete a custom preset from data/bot_presets.json."""
        clean_name = str(name or "").strip()
        p_path = os.path.join(DATA_DIR, "bot_presets.json")
        if not os.path.exists(p_path):
            return {"ok": False, "error": "Presets file not found."}
        try:
            presets = _safe_load_json_file(p_path, default={})
            if not isinstance(presets, dict):
                presets = {}
            if clean_name in presets:
                del presets[clean_name]
                if _atomic_write_json(p_path, presets):
                    self.log(f"Deleted automation preset '{clean_name}'.", "ok")
                    return {"ok": True}
                return {"ok": False, "error": "Failed to write presets atomically."}
            return {"ok": False, "error": f"Preset '{clean_name}' not found."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def run_action(self, action_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        p = payload or {}
        if action_id == "toggle_always_on_daemon":
            return self.toggle_always_on_daemon(
                enabled=p.get("enabled"),
            )
        if action_id == "toggle_hospital_watcher":
            return self.toggle_hospital_watcher(
                target=p.get("target"),
                enabled=p.get("enabled"),
            )
        if action_id == "toggle_alliance_help_watcher":
            return self.toggle_alliance_help_watcher(
                enabled=p.get("enabled"),
            )
        if action_id == "toggle_alliance_tech_watcher":
            return self.toggle_alliance_tech_watcher(
                enabled=p.get("enabled"),
            )
        if action_id == "start_rss_gather_loop":
            return self.start_rss_gather_loop(
                resource_type=str(p.get("resource_type") or "diamonds"),
                options=p.get("options") if isinstance(p.get("options"), dict) else p,
            )
        if action_id == "stop_rss_gather_loop":
            return self.stop_rss_gather_loop(pid=p.get("pid"))
        if action_id == "start_map_kills_loop":
            return self.start_map_kills_loop(
                mode=str(p.get("mode") or "boomers"),
                options=p.get("options") if isinstance(p.get("options"), dict) else p,
            )
        if action_id == "stop_map_kills_loop":
            return self.stop_map_kills_loop(pid=p.get("pid"))
        if action_id == "stop_all_farm_loops":
            return self.stop_all_farm_loops()
        if action_id == "probe_map_kills_status":
            return self.probe_map_kills_status(pid=p.get("pid"))
        if action_id == "get_farm_loops_state":
            return self.get_farm_loops_state()
        if action_id == "run_single_task" and str(p.get("task", "")).strip() == "hospital_heal" and not bool(p.get("dry_run", False)):
            return self.toggle_hospital_watcher(target=p.get("target"))
        if action_id == "quick_shield":
            return self.quick_shield(p.get("pid"))
        if action_id == "quick_recall":
            return self.quick_recall(p.get("pid"))
        if action_id == "get_troops_overview":
            return self.get_troops_overview(p.get("pid"), p.get("force_live", False))
        if action_id == "get_alliance_deltas":
            return self.get_alliance_deltas(p.get("state_id", 694), p.get("force_snapshot", False))
        if action_id == "get_presets":
            return self.get_presets()
        if action_id == "save_preset":
            return self.save_preset(p.get("name", ""), p.get("tasks", {}), p.get("desc", ""))
        if action_id == "delete_preset":
            return self.delete_preset(p.get("name", ""))
        if action_id == "open_inventory_excel":
            inv_xlsx = self.find_file("inventory reserves.xlsx")
            if not os.path.exists(inv_xlsx):
                self.log("Generating inventory reserves spreadsheet...", "info")
                self._run_tool("export inventory excel.py")
            if os.path.exists(inv_xlsx):
                self._open_output_file(inv_xlsx)
                self.log("Opened Inventory Reserves Excel workbook.", "ok")
                return {"ok": True}
            self.log("Inventory Reserves workbook not found.", "warn")
            return {"ok": False}
        if action_id == "open_google_roster":
            webbrowser.open(ROSTER_SHEET_URL)
            self.log("Opened Main Google Sheet Roster in browser.", "info")
            return {"ok": True}
        if action_id == "open_scratch_folder":
            self._open_output_file(SCRATCH_DIR)
            return {"ok": True}
        if action_id == "open_data_folder":
            target = DATA_DIR if os.path.isdir(DATA_DIR) else self.find_file("lastz_data_master")
            self._open_output_file(target)
            self.log("Data folder opened.", "info")
            return {"ok": True}
        if action_id == "open_vs_excel":
            self._open_named_file("vs_duel_rankings.xlsx")
            return {"ok": True}
        if action_id == "open_all_bases":
            self._open_named_file("map_all_bases.xlsx")
            return {"ok": True}
        if action_id == "open_all_resources":
            self._open_named_file("map_all_resources.csv")
            return {"ok": True}
        if action_id == "open_unshielded_excel":
            self._open_named_file("unshielded_targets.xlsx")
            return {"ok": True}
        if action_id == "open_active_migration":
            s = self.env.get("serverId", 694)
            perfect_path = os.path.join(BRACKET_DIR, f"State {s} Migration.xlsx")
            master_path = os.path.join(SCRATCH_DIR, f"State_{s}_Top_10_Alliances_Migration_Master.xlsx")
            if os.path.exists(perfect_path):
                self.log(f"Opening State {s} Migration Workbook.", "ok")
                self._open_output_file(perfect_path)
            elif os.path.exists(master_path):
                self.log(f"Opening State {s} Migration Master.", "ok")
                self._open_output_file(master_path)
            else:
                self._open_bracket_folder()
            return {"ok": True}
        if action_id == "export_top10":
            s = self.env.get("serverId", 694)
            for cand in (
                os.path.join(BRACKET_DIR, f"State {s} Migration.xlsx"),
                os.path.join(SCRATCH_DIR, f"State_{s}_Top_10_Alliances_Migration_Master.xlsx"),
                os.path.join(BRACKET_DIR, "State 694 Migration.xlsx"),
            ):
                if os.path.exists(cand):
                    self.log(f"Opening Top 10 Alliances Master: {os.path.basename(cand)}", "ok")
                    self._open_output_file(cand)
                    return {"ok": True}
            self.log("Top 10 Alliances Excel workbook not found.", "warn")
            return {"ok": False}
        if action_id == "open_selected_bracket_state":
            sel = str(p.get("state") or f"State {self.env.get('serverId', 694)}")
            target_name = f"{sel} Migration.xlsx"
            target_path = os.path.join(BRACKET_DIR, target_name)
            if os.path.exists(target_path):
                self.log(f"Opening {target_name}", "ok")
                self._open_output_file(target_path)
            else:
                self.log(f"{target_name} missing; opening bracket folder.", "warn")
                self._open_bracket_folder()
            return {"ok": True}
        if action_id == "open_bracket_folder":
            self._open_bracket_folder()
            return {"ok": True}

        threading.Thread(target=self._exec_bg_action, args=(action_id, p), daemon=True).start()
        return {"ok": True, "queued": True}

    def _open_named_file(self, rel_name: str) -> None:
        path = self.find_file(rel_name)
        if os.path.exists(path):
            self.log(f"Opening {os.path.basename(path)}", "ok")
            self._open_output_file(path)
        else:
            self.log(f"File not found: {rel_name}", "warn")

    def _open_bracket_folder(self) -> None:
        if os.path.exists(BRACKET_DIR):
            self.log("Bracket archive folder opened.", "info")
            self._open_output_file(BRACKET_DIR)
        else:
            self.log("Bracket archive folder not found yet.", "warn")

    def _exec_bg_action(self, action_id: str, p: dict[str, Any]) -> None:
        try:
            if action_id == "apply_engine":
                self.log("Applying 180 FPS & wide preloader (v8.0)...", "info")
                script = self.find_script("apply widescreen smooth map.py")
                res = self._subproc_run(_build_script_cmd(script, self._pid_args()), timeout=15, env=self._subprocess_env())
                self.log(f"Engine: {res.stdout.strip() or res.stderr.strip() or 'Done'}", "ok" if res.returncode == 0 else "err")

            elif action_id == "full_map_load":
                self.log("Triggering Full Map Load (v8.0 full LOD unlock + 1000x1000 sweep)...", "info")
                script = self.find_script("apply widescreen smooth map.py")
                args = list(self._pid_args()) + ["--full-map-load"]
                res = self._subproc_run(_build_script_cmd(script, args), timeout=15, env=self._subprocess_env())
                self.log(f"Full Map Load: {res.stdout.strip() or res.stderr.strip() or 'Done'}", "ok" if res.returncode == 0 else "err")

            elif action_id == "flush_ram":
                self.log("Flushing RAM and garbage collecting...", "info")
                script = self.find_script("flush game memory.py")
                if not os.path.exists(script):
                    script = self.find_script("manual_instant_gc.py")
                res = self._subproc_run(_build_script_cmd(script, self._pid_args()), timeout=15, env=self._subprocess_env())
                self.log(f"RAM Flush: {res.stdout.strip() or res.stderr.strip() or 'Done'}", "ok" if res.returncode == 0 else "err")

            elif action_id == "run_always_on_sweep_now":
                self._run_always_on_sweep_now()

            elif action_id in ("trigger_heli", "run_alliance_help_now"):
                self.log("[Always-On Daemon] Running immediate Alliance Help & Both Gift Tabs sweep across all running clients...", "info")
                tick = self._run_alliance_auto_help_once(force_log=True)
                if tick.get("skipped"):
                    with self._lock:
                        self._always_on_due_reset.add("auto_help")
                    self.log("[Always-On Daemon] Busy with another task - queued immediate retry.", "warn")
                    self._always_on_wake.set()

            elif action_id == "restart_daemon":
                self.log("Restarting Last Z Background Engine Daemon (v8.0)...", "info")
                with self._lock:
                    prev_dp = getattr(self, "_daemon_proc", None)
                    self._daemon_proc = None
                if prev_dp is not None:
                    try:
                        if prev_dp.poll() is None:
                            prev_dp.terminate()
                    except Exception:
                        pass
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        pname = (proc.info.get("name") or "").lower()
                        if not (pname.startswith("python") or pname.startswith("heinz")):
                            continue
                        if int(proc.info.get("pid") or 0) == os.getpid():
                            continue
                        cmd = " ".join(proc.cmdline() or [])
                        if "lastz auto engine daemon" in cmd or "lastz_auto_engine_daemon" in cmd:
                            proc.terminate()
                    except Exception:
                        pass
                time.sleep(0.3)
                script = self.find_script("lastz auto engine daemon.py")
                if not os.path.exists(script):
                    raise FileNotFoundError("Daemon script not found.")
                proc_d = self._subproc_popen(_build_script_cmd(script, ["--parent-pid", str(os.getpid())]))
                with self._lock:
                    self._daemon_proc = proc_d
                self.log("Background Auto-Engine Daemon restarted.", "ok")

            elif action_id == "export_inventory":
                self.log("Exporting bag inventory & reserves...", "info")
                sname = "export_inventory_excel.py"
                if not os.path.exists(self.find_script(sname)):
                    sname = "build_bag_inventory_excel.py"
                res = self._run_tool(sname, timeout=25)
                self.log(f"Inventory Export: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                for cand in ("inventory_reserves.xlsx", "bag_inventory_master.xlsx"):
                    t = self.find_file(cand)
                    if t and os.path.exists(t):
                        self._open_output_file(t)
                        break

            elif action_id == "export_tech":
                self.log("Exporting Tech Tree Progress...", "info")
                res = self._run_tool("export_tech_tree_excel.py", timeout=25)
                self.log(f"Tech Tree: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                t = self.find_file("Tech_Tree_Progress.xlsx")
                if t and os.path.exists(t):
                    self._open_output_file(t)

            elif action_id == "export_vs":
                self.log("Exporting VS Duel Rankings...", "info")
                res = self._run_tool("export_vs_duel_excel.py", timeout=25)
                self.log(f"VS Duel: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                self._open_output_file(self.find_file("vs_duel_rankings.xlsx"))

            elif action_id == "export_roster":
                self.log("Exporting Alliance Roster...", "info")
                res = self._run_tool("export_alliance_roster_excel.py", timeout=25)
                self.log(f"Roster: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                t = self.find_file("alliance_roster.xlsx")
                if not os.path.exists(t):
                    for fn in sorted(os.listdir(DATA_DIR)):
                        if "alliance" in fn.lower() and "roster" in fn.lower() and fn.lower().endswith(".xlsx"):
                            t = os.path.join(DATA_DIR, fn)
                            break
                if t and os.path.exists(t):
                    self._open_output_file(t)

            elif action_id == "export_alliance_members":
                self.log("Exporting Alliance Members Master...", "info")
                script = self.find_script("export_alliance_members_excel.py")
                res = self._subproc_run(_build_script_cmd(script), timeout=25)
                self.log(f"Alliance Members: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                t = self.find_file("Alliance_Members_Master.xlsx")
                if os.path.exists(t):
                    self._open_output_file(t)

            elif action_id == "export_map":
                self.log("Extracting full map intelligence...", "info")
                script = self.find_script("export_map_intelligence.py")
                t0 = time.time()
                res = self._subproc_run(_build_script_cmd(script), timeout=35)
                if res.returncode == 0:
                    self.log(f"Full map export complete ({time.time() - t0:.1f}s).", "ok")
                    t = self.find_file("map_all_bases.xlsx")
                    if os.path.exists(t):
                        self._open_output_file(t)
                else:
                    self.log(f"Map export failed: {res.stderr.strip() or res.stdout.strip()}", "err")

            elif action_id == "open_map_summary":
                self.log("Generating Map Intelligence Summary...", "info")
                script = self.find_script("export_map_summary_excel.py")
                res = self._subproc_run(_build_script_cmd(script), timeout=20)
                self.log(f"Map Summary: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                t = self.find_file("Map_Intelligence_Summary.xlsx")
                if os.path.exists(t):
                    self._open_output_file(t)

            elif action_id in ("navigate_resource", "dispatch_resource"):
                res_type = str(p.get("res_type") or "Mine")
                lvl_str = str(p.get("lvl_str") or "Level 6")
                lvl = int(lvl_str.replace("Level ", "").strip()) if "Level " in lvl_str else None
                dispatch = action_id == "dispatch_resource"
                with self._lock:
                    self.finder_status = {
                        "text": f"{'Dispatching squad to' if dispatch else 'Searching closest'} {res_type} ({lvl_str})...",
                        "tone": "warn",
                    }
                script = self.find_script("navigate to resource.py")
                extra = [res_type]
                if lvl is not None:
                    extra.append(str(lvl))
                if dispatch:
                    extra.append("--dispatch")
                extra.extend(self._pid_args())
                res = self._subproc_run(_build_script_cmd(script, extra), timeout=15, env=self._subprocess_env())
                out = res.stdout.strip()
                if "[+] Dispatched" in out or "[+] Found closest:" in out or "Navigated to" in out:
                    line = [l for l in out.splitlines() if "[+]" in l or "Navigated" in l][-1]
                    with self._lock:
                        self.finder_status = {"text": line, "tone": "ok"}
                    self.log(line, "ok")
                else:
                    err_msg = res.stderr.strip() or out or "No matching unoccupied resource found."
                    with self._lock:
                        self.finder_status = {"text": err_msg, "tone": "warn"}
                    self.log(err_msg, "warn")

            elif action_id in ("export_radar", "export_elite_radar"):
                elite = action_id == "export_elite_radar"
                self.log(f"Scanning {'Elite HQ 30-35' if elite else 'Unshielded HQ 25-35'} targets...", "info")
                res = self._run_tool("export_unshielded_targets.py", ["30"] if elite else None, timeout=25)
                if res.returncode == 0:
                    self.log("Target radar export complete.", "ok")
                    self._open_output_file(self.find_file("unshielded_targets.xlsx"))
                else:
                    self.log(f"Radar failed: {(res.stderr or res.stdout).strip()}", "err")

            elif action_id == "export_mines":
                self.log("Scanning Level 6-8 resource mines...", "info")
                res = self._run_tool("export_high_tier_resources.py", timeout=25)
                self.log(f"Mines: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                self._open_output_file(self.find_file("high_tier_resources.xlsx"))

            elif action_id == "scan_fleet":
                self.log("Scanning configured & running clients...", "info")
                if client_discovery is None:
                    self.log("client discovery.py missing.", "err")
                    return
                disc = client_discovery.discover_clients(save_cache=True)
                disc_list = disc if isinstance(disc, list) else (disc.get("clients", []) if isinstance(disc, dict) else [])
                with self._lock:
                    prev_pids = [int(c["pid"]) for c in self.running_clients if c.get("pid")]
                running = self._discover_running_clients(query_lua=True, force_pids=prev_pids)
                with self._lock:
                    self.discovered_clients = disc_list
                    self.running_clients = running
                self._update_dropdown_values(running)
                live_snaps = {}
                if bot_actions is not None:
                    for proc in running:
                        live_snaps[str(proc.get("label") or "")] = bot_actions.snapshot_client(client_discovery, int(proc["pid"]))
                self._refresh_fleet_state(live_snapshots=live_snaps)
                self.log(f"Fleet scan complete: {len(disc_list)} configured, {len(running)} running.", "ok")

            elif action_id == "setup_base_install":
                if not self._begin_action("setup_base_install"):
                    return
                try:
                    if sync_farm_clients is None:
                        self.log("sync farm clients.py unavailable.", "err")
                        return
                    base_dir = str(p.get("base_dir") or "").strip() or None
                    self.log("Inspecting & preparing Last Z base installation for multi-instance...", "info")
                    ok, info = sync_farm_clients.setup_base_installation(base_dir)
                    if ok:
                        lnk_note = " • Desktop shortcut ready" if info.get("main_shortcut_ok") else ""
                        self.log(
                            f"Setup ready: {info.get('base_game_dir')} (v{info.get('version') or '?'}) • GPU High-Perf set for {', '.join(info.get('gpu_applied') or ['Survival.exe'])}{lnk_note}",
                            "ok",
                        )
                        self.ensure_daemon_running()
                        self._exec_bg_action("scan_fleet", {})
                        if self.target_pid:
                            self._exec_bg_action("apply_engine", {})
                    else:
                        self.log(f"Setup error: {info.get('error', 'Unknown error')}", "err")
                    self._refresh_setup_status(base_dir)
                finally:
                    self._end_action("setup_base_install")

            elif action_id == "launch_single_client":
                label = str(p.get("label") or "").strip()
                mode = str(p.get("mode") or "windowed").strip().lower()
                if sync_farm_clients is None or not label:
                    return
                self.log(f"Launching '{label}' ({mode})...", "info")
                ok, info = sync_farm_clients.launch_client(label, mode=mode, wait_xlua=bool(p.get("wait_xlua", False)))
                if ok:
                    new_pid = info.get("pid")
                    msg = f"Focused {info.get('label')} (PID {new_pid})" if info.get("already_running") else f"Launched {info.get('label')} (PID {new_pid})"
                    self.log(msg, "ok")
                    refreshed = self._discover_running_clients(query_lua=False)
                    with self._lock:
                        self.running_clients = refreshed
                    self._update_dropdown_values(refreshed)
                    self._refresh_fleet_state()
                    if new_pid and mode != "hidden":
                        time.sleep(1.5)
                        try:
                            sync_farm_clients.show_process_windows(int(new_pid))
                        except Exception:
                            pass
                else:
                    self.log(f"Launch '{label}' failed: {info.get('error')}", "err")

            elif action_id == "stop_single_client":
                label = str(p.get("label") or "").strip()
                if sync_farm_clients is None or not label:
                    return
                ok, msg = sync_farm_clients.stop_client(label)
                self.log(f"Stop '{label}': {msg}", "ok" if ok else "err")
                time.sleep(0.4)
                self._exec_bg_action("scan_fleet", {})

            elif action_id == "sync_farm_builds":
                if not self._begin_action("sync_farm_builds"):
                    return
                try:
                    self.log("Syncing game binaries across Farm installs...", "info")
                    if sync_farm_clients is not None:
                        results = sync_farm_clients.sync_all_clients(force="--force" in str(p))
                        summary = "; ".join(f"{r.get('label')}: {'OK' if r.get('ok') else 'ERR'} ({r.get('message')})" for r in results)
                        all_ok = all(r.get("ok") for r in results) if results else True
                        self.log(f"Farm Sync: {summary or 'Complete'}", "ok" if all_ok else "warn")
                    else:
                        res = self._run_tool("sync farm clients.py", ["sync"], timeout=45)
                        out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                        self.log(f"Farm Sync: {out}", "ok" if res.returncode == 0 else "err")
                    self._refresh_setup_status()
                    self._refresh_fleet_state()
                finally:
                    self._end_action("sync_farm_builds")

            elif action_id == "heal_farm_launchers":
                if not self._begin_action("heal_farm_launchers"):
                    return
                try:
                    self.log("Checking Farm & Alt launcher wrappers and hooks...", "info")
                    if sync_farm_clients is not None and hasattr(sync_farm_clients, "heal_all_farm_launchers"):
                        rep = sync_farm_clients.heal_all_farm_launchers(
                            dry_run=bool(p.get("dry_run", False)),
                            force=bool(p.get("force", False)),
                        )
                        details = "; ".join(
                            str(r.get("message") or "")
                            for r in (rep.get("results") or [])
                            if not r.get("skipped")
                        )
                        lvl = "ok" if rep.get("ok") else "warn"
                        self.log(f"Farm Launcher Guard: {rep.get('summary')}{' - ' + details if details else ''}", lvl)
                    else:
                        res = self._run_tool("sync farm clients.py", ["heal-launchers"], timeout=30)
                        out = res.stdout.strip() or res.stderr.strip() or f"exit={res.returncode}"
                        self.log(f"Farm Launcher Guard: {out}", "ok" if res.returncode == 0 else "err")
                    self._refresh_setup_status()
                    self._refresh_fleet_state()
                finally:
                    self._end_action("heal_farm_launchers")

            elif action_id == "launch_all_farms":
                if not self._begin_action("launch_farms"):
                    self.log("Farm launch sequence is already running. Please wait...", "warn")
                    return
                try:
                    mode = str(p.get("mode") or "eco").strip().lower()
                    clients = client_discovery.discover_clients(save_cache=False) if client_discovery is not None else []
                    farms = [c for c in clients if c.get("role") != "main" and c.get("label")]
                    if not farms:
                        self.log("No secondary farm accounts configured. Use '+ Add Account' to configure instances.", "warn")
                        return

                    running_now = client_discovery.find_running_processes() if client_discovery is not None else []
                    running_labels = {str(r.get("label") or "").lower() for r in running_now}
                    to_launch = [f for f in farms if str(f.get("label") or "").lower() not in running_labels]

                    if not to_launch:
                        self.log(f"All {len(farms)} farm accounts are already active and online.", "ok")
                        return

                    total_to_launch = len(to_launch)
                    self.log(f"Initiating human-paced staged startup for {total_to_launch} farm client(s) in {mode} mode...", "info")

                    for idx, farm_info in enumerate(to_launch, start=1):
                        lbl = farm_info["label"]

                        # System RAM check before instance launch
                        try:
                            mem_avail_mb = int(psutil.virtual_memory().available / (1024 * 1024))
                            self.log(f"[Stage {idx}/{total_to_launch}] Checking system RAM ({mem_avail_mb}MB free > 1200MB threshold)...", "info")
                            if mem_avail_mb < 1200:
                                self.log(f"[Stage {idx}/{total_to_launch}] Low system RAM ({mem_avail_mb}MB free). Pausing 6s to allow memory recovery...", "warn")
                                time.sleep(6.0)
                        except Exception:
                            pass

                        self.log(f"[Stage {idx}/{total_to_launch}] Starting {lbl}...", "info")

                        ok = False
                        info: dict[str, Any] = {}
                        if sync_farm_clients is not None:
                            ok, info = sync_farm_clients.launch_client(lbl, mode=mode, auto_sync=True, wait_xlua=False)
                        else:
                            res = self._run_tool("sync farm clients.py", ["launch", lbl, mode], timeout=40)
                            ok = (res.returncode == 0)
                            info = {"pid": None}

                        new_pid = info.get("pid")
                        if ok and new_pid:
                            self.log(f"[Stage {idx}/{total_to_launch}] {lbl} process started (PID {new_pid}). Waiting for game engine & Lua to initialize...", "info")

                            # Wait up to 22s for xlua to load
                            xlua_ready = False
                            t_start = time.time()
                            while time.time() - t_start < 22.0:
                                time.sleep(1.2)
                                if client_discovery and client_discovery._xlua_loaded(new_pid):
                                    xlua_ready = True
                                    break

                            # Human settle pause between clients (5.0s to 7.0s) to prevent GPU swapchain contention
                            settle_delay = round(5.0 + (idx * 0.7) % 2.5, 1)
                            if idx < total_to_launch:
                                self.log(f"[Stage {idx}/{total_to_launch}] {lbl} online ({'Lua verified' if xlua_ready else 'Initializing'}). Pausing {settle_delay}s to settle graphics & CPU before next client...", "ok")
                                time.sleep(settle_delay)
                            else:
                                self.log(f"[Stage {idx}/{total_to_launch}] {lbl} online. Final instance settled.", "ok")
                        else:
                            err_msg = info.get("error") or "Process failed to start"
                            self.log(f"[Stage {idx}/{total_to_launch}] Failed to launch {lbl}: {err_msg}", "err")
                            time.sleep(2.0)

                    time.sleep(1.0)
                    self._exec_bg_action("scan_fleet", {})
                    self.log(f"Staged launch sequence complete. {total_to_launch} accounts stabilized.", "ok")
                finally:
                    self._end_action("launch_farms")

            elif action_id == "stop_all_farms":
                if not self._begin_action("stop_farms"):
                    return
                try:
                    self.log("Stopping secondary farm accounts (Main untouched)...", "info")
                    if sync_farm_clients is not None:
                        ok, msg = sync_farm_clients.stop_client("farms")
                        self.log(f"Stop Farms: {msg}", "ok" if ok else "err")
                    else:
                        res = self._run_tool("sync farm clients.py", ["stop", "farms"], timeout=20)
                        self.log(f"Stop Farms: {res.stdout.strip() or res.stderr.strip() or 'Done'}", "ok")
                    time.sleep(0.5)
                    self._exec_bg_action("scan_fleet", {})
                finally:
                    self._end_action("stop_farms")

            elif action_id == "provision_farm":
                if not self._begin_action("provision_farm"):
                    return
                try:
                    label = str(p.get("label") or "").strip()
                    prof = str(p.get("profile") or "").strip()
                    root_dir = str(p.get("root_dir") or "").strip()
                    exe_name = str(p.get("exe_name") or "").strip()
                    main_game_dir = str(p.get("main_game_dir") or "").strip() or None
                    launch_after = bool(p.get("launch_after", True))
                    create_shortcut = bool(p.get("create_shortcut", True))
                    if not exe_name.lower().endswith(".exe"):
                        exe_name = f"{exe_name}.exe"
                    self.log(f"Creating isolated account '{label or prof}' ({prof})...", "info")
                    if sync_farm_clients is not None:
                        ok, msg = sync_farm_clients.provision_new_client(
                            prof,
                            root_dir,
                            exe_name,
                            label=label or None,
                            main_game_dir=main_game_dir,
                            launch_after=launch_after,
                            create_shortcut=create_shortcut,
                        )
                        self.log(f"Add Account: {msg}", "ok" if ok else "err")
                    else:
                        args = ["provision", prof, root_dir, exe_name] + ([label] if label else [])
                        res = self._run_tool("sync farm clients.py", args, timeout=60)
                        self.log(f"Add Account: {res.stdout.strip() or res.stderr.strip() or 'Complete'}", "ok" if res.returncode == 0 else "err")
                    self._refresh_setup_status()
                    self._exec_bg_action("scan_fleet", {})
                finally:
                    self._end_action("provision_farm")

            elif action_id == "run_bot_cycle":
                with self._lock:
                    if "bot_cycle" in self._active_actions or any(
                        k.startswith("hero_progression:") for k in self._active_actions
                    ):
                        bot_busy = True
                    else:
                        self._active_actions.add("bot_cycle")
                        bot_busy = False
                if bot_busy:
                    self.log("Bot cycle or hero progression is already running...", "warn")
                    return
                try:
                    dry_run = bool(p.get("dry_run", False))
                    scope = str(p.get("scope") or "All Running")
                    target_arg = "all"
                    if scope == "Selected Client":
                        target_arg = self.selected_client_label or (str(self.target_pid) if self.target_pid else "all")
                    elif scope == "Main Only":
                        target_arg = "Main"
                    elif scope == "Farms Only":
                        target_arg = "farms"
                    mode_lbl = "Dry-Run Test" if dry_run else "Live Cycle"
                    self.log(f"[STAGE 0/5] Starting {mode_lbl} (target={target_arg}) - live telemetry streaming...", "stage", category="STAGE")
                    extra = ["--cycle", "--ignore-cooldowns", "--target", str(target_arg)]
                    if dry_run:
                        extra.append("--dry-run")
                    on_line, stream_state = self._make_bot_stream_handler()
                    res = self._stream_tool("multi client bot.py", extra, timeout=480, on_line=on_line)
                    self._refresh_fleet_state()
                    summary = f"{mode_lbl} finished (exit={res.returncode})"
                    payload: dict[str, Any] | None = stream_state.get("payload")
                    if payload is None and res.stdout:
                        for idx_pos in [m.start() for m in re.finditer(r'\{\s*"ok"\s*:', res.stdout)]:
                            try:
                                obj, _ = json.JSONDecoder().raw_decode(res.stdout[idx_pos:])
                                if isinstance(obj, dict):
                                    payload = obj
                                    break
                            except Exception:
                                continue
                    if isinstance(payload, dict):
                        total_tasks = sum(len((c.get("tasks") or {})) for c in (payload.get("clients") or []) if isinstance(c, dict))
                        summary = f"{mode_lbl}: processed {payload.get('processed_count', 0)}/{payload.get('running_count', 0)} running client(s) ({total_tasks} task(s) across 5 stages)"
                        for c in payload.get("clients", []):
                            c_lbl = str(c.get("label") or f"PID {c.get('pid')}")
                            for t_name, t_res in (c.get("tasks") or {}).items():
                                if isinstance(t_res, dict):
                                    self._log_task_deep_details(c_lbl, t_name, t_res, stream_state["streamed_norm"])
                    elif res.stdout:
                        clean_lines = [
                            ln.strip()
                            for ln in res.stdout.splitlines()
                            if ln.strip() and not ln.strip().startswith(("{", "}", "[", "]"))
                        ]
                        if clean_lines:
                            summary = clean_lines[-1]
                    self.log(summary, "ok" if res.returncode == 0 else "err")
                finally:
                    self._end_action("bot_cycle")

            elif action_id == "run_single_task":
                task_name = str(p.get("task", "")).strip()
                if not task_name:
                    return
                dry_run = bool(p.get("dry_run", False))
                target = str(p.get("target") or self.selected_client_label or (str(self.target_pid) if self.target_pid else "all"))
                hp_locks: list[str] | None = None
                if task_name == "hero_progression":
                    hp_locks = self._begin_hero_progression_lock(self._resolve_hero_progression_pids(target))
                    if hp_locks is None:
                        self.log("Hero progression is already running for target client(s).", "warn")
                        return
                    lock_key = f"single_task:hero_progression:{','.join(hp_locks)}"
                else:
                    lock_key = f"single_task:{task_name}"
                if not self._begin_action(lock_key):
                    if hp_locks:
                        self._end_hero_progression_lock(hp_locks)
                    return
                try:
                    mode_lbl = "Dry-Run" if dry_run else "Live"
                    self.log(f"[STAGE 1/1] Manual trigger: Running '{task_name}' [{mode_lbl}] on {target}...", "stage", category="STAGE")
                    extra = ["--cycle", "--tasks", task_name, "--target", target]
                    if dry_run:
                        extra.append("--dry-run")
                    on_line, stream_state = self._make_bot_stream_handler()
                    task_timeout = 240 if task_name == "daily_tasks_complete" else 150
                    res = self._stream_tool("multi client bot.py", extra, timeout=task_timeout, on_line=on_line)
                    self._refresh_fleet_state()
                    summary_msg = ""
                    log_kind = "ok" if res.returncode == 0 else "err"

                    parsed_json: dict[str, Any] | None = stream_state.get("payload")
                    if parsed_json is None and res.stdout:
                        for idx_pos in [m.start() for m in re.finditer(r'\{\s*"ok"\s*:', res.stdout)]:
                            try:
                                obj, _ = json.JSONDecoder().raw_decode(res.stdout[idx_pos:])
                                if isinstance(obj, dict):
                                    parsed_json = obj
                                    break
                            except Exception:
                                continue

                    if isinstance(parsed_json, dict):
                        clients = parsed_json.get("clients", [])
                        if not clients:
                            summary_msg = f"No running clients matched target '{target}'."
                            log_kind = "warn"
                        else:
                            client_parts: list[str] = []
                            all_success = True
                            for c in clients:
                                c_lbl = str(c.get("label") or f"PID {c.get('pid')}")
                                if not c.get("ok", True):
                                    all_success = False
                                    client_parts.append(f"{c_lbl}: snapshot failed ({c.get('error', 'unresponsive')})")
                                    continue
                                c_tasks = c.get("tasks", {})
                                t_res = c_tasks.get(task_name)
                                if t_res is None and c_tasks:
                                    t_res = next(iter(c_tasks.values()), None)
                                if not t_res:
                                    client_parts.append(f"{c_lbl}: skipped/disabled")
                                elif not isinstance(t_res, dict):
                                    client_parts.append(f"{c_lbl}: {t_res}")
                                else:
                                    # Emit every un-streamed deep detail line, delta, tip, modal, and RPC error
                                    self._log_task_deep_details(c_lbl, task_name, t_res, stream_state["streamed_norm"])
                                    tips = _filter_in_game_tips(t_res.get("in_game_tips") or t_res.get("tips") or [])
                                    if not t_res.get("ok", True):
                                        all_success = False
                                        err_msg = t_res.get("error") or "error"
                                        tip_suffix = f" [tips: {', '.join(str(t) for t in tips)}]" if tips else ""
                                        client_parts.append(f"{c_lbl}: failed ({err_msg}){tip_suffix}")
                                        continue

                                    details: list[str] = []
                                    trained_list = _as_list(t_res.get("trained"), dicts_only=True)
                                    busy_list = _as_list(t_res.get("busy"), dicts_only=True)
                                    if "trained" in t_res and isinstance(t_res["trained"], (list, dict)):
                                        total_cnt = sum(int(item.get("count", 0)) for item in trained_list)
                                        if total_cnt > 0:
                                            details.append(f"trained {total_cnt} troops across {len(trained_list)} barracks")
                                        elif busy_list:
                                            b_names = [str(item.get("barrack", "")) for item in busy_list if item.get("barrack")]
                                            details.append(f"all {len(busy_list)} barracks busy ({', '.join(b_names)})")
                                        else:
                                            details.append("0 troops trained")
                                    elif busy_list:
                                        b_names = [str(item.get("barrack", "")) for item in busy_list if item.get("barrack")]
                                        details.append(f"all {len(busy_list)} barracks busy ({', '.join(b_names)})")

                                    if "helped_all" in t_res and t_res["helped_all"]:
                                        details.append(f"helped {t_res.get('ally_help_num', 0)} alliance members")
                                    t1_c = self._extract_count(t_res.get("tab1_gifts_claimed"))
                                    t2_c = self._extract_count(t_res.get("tab2_chests_claimed"))
                                    if t1_c > 0 or t2_c > 0:
                                        details.append(f"alliance chests claimed (Tab 1: {t1_c}, Tab 2: {t2_c})")
                                    if "queued_troops" in t_res and t_res["queued_troops"] > 0:
                                        details.append(f"queued {t_res['queued_troops']} troops to heal")
                                    if "wounded_total" in t_res and t_res["wounded_total"] > 0 and not t_res.get("queued_troops"):
                                        details.append(f"{t_res['wounded_total']} wounded in hospital")
                                    claimed_uuids = _as_list(t_res.get("claimed_uuids"))
                                    if claimed_uuids:
                                        details.append(f"claimed {len(claimed_uuids)} radar rewards")
                                    if "repaired" in t_res:
                                        details.append(f"repaired {t_res['repaired']}")
                                    if "claimed" in t_res and t_res["claimed"]:
                                        c_raw = t_res["claimed"]
                                        c_val = len(_as_list(c_raw)) if isinstance(c_raw, (list, dict)) else c_raw
                                        if c_val:
                                            details.append(f"claimed {c_val}")
                                    if "battles" in t_res:
                                        b_raw = t_res["battles"]
                                        b_cnt = len(_as_list(b_raw)) if isinstance(b_raw, (list, dict)) else b_raw
                                        details.append(f"{b_cnt} battles")
                                    if "upgraded" in t_res and t_res["upgraded"]:
                                        details.append(f"upgraded {t_res['upgraded']}")
                                    elif task_name == "hero_progression":
                                        tot_hp = int(t_res.get("total_actions") or 0)
                                        skipped_hp = _as_list(t_res.get("skipped_reasons"))
                                        if tot_hp > 0:
                                            details.append(
                                                f"hero progression {tot_hp} action(s) "
                                                f"(lv={len(_as_list(t_res.get('level_ups')))}, break={len(_as_list(t_res.get('breakthroughs')))}, "
                                                f"star={len(_as_list(t_res.get('star_ups')))}, skill={len(_as_list(t_res.get('skill_ups')))}, "
                                                f"equip={len(_as_list(t_res.get('gear_installed')))}, gear={len(_as_list(t_res.get('gear_upgraded')))}, "
                                                f"promote={len(_as_list(t_res.get('gear_promoted')))}, weapon={len(_as_list(t_res.get('sp_upgraded')))})"
                                            )
                                        elif skipped_hp:
                                            details.append(str(skipped_hp[0]))
                                    dispatched_list = _as_list(t_res.get("dispatched"))
                                    if dispatched_list:
                                        details.append(f"dispatched {len(dispatched_list)} events")
                                    if "attacked" in t_res and isinstance(t_res["attacked"], dict) and t_res["attacked"]:
                                        atk = t_res["attacked"]
                                        t_desc = "XP" if atk.get("type") == 2 else ("Gold" if atk.get("type") == 1 else f"Type {atk.get('type')}")
                                        details.append(f"attacked Lv{atk.get('level')} {t_desc} mine #{atk.get('mineIndex')}")
                                    active_mines = _as_list(t_res.get("active_mines"), dicts_only=True)
                                    if active_mines:
                                        act = active_mines[0]
                                        r_min = int(act.get("remaining_sec", 0)) // 60
                                        r_hr = r_min // 60
                                        r_rem = r_min % 60
                                        details.append(f"actively mining ({r_hr}h {r_rem}m remaining)")
                                    if "refreshes_performed" in t_res and int(t_res.get("refreshes_performed") or 0) > 0:
                                        details.append(f"refreshed {t_res['refreshes_performed']}x")
                                    claimed_ach = _as_list(t_res.get("claimed_achievements"))
                                    if claimed_ach:
                                        details.append(f"claimed {len(claimed_ach)} achievements")
                                    if "message" in t_res and task_name == "daily_tasks_complete" and t_res["message"]:
                                        details.append(str(t_res["message"]))
                                    if "action" in t_res and t_res["action"] and t_res["action"] != "none":
                                        details.append(str(t_res["action"]))
                                    if tips:
                                        details.append("tips: " + ", ".join(str(tip) for tip in tips))
                                    for k in ("msg", "message", "summary", "status", "reason"):
                                        if k in t_res and t_res[k]:
                                            details.append(str(t_res[k]))
                                            break
                                    desc = (" - " + ", ".join(details)) if details else " OK"
                                    client_parts.append(f"{c_lbl}:{desc}")
                            summary_msg = "; ".join(client_parts)
                            log_kind = "ok" if all_success else ("warn" if any("OK" in s or "trained" in s or "queued" in s or "upgraded" in s or "battles" in s for s in client_parts) else "err")
                    else:
                        if res.returncode == 0:
                            lines = [ln.strip() for ln in (res.stdout or "").splitlines() if ln.strip() and not ln.strip().startswith(("{", "}", "[", "]"))]
                            summary_msg = lines[-1] if lines else f"Completed '{task_name}'"
                        else:
                            summary_msg = res.stderr.strip() or res.stdout.strip() or f"Process exited with code {res.returncode}"

                    self.log(f"Manual '{task_name}': {summary_msg}", log_kind)
                finally:
                    self._end_action(lock_key)
                    if hp_locks:
                        self._end_hero_progression_lock(hp_locks)

            elif action_id == "start_bot_daemon":
                script = self.find_script("multi client bot.py")
                self._subproc_popen(_build_script_cmd(script, ["--daemon"]))
                time.sleep(0.8)
                self._refresh_fleet_state()
                self.log("Multi-Client Bot background daemon started.", "ok")

            elif action_id == "stop_bot_daemon":
                res = self._run_tool("multi client bot.py", ["--stop-daemon"], timeout=15)
                time.sleep(0.5)
                self._refresh_fleet_state()
                self.log(f"Stop Bot Daemon: {res.stdout.strip() or res.stderr.strip() or 'Stopped'}", "ok")

            elif action_id == "install_bot_task":
                res = self._run_tool("multi client bot.py", ["--install-task"], timeout=20)
                self._invalidate_bot_task_status_cache()
                self._refresh_fleet_state()
                self.log(f"Windows Schedule: {res.stdout.strip() or res.stderr.strip() or 'Registered'}", "ok")

            elif action_id == "uninstall_bot_task":
                res = self._run_tool("multi client bot.py", ["--uninstall-task"], timeout=20)
                self._invalidate_bot_task_status_cache()
                self._refresh_fleet_state()
                self.log(f"Windows Schedule: {res.stdout.strip() or res.stderr.strip() or 'Removed'}", "ok")

            elif action_id == "sync_google_bracket":
                if not self._begin_action("sync_google_bracket"):
                    return
                try:
                    live_refresh = bool(self.running_clients)
                    extra = ["--states", "all"]
                    if live_refresh:
                        extra.append("--refresh-live")
                        if self.target_pid:
                            extra.extend(["--pid", str(self.target_pid)])
                    self.log("Syncing all 16 Google Drive Bracket spreadsheets...", "info")
                    res = self._run_tool("sync bracket drive sheets.py", extra, timeout=480)
                    self.log(f"Google Sync: {res.stdout.strip() or res.stderr.strip() or 'Done'}", "ok" if res.returncode == 0 else "err")
                finally:
                    self._end_action("sync_google_bracket")
        except Exception as exc:
            self.log(f"Action '{action_id}' error: {exc}", "err")


def _build_game_icons_bootstrap_js(
    icons_dir: str | None = None,
    include_heavy_packs: bool = True,
) -> str:
    """Build inline JS bootstrap assigning base64-encoded Last Z WebP game icons."""
    base_dir = icons_dir if icons_dir is not None else os.path.join(RES_ROOT, "assets", "game icons")
    core_icons: dict[str, str] = {}
    hero_sprites: dict[str, str] = {}
    hero_by_id: dict[str, str] = {}
    item_sprites: dict[str, str] = {}
    item_by_id: dict[str, str] = {}

    def _load_webp_dir(folder: str) -> dict[str, str]:
        loaded: dict[str, str] = {}
        if not os.path.isdir(folder):
            return loaded
        try:
            entries = sorted(os.listdir(folder))
        except OSError:
            return loaded
        for fname in entries:
            if not fname.lower().endswith(".webp"):
                continue
            fpath = os.path.join(folder, fname)
            if not os.path.isfile(fpath):
                continue
            key = os.path.splitext(fname)[0].replace(" ", "_")
            try:
                with open(fpath, "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode("ascii")
                loaded[key] = f"data:image/webp;base64,{b64}"
            except OSError:
                continue
        return loaded

    if os.path.isdir(base_dir):
        core_icons = _load_webp_dir(base_dir)
        if include_heavy_packs:
            hero_sprites = _load_webp_dir(os.path.join(base_dir, "heroes"))
            item_sprites = _load_webp_dir(os.path.join(base_dir, "items"))

            manifest_path = os.path.join(base_dir, "manifest.json")
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest = json.load(mf)
                except (OSError, ValueError, TypeError):
                    manifest = {}
                if isinstance(manifest, dict):
                    raw_hero_map = manifest.get("hero_id_to_sprite")
                    if isinstance(raw_hero_map, dict):
                        hero_by_id = {
                            str(k): str(v)
                            for k, v in raw_hero_map.items()
                            if k is not None and v is not None and str(k) != "" and str(v) != ""
                        }
                    raw_item_map = manifest.get("item_id_to_sprite")
                    if isinstance(raw_item_map, dict):
                        item_by_id = {
                            str(k): str(v)
                            for k, v in raw_item_map.items()
                            if k is not None and v is not None and str(k) != "" and str(v) != ""
                        }

    def _safe_js_json(payload: Any) -> str:
        return json.dumps(payload, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")

    hero_payload = {"sprites": hero_sprites, "byId": hero_by_id}
    item_payload = {"sprites": item_sprites, "byId": item_by_id}
    return "\n".join(
        (
            f"window.__GAME_ICONS__ = {_safe_js_json(core_icons)};",
            f"window.__GAME_HERO_ICONS__ = {_safe_js_json(hero_payload)};",
            f"window.__GAME_ITEM_ICONS__ = {_safe_js_json(item_payload)};",
        )
    )


def _load_html_with_assets(include_heavy_packs: bool = True) -> str:
    html_path = os.path.join(RES_ROOT, "web", "index.html")
    with open(html_path, "r", encoding="utf-8") as hf:
        html = hf.read()

    banner_path = os.path.join(RES_ROOT, "assets", "hero banner.png")
    if os.path.exists(banner_path):
        with open(banner_path, "rb") as bf:
            b64 = base64.b64encode(bf.read()).decode("ascii")
        html = html.replace("__HERO_BANNER_DATA_URI__", f"data:image/png;base64,{b64}")
    else:
        html = html.replace("__HERO_BANNER_DATA_URI__", "")

    icon_path = os.path.join(RES_ROOT, "assets", "heinz icon.png")
    if os.path.exists(icon_path):
        with open(icon_path, "rb") as icf:
            b64 = base64.b64encode(icf.read()).decode("ascii")
        html = html.replace("__HEINZ_ICON_DATA_URI__", f"data:image/png;base64,{b64}")
    else:
        html = html.replace("__HEINZ_ICON_DATA_URI__", "")

    if "/*__GAME_ICONS_BOOTSTRAP__*/" in html:
        html = html.replace(
            "/*__GAME_ICONS_BOOTSTRAP__*/",
            _build_game_icons_bootstrap_js(include_heavy_packs=include_heavy_packs),
        )
    return html


def _write_hydrated_html_cache(html: str) -> str:
    """Write hydrated UI HTML atomically to disk and return a file:/// URI.

    Edge WebView2's NavigateToString() enforces a hard 2 MB string ceiling and
    fails silently with a blank window when exceeded. Loading via CoreWebView2
    Navigate(file:///) bypasses that limit completely while keeping pywebview's
    JS API bridge fully wired.
    """
    import pathlib
    import tempfile

    candidates = [
        os.path.join(HEINZ_DATA_DIR, "cache", "heinz_hub_ui.html"),
        os.path.join(tempfile.gettempdir(), "heinz_hub_ui.html"),
    ]
    for target in candidates:
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            tmp_path = f"{target}.{os.getpid()}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as fh:
                fh.write(html)
            os.replace(tmp_path, target)
            return pathlib.Path(target).resolve().as_uri()
        except OSError:
            continue
    return ""


WEBVIEW2_CLIENT_GUID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
WEBVIEW2_DOWNLOAD_URL = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"


def _webview2_runtime_version() -> str:
    """Return installed Microsoft Edge WebView2 Runtime version ('' if missing)."""
    try:
        import winreg
    except ImportError:
        return ""
    probes = (
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_GUID}"),
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_GUID}"),
        (winreg.HKEY_CURRENT_USER, rf"Software\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_GUID}"),
    )
    for hive, sub in probes:
        try:
            with winreg.OpenKey(hive, sub) as k:
                ver, _ = winreg.QueryValueEx(k, "pv")
                if ver and str(ver) != "0.0.0.0":
                    return str(ver)
        except OSError:
            continue
    return ""


def _message_box(text: str, title: str = "HeinZ Helper", flags: int = 0x40) -> int:
    try:
        import ctypes

        return int(ctypes.windll.user32.MessageBoxW(None, text, title, flags))
    except Exception:
        return 0


NETFX48_DOWNLOAD_URL = "https://dotnet.microsoft.com/download/dotnet-framework/net48"


def _netfx472_release() -> int:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full") as k:
            val, _ = winreg.QueryValueEx(k, "Release")
            return int(val)
    except Exception:
        return 0


def _check_netfx_or_prompt() -> None:
    rel = _netfx472_release()
    if rel >= 461808:
        return
    log_crash(f"STARTUP: .NET Framework 4.7.2+ not detected (Release={rel})")
    res = _message_box(
        "HeinZ needs Microsoft .NET Framework 4.7.2 or 4.8 to run its desktop window.\n\n"
        "Click YES to open Microsoft's official .NET Framework 4.8 download page.\n"
        "Click NO to try starting HeinZ anyway.",
        "HeinZ - .NET Framework 4.8 required",
        0x04 | 0x30,
    )
    if res == 6:  # IDYES
        webbrowser.open(NETFX48_DOWNLOAD_URL)
        sys.exit(0)


def _check_webview2_or_prompt() -> None:
    if _webview2_runtime_version():
        return
    log_crash("STARTUP: Microsoft Edge WebView2 Runtime not detected")
    # MB_YESNO | MB_ICONWARNING
    res = _message_box(
        "HeinZ needs the free Microsoft Edge WebView2 Runtime to draw its window.\n\n"
        "It is built into Windows 11 and most up-to-date Windows 10 PCs, but it was not found here.\n\n"
        "Click YES to open Microsoft's download page (install it, then start HeinZ again).\n"
        "Click NO to try starting HeinZ anyway.",
        "HeinZ - WebView2 Runtime required",
        0x04 | 0x30,
    )
    if res == 6:  # IDYES
        webbrowser.open(WEBVIEW2_DOWNLOAD_URL)
        sys.exit(0)


def _get_primary_screen_size() -> tuple[int, int]:
    try:
        import ctypes

        u32 = ctypes.windll.user32
        w = int(u32.GetSystemMetrics(0))
        h = int(u32.GetSystemMetrics(1))
        if w >= 640 and h >= 480:
            return (w, h)
    except Exception:
        pass
    return (1920, 1080)


def main() -> None:
    if "--launch-client" in sys.argv:
        idx = sys.argv.index("--launch-client")
        target = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "Main"
        if sync_farm_clients is None:
            log_crash(f"--launch-client '{target}' failed: sync_farm_clients unavailable")
            sys.exit(1)
        ok, info = sync_farm_clients.launch_client(target, mode="windowed")
        if not ok:
            log_crash(f"--launch-client '{target}' failed: {info}")
            _message_box(
                f"Could not launch Last Z account '{target}'.\n\n{(info or {}).get('error', info)}\n\n"
                "Open HeinZ and use Scan / Setup to repair this account.",
                "HeinZ - Launch failed",
                0x10,
            )
            sys.exit(1)
        sys.exit(0)

    log_crash("STARTUP: Starting HeinZ Standalone Launcher & Command Hub (WebView2)")
    _check_netfx_or_prompt()
    _check_webview2_or_prompt()
    start_enhanced_directly = "--enhanced" in sys.argv
    backend = HubBackend(defer_enhanced=not start_enhanced_directly)
    if start_enhanced_directly:
        backend.start_monitors()
    html = _load_html_with_assets(include_heavy_packs=True)
    ui_url = _write_hydrated_html_cache(html)
    win_title = "HeinZ Helper" if start_enhanced_directly else "HeinZ Login"
    win_w, win_h = (1240, 840) if start_enhanced_directly else (440, 450)
    min_sz = (940, 680) if start_enhanced_directly else (400, 380)
    sw, sh = _get_primary_screen_size()
    win_x = max(0, (sw - win_w) // 2)
    win_y = max(0, (sh - win_h) // 2)
    if ui_url:
        win = webview.create_window(
            win_title,
            url=ui_url,
            js_api=backend,
            width=win_w,
            height=win_h,
            x=win_x,
            y=win_y,
            min_size=min_sz,
            background_color="#0D0F12",
        )
    else:
        compact_html = _load_html_with_assets(include_heavy_packs=False)
        win = webview.create_window(
            win_title,
            html=compact_html,
            js_api=backend,
            width=win_w,
            height=win_h,
            x=win_x,
            y=win_y,
            min_size=min_sz,
            background_color="#0D0F12",
        )
    backend.set_window(win)
    try:
        webview.start(debug=False)
    except Exception as exc:
        backend.shutdown()
        msg_low = str(exc).lower()
        log_crash(exc)
        desktop_crash = _write_redacted_desktop_crash(
            "webview.start",
            exc,
            extra={"unblocked_at_startup": _UNBLOCKED_AT_STARTUP},
        )
        desk_note = f"\n\nRedacted crash report saved to Desktop:\n{desktop_crash}" if desktop_crash else ""
        if "python.runtime" in msg_low or "clr" in msg_low:
            _message_box(
                "HeinZ could not load its UI runtime (.NET / pythonnet).\n\n"
                "Most common fix on a fresh Windows PC:\n"
                "1) Right-click HeinZ-Portable.zip -> Properties -> check 'Unblock' -> Apply, then re-extract, OR\n"
                "2) Right-click HeinZ.exe -> Run as administrator once, OR\n"
                "3) Make sure Microsoft .NET Framework 4.8 is installed."
                f"{desk_note}\n\n"
                f"Technical error:\n{exc}",
                "HeinZ - Runtime Blocked",
                0x10,
            )
            sys.exit(1)
        raise
    finally:
        backend.shutdown()
    log_crash("SHUTDOWN: HeinZ Helper closed cleanly")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        log_crash(exc)
        desktop_crash = _write_redacted_desktop_crash(
            "main",
            exc,
            extra={"unblocked_at_startup": _UNBLOCKED_AT_STARTUP},
        )
        saved_hint = desktop_crash or CRASH_LOG
        _message_box(
            f"HeinZ hit an unexpected error and has to close.\n\n{type(exc).__name__}: {exc}\n\n"
            f"Redacted report saved to:\n{saved_hint}",
            "HeinZ - Error",
            0x10,
        )
        raise
