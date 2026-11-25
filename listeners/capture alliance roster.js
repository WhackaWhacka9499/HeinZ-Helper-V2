const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args, { scheduling: 'exclusive' });
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const check = nf('lua_checkstack', 'int', ['pointer', 'int']);
const rawi = nf('lua_rawgeti', 'int', ['pointer', 'int', 'int64']);
const raw = nf('lua_rawget', 'int', ['pointer', 'int']);
const next = nf('lua_next', 'int', ['pointer', 'int']);
const pushnil = nf('lua_pushnil', 'void', ['pointer']);
const pushstring = nf('lua_pushstring', 'pointer', ['pointer', 'pointer']);
const typ = nf('lua_type', 'int', ['pointer', 'int']);
const num = nf('lua_tonumberx', 'double', ['pointer', 'int', 'pointer']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const tobool = nf('lua_toboolean', 'int', ['pointer', 'int']);
const length = Memory.alloc(8);
const registry = nf('xlua_get_registry_index', 'int', [])();

const fieldStrings = {};
function getFieldString(name) {
  if (!fieldStrings[name]) {
    fieldStrings[name] = Memory.allocUtf8String(name);
  }
  return fieldStrings[name];
}

function field(L, index, key) {
  pushstring(L, getFieldString(key));
  return raw(L, index);
}

function readNumber(L, index) {
  return typ(L, index) === 3 ? num(L, index, ptr(0)) : null;
}

function readString(L, index) {
  if (typ(L, index) !== 4) return null;
  const p = str(L, index, length);
  const size = Number(length.readU64());
  if (size === 0) return '';
  return p.readUtf8String(size);
}

function readBoolean(L, index) {
  const t = typ(L, index);
  if (t === 1) return tobool(L, index) !== 0;
  return null;
}

let sampled = false;
let busy = false;

Interceptor.attach(mod.getExportByName('lua_pcallk'), {
  onEnter(args) {
    this.L = args[0];
  },
  onLeave(ret) {
    if (sampled || busy || ret.toInt32() !== 0) return;
    busy = true;
    const L = this.L;
    const saved = top(L);

    try {
      if (!check(L, 64)) return;

      if (rawi(L, registry, 2) !== 5) return;
      const globals = top(L);

      if (field(L, globals, 'DataCenter') !== 5) {
        settop(L, saved);
        return;
      }
      const dataCenter = top(L);

      // 1. Alliance Base Data
      const allianceInfo = {};
      if (field(L, dataCenter, 'AllianceBaseDataManager') === 5) {
        const abdm = top(L);
        if (field(L, abdm, 'allianceBaseData') === 5) {
          const abd = top(L);
          for (const k of ['name', 'abbr', 'uid', 'rank', 'leaderUid', 'leaderName', 'serverId', 'memberCount', 'power']) {
            field(L, abd, k);
            const val = typ(L, -1) === 4 ? readString(L, -1) : readNumber(L, -1);
            if (val !== null) allianceInfo[k] = val;
            settop(L, abd);
          }
        }
        settop(L, abdm);
      }
      settop(L, dataCenter);

      // 2. Alliance Members
      const members = [];
      if (field(L, dataCenter, 'AllianceMemberDataManager') === 5) {
        const amdm = top(L);
        if (field(L, amdm, 'allianceMembers') === 5) {
          const membersTable = top(L);
          const memberKeys = ['uid', 'name', 'rank', 'power', 'arenaPower', 'mainCityLv', 'online', 'offLineTime', 'armyKill', 'joinTime', 'curServerId', 'migratePower'];

          pushnil(L);
          while (next(L, membersTable) !== 0) {
            const memberObj = top(L);
            if (typ(L, memberObj) === 5) {
              const m = {};
              for (const k of memberKeys) {
                field(L, memberObj, k);
                const t = typ(L, -1);
                if (t === 4) m[k] = readString(L, -1);
                else if (t === 3) m[k] = readNumber(L, -1);
                else if (t === 1) m[k] = readBoolean(L, -1);
                settop(L, memberObj);
              }
              members.push(m);
            }
            // Pop value, leave key
            settop(L, memberObj - 1);
          }
        }
        settop(L, amdm);
      }

      if (members.length > 0) {
        sampled = true;
        send({
          kind: 'alliance_roster',
          at: new Date().toISOString(),
          alliance: allianceInfo,
          count: members.length,
          members: members
        });
      }
    } catch (e) {
      send({ kind: 'error', error: String(e) });
    } finally {
      settop(L, saved);
      busy = false;
    }
  }
});

send({ kind: 'ready', mode: 'read-only alliance roster' });
