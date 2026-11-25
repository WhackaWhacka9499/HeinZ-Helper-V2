import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

TRACE_WPM_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local mgr = DataCenter and DataCenter.WorldPointManager
local mt = mgr and getmetatable(mgr)
local proto = mt and mt.__index

-- Use debug.sethook to trace what proto.CalcOutOfViewZones and AddToBuildList do!
if mgr and proto then
    local traceLog = {}
    local count = 0
    local function hook(event, line)
        count = count + 1
        if count > 250 then return end
        local info = debug.getinfo(2, "nSl")
        if info then
            local locals = {}
            for i = 1, 10 do
                local ln, lv = debug.getlocal(2, i)
                if not ln then break end
                if ln ~= "self" and type(lv) ~= "table" and type(lv) ~= "function" then
                    table.insert(locals, ln .. "=" .. tostring(lv))
                elseif ln ~= "self" and type(lv) == "table" then
                    table.insert(locals, ln .. "=tbl")
                end
            end
            table.insert(traceLog, string.format("  [%s] %s:%s (%s) {%s}",
                event, tostring(info.name), tostring(line or info.linedefined), tostring(info.short_src), table.concat(locals, ", ")))
        end
    end

    -- Find an unbuilt point in allViewPoints
    local sampleIdx, sampleInfo = nil, nil
    for k, v in pairs(mgr.allViewPoints or {}) do
        if not mgr.allObj[k] then
            sampleIdx, sampleInfo = k, v
            break
        end
    end

    p("=== Tracing AddToBuildList & BuildAsync on unbuilt point " .. tostring(sampleIdx) .. " ===")
    if sampleIdx then
        debug.sethook(hook, "c")
        mgr:AddToBuildList(sampleIdx)
        mgr:BuildAsync()
        debug.sethook()
    end
    for _, l in ipairs(traceLog) do p(l) end
    p("After AddToBuildList + BuildAsync: allObj[sampleIdx] = " .. tostring(mgr.allObj[sampleIdx]))
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
    if (p.isNull()) return '';
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
""" % json.dumps(TRACE_WPM_LUA)

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
