import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

SCENE_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local sm = CS.UnityEngine.SceneManagement.SceneManager
p("=== UNITY SCENES ===")
for i = 0, sm.sceneCount - 1 do
    local sc = sm.GetSceneAt(i)
    p(string.format("  Scene[%d]: name='%s', isLoaded=%s, rootCount=%d", i, sc.name, tostring(sc.isLoaded), sc.rootCount))
    local roots = sc:GetRootGameObjects()
    if roots then
        for r = 0, math.min(roots.Length - 1, 30) do
            local go = roots[r]
            p(string.format("    Root[%d]: %s (active=%s, children=%d)", r, go.name, tostring(go.activeSelf), go.transform.childCount))
        end
    end
end

local ws = SceneManager and SceneManager.World
if ws then
    p("\n=== SceneManager.World fields ===")
    for k, v in pairs(ws) do
        if type(v) ~= "function" then
            p(string.format("  ws.%s = %s", tostring(k), tostring(v)))
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
            if (loadstring(L, s) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    send({ type: 'result', data: getString(L, -1) });
                } else {
                    send({ type: 'error', data: getString(L, -1) });
                }
            } else {
                send({ type: 'error', data: 'Syntax: ' + getString(L, -1) });
            }
        } catch(e) {
            send({ type: 'error', data: e.toString() });
        } finally {
            settop(L, saved);
        }
    }
});
""" % json.dumps(SCENE_LUA)

def main():
    session = frida.attach('Survival.exe')
    res_holder = []
    script = session.create_script(FRIDA_JS)
    script.on('message', lambda m, d: res_holder.append(m.get('payload') if m.get('type') == 'send' else {'type': 'error', 'data': str(m)}))
    script.load()
    for _ in range(30):
        if res_holder: break
        time.sleep(0.1)
    try: session.detach()
    except Exception: pass
    if res_holder:
        print(res_holder[0].get('data'))

if __name__ == '__main__':
    main()
