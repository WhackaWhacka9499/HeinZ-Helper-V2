"""Tier 4: Real-World Application Scenarios Test Suite.

Simulates real-world client cycles:
1. Replicating the 15:44:18 live incident on FarmGame.exe (PID 23848, State #694):
   - Command Hub 'Running Live Cycle (target=all)'
   - Prevention of E000000 server rejection over 'Congratulations!' reward modal
   - Unthrottled radar processing across 10 radar events
   - Successful hospital cure queue commitment with SFSArray payload
   - Auto-dismissal of modal dialogs preventing client freeze
2. Replicating Alt3Game.exe (PID 14952, Player Heinzy², HQ 27, Power ~93.7M):
   - High-level alt account execution
   - Hero Battlefield gear protection preventing E000000 / E100172
   - Auto-gather formation locking safeguards (120816 / 120288)
3. Server Error Code Matrix:
   - Diagnostic validation of all historical LastZ error codes (E000000, 897722, 120816, 120288, 5560006, E100172)
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ba = importlib.import_module("tools.bot actions")

from tests.testHarness import (
    LuaTemplateInspector,
    MockCD,
    MockGameClient,
    SFSMessageValidator,
    ServerResponseSimulator,
)


class TestRealWorldScenarios(unittest.TestCase):
    """Tier 4: Real-World Application Scenarios Test Suite."""

    def setUp(self) -> None:
        self.validator = SFSMessageValidator()
        self.server_sim = ServerResponseSimulator()

    def test_replicate_154418_farm_game_incident_clean_execution(self) -> None:
        """Replicate the 15:44:18 live run on FarmGame.exe (PID 23848) with all bugfixes active.

        Verifies that:
        1. DailyQuestGetAllReward and DailyQuestReward do not trigger E000000.
        2. 'Congratulations!' reward modal is auto-dismissed.
        3. All 10 radar events are processed without the 3-event cap.
        4. Hospital healing enqueues troops with SFSArray format.
        5. Zero server rejection dialogs remain open.
        """
        farm_client = MockGameClient(
            pid=23848,
            label="Farm",
            role="farm",
            commander_name="Heinzy³",
            server_id=694,
            hq_level=25,
            stamina=120,
            free_formations=3,
        )

        # 1. State setup matching 15:44:18 incident
        farm_client.daily_quest_state["tasks"] = [
            {"id": "task_build", "state": 1},
            {"id": "task_gather", "state": 1},
            {"id": "task_recruit", "state": 1},
        ]
        farm_client.daily_quest_state["cur_value"] = 60
        farm_client.daily_quest_state["boxes"] = [1, 1, 0, 0, 0, 0]  # Boxes 1 and 2 claimable

        farm_client.wounded_troops = [
            {"armyId": "400101", "count": 250},
            {"armyId": "400201", "count": 120},
        ]

        farm_client.radar_events = [
            {"uuid": 1001, "type": "march", "state": 0},
            {"uuid": 1002, "type": "march", "state": 0},
            {"uuid": 1003, "type": "garbage", "state": 0},
            {"uuid": 1004, "type": "garbage", "state": 0},
            {"uuid": 1005, "type": "garbage", "state": 0},
            {"uuid": 1006, "type": "help", "state": 0},
            {"uuid": 1007, "type": "help", "state": 0},
            {"uuid": 1008, "type": "help", "state": 0},
            {"uuid": 1009, "type": "rescue", "state": 0},
            {"uuid": 1010, "type": "rescue", "state": 0},
        ]

        cd = MockCD(farm_client)

        # Execution Step A: Hospital Healing (Genuine production execution)
        res_heal = ba.run_hospital_heal(cd, farm_client.pid, {}, {}, dry_run=False)
        self.assertTrue(res_heal.get("ok"), "Hospital cure should succeed with SFSArray format")
        self.assertEqual(res_heal.get("action"), "started_heal_batch")
        self.assertEqual(res_heal.get("queued_troops"), 370)

        # Inspect client dispatched message
        last_msg = farm_client.dispatched_messages[-1]
        self.assertEqual(last_msg["msg"], "HospitalCure")
        payload_arr = last_msg["payload"]["arr"]
        self.assertTrue(isinstance(payload_arr, (list, dict)))
        self.assertEqual(len(payload_arr), 2)
        self.assertEqual(last_msg["payload"]["gold"], 0)

        # Execution Step B: Daily Quest Tasks Claim (Genuine production execution)
        res_claims = ba.run_daily_claims(cd, farm_client.pid, {}, {}, dry_run=False)
        self.assertTrue(res_claims.get("ok"))
        self.assertEqual(res_claims.get("daily_tasks_claimed"), 3)

        # In-game event: reward screen triggers 'Congratulations!' popup
        reward_dlg = farm_client.open_modal_dialog(
            dialog_type="UIGiftPackageRewardGet",
            title="Congratulations!",
            message="Z-Coins, Wood, Meat, EXP",
        )
        self.assertEqual(len(farm_client.modal_windows), 1)

        # Auto-dismiss hook dismisses the reward modal via production dismiss_all_popups
        res_dismiss = ba.dismiss_all_popups(cd, farm_client.pid, {}, {}, dry_run=False)
        self.assertTrue(res_dismiss.get("ok"))
        self.assertEqual(res_dismiss.get("dismissed_count"), 1)
        self.assertEqual(len(farm_client.modal_windows), 0)

        # Execution Step C: Full Preparedness Claim (Genuine production execution)
        res_prep = ba.run_treasure_helicopter(cd, farm_client.pid, {}, {}, dry_run=False)
        self.assertTrue(res_prep.get("ok"))

        # Execution Step D: Radar Events Unthrottled Dispatch (Genuine production execution)
        cfg_radar = {"radar_events": {"max_dispatches_per_cycle": 20}}
        res_radar = ba.run_radar_events(cd, farm_client.pid, {}, cfg_radar, dry_run=False)
        self.assertTrue(res_radar.get("ok"))
        self.assertEqual(len(res_radar.get("dispatched") or []), 10, "All 10 radar events must be dispatched")

        # Confirm 0 server rejection records were generated
        self.assertEqual(len(farm_client.server_sim.rejection_history), 0)
        self.assertEqual(len(farm_client.modal_windows), 0)

    def test_replicate_alt3_game_client_cycle(self) -> None:
        """Replicate Alt3Game.exe (PID 14952) full cycle with high-power safeguards.

        Verifies:
        1. Formation gear is protected against unequip/reinstall conflicts.
        2. Auto-gather formation limit and tile occupancy checks succeed.
        3. Clean snapshot output.
        """
        alt_client = MockGameClient(
            pid=14952,
            label="Alt3Z",
            role="alt",
            commander_name="Heinzy²",
            server_id=694,
            hq_level=27,
            stamina=150,
            free_formations=4,
        )

        snap = alt_client.get_snapshot()
        self.assertTrue(snap["ok"])
        self.assertEqual(snap["pid"], 14952)
        self.assertEqual(snap["name"], "Heinzy²")
        self.assertEqual(snap["hqLv"], 27)
        self.assertEqual(snap["power"], 93700000)

        # Hero Battlefield Gear check: Formation 1 gear locked
        gear_item = {"id": 2001, "name": "Titanium Armor"}
        valid_gear, err_gear = self.validator.validate_hero_battlefield_gear(gear_item, formation_locked=True)
        self.assertFalse(valid_gear, "Locked gear must be protected against swap")

        # Auto-Gather check: tile free and 4 formations free
        valid_march, err_march = self.validator.validate_auto_gather_march(
            tile_occupied=False, formation_available=(alt_client.free_formations > 0)
        )
        self.assertTrue(valid_march)

        # Production execution on Alt client
        cd_alt = MockCD(alt_client)
        res_daily = ba.run_daily_claims(cd_alt, alt_client.pid, {}, {}, dry_run=False)
        self.assertTrue(res_daily.get("ok"))

        res_popups = ba.dismiss_all_popups(cd_alt, alt_client.pid, {}, {}, dry_run=False)
        self.assertTrue(res_popups.get("ok"))

    def test_server_error_code_matrix(self) -> None:
        """Verify diagnostic recognition and categorization of all LastZ server error codes."""
        error_matrix = {
            "E000000": "Sorry, an unknown error occurred. Please try again or leave us feedback.",
            "897722": "Assist dispatch mission invalid duration or completed too quickly.",
            "120816": "Formation already locked or marching.",
            "120288": "Tile already occupied or expired.",
            "5560006": "Invalid treasure dig UUID or resource unavailable.",
            "E100172": "Hero battle set target chapter failed - hero gear locked.",
        }

        sim = ServerResponseSimulator()
        for code, expected_desc in error_matrix.items():
            self.assertIn(code, sim.ERROR_CODES)
            self.assertEqual(sim.ERROR_CODES[code], expected_desc)


if __name__ == "__main__":
    unittest.main()
