"""Standalone Mine Melee Refresh & Resource Gathering pipeline for Last Z bot engine.

Implements a defensive 3-stage Lua + Python pipeline:
- Stage 3A: Inspect Active Marches (WorldMyMarchDataManager / WorldMarchDataManager)
            & Formations (ArmyFormationDataManager) & Alliance Mine status.
- Stage 3B: Detect Melee Refresh & Depletion Conditions (remaining gather time below
            refresh_threshold_sec, expired/depleted/stuck tiles, or idle formations ready).
- Stage 3C: Staged Recall -> Restock -> Re-dispatch (safe recall in live mode or
            would_recall in dry_run; deploy free formations above reserve to active
            Alliance Mine or best territory resource node).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import threading
import time
import weakref
from pathlib import Path
from typing import Any

try:
    import psutil
except Exception:
    psutil = None  # type: ignore[assignment]

TOOLS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TOOLS_DIR.parent
_MODULE_LOAD_LOCK = threading.Lock()
_CD_SINGLETON_NAME = "heinz_client_discovery_singleton"
_BA_SINGLETON_NAME = "heinz_bot_actions_singleton"

LUA_JSON_HELPER = r"""
local function _esc(s)
  return '"' .. tostring(s):gsub('[%z\1-\31\\"\127]', function(c)
    return string.format('\\u%04x', c:byte())
  end) .. '"'
end
local _rjson = package and package.loaded and package.loaded.rapidjson
local _rjsonEmptyMode = 0
local _rjsonArrFn = nil
local _rjsonArrMt = { __jsontype = 'array' }
local _rjsonEmptyObjMode = 0
local _rjsonObjFn = nil
local _rjsonObjMt = { __jsontype = 'object' }
local _RJSON_ABORT = {}
if _rjson and type(_rjson.encode) == 'function' then
  local okP, resP = pcall(_rjson.encode, {})
  if okP and resP == '[]' then
    _rjsonEmptyMode = 1
  else
    if type(_rjson.array) == 'function' then
      local okA, arrVal = pcall(_rjson.array)
      if okA and arrVal ~= nil then
        local okAE, resAE = pcall(_rjson.encode, arrVal)
        if okAE and resAE == '[]' then
          _rjsonEmptyMode = 2
          _rjsonArrFn = _rjson.array
        end
      end
      if _rjsonEmptyMode == 0 then
        local okA2, arrVal2 = pcall(_rjson.array, {})
        if okA2 and arrVal2 ~= nil then
          local okAE2, resAE2 = pcall(_rjson.encode, arrVal2)
          if okAE2 and resAE2 == '[]' then
            _rjsonEmptyMode = 2
            _rjsonArrFn = function() return _rjson.array({}) end
          end
        end
      end
    end
    if _rjsonEmptyMode == 0 then
      local okM, resM = pcall(_rjson.encode, setmetatable({}, _rjsonArrMt))
      if okM and resM == '[]' then
        _rjsonEmptyMode = 3
      end
    end
  end
  if okP and resP == '{}' then
    _rjsonEmptyObjMode = 1
  else
    if type(_rjson.object) == 'function' then
      local okO, objVal = pcall(_rjson.object)
      if okO and objVal ~= nil then
        local okOE, resOE = pcall(_rjson.encode, objVal)
        if okOE and resOE == '{}' then
          _rjsonEmptyObjMode = 2
          _rjsonObjFn = _rjson.object
        end
      end
      if _rjsonEmptyObjMode == 0 then
        local okO2, objVal2 = pcall(_rjson.object, {})
        if okO2 and objVal2 ~= nil then
          local okOE2, resOE2 = pcall(_rjson.encode, objVal2)
          if okOE2 and resOE2 == '{}' then
            _rjsonEmptyObjMode = 2
            _rjsonObjFn = function() return _rjson.object({}) end
          end
        end
      end
    end
    if _rjsonEmptyObjMode == 0 then
      local okOM, resOM = pcall(_rjson.encode, setmetatable({}, _rjsonObjMt))
      if okOM and resOM == '{}' then
        _rjsonEmptyObjMode = 3
      end
    end
  end
end
local function _jdict(t)
  t = type(t) == 'table' and t or {}
  if getmetatable(t) == nil then
    setmetatable(t, _rjsonObjMt)
  end
  return t
end
local function _jarr(t)
  t = type(t) == 'table' and t or {}
  if getmetatable(t) == nil then
    setmetatable(t, _rjsonArrMt)
  end
  return t
end
local function _safe_tostring(v)
  local ok, s = pcall(tostring, v)
  if ok then return s end
  return '<' .. type(v) .. '>'
end
local function _collect_pairs(v)
  local ks, vs, n = {}, {}, 0
  for k, val in pairs(v) do
    n = n + 1
    ks[n] = k
    vs[n] = val
  end
  return ks, vs, n
end
local function _sanitize_json(v, d)
  d = d or 0
  local t = type(v)
  if t == 'nil' or t == 'boolean' or t == 'string' then
    return v
  elseif t == 'number' then
    if v ~= v or v == math.huge or v == -math.huge then return nil end
    return v
  elseif t == 'table' then
    if d > 6 then return '<depth>' end
    local mt = getmetatable(v)
    local jt = (type(mt) == 'table' and mt.__jsontype) or nil
    local isArr, maxI, cnt = (jt ~= 'object'), 0, 0
    for k, _ in pairs(v) do
      cnt = cnt + 1
      if isArr then
        if type(k) ~= 'number' or k < 1 or math.floor(k) ~= k then
          isArr = false
        elseif k > maxI then
          maxI = k
        end
      end
    end
    if cnt == 0 then
      if jt == 'object' then
        if _rjsonEmptyObjMode == 1 then return {} end
        if _rjsonEmptyObjMode == 2 then return _rjsonObjFn() end
        if _rjsonEmptyObjMode == 3 then return setmetatable({}, _rjsonObjMt) end
        return _RJSON_ABORT
      end
      if _rjsonEmptyMode == 1 then return {} end
      if _rjsonEmptyMode == 2 then return _rjsonArrFn() end
      if _rjsonEmptyMode == 3 then return setmetatable({}, _rjsonArrMt) end
      return _RJSON_ABORT
    end
    local outTbl = {}
    if isArr and maxI == cnt then
      for i = 1, cnt do
        local sv = _sanitize_json(v[i], d + 1)
        if sv == _RJSON_ABORT then return _RJSON_ABORT end
        if sv == nil then
          if _rjson and _rjson.null ~= nil then
            outTbl[i] = _rjson.null
          else
            return _RJSON_ABORT
          end
        else
          outTbl[i] = sv
        end
      end
    else
      for k, val in pairs(v) do
        local sv = _sanitize_json(val, d + 1)
        if sv == _RJSON_ABORT then return _RJSON_ABORT end
        if sv ~= nil then
          outTbl[_safe_tostring(k)] = sv
        end
      end
      if next(outTbl) == nil then
        if _rjsonEmptyObjMode == 1 then return {} end
        if _rjsonEmptyObjMode == 2 then return _rjsonObjFn() end
        if _rjsonEmptyObjMode == 3 then return setmetatable({}, _rjsonObjMt) end
        return _RJSON_ABORT
      end
    end
    return outTbl
  end
  return _safe_tostring(v)
end
local function _enc_lua(v, d)
  d = d or 0
  local t = type(v)
  if t == 'nil' then
    return 'null'
  elseif t == 'boolean' then
    return tostring(v)
  elseif t == 'number' then
    if v ~= v or v == math.huge or v == -math.huge then return 'null' end
    return tostring(v)
  elseif t == 'string' then
    return _esc(v)
  elseif t == 'table' then
    if d > 6 then return '"<depth>"' end
    local mt = getmetatable(v)
    local jt = (type(mt) == 'table' and mt.__jsontype) or nil
    if mt ~= nil and jt ~= 'object' and jt ~= 'array' then
      local okC, ks, vs, n = pcall(_collect_pairs, v)
      if not okC then return '{}' end
      local isArr, maxI = true, 0
      for i = 1, n do
        local k = ks[i]
        if type(k) ~= 'number' or k < 1 or math.floor(k) ~= k then
          isArr = false
          break
        end
        if k > maxI then maxI = k end
      end
      local p = {}
      if isArr and maxI == n then
        for i = 1, n do p[i] = _enc_lua(vs[i], d + 1) end
        return '[' .. table.concat(p, ',') .. ']'
      else
        for i = 1, n do
          p[i] = _esc(_safe_tostring(ks[i])) .. ':' .. _enc_lua(vs[i], d + 1)
        end
        return '{' .. table.concat(p, ',') .. '}'
      end
    end
    local isArr, maxI, cnt = (jt ~= 'object'), 0, 0
    for k, _ in pairs(v) do
      cnt = cnt + 1
      if isArr then
        if type(k) ~= 'number' or k < 1 or math.floor(k) ~= k then
          isArr = false
        elseif k > maxI then
          maxI = k
        end
      end
    end
    if cnt == 0 and jt == 'object' then
      return '{}'
    end
    local p = {}
    if isArr and maxI == cnt then
      for i = 1, cnt do p[i] = _enc_lua(v[i], d + 1) end
      return '[' .. table.concat(p, ',') .. ']'
    else
      for k, val in pairs(v) do
        table.insert(p, _esc(k) .. ':' .. _enc_lua(val, d + 1))
      end
      return '{' .. table.concat(p, ',') .. '}'
    end
  end
  return _esc(_safe_tostring(v))
end
local function _enc(v, d)
  d = d or 0
  if d == 0 and type(v) == 'table' and _rjson and type(_rjson.encode) == 'function' and next(v) ~= nil then
    local okS, clean = pcall(_sanitize_json, v, 0)
    if okS and clean ~= _RJSON_ABORT then
      local okRj, encoded = pcall(_rjson.encode, clean)
      if okRj and type(encoded) == 'string' then
        return encoded
      end
    end
  end
  return _enc_lua(v, d)
end
"""

LUA_MINE_MELEE_HELPERS = LUA_JSON_HELPER + r"""
local function _safe_call(fn, default)
  local ok, res = pcall(fn)
  if ok and res ~= nil then return res end
  return default
end

local function _first_pos(a, b, c, d, ...)
  local n = tonumber(a); if n and n > 0 then return n end
  n = tonumber(b); if n and n > 0 then return n end
  n = tonumber(c); if n and n > 0 then return n end
  n = tonumber(d); if n and n > 0 then return n end
  local extra = select('#', ...)
  for i = 1, extra do
    n = tonumber(select(i, ...))
    if n and n > 0 then return n end
  end
  return 0
end

local function _raw_prop(o, k)
  return o[k]
end

local function _read_pos_prop(obj, isTbl, k)
  if k == nil then return 0 end
  local ok, val
  if isTbl then
    val = obj[k]
    ok = true
  else
    ok, val = pcall(_raw_prop, obj, k)
  end
  if ok and val ~= nil then
    local n = tonumber(val)
    if n and n > 0 then return n end
  end
  return 0
end

local function _first_pos_prop(obj, a, b, c, d, e, f, ...)
  if not obj then return 0 end
  local isTbl = (type(obj) == 'table' and getmetatable(obj) == nil)
  local v
  if a ~= nil then v = _read_pos_prop(obj, isTbl, a); if v > 0 then return v end end
  if b ~= nil then v = _read_pos_prop(obj, isTbl, b); if v > 0 then return v end end
  if c ~= nil then v = _read_pos_prop(obj, isTbl, c); if v > 0 then return v end end
  if d ~= nil then v = _read_pos_prop(obj, isTbl, d); if v > 0 then return v end end
  if e ~= nil then v = _read_pos_prop(obj, isTbl, e); if v > 0 then return v end end
  if f ~= nil then v = _read_pos_prop(obj, isTbl, f); if v > 0 then return v end end
  local extra = select('#', ...)
  for i = 1, extra do
    v = _read_pos_prop(obj, isTbl, select(i, ...))
    if v > 0 then return v end
  end
  return 0
end

local function _to_xy(ptIdx)
  local n = tonumber(ptIdx) or 0
  if n <= 0 then return 0, 0 end
  if TileCoordWorld and TileCoordWorld.IndexToTilePos then
    local ok, pos = pcall(function() return TileCoordWorld.IndexToTilePos(n) end)
    if ok and type(pos) == 'table' and pos.x and pos.y then
      return tonumber(pos.x) or 0, tonumber(pos.y) or 0
    end
  end
  return (n - 1) % 1000, math.floor((n - 1) / 1000)
end

local function _dist(p1, p2)
  local x1, y1 = _to_xy(p1)
  local x2, y2 = _to_xy(p2)
  local dx, dy = x1 - x2, y1 - y2
  return math.sqrt(dx * dx + dy * dy)
end

local function _extract_collection(col)
  local items = {}
  if not col then return items end
  local found = false
  if type(col) == 'table' then
    for k, v in pairs(col) do
      if v ~= nil then
        table.insert(items, {key = k, val = v})
        found = true
      end
    end
    if found then return items end
  end
  pcall(function()
    if col.GetEnumerator then
      local iter = col:GetEnumerator()
      if iter then
        while iter:MoveNext() do
          local cur = iter.Current
          if cur ~= nil then
            local okK, k = pcall(function() return cur.Key end)
            local okV, v = pcall(function() return cur.Value end)
            if okK and okV and k ~= nil and v ~= nil then
              table.insert(items, {key = k, val = v})
              found = true
            else
              table.insert(items, {key = #items + 1, val = cur})
              found = true
            end
          end
        end
      end
    end
  end)
  if found then return items end
  pcall(function()
    local cnt = tonumber(col.Count) or 0
    if cnt > 0 then
      for i = 0, cnt - 1 do
        local okI, item = pcall(function() return col[i] end)
        if okI and item ~= nil then
          table.insert(items, {key = i + 1, val = item})
          found = true
        end
      end
    end
  end)
  return items
end

local function _get_player_snapshot()
  local p = LuaEntry and LuaEntry.Player
  local dc = DataCenter
  local afm = dc and (dc.ArmyFormationDataManager or dc.ArmyFormationManager)
  local bm = dc and dc.BuildManager
  local uid = (p and p.GetUid) and _safe_call(function() return p:GetUid() end, '') or (p and p.uid) or ''
  local name = (p and p.GetName) and _safe_call(function() return p:GetName() end, '') or (p and p.name) or ''
  local srv = (p and p.GetCurServerId) and _safe_call(function() return p:GetCurServerId() end, 0) or (p and p.serverId) or 0
  local homeSrv = (p and p.GetSelfServerId) and _safe_call(function() return p:GetSelfServerId() end, srv) or srv
  local pos = 0
  if p and p.GetMainWorldPos then pos = tonumber(_safe_call(function() return p:GetMainWorldPos() end, 0)) or 0 end
  if pos == 0 and p and p.GetPositionId then pos = tonumber(_safe_call(function() return p:GetPositionId() end, 0)) or 0 end
  if pos == 0 and bm and bm.GetFunbuildByItemID then
    local mb = _safe_call(function()
      return bm:GetFunbuildByItemID(BuildingTypes and BuildingTypes.FUN_BUILD_MAIN or 400000)
    end, nil)
    if mb and mb.pointId then pos = tonumber(mb.pointId) or 0 end
  end
  local freeForm = (afm and afm.GetFreeFormationCount) and tonumber(_safe_call(function() return afm:GetFreeFormationCount() end, 0)) or 0
  local unlockForm = (afm and afm.GetUnlockFormationCount) and tonumber(_safe_call(function() return afm:GetUnlockFormationCount() end, 0)) or 0
  local chatReady = (ChatInterface ~= nil)
  local inAlliance = false
  local allyUid = ''
  if p and p.IsInAlliance then
    inAlliance = _safe_call(function() return p:IsInAlliance() end, false) and true or false
  end
  if p and p.GetAllianceUid then
    allyUid = tostring(_safe_call(function() return p:GetAllianceUid() end, '') or '')
  end
  if not inAlliance and allyUid ~= '' and allyUid ~= '0' then
    inAlliance = true
  end
  local nowSec = 0
  if UITimeManager and UITimeManager.GetInstance then
    local tm = _safe_call(function() return UITimeManager:GetInstance() end, nil)
    if tm and tm.GetServerSeconds then nowSec = tonumber(_safe_call(function() return tm:GetServerSeconds() end, 0)) or 0 end
  end
  if nowSec <= 0 and TimeUtil and TimeUtil.GetServerTime then
    nowSec = tonumber(_safe_call(function() return TimeUtil.GetServerTime() end, 0)) or 0
  end
  if nowSec <= 0 then nowSec = os.time() end
  if nowSec > 1e12 then nowSec = math.floor(nowSec / 1000) end
  local inWorld = (SceneManager and SceneManager.IsInWorld) and (_safe_call(function() return SceneManager:IsInWorld() end, false) and true or false) or false
  return {
    uid = tostring(uid or ''),
    name = tostring(name or ''),
    serverId = tonumber(srv) or 0,
    homeServerId = tonumber(homeSrv) or 0,
    mainPos = tonumber(pos) or 0,
    freeFormations = freeForm,
    unlockFormations = unlockForm,
    inAlliance = inAlliance,
    allianceUid = allyUid,
    serverSec = nowSec,
    inWorld = inWorld,
    chatReady = chatReady,
  }
end

local function _get_mine_gather_res_meta(resId)
  local rid = tostring(resId or '')
  if rid == '' or rid == '0' then return nil end
  local cache = _G.__hzMineResCache
  if type(cache) ~= 'table' then
    cache = {}
    _G.__hzMineResCache = cache
  end
  local hit = cache[rid]
  if hit ~= nil then return hit end
  local lc = LocalController and LocalController.instance and LocalController.instance() or nil
  if not (lc and lc.getLine and TableName and TableName.GatherResource) then return nil end
  local row = _safe_call(function() return lc:getLine(TableName.GatherResource, rid) end, nil)
  if not (row and row.getValue) then return nil end
  local rTypeNum = tonumber(_safe_call(function() return row:getValue('resource_type') or row:getValue('type') end, -1)) or -1
  local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
  local meta = { resource_type = rTypeNum, level = lv }
  cache[rid] = meta
  return meta
end
"""

_HZ_MINE_VERSION = 1

_LUA_MINE_BOOTSTRAP = LUA_MINE_MELEE_HELPERS + f"""
_G.__hzMineVer = {_HZ_MINE_VERSION}
_G.__hzMineBridge = {{
  esc = _esc,
  jdict = _jdict,
  jarr = _jarr,
  enc = _enc,
  safe_call = _safe_call,
  first_pos = _first_pos,
  first_pos_prop = _first_pos_prop,
  to_xy = _to_xy,
  dist = _dist,
  extract_collection = _extract_collection,
  get_player_snapshot = _get_player_snapshot,
  get_mine_gather_res_meta = _get_mine_gather_res_meta,
}}
"""

_LUA_MINE_SHIM = f"""local _hzMB = _G.__hzMineBridge
if _G.__hzMineVer ~= {_HZ_MINE_VERSION} or type(_hzMB) ~= 'table' then
  return '__HZ_MINE_NEED_BOOTSTRAP__'
end
local _esc = _hzMB.esc
local _jdict = _hzMB.jdict
local _jarr = _hzMB.jarr
local _enc = _hzMB.enc
local _safe_call = _hzMB.safe_call
local _first_pos = _hzMB.first_pos
local _first_pos_prop = _hzMB.first_pos_prop
local _to_xy = _hzMB.to_xy
local _dist = _hzMB.dist
local _extract_collection = _hzMB.extract_collection
local _get_player_snapshot = _hzMB.get_player_snapshot
local _get_mine_gather_res_meta = _hzMB.get_mine_gather_res_meta
"""

_HZ_MINE_BRIDGE_LOCK = threading.RLock()
_HZ_MINE_BOOTSTRAPPED_TARGETS: dict[tuple[int, int, float], float] = {}
_HZ_MINE_FINALIZED_IDS: set[int] = set()
_MINE_PID_CTIME_CACHE: dict[int, tuple[float, float]] = {}
_MINE_PID_CTIME_TTL_S = 10.0


def _get_mine_pid_create_time(pid: int) -> float:
    try:
        pid_i = int(pid)
        if pid_i <= 0 or psutil is None:
            return 0.0
        now_m = time.monotonic()
        with _HZ_MINE_BRIDGE_LOCK:
            cached = _MINE_PID_CTIME_CACHE.get(pid_i)
            if cached is not None and (now_m - cached[1]) < _MINE_PID_CTIME_TTL_S:
                return cached[0]
        ctime = round(float(psutil.Process(pid_i).create_time()), 3)
        with _HZ_MINE_BRIDGE_LOCK:
            if len(_MINE_PID_CTIME_CACHE) >= 256:
                _MINE_PID_CTIME_CACHE.clear()
            _MINE_PID_CTIME_CACHE[pid_i] = (ctime, time.monotonic())
        return ctime
    except Exception:
        return 0.0


def _invalidate_mine_pid_ctime(pid: int) -> None:
    try:
        pid_i = int(pid)
    except Exception:
        return
    with _HZ_MINE_BRIDGE_LOCK:
        _MINE_PID_CTIME_CACHE.pop(pid_i, None)


def _mark_hz_mine_bootstrapped(cd: Any, cache_key: tuple[int, int, float]) -> None:
    cd_id = cache_key[0]
    with _HZ_MINE_BRIDGE_LOCK:
        if len(_HZ_MINE_BOOTSTRAPPED_TARGETS) >= 128:
            _HZ_MINE_BOOTSTRAPPED_TARGETS.clear()
        _HZ_MINE_BOOTSTRAPPED_TARGETS[cache_key] = time.monotonic()
        if cd_id not in _HZ_MINE_FINALIZED_IDS:
            _HZ_MINE_FINALIZED_IDS.add(cd_id)
            try:
                def _cleanup_cd(
                    _cid: int = cd_id,
                    _lock: Any = _HZ_MINE_BRIDGE_LOCK,
                    _finalized_ids: set[int] = _HZ_MINE_FINALIZED_IDS,
                    _bootstrapped: dict[tuple[int, int, float], float] = _HZ_MINE_BOOTSTRAPPED_TARGETS,
                ) -> None:
                    g = globals()
                    lock = g.get("_HZ_MINE_BRIDGE_LOCK") if isinstance(g, dict) else None
                    if lock is None:
                        lock = _lock
                    if lock is None:
                        return
                    finalized_ids = g.get("_HZ_MINE_FINALIZED_IDS") if isinstance(g, dict) else None
                    if not isinstance(finalized_ids, set):
                        finalized_ids = _finalized_ids
                    bootstrapped = g.get("_HZ_MINE_BOOTSTRAPPED_TARGETS") if isinstance(g, dict) else None
                    if not isinstance(bootstrapped, dict):
                        bootstrapped = _bootstrapped
                    try:
                        with lock:
                            if isinstance(finalized_ids, set):
                                finalized_ids.discard(_cid)
                            if isinstance(bootstrapped, dict):
                                for k in [k for k in bootstrapped if isinstance(k, tuple) and k[0] == _cid]:
                                    bootstrapped.pop(k, None)
                    except Exception:
                        pass

                fin = weakref.finalize(cd, _cleanup_cd)
                fin.atexit = False
            except TypeError:
                _HZ_MINE_FINALIZED_IDS.discard(cd_id)


def _eval_mine_lua(cd: Any, pid: int, lua_body: str, timeout: float = 10.0) -> dict[str, Any]:
    cache_key = (id(cd), int(pid), _get_mine_pid_create_time(int(pid)))
    with _HZ_MINE_BRIDGE_LOCK:
        is_bootstrapped = cache_key in _HZ_MINE_BOOTSTRAPPED_TARGETS

    if is_bootstrapped:
        lua = _LUA_MINE_SHIM + "\n" + lua_body
        ok, raw = cd.frida_eval_lua(pid, lua, timeout=timeout)
        if ok and isinstance(raw, str) and raw.strip() == "__HZ_MINE_NEED_BOOTSTRAP__":
            _invalidate_mine_pid_ctime(pid)
            with _HZ_MINE_BRIDGE_LOCK:
                _HZ_MINE_BOOTSTRAPPED_TARGETS.pop(cache_key, None)
            lua_full = _LUA_MINE_BOOTSTRAP + "\n" + lua_body
            ok, raw = cd.frida_eval_lua(pid, lua_full, timeout=timeout)
            if ok and not (isinstance(raw, str) and raw.strip() == "__HZ_MINE_NEED_BOOTSTRAP__"):
                _mark_hz_mine_bootstrapped(cd, cache_key)
    else:
        lua = _LUA_MINE_BOOTSTRAP + "\n" + lua_body
        ok, raw = cd.frida_eval_lua(pid, lua, timeout=timeout)
        if ok and not (isinstance(raw, str) and raw.strip() == "__HZ_MINE_NEED_BOOTSTRAP__"):
            _mark_hz_mine_bootstrapped(cd, cache_key)

    if not ok:
        _invalidate_mine_pid_ctime(pid)
        return {"ok": False, "task": "mine_melee_refresh", "error": str(raw)}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {"ok": True, "task": "mine_melee_refresh", "result": parsed}
    except Exception as exc:
        return {
            "ok": False,
            "task": "mine_melee_refresh",
            "error": f"json decode failed: {exc}",
            "raw": str(raw)[:500],
        }


def _used_formations_lua(context: dict[str, Any] | None, pid: int) -> str:
    used: list[str] = []
    if isinstance(context, dict):
        used = list(context.get("used_formations_by_pid", {}).get(pid, []))
    return "{" + ",".join(f"[{json.dumps(str(u))}]=true" for u in used if u) + "}"


def _record_used_formations(context: dict[str, Any] | None, pid: int, uuids: list[str]) -> None:
    if not isinstance(context, dict) or not uuids:
        return
    bucket = context.setdefault("used_formations_by_pid", {}).setdefault(pid, [])
    for u in uuids:
        su = str(u or "").strip()
        if su and su not in bucket:
            bucket.append(su)


def action_mine_melee_refresh(
    cd: Any,
    pid: int,
    dry_run: bool = True,
    refresh_threshold_sec: int = 300,
    min_payload_pct: float = 10.0,
    reserve_formations: int = 1,
    **kwargs: Any,
) -> dict[str, Any]:
    """Execute the 3-Stage Mine Melee & Resource Gathering refresh pipeline.

    Stage 3A: Inspect active marches in DataCenter.WorldMyMarchDataManager (and
              WorldMarchDataManager fallback) and formations in
              DataCenter.ArmyFormationDataManager.
    Stage 3B: Detect melee refresh and depletion conditions (remaining gather duration
              below refresh_threshold_sec, expired/depleted/stuck tiles, or idle free
              formations ready to harvest/refresh an alliance mine or resource node).
    Stage 3C: Staged Recall -> Restock -> Re-dispatch (recall marches needing refresh
              or log would_recall in dry_run; restock and dispatch available free
              formations above reserve_formations to Alliance Mine or best world resource).
    """
    # Defensive handling if called with positional dict args via legacy 6-arg convention
    cfg: dict[str, Any] = {}
    if isinstance(kwargs.get("cfg"), dict):
        cfg = kwargs["cfg"]
    elif isinstance(kwargs.get("ccfg"), dict):
        cfg = kwargs["ccfg"]

    context: dict[str, Any] | None = kwargs.get("context") if isinstance(kwargs.get("context"), dict) else None
    task_cfg: dict[str, Any] = cfg.get("mine_melee_refresh") if isinstance(cfg.get("mine_melee_refresh"), dict) else {}
    gather_cfg: dict[str, Any] = cfg.get("auto_gather") if isinstance(cfg.get("auto_gather"), dict) else {}

    # Allow explicit parameters to win, while falling back to task_cfg when defaults are used
    threshold_sec = max(0, int(task_cfg.get("refresh_threshold_sec", refresh_threshold_sec) if refresh_threshold_sec == 300 and "refresh_threshold_sec" in task_cfg else refresh_threshold_sec))
    payload_pct_min = max(0.0, float(task_cfg.get("min_payload_pct", min_payload_pct) if min_payload_pct == 10.0 and "min_payload_pct" in task_cfg else min_payload_pct))
    if "reserve_formations" in task_cfg and reserve_formations == 1:
        reserve_cnt = max(0, int(task_cfg["reserve_formations"]))
    elif "formation_reserve" in cfg and reserve_formations == 1:
        reserve_cnt = max(0, int(cfg["formation_reserve"]))
    else:
        reserve_cnt = max(0, int(reserve_formations))

    prio = list(
        task_cfg.get("resource_priority")
        or gather_cfg.get("resource_priority")
        or ["Oil", "Metal", "Wood", "Electricity"]
    )
    min_lv = int(task_cfg.get("min_level", gather_cfg.get("min_level", 3)))
    max_lv = int(task_cfg.get("max_level", gather_cfg.get("max_level", 9)))
    max_dist = float(task_cfg.get("max_distance", gather_cfg.get("max_distance", 150.0)))
    prefer_alliance_mine = bool(task_cfg.get("prefer_alliance_mine", True))
    dispatch_world_resources = bool(task_cfg.get("dispatch_world_resources", True))
    force_melee_refresh = bool(kwargs.get("force_melee_refresh", task_cfg.get("force_melee_refresh", False)))

    claimed_keys = list((context or {}).get("claimed_gather_points", []))
    claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys if k) + "}"
    prio_lua = "{" + ",".join(f"[{json.dumps(str(r))}]={i}" for i, r in enumerate(prio, 1)) + "}"
    used_forms_lua = _used_formations_lua(context, pid)

    lua_body = f"""
local dryRun = {str(bool(dry_run)).lower()}
local refreshThresholdSec = {threshold_sec}
local minPayloadPct = {payload_pct_min}
local reserveCount = {reserve_cnt}
local minLv = {min_lv}
local maxLv = {max_lv}
local maxDist = {max_dist}
local preferAllianceMine = {str(prefer_alliance_mine).lower()}
local dispatchWorldResources = {str(dispatch_world_resources).lower()}
local forceMeleeRefresh = {str(force_melee_refresh).lower()}
local claimedPts = {claimed_lua}
local prioOrder = {prio_lua}
local excludeForms = {used_forms_lua}
local resTypeMap = {{[0]='Oil', [1]='Metal', [2]='Wood', [12]='Electricity', [14]='Money', [15]='Gold'}}

local snap = _get_player_snapshot()
local dc = DataCenter
local nowSec = tonumber(snap.serverSec or 0) or os.time()
local nowMs = nowSec * 1000

local out = {{
  ok = true,
  task = 'mine_melee_refresh',
  dry_run = dryRun,
  action = 'none',
  message = '',
  refresh_threshold_sec = refreshThresholdSec,
  min_payload_pct = minPayloadPct,
  reserve_formations = reserveCount,
  free_formations = snap.freeFormations,
  usable_formations = 0,
  active_mining_marches = {{}},
  refreshed_count = 0,
  dispatched_count = 0,
  would_recall = {{}},
  recalled_marches = {{}},
  would_dispatch = {{}},
  dispatched_marches = {{}},
  formations_overview = {{}},
  errors = {{}},
  alliance_mine_status = {{
    has_center = false,
    has_march = false,
    mines_found = 0,
    target_point_id = 0,
    target_uuid = '0',
    remain_num = 0,
  }},
  stages = {{
    stage_3a = 'pending',
    stage_3b = 'pending',
    stage_3c = 'pending',
  }},
}}

if not dc then
  out.ok = false
  out.error = 'DataCenter unavailable'
  return _enc(out)
end

-- ============================================================================
-- STAGE 3A: Inspect Active Marches, Formations & Alliance Mines
-- ============================================================================
local afm = dc.ArmyFormationDataManager or dc.ArmyFormationManager
local wmm = dc.WorldMyMarchDataManager
local wmdm = dc.WorldMarchDataManager
local amm = dc.AllianceMineManager
local wpm = dc.WorldPointManager

-- 1) Inspect Alliance Mine Manager first so we can identify alliance mine points
local allianceMineByPoint = {{}}
local bestAllianceMine = nil
if amm and snap.inAlliance then
  out.alliance_mine_status.has_center = (tonumber(_safe_call(function() return amm:CheckIfHasAllianceCenter() end, 0)) or 0) > 0
  out.alliance_mine_status.has_march = _safe_call(function() return amm:CheckIfHasMarch() end, false) and true or false
  local rawMines = _safe_call(function() return amm:GetMyAlMines() end, nil) or amm.allianceMineInfoDic or amm.allMines or nil
  local mineEntries = _extract_collection(rawMines)
  for _, entry in ipairs(mineEntries) do
    local m = entry.val
    if type(m) == 'table' or type(m) == 'userdata' then
      local pt = _first_pos_prop(m, 'pointId', 'point', 'pos')
      local rem = tonumber(_safe_call(function() return m.remainNum or m.num or m.remain or 1 end, 1)) or 0
      local initNum = _first_pos(_first_pos_prop(m, 'initNum', 'totalNum'), rem)
      local cSpd = _first_pos_prop(m, 'collectSpeed', 'speed')
      local expMs = _first_pos_prop(m, 'expireTime', 'endTime')
      local bId = _first_pos_prop(m, 'buildId', 'id')
      local rawMineUuid = _safe_call(function() return (m.uuid and tostring(m.uuid) ~= '0' and m.uuid) or (m.id and tostring(m.id) ~= '0' and m.id) or entry.key end, nil)
      local muuid = tostring(rawMineUuid or '0')
      if pt > 0 then
        out.alliance_mine_status.mines_found = out.alliance_mine_status.mines_found + 1
        allianceMineByPoint[pt] = {{
          pointId = pt,
          uuid = muuid,
          rawUuid = rawMineUuid,
          remainNum = rem,
          initNum = initNum,
          collectSpeed = cSpd,
          expireTime = expMs,
          buildId = bId,
        }}
        if rem > 0 and not bestAllianceMine then
          bestAllianceMine = allianceMineByPoint[pt]
          out.alliance_mine_status.target_point_id = pt
          out.alliance_mine_status.target_uuid = muuid
          out.alliance_mine_status.remain_num = rem
          out.alliance_mine_status.init_num = initNum
          out.alliance_mine_status.collect_speed = cSpd
          out.alliance_mine_status.expire_time = expMs
          out.alliance_mine_status.build_id = bId
        end
      end
    end
  end
end

-- 2) Inspect ArmyFormationDataManager
local inMarchSet = {{}}
if afm and afm.GetInMarchArmyFormationUuids then
  local im = _safe_call(function() return afm:GetInMarchArmyFormationUuids() end, nil)
  for _, entry in ipairs(_extract_collection(im)) do
    inMarchSet[tostring(entry.val)] = true
    inMarchSet[tostring(entry.key)] = true
  end
end

local rawFormList = nil
if afm then
  if afm.GetArmyFormationList then
    rawFormList = _safe_call(function() return afm:GetArmyFormationList() end, nil)
  end
  if not rawFormList and afm.ArmyFormationList then
    rawFormList = afm.ArmyFormationList
  end
  if not rawFormList and afm.GetFormationList then
    rawFormList = _safe_call(function() return afm:GetFormationList() end, nil)
  end
end

local formEntries = _extract_collection(rawFormList)
local formationByUuid = {{}}
local formationByIndex = {{}}
local formationByMarchUuid = {{}}
local freeFormList = {{}}
local countedFreeForms = 0

for _, entry in ipairs(formEntries) do
  local f = entry.val
  if type(f) == 'table' or type(f) == 'userdata' then
    local fuuid = tostring(_safe_call(function() return f.uuid end, '') or '')
    if fuuid ~= '' then
      local fIdx = tonumber(_safe_call(function() return f.index end, entry.key)) or 0
      local fState = tonumber(_safe_call(function() return f.state or f.status end, 0)) or 0
      local fMarchUuid = tostring(_safe_call(function() return f.marchUuid end, '') or '')
      local fMaxSol = tonumber(_safe_call(function() return f.maxSoldierNum end, 0)) or 0
      local fCurSol = 1
      if afm and afm.GetCurSoldierNum then
        local cs = _safe_call(function() return afm:GetCurSoldierNum(f.uuid) end, nil)
        if cs ~= nil then fCurSol = tonumber(cs) or 0 end
      else
        local csField = _safe_call(function() return f.curSoldierNum or f.soldierNum end, nil)
        if csField ~= nil then fCurSol = tonumber(csField) or 0 end
      end
      local isBusy = (fState ~= 0) or inMarchSet[fuuid] or (fMarchUuid ~= '' and fMarchUuid ~= '0')
      if not isBusy then
        countedFreeForms = countedFreeForms + 1
      end
      local fInfo = {{
        uuid = fuuid,
        rawUuid = _safe_call(function() return f.uuid end, fuuid),
        index = fIdx,
        state = fState,
        inMarch = isBusy and true or false,
        marchUuid = (fMarchUuid ~= '0') and fMarchUuid or '',
        curSoldierNum = fCurSol,
        maxSoldierNum = fMaxSol,
        rawObj = f,
      }}
      formationByUuid[fuuid] = fInfo
      if fIdx > 0 then formationByIndex[fIdx] = fInfo end
      if fMarchUuid ~= '' and fMarchUuid ~= '0' then
        formationByMarchUuid[fMarchUuid] = fInfo
      end
      table.insert(out.formations_overview, {{
        uuid = fuuid,
        index = fIdx,
        state = fState,
        in_march = isBusy and true or false,
        march_uuid = (fMarchUuid ~= '0') and fMarchUuid or '',
        cur_soldiers = fCurSol,
        max_soldiers = fMaxSol,
      }})
      if not isBusy and not excludeForms[fuuid] then
        table.insert(freeFormList, fInfo)
      end
    end
  end
end

table.sort(out.formations_overview, function(a, b)
  return (tonumber(a.index) or 99) < (tonumber(b.index) or 99)
end)
table.sort(freeFormList, function(a, b)
  return (tonumber(a.index) or 99) < (tonumber(b.index) or 99)
end)
if snap.freeFormations == 0 and countedFreeForms > 0 then
  out.free_formations = countedFreeForms
end

-- 3) Inspect WorldMyMarchDataManager (and WorldMarchDataManager fallback for own marches)
local marchSources = {{}}
if wmm then
  if wmm.GetMyMarchList then
    local ml = _safe_call(function() return wmm:GetMyMarchList() end, nil)
    if ml then table.insert(marchSources, {{src = 'wmm.GetMyMarchList', col = ml}}) end
  end
  if wmm.GetAllMarches then
    local al = _safe_call(function() return wmm:GetAllMarches() end, nil)
    if al then table.insert(marchSources, {{src = 'wmm.GetAllMarches', col = al}}) end
  end
  if wmm.allMarch then table.insert(marchSources, {{src = 'wmm.allMarch', col = wmm.allMarch}}) end
  if wmm.allMarches then table.insert(marchSources, {{src = 'wmm.allMarches', col = wmm.allMarches}}) end
  if wmm.marchDic then table.insert(marchSources, {{src = 'wmm.marchDic', col = wmm.marchDic}}) end
  if wmm.myMarchDic then table.insert(marchSources, {{src = 'wmm.myMarchDic', col = wmm.myMarchDic}}) end
  if wmm.marchList then table.insert(marchSources, {{src = 'wmm.marchList', col = wmm.marchList}}) end
end
if wmdm then
  if wmdm.allMarches then table.insert(marchSources, {{src = 'wmdm.allMarches', col = wmdm.allMarches, filterOwn = true}}) end
  if wmdm.marchDic then table.insert(marchSources, {{src = 'wmdm.marchDic', col = wmdm.marchDic, filterOwn = true}}) end
  if wmdm.GetAllMarches then
    local wal = _safe_call(function() return wmdm:GetAllMarches() end, nil)
    if wal then table.insert(marchSources, {{src = 'wmdm.GetAllMarches', col = wal, filterOwn = true}}) end
  end
end

local collectTargetType = tonumber((MarchTargetType and MarchTargetType.COLLECT) or 2) or 2
local allianceMineTargetType = tonumber((MarchTargetType and MarchTargetType.COLLECT_ALLIANCE_BUILD_RESOURCE) or 35) or 35

local seenMarchUuids = {{}}
local rawMarchUuidByStr = {{}}
local activeAllianceMinePoints = {{}}

for _, mSrc in ipairs(marchSources) do
  local entries = _extract_collection(mSrc.col)
  for _, entry in ipairs(entries) do
    local m = entry.val
    if type(m) == 'table' or type(m) == 'userdata' then
      local ownerUid = tostring(_safe_call(function() return m.uid or m.ownerUid or m.playerUid end, '') or '')
      local isOwn = (not mSrc.filterOwn) or (ownerUid == '') or (snap.uid ~= '' and ownerUid == snap.uid)
      if isOwn then
        local rawMuuid = _safe_call(function() return m.uuid or m.marchUuid or m.id end, entry.key)
        local muuid = tostring(rawMuuid or '')
        if muuid ~= '' and not seenMarchUuids[muuid] then
          rawMarchUuidByStr[muuid] = rawMuuid
          local tType = tonumber(_safe_call(function() return m.target or m.targetType or m.marchType or m.type end, -1)) or -1
          local tPos = _first_pos_prop(m, 'targetPos', 'finalTargetPos', 'realTargetPos', 'targetPoint', 'pointId', 'endIndex', 'targetIndex')
          local isTargetForMineFlag = _safe_call(function()
            if m.IsTargetForMine then return m:IsTargetForMine() end
            return m._isTargetForMine
          end, false) and true or false
          local isAlMine = (tType == allianceMineTargetType) or (tPos > 0 and allianceMineByPoint[tPos] ~= nil)
          local isWorldGather = (tType == collectTargetType or tType == 21 or tType == 87 or tType == 100 or tType == 111 or tType == 112 or tType == 122 or isTargetForMineFlag)
          if not isWorldGather and not isAlMine and tType ~= 3 and tPos > 0 and wpm and wpm.GetPointInfo then
            local pInfo = _safe_call(function() return wpm:GetPointInfo(tPos) end, nil)
            if pInfo and pInfo.resourceInfo then
              isWorldGather = true
            end
          end

          -- Link ownerFormationUuid -> marchUuid in formations_overview even for non-mining marches
          local rawOwnerFormUuid = tostring(_safe_call(function() return m.ownerFormationUuid or m.formationUuid or m.armyFormationUuid or m.formUuid or m.teamUuid end, '') or '')
          if rawOwnerFormUuid ~= '' and rawOwnerFormUuid ~= '0' then
            for _, fo in ipairs(out.formations_overview) do
              if fo.uuid == rawOwnerFormUuid and (fo.march_uuid == '' or fo.march_uuid == '0') then
                fo.march_uuid = muuid
              end
            end
          end

          if isAlMine or isWorldGather then
            seenMarchUuids[muuid] = true
            if isAlMine and tPos > 0 then
              activeAllianceMinePoints[tPos] = muuid
              out.alliance_mine_status.has_march = true
            end

            local formUuid = (rawOwnerFormUuid ~= '0') and rawOwnerFormUuid or ''
            local formIdx = _first_pos_prop(m, 'formationId', 'formationIndex', 'index')
            if formUuid == '' and formationByMarchUuid[muuid] then
              formUuid = formationByMarchUuid[muuid].uuid
              formIdx = formationByMarchUuid[muuid].index
            elseif formUuid == '' and formIdx > 0 and formationByIndex[formIdx] then
              formUuid = formationByIndex[formIdx].uuid
            elseif formUuid ~= '' and formationByUuid[formUuid] and formIdx == 0 then
              formIdx = formationByUuid[formUuid].index
            end

            local mState = _first_pos_prop(m, 'state', 'marchState', 'status')
            local actStart = tonumber(_safe_call(function() return m.actStartTime end, 0)) or 0
            local actEnd = tonumber(_safe_call(function() return m.actEndTime end, 0)) or 0
            local rawStart = (actStart > 0 and actEnd > 0) and actStart or _first_pos_prop(m, 'startTime', 'collectStartTime', 'createTime', 'beginTime')
            local rawEnd = (actEnd > 0) and actEnd or _first_pos_prop(m, 'endTime', 'collectEndTime', 'finishTime', 'arriveTime')
            local startMs = (rawStart > 0 and rawStart < 1e11) and (rawStart * 1000) or rawStart
            local endMs = (rawEnd > 0 and rawEnd < 1e11) and (rawEnd * 1000) or rawEnd

            local remSec = -1
            if endMs > 0 and nowMs > 0 then
              remSec = math.max(0, math.floor((endMs - nowMs) / 1000))
            end

            local cInfo = _safe_call(function() return m.collectInfo or m.resourceInfo or m.extraInfo end, nil)
            local cap = _first_pos(
              _first_pos_prop(m, 'maxLoad', 'loadMax', 'capacity', 'armyWeight', 'collectMax', 'totalRes', 'maxCollect', 'carryMax'),
              type(cInfo) == 'table' and _first_pos_prop(cInfo, 'maxLoad', 'total', 'capacity', 'maxNum') or 0
            )
            local curLoad = _first_pos(
              _first_pos_prop(m, 'curLoad', 'collectNum', 'gathered', 'curCollect', 'haveCollect', 'resNum'),
              type(cInfo) == 'table' and _first_pos_prop(cInfo, 'curLoad', 'collectNum', 'num', 'gathered') or 0
            )
            local rawSpd = _first_pos(
              _first_pos_prop(m, 'collectSpeed', 'collectSpd'),
              type(cInfo) == 'table' and _first_pos_prop(cInfo, 'collectSpeed', 'speed') or 0
            )
            if rawSpd < 1e-6 then rawSpd = 0 end
            if rawSpd == 0 and isAlMine and tPos > 0 and allianceMineByPoint[tPos] then
              rawSpd = tonumber(allianceMineByPoint[tPos].collectSpeed or 0) or 0
            end
            local speed = rawSpd

            local elapsedSec = 0
            if startMs > 0 and nowMs > startMs then
              elapsedSec = math.floor((nowMs - startMs) / 1000)
            end
            local totalDurSec = 0
            if startMs > 0 and endMs > startMs then
              totalDurSec = math.floor((endMs - startMs) / 1000)
            end

            if curLoad <= 0 and speed > 0 and elapsedSec > 0 then
              curLoad = math.floor(speed * elapsedSec)
            end
            if cap <= 0 and speed > 0 and totalDurSec > 0 then
              cap = math.floor(speed * totalDurSec)
            end
            if curLoad <= 0 and cap > 0 and totalDurSec > 0 and elapsedSec > 0 then
              curLoad = math.min(cap, math.floor(cap * (elapsedSec / totalDurSec)))
            end

            local payloadPct = 0.0
            if cap > 0 and curLoad > 0 then
              payloadPct = math.min(100.0, math.floor((curLoad / cap) * 1000.0) / 10.0)
            elseif totalDurSec > 0 and elapsedSec > 0 then
              payloadPct = math.min(100.0, math.floor((elapsedSec / totalDurSec) * 1000.0) / 10.0)
            end

            local tileRem = -1
            if isAlMine and tPos > 0 and allianceMineByPoint[tPos] then
              tileRem = tonumber(allianceMineByPoint[tPos].remainNum or -1) or -1
            elseif tPos > 0 and wpm and wpm.GetPointInfo then
              local pi = _safe_call(function() return wpm:GetPointInfo(tPos) end, nil)
              local ri = pi and pi.resourceInfo
              if ri then
                local tr = _safe_call(function() return ri.remainRes or ri.remainNum or ri.num or ri.resCount end, nil)
                if tr ~= nil then tileRem = tonumber(tr) or -1 end
              end
            end

            local tx, ty = _to_xy(tPos)
            table.insert(out.active_mining_marches, {{
              marchUuid = muuid,
              formationUuid = formUuid,
              formationIndex = formIdx,
              pointId = tPos,
              coords = {{x = tx, y = ty}},
              targetType = tType,
              targetKind = isAlMine and 'alliance_mine' or 'world_resource',
              isAllianceMine = isAlMine and true or false,
              state = mState,
              startTime = startMs,
              endTime = endMs,
              remaining_sec = remSec,
              gathered_load = curLoad,
              capacity = cap,
              payload_pct = payloadPct,
              tile_remaining = tileRem,
              needs_refresh = false,
              refresh_reason = '',
            }})
          end
        end
      end
    end
  end
end

out.stages.stage_3a = 'completed'

-- ============================================================================
-- STAGE 3B: Detect Melee Refresh & Depletion Conditions
-- ============================================================================
local returningState = tonumber((MarchState and (MarchState.Return or MarchState.Returning or MarchState.Back)) or 3) or 3
local marchesToRecall = {{}}

for _, gm in ipairs(out.active_mining_marches) do
  local isReturning = (gm.state == returningState)
  if not isReturning then
    local needsRefresh = false
    local reason = ''

    if gm.endTime > 0 and nowMs > 0 and gm.endTime <= nowMs then
      needsRefresh = true
      reason = 'expired_or_depleted_endtime'
    elseif gm.tile_remaining == 0 then
      needsRefresh = true
      reason = 'tile_depleted_zero_remaining'
    elseif gm.remaining_sec >= 0 and gm.remaining_sec <= refreshThresholdSec then
      needsRefresh = true
      reason = string.format('remaining_below_threshold_%ds', gm.remaining_sec)
    elseif forceMeleeRefresh and gm.payload_pct >= minPayloadPct then
      needsRefresh = true
      reason = string.format('forced_melee_refresh_payload_%.1f_pct', gm.payload_pct)
    end

    gm.needs_refresh = needsRefresh
    gm.refresh_reason = reason
    if needsRefresh then
      table.insert(marchesToRecall, gm)
    end
  else
    gm.refresh_reason = 'already_returning'
  end
end

out.stages.stage_3b = 'completed'

-- ============================================================================
-- STAGE 3C: Staged Recall -> Restock -> Re-dispatch
-- ============================================================================
local mu = package.loaded['SlgEngine.Util.MarchUtil.MarchUtil'] or package.loaded['Util.MarchUtil_SLG'] or MarchUtil

-- Step 3C.1: Recall marches requiring melee refresh
for _, gm in ipairs(marchesToRecall) do
  local recEntry = {{
    marchUuid = gm.marchUuid,
    formationUuid = gm.formationUuid,
    formationIndex = gm.formationIndex,
    pointId = gm.pointId,
    coords = gm.coords,
    targetKind = gm.targetKind,
    remaining_sec = gm.remaining_sec,
    payload_pct = gm.payload_pct,
    reason = gm.refresh_reason,
    mode = dryRun and 'would_recall' or 'recalled',
  }}
  if dryRun then
    table.insert(out.would_recall, recEntry)
    if gm.isAllianceMine and gm.pointId > 0 then
      activeAllianceMinePoints[gm.pointId] = nil
    end
  else
    local recalledOk = false
    local recallErr = nil
    local gmUuidStr = tostring(gm.marchUuid or '')
    local rawMarchUuid = rawMarchUuidByStr[gmUuidStr]
    if rawMarchUuid == nil then
      if #gmUuidStr <= 15 then
        local n = tonumber(gmUuidStr)
        rawMarchUuid = (n ~= nil and tostring(n) == gmUuidStr) and n or gm.marchUuid
      else
        rawMarchUuid = gm.marchUuid
      end
    end
    if mu and mu.OnBackHome then
      local okR, errR = pcall(function() mu.OnBackHome(rawMarchUuid) end)
      recalledOk = okR
      if not okR then recallErr = 'OnBackHome: ' .. tostring(errR) end
    elseif mu and mu.StartMarch and MarchTargetType and MarchTargetType.BACK_HOME then
      local homePt = (mu.GetFormationStartPos and _safe_call(function() return mu.GetFormationStartPos() end, 0)) or tonumber(snap.mainPos or 0) or 0
      local okR, errR = pcall(function() mu.StartMarch(MarchTargetType.BACK_HOME, homePt, -1, -1, rawMarchUuid) end)
      recalledOk = okR
      if not okR then recallErr = 'StartMarch: ' .. tostring(errR) end
    elseif mu and mu.SendChangeMarchToServer and MarchTargetType and MarchTargetType.BACK_HOME then
      local homePt = (mu.GetFormationStartPos and _safe_call(function() return mu.GetFormationStartPos() end, 0)) or tonumber(snap.mainPos or 0) or 0
      local okR, errR = pcall(function()
        mu.SendChangeMarchToServer(rawMarchUuid, MarchTargetType.BACK_HOME, homePt, 0, true, tonumber(snap.serverId) or 0, -1)
      end)
      recalledOk = okR
      if not okR then recallErr = 'SendChangeMarchToServer: ' .. tostring(errR) end
    elseif SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.WorldMarchChange and MarchTargetType and MarchTargetType.BACK_HOME then
      local worldId = (LuaEntry and LuaEntry.Player and LuaEntry.Player.GetCurWorldId and _safe_call(function() return LuaEntry.Player:GetCurWorldId() end, 0)) or 0
      local okR, errR = pcall(function()
        SFSNetwork.SendMessage(MsgDefines.WorldMarchChange, rawMarchUuid, MarchTargetType.BACK_HOME, 0, '', worldId, true, tonumber(snap.serverId) or 0, -1, true)
      end)
      recalledOk = okR
      if not okR then recallErr = 'WorldMarchChange: ' .. tostring(errR) end
    else
      recallErr = 'no_verified_recall_handler'
    end
    recEntry.sent = recalledOk and true or false
    if recallErr then
      recEntry.error = recallErr
      table.insert(out.errors, string.format('Recall march %s: %s', tostring(gm.marchUuid or '?'), recallErr))
    end
    if recalledOk then
      table.insert(out.recalled_marches, recEntry)
      out.refreshed_count = out.refreshed_count + 1
      if gm.isAllianceMine and gm.pointId > 0 then
        activeAllianceMinePoints[gm.pointId] = nil
        out.alliance_mine_status.has_march = false
      end
    end
  end
end

-- Step 3C.2: Restock and filter usable free formations above reserveCount
local stockedFreeForms = {{}}
for _, fInfo in ipairs(freeFormList) do
  local curSol = tonumber(fInfo.curSoldierNum or 0) or 0
  if curSol <= 0 then
    if not dryRun and afm then
      if afm.AutoAddHero then
        local okH, errH = pcall(function() afm:AutoAddHero(fInfo.rawUuid) end)
        if not okH then
          table.insert(out.errors, string.format('F%s AutoAddHero: %s', tostring(fInfo.formationIndex or '?'), tostring(errH)))
        end
      end
      if afm.AutoAddSoldier then
        local okS, errS = pcall(function() afm:AutoAddSoldier(fInfo.rawUuid) end)
        if not okS then
          table.insert(out.errors, string.format('F%s AutoAddSoldier: %s', tostring(fInfo.formationIndex or '?'), tostring(errS)))
        end
      end
      if afm.GetCurSoldierNum then
        curSol = tonumber(_safe_call(function() return afm:GetCurSoldierNum(fInfo.rawUuid) end, 0)) or 0
      end
      if curSol <= 0 and afm.RefreshFormationSoldier then
        local okR, errR = pcall(function() afm:RefreshFormationSoldier(fInfo.rawUuid) end)
        if not okR then
          table.insert(out.errors, string.format('F%s RefreshFormationSoldier: %s', tostring(fInfo.formationIndex or '?'), tostring(errR)))
        end
      end
      if afm.SendFormToServer then
        local okF, errF = pcall(function() afm:SendFormToServer() end)
        if not okF then
          table.insert(out.errors, string.format('F%s SendFormToServer: %s', tostring(fInfo.formationIndex or '?'), tostring(errF)))
        end
      end
      if afm.GetCurSoldierNum then
        curSol = tonumber(_safe_call(function() return afm:GetCurSoldierNum(fInfo.rawUuid) end, 0)) or 0
      end
      fInfo.curSoldierNum = curSol
    else
      -- In dry-run mode, report formation as restockable without mutating client state
      fInfo.would_restock = true
      curSol = 1
    end
  end
  if curSol > 0 then
    table.insert(stockedFreeForms, fInfo)
  end
end

local usableForms = {{}}
if #stockedFreeForms > reserveCount then
  for i = reserveCount + 1, #stockedFreeForms do
    table.insert(usableForms, stockedFreeForms[i])
  end
end
out.usable_formations = #usableForms

-- Step 3C.3: Dispatch usable free formations to Alliance Mine first, then World Resource nodes
local fCursor = 1

if preferAllianceMine and fCursor <= #usableForms and bestAllianceMine and bestAllianceMine.pointId > 0 then
  local alPt = bestAllianceMine.pointId
  local alreadyHasActiveAlMarch = out.alliance_mine_status.has_march or (activeAllianceMinePoints[alPt] ~= nil)
  if not alreadyHasActiveAlMarch then
    local f = usableForms[fCursor]
    fCursor = fCursor + 1
    local tx, ty = _to_xy(alPt)
    local dispEntry = {{
      formationUuid = f.uuid,
      formationIndex = f.index,
      pointId = alPt,
      coords = {{x = tx, y = ty}},
      targetUuid = tostring(bestAllianceMine.uuid or '0'),
      targetKind = 'alliance_mine',
      marchTargetType = allianceMineTargetType,
      remainNum = bestAllianceMine.remainNum,
      mode = dryRun and 'would_dispatch' or 'dispatched',
    }}
    if dryRun then
      table.insert(out.would_dispatch, dispEntry)
    else
      local sentOk = false
      local sendErr = nil
      if mu and mu.SendCreateMarchMessage then
        local mineTargetUuid = bestAllianceMine.rawUuid
        if mineTargetUuid == nil then
          local uStr = tostring(bestAllianceMine.uuid or '')
          if uStr == '' or uStr == '0' then
            mineTargetUuid = 0
          elseif #uStr <= 15 then
            local n = tonumber(uStr)
            mineTargetUuid = (n ~= nil and tostring(n) == uStr) and n or uStr
          else
            mineTargetUuid = uStr
          end
        end
        local okS, errS = pcall(function()
          mu.SendCreateMarchMessage(
            f.rawUuid,
            allianceMineTargetType,
            alPt,
            mineTargetUuid,
            0,
            true,
            true,
            snap.serverId
          )
        end)
        sentOk = okS and true or false
        if not okS then sendErr = tostring(errS) end
      else
        sendErr = 'SendCreateMarchMessage unavailable'
      end
      dispEntry.sent = sentOk and true or false
      if sendErr then
        dispEntry.error = sendErr
        table.insert(out.errors, string.format('Dispatch F%s to alliance mine pt=%s: %s', tostring(f.index or '?'), tostring(alPt), sendErr))
      end
      if sentOk then
        table.insert(out.dispatched_marches, dispEntry)
        out.dispatched_count = out.dispatched_count + 1
      end
    end
  end
end

-- Dispatch any remaining usable free formations to best unoccupied World Resource tiles
if dispatchWorldResources and fCursor <= #usableForms and wpm and wpm.allViewPoints and wpm.GetPointInfo then
  local cands = {{}}
  local worldResType = tonumber((PointType and PointType.WorldResource) or 7) or 7
  local function _scan_vp_point(ptIdx, ptObj)
    if not ptObj then return end
    local isTbl = (type(ptObj) == 'table')
    local ptType = isTbl and (tonumber(ptObj.pointType or -1) or -1) or (tonumber(_safe_call(function() return ptObj.pointType end, -1)) or -1)
    if ptType ~= worldResType then return end
    local pnum = tonumber(ptIdx) or (isTbl and tonumber(ptObj.pointId) or tonumber(_safe_call(function() return ptObj.pointId end, 0))) or 0
    if pnum <= 0 then return end
    local claimKey = tostring(snap.serverId) .. ':' .. tostring(pnum)
    if claimedPts[claimKey] then return end
    local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil)
    local ri = info and info.resourceInfo or nil
    if ri and tonumber(ri.gatherUuid or 0) == 0 and tostring(ri.ownerUid or '') == '' then
      local rName = nil
      local lv = tonumber(ri.level or 0) or 0
      local rmeta = _get_mine_gather_res_meta(ri.resourceId or 0)
      if rmeta then
        rName = resTypeMap[rmeta.resource_type] or tostring(rmeta.resource_type)
        if rmeta.level > 0 then lv = rmeta.level end
      elseif ri.type ~= nil then
        local rTypeNum = tonumber(ri.type) or -1
        rName = resTypeMap[rTypeNum] or tostring(rTypeNum)
      end
      local pRank = rName and prioOrder[rName] or nil
      if pRank and lv >= minLv and lv <= maxLv then
        local d = snap.mainPos > 0 and _dist(snap.mainPos, pnum) or 0
        if d <= maxDist then
          local tx, ty = _to_xy(pnum)
          table.insert(cands, {{
            pointId = pnum,
            coords = {{x = tx, y = ty}},
            claimKey = claimKey,
            resourceType = rName,
            level = lv,
            dist = math.floor(d * 10) / 10,
            prio = pRank,
            score = pRank * 10000 - lv * 200 + d,
          }})
        end
      end
    end
  end
  if type(wpm.allViewPoints) == 'table' then
    for ptIdx, ptObj in pairs(wpm.allViewPoints) do
      _scan_vp_point(ptIdx, ptObj)
    end
  else
    for _, entry in ipairs(_extract_collection(wpm.allViewPoints)) do
      _scan_vp_point(entry.key, entry.val)
    end
  end

  table.sort(cands, function(a, b) return a.score < b.score end)

  local cIdx = 1
  while fCursor <= #usableForms and cIdx <= #cands do
    local f = usableForms[fCursor]
    local tile = cands[cIdx]
    fCursor = fCursor + 1
    cIdx = cIdx + 1
    local ptId = tonumber(tile.pointId) or 0
    local dispEntry = {{
      formationUuid = f.uuid,
      formationIndex = f.index,
      pointId = ptId,
      coords = tile.coords,
      claimKey = tile.claimKey,
      resourceType = tile.resourceType,
      level = tile.level,
      dist = tile.dist,
      targetKind = 'world_resource',
      marchTargetType = collectTargetType,
      mode = dryRun and 'would_dispatch' or 'dispatched',
    }}
    if dryRun then
      table.insert(out.would_dispatch, dispEntry)
    else
      local sentOk = false
      local sendErr = nil
      if mu and mu.SendCreateMarchMessage and ptId > 0 then
        local okS, errS = pcall(function()
          mu.SendCreateMarchMessage(
            f.rawUuid or tonumber(f.uuid) or f.uuid,
            collectTargetType,
            ptId,
            0,
            0,
            true,
            true,
            tonumber(snap.serverId) or 0
          )
        end)
        sentOk = okS and true or false
        if not okS then sendErr = tostring(errS) end
      else
        sendErr = (ptId <= 0) and 'invalid_target_point' or 'SendCreateMarchMessage unavailable'
      end
      dispEntry.sent = sentOk and true or false
      if sendErr then
        dispEntry.error = sendErr
        table.insert(out.errors, string.format('Dispatch F%s to resource pt=%s: %s', tostring(f.index or '?'), tostring(ptId), sendErr))
      end
      if sentOk then
        table.insert(out.dispatched_marches, dispEntry)
        out.dispatched_count = out.dispatched_count + 1
      end
    end
  end
end

out.stages.stage_3c = 'completed'

local recallActCount = dryRun and #out.would_recall or out.refreshed_count
local dispatchActCount = dryRun and #out.would_dispatch or out.dispatched_count
if recallActCount > 0 and dispatchActCount > 0 then
  out.action = dryRun and 'would_refresh_and_dispatch' or 'refreshed_and_dispatched'
  out.message = string.format(
    '%s %d mining march(es) and %s %d squad(s) (%d active mining marches)',
    dryRun and 'Would recall' or 'Recalled',
    recallActCount,
    dryRun and 'would dispatch' or 'dispatched',
    dispatchActCount,
    #out.active_mining_marches
  )
elseif recallActCount > 0 then
  out.action = dryRun and 'would_recall' or 'recalled_for_refresh'
  out.message = string.format(
    '%s %d mining march(es) below threshold/depleted (%d active mining marches)',
    dryRun and 'Would recall' or 'Recalled',
    recallActCount,
    #out.active_mining_marches
  )
elseif dispatchActCount > 0 then
  out.action = dryRun and 'would_dispatch' or 'dispatched_mine'
  out.message = string.format(
    '%s %d free formation(s) to mine/gather (%d active mining marches)',
    dryRun and 'Would dispatch' or 'Dispatched',
    dispatchActCount,
    #out.active_mining_marches
  )
elseif not dryRun and #out.errors > 0 then
  out.ok = false
  out.action = 'send_failed'
  out.error = table.concat(out.errors, '; ')
  out.message = 'Mine melee action failed: ' .. out.error
elseif #out.active_mining_marches > 0 then
  out.action = 'monitoring_active_mines'
  out.message = string.format(
    'Monitoring %d active mining march(es); none below %ds threshold (%d free formations)',
    #out.active_mining_marches,
    refreshThresholdSec,
    out.free_formations
  )
elseif out.usable_formations == 0 then
  out.action = 'no_free_formation_above_reserve'
  out.message = string.format(
    'No usable free formations above reserve=%d (free=%d)',
    reserveCount,
    out.free_formations
  )
else
  out.action = 'none'
  out.message = 'No active mining marches needing refresh and no unoccupied mine targets in viewport'
end

return _enc(out)
"""
    res = _eval_mine_lua(cd, pid, lua_body, timeout=12.0)
    if isinstance(res, dict):
        for list_key in (
            "would_recall",
            "recalled_marches",
            "would_dispatch",
            "dispatched_marches",
            "active_mining_marches",
            "formations_overview",
            "errors",
        ):
            val = res.get(list_key)
            if not isinstance(val, list):
                res[list_key] = []
    if not dry_run and context is not None and isinstance(res, dict) and res.get("ok") and isinstance(res.get("dispatched_marches"), list):
        used_uuids: list[str] = []
        claimed = context.setdefault("claimed_gather_points", [])
        for item in res["dispatched_marches"]:
            if not isinstance(item, dict) or not item.get("sent", False):
                continue
            ck = item.get("claimKey")
            if ck and ck not in claimed:
                claimed.append(ck)
            if item.get("formationUuid"):
                used_uuids.append(str(item["formationUuid"]))
        if used_uuids:
            _record_used_formations(context, pid, used_uuids)

    # Stage 3D: Delegate Monday/Tuesday Mine Melee (MineCaveManager, ActMineCave=25)
    # to the 4-stage Python-paced run_mining_event pipeline (Stage A Sync -> Stage B Claim -> Stage C Multi-Refresh -> Stage D Attack)
    if isinstance(res, dict) and res.get("ok"):
        try:
            ba_path = TOOLS_DIR / "bot actions.py"
            if ba_path.exists():
                ba_mod = None
                with _MODULE_LOAD_LOCK:
                    existing_ba = sys.modules.get(_BA_SINGLETON_NAME) or sys.modules.get("bot_actions")
                    if existing_ba is None:
                        resolved_ba = str(ba_path.resolve())
                        for cand in list(sys.modules.values()):
                            cand_file = getattr(cand, "__file__", None)
                            if cand_file:
                                try:
                                    if str(Path(cand_file).resolve()) == resolved_ba:
                                        existing_ba = cand
                                        break
                                except Exception:
                                    pass
                    if existing_ba is not None:
                        ba_mod = existing_ba
                        sys.modules.setdefault(_BA_SINGLETON_NAME, ba_mod)
                        sys.modules.setdefault("bot_actions", ba_mod)
                    else:
                        spec_ba = importlib.util.spec_from_file_location("bot_actions", str(ba_path))
                        if spec_ba and spec_ba.loader:
                            ba_mod = importlib.util.module_from_spec(spec_ba)
                            sys.modules[_BA_SINGLETON_NAME] = ba_mod
                            sys.modules["bot_actions"] = ba_mod
                            try:
                                spec_ba.loader.exec_module(ba_mod)
                            except Exception:
                                sys.modules.pop(_BA_SINGLETON_NAME, None)
                                sys.modules.pop("bot_actions", None)
                                raise
                if ba_mod is not None and hasattr(ba_mod, "run_mining_event"):
                    client_state_dict = kwargs.get("client_state") if isinstance(kwargs.get("client_state"), dict) else {}
                    cave_res = ba_mod.run_mining_event(
                        cd,
                        pid,
                        client_state_dict,
                        cfg,
                        dry_run=dry_run,
                        context=context,
                    )
                    res["mine_cave_melee"] = cave_res
                    if isinstance(res.get("stages"), dict):
                        if isinstance(cave_res, dict) and cave_res.get("ok"):
                            res["stages"]["stage_3d_mine_cave_melee"] = "completed"
                        else:
                            res["stages"]["stage_3d_mine_cave_melee"] = "failed"
                    if isinstance(cave_res, dict):
                        if cave_res.get("refreshes_performed"):
                            res["mine_cave_refreshes_performed"] = int(cave_res.get("refreshes_performed") or 0)
                        if cave_res.get("attacked"):
                            res["mine_cave_attacked"] = cave_res["attacked"]
        except Exception as exc:
            res["mine_cave_melee"] = {"ok": False, "error": str(exc)}
            if isinstance(res.get("stages"), dict):
                res["stages"]["stage_3d_mine_cave_melee"] = "failed"

    if isinstance(res, dict):
        res["detail_lines"] = _build_mine_melee_detail_lines(res)
    return res


def _build_mine_melee_detail_lines(res: dict[str, Any]) -> list[str]:
    """Build structured detail lines for Mine Melee Refresh & Resource Gathering."""
    lines: list[str] = []
    if not res.get("ok", True):
        lines.append(f"Error: {res.get('error') or res.get('reason') or 'unknown error'}")
        return lines
    dry_prefix = "[DRY-RUN] " if res.get("dry_run") else ""
    lines.append(
        f"{dry_prefix}Formations: free={res.get('free_formations', 0)}, usable={res.get('usable_formations', 0)}, "
        f"reserve={res.get('reserve_formations', 0)} (threshold={res.get('refresh_threshold_sec', 0)}s, min_payload={res.get('min_payload_pct', 0)}%)"
    )
    am_st = res.get("alliance_mine_status") or {}
    if isinstance(am_st, dict) and am_st.get("has_center"):
        lines.append(
            f"Alliance Mine: mines_found={am_st.get('mines_found', 0)}, has_march={bool(am_st.get('has_march'))}, "
            f"target_pt={am_st.get('target_point_id', 0)}, remain={am_st.get('remain_num', 0)}"
        )
    active = res.get("active_mining_marches") or []
    lines.append(f"Active mining marches: {len(active)}")
    for m in active[:8]:
        if not isinstance(m, dict):
            continue
        c = m.get("coords") or {}
        coord_str = f"({c.get('x', '?')},{c.get('y', '?')})" if isinstance(c, dict) else ""
        lines.append(
            f"  • Squad F{m.get('formationIndex', '?')} @ {m.get('targetKind', '?')} pt={m.get('pointId')} {coord_str}: "
            f"rem={m.get('remaining_sec', -1)}s, payload={m.get('payload_pct', 0)}%, tile_rem={m.get('tile_remaining', -1)}, "
            f"status={m.get('refresh_reason') or ('needs_refresh' if m.get('needs_refresh') else 'ok')}"
        )
    for rec in (res.get("recalled_marches") or res.get("would_recall") or []):
        if isinstance(rec, dict):
            lines.append(
                f"  • Recall F{rec.get('formationIndex', '?')} march={rec.get('marchUuid')} pt={rec.get('pointId')} "
                f"mode={rec.get('mode', '?')} reason={rec.get('reason', '?')}"
            )
    for disp in (res.get("dispatched_marches") or res.get("would_dispatch") or []):
        if isinstance(disp, dict):
            c = disp.get("coords") or {}
            coord_str = f"({c.get('x', '?')},{c.get('y', '?')})" if isinstance(c, dict) else ""
            lines.append(
                f"  • Dispatch F{disp.get('formationIndex', '?')} -> {disp.get('targetKind', '?')} "
                f"{disp.get('resourceType', '')} Lv{disp.get('level', '')} pt={disp.get('pointId')} {coord_str} mode={disp.get('mode', '?')}"
            )
    cave = res.get("mine_cave_melee")
    if isinstance(cave, dict):
        if not cave.get("ok", True):
            lines.append(f"Mine Cave Melee error: {cave.get('error')}")
        else:
            cave_msg = cave.get("action") or cave.get("reason") or cave.get("status") or "checked"
            lines.append(
                f"Mine Cave Melee (Mon/Tue): open={bool(cave.get('event_open'))}, fights={cave.get('fight_num', 0)}, "
                f"claimed={len(cave.get('claimed') or [])}, refreshes={cave.get('refreshes_performed', 0)}, status={cave_msg}"
            )
            for cl in (cave.get("detail_lines") or []):
                lines.append(f"  [Cave] {cl}")
    if res.get("message"):
        lines.append(f"Summary: {res.get('message')}")
    return lines


def run_mine_melee_refresh(
    cd: Any,
    pid: int,
    client_state: dict[str, Any] | None = None,
    cfg: dict[str, Any] | None = None,
    dry_run: bool = True,
    context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Standard 6-argument TASK_REGISTRY adapter for action_mine_melee_refresh."""
    cfg_dict = cfg if isinstance(cfg, dict) else {}
    task_cfg = cfg_dict.get("mine_melee_refresh") if isinstance(cfg_dict.get("mine_melee_refresh"), dict) else {}
    threshold_sec = int(kwargs.pop("refresh_threshold_sec", task_cfg.get("refresh_threshold_sec", 300)))
    min_payload = float(kwargs.pop("min_payload_pct", task_cfg.get("min_payload_pct", 10.0)))
    reserve = int(
        kwargs.pop(
            "reserve_formations",
            task_cfg.get("reserve_formations", cfg_dict.get("formation_reserve", 1)),
        )
    )
    return action_mine_melee_refresh(
        cd,
        pid,
        dry_run=dry_run,
        refresh_threshold_sec=threshold_sec,
        min_payload_pct=min_payload,
        reserve_formations=reserve,
        client_state=client_state,
        cfg=cfg_dict,
        context=context,
        **kwargs,
    )


def _load_client_discovery() -> Any:
    cd_path = TOOLS_DIR / "client discovery.py"
    with _MODULE_LOAD_LOCK:
        existing = sys.modules.get(_CD_SINGLETON_NAME) or sys.modules.get("client_discovery")
        if existing is not None:
            sys.modules.setdefault(_CD_SINGLETON_NAME, existing)
            sys.modules.setdefault("client_discovery", existing)
            return existing
        resolved = str(cd_path.resolve())
        for cand in list(sys.modules.values()):
            cand_file = getattr(cand, "__file__", None)
            if cand_file:
                try:
                    if str(Path(cand_file).resolve()) == resolved:
                        sys.modules[_CD_SINGLETON_NAME] = cand
                        sys.modules.setdefault("client_discovery", cand)
                        return cand
                except Exception:
                    pass
        spec = importlib.util.spec_from_file_location("client_discovery", str(cd_path))
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load client discovery from {cd_path}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[_CD_SINGLETON_NAME] = mod
        sys.modules["client_discovery"] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(_CD_SINGLETON_NAME, None)
            sys.modules.pop("client_discovery", None)
            raise
        return mod


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Mine Melee Refresh & Resource Gathering pipeline.")
    parser.add_argument("--pid", type=int, default=None, help="Target Survival.exe process PID (auto-detects if omitted)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run in non-destructive dry-run mode (default: True)")
    parser.add_argument("--live", action="store_true", help="Execute live recall/dispatch calls (disables dry-run)")
    parser.add_argument("--refresh-threshold-sec", type=int, default=300, help="Remaining gather seconds threshold for melee refresh")
    parser.add_argument("--min-payload-pct", type=float, default=10.0, help="Minimum payload percentage threshold")
    parser.add_argument("--reserve-formations", type=int, default=1, help="Number of free formations to keep in reserve")
    args = parser.parse_args()

    dry_run = not bool(args.live)
    cd = _load_client_discovery()
    target_pid = args.pid
    if not target_pid:
        running = cd.find_running_processes()
        if not running:
            print(json.dumps({"ok": False, "task": "mine_melee_refresh", "error": "no_running_client_found"}, indent=2))
            return 1
        running.sort(key=lambda p: (0 if str(p.get("role") or "").lower() == "main" else 1, int(p.get("pid") or 0)))
        target_pid = int(running[0]["pid"])

    res = action_mine_melee_refresh(
        cd,
        target_pid,
        dry_run=dry_run,
        refresh_threshold_sec=args.refresh_threshold_sec,
        min_payload_pct=args.min_payload_pct,
        reserve_formations=args.reserve_formations,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
