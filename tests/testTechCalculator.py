"""Tech Calculator Backend & Matrix Parity Verification Suite.

Covers:
1. 100% data parity of `launcher/assets/tech badge matrix.json` against
   `megamind/raw/xml tables/APS science.json` and `aps science tab.json`
   (21 active tabs, 430 nodes, 0 badge_cost diffs, 0 max_level diffs, 0 tier/col diffs).
2. Zero-badge trees and tiers progress & completion logic (`0.0%` at Lv 0,
   `50.0%` at half levels, `100.0%` & `is_maxed=True` only when all levels are maxed).
3. Live Lua sync via lupa (`levels`, `researching` from `ScienceManager:GetScienceQueue()`,
   `badges_in_bag` from `ItemManager`/`ItemData` item 200034), legacy flat Lua payload
   compatibility, and cached inventory fallback (`{raw_clean}_inventory.json`,
   `pid_{pid}_inventory.json`, legacy `all_inventory_with_tpl.json` gated by `allow_legacy_global`).
4. Cache fallback for `{raw_clean}_tech_tree_progress.json` and strict offline Farm isolation.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock

from lupa import LuaRuntime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_hub_module():
    path = PROJECT_ROOT / "launcher" / "heinzhubweb.py"
    spec = importlib.util.spec_from_file_location("test_tech_calc_hub_mod", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _parse_badge_cost_200034(goods_need: str) -> int:
    total = 0
    for part in str(goods_need or "").split("|"):
        if "," not in part:
            continue
        iid, cnt = part.split(",", 1)
        if iid.strip() == "200034":
            total += int(cnt.strip())
    return total


class TestTechBadgeMatrixParity(unittest.TestCase):
    """Verify 100% parity between tech badge matrix.json and Megamind APS_science tables."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix_path = PROJECT_ROOT / "launcher" / "assets" / "tech badge matrix.json"
        cls.tabs_path = PROJECT_ROOT / "megamind" / "raw" / "xml tables" / "aps science tab.json"
        cls.sci_path = PROJECT_ROOT / "megamind" / "raw" / "xml tables" / "APS science.json"
        cls.matrix = json.loads(cls.matrix_path.read_text(encoding="utf-8"))
        cls.tabs = json.loads(cls.tabs_path.read_text(encoding="utf-8"))
        cls.sci = json.loads(cls.sci_path.read_text(encoding="utf-8"))

    def test_matrix_has_exact_21_active_tabs_and_430_nodes(self) -> None:
        trees = self.matrix.get("trees", [])
        self.assertEqual(len(trees), 21, f"Expected 21 active tech trees, found {len(trees)}")

        expected_tab_ids = {int(tid) for tid in self.tabs["rows"].keys()}
        actual_tab_ids = {int(t["tab_id"]) for t in trees}
        self.assertEqual(actual_tab_ids, expected_tab_ids)

        total_nodes = sum(len(tr["nodes"]) for t in trees for tr in t["tiers"])
        self.assertEqual(total_nodes, 430, f"Expected 430 active tech nodes, found {total_nodes}")

        badge_trees = [t for t in trees if int(t.get("total_badges", 0)) > 0]
        zero_badge_trees = [t["tree_name"] for t in trees if int(t.get("total_badges", 0)) == 0]
        self.assertEqual(len(badge_trees), 15)
        self.assertEqual(
            set(zero_badge_trees),
            {
                "New Home",
                "Shelter Building",
                "Elite Troops",
                "HQ Management",
                "Rapid Growth",
                "Army Expansion",
            },
        )

    def test_matrix_zero_diffs_against_aps_science_costs_levels_tiers(self) -> None:
        sci_cols = self.sci["columns"]
        idx_sid = sci_cols.index("science_id")
        idx_lv = sci_cols.index("level")
        idx_max = sci_cols.index("max_level")
        idx_pos = sci_cols.index("position")
        idx_goods = sci_cols.index("goods_need")

        by_sid: dict[str, list[list[Any]]] = {}
        for row in self.sci["rows"].values():
            by_sid.setdefault(str(row[idx_sid]), []).append(row)

        tab_cols = self.tabs["columns"]
        idx_tab_sci = tab_cols.index("science")

        node_diffs: list[Any] = []
        badge_cost_diffs: list[Any] = []
        max_level_diffs: list[Any] = []
        tier_diffs: list[Any] = []
        col_diffs: list[Any] = []
        rollup_diffs: list[Any] = []

        for tree in self.matrix["trees"]:
            tid = str(tree["tab_id"])
            tab_row = self.tabs["rows"][tid]
            expected_sids = [s for s in str(tab_row[idx_tab_sci]).split(";") if s and s in by_sid]

            matrix_nodes: dict[str, tuple[int, dict[str, Any]]] = {}
            tree_badge_sum = 0
            tree_level_sum = 0

            for tr in tree["tiers"]:
                tier_badge_sum = 0
                tier_level_sum = 0
                for node in tr["nodes"]:
                    nid = str(node["id"])
                    matrix_nodes[nid] = (int(tr["tier"]), node)
                    costs = node["badge_costs"]
                    max_lv = int(node["max_level"])
                    if len(costs) != max_lv:
                        rollup_diffs.append(("badge_costs_len", nid, len(costs), max_lv))
                    if sum(costs) != int(node["total_badges"]):
                        rollup_diffs.append(("node_total_badges", nid, sum(costs), node["total_badges"]))
                    tier_badge_sum += sum(costs)
                    tier_level_sum += max_lv
                if tier_badge_sum != int(tr["total_badges"]):
                    rollup_diffs.append(("tier_total_badges", tid, tr["tier"], tier_badge_sum, tr["total_badges"]))
                if tier_level_sum != int(tr["total_levels"]):
                    rollup_diffs.append(("tier_total_levels", tid, tr["tier"], tier_level_sum, tr["total_levels"]))
                tree_badge_sum += tier_badge_sum
                tree_level_sum += tier_level_sum

            if tree_badge_sum != int(tree["total_badges"]):
                rollup_diffs.append(("tree_total_badges", tid, tree_badge_sum, tree["total_badges"]))
            if tree_level_sum != int(tree["total_levels"]):
                rollup_diffs.append(("tree_total_levels", tid, tree_level_sum, tree["total_levels"]))

            missing = set(expected_sids) - set(matrix_nodes.keys())
            extra = set(matrix_nodes.keys()) - set(expected_sids)
            if missing or extra:
                node_diffs.append((tid, sorted(missing), sorted(extra)))

            for sid, (m_tier, m_node) in matrix_nodes.items():
                rows = sorted(by_sid[sid], key=lambda r: int(r[idx_lv]))
                exp_max = int(rows[0][idx_max])
                if exp_max != int(m_node["max_level"]):
                    max_level_diffs.append((sid, exp_max, m_node["max_level"]))

                pos_str = next((str(r[idx_pos]) for r in rows if r[idx_pos]), "")
                self.assertIn(";", pos_str, f"Missing tier;col position in APS_science for {sid}")
                exp_tier, exp_col = (int(x) for x in pos_str.split(";", 1))
                if exp_tier != m_tier:
                    tier_diffs.append((sid, exp_tier, m_tier))
                if exp_col != int(m_node["col"]):
                    col_diffs.append((sid, exp_col, m_node["col"]))

                exp_costs = [_parse_badge_cost_200034(r[idx_goods]) for r in rows]
                if exp_costs != m_node["badge_costs"]:
                    badge_cost_diffs.append((sid, exp_costs, m_node["badge_costs"]))

        self.assertEqual(node_diffs, [], f"Tab node set mismatches: {node_diffs}")
        self.assertEqual(badge_cost_diffs, [], f"Badge cost diffs vs APS_science: {badge_cost_diffs}")
        self.assertEqual(max_level_diffs, [], f"max_level diffs vs APS_science: {max_level_diffs}")
        self.assertEqual(tier_diffs, [], f"Tier diffs vs APS_science: {tier_diffs}")
        self.assertEqual(col_diffs, [], f"Column diffs vs APS_science: {col_diffs}")
        self.assertEqual(rollup_diffs, [], f"Matrix rollup mismatches: {rollup_diffs}")


class TestTechCalculatorBackend(unittest.TestCase):
    """Behavioral, Lua-sync, caching, and isolation tests for HubBackend.get_tech_calculator_data()."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.hub = _load_hub_module()

    def _make_backend(self):
        with (
            mock.patch.object(self.hub.HubBackend, "_load_cached_state"),
            mock.patch.object(self.hub.HubBackend, "_load_always_on_daemon_config"),
            mock.patch.object(self.hub.HubBackend, "_start_always_on_daemon"),
            mock.patch.object(self.hub.HubBackend, "log"),
        ):
            return self.hub.HubBackend()

    def _clear_json_cache(self) -> None:
        with self.hub._JSON_MEM_LOCK:
            self.hub._JSON_MEM_CACHE.clear()

    def _run_with_tmp_env(self, tmp: str):
        orig_heinz = self.hub.HEINZ_DATA_DIR
        orig_data = self.hub.DATA_DIR
        self.hub.HEINZ_DATA_DIR = tmp
        self.hub.DATA_DIR = tmp
        self._clear_json_cache()
        return orig_heinz, orig_data

    def _restore_env(self, orig_heinz: str, orig_data: str) -> None:
        self.hub.HEINZ_DATA_DIR = orig_heinz
        self.hub.DATA_DIR = orig_data
        self._clear_json_cache()

    def test_zero_badge_trees_and_tiers_progress_and_maxed_flags(self) -> None:
        """Zero-badge trees & tiers must report 0.0% at Lv 0, 50.0% at half, and 100.0% + is_maxed only when maxed."""
        synthetic_matrix = {
            "version": 2,
            "trees": [
                {
                    "tab_id": 1,
                    "order": 1,
                    "tree_name": "Zero Badge Tree",
                    "total_badges": 0,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "300100", "name": "Node A", "max_level": 4, "col": 2, "badge_costs": [0, 0, 0, 0]},
                                {"id": "300200", "name": "Node B", "max_level": 4, "col": 6, "badge_costs": [0, 0, 0, 0]},
                            ],
                        },
                        {
                            "tier": 2,
                            "nodes": [
                                {"id": "300300", "name": "Node C", "max_level": 2, "col": 4, "badge_costs": [0, 0]},
                            ],
                        },
                    ],
                },
                {
                    "tab_id": 22,
                    "order": 2,
                    "tree_name": "Stale Header Badge Tree",
                    "total_badges": 0,  # Intentionally stale header; backend must use computed tree_tot > 0
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "1600000", "name": "Badge Node", "max_level": 2, "col": 4, "badge_costs": [100, 300]},
                            ],
                        },
                    ],
                },
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            jcache = Path(tmp) / "json cache"
            jcache.mkdir(parents=True, exist_ok=True)
            matrix_path = Path(tmp) / "tech badge matrix.json"
            matrix_path.write_text(json.dumps(synthetic_matrix), encoding="utf-8")

            backend = self._make_backend()
            orig = self._run_with_tmp_env(tmp)
            try:
                with (
                    mock.patch.object(self.hub, "client_discovery", None),
                    mock.patch.object(backend, "_discover_running_clients", return_value=[]),
                    mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                    mock.patch.object(backend, "log"),
                ):
                    # Case 1: Lv 0 everywhere
                    res0 = backend.get_tech_calculator_data()
                    self.assertTrue(res0["ok"])
                    z0 = res0["trees"][0]
                    b0 = res0["trees"][1]
                    self.assertFalse(z0["has_badges"])
                    self.assertFalse(z0["is_maxed"])
                    self.assertEqual(z0["progress_pct"], 0.0)
                    self.assertEqual(z0["levels_done"], 0)
                    self.assertEqual(z0["levels_total"], 10)
                    for tr in z0["tiers"]:
                        self.assertFalse(tr["has_badges"])
                        self.assertFalse(tr["is_maxed"])
                        self.assertEqual(tr["progress_pct"], 0.0)
                        self.assertEqual(tr["levels_done"], 0)
                        self.assertEqual(tr["nodes_done"], 0)
                    # Stale tree["total_badges"]==0 must NOT exclude real badge tree from trees_with_badges_count
                    self.assertTrue(b0["has_badges"])
                    self.assertEqual(res0["overall"]["trees_with_badges_count"], 1)
                    self.assertEqual(res0["overall"]["trees_maxed_count"], 0)
                    self.assertEqual(res0["overall"]["all_trees_maxed_count"], 0)
                    self.assertEqual(res0["overall"]["overall_levels_done"], 0)
                    self.assertEqual(res0["overall"]["overall_levels_total"], 12)
                    self.assertEqual(res0["overall"]["overall_levels_percentage"], 0.0)

                    # Case 2: Half levels on Zero Badge Tree (4/8 in tier 1 = 50.0%, 1/2 in tier 2 = 50.0%, 5/10 overall = 50.0%)
                    (jcache / "tech_tree_progress.json").write_text(
                        json.dumps({"300100": 4, "300200": 0, "300300": 1}),
                        encoding="utf-8",
                    )
                    self._clear_json_cache()
                    res_half = backend.get_tech_calculator_data()
                    zh = res_half["trees"][0]
                    self.assertFalse(zh["is_maxed"])
                    self.assertEqual(zh["progress_pct"], 50.0)
                    self.assertEqual(zh["levels_done"], 5)
                    self.assertEqual(zh["tiers"][0]["progress_pct"], 50.0)
                    self.assertFalse(zh["tiers"][0]["is_maxed"])
                    self.assertEqual(zh["tiers"][0]["levels_done"], 4)
                    self.assertEqual(zh["tiers"][0]["levels_total"], 8)
                    self.assertEqual(zh["tiers"][0]["nodes_done"], 1)
                    self.assertEqual(zh["tiers"][0]["nodes_total"], 2)
                    self.assertEqual(zh["tiers"][1]["progress_pct"], 50.0)
                    self.assertFalse(zh["tiers"][1]["is_maxed"])
                    self.assertEqual(res_half["overall"]["all_trees_maxed_count"], 0)
                    self.assertEqual(res_half["overall"]["trees_maxed_count"], 0)

                    # Case 3: Fully maxed Zero Badge Tree ONLY
                    (jcache / "tech_tree_progress.json").write_text(
                        json.dumps({"300100": 4, "300200": 4, "300300": 2}),
                        encoding="utf-8",
                    )
                    self._clear_json_cache()
                    res_zmax = backend.get_tech_calculator_data()
                    zm = res_zmax["trees"][0]
                    self.assertTrue(zm["is_maxed"])
                    self.assertEqual(zm["progress_pct"], 100.0)
                    self.assertTrue(all(tr["is_maxed"] and tr["progress_pct"] == 100.0 for tr in zm["tiers"]))
                    self.assertEqual(res_zmax["overall"]["all_trees_maxed_count"], 1)
                    self.assertEqual(res_zmax["overall"]["trees_maxed_count"], 0)
                    self.assertEqual(res_zmax["overall"]["overall_levels_done"], 10)
                    self.assertEqual(res_zmax["overall"]["overall_levels_percentage"], 83.3)

                    # Case 4: Both trees maxed
                    (jcache / "tech_tree_progress.json").write_text(
                        json.dumps({"300100": 4, "300200": 4, "300300": 2, "1600000": 2}),
                        encoding="utf-8",
                    )
                    self._clear_json_cache()
                    res_all = backend.get_tech_calculator_data()
                    self.assertEqual(res_all["overall"]["trees_maxed_count"], 1)
                    self.assertEqual(res_all["overall"]["all_trees_maxed_count"], 2)
                    self.assertEqual(res_all["overall"]["overall_levels_percentage"], 100.0)
                    self.assertEqual(res_all["overall"]["overall_percentage"], 100.0)
            finally:
                self._restore_env(*orig)

    def test_real_matrix_at_level_zero_never_marks_zero_badge_trees_complete(self) -> None:
        """Against the real 21-tree tech badge matrix.json, Lv 0 reports 0 maxed trees and 0.0% on all 6 zero-badge trees."""
        real_matrix_path = PROJECT_ROOT / "launcher" / "assets" / "tech badge matrix.json"
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "json cache").mkdir(parents=True, exist_ok=True)
            backend = self._make_backend()
            orig = self._run_with_tmp_env(tmp)
            try:
                with (
                    mock.patch.object(self.hub, "client_discovery", None),
                    mock.patch.object(backend, "_discover_running_clients", return_value=[]),
                    mock.patch.object(backend, "_find_asset", return_value=str(real_matrix_path)),
                    mock.patch.object(backend, "log"),
                ):
                    res = backend.get_tech_calculator_data()
                    self.assertTrue(res["ok"])
                    ov = res["overall"]
                    self.assertEqual(ov["trees_total_count"], 21)
                    self.assertEqual(ov["trees_with_badges_count"], 15)
                    self.assertEqual(ov["trees_maxed_count"], 0)
                    self.assertEqual(ov["all_trees_maxed_count"], 0)
                    self.assertEqual(ov["overall_levels_done"], 0)
                    self.assertEqual(ov["overall_levels_total"], 4075)
                    self.assertEqual(ov["overall_levels_percentage"], 0.0)
                    self.assertEqual(ov["overall_percentage"], 0.0)

                    zero_trees = [t for t in res["trees"] if not t["has_badges"]]
                    self.assertEqual(len(zero_trees), 6)
                    for zt in zero_trees:
                        self.assertFalse(zt["is_maxed"], f"{zt['tree_name']} must not be maxed at Lv 0")
                        self.assertEqual(zt["progress_pct"], 0.0, f"{zt['tree_name']} must be 0.0% at Lv 0")
                        for tr in zt["tiers"]:
                            self.assertFalse(tr["is_maxed"])
                            self.assertEqual(tr["progress_pct"], 0.0)
                            for n in tr["nodes"]:
                                self.assertEqual(len(n["badge_costs"]), n["max_level"])
                                self.assertFalse(n["has_badges"])
                                self.assertFalse(n["can_afford_next"])
            finally:
                self._restore_env(*orig)

    def test_live_structured_lua_sync_badges_queue_and_affordability(self) -> None:
        """Real lua_sci executed in lupa returns levels, researching queue IDs, and live item 200034 badges."""
        matrix = {
            "trees": [
                {
                    "tab_id": 22,
                    "order": 1,
                    "tree_name": "Hero Training",
                    "total_badges": 1600,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "1600000", "name": "Attack", "max_level": 3, "col": 2, "badge_costs": [100, 200, 300]},
                                {"id": "1601000", "name": "Strength", "max_level": 2, "col": 6, "badge_costs": [400, 600]},
                            ],
                        },
                    ],
                },
                {
                    "tab_id": 9,
                    "order": 2,
                    "tree_name": "Military Strategies",
                    "total_badges": 500,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "1180000", "name": "Fire Up", "max_level": 2, "col": 4, "badge_costs": [200, 300]},
                            ],
                        },
                    ],
                },
            ]
        }

        lua_bag_variants = [
            (
                "ItemManager.GetItemNum",
                r"""
                ItemManager = {
                    GetItemNum = function(self, id)
                        if tonumber(id) == 200034 then return 450 end
                        return 0
                    end
                }
                """,
                450,
            ),
            (
                "ItemManager.allItems",
                r"""
                ItemManager = {
                    allItems = {
                        u1 = { itemId = 200034, count = 200 },
                        u2 = { id = 200034, num = 250 },
                        u3 = { itemId = 999999, count = 9999 },
                    }
                }
                """,
                450,
            ),
            (
                "ItemData.GetItemCount",
                r"""
                ItemManager = {},
                ItemData = {
                    GetItemCount = function(self, id)
                        if tonumber(id) == 200034 then return 450 end
                        return 0
                    end
                }
                """,
                450,
            ),
            (
                "ItemData.ItemInfos",
                r"""
                ItemManager = {},
                ItemData = {
                    ItemInfos = {
                        uuid_a = { itemId = 200034, count = 450 },
                        uuid_b = { itemId = 1001, count = 99 },
                    }
                }
                """,
                450,
            ),
        ]

        for label, bag_lua_snippet, expected_bag in lua_bag_variants:
            with self.subTest(bag_source=label), tempfile.TemporaryDirectory() as tmp:
                jcache = Path(tmp) / "json cache"
                jcache.mkdir(parents=True, exist_ok=True)
                matrix_path = Path(tmp) / "tech badge matrix.json"
                matrix_path.write_text(json.dumps(matrix), encoding="utf-8")

                backend = self._make_backend()
                backend.running_clients = [{"pid": 101, "label": "Main", "role": "main"}]

                def _eval_lua(pid: int, code: str, timeout: float = 6.0):
                    lua = LuaRuntime(unpack_returned_tuples=True)
                    lua.execute(
                        f"""
                        DataCenter = {{
                            ScienceDataManager = {{
                                allScience = {{
                                    ["1600000"] = {{ level = 1 }},
                                    ["1601000"] = {{ lv = 2 }},
                                    ["1180000"] = 1,
                                }}
                            }},
                            ScienceManager = {{
                                GetScienceQueue = function(self)
                                    return {{
                                        {{ scienceId = "1600000", state = 2 }},
                                        {{ itemId = 1180002, state = 2 }},
                                        {{ scienceId = "1601000", state = 0 }},
                                    }}
                                end
                            }},
                            {bag_lua_snippet}
                        }}
                        """
                    )
                    return True, str(lua.execute(code))

                mock_cd = SimpleNamespace(
                    _xlua_loaded=mock.MagicMock(return_value=True),
                    frida_eval_lua=mock.MagicMock(side_effect=_eval_lua),
                    find_running_processes=mock.MagicMock(return_value=list(backend.running_clients)),
                )

                orig = self._run_with_tmp_env(tmp)
                try:
                    with (
                        mock.patch.object(self.hub, "client_discovery", mock_cd),
                        mock.patch.object(backend, "_discover_running_clients", return_value=list(backend.running_clients)),
                        mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                        mock.patch.object(backend, "log"),
                    ):
                        res = backend.get_tech_calculator_data(pid=101, force_live=True)
                        self.assertTrue(res["ok"])
                        self.assertTrue(res["is_live"])

                        # Invested: 1600000 lv1=100, 1601000 lv2=1000, 1180000 lv1=200 => 1300
                        # Remaining: 1600000 rem=500, 1601000 rem=0, 1180000 rem=300 => 800
                        ov = res["overall"]
                        self.assertEqual(ov["total_badges_invested"], 1300)
                        self.assertEqual(ov["total_badges_remaining"], 800)
                        self.assertEqual(ov["total_badges_whole_game"], 2100)
                        self.assertEqual(ov["badges_in_bag"], expected_bag)
                        self.assertEqual(ov["net_badges_deficit"], 350)

                        t_hero, t_mil = res["trees"]
                        # Hero Training: remaining=500, bag=450 -> deficit=50, can_max_now=False
                        self.assertTrue(t_hero["has_badges"])
                        self.assertEqual(t_hero["badges_remaining"], 500)
                        self.assertEqual(t_hero["net_badges_deficit"], 50)
                        self.assertFalse(t_hero["can_max_now"])

                        # Military Strategies: remaining=300, bag=450 -> deficit=0, can_max_now=True
                        self.assertTrue(t_mil["has_badges"])
                        self.assertEqual(t_mil["badges_remaining"], 300)
                        self.assertEqual(t_mil["net_badges_deficit"], 0)
                        self.assertTrue(t_mil["can_max_now"])

                        # Node-level contracts
                        n_atk, n_str = t_hero["tiers"][0]["nodes"]
                        n_fire = t_mil["tiers"][0]["nodes"][0]

                        self.assertEqual(n_atk["badge_costs"], [100, 200, 300])
                        self.assertEqual(len(n_atk["badge_costs"]), n_atk["max_level"])
                        self.assertEqual(n_atk["total_badges"], 600)
                        self.assertTrue(n_atk["has_badges"])
                        self.assertEqual(n_atk["next_level_badges"], 200)
                        self.assertTrue(n_atk["is_researching"])
                        self.assertTrue(n_atk["can_afford_next"])

                        self.assertTrue(n_str["is_maxed"])
                        self.assertFalse(n_str["is_researching"], "Idle state=0 queue item must not be flagged researching")
                        self.assertFalse(n_str["can_afford_next"], "Maxed node must not be flagged can_afford_next")

                        self.assertTrue(n_fire["is_researching"], "Level-specific science id 1180002 must map to 1180000")
                        self.assertEqual(n_fire["next_level_badges"], 300)
                        self.assertTrue(n_fire["can_afford_next"])

                        # Backwards-compatible flat disk cache
                        saved = json.loads((jcache / "main_tech_progress.json").read_text(encoding="utf-8"))
                        self.assertEqual(saved, {"1600000": 1, "1601000": 2, "1180000": 1})
                        self.assertIn("sci:main", backend._live_sync_ts)
                finally:
                    self._restore_env(*orig)

    def test_live_lua_single_queue_table_queue_manager_fallback_and_ttl(self) -> None:
        """Single-object GetScienceQueue(), QueueDataManager fallback, pid inventory fallback, and 60s TTL."""
        matrix = {
            "trees": [
                {
                    "tab_id": 22,
                    "order": 1,
                    "tree_name": "Hero Training",
                    "total_badges": 600,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "1600000", "name": "Attack", "max_level": 3, "col": 2, "badge_costs": [100, 200, 300]},
                            ],
                        }
                    ],
                }
            ]
        }

        queue_cases = [
            (
                "single_queue_object",
                r"""
                ScienceManager = {
                    GetScienceQueue = function(self)
                        return { scienceId = 1600000, state = 2 }
                    end
                }
                """,
            ),
            (
                "queue_data_manager_fallback",
                r"""
                QueueDataManager = {
                    GetAllQueueByType = function(self, qType)
                        if tonumber(qType) == 6 then
                            return { { itemId = 1600001, state = 2 } }
                        end
                        return {}
                    end
                }
                """,
            ),
        ]

        for label, q_lua in queue_cases:
            with self.subTest(queue_source=label), tempfile.TemporaryDirectory() as tmp:
                jcache = Path(tmp) / "json cache"
                jcache.mkdir(parents=True, exist_ok=True)
                matrix_path = Path(tmp) / "tech badge matrix.json"
                matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
                (jcache / "pid_404_inventory.json").write_text(
                    json.dumps([{"itemId": 200034, "count": 210}]),
                    encoding="utf-8",
                )

                backend = self._make_backend()
                backend.running_clients = [{"pid": 404, "label": "Client", "role": "farm"}]
                eval_count = 0

                def _eval_lua(pid: int, code: str, timeout: float = 6.0):
                    nonlocal eval_count
                    eval_count += 1
                    lua = LuaRuntime(unpack_returned_tuples=True)
                    lua.execute(
                        f"""
                        NewQueueType = {{ Science = 6 }}
                        DataCenter = {{
                            ScienceDataManager = {{ allScience = {{ ["1600000"] = {{ level = 1 }} }} }},
                            {q_lua}
                        }}
                        """
                    )
                    return True, str(lua.execute(code))

                mock_cd = SimpleNamespace(
                    _xlua_loaded=mock.MagicMock(return_value=True),
                    frida_eval_lua=mock.MagicMock(side_effect=_eval_lua),
                    find_running_processes=mock.MagicMock(return_value=list(backend.running_clients)),
                )

                orig = self._run_with_tmp_env(tmp)
                try:
                    with (
                        mock.patch.object(self.hub, "client_discovery", mock_cd),
                        mock.patch.object(backend, "_discover_running_clients", return_value=list(backend.running_clients)),
                        mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                        mock.patch.object(backend, "log"),
                    ):
                        res = backend.get_tech_calculator_data(pid=404, force_live=True)
                        self.assertTrue(res["is_live"])
                        self.assertEqual(eval_count, 1)
                        # Live Lua returned badges_in_bag=-1, so falls back to pid_404_inventory.json (210)
                        self.assertEqual(res["overall"]["badges_in_bag"], 210)
                        node = res["trees"][0]["tiers"][0]["nodes"][0]
                        self.assertTrue(node["is_researching"])
                        self.assertTrue(node["can_afford_next"])
                        self.assertIn("sci:pid_404", backend._live_sync_ts)

                        # Subsequent non-forced call within 60s TTL uses fresh disk cache without re-running Lua
                        res_cached = backend.get_tech_calculator_data(pid=404, force_live=False)
                        self.assertEqual(eval_count, 1)
                        self.assertFalse(res_cached["is_live"])
                        self.assertEqual(res_cached["overall"]["total_badges_invested"], 100)
                        self.assertEqual(res_cached["overall"]["badges_in_bag"], 210)
                finally:
                    self._restore_env(*orig)

    def test_legacy_flat_lua_payload_and_inventory_cache_fallback(self) -> None:
        """Legacy flat {tech_id: lv} Lua response and badges_in_bag=-1 must cleanly fall back to cached inventory."""
        matrix = {
            "trees": [
                {
                    "tab_id": 1,
                    "order": 1,
                    "tree_name": "Badge Tree",
                    "total_badges": 500,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "tech_101", "name": "Node 1", "max_level": 2, "col": 4, "badge_costs": [200, 300]},
                            ],
                        },
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            jcache = Path(tmp) / "json cache"
            jcache.mkdir(parents=True, exist_ok=True)
            matrix_path = Path(tmp) / "tech badge matrix.json"
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")

            # Per-account inventory cache with item 200034
            (jcache / "main_inventory.json").write_text(
                json.dumps([{"itemId": 200034, "count": 250}, {"itemId": 1001, "count": 99}]),
                encoding="utf-8",
            )

            backend = self._make_backend()
            backend.running_clients = [{"pid": 101, "label": "Main", "role": "main"}]

            mock_cd = SimpleNamespace(
                _xlua_loaded=mock.MagicMock(return_value=True),
                frida_eval_lua=mock.MagicMock(return_value=(True, json.dumps({"tech_101": 1}))),
                find_running_processes=mock.MagicMock(return_value=list(backend.running_clients)),
            )

            orig = self._run_with_tmp_env(tmp)
            try:
                with (
                    mock.patch.object(self.hub, "client_discovery", mock_cd),
                    mock.patch.object(backend, "_discover_running_clients", return_value=list(backend.running_clients)),
                    mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                    mock.patch.object(backend, "log"),
                ):
                    res = backend.get_tech_calculator_data(pid=101, force_live=True)
                    self.assertTrue(res["ok"])
                    self.assertTrue(res["is_live"])
                    self.assertEqual(res["overall"]["total_badges_invested"], 200)
                    self.assertEqual(res["overall"]["total_badges_remaining"], 300)
                    self.assertEqual(res["overall"]["badges_in_bag"], 250)
                    self.assertEqual(res["overall"]["net_badges_deficit"], 50)
                    node = res["trees"][0]["tiers"][0]["nodes"][0]
                    self.assertFalse(node["is_researching"])
                    self.assertFalse(node["can_afford_next"], "250 in bag cannot afford 300 next level")

                    # Also test legacy "{}" response
                    mock_cd.frida_eval_lua.return_value = (True, "{}")
                    res_empty = backend.get_tech_calculator_data(pid=101, force_live=True)
                    self.assertTrue(res_empty["is_live"])
                    self.assertEqual(res_empty["overall"]["total_badges_invested"], 0)
                    self.assertEqual(res_empty["overall"]["badges_in_bag"], 250)
                    self.assertTrue(
                        res_empty["trees"][0]["tiers"][0]["nodes"][0]["can_afford_next"],
                        "250 in bag can afford 200 Lv 1",
                    )
                    self.assertEqual(json.loads((jcache / "main_tech_progress.json").read_text(encoding="utf-8")), {})

                    # Also test structured Lua payload with badges_in_bag = -1 falling back to inventory cache
                    mock_cd.frida_eval_lua.return_value = (
                        True,
                        json.dumps({"levels": {"tech_101": 1}, "researching": ["tech_101"], "badges_in_bag": -1}),
                    )
                    res_neg = backend.get_tech_calculator_data(pid=101, force_live=True)
                    self.assertEqual(res_neg["overall"]["badges_in_bag"], 250)
                    self.assertTrue(res_neg["trees"][0]["tiers"][0]["nodes"][0]["is_researching"])
            finally:
                self._restore_env(*orig)

    def test_cache_fallback_loads_raw_clean_tech_tree_progress_json(self) -> None:
        """Cache fallback must load {raw_clean}_tech_tree_progress.json right after {raw_clean}_tech_progress.json."""
        matrix = {
            "trees": [
                {
                    "tab_id": 22,
                    "order": 1,
                    "tree_name": "Hero Training",
                    "total_badges": 270,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "1600000", "name": "Attack", "max_level": 2, "col": 2, "badge_costs": [120, 150]},
                            ],
                        }
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            jcache = Path(tmp) / "json cache"
            jcache.mkdir(parents=True, exist_ok=True)
            matrix_path = Path(tmp) / "tech badge matrix.json"
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")

            # Real nested snapshot format like heinzy_tech_tree_progress.json
            (jcache / "heinzy_tech_tree_progress.json").write_text(
                json.dumps({
                    "trees": [
                        {
                            "tab_id": 22,
                            "nodes": [{"tech_id": "1600000", "level": 1, "max_level": 2}],
                        }
                    ]
                }),
                encoding="utf-8",
            )
            (jcache / "heinzy_inventory.json").write_text(
                json.dumps([{"itemId": 200034, "count": 500}]),
                encoding="utf-8",
            )

            backend = self._make_backend()
            backend.running_clients = [{"pid": 303, "label": "Heinzy", "role": "main"}]
            mock_cd = SimpleNamespace(
                _xlua_loaded=mock.MagicMock(return_value=False),
                frida_eval_lua=mock.MagicMock(),
                find_running_processes=mock.MagicMock(return_value=list(backend.running_clients)),
            )

            orig = self._run_with_tmp_env(tmp)
            try:
                with (
                    mock.patch.object(self.hub, "client_discovery", mock_cd),
                    mock.patch.object(backend, "_discover_running_clients", return_value=list(backend.running_clients)),
                    mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                    mock.patch.object(backend, "log"),
                ):
                    res = backend.get_tech_calculator_data(pid=303)
                    self.assertTrue(res["ok"])
                    self.assertFalse(res["is_live"])
                    self.assertEqual(res["overall"]["total_badges_invested"], 120)
                    self.assertEqual(res["overall"]["total_badges_remaining"], 150)
                    self.assertEqual(res["overall"]["badges_in_bag"], 500)
                    self.assertTrue(res["trees"][0]["can_max_now"])

                    # When {raw_clean}_tech_progress.json also exists, it takes priority over _tech_tree_progress.json
                    (jcache / "heinzy_tech_progress.json").write_text(json.dumps({"1600000": 2}), encoding="utf-8")
                    self._clear_json_cache()
                    res2 = backend.get_tech_calculator_data(pid=303)
                    self.assertEqual(res2["overall"]["total_badges_invested"], 270)
                    self.assertTrue(res2["trees"][0]["is_maxed"])
            finally:
                self._restore_env(*orig)

    def test_strict_offline_farm_isolation_for_tech_and_badges_bag(self) -> None:
        """Offline Farm accounts must NEVER inherit Main's or legacy global tech progress or bag badges."""
        matrix = {
            "trees": [
                {
                    "tab_id": 22,
                    "order": 1,
                    "tree_name": "Hero Training",
                    "total_badges": 1000,
                    "tiers": [
                        {
                            "tier": 1,
                            "nodes": [
                                {"id": "1600000", "name": "Attack", "max_level": 2, "col": 2, "badge_costs": [400, 600]},
                            ],
                        }
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            jcache = Path(tmp) / "json cache"
            jcache.mkdir(parents=True, exist_ok=True)
            matrix_path = Path(tmp) / "tech badge matrix.json"
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")

            # Populate Main + legacy global caches with high levels and huge badge stock
            (jcache / "tech_tree_progress.json").write_text(json.dumps({"1600000": 2}), encoding="utf-8")
            (jcache / "main_tech_progress.json").write_text(json.dumps({"1600000": 2}), encoding="utf-8")
            (jcache / "all_inventory_with_tpl.json").write_text(
                json.dumps({"1": {"itemId": 200034, "count": 99999}}),
                encoding="utf-8",
            )
            (jcache / "main_inventory.json").write_text(
                json.dumps([{"itemId": 200034, "count": 55555}]),
                encoding="utf-8",
            )

            backend = self._make_backend()
            backend.running_clients = [
                {"pid": 101, "label": "Main", "role": "main"},
                {"pid": 202, "label": "Farm_Beta", "role": "farm"},
            ]
            mock_cd = SimpleNamespace(
                _xlua_loaded=mock.MagicMock(return_value=False),
                frida_eval_lua=mock.MagicMock(),
                find_running_processes=mock.MagicMock(return_value=list(backend.running_clients)),
            )

            orig = self._run_with_tmp_env(tmp)
            try:
                with (
                    mock.patch.object(self.hub, "client_discovery", mock_cd),
                    mock.patch.object(backend, "_discover_running_clients", return_value=list(backend.running_clients)),
                    mock.patch.object(backend, "_find_asset", return_value=str(matrix_path)),
                    mock.patch.object(backend, "log"),
                ):
                    # Offline Farm_Beta with explicit pid=202 -> 0 tech, 0 bag (no leak!)
                    farm_res = backend.get_tech_calculator_data(pid=202)
                    self.assertTrue(farm_res["ok"])
                    self.assertEqual(farm_res["overall"]["total_badges_invested"], 0)
                    self.assertEqual(farm_res["overall"]["badges_in_bag"], 0)
                    self.assertEqual(farm_res["overall"]["net_badges_deficit"], 1000)

                    # Offline Farm_Beta selected via selected_client_label with pid=None -> still 0 tech, 0 bag!
                    backend.selected_client_label = "Farm_Beta"
                    with mock.patch.object(backend, "_discover_running_clients", return_value=[]):
                        farm_sel_res = backend.get_tech_calculator_data(pid=None)
                    self.assertEqual(farm_sel_res["overall"]["total_badges_invested"], 0)
                    self.assertEqual(farm_sel_res["overall"]["badges_in_bag"], 0)

                    # Give Farm_Beta its own inventory cache -> reads only its own 320 badges
                    (jcache / "farm_beta_inventory.json").write_text(
                        json.dumps([{"itemId": 200034, "count": 320}]),
                        encoding="utf-8",
                    )
                    self._clear_json_cache()
                    farm_own_bag = backend.get_tech_calculator_data(pid=202)
                    self.assertEqual(farm_own_bag["overall"]["badges_in_bag"], 320)
                    self.assertEqual(farm_own_bag["overall"]["net_badges_deficit"], 680)

                    # Legacy offline Main (pid=None, no farm selected, no main_inventory.json) reads all_inventory_with_tpl.json
                    backend.selected_client_label = ""
                    (jcache / "main_inventory.json").unlink()
                    self._clear_json_cache()
                    with mock.patch.object(backend, "_discover_running_clients", return_value=[]):
                        legacy_main = backend.get_tech_calculator_data(pid=None)
                    self.assertEqual(legacy_main["overall"]["total_badges_invested"], 1000)
                    self.assertEqual(legacy_main["overall"]["badges_in_bag"], 99999)
                    self.assertEqual(legacy_main["overall"]["net_badges_deficit"], 0)
            finally:
                self._restore_env(*orig)


if __name__ == "__main__":
    unittest.main()
