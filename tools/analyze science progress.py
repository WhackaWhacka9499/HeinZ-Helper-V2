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

# Load science dump (tabs)
sci_dump = json.loads((ROOT / "heinzy_science_dump.json").read_text(encoding="utf-8"))
tabs = sci_dump.get("tabs", {})

# Load full templates and user science
full_dump = json.loads((ROOT / "science_tpls_and_user.json").read_text(encoding="utf-8"))
tpls = full_dump.get("tpls", {})
user_sci = full_dump.get("userSci", {})

# Resolve tab names
resolved_tabs = {}
for tid, t in tabs.items():
    name_id = str(t.get("name") or "")
    tab_name = dialog.get(name_id, f"Tree_{tid}")
    resolved_tabs[str(tid)] = {
        "id": int(tid),
        "name": tab_name,
        "order": t.get("order", 999),
        "techs": []
    }

# Process each user science
total_levels_done = 0
total_levels_max = 0

for sid, us in user_sci.items():
    cur_lv = us.get("level", 0)
    tpl = tpls.get(str(sid)) or {}
    tab_id = str(us.get("tabId") or tpl.get("tabId") or "")
    
    # Resolve science name
    name_id = str(us.get("nameId") or tpl.get("nameId") or "")
    line = tpl.get("line") or {}
    
    sci_name = dialog.get(name_id)
    if not sci_name and line:
        for lk, lv in line.items():
            if str(lv) in dialog and len(str(lv)) == 6:
                sci_name = dialog[str(lv)]
                break
    if not sci_name:
        sci_name = dialog.get(str(sid), f"Tech_{sid}")
        
    max_lv = tpl.get("maxLv") or 10
    
    total_levels_done += cur_lv
    total_levels_max += max_lv
    
    tech_info = {
        "id": sid,
        "name": sci_name,
        "level": cur_lv,
        "maxLevel": max_lv,
        "isMax": cur_lv >= max_lv
    }
    
    if tab_id in resolved_tabs:
        resolved_tabs[tab_id]["techs"].append(tech_info)
    else:
        if "other" not in resolved_tabs:
            resolved_tabs["other"] = {"id": 999, "name": "General / Other", "order": 999, "techs": []}
        resolved_tabs["other"]["techs"].append(tech_info)

# Sort tabs by order
sorted_tabs = sorted([t for t in resolved_tabs.values() if t["techs"]], key=lambda x: x["order"])

print(f"=== SCIENCE / TECH TREE PROGRESS ===")
print(f"Total Researched Technologies: {len(user_sci)}")
print(f"Total Tech Levels Researched: {total_levels_done} levels")
print(f"Active Tech Trees with Progress: {len(sorted_tabs)}\n")

for t in sorted_tabs:
    techs = t["techs"]
    maxed = sum(1 for x in techs if x["isMax"])
    tree_done = sum(x["level"] for x in techs)
    tree_max = sum(x["maxLevel"] for x in techs)
    pct = (tree_done / tree_max * 100) if tree_max > 0 else 0
    print(f"[{t['name']}] - Progress: {pct:.1f}% ({maxed}/{len(techs)} Techs Maxed, {tree_done}/{tree_max} Levels)")
    for tech in sorted(techs, key=lambda x: x["level"], reverse=True)[:6]:
        status = "MAX" if tech["isMax"] else f"{tech['level']}/{tech['maxLevel']}"
        print(f"   • {tech['name']}: Lv {status}")
    if len(techs) > 6:
        print(f"   ... and {len(techs) - 6} more techs")
    print()
