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
local seen = {}
for k, obj in pairs((mgr and mgr.allObj) or {}) do
    local cn = (obj._class_type and obj._class_type.__cname) or "Unknown"
    if not seen[cn] and obj.adjuster then
        seen[cn] = true
        local adj = obj.adjuster
        local f = adj:GetType():GetField("settings", allFlags)
        local arr = f and f:GetValue(adj)
        if arr and arr.Length > 0 then
            local st = arr:GetType():GetElementType()
            local tF = st:GetField("targets", allFlags)
            local lF = st:GetField("showLods", allFlags)
            local sDesc = {}
            for i = 0, arr.Length - 1 do
                local s = arr[i]
                local targets = tF:GetValue(s)
                local lods = lF:GetValue(s)
                local tNames = {}
                for ti = 0, targets.Length - 1 do
                    table.insert(tNames, targets[ti] and targets[ti].name or "nil")
                end
                local lNums = {}
                for li = 0, lods.Count - 1 do
                    table.insert(lNums, tostring(lods[li]))
                end
                table.insert(sDesc, string.format("[%d]={targets=(%s),lods=(%s)}", i, table.concat(tNames, ","), table.concat(lNums, ",")))
            end
            table.insert(out, cn .. ": " .. table.concat(sDesc, " ; "))
        end
    end
end
return table.concat(out, "\\n")
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
