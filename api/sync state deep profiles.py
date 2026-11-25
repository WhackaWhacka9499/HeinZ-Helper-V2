import frida
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

import importlib.util

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
DATA_DIR = REPO_ROOT / "data" / "json cache" / "bracket data"
LEGACY_DATA_DIR = Path(r"data/cache/bracket_data")
XLSX_DIR = REPO_ROOT / "data" / "bracket states"
XLSX_DIR.mkdir(parents=True, exist_ok=True)
CACHE_PATH = REPO_ROOT / "data" / "json cache" / "all_players_profile_cache.json"
MANIFEST_PATH = REPO_ROOT / "data" / "bracket sheets manifest.json"

FILE_MAP = {689: '1kzwtL7JaSJcl6X9qCHMFjKvLiXDlZVVAFWLImuuhT_c', 690: '1Ne8iGqUhgkokLqOOCVnybrDm05VTap57MCeZCQdzTms', 691: '1GT5bMLGHUS9S4etLll-wNIKb2T1d3GJXemhOmMelXxY', 692: '1FMcE6xztzRVy5aiis6gvXWhngN3Gp8nrDOAKahoP9gc', 693: '1Z-Z_gKT-toLTvcbT7BF5vHlSGZ0VG_9hQz68L_ux8u4', 694: '1q44x2sO0U1igCYYfl_HE7ctyvt_DMKds9XQ4UEXWttc', 695: '1N-grVFpOc5tRRRZzxd6QXRKtlijkE5Dx3JBSM4Nt-74', 696: '1trr7NlBwLTz92sCZLlEIDkLkmcMfeoXDlkMjx2nj1qo', 697: '11DkfxxxxKT9s78x6P-QXRYYCHmVMBOBVb3sAnLrCr0U', 698: '1Bx_7P2Y6uc46qyKjdxB3M1cdGJugj_UbkOGK5Q-1nnw', 699: '1tS6jdaBeRDCssUXY0IWPEPBk7kI9plePXstp6vraY44', 700: '1Y8wBL1shyh3hIOm3riEzhYhLf5Zlxqsotyg0CFCjvjg', 701: '1Dhca-KoNImHL5RoH3YMXnhAVlXdvx8zAzlWoZnK6_Ug', 702: '15Cg0oxlAu8Nr1eTAnzcrK0vX5S4kKOKpE-YWd1W0qkk', 703: '1GqIYAevzf9oTx1mitwlrD9qLAbd_R3mFF1VDqPN_xNc', 704: '1nlRHtLJKGdlJAFAbcMQCad4P8sNTZ0h2OFsXWoozDdg'}
if MANIFEST_PATH.exists():
    try:
        _mf = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        FILE_MAP = {int(k): v["id"] for k, v in _mf.get("spreadsheets", {}).items() if v.get("id")}
    except Exception:
        pass


def _resolve_active_pid():
    disc_path = TOOLS_DIR / "client discovery.py"
    if disc_path.exists():
        spec = importlib.util.spec_from_file_location("client_discovery", str(disc_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            running = mod.find_running_processes()
            if running:
                mains = [p for p in running if str(p.get("role") or "").lower() == "main"]
                return int((mains[0] if mains else running[0])["pid"])
    return "Survival.exe"

def load_cache():
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    tmp_path = f"{CACHE_PATH}.{os.getpid()}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    os.replace(tmp_path, CACHE_PATH)

def get_tier_and_passes(migrate_power):
    if migrate_power is None or migrate_power == 0:
        return ("Unknown", 0)
    if migrate_power <= 20000000:
        return ("Regular (Che1)", 10)
    elif migrate_power <= 40000000:
        return ("Intermediate (Che2)", 15)
    elif migrate_power <= 100000000:
        return ("Advanced (Che3)", 20)
    else:
        return ("Elite (Che4)", 50)

def role_str(rank_val):
    role_map = {1: 'R1', 2: 'R2', 3: 'R3', 4: 'R4', 5: 'Leader (R5)'}
    return role_map.get(rank_val, f'R{rank_val}')

def fetch_profiles_for_state(state_id, uids_to_query):
    if not uids_to_query:
        print(f"State {state_id}: All {len(uids_to_query)} profiles already in cache!")
        return {}

    print(f"\n[QUERY DISPATCH] State {state_id}: Dispatched {len(uids_to_query)} player queries at 70ms interval (~{len(uids_to_query)*0.07:.1f}s)...")

    js_code = f"""
    const mod = Process.getModuleByName('xlua.dll');
    const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
    const top = nf('lua_gettop', 'int', ['pointer']);
    const settop = nf('lua_settop', 'void', ['pointer', 'int']);
    const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
    const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
    const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
    const rawi = nf('lua_rawgeti', 'int', ['pointer', 'int', 'int64']);
    const raw = nf('lua_rawget', 'int', ['pointer', 'int']);
    const next = nf('lua_next', 'int', ['pointer', 'int']);
    const nil = nf('lua_pushnil', 'void', ['pointer']);
    const push = nf('lua_pushstring', 'pointer', ['pointer', 'pointer']);
    const typ = nf('lua_type', 'int', ['pointer', 'int']);
    const num = nf('lua_tonumberx', 'double', ['pointer', 'int', 'pointer']);
    const ptrfn = nf('lua_topointer', 'pointer', ['pointer', 'int']);
    const check = nf('lua_checkstack', 'int', ['pointer', 'int']);
    const length = Memory.alloc(8);
    const registry = nf('xlua_get_registry_index', 'int', [])();

    const stringCache = new Map();
    function allocStr(s) {{
        if (!stringCache.has(s)) stringCache.set(s, Memory.allocUtf8String(s));
        return stringCache.get(s);
    }}

    function field(L, index, key) {{
        push(L, allocStr(key));
        return raw(L, index);
    }}

    function getString(L, index, maxLen = 256) {{
        if (typ(L, index) !== 4) return null;
        const p = str(L, index, length);
        const sz = Number(length.readU64());
        if (sz === 0) return '';
        if (sz > maxLen) return null;
        return p.readUtf8String(sz);
    }}

    function getNumber(L, index) {{
        return typ(L, index) === 3 ? num(L, index, ptr(0)) : null;
    }}

    function dumpLuaTable(L, index, depth = 0, maxDepth = 2) {{
        if (depth > maxDepth) return '<truncated>';
        const saved = top(L);
        const obj = {{}};
        nil(L);
        let count = 0;
        while (next(L, index) && count++ < 80) {{
            let key = null;
            const kt = typ(L, -2);
            if (kt === 4) key = getString(L, -2, 80);
            else if (kt === 3) key = String(getNumber(L, -2));
            else key = 'k_' + kt;
            
            let val = null;
            const vt = typ(L, -1);
            if (vt === 1) val = true;
            else if (vt === 3) val = getNumber(L, -1);
            else if (vt === 4) val = getString(L, -1, 512);
            else if (vt === 5) val = dumpLuaTable(L, top(L), depth + 1, maxDepth);
            else val = '<type ' + vt + '>';
            
            if (key !== null) obj[key] = val;
            settop(L, top(L) - 1);
        }}
        settop(L, saved);
        return obj;
    }}

    let handler = null;
    const queue = {json.dumps(uids_to_query)};
    let lastQueryTime = 0;
    const QUERY_INTERVAL_MS = 70;
    let busy = false;
    let drainedSent = false;

    Interceptor.attach(mod.getExportByName('lua_pcallk'), {{
        onEnter(args) {{
            if (busy) return;
            const L = args[0];
            const nargs = args[1].toInt32();
            const saved = top(L);
            busy = true;

            try {{
                if (nargs === 2) {{
                    if (handler === null) {{
                        if (rawi(L, registry, 2) === 5) {{
                            const g = top(L);
                            if (field(L, g, 'GameMain') === 5 && field(L, top(L), 'Protocal') === 6) {{
                                handler = ptrfn(L, -1).toString();
                            }}
                            settop(L, g);
                        }}
                    }}
                    if (ptrfn(L, saved - nargs).toString() === handler) {{
                        const cmd = getString(L, saved - 1, 80);
                        if (cmd === 'get.new.user.info' || cmd === 'migrate.user.info') {{
                            const payload = dumpLuaTable(L, saved, 0, 2);
                            send({{kind: 'user_info', payload: payload}});
                        }}
                    }}
                }}

                const now = Date.now();
                if (queue.length > 0 && (now - lastQueryTime) >= QUERY_INTERVAL_MS) {{
                    const targetUid = queue.shift();
                    lastQueryTime = now;
                    const lua = 'return DataCenter.PlayerInfoDataManager:GetPlayerInfoFromServer(\"' + targetUid + '\")';
                    if (loadstring(L, allocStr(lua)) === 0) {{
                        pcall(L, 0, 0, 0);
                        if (queue.length % 50 === 0 || queue.length === 0) {{
                            send({{kind: 'progress', remaining: queue.length}});
                        }}
                    }}
                }}

                if (queue.length === 0 && (now - lastQueryTime) > 3000 && !drainedSent) {{
                    drainedSent = true;
                    send({{kind: 'drained'}});
                }}
            }} catch (e) {{
                send({{kind: 'error', error: String(e)}});
            }} finally {{
                settop(L, saved);
                busy = false;
            }}
        }}
    }});

    send({{kind: 'ready', count: queue.length}});
    """

    session = frida.attach(_resolve_active_pid())
    script = session.create_script(js_code)

    captured = {}
    drained = False

    def on_message(m, d):
        nonlocal drained
        if m['type'] == 'send':
            p = m['payload']
            kind = p.get('kind')
            if kind == 'user_info':
                pld = p.get('payload', {})
                uid = str(pld.get('uid'))
                if uid and uid != 'None':
                    captured[uid] = pld
            elif kind == 'progress':
                rem = p.get('remaining')
                print(f"State {state_id} progress: {len(uids_to_query) - rem}/{len(uids_to_query)} sent | {len(captured)} responses received", flush=True)
            elif kind == 'drained':
                drained = True
        elif m['type'] == 'error':
            print(f"Frida error: {m.get('description')}", flush=True)

    script.on('message', on_message)
    script.load()

    # Wait for completion
    timeout = time.time() + (len(uids_to_query) * 0.12) + 10
    while not drained and len(captured) < len(uids_to_query) and time.time() < timeout:
        time.sleep(0.5)

    session.detach()
    print(f"State {state_id}: Finished fetching. Captured {len(captured)}/{len(uids_to_query)} profiles.")
    return captured

def build_state_master_workbook(state_id, state_alliances):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    DARK_NAVY = "1B365D"
    ACCENT_BLUE = "2A5C9A"
    CARD_BG = "F8FAFC"
    BORDER_GRAY = "E2E8F0"
    BORDER_MED = "CBD5E1"

    ADV_BG = "E6E6FA"       # Lavender / Light Purple
    MID_BG = "E0F2FE"       # Light Ice Blue
    REG_BG = "F0FDF4"       # Light Green
    ELITE_BG = "FCE7F3"     # Light Pink
    GOLD_BG = "FEF3C7"      # Gold

    font_title = Font(name="Segoe UI", size=15, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Segoe UI", size=9.5, italic=True, color="E2E8F0")
    font_sec_hdr = Font(name="Segoe UI", size=11, bold=True, color="1B365D")
    font_table_hdr = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_sub_hdr = Font(name="Segoe UI", size=9.5, bold=True, color="334155")
    font_data = Font(name="Segoe UI", size=9.5)
    font_bold_data = Font(name="Segoe UI", size=9.5, bold=True)
    font_card_num = Font(name="Segoe UI", size=14, bold=True, color="1B365D")
    font_card_lbl = Font(name="Segoe UI", size=8.5, bold=True, color="64748B")

    fill_title = PatternFill(start_color=DARK_NAVY, end_color=DARK_NAVY, fill_type="solid")
    fill_hdr = PatternFill(start_color=ACCENT_BLUE, end_color=ACCENT_BLUE, fill_type="solid")
    fill_adv = PatternFill(start_color=ADV_BG, end_color=ADV_BG, fill_type="solid")
    fill_mid = PatternFill(start_color=MID_BG, end_color=MID_BG, fill_type="solid")
    fill_reg = PatternFill(start_color=REG_BG, end_color=REG_BG, fill_type="solid")
    fill_elite = PatternFill(start_color=ELITE_BG, end_color=ELITE_BG, fill_type="solid")
    fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    fill_card = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")

    thin_border_side = Side(style='thin', color=BORDER_GRAY)
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    double_bottom = Border(bottom=Side(style='double', color=DARK_NAVY), top=Side(style='thin', color=BORDER_MED))

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
    ws_ov["A2"] = f"Official In-Game Verified Migration Scores | Preparation Phase (Group 200162 | Target States: 689 - 704)"
    ws_ov["A2"].font = font_subtitle
    ws_ov["A2"].fill = fill_title
    ws_ov["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws_ov.row_dimensions[2].height = 20

    total_state_members = sum(len(a['members']) for a in state_alliances)
    total_state_passes = sum(a['total_passes_required'] for a in state_alliances)
    total_state_power = sum(a['total_fightpower'] for a in state_alliances)
    total_elite = sum(a['tier_distribution'].get('Elite (Che4)', 0) for a in state_alliances)

    cards = [
        ("TOTAL TOP 10 POWER", f"{total_state_power / 1e9:.2f}B", 2),
        ("TOTAL ACTIVE MEMBERS", f"{total_state_members:,}", 5),
        ("TOTAL PASSES NEEDED", f"{total_state_passes:,}", 8),
        ("ELITE TIER PLAYERS", f"{total_elite}", 11)
    ]

    for label, val, col_idx in cards:
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

    # Table Header
    ws_ov.cell(row=7, column=1, value="TOP 10 ALLIANCE SUMMARY & TIER BREAKDOWN").font = font_sec_hdr
    headers = [
        "State Rank", "Alliance Tag", "Alliance Full Name", "Alliance Leader", "Total Combat Power",
        "Member Count", "Total Passes Needed", "Avg Passes/Member", "Elite (>100M)", "Advanced (40-100M)",
        "Intermediate (20-40M)", "Regular (<=20M)", "Top Scorer (Migration Score)"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws_ov.cell(row=8, column=col_idx, value=h)
        cell.font = font_table_hdr
        cell.fill = fill_hdr
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_cell
    ws_ov.row_dimensions[8].height = 24

    cur_row = 9
    for al in state_alliances:
        members_cnt = len(al['members'])
        avg_passes = al['total_passes_required'] / members_cnt if members_cnt else 0
        tag = al['abbr']
        clean_name = al['name'].replace(':', '-').replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '')
        tab_title = f"{tag} - {clean_name}"[:31]

        top_scorer = al['members'][0]['name'] if al['members'] else "N/A"
        top_score_val = al['members'][0]['authoritative_migrate_power'] if al['members'] else 0

        ws_ov.cell(row=cur_row, column=1, value=al['rank']).alignment = Alignment(horizontal="center")
        ws_ov.cell(row=cur_row, column=2, value=f"[{tag}]").alignment = Alignment(horizontal="center")
        
        # Link to tab
        link_cell = ws_ov.cell(row=cur_row, column=3, value=f"=HYPERLINK(\"#'{tab_title}'!A1\", \"{al['name']}\")")
        link_cell.font = Font(name="Segoe UI", size=9.5, color="2563EB", underline="single")
        link_cell.alignment = Alignment(horizontal="left")

        ws_ov.cell(row=cur_row, column=4, value=al.get('leader', '')).alignment = Alignment(horizontal="left")
        
        c_pow = ws_ov.cell(row=cur_row, column=5, value=al['total_fightpower'])
        c_pow.number_format = '#,##0'
        c_pow.alignment = Alignment(horizontal="right")

        ws_ov.cell(row=cur_row, column=6, value=members_cnt).alignment = Alignment(horizontal="center")
        
        c_pass = ws_ov.cell(row=cur_row, column=7, value=al['total_passes_required'])
        c_pass.number_format = '#,##0'
        c_pass.alignment = Alignment(horizontal="right")

        c_avg = ws_ov.cell(row=cur_row, column=8, value=f"{avg_passes:.1f}")
        c_avg.alignment = Alignment(horizontal="center")

        c_el = ws_ov.cell(row=cur_row, column=9, value=al['tier_distribution'].get('Elite (Che4)', 0))
        c_el.alignment = Alignment(horizontal="center")
        if c_el.value > 0: c_el.fill = fill_elite

        c_adv = ws_ov.cell(row=cur_row, column=10, value=al['tier_distribution'].get('Advanced (Che3)', 0))
        c_adv.alignment = Alignment(horizontal="center")
        if c_adv.value > 0: c_adv.fill = fill_adv

        c_mid = ws_ov.cell(row=cur_row, column=11, value=al['tier_distribution'].get('Intermediate (Che2)', 0))
        c_mid.alignment = Alignment(horizontal="center")
        if c_mid.value > 0: c_mid.fill = fill_mid

        c_reg = ws_ov.cell(row=cur_row, column=12, value=al['tier_distribution'].get('Regular (Che1)', 0))
        c_reg.alignment = Alignment(horizontal="center")
        if c_reg.value > 0: c_reg.fill = fill_reg

        ws_ov.cell(row=cur_row, column=13, value=f"{top_scorer} ({top_score_val:,})").alignment = Alignment(horizontal="left")

        for c in range(1, 14):
            ws_ov.cell(row=cur_row, column=c).border = border_cell
            if c != 3: ws_ov.cell(row=cur_row, column=c).font = font_data
        
        ws_ov.row_dimensions[cur_row].height = 20
        cur_row += 1

    # Overview Totals Row
    ws_ov.cell(row=cur_row, column=1, value="")
    ws_ov.cell(row=cur_row, column=2, value="TOTAL")
    ws_ov.cell(row=cur_row, column=3, value="State Top 10 Combined")
    ws_ov.cell(row=cur_row, column=4, value="")
    c_tot_pow = ws_ov.cell(row=cur_row, column=5, value=f"=SUM(E9:E{cur_row-1})")
    c_tot_pow.number_format = '#,##0'
    ws_ov.cell(row=cur_row, column=6, value=f"=SUM(F9:F{cur_row-1})")
    c_tot_pass = ws_ov.cell(row=cur_row, column=7, value=f"=SUM(G9:G{cur_row-1})")
    c_tot_pass.number_format = '#,##0'
    c_tot_avg = ws_ov.cell(row=cur_row, column=8, value=f"=AVERAGE(H9:H{cur_row-1})")
    c_tot_avg.number_format = '0.0'
    ws_ov.cell(row=cur_row, column=9, value=f"=SUM(I9:I{cur_row-1})")
    ws_ov.cell(row=cur_row, column=10, value=f"=SUM(J9:J{cur_row-1})")
    ws_ov.cell(row=cur_row, column=11, value=f"=SUM(K9:K{cur_row-1})")
    ws_ov.cell(row=cur_row, column=12, value=f"=SUM(L9:L{cur_row-1})")
    ws_ov.cell(row=cur_row, column=13, value="")

    for c in range(1, 14):
        cell = ws_ov.cell(row=cur_row, column=c)
        cell.font = font_bold_data
        cell.fill = fill_total
        cell.border = double_bottom
        if c in [5, 7]: cell.alignment = Alignment(horizontal="right")
        elif c in [1, 2, 6, 8, 9, 10, 11, 12]: cell.alignment = Alignment(horizontal="center")
    ws_ov.row_dimensions[cur_row].height = 22

    # Tier Cutoff Matrix
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
        ("Che2", "Intermediate", "20,000,001 - 40,000,000 Power", "15 Passes", "Standard active combatant tier", fill_mid),
        ("Che3", "Advanced", "40,000,001 - 100,000,000 Power", "20 Passes", "High combatant tier, requires careful state balancing", fill_adv),
        ("Che4", "Elite", "> 100,000,000 Power", "50 Passes", "Requires President Approval / Strict Bracket Cap", fill_elite)
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

    # 2. INDIVIDUAL ALLIANCE TABS WITH FULL 15 COLUMNS
    for al in state_alliances:
        tag = al['abbr']
        clean_name = al['name'].replace(':', '-').replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '')
        tab_title = f"{tag} - {clean_name}"[:31]
        
        ws_al = wb.create_sheet(title=tab_title)
        ws_al.views.sheetView[0].showGridLines = True

        # Header Banner
        ws_al.merge_cells("A1:O1")
        ws_al["A1"] = f"[{tag}] {al['name']} | STATE {state_id} RANK #{al['rank']} ALLIANCE ROSTER"
        ws_al["A1"].font = font_title
        ws_al["A1"].fill = fill_title
        ws_al["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws_al.row_dimensions[1].height = 30

        ws_al.merge_cells("A2:O2")
        ws_al["A2"] = f"Leader: {al.get('leader', 'N/A')} | Total Power: {al['total_fightpower']:,} | Members: {len(al['members'])} | Passes: {al['total_passes_required']:,}"
        ws_al["A2"].font = font_subtitle
        ws_al["A2"].fill = fill_title
        ws_al["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws_al.row_dimensions[2].height = 20

        # Back link
        ws_al.cell(row=3, column=1, value=f"=HYPERLINK(\"#'State {state_id} Overview'!A1\", \"<- Back to State {state_id} Overview\")").font = Font(name="Segoe UI", size=9.5, color="2563EB", underline="single")

        # 15 Columns Headers
        r_headers = [
            "Rank", "Alliance Role", "HQ Level", "Player Name", "Player UID",
            "Official Migration Score", "Migration Tier", "Passes Required", "Current Power",
            "Max Historical Power", "Building Power", "Tech Power", "Hero Power", "Vehicle Power", "Troop Power"
        ]

        for col_idx, rh in enumerate(r_headers, 1):
            cell = ws_al.cell(row=5, column=col_idx, value=rh)
            cell.font = font_table_hdr
            cell.fill = fill_hdr
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border_cell
        ws_al.row_dimensions[5].height = 24

        m_row = 6
        for idx, m in enumerate(al['members'], 1):
            mp = m.get('authoritative_migrate_power', 0)
            tier = m.get('tier', 'Regular (Che1)')
            passes = m.get('passes_required', 10)
            role = role_str(m.get('rank', 1))

            ws_al.cell(row=m_row, column=1, value=idx).alignment = Alignment(horizontal="center")
            ws_al.cell(row=m_row, column=2, value=role).alignment = Alignment(horizontal="center")
            ws_al.cell(row=m_row, column=3, value=m.get('mainBuildingLevel', 0)).alignment = Alignment(horizontal="center")
            ws_al.cell(row=m_row, column=4, value=m.get('name', '')).alignment = Alignment(horizontal="left")
            ws_al.cell(row=m_row, column=5, value=str(m.get('uid', ''))).alignment = Alignment(horizontal="center")

            c_mp = ws_al.cell(row=m_row, column=6, value=mp)
            c_mp.number_format = '#,##0'
            c_mp.alignment = Alignment(horizontal="right")

            c_t = ws_al.cell(row=m_row, column=7, value=tier)
            c_t.alignment = Alignment(horizontal="center")
            if "Elite" in tier: c_t.fill = fill_elite
            elif "Advanced" in tier: c_t.fill = fill_adv
            elif "Intermediate" in tier: c_t.fill = fill_mid
            elif "Regular" in tier: c_t.fill = fill_reg

            ws_al.cell(row=m_row, column=8, value=passes).alignment = Alignment(horizontal="center")

            for col_idx, key in enumerate(['total_power', 'player_max_power', 'building_power', 'science_power', 'hero_power', 'tank_power', 'army_power'], 9):
                c_val = ws_al.cell(row=m_row, column=col_idx, value=m.get(key, 0))
                c_val.number_format = '#,##0'
                c_val.alignment = Alignment(horizontal="right")

            for c in range(1, 16):
                ws_al.cell(row=m_row, column=c).border = border_cell
                ws_al.cell(row=m_row, column=c).font = font_data
            
            ws_al.row_dimensions[m_row].height = 19
            m_row += 1

        # Roster Total Row
        ws_al.cell(row=m_row, column=1, value="")
        ws_al.cell(row=m_row, column=2, value="TOTAL")
        ws_al.cell(row=m_row, column=3, value="")
        ws_al.cell(row=m_row, column=4, value=f"{len(al['members'])} Members")
        ws_al.cell(row=m_row, column=5, value="")
        
        c_tot_mp = ws_al.cell(row=m_row, column=6, value=f"=SUM(F6:F{m_row-1})")
        c_tot_mp.number_format = '#,##0'
        ws_al.cell(row=m_row, column=7, value="")
        c_tot_pass = ws_al.cell(row=m_row, column=8, value=f"=SUM(H6:H{m_row-1})")
        c_tot_pass.number_format = '#,##0'

        for col_idx, col_let in enumerate(['I', 'J', 'K', 'L', 'M', 'N', 'O'], 9):
            c_sum = ws_al.cell(row=m_row, column=col_idx, value=f"=SUM({col_let}6:{col_let}{m_row-1})")
            c_sum.number_format = '#,##0'
            c_sum.alignment = Alignment(horizontal="right")

        for c in range(1, 16):
            cell = ws_al.cell(row=m_row, column=c)
            cell.font = font_bold_data
            cell.fill = fill_total
            cell.border = double_bottom
            if c in [6, 8, 9, 10, 11, 12, 13, 14, 15]: cell.alignment = Alignment(horizontal="right")
            elif c in [1, 2, 3, 5, 7]: cell.alignment = Alignment(horizontal="center")
        ws_al.row_dimensions[m_row].height = 22

    # Column Auto-Widths
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row in [1, 2]: continue
                val = str(cell.value or '')
                if val.startswith('='): val = "123,456,789"
                max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 11)

    out_file = XLSX_DIR / f"State {state_id} Migration.xlsx"
    wb.save(out_file)
    print(f"Master workbook generated: {out_file.name} ({os.path.getsize(out_file):,} bytes)")
    return out_file

def sync_state(state_id):
    print("\n" + "=" * 70)
    print(f"PROCESSING STATE {state_id} FOR COMPLETE 15-COLUMN MASTER DATA")
    print("=" * 70)

    roster_path = DATA_DIR / f"state_{state_id}" / "top10_alliance_rosters.json"
    if not roster_path.exists() and LEGACY_DATA_DIR.exists():
        roster_path = LEGACY_DATA_DIR / f"state_{state_id}" / "top10_alliance_rosters.json"
    if not roster_path.exists():
        print(f"Error: {roster_path} does not exist!")
        return False

    with open(roster_path, "r", encoding="utf-8") as f:
        rosters = json.load(f)

    cache = load_cache()
    all_uids = []
    for al in rosters:
        for m in al.get('members', []):
            uid = str(m.get('uid'))
            if uid: all_uids.append(uid)

    missing_uids = [u for u in all_uids if u not in cache]
    print(f"State {state_id}: Total members: {len(all_uids)} | Cached: {len(all_uids) - len(missing_uids)} | To fetch: {len(missing_uids)}")

    if missing_uids:
        new_profiles = fetch_profiles_for_state(state_id, missing_uids)
        cache.update(new_profiles)
        save_cache(cache)

    # Reconstruct Alliances with deep profile data
    state_alliances = []
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
                'name': pld.get('name') or m.get('name'),
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
                'status': 'VERIFIED_IN_GAME' if mp > 0 else 'PENDING'
            })
            
        members_data.sort(key=lambda x: (x['authoritative_migrate_power'], x['total_power']), reverse=True)
        total_passes = sum(m['passes_required'] for m in members_data)
        tier_counts = {}
        for m in members_data:
            tier_counts[m['tier']] = tier_counts.get(m['tier'], 0) + 1

        state_alliances.append({
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

    # Generate full 15-column Excel workbook
    xlsx_path = build_state_master_workbook(state_id, state_alliances)

    # Direct Native Google Spreadsheet Sync (preserves formatting & formulas)
    sync_mod_path = TOOLS_DIR / "sync bracket drive sheets.py"
    if sync_mod_path.exists():
        spec = importlib.util.spec_from_file_location("sync_bracket_drive_sheets", str(sync_mod_path))
        if spec and spec.loader:
            smod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(smod)
            res = smod.sync_single_state_to_drive(state_id, state_alliances)
            print(f"State {state_id} Migration: Native Google Sheet updated ({res['spreadsheet_id']})")

    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        s_id = int(sys.argv[1])
        sync_state(s_id)
    else:
        # Test on State 689
        sync_state(689)
