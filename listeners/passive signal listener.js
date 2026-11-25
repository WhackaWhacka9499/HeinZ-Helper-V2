// Passive Listener for Last Z Migration & Profile Signals
// Attaches to GameMain.Protocal via lua_pcallk in xlua.dll
// Zero game memory modification, zero packet injection, 100% borderless passive recording.

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
let verified = false;

Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        const L = args[0];
        const nargs = args[1].toInt32();
        if (nargs !== 2) return; // GameMain.Protocal(command, payload) has 2 arguments
        
        const saved = top(L);
        try {
            if (!check(L, 24)) return;
            
            // Resolve handler on first run
            if (handler === null) {
                if (rawi(L, registry, 2) === 5) {
                    const g = top(L);
                    if (field(L, g, 'GameMain') === 5 && field(L, top(L), 'Protocal') === 6) {
                        handler = ptrfn(L, -1).toString();
                    }
                    settop(L, g);
                }
            }
            
            // Verify function pointer matches GameMain.Protocal
            const fnPtr = ptrfn(L, saved - nargs).toString();
            if (fnPtr !== handler) return;
            
            const cmd = getString(L, saved - 1, 80);
            if (!cmd) return;
            
            // Filter for commands of interest
            const isMigrate = cmd.startsWith('migrate.') || cmd.startsWith('get.migrate.') || cmd.startsWith('push.migrate.');
            const isUser = (cmd === 'get.new.user.info' || cmd === 'get.user.info' || cmd === 'al.member.info');
            
            if (isMigrate || isUser) {
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

send({kind: 'attached', pid: Process.id, status: 'listening'});
