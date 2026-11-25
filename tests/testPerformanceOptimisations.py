"""Performance Optimisation, Delta-State, Caching & Benchmark Tests (Milestone M4).

Covers:
1. R1 UI & Hub contracts (`launcher/web/index.html`, `launcher/heinzhubweb.py`):
   - `node --check` on extracted `<script>` blocks + 0 duplicate HTML IDs.
   - Delta `get_state` wiring (`since_log_id`, `known_cfg_ver`, `include_catalog`),
     empty-delta non-clearing `syncLogs`, visibility-aware 2s/12s polling + dedup,
     sig-gated & tab-scoped `renderState`, rAF-coalesced batched `drawMapRadar`,
     and view-gated + rAF-coalesced `mousemove` hover hit-testing.
   - Hub `_load_roster_power_map` stat-cache, `query_map_rip_targets` deferred copy /
     clustering skip / distance-squared sorting, name-first `restart_daemon`,
     and `_load_tool_module` singleton caching.
2. R1/R2 Bot & Discovery contracts (`tools/multi client bot.py`, `tools/bot actions.py`,
   `tools/client discovery.py`):
   - `_load_module` singleton cache with 0 duplicate `atexit` registrations.
   - `get_task_status` 60s TTL cache.
   - `get_status(skip_discovery=..., skip_running=..., include_schedule=...)` signature & skip behavior.
   - `load_config` & `_load_stage_state` stat cache + mutation isolation + save invalidation.
   - `_load_bot_mine_melee_module` singleton cache.
   - `_G.__hzBridge` / `_G.__hzCommonVer` bootstrap + `__HZ_NEED_BOOTSTRAP__` recovery
     while preserving `local function _dismiss_modal_dialogs()`.
   - `snapshot_client` O(1) presence check & `rapidjson.encode` preference.
3. Real Benchmark Suite (`TestPerformanceBenchmarks` + `run_benchmarks()`).
"""

from __future__ import annotations

import ast
import atexit
import ctypes
from ctypes import wintypes
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock

from lupa import LuaRuntime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_mod(unique_name: str, rel_path: str):
    path = PROJECT_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(unique_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_js_function(html: str, fn_header_regex: str) -> str:
    """Extract a balanced-brace JS function block starting at fn_header_regex."""
    m = re.search(fn_header_regex, html)
    if not m:
        return ""
    start = m.start()
    brace_start = html.find("{", m.end() - 1)
    if brace_start == -1:
        return ""
    depth = 0
    in_str: str | None = None
    escaped = False
    for idx in range(brace_start, len(html)):
        ch = html[idx]
        if in_str is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ('"', "'", "`"):
            in_str = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return html[start : idx + 1]
    return html[start:]


class TestR1UiAndHubOptimisations(unittest.TestCase):
    """R1 UI (`launcher/web/index.html`) and Hub (`launcher/heinzhubweb.py`) contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.html_path = PROJECT_ROOT / "launcher" / "web" / "index.html"
        cls.html = cls.html_path.read_text(encoding="utf-8")
        cls.hub_path = PROJECT_ROOT / "launcher" / "heinzhubweb.py"
        cls.hub_src = cls.hub_path.read_text(encoding="utf-8")
        cls.hub = _load_mod("test_perf_hub_mod", "launcher/heinzhubweb.py")

    def test_index_html_js_syntax_node_check(self) -> None:
        """All <script> blocks in launcher/web/index.html must pass `node --check`."""
        node_bin = shutil.which("node")
        if not node_bin:
            self.skipTest("node executable not found on PATH")

        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", self.html, flags=re.S | re.I)
        self.assertGreater(len(scripts), 0, "Expected at least one <script> block in index.html")
        with tempfile.TemporaryDirectory() as tmp:
            for idx, body in enumerate(scripts):
                if not body.strip():
                    continue
                js_path = Path(tmp) / f"script_{idx}.js"
                js_path.write_text(body, encoding="utf-8")
                proc = subprocess.run(
                    [node_bin, "--check", str(js_path)],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(
                    proc.returncode,
                    0,
                    f"node --check failed on <script> #{idx}:\n{proc.stderr}\n{proc.stdout}",
                )

    def test_index_html_zero_duplicate_ids(self) -> None:
        """launcher/web/index.html must have zero duplicate id attributes."""
        all_ids = re.findall(r'\bid\s*=\s*"([^"]+)"', self.html)
        counts: dict[str, int] = {}
        for item in all_ids:
            counts[item] = counts.get(item, 0) + 1
        dups = {k: v for k, v in counts.items() if v > 1}
        self.assertEqual(dups, {}, f"Duplicate HTML IDs detected: {dups}")

    def test_index_html_delta_get_state_wiring(self) -> None:
        """refreshState & renderState must wire since_log_id, known_cfg_ver, include_catalog."""
        refresh_fn = _extract_js_function(self.html, r"async\s+function\s+refreshState\s*\(")
        self.assertTrue(refresh_fn, "refreshState() not found")
        self.assertIn("since_log_id", refresh_fn)
        self.assertIn("known_cfg_ver", refresh_fn)
        self.assertIn("include_catalog", refresh_fn)
        self.assertIn("lastRenderedLogId", refresh_fn)
        self.assertIn("_lastConfigVer", refresh_fn)
        self.assertIn("_hasTaskCatalog", refresh_fn)

        render_fn = _extract_js_function(self.html, r"function\s+renderState\s*\(")
        self.assertTrue(render_fn, "renderState() not found")
        self.assertIn("_lastConfigVer", render_fn)
        self.assertIn("config_ver", render_fn)
        self.assertIn("_hasTaskCatalog", render_fn)

    def test_index_html_sync_logs_empty_delta_non_clearing(self) -> None:
        """syncLogs must check logs_delta / logs_reset so empty delta does NOT clear console."""
        sync_fn = _extract_js_function(self.html, r"function\s+syncLogs\s*\(")
        self.assertTrue(sync_fn, "syncLogs() not found")
        self.assertRegex(
            sync_fn,
            re.compile(
                r"if\s*\(\s*logsDelta\s*&&\s*!logsReset\s*&&\s*(?:logs\.length\s*===?\s*0|!logs\.length)\s*\)\s*(?:\{\s*)?return\b"
            ),
            "syncLogs() must fast-return without clearing _allLogEntries when logsDelta && !logsReset && logs.length === 0",
        )
        self.assertRegex(
            sync_fn,
            re.compile(r"logsReset\s*\|\|\s*\(\s*!logsDelta\b"),
            "syncLogs() resetNeeded must guard empty-list clear with !logsDelta",
        )
        render_fn = _extract_js_function(self.html, r"function\s+renderState\s*\(")
        self.assertIn("logs_delta", render_fn)
        self.assertIn("logs_reset", render_fn)

    def test_index_html_visibility_aware_smart_polling(self) -> None:
        """Must use 2s/12s visibility-aware polling + visibilitychange + _stateInFlight dedup."""
        self.assertIn("_STATE_POLL_VISIBLE_MS = 2000", self.html)
        self.assertIn("_STATE_POLL_HIDDEN_MS = 12000", self.html)
        self.assertIn("visibilitychange", self.html)
        self.assertNotRegex(
            self.html,
            re.compile(r"setInterval\s*\(\s*refreshState\s*,\s*2000\s*\)"),
            "Unconditional setInterval(refreshState, 2000) must be replaced by visibility-aware polling",
        )
        refresh_fn = _extract_js_function(self.html, r"async\s+function\s+refreshState\s*\(")
        self.assertIn("_stateInFlight", refresh_fn)
        self.assertIn("_statePendingRefresh", refresh_fn)

    def test_index_html_dirty_check_and_tab_scoped_render_state(self) -> None:
        """renderState must gate header/setup/sidebar by sigs, scope tabs, use _domRef, and resync config."""
        render_fn = _extract_js_function(self.html, r"function\s+renderState\s*\(")
        self.assertTrue(render_fn)
        for sym in (
            "_lastHeaderSig",
            "_lastSetupSig",
            "_lastSidebarSig",
            "_overviewDirty",
            "_botsCardsDirty",
            "_domRef(",
            "currentView",
        ):
            self.assertIn(sym, render_fn, f"renderState() missing {sym}")
        # Must update config inputs when config_ver changes (not gated solely on firstLoad)
        self.assertRegex(
            render_fn,
            re.compile(r"(cfgChanged|config_ver|_lastConfigVer)"),
            "renderState() must re-sync config UI when config_ver changes",
        )

    def test_index_html_raf_coalesced_batched_draw_map_radar(self) -> None:
        """drawMapRadar must coalesce via requestAnimationFrame and batch fills by color/type."""
        # Check rAF coalescing around drawMapRadar / scheduleDrawMapRadar
        wrapper_fn = _extract_js_function(self.html, r"function\s+drawMapRadar\s*\(")
        self.assertTrue(wrapper_fn, "drawMapRadar() wrapper not found")
        sched_fn = _extract_js_function(self.html, r"function\s+scheduleDrawMapRadar\s*\(")
        if sched_fn:
            self.assertIn("requestAnimationFrame", sched_fn, "scheduleDrawMapRadar() must coalesce with requestAnimationFrame")
            self.assertRegex(
                sched_fn,
                re.compile(r"(?:_drawMapRadarNow|drawMapRadar)"),
                "scheduleDrawMapRadar() must invoke _drawMapRadarNow / drawMapRadar inside requestAnimationFrame",
            )
            self.assertIn("scheduleDrawMapRadar", wrapper_fn, "drawMapRadar() must delegate to scheduleDrawMapRadar()")
        else:
            self.assertIn("requestAnimationFrame", wrapper_fn, "drawMapRadar() must coalesce with requestAnimationFrame")

        # Extract _drawMapRadarNow first; fall back to drawMapRadar only if _drawMapRadarNow does not exist
        draw_fn = _extract_js_function(self.html, r"function\s+_drawMapRadarNow\s*\(")
        if not draw_fn:
            draw_fn = wrapper_fn
        self.assertTrue(draw_fn, "_drawMapRadarNow / drawMapRadar body not found")

        # Must NOT do ctx.beginPath(); ctx.arc(...); ctx.fill() per point inside `for (const pt of pts)`
        per_pt_loop = _extract_js_function(draw_fn, r"for\s*\(\s*const\s+pt\s+of\s+pts\s*\)\s*\{")
        self.assertTrue(
            per_pt_loop,
            "Expected `for (const pt of pts)` grouping loop inside _drawMapRadarNow/drawMapRadar",
        )
        self.assertNotIn(
            "ctx.fill()",
            per_pt_loop,
            "drawMapRadar still calls ctx.fill() per point inside `for (const pt of pts)` instead of batching!",
        )
        self.assertNotIn(
            "ctx.beginPath()",
            per_pt_loop,
            "drawMapRadar still calls ctx.beginPath() per point inside `for (const pt of pts)` instead of batching!",
        )
        after_loop = draw_fn[draw_fn.index(per_pt_loop) + len(per_pt_loop) :]
        self.assertIn("ctx.beginPath()", after_loop, "Expected batched ctx.beginPath() after per-point grouping")
        self.assertIn("ctx.arc(", after_loop, "Expected batched ctx.arc() after per-point grouping")
        self.assertIn("ctx.fill()", after_loop, "Expected batched ctx.fill() after per-point grouping")

    def test_index_html_gated_mousemove_and_raf_hover(self) -> None:
        """canvas mousemove must gate hover on currentView/drag + rAF; window mousemove must gate on _mapDragState.active."""
        canvas_mm = _extract_js_function(
            self.html,
            r'canvas\.addEventListener\(\s*["\']mousemove["\']\s*,\s*\(ev\)\s*=>\s*\{',
        )
        self.assertTrue(canvas_mm, "canvas.addEventListener('mousemove', ...) listener not found")
        idx_view = canvas_mm.find('currentView !== "map"')
        if idx_view == -1:
            idx_view = canvas_mm.find("currentView !== 'map'")
        idx_drag = canvas_mm.find("_mapDragState.active")
        idx_rect = canvas_mm.find("getBoundingClientRect")
        self.assertNotEqual(idx_view, -1, "canvas mousemove must guard on currentView !== 'map'")
        self.assertNotEqual(idx_drag, -1, "canvas mousemove must guard on _mapDragState.active")
        self.assertNotEqual(idx_rect, -1, "canvas mousemove must compute getBoundingClientRect inside rAF hover")
        self.assertLess(idx_view, idx_rect, "currentView guard must precede getBoundingClientRect()")
        self.assertLess(idx_drag, idx_rect, "_mapDragState.active guard must precede getBoundingClientRect()")
        self.assertIn(
            "requestAnimationFrame",
            canvas_mm,
            "canvas mousemove hover hit-testing must coalesce with requestAnimationFrame",
        )

        win_mm = _extract_js_function(
            self.html,
            r'window\.addEventListener\(\s*["\']mousemove["\']\s*,\s*\(ev\)\s*=>\s*\{',
        )
        self.assertTrue(win_mm, "window.addEventListener('mousemove', ...) drag listener not found")
        self.assertRegex(
            win_mm,
            re.compile(r"if\s*\(\s*!_mapDragState\.active\s*\)\s*return\s*;"),
            "window mousemove must immediately return when !_mapDragState.active",
        )

    def test_hub_load_roster_power_map_stat_cache(self) -> None:
        """_load_roster_power_map must cache by (path, mtime, size) and warm index hits must not re-read unchanged JSONs."""
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp) / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            roster_dir = Path(tmp) / "json cache" / "bracket data" / "state_702"
            roster_dir.mkdir(parents=True, exist_ok=True)
            roster_file = roster_dir / "top10_alliance_rosters.json"
            roster_file.write_text(
                json.dumps([{"rank": 1, "members": [{"uid": "u1", "power": 55_000_000, "curServerId": 702}]}]),
                encoding="utf-8",
            )
            idx_val = 500 * 1000 + 500 + 1
            (cache_dir / "world_map_cache_s702.json").write_text(
                json.dumps({
                    str(idx_val): {
                        "pointType": 6,
                        "serverId": 702,
                        "mainIndex": idx_val,
                        "pointIndex": idx_val,
                        "aoiVersion": 10,
                        "buildInfo": {"buildId": 400000, "ownerUid": "u1", "name": "Alpha", "alAbbr": "AAA", "level": 30},
                    }
                }),
                encoding="utf-8",
            )
            with self.hub._MAP_INDEX_LOCK:
                self.hub._WORLD_MAP_INDEX_CACHE.clear()

            sig1, map1 = self.hub._load_roster_power_map(tmp)
            self.assertEqual(map1[(702, "u1")]["power"], 55_000_000)

            orig_loads = self.hub.json.loads
            parse_calls = 0

            def _counting_loads(*args, **kwargs):
                nonlocal parse_calls
                parse_calls += 1
                return orig_loads(*args, **kwargs)

            with mock.patch.object(self.hub.json, "loads", side_effect=_counting_loads):
                sig2, map2 = self.hub._load_roster_power_map(tmp)
                self.assertEqual(sig1, sig2)
                self.assertEqual(map2[(702, "u1")]["power"], 55_000_000)
                self.assertEqual(parse_calls, 0, "_load_roster_power_map re-parsed unchanged roster JSON instead of using stat cache")

            # Warm _get_world_map_index must also avoid re-reading roster JSON
            idx1 = self.hub._get_world_map_index(tmp)
            self.assertEqual(idx1["hqs_by_uid"]["u1"]["power"], 55_000_000)
            with mock.patch.object(self.hub.json, "loads", side_effect=_counting_loads):
                idx2 = self.hub._get_world_map_index(tmp)
                self.assertIs(idx1, idx2)
                self.assertEqual(parse_calls, 0)

            # Mutating file updates mtime/size and invalidates cache
            time.sleep(0.02)
            roster_file.write_text(
                json.dumps([{"rank": 1, "members": [{"uid": "u1", "power": 77_000_000, "curServerId": 702}]}]),
                encoding="utf-8",
            )
            _, map3 = self.hub._load_roster_power_map(tmp)
            self.assertEqual(map3[(702, "u1")]["power"], 77_000_000)

    def test_hub_query_map_rip_targets_deferred_copy_and_cluster_skip(self) -> None:
        """query_map_rip_targets must skip _compute_alliance_clusters on hqs/unshielded/rss and defer dict copies."""
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp) / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            entries: dict[str, Any] = {}
            for i in range(25):
                idx = (100 + i) * 1000 + (200 + i) + 1
                entries[str(idx)] = {
                    "pointType": 6,
                    "serverId": 702,
                    "mainIndex": idx,
                    "pointIndex": idx,
                    "aoiVersion": 10,
                    "buildInfo": {
                        "buildId": 400000,
                        "ownerUid": f"u_{i}",
                        "name": f"Player_{i}",
                        "alAbbr": "TAG",
                        "level": 25 + (i % 5),
                        "protectEndTime": 0,
                    },
                }
            for i in range(10):
                idx = (300 + i) * 1000 + (300 + i) + 1
                entries[f"r_{i}"] = {
                    "pointType": 7,
                    "serverId": 702,
                    "mainIndex": idx,
                    "pointIndex": idx,
                    "aoiVersion": 10,
                    "resourceInfo": {"resourceId": 408, "gatherUuid": 0, "ownerUid": ""},
                }
            (cache_dir / "world_map_cache_s702.json").write_text(json.dumps(entries), encoding="utf-8")

            orig_data_dir = self.hub.DATA_DIR
            orig_heinz_dir = self.hub.HEINZ_DATA_DIR
            orig_env = os.environ.get("HEINZ_DATA_DIR")
            try:
                self.hub.DATA_DIR = tmp
                self.hub.HEINZ_DATA_DIR = tmp
                os.environ["HEINZ_DATA_DIR"] = tmp
                with self.hub._MAP_INDEX_LOCK:
                    self.hub._WORLD_MAP_INDEX_CACHE.clear()

                backend = self.hub.HubBackend.__new__(self.hub.HubBackend)
                backend._lock = threading.RLock()
                backend.env = {}

                cluster_calls = 0
                orig_cluster_fn = self.hub._compute_alliance_clusters

                def _spy_clusters(*args, **kwargs):
                    nonlocal cluster_calls
                    cluster_calls += 1
                    return orig_cluster_fn(*args, **kwargs)

                with mock.patch.object(self.hub, "_compute_alliance_clusters", side_effect=_spy_clusters):
                    for m in ("hqs", "unshielded", "rss"):
                        res = backend.query_map_rip_targets({"mode": m, "min_hq": 1, "rss_min_level": 1, "limit": 5, "sort_by": "distance"})
                        self.assertTrue(res["ok"])
                        self.assertLessEqual(len(res["targets"]), 5)
                        for row in res["targets"]:
                            self.assertNotIn("_search_hay", row)
                            self.assertIn("distance", row)
                    self.assertEqual(cluster_calls, 0, "_compute_alliance_clusters should be skipped for hqs/unshielded/rss modes")

                    # Mode 'clusters' MUST still compute clusters
                    res_cl = backend.query_map_rip_targets({"mode": "clusters", "min_members": 2, "cluster_radius": 60})
                    self.assertTrue(res_cl["ok"])
                    self.assertGreater(cluster_calls, 0)
            finally:
                self.hub.DATA_DIR = orig_data_dir
                self.hub.HEINZ_DATA_DIR = orig_heinz_dir
                if orig_env is None:
                    os.environ.pop("HEINZ_DATA_DIR", None)
                else:
                    os.environ["HEINZ_DATA_DIR"] = orig_env

        # Static contract: distance-squared sorting before dict copy
        q_src = inspect.getsource(self.hub.HubBackend.query_map_rip_targets)
        self.assertNotIn(
            "row = dict(hq)",
            q_src.split("matched_hqs")[1].split("matched_rss")[0],
            "query_map_rip_targets should defer dict(hq) copying until after sorting/slicing [:limit]",
        )

    def test_hub_restart_daemon_name_first_process_iter(self) -> None:
        """restart_daemon action must filter psutil.process_iter(['pid', 'name']) before inspecting cmdline."""
        m = re.search(r'elif\s+action_id\s*==\s*"restart_daemon"\s*:(.*?)(?=\n\s*elif\s+action_id\s*==)', self.hub_src, flags=re.S)
        self.assertIsNotNone(m, "restart_daemon block not found in heinzhubweb.py")
        block = m.group(1)
        self.assertIn('process_iter(["pid", "name"])', block.replace("'", '"'))
        self.assertNotIn('process_iter(["pid", "cmdline"])', block.replace("'", '"'))

    def test_hub_load_tool_module_cached(self) -> None:
        """_load_tool_module must return the cached module object on repeat calls."""
        m1 = self.hub._load_tool_module("client_discovery", os.path.join("tools", "client discovery.py"))
        m2 = self.hub._load_tool_module("client_discovery", os.path.join("tools", "client discovery.py"))
        self.assertIsNotNone(m1)
        self.assertIs(m1, m2, "_load_tool_module should cache loaded tool modules")

    def test_hub_get_state_delta_logs_config_ver_and_catalog(self) -> None:
        """HubBackend.get_state must support since_log_id, known_cfg_ver, and include_catalog contracts."""
        with (
            mock.patch.object(self.hub.HubBackend, "_load_cached_state"),
            mock.patch.object(self.hub.HubBackend, "_load_always_on_daemon_config"),
            mock.patch.object(self.hub.HubBackend, "_start_always_on_daemon"),
            mock.patch.object(self.hub.HubBackend, "log"),
        ):
            backend = self.hub.HubBackend()

        backend.logs = [
            {"id": 1, "time": "00:00:01", "msg": "boot", "kind": "info"},
            {"id": 2, "time": "00:00:02", "msg": "ready", "kind": "ok"},
            {"id": 3, "time": "00:00:03", "msg": "tick", "kind": "info"},
        ]
        backend._log_seq = 3

        # 1. Initial full fetch
        s_full = backend.get_state()
        self.assertFalse(s_full["logs_delta"])
        self.assertFalse(s_full["logs_reset"])
        self.assertEqual(s_full["log_head_id"], 3)
        self.assertEqual([e["id"] for e in s_full["logs"]], [1, 2, 3])
        self.assertIn("config_ver", s_full)
        self.assertIn("config", s_full)
        self.assertIn("task_catalog", s_full)

        cfg_ver = s_full["config_ver"]

        # 2. Unchanged delta fetch omits config & task_catalog and returns empty logs with logs_reset=False
        s_idle = backend.get_state(since_log_id=3, known_cfg_ver=cfg_ver, include_catalog=False)
        self.assertTrue(s_idle["logs_delta"])
        self.assertFalse(s_idle["logs_reset"])
        self.assertEqual(s_idle["log_head_id"], 3)
        self.assertEqual(s_idle["logs"], [])
        self.assertNotIn("config", s_idle)
        self.assertNotIn("task_catalog", s_idle)

        # 3. Incremental new log fetch returns only new logs > since_log_id
        backend.logs.append({"id": 4, "time": "00:00:04", "msg": "new", "kind": "info"})
        backend._log_seq = 4
        s_inc = backend.get_state(since_log_id=3, known_cfg_ver=cfg_ver, include_catalog=False)
        self.assertTrue(s_inc["logs_delta"])
        self.assertFalse(s_inc["logs_reset"])
        self.assertEqual(s_inc["log_head_id"], 4)
        self.assertEqual([e["id"] for e in s_inc["logs"]], [4])

        # 4. Empty buffer after clear_logs() signals logs_reset=True
        backend.logs.clear()
        s_cleared = backend.get_state(since_log_id=4, known_cfg_ver=cfg_ver, include_catalog=False)
        self.assertTrue(s_cleared["logs_delta"])
        self.assertTrue(s_cleared["logs_reset"])
        self.assertEqual(s_cleared["logs"], [])

        # 5. Sequence rewind signals logs_reset=True and mismatched known_cfg_ver re-includes config
        backend.logs.append({"id": 1, "time": "00:00:05", "msg": "restarted", "kind": "info"})
        backend._log_seq = 1
        s_rewind = backend.get_state(since_log_id=4, known_cfg_ver=cfg_ver - 1, include_catalog=True)
        self.assertTrue(s_rewind["logs_delta"])
        self.assertTrue(s_rewind["logs_reset"])
        self.assertEqual([e["id"] for e in s_rewind["logs"]], [1])
        self.assertIn("config", s_rewind)
        self.assertIn("task_catalog", s_rewind)

    def test_hub_lua_json_ser_lupa_roundtrip(self) -> None:
        """lupa: _LUA_JSON_SER handles _jarr({}), _jobj({}), NaN/Inf -> null, and control char escaping."""
        # 1. Pure-Lua fallback path (no package.loaded.rapidjson)
        lua_fb = LuaRuntime(unpack_returned_tuples=True)
        lua_fb.execute(
            self.hub._LUA_JSON_SER
            + r"""
            _G._test_ser = ser
            _G._test_jarr = _jarr
            _G._test_jobj = _jobj
            """
        )
        self.assertEqual(lua_fb.eval("_G._test_ser(_G._test_jarr({}))"), "[]")
        self.assertEqual(lua_fb.eval("_G._test_ser(_G._test_jobj({}))"), "{}")

        raw_fb = lua_fb.eval(
            r"""
            _G._test_ser(_G._test_jobj({
                emptyArr = _G._test_jarr({}),
                emptyObj = _G._test_jobj({}),
                nanVal = 0 / 0,
                posInf = math.huge,
                negInf = -math.huge,
                ctrl = "line1\nline2\r\t\b\f\"\\\0\1\31end",
                arrWithNan = _G._test_jarr({1, 0 / 0, math.huge, -math.huge}),
            }))
            """
        )
        parsed_fb = json.loads(raw_fb)
        self.assertEqual(parsed_fb["emptyArr"], [])
        self.assertEqual(parsed_fb["emptyObj"], {})
        self.assertIsNone(parsed_fb["nanVal"])
        self.assertIsNone(parsed_fb["posInf"])
        self.assertIsNone(parsed_fb["negInf"])
        self.assertEqual(parsed_fb["ctrl"], 'line1\nline2\r\t\b\f"\\\x00\x01\x1fend')
        self.assertEqual(parsed_fb["arrWithNan"], [1, None, None, None])

        # 2. Simulated C rapidjson path (where plain {} defaults to "{}" unless tagged via rapidjson.array)
        lua_rj = LuaRuntime(unpack_returned_tuples=True)
        lua_rj.execute(
            r"""
            local _arrMt = { __jsontype = "array" }
            local _objMt = { __jsontype = "object" }
            local function _mockEncode(v)
                local t = type(v)
                if t == "table" then
                    local mt = getmetatable(v)
                    if next(v) == nil then
                        return (mt and mt.__jsontype == "array") and "[]" or "{}"
                    end
                end
                error("force_fallback")
            end
            package.loaded.rapidjson = {
                array = function(t) return setmetatable(t or {}, _arrMt) end,
                object = function(t) return setmetatable(t or {}, _objMt) end,
                encode = _mockEncode,
            }
            """
            + self.hub._LUA_JSON_SER
            + r"""
            _G._test_ser = ser
            _G._test_jarr = _jarr
            _G._test_jobj = _jobj
            """
        )
        self.assertEqual(lua_rj.eval("_G._test_ser(_G._test_jarr({}))"), "[]")
        self.assertEqual(lua_rj.eval("_G._test_ser(_G._test_jobj({}))"), "{}")

    def test_hub_clear_logs_epoch_resets_even_with_immediate_new_log(self) -> None:
        """clear_logs() must bump _log_epoch so logs_reset is True even if a new log arrives before the next get_state."""
        with (
            mock.patch.object(self.hub.HubBackend, "_load_cached_state"),
            mock.patch.object(self.hub.HubBackend, "_load_always_on_daemon_config"),
            mock.patch.object(self.hub.HubBackend, "_start_always_on_daemon"),
            mock.patch.object(self.hub.HubBackend, "log"),
        ):
            backend = self.hub.HubBackend()

        backend.logs = [
            {"id": 1, "time": "00:00:01", "msg": "old1", "kind": "info"},
            {"id": 2, "time": "00:00:02", "msg": "old2", "kind": "info"},
        ]
        backend._log_seq = 2

        s0 = backend.get_state()
        old_epoch = s0["log_epoch"]
        old_head = s0["log_head_id"]

        clr = backend.clear_logs()
        self.assertTrue(clr["ok"])
        self.assertEqual(clr["log_epoch"], old_epoch + 1)

        # Immediately append a new log before the UI polls get_state
        backend.logs.append({"id": 3, "time": "00:00:03", "msg": "post-clear", "kind": "ok"})
        backend._log_seq = 3

        s1 = backend.get_state(since_log_id=old_head, since_log_epoch=old_epoch)
        self.assertTrue(s1["logs_delta"])
        self.assertTrue(s1["logs_reset"], "logs_reset must be True when since_log_epoch is stale after clear_logs()")
        self.assertEqual(s1["log_epoch"], old_epoch + 1)
        self.assertEqual([e["id"] for e in s1["logs"]], [3])

        # Even without since_log_epoch, _logs_cleared_seq watermark must trigger logs_reset=True
        s1_no_epoch = backend.get_state(since_log_id=old_head)
        self.assertTrue(s1_no_epoch["logs_reset"])
        self.assertEqual([e["id"] for e in s1_no_epoch["logs"]], [3])

        # Once client catches up to new epoch + log_head_id, idle poll returns logs_reset=False & []
        s2 = backend.get_state(since_log_id=s1["log_head_id"], since_log_epoch=s1["log_epoch"])
        self.assertFalse(s2["logs_reset"])
        self.assertEqual(s2["logs"], [])

    def test_hub_quick_shield_and_quick_recall_refresh_clients_and_lupa_json(self) -> None:
        """quick_shield and quick_recall must call _discover_running_clients and return valid lupa-serialized JSON."""
        self.assertNotIn(
            "self.discover_running_clients(",
            self.hub_src,
            "heinzhubweb.py must never call nonexistent self.discover_running_clients()",
        )

        with (
            mock.patch.object(self.hub.HubBackend, "_load_cached_state"),
            mock.patch.object(self.hub.HubBackend, "_load_always_on_daemon_config"),
            mock.patch.object(self.hub.HubBackend, "_start_always_on_daemon"),
            mock.patch.object(self.hub.HubBackend, "log"),
        ):
            backend = self.hub.HubBackend()

        backend.running_clients = [{"pid": 4242, "label": "Main", "role": "main"}]
        refreshed_list = [{"pid": 4242, "label": "Main", "role": "main", "shielded": True}]

        def _fake_eval_lua(pid: int, code: str, timeout: float = 8.0):
            lua = LuaRuntime(unpack_returned_tuples=True)
            lua.execute(
                r"""
                _G._usedTool = nil
                _G._recalledUuids = {}
                LuaEntry = { Player = { uid = "u_main" } }
                Localization = { GetString = function(_, k) return k end }
                DataCenter = {
                    ItemData = {
                        ItemInfos = {
                            ["u_item_1"] = { itemId = 9001, count = 2, template = { name = "Peace Shield 8h" } },
                        },
                        UseTool = function(_, itemId, cnt) _G._usedTool = { itemId, cnt } end,
                    },
                    ItemTemplateManager = {},
                    WorldMarchDataManager = {
                        allMarches = {
                            m1 = { uid = "u_main", uuid = "march_1" },
                            m2 = { uid = "u_main", uuid = "march_2" },
                            m3 = { uid = "other_player", uuid = "march_3" },
                        },
                    },
                }
                package.loaded["Util.MarchUtil_SLG"] = {
                    OnBackHome = function(uuid) _G._recalledUuids[#_G._recalledUuids + 1] = uuid end,
                }
                """
            )
            out = lua.execute(code)
            return True, str(out)

        mock_cd = SimpleNamespace(
            _xlua_loaded=mock.MagicMock(return_value=True),
            frida_eval_lua=mock.MagicMock(side_effect=_fake_eval_lua),
        )
        with (
            mock.patch.object(self.hub, "client_discovery", mock_cd),
            mock.patch.object(backend, "_discover_running_clients", return_value=refreshed_list) as disc_spy,
            mock.patch.object(backend, "_update_dropdown_values"),
            mock.patch.object(backend, "_refresh_fleet_state"),
            mock.patch.object(backend, "log"),
        ):
            res_shield = backend.quick_shield(pid=4242)
            self.assertTrue(res_shield["ok"])
            self.assertEqual(res_shield["itemId"], 9001)
            disc_spy.assert_called_with(query_lua=True, force_pids=[4242])
            self.assertEqual(backend.running_clients, refreshed_list)

            disc_spy.reset_mock()
            res_recall = backend.quick_recall(pid=4242)
            self.assertTrue(res_recall["ok"])
            self.assertEqual(res_recall["recalled"], 2)
            disc_spy.assert_called_with(query_lua=True, force_pids=[4242])
            self.assertEqual(backend.running_clients, refreshed_list)

    def test_hub_per_account_troops_tech_isolation_and_empty_live_inventory(self) -> None:
        """Per-account troops/tech caches must never leak across accounts, and empty live inventory must be accepted cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            jcache = Path(tmp) / "json cache"
            jcache.mkdir(parents=True, exist_ok=True)

            # Seed Main + legacy global caches with non-empty data
            main_troops = {
                "ok": True,
                "account_name": "Main",
                "totalTroops": 500000,
                "totalPower": 9000000,
                "armies": [{"id": "1", "name": "T10", "count": 500000}],
                "wounded": [],
                "typeCounts": {"infantry": 500000, "rider": 0, "vehicle": 0, "other": 0},
                "tierCounts": {"T10": 500000},
            }
            (jcache / "latest_troops_overview.json").write_text(json.dumps(main_troops), encoding="utf-8")
            (jcache / "main_troops_overview.json").write_text(json.dumps(main_troops), encoding="utf-8")

            # Stale non-empty inventory cache for Farm_Beta
            stale_inv = [{"itemId": 1001, "uuid": "old", "count": 5, "name": "Stale Speedup", "type": 1, "quality": 2}]
            (jcache / "farm_beta_inventory.json").write_text(json.dumps(stale_inv), encoding="utf-8")

            # Minimal deterministic tech badge matrix.json + legacy global maxed tech_tree_progress.json
            matrix_path = Path(tmp) / "tech badge matrix.json"
            matrix_path.write_text(
                json.dumps({
                    "trees": [{
                        "tab_id": 1,
                        "tree_name": "Test Tree",
                        "order": 1,
                        "total_badges": 100,
                        "tiers": [{
                            "tier": 1,
                            "nodes": [{
                                "id": "tech_101",
                                "name": "Node 1",
                                "max_level": 2,
                                "col": 1,
                                "badge_costs": [40, 60],
                            }],
                        }],
                    }]
                }),
                encoding="utf-8",
            )
            (jcache / "tech_tree_progress.json").write_text(json.dumps({"tech_101": 2}), encoding="utf-8")
            (jcache / "main_tech_progress.json").write_text(json.dumps({"tech_101": 2}), encoding="utf-8")

            with (
                mock.patch.object(self.hub.HubBackend, "_load_cached_state"),
                mock.patch.object(self.hub.HubBackend, "_load_always_on_daemon_config"),
                mock.patch.object(self.hub.HubBackend, "_start_always_on_daemon"),
                mock.patch.object(self.hub.HubBackend, "log"),
            ):
                backend = self.hub.HubBackend()

            backend.running_clients = [
                {"pid": 101, "label": "Main", "role": "main"},
                {"pid": 202, "label": "Farm_Beta", "role": "farm"},
            ]

            xlua_state = {101: False, 202: True}
            eval_calls = 0

            def _eval_empty_lua(pid: int, code: str, timeout: float = 8.0):
                nonlocal eval_calls
                eval_calls += 1
                lua = LuaRuntime(unpack_returned_tuples=True)
                lua.execute(
                    r"""
                    LuaEntry = { Player = { name = "Farm_Beta" } }
                    DataCenter = {
                        ItemData = { ItemInfos = {} },
                        ItemTemplateManager = {},
                        ScienceDataManager = { allScience = {} },
                        ArmyManager = { allArmy = {} },
                        HospitalManager = { allHospital = {} },
                        ArmyFormationDataManager = { ArmyFormationList = {} },
                    }
                    """
                )
                return True, str(lua.execute(code))

            mock_cd = SimpleNamespace(
                _xlua_loaded=mock.MagicMock(side_effect=lambda p: xlua_state.get(int(p), False)),
                frida_eval_lua=mock.MagicMock(side_effect=_eval_empty_lua),
                find_running_processes=mock.MagicMock(return_value=list(backend.running_clients)),
            )

            orig_heinz_dir = self.hub.HEINZ_DATA_DIR
            orig_data_dir = self.hub.DATA_DIR
            try:
                self.hub.HEINZ_DATA_DIR = tmp
                self.hub.DATA_DIR = tmp
                with self.hub._JSON_MEM_LOCK:
                    self.hub._JSON_MEM_CACHE.clear()

                with (
                    mock.patch.object(self.hub, "client_discovery", mock_cd),
                    mock.patch.object(backend, "_discover_running_clients", return_value=list(backend.running_clients)),
                    mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                    mock.patch.object(backend, "log"),
                ):
                    # 1. Empty live inventory is accepted cleanly, overwrites stale disk cache, updates _live_sync_ts
                    inv_live = backend.get_account_inventory(pid=202, force_live=True)
                    self.assertTrue(inv_live["ok"])
                    self.assertTrue(inv_live["is_live"])
                    self.assertTrue(inv_live["is_linked"])
                    self.assertEqual(inv_live["items"], [])
                    self.assertIn("inv:farm_beta", backend._live_sync_ts)
                    self.assertEqual(json.loads((jcache / "farm_beta_inventory.json").read_text(encoding="utf-8")), [])

                    # Cached empty inventory is respected within 60s TTL without re-querying Lua
                    calls_after_first = eval_calls
                    inv_cached = backend.get_account_inventory(pid=202, force_live=False)
                    self.assertEqual(eval_calls, calls_after_first)
                    self.assertEqual(inv_cached["items"], [])

                    # 2. Offline Farm_Beta MUST NOT inherit Main's or legacy global troops/tech caches
                    xlua_state[202] = False
                    troops_farm_off = backend.get_troops_overview(pid=202)
                    self.assertTrue(troops_farm_off["ok"])
                    self.assertEqual(troops_farm_off["totalTroops"], 0)
                    self.assertEqual(troops_farm_off["armies"], [])
                    self.assertEqual(troops_farm_off["wounded"], [])

                    tech_farm_off = backend.get_tech_calculator_data(pid=202)
                    self.assertTrue(tech_farm_off["ok"])
                    self.assertEqual(tech_farm_off["overall"]["total_badges_invested"], 0)

                    # 3. Online 0-tech Farm_Beta returns 0 invested, updates cache, does NOT clobber Main's cache
                    xlua_state[202] = True
                    tech_farm_live = backend.get_tech_calculator_data(pid=202, force_live=True)
                    self.assertTrue(tech_farm_live["ok"])
                    self.assertTrue(tech_farm_live["is_live"])
                    self.assertEqual(tech_farm_live["overall"]["total_badges_invested"], 0)
                    self.assertIn("sci:farm_beta", backend._live_sync_ts)
                    self.assertEqual(json.loads((jcache / "farm_beta_tech_progress.json").read_text(encoding="utf-8")), {})
                    self.assertEqual(json.loads((jcache / "main_tech_progress.json").read_text(encoding="utf-8")), {"tech_101": 2})

                    # Main still sees its own cached tech & troops cleanly
                    tech_main = backend.get_tech_calculator_data(pid=101)
                    self.assertEqual(tech_main["overall"]["total_badges_invested"], 100)
                    troops_main = backend.get_troops_overview(pid=101)
                    self.assertEqual(troops_main["totalTroops"], 500000)
            finally:
                self.hub.HEINZ_DATA_DIR = orig_heinz_dir
                self.hub.DATA_DIR = orig_data_dir
                with self.hub._JSON_MEM_LOCK:
                    self.hub._JSON_MEM_CACHE.clear()

    def test_hub_build_config_snapshot_returns_last_good_on_transient_error(self) -> None:
        """_build_config_snapshot must return the last good snapshot on transient read errors instead of (0, {})."""
        mcb_mod = _load_mod("test_perf_mcb_snap_mod", "tools/multi client bot.py")
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "bot config.json"
            cfg = mcb_mod.default_config()
            cfg["cycle_interval_seconds"] = 245
            mcb_mod.save_config(cfg, config_path=cfg_path)

            with (
                mock.patch.object(self.hub.HubBackend, "_load_cached_state"),
                mock.patch.object(self.hub.HubBackend, "_load_always_on_daemon_config"),
                mock.patch.object(self.hub.HubBackend, "_start_always_on_daemon"),
                mock.patch.object(self.hub.HubBackend, "log"),
            ):
                backend = self.hub.HubBackend()

            fake_mcb = SimpleNamespace(
                CONFIG_PATH=str(cfg_path),
                load_config=lambda: mcb_mod.load_config(config_path=cfg_path),
            )
            with mock.patch.object(self.hub, "multi_client_bot", fake_mcb):
                ver1, snap1 = backend._build_config_snapshot()
                self.assertGreater(ver1, 0)
                self.assertEqual(snap1["cycle_interval_seconds"], 245)

                # Mutate caller's returned dict to prove deep-copy isolation of _last_good_config_snapshot
                snap1["cycle_interval_seconds"] = 9999

                # Force cache miss + transient read failure
                backend._config_snapshot_cache = None
                fake_mcb.load_config = mock.MagicMock(side_effect=PermissionError("locked during atomic replace"))
                ver2, snap2 = backend._build_config_snapshot()
                self.assertEqual(ver2, ver1, "_build_config_snapshot returned ver=0 instead of last good version")
                self.assertNotEqual(snap2, {}, "_build_config_snapshot wiped snapshot to {} on transient error")
                self.assertEqual(snap2["cycle_interval_seconds"], 245)


class TestR1BotAndDiscoveryOptimisations(unittest.TestCase):
    """R1/R2 Bot & Discovery contracts (`multi client bot.py`, `bot actions.py`, `client discovery.py`)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mcb = _load_mod("test_perf_mcb_mod", "tools/multi client bot.py")
        cls.bot_actions = _load_mod("test_perf_ba_mod", "tools/bot actions.py")
        cls.cd = _load_mod("test_perf_cd_mod", "tools/client discovery.py")

    def test_bot_load_module_singleton_cache_and_zero_atexit_leak(self) -> None:
        """_load_module must cache in _MODULE_CACHE and register zero duplicate atexit handlers."""
        self.assertTrue(hasattr(self.mcb, "_MODULE_CACHE"), "multi client bot.py must define _MODULE_CACHE")
        cd_path = PROJECT_ROOT / "tools" / "client discovery.py"
        m1 = self.mcb._load_module("client_discovery", cd_path)
        nc1 = atexit._ncallbacks()
        m2 = self.mcb._load_module("client_discovery", cd_path)
        nc2 = atexit._ncallbacks()
        self.assertIs(m1, m2, "_load_module did not return cached singleton module")
        self.assertEqual(nc2, nc1, "_load_module leaked duplicate atexit callback on repeat load")

    def test_bot_get_task_status_60s_ttl_cache(self) -> None:
        """get_task_status() must cache schtasks results for 60s and refresh after TTL expiry."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "bot config.json"
            cfg = self.mcb.default_config()
            cfg["schedule"] = {"task_name": "LastZ_Test_Task", "legacy_task_names": []}
            self.mcb.save_config(cfg, config_path=cfg_path)

            subproc_calls = 0

            def _fake_run(*args, **kwargs):
                nonlocal subproc_calls
                subproc_calls += 1
                return SimpleNamespace(returncode=0, stdout="Status: Ready\nNext Run Time: N/A\n", stderr="")

            # Clear any existing task status cache before and after so mocked timestamps never leak
            def _clear_task_cache() -> None:
                for attr in ("_TASK_STATUS_CACHE", "_task_status_cache"):
                    cache_obj = getattr(self.mcb, attr, None)
                    if isinstance(cache_obj, dict):
                        cache_obj.clear()

            _clear_task_cache()
            now_val = [1_000_000.0]
            try:
                with (
                    mock.patch.object(self.mcb, "CONFIG_PATH", cfg_path),
                    mock.patch.object(self.mcb.subprocess, "run", side_effect=_fake_run),
                    mock.patch.object(self.mcb.time, "time", side_effect=lambda: now_val[0]),
                    mock.patch.object(self.mcb.time, "monotonic", side_effect=lambda: now_val[0]),
                ):
                    r1 = self.mcb.get_task_status()
                    r2 = self.mcb.get_task_status()
                    self.assertEqual(subproc_calls, 1, "get_task_status() did not cache schtasks output within 60s TTL")
                    self.assertEqual(r1["primary"]["task_name"], "LastZ_Test_Task")
                    self.assertEqual(r1["primary"]["state"], r2["primary"]["state"])

                    # Advance past 60s TTL
                    now_val[0] += 65.0
                    r3 = self.mcb.get_task_status()
                    self.assertEqual(subproc_calls, 2, "get_task_status() did not refresh after 60s TTL expired")
                    self.assertEqual(r3["primary"]["task_name"], "LastZ_Test_Task")
            finally:
                _clear_task_cache()

    def test_bot_get_status_kwargs_and_skips(self) -> None:
        """get_status() must accept skip_discovery, skip_running, include_schedule and skip disabled probes."""
        sig = inspect.signature(self.mcb.get_status)
        for param in ("skip_discovery", "skip_running", "include_schedule"):
            self.assertIn(param, sig.parameters, f"get_status() missing required parameter: {param}")

        cd_mock = SimpleNamespace(
            load_saved_profiles=mock.MagicMock(return_value={"clients": []}),
            discover_clients=mock.MagicMock(return_value={"clients": []}),
            find_running_processes=mock.MagicMock(return_value=[]),
        )
        with (
            mock.patch.object(self.mcb, "_load_module", return_value=cd_mock),
            mock.patch.object(self.mcb, "get_task_status", return_value={"primary": {"state": "Ready"}}) as task_spy,
            mock.patch.object(self.mcb, "is_daemon_running", return_value=False),
        ):
            res = self.mcb.get_status(skip_discovery=True, skip_running=True, include_schedule=False)
            self.assertIsInstance(res, dict)
            cd_mock.discover_clients.assert_not_called()
            cd_mock.find_running_processes.assert_not_called()
            task_spy.assert_not_called()

    def test_bot_load_config_stat_cache_mutation_isolation_and_save_invalidation(self) -> None:
        """load_config() must cache by (path, mtime, size), isolate caller mutations, and invalidate on save_config()."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "bot config.json"
            cfg = self.mcb.default_config()
            cfg["cycle_interval_seconds"] = 240
            self.mcb.save_config(cfg, config_path=cfg_path)

            c1 = self.mcb.load_config(config_path=cfg_path)
            self.assertEqual(c1["cycle_interval_seconds"], 240)
            # Mutate returned dict aggressively
            c1["cycle_interval_seconds"] = 9999
            c1["profiles"]["poison"] = {"enabled": False}

            orig_json_load = self.mcb.json.load
            load_calls = 0

            def _spy_load(*args, **kwargs):
                nonlocal load_calls
                load_calls += 1
                return orig_json_load(*args, **kwargs)

            with mock.patch.object(self.mcb.json, "load", side_effect=_spy_load):
                c2 = self.mcb.load_config(config_path=cfg_path)
                self.assertEqual(load_calls, 0, "load_config() re-parsed unchanged config file instead of hitting stat cache")
            self.assertEqual(c2["cycle_interval_seconds"], 240, "Mutation of returned config poisoned cache!")
            self.assertNotIn("poison", c2["profiles"])

            # save_config() must invalidate/update cache immediately
            c2["cycle_interval_seconds"] = 300
            self.mcb.save_config(c2, config_path=cfg_path)
            c3 = self.mcb.load_config(config_path=cfg_path)
            self.assertEqual(c3["cycle_interval_seconds"], 300)

    def test_bot_load_stage_state_stat_cache_mutation_isolation_and_save_invalidation(self) -> None:
        """_load_stage_state() must cache by (path, mtime, size), isolate caller mutations, and invalidate on save."""
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "bot_stage_state.json"
            self.mcb._save_stage_state({"version": 1, "clients": {"c1": {"stage": 2}}}, path=state_path)

            s1 = self.mcb._load_stage_state(path=state_path)
            self.assertEqual(s1["clients"]["c1"]["stage"], 2)
            s1["clients"]["c1"]["stage"] = 999

            orig_json_loads = self.mcb.json.loads
            loads_calls = 0

            def _spy_loads(*args, **kwargs):
                nonlocal loads_calls
                loads_calls += 1
                return orig_json_loads(*args, **kwargs)

            with mock.patch.object(self.mcb.json, "loads", side_effect=_spy_loads):
                s2 = self.mcb._load_stage_state(path=state_path)
                self.assertEqual(loads_calls, 0, "_load_stage_state() re-parsed unchanged file instead of hitting stat cache")
            self.assertEqual(s2["clients"]["c1"]["stage"], 2, "Mutation of returned stage state poisoned cache!")

            self.mcb._save_stage_state({"version": 1, "clients": {"c1": {"stage": 4}}}, path=state_path)
            s3 = self.mcb._load_stage_state(path=state_path)
            self.assertEqual(s3["clients"]["c1"]["stage"], 4)

    def test_bot_actions_load_bot_mine_melee_singleton_cache(self) -> None:
        """_load_bot_mine_melee_module() must return the same singleton module across calls."""
        m1 = self.bot_actions._load_bot_mine_melee_module()
        m2 = self.bot_actions._load_bot_mine_melee_module()
        self.assertIsNotNone(m1)
        self.assertIs(m1, m2, "_load_bot_mine_melee_module() must cache its module")

    def test_bot_actions_persistent_hz_bridge_bootstrap_and_recovery(self) -> None:
        """_eval_json must bootstrap _G.__hzBridge once, send compact payloads after, and recover on __HZ_NEED_BOOTSTRAP__."""
        ba_src = (PROJECT_ROOT / "tools" / "bot actions.py").read_text(encoding="utf-8")
        # Preserve empirical_challenger contract
        self.assertIn("local function _dismiss_modal_dialogs()", ba_src)
        self.assertTrue(
            "_G.__hzBridge" in ba_src or "_G.__hzCommonVer" in ba_src,
            "bot actions.py must implement persistent _G.__hzBridge / _G.__hzCommonVer Lua helper caching",
        )
        self.assertIn("__HZ_NEED_BOOTSTRAP__", ba_src)

        sent_payloads: list[str] = []
        responses = [
            (True, '{"ok": true, "step": 1}'),
            (True, '{"ok": true, "step": 2}'),
            (True, "__HZ_NEED_BOOTSTRAP__"),
            (True, '{"ok": true, "step": 3, "recovered": true}'),
        ]

        class _MockCD:
            def frida_eval_lua(self, pid: int, code: str, timeout: float = 8.0):
                sent_payloads.append(code)
                return responses.pop(0)

        mock_cd = _MockCD()
        test_pid = 9998877
        r1 = self.bot_actions._eval_json(mock_cd, test_pid, "return _enc({ok=true, step=1})")
        r2 = self.bot_actions._eval_json(mock_cd, test_pid, "return _enc({ok=true, step=2})")
        r3 = self.bot_actions._eval_json(mock_cd, test_pid, "return _enc({ok=true, step=3})")

        self.assertTrue(r1.get("ok"))
        self.assertTrue(r2.get("ok"))
        self.assertTrue(r3.get("ok"))
        self.assertTrue(r3.get("recovered"))
        self.assertEqual(len(sent_payloads), 4)
        self.assertLess(
            len(sent_payloads[1]),
            len(self.bot_actions.LUA_COMMON_HELPERS),
            "2nd _eval_json call still re-transmitted full LUA_COMMON_HELPERS instead of compact body",
        )
        self.assertGreater(
            len(sent_payloads[3]),
            len(sent_payloads[2]),
            "__HZ_NEED_BOOTSTRAP__ recovery did not re-send bootstrap payload",
        )

    def test_bot_actions_snapshot_client_o1_presence_and_rapidjson(self) -> None:
        """snapshot_client() must use O(1) presence check by default and LUA_JSON_HELPER must prefer rapidjson.encode."""
        sent: list[str] = []

        class _MockCD:
            def frida_eval_lua(self, pid: int, code: str, timeout: float = 8.0):
                sent.append(code)
                return True, json.dumps({"ok": True, "inWorld": True, "worldPointsCount": 1})

        res = self.bot_actions.snapshot_client(_MockCD(), 12345)
        self.assertTrue(res.get("ok"))
        lua_code = sent[0]
        self.assertNotIn(
            "for _ in pairs(DataCenter.WorldPointManager.allViewPoints)",
            lua_code,
            "snapshot_client() must not unconditionally O(N)-scan 73k allViewPoints entries",
        )
        self.assertIn("rapidjson", self.bot_actions.LUA_JSON_HELPER)
        self.assertIn("encode", self.bot_actions.LUA_JSON_HELPER)

    def test_client_discovery_name_first_and_rapidjson(self) -> None:
        """client discovery.py must use name-first process_iter, TTL discovery cache, and rapidjson.encode in LUA_QUICK_STATUS."""
        cd_src = (PROJECT_ROOT / "tools" / "client discovery.py").read_text(encoding="utf-8")
        self.assertIn('psutil.process_iter(["pid", "name"])', cd_src.replace("'", '"'))
        self.assertIn("_DISCOVER_CACHE_TTL_SEC", cd_src)
        self.assertIn("rapidjson", self.cd.LUA_QUICK_STATUS)
        self.assertIn("encode", self.cd.LUA_QUICK_STATUS)

    def test_bot_lua_json_helper_lupa_roundtrip(self) -> None:
        """lupa: bot actions & bot_mine_melee LUA_JSON_HELPER round-trip _jarr({}), _jdict({}), NaN/Inf -> null, and control chars."""
        bmm = self.bot_actions._load_bot_mine_melee_module()
        helpers = [("bot_actions", self.bot_actions.LUA_JSON_HELPER)]
        if bmm is not None and hasattr(bmm, "LUA_JSON_HELPER"):
            helpers.append(("bot_mine_melee", bmm.LUA_JSON_HELPER))

        for label, helper_lua in helpers:
            # 1. Pure-Lua fallback (_enc_lua)
            lua_fb = LuaRuntime(unpack_returned_tuples=True)
            lua_fb.execute(
                helper_lua
                + r"""
                _G._test_enc = _enc
                _G._test_jarr = _jarr
                _G._test_jdict = _jdict
                """
            )
            self.assertEqual(lua_fb.eval("_G._test_enc(_G._test_jarr({}))"), "[]", f"{label} _jarr({{}}) != '[]'")
            self.assertEqual(lua_fb.eval("_G._test_enc(_G._test_jdict({}))"), "{}", f"{label} _jdict({{}}) != '{{}}'")
            self.assertEqual(lua_fb.eval("_G._test_enc(0 / 0)"), "null", f"{label} NaN != 'null'")
            self.assertEqual(lua_fb.eval("_G._test_enc(math.huge)"), "null", f"{label} +Inf != 'null'")
            self.assertEqual(lua_fb.eval("_G._test_enc(-math.huge)"), "null", f"{label} -Inf != 'null'")

            raw_obj = lua_fb.eval(
                r"""
                _G._test_enc({
                    ok = true,
                    emptyArr = _G._test_jarr({}),
                    emptyDict = _G._test_jdict({}),
                    nanVal = 0 / 0,
                    posInf = math.huge,
                    negInf = -math.huge,
                    arrNan = _G._test_jarr({1, 0 / 0, math.huge, -math.huge}),
                    ctrl = "a\"b\\c\n\r\t\0\1\31\127z",
                })
                """
            )
            parsed = json.loads(raw_obj)
            self.assertTrue(parsed["ok"])
            self.assertEqual(parsed["emptyArr"], [])
            self.assertEqual(parsed["emptyDict"], {})
            self.assertIsNone(parsed["nanVal"])
            self.assertIsNone(parsed["posInf"])
            self.assertIsNone(parsed["negInf"])
            self.assertEqual(parsed["arrNan"], [1, None, None, None])
            self.assertEqual(parsed["ctrl"], 'a"b\\c\n\r\t\x00\x01\x1f\x7fz')

            # 2. Simulated C rapidjson module where encode({}) == "{}" + array()/object()/null supported
            lua_rj = LuaRuntime(unpack_returned_tuples=True)
            lua_rj.execute(
                r"""
                local _arrMt = { __jsontype = "array" }
                local _objMt = { __jsontype = "object" }
                local _nullTok = {}
                local function _encVal(v)
                    if v == _nullTok or v == nil then return "null" end
                    local t = type(v)
                    if t == "boolean" then return tostring(v) end
                    if t == "number" then return tostring(v) end
                    if t == "string" then
                        return '"' .. v:gsub('[%z\1-\31\\"\127]', function(c)
                            return string.format('\\u%04x', c:byte())
                        end) .. '"'
                    end
                    if t == "table" then
                        local mt = getmetatable(v)
                        local jt = mt and mt.__jsontype
                        if next(v) == nil then
                            return jt == "array" and "[]" or "{}"
                        end
                        local isArr, cnt = (jt ~= "object"), 0
                        for k, _ in pairs(v) do
                            cnt = cnt + 1
                            if type(k) ~= "number" or k < 1 or math.floor(k) ~= k then isArr = false end
                        end
                        local p = {}
                        if isArr then
                            for i = 1, cnt do p[i] = _encVal(v[i]) end
                            return "[" .. table.concat(p, ",") .. "]"
                        else
                            for k, val in pairs(v) do p[#p + 1] = _encVal(tostring(k)) .. ":" .. _encVal(val) end
                            return "{" .. table.concat(p, ",") .. "}"
                        end
                    end
                    return "null"
                end
                package.loaded.rapidjson = {
                    null = _nullTok,
                    array = function(t) return setmetatable(t or {}, _arrMt) end,
                    object = function(t) return setmetatable(t or {}, _objMt) end,
                    encode = _encVal,
                }
                """
                + helper_lua
                + r"""
                _G._test_enc = _enc
                _G._test_jarr = _jarr
                _G._test_jdict = _jdict
                """
            )
            self.assertEqual(lua_rj.eval("_G._test_enc(_G._test_jarr({}))"), "[]")
            self.assertEqual(lua_rj.eval("_G._test_enc(_G._test_jdict({}))"), "{}")
            parsed_rj = json.loads(
                lua_rj.eval(
                    r"""
                    _G._test_enc({
                        ok = true,
                        emptyArr = _G._test_jarr({}),
                        emptyDict = _G._test_jdict({}),
                        arrNan = _G._test_jarr({1, 0 / 0, math.huge, -math.huge}),
                        ctrl = "x\n\t\0\31\"\\y",
                    })
                    """
                )
            )
            self.assertEqual(parsed_rj["emptyArr"], [])
            self.assertEqual(parsed_rj["emptyDict"], {})
            self.assertEqual(parsed_rj["arrNan"], [1, None, None, None])
            self.assertEqual(parsed_rj["ctrl"], 'x\n\t\x00\x1f"\\y')

    def test_client_discovery_win32_64bit_handles_pid_guard_and_singleton(self) -> None:
        """_has_module_win32 must use 64-bit wintypes.HANDLE on a private WinDLL, reject pid <= 0, and share singleton."""
        if os.name == "nt":
            k32 = self.cd._KERNEL32
            self.assertIsNotNone(k32)
            self.assertIsNot(k32, ctypes.windll.kernel32, "_KERNEL32 must be a private WinDLL, not global ctypes.windll.kernel32")
            self.assertEqual(list(k32.CreateToolhelp32Snapshot.argtypes), [wintypes.DWORD, wintypes.DWORD])
            self.assertEqual(k32.CreateToolhelp32Snapshot.restype, wintypes.HANDLE)
            self.assertEqual(k32.Module32FirstW.argtypes[0], wintypes.HANDLE)
            self.assertEqual(k32.Module32FirstW.restype, wintypes.BOOL)
            self.assertEqual(k32.Module32NextW.argtypes[0], wintypes.HANDLE)
            self.assertEqual(k32.Module32NextW.restype, wintypes.BOOL)
            self.assertEqual(list(k32.CloseHandle.argtypes), [wintypes.HANDLE])
            self.assertEqual(k32.CloseHandle.restype, wintypes.BOOL)

            # Behavioral test with high 64-bit HANDLE values (>= 0x80000000 and >= 0x1_0000_0000) + pid <= 0 guard
            for high_handle in (0x80000004, 0x1_0000_0004):
                seen_handles: list[int] = []
                closed_handles: list[int] = []
                snap_attempts = [0]

                def _fake_snap(flags: int, pid: int, _hh: int = high_handle) -> int:
                    snap_attempts[0] += 1
                    if snap_attempts[0] == 1:
                        ctypes.set_last_error(24)  # ERROR_BAD_LENGTH retry path
                        return wintypes.HANDLE(-1).value
                    return _hh

                def _fake_first(handle: int, me_ptr: Any) -> int:
                    seen_handles.append(int(handle))
                    me_ptr._obj.szModule = "UnityPlayer.dll"
                    return 1

                def _fake_next(handle: int, me_ptr: Any) -> int:
                    seen_handles.append(int(handle))
                    me_ptr._obj.szModule = "xLua.dll"
                    return 1

                def _fake_close(handle: int) -> int:
                    closed_handles.append(int(handle))
                    return 1

                fake_k32 = SimpleNamespace(
                    CreateToolhelp32Snapshot=mock.MagicMock(side_effect=_fake_snap),
                    Module32FirstW=mock.MagicMock(side_effect=_fake_first),
                    Module32NextW=mock.MagicMock(side_effect=_fake_next),
                    CloseHandle=mock.MagicMock(side_effect=_fake_close),
                )
                with mock.patch.object(self.cd, "_KERNEL32", fake_k32):
                    # pid <= 0 rejected before touching kernel32
                    self.assertFalse(self.cd._has_module_win32(0, "xlua.dll"))
                    self.assertFalse(self.cd._has_module_win32(-42, "xlua.dll"))
                    fake_k32.CreateToolhelp32Snapshot.assert_not_called()

                    # Valid pid with 64-bit handle + ERROR_BAD_LENGTH retry
                    found = self.cd._has_module_win32(4242, "xlua.dll")
                    self.assertTrue(found)
                    self.assertEqual(snap_attempts[0], 2)
                    self.assertEqual(seen_handles, [high_handle, high_handle])
                    self.assertEqual(closed_handles, [high_handle])

        # Verify canonical heinz_client_discovery_singleton is shared across loaders
        hub_mod = _load_mod("test_perf_hub_singleton_check", "launcher/heinzhubweb.py")
        cd_from_mcb = self.mcb._load_module("client_discovery", PROJECT_ROOT / "tools" / "client discovery.py")
        cd_from_hub = hub_mod._load_tool_module("client_discovery", os.path.join("tools", "client discovery.py"))
        self.assertIn("heinz_client_discovery_singleton", sys.modules)
        self.assertIs(cd_from_mcb, sys.modules["heinz_client_discovery_singleton"])
        self.assertIs(cd_from_hub, sys.modules["heinz_client_discovery_singleton"])
        self.assertIs(cd_from_mcb._SHARED_STATE, self.cd._SHARED_STATE)

    def test_daemon_pid_lock_atomic_excl_and_parent_alive_pid_reuse(self) -> None:
        """Daemon _acquire_daemon_pid_lock must use atomic O_EXCL (returning None on contention) & _is_parent_alive defeats PID reuse."""
        daemon_path = PROJECT_ROOT / "daemon" / "lastz auto engine daemon.py"
        daemon_src = daemon_path.read_text(encoding="utf-8")
        daemon_mod = _load_mod("test_perf_daemon_mod", "daemon/lastz auto engine daemon.py")

        # Static contract: uses O_CREAT | O_EXCL and zero bare open() calls outside `with`
        self.assertIn("os.O_EXCL", daemon_src)
        tree = ast.parse(daemon_src)
        with_open_ids: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == "open":
                        with_open_ids.add(id(item.context_expr))
        bare_opens = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
            and id(node) not in with_open_ids
        ]
        self.assertEqual(bare_opens, [], f"Bare open() calls without `with` found at lines: {bare_opens}")

        with tempfile.TemporaryDirectory() as tmp:
            lock_file = Path(tmp) / "lastz_auto_engine.pid"

            # 1. Clean atomic acquisition writes current PID
            got = daemon_mod._acquire_daemon_pid_lock(str(lock_file))
            self.assertEqual(got, str(lock_file))
            self.assertEqual(lock_file.read_text(encoding="utf-8").strip(), str(os.getpid()))

            # 2. Contention against active daemon returns None (NEVER empty string "")
            lock_file.write_text("987654", encoding="utf-8")
            with mock.patch.object(daemon_mod, "_is_live_daemon_process", return_value=True):
                contended = daemon_mod._acquire_daemon_pid_lock(str(lock_file))
            self.assertIsNone(contended, "_acquire_daemon_pid_lock must return None on contention, never ''")

            # 3. OSError on os.open returns None (NEVER empty string "")
            with mock.patch.object(daemon_mod.os, "open", side_effect=PermissionError("access denied")), \
                 mock.patch.object(daemon_mod.time, "sleep"):
                errored = daemon_mod._acquire_daemon_pid_lock(str(lock_file))
            self.assertIsNone(errored, "_acquire_daemon_pid_lock must return None on OSError, never ''")

            # 4. Stale PID lockfile is cleaned and atomically re-acquired
            lock_file.write_text("987654", encoding="utf-8")
            with mock.patch.object(daemon_mod, "_is_live_daemon_process", return_value=False):
                recovered = daemon_mod._acquire_daemon_pid_lock(str(lock_file))
            self.assertEqual(recovered, str(lock_file))
            self.assertEqual(lock_file.read_text(encoding="utf-8").strip(), str(os.getpid()))

        # 5. _is_parent_alive detects Windows PID reuse via create_time mismatch
        self.assertTrue(daemon_mod._is_parent_alive(0, None))
        fake_proc_same = SimpleNamespace(
            is_running=lambda: True,
            status=lambda: "running",
            create_time=lambda: 1700000100.25,
        )
        fake_proc_reused = SimpleNamespace(
            is_running=lambda: True,
            status=lambda: "running",
            create_time=lambda: 1700000999.75,
        )
        with (
            mock.patch.object(daemon_mod.psutil, "pid_exists", return_value=True),
            mock.patch.object(daemon_mod.psutil, "Process", return_value=fake_proc_same),
        ):
            self.assertTrue(daemon_mod._is_parent_alive(54321, 1700000100.25))

        with (
            mock.patch.object(daemon_mod.psutil, "pid_exists", return_value=True),
            mock.patch.object(daemon_mod.psutil, "Process", return_value=fake_proc_reused),
        ):
            self.assertFalse(
                daemon_mod._is_parent_alive(54321, 1700000100.25),
                "_is_parent_alive must return False when PID was reused with a different create_time",
            )

        with mock.patch.object(daemon_mod.psutil, "pid_exists", return_value=False):
            self.assertFalse(daemon_mod._is_parent_alive(54321, 1700000100.25))

    def test_bot_actions_preparedness_probe_ok_and_dry_run_guard(self) -> None:
        """_probe_preparedness_phase must set ok=True and skip ActivityEventInfoGet when allow_network_refresh=False."""
        sig = inspect.signature(self.bot_actions._probe_preparedness_phase)
        self.assertIn("allow_network_refresh", sig.parameters)
        self.assertIs(sig.parameters["allow_network_refresh"].default, False)

        lua = LuaRuntime(unpack_returned_tuples=True)
        sent_messages: list[tuple[Any, Any]] = []

        def _record_send(msg_id: Any, arg: Any = None) -> None:
            sent_messages.append((msg_id, arg))

        lua.globals()["_py_record_send"] = _record_send
        lua.execute(
            r"""
            LuaEntry = { Player = { uid = "uid_prep_1", name = "Tester" } }
            UITimeManager = { GetInstance = function() return { GetServerTime = function() return 1700000000000 end } end }
            SceneManager = { IsInWorld = function() return false end }
            Localization = { GetString = function(_, k) return tostring(k) end }
            MsgDefines = { ActivityEventInfoGet = "ActivityEventInfoGet" }
            SFSNetwork = { SendMessage = function(msgId, arg) _py_record_send(msgId, arg) end }
            DataCenter = {
                ActPersonalArmsInfo = { list = {} },
                ActTimeCompeDataManager = { stage = 2 },
                AllianceCompeteDataManager = { CheckIfAllianceCompeteOpen = function() return false end },
                ActivityListDataManager = {},
            }
            """
        )

        class _LupaCD:
            def frida_eval_lua(self, pid: int, code: str, timeout: float = 8.0):
                return True, str(lua.execute(code))

        cd = _LupaCD()

        # Default read-only / dry-run call: ok=True and ZERO SFSNetwork.SendMessage calls
        res_ro = self.bot_actions._probe_preparedness_phase(cd, 77701)
        self.assertTrue(res_ro.get("ok"), f"_probe_preparedness_phase must return ok=True, got: {res_ro}")
        self.assertEqual(res_ro.get("time_compe_stage"), 2)
        self.assertEqual(
            sent_messages,
            [],
            "ActivityEventInfoGet must NOT be sent when allow_network_refresh=False",
        )

        # Explicit allow_network_refresh=True sends ActivityEventInfoGet "60002" when pa.list is empty
        res_live = self.bot_actions._probe_preparedness_phase(cd, 77701, allow_network_refresh=True)
        self.assertTrue(res_live.get("ok"))
        self.assertEqual(sent_messages, [("ActivityEventInfoGet", "60002")])

    def test_bot_actions_ensure_world_scene_colon_call_and_timeout(self) -> None:
        """ensure_world_scene must invoke SceneManager:ChangeToWorld() with colon-call and fail cleanly on timeout."""
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(
            r"""
            _G._changeToWorldCalls = 0
            SceneManager = {
                IsInWorld = function(self) return false end,
                ChangeToWorld = function(self)
                    if self ~= SceneManager then
                        error("SceneManager.ChangeToWorld must be called with colon syntax (self == SceneManager)")
                    end
                    _G._changeToWorldCalls = _G._changeToWorldCalls + 1
                end,
            }
            LuaEntry = { Player = { uid = "uid_world_1" } }
            DataCenter = {}
            """
        )

        class _LupaCD:
            def frida_eval_lua(self, pid: int, code: str, timeout: float = 8.0):
                return True, str(lua.execute(code))

        cd = _LupaCD()

        # 1. Timeout when still 0 world points -> ok=False, reason='world_scene_timeout', colon-call verified
        snaps_timeout = [
            {"ok": True, "inWorld": False, "worldPointsCount": 0},
            {"ok": True, "inWorld": True, "worldPointsCount": 0},
            {"ok": True, "inWorld": True, "worldPointsCount": 0},
        ]
        with (
            mock.patch.object(self.bot_actions, "snapshot_client", side_effect=lambda *a, **k: snaps_timeout.pop(0) if snaps_timeout else {"ok": True, "inWorld": True, "worldPointsCount": 0}),
            mock.patch.object(self.bot_actions.time, "sleep"),
        ):
            res_to = self.bot_actions.ensure_world_scene(cd, 77702, wait_seconds=0.05)
        self.assertEqual(lua.eval("_G._changeToWorldCalls"), 1, "SceneManager:ChangeToWorld() was not called with self")
        self.assertFalse(res_to.get("ok"), "ensure_world_scene must return ok=False when world points remain 0 at timeout")
        self.assertEqual(res_to.get("reason"), "world_scene_timeout")

        # 2. Succeeds once snapshot reports inWorld=True and worldPointsCount > 0
        snaps_ok = [
            {"ok": True, "inWorld": False, "worldPointsCount": 0},
            {"ok": True, "inWorld": True, "worldPointsCount": 88},
        ]
        with (
            mock.patch.object(self.bot_actions, "snapshot_client", side_effect=lambda *a, **k: snaps_ok.pop(0)),
            mock.patch.object(self.bot_actions.time, "sleep"),
        ):
            res_ok = self.bot_actions.ensure_world_scene(cd, 77702, wait_seconds=1.0)
        self.assertEqual(lua.eval("_G._changeToWorldCalls"), 2)
        self.assertTrue(res_ok.get("ok"))
        self.assertTrue(res_ok.get("switched"))
        self.assertEqual(res_ok.get("points"), 88)


def run_benchmarks() -> dict[str, dict[str, Any]]:
    """Run reproducible micro-benchmarks across Discovery, Bot, Config, and live 42 MB Map Rip."""
    results: dict[str, dict[str, Any]] = {}
    cd = _load_mod("bench_cd_mod", "tools/client discovery.py")
    mcb = _load_mod("bench_mcb_mod", "tools/multi client bot.py")
    hub = _load_mod("bench_hub_mod", "launcher/heinzhubweb.py")

    # 1. find_running_processes()
    t0 = time.perf_counter()
    procs_cold = cd.find_running_processes()
    t_cold = (time.perf_counter() - t0) * 1000.0
    t0 = time.perf_counter()
    cd.find_running_processes()
    t_warm = (time.perf_counter() - t0) * 1000.0
    results["find_running_processes"] = {"cold_ms": round(t_cold, 3), "warm_ms": round(t_warm, 3), "count": len(procs_cold)}

    # 2. discover_clients(save_cache=False)
    cd.invalidate_discovery_cache()
    t0 = time.perf_counter()
    disc_cold = cd.discover_clients(save_cache=False)
    t_disc_cold = (time.perf_counter() - t0) * 1000.0
    t0 = time.perf_counter()
    disc_warm = cd.discover_clients(save_cache=False)
    t_disc_warm = (time.perf_counter() - t0) * 1000.0
    results["discover_clients"] = {
        "cold_ms": round(t_disc_cold, 3),
        "warm_ms": round(t_disc_warm, 4),
        "clients": len(disc_warm) if isinstance(disc_warm, list) else len((disc_cold or {}).get("clients", [])),
    }

    # 3 & 4. load_config() & _load_stage_state() cold vs warm
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "bot config.json"
        mcb.save_config(mcb.default_config(), config_path=cfg_path)
        t0 = time.perf_counter()
        mcb.load_config(config_path=cfg_path)
        cfg_t1 = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        for _ in range(20):
            mcb.load_config(config_path=cfg_path)
        cfg_t_warm = ((time.perf_counter() - t0) * 1000.0) / 20.0
        results["load_config"] = {"first_ms": round(cfg_t1, 3), "repeat_avg_ms": round(cfg_t_warm, 4)}

        st_path = Path(tmp) / "bot_stage_state.json"
        mcb._save_stage_state({"version": 1, "clients": {"c1": {"stage": 3}}}, path=st_path)
        t0 = time.perf_counter()
        mcb._load_stage_state(path=st_path)
        st_t1 = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        for _ in range(20):
            mcb._load_stage_state(path=st_path)
        st_t_warm = ((time.perf_counter() - t0) * 1000.0) / 20.0
        results["load_stage_state"] = {"first_ms": round(st_t1, 3), "repeat_avg_ms": round(st_t_warm, 4)}

    # 5. get_task_status() warm vs cold (mocked subprocess for determinism)
    with mock.patch.object(mcb.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="Status: Ready\n", stderr="")):
        t0 = time.perf_counter()
        mcb.get_task_status()
        ts_1 = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        mcb.get_task_status()
        ts_2 = (time.perf_counter() - t0) * 1000.0
        results["get_task_status"] = {"first_ms": round(ts_1, 3), "second_ms": round(ts_2, 4)}

    # 6. get_status(...)
    kwargs_supported = True
    t0 = time.perf_counter()
    try:
        mcb.get_status(skip_discovery=True, skip_running=True, include_schedule=False)
    except TypeError:
        kwargs_supported = False
        mcb.get_status(skip_discovery=True)
    gs_ms = (time.perf_counter() - t0) * 1000.0
    results["get_status"] = {"elapsed_ms": round(gs_ms, 3), "kwargs_supported": kwargs_supported}

    # 7. _load_module() repeat call
    cd_path = PROJECT_ROOT / "tools" / "client discovery.py"
    t0 = time.perf_counter()
    mcb._load_module("client_discovery", cd_path)
    lm_1 = (time.perf_counter() - t0) * 1000.0
    t0 = time.perf_counter()
    mcb._load_module("client_discovery", cd_path)
    lm_2 = (time.perf_counter() - t0) * 1000.0
    results["load_module"] = {"first_ms": round(lm_1, 3), "repeat_ms": round(lm_2, 4)}

    # 8. Live 40+ MB Map Rip queries (prefer world_map_cache_s702.json, fall back to world_map_cache.json)
    cache_dir = PROJECT_ROOT / "data" / "cache"
    live_cache = cache_dir / "world_map_cache_s702.json"
    if not live_cache.exists():
        fallback_cache = cache_dir / "world_map_cache.json"
        if fallback_cache.exists():
            live_cache = fallback_cache
    if live_cache.exists():
        with hub._MAP_INDEX_LOCK:
            hub._WORLD_MAP_INDEX_CACHE.clear()
        backend = hub.HubBackend.__new__(hub.HubBackend)
        backend._lock = threading.RLock()
        backend.env = {}

        t0 = time.perf_counter()
        res_cold = backend.query_map_rip_targets({"mode": "unshielded", "min_hq": 25, "limit": 250})
        mr_cold = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        res_warm = backend.query_map_rip_targets({"mode": "unshielded", "min_hq": 25, "limit": 250})
        mr_warm = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        res_cl = backend.get_map_rip_clusters(cluster_radius=45.0, min_members=5)
        mr_cl = (time.perf_counter() - t0) * 1000.0

        results["map_rip_live_s702"] = {
            "cache_file": live_cache.name,
            "cache_mb": round(live_cache.stat().st_size / (1024 * 1024), 2),
            "cold_ms": round(mr_cold, 2),
            "warm_unshielded_ms": round(mr_warm, 2),
            "clusters_ms": round(mr_cl, 2),
            "unshielded_count": len(res_warm.get("targets", [])),
            "clusters_count": res_cl.get("count", 0),
            "cold_ok": bool(res_cold.get("ok")),
        }
    else:
        results["map_rip_live_s702"] = {
            "skipped": True,
            "reason": "neither world_map_cache_s702.json nor world_map_cache.json present",
        }

    return results


class TestPerformanceBenchmarks(unittest.TestCase):
    """Tier 4/5: Real-world performance benchmark execution & sanity verification."""

    def test_run_performance_benchmarks(self) -> None:
        bench = run_benchmarks()
        print("\n[BENCHMARK RESULTS]", json.dumps(bench, indent=2))
        self.assertIn("find_running_processes", bench)
        self.assertIn("discover_clients", bench)
        self.assertIn("load_config", bench)
        self.assertIn("load_stage_state", bench)
        self.assertIn("get_task_status", bench)
        self.assertIn("get_status", bench)
        self.assertIn("load_module", bench)
        self.assertLess(bench["discover_clients"]["warm_ms"], 50.0)
        mr = bench.get("map_rip_live_s702", {})
        cache_dir = PROJECT_ROOT / "data" / "cache"
        has_live_cache = (cache_dir / "world_map_cache_s702.json").exists() or (cache_dir / "world_map_cache.json").exists()
        if has_live_cache:
            self.assertFalse(mr.get("skipped"), f"Map Rip benchmark must not skip when cache is on disk: {mr}")
            self.assertTrue(mr["cold_ok"])
            self.assertGreater(mr["unshielded_count"], 0)


if __name__ == "__main__":
    if "--benchmark" in sys.argv:
        sys.argv.remove("--benchmark")
        print(json.dumps(run_benchmarks(), indent=2))
    else:
        unittest.main()
