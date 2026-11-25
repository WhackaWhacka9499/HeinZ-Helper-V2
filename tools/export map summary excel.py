import json
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def build_map_summary_excel():
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(tool_dir, ".."))
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    scratch_dir = r"data/cache"
    candidates = [
        os.path.join(data_dir, "json cache", "map_intelligence_summary.json"),
        os.path.join(data_dir, "map_intelligence_summary.json"),
        os.path.join(repo_root, "data", "json cache", "map_intelligence_summary.json"),
        os.path.join(repo_root, "data", "map_intelligence_summary.json"),
        os.path.join(scratch_dir, "map_intelligence_summary.json"),
    ]
    json_path = None
    for cand in candidates:
        if os.path.exists(cand):
            json_path = cand
            break
    if not json_path:
        json_path = candidates[0]
    if not os.path.exists(json_path):
        print("[-] Map summary JSON not found")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Map Intelligence Summary"
    ws.views.sheetView[0].showGridLines = True

    header_fill = PatternFill(start_color="047857", end_color="047857", fill_type="solid")
    alt_fill = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Segoe UI", size=14, bold=True, color="065F46")
    sub_font = Font(name="Segoe UI", size=10, italic=True, color="6B7280")
    bold_font = Font(name="Segoe UI", size=10, bold=True, color="111827")
    regular_font = Font(name="Segoe UI", size=10, color="1F2937")
    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB")
    )

    ws["A1"] = "LAST Z - FULL MAP STRATEGIC SUMMARY"
    ws["A1"].font = title_font
    ws["A2"] = f"Scan Timestamp: {data.get('timestamp', 'N/A')}"
    ws["A2"].font = sub_font

    metrics = [
        ("Total Player Bases Discovered", f"{data.get('total_bases', 0):,} bases"),
        ("Shielded (Protected) Bases", f"{data.get('shielded_bases', 0):,} bases"),
        ("Unshielded Targets (Vulnerable)", f"{data.get('unshielded_bases', 0):,} bases"),
        ("Total Resource Mines & Nodes", f"{data.get('total_resource_nodes', 0):,} nodes"),
        ("Total Wandering Monsters & Bosses", f"{data.get('total_monsters', 0):,} entities")
    ]

    ws["A4"] = "STRATEGIC MAP METRIC"
    ws["B4"] = "SCAN VALUE"
    ws["A4"].fill = header_fill
    ws["B4"].fill = header_fill
    ws["A4"].font = header_font
    ws["B4"].font = header_font
    ws["A4"].alignment = Alignment(horizontal="left", vertical="center")
    ws["B4"].alignment = Alignment(horizontal="center", vertical="center")

    for i, (k, v) in enumerate(metrics, start=5):
        ws[f"A{i}"] = k
        ws[f"B{i}"] = v
        ws[f"A{i}"].font = bold_font
        ws[f"B{i}"].font = regular_font
        ws[f"A{i}"].border = thin_border
        ws[f"B{i}"].border = thin_border
        ws[f"B{i}"].alignment = Alignment(horizontal="center")
        if i % 2 == 0:
            ws[f"A{i}"].fill = alt_fill
            ws[f"B{i}"].fill = alt_fill

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    out_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Map Intelligence Summary.xlsx")
    wb.save(out_path)
    print(f"[+] Saved Map Summary Excel to {out_path}")
    return out_path

if __name__ == "__main__":
    build_map_summary_excel()
