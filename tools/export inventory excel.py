import json
import os
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def export_inventory():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    scratch_dir = r"data/cache"
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    dialog_candidates = [
        os.path.join(repo_root, "launcher", "assets", "english-dialog.txt"),
        os.path.join(base_dir, "english-dialog.txt"),
        r"launcher/assets/english-dialog.txt",
    ]
    dialog_path = next((Path(p) for p in dialog_candidates if os.path.exists(p)), None)
    dialog = {}
    if dialog_path and dialog_path.exists():
        for line in dialog_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                dialog[k.strip()] = v.strip()

    fallback_names = {
        210110: "5-min Speedup",
        210112: "1-hr Speedup",
        210119: "5-min Building Speedup",
        210120: "1-hr Building Speedup",
        210122: "8-hr Building Speedup",
        210129: "1-min Speedup",
        210163: "1-hr Research Speedup",
        200210: "Transporters",
        200211: "Unlock Infantry Barracks",
        200212: "Shooter Camp",
        200213: "Unlock Tank Plant",
        200221: "Unlock Oil Refinery",
        200222: "Metal Furnace",
        200223: "Power Plant Generator",
        200230: "Food Farm Expansion",
        200231: "Water Filtration Plant",
        200232: "Gas Tank",
        200233: "Medical Station",
        200240: "Catalyst I",
        200241: "Catalyst II",
        200243: "Catalyst IV",
    }
    candidates = [
        os.path.join(data_dir, "json cache", "all_inventory_with_tpl.json"),
        os.path.join(data_dir, "all_inventory_with_tpl.json"),
        os.path.join(base_dir, "all_inventory_with_tpl.json"),
        os.path.join(scratch_dir, "all_inventory_with_tpl.json"),
    ]
    inv_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    out_xlsx = os.path.join(data_dir, "inventory reserves.xlsx")

    if not os.path.exists(inv_path):
        print(f"[-] Inventory file not found at {inv_path}")
        return False

    with open(inv_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    items = list(raw.values()) if isinstance(raw, dict) else raw
    resolved = []
    for it in items:
        name_id = str(it.get("nameId") or "")
        alt_id = str(it.get("altNameId") or "")
        item_id = str(it.get("itemId") or "")
        iid = int(item_id or 0)
        name = dialog.get(name_id) or dialog.get(alt_id) or dialog.get(item_id) or fallback_names.get(iid) or f"Item {item_id}"
        if "{0}" in name:
            param = str(it.get("param") or "").strip()
            if not param:
                if iid in (210110, 210119): param = "5"
                elif iid in (210112, 210120, 210163): param = "1"
                elif iid == 210122: param = "8"
                elif iid == 210129: param = "1"
                elif "fragment" in name.lower(): param = "Hero"
                else: param = "1"
            name = name.replace("{0}", param)
        resolved.append({
            "itemId": it.get("itemId"),
            "name": name,
            "count": it.get("count", 0),
            "type": it.get("type", 0)
        })

    resolved.sort(key=lambda x: x["count"], reverse=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bag & Reserves"
    ws.views.sheetView[0].showGridLines = True

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4B6F44", end_color="4B6F44", fill_type="solid")
    border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    cols = ["#", "Item ID", "Item Name", "Quantity", "Formatted Quantity", "Item Type"]
    ws.append(cols)

    for col_idx in range(1, len(cols) + 1):
        c = ws.cell(row=1, column=col_idx)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center_align

    for idx, r in enumerate(resolved, start=1):
        cnt = r["count"]
        row_vals = [idx, r["itemId"], r["name"], cnt, f"{cnt:,}", r["type"]]
        ws.append(row_vals)
        cur_row = idx + 1
        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=cur_row, column=col_idx)
            cell.border = thin_border
            if col_idx in (1, 2, 6):
                cell.alignment = center_align
            elif col_idx in (4, 5):
                cell.alignment = right_align
            else:
                cell.alignment = left_align

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(out_xlsx)
    print(f"[+] Successfully exported {len(resolved)} inventory items to:")
    print(f"    {out_xlsx}")
    return True

if __name__ == "__main__":
    export_inventory()
