import frida
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

ENHANCED_DIAG_LUA = r"""
-- Last Z engine and graphics diagnostic probe

local function IsNull(o)
    if o == nil then return true end
    if type(o) == "userdata" then
        local ok, res = pcall(function() return o:Equals(nil) end)
        if ok then return res end
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
    local okC, c = pcall(function() return col.Count end)
    if okC and type(c) == "number" then return c end
    local okL, l = pcall(function() return col.Length end)
    if okL and type(l) == "number" then return l end
    return -1
end

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

    -- 1. System, display and render pipeline metrics
    report.system.targetFrameRate = app and app.targetFrameRate or -1
    report.system.platform = app and tostring(app.platform) or "Unknown"
    report.system.unityVersion = app and tostring(app.unityVersion) or "Unknown"

    pcall(function()
        local display = CS.UnityEngine.Display.main
        if display then
            report.system.displayResolution = string.format("%dx%d", display.renderingWidth, display.renderingHeight)
            report.system.systemResolution = string.format("%dx%d", display.systemWidth, display.systemHeight)
        end
        if screen then
            report.system.fullScreenMode = tostring(screen.fullScreenMode)
            report.system.refreshRate = tostring(screen.currentResolution)
        end
    end)

    pcall(function()
        if gs then
            local rp = gs.currentRenderPipeline or gs.renderPipelineAsset
            report.pipeline.currentRenderPipeline = (rp and not IsNull(rp)) and (rp.name .. " (" .. rp:GetType().Name .. ")") or "Built-in Render Pipeline"
            report.pipeline.useScriptableRenderPipelineBatching = gs.useScriptableRenderPipelineBatching
            if rp and not IsNull(rp) then
                local rpType = rp:GetType()
                local urpFields = {"m_SupportsHDR", "m_MSAA", "m_RenderScale", "m_ShadowDistance", "m_ShadowCascadeCount", "m_MainLightShadowmapResolution", "m_ShadowDepthBias", "m_ShadowNormalBias", "m_UseSRPBatcher"}
                for _, fName in ipairs(urpFields) do
                    local fd = rpType:GetField(fName, allFlags)
                    if fd then
                        local ok, val = pcall(function() return fd:GetValue(rp) end)
                        if ok then report.pipeline["urp_" .. fName] = tostring(val) end
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
    end)

    -- 2. Quality settings (vsync, buffering, lod bias, shadows)
    if qs then
        pcall(function()
            report.quality.qualityLevel = qs.GetQualityLevel and qs.GetQualityLevel() or -1
            report.quality.vSyncCount = qs.vSyncCount
            report.quality.antiAliasing = qs.antiAliasing
            report.quality.anisotropicFiltering = tostring(qs.anisotropicFiltering)
            report.quality.lodBias = qs.lodBias
            report.quality.maximumLODLevel = qs.maximumLODLevel
            report.quality.pixelLightCount = qs.pixelLightCount
            report.quality.asyncUploadTimeSlice = qs.asyncUploadTimeSlice
            report.quality.asyncUploadBufferSize = qs.asyncUploadBufferSize
            report.quality.asyncUploadPersistentBuffer = qs.asyncUploadPersistentBuffer

            report.shadows.shadows = tostring(qs.shadows)
            report.shadows.shadowResolution = tostring(qs.shadowResolution)
            report.shadows.shadowProjection = tostring(qs.shadowProjection)
            report.shadows.shadowDistance = qs.shadowDistance
            report.shadows.shadowCascades = qs.shadowCascades
            report.shadows.shadowNearPlaneOffset = qs.shadowNearPlaneOffset
        end)

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

    -- 3. Camera depth buffer precision and clipping planes
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

    -- 4. World scene, camera controller and hooks audit
    local sm = SceneManager
    report.world_camera_hooks.isInWorld = sm and sm.IsInWorld and sm:IsInWorld() or false
    report.world_camera_hooks.masterAutoWorldHooked = sm and sm._masterAutoWorldHooked or false
    report.timers_and_globals.masterHeartbeatActive = _G._masterHeartbeatActive or false
    report.timers_and_globals.masterProxTimerActive = _G._masterProxTimerActive or false
    report.timers_and_globals.hasApplyLastZWorldMaster = type(_G.ApplyLastZWorldMaster) == "function"

    -- Inspect TimerManager active delay timers to detect rogue 5.0s heartbeat overwriting near=3 / far=35000
    pcall(function()
        if TimerManager then
            local tm = TimerManager:GetInstance()
            if tm then
                local timerSummary = {}
                for k, v in pairs(tm) do
                    if type(v) == "table" then
                        timerSummary[tostring(k)] = SafeCount(v)
                    elseif type(v) ~= "function" then
                        timerSummary[tostring(k)] = tostring(v)
                    end
                end
                report.timers_and_globals.timerManagerFields = timerSummary
            end
        end
    end)

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

    -- 5. World point lod manager, hysteresis and overlap audit
    local wpm = DataCenter and DataCenter.WorldPointManager
    if wpm then
        report.lod_pipeline.currentLodLevel = wpm.lodLv or "Unknown"
        report.lod_pipeline.isLodAdjusting = wpm.isLodAdjusting or false
        report.lod_pipeline.aoiOptimizeEnabled = wpm.aoiOptimizeEnabled
        report.lod_pipeline.aoiReconcileEnabled = wpm.aoiReconcileEnabled
        report.lod_pipeline.outOfViewOffX = wpm.outOfViewOffX
        report.lod_pipeline.reqPos = wpm.reqPos and string.format("(%.1f, %.1f)", wpm.reqPos.x or 0, wpm.reqPos.y or 0) or "nil"

        report.lod_pipeline.pointListCount = SafeCount(wpm.pointList)
        report.lod_pipeline.allObjCount = SafeCount(wpm.allObj)
        report.lod_pipeline.worldPointDicCount = SafeCount(wpm.worldPointDic)
        report.lod_pipeline.posPointDicCount = SafeCount(wpm.posPointDic)
        report.lod_pipeline.toBuildQueueLen = wpm.toBuildList and #wpm.toBuildList or 0
        report.lod_pipeline.toBuildListHead = wpm.toBuildListHead or 0

        -- Audit active objects in wpm.allObj (or pointList fallback)
        local objSource = wpm.allObj or wpm.pointList
        local sampleAdjuster = nil
        local totalObjs = 0
        local activeModelsNear = 0
        local culledModelsOutPos = 0
        local activeBothModelAndIcon = 0
        local adjusterOverlapCount = 0
        local classBreakdown = {}

        if objSource then
            for k, pt in pairs(objSource) do
                totalObjs = totalObjs + 1
                local cname = (pt._class_type and pt._class_type.__cname) or "Unknown"
                classBreakdown[cname] = (classBreakdown[cname] or 0) + 1

                if pt and pt.adjuster and not IsNull(pt.adjuster) then
                    if not sampleAdjuster then sampleAdjuster = pt.adjuster end
                end

                -- Check if both ModelGo and FarIcon/Icon are simultaneously active & visible in camera
                pcall(function()
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
                end)
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
            pcall(function()
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
            end)
        end
    end

    -- 6. Material, shader and terrain z-fighting audit
    pcall(function()
        local renderers = CS.UnityEngine.Object.FindObjectsOfType(typeof(CS.UnityEngine.MeshRenderer))
        if renderers and renderers.Length > 0 then
            report.materials.totalMeshRenderers = renderers.Length
            local instancingMismatches = 0
            local shaderCounts = {}
            local coplanarGroundRenderers = {}
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

                        -- Check ground/terrain/border/map plane objects near Y=0 that might Z-fight
                        local goName = mr.gameObject.name
                        local pos = mr.transform.position
                        if math.abs(pos.y) < 1.5 and (string.find(string.lower(goName), "ground") or string.find(string.lower(goName), "terrain") or string.find(string.lower(goName), "land") or string.find(string.lower(goName), "map") or string.find(string.lower(goName), "tile") or string.find(string.lower(goName), "plane") or string.find(string.lower(goName), "border") or string.find(string.lower(goName), "shadow")) then
                            if #coplanarGroundRenderers < 25 then
                                table.insert(coplanarGroundRenderers, {
                                    name = goName,
                                    y = pos.y,
                                    shader = sName,
                                    renderQueue = mat.renderQueue,
                                    sortingOrder = mr.sortingOrder,
                                    shadowMode = tostring(mr.shadowCastingMode),
                                    receiveShadows = mr.receiveShadows
                                })
                            end
                        end
                    end
                end
            end

            report.materials.instancingMismatchesSampled = instancingMismatches
            report.materials.shaderBreakdownSample = shaderCounts
            report.terrain_and_ground.coplanarGroundSample = coplanarGroundRenderers

            if instancingMismatches > 5 then
                table.insert(report.anomalies_detected, {
                    severity = "MEDIUM",
                    category = "SHADER_INSTANCING",
                    message = string.format("Found %d/250 sampled MeshRenderers with GPU instancing forced onto custom shaders (%s) that may not declare instancing passes.", instancingMismatches, "forced by optimizeInstance")
                })
            end
        end
    end)

    -- Check if _masterHeartbeatActive is running with the old 35000/3.0 camera override
    if report.timers_and_globals.masterHeartbeatActive then
        for _, c in ipairs(report.cameras) do
            if not c.orthographic and (c.farClipPlane >= 30000 or c.nearClipPlane <= 3.5) then
                table.insert(report.anomalies_detected, {
                    severity = "CRITICAL",
                    category = "ROGUE_HEARTBEAT_OVERRIDE",
                    message = string.format(
                        "_G._masterHeartbeatActive timer is actively resetting Camera '%s' back to Near=%.1f, Far=%.1f every 5 seconds! This overrides any one-shot flicker fix.",
                        c.name, c.nearClipPlane, c.farClipPlane
                    )
                })
            end
        end
    end

    return report
end

local ok, diagOrErr = pcall(RunWorldViewDiagnostics)
if not ok then
    return "ERROR_RUNNING_DIAG: " .. tostring(diagOrErr)
end

local diag = diagOrErr
local out = {}
local function p(s) table.insert(out, s) end

p("--------------------------------------------------------------------------------")
p("         LAST Z WORLD VIEW GRAPHICS DIAGNOSTIC REPORT (v2.0 ENHANCED)           ")
p("--------------------------------------------------------------------------------")
p(string.format("Timestamp: %s | Platform: %s | Unity: %s", diag.timestamp, diag.system.platform, diag.system.unityVersion))
p(string.format("Display: %s (Sys: %s) | Mode: %s | Refresh: %s | Target FPS: %d",
    diag.system.displayResolution or "N/A", diag.system.systemResolution or "N/A",
    diag.system.fullScreenMode or "N/A", diag.system.refreshRate or "N/A", diag.system.targetFrameRate or -1))
p(string.format("Pipeline: %s | SRP Batcher: %s",
    diag.pipeline.currentRenderPipeline or "N/A", tostring(diag.pipeline.useScriptableRenderPipelineBatching)))
for k, v in pairs(diag.pipeline) do
    if string.sub(k, 1, 4) == "urp_" then
        p(string.format("  * %s = %s", k, v))
    end
end

p(string.format("Quality (Lvl %s): VSync=%s | AA=%sx | AF=%s | LOD Bias=%.2f | MaxLOD=%s",
    tostring(diag.quality.qualityLevel), tostring(diag.quality.vSyncCount), tostring(diag.quality.antiAliasing),
    tostring(diag.quality.anisotropicFiltering), diag.quality.lodBias or 0, tostring(diag.quality.maximumLODLevel)))
p(string.format("Shadows: Mode=%s | Res=%s | Proj=%s | Dist=%.1f | Cascades=%s | NearOffset=%.2f",
    tostring(diag.shadows.shadows), tostring(diag.shadows.shadowResolution), tostring(diag.shadows.shadowProjection),
    diag.shadows.shadowDistance or 0, tostring(diag.shadows.shadowCascades), diag.shadows.shadowNearPlaneOffset or 0))

p("\n- Active cameras & depth precision -")
for _, c in ipairs(diag.cameras) do
    p(string.format(" * Camera: %-18s | En:%-5s | Ortho:%-5s | Near:%6.2f | Far:%8.1f | Ratio:%8.1f:1 | FOV:%5.1f | Clear:%s | HDR:%s | MSAA:%s",
        c.name, tostring(c.enabled), tostring(c.orthographic), c.nearClipPlane, c.farClipPlane, c.depthRatio,
        c.fieldOfView, c.clearFlags, tostring(c.hdr), tostring(c.msaa)))
end

p("\n- World camera & hook state -")
p(string.format(" * IsInWorld: %s | AutoWorldHooked: %s | HeartbeatActive: %s | ProxTimerActive: %s",
    tostring(diag.world_camera_hooks.isInWorld), tostring(diag.world_camera_hooks.masterAutoWorldHooked),
    tostring(diag.timers_and_globals.masterHeartbeatActive), tostring(diag.timers_and_globals.masterProxTimerActive)))
p(string.format(" * WorldCam Pos: %s | Euler: %s | Near: %s | Far: %s",
    tostring(diag.world_camera_hooks.worldCamPos), tostring(diag.world_camera_hooks.worldCamEuler),
    tostring(diag.world_camera_hooks.worldCamNear), tostring(diag.world_camera_hooks.worldCamFar)))
if diag.world_camera_hooks.afterUpdateActions then
    p(" * AfterUpdateActions: " .. table.concat(diag.world_camera_hooks.afterUpdateActions, ", "))
end
if diag.timers_and_globals.timerManagerFields then
    local tf = {}
    for k, v in pairs(diag.timers_and_globals.timerManagerFields) do table.insert(tf, k .. "=" .. tostring(v)) end
    p(" * TimerManager: " .. table.concat(tf, ", "))
end

p("\n- World point LOD pipeline & object state -")
p(string.format(" * Current LOD: %s | Adjusting: %s | reqPos: %s | AOI Opt: %s | AOI Reconcile: %s | outOfViewOffX: %s",
    tostring(diag.lod_pipeline.currentLodLevel), tostring(diag.lod_pipeline.isLodAdjusting),
    tostring(diag.lod_pipeline.reqPos), tostring(diag.lod_pipeline.aoiOptimizeEnabled),
    tostring(diag.lod_pipeline.aoiReconcileEnabled), tostring(diag.lod_pipeline.outOfViewOffX)))
p(string.format(" * Counts -> allObj: %s | worldPointDic: %s | posPointDic: %s | pointList: %s | toBuildQueue: %s (head: %s)",
    tostring(diag.lod_pipeline.allObjCount), tostring(diag.lod_pipeline.worldPointDicCount),
    tostring(diag.lod_pipeline.posPointDicCount), tostring(diag.lod_pipeline.pointListCount),
    tostring(diag.lod_pipeline.toBuildQueueLen), tostring(diag.lod_pipeline.toBuildListHead)))
p(string.format(" * 3D Models -> ActiveNear: %s | CulledToOutPos(-10000): %s | DualActive(Model+Icon): %s",
    tostring(diag.lod_pipeline.activeModelsNear), tostring(diag.lod_pipeline.culledModelsOutPos),
    tostring(diag.lod_pipeline.activeBothModelAndIcon)))

if diag.lod_pipeline.classBreakdown then
    local cb = {}
    for k, v in pairs(diag.lod_pipeline.classBreakdown) do table.insert(cb, k .. ":" .. tostring(v)) end
    p(" * Object Classes: " .. table.concat(cb, " | "))
end

if diag.lod_pipeline.sampleAdjusterSettings then
    p(" * Sample WorldPointAdjuster Settings:")
    for _, s in ipairs(diag.lod_pipeline.sampleAdjusterSettings) do
        p(string.format("    [%d] Targets: %-35s | LODs: %s", s.index, s.targets, s.assigned_lods))
    end
end

p("\n- Materials, shaders & coplanar ground audit -")
p(string.format(" * Total MeshRenderers: %s | Sampled Instancing Mismatches: %s",
    tostring(diag.materials.totalMeshRenderers), tostring(diag.materials.instancingMismatchesSampled)))
if diag.materials.shaderBreakdownSample then
    local sb = {}
    for k, v in pairs(diag.materials.shaderBreakdownSample) do table.insert(sb, k .. "(" .. tostring(v) .. ")") end
    p(" * Sampled Shaders: " .. table.concat(sb, ", "))
end
if diag.terrain_and_ground.coplanarGroundSample and #diag.terrain_and_ground.coplanarGroundSample > 0 then
    p(" * Coplanar Ground/Map Renderers near Y=0:")
    for _, g in ipairs(diag.terrain_and_ground.coplanarGroundSample) do
        p(string.format("    - %-28s | Y=%7.4f | Queue=%-4d | Order=%-3d | Shadow=%-4s | RecvShad=%-5s | Shader=%s",
            g.name, g.y, g.renderQueue, g.sortingOrder, g.shadowMode, tostring(g.receiveShadows), g.shader))
    end
end

p("\n- Detected anomalies & flicker causes -")
if #diag.anomalies_detected == 0 then
    p(" [OK] No critical rendering anomalies detected.")
else
    for i, anom in ipairs(diag.anomalies_detected) do
        p(string.format(" [%s] [%s] %s", anom.severity, anom.category, anom.message))
    end
end
p("--------------------------------------------------------------------------------")

return table.concat(out, "\n")
"""

FRIDA_JS = r"""
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
""" % json.dumps(ENHANCED_DIAG_LUA)

def main():
    session = frida.attach('Survival.exe')
    res_holder = []
    def on_msg(m, d):
        if m.get('type') == 'send':
            res_holder.append(m.get('payload'))
        else:
            res_holder.append({'type': 'error', 'data': str(m)})

    script = session.create_script(FRIDA_JS)
    script.on('message', on_msg)
    script.load()

    for _ in range(30):
        if res_holder:
            break
        time.sleep(0.1)

    try:
        session.detach()
    except Exception:
        pass

    if res_holder:
        r = res_holder[0]
        if r.get('type') == 'result':
            print(r.get('data'))
        else:
            print("ERROR:", r.get('data'))
    else:
        print("TIMEOUT")

if __name__ == '__main__':
    main()
