import json
import os
import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"data/cache")
DATA_DIR = ROOT / "bracket_data"
XLSX_DIR = ROOT / "bracket_xlsx"
XLSX_DIR.mkdir(parents=True, exist_ok=True)

BRACKET_STATES = list(range(689, 704)) # 689 to 703

# Color Palette
DARK_NAVY = "1B365D"
ACCENT_BLUE = "2A5C9A"
ICE_HEADER = "F1F5F9"
CARD_BG = "F8FAFC"
BORDER_GRAY = "E2E8F0"
BORDER_MED = "CBD5E1"

ADV_BG = "E6E6FA"       # Lavender / Light Purple
MID_BG = "E0F2FE"       # Light Ice Blue
REG_BG = "F0FDF4"       # Light Green
ELITE_BG = "FCE7F3"     # Light Pink

font_title = Font(name="Segoe UI", size=15, bold=True, color="FFFFFF")
font_subtitle = Font(name="Segoe UI", size=9.5, italic=True, color="E2E8F0")
font_sec_hdr = Font(name="Segoe UI", size=11, bold=True, color="1B365D")
font_table_hdr = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
font_sub_hdr = Font(name="Segoe UI", size=9.5, bold=True, color="334155")
font_data = Font(name="Segoe UI", size=9.5)
font_bold_data = Font(name="Segoe UI", size=9.5, bold=True)
font_num_data = Font(name="Segoe UI", size=9.5)
font_card_num = Font(name="Segoe UI", size=14, bold=True, color="1B365D")
font_card_lbl = Font(name="Segoe UI", size=8.5, bold=True, color="64748B")

fill_title = PatternFill(start_color=DARK_NAVY, end_color=DARK_NAVY, fill_type="solid")
fill_hdr = PatternFill(start_color=ACCENT_BLUE, end_color=ACCENT_BLUE, fill_type="solid")
fill_sub_hdr = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_adv = PatternFill(start_color=ADV_BG, end_color=ADV_BG, fill_type="solid")
fill_mid = PatternFill(start_color=MID_BG, end_color=MID_BG, fill_type="solid")
fill_reg = PatternFill(start_color=REG_BG, end_color=REG_BG, fill_type="solid")
fill_elite = PatternFill(start_color=ELITE_BG, end_color=ELITE_BG, fill_type="solid")
fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
fill_card = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")

thin_border_side = Side(style='thin', color=BORDER_GRAY)
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
med_bottom = Border(bottom=Side(style='medium', color=ACCENT_BLUE))
double_bottom = Border(bottom=Side(style='double', color=DARK_NAVY), top=Side(style='thin', color=BORDER_MED))

def get_tier_and_passes(migrate_power):
    if migrate_power is None or migrate_power == 0:
        return ("Unknown", 0)
    if migrate_power <= 20000000:
        return ("Regular (Che1)", 10)
    elif migrate_power <= 35000000:
        return ("Mid (Che2)", 20)
    elif migrate_power <= 50000000:
        return ("Advanced (Che3)", 35)
    else:
        return ("Elite (Che4)", 50)

def role_str(rank_val):
    role_map = {1: 'R1', 2: 'R2', 3: 'R3', 4: 'R4', 5: 'Leader (R5)'}
    return role_map.get(rank_val, f'R{rank_val}')

def generate_state_workbook(state_id):
    roster_path = DATA_DIR / f"state_{state_id}" / "top10_alliance_rosters.json"
    if not roster_path.exists():
        print(f"Error: {roster_path} not found.")
        return None

    with open(roster_path, "r", encoding="utf-8") as f:
        alliances = json.load(f)

    # Process metrics
    for al in alliances:
        al['total_passes'] = 0
        al['tier_counts'] = {'Elite (Che4)': 0, 'Advanced (Che3)': 0, 'Mid (Che2)': 0, 'Regular (Che1)': 0, 'Unknown': 0}
        for m in al.get('members', []):
            mp = m.get('migratePower') or m.get('power', 0)
            tier, passes = get_tier_and_passes(mp)
            m['calculated_tier'] = tier
            m['calculated_passes'] = passes
            al['total_passes'] += passes
            al['tier_counts'][tier] = al['tier_counts'].get(tier, 0) + 1

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # 1. OVERVIEW TAB
    ws_ov = wb.create_sheet(title=f"State {state_id} Overview")
    ws_ov.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_ov.merge_cells("A1:M1")
    ws_ov["A1"] = f"LAST Z: SURVIVAL | STATE {state_id} TOP 10 ALLIANCES MIGRATION MASTER DIRECTORY"
    ws_ov["A1"].font = font_title
    ws_ov["A1"].fill = fill_title
    ws_ov["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws_ov.row_dimensions[1].height = 32

    ws_ov.merge_cells("A2:M2")
    ws_ov["A2"] = f"Official In-Game Verified Migration Scores | Preparation Phase (Group 200162 | Target States: 689 - 703)"
    ws_ov["A2"].font = font_subtitle
    ws_ov["A2"].fill = fill_title
    ws_ov["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws_ov.row_dimensions[2].height = 20

    # Aggregate State KPIs
    total_state_members = sum(len(a['members']) for a in alliances)
    total_state_passes = sum(a['total_passes'] for a in alliances)
    total_state_power = sum(a['fightpower'] for a in alliances)
    total_elite = sum(a['tier_counts'].get('Elite (Che4)', 0) for a in alliances)

    cards = [
        ("TOTAL TOP 10 POWER", f"{total_state_power / 1e9:.2f}B", "B1", "C2", 2),
        ("TOTAL ACTIVE MEMBERS", f"{total_state_members:,}", "E1", "F2", 5),
        ("TOTAL PASSES NEEDED", f"{total_state_passes:,}", "H1", "I2", 8),
        ("ELITE TIER PLAYERS", f"{total_elite}", "K1", "L2", 11)
    ]

    for label, val, c1, c2, col_idx in cards:
        ws_ov.merge_cells(start_row=4, start_column=col_idx, end_row=4, end_column=col_idx+1)
        ws_ov.merge_cells(start_row=5, start_column=col_idx, end_row=5, end_column=col_idx+1)
        
        lbl_cell = ws_ov.cell(row=4, column=col_idx, value=label)
        lbl_cell.font = font_card_lbl
        lbl_cell.fill = fill_card
        lbl_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        val_cell = ws_ov.cell(row=5, column=col_idx, value=val)
        val_cell.font = font_card_num
        val_cell.fill = fill_card
        val_cell.alignment = Alignment(horizontal="center", vertical="center")

        for r in [4, 5]:
            for c in [col_idx, col_idx+1]:
                ws_ov.cell(row=r, column=c).border = border_cell

    ws_ov.row_dimensions[4].height = 16
    ws_ov.row_dimensions[5].height = 24

    # Summary Table Headers
    ws_ov.cell(row=7, column=1, value="TOP 10 ALLIANCE SUMMARY & TIER BREAKDOWN").font = font_sec_hdr

    headers = [
        "Rank", "Tag", "Alliance Name", "Total Power", "Members",
        "Leader", "Est. Passes", "Elite (>50M)", "Adv (35-50M)",
        "Mid (20-35M)", "Reg (<=20M)", "Avg Power", "Sheet Link"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws_ov.cell(row=8, column=col_idx, value=h)
        cell.font = font_table_hdr
        cell.fill = fill_hdr
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_cell
    ws_ov.row_dimensions[8].height = 24

    cur_row = 9
    for al in alliances:
        members_cnt = len(al['members'])
        avg_pow = al['fightpower'] / members_cnt if members_cnt else 0
        tag = al['abbr']
        
        ws_ov.cell(row=cur_row, column=1, value=al['rank']).alignment = Alignment(horizontal="center")
        ws_ov.cell(row=cur_row, column=2, value=f"[{tag}]").alignment = Alignment(horizontal="center")
        ws_ov.cell(row=cur_row, column=3, value=al['name']).alignment = Alignment(horizontal="left")
        
        c_pow = ws_ov.cell(row=cur_row, column=4, value=al['fightpower'])
        c_pow.number_format = '#,##0'
        c_pow.alignment = Alignment(horizontal="right")
        
        ws_ov.cell(row=cur_row, column=5, value=members_cnt).alignment = Alignment(horizontal="center")
        ws_ov.cell(row=cur_row, column=6, value=al.get('leader', '')).alignment = Alignment(horizontal="left")
        
        c_pass = ws_ov.cell(row=cur_row, column=7, value=al['total_passes'])
        c_pass.number_format = '#,##0'
        c_pass.alignment = Alignment(horizontal="right")
        
        c_el = ws_ov.cell(row=cur_row, column=8, value=al['tier_counts'].get('Elite (Che4)', 0))
        c_el.alignment = Alignment(horizontal="center")
        if c_el.value > 0: c_el.fill = fill_elite

        c_adv = ws_ov.cell(row=cur_row, column=9, value=al['tier_counts'].get('Advanced (Che3)', 0))
        c_adv.alignment = Alignment(horizontal="center")
        if c_adv.value > 0: c_adv.fill = fill_adv

        c_mid = ws_ov.cell(row=cur_row, column=10, value=al['tier_counts'].get('Mid (Che2)', 0))
        c_mid.alignment = Alignment(horizontal="center")
        if c_mid.value > 0: c_mid.fill = fill_mid

        c_reg = ws_ov.cell(row=cur_row, column=11, value=al['tier_counts'].get('Regular (Che1)', 0))
        c_reg.alignment = Alignment(horizontal="center")
        if c_reg.value > 0: c_reg.fill = fill_reg

        c_avg = ws_ov.cell(row=cur_row, column=12, value=int(avg_pow))
        c_avg.number_format = '#,##0'
        c_avg.alignment = Alignment(horizontal="right")

        link_cell = ws_ov.cell(row=cur_row, column=13, value=f"=HYPERLINK(\"#'{tag}'!A1\", \"View {tag} Roster ->\")")
        link_cell.alignment = Alignment(horizontal="center")
        link_cell.font = Font(name="Segoe UI", size=9.5, color="2563EB", underline="single")

        for c in range(1, 14):
            ws_ov.cell(row=cur_row, column=c).border = border_cell
            if c != 13: ws_ov.cell(row=cur_row, column=c).font = font_data
        
        ws_ov.row_dimensions[cur_row].height = 20
        cur_row += 1

    # Totals Row
    ws_ov.cell(row=cur_row, column=1, value="")
    ws_ov.cell(row=cur_row, column=2, value="TOTAL")
    ws_ov.cell(row=cur_row, column=3, value="State Top 10 Combined")
    c_tot_pow = ws_ov.cell(row=cur_row, column=4, value=f"=SUM(D9:D{cur_row-1})")
    c_tot_pow.number_format = '#,##0'
    ws_ov.cell(row=cur_row, column=5, value=f"=SUM(E9:E{cur_row-1})")
    ws_ov.cell(row=cur_row, column=6, value="")
    c_tot_pass = ws_ov.cell(row=cur_row, column=7, value=f"=SUM(G9:G{cur_row-1})")
    c_tot_pass.number_format = '#,##0'
    ws_ov.cell(row=cur_row, column=8, value=f"=SUM(H9:H{cur_row-1})")
    ws_ov.cell(row=cur_row, column=9, value=f"=SUM(I9:I{cur_row-1})")
    ws_ov.cell(row=cur_row, column=10, value=f"=SUM(J9:J{cur_row-1})")
    ws_ov.cell(row=cur_row, column=11, value=f"=SUM(K9:K{cur_row-1})")
    c_tot_avg = ws_ov.cell(row=cur_row, column=12, value=f"=AVERAGE(L9:L{cur_row-1})")
    c_tot_avg.number_format = '#,##0'
    ws_ov.cell(row=cur_row, column=13, value="")

    for c in range(1, 14):
        cell = ws_ov.cell(row=cur_row, column=c)
        cell.font = font_bold_data
        cell.fill = fill_total
        cell.border = double_bottom
        if c in [4, 7, 12]: cell.alignment = Alignment(horizontal="right")
        elif c in [1, 2, 5, 8, 9, 10, 11]: cell.alignment = Alignment(horizontal="center")
    ws_ov.row_dimensions[cur_row].height = 22

    # Tier Boundaries Legend Table
    cur_row += 3
    ws_ov.cell(row=cur_row, column=1, value="OFFICIAL MIGRATION TIER & PASS CUTOFF MATRIX").font = font_sec_hdr
    cur_row += 1

    matrix_headers = ["Tier Code", "Tier Name", "Migration Power Range", "Pass Cost", "Target Capacity / Rules"]
    for col_idx, mh in enumerate(matrix_headers, 1):
        cell = ws_ov.cell(row=cur_row, column=col_idx, value=mh)
        cell.font = font_table_hdr
        cell.fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_cell
    ws_ov.row_dimensions[cur_row].height = 20

    tiers_legend = [
        ("Che1", "Regular", "<= 20,000,000 Power", "10 Passes", "Unlimited standard migration capacity", fill_reg),
        ("Che2", "Mid Tier", "20,000,001 - 35,000,000 Power", "20 Passes", "Standard active combatant tier", fill_mid),
        ("Che3", "Advanced", "35,000,001 - 50,000,000 Power", "35 Passes", "High combatant tier, requires careful state balancing", fill_adv),
        ("Che4", "Elite", "> 50,000,000 Power", "50 Passes", "Requires President Approval / Strict Bracket Cap", fill_elite)
    ]

    for code, tname, rng, passes, note, fill_t in tiers_legend:
        cur_row += 1
        ws_ov.cell(row=cur_row, column=1, value=code).alignment = Alignment(horizontal="center")
        c2 = ws_ov.cell(row=cur_row, column=2, value=tname)
        c2.alignment = Alignment(horizontal="center")
        c2.fill = fill_t
        ws_ov.cell(row=cur_row, column=3, value=rng).alignment = Alignment(horizontal="center")
        ws_ov.cell(row=cur_row, column=4, value=passes).alignment = Alignment(horizontal="center")
        ws_ov.cell(row=cur_row, column=5, value=note).alignment = Alignment(horizontal="left")
        for c in range(1, 6):
            ws_ov.cell(row=cur_row, column=c).border = border_cell
            ws_ov.cell(row=cur_row, column=c).font = font_data
        ws_ov.row_dimensions[cur_row].height = 19

    # 2. INDIVIDUAL ALLIANCE TABS
    for al in alliances:
        tag = al['abbr']
        ws_al = wb.create_sheet(title=tag[:30])
        ws_al.views.sheetView[0].showGridLines = True

        # Alliance Header Banner
        ws_al.merge_cells("A1:K1")
        ws_al["A1"] = f"[{tag}] {al['name']} | STATE {state_id} RANK #{al['rank']} ALLIANCE ROSTER"
        ws_al["A1"].font = font_title
        ws_al["A1"].fill = fill_title
        ws_al["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws_al.row_dimensions[1].height = 30

        ws_al.merge_cells("A2:K2")
        ws_al["A2"] = f"Leader: {al.get('leader', 'N/A')} | Total Power: {al['fightpower']:,} | Total Members: {len(al['members'])} | Passes Needed: {al['total_passes']:,}"
        ws_al["A2"].font = font_subtitle
        ws_al["A2"].fill = fill_title
        ws_al["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws_al.row_dimensions[2].height = 20

        # Back link
        ws_al.cell(row=3, column=1, value=f"=HYPERLINK(\"#'State {state_id} Overview'!A1\", \"<- Back to State {state_id} Overview\")").font = Font(name="Segoe UI", size=9.5, color="2563EB", underline="single")

        # Roster Headers
        r_headers = [
            "Rank", "In-Game Name", "Role", "HQ", "Total Power",
            "Migration Score", "Migration Tier", "Passes", "Army Kills", "Status", "Player UID"
        ]

        for col_idx, rh in enumerate(r_headers, 1):
            cell = ws_al.cell(row=5, column=col_idx, value=rh)
            cell.font = font_table_hdr
            cell.fill = fill_hdr
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border_cell
        ws_al.row_dimensions[5].height = 24

        sorted_members = sorted(al.get('members', []), key=lambda m: -(m.get('migratePower') or m.get('power', 0)))

        m_row = 6
        for idx, m in enumerate(sorted_members, 1):
            pow_val = m.get('power', 0)
            mp = m.get('migratePower') or pow_val
            tier = m.get('calculated_tier', 'Regular (Che1)')
            passes = m.get('calculated_passes', 10)
            role = role_str(m.get('rank', 1))
            status = "Online" if m.get('online') else "Offline"

            ws_al.cell(row=m_row, column=1, value=idx).alignment = Alignment(horizontal="center")
            ws_al.cell(row=m_row, column=2, value=m.get('name', '')).alignment = Alignment(horizontal="left")
            ws_al.cell(row=m_row, column=3, value=role).alignment = Alignment(horizontal="center")
            ws_al.cell(row=m_row, column=4, value=m.get('mainCityLv', 0)).alignment = Alignment(horizontal="center")
            
            c_p = ws_al.cell(row=m_row, column=5, value=pow_val)
            c_p.number_format = '#,##0'
            c_p.alignment = Alignment(horizontal="right")

            c_mp = ws_al.cell(row=m_row, column=6, value=mp)
            c_mp.number_format = '#,##0'
            c_mp.alignment = Alignment(horizontal="right")

            c_t = ws_al.cell(row=m_row, column=7, value=tier)
            c_t.alignment = Alignment(horizontal="center")
            if "Elite" in tier: c_t.fill = fill_elite
            elif "Advanced" in tier: c_t.fill = fill_adv
            elif "Mid" in tier: c_t.fill = fill_mid
            elif "Regular" in tier: c_t.fill = fill_reg

            ws_al.cell(row=m_row, column=8, value=passes).alignment = Alignment(horizontal="center")

            c_k = ws_al.cell(row=m_row, column=9, value=m.get('armyKill', 0))
            c_k.number_format = '#,##0'
            c_k.alignment = Alignment(horizontal="right")

            c_st = ws_al.cell(row=m_row, column=10, value=status)
            c_st.alignment = Alignment(horizontal="center")
            if status == "Online":
                c_st.font = Font(name="Segoe UI", size=9.5, color="166534", bold=True)

            ws_al.cell(row=m_row, column=11, value=str(m.get('uid', ''))).alignment = Alignment(horizontal="center")

            for c in range(1, 12):
                ws_al.cell(row=m_row, column=c).border = border_cell
                if c != 10: ws_al.cell(row=m_row, column=c).font = font_data
            
            ws_al.row_dimensions[m_row].height = 19
            m_row += 1

        # Roster Total Row
        ws_al.cell(row=m_row, column=1, value="")
        ws_al.cell(row=m_row, column=2, value="ALLIANCE TOTAL")
        ws_al.cell(row=m_row, column=3, value=f"{len(sorted_members)} Members")
        ws_al.cell(row=m_row, column=4, value="")
        c_tot_pow = ws_al.cell(row=m_row, column=5, value=f"=SUM(E6:E{m_row-1})")
        c_tot_pow.number_format = '#,##0'
        c_tot_mp = ws_al.cell(row=m_row, column=6, value=f"=SUM(F6:F{m_row-1})")
        c_tot_mp.number_format = '#,##0'
        ws_al.cell(row=m_row, column=7, value="")
        c_tot_pass = ws_al.cell(row=m_row, column=8, value=f"=SUM(H6:H{m_row-1})")
        c_tot_pass.number_format = '#,##0'
        c_tot_k = ws_al.cell(row=m_row, column=9, value=f"=SUM(I6:I{m_row-1})")
        c_tot_k.number_format = '#,##0'
        ws_al.cell(row=m_row, column=10, value="")
        ws_al.cell(row=m_row, column=11, value="")

        for c in range(1, 12):
            cell = ws_al.cell(row=m_row, column=c)
            cell.font = font_bold_data
            cell.fill = fill_total
            cell.border = double_bottom
            if c in [5, 6, 8, 9]: cell.alignment = Alignment(horizontal="right")
            elif c in [1, 2, 3, 4, 7, 10, 11]: cell.alignment = Alignment(horizontal="center")
        ws_al.row_dimensions[m_row].height = 22

    # Auto-adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                # ignore merged title banner in row 1 and 2
                if cell.row in [1, 2]:
                    continue
                val = str(cell.value or '')
                if val.startswith('='): # formula
                    val = "123,456,789"
                max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 11)

    out_file = XLSX_DIR / f"State_{state_id}_Top_10_Alliances_Migration_Master.xlsx"
    wb.save(out_file)
    print(f"Generated: {out_file.name} ({os.path.getsize(out_file):,} bytes)")
    return out_file

def main():
    print("=" * 60)
    print("GENERATING ELEGANT EXCEL SHEETS FOR ALL 15 BRACKET STATES (689 - 703)")
    print("=" * 60)
    generated = []
    for s in BRACKET_STATES:
        res = generate_state_workbook(s)
        if res:
            generated.append(res)
    print("=" * 60)
    print(f"SUCCESSFULLY GENERATED {len(generated)} / {len(BRACKET_STATES)} MASTER EXCEL WORKBOOKS")
    print("=" * 60)

if __name__ == "__main__":
    main()
