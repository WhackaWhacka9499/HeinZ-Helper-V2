import frida
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"data/cache")

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

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        done = true;
        const L = args[0];
        const saved = top(L);
        try {
            const code = `
                local function enc(val, depth)
                    depth = depth or 0
                    if depth > 5 then return '"[max]"' end
                    local t = type(val)
                    if t == "number" then return tostring(val) end
                    if t == "boolean" then return val and "true" or "false" end
                    if t == "string" then return string.format("%q", val) end
                    if t == "table" then
                        local isA = true
                        local n = 0
                        for k, v in pairs(val) do
                            n = n + 1
                            if type(k) ~= "number" or k <= 0 or math.floor(k) ~= k then isA = false end
                        end
                        if isA and n > 0 then
                            local parts = {}
                            for i = 1, math.min(n, 200) do table.insert(parts, enc(val[i], depth + 1)) end
                            return "[" .. table.concat(parts, ",") .. "]"
                        else
                            local parts = {}
                            local count = 0
                            for k, v in pairs(val) do
                                count = count + 1
                                if count > 200 then break end
                                table.insert(parts, string.format("%q:%s", tostring(k), enc(v, depth + 1)))
                            end
                            return "{" .. table.concat(parts, ",") .. "}"
                        end
                    end
                    return "null"
                end

                local payload = {
                    heroes = {},
                    hero_equips = {},
                    hero_sp_equips = {},
                    vehicle = {
                        car_data = {},
                        refit_info = {},
                        equipped_parts = {},
                        all_parts = {},
                        chips = {},
                        talents = {}
                    },
                    buildings = {}
                }

                -- 1. HEROES (Deep)
                if DataCenter.HeroDataManager and DataCenter.HeroDataManager.allHero then
                    for id, h in pairs(DataCenter.HeroDataManager.allHero) do
                        if type(h) == "table" then
                            local hero = {
                                id = id,
                                name = h.name or (h.template and h.template.name),
                                level = h.level or h.curLv or h.lv,
                                star = h.star or h.curStar or h.starLevel,
                                quality = h.quality or (h.template and h.template.quality),
                                power = h.power or h.fightpower or h.heroPower,
                                militaryRank = h.militaryRank,
                                fragment = h.fragment or h.debris or h.chip or h.shards or h.curChip,
                                skills = {},
                                equips = {}
                            }
                            if h.skills then
                                for skId, skVal in pairs(h.skills) do
                                    if type(skVal) == "table" then
                                        table.insert(hero.skills, {
                                            id = skVal.id or skId,
                                            level = skVal.level or skVal.lv,
                                            pos = skVal.pos or skVal.index
                                        })
                                    elseif type(skVal) == "number" then
                                        table.insert(hero.skills, { id = skId, level = skVal })
                                    end
                                end
                            end
                            table.insert(payload.heroes, hero)
                        end
                    end
                end

                -- 2. HERO EQUIPMENT
                if DataCenter.HeroEquipManager then
                    if DataCenter.HeroEquipManager.allEquip then
                        for eqId, eq in pairs(DataCenter.HeroEquipManager.allEquip) do
                            if type(eq) == "table" then
                                table.insert(payload.hero_equips, {
                                    uuid = eq.uuid or eqId,
                                    templateId = eq.templateId or eq.id,
                                    heroId = eq.heroId or eq.heroUuid,
                                    slot = eq.slot or eq.pos,
                                    level = eq.level or eq.lv,
                                    quality = eq.quality,
                                    star = eq.star or eq.curStar,
                                    power = eq.power or eq.fightpower
                                })
                            end
                        end
                    end
                    if DataCenter.HeroEquipManager.heroEquipMap then
                        payload.hero_equip_map = DataCenter.HeroEquipManager.heroEquipMap
                    end
                end

                -- 2b. HERO SP EQUIPMENT (Special Equipment)
                if DataCenter.HeroSPEquipManager and DataCenter.HeroSPEquipManager.heroSPEquipMap then
                    for hId, sp in pairs(DataCenter.HeroSPEquipManager.heroSPEquipMap) do
                        if type(sp) == "table" then
                            table.insert(payload.hero_sp_equips, {
                                heroId = hId,
                                id = sp.id or sp.templateId,
                                level = sp.level or sp.lv,
                                star = sp.star or sp.breakLv or sp.step,
                                power = sp.power
                            })
                        end
                    end
                end

                -- 3. VEHICLES / GARAGE
                if DataCenter.GarageRefitManager then
                    payload.vehicle.car_data = DataCenter.GarageRefitManager.carNewData or {}
                    payload.vehicle.refit_info = DataCenter.GarageRefitManager.garageRefitInfo or {}
                    payload.vehicle.talents = DataCenter.GarageRefitManager.talentDatas or {}
                    payload.vehicle.damage_factor = DataCenter.GarageRefitManager.skillDamageFactor
                end

                if DataCenter.GarageComponManager then
                    payload.vehicle.power = DataCenter.GarageComponManager.m_power
                    if DataCenter.GarageComponManager.m_equipParts then
                        for k, v in pairs(DataCenter.GarageComponManager.m_equipParts) do
                            if type(v) == "table" then
                                table.insert(payload.vehicle.equipped_parts, {
                                    slot = k,
                                    id = v.id or v.templateId,
                                    level = v.level or v.lv,
                                    quality = v.quality,
                                    power = v.power
                                })
                            end
                        end
                    end
                    if DataCenter.GarageComponManager.m_parts then
                        for k, v in pairs(DataCenter.GarageComponManager.m_parts) do
                            if type(v) == "table" then
                                table.insert(payload.vehicle.all_parts, {
                                    uuid = k,
                                    id = v.id or v.templateId,
                                    level = v.level or v.lv,
                                    quality = v.quality,
                                    count = v.count or v.num
                                })
                            end
                        end
                    end
                end

                if DataCenter.CarChipManager and DataCenter.CarChipManager.allChipData then
                    for k, chip in pairs(DataCenter.CarChipManager.allChipData) do
                        if type(chip) == "table" then
                            table.insert(payload.vehicle.chips, {
                                uuid = k,
                                id = chip.id or chip.templateId,
                                level = chip.level or chip.lv,
                                star = chip.star or chip.starLevel,
                                quality = chip.quality,
                                slot = chip.slot,
                                armyType = chip.armyType,
                                power = chip.power
                            })
                        end
                    end
                end

                -- 4. BUILDINGS / STRUCTURES
                if DataCenter.BuildManager and DataCenter.BuildManager.allBuilding then
                    for uuid, b in pairs(DataCenter.BuildManager.allBuilding) do
                        if type(b) == "table" then
                            table.insert(payload.buildings, {
                                uuid = uuid,
                                buildId = b.buildId or b.id or b.buildingId,
                                templateId = b.templateId or b.tplId,
                                level = b.level or b.lv,
                                name = b.name or (b.template and b.template.name),
                                state = b.state or b.status,
                                pos = b.pos or (b.grid and {x = b.grid.x, y = b.grid.y})
                            })
                        end
                    end
                end

                return enc(payload)
            `;

            const cstr = Memory.allocUtf8String(code);
            if (loadstring(L, cstr) === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const res = getString(L, -1);
                    send({status: 'ok', data: res});
                } else {
                    send({status: 'pcall_err', err: getString(L, -1)});
                }
            } else {
                send({status: 'load_err', err: getString(L, -1)});
            }
        } catch(e) {
            send({status: 'exception', err: e.toString()});
        } finally {
            settop(L, saved);
        }
    }
});
"""

session = frida.attach(33632)
script = session.create_script(js)

data_out = None
def on_message(message, data):
    global data_out
    if message['type'] == 'send':
        payload = message['payload']
        if payload.get('status') == 'ok':
            try:
                data_out = json.loads(payload['data'])
            except Exception as e:
                print("JSON decode error:", e)
                data_out = payload['data']
        else:
            print("Error payload:", payload)

script.on('message', on_message)
script.load()

for _ in range(50):
    if data_out:
        break
    time.sleep(0.1)

session.detach()

if isinstance(data_out, dict):
    out_file = ROOT / "heinzy_assets_deep_dump.json"
    out_file.write_text(json.dumps(data_out, indent=2, ensure_ascii=False), encoding='utf-8')
    print("SAVED DEEP ASSETS TO:", out_file)
    print(f"Heroes: {len(data_out.get('heroes', []))}")
    print(f"Hero Equips: {len(data_out.get('hero_equips', []))}")
    print(f"Hero SP Equips: {len(data_out.get('hero_sp_equips', []))}")
    v = data_out.get('vehicle', {})
    print(f"Vehicle Equipped Parts: {len(v.get('equipped_parts', []))}, Total Parts: {len(v.get('all_parts', []))}, Chips: {len(v.get('chips', []))}, Power: {v.get('power')}")
    print(f"Buildings: {len(data_out.get('buildings', []))}")
else:
    print("Raw output:", str(data_out)[:500])
