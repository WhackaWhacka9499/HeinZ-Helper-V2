-- Last Z master engine overhaul v7.8

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

_G._PersistentWorldPointCache = _G._PersistentWorldPointCache or {}
_G._PersistentDesertCache = _G._PersistentDesertCache or {}
_G._MonsterIdSet = _G._MonsterIdSet or {}
_G._DynamicBuildIdSet = _G._DynamicBuildIdSet or {}

local _CACHE_FILE_PATH = "./data/cache/world_map_cache.json"

function _G.SaveWorldCacheToDisk()
    pcall(function()
        local cache = _G._PersistentWorldPointCache
        if not cache or not next(cache) then return end
        local rjson = pcall(require, "rapidjson") and require("rapidjson")
        if not rjson then return end
        local exportObj = {}
        for k, v in pairs(cache) do
            exportObj[tostring(k)] = v
        end
        local encoded = rjson.encode(exportObj)
        local f = io.open(_CACHE_FILE_PATH, "w")
        if f then
            f:write(encoded)
            f:close()
        end
    end)
end

function _G.LoadWorldCacheFromDisk()
    pcall(function()
        local rjson = pcall(require, "rapidjson") and require("rapidjson")
        if not rjson then return end
        local f = io.open(_CACHE_FILE_PATH, "r")
        if not f then return end
        local content = f:read("*a")
        f:close()
        if not content or #content < 5 then return end
        local decoded = rjson.decode(content)
        if type(decoded) == "table" then
            for kStr, v in pairs(decoded) do
                local kNum = tonumber(kStr)
                if kNum then
                    _G._PersistentWorldPointCache[kNum] = v
                end
            end
        end
    end)
end

if SafeTableCount(_G._PersistentWorldPointCache) == 0 then
    _G.LoadWorldCacheFromDisk()
end

local function FastIndexToXY(pointIndex)
    local tw = TileCountX or 1000
    local z = pointIndex - 1
    local py = math.floor(z / tw)
    return z - py * tw, py
end

function _G.RestoreWorldMapCache()
    local mgr = DataCenter and DataCenter.WorldPointManager
    if not mgr then return end
    mgr.allViewPoints = mgr.allViewPoints or {}
    local v2 = CS and CS.UnityEngine and CS.UnityEngine.Vector2
    for k, pi in pairs(_G._PersistentWorldPointCache or {}) do
        local entry = mgr.allViewPoints[k]
        local pType = (type(pi) == "table" and (pi.pointType or pi.PointType)) or 0
        local px, py = FastIndexToXY(k)
        local mv2 = v2 and v2(px, py) or nil
        if not entry then
            mgr.allViewPoints[k] = {
                pointIndex = k,
                mainIndex = (type(pi) == "table" and (pi.mainIndex or pi.id)) or k,
                mainIndexV2 = mv2,
                pointType = pType,
                pointInfo = pi
            }
        else
            entry.pointInfo = pi
            if entry.pointType == nil or entry.pointType == 0 then entry.pointType = pType end
            if entry.mainIndex == nil then entry.mainIndex = k end
            if entry.mainIndexV2 == nil and mv2 then entry.mainIndexV2 = mv2 end
        end
    end
    for k, di in pairs(_G._PersistentDesertCache or {}) do
        local entry = mgr.allViewPoints[k]
        local px, py = FastIndexToXY(k)
        local mv2 = v2 and v2(px, py) or nil
        if not entry then
            mgr.allViewPoints[k] = {
                pointIndex = k,
                mainIndex = k,
                mainIndexV2 = mv2,
                desertInfo = di
            }
        else
            entry.desertInfo = di
            if entry.mainIndexV2 == nil and mv2 then entry.mainIndexV2 = mv2 end
        end
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
    if not pi then return "ZOMBIE" end
    local mi = pi.monsterInfo or pi._parsedExtra or entry._parsedExtra
    if not mi and pi.extraInfo and PBController and PBController.ParsePbFromBytes then
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

function _G.RefreshMasterOverlayUI()
    local um = UIManager and UIManager:GetInstance()
    if not um or not um.m_topCanvas or IsNull(um.m_topCanvas) then return end
    local parentRect = um.m_topCanvas
    local uiLayer = parentRect.gameObject and parentRect.gameObject.layer or 5

    local barGo = _G._MasterOverlayBarGo
    local tmp = _G._MasterOverlayTmp
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
        barRect.sizeDelta = CS.UnityEngine.Vector2(820, 32)

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
    end

    local t = _G._MasterToggles
    local showBar = (t.showOverlay ~= false)
    if barGo.activeSelf ~= showBar then
        barGo:SetActive(showBar)
    end
    if not showBar then return end

    barGo.transform:SetAsLastSibling()
    local function badge(val)
        return val and "<color=#4ADE80>ON</color>" or "<color=#F87171>OFF</color>"
    end
    tmp.text = string.format(
        "<b><color=#38BDF8>LAST Z PC</color></b>  |  <b>[F1] Map:</b> %s  |  <b>[F2] Zombies:</b> %s  |  <b>[F3] Res:</b> %s  |  <b>[F4] Boomers:</b> %s  |  <b>[F5] HQs:</b> %s  |  <color=#94A3B8>[Home] Hide</color>",
        badge(t.masterEnabled),
        badge(t.showZombies),
        badge(t.showResources),
        badge(t.showBoomers),
        badge(t.showHQs)
    )
end

local function FastIndexToXY(pointIndex)
    local tw = TileCountX or 1000
    local z = pointIndex - 1
    local py = math.floor(z / tw)
    return z - py * tw, py
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

function _G.ApplyLastZWorldMaster()
    local app = CS.UnityEngine.Application
    local qs = CS.UnityEngine.QualitySettings
    local mgr = DataCenter and DataCenter.WorldPointManager
    local ws = SceneManager and SceneManager.World

    -- Hardware graphics (144 fps focused, 30 fps background, 2x msaa)
    if app then
        app.targetFrameRate = 180
    end
    if qs then
        qs.vSyncCount = 0
        qs.anisotropicFiltering = CS.UnityEngine.AnisotropicFiltering.ForceEnable
        qs.antiAliasing = 2
        qs.shadows = CS.UnityEngine.ShadowQuality.All
        qs.shadowCascades = 2
        qs.shadowDistance = 120.0
        qs.shadowNearPlaneOffset = 0.8
        qs.shadowResolution = CS.UnityEngine.ShadowResolution.High
        qs.asyncUploadTimeSlice = 16
        qs.asyncUploadBufferSize = 256
        qs.asyncUploadPersistentBuffer = true
        qs.lodBias = 2.5
        qs.maximumLODLevel = 0
    end

    local gs = CS.UnityEngine.Rendering and CS.UnityEngine.Rendering.GraphicsSettings
    local rp = gs and (gs.currentRenderPipeline or gs.renderPipelineAsset)
    if not IsNull(rp) then
        rp.shadowDistance = 120.0
        rp.shadowCascadeCount = 2
        rp.shadowDepthBias = 1.2
        rp.shadowNormalBias = 1.2
        rp.msaaSampleCount = 2
        local flags = CS.System.Reflection.BindingFlags
        local toInt = CS.System.Convert.ToInt32
        local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)
        local fRes = rp:GetType():GetField("m_MainLightShadowmapResolution", allFlags)
        if fRes then
            local v2048 = CS.System.Enum.ToObject(fRes.FieldType, toInt(2048))
            fRes:SetValue(rp, v2048)
        end
    end

    local qsu = require and require("Util.QualitySettingUtil")
    if qsu then
        qsu.OnLowFps = function() end
        local origSetGraphicQuality = qsu.SetGraphicQuality
        qsu.SetGraphicQuality = function(...)
            if origSetGraphicQuality then pcall(origSetGraphicQuality, ...) end
            if app then app.targetFrameRate = 180 end
            if qs then qs.vSyncCount = 0 end
        end
    end

    collectgarbage("setpause", 200)
    collectgarbage("setstepmul", 200)

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
    local flags = CS.System.Reflection.BindingFlags
    local toInt = CS.System.Convert.ToInt32
    local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)

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

        local f_params = tc:GetType():GetField("zoomParams", allFlags)
        local zparams = f_params and f_params:GetValue(tc)
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

    -- Smart adjuster expander

    local function expandAdjuster(adj)
        if not adj or IsNull(adj) then return false end
        local f = adj:GetType():GetField("settings", allFlags)
        local arr = f and f:GetValue(adj)
        if not arr or arr.Length == 0 then return false end
        local settingType = arr:GetType():GetElementType()
        local tF = settingType:GetField("targets", allFlags)
        local lF = settingType:GetField("showLods", allFlags)

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
                            llist:Add(toInt(1))
                            llist:Add(toInt(2))
                        elseif tname == "Icon" or tname == "IconHouse" or tname == "IconNormal" or tname == "FarIcon" or tname == "lodSetObj" then
                            llist:Clear()
                            for l = 3, 12 do llist:Add(toInt(l)) end
                        elseif tname == "NameLabel" or tname == "LevelLabel" or string.find(tname, "Near") or string.find(tname, "ModelHead") or tname == "ModelLabel" or string.find(tname, "Far") or string.find(tname, "IconHead") or tname == "IconLabel" then
                            llist:Clear()
                            for l = 1, 12 do llist:Add(toInt(l)) end
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

    local function optimizeInstance(inst)
        if IsNull(inst) then return end
        local animators = inst:GetComponentsInChildren(typeof(CS.UnityEngine.Animator), true)
        if animators then
            for i = 0, animators.Length - 1 do
                animators[i].cullingMode = CS.UnityEngine.AnimatorCullingMode.CullUpdateTransforms
            end
        end
        local particles = inst:GetComponentsInChildren(typeof(CS.UnityEngine.ParticleSystem), true)
        if particles then
            for i = 0, particles.Length - 1 do
                particles[i].cullingMode = CS.UnityEngine.ParticleSystemCullingMode.Pause
            end
        end
        local renderers = inst:GetComponentsInChildren(typeof(CS.UnityEngine.Renderer), true)
        if renderers then
            for i = 0, renderers.Length - 1 do
                local sm = renderers[i].sharedMaterial
                if not IsNull(sm) and not IsNull(sm.shader) then
                    local sName = sm.shader.name or ""
                    if string.find(sName, "Instanc") or string.find(sName, "Standard") or string.find(sName, "Universal") or string.find(sName, "URP") then
                        sm.enableInstancing = true
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
            if nil == self.cachedWorldPos then
                self.cachedWorldPos = SceneUtils.TileIndexToWorld(self.pointIndex, ForceChangeScene.World)
            end
            if nil == self.cachedWorldPos then return end

            local iconRenderer = mgr and mgr:GetIconRenderer()
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

    local ok_wir, wir = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldInstancedRepresentation")
    if ok_wir and wir then
        wir.RefreshInstancedFarIcon = function(self, info, forceAll)
            local path = self:_GetFarIconPath(info)
            local cfg = self:_GetFarIconConfig(info)
            if nil == path or "" == path then return end
            if nil == self.cachedWorldPos then
                self.cachedWorldPos = SceneUtils.TileIndexToWorld(self.pointIndex, ForceChangeScene.World)
            end
            if nil == self.cachedWorldPos then return end

            local iconRenderer = mgr and mgr:GetIconRenderer()
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
        wir._InstancedOnLodChanged = fastInstancedLodChange
    end
    if ok_wroi and wroi then
        wroi._ApplyInstancedLodState = applySmartInstancedLodState
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
                    self.adjuster = self.gameObject:GetComponent(typeof(CS.AutoAdjustLod))
                end
                if self.adjuster and not IsNull(self.adjuster) then
                    expandAdjuster(self.adjuster)
                    self.adjuster:UpdateLod((mgr and mgr.lodLv) or 1)
                end
                if info then pcall(self.SetBuildIconColor, self, info) end
            end

            local origOnMainModelLoaded = wbo.OnMainModelLoaded
            wbo.OnMainModelLoaded = function(self, ...)
                if origOnMainModelLoaded then pcall(origOnMainModelLoaded, self, ...) end
                optimizeInstance(self.instance)
            end

            wbo.CheckIdleShowAnim = function(self) end
            wbo.OnRandomNextIdleAnim = function(self) end
            wbo.RandomNextPlayIdleTime = function(self) return 999999 end

            local origSetProtectRenderVisible = wbo.SetProtectRenderVisible
            wbo.SetProtectRenderVisible = function(self, isVisible)
                local info = mgr and mgr:GetPointInfo(self.pointIndex)
                local bi = info and info.buildInfo
                local now = os.time()
                local hasShield = bi and bi.protectEndTime and (bi.protectEndTime > now)

                if hasShield then
                    if origSetProtectRenderVisible then pcall(origSetProtectRenderVisible, self, true) end
                    if self.protectRender and not IsNull(self.protectRender) then
                        if self.cachedWorldPos and self.protectRender.transform then
                            self.protectRender.transform.position = self.cachedWorldPos
                            local curLod = (mgr and mgr.lodLv) or 1
                            if curLod >= 4 then
                                self.protectRender.transform.localScale = CS.UnityEngine.Vector3(2.5, 2.5, 2.5)
                            else
                                self.protectRender.transform.localScale = CS.UnityEngine.Vector3.one
                            end
                        end
                        local prMesh = self.protectRender:GetComponent(typeof(CS.UnityEngine.Renderer))
                        if not IsNull(prMesh) then
                            prMesh.shadowCastingMode = CS.UnityEngine.Rendering.ShadowCastingMode.Off
                            prMesh.receiveShadows = false
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
                if lod <= 2 and not self.instance and self.CreateMain then
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

    -- Zombies and monsters overhaul
    local ok_wmo, wmo = pcall(require, "SlgEngine.DataCenter.WorldPointManager.WorldMonsterObject")
    if ok_wmo and wmo and not wmo.__masterMonsterHooked then
        wmo.__masterMonsterHooked = true

        -- Always show Zombie 2D FarIcon & Level Label at LOD 3..12 without needing the Monster filter tab selected!
        wmo.RefreshLodType = function(self)
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

        -- Skip expensive 3D skeletal animations on Zombies when zoomed out to 2D icons (lodLv >= 3)
        local origPlayAnim = wmo.PlayAnim
        if origPlayAnim then
            wmo.PlayAnim = function(self, animName, ...)
                local curLod = (mgr and mgr.lodLv) or 1
                if curLod >= 3 and animName == "idle" then
                    return
                end
                return origPlayAnim(self, animName, ...)
            end
        end
    end

    -- Tiered streaming and persistent cache
    -- Tiered Strategy (Zero Icon Deletion + Low RAM/CPU):
    --   - Resource Nodes (7), Radar Events (22), Cities (11), Alliance Centers (15), Bosses, Treasures:
    --     100% Global across the entire 1000x1000 map, NEVER evicted!
    --   - Real Player HQs (pType == 6, IsSmallBuild == false, ~3,295 total):
    --     380-tile build radius (760x760 box), 520-tile evict radius (1040x1040 box -> NEVER evicted once built!).
    --   - Small Seasonal Virus Buildings (pType == 6, IsSmallBuild == true, ~7,784 total):
    --     180-tile build radius (360x360 box), 250-tile evict radius (500x500 box).
    --   - Wandering Zombies (pType == 4, non-Boss, ~14,740 heavy SkinnedMeshRenderer prefabs):
    --     175-tile build radius (350x350 box), 245-tile evict radius (490x490 box).
    local function ShouldBuildPointNow(selfMgr, pointIndex, entry, camX, camY, isEvictCheck)
        if type(entry) ~= "table" then return false end
        local toggles = _G._MasterToggles
        local px, py = FastIndexToXY(pointIndex)
        local dist = math.max(math.abs(px - camX), math.abs(py - camY))

        if toggles and toggles.masterEnabled == false then
            return dist <= (isEvictCheck and 48 or 38)
        end

        local pi = entry.pointInfo
        if not pi then
            -- Desert-only decoration tile
            return dist <= (isEvictCheck and 110 or 80)
        end

        local pType = entry.pointType or pi.PointType or pi.pointType or -1
        if pType == 4 then
            local mCat = GetMonsterCategory(entry)
            if mCat == "BOOMER" or mCat == "BOSS" then
                if toggles and toggles.showBoomers == false then return false end
                if mCat == "BOSS" then return true end
                return dist <= (isEvictCheck and 310 or 230)
            else
                if toggles and toggles.showZombies == false then return false end
                return dist <= (isEvictCheck and 240 or 170)
            end
        elseif pType == 7 then
            if toggles and toggles.showResources == false then return false end
            return true
        elseif pType == 6 then
            if toggles and toggles.showHQs == false then return false end
            local isSmall = entry._isSmallBuild
            if isSmall == nil then
                local bid = selfMgr._GetBuildIdForFactory and selfMgr:_GetBuildIdForFactory(entry)
                isSmall = (bid ~= nil and selfMgr.IsSmallBuild and selfMgr:IsSmallBuild(bid)) and true or false
                entry._isSmallBuild = isSmall
            end
            if isSmall then
                return dist <= (isEvictCheck and 250 or 180)
            else
                return dist <= (isEvictCheck and 520 or 380)
            end
        end

        -- All other point types (Radar 22, Cities 11, Alliance 15, Treasures, Ice Caves):
        -- Always built globally across 100% of the map and NEVER evicted!
        return true
    end

    mgr.aoiOptimizeEnabled = true
    mgr.aoiReconcileEnabled = false
    mgr.outOfViewOffX = 100000

    -- Patch upvalues across WorldPointManager methods (BuildAsync LOD gates & ViewLevelRange boxes)
    local function patchWpmTableUpvalues(tbl)
        if type(tbl) ~= "table" or not debug or not debug.getupvalue or not debug.setupvalue then return end
        for _, fn in pairs(tbl) do
            if type(fn) == "function" then
                for uIdx = 1, 20 do
                    local uName, uVal = debug.getupvalue(fn, uIdx)
                    if not uName then break end
                    if uName == "OtherPointLod" or uName == "SelfPointLod" or uName == "OtherPlayerLod" or uName == "NightSacrificeLod" or uName == "DesertPointLod" then
                        debug.setupvalue(fn, uIdx, 20)
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
                    end
                end
            end
        end
    end

    patchWpmTableUpvalues(mgr)
    local mgrMt = getmetatable(mgr)
    if mgrMt and type(mgrMt.__index) == "table" then
        patchWpmTableUpvalues(mgrMt.__index)
    end

    mgr.GetViewBounds = function(self, padX, padY)
        return -100000, 100000, -100000, 100000
    end
    mgr.IsOutOfRange = function(self, ...)
        return false
    end
    mgr.IsOutOfRange2 = function(self, x, y, minX, maxX, minY, maxY)
        if x and y then
            local tw = TileCountX or 1000
            local pIdx = y * tw + x + 1
            local entry = self.allViewPoints and self.allViewPoints[pIdx]
            if entry then
                local camX, camY = GetActualCameraTilePos(self, SceneManager and SceneManager.World)
                return not ShouldBuildPointNow(self, pIdx, entry, camX, camY, false)
            end
        end
        return false
    end

    -- Always request svLod = 0 (Full Detail: Resources, Zombies, Bases, Events) from server
    mgr.GetServerLod = function(self, lod)
        return 0
    end

    -- Never skip unbuilt points during continuous AOI version checks
    mgr.SkipWorldPointForContinuesAoiVersion = function(self, pointId)
        if not self.aoiOptimizeEnabled then return false end
        local pi = self:GetPointInfo(pointId)
        local obj = self:GetObjectByPoint(pointId)
        if pi ~= nil and obj ~= nil then
            return true
        end
        return false
    end

    -- Smooth, zero-stutter frame budgets for DoParse (35/frame) and BuildAsync (12/frame)
    local _parseFrame = -1
    local _parseCount = 0
    mgr.IsBusy = function(self)
        local f = CS.UnityEngine.Time.frameCount
        if f ~= _parseFrame then
            _parseFrame = f
            _parseCount = 0
        end
        _parseCount = _parseCount + 1
        return _parseCount > 35
    end

    local _buildFrame = -1
    local _buildCount = 0
    mgr.IsSyncBusy = function(self)
        local f = CS.UnityEngine.Time.frameCount
        if f ~= _buildFrame then
            _buildFrame = f
            _buildCount = 0
        end
        _buildCount = _buildCount + 1
        local qLen = (self.toBuildList and #self.toBuildList) or 0
        local limit = (qLen > 50) and 100 or 30
        return _buildCount > limit
    end

    mgr.ReconcileAoiPoints = function(self, newIdSet, newCount)
        if not self.aoiPointIdSet then self.aoiPointIdSet = newIdSet or {}
        else for k in pairs(newIdSet or {}) do self.aoiPointIdSet[k] = true end end
    end
    mgr.ReconcileAoiDeserts = function(self, newIdSet, newCount)
        if not self.aoiDesertIdSet then self.aoiDesertIdSet = newIdSet or {}
        else for k in pairs(newIdSet or {}) do self.aoiDesertIdSet[k] = true end end
    end

    -- Persistent Cache Lifecycle Hooks (Never wipe viewpoints across scene switches)
    local proto = getmetatable(mgr) and getmetatable(mgr).__index or mgr
    if proto and not proto._masterCacheLifecycleHooked then
        proto._masterCacheLifecycleHooked = true

        local origClose = proto.Close
        proto.Close = function(self, ...)
            if self.allViewPoints then
                for k, v in pairs(self.allViewPoints) do
                    if type(v) == "table" then
                        if v.pointInfo ~= nil then _G._PersistentWorldPointCache[k] = v.pointInfo end
                        if v.desertInfo ~= nil then _G._PersistentDesertCache[k] = v.desertInfo end
                    end
                end
            end
            _G.SaveWorldCacheToDisk()
            return origClose(self, ...)
        end

        local origStartUp = proto.StartUp
        proto.StartUp = function(self, ...)
            local res = origStartUp(self, ...)
            pcall(_G.RestoreWorldMapCache)
            return res
        end

        local origAddPointInfo = proto.AddPointInfo
        if origAddPointInfo then
            proto.AddPointInfo = function(self, pointIndex, info, ...)
                if pointIndex and info then
                    _G._PersistentWorldPointCache[pointIndex] = info
                    if self.allViewPoints and not self.allViewPoints[pointIndex] then
                        self.allViewPoints[pointIndex] = { pointIndex = pointIndex, pointInfo = info }
                    end
                end
                return origAddPointInfo(self, pointIndex, info, ...)
            end
        end

        local origAddDesertInfo = proto.AddDesertInfo
        if origAddDesertInfo then
            proto.AddDesertInfo = function(self, pointIndex, info, ...)
                if pointIndex and info then
                    _G._PersistentDesertCache[pointIndex] = info
                    if self.allViewPoints and not self.allViewPoints[pointIndex] then
                        self.allViewPoints[pointIndex] = { pointIndex = pointIndex, desertInfo = info }
                    end
                end
                return origAddDesertInfo(self, pointIndex, info, ...)
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
                return origRemovePointInfo(self, pointIndex, true, false)
            end
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

    -- Restore all cached viewpoints from persistent memory/disk
    pcall(_G.RestoreWorldMapCache)

    -- Preload and stream in all unbuilt points across the world map
    local initCamX, initCamY = GetActualCameraTilePos(mgr, ws)
    if mgr.isInit == true and mgr.allViewPoints then
        for k, v in pairs(mgr.allViewPoints) do
            if type(v) == "table" and (v.pointInfo ~= nil or v.desertInfo ~= nil) then
                if not (mgr.allObj and mgr.allObj[k]) and not (mgr.toBuildSet and mgr.toBuildSet[k]) then
                    if ShouldBuildPointNow(mgr, k, v, initCamX, initCamY, false) then
                        if mgr.AddToBuildList then mgr:AddToBuildList(k) end
                    end
                end
            end
        end
    end

    if not (mgr and mgr.isInit == true) then
        mgr._masterAppliedForThisWorldSession = false
        return "HOOKS_READY_WAITING_FOR_WORLD_VIEW"
    end

    -- Clean any dead GameObjects that might have been left over in allObj
    if mgr.allObj then
        for k, obj in pairs(mgr.allObj) do
            if not obj or not obj.gameObject or IsNull(obj.gameObject) then
                mgr.allObj[k] = nil
            end
        end
    end

    -- Camera streamer: remove any legacy per-frame AfterUpdate hook that caused frame lag or moved transforms
    if ws and ws.Camera then
        local afterTbl = ws.Camera.AfterUpdate or ws.Camera.AfterUpdateAction
        if type(afterTbl) == "table" then
            afterTbl["Proximity3DGate"] = nil
        end
    end

    _G.ApplyToggleChangeImmediate = function()
        pcall(_G.RefreshMasterOverlayUI)
    end

    -- Refresh existing objects
    local now = os.time()
    for k, obj in pairs(mgr.allObj or {}) do
        if obj.adjuster and not IsNull(obj.adjuster) then
            expandAdjuster(obj.adjuster)
        end
        local cname = (obj._class_type and obj._class_type.__cname) or ""
        local info = mgr:GetPointInfo(obj.pointIndex)
        if cname == "WorldBuildObject" and info then
            pcall(obj.SetBuildIconColor, obj, info)
            local bi = info.buildInfo
            if bi and bi.protectEndTime and (bi.protectEndTime > now) then
                pcall(obj.SetProtectRenderVisible, obj, true)
            end
        elseif cname == "WorldMonsterObject" then
            pcall(obj.RefreshLodType, obj)
        elseif cname == "WorldResObjectInstanced" and info then
            obj._ApplyInstancedLodState = applySmartInstancedLodState
            pcall(obj._ApplyInstancedLodState, obj, info, false)
        end
    end

    -- Ensure background preloader is continuously sweeping and parsing world data
    if _G.StartBackgroundWorldPreloader then
        pcall(_G.StartBackgroundWorldPreloader)
    end

    mgr._masterAppliedForThisWorldSession = true
    pcall(_G.RefreshMasterOverlayUI)

    local totalPts = 0
    if mgr.allViewPoints then for _ in pairs(mgr.allViewPoints) do totalPts = totalPts + 1 end end
    local totalObjs = 0
    if mgr.allObj then for _ in pairs(mgr.allObj) do totalObjs = totalObjs + 1 end end

    return string.format("SUCCESS_MASTER_V7_7_HOTKEYS_SMOOTH (cachedPoints=%d, activeObj=%d)", totalPts, totalObjs)
end


function _G.StartBackgroundWorldPreloader()
    local mgr = DataCenter and DataCenter.WorldPointManager
    if not mgr or not TimerManager or not LuaEntry or not LuaEntry.Player then return end
    if mgr._bgSweepActive then return end
    mgr._bgSweepActive = true

    local tmManager = TimerManager:GetInstance()
    local serverId = LuaEntry.Player:GetSelfServerId()
    if not serverId then return end

    local maxTileX = (TileCountX or 1000) - 30
    local maxTileY = (TileCountY or 1000) - 30
    local startX, startY = 500, 500

    local p = LuaEntry.Player
    local bm = DataCenter.BuildManager
    local myHqIndex = (p and p.cityPointIndex) or (bm and bm.CityPointIndex) or 500500
    if SceneUtils and SceneUtils.IndexToTileXY then
        local hx, hy = SceneUtils.IndexToTileXY(myHqIndex)
        if hx and hy and hx > 0 and hy > 0 then startX, startY = hx, hy end
    end

    local gridStepX = 70
    local gridStepY = 60
    local allSectors = {}
    for gx = 30, maxTileX, gridStepX do
        for gy = 30, maxTileY, gridStepY do
            local dist = math.max(math.abs(gx - startX), math.abs(gy - startY))
            table.insert(allSectors, { x = gx, y = gy, d = dist })
        end
    end
    table.sort(allSectors, function(a, b) return a.d < b.d end)

    local sweepToken = (mgr._bgSweepToken or 0) + 1
    mgr._bgSweepToken = sweepToken
    local sIdx = 1
    local dirtyTicks = 0

    local function sStep()
        if mgr._bgSweepToken ~= sweepToken then return end
        if _G._MasterToggles and _G._MasterToggles.masterEnabled == false then
            tmManager:DelayInvoke(sStep, 1.0)
            return
        end

        local curWs = SceneManager and SceneManager.World
        local realCamX, realCamY = nil, nil
        if curWs and curWs.Camera and mgr.isInit == true then
            realCamX, realCamY = GetActualCameraTilePos(mgr, curWs)
        end

        if sIdx <= #allSectors then
            local sec = allSectors[sIdx]
            sIdx = sIdx + 1
            mgr.waitingForReply = false
            mgr:DoSendViewRequest(sec.x, sec.y, 0, serverId)

            if realCamX and realCamY and mgr.reqPos and mgr.reqPos.Set then
                mgr.reqPos:Set(realCamX, realCamY)
            end

            dirtyTicks = dirtyTicks + 1
            if dirtyTicks >= 40 then
                dirtyTicks = 0
                _G.SaveWorldCacheToDisk()
            end
            tmManager:DelayInvoke(sStep, 0.35)
        else
            -- Completed full 1000x1000 world map sweep. Flush disk cache, rest for 60s, then repeat for live changes
            _G.SaveWorldCacheToDisk()
            sIdx = 1
            tmManager:DelayInvoke(sStep, 60.0)
        end
    end
    sStep()

    -- Continuous parser pump so incoming packets are decoded even while in City view
    local pumpToken = (mgr._bgPumpToken or 0) + 1
    mgr._bgPumpToken = pumpToken
    local function sPump()
        if mgr._bgPumpToken ~= pumpToken then return end
        pcall(function()
            if mgr.ParseServerDataAsync then
                mgr:ParseServerDataAsync()
            end
        end)
        tmManager:DelayInvoke(sPump, 0.10)
    end
    sPump()
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

    -- Fast 40Hz (0.025s) Hotkey Poller for F1..F5 and Home
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
        { code = kc.Home, field = "showOverlay",   isWorldToggle = false },
    }

    local function pollHotkeys()
        if _G._masterHotkeyToken ~= hkToken then return end
        pcall(function()
            if not inp or not _G._MasterToggles then return end
            local prev = _G._keyPrevState
            for i = 1, #KEY_BINDINGS do
                local b = KEY_BINDINGS[i]
                local isDown = inp.GetKey(b.code) or inp.GetKeyDown(b.code)
                if isDown and not prev[b.field] then
                    prev[b.field] = true
                    _G._MasterToggles[b.field] = not _G._MasterToggles[b.field]
                    if b.isWorldToggle and _G.ApplyToggleChangeImmediate then
                        _G.ApplyToggleChangeImmediate()
                    else
                        pcall(_G.RefreshMasterOverlayUI)
                    end
                elseif not isDown and prev[b.field] then
                    prev[b.field] = false
                end
            end
        end)
        tmManager:DelayInvoke(pollHotkeys, 0.025)
    end
    tmManager:DelayInvoke(pollHotkeys, 0.025)

    local hbToken = (_G._masterHeartbeatToken or 0) + 1
    _G._masterHeartbeatToken = hbToken
    local function hb()
        if _G._masterHeartbeatToken ~= hbToken then return end
        pcall(function()
            pcall(_G.RefreshMasterOverlayUI)
            local curApp = CS.UnityEngine.Application
            local curQs = CS.UnityEngine.QualitySettings
            local curTp = CS.UnityEngine.ThreadPriority
            if curApp then
                local targetFps = 180
                if curApp.targetFrameRate ~= targetFps then curApp.targetFrameRate = targetFps end
                if curTp and curApp.backgroundLoadingPriority ~= curTp.High then curApp.backgroundLoadingPriority = curTp.High end
            end
            if curQs then
                if curQs.vSyncCount ~= 0 then curQs.vSyncCount = 0 end
                if curQs.maxQueuedFrames ~= 2 then curQs.maxQueuedFrames = 2 end
                if curQs.shadowDistance ~= 35.0 then curQs.shadowDistance = 35.0 end
                if curQs.asyncUploadTimeSlice ~= 4 then curQs.asyncUploadTimeSlice = 4 end
                if curQs.asyncUploadBufferSize ~= 512 then curQs.asyncUploadBufferSize = 512 end
                if curQs.realtimeReflectionProbes ~= false then curQs.realtimeReflectionProbes = false end
                if curQs.antiAliasing ~= 2 then curQs.antiAliasing = 2 end
            end

            local curWs = SceneManager and SceneManager.World
            if curWs and curWs.Camera and curWs.Camera.camera and not IsNull(curWs.Camera.camera) then
                curWs.Camera.camera.farClipPlane = 12000.0
                curWs.Camera.camera.nearClipPlane = 20.0
            end

            -- Auto-detect World View session
            local curMgr = DataCenter and DataCenter.WorldPointManager
            local isNowInWorld = (curMgr and curMgr.isInit == true)
            if isNowInWorld then
                if not curMgr._masterAppliedForThisWorldSession or curMgr:GetServerLod(6) ~= 0 then
                    if _G.ApplyLastZWorldMaster then
                        local ok, res = pcall(_G.ApplyLastZWorldMaster)
                        _G._LastMasterStatus = tostring(ok) .. ": " .. tostring(res)
                    end
                end
            elseif curMgr then
                curMgr._masterAppliedForThisWorldSession = false
            end
        end)

        -- Silent Helicopter Auto-Assist (Instant Help All)
        pcall(function()
            local ahm = DataCenter and DataCenter.AllianceHelpDataManager
            if ahm and ahm.GetHelpNum and ahm:GetHelpNum() > 0 then
                ahm:OnHelpAll()
            end
        end)

        collectgarbage("step", 60)
        tmManager:DelayInvoke(hb, 1.5)
    end
    tmManager:DelayInvoke(hb, 0.05)

    -- Dynamic Spatial Viewport Streamer: 180 FPS locked + zero pop-in + full map streaming
    local streamToken = (_G._masterStreamToken or 0) + 1
    _G._masterStreamToken = streamToken
    local lastStreamCamX, lastStreamCamY = -1, -1

    local function runCameraStreamer()
        if _G._masterStreamToken ~= streamToken then return end
        pcall(function()
            local curMgr = DataCenter and DataCenter.WorldPointManager
            local curWs = SceneManager and SceneManager.World
            if not (curMgr and curMgr.isInit == true) then return end

            local camX, camY = GetActualCameraTilePos(curMgr, curWs)
            local moved = (math.abs(camX - lastStreamCamX) >= 6 or math.abs(camY - lastStreamCamY) >= 6)
            if not moved and curMgr.allObj and next(curMgr.allObj) ~= nil then return end
            lastStreamCamX = camX
            lastStreamCamY = camY

            -- Ensure all built objects remain active for full-map visibility
            if curMgr.allObj then
                for k, v in pairs(curMgr.allObj) do
                    if v.gameObject and not IsNull(v.gameObject) and not v.gameObject.activeSelf then
                        v.gameObject:SetActive(true)
                    end
                end
            end

            -- Stream in newly visible points according to ShouldBuildPointNow
            if curMgr.allViewPoints and curMgr.AddToBuildList then
                local queuedThisTick = 0
                for k, v in pairs(curMgr.allViewPoints) do
                    if type(v) == "table" and (v.pointInfo ~= nil or v.desertInfo ~= nil) then
                        if not (curMgr.allObj and curMgr.allObj[k]) and not (curMgr.toBuildSet and curMgr.toBuildSet[k]) then
                            if ShouldBuildPointNow(curMgr, k, v, camX, camY, false) then
                                curMgr:AddToBuildList(k)
                                queuedThisTick = queuedThisTick + 1
                                if queuedThisTick >= 150 then break end
                            end
                        end
                    end
                end
            end
        end)
        tmManager:DelayInvoke(runCameraStreamer, 0.25)
    end
    tmManager:DelayInvoke(runCameraStreamer, 0.25)
end

-- Schedule execution on Unity's native main-thread tick (10ms) outside Frida's NativeFunction SEH frame
TimerManager:GetInstance():DelayInvoke(function()
    if _G.StartBackgroundWorldPreloader then pcall(_G.StartBackgroundWorldPreloader) end
    local ok, res = pcall(_G.ApplyLastZWorldMaster)
    _G._LastMasterStatus = tostring(ok) .. ": " .. tostring(res)
end, 0.01)

return "SUCCESS_SCHEDULED_MAIN_THREAD_V7"
