"""R2 Hook/Bridge, R3 Megamind Preload & R4 Guardrail Contract Tests (Milestone M4).

Covers:
1. R2 Hook & Bridge Contracts (`daemon/lastz auto engine daemon.py`,
   `tools/flush game memory.py`, `daemon/apply widescreen smooth map.py`):
   - `attempt_patch` & `flush_memory` route via `frida_eval_lua` (no raw `frida.attach`).
   - `FARM_ECO_LUA_PATCH` `ecoBeat` is closure-free and performs change-only C# writes.
   - `MASTER_LUA_CODE` uses 50x50 spatial bucketing + incremental point counter,
     stops unconditional `_ForceStreamRescan = true` in `sStep()`, caches C# reflection
     `FieldInfo`/boxed ints, memoizes `Material` IDs, caches `Renderer`, reconciles
     `shadowDistance`, throttles `pollHotkeys` & `SaveWorldCacheToDisk`, and uses `rapidjson`.
2. R3 `megamind/` Preload Contracts:
   - Offline `megamind/raw/*.json` integrity & R3 specification proofs.
   - Live `MASTER_LUA_CODE` preload manifest (`_G.WarmReadOnlyEngineCaches`) verification:
     every `DataCenter.*TemplateManager` exists with `msgs == []` & `events == []`,
     every `TableName.*` exists in `enums complete.json` & `xml tables manifest.json`
     and excludes heavy tables, strict exclusions never appear as preload targets,
     and all 7+ readiness checks + `_G._WarmupState` fields are present.
3. R4 Guardrail Contracts:
   - Zero occurrences of R4 prohibited terms across modified/added project files.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from lupa import LuaRuntime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _read_text(rel_path: str) -> str:
    return (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")


def _extract_python_function_src(src: str, func_name: str) -> str:
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    return ""


def _extract_lua_block(lua_src: str, header_pattern: str, max_chars: int = 12000) -> str:
    """Extract a Lua function/block starting at header_pattern up to a clean top-level `end` or slice."""
    m = re.search(header_pattern, lua_src)
    if not m:
        return ""
    start = m.start()
    indent_match = re.match(r"^[ \t]*", lua_src[lua_src.rfind("\n", 0, start) + 1 : start])
    base_indent = len(indent_match.group(0)) if indent_match else 0
    lines = lua_src[start : start + max_chars].splitlines()
    collected = [lines[0]]
    for line in lines[1:]:
        collected.append(line)
        stripped = line.lstrip(" \t")
        cur_indent = len(line) - len(stripped)
        if cur_indent <= base_indent and re.match(r"^end\b", stripped):
            break
    return "\n".join(collected)


def _extract_lua_if_true_branch(lua_src: str, if_pattern: str, max_chars: int = 12000) -> str:
    """Extract only the true-branch of a Lua `if ... then ... [else ...] end` block using indentation."""
    m = re.search(if_pattern, lua_src)
    if not m:
        return ""
    start = m.start()
    indent_match = re.match(r"^[ \t]*", lua_src[lua_src.rfind("\n", 0, start) + 1 : start])
    base_indent = len(indent_match.group(0)) if indent_match else 0
    if_block = _extract_lua_block(lua_src, if_pattern, max_chars=max_chars)
    if not if_block:
        return ""
    lines = if_block.splitlines()
    collected = [lines[0]]
    for line in lines[1:]:
        stripped = line.lstrip(" \t")
        cur_indent = len(line) - len(stripped)
        if cur_indent <= base_indent and re.match(r"^(?:else|elseif|end)\b", stripped):
            break
        collected.append(line)
    return "\n".join(collected)


def _strip_lua_comments(lua_code: str) -> str:
    """Strip Lua `--` and `--[[...]]` comments outside string literals, preserving newlines."""
    out: list[str] = []
    i = 0
    n = len(lua_code)
    while i < n:
        ch = lua_code[i]
        if ch in ('"', "'"):
            quote = ch
            out.append(ch)
            i += 1
            while i < n:
                c = lua_code[i]
                out.append(c)
                i += 1
                if c == "\\" and i < n:
                    out.append(lua_code[i])
                    i += 1
                elif c == quote:
                    break
        elif ch == "-" and i + 1 < n and lua_code[i + 1] == "-":
            m_long = re.match(r"--\[(=*)\[", lua_code[i:])
            if m_long:
                end_pat = "]" + m_long.group(1) + "]"
                end_idx = lua_code.find(end_pat, i + len(m_long.group(0)))
                if end_idx == -1:
                    break
                seg = lua_code[i : end_idx + len(end_pat)]
                out.append("\n" * seg.count("\n"))
                i = end_idx + len(end_pat)
            else:
                nl = lua_code.find("\n", i)
                if nl == -1:
                    break
                i = nl
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _extract_r3_warmup_code(master_lua: str) -> tuple[str, str]:
    """Anchor strictly on `function _G.WarmReadOnlyEngineCaches(` and include only its dedicated R3 helpers."""
    m_warm = re.search(r"function\s+_G\.WarmReadOnlyEngineCaches\s*\(", master_lua)
    if not m_warm:
        return "", ""
    warm_start = m_warm.start()
    warm_fn = _extract_lua_block(master_lua, r"function\s+_G\.WarmReadOnlyEngineCaches\s*\(", max_chars=30000)

    # Never cross backwards into StartBackgroundWorldPreloader / sStep / DoSendViewRequest / runCameraStreamer
    boundary = max(
        master_lua.rfind("DoSendViewRequest", 0, warm_start),
        master_lua.rfind("StartBackgroundWorldPreloader", 0, warm_start),
        master_lua.rfind("TriggerFullMapLoad", 0, warm_start),
        master_lua.rfind("runCameraStreamer", 0, warm_start),
    )
    search_from = 0 if boundary == -1 else boundary
    helper_positions = []
    for pat in (
        r"_G\._hzPreloadDone\b",
        r"_G\._WarmupState\b",
        r"local\s+function\s+_checkPreloadReadiness\s*\(",
        r"local\s+function\s+_warmXmlTable\s*\(",
    ):
        mh = re.search(pat, master_lua[search_from:warm_start])
        if mh:
            helper_positions.append(search_from + mh.start())
    helper_start = min(helper_positions) if helper_positions else warm_start
    r3_block = master_lua[helper_start:warm_start] + warm_fn
    return warm_fn, r3_block


def _extract_master_lua_code() -> str:
    src = _read_text("daemon/apply widescreen smooth map.py")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "MASTER_LUA_CODE":
                    return ast.literal_eval(node.value)
    raise AssertionError("MASTER_LUA_CODE not found in daemon/apply widescreen smooth map.py")


def _extract_farm_eco_lua_patch() -> str:
    src = _read_text("daemon/lastz auto engine daemon.py")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "FARM_ECO_LUA_PATCH":
                    return ast.literal_eval(node.value)
    raise AssertionError("FARM_ECO_LUA_PATCH not found in daemon/lastz auto engine daemon.py")


def _extract_lua_string_array(lua_src: str, var_name: str) -> list[str]:
    """Extract all quoted string literals from `local <var_name> = { ... }`."""
    m = re.search(rf"\blocal\s+{re.escape(var_name)}\s*=\s*\{{(.*?)\}}", lua_src, flags=re.S)
    if not m:
        return []
    return re.findall(r'["\']([A-Za-z0-9_]+)["\']', m.group(1))


def _lua_to_py(val: Any) -> Any:
    """Recursively convert lupa Lua tables into plain Python dicts/lists for JSON encoding."""
    if val is None or isinstance(val, (bool, int, float, str)):
        return val
    if hasattr(val, "items"):
        items = list(val.items())
        if not items:
            return {}
        if all(isinstance(k, int) and k >= 1 for k, _ in items):
            keys = sorted(k for k, _ in items)
            if keys == list(range(1, len(keys) + 1)):
                return [_lua_to_py(val[k]) for k in keys]
        return {str(k): _lua_to_py(v) for k, v in items}
    return str(val)


def _py_to_lua(lua: LuaRuntime, val: Any) -> Any:
    """Recursively convert plain Python dicts/lists into Lua tables."""
    if val is None or isinstance(val, (bool, int, float, str)):
        return val
    if isinstance(val, list):
        tbl = lua.table()
        for idx, item in enumerate(val, start=1):
            tbl[idx] = _py_to_lua(lua, item)
        return tbl
    if isinstance(val, dict):
        tbl = lua.table()
        for k, v in val.items():
            tbl[k] = _py_to_lua(lua, v)
        return tbl
    return str(val)


def _boot_master_lua_in_lupa(
    master_lua: str,
    *,
    cache_dir: str | None = None,
    active_sid: int = 702,
    pre_lua: str = "",
) -> tuple[LuaRuntime, Any]:
    """Boot the real MASTER_LUA_CODE inside an isolated lupa LuaRuntime with mock Unity/XLua stubs."""
    lua = LuaRuntime(unpack_returned_tuples=True)
    g = lua.globals()

    def _rjson_encode(obj: Any) -> str:
        return json.dumps(_lua_to_py(obj))

    def _rjson_decode(raw: str) -> Any:
        return _py_to_lua(lua, json.loads(str(raw)))

    rjson_mod = lua.table_from({"encode": _rjson_encode, "decode": _rjson_decode})
    g["_test_rjson_mod"] = rjson_mod
    g["_test_active_sid"] = int(active_sid)
    if cache_dir is not None:
        g["_MasterCacheDirOverride"] = str(cache_dir).replace("\\", "/")

    lua.execute(
        r"""
        package.loaded.rapidjson = _test_rjson_mod
        TileCountX = 1000
        typeof = function(x) return x end

        local function _makeVec(x, y, z)
            return { x = x or 0, y = y or 0, z = z or 0 }
        end
        local _vecMt = { __call = function(_, x, y, z) return _makeVec(x, y, z) end }
        local Vec2 = setmetatable({ zero = _makeVec(0, 0, 0) }, _vecMt)
        local Vec3 = setmetatable({ one = _makeVec(1, 1, 1), zero = _makeVec(0, 0, 0) }, _vecMt)

        CS = {
            UnityEngine = {
                Application = { targetFrameRate = 60, runInBackground = true, backgroundLoadingPriority = 0 },
                QualitySettings = {
                    vSyncCount = 1, maxQueuedFrames = 2, shadowDistance = 35.0,
                    asyncUploadTimeSlice = 4, asyncUploadBufferSize = 16,
                    realtimeReflectionProbes = true, antiAliasing = 0,
                    anisotropicFiltering = 0, shadows = 0, shadowResolution = 0,
                    masterTextureLimit = 0, lodBias = 1.0,
                },
                AnisotropicFiltering = { ForceEnable = 2 },
                ShadowQuality = { Disable = 0, All = 2 },
                ShadowResolution = { High = 2 },
                ThreadPriority = { High = 4 },
                AnimatorCullingMode = { CullUpdateTransforms = 1 },
                ParticleSystemCullingMode = { Pause = 0 },
                Rendering = {
                    ShadowCastingMode = { Off = 0 },
                    GraphicsSettings = { currentRenderPipeline = nil },
                },
                Camera = { main = nil },
                Renderer = {},
                Animator = {},
                ParticleSystem = {},
                Vector2 = Vec2,
                Vector3 = Vec3,
                Time = { frameCount = 1 },
                Screen = { width = 1920, height = 1080 },
                KeyCode = { F1 = 1, F2 = 2, F3 = 3, F4 = 4, F5 = 5, F6 = 6, Home = 7 },
                Input = { GetKey = function() return false end },
            },
            System = {
                Reflection = { BindingFlags = { Public = 16, NonPublic = 32, Instance = 4 } },
                Convert = { ToInt32 = function(v) return math.floor(tonumber(v) or 0) end },
                Enum = { ToObject = function(_, v) return v end },
            },
            AutoAdjustLod = {},
            SceneManager = { World = nil },
            GameEntry = {},
            ShaderManager = {},
            ResourceManager = { PreloadType = {} },
        }

        _G._testTimerQueue = {}
        local _tmInst = {}
        function _tmInst:DelayInvoke(fn, delay)
            _G._testTimerQueue[#_G._testTimerQueue + 1] = { fn = fn, delay = delay }
        end
        TimerManager = {
            GetInstance = function() return _tmInst end,
        }

        DataCenter = {
            WorldPointManager = {
                aoiServerId = _test_active_sid,
                isInit = false,
                allViewPoints = {},
                allObj = {},
                toBuildSet = {},
                lodLv = 4,
                GetServerLod = function() return 0 end,
            },
        }
        SceneManager = { CurrSceneID = 1, World = nil }
        LuaEntry = {
            m_isStartGame = true,
            isInitDB = true,
            Player = {
                uid = "uid_test_1",
                GetSelfServerId = function() return _test_active_sid end,
            },
        }
        LocalController = {
            instance = function()
                return {
                    HasTableInMem = function() return false end,
                    isTableLoaded = function() return false end,
                    getTable = function(_, name) return { _name = name } end,
                }
            end,
        }
        UIManager = {
            GetInstance = function() return { __cProjectStateReady = true } end,
        }
        TableName = {}
        """
    )
    if pre_lua:
        lua.execute(pre_lua)

    payload = master_lua.replace("__FORCE_FULL_LOAD_FLAG__", "false")
    lua.execute(payload)
    return lua, g


class TestR2HookAndBridgeContracts(unittest.TestCase):
    """R2 Hook, Frida Bridge, Spatial Bucketing, Reflection Cache & GC Contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.daemon_src = _read_text("daemon/lastz auto engine daemon.py")
        cls.flush_src = _read_text("tools/flush game memory.py")
        cls.master_lua = _extract_master_lua_code()

    def test_daemon_attempt_patch_uses_frida_eval_lua(self) -> None:
        """attempt_patch() and attempt_farm_eco_patch() must route via frida_eval_lua (no raw frida.attach)."""
        fn_src = _extract_python_function_src(self.daemon_src, "attempt_patch")
        self.assertTrue(fn_src, "attempt_patch() not found")
        self.assertIn("frida_eval_lua", fn_src)
        self.assertNotIn("frida.attach(", fn_src)

        farm_fn_src = _extract_python_function_src(self.daemon_src, "attempt_farm_eco_patch")
        self.assertTrue(farm_fn_src, "attempt_farm_eco_patch() not found")
        self.assertIn("frida_eval_lua", farm_fn_src)
        self.assertNotIn("frida.attach(", farm_fn_src)

    def test_flush_game_memory_uses_frida_eval_lua(self) -> None:
        """flush_memory() in tools/flush game memory.py must route via frida_eval_lua (no raw frida.attach)."""
        fn_src = _extract_python_function_src(self.flush_src, "flush_memory")
        self.assertTrue(fn_src, "flush_memory() not found")
        self.assertIn("frida_eval_lua", fn_src)
        self.assertNotIn("frida.attach(", fn_src)

    def test_farm_eco_lua_patch_closure_free_and_change_only(self) -> None:
        """FARM_ECO_LUA_PATCH ecoBeat & _ecoTickWork must be closure-free, change-only, and recover FPS drift."""
        eco_block = _extract_lua_block(self.daemon_src, r"local function ecoBeat\s*\(")
        self.assertTrue(eco_block, "ecoBeat() not found in FARM_ECO_LUA_PATCH")
        self.assertNotIn(
            "pcall(function()",
            eco_block,
            "ecoBeat() must not allocate an anonymous pcall(function() ... end) closure every 1.0s tick",
        )
        self.assertIn("pcall(_ecoTickWork)", eco_block, "ecoBeat() must delegate to _ecoTickWork")

        tick_work = _extract_lua_block(self.daemon_src, r"local function _ecoTickWork\s*\(")
        self.assertTrue(tick_work, "_ecoTickWork() not found in FARM_ECO_LUA_PATCH")
        self.assertNotIn(
            "pcall(function()",
            tick_work,
            "_ecoTickWork() must remain closure-free on every 1.0s tick",
        )
        self.assertRegex(
            tick_work,
            re.compile(r"app\.targetFrameRate\s*~=\s*tfps"),
            "_ecoTickWork() must detect in-scene FPS drift via `app.targetFrameRate ~= tfps`",
        )

        apply_block = _extract_lua_block(self.daemon_src, r"local function applyFarmPerfSettings\s*\(")
        self.assertTrue(apply_block, "applyFarmPerfSettings() not found")
        # Verify change-only guards on Application / QualitySettings writes
        self.assertRegex(apply_block, re.compile(r"app\.runInBackground\s*~=\s*true"))
        self.assertRegex(apply_block, re.compile(r"qs\.softParticles\s*~=\s*false"))
        self.assertRegex(apply_block, re.compile(r"qs\.realtimeReflectionProbes\s*~=\s*false"))

        # Behavioral lupa check: external FPS reset is recovered by _ecoTickWork on next ecoBeat
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(
            r"""
            _G._ecoQueue = {}
            CS = {
                UnityEngine = {
                    Application = { isFocused = true, targetFrameRate = 60, runInBackground = false },
                    Screen = { width = 1280, height = 720 },
                    QualitySettings = {
                        vSyncCount = 1, shadows = 2, antiAliasing = 4,
                        softParticles = true, realtimeReflectionProbes = true,
                    },
                    ShadowQuality = { Disable = 0 },
                },
            }
            SceneManager = { CurrSceneID = 1 }
            LuaEntry = { Player = { uid = "farm_uid_1" } }
            DataCenter = { AllianceHelpDataManager = { GetHelpNum = function() return 0 end } }
            local tm = {}
            function tm:DelayInvoke(fn, delay)
                _G._ecoQueue[#_G._ecoQueue + 1] = fn
            end
            TimerManager = { GetInstance = function() return tm end }
            """
        )
        res = lua.execute(_extract_farm_eco_lua_patch())
        self.assertTrue(str(res).startswith("SUCCESS_FARM_SMART_FPS_"))
        self.assertEqual(lua.eval("CS.UnityEngine.Application.targetFrameRate"), 120)
        # Simulate game engine resetting targetFrameRate in-scene while focus/width/scene stay unchanged
        lua.execute("CS.UnityEngine.Application.targetFrameRate = 30")
        lua.execute("local fn = table.remove(_G._ecoQueue, 1); fn()")
        self.assertEqual(
            lua.eval("CS.UnityEngine.Application.targetFrameRate"),
            120,
            "_ecoTickWork() failed to recover targetFrameRate after in-scene FPS drift",
        )

    def test_master_engine_spatial_bucketing_and_incremental_count(self) -> None:
        """MASTER_LUA_CODE _streamWork must use 50x50 spatial bucketing (not pairs(allViewPoints)) and incremental count."""
        # Spatial bucket size 50 & grid structure
        self.assertRegex(
            self.master_lua,
            re.compile(r"(BUCKET_SIZE|spatialBucket|gridBucket|GridBuckets)\s*=|math\.floor\([^)]*/\s*50\s*\)"),
            "MASTER_LUA_CODE must implement 50x50 spatial grid bucketing",
        )
        streamer_block = _extract_lua_block(self.master_lua, r"local function runCameraStreamer\s*\(")
        self.assertTrue(streamer_block, "runCameraStreamer() not found")
        self.assertIn("pcall(_streamWork)", streamer_block, "runCameraStreamer() must delegate to _streamWork")
        self.assertNotIn("pcall(function()", streamer_block, "runCameraStreamer() must be closure-free")

        stream_work = _extract_lua_block(self.master_lua, r"local function _streamWork\s*\(")
        self.assertTrue(stream_work, "_streamWork() not found in MASTER_LUA_CODE")
        self.assertIn("_MasterSpatialGrid", stream_work, "_streamWork() must iterate _G._MasterSpatialGrid")
        self.assertIn("BUCKET_SIZE", stream_work, "_streamWork() must compute bucket bounds using BUCKET_SIZE")
        self.assertRegex(
            stream_work,
            re.compile(r"pairs\s*\(\s*bucket\s*\)"),
            "_streamWork() must iterate points inside nearby spatial buckets",
        )
        self.assertNotRegex(
            stream_work,
            re.compile(r"pairs\s*\(\s*(?:curMgr|mgr)\.allViewPoints\s*\)"),
            "_streamWork() must iterate nearby spatial buckets instead of scanning all 73k curMgr.allViewPoints",
        )
        overlay_block = _extract_lua_block(self.master_lua, r"function _G\.RefreshMasterOverlayUI\s*\(")
        self.assertTrue(overlay_block, "RefreshMasterOverlayUI() not found")
        self.assertNotIn(
            "SafeTableCount(mgr.allViewPoints)",
            overlay_block,
            "RefreshMasterOverlayUI() must use incremental point count instead of O(73k) SafeTableCount(mgr.allViewPoints)",
        )

    def test_master_engine_no_unconditional_force_stream_rescan_in_sstep(self) -> None:
        """sStep() must not unconditionally set _G._ForceStreamRescan = true on every sector tick."""
        sstep_block = _extract_lua_block(self.master_lua, r"local function sStep\s*\(")
        self.assertTrue(sstep_block, "sStep() not found in MASTER_LUA_CODE")
        # Check inside the active `if sIdx <= #allSectors then ... else` branch (indentation-aware)
        sector_branch = _extract_lua_if_true_branch(sstep_block, r"if\s+sIdx\s*<=\s*#allSectors\s+then")
        self.assertTrue(sector_branch, "if sIdx <= #allSectors then branch not found in sStep()")
        self.assertNotIn(
            "_G._ForceStreamRescan = true",
            sector_branch,
            "sStep() must not force a full rescan on every sector tick",
        )

    def test_master_engine_cached_reflection_material_renderer_and_shadow_reconciled(self) -> None:
        """Verify cached reflection FieldInfo/ints, memoized Material IDs, cached Renderer, and reconciled shadowDistance."""
        # 1. Reflection FieldInfo / boxed int caching (accepts either pre-populated rc.* or nil-guarded lazy-once init)
        expand_block = _extract_lua_block(self.master_lua, r"local function expandAdjuster\s*\(")
        self.assertTrue(expand_block, "expandAdjuster() not found")
        self.assertIn("rc.adjSettingsField", expand_block, "expandAdjuster() must use cached rc.adjSettingsField")
        self.assertIn("boxedInts", expand_block, "expandAdjuster() must reuse cached rc.boxedInts")
        self.assertNotIn("ToInt32", expand_block, "expandAdjuster() must not box Int32s per call")

        has_settings_lookup = bool(
            re.search(r'GetType\s*\(\s*\)\s*:\s*GetField\s*\(\s*["\']settings["\']', expand_block)
        )
        if has_settings_lookup:
            # Lazy-once init inside expandAdjuster must be nil-guarded and stored in rc.adjSettingsField before the loop
            for_pos = expand_block.find("for i = 0")
            settings_pos = expand_block.find('"settings"')
            self.assertTrue(
                for_pos == -1 or settings_pos < for_pos,
                "expandAdjuster() must not call GetField('settings') inside the settings loop",
            )
            self.assertRegex(
                expand_block,
                re.compile(
                    r"if\b[^\n]*(?:==\s*nil|nil\s*==)[^\n]*then.*?GetField\s*\(\s*[\"']settings[\"'].*?rc\.adjSettingsField\s*=",
                    re.S,
                ),
                "expandAdjuster() calls GetField('settings') without a nil-guarded lazy rc.adjSettingsField cache!",
            )
        else:
            # Pre-populated outside expandAdjuster
            self.assertIn("adjSettingsField", self.master_lua)

        if re.search(r'GetField\s*\(\s*["\']targets["\']', expand_block):
            self.assertRegex(
                expand_block,
                re.compile(
                    r"if\b[^\n]*(?:==\s*nil|nil\s*==)[^\n]*then.*?GetField\s*\(\s*[\"']targets[\"'].*?rc\.adjTargetsField\s*=",
                    re.S,
                ),
                "expandAdjuster() calls GetField('targets') without a nil-guarded lazy rc.adjTargetsField cache!",
            )

        # 2. Material instance ID memoization in optimizeInstance
        opt_block = _extract_lua_block(self.master_lua, r"local function optimizeInstance\s*\(")
        self.assertTrue(opt_block, "optimizeInstance() not found")
        self.assertRegex(
            opt_block,
            re.compile(r"GetInstanceID\s*\("),
            "optimizeInstance() must memoize seen Material instance IDs via GetInstanceID()",
        )

        # 3. Cached Renderer in SetProtectRenderVisible (extract from unsliced master_lua to preserve base_indent)
        prot_block = _extract_lua_block(self.master_lua, r"wbo\.SetProtectRenderVisible\s*=\s*function")
        self.assertTrue(prot_block, "SetProtectRenderVisible hook not found")
        self.assertNotIn("fastBuildLodChange", prot_block, "prot_block overflowed past SetProtectRenderVisible")
        self.assertLess(len(prot_block), 4000, "prot_block unexpectedly large; check indentation extraction")
        self.assertRegex(
            prot_block,
            re.compile(r"_cachedProtect(?:Renderer)?|_protectRenderer|_cachedRenderer|_prRenderer|_prMesh|\._renderer\b"),
            "SetProtectRenderVisible must cache the Renderer component on self instead of calling GetComponent every call",
        )

        # 4. Reconciled shadowDistance between ApplyLastZWorldMaster and _hbWork() (plus closure-free hb())
        hb_block = _extract_lua_block(self.master_lua, r"local function hb\s*\(")
        self.assertTrue(hb_block, "hb() not found")
        self.assertIn("pcall(_hbWork)", hb_block, "hb() must delegate to _hbWork")
        self.assertNotIn("pcall(function()", hb_block, "hb() must be closure-free")

        hb_work = _extract_lua_block(self.master_lua, r"local function _hbWork\s*\(")
        self.assertTrue(hb_work, "_hbWork() not found in MASTER_LUA_CODE")
        self.assertIn(
            "shadowDistance = 120.0",
            hb_work,
            "_hbWork() must actively maintain shadowDistance = 120.0",
        )
        self.assertNotIn(
            "shadowDistance = 35.0",
            hb_work,
            "_hbWork() must reconcile shadowDistance with ApplyLastZWorldMaster (120.0), not reset to 35.0",
        )

        # 5. Idempotent SetGraphicQuality wrapper guard (MEDIUM #5)
        self.assertIn("qsu._origSetGraphicQuality", self.master_lua)

    def test_master_engine_throttled_hotkeys_disk_save_and_rapidjson(self) -> None:
        """pollHotkeys must be throttled (>=0.04s), SaveWorldCacheToDisk dirty-throttled, and rapidjson used."""
        hk_block = _extract_lua_block(self.master_lua, r"local function pollHotkeys\s*\(")
        self.assertTrue(hk_block, "pollHotkeys() not found")
        m_delay = re.search(r"DelayInvoke\s*\(\s*pollHotkeys\s*,\s*([0-9.]+)\s*\)", hk_block)
        self.assertIsNotNone(m_delay, "DelayInvoke(pollHotkeys, ...) not found")
        self.assertGreaterEqual(float(m_delay.group(1)), 0.04, "pollHotkeys should be throttled from 40Hz (0.025s) to >= 0.04s")

        save_block = _extract_lua_block(self.master_lua, r"function _G\.SaveWorldCacheToDisk\s*\(")
        self.assertTrue(save_block, "SaveWorldCacheToDisk() not found")
        self.assertRegex(
            save_block,
            re.compile(r"dirty|lastSave|Throttle|SaveInterval", re.I),
            "SaveWorldCacheToDisk must be dirty-gated / throttled",
        )
        self.assertIn("rapidjson", self.master_lua)
        self.assertRegex(
            self.master_lua,
            re.compile(r"\b(?:rjson|rapidjson|rj)\.encode\b"),
            "MASTER_LUA_CODE must encode JSON via rapidjson (rjson/rapidjson/rj.encode)",
        )

    def test_lua_save_world_cache_to_disk_wb_rollback_and_throttle(self) -> None:
        """lupa: SaveWorldCacheToDisk uses 'wb', rolls back on os.rename failure, and enforces 20s throttle."""
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            target_file = cache_dir / "world_map_cache_s702.json"
            original_sentinel = '{"1001":{"pointType":6,"sentinel":"KEEP_ME_INTACT"}}'
            target_file.write_text(original_sentinel, encoding="utf-8")

            lua, g = _boot_master_lua_in_lupa(self.master_lua, cache_dir=str(cache_dir), active_sid=702)

            # Instrument io.open modes, controllable clock, and os.rename fault injection
            lua.execute(
                r"""
                _G._testOpenModes = {}
                _G._testClock = 1000
                _G._testFailTmpRename = false
                _G._testFailBakRename = false
                local _origOpen = io.open
                io.open = function(path, mode)
                    _G._testOpenModes[#_G._testOpenModes + 1] = { path = path, mode = mode }
                    return _origOpen(path, mode)
                end
                os.time = function() return _G._testClock end
                local _origRename = os.rename
                os.rename = function(src, dst)
                    if _G._testFailTmpRename and tostring(src):sub(-4) == ".tmp" then
                        return nil, "locked"
                    end
                    if _G._testFailBakRename and tostring(dst):sub(-4) == ".bak" then
                        return nil, "locked"
                    end
                    return _origRename(src, dst)
                end
                """
            )

            # 1. Backup-rename-restore rollback when tmp -> target os.rename returns (nil, "locked")
            lua.execute(
                r"""
                _G._PersistentWorldPointCacheByServer[702] = {
                    [1001] = { pointType = 6, name = "Alpha_New_Long_Payload_1234567890" },
                    [1002] = { pointType = 6, name = "Beta_New_Long_Payload_1234567890" },
                }
                _G._WorldCacheDirtyCount[702] = 7
                _G._WorldCacheLoadedOk[702] = true
                _G._WorldCacheLastSaveTs[702] = 0
                _G._testFailTmpRename = true
                _G.SaveWorldCacheToDisk(702, true)
                _G._testFailTmpRename = false
                """
            )
            self.assertEqual(
                target_file.read_text(encoding="utf-8"),
                original_sentinel,
                "Original cache file must be restored intact when os.rename(tmp, target) returns (nil, 'locked')",
            )
            leftovers = [p.name for p in cache_dir.iterdir() if p.suffix in (".tmp", ".bak")]
            self.assertEqual(leftovers, [], f"Rollback leaked temporary/backup files: {leftovers}")
            self.assertEqual(
                lua.eval("_G._WorldCacheDirtyCount[702]"),
                7,
                "_WorldCacheDirtyCount must remain dirty after failed rename",
            )
            self.assertEqual(lua.eval("_G._WorldCacheLastSaveTs[702]"), 0)

            # Verify binary "wb" mode was used for tmp write (never text "w")
            write_modes = lua.eval(
                r"""
                (function()
                    local out = {}
                    for i = 1, #_G._testOpenModes do
                        local rec = _G._testOpenModes[i]
                        if tostring(rec.path):sub(-4) == ".tmp" then
                            out[#out + 1] = rec.mode
                        end
                    end
                    return table.concat(out, ",")
                end)()
                """
            )
            self.assertEqual(write_modes, "wb", f"Expected tmp write mode 'wb', got: {write_modes!r}")

            # 2. Failure when moving existing file -> .bak also keeps original intact, cleans .tmp, keeps dirty
            lua.execute(
                r"""
                _G._testFailBakRename = true
                _G.SaveWorldCacheToDisk(702, true)
                _G._testFailBakRename = false
                """
            )
            self.assertEqual(target_file.read_text(encoding="utf-8"), original_sentinel)
            leftovers_bak = [p.name for p in cache_dir.iterdir() if p.suffix in (".tmp", ".bak")]
            self.assertEqual(leftovers_bak, [], f"Failed backup rename leaked files: {leftovers_bak}")
            self.assertEqual(lua.eval("_G._WorldCacheDirtyCount[702]"), 7)

            # 3. Clean forced save succeeds at t=1000 and resets dirty count
            lua.execute("_G.SaveWorldCacheToDisk(702, true)")
            self.assertEqual(lua.eval("_G._WorldCacheDirtyCount[702]"), 0)
            self.assertEqual(lua.eval("_G._WorldCacheLastSaveTs[702]"), 1000)
            saved_json = json.loads(target_file.read_text(encoding="utf-8"))
            self.assertIn("1001", saved_json)
            self.assertIn("1002", saved_json)
            self.assertEqual([p.name for p in cache_dir.iterdir() if p.suffix in (".tmp", ".bak")], [])

            # 4. 20s minimum interval throttle on non-forced saves (even when dirty >= 150!)
            lua.execute(
                r"""
                _G._PersistentWorldPointCacheByServer[702][1003] = { pointType = 6, name = "Gamma_Throttled" }
                _G._WorldCacheDirtyCount[702] = 500
                _G._testClock = 1010
                _G.SaveWorldCacheToDisk(702, false)
                """
            )
            self.assertEqual(lua.eval("_G._WorldCacheDirtyCount[702]"), 500, "Save at +10s must be throttled")
            self.assertEqual(lua.eval("_G._WorldCacheLastSaveTs[702]"), 1000)
            self.assertNotIn("1003", json.loads(target_file.read_text(encoding="utf-8")))

            lua.execute(
                r"""
                _G._testClock = 1019
                _G.SaveWorldCacheToDisk(702, false)
                """
            )
            self.assertEqual(lua.eval("_G._WorldCacheDirtyCount[702]"), 500, "Save at +19s must still be throttled")

            lua.execute(
                r"""
                _G._testClock = 1020
                _G.SaveWorldCacheToDisk(702, false)
                """
            )
            self.assertEqual(lua.eval("_G._WorldCacheDirtyCount[702]"), 0, "Save at +20s must flush cleanly")
            self.assertEqual(lua.eval("_G._WorldCacheLastSaveTs[702]"), 1020)
            self.assertIn("1003", json.loads(target_file.read_text(encoding="utf-8")))

    def test_lua_resolve_cache_server_id_fallback(self) -> None:
        """lupa: ResolveCacheServerId must fall back nil and 0 to GetActiveWorldServerId() (never staying 0)."""
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            s702_file = cache_dir / "world_map_cache_s702.json"
            s0_file = cache_dir / "world_map_cache.json"

            lua, _ = _boot_master_lua_in_lupa(self.master_lua, cache_dir=str(cache_dir), active_sid=702)

            # Seed bucket 702 and trigger SaveWorldCacheToDisk(nil, true) & SaveWorldCacheToDisk(0, true)
            lua.execute(
                r"""
                _G._PersistentWorldPointCacheByServer[702] = {
                    [500501] = { pointType = 6, serverId = 702, name = "FallbackNil" }
                }
                _G._WorldCacheDirtyCount[702] = 1
                _G._WorldCacheLoadedOk[702] = true
                _G.SaveWorldCacheToDisk(nil, true)
                """
            )
            self.assertTrue(s702_file.is_file(), "SaveWorldCacheToDisk(nil, true) must resolve to world_map_cache_s702.json")
            self.assertFalse(s0_file.exists(), "SaveWorldCacheToDisk(nil, true) must NOT write world_map_cache.json (sid=0)")

            # Now test serverId = 0 with aoiServerId = 0 so it falls through to LuaEntry.Player:GetSelfServerId() -> 702
            lua.execute(
                r"""
                DataCenter.WorldPointManager.aoiServerId = 0
                _G._PersistentWorldPointCacheByServer[702][500502] = { pointType = 6, serverId = 702, name = "FallbackZero" }
                _G._WorldCacheDirtyCount[702] = 1
                _G.SaveWorldCacheToDisk(0, true)
                """
            )
            self.assertFalse(s0_file.exists(), "SaveWorldCacheToDisk(0, true) must NOT fall back to sid=0")
            saved = json.loads(s702_file.read_text(encoding="utf-8"))
            self.assertIn("500502", saved, "SaveWorldCacheToDisk(0, true) must write to world_map_cache_s702.json")

            # Clear in-memory caches and verify RestoreWorldMapCache(0) & RestoreWorldMapCache(nil) load s702
            lua.execute(
                r"""
                _G._PersistentWorldPointCacheByServer = {}
                _G._PersistentDesertCacheByServer = {}
                DataCenter.WorldPointManager.allViewPoints = {}
                _G.RestoreWorldMapCache(0)
                """
            )
            self.assertIsNotNone(lua.eval("_G._PersistentWorldPointCacheByServer[702]"))
            self.assertIsNone(lua.eval("_G._PersistentWorldPointCacheByServer[0]"))
            self.assertIsNotNone(lua.eval("DataCenter.WorldPointManager.allViewPoints[500502]"))

    def test_lua_remove_point_info_purge_and_v80_to_v81_hot_upgrade(self) -> None:
        """lupa: v8.0->v8.1 hot-upgrade avoids double-wrap and RemovePointInfo purges ptCache & desertCache."""
        with tempfile.TemporaryDirectory() as tmp:
            lua, _ = _boot_master_lua_in_lupa(self.master_lua, cache_dir=tmp, active_sid=702)

            # Simulate an already-hooked v8.0 prototype + QualitySettingUtil before running v8.1 ApplyLastZWorldMaster
            lua.execute(
                r"""
                _G._baseAddCalls = 0
                _G._baseAddDesertCalls = 0
                _G._baseRemoveCalls = 0
                _G._baseQsuCalls = 0

                local baseAdd = function(self, idx, info)
                    _G._baseAddCalls = _G._baseAddCalls + 1
                    self.allViewPoints[idx] = { pointIndex = idx, pointInfo = info }
                    return "added"
                end
                local baseAddDesert = function(self, idx, info)
                    _G._baseAddDesertCalls = _G._baseAddDesertCalls + 1
                    self.allViewPoints[idx] = self.allViewPoints[idx] or { pointIndex = idx }
                    self.allViewPoints[idx].desertInfo = info
                    return "added_desert"
                end
                local baseClose = function(self) return "closed" end
                local baseStartUp = function(self) return "started" end

                local proto = {
                    _masterCacheLifecycleHooked = true,
                    _masterCacheLifecycleHookedV8 = true,
                    _origAddPointInfoV8 = baseAdd,
                    _origAddDesertInfoV8 = baseAddDesert,
                    _origCloseV8 = baseClose,
                    _origStartUpV8 = baseStartUp,
                    -- Simulate stale v8.0 wrappers that would double-wrap if v8.1 wrapped proto.AddPointInfo directly
                    AddPointInfo = function(self, idx, info)
                        _G._baseAddCalls = _G._baseAddCalls + 100
                        return baseAdd(self, idx, info)
                    end,
                    AddDesertInfo = function(self, idx, info)
                        _G._baseAddDesertCalls = _G._baseAddDesertCalls + 100
                        return baseAddDesert(self, idx, info)
                    end,
                    Close = baseClose,
                    StartUp = baseStartUp,
                }
                local mgr = setmetatable({
                    aoiServerId = 702,
                    isInit = false,
                    allViewPoints = {},
                    allObj = {},
                    toBuildSet = {},
                    lodLv = 4,
                    GetServerLod = function() return 0 end,
                    RemovePointInfo = function(self, idx, forceRemove, isOutOfView)
                        _G._baseRemoveCalls = _G._baseRemoveCalls + 1
                        self.allViewPoints[idx] = nil
                        return "removed"
                    end,
                }, { __index = proto })
                DataCenter.WorldPointManager = mgr
                _G._testProto = proto

                local qsu = {
                    SetGraphicQuality = function(...)
                        _G._baseQsuCalls = _G._baseQsuCalls + 1
                    end,
                }
                package.loaded["Util.QualitySettingUtil"] = qsu
                _G._testQsu = qsu
                """
            )

            # Run v8.1 ApplyLastZWorldMaster TWICE to verify v8.0->v8.1 hot-upgrade & idempotency
            res1 = lua.eval("_G.ApplyLastZWorldMaster()")
            res2 = lua.eval("_G.ApplyLastZWorldMaster()")
            self.assertEqual(res1, "HOOKS_READY_WAITING_FOR_WORLD_VIEW")
            self.assertEqual(res2, "HOOKS_READY_WAITING_FOR_WORLD_VIEW")
            self.assertTrue(lua.eval("_G._testProto._masterCacheLifecycleHookedV81"))

            # Verify zero double-wrapping on AddPointInfo, AddDesertInfo, and SetGraphicQuality
            lua.execute(
                r"""
                local mgr = DataCenter.WorldPointManager
                mgr:AddPointInfo(100501, { pointType = 6, name = "Base1" })
                mgr:AddDesertInfo(100501, { desertType = 2 })
                mgr:AddPointInfo(100502, { pointType = 6, name = "Base2" })
                _G._testQsu.SetGraphicQuality(2)
                """
            )
            self.assertEqual(lua.eval("_G._baseAddCalls"), 2, "v8.0->v8.1 hot-upgrade double-wrapped AddPointInfo!")
            self.assertEqual(lua.eval("_G._baseAddDesertCalls"), 1, "v8.0->v8.1 hot-upgrade double-wrapped AddDesertInfo!")
            self.assertEqual(lua.eval("_G._baseQsuCalls"), 1, "ApplyLastZWorldMaster double-wrapped SetGraphicQuality!")
            self.assertEqual(lua.eval("_G._MasterViewPointCount"), 2)
            self.assertIsNotNone(lua.eval("_G._PersistentWorldPointCacheByServer[702][100501]"))
            self.assertIsNotNone(lua.eval("_G._PersistentDesertCacheByServer[702][100501]"))

            # Out-of-view culling (forceRemove=false, isOutOfView=true) MUST be blocked
            lua.execute("DataCenter.WorldPointManager:RemovePointInfo(100501, false, true)")
            self.assertEqual(lua.eval("_G._baseRemoveCalls"), 0)
            self.assertIsNotNone(lua.eval("_G._PersistentWorldPointCacheByServer[702][100501]"))
            self.assertIsNotNone(lua.eval("_G._PersistentDesertCacheByServer[702][100501]"))

            # Real server removal (forceRemove=true, isOutOfView=false) MUST purge ptCache & desertCache + unindex + mark dirty
            dirty_before = lua.eval("_G._WorldCacheDirtyCount[702] or 0")
            lua.execute("DataCenter.WorldPointManager:RemovePointInfo(100501, true, false)")
            self.assertEqual(lua.eval("_G._baseRemoveCalls"), 1)
            self.assertIsNone(lua.eval("_G._PersistentWorldPointCacheByServer[702][100501]"))
            self.assertIsNone(lua.eval("_G._PersistentDesertCacheByServer[702][100501]"))
            self.assertEqual(lua.eval("_G._MasterViewPointCount"), 1)
            self.assertGreater(lua.eval("_G._WorldCacheDirtyCount[702] or 0"), dirty_before)

            # String key removal also purges numeric key in ptCache/desertCache
            lua.execute("DataCenter.WorldPointManager:RemovePointInfo('100502', true, false)")
            self.assertIsNone(lua.eval("_G._PersistentWorldPointCacheByServer[702][100502]"))
            self.assertIsNone(lua.eval("_G._PersistentWorldPointCacheByServer[702]['100502']"))


class TestR3MegamindPreloadContracts(unittest.TestCase):
    """R3 Read-Only Pre-Loading Specification & Live Manifest Verification Against megamind/."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw_dir = PROJECT_ROOT / "megamind" / "raw"
        cls.dc_managers = json.loads((cls.raw_dir / "datacenter managers.json").read_text(encoding="utf-8"))
        cls.callgraph_data = json.loads((cls.raw_dir / "datacenter callgraph and protocols.json").read_text(encoding="utf-8"))
        cls.enums_data = json.loads((cls.raw_dir / "enums complete.json").read_text(encoding="utf-8"))
        cls.xml_manifest = json.loads((cls.raw_dir / "xml tables manifest.json").read_text(encoding="utf-8"))
        cls.csharp_data = json.loads((cls.raw_dir / "csharp and http endpoints.json").read_text(encoding="utf-8"))
        cls.master_lua = _extract_master_lua_code()

    def test_megamind_offline_corpus_integrity_and_r3_specs(self) -> None:
        """Offline megamind/ corpus must validate TableName, XML manifest, exclusions, and read-only TemplateManagers."""
        table_names = self.enums_data.get("enums", {}).get("TableName", {})
        self.assertGreaterEqual(len(table_names), 250, "Expected >= 250 TableName entries in enums complete.json")
        xml_tables = self.xml_manifest.get("xml_tables", {})
        self.assertGreaterEqual(len(xml_tables), 350, "Expected >= 350 XML tables in xml tables manifest.json")

        callgraphs = self.callgraph_data.get("callgraphs", {})
        dc_dict = self.dc_managers.get("datacenter", {})

        # Verify HotUpdatePrefetchManager is known and NOT a read-only TemplateManager
        self.assertIn("HotUpdatePrefetchManager", dc_dict)
        self.assertIn("DataCenter.HotUpdatePrefetchManager", callgraphs)

        # Verify GuideManager has InGuide method
        self.assertIn("GuideManager", dc_dict)
        guide_methods = {m.get("name") for m in dc_dict["GuideManager"].get("methods", [])}
        self.assertIn("InGuide", guide_methods)

        # Verify core TemplateManagers in R3 spec have msgs == [] and events == [] across ALL methods
        core_tms = [
            "ScienceTemplateManager",
            "HeroTemplateManager",
            "HeroLevelUpTemplateManager",
            "HeroEquipTemplateManager",
            "CarChipTemplateManager",
            "ItemTemplateManager",
            "VIPTemplateManager",
            "DetectEventTemplateManager",
            "DecorationTemplateManager",
            "NationTemplateManager",
            "GovernmentTemplateManager",
            "MailGroupTemplateManager",
            "MailShowTemplateManager",
        ]
        for tm in core_tms:
            self.assertIn(tm, dc_dict, f"{tm} missing from datacenter managers.json")
            fq = f"DataCenter.{tm}"
            self.assertIn(fq, callgraphs, f"{fq} missing from datacenter callgraph and protocols.json")
            for mname, minfo in callgraphs[fq].get("methods", {}).items():
                self.assertEqual(minfo.get("msgs", []), [], f"{fq}.{mname} has network msgs: {minfo.get('msgs')}")
                self.assertEqual(minfo.get("events", []), [], f"{fq}.{mname} has events: {minfo.get('events')}")

    def test_master_lua_preload_manifest_strictly_read_only_against_megamind(self) -> None:
        """Every preloaded TableName.* and DataCenter.*TemplateManager in MASTER_LUA_CODE must pass megamind/ proofs."""
        warm_fn, r3_block = _extract_r3_warmup_code(self.master_lua)
        self.assertTrue(warm_fn, "function _G.WarmReadOnlyEngineCaches(...) not found in MASTER_LUA_CODE")
        self.assertTrue(r3_block, "Could not extract R3 warmup block from MASTER_LUA_CODE")

        # Strip Lua comments before scanning tables, managers, exclusions, and GuideManager
        warm_clean = _strip_lua_comments(warm_fn)
        r3_clean = _strip_lua_comments(r3_block)

        # 1. Verify TableName.* (and local aliases + {"EnumKey", "xml_name"} pairs) against enums complete.json & xml tables manifest.json
        table_enum = self.enums_data.get("enums", {}).get("TableName", {})
        xml_tables = self.xml_manifest.get("xml_tables", {})
        all_xml_table_keys: set[str] = set()
        for tmeta in xml_tables.values():
            for tk in tmeta.get("table_keys", []):
                all_xml_table_keys.add(tk)

        tn_aliases = ["TableName"] + re.findall(
            r"\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*TableName\b",
            warm_clean,
        )
        preloaded_enum_keys: set[str] = set()
        for alias in tn_aliases:
            preloaded_enum_keys.update(re.findall(rf"\b{re.escape(alias)}\.([A-Za-z0-9_]+)\b", warm_clean))

        # Also extract string-keyed coreEnumKeys & mainEnumKeys arrays (nil-hole-safe iteration)
        core_enum_keys = _extract_lua_string_array(warm_clean, "coreEnumKeys")
        main_enum_keys = _extract_lua_string_array(warm_clean, "mainEnumKeys")
        self.assertGreaterEqual(len(core_enum_keys), 15, f"Expected >= 15 entries in coreEnumKeys, got {len(core_enum_keys)}")
        self.assertGreaterEqual(len(main_enum_keys), 8, f"Expected >= 8 entries in mainEnumKeys, got {len(main_enum_keys)}")
        preloaded_enum_keys.update(core_enum_keys)
        preloaded_enum_keys.update(main_enum_keys)

        # Also extract {"EnumKey", "xml_table_name"} fallback pairs used in WarmReadOnlyEngineCaches
        preloaded_pairs = re.findall(
            r'\{\s*["\']([A-Za-z0-9_]+)["\']\s*,\s*["\']([a-z0-9_]+)["\']\s*\}',
            warm_clean,
        )
        # Also extract direct string table names passed to _warmXmlTable(lc, "table_name", ...)
        direct_xml_strs = re.findall(
            r'_warmXmlTable\s*\([^,]+,\s*["\']([a-z0-9_]+)["\']',
            warm_clean,
        )

        total_tables = len(preloaded_enum_keys) + len(preloaded_pairs) + len(direct_xml_strs)
        self.assertGreaterEqual(total_tables, 30, "Expected >= 30 XML table entries across coreEnumKeys/mainEnumKeys/pairs")

        heavy_excluded = {"Barrel_Monster", "LW_Monster_Born", "PVELevelOld", "PVETriggerOld", "QuestXml"}
        heavy_excluded_xml = {table_enum[k] for k in heavy_excluded if k in table_enum} | {
            "barrel_monster",
            "lw_monster_born",
            "pve_level_old",
            "pve_trigger_old",
            "quest_xml",
        }

        for tbl_key in sorted(preloaded_enum_keys):
            self.assertNotIn(tbl_key, heavy_excluded, f"Heavy excluded table TableName.{tbl_key} must NOT be preloaded")
            self.assertTrue(
                (tbl_key in table_enum) or (f"TableName.{tbl_key}" in all_xml_table_keys),
                f"TableName.{tbl_key} does not exist in megamind/raw/enums complete.json or xml tables manifest.json",
            )
            if tbl_key in table_enum:
                mapped_name = table_enum[tbl_key]
                self.assertTrue(
                    (mapped_name in xml_tables) or (f"TableName.{tbl_key}" in all_xml_table_keys),
                    f"TableName.{tbl_key} ({mapped_name}) not found in megamind/raw/xml tables manifest.json",
                )

        for enum_key, fallback_xml in preloaded_pairs:
            self.assertNotIn(enum_key, heavy_excluded, f"Heavy excluded table {enum_key} must NOT be preloaded")
            self.assertNotIn(fallback_xml, heavy_excluded_xml, f"Heavy excluded XML {fallback_xml} must NOT be preloaded")
            self.assertTrue(
                (enum_key in table_enum) or (f"TableName.{enum_key}" in all_xml_table_keys),
                f"Table pair key TableName.{enum_key} not found in enums complete.json or xml tables manifest.json",
            )
            self.assertIn(
                fallback_xml,
                xml_tables,
                f"Fallback XML table '{fallback_xml}' for {enum_key} not found in xml tables manifest.json",
            )

        for xml_name in direct_xml_strs:
            self.assertNotIn(xml_name, heavy_excluded_xml, f"Heavy excluded XML {xml_name} must NOT be preloaded")
            self.assertIn(xml_name, xml_tables, f"Direct XML table '{xml_name}' not found in xml tables manifest.json")

        # 2. Verify DataCenter.*TemplateManager entries against datacenter managers.json & callgraph
        dc_dict = self.dc_managers.get("datacenter", {})
        callgraphs = self.callgraph_data.get("callgraphs", {})

        preloaded_tms = set(re.findall(r"\b([A-Za-z0-9_]+TemplateManager)\b", warm_clean))
        self.assertGreaterEqual(len(preloaded_tms), 1, "Expected >= 1 DataCenter.*TemplateManager in WarmReadOnlyEngineCaches")

        for tm_name in sorted(preloaded_tms):
            self.assertIn(tm_name, dc_dict, f"{tm_name} not found in megamind/raw/datacenter managers.json")
            fq = f"DataCenter.{tm_name}"
            self.assertIn(fq, callgraphs, f"{fq} not found in megamind/raw/datacenter callgraph and protocols.json")
            for mname, minfo in callgraphs[fq].get("methods", {}).items():
                self.assertEqual(
                    minfo.get("msgs", []),
                    [],
                    f"Preloaded {fq}.{mname} is NOT read-only (msgs={minfo.get('msgs')})",
                )
                self.assertEqual(
                    minfo.get("events", []),
                    [],
                    f"Preloaded {fq}.{mname} broadcasts events (events={minfo.get('events')})",
                )

        # 3. Strict exclusion list checks inside comment-stripped R3 warmup code
        for forbidden in (
            "HotUpdatePrefetchManager",
            "GuideNeedLoadManager",
            "OpenWindow",
            "DoSendViewRequest",
            "Global.Cache.Init",
            "StringLookupTable.Init",
            "rm.CacheTime",
            "rm.MaxInstancePerFrame",
            "SetMaxUnusedPoolCount",
        ):
            self.assertNotIn(forbidden, r3_clean, f"Forbidden non-read-only or excluded call '{forbidden}' found in R3 preload code!")

        self.assertNotRegex(
            r3_clean,
            re.compile(r"\.(?:CacheTime|MaxInstancePerFrame)\s*="),
            "R3 preload code must not mutate ResourceManager.CacheTime or MaxInstancePerFrame",
        )
        self.assertNotRegex(
            r3_clean,
            re.compile(r"PreloadType\.Cache\s+or\s+0\b|\bpType\s*=\s*0\b"),
            "R3 preload code must not fall back to raw integer 0 for ResourceManager.PreloadType",
        )
        self.assertRegex(
            r3_clean,
            re.compile(r"if\s+pType\s*~=\s*nil\s+then.*?PreloadAsset", re.S),
            "R3 PreloadAsset call must be gated on resolved CS.ResourceManager.PreloadType.Cache ~= nil",
        )

        # 4. Cross-check Tier 3 C# classes/methods against megamind/raw/csharp and http endpoints.json
        ac_types = self.csharp_data.get("csharp_reflected_types", {}).get("Assembly-CSharp", {})
        for cls_name, expected_methods in (
            ("ShaderManager", ("IsInitDone", "IsWarmUpDone", "GetCurWarmUpQueueCount", "StartWarmupByFrame")),
            ("ResourceManager", ("IsAssetDownloaded", "HasAsset", "PreloadAsset")),
            ("ParticleTemplateManager", ("IsWarmed", "Warm")),
        ):
            self.assertIn(cls_name, ac_types, f"{cls_name} missing from csharp and http endpoints.json")
            method_names = {m.split("(", 1)[0] for m in ac_types[cls_name].get("methods", [])}
            for mname in expected_methods:
                self.assertIn(mname, method_names, f"{cls_name}.{mname} not verified in megamind Assembly-CSharp")
        preload_enum_fields = {f.split(":", 1)[0] for f in ac_types.get("ResourceManager+PreloadType", {}).get("fields", [])}
        self.assertIn("Cache", preload_enum_fields, "ResourceManager+PreloadType.Cache missing from megamind")

        # GuideManager may ONLY appear in the negative InGuide() readiness check, never as an init/warm target
        guide_lines = [ln.strip() for ln in r3_clean.splitlines() if "GuideManager" in ln]
        for gln in guide_lines:
            self.assertIn("InGuide", gln, f"GuideManager referenced outside InGuide() readiness check: {gln}")

    def test_master_lua_preload_readiness_gate_and_warmup_state(self) -> None:
        """_G.WarmReadOnlyEngineCaches must enforce all 7+ readiness conditions and expose _G._WarmupState."""
        warm_fn, r3_block = _extract_r3_warmup_code(self.master_lua)
        self.assertTrue(warm_fn, "function _G.WarmReadOnlyEngineCaches(...) not found")
        r3_clean = _strip_lua_comments(r3_block)

        for cond in (
            "m_isStartGame",
            "isInitDB",
            "Player",
            "uid",
            "CurrSceneID",
            "__cProjectStateReady",
            "InGuide",
            "_needReleaseCache",
        ):
            self.assertIn(cond, r3_clean, f"Readiness gate missing required check: {cond}")

        self.assertIn("_WarmupState", r3_clean)
        for field in (
            "started",
            "done",
            "role",
            "uid",
            "tablesWarmed",
            "managersWarmed",
            "shadersStarted",
            "assetsWarmed",
            "skippedReason",
            "errors",
        ):
            self.assertIn(field, r3_clean, f"_G._WarmupState missing telemetry field: {field}")

    def test_lua_warm_read_only_engine_caches_behavior(self) -> None:
        """lupa: WarmReadOnlyEngineCaches enforces readiness gates, idempotency, nil-safe enum keys, & isolated pcalls."""
        with tempfile.TemporaryDirectory() as tmp:
            lua, _ = _boot_master_lua_in_lupa(self.master_lua, cache_dir=tmp, active_sid=702)

            # 1. Verify every readiness gate rejects with the exact skippedReason
            readiness_cases = [
                ("LuaEntry.m_isStartGame = false", "LuaEntry.m_isStartGame = true", "not_started_or_db_uninit"),
                ("LuaEntry.isInitDB = false", "LuaEntry.isInitDB = true", "not_started_or_db_uninit"),
                ("local _p = LuaEntry.Player; _G._savedP = _p; LuaEntry.Player = nil", "LuaEntry.Player = _G._savedP", "no_player"),
                ("LuaEntry.Player.uid = '0'", "LuaEntry.Player.uid = 'uid_ready_1'", "invalid_uid"),
                ("SceneManager.CurrSceneID = 99", "SceneManager.CurrSceneID = 1", "unsupported_scene"),
                ("UIManager.GetInstance = function() return { __cProjectStateReady = false } end",
                 "UIManager.GetInstance = function() return { __cProjectStateReady = true } end", "ui_not_ready"),
                ("DataCenter.GuideManager = { InGuide = function() return true end }",
                 "DataCenter.GuideManager = { InGuide = function() return false end }", "in_guide"),
                ("DataCenter.MemoryPolicyManager = { _needReleaseCache = true }",
                 "DataCenter.MemoryPolicyManager = { _needReleaseCache = false }", "low_memory_policy"),
            ]
            for setup_bad, restore_ok, expected_reason in readiness_cases:
                lua.execute(setup_bad)
                res = lua.eval("_G.WarmReadOnlyEngineCaches({ role = 'main' })")
                self.assertEqual(res, f"SKIPPED:{expected_reason}", f"Readiness gate failed for {expected_reason}")
                self.assertEqual(lua.eval("_G._WarmupState.skippedReason"), expected_reason)
                lua.execute(restore_ok)

            # 2. Verify nil-safe enum key iteration + isolated pcalls + PreloadType.Cache guard + idempotency
            lua.execute(
                r"""
                _G._testTimerQueue = {}
                _G._warmedTables = {}
                _G._preloadedAssets = {}
                _G._tmInits = 0

                -- Deliberately insert nil holes in the middle of coreEnumKeys and mainEnumKeys
                TableName = {
                    GoodsTab = "goods",
                    Resource = nil,
                    DailyQuest = "daily_quest",
                    CollectResource = "collect_resource",
                    Monster = "monster",
                    WorldCity = nil,
                    SidebarType = "sidebar_type",
                }
                LocalController = {
                    instance = function()
                        return {
                            HasTableInMem = function() return false end,
                            isTableLoaded = function() return false end,
                            getTable = function(_, name)
                                _G._warmedTables[name] = (_G._warmedTables[name] or 0) + 1
                                return { ok = true }
                            end,
                        }
                    end,
                }
                DataCenter.HeroTemplateManager = {
                    templateIds = {},
                    InitAllTemplate = function(self)
                        self.templateIds = { 101 }
                        _G._tmInits = _G._tmInits + 1
                    end,
                }
                -- Throw inside ShaderManager.IsInitDone to verify isolated pcall doesn't break later tasks
                CS.GameEntry.Shader = {
                    IsInitDone = function() error("simulated_shader_fault") end,
                }
                -- Throw on 1 icon out of 5 while 4 succeed
                CS.ResourceManager.PreloadType = { Cache = "CACHE_ENUM_TOKEN" }
                CS.GameEntry.Resource = {
                    IsAssetDownloaded = function(_, path)
                        if tostring(path):find("mine_lod_wood") then
                            error("simulated_icon_fault")
                        end
                        return true
                    end,
                    HasAsset = function() return true end,
                    PreloadAsset = function(_, path, pType)
                        _G._preloadedAssets[#_G._preloadedAssets + 1] = { path = path, pType = pType }
                    end,
                }
                """
            )

            # First call schedules warmup; immediate second call returns IN_PROGRESS (idempotent)
            sched_res = lua.eval("_G.WarmReadOnlyEngineCaches({ role = 'main' })")
            self.assertTrue(str(sched_res).startswith("WARMUP_SCHEDULED:"), f"Unexpected schedule result: {sched_res}")
            self.assertEqual(lua.eval("_G.WarmReadOnlyEngineCaches({ role = 'main' })"), "IN_PROGRESS")

            # Drain all scheduled TimerManager slices
            lua.execute(
                r"""
                local guard = 0
                while #_G._testTimerQueue > 0 and guard < 200 do
                    guard = guard + 1
                    local item = table.remove(_G._testTimerQueue, 1)
                    item.fn()
                end
                """
            )

            self.assertTrue(lua.eval("_G._WarmupState.done"), "Warmup must complete despite isolated faults")
            # Tables AFTER nil holes in TableName must have been warmed
            self.assertEqual(lua.eval("_G._warmedTables['goods']"), 1)
            self.assertEqual(lua.eval("_G._warmedTables['daily_quest']"), 1)
            self.assertEqual(lua.eval("_G._warmedTables['collect_resource']"), 1)
            self.assertEqual(lua.eval("_G._warmedTables['monster']"), 1)
            self.assertEqual(lua.eval("_G._warmedTables['sidebar_type']"), 1)
            # TemplateManager warmed cleanly despite ShaderManager fault
            self.assertEqual(lua.eval("_G._tmInits"), 1)
            self.assertEqual(lua.eval("_G._WarmupState.managersWarmed"), 1)
            # 4 of 5 icons warmed, 1 isolated icon fault + 1 shader fault recorded in errors
            self.assertEqual(lua.eval("_G._WarmupState.assetsWarmed"), 4)
            self.assertEqual(lua.eval("#_G._preloadedAssets"), 4)
            self.assertEqual(lua.eval("_G._preloadedAssets[1].pType"), "CACHE_ENUM_TOKEN")
            err_joined = lua.eval("table.concat(_G._WarmupState.errors, ' | ')")
            self.assertIn("simulated_shader_fault", err_joined)
            self.assertIn("simulated_icon_fault", err_joined)

            # Subsequent call returns ALREADY_DONE without re-running tasks
            self.assertEqual(lua.eval("_G.WarmReadOnlyEngineCaches({ role = 'main' })"), "ALREADY_DONE")
            self.assertEqual(lua.eval("_G._tmInits"), 1)

            # Verify PreloadAsset is NOT called when CS.ResourceManager.PreloadType.Cache is nil (no raw 0 fallback)
            lua.execute(
                r"""
                _G._testTimerQueue = {}
                _G._preloadedAssets = {}
                CS.ResourceManager.PreloadType = {}
                _G.WarmReadOnlyEngineCaches({ role = 'main', force = true })
                local guard = 0
                while #_G._testTimerQueue > 0 and guard < 200 do
                    guard = guard + 1
                    local item = table.remove(_G._testTimerQueue, 1)
                    item.fn()
                end
                """
            )
            self.assertEqual(
                lua.eval("#_G._preloadedAssets"),
                0,
                "PreloadAsset must NOT be called when CS.ResourceManager.PreloadType.Cache is nil",
            )


class TestR4GuardrailContracts(unittest.TestCase):
    """R4 Guardrail Verification: zero prohibited terms in modified/added project files."""

    def test_r4_no_prohibited_terms_in_modified_and_added_files(self) -> None:
        """Scan all modified/added .py, .html, .bat, .spec files for R4 prohibited terms."""
        # Dynamically construct patterns so literal terms never appear in this file
        term1_re = re.compile(r"\bcom" + r"mander\b", re.I)
        term2_re = re.compile(r"cour" + r"age\s+bad" + r"ges?", re.I)

        candidates: set[Path] = {
            PROJECT_ROOT / "launcher" / "web" / "index.html",
            PROJECT_ROOT / "launcher" / "heinzhubweb.py",
            PROJECT_ROOT / "tools" / "multi client bot.py",
            PROJECT_ROOT / "tools" / "bot actions.py",
            PROJECT_ROOT / "tools" / "client discovery.py",
            PROJECT_ROOT / "tools" / "flush game memory.py",
            PROJECT_ROOT / "daemon" / "lastz auto engine daemon.py",
            PROJECT_ROOT / "daemon" / "apply widescreen smooth map.py",
            PROJECT_ROOT / "tests" / "testPerformanceOptimisations.py",
            PROJECT_ROOT / "tests" / "testR2R3PreloadContracts.py",
            PROJECT_ROOT / "tests" / "run all tests.py",
        }
        try:
            proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    if len(line) >= 4:
                        rel = line[3:].strip().strip('"')
                        if " -> " in rel:
                            rel = rel.split(" -> ", 1)[1].strip('"')
                        p = PROJECT_ROOT / rel
                        if p.is_file() and p.suffix.lower() in {".py", ".html", ".bat", ".spec"}:
                            candidates.add(p)
        except Exception:
            pass

        violations: list[str] = []
        for path in sorted(candidates):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for idx, line in enumerate(text.splitlines(), start=1):
                if term1_re.search(line) or term2_re.search(line):
                    violations.append(f"{path.relative_to(PROJECT_ROOT)}:{idx}")

        self.assertEqual(violations, [], f"R4 prohibited term matches found at: {violations}")


if __name__ == "__main__":
    unittest.main()
