import pathlib

MASTER_LUA_CODE = r"""
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
        if ok and wx and wz and (wx ~= 0 or wz ~= 0) then
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
    if mgr and mgr.curCameraTarget and (mgr.curCameraTarget.x ~= 0 or mgr.curCameraTarget.z ~= 0) and SceneUtils and SceneUtils.WorldToTileXZ and ForceChangeScene then
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
        app.targetFrameRate = (app.isFocused == false) and 30 or 144
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
            if app then app.targetFrameRate = (app.isFocused == false) and 30 or 144 end
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

        -- Pass 1: Detect whether this adjuster has separate Near/Far representations
        local hasAnyModel = false
        local hasAnyFarIcon = false
        local hasAnyNearLabel = false
        local hasAnyFarLabel = false
        local meta = {}

        for i = 0, arr.Length - 1 do
            local s = arr[i]
            local targets = tF and tF:GetValue(s)
            local isModel = false
            local isFarIcon = false
            local isNearLabel = false
            local isFarLabel = false

            if targets and targets.Length > 0 then
                for t = 0, targets.Length - 1 do
                    local tObj = targets[t]
                    local tname = (not IsNull(tObj) and tObj.name) or ""
                    if tname == "ModelGo" or tname == "Model" or tname == "ModelInstance" then
                        isModel = true
                        hasAnyModel = true
                    elseif tname == "Icon" or tname == "IconHouse" or tname == "IconNormal" or tname == "FarIcon" or tname == "lodSetObj" then
                        isFarIcon = true
                        hasAnyFarIcon = true
                    elseif string.find(tname, "Near") or string.find(tname, "ModelHead") or tname == "ModelLabel" then
                        isNearLabel = true
                        hasAnyNearLabel = true
                    elseif string.find(tname, "Far") or string.find(tname, "IconHead") or tname == "IconLabel" then
                        isFarLabel = true
                        hasAnyFarLabel = true
                    end
                end
            end
            meta[i] = {
                s = s,
                isModel = isModel,
                isFarIcon = isFarIcon,
                isNearLabel = isNearLabel,
                isFarLabel = isFarLabel
            }
        end

        -- Pass 2: Assign LODs without ever orphaning single-representation objects
        for i = 0, arr.Length - 1 do
            local m = meta[i]
            local llist = lF and lF:GetValue(m.s)
            if llist then
                llist:Clear()
                if m.isModel then
                    if hasAnyFarIcon then
                        llist:Add(toInt(1))
                        llist:Add(toInt(2))
                    else
                        for l = 1, 12 do llist:Add(toInt(l)) end
                    end
                elseif m.isFarIcon then
                    if hasAnyModel then
                        for l = 3, 12 do llist:Add(toInt(l)) end
                    else
                        for l = 1, 12 do llist:Add(toInt(l)) end
                    end
                elseif m.isNearLabel then
                    if hasAnyFarLabel or hasAnyFarIcon then
                        llist:Add(toInt(1))
                        llist:Add(toInt(2))
                    else
                        for l = 1, 12 do llist:Add(toInt(l)) end
                    end
                elseif m.isFarLabel then
                    if hasAnyNearLabel then
                        for l = 3, 12 do llist:Add(toInt(l)) end
                    else
                        for l = 1, 12 do llist:Add(toInt(l)) end
                    end
                else
                    if arr.Length >= 4 then
                        if i < 2 then
                            llist:Add(toInt(1))
                            llist:Add(toInt(2))
                        else
                            for l = 3, 12 do llist:Add(toInt(l)) end
                        end
                    else
                        for l = 1, 12 do llist:Add(toInt(l)) end
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

            if not self.on_LodChanged then
                function self.on_LodChanged(lod) self:OnLodChanged(lod) end
                EventManager:GetInstance():AddListener(EventId.ChangeCameraLod, self.on_LodChanged)
            end

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
                if self.adjuster then expandAdjuster(self.adjuster) end
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

    -- Smooth, zero-stutter frame budgets for DoParse (45/frame) and BuildAsync (30/frame)
    local _parseFrame = -1
    local _parseCount = 0
    mgr.IsBusy = function(self)
        local f = CS.UnityEngine.Time.frameCount
        if f ~= _parseFrame then
            _parseFrame = f
            _parseCount = 0
        end
        _parseCount = _parseCount + 1
        return _parseCount > 45
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
        return _buildCount > 30
    end

    mgr.ReconcileAoiPoints = function(self, newIdSet, newCount)
        if not self.aoiPointIdSet then self.aoiPointIdSet = newIdSet or {}
        else for k in pairs(newIdSet or {}) do self.aoiPointIdSet[k] = true end end
    end
    mgr.ReconcileAoiDeserts = function(self, newIdSet, newCount)
        if not self.aoiDesertIdSet then self.aoiDesertIdSet = newIdSet or {}
        else for k in pairs(newIdSet or {}) do self.aoiDesertIdSet[k] = true end end
    end

    mgr.AddToDeleteList = function(self, index) end
    mgr.DeleteOutOfView = function(self) end
    mgr.CalcOutOfViewZones = function(self) end

    -- Save original unhooked methods once, then ALWAYS update wrapper closures on hot-reload!
    if not mgr._origAddToBuildList and mgr.AddToBuildList then mgr._origAddToBuildList = mgr.AddToBuildList end
    if not mgr._origAddPointInfo and mgr.AddPointInfo then mgr._origAddPointInfo = mgr.AddPointInfo end
    if not mgr._origAddDesertInfo and mgr.AddDesertInfo then mgr._origAddDesertInfo = mgr.AddDesertInfo end
    if not mgr._origRemovePointInfo and mgr.RemovePointInfo then mgr._origRemovePointInfo = mgr.RemovePointInfo end
    if not mgr._origForceDeletePoint and mgr.ForceDeletePoint then mgr._origForceDeletePoint = mgr.ForceDeletePoint end
    if not mgr._origClose and mgr.Close then mgr._origClose = mgr.Close end
    if not mgr._origInit and mgr.Init then mgr._origInit = mgr.Init end
    mgr.__masterCacheHooksInstalled = true

    local origAddToBuildList = mgr._origAddToBuildList
    if origAddToBuildList then
        mgr.AddToBuildList = function(self, pointIndex)
            local entry = self.allViewPoints and self.allViewPoints[pointIndex]
            if entry then
                if entry.mainIndex ~= pointIndex or entry.pointIndex ~= pointIndex then
                    return
                end
                local camX, camY = GetActualCameraTilePos(self, SceneManager and SceneManager.World)
                if not ShouldBuildPointNow(self, pointIndex, entry, camX, camY, false) then
                    return
                end
            end
            return origAddToBuildList(self, pointIndex)
        end
    end

    local origAddPointInfo = mgr._origAddPointInfo
    mgr.AddPointInfo = function(self, pi)
        if pi and pi.id then
            _G._PersistentWorldPointCache[pi.id] = pi
            local pt = pi.PointType or pi.pointType
            if pt == 4 then
                _G._MonsterIdSet[pi.id] = true
            elseif pt == 6 then
                _G._DynamicBuildIdSet[pi.id] = true
            end
        end
        if origAddPointInfo then return origAddPointInfo(self, pi) end
    end

    local origAddDesertInfo = mgr._origAddDesertInfo
    if origAddDesertInfo then
        mgr.AddDesertInfo = function(self, di)
            if di and di.id then
                _G._PersistentDesertCache[di.id] = di
            end
            return origAddDesertInfo(self, di)
        end
    end

    local origRemovePointInfo = mgr._origRemovePointInfo
    mgr.RemovePointInfo = function(self, pointIndex, forceRemove, isOutOfView)
        if forceRemove == true and isOutOfView ~= true then
            _G._PersistentWorldPointCache[pointIndex] = nil
            _G._MonsterIdSet[pointIndex] = nil
            _G._DynamicBuildIdSet[pointIndex] = nil
            if origRemovePointInfo then origRemovePointInfo(self, pointIndex, true) end
        end
    end

    local origForceDeletePoint = mgr._origForceDeletePoint
    if origForceDeletePoint then
        mgr.ForceDeletePoint = function(self, pointIndex)
            _G._PersistentWorldPointCache[pointIndex] = nil
            _G._MonsterIdSet[pointIndex] = nil
            _G._DynamicBuildIdSet[pointIndex] = nil
            return origForceDeletePoint(self, pointIndex)
        end
    end

    local origClose = mgr._origClose
    mgr.Close = function(self)
        if self.allViewPoints then
            for k, v in pairs(self.allViewPoints) do
                if type(v) == "table" and v.mainIndex == k and v.pointIndex == k then
                    if v.pointInfo then
                        _G._PersistentWorldPointCache[k] = v.pointInfo
                        local pt = v.pointType or v.pointInfo.PointType or v.pointInfo.pointType
                        if pt == 4 then _G._MonsterIdSet[k] = true
                        elseif pt == 6 then _G._DynamicBuildIdSet[k] = true end
                    end
                    if v.desertInfo then
                        _G._PersistentDesertCache[k] = v.desertInfo
                    end
                end
            end
        end
        self._masterAppliedForThisWorldSession = false
        if origClose then return origClose(self) end
    end

    local origInit = mgr._origInit
    if origInit then
        mgr.Init = function(self, ...)
            local ret = origInit(self, ...)
            self._masterAppliedForThisWorldSession = false
            if TimerManager then
                TimerManager:GetInstance():DelayInvoke(function()
                    if _G.ApplyLastZWorldMaster then pcall(_G.ApplyLastZWorldMaster) end
                end, 0.2)
            end
            return ret
        end
    end

    if not (mgr and mgr.isInit == true) then
        mgr._masterAppliedForThisWorldSession = false
        return "HOOKS_READY_WAITING_FOR_WORLD_VIEW"
    end

    -- Snapshot any points already in mgr.allViewPoints into _PersistentWorldPointCache
    for k, v in pairs(mgr.allViewPoints or {}) do
        if type(v) == "table" and v.mainIndex == k and v.pointIndex == k then
            if v.pointInfo then
                _G._PersistentWorldPointCache[k] = v.pointInfo
                local pt = v.pointType or v.pointInfo.PointType or v.pointInfo.pointType
                if pt == 4 then _G._MonsterIdSet[k] = true
                elseif pt == 6 then _G._DynamicBuildIdSet[k] = true end
            end
            if v.desertInfo then _G._PersistentDesertCache[k] = v.desertInfo end
        end
    end

    -- Re-hydrate mgr.allViewPoints from _PersistentWorldPointCache (for instant World View restore after HQ View)
    local restoredCount = 0
    for id, pi in pairs(_G._PersistentWorldPointCache) do
        local pt = pi.PointType or pi.pointType
        if pt == 4 then _G._MonsterIdSet[id] = true
        elseif pt == 6 then _G._DynamicBuildIdSet[id] = true end
        local existing = mgr.allViewPoints and mgr.allViewPoints[id]
        if not existing or not existing.pointInfo then
            pcall(mgr.AddPointInfo, mgr, pi)
            restoredCount = restoredCount + 1
        end
    end

    -- Queue eligible primary points around camera + all Global Objects into toBuildList
    local initCamX, initCamY = GetActualCameraTilePos(mgr, ws)
    local queuedCount = 0
    for k, v in pairs(mgr.allViewPoints or {}) do
        if type(v) == "table" and v.mainIndex == k and v.pointIndex == k and (v.pointInfo ~= nil or v.desertInfo ~= nil) then
            if not (mgr.allObj and mgr.allObj[k]) and not (mgr.toBuildSet and mgr.toBuildSet[k]) then
                if ShouldBuildPointNow(mgr, k, v, initCamX, initCamY, false) then
                    mgr:AddToBuildList(k)
                    queuedCount = queuedCount + 1
                end
            end
        end
    end

    -- Camera streamer and proximity gate
    -- Remove any legacy per-frame AfterUpdate hook that caused frame lag
    if ws and ws.Camera then
        local afterTbl = ws.Camera.AfterUpdate or ws.Camera.AfterUpdateAction
        if type(afterTbl) == "table" then
            afterTbl["Proximity3DGate"] = nil
        end
    end

    local outPos = CS.UnityEngine.Vector3(-10000, 0, -10000)
    local zeroPos = CS.UnityEngine.Vector3.zero
    local ENTER_DIST = 90
    local EXIT_DIST = 110
    local lastStreamCamX = -9999
    local lastStreamCamY = -9999
    local lastStreamLod = -1

    local function runSmartStreamAndProximityGate(forceScan)
        if not (mgr and mgr.isInit == true and mgr.allObj) then return end
        local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
        local curLod = GetHysteresisLod(mgr.lodLv or 1)
        local camMoved = (math.abs(camX - lastStreamCamX) >= 8) or (math.abs(camY - lastStreamCamY) >= 8) or (curLod ~= lastStreamLod) or forceScan

        -- 1. Evict ONLY distant wandering zombies (pType == 4) and distant small seasonal builds (pType == 6, isSmall == true).
        --    Also gate 3D meshes on Player Bases (pType == 6) and off-screen 3D models/labels on Resource Nodes (pType == 7) at LOD 1..2.
        local evictedThisTick = 0
        for k, obj in pairs(mgr.allObj) do
            local pType = obj.pointType or (obj.GetPointType and obj:GetPointType())
            local entry = mgr.allViewPoints and mgr.allViewPoints[k]
            if (pType == 4 or pType == 6) and evictedThisTick < 40 and entry and not ShouldBuildPointNow(mgr, k, entry, camX, camY, true) then
                mgr:DestroyObject(k)
                evictedThisTick = evictedThisTick + 1
            elseif pType == 6 and obj.gameObject and not IsNull(obj.gameObject) then
                local modelT = obj._cachedModelT
                if not modelT or IsNull(modelT) then
                    modelT = obj.gameObject.transform:Find("ModelGo") or obj.gameObject.transform:Find("Model")
                    obj._cachedModelT = modelT
                end
                if modelT and not IsNull(modelT) then
                    local px = obj._cachedTileX
                    local py = obj._cachedTileY
                    if not px or not py then
                        px, py = FastIndexToXY(obj.pointIndex)
                        obj._cachedTileX = px
                        obj._cachedTileY = py
                    end
                    local dx = math.abs(px - camX)
                    local dy = math.abs(py - camY)
                    local isCurrentlyCulled = (modelT.localPosition.x < -1000)
                    local shouldShow3D = false
                    if curLod <= 2 then
                        if isCurrentlyCulled then
                            shouldShow3D = (dx <= ENTER_DIST and dy <= ENTER_DIST)
                        else
                            shouldShow3D = (dx <= EXIT_DIST and dy <= EXIT_DIST)
                        end
                    end
                    if shouldShow3D and isCurrentlyCulled then
                        modelT.localPosition = zeroPos
                    elseif (not shouldShow3D) and (not isCurrentlyCulled) then
                        modelT.localPosition = outPos
                    end
                end
            elseif pType == 7 and camMoved and curLod <= 2 and obj._ApplyInstancedLodState then
                local px = obj._cachedTileX
                local py = obj._cachedTileY
                if not px or not py then
                    px, py = FastIndexToXY(obj.pointIndex)
                    obj._cachedTileX = px
                    obj._cachedTileY = py
                end
                local nearNow = (math.abs(px - camX) <= 85 and math.abs(py - camY) <= 85)
                if obj._wasNear3D ~= nearNow then
                    obj._wasNear3D = nearNow
                    local info = entry and entry.pointInfo
                    if info then pcall(obj._ApplyInstancedLodState, obj, info, false) end
                end
            end
        end

        -- 2. Stream in nearby unbuilt Zombies (_MonsterIdSet) and Player HQs / Seasonal (_DynamicBuildIdSet) (Zero C# P/Invoke!)
        if camMoved and mgr.allViewPoints then
            lastStreamCamX = camX
            lastStreamCamY = camY
            lastStreamLod = curLod
            for k in pairs(_G._DynamicBuildIdSet) do
                if not (mgr.allObj and mgr.allObj[k]) and not (mgr.toBuildSet and mgr.toBuildSet[k]) then
                    local v = mgr.allViewPoints[k]
                    if type(v) == "table" and v.mainIndex == k and v.pointIndex == k and v.pointInfo ~= nil then
                        if ShouldBuildPointNow(mgr, k, v, camX, camY, false) then
                            mgr:AddToBuildList(k)
                        end
                    end
                end
            end
            for k in pairs(_G._MonsterIdSet) do
                if not (mgr.allObj and mgr.allObj[k]) and not (mgr.toBuildSet and mgr.toBuildSet[k]) then
                    local v = mgr.allViewPoints[k]
                    if type(v) == "table" and v.mainIndex == k and v.pointIndex == k and v.pointInfo ~= nil then
                        if ShouldBuildPointNow(mgr, k, v, camX, camY, false) then
                            mgr:AddToBuildList(k)
                        end
                    end
                end
            end
        end

        if evictedThisTick > 0 then
            collectgarbage("step", 100)
        end
    end

    _G.ApplyToggleChangeImmediate = function()
        pcall(_G.RefreshMasterOverlayUI)
        if not (mgr and mgr.isInit == true and mgr.allObj) then return end
        local camX, camY = GetActualCameraTilePos(mgr, SceneManager and SceneManager.World)
        for k, obj in pairs(mgr.allObj) do
            local pType = obj.pointType or (obj.GetPointType and obj:GetPointType())
            local entry = mgr.allViewPoints and mgr.allViewPoints[k]
            if pType == 7 and obj._ApplyInstancedLodState then
                local info = entry and entry.pointInfo
                pcall(obj._ApplyInstancedLodState, obj, info, false)
            elseif entry and not ShouldBuildPointNow(mgr, k, entry, camX, camY, true) then
                mgr:DestroyObject(k)
            end
        end
        pcall(runSmartStreamAndProximityGate, true)
    end

    local proxToken = (_G._masterProxToken or 0) + 1
    _G._masterProxToken = proxToken
    if TimerManager then
        local tmManager = TimerManager:GetInstance()
        local function proxStep()
            if _G._masterProxToken ~= proxToken then return end
            pcall(runSmartStreamAndProximityGate, false)
            tmManager:DelayInvoke(proxStep, 0.18)
        end
        tmManager:DelayInvoke(proxStep, 0.18)
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

    -- Full map concentric sweep
    if LuaEntry and LuaEntry.Player and TimerManager then
        local maxTileX = (TileCountX or 1000) - 30
        local maxTileY = (TileCountY or 1000) - 30
        local startX, startY = GetActualCameraTilePos(mgr, ws)
        startX = math.floor(math.max(30, math.min(maxTileX, startX)))
        startY = math.floor(math.max(30, math.min(maxTileY, startY)))

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

        local sweepLod = 0 -- Full server detail cached into allViewPoints; non-zombies build immediately, zombies gated by radius!
        local serverId = LuaEntry.Player:GetSelfServerId()
        local tmManager = TimerManager:GetInstance()
        local sIdx = 1
        local sweepToken = (mgr._sweepToken or 0) + 1
        mgr._sweepToken = sweepToken

        local function sStep()
            if mgr._sweepToken ~= sweepToken then return end
            if not (mgr and mgr.isInit == true) then return end
            if sIdx > #allSectors then return end
            if _G._MasterToggles and _G._MasterToggles.masterEnabled == false then
                tmManager:DelayInvoke(sStep, 0.50)
                return
            end

            -- Save real camera reqPos so background sweep never hijacks reqPos
            local realCamX, realCamY = GetActualCameraTilePos(mgr, SceneManager.World)

            local p = allSectors[sIdx]
            sIdx = sIdx + 1
            mgr.waitingForReply = false
            mgr:DoSendViewRequest(p.x, p.y, sweepLod, serverId)

            if mgr.reqPos and mgr.reqPos.Set then
                mgr.reqPos:Set(realCamX, realCamY)
            end

            if sIdx <= #allSectors then
                tmManager:DelayInvoke(sStep, 0.14)
            end
        end
        sStep()
    end

    mgr._masterAppliedForThisWorldSession = true
    pcall(_G.RefreshMasterOverlayUI)
    pcall(runSmartStreamAndProximityGate, true)

    return string.format("SUCCESS_MASTER_V7_7_HOTKEYS_SMOOTH (restored=%d, queued=%d)", restoredCount, queuedCount)
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
        local res = oldChangeToWorld(self, ...)
        if TimerManager then
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
            if curApp then
                local targetFps = (curApp.isFocused == false) and 30 or 144
                if curApp.targetFrameRate ~= targetFps then curApp.targetFrameRate = targetFps end
            end
            if curQs and curQs.vSyncCount ~= 0 then curQs.vSyncCount = 0 end
            if curQs and curQs.antiAliasing ~= 2 then curQs.antiAliasing = 2 end

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
end

-- Schedule execution on Unity's native main-thread tick (10ms) outside Frida's NativeFunction SEH frame
TimerManager:GetInstance():DelayInvoke(function()
    local ok, res = pcall(_G.ApplyLastZWorldMaster)
    _G._LastMasterStatus = tostring(ok) .. ": " .. tostring(res)
end, 0.01)

return "SUCCESS_SCHEDULED_MAIN_THREAD_V7"
"""

# 1. Update lastz auto engine daemon.py
daemon_path = pathlib.Path(r"data/cache/lastz auto engine daemon.py")
daemon_text = daemon_path.read_text(encoding="utf-8")
start_idx = daemon_text.index('MASTER_LUA_CODE = r"""')
end_idx = daemon_text.index('FRIDA_JS = r"""')
new_daemon = (
    daemon_text[:start_idx]
    + 'MASTER_LUA_CODE = r"""\n'
    + MASTER_LUA_CODE.strip()
    + '\n"""\n\n'
    + daemon_text[end_idx:]
)
# Also make sure BOOTING_WAIT is retried in main() loop of daemon
new_daemon = new_daemon.replace(
    "if ok:\n                        log(f\"[+] Master Overhaul v6.1 successfully injected into Survival.exe (PID {pid})!\")\n                        log(f\"    Mode: {detail}\")\n                        patched_pids.add(pid)",
    "if ok and detail != 'BOOTING_WAIT':\n                        log(f\"[+] Master Overhaul v7.0 successfully injected into Survival.exe (PID {pid})!\")\n                        log(f\"    Mode: {detail}\")\n                        patched_pids.add(pid)"
)
daemon_path.write_text(new_daemon, encoding="utf-8")
print("Updated:", daemon_path)

# 2. Update apply widescreen smooth map.py
widescreen_path = pathlib.Path(r"data/cache/apply widescreen smooth map.py")
ws_text = widescreen_path.read_text(encoding="utf-8")
ws_start = ws_text.index('MASTER_LUA_CODE = r"""')
ws_end = ws_text.index('FRIDA_JS = r"""')
new_ws = (
    ws_text[:ws_start]
    + 'MASTER_LUA_CODE = r"""\n'
    + MASTER_LUA_CODE.strip()
    + '\n"""\n\n'
    + ws_text[ws_end:]
)
widescreen_path.write_text(new_ws, encoding="utf-8")
print("Updated:", widescreen_path)

# 3. Save standalone Lua copy to current scratch
standalone_lua = pathlib.Path(r"data/cache/lastz live remediation patch.lua")
standalone_lua.write_text(MASTER_LUA_CODE.strip() + "\n", encoding="utf-8")
print("Updated:", standalone_lua)
