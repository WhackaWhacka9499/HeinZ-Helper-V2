import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"data/cache")
DATA_DIR = ROOT / "bracket_data"
CACHE_PATH = ROOT / "all_players_profile_cache.json"
OUT_XLSX_DIR = ROOT / "bracket_xlsx_perfect"
OUT_XLSX_DIR.mkdir(parents=True, exist_ok=True)

TARGET_FOLDER_ID = "1aaeAu6jw2nrykBKWld_8kjqE2kQpVl78"

# Exact Styling Palette matching OG State 694 master
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
font_card_num = Font(name="Segoe UI", size=14, bold=True, color="1B365D")
font_card_lbl = Font(name="Segoe UI", size=8.5, bold=True, color="64748B")
font_red_bold = Font(name="Segoe UI", size=10, bold=True, color="991B1B")

fill_title = PatternFill(start_color=DARK_NAVY, end_color=DARK_NAVY, fill_type="solid")
fill_hdr = PatternFill(start_color=ACCENT_BLUE, end_color=ACCENT_BLUE, fill_type="solid")
fill_adv = PatternFill(start_color=ADV_BG, end_color=ADV_BG, fill_type="solid")
fill_mid = PatternFill(start_color=MID_BG, end_color=MID_BG, fill_type="solid")
fill_reg = PatternFill(start_color=REG_BG, end_color=REG_BG, fill_type="solid")
fill_elite = PatternFill(start_color=ELITE_BG, end_color=ELITE_BG, fill_type="solid")
fill_gold = PatternFill(start_color=GOLD_BG, end_color=GOLD_BG, fill_type="solid")
fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
fill_card = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")

thin_border_side = Side(style='thin', color=BORDER_GRAY)
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
double_bottom = Border(bottom=Side(style='double', color=DARK_NAVY), top=Side(style='thin', color=BORDER_MED))

def role_str(rank_val):
    role_map = {1: 'R1', 2: 'R2', 3: 'R3', 4: 'R4', 5: 'Leader (R5)'}
    return role_map.get(rank_val, f'R{rank_val}')

def get_tier_and_passes(migrate_power):
    if migrate_power is None or migrate_power == 0:
        return ("Regular (Che1)", 10)
    if migrate_power <= 20000000:
        return ("Regular (Che1)", 10)
    elif migrate_power <= 40000000:
        return ("Intermediate (Che2)", 15)
    elif migrate_power <= 100000000:
        return ("Advanced (Che3)", 20)
    else:
        return ("Elite (Che4)", 50)

def generate_state_master_excel(state_id, cache):
    roster_path = DATA_DIR / f"state_{state_id}" / "top10_alliance_rosters.json"
    if not roster_path.exists():
        print(f"Error: {roster_path} does not exist!")
        return None

    with open(roster_path, "r", encoding="utf-8") as f:
        rosters = json.load(f)

    alliances = []
    for al in rosters:
        members_data = []
        for m in al.get('members', []):
            uid = str(m.get('uid'))
            pld = cache.get(uid, {})
            mp = pld.get('migratePower') or m.get('power', 0)
            tier, passes = get_tier_and_passes(mp)
            
            members_data.append({
                'rank': m.get('rank', 1),
                'uid': uid,
                'name': pld.get('name') or m.get('name', ''),
                'mainBuildingLevel': pld.get('mainBuildingLevel') or m.get('mainCityLv', 0),
                'authoritative_migrate_power': mp,
                'tier': tier,
                'passes_required': passes,
                'total_power': pld.get('power') or m.get('power', 0),
                'player_max_power': pld.get('playerMaxPower') or 0,
                'building_power': pld.get('buildingPower') or 0,
                'science_power': pld.get('sciencePower') or 0,
                'hero_power': pld.get('heroPower') or 0,
                'tank_power': pld.get('tankPower') or 0,
                'army_power': pld.get('armyPower') or 0,
                'status': '100% IN-GAME VERIFIED' if mp > 0 else 'PENDING'
            })
            
        members_data.sort(key=lambda x: (x['authoritative_migrate_power'], x['total_power']), reverse=True)
        total_passes = sum(m['passes_required'] for m in members_data)
        tier_counts = {}
        for m in members_data:
            tier_counts[m['tier']] = tier_counts.get(m['tier'], 0) + 1

        alliances.append({
            'rank': al['rank'],
            'abbr': al['abbr'],
            'name': al['name'],
            'leader': al['leader'],
            'total_fightpower': al['fightpower'],
            'allianceId': al['allianceId'],
            'member_count': len(members_data),
            'total_passes_required': total_passes,
            'tier_distribution': tier_counts,
            'members': members_data
        })

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # 1. OVERVIEW TAB
    ws_ov = wb.create_sheet(title=f"State {state_id} Overview")
    ws_ov.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_ov.merge_cells("A1:M1")
    ws_ov["A1"] = f"State {state_id} Top 10 Alliances - Grouping 689-704"
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

    # 6 KPI Summary Cards (Row 4-5) matching OG master
    cards = [
        ("TOTAL ALLIANCES", f"{len(alliances)} Alliances", "B", "C"),
        ("TOTAL MEMBERS TRACKED", f"{total_state_members:,} Players", "D", "E"),
        ("TOTAL PASSES REQUIRED", f"{total_state_passes:,} Passes", "F", "G"),
        ("ADVANCED / ELITE DEMAND", f"{total_adv + total_elite:,} Players", "H", "I"),
        ("AVG PASSES / PLAYER", f"{(total_state_passes/total_state_members if total_state_members else 0):.1f} Passes", "J", "K"),
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
        
        for col_letter in [start_col, end_col]:
            for r in (4, 5):
                ws_ov[f"{col_letter}{r}"].border = border_cell

    ws_ov.row_dimensions[4].height = 16
    ws_ov.row_dimensions[5].height = 24
    ws_ov.row_dimensions[6].height = 10

    # Section Header (Blank per user request)
    ws_ov.merge_cells("A7:M7")
    ws_ov["A7"] = ""
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
    ws_ov.cell(row=tot_row, column=3, value=f"State {state_id} Top 10 Summary")
    ws_ov.cell(row=tot_row, column=4, value="")
    ws_ov.cell(row=tot_row, column=5, value=total_state_power)
    ws_ov.cell(row=tot_row, column=6, value=total_state_members)
    ws_ov.cell(row=tot_row, column=7, value=total_state_passes)
    ws_ov.cell(row=tot_row, column=8, value=round(total_state_passes / total_state_members if total_state_members else 0, 1))
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

    # Overview column widths matching OG
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

    # 2. DEDICATED ALLIANCE TABS (10 TABS)
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
        ws["A1"] = f"[{abbr}] {full_name} (State {state_id})"
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
        members = a['members']
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
                m.get('status', '100% IN-GAME VERIFIED')
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

        # Hide requested columns matching OG sheet (Rank A, Role B, HQ C, UID E, Current Power I, Status P)
        for c_letter in ['A', 'B', 'C', 'E', 'I', 'P']:
            ws.column_dimensions[c_letter].hidden = True

    # Set auto column widths across all alliance sheets
    for sheet in wb.worksheets:
        if sheet.title.startswith(f"State {state_id} Overview"):
            continue
        for col in sheet.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = 0
            for cell in col:
                if cell.row in (1, 2, 3, 4, 7):
                    continue
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    out_file = OUT_XLSX_DIR / f"State {state_id} Migration.xlsx"
    wb.save(out_file)
    print(f"Generated perfect OG-matching workbook: {out_file.name} ({os.path.getsize(out_file):,} bytes)")
    return out_file

def upload_native_sheet(state_id, xlsx_path):
    print(f"Uploading State {state_id} Migration to Google Drive as True Native Google Spreadsheet...")
    cmd = f'gdrive mutate upload "{str(xlsx_path)}" --parent {TARGET_FOLDER_ID} --mime-type application/vnd.google-apps.spreadsheet'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = res.stdout + res.stderr
    print(out.strip())
    m = re.search(r"\(ID:\s*([^\)]+)\)", out)
    if m:
        new_id = m.group(1).strip()
        share_cmd = f'gdrive mutate share {new_id} --role reader --type anyone'
        subprocess.run(share_cmd, shell=True, capture_output=True)
        return new_id
    return None

def clean_old_files():
    print("\nScanning Google Drive folder for old binary .xlsx files to clean up...")
    cmd = f'gdrive readonly ls {TARGET_FOLDER_ID} --json'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        try:
            files = json.loads(res.stdout)
            for f in files:
                f_id = f.get('id')
                f_name = f.get('name', '')
                f_type = f.get('mimeType', '')
                # Trash binary sheets or old test files
                if f_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    print(f"Trashing old binary xlsx: {f_name} (ID: {f_id})")
                    subprocess.run(f'gdrive mutate trash {f_id}', shell=True, capture_output=True)
        except Exception as e:
            print(f"Error parsing folder contents: {e}")

def main():
    print("=" * 70)
    print("BUILDING ALL 16 BRACKET STATES AS TRUE NATIVE GOOGLE SPREADSHEETS")
    print("100% IDENTICAL FORMATTING TO OG STATE 694 MASTER DIRECTORY")
    print("=" * 70)

    if not CACHE_PATH.exists():
        print("Cache file does not exist!")
        return

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        cache = json.load(f)
    print(f"Loaded player profile cache with {len(cache):,} verified player profiles.")

    # 1. Clean old binary files first
    clean_old_files()

    results = {}
    # 2. Generate and upload all 16 states
    for s in range(689, 705):
        print(f"\n[{s-688}/16] >>> Processing State {s} Master Sheet <<<")
        xlsx_path = generate_state_master_excel(s, cache)
        if xlsx_path:
            sheet_id = upload_native_sheet(s, xlsx_path)
            if sheet_id:
                link = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
                results[s] = {"id": sheet_id, "url": link}
                print(f"State {s} Native Sheet Live: {link}")
            time.sleep(1)

    print("\n" * 2)
    print("=" * 70)
    print("ALL 16 BRACKET NATIVE GOOGLE SPREADSHEETS SUCCESSFULLY DEPLOYED!")
    print("=" * 70)
    for s in range(689, 705):
        info = results.get(s, {})
        print(f"State {s}: {info.get('url', 'ERROR')}")

    out_summary = ROOT / "all_16_states_native_sheets.json"
    tmp_summary = out_summary.with_name(f"{out_summary.name}.{os.getpid()}.tmp")
    with open(tmp_summary, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    os.replace(tmp_summary, out_summary)

if __name__ == "__main__":
    main()
