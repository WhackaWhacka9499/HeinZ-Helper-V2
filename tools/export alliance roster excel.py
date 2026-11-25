import json
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_roster_excel():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    scratch_dir = r"data/cache"
    data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip() or os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    candidates = [
        os.path.join(data_dir, "json cache", "vs33_alliance_roster.json"),
        os.path.join(data_dir, "vs33_alliance_roster.json"),
        os.path.join(base_dir, "vs33_alliance_roster.json"),
        os.path.join(scratch_dir, "vs33_alliance_roster.json"),
    ]
    json_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    out_xlsx = os.path.join(data_dir, "vs33 alliance roster.xlsx")

    if not os.path.exists(json_path):
        print(f"[-] Roster JSON not found at {json_path}")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    alliance = data.get("alliance", {})
    members = data.get("members", [])
    members.sort(key=lambda m: m.get("power") or 0, reverse=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    abbr = str(alliance.get('abbr', 'VS33')).replace('[', '').replace(']', '')
    ws.title = f"{abbr} Alliance Roster"
    ws.views.sheetView[0].showGridLines = True

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    cols = ["#", "Rank", "HQ Level", "Player Name", "Total Power", "Arena Power", "Kills", "Online", "Server", "Player UID"]
    ws.append(cols)

    for col_idx in range(1, len(cols) + 1):
        c = ws.cell(row=1, column=col_idx)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center_align

    for idx, m in enumerate(members, start=1):
        rank_str = f"R{m.get('rank')}" if m.get('rank') else "R?"
        hq = m.get("mainCityLv", 0)
        name = str(m.get("name", ""))
        power = int(m.get("power") or 0)
        arena = int(m.get("arenaPower") or 0)
        kills = int(m.get("armyKill") or 0)
        online = "Online" if m.get("online") else "Offline"
        server = str(m.get("curServerId", ""))
        uid = str(m.get("uid", ""))

        row_vals = [idx, rank_str, hq, name, f"{power:,}", f"{arena:,}", f"{kills:,}", online, server, uid]
        ws.append(row_vals)

        cur_row = idx + 1
        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=cur_row, column=col_idx)
            cell.border = thin_border
            if col_idx in (1, 2, 3, 8, 9):
                cell.alignment = center_align
            elif col_idx in (5, 6, 7):
                cell.alignment = right_align
            else:
                cell.alignment = left_align

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(out_xlsx)
    print(f"[+] Successfully exported {len(members)} alliance members to:")
    print(f"    {out_xlsx}")
    return True

if __name__ == "__main__":
    build_roster_excel()
