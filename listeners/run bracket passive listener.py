import frida
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(__file__).resolve().parent
output_jsonl = root / "bracket signals.jsonl"
bracket_dir = root / "bracket data"
bracket_dir.mkdir(parents=True, exist_ok=True)

js_listener = """
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, {scheduling: 'exclusive'});
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const check = nf('lua_checkstack', 'int', ['pointer', 'int']);
const rawi = nf('lua_rawgeti', 'int', ['pointer', 'int', 'int64']);
const raw = nf('lua_rawget', 'int', ['pointer', 'int']);
const next = nf('lua_next', 'int', ['pointer', 'int']);
const nil = nf('lua_pushnil', 'void', ['pointer']);
const push = nf('lua_pushstring', 'pointer', ['pointer', 'pointer']);
const typ = nf('lua_type', 'int', ['pointer', 'int']);
const num = nf('lua_tonumberx', 'double', ['pointer', 'int', 'pointer']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const ptrfn = nf('lua_topointer', 'pointer', ['pointer', 'int']);
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

function dumpLuaTable(L, index, depth = 0, maxDepth = 3) {
    if (depth > maxDepth) return '<truncated>';
    const saved = top(L);
    const obj = {};
    nil(L);
    let count = 0;
    while (next(L, index) && count++ < 150) {
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

Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        const L = args[0];
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
            
            // Filter: Any alliance, rank, user, migration, or state info
            const match = (
                cmd === 'alliance.rank' ||
                cmd === 'al.rank' ||
                cmd === 'get.al.info' ||
                cmd === 'get.new.user.info' ||
                cmd === 'get.user.info' ||
                cmd === 'get.user.info.multi' ||
                cmd === 'al.member.info' ||
                cmd.startsWith('migrate.') ||
                cmd.startsWith('get.migrate.') ||
                cmd === 'get.server.info' ||
                cmd === 'server.trends.info'
            );
            
            if (match) {
                const payload = dumpLuaTable(L, saved, 0, 3);
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

send({kind: 'attached', pid: Process.id, status: 'listening'});
"""

print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting passive listener to Survival.exe...")
session = frida.attach('Survival.exe')

script = session.create_script(js_listener)

total_captured = 0

def on_message(message, data):
    global total_captured
    if message['type'] == 'send':
        payload = message['payload']
        kind = payload.get('kind')
        
        if kind == 'attached':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] *** LISTENER ACTIVE & MONITORING GAME ***")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for state visits, rankings, and profile clicks...")
            sys.stdout.flush()
            return
            
        if kind == 'inbound_packet':
            cmd = payload.get('command')
            data_body = payload.get('payload', {})
            total_captured += 1
            
            # Format high-level status line
            summary = ""
            if cmd == 'alliance.rank':
                ranking = data_body.get('allianceRanking') or data_body.get('list') or data_body.get('ranks') or {}
                count = len(ranking) if isinstance(ranking, (list, dict)) else 0
                # Try to determine server ID from ranking entries
                server_id = 'Unknown'
                if isinstance(ranking, dict) and ranking:
                    first_al = list(ranking.values())[0]
                    if isinstance(first_al, dict):
                        server_id = first_al.get('serverId') or first_al.get('server') or 'Unknown'
                summary = f"State: {server_id} | Total Ranked Alliances: {count}"
            elif cmd == 'al.rank':
                members = data_body.get('list') or data_body.get('ranks') or data_body.get('members') or {}
                count = len(members) if isinstance(members, (list, dict)) else 0
                al_id = data_body.get('allianceId', '')
                server_id = 'Unknown'
                if isinstance(members, dict) and members:
                    first_m = list(members.values())[0]
                    if isinstance(first_m, dict):
                        server_id = first_m.get('serverId') or first_m.get('curServerId') or 'Unknown'
                summary = f"Alliance ID: {al_id[:8]}... (State {server_id}) | Members: {count}"
            elif cmd in ('get.new.user.info', 'get.user.info'):
                name = data_body.get('name', 'Unknown')
                uid = data_body.get('uid', '')
                server = data_body.get('serverId', '')
                mp = data_body.get('migratePower')
                pwr = data_body.get('power', 0)
                mp_str = f"{int(mp):,}" if mp else "N/A"
                summary = f"Player: {name} (State {server}, UID {uid}) | Power: {int(pwr):,} | Migration: {mp_str}"
            elif cmd == 'get.user.info.multi':
                uids = data_body.get('uids') or {}
                count = len(uids) if isinstance(uids, (list, dict)) else 0
                summary = f"Batch Player Profiles Received: {count} players with Migration Scores"

            print(f"[{datetime.now().strftime('%H:%M:%S')}] [CAPTURED #{total_captured}] {cmd} -> {summary}")
            sys.stdout.flush()

            # Append to persistent JSONL
            with open(output_jsonl, 'a', encoding='utf-8') as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    elif message['type'] == 'error':
        print(f"[Error] {message.get('description')}")
        sys.stdout.flush()

script.on('message', on_message)
script.load()

# Keep running indefinitely
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDetaching listener cleanly...")
    session.detach()
