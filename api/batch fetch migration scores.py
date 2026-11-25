import frida
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"data/cache")
roster_json_path = root / "vs33_alliance_roster.json"
signals_log_path = root / "observed_signals.jsonl"
master_csv_path = root / "vs33_alliance_migration_scores.csv"
master_json_path = root / "vs33_alliance_migration_scores.json"

with open(roster_json_path, 'r', encoding='utf-8') as f:
    roster_data = json.load(f)

members = roster_data.get('members', [])
print(f"Loaded {len(members)} alliance members from roster baseline.")

# We want to retrieve scores for all members
js_code = """
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {scheduling: 'exclusive'});
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
function allocStr(s) {
    if (!stringCache.has(s)) stringCache.set(s, Memory.allocUtf8String(s));
    return stringCache.get(s);
}

function field(L, index, key) {
    push(L, allocStr(key));
    return raw(L, index);
}

function getString(L, index, maxLen = 256) {
    if (typ(L, index) !== 4) return null;
    const p = str(L, index, length);
    const sz = Number(length.readU64());
    if (sz === 0) return '';
    if (sz > maxLen) return null;
    return p.readUtf8String(sz);
}

function getNumber(L, index) {
    return typ(L, index) === 3 ? num(L, index, ptr(0)) : null;
}

function dumpLuaTable(L, index, depth = 0, maxDepth = 2) {
    if (depth > maxDepth) return '<truncated>';
    const saved = top(L);
    const obj = {};
    nil(L);
    let count = 0;
    while (next(L, index) && count++ < 80) {
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
    }
    settop(L, saved);
    return obj;
}

let handler = null;
let currentL = null;

// Interceptor on lua_pcallk to capture inbound packets and capture active lua_State
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        const L = args[0];
        currentL = L;
        const nargs = args[1].toInt32();
        if (nargs !== 2) return;
        
        const saved = top(L);
        try {
            if (!check(L, 24)) return;
            if (handler === null) {
                if (rawi(L, registry, 2) === 5) {
                    const g = top(L);
                    if (field(L, g, 'GameMain') === 5 && field(L, top(L), 'Protocal') === 6) {
                        handler = ptrfn(L, -1).toString();
                    }
                    settop(L, g);
                }
            }
            if (ptrfn(L, saved - nargs).toString() !== handler) return;
            
            const cmd = getString(L, saved - 1, 80);
            if (!cmd) return;
            
            if (cmd === 'get.new.user.info' || cmd === 'migrate.user.info') {
                const payload = dumpLuaTable(L, saved, 0, 2);
                send({
                    kind: 'inbound_packet',
                    command: cmd,
                    timestamp: new Date().toISOString(),
                    payload: payload
                });
            }
        } catch (e) {
            send({kind: 'error', error: String(e)});
        } finally {
            settop(L, saved);
        }
    }
});

rpc.exports = {
    queryUser(uid) {
        if (!currentL) return {status: 'no_state'};
        const L = currentL;
        const saved = top(L);
        try {
            const luaCode = 'return DataCenter.PlayerInfoDataManager:GetPlayerInfoFromServer(\"' + uid + '\")';
            const codePtr = Memory.allocUtf8String(luaCode);
            const errLoad = loadstring(L, codePtr);
            if (errLoad === 0) {
                const errCall = pcall(L, 0, 0, 0);
                if (errCall === 0) {
                    return {status: 'ok'};
                } else {
                    const p = str(L, -1, length);
                    return {status: 'call_error', err: p.readUtf8String()};
                }
            } else {
                const p = str(L, -1, length);
                return {status: 'load_error', err: p.readUtf8String()};
            }
        } catch (e) {
            return {status: 'exception', err: String(e)};
        } finally {
            settop(L, saved);
        }
    }
};

send({kind: 'ready'});
"""

session = frida.attach('Survival.exe')
script = session.create_script(js_code)

captured_results = {}

def get_tier_and_passes(migrate_power):
    if migrate_power is None or migrate_power == 0:
        return ("Unknown", 0)
    if migrate_power <= 20000000:
        return ("Regular (Che1)", 10)
    elif migrate_power <= 40000000:
        return ("Intermediate (Che2)", 15)
    elif migrate_power <= 10000000:
        return ("Advanced (Che3)", 20)
    else:
        return ("Elite (Che4)", 50)

def on_message(message, data):
    if message['type'] == 'send':
        p = message['payload']
        kind = p.get('kind')
        if kind == 'inbound_packet':
            cmd = p.get('command')
            pld = p.get('payload', {})
            uid = str(pld.get('uid'))
            if uid and uid != 'None':
                captured_results[uid] = pld
                mp = pld.get('migratePower')
                tier, passes = get_tier_and_passes(mp)
                name = pld.get('name')
                print(f"[{len(captured_results)}/96 CAPTURED] UID: {uid} | {name:<16} | Migration Score: {mp:,} -> {tier} ({passes} Passes)", flush=True)
                with open(signals_log_path, 'a', encoding='utf-8') as sf:
                    sf.write(json.dumps(p, ensure_ascii=False) + '\n')

script.on('message', on_message)
script.load()

# Wait for script ready
time.sleep(0.5)

print("\nStarting automated sequential retrieval for VS33 members...")
start_time = time.time()

for idx, m in enumerate(members):
    uid = str(m['uid'])
    name = m.get('name', 'Unknown')
    
    # If already captured, skip
    if uid in captured_results:
        continue
    
    # Send RPC query
    try:
        res = script.exports_sync.query_user(uid)
        if res.get('status') != 'ok':
            # Retry once after brief pause
            time.sleep(0.15)
            res = script.exports_sync.query_user(uid)
    except Exception as e:
        print(f"RPC query error for {name} ({uid}): {e}")
    
    # Polite pacing delay (320ms between queries)
    time.sleep(0.32)

# Wait an additional 3 seconds for trailing responses
print("\nWaiting for all network packets to settle...")
time.sleep(3)

session.detach()
elapsed = time.time() - start_time
print(f"\nCompleted query sequence in {elapsed:.1f}s. Total profiles captured: {len(captured_results)}/{len(members)}")

# Combine with roster baseline
master_records = []
for m in members:
    uid = str(m['uid'])
    pld = captured_results.get(uid, {})
    
    mp = pld.get('migratePower', 0)
    tier, passes = get_tier_and_passes(mp)
    
    rec = {
        'rank': m.get('rank'),
        'uid': uid,
        'name': pld.get('name') or m.get('name'),
        'mainBuildingLevel': pld.get('mainBuildingLevel') or m.get('mainCityLv'),
        'authoritative_migrate_power': mp,
        'tier': tier,
        'passes_required': passes,
        'total_power': pld.get('power') or m.get('power'),
        'player_max_power': pld.get('playerMaxPower') or 0,
        'building_power': pld.get('buildingPower') or 0,
        'science_power': pld.get('sciencePower') or 0,
        'hero_power': pld.get('heroPower') or 0,
        'tank_power': pld.get('tankPower') or 0,
        'army_power': pld.get('armyPower') or 0,
        'status': 'VERIFIED_IN_GAME' if mp > 0 else 'PENDING'
    }
    master_records.append(rec)

# Sort by authoritative_migrate_power descending (then total power)
master_records.sort(key=lambda x: (x['authoritative_migrate_power'], x['total_power']), reverse=True)

# Save Master JSON atomically
_tmp_master_json = f"{master_json_path}.{os.getpid()}.tmp"
with open(_tmp_master_json, 'w', encoding='utf-8') as f:
    json.dump({
        'alliance': '[VS33] VEIL OF SHADOWS',
        'state': 694,
        'retrieved_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'total_members': len(master_records),
        'verified_count': sum(1 for r in master_records if r['status'] == 'VERIFIED_IN_GAME'),
        'records': master_records
    }, f, indent=2, ensure_ascii=False)
os.replace(_tmp_master_json, master_json_path)

# Save Master CSV
import csv
with open(master_csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Rank', 'Alliance Rank', 'HQ Level', 'Player Name', 'Player UID',
        'Official Migration Score', 'Migration Tier', 'Passes Required',
        'Total Power', 'Max Historical Power',
        'Structure Power', 'Tech Power', 'Hero Power', 'Vehicle Power', 'Troop Power',
        'Data Status'
    ])
    for idx, r in enumerate(master_records, start=1):
        writer.writerow([
            idx,
            f"R{r['rank']}",
            r['mainBuildingLevel'],
            r['name'],
            f"'{r['uid']}",
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
            r['status']
        ])

print(f"Master files saved:\n  JSON: {master_json_path}\n  CSV:  {master_csv_path}")
