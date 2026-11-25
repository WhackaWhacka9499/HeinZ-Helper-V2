import frida, sys, time
sys.path.insert(0, r'data/cache')
from disassemble_wpm import parse54, disasm54

JS = r"""
const mod = Process.getModuleByName("xlua.dll");
const luaL_loadbufferx = new NativeFunction(mod.getExportByName("luaL_loadbufferx"), "int", ["pointer", "pointer", "uint64", "pointer", "pointer"]);
const lua_pcallk = new NativeFunction(mod.getExportByName("lua_pcallk"), "int", ["pointer", "int", "int", "int", "uint64", "pointer"]);
const lua_tolstring = new NativeFunction(mod.getExportByName("lua_tolstring"), "pointer", ["pointer", "int", "pointer"]);
const lua_settop = new NativeFunction(mod.getExportByName("lua_settop"), "void", ["pointer", "int"]);

let capturedL = null;
const hook = Interceptor.attach(mod.getExportByName("lua_gettop"), {
    onEnter(args) { if (!capturedL) capturedL = args[0]; }
});

const LUA = `
local mgr = DataCenter.WorldPointManager
local out = {}
for _, name in ipairs({'DoParse', 'ReconcileAoiPoints', 'ReconcileAoiDeserts', 'Update', 'Init', 'AddOccupyPoints2Queued', 'CreateObject'}) do
    local fn = mgr[name]
    if type(fn) == 'function' then
        local ok, d = pcall(string.dump, fn)
        if ok and d then
            local hex = {}
            for i = 1, #d do hex[i] = string.format('%02X', string.byte(d, i)) end
            table.insert(out, name .. ':' .. table.concat(hex))
        end
    end
end
return table.concat(out, '\\n')
`;

setTimeout(() => {
    hook.detach();
    const buf = Memory.allocUtf8String(LUA);
    luaL_loadbufferx(capturedL, buf, LUA.length, Memory.allocUtf8String("extra"), ptr(0));
    lua_pcallk(capturedL, 0, 1, 0, 0, ptr(0));
    const lenPtr = Memory.alloc(8);
    const s = lua_tolstring(capturedL, -1, lenPtr);
    send({d: s.readUtf8String(lenPtr.readU64().toNumber())});
    lua_settop(capturedL, -2);
}, 150);
"""

session = frida.attach(32196)
sc = session.create_script(JS)
res = []
sc.on("message", lambda m, d: res.append(m["payload"]["d"]))
sc.load()
time.sleep(0.5)
session.detach()

for line in res[0].split("\n"):
    if ":" in line:
        n, h = line.split(":", 1)
        disasm54(n, parse54(bytes.fromhex(h)))
