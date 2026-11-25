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
local out = {}
table.insert(out, "TileCountX=" .. tostring(TileCountX) .. ",TileCountY=" .. tostring(TileCountY))
local idx1 = SceneUtils.TileXYToIndex(10, 20)
local idx2 = SceneUtils.TileXYToIndex(600, 600)
local x1, y1 = SceneUtils.IndexToTileXY(idx1)
table.insert(out, string.format("idx(10,20)=%d -> (%d,%d)", idx1, x1, y1))
table.insert(out, string.format("idx(600,600)=%d", idx2))
if CS.SceneManager and CS.SceneManager.World then
    local wx, wy, wz = CS.SceneManager.World:GetCurTarget()
    local tx, ty = SceneUtils.WorldToTileXZ(wx, wz, ForceChangeScene.World)
    table.insert(out, string.format("CS_World:GetCurTarget=(%.1f,%.1f,%.1f)->tile=(%s,%s)", wx or -1, wy or -1, wz or -1, tostring(tx), tostring(ty)))
end
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
sc.on("message", lambda m, d: print(m["payload"]["data"]))
sc.load()
time.sleep(0.4)
session.detach()
