-- Last Z engine and graphics diagnostic probe

local function IsNull(o)
    if o == nil then return true end
    if type(o) == "userdata" then
        return o:Equals(nil)
    end
    return false
end

local function SafeCount(col)
    if col == nil then return 0 end
    if type(col) == "table" then
        local n = 0
        for _ in pairs(col) do n = n + 1 end
        return n
    end
    local t = col:GetType()
    local flags = CS.System.Reflection.BindingFlags
    local toInt = CS.System.Convert.ToInt32
    local allFlags = toInt(flags.Public) + toInt(flags.Instance)
    local pCount = t:GetProperty("Count", allFlags)
    if pCount then return pCount:GetValue(col, nil) end
    local pLen = t:GetProperty("Length", allFlags)
    if pLen then return pLen:GetValue(col, nil) end
    return -1
end

-- Phase 1: live remediation
local function ApplyWorldGraphicsFixes()
    local flags = CS.System.Reflection.BindingFlags
    local toInt = CS.System.Convert.ToInt32
    local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)

    -- 1. Neutralize rogue 5.0s heartbeat timers that reset Main Camera to Near=3.0 / Far=35000.0
    local tm = TimerManager and TimerManager:GetInstance()
    if tm then
        if tm.__update_timer then
            for timerObj, _ in pairs(tm.__update_timer) do
                if type(timerObj) == "table" and timerObj.one_shot == true and timerObj.obj_not_nil == false and timerObj.delay == 5.0 then
                    timerObj.over = true
                    timerObj.target_func = function() end
                    tm.__update_timer[timerObj] = nil
                end
            end
        end
        if tm.__update_toadd then
            for timerObj, _ in pairs(tm.__update_toadd) do
                if type(timerObj) == "table" and timerObj.one_shot == true and timerObj.obj_not_nil == false and timerObj.delay == 5.0 then
                    timerObj.over = true
                    timerObj.target_func = function() end
                    tm.__update_toadd[timerObj] = nil
                end
            end
        end

        if not tm._safeDelayInvokeWrapped then
            tm._safeDelayInvokeWrapped = true
            local origDelayInvoke = tm.DelayInvoke
            tm.DelayInvoke = function(self, func, delay, ...)
                if delay == 5.0 and type(func) == "function" and func ~= _G._cleanHeartbeatFunc then
                    local dinfo = debug and debug.getinfo and debug.getinfo(func, "S")
                    if dinfo and string.find(tostring(dinfo.short_src), "%[string") then
                        return
                    end
                end
                return origDelayInvoke(self, func, delay, ...)
            end
        end

        if not _G._cleanHeartbeatInstalled then
            _G._cleanHeartbeatInstalled = true
            _G._cleanHeartbeatFunc = function()
                local curApp = CS.UnityEngine.Application
                local curQs = CS.UnityEngine.QualitySettings
                if curApp and curApp.targetFrameRate ~= 180 then curApp.targetFrameRate = 180 end
                if curQs and curQs.vSyncCount ~= 0 then curQs.vSyncCount = 0 end

                local curWs = SceneManager and SceneManager.World
                if curWs and curWs.Camera and curWs.Camera.camera and not IsNull(curWs.Camera.camera) then
                    curWs.Camera.camera.farClipPlane = 12000.0
                    curWs.Camera.camera.nearClipPlane = 20.0
                end
                local mCam = CS.UnityEngine.Camera.main
                if not IsNull(mCam) and not mCam.orthographic then
                    mCam.farClipPlane = 12000.0
                    mCam.nearClipPlane = 20.0
                end

                local ahm = DataCenter and DataCenter.AllianceHelpDataManager
                if ahm and ahm.GetHelpNum and ahm:GetHelpNum() > 0 then
                    ahm:OnHelpAll()
                end
                tm:DelayInvoke(_G._cleanHeartbeatFunc, 5.0)
            end
            tm:DelayInvoke(_G._cleanHeartbeatFunc, 5.0)
        end
    end

    -- 2. Clamp Perspective Camera Depth Ratio (600:1) & Restore Orthographic UICamera (-100..1000)
    local allCams = CS.UnityEngine.Camera.allCameras
    if allCams then
        for i = 0, allCams.Length - 1 do
            local cam = allCams[i]
            if not IsNull(cam) then
                if cam.orthographic then
                    if cam.nearClipPlane > 0 then
                        cam.nearClipPlane = -100.0
                    end
                else
                    cam.nearClipPlane = 20.0
                    cam.farClipPlane = 12000.0
                end
            end
        end
    end

    local ws = SceneManager and SceneManager.World
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

    -- 3. Patch UniversalRenderPipelineAsset_High Shadow Cascades, Distance, Bias & MSAA
    local gs = CS.UnityEngine.Rendering.GraphicsSettings
    local rp = gs and (gs.currentRenderPipeline or gs.renderPipelineAsset)
    if not IsNull(rp) then
        rp.shadowDistance = 220.0
        rp.shadowCascadeCount = 2
        rp.shadowDepthBias = 1.2
        rp.shadowNormalBias = 1.2
        rp.msaaSampleCount = 4

        local t = rp:GetType()
        local fRes = t:GetField("m_MainLightShadowmapResolution", allFlags)
        if fRes then
            local v2048 = CS.System.Enum.ToObject(fRes.FieldType, toInt(2048))
            fRes:SetValue(rp, v2048)
        end
    end

    local qs = CS.UnityEngine.QualitySettings
    if qs then
        qs.shadowDistance = 220.0
        qs.shadowCascades = 2
        qs.shadowNearPlaneOffset = 0.8
    end

    -- 4. Clean up forced GPU instancing on incompatible custom shaders (SRP Batcher compatibility)
    local renderers = CS.UnityEngine.Object.FindObjectsOfType(typeof(CS.UnityEngine.MeshRenderer))
    if renderers then
        for r = 0, renderers.Length - 1 do
            local mr = renderers[r]
            if not IsNull(mr) then
                local mat = mr.sharedMaterial
                if not IsNull(mat) and mat.enableInstancing then
                    local sh = mat.shader
                    if not IsNull(sh) then
                        local sName = sh.name
                        if not string.find(sName, "Instanc") and not string.find(sName, "Standard") and not string.find(sName, "Universal") and not string.find(sName, "URP") then
                            mat.enableInstancing = false
                        end
                    end
                end
            end
        end
    end
end

-- Phase 2: enhanced diagnostic probe
local function RunWorldViewDiagnostics()
    local report = {
        timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ"),
        system = {},
        pipeline = {},
        quality = {},
        shadows = {},
        cameras = {},
        world_camera_hooks = {},
        timers_and_globals = {},
        lod_pipeline = {},
        materials = {},
        terrain_and_ground = {},
        anomalies_detected = {}
    }

    local app = CS.UnityEngine.Application
    local qs = CS.UnityEngine.QualitySettings
    local gs = CS.UnityEngine.Rendering and CS.UnityEngine.Rendering.GraphicsSettings
    local screen = CS.UnityEngine.Screen
    local flags = CS.System.Reflection.BindingFlags
    local toInt = CS.System.Convert.ToInt32
    local allFlags = toInt(flags.Public) + toInt(flags.NonPublic) + toInt(flags.Instance)

    -- 1. SYSTEM, DISPLAY & URP PIPELINE METRICS
    report.system.targetFrameRate = app and app.targetFrameRate or -1
    report.system.platform = app and tostring(app.platform) or "Unknown"
    report.system.unityVersion = app and tostring(app.unityVersion) or "Unknown"

    local display = CS.UnityEngine.Display.main
    if display then
        report.system.displayResolution = string.format("%dx%d", display.renderingWidth, display.renderingHeight)
        report.system.systemResolution = string.format("%dx%d", display.systemWidth, display.systemHeight)
    end
    if screen then
        report.system.fullScreenMode = tostring(screen.fullScreenMode)
        report.system.refreshRate = tostring(screen.currentResolution)
    end

    if gs then
        local rp = gs.currentRenderPipeline or gs.renderPipelineAsset
        report.pipeline.currentRenderPipeline = (not IsNull(rp)) and (rp.name .. " (" .. rp:GetType().Name .. ")") or "Built-in Render Pipeline"
        report.pipeline.useScriptableRenderPipelineBatching = gs.useScriptableRenderPipelineBatching
        if not IsNull(rp) then
            local rpType = rp:GetType()
            local urpFields = {"m_SupportsHDR", "m_MSAA", "m_RenderScale", "m_ShadowDistance", "m_ShadowCascadeCount", "m_MainLightShadowmapResolution", "m_ShadowDepthBias", "m_ShadowNormalBias", "m_UseSRPBatcher"}
            for _, fName in ipairs(urpFields) do
                local fd = rpType:GetField(fName, allFlags)
                if fd then
                    report.pipeline["urp_" .. fName] = tostring(fd:GetValue(rp))
                end
            end
            if rp.shadowDistance and rp.shadowDistance > 400.0 then
                table.insert(report.anomalies_detected, {
                    severity = "HIGH",
                    category = "URP_SHADOW_SHIMMER",
                    message = string.format("URP Asset shadowDistance=%.1f with %d cascade(s) and normalBias=%.2f causes shadow texel snapping and terrain shadow acne.", rp.shadowDistance, rp.shadowCascadeCount or 1, rp.shadowNormalBias or 0)
                })
            end
        end
    end

    -- 2. QUALITY SETTINGS & SHADOWS
    if qs then
        report.quality.qualityLevel = qs.GetQualityLevel and qs.GetQualityLevel() or -1
        report.quality.vSyncCount = qs.vSyncCount
        report.quality.antiAliasing = qs.antiAliasing
        report.quality.anisotropicFiltering = tostring(qs.anisotropicFiltering)
        report.quality.lodBias = qs.lodBias
        report.quality.maximumLODLevel = qs.maximumLODLevel
        report.quality.asyncUploadTimeSlice = qs.asyncUploadTimeSlice
        report.quality.asyncUploadBufferSize = qs.asyncUploadBufferSize
        report.quality.asyncUploadPersistentBuffer = qs.asyncUploadPersistentBuffer

        report.shadows.shadows = tostring(qs.shadows)
        report.shadows.shadowResolution = tostring(qs.shadowResolution)
        report.shadows.shadowProjection = tostring(qs.shadowProjection)
        report.shadows.shadowDistance = qs.shadowDistance
        report.shadows.shadowCascades = qs.shadowCascades
        report.shadows.shadowNearPlaneOffset = qs.shadowNearPlaneOffset

        if qs.vSyncCount == 0 and app and app.targetFrameRate > 120 then
            table.insert(report.anomalies_detected, {
                severity = "WARNING",
                category = "FRAME_PACING",
                message = string.format("vSyncCount is 0 with %d FPS target (%s). Borderless DWM presentation can produce micro-stutter.", app.targetFrameRate, tostring(report.system.fullScreenMode))
            })
        end

        if qs.shadowNearPlaneOffset and qs.shadowNearPlaneOffset > 1.5 then
            table.insert(report.anomalies_detected, {
                severity = "HIGH",
                category = "SHADOW_ACNE",
                message = string.format("shadowNearPlaneOffset is %.2f (recommended: 0.1 to 1.0). High offsets cause shadow acne and terrain shadow flicker.", qs.shadowNearPlaneOffset)
            })
        end
    end

    -- 3. CAMERA DEPTH BUFFER PRECISION & CLIPPING PLANES
    local allCams = CS.UnityEngine.Camera.allCameras
    if allCams then
        for i = 0, allCams.Length - 1 do
            local cam = allCams[i]
            if not IsNull(cam) then
                local nc = tonumber(cam.nearClipPlane) or 0
                local fc = tonumber(cam.farClipPlane) or 0
                local ratio = (nc > 0) and (fc / nc) or 0
                local camData = {
                    name = tostring(cam.name),
                    enabled = cam.enabled,
                    depth = tonumber(cam.depth) or 0,
                    clearFlags = tostring(cam.clearFlags),
                    orthographic = cam.orthographic,
                    nearClipPlane = nc,
                    farClipPlane = fc,
                    fieldOfView = tonumber(cam.fieldOfView) or 0,
                    cullingMask = tonumber(cam.cullingMask) or 0,
                    renderingPath = tostring(cam.actualRenderingPath),
                    hdr = cam.allowHDR,
                    msaa = cam.allowMSAA,
                    depthTextureMode = tostring(cam.depthTextureMode),
                    depthRatio = ratio
                }

                if not cam.orthographic and camData.depthRatio > 5000 then
                    table.insert(report.anomalies_detected, {
                        severity = "CRITICAL",
                        category = "DEPTH_BUFFER_COLLAPSE",
                        message = string.format(
                            "Camera '%s' has Near=%.2f, Far=%.1f (Ratio: %.0f:1). Extreme Far/Near ratio collapses 24-bit depth precision, causing severe Z-fighting and terrain flickering in world view.",
                            tostring(camData.name), nc, fc, ratio
                        ),
                        recommended_near = math.max(15.0, fc / 1500.0),
                        recommended_far = math.min(12000.0, fc)
                    })
                end

                table.insert(report.cameras, camData)
            end
        end
    end

    -- 4. WORLD SCENE, CAMERA CONTROLLER & HOOK STATE
    local sm = SceneManager
    report.world_camera_hooks.isInWorld = sm and sm.IsInWorld and sm:IsInWorld() or false
    report.world_camera_hooks.masterAutoWorldHooked = sm and sm._masterAutoWorldHooked or false
    report.timers_and_globals.masterHeartbeatActive = _G._masterHeartbeatActive or false
    report.timers_and_globals.masterProxTimerActive = _G._masterProxTimerActive or false

    local ws = sm and sm.World
    if ws and ws.Camera then
        report.lod_pipeline.hasWorldScene = true
        local wcam = ws.Camera
        if wcam.camera and not IsNull(wcam.camera) then
            report.world_camera_hooks.worldCamNear = wcam.camera.nearClipPlane
            report.world_camera_hooks.worldCamFar = wcam.camera.farClipPlane
            report.world_camera_hooks.worldCamPos = tostring(wcam.camera.transform.position)
            report.world_camera_hooks.worldCamEuler = tostring(wcam.camera.transform.eulerAngles)
        end

        local afterTbl = wcam.AfterUpdate or wcam.AfterUpdateAction
        if afterTbl then
            local actions = {}
            for k, _ in pairs(afterTbl) do
                table.insert(actions, tostring(k))
            end
            report.world_camera_hooks.afterUpdateActions = actions
        end

        local tc = wcam.touchCamera
        if tc and not IsNull(tc) then
            report.lod_pipeline.autoScrollVelocityMax = tc.AutoScrollVelocityMax
            report.lod_pipeline.autoScrollDamp = tc.AutoScrollDamp
            report.lod_pipeline.camFollowFactor = tc.CamFollowFactor
            report.lod_pipeline.zoomTime = tc.zoomTime
        end
    else
        report.lod_pipeline.hasWorldScene = false
    end

    -- 5. WORLD POINT LOD MANAGER, HYSTERESIS & OVERLAP AUDIT
    local wpm = DataCenter and DataCenter.WorldPointManager
    if wpm then
        report.lod_pipeline.currentLodLevel = wpm.lodLv or "Unknown"
        report.lod_pipeline.isLodAdjusting = wpm.isLodAdjusting or false
        report.lod_pipeline.aoiOptimizeEnabled = wpm.aoiOptimizeEnabled
        report.lod_pipeline.aoiReconcileEnabled = wpm.aoiReconcileEnabled
        report.lod_pipeline.outOfViewOffX = wpm.outOfViewOffX
        report.lod_pipeline.reqPos = wpm.reqPos and string.format("(%.1f, %.1f)", wpm.reqPos.x or 0, wpm.reqPos.y or 0) or "nil"

        report.lod_pipeline.allObjCount = SafeCount(wpm.allObj)
        report.lod_pipeline.zonePointMapCount = SafeCount(wpm.zonePointMap)
        report.lod_pipeline.validZonesCount = SafeCount(wpm.validZones)
        report.lod_pipeline.toBuildQueueLen = wpm.toBuildList and #wpm.toBuildList or 0
        report.lod_pipeline.toBuildListHead = wpm.toBuildListHead or 0

        local objSource = wpm.allObj or wpm.pointList
        local sampleAdjuster = nil
        local activeModelsNear = 0
        local culledModelsOutPos = 0
        local activeBothModelAndIcon = 0
        local classBreakdown = {}

        if objSource then
            for _, pt in pairs(objSource) do
                local cname = (pt._class_type and pt._class_type.__cname) or "Unknown"
                classBreakdown[cname] = (classBreakdown[cname] or 0) + 1

                if pt and pt.adjuster and not IsNull(pt.adjuster) and not sampleAdjuster then
                    sampleAdjuster = pt.adjuster
                end

                if pt.gameObject and not IsNull(pt.gameObject) and pt.gameObject.activeInHierarchy then
                    local tr = pt.gameObject.transform
                    local mGo = tr:Find("ModelGo") or tr:Find("Model")
                    local iGo = tr:Find("Icon") or tr:Find("IconHouse") or tr:Find("FarIcon") or tr:Find("lodSetObj")
                    if mGo and not IsNull(mGo) then
                        if mGo.localPosition.x < -1000 then
                            culledModelsOutPos = culledModelsOutPos + 1
                        elseif mGo.gameObject.activeInHierarchy then
                            activeModelsNear = activeModelsNear + 1
                            if iGo and not IsNull(iGo) and iGo.gameObject.activeInHierarchy then
                                activeBothModelAndIcon = activeBothModelAndIcon + 1
                            end
                        end
                    end
                end
            end
        end

        report.lod_pipeline.classBreakdown = classBreakdown
        report.lod_pipeline.activeModelsNear = activeModelsNear
        report.lod_pipeline.culledModelsOutPos = culledModelsOutPos
        report.lod_pipeline.activeBothModelAndIcon = activeBothModelAndIcon

        if activeBothModelAndIcon > 0 then
            table.insert(report.anomalies_detected, {
                severity = "HIGH",
                category = "LOD_DUAL_RENDER_FLICKER",
                message = string.format("%d world objects have BOTH 3D ModelGo and 2D FarIcon active simultaneously, causing Z-overlap and pop-in flicker.", activeBothModelAndIcon)
            })
        end

        if sampleAdjuster then
            local f = sampleAdjuster:GetType():GetField("settings", allFlags)
            local arr = f and f:GetValue(sampleAdjuster)
            if arr and arr.Length > 0 then
                local settingType = arr:GetType():GetElementType()
                local tF = settingType:GetField("targets", allFlags)
                local lF = settingType:GetField("showLods", allFlags)

                local settingsAudit = {}
                for idx = 0, arr.Length - 1 do
                    local s = arr[idx]
                    local tList = tF and tF:GetValue(s)
                    local lList = lF and lF:GetValue(s)

                    local lodStr = ""
                    if lList then
                        for li = 0, lList.Count - 1 do
                            lodStr = lodStr .. tostring(lList[li]) .. ","
                        end
                    end

                    local targetNames = ""
                    if tList then
                        for ti = 0, tList.Length - 1 do
                            local o = tList[ti]
                            targetNames = targetNames .. ((not IsNull(o) and o.name) or "null") .. ";"
                        end
                    end

                    table.insert(settingsAudit, {
                        index = idx,
                        targets = targetNames,
                        assigned_lods = lodStr
                    })
                end
                report.lod_pipeline.sampleAdjusterSettings = settingsAudit
            end
        end
    end

    -- 6. MATERIAL, SHADER & COPLANAR GROUND Z-FIGHTING AUDIT
    local renderers = CS.UnityEngine.Object.FindObjectsOfType(typeof(CS.UnityEngine.MeshRenderer))
    if renderers and renderers.Length > 0 then
        report.materials.totalMeshRenderers = renderers.Length
        local instancingMismatches = 0
        local shaderCounts = {}
        local totalChecked = math.min(renderers.Length, 250)

        for r = 0, totalChecked - 1 do
            local mr = renderers[r]
            if not IsNull(mr) and mr.enabled and mr.gameObject.activeInHierarchy then
                local mat = mr.sharedMaterial
                if not IsNull(mat) then
                    local shader = mat.shader
                    local sName = (not IsNull(shader) and shader.name) or "None"
                    shaderCounts[sName] = (shaderCounts[sName] or 0) + 1

                    if mat.enableInstancing and not IsNull(shader) then
                        if not string.find(sName, "Instanc") and not string.find(sName, "Standard") and not string.find(sName, "Universal") and not string.find(sName, "URP") then
                            instancingMismatches = instancingMismatches + 1
                        end
                    end
                end
            end
        end

        report.materials.instancingMismatchesSampled = instancingMismatches
        report.materials.shaderBreakdownSample = shaderCounts

        if instancingMismatches > 5 then
            table.insert(report.anomalies_detected, {
                severity = "MEDIUM",
                category = "SHADER_INSTANCING",
                message = string.format("Found %d/250 sampled MeshRenderers with GPU instancing forced onto custom shaders that do not declare instancing passes.", instancingMismatches)
            })
        end
    end

    if report.timers_and_globals.masterHeartbeatActive then
        for _, c in ipairs(report.cameras) do
            if not c.orthographic and (c.farClipPlane >= 30000 or c.nearClipPlane <= 3.5) then
                table.insert(report.anomalies_detected, {
                    severity = "CRITICAL",
                    category = "ROGUE_HEARTBEAT_OVERRIDE",
                    message = string.format(
                        "_G._masterHeartbeatActive timer is actively resetting Camera '%s' back to Near=%.1f, Far=%.1f every 5 seconds!",
                        c.name, c.nearClipPlane, c.farClipPlane
                    )
                })
            end
        end
    end

    return report
end

ApplyWorldGraphicsFixes()
local diag = RunWorldViewDiagnostics()
return diag
