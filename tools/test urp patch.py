import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

INSPECT_URP_PROPS = r"""
local out = {}
local function p(s) table.insert(out, s) end

local function IsNull(o)
    if o == nil then return true end
    if type(o) == "userdata" then
        return o:Equals(nil)
    end
    return false
end

local flags = CS.System.Reflection.BindingFlags
local toInt = CS.System.Convert.ToInt32
local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)

local gs = CS.UnityEngine.Rendering.GraphicsSettings
local rp = gs.currentRenderPipeline or gs.renderPipelineAsset
if not IsNull(rp) then
    rp.shadowDistance = 220.0
    rp.shadowCascadeCount = 2
    rp.shadowDepthBias = 1.2
    rp.shadowNormalBias = 1.2
    rp.msaaSampleCount = 4

    local t = rp:GetType()
    local fRes = t:GetField("m_MainLightShadowmapResolution", allFlags)
    if fRes then
        local v2048 = CS.System.Enum.ToObject(fRes.FieldType, toInt(2048))
        fRes:SetValue(rp, v2048)
    end
    p(string.format("URP Updated -> shadowDist=%.1f, cascades=%d, depthBias=%.1f, normalBias=%.1f, msaa=%d, shadowRes=%s",
        rp.shadowDistance, rp.shadowCascadeCount, rp.shadowDepthBias, rp.shadowNormalBias, rp.msaaSampleCount, tostring(rp.mainLightShadowmapResolution)))
end

local renderers = CS.UnityEngine.Object.FindObjectsOfType(typeof(CS.UnityEngine.MeshRenderer))
local fixedCount = 0
if renderers then
    for r = 0, renderers.Length - 1 do
        local mr = renderers[r]
        if not IsNull(mr) then
            local mat = mr.sharedMaterial
            if not IsNull(mat) and mat.enableInstancing then
                local sh = mat.shader
                if not IsNull(sh) then
                    local sName = sh.name
                    if not string.find(sName, "Instanc") and not string.find(sName, "Standard") and not string.find(sName, "Universal") and not string.find(sName, "URP") then
                        mat.enableInstancing = false
                        fixedCount = fixedCount + 1
                    end
                end
            end
        end
    end
end
p("Fixed non-instanced materials: " .. tostring(fixedCount))

return table.concat(out, "\n")
"""

FRIDA_JS = r"""
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
                    send({ type: 'result', data: getString(L, -1) });
                } else {
                    send({ type: 'error', data: getString(L, -1) });
                }
            } else {
                send({ type: 'error', data: 'Syntax: ' + getString(L, -1) });
            }
        } catch(e) {
            send({ type: 'error', data: e.toString() });
        } finally {
            settop(L, saved);
        }
    }
});
""" % json.dumps(INSPECT_URP_PROPS)

def main():
    session = frida.attach('Survival.exe')
    res_holder = []
    script = session.create_script(FRIDA_JS)
    script.on('message', lambda m, d: res_holder.append(m.get('payload') if m.get('type') == 'send' else {'type': 'error', 'data': str(m)}))
    script.load()
    for _ in range(30):
        if res_holder: break
        time.sleep(0.1)
    try: session.detach()
    except Exception: pass
    if res_holder:
        print(res_holder[0].get('data'))

if __name__ == '__main__':
    main()
