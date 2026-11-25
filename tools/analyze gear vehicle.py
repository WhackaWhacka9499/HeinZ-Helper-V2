import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

dump_path = Path(r"data/cache/heinzy_assets_deep_dump.json")
data = json.loads(dump_path.read_text(encoding="utf-8"))

from resolve_all_heroes import resolved_heroes
hero_names = {h["heroId"]: h["name"] for h in resolved_heroes}

equips = data.get("hero_equips", [])
print(f"Total Equipment items: {len(equips)}")

equipped_by_hero = {}
unequipped = []
for eq in equips:
    hid = eq.get("heroId")
    if hid and hid != 0:
        if hid not in equipped_by_hero:
            equipped_by_hero[hid] = []
        equipped_by_hero[hid].append(eq)
    else:
        unequipped.append(eq)

print(f"Equipped on heroes: {sum(len(v) for v in equipped_by_hero.values())} pieces across {len(equipped_by_hero)} heroes")
print(f"In Bag / Unequipped: {len(unequipped)} pieces")

print("\n--- HERO EQUIPPED GEAR BREAKDOWN ---")
slot_names = {1: "Weapon", 2: "Armor", 3: "Radar", 4: "Core"}
for hid, eq_list in sorted(equipped_by_hero.items(), key=lambda x: max(e["level"] for e in x[1]), reverse=True):
    hname = hero_names.get(hid, f"Hero_{hid}")
    parts = []
    for e in sorted(eq_list, key=lambda x: x.get("slot", 0)):
        s_name = slot_names.get(e.get("slot"), f"Slot_{e.get('slot')}")
        parts.append(f"{s_name}: Lv {e.get('level')}")
    details = ", ".join(parts)
    print(f"[{hid}] {hname}: {details}")

print("\n--- VEHICLE CHIPS BREAKDOWN ---")
chips = data.get("vehicle", {}).get("chips", [])
from collections import Counter
qual_counts = Counter(c.get("quality") for c in chips)
print(f"Total chips: {len(chips)}")
for q, cnt in sorted(qual_counts.items(), key=lambda x: str(x[0]), reverse=True):
    print(f"  Quality {q}: {cnt} chips")
high_chips = [c for c in chips if (c.get("quality") or 0) >= 4 or (c.get("level") or 0) > 1]
print(f"\nHigh-tier / Upgraded chips: {len(high_chips)}")
for c in high_chips[:15]:
    slot_label = slot_names.get(c.get("slot"), f"Slot {c.get('slot')}")
    print(f"  Chip ID {c.get('id')} | {slot_label} | ArmyType: {c.get('armyType')} | Quality: {c.get('quality')} | Star: {c.get('star')} | Lv: {c.get('level')}")
