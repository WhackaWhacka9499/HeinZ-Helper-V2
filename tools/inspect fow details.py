import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

FOW_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end
local flags = CS.System.Reflection.BindingFlags
local toInt = CS.System.Convert.ToInt32
local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)

local fow = CS.UnityEngine.GameObject.Find("FOWSystem")
if fow then
    local comps = fow:GetComponentsInChildren(typeof(CS.UnityEngine.Component), true)
    for i = 0, comps.Length - 1 do
        local c = comps[i]
        if c and (c:GetType().Name == "FowSystem2" or c:GetType().Name == "VolumetricFog") then
            p("=== Component: " .. c:GetType().FullName .. " (enabled=" .. tostring(c.enabled) .. ", active=" .. tostring(c.gameObject.activeInHierarchy) .. ") ===")
            local fields = c:GetType():GetFields(allFlags)
            for f = 0, fields.Length - 1 do
                local fd = fields[f]
                local ok, val = pcall(function() return fd:GetValue(c) end)
                local sVal = ok and string.gsub(tostring(val), "[^\32-\126]", "") or "err"
                p("  " .. fd.Name .. " = " .. sVal)
            end
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
""" % json.dumps(FOW_LUA)

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
