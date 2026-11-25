"""Modular per-client Last Z automation actions executed via Frida Lua bridge."""

from __future__ import annotations

import copy
import functools
import itertools
import json
import math
import os
import random
import re
import sys
import threading
import time
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

_BA_SINGLETON_NAME = "heinz_bot_actions_singleton"
if __name__ != "__main__":
    _self_mod = sys.modules.get(__name__)
    if _self_mod is not None:
        sys.modules.setdefault(_BA_SINGLETON_NAME, _self_mod)

_HEX_COLOR_TIP_RE = re.compile(r"^#?[0-9A-Fa-f]{6,8}(?:\s*\(#?[0-9A-Fa-f]{6,8}\))?$")


def _clean_in_game_tips(tips: Any) -> list[str]:
    """Filter out Unity RichText hex color strings (e.g. E000000) and deduplicate consecutive/repeated tips."""
    if not isinstance(tips, (list, tuple)):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in tips:
        s = str(item or "").strip()
        if not s:
            continue
        if _HEX_COLOR_TIP_RE.match(s) or s.upper() == "E000000":
            continue
        if s not in seen:
            seen.add(s)
            cleaned.append(s)
    return cleaned

_DATA_DIR = Path(os.environ["HEINZ_DATA_DIR"]) if os.environ.get("HEINZ_DATA_DIR", "").strip() else (Path(__file__).resolve().parent.parent / "data")
DAILY_STATE_PATH = _DATA_DIR / "daily_task_state.json"

_ENGLISH_DIALOG_CACHE: dict[str, str] | None = None


def _load_english_dialog() -> dict[str, str]:
    """Lazily load launcher/assets/english-dialog.txt as a Python localization fallback."""
    global _ENGLISH_DIALOG_CACHE
    if _ENGLISH_DIALOG_CACHE is not None:
        return _ENGLISH_DIALOG_CACHE
    here = Path(__file__).resolve()
    repo_root = here.parent.parent
    candidates = [
        repo_root / "launcher" / "assets" / "english-dialog.txt",
        repo_root / "assets" / "english-dialog.txt",
        repo_root / "_internal" / "assets" / "english-dialog.txt",
        repo_root.parent / "assets" / "english-dialog.txt",
    ]
    meipass = getattr(__import__("sys"), "_MEIPASS", None)
    if meipass:
        candidates.insert(0, Path(meipass) / "assets" / "english-dialog.txt")
        candidates.insert(1, Path(meipass) / "launcher" / "assets" / "english-dialog.txt")
    mapping: dict[str, str] = {}
    for cand in candidates:
        if cand.is_file():
            try:
                with cand.open("r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        if "=" in line:
                            k, v = line.split("=", 1)
                            ks = k.strip()
                            if ks:
                                mapping[ks] = v.strip()
                break
            except Exception:
                pass
    _ENGLISH_DIALOG_CACHE = mapping
    return mapping


def _localize_id(val: Any) -> str:
    """Resolve a numeric localization key via english-dialog.txt fallback."""
    raw = str(val or "").strip()
    if not raw:
        return ""
    if raw.isdigit():
        return _load_english_dialog().get(raw, raw)
    return raw

TASK_ORDER = (
    "auto_help",
    "rf_hq_under_attack",
    "war_safety",
    "hospital_heal",
    "mine_melee_refresh",
    "alliance_daily",
    "daily_tasks_complete",
    "daily_claims",
    "free_recruits",
    "research_queue",
    "vip_store_rewards",
    "hero_battlefield",
    "arena",
    "radar_events",
    "treasure_helicopter",
    "furylord",
    "full_preparedness",
    "speedups",
    "troop_training",
    "building_upgrades",
    "tyrant_event",
    "alliance_boss_mine",
    "garage_upgrades",
    "hero_progression",
    "bounties",
    "bounty_steal",
    "trucks",
    "mining_event",
    "boomer_runs",
    "auto_gather",
    "area_exploration",
)

ALL_TASKS = TASK_ORDER

RSS_RESOURCE_TYPE_IDS: dict[str, int] = {
    "Diamonds": 15,
    "Electricity": 12,
    "Zent": 14,
    "Wood": 2,
    "Food": 1,
}

RSS_RESOURCE_ID_TO_NAME: dict[int, str] = {
    1: "Food",
    2: "Wood",
    12: "Electricity",
    14: "Zent",
    15: "Diamonds",
}

RSS_DEFAULT_PRIORITY: tuple[str, ...] = (
    "Diamonds",
    "Electricity",
    "Zent",
    "Wood",
    "Food",
)

_RSS_RESOURCE_ALIASES: dict[str, str] = {
    # Diamonds (15 - aps_gather_resource: Diamond)
    "diamonds": "Diamonds",
    "diamond": "Diamonds",
    "gold": "Diamonds",
    "gem": "Diamonds",
    "gems": "Diamonds",
    "15": "Diamonds",
    # Electricity (12 - aps_gather_resource: Power Plant)
    "electricity": "Electricity",
    "power": "Electricity",
    "power plant": "Electricity",
    "power_plant": "Electricity",
    "powerplant": "Electricity",
    "elec": "Electricity",
    "12": "Electricity",
    # Zent (14 - aps_gather_resource: Zent Mine)
    "zent": "Zent",
    "zent mine": "Zent",
    "zent_mine": "Zent",
    "zentmine": "Zent",
    "money": "Zent",
    "cash": "Zent",
    "coin": "Zent",
    "coins": "Zent",
    "mine": "Zent",
    "14": "Zent",
    # Wood (2 - aps_gather_resource: Wood)
    "wood": "Wood",
    "lumber": "Wood",
    "lumberyard": "Wood",
    "timber": "Wood",
    "2": "Wood",
    # Food (1 - aps_gather_resource: Farmland)
    "food": "Food",
    "farmland": "Food",
    "farm": "Food",
    "metal": "Food",
    "oil": "Food",
    "steel": "Food",
    "iron": "Food",
    "1": "Food",
    "0": "Food",
}


def normalize_rss_resource_name(name: Any) -> str:
    """Normalize a resource name, legacy alias, or numeric resource_type ID to canonical gather name."""
    if name is None:
        return ""
    if isinstance(name, bool):
        return ""
    if isinstance(name, int):
        return RSS_RESOURCE_ID_TO_NAME.get(name, "Food" if name == 0 else "")
    raw = str(name).strip().lower()
    if not raw:
        return ""
    norm = re.sub(r"[\s\-]+", " ", raw)
    if norm in _RSS_RESOURCE_ALIASES:
        return _RSS_RESOURCE_ALIASES[norm]
    compact = norm.replace(" ", "_")
    if compact in _RSS_RESOURCE_ALIASES:
        return _RSS_RESOURCE_ALIASES[compact]
    return ""


def _resolve_rss_resource_list(
    resource_type: Any = "Diamonds",
    resource_types: list[Any] | tuple[Any, ...] | None = None,
) -> list[str]:
    """Resolve single resource name/ID or ordered priority list into deduplicated canonical names."""
    raw_items: list[Any] = []
    if resource_types is not None:
        if isinstance(resource_types, (list, tuple)):
            raw_items = list(resource_types)
        else:
            raw_items = [resource_types]
    elif isinstance(resource_type, (list, tuple)):
        raw_items = list(resource_type)
    elif isinstance(resource_type, str) and "," in resource_type:
        raw_items = [part.strip() for part in resource_type.split(",") if part.strip()]
    else:
        raw_items = [resource_type]

    resolved: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        cname = normalize_rss_resource_name(item)
        if cname and cname not in seen:
            seen.add(cname)
            resolved.append(cname)
    return resolved


RESOURCE_TYPE_NAMES = {
    1: "Food",
    2: "Wood",
    12: "Electricity",
    14: "Zent",
    15: "Diamonds",
}

BARRACKS_CONFIG = {
    "CarSoldier": {"queue_type": 1, "building_id": 423000},
    "FootSoldier": {"queue_type": 8, "building_id": 424000},
    "BowSoldier": {"queue_type": 9, "building_id": 425000},
}

SPEEDUP_MENU_MAP = {
    "build": {"menu": 7, "queue_type": "build", "name": "Build"},
    "research": {"menu": 6, "queue_type": 6, "name": "Research"},
    "train": {"menu": 3, "queue_type": "train", "name": "Train"},
    "heal": {"menu": 4, "queue_type": 3, "name": "Heal"},
}

LUA_JSON_HELPER = r"""
local function _esc(s)
  return '"' .. tostring(s):gsub('[%z\1-\31\\"\127]', function(c)
    return string.format('\\u%04x', c:byte())
  end) .. '"'
end
local function _is_valid_tip(s)
  if type(s) ~= 'string' then return false end
  local clean = s:match('^%s*(.-)%s*$')
  if clean == '' then return false end
  local bare = clean:gsub('^#', ''):gsub('%s*%b()$', '')
  if #bare >= 6 and #bare <= 8 and bare:match('^[0-9A-Fa-f]+$') then
    return false
  end
  return true
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
    if d > 5 then return '<depth>' end
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
    if d > 5 then return '"<depth>"' end
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
  local t = type(v)
  if d == 0 and t == 'table' and v.ok ~= nil then
    if type(_G.__hzPopupLog) == 'table' and #_G.__hzPopupLog > 0 then
      local poppedTips = {}
      local seenTips = {}
      local poppedModals = {}
      for i = 1, #_G.__hzPopupLog do
        local item = _G.__hzPopupLog[i]
        if type(item) == 'table' and item.type == 'modal_dialog' then
          table.insert(poppedModals, item)
        else
          local ts = tostring(item or '')
          if _is_valid_tip(ts) and not seenTips[ts] then
            seenTips[ts] = true
            table.insert(poppedTips, ts)
          end
        end
      end
      _G.__hzPopupLog = {}
      if v.in_game_tips == nil then
        v.in_game_tips = poppedTips
      end
      if v.modal_dialogs == nil and #poppedModals > 0 then
        v.modal_dialogs = poppedModals
      end
    end
    if type(_G.__hzSendErrors) == 'table' and #_G.__hzSendErrors > 0 then
      local merged = {}
      local seenE = {}
      if type(v.send_errors) == 'table' then
        for _, se in ipairs(v.send_errors) do
          local s = tostring(se or '')
          if s ~= '' and not seenE[s] then seenE[s] = true; table.insert(merged, s) end
        end
      end
      for _, se in ipairs(_G.__hzSendErrors) do
        local s = tostring(se or '')
        if s ~= '' and not seenE[s] then seenE[s] = true; table.insert(merged, s) end
      end
      _G.__hzSendErrors = {}
      if #merged > 0 then
        v.send_errors = merged
      end
    end
  end
  if d == 0 and t == 'table' and _rjson and type(_rjson.encode) == 'function' and next(v) ~= nil then
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

LUA_COMMON_HELPERS = LUA_JSON_HELPER + r"""
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

local function _safe_call(fn, default)
  local ok, res = pcall(fn)
  if ok and res ~= nil then return res end
  return default
end

local function _get_player_snapshot()
  local p = LuaEntry and LuaEntry.Player
  local dc = DataCenter
  local afm = dc and dc.ArmyFormationDataManager
  local bm = dc and dc.BuildManager
  local uid = (p and p.GetUid) and _safe_call(function() return p:GetUid() end, '') or ''
  local name = (p and p.GetName) and _safe_call(function() return p:GetName() end, '') or ''
  local srv = (p and p.GetCurServerId) and _safe_call(function() return p:GetCurServerId() end, 0) or 0
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
  local stamina = (p and p.GetCurStamina) and tonumber(_safe_call(function() return p:GetCurStamina() end, 0)) or 0
  local freeForm = (afm and afm.GetFreeFormationCount) and tonumber(_safe_call(function() return afm:GetFreeFormationCount() end, 0)) or 0
  local unlockForm = (afm and afm.GetUnlockFormationCount) and tonumber(_safe_call(function() return afm:GetUnlockFormationCount() end, 0)) or 0
  local chatReady = (ChatInterface ~= nil)
  local inAlliance = false
  local allyUid = ''
  local allyAbbr = ''
  if chatReady and p and p.IsInAlliance then
    inAlliance = _safe_call(function() return p:IsInAlliance() end, false)
  end
  if p and p.GetAllianceUid then
    allyUid = _safe_call(function() return p:GetAllianceUid() end, '')
  end
  if p and p.GetAllianceAbbr then
    allyAbbr = _safe_call(function() return p:GetAllianceAbbr() end, '')
  end
  local nowSec = 0
  if UITimeManager and UITimeManager.GetInstance then
    local tm = _safe_call(function() return UITimeManager:GetInstance() end, nil)
    if tm and tm.GetServerSeconds then nowSec = tonumber(_safe_call(function() return tm:GetServerSeconds() end, 0)) or 0 end
  end
  local inWorld = (SceneManager and SceneManager.IsInWorld) and (_safe_call(function() return SceneManager:IsInWorld() end, false) and true or false) or false
  local uidStr = tostring(uid or '')
  local isReady = (LuaEntry ~= nil and p ~= nil and dc ~= nil and SceneManager ~= nil and chatReady and afm ~= nil and bm ~= nil and uidStr ~= '' and uidStr ~= '0')
  return {
    uid = uidStr,
    name = tostring(name or ''),
    serverId = srv,
    homeServerId = homeSrv,
    mainPos = pos,
    stamina = stamina,
    freeFormations = freeForm,
    unlockFormations = unlockForm,
    inAlliance = inAlliance and true or false,
    allianceUid = tostring(allyUid or ''),
    allianceAbbr = tostring(allyAbbr or ''),
    hqLv = bm and tonumber(_safe_call(function() return bm.MainLv end, 0)) or 0,
    power = (p and p.GetPower) and tonumber(_safe_call(function() return p:GetPower() end, 0)) or 0,
    serverSec = nowSec,
    inWorld = inWorld,
    chatReady = chatReady,
    ready = isReady,
  }
end

local function _extract_dialog_info(arg1, arg2, arg3, arg4)
  local title = ''
  local content = ''
  if type(arg1) == 'table' then
    title = tostring(arg1.title or arg1.Title or arg1.header or '')
    content = tostring(arg1.content or arg1.Content or arg1.msg or arg1.message or arg1.text or arg1.info or '')
    if content == '' and arg1[1] then content = tostring(arg1[1]) end
  elseif type(arg1) == 'string' and type(arg4) == 'string' and arg4 ~= '' then
    content = tostring(arg1 or '')
    title = tostring(arg4 or '')
  elseif type(arg1) == 'string' and type(arg2) == 'string' and arg2 ~= '' then
    title = tostring(arg1 or '')
    content = tostring(arg2 or '')
  elseif type(arg1) == 'string' then
    content = tostring(arg1 or '')
    title = 'Notice'
  end
  if Localization and Localization.GetString then
    if title ~= '' then
      local okLt, st = pcall(function() return Localization:GetString(title) end)
      if okLt and type(st) == 'string' and st ~= '' and st ~= title then title = st end
    end
    if content ~= '' then
      local okLc, sc = pcall(function() return Localization:GetString(content) end)
      if okLc and type(sc) == 'string' and sc ~= '' and sc ~= content then content = sc end
    end
  end
  if title == '' then title = 'Notice' end
  return title, content
end

local function _resolve_loc_str(id)
  if id == nil then return '' end
  local raw = tostring(id)
  if Localization and Localization.GetString then
    local okL, s = pcall(function() return Localization:GetString(raw) end)
    if not okL or type(s) ~= 'string' or s == '' or s == raw then
      okL, s = pcall(function() return Localization:GetString(id) end)
    end
    if okL and type(s) == 'string' and s ~= '' and s ~= raw then
      return s .. ' (#' .. raw .. ')'
    end
  end
  return raw
end

local function _install_popup_logger()
  if _G.__hzPopupLog == nil then _G.__hzPopupLog = {} end
  if UIUtil then
    _G.__hzHookInstalled = true
    _G.__hzHookInstalledV2 = true
    _G.__hzHookInstalledV3 = true
    if type(UIUtil.ShowTipsId) == 'function' and UIUtil.ShowTipsId ~= _G.__hzWrapShowTipsIdMain then
      local orig = UIUtil.ShowTipsId
      _G.__hzOrigShowTipsIdMain = orig
      local wrap = function(id, ...)
        local txt = _resolve_loc_str(id)
        if _is_valid_tip(txt) and _G.__hzPopupLog[#_G.__hzPopupLog] ~= txt then
          table.insert(_G.__hzPopupLog, txt)
          while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        end
        return orig(id, ...)
      end
      _G.__hzWrapShowTipsIdMain = wrap
      UIUtil.ShowTipsId = wrap
    end
    if type(UIUtil.ShowTipsIdParams) == 'function' and UIUtil.ShowTipsIdParams ~= _G.__hzWrapShowTipsIdParamsMain then
      local orig = UIUtil.ShowTipsIdParams
      _G.__hzOrigShowTipsIdParamsMain = orig
      local wrap = function(id, ...)
        local txt = _resolve_loc_str(id)
        if _is_valid_tip(txt) and _G.__hzPopupLog[#_G.__hzPopupLog] ~= txt then
          table.insert(_G.__hzPopupLog, txt)
          while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        end
        return orig(id, ...)
      end
      _G.__hzWrapShowTipsIdParamsMain = wrap
      UIUtil.ShowTipsIdParams = wrap
    end
    if type(UIUtil.ShowTips) == 'function' and UIUtil.ShowTips ~= _G.__hzWrapShowTipsMain then
      local orig = UIUtil.ShowTips
      _G.__hzOrigShowTipsMain = orig
      local wrap = function(msg, ...)
        local txt = tostring(msg or '')
        if msg ~= nil and _is_valid_tip(txt) and _G.__hzPopupLog[#_G.__hzPopupLog] ~= txt then
          table.insert(_G.__hzPopupLog, txt)
          while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        end
        return orig(msg, ...)
      end
      _G.__hzWrapShowTipsMain = wrap
      UIUtil.ShowTips = wrap
    end
    if type(UIUtil.ShowMessage) == 'function' and UIUtil.ShowMessage ~= _G.__hzWrapShowMessageMain then
      local orig = UIUtil.ShowMessage
      _G.__hzOrigShowMessageMain = orig
      local wrap = function(tipText, btnNum, text1, text2, action1, action2, closeAction, titleText, ...)
        local t = (titleText ~= nil and tostring(titleText) ~= '') and tostring(titleText) or 'Tips'
        local c = tostring(tipText or '')
        table.insert(_G.__hzPopupLog, {
          type = 'modal_dialog',
          source = 'UIUtil.ShowMessage',
          title = t,
          content = c,
          timestamp = os.time(),
        })
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(tipText, btnNum, text1, text2, action1, action2, closeAction, titleText, ...)
      end
      _G.__hzWrapShowMessageMain = wrap
      UIUtil.ShowMessage = wrap
    end
    if type(UIUtil.ShowMessageBig) == 'function' and UIUtil.ShowMessageBig ~= _G.__hzWrapShowMessageBigMain then
      local orig = UIUtil.ShowMessageBig
      _G.__hzOrigShowMessageBigMain = orig
      local wrap = function(tipText, btnNum, text1, text2, action1, action2, closeAction, titleText, ...)
        local t = (titleText ~= nil and tostring(titleText) ~= '') and tostring(titleText) or 'Tips'
        local c = tostring(tipText or '')
        table.insert(_G.__hzPopupLog, {
          type = 'modal_dialog',
          source = 'UIUtil.ShowMessageBig',
          title = t,
          content = c,
          timestamp = os.time(),
        })
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(tipText, btnNum, text1, text2, action1, action2, closeAction, titleText, ...)
      end
      _G.__hzWrapShowMessageBigMain = wrap
      UIUtil.ShowMessageBig = wrap
    end
    if type(UIUtil.ShowModal) == 'function' and UIUtil.ShowModal ~= _G.__hzWrapShowModalMain then
      local orig = UIUtil.ShowModal
      _G.__hzOrigShowModalMain = orig
      local wrap = function(tipText, btnNum, text1, text2, action1, action2, closeAction, titleText, ...)
        local t = (titleText ~= nil and tostring(titleText) ~= '') and tostring(titleText) or 'Tips'
        local c = tostring(tipText or '')
        table.insert(_G.__hzPopupLog, {
          type = 'modal_dialog',
          source = 'UIUtil.ShowModal',
          title = t,
          content = c,
          timestamp = os.time(),
        })
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(tipText, btnNum, text1, text2, action1, action2, closeAction, titleText, ...)
      end
      _G.__hzWrapShowModalMain = wrap
      UIUtil.ShowModal = wrap
    end
    if type(UIUtil.ShowServerError) == 'function' and UIUtil.ShowServerError ~= _G.__hzWrapShowServerErrorMain then
      local orig = UIUtil.ShowServerError
      _G.__hzOrigShowServerErrorMain = orig
      local wrap = function(errorCode, ...)
        local txt = _resolve_loc_str(errorCode)
        table.insert(_G.__hzPopupLog, {
          type = 'modal_dialog',
          source = 'UIUtil.ShowServerError',
          title = 'ServerError',
          content = txt,
          errorCode = tostring(errorCode or ''),
          timestamp = os.time(),
        })
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(errorCode, ...)
      end
      _G.__hzWrapShowServerErrorMain = wrap
      UIUtil.ShowServerError = wrap
    end

    -- Hook ShowCommonDialog for modal dialog interception
    if type(UIUtil.ShowCommonDialog) == 'function' and UIUtil.ShowCommonDialog ~= _G.__hzWrapShowCommonDialogMain then
      _G.__hzCommonDialogHookInstalled = true
      local orig = UIUtil.ShowCommonDialog
      _G.__hzOrigShowCommonDialogMain = orig
      local wrap = function(arg1, arg2, arg3, arg4, ...)
        local t, c = _extract_dialog_info(arg1, arg2, arg3, arg4)
        local dlgEntry = {
          type = 'modal_dialog',
          title = t,
          content = c,
          timestamp = os.time(),
        }
        table.insert(_G.__hzPopupLog, dlgEntry)
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(arg1, arg2, arg3, arg4, ...)
      end
      _G.__hzWrapShowCommonDialogMain = wrap
      UIUtil.ShowCommonDialog = wrap
    end
  end

  -- Hook CommonDialog.Open and CommonDialog.Show
  if CommonDialog then
    if type(CommonDialog.Open) == 'function' and CommonDialog.Open ~= _G.__hzWrapCommonDialogOpen then
      _G.__hzCommonDialogOpenHookInstalled = true
      local orig = CommonDialog.Open
      _G.__hzOrigCommonDialogOpen = orig
      local wrap = function(a1, a2, ...)
        local t, c = _extract_dialog_info(a1, a2, nil, nil)
        table.insert(_G.__hzPopupLog, {
          type = 'modal_dialog',
          title = t,
          content = c,
          timestamp = os.time(),
        })
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(a1, a2, ...)
      end
      _G.__hzWrapCommonDialogOpen = wrap
      CommonDialog.Open = wrap
    end
    if type(CommonDialog.Show) == 'function' and CommonDialog.Show ~= _G.__hzWrapCommonDialogShow then
      _G.__hzCommonDialogShowHookInstalled = true
      local orig = CommonDialog.Show
      _G.__hzOrigCommonDialogShow = orig
      local wrap = function(a1, a2, ...)
        local t, c = _extract_dialog_info(a1, a2, nil, nil)
        table.insert(_G.__hzPopupLog, {
          type = 'modal_dialog',
          title = t,
          content = c,
          timestamp = os.time(),
        })
        while #_G.__hzPopupLog > 20 do table.remove(_G.__hzPopupLog, 1) end
        return orig(a1, a2, ...)
      end
      _G.__hzWrapCommonDialogShow = wrap
      CommonDialog.Show = wrap
    end
  end

  if Setting and Setting.SetPrivateInt then
    pcall(function() Setting.SetPrivateInt('UIShowHeroWarning', os.time() + 86400) end)
  end
end
pcall(_install_popup_logger)

local function _drain_popup_log()
  local list = {}
  local seen = {}
  if type(_G.__hzPopupLog) == 'table' then
    for i = 1, #_G.__hzPopupLog do
      local item = _G.__hzPopupLog[i]
      if type(item) == 'table' then
        table.insert(list, item)
      else
        local ts = tostring(item or '')
        if _is_valid_tip(ts) and not seen[ts] then
          seen[ts] = true
          table.insert(list, ts)
        end
      end
    end
    _G.__hzPopupLog = {}
  end
  return list
end

local function _dismiss_modal_dialogs()
  local dismissed = {}
  local mgr = UIManager and (type(UIManager.GetInstance) == 'function' and UIManager:GetInstance() or UIManager)
  if not mgr then return dismissed end

  local modalNames = {
    'CommonDialog',
    'UIGiftPackageRewardGet',
    'UIError',
    'UICommonReward',
    'UIRewardTips',
    'UIConfirmDialog',
    'UINoticeDialog',
  }

  for _, name in ipairs(modalNames) do
    local win = nil
    if mgr.GetWindow then
      pcall(function() win = mgr:GetWindow(name) end)
    end
    if not win and mgr.windows and type(mgr.windows) == 'table' then
      win = mgr.windows[name]
    end
    if win then
      local isOpen = true
      if win.View and win.View.activeSelf ~= nil then
        isOpen = win.View.activeSelf and true or false
      elseif win.activeSelf ~= nil then
        isOpen = win.activeSelf and true or false
      elseif win.IsOpen and type(win.IsOpen) == 'function' then
        local okO, resO = pcall(function() return win:IsOpen() end)
        if okO then isOpen = resO and true or false end
      end

      if isOpen then
        local handled = false
        if win.View then
          if win.View.OnBtnConfirmClick then
            pcall(function() win.View:OnBtnConfirmClick() end)
            handled = true
          elseif win.View.OnBtnCloseClick then
            pcall(function() win.View:OnBtnCloseClick() end)
            handled = true
          elseif win.View.OnBtnOkClick then
            pcall(function() win.View:OnBtnOkClick() end)
            handled = true
          elseif win.View.OnCloseBtn then
            pcall(function() win.View:OnCloseBtn() end)
            handled = true
          elseif win.View.OnClickClose then
            pcall(function() win.View:OnClickClose() end)
            handled = true
          end
        end
        if not handled and win.OnCloseBtn then
          pcall(function() win:OnCloseBtn() end)
          handled = true
        end
        if type(win.Close) == 'function' then
          pcall(function() win:Close() end)
          handled = true
        end
        if mgr.DestroyWindow then
          pcall(function() mgr:DestroyWindow(name) end)
          handled = true
        end
        if mgr.CloseWindow then
          pcall(function() mgr:CloseWindow(name) end)
          handled = true
        end
        if mgr.CloseUIView then
          pcall(function() mgr:CloseUIView(name) end)
          handled = true
        end
        if mgr.HideWindow then
          pcall(function() mgr:HideWindow(name) end)
          handled = true
        end
        table.insert(dismissed, name)
      end
    end
  end

  if mgr.windows and type(mgr.windows) == 'table' then
    for wName, wObj in pairs(mgr.windows) do
      if type(wName) == 'string' and type(wObj) == 'table' and wName ~= 'UINoticeTips' then
        -- Exclude UINoticeTips: it is the permanent floating toast overlay host, not a blocking modal dialog.
        if string.find(wName, 'CommonDialog') or string.find(wName, 'Dialog') or string.find(wName, 'Error') or string.find(wName, 'RewardGet') then
          local act = false
          if wObj.View and wObj.View.activeSelf ~= nil then
            act = wObj.View.activeSelf and true or false
          elseif wObj.activeSelf ~= nil then
            act = wObj.activeSelf and true or false
          end
          if act then
            local alreadyDismissed = false
            for _, dName in ipairs(dismissed) do
              if dName == wName then alreadyDismissed = true; break end
            end
            if not alreadyDismissed then
              if wObj.View and wObj.View.OnBtnCloseClick then
                pcall(function() wObj.View:OnBtnCloseClick() end)
              elseif wObj.View and wObj.View.OnBtnConfirmClick then
                pcall(function() wObj.View:OnBtnConfirmClick() end)
              end
              if type(wObj.Close) == 'function' then pcall(function() wObj:Close() end) end
              if mgr.DestroyWindow then pcall(function() mgr:DestroyWindow(wName) end) end
              if mgr.CloseWindow then pcall(function() mgr:CloseWindow(wName) end) end
              if mgr.CloseUIView then pcall(function() mgr:CloseUIView(wName) end) end
              if mgr.HideWindow then pcall(function() mgr:HideWindow(wName) end) end
              table.insert(dismissed, wName)
            end
          end
        end
      end
    end
  end

  return dismissed
end

local function _restock_formation(f)
  local afm = DataCenter and DataCenter.ArmyFormationDataManager
  if not afm or not f or not f.uuid then return false, 0 end
  local curSol = 1
  if afm.GetCurSoldierNum then
    local ok_s, cs = pcall(function() return afm:GetCurSoldierNum(f.uuid) end)
    if ok_s and cs ~= nil then curSol = tonumber(cs) or 0 end
  end
  if curSol > 0 then
    return true, curSol
  end
  local uKey = tostring(f.uuid)
  _G.__hzRestockTs = _G.__hzRestockTs or {}
  local nowTs = os.time()
  local lastTs = tonumber(_G.__hzRestockTs[uKey] or 0) or 0
  if lastTs > 0 and (nowTs - lastTs) < 180 then
    return false, 0
  end
  _G.__hzRestockTs[uKey] = nowTs
  _G.__hzSendErrors = _G.__hzSendErrors or {}
  if afm.AutoAddHero then
    local okH, errH = pcall(function() afm:AutoAddHero(f.uuid) end)
    if not okH then table.insert(_G.__hzSendErrors, 'AutoAddHero: ' .. tostring(errH)) end
  end
  if afm.AutoAddSoldier then
    local okS, errS = pcall(function() afm:AutoAddSoldier(f.uuid) end)
    if not okS then table.insert(_G.__hzSendErrors, 'AutoAddSoldier: ' .. tostring(errS)) end
  end
  if afm.GetCurSoldierNum then
    local ok_s1, cs1 = pcall(function() return afm:GetCurSoldierNum(f.uuid) end)
    if ok_s1 and cs1 ~= nil then curSol = tonumber(cs1) or 0 end
  end
  if curSol <= 0 and afm.RefreshFormationSoldier then
    local okR, errR = pcall(function() afm:RefreshFormationSoldier(f.uuid) end)
    if not okR then table.insert(_G.__hzSendErrors, 'RefreshFormationSoldier: ' .. tostring(errR)) end
  end
  if afm.SendFormToServer then
    -- ArmyFormationDataManager:SendFormToServer(self) takes nparams=1 (no uuid arg)
    local okF, errF = pcall(function() afm:SendFormToServer() end)
    if not okF then table.insert(_G.__hzSendErrors, 'SendFormToServer: ' .. tostring(errF)) end
  end
  if afm.GetCurSoldierNum then
    local ok_s2, cs2 = pcall(function() return afm:GetCurSoldierNum(f.uuid) end)
    if ok_s2 and cs2 ~= nil then curSol = tonumber(cs2) or 0 end
  end
  if curSol > 0 then
    _G.__hzRestockTs[uKey] = nil
    return true, curSol
  end
  return false, 0
end

local function _next_ready_formation(pool, startIdx, dryRun)
  local idx = tonumber(startIdx or 1) or 1
  if type(pool) ~= 'table' then return nil, idx end
  while idx <= #pool do
    local cand = pool[idx]
    idx = idx + 1
    if cand and cand.uuid then
      if dryRun then
        return cand, idx
      end
      local okSol = _restock_formation(cand)
      if okSol then
        return cand, idx
      end
    end
  end
  return nil, idx
end

local function _join_rally_headless(f, war, fallbackPt, serverId, dryRun)
  if not f or not f.uuid or type(war) ~= 'table' or not war.uuid then
    return false, 'invalid_rally_join_args', 0, 'none'
  end
  local targetPt = tonumber(war.targetPointId or war.targetPos or war.targetPoint or war.pointId or fallbackPt or 0) or 0
  if targetPt <= 0 then
    targetPt = tonumber(fallbackPt or 0) or 0
  end
  if dryRun then
    return true, nil, targetPt, 'dry_run'
  end
  local joinType = (MarchTargetType and MarchTargetType.JOIN_RALLY) or 6
  local srvId = tonumber(serverId or 0) or 0
  if MarchUtil and MarchUtil.SendCreateMarchMessage and targetPt > 0 and war.uuid then
    local okM, errM = pcall(function()
      MarchUtil.SendCreateMarchMessage(
        tonumber(f.uuid) or f.uuid,
        joinType,
        targetPt,
        war.uuid,
        0,
        true,
        true,
        srvId
      )
    end)
    if okM then
      return true, nil, targetPt, 'send_create_march'
    end
    return false, tostring(errM), targetPt, 'send_create_march'
  end
  local wm = DataCenter and DataCenter.AllianceWarDataManager
  if wm and wm.JoinRally then
    local okJ, errJ = pcall(function() wm:JoinRally(war.uuid) end)
    if okJ then
      return true, nil, targetPt, 'join_rally_fallback'
    end
    return false, tostring(errJ), targetPt, 'join_rally_fallback'
  end
  return false, 'MarchUtil.SendCreateMarchMessage unavailable', targetPt, 'unavailable'
end

local function _is_my_march_target(pnum, myTargetPts)
  local pt = tonumber(pnum or 0) or 0
  if pt <= 0 then return false end
  if type(myTargetPts) == 'table' and myTargetPts[pt] then
    return true
  end
  if MarchUtil and MarchUtil.CheckWorldPointHasMyTroop then
    local okChk, hasMine = pcall(function() return MarchUtil.CheckWorldPointHasMyTroop(pt) end)
    if okChk and hasMine then
      return true
    end
  end
  return false
end

local function _is_point_blacklisted(bl, pt, claimKey, warUuid)
  if type(bl) ~= 'table' then return false end
  if pt ~= nil then
    local n = tonumber(pt)
    if n and n > 0 and bl[tostring(n)] then return true end
    local s = tostring(pt)
    if s ~= '' and s ~= '0' and bl[s] then return true end
  end
  if claimKey ~= nil then
    local ck = tostring(claimKey)
    if ck ~= '' and bl[ck] then return true end
  end
  if warUuid ~= nil then
    local wu = tostring(warUuid)
    if wu ~= '' and wu ~= '0' and bl[wu] then return true end
  end
  return false
end

local function _pick_free_formations(reserveCount, excludeMap, allowMutate, includeEmpty)
  reserveCount = tonumber(reserveCount) or 0
  excludeMap = type(excludeMap) == 'table' and excludeMap or {}
  local wantEmpty = (includeEmpty == true)
  local afm = DataCenter and DataCenter.ArmyFormationDataManager
  if not afm or not afm.GetArmyFormationList then return {} end
  local inMarchSet = {}
  if afm.GetInMarchArmyFormationUuids then
    local im = afm:GetInMarchArmyFormationUuids()
    if type(im) == 'table' then
      for k, v in pairs(im) do
        inMarchSet[tostring(v)] = true
        inMarchSet[tostring(k)] = true
      end
    end
  end
  local restockTs = type(_G.__hzRestockTs) == 'table' and _G.__hzRestockTs or {}
  local nowTs = os.time()
  local list = afm:GetArmyFormationList() or {}
  local freeEntries = {}
  for _, f in ipairs(list) do
    if f and f.uuid then
      local uKey = tostring(f.uuid)
      local state = tonumber(f.state or 0)
      if state == 0 and not inMarchSet[uKey] and not excludeMap[uKey] then
        local curSol = 1
        if afm.GetCurSoldierNum then
          local ok_s, cs = pcall(function() return afm:GetCurSoldierNum(f.uuid) end)
          if ok_s and cs ~= nil then curSol = tonumber(cs) or 0 end
        end
        if curSol > 0 then
          table.insert(freeEntries, { form = f, idx = tonumber(f.index or 99) or 99, hasSol = true })
        elseif wantEmpty then
          local lastFail = tonumber(restockTs[uKey] or 0) or 0
          if lastFail == 0 or (nowTs - lastFail) >= 180 then
            table.insert(freeEntries, { form = f, idx = tonumber(f.index or 99) or 99, hasSol = false })
          end
        end
      end
    end
  end
  table.sort(freeEntries, function(a, b)
    if a.hasSol ~= b.hasSol then return a.hasSol end
    return a.idx < b.idx
  end)
  if #freeEntries <= reserveCount then
    return {}
  end
  local usable = {}
  for i = reserveCount + 1, #freeEntries do
    table.insert(usable, freeEntries[i].form)
  end
  return usable
end

local function _get_squad_occupancy(snap)
  local dc = DataCenter
  local afm = dc and dc.ArmyFormationDataManager
  local wmm = dc and dc.WorldMyMarchDataManager
  local totalF = tonumber(snap and snap.unlockFormations or 0) or 0
  local freeF = tonumber(snap and snap.freeFormations or 0) or 0
  if totalF <= 0 and afm and afm.GetArmyFormationList then
    local okL, lst = pcall(function() return afm:GetArmyFormationList() end)
    if okL and type(lst) == 'table' then
      local c = 0
      for _, f in ipairs(lst) do
        if type(f) == 'table' and f.uuid then c = c + 1 end
      end
      totalF = c
    end
  end
  local wmmCount = 0
  local hasWmm = false
  local myTargetPts = {}
  if wmm and wmm.GetAllMarches then
    local okM, mLst = pcall(function() return wmm:GetAllMarches() end)
    if okM and type(mLst) == 'table' then
      hasWmm = true
      for _, m in pairs(mLst) do
        if type(m) == 'table' then
          wmmCount = wmmCount + 1
          local p1 = tonumber(m.targetPos or 0) or 0
          local p2 = tonumber(m.endPos or 0) or 0
          local p3 = tonumber(m.targetPointId or 0) or 0
          local p4 = tonumber(m.pointId or 0) or 0
          local p5 = tonumber(m.finalTargetPos or 0) or 0
          if p1 > 0 then myTargetPts[p1] = true end
          if p2 > 0 then myTargetPts[p2] = true end
          if p3 > 0 then myTargetPts[p3] = true end
          if p4 > 0 then myTargetPts[p4] = true end
          if p5 > 0 then myTargetPts[p5] = true end
        end
      end
    end
  end
  local inMarchCount = 0
  if afm and afm.GetInMarchArmyFormationCount then
    local okI, ic = pcall(function() return afm:GetInMarchArmyFormationCount() end)
    if okI and ic ~= nil then inMarchCount = tonumber(ic) or 0 end
  elseif afm and afm.GetInMarchArmyFormationUuids then
    local okU, iu = pcall(function() return afm:GetInMarchArmyFormationUuids() end)
    if okU and type(iu) == 'table' then
      for _ in pairs(iu) do inMarchCount = inMarchCount + 1 end
    end
  end
  local diffActive = math.max(0, totalF - freeF)
  local activeM = math.max(diffActive, inMarchCount, hasWmm and wmmCount or 0)
  return {
    total_formations = totalF,
    free_formations = freeF,
    active_marches = activeM,
    wmm_marches = wmmCount,
    my_march_targets = myTargetPts,
  }
end
"""


def _used_formations_lua(context: dict[str, Any] | None, pid: int) -> str:
    used = []
    if context is not None:
        used = list(context.get("used_formations_by_pid", {}).get(pid, []))
    return "{" + ",".join(f"[{json.dumps(str(u))}]=true" for u in used if u) + "}"


def _blacklisted_points_lua(context: dict[str, Any] | None) -> str:
    """Serialize Hub-provided blacklisted_points (pointIds, warUuids, claimKeys) to a Lua lookup table."""
    raw = (context or {}).get("blacklisted_points")
    if isinstance(raw, dict):
        items = list(raw.keys())
    elif isinstance(raw, (list, tuple, set)):
        items = list(raw)
    else:
        items = []
    entries: list[str] = []
    seen: set[str] = set()
    for item in items:
        s = str(item or "").strip()
        if s and s not in ("0", "nil") and s not in seen:
            seen.add(s)
            entries.append(f"[{json.dumps(s)}]=true")
    return "{" + ",".join(entries) + "}"


def _record_used_formations(context: dict[str, Any] | None, pid: int, uuids: list[str]) -> None:
    if context is None or not uuids:
        return
    bucket = context.setdefault("used_formations_by_pid", {}).setdefault(pid, [])
    for u in uuids:
        su = str(u or "").strip()
        if su and su not in bucket:
            bucket.append(su)


def _normalize_eval_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize list/tip/modal/error collections across Lua eval results (handling rapidjson empty {} vs [])."""
    for list_key in (
        "detail_lines",
        "claimed_uuids",
        "dispatched",
        "dispatched_marches",
        "recalled_marches",
        "would_dispatch",
        "would_recall",
        "active_mining_marches",
        "formations_overview",
        "call_helps",
        "personal_arms_claimed",
        "vs_claimed_stages",
        "started",
        "marched",
        "reinforcements",
        "claimed",
        "claim_ready",
        "joined_rallies",
        "started_rallies",
        "joined_list",
    ):
        if list_key in payload:
            lv = payload.get(list_key)
            if not isinstance(lv, list):
                if isinstance(lv, tuple):
                    payload[list_key] = list(lv)
                elif isinstance(lv, dict):
                    payload[list_key] = list(lv.values()) if lv else []
                else:
                    payload[list_key] = []
    if "in_game_tips" in payload:
        payload["in_game_tips"] = _clean_in_game_tips(payload.get("in_game_tips"))
    if "tips" in payload:
        payload["tips"] = _clean_in_game_tips(payload.get("tips"))
    modals: list[Any] = []
    for key in ("popped_modals", "modal_dialogs"):
        val = payload.get(key)
        if isinstance(val, (list, tuple)):
            for m in val:
                if m not in modals:
                    modals.append(m)
    if modals or "popped_modals" in payload or "modal_dialogs" in payload:
        payload["popped_modals"] = modals
    errs: list[str] = []
    for key in ("send_errors", "errors"):
        val = payload.get(key)
        if isinstance(val, (list, tuple)):
            for e in val:
                se = str(e or "").strip()
                if se and se not in errs:
                    errs.append(se)
    if "errors" in payload and not isinstance(payload.get("errors"), list):
        payload["errors"] = list(errs)
    for key in ("send_err", "dispatch_error", "enter_err"):
        val = payload.get(key)
        se = str(val or "").strip()
        if se and se not in errs:
            errs.append(se)
    if errs or "send_errors" in payload:
        payload["send_errors"] = errs
    return payload


_VALID_STEP_STATUSES = frozenset({"dispatched", "waiting_for_squad", "searching", "physical_limit", "error"})


def _ensure_step_contract(
    res: dict[str, Any] | None,
    *,
    task_name: str = "",
    default_message: str = "",
) -> dict[str, Any]:
    """Enforce the standardized repeat-step return contract across RSS and Map Kill actions."""
    out: dict[str, Any] = dict(res) if isinstance(res, dict) else {"ok": False, "error": "empty_result"}
    if task_name and not out.get("task"):
        out["task"] = task_name

    ok = bool(out.get("ok", False))
    out["ok"] = ok

    dispatched_count = int(out.get("dispatched_count") or 0)
    if dispatched_count <= 0:
        disp = out.get("dispatched")
        if isinstance(disp, list):
            dispatched_count = len(disp)
        elif isinstance(disp, dict) and disp:
            dispatched_count = 1
    out["dispatched_count"] = max(0, dispatched_count)

    free_f = max(0, int(out.get("free_formations") or 0))
    usable_f = max(0, int(out.get("usable_formations") or 0))
    active_m = max(0, int(out.get("active_marches") or 0))
    total_f = max(0, int(out.get("total_formations") or 0))
    raw_stamina = out.get("stamina")
    if raw_stamina is None or isinstance(raw_stamina, bool):
        stamina: int | None = None
    else:
        try:
            stamina = max(0, int(raw_stamina))
        except (TypeError, ValueError):
            stamina = None

    out["free_formations"] = free_f
    out["usable_formations"] = usable_f
    out["active_marches"] = active_m
    out["total_formations"] = total_f
    out["stamina"] = stamina

    raw_status = str(out.get("status") or "").strip()
    if not ok:
        status = "physical_limit" if raw_status == "physical_limit" else "error"
    elif raw_status in _VALID_STEP_STATUSES:
        status = raw_status
    elif out["dispatched_count"] > 0:
        status = "dispatched"
    elif active_m > 0:
        status = "waiting_for_squad"
    else:
        status = "physical_limit"
    out["status"] = status

    if status in ("physical_limit", "error"):
        stop_reason = str(
            out.get("stop_reason")
            or out.get("reason")
            or out.get("error")
            or ("error" if status == "error" else "physical_limit")
        ).strip()
        out["stop_reason"] = stop_reason
    else:
        out["stop_reason"] = ""

    msg = str(
        out.get("message")
        or out.get("error")
        or out.get("reason")
        or out.get("stop_reason")
        or default_message
        or status
    ).strip()
    out["message"] = msg
    return out


def _build_detail_lines(task_name: str, res: dict[str, Any]) -> list[str]:
    """Build structured, in-depth telemetry detail_lines for any of the 30 bot actions."""
    if not isinstance(res, dict):
        return [f"Result: {res}"]

    lines: list[str] = []
    dry_tag = "[DRY-RUN] " if res.get("dry_run") else ""
    if not res.get("ok", True):
        lines.append(f"{dry_tag}FAILED: {res.get('error') or res.get('reason') or 'unknown error'}")

    if task_name == "auto_help":
        lines.append(
            f"{dry_tag}Ally Help: helped={res.get('ally_help_num', 0)} (sent={bool(res.get('helped_all'))}), "
            f"Chests Tab1={res.get('tab1_gifts_claimed', 0)}, Tab2={res.get('tab2_chests_claimed', 0)} "
            f"(total_gifts={res.get('gifts_claimed', 0)})"
        )
        calls = res.get("call_helps") or []
        if isinstance(calls, list) and calls:
            for ch in calls[:10]:
                if isinstance(ch, dict):
                    lines.append(
                        f"  • Call-Help {ch.get('kind', '?')} uuid={ch.get('uuid')} "
                        f"item={ch.get('itemId', ch.get('qType', ''))}"
                    )
        else:
            lines.append("  • Call-Help: 0 unhelped building/research/hospital queues")
    elif task_name == "rf_hq_under_attack":
        lines.append(
            f"{dry_tag}Defense Scan: shielded={bool(res.get('shielded'))}, "
            f"self_under_attack={bool(res.get('self_under_attack'))}, threats={len(res.get('threats') or [])}"
        )
        for th in (res.get("threats") or [])[:10]:
            if isinstance(th, dict):
                lines.append(
                    f"  • Threat src={th.get('source')} from=[{th.get('ownerAlliance', '')}] {th.get('ownerName', '')} "
                    f"pt={th.get('targetPoint')} eta={th.get('etaSec')}s isSelf={bool(th.get('isSelf'))}"
                )
        for rf in (res.get("reinforcements") or [])[:10]:
            if isinstance(rf, dict):
                lines.append(
                    f"  • Reinforced targetUid={rf.get('targetUid')} pt={rf.get('targetPoint')} "
                    f"formation={rf.get('formationUuid')}"
                )
        if res.get("shield_used"):
            lines.append(f"  • Activated shield: {res.get('shield_used')}")
        for al in (res.get("alerts") or []):
            lines.append(f"  ! ALERT: {al}")
    elif task_name == "war_safety":
        lines.append(
            f"{dry_tag}War Safety: action={res.get('action', 'safe')}, shielded={bool(res.get('shielded'))}, "
            f"war_fever={bool(res.get('war_fever_active'))}, threats={len(res.get('threats') or [])}"
        )
        for th in (res.get("threats") or [])[:10]:
            if isinstance(th, dict):
                lines.append(
                    f"  • Threat src={th.get('source')} pt={th.get('targetPoint')} eta={th.get('etaSec')}s "
                    f"hits_self={bool(th.get('hits_self'))} hits_gatherer={bool(th.get('hits_gatherer'))}"
                )
        if res.get("shield_used"):
            lines.append(f"  • Shield used: {res.get('shield_used')}")
        for rm in (res.get("recalled_marches") or []):
            lines.append(f"  • Recalled exposed gather march uuid={rm}")
    elif task_name == "hospital_heal":
        lines.append(
            f"{dry_tag}Hospital ({res.get('scene_view', '?')}, queue={res.get('queue_type', 3)}, "
            f"state={res.get('queue_state', 0)}): wounded={res.get('wounded_total', 0)} "
            f"(in_treatment={res.get('in_treatment_total', 0)}, untreated={res.get('untreated_total', 0)}, "
            f"rem={res.get('queue_remaining_sec', 0)}s, helped={res.get('is_helped', 0)})"
        )
        lines.append(
            f"  • Batches: chained={res.get('batches_chained', 0)}, queued_troops={res.get('total_queued_troops', res.get('queued_troops', 0))}, "
            f"collected={res.get('batches_collected', 0)}, cross_helps={res.get('cross_client_helps_triggered', 0)}, "
            f"speedup_sec={res.get('speedup_seconds_applied', 0)}"
        )
        for qa in (res.get("queued_armies") or [])[:8]:
            if isinstance(qa, dict):
                lines.append(
                    f"  • Army {qa.get('armyId')}: queued={qa.get('healNum')}/{qa.get('totalInjured')} "
                    f"({qa.get('unit_treat_sec')}s/troop, est={qa.get('est_sec')}s)"
                )
        for ch in (res.get("chain_history") or [])[:6]:
            if isinstance(ch, dict):
                lines.append(
                    f"  • Pass #{ch.get('pass')}: action={ch.get('action')} queued={ch.get('queued_troops')} "
                    f"verified={ch.get('cure_verified')} cross_helps={ch.get('cross_client_helps')}"
                )
    elif task_name == "mine_melee_refresh":
        lines.append(
            f"{dry_tag}Mine Melee Refresh: action={res.get('action')}, active={len(res.get('active_mining_marches') or [])}, "
            f"refreshed={res.get('refreshed_count', 0)}, dispatched={res.get('dispatched_count', 0)}"
        )
    elif task_name == "alliance_daily":
        lines.append(
            f"{dry_tag}Alliance Daily: action={res.get('action')}, "
            f"gifts={res.get('gifts_claimed', 0)} (T1={res.get('tab1_gifts_claimed', 0)}, T2={res.get('tab2_chests_claimed', 0)}), "
            f"red_packets={res.get('red_packets_claimed', 0)}, tasks={res.get('tasks_claimed', 0)}, "
            f"exploit_boxes={res.get('exploit_boxes_claimed', 0)}, tech_donated={res.get('tech_donated', 0)} (techId={res.get('tech_id', 0)})"
        )
    elif task_name == "daily_tasks_complete":
        lines.append(
            f"{dry_tag}Daily Tasks (One-Go): attempted={res.get('executed_count', 0)}, "
            f"score={res.get('score_before', 0)}->{res.get('score_after', 0)}/{res.get('max_score', 150)}, "
            f"chests={res.get('boxes_claimed', 0)}/{res.get('boxes_total', 5)}, "
            f"remaining_todo={len(res.get('remaining_todo') or [])}, skipped={len(res.get('skipped') or [])}"
        )
    elif task_name == "daily_claims":
        lines.append(
            f"{dry_tag}Daily Claims: tasks={res.get('daily_tasks_claimed', 0)}, "
            f"activity_chests={res.get('daily_boxes_claimed') or []}, "
            f"achievements={res.get('achievements_claimed', 0)}, "
            f"battle_passes={res.get('battle_passes_claimed') or []}, "
            f"season_passes={res.get('season_passes_claimed') or []}, "
            f"week_cards={res.get('week_cards_claimed', 0)}, "
            f"month_cards={res.get('month_cards_claimed', 0)}, "
            f"chapter_tasks={res.get('chapter_tasks_claimed', 0)}, "
            f"main_tasks={res.get('main_tasks_claimed', 0)}"
        )
        for pd in (res.get("passes_detail") or [])[:15]:
            if isinstance(pd, dict):
                lines.append(
                    f"  • Pass actId={pd.get('actId', pd.get('activityId', '?'))} ({pd.get('name', pd.get('manager', 'Pass'))}): "
                    f"claimed={pd.get('claimed', True)} red={pd.get('redCount', pd.get('claimable_tiers', 0))}"
                )
    elif task_name == "free_recruits":
        lines.append(
            f"{dry_tag}Free Recruits: hero_banners={res.get('hero_recruits') or []}, "
            f"small_people_free={bool(res.get('small_people_free'))}, "
            f"safe_chests_opened={res.get('chests_total_count', 0)}"
        )
        for ch in (res.get("chests_opened") or [])[:10]:
            if isinstance(ch, dict):
                lines.append(f"  • Opened item {ch.get('id')} x{ch.get('qty')}")
    elif task_name == "research_queue":
        lines.append(
            f"{dry_tag}Research Queue: action={res.get('action')}, checked={res.get('queues_checked', 0)}, "
            f"collected={res.get('collected', 0)}, help_req={res.get('help_requested', 0)}, "
            f"free_sped={res.get('free_sped', 0)}, started={len(res.get('started') or [])}"
        )
        for st in (res.get("started") or [])[:5]:
            if isinstance(st, dict):
                lines.append(f"  • Started scienceId={st.get('scienceId')} on buildUuid={st.get('buildUuid')}")
    elif task_name == "vip_store_rewards":
        lines.append(
            f"{dry_tag}VIP & Store (VIP Lv{res.get('vip_level', 0)}): "
            f"vip_points={bool(res.get('claimed_vip_points'))} (avail={bool(res.get('can_vip_points'))}), "
            f"vip_daily={bool(res.get('claimed_vip_daily'))} (avail={bool(res.get('can_vip_daily'))}), "
            f"store_items={res.get('claimed_store_items') or []}, "
            f"weekly_free={bool(res.get('claimed_weekly_free'))} (avail={bool(res.get('can_weekly_free'))})"
        )
        for cand in (res.get("store_free_candidates") or [])[:10]:
            if isinstance(cand, dict):
                lines.append(f"  • Store free good id={cand.get('id')} itemId={cand.get('itemId')} ({cand.get('boughtTimes')}/{cand.get('maxTimes')})")
        if res.get("verified_after"):
            lines.append(f"  • Post-claim verify: {res.get('verified_after')}")
    elif task_name == "hero_battlefield":
        lines.append(
            f"{dry_tag}Hero Battlefield: open={bool(res.get('event_open'))}, wins={res.get('total_wins', 0)}, "
            f"failures={res.get('total_failures', 0)}, quick_deploys={res.get('quick_deploys', 0)}, skips={res.get('skips_triggered', 0)}"
        )
        factions = res.get("factions") or {}
        if isinstance(factions, dict):
            for fk, fi in factions.items():
                if isinstance(fi, dict):
                    lines.append(
                        f"  • Faction {fk} ({fi.get('name', '?')}): unlocked={bool(fi.get('unlocked'))}, "
                        f"ch={fi.get('start_chapter', 0)}->{fi.get('end_chapter', fi.get('start_chapter', 0))}, "
                        f"lvl={fi.get('start_level', 0)}->{fi.get('end_level', fi.get('start_level', 0))}, "
                        f"wins={fi.get('wins', 0)}, quick={bool(fi.get('quick_fight_unlocked'))}, "
                        f"stopped={fi.get('stopped_reason') or 'done'}"
                    )
                    for b in (fi.get("battles") or [])[:6]:
                        if isinstance(b, dict):
                            lines.append(
                                f"    - Ch{b.get('chapter')} Lvl{b.get('level_idx')} (trig={b.get('trig_lvl_id')}): "
                                f"our={b.get('our_power')} vs enemy={b.get('enemy_power')}, won={bool(b.get('won'))}, "
                                f"skip={bool(b.get('skipped'))}, quick={bool(b.get('quick_deploy'))}"
                            )
    elif task_name == "arena":
        si = res.get("self_info") or {}
        lines.append(
            f"{dry_tag}Arena ({res.get('mode', '1v1')}, cross={bool(res.get('is_cross'))}): "
            f"free_rem={res.get('free_remaining', 0)}, refreshes={res.get('free_refreshes_used', 0)}, "
            f"fought={res.get('battles_fought', 0)}, rank={si.get('selfRank', 0)}, score={si.get('selfScore', 0)}, "
            f"stopped={res.get('stopped_reason') or res.get('reason') or 'done'}"
        )
        for b in (res.get("battles") or [])[:8]:
            if isinstance(b, dict):
                tgt = b.get("target") or {}
                if b.get("skipped_reason"):
                    bc = b.get("best_candidate") or {}
                    lines.append(
                        f"  • Skipped: {b.get('skipped_reason')} (best={bc.get('name', '?')} pwr={bc.get('power', 0)} odds={bc.get('win_odds_pct', 0)}%)"
                    )
                else:
                    lines.append(
                        f"  • vs {tgt.get('name', tgt.get('uid', '?'))} (pwr={tgt.get('power', 0)}, odds={b.get('win_odds_pct', 0)}%): "
                        f"camps={b.get('slot_camps')}, accepted={bool(b.get('accepted'))}, rank_after={b.get('rank_after', '?')}"
                    )
    elif task_name == "radar_events":
        lines.append(
            f"{dry_tag}Radar Events: scan_triggered={res.get('scan_triggered', 0)} (scans_rem={res.get('scans_remaining', 0)}), "
            f"total_events={res.get('total_events', 0)}, claimed={len(res.get('claimed_uuids') or [])}, dispatched={len(res.get('dispatched') or [])}"
        )
        for evd in (res.get("events_detail") or [])[:25]:
            if isinstance(evd, dict):
                lines.append(
                    f"  • Pin uuid={evd.get('uuid')} eventId={evd.get('eventId')} type={evd.get('category', evd.get('evType'))} "
                    f"pt={evd.get('pointId', 0)} state={evd.get('state')} -> {evd.get('action_taken', 'none')}"
                )
        if not res.get("events_detail"):
            for d in (res.get("dispatched") or [])[:15]:
                if isinstance(d, dict):
                    lines.append(f"  • Dispatched uuid={d.get('uuid')} eventId={d.get('eventId', '')} mode={d.get('mode')} cost={d.get('cost', 0)} form={d.get('formation', '')}")
    elif task_name == "treasure_helicopter":
        lines.append(
            f"{dry_tag}Treasure Helicopter: detected={len(res.get('detected') or [])}, "
            f"marched={len(res.get('marched') or [])}, claim_ready={len(res.get('claim_ready') or [])}, "
            f"claims_executed={len(res.get('claims_executed') or [])}, detail_req={len(res.get('detail_requested') or [])}"
        )
        for dt in (res.get("detected") or [])[:8]:
            if isinstance(dt, dict):
                lines.append(f"  • Treasure src={dt.get('source')} uuid={dt.get('uuid')} pt={dt.get('pointId')} state={dt.get('state')} rem={dt.get('remainSec')}s")
        for cl in (res.get("claims_executed") or [])[:8]:
            if isinstance(cl, dict):
                lines.append(f"  • Claimed uuid={cl.get('uuid')} pt={cl.get('pointId')} clicks={cl.get('burst_clicks')}")
    elif task_name == "furylord":
        lines.append(
            f"{dry_tag}Furylord: status={res.get('status', 'ok')}, in_window={bool(res.get('in_window'))}, open={bool(res.get('is_open'))}, "
            f"used_today={res.get('used_today', 0)}/{res.get('max_attacks', 4)}, bosses={res.get('boss_count', 0)}, "
            f"dispatched={res.get('dispatched_count', 0)}, claimed_rewards={bool(res.get('claimed_rewards'))}, "
            f"reason={res.get('stop_reason') or res.get('reason') or 'ok'}"
        )
        disp_fl = res.get("dispatched")
        if isinstance(disp_fl, dict):
            lines.append(f"  • Dispatched F{disp_fl.get('formationIndex')} -> pt={disp_fl.get('pointId')} rally={bool(disp_fl.get('rally'))}")
        elif isinstance(disp_fl, list):
            for d in disp_fl[:6]:
                if isinstance(d, dict):
                    lines.append(f"  • Dispatched {d.get('mode', 'march')} F{d.get('formationIndex')} -> pt={d.get('pointId')} rally={bool(d.get('rally'))}")
    elif task_name == "full_preparedness":
        ap = res.get("active_phase") or {}
        lines.append(
            f"{dry_tag}Full Preparedness: theme='{ap.get('theme') or '?'}' (actId={ap.get('act_id', 0)}, "
            f"vs_open={bool(ap.get('vs_open'))}, vs_day={ap.get('vs_day', 0)}), checked={res.get('personal_arms_checked', 0)}"
        )
        for pa in (res.get("personal_arms_claimed") or []):
            if isinstance(pa, dict):
                lines.append(f"  • Claimed slot={pa.get('slot')} actId={pa.get('actId')} score={pa.get('curScore')} stages={pa.get('stages')}")
        for tag, sub in (res.get("executed_actions") or {}).items():
            if isinstance(sub, dict):
                lines.append(f"  • Sub-action {tag}: ok={bool(sub.get('ok'))} action={sub.get('action') or sub.get('reason') or 'done'}")
    elif task_name == "speedups":
        theme_part = f", theme='{res.get('active_theme')}'" if res.get("active_theme") else ""
        lines.append(
            f"{dry_tag}Speedups: arms_ready={bool(res.get('arms_ready'))}, action={res.get('action', 'checked')}{theme_part}, "
            f"fp_score={res.get('fp_cur_score', 0)}/{res.get('fp_last_chest', 0)}, "
            f"vs_score={res.get('vs_cur_score', 0)}/{res.get('vs_last_chest', 0)}, "
            f"collected={len(res.get('finished_collected') or [])}, free={len(res.get('free_speeds') or [])}, items={len(res.get('item_speeds') or [])}"
        )
        for sp in (res.get("item_speeds") or [])[:8]:
            if isinstance(sp, dict):
                lines.append(f"  • Applied {sp.get('kind')} uuid={sp.get('uuid')} items={sp.get('itemIDs')} (x{sp.get('count')})")
    elif task_name == "troop_training":
        lines.append(
            f"{dry_tag}Troop Training: collected={len(res.get('collected') or [])}, "
            f"trained={len(res.get('trained') or [])}, busy={len(res.get('busy') or [])}"
        )
        for c in (res.get("collected") or []):
            if isinstance(c, dict):
                lines.append(f"  • Collected {c.get('barrack')} (qType={c.get('qType')})")
        for t in (res.get("trained") or []):
            if isinstance(t, dict):
                lines.append(f"  • Trained {t.get('barrack')}: armyId={t.get('armyId')} x{t.get('count')}")
        for b in (res.get("busy") or []):
            if isinstance(b, dict):
                lines.append(f"  • Busy {b.get('barrack')}: state={b.get('state')} endTime={b.get('endTime')}")
    elif task_name == "building_upgrades":
        lines.append(
            f"{dry_tag}Building Upgrades: res_collected={bool(res.get('resources_collected'))}, "
            f"free_queues={res.get('free_queues', 0)}, action={res.get('action') or res.get('reason') or 'none'}"
        )
        if isinstance(res.get("upgraded"), dict):
            u = res["upgraded"]
            lines.append(
                f"  • Upgraded itemId={u.get('itemId')} uuid={u.get('uuid')} Lv{u.get('level')}->Lv{u.get('targetLevel')} "
                f"(verified={res.get('verified')})"
            )
    elif task_name == "tyrant_event":
        lines.append(
            f"{dry_tag}Tyrant Event: open={bool(res.get('is_open'))}, in_battle={bool(res.get('in_battle'))}, "
            f"actId={res.get('actId')}, bossPt={res.get('bossPointId', 0)}, "
            f"free_claimed={bool(res.get('free_reward_claimed'))}, ally_claimed={bool(res.get('alliance_reward_claimed'))}"
        )
        if isinstance(res.get("hosted"), dict):
            h = res["hosted"]
            lines.append(f"  • Hosted F{h.get('formationIndex')} rally on pt={h.get('pointId')}")
        for j in (res.get("joined") or []):
            if isinstance(j, dict):
                lines.append(f"  • Joined war={j.get('warUuid')} with F{j.get('formationIndex', '?')}")
    elif task_name == "alliance_boss_mine":
        lines.append(
            f"{dry_tag}Bear & Alliance Mine: bear_open={bool(res.get('bear_open'))}, bear_in_battle={bool(res.get('bear_in_battle'))}, "
            f"bear_reward={bool(res.get('bear_reward_claimed'))}, bear_marched={bool(res.get('bear_marched'))}, "
            f"mine_center={bool(res.get('mine_has_center'))}, mine_march={bool(res.get('mine_has_march'))}, "
            f"mine_dispatched={bool(res.get('mine_dispatched'))}"
        )
    elif task_name == "garage_upgrades":
        lines.append(
            f"{dry_tag}Mod Vehicle Upgrades ({res.get('server_day_name', '?')}, only_mon={bool(res.get('only_monday'))}, "
            f"mode={res.get('refit_mode', 'free_only')}, free={res.get('free_count', 0)}, src={res.get('refit_source', 'none')}): "
            f"action={res.get('action')}, installed_all={bool(res.get('installed_all'))}, "
            f"merged_slots={res.get('merged_slots') or []}, refit_steps={res.get('refit_steps', 0)}"
        )
    elif task_name == "hero_progression":
        lv_ups = res.get("level_ups") or []
        brks = res.get("breakthroughs") or []
        stars = res.get("star_ups") or []
        skills = res.get("skill_ups") or []
        g_inst = res.get("gear_installed") or []
        g_up = res.get("gear_upgraded") or []
        g_pr = res.get("gear_promoted") or []
        sp_up = res.get("sp_upgraded") or []
        lines.append(
            f"{dry_tag}Hero Progression ({res.get('server_day_name', '?')}, scope={res.get('target_scope', 'formation_1')}, "
            f"only_hero_day={bool(res.get('only_hero_day', True))}, event_active={bool(res.get('event_active', False))}): "
            f"action={res.get('action')}, total={res.get('total_actions', 0)} "
            f"(lv={len(lv_ups)}, break={len(brks)}, star={len(stars)}, skill={len(skills)}, "
            f"equip={len(g_inst)}, gear_up={len(g_up)}, promote={len(g_pr)}, sp={len(sp_up)})"
        )
        for item in lv_ups[:8]:
            if isinstance(item, dict):
                lines.append(f"  • Level Up {item.get('heroName', item.get('heroId'))}: Lv{item.get('fromLv', '?')} (+{item.get('count', 1)}x item #{item.get('itemId')})")
        for item in brks[:5]:
            if isinstance(item, dict):
                lines.append(f"  • Breakthrough {item.get('heroName', item.get('heroId'))}: Lv{item.get('level', '?')}")
        for item in stars[:8]:
            if isinstance(item, dict):
                lines.append(f"  • Star/Rank Up {item.get('heroName', item.get('heroId'))}: star={item.get('star', '?')} (uni_used={item.get('universalUsed', 0)})")
        for item in skills[:8]:
            if isinstance(item, dict):
                lines.append(f"  • Skill Up {item.get('heroName', item.get('heroId'))}: S{item.get('skillIndex', '?')} Lv{item.get('fromLv', '?')}->{(int(item.get('fromLv') or 0) + 1)}")
        for item in g_inst[:6]:
            if isinstance(item, dict):
                lines.append(f"  • Auto-Equip {item.get('heroName', item.get('heroId'))}: {len(item.get('equipUuids') or [])} piece(s)")
        for item in g_up[:8]:
            if isinstance(item, dict):
                lines.append(f"  • Gear Enhance {item.get('heroName', item.get('heroId'))} slot {item.get('slot', '?')}: Lv{item.get('fromLv', '?')} (alloy={item.get('alloyUsed', 0)})")
        for item in g_pr[:6]:
            if isinstance(item, dict):
                lines.append(f"  • Gear Promote {item.get('heroName', item.get('heroId'))} slot {item.get('slot', '?')}: rank={item.get('promoteLevel', '?')}")
        for item in sp_up[:6]:
            if isinstance(item, dict):
                lines.append(f"  • Exclusive Weapon {item.get('heroName', item.get('heroId'))}: Lv{item.get('fromLv', '?')} (uni_used={item.get('universalUsed', 0)})")
    elif task_name == "bounties":
        helped_list = res.get("ally_helped") or res.get("allies_assisted") or []
        lines.append(
            f"{dry_tag}Gold Bounties (3-in-1): open={bool(res.get('is_open'))}, lock_orange={bool(res.get('lock_orange', True))}, "
            f"claimed_all={bool(res.get('claimed_all'))}, refreshed={len(res.get('refreshed') or [])}x, "
            f"dispatched={len(res.get('dispatched') or [])}, ally_helped={len(helped_list)}, "
            f"plundered={len(res.get('stolen') or [])}, skipped_non_gold={res.get('skipped_non_golden', 0)}, "
            f"stopped={res.get('stopped_reason') or 'done'}"
        )
        for r in (res.get("refreshed") or [])[:10]:
            if isinstance(r, dict):
                lines.append(f"  • Refreshed mode={r.get('mode')} lock={r.get('lockOrange', r.get('lock', True))} freeLeft={r.get('freeLeft', '?')} tickets={r.get('tickets', '?')}")
        for d in (res.get("dispatched") or [])[:10]:
            if isinstance(d, dict):
                lines.append(f"  • Dispatched bounty uuid={d.get('uuid')} color={d.get('color')} dur={d.get('marchDuration')}ms")
        for ah in helped_list[:10]:
            if isinstance(ah, dict):
                lines.append(f"  • Helped Ally Gold uuid={ah.get('uuid')} owner={ah.get('ownerName', ah.get('ally', ah.get('ownerUid', '?')))} color={ah.get('color')}")
        for st in (res.get("stolen") or [])[:10]:
            if isinstance(st, dict):
                lines.append(f"  • Plundered Bounty uuid={st.get('uuid')} srv={st.get('serverId')} Lv{st.get('level')} color={st.get('color')}")
    elif task_name == "bounty_steal":
        lines.append(
            f"{dry_tag}Bounty Steal: steals={res.get('today_steals', 0)}/{res.get('max_steals', 5)}, "
            f"servers={res.get('matched_servers') or []}, scanned={res.get('scanned_points', 0)}, "
            f"candidates={len(res.get('candidates') or [])}, stolen={len(res.get('stolen') or [])}, "
            f"skipped_same_state={res.get('skipped_same_state', 0)}, skipped_low_tier={res.get('skipped_low_tier', 0)}"
        )
        for st in (res.get("stolen") or [])[:10]:
            if isinstance(st, dict):
                lines.append(f"  • Stolen uuid={st.get('uuid')} srv={st.get('serverId')} pt={st.get('pointId')} Lv{st.get('level')} color={st.get('color')}")
    elif task_name == "trucks":
        lines.append(
            f"{dry_tag}Trade Trucks (srv={res.get('self_server')}, F1={res.get('f1_power', 0):,}): "
            f"departures={res.get('departure_count', 0)}, rob_count={res.get('rob_count', 0)}, "
            f"claimed={res.get('claimed', 0)}, rerolled={len(res.get('rerolled') or [])}, "
            f"sent={len(res.get('sent') or [])}, raided={len(res.get('attacked') or [])}"
        )
        for rr in (res.get("rerolled") or [])[:12]:
            if isinstance(rr, dict):
                lines.append(f"  • Rerolled truck uuid={rr.get('uuid')} mode={rr.get('mode')} q={rr.get('from_quality')}->{rr.get('to_quality', rr.get('target_quality', '?'))}")
        for s in (res.get("sent") or [])[:6]:
            if isinstance(s, dict):
                lines.append(f"  • Dispatched slot#{s.get('slot')} truck uuid={s.get('uuid')} Q{s.get('quality')}/targetQ{s.get('target_quality')} F{s.get('formation')}")
        for atk in (res.get("attacked") or [])[:6]:
            if isinstance(atk, dict):
                lines.append(f"  • Raided enemy truck uuid={atk.get('uuid')} srv={atk.get('serverId')} pwr={atk.get('targetPower', 0):,} (margin={atk.get('margin', 0):,})")
    elif task_name == "mining_event":
        lines.append(
            f"{dry_tag}Mining Event: open={bool(res.get('event_open'))}, scheduled_day={bool(res.get('is_scheduled_day'))}, "
            f"fights={res.get('fight_num', 0)}, claimed={len(res.get('claimed') or [])}, "
            f"refreshes={res.get('refreshes_performed', 0)}, active={len(res.get('active_mines') or [])}, "
            f"skipped_wrong={res.get('skipped_wrong_type_or_level', 0)}, skipped_players={res.get('skipped_occupied_players', 0)}, "
            f"reason={res.get('reason') or res.get('status') or 'ok'}"
        )
        if isinstance(res.get("attacked"), dict):
            a = res["attacked"]
            lines.append(f"  • Attacked Mine #{a.get('mineIndex')} (id={a.get('mineId')}, Lv{a.get('level')}) with F{a.get('formationIndex')}")
    elif task_name == "boomer_runs":
        lines.append(
            f"{dry_tag}Boomer Runs: status={res.get('status', 'ok')}, stamina={res.get('stamina', 0)}, open_rallies={res.get('open_rallies', 0)}, "
            f"dispatched={res.get('dispatched_count', 0)}, joined={bool(res.get('joined'))}, started_rally={bool(res.get('started_rally'))}, "
            f"reason={res.get('stop_reason') or res.get('reason') or 'ok'}"
        )
        if isinstance(res.get("joined"), dict):
            lines.append(f"  • Joined war={res['joined'].get('warUuid')} pt={res['joined'].get('targetPoint')}")
        if isinstance(res.get("started_rally"), dict):
            sr = res["started_rally"]
            lines.append(f"  • Started Lv{sr.get('level')} boomer rally pt={sr.get('pointId')} dist={sr.get('dist')} form={sr.get('formationUuid')}")
    elif task_name == "auto_gather":
        lines.append(
            f"{dry_tag}Auto Gather: status={res.get('status', 'ok')}, free_forms={res.get('free_formations', 0)}, usable={res.get('usable_formations', 0)}, "
            f"candidates={res.get('candidates_found', 0)}, dispatched={len(res.get('dispatched') or [])}, "
            f"reason={res.get('stop_reason') or res.get('reason') or res.get('action') or 'ok'}"
        )
        for d in (res.get("dispatched") or [])[:6]:
            if isinstance(d, dict):
                lines.append(f"  • Sent {d.get('formationUuid')} -> {d.get('resourceType')} Lv{d.get('level')} pt={d.get('pointId')} dist={d.get('dist')}")
    elif task_name == "rss_gather":
        lines.append(
            f"{dry_tag}RSS Gather ({','.join(res.get('resource_types') or []) or '?'}): status={res.get('status', 'ok')}, "
            f"squads={res.get('active_marches', 0)}/{res.get('total_formations', 0)} active (usable={res.get('usable_formations', 0)}), "
            f"dispatched={res.get('dispatched_count', 0)}, candidates={res.get('candidates_found', 0)}"
            + (f", stop_reason={res.get('stop_reason')}" if res.get("stop_reason") else "")
        )
        for d in (res.get("dispatched") or [])[:6]:
            if isinstance(d, dict):
                lines.append(f"  • Sent F{d.get('formationIndex', '?')} ({d.get('formationUuid')}) -> {d.get('resourceType')} Lv{d.get('level')} pt={d.get('pointId')} dist={d.get('dist')}")
    elif task_name == "standalone_npc":
        lines.append(
            f"{dry_tag}Standalone NPC: status={res.get('status', 'ok')}, stamina={res.get('stamina', 0)}, "
            f"lv={res.get('effective_min_level', 0)}..{res.get('effective_max_level', 0)} (unlocked={res.get('unlocked_max_level', 0)}), "
            f"dispatched={res.get('dispatched_count', 0)}, candidates={res.get('candidates_found', 0)}"
            + (f", stop_reason={res.get('stop_reason')}" if res.get("stop_reason") else "")
        )
        for d in (res.get("dispatched") or [])[:6]:
            if isinstance(d, dict):
                lines.append(f"  • Attacked Lv{d.get('level')} NPC (id={d.get('monsterId')}) pt={d.get('pointId')} dist={d.get('dist')} with F{d.get('formationIndex', '?')}")
    elif task_name == "saga_boss":
        lines.append(
            f"{dry_tag}Survival Saga: status={res.get('status', 'ok')}, detected={bool(res.get('detected'))}, active={bool(res.get('active'))}, "
            f"act_id={res.get('act_id', 0)}, bosses={res.get('boss_count', 0)}, open_rallies={res.get('open_rallies', 0)}, "
            f"dispatched={res.get('dispatched_count', 0)}, summoned={bool(res.get('summoned'))}"
            + (f", stop_reason={res.get('stop_reason')}" if res.get("stop_reason") else "")
        )
        for d in (res.get("dispatched") or [])[:6]:
            if isinstance(d, dict):
                lines.append(f"  • {d.get('mode', 'march')} pt={d.get('pointId')} Lv{d.get('level', '?')} with F{d.get('formationIndex', '?')}")
    elif task_name == "area_exploration":
        start_ord = int(res.get("start_order", res.get("order", 0)) or 0)
        end_ord = int(
            res.get(
                "end_order",
                res.get(
                    "order_after_battles",
                    res.get("order_after_jump", res.get("order", start_ord)),
                ),
            )
            or start_ord
        )
        lines.append(
            f"{dry_tag}Regional Exploration: stage={start_ord}->{end_ord}, "
            f"team_pwr={res.get('team_power', 0):,} vs monster_pwr={res.get('monster_power', 0):,}, "
            f"hangup_claimed={bool(res.get('hangup_claimed'))}, jumped={bool(res.get('jumped'))}, "
            f"wins={res.get('wins', 0)}/{len(res.get('battles') or [])}, skips={res.get('skips_triggered', 0)}, "
            f"stopped={res.get('stopped_reason') or 'done'}"
        )
        for b in (res.get("battles") or [])[:10]:
            if isinstance(b, dict):
                lines.append(
                    f"  • Stage {b.get('stage')} (id={b.get('level_id')}): outcome={b.get('outcome')}, "
                    f"skip={bool(b.get('skipped'))}, order_after={b.get('order_after')}"
                )
    elif task_name == "dismiss_popups":
        wins = res.get("dismissed_windows") or []
        lines.append(f"{dry_tag}Popups: dismissed={res.get('dismissed_count', 0)} windows={wins}")
    else:
        kv = [f"{k}={v}" for k, v in res.items() if k not in ("ok", "task", "dry_run", "detail_lines", "in_game_tips", "tips", "popped_modals", "modal_dialogs", "send_errors") and not isinstance(v, (dict, list))]
        lines.append(f"{dry_tag}{task_name}: " + (", ".join(kv[:8]) if kv else "completed"))

    if res.get("message") and not any(str(res["message"]) in ln for ln in lines):
        lines.append(f"Message: {res.get('message')}")
    tips = _clean_in_game_tips(res.get("in_game_tips") or res.get("tips") or [])
    for tip in tips[:5]:
        lines.append(f"In-game tip: {tip}")
    for err in (res.get("send_errors") or [])[:5]:
        lines.append(f"RPC/Send error: {err}")
    return lines


def _finalize_task_result(task_name: str, res: Any) -> dict[str, Any]:
    """Ensure every task result includes normalized tips, popped_modals, send_errors, and detail_lines."""
    if not isinstance(res, dict):
        res = {"ok": True, "task": task_name, "result": res}
    res.setdefault("task", task_name)
    _normalize_eval_payload(res)
    res.setdefault("popped_modals", [])
    res.setdefault("send_errors", [])
    existing = res.get("detail_lines")
    if not isinstance(existing, list) or len(existing) == 0:
        res["detail_lines"] = _build_detail_lines(task_name, res)
    else:
        res["detail_lines"] = [str(x) for x in existing if str(x or "").strip()]
        if not res["detail_lines"]:
            res["detail_lines"] = _build_detail_lines(task_name, res)
    if not res.get("message") and res["detail_lines"]:
        res["message"] = res["detail_lines"][0]
    return res


def _with_task_telemetry(task_name: str) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]:
    """Decorator guaranteeing structured detail_lines, popped_modals, and send_errors on any task return."""
    def _decorator(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        @functools.wraps(fn)
        def _wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            res = fn(*args, **kwargs)
            return _finalize_task_result(task_name, res)
        return _wrapper
    return _decorator


_HZ_COMMON_VERSION = 5

_LUA_COMMON_BOOTSTRAP = LUA_COMMON_HELPERS + f"""
_G.__hzCommonVer = {_HZ_COMMON_VERSION}
_G.__hzBridge = {{
  esc = _esc,
  is_valid_tip = _is_valid_tip,
  enc = _enc,
  jdict = _jdict,
  jarr = _jarr,
  to_xy = _to_xy,
  dist = _dist,
  safe_call = _safe_call,
  get_player_snapshot = _get_player_snapshot,
  extract_dialog_info = _extract_dialog_info,
  resolve_loc_str = _resolve_loc_str,
  install_popup_logger = _install_popup_logger,
  drain_popup_log = _drain_popup_log,
  dismiss_modal_dialogs = _dismiss_modal_dialogs,
  restock_formation = _restock_formation,
  next_ready_formation = _next_ready_formation,
  join_rally_headless = _join_rally_headless,
  is_my_march_target = _is_my_march_target,
  is_point_blacklisted = _is_point_blacklisted,
  pick_free_formations = _pick_free_formations,
  get_squad_occupancy = _get_squad_occupancy,
}}
"""

_LUA_COMMON_SHIM = f"""local _hzB = _G.__hzBridge
if _G.__hzCommonVer ~= {_HZ_COMMON_VERSION} or type(_hzB) ~= 'table' then
  return '__HZ_NEED_BOOTSTRAP__'
end
local _esc = _hzB.esc
local _is_valid_tip = _hzB.is_valid_tip
local _enc = _hzB.enc
local _jdict = _hzB.jdict
local _jarr = _hzB.jarr
local _to_xy = _hzB.to_xy
local _dist = _hzB.dist
local _safe_call = _hzB.safe_call
local _get_player_snapshot = _hzB.get_player_snapshot
local _extract_dialog_info = _hzB.extract_dialog_info
local _resolve_loc_str = _hzB.resolve_loc_str
local _install_popup_logger = _hzB.install_popup_logger
local _drain_popup_log = _hzB.drain_popup_log
local _dismiss_modal_dialogs = _hzB.dismiss_modal_dialogs
local _restock_formation = _hzB.restock_formation
local _next_ready_formation = _hzB.next_ready_formation
local _join_rally_headless = _hzB.join_rally_headless
local _is_my_march_target = _hzB.is_my_march_target
local _is_point_blacklisted = _hzB.is_point_blacklisted
local _pick_free_formations = _hzB.pick_free_formations
local _get_squad_occupancy = _hzB.get_squad_occupancy
if UIUtil or CommonDialog then pcall(_hzB.install_popup_logger) end
"""

_HZ_BRIDGE_LOCK = threading.Lock()
_HZ_BOOTSTRAPPED_TARGETS: dict[tuple[int, int, float], float] = {}
_HZ_FINALIZED_BRIDGE_IDS: set[int] = set()


def _get_pid_create_time(pid: int) -> float:
    try:
        if int(pid) <= 0:
            return 0.0
        import psutil
        return round(float(psutil.Process(int(pid)).create_time()), 3)
    except Exception:
        return 0.0


def _mark_hz_bootstrapped(cd: Any, cache_key: tuple[int, int, float]) -> None:
    cd_id = cache_key[0]
    with _HZ_BRIDGE_LOCK:
        if len(_HZ_BOOTSTRAPPED_TARGETS) >= 128:
            _HZ_BOOTSTRAPPED_TARGETS.clear()
        _HZ_BOOTSTRAPPED_TARGETS[cache_key] = time.monotonic()
        if cd_id not in _HZ_FINALIZED_BRIDGE_IDS:
            _HZ_FINALIZED_BRIDGE_IDS.add(cd_id)
            try:
                def _cleanup_cd(_cid: int = cd_id) -> None:
                    with _HZ_BRIDGE_LOCK:
                        _HZ_FINALIZED_BRIDGE_IDS.discard(_cid)
                        for k in [k for k in _HZ_BOOTSTRAPPED_TARGETS if isinstance(k, tuple) and k[0] == _cid]:
                            _HZ_BOOTSTRAPPED_TARGETS.pop(k, None)

                weakref.finalize(cd, _cleanup_cd)
            except TypeError:
                _HZ_FINALIZED_BRIDGE_IDS.discard(cd_id)


def _eval_json(cd: Any, pid: int, lua_body: str, timeout: float = 8.0) -> dict[str, Any]:
    cache_key = (id(cd), int(pid), _get_pid_create_time(int(pid)))
    with _HZ_BRIDGE_LOCK:
        is_bootstrapped = cache_key in _HZ_BOOTSTRAPPED_TARGETS

    if is_bootstrapped:
        lua = _LUA_COMMON_SHIM + "\n" + lua_body
        ok, raw = cd.frida_eval_lua(pid, lua, timeout=timeout)
        if ok and isinstance(raw, str) and raw.strip() == "__HZ_NEED_BOOTSTRAP__":
            with _HZ_BRIDGE_LOCK:
                _HZ_BOOTSTRAPPED_TARGETS.pop(cache_key, None)
            lua_full = _LUA_COMMON_BOOTSTRAP + "\n" + lua_body
            ok, raw = cd.frida_eval_lua(pid, lua_full, timeout=timeout)
            if ok and not (isinstance(raw, str) and raw.strip() == "__HZ_NEED_BOOTSTRAP__"):
                _mark_hz_bootstrapped(cd, cache_key)
    else:
        lua = _LUA_COMMON_BOOTSTRAP + "\n" + lua_body
        ok, raw = cd.frida_eval_lua(pid, lua, timeout=timeout)
        if ok and not (isinstance(raw, str) and raw.strip() == "__HZ_NEED_BOOTSTRAP__"):
            _mark_hz_bootstrapped(cd, cache_key)

    if not ok:
        return {"ok": False, "error": str(raw), "send_errors": [str(raw)]}
    if isinstance(raw, dict):
        return _normalize_eval_payload(raw)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return _normalize_eval_payload(parsed)
        return {"ok": True, "result": parsed}
    except Exception as exc:
        err_msg = f"json decode failed: {exc}"
        return {"ok": False, "error": err_msg, "raw": str(raw)[:500], "send_errors": [err_msg]}


def snapshot_client(cd: Any, pid: int, include_world_count: bool = False) -> dict[str, Any]:
    if include_world_count:
        wp_block = """
local wpm = DataCenter and DataCenter.WorldPointManager
local avp = wpm and wpm.allViewPoints
if type(avp) == 'table' then
  for _ in pairs(avp) do
    snap.worldPointsCount = snap.worldPointsCount + 1
  end
  snap.hasWorldPoints = (snap.worldPointsCount > 0)
elseif avp ~= nil then
  local okC, cnt = pcall(function() return avp.Count end)
  snap.worldPointsCount = okC and (tonumber(cnt) or 0) or 0
  snap.hasWorldPoints = (snap.worldPointsCount > 0)
end
"""
    else:
        wp_block = """
local wpm = DataCenter and DataCenter.WorldPointManager
local avp = wpm and wpm.allViewPoints
local hasWp = false
if type(avp) == 'table' then
  hasWp = (next(avp) ~= nil)
elseif avp ~= nil then
  local okC, cnt = pcall(function() return avp.Count end)
  hasWp = (okC and (tonumber(cnt) or 0) > 0)
end
snap.hasWorldPoints = hasWp
snap.worldPointsCount = hasWp and 1 or 0
"""
    lua = f"""
local dismissed = _dismiss_modal_dialogs()
local snap = _get_player_snapshot()
snap.dismissed_modals = dismissed
snap.worldPointsCount = 0
snap.hasWorldPoints = false
{wp_block}
snap.shielded = false
if DataCenter and DataCenter.StatusManager and DataCenter.StatusManager.CheckShield then
  local ok_s, res_s = pcall(function() return DataCenter.StatusManager:CheckShield() end)
  snap.shielded = (ok_s and res_s) and true or false
end
snap.ok = true
return _enc(snap)
"""
    return _eval_json(cd, pid, lua, timeout=8.0)


def dismiss_all_popups(
    cd: Any,
    pid: int,
    client_state: dict[str, Any] | None = None,
    cfg: dict[str, Any] | None = None,
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Auto-dismiss any active modal popups (CommonDialog, UIGiftPackageRewardGet, etc.)."""
    lua = r"""
local dismissed = _dismiss_modal_dialogs()
return _enc({
  ok = true,
  task = 'dismiss_popups',
  dismissed_count = #dismissed,
  dismissed_windows = dismissed,
  action = #dismissed > 0 and 'dismissed' or 'none',
})
"""
    return _eval_json(cd, pid, lua, timeout=6.0)


def ensure_world_scene(cd: Any, pid: int, wait_seconds: float = 3.2) -> dict[str, Any]:
    snap = snapshot_client(cd, pid)
    if not snap.get("ok"):
        return snap
    last_in_world = bool(snap.get("inWorld"))
    last_points = int(snap.get("worldPointsCount", 0) or 0)
    if last_in_world and last_points > 0:
        return {"ok": True, "switched": False, "points": last_points}
    lua = r"""
if SceneManager and SceneManager.IsInWorld and not SceneManager:IsInWorld() then
  if SceneManager.ChangeToWorld then
    SceneManager:ChangeToWorld()
    return _enc({ok = true, triggered = true})
  end
  return _enc({ok = false, triggered = false, error = 'SceneManager.ChangeToWorld unavailable'})
end
return _enc({ok = true, triggered = false})
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if not res.get("ok"):
        return res
    triggered = bool(res.get("triggered"))
    deadline = time.time() + max(0.0, float(wait_seconds))
    while time.time() < deadline:
        time.sleep(0.45)
        post = snapshot_client(cd, pid)
        if not post.get("ok"):
            return post
        last_in_world = bool(post.get("inWorld"))
        last_points = int(post.get("worldPointsCount", 0) or 0)
        if last_in_world and last_points > 0:
            return {"ok": True, "switched": triggered, "points": last_points}
    return {
        "ok": False,
        "reason": "world_scene_timeout",
        "switched": triggered,
        "inWorld": last_in_world,
        "points": last_points,
    }


def _precheck_world_step_readiness(
    cd: Any,
    pid: int,
    *,
    task_name: str,
    reserve: int = 0,
    context: dict[str, Any] | None = None,
    dry_run: bool = False,
    check_alliance: bool = False,
    min_stamina: int = 0,
    stamina_cost: int = 0,
    strict_stamina_reserve: bool = True,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Read-only squad/stamina/alliance readiness check BEFORE ensure_world_scene().

    Returns a finalized step-contract dict when the step can exit immediately (e.g. all
    squads busy -> waiting_for_squad, no troops -> no_troops_or_formations, out of stamina,
    not in alliance, or offline) WITHOUT yanking the client out of City view to World Map.
    Returns None when squads are usable and World scene is confirmed ready.
    """
    if dry_run:
        return None
    exclude_lua = _used_formations_lua(context, pid)
    resv = max(0, int(reserve or 0))
    lua = f"""
local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local usable = _pick_free_formations({resv}, {exclude_lua}, false, true)
local wpm = DataCenter and DataCenter.WorldPointManager
local avp = wpm and wpm.allViewPoints
local hasWp = false
if type(avp) == 'table' then
  hasWp = (next(avp) ~= nil)
elseif avp ~= nil then
  local okC, cnt = pcall(function() return avp.Count end)
  hasWp = (okC and (tonumber(cnt) or 0) > 0)
end
return _enc({{
  ok = true,
  inWorld = snap.inWorld and true or false,
  hasWorldPoints = hasWp and true or false,
  inAlliance = snap.inAlliance and true or false,
  stamina = snap.stamina,
  free_formations = occ.free_formations,
  usable_formations = #usable,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
}})
"""
    pre = _eval_json(cd, pid, lua, timeout=8.0)
    extra = dict(extra_fields or {})
    if not pre.get("ok"):
        return _ensure_step_contract(
            {
                **extra,
                **pre,
                "ok": False,
                "task": task_name,
                "dry_run": False,
                "status": "error",
                "stop_reason": pre.get("error") or "client_offline",
                "dispatched": [],
            },
            task_name=task_name,
        )

    free_f = int(pre.get("free_formations") or 0)
    usable_f = int(pre.get("usable_formations") or 0)
    active_m = int(pre.get("active_marches") or 0)
    total_f = int(pre.get("total_formations") or 0)
    stam = int(pre.get("stamina") or 0)

    if check_alliance and not pre.get("inAlliance"):
        return _ensure_step_contract(
            {
                **extra,
                "ok": True,
                "task": task_name,
                "dry_run": False,
                "status": "physical_limit",
                "stop_reason": "not_in_alliance",
                "reason": "not_in_alliance",
                "free_formations": free_f,
                "usable_formations": usable_f,
                "active_marches": active_m,
                "total_formations": total_f,
                "stamina": stam,
                "dispatched": [],
                "message": "Not in an alliance",
            },
            task_name=task_name,
        )

    if stamina_cost > 0:
        min_s = max(0, int(min_stamina or 0))
        cost_s = max(1, int(stamina_cost))
        need_stam = (min_s + cost_s) if strict_stamina_reserve else max(cost_s, min_s)
        if stam >= need_stam:
            max_by_stam = (stam - min_s) // cost_s
            if not strict_stamina_reserve:
                max_by_stam = max(1, max_by_stam)
        else:
            max_by_stam = 0
        if stam < need_stam or max_by_stam <= 0:
            return _ensure_step_contract(
                {
                    **extra,
                    "ok": True,
                    "task": task_name,
                    "dry_run": False,
                    "status": "physical_limit",
                    "stop_reason": "out_of_stamina",
                    "reason": "out_of_stamina",
                    "free_formations": free_f,
                    "usable_formations": usable_f,
                    "active_marches": active_m,
                    "total_formations": total_f,
                    "stamina": stam,
                    "dispatched": [],
                    "message": f"Out of stamina ({stam} left, need >={need_stam})",
                },
                task_name=task_name,
            )

    if usable_f == 0:
        if active_m > 0:
            return _ensure_step_contract(
                {
                    **extra,
                    "ok": True,
                    "task": task_name,
                    "dry_run": False,
                    "status": "waiting_for_squad",
                    "stop_reason": "",
                    "reason": "no_free_formation_above_reserve",
                    "free_formations": free_f,
                    "usable_formations": 0,
                    "active_marches": active_m,
                    "total_formations": total_f,
                    "stamina": stam,
                    "dispatched": [],
                    "message": f"Waiting for returning squad ({active_m}/{total_f} active marches)",
                },
                task_name=task_name,
            )
        return _ensure_step_contract(
            {
                **extra,
                "ok": True,
                "task": task_name,
                "dry_run": False,
                "status": "physical_limit",
                "stop_reason": "no_troops_or_formations",
                "reason": "no_free_formation_above_reserve",
                "free_formations": free_f,
                "usable_formations": 0,
                "active_marches": 0,
                "total_formations": total_f,
                "stamina": stam,
                "dispatched": [],
                "message": f"No usable squads available (free={free_f}, total={total_f}, reserve={resv})",
            },
            task_name=task_name,
        )

    if not pre.get("inWorld") or not pre.get("hasWorldPoints"):
        sw = ensure_world_scene(cd, pid)
        if not sw.get("ok") and not sw.get("inWorld"):
            return _ensure_step_contract(
                {
                    **extra,
                    **sw,
                    "ok": False,
                    "task": task_name,
                    "dry_run": False,
                    "status": "error",
                    "stop_reason": sw.get("reason") or sw.get("error") or "world_scene_timeout",
                    "dispatched": [],
                },
                task_name=task_name,
            )
    return None


def _lua_claim_alliance_gifts_block(dry_run_var: str = "dryRun", flag_var: str = "true") -> str:
    """Shared Lua snippet to claim Alliance Gifts & Rare Chests across BOTH Tab 1 and Tab 2."""
    return f"""
out.tab1_pending = tonumber(out.tab1_pending or 0) or 0
out.tab2_pending = tonumber(out.tab2_pending or 0) or 0
out.tab1_gifts_claimed = tonumber(out.tab1_gifts_claimed or 0) or 0
out.tab2_chests_claimed = tonumber(out.tab2_chests_claimed or 0) or 0
out.other_gifts_claimed = tonumber(out.other_gifts_claimed or 0) or 0
out.gifts_claimed = tonumber(out.gifts_claimed or 0) or 0
out.gift_claim_mode = tostring(out.gift_claim_mode or 'none')
out.errors = out.errors or {{}}

local agm = DataCenter and DataCenter.AllianceGiftDataManager
if ({flag_var}) and snap.inAlliance and agm then
  local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
    and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
    or ((tonumber(snap.serverSec or 0) or 0) * 1000)
  local tab1List, tab2List, otherTabs, seenGift = {{}}, {{}}, {{}}, {{}}
  local function _collect_gift(g, fallbackType)
    if type(g) ~= 'table' then return end
    local uuid = tostring(g.uuid or '')
    if uuid == '' or seenGift[uuid] then return end
    seenGift[uuid] = true
    local recv = tonumber(g.receiveState or 0) or 0
    if recv ~= 0 then return end
    local exp = tonumber(g.endTime or g.expirationTime or 0) or 0
    if exp > 0 and exp < 1e12 then exp = exp * 1000 end
    if exp > 0 and nowMs > 0 and exp <= nowMs then return end
    local rt = tonumber(g.rewardType or g.grpType or fallbackType or 1) or 1
    if rt == 1 then
      table.insert(tab1List, uuid)
    elseif rt == 2 then
      table.insert(tab2List, uuid)
    else
      otherTabs[rt] = otherTabs[rt] or {{}}
      table.insert(otherTabs[rt], uuid)
    end
  end

  local hasHydratedList = (type(agm.giftInfoList) == 'table' and next(agm.giftInfoList) ~= nil)
  if type(agm.giftInfoList) == 'table' then
    for _, g in pairs(agm.giftInfoList) do _collect_gift(g, nil) end
  end
  if agm.GetGiftInfoList then
    for _, tIdx in ipairs({{1, 2}}) do
      local lst = _safe_call(function() return agm:GetGiftInfoList(tIdx) end, nil)
      if type(lst) == 'table' then
        if next(lst) ~= nil then hasHydratedList = true end
        for _, g in pairs(lst) do _collect_gift(g, tIdx) end
      end
    end
  end

  -- Also check levelUpGiftInfoList if present
  local lvlPending = {{}}
  local lvlSrc = agm.levelUpGiftInfoList
  if (type(lvlSrc) ~= 'table' or next(lvlSrc) == nil) and agm.GetLevelUpGiftInfo then
    lvlSrc = _safe_call(function() return agm:GetLevelUpGiftInfo() end, nil)
  end
  if type(lvlSrc) == 'table' then
    for _, lg in pairs(lvlSrc) do
      if type(lg) == 'table' and tonumber(lg.receiveState or 0) == 0 and lg.uuid then
        table.insert(lvlPending, lg)
      end
    end
  end

  out.tab1_pending = #tab1List
  out.tab2_pending = #tab2List
  local modes = {{}}
  local totalGiftNum = tonumber(_safe_call(function() return agm:GetGiftNum() end, 0)) or 0

  -- Claim Tab 1 (Normal Gifts, rewardType = 1)
  if #tab1List > 0 then
    if MsgDefines and MsgDefines.AllianceReceiveAllGift and SFSNetwork then
      if not {dry_run_var} then
        local ok1, err1 = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceReceiveAllGift, 1) end)
        if not ok1 then table.insert(out.errors, 'AllianceGiftTab1All: ' .. tostring(err1)) end
      end
      out.tab1_gifts_claimed = #tab1List
      table.insert(modes, 'tab1_all(' .. #tab1List .. ')')
    elseif MsgDefines and MsgDefines.AllianceGiftGetReward and SFSNetwork then
      local c1 = 0
      for _, uuid in ipairs(tab1List) do
        if c1 >= 30 then break end
        if not {dry_run_var} then
          local ok1, err1 = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceGiftGetReward, uuid, 1) end)
          if not ok1 then table.insert(out.errors, 'AllianceGiftTab1: ' .. tostring(err1)) break end
        end
        c1 = c1 + 1
      end
      out.tab1_gifts_claimed = c1
      table.insert(modes, 'tab1_single(' .. c1 .. ')')
    end
  end

  -- Claim Tab 2 (Rare / Alliance Chests, rewardType = 2)
  if #tab2List > 0 then
    local k4 = tonumber((LuaEntry and LuaEntry.DataConfig and LuaEntry.DataConfig.TryGetNum
      and _safe_call(function() return LuaEntry.DataConfig:TryGetNum('alliance_gift', 'k4') end, 10)) or 10) or 10
    if k4 <= 0 then k4 = 10 end
    if (#tab2List >= k4 or not (MsgDefines and MsgDefines.AllianceGiftGetReward)) and MsgDefines and MsgDefines.AllianceReceiveAllGift and SFSNetwork then
      if not {dry_run_var} then
        local ok2, err2 = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceReceiveAllGift, 2) end)
        if not ok2 then table.insert(out.errors, 'AllianceGiftTab2All: ' .. tostring(err2)) end
      end
      out.tab2_chests_claimed = #tab2List
      table.insert(modes, 'tab2_all(' .. #tab2List .. ')')
    elseif MsgDefines and MsgDefines.AllianceGiftGetReward and SFSNetwork then
      local c2 = 0
      for _, uuid in ipairs(tab2List) do
        if c2 >= 30 then break end
        if not {dry_run_var} then
          local ok2, err2 = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceGiftGetReward, uuid, 2) end)
          if not ok2 then table.insert(out.errors, 'AllianceGiftTab2: ' .. tostring(err2)) break end
        end
        c2 = c2 + 1
      end
      out.tab2_chests_claimed = c2
      table.insert(modes, 'tab2_single(' .. c2 .. ')')
    end
  end

  -- Claim any other rewardType buckets if present
  for rt, list in pairs(otherTabs) do
    if #list > 0 then
      if MsgDefines and MsgDefines.AllianceReceiveAllGift and SFSNetwork then
        if not {dry_run_var} then
          local okO, errO = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceReceiveAllGift, rt) end)
          if not okO then table.insert(out.errors, 'AllianceGiftTab' .. tostring(rt) .. ': ' .. tostring(errO)) end
        end
        out.other_gifts_claimed = out.other_gifts_claimed + #list
        table.insert(modes, 'tab' .. tostring(rt) .. '_all(' .. #list .. ')')
      elseif MsgDefines and MsgDefines.AllianceGiftGetReward and SFSNetwork then
        for _, uuid in ipairs(list) do
          if not {dry_run_var} then
            local okO, errO = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceGiftGetReward, uuid, rt) end)
            if not okO then table.insert(out.errors, 'AllianceGiftSingle: ' .. tostring(errO)) break end
          end
          out.other_gifts_claimed = out.other_gifts_claimed + 1
        end
      end
    end
  end

  -- Fallback ONLY if GetGiftNum > 0 while giftInfoList has NOT yet hydrated at all (prevents empty-tab UINoticeTips popups)
  if not hasHydratedList and out.tab1_gifts_claimed == 0 and out.tab2_chests_claimed == 0 and out.other_gifts_claimed == 0 and totalGiftNum > 0 then
    if MsgDefines and MsgDefines.AllianceReceiveAllGift and SFSNetwork then
      local fbSent = false
      if not {dry_run_var} then
        local ok1, err1 = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceReceiveAllGift, 1) end)
        local ok2, err2 = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceReceiveAllGift, 2) end)
        if not ok1 then table.insert(out.errors, 'AllianceReceiveAllGift(1): ' .. tostring(err1)) end
        if not ok2 then table.insert(out.errors, 'AllianceReceiveAllGift(2): ' .. tostring(err2)) end
        fbSent = ok1 or ok2
      else
        fbSent = true
      end
      if fbSent then
        out.other_gifts_claimed = totalGiftNum
        table.insert(modes, 'fallback_tabs_1_2(' .. totalGiftNum .. ')')
      end
    end
  end

  -- Claim any alliance gift level-up chests or daily gift chests
  local agmCurLv = tonumber(_safe_call(function() return agm:GetCurLevel() end, 0)) or 0
  if #lvlPending > 0 then
    for _, lg in ipairs(lvlPending) do
      local uuid = tostring(lg.uuid)
      local rt = tonumber(lg.rewardType or 3) or 3
      local lLv = tonumber(lg.level or agmCurLv) or agmCurLv
      if not {dry_run_var} and SFSNetwork and MsgDefines then
        if MsgDefines.ReceiveGiftLevReward and lLv > 0 then
          local okL, errL = pcall(function() SFSNetwork.SendMessage(MsgDefines.ReceiveGiftLevReward, lLv) end)
          if not okL then table.insert(out.errors, 'ReceiveGiftLevReward: ' .. tostring(errL)) end
        elseif MsgDefines.AllianceGiftGetReward then
          local okL, errL = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceGiftGetReward, uuid, rt) end)
          if not okL then table.insert(out.errors, 'AllianceLevelGift: ' .. tostring(errL)) end
        end
      end
      out.other_gifts_claimed = out.other_gifts_claimed + 1
    end
  end
  if type(agm.dailyReward) == 'table' then
    for stageKey, dr in pairs(agm.dailyReward) do
      if type(dr) == 'table' and tonumber(dr.state or dr.receiveState or 0) == 1 then
        local stNum = tonumber(dr.stage or stageKey or 0) or 0
        if stNum > 0 and not {dry_run_var} and SFSNetwork and MsgDefines and MsgDefines.ReceiveGiftDailyReward then
          local okD, errD = pcall(function() SFSNetwork.SendMessage(MsgDefines.ReceiveGiftDailyReward, stNum) end)
          if not okD then table.insert(out.errors, 'ReceiveGiftDailyReward(' .. tostring(stNum) .. '): ' .. tostring(errD)) end
        end
        if stNum > 0 then out.other_gifts_claimed = out.other_gifts_claimed + 1 end
      end
    end
  end

  out.gifts_claimed = out.tab1_gifts_claimed + out.tab2_chests_claimed + out.other_gifts_claimed
  if #modes > 0 then out.gift_claim_mode = table.concat(modes, '+') end
end
"""


def _wait_for_alliance_gift_hydration(
    cd: Any,
    pid: int,
    max_wait_sec: float = 1.8,
    step_sec: float = 0.35,
) -> None:
    """Poll until AllianceGiftDataManager hydrates after AllianceGiftList before fallback claim."""
    poll_lua = r"""
local dc = DataCenter
local agm = dc and dc.AllianceGiftDataManager
if not agm then return _enc({ok = true, hydrated = true}) end
local num = agm.GetGiftNum and tonumber(_safe_call(function() return agm:GetGiftNum() end, 0)) or 0
if num <= 0 then return _enc({ok = true, hydrated = true}) end
if type(agm.giftInfoList) == 'table' and next(agm.giftInfoList) ~= nil then
  return _enc({ok = true, hydrated = true})
end
if agm.GetGiftInfoList then
  for tab = 1, 2 do
    local tlist = _safe_call(function() return agm:GetGiftInfoList(tab) end, nil)
    if type(tlist) == 'table' and next(tlist) ~= nil then
      return _enc({ok = true, hydrated = true})
    end
  end
end
return _enc({ok = true, hydrated = false})
"""
    deadline = time.monotonic() + max(0.0, float(max_wait_sec))
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(step_sec, remaining))
        p_res = _eval_json(cd, pid, poll_lua, timeout=5.0)
        if not isinstance(p_res, dict) or not p_res.get("ok") or p_res.get("hydrated"):
            break


def _merge_unique_list_field(dst: dict[str, Any], src: dict[str, Any], key: str, as_str: bool = False) -> None:
    cur = dst.get(key)
    if isinstance(cur, list):
        merged = list(cur)
    elif isinstance(cur, tuple):
        merged = list(cur)
    elif isinstance(cur, dict):
        merged = list(cur.values()) if cur else []
    elif cur is None:
        merged = []
    else:
        merged = [str(cur)] if as_str else [cur]
    add_val = src.get(key)
    if isinstance(add_val, (list, tuple, set)):
        items = list(add_val)
    elif isinstance(add_val, dict):
        items = list(add_val.values()) if add_val else []
    elif add_val is not None:
        items = [add_val]
    else:
        items = []
    for item in items:
        norm = str(item or "").strip() if as_str else item
        if as_str and not norm:
            continue
        if norm not in merged:
            merged.append(norm)
    if merged or key in dst or items:
        dst[key] = merged


def _run_alliance_gifts_followup(cd: Any, pid: int, dry_run: bool, res: dict[str, Any]) -> dict[str, Any]:
    """Claim alliance gifts after AllianceGiftList hydration when pass 1 requested the list."""
    if not dry_run:
        _wait_for_alliance_gift_hydration(cd, pid, max_wait_sec=1.8, step_sec=0.35)
    gifts_lua = _lua_claim_alliance_gifts_block("dryRun", "true")
    followup_lua = f"""
local dryRun = {str(dry_run).lower()}
local snap = _get_player_snapshot()
local out = {{
  ok = true,
  tab1_gifts_claimed = 0,
  tab2_chests_claimed = 0,
  other_gifts_claimed = 0,
  gifts_claimed = 0,
  tab1_pending = 0,
  tab2_pending = 0,
  gift_claim_mode = 'none',
  errors = {{}},
  send_errors = {{}},
  popped_modals = {{}},
  detail_lines = {{}},
}}
{gifts_lua}
if out.gifts_claimed > 0 or out.tab1_pending > 0 or out.tab2_pending > 0 then
  table.insert(out.detail_lines, string.format('Alliance Gifts: Tab1 normal=%d claimed (pending=%d), Tab2 chests=%d claimed (pending=%d), other=%d [mode=%s]', out.tab1_gifts_claimed, out.tab1_pending, out.tab2_chests_claimed, out.tab2_pending, out.other_gifts_claimed, tostring(out.gift_claim_mode)))
end
if not dryRun and out.gifts_claimed > 0 and type(_dismiss_modal_dialogs) == 'function' then
  local okD, dRes = pcall(_dismiss_modal_dialogs)
  if okD and type(dRes) == 'table' then
    for _, w in ipairs(dRes) do table.insert(out.popped_modals, w) end
  end
end
return _enc(out)
"""
    g_res = _eval_json(cd, pid, followup_lua, timeout=8.0)
    res.pop("needs_gift_wait", None)
    if not isinstance(g_res, dict) or not g_res.get("ok"):
        if isinstance(g_res, dict):
            _merge_unique_list_field(res, g_res, "errors", as_str=True)
            _merge_unique_list_field(res, g_res, "send_errors", as_str=True)
            _merge_unique_list_field(res, g_res, "in_game_tips", as_str=True)
            _merge_unique_list_field(res, g_res, "popped_modals", as_str=False)
            g_err = str(g_res.get("error") or "").strip()
            if g_err:
                errs = res.setdefault("errors", [])
                if isinstance(errs, list) and g_err not in errs:
                    errs.append(g_err)
                serrs = res.setdefault("send_errors", [])
                if isinstance(serrs, list) and g_err not in serrs:
                    serrs.append(g_err)
            if "in_game_tips" in res:
                res["in_game_tips"] = _clean_in_game_tips(res["in_game_tips"])
            if res.get("action") in (None, "none"):
                res["ok"] = False
                res["error"] = g_err or "alliance_gifts_followup_failed"
                res["message"] = f"Alliance gift claim follow-up failed: {res['error']}"
            else:
                res["gift_followup_ok"] = False
        return res
    for k in (
        "tab1_gifts_claimed",
        "tab2_chests_claimed",
        "other_gifts_claimed",
        "gifts_claimed",
        "tab1_pending",
        "tab2_pending",
        "gift_claim_mode",
    ):
        if k in g_res:
            res[k] = g_res[k]
    for list_key in ("errors", "send_errors", "in_game_tips", "detail_lines"):
        _merge_unique_list_field(res, g_res, list_key, as_str=(list_key != "detail_lines"))
    _merge_unique_list_field(res, g_res, "popped_modals", as_str=False)
    if "in_game_tips" in res:
        res["in_game_tips"] = _clean_in_game_tips(res["in_game_tips"])

    gifts_claimed = int(res.get("gifts_claimed", 0) or 0)
    if gifts_claimed > 0:
        tab1 = int(res.get("tab1_gifts_claimed", 0) or 0)
        tab2 = int(res.get("tab2_chests_claimed", 0) or 0)
        if res.get("task") == "auto_help":
            parts: list[str] = []
            if res.get("helped_all"):
                parts.append(f"helped {int(res.get('ally_help_num', 0) or 0)} allies")
            call_helps = res.get("call_helps")
            if isinstance(call_helps, list) and len(call_helps) > 0:
                parts.append(f"requested {len(call_helps)} helps")
            parts.append(f"claimed {gifts_claimed} gifts (Tab1={tab1}, Tab2={tab2})")
            res["action"] = (
                "helped_alliance"
                if res.get("helped_all")
                else ("claimed_gifts" if gifts_claimed > 0 else "called_help")
            )
            res["message"] = ", ".join(parts)
        else:
            if res.get("action") in (None, "none", ""):
                res["action"] = "completed"
            dl = res.get("detail_lines")
            if isinstance(dl, list):
                res["detail_lines"] = [
                    line for line in dl if not str(line).startswith("No pending alliance gifts")
                ]
            old_msg = str(res.get("message") or "")
            if not old_msg or old_msg.startswith("No pending"):
                res["message"] = f"claimed {gifts_claimed} gifts (Tab1={tab1}, Tab2={tab2})"
    return res


def run_auto_help(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("auto_help") or {}
    claim_gifts = bool(task_cfg.get("claim_gifts", True))
    gifts_lua = _lua_claim_alliance_gifts_block("dryRun", "claimGifts") if claim_gifts else ""
    lua = f"""
local dryRun = {str(dry_run).lower()}
local claimGifts = {str(claim_gifts).lower()}
local snap = _get_player_snapshot()
local dismissed = {{}}
local out = {{
  ok = true,
  task = 'auto_help',
  dry_run = dryRun,
  helped_all = false,
  ally_help_num = 0,
  call_helps = {{}},
  tab1_gifts_claimed = 0,
  tab2_chests_claimed = 0,
  other_gifts_claimed = 0,
  gifts_claimed = 0,
  tab1_pending = 0,
  tab2_pending = 0,
  gift_claim_mode = 'none',
  popped_modals = dismissed,
  errors = {{}},
  detail_lines = {{}},
}}
local hm = DataCenter and DataCenter.AllianceHelpDataManager
if hm then
  local helpNum = tonumber(_safe_call(function() return hm:GetHelpNum() end, hm.helpNum or 0)) or 0
  local otherCnt = 0
  if hm.otherHelpInfoList then
    for _ in pairs(hm.otherHelpInfoList) do otherCnt = otherCnt + 1 end
  end
  out.ally_help_num = math.max(helpNum, otherCnt)
  if out.ally_help_num > 0 then
    if not dryRun and SFSNetwork and MsgDefines and MsgDefines.AlHelpAll then
      local srvMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
        and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
        or ((tonumber(snap.serverSec or 0) or 0) * 1000)
      local okH, errH = pcall(function() SFSNetwork.SendMessage(MsgDefines.AlHelpAll, srvMs, true) end)
      if not okH then table.insert(out.errors, 'AlHelpAll: ' .. tostring(errH)) end
    end
    out.helped_all = true
    table.insert(out.detail_lines, string.format('Alliance Help: helped %d pending ally requests (AlHelpAll)', out.ally_help_num))
  end
end

local bm = DataCenter and DataCenter.BuildManager
if snap.inAlliance and bm and bm.GetAllBuildings and bm.GetBuildingDataByUuid then
  local buildings = bm:GetAllBuildings() or {{}}
  for _, b in pairs(buildings) do
    local uuid = b and b.uuid
    if uuid then
      local state = tonumber(b.state or 0) or 0
      local isUp = (state ~= 0) or _safe_call(function() return bm:IsUpgrading(uuid) end, false)
      local helped = tonumber(b.isHelped or 0) or 0
      if isUp and helped == 0 then
        if not dryRun then
          local helpType = (AllianceHelpType and (state == 4 and AllianceHelpType.FIX_BUILDING or AllianceHelpType.Building)) or 1
          local defQt = (NewQueueType and NewQueueType.Default) or 0
          local okB, errB = pcall(function()
            if hm and hm.SendCallHelp then
              hm:SendCallHelp(uuid, helpType, defQt, tostring(b.itemId or ''))
            elseif SFSNetwork and MsgDefines and MsgDefines.AllianceCallHelp then
              SFSNetwork.SendMessage(MsgDefines.AllianceCallHelp, tonumber(uuid) or uuid, helpType, defQt, tostring(b.itemId or ''))
            end
          end)
          if not okB then table.insert(out.errors, 'BuildingCallHelp: ' .. tostring(errB)) end
        end
        table.insert(out.call_helps, {{kind = 'building', uuid = tostring(uuid), itemId = b.itemId, state = state}})
        table.insert(out.detail_lines, string.format('Call Help: building item=%s uuid=%s state=%d', tostring(b.itemId or '?'), tostring(uuid), state))
      end
    end
  end
end

local qm = DataCenter and DataCenter.QueueDataManager
if snap.inAlliance and qm and qm.queueDic then
  local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
    and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
    or ((tonumber(snap.serverSec or 0) or 0) * 1000)
  -- Strictly include genuinely alliance-helpable queue types (exclude Army/Soldier training & promotion queues 1, 8, 9, 34!)
  local nonHelpableTypes = {{[1] = true, [8] = true, [9] = true, [34] = true, [45] = true}}
  local helpableTypes = {{[3] = 'healing', [6] = 'research', [11] = 'crafting:ProductEquip', [35] = 'healing:DomainHospital', [36] = 'crafting:EquipMaterial', [46] = 'dragon_healing', [107] = 'crafting:Equip'}}
  if type(NewQueueType) == 'table' then
    for k, v in pairs(NewQueueType) do
      local n = tonumber(v)
      if n and not nonHelpableTypes[n] and type(k) == 'string' then
        local kl = string.lower(k)
        if kl:find('science') or kl:find('research') or kl:find('tech') then
          helpableTypes[n] = helpableTypes[n] or ('research:' .. k)
        elseif kl:find('hospital') or kl:find('heal') or kl:find('cure') then
          helpableTypes[n] = helpableTypes[n] or ('healing:' .. k)
        elseif kl:find('craft') or kl:find('forge') or kl:find('equip') or kl:find('chip') or kl:find('make') or kl:find('workshop') or kl:find('gear') then
          helpableTypes[n] = helpableTypes[n] or ('crafting:' .. k)
        elseif (kl:find('build') or kl:find('repair')) and not kl:find('army') and not kl:find('soldier') then
          helpableTypes[n] = helpableTypes[n] or ('building:' .. k)
        end
      end
    end
  end

  for _, q in pairs(qm.queueDic) do
    if type(q) == 'table' and q.uuid and tonumber(q.state or 0) == 2 then
      local endT = tonumber(q.endTime or 0) or 0
      if endT > 0 and endT < 1e12 then endT = endT * 1000 end
      local active = (endT == 0 or nowMs == 0 or endT > nowMs)
      local alreadyHelped = (tonumber(q.isHelped or 0) or 0) ~= 0 or (tonumber(q.callHelp or 0) or 0) ~= 0
      local qt = tonumber(q.type or 0) or 0
      local qKind = helpableTypes[qt]
      if not qKind and tonumber(q.canHelp or 0) == 1 then
        qKind = 'queue_' .. tostring(qt)
      end
      if active and not alreadyHelped and qKind then
        if not dryRun then
          local helpType = (AllianceHelpType and AllianceHelpType.Queue) or 2
          local okQ, errQ = pcall(function()
            if hm and hm.SendCallHelp then
              hm:SendCallHelp(q.uuid, helpType, qt, tostring(q.itemId or ''))
            elseif SFSNetwork and MsgDefines and MsgDefines.AllianceCallHelp then
              SFSNetwork.SendMessage(MsgDefines.AllianceCallHelp, tonumber(q.uuid) or q.uuid, helpType, qt, tostring(q.itemId or ''))
            end
          end)
          if not okQ then table.insert(out.errors, 'QueueCallHelp(' .. tostring(qKind) .. '): ' .. tostring(errQ)) end
        end
        table.insert(out.call_helps, {{kind = qKind, uuid = tostring(q.uuid), qType = qt, itemId = q.itemId}})
        table.insert(out.detail_lines, string.format('Call Help: %s qType=%d uuid=%s item=%s', tostring(qKind), qt, tostring(q.uuid), tostring(q.itemId or '')))
      end
    end
  end
end

local _agmPre = claimGifts and snap.inAlliance and DataCenter and DataCenter.AllianceGiftDataManager
local _gNumPre = _agmPre and _agmPre.GetGiftNum and tonumber(_safe_call(function() return _agmPre:GetGiftNum() end, 0)) or 0
local _hasListPre = type(_agmPre and _agmPre.giftInfoList) == 'table' and next(_agmPre.giftInfoList) ~= nil
if not dryRun and _agmPre and _gNumPre > 0 and not _hasListPre and SFSNetwork and MsgDefines and MsgDefines.AllianceGiftList then
  local okGl, errGl = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceGiftList, 0, 200) end)
  if okGl then
    out.needs_gift_wait = true
  else
    table.insert(out.errors, 'AllianceGiftList: ' .. tostring(errGl))
  end
else
{gifts_lua}
end
if out.gifts_claimed > 0 or out.tab1_pending > 0 or out.tab2_pending > 0 then
  table.insert(out.detail_lines, string.format('Alliance Gifts: Tab1 normal=%d claimed (pending=%d), Tab2 chests=%d claimed (pending=%d), other=%d [mode=%s]', out.tab1_gifts_claimed, out.tab1_pending, out.tab2_chests_claimed, out.tab2_pending, out.other_gifts_claimed, tostring(out.gift_claim_mode)))
end

if out.helped_all or #out.call_helps > 0 or out.gifts_claimed > 0 then
  if not dryRun and type(_dismiss_modal_dialogs) == 'function' then
    local okD, dRes = pcall(_dismiss_modal_dialogs)
    if okD and type(dRes) == 'table' then
      for _, w in ipairs(dRes) do table.insert(out.popped_modals, w) end
    end
  end
  local parts = {{}}
  if out.helped_all then table.insert(parts, string.format("helped %d allies", out.ally_help_num)) end
  if #out.call_helps > 0 then table.insert(parts, string.format("requested %d helps", #out.call_helps)) end
  if out.gifts_claimed > 0 then
    table.insert(parts, string.format("claimed %d gifts (Tab1=%d, Tab2=%d)", out.gifts_claimed, out.tab1_gifts_claimed, out.tab2_chests_claimed))
  end
  out.action = (out.helped_all and 'helped_alliance') or (out.gifts_claimed > 0 and 'claimed_gifts') or 'called_help'
  out.message = table.concat(parts, ', ')
else
  out.action = 'none'
  out.message = 'No pending alliance helps, queues, or Tab1/Tab2 gifts'
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if not dry_run and res.get("ok") and res.get("needs_gift_wait"):
        res = _run_alliance_gifts_followup(cd, pid, dry_run, res)
    return res


def run_rf_hq_under_attack(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("rf_hq_under_attack", {})
    reserve = int(cfg.get("formation_reserve", 0))
    protected_uids = list((context or {}).get("protected_uids", []))
    protected_lua = "{" + ",".join(f"[{json.dumps(str(u))}]=true" for u in protected_uids if u) + "}"
    reinf_protected = bool(task_cfg.get("reinforce_protected_uids", True))
    reinf_ally = bool(task_cfg.get("reinforce_alliance_members", True))
    auto_shield = bool(task_cfg.get("auto_shield_on_self_attack", False))
    max_eta = int(task_cfg.get("max_incoming_eta_seconds", 900))
    dispatched_targets = list((context or {}).get("reinforced_targets", []))
    dispatched_lua = "{" + ",".join(f"[{json.dumps(str(t))}]=true" for t in dispatched_targets if t) + "}"

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local protectedUids = {protected_lua}
local dispatchedTargets = {dispatched_lua}
local reinfProtected = {str(reinf_protected).lower()}
local reinfAlly = {str(reinf_ally).lower()}
local autoShield = {str(auto_shield).lower()}
local maxEtaSec = {max_eta}

local snap = _get_player_snapshot()
local out = {{
  ok = true,
  task = 'rf_hq_under_attack',
  dry_run = dryRun,
  self_uid = snap.uid,
  self_under_attack = false,
  shielded = false,
  shield_used = nil,
  threats = {{}},
  reinforcements = {{}},
  alerts = {{}},
}}

if DataCenter.StatusManager and DataCenter.StatusManager.CheckShield then
  local ok_s, sh = pcall(function() return DataCenter.StatusManager:CheckShield() end)
  out.shielded = (ok_s and sh) and true or false
end

local nowMs = snap.serverSec * 1000
local rawThreats = {{}}

local function _push_threat(src, obj)
  if type(obj) ~= 'table' then return end
  local targetType = tonumber(obj.target or obj.targetType or obj.marchType or -1)
  local targetUid = tostring(obj.targetUid or obj.belongUid or obj.defUid or '')
  local targetPt = tonumber(obj.targetPos or obj.targetPoint or obj.pointId or 0)
  local marchUid = tostring(obj.uuid or obj.marchUuid or '')
  local ownerUid = tostring(obj.ownerUid or obj.atkUid or '')
  local ownerAlly = tostring(obj.allianceUid or '')
  local allyName = tostring(obj.allianceAbbr or '')
  if targetUid == '' and targetPt == snap.mainPos and snap.mainPos > 0 then
    targetUid = snap.uid
  end
  if ownerUid ~= '' and ownerUid == snap.uid then return end
  if snap.allianceUid ~= '' and ownerAlly == snap.allianceUid then return end

  local isHostileTarget = (targetType == 11 or targetType == 12 or targetType == 30 or targetType == 2 or targetType == 1)
  if src == 'radar' or src == 'alliance_alert' then
    if targetPt > 0 or targetUid ~= '' then isHostileTarget = true end
  end
  if not isHostileTarget or targetPt <= 0 then return end

  local endTime = tonumber(obj.endTime or obj.arriveTime or 0)
  local etaSec = -1
  if endTime > 0 and nowMs > 0 then
    etaSec = math.floor((endTime - nowMs) / 1000)
    if etaSec < -10 then return end
    if maxEtaSec > 0 and etaSec > maxEtaSec then return end
  end

  local key = marchUid ~= '' and marchUid or (tostring(targetPt) .. '_' .. targetUid)
  if not rawThreats[key] then
    rawThreats[key] = {{
      source = src,
      marchUuid = marchUid,
      targetType = targetType,
      targetUid = targetUid,
      targetPoint = targetPt,
      targetServerId = tonumber(obj.targetServer or snap.serverId) or snap.serverId,
      ownerName = tostring(obj.ownerName or ''),
      ownerAlliance = allyName,
      etaSec = etaSec,
      isSelf = (targetUid == snap.uid) or (snap.mainPos > 0 and targetPt == snap.mainPos),
      isProtected = (targetUid ~= '' and protectedUids[targetUid] == true),
    }}
  end
end

if DataCenter.RadarAlarmDataManager and DataCenter.RadarAlarmDataManager.GetAllMarches then
  local rm = DataCenter.RadarAlarmDataManager:GetAllMarches() or {{}}
  for _, m in pairs(rm) do _push_threat('radar', m) end
end
if DataCenter.AllianceAlertDataManager and DataCenter.AllianceAlertDataManager.GetAllianceAlertList then
  local al = DataCenter.AllianceAlertDataManager:GetAllianceAlertList() or {{}}
  for _, a in pairs(al) do _push_threat('alliance_alert', a) end
end
if DataCenter.WorldMarchDataManager and DataCenter.WorldMarchDataManager.allMarches then
  for _, m in pairs(DataCenter.WorldMarchDataManager.allMarches) do
    local t = tonumber(m and m.target or -1)
    if t == 11 or t == 12 then
      _push_threat('world_march', m)
    end
  end
end

local usableForms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, not dryRun)
local formIdx = 1

for _, th in pairs(rawThreats) do
  table.insert(out.threats, th)
  if th.isSelf then
    out.self_under_attack = true
    table.insert(out.alerts, string.format('SELF HQ ATTACKED by [%s] %s ETA=%ss', th.ownerAlliance, th.ownerName, tostring(th.etaSec)))
    if autoShield and not out.shielded then
      local bestShield = nil
      if DataCenter.ItemData and DataCenter.ItemData.ItemInfos and DataCenter.ItemTemplateManager then
        for id, info in pairs(DataCenter.ItemData.ItemInfos) do
          if tonumber(info and info.count or 0) > 0 then
            local ok_t, tmpl = pcall(function() return DataCenter.ItemTemplateManager:GetItemTemplate(tonumber(id)) end)
            if ok_t and tmpl then
              local nm = tostring(tmpl.GetName and tmpl:GetName() or ''):lower()
              if nm:find('shield') or nm:find('peace') or nm:find('truce') then
                bestShield = {{id = tostring(id), uuid = tostring(info.uuid or ''), name = nm}}
                break
              end
            end
          end
        end
      end
      if bestShield then
        if not dryRun then
          if DataCenter.ItemData and DataCenter.ItemData.UseTool then
            pcall(function() DataCenter.ItemData:UseTool(tonumber(bestShield.id), 1) end)
          elseif bestShield.uuid ~= '' and MsgDefines and MsgDefines.ItemUse then
            SFSNetwork.SendMessage(MsgDefines.ItemUse, {{uuid = bestShield.uuid, num = 1}})
          end
        end
        out.shield_used = bestShield
      else
        table.insert(out.alerts, 'NO_PEACE_SHIELD_IN_BAG')
      end
    end
  elseif (th.isProtected and reinfProtected) or (not th.isProtected and reinfAlly) then
    local tKey = tostring(snap.serverId) .. ':' .. tostring(th.targetPoint)
    local alreadyHave = dispatchedTargets[tKey] == true
    if not alreadyHave and MarchUtil and MarchUtil.CheckWorldPointHasMyTroop then
      local ok_chk, hasMine = pcall(function() return MarchUtil.CheckWorldPointHasMyTroop(th.targetPoint) end)
      if ok_chk and hasMine then alreadyHave = true end
    end
    if not alreadyHave and formIdx <= #usableForms then
      local f = usableForms[formIdx]
      formIdx = formIdx + 1
      if not dryRun and MarchUtil and MarchUtil.SendCreateMarchMessage then
        MarchUtil.SendCreateMarchMessage(
          f.uuid,
          MarchTargetType and MarchTargetType.ASSISTANCE_CITY or 14,
          th.targetPoint,
          tonumber(th.targetUid) or 0,
          0,
          false,
          true,
          th.targetServerId
        )
      end
      dispatchedTargets[tKey] = true
      table.insert(out.reinforcements, {{
        targetUid = th.targetUid,
        targetPoint = th.targetPoint,
        formationUuid = tostring(f.uuid),
        isProtected = th.isProtected,
        stateKey = tKey,
      }})
    end
  end
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if context is not None and isinstance(res.get("reinforcements"), list):
        ctx_targets = context.setdefault("reinforced_targets", [])
        used_uuids: list[str] = []
        for item in res["reinforcements"]:
            if not isinstance(item, dict):
                continue
            skey = item.get("stateKey")
            if skey and skey not in ctx_targets and not dry_run:
                ctx_targets.append(skey)
            if item.get("formationUuid"):
                used_uuids.append(str(item["formationUuid"]))
        if not dry_run and used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return res


def run_treasure_helicopter(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("treasure_helicopter", {})
    reserve = int(cfg.get("formation_reserve", 0))
    march_to_dig = bool(task_cfg.get("march_to_dig", True))
    auto_claim = bool(task_cfg.get("auto_claim_chat_treasures", True))
    lead_window = float(task_cfg.get("lead_window_seconds", 2.5))
    jitter_min_ms = int(task_cfg.get("jitter_min_ms", 110))
    jitter_max_ms = int(task_cfg.get("jitter_max_ms", 240))
    burst_clicks = max(1, int(task_cfg.get("burst_clicks", 6)))

    lua_scan = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local marchToDig = {str(march_to_dig).lower()}
local leadWin = {lead_window}
local snap = _get_player_snapshot()
local out = {{
  ok = true,
  task = 'treasure_helicopter',
  dry_run = dryRun,
  detected = {{}},
  marched = {{}},
  claim_ready = {{}},
  detail_requested = {{}},
}}

local seenPt = {{}}
local seenUuid = {{}}
local dm = DataCenter and DataCenter.DigTreasureDataManager
local wpm = DataCenter and DataCenter.WorldPointManager
local nowMs = snap.serverSec * 1000

local function _inspect_treasure(uuidStr, ptId, src)
  ptId = tonumber(ptId) or 0
  if ptId <= 0 then return end
  seenPt[ptId] = true
  local info = wpm and wpm.GetPointInfo and wpm:GetPointInfo(ptId) or nil
  local ti = info and info.treasureInfo or nil
  if not ti and not dryRun and MsgDefines and MsgDefines.WorldGetDetail then
    local curWorldId = (LuaEntry and LuaEntry.Player and LuaEntry.Player.GetCurWorldId and tonumber(LuaEntry.Player:GetCurWorldId())) or 0
    pcall(function() SFSNetwork.SendMessage(MsgDefines.WorldGetDetail, ptId, tonumber(snap.serverId) or 0, curWorldId, false) end)
    table.insert(out.detail_requested, ptId)
  end
  local uKey = tostring(uuidStr or (ti and ti.uuid) or (info and info.uuid) or '')
  if uKey ~= '' then
    if seenUuid[uKey] then return end
    seenUuid[uKey] = true
  end

  if ti and snap.allianceUid ~= '' and tostring(ti.allianceId or '') ~= '' and tostring(ti.allianceId) ~= snap.allianceUid then
    return
  end

  local state = ti and tonumber(ti.state or -1) or -1
  local rewardTimeMs = ti and tonumber(ti.rewardTime or 0) or 0
  local endTimeMs = ti and tonumber(ti.endTime or 0) or 0
  if rewardTimeMs > 0 and rewardTimeMs < 1e12 then rewardTimeMs = rewardTimeMs * 1000 end
  if endTimeMs > 0 and endTimeMs < 1e12 then endTimeMs = endTimeMs * 1000 end
  local rewardTime = math.floor(rewardTimeMs / 1000)
  local remSec = (rewardTime > 0 and snap.serverSec > 0) and (rewardTime - snap.serverSec) or -1
  local expired = (endTimeMs > 0 and nowMs > 0 and nowMs >= endTimeMs)
  local alreadyClaimed = (ti and ti.rewarduids and snap.uid ~= '' and tostring(ti.rewarduids):find(snap.uid, 1, true) ~= nil) and true or false

  if expired or alreadyClaimed then
    return
  end

  local entry = {{
    source = src,
    uuid = uKey,
    pointId = ptId,
    state = state,
    rewardTime = rewardTime,
    remainSec = remSec,
    inViewport = ti ~= nil,
  }}
  table.insert(out.detected, entry)

  local hasMyTroop = false
  if MarchUtil and MarchUtil.CheckWorldPointHasMyTroop then
    local ok_m, hm = pcall(function() return MarchUtil.CheckWorldPointHasMyTroop(ptId) end)
    hasMyTroop = (ok_m and hm) and true or false
  end

  if marchToDig and not hasMyTroop and state == 0 and (rewardTime == 0 or remSec > leadWin) then
    local forms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, not dryRun)
    if #forms > 0 then
      local f = forms[1]
      if not dryRun and MarchUtil and MarchUtil.SendCreateMarchMessage then
        MarchUtil.SendCreateMarchMessage(
          f.uuid,
          MarchTargetType and MarchTargetType.DIG_TREASURE or 79,
          ptId,
          tonumber(entry.uuid) or 0,
          0,
          false,
          true,
          snap.serverId
        )
      end
      table.insert(out.marched, {{pointId = ptId, uuid = entry.uuid, formationUuid = tostring(f.uuid)}})
    end
  end

  local ready = (state == 1 and not expired and not alreadyClaimed) or (state == 0 and remSec >= -30 and remSec <= leadWin) or (src == 'chat' and ti == nil and uKey ~= '')
  if ready and uKey ~= '' then
    table.insert(out.claim_ready, {{uuid = uKey, pointId = ptId, remainSec = remSec, state = state}})
  end
end

if dm and dm.activeDigTreasureForChatMsg then
  for _, item in pairs(dm.activeDigTreasureForChatMsg) do
    if type(item) == 'table' and tonumber(item.pointId or 0) > 0 then
      _inspect_treasure(item.uuid, item.pointId, 'chat')
    end
  end
end

if wpm and wpm.allViewPoints then
  for ptIdx, pt in pairs(wpm.allViewPoints) do
    local pnum = tonumber(ptIdx) or tonumber(pt and pt.pointId) or 0
    if pnum > 0 and not seenPt[pnum] then
      local info = wpm.GetPointInfo and wpm:GetPointInfo(pnum) or nil
      if info and info.treasureInfo then
        _inspect_treasure(info.uuid, pnum, 'viewport')
      end
    end
  end
end

return _enc(out)
"""
    scan_res = _eval_json(cd, pid, lua_scan, timeout=8.0)
    scan_wall_ts = time.monotonic()
    if not scan_res.get("ok"):
        return scan_res
    if not dry_run and context is not None and isinstance(scan_res.get("marched"), list):
        _record_used_formations(context, pid, [str(m.get("formationUuid")) for m in scan_res["marched"] if isinstance(m, dict) and m.get("formationUuid")])

    claimed: list[dict[str, Any]] = []
    if auto_claim and not dry_run and scan_res.get("claim_ready"):
        for target in scan_res["claim_ready"]:
            uuid_raw = target.get("uuid")
            pt_id = int(target.get("pointId") or 0)
            try:
                valid_int_uuid = int(uuid_raw) if uuid_raw is not None else 0
            except (ValueError, TypeError):
                valid_int_uuid = 0
            if valid_int_uuid <= 0:
                continue
            uuid_str = str(valid_int_uuid)
            rem = float(target.get("remainSec", -1))
            adj_rem = rem - max(0.0, time.monotonic() - scan_wall_ts)
            if 0 < adj_rem <= lead_window:
                # Coarse wait up to ~0.35s before landing, then check live server-time countdown
                wait_first = max(0.0, adj_rem - 0.35)
                if wait_first > 0.0:
                    time.sleep(wait_first)
                rem_lua = f"""
local dm = DataCenter and DataCenter.DigTreasureDataManager
local uuidStr = {json.dumps(uuid_str)}
local snap = _get_player_snapshot()
local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)
local liveRem = -1
if dm and dm.activeDigTreasureForChatMsg then
  for _, it in pairs(dm.activeDigTreasureForChatMsg) do
    if type(it) == 'table' and tostring(it.uuid or '') == uuidStr then
      local et = tonumber(it.endTime or it.digEndTime or it.finishTime or 0) or 0
      if et > 0 and et < 1e12 then et = et * 1000 end
      if et > 0 and nowMs > 0 then
        liveRem = (et - nowMs) / 1000.0
      else
        liveRem = 0
      end
      break
    end
  end
end
return _enc({{ok = true, live_rem = liveRem}})
"""
                for _poll_i in range(4):
                    r_check = _eval_json(cd, pid, rem_lua, timeout=4.0)
                    if not isinstance(r_check, dict) or not r_check.get("ok"):
                        break
                    live_rem = float(r_check.get("live_rem", -1))
                    if live_rem < 0 or live_rem <= 0.12:
                        break
                    if live_rem > lead_window:
                        break
                    time.sleep(min(0.25, max(0.05, live_rem - 0.08)))
            clicks_sent = 0
            still_active = True
            for _ in range(burst_clicks):
                click_lua = f"""
local dm = DataCenter and DataCenter.DigTreasureDataManager
local uuidStr = {json.dumps(uuid_str)}
local ptId = {pt_id}
local active = false
local sendErrs = {{}}
if dm and dm.activeDigTreasureForChatMsg then
  for _, it in pairs(dm.activeDigTreasureForChatMsg) do
    if type(it) == 'table' and tostring(it.uuid or '') == uuidStr then
      active = true
      break
    end
  end
end
if ptId > 0 and UIUtil and UIUtil.ClickAllianceTreasure then
  local okC, errC = pcall(function() UIUtil.ClickAllianceTreasure(ptId) end)
  if not okC then table.insert(sendErrs, 'ClickAllianceTreasure: ' .. tostring(errC)) end
end
if MsgDefines and MsgDefines.GetDigTreasureReward then
  local validUuid = tonumber(uuidStr)
  if validUuid and validUuid > 0 then
    local okS, errS = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.GetDigTreasureReward, validUuid)
    end)
    if not okS then table.insert(sendErrs, 'GetDigTreasureReward: ' .. tostring(errS)) end
  end
end
return _enc({{ok = true, active = active, send_errors = sendErrs}})
"""
                cres = _eval_json(cd, pid, click_lua, timeout=5.0)
                if not cres.get("ok"):
                    break
                if cres.get("send_errors"):
                    serrs = scan_res.setdefault("send_errors", [])
                    if isinstance(serrs, list):
                        for se in cres["send_errors"]:
                            if se not in serrs:
                                serrs.append(se)
                clicks_sent += 1
                still_active = bool(cres.get("active", False))
                time.sleep(random.uniform(jitter_min_ms, max(jitter_min_ms + 1, jitter_max_ms)) / 1000.0)
                if not still_active and clicks_sent >= 2:
                    break
            claimed.append(
                {
                    "uuid": uuid_str,
                    "pointId": pt_id,
                    "burst_clicks": clicks_sent,
                    "remaining_active": still_active,
                }
            )
    scan_res["claims_executed"] = claimed
    if claimed:
        try:
            dismiss_all_popups(cd, pid)
        except Exception:
            pass
    return scan_res


def _now_dt(context: dict[str, Any] | None = None) -> datetime:
    """Return current local datetime, honoring optional test injection in context."""
    override = (context or {}).get("now_dt")
    return override if isinstance(override, datetime) else datetime.now()


def _daily_state_path(context: dict[str, Any] | None = None) -> Path:
    custom = (context or {}).get("daily_state_path")
    return Path(custom) if custom else DAILY_STATE_PATH


def _client_key(client_state: dict[str, Any] | None, pid: int) -> str:
    st = client_state or {}
    return str(
        st.get("uid")
        or st.get("playerUid")
        or st.get("id")
        or st.get("account_key")
        or st.get("label")
        or pid
    )


def _load_daily_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _get_daily_count(
    context: dict[str, Any] | None,
    client_state: dict[str, Any] | None,
    pid: int,
    metric: str,
    now_dt: datetime | None = None,
) -> int:
    dt = now_dt or _now_dt(context)
    day_key = dt.strftime("%Y-%m-%d")
    mem = (context or {}).get("_daily_counts")
    key = f"{day_key}:{_client_key(client_state, pid)}:{metric}"
    if isinstance(mem, dict) and key in mem:
        return int(mem[key] or 0)
    data = _load_daily_state(_daily_state_path(context))
    return int((data.get(day_key) or {}).get(_client_key(client_state, pid), {}).get(metric, 0) or 0)


def _increment_daily_count(
    context: dict[str, Any] | None,
    client_state: dict[str, Any] | None,
    pid: int,
    metric: str,
    delta: int = 1,
    now_dt: datetime | None = None,
) -> int:
    dt = now_dt or _now_dt(context)
    day_key = dt.strftime("%Y-%m-%d")
    ckey = _client_key(client_state, pid)
    if isinstance(context, dict):
        mem = context.setdefault("_daily_counts", {})
        mkey = f"{day_key}:{ckey}:{metric}"
        mem[mkey] = int(mem.get(mkey, 0) or 0) + delta
    path = _daily_state_path(context)
    data = _load_daily_state(path)
    cutoff = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
    cleaned = {d: v for d, v in data.items() if isinstance(v, dict) and d >= cutoff}
    day_bucket = cleaned.setdefault(day_key, {})
    client_bucket = day_bucket.setdefault(ckey, {})
    client_bucket[metric] = int(client_bucket.get(metric, 0) or 0) + delta
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cleaned, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass
    return int(client_bucket[metric])


def _probe_preparedness_phase(cd: Any, pid: int, allow_network_refresh: bool = False) -> dict[str, Any]:
    """Query active Full Preparedness / Personal Arms phase, Alliance Duel (VS) phase, & incomplete Daily Quests."""
    lua = f"local allowNetworkRefresh = {str(bool(allow_network_refresh)).lower()}\n" + """
local snap = _get_player_snapshot()
local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)
local out = {
  ok = true,
  phase_names = {},
  score_labels = {},
  score_methods = {},
  vs_score_labels = {},
  vs_score_methods = {},
  daily_todo = {},
  act_id = 0,
  act_uid = "",
  theme = "",
  theme_raw = "",
  fp_cur_score = 0,
  fp_max_score = 0,
  fp_targets = {},
  fp_claimable = 0,
  perm_cur_score = 0,
  perm_max_score = 0,
  vs_open = false,
  vs_day = 0,
  vs_theme = "",
  vs_cur_score = 0,
  vs_max_score = 0,
  vs_targets = {},
  time_compe_stage = 0,
}
local loc = Localization
local function _loc(k)
  if k == nil then return '' end
  local ks = tostring(k)
  if ks == '' or ks == '0' then return '' end
  if loc and loc.GetString then
    local ok, s = pcall(function() return loc:GetString(ks) end)
    if ok and type(s) == 'string' and s ~= '' and s ~= ks then return s end
    ok, s = pcall(function() return loc.GetString(ks) end)
    if ok and type(s) == 'string' and s ~= '' and s ~= ks then return s end
  end
  return ''
end

local function _read_score(ei)
  if type(ei) ~= 'table' then return 0 end
  return math.max(
    tonumber(ei.curScore or 0) or 0,
    tonumber(ei.currentScore or 0) or 0,
    tonumber(ei.score or 0) or 0,
    tonumber(ei.duelDailyScore or 0) or 0
  )
end

local function _read_targets(ei)
  if type(ei) ~= 'table' then return {}, 0 end
  local src = (type(ei.rewardScoreIndexArr) == 'table' and #ei.rewardScoreIndexArr > 0 and ei.rewardScoreIndexArr)
    or (type(ei.targetList) == 'table' and #ei.targetList > 0 and ei.targetList) or nil
  local outT, maxT = {}, 0
  if type(src) == 'table' then
    for _, t in ipairs(src) do
      local tn = tonumber(t) or 0
      if tn > 0 then
        table.insert(outT, tn)
        if tn > maxT then maxT = tn end
      end
    end
  end
  return outT, maxT
end

local function _count_claimable(ei, targets, curScore, maxUnlockIndex)
  if type(ei) ~= 'table' or type(targets) ~= 'table' or #targets == 0 then return 0 end
  maxUnlockIndex = maxUnlockIndex or 999
  local claimedMap = {}
  if type(ei.hasRewardList) == 'table' then
    for _, rv in pairs(ei.hasRewardList) do claimedMap[tostring(rv)] = true end
  end
  if ei.newRewardFlagStr and tostring(ei.newRewardFlagStr) ~= '' then
    for part in tostring(ei.newRewardFlagStr):gmatch('[^,;|]+') do claimedMap[part] = true end
  end
  local canReceiveState = (TaskState and TaskState.CanReceive) or 1
  local cnt = 0
  for idx, tgt in ipairs(targets) do
    if idx <= maxUnlockIndex and tgt > 0 then
      local canC = false
      if ei.GetStateByScoreIndex then
        local okSt, stVal = pcall(function() return ei:GetStateByScoreIndex(tgt) end)
        if okSt and tonumber(stVal) ~= nil then
          canC = (tonumber(stVal) == canReceiveState)
        else
          canC = (curScore >= tgt and not claimedMap[tostring(idx)] and not claimedMap[tostring(tgt)])
        end
      else
        canC = (curScore >= tgt and not claimedMap[tostring(idx)] and not claimedMap[tostring(tgt)])
      end
      if canC then cnt = cnt + 1 end
    end
  end
  return cnt
end

local function _extract_methods(ei, paMgr, outLabels, outMethods)
  if type(ei) ~= 'table' then return end
  local methTbl = type(ei.getScoreMeth) == 'table' and ei.getScoreMeth or nil
  if not methTbl and paMgr and paMgr.GetScoreMeth and ei.actId then
    local ok, m = pcall(function() return paMgr:GetScoreMeth(ei.actId) end)
    if ok and type(m) == 'table' then methTbl = m end
  end
  if type(methTbl) ~= 'table' then return end
  for _, sc in pairs(methTbl) do
    if type(sc) == 'table' then
      local rawKey = tostring(sc.name or sc.tips or sc.id or '')
      local nm = _loc(sc.name)
      if nm == '' then nm = _loc(sc.tips) end
      if nm == '' then nm = _loc(sc.string) end
      if nm == '' then nm = _loc(sc.id) end
      if nm ~= '' then table.insert(outLabels, nm) end
      table.insert(outMethods, {
        id = rawKey,
        label = nm,
        type = tonumber(sc.type or 0) or 0,
        gotoType = tonumber(sc.gotoType or 0) or 0,
        points = tonumber(sc.points or sc.point or 0) or 0,
      })
    elseif type(sc) == 'string' then
      local sLoc = _loc(sc)
      if sLoc ~= '' then table.insert(outLabels, sLoc) end
      table.insert(outMethods, {id = sc, label = sLoc, type = 0, gotoType = 0, points = 0})
    end
  end
end

-- 0) Optional ActTimeCompeDataManager stage check
local atc = DataCenter and DataCenter.ActTimeCompeDataManager
if type(atc) == 'table' then
  out.time_compe_stage = tonumber(atc.stage or 0) or 0
end

-- 1) Primary live source: DataCenter.ActPersonalArmsInfo.list
local pa = DataCenter and DataCenter.ActPersonalArmsInfo
if allowNetworkRefresh and pa and SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.ActivityEventInfoGet then
  local hasEntries = false
  if type(pa.list) == 'table' then
    for _ in pairs(pa.list) do hasEntries = true; break end
  end
  if not hasEntries then
    pcall(function() SFSNetwork.SendMessage(MsgDefines.ActivityEventInfoGet, "60002") end)
  end
end
if pa and type(pa.list) == 'table' then
  local chosenEi = nil
  local chosenMaxT = -1
  for slotKey, v in pairs(pa.list) do
    local ei = type(v) == 'table' and (v.eventInfo or (v.GetEventInfo and _safe_call(function() return v:GetEventInfo() end, nil))) or nil
    if type(ei) == 'table' then
      local st = tonumber(ei.startTime or 0) or 0
      local et = tonumber(ei.endTime or 0) or 0
      if st > 0 and st < 1e12 then st = st * 1000 end
      if et > 0 and et < 1e12 then et = et * 1000 end
      local active = (st <= 0 or nowMs <= 0 or nowMs >= st) and (et <= 0 or nowMs <= 0 or nowMs <= et)
      local targets, maxT = _read_targets(ei)
      local score = _read_score(ei)
      local hasName = tostring(ei.actName or '') ~= ''
      if active then
        if not hasName and maxT > 0 and maxT <= 50 then
          -- 24h permanent chest-count bar (e.g. 60012 -> targets 2|8|18)
          out.perm_cur_score = score
          out.perm_max_score = maxT
        else
          -- Hourly rotating Full Preparedness phase (e.g. 60002 -> 8000|20000|60000)
          if not chosenEi or (hasName and tostring(chosenEi.actName or '') == '') or (maxT > chosenMaxT) then
            chosenEi = ei
            chosenMaxT = maxT
          end
        end
      end
    end
  end
  if chosenEi then
    out.act_id = tonumber(chosenEi.eventId or chosenEi.id or 0) or 0
    out.act_uid = tostring(chosenEi.actId or '')
    out.theme_raw = tostring(chosenEi.actName or '')
    local tLoc = _loc(chosenEi.actName)
    out.theme = (tLoc ~= '' and tLoc) or out.theme_raw
    if out.theme ~= '' then table.insert(out.phase_names, out.theme) end
    local targets, maxT = _read_targets(chosenEi)
    out.fp_targets = targets
    out.fp_max_score = maxT
    out.fp_cur_score = _read_score(chosenEi)
    out.fp_claimable = _count_claimable(chosenEi, targets, out.fp_cur_score, 999)
    _extract_methods(chosenEi, pa, out.score_labels, out.score_methods)
  end
end

-- 1b) Alliance Duel / VS Duel (AllianceCompeteDataManager + ActivityListDataManager "55000")
local acm = DataCenter and DataCenter.AllianceCompeteDataManager
local am = DataCenter and DataCenter.ActivityListDataManager
local vsActId = tostring((EnumActivity and EnumActivity.AllianceCompete and EnumActivity.AllianceCompete.ActId) or "55000")
local vsAct = am and ((am.GetActivityDataById and _safe_call(function() return am:GetActivityDataById(vsActId) end, nil))
  or (am.GetActivityOldDataById and _safe_call(function() return am:GetActivityOldDataById(vsActId) end, nil))) or nil
local vsOpen = false
if acm and acm.CheckIfAllianceCompeteOpen then
  local ok_vso, res_vso = pcall(function() return acm:CheckIfAllianceCompeteOpen() end)
  vsOpen = (ok_vso and res_vso) and true or false
end
local vsEi = nil
if type(vsAct) == 'table' then
  vsEi = vsAct.eventInfo or (vsAct.GetEventInfo and _safe_call(function() return vsAct:GetEventInfo() end, nil)) or nil
  if not vsOpen and type(vsEi) == 'table' then
    local st = tonumber(vsEi.startTime or 0) or 0
    local et = tonumber(vsEi.endTime or 0) or 0
    if st > 0 and st < 1e12 then st = st * 1000 end
    if et > 0 and et < 1e12 then et = et * 1000 end
    if (st <= 0 or nowMs <= 0 or nowMs >= st) and (et <= 0 or nowMs <= 0 or nowMs <= et) then
      vsOpen = true
    end
  end
end
if vsOpen then
  local rushDay = 0
  if acm and acm.GetRushDataDay then
    local ok_rd, res_rd = pcall(function() return tonumber(acm:GetRushDataDay()) or 0 end)
    if ok_rd then rushDay = res_rd end
  end
  if rushDay <= 0 and acm and acm.rushDataDay ~= nil then
    rushDay = tonumber(acm.rushDataDay) or 0
  end
  out.vs_open = true
  out.vs_day = rushDay
  local vsThemes = {
    [1] = "VS Day 1: Radar Training & Resource Gathering",
    [2] = "VS Day 2: Base Expansion & Building Upgrades",
    [3] = "VS Day 3: Age of Science & Research",
    [4] = "VS Day 4: Hero Initiative & Recruitment",
    [5] = "VS Day 5: Total Mobilization & Troop Training",
    [6] = "VS Day 6: Enemy Buster & Combat Readiness",
    [7] = "VS Day 7: War Champion",
  }
  local curTheme = vsThemes[rushDay] or ""
  if type(vsEi) == 'table' then
    local eiNameLoc = _loc(vsEi.actName)
    if eiNameLoc ~= '' then
      curTheme = curTheme ~= '' and (curTheme .. ' (' .. eiNameLoc .. ')') or eiNameLoc
    end
    local vTargets, vMax = _read_targets(vsEi)
    -- Respect unlocked box cap (3 / 6 / 9) for VS Duel target
    local maxUnlockIdx = 3
    if LuaEntry and LuaEntry.Effect and LuaEntry.Effect.GetGameEffect and EffectDefine then
      if EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_3 and _safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_3) end, 0) == 1 then
        maxUnlockIdx = 9
      elseif EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_2 and _safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_2) end, 0) == 1 then
        maxUnlockIdx = 6
      end
    end
    local effMax = vMax
    if #vTargets > 0 then
      local capIdx = math.min(#vTargets, maxUnlockIdx)
      effMax = tonumber(vTargets[capIdx]) or vMax
    end
    out.vs_targets = vTargets
    out.vs_cur_score = _read_score(vsEi)
    out.vs_max_score = effMax
    _extract_methods(vsEi, nil, out.vs_score_labels, out.vs_score_methods)
  elseif acm then
    out.vs_cur_score = tonumber(acm.curScore or acm.personalScore or (acm.GetPersonalScore and _safe_call(function() return acm:GetPersonalScore() end, 0)) or 0) or 0
    out.vs_max_score = tonumber(acm.targetScore or (acm.GetTargetScore and _safe_call(function() return acm:GetTargetScore(9) end, 0)) or 0) or 0
  end
  out.vs_theme = curTheme
  if curTheme ~= '' then
    table.insert(out.phase_names, curTheme)
    table.insert(out.vs_score_labels, curTheme)
  end
end

-- 2) Fallback: ActivityListDataManager for Full Preparedness if ActPersonalArmsInfo was empty
if am and out.act_id == 0 then
  local actInfo = nil
  local pType = ActivityType and (ActivityType.PERSONAL_ARMS or ActivityType.ActPersonalArms or ActivityType.PersonalArms) or 12
  if am.GetActivityDataById then
    actInfo = _safe_call(function() return am:GetActivityDataById("50000") end, nil)
  end
  if not actInfo and pType and am.GetActivityDataByType then
    local ok, a = pcall(function() return am:GetActivityDataByType(pType) end)
    if ok and type(a) == 'table' then actInfo = a end
  end
  if type(actInfo) == 'table' then
    out.act_id = tonumber(actInfo.id or actInfo.activityId or 0) or 0
    out.theme_raw = tostring(actInfo.activityName or actInfo.name or actInfo.title or '')
    local th = _loc(out.theme_raw)
    out.theme = (th ~= '' and th) or out.theme_raw
    if out.theme ~= '' then table.insert(out.phase_names, out.theme) end
    local aei = actInfo.eventInfo or (actInfo.GetEventInfo and _safe_call(function() return actInfo:GetEventInfo() end, nil)) or nil
    if type(aei) == 'table' then
      local targets, maxT = _read_targets(aei)
      out.fp_targets = targets
      out.fp_max_score = maxT
      out.fp_cur_score = _read_score(aei)
      _extract_methods(aei, nil, out.score_labels, out.score_methods)
    end
  end
end

-- 3) Incomplete Daily Quests (DataCenter.DailyTaskManager.dailyQuestTasks)
local dtm = DataCenter and DataCenter.DailyTaskManager
if dtm and type(dtm.dailyQuestTasks) == 'table' then
  for _, t in pairs(dtm.dailyQuestTasks) do
    if type(t) == 'table' and tonumber(t.state or 0) == 0 then
      local nm = _loc(t.name or t.desc or t.title)
      if nm ~= '' then
        table.insert(out.daily_todo, nm)
      elseif t.id then
        table.insert(out.daily_todo, 'daily:' .. tostring(t.id))
      end
    end
  end
end
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if isinstance(res, dict):
        # Python english-dialog.txt fallback in case Lua Localization missed any numeric key
        raw_theme = str(res.get("theme") or "").strip()
        theme_id = str(res.get("theme_raw") or raw_theme).strip()
        if (not raw_theme or raw_theme.isdigit()) and theme_id.isdigit():
            loc_theme = _localize_id(theme_id)
            if loc_theme and loc_theme != theme_id:
                res["theme"] = loc_theme
                pn = res.setdefault("phase_names", [])
                if isinstance(pn, list) and loc_theme not in pn:
                    pn.insert(0, loc_theme)
        for m_key, l_key in (("score_methods", "score_labels"), ("vs_score_methods", "vs_score_labels")):
            methods = res.get(m_key) or []
            labels = res.setdefault(l_key, [])
            if isinstance(methods, list) and isinstance(labels, list):
                for m in methods:
                    if isinstance(m, dict):
                        lbl = str(m.get("label") or "").strip()
                        mid = str(m.get("id") or "").strip()
                        if (not lbl or lbl.isdigit()) and mid.isdigit():
                            resolved = _localize_id(mid)
                            if resolved and resolved != mid:
                                m["label"] = resolved
                                if resolved not in labels:
                                    labels.append(resolved)
    return res


def _detect_training_event_boost(
    cd: Any,
    pid: int,
    probe: dict[str, Any] | None = None,
    allow_network_refresh: bool = False,
) -> dict[str, Any]:
    """Detect if Full Preparedness and/or Alliance Duel currently rewards Training Troops or Training Speedups."""
    pr = (
        probe
        if isinstance(probe, dict) and probe.get("ok")
        else _probe_preparedness_phase(cd, pid, allow_network_refresh=allow_network_refresh)
    )
    if not isinstance(pr, dict):
        pr = {}

    def _classify_training(theme: str, raw_id: str, methods: list[Any], labels: list[Any]) -> tuple[bool, bool]:
        m_ids = {str(m.get("id") or "").strip() for m in methods if isinstance(m, dict)}
        if raw_id:
            m_ids.add(str(raw_id).strip())
        blob = " ".join(
            [str(theme or "")]
            + [str(x or "") for x in labels]
            + [str(m.get("label") or "") for m in methods if isinstance(m, dict)]
        ).lower()

        train_ids = {"370025", "370027", "370007"}
        speed_ids = {"370002", "370005", "370034", "370037"}
        train_kws = (
            "military drill", "total mobilization", "train and assemble", "train troop",
            "troop training", "training troops", "holistic growth", "练兵", "训练士兵",
            "recruit soldier", "assemble 1 lv",
        )
        speed_kws = (
            "training speedup", "speedup on training", "use a total of",
            "use any 1-min speedup", "any speedup", "speedups", "训练加速", "通用加速",
        )
        matches_train = bool(m_ids & train_ids) or any(kw in blob for kw in train_kws)
        matches_speed = bool(m_ids & speed_ids) or any(kw in blob for kw in speed_kws)
        # Do not mis-match "Building Speedup" or "Research Speedup" alone as training speedup
        if matches_speed and not (m_ids & speed_ids):
            has_train_or_any_speed = any(
                kw in blob for kw in ("training speedup", "speedup on training", "use a total of", "use any 1-min speedup", "any speedup", "训练加速", "通用加速")
            )
            if not has_train_or_any_speed:
                matches_speed = False
        return matches_train, matches_speed

    # 1) Full Preparedness check
    fp_theme = str(pr.get("theme") or "")
    fp_raw = str(pr.get("theme_raw") or "")
    fp_methods = pr.get("score_methods") if isinstance(pr.get("score_methods"), list) else []
    fp_labels = pr.get("score_labels") if isinstance(pr.get("score_labels"), list) else []
    fp_cur = int(pr.get("fp_cur_score") or 0)
    fp_max = int(pr.get("fp_max_score") or 0)
    fp_m_train, fp_m_speed = _classify_training(fp_theme, fp_raw, fp_methods, fp_labels)
    fp_needs_points = (fp_max > 0 and fp_cur < fp_max)
    fp_zoom = bool((fp_m_train or fp_m_speed) and fp_needs_points)

    # 2) Alliance Duel / VS Duel check
    vs_open = bool(pr.get("vs_open", False))
    vs_day = int(pr.get("vs_day") or 0)
    vs_theme = str(pr.get("vs_theme") or "")
    vs_methods = pr.get("vs_score_methods") if isinstance(pr.get("vs_score_methods"), list) else []
    vs_labels = pr.get("vs_score_labels") if isinstance(pr.get("vs_score_labels"), list) else []
    vs_cur = int(pr.get("vs_cur_score") or 0)
    vs_max = int(pr.get("vs_max_score") or 0)
    vs_m_train, vs_m_speed = _classify_training(vs_theme, "", vs_methods, vs_labels)
    if vs_open and vs_day == 5:
        vs_m_train = True
        vs_m_speed = True
    vs_needs_points = vs_open and (vs_max > 0 and vs_cur < vs_max)
    vs_zoom = bool((vs_m_train or vs_m_speed) and vs_needs_points)

    reasons: list[str] = []
    if fp_zoom:
        kinds = "+".join(x for x, flg in (("Train", fp_m_train), ("Speedup", fp_m_speed)) if flg)
        reasons.append(f"Full Preparedness '{fp_theme}' [{kinds}] ({fp_cur:,}/{fp_max:,})")
    if vs_zoom:
        kinds = "+".join(x for x, flg in (("Train", vs_m_train), ("Speedup", vs_m_speed)) if flg)
        reasons.append(f"Alliance Duel Day {vs_day} '{vs_theme}' [{kinds}] ({vs_cur:,}/{vs_max:,})")

    return {
        "ok": True,
        "should_zoom": bool(fp_zoom or vs_zoom),
        "scores_on_train": bool((fp_zoom and fp_m_train) or (vs_zoom and vs_m_train)),
        "scores_on_speedup": bool((fp_zoom and fp_m_speed) or (vs_zoom and vs_m_speed)),
        "reasons": reasons,
        "fp": {
            "theme": fp_theme,
            "theme_raw": fp_raw,
            "matches_train": fp_m_train,
            "matches_speedup": fp_m_speed,
            "cur_score": fp_cur,
            "max_score": fp_max,
            "remaining": max(0, fp_max - fp_cur),
            "active_for_zoom": fp_zoom,
        },
        "vs": {
            "open": vs_open,
            "day": vs_day,
            "theme": vs_theme,
            "matches_train": vs_m_train,
            "matches_speedup": vs_m_speed,
            "cur_score": vs_cur,
            "max_score": vs_max,
            "remaining": max(0, vs_max - vs_cur),
            "active_for_zoom": vs_zoom,
        },
        "probe": pr,
    }


def _try_start_research(cd: Any, pid: int, dry_run: bool = False) -> dict[str, Any]:
    """Start an available Tech Lab research item if no research is currently running."""
    lua = f"""
local dryRun = {'true' if dry_run else 'false'}
local out = {{ok = true, action = 'none'}}
local sm = DataCenter and DataCenter.ScienceManager
local bm = DataCenter and DataCenter.BuildManager
if not sm then
  out.reason = 'no_science_manager'
  return _enc(out)
end
local busy = false
if sm.GetCurResearchingScience then
  local ok, cur = pcall(function() return sm:GetCurResearchingScience() end)
  if ok and type(cur) == 'table' and (cur.itemId or cur.scienceId or 0) ~= 0 then busy = true end
end
if busy then
  out.action = 'already_researching'
  return _enc(out)
end
local bUuid = 0
if bm and bm.GetAllBuilds then
  local ok, builds = pcall(function() return bm:GetAllBuilds() end)
  if ok and type(builds) == 'table' then
    for _, b in pairs(builds) do
      local bType = tonumber(type(b) == 'table' and (b.type or b.buildType) or 0) or 0
      if bType == (BuildingTypes and BuildingTypes.FUN_BUILD_SCIENE or 403000) or bType == 403000 then
        bUuid = tonumber(b.uuid or 0) or 0
        break
      end
    end
  end
end
local candidate = nil
if sm.GetCanResearchScienceList then
  local ok, lst = pcall(function() return sm:GetCanResearchScienceList() end)
  if ok and type(lst) == 'table' then
    for _, s in pairs(lst) do
      local sid = (type(s) == 'table' and ((tonumber(s.itemId or 0) or 0) > 0 and tonumber(s.itemId) or tonumber(s.id or 0))) or tonumber(s or 0) or 0
      if sid > 0 then candidate = sid; break end
    end
  end
elseif sm.GetScienceDic then
  local ok, dic = pcall(function() return sm:GetScienceDic() end)
  if ok and type(dic) == 'table' then
    for k, s in pairs(dic) do
      local sid = (type(s) == 'table' and ((tonumber(s.itemId or 0) or 0) > 0 and tonumber(s.itemId) or tonumber(s.id or k or 0))) or tonumber(k or 0) or 0
      local canUp = type(s) == 'table' and s.CanResearch and pcall(function() return s:CanResearch() end)
      if sid > 0 and canUp then candidate = sid; break end
    end
  end
end
if candidate and bUuid > 0 and MsgDefines and MsgDefines.ScienceResearchNew and SFSNetwork and SFSNetwork.SendMessage then
  if not dryRun then
    pcall(function()
      SFSNetwork.SendMessage(MsgDefines.ScienceResearchNew, {{itemId = candidate, useGold = 0, bUuid = bUuid, robotUuid = 0}})
    end)
  end
  out.action = 'started_research'
  out.scienceId = candidate
else
  out.action = 'no_candidate_or_lab'
  out.bUuid = bUuid
end
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=8.0)


_PREPAREDNESS_DISPATCH_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("shelter development", "shelter upgrade", "base expansion", "structure power", "building speedup", "building upgrade", "construction", "城建", "建筑", "370023", "370026", "370000", "370003", "370032", "370035"), ("build", "speed_build")),
    (("age of science", "tech power", "research speedup", "scientific research", "tech lab", "科技", "研究", "370024", "370001", "370004", "370033", "370036"), ("research", "speed_research")),
    (("military drill", "total mobilization", "troop training", "training speedup", "speedup on training", "train and assemble", "练兵", "士兵", "370025", "370005", "370007", "370037"), ("train", "speed_train")),
    (("holistic growth", "use a total of", "use any 1-min speedup", "comprehensive", "全面", "370027", "370002", "370034"), ("build", "research", "train", "speed_build", "speed_research", "speed_train")),
    (("hero progression", "hero initiative", "hero growth", "prime recruit", "basic recruit", "faction recruit", "consume 2,000 exp", "370029", "370010", "370011", "372213", "897518"), ("free_recruits",)),
    (("expert trader", "trade truck", "railway", "dispatch", "bounty", "贸易", "370028"), ("trucks", "bounties")),
    (("radar training", "radar event", "radar mission"), ("radar_events",)),
    (("boomer", "kill 1 lv", "zombie", "monster", "mutant", "boss", "370012", "370013"), ("boomer",)),
    (("gather", "mine zent", "resource", "采集", "370008", "370009", "370051"), ("gather",)),
)


def _match_preparedness_actions(probe: dict[str, Any]) -> list[str]:
    fp_methods = probe.get("score_methods") or []
    fp_method_ids = [
        str(m.get("id") or "") for m in fp_methods if isinstance(m, dict)
    ]
    fp_texts = [
        str(probe.get("theme") or ""),
        str(probe.get("theme_raw") or ""),
        *(str(x) for x in (probe.get("score_labels") or [])),
        *fp_method_ids,
    ]
    fp_blob = " ".join(fp_texts).lower()
    ordered: list[str] = []
    for keywords, tags in _PREPAREDNESS_DISPATCH_RULES:
        if any(kw in fp_blob for kw in keywords):
            for tag in tags:
                if tag not in ordered:
                    ordered.append(tag)
    # Fall back to VS Duel theme/methods only if Full Preparedness itself did not match an active theme
    if not ordered:
        vs_methods = probe.get("vs_score_methods") or []
        vs_method_ids = [
            str(m.get("id") or "") for m in vs_methods if isinstance(m, dict)
        ]
        vs_texts = [
            str(probe.get("vs_theme") or ""),
            *(str(x) for x in (probe.get("vs_score_labels") or [])),
            *vs_method_ids,
        ]
        vs_blob = " ".join(vs_texts).lower()
        for keywords, tags in _PREPAREDNESS_DISPATCH_RULES:
            if any(kw in vs_blob for kw in keywords):
                for tag in tags:
                    if tag not in ordered:
                        ordered.append(tag)
    # Only fall back if theme was completely unknown/empty (NOT when a real theme like Enemy Buster matched no safe PVE action)
    if not ordered and not str(probe.get("theme") or "").strip() and not str(probe.get("vs_theme") or "").strip():
        ordered = ["build", "train"]
    return ordered


def _run_scoped_speedup(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    category: str,
    dry_run: bool,
    context: dict[str, Any],
) -> dict[str, Any]:
    sp_cfg = dict(cfg.get("speedups") or {})
    sp_cfg["categories"] = {
        "build": category == "build",
        "research": category == "research",
        "train": category == "train",
        "heal": False,
    }
    sub_cfg = {**cfg, "speedups": sp_cfg}
    return run_speedups(cd, pid, client_state, sub_cfg, dry_run=dry_run, context=context)


def _execute_preparedness_actions(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool,
    context: dict[str, Any] | None,
    probe: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    pr = (
        probe
        if isinstance(probe, dict) and probe.get("ok")
        else _probe_preparedness_phase(cd, pid, allow_network_refresh=not dry_run)
    )
    tags = _match_preparedness_actions(pr)
    sub_ctx = dict(context or {})
    sub_ctx["_inside_preparedness"] = True
    executed: dict[str, dict[str, Any]] = {}

    action_map: dict[str, Callable[[], dict[str, Any]]] = {
        "build": lambda: run_building_upgrades(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "research": lambda: run_research_queue(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "train": lambda: run_troop_training(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "speed_build": lambda: _run_scoped_speedup(cd, pid, client_state, cfg, "build", dry_run, sub_ctx),
        "speed_research": lambda: _run_scoped_speedup(cd, pid, client_state, cfg, "research", dry_run, sub_ctx),
        "speed_train": lambda: _run_scoped_speedup(cd, pid, client_state, cfg, "train", dry_run, sub_ctx),
        "free_recruits": lambda: run_free_recruits(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "radar_events": lambda: run_radar_events(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "trucks": lambda: run_trucks(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "bounties": lambda: run_bounties(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "boomer": lambda: run_boomer_runs(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
        "gather": lambda: run_auto_gather(cd, pid, client_state, cfg, dry_run=dry_run, context=sub_ctx),
    }

    for tag in tags:
        # Skip redundant speed_train if train already zoomed through training speedups
        if tag == "speed_train" and isinstance(executed.get("train"), dict) and executed["train"].get("zoom_active"):
            continue
        fn = action_map.get(tag)
        if fn is None:
            continue
        try:
            executed[tag] = fn()
        except Exception as exc:
            executed[tag] = {"ok": False, "error": str(exc)}

    if isinstance(context, dict) and isinstance(sub_ctx.get("used_formations_by_pid"), dict):
        for k_pid, uuids in sub_ctx["used_formations_by_pid"].items():
            if isinstance(uuids, list):
                _record_used_formations(context, k_pid, [str(u) for u in uuids])
    return pr, executed


def run_full_preparedness(cd: Any, pid: int, client_state: dict[str, Any], cfg: dict[str, Any], dry_run: bool = False, context: dict[str, Any] | None = None) -> dict[str, Any]:
    fp_cfg = cfg.get("full_preparedness") or {}
    probe = _probe_preparedness_phase(cd, pid, allow_network_refresh=not dry_run)
    pre_claim = _claim_full_preparedness(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
    executed: dict[str, dict[str, Any]] = {}
    if fp_cfg.get("execute_tasks", True) and not (context or {}).get("_inside_preparedness"):
        probe, executed = _execute_preparedness_actions(cd, pid, client_state, cfg, dry_run, context, probe=probe)
    post_claim = _claim_full_preparedness(cd, pid, client_state, cfg, dry_run=dry_run, context=context) if executed else pre_claim

    # Merge pre + post claims cleanly
    out = dict(post_claim) if isinstance(post_claim, dict) else {"ok": True, "task": "full_preparedness"}
    merged_claims = list(pre_claim.get("personal_arms_claimed") or []) if isinstance(pre_claim, dict) else []
    if post_claim is not pre_claim and isinstance(post_claim, dict):
        for item in (post_claim.get("personal_arms_claimed") or []):
            if item not in merged_claims:
                merged_claims.append(item)
    out["personal_arms_claimed"] = merged_claims
    out["active_phase"] = probe
    out["executed_actions"] = executed

    # Build rich human-readable detail_lines
    detail_lines: list[str] = []
    theme_str = str(probe.get("theme") or "Unknown")
    raw_id = str(probe.get("theme_raw") or "")
    theme_disp = f"{theme_str} (#{raw_id})" if (raw_id and raw_id != theme_str) else theme_str
    fp_cur = int(probe.get("fp_cur_score") or 0)
    fp_max = int(probe.get("fp_max_score") or 0)
    vs_open = bool(probe.get("vs_open", False))
    vs_day = int(probe.get("vs_day") or 0)
    vs_cur = int(probe.get("vs_cur_score") or 0)
    vs_max = int(probe.get("vs_max_score") or 0)
    vs_part = f"VS=Day{vs_day} ({vs_cur:,}/{vs_max:,})" if vs_open else "VS=closed"
    detail_lines.append(
        f"Full Preparedness: theme='{theme_disp}' score={fp_cur:,}/{fp_max:,} "
        f"(targets={probe.get('fp_targets') or []}, actId={probe.get('act_id', 0)}, {vs_part}, checked={out.get('personal_arms_checked', 0)})"
    )
    score_lbls = [str(x) for x in (probe.get("score_labels") or []) if str(x).strip()]
    if score_lbls:
        detail_lines.append("  • Score methods: " + " | ".join(score_lbls[:6]))
    for pa in merged_claims:
        if isinstance(pa, dict):
            detail_lines.append(
                f"  • Claimed chest(s) slot={pa.get('slot')} actId={pa.get('actId')} score={pa.get('curScore')} stages={pa.get('stages')}"
            )
    if executed:
        for tag, sub in executed.items():
            if isinstance(sub, dict):
                detail_lines.append(
                    f"  • Sub-action {tag}: ok={bool(sub.get('ok'))} action={sub.get('action') or sub.get('reason') or 'done'}"
                    + (f" ({sub.get('message')})" if sub.get("message") else "")
                )
    else:
        detail_lines.append(f"  • No automated sub-actions matched theme '{theme_disp}'")
    out["detail_lines"] = detail_lines
    return out


def _claim_full_preparedness(cd: Any, pid: int, client_state: dict[str, Any], cfg: dict[str, Any], dry_run: bool = False, context: dict[str, Any] | None = None) -> dict[str, Any]:
    lua = f"""
local dryRun = {str(dry_run).lower()}
local out = {{
  ok = true,
  task = 'full_preparedness',
  dry_run = dryRun,
  personal_arms_claimed = {{}},
  personal_arms_checked = 0,
  daily_tasks_claimable = 0,
  daily_tasks_claimed = false,
  daily_boxes_claimed = {{}},
  vs_claimed_stages = {{}},
}}

local function _claim_event_info(slotKey, ei, fallbackActId, fallbackType)
  if type(ei) ~= 'table' then return end
  local actId = tostring(ei.actId or fallbackActId or '')
  local targets = (type(ei.rewardScoreIndexArr) == 'table' and #ei.rewardScoreIndexArr > 0 and ei.rewardScoreIndexArr)
    or (type(ei.targetList) == 'table' and ei.targetList) or nil
  if actId == '' or type(targets) ~= 'table' or #targets == 0 then return end
  out.personal_arms_checked = out.personal_arms_checked + 1
  local curScore = math.max(
    tonumber(ei.curScore or 0) or 0,
    tonumber(ei.currentScore or 0) or 0,
    tonumber(ei.score or 0) or 0,
    tonumber(ei.duelDailyScore or 0) or 0
  )
  local maxUnlockIndex = 999
  local acEvType = EnumActivity and EnumActivity.AllianceCompete and EnumActivity.AllianceCompete.EventType
  if acEvType ~= nil and tonumber(ei.type or -1) == tonumber(acEvType) then
    maxUnlockIndex = 3
    if LuaEntry and LuaEntry.Effect and LuaEntry.Effect.GetGameEffect and EffectDefine then
      if EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_3 and _safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_3) end, 0) == 1 then
        maxUnlockIndex = 9
      elseif EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_2 and _safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.APS_ALCOMPETE_ACT_UNLOCK_BOX_2) end, 0) == 1 then
        maxUnlockIndex = 6
      end
    end
  end
  local claimedMap = {{}}
  if type(ei.hasRewardList) == 'table' then
    for _, rv in pairs(ei.hasRewardList) do
      claimedMap[tostring(rv)] = true
    end
  end
  if ei.newRewardFlagStr and tostring(ei.newRewardFlagStr) ~= '' then
    for part in tostring(ei.newRewardFlagStr):gmatch('[^,;|]+') do
      claimedMap[part] = true
    end
  end
  local canReceiveState = (TaskState and TaskState.CanReceive) or 1
  local claimableStages = {{}}
  for idx, tgt in ipairs(targets) do
    if idx <= maxUnlockIndex then
      local tgtNum = tonumber(tgt) or 0
      if tgtNum > 0 then
        local canClaim = false
        if ei.GetStateByScoreIndex then
          local okSt, stVal = pcall(function() return ei:GetStateByScoreIndex(tgt) end)
          if okSt and tonumber(stVal) ~= nil then
            canClaim = (tonumber(stVal) == canReceiveState)
          else
            canClaim = (curScore >= tgtNum and not claimedMap[tostring(idx)] and not claimedMap[tostring(tgtNum)])
          end
        else
          canClaim = (curScore >= tgtNum and not claimedMap[tostring(idx)] and not claimedMap[tostring(tgtNum)])
        end
        if canClaim then
          -- AcceptPersonalRewardBatch.StagesToPersonalIndexes matches stage against rewardScoreIndexArr values (score thresholds)
          table.insert(claimableStages, tgtNum)
        end
      end
    end
  end
  if not dryRun and #claimableStages > 0 and SFSNetwork and SFSNetwork.SendMessage and MsgDefines then
    local evType = tonumber(ei.type or fallbackType or 1) or 1
    local ac = DataCenter and DataCenter.ActivityController
    if ac and ac.SendActivityGetRewardBatchCommand then
      pcall(function() ac:SendActivityGetRewardBatchCommand(actId, claimableStages, evType) end)
    elseif MsgDefines.AcceptPersonalRewardBatch then
      pcall(function()
        SFSNetwork.SendMessage(MsgDefines.AcceptPersonalRewardBatch, {{
          actId = actId,
          eventType = evType,
          stages = claimableStages,
        }})
      end)
    elseif MsgDefines.AcceptPersonalReward then
      for _, stg in ipairs(claimableStages) do
        pcall(function()
          SFSNetwork.SendMessage(MsgDefines.AcceptPersonalReward, {{
            actId = actId,
            stage = stg,
            eventType = evType,
          }})
        end)
      end
    end
  end
  if #claimableStages > 0 then
    table.insert(out.personal_arms_claimed, {{
      slot = tostring(slotKey),
      actId = actId,
      curScore = curScore,
      stages = claimableStages,
    }})
  end
end

local pa = DataCenter and DataCenter.ActPersonalArmsInfo
if pa then
  if type(pa.list) == 'table' then
    for k, v in pairs(pa.list) do
      local ei = type(v) == 'table' and (v.eventInfo or (v.GetEventInfo and _safe_call(function() return v:GetEventInfo() end, nil))) or nil
      _claim_event_info(k, ei, v and v.actId, 1)
    end
  end
  if pa.GetPermanentAct then
    local perm = _safe_call(function() return pa:GetPermanentAct() end, nil)
    local pei = type(perm) == 'table' and (perm.eventInfo or (perm.GetEventInfo and _safe_call(function() return perm:GetEventInfo() end, nil))) or nil
    _claim_event_info('permanent_24h', pei, perm and perm.actId, 3)
  end
end

-- 3) Alliance Compete (VS Duel) Stage Rewards (Stages 1 through 9) via ActivityListDataManager("55000")
local am = DataCenter and DataCenter.ActivityListDataManager
local vsActId = tostring((EnumActivity and EnumActivity.AllianceCompete and EnumActivity.AllianceCompete.ActId) or "55000")
local vsAct = am and ((am.GetActivityDataById and _safe_call(function() return am:GetActivityDataById(vsActId) end, nil)) or (am.GetActivityOldDataById and _safe_call(function() return am:GetActivityOldDataById(vsActId) end, nil))) or nil
if type(vsAct) == 'table' then
  local vsEi = vsAct.eventInfo or (vsAct.GetEventInfo and _safe_call(function() return vsAct:GetEventInfo() end, nil)) or nil
  local realVsActId = tostring(vsAct.activityId or vsAct.id or (vsEi and vsEi.actId) or vsActId)
  if type(vsEi) == 'table' then
    local beforeCnt = #out.personal_arms_claimed
    _claim_event_info('vs_duel', vsEi, realVsActId, tonumber(vsEi.type or 2) or 2)
    if #out.personal_arms_claimed > beforeCnt then
      local lastClaim = out.personal_arms_claimed[#out.personal_arms_claimed]
      out.vs_claimed_stages = lastClaim.stages or {{}}
    end
  end
end

if #out.personal_arms_claimed > 0 then
  pcall(_dismiss_modal_dialogs)
end
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=8.0)


def _resolve_theme_speedup_categories(
    probe: dict[str, Any] | None,
    configured_cats: dict[str, Any],
) -> tuple[dict[str, bool], str, list[str]]:
    """Intersect configured speedup categories with the active Full Preparedness / Alliance Duel theme.
    Prevents burning Build/Train speedups during research-only themes like Age of Science."""
    base = {
        "build": bool(configured_cats.get("build", True)),
        "research": bool(configured_cats.get("research", True)),
        "train": bool(configured_cats.get("train", True)),
        "heal": bool(configured_cats.get("heal", True)),
    }
    if not isinstance(probe, dict) or not probe.get("ok"):
        return base, "", []
    theme_name = str(probe.get("theme") or probe.get("vs_theme") or "").strip()
    matched = _match_preparedness_actions(probe)
    # If neither FP nor VS reported any recognizable theme text or score labels, do not block configured cats
    has_theme_signal = bool(
        theme_name
        or (probe.get("score_labels") or [])
        or (probe.get("vs_score_labels") or [])
        or (probe.get("score_methods") or [])
    )
    if not has_theme_signal:
        return base, "", matched
    allowed = {
        "build": base["build"] and ("speed_build" in matched),
        "research": base["research"] and ("speed_research" in matched),
        "train": base["train"] and ("speed_train" in matched),
        "heal": False,
    }
    return allowed, theme_name, matched


def run_speedups(cd: Any, pid: int, client_state: dict[str, Any], cfg: dict[str, Any], dry_run: bool = False, context: dict[str, Any] | None = None) -> dict[str, Any]:
    task_cfg = cfg.get("speedups", {})
    use_free = bool(task_cfg.get("use_free_speed", True))
    collect_finished = bool(task_cfg.get("collect_finished", True))
    use_items = bool(task_cfg.get("use_items", False))
    align_arms = bool(task_cfg.get("align_with_preparedness", True))
    ignore_theme = bool(task_cfg.get("ignore_theme_filter", False)) or bool((context or {}).get("_inside_preparedness"))
    reserve_sec = int(task_cfg.get("reserve_minutes", 120)) * 60
    max_items = int(task_cfg.get("max_items_per_cycle", 5))
    cats = dict(task_cfg.get("categories") or {})

    active_theme = ""
    matched_theme_tags: list[str] = []
    theme_skip_reason = ""
    if use_items and align_arms and not ignore_theme:
        probe = _probe_preparedness_phase(cd, pid, allow_network_refresh=not dry_run)
        cats, active_theme, matched_theme_tags = _resolve_theme_speedup_categories(probe, cats)
        if not any(cats.values()):
            use_items = False
            theme_skip_reason = (
                f"Active theme '{active_theme or 'current phase'}' does not score any enabled speedup category "
                f"(matched={matched_theme_tags}); skipping item speedups."
            )

    lua = f"""
local dryRun = {str(dry_run).lower()}
local useFree = {str(use_free).lower()}
local collectFin = {str(collect_finished).lower()}
local useItems = {str(use_items).lower()}
local alignArms = {str(align_arms).lower()}
local reserveSec = {reserve_sec}
local maxItems = {max_items}
local catBuild = {str(bool(cats.get("build", True))).lower()}
local catResearch = {str(bool(cats.get("research", True))).lower()}
local catTrain = {str(bool(cats.get("train", True))).lower()}
local catHeal = {str(bool(cats.get("heal", True))).lower()}

local snap = _get_player_snapshot()
local nowMs = snap.serverSec * 1000
local out = {{
  ok = true,
  task = 'speedups',
  dry_run = dryRun,
  finished_collected = {{}},
  free_speeds = {{}},
  item_speeds = {{}},
  arms_ready = true,
}}

local bm = DataCenter and DataCenter.BuildManager
local am = DataCenter and DataCenter.ArmyManager
local qm = DataCenter and DataCenter.QueueDataManager
local idata = DataCenter and DataCenter.ItemData

if collectFin then
  if bm and bm.GetAllBuildings and bm.CheckSendBuildFinish then
    for _, b in pairs(bm:GetAllBuildings() or {{}}) do
      if b and b.uuid then
        local fin = (bm.IsUpgradeFinish and bm:IsUpgradeFinish(b.uuid)) or (tonumber(b.state or 0) == 1 and tonumber(b.updateTime or 0) > 0 and nowMs > 0 and tonumber(b.updateTime) <= nowMs)
        if fin then
          if not dryRun then pcall(function() bm:CheckSendBuildFinish(b.uuid, false, true) end) end
          table.insert(out.finished_collected, {{kind = 'build', uuid = tostring(b.uuid), itemId = b.itemId}})
        end
      end
    end
  end
  if am and am.GetArmyQueue and am.CheckSendFinish then
    for _, qt in ipairs({{1, 8, 9}}) do
      local q = am:GetArmyQueue(qt)
      if q and q.uuid and (tonumber(q.state or 0) == 3 or (tonumber(q.endTime or 0) > 0 and nowMs > 0 and tonumber(q.endTime) <= nowMs)) then
        if not dryRun then pcall(function() am:CheckSendFinish(qt) end) end
        table.insert(out.finished_collected, {{kind = 'army_queue', qType = qt, uuid = tostring(q.uuid)}})
      end
    end
  end
  if qm and qm.queueDic then
    for _, q in pairs(qm.queueDic) do
      if q and q.uuid then
        local st = tonumber(q.state or 0)
        local fin = (st == 3) or (st == 2 and tonumber(q.endTime or 0) > 0 and nowMs > 0 and tonumber(q.endTime) <= nowMs)
        if fin and MsgDefines and MsgDefines.QueueFinish then
          if not dryRun then SFSNetwork.SendMessage(MsgDefines.QueueFinish, {{uuid = q.uuid}}) end
          table.insert(out.finished_collected, {{kind = 'queue', qType = tonumber(q.type or 0), uuid = tostring(q.uuid)}})
        end
      end
    end
  end
end

if useFree and bm and bm.GetAllBuildings and bm.CheckSendFreeSpeed then
  for _, b in pairs(bm:GetAllBuildings() or {{}}) do
    local isUpg = b and b.uuid and ((bm.IsUpgrading and bm:IsUpgrading(b.uuid)) or (tonumber(b.state or 0) == 1 and tonumber(b.updateTime or 0) > nowMs))
    if isUpg then
      local bId = tonumber(b.itemId or 0) or 0
      local freeTime = (bId > 0 and BuildingUtils and BuildingUtils.GetDroneFreeTimeForBuild and (tonumber(_safe_call(function() return BuildingUtils.GetDroneFreeTimeForBuild(bId) end, 0)) or 0)) or 0
      if freeTime <= 0 then freeTime = 300 end
      local remSec = (tonumber(b.updateTime or 0) - nowMs) / 1000
      if remSec > 0 and remSec <= freeTime then
        if not dryRun then pcall(function() bm:CheckSendFreeSpeed(b.uuid) end) end
        table.insert(out.free_speeds, {{kind = 'build', uuid = tostring(b.uuid), remSec = math.floor(remSec)}})
      end
    end
  end
end

local maxSecNeeded = 999999
if alignArms then
  out.arms_ready = false
  local neededPts = 0
  local hasActiveEvent = false

  local function _check_event_targets(ei)
    if type(ei) ~= 'table' then return end
    local targets = (type(ei.rewardScoreIndexArr) == 'table' and #ei.rewardScoreIndexArr > 0 and ei.rewardScoreIndexArr)
      or (type(ei.targetList) == 'table' and #ei.targetList > 0 and ei.targetList) or nil
    if not targets then return end
    local st = tonumber(ei.startTime or 0) or 0
    local et = tonumber(ei.endTime or 0) or 0
    if st > 0 and st < 1e12 then st = st * 1000 end
    if et > 0 and et < 1e12 then et = et * 1000 end
    local active = (st <= 0 or nowMs <= 0 or nowMs >= st) and (et <= 0 or nowMs <= 0 or nowMs <= et)
    if not active then return end
    hasActiveEvent = true
    local curScore = math.max(
      tonumber(ei.curScore or 0) or 0,
      tonumber(ei.currentScore or 0) or 0,
      tonumber(ei.score or 0) or 0
    )
    local lastChest = tonumber(targets[#targets]) or 0
    -- Prefer rotating hourly FP score target (e.g. 60,000) over the 24h permanent chest bar (2/8/18)
    if lastChest >= (tonumber(out.fp_last_chest or 0) or 0) then
      out.fp_cur_score = curScore
      out.fp_last_chest = lastChest
    end
    if lastChest > 0 and curScore < lastChest then
      local diff = lastChest - curScore
      if diff > neededPts then neededPts = diff end
      out.arms_ready = true
    end
  end

  -- 1) Full Preparedness (ActPersonalArmsInfo + 24h Permanent Bar)
  local pa = DataCenter and DataCenter.ActPersonalArmsInfo
  if pa then
    if type(pa.list) == 'table' then
      for _, v in pairs(pa.list) do
        local ei = type(v) == 'table' and (v.eventInfo or (v.GetEventInfo and _safe_call(function() return v:GetEventInfo() end, nil))) or nil
        _check_event_targets(ei)
      end
    end
    if pa.GetPermanentAct then
      local perm = _safe_call(function() return pa:GetPermanentAct() end, nil)
      local pei = type(perm) == 'table' and (perm.eventInfo or (perm.GetEventInfo and _safe_call(function() return perm:GetEventInfo() end, nil))) or nil
      _check_event_targets(pei)
    end
  end

  -- 2) VS Duel (ActivityListDataManager "55000" + AllianceCompeteDataManager)
  local acm = DataCenter and DataCenter.AllianceCompeteDataManager
  local am = DataCenter and DataCenter.ActivityListDataManager
  local vsActId = tostring((EnumActivity and EnumActivity.AllianceCompete and EnumActivity.AllianceCompete.ActId) or "55000")
  local vsAct = am and ((am.GetActivityDataById and _safe_call(function() return am:GetActivityDataById(vsActId) end, nil)) or (am.GetActivityOldDataById and _safe_call(function() return am:GetActivityOldDataById(vsActId) end, nil))) or nil
  if type(vsAct) == 'table' then
    local vsEi = vsAct.eventInfo or (vsAct.GetEventInfo and _safe_call(function() return vsAct:GetEventInfo() end, nil)) or nil
    if type(vsEi) == 'table' then
      local targets = (type(vsEi.rewardScoreIndexArr) == 'table' and #vsEi.rewardScoreIndexArr > 0 and vsEi.rewardScoreIndexArr)
        or (type(vsEi.targetList) == 'table' and #vsEi.targetList > 0 and vsEi.targetList) or nil
      if targets then
        hasActiveEvent = true
        local vsCur = tonumber(vsEi.curScore or vsEi.currentScore or vsEi.score or 0) or 0
        local vsLastChest = tonumber(targets[#targets]) or 0
        out.vs_cur_score = vsCur
        out.vs_last_chest = vsLastChest
        if vsLastChest > 0 and vsCur < vsLastChest then
          local vsDiff = vsLastChest - vsCur
          if vsDiff > neededPts then neededPts = vsDiff end
          out.arms_ready = true
        end
      end
    end
  elseif acm then
    local vsOpen = false
    if acm.CheckIfAllianceCompeteOpen then
      local ok_vo, r_vo = pcall(function() return acm:CheckIfAllianceCompeteOpen() end)
      vsOpen = ok_vo and r_vo
    end
    if vsOpen then
      hasActiveEvent = true
      local vsCur = tonumber(acm.curScore or acm.personalScore or (acm.GetPersonalScore and acm:GetPersonalScore()) or 0) or 0
      local vsLastChest = tonumber(acm.targetScore or (acm.GetTargetScore and acm:GetTargetScore(9)) or (acm.GetTargetScore and acm:GetTargetScore()) or 0) or 0
      out.vs_cur_score = vsCur
      out.vs_last_chest = vsLastChest
      if vsLastChest > 0 and vsCur < vsLastChest then
        local vsDiff = vsLastChest - vsCur
        if vsDiff > neededPts then neededPts = vsDiff end
        out.arms_ready = true
      end
    end
  end

  -- If events are running but the player already reached the last chest on all of them, STOP speedups
  if hasActiveEvent and not out.arms_ready then
    out.action = 'already_at_last_chest'
    out.reason = 'All active events (Full Preparedness / VS Duel) have already reached their final chest target. Zero speedups needed.'
  elseif not hasActiveEvent then
    out.arms_ready = false
    out.action = 'no_active_event'
  end

  -- Calculate the exact duration of speedups to reach the last chest target
  if neededPts > 0 then
    local ptsPerMin = 40
    local minutesNeeded = math.ceil(neededPts / ptsPerMin)
    maxSecNeeded = math.max(60, minutesNeeded * 60)
    out.points_needed = neededPts
    out.max_speedup_sec_allowed = maxSecNeeded
  end
end

if useItems and out.arms_ready and idata and idata.FindBestSpeedCombination and idata.GetSpeedItemTotalTime then
  local usedCount = 0
  local function _apply_speed(kind, targetUuid, menuId, endTimeMs, isBuild)
    if usedCount >= maxItems then return end
    local remSec = math.floor((tonumber(endTimeMs or 0) - nowMs) / 1000)
    if remSec <= 60 then return end
    local totalAvail = tonumber(idata:GetSpeedItemTotalTime(menuId)) or 0
    if (totalAvail - reserveSec) < 60 then return end
    local capSec = math.min(remSec, maxSecNeeded)
    local needSec = math.min(capSec, totalAvail - reserveSec)
    if needSec <= 0 then return end
    local combo = idata:FindBestSpeedCombination(menuId, needSec)
    if type(combo) ~= 'table' or #combo == 0 then return end
    local parts = {{}}
    local batchItems = 0
    for _, entry in ipairs(combo) do
      local cnt = math.min(tonumber(entry.count or 0) or 0, maxItems - usedCount - batchItems)
      if cnt > 0 and entry.itemId then
        table.insert(parts, tostring(entry.itemId) .. ';' .. tostring(cnt))
        batchItems = batchItems + cnt
      end
      if usedCount + batchItems >= maxItems then break end
    end
    if #parts == 0 then return end
    local itemStr = table.concat(parts, '|')
    if not dryRun then
      if isBuild and MsgDefines and MsgDefines.BuildCcdMNew then
        SFSNetwork.SendMessage(MsgDefines.BuildCcdMNew, {{
          bUUID = targetUuid,
          isFixRuins = false,
          itemIDs = itemStr,
          golloesSpeedTime = 0,
          useGold = false,
        }})
      elseif not isBuild and MsgDefines and MsgDefines.QueueCcdMNew then
        SFSNetwork.SendMessage(MsgDefines.QueueCcdMNew, {{
          qUUID = targetUuid,
          itemIDs = itemStr,
          isGold = 0,
          golloesSpeedTime = 0,
        }})
      end
    end
    usedCount = usedCount + batchItems
    table.insert(out.item_speeds, {{kind = kind, uuid = tostring(targetUuid), itemIDs = itemStr, count = batchItems}})
  end

  if catBuild and bm and bm.GetAllBuildings then
    for _, b in pairs(bm:GetAllBuildings() or {{}}) do
      local isUpg = b and b.uuid and ((bm.IsUpgrading and bm:IsUpgrading(b.uuid)) or (tonumber(b.state or 0) == 1 and tonumber(b.updateTime or 0) > nowMs))
      if isUpg then
        _apply_speed('build', b.uuid, 7, b.updateTime, true)
        break
      end
    end
  end
  if qm and qm.queueDic then
    for _, q in pairs(qm.queueDic) do
      if q and q.uuid and tonumber(q.state or 0) == 2 and usedCount < maxItems then
        local qt = tonumber(q.type or 0)
        if catResearch and qt == 6 then
          _apply_speed('research', q.uuid, 6, q.endTime, false)
        elseif catTrain and (qt == 1 or qt == 8 or qt == 9) then
          _apply_speed('train', q.uuid, 3, q.endTime, false)
        elseif catHeal and (qt == 3 or qt == 46) then
          _apply_speed('heal', q.uuid, 4, q.endTime, false)
        end
      end
    end
  end
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if isinstance(res, dict):
        if active_theme:
            res["active_theme"] = active_theme
            res["allowed_speedup_categories"] = [k for k, v in cats.items() if v]
        if theme_skip_reason:
            res["action"] = "skipped_off_theme"
            res["reason"] = theme_skip_reason
    return res


def run_troop_training(cd: Any, pid: int, client_state: dict[str, Any], cfg: dict[str, Any], dry_run: bool = False, context: dict[str, Any] | None = None) -> dict[str, Any]:
    task_cfg = cfg.get("troop_training", {}) or {}
    collect_finished = bool(task_cfg.get("collect_finished", True))
    train_highest = bool(task_cfg.get("train_highest_tier", True))
    barracks = list(task_cfg.get("barracks", ["CarSoldier", "FootSoldier", "BowSoldier"]))
    batch_override = int(task_cfg.get("batch_count", 0) or 0)
    event_speed_zoom = bool(task_cfg.get("event_speed_zoom", True))
    max_zoom_batches = int(task_cfg.get("max_zoom_batches", 50) or 50)
    zoom_use_universal = bool(task_cfg.get("zoom_use_universal_speedups", False))

    barrack_entries = []
    for name in barracks:
        meta = BARRACKS_CONFIG.get(name)
        if meta:
            barrack_entries.append(f"{{name={json.dumps(name)},qt={meta['queue_type']},bid={meta['building_id']}}}")
    barracks_lua = "{" + ",".join(barrack_entries) + "}"

    def _run_barrack_sweep(is_dry: bool) -> dict[str, Any]:
        lua_sweep = f"""
local dryRun = {str(is_dry).lower()}
local collectFin = {str(collect_finished).lower()}
local trainHigh = {str(train_highest).lower()}
local batchOverride = {batch_override}
local barracks = {barracks_lua}

local snap = _get_player_snapshot()
local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)
local out = {{
  ok = true,
  task = 'troop_training',
  dry_run = dryRun,
  collected = {{}},
  trained = {{}},
  busy = {{}},
  remaining_cap = 0,
  train_speedup_sec = 0,
  universal_speedup_sec = 0,
  speedup_items = {{}},
}}

local am = DataCenter and DataCenter.ArmyManager
local bm = DataCenter and DataCenter.BuildManager
local qm = DataCenter and DataCenter.QueueDataManager
local idata = DataCenter and DataCenter.ItemData
local itpl = DataCenter and DataCenter.ItemTemplateManager
if not am then
  out.ok = false
  out.error = 'ArmyManager unavailable'
  return _enc(out)
end

-- Inventory scan: dynamically verify all Training Speedups (type=2, type2=3: 200230..200235+) & Universal (type=2, type2=1)
if idata and type(idata.ItemInfos) == 'table' then
  for k, it in pairs(idata.ItemInfos) do
    if type(it) == 'table' then
      local iid = tonumber(it.itemId or it.id or k) or 0
      local cnt = tonumber(it.count or it.num or 0) or 0
      if cnt > 0 and iid > 0 then
        local tpl = itpl and itpl.GetItemTemplate and _safe_call(function() return itpl:GetItemTemplate(iid) end, nil)
        local t1 = tpl and tonumber(tpl.type or 0) or 0
        local t2 = tpl and tonumber(tpl.type2 or 0) or 0
        if t1 == 2 and (t2 == 3 or t2 == 1) then
          local sec = 0
          local paraStr = tostring((tpl and tpl.para) or '')
          local p3 = paraStr:match(';%d+;(%d+)$') or paraStr:match('(%d+)$')
          sec = tonumber(p3 or 0) or 0
          if sec <= 0 and tpl and tpl.para1 then
            local numP, unitP = tostring(tpl.para1):match('(%d+);([mhds])')
            local np = tonumber(numP or 0) or 0
            if unitP == 'm' then sec = np * 60
            elseif unitP == 'h' then sec = np * 3600
            elseif unitP == 'd' then sec = np * 86400
            elseif unitP == 's' then sec = np end
          end
          if sec > 0 then
            if t2 == 3 then
              out.train_speedup_sec = out.train_speedup_sec + (sec * cnt)
            elseif t2 == 1 then
              out.universal_speedup_sec = out.universal_speedup_sec + (sec * cnt)
            end
            table.insert(out.speedup_items, {{id = iid, count = cnt, sec = sec, kind = (t2 == 3 and 'train' or 'universal')}})
          end
        end
      end
    end
  end
  table.sort(out.speedup_items, function(a, b)
    if a.kind ~= b.kind then return a.kind == 'train' end
    return a.sec > b.sec
  end)
end

local maxArmy = tonumber((am.GetArmyNumMax and _safe_call(function() return am:GetArmyNumMax() end, 0)) or 0) or 0
local curArmy = tonumber((am.GetTotalArmyNum and _safe_call(function() return am:GetTotalArmyNum() end, 0)) or 0) or 0
local maxReserve = tonumber((am.GetReserveArmyMax and _safe_call(function() return am:GetReserveArmyMax() end, 0)) or 0) or 0
local curReserve = tonumber((am.GetReserveArmyNum and _safe_call(function() return am:GetReserveArmyNum() end, 0)) or 0) or 0

local remainingCap = 999999
if maxArmy > 0 or maxReserve > 0 then
  local left = maxArmy - curArmy
  local reserveLeft = maxReserve - curReserve
  remainingCap = math.max(0, left) + math.max(0, reserveLeft)
end
out.remaining_cap = remainingCap

for _, br in ipairs(barracks) do
  local q = am.GetArmyQueue and _safe_call(function() return am:GetArmyQueue(br.qt) end, nil) or nil
  local qState = q and tonumber(q.state or 0) or 0
  local qEnd = q and tonumber(q.endTime or 0) or 0
  if qEnd > 0 and qEnd < 1e12 then qEnd = qEnd * 1000 end
  local isFin = (q ~= nil) and (qState == 3 or (qState == 2 and qEnd > 0 and nowMs > 0 and qEnd <= nowMs))
  local collectedNow = false
  if isFin and collectFin then
    if not dryRun then
      local okF = false
      if am.CheckSendFinish then okF = pcall(function() am:CheckSendFinish(br.qt) end) end
      if not okF and q.uuid and SFSNetwork and MsgDefines and MsgDefines.QueueFinish then
        pcall(function() SFSNetwork.SendMessage(MsgDefines.QueueFinish, {{uuid = q.uuid}}) end)
      end
    end
    collectedNow = true
    table.insert(out.collected, {{barrack = br.name, qType = br.qt, uuid = tostring(q.uuid or '')}})
  end

  local isIdle = (q == nil) or (qState == 0) or (collectedNow and not dryRun)
  if isIdle and trainHigh and remainingCap > 0 then
    local tmpl = am.GetMaxLevelSoliderByBuildingId and _safe_call(function() return am:GetMaxLevelSoliderByBuildingId(br.bid) end, nil) or nil
    local armyId = tmpl and (type(tmpl) == 'table' and (tmpl.id or tmpl.armyId) or tmpl) or nil
    local maxTrain = (type(tmpl) == 'table' and tonumber(tmpl.max_train or 0)) or 0
    if not armyId and am.GetMaxUnLockId then
      local candId = tonumber(_safe_call(function() return am:GetMaxUnLockId(br.bid, true) end, 0) or 0) or 0
      if candId >= 1000 then armyId = candId end
    end
    if not armyId and am.allArmy then
      local targetType = (br.qt == 1 and 3) or (br.qt == 8 and 1) or (br.qt == 9 and 2) or 0
      local bestLv = 0
      for aid, a in pairs(am.allArmy) do
        if type(a) == 'table' then
          local atype = tonumber(a.type or a.armyType or 0) or 0
          local alv = tonumber(a.level or a.lv or a.tier or 0) or 0
          if (targetType == 0 or atype == targetType) and alv > bestLv then
            bestLv = alv
            armyId = a.id or a.armyId or aid
          end
        end
      end
    end

    if armyId and tostring(armyId) ~= '' then
      local aInfo = am.FindArmy and _safe_call(function() return am:FindArmy(tostring(armyId)) end, nil) or nil
      local batchCnt = batchOverride > 0 and batchOverride or (aInfo and tonumber(aInfo.train or 0) or 0)
      if batchCnt <= 0 then batchCnt = maxTrain > 0 and maxTrain or 200 end
      if batchCnt <= 0 then batchCnt = 100 end
      batchCnt = math.min(batchCnt, remainingCap)
      if batchCnt > 0 then
        if not dryRun then
          local sent = false
          if MsgDefines and MsgDefines.ArmyAdd and SFSNetwork and SFSNetwork.SendMessage then
            sent = pcall(function()
              SFSNetwork.SendMessage(MsgDefines.ArmyAdd, {{
                id = tostring(armyId),
                gold = false,
                num = math.floor(batchCnt),
              }})
            end)
          end
          if not sent and am.SendArmyAdd then
            pcall(function() am:SendArmyAdd(tostring(armyId), math.floor(batchCnt), false) end)
          end
        end
        remainingCap = remainingCap - batchCnt
        table.insert(out.trained, {{barrack = br.name, qType = br.qt, armyId = tostring(armyId), count = math.floor(batchCnt)}})
      end
    end
  elseif not isIdle then
    local remSec = (qEnd > nowMs) and math.ceil((qEnd - nowMs) / 1000) or 0
    local qtyMatch = tostring(q.itemId or ''):match(';(%d+);')
    table.insert(out.busy, {{
      barrack = br.name,
      qType = br.qt,
      uuid = tostring(q.uuid or ''),
      state = qState,
      endTime = qEnd,
      remSec = remSec,
      itemId = tostring(q.itemId or ''),
      count = tonumber(qtyMatch or q.num or 0) or 0,
    }})
  end
end

return _enc(out)
"""
        return _eval_json(cd, pid, lua_sweep, timeout=10.0)

    def _run_zoom_speedup_step(allow_partial: bool) -> dict[str, Any]:
        """Speed up the shortest active barracks training queue with exact non-overshooting training speedups."""
        lua_zoom = f"""
local useUniversal = {str(zoom_use_universal).lower()}
local allowPartial = {str(allow_partial).lower()}
local barracks = {barracks_lua}
local snap = _get_player_snapshot()
local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)
local am = DataCenter and DataCenter.ArmyManager
local idata = DataCenter and DataCenter.ItemData
local itpl = DataCenter and DataCenter.ItemTemplateManager
local out = {{
  ok = true,
  applied = false,
  reason = 'none',
  barrack = '',
  qType = 0,
  uuid = '',
  troop_count = 0,
  rem_sec_before = 0,
  applied_sec = 0,
  finished_queue = false,
  itemIDs = '',
  avail_sec = 0,
}}
if not am or not idata then
  out.ok = false
  out.reason = 'managers_unavailable'
  return _enc(out)
end

-- Gather active training queues across configured barracks; pick shortest remaining queue for fastest batch turnover
local bestQ = nil
for _, br in ipairs(barracks) do
  local q = am.GetArmyQueue and _safe_call(function() return am:GetArmyQueue(br.qt) end, nil) or nil
  if type(q) == 'table' and q.uuid and tonumber(q.state or 0) == 2 then
    local qEnd = tonumber(q.endTime or 0) or 0
    if qEnd > 0 and qEnd < 1e12 then qEnd = qEnd * 1000 end
    local remSec = math.max(0, math.ceil((qEnd - nowMs) / 1000))
    if remSec > 0 then
      local qtyMatch = tostring(q.itemId or ''):match(';(%d+);')
      local cand = {{
        barrack = br.name, qType = br.qt, uuid = q.uuid, remSec = remSec,
        count = tonumber(qtyMatch or q.num or 0) or 0,
      }}
      if not bestQ or cand.remSec < bestQ.remSec then bestQ = cand end
    end
  end
end
if not bestQ then
  out.reason = 'no_active_training_queue'
  return _enc(out)
end

-- Discover live training speedups (type=2, type2=3) + optional universal (type=2, type2=1)
local pool = {{}}
local totalAvail = 0
if type(idata.ItemInfos) == 'table' then
  for k, it in pairs(idata.ItemInfos) do
    if type(it) == 'table' then
      local iid = tonumber(it.itemId or it.id or k) or 0
      local cnt = tonumber(it.count or it.num or 0) or 0
      if cnt > 0 and iid > 0 then
        local tpl = itpl and itpl.GetItemTemplate and _safe_call(function() return itpl:GetItemTemplate(iid) end, nil)
        local t1 = tpl and tonumber(tpl.type or 0) or 0
        local t2 = tpl and tonumber(tpl.type2 or 0) or 0
        if t1 == 2 and (t2 == 3 or (useUniversal and t2 == 1)) then
          local paraStr = tostring((tpl and tpl.para) or '')
          local p3 = paraStr:match(';%d+;(%d+)$') or paraStr:match('(%d+)$')
          local sec = tonumber(p3 or 0) or 0
          if sec <= 0 and tpl and tpl.para1 then
            local numP, unitP = tostring(tpl.para1):match('(%d+);([mhds])')
            local np = tonumber(numP or 0) or 0
            if unitP == 'm' then sec = np * 60
            elseif unitP == 'h' then sec = np * 3600
            elseif unitP == 'd' then sec = np * 86400
            elseif unitP == 's' then sec = np end
          end
          if sec > 0 then
            totalAvail = totalAvail + (sec * cnt)
            table.insert(pool, {{id = iid, count = cnt, sec = sec, isTrain = (t2 == 3)}})
          end
        end
      end
    end
  end
end
out.avail_sec = totalAvail
if totalAvail <= 0 or #pool == 0 then
  out.reason = 'speedups_exhausted'
  return _enc(out)
end
if totalAvail < bestQ.remSec and not allowPartial then
  out.reason = 'insufficient_speedups_to_finish_batch'
  out.rem_sec_before = bestQ.remSec
  out.barrack = bestQ.barrack
  return _enc(out)
end

-- Sort: dedicated training speedups first, largest duration first for greedy non-overshooting fit
table.sort(pool, function(a, b)
  if a.isTrain ~= b.isTrain then return a.isTrain end
  return a.sec > b.sec
end)

local usedMap = {{}}
local usedOrder = {{}}
local remNeed = bestQ.remSec
local appliedSec = 0
for _, item in ipairs(pool) do
  if remNeed <= 0 then break end
  if item.sec <= remNeed then
    local take = math.min(item.count, math.floor(remNeed / item.sec))
    if take > 0 then
      usedMap[item.id] = (usedMap[item.id] or 0) + take
      item.count = item.count - take
      appliedSec = appliedSec + (take * item.sec)
      remNeed = remNeed - (take * item.sec)
    end
  end
end
-- If a small sub-item remainder stays (>0), spend 1 smallest remaining speedup to finish the queue cleanly!
if remNeed > 0 then
  local smallest = nil
  for _, item in ipairs(pool) do
    if item.count > 0 then
      if not smallest or item.sec < smallest.sec or (item.sec == smallest.sec and item.isTrain and not smallest.isTrain) then
        smallest = item
      end
    end
  end
  if smallest and (appliedSec + smallest.sec >= bestQ.remSec or allowPartial) then
    usedMap[smallest.id] = (usedMap[smallest.id] or 0) + 1
    smallest.count = smallest.count - 1
    appliedSec = appliedSec + smallest.sec
    remNeed = math.max(0, remNeed - smallest.sec)
  end
end

local parts = {{}}
for iid, cnt in pairs(usedMap) do
  if cnt > 0 then table.insert(parts, tostring(iid) .. ';' .. tostring(cnt)) end
end
if #parts == 0 then
  out.reason = 'no_matching_speedup_combo'
  return _enc(out)
end
local itemStr = table.concat(parts, '|')
if SFSNetwork and MsgDefines and MsgDefines.QueueCcdMNew then
  local okS, errS = pcall(function()
    SFSNetwork.SendMessage(MsgDefines.QueueCcdMNew, {{
      qUUID = bestQ.uuid,
      itemIDs = itemStr,
      isGold = 0,
      golloesSpeedTime = 0,
    }})
  end)
  if not okS then
    out.ok = false
    out.reason = 'QueueCcdMNew_error: ' .. tostring(errS)
    return _enc(out)
  end
end
out.applied = true
out.reason = 'sped_up'
out.barrack = bestQ.barrack
out.qType = bestQ.qType
out.uuid = tostring(bestQ.uuid)
out.troop_count = bestQ.count
out.rem_sec_before = bestQ.remSec
out.applied_sec = appliedSec
out.finished_queue = (appliedSec >= bestQ.remSec)
out.itemIDs = itemStr
return _enc(out)
"""
        return _eval_json(cd, pid, lua_zoom, timeout=10.0)

    # Phase 1: Always run standard barrack collect + highest-tier train sweep
    base_res = _run_barrack_sweep(dry_run)
    if not isinstance(base_res, dict) or not base_res.get("ok"):
        return base_res if isinstance(base_res, dict) else {"ok": False, "task": "troop_training", "error": "sweep_failed"}

    # Phase 2: Inspect Full Preparedness & Alliance Duel for Training Troops / Training Speedups boost!
    boost = _detect_training_event_boost(cd, pid, allow_network_refresh=not dry_run)
    fp_info = boost.get("fp") or {}
    vs_info = boost.get("vs") or {}
    should_zoom = bool(event_speed_zoom and boost.get("should_zoom"))

    out = dict(base_res)
    out["event_boost"] = {
        "should_zoom": boost.get("should_zoom", False),
        "reasons": boost.get("reasons") or [],
        "scores_on_train": boost.get("scores_on_train", False),
        "scores_on_speedup": boost.get("scores_on_speedup", False),
        "fp": fp_info,
        "vs": vs_info,
    }
    out["zoom_enabled"] = event_speed_zoom
    out["zoom_active"] = False
    out["zoom_batches"] = []
    out["zoom_troops_sped"] = 0
    out["zoom_speedup_sec_used"] = 0
    out["zoom_stopped_reason"] = "event_not_matching"
    detail_lines: list[str] = []

    train_sp_min = int((int(out.get("train_speedup_sec") or 0)) // 60)
    univ_sp_min = int((int(out.get("universal_speedup_sec") or 0)) // 60)
    detail_lines.append(
        f"Troop Training: collected={len(out.get('collected') or [])}, trained={len(out.get('trained') or [])}, "
        f"busy={len(out.get('busy') or [])}, train_speedups={train_sp_min}m (univ={univ_sp_min}m)"
    )
    for c in (out.get("collected") or []):
        if isinstance(c, dict):
            detail_lines.append(f"  • Collected {c.get('barrack')} (qType={c.get('qType')})")
    for t in (out.get("trained") or []):
        if isinstance(t, dict):
            detail_lines.append(f"  • Trained {t.get('barrack')}: armyId={t.get('armyId')} x{t.get('count')}")
    for b in (out.get("busy") or []):
        if isinstance(b, dict):
            detail_lines.append(
                f"  • Busy {b.get('barrack')}: x{b.get('count', '?')} rem={int(b.get('remSec') or 0) // 60}m {int(b.get('remSec') or 0) % 60}s"
            )

    if should_zoom and dry_run:
        out["zoom_active"] = True
        out["zoom_stopped_reason"] = "dry_run_preview"
        detail_lines.append(
            f"[ZOOM] [DRY-RUN] Active for: {'; '.join(boost.get('reasons') or [])} | avail_train_speedups={train_sp_min}m"
        )
    elif should_zoom and not dry_run:
        def _wait_training_queue_transition(
            target_uuid: str = "",
            prev_rem_sec: int = -1,
            expect_finished: bool = False,
            expect_any_active: bool = False,
            max_wait_sec: float = 1.4,
        ) -> None:
            poll_lua = f"""
local targetUuid = {json.dumps(str(target_uuid or ""))}
local prevRem = {int(prev_rem_sec)}
local expectFin = {str(bool(expect_finished)).lower()}
local expectActive = {str(bool(expect_any_active)).lower()}
local dc = DataCenter
local bqm = dc and dc.BuildQueueManager
local snap = _get_player_snapshot()
local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)
local matched = nil
local anyActive = false
local qTable = bqm and (bqm.queueList or bqm.allQueueList or bqm.buildQueueList)
if type(qTable) == 'table' then
  for _, q in pairs(qTable) do
    if type(q) == 'table' then
      local qt = tonumber(q.qType or q.queueType or 0) or 0
      local st = tonumber(q.state or 0) or 0
      local ft = tonumber(q.finishTime or 0) or 0
      if ft > 0 and ft < 1e12 then ft = ft * 1000 end
      local isTrainQ = (qt >= 3 and qt <= 6) or (qt >= 40 and qt <= 43)
      if isTrainQ and (st == 2 or (ft > nowMs and st ~= 3)) then
        anyActive = true
      end
      if targetUuid ~= '' and tostring(q.uuid or '') == targetUuid then
        local rem = (ft > nowMs) and math.ceil((ft - nowMs) / 1000) or 0
        matched = {{state = st, remSec = rem}}
      end
    end
  end
end
local ready = false
if expectActive then
  ready = anyActive
elseif targetUuid ~= '' then
  if expectFin then
    ready = (matched == nil) or (matched.state ~= 2) or (matched.remSec <= 0)
  else
    ready = (matched == nil) or (prevRem <= 0) or (matched.remSec < prevRem) or (matched.state ~= 2)
  end
end
return _enc({{ok = true, ready = ready}})
"""
            deadline = time.monotonic() + max_wait_sec
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                time.sleep(min(0.35, remaining))
                p_res = _eval_json(cd, pid, poll_lua, timeout=4.0)
                if not isinstance(p_res, dict) or not p_res.get("ok") or p_res.get("ready"):
                    break

        out["zoom_active"] = True
        detail_lines.append(f"[ZOOM] Activated by: {'; '.join(boost.get('reasons') or [])}")
        if out.get("trained"):
            _wait_training_queue_transition(expect_any_active=True, max_wait_sec=1.4)

        stopped_reason = "max_zoom_batches_reached"
        cur_boost = boost
        for batch_num in range(1, max(1, max_zoom_batches) + 1):
            if not cur_boost.get("should_zoom"):
                stopped_reason = "milestone_reached"
                break
            fp_before = int((cur_boost.get("fp") or {}).get("cur_score") or 0)
            fp_max = int((cur_boost.get("fp") or {}).get("max_score") or 0)
            vs_before = int((cur_boost.get("vs") or {}).get("cur_score") or 0)
            vs_max = int((cur_boost.get("vs") or {}).get("max_score") or 0)

            step = _run_zoom_speedup_step(allow_partial=bool(cur_boost.get("scores_on_speedup")))
            if not step.get("applied"):
                stopped_reason = str(step.get("reason") or "no_speedup_applied")
                break

            applied_sec = int(step.get("applied_sec") or 0)
            troops_sped = int(step.get("troop_count") or 0)
            out["zoom_speedup_sec_used"] += applied_sec
            finished_q = bool(step.get("finished_queue"))

            _wait_training_queue_transition(
                target_uuid=str(step.get("uuid") or ""),
                prev_rem_sec=int(step.get("rem_sec_before") or 0),
                expect_finished=finished_q,
                max_wait_sec=1.4,
            )
            re_collected = 0
            re_trained = 0
            if finished_q:
                out["zoom_troops_sped"] += troops_sped
                # Collect finished troops + immediately queue next training batch!
                next_sweep = _run_barrack_sweep(False)
                for c in (next_sweep.get("collected") or []):
                    out["collected"].append(c)
                    re_collected += 1
                for t in (next_sweep.get("trained") or []):
                    out["trained"].append(t)
                    re_trained += int(t.get("count") or 0)
                if re_trained > 0:
                    _wait_training_queue_transition(expect_any_active=True, max_wait_sec=1.2)

            # Re-read FP & VS scores after batch
            cur_boost = _detect_training_event_boost(cd, pid, allow_network_refresh=True)
            fp_after = int((cur_boost.get("fp") or {}).get("cur_score") or 0)
            vs_after = int((cur_boost.get("vs") or {}).get("cur_score") or 0)

            batch_rec = {
                "batch": batch_num,
                "barrack": step.get("barrack"),
                "troops_sped": troops_sped if finished_q else 0,
                "applied_sec": applied_sec,
                "itemIDs": step.get("itemIDs"),
                "finished_queue": finished_q,
                "requeued_troops": re_trained,
                "fp_before": fp_before,
                "fp_after": fp_after,
                "vs_before": vs_before,
                "vs_after": vs_after,
            }
            out["zoom_batches"].append(batch_rec)
            detail_lines.append(
                f"[ZOOM] Batch #{batch_num} ({step.get('barrack')}): sped up {troops_sped} troops "
                f"(-{applied_sec // 60}m via {step.get('itemIDs')}, finished={finished_q}, requeued=+{re_trained}) | "
                f"FP {fp_before:,}->{fp_after:,}/{fp_max:,} | VS {vs_before:,}->{vs_after:,}/{vs_max:,}"
            )

            if not finished_q:
                stopped_reason = "speedups_exhausted"
                break
            if re_trained == 0 and int(next_sweep.get("remaining_cap") or 0) <= 0:
                stopped_reason = "drill_ground_cap_reached"
                break

        out["zoom_stopped_reason"] = stopped_reason
        detail_lines.append(
            f"[ZOOM] Finished: {len(out['zoom_batches'])} batch(es), sped_troops={out['zoom_troops_sped']}, "
            f"speedups_used={out['zoom_speedup_sec_used'] // 60}m, stopped={stopped_reason}"
        )
        # Auto-claim any newly unlocked FP/VS chests after zooming!
        if out["zoom_batches"]:
            try:
                claim_post = _claim_full_preparedness(cd, pid, client_state, cfg, dry_run=False, context=context)
                claimed_chests = claim_post.get("personal_arms_claimed") or []
                if claimed_chests:
                    out["zoom_chests_claimed"] = claimed_chests
                    detail_lines.append(f"[ZOOM] Auto-claimed {len(claimed_chests)} unlocked event chest batch(es)")
            except Exception:
                pass
    else:
        fp_s = f"FP='{fp_info.get('theme') or 'none'}' {int(fp_info.get('cur_score') or 0):,}/{int(fp_info.get('max_score') or 0):,}"
        vs_s = (
            f"VS=Day{vs_info.get('day', 0)} {int(vs_info.get('cur_score') or 0):,}/{int(vs_info.get('max_score') or 0):,}"
            if vs_info.get("open")
            else "VS=closed"
        )
        detail_lines.append(f"Event Speed-Zoom: standby ({fp_s}; {vs_s})")

    # Build summary action & message
    if out.get("zoom_batches"):
        out["action"] = "zoom_trained"
        out["message"] = (
            f"Event Speed-Zoom: {len(out['zoom_batches'])} batch(es), sped {out['zoom_troops_sped']} troops "
            f"(-{out['zoom_speedup_sec_used'] // 60}m), stopped={out['zoom_stopped_reason']}"
        )
    elif out.get("trained"):
        out["action"] = "trained"
        total_trained = sum(int(t.get("count") or 0) for t in out["trained"] if isinstance(t, dict))
        out["message"] = f"Trained {total_trained} troops across {len(out['trained'])} barrack(s)"
    elif out.get("collected"):
        out["action"] = "collected"
        out["message"] = f"Collected completed troops from {len(out['collected'])} barrack(s)"
    elif out.get("busy"):
        out["action"] = "all_barracks_training"
        b_names = [str(b.get("barrack") or "") for b in out["busy"] if isinstance(b, dict)]
        out["message"] = f"All {len(out['busy'])} barracks actively training ({', '.join(b_names)})"
    else:
        out["action"] = "none"
        out["message"] = "No barracks available or army capacity full"

    out["detail_lines"] = detail_lines
    return out


def run_building_upgrades(cd: Any, pid: int, client_state: dict[str, Any], cfg: dict[str, Any], dry_run: bool = False, context: dict[str, Any] | None = None) -> dict[str, Any]:
    task_cfg = cfg.get("building_upgrades", {})
    collect_res = bool(task_cfg.get("collect_resources", True))
    hq_priority = bool(task_cfg.get("hq_priority", True))
    auto_prereqs = bool(task_cfg.get("auto_prerequisites", True))
    call_help = bool(task_cfg.get("call_alliance_help", True))
    prefer_fastest = bool(task_cfg.get("prefer_fastest", False))
    prio_ids = [int(x) for x in task_cfg.get("priority_building_types", [400000, 403000, 423000, 424000, 425000, 411000])]
    prio_lua = "{" + ",".join(f"[{bid}]={i}" for i, bid in enumerate(prio_ids, 1)) + "}"

    lua = f"""
local dryRun = {str(dry_run).lower()}
local collectRes = {str(collect_res).lower()}
local hqPriority = {str(hq_priority).lower()}
local autoPrereqs = {str(auto_prereqs).lower()}
local callHelp = {str(call_help).lower()}
local preferFastest = {str(prefer_fastest).lower()}
local prioOrder = {prio_lua}

local out = {{
  ok = true,
  task = 'building_upgrades',
  dry_run = dryRun,
  resources_collected = false,
  free_queues = 0,
  upgraded = nil,
  reason = '',
}}

local bm = DataCenter and DataCenter.BuildManager
local bqm = DataCenter and DataCenter.BuildQueueManager
if not bm or not bqm then
  out.ok = false
  out.error = 'BuildManager/BuildQueueManager unavailable'
  return _enc(out)
end

if collectRes and bm.OneClickResourceCollection then
  if not dryRun then pcall(function() bm:OneClickResourceCollection() end) end
  out.resources_collected = true
end

local nowMs = _get_player_snapshot().serverSec * 1000
-- Flush any finished building upgrades stuck in state~=0 while on World scene
local finishedCount = 0
if not dryRun and bm.CheckSendBuildFinish and type(bm.allBuilding) == 'table' and nowMs > 0 then
  for buuid, binfo in pairs(bm.allBuilding) do
    if type(binfo) == 'table' and tonumber(binfo.state or 0) ~= 0 then
      local ut = tonumber(binfo.updateTime or 0) or 0
      if ut > 0 and ut < 1e12 then ut = ut * 1000 end
      if ut > 0 and ut <= nowMs then
        pcall(function() bm:CheckSendBuildFinish(buuid, false, true) end)
        finishedCount = finishedCount + 1
      end
    end
  end
end
out.finished_flushed = finishedCount
local freeQueues = 0
if bqm.GetQueueList then
  for _, q in pairs(bqm:GetQueueList() or {{}}) do
    if type(q) == 'table' and tonumber(q.state or 0) == 0 then
      local isOwn = (tonumber(q.giftId or 0) == 0)
        or (bqm.IsRobotPermanentlyOwned and bqm:IsRobotPermanentlyOwned(q.uuid))
        or (bqm.IsUnlockBuildQueueLease and bqm:IsUnlockBuildQueueLease(q))
        or (tonumber(q.expireTime or 0) > nowMs)
      if isOwn then
        freeQueues = freeQueues + 1
      end
    end
  end
else
  local fqRaw = bqm.GetFreeQueueCount and bqm:GetFreeQueueCount()
  freeQueues = tonumber(fqRaw) or 0
end
out.free_queues = freeQueues
if freeQueues <= 0 then
  out.reason = 'no_free_builder_queue'
  return _enc(out)
end

-- Detect active functional queues so we never attempt to upgrade a building currently busy healing/researching/training
local busyBuildingTypes = {{}}
local qm = DataCenter and DataCenter.QueueDataManager
if qm and type(qm.queueDic) == 'table' then
  for _, q in pairs(qm.queueDic) do
    if type(q) == 'table' and tonumber(q.state or 0) == 2 then
      local qEnd = tonumber(q.endTime or 0) or 0
      if qEnd > 0 and qEnd < 1e12 then qEnd = qEnd * 1000 end
      if qEnd == 0 or nowMs == 0 or qEnd > nowMs then
        local qt = tonumber(q.type or 0) or 0
        if qt == 3 or qt == 46 then busyBuildingTypes[411000] = 'hospital_healing'
        elseif qt == 6 then busyBuildingTypes[403000] = 'lab_researching'
        elseif qt == 1 then busyBuildingTypes[423000] = 'car_barracks_training'
        elseif qt == 8 then busyBuildingTypes[424000] = 'foot_barracks_training'
        elseif qt == 9 then busyBuildingTypes[425000] = 'bow_barracks_training'
        end
      end
    end
  end
end

local btm = DataCenter and DataCenter.BuildTemplateManager
local function _get_next_lv_time(b)
  if not b or not btm or not btm.GetBuildingLevelTemplate then return 60 end
  local okT, lvTpl = pcall(function() return btm:GetBuildingLevelTemplate(b.itemId, (tonumber(b.level or 0) or 0) + 1) end)
  if not okT or not lvTpl then return -1 end
  return tonumber(lvTpl.time or lvTpl.buildTime or lvTpl.upgradeTime or 0) or 0
end

local function _can_upgrade_now(uuid)
  if not uuid then return false, nil, 0 end
  local b = bm:GetBuildingDataByUuid(uuid)
  if not b then return false, nil, 0 end
  if tonumber(b.state or 0) ~= 0 then return false, b, 0 end
  if tonumber(b.updateTime or 0) > 0 then return false, b, 0 end
  local bItemId = tonumber(b.itemId or 0) or 0
  if busyBuildingTypes[bItemId] then return false, b, 0 end
  if bm.isReachMax and bm:isReachMax(uuid) then return false, b, 0 end
  local nextTime = _get_next_lv_time(b)
  if nextTime <= 0 then return false, b, 0 end
  if bm.IsMeetPreconditionbyUuid and not bm:IsMeetPreconditionbyUuid(uuid) then return false, b, nextTime end
  if bm.CheckBuildUpgradeResAndItem then
    local ok_res, resInfo = pcall(function() return bm:CheckBuildUpgradeResAndItem(uuid) end)
    if ok_res then
      if type(resInfo) == 'table' then
        if resInfo.enough ~= true then return false, b, nextTime end
      elseif not resInfo then
        return false, b, nextTime
      end
    end
  end
  if bqm.IsCanUpgrade then
    local ok_q, canQ = pcall(function() return bqm:IsCanUpgrade(b.itemId, b.level, math.max(nextTime * 1000, 1000)) end)
    if ok_q and canQ == false then return false, b, nextTime end
  end
  return true, b, nextTime
end

local chosen = nil
local chosenTime = 0
local hqUuid = bm.MainBuildUuid
if not hqUuid and bm.GetFunbuildByItemID then
  local mb = bm:GetFunbuildByItemID(400000)
  if mb and mb.uuid then hqUuid = mb.uuid end
end
if hqPriority and not preferFastest and hqUuid then
  local canHq, bHq, tHq = _can_upgrade_now(hqUuid)
  if canHq and bHq then
    chosen = bHq
    chosenTime = tHq
  end
end

if not chosen and (autoPrereqs or not hqPriority or preferFastest) and bm.GetCanUpgradeBuildUuidList then
  local candUuids = bm:GetCanUpgradeBuildUuidList() or {{}}
  local bestScore = 999999999999
  for _, uuid in ipairs(candUuids) do
    local okU, b, nTime = _can_upgrade_now(uuid)
    if okU and b then
      local pRank = prioOrder[tonumber(b.itemId or 0)] or 50
      local lv = tonumber(b.level or 0) or 0
      local score = preferFastest and (nTime * 100 + lv) or (pRank * 1000 + lv)
      if score < bestScore then
        bestScore = score
        chosen = b
        chosenTime = nTime
      end
    end
  end
end

if not chosen then
  out.reason = 'no_affordable_precondition_met_building'
  return _enc(out)
end

-- Send FreeBuildingUpNew directly with real free robotUuid so upgrades work reliably from BOTH City and World scenes
local sentViaRpc = false
if not dryRun then
  if SFSNetwork and MsgDefines and MsgDefines.FreeBuildingUpNew then
    local tpl = btm and btm.GetBuildingDesTemplate and _safe_call(function() return btm:GetBuildingDesTemplate(chosen.itemId) end, nil) or nil
    local isSeason = tpl and tpl.IsSeasonBuild and _safe_call(function() return tpl:IsSeasonBuild() end, false) or false
    local robot = bqm.GetFreeQueue and _safe_call(function() return bqm:GetFreeQueue(isSeason, math.max(chosenTime * 1000, 1000)) end, nil) or nil
    if robot and robot.uuid then
      local param = {{
        uuid = tostring(chosen.uuid),
        bId = tonumber(chosen.itemId or 0),
        gold = (BuildUpgradeUseGoldType and BuildUpgradeUseGoldType.No) or 0,
        upLevel = (tonumber(chosen.level or 0) or 0) + 1,
        clientParam = '',
        truckId = 0,
        pathTime = 0,
        robotUuid = robot.uuid,
      }}
      pcall(function() SFSNetwork.SendMessage(MsgDefines.FreeBuildingUpNew, param) end)
      sentViaRpc = true
    end
  end
  if not sentViaRpc and bm.UpgradeBuilding then
    bm:UpgradeBuilding(chosen.uuid)
  end
end

out.action = 'upgraded'
out.upgraded = {{
  uuid = tostring(chosen.uuid),
  itemId = tonumber(chosen.itemId or 0),
  level = tonumber(chosen.level or 0),
  targetLevel = (tonumber(chosen.level or 0) or 0) + 1,
  upgradeTimeSec = chosenTime,
}}
out.message = string.format("Started upgrade on building %d to Lv%d (~%ds)", tonumber(chosen.itemId or 0), (tonumber(chosen.level or 0) or 0) + 1, chosenTime)
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if not dry_run and res.get("ok") and isinstance(res.get("upgraded"), dict):
        # Verify server accepted the building upgrade (state!=0 or updateTime>nowMs), then send alliance help
        upg = res["upgraded"]
        b_uuid = str(upg.get("uuid") or "")
        b_item = str(upg.get("itemId") or "")
        time.sleep(0.8)
        verify_lua = f"""
local bUuid = {json.dumps(b_uuid)}
local bItemId = {json.dumps(b_item)}
local callHelp = {str(call_help).lower()}
local bm = DataCenter and DataCenter.BuildManager
local hm = DataCenter and DataCenter.AllianceHelpDataManager
local snap = _get_player_snapshot()
local nowMs = (snap.serverSec or 0) * 1000
local b = bm and bm.GetBuildingDataByUuid and bm:GetBuildingDataByUuid(tonumber(bUuid) or bUuid) or nil
if not b and bm and bm.GetBuildingDataByUuid then b = bm:GetBuildingDataByUuid(bUuid) end
local started = false
if b then
  local ut = tonumber(b.updateTime or 0) or 0
  if ut > 0 and ut < 1e12 then ut = ut * 1000 end
  started = (tonumber(b.state or 0) ~= 0) or (ut > nowMs) or (tonumber(b.level or 0) >= {int(upg.get('targetLevel') or 0)})
  if started and callHelp and tonumber(b.isHelped or 0) == 0 and tonumber(b.state or 0) ~= 0 then
    local helpType = (AllianceHelpType and AllianceHelpType.Building) or 1
    local defQt = (NewQueueType and NewQueueType.Default) or 0
    pcall(function()
      if hm and hm.SendCallHelp then
        hm:SendCallHelp(b.uuid, helpType, defQt, bItemId)
      elseif SFSNetwork and MsgDefines and MsgDefines.AllianceCallHelp then
        SFSNetwork.SendMessage(MsgDefines.AllianceCallHelp, tonumber(b.uuid) or b.uuid, helpType, defQt, bItemId)
      end
    end)
  end
end
return _enc({{ ok = true, started = started, state = b and tonumber(b.state or 0) or -1, level = b and tonumber(b.level or 0) or -1, updateTime = b and tonumber(b.updateTime or 0) or 0 }})
"""
        vres = _eval_json(cd, pid, verify_lua, timeout=6.0)
        res["verified"] = vres
        if vres.get("ok") and not vres.get("started"):
            res["ok"] = False
            res["action"] = "upgrade_rejected"
            res["reason"] = "server_rejected_upgrade"
            res["message"] = f"Server rejected upgrade on building {b_item} (uuid={b_uuid})"
    return res


def run_tyrant_event(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = (cfg or {}).get("tyrant_event") or {}
    ctx = context or {}
    reserve_raw = ctx.get("reserve_override") if ctx.get("reserve_override") is not None else (cfg or {}).get("formation_reserve", 0)
    reserve = max(0, int(reserve_raw or 0))
    claim_free = bool(task_cfg.get("claim_free_reward", True))
    claim_ally = bool(task_cfg.get("claim_alliance_reward", True))
    join_or_atk = bool(task_cfg.get("join_or_attack", True))
    prefer_rally = bool(task_cfg.get("prefer_rally", False))
    f1_host = bool(task_cfg.get("f1_always_host_rally", True))
    others_join = bool(task_cfg.get("other_formations_join_rallies", True))
    repeat_free = bool(task_cfg.get("repeat_when_free", True))
    fast_repeat_sec = int(task_cfg.get("fast_repeat_sec", 10) or 10)

    blacklisted_lua = _blacklisted_points_lua(context)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local claimFree = {str(claim_free).lower()}
local claimAlly = {str(claim_ally).lower()}
local joinOrAtk = {str(join_or_atk).lower()}
local preferRally = {str(prefer_rally).lower()}
local f1Host = {str(f1_host).lower()}
local othersJoin = {str(others_join).lower()}
local repeatFree = {str(repeat_free).lower()}
local blacklistedPts = {blacklisted_lua}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local abm = DataCenter and DataCenter.AllianceBossManager
local out = {{
  ok = true,
  task = 'tyrant_event',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  message = '',
  is_open = false,
  in_battle = false,
  actId = nil,
  bossPointId = 0,
  free_reward_claimed = false,
  alliance_reward_claimed = false,
  dispatched = _jarr({{}}),
  marched = _jarr({{}}),
  hosted = nil,
  joined = _jarr({{}}),
  marched_uuids = _jarr({{}}),
  send_errors = _jarr({{}}),
  fast_repeat = false,
  fast_repeat_sec = {fast_repeat_sec},
}}

if not abm then
  out.ok = false
  out.error = 'AllianceBossManager unavailable'
  out.status = 'error'
  out.stop_reason = 'alliance_boss_manager_unavailable'
  out.message = 'AllianceBossManager unavailable'
  return _enc(out)
end

out.is_open = (abm.IsAllianceBossActivityOpen and _safe_call(function() return abm:IsAllianceBossActivityOpen() end, false)) and true or false
out.in_battle = (abm.GetIsInBattle and _safe_call(function() return abm:GetIsInBattle() end, false)) and true or false
out.actId = (abm.GetCurrActivityId and _safe_call(function() return abm:GetCurrActivityId() end, nil)) or nil
local bInfo = (abm.GetBossInfo and _safe_call(function() return abm:GetBossInfo() end, {{}})) or {{}}
out.bossPointId = tonumber(type(bInfo) == 'table' and (bInfo.pointId or bInfo.pointIndex or bInfo.pos) or 0) or 0
local wpm = DataCenter and DataCenter.WorldPointManager
local bossPtInfo = (out.bossPointId > 0 and wpm and wpm.GetPointInfo) and _safe_call(function() return wpm:GetPointInfo(out.bossPointId) end, nil) or nil
local bossUuid = (type(bInfo) == 'table' and (bInfo.uuid or bInfo.bossUuid)) or (bossPtInfo and bossPtInfo.uuid) or 0

if claimFree and abm.GetIsFreeRewardCanReceive and _safe_call(function() return abm:GetIsFreeRewardCanReceive() end, false) then
  if not dryRun and abm.OnSendReceiveAllianceBossFreeRewardMessage then
    local okR, errR = pcall(function() abm:OnSendReceiveAllianceBossFreeRewardMessage() end)
    if okR then
      out.free_reward_claimed = true
    else
      table.insert(out.send_errors, 'FreeReward: ' .. tostring(errR))
    end
  else
    out.free_reward_claimed = true
  end
end

if claimAlly and abm.CanReceivedAllianceReward and _safe_call(function() return abm:CanReceivedAllianceReward() end, false) and out.actId then
  if not dryRun and SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.ReceiveAllianceBossAllianceReward then
    local okA, errA = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.ReceiveAllianceBossAllianceReward, tonumber(out.actId) or out.actId)
    end)
    if okA then
      out.alliance_reward_claimed = true
    else
      table.insert(out.send_errors, 'AllianceReward: ' .. tostring(errA))
    end
  else
    out.alliance_reward_claimed = true
  end
end

if not snap.inAlliance then
  out.status = 'physical_limit'
  out.stop_reason = 'not_in_alliance'
  out.message = 'Not in an alliance'
  return _enc(out)
end

if not out.is_open then
  out.status = 'physical_limit'
  out.stop_reason = 'not_detected'
  out.message = 'The Tyrant event is not currently open'
  return _enc(out)
end

if not out.in_battle then
  out.status = 'physical_limit'
  out.stop_reason = 'event_not_in_battle'
  out.message = 'The Tyrant event is open but not currently in battle phase'
  return _enc(out)
end

local tyrantRallies = {{}}
local f1Form = nil
local bossBlacklisted = (out.bossPointId > 0 and _is_point_blacklisted(blacklistedPts, out.bossPointId, nil, nil)) and true or false

if joinOrAtk then
  local wm = DataCenter and DataCenter.AllianceWarDataManager
  local allyBossTeamType = (AllianceTeamType and AllianceTeamType.ATTACK_ALLIANCE_BOSS) or 10
  if wm and wm.GetAllAllianceWar then
    local wars = _safe_call(function() return wm:GetAllAllianceWar() end, {{}}) or {{}}
    for _, w in pairs(wars) do
      if type(w) == 'table' then
        local wType = tonumber(w.type or -1) or -1
        if wType == allyBossTeamType and w.uuid then
          local wPt = tonumber(w.targetPointId or w.targetPos or w.targetPoint or w.pointId or out.bossPointId) or out.bossPointId
          local alreadyIn = wm.HasRallyFormationForInfo and _safe_call(function() return wm:HasRallyFormationForInfo(w) end, false)
          if not alreadyIn and tostring(w.attackUid or '') ~= tostring(snap.uid or '') and not _is_point_blacklisted(blacklistedPts, wPt, nil, w.uuid) then
            table.insert(tyrantRallies, w)
          end
        end
      end
    end
  end

  if f1Host then
    -- Pick F1 BEFORE applying reserve to extra formations; honour full reserve if reserve >= total_formations
    local allFree = _pick_free_formations(0, {_used_formations_lua(context, pid)}, false, not dryRun)
    local rawOthers = {{}}
    local otherForms = {{}}
    local allReserved = (occ.total_formations > 0 and reserve >= occ.total_formations)
    if not allReserved then
      for _, f in ipairs(allFree) do
        if tonumber(f.index or 0) == 1 and not f1Form then
          f1Form = f
        else
          table.insert(rawOthers, f)
        end
      end
      if #rawOthers > reserve then
        for i = reserve + 1, #rawOthers do
          table.insert(otherForms, rawOthers[i])
        end
      end
    end
    out.usable_formations = (f1Form and 1 or 0) + #otherForms

    if f1Form and out.bossPointId > 0 and not bossBlacklisted and MarchUtil and MarchUtil.SendCreateMarchMessage then
      local f1Ready = dryRun or _restock_formation(f1Form)
      if not f1Ready then
        f1Form = nil
        out.usable_formations = math.max(0, out.usable_formations - 1)
      else
        local tType = (MarchTargetType and MarchTargetType.RALLY_FOR_ALLIANCE_BOSS) or 74
        local okS, errS = true, nil
        if not dryRun then
          okS, errS = pcall(function()
            MarchUtil.SendCreateMarchMessage(tonumber(f1Form.uuid) or f1Form.uuid, tType, out.bossPointId, bossUuid, 1, 1, nil, snap.serverId)
          end)
        end
        if okS then
          local hRec = {{
            mode = 'f1_host_rally',
            pointId = out.bossPointId,
            targetPoint = out.bossPointId,
            warUuid = '',
            formationIndex = 1,
            formationUuid = tostring(f1Form.uuid),
          }}
          out.hosted = hRec
          table.insert(out.marched, hRec)
          table.insert(out.dispatched, hRec)
          table.insert(out.marched_uuids, tostring(f1Form.uuid))
        else
          table.insert(out.send_errors, 'TyrantF1Rally: ' .. tostring(errS))
        end
      end
    end

    if othersJoin and #otherForms > 0 and #tyrantRallies > 0 then
      local otherIdx = 1
      for rIdx = 1, #tyrantRallies do
        local w = tyrantRallies[rIdx]
        local f = nil
        f, otherIdx = _next_ready_formation(otherForms, otherIdx, dryRun)
        if not f then break end
        local okJ, errJ, jPt, jMethod = _join_rally_headless(f, w, out.bossPointId, snap.serverId, dryRun)
        if okJ then
          local jRec = {{
            mode = 'join_rally',
            warUuid = tostring(w.uuid),
            targetPoint = jPt,
            pointId = jPt,
            formationIndex = tonumber(f.index or 0),
            formationUuid = tostring(f.uuid),
            joinMethod = jMethod,
          }}
          table.insert(out.joined, jRec)
          table.insert(out.marched, jRec)
          table.insert(out.dispatched, jRec)
          table.insert(out.marched_uuids, tostring(f.uuid))
        else
          table.insert(out.send_errors, 'TyrantJoinRally: ' .. tostring(errJ))
          break
        end
      end
    end
  else
    local forms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, false, not dryRun)
    out.usable_formations = #forms
    if #forms > 0 then
      local f, _ = _next_ready_formation(forms, 1, dryRun)
      if not f then
        out.usable_formations = 0
      else
        local joined = false
        if #tyrantRallies > 0 then
          local w = tyrantRallies[1]
          local okJ, errJ, jPt, jMethod = _join_rally_headless(f, w, out.bossPointId, snap.serverId, dryRun)
          if okJ then
            local jRec = {{
              mode = 'join_rally',
              warUuid = tostring(w.uuid),
              targetPoint = jPt,
              pointId = jPt,
              formationIndex = tonumber(f.index or 0),
              formationUuid = tostring(f.uuid),
              joinMethod = jMethod,
            }}
            table.insert(out.joined, jRec)
            table.insert(out.marched, jRec)
            table.insert(out.dispatched, jRec)
            table.insert(out.marched_uuids, tostring(f.uuid))
            joined = true
          else
            table.insert(out.send_errors, 'TyrantJoinRally: ' .. tostring(errJ))
          end
        end
        if not joined and out.bossPointId > 0 and not bossBlacklisted and MarchUtil and MarchUtil.SendCreateMarchMessage then
          local tType = preferRally and ((MarchTargetType and MarchTargetType.RALLY_FOR_ALLIANCE_BOSS) or 74) or ((MarchTargetType and MarchTargetType.ATTACK_ALLIANCE_BOSS) or 53)
          local okS, errS = true, nil
          if not dryRun then
            okS, errS = pcall(function()
              MarchUtil.SendCreateMarchMessage(tonumber(f.uuid) or f.uuid, tType, out.bossPointId, bossUuid, preferRally and 1 or 0, 1, nil, snap.serverId)
            end)
          end
          if okS then
            local mRec = {{
              mode = preferRally and 'rally' or 'attack',
              pointId = out.bossPointId,
              targetPoint = out.bossPointId,
              warUuid = '',
              formationIndex = tonumber(f.index or 0),
              formationUuid = tostring(f.uuid),
            }}
            table.insert(out.marched, mRec)
            table.insert(out.dispatched, mRec)
            table.insert(out.marched_uuids, tostring(f.uuid))
          else
            table.insert(out.send_errors, 'TyrantMarch: ' .. tostring(errS))
          end
        end
      end
    end
  end

  if repeatFree then
    out.fast_repeat = true
  end
end

out.dispatched_count = #out.dispatched
if out.dispatched_count > 0 then
  out.status = 'dispatched'
  out.stop_reason = ''
  if not dryRun then
    out.active_marches = occ.active_marches + out.dispatched_count
    out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
  end
  out.message = string.format('Dispatched %d squad(s) against The Tyrant (hosted=%s, joined=%d)', out.dispatched_count, out.hosted and 'yes' or 'no', #out.joined)
elseif #out.send_errors > 0 then
  out.ok = false
  out.status = 'error'
  out.stop_reason = 'send_failed'
  out.message = out.send_errors[1]
elseif out.usable_formations == 0 then
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad during Tyrant battle (%d/%d active)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No usable squads available for The Tyrant (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
elseif occ.active_marches > 0 then
  out.status = 'waiting_for_squad'
  out.stop_reason = ''
  out.message = string.format('Waiting for F1 return or open Tyrant rallies (%d/%d active)', occ.active_marches, occ.total_formations)
elseif not joinOrAtk then
  out.status = 'physical_limit'
  out.stop_reason = 'attack_disabled'
  out.message = 'The Tyrant join/attack option is disabled'
elseif out.bossPointId <= 0 and #tyrantRallies == 0 then
  out.status = 'physical_limit'
  out.stop_reason = 'no_targets_found'
  out.message = 'The Tyrant battle open but boss point not found'
elseif f1Host and not f1Form then
  out.status = 'physical_limit'
  out.stop_reason = 'f1_unavailable'
  out.message = 'Formation 1 unavailable and no open Tyrant rallies to join'
else
  out.status = 'physical_limit'
  out.stop_reason = 'no_targets_found'
  out.message = 'No actionable Tyrant boss target or open rally available'
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if context is not None:
        used_uuids: list[str] = []
        if isinstance(res.get("marched_uuids"), list):
            used_uuids.extend(str(u) for u in res["marched_uuids"] if u)
        elif isinstance(res.get("marched"), dict) and res["marched"].get("formationUuid"):
            used_uuids.append(str(res["marched"]["formationUuid"]))
        if not dry_run and used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return _ensure_step_contract(res, task_name="tyrant_event", default_message="Tyrant event step completed")


def run_boomer_runs(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = (cfg or {}).get("boomer_runs") or {}
    ctx = context or {}
    reserve_raw = ctx.get("reserve_override") if ctx.get("reserve_override") is not None else (cfg or {}).get("formation_reserve", 0)
    reserve = max(0, int(reserve_raw or 0))
    join_open = bool(task_cfg.get("join_open_rallies", True))
    auto_rally = bool(task_cfg.get("auto_start_rally", True))
    min_lv_raw = ctx.get("min_level_override") if ctx.get("min_level_override") is not None else task_cfg.get("min_level", 1)
    max_lv_raw = ctx.get("max_level_override") if ctx.get("max_level_override") is not None else task_cfg.get("max_level", 5)
    min_lv = max(1, int(min_lv_raw or 1))
    max_lv = max(min_lv, int(max_lv_raw or min_lv))
    stamina_cost = max(1, int(ctx.get("stamina_cost_override") if ctx.get("stamina_cost_override") is not None else task_cfg.get("stamina_cost", 20)))
    has_min_stam_override = ctx.get("min_stamina_override") is not None
    if has_min_stam_override:
        min_stamina = max(0, int(ctx.get("min_stamina_override") or 0))
    else:
        min_stamina = max(0, int(task_cfg.get("min_stamina", (cfg or {}).get("min_stamina", 60))))
    search_lv_override = ctx.get("search_level")
    search_lv_val = max(min_lv, min(max_lv, int(search_lv_override))) if search_lv_override is not None else 0

    early = _precheck_world_step_readiness(
        cd,
        pid,
        task_name="boomer_runs",
        reserve=reserve,
        context=context,
        dry_run=dry_run,
        check_alliance=True,
        min_stamina=min_stamina,
        stamina_cost=stamina_cost,
        strict_stamina_reserve=has_min_stam_override,
    )
    if early is not None:
        return early

    claimed_keys = list(ctx.get("claimed_boomer_points", []))
    claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys) + "}"
    blacklisted_lua = _blacklisted_points_lua(context)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local joinOpen = {str(join_open).lower()}
local autoRally = {str(auto_rally).lower()}
local minLv = {min_lv}
local maxLv = {max_lv}
local minStam = {min_stamina}
local staminaCost = {stamina_cost}
local strictReserve = {str(has_min_stam_override).lower()}
local reqSearchLv = {search_lv_val}
local claimedPts = {claimed_lua}
local blacklistedPts = {blacklisted_lua}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local mm = DataCenter and DataCenter.MonsterManager
local unlockedBossMaxLv = 0
if mm then
  local findMax = 0
  local atkMax = 0
  if mm.GetCanFindBossMaxLevel then
    findMax = tonumber(_safe_call(function() return mm:GetCanFindBossMaxLevel(0) end, 0)) or 0
  end
  if mm.GetCurCanAttackBossMaxLevel then
    atkMax = tonumber(_safe_call(function() return mm:GetCurCanAttackBossMaxLevel() end, 0)) or 0
  end
  if findMax > 0 and atkMax > 0 then
    unlockedBossMaxLv = math.min(findMax, atkMax)
  elseif findMax > 0 then
    unlockedBossMaxLv = findMax
  elseif atkMax > 0 then
    unlockedBossMaxLv = atkMax
  end
end
if unlockedBossMaxLv > 0 then
  if maxLv > unlockedBossMaxLv then maxLv = unlockedBossMaxLv end
  if minLv > maxLv then minLv = maxLv end
end
local effSearchLv = (reqSearchLv > 0) and math.max(minLv, math.min(maxLv, reqSearchLv)) or maxLv

local out = {{
  ok = true,
  task = 'boomer_runs',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  message = '',
  unlocked_max_level = unlockedBossMaxLv,
  effective_min_level = minLv,
  effective_max_level = maxLv,
  open_rallies = 0,
  joined = nil,
  joined_list = _jarr({{}}),
  started_rally = nil,
  started_rallies = _jarr({{}}),
  dispatched = _jarr({{}}),
  searched = false,
  searched_level = 0,
  send_errors = _jarr({{}}),
  reason = '',
}}

if not snap.inAlliance then
  out.reason = 'not_in_alliance'
  out.status = 'physical_limit'
  out.stop_reason = 'not_in_alliance'
  out.message = 'Not in an alliance (Boomers require alliance rallies)'
  return _enc(out)
end

local needStam = strictReserve and (minStam + staminaCost) or math.max(staminaCost, minStam)
local maxByStamina = 0
if snap.stamina >= needStam then
  if strictReserve then
    maxByStamina = math.floor((snap.stamina - minStam) / staminaCost)
  else
    maxByStamina = math.max(1, math.floor((snap.stamina - minStam) / staminaCost))
  end
end

if snap.stamina < needStam or maxByStamina <= 0 then
  out.reason = 'below_min_stamina'
  out.status = 'physical_limit'
  out.stop_reason = 'out_of_stamina'
  out.message = string.format('Out of stamina (%d left, need >=%d)', snap.stamina, needStam)
  return _enc(out)
end

local forms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, false, not dryRun)
out.usable_formations = #forms
if #forms == 0 then
  out.reason = 'no_free_formation_above_reserve'
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No usable squads available (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
  return _enc(out)
end

local formIdx = 1
local remStamBudget = maxByStamina
local ranOutOfTroops = false
local activeTargetPts = {{}}
local bossTeamType = (AllianceTeamType and AllianceTeamType.ATTACK_BOSS) or 0
local wm = DataCenter and DataCenter.AllianceWarDataManager

if wm and wm.GetAllAllianceWar then
  local wars = _safe_call(function() return wm:GetAllAllianceWar() end, {{}}) or {{}}
  for _, w in pairs(wars) do
    if type(w) == 'table' then
      local wType = tonumber(w.type or -1) or -1
      if wType == bossTeamType and w.uuid then
        local tpt = tonumber(w.targetPointId or w.targetPos or w.targetPoint or w.pointId or 0) or 0
        if tpt > 0 then activeTargetPts[tpt] = true end
        out.open_rallies = out.open_rallies + 1
        if joinOpen and formIdx <= #forms and remStamBudget > 0 then
          local alreadyIn = wm.HasRallyFormationForInfo and _safe_call(function() return wm:HasRallyFormationForInfo(w) end, false)
          local skipW = _is_point_blacklisted(blacklistedPts, tpt, nil, w.uuid)
            or (tpt > 0 and _is_my_march_target(tpt, occ.my_march_targets))
          if not alreadyIn and not skipW and tostring(w.attackUid or '') ~= tostring(snap.uid or '') then
            local f = nil
            f, formIdx = _next_ready_formation(forms, formIdx, dryRun)
            if not f then
              ranOutOfTroops = true
            else
              local okJ, errJ, jPt, jMethod = _join_rally_headless(f, w, tpt, snap.serverId, dryRun)
              if okJ then
                local jRec = {{
                  mode = 'join_rally',
                  warUuid = tostring(w.uuid),
                  targetPoint = jPt,
                  pointId = jPt,
                  formationUuid = tostring(f.uuid),
                  formationIndex = tonumber(f.index or 0),
                  joinMethod = jMethod,
                }}
                if not out.joined then out.joined = jRec end
                table.insert(out.joined_list, jRec)
                table.insert(out.dispatched, jRec)
                remStamBudget = remStamBudget - 1
              else
                table.insert(out.send_errors, 'JoinRally: ' .. tostring(errJ))
              end
            end
          end
        end
      end
    end
  end
end

if autoRally and not ranOutOfTroops and formIdx <= #forms and remStamBudget > 0 then
  local wpm = DataCenter and DataCenter.WorldPointManager
  local lc = LocalController and LocalController.instance and LocalController.instance()
  local normalSpecial = (MonsterSpecialType and MonsterSpecialType.Normal) or 0
  local cands = {{}}
  local seenPt = {{}}
  if wpm and wpm.allViewPoints and wpm.GetPointInfo then
    for ptIdx, ptObj in pairs(wpm.allViewPoints) do
      local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
      local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.pointId)) or 0
      if ptType == ((PointType and PointType.WorldMonster) or 4) and pnum > 0 then
        local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
        local pb = info and info._parsedExtra or nil
        if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
          local ok_pb, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
          if ok_pb and parsed then pb = parsed end
          if not pb then
            local pbName = (PBTypeDict and PBTypeDict[13]) or '.protobuf.WorldPointMonster'
            local ok_pb2, parsed2 = pcall(function() return PBController.ParsePbFromBytes(pbName, info.extraInfo) end)
            if ok_pb2 and parsed2 then pb = parsed2 end
          end
        end
        if pb and pb.monsterId and lc and TableName and TableName.Monster then
          local row = _safe_call(function() return lc:getLine(TableName.Monster, tostring(pb.monsterId)) end, nil)
          if row then
            local isBoss = tonumber(_safe_call(function() return row:getValue('boss') end, 0)) or 0
            local special = tonumber(_safe_call(function() return row:getValue('special') end, 0)) or 0
            local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
            if isBoss == 1 and special == normalSpecial and lv >= minLv and lv <= maxLv then
              local targetPt = tonumber(info and info.mainIndex or 0) or 0
              if targetPt <= 0 then targetPt = pnum end
              local claimKey = tostring(snap.serverId) .. ':' .. tostring(targetPt)
              if not seenPt[targetPt]
                 and not activeTargetPts[targetPt]
                 and not claimedPts[claimKey]
                 and not _is_point_blacklisted(blacklistedPts, targetPt, claimKey, nil)
                 and not _is_my_march_target(targetPt, occ.my_march_targets) then
                seenPt[targetPt] = true
                local d = snap.mainPos > 0 and _dist(snap.mainPos, targetPt) or 9999
                table.insert(cands, {{
                  pointId = targetPt,
                  claimKey = claimKey,
                  uuid = (info and info.uuid) or (pb and pb.uuid) or 0,
                  monsterId = tonumber(pb.monsterId) or 0,
                  level = lv,
                  dist = math.floor(d * 10) / 10,
                }})
              end
            end
          end
        end
      end
    end
  end

  table.sort(cands, function(a, b)
    if a.dist ~= b.dist then return a.dist < b.dist end
    return a.level > b.level
  end)

  local rallyType = (MarchTargetType and MarchTargetType.RALLY_FOR_BOSS) or 7
  local cIdx = 1
  while formIdx <= #forms and remStamBudget > 0 and cIdx <= #cands do
    local best = cands[cIdx]
    cIdx = cIdx + 1
    local f = nil
    f, formIdx = _next_ready_formation(forms, formIdx, dryRun)
    if not f then
      ranOutOfTroops = true
      break
    end
    local okS, errS = true, nil
    if not dryRun then
      if MarchUtil and MarchUtil.SendCreateMarchMessage then
        okS, errS = pcall(function()
          MarchUtil.SendCreateMarchMessage(
            tonumber(f.uuid) or f.uuid,
            rallyType,
            best.pointId,
            best.uuid or 0,
            1,
            true,
            true,
            snap.serverId
          )
        end)
      else
        okS, errS = false, 'MarchUtil.SendCreateMarchMessage unavailable'
      end
    end
    if okS then
      local sRec = {{
        mode = 'host_rally',
        pointId = best.pointId,
        targetPoint = best.pointId,
        warUuid = '',
        claimKey = best.claimKey,
        level = best.level,
        dist = best.dist,
        monsterId = best.monsterId,
        formationUuid = tostring(f.uuid),
        formationIndex = tonumber(f.index or 0),
      }}
      if not out.started_rally then out.started_rally = sRec end
      table.insert(out.started_rallies, sRec)
      table.insert(out.dispatched, sRec)
      activeTargetPts[best.pointId] = true
      remStamBudget = remStamBudget - 1
    else
      table.insert(out.send_errors, 'HostBoomerRally: ' .. tostring(errS))
      break
    end
  end

  if #out.dispatched == 0 and not ranOutOfTroops then
    local searchLv = effSearchLv
    if snap.mainPos > 0 and SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.FindMonster then
      if not dryRun then
        local okF, errF = pcall(function()
          SFSNetwork.SendMessage(MsgDefines.FindMonster, tonumber(snap.mainPos), searchLv, true, 0, normalSpecial)
        end)
        if okF then
          out.searched = true
          out.searched_level = searchLv
        else
          table.insert(out.send_errors, 'FindMonster(Boomer): ' .. tostring(errF))
        end
      else
        out.searched = true
        out.searched_level = searchLv
      end
    end
    out.reason = 'no_boomer_in_viewport_requested_scan'
  end
end

out.dispatched_count = #out.dispatched
if out.dispatched_count > 0 then
  out.status = 'dispatched'
  out.stop_reason = ''
  if not dryRun then
    out.active_marches = occ.active_marches + out.dispatched_count
    out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
  end
  out.message = string.format('Dispatched %d Boomer rally squad(s) (joined=%d, hosted=%d)', out.dispatched_count, #out.joined_list, #out.started_rallies)
elseif ranOutOfTroops then
  out.usable_formations = 0
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No stocked squads available for Boomers (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
elseif out.searched then
  out.status = 'searching'
  out.stop_reason = ''
  out.message = string.format('Searching map for Lv%d Boomer', out.searched_level)
elseif #out.send_errors > 0 then
  out.ok = false
  out.status = 'error'
  out.stop_reason = 'send_failed'
  out.message = out.send_errors[1]
else
  out.status = 'physical_limit'
  out.stop_reason = 'no_targets_found'
  out.message = 'No open Boomer rallies or viewport Boomers found'
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if not dry_run and context is not None:
        used_uuids: list[str] = []
        claimed_boomers = context.setdefault("claimed_boomer_points", [])
        for rec in (res.get("dispatched") or []):
            if isinstance(rec, dict):
                fu = rec.get("formationUuid")
                if fu:
                    used_uuids.append(str(fu))
                ck = rec.get("claimKey")
                if ck and ck not in claimed_boomers:
                    claimed_boomers.append(ck)
        if not used_uuids and isinstance(res.get("started_rally"), dict) and res["started_rally"].get("formationUuid"):
            used_uuids.append(str(res["started_rally"]["formationUuid"]))
        if used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return _ensure_step_contract(res, task_name="boomer_runs", default_message="Boomer runs step completed")


def run_auto_gather(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = (cfg or {}).get("auto_gather") or {}
    ctx = context or {}
    reserve_raw = ctx.get("reserve_override") if ctx.get("reserve_override") is not None else (cfg or {}).get("formation_reserve", 0)
    reserve = max(0, int(reserve_raw or 0))
    raw_prio = list(task_cfg.get("resource_priority", ["Diamonds", "Electricity", "Zent", "Wood", "Food"]))
    prio = _resolve_rss_resource_list(raw_prio)
    if not prio:
        prio = list(RSS_DEFAULT_PRIORITY)
    min_lv = max(1, int(task_cfg.get("min_level", 3) or 1))
    max_lv = max(min_lv, int(task_cfg.get("max_level", 9) or min_lv))
    max_dist = max(1.0, float(task_cfg.get("max_distance", 150) or 150))

    if not dry_run:
        sw = ensure_world_scene(cd, pid)
        if not sw.get("ok"):
            return _ensure_step_contract(
                {**sw, "ok": False, "status": "error", "stop_reason": sw.get("reason") or sw.get("error") or "world_scene_timeout"},
                task_name="auto_gather",
            )

    claimed_keys = list(ctx.get("claimed_gather_points", []))
    claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys) + "}"
    blacklisted_lua = _blacklisted_points_lua(context)
    prio_lua = "{" + ",".join(f"[{json.dumps(str(r))}]={i}" for i, r in enumerate(prio, 1)) + "}"

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local minLv = {min_lv}
local maxLv = {max_lv}
local maxDist = {max_dist}
local claimedPts = {claimed_lua}
local blacklistedPts = {blacklisted_lua}
local prioOrder = {prio_lua}
local resTypeMap = {{[1]='Food', [2]='Wood', [12]='Electricity', [14]='Zent', [15]='Diamonds'}}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local out = {{
  ok = true,
  task = 'auto_gather',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  candidates_found = 0,
  dispatched = _jarr({{}}),
  send_errors = _jarr({{}}),
  reason = '',
  action = 'none',
  message = '',
}}

local usable = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, false, not dryRun)
out.usable_formations = #usable
if #usable == 0 then
  out.reason = 'no_free_formation_above_reserve'
  out.action = 'all_squads_busy'
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = 'All squads currently busy, empty, or reserved'
  end
  return _enc(out)
end

local wpm = DataCenter and DataCenter.WorldPointManager
if not wpm or not wpm.allViewPoints or not wpm.GetPointInfo then
  out.reason = 'world_points_not_loaded'
  out.status = 'searching'
  out.stop_reason = ''
  out.message = 'World points not loaded yet'
  return _enc(out)
end

local lc = LocalController and LocalController.instance and LocalController.instance()
local cands = {{}}
for ptIdx, ptObj in pairs(wpm.allViewPoints) do
  local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
  local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.mainIndex or ptObj.pointId)) or 0
  if ptType == ((PointType and PointType.WorldResource) or 7) and pnum > 0 then
    local claimKey = tostring(snap.serverId) .. ':' .. tostring(pnum)
    if not claimedPts[claimKey]
       and not _is_point_blacklisted(blacklistedPts, pnum, claimKey, nil)
       and not _is_my_march_target(pnum, occ.my_march_targets) then
      local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
      local ri = info and info.resourceInfo or nil
      if ri and (tonumber(ri.gatherUuid or 0) or 0) == 0 and tostring(ri.ownerUid or '') == '' then
        local row = (lc and TableName and TableName.GatherResource) and _safe_call(function() return lc:getLine(TableName.GatherResource, tostring(ri.resourceId or 0)) end, nil) or nil
        if row then
          local rTypeNum = tonumber(_safe_call(function() return row:getValue('resource_type') end, nil) or _safe_call(function() return row:getValue('type') end, -1)) or -1
          local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
          local rName = resTypeMap[rTypeNum] or tostring(rTypeNum)
          local pRank = prioOrder[rName]
          if pRank and lv >= minLv and lv <= maxLv then
            local d = snap.mainPos > 0 and _dist(snap.mainPos, pnum) or 0
            if d <= maxDist then
              table.insert(cands, {{
                pointId = pnum,
                claimKey = claimKey,
                resourceType = rName,
                resourceTypeId = rTypeNum,
                level = lv,
                dist = math.floor(d * 10) / 10,
                prio = pRank,
              }})
            end
          end
        end
      end
    end
  end
end

out.candidates_found = #cands
if #cands == 0 then
  out.reason = 'no_matching_unoccupied_tile_in_viewport'
  out.status = 'physical_limit'
  out.stop_reason = 'no_targets_found'
  out.message = 'No matching unoccupied resource tile in viewport'
  return _enc(out)
end

table.sort(cands, function(a, b)
  if a.prio ~= b.prio then return a.prio < b.prio end
  if a.level ~= b.level then return a.level > b.level end
  return a.dist < b.dist
end)

local formIdx = 1
local ranOutOfTroops = false
local mType = tonumber((MarchTargetType and MarchTargetType.COLLECT) or 2) or 2
local srvId = tonumber(snap.serverId) or 0
for i = 1, #cands do
  local tile = cands[i]
  local f = nil
  f, formIdx = _next_ready_formation(usable, formIdx, dryRun)
  if not f then
    if #out.dispatched == 0 then ranOutOfTroops = true end
    break
  end
  local ptId = tonumber(tile.pointId) or 0
  local okS, errS = true, nil
  if not dryRun then
    if MarchUtil and MarchUtil.SendCreateMarchMessage and ptId > 0 and f and f.uuid then
      okS, errS = pcall(function()
        MarchUtil.SendCreateMarchMessage(
          tonumber(f.uuid) or f.uuid,
          mType,
          ptId,
          0,
          0,
          true,
          true,
          srvId
        )
      end)
    else
      okS, errS = false, 'MarchUtil.SendCreateMarchMessage unavailable'
    end
  end
  if okS then
    table.insert(out.dispatched, {{
      pointId = ptId,
      targetPoint = ptId,
      warUuid = '',
      claimKey = tile.claimKey,
      resourceType = tile.resourceType,
      resourceTypeId = tile.resourceTypeId,
      level = tonumber(tile.level) or 0,
      dist = tonumber(tile.dist) or 0,
      formationUuid = tostring(f.uuid),
      formationIndex = tonumber(f.index or 0),
    }})
  else
    table.insert(out.send_errors, 'GatherMarch: ' .. tostring(errS))
  end
end

out.dispatched_count = #out.dispatched
if out.dispatched_count > 0 then
  out.action = 'dispatched_gather'
  out.status = 'dispatched'
  out.stop_reason = ''
  if not dryRun then
    out.active_marches = occ.active_marches + out.dispatched_count
    out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
  end
  out.message = string.format('Dispatched %d squad(s) to gather resources', out.dispatched_count)
elseif ranOutOfTroops then
  out.usable_formations = 0
  out.action = 'all_squads_busy'
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = 'All squads currently busy, empty, or reserved'
  end
else
  out.ok = (#out.send_errors == 0)
  out.action = 'none'
  out.status = (#out.send_errors > 0) and 'error' or 'physical_limit'
  out.stop_reason = (#out.send_errors > 0) and 'send_failed' or 'no_targets_found'
  out.message = (#out.send_errors > 0) and out.send_errors[1] or (out.reason ~= '' and out.reason or 'No resource tiles gathered')
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if not dry_run and context is not None and isinstance(res.get("dispatched"), list):
        used_uuids: list[str] = []
        claimed = context.setdefault("claimed_gather_points", [])
        for item in res["dispatched"]:
            if isinstance(item, dict):
                ck = item.get("claimKey")
                if ck and ck not in claimed:
                    claimed.append(ck)
                if item.get("formationUuid"):
                    used_uuids.append(str(item["formationUuid"]))
        if used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return _ensure_step_contract(res, task_name="auto_gather", default_message="Auto gather step completed")


def run_furylord(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Attack/rally Furylord at 03:00 exact (or when forced via Map Kills) up to 4 times daily."""
    fl_cfg = (cfg or {}).get("furylord") or {}
    ctx = context or {}
    exact_hour = int(fl_cfg.get("exact_hour", 3))
    exact_minute = int(fl_cfg.get("exact_minute", 0))
    window_min = max(1, int(fl_cfg.get("window_minutes", 20)))
    max_attacks = max(1, int(fl_cfg.get("max_attacks", 4)))
    form_index = int(fl_cfg.get("formation_index", 1))
    prefer_rally = bool(fl_cfg.get("prefer_rally", True))
    claim_rewards = bool(fl_cfg.get("claim_rewards", True))
    join_open = bool(fl_cfg.get("join_open_rallies", True))
    reserve_raw = ctx.get("reserve_override") if ctx.get("reserve_override") is not None else 0
    reserve = max(0, int(reserve_raw or 0))
    has_min_stam_override = ctx.get("min_stamina_override") is not None
    min_stamina = max(0, int(ctx.get("min_stamina_override") or 0)) if has_min_stam_override else 0
    stamina_cost = max(0, int(ctx.get("stamina_cost_override") if ctx.get("stamina_cost_override") is not None else fl_cfg.get("stamina_cost", 0)))

    now_dt = _now_dt(context)
    target_dt = now_dt.replace(hour=exact_hour, minute=exact_minute, second=0, microsecond=0)
    delta_sec = (now_dt - target_dt).total_seconds()
    in_window = (0 <= delta_sec <= window_min * 60) or bool(ctx.get("force_furylord"))
    used_today = _get_daily_count(context, client_state, pid, "furylord_attacks", now_dt)
    remaining_today = max(0, max_attacks - used_today)

    blacklisted_lua = _blacklisted_points_lua(context)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local inWindow = {str(in_window).lower()}
local remaining = {remaining_today}
local formIdx = {form_index}
local reserve = {reserve}
local preferRally = {str(prefer_rally).lower()}
local claimRew = {str(claim_rewards).lower()}
local joinOpen = {str(join_open).lower()}
local minStam = {min_stamina}
local staminaCost = {stamina_cost}
local blacklistedPts = {blacklisted_lua}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local out = {{
  ok = true,
  task = 'furylord',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  player_uid = snap.uid,
  message = '',
  in_window = inWindow,
  is_open = false,
  in_act = false,
  boss_count = 0,
  open_rallies = 0,
  reward_count = 0,
  max_reward_count = 0,
  target_point = 0,
  claimed_rewards = false,
  dispatched = _jarr({{}}),
  joined_rallies = _jarr({{}}),
  send_errors = _jarr({{}}),
  fast_repeat = false,
  fast_repeat_sec = 10,
  reason = '',
}}

local rbm = DataCenter and DataCenter.ActRoamingBossManager
if not rbm then
  out.reason = 'roaming_boss_manager_unavailable'
  out.status = 'physical_limit'
  out.stop_reason = 'not_detected'
  out.message = 'ActRoamingBossManager unavailable'
  return _enc(out)
end

out.is_open = (rbm.IsActOpen and _safe_call(function() return rbm:IsActOpen() end, false)) and true or false
out.in_act = (rbm.IsInAct and _safe_call(function() return rbm:IsInAct() end, false)) and true or false

local normalRewardType = (RoamingBossRewardType and RoamingBossRewardType.Normal) or 2
local hasLiveRewardCap = false
if rbm.GetBossRewardCount then
  local okRC, rc = pcall(function() return rbm:GetBossRewardCount(normalRewardType) end)
  if okRC and rc ~= nil then
    out.reward_count = tonumber(rc) or 0
  end
end
if rbm.GetMaxBossRewardCount then
  local okMR, mr = pcall(function() return rbm:GetMaxBossRewardCount(normalRewardType) end)
  if okMR and mr ~= nil then
    out.max_reward_count = tonumber(mr) or 0
    if out.max_reward_count > 0 then hasLiveRewardCap = true end
  end
end

if claimRew and rbm.SendGetBossReward and out.reward_count > 0 then
  if not dryRun then
    local okCR, errCR = pcall(function() rbm:SendGetBossReward({{}}) end)
    if okCR then
      out.claimed_rewards = true
    else
      table.insert(out.send_errors, 'SendGetBossReward: ' .. tostring(errCR))
    end
  else
    out.claimed_rewards = true
  end
end

local bosses = {{}}
if rbm.GetBossInfoListNew then
  local okB, resB = pcall(function() return rbm:GetBossInfoListNew() end)
  if okB and type(resB) == 'table' then bosses = resB end
end
local targetUuid = 0
for _, b in pairs(bosses) do
  if type(b) == 'table' then
    out.boss_count = out.boss_count + 1
    local pt = (tonumber(b.pointId or 0) or 0) > 0 and tonumber(b.pointId) or (tonumber(b.pos or 0) or 0) > 0 and tonumber(b.pos) or (tonumber(b.tilePos or 0) or 0)
    if pt > 0 and out.target_point == 0 and not _is_point_blacklisted(blacklistedPts, pt, nil, nil) then
      out.target_point = pt
      targetUuid = b.uuid or 0
    end
  end
end

-- Fallback scan of WorldPointManager for RoamingBossNormal (27) / RoamingBossSpecial (28)
local wpm = DataCenter and DataCenter.WorldPointManager
local lc = LocalController and LocalController.instance and LocalController.instance()
if out.target_point == 0 and wpm and wpm.allViewPoints and wpm.GetPointInfo and lc and TableName and TableName.Monster then
  local roamNorm = (MonsterSpecialType and MonsterSpecialType.RoamingBossNormal) or 27
  local roamSpec = (MonsterSpecialType and MonsterSpecialType.RoamingBossSpecial) or 28
  local bestDist = 1e9
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
    local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.pointId)) or 0
    if ptType == ((PointType and PointType.WorldMonster) or 4) and pnum > 0 then
      local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
      local pb = info and info._parsedExtra or nil
      if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
        local okP, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
        if okP and parsed then pb = parsed end
      end
      if pb and pb.monsterId then
        local row = _safe_call(function() return lc:getLine(TableName.Monster, tostring(pb.monsterId)) end, nil)
        if row then
          local sp = tonumber(_safe_call(function() return row:getValue('special') end, 0)) or 0
          if sp == roamNorm or sp == roamSpec then
            local tpt = tonumber(info and info.mainIndex or 0) or 0
            if tpt <= 0 then tpt = pnum end
            out.boss_count = out.boss_count + 1
            if not _is_point_blacklisted(blacklistedPts, tpt, nil, nil) then
              local d = snap.mainPos > 0 and _dist(snap.mainPos, tpt) or 0
              if d < bestDist then
                bestDist = d
                out.target_point = tpt
                targetUuid = (info and info.uuid) or (pb and pb.uuid) or 0
              end
            end
          end
        end
      end
    end
  end
end

if out.target_point > 0 and targetUuid == 0 and wpm and wpm.GetPointInfo then
  local pi = _safe_call(function() return wpm:GetPointInfo(out.target_point) end, nil)
  if pi and pi.uuid then targetUuid = pi.uuid end
end

-- Scan open alliance Furylord rallies (AllianceTeamType.ATTACK_ROAMING_BOSS = 14)
local wm = DataCenter and DataCenter.AllianceWarDataManager
local flRallies = {{}}
local flTeamType = (AllianceTeamType and AllianceTeamType.ATTACK_ROAMING_BOSS) or 14
if snap.inAlliance and wm and wm.GetAllAllianceWar then
  local wars = _safe_call(function() return wm:GetAllAllianceWar() end, {{}}) or {{}}
  for _, w in pairs(wars) do
    if type(w) == 'table' then
      local wType = tonumber(w.type or -1) or -1
      if wType == flTeamType and w.uuid then
        local wPt = tonumber(w.targetPointId or w.targetPos or w.targetPoint or w.pointId or out.target_point) or out.target_point
        out.open_rallies = out.open_rallies + 1
        local alreadyIn = wm.HasRallyFormationForInfo and _safe_call(function() return wm:HasRallyFormationForInfo(w) end, false)
        if not alreadyIn and tostring(w.attackUid or '') ~= tostring(snap.uid or '') and not _is_point_blacklisted(blacklistedPts, wPt, nil, w.uuid) then
          table.insert(flRallies, w)
        end
      end
    end
  end
end

if not inWindow then
  out.reason = 'outside_0300_window'
  out.status = 'physical_limit'
  out.stop_reason = 'outside_window'
  out.message = 'Outside scheduled Furylord window'
  return _enc(out)
end
if hasLiveRewardCap and out.reward_count >= out.max_reward_count then
  out.reason = 'daily_reward_limit_reached'
  out.status = 'physical_limit'
  out.stop_reason = 'daily_limit_reached'
  out.message = string.format('Daily Furylord reward limit reached (%d/%d)', out.reward_count, out.max_reward_count)
  return _enc(out)
end
if remaining <= 0 then
  out.reason = 'daily_4x_limit_reached'
  out.status = 'physical_limit'
  out.stop_reason = 'daily_limit_reached'
  out.message = 'Daily Furylord attack limit reached'
  return _enc(out)
end
if not (out.is_open or out.in_act) and out.boss_count == 0 and #flRallies == 0 then
  out.reason = 'event_not_active'
  out.status = 'physical_limit'
  out.stop_reason = 'not_detected'
  out.message = 'Furylord event is not currently active'
  return _enc(out)
end
if staminaCost > 0 and snap.stamina < (minStam + staminaCost) then
  out.reason = 'out_of_stamina'
  out.status = 'physical_limit'
  out.stop_reason = 'out_of_stamina'
  out.message = string.format('Out of stamina (%d left, need >=%d)', snap.stamina, minStam + staminaCost)
  return _enc(out)
end
if out.target_point <= 0 and #flRallies == 0 then
  if rbm.SendGetBossInfo and not dryRun then
    local okBI, errBI = pcall(function() rbm:SendGetBossInfo() end)
    if not okBI then table.insert(out.send_errors, 'SendGetBossInfo: ' .. tostring(errBI)) end
  end
  out.reason = 'no_furylord_target'
  out.status = 'searching'
  out.stop_reason = ''
  out.fast_repeat = true
  out.message = 'Refreshing Furylord boss list from server'
  return _enc(out)
end

-- Pick designated formation (default F1) BEFORE applying reserve; apply reserve only to extra/non-F1 formations
local rawFree = _pick_free_formations(0, {_used_formations_lua(context, pid)}, false, not dryRun)
local chosenForm = nil
local rawOthers = {{}}
local otherForms = {{}}
local allReserved = (occ.total_formations > 0 and reserve >= occ.total_formations)
if not allReserved then
  for _, f in ipairs(rawFree) do
    if tonumber(f.index or 0) == formIdx and not chosenForm then
      chosenForm = f
    else
      table.insert(rawOthers, f)
    end
  end
  if #rawOthers > reserve then
    for i = reserve + 1, #rawOthers do
      table.insert(otherForms, rawOthers[i])
    end
  end
end
out.usable_formations = (chosenForm and 1 or 0) + #otherForms

local remBudget = hasLiveRewardCap and math.min(remaining, math.max(0, out.max_reward_count - out.reward_count)) or remaining

-- Join open alliance Furylord rallies (preferring non-F1 squads first so F1 can also rally/attack)
if joinOpen and #flRallies > 0 and out.usable_formations > 0 and remBudget > 0 then
  local joinPool = {{}}
  for _, f in ipairs(otherForms) do table.insert(joinPool, f) end
  if chosenForm and out.target_point <= 0 then
    table.insert(joinPool, chosenForm)
    chosenForm = nil
  end
  local poolIdx = 1
  for rIdx = 1, #flRallies do
    if remBudget <= 0 then break end
    local w = flRallies[rIdx]
    local f = nil
    f, poolIdx = _next_ready_formation(joinPool, poolIdx, dryRun)
    if not f then break end
    local okJ, errJ, jPt, jMethod = _join_rally_headless(f, w, out.target_point, snap.serverId, dryRun)
    if okJ then
      local jRec = {{
        mode = 'join_rally',
        warUuid = tostring(w.uuid),
        formationIndex = tonumber(f.index or 0),
        formationUuid = tostring(f.uuid),
        pointId = jPt,
        targetPoint = jPt,
        rally = true,
        joinMethod = jMethod,
        confirmed = (not dryRun and jMethod == 'send_create_march') and true or false,
      }}
      table.insert(out.joined_rallies, jRec)
      table.insert(out.dispatched, jRec)
      remBudget = remBudget - 1
    else
      table.insert(out.send_errors, 'FurylordJoinRally: ' .. tostring(errJ))
      break
    end
  end
end

-- Host/Attack Furylord with chosen formation (default F1)
if chosenForm and out.target_point > 0 and remBudget > 0 then
  local fReady = dryRun or _restock_formation(chosenForm)
  if not fReady then
    chosenForm = nil
    out.usable_formations = math.max(0, out.usable_formations - 1)
  elseif MarchUtil and MarchUtil.SendCreateMarchMessage then
    local tType = (MarchTargetType and (MarchTargetType.RALLY_FOR_ROAMING_BOSS or MarchTargetType.ATTACK_ROAMING_BOSS)) or 93
    local okS, errS = true, nil
    if not dryRun then
      okS, errS = pcall(function()
        MarchUtil.SendCreateMarchMessage(tonumber(chosenForm.uuid) or chosenForm.uuid, tType, out.target_point, targetUuid, preferRally and 1 or 0, 1, nil, snap.serverId)
      end)
    end
    if okS then
      local dRec = {{
        mode = preferRally and 'rally' or 'attack',
        formationIndex = formIdx,
        formationUuid = tostring(chosenForm.uuid),
        pointId = out.target_point,
        targetPoint = out.target_point,
        warUuid = '',
        rally = preferRally,
        confirmed = (not dryRun) and true or false,
      }}
      table.insert(out.dispatched, dRec)
      remBudget = remBudget - 1
      if remBudget > 0 then
        out.fast_repeat = true
      end
    else
      table.insert(out.send_errors, 'FurylordMarch: ' .. tostring(errS))
    end
  else
    table.insert(out.send_errors, 'MarchUtil.SendCreateMarchMessage unavailable')
  end
end

out.dispatched_count = #out.dispatched
if out.dispatched_count > 0 then
  out.status = 'dispatched'
  out.stop_reason = ''
  if not dryRun then
    out.active_marches = occ.active_marches + out.dispatched_count
    out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
  end
  out.message = string.format('Dispatched %d Furylord squad(s) (joined=%d)', out.dispatched_count, #out.joined_rallies)
elseif #out.send_errors > 0 then
  out.ok = false
  out.status = 'error'
  out.stop_reason = 'send_failed'
  out.message = out.send_errors[1]
elseif out.usable_formations == 0 then
  if occ.active_marches > 0 then
    out.reason = 'f1_busy_waiting_return'
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.fast_repeat = true
    out.message = string.format('Waiting for F%d to return (%d/%d active marches)', formIdx, occ.active_marches, occ.total_formations)
  else
    out.reason = 'no_free_formation'
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No usable squads available for Furylord (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
elseif not chosenForm then
  if occ.active_marches > 0 then
    out.reason = 'f1_busy_waiting_return'
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.fast_repeat = true
    out.message = string.format('Waiting for F%d to return (%d/%d active marches)', formIdx, occ.active_marches, occ.total_formations)
  else
    out.reason = 'f1_unavailable'
    out.status = 'physical_limit'
    out.stop_reason = 'f1_unavailable'
    out.message = string.format('Formation %d unavailable for Furylord (free=%d, total=%d)', formIdx, occ.free_formations, occ.total_formations)
  end
elseif occ.active_marches > 0 then
  out.status = 'waiting_for_squad'
  out.stop_reason = ''
  out.fast_repeat = true
  out.message = 'Waiting for Furylord rally or squad availability'
else
  out.status = 'physical_limit'
  out.stop_reason = 'no_targets_found'
  out.message = 'No actionable Furylord target or rally available'
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    eff_client_state = dict(client_state or {})
    if res.get("player_uid") and not any(eff_client_state.get(k) for k in ("uid", "playerUid", "id", "account_key", "label")):
        eff_client_state["uid"] = str(res["player_uid"])
        used_today = _get_daily_count(context, eff_client_state, pid, "furylord_attacks", now_dt)
    res["used_today"] = used_today
    res["max_attacks"] = max_attacks
    disp_items: list[dict[str, Any]] = []
    if isinstance(res.get("dispatched"), list):
        disp_items = [x for x in res["dispatched"] if isinstance(x, dict)]
    elif isinstance(res.get("dispatched"), dict):
        disp_items = [res["dispatched"]]
    if disp_items and not dry_run and res.get("ok"):
        used_uuids = [str(item["formationUuid"]) for item in disp_items if item.get("formationUuid")]
        if used_uuids and context is not None:
            _record_used_formations(context, pid, used_uuids)
        confirmed_direct = sum(
            1
            for item in disp_items
            if item.get("mode") in ("attack", "rally") and item.get("confirmed") is True
        )
        if confirmed_direct > 0:
            res["used_today"] = _increment_daily_count(
                context, eff_client_state, pid, "furylord_attacks", confirmed_direct, now_dt
            )
    if int(res.get("max_reward_count") or 0) > 0:
        res["used_today"] = max(int(res.get("used_today") or 0), int(res.get("reward_count") or 0))
    return _ensure_step_contract(res, task_name="furylord", default_message="Furylord step completed")


def run_rss_gather_step(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    resource_type: str | list[str] | tuple[str, ...] = "Diamonds",
    min_level: int = 1,
    max_level: int = 8,
    max_distance: float = 150.0,
    reserve: int = 0,
    search_level: int | None = None,
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
    *,
    resource_types: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Repeat-ready single step to gather one resource or a priority queue of resources.

    Uses verified aps gather resource.json resource_type IDs:
      15=Diamonds, 12=Electricity, 14=Zent, 2=Wood, 1=Food.
    """
    ctx = context or {}
    resolved = _resolve_rss_resource_list(resource_type, resource_types=resource_types)
    if not resolved:
        return _ensure_step_contract(
            {
                "ok": False,
                "task": "rss_gather",
                "dry_run": bool(dry_run),
                "status": "error",
                "stop_reason": "invalid_resource_type",
                "message": f"Unknown resource type: {resource_types if resource_types is not None else resource_type!r}",
                "dispatched": [],
            },
            task_name="rss_gather",
        )

    min_lv = max(1, int(min_level or 1))
    max_lv = max(min_lv, int(max_level or min_lv))
    max_dist = max(1.0, float(max_distance or 150.0))
    resv = max(0, int(reserve or 0))
    target_search_lv = max(min_lv, min(max_lv, int(search_level))) if search_level is not None else max_lv

    search_res_override = normalize_rss_resource_name(ctx.get("search_resource_type")) if ctx.get("search_resource_type") else ""
    search_res_name = search_res_override if search_res_override in resolved else resolved[0]
    search_res_id = RSS_RESOURCE_TYPE_IDS[search_res_name]

    early = _precheck_world_step_readiness(
        cd,
        pid,
        task_name="rss_gather",
        reserve=resv,
        context=context,
        dry_run=dry_run,
        extra_fields={"resource_types": list(resolved)},
    )
    if early is not None:
        return early

    claimed_keys = list(ctx.get("claimed_gather_points", []))
    claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys) + "}"
    blacklisted_lua = _blacklisted_points_lua(context)
    prio_lua = "{" + ",".join(f"[{json.dumps(str(r))}]={i}" for i, r in enumerate(resolved, 1)) + "}"
    prio_id_lua = "{" + ",".join(f"[{RSS_RESOURCE_TYPE_IDS[r]}]={i}" for i, r in enumerate(resolved, 1)) + "}"
    res_list_lua = "{" + ",".join(json.dumps(str(r)) for r in resolved) + "}"

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {resv}
local minLv = {min_lv}
local maxLv = {max_lv}
local maxDist = {max_dist}
local targetSearchLv = {target_search_lv}
local searchResName = {json.dumps(search_res_name)}
local searchResId = {search_res_id}
local claimedPts = {claimed_lua}
local blacklistedPts = {blacklisted_lua}
local prioOrder = {prio_lua}
local prioIdOrder = {prio_id_lua}
local resTypeMap = {{[1]='Food', [2]='Wood', [12]='Electricity', [14]='Zent', [15]='Diamonds'}}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local out = {{
  ok = true,
  task = 'rss_gather',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  message = '',
  resource_types = _jarr({res_list_lua}),
  candidates_found = 0,
  occupied_skipped = 0,
  find_res_point = 0,
  searched = false,
  searched_level = 0,
  searched_resource_type = '',
  searched_resource_id = 0,
  dispatched = _jarr({{}}),
  send_errors = _jarr({{}}),
}}

local usable = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, false, not dryRun)
out.usable_formations = #usable
if #usable == 0 then
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No usable squads available (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
  return _enc(out)
end

local wpm = DataCenter and DataCenter.WorldPointManager
local crm = DataCenter and DataCenter.CollectResourceManager
local lc = LocalController and LocalController.instance and LocalController.instance()
local cands = {{}}
local seenPt = {{}}

local function _consider_resource_point(pnum, ptObj, fromFindRes)
  pnum = tonumber(pnum) or 0
  if pnum <= 0 or seenPt[pnum] then return false end
  seenPt[pnum] = true
  local claimKey = tostring(snap.serverId) .. ':' .. tostring(pnum)
  if claimedPts[claimKey]
     or _is_point_blacklisted(blacklistedPts, pnum, claimKey, nil)
     or _is_my_march_target(pnum, occ.my_march_targets) then
    return false
  end
  local info = (wpm and wpm.GetPointInfo) and _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
  local ri = info and info.resourceInfo or nil
  if not ri then return false end
  local gUuid = tonumber(ri.gatherUuid or 0) or 0
  local ownerUid = tostring(ri.ownerUid or '')
  if gUuid ~= 0 or ownerUid ~= '' then
    out.occupied_skipped = out.occupied_skipped + 1
    return false
  end
  local row = (lc and TableName and TableName.GatherResource) and _safe_call(function() return lc:getLine(TableName.GatherResource, tostring(ri.resourceId or 0)) end, nil) or nil
  if not row then return false end
  local rTypeNum = tonumber(_safe_call(function() return row:getValue('resource_type') end, nil) or _safe_call(function() return row:getValue('type') end, -1)) or -1
  local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
  local rName = resTypeMap[rTypeNum] or tostring(rTypeNum)
  local pRank = prioOrder[rName] or prioIdOrder[rTypeNum]
  if not pRank or lv < minLv or lv > maxLv then return false end
  local d = snap.mainPos > 0 and _dist(snap.mainPos, pnum) or 0
  if d > maxDist then return false end
  table.insert(cands, {{
    pointId = pnum,
    claimKey = claimKey,
    resourceType = rName,
    resourceTypeId = rTypeNum,
    level = lv,
    dist = math.floor(d * 10) / 10,
    prio = pRank,
    fromFindRes = fromFindRes and true or false,
  }})
  return true
end

if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
    local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.mainIndex or ptObj.pointId)) or 0
    if ptType == ((PointType and PointType.WorldResource) or 7) and pnum > 0 then
      _consider_resource_point(pnum, ptObj, false)
    end
  end
end

-- Check CollectResourceManager:GetFindResPoint() directly so server-found tiles work even before camera pan
local findResPt = 0
if crm and crm.GetFindResPoint then
  findResPt = tonumber(_safe_call(function() return crm:GetFindResPoint() end, 0)) or 0
end
out.find_res_point = findResPt
if findResPt > 0 and not seenPt[findResPt] then
  local added = _consider_resource_point(findResPt, nil, true)
  if not added then
    local req = type(_G.__hzFindResReq) == 'table' and _G.__hzFindResReq or nil
    if req
       and (os.time() - (tonumber(req.ts) or 0)) <= 30
       and findResPt ~= (tonumber(req.prevPt) or 0)
       and (prioOrder[req.resName] or prioIdOrder[req.resId]) then
      local infoCheck = (wpm and wpm.GetPointInfo) and _safe_call(function() return wpm:GetPointInfo(findResPt) end, nil) or nil
      local hasRi = (type(infoCheck) == 'table' and infoCheck.resourceInfo ~= nil)
      if not hasRi then
        local claimKey = tostring(snap.serverId) .. ':' .. tostring(findResPt)
        if not claimedPts[claimKey]
           and not _is_point_blacklisted(blacklistedPts, findResPt, claimKey, nil)
           and not _is_my_march_target(findResPt, occ.my_march_targets) then
          local pRank = prioOrder[req.resName] or prioIdOrder[req.resId]
          local lv = tonumber(req.lv) or targetSearchLv
          local d = snap.mainPos > 0 and _dist(snap.mainPos, findResPt) or 0
          if pRank and lv >= minLv and lv <= maxLv and d <= maxDist then
            table.insert(cands, {{
              pointId = findResPt,
              claimKey = claimKey,
              resourceType = tostring(req.resName or searchResName),
              resourceTypeId = tonumber(req.resId or searchResId) or searchResId,
              level = lv,
              dist = math.floor(d * 10) / 10,
              prio = pRank,
              fromFindRes = true,
            }})
          end
        end
      end
    end
  end
end

out.candidates_found = #cands

if #cands > 0 then
  -- Highest priority resource first, then highest tile level, then closest distance
  table.sort(cands, function(a, b)
    if a.prio ~= b.prio then return a.prio < b.prio end
    if a.level ~= b.level then return a.level > b.level end
    return a.dist < b.dist
  end)

  local formIdx = 1
  local ranOutOfTroops = false
  local mType = tonumber((MarchTargetType and MarchTargetType.COLLECT) or 2) or 2
  local srvId = tonumber(snap.serverId) or 0
  for i = 1, #cands do
    local tile = cands[i]
    local f = nil
    f, formIdx = _next_ready_formation(usable, formIdx, dryRun)
    if not f then
      if #out.dispatched == 0 then ranOutOfTroops = true end
      break
    end
    local ptId = tonumber(tile.pointId) or 0
    local okS, errS = true, nil
    if not dryRun then
      if MarchUtil and MarchUtil.SendCreateMarchMessage and ptId > 0 and f and f.uuid then
        okS, errS = pcall(function()
          MarchUtil.SendCreateMarchMessage(
            tonumber(f.uuid) or f.uuid,
            mType,
            ptId,
            0,
            0,
            true,
            true,
            srvId
          )
        end)
      else
        okS, errS = false, 'MarchUtil.SendCreateMarchMessage unavailable'
      end
    end
    if okS then
      if tile.fromFindRes then
        _G.__hzFindResReq = nil
      end
      table.insert(out.dispatched, {{
        pointId = ptId,
        targetPoint = ptId,
        warUuid = '',
        claimKey = tile.claimKey,
        resourceType = tile.resourceType,
        resourceTypeId = tile.resourceTypeId,
        level = tonumber(tile.level) or 0,
        dist = tonumber(tile.dist) or 0,
        formationUuid = tostring(f.uuid),
        formationIndex = tonumber(f.index or 0),
        fromFindRes = tile.fromFindRes and true or false,
      }})
    else
      table.insert(out.send_errors, 'GatherMarch: ' .. tostring(errS))
    end
  end

  out.dispatched_count = #out.dispatched
  if out.dispatched_count > 0 then
    out.status = 'dispatched'
    out.stop_reason = ''
    if not dryRun then
      out.active_marches = occ.active_marches + out.dispatched_count
      out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
    end
    local firstTile = out.dispatched[1]
    out.message = string.format('Dispatched %d squad(s) to %s (top Lv%d)', out.dispatched_count, tostring(firstTile.resourceType), tonumber(firstTile.level) or 0)
  elseif ranOutOfTroops then
    out.usable_formations = 0
    if occ.active_marches > 0 then
      out.status = 'waiting_for_squad'
      out.stop_reason = ''
      out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
    else
      out.status = 'physical_limit'
      out.stop_reason = 'no_troops_or_formations'
      out.message = string.format('No stocked squads available to gather (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
    end
  else
    out.ok = false
    out.status = 'error'
    out.stop_reason = 'send_failed'
    out.message = (#out.send_errors > 0) and out.send_errors[1] or 'Failed to dispatch gather march'
  end
  return _enc(out)
end

-- No matching unoccupied tiles in viewport while squads are usable: send FindResourcePoint (nparams=4)
out.searched_level = targetSearchLv
out.searched_resource_type = searchResName
out.searched_resource_id = searchResId
if not dryRun then
  if SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.FindResourcePoint then
    local okF, errF = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.FindResourcePoint, searchResId, targetSearchLv, '')
    end)
    if okF then
      _G.__hzFindResReq = {{
        resId = searchResId,
        resName = searchResName,
        lv = targetSearchLv,
        prevPt = findResPt,
        ts = os.time(),
      }}
      out.searched = true
      out.status = 'searching'
      out.stop_reason = ''
      out.message = string.format('Searching map for Lv%d %s (resType=%d)', targetSearchLv, searchResName, searchResId)
    else
      table.insert(out.send_errors, 'FindResourcePoint: ' .. tostring(errF))
      out.ok = false
      out.status = 'error'
      out.stop_reason = 'find_resource_failed'
      out.message = 'FindResourcePoint failed: ' .. tostring(errF)
    end
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_targets_found'
    out.message = 'No matching unoccupied tiles in viewport and FindResourcePoint unavailable'
  end
else
  out.searched = true
  out.status = 'searching'
  out.stop_reason = ''
  out.message = string.format('[DRY-RUN] Would search for Lv%d %s (resType=%d)', targetSearchLv, searchResName, searchResId)
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if not dry_run and context is not None and isinstance(res.get("dispatched"), list):
        used_uuids: list[str] = []
        claimed = context.setdefault("claimed_gather_points", [])
        for item in res["dispatched"]:
            if isinstance(item, dict):
                ck = item.get("claimKey")
                if ck and ck not in claimed:
                    claimed.append(ck)
                if item.get("formationUuid"):
                    used_uuids.append(str(item["formationUuid"]))
        if used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return _ensure_step_contract(res, task_name="rss_gather", default_message="RSS gather step completed")


def run_standalone_npc_step(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    min_level: int = 0,
    max_level: int = 0,
    max_distance: float = 150.0,
    reserve: int = 0,
    min_stamina: int = 0,
    stamina_cost: int = 10,
    search_level: int | None = None,
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Repeat-ready single step to hunt standalone world map NPCs (APS_monster boss=0, special=0)."""
    ctx = context or {}
    req_min_lv = max(0, int(min_level or 0))
    req_max_lv = max(0, int(max_level or 0))
    max_dist = max(1.0, float(max_distance or 150.0))
    resv = max(0, int(reserve or 0))
    min_stam = max(0, int(min_stamina or 0))
    stam_cost = max(1, int(stamina_cost or 10))
    req_search_lv = max(0, int(search_level)) if search_level is not None else 0

    early = _precheck_world_step_readiness(
        cd,
        pid,
        task_name="standalone_npc",
        reserve=resv,
        context=context,
        dry_run=dry_run,
        min_stamina=min_stam,
        stamina_cost=stam_cost,
        strict_stamina_reserve=True,
    )
    if early is not None:
        return early

    claimed_keys = list(ctx.get("claimed_npc_points", []))
    claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys) + "}"
    blacklisted_lua = _blacklisted_points_lua(context)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reqMinLv = {req_min_lv}
local reqMaxLv = {req_max_lv}
local maxDist = {max_dist}
local reserve = {resv}
local minStam = {min_stam}
local staminaCost = {stam_cost}
local reqSearchLv = {req_search_lv}
local claimedPts = {claimed_lua}
local blacklistedPts = {blacklisted_lua}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local mm = DataCenter and DataCenter.MonsterManager
local unlockedMaxLv = 0
if mm then
  if mm.GetCanFindMonsterMaxLevel then
    unlockedMaxLv = tonumber(_safe_call(function() return mm:GetCanFindMonsterMaxLevel() end, 0)) or 0
  end
  if unlockedMaxLv <= 0 and mm.find_monster_max_level then
    unlockedMaxLv = tonumber(mm.find_monster_max_level) or 0
  end
end
local hasUnlockedCap = (unlockedMaxLv > 0)
if not hasUnlockedCap then unlockedMaxLv = 30 end

local effMaxLv = (reqMaxLv > 0) and reqMaxLv or unlockedMaxLv
if hasUnlockedCap and effMaxLv > unlockedMaxLv then
  effMaxLv = unlockedMaxLv
end
local effMinLv = (reqMinLv > 0) and math.min(reqMinLv, effMaxLv) or 1
local targetSearchLv = (reqSearchLv > 0) and math.max(effMinLv, math.min(effMaxLv, reqSearchLv)) or effMaxLv

local out = {{
  ok = true,
  task = 'standalone_npc',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  message = '',
  unlocked_max_level = unlockedMaxLv,
  effective_min_level = effMinLv,
  effective_max_level = effMaxLv,
  candidates_found = 0,
  searched = false,
  searched_level = 0,
  dispatched = _jarr({{}}),
  send_errors = _jarr({{}}),
}}

local maxByStamina = math.floor((snap.stamina - minStam) / staminaCost)
if snap.stamina < math.max(staminaCost, minStam) or maxByStamina <= 0 then
  out.status = 'physical_limit'
  out.stop_reason = 'out_of_stamina'
  out.message = string.format('Out of stamina (%d left, need >=%d with reserve %d)', snap.stamina, math.max(staminaCost, minStam + staminaCost), minStam)
  return _enc(out)
end

local usable = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, false, not dryRun)
out.usable_formations = #usable
if #usable == 0 then
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No usable squads available (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
  return _enc(out)
end

local wpm = DataCenter and DataCenter.WorldPointManager
local lc = LocalController and LocalController.instance and LocalController.instance()
local normalSpecial = (MonsterSpecialType and MonsterSpecialType.Normal) or 0
local cands = {{}}
local seenPt = {{}}

if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
    local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.pointId)) or 0
    if ptType == ((PointType and PointType.WorldMonster) or 4) and pnum > 0 then
      local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
      local pb = info and info._parsedExtra or nil
      if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
        local ok_pb, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
        if ok_pb and parsed then pb = parsed end
        if not pb then
          local pbName = (PBTypeDict and PBTypeDict[13]) or '.protobuf.WorldPointMonster'
          local ok_pb2, parsed2 = pcall(function() return PBController.ParsePbFromBytes(pbName, info.extraInfo) end)
          if ok_pb2 and parsed2 then pb = parsed2 end
        end
      end
      if pb and pb.monsterId and lc and TableName and TableName.Monster then
        local row = _safe_call(function() return lc:getLine(TableName.Monster, tostring(pb.monsterId)) end, nil)
        if row then
          local isBoss = tonumber(_safe_call(function() return row:getValue('boss') end, 0)) or 0
          local special = tonumber(_safe_call(function() return row:getValue('special') end, 0)) or 0
          local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
          if isBoss == 0 and special == normalSpecial and lv >= effMinLv and lv <= effMaxLv then
            local targetPt = tonumber(info and info.mainIndex or 0) or 0
            if targetPt <= 0 then targetPt = pnum end
            local claimKey = tostring(snap.serverId) .. ':' .. tostring(targetPt)
            if not seenPt[targetPt]
               and not claimedPts[claimKey]
               and not _is_point_blacklisted(blacklistedPts, targetPt, claimKey, nil)
               and not _is_my_march_target(targetPt, occ.my_march_targets) then
              seenPt[targetPt] = true
              local d = snap.mainPos > 0 and _dist(snap.mainPos, targetPt) or 0
              if d <= maxDist then
                table.insert(cands, {{
                  pointId = targetPt,
                  claimKey = claimKey,
                  uuid = (info and info.uuid) or (pb and pb.uuid) or 0,
                  monsterId = tonumber(pb.monsterId) or 0,
                  level = lv,
                  dist = math.floor(d * 10) / 10,
                }})
              end
            end
          end
        end
      end
    end
  end
end

out.candidates_found = #cands

if #cands > 0 then
  -- Highest level standalone NPC first, then closest distance
  table.sort(cands, function(a, b)
    if a.level ~= b.level then return a.level > b.level end
    return a.dist < b.dist
  end)

  local formIdx = 1
  local remStamBudget = maxByStamina
  local ranOutOfTroops = false
  local atkType = (MarchTargetType and MarchTargetType.ATTACK_MONSTER) or 1
  local srvId = tonumber(snap.serverId) or 0
  for i = 1, #cands do
    if remStamBudget <= 0 then break end
    local npc = cands[i]
    local f = nil
    f, formIdx = _next_ready_formation(usable, formIdx, dryRun)
    if not f then
      if #out.dispatched == 0 then ranOutOfTroops = true end
      break
    end
    local ptId = tonumber(npc.pointId) or 0
    local okS, errS = true, nil
    if not dryRun then
      if MarchUtil and MarchUtil.SendCreateMarchMessage and ptId > 0 and f and f.uuid then
        okS, errS = pcall(function()
          MarchUtil.SendCreateMarchMessage(
            tonumber(f.uuid) or f.uuid,
            atkType,
            ptId,
            npc.uuid or 0,
            0,
            true,
            true,
            srvId
          )
        end)
      else
        okS, errS = false, 'MarchUtil.SendCreateMarchMessage unavailable'
      end
    end
    if okS then
      table.insert(out.dispatched, {{
        pointId = ptId,
        targetPoint = ptId,
        warUuid = '',
        claimKey = npc.claimKey,
        monsterId = npc.monsterId,
        level = npc.level,
        dist = npc.dist,
        formationUuid = tostring(f.uuid),
        formationIndex = tonumber(f.index or 0),
      }})
      remStamBudget = remStamBudget - 1
    else
      table.insert(out.send_errors, 'AttackNPC: ' .. tostring(errS))
    end
  end

  out.dispatched_count = #out.dispatched
  if out.dispatched_count > 0 then
    out.status = 'dispatched'
    out.stop_reason = ''
    if not dryRun then
      out.active_marches = occ.active_marches + out.dispatched_count
      out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
    end
    out.message = string.format('Dispatched %d squad(s) to attack standalone NPCs (top Lv%d)', out.dispatched_count, tonumber(out.dispatched[1].level) or 0)
  elseif ranOutOfTroops then
    out.usable_formations = 0
    if occ.active_marches > 0 then
      out.status = 'waiting_for_squad'
      out.stop_reason = ''
      out.message = string.format('Waiting for returning squad (%d/%d active marches)', occ.active_marches, occ.total_formations)
    else
      out.status = 'physical_limit'
      out.stop_reason = 'no_troops_or_formations'
      out.message = string.format('No stocked squads available for standalone NPCs (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
    end
  else
    out.ok = false
    out.status = 'error'
    out.stop_reason = 'send_failed'
    out.message = (#out.send_errors > 0) and out.send_errors[1] or 'Failed to dispatch standalone NPC march'
  end
  return _enc(out)
end

-- No matching NPCs in viewport: send FindMonster (nparams=6: mainPos, targetLevel, false, 0, 0)
out.searched_level = targetSearchLv
if not dryRun then
  if snap.mainPos > 0 and SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.FindMonster then
    local okF, errF = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.FindMonster, tonumber(snap.mainPos), targetSearchLv, false, 0, normalSpecial)
    end)
    if okF then
      out.searched = true
      out.status = 'searching'
      out.stop_reason = ''
      out.message = string.format('Searching map for Lv%d standalone NPC', targetSearchLv)
    else
      table.insert(out.send_errors, 'FindMonster(NPC): ' .. tostring(errF))
      out.ok = false
      out.status = 'error'
      out.stop_reason = 'find_monster_failed'
      out.message = 'FindMonster failed: ' .. tostring(errF)
    end
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_targets_found'
    out.message = 'No matching standalone NPCs in viewport and FindMonster unavailable'
  end
else
  out.searched = true
  out.status = 'searching'
  out.stop_reason = ''
  out.message = string.format('[DRY-RUN] Would search for Lv%d standalone NPC', targetSearchLv)
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if not dry_run and context is not None and isinstance(res.get("dispatched"), list):
        used_uuids: list[str] = []
        claimed = context.setdefault("claimed_npc_points", [])
        for item in res["dispatched"]:
            if isinstance(item, dict):
                ck = item.get("claimKey")
                if ck and ck not in claimed:
                    claimed.append(ck)
                if item.get("formationUuid"):
                    used_uuids.append(str(item["formationUuid"]))
        if used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return _ensure_step_contract(res, task_name="standalone_npc", default_message="Standalone NPC step completed")


def run_saga_kill_step(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    reserve: int = 0,
    min_stamina: int = 0,
    stamina_cost: int = 10,
    allow_summon: bool = True,
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Repeat-ready single step for Survival Saga Zombies (ChallengeBoss=4 / MonsterTowerAlBoss=40)."""
    ctx = context or {}
    resv = max(0, int(reserve or 0))
    min_stam = max(0, int(min_stamina or 0))
    stam_cost = max(1, int(stamina_cost or 10))
    summon_ok = bool(allow_summon) and not bool(ctx.get("summon_cooldown_active", False))

    early = _precheck_world_step_readiness(
        cd,
        pid,
        task_name="saga_boss",
        reserve=resv,
        context=context,
        dry_run=dry_run,
        min_stamina=min_stam,
        stamina_cost=stam_cost,
        strict_stamina_reserve=True,
        extra_fields={"detected": False},
    )
    if early is not None:
        return early

    claimed_keys = list(ctx.get("claimed_saga_points", []))
    claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys) + "}"
    blacklisted_lua = _blacklisted_points_lua(context)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {resv}
local minStam = {min_stam}
local staminaCost = {stam_cost}
local allowSummon = {str(summon_ok).lower()}
local claimedPts = {claimed_lua}
local blacklistedPts = {blacklisted_lua}

local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local challengeSpecial = (MonsterSpecialType and MonsterSpecialType.ChallengeBoss) or 4
local alBossSpecial = (MonsterSpecialType and MonsterSpecialType.MonsterTowerAlBoss) or 40

local out = {{
  ok = true,
  task = 'saga_boss',
  dry_run = dryRun,
  status = 'physical_limit',
  stop_reason = '',
  dispatched_count = 0,
  free_formations = occ.free_formations,
  usable_formations = 0,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  stamina = snap.stamina,
  message = '',
  detected = false,
  active = false,
  act_id = 0,
  difficulty_selected = false,
  can_rally = false,
  have_al_boss_act = false,
  boss_count = 0,
  open_rallies = 0,
  summoned = false,
  searched = false,
  dispatched = _jarr({{}}),
  joined_rallies = _jarr({{}}),
  send_errors = _jarr({{}}),
}}

local mtd = DataCenter and DataCenter.ActMonsterTowerData
local actId = 0
local activeInfo = nil
local isEnded = false
local diffSelected = false
local canRally = false
local haveAlBoss = false
local alActInfo = nil

if mtd then
  if mtd.GetActiveChallengeInfo then
    local ac = _safe_call(function() return mtd:GetActiveChallengeInfo() end, nil)
    if type(ac) == 'table' then
      activeInfo = ac
      actId = tonumber(ac.actId or ac.activityId or ac.id or 0) or 0
    end
  end
  if actId <= 0 and mtd.GetInfoActAll then
    local allActs = _safe_call(function() return mtd:GetInfoActAll() end, nil)
    if type(allActs) == 'table' then
      for k, v in pairs(allActs) do
        local candId = 0
        if type(v) == 'table' then
          candId = tonumber(v.actId or v.activityId or v.id or k or 0) or 0
        else
          candId = tonumber(k or 0) or 0
        end
        if candId > 0 then
          local endedCand = (mtd.CheckIfIsToEnd) and (_safe_call(function() return mtd:CheckIfIsToEnd(candId) end, false) and true or false) or false
          if not endedCand then
            actId = candId
            if not activeInfo and type(v) == 'table' then activeInfo = v end
            break
          end
        end
      end
    end
  end
  if actId > 0 and mtd.CheckIfIsToEnd then
    isEnded = _safe_call(function() return mtd:CheckIfIsToEnd(actId) end, false) and true or false
  end
  if actId > 0 and mtd.HasSelectedDifficulty then
    diffSelected = _safe_call(function() return mtd:HasSelectedDifficulty(actId) end, false) and true or false
  end
  if mtd.CanShowChallengeBossRally then
    canRally = _safe_call(function() return mtd:CanShowChallengeBossRally() end, false) and true or false
  end
  if mtd.CheckHaveAlBossAct then
    haveAlBoss = _safe_call(function() return mtd:CheckHaveAlBossAct() end, false) and true or false
  end
  if actId > 0 and mtd.GetAllianceActInfo then
    alActInfo = _safe_call(function() return mtd:GetAllianceActInfo(actId) end, nil)
  end
end

local sagaActive = ((activeInfo ~= nil and not isEnded) or (actId > 0 and not isEnded) or haveAlBoss or (type(alActInfo) == 'table'))
out.active = sagaActive and true or false
out.act_id = actId
out.difficulty_selected = diffSelected and true or false
out.can_rally = canRally and true or false
out.have_al_boss_act = haveAlBoss and true or false

-- Scan WorldPointManager for ChallengeBoss (4) and MonsterTowerAlBoss (40)
local wpm = DataCenter and DataCenter.WorldPointManager
local lc = LocalController and LocalController.instance and LocalController.instance()
local sagaBosses = {{}}
local sagaPtSet = {{}}
local seenPt = {{}}

local function _parse_challenge_boss_pb(info, pb)
  if type(info) == 'table' and type(info.challengeBossInfo) == 'table' then
    return info.challengeBossInfo
  end
  if type(pb) == 'table' and (pb.bossOwnerUid ~= nil or pb.allianceId ~= nil) then
    return pb
  end
  if PBController and PBController.ParsePbFromBytes then
    local rawBytes = (type(pb) == 'table' and pb.extraInfo) or (type(info) == 'table' and info.extraInfo) or nil
    if rawBytes then
      local pbType = (PBTypeDict and PBTypeDict[10]) or '.protobuf.ChallengeBossInfo'
      local ok1, p1 = pcall(function() return PBController.ParsePbFromBytes(pbType, rawBytes) end)
      if ok1 and type(p1) == 'table' and (p1.bossOwnerUid ~= nil or p1.allianceId ~= nil or p1.monsterId ~= nil) then
        return p1
      end
      local ok2, p2 = pcall(function() return PBController.ParsePbFromBytes('protobuf.ChallengeBossInfo', rawBytes) end)
      if ok2 and type(p2) == 'table' and (p2.bossOwnerUid ~= nil or p2.allianceId ~= nil or p2.monsterId ~= nil) then
        return p2
      end
    end
  end
  return nil
end

if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
    local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.pointId)) or 0
    if ptType == ((PointType and PointType.WorldMonster) or 4) and pnum > 0 then
      local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
      local pb = info and info._parsedExtra or nil
      if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
        local ok_pb, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
        if ok_pb and parsed then pb = parsed end
        if not pb then
          local pbName = (PBTypeDict and PBTypeDict[13]) or '.protobuf.WorldPointMonster'
          local ok_pb2, parsed2 = pcall(function() return PBController.ParsePbFromBytes(pbName, info.extraInfo) end)
          if ok_pb2 and parsed2 then pb = parsed2 end
        end
      end
      local cb = _parse_challenge_boss_pb(info, pb)
      local monsterId = (pb and pb.monsterId) or (cb and cb.monsterId) or nil
      if monsterId and lc and TableName and TableName.Monster then
        local row = _safe_call(function() return lc:getLine(TableName.Monster, tostring(monsterId)) end, nil)
        if row then
          local special = tonumber(_safe_call(function() return row:getValue('special') end, 0)) or 0
          if special == challengeSpecial or special == alBossSpecial then
            local targetPt = tonumber(info and info.mainIndex or 0) or 0
            if targetPt <= 0 then targetPt = pnum end
            sagaPtSet[targetPt] = true
            if not seenPt[targetPt] then
              seenPt[targetPt] = true
              local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
              local bossOwnerUid = tostring((cb and (cb.bossOwnerUid or cb.ownerUid)) or (pb and (pb.bossOwnerUid or pb.ownerUid)) or (info and info.ownerUid) or '')
              local bossAllyId = tostring((cb and (cb.allianceId or cb.allianceUid)) or (pb and (pb.allianceId or pb.allianceUid)) or (info and (info.allianceId or info.allianceUid)) or '')
              local isOwn = (bossOwnerUid ~= '' and bossOwnerUid == snap.uid)
              local isAlBoss = (special == alBossSpecial)
              local isAlly = (bossAllyId ~= '' and snap.allianceUid ~= '' and bossAllyId == snap.allianceUid)
              local prio = isOwn and 1 or ((isAlBoss or isAlly) and 2 or 3)
              local d = snap.mainPos > 0 and _dist(snap.mainPos, targetPt) or 0
              local claimKey = tostring(snap.serverId) .. ':' .. tostring(targetPt)
              local skipBoss = (claimedPts[claimKey] and true or false)
                or _is_point_blacklisted(blacklistedPts, targetPt, claimKey, nil)
                or _is_my_march_target(targetPt, occ.my_march_targets)
              table.insert(sagaBosses, {{
                pointId = targetPt,
                claimKey = claimKey,
                uuid = (info and info.uuid) or (pb and pb.uuid) or 0,
                monsterId = tonumber(monsterId) or 0,
                level = lv,
                special = special,
                bossOwnerUid = bossOwnerUid,
                allianceId = bossAllyId,
                isOwn = isOwn,
                isAlly = isAlly,
                isAlBoss = isAlBoss,
                prio = prio,
                dist = math.floor(d * 10) / 10,
                claimed = skipBoss,
              }})
            end
          end
        end
      end
    end
  end
end

out.boss_count = #sagaBosses

-- Scan AllianceWarDataManager for open alliance Saga rallies
local wm = DataCenter and DataCenter.AllianceWarDataManager
local sagaRallies = {{}}
if snap.inAlliance and wm and wm.GetAllAllianceWar then
  local wars = _safe_call(function() return wm:GetAllAllianceWar() end, {{}}) or {{}}
  for _, w in pairs(wars) do
    if type(w) == 'table' and w.uuid then
      local tpt = tonumber(w.targetPointId or w.targetPos or w.targetPoint or w.pointId or 0) or 0
      local isSagaRally = (tpt > 0 and sagaPtSet[tpt]) and true or false
      if not isSagaRally and w.monsterId and lc and TableName and TableName.Monster then
        local row = _safe_call(function() return lc:getLine(TableName.Monster, tostring(w.monsterId)) end, nil)
        if row then
          local sp = tonumber(_safe_call(function() return row:getValue('special') end, 0)) or 0
          if sp == challengeSpecial or sp == alBossSpecial then isSagaRally = true end
        end
      end
      if isSagaRally then
        out.open_rallies = out.open_rallies + 1
        local alreadyIn = wm.HasRallyFormationForInfo and _safe_call(function() return wm:HasRallyFormationForInfo(w) end, false)
        local skipR = _is_point_blacklisted(blacklistedPts, tpt, nil, w.uuid)
          or (tpt > 0 and _is_my_march_target(tpt, occ.my_march_targets))
        if not alreadyIn and not skipR and tostring(w.attackUid or '') ~= tostring(snap.uid or '') then
          table.insert(sagaRallies, {{ war = w, targetPoint = tpt }})
        end
      end
    end
  end
end

out.detected = (sagaActive or #sagaBosses > 0 or out.open_rallies > 0) and true or false
if not out.detected then
  out.status = 'physical_limit'
  out.stop_reason = 'not_detected'
  out.message = 'Survival Saga event is not active and no Saga bosses detected on map'
  return _enc(out)
end

local maxByStamina = math.floor((snap.stamina - minStam) / staminaCost)
if snap.stamina < math.max(staminaCost, minStam) or maxByStamina <= 0 then
  out.status = 'physical_limit'
  out.stop_reason = 'out_of_stamina'
  out.message = string.format('Out of stamina (%d left, need >=%d with reserve %d)', snap.stamina, math.max(staminaCost, minStam + staminaCost), minStam)
  return _enc(out)
end

local usable = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, false, not dryRun)
out.usable_formations = #usable
if #usable == 0 then
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad for Survival Saga (%d/%d active)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No usable squads available for Survival Saga (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
  return _enc(out)
end

local formIdx = 1
local remStamBudget = maxByStamina
local ranOutOfTroops = false

-- 1. Join open alliance Saga rallies first (headless SendCreateMarchMessage with JOIN_RALLY)
if snap.inAlliance and #sagaRallies > 0 then
  for _, sr in ipairs(sagaRallies) do
    if formIdx > #usable or remStamBudget <= 0 then break end
    local w = sr.war
    local f = nil
    f, formIdx = _next_ready_formation(usable, formIdx, dryRun)
    if not f then
      ranOutOfTroops = true
      break
    end
    local okJ, errJ, jPt, jMethod = _join_rally_headless(f, w, sr.targetPoint, snap.serverId, dryRun)
    if okJ then
      local jRec = {{
        mode = 'join_saga_rally',
        warUuid = tostring(w.uuid),
        pointId = jPt,
        targetPoint = jPt,
        formationUuid = tostring(f.uuid),
        formationIndex = tonumber(f.index or 0),
        joinMethod = jMethod,
      }}
      table.insert(out.joined_rallies, jRec)
      table.insert(out.dispatched, jRec)
      remStamBudget = remStamBudget - 1
    else
      table.insert(out.send_errors, 'JoinSagaRally: ' .. tostring(errJ))
    end
  end
end

-- 2. Attack or rally Saga bosses on map (own > ally/AlBoss > other, then closest)
if #sagaBosses > 0 and not ranOutOfTroops and formIdx <= #usable and remStamBudget > 0 then
  table.sort(sagaBosses, function(a, b)
    if a.prio ~= b.prio then return a.prio < b.prio end
    return a.dist < b.dist
  end)
  local atkType = (MarchTargetType and MarchTargetType.ATTACK_MONSTER) or 1
  local rallyType = (MarchTargetType and MarchTargetType.RALLY_FOR_BOSS) or 7
  local srvId = tonumber(snap.serverId) or 0
  for _, boss in ipairs(sagaBosses) do
    if formIdx > #usable or remStamBudget <= 0 then break end
    if not boss.claimed then
      local f = nil
      f, formIdx = _next_ready_formation(usable, formIdx, dryRun)
      if not f then
        if #out.dispatched == 0 then ranOutOfTroops = true end
        break
      end
      local useRally = ((boss.isAlBoss or canRally) and snap.inAlliance) and true or false
      local mType = useRally and rallyType or atkType
      local rallyFlag = useRally and 1 or 0
      local okS, errS = true, nil
      if not dryRun then
        if MarchUtil and MarchUtil.SendCreateMarchMessage and boss.pointId > 0 and f and f.uuid then
          okS, errS = pcall(function()
            MarchUtil.SendCreateMarchMessage(
              tonumber(f.uuid) or f.uuid,
              mType,
              boss.pointId,
              boss.uuid or 0,
              rallyFlag,
              true,
              true,
              srvId
            )
          end)
        else
          okS, errS = false, 'MarchUtil.SendCreateMarchMessage unavailable'
        end
      end
      if okS then
        table.insert(out.dispatched, {{
          mode = useRally and 'rally_saga_boss' or 'attack_saga_boss',
          pointId = boss.pointId,
          targetPoint = boss.pointId,
          warUuid = '',
          claimKey = boss.claimKey,
          monsterId = boss.monsterId,
          level = boss.level,
          special = boss.special,
          isOwn = boss.isOwn,
          isAlBoss = boss.isAlBoss,
          dist = boss.dist,
          formationUuid = tostring(f.uuid),
          formationIndex = tonumber(f.index or 0),
        }})
        remStamBudget = remStamBudget - 1
      else
        table.insert(out.send_errors, 'SagaMarch: ' .. tostring(errS))
      end
    end
  end
end

out.dispatched_count = #out.dispatched
if out.dispatched_count > 0 then
  out.status = 'dispatched'
  out.stop_reason = ''
  if not dryRun then
    out.active_marches = occ.active_marches + out.dispatched_count
    out.free_formations = math.max(0, occ.free_formations - out.dispatched_count)
  end
  out.message = string.format('Dispatched %d squad(s) against Survival Saga (joined=%d)', out.dispatched_count, #out.joined_rallies)
  return _enc(out)
end

if ranOutOfTroops then
  out.usable_formations = 0
  if occ.active_marches > 0 then
    out.status = 'waiting_for_squad'
    out.stop_reason = ''
    out.message = string.format('Waiting for returning squad for Survival Saga (%d/%d active)', occ.active_marches, occ.total_formations)
  else
    out.status = 'physical_limit'
    out.stop_reason = 'no_troops_or_formations'
    out.message = string.format('No stocked squads available for Survival Saga (free=%d, total=%d, reserve=%d)', occ.free_formations, occ.total_formations, reserve)
  end
  return _enc(out)
end

-- 3. Strict summon guard: ONLY call CallChallengeActBoss when allowSummon AND not dryRun AND boss_count == 0 AND open_rallies == 0 AND usable_formations > 0
if sagaActive and diffSelected and allowSummon and actId > 0
   and out.boss_count == 0 and out.open_rallies == 0 and out.usable_formations > 0 then
  if not dryRun then
    if SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.CallChallengeActBoss then
      local okSum, errSum = pcall(function()
        SFSNetwork.SendMessage(MsgDefines.CallChallengeActBoss, tonumber(actId) or actId)
      end)
      if okSum then
        out.summoned = true
        out.status = 'searching'
        out.stop_reason = ''
        out.message = string.format('Summoned Survival Saga boss (actId=%d)', actId)
        return _enc(out)
      else
        table.insert(out.send_errors, 'CallChallengeActBoss: ' .. tostring(errSum))
      end
    end
  else
    out.summoned = false
    out.would_summon = true
    out.status = 'searching'
    out.stop_reason = ''
    out.message = string.format('[DRY-RUN] Would summon Survival Saga boss (actId=%d)', actId)
    return _enc(out)
  end
end

-- 4. Fallback map search via FindMonster (nparams=6: mainPos, 1, false, 0, ChallengeBoss=4)
if sagaActive and out.boss_count == 0 and out.open_rallies == 0 and snap.mainPos > 0 and SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.FindMonster then
  if not dryRun then
    local okF, errF = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.FindMonster, tonumber(snap.mainPos), 1, false, 0, challengeSpecial)
    end)
    if okF then
      out.searched = true
      out.status = 'searching'
      out.stop_reason = ''
      out.message = 'Searching map for Survival Saga boss'
      return _enc(out)
    else
      table.insert(out.send_errors, 'FindMonster(Saga): ' .. tostring(errF))
    end
  else
    out.searched = true
    out.status = 'searching'
    out.stop_reason = ''
    out.message = '[DRY-RUN] Would search map for Survival Saga boss'
    return _enc(out)
  end
end

if #out.send_errors > 0 then
  out.ok = false
  out.status = 'error'
  out.stop_reason = 'send_failed'
  out.message = out.send_errors[1]
elseif (out.boss_count > 0 or out.open_rallies > 0) and occ.active_marches > 0 then
  out.status = 'waiting_for_squad'
  out.stop_reason = ''
  out.message = string.format('Existing Survival Saga boss/rally already in progress (%d/%d active marches)', occ.active_marches, occ.total_formations)
else
  out.status = 'physical_limit'
  out.stop_reason = 'no_targets_found'
  out.message = (sagaActive and not diffSelected) and 'Saga active but difficulty not selected and no bosses on map' or 'No Survival Saga bosses available'
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if not dry_run and context is not None and isinstance(res.get("dispatched"), list):
        used_uuids: list[str] = []
        claimed = context.setdefault("claimed_saga_points", [])
        for item in res["dispatched"]:
            if isinstance(item, dict):
                ck = item.get("claimKey")
                if ck and ck not in claimed:
                    claimed.append(ck)
                if item.get("formationUuid"):
                    used_uuids.append(str(item["formationUuid"]))
        if used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return _ensure_step_contract(res, task_name="saga_boss", default_message="Survival Saga step completed")


def detect_map_kill_targets(cd: Any, pid: int) -> dict[str, Any]:
    """Fast single read-only Lua probe detecting Boomers, Standalone NPCs, Saga, The Tyrant, and Furylord."""
    lua = r"""
local snap = _get_player_snapshot()
local occ = _get_squad_occupancy(snap)
local dc = DataCenter
local mm = dc and dc.MonsterManager
local wpm = dc and dc.WorldPointManager
local wm = dc and dc.AllianceWarDataManager
local mtd = dc and dc.ActMonsterTowerData
local abm = dc and dc.AllianceBossManager
local rbm = dc and dc.ActRoamingBossManager
local lc = LocalController and LocalController.instance and LocalController.instance()

local normalSpecial = (MonsterSpecialType and MonsterSpecialType.Normal) or 0
local challengeSpecial = (MonsterSpecialType and MonsterSpecialType.ChallengeBoss) or 4
local roamNormSpecial = (MonsterSpecialType and MonsterSpecialType.RoamingBossNormal) or 27
local roamSpecSpecial = (MonsterSpecialType and MonsterSpecialType.RoamingBossSpecial) or 28
local alBossSpecial = (MonsterSpecialType and MonsterSpecialType.MonsterTowerAlBoss) or 40

local maxNpcLv = 0
local maxBoomerLv = 0
local restBoomerKills = 0
if mm then
  if mm.GetCanFindMonsterMaxLevel then
    maxNpcLv = tonumber(_safe_call(function() return mm:GetCanFindMonsterMaxLevel() end, 0)) or 0
  end
  if maxNpcLv <= 0 and mm.find_monster_max_level then
    maxNpcLv = tonumber(mm.find_monster_max_level) or 0
  end
  if mm.GetCanFindBossMaxLevel then
    maxBoomerLv = tonumber(_safe_call(function() return mm:GetCanFindBossMaxLevel(0) end, 0)) or 0
  end
  if maxBoomerLv <= 0 and mm.GetCurCanAttackBossMaxLevel then
    maxBoomerLv = tonumber(_safe_call(function() return mm:GetCurCanAttackBossMaxLevel() end, 0)) or 0
  end
  if mm.GetRestKillBossNum then
    restBoomerKills = tonumber(_safe_call(function() return mm:GetRestKillBossNum() end, 0)) or 0
  elseif mm.kill_boss_max_num then
    restBoomerKills = math.max(0, (tonumber(mm.kill_boss_max_num) or 0) - (tonumber(mm.daily_kill_boss) or 0))
  end
end

-- Single-pass scan of viewport monsters
local boomerVpCount = 0
local npcVpCount = 0
local npcVpMaxLv = 0
local sagaVpCount = 0
local flVpCount = 0
local seenPt = {}

if wpm and wpm.allViewPoints and wpm.GetPointInfo and lc and TableName and TableName.Monster then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1) or -1
    local pnum = tonumber(ptIdx) or tonumber(ptObj and (ptObj.pointIndex or ptObj.pointId)) or 0
    if ptType == ((PointType and PointType.WorldMonster) or 4) and pnum > 0 then
      local info = _safe_call(function() return wpm:GetPointInfo(pnum) end, nil) or ptObj
      local targetPt = tonumber(info and info.mainIndex or 0) or 0
      if targetPt <= 0 then targetPt = pnum end
      if not seenPt[targetPt] then
        seenPt[targetPt] = true
        local pb = info and info._parsedExtra or nil
        if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
          local okP, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
          if okP and parsed then pb = parsed end
        end
        if pb and pb.monsterId then
          local row = _safe_call(function() return lc:getLine(TableName.Monster, tostring(pb.monsterId)) end, nil)
          if row then
            local isBoss = tonumber(_safe_call(function() return row:getValue('boss') end, 0)) or 0
            local special = tonumber(_safe_call(function() return row:getValue('special') end, 0)) or 0
            local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
            if isBoss == 0 and special == normalSpecial then
              npcVpCount = npcVpCount + 1
              if lv > npcVpMaxLv then npcVpMaxLv = lv end
            elseif isBoss == 1 and special == normalSpecial then
              boomerVpCount = boomerVpCount + 1
            elseif special == challengeSpecial or special == alBossSpecial then
              sagaVpCount = sagaVpCount + 1
            elseif special == roamNormSpecial or special == roamSpecSpecial then
              flVpCount = flVpCount + 1
            end
          end
        end
      end
    end
  end
end

-- Single-pass scan of open alliance rallies
local boomerOpenRallies = 0
local tyrantOpenRallies = 0
local flOpenRallies = 0
if snap.inAlliance and wm and wm.GetAllAllianceWar then
  local bossTeam = (AllianceTeamType and AllianceTeamType.ATTACK_BOSS) or 0
  local tyrantTeam = (AllianceTeamType and AllianceTeamType.ATTACK_ALLIANCE_BOSS) or 10
  local flTeam = (AllianceTeamType and AllianceTeamType.ATTACK_ROAMING_BOSS) or 14
  local wars = _safe_call(function() return wm:GetAllAllianceWar() end, {}) or {}
  for _, w in pairs(wars) do
    if type(w) == 'table' and w.uuid then
      local wType = tonumber(w.type or -1) or -1
      if wType == bossTeam then
        boomerOpenRallies = boomerOpenRallies + 1
      elseif wType == tyrantTeam then
        tyrantOpenRallies = tyrantOpenRallies + 1
      elseif wType == flTeam then
        flOpenRallies = flOpenRallies + 1
      end
    end
  end
end

-- Saga (ActMonsterTowerData)
local sagaActId = 0
local sagaActive = false
local sagaDiffSelected = false
if mtd then
  local ac = mtd.GetActiveChallengeInfo and _safe_call(function() return mtd:GetActiveChallengeInfo() end, nil) or nil
  if type(ac) == 'table' then
    sagaActId = tonumber(ac.actId or ac.activityId or ac.id or 0) or 0
  end
  if sagaActId <= 0 and mtd.GetInfoActAll then
    local allActs = _safe_call(function() return mtd:GetInfoActAll() end, nil)
    if type(allActs) == 'table' then
      for k, v in pairs(allActs) do
        local cid = (type(v) == 'table' and (tonumber(v.actId or v.activityId or v.id or k or 0) or 0)) or (tonumber(k or 0) or 0)
        if cid > 0 then
          local ended = mtd.CheckIfIsToEnd and (_safe_call(function() return mtd:CheckIfIsToEnd(cid) end, false) and true or false) or false
          if not ended then
            sagaActId = cid
            break
          end
        end
      end
    end
  end
  local ended = (sagaActId > 0 and mtd.CheckIfIsToEnd) and (_safe_call(function() return mtd:CheckIfIsToEnd(sagaActId) end, false) and true or false) or false
  local haveAl = mtd.CheckHaveAlBossAct and (_safe_call(function() return mtd:CheckHaveAlBossAct() end, false) and true or false) or false
  local alInfo = (sagaActId > 0 and mtd.GetAllianceActInfo) and _safe_call(function() return mtd:GetAllianceActInfo(sagaActId) end, nil) or nil
  sagaDiffSelected = (sagaActId > 0 and mtd.HasSelectedDifficulty) and (_safe_call(function() return mtd:HasSelectedDifficulty(sagaActId) end, false) and true or false) or false
  sagaActive = ((type(ac) == 'table' and not ended) or (sagaActId > 0 and not ended) or haveAl or (type(alInfo) == 'table')) and true or false
end

-- The Tyrant (AllianceBossManager)
local tyrantOpen = false
local tyrantInBattle = false
local tyrantBossPt = 0
if abm then
  tyrantOpen = (abm.IsAllianceBossActivityOpen and _safe_call(function() return abm:IsAllianceBossActivityOpen() end, false)) and true or false
  tyrantInBattle = (abm.GetIsInBattle and _safe_call(function() return abm:GetIsInBattle() end, false)) and true or false
  local bInfo = abm.GetBossInfo and _safe_call(function() return abm:GetBossInfo() end, {}) or {}
  if type(bInfo) == 'table' then
    tyrantBossPt = tonumber(bInfo.pointId or bInfo.pointIndex or bInfo.pos or 0) or 0
  end
end

-- Furylord (ActRoamingBossManager)
local flOpen = false
local flInAct = false
local flBossCount = 0
local flRewCount = 0
local flMaxRewCount = 0
if rbm then
  flOpen = (rbm.IsActOpen and _safe_call(function() return rbm:IsActOpen() end, false)) and true or false
  flInAct = (rbm.IsInAct and _safe_call(function() return rbm:IsInAct() end, false)) and true or false
  if rbm.GetBossInfoListNew then
    local bl = _safe_call(function() return rbm:GetBossInfoListNew() end, nil)
    if type(bl) == 'table' then
      for _, b in pairs(bl) do
        if type(b) == 'table' then flBossCount = flBossCount + 1 end
      end
    end
  end
  local rewNorm = (RoamingBossRewardType and RoamingBossRewardType.Normal) or 2
  if rbm.GetBossRewardCount then
    flRewCount = tonumber(_safe_call(function() return rbm:GetBossRewardCount(rewNorm) end, 0)) or 0
  end
  if rbm.GetMaxBossRewardCount then
    flMaxRewCount = tonumber(_safe_call(function() return rbm:GetMaxBossRewardCount(rewNorm) end, 0)) or 0
  end
end
if flVpCount > flBossCount then flBossCount = flVpCount end

return _enc({
  ok = true,
  stamina = snap.stamina,
  free_formations = occ.free_formations,
  active_marches = occ.active_marches,
  total_formations = occ.total_formations,
  in_alliance = snap.inAlliance and true or false,
  in_world = snap.inWorld and true or false,
  max_npc_level = maxNpcLv,
  max_boomer_level = maxBoomerLv,
  rest_boomer_kills = restBoomerKills,
  boomers = _jdict({
    detected = snap.inAlliance and true or false,
    open_rallies = boomerOpenRallies,
    viewport_count = boomerVpCount,
  }),
  standalone_npc = _jdict({
    detected = true,
    viewport_count = npcVpCount,
    max_level = (maxNpcLv > 0) and maxNpcLv or npcVpMaxLv,
  }),
  saga = _jdict({
    detected = (sagaActive or sagaVpCount > 0) and true or false,
    active = sagaActive and true or false,
    act_id = sagaActId,
    boss_count = sagaVpCount,
    difficulty_selected = sagaDiffSelected and true or false,
  }),
  tyrant = _jdict({
    detected = (tyrantOpen and tyrantInBattle) and true or false,
    is_open = tyrantOpen and true or false,
    in_battle = tyrantInBattle and true or false,
    boss_point_id = tyrantBossPt,
    open_rallies = tyrantOpenRallies,
  }),
  furylord = _jdict({
    detected = (flOpen or flInAct or flBossCount > 0 or flOpenRallies > 0) and true or false,
    is_open = flOpen and true or false,
    in_act = flInAct and true or false,
    boss_count = flBossCount,
    open_rallies = flOpenRallies,
    reward_count = flRewCount,
    max_reward_count = flMaxRewCount,
  }),
})
"""
    res = _eval_json(cd, pid, lua, timeout=6.0)
    if not res.get("ok"):
        res.setdefault("stamina", 0)
        res.setdefault("free_formations", 0)
        res.setdefault("active_marches", 0)
        res.setdefault("total_formations", 0)
        res.setdefault("in_alliance", False)
        res.setdefault("max_npc_level", 0)
        res.setdefault("max_boomer_level", 0)
        res.setdefault("rest_boomer_kills", 0)
        res.setdefault("boomers", {"detected": False, "open_rallies": 0, "viewport_count": 0})
        res.setdefault("standalone_npc", {"detected": False, "viewport_count": 0, "max_level": 0})
        res.setdefault("saga", {"detected": False, "active": False, "act_id": 0, "boss_count": 0, "difficulty_selected": False})
        res.setdefault("tyrant", {"detected": False, "is_open": False, "in_battle": False, "boss_point_id": 0})
        res.setdefault("furylord", {"detected": False, "is_open": False, "in_act": False, "boss_count": 0, "reward_count": 0, "max_reward_count": 0})
    return res


def run_bounties(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Unified 3-in-1 Gold Bounties: Lock Orange + Claim/Dispatch Gold + Help Allies Gold + Plunder Bounties."""
    b_cfg = cfg.get("bounties") or {}
    only_golden = bool(b_cfg.get("only_golden", True))
    min_color = int(b_cfg.get("min_color", 4))
    lock_orange = bool(b_cfg.get("lock_orange", True))
    help_allies_golden = bool(b_cfg.get("help_allies_golden", True))
    plunder_bounties = bool(b_cfg.get("plunder_bounties", True))
    use_free = bool(b_cfg.get("use_free", True))
    use_tickets = bool(b_cfg.get("use_tickets", True))
    use_diamonds = bool(b_cfg.get("use_diamonds", False))
    claim_completed = bool(b_cfg.get("claim_completed", True))
    max_refreshes = max(0, int(b_cfg.get("max_refreshes_per_cycle", 8)))

    if not dry_run:
        sync_lua = (
            "local dm = DataCenter and DataCenter.ActDispatchTaskDataManager; "
            "if dm then "
            f"if {str(lock_orange).lower()} and dm.SetLocalLockOrange then pcall(function() dm:SetLocalLockOrange(true) end) end; "
            "if dm.GetAllSingleTasksFromServer then pcall(function() dm:GetAllSingleTasksFromServer() end) end; "
            f"if {str(help_allies_golden).lower()} and dm.GetAllAllianceTasksFromServer then pcall(function() dm:GetAllAllianceTasksFromServer() end) end "
            "end; return _enc({ok=true})"
        )
        _eval_json(cd, pid, sync_lua, timeout=6.0)
        time.sleep(0.55)

    seen_dispatched: set[str] = set()
    used_heroes_py: list[str] = []

    def _run_step(step_claim: bool, step_help: bool) -> dict[str, Any]:
        seen_lua = "{" + ",".join(f"[{json.dumps(u)}]=true" for u in sorted(seen_dispatched)) + "}"
        extra_used_lua = "{" + ",".join(json.dumps(h) for h in used_heroes_py) + "}"
        lua = f"""
local dryRun = {str(dry_run).lower()}
local onlyGolden = {str(only_golden).lower()}
local minColorCfg = {min_color}
local lockOrange = {str(lock_orange).lower()}
local helpAllies = {str(step_help).lower()}
local useFree = {str(use_free).lower()}
local useTickets = {str(use_tickets).lower()}
local useDiamonds = {str(use_diamonds).lower()}
local claimDone = {str(step_claim).lower()}
local maxRefreshes = {max_refreshes}
local alreadyDispatched = {seen_lua}
local extraUsedHeroes = {extra_used_lua}

local snap = _get_player_snapshot()
local dismissed = {{}}
pcall(function() dismissed = _dismiss_modal_dialogs() or {{}} end)
local out = {{
  ok = true,
  task = 'bounties',
  dry_run = dryRun,
  is_open = false,
  lock_orange = lockOrange,
  claimed_all = false,
  refreshed = {{}},
  dispatched = {{}},
  allies_assisted = {{}},
  ally_helped = {{}},
  assist_left = 0,
  idle_count = 0,
  skipped_non_golden = 0,
  skipped_no_heroes = 0,
  stopped_reason = '',
  item_colors = {{}},
  newly_used_heroes = {{}},
  popped_modals = dismissed,
  errors = {{}},
  detail_lines = {{}},
}}

local dm = DataCenter and DataCenter.ActDispatchTaskDataManager
if not dm then
  out.stopped_reason = 'dispatch_manager_unavailable'
  table.insert(out.detail_lines, 'ActDispatchTaskDataManager unavailable')
  return _enc(out)
end

-- Always enforce Lock Orange preference BEFORE refreshing or dispatching
if lockOrange and dm.SetLocalLockOrange then
  pcall(function() dm:SetLocalLockOrange(true) end)
end

if ItemColor and type(ItemColor) == 'table' then
  for k, v in pairs(ItemColor) do
    if type(v) == 'number' then out.item_colors[tostring(k)] = v end
  end
end

local minGolden = minColorCfg
if ItemColor and type(ItemColor) == 'table' then
  minGolden = tonumber(ItemColor.ORANGE or minColorCfg) or minColorCfg
end
if not onlyGolden then minGolden = 0 end

local am = DataCenter and DataCenter.ActivityListDataManager
if am and am.CheckIfActivityOpen and EnumActivity and EnumActivity.DispatchTask then
  out.is_open = am:CheckIfActivityOpen(EnumActivity.DispatchTask.Type) or false
else
  out.is_open = true
end

local tasks = dm.GetAllSingleTasks and _safe_call(function() return dm:GetAllSingleTasks() end, {{}}) or {{}}
local taskCount = 0
for _ in pairs(tasks) do taskCount = taskCount + 1 end
if taskCount == 0 and dm.GetAllSingleTasksFromServer then
  if not dryRun then pcall(function() dm:GetAllSingleTasksFromServer() end) end
  tasks = dm.GetAllSingleTasks and _safe_call(function() return dm:GetAllSingleTasks() end, {{}}) or {{}}
end

local function _is_unrewarded(v)
  return v == nil or v == false or tonumber(v) == 0
end

local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)

-- 1) Claim completed bounties first
if claimDone then
  local claimCount = 0
  for _, t in pairs(tasks) do
    if type(t) == 'table' then
      local ct = tonumber(t.completionTime or 0) or 0
      if ct > 0 and ct < 1e12 then ct = ct * 1000 end
      if ct > 0 and nowMs > 0 and nowMs >= ct and _is_unrewarded(t.rewarded) then
        claimCount = claimCount + 1
      end
    end
  end
  if claimCount > 0 and MsgDefines and MsgDefines.DispatchRewardAll and SFSNetwork then
    if not dryRun then
      local okC, errC = pcall(function() SFSNetwork.SendMessage(MsgDefines.DispatchRewardAll) end)
      if not okC then table.insert(out.errors, 'DispatchRewardAll: ' .. tostring(errC)) end
    end
    out.claimed_all = true
    table.insert(out.detail_lines, string.format('Claimed %d completed bounty rewards (DispatchRewardAll)', claimCount))
  end
end

local lc = LocalController and LocalController.instance and LocalController.instance() or nil
local function _task_color(t)
  if type(t) ~= 'table' then return 0 end
  if t.cfg and t.cfg.color then return tonumber(t.cfg.color) or 0 end
  if t.color then return tonumber(t.color) or 0 end
  local cid = tostring(t.cfgId or t.missionId or '')
  if cid ~= '' and lc and lc.getLine and TableName and TableName.LwDispatchTask then
    local ok, row = pcall(function() return lc:getLine(TableName.LwDispatchTask, cid) end)
    if ok and row and row.getValue then
      local okc, cv = pcall(function() return row:getValue('color') end)
      if okc and cv ~= nil then return tonumber(cv) or 0 end
    end
  end
  local n = tonumber(cid) or 0
  if n >= 100000 then return math.max(0, math.floor(n / 100000) - 1) end
  return 0
end

local function _task_level(t)
  if type(t) ~= 'table' then return 0 end
  if t.level then return tonumber(t.level) or 0 end
  if t.cfg and t.cfg.level then return tonumber(t.cfg.level) or 0 end
  return 0
end

-- Build 1-indexed array of used hero UUIDs (matches Dispatch.GetRecommendHeroList table.indexof requirement)
local usedHeroArr = {{}}
local usedHeroSet = {{}}
local function _mark_hero_used(hu)
  if not hu then return end
  local hs = tostring(hu)
  if hs == '' or hs == '0' then return end
  if not usedHeroSet[hs] then
    usedHeroSet[hs] = true
    table.insert(usedHeroArr, hu)
  end
end
if dm.GetAllUsedHeroList then
  local existingUsed = _safe_call(function() return dm:GetAllUsedHeroList() end, {{}}) or {{}}
  for _, hu in pairs(existingUsed) do _mark_hero_used(hu) end
end
for _, hu in ipairs(extraUsedHeroes) do
  _mark_hero_used(tonumber(hu) or hu)
end

-- Compute available formation slots robustly (idle count minus in-flight dispatched across refreshes)
local idleCount = dm.GetIdleCount and tonumber(_safe_call(function() return dm:GetIdleCount() end, 0)) or 4
local extraBusy = 0
for _ in pairs(alreadyDispatched) do extraBusy = extraBusy + 1 end
-- Subtract only if server hasn't already decremented them into active tasks
local serverActiveCount = 0
for _, t in pairs(tasks) do
  if type(t) == 'table' and (tonumber(t.completionTime or 0) or 0) > 0 and not alreadyDispatched[tostring(t.uuid or '')] then
    serverActiveCount = serverActiveCount + 1
  end
end
out.idle_count = idleCount

-- Sort single tasks by color desc, level desc so highest-tier golden tasks get hero priority
local candidateTasks = {{}}
for _, t in pairs(tasks) do
  if type(t) == 'table' and t.isstealtask ~= true and (tonumber(t.completionTime or 0) or 0) == 0 and _is_unrewarded(t.rewarded) then
    if not alreadyDispatched[tostring(t.uuid or '')] then
      table.insert(candidateTasks, t)
    end
  end
end
table.sort(candidateTasks, function(a, b)
  local ca, cb = _task_color(a), _task_color(b)
  if ca ~= cb then return ca > cb end
  local la, lb = _task_level(a), _task_level(b)
  if la ~= lb then return la > lb end
  return tostring(a.uuid or '') < tostring(b.uuid or '')
end)

local nonGoldenIdle = 0
local goldenWaitingSlot = 0
for _, t in ipairs(candidateTasks) do
  local tc = _task_color(t)
  local tlv = _task_level(t)
  local tuStr = tostring(t.uuid or '')
  if tc >= minGolden then
    if idleCount > 0 and MsgDefines and MsgDefines.DispatchStart and SFSNetwork then
      local heroes = nil
      if dm.GetRecommendHeroList then
        local okH, rec = pcall(function() return dm:GetRecommendHeroList(t, usedHeroArr) end)
        if okH and type(rec) == 'table' then heroes = rec end
      end
      if type(heroes) == 'table' and #heroes > 0 then
        local marchDurMs = tonumber(t.marchTime or t.marchDuration or (t.cfg and t.cfg.marchTime) or t.duration or 0) or 0
        if marchDurMs <= 0 then
          local ptId = tonumber(t.pointId or 0) or 0
          local myPt = LuaEntry and LuaEntry.Player and LuaEntry.Player.GetMainWorldPos and tonumber(LuaEntry.Player:GetMainWorldPos() or 0) or 0
          local worldObj = SceneManager and SceneManager.World
          local spd = LuaEntry and LuaEntry.DataConfig and LuaEntry.DataConfig.TryGetNum and tonumber(_safe_call(function() return LuaEntry.DataConfig:TryGetNum('armyspeed', 'k2') end, 0)) or 0
          if ptId > 0 and myPt > 0 and worldObj and SceneUtils and SceneUtils.IndexToTilePos and Vector2 and Vector2.Distance and spd > 0 then
            local okM, calcMs = pcall(function()
              local p1 = SceneUtils.IndexToTilePos(myPt, worldObj)
              local p2 = SceneUtils.IndexToTilePos(ptId, worldObj)
              return math.ceil(Vector2.Distance(p1, p2) * 1000 / spd)
            end)
            if okM and tonumber(calcMs) and tonumber(calcMs) > 0 then marchDurMs = tonumber(calcMs) end
          end
        end
        if marchDurMs <= 0 then marchDurMs = 1000 end
        local sendOk, sendErr = true, nil
        if not dryRun then
          sendOk, sendErr = pcall(function() SFSNetwork.SendMessage(MsgDefines.DispatchStart, tonumber(t.uuid) or t.uuid, heroes, marchDurMs) end)
        end
        if sendOk then
          idleCount = idleCount - 1
          for _, hu in pairs(heroes) do
            _mark_hero_used(hu)
            table.insert(out.newly_used_heroes, tostring(hu))
          end
          table.insert(out.dispatched, {{
            uuid = tuStr, cfgId = tonumber(t.cfgId or 0) or 0, color = tc, level = tlv,
            heroCount = #heroes, marchDuration = marchDurMs,
          }})
          table.insert(out.detail_lines, string.format('Dispatched Gold Bounty: uuid=%s color=%d lv=%d heroes=%d', tuStr, tc, tlv, #heroes))
        else
          table.insert(out.errors, 'DispatchStart(' .. tuStr .. '): ' .. tostring(sendErr))
        end
      else
        out.skipped_no_heroes = out.skipped_no_heroes + 1
        table.insert(out.detail_lines, string.format('Skipped Gold Bounty uuid=%s color=%d lv=%d: no eligible unused heroes', tuStr, tc, tlv))
      end
    else
      goldenWaitingSlot = goldenWaitingSlot + 1
    end
  else
    nonGoldenIdle = nonGoldenIdle + 1
  end
end
out.skipped_non_golden = nonGoldenIdle
out.idle_count = idleCount

-- Refresh ONLY when non-golden tasks remain & idle slots exist (always passing lockOrange = true!)
if nonGoldenIdle > 0 and idleCount > 0 and maxRefreshes > 0 and MsgDefines and MsgDefines.DispatchTaskRefresh and SFSNetwork then
  local itemId, itemCost, diamondCost = 0, 1, 0
  if dm.GetTaskRefreshSetting then
    local ok, dCnt, iId, iCnt = pcall(function() return dm:GetTaskRefreshSetting() end)
    if ok then
      diamondCost = tonumber(dCnt or 0) or 0
      itemId = tonumber(iId or 0) or 0
      itemCost = tonumber(iCnt or 1) or 1
    end
  end
  local idata = DataCenter and DataCenter.ItemData
  local ticketCnt = (itemId > 0 and idata and idata.GetItemCount) and (tonumber(_safe_call(function() return idata:GetItemCount(itemId) end, 0)) or 0) or 0
  local freeLeft = dm.GetFreeRefreshNum and (tonumber(_safe_call(function() return dm:GetFreeRefreshNum() end, 0)) or 0) or (dm.freeRefreshNum and tonumber(dm.freeRefreshNum) or 0)

  if (useFree and freeLeft > 0) or (useTickets and ticketCnt >= itemCost) then
    if not dryRun then
      local okRf, errRf = pcall(function() SFSNetwork.SendMessage(MsgDefines.DispatchTaskRefresh, 0, lockOrange) end)
      if not okRf then table.insert(out.errors, 'DispatchTaskRefresh: ' .. tostring(errRf)) end
    end
    out.did_refresh = true
    local mode = (freeLeft > 0) and 'free' or 'ticket'
    table.insert(out.refreshed, {{costType = 0, mode = mode, lockOrange = lockOrange, itemId = itemId, tickets = ticketCnt, freeLeft = freeLeft}})
    table.insert(out.detail_lines, string.format('Refreshed bounties (mode=%s, lockOrange=%s, freeLeft=%d, tickets=%d)', mode, tostring(lockOrange), freeLeft, ticketCnt))
  elseif useDiamonds and (diamondCost <= 0 or (tonumber(snap.gold or 0) or 0) >= diamondCost) then
    if not dryRun then
      local okRf, errRf = pcall(function() SFSNetwork.SendMessage(MsgDefines.DispatchTaskRefresh, 1, lockOrange) end)
      if not okRf then table.insert(out.errors, 'DispatchTaskRefresh(gold): ' .. tostring(errRf)) end
    end
    out.did_refresh = true
    table.insert(out.refreshed, {{costType = 1, mode = 'diamonds', lockOrange = lockOrange, cost = diamondCost}})
    table.insert(out.detail_lines, string.format('Refreshed bounties (mode=diamonds cost=%d, lockOrange=%s)', diamondCost, tostring(lockOrange)))
  else
    out.stopped_reason = 'no_free_or_ticket_refresh'
  end
elseif idleCount <= 0 then
  out.stopped_reason = 'all_slots_busy'
elseif nonGoldenIdle == 0 then
  out.stopped_reason = 'no_non_golden_idle_remaining'
end

-- 2) Help Allies with Golden Tasks (DispatchAssist)
if helpAllies and snap.inAlliance and dm.GetAllAllianceTasks and MsgDefines and MsgDefines.DispatchAssist and SFSNetwork then
  local assistLeft = dm.GetAssistLeftCount and tonumber(_safe_call(function() return dm:GetAssistLeftCount() end, 0)) or 0
  out.assist_left = assistLeft
  if assistLeft > 0 then
    local myUid = tostring((LuaEntry and LuaEntry.Player and LuaEntry.Player.GetUid and LuaEntry.Player:GetUid()) or snap.uid or '')
    local allyTasks = _safe_call(function() return dm:GetAllAllianceTasks() end, {{}}) or {{}}
    local allyGoldCands = {{}}
    for _, at in pairs(allyTasks) do
      if type(at) == 'table' and at.uuid and tostring(at.uid or '') ~= myUid and _is_unrewarded(at.rewarded) then
        local ac = _task_color(at)
        local alreadyAssist = (tostring(at.assistUid or '') == myUid) or (tonumber(at.doubleReward or 0) > 0) or (at.isAssist == true)
        local ct = tonumber(at.completionTime or 0) or 0
        if ct > 0 and ct < 1e12 then ct = ct * 1000 end
        local readyToAssist = (ct > 0 and nowMs > 0 and ct <= nowMs)
        if ac >= minGolden and not alreadyAssist and readyToAssist then
          table.insert(allyGoldCands, at)
        end
      end
    end
    table.sort(allyGoldCands, function(a, b)
      local la, lb = _task_level(a), _task_level(b)
      if la ~= lb then return la > lb end
      return tostring(a.uuid or '') < tostring(b.uuid or '')
    end)
    for _, at in ipairs(allyGoldCands) do
      if assistLeft <= 0 then break end
      local au = tostring(at.uuid)
      if not dryRun then
        local okA, errA = pcall(function() SFSNetwork.SendMessage(MsgDefines.DispatchAssist, tonumber(at.uuid) or at.uuid) end)
        if not okA then table.insert(out.errors, 'DispatchAssist(' .. au .. '): ' .. tostring(errA)) end
      end
      assistLeft = assistLeft - 1
      local aRec = {{
        uuid = au, ally = tostring(at.name or at.ownerName or at.uid or ''),
        ownerName = tostring(at.name or at.ownerName or ''), ownerUid = tostring(at.uid or ''),
        color = _task_color(at), level = _task_level(at),
      }}
      table.insert(out.allies_assisted, aRec)
      table.insert(out.ally_helped, aRec)
      table.insert(out.detail_lines, string.format('Helped Ally Gold Bounty: ally=%s uuid=%s color=%d lv=%d', tostring(aRec.ally), au, aRec.color, aRec.level))
    end
    out.assist_left = assistLeft
  end
end

return _enc(out)
"""
        return _eval_json(cd, pid, lua, timeout=10.0)

    first = _run_step(claim_completed, help_allies_golden)
    if not first.get("ok"):
        return first

    agg = dict(first)
    dispatched_all = list(first.get("dispatched") or [])
    refreshed_all = list(first.get("refreshed") or [])
    errors_all = list(first.get("errors") or [])
    lines_all = list(first.get("detail_lines") or [])
    modals_all = list(first.get("popped_modals") or [])
    for d in dispatched_all:
        if isinstance(d, dict) and d.get("uuid"):
            seen_dispatched.add(str(d["uuid"]))
    for hu in first.pop("newly_used_heroes", []) or []:
        if str(hu) not in used_heroes_py:
            used_heroes_py.append(str(hu))

    did_refresh = bool(agg.pop("did_refresh", False))
    attempts = 0
    if not dry_run and max_refreshes > 0:
        while did_refresh and attempts < max_refreshes:
            attempts += 1
            time.sleep(0.8)
            nxt = _run_step(False, False)
            if not nxt.get("ok"):
                break
            for d in nxt.get("dispatched") or []:
                if isinstance(d, dict) and d.get("uuid"):
                    seen_dispatched.add(str(d["uuid"]))
            for hu in nxt.pop("newly_used_heroes", []) or []:
                if str(hu) not in used_heroes_py:
                    used_heroes_py.append(str(hu))
            dispatched_all.extend(nxt.get("dispatched") or [])
            refreshed_all.extend(nxt.get("refreshed") or [])
            errors_all.extend(nxt.get("errors") or [])
            lines_all.extend(nxt.get("detail_lines") or [])
            modals_all.extend(nxt.get("popped_modals") or [])
            agg["idle_count"] = nxt.get("idle_count", agg.get("idle_count"))
            agg["skipped_non_golden"] = nxt.get("skipped_non_golden", agg.get("skipped_non_golden"))
            agg["skipped_no_heroes"] = nxt.get("skipped_no_heroes", agg.get("skipped_no_heroes"))
            if nxt.get("stopped_reason"):
                agg["stopped_reason"] = nxt["stopped_reason"]
            did_refresh = bool(nxt.get("did_refresh", False))

    agg["dispatched"] = dispatched_all
    agg["refreshed"] = refreshed_all
    agg["claimed"] = bool(agg.get("claimed_all"))

    # 3) Integrated Bounty Plunder / Steal (unified 3-in-1 when plunder_bounties=True)
    if plunder_bounties:
        plunder_sub = b_cfg.get("plunder") if isinstance(b_cfg.get("plunder"), dict) else {}
        bs_existing = cfg.get("bounty_steal") if isinstance(cfg.get("bounty_steal"), dict) else {}
        merged_bs = dict(bs_existing)
        merged_bs.update(plunder_sub)
        plunder_cfg = dict(cfg)
        plunder_cfg["bounty_steal"] = merged_bs
        plunder_res = run_bounty_steal(cd, pid, client_state, plunder_cfg, dry_run=dry_run, context=context)
        agg["stolen"] = list(plunder_res.get("stolen") or [])
        agg["steal_candidates"] = list(plunder_res.get("candidates") or [])
        agg["today_steals"] = plunder_res.get("today_steals", 0)
        agg["max_steals"] = plunder_res.get("max_steals", 0)
        agg["plunder_reason"] = plunder_res.get("reason", "")
        errors_all.extend(plunder_res.get("errors") or [])
        lines_all.extend(plunder_res.get("detail_lines") or [])
        modals_all.extend(plunder_res.get("popped_modals") or [])
    else:
        agg["stolen"] = []
        agg["steal_candidates"] = []

    agg["errors"] = errors_all
    agg["popped_modals"] = modals_all
    agg["lock_orange"] = lock_orange
    agg["help_allies_golden"] = help_allies_golden
    agg["plunder_bounties"] = plunder_bounties
    agg["ally_helped"] = list(agg.get("ally_helped") or agg.get("allies_assisted") or [])
    if not lines_all:
        lines_all.append(
            f"Bounties idle: lockOrange={lock_orange}, idle={agg.get('idle_count', 0)}, "
            f"non_golden={agg.get('skipped_non_golden', 0)}, assist_left={agg.get('assist_left', 0)}, reason={agg.get('stopped_reason', 'none')}"
        )
    agg["detail_lines"] = lines_all
    acted = (
        (1 if agg.get("claimed_all") else 0)
        + len(dispatched_all)
        + len(agg.get("ally_helped") or [])
        + len(agg.get("stolen") or [])
        + len(refreshed_all)
    )
    agg["action"] = "completed" if acted > 0 else "none"
    agg["message"] = (
        f"Bounties (3-in-1 lock={lock_orange}): dispatched={len(dispatched_all)}, refreshed={len(refreshed_all)}, "
        f"ally_helped={len(agg.get('ally_helped') or [])}, plundered={len(agg.get('stolen') or [])}"
    )
    return agg


def run_bounty_steal(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Jump/scan another state and steal ONLY Golden Lv5+ bounties."""
    bs_cfg = cfg.get("bounty_steal") or {}
    cross_only = bool(bs_cfg.get("cross_state_only", True))
    only_golden = bool(bs_cfg.get("only_golden", True))
    min_color = int(bs_cfg.get("min_color", 4))
    min_level = int(bs_cfg.get("min_level", 5))
    max_steals = int(bs_cfg.get("max_daily_steals", 5))
    max_scan = max(1, int(bs_cfg.get("max_servers_scan", 4)))

    lua = f"""
local dryRun = {str(dry_run).lower()}
local crossOnly = {str(cross_only).lower()}
local onlyGolden = {str(only_golden).lower()}
local minColorCfg = {min_color}
local minLevel = {min_level}
local maxStealsCfg = {max_steals}
local maxScan = {max_scan}

local snap = _get_player_snapshot()
local out = {{
  ok = true,
  task = 'bounty_steal',
  dry_run = dryRun,
  self_server = snap.serverId,
  today_steals = 0,
  max_steals = 0,
  matched_servers = {{}},
  scanned_points = 0,
  candidates = {{}},
  stolen = {{}},
  skipped_same_state = 0,
  skipped_low_tier = 0,
  errors = {{}},
  detail_lines = {{}},
}}

local dm = DataCenter and DataCenter.ActDispatchTaskDataManager
if not dm then
  out.reason = 'dispatch_manager_unavailable'
  table.insert(out.detail_lines, 'Plunder skipped: ActDispatchTaskDataManager unavailable')
  return _enc(out)
end

local gameMax = 5
if dm.GetDispatchSetting then
  gameMax = tonumber(_safe_call(function() return dm:GetDispatchSetting('steal_count') end, 5) or 5) or 5
end
out.today_steals = dm.GetTodayStealNum and (tonumber(_safe_call(function() return dm:GetTodayStealNum() end, 0) or 0) or 0) or 0
out.max_steals = math.min(maxStealsCfg, gameMax)
if out.today_steals >= out.max_steals then
  out.reason = 'daily_steal_limit_reached'
  table.insert(out.detail_lines, string.format('Plunder limit reached: %d/%d steals used today', out.today_steals, out.max_steals))
  return _enc(out)
end

local minGolden = minColorCfg
if ItemColor and type(ItemColor) == 'table' then
  minGolden = tonumber(ItemColor.ORANGE or minColorCfg) or minColorCfg
end
if not onlyGolden then minGolden = 0 end

-- Collect foreign match servers and request world dispatch view if needed
local wpm = DataCenter and DataCenter.WorldPointManager
local foreignSids = {{}}
if type(dm.matchServers) == 'table' then
  for sid, active in pairs(dm.matchServers) do
    local nsid = tonumber(sid) or 0
    if active and nsid > 0 and (not crossOnly or nsid ~= snap.serverId) then
      table.insert(foreignSids, nsid)
    end
  end
end
table.sort(foreignSids)
out.matched_servers = foreignSids
out._min_golden = minGolden
out._min_level = minLevel
out._cross_only = crossOnly
out._max_scan = maxScan
out.ok = true
return _enc(out)
"""
    scan_helper = r"""
local dm = DataCenter and DataCenter.ActDispatchTaskDataManager
local wpm = DataCenter and DataCenter.WorldPointManager
local p = LuaEntry and LuaEntry.Player
local myUid = (p and p.GetUid) and tostring(p:GetUid() or '') or ''
local homeSid = (p and p.GetSelfServerId) and tonumber(p:GetSelfServerId() or 0) or (p and p.GetCurServerId and tonumber(p:GetCurServerId() or 0) or 0)
local scanned, sameStateCnt, lowTierCnt = 0, 0, 0
local cands = {}
if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  local dispType = WorldPointType and WorldPointType.HERO_DISPATCH or 22
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptype = tonumber(ptObj and ptObj.pointType or -1)
    if ptype == tonumber(dispType) then
      local pnum = tonumber(ptIdx) or tonumber(ptObj and ptObj.pointId) or 0
      local info = (pnum > 0 and wpm:GetPointInfo(pnum)) or (ptObj and ptObj.pointInfo) or ptObj
      local dmInfo = info and (info.dispatchMission or info._parsedExtra) or nil
      if (not dmInfo or not dmInfo.uuid) and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
        local ok_pb, pb = pcall(function() return PBController.ParsePbFromBytes('protobuf.DispatchMission', info.extraInfo) end)
        if ok_pb and pb and pb.uuid then dmInfo = pb end
      end
      if dmInfo and dmInfo.uuid then
        scanned = scanned + 1
        local sid = tonumber((info and (info.serverId or info.srcServerId)) or dmInfo.serverId or 0) or 0
        local sameState = (homeSid > 0 and sid == homeSid) or (sid == 0)
        local samePlayer = tostring(dmInfo.ownerUid or dmInfo.uid or '') == myUid
        if crossOnly and (sameState or samePlayer) then
          sameStateCnt = sameStateCnt + 1
        else
          local cfgId = tostring(dmInfo.cfgId or dmInfo.missionId or '')
          local row = (LocalController and LocalController.instance and TableName and TableName.LwDispatchTask)
            and LocalController.instance():getLine(TableName.LwDispatchTask, cfgId) or nil
          local color = tonumber((row and row:getValue('color')) or dmInfo.color or 0) or 0
          local level = tonumber((row and row:getValue('level')) or dmInfo.level or 0) or 0
          local stealMax = tonumber((row and row:getValue('steal_maxtimes')) or 99) or 99
          local stealCnt = type(dmInfo.stealUids) == 'table' and #dmInfo.stealUids or 0
          local alreadyStole = false
          if type(dmInfo.stealUids) == 'table' then
            for _, su in pairs(dmInfo.stealUids) do
              if tostring(su) == myUid then alreadyStole = true; break end
            end
          end
          if not alreadyStole and stealCnt < stealMax and color >= minGolden and level >= minLevel then
            table.insert(cands, {
              uuid = tostring(dmInfo.uuid),
              serverId = sid,
              pointId = pnum,
              color = color,
              level = level,
            })
          else
            lowTierCnt = lowTierCnt + 1
          end
        end
      end
    end
  end
end
"""
    base_res = _eval_json(cd, pid, lua, timeout=10.0)
    if not base_res.get("ok"):
        return base_res

    min_golden_val = int(base_res.pop("_min_golden", min_color))
    min_level_val = int(base_res.pop("_min_level", min_level))
    cross_only_val = bool(base_res.pop("_cross_only", cross_only))
    max_scan_val = int(base_res.pop("_max_scan", max_scan))
    rem = max(0, int(base_res.get("max_steals", 0)) - int(base_res.get("today_steals", 0)))
    foreign_sids = list(base_res.get("matched_servers") or [])
    all_candidates: list[dict[str, Any]] = []
    seen_uuids: set[str] = set()
    steal_errors: list[str] = list(base_res.get("errors") or [])
    steal_lines: list[str] = list(base_res.get("detail_lines") or [])

    def _scan_and_steal_current(do_steal: bool, limit_rem: int) -> dict[str, Any]:
        skip_lua = "{" + ",".join(f"[{json.dumps(u)}]=true" for u in sorted(seen_uuids)) + "}"
        scan_lua = (
            f"local minGolden = {min_golden_val}\n"
            f"local minLevel = {min_level_val}\n"
            f"local crossOnly = {str(cross_only_val).lower()}\n"
            f"local doSteal = {str(do_steal).lower()}\n"
            f"local rem = {limit_rem}\n"
            f"local skipUuids = {skip_lua}\n"
            + scan_helper
            + r"""
table.sort(cands, function(a, b)
  if a.level ~= b.level then return a.level > b.level end
  return a.color > b.color
end)
local stolen = {}
local errs = {}
for _, c in ipairs(cands) do
  if rem <= 0 then break end
  if not skipUuids[tostring(c.uuid)] and MsgDefines and MsgDefines.DispatchSteal and SFSNetwork then
    if doSteal then
      local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.DispatchSteal, tonumber(c.uuid) or c.uuid, c.serverId) end)
      if not okS then table.insert(errs, 'DispatchSteal(' .. tostring(c.uuid) .. '): ' .. tostring(errS)) end
    end
    table.insert(stolen, c)
    rem = rem - 1
  end
end
return _enc({ok=true, scanned=scanned, same_state=sameStateCnt, low_tier=lowTierCnt, candidates=cands, stolen=stolen, errs=errs})
"""
        )
        return _eval_json(cd, pid, scan_lua, timeout=10.0)

    def _merge_scan(sr: dict[str, Any]) -> None:
        base_res["scanned_points"] = int(base_res.get("scanned_points", 0)) + int(sr.get("scanned", 0))
        base_res["skipped_same_state"] = int(base_res.get("skipped_same_state", 0)) + int(sr.get("same_state", 0))
        base_res["skipped_low_tier"] = int(base_res.get("skipped_low_tier", 0)) + int(sr.get("low_tier", 0))
        for e in sr.get("errs") or []:
            steal_errors.append(str(e))
        for c in sr.get("candidates") or []:
            u = str(c.get("uuid") or "")
            if u and u not in seen_uuids:
                seen_uuids.add(u)
                all_candidates.append(c)
        for st_item in sr.get("stolen") or []:
            base_res.setdefault("stolen", []).append(st_item)
            steal_lines.append(
                f"Plundered bounty: uuid={st_item.get('uuid')} S{st_item.get('serverId')} color={st_item.get('color')} lv={st_item.get('level')}"
            )

    home_scan = _scan_and_steal_current(False, rem)
    if home_scan.get("ok"):
        _merge_scan(home_scan)

    if not dry_run and rem > 0 and foreign_sids and max_scan_val > 0:
        ensure_world_scene(cd, pid, wait_seconds=2.2)
        switched = False
        try:
            for fsid in foreign_sids[:max_scan_val]:
                if rem <= 0:
                    break
                switched = True
                _eval_json(
                    cd,
                    pid,
                    f"if CrossServerUtil and CrossServerUtil.OnCrossServer then CrossServerUtil.OnCrossServer({int(fsid)}, 0) end; return _enc({{ok=true}})",
                    timeout=8.0,
                )
                for _ in range(10):
                    conn_st = _eval_json(
                        cd,
                        pid,
                        "return _enc({ok=true, conn=(LuaEntry and LuaEntry.CrossNetwork and LuaEntry.CrossNetwork.IsConnected) and LuaEntry.CrossNetwork:IsConnected() or false})",
                        timeout=6.0,
                    )
                    if conn_st.get("conn"):
                        break
                    time.sleep(0.25)
                time.sleep(0.45)
                for vx, vy in ((600, 600), (450, 450), (750, 750)):
                    if rem <= 0:
                        break
                    _eval_json(
                        cd,
                        pid,
                        f"""
                        local w = SceneManager and SceneManager.World
                        if w and w.Camera then
                          local z = w.Camera.GetInitZoom and w.Camera:GetInitZoom() or 100.0
                          pcall(function() w.Camera:SetZoom(z) end)
                          if w.Lookat and w.TileXYToWorld then
                            pcall(function() w:Lookat(w:TileXYToWorld({vx}, {vy})) end)
                          end
                        end
                        local wpm = DataCenter and DataCenter.WorldPointManager
                        if wpm and wpm.DoSendViewRequest then
                          pcall(function() wpm:DoSendViewRequest({vx}, {vy}, 1, {int(fsid)}) end)
                        end
                        return _enc({{ok=true}})
                        """,
                        timeout=6.0,
                    )
                    time.sleep(0.95)
                    sr = _scan_and_steal_current(True, rem)
                    if sr.get("ok"):
                        newly_stolen = []
                        for st_item in sr.get("stolen") or []:
                            su = str(st_item.get("uuid") or "")
                            if su and su not in seen_uuids:
                                newly_stolen.append(st_item)
                        sr["stolen"] = newly_stolen
                        _merge_scan(sr)
                        rem = max(0, rem - len(newly_stolen))
        finally:
            if switched:
                _eval_json(
                    cd,
                    pid,
                    """
                    if CrossServerUtil and CrossServerUtil.OnBackSelfServer then pcall(function() CrossServerUtil.OnBackSelfServer() end) end
                    local w = SceneManager and SceneManager.World
                    local p = LuaEntry and LuaEntry.Player
                    if w and p and p.GetMainWorldPos and SceneUtils and SceneUtils.IndexToTileXY and w.Lookat and w.TileXYToWorld then
                      local pos = tonumber(p:GetMainWorldPos() or 0) or 0
                      if pos > 0 then
                        local hx, hy = SceneUtils.IndexToTileXY(pos)
                        pcall(function() w:Lookat(w:TileXYToWorld(hx, hy)) end)
                      end
                      if w.UpdateViewRequest then pcall(function() w:UpdateViewRequest() end) end
                    end
                    return _enc({ok=true})
                    """,
                    timeout=8.0,
                )
                time.sleep(0.6)

    base_res["candidates"] = all_candidates
    base_res["errors"] = steal_errors
    if not steal_lines:
        steal_lines.append(
            f"Plunder scan: scanned={base_res.get('scanned_points', 0)} points, stolen={len(base_res.get('stolen') or [])}, steals={base_res.get('today_steals', 0)}/{base_res.get('max_steals', 0)}"
        )
    base_res["detail_lines"] = steal_lines
    base_res["action"] = "completed" if len(base_res.get("stolen") or []) > 0 else "none"
    return base_res


def run_trucks(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Claim all finished/golden trucks first, wait for server sync, reroll & dispatch up to slots, and raid cross-state trucks."""
    tr_cfg = cfg.get("trucks") or {}
    daily_sends = int(tr_cfg.get("daily_sends", 4))
    raw_slots = tr_cfg.get("slots") or []
    slots: list[dict[str, int]] = []
    for idx in range(4):
        s = raw_slots[idx] if idx < len(raw_slots) and isinstance(raw_slots[idx], dict) else {}
        slots.append({
            "quality": max(1, min(5, int(s.get("quality", 5)))),
            "formation": max(0, min(4, int(s.get("formation", idx + 1)))),
        })
    reroll_items = bool(tr_cfg.get("reroll_with_items", True))
    reroll_diamonds = bool(tr_cfg.get("reroll_with_diamonds", False))
    max_rerolls = max(0, int(tr_cfg.get("max_rerolls_per_truck", 6)))
    claim_completed = bool(tr_cfg.get("claim_completed", True))
    atk_enabled = bool(tr_cfg.get("attack_enabled", True))
    atk_limit = int(tr_cfg.get("attack_daily_limit", 4))
    atk_cross_only = bool(tr_cfg.get("attack_cross_state_only", True))
    atk_margin = int(tr_cfg.get("attack_power_margin_below_f1", 20_000_000))

    slots_lua = "{" + ",".join(f"{{q={s['quality']},f={s['formation']}}}" for s in slots) + "}"

    # Phase 1: Claim ALL arrived / rewardable trucks + first-reward FIRST, before refreshing/dispatching
    claimed_uuids: list[str] = []
    claimed_details: list[dict[str, Any]] = []
    claim_errors: list[str] = []
    claim_detail_lines: list[str] = []
    popped_modals: list[str] = []

    if claim_completed:
        claim_lua = f"""
local dryRun = {str(dry_run).lower()}
local dismissed = {{}}
pcall(function() dismissed = _dismiss_modal_dialogs() or {{}} end)
local out = {{
  ok = true,
  claimed = 0,
  claimed_list = {{}},
  errors = {{}},
  detail_lines = {{}},
  popped_modals = dismissed,
}}
local st = DataCenter and DataCenter.LWMyStationDataManager
if not st then
  out.reason = 'station_manager_unavailable'
  return _enc(out)
end

if st.hasFirstReward and st.TryCollectFirstReward then
  if not dryRun then
    local okF, errF = pcall(function() st:TryCollectFirstReward() end)
    if not okF then table.insert(out.errors, 'TryCollectFirstReward: ' .. tostring(errF)) end
  end
  out.claimed = out.claimed + 1
  table.insert(out.detail_lines, 'Claimed station first-time reward')
end

local rewardEnum = (TruckStationState and TruckStationState.Reward) or 4
local arrivedEnum = (TrainState and TrainState.ArrivedFinal) or 3
local beforeDepEnum = (TrainState and TrainState.BeforeDeparture) or 1
local travellingEnum = (TrainState and TrainState.Travelling) or 2
local seenClaim = {{}}

local function _check_and_claim(tr, srcLabel)
  if type(tr) ~= 'table' or not tr.uuid then return end
  local uStr = tostring(tr.uuid)
  if seenClaim[uStr] then return end
  local stState = st.GetTruckStationStateByTrainData and _safe_call(function() return st:GetTruckStationStateByTrainData(tr) end, -1) or -1
  local trState = tr.GetTrainState and _safe_call(function() return tr:GetTrainState() end, -1) or -1
  local depTs = tonumber(tr.departureTs or 0) or 0
  local hasArrivedReward = (tr.hasReward == true) and (tonumber(trState) ~= beforeDepEnum) and (tonumber(trState) ~= travellingEnum) and (depTs > 0 or srcLabel == 'old/history')
  local canClaim = hasArrivedReward or (tonumber(tr.rewardState or 0) == 1)
    or (tonumber(stState) == rewardEnum) or (tonumber(trState) == arrivedEnum)
  if canClaim then
    seenClaim[uStr] = true
    local q = tonumber(tr.quality or tr.color or tr.level or 1) or 1
    if not dryRun then
      local okC, errC = false, nil
      if st.TryCollectReward then
        okC, errC = pcall(function() st:TryCollectReward(tr.uuid) end)
      elseif SFSNetwork and MsgDefines and MsgDefines.CollectTrainReward then
        okC, errC = pcall(function() SFSNetwork.SendMessage(MsgDefines.CollectTrainReward, tonumber(tr.uuid) or tr.uuid) end)
      end
      if not okC then table.insert(out.errors, 'CollectTrainReward(' .. uStr .. '): ' .. tostring(errC)) end
    end
    out.claimed = out.claimed + 1
    table.insert(out.claimed_list, {{uuid = uStr, quality = q, source = srcLabel, slotIndex = tonumber(tr.index or 0) or 0}})
    table.insert(out.detail_lines, string.format('Claimed %s truck reward: uuid=%s quality=%d (slot=%s)', srcLabel, uStr, q, tostring(tr.index or '?')))
  end
end

local myTrainsAll = st.GetMyTrains and _safe_call(function() return st:GetMyTrains() end, {{}}) or (st.myTrains or {{}})
for _, tr in pairs(myTrainsAll) do _check_and_claim(tr, 'active/arrived') end
local oldTrainsAll = (st.GetMyOldTrains and _safe_call(function() return st:GetMyOldTrains() end, {{}})) or (type(st.myOldTrains) == 'table' and st.myOldTrains) or {{}}
for _, tr in pairs(oldTrainsAll) do _check_and_claim(tr, 'old/history') end

return _enc(out)
"""
        c_res = _eval_json(cd, pid, claim_lua, timeout=8.0)
        claimed_details = list(c_res.get("claimed_list") or [])
        claimed_uuids = [str(x.get("uuid")) for x in claimed_details if isinstance(x, dict) and x.get("uuid")]
        claim_errors.extend(list(c_res.get("errors") or []))
        claim_detail_lines.extend(list(c_res.get("detail_lines") or []))
        popped_modals.extend(list(c_res.get("popped_modals") or []))
        claimed_pre = int(c_res.get("claimed", 0) or 0)
    else:
        claimed_pre = 0

    # Always refresh station data when claiming finished trucks OR when spare train cache is empty on a fresh client
    if not dry_run:
        sync_parts = [
            "local st = DataCenter and DataCenter.LWMyStationDataManager; "
            "local needSt = " + ("true" if claimed_pre > 0 else "false") + "; "
            "if st and not needSt then local sp = st.GetMySpareTrains and _safe_call(function() return st:GetMySpareTrains() end, {}) or {}; "
            "local n = 0; for _ in pairs(sp) do n = n + 1 end; if n == 0 then needSt = true end end; "
            "if st and needSt then if st.TryGetMyStationData then pcall(function() st:TryGetMyStationData() end) "
            "elseif SFSNetwork and MsgDefines and MsgDefines.GetMyStationData then pcall(function() SFSNetwork.SendMessage(MsgDefines.GetMyStationData) end) end end"
        ]
        if atk_enabled:
            sync_parts.append(
                "local td = DataCenter and DataCenter.LWTrainDataManager; "
                "if td then if td.SetFilterLocalServer then pcall(function() td:SetFilterLocalServer(false) end) end; "
                "if td.TryGetTrainList then pcall(function() td:TryGetTrainList(false) end) end end"
            )
        sync_parts.append("return _enc({ok=true, synced_station=needSt})")
        sync_res = _eval_json(cd, pid, "; ".join(sync_parts), timeout=6.0)
        if claimed_pre > 0 or sync_res.get("synced_station") or atk_enabled:
            time.sleep(1.0 if (claimed_pre > 0 or sync_res.get("synced_station")) else 0.75)

    # Phase 2A: Iterative reroll step-by-step (only waiting briefly between actual server rerolls so updated quality arrives)
    rerolled_log: list[dict[str, Any]] = []
    if not dry_run and max_rerolls > 0 and (reroll_items or reroll_diamonds):
        for _round in range(max_rerolls):
            rr_lua = f"""
local dailySends = {daily_sends}
local slots = {slots_lua}
local rerollItems = {str(reroll_items).lower()}
local rerollDiamonds = {str(reroll_diamonds).lower()}

local snap = _get_player_snapshot()
local st = DataCenter and DataCenter.LWMyStationDataManager
if not st or not st.TryChangeTrain then return _enc({{ok = true, did_reroll = false}}) end
local depCount = st.GetDepartureCount and (tonumber(st:GetDepartureCount() or 0) or 0) or 0
if depCount >= dailySends then return _enc({{ok = true, did_reroll = false}}) end

local spare = st.GetMySpareTrains and _safe_call(function() return st:GetMySpareTrains() end, {{}}) or {{}}
local idata = DataCenter and DataCenter.ItemData
local contractItemId = tonumber(st.CHANGE_TRAIN_ITEM_ID or 200184) or 200184
local contractOwned = (idata and idata.GetItemCount) and (tonumber(_safe_call(function() return idata:GetItemCount(contractItemId) end, 0)) or 0) or 0
local goldCost = tonumber(st.GOLD_TO_REFRESH_TRUCK or 200) or 200

local did = false
local logs = {{}}
local idxCursor = depCount
local readyEnum = (TruckStationState and TruckStationState.Ready) or 1
local beforeDepEnum = (TrainState and TrainState.BeforeDeparture) or 1
for _, tr in pairs(spare) do
  if idxCursor >= dailySends then break end
  local stState = (type(tr) == 'table' and st.GetTruckStationStateByTrainData) and _safe_call(function() return st:GetTruckStationStateByTrainData(tr) end, readyEnum) or readyEnum
  local trState = (type(tr) == 'table' and tr.GetTrainState) and _safe_call(function() return tr:GetTrainState() end, beforeDepEnum) or beforeDepEnum
  if type(tr) == 'table' and tr.uuid and (tonumber(stState) == readyEnum or tonumber(trState) == beforeDepEnum) then
    idxCursor = idxCursor + 1
    local slot = slots[math.min(idxCursor, #slots)] or {{q = 5, f = idxCursor}}
    local q = tonumber(tr.quality or tr.color or tr.level or 1) or 1
    if q < slot.q then
      if rerollItems and contractOwned > 0 then
        local okR, errR = pcall(function() st:TryChangeTrain(tr.uuid, nil) end)
        if okR then
          contractOwned = contractOwned - 1
          did = true
          table.insert(logs, {{uuid = tostring(tr.uuid), mode = 'contract', from_quality = q, target_quality = slot.q}})
        end
      elseif rerollDiamonds and (tonumber(snap.gold or 0) or 0) >= goldCost then
        local okR, errR = pcall(function() st:TryChangeTrain(tr.uuid, goldCost) end)
        if okR then
          did = true
          table.insert(logs, {{uuid = tostring(tr.uuid), mode = 'diamonds', from_quality = q, target_quality = slot.q}})
        end
      end
    end
  end
end
return _enc({{ok = true, did_reroll = did, logs = logs}})
"""
            rr_res = _eval_json(cd, pid, rr_lua, timeout=6.0)
            r_logs = list(rr_res.get("logs") or [])
            if not rr_res.get("did_reroll") or not r_logs:
                break
            rerolled_log.extend(r_logs)
            time.sleep(0.45)

    # Phase 2B: Dispatch ready spare trucks (especially quality >= target, or best spare when rerolls exhausted) + Cross-state attacks
    lua = f"""
local dryRun = {str(dry_run).lower()}
local dailySends = {daily_sends}
local slots = {slots_lua}
local rerollItems = {str(reroll_items).lower()}
local rerollDiamonds = {str(reroll_diamonds).lower()}
local atkEnabled = {str(atk_enabled).lower()}
local atkLimit = {atk_limit}
local atkCrossOnly = {str(atk_cross_only).lower()}
local atkMargin = {atk_margin}

local snap = _get_player_snapshot()
local dismissed = {{}}
pcall(function() dismissed = _dismiss_modal_dialogs() or {{}} end)
local out = {{
  ok = true,
  task = 'trucks',
  dry_run = dryRun,
  self_server = snap.serverId,
  f1_power = 0,
  claimed = {claimed_pre},
  rerolled = {{}},
  sent = {{}},
  attacked = {{}},
  skipped_same_state = 0,
  skipped_too_strong = 0,
  departure_count = 0,
  max_daily_sends = dailySends,
  remaining_slots = 0,
  rob_count = 0,
  popped_modals = dismissed,
  errors = {{}},
  detail_lines = {{}},
}}

local st = DataCenter and DataCenter.LWMyStationDataManager
local td = DataCenter and DataCenter.LWTrainDataManager
local af = DataCenter and DataCenter.ArmyFormationDataManager
if not st then
  out.ok = false
  out.reason = 'station_manager_unavailable'
  table.insert(out.detail_lines, 'LWMyStationDataManager unavailable')
  return _enc(out)
end

local f1 = af and af.GetOneArmyInfoByIndex and _safe_call(function() return af:GetOneArmyInfoByIndex(1) end, nil) or nil
local hm = DataCenter and DataCenter.HeroDataManager
local am = DataCenter and DataCenter.ArmyManager
local function _calc_form_power(formObj)
  if type(formObj) ~= 'table' then return 0 end
  local pw = 0
  if formObj.GetPower then
    local ok, v = pcall(function() return formObj:GetPower() end)
    if ok then pw = math.floor(tonumber(v or 0) or 0) end
  end
  if pw <= 0 and formObj.GetFormationPower then
    local ok, v = pcall(function() return formObj:GetFormationPower() end)
    if ok then pw = math.floor(tonumber(v or 0) or 0) end
  end
  if pw <= 0 and MarchUtil and MarchUtil.GetFormationPower then
    local hArg = (formObj.GetCurHeroes and _safe_call(function() return formObj:GetCurHeroes() end, nil)) or formObj.heroes or formObj.heroUuids
    if type(hArg) == 'table' and next(hArg) ~= nil then
      local solTbl = {{}}
      local maxSol = am and am.GetSelfMaxPowerSoldier and _safe_call(function() return am:GetSelfMaxPowerSoldier() end, nil) or nil
      local aid = maxSol and tonumber(maxSol.armyId or maxSol.id or 0) or 0
      local cs = (af and af.GetCurSoldierNum and formObj.uuid) and (tonumber(_safe_call(function() return af:GetCurSoldierNum(formObj.uuid) end, 0)) or 0) or 0
      if cs <= 0 then cs = tonumber(formObj.totalSoldierNum or formObj.maxNum or 0) or 0 end
      if aid > 0 and cs > 0 then solTbl[aid] = cs end
      local ok, mp = pcall(function() return MarchUtil.GetFormationPower(hArg, solTbl, formObj.index or 1) end)
      if ok and tonumber(mp) then pw = math.floor(tonumber(mp) or 0) end
    end
  end
  if pw <= 0 and hm and type(formObj.heroes) == 'table' then
    local sumH = 0
    for hk, hv in pairs(formObj.heroes) do
      local ho = (hm.GetHeroByUuid and (hm:GetHeroByUuid(hk) or hm:GetHeroByUuid(hv))) or nil
      if type(ho) == 'table' then
        sumH = sumH + (tonumber((ho.GetPower and ho:GetPower()) or ho.power or ho.totalPower or 0) or 0)
      end
    end
    pw = math.floor(sumH)
  end
  if pw <= 0 then
    pw = math.floor(tonumber(formObj.power or formObj.totalPower or 0) or 0)
  end
  return pw
end

if f1 then out.f1_power = _calc_form_power(f1) end
if out.f1_power <= 0 and st.GetDefenceFormationByIndex then
  local df1 = _safe_call(function() return st:GetDefenceFormationByIndex(1) end, nil)
  if df1 then out.f1_power = _calc_form_power(df1) end
end

local curDep, cfgMax = 0, dailySends
if st.GetDepartureCount then
  local okD, d1, d2 = pcall(function() return st:GetDepartureCount() end)
  if okD then
    curDep = tonumber(d1 or 0) or 0
    if tonumber(d2 or 0) and tonumber(d2) > 0 then cfgMax = math.min(dailySends, tonumber(d2)) end
  end
end
out.departure_count = curDep
out.max_daily_sends = cfgMax
out.rob_count = st.GetRobCount and (tonumber(_safe_call(function() return st:GetRobCount() end, 0)) or 0) or 0

-- Dispatch spare trucks up to remaining daily slots
local spare = st.GetMySpareTrains and _safe_call(function() return st:GetMySpareTrains() end, {{}}) or {{}}
local readyEnumCheck = (TruckStationState and TruckStationState.Ready) or 1
local beforeDepCheck = (TrainState and TrainState.BeforeDeparture) or 1
local spareList = {{}}
for _, tr in pairs(spare) do
  if type(tr) == 'table' and tr.uuid then
    local stS = st.GetTruckStationStateByTrainData and _safe_call(function() return st:GetTruckStationStateByTrainData(tr) end, readyEnumCheck) or readyEnumCheck
    local trS = tr.GetTrainState and _safe_call(function() return tr:GetTrainState() end, beforeDepCheck) or beforeDepCheck
    if tonumber(stS) == readyEnumCheck or tonumber(trS) == beforeDepCheck then
      table.insert(spareList, tr)
    end
  end
end
table.sort(spareList, function(a, b)
  local qa = tonumber(a.quality or a.color or a.level or 1) or 1
  local qb = tonumber(b.quality or b.color or b.level or 1) or 1
  if qa ~= qb then return qa > qb end
  return (tonumber(a.index or 99) or 99) < (tonumber(b.index or 99) or 99)
end)

local usedSlotIdx = out.departure_count
local usedFormIdx = {{}}
local busyForms = st.GetBusyDefenceFormationIndexList and _safe_call(function() return st:GetBusyDefenceFormationIndexList() end, {{}}) or {{}}
if type(busyForms) == 'table' then
  for _, bi in pairs(busyForms) do usedFormIdx[tonumber(bi or 0) or 0] = true end
end

local function _form_has_heroes(form)
  if type(form) ~= 'table' then return false end
  if type(form.heroes) == 'table' and next(form.heroes) ~= nil then return true end
  if type(form.heroUuids) == 'table' and next(form.heroUuids) ~= nil then return true end
  if form.GetCurHeroes then
    local ch = _safe_call(function() return form:GetCurHeroes() end, nil)
    if type(ch) == 'table' and next(ch) ~= nil then return true end
  end
  return false
end

local function _pick_truck_form(prefIdx)
  local candIdxs = {{}}
  if prefIdx > 0 then table.insert(candIdxs, prefIdx) end
  for idx = 1, 4 do if idx ~= prefIdx then table.insert(candIdxs, idx) end end
  for _, idx in ipairs(candIdxs) do
    if not usedFormIdx[idx] then
      local form = nil
      if st.GetDefenceFormationByIndex then
        form = _safe_call(function() return st:GetDefenceFormationByIndex(idx) end, nil)
      end
      if (not _form_has_heroes(form)) and af and af.GetOneArmyInfoByIndex then
        form = _safe_call(function() return af:GetOneArmyInfoByIndex(idx) end, nil)
      end
      if _form_has_heroes(form) then
        return form, tonumber(form.index or idx) or idx
      end
    end
  end
  if st.GetMaxBattlePowerFreeDefenceFormation then
    local ff = _safe_call(function() return st:GetMaxBattlePowerFreeDefenceFormation() end, nil)
    if _form_has_heroes(ff) then
      return ff, tonumber(ff.index or 1) or 1
    end
  end
  return nil, 0
end

-- Check actual remaining reroll affordability so we never strand remaining_slots when contracts=0 and diamonds=off
local idata = DataCenter and DataCenter.ItemData
local contractItemId = tonumber(st.CHANGE_TRAIN_ITEM_ID or 200184) or 200184
local contractOwned = (idata and idata.GetItemCount) and (tonumber(_safe_call(function() return idata:GetItemCount(contractItemId) end, 0)) or 0) or 0
local goldCost = tonumber(st.GOLD_TO_REFRESH_TRUCK or 200) or 200
local canAffordReroll = (rerollItems and contractOwned > 0) or (rerollDiamonds and (tonumber(snap.gold or 0) or 0) >= goldCost)
out.contracts_remaining = contractOwned
out.can_afford_reroll = canAffordReroll

local readyEnum = (TruckStationState and TruckStationState.Ready) or 1
for _, tr in ipairs(spareList) do
  if usedSlotIdx >= cfgMax then break end
  local q = tonumber(tr.quality or tr.color or tr.level or 1) or 1
  local stState = st.GetTruckStationStateByTrainData and _safe_call(function() return st:GetTruckStationStateByTrainData(tr) end, readyEnum) or readyEnum
  local slotNum = usedSlotIdx + 1
  local slot = slots[math.min(slotNum, #slots)] or {{q = 5, f = slotNum}}
  if dryRun and q < slot.q and canAffordReroll then
    table.insert(out.rerolled, {{uuid = tostring(tr.uuid), mode = (rerollItems and contractOwned > 0) and 'contract' or 'diamonds', from_quality = q, target_quality = slot.q}})
  end
  -- Dispatch when quality meets target, when Q4+, OR when we can no longer afford to reroll (prevents stranded remaining_slots=1)
  local canSendAnyRemaining = (q >= slot.q) or (not canAffordReroll) or (q >= 4)
  if (stState == readyEnum or stState == -1) and canSendAnyRemaining then
    local form, fIndexUsed = _pick_truck_form(slot.f)
    if form and st.TryDepartureTrain then
      usedSlotIdx = usedSlotIdx + 1
      usedFormIdx[fIndexUsed] = true
      if not dryRun then
        local okDep, errDep = pcall(function() st:TryDepartureTrain(tr.uuid, form) end)
        if not okDep then table.insert(out.errors, 'TryDepartureTrain(' .. tostring(tr.uuid) .. '): ' .. tostring(errDep)) end
      end
      table.insert(out.sent, {{
        slot = usedSlotIdx,
        uuid = tostring(tr.uuid),
        quality = q,
        target_quality = slot.q,
        formation = fIndexUsed,
      }})
      table.insert(out.detail_lines, string.format('Dispatched truck slot=%d: uuid=%s quality=%d/%d formation=%d (contracts=%d)', usedSlotIdx, tostring(tr.uuid), q, slot.q, fIndexUsed, contractOwned))
    else
      table.insert(out.detail_lines, string.format('Skipped truck uuid=%s quality=%d: no free defence formation', tostring(tr.uuid), q))
    end
  else
    table.insert(out.detail_lines, string.format('Held truck uuid=%s quality=%d (< target %d, stationState=%s, contracts=%d)', tostring(tr.uuid), q, slot.q, tostring(stState), contractOwned))
  end
end

out.remaining_slots = math.max(0, cfgMax - usedSlotIdx)

-- Cross-state Truck Raids (exact 5-arg TryAttackTrain(trainUuid, trainServerId, formation, formationPower, armyId))
if atkEnabled and td and out.rob_count < atkLimit and out.f1_power > 0 then
  if td.SetFilterLocalServer then pcall(function() td:SetFilterLocalServer(false) end) end
  local enemies = td.GetEnemyTruckList and _safe_call(function() return td:GetEnemyTruckList() end, {{}}) or {{}}
  out.enemy_trucks_seen = 0
  for _ in pairs(enemies) do out.enemy_trucks_seen = out.enemy_trucks_seen + 1 end
  local remAtk = atkLimit - out.rob_count
  local maxTargetPower = out.f1_power - atkMargin
  local atkForm = (st.GetMaxBattlePowerFreeAttackFormation and _safe_call(function() return st:GetMaxBattlePowerFreeAttackFormation() end, nil))
    or (st.GetAttackFormationByIndex and _safe_call(function() return st:GetAttackFormationByIndex(1) end, nil))
    or f1
  local atkPower = (atkForm and _calc_form_power(atkForm)) or out.f1_power
  if atkPower <= 0 then atkPower = out.f1_power end
  local maxSol = am and am.GetSelfMaxPowerSoldier and _safe_call(function() return am:GetSelfMaxPowerSoldier() end, nil) or nil
  local atkArmyId = (maxSol and tostring(maxSol.armyId or maxSol.id or '')) or ''

  for _, tr in pairs(enemies) do
    if remAtk <= 0 then break end
    if type(tr) == 'table' and tr.uuid then
      local tSid = tonumber(tr.serverId or 0) or 0
      local tPow = tonumber(tr.power or tr.totalPower or tr.formationPower or 0) or 0
      if atkCrossOnly and (tSid <= 0 or (snap.serverId > 0 and tSid == snap.serverId)) then
        out.skipped_same_state = out.skipped_same_state + 1
      elseif maxTargetPower <= 0 or tPow <= 0 or tPow > maxTargetPower then
        out.skipped_too_strong = out.skipped_too_strong + 1
      elseif atkForm then
        if not dryRun and st.TryAttackTrain then
          local okA, errA = pcall(function()
            st:TryAttackTrain(tr.uuid, tSid, atkForm, atkPower, atkArmyId)
          end)
          if not okA then table.insert(out.errors, 'TryAttackTrain(' .. tostring(tr.uuid) .. '): ' .. tostring(errA)) end
        end
        table.insert(out.attacked, {{
          uuid = tostring(tr.uuid),
          serverId = tSid,
          targetPower = tPow,
          f1Power = atkPower,
          margin = atkPower - tPow,
        }})
        table.insert(out.detail_lines, string.format('Raided cross-state truck uuid=%s S%d (targetPow=%d vs atkPow=%d)', tostring(tr.uuid), tSid, tPow, atkPower))
        remAtk = remAtk - 1
      end
    end
  end
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=12.0)
    if claimed_uuids:
        res["claimed_uuids"] = claimed_uuids
    if claimed_details:
        res["claimed_details"] = claimed_details
    if rerolled_log:
        res["rerolled"] = rerolled_log + list(res.get("rerolled") or [])
    if claim_errors:
        res["errors"] = claim_errors + list(res.get("errors") or [])
    if popped_modals:
        res["popped_modals"] = popped_modals + list(res.get("popped_modals") or [])
    combined_lines = list(claim_detail_lines) + [
        f"Reroll step: uuid={r.get('uuid')} from Q{r.get('from_quality')}->target Q{r.get('target_quality')} ({r.get('mode')})"
        for r in rerolled_log
    ] + list(res.get("detail_lines") or [])
    if not combined_lines:
        combined_lines.append(
            f"Station idle: departure={res.get('departure_count', 0)}/{res.get('max_daily_sends', daily_sends)}, remaining_slots={res.get('remaining_slots', 0)}, rob={res.get('rob_count', 0)}/{atk_limit}"
        )
    res["detail_lines"] = combined_lines
    acted = int(res.get("claimed", 0) or 0) + len(res.get("sent") or []) + len(res.get("attacked") or []) + len(res.get("rerolled") or [])
    res["action"] = "completed" if acted > 0 else "none"
    res["message"] = (
        f"Trucks: claimed={res.get('claimed', 0)}, rerolled={len(res.get('rerolled') or [])}, "
        f"sent={len(res.get('sent') or [])}, raided={len(res.get('attacked') or [])}, remaining_slots={res.get('remaining_slots', 0)}"
    )
    return res


def run_mining_event(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Mon/Tue Mine Melee (MineCaveManager, ActMineCave=25) executed in 4 asynchronous Python-paced stages:

    - Stage A: Request & Sync MineCave Info (`mc:TryReqUpdateMineCaveInfo()`, wait 1.0s in Python for SFS2X response, then read `mc:GetMineCaveInfo()`).
    - Stage B: Claim Completed Mine Melee Rewards (`MsgDefines.ClaimMineCaveReward`, wait 0.8s in Python, then re-sync `GetMineCaveInfo()`).
    - Stage C: Staged Multi-Refresh Loop (`0..max_refreshes` in Python; if no matching unoccupied mine is found, trigger `MsgDefines.RefreshMineCaveList`, sleep 1.2s in Python for the server's new `minesList` packet, and re-scan).
    - Stage D: Dispatch Free Formation to Occupy Mine (`mc:SetAttackMineIndex`, `mc:SetDispatchFormation`, `MsgDefines.BeginPvpCaveFight`).
    """
    mn_cfg = cfg.get("mining_event") or {}
    weekdays = [int(x) for x in (mn_cfg.get("weekdays") or [0, 1])]
    mine_type = int(mn_cfg.get("mine_type", 2))  # 2 = Crystal/XP Mine, 1 = Gold Mine, 0 = Any
    mine_level = int(mn_cfg.get("mine_level", 7))
    min_level = max(1, int(mn_cfg.get("min_level", 1)))
    skip_players = bool(mn_cfg.get("skip_occupied_players", True))
    claim_fin = bool(mn_cfg.get("claim_finished", True))
    max_refreshes = max(0, int(mn_cfg.get("max_refreshes", 3)))

    now_dt = _now_dt(context)
    force_mining = bool((context or {}).get("force_mining")) or bool(
        context and "mining_event" in (context.get("task_filter") or [])
    )
    is_scheduled_day = (now_dt.weekday() in weekdays) or force_mining
    if not is_scheduled_day and not dry_run and not force_mining:
        return {
            "ok": True,
            "task": "mining_event",
            "status": "off_schedule_not_mon_tue",
            "reason": "off_schedule_not_mon_tue",
            "weekday": now_dt.weekday(),
            "stages_completed": [],
        }

    stages_completed: list[str] = []
    all_tips: list[str] = []

    # -------------------------------------------------------------------------
    # STAGE A: Request & Sync MineCave Info
    # -------------------------------------------------------------------------
    stage_a_req_lua = f"""
local dryRun = {str(dry_run).lower()}
local out = {{ ok = true, stage = 'stage_a_req', dry_run = dryRun, requested_update = false, event_open = false, has_cached_info = false }}
local mc = DataCenter and DataCenter.MineCaveManager
if not mc then
  out.ok = false
  out.reason = 'mine_cave_manager_unavailable'
  return _enc(out)
end
if ActivityEnum and ActivityEnum.ActivityType and ActivityEnum.ActivityType.ActMineCave == nil then
  ActivityEnum.ActivityType.ActMineCave = 25
end
local snap = _get_player_snapshot()
local function _check_event_open()
  if mc.CheckActMineIsShow then
    local ok, isShow = pcall(function() return mc:CheckActMineIsShow() end)
    if ok and isShow then return true end
  end
  local actMgr = DataCenter and DataCenter.ActivityListDataManager
  if actMgr and actMgr.GetActivityDataByType then
    local ok, acts = pcall(function() return actMgr:GetActivityDataByType(25) end)
    if ok and type(acts) == 'table' and #acts > 0 then
      local nowMs = (snap.serverSec or 0) * 1000
      for _, a in pairs(acts) do
        local st = tonumber(a.startTime or 0) or 0
        local et = tonumber(a.endTime or 0) or 0
        if (st == 0 and et == 0) or (nowMs >= st and nowMs < et) then
          return true
        end
      end
    end
  end
  local info = mc.GetMineCaveInfo and mc:GetMineCaveInfo()
  if info and type(info.minesList) == 'table' and #info.minesList > 0 then
    return true
  end
  return false
end
out.event_open = _check_event_open()
local curInfo = mc.GetMineCaveInfo and mc:GetMineCaveInfo() or nil
out.has_cached_info = (curInfo ~= nil and type(curInfo.minesList) == 'table')
if not dryRun and (out.event_open or {str(force_mining).lower()}) then
  if mc.TryReqUpdateMineCaveInfo then
    pcall(function() mc:TryReqUpdateMineCaveInfo() end)
    out.requested_update = true
  elseif SFSNetwork and MsgDefines and MsgDefines.GetMineCaveInfo then
    pcall(function() SFSNetwork.SendMessage(MsgDefines.GetMineCaveInfo) end)
    out.requested_update = true
  end
end
return _enc(out)
"""
    stage_a_req = _eval_json(cd, pid, stage_a_req_lua, timeout=8.0)
    all_tips.extend(stage_a_req.get("in_game_tips") or [])
    if not stage_a_req.get("ok") and stage_a_req.get("reason") == "mine_cave_manager_unavailable":
        return {
            "ok": True,
            "task": "mining_event",
            "dry_run": dry_run,
            "is_scheduled_day": is_scheduled_day,
            "event_open": False,
            "reason": "mine_cave_manager_unavailable",
            "stages_completed": stages_completed,
            "in_game_tips": _clean_in_game_tips(all_tips),
        }

    # Wait in Python for the async SFS2X GetMineCaveInfo response packet to populate MineCaveManager
    if not dry_run and stage_a_req.get("requested_update"):
        time.sleep(1.0)

    def _inspect_mine_cave_state() -> dict[str, Any]:
        inspect_lua = f"""
local targetType = {mine_type}
local targetLevel = {mine_level}
local minLevel = {min_level}
local skipPlayers = {str(skip_players).lower()}
local snap = _get_player_snapshot()
local mc = DataCenter and DataCenter.MineCaveManager
local out = {{
  ok = true,
  event_open = false,
  max_mines = 1,
  active_count = 0,
  active_mines = {{}},
  claimable_mines = {{}},
  fight_num = 0,
  refresh_num = 0,
  last_refresh_time = 0,
  can_refresh = false,
  refresh_cost = 0,
  exact_candidates = {{}},
  fallback_candidates = {{}},
  mines_list_count = 0,
  skipped_wrong_type_or_level = 0,
  skipped_occupied_players = 0,
  server_sec = snap.serverSec or os.time(),
}}
if not mc then
  out.ok = false
  out.reason = 'mine_cave_manager_unavailable'
  return _enc(out)
end
if ActivityEnum and ActivityEnum.ActivityType and ActivityEnum.ActivityType.ActMineCave == nil then
  ActivityEnum.ActivityType.ActMineCave = 25
end
local info = mc.GetMineCaveInfo and mc:GetMineCaveInfo() or {{}}
if mc.CheckActMineIsShow then
  local okS, isShow = pcall(function() return mc:CheckActMineIsShow() end)
  if okS and isShow then out.event_open = true end
end
if not out.event_open and type(info.minesList) == 'table' and #info.minesList > 0 then
  out.event_open = true
end
out.max_mines = (DataConfig and DataConfig.TryGetNum and tonumber(DataConfig.TryGetNum('mine_cave', 'k3') or 1)) or 1
if out.max_mines < 1 then out.max_mines = 1 end
out.fight_num = tonumber((mc.GetFightNum and _safe_call(function() return mc:GetFightNum() end, 0)) or info.fightNum or 0) or 0
out.refresh_num = tonumber(info.refreshNum or 0) or 0
out.last_refresh_time = tonumber(info.lastRefreshTime or 0) or 0
if mc.CheckIfCanRefresh and info.minesList ~= nil then
  out.can_refresh = _safe_call(function() return mc:CheckIfCanRefresh() end, false) and true or false
end
if mc.GetRefreshCost and info.minesList ~= nil then
  out.refresh_cost = tonumber(_safe_call(function() return mc:GetRefreshCost() end, 0)) or 0
end

if type(info.myMinesList) == 'table' then
  for _, myM in pairs(info.myMinesList) do
    if type(myM) == 'table' and myM.uuid then
      local unrew = (myM.rewarded == nil or myM.rewarded == false or tonumber(myM.rewarded) == 0)
      local endT = tonumber(myM.endTime or 0) or 0
      if endT > 1e12 then endT = math.floor(endT / 1000) end
      if endT > 0 and snap.serverSec >= endT and unrew then
        table.insert(out.claimable_mines, {{
          uuid = tostring(myM.uuid),
          raw_uuid = myM.uuid,
          mineId = tonumber(myM.mineId or 0) or 0,
          endTime = endT,
        }})
      elseif endT > 0 and snap.serverSec < endT then
        out.active_count = out.active_count + 1
        table.insert(out.active_mines, {{
          mineId = tonumber(myM.mineId or 0) or 0,
          uuid = tostring(myM.uuid),
          remaining_sec = math.max(0, endT - snap.serverSec),
          endTime = endT,
        }})
      end
    end
  end
end

local mines = type(info.minesList) == 'table' and info.minesList or {{}}
for _, m in pairs(mines) do
  if type(m) == 'table' and m.mineId then
    out.mines_list_count = out.mines_list_count + 1
    local conf = (mc.GetMineConf and _safe_call(function() return mc:GetMineConf(m.mineId) end, nil)) or {{}}
    local mType = tonumber(conf and conf.type or 0) or 0
    local mLv = tonumber(conf and conf.level or 0) or 0
    local typeMatch = (targetType == 0 or mType == targetType)
    local exactLv = (mLv == targetLevel)
    local rangeLv = (mLv >= minLevel and mLv <= targetLevel)
    if typeMatch and (exactLv or rangeLv) then
      local occ = m.occupyInfo
      local oUid = tostring(m.ownerUid or (type(occ) == 'table' and occ.ownerUid) or '')
      local isSelf = (oUid ~= '' and oUid == tostring(snap.uid))
      local hasPlayer = (oUid ~= '' and oUid ~= '0') or (mc.CheckIfEnemyIsPlayer and _safe_call(function() return mc:CheckIfEnemyIsPlayer(m) end, false)) or false
      if isSelf then
        -- Never attack own occupied mine
      elseif skipPlayers and hasPlayer then
        out.skipped_occupied_players = out.skipped_occupied_players + 1
      else
        local cand = {{
          index = tonumber(m.index or 0) or 0,
          mineId = tonumber(m.mineId),
          type = mType,
          level = mLv,
        }}
        if exactLv then
          table.insert(out.exact_candidates, cand)
        end
        if rangeLv then
          table.insert(out.fallback_candidates, cand)
        end
      end
    else
      out.skipped_wrong_type_or_level = out.skipped_wrong_type_or_level + 1
    end
  end
end
table.sort(out.exact_candidates, function(a, b) return a.level > b.level end)
table.sort(out.fallback_candidates, function(a, b) return a.level > b.level end)
return _enc(out)
"""
        st = _eval_json(cd, pid, inspect_lua, timeout=8.0)
        all_tips.extend(st.get("in_game_tips") or [])
        return st

    state = _inspect_mine_cave_state()
    stages_completed.append("stage_a_sync_info")

    out: dict[str, Any] = {
        "ok": True,
        "task": "mining_event",
        "dry_run": dry_run,
        "is_scheduled_day": is_scheduled_day,
        "event_open": bool(state.get("event_open") or stage_a_req.get("event_open")),
        "claimed": [],
        "refreshed": False,
        "refreshes_performed": 0,
        "refresh_history": [],
        "candidates": [],
        "attacked": None,
        "active_mines": state.get("active_mines") or [],
        "skipped_wrong_type_or_level": int(state.get("skipped_wrong_type_or_level") or 0),
        "skipped_occupied_players": int(state.get("skipped_occupied_players") or 0),
        "fight_num": int(state.get("fight_num") or 0),
        "stages_completed": stages_completed,
        "reason": "",
    }

    # -------------------------------------------------------------------------
    # STAGE B: Claim Completed Mine Melee Rewards (with async settle wait)
    # -------------------------------------------------------------------------
    claimable = state.get("claimable_mines") or []
    if claim_fin and claimable:
        claim_lua = f"""
local dryRun = {str(dry_run).lower()}
local out = {{ ok = true, claimed = {{}} }}
local mc = DataCenter and DataCenter.MineCaveManager
local info = mc and mc.GetMineCaveInfo and mc:GetMineCaveInfo() or {{}}
local snap = _get_player_snapshot()
if type(info.myMinesList) == 'table' then
  for _, myM in pairs(info.myMinesList) do
    if type(myM) == 'table' and myM.uuid then
      local unrew = (myM.rewarded == nil or myM.rewarded == false or tonumber(myM.rewarded) == 0)
      local endT = tonumber(myM.endTime or 0) or 0
      if endT > 1e12 then endT = math.floor(endT / 1000) end
      if endT > 0 and snap.serverSec >= endT and unrew then
        if not dryRun then
          if mc.ReqClaimMineCaveReward then
            pcall(function() mc:ReqClaimMineCaveReward(myM.uuid) end)
          elseif MsgDefines and MsgDefines.ClaimMineCaveReward and SFSNetwork then
            pcall(function() SFSNetwork.SendMessage(MsgDefines.ClaimMineCaveReward, myM.uuid) end)
          end
        end
        table.insert(out.claimed, {{ uuid = tostring(myM.uuid), mineId = tonumber(myM.mineId or 0) or 0 }})
      end
    end
  end
end
return _enc(out)
"""
        claim_res = _eval_json(cd, pid, claim_lua, timeout=8.0)
        all_tips.extend(claim_res.get("in_game_tips") or [])
        out["claimed"] = claim_res.get("claimed") or []
        if not dry_run and out["claimed"]:
            time.sleep(0.8)
            state = _inspect_mine_cave_state()
            out["active_mines"] = state.get("active_mines") or []
            out["fight_num"] = int(state.get("fight_num") or out["fight_num"])
    stages_completed.append("stage_b_claim_rewards")

    max_mines = max(1, int(state.get("max_mines") or 1))
    active_mines = out["active_mines"]
    if len(active_mines) >= max_mines:
        out["action"] = "active_mining"
        out["status"] = "actively_mining"
        first_act = active_mines[0]
        r_min = int(first_act.get("remaining_sec") or 0) // 60
        out["reason"] = f"already_occupying_mine_{r_min // 60}h{r_min % 60}m_remaining"
        out["in_game_tips"] = _clean_in_game_tips(all_tips)
        return out

    if not is_scheduled_day and not force_mining and not out["event_open"]:
        out["reason"] = "off_schedule_not_mon_tue"
        out["in_game_tips"] = _clean_in_game_tips(all_tips)
        return out
    if not out["event_open"]:
        out["reason"] = "mine_cave_event_closed"
        out["in_game_tips"] = _clean_in_game_tips(all_tips)
        return out
    if out["fight_num"] <= 0:
        out["reason"] = "daily_fights_exhausted"
        out["in_game_tips"] = _clean_in_game_tips(all_tips)
        return out

    # -------------------------------------------------------------------------
    # STAGE C: Staged Multi-Refresh Loop for Mine Melee (0..max_refreshes)
    # -------------------------------------------------------------------------
    chosen_candidates: list[dict[str, Any]] = []
    for refresh_idx in range(max_refreshes + 1):
        exact_cands = state.get("exact_candidates") or []
        out["skipped_wrong_type_or_level"] = int(state.get("skipped_wrong_type_or_level") or 0)
        out["skipped_occupied_players"] = int(state.get("skipped_occupied_players") or 0)
        if exact_cands:
            chosen_candidates = exact_cands
            break

        if refresh_idx >= max_refreshes:
            break

        can_refresh = bool(state.get("can_refresh", False))
        if dry_run:
            out["refresh_history"].append({
                "attempt": refresh_idx + 1,
                "mode": "dry_run_would_refresh",
                "can_refresh": can_refresh,
                "refresh_cost": int(state.get("refresh_cost") or 0),
            })
            break

        if not can_refresh:
            out["refresh_history"].append({
                "attempt": refresh_idx + 1,
                "sent": False,
                "reason": "cannot_refresh_or_limit_reached",
            })
            break

        # Respect short server refresh cooldown if lastRefreshTime was < 2 seconds ago
        last_ref_t = int(state.get("last_refresh_time") or 0)
        if last_ref_t > 10**11:
            last_ref_t = last_ref_t // 1000
        srv_sec = int(state.get("server_sec") or 0)
        if srv_sec > 10**11:
            srv_sec = srv_sec // 1000
        if last_ref_t > 0 and srv_sec > 0 and 0 <= (srv_sec - last_ref_t) < 2:
            time.sleep(min(5.0, max(0.4, float(2 - (srv_sec - last_ref_t)))))

        refresh_lua = r"""
local out = { ok = true, sent = false, filter_server = 0 }
local mc = DataCenter and DataCenter.MineCaveManager
if not mc then
  out.ok = false
  out.reason = 'mine_cave_manager_unavailable'
  return _enc(out)
end
local filterSrv = tonumber(mc.canCross or 0) or 0
out.filter_server = filterSrv
if mc.ReqRefreshMineCaveList then
  local okR = pcall(function() mc:ReqRefreshMineCaveList(filterSrv) end)
  out.sent = okR and true or false
elseif mc.TryReqRefreshMineCave then
  local okR = pcall(function() mc:TryReqRefreshMineCave(filterSrv) end)
  out.sent = okR and true or false
elseif MsgDefines and MsgDefines.RefreshMineCaveList and SFSNetwork then
  local okR = pcall(function() SFSNetwork.SendMessage(MsgDefines.RefreshMineCaveList, filterSrv) end)
  out.sent = okR and true or false
end
return _enc(out)
"""
        ref_res = _eval_json(cd, pid, refresh_lua, timeout=8.0)
        all_tips.extend(ref_res.get("in_game_tips") or [])
        if not ref_res.get("sent"):
            out["refresh_history"].append({
                "attempt": refresh_idx + 1,
                "sent": False,
                "reason": "refresh_rpc_not_sent",
            })
            break

        out["refreshed"] = True
        out["refreshes_performed"] = int(out["refreshes_performed"]) + 1

        # Wait 1.2s in Python for RefreshMineCaveListMessage:HandleMessage -> mc:UpdateMineCaveInfo
        time.sleep(1.2)
        state = _inspect_mine_cave_state()
        out["refresh_history"].append({
            "attempt": refresh_idx + 1,
            "sent": True,
            "mines_list_count": int(state.get("mines_list_count") or 0),
            "exact_matches": len(state.get("exact_candidates") or []),
            "fallback_matches": len(state.get("fallback_candidates") or []),
        })

    if not chosen_candidates:
        chosen_candidates = state.get("fallback_candidates") or []

    out["candidates"] = chosen_candidates
    stages_completed.append("stage_c_scan_and_refresh")

    # -------------------------------------------------------------------------
    # STAGE D: Dispatch Free Formation to Occupy Mine
    # -------------------------------------------------------------------------
    if chosen_candidates:
        target_cand = chosen_candidates[0]
        target_idx = int(target_cand.get("index") or 0)
        target_mine_id = int(target_cand.get("mineId") or 0)
        target_m_type = int(target_cand.get("type") or 0)
        target_m_lv = int(target_cand.get("level") or 0)

        attack_lua = f"""
local dryRun = {str(dry_run).lower()}
local targetIndex = {target_idx}
local targetMineId = {target_mine_id}
local targetMType = {target_m_type}
local targetMLv = {target_m_lv}
local out = {{ ok = true, attacked = nil, action = '', reason = '' }}
local mc = DataCenter and DataCenter.MineCaveManager
if not mc then
  out.reason = 'mine_cave_manager_unavailable'
  return _enc(out)
end
local canAtk = (mc.CheckIfCanAttack and _safe_call(function() return mc:CheckIfCanAttack() end, true))
if canAtk == nil then canAtk = true end
if not canAtk then
  out.reason = 'cannot_attack_cave'
  return _enc(out)
end
local frees = _pick_free_formations(0, {_used_formations_lua(context, pid)}, not dryRun)
local chosen = frees[1]
if not chosen then
  out.reason = 'no_free_formation_available'
  return _enc(out)
end
if MsgDefines and MsgDefines.BeginPvpCaveFight and SFSNetwork then
  local af = DataCenter and DataCenter.ArmyFormationDataManager
  local fullForm = af and af.GetOneArmyInfoByUuid and af:GetOneArmyInfoByUuid(chosen.uuid) or nil
  local heroList = {{}}
  if fullForm and type(fullForm.heroes) == 'table' then
    for u, idx in pairs(fullForm.heroes) do
      table.insert(heroList, {{ index = tonumber(idx), uuid = tonumber(u) or tostring(u) }})
    end
  end
  local soldiersMap = (fullForm and type(fullForm.soldiers) == 'table' and fullForm.soldiers) or {{}}
  local powerStr = tostring(chosen.power or '0')
  if not dryRun then
    if mc.SetAttackMineIndex then pcall(function() mc:SetAttackMineIndex(targetIndex) end) end
    if mc.SetDispatchFormation then pcall(function() mc:SetDispatchFormation(chosen.uuid) end) end
    local sendOk, sendErr = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.BeginPvpCaveFight, targetIndex, chosen.uuid, heroList, soldiersMap, powerStr, 0, 0)
    end)
    if not sendOk then
      out.error = tostring(sendErr)
    end
  end
  out.attacked = {{
    mineIndex = targetIndex,
    mineId = targetMineId,
    type = targetMType,
    level = targetMLv,
    formationUuid = tostring(chosen.uuid),
    formationIndex = tonumber(chosen.index or 0),
  }}
  out.action = string.format('attacked_mine_%d_level_%d', targetIndex, targetMLv)
else
  out.reason = 'begin_pvp_cave_fight_unavailable'
end
return _enc(out)
"""
        atk_res = _eval_json(cd, pid, attack_lua, timeout=8.0)
        all_tips.extend(atk_res.get("in_game_tips") or [])
        if atk_res.get("attacked"):
            out["attacked"] = atk_res["attacked"]
            out["action"] = atk_res.get("action") or f"attacked_mine_{target_idx}_level_{target_m_lv}"
            if not dry_run and context is not None and out["attacked"].get("formationUuid"):
                _record_used_formations(context, pid, [str(out["attacked"]["formationUuid"])])
        else:
            out["reason"] = atk_res.get("reason") or "attack_skipped"
        if atk_res.get("error"):
            out["error"] = atk_res["error"]
    else:
        out["reason"] = "no_matching_unoccupied_mines"

    stages_completed.append("stage_d_dispatch_attack")
    out["in_game_tips"] = _clean_in_game_tips(all_tips)
    return out


_EXPLORE_FAIL_CACHE: dict[tuple[int, int], int] = {}


def run_vip_store_rewards(
    cd: Any,
    pid: int,
    snapshot: dict[str, Any],
    ccfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Claim VIP daily points chest, VIP daily freebie, Store 2nd-tab (VIP Shop) free items, and free weekly pack."""
    vcfg = ccfg.get("vip_store_rewards") or {}
    claim_points = bool(vcfg.get("claim_vip_points", True))
    claim_daily = bool(vcfg.get("claim_vip_daily_freebie", True))
    claim_store = bool(vcfg.get("claim_store_vip_tab_free", True))
    claim_weekly = bool(vcfg.get("claim_weekly_gift_freebie", True))

    lua_hdr = (
        f"local dryRun = {'true' if dry_run else 'false'}\n"
        f"local claimPoints = {'true' if claim_points else 'false'}\n"
        f"local claimDaily = {'true' if claim_daily else 'false'}\n"
        f"local claimStore = {'true' if claim_store else 'false'}\n"
        f"local claimWeekly = {'true' if claim_weekly else 'false'}\n"
    )
    lua_body = r"""
local out = {
  ok = true,
  dry_run = dryRun,
  vip_level = 0,
  can_vip_points = false,
  can_vip_daily = false,
  can_weekly_free = false,
  store_free_candidates = {},
  claimed_vip_points = false,
  claimed_vip_daily = false,
  claimed_store_items = {},
  claimed_weekly_free = false,
}

local vm = DataCenter and DataCenter.VIPManager
if vm then
  out.vip_level = tonumber(vm.GetVipLevel and vm:GetVipLevel() or 0) or 0
  out.can_vip_points = (vm.CanGetDailyPoint and vm:CanGetDailyPoint()) and true or false
  out.can_vip_daily = (vm.FreeGoodCanGet and vm:FreeGoodCanGet()) and true or false
  if claimPoints and out.can_vip_points then
    if not dryRun and vm.RequestVipGetDailyPoint then
      pcall(function() vm:RequestVipGetDailyPoint() end)
    end
    out.claimed_vip_points = true
  end
  if claimDaily and out.can_vip_daily then
    if not dryRun and vm.ReceiveFreeReward then
      pcall(function() vm:ReceiveFreeReward() end)
    end
    out.claimed_vip_daily = true
  end
end

local csm = DataCenter and DataCenter.CommonShopManager
if claimStore and csm and csm.GetGoodsListByShopType then
  local goods = csm:GetGoodsListByShopType(2)
  local infoDic = (type(csm.goodsInfoDic) == "table" and csm.goodsInfoDic[2]) or {}
  if type(goods) == "table" then
    for _, item in pairs(goods) do
      if type(item) == "table" and item.id then
        local costNum = tonumber(item.costNum or 0) or 0
        local maxTimes = tonumber(item.maxTimes or 1) or 1
        local vipReq = tonumber(item.vipLevel or 0) or 0
        local info = infoDic[item.id] or infoDic[tonumber(item.id)]
        local bought = tonumber(type(info) == "table" and info.boughtTimes or 0) or 0
        if costNum == 0 and bought < maxTimes and vipReq <= out.vip_level then
          table.insert(out.store_free_candidates, {
            id = tonumber(item.id),
            itemId = tostring(item.itemId or ""),
            boughtTimes = bought,
            maxTimes = maxTimes,
          })
          if not dryRun and MsgDefines and MsgDefines.BuyCommonShopGoods and SFSNetwork then
            pcall(function()
              SFSNetwork.SendMessage(MsgDefines.BuyCommonShopGoods, tonumber(item.id), nil, 1)
            end)
          end
          table.insert(out.claimed_store_items, tonumber(item.id))
        end
      end
    end
  end
end

if claimWeekly and GiftPackageData and GiftPackageData.CheckIfHasFreeWeeklyPackage then
  out.can_weekly_free = GiftPackageData:CheckIfHasFreeWeeklyPackage() and true or false
  if out.can_weekly_free then
    if not dryRun and MsgDefines and MsgDefines.BuyFreeWeeklyPackage and SFSNetwork then
      pcall(function() SFSNetwork.SendMessage(MsgDefines.BuyFreeWeeklyPackage) end)
    end
    out.claimed_weekly_free = true
  end
end

if out.claimed_vip_points or out.claimed_vip_daily or #out.claimed_store_items > 0 or out.claimed_weekly_free then
  pcall(_dismiss_modal_dialogs)
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua_hdr + lua_body, timeout=8.0)
    did_send = (
        not dry_run
        and res.get("ok")
        and (
            res.get("claimed_vip_points")
            or res.get("claimed_vip_daily")
            or res.get("claimed_store_items")
            or res.get("claimed_weekly_free")
        )
    )
    if did_send:
        time.sleep(0.6)
        verify = _eval_json(
            cd,
            pid,
            r"""
local v = { ok = true }
local vm = DataCenter and DataCenter.VIPManager
if vm then
  v.remaining_vip_points = (vm.CanGetDailyPoint and vm:CanGetDailyPoint()) and true or false
  v.remaining_vip_daily = (vm.FreeGoodCanGet and vm:FreeGoodCanGet()) and true or false
end
if GiftPackageData and GiftPackageData.CheckIfHasFreeWeeklyPackage then
  v.remaining_weekly_free = GiftPackageData:CheckIfHasFreeWeeklyPackage() and true or false
end
return _enc(v)
""",
            timeout=5.0,
        )
        if verify.get("ok"):
            res["verified_after"] = {k: val for k, val in verify.items() if k != "ok"}
    return res


def snapshot_formations_and_gear(cd: Any, pid: int) -> dict[str, Any]:
    """Capture snapshot of all formation layouts and hero gear loadouts for safety."""
    lua = r"""
local out = { ok = true, formations = {}, gear_map = {}, f1_hero_uuids = {}, f1_gear_sets = {} }
local afm = DataCenter and (DataCenter.ArmyFormationDataManager or DataCenter.ArmyFormationManager)
if afm and afm.ArmyFormationList then
  for k, f in pairs(afm.ArmyFormationList) do
    if type(f) == "table" then
      local fHeroes = {}
      if f.heroes and type(f.heroes) == "table" then
        for hk, hv in pairs(f.heroes) do
          local hid = (type(hk) == "string" and #hk > 5 and hk) or (type(hk) == "number" and hk > 100000 and tostring(hk)) or (type(hv) == "table" and (hv.uuid or hv.heroId or hv.id)) or hv
          if hid and tostring(hid) ~= "" and tostring(hid) ~= "0" then table.insert(fHeroes, tostring(hid)) end
        end
      end
      table.insert(out.formations, {
        index = tonumber(f.index or k) or 0,
        uuid = tostring(f.uuid or ''),
        name = tostring(f.name or ''),
        heroes = fHeroes
      })
    end
  end
end

local hem = DataCenter and DataCenter.HeroEquipManager

-- Hero ID <-> UUID bidirectional mapping via HeroDataManager
local hdm = DataCenter and DataCenter.HeroDataManager
local uuidToHeroId = {}
local heroIdToUuid = {}
if hdm then
  local hList = (hdm.GetAllHeroList and _safe_call(function() return hdm:GetAllHeroList() end, nil)) or hdm.allHeroList or hdm.allHero or {}
  if type(hList) == "table" then
    for _, h in pairs(hList) do
      if type(h) == "table" then
        local huuid = tostring(h.uuid or "")
        local hid = tostring(h.heroId or h.id or "")
        if huuid ~= "" and hid ~= "" then
          uuidToHeroId[huuid] = hid
          heroIdToUuid[hid] = huuid
        end
      end
    end
  end
end

if hem and hem.heroEquipMap then
  for hid, eqList in pairs(hem.heroEquipMap) do
    local sMap = {}
    if type(eqList) == "table" then
      for slot, eq in pairs(eqList) do
        local eqUuid = type(eq) == "table" and (eq.uuid or eq.id) or tostring(eq or '')
        if eqUuid and eqUuid ~= '' then sMap[tostring(slot)] = eqUuid end
      end
    end
    local hidStr = tostring(hid)
    out.gear_map[hidStr] = sMap
    if uuidToHeroId[hidStr] and not out.gear_map[uuidToHeroId[hidStr]] then
      out.gear_map[uuidToHeroId[hidStr]] = sMap
    end
    if heroIdToUuid[hidStr] and not out.gear_map[heroIdToUuid[hidStr]] then
      out.gear_map[heroIdToUuid[hidStr]] = sMap
    end
  end
end

-- Also inspect hem.allEquip to discover equipped gear and build ranked sets
local heroEquipRank = {}
if hem and hem.allEquip then
  for eqId, eq in pairs(hem.allEquip) do
    if type(eq) == "table" then
      local eqHero = tostring(eq.heroId or eq.heroUuid or eq.ownerUuid or eq.ownerId or "")
      local slot = tostring(eq.slot or eq.pos or eq.equipSlot or 1)
      local eqUuid = tostring(eq.uuid or eq.id or eqId or "")
      local eqLv = tonumber(eq.level or eq.lv or eq.quality or 1) or 1
      if eqHero ~= "" and eqHero ~= "0" and eqUuid ~= "" then
        if not out.gear_map[eqHero] then out.gear_map[eqHero] = {} end
        if not out.gear_map[eqHero][slot] then out.gear_map[eqHero][slot] = eqUuid end
        local crossId = uuidToHeroId[eqHero] or heroIdToUuid[eqHero]
        if crossId then
          if not out.gear_map[crossId] then out.gear_map[crossId] = {} end
          if not out.gear_map[crossId][slot] then out.gear_map[crossId][slot] = eqUuid end
        end

        local rankKey = uuidToHeroId[eqHero] or eqHero
        if not heroEquipRank[rankKey] then heroEquipRank[rankKey] = { hero = rankKey, totalLv = 0, count = 0, gears = {} } end
        heroEquipRank[rankKey].totalLv = heroEquipRank[rankKey].totalLv + eqLv
        heroEquipRank[rankKey].count = heroEquipRank[rankKey].count + 1
        heroEquipRank[rankKey].gears[slot] = eqUuid
      end
    end
  end
end

-- Identify F1 heroes (or active formation with deployed heroes) and their 5 gear sets
local f_active = nil
local f1IsLocked = false
local formList = (afm and afm.GetArmyFormationList and _safe_call(function() return afm:GetArmyFormationList() end, nil)) or (afm and afm.ArmyFormationList) or {}
if type(formList) == "table" then
  for _, f in pairs(formList) do
    if type(f) == "table" then
      local fState = tonumber(f.state or 0) or 0
      local hasMarch = (f.marchUuid and tostring(f.marchUuid) ~= '' and tostring(f.marchUuid) ~= '0')
      if tonumber(f.index or 0) == 1 then
        if fState ~= 0 or hasMarch then f1IsLocked = true end
        if not f_active then f_active = f end
      elseif fState ~= 0 or hasMarch then
        f1IsLocked = true
      end
    end
  end
  if not f_active then
    for _, f in pairs(formList) do
      if type(f) == "table" and f.heroes and next(f.heroes) ~= nil then
        f_active = f
        break
      end
    end
  end
  if not f_active and formList[1] then f_active = formList[1] end
end
if afm and afm.GetInMarchArmyFormationUuids then
  local ok_im, im = pcall(function() return afm:GetInMarchArmyFormationUuids() end)
  if ok_im and type(im) == "table" and next(im) ~= nil then f1IsLocked = true end
end
if afm and afm.IsFormationMarching then
  local ok_m, m = pcall(function() return afm:IsFormationMarching(1) end)
  if ok_m and m then f1IsLocked = true end
end
out.f1_locked = f1IsLocked

local f1Heroes = {}
if f_active then
  if f_active.heroUuids and type(f_active.heroUuids) == "table" and #f_active.heroUuids > 0 then
    for idx = 1, 5 do
      if f_active.heroUuids[idx] then table.insert(f1Heroes, f_active.heroUuids[idx]) end
    end
  end
  if #f1Heroes == 0 and f_active.heroes and type(f_active.heroes) == "table" then
    for hk, hv in pairs(f_active.heroes) do
      local hid = (type(hk) == "string" and #hk > 5 and hk) or (type(hk) == "number" and hk > 100000 and tostring(hk)) or (type(hv) == "table" and (hv.uuid or hv.heroId or hv.id)) or hv
      if hid and tostring(hid) ~= "" and tostring(hid) ~= "0" then
        table.insert(f1Heroes, tostring(hid))
      end
    end
  end
end

for idx = 1, math.min(5, #f1Heroes) do
  local hid = f1Heroes[idx]
  if hid then
    local hidStr = tostring(hid)
    table.insert(out.f1_hero_uuids, hidStr)
    local gset = out.gear_map[hidStr]
    if (not gset or next(gset) == nil) and uuidToHeroId[hidStr] then
      gset = out.gear_map[uuidToHeroId[hidStr]]
    end
    if (not gset or next(gset) == nil) and heroIdToUuid[hidStr] then
      gset = out.gear_map[heroIdToUuid[hidStr]]
    end
    if gset and next(gset) ~= nil then
      table.insert(out.f1_gear_sets, gset)
    end
  end
end

-- Fallback to top 5 highest-level equipped sets in hem.allEquip if F1 sets are missing/insufficient
if #out.f1_gear_sets < 5 and next(heroEquipRank) ~= nil then
  local rankedList = {}
  for _, r in pairs(heroEquipRank) do
    table.insert(rankedList, r)
  end
  table.sort(rankedList, function(a, b)
    if a.count ~= b.count then return a.count > b.count end
    return a.totalLv > b.totalLv
  end)
  for _, r in ipairs(rankedList) do
    if #out.f1_gear_sets >= 5 then break end
    local alreadyIn = false
    for _, existing in ipairs(out.f1_gear_sets) do
      if existing == r.gears then alreadyIn = true; break end
    end
    if not alreadyIn and next(r.gears) ~= nil then
      table.insert(out.f1_gear_sets, r.gears)
    end
  end
end

_G.__hzOriginalGearSnapshot = out
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=8.0)


def restore_formations_and_gear(cd: Any, pid: int) -> dict[str, Any]:
    """Restore all hero gear back to original owners and formation layouts from snapshot."""
    lua = r"""
local out = { ok = true, restored_count = 0, errors = {} }
local snap = _G.__hzOriginalGearSnapshot
if not snap or not snap.gear_map or snap.f1_locked then
  out.reason = snap and snap.f1_locked and "f1_was_locked_no_gear_swapped" or "no_gear_snapshot_found"
  _G.__hzOriginalGearSnapshot = nil
  return _enc(out)
end

local hem = DataCenter and DataCenter.HeroEquipManager
local hdm = DataCenter and DataCenter.HeroDataManager
local installMsg = (MsgDefines and MsgDefines.HeroEquipInstall) or "hero.equip.install"

for origHeroId, slots in pairs(snap.gear_map) do
  if type(slots) == "table" then
    local eqArr = {}
    for _, eqUuid in pairs(slots) do
      local numEq = tonumber(eqUuid)
      if numEq and numEq > 0 then
        table.insert(eqArr, numEq)
      end
    end
    if #eqArr > 0 then
      local numHeroId = tonumber(origHeroId)
      if (not numHeroId or numHeroId > 1000000000) and hdm then
        local h = hdm.GetHeroByUuid and _safe_call(function() return hdm:GetHeroByUuid(origHeroId) end, nil)
        if h and (h.heroId or h.id) then numHeroId = tonumber(h.heroId or h.id) end
      end
      if numHeroId and numHeroId > 0 then
        local toInstall = {}
        for _, eqNum in ipairs(eqArr) do
          local eqObj = hem and hem.GetEquipByUuid and _safe_call(function() return hem:GetEquipByUuid(eqNum) end, nil)
          local ownerId = eqObj and tonumber(eqObj.heroId or 0) or 0
          if ownerId == 0 then
            table.insert(toInstall, eqNum)
          end
        end
        if #toInstall > 0 then
          local ok = false
          if hem and hem.HeroEquipInstall then
            ok = pcall(function() hem:HeroEquipInstall(numHeroId, toInstall) end)
          end
          if not ok and SFSNetwork and SFSNetwork.SendMessage then
            pcall(function() SFSNetwork.SendMessage(installMsg, numHeroId, toInstall) end)
          end
          out.restored_count = out.restored_count + #toInstall
        end
      end
    end
  end
end

_G.__hzOriginalGearSnapshot = nil
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=10.0)


def run_hero_battlefield(
    cd: Any,
    pid: int,
    snapshot: dict[str, Any],
    ccfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pre-fill each of the 3 Campervan factions strictly with strongest faction heroes, borrow F1 gear, and push highest stage with >=90% win-rate."""
    hcfg = ccfg.get("hero_battlefield") or {}
    prefill = bool(hcfg.get("auto_prefill_strongest_faction", True))
    use_quick_deploy = bool(hcfg.get("use_quick_deploy", True))
    auto_skip_battle = bool(hcfg.get("auto_skip_battle", True))
    max_battles = max(1, min(15, int(hcfg.get("max_battles_per_faction", 5))))
    stop_on_fail = bool(hcfg.get("stop_on_fail", True))
    skip_failed = bool(hcfg.get("skip_if_failed_this_period", True))

    camp_names = {1: "Blood Rose", 2: "Wings of Dawn", 3: "Guard of Order"}

    # First check overall status & inspect all 3 factions + strictly build per-faction rosters
    inspect_lua = r"""
local out = { ok = true, event_open = false, camps = {} }
local lo = DataCenter and DataCenter.LandingOperationsDataManager
if not lo or not lo.data then
  out.reason = "landing_operations_unavailable"
  return _enc(out)
end
out.event_open = (lo.IsOpen and lo:IsOpen()) and true or false
local hd = DataCenter and DataCenter.HeroDataManager
local allHeroes = (hd and hd.GetAllHeroList and hd:GetAllHeroList()) or {}
local tcm = DataCenter and DataCenter.TowerClimbingManager

local afm = DataCenter and (DataCenter.ArmyFormationDataManager or DataCenter.ArmyFormationManager)
local marchingHeroUuids = {}
local formList = (afm and afm.GetArmyFormationList and _safe_call(function() return afm:GetArmyFormationList() end, nil)) or (afm and afm.ArmyFormationList) or {}
if type(formList) == "table" then
  for _, f in pairs(formList) do
    if type(f) == "table" and tonumber(f.state or 0) ~= 0 and f.heroes then
      for hk, hv in pairs(f.heroes) do
        local hu = (type(hk) == "string" and #hk > 5 and hk) or (type(hk) == "number" and hk > 100000 and tostring(hk)) or (type(hv) == "table" and (hv.uuid or hv.heroId or hv.id)) or hv
        if hu and tostring(hu) ~= "" and tostring(hu) ~= "0" then
          marchingHeroUuids[tostring(hu)] = true
        end
      end
    end
  end
end

for camp = 1, 3 do
  local list = {}
  for _, h in pairs(allHeroes) do
    if type(h) == "table" and tonumber(h.camp or 0) == camp then
      table.insert(list, h)
    end
  end
  table.sort(list, function(a, b)
    local pa = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(a)) or 0
    local pb = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(b)) or 0
    return pa > pb
  end)
  local heroUuids = {}
  local heroPreview = {}
  local marchingHeroCount = 0
  for i = 1, math.min(5, #list) do
    local h = list[i]
    local hu = tostring(h.uuid or "")
    if hu ~= "" and marchingHeroUuids[hu] then
      marchingHeroCount = marchingHeroCount + 1
    end
    table.insert(heroUuids, h.uuid)
    table.insert(heroPreview, {
      id = tonumber(h.heroId or h.id or 0),
      uuid = hu,
      camp = tonumber(h.camp or 0),
      power = tonumber((HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(h)) or 0) or 0,
      is_marching = (hu ~= "" and marchingHeroUuids[hu]) and true or false,
    })
  end
  local cap = 0
  if #heroUuids > 0 and MarchUtil and MarchUtil.GetHeroMaxSoldiers and PveEntrance and PveEntrance.LandingOperation then
    local okC, valC = pcall(function() return MarchUtil.GetHeroMaxSoldiers(heroUuids, PveEntrance.LandingOperation) end)
    if okC and valC then cap = tonumber(valC) or 0 end
  end
  out.camps[tostring(camp)] = {
    camp = camp,
    unlocked = (lo.IsCampUnlock and lo:IsCampUnlock(camp)) and true or false,
    can_fight = (lo.IsCampCanFight and lo:IsCampCanFight(camp)) and true or false,
    failed_this_period = (lo.IsCampFailedThisPeriod and lo:IsCampFailedThisPeriod(camp)) and true or false,
    target_chapter = tonumber(lo.data.GetTargetChapter and lo.data:GetTargetChapter(camp) or 0) or 0,
    unlock_chapter = tonumber(lo.data.GetUnlockChapter and lo.data:GetUnlockChapter(camp) or 0) or 0,
    cur_level = tonumber(lo.data.GetCampLevel and lo.data:GetCampLevel(camp) or 0) or 0,
    top_heroes = heroPreview,
    marching_hero_count = marchingHeroCount,
    troop_cap = cap,
  }
end
return _enc(out)
"""
    status = _eval_json(cd, pid, inspect_lua, timeout=8.0)
    if not status.get("ok"):
        return status
    if not status.get("event_open"):
        status["dry_run"] = dry_run
        status["reason"] = "hero_battlefield_closed"
        status["factions"] = {}
        return status

    faction_results: dict[str, Any] = {}
    total_wins = 0
    total_failures = 0
    quick_deploys = 0
    skips_triggered = 0

    # Snapshot all formations and gear loadouts before altering equipment
    if not dry_run:
        snapshot_formations_and_gear(cd, pid)

    try:
        for camp in (1, 2, 3):
            c_key = str(camp)
            c_info = (status.get("camps") or {}).get(c_key) or {}
            f_rep: dict[str, Any] = {
                "name": camp_names.get(camp, f"Faction {camp}"),
                "unlocked": c_info.get("unlocked", False),
                "can_fight": c_info.get("can_fight", False),
                "failed_this_period": c_info.get("failed_this_period", False),
                "start_chapter": c_info.get("target_chapter", 0),
                "start_level": c_info.get("cur_level", 0),
                "hero_count": len(c_info.get("top_heroes") or []),
                "troop_cap": c_info.get("troop_cap", 0),
                "wins": 0,
                "stopped_reason": None,
                "battles": [],
            }

            if not c_info.get("unlocked"):
                f_rep["stopped_reason"] = "faction_locked"
                faction_results[c_key] = f_rep
                continue
            if skip_failed and c_info.get("failed_this_period"):
                f_rep["stopped_reason"] = "already_failed_this_period"
                faction_results[c_key] = f_rep
                continue
            if not c_info.get("can_fight"):
                f_rep["stopped_reason"] = "cannot_fight"
                faction_results[c_key] = f_rep
                continue
            if len(c_info.get("top_heroes") or []) == 0 or int(c_info.get("troop_cap") or 0) <= 0:
                f_rep["stopped_reason"] = "no_faction_heroes_or_troops"
                faction_results[c_key] = f_rep
                continue
            if dry_run:
                f_rep["stopped_reason"] = "dry_run_preview"
                f_rep["top_heroes"] = c_info.get("top_heroes")
                faction_results[c_key] = f_rep
                continue

            # Ensure Target Chapter is locked in on the server before launching PVE battles
            # (HeroBattleSetTargetChapter rejects unlockChapter=curCampChapter+1 with E100172;
            # valid target chapter at start of period is curCampChapter, e.g. 1..curCampChapter).
            if int(c_info.get("target_chapter") or 0) <= 0:
                init_ch_lua = (
                    f"local camp = {camp}\n"
                ) + r"""
local lo = DataCenter and DataCenter.LandingOperationsDataManager
if not lo or not lo.data then return _enc({ ok = false, reason = 'lo_missing' }) end
local curT = tonumber(lo.data.GetTargetChapter and lo.data:GetTargetChapter(camp) or 0) or 0
local campCh = tonumber(lo.data.GetCampChapter and lo.data:GetCampChapter(camp) or 0) or 1
if curT <= 0 and campCh > 0 and lo.SendTargetChapter then
  pcall(function() lo:SendTargetChapter(camp, campCh) end)
  return _enc({ ok = true, sent = true, target_ch = campCh })
end
return _enc({ ok = true, sent = false, target_ch = curT > 0 and curT or campCh })
"""
                init_res = _eval_json(cd, pid, init_ch_lua, timeout=6.0)
                if init_res.get("sent"):
                    time.sleep(0.7)

            for _ in range(max_battles):
                step_lua = (
                    f"local camp = {camp}\n"
                    f"local doPrefill = {'true' if prefill else 'false'}\n"
                ) + r"""
local out = { ok = true, sent = false, reason = "" }
local lo = DataCenter and DataCenter.LandingOperationsDataManager
if not lo or not lo.data then
  out.reason = "lo_missing"; return _enc(out)
end
if lo.IsCampFailedThisPeriod and lo:IsCampFailedThisPeriod(camp) then
  out.reason = "failed_this_period"; return _enc(out)
end
if lo.IsCampCanFight and not lo:IsCampCanFight(camp) then
  out.reason = "cannot_fight"; return _enc(out)
end

-- 1. Build strictly faction-filtered top 5 heroes
local hd = DataCenter and DataCenter.HeroDataManager
local loHeroes = {}
local realHeroes = {}
local realHeroesByUuid = {}
local uuids = {}
if doPrefill and hd and hd.GetAllHeroList then
  local list = {}
  for _, h in pairs(hd:GetAllHeroList()) do
    if type(h) == "table" and tonumber(h.camp or 0) == camp then
      table.insert(list, h)
    end
  end
  table.sort(list, function(a, b)
    local pa = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(a)) or 0
    local pb = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(b)) or 0
    return pa > pb
  end)
  for i = 1, math.min(5, #list) do
    local h = list[i]
    realHeroes[i] = h
    realHeroesByUuid[h.uuid] = h
    loHeroes[i] = {
      index = i,
      uuid = h.uuid,
      heroId = h.heroId or h.id,
      id = h.heroId or h.id,
      camp = camp,
      rarity = h.rarity,
      level = h.level,
      finalLevel = h.finalLevel,
      quality = h.quality,
      power = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(h)) or 0,
    }
    table.insert(uuids, h.uuid)
  end
else
  local curH = (lo.GetBattleHeroByCamp and lo:GetBattleHeroByCamp(camp)) or {}
  for i = 1, 5 do
    if curH[i] then
      local hu = type(curH[i]) == "table" and curH[i].uuid or curH[i]
      local hObj = hd and hd.GetHeroByUuid and hd:GetHeroByUuid(hu)
      if hObj then
        realHeroes[i] = hObj
        realHeroesByUuid[hu] = hObj
      end
      loHeroes[i] = type(curH[i]) == "table" and curH[i] or { index = i, uuid = hu }
      if loHeroes[i].index == nil then loHeroes[i].index = i end
      if hObj and loHeroes[i].rarity == nil then loHeroes[i].rarity = hObj.rarity end
      table.insert(uuids, hu)
    end
  end
end

if #uuids == 0 then
  out.reason = "no_faction_heroes"; return _enc(out)
end

-- March Conflict Check: never swap equipment if any selected hero or F1 is deployed in the field
-- (Campervan PVE itself runs cleanly even while world marches are active.)
local afm = DataCenter and (DataCenter.ArmyFormationDataManager or DataCenter.ArmyFormationManager)
local isAnyHeroMarching = false
local formList = (afm and afm.GetArmyFormationList and _safe_call(function() return afm:GetArmyFormationList() end, nil)) or (afm and afm.ArmyFormationList) or {}
if type(formList) == "table" then
  for _, f in pairs(formList) do
    if type(f) == "table" and tonumber(f.state or 0) ~= 0 and f.heroes then
      for hk, hv in pairs(f.heroes) do
        local hu = (type(hk) == "string" and #hk > 5 and hk) or (type(hk) == "number" and hk > 100000 and tostring(hk)) or (type(hv) == "table" and (hv.uuid or hv.heroId or hv.id)) or hv
        if hu and tostring(hu) ~= "" and tostring(hu) ~= "0" then
          for _, lu in ipairs(uuids) do
            if tostring(lu) == tostring(hu) then
              isAnyHeroMarching = true
              break
            end
          end
        end
        if isAnyHeroMarching then break end
      end
    end
    if isAnyHeroMarching then break end
  end
end

-- 2. Equip unequipped suggested gear onto faction heroes (numeric equip UUIDs only; never steal gear already worn by another hero without uninstall, and skip if marching)
local hem = DataCenter and DataCenter.HeroEquipManager
local f1Locked = isAnyHeroMarching or (_G.__hzOriginalGearSnapshot and _G.__hzOriginalGearSnapshot.f1_locked)
if not f1Locked and hem and hem.GetSuggestUnEquipUuidListByHeroId and hem.HeroEquipInstall then
  for i = 1, #loHeroes do
    local targetH = loHeroes[i]
    local tHeroId = targetH and tonumber(targetH.heroId or targetH.id) or 0
    if tHeroId > 0 then
      local okSug, sugList = pcall(function() return hem:GetSuggestUnEquipUuidListByHeroId(tHeroId) end)
      if okSug and type(sugList) == "table" and #sugList > 0 then
        local numList = {}
        for _, u in ipairs(sugList) do
          local nu = tonumber(u)
          if nu and nu > 0 then table.insert(numList, nu) end
        end
        if #numList > 0 then
          pcall(function() hem:HeroEquipInstall(tHeroId, numList) end)
        end
      end
    end
  end
end

-- 3. Calculate our power + army capacity (using real HeroData objects so HeroUtils.GetHeroPower has .rarity)
local ourHeroPower = 0
for i, h in ipairs(loHeroes) do
  local rh = realHeroes[i] or h
  local okP, p = pcall(function() return HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(rh) end)
  p = (okP and tonumber(p)) or (tonumber(h.power or 0) or 0)
  ourHeroPower = ourHeroPower + p
end
local cap = MarchUtil and MarchUtil.GetHeroMaxSoldiers and MarchUtil.GetHeroMaxSoldiers(uuids, PveEntrance.LandingOperation) or 0
local rawArmy = DataCenter and DataCenter.TowerClimbingManager and DataCenter.TowerClimbingManager:GetSelfArmys(tonumber(cap) or 0) or {}
-- UserSetHeroBattleArmyMessage & UserSelectHeroBattlePveMessage expect army as dictionary map { [tostring(armyId)] = count }
local loArmyMap = {}
for ak, av in pairs(rawArmy) do
  local cnt = math.floor(tonumber(av) or 0)
  if cnt > 0 then
    loArmyMap[tostring(ak)] = cnt
  end
end

local squadPower = 0
if MarchUtil and MarchUtil.GetFormationPower then
  local campParam = 0
  pcall(function()
    if MarchUtil.GetCampAddParam then campParam = MarchUtil.GetCampAddParam(realHeroesByUuid) or 0 end
  end)
  local okP, pVal = pcall(function()
    return MarchUtil.GetFormationPower(realHeroesByUuid, loArmyMap, 1, campParam)
  end)
  if okP and pVal and tonumber(pVal) and tonumber(pVal) > 0 then
    squadPower = math.ceil(tonumber(pVal))
  end
end
local ourTotalPower = squadPower > 0 and squadPower or ourHeroPower

-- 4. Dynamic Chapter & Level selection: Target Selection in Campervan
-- curCampLevel[camp] holds the completed level count in the current period's Target Chapter (0..#trigger).
-- Valid Target Chapter for HeroBattleSetTargetChapter is curCampChapter (NOT unlockChapter = curCampChapter+1, which returns E100172).
local curUnlockLev = lo and lo.data and lo.data.curUnlockLev and tonumber(lo.data.curUnlockLev[camp] or 0) or 0
local curCampLvl = tonumber(lo.data.GetCampLevel and lo.data:GetCampLevel(camp) or 0) or 0
local campCh = tonumber(lo.data.GetCampChapter and lo.data:GetCampChapter(camp) or 0) or 1
local curCh = tonumber(lo.data.GetTargetChapter and lo.data:GetTargetChapter(camp) or 0) or 0
local targetCh = curCh > 0 and curCh or math.max(campCh, 1)

local maps = (lo.GetMapByCamp and lo:GetMapByCamp(camp)) or {}
local pltMgr = PveLevelTemplateManager or (DataCenter and DataCenter.PveLevelTemplateManager)

local chosenLvlIdx = curCampLvl + 1
local chosenTrigId = nil
local chosenFirstTrig = nil
local enemyPower = 0

local map = (lo.GetMapByCamp and lo:GetMapByCamp(camp, targetCh)) or maps[targetCh] or maps[1] or {}
if type(map) == "table" and type(map.trigger) == "table" and #map.trigger > 0 then
  if chosenLvlIdx > #map.trigger then
    out.reason = "chapter_complete"; out.target_ch = targetCh; out.prev_camp_lvl = curCampLvl; return _enc(out)
  end
  if chosenLvlIdx < 1 then chosenLvlIdx = 1 end
  chosenTrigId = map.trigger[chosenLvlIdx]
  -- Verified via Megamind hero_battle XML: chapter enemy power lives on map.power (PveLevelTemplate has no power column)
  enemyPower = tonumber(map.power or map.fightpower or map.recommendPower or 0) or 0
  if chosenTrigId and pltMgr then
    local tmpl = pltMgr:GetTemplate(chosenTrigId)
    if tmpl then
      chosenFirstTrig = type(tmpl.triggerList) == "table" and tmpl.triggerList[1] or chosenTrigId
      if enemyPower <= 0 then
        enemyPower = tonumber(tmpl.fightpower or tmpl.power or tmpl.recommendPower or 0) or 0
      end
    end
  end
  if enemyPower <= 0 and lo.GetMapTemplateByLevelId and chosenTrigId then
    local mtpl = _safe_call(function() return lo:GetMapTemplateByLevelId(chosenTrigId) end, nil)
    if type(mtpl) == "table" then
      enemyPower = tonumber(mtpl.power or mtpl.fightpower or mtpl.recommendPower or 0) or 0
    end
  end
end

if not chosenTrigId or not chosenFirstTrig then
  out.reason = "pve_trigger_missing"; out.trig_lvl = chosenTrigId; return _enc(out)
end

local chipFid = 0
if DataCenter and DataCenter.CarChipManager and FormationSetting and FormationSetting.LandingOperation then
  pcall(function() chipFid = DataCenter.CarChipManager:GetSetting(FormationSetting.LandingOperation, camp) or 0 end)
end
local oUuidNum = 0
if DataCenter and DataCenter.OverlordManager and FormationSetting and FormationSetting.LandingOperation then
  local okO, rawO = pcall(function() return DataCenter.OverlordManager:GetSettingUUID(FormationSetting.LandingOperation, camp) end)
  if okO and rawO then oUuidNum = tonumber(rawO) or 0 end
end
local canQuick = (lo.IsCanQuickFight and _safe_call(function() return lo:IsCanQuickFight() end, false)) and true or false

local okSend, errSend = pcall(function()
  if lo.SetSelectCamp then lo:SetSelectCamp(camp) end
  if lo.SendTargetChapter and targetCh > 0 and curCh <= 0 then
    pcall(function() lo:SendTargetChapter(camp, targetCh) end)
  end
  if lo.SendSetHeroBattleArmy then
    pcall(function() lo:SendSetHeroBattleArmy(loHeroes, loArmyMap) end)
  end
  lo:SendHeroBattlePve({
    camp = camp,
    level = chosenTrigId,
    trigger = chosenFirstTrig,
    heroes = loHeroes,
    army = loArmyMap,
    formations = loHeroes,
    isQuickFight = canQuick,
    chipFormationId = chipFid,
    overlordUuid = oUuidNum,
  })
end)

out.sent = okSend
out.send_err = errSend and tostring(errSend) or nil
out.prev_ch = targetCh
out.prev_camp_ch = campCh
out.prev_lvl = curCampLvl
out.prev_camp_lvl = curCampLvl
out.prev_unlock_lev = curUnlockLev
out.target_ch = targetCh
out.target_lvl_idx = chosenLvlIdx
out.trig_lvl_id = chosenTrigId
out.first_trig = chosenFirstTrig
out.is_quick_fight = canQuick
out.troop_cap = cap
out.our_power = ourTotalPower
out.enemy_power = enemyPower
out.win_rate_est = enemyPower > 0 and math.min(1.0, ourTotalPower / enemyPower) or 1.0
return _enc(out)
"""
                sent_res = _eval_json(cd, pid, step_lua, timeout=8.0)
                if not sent_res.get("ok") or not sent_res.get("sent"):
                    f_rep["stopped_reason"] = sent_res.get("reason") or sent_res.get("send_err") or sent_res.get("error") or "send_failed"
                    if sent_res.get("in_game_tips"):
                        f_rep["tips"] = sent_res["in_game_tips"]
                    break

                battle_quick = bool(use_quick_deploy and (sent_res.get("is_quick_fight") or prefill))
                if battle_quick:
                    quick_deploys += 1

                battle_skipped = False
                if auto_skip_battle and not sent_res.get("is_quick_fight"):
                    skip_res = _skip_active_pve_after_delay(cd, pid, delay_sec=0.55)
                    if skip_res.get("skipped"):
                        battle_skipped = True
                        skips_triggered += 1

                prev_camp_lvl = int(sent_res.get("prev_camp_lvl") or sent_res.get("prev_lvl") or 0)
                prev_camp_ch = int(sent_res.get("prev_camp_ch") or sent_res.get("prev_ch") or 0)
                prev_unlock = int(sent_res.get("prev_unlock_lev") or 0)
                chk: dict[str, Any] = {}
                poll_deadline = time.time() + (3.0 if sent_res.get("is_quick_fight") else 6.5)
                while True:
                    time.sleep(0.45)
                    check_lua = (
                        f"local camp = {camp}\n"
                        f"local trySkip = {'true' if (auto_skip_battle and not battle_skipped) else 'false'}\n"
                        + _lua_trigger_pve_skip_snippet()
                        + r"""
local out = { ok = true, skipped_now = false, skip_method = 'none' }
if trySkip then
  local sk, how = _trigger_active_pve_skip()
  if sk then
    out.skipped_now = true
    out.skip_method = tostring(how or 'skip')
  end
end
local lo = DataCenter and DataCenter.LandingOperationsDataManager
out.cur_ch = tonumber(lo.data:GetTargetChapter(camp) or 0) or 0
out.cur_camp_ch = tonumber(lo.data.GetCampChapter and lo.data:GetCampChapter(camp) or 0) or 0
out.cur_lvl = tonumber(lo.data:GetCampLevel(camp) or 0) or 0
out.cur_unlock_lev = lo and lo.data and lo.data.curUnlockLev and lo.data.curUnlockLev[camp] or 0
out.failed_this_period = (lo.IsCampFailedThisPeriod and lo:IsCampFailedThisPeriod(camp)) and true or false
out.can_fight = (lo.IsCampCanFight and lo:IsCampCanFight(camp)) and true or false
local bl = DataCenter and DataCenter.BattleLevel
out.in_bl = (bl and bl.IsInBattleLevel and bl:IsInBattleLevel()) and true or false
return _enc(out)
"""
                    )
                    chk = _eval_json(cd, pid, check_lua, timeout=6.0)
                    if chk.get("skipped_now") and not battle_skipped:
                        battle_skipped = True
                        skips_triggered += 1
                    cur_l = int(chk.get("cur_lvl") or 0)
                    cur_u = int(chk.get("cur_unlock_lev") or 0)
                    cur_cc = int(chk.get("cur_camp_ch") or 0)
                    if cur_l > prev_camp_lvl or cur_u > prev_unlock or cur_cc > prev_camp_ch or chk.get("failed_this_period"):
                        break
                    if not chk.get("in_bl") and time.time() + 1.0 < poll_deadline:
                        # Settled in non-battle or quick-fight completed
                        break
                    if time.time() >= poll_deadline:
                        break

                if not sent_res.get("is_quick_fight"):
                    _ensure_exited_pve_cleanly(cd, pid)

                new_camp_lvl = int(chk.get("cur_lvl") or 0)
                new_unlock = int(chk.get("cur_unlock_lev") or 0)
                new_camp_ch = int(chk.get("cur_camp_ch") or 0)
                advanced = (new_camp_lvl > prev_camp_lvl) or (new_unlock > prev_unlock) or (new_camp_ch > prev_camp_ch)
                failed_now = bool(chk.get("failed_this_period")) or not advanced
                combined_tips = (sent_res.get("in_game_tips") or []) + (chk.get("in_game_tips") or [])

                f_rep["end_chapter"] = max(int(chk.get("cur_ch") or 0), new_camp_ch)
                f_rep["end_level"] = new_camp_lvl
                f_rep["quick_fight_unlocked"] = bool(sent_res.get("is_quick_fight"))
                f_rep["battles"].append({
                    "chapter": sent_res.get("target_ch"),
                    "level_idx": sent_res.get("target_lvl_idx"),
                    "trig_lvl_id": sent_res.get("trig_lvl_id"),
                    "our_power": sent_res.get("our_power"),
                    "enemy_power": sent_res.get("enemy_power"),
                    "win_rate_est": sent_res.get("win_rate_est"),
                    "won": advanced,
                    "failed": failed_now,
                    "skipped": battle_skipped,
                    "quick_deploy": battle_quick,
                    "tips": combined_tips,
                })
                if advanced:
                    f_rep["wins"] += 1
                    total_wins += 1
                else:
                    total_failures += 1
                    f_rep["stopped_reason"] = "defeat_or_blocked" if not chk.get("failed_this_period") else "defeat_period_failed"
                    if stop_on_fail:
                        break

            if not f_rep["stopped_reason"]:
                f_rep["stopped_reason"] = "max_battles_reached"
            faction_results[c_key] = f_rep
    finally:
        # Guarantee full restoration of F1 gear and original hero loadouts
        if not dry_run:
            restore_formations_and_gear(cd, pid)

    all_tips: list[str] = []
    for f_rep in faction_results.values():
        for t in f_rep.get("tips") or []:
            all_tips.append(str(t))
        for b in f_rep.get("battles") or []:
            for t in b.get("tips") or []:
                all_tips.append(str(t))
    all_tips = _clean_in_game_tips(all_tips)

    return {
        "ok": True,
        "dry_run": dry_run,
        "event_open": True,
        "total_wins": total_wins,
        "total_failures": total_failures,
        "quick_deploys": quick_deploys,
        "skips_triggered": skips_triggered,
        "factions": faction_results,
        "in_game_tips": all_tips,
    }


def _arena_round_win_prob(my_pwr: float, opp_pwr: float) -> float:
    """Estimate single-squad PvP win probability from combat powers."""
    if opp_pwr <= 0:
        return 0.99
    if my_pwr <= 0:
        return 0.0
    ratio = max(1e-9, float(opp_pwr) / float(my_pwr))
    return 1.0 / (1.0 + (ratio ** 6.5))


def _arena_best_matchup(
    is_3v3: bool,
    pure_camps: dict[str, Any],
    opp: dict[str, Any],
) -> dict[str, Any]:
    """Select optimal pure-faction slot order against an opponent and compute win odds."""
    active_camps = [
        c for c, info in sorted(
            pure_camps.items(),
            key=lambda kv: float((kv[1] or {}).get("base_power") or 0),
            reverse=True,
        )
        if int((info or {}).get("hero_count") or 0) > 0 and float((info or {}).get("base_power") or 0) > 0
    ]
    if not active_camps:
        return {"win_odds": 0.0, "slot_camps": [], "round_odds": []}

    if not is_3v3:
        best_c = active_camps[0]
        sp = (pure_camps[best_c].get("slot_powers") or {}).get("1") or pure_camps[best_c].get("base_power") or 0
        p = _arena_round_win_prob(float(sp), float(opp.get("power") or 0))
        return {
            "win_odds": p,
            "slot_camps": [int(best_c)],
            "round_odds": [round(p * 100.0, 2)],
            "my_total_power": int(sp),
        }

    batches = [float(b.get("power") or 0) for b in (opp.get("batches") or [])[:3]]
    if len(batches) == 3 and len(active_camps) >= 3:
        best_res: dict[str, Any] | None = None
        for perm in itertools.permutations(active_camps[:3], 3):
            p_rounds: list[float] = []
            s_pwrs: list[float] = []
            for slot_idx, c_key in enumerate(perm, start=1):
                sp = float((pure_camps[c_key].get("slot_powers") or {}).get(str(slot_idx)) or pure_camps[c_key].get("base_power") or 0)
                s_pwrs.append(sp)
                p_rounds.append(_arena_round_win_prob(sp, batches[slot_idx - 1]))
            p1, p2, p3 = p_rounds
            p_match = (p1 * p2 * (1.0 - p3)) + (p1 * (1.0 - p2) * p3) + ((1.0 - p1) * p2 * p3) + (p1 * p2 * p3)
            margin = sum(s_pwrs[i] - batches[i] for i in range(3))
            if (
                best_res is None
                or p_match > best_res["win_odds"] + 1e-6
                or (abs(p_match - best_res["win_odds"]) <= 1e-6 and margin > best_res["_margin"])
            ):
                best_res = {
                    "win_odds": p_match,
                    "slot_camps": [int(c) for c in perm],
                    "round_odds": [round(p * 100.0, 2) for p in p_rounds],
                    "my_total_power": int(sum(s_pwrs)),
                    "_margin": margin,
                }
        assert best_res is not None
        best_res.pop("_margin", None)
        return best_res

    slot_camps = [int(c) for c in active_camps[:3]]
    my_total = sum(
        float((pure_camps[str(c)].get("slot_powers") or {}).get(str(idx)) or pure_camps[str(c)].get("base_power") or 0)
        for idx, c in enumerate(slot_camps, start=1)
    )
    p = _arena_round_win_prob(my_total, float(opp.get("power") or 0))
    return {
        "win_odds": p,
        "slot_camps": slot_camps,
        "round_odds": [round(p * 100.0, 2)],
        "my_total_power": int(my_total),
    }


def run_arena(
    cd: Any,
    pid: int,
    snapshot: dict[str, Any],
    ccfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run daily Arena battles (auto-detects 1v1 vs 3v3, pure faction top-5 teams, >win-odds filter)."""
    acfg = ccfg.get("arena") or {}
    max_battles = max(1, min(10, int(acfg.get("max_battles_per_cycle", 5))))
    refresh_opps = bool(acfg.get("refresh_opponents", True))
    auto_free_refresh = bool(acfg.get("auto_free_refresh", True))
    pick_weakest = bool(acfg.get("pick_weakest", True))
    min_win_odds = max(0.50, min(0.99, float(acfg.get("min_win_odds_pct", 70)) / 100.0))

    def _sync_info() -> None:
        _eval_json(
            cd,
            pid,
            r"""
if SFSNetwork and MsgDefines then
  if MsgDefines.GetArenaInfo then
    pcall(function() SFSNetwork.SendMessage(MsgDefines.GetArenaInfo, 1) end)
  end
  if MsgDefines.GetCrossArenaInfo then
    pcall(function() SFSNetwork.SendMessage(MsgDefines.GetCrossArenaInfo, 1) end)
  end
end
return _enc({ ok = true })
""",
            timeout=5.0,
        )
        time.sleep(0.75)

    def _poll_arena() -> dict[str, Any]:
        return _eval_json(
            cd,
            pid,
            r"""
local out = { ok = true, closed = false, opponents = {}, pure_camps = {}, is_cross = false }
local cam = DataCenter and DataCenter.CrossArenaManager
local am = DataCenter and DataCenter.ArenaManager
local useCross = false
if cam then
  local canCross = (cam.GetCanJoinAct and _safe_call(function() return cam:GetCanJoinAct() end, false)) and true or false
  local crossHasCh = type(cam.challengeList) == "table" and next(cam.challengeList) ~= nil
  local regHasCh = am and type(am.challengeList) == "table" and next(am.challengeList) ~= nil
  if canCross or (crossHasCh and not regHasCh) then
    useCross = true
    am = cam
  end
end
if not am then
  out.reason = "arena_manager_unavailable"; return _enc(out)
end
out.is_cross = useCross
local is3v3 = ((am.GetIs3V3 and am:GetIs3V3()) or am.batch == true) and true or false
out.is_3v3 = is3v3
out.closed = ((am.CheckTemporarilyClosed and am:CheckTemporarilyClosed()) or (am.CheckIfIsSubmiting and am:CheckIfIsSubmiting())) and true or false
local si = am.selfInfo or {}
out.self_info = {
  fightTimes = tonumber(si.fightTimes or 0) or 0,
  buyTimes = tonumber(si.buyTimes or 0) or 0,
  selfPower = tonumber(si.selfPower or 0) or 0,
  selfRank = tonumber(si.selfRank or 0) or 0,
  selfScore = tonumber(si.selfScore or 0) or 0,
  dailyRefreshTimes = tonumber(si.dailyRefreshTimes or am.dailyRefreshTimes or 0) or 0,
}
out.free_remaining = math.max(0, 5 + out.self_info.buyTimes - out.self_info.fightTimes)

local hd = DataCenter and DataCenter.HeroDataManager
local bl = DataCenter and DataCenter.BattleLevel
local buffDict = (bl and bl.GetBuffEffectDict) and bl:GetBuffEffectDict() or {}
local fsKey = is3v3 and (FormationSetting and FormationSetting.Arena3V3Defense) or (FormationSetting and FormationSetting.Arena)

for camp = 1, 3 do
  local list = {}
  if hd and hd.GetAllHeroList then
    for _, h in pairs(hd:GetAllHeroList()) do
      if type(h) == "table" and h.uuid and tonumber(h.camp or 0) == camp then
        table.insert(list, h)
      end
    end
  end
  table.sort(list, function(a, b)
    local pa = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(a)) or 0
    local pb = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(b)) or 0
    return pa > pb
  end)
  local uuids, heroesP, heroSummary = {}, {}, {}
  for i = 1, math.min(5, #list) do
    local h = list[i]
    table.insert(uuids, h.uuid)
    heroesP[h.uuid] = h
    table.insert(heroSummary, { id = h.heroId, power = (HeroUtils and HeroUtils.GetHeroPower(h)) or 0 })
  end
  local slotPowers = {}
  local maxSlots = is3v3 and 3 or 1
  for slotIdx = 1, maxSlots do
    local pwr = 0
    if #uuids > 0 and MarchUtil and MarchUtil.GetArmys and MarchUtil.GetFormationPower then
      local chipId = (CarChipManager and CarChipManager.GetSetting and fsKey) and (tonumber(CarChipManager:GetSetting(fsKey, is3v3 and slotIdx or nil) or 0) or 0) or (is3v3 and slotIdx or 0)
      local olUuid = (OverlordManager and OverlordManager.GetSettingUUID and fsKey) and (tonumber(OverlordManager:GetSettingUUID(fsKey, is3v3 and slotIdx or nil) or 0) or 0) or 0
      local soldiers = MarchUtil:GetArmys(uuids, olUuid) or {}
      local campParam = (MarchUtil.GetCampAddParam and MarchUtil.GetCampAddParam(heroesP)) or 0
      local rawPwr = MarchUtil.GetFormationPower(heroesP, soldiers, 1, campParam, buffDict, false, true, false, chipId, olUuid) or 0
      pwr = math.ceil(tonumber(rawPwr) or 0)
    end
    slotPowers[tostring(slotIdx)] = pwr
  end
  local basePwr = slotPowers["1"] or 0
  out.pure_camps[tostring(camp)] = {
    camp = camp,
    hero_count = #uuids,
    heroes = heroSummary,
    base_power = basePwr,
    slot_powers = slotPowers,
  }
end

if type(am.challengeList) == "table" then
  for _, c in pairs(am.challengeList) do
    if type(c) == "table" and (c.uid ~= nil or c.armyId ~= nil) then
      local batches = {}
      if type(c.armyBatch) == "table" then
        for bi, ab in ipairs(c.armyBatch) do
          table.insert(batches, { idx = bi, power = tonumber(ab.power or 0) or 0 })
        end
      end
      local cType = tonumber(c.type)
      if cType == nil then cType = 1 end
      local cUid = tostring(c.uid or "")
      local cArmyId = tostring(c.armyId or "")
      local targetId = (cType == 0 or cUid == "") and (cArmyId ~= "" and cArmyId or cUid) or cUid
      table.insert(out.opponents, {
        uid = targetId,
        raw_uid = cUid,
        army_id = cArmyId,
        name = tostring(c.name or ""),
        type = cType,
        power = tonumber(c.power or 0) or 0,
        rank = tonumber(c.rank or 0) or 0,
        score = tonumber(c.score or 0) or 0,
        batches = batches,
      })
    end
  end
end
return _enc(out)
""",
            timeout=6.0,
        )

    if refresh_opps:
        _sync_info()

    st = _poll_arena()
    if not st.get("ok"):
        return st
    if st.get("closed"):
        st["dry_run"] = dry_run
        st["reason"] = "arena_temporarily_closed"
        return st

    free_rem = int(st.get("free_remaining") or 0)
    to_fight = min(max_battles, free_rem)
    if to_fight <= 0:
        return {
            "ok": True,
            "dry_run": dry_run,
            "mode": "3v3" if st.get("is_3v3") else "1v1",
            "is_cross": bool(st.get("is_cross")),
            "self_info": st.get("self_info"),
            "free_remaining": free_rem,
            "battles_fought": 0,
            "reason": "no_free_arena_attempts_remaining",
        }

    def _pick_target(cur_st: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        is3 = bool(cur_st.get("is_3v3"))
        camps = cur_st.get("pure_camps") or {}
        scored: list[dict[str, Any]] = []
        for opp in cur_st.get("opponents") or []:
            plan = _arena_best_matchup(is3, camps, opp)
            scored.append({
                "opp": opp,
                "plan": plan,
                "win_odds": float(plan.get("win_odds") or 0.0),
                "win_odds_pct": round(float(plan.get("win_odds") or 0.0) * 100.0, 2),
            })
        viable = [s for s in scored if s["win_odds"] >= min_win_odds]
        if not viable:
            return None, scored
        if pick_weakest:
            viable.sort(key=lambda s: (-s["win_odds"], float(s["opp"].get("power") or 0)))
        else:
            viable.sort(key=lambda s: (-int(s["opp"].get("score") or 0), -s["win_odds"]))
        return viable[0], scored

    if dry_run:
        picked, scored = _pick_target(st)
        best_any = max(scored, key=lambda s: s["win_odds"], default=None)
        return {
            "ok": True,
            "dry_run": True,
            "mode": "3v3" if st.get("is_3v3") else "1v1",
            "is_cross": bool(st.get("is_cross")),
            "min_win_odds_pct": round(min_win_odds * 100.0, 1),
            "self_info": st.get("self_info"),
            "free_remaining": free_rem,
            "planned_battles": to_fight,
            "pure_factions": st.get("pure_camps"),
            "selected_candidate": (
                {
                    "uid": picked["opp"]["uid"],
                    "name": picked["opp"]["name"],
                    "power": picked["opp"]["power"],
                    "rank": picked["opp"]["rank"],
                    "win_odds_pct": picked["win_odds_pct"],
                    "slot_camps": picked["plan"]["slot_camps"],
                    "round_odds_pct": picked["plan"]["round_odds"],
                }
                if picked else None
            ),
            "best_available_odds_pct": best_any["win_odds_pct"] if best_any else 0.0,
        }

    battles_log: list[dict[str, Any]] = []
    stopped_reason: str | None = None
    free_refreshes_used = 0
    cur_st = st

    for idx_b in range(to_fight):
        if idx_b > 0:
            _sync_info()
            cur_st = _poll_arena()
            if not cur_st.get("ok"):
                stopped_reason = cur_st.get("error") or "poll_failed"
                break
            if int(cur_st.get("free_remaining") or 0) <= 0:
                stopped_reason = "no_free_arena_attempts_remaining"
                break

        picked, scored = _pick_target(cur_st)
        while picked is None and auto_free_refresh and free_refreshes_used < 2:
            free_refreshes_used += 1
            is_cross_cur = bool(cur_st.get("is_cross"))
            _eval_json(
                cd,
                pid,
                f"local isCross = {'true' if is_cross_cur else 'false'}\n" + r"""
if SFSNetwork and MsgDefines then
  local refMsg = isCross and MsgDefines.RefreshCrossArenaChallenge or MsgDefines.RefreshArenaChallenge
  if refMsg then
    pcall(function() SFSNetwork.SendMessage(refMsg, false) end)
  end
end
return _enc({ ok = true })
""",
                timeout=5.0,
            )
            time.sleep(0.8)
            _sync_info()
            cur_st = _poll_arena()
            picked, scored = _pick_target(cur_st)

        if picked is None:
            best_any = max(scored, key=lambda s: s["win_odds"], default=None)
            stopped_reason = f"no_opponent_above_win_odds_{int(min_win_odds * 100)}pct"
            if best_any:
                battles_log.append({
                    "skipped_reason": stopped_reason,
                    "best_candidate": {
                        "uid": best_any["opp"]["uid"],
                        "name": best_any["opp"]["name"],
                        "power": best_any["opp"]["power"],
                        "win_odds_pct": best_any["win_odds_pct"],
                    },
                })
            break

        tgt_opp = picked["opp"]
        slot_camps = picked["plan"]["slot_camps"]
        is3 = bool(cur_st.get("is_3v3"))
        is_cross_cur = bool(cur_st.get("is_cross"))
        slot_camps_lua = "{" + ",".join(str(int(c)) for c in slot_camps) + "}"
        opp_type_val = int(tgt_opp["type"]) if tgt_opp.get("type") is not None else 1

        atk_lua = (
            f"local targetUid = {json.dumps(str(tgt_opp['uid']))}\n"
            f"local targetType = {opp_type_val}\n"
            f"local targetRank = {int(tgt_opp.get('rank') or 0)}\n"
            f"local targetScore = {int(tgt_opp.get('score') or 0)}\n"
            f"local is3v3 = {'true' if is3 else 'false'}\n"
            f"local isCross = {'true' if is_cross_cur else 'false'}\n"
            f"local slotCamps = {slot_camps_lua}\n"
        ) + r"""
local out = { ok = true, sent = false, reason = "" }
local am = isCross and (DataCenter and DataCenter.CrossArenaManager) or (DataCenter and DataCenter.ArenaManager)
if not am or not am.selfInfo then
  out.reason = "arena_missing"; return _enc(out)
end
-- Populate am.cacheTargetInfo before StartArenaBattle so BaseArenaManager:CacheTargetRankChange never indexes nil
local matchedTarget = nil
if type(am.challengeList) == "table" then
  for _, c in pairs(am.challengeList) do
    if type(c) == "table" and (tostring(c.uid or "") == targetUid or tostring(c.armyId or "") == targetUid) then
      matchedTarget = c
      break
    end
  end
end
if matchedTarget and am.SetCacheTargetInfo then
  pcall(function() am:SetCacheTargetInfo(matchedTarget) end)
end
if not am.cacheTargetInfo then
  am.cacheTargetInfo = matchedTarget or { uid = targetUid, rank = targetRank, score = targetScore }
end
local prevFight = tonumber(am.selfInfo.fightTimes or 0) or 0
local hd = DataCenter and DataCenter.HeroDataManager
local bl = DataCenter and DataCenter.BattleLevel
local buffDict = (bl and bl.GetBuffEffectDict) and bl:GetBuffEffectDict() or {}

local function build_pure_camp(campId, fsKey, slotIdx)
  local list = {}
  if hd and hd.GetAllHeroList then
    for _, h in pairs(hd:GetAllHeroList()) do
      if type(h) == "table" and h.uuid and tonumber(h.camp or 0) == campId then
        table.insert(list, h)
      end
    end
  end
  table.sort(list, function(a, b)
    local pa = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(a)) or 0
    local pb = (HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(b)) or 0
    return pa > pb
  end)
  local topObjs, uuids, heroesP, heroesIdx = {}, {}, {}, {}
  for i = 1, math.min(5, #list) do
    local h = list[i]
    table.insert(topObjs, h)
    table.insert(uuids, h.uuid)
    heroesP[h.uuid] = h
    table.insert(heroesIdx, { index = i, uuid = h.uuid })
  end
  if #topObjs == 0 then return nil end
  local chipId = (CarChipManager and CarChipManager.GetSetting and fsKey) and (tonumber(CarChipManager:GetSetting(fsKey, slotIdx) or 0) or 0) or (slotIdx or 0)
  local olUuid = (OverlordManager and OverlordManager.GetSettingUUID and fsKey) and (tonumber(OverlordManager:GetSettingUUID(fsKey, slotIdx) or 0) or 0) or 0
  local soldiers = (MarchUtil and MarchUtil.GetArmys) and MarchUtil:GetArmys(uuids, olUuid) or {}
  local useArmyId = 0
  for k, v in pairs(soldiers) do
    if (tonumber(v) or 0) > 0 then useArmyId = tonumber(k) or 0; break end
  end
  if useArmyId == 0 then
    for k, _ in pairs(soldiers) do useArmyId = tonumber(k) or 0; break end
  end
  local campParam = (MarchUtil and MarchUtil.GetCampAddParam) and MarchUtil.GetCampAddParam(heroesP) or 0
  local rawPwr = (MarchUtil and MarchUtil.GetFormationPower) and MarchUtil.GetFormationPower(heroesP, soldiers, 1, campParam, buffDict, false, true, false, chipId, olUuid) or 0
  return {
    topObjs = topObjs,
    heroesIdx = heroesIdx,
    power = math.ceil(tonumber(rawPwr) or 0),
    useArmyId = useArmyId,
    chipFormationId = chipId,
    overlordUuid = olUuid,
  }
end

if is3v3 then
  am.isSendStart3V3Battle = false
  local fsKey = FormationSetting and FormationSetting.Arena3V3Defense
  local formations = {}
  for sIdx, campId in ipairs(slotCamps) do
    local squad = build_pure_camp(campId, fsKey, sIdx)
    if squad then
      table.insert(formations, {
        index = sIdx,
        heroes = squad.heroesIdx,
        power = squad.power,
        useArmyId = squad.useArmyId,
        chipFormationId = squad.chipFormationId,
        overlordUuid = squad.overlordUuid,
      })
    end
  end
  if #formations == 0 then
    out.reason = "no_3v3_heroes"; return _enc(out)
  end
  local msg3v3 = isCross and MsgDefines.StartCrossArena3V3Battle or MsgDefines.StartArena3V3Battle
  local okS, errS = pcall(function()
    SFSNetwork.SendMessage(msg3v3, targetUid, targetType, formations)
  end)
  out.sent = okS
  out.send_err = errS and tostring(errS) or nil
else
  local fsKey = FormationSetting and FormationSetting.Arena
  local campId = slotCamps[1] or 1
  local squad = build_pure_camp(campId, fsKey, nil)
  if not squad then
    out.reason = "no_heroes_owned"; return _enc(out)
  end
  local aid = squad.useArmyId
  if aid == 0 then
    local tcm = DataCenter and DataCenter.TowerClimbingManager
    if tcm and tcm.GetSelfArmys then
      for k, _ in pairs(tcm:GetSelfArmys(1) or {}) do
        local val = tonumber(k) or 0
        if val > aid then aid = val end
      end
    end
  end
  local msg1v1 = isCross and MsgDefines.StartCrossArenaBattle or MsgDefines.StartArenaBattle
  local okS, errS = pcall(function()
    SFSNetwork.SendMessage(
      msg1v1,
      targetUid,
      targetType,
      squad.heroesIdx,
      squad.power,
      aid,
      squad.chipFormationId,
      squad.overlordUuid
    )
  end)
  out.sent = okS
  out.send_err = errS and tostring(errS) or nil
end

out.prev_fight_times = prevFight
out.prev_score = tonumber(am.selfInfo.selfScore or 0) or 0
out.prev_rank = tonumber(am.selfInfo.selfRank or 0) or 0
return _enc(out)
"""
        sent = _eval_json(cd, pid, atk_lua, timeout=6.0)
        if not sent.get("sent"):
            stopped_reason = sent.get("reason") or sent.get("send_err") or sent.get("error") or "send_failed"
            break

        time.sleep(1.4)
        res_poll = _eval_json(
            cd,
            pid,
            f"local isCross = {'true' if is_cross_cur else 'false'}\n" + r"""
local out = { ok = true }
local am = isCross and (DataCenter and DataCenter.CrossArenaManager) or (DataCenter and DataCenter.ArenaManager)
if am then am.isSendStart3V3Battle = false end
out.fight_times = tonumber(am and am.selfInfo and am.selfInfo.fightTimes or 0) or 0
out.rank_after = tonumber(am and am.selfInfo and am.selfInfo.selfRank or 0) or 0
out.score_after = tonumber(am and am.selfInfo and am.selfInfo.selfScore or 0) or 0
out.closed = ((am and am.CheckTemporarilyClosed and am:CheckTemporarilyClosed()) or (am and am.CheckIfIsSubmiting and am:CheckIfIsSubmiting())) and true or false
if am and am.round3V3Data then
  out.match_won = (am.round3V3Data.win == true)
  local w, l = 0, 0
  if type(am.round3V3Data.roundData) == "table" then
    for _, rd in ipairs(am.round3V3Data.roundData) do
      if (tonumber(rd.otherAfterHealth or 0) or 0) <= 0 and (tonumber(rd.selfAfterHealth or 0) or 0) > 0 then
        w = w + 1
      else
        l = l + 1
      end
    end
  end
  out.rounds_won = w
  out.rounds_lost = l
end
return _enc(out)
""",
            timeout=5.0,
        )
        tips = (sent.get("in_game_tips") or []) + (res_poll.get("in_game_tips") or [])
        prev_ft = int(sent.get("prev_fight_times") or 0)
        prev_score = int(sent.get("prev_score") or 0)
        prev_rank = int(sent.get("prev_rank") or 0)
        new_ft = int(res_poll.get("fight_times") or 0)
        new_score = int(res_poll.get("score_after") or 0)
        new_rank = int(res_poll.get("rank_after") or 0)
        accepted = (new_ft > prev_ft) or (new_score != prev_score and new_score > 0) or (new_rank > 0 and new_rank != prev_rank)
        b_entry: dict[str, Any] = {
            "mode": "3v3" if is3 else "1v1",
            "is_cross": is_cross_cur,
            "target": {
                "uid": tgt_opp["uid"],
                "name": tgt_opp["name"],
                "power": tgt_opp["power"],
                "rank": tgt_opp["rank"],
            },
            "win_odds_pct": picked["win_odds_pct"],
            "slot_camps": slot_camps,
            "round_odds_pct": picked["plan"]["round_odds"],
            "fight_times_after": new_ft,
            "rank_after": new_rank,
            "score_after": new_score,
            "accepted": accepted,
            "tips": tips,
        }
        if "match_won" in res_poll:
            b_entry["match_won"] = res_poll["match_won"]
            b_entry["rounds_won"] = res_poll["rounds_won"]
            b_entry["rounds_lost"] = res_poll["rounds_lost"]
        battles_log.append(b_entry)

        if any("302236" in str(t) for t in tips) or res_poll.get("closed"):
            stopped_reason = "arena_reward_tallying_or_closed"
            break
        has_error_tip = any(
            any(w in str(t).lower() for w in ("error", "fail", "not enough", "insufficient", "limit"))
            for t in tips
        )
        if not accepted and has_error_tip:
            stopped_reason = f"server_rejected_tips_{tips[0]}"
            break
        time.sleep(0.5)

    return {
        "ok": True,
        "dry_run": False,
        "mode": "3v3" if st.get("is_3v3") else "1v1",
        "min_win_odds_pct": round(min_win_odds * 100.0, 1),
        "free_refreshes_used": free_refreshes_used,
        "self_info": st.get("self_info"),
        "battles_fought": sum(1 for b in battles_log if b.get("accepted")),
        "battles": battles_log,
        "stopped_reason": stopped_reason or "completed",
    }


def run_area_exploration(
    cd: Any,
    pid: int,
    snapshot: dict[str, Any],
    ccfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Claim Exploration idle chest, execute available Batch Jump, and auto-battle solo stages until fail."""
    ecfg = ccfg.get("area_exploration") or {}
    claim_hangup = bool(ecfg.get("claim_hangup_rewards", True))
    auto_jump = bool(ecfg.get("auto_jump", True))
    auto_battle = bool(ecfg.get("auto_battle", True))
    auto_skip = bool(ecfg.get("auto_skip_battle", True))
    max_battles = max(1, min(20, int(ecfg.get("max_battles_per_cycle", 5))))
    stop_on_fail = bool(ecfg.get("stop_on_fail", True))
    skip_failed_same_power = bool(ecfg.get("skip_already_failed_same_power", True))

    prep_lua = (
        f"local dryRun = {'true' if dry_run else 'false'}\n"
        f"local claimHangup = {'true' if claim_hangup else 'false'}\n"
        f"local autoJump = {'true' if auto_jump else 'false'}\n"
    ) + r"""
local out = { ok = true, dry_run = dryRun, hangup_claimed = false }
local tcm = DataCenter and DataCenter.TowerClimbingManager
local sm = DataCenter and DataCenter.StoryManager
if not tcm then
  out.reason = "tower_climbing_unavailable"; return _enc(out)
end

out.order = tonumber(tcm:GetOrder() or 0) or 0
out.next_id = tonumber(tcm:GetNextLevelId() or 0) or 0
out.is_max = (tcm.IsMaxLevel and tcm:IsMaxLevel()) and true or false
out.monster_power = (out.next_id > 0 and tcm.GetMonsterLevelPower and tonumber(tcm:GetMonsterLevelPower(out.next_id) or 0)) or 0

if sm then
  local nowMs = (TimeUtil and TimeUtil.GetServerTimeMs and TimeUtil.GetServerTimeMs()) or (os.time() * 1000)
  local startMs = tonumber(sm.GetHangupTime and sm:GetHangupTime() or nowMs) or nowMs
  local minMs = tonumber(sm.GetMinHangupTime and sm:GetMinHangupTime() or 300000) or 300000
  local elapsedMs = math.max(0, nowMs - startMs)
  out.hangup_elapsed_ms = elapsedMs
  out.hangup_eligible = elapsedMs >= minMs
  if claimHangup and out.hangup_eligible then
    if not dryRun and sm.SendReceiveHangupReward then
      pcall(function() sm:SendReceiveHangupReward() end)
    end
    out.hangup_claimed = true
  end
end

local okJ, _, jCnt, lastOrd, heroes, forms, startOrd, pwr = pcall(function() return tcm:GetJumpLevel() end)
out.team_power = tonumber(okJ and pwr or 0) or 0
out.jump_available = {
  count = tonumber(okJ and jCnt or 0) or 0,
  from_order = tonumber(okJ and startOrd or 0) or 0,
  to_order = tonumber(okJ and lastOrd or 0) or 0,
}
out.jumped = false
if autoJump and okJ and (tonumber(jCnt or 0) or 0) > 0 and (tonumber(lastOrd or 0) or 0) > out.order then
  if not dryRun and MsgDefines and MsgDefines.UserStartBarrelPushBatch and SFSNetwork then
    pcall(function()
      SFSNetwork.SendMessage(MsgDefines.UserStartBarrelPushBatch, {
        ["until"] = tonumber(lastOrd),
        heroes = heroes,
        formations = forms,
        power = tonumber(pwr or 0),
      })
    end)
    out.jumped = true
  end
end
return _enc(out)
"""
    prep = _eval_json(cd, pid, prep_lua, timeout=8.0)
    if not prep.get("ok"):
        return prep
    initial_order = int(prep.get("order") or 0)
    prep["start_order"] = initial_order

    if prep.get("jumped"):
        time.sleep(1.3)
        post_j = _eval_json(
            cd,
            pid,
            r"""
local tcm = DataCenter and DataCenter.TowerClimbingManager
return _enc({
  ok = true,
  order = tonumber(tcm and tcm:GetOrder() or 0) or 0,
  next_id = tonumber(tcm and tcm:GetNextLevelId() or 0) or 0,
})
""",
            timeout=5.0,
        )
        if post_j.get("ok"):
            prep["order_after_jump"] = post_j.get("order")
            prep["order"] = post_j.get("order", prep.get("order"))
            prep["next_id"] = post_j.get("next_id", prep.get("next_id"))

    if dry_run or not auto_battle or prep.get("is_max"):
        prep["end_order"] = int(prep.get("order") or initial_order)
        prep["battles"] = []
        prep["skips_triggered"] = 0
        prep["stopped_reason"] = "dry_run" if dry_run else ("max_level" if prep.get("is_max") else "auto_battle_disabled")
        return prep

    cur_order = int(prep.get("order") or 0)
    team_pwr = int(prep.get("team_power") or 0)
    if skip_failed_same_power and _EXPLORE_FAIL_CACHE.get((pid, cur_order), -1) >= team_pwr and team_pwr > 0:
        prep["end_order"] = cur_order
        prep["battles"] = []
        prep["skips_triggered"] = 0
        prep["stopped_reason"] = f"skipped_previously_failed_stage_{cur_order + 1}_at_power_{team_pwr}"
        return prep

    battles_log: list[dict[str, Any]] = []
    skips_triggered = 0
    stopped_reason: str | None = None

    def _cleanup_to_city() -> None:
        _ensure_exited_pve_cleanly(cd, pid)

    # Guard against re-entering if client is already stuck inside a PVE battle scene
    _ensure_exited_pve_cleanly(cd, pid, only_if_stuck=True)

    for _ in range(max_battles):
        enter_res = _eval_json(
            cd,
            pid,
            f"local autoSkip = {'true' if auto_skip else 'false'}\n"
            + r"""
local out = { ok = true, entered = false }
local tcm = DataCenter and DataCenter.TowerClimbingManager
if not tcm or (tcm.IsMaxLevel and tcm:IsMaxLevel()) then
  out.reason = "max_level"; return _enc(out)
end
out.start_order = tonumber(tcm:GetOrder() or 0) or 0
out.next_id = tonumber(tcm:GetNextLevelId() or 0) or 0
out.is_barrel = (tcm.CheckIsBarrel and tcm:CheckIsBarrel(out.next_id)) and true or false
out.monster_power = (tcm.GetMonsterLevelPower and tonumber(tcm:GetMonsterLevelPower(out.next_id) or 0)) or 0
local okJ, _, _, _, _, _, _, pwr = pcall(function() return tcm:GetJumpLevel() end)
out.team_power = tonumber(okJ and pwr or 0) or 0
if out.is_barrel and not autoSkip then
  out.reason = "barrel_minigame_stage_" .. tostring(out.start_order + 1)
  return _enc(out)
end

local mgr = UIManager and UIManager:GetInstance()
if not mgr then
  out.reason = "uimgr_unavailable"; return _enc(out)
end
mgr:OpenWindow("UIJeepAdventureMain")
local win = mgr:GetWindow("UIJeepAdventureMain")
if not win or not win.View or not win.View.BattleStart then
  out.reason = "jeep_view_missing"; return _enc(out)
end
local okB, errB = pcall(function() win.View:BattleStart() end)
out.entered = okB
out.enter_err = errB and tostring(errB) or nil
return _enc(out)
""",
            timeout=8.0,
        )
        if not enter_res.get("ok") or not enter_res.get("entered"):
            stopped_reason = enter_res.get("reason") or enter_res.get("enter_err") or enter_res.get("error") or "enter_failed"
            break

        time.sleep(1.3)
        start_order = int(enter_res.get("start_order") or 0)

        trig_res = _eval_json(
            cd,
            pid,
            f"local autoSkip = {'true' if auto_skip else 'false'}\n"
            f"local isBarrelStage = {'true' if enter_res.get('is_barrel') else 'false'}\n"
            + _lua_trigger_pve_skip_snippet()
            + r"""
local out = { ok = true, triggered = false, used_fast = false, skipped_now = false }
if isBarrelStage and autoSkip and DataCenter and DataCenter.LWBattleManager and DataCenter.LWBattleManager.Skip then
  local okSk = pcall(function() DataCenter.LWBattleManager:Skip() end)
  out.skipped_now = okSk
  out.triggered = okSk or (DataCenter.BattleLevel and DataCenter.BattleLevel:IsInBattleLevel()) or false
  return _enc(out)
end
local mgr = UIManager and UIManager:GetInstance()
local w = mgr and mgr:GetWindow("UIPVEScene")
if w and w.View then
  if w.View.finishOpen == true and w.View.OnFastCombatBtnClick then
    local okF = pcall(function() w.View:OnFastCombatBtnClick() end)
    out.used_fast = okF
    out.triggered = okF
  elseif w.View.OnRealStartPVE then
    local okS, errS = pcall(function() w.View:OnRealStartPVE(false) end)
    out.triggered = okS
    out.err = errS and tostring(errS) or nil
    -- Do NOT skip at t=0ms before PveActorMgr.startPlay==true (calling OnShowResult early poisons forceShowResultFlag!).
    -- The fast 0.4s poll loop immediately below triggers _trigger_active_pve_skip() the instant startPlay flips true.
  end
else
  -- Non-UIPVEScene barrel levels start automatically inside BattleLevel
  out.triggered = DataCenter and DataCenter.BattleLevel and DataCenter.BattleLevel:IsInBattleLevel() or false
  out.no_pve_scene = true
  if autoSkip and DataCenter and DataCenter.LWBattleManager and DataCenter.LWBattleManager.Skip and DataCenter.LWBattleManager.logic then
    local okSk = pcall(function() DataCenter.LWBattleManager:Skip() end)
    if okSk then out.skipped_now = true end
  end
end
return _enc(out)
""",
            timeout=8.0,
        )
        if not trig_res.get("triggered"):
            _cleanup_to_city()
            stopped_reason = trig_res.get("err") or "trigger_fight_failed"
            break

        battle_skipped = bool(trig_res.get("skipped_now") or trig_res.get("used_fast"))
        if battle_skipped:
            skips_triggered += 1

        outcome = "timeout"
        end_order = start_order
        deadline = time.time() + 28.0
        while time.time() < deadline:
            time.sleep(0.4)
            poll = _eval_json(
                cd,
                pid,
                f"local trySkip = {'true' if (auto_skip and not battle_skipped) else 'false'}\n"
                + _lua_trigger_pve_skip_snippet()
                + r"""
local out = { ok = true, skipped = false, skip_method = 'none' }
local tcm = DataCenter and DataCenter.TowerClimbingManager
out.order = tonumber(tcm and tcm:GetOrder() or 0) or 0
local mgr = UIManager and UIManager:GetInstance()
local hasWin = false
local hasLose = false
local loseWinName = nil
if mgr and mgr.windows then
  for k, w in pairs(mgr.windows) do
    local act = (type(w) == "table" and w.View and w.View.activeSelf) and true or false
    if act then
      local ks = tostring(k)
      if ks == "UIParkourBattleWin" or ks == "UIPveBattleWin" or ks == "UIPVEResult" then
        hasWin = true
      elseif ks:lower():find("lose") then
        hasLose = true
        loseWinName = ks
      end
    end
  end
end
out.win_open = hasWin
out.lose_open = hasLose
out.lose_win = loseWinName
if trySkip and not hasWin and not hasLose then
  local sk, how = _trigger_active_pve_skip()
  if sk then
    out.skipped = true
    out.skip_method = tostring(how or 'skip')
  else
    out.skip_method = tostring(how or 'waiting')
  end
end
local bl = DataCenter and DataCenter.BattleLevel
out.in_bl = (bl and bl.IsInBattleLevel and bl:IsInBattleLevel()) and true or false
out.in_home = (SceneManager and SceneManager:IsInHome()) and true or false
return _enc(out)
""",
                timeout=6.0,
            )
            if poll.get("skipped") and not battle_skipped:
                battle_skipped = True
                skips_triggered += 1
            if not poll.get("ok"):
                continue
            end_order = int(poll.get("order") or start_order)
            if poll.get("win_open") or end_order > start_order:
                # Wait briefly for UIParkourBattleWin so OnBtnBackClick exits cleanly if order incremented first
                if not poll.get("win_open") and poll.get("in_bl") and time.time() + 4.0 < deadline:
                    continue
                outcome = "won"
                break
            if poll.get("lose_open"):
                outcome = "lost"
                break
            if not poll.get("in_bl") and poll.get("in_home") and end_order == start_order:
                outcome = "lost"
                break

        _cleanup_to_city()
        time.sleep(0.5)

        battles_log.append({
            "stage": start_order + 1,
            "level_id": enter_res.get("next_id"),
            "monster_power": enter_res.get("monster_power"),
            "team_power": enter_res.get("team_power"),
            "outcome": outcome,
            "skipped": battle_skipped,
            "order_after": end_order,
        })

        if outcome != "won":
            if team_pwr > 0:
                _EXPLORE_FAIL_CACHE[(pid, start_order)] = int(enter_res.get("team_power") or team_pwr)
            stopped_reason = f"stage_{start_order + 1}_{outcome}"
            if stop_on_fail:
                break

    final_order = max(
        [
            int(initial_order),
            int(prep.get("order") or 0),
            int(prep.get("order_after_jump") or 0),
            *(int(b.get("order_after") or 0) for b in battles_log if isinstance(b, dict)),
        ]
    )
    prep["end_order"] = final_order
    prep["order_after_battles"] = final_order
    prep["battles"] = battles_log
    prep["wins"] = sum(1 for b in battles_log if b.get("outcome") == "won")
    prep["skips_triggered"] = skips_triggered
    prep["stopped_reason"] = stopped_reason or "max_battles_reached"
    return prep


_LUA_QUEUE_HELP_HELPER = r"""
local function _send_queue_alliance_help(qm, q)
  if type(q) ~= 'table' and type(q) ~= 'userdata' then return false end
  local qUuid = q.uuid
  if qUuid == nil or tostring(qUuid) == '' then return false end
  local helpType = (AllianceHelpType and AllianceHelpType.Queue) or 1
  local qType = math.tointeger(math.floor(tonumber(q.type or 0) or 0)) or 0
  local itemId = tostring(q.itemId or '')
  local ahdm = DataCenter and DataCenter.AllianceHelpDataManager
  if ahdm and ahdm.SendCallHelp then
    local ok = pcall(function() ahdm:SendCallHelp(qUuid, helpType, qType, itemId) end)
    if ok then return true end
  end
  if qm and qm.OnAllianceCallHelp then
    pcall(function() qm:OnAllianceCallHelp(qUuid) end)
  end
  if SFSNetwork and MsgDefines and MsgDefines.AllianceCallHelp then
    local ok = pcall(function()
      SFSNetwork.SendMessage(MsgDefines.AllianceCallHelp, qUuid, helpType, qType, itemId)
    end)
    return ok
  end
  return false
end

local function _collect_or_help_queue(qm, q, nowMs, dryRun, outCollectFlag, outHelpFlag)
  if (type(q) ~= 'table' and type(q) ~= 'userdata') or not q.uuid then return false end
  local qSt = tonumber(q.state or 0) or 0
  if q.GetQueueState then
    local ok, s = pcall(function() return tonumber(q:GetQueueState()) or qSt end)
    if ok and s then qSt = s end
  elseif qm and qm.GetQueueState then
    local ok, s = pcall(function() return tonumber(qm:GetQueueState(q)) or qSt end)
    if ok and s then qSt = s end
  end
  local finState = (NewQueueState and tonumber(NewQueueState.Finish)) or 3
  local workState = (NewQueueState and tonumber(NewQueueState.Work)) or 2
  local endMs = tonumber(q.endTime or 0) or 0
  if endMs > 0 and endMs < 1e12 then endMs = endMs * 1000 end
  local isFin = (qSt == finState) or (qSt == workState and endMs > 0 and nowMs > 0 and endMs <= nowMs)
  if not isFin and qm and qm.IsQueueTimeFinish then
    local ok, f = pcall(function() return qm:IsQueueTimeFinish(q) end)
    if ok and f and qSt ~= 0 then isFin = true end
  end
  if isFin then
    if not dryRun and SFSNetwork and MsgDefines and MsgDefines.QueueFinish then
      pcall(function() SFSNetwork.SendMessage(MsgDefines.QueueFinish, {uuid = q.uuid}) end)
    end
    if outCollectFlag then outCollectFlag(q) end
    return 'finished'
  end
  if qSt == workState and tonumber(q.isHelped or 0) == 0 then
    if not dryRun then
      _send_queue_alliance_help(qm, q)
    end
    if outHelpFlag then outHelpFlag(q) end
    return 'helped'
  end
  return (qSt == workState) and 'working' or 'free'
end
"""

_LUA_SERVER_TIME_HELPER = r"""
local function _get_server_weekday(nowSec)
  local sec = math.floor(tonumber(nowSec or 0) or 0)
  if sec <= 0 then sec = os.time() end
  local dt = os.date('*t', sec)
  local names = {'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'}
  local w = tonumber(dt and dt.wday or 0) or 0
  return w, names[w] or 'Unknown'
end
"""


def run_war_safety(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("war_safety") or {}
    auto_shield = bool(task_cfg.get("auto_shield_on_attack", True))
    respect_fever = bool(task_cfg.get("respect_war_fever", True))
    recall_gatherers = bool(task_cfg.get("recall_gatherers_on_attack", True))
    max_eta = int(task_cfg.get("max_eta_seconds", 300) or 300)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local autoShield = {str(auto_shield).lower()}
local respectFever = {str(respect_fever).lower()}
local recallGatherers = {str(recall_gatherers).lower()}
local maxEta = {max_eta}

local snap = _get_player_snapshot()
local dc = DataCenter
local sm = dc and dc.StatusManager
local out = {{
  ok = true,
  task = 'war_safety',
  dry_run = dryRun,
  shielded = false,
  war_fever_active = false,
  threats = {{}},
  shield_used = nil,
  recalled_marches = {{}},
  action = 'safe',
}}

if sm and sm.CheckShield then
  out.shielded = _safe_call(function() return sm:CheckShield() end, false) and true or false
end
if sm and sm.GetWarFeverStatusValue then
  local wf = tonumber(_safe_call(function() return sm:GetWarFeverStatusValue() end, 0)) or 0
  if wf > 0 then out.war_fever_active = true end
end

local nowMs = (snap.serverSec or 0) * 1000
local gatherPts = {{}}
local myMarches = {{}}
local wmm = dc and dc.WorldMyMarchDataManager
if wmm and wmm.GetAllMarches then
  local lst = _safe_call(function() return wmm:GetAllMarches() end, {{}}) or {{}}
  for k, m in pairs(lst) do
    if type(m) == 'table' then
      local muuid = tostring(m.uuid or k or '')
      local tType = tonumber(m.target or m.targetType or -1) or -1
      local tPos = tonumber(m.targetPos or m.finalTargetPos or 0) or 0
      local isGather = (tType == 2 or tType == 35 or tType == 87 or tType == 100)
      table.insert(myMarches, {{uuid = muuid, target = tType, targetPos = tPos, is_gather = isGather}})
      if isGather and tPos > 0 then gatherPts[tPos] = muuid end
    end
  end
end

local seenThreat = {{}}
local selfAttacked = false
local threatenedGatherUuids = {{}}
local function _scan_threat(src, obj)
  if type(obj) ~= 'table' then return end
  local ownerUid = tostring(obj.ownerUid or obj.atkUid or '')
  local ownerAlly = tostring(obj.allianceUid or '')
  if ownerUid ~= '' and ownerUid == snap.uid then return end
  if snap.allianceUid ~= '' and ownerAlly == snap.allianceUid then return end
  local tPt = tonumber(obj.targetPos or obj.targetPoint or obj.pointId or 0) or 0
  local tUid = tostring(obj.targetUid or obj.belongUid or obj.defUid or '')
  local tType = tonumber(obj.target or obj.targetType or obj.marchType or -1) or -1
  local endTime = tonumber(obj.endTime or obj.arriveTime or 0) or 0
  local eta = -1
  if endTime > 0 and nowMs > 0 then
    eta = math.floor((endTime - nowMs) / 1000)
    if eta < -10 or (maxEta > 0 and eta > maxEta) then return end
  end
  local hitsSelf = (tUid == snap.uid) or (snap.mainPos > 0 and tPt == snap.mainPos)
  local hitGatherUuid = (tPt > 0 and gatherPts[tPt]) or nil
  local isHostile = (tType == 11 or tType == 12 or tType == 10 or tType == 41 or src == 'radar')
  if not isHostile or (not hitsSelf and not hitGatherUuid) then return end
  local key = tostring(obj.uuid or obj.marchUuid or (src .. ':' .. tostring(tPt)))
  if seenThreat[key] then return end
  seenThreat[key] = true
  table.insert(out.threats, {{
    source = src,
    marchUuid = key,
    targetPoint = tPt,
    etaSec = eta,
    hits_self = hitsSelf,
    hits_gatherer = hitGatherUuid ~= nil,
  }})
  if hitsSelf then selfAttacked = true end
  if hitGatherUuid then threatenedGatherUuids[hitGatherUuid] = true end
end

local ram = dc and dc.RadarAlarmDataManager
if ram and ram.GetAllMarches then
  for _, m in pairs(_safe_call(function() return ram:GetAllMarches() end, {{}}) or {{}}) do _scan_threat('radar', m) end
end
local aam = dc and dc.AllianceAlertDataManager
if aam and aam.GetAllianceAlertList then
  for _, m in pairs(_safe_call(function() return aam:GetAllianceAlertList() end, {{}}) or {{}}) do _scan_threat('alliance_alert', m) end
end
local wmdm = dc and dc.WorldMarchDataManager
if wmdm and type(wmdm.allMarches) == 'table' then
  for _, m in pairs(wmdm.allMarches) do _scan_threat('world_march', m) end
end

if selfAttacked and autoShield and not out.shielded then
  if respectFever and out.war_fever_active then
    out.action = 'under_attack_war_fever_blocked_shield'
  else
    local idata = dc and dc.ItemData
    local itm = dc and dc.ItemTemplateManager
    if idata and idata.ItemInfos then
      for uuid, info in pairs(idata.ItemInfos) do
        local cnt = tonumber(info and info.count or 0) or 0
        if cnt > 0 then
          local tmpl = info.template or (itm and _safe_call(function() return itm:GetItemTemplate(tonumber(info.itemId)) end, nil))
          local nm = tmpl and Localization and Localization.GetString and tostring(_safe_call(function() return Localization:GetString(tostring(tmpl.name or '')) end, '') or ''):lower() or ''
          if nm:find('shield') or nm:find('peace') or nm:find('truce') then
            if not dryRun then
              if idata.UseTool then
                pcall(function() idata:UseTool(tonumber(info.itemId), 1) end)
              elseif MsgDefines and MsgDefines.ItemUse and SFSNetwork then
                pcall(function() SFSNetwork.SendMessage(MsgDefines.ItemUse, {{uuid = tostring(uuid), num = 1}}) end)
              end
            end
            out.shield_used = {{id = tostring(info.itemId), uuid = tostring(uuid), name = nm}}
            out.action = 'shield_activated'
            break
          end
        end
      end
    end
  end
end

if recallGatherers and (selfAttacked or next(threatenedGatherUuids) ~= nil) then
  local mu = package.loaded['SlgEngine.Util.MarchUtil.MarchUtil'] or package.loaded['Util.MarchUtil_SLG']
  for _, gm in ipairs(myMarches) do
    if gm.is_gather and (selfAttacked or threatenedGatherUuids[gm.uuid]) and gm.uuid ~= '' then
      if not dryRun and mu and mu.OnBackHome then
        pcall(function() mu.OnBackHome(gm.uuid) end)
      end
      table.insert(out.recalled_marches, gm.uuid)
      if out.action == 'safe' then out.action = 'recalled_gatherers' end
    end
  end
end

return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=10.0)


def run_hospital_heal(
    cd: Any,
    pid: int,
    client_state: dict[str, Any] | bool | None = None,
    cfg: dict[str, Any] | None = None,
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
    use_speedups: bool | None = None,
    max_speedup_mins: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if isinstance(client_state, bool):
        dry_run = client_state
        client_state = {}
    client_state = client_state if isinstance(client_state, dict) else {}
    cfg = cfg if isinstance(cfg, dict) else {}
    task_cfg = cfg.get("hospital_heal") or {}
    collect_fin = bool(kwargs.get("collect_finished", task_cfg.get("collect_finished", True)))
    batch_minutes = max(1, int(kwargs.get("batch_minutes", task_cfg.get("batch_minutes", 30)) or 30))
    min_troops = max(1, int(kwargs.get("min_batch_troops", task_cfg.get("min_batch_troops", 1)) or 1))
    max_troops = max(min_troops, int(kwargs.get("max_batch_troops", task_cfg.get("max_batch_troops", 1500)) or 1500))
    call_help = bool(kwargs.get("call_alliance_help", task_cfg.get("call_alliance_help", True)))
    max_chain_batches = max(1, int(kwargs.get("max_chain_batches", task_cfg.get("max_chain_batches", 5)) or 5))
    cross_client_help = bool(kwargs.get("cross_client_help", task_cfg.get("cross_client_help", True)))
    if use_speedups is None:
        use_speedups = bool(task_cfg.get("use_speedups", False))
    else:
        use_speedups = bool(use_speedups)
    if max_speedup_mins is None:
        max_speedup_mins = max(0, int(task_cfg.get("max_speedup_mins", 0) or 0))
    else:
        max_speedup_mins = max(0, int(max_speedup_mins or 0))

    lua_header = (
        f"local dryRun = {str(dry_run).lower()}\n"
        f"local collectFin = {str(collect_fin).lower()}\n"
        f"local batchSec = {batch_minutes * 60}\n"
        f"local batchMinutes = {batch_minutes}\n"
        f"local minTroops = {min_troops}\n"
        f"local maxTroops = {max_troops}\n"
        f"local callHelp = {str(call_help).lower()}\n"
        f"local useSpeedups = {str(use_speedups).lower()}\n"
        f"local maxSpeedupMins = {max_speedup_mins}\n"
    )

    lua = _LUA_QUEUE_HELP_HELPER + "\n" + lua_header + r"""
local snap = _get_player_snapshot()
local dc = DataCenter
local hm = dc and dc.HospitalManager
local qm = dc and dc.QueueDataManager
local atm = dc and dc.ArmyTemplateManager

local isDragon = (CommonUtil and CommonUtil.IsInDragonActivity and _safe_call(function() return CommonUtil.IsInDragonActivity() end, false)) or false
local targetQType = isDragon
  and ((NewQueueType and tonumber(NewQueueType.DragonHospital)) or 46)
  or ((NewQueueType and tonumber(NewQueueType.Hospital)) or 3)
local currSceneId = (SceneManager and tonumber(SceneManager.CurrSceneID)) or 0
local isInHome = (SceneManager and SceneManager.IsInHome and _safe_call(function() return SceneManager:IsInHome() end, nil))
local sceneView = (currSceneId == 1 or isInHome == true) and 'city' or ((currSceneId == 2 or isInHome == false) and 'world' or 'other')

local out = {
  ok = true,
  task = 'hospital_heal',
  dry_run = dryRun,
  dormant = false,
  scene_id = currSceneId,
  scene_view = sceneView,
  is_dragon_activity = isDragon,
  world_view_compatible = true,
  rpc_protocol = "MsgDefines.HospitalCure ('hospital.cure') -> { arr = { [armyId] = healNum }, gold = IsGold.NoUseGold }",
  batch_minutes = batchMinutes,
  in_treatment_total = 0,
  untreated_total = 0,
  wounded_total = 0,
  in_treatment_armies = {},
  untreated_armies = {},
  queue_uuid = '',
  queue_type = targetQType,
  queue_state = 0,
  queue_start_ms = 0,
  queue_end_ms = 0,
  queue_remaining_sec = 0,
  remaining_seconds = 0,
  is_helped = 0,
  collected = false,
  help_requested = false,
  use_speedups = useSpeedups,
  max_speedup_mins = maxSpeedupMins,
  speedup_inventory = {['210140'] = 0, ['210141'] = 0, ['210142'] = 0},
  speedups_applied = {},
  speedup_seconds_applied = 0,
  speedup_item_str = '',
  queued_troops = 0,
  estimated_batch_sec = 0,
  queued_armies = {},
  heal_time_calibration = {},
  rpc_sent = false,
  rpc_payload = nil,
  phases_executed = {},
  action = 'none',
}
if not hm or not qm then
  out.ok = false
  out.error = 'HospitalManager or QueueDataManager unavailable'
  return _enc(out)
end

local function _get_num_field(obj, ...)
  local names = {...}
  for i = 1, #names do
    local nm = names[i]
    local ok, val = pcall(function() return obj[nm] end)
    if ok and val ~= nil then
      local num = tonumber(val)
      if num ~= nil then return num end
    end
  end
  return 0
end

local function _get_str_field(obj, ...)
  local names = {...}
  for i = 1, #names do
    local nm = names[i]
    local ok, val = pcall(function() return obj[nm] end)
    if ok and val ~= nil and tostring(val) ~= '' then
      return tostring(val)
    end
  end
  return ''
end

local function _get_queue_state(q)
  if q == nil then return 0 end
  if q.GetQueueState then
    local okS, s = pcall(function() return tonumber(q:GetQueueState()) end)
    if okS and s ~= nil then return math.floor(s) end
  end
  if qm and qm.GetQueueState then
    local okS, s = pcall(function() return tonumber(qm:GetQueueState(q)) end)
    if okS and s ~= nil then return math.floor(s) end
  end
  return math.floor(_get_num_field(q, 'state'))
end

-- Real buffed per-soldier heal duration in seconds (exact match to UIHospitalMainView / ArmyTemplateManager:GetTreatTime)
local function _get_real_treat_sec(aid)
  if not atm then return 30.0 end
  local t = nil
  if atm.GetTreatTime then
    t = _safe_call(function() return atm:GetTreatTime(tostring(aid)) end, nil)
    if not t or tonumber(t) == nil or tonumber(t) <= 0 then
      t = _safe_call(function() return atm:GetTreatTime(tonumber(aid) or aid) end, nil)
    end
  end
  if (not t or tonumber(t) == nil or tonumber(t) <= 0) and atm.GetArmyTemplate then
    local tpl = _safe_call(function() return atm:GetArmyTemplate(tostring(aid)) end, nil)
    if not tpl then
      tpl = _safe_call(function() return atm:GetArmyTemplate(tonumber(aid) or aid) end, nil)
    end
    if tpl and tpl.GetTreatTime then
      t = _safe_call(function() return tpl:GetTreatTime() end, nil)
    end
  end
  local num = tonumber(t)
  if num and num > 0 then
    return num
  end
  return 30.0
end

local function _get_treat_resources(aid)
  if not atm or not atm.GetArmyTemplate then return nil end
  local tpl = _safe_call(function() return atm:GetArmyTemplate(tostring(aid)) end, nil)
  if not tpl then
    tpl = _safe_call(function() return atm:GetArmyTemplate(tonumber(aid) or aid) end, nil)
  end
  if tpl and tpl.GetTreatResource then
    local res = _safe_call(function() return tpl:GetTreatResource() end, nil)
    if type(res) == 'table' then return res end
  end
  return nil
end

local function _get_treat_res_percent()
  local percent = 1.0
  if LuaEntry and LuaEntry.Effect and EffectDefine then
    if isDragon then
      local num1 = tonumber(_safe_call(function() return LuaEntry.Effect:GetGameEffect(30318) end, 0)) or 0
      percent = math.max(0.0, 1.0 - num1 / 100.0)
    else
      local num1 = tonumber(_safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.CURE_RESOURCE_REDUCE) end, 0)) or 0
      local num2 = tonumber(_safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.HEAL_MONEY_DEC) end, 0)) or 0
      percent = math.max(0.0, (1.0 - num1 / 100.0) * (1.0 - num2 / 100.0))
    end
  end
  return percent
end

-- ============================================================================
-- PHASE A: Telemetry & Queue 3 Inspection (Pure DataCenter - City & World Safe)
-- ============================================================================
table.insert(out.phases_executed, 'PhaseA_Telemetry')
local nowMs = (snap.serverSec or 0) * 1000
if nowMs <= 0 then
  nowMs = (UITimeManager and UITimeManager.GetInstance and _safe_call(function() return UITimeManager:GetInstance():GetServerTime() end, 0))
    or (TimeUtil and TimeUtil.GetServerTimeMs and _safe_call(function() return TimeUtil.GetServerTimeMs() end, 0))
    or (os.time() * 1000)
end

-- 1) Extract HospitalInfo entries (prefer hm:GetAllHospital() which honors DragonActivity + level sort)
local injuredEntries = {}
local injuredCandidates = {}
if hm.GetAllHospital then
  local ok_g, g = pcall(function() return hm:GetAllHospital() end)
  if ok_g and g ~= nil then table.insert(injuredCandidates, g) end
end
if isDragon and hm.dragonHospital ~= nil then
  table.insert(injuredCandidates, hm.dragonHospital)
end
if hm.allHospital ~= nil then table.insert(injuredCandidates, hm.allHospital) end
if hm.GetHospitalDic then
  local ok_d, d = pcall(function() return hm:GetHospitalDic() end)
  if ok_d and d ~= nil then table.insert(injuredCandidates, d) end
end
if hm.hospitalDic ~= nil then table.insert(injuredCandidates, hm.hospitalDic) end

local function _extract_entries(col, dst)
  if not col then return false end
  local found = false
  if type(col) == 'table' then
    local n = #col
    if n > 0 then
      for i = 1, n do
        if col[i] ~= nil then
          table.insert(dst, {key = i, val = col[i]})
          found = true
        end
      end
      if found then return true end
    end
    for k, v in pairs(col) do
      if v ~= nil then
        table.insert(dst, {key = k, val = v})
        found = true
      end
    end
    if found then return true end
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
              table.insert(dst, {key = k, val = v})
              found = true
            else
              table.insert(dst, {key = #dst + 1, val = cur})
              found = true
            end
          end
        end
      end
    end
  end)
  if found then return true end
  pcall(function()
    local cnt = tonumber(col.Count) or 0
    if cnt > 0 then
      for i = 0, cnt - 1 do
        local okI, item = pcall(function() return col[i] end)
        if okI and item ~= nil then
          table.insert(dst, {key = i, val = item})
          found = true
        end
      end
    end
  end)
  return found
end

for _, cand in ipairs(injuredCandidates) do
  if _extract_entries(cand, injuredEntries) then break end
end

local seenArmy = {}
for _, item in ipairs(injuredEntries) do
  local entry = item.val
  local k = item.key
  if type(entry) == 'table' or type(entry) == 'userdata' or type(entry) == 'number' then
    local aid = ''
    local healCnt = 0
    local deadCnt = 0
    if type(entry) == 'number' then
      aid = tostring(k or '')
      deadCnt = math.max(0, math.floor(tonumber(entry) or 0))
    else
      aid = _get_str_field(entry, 'armyId', 'id')
      if aid == '' and k ~= nil then aid = tostring(k) end
      healCnt = math.max(0, math.floor(_get_num_field(entry, 'heal', 'healing', 'cure')))
      deadCnt = math.max(0, math.floor(_get_num_field(entry, 'dead', 'num', 'injured', 'wounded', 'count', 'hurt')))
    end
    if aid ~= '' and not seenArmy[aid] then
      seenArmy[aid] = true
      local uSec = _get_real_treat_sec(aid)
      if healCnt > 0 then
        out.in_treatment_total = out.in_treatment_total + healCnt
        table.insert(out.in_treatment_armies, {armyId = aid, heal = healCnt, unit_treat_sec = uSec})
      end
      if deadCnt > 0 then
        out.untreated_total = out.untreated_total + deadCnt
        table.insert(out.untreated_armies, {armyId = aid, dead = deadCnt, unit_treat_sec = uSec})
      end
    end
  end
end
out.wounded_total = out.in_treatment_total + out.untreated_total

-- Calibrate real 30-min batch size telemetry (works even when dormant/0 wounded for dry-run verification)
if #out.untreated_armies > 0 then
  for i = 1, math.min(5, #out.untreated_armies) do
    local ua = out.untreated_armies[i]
    local uSec = ua.unit_treat_sec or _get_real_treat_sec(ua.armyId)
    local bTroops = math.max(1, math.min(maxTroops, math.floor(batchSec / math.max(0.1, uSec))))
    table.insert(out.heal_time_calibration, {
      armyId = ua.armyId,
      unit_treat_sec = uSec,
      batch_troops_for_target = bTroops,
      est_batch_sec = math.ceil(bTroops * uSec),
    })
  end
else
  local am = dc and dc.ArmyManager
  local allArmy = am and (am.allArmy or am.armyList or am.armyDic)
  if type(allArmy) == 'table' then
    local calCnt = 0
    for k, a in pairs(allArmy) do
      if calCnt < 3 and type(a) == 'table' then
        local aid = tostring(a.armyId or a.id or k)
        local free = tonumber(a.free or a.num or a.count or 0) or 0
        if aid ~= '' and free > 0 then
          local uSec = _get_real_treat_sec(aid)
          local bTroops = math.max(1, math.min(maxTroops, math.floor(batchSec / math.max(0.1, uSec))))
          table.insert(out.heal_time_calibration, {
            armyId = aid,
            unit_treat_sec = uSec,
            batch_troops_for_target = bTroops,
            est_batch_sec = math.ceil(bTroops * uSec),
          })
          calCnt = calCnt + 1
        end
      end
    end
  end
end

-- 2) Inspect Hospital Queue (targetQType = 3 normal, 46 dragon) from DataCenter.QueueDataManager
local finState = (NewQueueState and tonumber(NewQueueState.Finish)) or 3
local workState = (NewQueueState and tonumber(NewQueueState.Work)) or 2

local activeQ = nil
if qm and qm.GetQueueByType then
  local single = _safe_call(function() return qm:GetQueueByType(targetQType) end, nil)
  if type(single) == 'table' or type(single) == 'userdata' then
    activeQ = single
  end
end
if not activeQ and qm and qm.queueDic then
  local qEntries = {}
  _extract_entries(qm.queueDic, qEntries)
  for _, qe in ipairs(qEntries) do
    local q = qe.val
    if type(q) == 'table' or type(q) == 'userdata' then
      local qt = math.floor(_get_num_field(q, 'type'))
      if qt == targetQType then
        local qSt = _get_queue_state(q)
        if not activeQ or qSt == workState or qSt == finState then
          activeQ = q
          if qSt == workState or qSt == finState then break end
        end
      end
    end
  end
end

local activeQState = 0
local activeStartMs = 0
local activeEndMs = 0
local activeHelped = 0
if activeQ then
  activeQState = _get_queue_state(activeQ)
  activeStartMs = _get_num_field(activeQ, 'startTime')
  activeEndMs = _get_num_field(activeQ, 'endTime')
  if activeStartMs > 0 and activeStartMs < 1e12 then activeStartMs = activeStartMs * 1000 end
  if activeEndMs > 0 and activeEndMs < 1e12 then activeEndMs = activeEndMs * 1000 end
  activeHelped = math.floor(_get_num_field(activeQ, 'isHelped', 'callHelp'))
  out.queue_uuid = _get_str_field(activeQ, 'uuid')
  out.queue_type = math.floor(_get_num_field(activeQ, 'type'))
  if out.queue_type <= 0 then out.queue_type = targetQType end
  out.queue_state = activeQState
  out.queue_start_ms = activeStartMs
  out.queue_end_ms = activeEndMs
  out.is_helped = activeHelped
  if activeQState == workState and activeEndMs > nowMs and nowMs > 0 then
    out.queue_remaining_sec = math.max(0, math.floor((activeEndMs - nowMs) / 1000))
    out.remaining_seconds = out.queue_remaining_sec
  end
end

-- Inspect healing speedup inventory (210140 = 1m, 210141 = 5m, 210142 = 60m)
local healSpeedDefs = {
  {id = 210142, key = '210142', mins = 60, sec = 3600},
  {id = 210141, key = '210141', mins = 5,  sec = 300},
  {id = 210140, key = '210140', mins = 1,  sec = 60},
}
local idata = dc and dc.ItemData
if idata then
  if idata.ItemInfos then
    local itemEntries = {}
    _extract_entries(idata.ItemInfos, itemEntries)
    for _, ie in ipairs(itemEntries) do
      local info = ie.val
      if type(info) == 'table' or type(info) == 'userdata' then
        local iid = math.floor(_get_num_field(info, 'itemId', 'id'))
        if iid <= 0 then iid = tonumber(ie.key) or 0 end
        local icnt = math.max(0, math.floor(_get_num_field(info, 'count', 'num')))
        if iid == 210140 or iid == 210141 or iid == 210142 then
          local kstr = tostring(iid)
          out.speedup_inventory[kstr] = (out.speedup_inventory[kstr] or 0) + icnt
        end
      end
    end
  end
  if idata.GetItemCount then
    for _, sp in ipairs(healSpeedDefs) do
      if (out.speedup_inventory[sp.key] or 0) == 0 then
        local cnt = math.max(0, math.floor(tonumber(_safe_call(function() return idata:GetItemCount(sp.id) end, 0)) or 0))
        if cnt > 0 then out.speedup_inventory[sp.key] = cnt end
      end
    end
  end
end

local isActivelyHealing = (activeQ ~= nil and activeQState == workState and activeEndMs > nowMs and nowMs > 0)
local isQueueFinished = false
if activeQ ~= nil then
  isQueueFinished = (activeQState == finState) or (activeQState == workState and activeEndMs > 0 and nowMs > 0 and activeEndMs <= nowMs)
  if not isQueueFinished and qm and qm.IsQueueTimeFinish and out.queue_uuid ~= '' then
    local okF, f = pcall(function() return qm:IsQueueTimeFinish(activeQ) end)
    if okF and f and activeQState ~= 0 then isQueueFinished = true end
  end
end

-- ============================================================================
-- PHASE B: Alliance Help on Active Queue (Exact SendCallHelp 4-Arg Protocol)
-- ============================================================================
if isActivelyHealing then
  out.action = 'healing_in_progress'
  if callHelp and out.is_helped == 0 and out.queue_uuid ~= '' then
    table.insert(out.phases_executed, 'PhaseB_AllianceHelp')
    if not dryRun then
      if _send_queue_alliance_help(qm, activeQ) then
        out.is_helped = 1
        out.help_requested = true
        out.action = 'requested_help'
      end
    else
      out.help_requested = true
      out.action = 'requested_help'
    end
  end
end

-- ============================================================================
-- PHASE C: Smart Healing Speedup Application
-- ============================================================================
if isActivelyHealing and useSpeedups and out.queue_remaining_sec > 0 and out.queue_uuid ~= '' then
  table.insert(out.phases_executed, 'PhaseC_Speedups')
  local budgetSec = out.queue_remaining_sec
  if maxSpeedupMins > 0 then
    budgetSec = math.min(budgetSec, maxSpeedupMins * 60)
  end
  local parts = {}
  local totalAppliedSec = 0
  for _, sp in ipairs(healSpeedDefs) do
    local avail = tonumber(out.speedup_inventory[sp.key] or 0) or 0
    if avail > 0 and budgetSec >= sp.sec then
      local useQty = math.min(avail, math.floor(budgetSec / sp.sec))
      if useQty > 0 then
        budgetSec = budgetSec - (useQty * sp.sec)
        totalAppliedSec = totalAppliedSec + (useQty * sp.sec)
        table.insert(parts, tostring(sp.id) .. ';' .. tostring(useQty))
        table.insert(out.speedups_applied, {
          itemId = sp.id,
          mins = sp.mins,
          count = useQty,
          total_sec = useQty * sp.sec,
        })
      end
    end
  end
  out.speedup_seconds_applied = totalAppliedSec
  out.speedup_item_str = table.concat(parts, '|')
  if #parts > 0 then
    if not dryRun and SFSNetwork and MsgDefines and MsgDefines.QueueCcdMNew then
      local goldFlag = (IsGold and IsGold.NoUseGold) or 0
      pcall(function()
        SFSNetwork.SendMessage(MsgDefines.QueueCcdMNew, {
          qUUID = activeQ.uuid,
          itemIDs = out.speedup_item_str,
          isGold = goldFlag,
        })
      end)
      out.queue_remaining_sec = math.max(0, out.queue_remaining_sec - totalAppliedSec)
      out.remaining_seconds = out.queue_remaining_sec
      if out.queue_remaining_sec <= 0 then
        isActivelyHealing = false
        isQueueFinished = true
      end
    end
    out.action = dryRun and 'would_apply_healing_speedups' or 'applied_healing_speedups'
  end
end

-- ============================================================================
-- PHASE D: Collect Finished Healing
-- ============================================================================
if isQueueFinished and collectFin and activeQ then
  table.insert(out.phases_executed, 'PhaseD_CollectFinished')
  local status = _collect_or_help_queue(qm, activeQ, nowMs, dryRun,
    function()
      out.collected = true
      if not dryRun and hm and hm.CheckSendFinish then
        pcall(function() hm:CheckSendFinish() end)
      end
    end,
    function() if callHelp then out.help_requested = true end end
  )
  if status == 'finished' or isQueueFinished then
    out.collected = true
    out.action = 'collected_healed'
    if not dryRun and hm and hm.CheckSendFinish then
      pcall(function() hm:CheckSendFinish() end)
    end
    isActivelyHealing = false
    out.queue_state = 0
    out.queue_remaining_sec = 0
    out.remaining_seconds = 0
  end
end

-- ============================================================================
-- PHASE E: Enqueue Untreated Wounded Pool (Exact HospitalCure Dictionary Map)
-- ============================================================================
if not isActivelyHealing and out.untreated_total > 0 then
  table.insert(out.phases_executed, 'PhaseE_EnqueueUntreated')
  local healArrMap = {}
  local healArrCount = 0
  local secLeft = batchSec
  local totalSelected = 0
  local estBatchSec = 0.0
  local resPercent = _get_treat_res_percent()
  local ownResource = {}
  local resourceShortage = false

  for _, uArmy in ipairs(out.untreated_armies) do
    local aid = tostring(uArmy.armyId or '')
    local injured = math.floor(tonumber(uArmy.dead or 0) or 0)
    if injured > 0 and aid ~= '' and totalSelected < maxTroops and secLeft > 0 then
      local unitSec = uArmy.unit_treat_sec or _get_real_treat_sec(aid)
      -- Cap by available resources (matches UIHospitalMainView:PreShowCountDefault)
      local maxAffordable = injured
      local tempRes = _get_treat_resources(aid)
      if tempRes and LuaEntry and LuaEntry.Resource and LuaEntry.Resource.GetCntByResType then
        for _, v1 in ipairs(tempRes) do
          local rt = v1.resourceType
          local baseCost = tonumber(v1.count or 0) or 0
          local cost = math.ceil(baseCost * resPercent)
          if rt ~= nil and cost > 0 then
            if ownResource[rt] == nil then
              ownResource[rt] = tonumber(_safe_call(function() return LuaEntry.Resource:GetCntByResType(rt) end, 0)) or 0
            end
            local afford = math.floor(math.max(0, ownResource[rt]) / cost)
            if afford < maxAffordable then
              maxAffordable = afford
            end
          end
        end
      end
      if maxAffordable <= 0 then
        resourceShortage = true
      else
        local byTime = math.floor(secLeft / math.max(0.1, unitSec))
        local take = math.min(maxAffordable, maxTroops - totalSelected, byTime)
        if take <= 0 and totalSelected == 0 then
          -- Always heal at least 1 soldier if 1 soldier exceeds batchSec and resources allow
          take = math.min(maxAffordable, maxTroops, 1)
        end
        local takeInt = math.tointeger(math.floor(take)) or math.floor(take)
        if takeInt > 0 then
          healArrMap[aid] = takeInt
          healArrCount = healArrCount + 1
          table.insert(out.queued_armies, {
            armyId = aid,
            healNum = takeInt,
            totalInjured = injured,
            unit_treat_sec = unitSec,
            est_sec = math.ceil(takeInt * unitSec),
          })
          totalSelected = totalSelected + takeInt
          estBatchSec = estBatchSec + (takeInt * unitSec)
          secLeft = secLeft - (takeInt * unitSec)
          if tempRes then
            for _, v1 in ipairs(tempRes) do
              local rt = v1.resourceType
              local cost = math.ceil((tonumber(v1.count or 0) or 0) * resPercent)
              if rt ~= nil and cost > 0 and ownResource[rt] ~= nil then
                ownResource[rt] = ownResource[rt] - (cost * takeInt)
              end
            end
          end
        end
      end
    end
  end

  if totalSelected == 0 and resourceShortage then
    out.ok = false
    out.dormant = false
    out.action = 'insufficient_resources'
    out.error = 'Insufficient resources to heal untreated troops'
    out.message = out.error
    return _enc(out)
  end

  if totalSelected > 0 and healArrCount > 0 then
    local goldFlag = (IsGold and IsGold.NoUseGold) or 0
    out.estimated_batch_sec = math.ceil(estBatchSec)
    out.rpc_payload = {
      cmd = (MsgDefines and MsgDefines.HospitalCure) or 'hospital.cure',
      gold = goldFlag,
      arr = healArrMap,
    }
    if not dryRun then
      if not (MsgDefines and MsgDefines.HospitalCure and SFSNetwork and SFSNetwork.SendMessage) then
        out.ok = false
        out.action = 'cure_rpc_unavailable'
        out.error = 'MsgDefines.HospitalCure or SFSNetwork.SendMessage unavailable'
        return _enc(out)
      end
      -- Drain stale pre-send popups so post-send verification only captures popups from this cure RPC
      if type(_G.__hzPopupLog) == 'table' and #_G.__hzPopupLog > 0 then
        out.pre_send_popups = _drain_popup_log()
      end
      local sendOk, sendErr = pcall(function()
        SFSNetwork.SendMessage(MsgDefines.HospitalCure, {
          arr = healArrMap,
          gold = goldFlag,
        })
      end)
      out.rpc_sent = sendOk
      if not sendOk then
        out.ok = false
        out.action = 'cure_rpc_error'
        out.error = 'HospitalCure SendMessage threw: ' .. tostring(sendErr)
        return _enc(out)
      end
    elseif dryRun and callHelp then
      out.help_requested = true
    end
    out.dormant = false
    out.queued_troops = totalSelected
    out.action = dryRun and 'would_queue_healing' or 'started_heal_batch'
    out.message = string.format(
      "%s %d untreated troops for healing (~%ds est, in_treatment=%d, untreated=%d)",
      dryRun and "Would queue" or "Queued",
      totalSelected, out.estimated_batch_sec, out.in_treatment_total, out.untreated_total
    )
    return _enc(out)
  end
end

if out.wounded_total == 0 and out.in_treatment_total == 0 and out.untreated_total == 0 and not isActivelyHealing and not isQueueFinished and not out.collected then
  out.dormant = true
  out.action = 'dormant_no_wounded'
  out.message = 'No wounded troops in hospital (dormant)'
  return _enc(out)
end

out.dormant = false

if isActivelyHealing then
  local remSec = out.queue_remaining_sec
  local d = math.floor(remSec / 86400)
  local h = math.floor((remSec % 86400) / 3600)
  local m = math.floor((remSec % 3600) / 60)
  local s = math.floor(remSec % 60)
  local timeStr = d > 0 and string.format("%dd %dh", d, h)
    or (h > 0 and string.format("%dh %dm", h, m)
    or (m > 0 and string.format("%dm %ds", m, s) or string.format("%ds", s)))
  out.message = string.format(
    "Hospital Queue %d healing %d troops (%s remaining, %d untreated waiting, helped=%d)",
    out.queue_type, out.in_treatment_total, timeStr, out.untreated_total, out.is_helped
  )
  return _enc(out)
end

if out.collected and out.queued_troops == 0 then
  out.message = string.format("Collected finished healing batch (untreated remaining=%d)", out.untreated_total)
end

return _enc(out)
"""

    def _build_verify_lua(pre_in_treat: int, pre_untreated: int) -> str:
        hdr = (
            f"local preInTreat = {int(pre_in_treat)}\n"
            f"local preUntreated = {int(pre_untreated)}\n"
            f"local callHelp = {str(call_help).lower()}\n"
        )
        return _LUA_QUEUE_HELP_HELPER + "\n" + hdr + r"""
local snap = _get_player_snapshot()
local dc = DataCenter
local hm = dc and dc.HospitalManager
local qm = dc and dc.QueueDataManager
local isDragon = (CommonUtil and CommonUtil.IsInDragonActivity and _safe_call(function() return CommonUtil.IsInDragonActivity() end, false)) or false
local targetQType = isDragon
  and ((NewQueueType and tonumber(NewQueueType.DragonHospital)) or 46)
  or ((NewQueueType and tonumber(NewQueueType.Hospital)) or 3)

local out = {
  ok = true,
  cure_verified = false,
  in_treatment_total = 0,
  untreated_total = 0,
  wounded_total = 0,
  queue_uuid = '',
  queue_type = targetQType,
  queue_state = 0,
  queue_remaining_sec = 0,
  remaining_seconds = 0,
  is_helped = 0,
  help_requested = false,
  open_error_windows = {},
}
if not hm or not qm then
  out.ok = false
  out.error = 'HospitalManager or QueueDataManager unavailable during verify'
  return _enc(out)
end

local function _get_num(obj, ...)
  local names = {...}
  for i = 1, #names do
    local ok, val = pcall(function() return obj[names[i]] end)
    if ok and val ~= nil then
      local num = tonumber(val)
      if num ~= nil then return num end
    end
  end
  return 0
end

local function _get_str(obj, ...)
  local names = {...}
  for i = 1, #names do
    local ok, val = pcall(function() return obj[names[i]] end)
    if ok and val ~= nil and tostring(val) ~= '' then return tostring(val) end
  end
  return ''
end

-- 1) Re-read hospital wounded & in-treatment counts
local entries = {}
local col = (hm.GetAllHospital and _safe_call(function() return hm:GetAllHospital() end, nil))
  or (isDragon and hm.dragonHospital)
  or hm.allHospital
if type(col) == 'table' then
  for k, v in pairs(col) do
    if type(v) == 'table' or type(v) == 'userdata' then
      local healCnt = math.max(0, math.floor(_get_num(v, 'heal', 'healing', 'cure')))
      local deadCnt = math.max(0, math.floor(_get_num(v, 'dead', 'num', 'injured', 'wounded', 'count', 'hurt')))
      out.in_treatment_total = out.in_treatment_total + healCnt
      out.untreated_total = out.untreated_total + deadCnt
    end
  end
end
out.wounded_total = out.in_treatment_total + out.untreated_total

-- 2) Re-read Queue Type 3 (or 46)
local nowMs = (snap.serverSec or 0) * 1000
if nowMs <= 0 then
  nowMs = (UITimeManager and UITimeManager.GetInstance and _safe_call(function() return UITimeManager:GetInstance():GetServerTime() end, 0))
    or (os.time() * 1000)
end
local workState = (NewQueueState and tonumber(NewQueueState.Work)) or 2
local finState = (NewQueueState and tonumber(NewQueueState.Finish)) or 3

local targetQ = qm.GetQueueByType and _safe_call(function() return qm:GetQueueByType(targetQType) end, nil) or nil
if not targetQ and type(qm.queueDic) == 'table' then
  for _, q in pairs(qm.queueDic) do
    if (type(q) == 'table' or type(q) == 'userdata') and math.floor(_get_num(q, 'type')) == targetQType then
      targetQ = q
      break
    end
  end
end

if targetQ then
  local qSt = math.floor(_get_num(targetQ, 'state'))
  if targetQ.GetQueueState then
    local okS, s = pcall(function() return tonumber(targetQ:GetQueueState()) end)
    if okS and s ~= nil then qSt = math.floor(s) end
  elseif qm.GetQueueState then
    local okS, s = pcall(function() return tonumber(qm:GetQueueState(targetQ)) end)
    if okS and s ~= nil then qSt = math.floor(s) end
  end
  local endMs = _get_num(targetQ, 'endTime')
  if endMs > 0 and endMs < 1e12 then endMs = endMs * 1000 end
  out.queue_uuid = _get_str(targetQ, 'uuid')
  out.queue_type = math.floor(_get_num(targetQ, 'type'))
  if out.queue_type <= 0 then out.queue_type = targetQType end
  out.queue_state = qSt
  out.is_helped = math.floor(_get_num(targetQ, 'isHelped', 'callHelp'))
  if qSt == workState and endMs > nowMs and nowMs > 0 then
    out.queue_remaining_sec = math.max(0, math.floor((endMs - nowMs) / 1000))
    out.remaining_seconds = out.queue_remaining_sec
  end
end

-- 3) Detect any open Tips / Modal error dialogs via UIManager
pcall(function()
  if UIManager and UIManager.GetInstance and UIWindowNames then
    local um = UIManager:GetInstance()
    for _, wName in ipairs({UIWindowNames.UICommonMessageTip, UIWindowNames.UICommonModal}) do
      if wName and um.IsWindowOpen and um:IsWindowOpen(wName) then
        local txt = ''
        local win = um.GetWindow and um:GetWindow(wName)
        if win and win.View then
          pcall(function()
            if win.View.tipText then txt = tostring(win.View.tipText)
            elseif win.View.contentText and win.View.contentText.text then txt = tostring(win.View.contentText.text)
            end
          end)
        end
        table.insert(out.open_error_windows, {window = tostring(wName), text = txt})
      end
    end
  end
end)

-- 4) Verify cure was accepted by server
local cureVerified = (out.in_treatment_total > preInTreat)
  or (out.untreated_total < preUntreated)
  or (out.queue_state == workState and out.queue_remaining_sec > 0)
  or (out.queue_state == finState)
out.cure_verified = cureVerified

-- 5) Immediately request Alliance Help ONLY after Queue 3 is verified active with UUID
if cureVerified and callHelp and targetQ and out.queue_state == workState and out.queue_uuid ~= '' and out.is_helped == 0 then
  if _send_queue_alliance_help(qm, targetQ) then
    out.help_requested = true
    out.is_helped = 1
  end
end

return _enc(out)
"""

    batches_chained = 0
    total_queued_troops = 0
    cross_client_helps_triggered = 0
    total_collected = 0
    any_help_requested = False
    all_tips: list[str] = []
    all_modals: list[dict[str, Any]] = []
    chain_history: list[dict[str, Any]] = []
    last_res: dict[str, Any] = {}

    for pass_idx in range(max_chain_batches):
        step_res = _eval_json(cd, pid, lua, timeout=10.0)
        if not isinstance(step_res, dict) or not step_res.get("ok", False):
            if pass_idx == 0:
                err_out = step_res if isinstance(step_res, dict) else {"ok": False, "error": "hospital_heal eval failed"}
                err_out.setdefault("task", "hospital_heal")
                err_out.setdefault("dormant", False)
                err_out.setdefault("batches_chained", 0)
                err_out.setdefault("total_queued_troops", 0)
                err_out.setdefault("cross_client_helps_triggered", 0)
                return err_out
            break

        last_res = step_res
        step_tips = _clean_in_game_tips(step_res.get("in_game_tips") or step_res.get("tips") or [])
        if step_tips:
            all_tips.extend(step_tips)
        step_modals = list(step_res.get("modal_dialogs") or [])
        if step_modals:
            all_modals.extend(step_modals)

        wounded_total = int(step_res.get("wounded_total") or 0)
        in_treat = int(step_res.get("in_treatment_total") or 0)
        untreated = int(step_res.get("untreated_total") or 0)
        queued_now = int(step_res.get("queued_troops") or 0)
        collected_now = bool(step_res.get("collected", False))
        speedups_now = int(step_res.get("speedup_seconds_applied") or 0)
        step_action = str(step_res.get("action") or "")
        step_dormant = bool(step_res.get("dormant", False))

        # Early exit when hospital is completely empty (dormant)
        if step_dormant and wounded_total == 0 and in_treat == 0 and untreated == 0 and not collected_now:
            chain_history.append({
                "pass": pass_idx + 1,
                "action": "dormant_no_wounded",
                "dormant": True,
                "wounded_total": 0,
                "queued_troops": 0,
                "cross_client_helps": 0,
            })
            break

        # Post-enqueue 1.0s Server Verification & Batch-Chaining Guard + Alliance Help
        cure_verified = True
        if not dry_run and queued_now > 0:
            pre_in_treat = in_treat
            pre_untreated = untreated
            time.sleep(1.0)
            ver_res = _eval_json(cd, pid, _build_verify_lua(pre_in_treat, pre_untreated), timeout=8.0)
            ver_tips = _clean_in_game_tips(
                (ver_res.get("in_game_tips") or []) if isinstance(ver_res, dict) else []
            )
            ver_modals = list((ver_res.get("modal_dialogs") or []) if isinstance(ver_res, dict) else [])
            open_err_wins = list((ver_res.get("open_error_windows") or []) if isinstance(ver_res, dict) else [])
            for w_info in open_err_wins:
                ver_modals.append({
                    "type": "open_error_window",
                    "title": str(w_info.get("window") or "Tips"),
                    "content": str(w_info.get("text") or ""),
                })
            if ver_tips:
                all_tips.extend(ver_tips)
            if ver_modals:
                all_modals.extend(ver_modals)

            post_modals = step_modals + ver_modals
            post_tips = _clean_in_game_tips(step_tips + ver_tips)

            if not isinstance(ver_res, dict) or not ver_res.get("ok", False):
                cure_verified = False
                fail_reason = (
                    str(ver_res.get("error") or "post-cure verification eval failed")
                    if isinstance(ver_res, dict)
                    else "post-cure verification eval failed"
                )
            else:
                in_treat_after = int(ver_res.get("in_treatment_total") or 0)
                untreated_after = int(ver_res.get("untreated_total") or 0)
                q_state_after = int(ver_res.get("queue_state") or 0)
                q_rem_after = int(ver_res.get("queue_remaining_sec") or 0)
                cure_verified = bool(
                    ver_res.get("cure_verified", False)
                    or (in_treat_after > pre_in_treat)
                    or (untreated_after < pre_untreated)
                    or (q_state_after == 2 and q_rem_after > 0)
                    or (q_state_after == 3)
                )
                # Abort if server did NOT start healing (in_treatment still 0 and untreated did not drop, or modal error blocked it)
                if not cure_verified or (in_treat_after == 0 and untreated_after >= pre_untreated and q_state_after != 2 and q_state_after != 3):
                    cure_verified = False
                    modal_strs = [
                        f"{m.get('title', 'Tips')}: {m.get('content', '')}".strip(": ")
                        for m in post_modals
                        if isinstance(m, dict)
                    ]
                    fail_parts = [
                        f"HospitalCure rejected/ignored by server after 1.0s "
                        f"(in_treatment={in_treat_after}, untreated={untreated_after}, queue_state={q_state_after})"
                    ]
                    if modal_strs:
                        fail_parts.append("modals=" + "; ".join(modal_strs))
                    if post_tips:
                        fail_parts.append("tips=" + "; ".join(post_tips))
                    fail_reason = " | ".join(fail_parts)
                else:
                    # Sync step_res telemetry with verified live post-cure state
                    in_treat = in_treat_after
                    untreated = untreated_after
                    wounded_total = int(ver_res.get("wounded_total") or (in_treat + untreated))
                    step_res["in_treatment_total"] = in_treat
                    step_res["untreated_total"] = untreated
                    step_res["wounded_total"] = wounded_total
                    step_res["queue_uuid"] = str(ver_res.get("queue_uuid") or step_res.get("queue_uuid") or "")
                    step_res["queue_type"] = int(ver_res.get("queue_type") or step_res.get("queue_type") or 3)
                    step_res["queue_state"] = q_state_after
                    step_res["queue_remaining_sec"] = q_rem_after
                    step_res["remaining_seconds"] = q_rem_after
                    step_res["is_helped"] = int(ver_res.get("is_helped") or step_res.get("is_helped") or 0)
                    if ver_res.get("help_requested"):
                        step_res["help_requested"] = True
                        step_res["is_helped"] = 1

            if not cure_verified:
                step_res["ok"] = False
                step_res["action"] = "cure_rejected_by_server"
                step_res["cure_verified"] = False
                step_res["error"] = fail_reason
                step_res["message"] = fail_reason
                step_res["queued_troops"] = 0
                step_res["total_queued_troops"] = total_queued_troops
                step_res["batches_chained"] = batches_chained
                step_res["cross_client_helps_triggered"] = cross_client_helps_triggered
                step_res["popped_modals"] = all_modals
                if all_tips:
                    step_res["in_game_tips"] = _clean_in_game_tips(all_tips)
                chain_history.append({
                    "pass": pass_idx + 1,
                    "action": "cure_rejected_by_server",
                    "dormant": False,
                    "cure_verified": False,
                    "wounded_total": wounded_total,
                    "in_treatment_total": in_treat,
                    "untreated_total": untreated,
                    "queued_troops": 0,
                    "error": fail_reason,
                    "popped_modals": post_modals,
                    "in_game_tips": post_tips,
                })
                step_res["chain_passes"] = len(chain_history)
                step_res["chain_history"] = chain_history
                return step_res

        if queued_now > 0:
            batches_chained += 1
            total_queued_troops += queued_now
            step_res["cure_verified"] = True if not dry_run else None
        if collected_now:
            total_collected += 1
        if step_res.get("help_requested"):
            any_help_requested = True

        # Cross-client auto-help: notify other running accounts to tap Alliance Help immediately
        needs_cross_help = (
            (queued_now > 0 and cure_verified)
            or step_action in (
                "queued_healing",
                "collected_and_queued_healing",
                "started_heal_batch",
                "collected_and_started_batch",
                "requested_help",
                "healing_in_progress",
            )
        )
        helps_this_pass = 0
        if cross_client_help and needs_cross_help and hasattr(cd, "find_running_processes"):
            if not dry_run and (queued_now > 0 or step_action == "requested_help"):
                time.sleep(0.25)
            try:
                other_procs = [
                    p for p in (cd.find_running_processes() or [])
                    if int(p.get("pid") or 0) > 0 and int(p.get("pid") or 0) != int(pid)
                ]
            except Exception:
                other_procs = []
            for other in other_procs:
                other_pid = int(other["pid"])
                try:
                    h_res = run_auto_help(cd, other_pid, {}, cfg, dry_run=dry_run, context=context)
                    if isinstance(h_res, dict) and h_res.get("ok"):
                        if h_res.get("helped_all") or int(h_res.get("ally_help_num") or 0) > 0:
                            helps_this_pass += 1
                            cross_client_helps_triggered += 1
                except Exception:
                    pass

        chain_history.append({
            "pass": pass_idx + 1,
            "action": step_action,
            "dormant": False,
            "cure_verified": cure_verified if queued_now > 0 else None,
            "wounded_total": wounded_total,
            "in_treatment_total": in_treat,
            "untreated_total": untreated,
            "queued_troops": queued_now,
            "collected": collected_now,
            "help_requested": bool(step_res.get("help_requested", False)),
            "speedup_seconds_applied": speedups_now,
            "cross_client_helps": helps_this_pass,
        })

        # In dry-run mode state does not mutate, so never sleep or re-loop redundantly
        if dry_run:
            break

        # Decide whether to pause 1.2s and re-check Queue 3 for immediate next-batch chaining
        should_chain_next = (
            (pass_idx + 1 < max_chain_batches)
            and (
                (queued_now > 0 and cure_verified)
                or helps_this_pass > 0
                or speedups_now > 0
                or (collected_now and untreated > 0)
                or step_action == "requested_help"
            )
        )
        if not should_chain_next:
            break
        time.sleep(1.2)

    if not last_res:
        return {
            "ok": False,
            "task": "hospital_heal",
            "dormant": False,
            "error": "No hospital_heal pass completed",
            "batches_chained": 0,
            "total_queued_troops": 0,
            "cross_client_helps_triggered": 0,
        }

    final_dormant = bool(
        last_res.get("dormant", False)
        and batches_chained == 0
        and total_queued_troops == 0
        and total_collected == 0
        and int(last_res.get("wounded_total") or 0) == 0
        and int(last_res.get("in_treatment_total") or 0) == 0
        and int(last_res.get("untreated_total") or 0) == 0
    )
    last_res["dormant"] = final_dormant
    if final_dormant:
        last_res["action"] = "dormant_no_wounded"
    last_res["batches_chained"] = batches_chained
    last_res["total_queued_troops"] = total_queued_troops
    last_res["queued_troops"] = total_queued_troops if total_queued_troops > 0 else int(last_res.get("queued_troops") or 0)
    last_res["cross_client_helps_triggered"] = cross_client_helps_triggered
    last_res["batches_collected"] = total_collected
    last_res["max_chain_batches"] = max_chain_batches
    last_res["chain_passes"] = len(chain_history)
    last_res["chain_history"] = chain_history
    if any_help_requested:
        last_res["help_requested"] = True
    if all_tips:
        last_res["in_game_tips"] = _clean_in_game_tips(all_tips)
    if all_modals:
        last_res["popped_modals"] = all_modals
    if batches_chained > 0 and not final_dormant:
        last_res["action"] = "started_heal_batch"
        last_res["message"] = (
            f"Queued {total_queued_troops} troops across {batches_chained} batch(es) "
            f"(in_treatment={int(last_res.get('in_treatment_total') or 0)}, "
            f"untreated={int(last_res.get('untreated_total') or 0)}, "
            f"cross_helps={cross_client_helps_triggered})"
        )
    return last_res


action_hospital_heal = run_hospital_heal


def run_alliance_daily(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
    tech_only: bool = False,
) -> dict[str, Any]:
    task_cfg = cfg.get("alliance_daily") or {}
    tech_only_mode = bool(tech_only or task_cfg.get("tech_only", False))
    donate_tech = True if tech_only_mode else bool(task_cfg.get("donate_tech", True))
    use_gold = bool(task_cfg.get("use_gold_donate", False))
    claim_gifts = False if tech_only_mode else bool(task_cfg.get("claim_gifts", True))
    claim_red = False if tech_only_mode else bool(task_cfg.get("claim_red_packets", True))
    claim_tasks = False if tech_only_mode else bool(task_cfg.get("claim_tasks", True))
    help_allies = False if tech_only_mode else bool(task_cfg.get("help_allies", True))
    gifts_lua = _lua_claim_alliance_gifts_block("dryRun", "claimGifts") if claim_gifts else ""

    lua = f"""
local dryRun = {str(dry_run).lower()}
local techOnly = {str(tech_only_mode).lower()}
local donateTech = {str(donate_tech).lower()}
local useGold = {str(use_gold).lower()}
local claimGifts = {str(claim_gifts).lower()}
local claimRed = {str(claim_red).lower()}
local claimTasks = {str(claim_tasks).lower()}
local helpAllies = {str(help_allies).lower()}

local snap = _get_player_snapshot()
local dc = DataCenter
local dismissed = {{}}
local out = {{
  ok = true,
  task = 'alliance_daily',
  tech_only = techOnly,
  dry_run = dryRun,
  ally_help_num = 0,
  helped_all = false,
  gifts_claimed = 0,
  tab1_gifts_claimed = 0,
  tab2_chests_claimed = 0,
  other_gifts_claimed = 0,
  tab1_pending = 0,
  tab2_pending = 0,
  gift_claim_mode = 'none',
  red_packets_claimed = 0,
  tasks_claimed = 0,
  exploit_boxes_claimed = 0,
  tech_donated = 0,
  tech_remaining = 0,
  tech_id = 0,
  popped_modals = dismissed,
  errors = {{}},
  detail_lines = {{}},
  action = 'none',
}}
if not snap.inAlliance then
  out.action = 'skipped_no_alliance'
  table.insert(out.detail_lines, 'Skipped alliance daily: player not in an alliance')
  return _enc(out)
end

-- 0) Ally Help All
local hm = dc and dc.AllianceHelpDataManager
if helpAllies and hm then
  local helpNum = tonumber(_safe_call(function() return hm:GetHelpNum() end, hm.helpNum or 0)) or 0
  local otherCnt = 0
  if hm.otherHelpInfoList then
    for _ in pairs(hm.otherHelpInfoList) do otherCnt = otherCnt + 1 end
  end
  out.ally_help_num = math.max(helpNum, otherCnt)
  if out.ally_help_num > 0 then
    if not dryRun and SFSNetwork and MsgDefines and MsgDefines.AlHelpAll then
      local srvMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
        and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
        or ((tonumber(snap.serverSec or 0) or 0) * 1000)
      local okH, errH = pcall(function() SFSNetwork.SendMessage(MsgDefines.AlHelpAll, srvMs, true) end)
      if not okH then table.insert(out.errors, 'AlHelpAll: ' .. tostring(errH)) end
    end
    out.helped_all = true
    table.insert(out.detail_lines, string.format('Alliance Help: helped %d allies', out.ally_help_num))
  end
end

-- 1) Alliance Gifts (Tab 1 normal gifts + Tab 2 rare/alliance chests, ignoring k5 HQ gate)
local _agmPre = claimGifts and dc and dc.AllianceGiftDataManager
local _gNumPre = _agmPre and _agmPre.GetGiftNum and tonumber(_safe_call(function() return _agmPre:GetGiftNum() end, 0)) or 0
local _hasListPre = type(_agmPre and _agmPre.giftInfoList) == 'table' and next(_agmPre.giftInfoList) ~= nil
if not dryRun and _agmPre and _gNumPre > 0 and not _hasListPre and SFSNetwork and MsgDefines and MsgDefines.AllianceGiftList then
  local okGl, errGl = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllianceGiftList, 0, 200) end)
  if okGl then
    out.needs_gift_wait = true
  else
    table.insert(out.errors, 'AllianceGiftList: ' .. tostring(errGl))
  end
else
{gifts_lua}
end
if out.gifts_claimed > 0 or out.tab1_pending > 0 or out.tab2_pending > 0 then
  table.insert(out.detail_lines, string.format('Alliance Gifts: Tab1 normal=%d (pending=%d), Tab2 chests=%d (pending=%d), other=%d [mode=%s]', out.tab1_gifts_claimed, out.tab1_pending, out.tab2_chests_claimed, out.tab2_pending, out.other_gifts_claimed, tostring(out.gift_claim_mode)))
end

-- 2) Alliance Red Packets
local arp = dc and dc.AllianceRedPacketManager
if claimRed and arp and not _safe_call(function() return arp:IsMaxGetCount() end, false) then
  local list = _safe_call(function() return arp:GetClaimableRedPacketsSortedByTime() end, nil)
    or _safe_call(function() return arp:GetValidRedPacketsSortedByTime() end, {{}}) or {{}}
  for _, rp in ipairs(list) do
    if out.red_packets_claimed >= 10 then break end
    local uuid = tostring((type(rp) == 'table' and (rp.uuid or rp.redPacketId)) or rp or '')
    if uuid ~= '' and (not arp.IsClaimableRedPacketByUuid or _safe_call(function() return arp:IsClaimableRedPacketByUuid(uuid) end, true)) then
      if not dryRun and arp.RequestOpenRedPacketReceive then
        local okR, errR = pcall(function() arp:RequestOpenRedPacketReceive(uuid) end)
        if not okR then table.insert(out.errors, 'RedPacket(' .. uuid .. '): ' .. tostring(errR)) end
      end
      out.red_packets_claimed = out.red_packets_claimed + 1
    end
  end
  if out.red_packets_claimed > 0 then
    table.insert(out.detail_lines, string.format('Red Packets: claimed %d alliance red packets', out.red_packets_claimed))
  end
end

-- 3) Alliance Tasks + Contribute Milestone Boxes
local atm = dc and dc.AllianceTaskManager
if claimTasks and atm and _safe_call(function() return atm:CheckIfAllianceTaskOpen() end, false) then
  local tlist = _safe_call(function() return atm:GetTaskList() end, {{}}) or {{}}
  local claimedIds = {{}}
  for _, t in pairs(tlist) do
    if type(t) == 'table' and tonumber(t.state or 0) == 1 then
      local tid = tonumber(t.id or t.taskId or 0) or 0
      if tid > 0 then
        if not dryRun and SFSNetwork and MsgDefines and MsgDefines.ClaimAllianceTaskReward then
          local okT, errT = pcall(function() SFSNetwork.SendMessage(MsgDefines.ClaimAllianceTaskReward, tid) end)
          if not okT then table.insert(out.errors, 'AllianceTask(' .. tostring(tid) .. '): ' .. tostring(errT)) end
        end
        out.tasks_claimed = out.tasks_claimed + 1
        table.insert(claimedIds, tostring(tid))
      end
    end
  end
  if out.tasks_claimed > 0 then
    table.insert(out.detail_lines, string.format('Alliance Tasks: claimed %d tasks [%s]', out.tasks_claimed, table.concat(claimedIds, ',')))
  end
end

local acm = dc and dc.AlContributeManager
if claimTasks and acm then
  local boxCnt = tonumber(_safe_call(function() return acm:GetUnclaimedBoxCount() end, 0)) or 0
  if boxCnt == 0 and acm.GetUnTakeExploitRewardNum then
    boxCnt = tonumber(_safe_call(function() return acm:GetUnTakeExploitRewardNum() end, 0)) or 0
  end
  if boxCnt > 0 and acm.ClaimBoxReq then
    for idx = 1, math.min(6, boxCnt) do
      if not dryRun then
        local okC, errC = pcall(function() acm:ClaimBoxReq(idx) end)
        if not okC then table.insert(out.errors, 'ContributeBox(' .. tostring(idx) .. '): ' .. tostring(errC)) end
      end
      out.exploit_boxes_claimed = out.exploit_boxes_claimed + 1
    end
    table.insert(out.detail_lines, string.format('Alliance Contribute Boxes: claimed %d boxes', out.exploit_boxes_claimed))
  end
end

-- 4) Alliance Tech Donations (RSS first)
local asc = dc and dc.AllianceScienceDataManager
if donateTech and asc then
  local rest = tonumber(_safe_call(function() return asc:GetResDonateRestCount() end, 0)) or 0
  out.tech_remaining = rest
  if rest > 0 and SFSNetwork and MsgDefines and MsgDefines.AlScienceDonate then
    local nowSec = snap.serverSec or os.time()
    local targetId = tonumber(_safe_call(function() return asc:GetRecommendId() end, 0)) or 0
    local valid = targetId > 0 and _safe_call(function() return asc:CanDonateScience(targetId, nowSec) end, false)
    if not valid and type(asc.alScienceList) == 'table' then
      targetId = 0
      for k, s in pairs(asc.alScienceList) do
        local sid = (type(s) == 'table' and ((tonumber(s.scienceId or 0) or 0) > 0 and tonumber(s.scienceId) or tonumber(s.id or k or 0))) or tonumber(k or 0) or 0
        if sid > 0 and _safe_call(function() return asc:CanDonateScience(sid, nowSec) end, false) then
          targetId = sid
          break
        end
      end
    end
    if targetId > 0 then
      local times = math.min(20, rest)
      out.tech_id = targetId
      for _ = 1, times do
        if not dryRun then
          local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.AlScienceDonate, targetId, 0, nil, nil, nil) end)
          if not okS then table.insert(out.errors, 'AlScienceDonate: ' .. tostring(errS)) break end
        end
        out.tech_donated = out.tech_donated + 1
      end
      out.tech_remaining = math.max(0, rest - out.tech_donated)
      table.insert(out.detail_lines, string.format('Alliance Tech: RSS donated x%d to techId=%d (remaining=%d)', out.tech_donated, targetId, out.tech_remaining))
    end
  elseif useGold and SFSNetwork and MsgDefines and MsgDefines.AlScienceGoldDonate then
    local gRest = tonumber(_safe_call(function() return asc:GetGoldDonateRestCount() end, 0)) or 0
    local rec = tonumber(_safe_call(function() return asc:GetRecommendId() end, 0)) or 0
    if gRest > 0 and gRest < 999999 and rec > 0 then
      if not dryRun then
        local okG, errG = pcall(function() SFSNetwork.SendMessage(MsgDefines.AlScienceGoldDonate, rec, nil, nil, nil) end)
        if not okG then table.insert(out.errors, 'AlScienceGoldDonate: ' .. tostring(errG)) end
      end
      out.tech_id = rec
      out.tech_donated = 1
      table.insert(out.detail_lines, string.format('Alliance Tech: gold donated to techId=%d', rec))
    end
  end
end

if (out.ally_help_num + out.gifts_claimed + out.red_packets_claimed + out.tasks_claimed + out.exploit_boxes_claimed + out.tech_donated) > 0 then
  out.action = (techOnly and out.tech_donated > 0) and 'donated_tech' or 'completed'
  if not dryRun then
    pcall(function()
      local d2 = _dismiss_modal_dialogs() or {{}}
      for _, w in ipairs(d2) do table.insert(out.popped_modals, w) end
    end)
  end
else
  if techOnly then
    table.insert(out.detail_lines, string.format('Alliance Tech: 0 RSS donations available (rest=%d)', out.tech_remaining))
  else
    table.insert(out.detail_lines, 'No pending alliance gifts, red packets, tasks, or tech donations')
  end
end
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=12.0)
    if not dry_run and res.get("ok") and res.get("needs_gift_wait"):
        res = _run_alliance_gifts_followup(cd, pid, dry_run, res)
    return res


def run_research_queue(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("research_queue") or {}
    prefer_rec = bool(task_cfg.get("prefer_recommended", True))
    call_help = bool(task_cfg.get("call_alliance_help", True))
    use_free = bool(task_cfg.get("use_free_speed", True))
    priority_tabs = task_cfg.get("priority_tabs") or [5, 1, 2, 3, 4]
    tabs_lua = "{" + ", ".join(str(int(x)) for x in priority_tabs) + "}"

    lua = _LUA_QUEUE_HELP_HELPER + f"""
local dryRun = {str(dry_run).lower()}
local preferRec = {str(prefer_rec).lower()}
local callHelp = {str(call_help).lower()}
local useFree = {str(use_free).lower()}
local priorityTabs = {tabs_lua}

local snap = _get_player_snapshot()
local dc = DataCenter
local sm = dc and dc.ScienceManager
local qm = dc and dc.QueueDataManager
local out = {{
  ok = true,
  task = 'research_queue',
  dry_run = dryRun,
  queues_checked = 0,
  collected = 0,
  help_requested = 0,
  free_sped = 0,
  started = {{}},
  action = 'none',
}}
if not sm or not qm then
  out.ok = false
  out.error = 'ScienceManager or QueueDataManager unavailable'
  return _enc(out)
end

local nowMs = (snap.serverSec or 0) * 1000
local qType = (NewQueueType and tonumber(NewQueueType.Science)) or 6
local qs = qm.GetAllQueueByType and _safe_call(function() return qm:GetAllQueueByType(qType) end, {{}}) or {{}}
local freeQueues = {{}}

for _, q in ipairs(qs) do
  out.queues_checked = out.queues_checked + 1
  local st = _collect_or_help_queue(qm, q, nowMs, dryRun,
    function() out.collected = out.collected + 1 end,
    function() if callHelp then out.help_requested = out.help_requested + 1 end end
  )
  local bUuid = tonumber(q.funcUuid or 0) or 0
  if st == 'finished' or st == 'free' then
    if bUuid > 0 then table.insert(freeQueues, bUuid) end
  elseif useFree and bUuid > 0 and qm.GetScienceFreeByBuildUuid and MsgDefines and MsgDefines.FreeSpeedQueue then
    local freeList = _safe_call(function() return qm:GetScienceFreeByBuildUuid(bUuid) end, {{}}) or {{}}
    if #freeList > 0 then
      local qUuids = {{}}
      for _, fq in ipairs(freeList) do if fq and fq.uuid then table.insert(qUuids, fq.uuid) end end
      if #qUuids > 0 then
        if not dryRun and SFSNetwork then
          pcall(function() SFSNetwork.SendMessage(MsgDefines.FreeSpeedQueue, {{queueList = qUuids}}) end)
        end
        out.free_sped = out.free_sped + #qUuids
      end
    end
  end
end

local function _pick_science(bUuid)
  if preferRec and sm.GetRecommendScienceId then
    local rid = tonumber(_safe_call(function() return sm:GetRecommendScienceId(bUuid) end, 0)) or 0
    if rid > 0 and not _safe_call(function() return sm:IsScienceResearching(rid) end, false) then
      local curLv = tonumber(_safe_call(function() return sm:GetScienceLevel(rid) end, 0)) or 0
      if not sm.IsResearchableScience or _safe_call(function() return sm:IsResearchableScience(rid, curLv + 1) end, true) then
        return rid
      end
    end
  end
  local stm = dc and dc.ScienceTemplateManager
  if stm and stm.GetLineListByTab then
    for _, tabId in ipairs(priorityTabs) do
      local lines = _safe_call(function() return stm:GetLineListByTab(tabId) end, nil)
      if type(lines) == 'table' then
        for _, sidRaw in pairs(lines) do
          local sid = tonumber((type(sidRaw) == 'table' and (sidRaw.id or sidRaw.scienceId)) or sidRaw or 0) or 0
          if sid > 0 and not _safe_call(function() return sm:IsScienceResearching(sid) end, false) then
            local curLv = tonumber(_safe_call(function() return sm:GetScienceLevel(sid) end, 0)) or 0
            local maxLv = tonumber(_safe_call(function() return sm:GetScienceMaxLevel(sid) end, 0)) or 0
            if curLv < maxLv and _safe_call(function() return sm:IsUnlockScience(sid) end, false)
               and _safe_call(function() return sm:IsResearchableScience(sid, curLv + 1) end, false) then
              return sid
            end
          end
        end
      end
    end
  end
  return 0
end

for _, bUuid in ipairs(freeQueues) do
  local sid = _pick_science(bUuid)
  if sid > 0 and SFSNetwork and MsgDefines and MsgDefines.ScienceResearchNew then
    if not dryRun then
      pcall(function()
        SFSNetwork.SendMessage(MsgDefines.ScienceResearchNew, {{
          itemId = sid, useGold = 0, bUuid = bUuid, robotUuid = 0, itemIDs = '',
        }})
      end)
    end
    table.insert(out.started, {{buildUuid = bUuid, scienceId = sid}})
  end
end

if #out.started > 0 then
  out.action = 'started_research'
elseif out.collected > 0 or out.help_requested > 0 or out.free_sped > 0 then
  out.action = 'updated_queues'
elseif out.queues_checked > 0 then
  out.action = 'all_queues_busy'
end
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=10.0)


def _lua_trigger_pve_skip_snippet() -> str:
    """Shared verified Lua helper to skip an active PVE battle safely.
    Matches exact UIPVESceneView:OnShowResult() & PveActorMgr:ShowResult() preconditions:
      1) Wait until PveActorMgr.startPlay == true and not onPreStart (never poison forceShowResultFlag early!)
      2) Call ForceShowResult() -> ShowResult(true) -> ForceShowResultFlag() in that exact order!
      3) Works in BOTH PVE scenes and Area Exploration (where SceneManager:IsInPVE() can be false while UIPVEScene & PveActorMgr.startPlay are active).
    """
    return """
local function _trigger_active_pve_skip()
  local skipped = false
  local method = 'none'
  local uim = UIManager and (type(UIManager.GetInstance) == 'function' and UIManager:GetInstance() or UIManager)
  local pveWin = nil
  if uim then
    if uim.GetWindow then
      pcall(function() pveWin = uim:GetWindow('UIPVEScene') end)
    end
    if not pveWin and uim.windows and type(uim.windows) == 'table' then
      pveWin = uim.windows['UIPVEScene']
    end
  end
  local pveView = pveWin and (pveWin.View or pveWin.view) or pveWin
  local inPveView = (pveView ~= nil and pveView.activeSelf == true)
  local isMainLvl = (DataCenter and DataCenter.BattleLevel and DataCenter.BattleLevel.IsMainLevel
    and _safe_call(function() return DataCenter.BattleLevel:IsMainLevel() end, false)) and true or false
  local inRealPve = (SceneManager and SceneManager.IsInPVE
    and _safe_call(function() return SceneManager:IsInPVE() end, false)) and true or false
  if isMainLvl then inRealPve = false end
  local hasBarrelLogic = (DataCenter and DataCenter.LWBattleManager and DataCenter.LWBattleManager.logic ~= nil)
  local actorCls = PveActorMgr or package.loaded['Scene.BattlePveModule.PveActorMgr1']
  local actorMgr = (actorCls and actorCls.GetInstance) and _safe_call(function() return actorCls:GetInstance() end, nil) or nil
  local actorPlaying = (actorMgr ~= nil and actorMgr.startPlay == true and not actorMgr.onPreStart and not actorMgr.showResult)
  if not inPveView and not inRealPve and not hasBarrelLogic and not actorPlaying then
    return false, 'not_in_pve'
  end
  local lp = pveView and pveView.levelParam
  -- 1) Barrel / Parkour stages: LWBattleManager:Skip() / OnSkipPVE() / CarBattlePveManager:SkipLevel()
  if (hasBarrelLogic or (lp and lp.isBarrel)) then
    if DataCenter and DataCenter.LWBattleManager and DataCenter.LWBattleManager.Skip then
      local okB = pcall(function()
        if inPveView and type(pveView.OnSkipPVE) == 'function' and lp and lp.isBarrel then
          pveView:OnSkipPVE()
        else
          DataCenter.LWBattleManager:Skip(function()
            if pveView and pveView.OnHomeClick then pcall(function() pveView:OnHomeClick() end) end
          end)
        end
      end)
      if okB then
        skipped = true
        method = 'LWBattleManager.Skip'
      end
    end
    if not skipped and DataCenter and DataCenter.CarBattlePveManager and DataCenter.CarBattlePveManager.SkipLevel then
      local okC = pcall(function() DataCenter.CarBattlePveManager:SkipLevel() end)
      if okC then
        skipped = true
        method = 'CarBattlePveManager.SkipLevel'
      end
    end
  end
  -- 2) Non-barrel PVE playback skip (Area Exploration, Hero Battlefield, etc.):
  --    ONLY fire once PveActorMgr.startPlay == true and not onPreStart!
  --    CRITICAL: ShowResult(true) MUST run BEFORE ForceShowResultFlag() (otherwise ShowResult aborts immediately!).
  if not skipped and (inPveView or inRealPve or actorPlaying) then
    if actorMgr and actorMgr.showResult == true then
      return true, 'already_shown_result'
    end
    if not actorPlaying then
      return false, 'waiting_start_play'
    end
    -- Clear any prematurely poisoned flag before calling ShowResult
    if actorMgr.forceShowResultFlag == true and actorMgr.showResult ~= true then
      pcall(function() actorMgr.forceShowResultFlag = false end)
    end
    if inPveView and type(pveView.OnShowResult) == 'function' and pveView.finishLockOpen ~= false then
      pcall(function() pveView:OnShowResult() end)
      if actorMgr.showResult == true then
        skipped = true
        method = 'UIPVEScene.OnShowResult'
      end
    end
    if not skipped and actorMgr.ShowResult then
      pcall(function()
        if actorMgr.forceShowResultFlag == true and actorMgr.showResult ~= true then
          actorMgr.forceShowResultFlag = false
        end
        if actorMgr.ForceShowResult then actorMgr:ForceShowResult() end
        actorMgr:ShowResult(true)
        if actorMgr.showResult == true and actorMgr.ForceShowResultFlag then
          actorMgr:ForceShowResultFlag()
        end
      end)
      if actorMgr.showResult == true then
        skipped = true
        method = 'PveActorMgr.ShowResult'
      end
    end
  end
  return skipped, method
end
"""


def _ensure_exited_pve_cleanly(cd: Any, pid: int, only_if_stuck: bool = False) -> dict[str, Any]:
    """Safely back out of an active PVE result/scene using ONLY the game's real UI button callbacks (never DestroyWindow or raw SceneManager scene resets)."""
    lua_chk = f"""
local onlyIfStuck = {str(only_if_stuck).lower()}
local dc = DataCenter
local bl = dc and dc.BattleLevel
local um = UIManager and (type(UIManager.GetInstance) == 'function' and UIManager:GetInstance() or UIManager)
local inPve = (SceneManager and SceneManager.IsInPVE and _safe_call(function() return SceneManager:IsInPVE() end, false)) and true or false
local isMain = (bl and bl.IsMainLevel and _safe_call(function() return bl:IsMainLevel() end, false)) and true or false
local hasBarrel = (dc and dc.LWBattleManager and dc.LWBattleManager.logic ~= nil)
local resultWinNames = {{
  'UIPVEResult', 'UIParkourBattleWin', 'UIPveBattleWin', 'UIPveBattleLose',
  'UITowerupBattleLose', 'UIParkourBattleLose', 'UIPVEScene', 'UIJeepAdventureMain',
}}
local pveWinsOpen = false
if um then
  for _, wn in ipairs(resultWinNames) do
    local w = um.GetWindow and _safe_call(function() return um:GetWindow(wn) end, nil)
    if w and ((w.View and w.View.activeSelf) or w.activeSelf) then
      pveWinsOpen = true
      break
    end
  end
end
if onlyIfStuck and (not inPve) and (not hasBarrel) and (not pveWinsOpen) then
  return _enc({{ok = true, needed = false, inPve = false, isMain = isMain}})
end

-- Use ONLY real UI callbacks / LWBattleManager:Exit; NEVER DestroyWindow, CloseAllWindow, or raw SceneManager.ChangeToCity/ChangeToMainLevel
local clicked = {{}}
if um then
  for _, wn in ipairs(resultWinNames) do
    local w = um.GetWindow and _safe_call(function() return um:GetWindow(wn) end, nil)
    if w and w.View and w.View.activeSelf then
      if type(w.View.OnBtnBackClick) == 'function' then
        pcall(function() w.View:OnBtnBackClick() end)
        table.insert(clicked, wn .. ':OnBtnBackClick')
      elseif type(w.View.OnHomeClick) == 'function' then
        pcall(function() w.View:OnHomeClick() end)
        table.insert(clicked, wn .. ':OnHomeClick')
      elseif type(w.View.OnCloseBtn) == 'function' then
        pcall(function() w.View:OnCloseBtn() end)
        table.insert(clicked, wn .. ':OnCloseBtn')
      end
    end
  end
end
if hasBarrel and dc.LWBattleManager.Exit then
  pcall(function() dc.LWBattleManager:Exit(nil, 'win') end)
  table.insert(clicked, 'LWBattleManager:Exit')
end
return _enc({{ok = true, needed = true, wasInPve = inPve, wasBarrel = hasBarrel, clicked = clicked}})
"""
    return _eval_json(cd, pid, lua_chk, timeout=8.0)


def _skip_active_pve_after_delay(cd: Any, pid: int, delay_sec: float = 0.45) -> dict[str, Any]:
    """Wait briefly for PVE transition, invoke verified prod-safe skip, and verify clean exit."""
    if delay_sec > 0:
        time.sleep(delay_sec)
    skip_fn = _lua_trigger_pve_skip_snippet()
    lua = f"""
{skip_fn}
local ok, how = _trigger_active_pve_skip()
return _enc({{ok = true, skipped = ok, method = how}})
"""
    try:
        return _eval_json(cd, pid, lua, timeout=6.0)
    except Exception as exc:
        return {"ok": False, "skipped": False, "error": str(exc)}


def run_radar_events(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("radar_events") or {}
    claim_fin = bool(task_cfg.get("claim_finished", True))
    auto_dispatch = bool(task_cfg.get("auto_dispatch", True))
    max_dispatch = int(task_cfg.get("max_dispatches_per_cycle", 20) or 20)
    reserve = int(cfg.get("formation_reserve", 0) or 0)
    min_stamina = int(cfg.get("min_stamina", 60) or 60)

    if auto_dispatch and not dry_run:
        ensure_world_scene(cd, pid, wait_seconds=2.2)

    # Phase 0 (Separate pre-pass): Top-Left Lady Walkie-Talkie (30424) + Radar Summon (SU_DetectSummon) + Level Reward + Laura Milestone
    # Runs BEFORE checking freeSquads and gives server 0.65s to push newly spawned radar pins!
    lua_stage0 = f"""
local dryRun = {str(dry_run).lower()}
local dc = DataCenter
local rcm = dc and dc.RadarCenterDataManager
local out = {{
  ok = true,
  lady_skill_used = 0,
  scans_remaining = 0,
  radar_summon_triggered = false,
  level_reward_claimed = false,
  laura_reward_claimed = false,
  detect_level = 0,
  reward_level = 0,
  summon_level = -1,
  spawned_refresh = false,
  errors = {{}},
  detail_lines = {{}},
}}
if not rcm then
  out.ok = false
  out.error = 'RadarCenterDataManager unavailable'
  return _enc(out)
end

local detLv = (rcm.GetDetectInfoLevel and tonumber(_safe_call(function() return rcm:GetDetectInfoLevel() end, 0))) or 0
local rewLv = (rcm.GetDetectInfoRewardLevel and tonumber(_safe_call(function() return rcm:GetDetectInfoRewardLevel() end, 0))) or 0
local sumLv = (rcm.GetSummonLevel and tonumber(_safe_call(function() return rcm:GetSummonLevel() end, -1))) or -1
out.detect_level = detLv
out.reward_level = rewLv
out.summon_level = sumLv

-- 0a) Top-Left Lady Walkie-Talkie Scan (GAME_EFFECT_30424)
local hesm = dc and dc.HeroEffectSkillManager
local ladyEffectId = (EffectDefine and EffectDefine.GAME_EFFECT_30424) or 30424
local restNum = tonumber((hesm and hesm.GetRestNum and _safe_call(function() return hesm:GetRestNum(ladyEffectId) end, 0)) or 0) or 0
out.scans_remaining = math.floor(restNum)
if hesm and hesm.CanUse and _safe_call(function() return hesm:CanUse(ladyEffectId) end, false) then
  local useCharges = restNum > 0 and math.floor(restNum) or 1
  if not dryRun then
    local okL, errL = pcall(function()
      if hesm.Use then
        hesm:Use(ladyEffectId)
      elseif SFSNetwork and MsgDefines and MsgDefines.UseHeroEffectSkill then
        SFSNetwork.SendMessage(MsgDefines.UseHeroEffectSkill, ladyEffectId, useCharges)
      end
    end)
    if not okL then table.insert(out.errors, 'LadySkill(30424): ' .. tostring(errL)) end
  end
  out.lady_skill_used = useCharges
  out.scans_remaining = 0
  out.spawned_refresh = true
  table.insert(out.detail_lines, string.format('Top-Left Lady Walkie-Talkie: activated scan skill effectId=%d (charges=%d)', ladyEffectId, useCharges))
end

-- 0b) Radar Level Summon Bubble (SU_DetectSummon)
if sumLv >= 0 and detLv > sumLv and SFSNetwork and MsgDefines and MsgDefines.SU_DetectSummon then
  if not dryRun then
    local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.SU_DetectSummon) end)
    if not okS then table.insert(out.errors, 'SU_DetectSummon: ' .. tostring(errS)) end
  end
  out.radar_summon_triggered = true
  out.spawned_refresh = true
  table.insert(out.detail_lines, string.format('Radar Summon: triggered SU_DetectSummon (%d -> %d)', sumLv, detLv))
end

-- 0c) Radar Level-Up Reward Chest (ReceiveDetectLevelReward) - gate strictly on actual upgrade/pending flag!
local dInfo = rcm.GetDetectInfo and _safe_call(function() return rcm:GetDetectInfo() end, nil) or nil
local canUp = (rcm.CheckNeedShowUpLevelPanel and _safe_call(function() return rcm:CheckNeedShowUpLevelPanel() end, false))
  or (type(dInfo) == 'table' and dInfo.upgrade == true)
if canUp and SFSNetwork and MsgDefines and MsgDefines.ReceiveDetectLevelReward then
  if not dryRun then
    local okR, errR = pcall(function() SFSNetwork.SendMessage(MsgDefines.ReceiveDetectLevelReward) end)
    if not okR then table.insert(out.errors, 'ReceiveDetectLevelReward: ' .. tostring(errR)) end
  end
  out.level_reward_claimed = true
  out.spawned_refresh = true
  table.insert(out.detail_lines, string.format('Radar Level Reward: claimed ReceiveDetectLevelReward (rewardLv=%d -> detectLv=%d)', rewLv, detLv))
end

-- 0d) Laura Milestone Reward
if rcm.GetLauraData and SFSNetwork and MsgDefines and MsgDefines.DetectEventLauraRewardReceive then
  local lData = _safe_call(function() return rcm:GetLauraData() end, nil)
  if type(lData) == 'table' then
    local ord = tonumber(lData.lauraOrder or 0) or 0
    local oMax = tonumber(lData.lauraOrderMax or 0) or 0
    if oMax > 0 and ord >= oMax then
      if not dryRun then
        local okLR, errLR = pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventLauraRewardReceive) end)
        if not okLR then table.insert(out.errors, 'DetectEventLauraRewardReceive: ' .. tostring(errLR)) end
      end
      out.laura_reward_claimed = true
      table.insert(out.detail_lines, string.format('Laura Milestone Reward: claimed (%d/%d)', ord, oMax))
    end
  end
end

return _enc(out)
"""
    st0 = _eval_json(cd, pid, lua_stage0, timeout=10.0)
    if not isinstance(st0, dict) or not st0.get("ok"):
        return st0 if isinstance(st0, dict) else {"ok": False, "task": "radar_events", "error": "RadarCenterDataManager unavailable"}
    if st0.get("spawned_refresh") and not dry_run:
        time.sleep(0.75)

    # Phase 1 + 2 + 3: Claim Finished -> Instant Auto-Finish -> Process ALL Event Types (Non-March first, then March-Based)
    skip_fn = _lua_trigger_pve_skip_snippet()
    lua = f"""
{skip_fn}
local dryRun = {str(dry_run).lower()}
local claimFin = {str(claim_fin).lower()}
local autoDispatch = {str(auto_dispatch).lower()}
local maxDispatch = {max_dispatch}
local reserve = {reserve}
local minStamina = {min_stamina}

local snap = _get_player_snapshot()
local dc = DataCenter
local rcm = dc and dc.RadarCenterDataManager
local out = {{
  ok = true,
  task = 'radar_events',
  dry_run = dryRun,
  total_events = 0,
  free_formations = tonumber(snap.freeFormations or 0) or 0,
  unlock_formations = tonumber(snap.unlockFormations or 0) or 0,
  auto_finished_count = 0,
  claimed_uuids = {{}},
  dispatched = {{}},
  events_detail = {{}},
  pve_triggered = 0,
  pve_skipped = 0,
  popped_modals = {{}},
  errors = {{}},
  detail_lines = {{}},
  action = 'none',
}}
if not rcm then
  out.ok = false
  out.error = 'RadarCenterDataManager unavailable'
  table.insert(out.detail_lines, 'RadarCenterDataManager unavailable')
  return _enc(out)
end

local function _loc(k)
  if k == nil then return '' end
  local ks = tostring(k)
  if ks == '' or ks == '0' then return '' end
  if Localization and Localization.GetString then
    local ok, s = pcall(function() return Localization:GetString(ks) end)
    if ok and type(s) == 'string' and s ~= '' and s ~= ks then return s end
  end
  return ''
end

local nowMs = (UITimeManager and UITimeManager.GetInstance and UITimeManager:GetInstance().GetServerTime
  and math.floor(tonumber(UITimeManager:GetInstance():GetServerTime()) or 0))
  or ((tonumber(snap.serverSec or 0) or 0) * 1000)
local events = type(rcm.events) == 'table' and rcm.events or {{}}

local function _ev_label(t)
  local map = {{
    [1] = 'Special', [2] = 'Normal/Mutant', [5] = 'RadarRally', [6] = 'PickGarbage',
    [7] = 'RadarPVE', [8] = 'Boss/Skull', [9] = 'HeroTrial', [10] = 'SpecialOps',
    [11] = 'SweepField', [12] = 'OccupyField', [13] = 'GuidePVE', [14] = 'GuideMonster',
    [16] = 'TalkCity', [17] = 'TalkWorld', [18] = 'Plot', [19] = 'HelpAllies',
    [20] = 'Rescue', [21] = 'Gather/Pickaxe', [22] = 'AttackNPCHQ', [23] = 'TreasureDig',
    [24] = 'SevenDay', [25] = 'Doomwalker', [26] = 'Parkour', [27] = 'OverlordRescue',
    [28] = 'OverlordBattle', [29] = 'OverlordHunter',
  }}
  return map[t] or ('Type' .. tostring(t))
end

-- Stage 1: Claim all completed radar rewards (state == 1) - NEVER gated on freeSquads!
local detMgr = dc and dc.DetectEventTemplateManager
local finUuids = {{}}
for k, ev in pairs(events) do
  if type(ev) == 'table' then
    out.total_events = out.total_events + 1
    if claimFin and tonumber(ev.state or 0) == 1 then
      local u = ev.uuid or k
      local tmpl = detMgr and _safe_call(function() return detMgr:GetDetectEventTemplate(tonumber(ev.eventId) or ev.eventId) end, nil)
      local evType = tonumber((tmpl and tmpl.type) or ev.type or 0) or 0
      table.insert(finUuids, tonumber(u) or u)
      table.insert(out.events_detail, {{
        uuid = tostring(u), eventId = tostring(ev.eventId or ''), type = evType, evType = evType,
        category = _ev_label(evType), pointId = tonumber(ev.pointId or 0) or 0,
        quality = tonumber(ev.quality or (tmpl and tmpl.quality) or 0) or 0,
        state = 1, stage = 'claim', action = 'claimed_reward', action_taken = 'claimed_reward',
      }})
    end
  end
end
if claimFin and #finUuids > 0 and SFSNetwork and MsgDefines then
  if not dryRun then
    if MsgDefines.BatchDetectEventRewardReceive then
      local okB, errB = pcall(function() SFSNetwork.SendMessage(MsgDefines.BatchDetectEventRewardReceive, finUuids) end)
      if not okB then table.insert(out.errors, 'BatchDetectEventRewardReceive: ' .. tostring(errB)) end
    elseif MsgDefines.DetectEventRewardReceive then
      for _, u in ipairs(finUuids) do
        local okR, errR = pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventRewardReceive, tonumber(u) or u, false) end)
        if not okR then table.insert(out.errors, 'DetectEventRewardReceive(' .. tostring(u) .. '): ' .. tostring(errR)) end
      end
    end
  end
  for _, u in ipairs(finUuids) do table.insert(out.claimed_uuids, tostring(u)) end
  table.insert(out.detail_lines, string.format('Claimed %d completed radar reward(s) [%s]', #out.claimed_uuids, table.concat(out.claimed_uuids, ',')))
end

if autoDispatch and (maxDispatch == 0 or maxDispatch > 0) then
  local curStamina = tonumber(snap.stamina or 0) or 0
  local freeForms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, not dryRun)
  out.free_formations = #freeForms
  local mu = package.loaded['SlgEngine.Util.MarchUtil.MarchUtil'] or package.loaded['Util.MarchUtil_SLG'] or MarchUtil

  local pveType = DetectEventType and DetectEventType.DetectEventPVE or 7
  local parkourType = DetectEventType and DetectEventType.RewardParkour or 26
  local heroTrial = DetectEventType and DetectEventType.HeroTrial or 9
  local guidePveType = DetectEventType and DetectEventType.GUIDE_PVE_LEVEL or 13
  local specialOpsType = DetectEventType and DetectEventType.SPECIAL_OPS or 10
  local helpType = DetectEventType and DetectEventType.HELP or 19
  local rescueType = DetectEventType and DetectEventType.RESCUE or 20
  local overlordRescueType = DetectEventType and DetectEventType.OVERLORD_RESCUE or 27
  local garbageType = DetectEventType and DetectEventType.DetectEventPickGarbage or 6
  local treasureType = DetectEventType and DetectEventType.ALLIANCE_TREASURE or 23
  local collectType = DetectEventType and DetectEventType.COLLECT or 21
  local npcCityType = DetectEventType and DetectEventType.NPC_CITY or 22
  local bossType = DetectEventType and DetectEventType.DetectEventTypeBoss or 8
  local talkCityType = DetectEventType and DetectEventType.DetectTalkCity or 16
  local talkWorldType = DetectEventType and DetectEventType.DetectTalkWorld or 17
  local plotType = DetectEventType and DetectEventType.PLOT or 18

  -- Stage 2: Fast-path Instant Auto-Finish for {{6=PickGarbage, 19=HELP, 20=RESCUE, 27=OVERLORD_RESCUE}} - works even with freeSquads == 0 AND without UIDetectEvent open!
  local autoFinishedUuids = {{}}
  local uim = UIManager and (type(UIManager.GetInstance) == 'function' and UIManager:GetInstance() or UIManager)
  local rWinCfg = uim and uim.GetWindowConfig and _safe_call(function() return uim:GetWindowConfig('UIDetectEvent') end, nil)
  local rCtrl = rWinCfg and rWinCfg.Ctrl
  local didAutoFinish = false
  if rCtrl and rCtrl.GetAutoCompleteTaskNumAndCost and rCtrl.AutoCompleteTask then
    local ok_ac, aCount, aCost, aUuids = pcall(function() return rCtrl:GetAutoCompleteTaskNumAndCost() end)
    if ok_ac and aCount and aCount > 0 and type(aUuids) == 'table' and #aUuids > 0 then
      if curStamina - (aCost or 0) >= minStamina then
        if not dryRun then
          local okAF, errAF = pcall(function() rCtrl:AutoCompleteTask(aUuids) end)
          if not okAF then table.insert(out.errors, 'AutoCompleteTask: ' .. tostring(errAF)) end
        end
        curStamina = curStamina - (aCost or 0)
        didAutoFinish = true
        out.auto_finished_count = #aUuids
        for _, u in ipairs(aUuids) do
          autoFinishedUuids[tostring(u)] = true
          table.insert(out.dispatched, {{uuid = tostring(u), mode = 'auto_finish_instant', cost = math.floor((aCost or 0) / math.max(1, #aUuids))}})
          table.insert(out.events_detail, {{uuid = tostring(u), stage = 'auto_finish', action = 'auto_finish_instant', action_taken = 'auto_finish_instant'}})
        end
        table.insert(out.detail_lines, string.format('Auto-Finish (Ctrl): completed %d radar task(s) instantly (stamina cost=%d)', #aUuids, tonumber(aCost or 0) or 0))
      end
    end
  end
  -- Direct AutoFinishDetectEvent fallback when GAME_EFFECT_50001 is unlocked and UIDetectEvent controller isn't loaded
  if not didAutoFinish and SFSNetwork and MsgDefines and MsgDefines.AutoFinishDetectEvent then
    local canAutoEff = (LuaEntry and LuaEntry.Effect and LuaEntry.Effect.GetGameEffect and EffectDefine and EffectDefine.GAME_EFFECT_50001
      and tonumber(_safe_call(function() return LuaEntry.Effect:GetGameEffect(EffectDefine.GAME_EFFECT_50001) end, 0) or 0) or 0) > 0
    if canAutoEff then
      local afUuids, afCost = {{}}, 0
      for k, ev in pairs(events) do
        if type(ev) == 'table' and tonumber(ev.state or -1) == 0 then
          local tmpl = detMgr and _safe_call(function() return detMgr:GetDetectEventTemplate(tonumber(ev.eventId) or ev.eventId) end, nil)
          local et = tonumber((tmpl and tmpl.type) or ev.type or 0) or 0
          if et == garbageType or et == helpType or et == rescueType or et == overlordRescueType then
            local u = ev.uuid or k
            local c = (rcm.GetDetectCostNum and tonumber(_safe_call(function() return rcm:GetDetectCostNum(et, u) end, 10))) or 10
            table.insert(afUuids, tonumber(u) or u)
            afCost = afCost + c
          end
        end
      end
      if #afUuids > 0 and (curStamina - afCost >= minStamina) then
        if not dryRun then
          local okAF, errAF = pcall(function() SFSNetwork.SendMessage(MsgDefines.AutoFinishDetectEvent, afUuids) end)
          if not okAF then table.insert(out.errors, 'AutoFinishDetectEvent: ' .. tostring(errAF)) end
        end
        curStamina = curStamina - afCost
        out.auto_finished_count = #afUuids
        for _, u in ipairs(afUuids) do
          autoFinishedUuids[tostring(u)] = true
          table.insert(out.dispatched, {{uuid = tostring(u), mode = 'auto_finish_direct', cost = math.floor(afCost / math.max(1, #afUuids))}})
          table.insert(out.events_detail, {{uuid = tostring(u), stage = 'auto_finish', action = 'auto_finish_direct', action_taken = 'auto_finish_direct'}})
        end
        table.insert(out.detail_lines, string.format('Auto-Finish (Direct): completed %d radar task(s) instantly (stamina cost=%d)', #afUuids, afCost))
      end
    end
  end

  -- Stage 3: Collect ALL pending (state == 0) events & sort non-march tasks BEFORE march-based tasks!
  -- prio 1 = non-march instant/doing (Help, Rescue, PickGarbage, Treasure, Talk)
  -- prio 2 = non-march PVE / Exploration / SpecialOps / Parkour (NEVER gated on freeSquads!)
  -- prio 3 = march-based Gather/Pickaxes
  -- prio 4 = march-based Attack NPC HQ / Boss / Mutant
  local pendingList = {{}}
  for k, ev in pairs(events) do
    if type(ev) == 'table' and tonumber(ev.state or -1) == 0 and not autoFinishedUuids[tostring(ev.uuid or k)] then
      local evUuid = ev.uuid or k
      local startT = tonumber(ev.startTime or 0) or 0
      local endT = tonumber(ev.endTime or 0) or 0
      local doing = rcm.IsDetectEventDoing and _safe_call(function() return rcm:IsDetectEventDoing(evUuid, false) end, false) or false
      local tmpl = detMgr and _safe_call(function() return detMgr:GetDetectEventTemplate(tonumber(ev.eventId) or ev.eventId) end, nil)
      local evType = tonumber((tmpl and tmpl.type) or ev.type or 0) or 0
      local cost = tonumber((rcm.GetDetectCostNum and _safe_call(function() return rcm:GetDetectCostNum(evType, evUuid) end, nil))
        or (tmpl and (tmpl.cost or tmpl.stamina)) or ev.cost or 0) or 0
      -- CRITICAL FIX: SPECIAL_OPS (10) & permanent pins have endTime == startTime (in the past) and NEVER expire!
      local active = (evType == specialOpsType) or (endT == 0) or (endT == startT) or (nowMs == 0) or (endT > nowMs)
      local ptId = tonumber(ev.pointId or 0) or 0
      if ptId <= 0 and evType == helpType and type(ev.helpInfo) == 'table' then
        ptId = tonumber(ev.helpInfo.pointId or 0) or 0
      end
      local prio = 4
      if doing or evType == helpType or evType == rescueType or evType == overlordRescueType or evType == garbageType or evType == treasureType or evType == talkCityType or evType == talkWorldType or evType == plotType then
        prio = 1
      elseif evType == pveType or evType == heroTrial or evType == guidePveType or evType == specialOpsType or evType == parkourType then
        prio = 2
      elseif evType == collectType or evType == 11 or evType == 12 then
        prio = 3
      end
      local locName = (tmpl and _loc(tmpl.name)) or ''
      if locName == '' and type(tmpl and tmpl.seasonInfo) == 'table' and tmpl.seasonInfo[1] and tmpl.seasonInfo[1].name then
        locName = tostring(tmpl.seasonInfo[1].name)
      end
      table.insert(pendingList, {{
        key = k, ev = ev, uuid = evUuid, startT = startT, endT = endT, active = active, doing = doing,
        tmpl = tmpl, cost = cost, evType = evType, pointId = ptId, prio = prio, locName = locName,
        quality = tonumber(ev.quality or (tmpl and tmpl.quality) or 0) or 0,
      }})
    end
  end
  table.sort(pendingList, function(a, b)
    if a.prio ~= b.prio then return a.prio < b.prio end
    if a.quality ~= b.quality then return a.quality > b.quality end
    return tostring(a.uuid) < tostring(b.uuid)
  end)

  local fIdx = 1
  local pveEnteredThisPass = false
  local tcm = dc and dc.TowerClimbingManager
  local wpm = dc and dc.WorldPointManager

  for _, item in ipairs(pendingList) do
    local ev = item.ev
    local evUuid = item.uuid
    local endT = item.endT
    local evType = item.evType
    local cost = item.cost
    local ptId = item.pointId
    local tmpl = item.tmpl
    local label = _ev_label(evType)
    local nameTag = (item.locName ~= '' and (' "' .. item.locName .. '"') or '')
    local detailRec = {{
      uuid = tostring(evUuid), eventId = tostring(ev.eventId or ''), type = evType, evType = evType,
      label = label, category = label, name = item.locName, pointId = ptId, quality = item.quality,
      cost = cost, stage = item.prio, state = tonumber(ev.state or 0) or 0,
    }}

    if maxDispatch > 0 and #out.dispatched >= maxDispatch then
      detailRec.action = 'skipped_max_dispatch'
      detailRec.action_taken = 'skipped_max_dispatch'
      table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): skipped (max_dispatch=%d reached)', label, nameTag, tostring(ev.eventId or ''), ptId, maxDispatch))
      table.insert(out.events_detail, detailRec)
    elseif item.doing then
      if endT > 0 and nowMs > 0 and nowMs >= endT then
        local finMode = nil
        if evType == garbageType and MsgDefines and MsgDefines.FinishSampling then
          if not dryRun and SFSNetwork then pcall(function() SFSNetwork.SendMessage(MsgDefines.FinishSampling, tonumber(evUuid) or evUuid) end) end
          finMode = 'finish_sampling'
        elseif evType == helpType and MsgDefines and MsgDefines.DetectEventHelpEnd then
          if not dryRun and SFSNetwork then pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventHelpEnd, tonumber(evUuid) or evUuid) end) end
          finMode = 'finish_help'
        elseif (evType == rescueType or evType == overlordRescueType) and MsgDefines and MsgDefines.DetectEventRescueEnd then
          if not dryRun and SFSNetwork then pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventRescueEnd, tonumber(evUuid) or evUuid) end) end
          finMode = 'finish_rescue'
        end
        if finMode then
          table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), mode = finMode}})
          detailRec.action = finMode
          detailRec.action_taken = finMode
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): completed active timer (%s)', label, nameTag, tostring(ev.eventId or ''), finMode))
        else
          detailRec.action = 'in_progress'
          detailRec.action_taken = 'in_progress'
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): already in progress', label, nameTag, tostring(ev.eventId or ''), ptId))
        end
      else
        detailRec.action = 'skipped_in_progress'
        detailRec.action_taken = 'skipped_in_progress'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): already in progress', label, nameTag, tostring(ev.eventId or ''), ptId))
      end
      table.insert(out.events_detail, detailRec)
    elseif not item.active then
      detailRec.action = 'skipped_expired'
      detailRec.action_taken = 'skipped_expired'
      table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): skipped (expired)', label, nameTag, tostring(ev.eventId or ''), ptId))
      table.insert(out.events_detail, detailRec)
    elseif curStamina - cost < minStamina then
      detailRec.action = 'skipped_low_stamina'
      detailRec.action_taken = 'skipped_low_stamina'
      table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): skipped (stamina %d - cost %d < min %d)', label, nameTag, tostring(ev.eventId or ''), ptId, curStamina, cost, minStamina))
      table.insert(out.events_detail, detailRec)
    else
      -- A) NON-MARCH: SpecialOps (10) - Pure server RPC Batch Jump (DetectEventPveBatch) when power >= +30% threshold; NEVER force-loads 3D road scene!
      if evType == specialOpsType then
        local soNum = (rcm.GetSpecialOpsNum and tonumber(_safe_call(function() return rcm:GetSpecialOpsNum() end, 0))) or 0
        local soOrd = (rcm.GetSpecialOpsOrder and tonumber(_safe_call(function() return rcm:GetSpecialOpsOrder() end, 0))) or 0
        local pveEnt = (PveEntrance and PveEntrance.DetectEventPve) or 3
        local myPwr = (rcm.GetJumpPower and tonumber(_safe_call(function() return rcm:GetJumpPower(true, pveEnt) end, 0))) or 0
        local monLvlId = tonumber((tmpl and tmpl.para2) or 0) or 0
        local monPwr = (monLvlId > 0 and tcm and tcm.GetMonsterLevelPower and tonumber(_safe_call(function() return tcm:GetMonsterLevelPower(monLvlId) end, 0)))
          or tonumber((tmpl and tmpl.recommend_power) or 0) or 0
        local jHeroes, jSoldiers, jSkipNum, jPower = nil, nil, 0, 0
        if rcm.GetJumpLevel then
          local okJ, h, s, sk, pw = pcall(function() return rcm:GetJumpLevel() end)
          if okJ then
            jHeroes, jSoldiers, jSkipNum, jPower = h, s, tonumber(sk or 0) or 0, tonumber(pw or 0) or 0
          end
        end
        if soNum <= 0 then
          detailRec.action = 'skipped_no_special_ops_attempts'
          detailRec.action_taken = 'skipped_no_special_ops_attempts'
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): skipped (0 daily Special Ops attempts left)', label, nameTag, tostring(ev.eventId or ''), ptId))
        elseif jSkipNum > 0 and type(jHeroes) == 'table' and SFSNetwork and MsgDefines and MsgDefines.DetectEventPveBatch then
          -- Pure server-side batch completion: zero 3D road scene load, zero UI risk!
          local batchCost = jSkipNum * math.max(10, cost)
          if curStamina - batchCost >= minStamina then
            if not dryRun then
              local okB, errB = pcall(function()
                SFSNetwork.SendMessage(MsgDefines.DetectEventPveBatch, {{
                  heroes = jHeroes,
                  armys = jSoldiers or {{}},
                  power = jPower > 0 and jPower or myPwr,
                  skipNum = jSkipNum,
                }})
              end)
              if not okB then table.insert(out.errors, 'DetectEventPveBatch: ' .. tostring(errB)) end
            end
            curStamina = curStamina - batchCost
            table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), pointId = ptId, mode = 'special_ops_batch_jump', skipNum = jSkipNum, cost = batchCost}})
            detailRec.action = 'special_ops_batch_jump'
            detailRec.action_taken = 'special_ops_batch_jump'
            table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): batch-jumped %d Special Ops stage(s) via DetectEventPveBatch (order=%d->%d, pwr=%d)', label, nameTag, tostring(ev.eventId or ''), ptId, jSkipNum, soOrd, soOrd + jSkipNum, math.floor(jPower > 0 and jPower or myPwr)))
          else
            detailRec.action = 'skipped_low_stamina'
            detailRec.action_taken = 'skipped_low_stamina'
            table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): skipped batch jump (stamina %d < need %d + min %d)', label, nameTag, tostring(ev.eventId or ''), ptId, curStamina, batchCost, minStamina))
          end
        else
          local needJumpPwr = math.floor(monPwr * 1.30)
          detailRec.action = 'standby_below_batch_jump_threshold'
          detailRec.action_taken = 'standby_below_batch_jump_threshold'
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): standby (order=%d, pwr=%d vs enemy=%d; instant batch-jump unlocks at %d, left=%d)', label, nameTag, tostring(ev.eventId or ''), ptId, soOrd, math.floor(myPwr), math.floor(monPwr), needJumpPwr, soNum))
        end

      -- B) NON-MARCH: Radar PVE / Hero Trial / Guide PVE (7, 9, 13) - pure server RPC StartDetectEventPve
      elseif evType == pveType or evType == heroTrial or evType == guidePveType then
        if pveEnteredThisPass then
          detailRec.action = 'deferred_pve_busy'
          detailRec.action_taken = 'deferred_pve_busy'
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): deferred (another PVE fight already started this pass)', label, nameTag, tostring(ev.eventId or '')))
        else
          if not dryRun and rcm.StartDetectEventPve then
            local okP, errP = pcall(function() rcm:StartDetectEventPve(evUuid) end)
            if not okP then table.insert(out.errors, 'StartDetectEventPve(' .. tostring(evUuid) .. '): ' .. tostring(errP)) end
          end
          pveEnteredThisPass = true
          curStamina = curStamina - cost
          out.pve_triggered = out.pve_triggered + 1
          table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), mode = 'pve', cost = cost}})
          detailRec.action = 'pve_started'
          detailRec.action_taken = 'pve_started'
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): started radar PVE via StartDetectEventPve (stamina -%d)', label, nameTag, tostring(ev.eventId or ''), cost))
        end

      -- C) NON-MARCH: Reward Parkour (26) - PURE SERVER RPC (DetectPurkoutStart + ReceivePurkoutReward, zero 3D ChangeToLevel scene load!)
      elseif evType == parkourType and SFSNetwork and MsgDefines and MsgDefines.DetectPurkoutStart then
        if not dryRun then
          local okPk1, errPk1 = pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectPurkoutStart, tonumber(evUuid) or evUuid) end)
          if not okPk1 then table.insert(out.errors, 'DetectPurkoutStart: ' .. tostring(errPk1)) end
          if rcm.ReceivePurkoutReward then
            local okPk2, errPk2 = pcall(function() rcm:ReceivePurkoutReward(tonumber(evUuid) or evUuid, '', '', 100) end)
            if not okPk2 then table.insert(out.errors, 'ReceivePurkoutReward: ' .. tostring(errPk2)) end
          end
        end
        curStamina = curStamina - cost
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), mode = 'parkour_rpc', cost = cost}})
        detailRec.action = 'parkour_rpc_completed'
        detailRec.action_taken = 'parkour_rpc_completed'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): completed RewardParkour via pure server RPC (DetectPurkoutStart+ReceivePurkoutReward)', label, nameTag, tostring(ev.eventId or '')))

      -- D) NON-MARCH: Pick Garbage (6)
      elseif evType == garbageType then
        if not dryRun then
          if rcm.AddToFakeGarbageMarchManager and ptId > 0 then
            pcall(function() rcm:AddToFakeGarbageMarchManager(ptId) end)
          end
          if SFSNetwork and MsgDefines and MsgDefines.StartPickGarbage then
            local okG, errG = pcall(function() SFSNetwork.SendMessage(MsgDefines.StartPickGarbage, tonumber(evUuid) or evUuid) end)
            if not okG then table.insert(out.errors, 'StartPickGarbage: ' .. tostring(errG)) end
          end
        end
        curStamina = curStamina - cost
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), pointId = ptId, mode = 'start_pick_garbage', cost = cost}})
        detailRec.action = 'start_pick_garbage'
        detailRec.action_taken = 'start_pick_garbage'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): started pick garbage', label, nameTag, tostring(ev.eventId or ''), ptId))

      -- E) NON-MARCH: Alliance Treasure Dig (23)
      elseif evType == treasureType and SFSNetwork and MsgDefines and MsgDefines.ClickCreateTreasureDetect then
        if not dryRun then
          local okT, errT = pcall(function() SFSNetwork.SendMessage(MsgDefines.ClickCreateTreasureDetect, tonumber(evUuid) or evUuid) end)
          if not okT then table.insert(out.errors, 'ClickCreateTreasureDetect: ' .. tostring(errT)) end
        end
        curStamina = curStamina - cost
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), pointId = ptId, mode = 'treasure_dig', cost = cost}})
        detailRec.action = 'treasure_dig'
        detailRec.action_taken = 'treasure_dig'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): triggered alliance treasure dig', label, nameTag, tostring(ev.eventId or ''), ptId))

      -- F) NON-MARCH: Help Allies (19) - uses ev.helpInfo.pointId!
      elseif evType == helpType and MsgDefines and MsgDefines.DetectEventHelpStart and SFSNetwork then
        local helpPtId = (type(ev.helpInfo) == 'table' and tonumber(ev.helpInfo.pointId or 0) or 0)
        if helpPtId <= 0 then helpPtId = ptId end
        local helpAllyName = (type(ev.helpInfo) == 'table' and ev.helpInfo.name) or ev.helpName or ev.helpUid or ''
        if not dryRun then
          if dc.FakeHelperMarchManager and helpPtId > 0 then
            if dc.FakeHelperMarchManager.StartMarch then
              pcall(function() dc.FakeHelperMarchManager:StartMarch(helpPtId) end)
            elseif dc.FakeHelperMarchManager.AddMarchIndex then
              pcall(function() dc.FakeHelperMarchManager:AddMarchIndex(helpPtId) end)
            end
          end
          local okH, errH = pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventHelpStart, tonumber(evUuid) or evUuid) end)
          if not okH then table.insert(out.errors, 'DetectEventHelpStart: ' .. tostring(errH)) end
        end
        curStamina = curStamina - cost
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), pointId = helpPtId, mode = 'start_help', cost = cost}})
        detailRec.pointId = helpPtId
        detailRec.action = 'start_help'
        detailRec.action_taken = 'start_help'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d ally=%s): helped ally radar event', label, nameTag, tostring(ev.eventId or ''), helpPtId, tostring(helpAllyName)))

      -- G) NON-MARCH: Rescue / Overlord Rescue (20, 27)
      elseif (evType == rescueType or evType == overlordRescueType) and MsgDefines and MsgDefines.DetectEventRescueStart and SFSNetwork then
        if not dryRun then
          if dc.FakeRescueMarchManager and dc.FakeRescueMarchManager.AddMarchIndex and ptId > 0 then
            pcall(function() dc.FakeRescueMarchManager:AddMarchIndex(ptId) end)
          end
          local okR, errR = pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventRescueStart, tonumber(evUuid) or evUuid) end)
          if not okR then table.insert(out.errors, 'DetectEventRescueStart: ' .. tostring(errR)) end
        end
        curStamina = curStamina - cost
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), mode = 'start_rescue', cost = cost}})
        detailRec.action = 'start_rescue'
        detailRec.action_taken = 'start_rescue'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): started ally/overlord rescue', label, nameTag, tostring(ev.eventId or '')))

      -- H) NON-MARCH: Talk / Plot dialogs (16, 17, 18)
      elseif (evType == talkCityType or evType == talkWorldType or evType == plotType) and SFSNetwork and MsgDefines and MsgDefines.SU_DetectDialog then
        if not dryRun then
          local okD, errD = pcall(function() SFSNetwork.SendMessage(MsgDefines.SU_DetectDialog, tonumber(evUuid) or evUuid) end)
          if not okD then table.insert(out.errors, 'SU_DetectDialog: ' .. tostring(errD)) end
        end
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), mode = 'detect_dialog', cost = cost}})
        detailRec.action = 'detect_dialog'
        detailRec.action_taken = 'detect_dialog'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): completed radar dialog event', label, nameTag, tostring(ev.eventId or '')))

      -- I) MARCH-BASED: Boss/Skull (8), NPC HQ (22), Gather/Pickaxes (21), Normal/Mutant (1, 2, 5, 11, 12, 14, 25, 28, 29)
      elseif evType == bossType and ptId <= 0 and rcm.FindMonsterBoss then
        local bLv = tonumber((LuaEntry and LuaEntry.Player and LuaEntry.Player.pveBossLevel) or 1) or 1
        if dc.MonsterTemplateManager and dc.MonsterTemplateManager.GetCanAttackBossMaxLevel and dc.BuildManager then
          local mLv = tonumber(_safe_call(function() return dc.MonsterTemplateManager:GetCanAttackBossMaxLevel(dc.BuildManager.MainLv) end, bLv)) or bLv
          bLv = math.max(1, math.min(bLv, mLv))
        end
        if not dryRun then
          local okFB, errFB = pcall(function() rcm:FindMonsterBoss(bLv, nil) end)
          if not okFB then table.insert(out.errors, 'FindMonsterBoss: ' .. tostring(errFB)) end
        end
        table.insert(out.dispatched, {{uuid = tostring(evUuid), eventId = tostring(ev.eventId), mode = 'find_monster_boss', level = bLv}})
        detailRec.action = 'find_monster_boss'
        detailRec.action_taken = 'find_monster_boss'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s): summoned boss level %d via FindMonsterBoss', label, nameTag, tostring(ev.eventId or ''), bLv))

      elseif ptId > 0 then
        local f = (fIdx <= #freeForms) and freeForms[fIdx] or nil
        if f and f.uuid and mu and mu.SendCreateMarchMessage then
          fIdx = fIdx + 1
          local mType = (MarchTargetType and MarchTargetType.EXPLORE) or 20
          local targetUuid = tonumber(ev.relatedUuid or 0) or 0
          local ptInfo = (wpm and wpm.GetPointInfo and _safe_call(function() return wpm:GetPointInfo(ptId) end, nil))
            or (SceneManager and SceneManager.World and SceneManager.World.GetPointInfo and _safe_call(function() return SceneManager.World:GetPointInfo(ptId) end, nil))
            or nil
          if targetUuid <= 0 and type(ptInfo) == 'table' and ptInfo.uuid then
            targetUuid = tonumber(ptInfo.uuid) or 0
          end
          local isRallyBoss = false
          if evType == collectType then
            mType = (MarchTargetType and MarchTargetType.COLLECT) or 2
            if ptInfo then
              local tStr = tostring(ptInfo)
              if tStr:find('CollectArmy') or tStr:find('ArmyCollect') then
                mType = (MarchTargetType and MarchTargetType.ATTACK_ARMY_COLLECT) or 10
              elseif tStr:find('Monster') then
                mType = (MarchTargetType and MarchTargetType.ATTACK_MONSTER) or 1
              elseif tStr:find('Sample') then
                mType = (MarchTargetType and MarchTargetType.SAMPLE) or 21
              end
            end
          elseif evType == npcCityType then
            mType = (MarchTargetType and (MarchTargetType.DIRECT_ATTACK_NPC_CITY or MarchTargetType.ATTACK_NPC_CITY or MarchTargetType.ATTACK_MONSTER)) or 46
            if ptInfo and ptInfo.uuid then targetUuid = tonumber(ptInfo.uuid) or targetUuid end
          elseif evType == bossType then
            -- Boss/Skull ("Defeat 1 Boomer"): rally boss uses RALLY_FOR_BOSS (7) with timeIndex=1; otherwise ATTACK_MONSTER (1)
            local lowNm = string.lower(item.locName or '')
            if lowNm:find('boomer') or lowNm:find('frostbane') or lowNm:find('stegosaurus') or (tmpl and tostring(tmpl.icon or '') == 'Detect_icon_boss') then
              isRallyBoss = true
              mType = (MarchTargetType and MarchTargetType.RALLY_FOR_BOSS) or 7
            else
              mType = (MarchTargetType and MarchTargetType.ATTACK_MONSTER) or 1
            end
          elseif evType == 1 or evType == 2 or evType == 5 or evType == 11 or evType == 12 or evType == 14 or evType == 25 or evType == 28 or evType == 29 then
            mType = (MarchTargetType and MarchTargetType.ATTACK_MONSTER) or 1
          end

          local srvId = tonumber(snap.serverId) or snap.serverId
          if not dryRun then
            local okM, errM = pcall(function()
              if isRallyBoss then
                mu.SendCreateMarchMessage(tonumber(f.uuid) or f.uuid, tonumber(mType) or mType, ptId, targetUuid, 1, 1, nil, srvId)
              else
                mu.SendCreateMarchMessage(tonumber(f.uuid) or f.uuid, tonumber(mType) or mType, ptId, targetUuid, 0, true, true, srvId)
              end
            end)
            if not okM then table.insert(out.errors, 'March(' .. label .. '): ' .. tostring(errM)) end
          end
          curStamina = curStamina - cost
          table.insert(out.dispatched, {{
            uuid = tostring(evUuid), eventId = tostring(ev.eventId), pointId = ptId,
            mode = isRallyBoss and 'rally_boss' or 'march', march_type = tonumber(mType) or mType,
            formation = tostring(f.uuid), cost = cost,
          }})
          detailRec.formation = tostring(f.uuid)
          detailRec.march_type = tonumber(mType) or mType
          detailRec.action = isRallyBoss and 'dispatched_rally' or 'dispatched_march'
          detailRec.action_taken = detailRec.action
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): sent F%s (marchType=%d cost=%d)', label, nameTag, tostring(ev.eventId or ''), ptId, tostring(f.index or f.uuid), tonumber(mType) or 0, cost))
        else
          detailRec.action = 'skipped_no_free_formation'
          detailRec.action_taken = 'skipped_no_free_formation'
          table.insert(out.detail_lines, string.format('Pin %s%s (id=%s pt=%d): skipped (%d/%d formations free - all squads busy marching/gathering)', label, nameTag, tostring(ev.eventId or ''), ptId, #freeForms, out.unlock_formations))
        end
      else
        detailRec.action = 'skipped_unhandled_type'
        detailRec.action_taken = 'skipped_unhandled_type'
        table.insert(out.detail_lines, string.format('Pin %s%s (id=%s type=%d pt=%d): skipped (unhandled pin without tile)', label, nameTag, tostring(ev.eventId or ''), evType, ptId))
      end
      table.insert(out.events_detail, detailRec)
    end
  end
end

-- Check immediately if an exploration/PVE scene is already open to auto-skip
if not dryRun then
  local sk, how = _trigger_active_pve_skip()
  if sk then
    out.pve_skipped = out.pve_skipped + 1
    table.insert(out.detail_lines, 'Radar PVE Auto-Skip: ' .. tostring(how))
  end
end

if (#out.claimed_uuids > 0 or #out.dispatched > 0) and not dryRun then
  pcall(function()
    local d2 = _dismiss_modal_dialogs() or {{}}
    for _, w in ipairs(d2) do table.insert(out.popped_modals, w) end
  end)
end

return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=14.0)
    if not isinstance(res, dict):
        res = {"ok": False, "task": "radar_events", "error": "radar_sweep_failed"}

    # Merge Stage 0 results into final response
    res["lady_skill_used"] = int(st0.get("lady_skill_used") or 0)
    res["scans_remaining"] = int(st0.get("scans_remaining") or 0)
    res["radar_summon_triggered"] = bool(st0.get("radar_summon_triggered", False))
    res["level_reward_claimed"] = bool(st0.get("level_reward_claimed", False))
    res["laura_reward_claimed"] = bool(st0.get("laura_reward_claimed", False))
    res["detect_level"] = int(st0.get("detect_level") or 0)
    res["reward_level"] = int(st0.get("reward_level") or 0)
    res["summon_level"] = int(st0.get("summon_level", -1) if st0.get("summon_level") is not None else -1)
    res["scan_triggered"] = res["lady_skill_used"] + (1 if res["radar_summon_triggered"] else 0)

    merged_errors = list(st0.get("errors") or []) + list(res.get("errors") or [])
    res["errors"] = merged_errors

    # Auto-skip any newly entered PVE / SpecialOps / Parkour fight cleanly!
    if res.get("ok") and int(res.get("pve_triggered", 0) or 0) > 0 and not dry_run:
        for delay in (0.65, 1.0):
            skip_res = _skip_active_pve_after_delay(cd, pid, delay_sec=delay)
            if skip_res.get("skipped"):
                res["pve_skipped"] = int(res.get("pve_skipped", 0) or 0) + 1
                res.setdefault("detail_lines", []).append(
                    f"Radar PVE Auto-Skip (post-enter): {skip_res.get('method', 'OnSkipPVE')}"
                )
                break

    # If auto-finish completed tasks, poll briefly until resulting state==1 rewards hydrate and claim them!
    if res.get("ok") and int(res.get("auto_finished_count", 0) or 0) > 0 and claim_fin and not dry_run:
        post_claim_lua = """
local rcm = DataCenter and DataCenter.RadarCenterDataManager
local fin = {}
if rcm and type(rcm.events) == 'table' then
  for k, ev in pairs(rcm.events) do
    if type(ev) == 'table' and tonumber(ev.state or 0) == 1 then
      table.insert(fin, tonumber(ev.uuid or k) or (ev.uuid or k))
    end
  end
end
local claimed = {}
local errs = {}
if #fin > 0 and SFSNetwork and MsgDefines then
  if MsgDefines.BatchDetectEventRewardReceive then
    local okB, errB = pcall(function() SFSNetwork.SendMessage(MsgDefines.BatchDetectEventRewardReceive, fin) end)
    if okB then
      for _, u in ipairs(fin) do table.insert(claimed, u) end
    else
      table.insert(errs, 'BatchDetectEventRewardReceive: ' .. tostring(errB))
    end
  elseif MsgDefines.DetectEventRewardReceive then
    for _, u in ipairs(fin) do
      local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.DetectEventRewardReceive, u, false) end)
      if okS then
        table.insert(claimed, u)
      else
        table.insert(errs, 'DetectEventRewardReceive(' .. tostring(u) .. '): ' .. tostring(errS))
      end
    end
  else
    table.insert(errs, 'DetectEventRewardReceive_unavailable')
  end
end
return _enc({ok = true, pending_fin = #fin, claimed = claimed, errors = errs, send_errors = errs})
"""
        post_claim: dict[str, Any] = {}
        deadline = time.monotonic() + 1.4
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(0.35, remaining))
            post_claim = _eval_json(cd, pid, post_claim_lua, timeout=6.0)
            if not isinstance(post_claim, dict) or not post_claim.get("ok"):
                break
            if post_claim.get("claimed") or int(post_claim.get("pending_fin") or 0) > 0:
                break
        if isinstance(post_claim, dict):
            if post_claim.get("errors"):
                res.setdefault("errors", [])
                if isinstance(res["errors"], list):
                    for pe in post_claim["errors"]:
                        if pe and pe not in res["errors"]:
                            res["errors"].append(pe)
            if post_claim.get("send_errors"):
                res.setdefault("send_errors", [])
                if isinstance(res["send_errors"], list):
                    for se in post_claim["send_errors"]:
                        if se and se not in res["send_errors"]:
                            res["send_errors"].append(se)
            if post_claim.get("in_game_tips"):
                existing_tips = list(res.get("in_game_tips") or [])
                res["in_game_tips"] = _clean_in_game_tips(existing_tips + list(post_claim["in_game_tips"]))
            if post_claim.get("popped_modals"):
                existing_modals = list(res.get("popped_modals") or [])
                for mdl in post_claim["popped_modals"]:
                    if mdl not in existing_modals:
                        existing_modals.append(mdl)
                res["popped_modals"] = existing_modals
            extra_claimed = post_claim.get("claimed") or []
            if isinstance(extra_claimed, dict):
                extra_claimed = list(extra_claimed.values()) if extra_claimed else []
            if extra_claimed:
                cur_cu = res.get("claimed_uuids")
                if not isinstance(cur_cu, list):
                    if isinstance(cur_cu, tuple):
                        cur_cu = list(cur_cu)
                    elif isinstance(cur_cu, dict):
                        cur_cu = list(cur_cu.values()) if cur_cu else []
                    else:
                        cur_cu = []
                    res["claimed_uuids"] = cur_cu
                cur_cu.extend(str(u) for u in extra_claimed)
                dl = res.get("detail_lines")
                if not isinstance(dl, list):
                    dl = []
                    res["detail_lines"] = dl
                dl.append(
                    f"Post-AutoFinish Claim: claimed {len(extra_claimed)} newly completed radar reward(s)"
                )

    # Prepend concise summary header + Stage 0 lines so console shows complete state
    header = (
        f"Radar Summary: lv={res['detect_level']} (rewLv={res['reward_level']}, sumLv={res['summon_level']}), "
        f"scans_rem={res['scans_remaining']}, freeSquads={res.get('free_formations', 0)}/{res.get('unlock_formations', 0)}, "
        f"total_pins={res.get('total_events', 0)}, claimed={len(res.get('claimed_uuids') or [])}, "
        f"dispatched={len(res.get('dispatched') or [])}"
    )
    res["detail_lines"] = [header] + list(st0.get("detail_lines") or []) + list(res.get("detail_lines") or [])

    if (
        res["lady_skill_used"] > 0
        or res["radar_summon_triggered"]
        or res["level_reward_claimed"]
        or res["laura_reward_claimed"]
        or len(res.get("claimed_uuids") or []) > 0
        or len(res.get("dispatched") or []) > 0
    ):
        res["action"] = "processed"
        parts = []
        if res["lady_skill_used"] > 0:
            parts.append(f"used Lady scan x{res['lady_skill_used']}")
        if res["level_reward_claimed"]:
            parts.append("claimed radar level reward")
        if res["radar_summon_triggered"]:
            parts.append("triggered radar summon")
        if res.get("claimed_uuids"):
            parts.append(f"claimed {len(res['claimed_uuids'])} reward(s)")
        if res.get("dispatched"):
            parts.append(f"dispatched {len(res['dispatched'])} event(s)")
        res["message"] = ", ".join(parts)
    else:
        res["action"] = "none"
        res["message"] = "No radar scans, rewards, or events ready to claim or dispatch"

    used = [str(item["formation"]) for item in (res.get("dispatched") or []) if isinstance(item, dict) and item.get("formation")]
    if not dry_run and used:
        _record_used_formations(context, pid, used)
    return res


def run_daily_claims(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("daily_claims") or {}
    c_daily = bool(task_cfg.get("claim_daily_tasks", True))
    c_ach = bool(task_cfg.get("claim_achievements", True))
    c_bp = bool(task_cfg.get("claim_battle_pass", True))
    c_chap = bool(task_cfg.get("claim_chapter_tasks", True))
    c_main = bool(task_cfg.get("claim_main_tasks", True))

    lua = f"""
local dryRun = {str(dry_run).lower()}
local cDaily = {str(c_daily).lower()}
local cAch = {str(c_ach).lower()}
local cBp = {str(c_bp).lower()}
local cChap = {str(c_chap).lower()}
local cMain = {str(c_main).lower()}

local dc = DataCenter
local dismissed = {{}}
pcall(function() dismissed = _dismiss_modal_dialogs() or {{}} end)
local out = {{
  ok = true,
  task = 'daily_claims',
  dry_run = dryRun,
  daily_tasks_claimed = 0,
  daily_boxes_claimed = {{}},
  daily_cur_value = 0,
  achievements_claimed = 0,
  battle_passes_claimed = {{}},
  season_passes_claimed = {{}},
  week_cards_claimed = 0,
  month_cards_claimed = 0,
  chapter_tasks_claimed = 0,
  main_tasks_claimed = 0,
  passes_detail = {{}},
  popped_modals = dismissed,
  errors = {{}},
  detail_lines = {{}},
  action = 'none',
}}

-- Helper: collect active open activity IDs if ActivityListDataManager is present
local activeActs = {{}}
local actMgr = dc and dc.ActivityListDataManager
if actMgr then
  for _, tblName in ipairs({{'nowActivityList', 'activityList'}}) do
    local t = actMgr[tblName]
    if type(t) == 'table' then
      for k, a in pairs(t) do
        local aid = tonumber((type(a) == 'table' and (a.id or a.activityId or a.key)) or k or 0) or 0
        if aid > 0 then
          activeActs[aid] = (type(a) == 'table' and a) or {{ id = aid }}
        end
      end
    end
  end
end

-- 1) Daily Tasks & Milestone Chests
local dtm = dc and dc.DailyTaskManager
if cDaily and dtm then
  local tasksTbl = dtm.dailyQuestTasks
  if (type(tasksTbl) ~= 'table' or next(tasksTbl) == nil) then
    if dtm.GetAllDailyTask then
      local alt = _safe_call(function() return dtm:GetAllDailyTask() end, nil)
      if type(alt) == 'table' and next(alt) ~= nil then tasksTbl = alt end
    end
    if (type(tasksTbl) ~= 'table' or next(tasksTbl) == nil) and not dryRun and dtm.TryReqUpdateData then
      pcall(function() dtm:TryReqUpdateData() end)
    end
  end
  local taskIds = {{}}
  if type(tasksTbl) == 'table' then
    for _, t in pairs(tasksTbl) do
      if type(t) == 'table' and tonumber(t.state or 0) == 1 then
        out.daily_tasks_claimed = out.daily_tasks_claimed + 1
        local tid = tonumber(t.id or t.taskId or 0) or 0
        if tid > 0 then table.insert(taskIds, tid) end
      end
    end
  end
  if out.daily_tasks_claimed > 0 then
    if not dryRun and SFSNetwork and MsgDefines then
      if MsgDefines.DailyQuestGetAllReward then
        local okD, errD = pcall(function() SFSNetwork.SendMessage(MsgDefines.DailyQuestGetAllReward) end)
        if not okD then table.insert(out.errors, 'DailyQuestGetAllReward: ' .. tostring(errD)) end
      elseif MsgDefines.DailyTaskReward then
        for _, tid in ipairs(taskIds) do
          local okD, errD = pcall(function() SFSNetwork.SendMessage(MsgDefines.DailyTaskReward, tid) end)
          if not okD then table.insert(out.errors, 'DailyTaskReward(' .. tostring(tid) .. '): ' .. tostring(errD)) end
        end
      end
    end
    table.insert(out.detail_lines, string.format('Daily Tasks: claimed %d completed tasks [%s]', out.daily_tasks_claimed, table.concat(taskIds, ',')))
  end

  -- Prevent 0ms collision: if DailyQuestGetAllReward was dispatched in this tick, quest points
  -- have not yet been granted on the server. Only claim milestone chests when state is confirmed
  -- and no task batch was fired in the exact same tick.
  if out.daily_tasks_claimed == 0 and dtm.GetBoxState then
    local curVal = tonumber(_safe_call(function() return dtm:GetCurValue() end, 0)) or 0
    out.daily_cur_value = curVal
    local maxBox = (type(dtm.dailyBoxActive) == 'table' and #dtm.dailyBoxActive > 0 and #dtm.dailyBoxActive) or 8
    for boxIdx = 1, maxBox do
      if tonumber(_safe_call(function() return dtm:GetBoxState(boxIdx, curVal) end, 0)) == 1 then
        if not dryRun and SFSNetwork and MsgDefines and MsgDefines.DailyQuestReward then
          local okB, errB = pcall(function() SFSNetwork.SendMessage(MsgDefines.DailyQuestReward, boxIdx) end)
          if not okB then table.insert(out.errors, 'DailyQuestReward(' .. tostring(boxIdx) .. '): ' .. tostring(errB)) end
        end
        table.insert(out.daily_boxes_claimed, boxIdx)
        table.insert(out.detail_lines, string.format('Daily Milestone Box: claimed box #%d (activity=%d)', boxIdx, curVal))
        break -- Stagger milestone chest claims: one box per cycle prevents packet flood and modal overlay collisions
      end
    end
  end
end

-- 2) Achievements
local am = dc and dc.AchievementManager
if cAch and am then
  local cnt = tonumber(_safe_call(function() return am:GetClaimCount() end, 0)) or 0
  if cnt > 0 or _safe_call(function() return am:HasClaimable() end, false) then
    local allTypes = _safe_call(function() return am:GetAllTypes() end, nil)
    if type(allTypes) == 'table' then
      for _, tp in ipairs(allTypes) do
        local tCnt = tonumber(_safe_call(function() return am:GetTypeClaimCount(tp) end, 0)) or 0
        if tCnt > 0 then
          if not dryRun and SFSNetwork and MsgDefines and MsgDefines.AchievementRewardGet then
            local okA, errA = pcall(function() SFSNetwork.SendMessage(MsgDefines.AchievementRewardGet, tp) end)
            if not okA then table.insert(out.errors, 'AchievementRewardGet(' .. tostring(tp) .. '): ' .. tostring(errA)) end
          end
          out.achievements_claimed = out.achievements_claimed + tCnt
          table.insert(out.detail_lines, string.format('Achievements: claimed category=%s (%d items)', tostring(tp), tCnt))
          break -- Staggered claim: one category per cycle prevents packet flood
        end
      end
    end
    if out.achievements_claimed == 0 and cnt > 0 then
      out.achievements_claimed = cnt
      table.insert(out.detail_lines, string.format('Achievements: %d claimable pending', cnt))
    end
  end
end

-- 3) ALL Active Battle Passes, Season Passes & Event/Card Passes
if cBp and dc then
  local claimedBpMap = {{}}
  local function _claim_abp(actId, info, label)
    if not actId or actId <= 0 or claimedBpMap[actId] then return end
    local abp = dc.ActBattlePassData
    local hasClaim = false
    local redCnt = 0
    if abp and abp.GetActRed then
      redCnt = tonumber(_safe_call(function() return abp:GetActRed(actId) end, 0)) or 0
      if redCnt > 0 then hasClaim = true end
    end
    if not hasClaim and abp and abp.CheckCurGetReward then
      hasClaim = _safe_call(function() return abp:CheckCurGetReward(actId) end, false) and true or false
    end
    if not hasClaim and type(info) == 'table' then
      for _, st in pairs(info.stateInfo or {{}}) do
        if type(st) == 'table' and (tonumber(st.normalState or 0) == 1 or tonumber(st.specialState or 0) == 1 or tonumber(st.moreSpecialState or 0) == 1) then
          hasClaim = true; break
        end
      end
      if not hasClaim then
        local tArr = info.taskList or info.taskArr
        if type(tArr) == 'table' then
          for _, t in pairs(tArr) do
            if type(t) == 'table' and tonumber(t.state or 0) == 1 then hasClaim = true; break end
          end
        end
      end
    end
    if hasClaim then
      claimedBpMap[actId] = true
      if not dryRun and SFSNetwork and MsgDefines and MsgDefines.ReceiveBattlePassAllReward then
        local okP, errP = pcall(function() SFSNetwork.SendMessage(MsgDefines.ReceiveBattlePassAllReward, actId, 1) end)
        if not okP then table.insert(out.errors, 'BattlePass(' .. tostring(actId) .. '): ' .. tostring(errP)) end
      end
      table.insert(out.battle_passes_claimed, actId)
      table.insert(out.passes_detail, {{manager = label or 'ActBattlePassData', activityId = actId, redCount = redCnt}})
      table.insert(out.detail_lines, string.format('%s: claimed actId=%d (red=%d)', label or 'BattlePass', actId, redCnt))
    end
  end

  -- 3a) ActBattlePassData list + any BattlePass / GroundPass activities
  local abp = dc.ActBattlePassData
  if abp then
    if type(abp.list) == 'table' then
      for actKey, info in pairs(abp.list) do
        local actId = tonumber((type(info) == 'table' and (info.activityId or actKey)) or actKey or 0) or 0
        _claim_abp(actId, info, 'ActBattlePassData')
      end
    end
    for aid, actObj in pairs(activeActs) do
      local tp = tonumber(actObj.type or 0) or 0
      if tp == 27 or abp.GetInfoByActId then
        local info = (abp.GetInfoByActId and _safe_call(function() return abp:GetInfoByActId(aid) end, nil)) or nil
        if info ~= nil or tp == 27 then
          _claim_abp(aid, info, 'ActBattlePassData(act)')
        end
      end
    end
  end

  -- 3b) GroundPassManager
  local gpm = dc.GroundPassManager
  if gpm and gpm.GetCurrentBattlePassInfo then
    local gInfo = _safe_call(function() return gpm:GetCurrentBattlePassInfo() end, nil)
    if type(gInfo) == 'table' then
      local gId = tonumber(gInfo.activityId or gInfo.id or 0) or 0
      if gId > 0 then _claim_abp(gId, gInfo, 'GroundPassManager') end
    end
  end

  -- 3c) SeasonPassManager
  local spm = dc.SeasonPassManager
  if spm then
    local seenSp = {{}}
    local spCandidates = {{}}
    if type(spm.seasonPassInfoDic) == 'table' then
      for k, sp in pairs(spm.seasonPassInfoDic) do
        local aid = tonumber((type(sp) == 'table' and (sp.activityId or k)) or k or 0) or 0
        if aid > 0 and not seenSp[aid] then seenSp[aid] = true; table.insert(spCandidates, aid) end
      end
    end
    for aid, actObj in pairs(activeActs) do
      if tonumber(actObj.type or 0) == 45 and not seenSp[aid] then
        seenSp[aid] = true; table.insert(spCandidates, aid)
      end
    end
    for _, aid in ipairs(spCandidates) do
      local totRed = tonumber(_safe_call(function() return spm:GetTotalRedCount(aid) end, 0)) or 0
      local lvlRed = tonumber(_safe_call(function() return spm:GetPassLevelRedCount(aid) end, 0)) or 0
      if totRed > 0 or lvlRed > 0 then
        if not dryRun then
          if spm.ClaimAllLevelRewardsReq then
            local okS, errS = pcall(function() spm:ClaimAllLevelRewardsReq(aid, true) end)
            if not okS then table.insert(out.errors, 'SeasonPass(' .. tostring(aid) .. '): ' .. tostring(errS)) end
          elseif SFSNetwork and MsgDefines and MsgDefines.ClaimAllSeasonPassReward then
            local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.ClaimAllSeasonPassReward, aid, true) end)
            if not okS then table.insert(out.errors, 'ClaimAllSeasonPassReward(' .. tostring(aid) .. '): ' .. tostring(errS)) end
          end
        end
        table.insert(out.season_passes_claimed, aid)
        table.insert(out.passes_detail, {{manager = 'SeasonPassManager', activityId = aid, redCount = math.max(totRed, lvlRed)}})
        table.insert(out.detail_lines, string.format('SeasonPass: claimed all tier/task rewards for actId=%d (red=%d)', aid, math.max(totRed, lvlRed)))
      end
    end
  end

  -- 3d) WeekCardManager (Weekly Free & Paid Daily Claims)
  local wcm = dc.WeekCardManager
  if wcm then
    local hasFree = _safe_call(function() return wcm:CheckIfHasFreeReward() end, false) and true or false
    local hasRed = _safe_call(function() return wcm:CheckIfHasRed() end, false) and true or false
    if hasFree or hasRed then
      if not dryRun and SFSNetwork and MsgDefines then
        if MsgDefines.AllClaimWeekCardReward then
          local okW, errW = pcall(function() SFSNetwork.SendMessage(MsgDefines.AllClaimWeekCardReward, hasFree) end)
          if not okW then table.insert(out.errors, 'AllClaimWeekCardReward: ' .. tostring(errW)) end
        elseif hasFree and MsgDefines.ClaimWeekCardFreeReward then
          local okW, errW = pcall(function() SFSNetwork.SendMessage(MsgDefines.ClaimWeekCardFreeReward) end)
          if not okW then table.insert(out.errors, 'ClaimWeekCardFreeReward: ' .. tostring(errW)) end
        end
      end
      out.week_cards_claimed = out.week_cards_claimed + 1
      table.insert(out.passes_detail, {{manager = 'WeekCardManager', hasFree = hasFree, hasRed = hasRed}})
      table.insert(out.detail_lines, string.format('WeekCard: claimed rewards (free=%s, red=%s)', tostring(hasFree), tostring(hasRed)))
    end
  end

  -- 3e) DayRechargeMonthCardManager (e.g. Apoca Treasure Guide)
  local drm = dc.DayRechargeMonthCardManager
  if drm then
    local seenDrm = {{}}
    local drmIds = {{}}
    if tonumber(drm.activityId or 0) > 0 then
      local aid = tonumber(drm.activityId)
      seenDrm[aid] = true; table.insert(drmIds, aid)
    end
    if type(drm.monthCardInfo) == 'table' then
      for k, _ in pairs(drm.monthCardInfo) do
        local aid = tonumber(k or 0) or 0
        if aid > 0 and not seenDrm[aid] then seenDrm[aid] = true; table.insert(drmIds, aid) end
      end
    end
    for aid, actObj in pairs(activeActs) do
      if tonumber(actObj.type or 0) == 1005 and not seenDrm[aid] then
        seenDrm[aid] = true; table.insert(drmIds, aid)
      end
    end
    for _, aid in ipairs(drmIds) do
      local rc = tonumber(_safe_call(function() return drm:GetRedCount(aid) end, 0)) or 0
      local unrec = _safe_call(function() return drm:GetUnReceivedReward(aid) end, {{}}) or {{}}
      local unrecCnt = (type(unrec) == 'table') and #unrec or (tonumber(unrec) or 0)
      if unrecCnt > 0 then
        if not dryRun and drm.GetAllReward then
          local okM, errM = pcall(function() drm:GetAllReward(aid) end)
          if not okM then table.insert(out.errors, 'DayRechargeMonthCard(' .. tostring(aid) .. '): ' .. tostring(errM)) end
          if drm.SetIsClickToDay then pcall(function() drm:SetIsClickToDay() end) end
        end
        out.month_cards_claimed = out.month_cards_claimed + 1
        table.insert(out.passes_detail, {{manager = 'DayRechargeMonthCardManager', activityId = aid, redCount = rc, unreceived = unrecCnt}})
        table.insert(out.detail_lines, string.format('DayRechargeMonthCard: claimed actId=%d (%d rewards)', aid, unrecCnt))
      elseif rc > 0 and not dryRun and drm.SetIsClickToDay then
        pcall(function() drm:SetIsClickToDay() end)
      end
    end
  end

  -- 3f) MonthMsgCardManager (e.g. Weekly Promo Pass / Monthly Msg Card)
  local mmc = dc.MonthMsgCardManager
  if mmc and type(mmc.dataDict) == 'table' then
    for k, _ in pairs(mmc.dataDict) do
      local aid = tonumber(k or 0) or 0
      if aid > 0 then
        local rc = tonumber(_safe_call(function() return mmc:GetRedCount(aid) end, 0)) or 0
        if rc > 0 then
          local cIdx = _safe_call(function() return mmc:GetCanRewardIndex(aid) end, nil)
          local claimedHere = 0
          if type(cIdx) == 'number' and cIdx > 0 then
            if not dryRun and mmc.ReceiveWeekCardData then
              local okC, errC = pcall(function() mmc:ReceiveWeekCardData(aid, cIdx) end)
              if not okC then table.insert(out.errors, 'MonthMsgCard(' .. tostring(aid) .. '): ' .. tostring(errC)) end
            end
            claimedHere = 1
          elseif type(cIdx) == 'table' then
            for ik, iv in pairs(cIdx) do
              local idxNum = tonumber((type(iv) == 'table' and (iv.index or iv.id)) or iv or ik or 0) or 0
              if idxNum > 0 then
                if not dryRun and mmc.ReceiveWeekCardData then
                  local okC, errC = pcall(function() mmc:ReceiveWeekCardData(aid, idxNum) end)
                  if not okC then table.insert(out.errors, 'MonthMsgCard(' .. tostring(aid) .. ',' .. tostring(idxNum) .. '): ' .. tostring(errC)) end
                end
                claimedHere = claimedHere + 1
              end
            end
          end
          if claimedHere > 0 then
            out.month_cards_claimed = out.month_cards_claimed + claimedHere
            table.insert(out.passes_detail, {{manager = 'MonthMsgCardManager', activityId = aid, redCount = rc, indices = claimedHere}})
            table.insert(out.detail_lines, string.format('MonthMsgCard: claimed %d reward(s) for actId=%d (red=%d)', claimedHere, aid, rc))
          end
        end
      end
    end
  end

  -- 3g) Golloes Month Card free daily gift if active
  local mcn = dc.MonthCardNewManager
  if mcn and mcn.CheckIfHasGolloesGift and _safe_call(function() return mcn:CheckIfHasGolloesGift() end, false) then
    if not dryRun and SFSNetwork and MsgDefines and MsgDefines.ClaimGolloesDailyReward then
      local okG, errG = pcall(function() SFSNetwork.SendMessage(MsgDefines.ClaimGolloesDailyReward) end)
      if not okG then table.insert(out.errors, 'ClaimGolloesDailyReward: ' .. tostring(errG)) end
    end
    out.month_cards_claimed = out.month_cards_claimed + 1
    table.insert(out.passes_detail, {{manager = 'MonthCardNewManager', kind = 'GolloesDailyReward'}})
    table.insert(out.detail_lines, 'MonthCardNewManager: claimed daily Golloes gift')
  end

  -- 3h) HeroMonthCardManager
  local hmc = dc.HeroMonthCardManager
  if hmc then
    local unrec = hmc.GetUnReceivedReward and _safe_call(function() return hmc:GetUnReceivedReward() end, 0) or 0
    local canClaimHmc = (type(unrec) == 'number' and unrec > 0) or (type(unrec) == 'table' and #unrec > 0)
    local hmcInfo = hmc.monthCardInfo
    if not canClaimHmc and type(hmcInfo) == 'table' and tonumber(hmcInfo.buy or 0) > 0 and type(hmcInfo.rewardArr) == 'table' then
      local canState = (HeroMonthCardRewardState and HeroMonthCardRewardState.REWARD_STATE_CAN_RECEIVE) or 1
      for _, rw in pairs(hmcInfo.rewardArr) do
        if type(rw) == 'table' and hmc.GetRewardState and tonumber(_safe_call(function() return hmc:GetRewardState(rw) end, -1)) == canState then
          canClaimHmc = true; break
        end
      end
    end
    if canClaimHmc and SFSNetwork and MsgDefines and MsgDefines.GetHeroMonthCardAllReward then
      if not dryRun then
        local okH, errH = pcall(function() SFSNetwork.SendMessage(MsgDefines.GetHeroMonthCardAllReward) end)
        if not okH then table.insert(out.errors, 'GetHeroMonthCardAllReward: ' .. tostring(errH)) end
      end
      out.month_cards_claimed = out.month_cards_claimed + 1
      table.insert(out.passes_detail, {{manager = 'HeroMonthCardManager', activityId = hmcInfo and hmcInfo.activityId or 0}})
      table.insert(out.detail_lines, 'HeroMonthCardManager: claimed all available Hero Month Card rewards')
    end
  end

  -- 3i) ActSeasonWeekCardData
  local asw = dc.ActSeasonWeekCardData
  if asw and type(asw.list) == 'table' then
    for k, swInfo in pairs(asw.list) do
      local aid = tonumber((type(swInfo) == 'table' and (swInfo.activityId or k)) or k or 0) or 0
      if aid > 0 then
        local swRed = asw.GetActRed and tonumber(_safe_call(function() return asw:GetActRed(aid) end, 0)) or 0
        if swRed > 0 and SFSNetwork and MsgDefines and MsgDefines.ReceiveSeasonWeekCardReward then
          if not dryRun then
            local okSW, errSW = pcall(function()
              SFSNetwork.SendMessage(MsgDefines.ReceiveSeasonWeekCardReward, aid, 1, true)
              SFSNetwork.SendMessage(MsgDefines.ReceiveSeasonWeekCardReward, aid, 1, false)
            end)
            if not okSW then table.insert(out.errors, 'ReceiveSeasonWeekCardReward(' .. tostring(aid) .. '): ' .. tostring(errSW)) end
          end
          out.week_cards_claimed = out.week_cards_claimed + 1
          table.insert(out.passes_detail, {{manager = 'ActSeasonWeekCardData', activityId = aid, redCount = swRed}})
          table.insert(out.detail_lines, string.format('SeasonWeekCard: claimed actId=%d (red=%d)', aid, swRed))
        end
      end
    end
  end
end

-- 4) Chapter Tasks & Main/Growth Tasks (TaskRewardBatch)
local batchTaskIds = {{}}
local seenTaskIds = {{}}
local ctm = dc and dc.ChapterTaskManager
if cChap and ctm and ctm.GetCanReceivedList then
  local lst = _safe_call(function() return ctm:GetCanReceivedList() end, {{}}) or {{}}
  for _, v in ipairs(lst) do
    local tid = tostring((type(v) == 'table' and (v.id or v.taskId)) or v or '')
    if tid ~= '' and not seenTaskIds[tid] then
      seenTaskIds[tid] = true
      table.insert(batchTaskIds, tid)
      out.chapter_tasks_claimed = out.chapter_tasks_claimed + 1
    end
  end
end

local tm = dc and dc.TaskManager
if cMain and tm then
  if tm.GetCanReceivedLevelList then
    local lvlLst = _safe_call(function() return tm:GetCanReceivedLevelList() end, {{}}) or {{}}
    for _, v in ipairs(lvlLst) do
      local tid = tostring((type(v) == 'table' and (v.id or v.taskId)) or v or '')
      if tid ~= '' and not seenTaskIds[tid] then
        seenTaskIds[tid] = true
        table.insert(batchTaskIds, tid)
        out.main_tasks_claimed = out.main_tasks_claimed + 1
      end
    end
  end
  local showMain = tm.IsShowMainTask and _safe_call(function() return tm:IsShowMainTask() end, false) or false
  if showMain and tm.GetAllMainTaskForView then
    local vLst = _safe_call(function() return tm:GetAllMainTaskForView() end, {{}}) or {{}}
    for _, v in ipairs(vLst) do
      if type(v) == 'table' and tonumber(v.state or 0) == 1 then
        local tid = tostring(v.id or v.taskId or '')
        if tid ~= '' and not seenTaskIds[tid] then
          seenTaskIds[tid] = true
          table.insert(batchTaskIds, tid)
          out.main_tasks_claimed = out.main_tasks_claimed + 1
        end
      end
    end
  end
end

if #batchTaskIds > 0 then
  if not dryRun and SFSNetwork and MsgDefines and MsgDefines.TaskRewardBatch then
    local chunk = {{}}
    for _, tid in ipairs(batchTaskIds) do
      table.insert(chunk, tid)
      if #chunk >= 25 then
        local payload = table.concat(chunk, ';')
        local okT, errT = pcall(function() SFSNetwork.SendMessage(MsgDefines.TaskRewardBatch, payload) end)
        if not okT then table.insert(out.errors, 'TaskRewardBatch: ' .. tostring(errT)) end
        chunk = {{}}
      end
    end
    if #chunk > 0 then
      local payload = table.concat(chunk, ';')
      local okT, errT = pcall(function() SFSNetwork.SendMessage(MsgDefines.TaskRewardBatch, payload) end)
      if not okT then table.insert(out.errors, 'TaskRewardBatch: ' .. tostring(errT)) end
    end
  end
  table.insert(out.detail_lines, string.format('Tasks: claimed chapter=%d, main/level=%d (total=%d)', out.chapter_tasks_claimed, out.main_tasks_claimed, #batchTaskIds))
end

local totalClaimed = out.daily_tasks_claimed + #out.daily_boxes_claimed + out.achievements_claimed
  + #out.battle_passes_claimed + #out.season_passes_claimed + out.week_cards_claimed + out.month_cards_claimed
  + out.chapter_tasks_claimed + out.main_tasks_claimed
if totalClaimed > 0 then
  out.action = 'claimed'
  pcall(function()
    local d2 = _dismiss_modal_dialogs() or {{}}
    for _, w in ipairs(d2) do table.insert(out.popped_modals, w) end
  end)
else
  table.insert(out.detail_lines, 'No pending daily tasks, chests, achievements, chapter/main tasks, or pass rewards')
end
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=12.0)


def _scan_daily_tasks_live(cd: Any, pid: int) -> dict[str, Any]:
    """Read all Daily Tasks, XML metadata, activity score, and milestone chests from DataCenter.DailyTaskManager."""
    lua = r"""
local out = {
  ok = true,
  active_score = 0,
  max_score = 150,
  boxes = {},
  tasks = {},
  errors = {},
}
local function _loc(k)
  if not k or tostring(k) == '' then return '' end
  local ok, s = pcall(function() return Localization:GetString(tostring(k)) end)
  if ok and s and s ~= '' then return tostring(s) end
  return tostring(k)
end
local dtm = DataCenter and DataCenter.DailyTaskManager
if not dtm then
  out.ok = false
  table.insert(out.errors, 'DailyTaskManager unavailable')
  return _enc(out)
end
if dtm.GetCurValue then
  out.active_score = tonumber(_safe_call(function() return dtm:GetCurValue() end, 0)) or 0
end
if dtm.GetDailyMaxValue then
  local mv = tonumber(_safe_call(function() return dtm:GetDailyMaxValue() end, 0)) or 0
  if mv > 0 then out.max_score = mv end
end
if type(dtm.dailyBoxActive) == 'table' then
  for idx, thr in ipairs(dtm.dailyBoxActive) do
    local st = 0
    if dtm.GetBoxState then
      st = tonumber(_safe_call(function() return dtm:GetBoxState(idx, out.active_score) end, 0)) or 0
    end
    table.insert(out.boxes, { idx = idx, threshold = tonumber(thr or 0) or 0, state = st })
  end
end
local list = nil
if dtm.GetSortDailyTask then
  list = _safe_call(function() return dtm:GetSortDailyTask() end, nil)
end
if type(list) ~= 'table' or next(list) == nil then
  list = dtm.dailyQuestTasks
end
if (type(list) ~= 'table' or next(list) == nil) and dtm.GetAllDailyTask then
  list = _safe_call(function() return dtm:GetAllDailyTask() end, nil)
end
local lc = LocalController and LocalController.instance and LocalController.instance()
if type(list) == 'table' then
  for _, t in pairs(list) do
    if type(t) == 'table' then
      local tid = tostring(t.id or t.taskId or '')
      if tid ~= '' then
        local row = lc and lc.getLine and TableName and TableName.DailyQuest and _safe_call(function() return lc:getLine(TableName.DailyQuest, tid) end, nil) or nil
        local nameRaw = row and tostring(_safe_call(function() return row.name end, '') or '') or ''
        local descRaw = row and tostring(_safe_call(function() return row.desc end, '') or '') or ''
        local nameLoc = _loc(nameRaw)
        local descLoc = _loc(descRaw)
        local gotype = row and (tonumber(_safe_call(function() return row.gotype end, 0)) or 0) or 0
        local gotype2 = row and (tonumber(_safe_call(function() return row.gotype2 end, 0)) or 0) or 0
        local go = row and (tonumber(_safe_call(function() return row.go end, 0)) or 0) or 0
        local gopara = row and tostring(_safe_call(function() return row.gopara end, '') or '') or ''
        local pt = row and (tonumber(_safe_call(function() return row.point end, 0)) or 0) or 0
        table.insert(out.tasks, {
          id = tid,
          num = tonumber(t.num or 0) or 0,
          totalNum = tonumber(t.totalNum or 0) or 0,
          state = tonumber(t.state or 0) or 0,
          point = pt,
          name_raw = nameRaw,
          name = nameLoc,
          desc_raw = descRaw,
          desc = descLoc,
          gotype = gotype,
          gotype2 = gotype2,
          go = go,
          gopara = gopara,
        })
      end
    end
  end
end
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if isinstance(res, dict) and isinstance(res.get("tasks"), list):
        for t in res["tasks"]:
            if not isinstance(t, dict):
                continue
            for fk, rk in (("name", "name_raw"), ("desc", "desc_raw")):
                v = str(t.get(fk) or "").strip()
                rv = str(t.get(rk) or v).strip()
                if (not v or v.isdigit()) and rv.isdigit():
                    resolved = _localize_id(rv)
                    if resolved and resolved != rv:
                        t[fk] = resolved
            total_n = int(t.get("totalNum") or 0)
            desc = str(t.get("desc") or "").replace("{0}", str(total_n))
            t["desc_formatted"] = desc
    return res if isinstance(res, dict) else {"ok": False, "tasks": [], "boxes": [], "active_score": 0}


def _classify_daily_task_kind(t: dict[str, Any]) -> str:
    """Map a live DailyTaskManager row to a deterministic action kind."""
    tid = str(t.get("id") or "").strip()
    desc = str(t.get("desc_formatted") or t.get("desc") or "").lower()
    g2 = int(t.get("gotype2") or 0)

    if tid == "1000052" or g2 == 99 or ("like" in desc and "post" in desc):
        return "social_likes"
    if tid == "1000037" or ("hero exp" in desc):
        return "hero_exp"
    if tid == "1000016" or ("recruitment ticket" in desc) or ("recruit" in desc and "ticket" in desc):
        return "recruit_ticket"
    if tid == "1000045" or g2 == 81 or ("donate" in desc and "alliance tech" in desc):
        return "alliance_donate"
    if tid == "1000017" or g2 == 17 or ("help allies" in desc):
        return "alliance_help"
    if tid == "1000012" or ("upgrade building" in desc):
        return "building_upgrade"
    if tid == "1000006" or ("research" in desc and "tech" in desc):
        return "research_tech"
    if tid in ("1000002", "1000003", "1000004", "1000025", "1000026", "1000027", "1000028", "1000029", "1000030", "1000031", "1000032", "1000033") or (
        "train" in desc and any(w in desc for w in ("rider", "assaulter", "shooter"))
    ):
        return "train_troops"
    if tid == "1000035" or ("speedup" in desc):
        return "use_speedup"
    if tid == "1000046" or g2 == 82 or ("arena" in desc):
        return "arena_attack"
    if tid == "1000044" or g2 == 80 or ("trade truck" in desc):
        return "trade_trucks"
    if tid == "1000047" or g2 == 83 or ("plunder" in desc and "bounty" in desc):
        return "plunder_bounty"
    if tid == "1000024" or ("warehouse resource" in desc):
        return "warehouse_item"
    if tid == "1000018" or ("radar event" in desc):
        return "radar_events"
    if tid in ("1000013", "1000043", "1000049", "1000050", "1000051") or (
        "team-up" in desc or "frostbane" in desc or "boomer" in desc or "stegosaur" in desc
    ):
        return "boss_rally"
    if tid in ("1000048", "1000034", "1000014", "1000015", "1000022") or (
        "gathering act" in desc or "gather" in desc or ("mine" in desc and "stone" in desc)
    ):
        return "gather_acts"
    if tid in ("1000005", "1000007") or ("defeat" in desc and "creep" in desc):
        return "defeat_creeps"
    if tid == "1000023" or g2 == 29 or ("pack shop" in desc):
        return "pack_shop_iap"
    if tid == "1000042" or ("attack headquarters" in desc):
        return "attack_hq"
    return "unknown"


def _do_daily_social_likes(cd: Any, pid: int, needed: int, dry_run: bool = False) -> dict[str, Any]:
    """Like `needed` different Moment posts via DataCenter.MomentManager:SendLoveMoment(uid, uuid).
    Actively refreshes Moment lists (SendGetChatMomentList + SendGetMomentList + SendGetFriendMomentsLikeInfo)
    on fresh clients where MomentManager caches start empty."""
    need = max(1, int(needed or 1))
    lua_collect_body = """
local mm = DataCenter and DataCenter.MomentManager
if not mm then return _enc({ ok = false, reason = 'MomentManager unavailable', unliked = {} }) end
local unliked = {}
local seen = {}
local function _is_unliked(m)
  if m.isLove == true or m.hasLove == true or m.isLiked == true then return false end
  if m.love == true then return false end
  local lv = tonumber(m.love or 0) or 0
  return lv == 0
end
local function collect(tbl)
  if type(tbl) ~= 'table' then return end
  for _, m in pairs(tbl) do
    if type(m) == 'table' then
      local muuid = m.uuid or m.id or m.momentId
      local muid = m.uid or m.playerUid or m.userId
      if muuid and muid and _is_unliked(m) then
        local key = tostring(muuid)
        if not seen[key] then
          seen[key] = true
          table.insert(unliked, { uid = tostring(muid), uuid = muuid })
        end
      end
    end
  end
end
if mm.GetChatMomentRecommendsList then
  collect(_safe_call(function() return mm:GetChatMomentRecommendsList() end, nil))
end
if mm.GetChatMomentList then
  collect(_safe_call(function() return mm:GetChatMomentList() end, nil))
end
if mm.chatmomentinfo then
  collect(mm.chatmomentinfo.recommends)
  collect(mm.chatmomentinfo.chatMomentContainer)
  collect(mm.chatmomentinfo.chatHistoryContainer)
end
if mm.info then
  collect(mm.info.momentContainer)
  if type(mm.info.momentPlayerContainer) == 'table' then
    for _, pList in pairs(mm.info.momentPlayerContainer) do
      collect(pList)
    end
  end
end
if mm.GetFriendMomentsInfo then
  local fm = _safe_call(function() return mm:GetFriendMomentsInfo() end, nil)
  if type(fm) == 'table' then
    collect(fm.list or fm.moments or fm)
  end
end
"""
    lua_check = (
        lua_collect_body
        + """
local refreshed = false
if #unliked < %d and not %s then
  if mm.chatMomentListRequestInFlight == true and mm.ResetChatMomentListRequestState then
    pcall(function() mm:ResetChatMomentListRequestState() end)
  end
  if mm.SendGetChatMomentList then
    pcall(function() mm:SendGetChatMomentList(0, true, true, 0) end)
    refreshed = true
  end
  if mm.SendGetMomentList then
    pcall(function() mm:SendGetMomentList(0, 0) end)
    refreshed = true
  end
  if mm.SendGetFriendMomentsLikeInfo then
    pcall(function() mm:SendGetFriendMomentsLikeInfo() end)
  end
end
return _enc({ ok = true, unliked_count = #unliked, refreshed = refreshed, unliked = unliked })
""" % (need, str(dry_run).lower())
    )
    r = _eval_json(cd, pid, lua_check, timeout=8.0)
    if r.get("refreshed") and not dry_run:
        lua_recheck = lua_collect_body + "\nreturn _enc({ ok = true, unliked_count = #unliked, refreshed = false, unliked = unliked })\n"
        for _ in range(6):
            time.sleep(0.7)
            r = _eval_json(cd, pid, lua_recheck, timeout=8.0)
            if len(r.get("unliked") or []) >= need:
                break
    unliked = r.get("unliked") or []
    to_like = unliked[:need]
    if dry_run:
        return {"ok": True, "liked": len(to_like), "available": len(unliked), "dry_run": True}
    liked = 0
    errors: list[str] = []
    for post in to_like:
        p_uid = str(post.get("uid") or "")
        p_uuid = post.get("uuid")
        if not p_uid or not p_uuid:
            continue
        lua_like = f"""
local mm = DataCenter and DataCenter.MomentManager
if not mm or not mm.SendLoveMoment then return _enc({{ ok = false, err = 'SendLoveMoment unavailable' }}) end
local okL, errL = pcall(function() mm:SendLoveMoment({json.dumps(p_uid)}, {int(p_uuid) if isinstance(p_uuid, (int, float)) else json.dumps(str(p_uuid))}) end)
return _enc({{ ok = okL, err = okL and '' or tostring(errL) }})
"""
        lr = _eval_json(cd, pid, lua_like, timeout=6.0)
        if lr.get("ok"):
            liked += 1
        elif lr.get("err"):
            errors.append(str(lr["err"]))
        time.sleep(0.35)
    return {"ok": len(errors) == 0, "liked": liked, "available": len(unliked), "errors": errors}


def _do_daily_hero_exp(cd: Any, pid: int, needed: int, dry_run: bool = False) -> dict[str, Any]:
    """Use `needed` smallest Hero EXP items (e.g., itemId=200394 = 1 EXP) on lowest-level non-maxed hero via HeroLvUp."""
    need = max(1, int(needed or 1))
    lua = f"""
local dryRun = {str(dry_run).lower()}
local need = {need}
local dc = DataCenter
local hm = dc and dc.HeroDataManager
local idata = dc and dc.ItemData
local itm = dc and dc.ItemTemplateManager
local out = {{ ok = true, used = 0, heroId = 0, itemId = 0, reason = '' }}
if not hm or not idata or type(idata.ItemInfos) ~= 'table' then
  out.ok = false; out.reason = 'HeroDataManager/ItemData unavailable'; return _enc(out)
end
local bestItem = nil
for uuid, info in pairs(idata.ItemInfos) do
  if type(info) == 'table' then
    local cnt = tonumber(info.count or 0) or 0
    local iid = tonumber(info.itemId or 0) or 0
    if cnt >= need and iid > 0 then
      local tmpl = info.template or (itm and _safe_call(function() return itm:GetItemTemplate(iid) end, nil))
      local tp = tmpl and tonumber(tmpl.type or -1) or -1
      local tp2 = tmpl and tonumber(tmpl.type2 or -1) or -1
      if tp == 91 and tp2 == 1 then
        local expVal = tonumber(info.para1 or (tmpl and tmpl.para1) or 999999999) or 999999999
        if not bestItem or expVal < bestItem.expVal then
          bestItem = {{ uuid = tostring(uuid), itemId = iid, count = cnt, expVal = expVal }}
        end
      end
    end
  end
end
if not bestItem then
  out.reason = 'no_hero_exp_items_available'; return _enc(out)
end
local bestHero = nil
local list = _safe_call(function() return hm:GetHeroSortList() end, nil) or hm.allHero or {{}}
for _, h in pairs(list) do
  if type(h) == 'table' and h.uuid then
    local lv = tonumber(h.level or 0) or 0
    local maxLv = tonumber(h.curMaxLevel or h.finalLevel or 200) or 200
    if lv > 0 and lv < maxLv then
      if not bestHero or lv < bestHero.lv then
        bestHero = {{ uuid = h.uuid, heroId = tonumber(h.heroId or 0) or 0, lv = lv, maxLv = maxLv }}
      end
    end
  end
end
if not bestHero then
  out.reason = 'all_heroes_at_max_level'; return _enc(out)
end
out.heroId = bestHero.heroId
out.heroLv = bestHero.lv
out.itemId = bestItem.itemId
out.expPerItem = bestItem.expVal
if not dryRun and SFSNetwork and MsgDefines and MsgDefines.HeroLvUp then
  SFSNetwork.SendMessage(MsgDefines.HeroLvUp, bestHero.uuid, bestItem.uuid, need)
end
out.used = need
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=8.0)
    if not dry_run and int(res.get("used") or 0) > 0:
        time.sleep(0.9)
    return res


def _do_daily_ticket_recruit(cd: Any, pid: int, needed: int, dry_run: bool = False) -> dict[str, Any]:
    """Use Recruitment Tickets (never diamonds) via LotteryHeroCard(id, isTen=0, useFree=0, itemId, 0)."""
    need = max(1, int(needed or 1))
    lua = f"""
local dryRun = {str(dry_run).lower()}
local need = {need}
local dc = DataCenter
local ldm = dc and dc.LotteryDataManager
local idata = dc and dc.ItemData
local out = {{ ok = true, recruited = 0, bannerId = '', ticketItemId = '', ticketCount = 0, usedFree = false, reason = '' }}
if not ldm or not idata or type(idata.ItemInfos) ~= 'table' then
  out.ok = false; out.reason = 'LotteryDataManager/ItemData unavailable'; return _enc(out)
end
-- Build itemId -> count map
local inv = {{}}
for _, info in pairs(idata.ItemInfos) do
  if type(info) == 'table' then
    local iid = tostring(info.itemId or '')
    local cnt = tonumber(info.count or 0) or 0
    if iid ~= '' and cnt > 0 then inv[iid] = (inv[iid] or 0) + cnt end
  end
end
local snap = _get_player_snapshot()
local nowMs = (snap.serverSec or 0) * 1000
local dict = _safe_call(function() return ldm:GetAllShowLotteryDict() end, nil) or ldm.lotteryDict or {{}}
local cands = {{}}
for k, lv in pairs(dict) do
  if type(lv) == 'table' then
    local lid = tostring(lv.id or k)
    local ltype = tonumber(lv.type or 0) or 0
    local dFree = tonumber(lv.dailyFree or 0) or 0
    local cdFree = (tonumber(lv.free_cd or 0) or 0) > 0 and (tonumber(lv.nextFreeTime or 0) or 0) <= nowMs and nowMs > 0
    local itemStr = tostring(lv.item or '')
    -- Parse first 1x cost token "itemId;cost" before '|'
    local firstTok = itemStr:match('^([^|]+)') or itemStr
    local tItem, tCost = firstTok:match('^(%d+);(%d+)$')
    local tCostNum = tonumber(tCost or 0) or 0
    local owned = (tItem and inv[tItem]) or 0
    if dFree > 0 or cdFree then
      table.insert(cands, {{ prio = 1, id = lid, useFree = 1, itemId = '', cost = 0, owned = 999 }})
    elseif tItem and tCostNum > 0 and owned >= tCostNum then
      -- Prefer standard Hero Recruitment (id=='103' or type==1) before Refugee Recruitment (901)
      local prio = (lid == '103' and 2) or (ltype == 1 and 3) or 5
      table.insert(cands, {{ prio = prio, id = lid, useFree = 0, itemId = tItem, cost = tCostNum, owned = owned }})
    end
  end
end
table.sort(cands, function(a, b) return a.prio < b.prio end)
if #cands == 0 then
  out.reason = 'no_recruitment_tickets_or_free_draws_available'
  return _enc(out)
end
local pick = cands[1]
out.bannerId = pick.id
out.ticketItemId = pick.itemId
out.ticketCount = pick.owned
out.usedFree = (pick.useFree == 1)
local draws = math.min(need, pick.cost > 0 and math.floor(pick.owned / pick.cost) or need)
if draws <= 0 then
  out.reason = 'insufficient_tickets'
  return _enc(out)
end
if not dryRun and SFSNetwork and MsgDefines and MsgDefines.LotteryHeroCard then
  for _ = 1, draws do
    pcall(function()
      SFSNetwork.SendMessage(MsgDefines.LotteryHeroCard, tostring(pick.id), 0, pick.useFree, tostring(pick.itemId), 0)
    end)
  end
end
out.recruited = draws
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=10.0)
    if not dry_run and int(res.get("recruited") or 0) > 0:
        time.sleep(1.5)
        # Clear HeroUtils.IsInTheLottery safety flag and dismiss UINewHero modal if popped
        _eval_json(cd, pid, "pcall(function() if HeroUtils then HeroUtils.IsInTheLottery = false end; _dismiss_modal_dialogs() end); return _enc({ok=true})", timeout=5.0)
    return res


def _do_daily_boss_rally(
    cd: Any,
    pid: int,
    needed: int,
    target_keyword: str,
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Start (or join) up to `needed` rally marches against Frostbane / Boomer / Stegosaur bosses."""
    need = max(1, int(needed or 1))
    reserve = int(cfg.get("formation_reserve", 0))
    kw = (target_keyword or "").strip().lower()

    if not dry_run:
        ensure_world_scene(cd, pid)

    def _attempt_rally(allow_search: bool) -> dict[str, Any]:
        lua = f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local need = {need}
local kw = {json.dumps(kw)}
local allowSearch = {str(allow_search).lower()}
local snap = _get_player_snapshot()
local dc = DataCenter
local lc = LocalController and LocalController.instance and LocalController.instance()
local out = {{
  ok = true,
  started = {{}},
  joined = {{}},
  searched = false,
  search_level = 0,
  free_formations = 0,
  reason = '',
}}
if not snap.inAlliance then
  out.reason = 'not_in_alliance'; return _enc(out)
end
local forms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, not dryRun)
out.free_formations = #forms

-- Dedupe active boss rallies & join open ally boss rallies first before hosting a new one
local wm = dc and dc.AllianceWarDataManager
local myOpenRallies = 0
local activeTargetPts = {{}}
if wm and wm.GetAllAllianceWar then
  local wars = _safe_call(function() return wm:GetAllAllianceWar() end, nil) or {{}}
  for _, w in pairs(wars) do
    if type(w) == 'table' and tonumber(w.type or -1) == (AllianceTeamType and AllianceTeamType.ATTACK_BOSS or 0) and w.uuid then
      local tpt = tonumber(w.targetPointId or w.targetPos or w.targetPoint or 0) or 0
      if tpt > 0 then activeTargetPts[tpt] = true end
      if tostring(w.attackUid or '') == tostring(snap.uid or '') then
        myOpenRallies = myOpenRallies + 1
      elseif #forms > 0 and (#out.joined + myOpenRallies) < need then
        local alreadyIn = wm.HasRallyFormationForInfo and _safe_call(function() return wm:HasRallyFormationForInfo(w) end, false)
        if not alreadyIn then
          if not dryRun and wm.JoinRally then
            pcall(function() wm:JoinRally(w.uuid) end)
          end
          table.insert(out.joined, {{ warUuid = tostring(w.uuid), targetPoint = tpt }})
          table.remove(forms, 1)
        end
      end
    end
  end
end
out.my_open_rallies = myOpenRallies
local remainingToHost = math.max(0, need - myOpenRallies - #out.joined)
if remainingToHost <= 0 then
  out.reason = (#out.joined > 0) and 'joined_open_ally_rally' or 'already_hosting_active_boss_rally'
  return _enc(out)
end
if #forms == 0 then
  out.reason = (#out.joined > 0) and 'joined_open_ally_rally' or 'no_free_formation'
  return _enc(out)
end

local function _loc(k)
  if not k or tostring(k) == '' then return '' end
  local ok, s = pcall(function() return Localization:GetString(tostring(k)) end)
  return (ok and s and s ~= '') and tostring(s) or tostring(k)
end

local mm = dc and dc.MonsterManager
local canMax = mm and mm.GetCanFindBossMaxLevel and tonumber(_safe_call(function() return mm:GetCanFindBossMaxLevel() end, 10)) or 10
local searchLv = math.max(1, math.min(canMax, 5))
if canMax >= 20 then searchLv = math.min(canMax, 10) end

local wpm = dc and dc.WorldPointManager
local bosses = {{}}
if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1)
    local pnum = tonumber(ptIdx) or tonumber(ptObj and ptObj.pointId) or 0
    if ptType == (PointType and PointType.WorldMonster or 4) and pnum > 0 then
      local info = wpm:GetPointInfo(pnum)
      local pb = info and info._parsedExtra or nil
      if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
        local ok_pb, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
        if ok_pb and parsed then pb = parsed end
      end
      if pb and pb.monsterId and lc and TableName and TableName.Monster then
        local row = lc:getLine(TableName.Monster, tostring(pb.monsterId))
        if row then
          local isBoss = tonumber(_safe_call(function() return row:getValue('boss') end, 0)) or 0
          local lv = tonumber(_safe_call(function() return row:getValue('level') end, 0)) or 0
          local nm = _loc(_safe_call(function() return row:getValue('name') end, ''))
          local nml = nm:lower()
          local kwMatch = (kw == '') or (nml:find(kw, 1, true) ~= nil)
          -- Match requested boss type (Frostbane / Boomer / Stegosaurus) or fallback to any normal rally boss
          if isBoss == 1 and lv > 0 and lv <= math.max(canMax, 60) and (kwMatch or nml:find('frostbane') or nml:find('boomer') or nml:find('stego')) then
            local targetPt = tonumber(info and info.mainIndex or 0) or 0
            if targetPt <= 0 then targetPt = pnum end
            if not activeTargetPts[targetPt] then
              local d = snap.mainPos > 0 and _dist(snap.mainPos, targetPt) or 9999
              table.insert(bosses, {{
                pointId = targetPt,
                uuid = (info and info.uuid) or (pb and pb.uuid) or 0,
                monsterId = tonumber(pb.monsterId) or 0,
                name = nm,
                level = lv,
                kwMatch = kwMatch,
                dist = math.floor(d * 10) / 10,
                score = (kwMatch and 0 or 50000) + lv * 50 + d,
              }})
            end
          end
        end
      end
    end
  end
end

table.sort(bosses, function(a, b) return a.score < b.score end)
local maxLaunch = math.min(remainingToHost, #forms, #bosses)
if maxLaunch > 0 then
  for i = 1, maxLaunch do
    local f = forms[i]
    local b = bosses[i]
    if not dryRun and MarchUtil and MarchUtil.SendCreateMarchMessage then
      pcall(function()
        MarchUtil.SendCreateMarchMessage(
          f.uuid,
          MarchTargetType and MarchTargetType.RALLY_FOR_BOSS or 7,
          b.pointId,
          b.uuid or 0,
          1,
          true,
          true,
          snap.serverId
        )
      end)
    end
    table.insert(out.started, {{
      pointId = b.pointId,
      name = b.name,
      level = b.level,
      dist = b.dist,
      formationUuid = tostring(f.uuid),
    }})
  end
elseif allowSearch and not dryRun and SFSNetwork and MsgDefines then
  if MsgDefines.FindMonster and snap.mainPos > 0 then
    pcall(function() SFSNetwork.SendMessage(MsgDefines.FindMonster, tonumber(snap.mainPos), searchLv, true) end)
    out.searched = true
    out.search_level = searchLv
  elseif MsgDefines.FindMonsterBoss then
    pcall(function() SFSNetwork.SendMessage(MsgDefines.FindMonsterBoss, searchLv, 0) end)
    out.searched = true
    out.search_level = searchLv
  end
  out.reason = 'searching_world_for_boss'
else
  out.reason = 'no_rally_boss_found_in_viewport'
end
return _enc(out)
"""
        return _eval_json(cd, pid, lua, timeout=10.0)

    res = _attempt_rally(allow_search=True)
    if res.get("searched") and not dry_run:
        time.sleep(2.0)
        res = _attempt_rally(allow_search=False)
    if context is not None and isinstance(res.get("started"), list):
        used_uuids = [str(x["formationUuid"]) for x in res["started"] if isinstance(x, dict) and x.get("formationUuid")]
        if not dry_run and used_uuids:
            _record_used_formations(context, pid, used_uuids)
    return res


def _do_daily_gather_acts(
    cd: Any,
    pid: int,
    needed: int,
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch up to `needed` free squads to lowest-level (fast Lv1-3) unoccupied resource tiles via FindResourcePoint + COLLECT."""
    need = max(1, int(needed or 1))
    reserve = int(cfg.get("formation_reserve", 0))

    if not dry_run:
        ensure_world_scene(cd, pid)

    dispatched: list[dict[str, Any]] = []
    claimed_keys = list((context or {}).get("claimed_gather_points", []))
    reason = ""

    # Try dispatching up to `need` squads (searching a fresh Lv1 resource tile if viewport has none)
    for attempt_idx in range(need):
        claimed_lua = "{" + ",".join(f"[{json.dumps(str(k))}]=true" for k in claimed_keys) + "}"
        def _pick_gather_lua(allow_search: bool) -> str:
            return f"""
local dryRun = {str(dry_run).lower()}
local reserve = {reserve}
local allowSearch = {str(allow_search).lower()}
local claimedPts = {claimed_lua}
local snap = _get_player_snapshot()
local dc = DataCenter
local forms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, not dryRun)
if #forms == 0 then
  return _enc({{ ok = true, dispatched = nil, need_search = false, reason = 'no_free_formation' }})
end
local wpm = dc and dc.WorldPointManager
local crm = dc and dc.CollectResourceManager
local cands = {{}}
local function add_point(pnum, boost)
  pnum = tonumber(pnum) or 0
  if pnum <= 0 or not wpm or not wpm.GetPointInfo then return end
  local ck = tostring(snap.serverId) .. ':' .. tostring(pnum)
  if claimedPts[ck] then return end
  local info = wpm:GetPointInfo(pnum)
  local ri = info and info.resourceInfo or nil
  if ri and tonumber(ri.gatherUuid or 0) == 0 and tostring(ri.ownerUid or '') == '' then
    local row = LocalController and LocalController.instance and LocalController.instance():getLine(TableName.GatherResource, tostring(ri.resourceId or 0))
    local lv = row and (tonumber(_safe_call(function() return row:getValue('level') end, 1)) or 1) or 1
    local d = snap.mainPos > 0 and _dist(snap.mainPos, pnum) or 0
    -- Strongly prefer low level (Lv1-3 finishes fastest for Daily Gathering Acts!) and close distance
    table.insert(cands, {{
      pointId = pnum,
      claimKey = ck,
      level = lv,
      dist = math.floor(d * 10) / 10,
      score = (boost and -50000 or 0) + lv * 1000 + d,
    }})
  end
end
if crm and crm.GetFindResPoint then
  local fp = _safe_call(function() return crm:GetFindResPoint() end, 0)
  if tonumber(fp or 0) > 0 then add_point(fp, true) end
end
if wpm and wpm.allViewPoints then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local ptType = tonumber(ptObj and ptObj.pointType or -1)
    local pnum = tonumber(ptIdx) or tonumber(ptObj and ptObj.pointId) or 0
    if ptType == (PointType and PointType.WorldResource or 7) and pnum > 0 then
      add_point(pnum, false)
    end
  end
end
if #cands == 0 then
  if allowSearch and not dryRun and SFSNetwork and MsgDefines and MsgDefines.FindResourcePoint then
    local resTypes = {{14, 0, 2, 1, 12}}
    local rt = resTypes[({attempt_idx} % #resTypes) + 1]
    pcall(function() SFSNetwork.SendMessage(MsgDefines.FindResourcePoint, rt, 1, '') end)
    return _enc({{ ok = true, dispatched = nil, need_search = true, search_type = rt, reason = 'searching_lv1_resource' }})
  end
  return _enc({{ ok = true, dispatched = nil, need_search = false, reason = 'no_unoccupied_resource_in_viewport' }})
end
table.sort(cands, function(a, b) return a.score < b.score end)
local tile = cands[1]
local f = forms[1]
if not dryRun and MarchUtil and MarchUtil.SendCreateMarchMessage then
  pcall(function()
    MarchUtil.SendCreateMarchMessage(
      tonumber(f.uuid) or f.uuid,
      MarchTargetType and MarchTargetType.COLLECT or 2,
      tile.pointId,
      0,
      0,
      true,
      true,
      tonumber(snap.serverId) or 0
    )
  end)
end
return _enc({{
  ok = true,
  need_search = false,
  dispatched = {{
    pointId = tile.pointId,
    claimKey = tile.claimKey,
    level = tile.level,
    dist = tile.dist,
    formationUuid = tostring(f.uuid),
  }},
}})
"""
        r = _eval_json(cd, pid, _pick_gather_lua(allow_search=True), timeout=10.0)
        if r.get("need_search") and not dry_run:
            time.sleep(1.8)
            r = _eval_json(cd, pid, _pick_gather_lua(allow_search=False), timeout=10.0)
        disp = r.get("dispatched")
        if isinstance(disp, dict) and disp.get("pointId"):
            dispatched.append(disp)
            ck = str(disp.get("claimKey") or "")
            if ck and ck not in claimed_keys:
                claimed_keys.append(ck)
            if context is not None:
                c_list = context.setdefault("claimed_gather_points", [])
                if ck and ck not in c_list and not dry_run:
                    c_list.append(ck)
                if not dry_run and disp.get("formationUuid"):
                    _record_used_formations(context, pid, [str(disp["formationUuid"])])
            if not dry_run:
                time.sleep(0.5)
        else:
            reason = str(r.get("reason") or "")
            break

    return {"ok": True, "dispatched": dispatched, "count": len(dispatched), "reason": reason}


def _claim_all_daily_tasks_and_boxes(cd: Any, pid: int, dry_run: bool = False) -> dict[str, Any]:
    """Claim ALL completed Daily Tasks (state==1) AND ALL unlocked Daily Milestone Chests (30..150)."""
    before = _scan_daily_tasks_live(cd, pid)
    claimable_tasks = [t for t in (before.get("tasks") or []) if int(t.get("state") or 0) == 1]
    claimable_boxes = [b for b in (before.get("boxes") or []) if int(b.get("state") or 0) == 1]

    if dry_run:
        return {
            "ok": True,
            "tasks_claimed": len(claimable_tasks),
            "boxes_claimed": [int(b.get("idx") or 0) for b in claimable_boxes],
            "active_score": int(before.get("active_score") or 0),
        }

    # 1) Fire DailyQuestGetAllReward ("receive.daily.task.and.stage.reward") if any task or box is claimable
    if claimable_tasks or claimable_boxes:
        _eval_json(
            cd,
            pid,
            """
local errs = {}
if SFSNetwork and MsgDefines then
  if MsgDefines.DailyQuestGetAllReward then
    local ok1, e1 = pcall(function() SFSNetwork.SendMessage(MsgDefines.DailyQuestGetAllReward) end)
    if not ok1 then table.insert(errs, tostring(e1)) end
  elseif MsgDefines.DailyTaskReward then
    local dtm = DataCenter and DataCenter.DailyTaskManager
    for _, t in pairs((dtm and dtm.dailyQuestTasks) or {}) do
      if type(t) == 'table' and tonumber(t.state or 0) == 1 then
        pcall(function() SFSNetwork.SendMessage(MsgDefines.DailyTaskReward, tostring(t.id or t.taskId)) end)
      end
    end
  end
end
return _enc({ ok = #errs == 0, errors = errs })
""",
            timeout=8.0,
        )
        time.sleep(1.3)

    # 2) Re-scan and explicitly claim any newly unlocked milestone boxes (1..5 -> 30,60,90,120,150)
    mid = _scan_daily_tasks_live(cd, pid)
    boxes_sent: list[int] = []
    for b in (mid.get("boxes") or []):
        if int(b.get("state") or 0) == 1:
            b_idx = int(b.get("idx") or 0)
            if b_idx > 0:
                _eval_json(
                    cd,
                    pid,
                    f"if SFSNetwork and MsgDefines and MsgDefines.DailyQuestReward then pcall(function() SFSNetwork.SendMessage(MsgDefines.DailyQuestReward, {b_idx}) end) end; return _enc({{ok=true}})",
                    timeout=6.0,
                )
                boxes_sent.append(b_idx)
                time.sleep(0.55)

    # Dismiss reward popup modals cleanly (excluding UINoticeTips)
    _eval_json(cd, pid, "pcall(_dismiss_modal_dialogs); return _enc({ok=true})", timeout=5.0)
    time.sleep(0.6)
    after = _scan_daily_tasks_live(cd, pid)
    claimed_boxes_after = [int(b.get("idx") or 0) for b in (after.get("boxes") or []) if int(b.get("state") or 0) == 2]
    return {
        "ok": True,
        "tasks_claimed": len(claimable_tasks),
        "boxes_sent": boxes_sent,
        "boxes_claimed_total": claimed_boxes_after,
        "active_score_before": int(before.get("active_score") or 0),
        "active_score_after": int(after.get("active_score") or 0),
    }


def run_daily_tasks_complete(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One-go Daily Tasks Orchestrator: scans all listed Daily Tasks in DataCenter.DailyTaskManager,
    completes every actionable incomplete task, and claims all completed tasks + milestone chests (30..150)."""
    task_cfg = cfg.get("daily_tasks_complete") or {}
    allow_pvp_hq = bool(task_cfg.get("allow_pvp_hq_attack", False))

    scan_before = _scan_daily_tasks_live(cd, pid)
    if not scan_before.get("ok"):
        return {
            "ok": False,
            "task": "daily_tasks_complete",
            "dry_run": dry_run,
            "error": "; ".join(scan_before.get("errors") or ["DailyTaskManager unavailable"]),
            "detail_lines": ["Daily Tasks scan failed: DailyTaskManager unavailable"],
        }

    tasks_before = scan_before.get("tasks") or []
    score_before = int(scan_before.get("active_score") or 0)
    max_score = int(scan_before.get("max_score") or 150)

    todo_tasks = [t for t in tasks_before if int(t.get("state") or 0) == 0]
    claimable_before = [t for t in tasks_before if int(t.get("state") or 0) == 1]
    claimed_before = [t for t in tasks_before if int(t.get("state") or 0) == 2]

    detail_lines: list[str] = [
        f"Daily Tasks Scan (Before): score={score_before}/{max_score} | TODO={len(todo_tasks)} | Claimable={len(claimable_before)} | Claimed={len(claimed_before)}"
    ]
    executed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[str] = []

    # Execution priority: instant city/RPC tasks first, then world/march tasks, then safety-skipped items
    order_rank = {
        "social_likes": 10,
        "hero_exp": 15,
        "recruit_ticket": 20,
        "alliance_donate": 25,
        "alliance_help": 30,
        "building_upgrade": 35,
        "research_tech": 40,
        "train_troops": 45,
        "use_speedup": 50,
        "arena_attack": 55,
        "trade_trucks": 60,
        "plunder_bounty": 65,
        "warehouse_item": 70,
        "radar_events": 80,
        "boss_rally": 85,
        "gather_acts": 90,
        "defeat_creeps": 95,
        "pack_shop_iap": 990,
        "attack_hq": 995,
        "unknown": 999,
    }

    classified_todo = []
    for t in todo_tasks:
        kind = _classify_daily_task_kind(t)
        classified_todo.append((order_rank.get(kind, 999), kind, t))
    classified_todo.sort(key=lambda x: x[0])

    # Avoid calling the same multi-task runner twice (e.g., 3 troop training tasks in one pass)
    ran_shared_kinds: set[str] = set()

    for _, kind, t in classified_todo:
        tid = str(t.get("id") or "")
        desc = str(t.get("desc_formatted") or t.get("desc") or tid)
        cur_n = int(t.get("num") or 0)
        tot_n = max(1, int(t.get("totalNum") or 1))
        remaining = max(1, tot_n - cur_n)

        if kind == "pack_shop_iap":
            msg = f"[{tid}] {desc} ({cur_n}/{tot_n}) -> SKIPPED (Real-money Pack Shop IAP - never automated)"
            detail_lines.append(msg)
            skipped.append({"id": tid, "kind": kind, "desc": desc, "reason": "real_money_iap"})
            continue

        if kind == "attack_hq" and not allow_pvp_hq:
            msg = f"[{tid}] {desc} ({cur_n}/{tot_n}) -> SKIPPED (PvP/NAP & Peace Shield safety; other tasks reach 245/150 pts)"
            detail_lines.append(msg)
            skipped.append({"id": tid, "kind": kind, "desc": desc, "reason": "pvp_nap_safety"})
            continue

        if kind in ("train_troops",) and kind in ran_shared_kinds:
            continue
        ran_shared_kinds.add(kind)

        try:
            sub_res: dict[str, Any] = {}
            if kind == "social_likes":
                sub_res = _do_daily_social_likes(cd, pid, remaining, dry_run=dry_run)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> liked {sub_res.get('liked', 0)}/{remaining} posts (available={sub_res.get('available', 0)})")
            elif kind == "hero_exp":
                sub_res = _do_daily_hero_exp(cd, pid, remaining, dry_run=dry_run)
                detail_lines.append(
                    f"[{tid}] {desc} ({cur_n}/{tot_n}) -> used {sub_res.get('used', 0)}x item {sub_res.get('itemId', 0)} on hero {sub_res.get('heroId', 0)} (Lv{sub_res.get('heroLv', '?')})"
                    + (f" ({sub_res.get('reason')})" if sub_res.get("reason") else "")
                )
            elif kind == "recruit_ticket":
                sub_res = _do_daily_ticket_recruit(cd, pid, remaining, dry_run=dry_run)
                detail_lines.append(
                    f"[{tid}] {desc} ({cur_n}/{tot_n}) -> recruited {sub_res.get('recruited', 0)}x on banner {sub_res.get('bannerId', '')} (ticket={sub_res.get('ticketItemId', 'free')})"
                    + (f" ({sub_res.get('reason')})" if sub_res.get("reason") else "")
                )
            elif kind == "alliance_donate":
                sub_res = run_alliance_daily(cd, pid, client_state, cfg, dry_run=dry_run, context=context, tech_only=True)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "alliance_help":
                sub_res = run_auto_help(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "building_upgrade":
                # Pick fastest/cheapest affordable building (prefer_fastest=True) so Daily Task finishes cleanly
                b_cfg = copy.deepcopy(cfg)
                b_cfg.setdefault("building_upgrades", {})["hq_priority"] = False
                b_cfg["building_upgrades"]["prefer_fastest"] = True
                b_cfg["building_upgrades"]["auto_prerequisites"] = True
                b_cfg["building_upgrades"]["call_alliance_help"] = True
                sub_res = run_building_upgrades(cd, pid, client_state, b_cfg, dry_run=dry_run, context=context)
                # If the upgrade finishes within <= 20s (e.g. Lv1-3 building after VIP reduction), wait & flush finish immediately!
                if not dry_run and sub_res.get("ok") and isinstance(sub_res.get("upgraded"), dict):
                    b_uuid = str(sub_res["upgraded"].get("uuid") or "")
                    v_info = sub_res.get("verified") or {}
                    ut_raw = int(v_info.get("updateTime") or 0)
                    if ut_raw > 0:
                        if ut_raw < 10**12:
                            ut_raw *= 1000
                        snap_now = snapshot_client(cd, pid)
                        now_ms = int(snap_now.get("serverSec") or 0) * 1000
                        rem_s = (ut_raw - now_ms) / 1000.0 if now_ms > 0 else 9999
                        if -60 <= rem_s <= 20:
                            if rem_s > 0:
                                time.sleep(min(rem_s + 1.2, 22.0))
                            _eval_json(
                                cd,
                                pid,
                                f"local bm = DataCenter and DataCenter.BuildManager; if bm and bm.CheckSendBuildFinish then pcall(function() bm:CheckSendBuildFinish(tonumber({json.dumps(b_uuid)}) or {json.dumps(b_uuid)}, false, true) end) end; return _enc({{ok=true}})",
                                timeout=6.0,
                            )
                            time.sleep(1.0)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('reason') or sub_res.get('action') or 'done'}")
            elif kind == "research_tech":
                sub_res = run_research_queue(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('reason') or sub_res.get('action') or 'done'}")
            elif kind == "train_troops":
                sub_res = run_troop_training(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "use_speedup":
                s_cfg = copy.deepcopy(cfg)
                s_cfg.setdefault("speedups", {})["use_items"] = True
                s_cfg["speedups"]["align_with_preparedness"] = False
                s_cfg["speedups"]["ignore_theme_filter"] = True
                s_cfg["speedups"]["max_items_per_cycle"] = max(1, min(remaining, 3))
                sub_res = run_speedups(cd, pid, client_state, s_cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "arena_attack":
                a_cfg = copy.deepcopy(cfg)
                a_cfg.setdefault("arena", {})["max_battles_per_cycle"] = max(remaining, 1)
                sub_res = run_arena(cd, pid, client_state, a_cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "trade_trucks":
                sub_res = run_trucks(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "plunder_bounty":
                sub_res = run_bounty_steal(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "radar_events":
                sub_res = run_radar_events(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('message') or sub_res.get('action') or 'done'}")
            elif kind == "boss_rally":
                dl = desc.lower()
                b_kw = "frostbane" if "frostbane" in dl else ("stego" if "stego" in dl else ("boomer" if "boomer" in dl else ""))
                sub_res = _do_daily_boss_rally(cd, pid, remaining, b_kw, cfg, dry_run=dry_run, context=context)
                started_list = sub_res.get("started") or []
                joined_list = sub_res.get("joined") or []
                if started_list or joined_list:
                    parts = []
                    if joined_list:
                        parts.append(f"joined {len(joined_list)} ally rally")
                    if started_list:
                        labels = ", ".join(f"{x.get('name', 'Boss')} Lv{x.get('level', '?')}@{x.get('pointId', 0)}" for x in started_list)
                        parts.append(f"launched {len(started_list)} rally: {labels}")
                    detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> " + "; ".join(parts) + " (completes after 5m rally march)")
                else:
                    detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('reason') or 'no rally launched'}")
            elif kind == "gather_acts":
                sub_res = _do_daily_gather_acts(cd, pid, remaining, cfg, dry_run=dry_run, context=context)
                g_disp = sub_res.get("dispatched") or []
                if g_disp:
                    pts = ", ".join(f"Lv{x.get('level', '?')}@{x.get('pointId', 0)}" for x in g_disp)
                    detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> dispatched {len(g_disp)} fast gather march(es): {pts}")
                else:
                    detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('reason') or 'no free formation / tile'}")
            elif kind == "warehouse_item":
                sub_res = run_free_recruits(cd, pid, client_state, cfg, dry_run=dry_run, context=context)
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> {sub_res.get('action') or 'done'}")
            elif kind == "defeat_creeps":
                if not dry_run:
                    ensure_world_scene(cd, pid)
                sub_res = _eval_json(
                    cd,
                    pid,
                    f"""
local dryRun = {str(dry_run).lower()}
local snap = _get_player_snapshot()
local forms = _pick_free_formations({int(cfg.get('formation_reserve', 0))}, {_used_formations_lua(context, pid)}, not dryRun)
if #forms == 0 then return _enc({{ ok = true, attacked = 0, reason = 'no_free_formation' }}) end
local wpm = DataCenter and DataCenter.WorldPointManager
local lc = LocalController and LocalController.instance and LocalController.instance()
local target = nil
if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local pnum = tonumber(ptIdx) or tonumber(ptObj and ptObj.pointId) or 0
    if tonumber(ptObj and ptObj.pointType or -1) == (PointType and PointType.WorldMonster or 4) and pnum > 0 then
      local info = wpm:GetPointInfo(pnum)
      local pb = info and info._parsedExtra
      if not pb and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
        local okP, parsed = pcall(function() return PBController.ParsePbFromBytes('protobuf.WorldPointMonster', info.extraInfo) end)
        if okP and parsed then pb = parsed end
      end
      if pb and pb.monsterId and lc and TableName and TableName.Monster then
        local row = lc:getLine(TableName.Monster, tostring(pb.monsterId))
        if row and (tonumber(_safe_call(function() return row:getValue('boss') end, 0)) or 0) == 0 then
          local lv = tonumber(_safe_call(function() return row:getValue('level') end, 99)) or 99
          if not target or lv < target.lv then
            target = {{ pointId = tonumber(info and info.mainIndex or pnum) or pnum, uuid = (info and info.uuid) or 0, lv = lv }}
          end
        end
      end
    end
  end
end
if target then
  if not dryRun and MarchUtil and MarchUtil.SendCreateMarchMessage then
    pcall(function() MarchUtil.SendCreateMarchMessage(forms[1].uuid, MarchTargetType and MarchTargetType.ATTACK_MONSTER or 1, target.pointId, target.uuid or 0, 0, true, true, snap.serverId) end)
  end
  return _enc({{ ok = true, attacked = 1, pointId = target.pointId, lv = target.lv, formationUuid = tostring(forms[1].uuid) }})
end
if not dryRun and SFSNetwork and MsgDefines and MsgDefines.FindMonster and snap.mainPos > 0 then
  pcall(function() SFSNetwork.SendMessage(MsgDefines.FindMonster, tonumber(snap.mainPos), 1, false) end)
end
return _enc({{ ok = true, attacked = 0, reason = 'searching_creep' }})
""",
                    timeout=8.0,
                )
                if not dry_run and context is not None and sub_res.get("formationUuid"):
                    _record_used_formations(context, pid, [str(sub_res["formationUuid"])])
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> attacked={sub_res.get('attacked', 0)} {sub_res.get('reason', '')}")
            elif kind == "attack_hq":
                # Opt-in only (allow_pvp_hq_attack=True): NEVER breaks own Peace Shield, skips allies and shielded bases
                if not dry_run:
                    ensure_world_scene(cd, pid)
                sub_res = _eval_json(
                    cd,
                    pid,
                    f"""
local dryRun = {str(dry_run).lower()}
local snap = _get_player_snapshot()
if snap.shieldEndTime and tonumber(snap.shieldEndTime) > (snap.serverSec or 0) then
  return _enc({{ ok = true, attacked = 0, reason = 'skipped_own_peace_shield_active' }})
end
local forms = _pick_free_formations({int(cfg.get('formation_reserve', 0))}, {_used_formations_lua(context, pid)}, not dryRun)
if #forms == 0 then return _enc({{ ok = true, attacked = 0, reason = 'no_free_formation' }}) end
local wpm = DataCenter and DataCenter.WorldPointManager
local target = nil
local nowSec = tonumber(snap.serverSec or os.time()) or os.time()
local myUid = tostring(snap.uid or '')
local myAlly = tostring(snap.allianceUid or '')
if wpm and wpm.allViewPoints and wpm.GetPointInfo then
  for ptIdx, ptObj in pairs(wpm.allViewPoints) do
    local pnum = tonumber(ptIdx) or tonumber(ptObj and ptObj.pointId) or 0
    if tonumber(ptObj and ptObj.pointType or -1) == (PointType and PointType.WorldCity or 6) and pnum > 0 then
      local info = wpm:GetPointInfo(pnum)
      local bi = info and info.buildInfo
      if type(bi) == 'table' then
        local tUid = tostring(bi.uid or bi.ownerUid or '')
        local tAlly = tostring(bi.allianceId or bi.allianceUid or '')
        local protEnd = tonumber(bi.protectEndTime or 0) or 0
        if protEnd > 1e12 then protEnd = math.floor(protEnd / 1000) end
        local lv = tonumber(bi.level or bi.mainLevel or 99) or 99
        local isSameAlly = (myAlly ~= '' and myAlly ~= '0' and tAlly == myAlly)
        if tUid ~= '' and tUid ~= myUid and not isSameAlly and protEnd <= nowSec and lv <= 15 then
          if not target or lv < target.lv then
            target = {{ pointId = tonumber(info.mainIndex or pnum) or pnum, uuid = info.uuid or 0, lv = lv, uid = tUid }}
          end
        end
      end
    end
  end
end
if not target then
  return _enc({{ ok = true, attacked = 0, reason = 'no_safe_unshielded_low_hq_found' }})
end
if not dryRun and MarchUtil and MarchUtil.SendCreateMarchMessage then
  pcall(function() MarchUtil.SendCreateMarchMessage(forms[1].uuid, MarchTargetType and MarchTargetType.ATTACK_PLAYER or 3, target.pointId, target.uuid or 0, 0, true, true, snap.serverId) end)
end
return _enc({{ ok = true, attacked = 1, pointId = target.pointId, lv = target.lv, formationUuid = tostring(forms[1].uuid) }})
""",
                    timeout=8.0,
                )
                if not dry_run and context is not None and sub_res.get("formationUuid"):
                    _record_used_formations(context, pid, [str(sub_res["formationUuid"])])
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> opt-in HQ attack={sub_res.get('attacked', 0)} ({sub_res.get('reason') or ('Lv' + str(sub_res.get('lv', '?')) + '@' + str(sub_res.get('pointId', 0)))})")
            else:
                detail_lines.append(f"[{tid}] {desc} ({cur_n}/{tot_n}) -> SKIPPED (unmapped daily task kind={kind})")
                skipped.append({"id": tid, "kind": kind, "desc": desc, "reason": "unmapped_kind"})
                continue

            executed.append({"id": tid, "kind": kind, "desc": desc, "ok": bool(sub_res.get("ok", True)), "result": sub_res})
            if not sub_res.get("ok", True) and sub_res.get("error"):
                errors.append(f"{tid}/{kind}: {sub_res['error']}")
        except Exception as exc:
            errors.append(f"{tid}/{kind}: {exc}")
            detail_lines.append(f"[{tid}] {desc} -> ERROR: {exc}")

    # Final claim pass: claim ALL completed Daily Tasks + ALL unlocked Milestone Chests (30..150)
    if not dry_run and executed:
        time.sleep(1.0)
    claim_res = _claim_all_daily_tasks_and_boxes(cd, pid, dry_run=dry_run)

    # Final post-run scan
    scan_after = _scan_daily_tasks_live(cd, pid) if not dry_run else scan_before
    tasks_after = scan_after.get("tasks") or []
    score_after = int(scan_after.get("active_score") or score_before)
    todo_after = [t for t in tasks_after if int(t.get("state") or 0) == 0]
    claimable_after = [t for t in tasks_after if int(t.get("state") or 0) == 1]
    claimed_after = [t for t in tasks_after if int(t.get("state") or 0) == 2]
    boxes_claimed_cnt = sum(1 for b in (scan_after.get("boxes") or []) if int(b.get("state") or 0) == 2)
    boxes_total_cnt = len(scan_after.get("boxes") or [])

    detail_lines.append(
        f"Daily Tasks Claimed: +{claim_res.get('tasks_claimed', 0)} tasks | Milestone Chests Claimed: {boxes_claimed_cnt}/{boxes_total_cnt} | Score: {score_before} -> {score_after}/{max_score}"
    )
    if todo_after:
        rem_strs = [f"{t.get('desc_formatted') or t.get('id')} ({t.get('num', 0)}/{t.get('totalNum', 0)})" for t in todo_after]
        detail_lines.append(f"Remaining TODO ({len(todo_after)}): " + "; ".join(rem_strs))

    action_label = "completed_and_claimed" if (executed or claim_res.get("tasks_claimed", 0) > 0 or claim_res.get("boxes_sent")) else "all_done"
    summary_msg = (
        f"Daily Tasks: {len(executed)} attempted, +{claim_res.get('tasks_claimed', 0)} claimed, "
        f"score {score_before}->{score_after}/{max_score}, chests {boxes_claimed_cnt}/{boxes_total_cnt}, "
        f"{len(todo_after)} remaining ({len(skipped)} skipped for safety)"
    )

    return {
        "ok": len(errors) == 0,
        "task": "daily_tasks_complete",
        "dry_run": dry_run,
        "action": action_label,
        "message": summary_msg,
        "score_before": score_before,
        "score_after": score_after,
        "max_score": max_score,
        "boxes_claimed": boxes_claimed_cnt,
        "boxes_total": boxes_total_cnt,
        "executed_count": len(executed),
        "executed": [{"id": e["id"], "kind": e["kind"], "desc": e["desc"], "ok": e["ok"]} for e in executed],
        "skipped": skipped,
        "claim_result": claim_res,
        "remaining_todo": [
            {"id": t.get("id"), "desc": t.get("desc_formatted"), "num": t.get("num"), "totalNum": t.get("totalNum")}
            for t in todo_after
        ],
        "errors": errors,
        "detail_lines": detail_lines,
    }


def run_free_recruits(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("free_recruits") or {}
    c_hero = bool(task_cfg.get("claim_hero_recruits", True))
    c_small = bool(task_cfg.get("claim_small_people", True))
    open_chests = bool(task_cfg.get("open_safe_chests", True))
    max_chests = int(task_cfg.get("max_chests_per_cycle", 20) or 20)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local cHero = {str(c_hero).lower()}
local cSmall = {str(c_small).lower()}
local openChests = {str(open_chests).lower()}
local maxChests = {max_chests}

local snap = _get_player_snapshot()
local dc = DataCenter
local nowMs = (snap.serverSec or 0) * 1000
local out = {{
  ok = true,
  task = 'free_recruits',
  dry_run = dryRun,
  hero_recruits = {{}},
  small_people_free = false,
  chests_opened = {{}},
  chests_total_count = 0,
  action = 'none',
}}

local ldm = dc and dc.LotteryDataManager
if cHero and ldm then
  local dict = _safe_call(function() return ldm:GetAllShowLotteryDict() end, nil) or ldm.lotteryDict or {{}}
  for k, lv in pairs(dict) do
    if type(lv) == 'table' then
      local lid = tostring(lv.id or k)
      local dFree = tonumber(lv.dailyFree or 0) or 0
      local cdFree = (tonumber(lv.free_cd or 0) or 0) > 0 and (tonumber(lv.nextFreeTime or 0) or 0) <= nowMs and nowMs > 0
      if dFree > 0 or cdFree then
        if not dryRun and SFSNetwork and MsgDefines and MsgDefines.LotteryHeroCard then
          pcall(function() SFSNetwork.SendMessage(MsgDefines.LotteryHeroCard, tostring(lid), 0, 1, '', 0) end)
        end
        table.insert(out.hero_recruits, lid)
      end
    end
  end
end

local spr = dc and dc.SmallPeopleRecruitDataManager
if cSmall and spr and _safe_call(function() return spr:IsRecruitOpen() end, false) then
  local info = _safe_call(function() return spr:GetRecruitInfo() end, nil)
  if type(info) == 'table' and tonumber(info.freeCount or info.free or 0) > 0 then
    out.small_people_free = true
  end
end

local idata = dc and dc.ItemData
if openChests and idata and idata.ItemInfos and maxChests > 0 then
  local itm = dc.ItemTemplateManager
  for uuid, info in pairs(idata.ItemInfos) do
    if out.chests_total_count >= maxChests then break end
    local cnt = tonumber(info and info.count or 0) or 0
    if cnt > 0 and tostring(info.use or '') == '1' then
      local tmpl = info.template or (itm and _safe_call(function() return itm:GetItemTemplate(tonumber(info.itemId)) end, nil))
      local tp = tmpl and tonumber(tmpl.type or -1) or -1
      local pages = tmpl and tonumber(tmpl.pages or -1) or -1
      local para1 = tostring(info.para1 or '')
      -- Strictly open only safe drop/reward chests (pages==4 and tp in {{1,5}}, excluding tp==59 choice boxes and tp==3 RSS/stamina and tp==204 speedups)
      if pages == 4 and (tp == 1 or tp == 5) and para1 ~= '' then
        local nm = (tmpl and tmpl.name and Localization and Localization.GetString and tostring(_safe_call(function() return Localization:GetString(tostring(tmpl.name)) end, '') or ''):lower()) or ''
        if not (nm:find('shield') or nm:find('peace') or nm:find('truce') or nm:find('tele') or nm:find('stamina') or nm:find('speed')) then
          local openQty = math.min(cnt, maxChests - out.chests_total_count)
          if openQty > 0 then
            if not dryRun then
              if idata.UseTool then
                pcall(function() idata:UseTool(tonumber(info.itemId), openQty) end)
              elseif SFSNetwork and MsgDefines and MsgDefines.ItemUse then
                pcall(function() SFSNetwork.SendMessage(MsgDefines.ItemUse, {{uuid = tostring(uuid), num = openQty}}) end)
              end
            end
            table.insert(out.chests_opened, {{id = tostring(info.itemId), qty = openQty}})
            out.chests_total_count = out.chests_total_count + openQty
          end
        end
      end
    end
  end
end

if #out.hero_recruits > 0 or out.chests_total_count > 0 then
  out.action = 'claimed'
  pcall(_dismiss_modal_dialogs)
end
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=10.0)


def run_garage_upgrades(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("garage_upgrades") or {}
    only_monday = bool(task_cfg.get("only_monday", True))
    up_refit = bool(task_cfg.get("upgrade_refit", True))
    free_only = bool(task_cfg.get("use_refit_free_only", True))
    install_comp = bool(task_cfg.get("install_better_components", True))
    merge_comp = bool(task_cfg.get("merge_components", True))
    max_steps = int(task_cfg.get("max_refit_steps_per_cycle", 5) or 5)

    lua = _LUA_SERVER_TIME_HELPER + f"""
local dryRun = {str(dry_run).lower()}
local onlyMonday = {str(only_monday).lower()}
local upRefit = {str(up_refit).lower()}
local freeOnly = {str(free_only).lower()}
local installComp = {str(install_comp).lower()}
local mergeComp = {str(merge_comp).lower()}
local maxSteps = {max_steps}

local snap = _get_player_snapshot()
local wday, dayName = _get_server_weekday(snap.serverSec)
local dc = DataCenter
local grm = dc and dc.GarageRefitManager
local gcm = dc and dc.GarageComponManager
local out = {{
  ok = true,
  task = 'garage_upgrades',
  dry_run = dryRun,
  only_monday = onlyMonday,
  server_wday = wday,
  server_day_name = dayName,
  installed_all = false,
  merged_slots = {{}},
  refit_steps = 0,
  action = 'none',
}}

if onlyMonday and wday ~= 2 then
  out.action = 'skipped_not_monday'
  return _enc(out)
end

if gcm and _safe_call(function() return gcm:CheckOpen() end, false) then
  if installComp and _safe_call(function() return gcm:CheckCanEquipRed() end, false) then
    if not dryRun and SFSNetwork and MsgDefines and MsgDefines.CarComponInstallAll then
      pcall(function() SFSNetwork.SendMessage(MsgDefines.CarComponInstallAll) end)
    end
    out.installed_all = true
  end
  if mergeComp and _safe_call(function() return gcm:CheckCanMergeRed() end, false) then
    for pos = 1, 6 do
      if _safe_call(function() return gcm:CheckCanMerge(pos) end, false) then
        if not dryRun and SFSNetwork and MsgDefines and MsgDefines.CarComponUpgradeAll then
          pcall(function() SFSNetwork.SendMessage(MsgDefines.CarComponUpgradeAll, pos) end)
        end
        table.insert(out.merged_slots, pos)
      end
    end
  end
end

if upRefit and grm and not _safe_call(function() return grm:IsMaxLevel() end, true) then
  -- Verified Megamind signatures: GetFreeCount(self), GetGarageFreeCount(self, id), GetUsedFreeCount(self), GetCanClickUpgradeCount(self)
  local rawFree1 = tonumber(_safe_call(function() return grm:GetFreeCount() end, 0)) or 0
  local rawFree2 = tonumber(_safe_call(function() return grm:GetGarageFreeCount(1) end, 0)) or 0
  local usedFree = tonumber(_safe_call(function() return grm:GetUsedFreeCount() end, 0)) or 0
  local fieldFree = tonumber(grm.freeCount or 0) or 0
  local freeCnt = math.max(rawFree1, rawFree2, math.max(0, fieldFree - usedFree))
  local canClick = tonumber(_safe_call(function() return grm:GetCanClickUpgradeCount() end, 0)) or 0
  local canLv = _safe_call(function() return grm:IsCanLeveUp() end, false) and true or false
  out.free_count = freeCnt
  out.used_free_count = usedFree
  out.can_click_count = canClick
  out.refit_mode = freeOnly and 'free_only' or 'wrench_enabled'

  local steps = 0
  if freeCnt > 0 then
    steps = math.min(freeCnt, maxSteps)
    out.refit_source = 'free'
  elseif not freeOnly and (canClick > 0 or canLv) then
    steps = math.min(math.max(1, canClick), maxSteps)
    out.refit_source = 'golden_wrenches'
  else
    out.refit_source = 'none'
    if freeOnly and (canClick > 0 or canLv) then
      out.reason = 'free_refits_exhausted_wrench_guard_active'
    end
  end
  if steps > 0 and SFSNetwork and MsgDefines then
    if not dryRun then
      if _safe_call(function() return grm:IsOpenNewGarageRefit() end, false) and MsgDefines.GarageRefitNewAddExp then
        pcall(function() SFSNetwork.SendMessage(MsgDefines.GarageRefitNewAddExp, {{count = steps}}) end)
        out.refit_steps = steps
      elseif MsgDefines.GarageRefit then
        local refitUuid = nil
        local rd = (grm.GetGarageRefitData and _safe_call(function() return grm:GetGarageRefitData() end, nil)) or grm.garageRefitInfo
        if type(rd) == 'table' then
          refitUuid = tonumber(rd.uuid)
          if not refitUuid then
            for _, rv in pairs(rd) do
              if type(rv) == 'table' and tonumber(rv.uuid or 0) > 0 then
                refitUuid = tonumber(rv.uuid)
                break
              end
            end
          end
        end
        if refitUuid and refitUuid > 0 then
          pcall(function() SFSNetwork.SendMessage(MsgDefines.GarageRefit, {{uuid = refitUuid, count = steps}}) end)
          out.refit_steps = steps
        end
      end
    else
      out.refit_steps = steps
    end
  end
end

if out.installed_all or #out.merged_slots > 0 or out.refit_steps > 0 then
  out.action = 'upgraded'
end
return _enc(out)
"""
    return _eval_json(cd, pid, lua, timeout=10.0)


_HERO_EVENT_KEYWORDS: tuple[str, ...] = (
    "hero",
    "heroes",
    "shard",
    "shards",
    "fragment",
    "fragments",
    "skill",
    "skills",
    "star",
    "stars",
    "recruit",
    "recruits",
    "recruitment",
    "equip",
    "equipment",
    "gear",
    "exclusive",
    "awakening",
    "initiative",
)
_HERO_EVENT_KEYWORD_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (kw, re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE))
    for kw in _HERO_EVENT_KEYWORDS
)


def _is_hero_progression_event_active(
    probe: dict[str, Any] | None,
    server_wday: int = 0,
) -> tuple[bool, str, str]:
    """Return (is_active, reason, active_theme) for Hero Progression / Alliance Duel Day 4."""
    # Lua os.date('*t').wday: 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu (VS Day 4: Hero Initiative), 6=Fri, 7=Sat
    if int(server_wday or 0) == 5:
        theme = ""
        if isinstance(probe, dict):
            theme = str(probe.get("vs_theme") or probe.get("theme") or "Alliance Duel Day 4 (Hero Initiative)")
        return True, "vs_hero_day_thursday", theme or "Alliance Duel Day 4 (Hero Initiative)"
    if isinstance(probe, dict) and probe.get("vs_open") and int(probe.get("vs_day") or 0) == 4:
        theme = str(probe.get("vs_theme") or probe.get("theme") or "VS Day 4: Hero Initiative")
        return True, "vs_hero_day_4", theme or "VS Day 4: Hero Initiative"
    if isinstance(probe, dict) and probe.get("ok", True) and not probe.get("error"):
        vs_day = int(probe.get("vs_day") or 0)
        texts = [
            str(probe.get("theme") or ""),
            str(probe.get("theme_raw") or ""),
            str(probe.get("vs_theme") or "") if vs_day in (0, 4) else "",
        ]
        blob = " ".join(texts).lower()
        for kw, pat in _HERO_EVENT_KEYWORD_PATTERNS:
            if pat.search(blob):
                active_theme = str(probe.get("theme") or (probe.get("vs_theme") if vs_day in (0, 4) else "") or kw).strip()
                return True, f"active_theme:{kw}", active_theme
    return False, "off_hero_day", ""


def _filter_hero_progression_targets(
    heroes: list[dict[str, Any]],
    *,
    target_scope: str = "formation_1",
    min_rarity: int = 4,
    pinned_hero_ids: list[int] | set[int] | None = None,
    single_hero_uuid: str = "",
) -> list[dict[str, Any]]:
    """Pure filter selecting target heroes according to Heroes tab scope & rarity settings."""
    pinned_set = {int(x) for x in (pinned_hero_ids or []) if not isinstance(x, bool) and str(x).isdigit()}
    scope = str(target_scope or "formation_1").strip().lower()
    single_uuid = str(single_hero_uuid or "").strip()
    if scope == "hero_uuid" and not single_uuid:
        return []
    out: list[dict[str, Any]] = []
    for h in heroes or []:
        if not isinstance(h, dict):
            continue
        huuid = str(h.get("uuid") or "").strip()
        hid = int(h.get("heroId") or 0)
        rarity = int(h.get("rarity") or 1)
        fidx = int(h.get("formationIndex") or 0)
        if single_uuid:
            if huuid == single_uuid or (single_uuid.isdigit() and hid == int(single_uuid)):
                out.append(h)
            continue
        if scope == "hero_uuid":
            continue
        if scope == "formation_1":
            if fidx == 1 and rarity >= min_rarity:
                out.append(h)
        elif scope == "all_formations":
            if fidx > 0 and rarity >= min_rarity:
                out.append(h)
        elif scope == "pinned":
            if hid in pinned_set:
                out.append(h)
        elif scope == "all_orange":
            if rarity >= 4:
                out.append(h)
        else:
            if rarity >= min_rarity:
                out.append(h)
    return out


def inspect_hero_progression(
    cd: Any,
    pid: int,
    include_probe: bool = True,
    allow_network_refresh: bool = False,
) -> dict[str, Any]:
    """Read-only live inspection of hero roster, EXP/shard/skill-book/gear materials, and upgrade readiness."""
    lua = _LUA_SERVER_TIME_HELPER + r"""
local snap = _get_player_snapshot()
local wday, dayName = _get_server_weekday(snap.serverSec)
local dc = DataCenter
local hdm = dc and dc.HeroDataManager
local hem = dc and dc.HeroEquipManager
local hsp = dc and dc.HeroSPEquipManager
local afm = dc and dc.ArmyFormationDataManager
local idata = dc and dc.ItemData
local itm = dc and dc.ItemTemplateManager
local hlum = dc and dc.HeroLevelUpTemplateManager
local hetm = dc and dc.HeroEquipTemplateManager

local function _loc(raw)
  local s = tostring(raw or '')
  if s == '' then return '' end
  if Localization and Localization.GetString and string.match(s, '^%d+$') then
    local ok, v = pcall(function() return Localization:GetString(s) end)
    if ok and v and tostring(v) ~= '' then return tostring(v) end
  end
  return s
end

local out = {
  ok = true,
  server_wday = wday,
  server_day_name = dayName,
  hq_max_hero_level = 0,
  materials = {
    hero_exp_total = 0,
    hero_exp_items = {},
    skill_books = { orange = 0, purple = 0, blue = 0, total = 0 },
    universal_shards = { orange = 0, purple = 0, blue = 0, total = 0, by_color = _jdict({}) },
    enhancement_alloy_total = 0,
    enhancement_alloy_exp_total = 0,
    enhancement_alloy_items = {},
    power_cores = 0,
    universal_equip_materials = 0,
    universal_sp_shards = 0,
    universal_break_minerals = 0,
    zent = tonumber((snap.resources and (snap.resources.money or snap.resources.zent)) or 0) or 0,
  },
  heroes = {},
  summary = {
    total_heroes = 0,
    orange_heroes = 0,
    upgradable_level = 0,
    upgradable_star_own = 0,
    upgradable_star_uni = 0,
    upgradable_skills = 0,
    upgradable_gear = 0,
    better_gear_heroes = 0,
    upgradable_sp = 0,
  },
}

if not hdm then
  out.ok = false
  out.error = 'HeroDataManager unavailable'
  return _enc(out)
end

-- 1. Build itemId -> {count, uuid, expVal, color, type, type2, name} map
local itemById = {}
local expItems = {}
local alloyItems = {}
local commonDebrisSet = {}
if HeroUtils and HeroUtils.GetAllCommonHeroDebris then
  local okC, cdList = pcall(function() return HeroUtils.GetAllCommonHeroDebris() end)
  if okC and type(cdList) == 'table' then
    for k, v in pairs(cdList) do
      local iv = tonumber(v) or tonumber(k) or 0
      if iv > 0 then commonDebrisSet[iv] = true end
    end
  end
end
local goldDebrisId = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetGoldHeroDebrisId and HeroUtils.GetGoldHeroDebrisId() end, 210454)) or 210454
if goldDebrisId > 0 then commonDebrisSet[goldDebrisId] = true end
commonDebrisSet[210454] = true

if idata and type(idata.ItemInfos) == 'table' then
  for uuid, info in pairs(idata.ItemInfos) do
    if type(info) == 'table' then
      local iid = tonumber(info.itemId or info.id or 0) or 0
      local cnt = tonumber(info.count or info.num or 0) or 0
      if iid > 0 and cnt > 0 then
        local tpl = info.template or (itm and _safe_call(function() return itm:GetItemTemplate(iid) end, nil))
        local tp = tonumber((tpl and (tpl.type or tpl.itemType)) or info.type or 0) or 0
        local tp2 = tonumber((tpl and tpl.type2) or info.type2 or 0) or 0
        local col = tonumber((tpl and (tpl.color or tpl.quality)) or 1) or 1
        local pVal = tonumber(info.para1 or (tpl and (tpl.para1 or tpl.para)) or 0) or 0
        local nm = _loc((tpl and (tpl.name or tpl.itemName)) or tostring(iid))
        if not itemById[iid] then
          itemById[iid] = { itemId = iid, uuid = tostring(uuid), count = cnt, type = tp, type2 = tp2, color = col, para = pVal, name = nm }
        else
          itemById[iid].count = itemById[iid].count + cnt
        end
        if tp == 91 and (tp2 == 1 or pVal > 0) then
          local ev = pVal > 0 and pVal or 1
          out.materials.hero_exp_total = out.materials.hero_exp_total + (ev * cnt)
          table.insert(expItems, { itemId = iid, uuid = tostring(uuid), name = nm, count = cnt, expVal = ev })
        end
        if tp == 211 or tp == 132 then
          local av = pVal > 0 and pVal or 100
          out.materials.enhancement_alloy_total = out.materials.enhancement_alloy_total + cnt
          out.materials.enhancement_alloy_exp_total = out.materials.enhancement_alloy_exp_total + (av * cnt)
          table.insert(alloyItems, { itemId = iid, uuid = tostring(uuid), name = nm, count = cnt, expVal = av, color = col })
        end
        if iid == 230101 then out.materials.skill_books.orange = out.materials.skill_books.orange + cnt end
        if iid == 230102 then out.materials.skill_books.purple = out.materials.skill_books.purple + cnt end
        if iid == 230103 then out.materials.skill_books.blue = out.materials.skill_books.blue + cnt end
        if iid == 230109 then out.materials.power_cores = out.materials.power_cores + cnt end
        if iid == 230126 then out.materials.universal_equip_materials = out.materials.universal_equip_materials + cnt end
        if iid == 260000 then out.materials.universal_sp_shards = out.materials.universal_sp_shards + cnt end
        if iid == 214000 then out.materials.universal_break_minerals = out.materials.universal_break_minerals + cnt end
        local isCommonShard = commonDebrisSet[iid] and true or false
        if not isCommonShard and HeroUtils and HeroUtils.IsCommonHeroDebris then
          local okIsC, resIsC = pcall(function() return HeroUtils.IsCommonHeroDebris(iid) end)
          if okIsC and resIsC then
            commonDebrisSet[iid] = true
            isCommonShard = true
          end
        end
        if isCommonShard then
          out.materials.universal_shards.total = out.materials.universal_shards.total + cnt
          local cKey = tostring(col)
          out.materials.universal_shards.by_color[cKey] = (out.materials.universal_shards.by_color[cKey] or 0) + cnt
          if col >= 4 or iid == 210454 then
            out.materials.universal_shards.orange = out.materials.universal_shards.orange + cnt
          elseif col == 3 then
            out.materials.universal_shards.purple = out.materials.universal_shards.purple + cnt
          elseif col == 2 then
            out.materials.universal_shards.blue = out.materials.universal_shards.blue + cnt
          end
        end
      end
    end
  end
end
out.materials.skill_books.total = out.materials.skill_books.orange + out.materials.skill_books.purple + out.materials.skill_books.blue
table.sort(expItems, function(a, b) return (a.expVal or 0) > (b.expVal or 0) end)
table.sort(alloyItems, function(a, b) return (a.expVal or 0) > (b.expVal or 0) end)
out.materials.hero_exp_items = expItems
out.materials.enhancement_alloy_items = alloyItems

local hqMaxLv = tonumber(_safe_call(function() return hlum and hlum.GetMaxLevelByMainLv and hlum:GetMaxLevelByMainLv() end, 0)) or 0
if hqMaxLv <= 0 then hqMaxLv = tonumber(hdm.maxLevel or 0) or 0 end
out.hq_max_hero_level = hqMaxLv

-- 2. Map hero UUID/ID -> Formation index (1..4)
local heroFormation = {}
local formList = (afm and afm.GetArmyFormationList and _safe_call(function() return afm:GetArmyFormationList() end, nil)) or (afm and afm.ArmyFormationList) or {}
if type(formList) == 'table' then
  for idxKey, f in pairs(formList) do
    if type(f) == 'table' then
      local fidx = tonumber(f.index or f.formationIndex or idxKey or 0) or 0
      local hArr = f.heroes or f.heroUuids or f.heroIds or (_safe_call(function() return f.GetCurHeroes and f:GetCurHeroes() end, nil)) or {}
      if type(hArr) == 'table' and fidx > 0 then
        for _, hv in pairs(hArr) do
          local s = ''
          if type(hv) == 'table' then
            s = tostring(hv.uuid or hv.heroUuid or hv.heroId or hv.id or '')
          else
            s = tostring(hv or '')
          end
          if s ~= '' and s ~= '0' and (not heroFormation[s] or fidx < heroFormation[s]) then
            heroFormation[s] = fidx
          end
        end
      end
    end
  end
end

local CAMP_NAMES = { [1] = 'Blood Rose', [2] = 'Wings of Dawn', [3] = 'Guard of Order' }
local RARITY_NAMES = { [5] = 'Orange', [4] = 'Orange', [3] = 'Purple', [2] = 'Blue', [1] = 'Green' }
local SLOT_NAMES = { [1] = 'Weapon', [2] = 'Armor', [3] = 'Boots', [4] = 'Accessory' }

local rawList = (hdm.GetHeroSortList and _safe_call(function() return hdm:GetHeroSortList() end, nil))
  or (hdm.GetAllHeroList and _safe_call(function() return hdm:GetAllHeroList() end, nil))
  or hdm.allHero or {}

local seenHero = {}
local heroesOut = {}
for _, h in pairs(rawList) do
  if type(h) == 'table' and h.uuid then
    local huuid = tostring(h.uuid)
    local hid = tonumber(h.heroId or h.id or 0) or 0
    if not seenHero[huuid] and hid > 0 then
      seenHero[huuid] = true
      local rawName = _safe_call(function() return HeroUtils and HeroUtils.GetHeroNameByConfigId and HeroUtils.GetHeroNameByConfigId(hid) end, '')
      local hName = _loc(rawName)
      if hName == '' then hName = _loc(h.name or (h.template and h.template.name) or ('Hero #' .. tostring(hid))) end
      local rarity = tonumber(h.rarity or (h.template and h.template.rarity) or 1) or 1
      local camp = tonumber(h.camp or (h.template and h.template.camp) or _safe_call(function() return HeroUtils and HeroUtils.GetCampByHeroId and HeroUtils.GetCampByHeroId(hid) end, 0) or 0) or 0
      local power = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetHeroPower and HeroUtils.GetHeroPower(h) end, h.power or 0)) or 0
      local lv = tonumber(h.level or h.lv or 1) or 1
      local curMaxLv = tonumber(h.curMaxLevel or h.finalLevel or _safe_call(function() return HeroUtils and HeroUtils.GetHeroFinalLevel and HeroUtils.GetHeroFinalLevel(h) end, 0) or hqMaxLv or 200) or 200
      if hqMaxLv > 0 and curMaxLv > hqMaxLv then curMaxLv = hqMaxLv end
      local needExp = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetLevelUpNeedExp and HeroUtils.GetLevelUpNeedExp(h) end, 0)) or 0
      local canLevelUp = (lv < curMaxLv) and (out.materials.hero_exp_total > 0) and (needExp <= 0 or out.materials.hero_exp_total >= needExp)
      local canBreak = false
      if lv >= curMaxLv and hdm.HasBeyondHero then
        local bTimes = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetBeyondTimesByLevel and HeroUtils.GetBeyondTimesByLevel(lv) end, 0)) or 0
        if bTimes > 0 and not _safe_call(function() return HeroUtils and HeroUtils.IsNeedUpMainBuild and HeroUtils.IsNeedUpMainBuild(h) end, false) then
          canBreak = true
        end
      end

      -- Stars / Rank & Shards
      local star, starProg = 0, 0
      if HeroUtils and HeroUtils.GetHeroStarAndProgress then
        local okS, s1, s2 = pcall(function() return HeroUtils.GetHeroStarAndProgress(h) end)
        if okS then
          star = tonumber(s1 or 0) or 0
          starProg = tonumber(s2 or 0) or 0
        end
      end
      if star <= 0 then
        star = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetHeroStarCount and HeroUtils.GetHeroStarCount(h) end, h.star or 0)) or 0
      end
      local maxStar = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetMaxStarByRarity and HeroUtils.GetMaxStarByRarity(rarity) end, 5)) or 5
      local isStarMax = _safe_call(function() return HeroUtils and HeroUtils.IsReachStarLimit and HeroUtils.IsReachStarLimit(h) end, false) and true or (star >= maxStar)
      local debrisId = tonumber(_safe_call(function() return HeroUtils and HeroUtils.GetHeroDebrisIdByHeroId and HeroUtils.GetHeroDebrisIdByHeroId(hid) end, (h.template and h.template.hero_pieces) or 0)) or 0
      local ownedShards = (debrisId > 0 and itemById[debrisId] and itemById[debrisId].count) or 0
      local needShards = 0
      if not isStarMax then
        local okCost, c1, c2 = pcall(function() return HeroUtils and HeroUtils.GetHeroStarCostByHeroData and HeroUtils.GetHeroStarCostByHeroData(h) end)
        if okCost then
          if type(c1) == 'table' then
            needShards = tonumber(c1.num or c1.count or c1.cost or c1[2] or 0) or 0
          else
            needShards = tonumber(c2 or c1 or 0) or 0
          end
        end
      end
      local uniAvail = (rarity >= 4 and out.materials.universal_shards.orange)
        or (rarity == 3 and out.materials.universal_shards.purple)
        or (rarity == 2 and out.materials.universal_shards.blue) or 0
      local canStarOwn = (not isStarMax) and (needShards > 0) and (ownedShards >= needShards)
      local canStarUni = (not isStarMax) and (needShards > 0) and (ownedShards < needShards) and ((ownedShards + uniAvail) >= needShards)

      -- Skills
      local skillsOut = {}
      local upSkillsCnt = 0
      local rawSkills = h.skills or h.skillList or _safe_call(function() return HeroUtils and HeroUtils.GetHeroSkillList and HeroUtils.GetHeroSkillList(hid, h) end, nil) or {}
      local defaultSkillBook = (rarity >= 4 and 230101) or (rarity == 3 and 230102) or 230103
      if type(rawSkills) == 'table' then
        local sIdx = 0
        for skKey, sv in pairs(rawSkills) do
          sIdx = sIdx + 1
          local idx = tonumber((type(sv) == 'table' and (sv.index or sv.skillIndex or sv.pos)) or (type(skKey) == 'number' and skKey) or sIdx) or sIdx
          local sid = tonumber((type(sv) == 'table' and (sv.id or sv.skillId)) or (type(sv) == 'number' and sv) or 0) or 0
          local slv = tonumber((type(sv) == 'table' and (sv.lv or sv.level)) or 1) or 1
          local smax = tonumber((type(sv) == 'table' and (sv.maxLevel or sv.maxLv)) or _safe_call(function() return HeroUtils and HeroUtils.GetSkillLevelLimit and HeroUtils.GetSkillLevelLimit(hid, idx, star, lv) end, 10) or 10) or 10
          local sItemId, sCostNum = defaultSkillBook, 0
          if sid > 0 and HeroUtils and HeroUtils.GetSkillUpgradeItemAndNum then
            local okSc, si, sn = pcall(function() return HeroUtils.GetSkillUpgradeItemAndNum(sid, slv) end)
            if okSc then
              if type(si) == 'table' then
                sItemId = tonumber(si.itemId or si.id or si[1] or defaultSkillBook) or defaultSkillBook
                sCostNum = tonumber(si.num or si.count or si[2] or 0) or 0
              else
                if tonumber(si or 0) > 0 then sItemId = tonumber(si) end
                sCostNum = tonumber(sn or 0) or 0
              end
            end
          end
          local ownedBook = (sItemId > 0 and itemById[sItemId] and itemById[sItemId].count) or 0
          local canSk = (slv > 0 and slv < smax and sCostNum > 0 and ownedBook >= sCostNum)
          if canSk then upSkillsCnt = upSkillsCnt + 1 end
          local sName = _loc(_safe_call(function() return HeroUtils and HeroUtils.GetSkillName and HeroUtils.GetSkillName(sid) end, 'Skill ' .. tostring(idx)))
          table.insert(skillsOut, {
            index = idx,
            id = sid,
            name = sName ~= '' and sName or ('Skill ' .. tostring(idx)),
            level = slv,
            maxLevel = smax,
            itemId = sItemId,
            costNum = sCostNum,
            ownedItem = ownedBook,
            canUpgrade = canSk,
          })
        end
        table.sort(skillsOut, function(a, b) return (a.index or 0) < (b.index or 0) end)
      end

      -- Equipped Gear (4 slots)
      local gearOut = {}
      local upGearCnt, prGearCnt = 0, 0
      local hasBetterGear = false
      local suggestUuids = {}
      if hem then
        hasBetterGear = _safe_call(function() return hem.HasAnyBetterEquip and hem:HasAnyBetterEquip(hid) end, false) and true or false
        local sug = _safe_call(function() return hem.GetSuggestUnEquipUuidListByHeroId and hem:GetSuggestUnEquipUuidListByHeroId(hid) end, nil)
        if type(sug) == 'table' then
          for _, su in pairs(sug) do
            if su and tostring(su) ~= '' then table.insert(suggestUuids, tostring(su)) end
          end
          if #suggestUuids > 0 then hasBetterGear = true end
        end
        for slot = 1, 4 do
          local eq = _safe_call(function() return hem.GetEquipByHeroIdAndSlot and hem:GetEquipByHeroIdAndSlot(hid, slot) end, nil)
          if type(eq) == 'string' or type(eq) == 'number' then
            eq = _safe_call(function() return hem.GetEquipByUuid and hem:GetEquipByUuid(eq) end, nil)
          end
          if type(eq) == 'table' and (eq.uuid or eq.id) then
            local equuid = tostring(eq.uuid or eq.id)
            local eqId = tonumber(eq.equipId or eq.configId or eq.id or 0) or 0
            local eqLv = tonumber(eq.level or eq.lv or 1) or 1
            local eqQual = tonumber(eq.quality or (eq.template and eq.template.quality) or 1) or 1
            local eqProm = tonumber(eq.promoteLevel or eq.promoteLv or eq.rank or 0) or 0
            local eqMaxLv = tonumber(_safe_call(function() return hetm and hetm.GetMaxLevel and hetm:GetMaxLevel(eq) end, eqQual >= 5 and 50 or (eqQual == 4 and 30 or 20))) or 20
            local eqPow = tonumber(_safe_call(function() return hem.GetEquipPower and hem:GetEquipPower(eq) end, 0)) or 0
            local eqNeedExp = tonumber(_safe_call(function() return hem.GetEquipLvUpNeedExp and hem:GetEquipLvUpNeedExp(equuid) end, 0)) or 0
            local canEqUp = _safe_call(function() return hem.IsEquipCanUpgrade and hem:IsEquipCanUpgrade(equuid, false) end, false) and true or false
            if not canEqUp and eqLv < eqMaxLv and eqNeedExp > 0 and out.materials.enhancement_alloy_exp_total >= eqNeedExp then
              canEqUp = true
            end
            canEqUp = canEqUp and (eqLv < eqMaxLv) and (eqNeedExp > 0)
            local canEqProm = _safe_call(function() return hem.IsEquipCanPromote and hem:IsEquipCanPromote(equuid, false) end, false) and true or false
            local promoteNeedFodder = (eqProm >= 23)
            if canEqUp then upGearCnt = upGearCnt + 1 end
            if canEqProm then prGearCnt = prGearCnt + 1 end
            table.insert(gearOut, {
              uuid = equuid,
              slot = slot,
              slotName = SLOT_NAMES[slot] or ('Slot ' .. tostring(slot)),
              equipId = eqId,
              quality = eqQual,
              level = eqLv,
              maxLevel = eqMaxLv,
              promoteLevel = eqProm,
              promoteNeedFodder = promoteNeedFodder,
              power = eqPow,
              needExp = eqNeedExp,
              canUpgrade = canEqUp,
              canPromote = canEqProm,
            })
          else
            table.insert(gearOut, {
              uuid = '',
              slot = slot,
              slotName = SLOT_NAMES[slot] or ('Slot ' .. tostring(slot)),
              equipId = 0,
              quality = 0,
              level = 0,
              maxLevel = 0,
              promoteLevel = 0,
              promoteNeedFodder = false,
              power = 0,
              needExp = 0,
              canUpgrade = false,
              canPromote = false,
            })
          end
        end
      end

      -- Exclusive Weapon (SP Equip)
      local spInfo = { has = false, active = false, level = 0, maxLevel = 25, stage = 0, star = 0, canUpgrade = false, canBreak = false, costItemId = 0, needCount = 0, lackCount = 0, breakCostItemId = 0, breakNeedCount = 0, breakLackCount = 0 }
      if hsp and _safe_call(function() return hsp:HasSPEquip(hid) end, false) then
        local spd = _safe_call(function() return hsp:GetData(hid) end, nil)
        spInfo.has = true
        spInfo.active = _safe_call(function() return hsp:IsSPActive(hid) end, false) and true or false
        spInfo.level = tonumber((type(spd) == 'table' and (spd.level or spd.lv)) or 0) or 0
        spInfo.stage = tonumber(_safe_call(function() return hsp:GetStage(hid) end, 0)) or 0
        spInfo.star = tonumber(_safe_call(function() return hsp:GetStar(hid) end, 0)) or 0
        spInfo.canUpgrade = _safe_call(function() return hsp:IsEquipCanUpgrade(hid) end, false) and true or false
        spInfo.canBreak = _safe_call(function() return hsp:IsHeroEquipCanBreak(hid) end, false) and true or false
        local okSpc, spItem, spLack = pcall(function() return hsp:EquipUpgradeNeedItemAndLackCount(hid) end)
        if okSpc then
          if type(spItem) == 'table' then
            spInfo.costItemId = tonumber(spItem.itemId or spItem.id or 0) or 0
            spInfo.needCount = tonumber(spItem.num or spItem.count or 0) or 0
          else
            spInfo.costItemId = tonumber(spItem or 0) or 0
          end
          spInfo.lackCount = tonumber(spLack or 0) or 0
        end
        if hsp.GetEquipBreakNeedItem then
          local okBrk, brkItem, brkLack = pcall(function() return hsp:GetEquipBreakNeedItem(hid) end)
          if okBrk then
            if type(brkItem) == 'table' then
              spInfo.breakCostItemId = tonumber(brkItem.itemId or brkItem.id or brkItem[1] or 0) or 0
              spInfo.breakNeedCount = tonumber(brkItem.num or brkItem.count or brkItem[2] or 0) or 0
              if brkLack == nil and brkItem.lackCount ~= nil then brkLack = brkItem.lackCount end
            else
              spInfo.breakCostItemId = tonumber(brkItem or 0) or 0
            end
            spInfo.breakLackCount = tonumber(brkLack or 0) or 0
            if spInfo.breakNeedCount > 0 and brkLack == nil then
              local ownedBrk = (spInfo.breakCostItemId > 0 and itemById[spInfo.breakCostItemId] and itemById[spInfo.breakCostItemId].count) or 0
              spInfo.breakLackCount = math.max(0, spInfo.breakNeedCount - ownedBrk)
            end
          end
        end
      end

      local fidx = heroFormation[huuid] or heroFormation[tostring(hid)] or 0
      local anyUp = canLevelUp or canBreak or canStarOwn or upSkillsCnt > 0 or upGearCnt > 0 or hasBetterGear or spInfo.canUpgrade or spInfo.canBreak

      out.summary.total_heroes = out.summary.total_heroes + 1
      if rarity >= 4 then out.summary.orange_heroes = out.summary.orange_heroes + 1 end
      if canLevelUp or canBreak then out.summary.upgradable_level = out.summary.upgradable_level + 1 end
      if canStarOwn then out.summary.upgradable_star_own = out.summary.upgradable_star_own + 1 end
      if canStarUni then out.summary.upgradable_star_uni = out.summary.upgradable_star_uni + 1 end
      if upSkillsCnt > 0 then out.summary.upgradable_skills = out.summary.upgradable_skills + 1 end
      if upGearCnt > 0 then out.summary.upgradable_gear = out.summary.upgradable_gear + 1 end
      if hasBetterGear then out.summary.better_gear_heroes = out.summary.better_gear_heroes + 1 end
      if spInfo.canUpgrade or spInfo.canBreak then out.summary.upgradable_sp = out.summary.upgradable_sp + 1 end

      table.insert(heroesOut, {
        uuid = huuid,
        heroId = hid,
        name = hName,
        rarity = rarity,
        rarityName = RARITY_NAMES[rarity] or tostring(rarity),
        camp = camp,
        campName = CAMP_NAMES[camp] or 'Neutral',
        power = power,
        formationIndex = fidx,
        level = lv,
        curMaxLevel = curMaxLv,
        needExp = needExp,
        canLevelUp = canLevelUp,
        canBreakthrough = canBreak,
        star = star,
        starProgress = starProg,
        maxStar = maxStar,
        isStarMax = isStarMax,
        debrisItemId = debrisId,
        ownedShards = ownedShards,
        needShards = needShards,
        canStarUpOwn = canStarOwn,
        canStarUpWithUniversal = canStarUni,
        skills = skillsOut,
        upgradableSkillsCount = upSkillsCnt,
        gear = gearOut,
        hasBetterGear = hasBetterGear,
        suggestGearUuids = suggestUuids,
        upgradableGearCount = upGearCnt,
        promotableGearCount = prGearCnt,
        spEquip = spInfo,
        anyUpgradable = anyUp,
      })
    end
  end
end

table.sort(heroesOut, function(a, b)
  local fa = (a.formationIndex or 0) > 0 and a.formationIndex or 99
  local fb = (b.formationIndex or 0) > 0 and b.formationIndex or 99
  if fa ~= fb then return fa < fb end
  if (a.power or 0) ~= (b.power or 0) then return (a.power or 0) > (b.power or 0) end
  return (a.level or 0) > (b.level or 0)
end)
out.heroes = heroesOut
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=12.0)
    if isinstance(res, dict) and res.get("ok"):
        probe = _probe_preparedness_phase(cd, pid, allow_network_refresh=allow_network_refresh) if include_probe else None
        ev_active, ev_reason, ev_theme = _is_hero_progression_event_active(
            probe, int(res.get("server_wday") or 0)
        )
        res["event_status"] = {
            "hero_day_active": ev_active,
            "reason": ev_reason,
            "active_theme": ev_theme,
            "server_day_name": res.get("server_day_name", ""),
        }
    return res


_VALID_HERO_MODULES: tuple[str, ...] = ("", "level", "star", "skill", "gear", "gear_promote", "sp_equip")


def _lua_quote(val: Any) -> str:
    """Safely quote a Python string as a single-quoted Lua string literal."""
    s = str(val if val is not None else "")
    s = (
        s.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\x00", "")
    )
    return f"'{s}'"


def _promote_core_cost_for_level(promote_level: int) -> int:
    """Return Power Core (230109) cost for promoting from `promote_level` per ds_equip_promote.json."""
    lv = int(promote_level or 0)
    if lv <= 1:
        return 100
    if lv <= 4:
        return 200
    if lv <= 7:
        return 300
    if lv <= 10:
        return 500
    if lv <= 16:
        return 700
    if lv <= 22:
        return 1000
    if lv <= 28:
        return 1500
    if lv == 29:
        return 3000
    return 0


def run_hero_progression(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Automated Hero Progression: Leveling (+Breakthrough), Star-Ups, Skills, Gear & Exclusive Weapons."""
    ctx = context or {}
    task_cfg = dict(cfg.get("hero_progression") or {})

    def _cfg_int(key: str, default: int, src: dict[str, Any] | None = None) -> int:
        val = (task_cfg if src is None else src).get(key)
        if val is None or val == "" or isinstance(val, bool):
            return default
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    force_ignore_day_guard = bool(ctx.get("force_ignore_day_guard", False))
    only_hero_day = bool(task_cfg.get("only_hero_day", True)) and not force_ignore_day_guard
    target_scope = str(ctx.get("target_scope") or task_cfg.get("target_scope") or "formation_1").strip().lower()
    min_rarity = _cfg_int("min_rarity", 4)
    pinned_ids = [int(x) for x in (task_cfg.get("pinned_hero_ids") or []) if str(x).isdigit()]
    max_actions = max(1, _cfg_int("max_actions_per_cycle", _cfg_int("max_actions_per_cycle", 15), ctx))
    single_hero_uuid = str(ctx.get("hero_uuid") or "").strip()
    only_module = str(ctx.get("only_module") or "").strip().lower()

    if only_module not in _VALID_HERO_MODULES:
        err_msg = f"Unknown only_module: {only_module}"
        return {
            "ok": False,
            "task": "hero_progression",
            "dry_run": dry_run,
            "action": "invalid_module",
            "reason": err_msg,
            "error": err_msg,
            "event_active": False,
            "server_day_name": "",
            "target_scope": target_scope,
            "only_hero_day": only_hero_day,
            "force_ignore_day_guard": force_ignore_day_guard,
            "only_module": only_module,
            "hero_uuid": single_hero_uuid,
            "total_actions": 0,
            "level_ups": [],
            "breakthroughs": [],
            "star_ups": [],
            "skill_ups": [],
            "gear_installed": [],
            "gear_upgraded": [],
            "gear_promoted": [],
            "sp_upgraded": [],
            "skipped": [],
            "skipped_reasons": [],
            "errors": [err_msg],
            "send_errors": [],
            "in_game_tips": [],
            "popped_modals": [],
        }

    upgrade_levels = bool(task_cfg.get("upgrade_levels", True)) if not only_module else (only_module == "level")
    allow_breakthrough = bool(task_cfg.get("allow_breakthrough", True)) if not only_module else (only_module == "level")
    target_level_cap = max(0, _cfg_int("target_level_cap", 0))
    exp_reserve = max(0, _cfg_int("exp_reserve_millions", 0)) * 1_000_000

    upgrade_stars = bool(task_cfg.get("upgrade_stars", True)) if not only_module else (only_module == "star")
    use_universal_shards = bool(task_cfg.get("use_universal_shards", False))
    universal_shard_reserve = max(0, _cfg_int("universal_shard_reserve", 50))

    upgrade_skills = bool(task_cfg.get("upgrade_skills", True)) if not only_module else (only_module == "skill")
    skill_book_reserve = max(0, _cfg_int("skill_book_reserve", 0))

    auto_equip_best = bool(task_cfg.get("auto_equip_best", True)) if not only_module else (only_module == "gear")
    upgrade_gear = bool(task_cfg.get("upgrade_gear", True)) if not only_module else (only_module == "gear")
    min_gear_quality = _cfg_int("min_gear_quality", _cfg_int("min_gear_quality", 5), ctx)
    alloy_reserve = max(0, _cfg_int("alloy_reserve", 0))
    allow_gear_promote = bool(task_cfg.get("allow_gear_promote", False)) if not only_module else (only_module == "gear_promote")
    power_core_reserve = max(0, _cfg_int("power_core_reserve", 0))
    use_replacement_equip = bool(task_cfg.get("use_replacement_equip", False))
    allow_sp_equip = bool(task_cfg.get("allow_sp_equip", False)) if not only_module else (only_module == "sp_equip")
    use_universal_sp_shards = bool(task_cfg.get("use_universal_sp_shards", False))

    if only_hero_day:
        wday_lua = _LUA_SERVER_TIME_HELPER + """
local snap = _get_player_snapshot()
local wday, dayName = _get_server_weekday(snap.serverSec)
return _enc({ ok = true, server_wday = wday, server_day_name = dayName })
"""
        wday_res = _eval_json(cd, pid, wday_lua, timeout=5.0)
        if not isinstance(wday_res, dict) or not wday_res.get("ok"):
            err_msg = (wday_res or {}).get("error", "Hero day check failed")
            return {
                "ok": False,
                "task": "hero_progression",
                "dry_run": dry_run,
                "action": "inspect_failed",
                "reason": str(err_msg),
                "error": err_msg,
                "event_active": False,
                "event_reason": "",
                "active_theme": "",
                "server_day_name": "",
                "target_scope": target_scope,
                "only_hero_day": only_hero_day,
                "force_ignore_day_guard": force_ignore_day_guard,
                "only_module": only_module,
                "hero_uuid": single_hero_uuid,
                "heroes_scanned": 0,
                "heroes_matched": 0,
                "total_actions": 0,
                "level_ups": [],
                "breakthroughs": [],
                "star_ups": [],
                "skill_ups": [],
                "gear_installed": [],
                "gear_upgraded": [],
                "gear_promoted": [],
                "sp_upgraded": [],
                "skipped": [],
                "skipped_reasons": [],
                "errors": [str(err_msg)],
                "send_errors": list((wday_res or {}).get("send_errors") or []),
                "in_game_tips": [],
                "popped_modals": [],
            }
        s_wday = int(wday_res.get("server_wday") or 0)
        s_day_name = str(wday_res.get("server_day_name") or "")
        probe_fast = _probe_preparedness_phase(cd, pid, allow_network_refresh=not dry_run) if s_wday != 5 else None
        ev_active_fast, ev_reason_fast, ev_theme_fast = _is_hero_progression_event_active(probe_fast, s_wday)
        if not ev_active_fast:
            skip_msg = (
                f"Waiting for Alliance Duel Day 4 (Hero Initiative) or Hero Full Preparedness (today={s_day_name})."
            )
            return {
                "ok": True,
                "task": "hero_progression",
                "dry_run": dry_run,
                "target_scope": target_scope,
                "only_hero_day": only_hero_day,
                "force_ignore_day_guard": force_ignore_day_guard,
                "only_module": only_module,
                "hero_uuid": single_hero_uuid,
                "event_active": False,
                "event_reason": ev_reason_fast,
                "active_theme": ev_theme_fast,
                "server_day_name": s_day_name,
                "heroes_scanned": 0,
                "heroes_matched": 0,
                "level_ups": [],
                "breakthroughs": [],
                "star_ups": [],
                "skill_ups": [],
                "gear_installed": [],
                "gear_upgraded": [],
                "gear_promoted": [],
                "sp_upgraded": [],
                "total_actions": 0,
                "skipped_reasons": [skip_msg],
                "skipped": [skip_msg],
                "errors": [],
                "send_errors": [],
                "in_game_tips": [],
                "popped_modals": [],
                "action": "skipped_not_hero_day",
                "reason": skip_msg,
            }

    insp = inspect_hero_progression(cd, pid, include_probe=True, allow_network_refresh=not dry_run)
    if not isinstance(insp, dict) or not insp.get("ok"):
        err_msg = (insp or {}).get("error", "Hero inspection failed")
        return {
            "ok": False,
            "task": "hero_progression",
            "dry_run": dry_run,
            "action": "inspect_failed",
            "reason": str(err_msg),
            "error": err_msg,
            "event_active": False,
            "server_day_name": "",
            "target_scope": target_scope,
            "only_hero_day": only_hero_day,
            "force_ignore_day_guard": force_ignore_day_guard,
            "only_module": only_module,
            "hero_uuid": single_hero_uuid,
            "total_actions": 0,
            "level_ups": [],
            "breakthroughs": [],
            "star_ups": [],
            "skill_ups": [],
            "gear_installed": [],
            "gear_upgraded": [],
            "gear_promoted": [],
            "sp_upgraded": [],
            "skipped": [],
            "skipped_reasons": [],
            "errors": [str(err_msg)],
            "send_errors": [],
            "in_game_tips": [],
            "popped_modals": [],
        }

    ev = insp.get("event_status") or {}
    ev_active = bool(ev.get("hero_day_active", False))
    ev_reason = str(ev.get("reason") or "")
    out: dict[str, Any] = {
        "ok": True,
        "task": "hero_progression",
        "dry_run": dry_run,
        "target_scope": target_scope,
        "only_hero_day": only_hero_day,
        "force_ignore_day_guard": force_ignore_day_guard,
        "only_module": only_module,
        "hero_uuid": single_hero_uuid,
        "event_active": ev_active,
        "event_reason": ev_reason,
        "active_theme": str(ev.get("active_theme") or ""),
        "server_day_name": str(insp.get("server_day_name") or ""),
        "heroes_scanned": len(insp.get("heroes") or []),
        "heroes_matched": 0,
        "level_ups": [],
        "breakthroughs": [],
        "star_ups": [],
        "skill_ups": [],
        "gear_installed": [],
        "gear_upgraded": [],
        "gear_promoted": [],
        "sp_upgraded": [],
        "total_actions": 0,
        "skipped_reasons": [],
        "skipped": [],
        "errors": [],
        "send_errors": [],
        "in_game_tips": [],
        "popped_modals": [],
        "action": "none",
        "reason": "",
    }

    def _finalize_out() -> dict[str, Any]:
        out["skipped"] = list(out["skipped_reasons"])
        if not out.get("reason"):
            out["reason"] = out["skipped_reasons"][0] if out["skipped_reasons"] else out["action"]
        return out

    if only_hero_day and not ev_active:
        out["action"] = "skipped_not_hero_day"
        out["skipped_reasons"].append(
            f"Waiting for Alliance Duel Day 4 (Hero Initiative) or Hero Full Preparedness (today={out['server_day_name']})."
        )
        return _finalize_out()

    targets = _filter_hero_progression_targets(
        insp.get("heroes") or [],
        target_scope=target_scope,
        min_rarity=min_rarity,
        pinned_hero_ids=pinned_ids,
        single_hero_uuid=single_hero_uuid,
    )
    out["heroes_matched"] = len(targets)
    if not targets:
        out["action"] = "no_matching_heroes"
        out["skipped_reasons"].append(f"No heroes matched scope={target_scope}, min_rarity={min_rarity}.")
        return _finalize_out()

    mats = insp.get("materials") or {}
    rem_exp_items = [dict(x) for x in (mats.get("hero_exp_items") or []) if int(x.get("count") or 0) > 0]
    rem_exp_total = int(mats.get("hero_exp_total") or 0)

    merged_alloy: dict[int, dict[str, Any]] = {}
    for raw_ai in (mats.get("enhancement_alloy_items") or []):
        if not isinstance(raw_ai, dict):
            continue
        gid = int(raw_ai.get("itemId") or 0)
        cnt = int(raw_ai.get("count") or 0)
        if gid <= 0 or cnt <= 0:
            continue
        if gid not in merged_alloy:
            merged_alloy[gid] = dict(raw_ai)
        else:
            merged_alloy[gid]["count"] = int(merged_alloy[gid].get("count") or 0) + cnt
    rem_alloy_items = sorted(merged_alloy.values(), key=lambda x: int(x.get("expVal") or 0), reverse=True)
    rem_alloy_count = int(mats.get("enhancement_alloy_total") or sum(int(x.get("count") or 0) for x in rem_alloy_items))

    rem_uni_orange = int((mats.get("universal_shards") or {}).get("orange") or 0)
    rem_uni_purple = int((mats.get("universal_shards") or {}).get("purple") or 0)
    rem_uni_blue = int((mats.get("universal_shards") or {}).get("blue") or 0)
    rem_books: dict[int, int] = {
        230101: int((mats.get("skill_books") or {}).get("orange") or 0),
        230102: int((mats.get("skill_books") or {}).get("purple") or 0),
        230103: int((mats.get("skill_books") or {}).get("blue") or 0),
    }
    rem_power_cores = int(mats.get("power_cores") or 0)
    rem_uni_equip_mats = int(mats.get("universal_equip_materials") or 0)
    rem_uni_sp = int(mats.get("universal_sp_shards") or 0)
    rem_break_minerals = int(mats.get("universal_break_minerals") or 0)

    actions_left = max_actions

    def _send_lua(code: str, confirm_lua: str | None = None) -> dict[str, Any]:
        if dry_run:
            return {"ok": True, "dry_run": True}
        r = _eval_json(cd, pid, code, timeout=8.0)
        if isinstance(r, dict):
            for tip in (r.get("in_game_tips") or r.get("tips") or []):
                ts = str(tip or "").strip()
                if ts and ts not in out["in_game_tips"]:
                    out["in_game_tips"].append(ts)
            for mdl in (r.get("popped_modals") or r.get("modals") or []):
                ms = str(mdl or "").strip()
                if ms and ms not in out["popped_modals"]:
                    out["popped_modals"].append(ms)
            if not r.get("ok"):
                errs = list(r.get("send_errors") or [])
                if r.get("error"):
                    errs.append(str(r.get("error")))
                if not errs:
                    errs.append("rpc_failed")
                for es in errs:
                    ess = str(es).strip()
                    if ess:
                        if ess not in out["send_errors"]:
                            out["send_errors"].append(ess)
                        if ess not in out["errors"]:
                            out["errors"].append(ess)
                time.sleep(0.28)
                return r
        else:
            msg = "invalid_rpc_response"
            if msg not in out["send_errors"]:
                out["send_errors"].append(msg)
            if msg not in out["errors"]:
                out["errors"].append(msg)
            return {"ok": False, "error": msg}

        if confirm_lua:
            for delay in (0.15, 0.25, 0.35):
                time.sleep(delay)
                c_res = _eval_json(cd, pid, confirm_lua, timeout=4.0)
                if not isinstance(c_res, dict) or not c_res.get("ok") or c_res.get("confirmed"):
                    break
        else:
            time.sleep(0.28)
        return r

    for h in targets:
        if actions_left <= 0:
            break
        huuid = str(h.get("uuid") or "")
        hid = int(h.get("heroId") or 0)
        hname = str(h.get("name") or f"Hero #{hid}")
        rarity = int(h.get("rarity") or 1)
        huuid_lua = _lua_quote(huuid)

        # 1. Auto-equip best idle gear (free, zero materials)
        if auto_equip_best and actions_left > 0 and h.get("hasBetterGear") and (h.get("suggestGearUuids") or []):
            suuids = [str(u) for u in (h.get("suggestGearUuids") or []) if u]
            if suuids:
                arr_lua = ",".join(_lua_quote(u) for u in suuids)
                code = f"""
local hem = DataCenter and DataCenter.HeroEquipManager
local eqArr = {{}}
for _, u in ipairs({{{arr_lua}}}) do
  local nu = tonumber(u)
  if nu and nu > 0 then table.insert(eqArr, nu) end
end
if #eqArr == 0 then
  return _enc({{ok = false, error = 'No numeric equip UUIDs'}})
end
if hem and hem.HeroEquipInstall then
  local okS, errS = pcall(function() hem:HeroEquipInstall({hid}, eqArr) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroEquipInstall: ' .. tostring(errS)}}}})
elseif SFSNetwork and MsgDefines and MsgDefines.HeroEquipInstall then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroEquipInstall, {hid}, eqArr) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroEquipInstall: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroEquipInstall unavailable'}})
"""
                r = _send_lua(code)
                if r.get("ok"):
                    out["gear_installed"].append({"heroId": hid, "heroName": hname, "equipUuids": suuids})
                    actions_left -= 1

        # 2. Star-Ups / Rank-Ups (HeroRankUpgrade(uuid, useCommonPieceNum))
        if upgrade_stars and actions_left > 0 and not h.get("isStarMax"):
            need_sh = int(h.get("needShards") or 0)
            owned_sh = int(h.get("ownedShards") or 0)
            if need_sh > 0:
                use_common = 0
                can_do = False
                if owned_sh >= need_sh:
                    can_do = True
                    use_common = 0
                elif use_universal_shards:
                    deficit = need_sh - owned_sh
                    pool = rem_uni_orange if rarity >= 4 else (rem_uni_purple if rarity == 3 else rem_uni_blue)
                    if pool - deficit >= universal_shard_reserve:
                        can_do = True
                        use_common = deficit
                        if rarity >= 4:
                            rem_uni_orange -= deficit
                        elif rarity == 3:
                            rem_uni_purple -= deficit
                        else:
                            rem_uni_blue -= deficit
                if can_do:
                    code = f"""
local huuidNum = tonumber({huuid_lua})
if not huuidNum or huuidNum <= 0 then
  return _enc({{ok = false, error = 'Invalid numeric hero UUID'}})
end
if SFSNetwork and MsgDefines and MsgDefines.HeroRankUpgrade then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroRankUpgrade, huuidNum, {use_common}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroRankUpgrade: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroRankUpgrade unavailable'}})
"""
                    r = _send_lua(code)
                    if r.get("ok"):
                        out["star_ups"].append({
                            "heroId": hid,
                            "heroName": hname,
                            "star": int(h.get("star") or 0),
                            "needShards": need_sh,
                            "universalUsed": use_common,
                        })
                        actions_left -= 1

        # 3. Level Breakthrough (HeroLvBeyond) & Hero Leveling (HeroLvUp)
        cur_lv = int(h.get("level") or 1)
        cur_max_lv = int(h.get("curMaxLevel") or 0)
        eff_cap = min(cur_max_lv, target_level_cap) if (target_level_cap > 0 and cur_max_lv > 0) else (target_level_cap or cur_max_lv)
        if allow_breakthrough and actions_left > 0 and h.get("canBreakthrough") and (target_level_cap <= 0 or cur_lv < target_level_cap):
            code = f"""
local huuidNum = tonumber({huuid_lua})
if not huuidNum or huuidNum <= 0 then
  return _enc({{ok = false, error = 'Invalid numeric hero UUID'}})
end
if SFSNetwork and MsgDefines and MsgDefines.HeroLvBeyond then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroLvBeyond, huuidNum) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroLvBeyond: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroLvBeyond unavailable'}})
"""
            confirm_bt = (
                f"""
local hdm = DataCenter and DataCenter.HeroDataManager
local h = hdm and hdm.GetHeroByUuid and _safe_call(function() return hdm:GetHeroByUuid(tonumber({huuid_lua})) end, nil)
local mx = h and tonumber(_safe_call(function() return h.curMaxLevel or h.maxLevel or 0 end, 0)) or 0
return _enc({{ok = true, confirmed = (mx > {cur_max_lv})}})
"""
                if upgrade_levels
                else None
            )
            r = _send_lua(code, confirm_lua=confirm_bt)
            if r.get("ok"):
                out["breakthroughs"].append({"heroId": hid, "heroName": hname, "level": cur_lv})
                actions_left -= 1

        if upgrade_levels and actions_left > 0 and cur_lv < eff_cap and rem_exp_items:
            need_exp = max(1, int(h.get("needExp") or 0))
            spendable_exp = rem_exp_total - exp_reserve
            if spendable_exp >= need_exp:
                # Choose an EXP item stack that covers need_exp with minimal packet overhead
                chosen = None
                chosen_cnt = 0
                for it in rem_exp_items:
                    icnt = int(it.get("count") or 0)
                    ieval = max(1, int(it.get("expVal") or 1))
                    if icnt <= 0:
                        continue
                    needed_n = (need_exp + ieval - 1) // ieval
                    max_by_reserve = (spendable_exp) // ieval
                    use_n = min(icnt, max(1, needed_n), max_by_reserve)
                    if use_n > 0 and (use_n * ieval) >= need_exp:
                        chosen = it
                        chosen_cnt = use_n
                        break
                if chosen is None:
                    # Fallback: spend largest affordable stack toward next level
                    for it in rem_exp_items:
                        icnt = int(it.get("count") or 0)
                        ieval = max(1, int(it.get("expVal") or 1))
                        max_by_reserve = spendable_exp // ieval
                        use_n = min(icnt, max_by_reserve, 50)
                        if use_n > 0:
                            chosen = it
                            chosen_cnt = use_n
                            break
                if chosen is not None and chosen_cnt > 0:
                    iuuid_lua = _lua_quote(chosen.get("uuid") or "")
                    code = f"""
local huuidNum = tonumber({huuid_lua})
if not huuidNum or huuidNum <= 0 then
  return _enc({{ok = false, error = 'Invalid numeric hero UUID'}})
end
if SFSNetwork and MsgDefines and MsgDefines.HeroLvUp then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroLvUp, huuidNum, {iuuid_lua}, {chosen_cnt}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroLvUp: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroLvUp unavailable'}})
"""
                    r = _send_lua(code)
                    if r.get("ok"):
                        spent = chosen_cnt * max(1, int(chosen.get("expVal") or 1))
                        chosen["count"] = int(chosen.get("count") or 0) - chosen_cnt
                        rem_exp_total = max(0, rem_exp_total - spent)
                        out["level_ups"].append({
                            "heroId": hid,
                            "heroName": hname,
                            "fromLv": cur_lv,
                            "itemId": int(chosen.get("itemId") or 0),
                            "count": chosen_cnt,
                            "expSpent": spent,
                        })
                        actions_left -= 1

        # 4. Skill Upgrades (HeroSkillUpgrade(heroUuid, skillIndex))
        if upgrade_skills and actions_left > 0:
            for sk in (h.get("skills") or []):
                if actions_left <= 0:
                    break
                if not sk.get("canUpgrade"):
                    continue
                s_item = int(sk.get("itemId") or 0)
                s_cost = int(sk.get("costNum") or 0)
                s_idx = int(sk.get("index") or 0)
                if s_idx <= 0 or s_cost <= 0:
                    continue
                rem_books.setdefault(s_item, int(sk.get("ownedItem") or 0))
                avail_bk = rem_books[s_item]
                if avail_bk - s_cost < skill_book_reserve:
                    continue
                code = f"""
local huuidNum = tonumber({huuid_lua})
if not huuidNum or huuidNum <= 0 then
  return _enc({{ok = false, error = 'Invalid numeric hero UUID'}})
end
if SFSNetwork and MsgDefines and MsgDefines.HeroSkillUpgrade then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroSkillUpgrade, huuidNum, {s_idx}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroSkillUpgrade: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroSkillUpgrade unavailable'}})
"""
                r = _send_lua(code)
                if r.get("ok"):
                    rem_books[s_item] = max(0, rem_books[s_item] - s_cost)
                    out["skill_ups"].append({
                        "heroId": hid,
                        "heroName": hname,
                        "skillIndex": s_idx,
                        "skillName": str(sk.get("name") or f"Skill {s_idx}"),
                        "fromLv": int(sk.get("level") or 0),
                        "costNum": s_cost,
                        "itemId": s_item,
                    })
                    actions_left -= 1

        # 5. Gear Enhancement (Enhancement Alloy ONLY - NEVER fodder real gear!) + opt-in Promote
        if (upgrade_gear or allow_gear_promote) and actions_left > 0:
            for eq in (h.get("gear") or []):
                if actions_left <= 0:
                    break
                equuid = str(eq.get("uuid") or "")
                eq_qual = int(eq.get("quality") or 0)
                if not equuid or eq_qual < min_gear_quality:
                    continue
                equuid_lua = _lua_quote(equuid)
                eq_lv = int(eq.get("level") or 0)
                eq_max_lv = int(eq.get("maxLevel") or 0)
                need_eq_exp = int(eq.get("needExp") or 0)
                if upgrade_gear and eq.get("canUpgrade") and rem_alloy_items and need_eq_exp > 0 and (eq_max_lv <= 0 or eq_lv < eq_max_lv):
                    cost_goods_entries: list[tuple[int, int, int]] = []
                    acc_exp = 0
                    avail_alloy_budget = max(0, rem_alloy_count - alloy_reserve)
                    for ai in rem_alloy_items:
                        if acc_exp >= need_eq_exp or avail_alloy_budget <= 0:
                            break
                        acnt = int(ai.get("count") or 0)
                        aval = max(1, int(ai.get("expVal") or 100))
                        if acnt <= 0:
                            continue
                        rem_need = need_eq_exp - acc_exp
                        take = min(acnt, avail_alloy_budget, (rem_need + aval - 1) // aval)
                        if take > 0:
                            cost_goods_entries.append((int(ai.get("itemId") or 0), take, take * aval))
                            acc_exp += take * aval
                            avail_alloy_budget -= take
                    if cost_goods_entries and acc_exp >= need_eq_exp:
                        goods_lua = ",".join(
                            f"{{goodsId='{gid}',num={cnt}}}" for gid, cnt, _ in cost_goods_entries
                        )
                        code = f"""
local hem = DataCenter and DataCenter.HeroEquipManager
local eqNum = tonumber({equuid_lua})
if not eqNum or eqNum <= 0 then
  return _enc({{ok = false, error = 'Invalid numeric equip UUID'}})
end
local costGoods = {{{goods_lua}}}
local costEquipArr = {{}}
if hem and hem.HeroEquipUpgrade then
  local okS, errS = pcall(function() hem:HeroEquipUpgrade(eqNum, costGoods, costEquipArr) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroEquipUpgrade: ' .. tostring(errS)}}}})
elseif SFSNetwork and MsgDefines and MsgDefines.HeroEquipUpgrade then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroEquipUpgrade, eqNum, costGoods, costEquipArr) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroEquipUpgrade: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroEquipUpgrade unavailable'}})
"""
                        confirm_eq_up = (
                            f"""
local hem = DataCenter and DataCenter.HeroEquipManager
local e = hem and hem.GetEquipByUuid and _safe_call(function() return hem:GetEquipByUuid(tonumber({equuid_lua})) end, nil)
local lv = e and tonumber(_safe_call(function() return e.level or 0 end, 0)) or 0
return _enc({{ok = true, confirmed = (lv > {eq_lv})}})
"""
                            if (allow_gear_promote and eq.get("canPromote"))
                            else None
                        )
                        r = _send_lua(code, confirm_lua=confirm_eq_up)
                        if r.get("ok"):
                            used_cnt = 0
                            for gid, cnt, _ in cost_goods_entries:
                                used_cnt += cnt
                                for ai in rem_alloy_items:
                                    if int(ai.get("itemId") or 0) == gid:
                                        ai["count"] = max(0, int(ai.get("count") or 0) - cnt)
                                        break
                            rem_alloy_count = max(0, rem_alloy_count - used_cnt)
                            out["gear_upgraded"].append({
                                "heroId": hid,
                                "heroName": hname,
                                "slot": int(eq.get("slot") or 0),
                                "equipUuid": equuid,
                                "fromLv": eq_lv,
                                "alloyUsed": used_cnt,
                            })
                            actions_left -= 1

                if allow_gear_promote and actions_left > 0 and eq.get("canPromote"):
                    prom_lv = int(eq.get("promoteLevel") or 0)
                    needs_fodder = bool(eq.get("promoteNeedFodder")) or (prom_lv >= 23)
                    est_core_cost = _promote_core_cost_for_level(prom_lv)
                    if est_core_cost <= 0:
                        out["skipped_reasons"].append(f"{hname} slot {eq.get('slot', '?')}: gear promote already at max level ({prom_lv}).")
                        continue
                    if rem_power_cores - est_core_cost < power_core_reserve:
                        out["skipped_reasons"].append(
                            f"{hname} slot {eq.get('slot', '?')}: Power Cores below reserve ({rem_power_cores} - {est_core_cost} < {power_core_reserve})."
                        )
                        continue
                    rep_num = 0
                    if needs_fodder:
                        req_rep = 3 if prom_lv >= 29 else (2 if prom_lv == 26 else 1)
                        if not use_replacement_equip:
                            out["skipped_reasons"].append(
                                f"{hname} slot {eq.get('slot', '?')}: promote lv{prom_lv} requires fodder/Universal Equip Material (enable use_replacement_equip)."
                            )
                            continue
                        if rem_uni_equip_mats < req_rep:
                            out["skipped_reasons"].append(
                                f"{hname} slot {eq.get('slot', '?')}: promote lv{prom_lv} needs {req_rep} Universal Equip Material(s) (230126), owned={rem_uni_equip_mats}."
                            )
                            continue
                        rep_num = req_rep
                    # Strict safety: NEVER sacrifice real gear (pass empty costEquipArr = {})
                    code = f"""
local hem = DataCenter and DataCenter.HeroEquipManager
local eqNum = tonumber({equuid_lua})
if not eqNum or eqNum <= 0 then
  return _enc({{ok = false, error = 'Invalid numeric equip UUID'}})
end
if hem and hem.HeroEquipPromote then
  local okS, errS = pcall(function() hem:HeroEquipPromote(eqNum, {{}}, {rep_num}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroEquipPromote: ' .. tostring(errS)}}}})
elseif SFSNetwork and MsgDefines and MsgDefines.HeroEquipPromoteUp then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroEquipPromoteUp, eqNum, {{}}, {rep_num}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroEquipPromoteUp: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroEquipPromote unavailable'}})
"""
                    r = _send_lua(code)
                    if r.get("ok"):
                        rem_power_cores = max(0, rem_power_cores - est_core_cost)
                        if rep_num > 0:
                            rem_uni_equip_mats = max(0, rem_uni_equip_mats - rep_num)
                        out["gear_promoted"].append({
                            "heroId": hid,
                            "heroName": hname,
                            "slot": int(eq.get("slot") or 0),
                            "equipUuid": equuid,
                            "promoteLevel": prom_lv,
                            "powerCoresUsed": est_core_cost,
                            "replacementUsed": rep_num,
                        })
                        actions_left -= 1

        # 6. Exclusive Weapon (SP Equip - opt-in: Upgrade + Breakthrough)
        sp = h.get("spEquip") or {}
        if allow_sp_equip and actions_left > 0 and sp.get("has") and sp.get("active") and sp.get("canUpgrade"):
            lack_sp = max(0, int(sp.get("lackCount") or 0))
            if lack_sp == 0 or (use_universal_sp_shards and rem_uni_sp >= lack_sp):
                use_uni_sp = lack_sp if (lack_sp > 0 and use_universal_sp_shards) else 0
                code = f"""
local hsp = DataCenter and DataCenter.HeroSPEquipManager
if hsp and hsp.HeroEquipUpgrade then
  local okS, errS = pcall(function() hsp:HeroEquipUpgrade({hid}, {use_uni_sp}, {{}}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroSPEquipUpgrade: ' .. tostring(errS)}}}})
elseif SFSNetwork and MsgDefines and MsgDefines.HeroSPEquipUpgrade then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroSPEquipUpgrade, {hid}, {use_uni_sp}, {{}}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroSPEquipUpgrade: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroSPEquipUpgrade unavailable'}})
"""
                confirm_sp = (
                    f"""
local hsp = DataCenter and DataCenter.HeroSPEquipManager
local info = hsp and hsp.GetHeroSPEquipInfo and _safe_call(function() return hsp:GetHeroSPEquipInfo({hid}) end, nil)
local lv = info and tonumber(_safe_call(function() return info.level or 0 end, 0)) or 0
return _enc({{ok = true, confirmed = (lv > {int(sp.get('level') or 0)})}})
"""
                    if sp.get("canBreak")
                    else None
                )
                r = _send_lua(code, confirm_lua=confirm_sp)
                if r.get("ok"):
                    if use_uni_sp > 0:
                        rem_uni_sp = max(0, rem_uni_sp - use_uni_sp)
                    out["sp_upgraded"].append({
                        "heroId": hid,
                        "heroName": hname,
                        "fromLv": int(sp.get("level") or 0),
                        "universalUsed": use_uni_sp,
                    })
                    actions_left -= 1
            elif lack_sp > 0:
                out["skipped_reasons"].append(
                    f"{hname} SP upgrade needs {lack_sp} universal SP shard(s) (260000), owned={rem_uni_sp}, enabled={use_universal_sp_shards}."
                )

        if allow_sp_equip and actions_left > 0 and sp.get("has") and sp.get("active") and sp.get("canBreak"):
            lack_brk = max(0, int(sp.get("breakLackCount") or 0))
            if lack_brk == 0 or (use_universal_sp_shards and rem_break_minerals >= lack_brk):
                use_uni_brk = lack_brk if (lack_brk > 0 and use_universal_sp_shards) else 0
                code = f"""
if SFSNetwork and MsgDefines and MsgDefines.HeroSPEquipBreak then
  local okS, errS = pcall(function() SFSNetwork.SendMessage(MsgDefines.HeroSPEquipBreak, {hid}, {use_uni_brk}, {{}}) end)
  if okS then return _enc({{ok = true}}) end
  return _enc({{ok = false, error = tostring(errS), send_errors = {{'HeroSPEquipBreak: ' .. tostring(errS)}}}})
end
return _enc({{ok = false, error = 'HeroSPEquipBreak unavailable'}})
"""
                r = _send_lua(code)
                if r.get("ok"):
                    if use_uni_brk > 0:
                        rem_break_minerals = max(0, rem_break_minerals - use_uni_brk)
                    out["sp_upgraded"].append({
                        "heroId": hid,
                        "heroName": hname,
                        "fromLv": int(sp.get("level") or 0),
                        "universalUsed": use_uni_brk,
                        "breakthrough": True,
                    })
                    actions_left -= 1
            elif lack_brk > 0:
                out["skipped_reasons"].append(
                    f"{hname} SP breakthrough needs {lack_brk} universal break mineral(s) (214000), owned={rem_break_minerals}, enabled={use_universal_sp_shards}."
                )

    total = (
        len(out["level_ups"])
        + len(out["breakthroughs"])
        + len(out["star_ups"])
        + len(out["skill_ups"])
        + len(out["gear_installed"])
        + len(out["gear_upgraded"])
        + len(out["gear_promoted"])
        + len(out["sp_upgraded"])
    )
    out["total_actions"] = total
    out["action"] = "upgraded" if total > 0 else "nothing_upgradable"
    return _finalize_out()


def run_alliance_boss_mine(
    cd: Any,
    pid: int,
    client_state: dict[str, Any],
    cfg: dict[str, Any],
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_cfg = cfg.get("alliance_boss_mine") or {}
    bear_claim = bool(task_cfg.get("bear_claim_rewards", True))
    bear_join = bool(task_cfg.get("bear_join_or_rally", True))
    mine_dispatch = bool(task_cfg.get("alliance_mine_dispatch", True))
    reserve = int(cfg.get("formation_reserve", 0) or 0)

    lua = f"""
local dryRun = {str(dry_run).lower()}
local bearClaim = {str(bear_claim).lower()}
local bearJoin = {str(bear_join).lower()}
local mineDispatch = {str(mine_dispatch).lower()}
local reserve = {reserve}

local snap = _get_player_snapshot()
local dc = DataCenter
local abb = dc and dc.AllianceBossBearManager
local amm = dc and dc.AllianceMineManager
local out = {{
  ok = true,
  task = 'alliance_boss_mine',
  dry_run = dryRun,
  bear_open = false,
  bear_in_battle = false,
  bear_reward_claimed = false,
  bear_marched = nil,
  mine_has_center = false,
  mine_has_march = false,
  mine_dispatched = nil,
  errors = {{}},
  action = 'none',
}}
if not snap.inAlliance then
  out.action = 'skipped_no_alliance'
  return _enc(out)
end

local mu = package.loaded['SlgEngine.Util.MarchUtil.MarchUtil'] or package.loaded['Util.MarchUtil_SLG']
local freeForms = _pick_free_formations(reserve, {_used_formations_lua(context, pid)}, not dryRun)
local fIdx = 1

-- 1) Alliance Boss Bear Trap
if abb then
  out.bear_open = _safe_call(function() return abb:IsAllianceBossActivityOpen() end, false) and true or false
  out.bear_in_battle = _safe_call(function() return abb:GetIsInBattle() end, false) and true or false
  if bearClaim and _safe_call(function() return abb:GetIsFreeRewardCanReceive() end, false) then
    local actId = tonumber(_safe_call(function() return abb:GetCurrActivityId() end, 0)) or 0
    if actId > 0 then
      local claimOk = dryRun
      if not dryRun then
        if SFSNetwork and MsgDefines and MsgDefines.ReceiveAllianceBossFreeReward then
          local okC, errC = pcall(function() SFSNetwork.SendMessage(MsgDefines.ReceiveAllianceBossFreeReward, actId) end)
          if okC then
            claimOk = true
          else
            table.insert(out.errors, 'ReceiveAllianceBossFreeReward: ' .. tostring(errC))
          end
        else
          table.insert(out.errors, 'ReceiveAllianceBossFreeReward unavailable')
        end
      end
      if claimOk then
        out.bear_reward_claimed = true
      end
    end
  end
  if bearJoin and out.bear_open and out.bear_in_battle and fIdx <= #freeForms then
    local bInfo = _safe_call(function() return abb:GetBossInfo() end, {{}}) or {{}}
    local ptId = tonumber(bInfo.pointId or 0) or 0
    local bossUuid = bInfo.bossUuid or bInfo.uuid or 0
    if ptId > 0 and mu and mu.SendCreateMarchMessage then
      local f = freeForms[fIdx]
      local sentOk = dryRun
      if not dryRun then
        local okM, errM = pcall(function()
          mu.SendCreateMarchMessage(f.uuid, (MarchTargetType and MarchTargetType.RALLY_FOR_ALLIANCE_BOSS) or 74, ptId, bossUuid, 0, true, true, snap.serverId)
        end)
        if okM then
          sentOk = true
        else
          table.insert(out.errors, 'AllianceBossBearMarch: ' .. tostring(errM))
        end
      end
      if sentOk then
        fIdx = fIdx + 1
        out.bear_marched = {{formation = f.uuid, pointId = ptId}}
      end
    end
  end
end

-- 2) Alliance Mine
if amm then
  out.mine_has_center = tonumber(_safe_call(function() return amm:CheckIfHasAllianceCenter() end, 0) or 0) > 0
  out.mine_has_march = _safe_call(function() return amm:CheckIfHasMarch() end, false) and true or false
  if mineDispatch and out.mine_has_center and not out.mine_has_march and fIdx <= #freeForms then
    local mines = _safe_call(function() return amm:GetMyAlMines() end, nil) or amm.allianceMineInfoDic or {{}}
    local targetPt = 0
    local targetUid = 0
    for k, m in pairs(mines) do
      if type(m) == 'table' then
        local pt = (tonumber(m.pointId or 0) or 0) > 0 and tonumber(m.pointId) or (tonumber(m.point or 0) or 0)
        local rem = tonumber(m.remainNum or m.num or 1) or 0
        if pt > 0 and rem > 0 then
          targetPt = pt
          targetUid = m.uuid or k or 0
          break
        end
      end
    end
    if targetPt > 0 and mu and mu.SendCreateMarchMessage then
      local f = freeForms[fIdx]
      local sentOk = dryRun
      if not dryRun then
        local okD, errD = pcall(function()
          mu.SendCreateMarchMessage(f.uuid, (MarchTargetType and MarchTargetType.COLLECT_ALLIANCE_BUILD_RESOURCE) or 35, targetPt, targetUid, 0, true, true, snap.serverId)
        end)
        if okD then
          sentOk = true
        else
          table.insert(out.errors, 'AllianceMineDispatch: ' .. tostring(errD))
        end
      end
      if sentOk then
        fIdx = fIdx + 1
        out.mine_dispatched = {{formation = f.uuid, pointId = targetPt}}
      end
    end
  end
end

if out.bear_reward_claimed or out.bear_marched or out.mine_dispatched then
  out.action = 'completed'
elseif not dryRun and #out.errors > 0 then
  out.ok = false
  out.action = 'send_failed'
  out.error = table.concat(out.errors, '; ')
end
return _enc(out)
"""
    res = _eval_json(cd, pid, lua, timeout=12.0)
    used = [
        str(info["formation"])
        for k in ("bear_marched", "mine_dispatched")
        for info in [res.get(k)]
        if isinstance(info, dict) and info.get("formation")
    ]
    if not dry_run and used:
        _record_used_formations(context, pid, used)
    return res


_BOT_MINE_MELEE_MODULE: Any = None
_BOT_MINE_MELEE_LOCK = threading.Lock()
_BMM_SINGLETON_NAME = "heinz_bot_mine_melee_singleton"


def _load_bot_mine_melee_module() -> Any:
    global _BOT_MINE_MELEE_MODULE
    if _BOT_MINE_MELEE_MODULE is not None:
        return _BOT_MINE_MELEE_MODULE
    with _BOT_MINE_MELEE_LOCK:
        if _BOT_MINE_MELEE_MODULE is not None:
            return _BOT_MINE_MELEE_MODULE
        existing = sys.modules.get(_BMM_SINGLETON_NAME)
        if existing is not None:
            _BOT_MINE_MELEE_MODULE = existing
            return existing
        try:
            from tools import bot_mine_melee as _bmm
            sys.modules.setdefault(_BMM_SINGLETON_NAME, _bmm)
            _BOT_MINE_MELEE_MODULE = _bmm
            return _bmm
        except ImportError:
            try:
                import bot_mine_melee as _bmm
                sys.modules.setdefault(_BMM_SINGLETON_NAME, _bmm)
                _BOT_MINE_MELEE_MODULE = _bmm
                return _bmm
            except ImportError:
                import importlib.util
                mod_path = Path(__file__).resolve().parent / "bot mine melee.py"
                resolved = str(mod_path.resolve())
                for cand in list(sys.modules.values()):
                    cand_file = getattr(cand, "__file__", None)
                    if cand_file:
                        try:
                            if str(Path(cand_file).resolve()) == resolved:
                                sys.modules[_BMM_SINGLETON_NAME] = cand
                                _BOT_MINE_MELEE_MODULE = cand
                                return cand
                        except Exception:
                            pass
                spec = importlib.util.spec_from_file_location("bot_mine_melee", str(mod_path))
                if spec is None or spec.loader is None:
                    raise ImportError(f"Unable to load bot_mine_melee from {mod_path}")
                mod = importlib.util.module_from_spec(spec)
                sys.modules[_BMM_SINGLETON_NAME] = mod
                sys.modules.setdefault("bot_mine_melee", mod)
                try:
                    spec.loader.exec_module(mod)
                except Exception:
                    sys.modules.pop(_BMM_SINGLETON_NAME, None)
                    raise
                _BOT_MINE_MELEE_MODULE = mod
                return mod


def action_mine_melee_refresh(
    cd: Any,
    pid: int,
    client_state: dict[str, Any] | bool | None = None,
    cfg: dict[str, Any] | int | None = None,
    dry_run: bool = False,
    context: dict[str, Any] | None = None,
    refresh_threshold_sec: int | None = None,
    min_payload_pct: float | None = None,
    reserve_formations: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Wrapper in bot actions.py that imports and calls action_mine_melee_refresh from bot mine melee.py."""
    if isinstance(client_state, bool):
        dry_run = client_state
        client_state = {}
    if isinstance(cfg, (int, float)) and not isinstance(cfg, bool):
        if refresh_threshold_sec is None:
            refresh_threshold_sec = int(cfg)
        cfg = {}
    client_state = client_state if isinstance(client_state, dict) else {}
    cfg = cfg if isinstance(cfg, dict) else {}
    task_cfg = cfg.get("mine_melee_refresh") or {}

    resolved_threshold = (
        int(refresh_threshold_sec)
        if refresh_threshold_sec is not None
        else int(task_cfg.get("refresh_threshold_sec", 300) or 300)
    )
    resolved_payload_pct = (
        float(min_payload_pct)
        if min_payload_pct is not None
        else float(task_cfg.get("min_payload_pct", 10.0) if task_cfg.get("min_payload_pct") is not None else 10.0)
    )
    resolved_reserve = (
        int(reserve_formations)
        if reserve_formations is not None
        else int(
            task_cfg.get("reserve_formations")
            if task_cfg.get("reserve_formations") is not None
            else (cfg.get("formation_reserve", 1) if cfg.get("formation_reserve") is not None else 1)
        )
    )

    bmm = _load_bot_mine_melee_module()
    res = bmm.action_mine_melee_refresh(
        cd,
        pid,
        dry_run=bool(dry_run),
        refresh_threshold_sec=resolved_threshold,
        min_payload_pct=resolved_payload_pct,
        reserve_formations=resolved_reserve,
        client_state=client_state,
        cfg=cfg,
        context=context,
        **kwargs,
    )
    if not dry_run and isinstance(res, dict) and res.get("ok") and context is not None:
        used: list[str] = []
        for key in ("dispatched", "dispatched_marches"):
            items = res.get(key)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get("sent", True):
                        fu = item.get("formation") or item.get("formationUuid") or item.get("formation_uuid")
                        if fu:
                            used.append(str(fu))
        if used:
            _record_used_formations(context, pid, used)
    return res


run_mine_melee_refresh = action_mine_melee_refresh

action_auto_help = run_auto_help
action_rf_hq_under_attack = run_rf_hq_under_attack
action_war_safety = run_war_safety
action_alliance_daily = run_alliance_daily
action_daily_tasks_complete = run_daily_tasks_complete
action_daily_claims = run_daily_claims
action_free_recruits = run_free_recruits
action_research_queue = run_research_queue
action_vip_store_rewards = run_vip_store_rewards
action_hero_battlefield = run_hero_battlefield
action_arena = run_arena
action_radar_events = run_radar_events
action_treasure_helicopter = run_treasure_helicopter
action_furylord = run_furylord
action_full_preparedness = run_full_preparedness
action_speedups = run_speedups
action_troop_training = run_troop_training
action_building_upgrades = run_building_upgrades
action_tyrant_event = run_tyrant_event
action_alliance_boss_mine = run_alliance_boss_mine
action_garage_upgrades = run_garage_upgrades
action_hero_progression = run_hero_progression
action_bounties = run_bounties
action_bounty_steal = run_bounty_steal
action_trucks = run_trucks
action_mining_event = run_mining_event
action_boomer_runs = run_boomer_runs
action_auto_gather = run_auto_gather
action_area_exploration = run_area_exploration


TASK_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "auto_help": run_auto_help,
    "rf_hq_under_attack": run_rf_hq_under_attack,
    "war_safety": run_war_safety,
    "hospital_heal": run_hospital_heal,
    "mine_melee_refresh": run_mine_melee_refresh,
    "alliance_daily": run_alliance_daily,
    "daily_tasks_complete": run_daily_tasks_complete,
    "daily_claims": run_daily_claims,
    "free_recruits": run_free_recruits,
    "research_queue": run_research_queue,
    "vip_store_rewards": run_vip_store_rewards,
    "hero_battlefield": run_hero_battlefield,
    "arena": run_arena,
    "radar_events": run_radar_events,
    "treasure_helicopter": run_treasure_helicopter,
    "furylord": run_furylord,
    "full_preparedness": run_full_preparedness,
    "speedups": run_speedups,
    "troop_training": run_troop_training,
    "building_upgrades": run_building_upgrades,
    "tyrant_event": run_tyrant_event,
    "alliance_boss_mine": run_alliance_boss_mine,
    "garage_upgrades": run_garage_upgrades,
    "hero_progression": run_hero_progression,
    "bounties": run_bounties,
    "bounty_steal": run_bounty_steal,
    "trucks": run_trucks,
    "mining_event": run_mining_event,
    "boomer_runs": run_boomer_runs,
    "auto_gather": run_auto_gather,
    "area_exploration": run_area_exploration,
    "dismiss_popups": dismiss_all_popups,
}

# Wrap all task functions, aliases, and registry entries with structured telemetry
for _tkey, _tfn in list(TASK_REGISTRY.items()):
    _wrapped = _with_task_telemetry(_tkey)(_tfn)
    TASK_REGISTRY[_tkey] = _wrapped
    if _tfn.__name__ in globals():
        globals()[_tfn.__name__] = _wrapped
    for _alias in (f"run_{_tkey}", f"action_{_tkey}"):
        if _alias in globals():
            globals()[_alias] = _wrapped

action_rss_gather_step = run_rss_gather_step
action_standalone_npc_step = run_standalone_npc_step
action_saga_kill_step = run_saga_kill_step

# Extended handler map exposing all TASK_REGISTRY entries plus repeat-ready world farm/kill steps
TASK_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    **TASK_REGISTRY,
    "rss_gather": _with_task_telemetry("rss_gather")(run_rss_gather_step),
    "standalone_npc": _with_task_telemetry("standalone_npc")(run_standalone_npc_step),
    "saga_boss": _with_task_telemetry("saga_boss")(run_saga_kill_step),
}


def _cli_main() -> int:
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description="Last Z per-client automation action runner")
    parser.add_argument(
        "--test-action",
        "--action",
        dest="test_action",
        required=True,
        help="Action/task name to execute (e.g. hospital_heal, mine_melee_refresh)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Execute in dry-run mode without mutating live game state",
    )
    parser.add_argument(
        "--pid",
        type=int,
        default=0,
        help="Target Survival.exe PID (0 = auto-discover running process)",
    )
    parser.add_argument(
        "--use-speedups",
        action="store_true",
        default=False,
        help="Enable smart healing speedup calculation for hospital_heal",
    )
    parser.add_argument(
        "--max-speedup-mins",
        type=int,
        default=0,
        help="Max speedup minutes cap for hospital_heal (0 = uncapped up to remaining time)",
    )
    parser.add_argument(
        "--max-chain-batches",
        type=int,
        default=5,
        help="Max sequential healing micro-batches to chain per hospital_heal invocation",
    )
    parser.add_argument(
        "--refresh-threshold-sec",
        type=int,
        default=300,
        help="Refresh threshold in seconds for mine_melee_refresh",
    )
    parser.add_argument(
        "--min-payload-pct",
        type=float,
        default=10.0,
        help="Minimum payload percentage for mine_melee_refresh",
    )
    parser.add_argument(
        "--reserve-formations",
        type=int,
        default=1,
        help="Number of formations to reserve",
    )
    args = parser.parse_args()

    cd_path = Path(__file__).resolve().parent / "client discovery.py"
    spec = importlib.util.spec_from_file_location("client_discovery", str(cd_path))
    if spec is None or spec.loader is None:
        print(json.dumps({"ok": False, "error": f"Failed to load {cd_path}"}))
        return 1
    cd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cd)

    pid = int(args.pid or 0)
    if pid <= 0:
        running = cd.find_running_processes()
        if not running:
            print(json.dumps({"ok": False, "error": "No running Survival.exe process found"}))
            return 1
        running.sort(key=lambda p: (0 if str(p.get("role") or "").lower() == "main" else 1, int(p.get("pid") or 0)))
        pid = int(running[0]["pid"])

    action_key = str(args.test_action or "").strip()
    if action_key.startswith("action_"):
        action_key = action_key[len("action_"):]
    elif action_key.startswith("run_"):
        action_key = action_key[len("run_"):]

    fn = TASK_REGISTRY.get(action_key) or TASK_HANDLERS.get(action_key)
    if fn is None:
        print(json.dumps({"ok": False, "error": f"Unknown action: {args.test_action}", "available": sorted(set(TASK_REGISTRY.keys()) | set(TASK_HANDLERS.keys()))}))
        return 1

    snap = snapshot_client(cd, pid)
    cfg: dict[str, Any] = {
        "formation_reserve": args.reserve_formations,
        "hospital_heal": {
            "collect_finished": True,
            "batch_minutes": 30,
            "min_batch_troops": 25,
            "max_batch_troops": 1500,
            "call_alliance_help": True,
            "use_speedups": bool(args.use_speedups),
            "max_speedup_mins": int(args.max_speedup_mins),
            "max_chain_batches": int(args.max_chain_batches),
        },
        "mine_melee_refresh": {
            "refresh_threshold_sec": int(args.refresh_threshold_sec),
            "min_payload_pct": float(args.min_payload_pct),
            "reserve_formations": int(args.reserve_formations),
        },
    }
    ctx: dict[str, Any] = {}
    if action_key == "hospital_heal":
        res = run_hospital_heal(
            cd,
            pid,
            snap,
            cfg,
            dry_run=bool(args.dry_run),
            context=ctx,
            use_speedups=bool(args.use_speedups),
            max_speedup_mins=int(args.max_speedup_mins),
            max_chain_batches=int(args.max_chain_batches),
        )
    elif action_key == "mine_melee_refresh":
        res = action_mine_melee_refresh(
            cd,
            pid,
            snap,
            cfg,
            dry_run=bool(args.dry_run),
            context=ctx,
            refresh_threshold_sec=int(args.refresh_threshold_sec),
            min_payload_pct=float(args.min_payload_pct),
            reserve_formations=int(args.reserve_formations),
        )
    else:
        res = fn(cd, pid, snap, cfg, dry_run=bool(args.dry_run), context=ctx)

    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if isinstance(res, dict) and res.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(_cli_main())
