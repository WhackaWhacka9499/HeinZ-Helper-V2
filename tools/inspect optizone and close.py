import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

OPTIZONE_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local mgr = DataCenter and DataCenter.WorldPointManager
local mt = mgr and getmetatable(mgr)
local proto = mt and mt.__index

if mgr and proto then
    p("=== 1. Check overridden methods on mgr instance vs class prototype ===")
    for _, name in ipairs({"CalcOutOfViewZones", "DeleteOutOfView", "AddToDeleteList", "RemovePointInfo", "ReconcileAoiPoints", "ReconcileAoiDeserts", "OptiZone_Add", "OptiZone_Remove", "OptiZone_Draw", "Close", "DestroyAll", "GetViewLevelRange", "GetViewBounds", "IsOutOfRange", "IsOutOfRange2"}) do
        p(string.format("  %-22s: instance=%s | proto=%s", name, tostring(rawget(mgr, name)), tostring(proto[name])))
    end

    p("\n=== 2. Trace what proto.OptiZone_Add(mgr, zoneId) does ===")
    -- Find a zoneId in zonePointMap that is NOT in validZones
    local testZoneId = nil
    local testZoneCount = 0
    for zId, zTbl in pairs(mgr.zonePointMap or {}) do
        if not mgr.validZones[zId] then
            local c = table.count(zTbl)
            if c > 0 then
                testZoneId = zId
                testZoneCount = c
                break
            end
        end
    end

    p(string.format("  Before OptiZone_Add: validZones=%d, toBuildList=%d (head=%d), allObj=%d",
        table.count(mgr.validZones), mgr.toBuildList and #mgr.toBuildList or 0, mgr.toBuildListHead or 0, table.count(mgr.allObj)))
    if testZoneId then
        p(string.format("  Testing OptiZone_Add on zoneId=%s (has %d points in zonePointMap)...", tostring(testZoneId), testZoneCount))
        mgr.validZones[testZoneId] = true
        proto.OptiZone_Add(mgr, testZoneId)
        p(string.format("  After OptiZone_Add: validZones=%d, toBuildList=%d (head=%d), allObj=%d",
            table.count(mgr.validZones), mgr.toBuildList and #mgr.toBuildList or 0, mgr.toBuildListHead or 0, table.count(mgr.allObj)))
    end

    p("\n=== 3. Trace what happens on World <-> HQ (City) transition ===")
    p("  SceneManager.ChangeToMainCity = " .. tostring(SceneManager and SceneManager.ChangeToMainCity))
    p("  SceneManager.ChangeToWorld = " .. tostring(SceneManager and SceneManager.ChangeToWorld))
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
""" % json.dumps(OPTIZONE_LUA)

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
