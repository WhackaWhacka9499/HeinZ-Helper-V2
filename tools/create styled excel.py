import json
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

json_path = r"data/cache/vs33_alliance_migration_scores.json"
desktop_xlsx = r"data/exports/VS33_State_694_Migration_Master.xlsx"
scratch_xlsx = r"data/cache/VS33_State_694_Migration_Master.xlsx"

data = json.load(open(json_path, 'r', encoding='utf-8'))
records = data['records']

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "VS33 Migration Scores"
ws.views.sheetView[0].showGridLines = True

# Colors
DARK_BLUE = "1B365D"
LIGHT_BLUE = "E8EEF5"
ACCENT_BLUE = "2A5C9A"
ADV_BG = "E6E6FA"       # Lavender / Light Purple for Advanced
MID_BG = "E0F2FE"       # Light Ice Blue for Intermediate
REG_BG = "F0FDF4"       # Light Green for Regular

font_title = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="E0E0E0")
font_summary_label = Font(name="Segoe UI", size=10, bold=True, color="1B365D")
font_summary_val = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_data = Font(name="Segoe UI", size=10)
font_bold_data = Font(name="Segoe UI", size=10, bold=True)
font_user = Font(name="Segoe UI", size=10, bold=True, color="B45309")

fill_title = PatternFill(start_color=DARK_BLUE, end_color=DARK_BLUE, fill_type="solid")
fill_header = PatternFill(start_color=ACCENT_BLUE, end_color=ACCENT_BLUE, fill_type="solid")
fill_adv = PatternFill(start_color=ADV_BG, end_color=ADV_BG, fill_type="solid")
fill_mid = PatternFill(start_color=MID_BG, end_color=MID_BG, fill_type="solid")
fill_reg = PatternFill(start_color=REG_BG, end_color=REG_BG, fill_type="solid")
fill_user = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Gold tint for Heinzy

thin_gray = Side(style='thin', color='E2E8F0')
border_cell = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)

# Title Banner
ws.merge_cells("A1:P1")
ws["A1"] = "LAST Z: SURVIVAL | [VS33] VEIL OF SHADOWS (STATE 694) MASTER MIGRATION ROSTER"
ws["A1"].font = font_title
ws["A1"].fill = fill_title
ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 34

ws.merge_cells("A2:P2")
ws["A2"] = "Official In-Game Verified Migration Scores | Preparation Phase Live (06 Nov 2026) | Target Servers: States 689 - 704"
ws["A2"].font = font_subtitle
ws["A2"].fill = fill_title
ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[2].height = 20

# Summary Row
ws.merge_cells("A3:C3")
ws["A3"] = "Total Members: 96"
ws["A3"].font = font_summary_label
ws["A3"].alignment = Alignment(horizontal="left", vertical="center")

ws.merge_cells("D3:G3")
ws["D3"] = "Total Alliance Passes Required: 1,210 Passes (96 Members)"
ws["D3"].font = Font(name="Segoe UI", size=11, bold=True, color="B91C1C")
ws["D3"].alignment = Alignment(horizontal="left", vertical="center")

ws.merge_cells("H3:P3")
ws["H3"] = "Tier Breakdown: Advanced (20 passes): 6 players | Intermediate (15 passes): 38 players | Regular (10 passes): 52 players"
ws["H3"].font = font_summary_val
ws["H3"].alignment = Alignment(horizontal="right", vertical="center")
ws.row_dimensions[3].height = 24

# Empty spacer
ws.row_dimensions[4].height = 8

# Headers
headers = [
    "Rank", "Alliance Rank", "HQ Level", "Player Name", "Player UID",
    "Official Migration Score", "Migration Tier", "Passes Required",
    "Total Power", "Max Historical Power",
    "Structure Power", "Tech Power", "Hero Power", "Vehicle Power", "Troop Power",
    "Verification Status"
]

ws.row_dimensions[5].height = 26
for col_num, h in enumerate(headers, 1):
    cell = ws.cell(row=5, column=col_num, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border_cell

# Populate Rows
for row_idx, r in enumerate(records, 6):
    ws.row_dimensions[row_idx].height = 20
    is_user = (r['name'] == 'Heinzy300cm')
    tier = r['tier']
    
    tier_fill = fill_adv if "Advanced" in tier else (fill_mid if "Intermediate" in tier else fill_reg)
    if is_user:
        row_fill = fill_user
    else:
        row_fill = None

    row_data = [
        row_idx - 5,
        f"R{r['rank']}",
        r['mainBuildingLevel'],
        r['name'],
        r['uid'],
        r['authoritative_migrate_power'],
        r['tier'],
        r['passes_required'],
        r['total_power'],
        r['player_max_power'],
        r['building_power'],
        r['science_power'],
        r['hero_power'],
        r['tank_power'],
        r['army_power'],
        "100% IN-GAME VERIFIED"
    ]
    
    for col_idx, val in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=val)
        cell.font = font_user if is_user else font_data
        cell.border = border_cell
        
        if row_fill:
            cell.fill = row_fill
            
        # Alignments & Formatting
        if col_idx in [1, 2, 3]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx == 4:
            cell.alignment = Alignment(horizontal="left", vertical="center")
            if is_user:
                cell.font = font_user
        elif col_idx == 5:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.number_format = "@"
        elif col_idx == 6:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            cell.font = font_bold_data
        elif col_idx == 7:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = tier_fill
            cell.font = font_bold_data
        elif col_idx == 8:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(name="Segoe UI", size=10, bold=True, color="B91C1C" if val >= 20 else ("1D4ED8" if val == 15 else "15803D"))
        elif col_idx in [9, 10, 11, 12, 13, 14, 15]:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
        elif col_idx == 16:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(name="Segoe UI", size=9, bold=True, color="15803D")

# Auto-fit column widths
for col in ws.columns:
    max_len = 0
    col_letter = get_column_letter(col[0].column)
    for cell in col:
        if cell.row in [1, 2, 3]: # Skip banner rows for width calculation
            continue
        v_str = str(cell.value or '')
        if cell.number_format == "#,##0" and isinstance(cell.value, (int, float)):
            v_str = f"{cell.value:,.0f}"
        if len(v_str) > max_len:
            max_len = len(v_str)
    ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# Specific custom widths
ws.column_dimensions['A'].width = 8   # Rank
ws.column_dimensions['B'].width = 14  # Alliance Rank
ws.column_dimensions['C'].width = 11  # HQ
ws.column_dimensions['D'].width = 20  # Name
ws.column_dimensions['E'].width = 20  # UID
ws.column_dimensions['F'].width = 24  # Migration Score
ws.column_dimensions['G'].width = 22  # Tier
ws.column_dimensions['H'].width = 16  # Passes Required
ws.column_dimensions['I'].width = 18  # Total Power
ws.column_dimensions['J'].width = 19  # Max Power

# Freeze Panes at row 6
ws.freeze_panes = "A6"

# Hide requested columns (keep them in the workbook, but hide from view)
# Verification status (P), Rank (A), Alliance Rank (B), HQ Level (C), Player UID (E), Total Power (I)
for c_letter in ['A', 'B', 'C', 'E', 'I', 'P']:
    ws.column_dimensions[c_letter].hidden = True

wb.save(scratch_xlsx)
wb.save(desktop_xlsx)
print(f"Excel workbook created successfully:\n  Desktop: {desktop_xlsx}\n  Scratch: {scratch_xlsx}")
