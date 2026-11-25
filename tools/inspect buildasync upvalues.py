import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BUILDASYNC_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local mgr = DataCenter and DataCenter.WorldPointManager
local mt = mgr and getmetatable(mgr)
local proto = mt and mt.__index

if proto then
    p("=== 1. Upvalues of WorldPointManager:BuildAsync ===")
    for i = 1, 10 do
        local name, val = debug.getupvalue(proto.BuildAsync, i)
        if not name then break end
        if name ~= "_ENV" then
            p(string.format("  [%d] %s = %s", i, name, tostring(val)))
        end
    end

    p("\n=== 2. Upvalues & Identifiers of WorldPointManager:OnLodChanged & OnCameraChange & Update ===")
    for _, mname in ipairs({"OnLodChanged", "OnCameraChange", "Update"}) do
        local fn = proto[mname]
        if fn then
            local ok, dumped = pcall(string.dump, fn)
            local strings = {}
            if ok and dumped then
                for s in string.gmatch(dumped, "[%w_%./\\:%-%+%*%s%(%)%[%]%{%}]+") do
                    if #s >= 3 and not string.find(s, "^%s+$") then table.insert(strings, s) end
                end
            end
            p("  " .. mname .. ": " .. table.concat(strings, " | "))
            for i = 1, 10 do
                local n, v = debug.getupvalue(fn, i)
                if not n then break end
                if n ~= "_ENV" then p(string.format("    upval [%d] %s = %s", i, n, tostring(v))) end
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
""" % json.dumps(BUILDASYNC_LUA)

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
