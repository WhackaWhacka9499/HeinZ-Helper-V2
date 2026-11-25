import frida, time, psutil

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
TimerManager:GetInstance():DelayInvoke(function()
    pcall(function()
        local mgr = DataCenter and DataCenter.WorldPointManager
        local ws = SceneManager and SceneManager.World
        if ws and ws.Camera then
            local afterTbl = ws.Camera.AfterUpdate or ws.Camera.AfterUpdateAction
            if type(afterTbl) == "table" then
                afterTbl["Proximity3DGate"] = nil
            end
        end
        -- Stop old heartbeat & proximity timers from re-queuing all 14,740 monsters
        _G._masterHeartbeatToken = (_G._masterHeartbeatToken or 0) + 1
        _G._masterProxToken = (_G._masterProxToken or 0) + 1

        if not mgr then return end
        local camX, camY = 600, 600
        if mgr.curCameraTarget and mgr.curCameraTarget.x and mgr.curCameraTarget.x > 0 then
            camX, camY = SceneUtils.WorldToTilePos(mgr.curCameraTarget.x, mgr.curCameraTarget.y, mgr.curCameraTarget.z)
        elseif mgr.reqPos and mgr.reqPos.x then
            camX, camY = mgr.reqPos.x, mgr.reqPos.y
        end

        -- Clear pending build queue of distant monsters
        mgr.toBuildList = {}
        mgr.toBuildSet = {}
        mgr.toBuildListHead = 1

        local destroyedMonsters = 0
        local deactivated3D = 0
        for k, obj in pairs(mgr.allObj or {}) do
            local cn = (obj._class_type and obj._class_type.__cname) or ""
            local px, py = SceneUtils.IndexToTileXY(k)
            local dist = math.max(math.abs(px - camX), math.abs(py - camY))
            if cn == "WorldMonsterObject" and dist > 140 then
                mgr:DestroyObject(k)
                destroyedMonsters = destroyedMonsters + 1
            else
                if obj.adjuster then
                    pcall(obj.adjuster.SetNoOptimizeActivate, obj.adjuster, true)
                end
                if obj.gameObject then
                    local m = obj._cachedModelT or obj.gameObject.transform:Find("ModelGo") or obj.gameObject.transform:Find("Model")
                    if m and m.gameObject then
                        if (mgr.lodLv or 1) >= 3 or dist > 90 then
                            if m.gameObject.activeSelf then
                                m.gameObject:SetActive(false)
                                deactivated3D = deactivated3D + 1
                            end
                        else
                            m.localPosition = CS.UnityEngine.Vector3.zero
                            if not m.gameObject.activeSelf then
                                m.gameObject:SetActive(true)
                            end
                        end
                    end
                end
            end
        end

        collectgarbage("collect")
        CS.UnityEngine.Resources.UnloadUnusedAssets()
        _G._ReliefResult = string.format("destroyedMonsters=%d, deactivated3D=%d", destroyedMonsters, deactivated3D)
    end)
end, 0.01)
return "SCHEDULED_RELIEF"
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
time.sleep(0.5)
session.detach()
