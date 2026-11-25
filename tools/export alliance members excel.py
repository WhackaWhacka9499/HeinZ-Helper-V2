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

def build_alliance_members_excel():
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(tool_dir, ".."))
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    scratch_dir = r"data/cache"
    candidates = [
        os.path.join(data_dir, "json cache", "all_players_profile_cache.json"),
        os.path.join(data_dir, "all_players_profile_cache.json"),
        os.path.join(repo_root, "data", "json cache", "all_players_profile_cache.json"),
        os.path.join(repo_root, "data", "all_players_profile_cache.json"),
        os.path.join(scratch_dir, "all_players_profile_cache.json"),
        os.path.join(scratch_dir, "lastz_data_master", "all_players_profile_cache.json"),
    ]
    json_path = None
    for cand in candidates:
        if os.path.exists(cand):
            json_path = cand
            break
    if not json_path:
        json_path = candidates[0]
    if not os.path.exists(json_path):
        print("[-] Players cache JSON not found")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Alliance Members Master"
    ws.views.sheetView[0].showGridLines = True

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    bold_font = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
    regular_font = Font(name="Segoe UI", size=10, color="1E293B")
    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0")
    )

    headers = [
        "State", "Alliance Tag", "Alliance Name", "Player Name", 
        "Player UID", "HQ Level", "Power", "Troop Kills", "VIP Level", "Country"
    ]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    players = list(data.values()) if isinstance(data, dict) else data
    # Sort by Power descending
    players.sort(key=lambda p: int(p.get("power", 0) or 0), reverse=True)

    row_idx = 2
    for p in players:
        state_id = p.get("serverId", "")
        state_str = f"#{state_id}" if state_id else ""
        al_tag = p.get("abbr", p.get("alAbbr", ""))
        al_name = p.get("allianceName", "")
        name = p.get("name", "Unknown")
        uid = str(p.get("uid", p.get("_id", "")))
        base_lvl = p.get("baseLevel", p.get("mainBuildingLevel", 0))
        power = int(p.get("power", 0) or 0)
        kills = int(p.get("armyKill", 0) or 0)
        vip = p.get("vipLevel", "")
        flag = p.get("countryflag", p.get("countryFlag", ""))

        vals = [state_str, al_tag, al_name, name, uid, base_lvl, power, kills, vip, flag]
        for col_idx, val in enumerate(vals, start=1):
            c = ws.cell(row=row_idx, column=col_idx, value=val)
            c.font = regular_font
            c.border = thin_border
            if col_idx in [1, 2, 5, 6, 9, 10]:
                c.alignment = Alignment(horizontal="center")
            elif col_idx in [7, 8]:
                c.alignment = Alignment(horizontal="right")
                c.number_format = "#,##0"

        if row_idx % 2 == 0:
            for col_idx in range(1, 11):
                ws.cell(row=row_idx, column=col_idx).fill = alt_fill

        row_idx += 1

    # Freeze header row
    ws.freeze_panes = "A2"

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col[:100])
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    out_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Alliance Members Master.xlsx")
    wb.save(out_path)
    print(f"[+] Saved Alliance Members Excel to {out_path} ({len(players)} players)")
    return out_path

if __name__ == "__main__":
    build_alliance_members_excel()
