import frida, time, psutil

for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
    if p.info['name'] == 'Survival.exe':
        print(f"Survival.exe PID={p.info['pid']} RSS={p.info['memory_info'].rss / (1024**3):.2f} GB VMS={p.info['memory_info'].vms / (1024**3):.2f} GB")

JS = r"""
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

const luaPayload = `
local mgr = DataCenter and DataCenter.WorldPointManager
local byClass = {}
local byType = {}
local desertCount = 0
local pointCount = 0
local bothCount = 0
for k, v in pairs((mgr and mgr.allViewPoints) or {}) do
    if type(v) == "table" and v.mainIndex == k and v.pointIndex == k then
        if v.desertInfo then desertCount = desertCount + 1 end
        if v.pointInfo then
            pointCount = pointCount + 1
            local pt = v.pointType or v.pointInfo.pointType or v.pointInfo.PointType or -1
            byType[pt] = (byType[pt] or 0) + 1
        end
        if v.desertInfo and v.pointInfo then bothCount = bothCount + 1 end
    end
end
local activeGoCount = 0
local modelGoActiveCount = 0
for k, obj in pairs((mgr and mgr.allObj) or {}) do
    local cn = (obj._class_type and obj._class_type.__cname) or "Unknown"
    byClass[cn] = (byClass[cn] or 0) + 1
    if obj.gameObject then
        activeGoCount = activeGoCount + 1
        local m = obj._cachedModelT
        if m and m.localPosition.x > -1000 then
            modelGoActiveCount = modelGoActiveCount + 1
        end
    end
end
local out = {
    "LuaMemMB=" .. string.format("%.1f", collectgarbage("count")/1024),
    "FPS=" .. string.format("%.1f", 1.0 / CS.UnityEngine.Time.smoothDeltaTime),
    "primaryPointInfo=" .. pointCount,
    "primaryDesertInfo=" .. desertCount,
    "both=" .. bothCount,
    "activeGo=" .. activeGoCount,
    "modelGoActive=" .. modelGoActiveCount
}
for k, v in pairs(byClass) do table.insert(out, "Class:" .. k .. "=" .. v) end
for k, v in pairs(byType) do table.insert(out, "Type:" .. tostring(k) .. "=" .. v) end
return table.concat(out, " | ")
`;

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        done = true;
        const L = args[0];
        const saved = top(L);
        try {
            const s = Memory.allocUtf8String(luaPayload);
            if (loadstring(L, s) === 0 && pcall(L, 0, 1, 0) === 0) {
                send({ data: getString(L, -1) });
            } else {
                send({ data: 'ERR: ' + getString(L, -1) });
            }
        } finally {
            settop(L, saved);
        }
    }
});
"""

session = frida.attach("Survival.exe")
sc = session.create_script(JS)
sc.on("message", lambda m, d: print(m.get("payload", m)))
sc.load()
time.sleep(0.4)
session.detach()
