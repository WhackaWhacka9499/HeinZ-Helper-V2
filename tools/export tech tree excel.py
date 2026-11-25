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

def build_tech_tree_excel():
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(tool_dir, ".."))
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    scratch_dir = r"data/cache"
    candidates = [
        os.path.join(data_dir, "json cache", "heinzy_tech_tree_progress.json"),
        os.path.join(data_dir, "heinzy_tech_tree_progress.json"),
        os.path.join(repo_root, "data", "json cache", "heinzy_tech_tree_progress.json"),
        os.path.join(repo_root, "data", "heinzy_tech_tree_progress.json"),
        os.path.join(scratch_dir, "lastz_data_master", "heinzy_tech_tree_progress.json"),
        os.path.join(scratch_dir, "heinzy_tech_tree_progress.json"),
    ]
    json_path = None
    for cand in candidates:
        if os.path.exists(cand):
            json_path = cand
            break
    if not json_path:
        json_path = candidates[0]
    if not os.path.exists(json_path):
        print("[-] Tech tree JSON not found")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = openpyxl.Workbook()
    
# - Styling Palette (Clean Google Sheets dark/neutral professional)
    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
    accent_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    alt_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Segoe UI", size=14, bold=True, color="111827")
    sub_font = Font(name="Segoe UI", size=10, italic=True, color="6B7280")
    bold_font = Font(name="Segoe UI", size=10, bold=True, color="111827")
    regular_font = Font(name="Segoe UI", size=10, color="1F2937")
    thin_border = Border(
        left=Side(style="thin", color="E5E7EB"),
        right=Side(style="thin", color="E5E7EB"),
        top=Side(style="thin", color="E5E7EB"),
        bottom=Side(style="thin", color="E5E7EB")
    )

    # Sheet 1: Overview & Laboratory Summary
    ws_sum = wb.active
    ws_sum.title = "Laboratory Overview"
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "HEINZY - LABORATORY & TECH TREE INTELLIGENCE"
    ws_sum["A1"].font = title_font
    ws_sum["A2"] = "Exported from Live Client Research State"
    ws_sum["A2"].font = sub_font

    lab = data.get("laboratory_summary", {})
    s1 = data.get("season_1_mastery", {})

    metrics = [
        ("Overall Laboratory Completion", f"{lab.get('overall_laboratory_progress_percentage', 0)}%"),
        ("Researched Technologies", f"{lab.get('total_technologies_researched', 0)} nodes"),
        ("Active Research Trees", f"{lab.get('total_active_tech_trees', 0)} trees"),
        ("Completed Research Levels", f"{lab.get('overall_levels_completed', 0)} / {lab.get('overall_levels_maximum', 0)}"),
        ("Fully Maxed (100%) Trees", f"{lab.get('trees_100_percent_maxed_count', 0)} trees"),
        ("Season 1 Mastery Level", f"Level {s1.get('level', 0)}"),
        ("Stored Mastery EXP", f"{s1.get('stored_exp', 0):,} EXP"),
        ("Mastery Status", s1.get("status", "Active"))
    ]

    ws_sum["A4"] = "RESEARCH METRIC"
    ws_sum["B4"] = "CURRENT STATUS"
    ws_sum["A4"].fill = accent_fill
    ws_sum["B4"].fill = accent_fill
    ws_sum["A4"].font = header_font
    ws_sum["B4"].font = header_font
    ws_sum["A4"].alignment = Alignment(horizontal="left", vertical="center")
    ws_sum["B4"].alignment = Alignment(horizontal="center", vertical="center")

    for i, (k, v) in enumerate(metrics, start=5):
        ws_sum[f"A{i}"] = k
        ws_sum[f"B{i}"] = v
        ws_sum[f"A{i}"].font = bold_font
        ws_sum[f"B{i}"].font = regular_font
        ws_sum[f"A{i}"].border = thin_border
        ws_sum[f"B{i}"].border = thin_border
        ws_sum[f"B{i}"].alignment = Alignment(horizontal="center")
        if i % 2 == 0:
            ws_sum[f"A{i}"].fill = alt_fill
            ws_sum[f"B{i}"].fill = alt_fill

    # Sheet 2: All Research Trees Detail
    ws_trees = wb.create_sheet(title="All Research Trees")
    ws_trees.views.sheetView[0].showGridLines = True

    headers = ["Tree Name", "Technology Name", "Current Level", "Max Level", "Completion", "Status"]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws_trees.cell(row=1, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    trees = data.get("trees", {})
    row_idx = 2
    if isinstance(trees, dict):
        for tree_name, tree_data in trees.items():
            if isinstance(tree_data, dict):
                skills = tree_data.get("skills", tree_data.get("technologies", {}))
                if isinstance(skills, dict):
                    for tech_name, tech_info in skills.items():
                        cur_lvl = tech_info.get("level", 0) if isinstance(tech_info, dict) else tech_info
                        max_lvl = tech_info.get("max_level", 10) if isinstance(tech_info, dict) else 10
                        pct = f"{(cur_lvl / max_lvl * 100):.1f}%" if max_lvl > 0 else "N/A"
                        status = "MAXED" if cur_lvl >= max_lvl else f"{cur_lvl}/{max_lvl}"

                        vals = [tree_name, tech_name, cur_lvl, max_lvl, pct, status]
                        for c_idx, val in enumerate(vals, start=1):
                            c = ws_trees.cell(row=row_idx, column=c_idx, value=val)
                            c.font = regular_font
                            c.border = thin_border
                            if c_idx in [3, 4, 5, 6]:
                                c.alignment = Alignment(horizontal="center")
                        if row_idx % 2 == 0:
                            for c_idx in range(1, 7):
                                ws_trees.cell(row=row_idx, column=c_idx).fill = alt_fill
                        row_idx += 1
                else:
                    # Flat summary of tree
                    cur_lvl = tree_data.get("completed_levels", 0)
                    max_lvl = tree_data.get("max_levels", 0)
                    pct = f"{tree_data.get('progress_percentage', 0)}%"
                    status = "MAXED" if cur_lvl >= max_lvl and max_lvl > 0 else f"{cur_lvl}/{max_lvl}"
                    vals = [tree_name, "Tree Master", cur_lvl, max_lvl, pct, status]
                    for c_idx, val in enumerate(vals, start=1):
                        c = ws_trees.cell(row=row_idx, column=c_idx, value=val)
                        c.font = regular_font
                        c.border = thin_border
                    row_idx += 1

    # Auto-adjust column widths
    for ws in [ws_sum, ws_trees]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    out_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Tech Tree Progress.xlsx")
    wb.save(out_path)
    print(f"[+] Saved Tech Tree Excel to {out_path}")
    return out_path

if __name__ == "__main__":
    build_tech_tree_excel()