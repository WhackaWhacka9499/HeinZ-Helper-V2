import frida
import json
import time

LUA = r"""
local out = {}
table.insert(out, "=== INSPECTING NETWORK CALLERS ===")

if NetworkHelper then
    table.insert(out, "NetworkHelper methods:")
    for k, v in pairs(NetworkHelper) do
        if type(v) == "function" then
            table.insert(out, "  function NetworkHelper." .. tostring(k))
        end
    end
end

if SFSNetwork then
    table.insert(out, "SFSNetwork methods:")
    for k, v in pairs(SFSNetwork) do
        if type(v) == "function" then
            table.insert(out, "  function SFSNetwork." .. tostring(k))
        end
    end
end

if SocketManager then
    table.insert(out, "SocketManager methods:")
    for k, v in pairs(SocketManager) do
        if type(v) == "function" then
            table.insert(out, "  function SocketManager." .. tostring(k))
        end
    end
end

return table.concat(out, "\n")
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

session = frida.attach(4992)
script = session.create_script(FRIDA_JS)
res = []
def on_msg(m, d):
    res.append(m)
script.on('message', on_msg)
script.load()
for _ in range(30):
    if res: break
    time.sleep(0.1)
session.detach()
if res:
    payload = res[0].get('payload', {})
    print(payload.get('data') or res[0])
else:
    print("No response received within timeout")
