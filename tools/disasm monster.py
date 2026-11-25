import frida, sys, time
sys.path.insert(0, r'data/cache')
from disassemble_wpm import parse54, disasm54

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
local out = {}
for _, name in ipairs({'DestroyObject', 'OnCameraChange', 'OnLodChanged'}) do
    local fn = mgr[name]
    if type(fn) == 'function' then
        local ok, d = pcall(string.dump, fn)
        if ok and d then
            local hex = {}
            for i = 1, #d do hex[i] = string.format('%02X', string.byte(d, i)) end
            table.insert(out, 'WPM.' .. name .. ':' .. table.concat(hex))
        end
    end
end
local ok_m, wmo = pcall(require, 'SlgEngine.DataCenter.WorldPointManager.WorldMonsterObject')
if ok_m and wmo then
    for k, v in pairs(wmo) do
        if type(v) == 'function' then
            local ok, d = pcall(string.dump, v)
            if ok and d then
                local hex = {}
                for i = 1, #d do hex[i] = string.format('%02X', string.byte(d, i)) end
                table.insert(out, 'WMO.' .. tostring(k) .. ':' .. table.concat(hex))
            end
        end
    end
end
return table.concat(out, '\\n')
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
res = []
sc.on("message", lambda m, d: res.append(m["payload"]["data"]))
sc.load()
time.sleep(0.5)
session.detach()

for line in res[0].split("\n"):
    if ":" in line:
        n, h = line.split(":", 1)
        disasm54(n, parse54(bytes.fromhex(h)))
