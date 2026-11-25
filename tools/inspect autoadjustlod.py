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
local flags = CS.System.Reflection.BindingFlags
local toInt = CS.System.Convert.ToInt32
local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)
local out = {}
for k, obj in pairs((mgr and mgr.allObj) or {}) do
    if obj.adjuster then
        local t = obj.adjuster:GetType()
        local flds = t:GetFields(allFlags)
        for i = 0, flds.Length - 1 do
            local f = flds[i]
            table.insert(out, "F:" .. f.Name .. "=" .. tostring(f:GetValue(obj.adjuster)))
        end
        local mths = t:GetMethods(allFlags)
        for i = 0, mths.Length - 1 do
            local m = mths[i]
            if m.DeclaringType == t then
                table.insert(out, "M:" .. m.Name)
            end
        end
        break
    end
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
