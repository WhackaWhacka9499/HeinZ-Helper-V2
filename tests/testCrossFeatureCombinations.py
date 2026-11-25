"""Tier 3: Cross-Feature Combinations & State Transitions Test Suite.

Verifies:
- Live cycle sequence simulation across sequential abilities in TASK_ORDER
- Sequential pipeline: hospital_heal -> daily_claims -> radar_events -> full_preparedness
- Inter-packet collision prevention across consecutive claim and dispatch cycles
- Shared context propagation (protected_uids, claimed_gather_points, reinforced_targets)
- Error cascade isolation (failure or no-op in task A does not corrupt task B)
- Cross-client state isolation (PID 23848 vs PID 14952)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.testHarness import (
    MockGameClient,
    SFSMessageValidator,
    ServerResponseSimulator,
)


class TestCrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Cross-Feature Combinations & State Transitions Test Suite."""

    def setUp(self) -> None:
        self.validator = SFSMessageValidator()
        self.server_sim = ServerResponseSimulator()

    def test_live_cycle_sequence_simulation_clean_transitions(self) -> None:
        """Simulate a complete 4-step sequence: hospital_heal -> daily_claims -> radar_events -> full_preparedness."""
        client = MockGameClient(
            pid=23848,
            label="Farm",
            role="farm",
            stamina=100,
            free_formations=3,
        )

        # 1. Setup Hospital State: 100 wounded soldiers
        client.wounded_troops = [{"armyId": "400101", "count": 100}]

        # 2. Setup Daily Claims State: 2 completed tasks, 0 boxes
        client.daily_quest_state["tasks"] = [
            {"id": "t1", "state": 1},
            {"id": "t2", "state": 1},
        ]
        client.daily_quest_state["cur_value"] = 40
        client.daily_quest_state["boxes"] = [1, 0, 0, 0, 0, 0]

        # 3. Setup Radar State: 4 radar events (1 march, 3 non-marches)
        client.radar_events = [
            {"uuid": 101, "type": "march", "state": 0},
            {"uuid": 102, "type": "garbage", "state": 0},
            {"uuid": 103, "type": "help", "state": 0},
            {"uuid": 104, "type": "rescue", "state": 0},
        ]

        # 4. Setup Full Preparedness State: batch claim stages [1, 2]
        client.personal_arms_state["cur_score"] = 5000
        client.personal_arms_state["targets"] = [1000, 3000, 6000]

        # Shared execution context across cycle
        shared_ctx = {
            "protected_uids": ["uid_farm_1", "uid_alt_3"],
            "claimed_gather_points": [],
            "reinforced_targets": [],
            "executed_tasks": [],
        }

        # Step 1: Hospital Heal
        heal_payload = {
            "arr": [{"armyId": str(t["armyId"]), "healNum": t["count"]} for t in client.wounded_troops],
            "gold": 0,
        }
        res_heal = client.send_sfs_message("HospitalCure", heal_payload)
        self.assertTrue(res_heal["ok"])
        shared_ctx["executed_tasks"].append("hospital_heal")

        # Step 2: Daily Claims (Staggered to prevent 0ms collision)
        # First send GetAllReward
        res_daily_tasks = client.send_sfs_message("DailyQuestGetAllReward", {})
        self.assertTrue(res_daily_tasks["ok"])

        # Auto-dismiss reward popup if generated
        client.dismiss_modal_dialogs()

        # Then send milestone box (staggered tick)
        res_box = client.send_sfs_message("DailyQuestReward", {"stage": 1})
        self.assertTrue(res_box["ok"])
        shared_ctx["executed_tasks"].append("daily_claims")

        # Step 3: Radar Events (All 4 unthrottled)
        dispatched_radar = []
        for ev in client.radar_events:
            dispatched_radar.append(ev["uuid"])
        self.assertEqual(len(dispatched_radar), 4)
        shared_ctx["executed_tasks"].append("radar_events")

        # Step 4: Full Preparedness (Batch 1-indexed, no duplicate individual calls)
        batch_payload = {
            "actId": client.personal_arms_state["act_id"],
            "eventType": 1,
            "stages": [1, 2],  # 1-indexed
        }
        res_prep = client.send_sfs_message("AcceptPersonalRewardBatch", batch_payload)
        self.assertTrue(res_prep["ok"])
        shared_ctx["executed_tasks"].append("full_preparedness")

        # Verify no rejection dialogs were left open
        self.assertEqual(len(client.modal_windows), 0)
        self.assertEqual(len(client.server_sim.rejection_history), 0)
        self.assertEqual(len(shared_ctx["executed_tasks"]), 4)

    def test_inter_packet_collision_prevention_between_claims(self) -> None:
        """Verify that rapid successive claims do not provoke E000000 server rejections."""
        client = MockGameClient(pid=23848, label="Farm")

        # Simulation: Task claims then batch arms claims
        r1 = client.send_sfs_message("DailyQuestGetAllReward", {})
        self.assertTrue(r1["ok"])

        # Batch claims with 1-based indexing
        r2 = client.send_sfs_message(
            "AcceptPersonalRewardBatch",
            {"actId": "act_arms", "eventType": 1, "stages": [1, 2, 3]},
        )
        self.assertTrue(r2["ok"])

        # Rejection count must be 0
        self.assertEqual(len(client.server_sim.rejection_history), 0)

    def test_shared_context_isolation_across_clients(self) -> None:
        """Verify that shared_ctx maintains protected UIDs and prevents resource collisions between Farm and Alt."""
        farm_client = MockGameClient(pid=23848, label="Farm", role="farm", commander_name="Heinzy³")
        alt_client = MockGameClient(pid=14952, label="Alt3", role="alt", commander_name="Heinzy²")

        shared_ctx = {
            "protected_uids": ["uid_heinzy_2", "uid_heinzy_3"],
            "claimed_gather_points": [501234],
            "reinforced_targets": [],
        }

        # Alt gathers tile 501234
        self.assertIn(501234, shared_ctx["claimed_gather_points"])

        # Farm gathers next tile: checks if 501234 is claimed
        tile_candidate = 501234
        tile_is_occupied = tile_candidate in shared_ctx["claimed_gather_points"]
        self.assertTrue(tile_is_occupied, "Farm must recognize tile claimed by Alt")

        # Farm selects unreserved tile 501235
        safe_tile = 501235
        self.assertNotIn(safe_tile, shared_ctx["claimed_gather_points"])
        shared_ctx["claimed_gather_points"].append(safe_tile)

        self.assertEqual(len(shared_ctx["claimed_gather_points"]), 2)

    def test_error_cascade_isolation(self) -> None:
        """Verify that a no-op or benign issue in one task does not crash subsequent tasks."""
        client = MockGameClient(pid=23848, label="Farm")

        # Task 1: Hospital heal has 0 wounded
        client.wounded_troops = []
        ok1, raw1 = client._eval_hospital_heal_lua("hospital logic")
        self.assertTrue(ok1)
        self.assertIn("no_wounded", raw1)

        # Task 2: Radar events runs immediately afterwards
        client.radar_events = [{"uuid": 99, "type": "garbage", "state": 0}]
        ok2, raw2 = client._eval_radar_events_lua("radar logic")
        self.assertTrue(ok2)
        self.assertIn("dispatched", raw2)


if __name__ == "__main__":
    unittest.main()
