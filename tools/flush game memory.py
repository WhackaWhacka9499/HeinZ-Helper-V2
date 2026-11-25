import argparse
import importlib.util
import os
import sys
import threading
import psutil

_CLIENT_DISCOVERY_MOD = None
_CD_LOAD_LOCK = threading.Lock()
_CANONICAL_CD_MOD = "heinz_client_discovery_singleton"

LUA = r"""
local beforeMem = collectgarbage("count")

collectgarbage("collect")

pcall(function()
    CS.System.GC.Collect()
    CS.UnityEngine.Resources.UnloadUnusedAssets()
end)

local afterMem = collectgarbage("count")
return string.format("Lua Heap: %.2f MB -> %.2f MB (Freed: %.2f MB)", beforeMem / 1024.0, afterMem / 1024.0, (beforeMem - afterMem) / 1024.0)
"""


def _load_client_discovery():
    global _CLIENT_DISCOVERY_MOD
    with _CD_LOAD_LOCK:
        if _CLIENT_DISCOVERY_MOD is not None:
            return _CLIENT_DISCOVERY_MOD
        existing = sys.modules.get(_CANONICAL_CD_MOD)
        if existing is not None:
            _CLIENT_DISCOVERY_MOD = existing
            return existing
        disc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client discovery.py")
        if not os.path.exists(disc):
            return None
        spec = importlib.util.spec_from_file_location("client_discovery", disc)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules.setdefault(_CANONICAL_CD_MOD, mod)
        _CLIENT_DISCOVERY_MOD = sys.modules[_CANONICAL_CD_MOD]
        return _CLIENT_DISCOVERY_MOD


def _resolve_pid(pid=None):
    if pid is not None:
        return int(pid)
    env_pid = os.environ.get("LASTZ_TARGET_PID", "").strip()
    if env_pid.isdigit():
        return int(env_pid)
    try:
        mod = _load_client_discovery()
        if mod is not None:
            resolved = mod.resolve_target_pid()
            if resolved:
                return resolved
    except Exception:
        pass
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and p.info['name'].lower() in ('survival.exe', 'farmgame.exe', 'alt3game.exe'):
            return p.info['pid']
    return None


def flush_memory(pid=None):
    target_pid = _resolve_pid(pid)
    if target_pid is None:
        return "No Last Z client running"

    target_pid = int(target_pid)
    if target_pid <= 0 or not psutil.pid_exists(target_pid):
        return f"Error: target PID {target_pid} is not running"

    cd = _load_client_discovery()
    if cd is None:
        return "Error: client discovery module unavailable"
    if hasattr(cd, "_xlua_loaded") and not cd._xlua_loaded(target_pid):
        return "Error: Last Z client is still booting (xlua.dll not loaded)"
    # Keep total Frida call budget under the 15s subprocess timeout used by Hub/app callers
    ok, res = cd.frida_eval_lua(target_pid, LUA, timeout=6.0, retries=1)
    if not ok:
        return f"Error: {res}"
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flush Lua and Unity memory on a Last Z client.")
    parser.add_argument("--pid", type=int, default=None, help="Target process PID")
    args = parser.parse_args()
    out = flush_memory(pid=args.pid)
    print(out)
    if isinstance(out, str) and out.startswith("Error:"):
        sys.exit(1)
