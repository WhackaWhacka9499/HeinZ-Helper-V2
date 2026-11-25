import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

INSPECT_TM_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local tm = TimerManager and TimerManager:GetInstance()
if tm then
    p("=== TimerManager methods & __update_timer contents ===")
    if tm._class_type then
        for k, v in pairs(tm._class_type) do
            p("  class." .. tostring(k) .. " = " .. tostring(v))
        end
    end
    if tm.__update_timer then
        local cnt = 0
        for k, v in pairs(tm.__update_timer) do
            cnt = cnt + 1
            local fields = {}
            if type(k) == "table" then
                for fk, fv in pairs(k) do
                    if type(fv) == "function" then
                        local dinfo = debug and debug.getinfo and debug.getinfo(fv, "Sln")
                        local src = dinfo and (tostring(dinfo.short_src) .. ":" .. tostring(dinfo.linedefined)) or "func"
                        table.insert(fields, tostring(fk) .. "=" .. src)
                    else
                        table.insert(fields, tostring(fk) .. "=" .. tostring(fv))
                    end
                end
            end
            if string.find(table.concat(fields, ","), "string") or (type(k) == "table" and (k.delay == 5 or k.delay == 0.25)) then
                p(string.format("  MATCH [%s]: %s", tostring(k), table.concat(fields, ", ")))
            end
        end
        p("Total __update_timer: " .. tostring(cnt))
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
""" % json.dumps(INSPECT_TM_LUA)

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
