import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

DIAG_MAP_SWEEP_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local mgr = DataCenter and DataCenter.WorldPointManager
local ws = SceneManager and SceneManager.World

p("=== 1. GLOBAL & PLAYER CHECK ===")
p("LuaEntry = " .. tostring(LuaEntry))
p("LuaEntry.Player = " .. tostring(LuaEntry and LuaEntry.Player))
p("DataCenter.PlayerDataManager = " .. tostring(DataCenter and DataCenter.PlayerDataManager))
if mgr then
    p("mgr.aoiServerId = " .. tostring(mgr.aoiServerId))
    p("mgr.waitingForReply = " .. tostring(mgr.waitingForReply))
    p("mgr.lastSendTime = " .. tostring(mgr.lastSendTime))
    p("mgr.busyTime = " .. tostring(mgr.busyTime))
    p("mgr.syncBusyTime = " .. tostring(mgr.syncBusyTime))
    p("mgr.disableRequestOpt = " .. tostring(mgr.disableRequestOpt))
    p("mgr.aoiOptimizeEnabled = " .. tostring(mgr.aoiOptimizeEnabled))
    p("mgr.aoiReconcileEnabled = " .. tostring(mgr.aoiReconcileEnabled))
    p("mgr.worldLodType = " .. tostring(mgr.worldLodType))
    p("mgr.lodLv = " .. tostring(mgr.lodLv))
    p("mgr.aoiLodLevel = " .. tostring(mgr.aoiLodLevel))
end

p("\n=== 2. WORLDPOINTMANAGER METHODS & SOURCE LOCATIONS ===")
if mgr then
    local mt = getmetatable(mgr)
    local idx = mt and mt.__index
    if type(idx) == "table" then
        local names = {}
        for k, v in pairs(idx) do
            if type(v) == "function" then
                local info = debug.getinfo(v, "S")
                table.insert(names, string.format("  %-36s (%s:%d-%d)", tostring(k), tostring(info and info.short_src), info and info.linedefined or -1, info and info.lastlinedefined or -1))
            end
        end
        table.sort(names)
        for _, line in ipairs(names) do p(line) end
    end
end

p("\n=== 3. WORLD CAMERA ZOOM / DISTANCE / MOBILE LIMITS ===")
if ws and ws.Camera then
    local wcam = ws.Camera
    for k, v in pairs(wcam) do
        if type(v) ~= "function" then
            p(string.format("  ws.Camera.%-26s = %s", tostring(k), tostring(v)))
        end
    end
    local mt = getmetatable(wcam)
    local idx = mt and mt.__index
    if type(idx) == "table" then
        local cnames = {}
        for k, v in pairs(idx) do
            if type(v) == "function" then
                local info = debug.getinfo(v, "S")
                table.insert(cnames, string.format("  ws.Camera:%-28s (%s:%d-%d)", tostring(k), tostring(info and info.short_src), info and info.linedefined or -1, info and info.lastlinedefined or -1))
            end
        end
        table.sort(cnames)
        for _, line in ipairs(cnames) do p(line) end
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
""" % json.dumps(DIAG_MAP_SWEEP_LUA)

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
