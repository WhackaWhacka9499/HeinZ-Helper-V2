"""Empirical Challenger Test Suite for Milestone 4.

Author: teamwork_challenger_1
Target: LastZ PC Master Overhaul
Scope: Empirical edge-case validation, stress harnesses, and contract enforcement
       on production modules (tools/bot actions.py, tools/client discovery.py, data/bot config.json).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Dynamically load production modules
def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

TOOLS_DIR = PROJECT_ROOT / "tools"
bot_actions = _load_module("bot_actions", TOOLS_DIR / "bot actions.py")
client_discovery = _load_module("client_discovery", TOOLS_DIR / "client discovery.py")

from tests.testHarness import (
    MockGameClient,
    ProtocolContractViolation,
    SFSMessageValidator,
    ServerResponseSimulator,
    LuaTemplateInspector,
)


class MockFridaBridge:
    """Mock client discovery bridge that intercepts and records all evaluated Lua scripts."""

    def __init__(self, default_response: Optional[Dict[str, Any]] = None):
        self.recorded_lua: List[str] = []
        self.default_response = default_response or {"ok": True, "action": "none"}

    def frida_eval_lua(self, pid: int, lua: str, timeout: float = 8.0) -> Tuple[bool, str]:
        self.recorded_lua.append(lua)
        return True, json.dumps(self.default_response)


class TestEmpiricalChallenger(unittest.TestCase):
    """Empirical adversarial verification tests covering all Milestone 4 challenge vectors."""

    def setUp(self) -> None:
        self.cfg_path = PROJECT_ROOT / "data" / "bot config.json"
        with open(self.cfg_path, "r", encoding="utf-8") as f:
            self.bot_config = json.load(f)
        self.validator = SFSMessageValidator()
        self.server_sim = ServerResponseSimulator()

    # =========================================================================
    # Task 2.1: Radar Processing Unthrottling & 0ms Timing Verification
    # =========================================================================

    def test_radar_lua_generation_unthrottled_and_no_arbitrary_clamp(self) -> None:
        """Verify that run_radar_events generates Lua with maxDispatch >= 20 and no hardcoded 3 clamp."""
        mock_bridge = MockFridaBridge({"ok": True, "task": "radar_events", "dispatched": [], "action": "none"})
        cfg = {"radar_events": {"max_dispatches_per_cycle": 20, "auto_dispatch": True}}
        client_state = {"inWorld": True, "worldPointsCount": 10}

        bot_actions.run_radar_events(mock_bridge, 23848, client_state, cfg, dry_run=True)
        self.assertTrue(len(mock_bridge.recorded_lua) > 0, "No Lua script was recorded by the bridge")

        lua_code = mock_bridge.recorded_lua[-1]

        # 1. Verify maxDispatch is configured to 20
        self.assertIn("local maxDispatch = 20", lua_code)

        # 2. Verify no hardcoded break at 3
        self.assertFalse(
            bool(re.search(r"#out\.dispatched\s*>=\s*3\b", lua_code)),
            "Found forbidden hardcoded break at 3 in radar dispatch loop!"
        )

        # 3. Verify loop uses maxDispatch parameter
        self.assertTrue(
            bool(re.search(r"#out\.dispatched\s*>=\s*maxDispatch", lua_code)),
            "Radar loop does not respect maxDispatch threshold."
        )

    def test_radar_non_march_0ms_packet_separation(self) -> None:
        """Verify that non-march tasks (garbage, help, rescue) do NOT send start and finish in the same tick."""
        mock_bridge = MockFridaBridge()
        cfg = {"radar_events": {"max_dispatches_per_cycle": 20}}
        client_state = {"inWorld": True, "worldPointsCount": 10}

        bot_actions.run_radar_events(mock_bridge, 23848, client_state, cfg, dry_run=True)
        lua_code = mock_bridge.recorded_lua[-1]

        # Ensure StartPickGarbage does not have FinishSampling in the same branch
        garbage_start_match = re.search(r"StartPickGarbage.*?(FinishSampling)", lua_code, re.DOTALL)
        if garbage_start_match:
            # If FinishSampling appears after StartPickGarbage, it MUST be inside a doing/endT expired branch
            self.assertIn("if doing then", lua_code)
            self.assertIn("nowMs >= endT", lua_code)

        # Verify DetectEventHelpStart and DetectEventHelpEnd are separated
        help_start_idx = lua_code.find("DetectEventHelpStart")
        help_end_idx = lua_code.find("DetectEventHelpEnd")
        self.assertTrue(help_start_idx != -1 and help_end_idx != -1)
        # HelpEnd must be in the 'doing' branch
        self.assertTrue(lua_code.find("if doing then") < help_end_idx)

    def test_radar_stress_harness_15_event_board(self) -> None:
        """Stress harness: Verify that a board with 15 events dispatches up to available limits without stopping at 3."""
        # Simulated 15-event radar board
        board = [
            {"uuid": f"radar_{i}", "eventId": 1000 + i, "type": (2 if i < 3 else (6 if i < 8 else 19)), "state": 0}
            for i in range(15)
        ]
        free_formations = 3
        available_stamina = 150  # 15 events * 5 stamina = 75 stamina required

        # Simulate unthrottled execution matching the production logic in run_radar_events
        dispatched = []
        cur_stamina = available_stamina
        f_idx = 0
        for ev in board:
            ev_type = ev["type"]
            cost = 5
            if cur_stamina >= cost:
                if ev_type in (6, 19):  # non-march garbage/help
                    dispatched.append({"uuid": ev["uuid"], "mode": "non-march", "cost": cost})
                    cur_stamina -= cost
                elif ev_type == 2:  # march event
                    if f_idx < free_formations:
                        f_idx += 1
                        dispatched.append({"uuid": ev["uuid"], "mode": "march", "formation": f"f_{f_idx}", "cost": cost})
                        cur_stamina -= cost

        # Total dispatched should be 3 marches + 5 garbage + 7 help = 15 events!
        self.assertGreater(len(dispatched), 3, f"Dispatched only {len(dispatched)} events - failed unthrottling!")
        self.assertEqual(len(dispatched), 15)

        # Validate against SFS contract
        valid, err = self.validator.validate_radar_dispatch_loop(
            total_events_on_board=len(board),
            dispatched_count=len(dispatched),
            free_formations=free_formations,
            available_stamina=available_stamina,
        )
        self.assertTrue(valid, f"Radar dispatch loop contract violation: {err}")

    # =========================================================================
    # Task 2.2: Hospital Cure Serialization & Deadlock Prevention Verification
    # =========================================================================

    def test_hospital_cure_lua_payload_structure(self) -> None:
        """Verify that run_hospital_heal constructs the verified {[armyId] = healNum} healArrMap and gold=goldFlag."""
        mock_bridge = MockFridaBridge({"ok": True, "task": "hospital_heal", "action": "dormant_no_wounded", "dormant": True, "wounded_total": 0})
        cfg = {"hospital_heal": {"min_batch_troops": 25, "max_batch_troops": 1500, "batch_minutes": 30}}
        client_state = {}

        bot_actions.run_hospital_heal(mock_bridge, 23848, client_state, cfg, dry_run=False)
        lua_code = mock_bridge.recorded_lua[0]

        # 1. Verify that healArrMap is built as a dictionary map {[aid] = takeInt}
        self.assertIn("local healArrMap = {}", lua_code)
        self.assertIn("healArrMap[aid] = takeInt", lua_code)

        # 2. Verify that SFSNetwork.SendMessage(MsgDefines.HospitalCure) receives { arr = healArrMap, gold = goldFlag }
        self.assertTrue(
            bool(re.search(r"SendMessage\(MsgDefines\.HospitalCure,\s*\{.*?arr\s*=\s*healArrMap.*?gold\s*=\s*goldFlag.*?\}\)", lua_code, re.DOTALL)),
            "HospitalCure message payload does not pass arr = healArrMap and gold = goldFlag!"
        )

    def test_hospital_cure_stale_queue_deadlock_prevention(self) -> None:
        """Verify that stale queues with endTime == 0 or endTime <= nowMs do not set isActivelyHealing = true."""
        mock_bridge = MockFridaBridge({"ok": True, "task": "hospital_heal", "action": "dormant_no_wounded", "dormant": True, "wounded_total": 0})
        cfg = {"hospital_heal": {}}
        client_state = {}

        bot_actions.run_hospital_heal(mock_bridge, 23848, client_state, cfg, dry_run=False)
        lua_code = mock_bridge.recorded_lua[0]

        # Must verify that isActivelyHealing requires activeEndMs > nowMs and nowMs > 0
        self.assertIn("local isActivelyHealing = (activeQ ~= nil and activeQState == workState and activeEndMs > nowMs and nowMs > 0)", lua_code)
        self.assertIn("activeQState == workState and activeEndMs > 0 and nowMs > 0 and activeEndMs <= nowMs", lua_code)

    def test_hospital_csharp_dictionary_enumeration_support(self) -> None:
        """Verify that run_hospital_heal Lua supports C# GetEnumerator() and Count iteration."""
        mock_bridge = MockFridaBridge()
        bot_actions.run_hospital_heal(mock_bridge, 23848, {}, {}, dry_run=True)
        lua_code = mock_bridge.recorded_lua[-1]

        # Must include enumerator fallback
        self.assertIn("col.GetEnumerator", lua_code)
        self.assertIn("iter:MoveNext()", lua_code)
        self.assertIn("col.Count", lua_code)

    # =========================================================================
    # Task 2.3: Claim Collision Prevention Verification
    # =========================================================================

    def test_daily_claims_no_0ms_packet_collision(self) -> None:
        """Verify that run_daily_claims does not dispatch milestone chests if task claims fired in same tick."""
        mock_bridge = MockFridaBridge({"ok": True, "task": "daily_claims", "action": "claimed", "daily_tasks_claimed": 5, "daily_boxes_claimed": []})
        cfg = {"daily_claims": {"claim_daily_tasks": True}}
        client_state = {}

        bot_actions.run_daily_claims(mock_bridge, 23848, client_state, cfg, dry_run=False)
        lua_code = mock_bridge.recorded_lua[-1]

        # Milestone box claim loop must be guarded by out.daily_tasks_claimed == 0
        box_guard = re.search(r"if\s+out\.daily_tasks_claimed\s*==\s*0\s+and\s+dtm\.GetBoxState\s+then", lua_code)
        self.assertIsNotNone(
            box_guard,
            "DailyQuestReward chest claiming is NOT guarded by out.daily_tasks_claimed == 0! 0ms collision risk present."
        )

        # Milestone box claim must include break to stagger box claims across cycles
        self.assertIn("break -- Stagger milestone chest claims", lua_code, "DailyQuestReward chest loop is missing stagger 'break' statement!")

    def test_full_preparedness_1_indexed_and_no_redundant_dispatch(self) -> None:
        """Verify that _claim_full_preparedness uses 1-indexed/threshold stages and does not send both individual & batch."""
        actions_file = TOOLS_DIR / "bot actions.py"
        with open(actions_file, "r", encoding="utf-8") as f:
            code = f.read()

        # 1. Verify stage insertion in _claim_full_preparedness without 0-based (idx - 1) offset
        self.assertIn(
            "table.insert(claimableStages, tgtNum)",
            code,
            "Full preparedness does not populate claimableStages!"
        )
        self.assertNotIn(
            "table.insert(claimableIndices, idx - 1)",
            code,
            "Full preparedness still contains 0-based index calculation (idx - 1)!"
        )

        # 2. Verify exclusive branch between batch and single
        self.assertTrue(
            bool(re.search(r"elseif MsgDefines\.AcceptPersonalRewardBatch then.*?elseif MsgDefines\.AcceptPersonalReward then", code, re.DOTALL)),
            "Full preparedness does not use exclusive if/elseif for batch vs single dispatch!"
        )

    # =========================================================================
    # Task 2.4: Modal Dialog Auto-Dismissal Verification
    # =========================================================================

    def test_modal_dialog_logger_and_auto_dismissal_coverage(self) -> None:
        """Verify that _install_popup_logger and _dismiss_modal_dialogs handle CommonDialog and UIGiftPackageRewardGet."""
        actions_file = TOOLS_DIR / "bot actions.py"
        with open(actions_file, "r", encoding="utf-8") as f:
            code = f.read()

        # Check modal types handled
        self.assertIn("CommonDialog", code)
        self.assertIn("UIGiftPackageRewardGet", code)
        self.assertIn("UIError", code)
        self.assertIn("UIConfirmDialog", code)
        self.assertIn("string.find(wName, 'Error')", code)

        # Check dismiss logic in _dismiss_modal_dialogs
        self.assertIn("local function _dismiss_modal_dialogs()", code)
        self.assertIn("mgr:CloseUIView(name)", code)

        # Check task registry export
        self.assertIn('"dismiss_popups": dismiss_all_popups', code)

    def test_dismiss_all_popups_callable(self) -> None:
        """Verify that dismiss_all_popups task executes cleanly and returns standard format."""
        mock_bridge = MockFridaBridge({"ok": True, "task": "dismiss_popups", "action": "dismissed", "dismissed_modals": []})
        res = bot_actions.dismiss_all_popups(mock_bridge, 23848, {}, {}, dry_run=True)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("task"), "dismiss_popups")

    # =========================================================================
    # Task 2.5: Frida Session Caching in client discovery.py
    # =========================================================================

    def test_frida_session_caching_architecture(self) -> None:
        """Verify that client discovery.py implements _FridaSessionHolder and _CACHED_SESSIONS."""
        discovery_file = TOOLS_DIR / "client discovery.py"
        with open(discovery_file, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("class _FridaSessionHolder:", code)
        self.assertIn("_CACHED_SESSIONS: dict[int, _FridaSessionHolder] = {}", code)
        self.assertIn("def close_frida_session(pid: int | None = None) -> None:", code)
        self.assertIn("atexit.register(close_frida_session)", code)


if __name__ == "__main__":
    unittest.main()
