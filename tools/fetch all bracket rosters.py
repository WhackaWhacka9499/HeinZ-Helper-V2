import frida
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import importlib.util

BRACKET_STATES = list(range(689, 705))
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "json cache" / "bracket data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Collect all alliance UIDs across all 15 states
alliance_queue = []
alliance_metadata = {} # aid -> {state, abbr, name, rank, fightpower}

for s in BRACKET_STATES:
    t10_path = DATA_DIR / f"state_{s}" / "top10_alliances.json"
    if not t10_path.exists():
        print(f"Warning: {t10_path} does not exist!")
        continue
    top10 = json.load(open(t10_path, "r", encoding="utf-8"))
    for item in top10:
        aid = item.get("uid")
        if aid:
            alliance_queue.append(aid)
            alliance_metadata[aid] = {
                "state": s,
                "abbr": item.get("abbr", ""),
                "name": item.get("alliancename", ""),
                "rank": item.get("rank"),
                "fightpower": item.get("fightpower", 0)
            }

print(f"Loaded {len(alliance_queue)} alliances to fetch across {len(BRACKET_STATES)} states.")

js = f"""
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
    while (next(L, index) && count++ < 150) {{
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
const queue = {json.dumps(alliance_queue)};
let lastQueryTime = 0;
const QUERY_INTERVAL_MS = 380; // 380ms between alliance roster queries
let busy = false;
let done = false;

Interceptor.attach(mod.getExportByName('lua_pcallk'), {{
    onEnter(args) {{
        if (busy || done) return;
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
                    if (cmd === 'al.rank') {{
                        const payload = dumpLuaTable(L, saved, 0, 3);
                        send({{kind: 'al_rank_response', payload: payload}});
                    }}
                }}
            }}

            const now = Date.now();
            if (queue.length > 0 && (now - lastQueryTime) >= QUERY_INTERVAL_MS) {{
                const aid = queue.shift();
                lastQueryTime = now;
                const lua = 'return SFSNetwork.SendMessage(MsgDefines.AlRank, \"' + aid + '\")';
                if (loadstring(L, allocStr(lua)) === 0) {{
                    pcall(L, 0, 0, 0);
                    if (queue.length % 10 === 0 || queue.length === 0) {{
                        send({{kind: 'progress', remaining: queue.length}});
                    }}
                }}
            }}

            if (queue.length === 0 && (now - lastQueryTime) > 4000) {{
                send({{kind: 'all_dispatched'}});
                done = true;
            }}
        }} catch (e) {{
            send({{kind: 'error', error: String(e)}});
        }} finally {{
            settop(L, saved);
            busy = false;
        }}
    }}
}});

send({{kind: 'ready', total: queue.length}});
"""

_cd_spec = importlib.util.spec_from_file_location("client_discovery", str(REPO_ROOT / "tools" / "client discovery.py"))
_cd_mod = importlib.util.module_from_spec(_cd_spec)
_cd_spec.loader.exec_module(_cd_mod)
_target_pid = _cd_mod.resolve_target_pid()
session = frida.attach(_target_pid or 'Survival.exe')
script = session.create_script(js)

captured_rosters = {} # aid -> list of members

def on_message(m, d):
    if m['type'] == 'send':
        p = m['payload']
        kind = p.get('kind')
        if kind == 'progress':
            rem = p.get('remaining')
            print(f"Dispatched queries... {rem} alliances remaining", flush=True)
        elif kind == 'al_rank_response':
            payload = p.get('payload', {})
            aid = payload.get('allianceId')
            members = payload.get('list', {})
            if aid and isinstance(members, dict):
                member_list = list(members.values())
                captured_rosters[aid] = member_list
                meta = alliance_metadata.get(aid, {})
                s = meta.get("state", "?")
                abbr = meta.get("abbr", "?")
                print(f"[RECV] State {s} | [{abbr}] -> {len(member_list)} members ({len(captured_rosters)}/{len(alliance_queue)} total)", flush=True)
        elif kind == 'all_dispatched':
            print("All alliance roster queries completed.", flush=True)
        elif kind == 'error':
            print("ERROR:", p.get('error'), flush=True)
    elif m['type'] == 'error':
        print("FRIDA ERROR:", m.get('description'), flush=True)

script.on('message', on_message)
script.load()

# Allow up to 90 seconds for all 150 rosters to be gathered
start_t = time.time()
while time.time() - start_t < 90:
    if len(captured_rosters) >= len(alliance_queue):
        break
    time.sleep(0.5)

session.detach()

print("\n" + "=" * 60)
print(f"ALLIANCE ROSTER FETCH COMPLETE: {len(captured_rosters)} / {len(alliance_queue)} ALLIANCES CAPTURED")
print("=" * 60)

# Organize by state and save
for s in BRACKET_STATES:
    state_dir = DATA_DIR / f"state_{s}"
    state_dir.mkdir(parents=True, exist_ok=True)
    
    t10_path = state_dir / "top10_alliances.json"
    if not t10_path.exists():
        continue
    top10 = json.load(open(t10_path, "r", encoding="utf-8"))
    
    state_rosters = []
    total_state_players = 0
    for al in top10:
        aid = al.get("uid")
        members = captured_rosters.get(aid, [])
        total_state_players += len(members)
        state_rosters.append({
            "allianceId": aid,
            "abbr": al.get("abbr"),
            "name": al.get("alliancename"),
            "rank": al.get("rank"),
            "fightpower": al.get("fightpower"),
            "leader": al.get("leader"),
            "memberCount": len(members),
            "members": members
        })
        
    out_file = state_dir / "top10_alliance_rosters.json"
    tmp_file = state_dir / f"top10_alliance_rosters.json.{os.getpid()}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(state_rosters, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, out_file)
        
    print(f"State {s}: Saved {len(state_rosters)} rosters with {total_state_players} total players to {out_file.name}")

print("\nPhase 2 Complete!")
