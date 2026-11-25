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
                local function cleanVal(v)
                    local t = type(v)
                    if t == "number" or t == "boolean" then return v end
                    if t == "string" then return v end
                    return nil
                end

                -- 1. Heroes
                local heroList = {}
                if DataCenter.HeroDataManager and DataCenter.HeroDataManager.allHero then
                    for k, h in pairs(DataCenter.HeroDataManager.allHero) do
                        if type(h) == "table" then
                            local item = {
                                id = h.id or h.heroId or k,
                                name = h.name or (h.template and h.template.name),
                                star = h.star or h.starLevel or h.curStar,
                                level = h.level or h.lv or h.curLv,
                                quality = h.quality or (h.template and h.template.quality),
                                power = h.power or h.fightpower or h.heroPower,
                                militaryRank = h.militaryRank,
                                skills = {}
                            }
                            if h.skills then
                                for sk, sv in pairs(h.skills) do
                                    if type(sv) == "table" then
                                        table.insert(item.skills, { id = sv.id or sk, lv = sv.lv or sv.level })
                                    end
                                end
                            end
                            table.insert(heroList, item)
                        end
                    end
                end

                -- 2. Armies / Troops
                local armyList = {}
                if DataCenter.ArmyManager and DataCenter.ArmyManager.allArmy then
                    for k, a in pairs(DataCenter.ArmyManager.allArmy) do
                        if type(a) == "table" then
                            table.insert(armyList, {
                                id = a.id or a.armyId or k,
                                name = a.name,
                                count = a.count or a.num or a.armyNum,
                                level = a.level or a.lv,
                                type = a.type or a.armyType
                            })
                        end
                    end
                end

                -- 3. Formations
                local formations = {}
                if DataCenter.ArmyFormationDataManager and DataCenter.ArmyFormationDataManager.ArmyFormationList then
                    for k, f in pairs(DataCenter.ArmyFormationDataManager.ArmyFormationList) do
                        if type(f) == "table" then
                            local fItem = {
                                uuid = f.uuid,
                                index = f.index,
                                power = f.power or f.fightpower,
                                heroIds = f.heroes or f.heroIds
                            }
                            table.insert(formations, fItem)
                        end
                    end
                end

                local out = {
                    heroes = heroList,
                    armies = armyList,
                    formations = formations
                }

                -- Simple JSON encode
                local function enc(val)
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
                            for i = 1, n do table.insert(parts, enc(val[i])) end
                            return "[" .. table.concat(parts, ",") .. "]"
                        else
                            local parts = {}
                            for k, v in pairs(val) do
                                table.insert(parts, string.format("%q:%s", tostring(k), enc(v)))
                            end
                            return "{" .. table.concat(parts, ",") .. "}"
                        end
                    end
                    return "null"
                end

                return enc(out)
            `;
            loadstring(L, Memory.allocUtf8String(code));
            pcall(L, 0, 1, 0);
            send({payload: getString(L, top(L))});
        } catch(e) {
            send({e: String(e)});
        } finally {
            settop(L, saved);
        }
    }
});
"""

session = frida.attach('Survival.exe')
s = session.create_script(js)
payload = None
def on_m(m, d):
    global payload
    if m['type'] == 'send':
        payload = m['payload'].get('payload')
s.on('message', on_m)
s.load()
time.sleep(1.5)
session.detach()

if payload:
    try:
        data = json.loads(payload)
        out_path = ROOT / "heinzy_military_full.json"
        tmp_path = out_path.with_name(f"{out_path.name}.{os.getpid()}.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, out_path)
        print(f"Dumped {len(data.get('heroes', []))} heroes, {len(data.get('armies', []))} army types, {len(data.get('formations', []))} formations to {out_path.name}")
    except Exception as e:
        print("JSON parse error:", e)
        print("Payload:", payload[:1000])
else:
    print("None")
