import atexit
import ctypes
from ctypes import wintypes
import types
from typing import Any
import json
import os
import random
import re
import subprocess
import sys
import threading
import time
import winreg
from pathlib import Path

import psutil

try:
    import frida
except ImportError:
    frida = None

_SINGLETON_MODULE_KEY = "heinz_client_discovery_singleton"
_SHARED_STATE_MOD_KEY = "_heinz_client_discovery_shared_state"


def _get_shared_state() -> dict[str, Any]:
    mod = sys.modules.get(_SHARED_STATE_MOD_KEY)
    if mod is not None and isinstance(getattr(mod, "state", None), dict):
        return mod.state
    state: dict[str, Any] = {
        "io_lock": threading.Lock(),
        "pid_locks_guard": threading.Lock(),
        "pid_locks": {},
        "session_cache_lock": threading.Lock(),
        "cached_sessions": {},
        "last_detach_ts": {},
        "xlua_cache_lock": threading.Lock(),
        "xlua_loaded_cache": {},
        "discover_cache_lock": threading.Lock(),
        "app_info_cache": {},
        "game_ver_cache": {},
        "discover": {"entry": None, "gen": 0},
        "shortcut_dirs_cache": None,
        "atexit_registered": False,
    }
    mod = types.ModuleType(_SHARED_STATE_MOD_KEY)
    mod.state = state  # type: ignore[attr-defined]
    sys.modules[_SHARED_STATE_MOD_KEY] = mod
    return state


_SHARED_STATE = _get_shared_state()

if os.name == "nt":
    class MODULEENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("th32ModuleID", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("GlblcntUsage", wintypes.DWORD),
            ("ProccntUsage", wintypes.DWORD),
            ("modBaseAddr", ctypes.c_void_p),
            ("modBaseSize", wintypes.DWORD),
            ("hModule", wintypes.HMODULE),
            ("szModule", wintypes.WCHAR * 256),
            ("szExePath", wintypes.WCHAR * 260),
        ]

    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _KERNEL32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _KERNEL32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _KERNEL32.Module32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MODULEENTRY32W)]
    _KERNEL32.Module32FirstW.restype = wintypes.BOOL
    _KERNEL32.Module32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MODULEENTRY32W)]
    _KERNEL32.Module32NextW.restype = wintypes.BOOL
    _KERNEL32.CloseHandle.argtypes = [wintypes.HANDLE]
    _KERNEL32.CloseHandle.restype = wintypes.BOOL
    _KERNEL32.GetLogicalDrives.argtypes = []
    _KERNEL32.GetLogicalDrives.restype = wintypes.DWORD
    _KERNEL32.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    _KERNEL32.GetDriveTypeW.restype = wintypes.UINT
else:
    MODULEENTRY32W = None  # type: ignore[assignment,misc]
    _KERNEL32 = None

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ["HEINZ_DATA_DIR"]) if os.environ.get("HEINZ_DATA_DIR", "").strip() else (REPO_ROOT / "data")
PROFILES_PATH = DATA_DIR / "client profiles.json"

IGNORE_EXES = {
    "unitycrashhandler64.exe",
    "unitycrashhandler32.exe",
    "launcher.exe",
    "launcher_patched.exe",
    "launcher_third.exe",
    "farmlauncherhook.exe",
    "last z.exe",
    "uninstall.exe",
}

_SHORTCUT_DIRS_CACHE: set[Path] | None = None


def _hidden_subproc_kwargs() -> dict:
    kwargs: dict = {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
    }
    si_cls = getattr(subprocess, "STARTUPINFO", None)
    if si_cls is not None:
        si = si_cls()
        si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        si.wShowWindow = 0
        kwargs["startupinfo"] = si
    return kwargs

FRIDA_RPC_JS = r"""
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcallk = nf('lua_pcallk', 'int', ['pointer', 'int', 'int', 'int', 'pointer', 'pointer']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const length = Memory.alloc(8);

function getString(L, index) {
    const p = str(L, index, length);
    if (p.isNull()) return '';
    const sz = Number(length.readU64());
    return sz === 0 ? '' : p.readUtf8String(sz);
}

// Single persistent Interceptor hook on lua_pcallk eliminates Gum trampoline
// attach/detach race conditions (frida-agent.dll 0xC0000005) across rapid calls.
const pendingJobs = [];
let hasPending = false;
let inExec = false;
let hookInstalled = false;

function ensureHook() {
    if (hookInstalled) return;
    hookInstalled = true;
    Interceptor.attach(mod.getExportByName('lua_pcallk'), {
        onEnter(args) {
            if (!hasPending || inExec) return;
            if (pendingJobs.length === 0) {
                hasPending = false;
                return;
            }
            inExec = true;
            const job = pendingJobs.shift();
            hasPending = pendingJobs.length > 0;
            if (!job || job.done) {
                inExec = false;
                return;
            }
            const L = args[0];
            const saved = top(L);
            try {
                const s = Memory.allocUtf8String(job.code);
                if (loadstring(L, s) === 0) {
                    if (pcallk(L, 0, 1, 0, ptr(0), ptr(0)) === 0) {
                        job.finish({ success: true, result: getString(L, -1) });
                    } else {
                        job.finish({ success: false, error: getString(L, -1) });
                    }
                } else {
                    job.finish({ success: false, error: 'Syntax error: ' + getString(L, -1) });
                }
            } catch (e) {
                job.finish({ success: false, error: e.toString() });
            } finally {
                settop(L, saved);
                inExec = false;
            }
        }
    });
}

function execLua(code, timeoutMs) {
    ensureHook();
    const ms = (typeof timeoutMs === 'number' && timeoutMs > 0) ? timeoutMs : 5000;
    return new Promise((resolve) => {
        const job = {
            code: code,
            done: false,
            timer: null,
            finish(payload) {
                if (this.done) return;
                this.done = true;
                if (this.timer !== null) {
                    clearTimeout(this.timer);
                    this.timer = null;
                }
                const idx = pendingJobs.indexOf(this);
                if (idx !== -1) pendingJobs.splice(idx, 1);
                hasPending = pendingJobs.length > 0;
                resolve(payload);
            }
        };
        job.timer = setTimeout(() => {
            job.finish({ success: false, error: 'Client busy or scene loading (Lua tick timeout).' });
        }, ms);
        pendingJobs.push(job);
        hasPending = true;
    });
}

rpc.exports = {
    evalLua(code, timeoutMs) {
        return execLua(code, timeoutMs);
    }
};
"""

LUA_QUICK_STATUS = r"""
local function isNull(o)
    if o == nil then return true end
    if type(o) == "userdata" then return o:Equals(nil) end
    return false
end

local function ser(v)
    local t = type(v)
    if t == "number" then
        if v ~= v or v == math.huge or v == -math.huge then return "null" end
        return tostring(v)
    elseif t == "boolean" then
        return tostring(v)
    elseif t == "string" then
        return '"' .. v:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t') .. '"'
    elseif t == "table" then
        local isArr = true
        local maxI, cnt = 0, 0
        for k, _ in pairs(v) do
            cnt = cnt + 1
            if type(k) ~= "number" or k <= 0 or math.floor(k) ~= k then
                isArr = false
            elseif k > maxI then
                maxI = k
            end
        end
        if cnt == 0 then return "[]" end
        if isArr and maxI == cnt then
            local parts = {}
            for i = 1, cnt do parts[i] = ser(v[i]) end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            local parts = {}
            for k, val in pairs(v) do
                table.insert(parts, string.format('"%s":%s', tostring(k), ser(val)))
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    end
    return "null"
end

local _rjson = package and package.loaded and package.loaded.rapidjson
local function _encode_json(tbl)
    if _rjson and type(_rjson.encode) == "function" then
        local ok, s = pcall(_rjson.encode, tbl)
        if ok and type(s) == "string" then
            return s
        end
    end
    return ser(tbl)
end

local p = LuaEntry and LuaEntry.Player
local uid = p and (p.uid or (p.GetUid and p:GetUid())) or ""
local uidStr = tostring(uid)
if not p or uidStr == "" or uidStr == "nil" then
    return _encode_json({ loggedIn = false, sceneId = (SceneManager and SceneManager.CurrSceneID) or 0 })
end

local serverId = (p.GetCurServerId and p:GetCurServerId()) or p.serverId or 0
local selfServerId = (p.GetSelfServerId and p:GetSelfServerId()) or serverId
local bm = DataCenter and DataCenter.BuildManager
local hqLevel = (bm and bm.MainLv and bm.MainLv > 0 and bm.MainLv) or (p.mainCityLv and p.mainCityLv > 0 and p.mainCityLv) or 0
local playerPower = (p.power and p.power > 0 and p.power) or (p.playerPower and p.playerPower > 0 and p.playerPower) or 0
local abd = DataCenter and DataCenter.AllianceBaseDataManager and DataCenter.AllianceBaseDataManager:GetAllianceBaseData()
local alTag = (abd and abd.abbr) or p.allianceAbbr or ""
local alName = (abd and abd.name) or p.allianceName or ""

local ahm = DataCenter and DataCenter.AllianceHelpDataManager
local helpCount = 0
if ahm and ahm.GetHelpNum then
    pcall(function() helpCount = ahm:GetHelpNum() or 0 end)
end

local totalForm = 0
local freeForm = 0
local afm = DataCenter and DataCenter.ArmyFormationDataManager
local wmdm = DataCenter and DataCenter.WorldMarchDataManager
local occupiedForm = {}
local activeMarchCount = 0
local nowSec = os.time()
local underAttack = false
local incomingAttackCount = 0
local ownPointId = tonumber(p.world_main_pos or 0) or 0

if wmdm and wmdm.allMarches then
    for _, m in pairs(wmdm.allMarches) do
        if type(m) == "table" then
            local mUid = tostring(m.uid)
            if mUid == uidStr then
                activeMarchCount = activeMarchCount + 1
                if m.formationId then
                    occupiedForm[tonumber(m.formationId)] = true
                end
            end
            if tostring(m.targetUid) == uidStr and m.marchType and tonumber(m.marchType) == 1 and mUid ~= uidStr then
                if not m.endTime or tonumber(m.endTime) >= nowSec then
                    underAttack = true
                    incomingAttackCount = incomingAttackCount + 1
                end
            end
        end
    end
end

if afm then
    pcall(function()
        if afm.GetUnlockFormationCount then
            totalForm = tonumber(afm:GetUnlockFormationCount()) or 0
        elseif afm.ArmyFormationList then
            for _ in pairs(afm.ArmyFormationList) do totalForm = totalForm + 1 end
        end
        if afm.GetFreeFormationCount then
            freeForm = tonumber(afm:GetFreeFormationCount()) or 0
        elseif afm.GetInMarchArmyFormationCount then
            local inMarch = tonumber(afm:GetInMarchArmyFormationCount()) or 0
            freeForm = math.max(0, totalForm - inMarch)
        else
            freeForm = math.max(0, totalForm - activeMarchCount)
        end
    end)
end

local shieldEnd = 0
pcall(function()
    local mainBuild = bm and BuildingTypes and BuildingTypes.FUN_BUILD_MAIN and bm:GetFunbuildByItemID(BuildingTypes.FUN_BUILD_MAIN)
    local mainUuid = mainBuild and mainBuild.uuid
    local wpm = DataCenter and DataCenter.WorldPointManager
    local bData = mainUuid and wpm and wpm.GetBuildDataByUuid and wpm:GetBuildDataByUuid(mainUuid)
    if bData and bData.extraParam and bData.extraParam.protectEndTime then
        shieldEnd = tonumber(bData.extraParam.protectEndTime) or 0
    end
end)

local app = CS and CS.UnityEngine and CS.UnityEngine.Application
local productName = app and app.productName or ""
local targetFps = app and app.targetFrameRate or 0
local sc = SceneManager and SceneManager.CurrSceneID or 0
local unityTime = CS and CS.UnityEngine and CS.UnityEngine.Time
local udt = unityTime and unityTime.unscaledDeltaTime or 0
local sdt = unityTime and unityTime.smoothDeltaTime or 0
local liveFps = (udt > 0 and udt < math.huge) and math.floor(1.0 / udt + 0.5) or 0
local smoothFps = (sdt > 0 and sdt < math.huge) and math.floor(1.0 / sdt + 0.5) or 0

return _encode_json({
    loggedIn = true,
    productName = tostring(productName),
    uid = uidStr,
    name = tostring(p.name or "Unknown"),
    serverId = tonumber(serverId) or 0,
    selfServerId = tonumber(selfServerId) or tonumber(serverId) or 0,
    hqLevel = tonumber(hqLevel) or 0,
    pointId = ownPointId,
    power = tonumber(playerPower) or 0,
    stamina = tonumber(p.stamina or p.actionPoint or 0) or 0,
    diamond = tonumber(p.gold or ((p.freeGold or 0) + (p.paidGold or 0)) or 0) or 0,
    allianceTag = tostring(alTag or ""),
    allianceName = tostring(alName or ""),
    helpCount = tonumber(helpCount) or 0,
    totalFormations = totalForm,
    freeFormations = freeForm,
    activeMarches = activeMarchCount,
    underAttack = underAttack,
    incomingAttacks = incomingAttackCount,
    shieldEndTime = tonumber(shieldEnd) or 0,
    sceneId = tonumber(sc) or 0,
    fps = liveFps,
    smoothFps = smoothFps,
    fpsCap = tonumber(targetFps) or 0,
    masterPatched = _G._MasterAppliedForThisWorldSession == true
})
"""


def _decode_reg_bytes(val):
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="ignore").rstrip("\x00").strip()
    if isinstance(val, str):
        return val.strip()
    return str(val or "").strip()


def read_readygo_registry():
    """Enumerate all isolated Unity ReadyGo profile subkeys from HKCU."""
    profiles = {}
    base_path = r"Software\ReadyGo"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path) as root_key:
            sub_count = winreg.QueryInfoKey(root_key)[0]
            for i in range(sub_count):
                sub_name = winreg.EnumKey(root_key, i)
                try:
                    with winreg.OpenKey(root_key, sub_name) as sk:
                        val_count = winreg.QueryInfoKey(sk)[1]
                        uid = ""
                        server_id = ""
                        has_token = False
                        custom_uids = 0
                        for j in range(val_count):
                            vname, vdata, _ = winreg.EnumValue(sk, j)
                            if vname.startswith("Setting.GAME_UID"):
                                uid = _decode_reg_bytes(vdata)
                            elif vname.startswith("Setting.SERVER_ID"):
                                server_id = _decode_reg_bytes(vdata)
                            elif vname.startswith("SeToken"):
                                has_token = bool(vdata)
                            elif vname.startswith("Setting.CUSTOM_UID"):
                                custom_uids += 1
                        profiles[sub_name] = {
                            "unity_profile": sub_name,
                            "uid": uid,
                            "server_id": int(server_id) if server_id.isdigit() else 0,
                            "has_token": has_token,
                            "known_uids": custom_uids,
                        }
                except OSError:
                    continue
    except OSError:
        pass
    return profiles


_APP_INFO_CACHE: dict[str, tuple[float, tuple[str, str]]] = _SHARED_STATE["app_info_cache"]
_GAME_VER_CACHE: dict[str, tuple[float, str]] = _SHARED_STATE["game_ver_cache"]
_DISCOVER_CACHE: tuple[float, list[dict[str, Any]]] | None = None
_DISCOVER_CACHE_STATE: dict[str, Any] = _SHARED_STATE["discover"]
_DISCOVER_CACHE_LOCK: threading.Lock = _SHARED_STATE["discover_cache_lock"]
_DISCOVER_CACHE_TTL_SEC = 60.0
_XLUA_CACHE_LOCK: threading.Lock = _SHARED_STATE["xlua_cache_lock"]
_XLUA_LOADED_CACHE: dict[tuple[int, int], bool] = _SHARED_STATE["xlua_loaded_cache"]


def _profiles_stat_sig(path: Path) -> tuple[Any, ...]:
    try:
        st = path.stat()
        return (True, st.st_mtime_ns, st.st_ctime_ns, st.st_size, st.st_ino)
    except FileNotFoundError:
        return (False, 0, 0, 0, 0)
    except OSError:
        return (None, 0, 0, 0, 0)


def invalidate_discovery_cache() -> None:
    """Clear cached client discovery and app-info metadata (call after provisioning/setup)."""
    global _DISCOVER_CACHE, _SHORTCUT_DIRS_CACHE
    with _DISCOVER_CACHE_LOCK:
        _DISCOVER_CACHE_STATE["gen"] += 1
        _DISCOVER_CACHE_STATE["entry"] = None
        _DISCOVER_CACHE = None
        _SHORTCUT_DIRS_CACHE = None
        _SHARED_STATE["shortcut_dirs_cache"] = None
        _APP_INFO_CACHE.clear()
        _GAME_VER_CACHE.clear()


def _read_app_info(game_dir: Path):
    key = str(game_dir).lower()
    now = time.monotonic()
    with _DISCOVER_CACHE_LOCK:
        cached = _APP_INFO_CACHE.get(key)
        if cached is not None and (now - cached[0]) < 120.0:
            return cached[1]
    res = ("", "")
    for data_name in ["Survival_Data", f"{game_dir.name}_Data"]:
        p = game_dir / data_name / "app.info"
        if p.exists():
            lines = [ln.strip() for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
            if len(lines) >= 2:
                res = (lines[0], lines[1])
                break
    if res == ("", ""):
        for sub in game_dir.glob("*_Data"):
            p = sub / "app.info"
            if p.exists():
                lines = [ln.strip() for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
                if len(lines) >= 2:
                    res = (lines[0], lines[1])
                    break
    with _DISCOVER_CACHE_LOCK:
        if len(_APP_INFO_CACHE) > 256:
            _APP_INFO_CACHE.clear()
        _APP_INFO_CACHE[key] = (now, res)
    return res


def _read_game_version(game_dir: Path):
    key = str(game_dir).lower()
    now = time.monotonic()
    with _DISCOVER_CACHE_LOCK:
        cached = _GAME_VER_CACHE.get(key)
        if cached is not None and (now - cached[0]) < 120.0:
            return cached[1]
    vf = game_dir / "config" / "Game_version.txt"
    ver = vf.read_text(encoding="utf-8", errors="ignore").strip() if vf.exists() else ""
    with _DISCOVER_CACHE_LOCK:
        if len(_GAME_VER_CACHE) > 256:
            _GAME_VER_CACHE.clear()
        _GAME_VER_CACHE[key] = (now, ver)
    return ver


def _extract_lnk_candidate_paths(lnk_path: Path) -> set[str]:
    """Extract ASCII and UTF-16LE (even/odd aligned) filesystem paths embedded in a Windows .lnk binary."""
    paths: set[str] = set()
    pat = re.compile(r'([A-Za-z]:\\[^\x00-\x1f"<>?*|\r\n]+)')
    try:
        raw = lnk_path.read_bytes()
    except OSError:
        return paths
    for chunk in (
        raw.decode("latin-1", errors="ignore"),
        raw.decode("utf-16-le", errors="ignore"),
        raw[1:].decode("utf-16-le", errors="ignore"),
    ):
        for match in pat.findall(chunk):
            cleaned = match.strip().rstrip("\"' ")
            if len(cleaned) >= 4:
                paths.add(cleaned)
    return paths


def _scan_shortcut_dirs(force_refresh: bool = False):
    """Find candidate Last Z root folders referenced by desktop or start menu shortcuts without spawning PowerShell."""
    global _SHORTCUT_DIRS_CACHE
    with _DISCOVER_CACHE_LOCK:
        cached_dirs = _SHARED_STATE.get("shortcut_dirs_cache")
        if cached_dirs is not None and not force_refresh:
            return set(cached_dirs)

    dirs = set()
    lnk_dirs = [
        Path(os.path.expandvars(r"%USERPROFILE%\Desktop")),
        Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")),
    ]
    lnk_files = []
    for d in lnk_dirs:
        if d.exists():
            candidates_lnk = list(d.glob("*.lnk"))
            try:
                for sub in d.iterdir():
                    if sub.is_dir():
                        candidates_lnk.extend(sub.glob("*.lnk"))
            except OSError:
                pass
            for f in candidates_lnk:
                fname = f.name.lower()
                if any(k in fname for k in ("last z", "lastz", "farm", "third")) or re.search(r"\balt\d*\b", fname):
                    lnk_files.append(f)
    if not lnk_files:
        with _DISCOVER_CACHE_LOCK:
            _SHORTCUT_DIRS_CACHE = set()
            _SHARED_STATE["shortcut_dirs_cache"] = set()
        return dirs

    for lnk_file in lnk_files:
        for raw_path in _extract_lnk_candidate_paths(lnk_file):
            p = Path(raw_path)
            if p.suffix.lower() in (".vbs", ".ps1") and p.exists():
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                    for m2 in re.findall(r'([A-Za-z]:\\[^"\'\r\n]+)', txt):
                        p2 = Path(m2.strip())
                        if (p2 / "Survival_Data").exists() or p2.name.lower() == "game":
                            dirs.add(p2)
                        elif (p2 / "Game").exists():
                            dirs.add(p2 / "Game")
                except Exception:
                    pass
            cur = p if p.is_dir() else p.parent
            for cand in (cur, cur.parent, cur.parent / "Game"):
                if (cand / "Survival.exe").exists() or (cand / "GameAssembly.dll").exists():
                    dirs.add(cand)

    with _DISCOVER_CACHE_LOCK:
        _SHORTCUT_DIRS_CACHE = set(dirs)
        _SHARED_STATE["shortcut_dirs_cache"] = set(dirs)
    return dirs


def _fixed_drive_letters() -> list[str]:
    """Return available fixed drive letters (C..Z) without stalling on optical/offline drives."""
    letters: list[str] = []
    try:
        if _KERNEL32 is None:
            return list("CDEFG")
        mask = _KERNEL32.GetLogicalDrives()
        for idx in range(2, 26):  # C..Z
            if mask & (1 << idx):
                letter = chr(65 + idx)
                dtype = _KERNEL32.GetDriveTypeW(f"{letter}:\\")
                if dtype in (2, 3):  # DRIVE_REMOVABLE or DRIVE_FIXED
                    letters.append(letter)
    except Exception:
        letters = list("CDEFG")
    return letters or list("CDEFG")


def _scan_uninstall_registry() -> set[Path]:
    """Find Last Z install folders from Windows Uninstall registry entries."""
    found: set[Path] = set()
    reg_roots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, sub in reg_roots:
        try:
            with winreg.OpenKey(hive, sub) as key:
                cnt = winreg.QueryInfoKey(key)[0]
                for i in range(cnt):
                    try:
                        name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, name) as sk:
                            vals = {}
                            for kname in ("DisplayName", "Publisher", "InstallLocation", "DisplayIcon", "UninstallString"):
                                try:
                                    v, _ = winreg.QueryValueEx(sk, kname)
                                    vals[kname] = str(v or "")
                                except OSError:
                                    pass
                            hay = " ".join(vals.values()).lower()
                            if "last z" in hay or "readygo" in hay or "survival.exe" in hay:
                                for raw in (vals.get("InstallLocation", ""), vals.get("DisplayIcon", ""), vals.get("UninstallString", "")):
                                    m = re.search(r'([A-Za-z]:\\[^"\r\n,]+)', raw)
                                    if not m:
                                        continue
                                    p = Path(m.group(1).strip())
                                    base = p if p.is_dir() else p.parent
                                    for cand in (base, base / "Game", base.parent / "Game"):
                                        if (cand / "Survival.exe").exists() or (cand / "GameAssembly.dll").exists():
                                            found.add(cand)
                    except OSError:
                        continue
        except OSError:
            continue
    return found


def _scan_filesystem_roots():
    """Locate any Last Z Game installations on any PC without user-specific hardcoding."""
    candidates = set()
    for base_env in (r"%LOCALAPPDATA%", r"%LOCALAPPDATA%\Programs", r"%USERPROFILE%\Games", r"%PROGRAMFILES%", r"%PROGRAMFILES(X86)%"):
        root_dir = Path(os.path.expandvars(base_env))
        if not root_dir.exists():
            continue
        for sub_name in ("Last Z", "LastZ", "Last Z Survival"):
            cand_game = root_dir / sub_name / "Game"
            if cand_game.exists():
                candidates.add(cand_game)
            elif (root_dir / sub_name / "GameAssembly.dll").exists():
                candidates.add(root_dir / sub_name)

    for drive_letter in _fixed_drive_letters():
        for search_root in (Path(f"{drive_letter}:\\"), Path(f"{drive_letter}:\\Games")):
            if not search_root.exists():
                continue
            try:
                for entry in search_root.iterdir():
                    if not entry.is_dir():
                        continue
                    low = entry.name.lower()
                    if "last z" in low or "lastz" in low:
                        g = entry / "Game"
                        if g.exists():
                            candidates.add(g)
                        elif (entry / "GameAssembly.dll").exists():
                            candidates.add(entry)
            except OSError:
                continue

    for proc in psutil.process_iter(["name", "exe"]):
        try:
            exe = proc.info.get("exe")
            if exe:
                gdir = Path(exe).parent
                if (gdir / "GameAssembly.dll").exists() and ((gdir / "Survival_Data").exists() or (gdir / "Survival.exe").exists()):
                    candidates.add(gdir)
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue

    candidates.update(_scan_uninstall_registry())
    candidates.update(_scan_shortcut_dirs())
    return sorted(candidates, key=lambda p: str(p).lower())


def detect_vanilla_base_install(explicit_path: str | None = None) -> dict:
    """Resolve the primary/vanilla Last Z Game folder on the current PC."""
    cand_dirs: list[Path] = []
    if explicit_path:
        ep = Path(explicit_path.strip().strip('"'))
        for c in (ep, ep / "Game", ep.parent):
            if c.exists() and (c / "Survival.exe").exists():
                cand_dirs.append(c)
                break
    for c in _scan_filesystem_roots():
        if all(not _is_same_target(c, x) for x in cand_dirs):
            cand_dirs.append(c)

    best = None
    best_score = -1
    local_app_low = str(Path(os.path.expandvars(r"%LOCALAPPDATA%"))).lower()
    for gd in cand_dirs:
        if not (gd / "Survival.exe").exists() or not (gd / "GameAssembly.dll").exists():
            continue
        company, prof = _read_app_info(gd)
        if company and company != "ReadyGo":
            continue
        score = 0
        if prof == "LastZ" or not prof:
            score += 50
        if local_app_low in str(gd).lower():
            score += 20
        if (gd.parent / "launcher" / "Launcher.exe").exists() or (gd.parent / "Last Z.exe").exists():
            score += 10
        if score > best_score:
            best_score = score
            best = gd

    if best is None:
        return {"found": False, "game_dir": "", "root_dir": "", "version": "", "unity_profile": ""}

    _, prof = _read_app_info(best)
    return {
        "found": True,
        "game_dir": str(best),
        "root_dir": str(best.parent),
        "version": _read_game_version(best),
        "unity_profile": prof or "LastZ",
        "has_launcher": (best.parent / "launcher" / "Launcher.exe").exists(),
        "has_top_exe": (best.parent / "Last Z.exe").exists(),
    }


def _is_same_target(path_a: Path, path_b: Path):
    try:
        return str(path_a.resolve()).lower() == str(path_b.resolve()).lower()
    except OSError:
        return str(path_a).lower() == str(path_b).lower()


def _detect_primary_exe(game_dir: Path, unity_profile: str):
    exes = [
        p for p in game_dir.glob("*.exe")
        if p.name.lower() not in IGNORE_EXES
    ]
    non_default = [p for p in exes if p.name.lower() != "survival.exe"]
    if unity_profile != "LastZ" and non_default:
        # Prefer custom EXE matching junction or non-Survival.exe name
        for p in non_default:
            if (game_dir / f"{p.stem}_Data").exists():
                return p
        return non_default[0]
    surv = game_dir / "Survival.exe"
    if surv.exists():
        return surv
    return non_default[0] if non_default else None


_IO_LOCK: threading.Lock = _SHARED_STATE["io_lock"]
_PID_LOCKS_GUARD: threading.Lock = _SHARED_STATE["pid_locks_guard"]
_PID_LOCKS: dict[int, threading.Lock] = _SHARED_STATE["pid_locks"]
_SESSION_CACHE_LOCK: threading.Lock = _SHARED_STATE["session_cache_lock"]
_SAVE_PROFILES_ATOMIC = True


def _get_pid_lock(pid: int) -> threading.Lock:
    with _PID_LOCKS_GUARD:
        lock = _PID_LOCKS.get(pid)
        if lock is None:
            lock = threading.Lock()
            _PID_LOCKS[pid] = lock
        return lock


def load_saved_profiles():
    with _IO_LOCK:
        if PROFILES_PATH.exists():
            try:
                data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return {}


def save_profiles(data):
    global _DISCOVER_CACHE
    with _IO_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = PROFILES_PATH.with_name(
            f"{PROFILES_PATH.name}.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp"
        )
        try:
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            for attempt in range(5):
                try:
                    os.replace(tmp, PROFILES_PATH)
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
            with _DISCOVER_CACHE_LOCK:
                _DISCOVER_CACHE_STATE["gen"] += 1
                _DISCOVER_CACHE_STATE["entry"] = None
                _DISCOVER_CACHE = None


def discover_clients(save_cache=True, force_refresh: bool = False):
    """Auto-discover all installed Last Z client instances across drives and Registry (TTL-cached)."""
    global _DISCOVER_CACHE
    profiles_key = os.path.normcase(os.path.abspath(str(PROFILES_PATH)))
    profiles_sig = _profiles_stat_sig(PROFILES_PATH)
    now_mono = time.monotonic()
    with _DISCOVER_CACHE_LOCK:
        cached = _DISCOVER_CACHE_STATE["entry"]
        if (
            not save_cache
            and not force_refresh
            and cached is not None
            and cached[0] == profiles_key
            and cached[1] == profiles_sig
            and (now_mono - cached[2]) < _DISCOVER_CACHE_TTL_SEC
        ):
            return [dict(c) for c in cached[3]]
        scan_gen = _DISCOVER_CACHE_STATE["gen"]
    reg_profiles = read_readygo_registry()
    raw_dirs = _scan_filesystem_roots()
    saved = load_saved_profiles()
    saved_map = {str(item.get("game_dir", "")).lower(): item for item in saved.get("clients", [])}

    # Include any custom saved directories
    for item in saved.get("clients", []):
        gd = Path(item.get("game_dir", ""))
        if gd.exists() and all(not _is_same_target(gd, x) for x in raw_dirs):
            raw_dirs.append(gd)

    # Deduplicate NTFS junctions pointing to the same physical Game directory, preferring %LOCALAPPDATA% path
    deduped = []
    local_app_str = str(Path(os.path.expandvars(r"%LOCALAPPDATA%"))).lower()
    for gd in raw_dirs:
        if not (gd / "Survival.exe").exists() and not any(gd.glob("*.exe")):
            continue
        company, prod = _read_app_info(gd)
        if company and company != "ReadyGo":
            continue
        duplicate_idx = None
        for idx, existing in enumerate(deduped):
            if _is_same_target(gd, existing):
                duplicate_idx = idx
                break
        if duplicate_idx is not None:
            if local_app_str in str(gd).lower():
                deduped[duplicate_idx] = gd
        else:
            deduped.append(gd)

    clients = []
    for gd in deduped:
        _, unity_profile = _read_app_info(gd)
        unity_profile = unity_profile or "LastZ"
        exe_path = _detect_primary_exe(gd, unity_profile)
        if not exe_path:
            continue
        reg = reg_profiles.get(unity_profile, {})
        ver = _read_game_version(gd)

        existing_cfg = saved_map.get(str(gd).lower(), {})
        role = existing_cfg.get("role")
        if not role:
            role = "main" if unity_profile == "LastZ" else "farm"

        label = existing_cfg.get("label")
        if not label:
            if unity_profile == "LastZ":
                label = "Main"
            elif unity_profile == "FarmZ":
                label = "Farm"
            elif unity_profile == "Alt3Z":
                label = "Third"
            else:
                label = unity_profile

        entry = {
            "id": existing_cfg.get("id") or unity_profile.lower(),
            "label": label,
            "role": role,
            "unity_profile": unity_profile,
            "game_dir": str(gd),
            "exe_path": str(exe_path),
            "exe_name": exe_path.name,
            "version": ver,
            "uid": reg.get("uid", ""),
            "server_id": reg.get("server_id", 0),
            "has_token": bool(reg.get("has_token", False)),
            "bot_enabled": existing_cfg.get("bot_enabled", role != "main"),
            "launch_mode": existing_cfg.get("launch_mode", "windowed"),
            "gather_resource": existing_cfg.get("gather_resource", "Any"),
            "gather_level": existing_cfg.get("gather_level", 0),
        }
        clients.append(entry)

    # Sort Main first, then alphabetically
    clients.sort(key=lambda c: (0 if c["role"] == "main" else 1, c["unity_profile"].lower()))

    if save_cache:
        payload = {
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "clients": clients,
        }
        save_profiles(payload)
        with _DISCOVER_CACHE_LOCK:
            post_sig = _profiles_stat_sig(PROFILES_PATH)
            entry = (profiles_key, post_sig, time.monotonic(), [dict(c) for c in clients])
            _DISCOVER_CACHE_STATE["entry"] = entry
            _DISCOVER_CACHE = (entry[2], entry[3])
    else:
        with _DISCOVER_CACHE_LOCK:
            if _DISCOVER_CACHE_STATE["gen"] == scan_gen and _profiles_stat_sig(PROFILES_PATH) == profiles_sig:
                entry = (profiles_key, profiles_sig, time.monotonic(), [dict(c) for c in clients])
                _DISCOVER_CACHE_STATE["entry"] = entry
                _DISCOVER_CACHE = (entry[2], entry[3])
    return [dict(c) for c in clients]


def _resolve_proc_exe(proc) -> str:
    """Safely read executable path from proc.info or lazy proc.exe() only when needed."""
    info = getattr(proc, "info", None)
    if isinstance(info, dict) and "exe" in info:
        return str(info["exe"] or "")
    exe_val = ""
    try:
        exe_val = str(proc.exe() or "")
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError, AttributeError):
        exe_val = ""
    if isinstance(info, dict):
        info["exe"] = exe_val
    return exe_val


def is_lastz_process(proc, known_exe_names: set[str] | None = None):
    """Return True if proc looks like a Last Z game binary (name-first fast filter)."""
    try:
        name = (proc.info.get("name") or "").lower()
        if not name.endswith(".exe") or name in IGNORE_EXES:
            return False
        fast_match = (
            name in ("survival.exe", "farmgame.exe", "alt3game.exe")
            or (known_exe_names is not None and name in known_exe_names)
            or "lastz" in name
            or (name.startswith(("farm", "alt")) and "game" in name)
        )
        if not fast_match:
            return False
        exe = _resolve_proc_exe(proc)
        if exe:
            gdir = Path(exe).parent
            has_ga = (gdir / "GameAssembly.dll").exists()
            has_surv_data = (gdir / "Survival_Data").exists()
            company = ""
            if has_ga:
                company, _ = _read_app_info(gdir)
                if company == "ReadyGo":
                    return True
            if name in ("survival.exe", "farmgame.exe", "alt3game.exe") and has_surv_data:
                return True
            if known_exe_names is not None and name in known_exe_names and has_ga:
                if company == "ReadyGo" or has_surv_data:
                    return True
        elif name in ("survival.exe", "farmgame.exe", "alt3game.exe"):
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
        pass
    return False


def find_running_processes():
    """Return basic info for all running Last Z client processes using name-first filtering."""
    installed = discover_clients(save_cache=False)
    by_exe_path = {c["exe_path"].lower(): c for c in installed}
    by_real_path = {}
    for c in installed:
        try:
            by_real_path[str(Path(c["exe_path"]).resolve()).lower()] = c
        except OSError:
            pass

    known_exe_names = {c["exe_name"].lower(): c for c in installed}
    known_name_set = set(known_exe_names.keys())
    running = []
    # Only request pid+name across all OS processes; fetch .exe lazily only for Last Z candidates (~90x faster).
    for proc in psutil.process_iter(["pid", "name"]):
        if not is_lastz_process(proc, known_exe_names=known_name_set):
            continue
        exe = _resolve_proc_exe(proc)
        cfg = by_exe_path.get(exe.lower()) if exe else None
        if not cfg and exe:
            try:
                cfg = by_real_path.get(str(Path(exe).resolve()).lower())
            except OSError:
                cfg = None
        if not cfg:
            cfg = known_exe_names.get((proc.info.get("name") or "").lower(), {})

        company, unity_profile = ("", cfg.get("unity_profile", ""))
        if exe:
            company, prod = _read_app_info(Path(exe).parent)
            if prod:
                unity_profile = prod

        running.append({
            "pid": proc.info["pid"],
            "exe_name": proc.info.get("name") or "",
            "exe_path": exe,
            "unity_profile": unity_profile or "Unknown",
            "label": cfg.get("label") or Path(proc.info.get("name") or "LastZ").stem,
            "role": cfg.get("role") or ("main" if (proc.info.get("name") or "").lower() == "survival.exe" else "farm"),
            "reg_uid": cfg.get("uid", ""),
            "reg_server_id": cfg.get("server_id", 0),
        })
    running.sort(key=lambda r: (0 if r["role"] == "main" else 1, r["exe_name"].lower(), r["pid"]))
    return running


def _has_module_win32(pid: int, target_dll_lower: str) -> bool | None:
    """Fast Win32 CreateToolhelp32Snapshot module check (avoids full VirtualQueryEx memory_maps scan)."""
    if os.name != "nt" or _KERNEL32 is None or MODULEENTRY32W is None:
        return None
    try:
        pid_i = int(pid)
        if pid_i <= 0:
            return False

        TH32CS_SNAPMODULE = 0x00000008
        TH32CS_SNAPMODULE32 = 0x00000010
        ERROR_BAD_LENGTH = 24
        INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
        target_name = str(target_dll_lower or "").lower()

        snap = None
        for _ in range(5):
            ctypes.set_last_error(0)
            cand = _KERNEL32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid_i)
            if cand and cand != INVALID_HANDLE_VALUE:
                snap = cand
                break
            if ctypes.get_last_error() == ERROR_BAD_LENGTH:
                time.sleep(0.01)
                continue
            return None
        if not snap or snap == INVALID_HANDLE_VALUE:
            return None
        try:
            me = MODULEENTRY32W()
            me.dwSize = ctypes.sizeof(MODULEENTRY32W)
            ok = _KERNEL32.Module32FirstW(snap, ctypes.byref(me))
            while ok:
                if (me.szModule or "").lower() == target_name:
                    return True
                ok = _KERNEL32.Module32NextW(snap, ctypes.byref(me))
            return False
        finally:
            _KERNEL32.CloseHandle(snap)
    except Exception:
        return None


def _xlua_loaded(pid, min_uptime_sec: float = 12.0):
    try:
        pid_i = int(pid)
        if pid_i <= 0:
            return False
        p = psutil.Process(pid_i)
        ctime = p.create_time()
        if min_uptime_sec > 0 and (time.time() - ctime) < min_uptime_sec:
            return False
        cache_key = (pid_i, int(ctime))
        with _XLUA_CACHE_LOCK:
            if _XLUA_LOADED_CACHE.get(cache_key):
                return True
        fast = _has_module_win32(pid_i, "xlua.dll")
        if fast is not None:
            if fast:
                with _XLUA_CACHE_LOCK:
                    if len(_XLUA_LOADED_CACHE) > 64:
                        _XLUA_LOADED_CACHE.clear()
                    _XLUA_LOADED_CACHE[cache_key] = True
            return fast
        for mmap in p.memory_maps():
            if mmap.path.lower().endswith("xlua.dll"):
                with _XLUA_CACHE_LOCK:
                    if len(_XLUA_LOADED_CACHE) > 64:
                        _XLUA_LOADED_CACHE.clear()
                    _XLUA_LOADED_CACHE[cache_key] = True
                return True
        return False
    except Exception:
        return False


class _FridaSessionHolder:
    """Encapsulates a cached Frida session and RPC script for a target PID."""

    def __init__(self, pid: int, session: Any, script: Any):
        self.pid = pid
        self.session = session
        self.script = script
        self.last_used = time.monotonic()
        self.is_valid = True

    def is_alive(self) -> bool:
        if not self.is_valid or self.session is None or self.script is None:
            return False
        try:
            if getattr(self.session, "is_detached", False):
                return False
            return psutil.pid_exists(self.pid)
        except Exception:
            return False

    def close(self) -> None:
        self.is_valid = False
        if self.script is not None:
            try:
                self.script.unload()
            except Exception:
                pass
            self.script = None
        if self.session is not None:
            try:
                self.session.detach()
            except Exception:
                pass
            self.session = None


_CACHED_SESSIONS: dict[int, _FridaSessionHolder] = {}
if _SHARED_STATE["cached_sessions"]:
    _CACHED_SESSIONS = _SHARED_STATE["cached_sessions"]
else:
    _SHARED_STATE["cached_sessions"] = _CACHED_SESSIONS
_LAST_DETACH_TS: dict[int, float] = _SHARED_STATE["last_detach_ts"]


def _make_detached_handler(
    target_pid: int,
    holder_ref: list[_FridaSessionHolder | None] | None = None,
    session_obj: Any = None,
    detached_flag: list[bool] | None = None,
):
    def on_detached(reason, crash):
        if detached_flag is not None:
            detached_flag[0] = True
        expected_holder = holder_ref[0] if holder_ref else None
        evicted: _FridaSessionHolder | None = None
        with _SESSION_CACHE_LOCK:
            cur = _CACHED_SESSIONS.get(target_pid)
            if cur is not None:
                if expected_holder is not None:
                    if cur is expected_holder:
                        evicted = _CACHED_SESSIONS.pop(target_pid, None)
                elif session_obj is not None:
                    if cur.session is session_obj:
                        evicted = _CACHED_SESSIONS.pop(target_pid, None)
                else:
                    evicted = _CACHED_SESSIONS.pop(target_pid, None)
            _LAST_DETACH_TS[target_pid] = time.monotonic()
        if expected_holder is not None:
            expected_holder.is_valid = False
        if evicted is not None and evicted is not expected_holder:
            evicted.is_valid = False
        _prune_dead_pid_caches()

    return on_detached


def close_frida_session(pid: int | None = None) -> None:
    """Explicitly detach and clean up cached Frida session(s)."""
    to_close: list[_FridaSessionHolder] = []
    now_mono = time.monotonic()
    with _SESSION_CACHE_LOCK:
        if pid is not None:
            target_pid = int(pid)
            holder = _CACHED_SESSIONS.pop(target_pid, None)
            if holder is not None:
                _LAST_DETACH_TS[target_pid] = now_mono
                to_close.append(holder)
        else:
            for target_pid, holder in list(_CACHED_SESSIONS.items()):
                _LAST_DETACH_TS[target_pid] = now_mono
                to_close.append(holder)
            _CACHED_SESSIONS.clear()
    for holder in to_close:
        try:
            holder.close()
        except Exception:
            pass
    _prune_dead_pid_caches()


def _prune_dead_pid_caches() -> None:
    """Remove stale dead-PID entries from session/lock/xlua caches to prevent unbounded growth."""
    try:
        with _SESSION_CACHE_LOCK:
            active_pids = set(_CACHED_SESSIONS.keys())
            detach_candidates = [k for k in _LAST_DETACH_TS.keys() if k not in active_pids] if len(_LAST_DETACH_TS) > 32 else []
        with _PID_LOCKS_GUARD:
            lock_candidates = [k for k in _PID_LOCKS.keys() if k not in active_pids] if len(_PID_LOCKS) > 32 else []
        with _XLUA_CACHE_LOCK:
            xlua_candidates = list(_XLUA_LOADED_CACHE.keys()) if len(_XLUA_LOADED_CACHE) > 32 else []

        if not detach_candidates and not lock_candidates and not xlua_candidates:
            return

        pid_alive_cache: dict[int, bool] = {}

        def _is_alive_pid(p: int) -> bool:
            if p not in pid_alive_cache:
                pid_alive_cache[p] = psutil.pid_exists(int(p))
            return pid_alive_cache[p]

        dead_detach = [k for k in detach_candidates if not _is_alive_pid(int(k))]
        dead_locks = [k for k in lock_candidates if not _is_alive_pid(int(k))]
        dead_xlua = [k for k in xlua_candidates if not _is_alive_pid(int(k[0]))]

        if dead_detach:
            with _SESSION_CACHE_LOCK:
                for pid_k in dead_detach:
                    if pid_k not in _CACHED_SESSIONS:
                        _LAST_DETACH_TS.pop(pid_k, None)
        if dead_locks:
            with _SESSION_CACHE_LOCK:
                current_active = set(_CACHED_SESSIONS.keys())
            with _PID_LOCKS_GUARD:
                for pid_k in dead_locks:
                    lock = _PID_LOCKS.get(pid_k)
                    if lock is not None and pid_k not in current_active and not lock.locked():
                        _PID_LOCKS.pop(pid_k, None)
        if dead_xlua:
            with _XLUA_CACHE_LOCK:
                for k in dead_xlua:
                    _XLUA_LOADED_CACHE.pop(k, None)
    except Exception:
        pass


_ATEXIT_REGISTERED = bool(_SHARED_STATE.get("atexit_registered", False))
if not _ATEXIT_REGISTERED:
    _ATEXIT_REGISTERED = True
    _SHARED_STATE["atexit_registered"] = True
    atexit.register(close_frida_session)


def frida_eval_lua(pid: int, lua_code: str, timeout: float = 5.0, retries: int = 3):
    """Execute a read/eval Lua chunk inside a running Last Z process via xlua.dll and return (ok, result_or_err).
    
    Reuses cached Frida sessions to eliminate attach/detach churn and prevent
    VirtualAllocEx 0x00000005 memory allocation collisions.
    """
    if frida is None:
        return False, "Frida package is not installed"

    target_pid = int(pid)
    timeout_ms = int(max(1.0, float(timeout or 5.0)) * 1000)
    last_err = "Unknown error"
    pid_lock = _get_pid_lock(target_pid)

    with pid_lock:
        for attempt in range(retries + 1):
            with _SESSION_CACHE_LOCK:
                holder = _CACHED_SESSIONS.get(target_pid)
            if holder is not None and not holder.is_alive():
                with _SESSION_CACHE_LOCK:
                    if _CACHED_SESSIONS.get(target_pid) is holder:
                        _CACHED_SESSIONS.pop(target_pid, None)
                holder.close()
                holder = None

            # 1. Try to evaluate with existing cached session
            if holder is not None:
                try:
                    res = holder.script.exports_sync.eval_lua(lua_code, timeout_ms)
                    holder.last_used = time.monotonic()
                    if isinstance(res, dict) and res.get("success"):
                        return True, res.get("result", "")
                    last_err = res.get("error", str(res)) if isinstance(res, dict) else str(res)
                    if attempt < retries and "timeout" in last_err.lower():
                        time.sleep(random.uniform(0.35, 0.55) * (attempt + 1))
                        continue
                    return False, last_err
                except Exception as exc:
                    last_err = str(exc)
                    with _SESSION_CACHE_LOCK:
                        if _CACHED_SESSIONS.get(target_pid) is holder:
                            _CACHED_SESSIONS.pop(target_pid, None)
                        _LAST_DETACH_TS[target_pid] = time.monotonic()
                    holder.close()

            # 2. Need to establish a new session - enforce safe attach rate-limiting
            with _SESSION_CACHE_LOCK:
                last_ts = _LAST_DETACH_TS.get(target_pid, 0.0)
            min_gap = random.uniform(0.28, 0.38)
            gap = time.monotonic() - last_ts
            if last_ts > 0.0 and gap < min_gap:
                time.sleep(min_gap - gap)

            new_holder: _FridaSessionHolder | None = None
            try:
                holder_ref: list[_FridaSessionHolder | None] = [None]
                detached_flag = [False]
                session = frida.attach(target_pid)
                session.on(
                    "detached",
                    _make_detached_handler(
                        target_pid,
                        holder_ref=holder_ref,
                        session_obj=session,
                        detached_flag=detached_flag,
                    ),
                )
                script = session.create_script(FRIDA_RPC_JS)
                script.load()

                new_holder = _FridaSessionHolder(target_pid, session, script)
                holder_ref[0] = new_holder
                if detached_flag[0] or getattr(session, "is_detached", False):
                    new_holder.close()
                    raise RuntimeError("Frida session detached during initialization")

                prev_holder = None
                with _SESSION_CACHE_LOCK:
                    prev_holder = _CACHED_SESSIONS.get(target_pid)
                    _CACHED_SESSIONS[target_pid] = new_holder
                if prev_holder is not None and prev_holder is not new_holder:
                    prev_holder.close()

                res = script.exports_sync.eval_lua(lua_code, timeout_ms)
                new_holder.last_used = time.monotonic()
                if isinstance(res, dict) and res.get("success"):
                    return True, res.get("result", "")
                last_err = res.get("error", str(res)) if isinstance(res, dict) else str(res)
                if attempt < retries and "timeout" in last_err.lower():
                    time.sleep(random.uniform(0.35, 0.55) * (attempt + 1))
                    continue
                return False, last_err
            except Exception as e:
                last_err = str(e)
                evicted_holder = None
                with _SESSION_CACHE_LOCK:
                    cur = _CACHED_SESSIONS.get(target_pid)
                    if cur is not None and (new_holder is None or cur is new_holder):
                        evicted_holder = _CACHED_SESSIONS.pop(target_pid, None)
                    _LAST_DETACH_TS[target_pid] = time.monotonic()
                if evicted_holder is not None:
                    evicted_holder.close()
                elif new_holder is not None:
                    new_holder.close()
                if attempt < retries:
                    # Exponential backoff to avoid colliding with VirtualAllocEx
                    time.sleep(random.uniform(0.40, 0.70) * (attempt + 1))

    return False, last_err


def resolve_target_pid(pid=None, profile=None):
    """Resolve explicit PID, LASTZ_TARGET_PID env var, profile name, or first running client."""
    if pid is not None:
        return int(pid)
    env_pid = os.environ.get("LASTZ_TARGET_PID", "").strip()
    if env_pid.isdigit():
        return int(env_pid)
    running = find_running_processes()
    if profile:
        prof_low = profile.lower()
        for r in running:
            if r["unity_profile"].lower() == prof_low or r["label"].lower() == prof_low or r["exe_name"].lower() == prof_low:
                return r["pid"]
    if running:
        return running[0]["pid"]
    return None


def discover_running_clients(query_lua=True):
    """Discover all running Last Z processes with optional live in-game Lua state."""
    running = find_running_processes()
    if not query_lua:
        return running

    enriched = []
    for r in running:
        item = dict(r)
        if not _xlua_loaded(r["pid"]):
            item["loggedIn"] = False
            item["statusText"] = "Booting (xlua pending)"
            enriched.append(item)
            continue

        ok, out = frida_eval_lua(r["pid"], LUA_QUICK_STATUS)
        if ok:
            try:
                data = json.loads(out)
                item.update(data)
                if data.get("loggedIn"):
                    home_srv = data.get("selfServerId") or data.get("serverId")
                    item["statusText"] = f"[{data.get('allianceTag') or '-'}] {data.get('name')} (#{home_srv})"
                else:
                    item["statusText"] = "Loading / Login Screen"
            except Exception as e:
                item["loggedIn"] = False
                item["statusText"] = f"Parse error: {e}"
        else:
            item["loggedIn"] = False
            item["statusText"] = f"Lua unavailable: {out}"
        enriched.append(item)
    return enriched


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    if mode == "installed":
        print(json.dumps(discover_clients(), indent=2, ensure_ascii=False))
    elif mode == "running":
        print(json.dumps(discover_running_clients(query_lua=True), indent=2, ensure_ascii=False))
    else:
        print(json.dumps({
            "installed": discover_clients(),
            "running": discover_running_clients(query_lua="--quick" not in sys.argv),
        }, indent=2, ensure_ascii=False))
else:
    _self_mod = sys.modules.get(__name__)
    if _self_mod is not None:
        sys.modules.setdefault(_SINGLETON_MODULE_KEY, _self_mod)
