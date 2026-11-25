import frida
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

root = r"data/cache"
top10_info_path = os.path.join(root, "state_694_top10_alliances.json")
output_rosters_path = os.path.join(root, "top10_alliance_rosters.json")

alliances = json.load(open(top10_info_path, 'r', encoding='utf-8'))
aid_list = [a['uid'] for a in alliances]
print(f"Loaded {len(alliances)} top alliances: {aid_list}")

js_code = f"""
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {{scheduling: 'exclusive'}});
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
const queue = {json.dumps(aid_list)};
let lastQueryTime = 0;
const QUERY_INTERVAL_MS = 650;
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
                        send({{
                            kind: 'al_rank_response',
                            payload: payload
                        }});
                    }}
                }}
            }}

            const now = Date.now();
            if (queue.length > 0 && (now - lastQueryTime) >= QUERY_INTERVAL_MS) {{
                const aid = queue.shift();
                lastQueryTime = now;
                const luaCode = 'return SFSNetwork.SendMessage(MsgDefines.AlRank, \"' + aid + '\")';
                const codePtr = allocStr(luaCode);
                if (loadstring(L, codePtr) === 0) {{
                    pcall(L, 0, 0, 0);
                    send({{kind: 'query_dispatched', aid: aid, remaining: queue.length}});
                }}
            }}

            if (queue.length === 0 && (now - lastQueryTime) > 3000) {{
                send({{kind: 'all_rosters_dispatched'}});
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

send({{kind: 'ready', total_alliances: queue.length}});
"""

session = frida.attach('Survival.exe')
script = session.create_script(js_code)

captured_rosters = {}

def on_message(message, data):
    if message['type'] == 'send':
        p = message['payload']
        kind = p.get('kind')
        if kind == 'al_rank_response':
            pld = p.get('payload', {})
            aid = pld.get('allianceId')
            members = pld.get('list', {})
            if aid and members:
                captured_rosters[aid] = list(members.values()) if isinstance(members, dict) else members
                print(f"[ROSTER RECEIVED] Alliance ID: {aid} -> {len(captured_rosters[aid])} members", flush=True)
        elif kind == 'query_dispatched':
            print(f"[DISPATCH] Alliance ID: {p.get('aid')} (Remaining: {p.get('remaining')})", flush=True)

script.on('message', on_message)
script.load()

# Wait until all 10 captured or timeout (up to 20s)
for _ in range(40):
    if len(captured_rosters) >= len(alliances):
        break
    time.sleep(0.5)

session.detach()

print(f"\nTotal Rosters Captured: {len(captured_rosters)}/{len(alliances)}")

# If VS33 was cached or needs fallback
roster_vs33_path = os.path.join(root, "vs33_alliance_roster.json")
if 'c7d0e0f2c4bf4357b8eb2fc42a3fc221' not in captured_rosters and os.path.exists(roster_vs33_path):
    d_vs33 = json.load(open(roster_vs33_path, 'r', encoding='utf-8'))
    captured_rosters['c7d0e0f2c4bf4357b8eb2fc42a3fc221'] = d_vs33.get('members', [])
    print(f"Loaded VS33 from local cache: {len(captured_rosters['c7d0e0f2c4bf4357b8eb2fc42a3fc221'])} members")

alliance_rosters = []
for a in alliances:
    aid = a['uid']
    roster = captured_rosters.get(aid, [])
    roster.sort(key=lambda x: x.get('power', 0), reverse=True)
    alliance_rosters.append({
        'rank': a.get('rank'),
        'abbr': a.get('abbr'),
        'name': a.get('alliancename'),
        'leader': a.get('leader'),
        'total_fightpower': a.get('fightpower'),
        'allianceId': aid,
        'member_count': len(roster),
        'members': roster
    })
    print(f"  #{a.get('rank')} [{a.get('abbr')}] {a.get('alliancename')}: {len(roster)} members")

_tmp_rosters_path = f"{output_rosters_path}.{os.getpid()}.tmp"
with open(_tmp_rosters_path, 'w', encoding='utf-8') as f:
    json.dump(alliance_rosters, f, indent=2, ensure_ascii=False)
os.replace(_tmp_rosters_path, output_rosters_path)

print(f"\nSaved all rosters to: {output_rosters_path}")
