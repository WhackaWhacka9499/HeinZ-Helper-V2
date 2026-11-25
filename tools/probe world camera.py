import frida
import sys
import time
import json

sys.stdout.reconfigure(encoding='utf-8')

session = frida.attach('Survival.exe')

lua_code = """
local function enc(val, depth)
    depth = depth or 0
    if depth > 4 then return '\"...\"' end
    local t = type(val)
    if t == 'number' or t == 'boolean' then return tostring(val)
    elseif t == 'string' then return string.format('%q', val)
    elseif t == 'table' then
        local isArr = (#val > 0)
        local parts = {}
        if isArr then
            for i = 1, #val do table.insert(parts, enc(val[i], depth + 1)) end
            return '[' .. table.concat(parts, ',') .. ']'
        else
            for k, v in pairs(val) do
                table.insert(parts, string.format('%q:%s', tostring(k), enc(v, depth + 1)))
            end
            return '{' .. table.concat(parts, ',') .. '}'
        end
    else
        return '\"' .. tostring(val) .. '\"'
    end
end

local mgr = DataCenter and DataCenter.WorldPointManager
local scene = SceneManager and SceneManager.World
local cam = scene and scene.Camera
local ranges = mgr and mgr:GetViewLevelRange()
local lodRanges = mgr and mgr:GetLodRequestRange()
local outX = mgr and mgr.outOfViewOffX
local aoiOpt = mgr and mgr.aoiOptimizeEnabled

local res = {
    hasMgr = (mgr ~= nil),
    hasScene = (scene ~= nil),
    outOfViewOffX = outX,
    aoiOpt = aoiOpt,
    ranges = ranges,
    lodRanges = lodRanges,
    screenW = CS.UnityEngine.Screen.width,
    screenH = CS.UnityEngine.Screen.height
}
return enc(res)
"""

js = r"""
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
    const sz = Number(length.readU64());
    return sz === 0 ? '' : p.readUtf8String(sz);
}

const luaPayload = %s;

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        done = true;
        const L = args[0];
        const saved = top(L);
        try {
            const s = Memory.allocUtf8String(luaPayload);
            if (loadstring(L, s) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const ret = getString(L, -1);
                    send({ type: 'probe', data: ret });
                } else {
                    const err = getString(L, -1);
                    send({ type: 'lua_error', data: err });
                }
            }
        } catch(e) {
            send({ type: 'error', data: e.toString() });
        } finally {
            settop(L, saved);
        }
    }
});
""" % json.dumps(lua_code)

script = session.create_script(js)
def on_msg(m, d):
    if m.get('type') == 'send':
        payload = m.get('payload', {})
        print(payload.get('type'), payload.get('data'))
    else:
        print('Error:', m)

script.on('message', on_msg)
script.load()
time.sleep(2)
session.detach()
