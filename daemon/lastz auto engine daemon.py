import importlib.util
import os
import sys
import time
import psutil
from datetime import datetime

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_ENV_DATA_DIR = os.environ.get("HEINZ_DATA_DIR", "").strip()
LOG_FILE = (
    os.path.join(_ENV_DATA_DIR, "logs", "lastz_auto_engine.log")
    if _ENV_DATA_DIR
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "lastz_auto_engine.log")
)


_LOG_DIR_READY = False
_CLIENT_DISCOVERY_MOD = None
_LIVE_TRANSLATOR_MOD = None
_SYNC_FARM_CLIENTS_MOD = None


def _load_sync_farm_clients():
    """Load tools/sync farm clients.py cleanly for periodic Farm launcher auto-heal guard (non-fatal)."""
    global _SYNC_FARM_CLIENTS_MOD
    if _SYNC_FARM_CLIENTS_MOD is not None:
        return _SYNC_FARM_CLIENTS_MOD
    try:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sfc_path = os.path.join(repo_root, "tools", "sync farm clients.py")
        if not os.path.isfile(sfc_path):
            return None
        spec = importlib.util.spec_from_file_location("daemon_sync_farm_clients", sfc_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SYNC_FARM_CLIENTS_MOD = mod
        return mod
    except Exception as exc:
        log(f"[!] Farm launcher auto-heal module unavailable (non-fatal): {exc}")
        return None


def run_farm_launcher_guard(sfc_mod=None):
    """Run Farm launcher auto-heal guard quietly; log only when files are restored, backed up, or warned."""
    mod = sfc_mod if sfc_mod is not None else _load_sync_farm_clients()
    if mod is None or not hasattr(mod, "heal_all_farm_launchers"):
        return None
    try:
        rep = mod.heal_all_farm_launchers(dry_run=False, force=False)
        if not isinstance(rep, dict):
            return None
        if rep.get("healed_count", 0) > 0 or rep.get("failed_count", 0) > 0:
            details = "; ".join(
                str(r.get("message") or "")
                for r in (rep.get("results") or [])
                if r.get("healed") or not r.get("ok")
            )
            log(f"[+] Farm Launcher Auto-Heal Guard: {rep.get('summary')} ({details})")
        elif rep.get("backed_up_count", 0) > 0:
            log(f"[+] Farm Launcher Auto-Heal Guard: {rep.get('summary')}")
        return rep
    except Exception as exc:
        log(f"[!] Farm Launcher Auto-Heal Guard skipped (non-fatal): {exc}")
        return None


def log(msg):
    global _LOG_DIR_READY
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    try:
        if not _LOG_DIR_READY:
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            _LOG_DIR_READY = True
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def _load_master_engine_module():
    master_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apply widescreen smooth map.py")
    spec = importlib.util.spec_from_file_location("lastz_master_engine", master_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load master engine script at {master_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_MASTER_MOD = _load_master_engine_module()
MASTER_LUA_CODE = _MASTER_MOD.MASTER_LUA_CODE
FRIDA_JS = _MASTER_MOD.FRIDA_JS
PRELOAD_TRIGGER_LUA = getattr(
    _MASTER_MOD,
    "PRELOAD_TRIGGER_LUA",
    r"""
if _G.WarmReadOnlyEngineCaches then
    return _G.WarmReadOnlyEngineCaches({ role = "__ROLE__" })
end
if _G._FarmEcoMode then
    return "SKIPPED:farm_eco_mode"
end
return "PRELOAD_HOOK_NOT_INSTALLED"
""",
)


def _load_client_discovery():
    global _CLIENT_DISCOVERY_MOD
    if _CLIENT_DISCOVERY_MOD is not None:
        return _CLIENT_DISCOVERY_MOD
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cd_path = os.path.join(repo_root, "tools", "client discovery.py")
    spec = importlib.util.spec_from_file_location("client_discovery", cd_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load client discovery script at {cd_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _CLIENT_DISCOVERY_MOD = mod
    return mod


def _load_live_translator():
    """Load tools/live translator server.py cleanly (non-fatal if missing)."""
    global _LIVE_TRANSLATOR_MOD
    if _LIVE_TRANSLATOR_MOD is not None:
        return _LIVE_TRANSLATOR_MOD
    try:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tr_path = os.path.join(repo_root, "tools", "live translator server.py")
        if not os.path.isfile(tr_path):
            return None
        spec = importlib.util.spec_from_file_location("live_translator_server", tr_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _LIVE_TRANSLATOR_MOD = mod
        return mod
    except Exception as exc:
        log(f"[!] Live translator module unavailable (non-fatal): {exc}")
        return None


def sync_translator_hook(cd, pid, tr_mod, port, cfg):
    """Inject or update the idempotent live translator Lua hook on a running Last Z client."""
    try:
        disc = cd if cd is not None else _load_client_discovery()
        if hasattr(disc, "_xlua_loaded") and not disc._xlua_loaded(pid):
            return False, "BOOTING_WAIT"
        lua_hook = tr_mod.build_translator_lua_hook(
            port=int(port),
            enabled=bool(cfg.get("enabled", True)),
            target_lang=str(cfg.get("target_lang") or "auto"),
            auto_translate_chat=bool(cfg.get("auto_translate_chat", True)),
        )
        ok, res = disc.frida_eval_lua(pid, lua_hook, timeout=5.0, retries=0)
        return ok, (res or "").strip() if ok else res
    except Exception as e:
        return False, str(e)


def attempt_patch(pid, cd=None):
    try:
        env_data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip()
        cache_dir = (
            os.path.join(env_data_dir, "cache")
            if env_data_dir
            else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache")
        )
        os.makedirs(cache_dir, exist_ok=True)
    except Exception:
        pass

    try:
        psutil.Process(pid).nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception:
        pass

    try:
        disc = cd if cd is not None else _load_client_discovery()
        if not disc._xlua_loaded(pid):
            return False, "BOOTING_WAIT"
        payload = MASTER_LUA_CODE.replace("__FORCE_FULL_LOAD_FLAG__", "false")
        ok, res = disc.frida_eval_lua(pid, payload, timeout=10.0, retries=1)
        if not ok:
            return False, res
        detail = (res or "").strip() or "SUCCESS_SCHEDULED_MAIN_THREAD_V8"
        return True, detail
    except Exception as e:
        return False, str(e)


def trigger_readonly_preload(cd, pid, role="main"):
    """Trigger R3 strictly read-only cache warm-up via lightweight Lua hook."""
    try:
        disc = cd if cd is not None else _load_client_discovery()
        if hasattr(disc, "_xlua_loaded") and not disc._xlua_loaded(pid):
            return False, "BOOTING_WAIT"
        safe_role = "farm" if str(role).lower() == "farm" else "main"
        lua = PRELOAD_TRIGGER_LUA.replace("__ROLE__", safe_role)
        ok, res = disc.frida_eval_lua(pid, lua, timeout=5.0, retries=0)
        return ok, (res or "").strip() if ok else res
    except Exception as e:
        return False, str(e)


FARM_ECO_LUA_PATCH = r"""
if not DataCenter or not LuaEntry or not LuaEntry.Player then
    return "BOOTING_WAIT"
end
local uid = tostring(LuaEntry.Player.uid or "")
if uid == "" or uid == "0" then
    return "BOOTING_WAIT"
end

local unity = CS and CS.UnityEngine
local app = unity and unity.Application
local qs = unity and unity.QualitySettings
local scr = unity and unity.Screen
local shadowDisable = unity and unity.ShadowQuality and unity.ShadowQuality.Disable
local tm = TimerManager and TimerManager:GetInstance()

local lastTargetFps = nil
local lastFocused = nil
local lastWidth = nil
local lastScene = nil
local perfInitApplied = false

local function computeFarmTargetFps()
    if not app then return 60, false, 0 end
    local focused = (app.isFocused == true)
    local w = scr and scr.width or 1280
    if focused then
        return 120, true, w
    end
    if w > 0 and w <= 720 then
        return 15, false, w
    end
    return 30, false, w
end

local function applyFarmPerfSettings(targetFps)
    if app then
        if app.targetFrameRate ~= targetFps then
            app.targetFrameRate = targetFps
        end
        if app.runInBackground ~= true then
            app.runInBackground = true
        end
    end
    if qs and not perfInitApplied then
        if qs.vSyncCount ~= 0 then qs.vSyncCount = 0 end
        if shadowDisable and qs.shadows ~= shadowDisable then
            qs.shadows = shadowDisable
        end
        if qs.antiAliasing ~= 0 then qs.antiAliasing = 0 end
        if qs.softParticles ~= false then qs.softParticles = false end
        if qs.realtimeReflectionProbes ~= false then qs.realtimeReflectionProbes = false end
        perfInitApplied = true
    end
end

local initFps, initFocused, initWidth = computeFarmTargetFps()
lastTargetFps = initFps
lastFocused = initFocused
lastWidth = initWidth
lastScene = SceneManager and SceneManager.CurrSceneID
pcall(applyFarmPerfSettings, initFps)

_G._MasterAppliedForThisWorldSession = true
_G._FarmEcoMode = true

local ecoToken = (_G._farmEcoToken or 0) + 1
_G._farmEcoToken = ecoToken
local ecoBeatCount = 0

local function _doFarmAllianceHelp()
    local ah = DataCenter and DataCenter.AllianceHelpDataManager
    if ah and ah.GetHelpNum and ah:GetHelpNum() > 0 then
        if SFSNetwork and MsgDefines and MsgDefines.AlHelpAll then
            SFSNetwork.SendMessage(MsgDefines.AlHelpAll)
        elseif ah.TryAutoHelp then
            ah:TryAutoHelp()
        end
    end
end

local function _ecoTickWork()
    local tfps, focused, w = computeFarmTargetFps()
    local curScene = SceneManager and SceneManager.CurrSceneID
    if curScene ~= lastScene then
        lastScene = curScene
        perfInitApplied = false
    end
    local fpsDrifted = (app ~= nil and app.targetFrameRate ~= tfps)
    if fpsDrifted or tfps ~= lastTargetFps or focused ~= lastFocused or w ~= lastWidth or not perfInitApplied then
        lastTargetFps = tfps
        lastFocused = focused
        lastWidth = w
        applyFarmPerfSettings(tfps)
    end
    if (ecoBeatCount % 5) == 0 then
        _doFarmAllianceHelp()
        collectgarbage("step", 24)
    end
end

if tm then
    local function ecoBeat()
        if _G._farmEcoToken ~= ecoToken then return end
        ecoBeatCount = ecoBeatCount + 1
        pcall(_ecoTickWork)
        tm:DelayInvoke(ecoBeat, 1.0)
    end
    tm:DelayInvoke(ecoBeat, 1.0)
end

return "SUCCESS_FARM_SMART_FPS_" .. tostring(initFps)
"""


def attempt_farm_eco_patch(cd, pid):
    """Apply responsive smart-FPS eco/smooth patch and passive help loop to a farm or alt client."""
    try:
        if not cd._xlua_loaded(pid):
            return False, "BOOTING_WAIT"
        ok, res = cd.frida_eval_lua(pid, FARM_ECO_LUA_PATCH, timeout=8.0, retries=1)
        if not ok:
            return False, res
        return True, res.strip() or "SUCCESS_FARM_SMART_FPS"
    except Exception as e:
        return False, str(e)


def _parse_parent_pid() -> int:
    for idx, arg in enumerate(sys.argv):
        if arg == "--parent-pid" and idx + 1 < len(sys.argv):
            try:
                return int(sys.argv[idx + 1])
            except ValueError:
                return 0
        if arg.startswith("--parent-pid="):
            try:
                return int(arg.split("=", 1)[1])
            except ValueError:
                return 0
    return 0


def _is_live_daemon_process(pid: int) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    if not psutil.pid_exists(pid):
        return False
    try:
        p = psutil.Process(pid)
        if not p.is_running() or p.status() == psutil.STATUS_ZOMBIE:
            return False
        try:
            cmd = " ".join(p.cmdline() or []).lower()
        except psutil.AccessDenied:
            try:
                pname = (p.name() or "").lower()
                return ("python" in pname) or ("heinz" in pname)
            except Exception:
                return True
        return ("lastz auto engine daemon" in cmd) or ("lastz_auto_engine_daemon" in cmd)
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False
    except Exception:
        return False


def _capture_parent_create_time(parent_pid: int) -> tuple[bool, float | None]:
    """Capture (alive, create_time) for parent_pid at startup to defeat Windows PID reuse."""
    if parent_pid <= 0:
        return True, None
    try:
        p = psutil.Process(parent_pid)
        if not p.is_running() or p.status() == psutil.STATUS_ZOMBIE:
            return False, None
        return True, float(p.create_time())
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False, None
    except psutil.AccessDenied:
        return psutil.pid_exists(parent_pid), None
    except Exception:
        return psutil.pid_exists(parent_pid), None


def _is_parent_alive(parent_pid: int, expected_create_time: float | None) -> bool:
    """Verify parent_pid is still the exact same process instance (matching PID and create_time)."""
    if parent_pid <= 0:
        return True
    if not psutil.pid_exists(parent_pid):
        return False
    try:
        p = psutil.Process(parent_pid)
        if not p.is_running() or p.status() == psutil.STATUS_ZOMBIE:
            return False
        if expected_create_time is not None:
            cur_ct = float(p.create_time())
            if abs(cur_ct - expected_create_time) > 0.01:
                return False
        return True
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False
    except psutil.AccessDenied:
        return psutil.pid_exists(parent_pid)
    except Exception:
        return psutil.pid_exists(parent_pid)


def _acquire_daemon_pid_lock(lock_path: str | None = None) -> str | None:
    """Atomically acquire the daemon PID lockfile with stale-PID cleanup retry.

    Returns the acquired lock_path on success, or None if another daemon holds the
    lock or the lock cannot be acquired safely (never falls through unlocked).
    """
    if not lock_path:
        lock_dir = os.path.dirname(LOG_FILE)
        lock_path = os.path.join(lock_dir, "lastz_auto_engine.pid")
    else:
        lock_dir = os.path.dirname(os.path.abspath(lock_path))

    try:
        os.makedirs(lock_dir, exist_ok=True)
    except OSError:
        return None

    for attempt in range(5):
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raw = ""
            file_age = 0.0
            try:
                file_age = max(0.0, time.time() - os.path.getmtime(lock_path))
            except OSError:
                file_age = 0.0
            try:
                with open(lock_path, "r", encoding="utf-8") as fh:
                    raw = fh.read().strip()
            except FileNotFoundError:
                continue
            except OSError:
                if attempt < 4:
                    time.sleep(0.05)
                    continue
                return None

            if not raw:
                # Creator may still be flushing its PID; wait briefly before treating empty file as stale.
                if attempt < 3 and file_age < 2.0:
                    time.sleep(0.05)
                    continue
                try:
                    os.remove(lock_path)
                except FileNotFoundError:
                    pass
                except OSError:
                    if attempt < 4:
                        time.sleep(0.05)
                        continue
                    return None
                continue

            try:
                old_pid = int(raw.splitlines()[0].strip())
            except ValueError:
                old_pid = 0

            if old_pid > 0 and _is_live_daemon_process(old_pid):
                return None

            try:
                os.remove(lock_path)
            except FileNotFoundError:
                pass
            except OSError:
                if attempt < 4:
                    time.sleep(0.05)
                    continue
                return None
            continue
        except OSError:
            if attempt < 4:
                time.sleep(0.05)
                continue
            return None

        fh = None
        try:
            fh = os.fdopen(fd, "w", encoding="utf-8")
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                os.remove(lock_path)
            except OSError:
                pass
            return None

        try:
            with fh:
                fh.write(str(os.getpid()))
                fh.flush()
            return lock_path
        except Exception:
            try:
                os.remove(lock_path)
            except OSError:
                pass
            return None

    return None


def main():
    once = "--once" in sys.argv
    parent_pid = _parse_parent_pid()
    parent_alive_at_start, parent_create_time = _capture_parent_create_time(parent_pid)
    if parent_pid > 0 and not parent_alive_at_start:
        log(f"- Parent Hub (PID {parent_pid}) already exited before watcher startup; exiting cleanly. -")
        return

    lock_path = None
    if not once:
        lock_path = _acquire_daemon_pid_lock()
        if not lock_path:
            log("- Another auto-engine watcher daemon is already active (or PID lock unavailable); exiting duplicate instance. -")
            return

    cd = _load_client_discovery()
    tr_mod = _load_live_translator()
    translator_port = 0
    translator_started_here = False
    if tr_mod is not None:
        try:
            tr_info = tr_mod.ensure_server_running()
            if tr_info and tr_info.get("running"):
                translator_port = int(tr_info.get("port") or 18765)
                translator_started_here = not bool(tr_info.get("external", False))
                log(f"[+] Live Translator bridge ready on http://127.0.0.1:{translator_port}/client.php")
        except Exception as tr_exc:
            log(f"[!] Live Translator server startup skipped (non-fatal): {tr_exc}")

    log("- Last Z multi-client auto-engine watcher daemon (v8.1) -")
    log("- Monitoring for Main and Farm/Alt Last Z launches (adaptive idle sleep) -")

    sfc_mod = _load_sync_farm_clients()
    if sfc_mod is not None:
        run_farm_launcher_guard(sfc_mod)
    last_launcher_guard_at = time.monotonic()
    launcher_guard_interval_sec = 300.0

    patched_pids = {}
    preload_state = {}
    translator_hook_sig = {}
    translator_retry_after = {}
    idle_since = time.monotonic()

    try:
        while True:
            try:
                if parent_pid > 0 and not _is_parent_alive(parent_pid, parent_create_time):
                    log(f"- Parent Hub (PID {parent_pid}) exited; stopping watcher daemon cleanly. -")
                    break

                procs = cd.find_running_processes()
                current_map = {p["pid"]: p for p in procs}
                current_pids = set(current_map.keys())

                dead_pids = set(patched_pids.keys()) - current_pids
                for dp in dead_pids:
                    info = patched_pids.pop(dp, {})
                    preload_state.pop(dp, None)
                    translator_hook_sig.pop(dp, None)
                    translator_retry_after.pop(dp, None)
                    log(f"[-] {info.get('exe_name', 'Client')} (PID {dp}) terminated. Resetting monitor state.")

                has_pending = False
                for pid, pinfo in current_map.items():
                    if pid not in patched_pids:
                        has_pending = True
                        if not cd._xlua_loaded(pid):
                            continue
                        role = pinfo.get("role", "farm")
                        exe_name = pinfo.get("exe_name", "Client")
                        label = pinfo.get("label", exe_name)
                        time.sleep(0.5)
                        if role == "main":
                            ok, detail = attempt_patch(pid, cd=cd)
                        else:
                            ok, detail = attempt_farm_eco_patch(cd, pid)
                        if ok and detail != "BOOTING_WAIT":
                            mode_tag = "Master Overhaul v8.0" if role == "main" else "Farm Smart Engine (120/30/15 FPS)"
                            log(f"[+] {mode_tag} attached to {label} ({exe_name}, PID {pid})")
                            log(f"    Mode: {detail}")
                            patched_pids[pid] = pinfo
                            if role == "main" and not once:
                                preload_state[pid] = {"done": False, "attempts": 0, "next_at": time.monotonic() + 25.0}
                        else:
                            time.sleep(0.5)

                if tr_mod is not None:
                    try:
                        tr_info = tr_mod.ensure_server_running()
                        if tr_info and tr_info.get("running"):
                            translator_port = int(tr_info.get("port") or translator_port or 18765)
                            if not tr_info.get("external", False):
                                translator_started_here = True
                        if translator_port > 0 and patched_pids:
                            tr_cfg = tr_mod.load_translator_config()
                            tr_enabled = bool(tr_cfg.get("enabled", True))
                            tr_sig = (
                                translator_port,
                                tr_enabled,
                                str(tr_cfg.get("target_lang") or "auto"),
                                bool(tr_cfg.get("auto_translate_chat", True)),
                            )
                            now_tr = time.monotonic()
                            for pid, pinfo in list(patched_pids.items()):
                                if pid not in current_pids:
                                    continue
                                prev_sig = translator_hook_sig.get(pid)
                                if prev_sig == tr_sig:
                                    continue
                                if not tr_enabled and prev_sig is None:
                                    continue
                                if now_tr < translator_retry_after.get(pid, 0.0):
                                    continue
                                ok_tr, res_tr = sync_translator_hook(cd, pid, tr_mod, translator_port, tr_cfg)
                                if ok_tr and res_tr != "BOOTING_WAIT":
                                    translator_hook_sig[pid] = tr_sig
                                    translator_retry_after.pop(pid, None)
                                    lbl = pinfo.get("label", pinfo.get("exe_name", "Client"))
                                    log(f"[+] Live Translator hook synced on {lbl} (PID {pid}): {res_tr}")
                                else:
                                    translator_retry_after[pid] = now_tr + 5.0
                    except Exception:
                        pass

                if not once and preload_state:
                    now_mono = time.monotonic()
                    for pid, pst in list(preload_state.items()):
                        if pid not in current_pids or pst["done"] or now_mono < pst["next_at"]:
                            continue
                        ok_p, res_p = trigger_readonly_preload(cd, pid, role="main")
                        res_str = str(res_p or "").strip()
                        if ok_p and res_str in ("ALREADY_DONE", "SKIPPED:farm_eco_mode", "PRELOAD_HOOK_NOT_INSTALLED"):
                            pst["done"] = True
                            if res_str == "ALREADY_DONE":
                                log(f"[+] R3 read-only preload confirmed complete for PID {pid}")
                        elif ok_p and (res_str == "IN_PROGRESS" or res_str.startswith("WARMUP_SCHEDULED")):
                            pst["attempts"] += 1
                            if res_str.startswith("WARMUP_SCHEDULED"):
                                log(f"[+] R3 read-only preload fallback scheduled for PID {pid}: {res_str}")
                            pst["done"] = pst["attempts"] >= 10
                            pst["next_at"] = now_mono + 10.0
                        else:
                            pst["attempts"] += 1
                            pst["done"] = pst["attempts"] >= 10
                            pst["next_at"] = now_mono + 30.0

                if not once and sfc_mod is not None:
                    now_guard = time.monotonic()
                    if (now_guard - last_launcher_guard_at) >= launcher_guard_interval_sec:
                        last_launcher_guard_at = now_guard
                        run_farm_launcher_guard(sfc_mod)

                if once:
                    break

                # Adaptive polling cadence: fast when booting (1.5s), steady when clients running (3.0s), deep idle when 0 clients (5.0s)
                if current_pids:
                    idle_since = time.monotonic()
                    sleep_sec = 1.5 if has_pending else 3.0
                else:
                    sleep_sec = 5.0 if (time.monotonic() - idle_since) >= 15.0 else 2.5
                time.sleep(sleep_sec)
            except Exception:
                if once:
                    break
                time.sleep(3.0)
    finally:
        if tr_mod is not None and translator_started_here:
            try:
                tr_mod.stop_server()
            except Exception:
                pass
        if lock_path and os.path.exists(lock_path):
            try:
                with open(lock_path, "r", encoding="utf-8") as fh:
                    cur = fh.read().strip()
                if cur == str(os.getpid()):
                    os.remove(lock_path)
            except Exception:
                pass


if __name__ == "__main__":
    main()
