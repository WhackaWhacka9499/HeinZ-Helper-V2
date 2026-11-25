import frida
import json
import time
import os
import csv
from datetime import datetime

LUA_EXPORT = r"""
local mgr = DataCenter and DataCenter.WorldPointManager
if not mgr then return '{"error": "no mgr"}' end

local now = os.time()
local bases = {}
local resources = {}
local monsters = {}
local seasonal = {}

for k, obj in pairs(mgr.allObj or {}) do
    local pType = obj.pointType or (obj.GetPointType and obj:GetPointType())
    local px, py = SceneUtils.IndexToTileXY(obj.pointIndex)
    local info = mgr:GetPointInfo(obj.pointIndex)
    local cname = obj._class_type and obj._class_type.__cname or ""
    
    -- Player Base (pType == 6 or WorldBuildObject)
    if pType == 6 or cname == "WorldBuildObject" then
        local bi = info and info.buildInfo
        local bid = (mgr._GetBuildIdForFactory and mgr:_GetBuildIdForFactory(obj)) or (bi and bi.buildId) or 0
        local isSmall = (mgr.IsSmallBuild and bid and mgr:IsSmallBuild(bid)) or false
        
        -- If it's a seasonal structure / alliance tile mapped under WorldBuildObject
        if isSmall or (bi and (bi.isSeasonBuild or bi.seasonType or bi.allianceBuildingId or bi.buildingType == 11 or bi.buildingType == 15)) then
            table.insert(seasonal, {
                point_index = obj.pointIndex,
                x = px,
                y = py,
                name = bi and (bi.name or bi.buildingName or bi.nickName) or "Seasonal Structure",
                build_id = bid,
                level = bi and bi.level or 0,
                alliance_id = bi and tostring(bi.allianceId or "") or "",
                alliance_tag = bi and tostring(bi.alShortName or bi.alTag or "") or "",
                building_type = bi and (bi.buildingType or bi.type) or pType or 0
            })
        else
            local protectEnd = bi and bi.protectEndTime or 0
            local hasShield = (protectEnd > now)
            local shieldMinutes = hasShield and math.floor((protectEnd - now) / 60) or 0
            
            table.insert(bases, {
                point_index = obj.pointIndex,
                x = px,
                y = py,
                name = bi and (bi.name or bi.nickName) or "Unknown",
                level = bi and bi.level or 0,
                uid = bi and tostring(bi.uid or bi.ownerUid or "") or "",
                alliance_id = bi and tostring(bi.allianceId or "") or "",
                alliance_tag = bi and tostring(bi.alShortName or bi.alTag or "") or "",
                alliance_name = bi and tostring(bi.allianceName or "") or "",
                server_id = bi and (bi.srcServerId or bi.serverId) or 0,
                has_shield = hasShield,
                shield_minutes_left = shieldMinutes,
                shield_end_time = protectEnd
            })
        end
    -- Dedicated Seasonal / Alliance / Pass Structures (pType 11, 15, or seasonal building objects)
    elseif pType == 11 or pType == 15 or pType == 16 or pType == 18 or cname == "WorldCityObject" or cname == "WorldAllianceBuildObject" then
        local bi = info and (info.buildInfo or info.cityInfo or info.allianceBuildInfo)
        table.insert(seasonal, {
            point_index = obj.pointIndex,
            x = px,
            y = py,
            name = bi and (bi.name or bi.cityName or bi.buildingName) or (cname ~= "" and cname or "Alliance/City Node"),
            build_id = bi and (bi.buildId or bi.cityId) or 0,
            level = bi and bi.level or 0,
            alliance_id = bi and tostring(bi.allianceId or "") or "",
            alliance_tag = bi and tostring(bi.alShortName or bi.alTag or "") or "",
            building_type = pType or 0
        })
    -- Resource Node
    elseif pType == 1 or pType == 12 or pType == 7 or cname == "WorldResObjectInstanced" then
        local ri = info and info.resourceInfo
        local rType = "Resource"
        if ri and ri.resourceId then
            local tData = GetTableData and GetTableData(TableName.GatherResource, ri.resourceId, "resource_type")
            if tData == 1 then rType = "Metal"
            elseif tData == 2 then rType = "Wood"
            elseif tData == 12 then rType = "Electricity"
            elseif tData == 14 then rType = "Money"
            elseif tData == 15 then rType = "Gold"
            end
        end
        table.insert(resources, {
            point_index = obj.pointIndex,
            x = px,
            y = py,
            resource_type = rType,
            resource_id = ri and ri.resourceId or 0,
            level = ri and ri.level or 0,
            remaining_amount = ri and (ri.remainNum or ri.num) or 0
        })
    -- Monsters
    elseif pType == 4 or cname == "WorldMonsterObject" then
        local mi = info and info.monsterInfo
        table.insert(monsters, {
            point_index = obj.pointIndex,
            x = px,
            y = py,
            monster_id = mi and mi.monsterId or 0,
            level = mi and mi.level or 0
        })
    end
end

-- Pure Lua JSON Encoder with safe string escaping (strips \r, \n, \t and escapes quotes/backslashes)
local function escapeStr(s)
    if s == nil then return '""' end
    local str = tostring(s)
    str = str:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\r', ' '):gsub('\n', ' '):gsub('\t', ' ')
    return '"' .. str .. '"'
end

local function toJson(val)
    local t = type(val)
    if t == "number" or t == "boolean" then
        return tostring(val)
    elseif t == "string" then
        return escapeStr(val)
    elseif t == "table" then
        local isArray = (#val > 0)
        local parts = {}
        if isArray then
            for i = 1, #val do
                table.insert(parts, toJson(val[i]))
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            for k, v in pairs(val) do
                table.insert(parts, string.format("%s:%s", escapeStr(k), toJson(v)))
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    else
        return "null"
    end
end

local result = {
    total_objects = #(mgr.allObj or {}),
    bases_count = #bases,
    resources_count = #resources,
    monsters_count = #monsters,
    seasonal_count = #seasonal,
    bases = bases,
    resources = resources,
    monsters = monsters,
    seasonal = seasonal
}

return toJson(result)
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
            const loadErr = loadstring(L, s);
            if (loadErr === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const ret = getString(L, -1);
                    send({ type: 'result', data: ret });
                } else {
                    const err = getString(L, -1);
                    send({ type: 'error', data: err });
                }
            } else {
                const syntaxErr = getString(L, -1);
                send({ type: 'error', data: 'Syntax error: ' + syntaxErr });
            }
        } catch(e) {
            send({ type: 'error', data: e.toString() });
        } finally {
            settop(L, saved);
        }
    }
});
""" % json.dumps(LUA_EXPORT)

def _resolve_target_pid(explicit_pid=None):
    if explicit_pid is not None:
        try:
            return int(explicit_pid)
        except (ValueError, TypeError):
            pass
    env_pid = os.environ.get("LASTZ_TARGET_PID", "").strip()
    if env_pid.isdigit():
        return int(env_pid)
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cd_path = os.path.join(base_dir, "client discovery.py")
        if os.path.exists(cd_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("cd_mod", cd_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            resolved = mod.resolve_target_pid()
            if resolved:
                return resolved
    except Exception:
        pass
    import psutil
    for p in psutil.process_iter(['pid', 'name']):
        if (p.info.get('name') or '').lower() in ('survival.exe', 'farmgame.exe', 'alt2game.exe', 'alt3game.exe'):
            return p.info['pid']
    return None


def main():
    target_pid = _resolve_target_pid()
    if not target_pid:
        print("[-] Last Z process not found (start Last Z PC first)")
        return
    session = frida.attach(target_pid)
    script = session.create_script(FRIDA_JS)
    res = []
    script.on('message', lambda m, d: res.append(m))
    script.load()
    for _ in range(40):
        if res: break
        time.sleep(0.1)
    session.detach()

    if not res:
        print("[-] Timeout waiting for data export")
        return

    payload = res[0].get('payload', {})
    if res[0].get('type') == 'error' or payload.get('type') == 'error':
        print(f"[-] Error: {payload.get('data') or res[0]}")
        return

    data_str = payload.get('data')
    data = json.loads(data_str)
    
    bases = data.get('bases', [])
    resources = data.get('resources', [])
    monsters = data.get('monsters', [])
    seasonal = data.get('seasonal', [])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    out_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(out_dir, exist_ok=True)
    bases_csv = os.path.join(out_dir, "map_all_bases.csv")
    resources_csv = os.path.join(out_dir, "map_all_resources.csv")
    seasonal_csv = os.path.join(out_dir, "map_all_seasonal_structures.csv")
    summary_json = os.path.join(out_dir, "map_intelligence_summary.json")

    # Load existing bases if present to maintain an accumulated distinct base ledger
    distinct_bases = {}
    if os.path.exists(bases_csv):
        try:
            with open(bases_csv, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row.get("uid") or f"{row.get('x')}_{row.get('y')}"
                    if key:
                        distinct_bases[key] = row
        except Exception:
            pass

    # Merge freshly scanned bases into distinct ledger (latest scan updates coordinates/shields)
    for b in bases:
        key = str(b.get("uid") or "").strip() or f"{b.get('x')}_{b.get('y')}"
        if key:
            distinct_bases[key] = b

    all_bases = list(distinct_bases.values()) if distinct_bases else bases

    # Load existing seasonal structures if present
    distinct_seasonal = {}
    if os.path.exists(seasonal_csv):
        try:
            with open(seasonal_csv, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skey = f"{row.get('x')}_{row.get('y')}_{row.get('build_id', '')}"
                    distinct_seasonal[skey] = row
        except Exception:
            pass
    for s in seasonal:
        skey = f"{s.get('x')}_{s.get('y')}_{s.get('build_id', '')}"
        distinct_seasonal[skey] = s
    all_seasonal = list(distinct_seasonal.values()) if distinct_seasonal else seasonal

    # Write Bases CSV (accumulated distinct bases)
    if all_bases:
        keys = list(all_bases[0].keys())
        with open(bases_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_bases)

    # Write Seasonal CSV
    if all_seasonal:
        skeys = list(all_seasonal[0].keys())
        with open(seasonal_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=skeys)
            writer.writeheader()
            writer.writerows(all_seasonal)

    # Write Resources CSV
    if resources:
        rkeys = list(resources[0].keys())
        with open(resources_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=rkeys)
            writer.writeheader()
            writer.writerows(resources)

    # Summary
    shielded_count = sum(1 for b in all_bases if str(b.get('has_shield', '')).lower() in ('true', '1'))
    unshielded_count = len(all_bases) - shielded_count
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_bases": len(all_bases),
        "viewport_bases": len(bases),
        "shielded_bases": shielded_count,
        "unshielded_bases": unshielded_count,
        "total_seasonal_structures": len(all_seasonal),
        "total_resource_nodes": len(resources),
        "total_monsters": len(monsters)
    }
    tmp_summary_json = f"{summary_json}.{os.getpid()}.tmp"
    with open(tmp_summary_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp_summary_json, summary_json)

    print(f"[+] Successfully exported Map Intelligence:")
    print(f"    - Bases: {len(all_bases)} accumulated distinct ({len(bases)} in current viewport, {shielded_count} shielded, {unshielded_count} unshielded) -> {bases_csv}")
    print(f"    - Seasonal/Alliance: {len(all_seasonal)} structures -> {seasonal_csv}")
    print(f"    - Resources: {len(resources)} nodes -> {resources_csv}")
    print(f"    - Monsters: {len(monsters)} -> {summary_json}")
    print(f"    - Monsters: {len(monsters)} -> {summary_json}")

if __name__ == '__main__':
    main()
