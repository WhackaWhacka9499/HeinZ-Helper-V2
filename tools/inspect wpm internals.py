import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

INSPECT_WPM_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local mgr = DataCenter and DataCenter.WorldPointManager
local ws = SceneManager and SceneManager.World

local function dumpUpvalues(fn, label)
    if type(fn) ~= "function" then return end
    p("=== Upvalues of " .. label .. " ===")
    for i = 1, 30 do
        local name, val = debug.getupvalue(fn, i)
        if not name then break end
        if type(val) == "table" then
            local sub = {}
            local c = 0
            for k, v in pairs(val) do
                c = c + 1
                if c <= 15 then table.insert(sub, tostring(k) .. "=" .. tostring(v)) end
            end
            p(string.format("  [%d] %s = table(count=%d) {%s}", i, name, c, table.concat(sub, ", ")))
        else
            p(string.format("  [%d] %s = %s", i, name, tostring(val)))
        end
    end
end

if mgr then
    dumpUpvalues(mgr.DoSendViewRequest, "mgr.DoSendViewRequest")
    dumpUpvalues(mgr.SendViewRequest, "mgr.SendViewRequest")
    dumpUpvalues(mgr.UpdateViewRequest, "mgr.UpdateViewRequest")
    dumpUpvalues(mgr.GetViewLevelRange, "mgr.GetViewLevelRange")
    dumpUpvalues(mgr.GetViewBounds, "mgr.GetViewBounds")
    dumpUpvalues(mgr.GetLodRequestRange, "mgr.GetLodRequestRange")
    dumpUpvalues(mgr.GetServerLod, "mgr.GetServerLod")
    dumpUpvalues(mgr.CheckWorldPointVisible, "mgr.CheckWorldPointVisible")
    dumpUpvalues(mgr.DoParse, "mgr.DoParse")
    dumpUpvalues(mgr.CreateObject, "mgr.CreateObject")
    dumpUpvalues(mgr.Close, "mgr.Close")

    p("\n=== Testing GetServerLod & GetLodRequestRange & GetViewLevelRange ===")
    for lod = 1, 12 do
        local sLod = mgr:GetServerLod(lod)
        local rRange = mgr:GetLodRequestRange(lod)
        local lRange1, lRange2, lRange3 = mgr:GetViewLevelRange(lod)
        p(string.format("  LOD %2d -> ServerLod=%s | ReqRange=%s | ViewLevelRange=(%s, %s, %s)",
            lod, tostring(sLod), tostring(rRange), tostring(lRange1), tostring(lRange2), tostring(lRange3)))
    end

    p("\n=== Inspecting mgr data structures ===")
    p("  zonePointMap count = " .. tostring(table.count(mgr.zonePointMap)))
    p("  validZones count = " .. tostring(table.count(mgr.validZones)))
    p("  allViewPoints count = " .. tostring(table.count(mgr.allViewPoints)))
    p("  outOfViewPoints count = " .. tostring(table.count(mgr.outOfViewPoints)))
    p("  pointsIds count = " .. tostring(table.count(mgr.pointsIds)))
    p("  uuidInfoMap count = " .. tostring(table.count(mgr.uuidInfoMap)))
    p("  allObj count = " .. tostring(table.count(mgr.allObj)))
    p("  toBuildList count = " .. tostring(mgr.toBuildList and #mgr.toBuildList or 0) .. " (head=" .. tostring(mgr.toBuildListHead) .. ")")
    p("  toBuildSet count = " .. tostring(table.count(mgr.toBuildSet)))

    -- Sample zonePointMap entries
    local zCount = 0
    local totalPointsInZoneMap = 0
    for zId, zTbl in pairs(mgr.zonePointMap or {}) do
        zCount = zCount + 1
        if type(zTbl) == "table" then
            local pc = table.count(zTbl)
            totalPointsInZoneMap = totalPointsInZoneMap + pc
            if pc > 0 and zCount <= 20 then
                p(string.format("    zonePointMap[%s] has %d points", tostring(zId), pc))
            end
        end
    end
    p("  Total points stored across all zonePointMap zones = " .. tostring(totalPointsInZoneMap))
end

if ws and ws.Camera then
    p("\n=== WorldCamera Zoom / Edge / Mobile Restrictions ===")
    p("  GetZoom() = " .. tostring(ws.Camera:GetZoom()))
    p("  GetZoomMin() = " .. tostring(ws.Camera:GetZoomMin()))
    p("  GetZoomMax() = " .. tostring(ws.Camera:GetZoomMax()))
    p("  GetInitZoom() = " .. tostring(ws.Camera:GetInitZoom()))
    p("  GetLodLevel() = " .. tostring(ws.Camera:GetLodLevel()))
    p("  GetLodDistance() = " .. tostring(ws.Camera:GetLodDistance()))
    p("  GetMinLodDistance() = " .. tostring(ws.Camera:GetMinLodDistance()))
    dumpUpvalues(ws.Camera.GetLodLevel, "ws.Camera.GetLodLevel")
    dumpUpvalues(ws.Camera.ClampToEdge, "ws.Camera.ClampToEdge")
    dumpUpvalues(ws.Camera.SetZoomMax, "ws.Camera.SetZoomMax")
    if ws.Camera.touchCamera then
        local tc = ws.Camera.touchCamera
        p("  tc.CamZoomMin = " .. tostring(tc.CamZoomMin))
        p("  tc.CamZoomMax = " .. tostring(tc.CamZoomMax))
        p("  tc.BoundaryMin = " .. tostring(tc.BoundaryMin))
        p("  tc.BoundaryMax = " .. tostring(tc.BoundaryMax))
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
""" % json.dumps(INSPECT_WPM_LUA)

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
