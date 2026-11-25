import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"data/cache")

# Load english dialog
dialog_path = Path(r"launcher/assets/english-dialog.txt")
dialog = {}
for line in dialog_path.read_text(encoding="utf-8", errors="ignore").splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        dialog[k.strip()] = v.strip()

# Load tabs
sci_dump = json.loads((ROOT / "heinzy_science_dump.json").read_text(encoding="utf-8"))
tabs = sci_dump.get("tabs", {})

# Load resolved sciences
user_sci = json.loads((ROOT / "heinzy_user_science_resolved.json").read_text(encoding="utf-8"))

# Build tab container
tab_map = {}
for tid, t in tabs.items():
    name_id = str(t.get("name") or "")
    tab_name = dialog.get(name_id, f"Tree_{tid}")
    tab_map[str(tid)] = {
        "id": int(tid),
        "name": tab_name,
        "order": t.get("order", 999),
        "techs": []
    }

unassigned = []
for sid, s in user_sci.items():
    tab_id = str(s.get("tabId") or "")
    name_id = str(s.get("nameId") or "")
    tech_name = dialog.get(name_id, f"Tech_{sid}")
    
    cur_lv = int(s.get("level") or 0)
    max_lv = int(s.get("maxLv") or 10)
    
    tech_item = {
        "id": sid,
        "name": tech_name,
        "level": cur_lv,
        "maxLevel": max_lv,
        "isMax": cur_lv >= max_lv
    }
    
    if tab_id in tab_map:
        tab_map[tab_id]["techs"].append(tech_item)
    else:
        unassigned.append(tech_item)

sorted_trees = sorted([t for t in tab_map.values() if t["techs"]], key=lambda x: x["order"])

print(f"=== FULL TECH TREE BREAKDOWN (LABORATORY) ===")
print(f"Total Researched Technologies: {len(user_sci)}")
print(f"Active Tech Trees Researched: {len(sorted_trees)}")
if unassigned:
    print(f"Unassigned techs: {len(unassigned)}")

total_levels_done = 0
total_levels_max = 0

for t in sorted_trees:
    techs = t["techs"]
    maxed = sum(1 for x in techs if x["isMax"])
    tree_done = sum(x["level"] for x in techs)
    tree_max = sum(x["maxLevel"] for x in techs)
    pct = (tree_done / tree_max * 100) if tree_max > 0 else 0
    total_levels_done += tree_done
    total_levels_max += tree_max
    
    print(f"\n[DIR] [{t['name']}] - Progress: {pct:.1f}% ({maxed}/{len(techs)} Maxed | {tree_done}/{tree_max} Levels)")
    for tech in sorted(techs, key=lambda x: (x["isMax"], x["level"]), reverse=True):
        status = f"Lv {tech['level']}/{tech['maxLevel']}" + (" (MAX)" if tech["isMax"] else "")
        print(f"   • {tech['name']}: {status}")

print(f"\nOverall Laboratory Progress: {total_levels_done}/{total_levels_max} levels ({(total_levels_done/total_levels_max*100):.1f}%)")
