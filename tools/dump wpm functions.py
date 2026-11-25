import frida
import json
import time
import sys
import base64

sys.stdout.reconfigure(encoding='utf-8')

DUMP_LUA = r"""
local out = {}
local mgr = DataCenter and DataCenter.WorldPointManager
local mt = mgr and getmetatable(mgr)
local proto = mt and mt.__index

local function inspectFunc(fn, name)
    if type(fn) ~= "function" then return end
    local ok, dumped = pcall(string.dump, fn)
    local info = debug.getinfo(fn, "Slnu")
    -- Extract all printable strings from bytecode chunk
    local strings = {}
    if ok and dumped then
        for s in string.gmatch(dumped, "[%w_%./\\:%-%+%*%s%(%)%[%]%{%}]+") do
            if #s >= 3 and not string.find(s, "^%s+$") then
                table.insert(strings, s)
            end
        end
    end
    table.insert(out, string.format("=== %s (%s:%d-%d, params=%d, upvals=%d) ===",
        name, tostring(info and info.short_src), info and info.linedefined or -1, info and info.lastlinedefined or -1,
        info and info.nparams or -1, info and info.nups or -1))
    table.insert(out, "  Strings/Identifiers: " .. table.concat(strings, " | "))
end

if proto then
    local targets = {
        "StartUp", "Close", "DestroyAll",
        "GetViewLevelRange", "GetViewBounds", "GetLodRequestRange", "GetServerLod",
        "UpdateViewRequest", "SendViewRequest", "DoSendViewRequest",
        "HandleViewPointsReply", "ParseServerDataAsync", "DoParse",
        "AddPointInfo", "AddDesertInfo", "AddToBuildList", "BuildAsync", "CreateObject",
        "IsOutOfRange", "IsOutOfRange2", "CalcOutOfViewZones", "DeleteOutOfView",
        "OptiZone_Add", "OptiZone_Remove", "OptiZone_Draw"
    }
    for _, t in ipairs(targets) do
        inspectFunc(proto[t], "WorldPointManager:" .. t)
    end
end

local ws = SceneManager and SceneManager.World
if ws and ws.Camera then
    local cmt = getmetatable(ws.Camera)
    local cproto = cmt and cmt.__index
    if type(cproto) == "table" then
        for _, t in ipairs({"Init", "InitMeta", "GetZoomMin", "GetZoomMax", "SetZoomMax", "GetLodLevel", "ClampToEdge", "RecalculateEdgePadding", "RecalculateEdgePoints"}) do
            inspectFunc(cproto[t], "WorldCamera:" .. t)
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
""" % json.dumps(DUMP_LUA)

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
