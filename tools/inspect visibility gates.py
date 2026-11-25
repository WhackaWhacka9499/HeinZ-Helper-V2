import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

VIS_GATES_LUA = r"""
local out = {}
local function p(s) table.insert(out, s) end

local mgr = DataCenter and DataCenter.WorldPointManager

local function dumpTableDeep(t, indent, maxDepth)
    indent = indent or ""
    maxDepth = maxDepth or 3
    if maxDepth <= 0 or type(t) ~= "table" then return tostring(t) end
    local parts = {}
    local cnt = 0
    for k, v in pairs(t) do
        cnt = cnt + 1
        if cnt <= 20 then
            if type(v) == "table" then
                table.insert(parts, tostring(k) .. "=" .. dumpTableDeep(v, indent .. "  ", maxDepth - 1))
            else
                table.insert(parts, tostring(k) .. "=" .. tostring(v))
            end
        end
    end
    return "{" .. table.concat(parts, ", ") .. "}"
end

if mgr then
    p("=== 1. ViewLevelRange & LodRequestRange Tables ===")
    for i = 1, 10 do
        local name, val = debug.getupvalue(mgr.GetViewLevelRange, i)
        if not name then break end
        if name ~= "_ENV" then
            p("  GetViewLevelRange upval " .. name .. " = " .. dumpTableDeep(val, "", 3))
        end
    end
    for i = 1, 10 do
        local name, val = debug.getupvalue(mgr.GetLodRequestRange, i)
        if not name then break end
        if name ~= "_ENV" then
            p("  GetLodRequestRange upval " .. name .. " = " .. dumpTableDeep(val, "", 3))
        end
    end

    p("\n=== 2. Check GetViewBounds() and IsOutOfRange() ===")
    local b1, b2, b3, b4 = mgr:GetViewBounds()
    p("  mgr:GetViewBounds() = " .. dumpTableDeep(b1, "", 2) .. ", " .. tostring(b2) .. ", " .. tostring(b3) .. ", " .. tostring(b4))
    p("  mgr:IsOutOfRange(600, 600) = " .. tostring(mgr:IsOutOfRange(600, 600)))
    p("  mgr:IsOutOfRange(100, 100) = " .. tostring(mgr:IsOutOfRange(100, 100)))

    p("\n=== 3. Sample points in allViewPoints vs allObj ===")
    local typeCountsAll = {}
    local typeCountsBuilt = {}
    local sampleUnbuilt = nil
    for ptIdx, info in pairs(mgr.allViewPoints or {}) do
        local pt = info.type or info.pointType or -1
        typeCountsAll[pt] = (typeCountsAll[pt] or 0) + 1
        if mgr.allObj and mgr.allObj[ptIdx] then
            typeCountsBuilt[pt] = (typeCountsBuilt[pt] or 0) + 1
        elseif not sampleUnbuilt and (pt == 6 or pt == 4 or pt == 1 or pt == 2) then
            sampleUnbuilt = { idx = ptIdx, info = info }
        end
    end
    p("  allViewPoints by type: " .. dumpTableDeep(typeCountsAll, "", 2))
    p("  allObj (built) by type: " .. dumpTableDeep(typeCountsBuilt, "", 2))

    if sampleUnbuilt then
        local idx = sampleUnbuilt.idx
        local info = sampleUnbuilt.info
        local tx, ty = SceneUtils.IndexToTileXY(idx)
        p(string.format("  Sample unbuilt point index=%s (tile %s,%s), type=%s", tostring(idx), tostring(tx), tostring(ty), tostring(info.type)))
        p("    CheckWorldPointVisible(info) = " .. tostring(mgr:CheckWorldPointVisible(info)))
        p("    IsOutOfRange(tx, ty) = " .. tostring(mgr:IsOutOfRange(tx, ty)))
    end
end

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
""" % json.dumps(VIS_GATES_LUA)

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
