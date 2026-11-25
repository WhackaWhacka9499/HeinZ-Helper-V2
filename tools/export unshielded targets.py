import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
import sys

def export_unshielded_targets(min_hq=25):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    scratch_dir = r"data/cache"
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    candidates = [
        os.path.join(data_dir, "map all bases.xlsx"),
        os.path.join(data_dir, "map_all_bases.xlsx"),
        os.path.join(data_dir, "json cache", "map_all_bases.xlsx"),
        os.path.join(base_dir, "map_all_bases.xlsx"),
        os.path.join(scratch_dir, "map_all_bases.xlsx"),
    ]
    input_xlsx = next((p for p in candidates if os.path.exists(p)), candidates[0])
    output_xlsx = os.path.join(data_dir, "unshielded targets.xlsx")

    if not os.path.exists(input_xlsx):
        print(f"[-] Input file not found: {input_xlsx}. Run map intelligence export first.")
        return False

    wb_in = openpyxl.load_workbook(input_xlsx)
    ws_in = wb_in.active
    rows = list(ws_in.iter_rows(values_only=True))
    if len(rows) < 2:
        print("[-] No base data found in map_all_bases.xlsx")
        return False

    headers = rows[0]
    # Header indices: x(0), y(1), level(2), name(3), has_shield(4), shield_minutes_left(5), uid(6), alliance_id(7), point_index(8), shield_end_time(9), alliance_name(10), server_id(11), alliance_tag(12)
    unshielded = []
    for r in rows[1:]:
        has_shield = r[4]
        level = r[2]
        if not has_shield and isinstance(level, (int, float)) and level >= min_hq:
            unshielded.append({
                "level": int(level),
                "x": r[0],
                "y": r[1],
                "name": str(r[3] or "Unknown"),
                "alliance": str(r[12] or r[10] or "None"),
                "server": str(r[11] or ""),
                "uid": str(r[6] or "")
            })

    # Sort descending by HQ level, then by alliance
    unshielded.sort(key=lambda x: (x["level"], x["alliance"]), reverse=True)

    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = f"Unshielded HQ {min_hq}+"
    ws_out.views.sheetView[0].showGridLines = True

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    cols = ["HQ Level", "X Coord", "Y Coord", "Target Name", "Alliance Tag", "Server ID", "Player UID"]
    ws_out.append(cols)

    for col_idx in range(1, len(cols) + 1):
        cell = ws_out.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    for r_idx, target in enumerate(unshielded, start=1):
        row_vals = [
            target["level"],
            target["x"],
            target["y"],
            target["name"],
            target["alliance"],
            target["server"],
            target["uid"]
        ]
        ws_out.append(row_vals)
        cur_row = r_idx + 1
        for col_idx in range(1, len(row_vals) + 1):
            c = ws_out.cell(row=cur_row, column=col_idx)
            c.border = thin_border
            if col_idx in (1, 2, 3, 5, 6):
                c.alignment = center_align
            else:
                c.alignment = left_align

    for col in ws_out.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_out.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb_out.save(output_xlsx)
    print(f"[+] Successfully exported {len(unshielded)} unshielded bases (HQ {min_hq}+) to:")
    print(f"    {output_xlsx}")
    return True

if __name__ == "__main__":
    hq_arg = int(sys.argv[1]) if len(sys.argv) > 1 and str(sys.argv[1]).lstrip("-").isdigit() else 25
    export_unshielded_targets(hq_arg)
