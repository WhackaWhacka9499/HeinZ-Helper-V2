import frida, time, json

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
local bar = _G._MasterOverlayBarGo
local tmp = _G._MasterOverlayTmp
local t = _G._MasterToggles
local barActive = bar and (type(bar) == "userdata" and not bar:Equals(nil)) and bar.activeSelf
local textVal = tmp and (type(tmp) == "userdata" and not tmp:Equals(nil)) and tmp.text or "nil"
local togglesStr = ""
if t then
    for k, v in pairs(t) do
        togglesStr = togglesStr .. k .. "=" .. tostring(v) .. ", "
    end
end
return string.format("BarGo=%s (active=%s) | Text=%s | Toggles={%s}", tostring(bar), tostring(barActive), tostring(textVal), togglesStr)
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
sc.on("message", lambda m, d: print(m.get("payload", {}).get("data", m)))
sc.load()
time.sleep(0.4)
session.detach()
