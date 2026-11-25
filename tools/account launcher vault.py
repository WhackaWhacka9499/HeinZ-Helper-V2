"""Account binding vault, first-time email verification tracker, and Vanilla/Enhanced launcher.

Manages isolated Last Z PC account bindings under `<HEINZ_DATA_DIR>/json cache/bound accounts.json`,
inspects Unity ReadyGo profile session readiness (presence-only for tokens; raw token bytes are
never read, stored, or logged), and launches accounts in either:
- Vanilla mode (strictly zero-attach: stops background HeinZ daemons/translators, never imports or
  touches Frida, spawns the game detached, and signals HeinZ to exit cleanly), or
- Enhanced mode (detached borderless/windowed/fullscreen launch compatible with HeinZ tools).
"""

from __future__ import annotations

import base64
import ctypes
import importlib.util
import inspect
import json
import os
import re
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

import psutil

try:
    import winreg  # type: ignore[import-not-found]
except ImportError:
    winreg = None  # type: ignore[assignment]

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
READYGO_REG_BASE = r"Software\ReadyGo"
GPU_PREF_KEY = r"Software\Microsoft\DirectX\UserGpuPreferences"

VALID_WINDOW_STYLES: tuple[str, ...] = ("borderless", "windowed", "fullscreen")
VALID_LAUNCH_MODES: tuple[str, ...] = ("vanilla", "enhanced")

RESERVED_PROFILES: frozenset[str] = frozenset(
    {
        "LASTZ",
        "FARMZ",
        "ALT2Z",
        "ALT3Z",
        "ALT4Z",
        "ALT5Z",
        "ALT6Z",
        "ALT7Z",
        "ALT8Z",
        "ALT9Z",
    }
)

_SESSION_CLEAR_PREFIXES: tuple[str, ...] = (
    "SeToken",
    "Setting.GAME_UID",
    "GAME_ACCOUNT",
    "Setting.GAME_ACCOUNT",
)

_FORBIDDEN_VAULT_KEY_FRAGMENTS: tuple[str, ...] = (
    "setoken",
    "password",
    "passwd",
    "secret",
    "raw_token",
    "session_token",
    "auth_token",
)

_DAEMON_SCRIPT_MARKERS: tuple[str, ...] = (
    "lastz auto engine daemon.py",
    "live translator server.py",
)

_EMAIL_PATTERN = re.compile(
    r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}@"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*"
    r"\.[a-z]{2,24}$"
)
_PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")

_VAULT_IO_LOCK = threading.Lock()
_MOD_CACHE_LOCK = threading.Lock()
_LOADED_MODULES: dict[str, Any] = {}


# ------------------------------------------------------------------
# Path & Lazy Module Helpers
# ------------------------------------------------------------------


def _resolve_data_dir() -> Path:
    override = os.environ.get("HEINZ_DATA_DIR", "").strip()
    if override:
        return Path(override)
    return REPO_ROOT / "data"


def resolve_vault_path() -> Path:
    """Resolve `<HEINZ_DATA_DIR>/json cache/bound accounts.json` dynamically."""
    return _resolve_data_dir() / "json cache" / "bound accounts.json"


def _load_tool_module(cache_key: str, filename: str) -> Any | None:
    target = TOOLS_DIR / filename
    if not target.is_file():
        return None
    with _MOD_CACHE_LOCK:
        cached = _LOADED_MODULES.get(cache_key)
        if cached is not None:
            return cached
    try:
        spec = importlib.util.spec_from_file_location(cache_key, str(target))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with _MOD_CACHE_LOCK:
            _LOADED_MODULES[cache_key] = mod
        return mod
    except Exception:
        return None


def _load_client_discovery() -> Any | None:
    return _load_tool_module("heinz_vault_client_discovery", "client discovery.py")


def _load_game_engine_manager() -> Any | None:
    return _load_tool_module("heinz_vault_game_engine_manager", "game engine manager.py")


def _load_sync_farm_clients() -> Any | None:
    return _load_tool_module("heinz_vault_sync_farm_clients", "sync farm clients.py")


# ------------------------------------------------------------------
# Registry Session Inspector (Presence-Only for Tokens!)
# ------------------------------------------------------------------


def _decode_non_secret_reg_value(val: Any) -> str:
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="ignore").rstrip("\x00").strip()
    if isinstance(val, str):
        return val.strip()
    if val is None:
        return ""
    return str(val).strip()


def _parse_int_safe(val: Any) -> int:
    if isinstance(val, bool):
        return 0
    if isinstance(val, int):
        return val
    text = _decode_non_secret_reg_value(val)
    if text.isdigit():
        return int(text)
    return 0


def inspect_profile_session(
    unity_profile: str,
    reg_reader: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Inspect HKCU\\Software\\ReadyGo\\<unity_profile> for session readiness.

    Checks presence ONLY (`bool(vdata)`) for any value starting with `SeToken`.
    Never decodes, stores, returns, or logs raw token bytes.
    """
    prof = str(unity_profile or "").strip()
    has_token = False
    uid = ""
    server_id = 0

    if reg_reader is not None:
        raw = reg_reader(prof)
        if isinstance(raw, dict):
            saw_setoken_key = False
            for k, v in raw.items():
                ks = str(k)
                if ks.startswith("SeToken"):
                    saw_setoken_key = True
                    if bool(v):
                        has_token = True
                elif ks.startswith("Setting.GAME_UID"):
                    cand_uid = _decode_non_secret_reg_value(v)
                    if cand_uid:
                        uid = cand_uid
                elif ks.startswith("Setting.SERVER_ID"):
                    cand_srv = _parse_int_safe(v)
                    if cand_srv > 0:
                        server_id = cand_srv

            if not saw_setoken_key and "has_token" in raw:
                has_token = bool(raw.get("has_token"))
            if not uid and "uid" in raw:
                uid = _decode_non_secret_reg_value(raw.get("uid"))
            if server_id <= 0 and "server_id" in raw:
                server_id = _parse_int_safe(raw.get("server_id"))
    elif prof and _PROFILE_NAME_PATTERN.fullmatch(prof) and winreg is not None:
        subkey = f"{READYGO_REG_BASE}\\{prof}"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as sk:
                val_count = winreg.QueryInfoKey(sk)[1]
                for idx in range(val_count):
                    vname, vdata, _ = winreg.EnumValue(sk, idx)
                    if vname.startswith("SeToken"):
                        if bool(vdata):
                            has_token = True
                    elif vname.startswith("Setting.GAME_UID"):
                        cand_uid = _decode_non_secret_reg_value(vdata)
                        if cand_uid:
                            uid = cand_uid
                    elif vname.startswith("Setting.SERVER_ID"):
                        cand_srv = _parse_int_safe(vdata)
                        if cand_srv > 0:
                            server_id = cand_srv
        except OSError:
            pass

    verified = bool(has_token and uid)
    return {
        "unity_profile": prof,
        "has_token": bool(has_token),
        "uid": uid,
        "server_id": int(server_id),
        "verified": verified,
        "needs_email_code": not verified,
    }


def clear_profile_session_token(unity_profile: str) -> dict[str, Any]:
    """Delete ONLY session token and account UID values inside HKCU\\Software\\ReadyGo\\<unity_profile>.

    Never touches any other profile or registry hive. Ensures the next launch of this isolated
    profile prompts Last Z's official Email Login and Email Verification Code flow.
    """
    prof = str(unity_profile or "").strip()
    if not prof or not _PROFILE_NAME_PATTERN.fullmatch(prof):
        return {
            "ok": False,
            "unity_profile": prof,
            "key_existed": False,
            "deleted_count": 0,
            "deleted_names": [],
            "error": "Invalid unity_profile name",
            "message": f"Refused to clear session for invalid unity_profile '{prof}'",
        }

    if winreg is None:
        return {
            "ok": False,
            "unity_profile": prof,
            "key_existed": False,
            "deleted_count": 0,
            "deleted_names": [],
            "error": "winreg is unavailable on this platform",
            "message": "Windows Registry API is unavailable",
        }

    subkey = f"{READYGO_REG_BASE}\\{prof}"
    access = winreg.KEY_READ | winreg.KEY_SET_VALUE
    deleted_names: list[str] = []

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, access) as sk:
            val_count = winreg.QueryInfoKey(sk)[1]
            to_delete: list[str] = []
            for idx in range(val_count):
                # Discard value data immediately without reading or inspecting bytes.
                vname, _, _ = winreg.EnumValue(sk, idx)
                if any(vname.startswith(prefix) for prefix in _SESSION_CLEAR_PREFIXES):
                    to_delete.append(vname)
            for vname in to_delete:
                winreg.DeleteValue(sk, vname)
                deleted_names.append(vname)
    except FileNotFoundError:
        return {
            "ok": True,
            "unity_profile": prof,
            "key_existed": False,
            "deleted_count": 0,
            "deleted_names": [],
            "message": f"Profile '{prof}' has no saved session in registry; ready for fresh email login.",
        }
    except OSError as exc:
        return {
            "ok": False,
            "unity_profile": prof,
            "key_existed": True,
            "deleted_count": len(deleted_names),
            "deleted_names": deleted_names,
            "error": str(exc),
            "message": f"Could not clear session values for '{prof}': {exc}",
        }

    return {
        "ok": True,
        "unity_profile": prof,
        "key_existed": True,
        "deleted_count": len(deleted_names),
        "deleted_names": deleted_names,
        "message": (
            f"Cleared {len(deleted_names)} saved session value(s) for '{prof}'. "
            "Next launch will prompt for Last Z email verification code."
        ),
    }


# ------------------------------------------------------------------
# Validation & Vault Persistence
# ------------------------------------------------------------------


def validate_email(email: str) -> tuple[bool, str]:
    """Validate and normalize an email address (trimmed lowercase local@domain.tld).

    Returns `(True, normalized_email)` on success or `(False, error_message)` on failure.
    """
    cleaned = str(email or "").strip().lower()
    if not cleaned:
        return False, "Email address is required"
    if len(cleaned) > 254:
        return False, "Email address exceeds maximum length (254 characters)"
    if any(ch.isspace() for ch in cleaned):
        return False, "Email address cannot contain whitespace"
    if cleaned.count("@") != 1:
        return False, "Invalid email address (expected local@domain.tld)"
    local_part, domain_part = cleaned.split("@", 1)
    if not local_part or not domain_part:
        return False, "Invalid email address (expected local@domain.tld)"
    if local_part.startswith(".") or local_part.endswith(".") or ".." in local_part:
        return False, "Invalid email local part (leading, trailing, or consecutive dots)"
    if ".." in domain_part:
        return False, "Invalid email domain (consecutive dots)"
    if not _EMAIL_PATTERN.fullmatch(cleaned):
        return False, "Invalid email address syntax (expected local@domain.tld)"
    return True, cleaned


def _normalize_window_style(style: str | None, strict: bool = False) -> str:
    raw = str(style or "").strip().lower()
    if not raw:
        return "borderless"
    if raw in VALID_WINDOW_STYLES:
        return raw
    if strict:
        raise ValueError(
            f"Invalid window_style '{style}' (expected one of {', '.join(VALID_WINDOW_STYLES)})"
        )
    return "borderless"


def _sanitize_account_record(rec: dict[str, Any]) -> dict[str, Any]:
    """Strip any unexpected secret/token keys before writing to disk."""
    clean: dict[str, Any] = {}
    for k, v in rec.items():
        kl = str(k).lower()
        if any(frag in kl for frag in _FORBIDDEN_VAULT_KEY_FRAGMENTS):
            continue
        clean[k] = v
    return clean


def load_vault() -> dict[str, Any]:
    """Load the bound accounts vault JSON safely, returning an empty schema if missing."""
    path = resolve_vault_path()
    with _VAULT_IO_LOCK:
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    accounts = [
                        dict(item)
                        for item in (raw.get("accounts") or [])
                        if isinstance(item, dict)
                    ]
                    return {
                        "schema_version": int(raw.get("schema_version") or 1),
                        "updated_at": int(raw.get("updated_at") or 0),
                        "accounts": accounts,
                    }
            except Exception:
                pass
    return {
        "schema_version": 1,
        "updated_at": 0,
        "accounts": [],
    }


def save_vault(data: dict[str, Any]) -> None:
    """Persist the bound accounts vault atomically via temp file + `os.replace`."""
    path = resolve_vault_path()
    accounts_clean = [
        _sanitize_account_record(item)
        for item in (data.get("accounts") or [])
        if isinstance(item, dict)
    ]
    payload = {
        "schema_version": int(data.get("schema_version") or 1),
        "updated_at": int(time.time()),
        "accounts": accounts_clean,
    }

    with _VAULT_IO_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Keep temp filename underscore-free as well.
        tmp = path.with_name(
            f"{path.name}.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp"
        )
        try:
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
                fh.flush()
                try:
                    os.fsync(fh.fileno())
                except OSError:
                    pass
            for attempt in range(5):
                try:
                    os.replace(tmp, path)
                    break
                except (PermissionError, OSError):
                    if attempt == 4:
                        raise
                    time.sleep(0.05)
        finally:
            try:
                if tmp.exists():
                    tmp.unlink(missing_ok=True)
            except OSError:
                pass


# ------------------------------------------------------------------
# Account Discovery, Allocation, Binding & CRUD
# ------------------------------------------------------------------


def _find_account_index(accounts: list[dict[str, Any]], identifier: str) -> int | None:
    needle = str(identifier or "").strip().lower()
    if not needle:
        return None
    for field in ("id", "unity_profile", "email", "label"):
        for idx, acc in enumerate(accounts):
            val = str(acc.get(field) or "").strip().lower()
            if val and val == needle:
                return idx
    return None


def _find_running_game_pids(accounts: list[dict[str, Any]]) -> dict[str, int]:
    """Lightweight zero-Frida scan returning `{account_id: pid}` for running vault accounts."""
    if not accounts:
        return {}
    by_exe_name: dict[str, list[dict[str, Any]]] = {}
    for acc in accounts:
        exe_name = str(acc.get("exe_name") or "").strip().lower()
        if not exe_name and acc.get("exe_path"):
            exe_name = Path(str(acc["exe_path"])).name.lower()
        if exe_name:
            by_exe_name.setdefault(exe_name, []).append(acc)

    if not by_exe_name:
        return {}

    matched: dict[str, int] = {}
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = str(proc.info.get("name") or "").lower()
                if pname not in by_exe_name:
                    continue
                candidates = by_exe_name[pname]
                pid = int(proc.info["pid"])
                proc_exe_norm = ""
                try:
                    raw_exe = proc.exe()
                    if raw_exe:
                        proc_exe_norm = os.path.normcase(os.path.abspath(raw_exe))
                except (psutil.NoSuchProcess, psutil.AccessDenied, OSError, AttributeError):
                    proc_exe_norm = ""

                picked = None
                if proc_exe_norm:
                    for cand in candidates:
                        cpath = str(cand.get("exe_path") or "").strip()
                        if cpath and os.path.normcase(os.path.abspath(cpath)) == proc_exe_norm:
                            picked = cand
                            break
                if picked is None and len(candidates) == 1:
                    picked = candidates[0]
                if picked is not None:
                    aid = str(picked.get("id") or picked.get("unity_profile") or "").lower()
                    if aid and aid not in matched:
                        matched[aid] = pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                continue
    except Exception:
        return matched
    return matched


def _enrich_account(
    acc: dict[str, Any],
    reg_reader: Callable[[str], dict[str, Any] | None] | None = None,
    running_pids: dict[str, int] | None = None,
) -> dict[str, Any]:
    prof = str(acc.get("unity_profile") or "").strip()
    aid = str(acc.get("id") or prof.lower()).strip().lower()
    exe_path_str = str(acc.get("exe_path") or "").strip()
    game_dir_str = str(acc.get("game_dir") or "").strip()
    exe_name = str(acc.get("exe_name") or (Path(exe_path_str).name if exe_path_str else "")).strip()
    window_style = _normalize_window_style(acc.get("window_style"), strict=False)
    source = str(acc.get("source") or "bound").strip().lower()
    if source not in ("bound", "imported"):
        source = "bound"

    sess = inspect_profile_session(prof, reg_reader=reg_reader)
    pid_val: int | None = None
    if running_pids is not None:
        pid_val = running_pids.get(aid)
    is_running = pid_val is not None and pid_val > 0
    slot_ready = bool(exe_path_str and Path(exe_path_str).is_file())

    return {
        "id": aid,
        "email": str(acc.get("email") or "").strip().lower(),
        "label": str(acc.get("label") or prof or aid).strip(),
        "unity_profile": prof,
        "exe_name": exe_name,
        "game_dir": game_dir_str,
        "exe_path": exe_path_str,
        "window_style": window_style,
        "source": source,
        "verified": bool(sess["verified"]),
        "needs_email_code": bool(sess["needs_email_code"]),
        "has_token": bool(sess["has_token"]),
        "uid": str(sess["uid"]),
        "server_id": int(sess["server_id"]),
        "is_running": is_running,
        "pid": pid_val,
        "last_mode": str(acc.get("last_mode") or "").strip().lower(),
        "last_launched_at": int(acc.get("last_launched_at") or 0),
        "slot_ready": slot_ready,
    }


def sync_discovered_accounts(save: bool = True) -> list[dict[str, Any]]:
    """Import existing configured Last Z profiles via `tools/client discovery.py`.

    Preserves any user-set `email`, `label`, and `window_style` on existing vault entries.
    """
    vault = load_vault()
    accounts: list[dict[str, Any]] = list(vault.get("accounts") or [])
    by_prof = {
        str(a.get("unity_profile") or "").strip().lower(): idx
        for idx, a in enumerate(accounts)
        if str(a.get("unity_profile") or "").strip()
    }
    by_id = {
        str(a.get("id") or "").strip().lower(): idx
        for idx, a in enumerate(accounts)
        if str(a.get("id") or "").strip()
    }

    cd = _load_client_discovery()
    if cd is None or not hasattr(cd, "discover_clients"):
        return accounts

    try:
        discovered = cd.discover_clients(save_cache=False) or []
    except Exception:
        return accounts

    changed = False
    now_ts = int(time.time())
    for client in discovered:
        if not isinstance(client, dict):
            continue
        prof = str(client.get("unity_profile") or "").strip()
        if not prof:
            continue
        cid = str(client.get("id") or prof.lower()).strip().lower()
        game_dir = str(client.get("game_dir") or "").strip()
        exe_path = str(client.get("exe_path") or "").strip()
        exe_name = str(client.get("exe_name") or (Path(exe_path).name if exe_path else "")).strip()
        disc_label = str(client.get("label") or prof).strip()

        existing_idx = by_prof.get(prof.lower())
        if existing_idx is None:
            existing_idx = by_id.get(cid)

        if existing_idx is not None:
            existing = accounts[existing_idx]
            # Preserve user-set email, label, and window_style unconditionally.
            if not existing.get("game_dir") and game_dir:
                existing["game_dir"] = game_dir
                changed = True
            if not existing.get("exe_path") and exe_path:
                existing["exe_path"] = exe_path
                changed = True
            if not existing.get("exe_name") and exe_name:
                existing["exe_name"] = exe_name
                changed = True
            if existing.get("source") == "imported":
                if game_dir and existing.get("game_dir") != game_dir and Path(game_dir).exists():
                    existing["game_dir"] = game_dir
                    changed = True
                if exe_path and existing.get("exe_path") != exe_path and Path(exe_path).is_file():
                    existing["exe_path"] = exe_path
                    changed = True
                if exe_name and not existing.get("exe_name"):
                    existing["exe_name"] = exe_name
                    changed = True
        else:
            entry = {
                "id": cid,
                "email": "",
                "label": disc_label,
                "unity_profile": prof,
                "exe_name": exe_name,
                "game_dir": game_dir,
                "exe_path": exe_path,
                "window_style": _normalize_window_style(client.get("window_style") or "borderless"),
                "source": "imported",
                "created_at": now_ts,
                "last_mode": "",
                "last_launched_at": 0,
            }
            accounts.append(entry)
            by_prof[prof.lower()] = len(accounts) - 1
            by_id[cid] = len(accounts) - 1
            changed = True

    if save and changed:
        vault["accounts"] = accounts
        save_vault(vault)
    return accounts


def list_bound_accounts(
    sync_discovered: bool = True,
    reg_reader: Callable[[str], dict[str, Any] | None] | None = None,
) -> list[dict[str, Any]]:
    """Return enriched metadata for all bound and imported accounts."""
    if sync_discovered:
        accounts = sync_discovered_accounts(save=True)
    else:
        accounts = list(load_vault().get("accounts") or [])

    running_pids = _find_running_game_pids(accounts)
    return [
        _enrich_account(acc, reg_reader=reg_reader, running_pids=running_pids)
        for acc in accounts
    ]


def allocate_next_profile(existing_accounts: list[dict[str, Any]]) -> tuple[str, str]:
    """Allocate the next unused 5-char Unity profile (`Hz01Z`..`Hz99Z`) and exe (`Hz01Game.exe`..)."""
    used_profiles: set[str] = set(RESERVED_PROFILES)
    used_exes: set[str] = set()

    for acc in existing_accounts or []:
        if not isinstance(acc, dict):
            continue
        prof = str(acc.get("unity_profile") or "").strip().upper()
        aid = str(acc.get("id") or "").strip().upper()
        if prof:
            used_profiles.add(prof)
        if aid:
            used_profiles.add(aid)
        exe_name = str(acc.get("exe_name") or "").strip().lower()
        if exe_name:
            used_exes.add(exe_name)
        exe_path = str(acc.get("exe_path") or "").strip()
        if exe_path:
            used_exes.add(Path(exe_path).name.lower())

    for num in range(1, 100):
        prof = f"Hz{num:02d}Z"
        exe_name = f"Hz{num:02d}Game.exe"
        if prof.upper() not in used_profiles and exe_name.lower() not in used_exes:
            return prof, exe_name

    raise RuntimeError("No free Hz01Z..Hz99Z profile slots remain")


def _invoke_ensure_account_slot(
    unity_profile: str,
    exe_name: str,
    engine_root: Path | None = None,
    source_game_dir: str | None = None,
) -> dict[str, Any]:
    """Call `game engine manager.py`'s `ensure_account_slot` if installed and available."""
    gem = _load_game_engine_manager()
    if gem is None or not hasattr(gem, "ensure_account_slot"):
        return {
            "ok": False,
            "slot_ready": False,
            "game_dir": "",
            "exe_path": "",
            "message": "Last Z Engine is not installed yet. Import or Download the Engine first before launching.",
        }

    fn = gem.ensure_account_slot
    try:
        sig = inspect.signature(fn)
        kwargs: dict[str, Any] = {}
        if "engine_root" in sig.parameters:
            kwargs["engine_root"] = engine_root
        if "source_game_dir" in sig.parameters:
            kwargs["source_game_dir"] = source_game_dir
        res = fn(unity_profile, exe_name, **kwargs)
    except Exception as exc:
        return {
            "ok": False,
            "slot_ready": False,
            "game_dir": "",
            "exe_path": "",
            "message": (
                f"Could not prepare isolated game slot ({exc}). "
                "Import or Download the Last Z Engine first."
            ),
        }

    if not isinstance(res, dict):
        return {
            "ok": False,
            "slot_ready": False,
            "game_dir": "",
            "exe_path": "",
            "message": "Unexpected response from Game Engine Manager. Import or Download the Engine first.",
        }

    ok = bool(res.get("ok", res.get("slot_ready", res.get("ready", False))))
    game_dir = str(res.get("game_dir") or res.get("slot_game_dir") or res.get("slot_dir") or "").strip()
    exe_path = str(res.get("exe_path") or "").strip()
    if not exe_path and game_dir:
        exe_path = str(Path(game_dir) / exe_name)
    slot_ready = bool(ok and exe_path and Path(exe_path).is_file())
    msg = str(res.get("message") or res.get("error") or "").strip()
    if not ok:
        if not msg:
            msg = "No Last Z Engine found yet. Import or Download the Engine first."
        elif "import" not in msg.lower() and "download" not in msg.lower():
            msg = f"{msg} Import or Download the Last Z Engine first."
    return {
        "ok": ok,
        "slot_ready": slot_ready,
        "game_dir": game_dir,
        "exe_path": exe_path,
        "message": msg,
    }


def bind_new_account(
    email: str,
    label: str = "",
    window_style: str = "borderless",
    source_game_dir: str | None = None,
    engine_root: Path | None = None,
    skip_registry_clear: bool = False,
    reg_reader: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Bind a new Last Z account email to a fresh isolated `HzXXZ` profile slot."""
    valid, norm_or_err = validate_email(email)
    if not valid:
        return {"ok": False, "error": norm_or_err, "message": norm_or_err}
    norm_email = norm_or_err

    try:
        eff_style = _normalize_window_style(window_style, strict=True)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "message": str(exc)}

    vault = load_vault()
    accounts: list[dict[str, Any]] = list(vault.get("accounts") or [])

    for existing in accounts:
        if str(existing.get("email") or "").strip().lower() == norm_email:
            err = f"Email '{norm_email}' is already bound to account '{existing.get('label') or existing.get('id')}'"
            return {"ok": False, "error": err, "message": err}

    try:
        unity_profile, exe_name = allocate_next_profile(accounts)
    except RuntimeError as exc:
        return {"ok": False, "error": str(exc), "message": str(exc)}

    if not skip_registry_clear:
        clear_profile_session_token(unity_profile)

    slot_info = _invoke_ensure_account_slot(
        unity_profile,
        exe_name,
        engine_root=engine_root,
        source_game_dir=source_game_dir,
    )

    clean_label = str(label or "").strip() or norm_email.split("@", 1)[0]
    entry = {
        "id": unity_profile.lower(),
        "email": norm_email,
        "label": clean_label,
        "unity_profile": unity_profile,
        "exe_name": exe_name,
        "game_dir": slot_info["game_dir"],
        "exe_path": slot_info["exe_path"],
        "window_style": eff_style,
        "source": "bound",
        "created_at": int(time.time()),
        "last_mode": "",
        "last_launched_at": 0,
    }
    accounts.append(entry)
    vault["accounts"] = accounts
    save_vault(vault)

    # Freshly bound profiles start unverified unless a mock reg_reader explicitly reports otherwise.
    effective_reader = reg_reader
    if effective_reader is None and skip_registry_clear:
        effective_reader = lambda _p: {}
    enriched = _enrich_account(entry, reg_reader=effective_reader, running_pids={})

    if enriched["slot_ready"]:
        msg = (
            f"Bound '{clean_label}' ({norm_email}) to isolated profile {unity_profile}. "
            "First login will require Last Z's email verification code."
        )
    else:
        note = slot_info.get("message") or "Import or Download the Last Z Engine first."
        msg = (
            f"Bound '{clean_label}' ({norm_email}) to isolated profile {unity_profile}. "
            f"{note} First login will require Last Z's email verification code."
        )

    return {
        "ok": True,
        "account": enriched,
        "requires_email_code": bool(enriched["needs_email_code"]),
        "slot_ready": bool(enriched["slot_ready"]),
        "message": msg,
    }


def update_account(
    account_id: str,
    email: str | None = None,
    label: str | None = None,
    window_style: str | None = None,
    reg_reader: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Atomically update email, label, and/or window_style for an existing vault account."""
    vault = load_vault()
    accounts: list[dict[str, Any]] = list(vault.get("accounts") or [])
    idx = _find_account_index(accounts, account_id)
    if idx is None:
        err = f"Account '{account_id}' not found in vault"
        return {"ok": False, "error": err, "message": err}

    target = dict(accounts[idx])

    if email is not None:
        valid, norm_or_err = validate_email(email)
        if not valid:
            return {"ok": False, "error": norm_or_err, "message": norm_or_err}
        for other_idx, other in enumerate(accounts):
            if other_idx == idx:
                continue
            if str(other.get("email") or "").strip().lower() == norm_or_err:
                err = f"Email '{norm_or_err}' is already bound to account '{other.get('label') or other.get('id')}'"
                return {"ok": False, "error": err, "message": err}
        target["email"] = norm_or_err

    if label is not None:
        clean_label = str(label).strip()
        if not clean_label:
            err = "Account label cannot be empty"
            return {"ok": False, "error": err, "message": err}
        target["label"] = clean_label

    if window_style is not None:
        try:
            target["window_style"] = _normalize_window_style(window_style, strict=True)
        except ValueError as exc:
            return {"ok": False, "error": str(exc), "message": str(exc)}

    accounts[idx] = target
    vault["accounts"] = accounts
    save_vault(vault)

    enriched = _enrich_account(target, reg_reader=reg_reader, running_pids=_find_running_game_pids([target]))
    return {
        "ok": True,
        "account": enriched,
        "message": f"Updated account '{enriched['label']}' ({enriched['unity_profile']}).",
    }


def unbind_account(account_id: str, clear_session: bool = False) -> dict[str, Any]:
    """Remove an account from the vault and optionally clear its isolated Unity session token."""
    vault = load_vault()
    accounts: list[dict[str, Any]] = list(vault.get("accounts") or [])
    idx = _find_account_index(accounts, account_id)
    if idx is None:
        err = f"Account '{account_id}' not found in vault"
        return {"ok": False, "error": err, "message": err}

    removed = accounts.pop(idx)
    vault["accounts"] = accounts
    save_vault(vault)

    clear_res: dict[str, Any] | None = None
    if clear_session:
        clear_res = clear_profile_session_token(str(removed.get("unity_profile") or ""))

    return {
        "ok": True,
        "removed_id": str(removed.get("id") or account_id),
        "unity_profile": str(removed.get("unity_profile") or ""),
        "session_cleared": bool(clear_session and (clear_res or {}).get("ok", False)),
        "message": f"Removed account '{removed.get('label') or removed.get('id')}' from vault.",
    }


def reset_account_verification(account_id: str) -> dict[str, Any]:
    """Clear saved `SeToken*` / UID session values so next launch requires an email verification code."""
    vault = load_vault()
    accounts: list[dict[str, Any]] = list(vault.get("accounts") or [])
    idx = _find_account_index(accounts, account_id)
    if idx is None:
        err = f"Account '{account_id}' not found in vault"
        return {"ok": False, "error": err, "message": err}

    acc = accounts[idx]
    prof = str(acc.get("unity_profile") or "").strip()
    clear_res = clear_profile_session_token(prof)
    if not clear_res.get("ok"):
        return {
            "ok": False,
            "account_id": str(acc.get("id") or prof.lower()),
            "unity_profile": prof,
            "error": clear_res.get("error", "Failed to clear session"),
            "message": clear_res.get("message", "Failed to clear session"),
        }

    return {
        "ok": True,
        "account_id": str(acc.get("id") or prof.lower()),
        "unity_profile": prof,
        "deleted_count": int(clear_res.get("deleted_count", 0)),
        "requires_email_code": True,
        "message": (
            f"Reset email verification for '{acc.get('label') or prof}' ({prof}). "
            "Next launch will prompt Last Z's official Email Verification Code."
        ),
    }


# ------------------------------------------------------------------
# Strict Vanilla Zero-Attach Guard & Borderless Launcher
# ------------------------------------------------------------------


def _is_protected_game_exe(proc_name_lower: str) -> bool:
    if not proc_name_lower.endswith(".exe"):
        return False
    if proc_name_lower in ("survival.exe", "last z.exe", "launcher.exe"):
        return True
    if proc_name_lower.endswith("game.exe") or proc_name_lower.startswith("launcher_"):
        return True
    return False


def stop_background_heinz_daemons() -> dict[str, Any]:
    """Cleanly terminate any running HeinZ daemon or live translator processes.

    NEVER touches any game executable or the calling process PID.
    """
    my_pid = os.getpid()
    targets: list[tuple[Any, int, str, str]] = []

    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                pid = int(proc.info.get("pid") or 0)
                if pid <= 0 or pid == my_pid:
                    continue
                pname = str(proc.info.get("name") or "")
                pname_low = pname.lower()
                if _is_protected_game_exe(pname_low):
                    continue
                if not ("python" in pname_low or pname_low in ("py.exe", "heinz.exe")):
                    continue

                cmdline_raw = proc.info.get("cmdline") or []
                cmdline_str = " ".join(str(part) for part in cmdline_raw).lower()
                if not cmdline_str:
                    continue
                # Never interrupt test runners invoking unit tests.
                if "unittest" in cmdline_str or "pytest" in cmdline_str:
                    continue

                matched_marker = next(
                    (marker for marker in _DAEMON_SCRIPT_MARKERS if marker in cmdline_str),
                    None,
                )
                if matched_marker is not None:
                    targets.append((proc, pid, pname, matched_marker))
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                continue
    except Exception as exc:
        return {
            "ok": False,
            "stopped_count": 0,
            "stopped": [],
            "errors": [str(exc)],
        }

    stopped: list[dict[str, Any]] = []
    errors: list[str] = []
    terminated_procs: list[tuple[Any, int, str, str]] = []

    for proc, pid, pname, marker in targets:
        try:
            proc.terminate()
            terminated_procs.append((proc, pid, pname, marker))
        except (psutil.NoSuchProcess, ProcessLookupError):
            stopped.append({"pid": pid, "name": pname, "target": marker})
        except Exception as exc:
            errors.append(f"PID {pid} ({marker}): {exc}")

    for proc, pid, pname, marker in terminated_procs:
        try:
            if hasattr(proc, "wait"):
                proc.wait(timeout=2.0)
            stopped.append({"pid": pid, "name": pname, "target": marker})
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                if hasattr(proc, "wait"):
                    proc.wait(timeout=1.0)
                stopped.append({"pid": pid, "name": pname, "target": marker})
            except Exception as exc:
                errors.append(f"PID {pid} kill failed ({marker}): {exc}")
        except (psutil.NoSuchProcess, ProcessLookupError):
            stopped.append({"pid": pid, "name": pname, "target": marker})
        except Exception as exc:
            errors.append(f"PID {pid} wait failed ({marker}): {exc}")

    return {
        "ok": len(errors) == 0,
        "stopped_count": len(stopped),
        "stopped": stopped,
        "errors": errors,
    }


def _detect_primary_monitor_size() -> tuple[int, int]:
    try:
        if os.name == "nt":
            user32 = ctypes.windll.user32
            w = int(user32.GetSystemMetrics(0))
            h = int(user32.GetSystemMetrics(1))
            if w >= 640 and h >= 360:
                return w, h
    except Exception:
        pass
    return 1280, 720


def build_launch_args(
    exe_path: Path,
    window_style: str = "borderless",
    width: int = 0,
    height: int = 0,
) -> list[str]:
    """Build Unity launch argv including `--from-launcher=` token and window style flags."""
    eff_style = _normalize_window_style(window_style, strict=True)
    token = base64.b64encode(f"{int(time.time())}|LZ".encode("utf-8")).decode("utf-8")
    args = [str(exe_path), f"--from-launcher={token}"]

    if eff_style == "borderless":
        if int(width or 0) > 0 and int(height or 0) > 0:
            w, h = int(width), int(height)
        else:
            det_w, det_h = _detect_primary_monitor_size()
            w = int(width) if int(width or 0) > 0 else det_w
            h = int(height) if int(height or 0) > 0 else det_h
        args.extend(
            [
                "-popupwindow",
                "-screen-fullscreen",
                "0",
                "-screen-width",
                str(w),
                "-screen-height",
                str(h),
            ]
        )
    elif eff_style == "windowed":
        w = int(width) if int(width or 0) > 0 else 1280
        h = int(height) if int(height or 0) > 0 else 720
        args.extend(
            [
                "-screen-width",
                str(w),
                "-screen-height",
                str(h),
                "-screen-fullscreen",
                "0",
            ]
        )
    elif eff_style == "fullscreen":
        args.extend(["-screen-fullscreen", "1"])

    return args


def _signed_dword(val: int) -> int:
    return struct.unpack("i", struct.pack("I", int(val) & 0xFFFFFFFF))[0]


def _repair_window_and_gpu_direct(unity_profile: str, exe_path: Path) -> None:
    """Zero-Frida direct HKCU repair for off-screen `-32000` Unity coords and High-Perf GPU pref."""
    if winreg is None:
        return
    prof = str(unity_profile or "").strip()
    if prof and _PROFILE_NAME_PATTERN.fullmatch(prof):
        subkey = f"{READYGO_REG_BASE}\\{prof}"
        pos_keys = (
            ("Screenmanager Window Position X_h4088080503", 80),
            ("Screenmanager Window Position Y_h4088080502", 80),
            ("WindowX_h2353518033", 80),
            ("WindowY_h2353518032", 80),
        )
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE
            ) as key:
                repaired = False
                for name, default_val in pos_keys:
                    try:
                        cur, typ = winreg.QueryValueEx(key, name)
                        sval = _signed_dword(cur) if (typ == winreg.REG_DWORD and isinstance(cur, int)) else -99999
                    except FileNotFoundError:
                        continue
                    if sval < -100 or sval > 10000:
                        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, default_val)
                        repaired = True
                if repaired:
                    winreg.SetValueEx(
                        key,
                        "Screenmanager Fullscreen mode_h3630240806",
                        0,
                        winreg.REG_DWORD,
                        3,
                    )
        except OSError:
            pass

    try:
        if exe_path.is_file():
            with winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, GPU_PREF_KEY, 0, winreg.KEY_SET_VALUE
            ) as gk:
                winreg.SetValueEx(gk, str(exe_path), 0, winreg.REG_SZ, "GpuPreference=2;")
    except OSError:
        pass


def _prepare_runtime_prefs(unity_profile: str, exe_path: Path, mode: str) -> None:
    """Repair off-screen Unity coordinates and apply High-Perf GPU preference safely."""
    if mode == "vanilla":
        # Strictly avoid loading sync farm clients / client discovery in Vanilla mode so Frida is never imported.
        _repair_window_and_gpu_direct(unity_profile, exe_path)
        return

    sfc = _load_sync_farm_clients()
    if sfc is not None:
        try:
            if hasattr(sfc, "repair_unity_window_position"):
                sfc.repair_unity_window_position(unity_profile)
        except Exception:
            pass
        try:
            if hasattr(sfc, "apply_gpu_high_performance") and exe_path.is_file():
                sfc.apply_gpu_high_performance([exe_path])
        except Exception:
            pass
        return

    _repair_window_and_gpu_direct(unity_profile, exe_path)


def launch_bound_account(
    account_id: str,
    mode: str = "vanilla",
    window_style: str | None = None,
    engine_root: Path | None = None,
    dry_run: bool = False,
    popen_fn: Callable[..., Any] | None = None,
    reg_reader: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Launch a bound Last Z account in Pure Vanilla (zero-attach) or Enhanced mode."""
    eff_mode = str(mode or "vanilla").strip().lower()
    if eff_mode not in VALID_LAUNCH_MODES:
        err = f"Invalid launch mode '{mode}' (expected 'vanilla' or 'enhanced')"
        return {"ok": False, "error": err, "message": err}

    vault = load_vault()
    accounts: list[dict[str, Any]] = list(vault.get("accounts") or [])
    idx = _find_account_index(accounts, account_id)
    if idx is None:
        err = f"Account '{account_id}' not found in bound accounts vault"
        return {"ok": False, "error": err, "message": err}

    acc = dict(accounts[idx])
    try:
        eff_style = _normalize_window_style(
            window_style if window_style is not None else acc.get("window_style"),
            strict=True,
        )
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "message": str(exc)}

    prof = str(acc.get("unity_profile") or "").strip()
    exe_name = str(acc.get("exe_name") or "").strip() or "Survival.exe"
    exe_path_str = str(acc.get("exe_path") or "").strip()
    game_dir_str = str(acc.get("game_dir") or "").strip()
    exe_path = Path(exe_path_str) if exe_path_str else None

    if exe_path is None or not exe_path.is_file():
        slot_info = _invoke_ensure_account_slot(prof, exe_name, engine_root=engine_root)
        if slot_info.get("exe_path"):
            exe_path_str = slot_info["exe_path"]
            exe_path = Path(exe_path_str)
            acc["exe_path"] = exe_path_str
        if slot_info.get("game_dir"):
            game_dir_str = slot_info["game_dir"]
            acc["game_dir"] = game_dir_str

    if exe_path is None or (not dry_run and not exe_path.is_file()):
        err = (
            f"Isolated game slot executable is missing for '{acc.get('label') or prof}'. "
            "Import or Download the Last Z Engine first."
        )
        return {
            "ok": False,
            "mode": eff_mode,
            "should_exit_heinz": False,
            "account_id": str(acc.get("id") or prof.lower()),
            "slot_ready": False,
            "error": err,
            "message": err,
        }

    work_dir = Path(game_dir_str) if game_dir_str else exe_path.parent
    session = inspect_profile_session(prof, reg_reader=reg_reader)
    needs_email_code = bool(session["needs_email_code"])

    # Skip real HKCU edits during dry-run or when a mock reg_reader is active.
    if not dry_run and reg_reader is None:
        try:
            _prepare_runtime_prefs(prof, exe_path, eff_mode)
        except Exception:
            pass

    stopped_count = 0
    if eff_mode == "vanilla" and not dry_run:
        stop_res = stop_background_heinz_daemons()
        stopped_count = int(stop_res.get("stopped_count", 0))

    args = build_launch_args(exe_path, window_style=eff_style)

    env = os.environ.copy()
    env["__COMPAT_LAYER"] = "DISABLEDXMAXIMIZEDWINDOWEDMODE"
    base_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    breakaway_flag = getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000)
    creationflags = base_flags | breakaway_flag

    popen_kwargs: dict[str, Any] = {
        "cwd": str(work_dir),
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    si_cls = getattr(subprocess, "STARTUPINFO", None)
    if si_cls is not None:
        si = si_cls()
        si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        si.wShowWindow = 1  # SW_SHOWNORMAL
        popen_kwargs["startupinfo"] = si

    pid = 0
    if not dry_run:
        spawner = popen_fn or subprocess.Popen
        try:
            proc = spawner(args, creationflags=creationflags, **popen_kwargs)
        except OSError:
            if popen_fn is not None:
                raise
            proc = spawner(args, creationflags=base_flags, **popen_kwargs)
        pid = int(getattr(proc, "pid", 0) or 0)

        acc["last_launched_at"] = int(time.time())
        acc["last_mode"] = eff_mode
        accounts[idx] = acc
        vault["accounts"] = accounts
        save_vault(vault)

    mode_desc = "Pure Vanilla (zero-attach)" if eff_mode == "vanilla" else "Enhanced"
    verify_note = " First-time email verification code required." if needs_email_code else ""
    prefix = "[DRY-RUN] " if dry_run else ""
    msg = (
        f"{prefix}Launched '{acc.get('label') or prof}' ({prof}) in {mode_desc} mode "
        f"[{eff_style}].{verify_note}"
    )

    return {
        "ok": True,
        "mode": eff_mode,
        "should_exit_heinz": (eff_mode == "vanilla"),
        "account_id": str(acc.get("id") or prof.lower()),
        "label": str(acc.get("label") or prof),
        "email": str(acc.get("email") or ""),
        "unity_profile": prof,
        "exe_path": str(exe_path),
        "args": args,
        "pid": pid,
        "needs_email_code": needs_email_code,
        "window_style": eff_style,
        "daemons_stopped": stopped_count,
        "message": msg,
    }


if __name__ == "__main__":
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "list"
    if cmd == "list":
        sync_flag = "--no-sync" not in sys.argv
        print(json.dumps(list_bound_accounts(sync_discovered=sync_flag), indent=2, ensure_ascii=False))
    elif cmd == "bind" and len(sys.argv) >= 3:
        lbl = sys.argv[3] if len(sys.argv) >= 4 else ""
        res = bind_new_account(sys.argv[2], label=lbl)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res.get("ok") else 1)
    elif cmd == "launch" and len(sys.argv) >= 3:
        lmode = sys.argv[3] if len(sys.argv) >= 4 else "vanilla"
        wstyle = sys.argv[4] if len(sys.argv) >= 5 else None
        res = launch_bound_account(sys.argv[2], mode=lmode, window_style=wstyle, dry_run="--dry-run" in sys.argv)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res.get("ok") else 1)
    elif cmd == "reset-verify" and len(sys.argv) >= 3:
        res = reset_account_verification(sys.argv[2])
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res.get("ok") else 1)
    else:
        print(
            json.dumps(
                {
                    "usage": [
                        "list [--no-sync]",
                        "bind <email> [label]",
                        "launch <account_id> [vanilla|enhanced] [borderless|windowed|fullscreen] [--dry-run]",
                        "reset-verify <account_id>",
                    ]
                },
                indent=2,
            )
        )
