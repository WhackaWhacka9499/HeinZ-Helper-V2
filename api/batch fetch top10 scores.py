import frida
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

root = r"data/cache"
top10_rosters_path = os.path.join(root, "top10_alliance_rosters.json")
signals_log_path = os.path.join(root, "observed_signals.jsonl")
output_top10_json = os.path.join(root, "top10_alliances_migration_scores.json")

alliances = json.load(open(top10_rosters_path, 'r', encoding='utf-8'))

all_members = []
for a in alliances:
    abbr = a['abbr']
    a_name = a['name']
    for m in a['members']:
        m['alliance_tag'] = abbr
        m['alliance_name'] = a_name
        all_members.append(m)

total_members_count = len(all_members)
print(f"Total members across Top 10 Alliances: {total_members_count}")

# Check already captured in signals log
already_captured = {}
if os.path.exists(signals_log_path):
    with open(signals_log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                d = json.loads(line)
                pld = d.get('payload', {})
                uid = str(pld.get('uid'))
                if uid and uid != 'None' and 'migratePower' in pld:
                    already_captured[uid] = pld
            except:
                pass

print(f"Already captured from prior runs / cache: {len(already_captured)} profiles.")
uids_to_query = []
seen = set()
for m in all_members:
    uid = str(m['uid'])
    if uid not in already_captured and uid not in seen:
        seen.add(uid)
        uids_to_query.append(uid)

print(f"Remaining unique UIDs to query: {len(uids_to_query)}")

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
const QUERY_INTERVAL_MS = 280; // 280ms interval on main thread
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
                        send({{
                            kind: 'inbound_packet',
                            command: cmd,
                            timestamp: new Date().toISOString(),
                            payload: payload
                        }});
                    }}
                }}
            }}

            const now = Date.now();
            if (queue.length > 0 && (now - lastQueryTime) >= QUERY_INTERVAL_MS) {{
                const targetUid = queue.shift();
                lastQueryTime = now;
                
                const luaCode = 'return DataCenter.PlayerInfoDataManager:GetPlayerInfoFromServer(\"' + targetUid + '\")';
                const codePtr = allocStr(luaCode);
                if (loadstring(L, codePtr) === 0) {{
                    pcall(L, 0, 0, 0);
                    if (queue.length % 25 === 0 || queue.length === 0) {{
                        send({{kind: 'progress', remaining: queue.length}});
                    }}
                }}
            }}
            
            if (queue.length === 0 && (now - lastQueryTime) > 4000 && !drainedSent) {{
                drainedSent = true;
                send({{kind: 'queue_drained'}});
            }}
        }} catch (e) {{
            send({{kind: 'error', error: String(e)}});
        }} finally {{
            settop(L, saved);
            busy = false;
        }}
    }}
}});

send({{kind: 'attached', pid: Process.id, queue_size: queue.length}});
"""

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

def main():
    session = frida.attach('Survival.exe')
    print("Attached to Survival.exe. Starting batch ingestion...")
    script = session.create_script(js_code)
    
    captured_results = dict(already_captured)
    drained = False
    start_time = time.time()

    def on_message(message, data):
        nonlocal drained
        if message['type'] == 'send':
            p = message['payload']
            kind = p.get('kind')
            if kind == 'attached':
                print(f"[ATTACHED] Queue runner active. Queries to process: {p.get('queue_size')}", flush=True)
            elif kind == 'progress':
                rem = p.get('remaining')
                done_count = len(uids_to_query) - rem
                elapsed = time.time() - start_time
                print(f"[DISPATCH PROGRESS] Dispatched {done_count}/{len(uids_to_query)} queries ({rem} remaining) | Captured total: {len(captured_results)}/{total_members_count} | {elapsed:.0f}s", flush=True)
            elif kind == 'inbound_packet':
                pld = p.get('payload', {})
                uid = str(pld.get('uid'))
                if uid and uid != 'None':
                    captured_results[uid] = pld
                    with open(signals_log_path, 'a', encoding='utf-8') as sf:
                        sf.write(json.dumps(p, ensure_ascii=False) + '\n')
            elif kind == 'queue_drained':
                print("[ALL QUERIES COMPLETED AND DRAINED]", flush=True)
                drained = True
            elif kind == 'error':
                print(f"[SCRIPT ERROR] {p.get('error')}", flush=True)
        elif message['type'] == 'error':
            print(f"[FRIDA ERROR] {message.get('description')}", flush=True)

    script.on('message', on_message)
    script.load()

    max_timeout = time.time() + 350
    last_status_report = time.time()
    while not drained and len(captured_results) < total_members_count and time.time() < max_timeout:
        time.sleep(1)
        if time.time() - last_status_report > 15:
            last_status_report = time.time()
            print(f"[STATUS HEARTBEAT] Total profiles captured so far: {len(captured_results)}/{total_members_count}", flush=True)

    time.sleep(3)
    session.detach()
    print(f"\nFinal tally: {len(captured_results)}/{total_members_count} total profiles captured.")

    # Reconstruct Alliances with updated scores
    final_alliances_data = []
    for a in alliances:
        tag = a['abbr']
        full_name = a['name']
        members_data = []
        for m in a['members']:
            uid = str(m['uid'])
            pld = captured_results.get(uid, {})
            mp = pld.get('migratePower', 0)
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
        
        # Calculate summary statistics for alliance
        total_alliance_passes = sum(m['passes_required'] for m in members_data)
        tier_counts = {}
        for m in members_data:
            t = m['tier']
            tier_counts[t] = tier_counts.get(t, 0) + 1
            
        final_alliances_data.append({
            'rank': a['rank'],
            'abbr': tag,
            'name': full_name,
            'leader': a['leader'],
            'total_fightpower': a['total_fightpower'],
            'allianceId': a['allianceId'],
            'member_count': len(members_data),
            'total_passes_required': total_alliance_passes,
            'tier_distribution': tier_counts,
            'members': members_data
        })

    _tmp_top10_json = f"{output_top10_json}.{os.getpid()}.tmp"
    with open(_tmp_top10_json, 'w', encoding='utf-8') as f:
        json.dump({
            'state': 694,
            'retrieved_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'alliances_count': len(final_alliances_data),
            'alliances': final_alliances_data
        }, f, indent=2, ensure_ascii=False)
    os.replace(_tmp_top10_json, output_top10_json)

    print(f"\nSaved consolidated data to {output_top10_json}")

if __name__ == '__main__':
    main()
