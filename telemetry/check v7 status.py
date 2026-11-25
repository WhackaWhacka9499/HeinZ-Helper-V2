import frida, time

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
local inWorld = SceneManager and SceneManager.IsInWorld and SceneManager:IsInWorld()
local hasWorld = (SceneManager and SceneManager.World ~= nil)
local isInit = mgr and mgr.isInit
local c_vp = 0
local c_primary = 0
local c_obj = 0
local c_cache = 0
for k, v in pairs((mgr and mgr.allViewPoints) or {}) do
    c_vp = c_vp + 1
    if type(v) == "table" and v.mainIndex == k and v.pointIndex == k then
        c_primary = c_primary + 1
    end
end
for _ in pairs((mgr and mgr.allObj) or {}) do c_obj = c_obj + 1 end
for _ in pairs(_G._PersistentWorldPointCache or {}) do c_cache = c_cache + 1 end
local qLen = (mgr and mgr.toBuildList and #mgr.toBuildList or 0) - (mgr and mgr.toBuildListHead or 1) + 1
if qLen < 0 then qLen = 0 end
local smFields = {}
if SceneManager then
    for k, v in pairs(SceneManager) do
        if type(v) ~= "function" then table.insert(smFields, tostring(k) .. "=" .. tostring(v)) end
    end
end
local mFields = {}
if mgr then
    for k, v in pairs(mgr) do
        if type(v) ~= "function" then
            if type(v) == "table" then
                local c = 0
                for _ in pairs(v) do c = c + 1 end
                table.insert(mFields, tostring(k) .. "=tbl(" .. c .. ")")
            else
                table.insert(mFields, tostring(k) .. "=" .. tostring(v))
            end
        end
    end
end
return string.format("Status=%s | InWorld=%s | hasWorld=%s | isInit=%s | lodLv=%s | allViewPoints=%d (primary=%d) | allObj(built)=%d | buildQueue=%d | persistentCache=%d | fps=%s\\nSM: %s\\nMGR: %s",
    tostring(_G._LastMasterStatus), tostring(inWorld), tostring(hasWorld), tostring(isInit), tostring(mgr and mgr.lodLv), c_vp, c_primary, c_obj, qLen, c_cache, tostring(CS.UnityEngine.Application.targetFrameRate), table.concat(smFields, ", "), table.concat(mFields, ", "))
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
sc.on("message", lambda m, d: print(m["payload"]["data"]))
sc.load()
time.sleep(0.4)
session.detach()
