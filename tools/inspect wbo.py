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
local mgr = DataCenter.WorldPointManager
local smallCount = 0
local hqCount = 0
for k, v in pairs(mgr.allViewPoints or {}) do
    if type(v) == "table" and v.mainIndex == k and v.pointIndex == k and v.pointInfo then
        local pt = v.pointType or v.pointInfo.pointType or v.pointInfo.PointType
        if pt == 6 then
            local bid = mgr:_GetBuildIdForFactory(v)
            if bid and mgr:IsSmallBuild(bid) then
                smallCount = smallCount + 1
            else
                hqCount = hqCount + 1
            end
        end
    end
end
return string.format("PlayerHQs=%d | SmallSeasonalBuilds=%d", hqCount, smallCount)
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
