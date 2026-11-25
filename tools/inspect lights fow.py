import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

LIGHT_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local lights = CS.UnityEngine.Object.FindObjectsOfType(typeof(CS.UnityEngine.Light))
p("=== ACTIVE LIGHTS ===")
if lights then
    for i = 0, lights.Length - 1 do
        local l = lights[i]
        if l and l.enabled and l.gameObject.activeInHierarchy then
            p(string.format("  Light '%s' (type=%s): shadows=%s, strength=%s, bias=%s, normalBias=%s, nearPlane=%s, mask=%s",
                tostring(l.gameObject.name), tostring(l.type), tostring(l.shadows),
                tostring(l.shadowStrength), tostring(l.shadowBias), tostring(l.shadowNormalBias), tostring(l.shadowNearPlane), tostring(l.cullingMask)))
        end
    end
end

p("\n=== FOWSystem & uSkyPro ===")
local fow = CS.UnityEngine.GameObject.Find("FOWSystem")
if fow then
    local comps = fow:GetComponentsInChildren(typeof(CS.UnityEngine.Component), true)
    for i = 0, comps.Length - 1 do
        local c = comps[i]
        if c then p("  FOW comp: " .. c.gameObject.name .. " -> " .. c:GetType().FullName) end
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
""" % json.dumps(LIGHT_LUA)

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
