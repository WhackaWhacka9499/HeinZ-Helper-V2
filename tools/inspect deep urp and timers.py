import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

DEEP_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local flags = CS.System.Reflection.BindingFlags
local toInt = CS.System.Convert.ToInt32
local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)

-- 1. Inspect UniversalRenderPipelineAsset_High fields
p("=== 1. URP PIPELINE ASSET FIELDS ===")
pcall(function()
    local gs = CS.UnityEngine.Rendering.GraphicsSettings
    local rp = gs.currentRenderPipeline or gs.renderPipelineAsset
    if rp then
        local t = rp:GetType()
        local fields = t:GetFields(allFlags)
        for i = 0, fields.Length - 1 do
            local f = fields[i]
            local fn = f.Name
            if string.find(string.lower(fn), "shadow") or string.find(string.lower(fn), "bias") or string.find(string.lower(fn), "msaa") or string.find(string.lower(fn), "hdr") or string.find(string.lower(fn), "scale") or string.find(string.lower(fn), "batch") or string.find(string.lower(fn), "depth") or string.find(string.lower(fn), "cascade") or string.find(string.lower(fn), "light") then
                local ok, val = pcall(function() return f:GetValue(rp) end)
                p(string.format("  %s = %s", fn, ok and tostring(val) or "err"))
            end
        end
    end
end)

-- 2. Inspect TimerManager.__update_timer entries to locate the 5s rogue heartbeat
p("\n=== 2. TIMER MANAGER ACTIVE TIMERS (delay >= 0.2) ===")
pcall(function()
    local tm = TimerManager and TimerManager:GetInstance()
    if tm and tm.__update_timer then
        for k, tObj in pairs(tm.__update_timer) do
            if type(tObj) == "table" then
                local infoParts = {}
                for tk, tv in pairs(tObj) do
                    if type(tv) ~= "function" and type(tv) ~= "table" then
                        table.insert(infoParts, tostring(tk) .. "=" .. tostring(tv))
                    elseif type(tv) == "function" then
                        local dinfo = debug and debug.getinfo and debug.getinfo(tv, "Sln")
                        if dinfo then
                            table.insert(infoParts, string.format("%s=func(%s:%d)", tostring(tk), tostring(dinfo.short_src), dinfo.linedefined or -1))
                        else
                            table.insert(infoParts, tostring(tk) .. "=func")
                        end
                    end
                end
                p(string.format("  Timer[%s]: %s", tostring(k), table.concat(infoParts, ", ")))
            end
        end
    end
end)

-- 3. Inspect SceneManager & World Camera state
p("\n=== 3. SCENE MANAGER & WORLD CAMERA ===")
pcall(function()
    local sm = SceneManager
    if sm then
        for k, v in pairs(sm) do
            if type(v) ~= "function" then
                p(string.format("  SceneManager.%s = %s", tostring(k), tostring(v)))
            end
        end
    end
    local ws = sm and sm.World
    if ws and ws.Camera then
        for k, v in pairs(ws.Camera) do
            if type(v) ~= "function" then
                p(string.format("  ws.Camera.%s = %s", tostring(k), tostring(v)))
            end
        end
    end
end)

-- 4. Inspect WorldPointManager fields
p("\n=== 4. WORLD POINT MANAGER FIELDS ===")
pcall(function()
    local wpm = DataCenter and DataCenter.WorldPointManager
    if wpm then
        for k, v in pairs(wpm) do
            if type(v) == "table" then
                local cnt = 0
                for _ in pairs(v) do cnt = cnt + 1 end
                p(string.format("  wpm.%s = table(count=%d)", tostring(k), cnt))
            elseif type(v) ~= "function" then
                p(string.format("  wpm.%s = %s", tostring(k), tostring(v)))
            end
        end
    end
end)

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
""" % json.dumps(DEEP_LUA)

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
