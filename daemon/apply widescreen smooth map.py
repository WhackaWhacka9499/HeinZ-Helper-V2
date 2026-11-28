import argparse
import importlib.util
import os
import sys
import time
import json

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MASTER_LUA_CODE = r"""
-- Last Z master engine overhaul v8.3 (Zero-gap svLod=1 sweep, global HQs/Boomers/Resources, silent 5m refresh, viewport-first 50x50 grid)

local function IsNull(o)
    if o == nil then return true end
    if type(o) == "userdata" then
        return o:Equals(nil)
    end
    return false
end

local function SafeTableCount(t)
    if type(t) ~= "table" then return 0 end
    local c = 0
    for _ in pairs(t) do c = c + 1 end
    return c
end
if type(table.count) ~= "function" then
    table.count = SafeTableCount
end

local _cachedRjson = nil
local function GetRapidJson()
    if _cachedRjson ~= nil then
        return _cachedRjson or nil
    end
    local loaded = package and package.loaded and package.loaded.rapidjson
    if loaded then
        _cachedRjson = loaded
        return loaded
    end
    local ok, mod = pcall(require, "rapidjson")
    if ok and mod then
        _cachedRjson = mod
        return mod
    end
    _cachedRjson = false
    return nil
end

local function GetActiveWorldServerId(mgr)
    mgr = mgr or (DataCenter and DataCenter.WorldPointManager)
    if mgr then
        local aoiSid = tonumber(mgr.aoiServerId or 0) or 0
        if aoiSid > 0 then return aoiSid end
    end
    local p = LuaEntry and LuaEntry.Player
    if p and p.GetSelfServerId then
        local ok, sid = pcall(p.GetSelfServerId, p)
        local numSid = ok and tonumber(sid) or nil
        if numSid and numSid > 0 then
            return numSid
        end
    end
    return 0
end

local function ResolveCacheServerId(serverId, mgr)
    local sid = tonumber(serverId)
    if not sid or sid <= 0 then
        sid = tonumber(GetActiveWorldServerId(mgr)) or 0
    end
    if sid < 0 then sid = 0 end
    return sid
end

_G._PersistentWorldPointCacheByServer = _G._PersistentWorldPointCacheByServer or {}
_G._PersistentDesertCacheByServer = _G._PersistentDesertCacheByServer or {}
_G._MonsterIdSet = _G._MonsterIdSet or {}
_G._DynamicBuildIdSet = _G._DynamicBuildIdSet or {}
_G._WorldCacheDirtyCount = _G._WorldCacheDirtyCount or {}
_G._WorldCacheLastSaveTs = _G._WorldCacheLastSaveTs or {}
_G._FullMapLoadState = _G._FullMapLoadState or {
    active = false,
    done = 0,
    total = 0,
    serverId = 0,
    lastCompletedAt = 0,
}

local BUCKET_SIZE = 50
local MONSTER_NEAR_3D_RADIUS = 85
local MONSTER_EVICT_3D_RADIUS = 115
_G._MasterSpatialGrid = _G._MasterSpatialGrid or {}
_G._MasterDirtyBuckets = _G._MasterDirtyBuckets or {}
_G._MasterViewPointCount = _G._MasterViewPointCount or 0
_G._MasterGridTableRef = _G._MasterGridTableRef or nil
_G._MasterObjCount = _G._MasterObjCount or 0
_G._MasterAllObjRef = _G._MasterAllObjRef or nil
_G._MasterNear3DMonsters = _G._MasterNear3DMonsters or {}
_G._MasterProxyMonsterLabels = _G._MasterProxyMonsterLabels or {}
_G._MasterProxyMonsters = _G._MasterProxyMonsters or {}
_G._MasterReconcilePass = _G._MasterReconcilePass or nil
_G._MasterReconcileToken = _G._MasterReconcileToken or 0
_G._MasterLastResLodCamX = _G._MasterLastResLodCamX or -9999
_G._MasterLastResLodCamY = _G._MasterLastResLodCamY or -9999

local _DEFAULT_CACHE_DIR = "./data/cache"
_G._WorldCacheLoadedOk = _G._WorldCacheLoadedOk or {}

local function GetCacheDir()
    local ov = _G._MasterCacheDirOverride
    if type(ov) == "string" and ov ~= "" then
        return (ov:gsub("\\", "/"):gsub("/+$", ""))
    end
    local envDir = os and os.getenv and os.getenv("HEINZ_DATA_DIR")
    if type(envDir) == "string" and envDir ~= "" then
        return (envDir:gsub("\\", "/"):gsub("/+$", "")) .. "/cache"
    end
    return _DEFAULT_CACHE_DIR
end

local function GetServerCacheTables(serverId, mgr)
    local sid = ResolveCacheServerId(serverId, mgr)
    _G._PersistentWorldPointCacheByServer[sid] = _G._PersistentWorldPointCacheByServer[sid] or {}
    _G._PersistentDesertCacheByServer[sid] = _G._PersistentDesertCacheByServer[sid] or {}
    _G._PersistentWorldPointCache = _G._PersistentWorldPointCacheByServer[sid]
    _G._PersistentDesertCache = _G._PersistentDesertCacheByServer[sid]
    return _G._PersistentWorldPointCacheByServer[sid], _G._PersistentDesertCacheByServer[sid], sid
end

local function GetCacheFilePath(serverId, mgr)
    local dir = GetCacheDir()
    local sid = ResolveCacheServerId(serverId, mgr)
    if sid > 0 then
        return dir .. "/world_map_cache_s" .. tostring(sid) .. ".json"
    end
    return dir .. "/world_map_cache.json"
end

local function MarkWorldCacheDirty(serverId, delta)
    local sid = ResolveCacheServerId(serverId)
    _G._WorldCacheDirtyCount[sid] = (_G._WorldCacheDirtyCount[sid] or 0) + (delta or 1)
end

local _DISK_SAVE_MIN_INTERVAL_SEC = 20

function _G.SaveWorldCacheToDisk(serverId, forceSave)
    pcall(function()
        local cache, _, sid = GetServerCacheTables(serverId)
        if not cache or not next(cache) then return end
        local dirty = _G._WorldCacheDirtyCount[sid] or 0
        local lastSave = _G._WorldCacheLastSaveTs[sid] or 0
        local now = os.time()
        if not forceSave then
            if dirty <= 0 then return end
            if (now - lastSave) < _DISK_SAVE_MIN_INTERVAL_SEC then
                return
            end
        elseif dirty <= 0 and lastSave > 0 then
            return
        end
        local rjson = GetRapidJson()
        if not rjson then return end
        local exportObj = {}
        for k, v in pairs(cache) do
            exportObj[tostring(k)] = v
        end
        local encoded = rjson.encode(exportObj)
        if type(encoded) ~= "string" or #encoded < 5 then return end
        local filePath = GetCacheFilePath(sid)
        local hasExisting = false
        local existingSize = 0
        local ef = io.open(filePath, "rb")
        if ef then
            hasExisting = true
            existingSize = ef:seek("end") or 0
            ef:close()
        end
        if existingSize > 0 and (not _G._WorldCacheLoadedOk[sid]) and #encoded < existingSize then
            return
        end
        if existingSize >= 4096 and #encoded < math.floor(existingSize * 0.25) then
            return
        end
        local randTag = tostring(now) .. "_" .. tostring(math.random(100000, 999999))
        local tmpPath = filePath .. "." .. randTag .. ".tmp"
        local bakPath = filePath .. "." .. randTag .. ".bak"
        local f = io.open(tmpPath, "wb")
        if not f then return end
        local okW = f:write(encoded)
        local okFlush = false
        if okW then
            okFlush = (f:flush() ~= nil)
        end
        local okClose = f:close()
        if not okW or not okFlush or not okClose then
            pcall(os.remove, tmpPath)
            return
        end
        local movedToBak = false
        if hasExisting then
            local okBakCall, bakRes = pcall(os.rename, filePath, bakPath)
            if not (okBakCall and bakRes) then
                pcall(os.remove, tmpPath)
                return
            end
            movedToBak = true
        end
        local okCall, renRes = pcall(function() return os.rename(tmpPath, filePath) end)
        if okCall and renRes then
            if movedToBak then
                pcall(os.remove, bakPath)
            end
            _G._WorldCacheDirtyCount[sid] = 0
            _G._WorldCacheLastSaveTs[sid] = now
            _G._WorldCacheLoadedOk[sid] = true
        else
            if movedToBak then
                pcall(os.rename, bakPath, filePath)
            end
            pcall(os.remove, tmpPath)
        end
    end)
end

function _G.LoadWorldCacheFromDisk(serverId)
    pcall(function()
        local cache, _, sid = GetServerCacheTables(serverId)
        local rjson = GetRapidJson()
        if not rjson then return end
        local filePath = GetCacheFilePath(sid)
        local f = io.open(filePath, "rb")
        if not f then return end
        local content = f:read("*a")
        f:close()
        if not content or #content < 5 then return end
        local decoded = rjson.decode(content)
        if type(decoded) == "table" and next(decoded) ~= nil then
            local hadLivePoints = (next(cache) ~= nil)
            local prevDirty = _G._WorldCacheDirtyCount[sid] or 0
            for kStr, v in pairs(decoded) do
                local kNum = tonumber(kStr)
                if kNum and cache[kNum] == nil then
                    cache[kNum] = v
                end
            end
            if not hadLivePoints then
                _G._WorldCacheDirtyCount[sid] = 0
                _G._WorldCacheLastSaveTs[sid] = os.time()
            else
                _G._WorldCacheDirtyCount[sid] = math.max(prevDirty, 1)
            end
            _G._WorldCacheLoadedOk[sid] = true
        end
    end)
end

do
    local initCache, _, initSid = GetServerCacheTables()
    if next(initCache) == nil or not _G._WorldCacheLoadedOk[initSid] then
        _G.LoadWorldCacheFromDisk(initSid)
    end
end

local function FastIndexToXY(pointIndex)
    local tw = TileCountX or 1000
    local z = pointIndex - 1
    local py = math.floor(z / tw)
    return z - py * tw, py
end

local function IndexViewPoint(mgr, pointIndex, entry, markDirty)
    if not pointIndex or type(entry) ~= "table" then return end
    local px = entry._px
    local py = entry._py
    if px == nil or py == nil then
        px, py = FastIndexToXY(pointIndex)
        entry._px = px
        entry._py = py
    end
    local bx = math.floor(px / BUCKET_SIZE)
    local by = math.floor(py / BUCKET_SIZE)
    local bKey = by * 4096 + bx
    local grid = _G._MasterSpatialGrid
    local bucket = grid[bKey]
    if not bucket then
        bucket = {}
        grid[bKey] = bucket
    end
    if bucket[pointIndex] == nil then
        _G._MasterViewPointCount = (_G._MasterViewPointCount or 0) + 1
    end
    bucket[pointIndex] = entry
    if markDirty then
        _G._MasterDirtyBuckets[bKey] = true
    end
end

local function UnindexViewPoint(pointIndex, entry)
    if not pointIndex then return end
    local px = type(entry) == "table" and entry._px or nil
    local py = type(entry) == "table" and entry._py or nil
    if px == nil or py == nil then
        px, py = FastIndexToXY(pointIndex)
    end
    local bx = math.floor(px / BUCKET_SIZE)
    local by = math.floor(py / BUCKET_SIZE)
    local bKey = by * 4096 + bx
    local bucket = _G._MasterSpatialGrid and _G._MasterSpatialGrid[bKey]
    if bucket and bucket[pointIndex] ~= nil then
        bucket[pointIndex] = nil
        _G._MasterViewPointCount = math.max(0, (_G._MasterViewPointCount or 1) - 1)
    end
end

local function RebuildSpatialGrid(mgr)
    local grid = {}
    local count = 0
    if mgr and type(mgr.allViewPoints) == "table" then
        for k, entry in pairs(mgr.allViewPoints) do
            if type(entry) == "table" then
                local px = entry._px
                local py = entry._py
                if px == nil or py == nil then
                    px, py = FastIndexToXY(k)
                    entry._px = px
                    entry._py = py
                end
                local bx = math.floor(px / BUCKET_SIZE)
                local by = math.floor(py / BUCKET_SIZE)
                local bKey = by * 4096 + bx
                local bucket = grid[bKey]
                if not bucket then
                    bucket = {}
                    grid[bKey] = bucket
                end
                bucket[k] = entry
                count = count + 1
            end
        end
    end
    _G._MasterSpatialGrid = grid
    _G._MasterDirtyBuckets = {}
    _G._MasterViewPointCount = count
    _G._MasterGridTableRef = mgr and mgr.allViewPoints or nil
    _G._MasterStreamReset = true
end

local function SyncSpatialGridIfReplaced(mgr)
    if not mgr then return end
    local vp = mgr.allViewPoints
    if type(vp) ~= "table" then
        if (_G._MasterViewPointCount or 0) > 0 or _G._MasterGridTableRef ~= nil then
            RebuildSpatialGrid(mgr)
        end
        return
    end
    if _G._MasterGridTableRef ~= vp or ((_G._MasterViewPointCount or 0) > 0 and next(vp) == nil) then
        RebuildSpatialGrid(mgr)
    end
end

local function _syncMasterObjCount(targetMgr)
    if not targetMgr or type(targetMgr.allObj) ~= "table" then
        _G._MasterObjCount = 0
        _G._MasterAllObjRef = nil
        return 0
    end
    if _G._MasterAllObjRef ~= targetMgr.allObj or ((_G._MasterObjCount or 0) > 0 and next(targetMgr.allObj) == nil) then
        _G._MasterAllObjRef = targetMgr.allObj
        _G._MasterObjCount = SafeTableCount(targetMgr.allObj)
    end
    return _G._MasterObjCount or 0
end

function _G.RestoreWorldMapCache(serverId)
    local mgr = DataCenter and DataCenter.WorldPointManager
    if not mgr then return end
    local sid = ResolveCacheServerId(serverId, mgr)
    local ptCache, desertCache = GetServerCacheTables(sid, mgr)
    if next(ptCache) == nil then
        _G.LoadWorldCacheFromDisk(sid)
    end
    mgr.allViewPoints = mgr.allViewPoints or {}
    SyncSpatialGridIfReplaced(mgr)
    local v2 = CS and CS.UnityEngine and CS.UnityEngine.Vector2
    for k, pi in pairs(ptCache or {}) do
        local entry = mgr.allViewPoints[k]
        local pType = (type(pi) == "table" and (pi.pointType or pi.PointType)) or 0
        local px, py = FastIndexToXY(k)
        local mv2 = v2 and v2(px, py) or nil
        if not entry then
            entry = {
                pointIndex = k,
                mainIndex = (type(pi) == "table" and (pi.mainIndex or pi.id)) or k,
                mainIndexV2 = mv2,
                pointType = pType,
                pointInfo = pi,
                _px = px,
                _py = py,
            }
            mgr.allViewPoints[k] = entry
        else
            entry.pointInfo = pi
            entry._px = px
            entry._py = py
            if entry.pointType == nil or entry.pointType == 0 then entry.pointType = pType end
            if entry.mainIndex == nil then entry.mainIndex = k end
            if entry.mainIndexV2 == nil and mv2 then entry.mainIndexV2 = mv2 end
        end
        IndexViewPoint(mgr, k, entry, true)
    end
    for k, di in pairs(desertCache or {}) do
        local entry = mgr.allViewPoints[k]
        local px, py = FastIndexToXY(k)
        local mv2 = v2 and v2(px, py) or nil
        if not entry then
            entry = {
                pointIndex = k,
                mainIndex = k,
                mainIndexV2 = mv2,
                desertInfo = di,
                _px = px,
                _py = py,
            }
            mgr.allViewPoints[k] = entry
        else
            entry.desertInfo = di
            entry._px = px
            entry._py = py
            if entry.mainIndexV2 == nil and mv2 then entry.mainIndexV2 = mv2 end
        end
        IndexViewPoint(mgr, k, entry, true)
    end
end

_G._MasterToggles = _G._MasterToggles or {
    masterEnabled = true,  -- [F1] Master World Map Overhaul ON/OFF
    showZombies   = true,  -- [F2] Show/Hide Wandering Zombies (mi.type <= 2)
    showResources = true,  -- [F3] Show/Hide Resource Nodes (pType == 7)
    showBoomers   = true,  -- [F4] Show/Hide Boomers & Bosses (mi.type >= 3)
    showHQs       = true,  -- [F5] Show/Hide Player HQs & Buildings (pType == 6)
    showOverlay   = true,  -- [Home] Show/Hide Top-Center HUD Overlay
}

local function GetMonsterCategory(entry)
    if type(entry) ~= "table" then return "ZOMBIE" end
    local cat = entry._monsterCat
    if cat then return cat end
    local pi = entry.pointInfo
    local mi = (pi and (pi.monsterInfo or pi._parsedExtra)) or entry._parsedExtra
    if not mi and pi and pi.extraInfo and PBController and PBController.ParsePbFromBytes then
        local ok, parsed = pcall(PBController.ParsePbFromBytes, pi.extraInfo, "protobuf.WorldPointMonster")
        if ok and parsed then
            mi = parsed
            pi._parsedExtra = parsed
            entry._parsedExtra = parsed
        end
    end
    if mi and mi.type then
        if mi.type == 3 then
            cat = "BOOMER"
        elseif mi.type > 3 then
            cat = "BOSS"
        else
            cat = "ZOMBIE"
        end
        entry._monsterCat = cat
        return cat
    end
    return "ZOMBIE"
end

local function _overlayBadge(val)
    return val and "<color=#4ADE80>ON</color>" or "<color=#F87171>OFF</color>"
end

function _G.RefreshMasterOverlayUI()
    local um = UIManager and UIManager:GetInstance()
    if not um or not um.m_topCanvas or IsNull(um.m_topCanvas) then return end
    local parentRect = um.m_topCanvas
    local uiLayer = parentRect.gameObject and parentRect.gameObject.layer or 5

    local barGo = _G._MasterOverlayBarGo
    local tmp = _G._MasterOverlayTmp
    local justCreatedBar = false
    if not barGo or IsNull(barGo) or not tmp or IsNull(tmp) then
        local existing = parentRect:Find("LastZMasterOverlayBar")
        if existing and not IsNull(existing) then
            CS.UnityEngine.Object.Destroy(existing.gameObject)
        end

        barGo = CS.UnityEngine.GameObject("LastZMasterOverlayBar")
        barGo.layer = uiLayer
        barGo.transform:SetParent(parentRect, false)
        local barRect = barGo:AddComponent(typeof(CS.UnityEngine.RectTransform))
        barRect.anchorMin = CS.UnityEngine.Vector2(0.5, 1.0)
        barRect.anchorMax = CS.UnityEngine.Vector2(0.5, 1.0)
        barRect.pivot = CS.UnityEngine.Vector2(0.5, 1.0)
        barRect.anchoredPosition = CS.UnityEngine.Vector2(0, -6)
        barRect.sizeDelta = CS.UnityEngine.Vector2(1060, 32)

        local bgImg = barGo:AddComponent(typeof(CS.UnityEngine.UI.Image))
        bgImg.color = CS.UnityEngine.Color(0.05, 0.07, 0.11, 0.86)
        bgImg.raycastTarget = false

        local txtGo = CS.UnityEngine.GameObject("OverlayText")
        txtGo.layer = uiLayer
        txtGo.transform:SetParent(barGo.transform, false)
        local txtRect = txtGo:AddComponent(typeof(CS.UnityEngine.RectTransform))
        txtRect.anchorMin = CS.UnityEngine.Vector2.zero
        txtRect.anchorMax = CS.UnityEngine.Vector2.one
        txtRect.offsetMin = CS.UnityEngine.Vector2(10, 0)
        txtRect.offsetMax = CS.UnityEngine.Vector2(-10, 0)

        tmp = txtGo:AddComponent(typeof(CS.TMPro.TextMeshProUGUI))
        local tmps = um.container and um.container:GetComponentsInChildren(typeof(CS.TMPro.TextMeshProUGUI), true)
        if tmps and tmps.Length > 0 and tmps[0].font then
            tmp.font = tmps[0].font
        end
        tmp.fontSize = 14.5
        tmp.alignment = CS.TMPro.TextAlignmentOptions.Center
        tmp.raycastTarget = false
        tmp.enableWordWrapping = false

        _G._MasterOverlayBarGo = barGo
        _G._MasterOverlayTmp = tmp
        _G._MasterLastOverlayText = nil
        justCreatedBar = true
    end

    local t = _G._MasterToggles
    local showBar = (t.showOverlay ~= false)
    local wasVisible = barGo.activeSelf
    if wasVisible ~= showBar then
        barGo:SetActive(showBar)
    end
    if not showBar then return end

    local curSceneId = SceneManager and SceneManager.CurrSceneID
    local curParent = (barGo.transform and barGo.transform.parent) or parentRect
    local curChildCount = (curParent and curParent.childCount) or (parentRect and parentRect.childCount) or nil
    local isNotLastSibling = false
    if curChildCount ~= nil and barGo.transform and type(barGo.transform.GetSiblingIndex) == "function" then
        local okSib, sibIdx = pcall(barGo.transform.GetSiblingIndex, barGo.transform)
        if okSib and type(sibIdx) == "number" and sibIdx < (curChildCount - 1) then
            isNotLastSibling = true
        end
    end
    if justCreatedBar
        or (not wasVisible)
        or _G._MasterOverlayLastSceneId ~= curSceneId
        or (curChildCount ~= nil and _G._MasterOverlayLastChildCount ~= curChildCount)
        or isNotLastSibling
    then
        barGo.transform:SetAsLastSibling()
        _G._MasterOverlayLastSceneId = curSceneId
        _G._MasterOverlayLastChildCount = curChildCount
    end
    local fls = _G._FullMapLoadState or {}
    local mgr = DataCenter and DataCenter.WorldPointManager
    if mgr then
        SyncSpatialGridIfReplaced(mgr)
        _syncMasterObjCount(mgr)
    end
    local ptCount = _G._MasterViewPointCount or 0
    local objCount = tonumber(_G._MasterObjCount or 0) or 0
    local loadBadge
    if fls.active and (not fls.silentRefresh) and (fls.total or 0) > 0 then
        local pct = math.min(100, math.floor(((fls.done or 0) * 100) / fls.total))
        loadBadge = string.format("<color=#FBBF24>%d%% (%d/%d)</color>", pct, fls.done or 0, fls.total)
    elseif ptCount > 0 then
        if mgr and mgr.isInit == true then
            loadBadge = string.format("<color=#4ADE80>%.1fk pts / %d obj</color>", ptCount / 1000.0, objCount)
        else
            loadBadge = string.format("<color=#4ADE80>%.1fk pts (Cached)</color>", ptCount / 1000.0)
        end
    else
        loadBadge = "<color=#94A3B8>Idle</color>"
    end
    local barRect = barGo:GetComponent(typeof(CS.UnityEngine.RectTransform))
    if barRect and not IsNull(barRect) and barRect.sizeDelta.x < 1040 then
        barRect.sizeDelta = CS.UnityEngine.Vector2(1060, 32)
    end
    local newText = string.format(
        "<b><color=#38BDF8>LAST Z PC</color></b>  |  <b>[F1] Map:</b> %s  |  <b>[F2] Zom:</b> %s  |  <b>[F3] Res:</b> %s  |  <b>[F4] Boom:</b> %s  |  <b>[F5] HQs:</b> %s  |  <b>[F6] Full Load:</b> %s  |  <color=#94A3B8>[Home]</color>",
        _overlayBadge(t.masterEnabled),
        _overlayBadge(t.showZombies),
        _overlayBadge(t.showResources),
        _overlayBadge(t.showBoomers),
        _overlayBadge(t.showHQs),
        loadBadge
    )
    if _G._MasterLastOverlayText ~= newText then
        tmp.text = newText
        _G._MasterLastOverlayText = newText
    end
end

-- Shared spatial visibility & toggle filter (used by ApplyLastZWorldMaster, ApplyToggleChangeImmediate, and runCameraStreamer)
function _G.ShouldBuildPointNow(selfMgr, pointIndex, entry, camX, camY, isEvictCheck)
    if type(entry) ~= "table" then return false end
    local toggles = _G._MasterToggles
    local px = entry._px
    local py = entry._py
    if px == nil or py == nil then
        px, py = FastIndexToXY(pointIndex)
        entry._px = px
        entry._py = py
    end
    local dist = math.max(math.abs(px - camX), math.abs(py - camY))

    if toggles and toggles.masterEnabled == false then
        return dist <= (isEvictCheck and 48 or 38)
    end

    local pi = entry.pointInfo
    if not pi then
        return dist <= (isEvictCheck and 110 or 80)
    end

    local pType = entry.pointType or pi.PointType or pi.pointType or -1
    if pType == 4 then
        local mCat = GetMonsterCategory(entry)
        if mCat == "BOOMER" or mCat == "BOSS" then
            if toggles and toggles.showBoomers == false then return false end
            return true
        else
            if toggles and toggles.showZombies == false then return false end
            return true
        end
    elseif pType == 7 then
        if toggles and toggles.showResources == false then return false end
        return true
    elseif pType == 6 then
        if toggles and toggles.showHQs == false then return false end
        return true
    end

    -- All point types (HQs, Resources, Zombies, Boomers, Radar 22, Cities 11, Alliance 15, Treasures): 100% corner-to-corner globally visible!
    return true
end

local HYSTERESIS_COOLDOWN = 0.35
_G._lastStableBand = _G._lastStableBand or "NEAR"
_G._lastBandSwitchTime = _G._lastBandSwitchTime or 0

local function GetHysteresisLod(rawLod)
    local now = CS.UnityEngine.Time.unscaledTime
    local curBand = _G._lastStableBand
    if curBand == "NEAR" then
        if rawLod >= 4 or (rawLod == 3 and (now - _G._lastBandSwitchTime) >= HYSTERESIS_COOLDOWN) then
            _G._lastStableBand = "FAR"
            _G._lastBandSwitchTime = now
            return math.max(3, rawLod)
        else
            return math.min(2, rawLod)
        end
    else
        if rawLod <= 1 or (rawLod == 2 and (now - _G._lastBandSwitchTime) >= HYSTERESIS_COOLDOWN) then
            _G._lastStableBand = "NEAR"
            _G._lastBandSwitchTime = now
            return math.min(2, rawLod)
        else
            return math.max(3, rawLod)
        end
    end
end

local function GetActualCameraTilePos(mgr, ws)
    local csWorld = CS.SceneManager and CS.SceneManager.World
    if csWorld and not IsNull(csWorld) and SceneUtils and SceneUtils.WorldToTileXZ and ForceChangeScene then
        local ok, wx, wy, wz = pcall(csWorld.GetCurTarget, csWorld)
        if ok and wx and wz and (wx > 0 or wz > 0) then
            if mgr and mgr.curCameraTarget and mgr.curCameraTarget.Set then
                mgr.curCameraTarget:Set(wx, wy, wz)
            end
            local tx, ty = SceneUtils.WorldToTileXZ(wx, wz, ForceChangeScene.World)
            if tx and ty and tx >= 0 and ty >= 0 then
                _G._lastValidCamX = tx
                _G._lastValidCamY = ty
                return tx, ty
            end
        end
    end
    local mainCam = CS and CS.UnityEngine and CS.UnityEngine.Camera and CS.UnityEngine.Camera.main
    if not IsNull(mainCam) and SceneUtils and SceneUtils.WorldToTileXZ and ForceChangeScene then
        local pos = mainCam.transform.position
        local fwd = mainCam.transform.forward
        if fwd.y ~= 0 then
            local t = -pos.y / fwd.y
            local gx = pos.x + fwd.x * t
            local gz = pos.z + fwd.z * t
            local tx, ty = SceneUtils.WorldToTileXZ(gx, gz, ForceChangeScene.World)
            if tx and ty and tx >= 0 and ty >= 0 then
                _G._lastValidCamX = tx
                _G._lastValidCamY = ty
                return tx, ty
            end
        end
    end
    if mgr and mgr.curCameraTarget and (mgr.curCameraTarget.x > 0 or mgr.curCameraTarget.z > 0) and SceneUtils and SceneUtils.WorldToTileXZ and ForceChangeScene then
        local tx, ty = SceneUtils.WorldToTileXZ(mgr.curCameraTarget.x, mgr.curCameraTarget.z, ForceChangeScene.World)
        if tx and ty and tx > 0 and ty > 0 then
            _G._lastValidCamX = tx
            _G._lastValidCamY = ty
            return tx, ty
        end
    end
    if _G._lastValidCamX and _G._lastValidCamY then
        return _G._lastValidCamX, _G._lastValidCamY
    end
    if mgr and mgr.reqPos and mgr.reqPos.x and mgr.reqPos.x > 0 then
        return mgr.reqPos.x, mgr.reqPos.y
    end
    return 500, 500
end

local function GetMasterRefCache()
    local rc = _G._MasterReflectionCache
    if rc then return rc end
    local flags = CS.System.Reflection.BindingFlags
    local toInt = CS.System.Convert.ToInt32
    local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)
    local boxedInts = {}
    for idx = 1, 12 do
        boxedInts[idx] = toInt(idx)
    end
    rc = {
        allFlags = allFlags,
        toInt = toInt,
        boxedInts = boxedInts,
        boxed2048 = toInt(2048),
        shadowField = nil,
        shadowVal2048 = nil,
        zoomParamsField = nil,
        adjSettingsField = nil,
        adjTargetsField = nil,
        adjShowLodsField = nil,
        typeAnimator = typeof(CS.UnityEngine.Animator),
        typeParticle = typeof(CS.UnityEngine.ParticleSystem),
        typeRenderer = typeof(CS.UnityEngine.Renderer),
        typeAutoAdjustLod = typeof(CS.AutoAdjustLod),
        cullTransform = CS.UnityEngine.AnimatorCullingMode.CullUpdateTransforms,
        particlePause = CS.UnityEngine.ParticleSystemCullingMode.Pause,
        shadowOff = CS.UnityEngine.Rendering.ShadowCastingMode.Off,
        vecScale25 = CS.UnityEngine.Vector3(2.5, 2.5, 2.5),
        vecOne = CS.UnityEngine.Vector3.one,
    }
    _G._MasterReflectionCache = rc
    return rc
end

function _G.ApplyLastZWorldMaster()
    local app = CS.UnityEngine.Application
    local qs = CS.UnityEngine.QualitySettings
    local mgr = DataCenter and DataCenter.WorldPointManager
    local ws = SceneManager and SceneManager.World
    local rc = GetMasterRefCache()

    -- Hardware graphics (180 fps, 2x msaa, 120m shadow distance)
    if app then
        if app.targetFrameRate ~= 180 then app.targetFrameRate = 180 end
    end
    if qs then
        if qs.vSyncCount ~= 0 then qs.vSyncCount = 0 end
        qs.anisotropicFiltering = CS.UnityEngine.AnisotropicFiltering.ForceEnable
        if qs.antiAliasing ~= 2 then qs.antiAliasing = 2 end
        qs.shadows = CS.UnityEngine.ShadowQuality.All
        if qs.shadowCascades ~= 2 then qs.shadowCascades = 2 end
        if qs.shadowDistance ~= 120.0 then qs.shadowDistance = 120.0 end
        if qs.shadowNearPlaneOffset ~= 0.8 then qs.shadowNearPlaneOffset = 0.8 end
        qs.shadowResolution = CS.UnityEngine.ShadowResolution.High
        if qs.asyncUploadTimeSlice ~= 16 then qs.asyncUploadTimeSlice = 16 end
        if qs.asyncUploadBufferSize ~= 256 then qs.asyncUploadBufferSize = 256 end
        if qs.asyncUploadPersistentBuffer ~= true then qs.asyncUploadPersistentBuffer = true end
        if qs.lodBias ~= 2.5 then qs.lodBias = 2.5 end
        if qs.maximumLODLevel ~= 0 then qs.maximumLODLevel = 0 end
    end
    _G._MasterPerfDirty = false

    local gs = CS.UnityEngine.Rendering and CS.UnityEngine.Rendering.GraphicsSettings
    local rp = gs and (gs.currentRenderPipeline or gs.renderPipelineAsset)
    if not IsNull(rp) then
        rp.shadowDistance = 120.0
        rp.shadowCascadeCount = 2
        rp.shadowDepthBias = 1.2
        rp.shadowNormalBias = 1.2
        rp.msaaSampleCount = 2
        if rc.shadowField == nil then
            local fRes = rp:GetType():GetField("m_MainLightShadowmapResolution", rc.allFlags)
            rc.shadowField = fRes or false
            if fRes then
                rc.shadowVal2048 = CS.System.Enum.ToObject(fRes.FieldType, rc.boxed2048)
            end
        end
        if rc.shadowField and rc.shadowVal2048 then
            rc.shadowField:SetValue(rp, rc.shadowVal2048)
        end
    end

    local ok_qsu, qsu = pcall(require, "Util.QualitySettingUtil")
    if ok_qsu and qsu then
        qsu.OnLowFps = function() end
        if qsu._origSetGraphicQuality == nil and type(qsu.SetGraphicQuality) == "function" then
            qsu._origSetGraphicQuality = qsu.SetGraphicQuality
        end
        local origSetGraphicQuality = qsu._origSetGraphicQuality
        qsu.SetGraphicQuality = function(...)
            if origSetGraphicQuality then pcall(origSetGraphicQuality, ...) end
            if app and app.targetFrameRate ~= 180 then app.targetFrameRate = 180 end
            if qs and qs.vSyncCount ~= 0 then qs.vSyncCount = 0 end
            _G._MasterPerfDirty = true
        end
    end

    pcall(collectgarbage, "setpause", 200)
    pcall(collectgarbage, "setstepmul", 200)

    if not mgr then
        return "WAITING_FOR_WORLD_POINT_MANAGER"
    end

    -- Camera setup (far 12000, near 20)
    if ws and ws.Camera then
        ws.Camera.ReCalcFarPlane = function(self, camDist)
            if self.camera and not IsNull(self.camera) then
                self.camera.farClipPlane = 12000.0
                self.camera.nearClipPlane = 20.0
            end
        end
        if ws.Camera.camera and not IsNull(ws.Camera.camera) then
            ws.Camera.camera.farClipPlane = 12000.0
            ws.Camera.camera.nearClipPlane = 20.0
        end
    end
    local mainCam = CS.UnityEngine.Camera.main
    if not IsNull(mainCam) then
        mainCam.farClipPlane = 12000.0
        mainCam.nearClipPlane = 20.0
    end

    -- Scrolling and panning overhaul
    if ws and ws.Camera and ws.Camera.touchCamera and not IsNull(ws.Camera.touchCamera) then
        local tc = ws.Camera.touchCamera
        pcall(function() tc.AutoScrollVelocityMax = 1600.0 end)
        pcall(function() tc.AutoScrollDamp = 700.0 end)
        pcall(function() tc.zoomTime = 0.06 end)
        pcall(function() tc.CamFollowFactor = 45.0 end)

        if tc.AutoScrollDamps then
            tc.AutoScrollDamps:Clear()
            local smoothDamps = { 200, 250, 300, 350, 400, 500, 600, 750, 900, 1000 }
            for i = 1, #smoothDamps do tc.AutoScrollDamps:Add(smoothDamps[i]) end
        end

        if rc.zoomParamsField == nil then
            rc.zoomParamsField = tc:GetType():GetField("zoomParams", rc.allFlags) or false
        end
        local zparams = rc.zoomParamsField and rc.zoomParamsField:GetValue(tc)
        if zparams and zparams.Count >= 3 then
            pcall(function() zparams[0].sensitivity = 150.0 end)
            pcall(function() zparams[1].sensitivity = 200.0 end)
            pcall(function() zparams[2].sensitivity = 400.0 end)
        end
    end

    if ws and ws.Camera then
        ws.Camera.SetScrollDamps = function(self) end
        if ws.Camera.AfterUpdateAction then
            ws.Camera.AfterUpdateAction["KeyboardWASDPanning"] = nil
        end
    end

    -- Smart adjuster expander (cached FieldInfo & boxed Int32)
    local function ensureAdjusterReflection(adj)
        if rc.adjSettingsField ~= nil then return rc.adjSettingsField end
        local adjType = (adj and adj:GetType()) or rc.typeAutoAdjustLod
        if not adjType then return false end
        local f = adjType:GetField("settings", rc.allFlags) or false
        rc.adjSettingsField = f
        if f and adj then
            local arr = f:GetValue(adj)
            if arr and arr.GetType then
                local settingType = arr:GetType():GetElementType()
                if settingType then
                    rc.adjTargetsField = settingType:GetField("targets", rc.allFlags) or false
                    rc.adjShowLodsField = settingType:GetField("showLods", rc.allFlags) or false
                end
            end
        end
        return f
    end
    pcall(ensureAdjusterReflection, nil)

    local function expandAdjuster(adj)
        if not adj or IsNull(adj) then return false end
        local f = rc.adjSettingsField or ensureAdjusterReflection(adj)
        if not f then return false end
        local arr = f:GetValue(adj)
        if not arr or arr.Length == 0 then return false end
        local tF = rc.adjTargetsField
        local lF = rc.adjShowLodsField
        if tF == nil or lF == nil then
            local settingType = arr:GetType():GetElementType()
            tF = settingType:GetField("targets", rc.allFlags) or false
            lF = settingType:GetField("showLods", rc.allFlags) or false
            rc.adjTargetsField = tF
            rc.adjShowLodsField = lF
        end
        local boxedInts = rc.boxedInts

        for i = 0, arr.Length - 1 do
            local s = arr[i]
            local targets = tF and tF:GetValue(s)
            local llist = lF and lF:GetValue(s)
            if targets and llist then
                for t = 0, targets.Length - 1 do
                    local tObj = targets[t]
                    if not IsNull(tObj) then
                        local tname = tObj.name
                        if tname == "ModelGo" or tname == "Model" or tname == "ModelInstance" then
                            llist:Clear()
                            llist:Add(boxedInts[1])
                            llist:Add(boxedInts[2])
                        elseif tname == "Icon" or tname == "IconHouse" or tname == "IconNormal" or tname == "FarIcon" or tname == "lodSetObj" then
                            llist:Clear()
                            for l = 3, 12 do llist:Add(boxedInts[l]) end
                        elseif tname == "NameLabel" or tname == "LevelLabel" or string.find(tname, "Near") or string.find(tname, "ModelHead") or tname == "ModelLabel" or string.find(tname, "Far") or string.find(tname, "IconHead") or tname == "IconLabel" then
                            llist:Clear()
                            for l = 1, 12 do llist:Add(boxedInts[l]) end
                        end
                    end
                end
            end
        end

        local curLod = GetHysteresisLod((mgr and mgr.lodLv) or 1)
        pcall(adj.UpdateLod, adj, curLod)
        return true
    end

    if WorldPointObject and not WorldPointObject.__masterAdjusterHooked then
        local old_SetAutoAdjustLod = WorldPointObject.SetAutoAdjustLod
        WorldPointObject.SetAutoAdjustLod = function(self)
            if old_SetAutoAdjustLod then old_SetAutoAdjustLod(self) end
            if self.adjuster and not IsNull(self.adjuster) then
                expandAdjuster(self.adjuster)
            end
        end
        WorldPointObject.__masterAdjusterHooked = true
    end

    _G._MasterSeenMaterialIds = _G._MasterSeenMaterialIds or {}
    _G._MasterSeenMatCount = _G._MasterSeenMatCount or 0
    local function optimizeInstance(inst)
        if IsNull(inst) then return end
        local instType = type(inst)
        if (instType ~= "userdata" and instType ~= "table") or not inst.GetComponentsInChildren then
            return
        end
        local okAnim, animators = pcall(inst.GetComponentsInChildren, inst, rc.typeAnimator, true)
        if okAnim and animators then
            local cullMode = rc.cullTransform
            for i = 0, animators.Length - 1 do
                if animators[i].cullingMode ~= cullMode then
                    animators[i].cullingMode = cullMode
                end
            end
        end
        local okPart, particles = pcall(inst.GetComponentsInChildren, inst, rc.typeParticle, true)
        if okPart and particles then
            local pPause = rc.particlePause
            for i = 0, particles.Length - 1 do
                if particles[i].cullingMode ~= pPause then
                    particles[i].cullingMode = pPause
                end
            end
        end
        local okRend, renderers = pcall(inst.GetComponentsInChildren, inst, rc.typeRenderer, true)
        if okRend and renderers then
            local seenMats = _G._MasterSeenMaterialIds
            for i = 0, renderers.Length - 1 do
                local sm = renderers[i].sharedMaterial
                if not IsNull(sm) then
                    local matId = sm.GetInstanceID and sm:GetInstanceID() or nil
                    if matId == nil or not seenMats[matId] then
                        if matId ~= nil then
                            if (_G._MasterSeenMatCount or 0) >= 4096 then
                                seenMats = {}
                                _G._MasterSeenMaterialIds = seenMats
                                _G._MasterSeenMatCount = 0
                            end
                            seenMats[matId] = true
                            _G._MasterSeenMatCount = (_G._MasterSeenMatCount or 0) + 1
                        end
                        if not IsNull(sm.shader) then
                            local sName = sm.shader.name or ""
                            if string.find(sName, "Instanc") or string.find(sName, "Standard") or string.find(sName, "Universal") or string.find(sName, "URP") then
                                if sm.enableInstancing ~= true then
                                    sm.enableInstancing = true
                                end
                            end
                        end
                    end
                end
            end
        end
    end

    -- Resource nodes overhaul
    local RESOURCE_LOD_ICON = {
        [1] = "Assets/Main/Sprites/LodIcon/mine_lod_metal.png",
        [2] = "Assets/Main/Sprites/LodIcon/mine_lod_wood.png",
        [12] = "Assets/Main/Sprites/LodIcon/mine_lod_electricity.png",
        [14] = "Assets/Main/Sprites/LodIcon/mine_lod_money.png",
        [15] = "Assets/Main/Sprites/LodIcon/gold_select.png"
    }
    local DEFAULT_RESOURCE_LOD_ICON = "Assets/Main/Sprites/LodIcon/mine_lod_money.png"
    local RESOURCE_ICON_CFG = {
        offset = CS.UnityEngine.Vector3(0, 2, 0),
        scale = CS.UnityEngine.Vector3(2.7, 2.7, 1.0)
    }

    -- Monster GPU-instanced proxy configuration (pType == 4 zoomed-out / distant rendering)
    local MONSTER_LOD_ICON = {
        ZOMBIE = "Assets/Main/Sprites/LodIcon/monster.png",
        BOOMER = "Assets/Main/Sprites/LodIcon/G_Sj_iocnboss_1.png",
        BOSS   = "Assets/Main/Sprites/LodIcon/UIworld_img_boss.png",
    }
    local MONSTER_ICON_CFG = {
        offset = CS.UnityEngine.Vector3(0, 1.6, 0),
        scale  = CS.UnityEngine.Vector3(2.2, 2.2, 1.0),
    }
    local MONSTER_BOSS_CFG = {
        offset = CS.UnityEngine.Vector3(0, 2.2, 0),
        scale  = CS.UnityEngine.Vector3(3.0, 3.0, 1.0),
    }
    local MONSTER_LABEL_CFG = {
        offset = CS.UnityEngine.Vector3(0, 0.35, 0),
        scale  = CS.UnityEngine.Vector3(1.0, 1.0, 1.0),
    }

    local _MonsterFallbackBatch = _G._MasterMonsterFallbackBatch
    if not _MonsterFallbackBatch then
        _MonsterFallbackBatch = {
            entries = {},
            count = 0,
            dirty = false,
            chunks = {},
            mesh = nil,
            mat = nil,
            mpb = nil,
            hookedCamera = false,
        }
        _G._MasterMonsterFallbackBatch = _MonsterFallbackBatch
    end

    local function _ensureFallbackAssets()
        local fb = _MonsterFallbackBatch
        if fb.mesh and fb.mat then return true end
        local ue = CS and CS.UnityEngine
        if not ue or not ue.Mesh or not ue.Material or not ue.Shader or not ue.Graphics then
            return false
        end
        local ok = pcall(function()
            if not fb.mesh then
                local m = ue.Mesh()
                m.name = "MasterMonsterProxyQuad"
                local verts = CS.System.Array.CreateInstance(typeof(ue.Vector3), 4)
                verts[0] = ue.Vector3(-0.5, -0.5, 0)
                verts[1] = ue.Vector3(0.5, -0.5, 0)
                verts[2] = ue.Vector3(0.5, 0.5, 0)
                verts[3] = ue.Vector3(-0.5, 0.5, 0)
                local tris = CS.System.Array.CreateInstance(typeof(CS.System.Int32), 6)
                tris[0] = 0; tris[1] = 2; tris[2] = 1
                tris[3] = 0; tris[4] = 3; tris[5] = 2
                m.vertices = verts
                m.triangles = tris
                m:RecalculateBounds()
                fb.mesh = m
            end
            if not fb.mat then
                local shader = ue.Shader.Find("Universal Render Pipeline/Unlit")
                    or ue.Shader.Find("Sprites/Default")
                    or ue.Shader.Find("Unlit/Color")
                if shader then
                    local mat = ue.Material(shader)
                    mat.enableInstancing = true
                    if ue.Color then
                        pcall(function() mat.color = ue.Color(0.95, 0.35, 0.25, 0.9) end)
                    end
                    fb.mat = mat
                end
            end
            if not fb.mpb and ue.MaterialPropertyBlock then
                fb.mpb = ue.MaterialPropertyBlock()
            end
        end)
        return ok and fb.mesh ~= nil and fb.mat ~= nil
    end

    local function _rebuildFallbackChunks()
        local fb = _MonsterFallbackBatch
        fb.dirty = false
        fb.chunks = {}
        if fb.count <= 0 then return end
        local ue = CS and CS.UnityEngine
        local sysArr = CS and CS.System and CS.System.Array
        if not ue or not ue.Matrix4x4 or not ue.Quaternion then return end
        local list = {}
        for _, item in pairs(fb.entries) do
            list[#list + 1] = item
        end
        fb.count = #list
        local rot = ue.Quaternion.Euler(60, 0, 0)
        local idx = 1
        while idx <= #list do
            local endIdx = math.min(#list, idx + 1022)
            local sliceLen = endIdx - idx + 1
            local matArr = (sysArr and sysArr.CreateInstance)
                and sysArr.CreateInstance(typeof(ue.Matrix4x4), sliceLen)
                or {}
            for i = 0, sliceLen - 1 do
                local it = list[idx + i]
                local mat = ue.Matrix4x4.TRS(it.pos, rot, it.scale)
                if type(matArr) == "table" then
                    matArr[i + 1] = mat
                else
                    matArr[i] = mat
                end
            end
            fb.chunks[#fb.chunks + 1] = { mats = matArr, len = sliceLen }
            idx = endIdx + 1
        end
    end

    function _MonsterFallbackBatch.Set(pointIndex, pos, cfg)
        if not pointIndex or not pos then return false end
        local fb = _MonsterFallbackBatch
        if fb.entries[pointIndex] == nil then
            fb.count = fb.count + 1
        end
        local off = (cfg and cfg.offset) or MONSTER_ICON_CFG.offset
        local sc = (cfg and cfg.scale) or MONSTER_ICON_CFG.scale
        local ue = CS and CS.UnityEngine
        local drawPos = (ue and ue.Vector3)
            and ue.Vector3((pos.x or 0) + (off.x or 0), (pos.y or 0) + (off.y or 0), (pos.z or 0) + (off.z or 0))
            or pos
        fb.entries[pointIndex] = { pos = drawPos, scale = sc }
        fb.dirty = true
        return true
    end

    function _MonsterFallbackBatch.Remove(pointIndex)
        local fb = _MonsterFallbackBatch
        if pointIndex ~= nil and fb.entries[pointIndex] ~= nil then
            fb.entries[pointIndex] = nil
            fb.count = math.max(0, fb.count - 1)
            fb.dirty = true
        end
    end

    function _MonsterFallbackBatch.Clear()
        local fb = _MonsterFallbackBatch
        fb.entries = {}
        fb.count = 0
        fb.chunks = {}
        fb.dirty = false
    end

    function _MonsterFallbackBatch.Render(cam)
        local fb = _MonsterFallbackBatch
        if fb.count <= 0 then return end
        local ueCam = CS and CS.UnityEngine and CS.UnityEngine.Camera
        if cam ~= nil and ueCam and ueCam.main and not IsNull(ueCam.main) and cam ~= ueCam.main then
            return
        end
        local curMgr = DataCenter and DataCenter.WorldPointManager
        if not curMgr or curMgr.isInit ~= true then return end
        if not _ensureFallbackAssets() then return end
        if fb.dirty then
            _rebuildFallbackChunks()
        end
        local gfx = CS and CS.UnityEngine and CS.UnityEngine.Graphics
        if not gfx or not gfx.DrawMeshInstanced then return end
        for i = 1, #fb.chunks do
            local c = fb.chunks[i]
            pcall(gfx.DrawMeshInstanced, fb.mesh, 0, fb.mat, c.mats, c.len, fb.mpb)
        end
    end

    if not _MonsterFallbackBatch.hookedCamera then
        local ueCam = CS and CS.UnityEngine and CS.UnityEngine.Camera
        if ueCam then
            local cb = function(cam)
                _MonsterFallbackBatch.Render(cam)
            end
            local okHook = pcall(function()
                local cur = ueCam.onPreCull
                if cur == nil then
                    ueCam.onPreCull = cb
                elseif type(cur) == "function" then
                    ueCam.onPreCull = function(cam)
                        cur(cam)
                        cb(cam)
                    end
                else
                    local okAdd = pcall(function()
                        ueCam.onPreCull = cur + cb
                    end)
                    if not okAdd then
                        ueCam.onPreCull("+", cb)
                    end
                end
            end)
            if okHook and ueCam.onPreCull ~= nil then
                _MonsterFallbackBatch.hookedCamera = true
            end
        end
    end

    local ok_wroi, wroi = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldResObjectInstanced")
    if ok_wroi and wroi then
        wroi._IsResourceLodVisible = function(self) return true end
        wroi._ShouldShowInstancedLabel = function(self, info)
            if (self.lodLv or 1) > 2 or not self.pointIndex then return false end
            local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
            local px, py = FastIndexToXY(self.pointIndex)
            return math.abs(px - camX) <= 85 and math.abs(py - camY) <= 85
        end

        wroi._GetFarIconPath = function(self, info)
            local bi = info and info.resourceInfo
            if nil == bi then return DEFAULT_RESOURCE_LOD_ICON end
            local rt = GetTableData(TableName.GatherResource, bi.resourceId, "resource_type")
            return RESOURCE_LOD_ICON[rt] or DEFAULT_RESOURCE_LOD_ICON
        end

        wroi._GetFarIconConfig = function(self, info)
            return RESOURCE_ICON_CFG
        end

        wroi.RefreshInstancedFarIcon = function(self, info, forceAll)
            local path = self:_GetFarIconPath(info)
            local cfg = self:_GetFarIconConfig(info)
            if nil == path or "" == path then path = DEFAULT_RESOURCE_LOD_ICON end
            if nil == self.cachedWorldPos and self.pointIndex and SceneUtils and SceneUtils.TileIndexToWorld and ForceChangeScene then
                self.cachedWorldPos = SceneUtils.TileIndexToWorld(self.pointIndex, ForceChangeScene.World)
            end
            if nil == self.cachedWorldPos then return end

            local iconRenderer = mgr and mgr.GetIconRenderer and mgr:GetIconRenderer()
            if not iconRenderer then return end

            if nil == self.iconHandle then
                self.iconHandle = iconRenderer:AddIcon(self.cachedWorldPos, path, cfg)
                self.iconPath = path
            elseif forceAll or self.iconPath ~= path then
                self.iconHandle = iconRenderer:UpdateIcon(self.iconHandle, self.cachedWorldPos, path, cfg)
                self.iconPath = path
            end
        end
    end

    local function applySmartInstancedLodState(self, info, forceAll)
        local toggles = _G._MasterToggles
        if toggles and (toggles.masterEnabled == false or toggles.showResources == false) then
            if self.RemoveInstancedModel then self:RemoveInstancedModel() end
            if self.DestroyInstancedFarIcon then self:DestroyInstancedFarIcon() end
            if self.RemoveInstancedLabel then self:RemoveInstancedLabel() end
            return
        end
        local rawLod = self.lodLv or 0
        local useNear3D = false
        if rawLod <= 2 and self.pointIndex then
            local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
            local px, py = FastIndexToXY(self.pointIndex)
            if math.abs(px - camX) <= 85 and math.abs(py - camY) <= 85 then
                useNear3D = true
            end
        end
        if useNear3D then
            self:RefreshInstancedModel(info, forceAll)
            if self.DestroyInstancedFarIcon then self:DestroyInstancedFarIcon() end
        else
            self:RemoveInstancedModel()
            self:RefreshInstancedFarIcon(info, forceAll)
        end
        self:RefreshInstancedLabel(info)
    end

    local function fastInstancedLodChange(self, lod)
        local oldLod = self.lodLv or 0
        if oldLod == lod then return end
        self.lodLv = lod
        if lod >= 3 and oldLod >= 3 then return end

        local px = self._cachedTileX
        local py = self._cachedTileY
        if not px or not py then
            px, py = FastIndexToXY(self.pointIndex)
            self._cachedTileX = px
            self._cachedTileY = py
        end
        local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
        local wasNear = oldLod <= 2 and math.abs(px - camX) <= 85 and math.abs(py - camY) <= 85
        local isNear = lod <= 2 and math.abs(px - camX) <= 85 and math.abs(py - camY) <= 85
        if wasNear == isNear and oldLod >= 3 and lod >= 3 then return end

        local info = mgr and mgr:GetPointInfo(self.pointIndex)
        if info then self:_ApplyInstancedLodState(info) end
    end

    local ok_wir, wir = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldInstancedRepresentation")
    if ok_wir and wir then
        wir.RefreshInstancedFarIcon = function(self, info, forceAll)
            local path = self:_GetFarIconPath(info)
            local cfg = self:_GetFarIconConfig(info)
            if nil == path or "" == path then return end
            if nil == self.cachedWorldPos and self.pointIndex and SceneUtils and SceneUtils.TileIndexToWorld and ForceChangeScene then
                self.cachedWorldPos = SceneUtils.TileIndexToWorld(self.pointIndex, ForceChangeScene.World)
            end
            if nil == self.cachedWorldPos then return end

            local iconRenderer = mgr and mgr.GetIconRenderer and mgr:GetIconRenderer()
            if not iconRenderer then return end

            if nil == self.iconHandle then
                self.iconHandle = iconRenderer:AddIcon(self.cachedWorldPos, path, cfg)
                self.iconPath = path
            elseif forceAll or self.iconPath ~= path then
                self.iconHandle = iconRenderer:UpdateIcon(self.iconHandle, self.cachedWorldPos, path, cfg)
                self.iconPath = path
            end
        end

        wir._ApplyInstancedLodState = applySmartInstancedLodState
        wir._InstancedOnLodChanged = fastInstancedLodChange
    end
    if ok_wroi and wroi then
        wroi._ApplyInstancedLodState = applySmartInstancedLodState
        wroi._InstancedOnLodChanged = fastInstancedLodChange
        local wroiMt = getmetatable(wroi)
        if wroiMt and type(wroiMt.__index) == "table" then
            wroiMt.__index._ApplyInstancedLodState = applySmartInstancedLodState
            wroiMt.__index._InstancedOnLodChanged = fastInstancedLodChange
            wroiMt.__index.RefreshInstancedFarIcon = wroi.RefreshInstancedFarIcon
            wroiMt.__index._ShouldShowInstancedLabel = wroi._ShouldShowInstancedLabel
            wroiMt.__index._IsResourceLodVisible = wroi._IsResourceLodVisible
        end
    end

    -- Seasonal buildings
    local ok_wboil, wboil = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldBuildObjectInstancedLod")
    if ok_wboil and wboil then
        wboil.CreateGameObject = function(self)
            local baseCls = WorldPointObject
            if baseCls and baseCls.CreateGameObject then baseCls.CreateGameObject(self) end

            self.lodLv = CS.SceneManager.World ~= nil and CS.SceneManager.World:GetLodLevel() or 0
            local info = mgr and mgr:GetPointInfo(self.pointIndex)
            if nil == info then return end
            if self:_RefreshData(info) == false then return end

            self.cachedWorldPos = SceneUtils.TileIndexToWorld(self.pointIndex, ForceChangeScene.World)
            if (self.lodLv or 0) <= 2 then
                self:CreateModelInstance(info)
                self:CreateLabel(info)
            else
                self:CreateFarIcon(info)
                if self.DestroyLabel then self:DestroyLabel() end
            end
            self:_CheckOverlays(info)
        end

        wboil.OnLodChanged = function(self, lod)
            if self.lodLv == lod then return end
            local oldLod = self.lodLv or 0
            self.lodLv = lod
            local oldNear = oldLod <= 2
            local newNear = lod <= 2
            if oldNear ~= newNear then
                local info = mgr and mgr:GetPointInfo(self.pointIndex)
                if nil ~= info then self:_RefreshData(info) end
                if newNear then
                    if self.DestroyFarIcon then self:DestroyFarIcon() end
                    if info then
                        self:CreateModelInstance(info)
                        self:CreateLabel(info)
                    end
                else
                    if self.DestroyModelInstance then self:DestroyModelInstance() end
                    if self.DestroyLabel then self:DestroyLabel() end
                    if info then
                        self:CreateFarIcon(info)
                    end
                end
            end
            self:_OnLodSwitched()
            self:UpdateTargetAnchor()
        end
    end

    -- Player bases
    local ok_wbo, wbo = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldBuildObject")
    if ok_wbo and wbo then
        if not wbo.__masterHooked then
            wbo.__masterHooked = true
            local origSetAutoAdjustLod = wbo.SetAutoAdjustLod
            wbo.SetAutoAdjustLod = function(self, info)
                if origSetAutoAdjustLod then pcall(origSetAutoAdjustLod, self, info) end
                if not self.adjuster and self.gameObject and not IsNull(self.gameObject) then
                    self.adjuster = self.gameObject:GetComponent(rc.typeAutoAdjustLod)
                end
                if self.adjuster and not IsNull(self.adjuster) then
                    expandAdjuster(self.adjuster)
                    self.adjuster:UpdateLod((mgr and mgr.lodLv) or 1)
                end
                if info then pcall(self.SetBuildIconColor, self, info) end
            end

            local origOnMainModelLoaded = wbo._origOnMainModelLoaded or wbo.OnMainModelLoaded
            wbo._origOnMainModelLoaded = origOnMainModelLoaded
            wbo.OnMainModelLoaded = function(self, go, ...)
                if origOnMainModelLoaded then pcall(origOnMainModelLoaded, self, go, ...) end
                local target = (not IsNull(go) and go)
                    or (not IsNull(self.model) and self.model)
                    or (not IsNull(self.mainModel) and self.mainModel)
                    or (not IsNull(self.gameObject) and self.gameObject)
                if target then
                    optimizeInstance(target)
                end
            end

            if type(wbo.CreateMain) == "function" then
                local origCreateMain = wbo._origCreateMain or wbo.CreateMain
                wbo._origCreateMain = origCreateMain
                wbo.CreateMain = function(self, info, ...)
                    local curLod = (mgr and mgr.lodLv) or 1
                    if curLod >= 3 then
                        return
                    end
                    if self.pointIndex then
                        local px = self._cachedTileX
                        local py = self._cachedTileY
                        if not px or not py then
                            px, py = FastIndexToXY(self.pointIndex)
                            self._cachedTileX = px
                            self._cachedTileY = py
                        end
                        local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
                        if math.abs(px - camX) > 110 or math.abs(py - camY) > 110 then
                            return
                        end
                    end
                    return origCreateMain(self, info, ...)
                end
            end

            wbo.CheckIdleShowAnim = function(self) end
            wbo.OnRandomNextIdleAnim = function(self) end
            wbo.RandomNextPlayIdleTime = function(self) return 999999 end

            local origSetProtectRenderVisible = wbo.SetProtectRenderVisible
            wbo.SetProtectRenderVisible = function(self, isVisible)
                local info = mgr and mgr:GetPointInfo(self.pointIndex)
                local bi = info and info.buildInfo
                local protectEnd = bi and bi.protectEndTime
                local hasShield = (protectEnd ~= nil and protectEnd > 0) and (protectEnd > os.time())

                if hasShield then
                    if origSetProtectRenderVisible then pcall(origSetProtectRenderVisible, self, true) end
                    if self.protectRender and not IsNull(self.protectRender) then
                        if self.cachedWorldPos and self.protectRender.transform then
                            self.protectRender.transform.position = self.cachedWorldPos
                            local curLod = (mgr and mgr.lodLv) or 1
                            if curLod >= 4 then
                                self.protectRender.transform.localScale = rc.vecScale25
                            else
                                self.protectRender.transform.localScale = rc.vecOne
                            end
                        end
                        if self._cachedProtectRendererTarget ~= self.protectRender or self._cachedProtectRenderer == nil then
                            self._cachedProtectRendererTarget = self.protectRender
                            self._cachedProtectRenderer = self.protectRender:GetComponent(rc.typeRenderer) or false
                        end
                        local prMesh = self._cachedProtectRenderer
                        if prMesh and not IsNull(prMesh) then
                            if prMesh.shadowCastingMode ~= rc.shadowOff then
                                prMesh.shadowCastingMode = rc.shadowOff
                            end
                            if prMesh.receiveShadows ~= false then
                                prMesh.receiveShadows = false
                            end
                        end
                        if self.protectRender.enabled == false then self.protectRender.enabled = true end
                        if self.protectRender.gameObject and not self.protectRender.gameObject.activeSelf then
                            self.protectRender.gameObject:SetActive(true)
                        end
                    end
                else
                    if origSetProtectRenderVisible then pcall(origSetProtectRenderVisible, self, isVisible) end
                end
            end

            local function fastBuildLodChange(self, lod)
                local oldLod = self.lodLv or 0
                if oldLod == lod then return end
                self.lodLv = lod
                if lod >= 3 and oldLod >= 3 then return end

                local px = self._cachedTileX
                local py = self._cachedTileY
                if not px or not py then
                    px, py = FastIndexToXY(self.pointIndex)
                    self._cachedTileX = px
                    self._cachedTileY = py
                end
                local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
                local wasNear = oldLod <= 2 and math.abs(px - camX) <= 110 and math.abs(py - camY) <= 110
                local isNear = lod <= 2 and math.abs(px - camX) <= 110 and math.abs(py - camY) <= 110
                if wasNear == isNear and oldLod >= 3 and lod >= 3 then return end

                if not self.adjuster and self.gameObject and not IsNull(self.gameObject) then
                    self.adjuster = self.gameObject:GetComponent(typeof(CS.AutoAdjustLod))
                end
                if self.adjuster and not IsNull(self.adjuster) then
                    self.adjuster:UpdateLod(lod)
                end

                local info = mgr and mgr:GetPointInfo(self.pointIndex)
                if info and self.CheckShowEffect then
                    pcall(self.CheckShowEffect, self, info, lod)
                end
                if isNear and not self.instance and self.CreateMain then
                    pcall(self.CreateMain, self, info)
                end
            end
            wbo.LodChange = fastBuildLodChange
            local wboMt = getmetatable(wbo)
            if wboMt and type(wboMt.__index) == "table" then
                wboMt.__index.LodChange = fastBuildLodChange
            end
        end
    end

    -- Player HQ Labels & Depth Occlusion Fix
    local ok_uiwl, uiwl = pcall(require, "SlgEngine.DataCenter.WorldPointManager.UIWorldLabel")
    if ok_uiwl and uiwl and not uiwl.__masterLabelHooked then
        uiwl.__masterLabelHooked = true
        local function fixNameDepthAndPosition(self)
            if self.nameObj and not IsNull(self.nameObj) then
                self.nameObj.transform.localPosition = CS.UnityEngine.Vector3(0, -0.42, -0.60)
                local sr = self.nameObj:GetComponent(typeof(CS.UnityEngine.SpriteRenderer))
                if sr and not IsNull(sr) then
                    sr.sortingOrder = 50
                    if not sr.enabled then sr.enabled = true end
                end
                if self.nameTxt and not IsNull(self.nameTxt) then
                    local mr = self.nameTxt:GetComponent(typeof(CS.UnityEngine.MeshRenderer))
                    if mr and not IsNull(mr) then
                        mr.sortingOrder = 51
                        if not mr.enabled then mr.enabled = true end
                        if mr.material then
                            mr.material:SetFloat("_ZTest", 8)
                        end
                    end
                end
            end
        end

        local origSetName = uiwl.SetName
        uiwl.SetName = function(self, name, color, needFitLevel, needFitCountry)
            if origSetName then pcall(origSetName, self, name, color, needFitLevel, needFitCountry) end
            fixNameDepthAndPosition(self)
        end

        local origSetNameAutoFit = uiwl.SetNameAutoFit
        uiwl.SetNameAutoFit = function(self, ...)
            if origSetNameAutoFit then pcall(origSetNameAutoFit, self, ...) end
            fixNameDepthAndPosition(self)
        end
    end

    -- Zombies and monsters overhaul (GPU-instanced proxy at lodLv >= 3 or distant, lazy near-3D promotion)
    local ok_wmo, wmo = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldMonsterObject")
    if ok_wmo and wmo then
        local origRefreshLod = wmo._origRefreshLodType or wmo.RefreshLodType
        wmo._origRefreshLodType = origRefreshLod
        wmo.RefreshLodType = function(self)
            if self._isProxyMode then return end
            if self.lodSetObj and not IsNull(self.lodSetObj) and self.lodSetObj.gameObject then
                self.lodSetObj.gameObject:SetActive(true)
            end
            if self.lodSetObj_2 and not IsNull(self.lodSetObj_2) and self.lodSetObj_2.gameObject then
                self.lodSetObj_2.gameObject:SetActive(true)
            end
            if self.lodSetObj_3 and not IsNull(self.lodSetObj_3) and self.lodSetObj_3.gameObject then
                self.lodSetObj_3.gameObject:SetActive(true)
            end
        end

        local origCreateGO = wmo._origCreateGO or wmo.CreateGameObject
        wmo._origCreateGO = origCreateGO
        local origOnCreateGO = wmo._origOnCreateGO or wmo.OnCreateGameObject
        wmo._origOnCreateGO = origOnCreateGO
        local origDestroy = wmo._origDestroy or wmo.Destroy
        wmo._origDestroy = origDestroy
        local origUpdateGO = wmo._origUpdateGO or wmo.UpdateGameObject
        wmo._origUpdateGO = origUpdateGO
        local origSetIsBattle = wmo._origSetIsBattle or wmo.SetIsBattle
        wmo._origSetIsBattle = origSetIsBattle
        local origPlayAnim = wmo._origPlayAnim or wmo.PlayAnim
        wmo._origPlayAnim = origPlayAnim

        wmo._ShouldUseNear3D = function(self, info)
            local toggles = _G._MasterToggles
            local pIdx = self.pointIndex
            if not pIdx or pIdx <= 0 then
                return "NEAR3D"
            end
            local px = self._cachedTileX
            local py = self._cachedTileY
            if not px or not py then
                px, py = FastIndexToXY(pIdx)
                self._cachedTileX = px
                self._cachedTileY = py
            end
            local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
            local dist = math.max(math.abs(px - camX), math.abs(py - camY))
            if toggles then
                if toggles.masterEnabled == false and dist > 48 then
                    return "HIDDEN"
                end
                info = info or (mgr and mgr.GetPointInfo and mgr:GetPointInfo(pIdx))
                local cat = GetMonsterCategory({ pointInfo = info, _parsedExtra = self.monsterInfo })
                if (cat == "BOOMER" or cat == "BOSS") and toggles.showBoomers == false then
                    return "HIDDEN"
                elseif cat == "ZOMBIE" and toggles.showZombies == false then
                    return "HIDDEN"
                end
            end
            if self.isInBattle == true then
                return "NEAR3D"
            end
            local curLod = (mgr and mgr.lodLv) or 1
            if curLod >= 3 then
                return "PROXY"
            end
            if dist <= MONSTER_NEAR_3D_RADIUS then
                return "NEAR3D"
            end
            return "PROXY"
        end

        wmo._EnsureProxyVisual = function(self, info)
            local pIdx = self.pointIndex
            if not pIdx or pIdx <= 0 then return end
            if _G._MasterProxyMonsters then
                if self._isProxyMode then
                    _G._MasterProxyMonsters[pIdx] = self
                else
                    _G._MasterProxyMonsters[pIdx] = nil
                end
            end
            info = info or (mgr and mgr.GetPointInfo and mgr:GetPointInfo(pIdx))
            if nil == self.cachedWorldPos and SceneUtils and SceneUtils.TileIndexToWorld and ForceChangeScene then
                self.cachedWorldPos = SceneUtils.TileIndexToWorld(pIdx, ForceChangeScene.World)
            end
            if nil == self.cachedWorldPos then return end

            local mi = (info and info.monsterInfo) or (info and info._parsedExtra) or self.monsterInfo
            if not mi and info and info.extraInfo and PBController and PBController.ParsePbFromBytes then
                local okPb, parsed = pcall(PBController.ParsePbFromBytes, info.extraInfo, "protobuf.WorldPointMonster")
                if okPb and parsed then
                    mi = parsed
                    info._parsedExtra = parsed
                end
            end
            if mi then
                self.monsterInfo = mi
            end

            local cat = GetMonsterCategory({ pointInfo = info, _parsedExtra = mi })
            local path = MONSTER_LOD_ICON[cat] or MONSTER_LOD_ICON.ZOMBIE
            local cfg = (cat == "BOSS" or cat == "BOOMER") and MONSTER_BOSS_CFG or MONSTER_ICON_CFG

            local ir = mgr and mgr.GetIconRenderer and mgr:GetIconRenderer()
            if ir and ir.AddIcon then
                if self._proxyIconHandle == nil then
                    local okAdd, handle = pcall(ir.AddIcon, ir, self.cachedWorldPos, path, cfg)
                    if okAdd and handle ~= nil then
                        self._proxyIconHandle = handle
                        self._proxyIconPath = path
                        _MonsterFallbackBatch.Remove(pIdx)
                    else
                        _MonsterFallbackBatch.Set(pIdx, self.cachedWorldPos, cfg)
                    end
                elseif self._proxyIconPath ~= path and ir.UpdateIcon then
                    local okUpd, handle = pcall(ir.UpdateIcon, ir, self._proxyIconHandle, self.cachedWorldPos, path, cfg)
                    if okUpd then
                        if handle ~= nil then
                            self._proxyIconHandle = handle
                        end
                        self._proxyIconPath = path
                    end
                end
            else
                _MonsterFallbackBatch.Set(pIdx, self.cachedWorldPos, cfg)
            end

            local curLod = (mgr and mgr.lodLv) or 1
            local lr = mgr and mgr.GetLabelRenderer and mgr:GetLabelRenderer()
            if curLod <= 4 and mi and mi.monsterId then
                local mtm = DataCenter and DataCenter.MonsterTemplateManager
                if mtm and mtm.GetTableValue then
                    local okLv, lvVal = pcall(mtm.GetTableValue, mtm, mi.monsterId, "level")
                    if okLv and lvVal ~= nil then
                        self.monsterLevel = tonumber(lvVal) or self.monsterLevel or 1
                    end
                end
                local lvNum = tonumber(self.monsterLevel or 1) or 1
                if lr and lr.AddLabel then
                    if self._proxyLabelHandle ~= nil and self._proxyLabelLv ~= lvNum then
                        if lr.RemoveLabel then
                            pcall(lr.RemoveLabel, lr, self._proxyLabelHandle)
                            self._proxyLabelHandle = nil
                            self._proxyLabelLv = nil
                        elseif lr.UpdateLabel then
                            local okUpdL, lHandle = pcall(lr.UpdateLabel, lr, self._proxyLabelHandle, self.cachedWorldPos, lvNum)
                            if okUpdL and lHandle ~= nil then
                                self._proxyLabelHandle = lHandle
                                self._proxyLabelLv = lvNum
                            end
                        end
                    end
                    if self._proxyLabelHandle == nil then
                        local okLbl, lHandle = pcall(lr.AddLabel, lr, self.cachedWorldPos, lvNum, MONSTER_LABEL_CFG)
                        if okLbl and lHandle ~= nil then
                            self._proxyLabelHandle = lHandle
                            self._proxyLabelLv = lvNum
                        end
                    end
                end
                if self._proxyLabelHandle ~= nil then
                    if pIdx and _G._MasterProxyMonsterLabels then
                        _G._MasterProxyMonsterLabels[pIdx] = self
                    end
                elseif pIdx and _G._MasterProxyMonsterLabels then
                    _G._MasterProxyMonsterLabels[pIdx] = nil
                end
            elseif self._proxyLabelHandle ~= nil then
                if lr and lr.RemoveLabel then
                    pcall(lr.RemoveLabel, lr, self._proxyLabelHandle)
                end
                self._proxyLabelHandle = nil
                self._proxyLabelLv = nil
                if pIdx and _G._MasterProxyMonsterLabels then
                    _G._MasterProxyMonsterLabels[pIdx] = nil
                end
            elseif pIdx and _G._MasterProxyMonsterLabels then
                _G._MasterProxyMonsterLabels[pIdx] = nil
            end
        end

        wmo._ClearProxyVisual = function(self)
            if self._proxyIconHandle ~= nil then
                local ir = mgr and mgr.GetIconRenderer and mgr:GetIconRenderer()
                if ir and ir.RemoveIcon then
                    pcall(ir.RemoveIcon, ir, self._proxyIconHandle)
                end
                self._proxyIconHandle = nil
                self._proxyIconPath = nil
            end
            if self._proxyLabelHandle ~= nil then
                local lr = mgr and mgr.GetLabelRenderer and mgr:GetLabelRenderer()
                if lr and lr.RemoveLabel then
                    pcall(lr.RemoveLabel, lr, self._proxyLabelHandle)
                end
                self._proxyLabelHandle = nil
                self._proxyLabelLv = nil
            end
            if self.pointIndex ~= nil then
                if _G._MasterProxyMonsterLabels then
                    _G._MasterProxyMonsterLabels[self.pointIndex] = nil
                end
                if _G._MasterProxyMonsters then
                    _G._MasterProxyMonsters[self.pointIndex] = nil
                end
                _MonsterFallbackBatch.Remove(self.pointIndex)
            end
        end

        wmo._ApplyMonsterLodState = function(self, info)
            local mode = self:_ShouldUseNear3D(info)
            if mode == "HIDDEN" then
                if self.gameObject or self.instance then
                    if origDestroy then pcall(origDestroy, self) end
                    self.gameObject = nil
                    self.instance = nil
                    self.model = nil
                    self.anims = nil
                    self.gpuAnims = nil
                    self.cityLabels = nil
                end
                self:_ClearProxyVisual()
                self._isProxyMode = true
                if self.pointIndex then _G._MasterNear3DMonsters[self.pointIndex] = nil end
            elseif mode == "PROXY" then
                if self.gameObject or self.instance then
                    if origDestroy then pcall(origDestroy, self) end
                    self.gameObject = nil
                    self.instance = nil
                    self.model = nil
                    self.anims = nil
                    self.gpuAnims = nil
                    self.cityLabels = nil
                end
                self._isProxyMode = true
                if self.pointIndex then _G._MasterNear3DMonsters[self.pointIndex] = nil end
                self:_EnsureProxyVisual(info)
            else
                self:_ClearProxyVisual()
                self._isProxyMode = false
                if self.pointIndex then _G._MasterNear3DMonsters[self.pointIndex] = self end
                if not self.gameObject and not self.instance then
                    if origCreateGO then origCreateGO(self) end
                elseif self.gameObject and not IsNull(self.gameObject) and self.gameObject.SetActive then
                    self.gameObject:SetActive(true)
                end
            end
        end

        wmo.CreateGameObject = function(self)
            local pIdx = self.pointIndex
            if not pIdx or pIdx <= 0 then
                if origCreateGO then return origCreateGO(self) end
                return
            end
            local info = mgr and mgr.GetPointInfo and mgr:GetPointInfo(pIdx)
            local mode = self:_ShouldUseNear3D(info)
            if mode == "HIDDEN" then
                self:_ClearProxyVisual()
                self._isProxyMode = true
                _G._MasterNear3DMonsters[pIdx] = nil
                return
            elseif mode == "PROXY" then
                self._isProxyMode = true
                _G._MasterNear3DMonsters[pIdx] = nil
                self:_EnsureProxyVisual(info)
                return
            end
            self:_ClearProxyVisual()
            self._isProxyMode = false
            _G._MasterNear3DMonsters[pIdx] = self
            if origCreateGO then return origCreateGO(self) end
        end

        wmo.OnCreateGameObject = function(self, ...)
            if self._isProxyMode then
                local firstArg = select(1, ...)
                if not self.gameObject and firstArg and not IsNull(firstArg) then
                    if type(firstArg) == "table" and firstArg.gameObject and not IsNull(firstArg.gameObject) then
                        self.gameObject = firstArg.gameObject
                    elseif type(firstArg) == "table" and firstArg.Result and not IsNull(firstArg.Result) then
                        self.gameObject = firstArg.Result
                    elseif type(firstArg) == "userdata" or (type(firstArg) == "table" and (firstArg.SetActive or firstArg.GetComponentsInChildren)) then
                        self.gameObject = firstArg
                    end
                end
                if self.gameObject and not IsNull(self.gameObject) then
                    if self.GameObjectDestroy then
                        pcall(self.GameObjectDestroy, self, self.gameObject)
                    elseif CS and CS.UnityEngine and CS.UnityEngine.Object and CS.UnityEngine.Object.Destroy then
                        pcall(CS.UnityEngine.Object.Destroy, self.gameObject)
                    elseif self.gameObject.SetActive then
                        pcall(self.gameObject.SetActive, self.gameObject, false)
                    end
                end
                if self.instance and type(self.instance) == "table" and self.instance.Destroy then
                    pcall(self.instance.Destroy, self.instance)
                end
                self.gameObject = nil
                self.instance = nil
                self.model = nil
                self.anims = nil
                self.gpuAnims = nil
                self.cityLabels = nil
                if self.pointIndex and _G._MasterNear3DMonsters then
                    _G._MasterNear3DMonsters[self.pointIndex] = nil
                end
                return
            end
            local r = origOnCreateGO and origOnCreateGO(self, ...) or nil
            local target = (not IsNull(self.gameObject) and self.gameObject)
                or (not IsNull(self.model) and self.model)
            if target then
                optimizeInstance(target)
            end
            if self.RefreshLodType then
                self:RefreshLodType()
            end
            return r
        end

        wmo.UpdateGameObject = function(self, ...)
            local info = mgr and mgr.GetPointInfo and mgr:GetPointInfo(self.pointIndex)
            local vp = mgr and mgr.allViewPoints and self.pointIndex and mgr.allViewPoints[self.pointIndex]
            if type(vp) == "table" then
                vp._monsterCat = nil
                vp._parsedExtra = nil
            end
            if info then
                if info.monsterInfo then
                    self.monsterInfo = info.monsterInfo
                elseif info.extraInfo then
                    info._parsedExtra = nil
                    self.monsterInfo = nil
                end
            end
            if self._isProxyMode then
                self:_ApplyMonsterLodState(info)
                return
            end
            local r = origUpdateGO and origUpdateGO(self, ...) or nil
            self:_ApplyMonsterLodState(info)
            return r
        end

        wmo.Destroy = function(self, ...)
            self:_ClearProxyVisual()
            if self.pointIndex ~= nil then
                _G._MasterNear3DMonsters[self.pointIndex] = nil
                if _G._MasterProxyMonsterLabels then
                    _G._MasterProxyMonsterLabels[self.pointIndex] = nil
                end
                if _G._MasterProxyMonsters then
                    _G._MasterProxyMonsters[self.pointIndex] = nil
                end
            end
            self._isProxyMode = nil
            if origDestroy and (self.gameObject or self.instance) then
                return origDestroy(self, ...)
            end
            self.monsterInfo = nil
            self.model = nil
            if self.RemoveAllListeners then
                pcall(self.RemoveAllListeners, self)
            end
        end

        wmo.SetIsBattle = function(self, value, ...)
            if value == true and self._isProxyMode then
                self:_ClearProxyVisual()
                self._isProxyMode = false
                if self.pointIndex then _G._MasterNear3DMonsters[self.pointIndex] = self end
                if origCreateGO and not self.gameObject and not self.instance then
                    pcall(origCreateGO, self)
                end
            end
            if origSetIsBattle then
                return origSetIsBattle(self, value, ...)
            end
        end

        -- Skip expensive 3D skeletal animations on Zombies when proxied or zoomed out to 2D icons (lodLv >= 3)
        if origPlayAnim then
            wmo.PlayAnim = function(self, animName, ...)
                if self._isProxyMode or not self.gameObject then
                    return
                end
                local curLod = (mgr and mgr.lodLv) or 1
                if curLod >= 3 and animName == "idle" then
                    return
                end
                return origPlayAnim(self, animName, ...)
            end
        end

        wmo.__masterMonsterHooked = true
    end

    -- Preserve click-to-inspect/attack on GPU-instanced proxied monsters
    local ok_wim, wim = pcall(require, "Scene.WorldScene.SubModule.WorldInputManager")
    if ok_wim and wim and not wim.__masterClickHooked then
        wim.__masterClickHooked = true
        local _resolvedInClick = nil
        local _lastInputClickArg1 = nil
        local _lastInputClickArg2 = nil

        local function resolveProxyMonsterClick(posOrIdx)
            local curMgr = DataCenter and DataCenter.WorldPointManager
            if not curMgr or not curMgr.allViewPoints or posOrIdx == nil then return nil end
            local tileIndex = nil
            local posType = type(posOrIdx)
            if posType == "number" then
                tileIndex = posOrIdx
            elseif posType == "table" or posType == "userdata" then
                if posType == "table" and (posOrIdx.pointIndex or posOrIdx.tileIndex or posOrIdx.mainIndex) then
                    tileIndex = tonumber(posOrIdx.pointIndex or posOrIdx.tileIndex or posOrIdx.mainIndex)
                elseif SceneUtils and ForceChangeScene then
                    if SceneUtils.WorldToTileIndex then
                        local okTi, ti = pcall(SceneUtils.WorldToTileIndex, posOrIdx, ForceChangeScene.World)
                        if okTi and type(ti) == "number" and ti > 0 then
                            tileIndex = ti
                        end
                    end
                    if not tileIndex and SceneUtils.WorldToTileXZ and posOrIdx.x ~= nil then
                        local wz = (posOrIdx.z ~= nil) and posOrIdx.z or posOrIdx.y
                        if wz ~= nil then
                            local okXz, tx, ty = pcall(SceneUtils.WorldToTileXZ, posOrIdx.x, wz, ForceChangeScene.World)
                            if okXz and type(tx) == "number" and type(ty) == "number" and tx >= 0 and ty >= 0 then
                                tileIndex = ty * (TileCountX or 1000) + tx + 1
                            end
                        end
                    end
                end
            else
                return nil
            end
            if not tileIndex or tileIndex <= 0 then return nil end
            local vp = curMgr.allViewPoints[tileIndex]
            local mainIdx = (type(vp) == "table" and vp.mainIndex) or tileIndex
            local obj = curMgr.allObj and curMgr.allObj[mainIdx]
            if obj and obj._isProxyMode then
                return mainIdx, obj
            end
            return nil
        end

        local function resolveWorldClickPosFromWim(selfWim)
            if selfWim then
                local direct = selfWim.curClickPos or selfWim.clickPos or selfWim.touchWorldPos
                if direct ~= nil then return direct end
                if type(selfWim.GetClickWorldBulidingPos) == "function" then
                    local okBp, bp = pcall(selfWim.GetClickWorldBulidingPos, selfWim)
                    if okBp and bp ~= nil then return bp end
                end
                if type(selfWim.GetCurIndex) == "function" then
                    local okCi, ci = pcall(selfWim.GetCurIndex, selfWim)
                    if okCi and type(ci) == "number" and ci > 0 then return ci end
                end
            end
            if _lastInputClickArg1 ~= nil then
                if type(_lastInputClickArg1) == "number" then
                    return _lastInputClickArg1
                elseif (type(_lastInputClickArg1) == "table" or type(_lastInputClickArg1) == "userdata") and _lastInputClickArg1.z ~= nil and _lastInputClickArg1.z ~= 0 then
                    return _lastInputClickArg1
                end
            end
            local mainCam = CS and CS.UnityEngine and CS.UnityEngine.Camera and CS.UnityEngine.Camera.main
            local inp = CS and CS.UnityEngine and CS.UnityEngine.Input
            local screenPos = ((type(_lastInputClickArg1) == "table" or type(_lastInputClickArg1) == "userdata") and _lastInputClickArg1.x ~= nil and _lastInputClickArg1)
                or ((type(_lastInputClickArg2) == "table" or type(_lastInputClickArg2) == "userdata") and _lastInputClickArg2.x ~= nil and _lastInputClickArg2)
                or (inp and inp.mousePosition)
            if mainCam and not IsNull(mainCam) and screenPos and mainCam.ScreenPointToRay then
                local okRay, ray = pcall(mainCam.ScreenPointToRay, mainCam, screenPos)
                if okRay and ray and ray.origin and ray.direction and ray.direction.y ~= 0 then
                    local t = -ray.origin.y / ray.direction.y
                    if t > 0 then
                        return {
                            x = ray.origin.x + ray.direction.x * t,
                            y = 0,
                            z = ray.origin.z + ray.direction.z * t,
                        }
                    end
                end
            end
            return nil
        end

        local function invokeUIOnClickWorld(proxyIdx)
            if not proxyIdx or not _G.UIUtil or not _G.UIUtil.OnClickWorld then return false, nil end
            local fn = _G.UIUtil.OnClickWorld
            local firstParamName = (debug and debug.getlocal) and select(1, debug.getlocal(fn, 1)) or nil
            if firstParamName == "pointIndex" or firstParamName == "index" or firstParamName == "tileIndex" or firstParamName == "pos" or firstParamName == "pIdx" or firstParamName == "pointId" then
                return pcall(fn, proxyIdx)
            end
            return pcall(fn, _G.UIUtil, proxyIdx)
        end

        if type(wim.OnInputClick) == "function" then
            local origOnInputClick = wim._origOnInputClick or wim.OnInputClick
            wim._origOnInputClick = origOnInputClick
            wim.OnInputClick = function(self, a1, a2, a3, ...)
                _lastInputClickArg1 = a1
                _lastInputClickArg2 = a2
                local okIc, resIc = pcall(origOnInputClick, self, a1, a2, a3, ...)
                _lastInputClickArg1 = nil
                _lastInputClickArg2 = nil
                if not okIc then error(resIc) end
                return resIc
            end
        end

        if type(wim.GetInstancedBuildingClickIndex) == "function" then
            local origGetIdx = wim._origGetInstancedBuildingClickIndex or wim.GetInstancedBuildingClickIndex
            wim._origGetInstancedBuildingClickIndex = origGetIdx
            wim.GetInstancedBuildingClickIndex = function(self, posOrIdx, ...)
                local idx = origGetIdx(self, posOrIdx, ...)
                if idx ~= nil and idx ~= 0 then
                    return idx
                end
                local proxyIdx = resolveProxyMonsterClick(posOrIdx)
                if proxyIdx then
                    _resolvedInClick = proxyIdx
                    return proxyIdx
                end
                return idx
            end
        end

        if type(wim.ClickWorld) == "function" then
            local origClickWorld = wim._origClickWorld or wim.ClickWorld
            wim._origClickWorld = origClickWorld
            wim.ClickWorld = function(self, optTileIdx, ...)
                _resolvedInClick = nil
                local okCall, res = pcall(origClickWorld, self, optTileIdx, ...)
                local wasResolvedByGetIdx = (_resolvedInClick ~= nil)
                _resolvedInClick = nil
                if not okCall then
                    error(res)
                end
                if (res == nil or res == false) and not wasResolvedByGetIdx then
                    local clickTarget = optTileIdx
                    if clickTarget == nil then
                        clickTarget = resolveWorldClickPosFromWim(self)
                    end
                    local proxyIdx = resolveProxyMonsterClick(clickTarget)
                    if proxyIdx then
                        local okClick, clickRes = invokeUIOnClickWorld(proxyIdx)
                        if okClick and clickRes ~= nil then
                            return clickRes
                        end
                    end
                end
                return res
            end
        end
    end

    -- Tiered streaming and persistent cache (uses shared _G.ShouldBuildPointNow)
    local ShouldBuildPointNow = _G.ShouldBuildPointNow

    mgr.aoiOptimizeEnabled = true
    mgr.aoiReconcileEnabled = false
    mgr.outOfViewOffX = 100000

    -- Patch upvalues across ALL WorldPointManager inheritance levels (instance, WorldPointManager_SLG, AND superclass _vtbl!)
    local function patchFnUpvalues(fn)
        if type(fn) ~= "function" or not debug or not debug.getupvalue or not debug.setupvalue then return 0 end
        local patched = 0
        for uIdx = 1, 30 do
            local uName, uVal = debug.getupvalue(fn, uIdx)
            if not uName then break end
            if uName == "OtherPointLod" or uName == "SelfPointLod" or uName == "OtherPlayerLod" or uName == "NightSacrificeLod" or uName == "DesertPointLod" then
                debug.setupvalue(fn, uIdx, 20)
                patched = patched + 1
            elseif (uName == "ViewLevelRange" or uName == "ViewLevelRangeLandscape" or uName == "ViewLevelRange_Old") and type(uVal) == "table" then
                for k, v in pairs(uVal) do
                    if type(v) == "table" then
                        v.x = 100000
                        v.y = 100000
                    end
                end
                for lodIdx = 1, 12 do
                    if type(uVal[lodIdx]) ~= "table" then
                        uVal[lodIdx] = { x = 100000, y = 100000 }
                    else
                        uVal[lodIdx].x = 100000
                        uVal[lodIdx].y = 100000
                    end
                end
                patched = patched + 1
            end
        end
        return patched
    end

    local function patchWpmTableUpvalues(tbl)
        if type(tbl) ~= "table" then return 0 end
        local total = 0
        for _, fn in pairs(tbl) do
            if type(fn) == "function" then
                total = total + patchFnUpvalues(fn)
            end
        end
        return total
    end

    local vtblPatchedCount = 0
    vtblPatchedCount = vtblPatchedCount + patchWpmTableUpvalues(mgr)
    -- Direct method lookups (reaches superclass BaseClass _vtbl methods immediately)
    for _, keyName in ipairs({"BuildAsync", "GetViewLevelRange", "GetLodRequestRange", "Update", "UpdateViewRequest", "DoSendViewRequest", "SendViewRequest"}) do
        if type(mgr[keyName]) == "function" then
            vtblPatchedCount = vtblPatchedCount + patchFnUpvalues(mgr[keyName])
        end
    end
    -- Walk metatable & BaseClass _class[super] _vtbl chain so every inherited function is unlocked
    local curTbl = mgr
    local visited = {}
    for _ = 1, 6 do
        if not curTbl or visited[curTbl] then break end
        visited[curTbl] = true
        local mt = getmetatable(curTbl)
        local idx = mt and mt.__index
        if type(idx) == "table" then
            vtblPatchedCount = vtblPatchedCount + patchWpmTableUpvalues(idx)
            curTbl = idx
        elseif type(idx) == "function" and debug and debug.getupvalue then
            local clsMap, sup = nil, nil
            for u = 1, 8 do
                local un, uv = debug.getupvalue(idx, u)
                if not un then break end
                if un == "_class" and type(uv) == "table" then clsMap = uv end
                if un == "super" and type(uv) == "table" then sup = uv end
            end
            while clsMap and sup and not visited[sup] do
                visited[sup] = true
                local vtbl = clsMap[sup]
                if type(vtbl) == "table" then
                    vtblPatchedCount = vtblPatchedCount + patchWpmTableUpvalues(vtbl)
                end
                sup = sup.super
            end
            break
        else
            break
        end
    end
    _G._MasterVtblPatchedCount = vtblPatchedCount

    local _HUGE_RANGE_CELL = { x = 100000, y = 100000 }
    local _HUGE_VIEW_RANGE_TABLE = {}
    for lodIdx = 1, 20 do
        _HUGE_VIEW_RANGE_TABLE[lodIdx] = _HUGE_RANGE_CELL
    end
    setmetatable(_HUGE_VIEW_RANGE_TABLE, {
        __index = function(_, key)
            if type(key) == "number" then
                return _HUGE_RANGE_CELL
            end
            return nil
        end
    })

    local _DEFAULT_REQ_RANGE_CELL = { x = 24, y = 28 }
    local _SAFE_LOD_REQUEST_RANGE = {}
    for lodIdx = 1, 20 do
        _SAFE_LOD_REQUEST_RANGE[lodIdx] = _DEFAULT_REQ_RANGE_CELL
    end
    setmetatable(_SAFE_LOD_REQUEST_RANGE, {
        __index = function(_, key)
            if type(key) == "number" then
                return _DEFAULT_REQ_RANGE_CELL
            end
            return nil
        end
    })

    if not mgr._origGetViewLevelRange and mgr.GetViewLevelRange then mgr._origGetViewLevelRange = mgr.GetViewLevelRange end
    if not mgr._origGetLodRequestRange and mgr.GetLodRequestRange then mgr._origGetLodRequestRange = mgr.GetLodRequestRange end
    mgr.GetViewLevelRange = function(self, ...)
        if _G._MasterToggles and _G._MasterToggles.masterEnabled == false and self._origGetViewLevelRange then
            local okOrig, orig = pcall(self._origGetViewLevelRange, self, ...)
            if okOrig and type(orig) == "table" and type(orig[1]) == "table" then
                return orig
            end
        end
        return _HUGE_VIEW_RANGE_TABLE
    end
    mgr.GetLodRequestRange = function(self, ...)
        if self._origGetLodRequestRange then
            local okOrig, orig = pcall(self._origGetLodRequestRange, self, ...)
            if okOrig and type(orig) == "table" and type(orig[1]) == "table" then
                local rx = tonumber(orig[1].x)
                local ry = tonumber(orig[1].y)
                if rx and ry and rx > 0 and rx <= 500 and ry > 0 and ry <= 500 then
                    for lodIdx = 1, 12 do
                        if type(orig[lodIdx]) ~= "table" then
                            orig[lodIdx] = orig[1]
                        end
                    end
                    return orig
                end
            end
        end
        return _SAFE_LOD_REQUEST_RANGE
    end

    mgr.GetViewBounds = function(self, padX, padY)
        return -100000, 100000, -100000, 100000
    end
    mgr.IsOutOfRange = function(self, ...)
        return false
    end
    local _oorFrame = -1
    local _oorCamX, _oorCamY = 500, 500
    mgr.IsOutOfRange2 = function(self, x, y, minX, maxX, minY, maxY)
        if x and y then
            local tw = TileCountX or 1000
            local pIdx = y * tw + x + 1
            local entry = self.allViewPoints and self.allViewPoints[pIdx]
            if entry then
                local f = CS and CS.UnityEngine and CS.UnityEngine.Time and CS.UnityEngine.Time.frameCount or -2
                if f ~= _oorFrame then
                    _oorFrame = f
                    _oorCamX, _oorCamY = GetActualCameraTilePos(self, SceneManager and SceneManager.World)
                end
                return not ShouldBuildPointNow(self, pIdx, entry, _oorCamX, _oorCamY, false)
            end
        end
        return false
    end

    -- Zoomed out (lod >= 3): request svLod = 1 (71x101 box, 3.7x area, 100% HQs/Zombies/Resources/Cities/Radar)
    -- Zoomed in (lod <= 2): request svLod = 0 (48x41 box, includes small seasonal decor tiles)
    mgr.GetServerLod = function(self, lod)
        if type(lod) == "number" and lod >= 3 then
            return 1
        end
        return 0
    end

    -- Never skip unbuilt points/deserts during continuous AOI version checks
    mgr.SkipWorldPointForContinuesAoiVersion = function(self, pointId)
        if not self.aoiOptimizeEnabled then return false end
        local pi = self:GetPointInfo(pointId)
        local obj = self:GetObjectByPoint(pointId)
        if pi ~= nil and obj ~= nil then
            return true
        end
        return false
    end
    mgr.SkipDesertForContinuesAoiVersion = function(self, pointId)
        if not self.aoiOptimizeEnabled then return false end
        local entry = self.allViewPoints and self.allViewPoints[pointId]
        local obj = self:GetObjectByPoint(pointId)
        if entry and entry.desertInfo ~= nil and obj ~= nil then
            return true
        end
        return false
    end

    -- High-throughput zero-stutter frame budgets using os.clock() wall-clock deltas (DoParse <= 2.5ms, BuildAsync <= 3.5ms)
    local _parseFrame = -1
    local _parseCount = 0
    local _parseStartClock = 0
    local _PARSE_BUDGET_SEC = 0.0025
    mgr.IsBusy = function(self)
        local timeApi = CS and CS.UnityEngine and CS.UnityEngine.Time
        local f = timeApi and timeApi.frameCount or 0
        local nowClk = os.clock()
        if f ~= _parseFrame then
            _parseFrame = f
            _parseCount = 0
            _parseStartClock = nowClk
        end
        _parseCount = _parseCount + 1
        if _parseCount <= 4 then
            return false
        end
        local dt = nowClk - _parseStartClock
        if dt < 0 then
            _parseStartClock = nowClk
            dt = 0
        end
        if dt >= _PARSE_BUDGET_SEC then
            return true
        end
        return _parseCount > 90
    end

    local _buildFrame = -1
    local _buildCount = 0
    local _buildStartClock = 0
    local _BUILD_BUDGET_SEC = 0.0035
    mgr.IsSyncBusy = function(self)
        local timeApi = CS and CS.UnityEngine and CS.UnityEngine.Time
        local f = timeApi and timeApi.frameCount or 0
        local nowClk = os.clock()
        if f ~= _buildFrame then
            _buildFrame = f
            _buildCount = 0
            _buildStartClock = nowClk
        end
        _buildCount = _buildCount + 1
        if _buildCount <= 4 then
            return false
        end
        local dt = nowClk - _buildStartClock
        if dt < 0 then
            _buildStartClock = nowClk
            dt = 0
        end
        if dt >= _BUILD_BUDGET_SEC then
            return true
        end
        return _buildCount > 250
    end

    mgr.ReconcileAoiPoints = function(self, newIdSet, newCount)
        if not self.aoiPointIdSet then self.aoiPointIdSet = newIdSet or {}
        else for k in pairs(newIdSet or {}) do self.aoiPointIdSet[k] = true end end
    end
    mgr.ReconcileAoiDeserts = function(self, newIdSet, newCount)
        if not self.aoiDesertIdSet then self.aoiDesertIdSet = newIdSet or {}
        else for k in pairs(newIdSet or {}) do self.aoiDesertIdSet[k] = true end end
    end

    local function _clearAllProxyRenderers(targetMgr)
        if _MonsterFallbackBatch and _MonsterFallbackBatch.Clear then
            _MonsterFallbackBatch.Clear()
        end
        _G._MasterNear3DMonsters = {}
        _G._MasterProxyMonsterLabels = {}
        _G._MasterProxyMonsters = {}
        if not targetMgr then return end
        if targetMgr.GetIconRenderer then
            local okIr, ir = pcall(targetMgr.GetIconRenderer, targetMgr)
            if okIr and ir and ir.Clear then
                pcall(ir.Clear, ir)
            end
        end
        if targetMgr.GetLabelRenderer then
            local okLr, lr = pcall(targetMgr.GetLabelRenderer, targetMgr)
            if okLr and lr and lr.Clear then
                pcall(lr.Clear, lr)
            end
        end
    end

    -- Persistent Cache Lifecycle Hooks (Per-server cache; never wipe viewpoints across scene switches)
    local mt = getmetatable(mgr)
    local proto = (mt and type(mt.__index) == "table") and mt.__index or mgr
    if proto and not proto._masterCacheLifecycleHookedV82 then
        proto._masterCacheLifecycleHookedV82 = true
        proto._masterCacheLifecycleHookedV81 = true
        proto._masterCacheLifecycleHookedV8 = true
        proto._masterCacheLifecycleHooked = true

        local origClose = proto._origCloseV8 or proto.Close
        proto._origCloseV8 = origClose
        proto.Close = function(self, ...)
            local sid = ResolveCacheServerId(nil, self)
            local ptCache, desertCache = GetServerCacheTables(sid, self)
            if self.allViewPoints then
                for k, v in pairs(self.allViewPoints) do
                    if type(v) == "table" then
                        if v.pointInfo ~= nil and ptCache[k] ~= v.pointInfo then
                            ptCache[k] = v.pointInfo
                            MarkWorldCacheDirty(sid, 1)
                        end
                        if v.desertInfo ~= nil and desertCache[k] ~= v.desertInfo then
                            desertCache[k] = v.desertInfo
                            MarkWorldCacheDirty(sid, 1)
                        end
                    end
                end
            end
            _G.SaveWorldCacheToDisk(sid, true)
            _clearAllProxyRenderers(self)
            local ret = nil
            if origClose then
                ret = origClose(self, ...)
            end
            _G._MasterSpatialGrid = {}
            _G._MasterDirtyBuckets = {}
            _G._MasterViewPointCount = 0
            _G._MasterGridTableRef = nil
            _G._MasterObjCount = 0
            _G._MasterAllObjRef = nil
            _G._MasterProxyMonsters = {}
            _G._MasterStreamReset = true
            return ret
        end

        local origCreateObject = proto._origCreateObjectV8 or proto.CreateObject
        proto._origCreateObjectV8 = origCreateObject
        if origCreateObject then
            proto.CreateObject = function(self, pointIndex, ...)
                _syncMasterObjCount(self)
                local had = (self.allObj ~= nil and pointIndex ~= nil and self.allObj[pointIndex] ~= nil)
                local ret = origCreateObject(self, pointIndex, ...)
                if not had and self.allObj ~= nil and pointIndex ~= nil and self.allObj[pointIndex] ~= nil then
                    _G._MasterObjCount = (_G._MasterObjCount or 0) + 1
                end
                return ret
            end
        end

        local origDestroyObject = proto._origDestroyObjectV8 or proto.DestroyObject
        proto._origDestroyObjectV8 = origDestroyObject
        if origDestroyObject then
            proto.DestroyObject = function(self, pointIndex, ...)
                _syncMasterObjCount(self)
                local prevObj = (self.allObj ~= nil and pointIndex ~= nil) and self.allObj[pointIndex] or nil
                if prevObj and prevObj._ClearProxyVisual then
                    pcall(prevObj._ClearProxyVisual, prevObj)
                end
                if pointIndex ~= nil and _G._MasterNear3DMonsters then
                    _G._MasterNear3DMonsters[pointIndex] = nil
                end
                if pointIndex ~= nil and _G._MasterProxyMonsterLabels then
                    _G._MasterProxyMonsterLabels[pointIndex] = nil
                end
                if pointIndex ~= nil and _G._MasterProxyMonsters then
                    _G._MasterProxyMonsters[pointIndex] = nil
                end
                local ret = origDestroyObject(self, pointIndex, ...)
                if prevObj ~= nil and (self.allObj == nil or self.allObj[pointIndex] == nil) then
                    _G._MasterObjCount = math.max(0, (_G._MasterObjCount or 1) - 1)
                end
                return ret
            end
        end

        local origStartUp = proto._origStartUpV8 or proto.StartUp
        proto._origStartUpV8 = origStartUp
        proto.StartUp = function(self, ...)
            local res = origStartUp and origStartUp(self, ...) or nil
            SyncSpatialGridIfReplaced(self)
            pcall(_G.RestoreWorldMapCache, ResolveCacheServerId(nil, self))
            _G._ForceStreamRescan = true
            return res
        end

        local origAddPointInfo = proto._origAddPointInfoV8 or proto.AddPointInfo
        proto._origAddPointInfoV8 = origAddPointInfo
        if origAddPointInfo then
            proto.AddPointInfo = function(self, arg1, arg2, ...)
                local pKey, pInfo
                if type(arg1) == "table" and arg2 == nil then
                    pInfo = arg1
                    pKey = tonumber(arg1.id or arg1.pointIndex or arg1.mainIndex)
                else
                    pKey = arg1
                    pInfo = arg2
                end
                local sid = ResolveCacheServerId(nil, self)
                if pKey and pInfo then
                    local ptCache = GetServerCacheTables(sid, self)
                    if ptCache[pKey] ~= pInfo then
                        ptCache[pKey] = pInfo
                        MarkWorldCacheDirty(sid, 1)
                    end
                    if self.allViewPoints and not self.allViewPoints[pKey] then
                        self.allViewPoints[pKey] = { pointIndex = pKey, pointInfo = pInfo }
                    elseif self.allViewPoints and type(self.allViewPoints[pKey]) == "table" then
                        self.allViewPoints[pKey]._monsterCat = nil
                        self.allViewPoints[pKey]._parsedExtra = nil
                    end
                end
                local ret = origAddPointInfo(self, arg1, arg2, ...)
                if pKey and self.allViewPoints and self.allViewPoints[pKey] then
                    self.allViewPoints[pKey]._monsterCat = nil
                    self.allViewPoints[pKey]._parsedExtra = nil
                    IndexViewPoint(self, pKey, self.allViewPoints[pKey], true)
                end
                return ret
            end
        end

        local origAddDesertInfo = proto._origAddDesertInfoV8 or proto.AddDesertInfo
        proto._origAddDesertInfoV8 = origAddDesertInfo
        if origAddDesertInfo then
            proto.AddDesertInfo = function(self, arg1, arg2, ...)
                local dKey, dInfo
                if type(arg1) == "table" and arg2 == nil then
                    dInfo = arg1
                    dKey = tonumber(arg1.id or arg1.pointIndex or arg1.mainIndex)
                else
                    dKey = arg1
                    dInfo = arg2
                end
                local sid = ResolveCacheServerId(nil, self)
                if dKey and dInfo then
                    local _, desertCache = GetServerCacheTables(sid, self)
                    if desertCache[dKey] ~= dInfo then
                        desertCache[dKey] = dInfo
                        MarkWorldCacheDirty(sid, 1)
                    end
                    if self.allViewPoints and not self.allViewPoints[dKey] then
                        self.allViewPoints[dKey] = { pointIndex = dKey, desertInfo = dInfo }
                    end
                end
                local ret = origAddDesertInfo(self, arg1, arg2, ...)
                if dKey and self.allViewPoints and self.allViewPoints[dKey] then
                    IndexViewPoint(self, dKey, self.allViewPoints[dKey], true)
                end
                return ret
            end
        end
    end

    -- Full Map Preloader: Disable out-of-view zone and object purging so the entire map stays loaded
    if not mgr._origAddToDeleteList and mgr.AddToDeleteList then mgr._origAddToDeleteList = mgr.AddToDeleteList end
    if not mgr._origDeleteOutOfView and mgr.DeleteOutOfView then mgr._origDeleteOutOfView = mgr.DeleteOutOfView end
    if not mgr._origCalcOutOfViewZones and mgr.CalcOutOfViewZones then mgr._origCalcOutOfViewZones = mgr.CalcOutOfViewZones end
    if not mgr._origForceDeletePoint and mgr.ForceDeletePoint then mgr._origForceDeletePoint = mgr.ForceDeletePoint end
    if not mgr._origRemovePointInfo and mgr.RemovePointInfo then mgr._origRemovePointInfo = mgr.RemovePointInfo end

    -- Keep all offscreen objects loaded across the entire world map
    mgr.AddToDeleteList = function(self, index) end
    mgr.DeleteOutOfView = function(self) end
    mgr.CalcOutOfViewZones = function(self) end

    -- Only allow real server removals (when an entity actually dies or despawns, not out-of-view culling)
    local origRemovePointInfo = mgr._origRemovePointInfo
    if origRemovePointInfo then
        mgr.RemovePointInfo = function(self, pointIndex, forceRemove, isOutOfView)
            if forceRemove == true and isOutOfView ~= true then
                local prevEntry = self.allViewPoints and self.allViewPoints[pointIndex]
                local prevObj = self.allObj and pointIndex ~= nil and self.allObj[pointIndex] or nil
                if prevObj and prevObj._ClearProxyVisual then
                    pcall(prevObj._ClearProxyVisual, prevObj)
                end
                if pointIndex ~= nil and _G._MasterNear3DMonsters then
                    _G._MasterNear3DMonsters[pointIndex] = nil
                end
                if pointIndex ~= nil and _G._MasterProxyMonsterLabels then
                    _G._MasterProxyMonsterLabels[pointIndex] = nil
                end
                if pointIndex ~= nil and _G._MasterProxyMonsters then
                    _G._MasterProxyMonsters[pointIndex] = nil
                end
                local cntBefore = _G._MasterObjCount or 0
                local ret = origRemovePointInfo(self, pointIndex, true, false)
                if prevObj ~= nil and (self.allObj == nil or self.allObj[pointIndex] == nil) and (_G._MasterObjCount or 0) == cntBefore then
                    _G._MasterObjCount = math.max(0, cntBefore - 1)
                end
                UnindexViewPoint(pointIndex, prevEntry)
                local sid = ResolveCacheServerId(nil, self)
                local ptCache, desertCache = GetServerCacheTables(sid, self)
                if pointIndex ~= nil then
                    if ptCache then ptCache[pointIndex] = nil end
                    if desertCache then desertCache[pointIndex] = nil end
                    local numKey = tonumber(pointIndex)
                    if numKey ~= nil then
                        if ptCache then ptCache[numKey] = nil end
                        if desertCache then desertCache[numKey] = nil end
                    end
                end
                MarkWorldCacheDirty(sid, 1)
                return ret
            end
        end
    end

    if type(mgr.OnLodChanged) == "function" then
        local origOnLodChanged = mgr._origOnLodChangedV8 or mgr.OnLodChanged
        mgr._origOnLodChangedV8 = origOnLodChanged
        mgr.OnLodChanged = function(self, lod, ...)
            local r = origOnLodChanged(self, lod, ...)
            _G._MasterLodDirty = true
            _G._MasterReconcilePass = nil
            local startClk = os.clock()
            local budgetHit = false
            if type(lod) == "number" and lod >= 3 and _G._MasterNear3DMonsters then
                local countDemoted = 0
                for pIdx, mObj in pairs(_G._MasterNear3DMonsters) do
                    if mObj and mObj._ApplyMonsterLodState then
                        local info = self.GetPointInfo and self:GetPointInfo(pIdx)
                        pcall(mObj._ApplyMonsterLodState, mObj, info)
                    else
                        _G._MasterNear3DMonsters[pIdx] = nil
                    end
                    countDemoted = countDemoted + 1
                    if (countDemoted % 8 == 0) and (os.clock() - startClk) >= 0.0020 then
                        budgetHit = true
                        break
                    end
                end
            end
            if (not budgetHit) and type(lod) == "number" and lod >= 5 and _G._MasterProxyMonsterLabels then
                local lr = self.GetLabelRenderer and self:GetLabelRenderer()
                local countLbl = 0
                for pIdx, mObj in pairs(_G._MasterProxyMonsterLabels) do
                    if mObj and mObj._proxyLabelHandle ~= nil then
                        if lr and lr.RemoveLabel then
                            pcall(lr.RemoveLabel, lr, mObj._proxyLabelHandle)
                        end
                        mObj._proxyLabelHandle = nil
                        mObj._proxyLabelLv = nil
                    end
                    _G._MasterProxyMonsterLabels[pIdx] = nil
                    countLbl = countLbl + 1
                    if (countLbl % 16 == 0) and (os.clock() - startClk) >= 0.0020 then
                        break
                    end
                end
            elseif (not budgetHit) and type(lod) == "number" and lod <= 4 and _G._MasterProxyMonsters and next(_G._MasterProxyMonsters) ~= nil then
                local toggles = _G._MasterToggles
                local needCam = (lod <= 2) or (toggles ~= nil and toggles.masterEnabled == false)
                local camX, camY = 500, 500
                if needCam then
                    camX, camY = GetActualCameraTilePos(self, SceneManager and SceneManager.World)
                end
                local allObj = self.allObj
                local countRestored = 0
                for pIdx, mObj in pairs(_G._MasterProxyMonsters) do
                    if mObj and mObj._isProxyMode and mObj._proxyLabelHandle == nil and mObj._EnsureProxyVisual then
                        if allObj and allObj[pIdx] ~= mObj then
                            _G._MasterProxyMonsters[pIdx] = nil
                        else
                            local allowed = true
                            if needCam then
                                local px = mObj._cachedTileX
                                local py = mObj._cachedTileY
                                if not px or not py then
                                    px, py = FastIndexToXY(pIdx)
                                    mObj._cachedTileX = px
                                    mObj._cachedTileY = py
                                end
                                local dist = math.max(math.abs(px - camX), math.abs(py - camY))
                                if lod <= 2 and (dist <= MONSTER_NEAR_3D_RADIUS or mObj.isInBattle == true) then
                                    allowed = false
                                elseif toggles and toggles.masterEnabled == false and dist > 48 then
                                    allowed = false
                                end
                            end
                            local vp = allowed and self.allViewPoints and self.allViewPoints[pIdx] or nil
                            local info = allowed and ((vp and vp.pointInfo) or (self.GetPointInfo and self:GetPointInfo(pIdx))) or nil
                            if allowed and toggles then
                                local cat = GetMonsterCategory({ pointInfo = info, _parsedExtra = mObj.monsterInfo })
                                if (cat == "BOOMER" or cat == "BOSS") and toggles.showBoomers == false then
                                    allowed = false
                                elseif cat == "ZOMBIE" and toggles.showZombies == false then
                                    allowed = false
                                end
                            end
                            if allowed then
                                pcall(mObj._EnsureProxyVisual, mObj, info)
                            end
                        end
                    end
                    countRestored = countRestored + 1
                    if (countRestored % 16 == 0) and (os.clock() - startClk) >= 0.0020 then
                        break
                    end
                end
            end
            return r
        end
    end

    -- Sanitize mgr.lodLv to integer
    if type(mgr.lodLv) ~= "number" then
        mgr.lodLv = 4
    end

    -- Polyfill SceneManager.World fallbacks so City/World transitions never throw nil method errors
    local curWs = SceneManager and SceneManager.World
    if curWs then
        if not curWs.GetLodLevel then
            curWs.GetLodLevel = function(self)
                return (type(mgr.lodLv) == "number" and mgr.lodLv) or 4
            end
        end
        if not curWs.GetStaticMgr then
            local dummy = { AddOccupyPoints2Queued = function() end }
            curWs.GetStaticMgr = function(self) return dummy end
        end
    end

    -- Safe guard WorldHeroDispatchTaskObject against destroyed GameObject when preloading in City view
    local ok_whd, whd = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldHeroDispatchTaskObject")
    if ok_whd and whd and not whd._masterNullGuarded then
        whd._masterNullGuarded = true
        local origUpdateReward = whd.UpdateShowRewardUI
        if type(origUpdateReward) == "function" then
            whd.UpdateShowRewardUI = function(self, ...)
                if not self or not self.gameObject or IsNull(self.gameObject) then return end
                return origUpdateReward(self, ...)
            end
        end
    end

    -- Safe guard mgr.AddOccupyPoints2Queued against uninitialized World static manager
    if mgr and mgr.AddOccupyPoints2Queued and not mgr._masterAddOccupyGuarded then
        mgr._masterAddOccupyGuarded = true
        local origAddOccupy = mgr.AddOccupyPoints2Queued
        mgr.AddOccupyPoints2Queued = function(self, tilePos, radius, points, iscity)
            local wScene = SceneManager and SceneManager.World
            if wScene and wScene.GetStaticMgr then
                local ok, smObj = pcall(wScene.GetStaticMgr, wScene)
                if ok and smObj and smObj.AddOccupyPoints2Queued then
                    return pcall(smObj.AddOccupyPoints2Queued, smObj, tilePos, radius, points, iscity)
                end
            end
        end
    end

    -- Ensure on_LodChanged is registered on ChangeCameraLod without wiping existing game listeners
    if EventManager and EventId and EventId.ChangeCameraLod and mgr.on_LodChanged then
        local em = EventManager:GetInstance()
        if em then
            pcall(em.AddListener, em, EventId.ChangeCameraLod, mgr.on_LodChanged, mgr)
        end
    end

    -- Restore all cached viewpoints from persistent memory/disk and sync spatial buckets
    pcall(_G.RestoreWorldMapCache)
    if mgr.allViewPoints then
        local sidSync = ResolveCacheServerId(nil, mgr)
        local ptSync, desSync = GetServerCacheTables(sidSync, mgr)
        for k, v in pairs(mgr.allViewPoints) do
            if type(v) == "table" then
                if v.pointInfo ~= nil and ptSync[k] ~= v.pointInfo then
                    ptSync[k] = v.pointInfo
                    MarkWorldCacheDirty(sidSync, 1)
                end
                if v.desertInfo ~= nil and desSync[k] ~= v.desertInfo then
                    desSync[k] = v.desertInfo
                    MarkWorldCacheDirty(sidSync, 1)
                end
            end
        end
        RebuildSpatialGrid(mgr)
    else
        SyncSpatialGridIfReplaced(mgr)
    end

    -- Preload and stream all spatial buckets on world entry (viewport-first concentric rings, deduplicated by mainIndex)
    local initCamX, initCamY = GetActualCameraTilePos(mgr, ws)
    if mgr.isInit == true and mgr.allViewPoints and mgr.AddToBuildList then
        -- Reset any stale duplicate sub-tile queue entries before clean deduplicated viewport-first streaming
        if type(mgr.toBuildList) == "table" and #mgr.toBuildList > 2000 then
            mgr.toBuildList = {}
            mgr.toBuildListHead = 1
            mgr.toBuildSet = {}
        end
        local grid = _G._MasterSpatialGrid
        local camBx = math.floor(initCamX / BUCKET_SIZE)
        local camBy = math.floor(initCamY / BUCKET_SIZE)
        local minBx = math.max(0, math.floor((initCamX - 300) / BUCKET_SIZE))
        local maxBx = math.min(20, math.floor((initCamX + 300) / BUCKET_SIZE))
        local minBy = math.max(0, math.floor((initCamY - 300) / BUCKET_SIZE))
        local maxBy = math.min(20, math.floor((initCamY + 300) / BUCKET_SIZE))
        local ordered = {}
        for bx = minBx, maxBx do
            for by = minBy, maxBy do
                local bKey = by * 4096 + bx
                if grid and grid[bKey] then
                    local dx = bx - camBx
                    local dy = by - camBy
                    ordered[#ordered + 1] = { key = bKey, d2 = dx * dx + dy * dy }
                end
            end
        end
        table.sort(ordered, function(a, b) return a.d2 < b.d2 end)
        for i = 1, #ordered do
            local bucket = grid[ordered[i].key]
            if bucket then
                for k, v in pairs(bucket) do
                    if type(v) == "table" and (v.mainIndex == nil or v.mainIndex == k) and (v.pointInfo ~= nil or v.desertInfo ~= nil) then
                        if not (mgr.allObj and mgr.allObj[k]) and not (mgr.toBuildSet and mgr.toBuildSet[k]) then
                            if ShouldBuildPointNow(mgr, k, v, initCamX, initCamY, false) then
                                mgr:AddToBuildList(k)
                            end
                        end
                    end
                end
            end
        end
    end

    if not (mgr and mgr.isInit == true) then
        mgr._masterAppliedForThisWorldSession = false
        return "HOOKS_READY_WAITING_FOR_WORLD_VIEW"
    end

    _syncMasterObjCount(mgr)

    -- Camera streamer: remove any legacy per-frame AfterUpdate hook that caused frame lag or moved transforms
    if ws and ws.Camera then
        local afterTbl = ws.Camera.AfterUpdate or ws.Camera.AfterUpdateAction
        if type(afterTbl) == "table" then
            afterTbl["Proximity3DGate"] = nil
        end
    end

    local function _applyToggleEntry(curMgr, k, obj, camX, camY)
        if not obj then return end
        local vp = curMgr.allViewPoints and curMgr.allViewPoints[k]
        local cname = (obj._class_type and obj._class_type.__cname) or ""
        if obj._ApplyMonsterLodState then
            local info = (vp and vp.pointInfo) or (curMgr.GetPointInfo and curMgr:GetPointInfo(obj.pointIndex))
            pcall(obj._ApplyMonsterLodState, obj, info)
        elseif cname == "WorldResObjectInstanced" and obj._ApplyInstancedLodState then
            local info = (vp and vp.pointInfo) or (curMgr.GetPointInfo and curMgr:GetPointInfo(obj.pointIndex))
            if info then pcall(obj._ApplyInstancedLodState, obj, info, false) end
        elseif obj.gameObject and not IsNull(obj.gameObject) then
            local shouldShow = (vp ~= nil) and _G.ShouldBuildPointNow(curMgr, k, vp, camX, camY, false) or true
            if obj.gameObject.activeSelf ~= shouldShow then
                obj.gameObject:SetActive(shouldShow)
            end
        end
    end

    _G.ApplyToggleChangeImmediate = function()
        local tok = (_G._MasterToggleSweepToken or 0) + 1
        _G._MasterToggleSweepToken = tok
        local curMgr = DataCenter and DataCenter.WorldPointManager
        local curWs = SceneManager and SceneManager.World
        if curMgr and curMgr.isInit == true and curMgr.allObj then
            local camX, camY = GetActualCameraTilePos(curMgr, curWs)
            local objTbl = curMgr.allObj
            local nextK, nextV = next(objTbl, nil)
            local function _toggleSlice()
                if _G._MasterToggleSweepToken ~= tok then return end
                if DataCenter and DataCenter.WorldPointManager ~= curMgr or curMgr.isInit ~= true then return end
                local startClk = os.clock()
                local processed = 0
                while nextK ~= nil do
                    local curK, curObj = nextK, nextV
                    local okN, nk, nv = pcall(next, objTbl, curK)
                    if okN then
                        nextK, nextV = nk, nv
                    else
                        nextK, nextV = nil, nil
                    end
                    _applyToggleEntry(curMgr, curK, curObj, camX, camY)
                    processed = processed + 1
                    if nextK ~= nil and (processed % 16 == 0) and (os.clock() - startClk) >= 0.0025 then
                        local tm = TimerManager and TimerManager:GetInstance()
                        if tm and tm.DelayInvoke then
                            tm:DelayInvoke(_toggleSlice, 0.02)
                            return
                        end
                    end
                end
            end
            pcall(_toggleSlice)
        end
        _G._ForceStreamRescan = true
        pcall(_G.RefreshMasterOverlayUI)
    end

    -- Time-sliced dead-GO sweep and existing object refresh (0.0025s os.clock() budget/tick)
    if mgr.allObj then
        local sweepTok = (_G._MasterRefreshSweepToken or 0) + 1
        _G._MasterRefreshSweepToken = sweepTok
        local objTbl = mgr.allObj
        local nowSec = os.time()
        local nextK, nextV = next(objTbl, nil)
        local function _refreshSlice()
            if _G._MasterRefreshSweepToken ~= sweepTok then return end
            local startClk = os.clock()
            local processed = 0
            while nextK ~= nil do
                local curK, curObj = nextK, nextV
                local okN, nk, nv = pcall(next, objTbl, curK)
                if okN then
                    nextK, nextV = nk, nv
                else
                    nextK, nextV = nil, nil
                end
                local cname = curObj and ((curObj._class_type and curObj._class_type.__cname) or "") or ""
                local isInstancedObj = curObj and (curObj._ApplyInstancedLodState ~= nil or string.find(cname, "Instanced", 1, true) ~= nil)
                local hasAsyncPending = curObj and (curObj.instance ~= nil)
                if not curObj or (not curObj._isProxyMode and not isInstancedObj and not hasAsyncPending and (not curObj.gameObject or IsNull(curObj.gameObject))) then
                    objTbl[curK] = nil
                    if _G._MasterNear3DMonsters then _G._MasterNear3DMonsters[curK] = nil end
                    if _G._MasterProxyMonsterLabels then _G._MasterProxyMonsterLabels[curK] = nil end
                    if _G._MasterProxyMonsters then _G._MasterProxyMonsters[curK] = nil end
                    _G._MasterObjCount = math.max(0, (_G._MasterObjCount or 1) - 1)
                else
                    if curObj.adjuster and not IsNull(curObj.adjuster) then
                        expandAdjuster(curObj.adjuster)
                    end
                    local info = mgr.GetPointInfo and mgr:GetPointInfo(curObj.pointIndex)
                    if cname == "WorldBuildObject" and info then
                        if curObj.SetBuildIconColor then pcall(curObj.SetBuildIconColor, curObj, info) end
                        local bi = info.buildInfo
                        if bi and bi.protectEndTime and (bi.protectEndTime > nowSec) and curObj.SetProtectRenderVisible then
                            pcall(curObj.SetProtectRenderVisible, curObj, true)
                        end
                    elseif cname == "WorldMonsterObject" then
                        if curObj._ApplyMonsterLodState then
                            pcall(curObj._ApplyMonsterLodState, curObj, info)
                        elseif curObj.RefreshLodType then
                            pcall(curObj.RefreshLodType, curObj)
                        end
                    elseif cname == "WorldResObjectInstanced" and info then
                        curObj._ApplyInstancedLodState = applySmartInstancedLodState
                        pcall(curObj._ApplyInstancedLodState, curObj, info, false)
                    end
                end
                processed = processed + 1
                if nextK ~= nil and (processed % 16 == 0) and (os.clock() - startClk) >= 0.0025 then
                    local tm = TimerManager and TimerManager:GetInstance()
                    if tm and tm.DelayInvoke then
                        tm:DelayInvoke(_refreshSlice, 0.02)
                        return
                    end
                end
            end
        end
        pcall(_refreshSlice)
    end

    -- Ensure background preloader is continuously sweeping and parsing world data
    if _G.StartBackgroundWorldPreloader then
        pcall(_G.StartBackgroundWorldPreloader, false)
    end

    mgr._masterAppliedForThisWorldSession = true
    _G._ForceStreamRescan = true
    pcall(_G.RefreshMasterOverlayUI)

    local totalPts = _G._MasterViewPointCount or 0
    local totalObjs = tonumber(_G._MasterObjCount or 0) or 0

    return string.format(
        "SUCCESS_MASTER_V8_0_FULL_MAP_LOAD (server=%d, vtblPatched=%d, cachedPoints=%d, activeObj=%d)",
        GetActiveWorldServerId(mgr),
        tonumber(_G._MasterVtblPatchedCount or 0) or 0,
        totalPts,
        totalObjs
    )
end


function _G.StartBackgroundWorldPreloader(forceRestart)
    local mgr = DataCenter and DataCenter.WorldPointManager
    if not mgr or not TimerManager or not LuaEntry or not LuaEntry.Player then return false end
    local serverId = GetActiveWorldServerId(mgr)
    if not serverId or serverId <= 0 then return false end

    if mgr._bgSweepActive and not forceRestart and mgr._bgSweepServerId == serverId then
        return true
    end
    mgr._bgSweepActive = true
    mgr._bgSweepServerId = serverId

    local tmManager = TimerManager:GetInstance()
    local tileW = TileCountX or 1000
    local tileH = TileCountY or 1000
    local startX, startY = 500, 500

    local curWsInit = SceneManager and SceneManager.World
    if curWsInit and curWsInit.Camera and mgr.isInit == true then
        startX, startY = GetActualCameraTilePos(mgr, curWsInit)
    else
        local p = LuaEntry.Player
        local bm = DataCenter.BuildManager
        local myHqIndex = (p and p.cityPointIndex) or (bm and bm.CityPointIndex) or 500500
        if SceneUtils and SceneUtils.IndexToTileXY then
            local hx, hy = SceneUtils.IndexToTileXY(myHqIndex)
            if hx and hy and hx > 0 and hy > 0 then startX, startY = hx, hy end
        end
    end

    -- Zero-gap overlapping svLod=1 grid (server returns 71x101 full-detail HQs/Zombies/Resources/Cities/Radar)
    -- Step 64x90 guarantees 7..11 tiles overlap on every border and full 0..999 edge-to-edge coverage (192 sectors)
    local xs = {}
    for gx = 32, tileW - 32, 64 do
        xs[#xs + 1] = gx
    end
    if #xs == 0 then
        xs[#xs + 1] = math.max(0, math.floor(tileW / 2))
    elseif xs[#xs] < (tileW - 36) then
        xs[#xs + 1] = tileW - 32
    end
    local ys = {}
    for gy = 48, tileH - 48, 90 do
        ys[#ys + 1] = gy
    end
    if #ys == 0 then
        ys[#ys + 1] = math.max(0, math.floor(tileH / 2))
    elseif ys[#ys] < (tileH - 51) then
        ys[#ys + 1] = tileH - 48
    end

    local allSectors = {}
    for ix = 1, #xs do
        local gx = xs[ix]
        for iy = 1, #ys do
            local gy = ys[iy]
            local dx = gx - startX
            local dy = gy - startY
            allSectors[#allSectors + 1] = { x = gx, y = gy, d2 = dx * dx + dy * dy }
        end
    end
    table.sort(allSectors, function(a, b) return a.d2 < b.d2 end)

    local sweepToken = (mgr._bgSweepToken or 0) + 1
    mgr._bgSweepToken = sweepToken
    local sIdx = 1
    local dirtyTicks = 0
    local fastStepDelay = forceRestart and 0.075 or 0.10
    local batchSize = forceRestart and 2 or 2
    local isSilentRefresh = (not forceRestart) and ((_G._MasterViewPointCount or 0) >= 20000)
    local lastSortX, lastSortY = startX, startY

    local function sendSectorSvLod1(gx, gy, targetSid)
        local cx = math.max(0, math.min(tileW - 1, math.floor(gx)))
        local cy = math.max(0, math.min(tileH - 1, math.floor(gy)))
        if mgr.isInit == true then
            mgr.waitingForReply = false
            mgr:DoSendViewRequest(cx, cy, 1, targetSid)
            return
        end
        -- In City view (CurrSceneID == 1), SceneUtils.ClampTilePosXY clamps to 80x80 city bounds.
        -- Send the exact GetViewLevelWorldInfo packet directly with 0..999 world coordinates so City preloading works seamlessly.
        if SFSNetwork and SFSNetwork.SendMessage and MsgDefines and MsgDefines.GetViewLevelWorldInfo then
            local realSid = targetSid
            local worldId = 0
            local p = LuaEntry and LuaEntry.Player
            if p then
                if p.IsInSelfServer then
                    local okSelf, inSelf = pcall(p.IsInSelfServer, p)
                    if okSelf and inSelf == false and p.GetCrossServerId then
                        local okCross, cSid = pcall(p.GetCrossServerId, p)
                        if okCross and tonumber(cSid) and tonumber(cSid) > 0 then
                            realSid = tonumber(cSid)
                        end
                    end
                end
                if p.GetCurWorldId then
                    local okWid, wid = pcall(p.GetCurWorldId, p)
                    if okWid and tonumber(wid) then
                        worldId = tonumber(wid)
                    end
                end
            end
            SFSNetwork.SendMessage(MsgDefines.GetViewLevelWorldInfo, cx, cy, 0, 1, realSid, worldId, nil, 0)
        end
    end

    local function reprioritizeRemaining(camX, camY)
        if sIdx >= #allSectors then return end
        local tail = {}
        local n = 0
        for i = sIdx, #allSectors do
            local sec = allSectors[i]
            local dx = sec.x - camX
            local dy = sec.y - camY
            sec.d2 = dx * dx + dy * dy
            n = n + 1
            tail[n] = sec
        end
        table.sort(tail, function(a, b) return a.d2 < b.d2 end)
        for i = 1, n do
            allSectors[sIdx + i - 1] = tail[i]
        end
        lastSortX, lastSortY = camX, camY
    end

    _G._FullMapLoadState = {
        active = true,
        silentRefresh = isSilentRefresh,
        done = 0,
        total = #allSectors,
        serverId = serverId,
        lastCompletedAt = (_G._FullMapLoadState and _G._FullMapLoadState.lastCompletedAt) or 0,
    }
    pcall(_G.RefreshMasterOverlayUI)

    local function sStep()
        if mgr._bgSweepToken ~= sweepToken then return end
        if _G._MasterToggles and _G._MasterToggles.masterEnabled == false then
            _G._FullMapLoadState.active = false
            tmManager:DelayInvoke(sStep, 1.0)
            return
        end

        local liveSid = GetActiveWorldServerId(mgr)
        if liveSid > 0 and liveSid ~= serverId then
            -- User switched to another state (e.g. VS Duel cross-state visit); restart sweep on the live server!
            mgr._bgSweepActive = false
            _G.StartBackgroundWorldPreloader(true)
            return
        end

        local curWs = SceneManager and SceneManager.World
        local realCamX, realCamY = nil, nil
        if curWs and curWs.Camera and mgr.isInit == true then
            realCamX, realCamY = GetActualCameraTilePos(mgr, curWs)
            if realCamX and realCamY and (math.abs(realCamX - lastSortX) >= 80 or math.abs(realCamY - lastSortY) >= 80) then
                reprioritizeRemaining(realCamX, realCamY)
            end
        end

        if sIdx <= #allSectors then
            local prevReqX = mgr.reqPos and mgr.reqPos.x or nil
            local prevReqY = mgr.reqPos and mgr.reqPos.y or nil
            local sent = 0
            while sent < batchSize and sIdx <= #allSectors do
                local sec = allSectors[sIdx]
                sIdx = sIdx + 1
                sent = sent + 1
                sendSectorSvLod1(sec.x, sec.y, serverId)
            end

            if realCamX and realCamY and mgr.reqPos and mgr.reqPos.Set then
                mgr.reqPos:Set(realCamX, realCamY)
            elseif prevReqX and prevReqY and mgr.reqPos and mgr.reqPos.Set then
                mgr.reqPos:Set(prevReqX, prevReqY)
            end

            _G._FullMapLoadState.active = true
            _G._FullMapLoadState.silentRefresh = isSilentRefresh
            _G._FullMapLoadState.done = sIdx - 1
            _G._FullMapLoadState.total = #allSectors
            _G._FullMapLoadState.serverId = serverId

            dirtyTicks = dirtyTicks + sent
            if (dirtyTicks % 4) < sent then
                pcall(_G.RefreshMasterOverlayUI)
            end
            if dirtyTicks >= 40 then
                dirtyTicks = 0
                if mgr.isInit ~= true then
                    _G.SaveWorldCacheToDisk(serverId, false)
                end
            end
            tmManager:DelayInvoke(sStep, fastStepDelay)
        else
            -- Completed full 1000x1000 zero-gap map sweep. Defer 40MB disk flush until idle/City, rest 5 min, then silently refresh
            local deferTok = (_G._MasterDeferredSaveToken or 0) + 1
            _G._MasterDeferredSaveToken = deferTok
            local deferTries = 0
            local function _deferredIdleSave()
                if _G._MasterDeferredSaveToken ~= deferTok then return end
                deferTries = deferTries + 1
                local curMgr = DataCenter and DataCenter.WorldPointManager
                local inWorld = (curMgr and curMgr.isInit == true)
                local camQuiet = (os.clock() - (_G._LastCameraMoveClock or 0)) >= 2.5
                local streamIdle = (_G._MasterStreamActive ~= true)
                if (not inWorld) or (streamIdle and camQuiet) or deferTries >= 12 then
                    _G.SaveWorldCacheToDisk(serverId, true)
                    return
                end
                tmManager:DelayInvoke(_deferredIdleSave, 1.0)
            end
            tmManager:DelayInvoke(_deferredIdleSave, 0.5)
            _G._FullMapLoadState.active = false
            _G._FullMapLoadState.silentRefresh = true
            _G._FullMapLoadState.done = #allSectors
            _G._FullMapLoadState.lastCompletedAt = os.time()
            _G._ForceStreamRescan = true
            pcall(_G.RefreshMasterOverlayUI)
            sIdx = 1
            isSilentRefresh = true
            if realCamX and realCamY then
                reprioritizeRemaining(realCamX, realCamY)
            end
            fastStepDelay = 0.16
            batchSize = 1
            tmManager:DelayInvoke(sStep, 300.0)
        end
    end
    sStep()

    -- Adaptive parser pump so incoming packets decode immediately even while in City view
    local pumpToken = (mgr._bgPumpToken or 0) + 1
    mgr._bgPumpToken = pumpToken
    local function sPump()
        if mgr._bgPumpToken ~= pumpToken then return end
        local hasPending = false
        pcall(function()
            if mgr.ParseServerDataAsync then
                mgr:ParseServerDataAsync()
            end
            local mq = mgr.messageQueue
            local pm = mgr.pointMessageArray
            if (type(mq) == "table" and #mq > 0) or (type(pm) == "table" and #pm > 0) then
                hasPending = true
            end
        end)
        tmManager:DelayInvoke(sPump, hasPending and 0.04 or 0.15)
    end
    sPump()
    return true
end

function _G.TriggerFullMapLoad(forceRestart)
    if _G._MasterToggles then
        _G._MasterToggles.masterEnabled = true
    end
    local mgr = DataCenter and DataCenter.WorldPointManager
    local status = "NO_WORLD_POINT_MANAGER"
    if _G.ApplyLastZWorldMaster then
        local ok, res = pcall(_G.ApplyLastZWorldMaster)
        status = tostring(ok) .. ": " .. tostring(res)
        _G._LastMasterStatus = status
    end
    if mgr then
        local sid = GetActiveWorldServerId(mgr)
        pcall(_G.RestoreWorldMapCache, sid)
        SyncSpatialGridIfReplaced(mgr)
        _G.StartBackgroundWorldPreloader(forceRestart ~= false)
        _G._ForceStreamRescan = true
        -- Immediately queue an initial viewport-first burst of unbuilt points in concentric spatial buckets
        if mgr.isInit == true and mgr.allViewPoints and mgr.AddToBuildList then
            local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
            local camBx = math.floor(camX / BUCKET_SIZE)
            local camBy = math.floor(camY / BUCKET_SIZE)
            local burst = 0
            local grid = _G._MasterSpatialGrid
            local minBx = math.max(0, math.floor((camX - 530) / BUCKET_SIZE))
            local maxBx = math.min(20, math.floor((camX + 530) / BUCKET_SIZE))
            local minBy = math.max(0, math.floor((camY - 530) / BUCKET_SIZE))
            local maxBy = math.min(20, math.floor((camY + 530) / BUCKET_SIZE))
            local ordered = {}
            for bx = minBx, maxBx do
                for by = minBy, maxBy do
                    local bKey = by * 4096 + bx
                    if grid and grid[bKey] then
                        local dx = bx - camBx
                        local dy = by - camBy
                        ordered[#ordered + 1] = { key = bKey, d2 = dx * dx + dy * dy }
                    end
                end
            end
            table.sort(ordered, function(a, b) return a.d2 < b.d2 end)
            for i = 1, #ordered do
                local bucket = grid[ordered[i].key]
                if bucket then
                    for k, v in pairs(bucket) do
                        if type(v) == "table" and (v.mainIndex == nil or v.mainIndex == k) and (v.pointInfo ~= nil or v.desertInfo ~= nil) then
                            if not (mgr.allObj and mgr.allObj[k]) and not (mgr.toBuildSet and mgr.toBuildSet[k]) then
                                if _G.ShouldBuildPointNow(mgr, k, v, camX, camY, false) then
                                    mgr:AddToBuildList(k)
                                    burst = burst + 1
                                    if burst >= 800 then break end
                                end
                            end
                        end
                    end
                end
                if burst >= 800 then break end
            end
        end
    end
    pcall(_G.RefreshMasterOverlayUI)
    local ptCnt = _G._MasterViewPointCount or 0
    local objCnt = tonumber(_G._MasterObjCount or 0) or 0
    return string.format(
        "FULL_MAP_LOAD_TRIGGERED (server=%d, inWorld=%s, points=%d, built=%d, vtblPatched=%d)",
        GetActiveWorldServerId(mgr),
        tostring(mgr and mgr.isInit == true),
        ptCnt,
        objCnt,
        tonumber(_G._MasterVtblPatchedCount or 0) or 0
    )
end

-- Scene transitions, hotkey poller and heartbeat
if not DataCenter or not SceneManager or not TimerManager then
    return "BOOTING_WAIT"
end

local sm = SceneManager
if sm and not sm._masterAutoWorldHooked then
    sm._masterAutoWorldHooked = true
    local oldChangeToWorld = sm.ChangeToWorld
    sm.ChangeToWorld = function(self, ...)
        pcall(_G.RestoreWorldMapCache)
        local res = oldChangeToWorld(self, ...)
        if TimerManager then
            TimerManager:GetInstance():DelayInvoke(function()
                if _G.ApplyLastZWorldMaster then pcall(_G.ApplyLastZWorldMaster) end
            end, 0.05)
            TimerManager:GetInstance():DelayInvoke(function()
                if _G.ApplyLastZWorldMaster then pcall(_G.ApplyLastZWorldMaster) end
            end, 0.5)
            TimerManager:GetInstance():DelayInvoke(function()
                if _G.ApplyLastZWorldMaster then pcall(_G.ApplyLastZWorldMaster) end
            end, 1.5)
        end
        return res
    end
end

if TimerManager then
    local tmManager = TimerManager:GetInstance()

    -- Throttled 20Hz (0.05s) Hotkey Poller for F1..F6 and Home
    local hkToken = (_G._masterHotkeyToken or 0) + 1
    _G._masterHotkeyToken = hkToken
    _G._keyPrevState = _G._keyPrevState or {}

    local kc = CS.UnityEngine.KeyCode
    local inp = CS.UnityEngine.Input
    local KEY_BINDINGS = {
        { code = kc.F1,   field = "masterEnabled", isWorldToggle = true },
        { code = kc.F2,   field = "showZombies",   isWorldToggle = true },
        { code = kc.F3,   field = "showResources", isWorldToggle = true },
        { code = kc.F4,   field = "showBoomers",   isWorldToggle = true },
        { code = kc.F5,   field = "showHQs",       isWorldToggle = true },
        { code = kc.F6,   field = "__fullMapLoad", isFullLoad = true },
        { code = kc.Home, field = "showOverlay",   isWorldToggle = false },
    }

    local function _pollHotkeysWork()
        if not inp or not _G._MasterToggles then return end
        local prev = _G._keyPrevState
        if (inp.anyKey ~= nil or inp.anyKeyDown ~= nil) and (not inp.anyKey) and (not inp.anyKeyDown) then
            local hasLatched = false
            for i = 1, #KEY_BINDINGS do
                if prev[KEY_BINDINGS[i].field] then
                    hasLatched = true
                    break
                end
            end
            if not hasLatched then return end
        end
        for i = 1, #KEY_BINDINGS do
            local b = KEY_BINDINGS[i]
            local isDown = inp.GetKey(b.code) or (inp.GetKeyDown and inp.GetKeyDown(b.code))
            if isDown and not prev[b.field] then
                prev[b.field] = true
                if b.isFullLoad then
                    if _G.TriggerFullMapLoad then
                        pcall(_G.TriggerFullMapLoad, true)
                    end
                else
                    _G._MasterToggles[b.field] = not _G._MasterToggles[b.field]
                    if b.isWorldToggle and _G.ApplyToggleChangeImmediate then
                        _G.ApplyToggleChangeImmediate()
                    else
                        pcall(_G.RefreshMasterOverlayUI)
                    end
                end
            elseif not isDown and prev[b.field] then
                prev[b.field] = false
            end
        end
    end

    local function pollHotkeys()
        if _G._masterHotkeyToken ~= hkToken then return end
        pcall(_pollHotkeysWork)
        tmManager:DelayInvoke(pollHotkeys, 0.05)
    end
    tmManager:DelayInvoke(pollHotkeys, 0.05)

    local hbToken = (_G._masterHeartbeatToken or 0) + 1
    _G._masterHeartbeatToken = hbToken
    local _hbApp = CS.UnityEngine.Application
    local _hbQs = CS.UnityEngine.QualitySettings
    local _hbTp = CS.UnityEngine.ThreadPriority
    local _hbLastScene = nil

    local function _hbWork()
        pcall(_G.RefreshMasterOverlayUI)
        local curScene = SceneManager and SceneManager.CurrSceneID
        if curScene ~= _hbLastScene then
            _hbLastScene = curScene
            _G._MasterPerfDirty = true
        end
        if _hbApp then
            if _hbApp.targetFrameRate ~= 180 then _hbApp.targetFrameRate = 180 end
            if _hbTp and _hbApp.backgroundLoadingPriority ~= _hbTp.High then _hbApp.backgroundLoadingPriority = _hbTp.High end
        end
        if _hbQs and (_G._MasterPerfDirty or _hbQs.shadowDistance ~= 120.0 or _hbQs.vSyncCount ~= 0) then
            if _hbQs.vSyncCount ~= 0 then _hbQs.vSyncCount = 0 end
            if _hbQs.maxQueuedFrames ~= 2 then _hbQs.maxQueuedFrames = 2 end
            if _hbQs.shadowDistance ~= 120.0 then _hbQs.shadowDistance = 120.0 end
            if _hbQs.asyncUploadTimeSlice ~= 16 then _hbQs.asyncUploadTimeSlice = 16 end
            if _hbQs.asyncUploadBufferSize ~= 256 then _hbQs.asyncUploadBufferSize = 256 end
            if _hbQs.realtimeReflectionProbes ~= false then _hbQs.realtimeReflectionProbes = false end
            if _hbQs.antiAliasing ~= 2 then _hbQs.antiAliasing = 2 end
            _G._MasterPerfDirty = false
        end

        local curWs = SceneManager and SceneManager.World
        if curWs and curWs.Camera and curWs.Camera.camera and not IsNull(curWs.Camera.camera) then
            local cam = curWs.Camera.camera
            if cam.farClipPlane ~= 12000.0 then cam.farClipPlane = 12000.0 end
            if cam.nearClipPlane ~= 20.0 then cam.nearClipPlane = 20.0 end
        end

        -- Auto-detect World View session and flush dirty map cache when camera/stream is idle
        local curMgr = DataCenter and DataCenter.WorldPointManager
        local isNowInWorld = (curMgr and curMgr.isInit == true)
        if isNowInWorld then
            if not curMgr._masterAppliedForThisWorldSession or curMgr:GetServerLod(6) > 1 then
                if _G.ApplyLastZWorldMaster then
                    local ok, res = pcall(_G.ApplyLastZWorldMaster)
                    _G._LastMasterStatus = tostring(ok) .. ": " .. tostring(res)
                end
            end
        elseif curMgr then
            curMgr._masterAppliedForThisWorldSession = false
        end
        local hbSid = ResolveCacheServerId(nil, curMgr)
        if hbSid > 0 and (_G._WorldCacheDirtyCount[hbSid] or 0) > 0 then
            local sweepBusy = (_G._FullMapLoadState and _G._FullMapLoadState.active == true)
            local camIdle = (not isNowInWorld) or ((os.clock() - (_G._LastCameraMoveClock or 0)) >= 2.5 and _G._MasterStreamActive ~= true)
            if (not sweepBusy) and camIdle and (os.time() - (_G._WorldCacheLastSaveTs[hbSid] or 0)) >= 25 then
                _G.SaveWorldCacheToDisk(hbSid, false)
            end
        end
    end

    local function _hbHeliWork()
        local ahm = DataCenter and DataCenter.AllianceHelpDataManager
        if ahm and ahm.GetHelpNum and ahm:GetHelpNum() > 0 then
            ahm:OnHelpAll()
        end
    end

    local function hb()
        if _G._masterHeartbeatToken ~= hbToken then return end
        pcall(_hbWork)
        pcall(_hbHeliWork)
        collectgarbage("step", 60)
        tmManager:DelayInvoke(hb, 1.5)
    end
    tmManager:DelayInvoke(hb, 0.05)

    -- Dynamic Spatial Viewport Streamer: 50x50 Spatial Bucketing with viewport-first concentric priority
    local streamToken = (_G._masterStreamToken or 0) + 1
    _G._masterStreamToken = streamToken
    local lastStreamCamX, lastStreamCamY = -9999, -9999
    local streamHasMoreWork = true
    local STREAM_MAX_RADIUS = 1000
    local _pendingBucketKeys = {}
    local _pendingBucketIdx = 1
    local _pendingBucketSeen = {}

    local function _enqueueStreamBucket(bKey)
        if not _pendingBucketSeen[bKey] and _G._MasterSpatialGrid and _G._MasterSpatialGrid[bKey] then
            _pendingBucketSeen[bKey] = true
            _pendingBucketKeys[#_pendingBucketKeys + 1] = bKey
        end
    end

    local function _sortPendingNearest(camBx, camBy)
        local n = #_pendingBucketKeys - _pendingBucketIdx + 1
        if n <= 1 then return end
        local items = {}
        for i = _pendingBucketIdx, #_pendingBucketKeys do
            local bk = _pendingBucketKeys[i]
            local bx = bk % 4096
            local by = math.floor(bk / 4096)
            local dx = bx - camBx
            local dy = by - camBy
            items[#items + 1] = { key = bk, d2 = dx * dx + dy * dy }
        end
        table.sort(items, function(a, b) return a.d2 < b.d2 end)
        for i = 1, #items do
            _pendingBucketKeys[_pendingBucketIdx + i - 1] = items[i].key
        end
    end

    local lastLodReconcile = -1
    local lastLodCamX, lastLodCamY = -9999, -9999
    local lastResLodReconcile = -1

    local function _reconcileMonsterAndResourceLods(curMgr, camX, camY, curLod, streamStart)
        local resNeedNow = (curLod ~= lastResLodReconcile)
            or (math.abs(camX - (_G._MasterLastResLodCamX or -9999)) >= 6)
            or (math.abs(camY - (_G._MasterLastResLodCamY or -9999)) >= 6)
        local pass = _G._MasterReconcilePass
        if not pass
            or pass.mgr ~= curMgr
            or pass.lod ~= curLod
            or math.abs(camX - pass.camX) >= 4
            or math.abs(camY - pass.camY) >= 4
            or (resNeedNow and not pass.resNeedUpdate)
        then
            local tok = (_G._MasterReconcileToken or 0) + 1
            _G._MasterReconcileToken = tok
            local evictKeys = {}
            local nearMap = _G._MasterNear3DMonsters
            if nearMap then
                for pIdx in pairs(nearMap) do
                    evictKeys[#evictKeys + 1] = pIdx
                end
            end
            local labelKeys = {}
            if curLod >= 5 and _G._MasterProxyMonsterLabels and next(_G._MasterProxyMonsterLabels) ~= nil then
                for pIdx in pairs(_G._MasterProxyMonsterLabels) do
                    labelKeys[#labelKeys + 1] = pIdx
                end
            end
            local restoreKeys = {}
            if curLod <= 4 and _G._MasterProxyMonsters and next(_G._MasterProxyMonsters) ~= nil then
                for pIdx, mObj in pairs(_G._MasterProxyMonsters) do
                    if mObj and mObj._isProxyMode and mObj._proxyLabelHandle == nil then
                        restoreKeys[#restoreKeys + 1] = pIdx
                    end
                end
            end
            local buckets = {}
            local grid = _G._MasterSpatialGrid
            if grid and curMgr.allObj and curLod <= 2 then
                local scanRadius = 110
                local camBx = math.floor(camX / BUCKET_SIZE)
                local camBy = math.floor(camY / BUCKET_SIZE)
                local minBx = math.max(0, math.floor((camX - scanRadius) / BUCKET_SIZE))
                local maxBx = math.min(20, math.floor((camX + scanRadius) / BUCKET_SIZE))
                local minBy = math.max(0, math.floor((camY - scanRadius) / BUCKET_SIZE))
                local maxBy = math.min(20, math.floor((camY + scanRadius) / BUCKET_SIZE))
                local ordered = {}
                for bx = minBx, maxBx do
                    for by = minBy, maxBy do
                        local bKey = by * 4096 + bx
                        if grid[bKey] then
                            local dx = bx - camBx
                            local dy = by - camBy
                            ordered[#ordered + 1] = { key = bKey, d2 = dx * dx + dy * dy }
                        end
                    end
                end
                table.sort(ordered, function(a, b) return a.d2 < b.d2 end)
                for i = 1, #ordered do
                    buckets[i] = ordered[i].key
                end
            end
            pass = {
                mgr = curMgr,
                lod = curLod,
                camX = camX,
                camY = camY,
                token = tok,
                phase = "EVICT",
                resNeedUpdate = resNeedNow,
                evictKeys = evictKeys,
                evictIdx = 1,
                labelKeys = labelKeys,
                labelIdx = 1,
                restoreKeys = restoreKeys,
                restoreIdx = 1,
                buckets = buckets,
                bucketIdx = 1,
                curBucketKeys = nil,
                itemIdx = 1,
            }
            _G._MasterReconcilePass = pass
        end

        if pass.phase == "EVICT" then
            local nearMap = _G._MasterNear3DMonsters
            local demoteOps = 0
            while pass.evictIdx <= #pass.evictKeys do
                local pIdx = pass.evictKeys[pass.evictIdx]
                pass.evictIdx = pass.evictIdx + 1
                local mObj = nearMap and nearMap[pIdx]
                if mObj and mObj._ApplyMonsterLodState then
                    local px = mObj._cachedTileX
                    local py = mObj._cachedTileY
                    if not px or not py then
                        px, py = FastIndexToXY(pIdx)
                        mObj._cachedTileX = px
                        mObj._cachedTileY = py
                    end
                    local dist = math.max(math.abs(px - pass.camX), math.abs(py - pass.camY))
                    if (pass.lod >= 3 or dist > MONSTER_EVICT_3D_RADIUS) and mObj.isInBattle ~= true then
                        local info = curMgr.GetPointInfo and curMgr:GetPointInfo(pIdx)
                        pcall(mObj._ApplyMonsterLodState, mObj, info)
                    end
                elseif nearMap then
                    nearMap[pIdx] = nil
                end
                demoteOps = demoteOps + 1
                if pass.evictIdx <= #pass.evictKeys and (demoteOps % 16 == 0) and (os.clock() - streamStart) >= 0.0025 then
                    _G._MasterLodDirty = true
                    return false
                end
            end
            pass.phase = "LABELS"
        end

        if pass.phase == "LABELS" then
            if pass.lod >= 5 and pass.labelKeys and pass.labelIdx <= #pass.labelKeys then
                local lblMap = _G._MasterProxyMonsterLabels
                local lr = curMgr.GetLabelRenderer and curMgr:GetLabelRenderer()
                local lblOps = 0
                while pass.labelIdx <= #pass.labelKeys do
                    local pIdx = pass.labelKeys[pass.labelIdx]
                    pass.labelIdx = pass.labelIdx + 1
                    local mObj = lblMap and lblMap[pIdx]
                    if mObj and mObj._proxyLabelHandle ~= nil then
                        if lr and lr.RemoveLabel then
                            pcall(lr.RemoveLabel, lr, mObj._proxyLabelHandle)
                        end
                        mObj._proxyLabelHandle = nil
                        mObj._proxyLabelLv = nil
                    end
                    if lblMap then
                        lblMap[pIdx] = nil
                    end
                    lblOps = lblOps + 1
                    if pass.labelIdx <= #pass.labelKeys and (lblOps % 16 == 0) and (os.clock() - streamStart) >= 0.0025 then
                        _G._MasterLodDirty = true
                        return false
                    end
                end
            end
            pass.phase = "SCAN"
        end

        if pass.phase == "SCAN" then
            local grid = _G._MasterSpatialGrid
            if pass.lod <= 2 and grid and curMgr.allObj then
                local ops = 0
                while pass.bucketIdx <= #pass.buckets do
                    local bKey = pass.buckets[pass.bucketIdx]
                    local bucket = grid[bKey]
                    if bucket then
                        if not pass.curBucketKeys then
                            local keys = {}
                            for k in pairs(bucket) do
                                keys[#keys + 1] = k
                            end
                            pass.curBucketKeys = keys
                            pass.itemIdx = 1
                        end
                        while pass.itemIdx <= #pass.curBucketKeys do
                            local k = pass.curBucketKeys[pass.itemIdx]
                            pass.itemIdx = pass.itemIdx + 1
                            local v = bucket[k]
                            local obj = curMgr.allObj[k]
                            if obj and obj._lastReconcileToken ~= pass.token then
                                obj._lastReconcileToken = pass.token
                                if obj._isProxyMode and obj._ApplyMonsterLodState then
                                    local px = obj._cachedTileX or (type(v) == "table" and v._px)
                                    local py = obj._cachedTileY or (type(v) == "table" and v._py)
                                    if not px or not py then
                                        px, py = FastIndexToXY(k)
                                    end
                                    if math.max(math.abs(px - pass.camX), math.abs(py - pass.camY)) <= MONSTER_NEAR_3D_RADIUS then
                                        local info = (type(v) == "table" and v.pointInfo) or (curMgr.GetPointInfo and curMgr:GetPointInfo(k))
                                        pcall(obj._ApplyMonsterLodState, obj, info)
                                    end
                                elseif obj._ApplyInstancedLodState then
                                    if (obj.lodLv or 0) ~= pass.lod or pass.resNeedUpdate then
                                        obj.lodLv = pass.lod
                                        local info = (type(v) == "table" and v.pointInfo) or (curMgr.GetPointInfo and curMgr:GetPointInfo(k))
                                        if info then pcall(obj._ApplyInstancedLodState, obj, info, false) end
                                    end
                                elseif obj.CreateMain and not obj.instance then
                                    local px = obj._cachedTileX or (type(v) == "table" and v._px)
                                    local py = obj._cachedTileY or (type(v) == "table" and v._py)
                                    if not px or not py then
                                        px, py = FastIndexToXY(k)
                                        obj._cachedTileX = px
                                        obj._cachedTileY = py
                                    end
                                    if math.abs(px - pass.camX) <= 110 and math.abs(py - pass.camY) <= 110 then
                                        if obj.LodChange and (obj.lodLv or 0) ~= pass.lod then
                                            pcall(obj.LodChange, obj, pass.lod)
                                        elseif obj.CreateMain then
                                            local info = (type(v) == "table" and v.pointInfo) or (curMgr.GetPointInfo and curMgr:GetPointInfo(k))
                                            if info then pcall(obj.CreateMain, obj, info) end
                                        end
                                    end
                                end
                                ops = ops + 1
                                local hasRemaining = (pass.itemIdx <= #pass.curBucketKeys) or (pass.bucketIdx < #pass.buckets)
                                if hasRemaining and (ops % 32 == 0) and (os.clock() - streamStart) >= 0.0025 then
                                    _G._MasterLodDirty = true
                                    return false
                                end
                            end
                        end
                    end
                    pass.curBucketKeys = nil
                    pass.itemIdx = 1
                    pass.bucketIdx = pass.bucketIdx + 1
                end
            end
            pass.phase = "RESTORE_LABELS"
        end

        if pass.phase == "RESTORE_LABELS" then
            if pass.lod <= 4 and pass.restoreKeys and pass.restoreIdx <= #pass.restoreKeys then
                local proxyMap = _G._MasterProxyMonsters
                local allObj = curMgr.allObj
                local toggles = _G._MasterToggles
                local restoreOps = 0
                while pass.restoreIdx <= #pass.restoreKeys do
                    local pIdx = pass.restoreKeys[pass.restoreIdx]
                    pass.restoreIdx = pass.restoreIdx + 1
                    local obj = proxyMap and proxyMap[pIdx]
                    if obj and obj._isProxyMode and obj._proxyLabelHandle == nil and obj._EnsureProxyVisual then
                        if allObj and allObj[pIdx] ~= obj then
                            if proxyMap then proxyMap[pIdx] = nil end
                        else
                            local vp = curMgr.allViewPoints and curMgr.allViewPoints[pIdx]
                            local info = (vp and vp.pointInfo) or (curMgr.GetPointInfo and curMgr:GetPointInfo(pIdx))
                            local allowed = true
                            if toggles then
                                if toggles.masterEnabled == false then
                                    local px = obj._cachedTileX
                                    local py = obj._cachedTileY
                                    if not px or not py then
                                        px, py = FastIndexToXY(pIdx)
                                        obj._cachedTileX = px
                                        obj._cachedTileY = py
                                    end
                                    if math.max(math.abs(px - pass.camX), math.abs(py - pass.camY)) > 48 then
                                        allowed = false
                                    end
                                end
                                if allowed then
                                    local cat = GetMonsterCategory({ pointInfo = info, _parsedExtra = obj.monsterInfo })
                                    if (cat == "BOOMER" or cat == "BOSS") and toggles.showBoomers == false then
                                        allowed = false
                                    elseif cat == "ZOMBIE" and toggles.showZombies == false then
                                        allowed = false
                                    end
                                end
                            end
                            if allowed then
                                pcall(obj._EnsureProxyVisual, obj, info)
                            end
                        end
                    end
                    restoreOps = restoreOps + 1
                    if pass.restoreIdx <= #pass.restoreKeys and (restoreOps % 16 == 0) and (os.clock() - streamStart) >= 0.0025 then
                        _G._MasterLodDirty = true
                        return false
                    end
                end
            end
        end
        _G._MasterReconcilePass = nil
        return true
    end

    local function _streamWork()
        local curMgr = DataCenter and DataCenter.WorldPointManager
        local curWs = SceneManager and SceneManager.World
        if not (curMgr and curMgr.isInit == true) then
            streamHasMoreWork = true
            _G._MasterStreamActive = false
            return
        end

        local streamStart = os.clock()
        SyncSpatialGridIfReplaced(curMgr)
        if _G._MasterStreamReset then
            _G._MasterStreamReset = false
            _pendingBucketKeys = {}
            _pendingBucketIdx = 1
            _pendingBucketSeen = {}
            lastStreamCamX, lastStreamCamY = -9999, -9999
            lastLodReconcile = -1
            lastLodCamX, lastLodCamY = -9999, -9999
            lastResLodReconcile = -1
            _G._MasterLastResLodCamX = -9999
            _G._MasterLastResLodCamY = -9999
            _G._MasterReconcilePass = nil
            streamHasMoreWork = false
        end
        local camX, camY = GetActualCameraTilePos(curMgr, curWs)
        local curLod = (curMgr and curMgr.lodLv) or 1
        local camBx = math.floor(camX / BUCKET_SIZE)
        local camBy = math.floor(camY / BUCKET_SIZE)
        local moved = (math.abs(camX - lastStreamCamX) >= 6 or math.abs(camY - lastStreamCamY) >= 6)
        if moved then
            _G._LastCameraMoveClock = streamStart
        end
        local resMoved = (curLod ~= lastResLodReconcile)
            or (math.abs(camX - (_G._MasterLastResLodCamX or -9999)) >= 6)
            or (math.abs(camY - (_G._MasterLastResLodCamY or -9999)) >= 6)
        local lodChanged = (curLod ~= lastLodReconcile)
            or (_G._MasterLodDirty == true)
            or (math.abs(camX - lastLodCamX) >= 4 or math.abs(camY - lastLodCamY) >= 4)
            or resMoved
        if lodChanged then
            _G._MasterLodDirty = false
            local lodDone = _reconcileMonsterAndResourceLods(curMgr, camX, camY, curLod, streamStart)
            if lodDone then
                lastLodReconcile = curLod
                lastLodCamX = camX
                lastLodCamY = camY
                if resMoved then
                    lastResLodReconcile = curLod
                    _G._MasterLastResLodCamX = camX
                    _G._MasterLastResLodCamY = camY
                end
            end
        end
        local forced = (_G._ForceStreamRescan == true)
        local dirtyBuckets = _G._MasterDirtyBuckets
        local hasDirty = (dirtyBuckets ~= nil and next(dirtyBuckets) ~= nil)
        local hasPending = (_pendingBucketIdx <= #_pendingBucketKeys)
        if not moved and not forced and not hasDirty and not hasPending then
            streamHasMoreWork = (_G._MasterLodDirty == true)
            _G._MasterStreamActive = streamHasMoreWork
            return
        end

        local needSort = false
        if forced then
            _pendingBucketKeys = {}
            _pendingBucketIdx = 1
            _pendingBucketSeen = {}
            _G._ForceStreamRescan = false
            if dirtyBuckets then
                for dk in pairs(dirtyBuckets) do dirtyBuckets[dk] = nil end
            end
            for bKey in pairs(_G._MasterSpatialGrid or {}) do
                _enqueueStreamBucket(bKey)
            end
            lastStreamCamX = camX
            lastStreamCamY = camY
            needSort = true
        else
            if moved then
                local minBx = math.max(0, math.floor((camX - STREAM_MAX_RADIUS) / BUCKET_SIZE))
                local maxBx = math.min(20, math.floor((camX + STREAM_MAX_RADIUS) / BUCKET_SIZE))
                local minBy = math.max(0, math.floor((camY - STREAM_MAX_RADIUS) / BUCKET_SIZE))
                local maxBy = math.min(20, math.floor((camY + STREAM_MAX_RADIUS) / BUCKET_SIZE))
                for bx = minBx, maxBx do
                    for by = minBy, maxBy do
                        _enqueueStreamBucket(by * 4096 + bx)
                    end
                end
                lastStreamCamX = camX
                lastStreamCamY = camY
                needSort = true
            end
            if hasDirty then
                for dk in pairs(dirtyBuckets) do
                    dirtyBuckets[dk] = nil
                    _enqueueStreamBucket(dk)
                end
                needSort = true
            end
        end

        if needSort then
            _sortPendingNearest(camBx, camBy)
        end

        local queuedThisTick = 0
        local hitCap = false
        local grid = _G._MasterSpatialGrid
        if grid and curMgr.AddToBuildList then
            while _pendingBucketIdx <= #_pendingBucketKeys do
                local bKey = _pendingBucketKeys[_pendingBucketIdx]
                local bx = bKey % 4096
                local by = math.floor(bKey / 4096)
                local isViewportCore = (math.abs(bx - camBx) <= 1 and math.abs(by - camBy) <= 1)
                local bucket = grid[bKey]
                if bucket then
                    for k, v in pairs(bucket) do
                        if type(v) == "table" and (v.mainIndex == nil or v.mainIndex == k) and (v.pointInfo ~= nil or v.desertInfo ~= nil) then
                            if not (curMgr.allObj and curMgr.allObj[k]) and not (curMgr.toBuildSet and curMgr.toBuildSet[k]) then
                                if _G.ShouldBuildPointNow(curMgr, k, v, camX, camY, false) then
                                    curMgr:AddToBuildList(k)
                                    queuedThisTick = queuedThisTick + 1
                                    if (not isViewportCore) and (queuedThisTick >= 400 or ((queuedThisTick % 16 == 0) and (os.clock() - streamStart) >= 0.0025)) then
                                        hitCap = true
                                        break
                                    end
                                end
                            end
                        end
                    end
                end
                if hitCap then
                    break
                end
                _pendingBucketSeen[bKey] = nil
                _pendingBucketIdx = _pendingBucketIdx + 1
            end
        end
        if _pendingBucketIdx > #_pendingBucketKeys then
            _pendingBucketKeys = {}
            _pendingBucketIdx = 1
            _pendingBucketSeen = {}
            streamHasMoreWork = (_G._MasterLodDirty == true)
        else
            streamHasMoreWork = true
        end
        _G._MasterStreamActive = streamHasMoreWork
    end

    local function runCameraStreamer()
        if _G._masterStreamToken ~= streamToken then return end
        pcall(_streamWork)
        tmManager:DelayInvoke(runCameraStreamer, streamHasMoreWork and 0.05 or 0.20)
    end
    tmManager:DelayInvoke(runCameraStreamer, 0.05)
end

-- R3 Safe Strictly Read-Only Pre-Loading (Staggered post-login warm-up, zero SFS/UI/Guide mutation)
_G._hzPreloadDone = _G._hzPreloadDone or {}
_G._WarmupState = _G._WarmupState or {
    started = false,
    done = false,
    role = "main",
    uid = "",
    tablesWarmed = 0,
    managersWarmed = 0,
    shadersStarted = false,
    assetsWarmed = 0,
    skippedReason = "",
    errors = {},
}

local function _checkPreloadReadiness()
    if not LuaEntry or LuaEntry.m_isStartGame ~= true or LuaEntry.isInitDB ~= true then
        return false, "not_started_or_db_uninit"
    end
    if not LuaEntry.Player then
        return false, "no_player"
    end
    local uid = tostring(LuaEntry.Player.uid or "")
    if uid == "" or uid == "0" or uid == "nil" then
        return false, "invalid_uid"
    end
    if not DataCenter or not LocalController or not LocalController.instance or not TimerManager then
        return false, "core_singletons_missing"
    end
    if not SceneManager or (SceneManager.CurrSceneID ~= 1 and SceneManager.CurrSceneID ~= 2) then
        return false, "unsupported_scene"
    end
    local um = UIManager and UIManager.GetInstance and UIManager:GetInstance()
    if not um or um.__cProjectStateReady ~= true then
        return false, "ui_not_ready"
    end
    if DataCenter.GuideManager and DataCenter.GuideManager.InGuide and DataCenter.GuideManager:InGuide() then
        return false, "in_guide"
    end
    if DataCenter.MemoryPolicyManager and DataCenter.MemoryPolicyManager._needReleaseCache == true then
        return false, "low_memory_policy"
    end
    return true, uid
end

local function _roleRank(r)
    if r == "main" or r == true then return 2 end
    if r == "farm" then return 1 end
    return 0
end

local function _warmXmlTable(lc, tblName, st)
    if not tblName or tblName == "" then return end
    local inMem = false
    if lc.HasTableInMem then
        local okMem, memVal = pcall(lc.HasTableInMem, lc, tblName)
        if not okMem then
            st.errors[#st.errors + 1] = tostring(tblName) .. ".HasTableInMem:" .. tostring(memVal)
            return
        end
        inMem = (memVal == true)
    end
    if not inMem and lc.isTableLoaded then
        local okLoaded, loadedVal = pcall(lc.isTableLoaded, lc, tblName)
        if not okLoaded then
            st.errors[#st.errors + 1] = tostring(tblName) .. ".isTableLoaded:" .. tostring(loadedVal)
            return
        end
        inMem = (loadedVal == true)
    end
    if not inMem and lc.getTable then
        local ok, res = pcall(lc.getTable, lc, tblName)
        if ok then
            local loadedNow = (res ~= nil)
            if not loadedNow and lc.HasTableInMem then
                local okAfter, afterVal = pcall(lc.HasTableInMem, lc, tblName)
                loadedNow = okAfter and (afterVal == true)
            end
            if not loadedNow and lc.isTableLoaded then
                local okAfterL, afterLVal = pcall(lc.isTableLoaded, lc, tblName)
                loadedNow = okAfterL and (afterLVal == true)
            end
            if loadedNow then
                st.tablesWarmed = (st.tablesWarmed or 0) + 1
            else
                st.errors[#st.errors + 1] = tostring(tblName) .. ":getTable_returned_nil"
            end
        else
            st.errors[#st.errors + 1] = tostring(tblName) .. ":" .. tostring(res)
        end
    end
end

local function _warmManagerMethod(mgr, methodName, st)
    if mgr and type(mgr[methodName]) == "function" then
        local ok, err = pcall(mgr[methodName], mgr)
        if ok then
            return true
        end
        st.errors[#st.errors + 1] = methodName .. ":" .. tostring(err)
    end
    return false
end

function _G.WarmReadOnlyEngineCaches(opts)
    opts = type(opts) == "table" and opts or {}
    local rawRole = opts.role or (_G._FarmEcoMode and "farm" or "main")
    local role = (tostring(rawRole):lower() == "farm") and "farm" or "main"
    local force = opts.force == true
    local st = _G._WarmupState
    st.errors = st.errors or {}

    local ready, uidOrReason = _checkPreloadReadiness()
    if not ready then
        st.skippedReason = uidOrReason
        return "SKIPPED:" .. tostring(uidOrReason)
    end
    local uid = uidOrReason

    local doneVal = _G._hzPreloadDone[uid]
    if _roleRank(doneVal) >= _roleRank(role) and not force then
        if st.started and st.uid ~= uid then
            _G._hzWarmupToken = (_G._hzWarmupToken or 0) + 1
            st.started = false
        end
        st.uid = uid
        st.role = (doneVal == true) and "main" or doneVal
        st.done = true
        st.skippedReason = "already_warmed"
        return "ALREADY_DONE"
    end
    if st.started and st.uid == uid and _roleRank(role) <= _roleRank(st.role) and not force then
        return "IN_PROGRESS"
    end

    local okLc, lc = pcall(LocalController.instance)
    if not okLc or not lc then
        st.skippedReason = "no_local_controller"
        return "SKIPPED:no_local_controller"
    end

    st.role = role
    st.uid = uid
    st.started = true
    st.done = false
    st.skippedReason = ""
    st.tablesWarmed = 0
    st.managersWarmed = 0
    st.shadersStarted = false
    st.assetsWarmed = 0
    st.errors = {}

    local tasks = {}
    local tn = (type(TableName) == "table" and TableName) or {}

    -- Tier 1 Core Tables (Main + Farm): string key lists prevent Lua nil-hole truncation
    local coreEnumKeys = {
        "GoodsTab", "Resource", "DailyQuest", "BuildingDes", "LevelUp",
        "ScienceNew", "APSScienceTab", "ArmsTab", "LwDispatchSetting",
        "LwDispatchTask", "NewHeroesLevelUp", "HeroMilitaryRank", "Equip",
        "EquipAttribute", "NewHeroesB", "Vip", "Affect_Num", "CollectResource",
    }
    local coreExtraKeys = {
        {"Building", "building"}, {"DetectEvent", "detect_event"},
        {"GatherResource", "aps_gather_resource"}, {"VipTemp", "vip_temp"},
        {"EffectNumDesc", "effect_num_des"}, {"NewHeroes", "aps_new_heroes"},
        {"SkillTab", "skill"},
    }
    for _, key in ipairs(coreEnumKeys) do
        local t = tn[key]
        if t ~= nil and t ~= "" then
            tasks[#tasks + 1] = function() _warmXmlTable(lc, t, st) end
        end
    end
    for _, pair in ipairs(coreExtraKeys) do
        local t = tn[pair[1]] or pair[2]
        if t ~= nil and t ~= "" then
            tasks[#tasks + 1] = function() _warmXmlTable(lc, t, st) end
        end
    end

    if role == "main" then
        -- Tier 1 Main-only UI/map tables
        local mainEnumKeys = {
            "Monster", "WorldCity", "CarCompon", "CarMicrochip",
            "CarMicrochipAttribute", "Decoration", "Government",
            "WorldLod", "TroopAction", "SidebarType",
        }
        local mainExtraKeys = {
            {"CarMicrochipGrading", "car_microchip_grading"},
            {"NationConf", "aps_country"},
        }
        for _, key in ipairs(mainEnumKeys) do
            local t = tn[key]
            if t ~= nil and t ~= "" then
                tasks[#tasks + 1] = function() _warmXmlTable(lc, t, st) end
            end
        end
        for _, pair in ipairs(mainExtraKeys) do
            local t = tn[pair[1]] or pair[2]
            if t ~= nil and t ~= "" then
                tasks[#tasks + 1] = function() _warmXmlTable(lc, t, st) end
            end
        end

        -- Tier 2 Read-Only DataCenter.*TemplateManager singletons (msgs=0, events=0)
        local tmSpecs = {
            { "ScienceTemplateManager", function(m)
                if not m.initFinish or (type(m.scienceTemplateDic) == "table" and not next(m.scienceTemplateDic)) then
                    local ok = _warmManagerMethod(m, "TryInitAllTab", st)
                    if _warmManagerMethod(m, "TryInitAllScience", st) then ok = true end
                    if not ok then ok = _warmManagerMethod(m, "InitAllTemplate", st) end
                    if ok then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "HeroTemplateManager", function(m)
                if type(m.templateIds) ~= "table" or #m.templateIds == 0 then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "HeroLevelUpTemplateManager", function(m)
                if m.isInit ~= true and (type(m.templateDic) ~= "table" or not next(m.templateDic)) then
                    if _warmManagerMethod(m, "TransAllTemplates", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "HeroEquipTemplateManager", function(m)
                if m.isInit ~= true and (type(m.allTemplate) ~= "table" or not next(m.allTemplate)) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "CarChipTemplateManager", function(m)
                local warmed = false
                if type(m.allCarChipTemplate) ~= "table" or not next(m.allCarChipTemplate) then
                    if _warmManagerMethod(m, "InitCarChipTemplate", st) then warmed = true end
                end
                if type(m.allCarChipAttributeTemplate) ~= "table" or not next(m.allCarChipAttributeTemplate) then
                    if _warmManagerMethod(m, "InitCarChipAttributeTemplate", st) then warmed = true end
                end
                if type(m.allCarChipGradingTemplate) ~= "table" or not next(m.allCarChipGradingTemplate) then
                    if _warmManagerMethod(m, "InitCarChipGradingTemplate", st) then warmed = true end
                end
                if type(m.allCarChipPromoteTemplate) ~= "table" or not next(m.allCarChipPromoteTemplate) then
                    if _warmManagerMethod(m, "InitCarChipPromoteTemplate", st) then warmed = true end
                end
                if warmed then st.managersWarmed = st.managersWarmed + 1 end
            end },
            { "ItemTemplateManager", function(m)
                if type(m.itemDic) ~= "table" or not next(m.itemDic) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "VIPTemplateManager", function(m)
                if type(m.vipDataIds) ~= "table" or #m.vipDataIds == 0 then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "DetectEventTemplateManager", function(m)
                if type(m.detectEventTemplateDic) ~= "table" or not next(m.detectEventTemplateDic) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "DecorationTemplateManager", function(m)
                if type(m.templateDic) ~= "table" or not next(m.templateDic) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "NationTemplateManager", function(m)
                if type(m.nationsDic) ~= "table" or not next(m.nationsDic) then
                    if _warmManagerMethod(m, "InitNationDic", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "GovernmentTemplateManager", function(m)
                if m.isInit ~= true and (type(m.templateDic) ~= "table" or not next(m.templateDic)) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "MailGroupTemplateManager", function(m)
                if type(m.templateDict) ~= "table" or not next(m.templateDict) then
                    if _warmManagerMethod(m, "InitTemplateDict", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "MailShowTemplateManager", function(m)
                if type(m.templateDict) ~= "table" or not next(m.templateDict) then
                    if _warmManagerMethod(m, "InitTemplateDict", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "TroopActionTemplateManager", function(m)
                if type(m.tempDict) ~= "table" or not next(m.tempDict) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "SUSidebarTemplateManager", function(m)
                if m.isInit ~= true and (type(m.allTemplate) ~= "table" or not next(m.allTemplate)) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
            { "SUSidebarTypeTemplateManager", function(m)
                if m.isInit ~= true and (type(m.allTemplate) ~= "table" or not next(m.allTemplate)) then
                    if _warmManagerMethod(m, "InitAllTemplate", st) then st.managersWarmed = st.managersWarmed + 1 end
                end
            end },
        }
        for i = 1, #tmSpecs do
            local spec = tmSpecs[i]
            tasks[#tasks + 1] = function()
                local mgrObj = DataCenter and DataCenter[spec[1]]
                if mgrObj then spec[2](mgrObj) end
            end
        end

        -- Tier 3 Strictly Read-Only Engine Caches, Shaders & Local Assets (Main only)
        tasks[#tasks + 1] = function()
            local okSem, errSem = pcall(function()
                local sem = DataCenter and DataCenter.ShaderEffectManager
                if sem and type(sem.Startup) == "function" and (type(sem.material) ~= "table" or not next(sem.material)) then
                    sem:Startup()
                end
            end)
            if not okSem then
                st.errors[#st.errors + 1] = "ShaderEffectManager.Startup:" .. tostring(errSem)
            end
        end

        tasks[#tasks + 1] = function()
            local okFind, smgr = pcall(function()
                local s = CS and CS.GameEntry and CS.GameEntry.Shader
                if s and not IsNull(s) then return s end
                local smCls = CS and CS.ShaderManager
                if not smCls then return nil end
                local okInst, inst = pcall(function() return smCls.Instance end)
                if okInst and inst and not IsNull(inst) then return inst end
                local okGet, g = pcall(function()
                    return smCls.GetInstance and smCls:GetInstance() or nil
                end)
                if okGet and g and not IsNull(g) then return g end
                return smCls
            end)
            if not okFind then
                st.errors[#st.errors + 1] = "ShaderManager.resolve:" .. tostring(smgr)
                return
            end
            if not smgr or IsNull(smgr) then return end
            local okInit, initDone = pcall(function()
                return smgr.IsInitDone and smgr:IsInitDone() == true
            end)
            if not okInit then
                st.errors[#st.errors + 1] = "ShaderManager.IsInitDone:" .. tostring(initDone)
                return
            end
            if not initDone then return end
            local okCheck, needWarm = pcall(function()
                return smgr.IsWarmUpDone and (not smgr:IsWarmUpDone())
                    and smgr.GetCurWarmUpQueueCount and (smgr:GetCurWarmUpQueueCount() > 0)
            end)
            if not okCheck then
                st.errors[#st.errors + 1] = "ShaderManager.check:" .. tostring(needWarm)
                return
            end
            if needWarm then
                local okStart, errStart = pcall(function()
                    if smgr.StartWarmupByFrame then
                        smgr:StartWarmupByFrame()
                        return true
                    end
                    return false
                end)
                if okStart and errStart == true then
                    st.shadersStarted = true
                elseif not okStart then
                    st.errors[#st.errors + 1] = "ShaderManager.StartWarmupByFrame:" .. tostring(errStart)
                end
            end
        end

        tasks[#tasks + 1] = function()
            local okRm, rm = pcall(function()
                local r = CS and CS.GameEntry and CS.GameEntry.Resource
                if r and not IsNull(r) then return r end
                local rmCls = CS and CS.ResourceManager
                if not rmCls then return nil end
                local okInst, inst = pcall(function() return rmCls.Instance end)
                if okInst and inst and not IsNull(inst) then return inst end
                local okGet, g = pcall(function()
                    return rmCls.GetInstance and rmCls:GetInstance() or nil
                end)
                if okGet and g and not IsNull(g) then return g end
                return rmCls
            end)
            if not okRm then
                st.errors[#st.errors + 1] = "ResourceManager.resolve:" .. tostring(rm)
                return
            end
            if not rm or IsNull(rm) then return end

            local okPt, pType = pcall(function()
                return CS and CS.ResourceManager and CS.ResourceManager.PreloadType and CS.ResourceManager.PreloadType.Cache
            end)
            if not okPt then
                st.errors[#st.errors + 1] = "ResourceManager.PreloadType:" .. tostring(pType)
                pType = nil
            end

            if pType ~= nil then
                local localIcons = {
                    "Assets/Main/Sprites/LodIcon/mine_lod_metal.png",
                    "Assets/Main/Sprites/LodIcon/mine_lod_wood.png",
                    "Assets/Main/Sprites/LodIcon/mine_lod_electricity.png",
                    "Assets/Main/Sprites/LodIcon/mine_lod_money.png",
                    "Assets/Main/Sprites/LodIcon/gold_select.png",
                }
                for _, path in ipairs(localIcons) do
                    local okPre, warmed = pcall(function()
                        if rm.IsAssetDownloaded and rm.HasAsset and rm.PreloadAsset
                            and rm:IsAssetDownloaded(path) == true and rm:HasAsset(path) == true then
                            rm:PreloadAsset(path, pType, nil)
                            return true
                        end
                        return false
                    end)
                    if okPre and warmed == true then
                        st.assetsWarmed = st.assetsWarmed + 1
                    elseif not okPre then
                        st.errors[#st.errors + 1] = tostring(path) .. ":" .. tostring(warmed)
                    end
                end
            end

            local okPtm, ptm = pcall(function()
                return CS and CS.GameEntry and CS.GameEntry.ParticleTemplate
            end)
            if not okPtm then
                st.errors[#st.errors + 1] = "ParticleTemplate.resolve:" .. tostring(ptm)
                return
            end
            if ptm and not IsNull(ptm) and type(_G._hzLocalParticlePaths) == "table" then
                for _, pPath in ipairs(_G._hzLocalParticlePaths) do
                    if type(pPath) == "string" and pPath ~= "" then
                        local okWarm, warmed = pcall(function()
                            if ptm.IsWarmed and ptm.Warm and rm.IsAssetDownloaded and rm.HasAsset
                                and rm:IsAssetDownloaded(pPath) == true and rm:HasAsset(pPath) == true
                                and not ptm:IsWarmed(pPath) then
                                ptm:Warm(pPath)
                                return true
                            end
                            return false
                        end)
                        if okWarm and warmed == true then
                            st.assetsWarmed = st.assetsWarmed + 1
                        elseif not okWarm then
                            st.errors[#st.errors + 1] = tostring(pPath) .. ":" .. tostring(warmed)
                        end
                    end
                end
            end
        end
    end

    local tm = TimerManager:GetInstance()
    local warmToken = (_G._hzWarmupToken or 0) + 1
    _G._hzWarmupToken = warmToken
    local idx = 1

    local function runSlice()
        if _G._hzWarmupToken ~= warmToken then return end
        local okReady, reason = _checkPreloadReadiness()
        if not okReady then
            st.started = false
            st.skippedReason = reason
            return
        end
        if reason ~= uid then
            st.started = false
            st.skippedReason = "uid_changed"
            return
        end
        local endIdx = math.min(#tasks, idx + 1)
        while idx <= endIdx do
            local fn = tasks[idx]
            idx = idx + 1
            if fn then
                local okTask, errTask = pcall(fn)
                if not okTask then
                    st.errors[#st.errors + 1] = "slice:" .. tostring(errTask)
                end
            end
        end
        if idx > #tasks then
            st.started = false
            st.done = true
            st.skippedReason = ""
            _G._hzPreloadDone[uid] = role
            return
        end
        tm:DelayInvoke(runSlice, 0.06)
    end

    tm:DelayInvoke(runSlice, 0.06)
    return "WARMUP_SCHEDULED:" .. tostring(#tasks)
end

-- Schedule execution on Unity's native main-thread tick (10ms) outside Frida's NativeFunction SEH frame
local _FORCE_FULL_LOAD = __FORCE_FULL_LOAD_FLAG__
TimerManager:GetInstance():DelayInvoke(function()
    if _FORCE_FULL_LOAD and _G.TriggerFullMapLoad then
        local ok, res = pcall(_G.TriggerFullMapLoad, true)
        _G._LastMasterStatus = tostring(ok) .. ": " .. tostring(res)
    else
        if _G.StartBackgroundWorldPreloader then pcall(_G.StartBackgroundWorldPreloader, false) end
        local ok, res = pcall(_G.ApplyLastZWorldMaster)
        _G._LastMasterStatus = tostring(ok) .. ": " .. tostring(res)
    end
end, 0.01)

-- Post-login automatic R3 read-only preload trigger (staggered retries if UI/login is still completing)
do
    local tmPre = TimerManager:GetInstance()
    local autoTries = 0
    local autoToken = (_G._hzAutoPreloadToken or 0) + 1
    _G._hzAutoPreloadToken = autoToken
    local function tryAutoPreload()
        if _G._hzAutoPreloadToken ~= autoToken then return end
        local ok, res = pcall(_G.WarmReadOnlyEngineCaches, { role = "main" })
        if ok and res == "ALREADY_DONE" then
            return
        end
        if not ok or res ~= "IN_PROGRESS" then
            autoTries = autoTries + 1
        end
        if autoTries < 15 then
            tmPre:DelayInvoke(tryAutoPreload, 2.5)
        end
    end
    tmPre:DelayInvoke(tryAutoPreload, 1.0)
end

return _FORCE_FULL_LOAD and "SUCCESS_FULL_MAP_LOAD_SCHEDULED_V8" or "SUCCESS_SCHEDULED_MAIN_THREAD_V8"
"""

PRELOAD_TRIGGER_LUA = r"""
if _G.WarmReadOnlyEngineCaches then
    return _G.WarmReadOnlyEngineCaches({ role = "__ROLE__" })
end
if _G._FarmEcoMode then
    return "SKIPPED:farm_eco_mode"
end
return "PRELOAD_HOOK_NOT_INSTALLED"
"""

def _build_frida_js(force_full_map_load=False):
    payload = MASTER_LUA_CODE.replace("__FORCE_FULL_LOAD_FLAG__", "true" if force_full_map_load else "false")
    return r"""
const mod = Process.getModuleByName('xlua.dll');
const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
const top = nf('lua_gettop', 'int', ['pointer']);
const settop = nf('lua_settop', 'void', ['pointer', 'int']);
const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
const length = Memory.alloc(8);

function getString(L, index) {
    const p = str(L, index, length);
    const sz = Number(length.readU64());
    return sz === 0 ? '' : p.readUtf8String(sz);
}

const luaPayload = %s;

let done = false;
Interceptor.attach(mod.getExportByName('lua_pcallk'), {
    onEnter(args) {
        if (done) return;
        done = true;
        const L = args[0];
        const saved = top(L);
        try {
            const s = Memory.allocUtf8String(luaPayload);
            const loadErr = loadstring(L, s);
            if (loadErr === 0) {
                if (pcall(L, 0, 1, 0) === 0) {
                    const ret = getString(L, -1);
                    send({ type: 'result', data: ret });
                } else {
                    const err = getString(L, -1);
                    send({ type: 'error', data: err });
                }
            } else {
                const syntaxErr = getString(L, -1);
                send({ type: 'error', data: 'Syntax error: ' + syntaxErr });
            }
        } catch(e) {
            send({ type: 'error', data: e.toString() });
        } finally {
            settop(L, saved);
        }
    }
});
""" % json.dumps(payload)

FRIDA_JS = _build_frida_js(False)

_CLIENT_DISCOVERY_MOD = None

def _load_client_discovery():
    global _CLIENT_DISCOVERY_MOD
    if _CLIENT_DISCOVERY_MOD is not None:
        return _CLIENT_DISCOVERY_MOD
    disc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "client discovery.py")
    if os.path.exists(disc):
        spec = importlib.util.spec_from_file_location("client_discovery", disc)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _CLIENT_DISCOVERY_MOD = mod
            return mod
    return None

def _resolve_target(explicit_pid=None):
    if explicit_pid is not None:
        return int(explicit_pid)
    env_pid = os.environ.get("LASTZ_TARGET_PID", "").strip()
    if env_pid.isdigit():
        return int(env_pid)
    try:
        mod = _load_client_discovery()
        if mod is not None:
            resolved = mod.resolve_target_pid()
            if resolved:
                return resolved
    except Exception:
        pass
    return None


def resolve_runtime_cache_dir():
    env_data_dir = os.environ.get("HEINZ_DATA_DIR", "").strip()
    if env_data_dir:
        return os.path.abspath(os.path.join(env_data_dir, "cache"))
    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache")
    )


def build_master_lua_payload(force_full_map_load=False, cache_dir=None):
    body = MASTER_LUA_CODE.replace("__FORCE_FULL_LOAD_FLAG__", "true" if force_full_map_load else "false")
    if cache_dir:
        norm_dir = str(cache_dir).replace("\\", "/").rstrip("/")
        if norm_dir:
            return f"_G._MasterCacheDirOverride = {json.dumps(norm_dir)}\n" + body
    return body


def main(pid=None, full_map_load=False):
    target_pid = _resolve_target(pid)
    if not target_pid:
        print("[-] No running Last Z client found")
        return False
    cache_dir = ""
    try:
        cache_dir = resolve_runtime_cache_dir()
        os.makedirs(cache_dir, exist_ok=True)
    except Exception:
        pass

    try:
        import psutil
        psutil.Process(target_pid).nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception:
        pass

    cd = _load_client_discovery()
    if cd is None:
        print("[-] Could not load client discovery module")
        return False
    if hasattr(cd, "_xlua_loaded") and not cd._xlua_loaded(int(target_pid)):
        print("[-] Target client is still booting (xlua.dll not loaded)")
        return False

    payload = build_master_lua_payload(force_full_map_load=full_map_load, cache_dir=cache_dir)
    ok, res = cd.frida_eval_lua(int(target_pid), payload, timeout=10.0, retries=2)
    if ok:
        print(f"[+] Result: {res}")
        return True
    print(f"[-] Error: {res}")
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apply hardware FPS and world map optimizations to a Last Z client.")
    parser.add_argument("--pid", type=int, default=None, help="Target process PID")
    parser.add_argument("--full-map-load", action="store_true", help="Force-trigger an immediate full 1000x1000 world map sweep & build")
    args = parser.parse_args()
    ok = main(pid=args.pid, full_map_load=args.full_map_load)
    sys.exit(0 if ok else 1)
