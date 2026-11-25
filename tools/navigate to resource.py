"""Find, navigate to, and optionally gather the nearest unoccupied resource node."""

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ["HEINZ_DATA_DIR"]) if os.environ.get("HEINZ_DATA_DIR", "").strip() else (REPO_ROOT / "data")
CSV_PATH = DATA_DIR / "map all resources.csv"


def _load_cd():
    path = REPO_ROOT / "tools" / "client discovery.py"
    spec = importlib.util.spec_from_file_location("client_discovery", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RES_ALIASES = {
    "oil": (0, {"oil", "fuel", "gas"}),
    "mine": (1, {"mine", "metal", "steel", "iron"}),
    "metal": (1, {"mine", "metal", "steel", "iron"}),
    "steel": (1, {"mine", "metal", "steel", "iron"}),
    "wood": (2, {"wood", "lumber", "farm"}),
    "food": (2, {"food", "farm", "wood"}),
    "electricity": (12, {"electricity", "power", "elec"}),
    "power": (12, {"electricity", "power", "elec"}),
    "money": (14, {"money", "cash", "coin"}),
    "gold": (15, {"gold", "diamond", "gem"}),
    "diamond": (15, {"gold", "diamond", "gem"}),
}

RES_TYPE_NAMES = {
    0: "Oil",
    1: "Mine",
    2: "Wood",
    12: "Electricity",
    14: "Money",
    15: "Diamond",
}


def _lua_safe_encoder() -> str:
    return r"""
local function _esc(s)
    return (s:gsub("[%z\1-\31\\\"\127-\255]", function(c)
        return string.format("\\u%04x", string.byte(c))
    end))
end
local function _enc(v, d)
    d = d or 0
    if d > 5 then return '"<depth>"' end
    local tv = type(v)
    if v == nil then return "null" end
    if tv == "boolean" then return tostring(v) end
    if tv == "number" then
        if v ~= v or v == math.huge or v == -math.huge then return "0" end
        return tostring(v)
    end
    if tv == "string" then return '"' .. _esc(v) .. '"' end
    if tv == "table" then
        local isArr = (#v > 0)
        local parts = {}
        if isArr then
            for i = 1, #v do table.insert(parts, _enc(v[i], d + 1)) end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            for k, val in pairs(v) do
                table.insert(parts, '"' .. _esc(tostring(k)) .. '":' .. _enc(val, d + 1))
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    end
    return '"' .. _esc(tostring(v)) .. '"'
end
"""


def scan_live_viewport_nodes(cd, pid: int) -> dict:
    lua_code = _lua_safe_encoder() + r"""
local p = LuaEntry and LuaEntry.Player
local bm = DataCenter and DataCenter.BuildManager
local wpm = DataCenter and DataCenter.WorldPointManager
local lc = LocalController and LocalController.instance and LocalController.instance()

local mainPt = p and p.world_main_pos or 0
local srvId = 0
if p then
    if p.GetSelfServerId then srvId = p:GetSelfServerId() end
    if (not srvId or srvId == 0) then srvId = p.serverId or 0 end
end

local bx, by = 0, 0
if mainPt > 0 and SceneUtils and SceneUtils.IndexToTileXY then
    bx, by = SceneUtils.IndexToTileXY(mainPt)
elseif mainPt > 0 then
    by = math.floor(mainPt / 1000)
    bx = mainPt % 1000
end

local nodes = {}
if wpm and wpm.allViewPoints then
    for idx, info in pairs(wpm.allViewPoints) do
        if type(info) == "table" and info.pointType == 7 then
            local pt = tonumber(info.pointIndex or info.mainIndex or idx) or 0
            local detail = wpm.GetPointInfo and wpm:GetPointInfo(pt) or info
            local rinfo = detail and detail.resourceInfo or nil
            local resId = rinfo and tonumber(rinfo.resourceId) or 0
            local gatherUuid = rinfo and tonumber(rinfo.gatherUuid) or 0
            local ownerUid = rinfo and tostring(rinfo.ownerUid or "") or ""
            local resType = -1
            local lv = 0
            local modelName = ""
            if lc and TableName and TableName.GatherResource and resId > 0 then
                local okLine, row = pcall(function() return lc:getLine(TableName.GatherResource, tostring(resId)) end)
                if okLine and row and row.getValue then
                    resType = tonumber(row:getValue("resource_type")) or -1
                    lv = tonumber(row:getValue("level")) or 0
                    modelName = tostring(row:getValue("model") or "")
                end
            end
            local nx, ny = 0, 0
            if pt > 0 and SceneUtils and SceneUtils.IndexToTileXY then
                nx, ny = SceneUtils.IndexToTileXY(pt)
            elseif pt > 0 then
                ny = math.floor(pt / 1000)
                nx = pt % 1000
            end
            table.insert(nodes, {
                pointId = pt,
                x = nx,
                y = ny,
                resId = resId,
                resType = resType,
                level = lv,
                model = modelName,
                gatherUuid = gatherUuid,
                ownerUid = ownerUid,
                occupied = (gatherUuid ~= 0) or (ownerUid ~= "")
            })
        end
    end
end

local inWorld = (SceneManager and SceneManager.IsInWorld and SceneManager:IsInWorld()) and true or false
return _enc({
    serverId = srvId,
    mainPointId = mainPt,
    baseX = bx,
    baseY = by,
    inWorld = inWorld,
    nodes = nodes
})
"""
    ok, raw = cd.frida_eval_lua(pid, lua_code, timeout=10.0, retries=2)
    if not ok:
        return {"error": raw, "nodes": []}
    try:
        return json.loads(raw)
    except Exception as e:
        return {"error": f"JSON parse error: {e}", "nodes": []}


def ensure_world_scene(cd, pid: int, wait_s: float = 3.2) -> bool:
    """Switch client to the world map scene cleanly if currently inside city view."""
    lua_chk = """
if SceneManager and SceneManager.IsInWorld and SceneManager:IsInWorld() then
    return "ALREADY_WORLD"
end
if LWBattleManager and LWBattleManager.isInBattle then
    return "IN_PVE"
end
if SceneManager and SceneManager.ChangeToWorld then
    local okW = pcall(function() SceneManager:ChangeToWorld() end)
    if not okW then pcall(SceneManager.ChangeToWorld) end
    return "SWITCHING"
end
return "NO_SM"
"""
    ok, res = cd.frida_eval_lua(pid, lua_chk, timeout=8.0, retries=1)
    if not ok:
        return False
    if "SWITCHING" in res:
        time.sleep(wait_s)
    return "ALREADY_WORLD" in res or "SWITCHING" in res


def find_via_server_search(cd, pid: int, res_type_int: int, level: int | None) -> bool:
    """Trigger the in-game server resource search when the local viewport has no candidates."""
    target_lv = int(level) if level is not None else 6
    lua_search = f"""
local ok, err = pcall(function()
    if SFSNetwork and MsgDefines and MsgDefines.FindResourcePoint then
        SFSNetwork.SendMessage(MsgDefines.FindResourcePoint, {{type = {int(res_type_int)}, level = {target_lv}, param = ""}})
    end
end)
return tostring(ok) .. ":" .. tostring(err)
"""
    ok, res = cd.frida_eval_lua(pid, lua_search, timeout=8.0, retries=1)
    return ok and res.startswith("true")


def find_and_go_resource(
    resource_choice="Mine",
    level_choice=6,
    base_x=None,
    base_y=None,
    dispatch=False,
    pid=None,
    profile=None,
):
    cd = _load_cd()
    target_pid = cd.resolve_target_pid(pid=pid, profile=profile)
    if not target_pid:
        print("[-] Could not find a running Last Z client.")
        return False

    choice_low = str(resource_choice or "Mine").strip().lower()
    want_type_int, alias_set = RES_ALIASES.get(choice_low, (-1, {choice_low}))
    want_lv = int(level_choice) if level_choice is not None else None

    view = scan_live_viewport_nodes(cd, target_pid)
    if view.get("error"):
        print(f"[-] Live scan error (PID {target_pid}): {view['error']}")
        return False

    if not view.get("inWorld"):
        ensure_world_scene(cd, target_pid)
        view = scan_live_viewport_nodes(cd, target_pid)

    srv_id = int(view.get("serverId") or 0)
    bx = base_x if base_x is not None else int(view.get("baseX") or 500)
    by = base_y if base_y is not None else int(view.get("baseY") or 500)

    if not view.get("nodes") and want_type_int >= 0:
        find_via_server_search(cd, target_pid, want_type_int, want_lv)
        time.sleep(1.5)
        view = scan_live_viewport_nodes(cd, target_pid)

    candidates = []
    for n in view.get("nodes", []):
        if n.get("occupied"):
            continue
        rt = int(n.get("resType", -1))
        lv = int(n.get("level", 0))
        if want_type_int >= 0 and rt != want_type_int:
            continue
        if want_lv is not None and lv != want_lv:
            continue
        dist = math.hypot(n["x"] - bx, n["y"] - by)
        candidates.append({
            "dist": dist,
            "x": n["x"],
            "y": n["y"],
            "pointId": int(n["pointId"]),
            "level": lv,
            "type": RES_TYPE_NAMES.get(rt, choice_low.title()),
            "source": "live",
        })

    if not candidates and srv_id == 702 and CSV_PATH.exists():
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rtype = (row.get("Resource") or "").lower()
                if rtype not in alias_set and not any(a in rtype for a in alias_set):
                    continue
                if want_lv is not None:
                    try:
                        if int(row.get("Level", 0)) != want_lv:
                            continue
                    except ValueError:
                        continue
                if (row.get("Gatherer") or "").strip():
                    continue
                rx = int(row["X"])
                ry = int(row["Y"])
                pt_id = int(ry * 1000 + rx)
                candidates.append({
                    "dist": math.hypot(rx - bx, ry - by),
                    "x": rx,
                    "y": ry,
                    "pointId": pt_id,
                    "level": int(row.get("Level") or 0),
                    "type": row.get("Resource") or resource_choice,
                    "source": "csv702",
                })

    if not candidates:
        print(f"[-] No unoccupied {resource_choice} (Lv.{want_lv or 'Any'}) found on State #{srv_id} (PID {target_pid}).")
        return False

    candidates.sort(key=lambda item: (-item["level"], item["dist"]) if want_lv is None else (item["dist"],))
    best = candidates[0]
    tx, ty, pt_id = best["x"], best["y"], best["pointId"]
    print(f"[+] Found closest: Lv.{best['level']} {best['type']} at ({tx}, {ty}) [Dist: {best['dist']:.1f}, src: {best['source']}, State #{srv_id}, PID {target_pid}]")

    lua_nav = f"""
local pt = {pt_id}
local srvId = {srv_id}
if srvId == 0 and LuaEntry and LuaEntry.Player then
    srvId = LuaEntry.Player.serverId or 0
end
if SceneManager and SceneManager.IsInWorld and not SceneManager:IsInWorld() then
    local inPve = (LWBattleManager and LWBattleManager.isInBattle) or false
    if not inPve and SceneManager.ChangeToWorld then
        local okW = pcall(function() SceneManager:ChangeToWorld() end)
        if not okW then pcall(SceneManager.ChangeToWorld) end
    end
end
if GoToUtil and GoToUtil.GotoWorldPos then
    if SceneUtils and SceneUtils.TileIndexToWorld then
        local wp = SceneUtils.TileIndexToWorld(pt)
        GoToUtil.GotoWorldPos(wp)
    else
        local vec = UnityEngine.Vector2.New({tx}, {ty})
        GoToUtil.GotoWorldPos(vec, true)
    end
end
return "Navigated to ({tx}, {ty}) pointId=" .. tostring(pt) .. " srv=" .. tostring(srvId)
"""
    ok_nav, nav_res = cd.frida_eval_lua(target_pid, lua_nav, timeout=10.0, retries=1)
    if not ok_nav:
        print(f"[-] Navigation failed: {nav_res}")
        return False
    print(f"[+] {nav_res}")

    if dispatch:
        lua_dispatch = f"""
local pt = {pt_id}
local srvId = {srv_id}
if srvId == 0 and LuaEntry and LuaEntry.Player then
    srvId = (LuaEntry.Player.GetSelfServerId and LuaEntry.Player:GetSelfServerId()) or LuaEntry.Player.serverId or 0
end
local wpm = DataCenter and DataCenter.WorldPointManager
local pInfo = wpm and wpm.GetPointInfo and wpm:GetPointInfo(pt) or nil
if pInfo and pInfo.resourceInfo then
    local g = tonumber(pInfo.resourceInfo.gatherUuid) or 0
    local o = tostring(pInfo.resourceInfo.ownerUid or "")
    if g ~= 0 or o ~= "" then
        return "ABORT_OCCUPIED:" .. o
    end
end

local af = DataCenter and DataCenter.ArmyFormationDataManager
if not af or not MarchUtil then
    return "NO_MARCH_API"
end
local list = af.GetFormationList and af:GetFormationList() or {{}}
local freeForm = nil
for _, f in pairs(list) do
    local st = tonumber(type(f) == "table" and (f.status or f.state or 0) or -1) or -1
    if type(f) == "table" and f.uuid and st == 0 then
        if not freeForm or (tonumber(f.index) or 99) < (tonumber(freeForm.index) or 99) then
            freeForm = f
        end
    end
end
if not freeForm then
    return "NO_FREE_FORMATION"
end

MarchUtil.SendCreateMarchMessage(freeForm.uuid, 2, pt, 0, 0, 1, nil, srvId)
return "DISPATCHED_FORM_" .. tostring(freeForm.index or 0) .. "_TO_" .. tostring(pt)
"""
        time.sleep(0.5)
        ok_d, d_res = cd.frida_eval_lua(target_pid, lua_dispatch, timeout=10.0, retries=1)
        if not ok_d:
            print(f"[!] Dispatch failed: {d_res}")
            return False
        print(f"[DISPATCH] {d_res}")
        return "DISPATCHED" in d_res

    return True


def main():
    parser = argparse.ArgumentParser(description="Find and navigate/dispatch to nearest unoccupied resource tile.")
    parser.add_argument("resource_type", nargs="?", default="Mine", help="Mine, Oil, Wood, Electricity, Money, Diamond")
    parser.add_argument("level", nargs="?", type=int, default=None, help="Target node level (e.g. 6)")
    parser.add_argument("--dispatch", action="store_true", help="Send free formation to gather the node")
    parser.add_argument("--pid", type=int, default=None, help="Target process PID")
    parser.add_argument("--profile", type=str, default=None, help="Target Unity profile or client label")
    args = parser.parse_args()

    res = find_and_go_resource(
        resource_choice=args.resource_type,
        level_choice=args.level,
        dispatch=args.dispatch,
        pid=args.pid,
        profile=args.profile,
    )
    sys.exit(0 if res else 1)


if __name__ == "__main__":
    main()
