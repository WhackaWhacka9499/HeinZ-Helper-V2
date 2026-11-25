import argparse
import importlib.util
import json
import os
import sys

if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

_CD_MODULE = None


def _get_cd():
    global _CD_MODULE
    if _CD_MODULE is not None:
        return _CD_MODULE
    disc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client discovery.py")
    if os.path.exists(disc_path):
        spec = importlib.util.spec_from_file_location("client_discovery", disc_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _CD_MODULE = mod
            return mod
    return None


LUA_DETECT = r"""
local function serializeVal(v)
    local t = type(v)
    if t == "number" or t == "boolean" then
        return tostring(v)
    elseif t == "string" then
        local s = v:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t')
        return '"' .. s .. '"'
    elseif t == "table" then
        local isArr = true
        local maxI = 0
        local count = 0
        for k, _ in pairs(v) do
            count = count + 1
            if type(k) ~= "number" or k <= 0 or math.floor(k) ~= k then
                isArr = false
            elseif k > maxI then
                maxI = k
            end
        end
        if count == 0 then return "[]" end
        if isArr and maxI == count then
            local items = {}
            for i = 1, count do
                table.insert(items, serializeVal(v[i]))
            end
            return "[" .. table.concat(items, ",") .. "]"
        else
            local entries = {}
            for k, val in pairs(v) do
                table.insert(entries, string.format('"%s":%s', tostring(k), serializeVal(val)))
            end
            return "{" .. table.concat(entries, ",") .. "}"
        end
    else
        return "null"
    end
end

local p = LuaEntry and LuaEntry.Player
local serverId = (p and ((p.GetSelfServerId and p:GetSelfServerId()) or (p.GetCurServerId and p:GetCurServerId()) or p.serverId)) or 0
local curServerId = (p and p.GetCurServerId and p:GetCurServerId()) or serverId
local serverName = (p and p.serverName) or ("State#" .. tostring(serverId))
local playerName = (p and p.name) or "Unknown"
local playerUid = (p and p.uid) or ""
local playerPower = (p and ((p.power and p.power > 0 and p.power) or p.playerPower)) or 0
local bm = DataCenter and DataCenter.BuildManager
local playerHq = (bm and bm.MainLv and bm.MainLv > 0 and bm.MainLv) or (p and p.mainCityLv) or 0
local armyKill = (p and p.armyKill) or 0

local abd, acm
pcall(function()
    if DataCenter and DataCenter.AllianceBaseDataManager then
        abd = DataCenter.AllianceBaseDataManager:GetAllianceBaseData()
    end
end)
local alTag = (abd and abd.abbr) or (p and p.allianceAbbr) or ""
local alName = (abd and abd.name) or (p and p.allianceName) or ""
local alId = (abd and abd.uid) or (p and p.allianceId) or ""
local alPower = (abd and abd.power) or 0
local alMembers = (abd and abd.memberCount) or 0

local vsIsOpen, vsInCompete, fightServerId, fightAllianceId, fightAlTag, rushDay = false, false, 0, "", "", 0
pcall(function()
    acm = DataCenter and DataCenter.AllianceCompeteDataManager
    if acm then
        vsIsOpen = acm:CheckIfAllianceCompeteOpen() or false
        vsInCompete = acm:CheckIfIsInCompete() or false
        fightServerId = acm:GetFightServerId() or 0
        fightAllianceId = acm:GetFightAllianceId() or ""
        local vsList = acm:GetVSAllianceList()
        if vsList and fightAllianceId and vsList[fightAllianceId] then
            fightAlTag = vsList[fightAllianceId].abbr or vsList[fightAllianceId].alName or ""
        end
        rushDay = acm:GetRushDataDay() or 0
    end
end)

local season = (SeasonUtil and SeasonUtil.GetSeason and SeasonUtil.GetSeason()) or 0
local sgm = DataCenter and DataCenter.SeasonGroupManager
local bracketId = 0
local bracketServers = {}
if sgm and serverId > 0 then
    pcall(function()
        bracketId = sgm:GetTemplateId(season, serverId) or 0
        local tmpl = sgm:GetTemplate(season, serverId)
        if tmpl and tmpl.serverIds then
            for i = 1, #tmpl.serverIds do
                table.insert(bracketServers, tmpl.serverIds[i])
            end
        end
    end)
end

if #bracketServers == 0 and serverId >= 689 and serverId <= 704 then
    bracketId = 16
    for s = 689, 704 do
        table.insert(bracketServers, s)
    end
end

local env = {
    isLive = true,
    serverId = serverId,
    curServerId = curServerId,
    serverName = serverName,
    playerName = playerName,
    playerUid = tostring(playerUid),
    playerPower = playerPower,
    playerHq = playerHq,
    armyKill = armyKill,
    allianceTag = alTag,
    allianceName = alName,
    allianceId = tostring(alId),
    alliancePower = alPower,
    allianceMembers = alMembers,
    vsIsOpen = vsIsOpen,
    vsInCompete = vsInCompete,
    fightServerId = fightServerId,
    fightAllianceId = tostring(fightAllianceId),
    fightAllianceTag = fightAlTag,
    rushDay = rushDay,
    season = season,
    bracketId = bracketId,
    bracketServers = bracketServers
}

return serializeVal(env)
"""

_ENV_DATA_DIR = os.environ.get("HEINZ_DATA_DIR", "").strip()
CACHE_FILE = (
    os.path.join(_ENV_DATA_DIR, "detected_environment.json")
    if _ENV_DATA_DIR
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "detected_environment.json")
)


def _read_cached_env() -> dict | None:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if isinstance(cached, dict):
            cached["isLive"] = False
            return cached
    except Exception:
        pass
    return None


def _resolve_target_pid(pid=None):
    cd = _get_cd()
    if cd is not None:
        return cd.resolve_target_pid(pid=pid)
    if pid is not None:
        return int(pid)
    env_pid = os.environ.get("LASTZ_TARGET_PID", "").strip()
    return int(env_pid) if env_pid.isdigit() else None


def detect_environment(pid=None):
    pid = _resolve_target_pid(pid)

    if not pid:
        return _read_cached_env() or {
            "isLive": False,
            "serverId": 0,
            "serverName": "State Unknown",
            "playerName": "Offline",
            "playerUid": "",
            "playerPower": 0,
            "playerHq": 0,
            "armyKill": 0,
            "allianceTag": "",
            "allianceName": "",
            "allianceId": "",
            "alliancePower": 0,
            "allianceMembers": 0,
            "vsIsOpen": False,
            "vsInCompete": False,
            "fightServerId": 0,
            "fightAllianceId": "",
            "fightAllianceTag": "",
            "rushDay": 0,
            "season": 0,
            "bracketId": 0,
            "bracketServers": [],
        }

    cd = _get_cd()
    if cd is not None:
        try:
            ok, raw = cd.frida_eval_lua(pid, LUA_DETECT, timeout=6.0, retries=2)
            if ok and raw:
                data = json.loads(raw)
                if isinstance(data, dict):
                    data["isLive"] = True
                    data["pid"] = pid
                    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                    tmp = f"{CACHE_FILE}.{os.getpid()}.tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    os.replace(tmp, CACHE_FILE)
                    return data
        except Exception as e:
            if sys.stdout is not None:
                print(f"Environment sync note: {e}")

    return _read_cached_env() or {"isLive": False, "serverId": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect live Last Z account and state environment.")
    parser.add_argument("--pid", type=int, default=None, help="Target game process PID")
    args = parser.parse_args()
    env = detect_environment(pid=args.pid)
    print(json.dumps(env, indent=2, ensure_ascii=False))
