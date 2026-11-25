import argparse
import os
import sys
import frida
import json
import time

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _resolve_pid(explicit_pid=None):
    if explicit_pid is not None:
        return int(explicit_pid)
    env_pid = os.environ.get("LASTZ_TARGET_PID", "").strip()
    if env_pid.isdigit():
        return int(env_pid)
    try:
        import importlib.util
        disc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "client discovery.py")
        if os.path.exists(disc):
            spec = importlib.util.spec_from_file_location("client_discovery", disc)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            p = mod.resolve_target_pid()
            if p:
                return p
    except Exception:
        pass
    import psutil
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() in ("survival.exe", "farmgame.exe", "alt3game.exe"):
            return proc.info["pid"]
    return None


LUA = r"""
local ahm = DataCenter and DataCenter.AllianceHelpDataManager
if not ahm then return "[-] AllianceHelpDataManager not found" end

local beforeNum = ahm:GetHelpNum()
local beforePoint = ahm:GetTodayHelpPoint()

local ok, err = pcall(ahm.OnHelpAll, ahm)

local afterNum = ahm:GetHelpNum()
local afterPoint = ahm:GetTodayHelpPoint()

return string.format("Helped: %s (helpNum: %d -> %d, points: %d -> %d)", tostring(ok), beforeNum, afterNum, beforePoint, afterPoint)
"""

FRIDA_JS = r"""
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const length = Memory.alloc(8);

function getString(L, index) {
    const p = str(L, index, length);
    const sz = Number(length.readU64());
    return sz === 0 ? '' : p.readUtf8String(sz);
}

const luaPayload = %s;

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        done = true;
        const L = args[0];
        const saved = top(L);
        try {
            const s = Memory.allocUtf8String(luaPayload);
            const loadErr = loadstring(L, s);
            if (loadErr === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const ret = getString(L, -1);
                    send({ type: 'result', data: ret });
                } else {
                    const err = getString(L, -1);
                    send({ type: 'error', data: err });
                }
            } else {
                const syntaxErr = getString(L, -1);
                send({ type: 'error', data: 'Syntax error: ' + syntaxErr });
            }
        } catch(e) {
            send({ type: 'error', data: e.toString() });
        } finally {
            settop(L, saved);
        }
    }
});
""" % json.dumps(LUA)


def trigger_help(pid=None):
    target_pid = _resolve_pid(pid)
    if not target_pid:
        return "No running Last Z client found"
    session = frida.attach(target_pid)
    script = session.create_script(FRIDA_JS)
    res = []

    def on_msg(m, d):
        res.append(m)

    script.on('message', on_msg)
    script.load()
    for _ in range(30):
        if res:
            break
        time.sleep(0.1)
    session.detach()
    if res:
        payload = res[0].get('payload', {})
        return payload.get('data') or str(res[0])
    return "No response received within timeout"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger alliance help all on a Last Z client.")
    parser.add_argument("--pid", type=int, default=None, help="Target process PID")
    args = parser.parse_args()
    print(trigger_help(pid=args.pid))
