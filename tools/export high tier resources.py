import csv
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def export_high_tier_resources(min_level=6):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    scratch_dir = r"data/cache"
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    candidates = [
        os.path.join(data_dir, "map all resources.csv"),
        os.path.join(data_dir, "map_all_resources.csv"),
        os.path.join(data_dir, "json cache", "map_all_resources.csv"),
        os.path.join(base_dir, "map_all_resources.csv"),
        os.path.join(scratch_dir, "map_all_resources.csv"),
    ]
    input_csv = next((p for p in candidates if os.path.exists(p)), candidates[0])
    out_xlsx = os.path.join(data_dir, "high tier resources.xlsx")

    if not os.path.exists(input_csv):
        print(f"[-] map_all_resources.csv not found at {input_csv}")
        return False

    nodes = []
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rid = int(row.get("resource_id", 0))
                lvl = rid % 10
            except ValueError:
                lvl = 0
            if lvl >= min_level:
                nodes.append({
                    "level": lvl,
                    "x": int(row.get("x", 0)),
                    "y": int(row.get("y", 0)),
                    "type": str(row.get("resource_type", "")).capitalize(),
                    "name": str(row.get("name", "")),
                    "amount": int(row.get("total_amount", 0) or 0)
                })

    nodes.sort(key=lambda n: (n["level"], n["type"]), reverse=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Lvl {min_level}-8 Resource Mines"
    ws.views.sheetView[0].showGridLines = True

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    cols = ["Node Level", "Resource Type", "X Coord", "Y Coord", "Total Yield", "Name"]
    ws.append(cols)

    for col_idx in range(1, len(cols) + 1):
        c = ws.cell(row=1, column=col_idx)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center_align

    for idx, n in enumerate(nodes, start=1):
        row_vals = [
            n["level"],
            n["type"],
            n["x"],
            n["y"],
            f"{n['amount']:,}" if n['amount'] > 0 else "Full",
            n["name"]
        ]
        ws.append(row_vals)
        cur_row = idx + 1
        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=cur_row, column=col_idx)
            cell.border = thin_border
            if col_idx in (1, 2, 3, 4):
                cell.alignment = center_align
            elif col_idx == 5:
                cell.alignment = right_align
            else:
                cell.alignment = left_align

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(out_xlsx)
    print(f"[+] Successfully exported {len(nodes)} high-tier mines (Lvl {min_level}+) to:")
    print(f"    {out_xlsx}")
    return True

if __name__ == "__main__":
    export_high_tier_resources(6)
