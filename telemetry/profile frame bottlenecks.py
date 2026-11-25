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
local allObj = mgr and mgr.allObj or {}

local t0 = os.clock()
local c = 0
for k, obj in pairs(allObj) do
    local pType = obj.pointType or (obj.GetPointType and obj:GetPointType())
    if pType == 6 then c = c + 1 end
end
local msOld = (os.clock() - t0) * 1000

local t1 = os.clock()
local c2 = 0
for k, obj in pairs(allObj) do
    -- Fast direct field access without function call
    local pType = obj.pointType
    if pType == 6 or pType == 4 then c2 = c2 + 1 end
end
local msNew = (os.clock() - t1) * 1000

return string.format("12500 objs: oldLoop=%.2fms | fastLoop=%.2fms", msOld, msNew)
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
