import json
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

root = r"data/cache"
json_path = os.path.join(root, "top10_alliances_migration_scores.json")
desktop_xlsx = r"data/exports/State_694_Top_10_Alliances_Migration_Master.xlsx"
scratch_xlsx = os.path.join(root, "State_694_Top_10_Alliances_Migration_Master.xlsx")

if not os.path.exists(json_path):
    print(f"Error: {json_path} does not exist yet.")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    state_data = json.load(f)

alliances = state_data['alliances']

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palette
DARK_NAVY = "1B365D"
ACCENT_BLUE = "2A5C9A"
ICE_HEADER = "F1F5F9"
CARD_BG = "F8FAFC"
BORDER_GRAY = "E2E8F0"
BORDER_MED = "CBD5E1"

ADV_BG = "E6E6FA"       # Lavender / Light Purple for Advanced
MID_BG = "E0F2FE"       # Light Ice Blue for Intermediate
REG_BG = "F0FDF4"       # Light Green for Regular
ELITE_BG = "FCE7F3"     # Light Pink/Purple for Elite
GOLD_BG = "FEF3C7"      # Gold highlight for User (Heinzy)

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
font_red_bold = Font(name="Segoe UI", size=10, bold=True, color="991B1B")

fill_title = PatternFill(start_color=DARK_NAVY, end_color=DARK_NAVY, fill_type="solid")
fill_hdr = PatternFill(start_color=ACCENT_BLUE, end_color=ACCENT_BLUE, fill_type="solid")
fill_sub_hdr = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_adv = PatternFill(start_color=ADV_BG, end_color=ADV_BG, fill_type="solid")
fill_mid = PatternFill(start_color=MID_BG, end_color=MID_BG, fill_type="solid")
fill_reg = PatternFill(start_color=REG_BG, end_color=REG_BG, fill_type="solid")
fill_elite = PatternFill(start_color=ELITE_BG, end_color=ELITE_BG, fill_type="solid")
fill_gold = PatternFill(start_color=GOLD_BG, end_color=GOLD_BG, fill_type="solid")
fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
fill_card = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")

thin_border_side = Side(style='thin', color=BORDER_GRAY)
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
med_bottom = Border(bottom=Side(style='medium', color=ACCENT_BLUE))
double_bottom = Border(bottom=Side(style='double', color=DARK_NAVY), top=Side(style='thin', color=BORDER_MED))

def role_str(rank_val):
    role_map = {1: 'R1', 2: 'R2', 3: 'R3', 4: 'R4', 5: 'Leader (R5)'}
    return role_map.get(rank_val, f'R{rank_val}')

# - State 694 Overview Tab
ws_ov = wb.create_sheet(title="State 694 Overview")
ws_ov.views.sheetView[0].showGridLines = True

# Title Banner
ws_ov.merge_cells("A1:M1")
ws_ov["A1"] = "LAST Z: SURVIVAL | STATE 694 TOP 10 ALLIANCES MIGRATION MASTER DIRECTORY"
ws_ov["A1"].font = font_title
ws_ov["A1"].fill = fill_title
ws_ov["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws_ov.row_dimensions[1].height = 32

ws_ov.merge_cells("A2:M2")
ws_ov["A2"] = "Official In-Game Verified Migration Scores | Preparation Phase (Group 200162 | Target States: 689 - 704)"
ws_ov["A2"].font = font_subtitle
ws_ov["A2"].fill = fill_title
ws_ov["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws_ov.row_dimensions[2].height = 20

# Calculate Aggregate State KPIs
total_state_members = sum(len(a['members']) for a in alliances)
total_state_passes = sum(a['total_passes_required'] for a in alliances)
total_state_power = sum(a['total_fightpower'] for a in alliances)

total_elite = sum(a['tier_distribution'].get('Elite (Che4)', 0) for a in alliances)
total_adv = sum(a['tier_distribution'].get('Advanced (Che3)', 0) for a in alliances)
total_mid = sum(a['tier_distribution'].get('Intermediate (Che2)', 0) for a in alliances)
total_reg = sum(a['tier_distribution'].get('Regular (Che1)', 0) for a in alliances)

# KPI Summary Cards (Row 4-5)
cards = [
    ("TOTAL ALLIANCES", f"{len(alliances)} Alliances", "B", "C"),
    ("TOTAL MEMBERS TRACKED", f"{total_state_members:,} Players", "D", "E"),
    ("TOTAL PASSES REQUIRED", f"{total_state_passes:,} Passes", "F", "G"),
    ("ADVANCED / ELITE DEMAND", f"{total_adv + total_elite:,} Players", "H", "I"),
    ("AVG PASSES / PLAYER", f"{(total_state_passes/total_state_members):.1f} Passes", "J", "K"),
    ("COMBAT POWER ANALYZED", f"{total_state_power / 1e9:.2f} Billion", "L", "M"),
]

for label, val, start_col, end_col in cards:
    ws_ov.merge_cells(f"{start_col}4:{end_col}4")
    ws_ov.merge_cells(f"{start_col}5:{end_col}5")
    
    cell_lbl = ws_ov[f"{start_col}4"]
    cell_lbl.value = label
    cell_lbl.font = font_card_lbl
    cell_lbl.fill = fill_card
    cell_lbl.alignment = Alignment(horizontal="center", vertical="center")
    
    cell_val = ws_ov[f"{start_col}5"]
    cell_val.value = val
    if "PASSES" in label and "AVG" not in label:
        cell_val.font = Font(name="Segoe UI", size=13, bold=True, color="991B1B")
    else:
        cell_val.font = font_card_num
    cell_val.fill = fill_card
    cell_val.alignment = Alignment(horizontal="center", vertical="center")
    
    # Border card
    for col_letter in [start_col, end_col]:
        for r in (4, 5):
            ws_ov[f"{col_letter}{r}"].border = border_cell

ws_ov.row_dimensions[4].height = 16
ws_ov.row_dimensions[5].height = 24
ws_ov.row_dimensions[6].height = 10

# Section Header
ws_ov.merge_cells("A7:M7")
ws_ov["A7"] = "STATE 694 TOP 10 ALLIANCES LEAGUE TABLE & MIGRATION DEMAND"
ws_ov["A7"].font = font_sec_hdr
ws_ov["A7"].alignment = Alignment(horizontal="left", vertical="center")
ws_ov.row_dimensions[7].height = 24

ov_headers = [
    "State Rank", "Alliance Tag", "Alliance Full Name", "Alliance Leader",
    "Total Combat Power", "Member Count", "Total Passes Needed", "Avg Passes/Member",
    "Elite (>100M)", "Advanced (40-100M)", "Intermediate (20-40M)", "Regular (<=20M)",
    "Top Scorer (Migration Score)"
]

ws_ov.row_dimensions[8].height = 26
for c_idx, h in enumerate(ov_headers, 1):
    cell = ws_ov.cell(row=8, column=c_idx, value=h)
    cell.font = font_table_hdr
    cell.fill = fill_hdr
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border_cell

for r_idx, a in enumerate(alliances, 9):
    members = a['members']
    top_scorer = members[0] if len(members) > 0 else {}
    top_scorer_str = f"{top_scorer.get('name', 'N/A')} ({top_scorer.get('authoritative_migrate_power', 0):,})"
    
    tier_dist = a.get('tier_distribution', {})
    c_elite = tier_dist.get('Elite (Che4)', 0)
    c_adv = tier_dist.get('Advanced (Che3)', 0)
    c_mid = tier_dist.get('Intermediate (Che2)', 0)
    c_reg = tier_dist.get('Regular (Che1)', 0)
    
    m_count = len(members)
    avg_passes = a['total_passes_required'] / m_count if m_count > 0 else 0
    
    row_data = [
        a['rank'],
        f"[{a['abbr']}]",
        a['name'],
        a['leader'],
        a['total_fightpower'],
        m_count,
        a['total_passes_required'],
        round(avg_passes, 1),
        c_elite,
        c_adv,
        c_mid,
        c_reg,
        top_scorer_str
    ]
    
    ws_ov.row_dimensions[r_idx].height = 20
    for c_idx, val in enumerate(row_data, 1):
        cell = ws_ov.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_data
        cell.border = border_cell
        
        if c_idx in (1, 6, 9, 10, 11, 12):
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.number_format = "#,##0"
        elif c_idx == 2:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = font_bold_data
        elif c_idx in (5, 7):
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            if c_idx == 7:
                cell.font = font_red_bold
        elif c_idx == 8:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.0"
        elif c_idx == 13:
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.font = font_bold_data
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Grand Total Row
tot_row = len(alliances) + 9
ws_ov.row_dimensions[tot_row].height = 24
ws_ov.cell(row=tot_row, column=1, value="")
ws_ov.cell(row=tot_row, column=2, value="TOTAL")
ws_ov.cell(row=tot_row, column=3, value="State 694 Top 10 Summary")
ws_ov.cell(row=tot_row, column=4, value="")
ws_ov.cell(row=tot_row, column=5, value=total_state_power)
ws_ov.cell(row=tot_row, column=6, value=total_state_members)
ws_ov.cell(row=tot_row, column=7, value=total_state_passes)
ws_ov.cell(row=tot_row, column=8, value=round(total_state_passes / total_state_members, 1))
ws_ov.cell(row=tot_row, column=9, value=total_elite)
ws_ov.cell(row=tot_row, column=10, value=total_adv)
ws_ov.cell(row=tot_row, column=11, value=total_mid)
ws_ov.cell(row=tot_row, column=12, value=total_reg)
ws_ov.cell(row=tot_row, column=13, value="")

for c_idx in range(1, 14):
    cell = ws_ov.cell(row=tot_row, column=c_idx)
    cell.font = font_bold_data
    cell.fill = fill_total
    cell.border = double_bottom
    if c_idx in (1, 2, 6, 9, 10, 11, 12):
        cell.alignment = Alignment(horizontal="center", vertical="center")
        if c_idx > 2:
            cell.number_format = "#,##0"
    elif c_idx in (5, 7):
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "#,##0"
        if c_idx == 7:
            cell.font = Font(name="Segoe UI", size=10, bold=True, color="991B1B")
    elif c_idx == 8:
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "0.0"

# Migration Mechanics Callout Box (Row 22 onwards)
rule_start = tot_row + 2
ws_ov.merge_cells(f"A{rule_start}:M{rule_start}")
ws_ov[f"A{rule_start}"] = "MIGRATION EVENT MECHANICS & PASS COST MATRIX (GROUP 200162)"
ws_ov[f"A{rule_start}"].font = font_sec_hdr
ws_ov[f"A{rule_start}"].alignment = Alignment(horizontal="left", vertical="center")
ws_ov.row_dimensions[rule_start].height = 24

rule_headers = ["Tier Code", "Tier Name", "Migration Score Bracket", "Passes Required", "Server Limit Condition", "Eligible State Group"]
ws_ov.row_dimensions[rule_start + 1].height = 22

rule_specs = [
    ("Che1", "Regular", "<= 20,000,000", 10, "Exempt from serverLimit (Standard Migration)", "Season 1 Group 200162 (States 689 - 704)"),
    ("Che2", "Intermediate", "20,000,001 - 40,000,000", 15, "Standard Cap Tracking (serverLimit = 15M)", "Season 1 Group 200162 (States 689 - 704)"),
    ("Che3", "Advanced", "40,000,001 - 100,000,000", 20, "Quota Limited / State Entry Approval", "Season 1 Group 200162 (States 689 - 704)"),
    ("Che4", "Elite", "> 100,000,000", 50, "Top Power Special Transfer Authorization", "Season 1 Group 200162 (States 689 - 704)")
]

col_spans = [
    ("A", "B"), # Tier Code
    ("C", "D"), # Tier Name
    ("E", "F"), # Score Bracket
    ("G", "G"), # Passes
    ("H", "J"), # Condition
    ("K", "M")  # Group
]

for idx, (sc, ec) in enumerate(col_spans):
    if sc != ec:
        ws_ov.merge_cells(f"{sc}{rule_start + 1}:{ec}{rule_start + 1}")
    c = ws_ov[f"{sc}{rule_start + 1}"]
    c.value = rule_headers[idx]
    c.font = Font(name="Segoe UI", size=9.5, bold=True, color="FFFFFF")
    c.fill = fill_hdr
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell

for r_offset, (code, name, bracket, passes, cond, grp) in enumerate(rule_specs, 2):
    r_num = rule_start + r_offset
    ws_ov.row_dimensions[r_num].height = 20
    vals = [code, name, bracket, passes, cond, grp]
    for idx, (sc, ec) in enumerate(col_spans):
        if sc != ec:
            ws_ov.merge_cells(f"{sc}{r_num}:{ec}{r_num}")
        c = ws_ov[f"{sc}{r_num}"]
        c.value = vals[idx]
        c.font = font_data
        c.border = border_cell
        if idx in (0, 1, 3):
            c.alignment = Alignment(horizontal="center", vertical="center")
            if idx == 1:
                c.font = font_bold_data
            if idx == 3:
                c.font = font_red_bold
        else:
            c.alignment = Alignment(horizontal="left", vertical="center")

# - Dedicated Alliance Tabs (10 Tabs)
member_headers = [
    "Rank", "Alliance Role", "HQ Level", "Player Name", "Player UID",
    "Official Migration Score", "Migration Tier", "Passes Required",
    "Current Power", "Max Historical Power",
    "Building Power", "Tech Power", "Hero Power", "Vehicle Power", "Troop Power",
    "Verification Status"
]

for a in alliances:
    abbr = a['abbr'].replace('[', '').replace(']', '').strip()
    full_name = a['name'].replace('[', '').replace(']', '').replace(':', '').replace('/', '').replace('\\', '').replace('?', '').replace('*', '').strip()
    tab_title = f"{abbr} - {full_name}"[:31].strip()
    
    ws = wb.create_sheet(title=tab_title)
    ws.views.sheetView[0].showGridLines = True
    
    # Title Banner
    ws.merge_cells("A1:P1")
    ws["A1"] = f"LAST Z: SURVIVAL | [{abbr}] {full_name.upper()} (STATE 694)"
    ws["A1"].font = font_title
    ws["A1"].fill = fill_title
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32
    
    ws.merge_cells("A2:P2")
    ws["A2"] = f"State Rank: #{a['rank']} | Leader: {a['leader']} | Total Combat Power: {a['total_fightpower']:,} | Members: {len(a['members'])}"
    ws["A2"].font = font_subtitle
    ws["A2"].fill = fill_title
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20
    
    # Metrics Row
    tier_dist = a.get('tier_distribution', {})
    c_elite = tier_dist.get('Elite (Che4)', 0)
    c_adv = tier_dist.get('Advanced (Che3)', 0)
    c_mid = tier_dist.get('Intermediate (Che2)', 0)
    c_reg = tier_dist.get('Regular (Che1)', 0)
    
    ws.merge_cells("A3:C3")
    ws["A3"] = f"Total Members: {len(a['members'])}"
    ws["A3"].font = font_sub_hdr
    ws["A3"].alignment = Alignment(horizontal="left", vertical="center")
    
    ws.merge_cells("D3:H3")
    ws["D3"] = f"Total Passes: {a['total_passes_required']:,} Passes (Members: {len(a['members'])})"
    ws["D3"].font = Font(name="Segoe UI", size=11, bold=True, color="991B1B")
    ws["D3"].alignment = Alignment(horizontal="left", vertical="center")
    
    ws.merge_cells("J3:O3")
    ws["J3"] = f"Tier Breakdown: Elite (>100M): {c_elite} | Advanced (40-100M): {c_adv} | Intermediate (20-40M): {c_mid} | Regular (<=20M): {c_reg}"
    ws["J3"].font = font_sub_hdr
    ws["J3"].alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[3].height = 22
    
    ws.row_dimensions[4].height = 8
    
    # Column Headers
    ws.row_dimensions[5].height = 26
    for c_idx, h in enumerate(member_headers, 1):
        cell = ws.cell(row=5, column=c_idx, value=h)
        cell.font = font_table_hdr
        cell.fill = fill_hdr
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_cell
        
    # Populate Members
    members = sorted(a['members'], key=lambda x: (x.get('authoritative_migrate_power', 0), x.get('total_power', 0)), reverse=True)
    for m_idx, m in enumerate(members, 1):
        r_num = m_idx + 5
        ws.row_dimensions[r_num].height = 20
        
        name = m.get('name', '')
        is_user = (name == 'Heinzy')
        tier = m.get('tier', 'Unknown')
        
        # Color fill based on tier or user
        if is_user:
            row_fill = fill_gold
        elif 'Elite' in tier:
            row_fill = fill_elite
        elif 'Advanced' in tier:
            row_fill = fill_adv
        elif 'Intermediate' in tier:
            row_fill = fill_mid
        elif 'Regular' in tier:
            row_fill = fill_reg
        else:
            row_fill = None
            
        m_row = [
            m_idx,
            role_str(m.get('rank', 1)),
            m.get('mainBuildingLevel', 0),
            name,
            str(m.get('uid', '')),
            m.get('authoritative_migrate_power', 0),
            tier,
            m.get('passes_required', 0),
            m.get('total_power', 0),
            m.get('player_max_power', 0),
            m.get('building_power', 0),
            m.get('science_power', 0),
            m.get('hero_power', 0),
            m.get('tank_power', 0),
            m.get('army_power', 0),
            m.get('status', 'PENDING')
        ]
        
        for c_idx, val in enumerate(m_row, 1):
            cell = ws.cell(row=r_num, column=c_idx, value=val)
            cell.font = font_data
            cell.border = border_cell
            if row_fill:
                cell.fill = row_fill
                
            # Alignments & Number Formats
            if c_idx in (1, 2, 3, 7, 8, 16):
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if c_idx in (1, 3, 8):
                    cell.number_format = "#,##0"
                if c_idx == 8:
                    cell.font = font_bold_data
            elif c_idx in (4, 5):
                cell.alignment = Alignment(horizontal="left", vertical="center")
                if is_user and c_idx == 4:
                    cell.font = Font(name="Segoe UI", size=10, bold=True, color="B45309")
            elif c_idx == 6:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "#,##0"
                cell.font = font_bold_data
            else: # Numerical Power fields
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "#,##0"

    # Freeze panes at A6 so header & stats are sticky
    ws.freeze_panes = "A6"
    
    # Auto-filter on header
    last_col_letter = get_column_letter(len(member_headers))
    ws.auto_filter.ref = f"A5:{last_col_letter}{len(members) + 5}"

    # Hide requested columns (keep them in the workbook, but hide from view)
    # Verification status (P), Rank (A), Alliance Rank (B), HQ Level (C), Player UID (E), Total Power (I)
    for c_letter in ['A', 'B', 'C', 'E', 'I', 'P']:
        ws.column_dimensions[c_letter].hidden = True

# Set auto column widths across all sheets
for sheet in wb.worksheets:
    for col in sheet.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Ignore merged banner lines (rows 1-3)
            if cell.row in (1, 2, 3, 4, 7):
                continue
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

# Ensure overview column widths look spacious
ws_ov.column_dimensions["A"].width = 12
ws_ov.column_dimensions["B"].width = 15
ws_ov.column_dimensions["C"].width = 24
ws_ov.column_dimensions["D"].width = 20
ws_ov.column_dimensions["E"].width = 22
ws_ov.column_dimensions["F"].width = 15
ws_ov.column_dimensions["G"].width = 20
ws_ov.column_dimensions["H"].width = 18
ws_ov.column_dimensions["I"].width = 16
ws_ov.column_dimensions["J"].width = 20
ws_ov.column_dimensions["K"].width = 22
ws_ov.column_dimensions["L"].width = 18
ws_ov.column_dimensions["M"].width = 28

# Save to Desktop and Scratch
wb.save(desktop_xlsx)
wb.save(scratch_xlsx)
print(f"Successfully generated State 694 Top 10 Alliances Master Excel at:\n- {desktop_xlsx}\n- {scratch_xlsx}")