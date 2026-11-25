import frida
import json
import time
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

LUA_REQUEST = r"""
if not SFSNetwork or not MsgDefines or not MsgDefines.AllianceCompeteRankList then
    return "[-] SFSNetwork or MsgDefines not found"
end

-- Request Day (0), Week (1), and History (3)
SFSNetwork.SendMessage(MsgDefines.AllianceCompeteRankList, 0)
SFSNetwork.SendMessage(MsgDefines.AllianceCompeteRankList, 1)
pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceCompeteRankList, 3) end)

return "[+] Sent VS Duel ranking requests"
"""

LUA_EXTRACT = r"""
local acm = DataCenter and DataCenter.AllianceCompeteDataManager
if not acm then return "{}" end

local function serializeVal(v)
    local t = type(v)
    if t == "number" or t == "boolean" then
        return tostring(v)
    elseif t == "string" then
        local s = v:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t')
        return '"' .. s .. '"'
    elseif t == "table" then
        local isArr = true
        local maxI = 0
        local count = 0
        for k, _ in pairs(v) do
            count = count + 1
            if type(k) ~= "number" or k <= 0 or math.floor(k) ~= k then
                isArr = false
            elseif k > maxI then
                maxI = k
            end
        end
        if count == 0 then return "[]" end
        if isArr and maxI == count then
            local items = {}
            for i = 1, count do
                table.insert(items, serializeVal(v[i]))
            end
            return "[" .. table.concat(items, ",") .. "]"
        else
            local entries = {}
            for k, val in pairs(v) do
                table.insert(entries, string.format('"%s":%s', tostring(k), serializeVal(val)))
            end
            return "{" .. table.concat(entries, ",") .. "}"
        end
    else
        return "null"
    end
end

local data = {
    isOpen = acm:CheckIfAllianceCompeteOpen(),
    isInCompete = acm:CheckIfIsInCompete(),
    fightServerId = acm:GetFightServerId(),
    fightAllianceId = acm:GetFightAllianceId(),
    rushDataDay = acm:GetRushDataDay(),
    dayRank = acm:GetRankList(0) or {},
    weekRank = acm:GetRankList(1) or {},
    historyRank = acm:GetRankList(3) or {}
}

return serializeVal(data)
"""

FRIDA_JS = r"""
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcallk = nf('lua_pcallk', 'int', ['pointer', 'int', 'int', 'int', 'pointer', 'pointer']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const length = Memory.alloc(8);

function getString(L, index) {
    const p = str(L, index, length);
    const sz = Number(length.readU64());
    return sz === 0 ? '' : p.readUtf8String(sz);
}

function execLua(code, cb) {
    let done = false;
    const h = Interceptor.attach(mod.getExportByName('lua_pcallk'), {
        onEnter(args) {
            if (done) return;
            done = true;
            const L = args[0];
            const saved = top(L);
            try {
                const s = Memory.allocUtf8String(code);
                if (loadstring(L, s) === 0) {
                    if (pcallk(L, 0, 1, 0, ptr(0), ptr(0)) === 0) {
                        cb(null, getString(L, -1));
                    } else {
                        cb(getString(L, -1), null);
                    }
                } else {
                    cb('Syntax error: ' + getString(L, -1), null);
                }
            } catch(e) {
                cb(e.toString(), null);
            } finally {
                settop(L, saved);
                h.detach();
            }
        }
    });
}

rpc.exports = {
    evalLua(code) {
        return new Promise((resolve) => {
            execLua(code, (err, res) => {
                if (err) resolve({ success: false, error: err });
                else resolve({ success: true, result: res });
            });
        });
    }
};
"""

def main():
    import psutil
    target_pid = None
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and 'survival.exe' in p.info['name'].lower():
            target_pid = p.info['pid']
            break
            
    if not target_pid:
        print("[-] Survival.exe not running")
        return

    print(f"[+] Attaching to Survival.exe (PID {target_pid})...")
    session = frida.attach(target_pid)
    script = session.create_script(FRIDA_JS)
    script.load()

    print("[+] Requesting latest VS duel ranking packets from game server...")
    req_res = script.exports_sync.eval_lua(LUA_REQUEST)
    if not req_res.get('success'):
        print(f"[-] Request failed: {req_res.get('error')}")
        session.detach()
        return

    # Wait for server response
    time.sleep(1.8)

    print("[+] Extracting ranking data from memory...")
    data_res = script.exports_sync.eval_lua(LUA_EXTRACT)
    session.detach()

    if not data_res.get('success'):
        print(f"[-] Extraction failed: {data_res.get('error')}")
        return

    raw_json = data_res.get('result', '{}')
    data = json.loads(raw_json)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "vs_duel_rankings.json")
    tmp_json_path = f"{json_path}.{os.getpid()}.tmp"
    with open(tmp_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_json_path, json_path)
    print(f"[+] Saved raw JSON to: {json_path}")

    # Build Excel workbook
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    # remove default sheet
    wb.remove(wb.active)

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    sub_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    def populate_sheet(ws, title, rows):
        ws.views.sheetView[0].showGridLines = True
        ws.title = title
        
        headers = ["Rank", "Player Name", "Alliance Tag", "Score", "Score (Formatted)", "UID", "Alliance ID"]
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align

        for r_idx, r in enumerate(rows, start=1):
            name = str(r.get("name", "Unknown"))
            abbr = str(r.get("abbr", r.get("alName", "")))
            score = int(r.get("score", 0))
            uid = str(r.get("uid", ""))
            aid = str(r.get("aid", ""))
            score_fmt = f"{score:,}"
            
            row_data = [r_idx, name, abbr, score, score_fmt, uid, aid]
            ws.append(row_data)
            
            curr_row = r_idx + 1
            for col_idx in range(1, len(row_data) + 1):
                c = ws.cell(row=curr_row, column=col_idx)
                c.border = thin_border
                if col_idx in (1, 3):
                    c.alignment = center_align
                elif col_idx in (4, 5):
                    c.alignment = right_align
                else:
                    c.alignment = left_align

        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    day_rows = data.get("dayRank", [])
    week_rows = data.get("weekRank", [])

    ws_day = wb.create_sheet(title="Today's Duel Rankings")
    populate_sheet(ws_day, "Today's Duel Rankings", day_rows)

    ws_week = wb.create_sheet(title="Weekly Duel Totals")
    populate_sheet(ws_week, "Weekly Duel Totals", week_rows)

    # History days if present
    hist = data.get("historyRank", {})
    if isinstance(hist, dict):
        for day_k, day_list in hist.items():
            if isinstance(day_list, list) and len(day_list) > 0:
                ws_h = wb.create_sheet(title=f"Day {day_k} History")
                populate_sheet(ws_h, f"Day {day_k} History", day_list)
    elif isinstance(hist, list):
        for day_idx, day_list in enumerate(hist):
            if isinstance(day_list, list) and len(day_list) > 0:
                ws_h = wb.create_sheet(title=f"Day {day_idx + 1} History")
                populate_sheet(ws_h, f"Day {day_idx + 1} History", day_list)

    excel_path = os.path.join(base_dir, "vs_duel_rankings.xlsx")
    wb.save(excel_path)
    print(f"[+] Successfully exported {len(day_rows)} daily rows and {len(week_rows)} weekly rows to:")
    print(f"    {excel_path}")

    # Print top 10 preview
    print("\n--- TOP 10 TODAY'S DUEL RANKINGS ---")
    for i, r in enumerate(day_rows[:10], 1):
        print(f"#{i:2d} | {r.get('name')} [{r.get('abbr', '')}] | Score: {int(r.get('score', 0)):,} | UID: {r.get('uid')}")

if __name__ == "__main__":
    main()
