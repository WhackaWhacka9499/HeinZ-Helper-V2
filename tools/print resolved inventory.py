import json
from pathlib import Path

dialog_path = Path(r"launcher/assets/english-dialog.txt")
dialog = {}
for line in dialog_path.read_text(encoding="utf-8", errors="ignore").splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        dialog[k.strip()] = v.strip()

inv_path = Path(r"data/cache/all_inventory_with_tpl.json")
raw = json.loads(inv_path.read_text(encoding="utf-8"))
items = list(raw.values()) if isinstance(raw, dict) else raw

resolved = []
for it in items:
    name_id = str(it.get("nameId") or "")
    alt_id = str(it.get("altNameId") or "")
    item_id = str(it.get("itemId") or "")
    
    name = dialog.get(name_id) or dialog.get(alt_id) or dialog.get(item_id) or f"Item_{item_id}"
    resolved.append({
        "itemId": it.get("itemId"),
        "name": name,
        "count": it.get("count"),
        "type": it.get("type"),
        "quality": it.get("quality")
    })

# Sort by count desc
resolved.sort(key=lambda x: x["count"], reverse=True)

print(f"Total resolved items: {len(resolved)}")
for r in resolved[:35]:
    print(f"[{r['itemId']}] {r['name']} - Count: {r['count']:,} (Type: {r['type']}, Q: {r['quality']})")
