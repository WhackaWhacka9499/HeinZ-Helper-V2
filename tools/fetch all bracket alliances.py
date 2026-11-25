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
OUT_DIR = REPO_ROOT / "data" / "json cache" / "bracket data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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
    while (next(L, index) && count++ < 120) {{
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
const stateQueue = {json.dumps(BRACKET_STATES)};
let lastQueryTime = 0;
const QUERY_INTERVAL_MS = 600; // 600ms between state queries
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
                    if (cmd === 'alliance.rank.limit' || cmd === 'alliance.rank') {{
                        const payload = dumpLuaTable(L, saved, 0, 3);
                        send({{kind: 'state_alliances_response', cmd: cmd, payload: payload}});
                    }}
                }}
            }}

            const now = Date.now();
            if (stateQueue.length > 0 && (now - lastQueryTime) >= QUERY_INTERVAL_MS) {{
                const targetState = stateQueue.shift();
                lastQueryTime = now;
                const lua = 'return SFSNetwork.SendMessage(MsgDefines.AllianceRankLimit, ' + targetState + ')';
                if (loadstring(L, allocStr(lua)) === 0) {{
                    pcall(L, 0, 0, 0);
                    send({{kind: 'state_queried', state: targetState, remaining: stateQueue.length}});
                }}
            }}

            if (stateQueue.length === 0 && (now - lastQueryTime) > 3000) {{
                send({{kind: 'all_states_queried'}});
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

send({{kind: 'ready', total_states: stateQueue.length}});
"""

_cd_spec = importlib.util.spec_from_file_location("client_discovery", str(REPO_ROOT / "tools" / "client discovery.py"))
_cd_mod = importlib.util.module_from_spec(_cd_spec)
_cd_spec.loader.exec_module(_cd_mod)
_target_pid = _cd_mod.resolve_target_pid()
session = frida.attach(_target_pid or 'Survival.exe')
script = session.create_script(js)

captured_by_state = {}

def on_message(m, d):
    if m['type'] == 'send':
        p = m['payload']
        kind = p.get('kind')
        if kind == 'state_queried':
            print(f"[QUERY] State {p.get('state')} dispatched ({p.get('remaining')} remaining)...", flush=True)
        elif kind == 'state_alliances_response':
            payload = p.get('payload', {})
            ranking = payload.get('allianceRanking') or payload.get('serverRanking') or payload.get('list') or {}
            if isinstance(ranking, dict) and ranking:
                # determine state from first item
                first = next(iter(ranking.values()))
                s_id = first.get('serverId')
                if s_id:
                    captured_by_state[s_id] = ranking
                    print(f"[RECV] >>> State {s_id}: Successfully captured {len(ranking)} ranked alliances! <<<", flush=True)
        elif kind == 'all_states_queried':
            print("[DONE] All state queries sent and settled.", flush=True)
        elif kind == 'error':
            print(f"[ERROR] {p.get('error')}", flush=True)
    elif m['type'] == 'error':
        print(f"[FRIDA ERROR] {m.get('description')}", flush=True)

script.on('message', on_message)
script.load()

# Wait for all states to return
start_t = time.time()
while time.time() - start_t < 25:
    if len(captured_by_state) >= len(BRACKET_STATES):
        break
    time.sleep(0.5)

session.detach()

print("\n" + "=" * 60)
print(f"AUTOMATED BRACKET FETCH SUMMARY: {len(captured_by_state)} / {len(BRACKET_STATES)} STATES")
print("=" * 60)

for s in sorted(BRACKET_STATES):
    ranking = captured_by_state.get(s, {})
    state_dir = OUT_DIR / f"state_{s}"
    state_dir.mkdir(parents=True, exist_ok=True)
    
    # Sort top 10
    top10 = []
    for k in sorted(ranking.keys(), key=lambda x: int(x) if str(x).isdigit() else 999):
        item = ranking[k]
        top10.append(item)
        if len(top10) >= 10:
            break
            
    out_alliances = state_dir / "top10_alliances.json"
    tmp_alliances = state_dir / f"top10_alliances.json.{os.getpid()}.tmp"
    with open(tmp_alliances, "w", encoding="utf-8") as f:
        json.dump(top10, f, indent=2, ensure_ascii=False)
    os.replace(tmp_alliances, out_alliances)
        
    print(f"State {s}: {len(top10)} Top Alliances saved to state_{s}/top10_alliances.json")
    for a in top10[:3]:
        print(f"   Rank {a.get('rank')}: [{a.get('abbr')}] {a.get('alliancename')} (Power: {a.get('fightpower'):,}) Leader: {a.get('leader')}")

print("\nPhase 1 Complete!")
