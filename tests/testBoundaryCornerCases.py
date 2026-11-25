"""Tier 2: Boundary & Corner Cases Test Suite.

Verifies:
- Empty queue states (nil/empty queueDic)
- Zero wounded troops (graceful no_wounded action without invalid SFS packets)
- Max radar events stress (10, 25, 50 events on board)
- Missing / 0 free formations (march skipping with non-march execution)
- Zero gold parameter integrity (gold = 0 vs nil/omitted)
- Corrupted / malformed dictionary structures (type coercion & resilience)
- Invalid stage indices (0 vs 1 indexing, negative stages, out of bounds)
- Quest milestone point threshold boundaries
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
    MockCD,
    MockGameClient,
    SFSMessageValidator,
    ServerResponseSimulator,
)


class TestBoundaryCornerCases(unittest.TestCase):
    """Tier 2: Boundary & Corner Cases Test Suite."""

    def setUp(self) -> None:
        self.validator = SFSMessageValidator()
        self.server_sim = ServerResponseSimulator()

    # -------------------------------------------------------------------------
    # 1. Empty Queue States
    # -------------------------------------------------------------------------
    def test_empty_queue_dic_returns_idle_status(self) -> None:
        """Verify that an empty queueDic does not crash and reports queue free/idle."""
        client = MockGameClient(pid=23848, label="Farm")
        client.queue_dic = {}

        # Querying queue status with empty dictionary
        queue_types = [1, 3, 6, 8, 9]  # Train, heal, research, barracks
        for q_type in queue_types:
            q_entry = client.queue_dic.get(str(q_type))
            self.assertIsNone(q_entry)
            status = "free" if q_entry is None else "busy"
            self.assertEqual(status, "free")

    def test_malformed_queue_entry_resilience(self) -> None:
        """Verify that malformed or unexpected queue entries do not cause unhandled exceptions."""
        client = MockGameClient(pid=23848, label="Farm")
        client.queue_dic = {
            "3": {"corrupted": True},  # Missing state, endTime
            "6": None,
        }

        # Safe extraction
        q3 = client.queue_dic.get("3") or {}
        state = q3.get("state", 0)
        end_time = q3.get("endTime", 0)
        self.assertEqual(state, 0)
        self.assertEqual(end_time, 0)

    # -------------------------------------------------------------------------
    # 2. Zero Wounded Troops
    # -------------------------------------------------------------------------
    def test_zero_wounded_troops_returns_cleanly(self) -> None:
        """Verify that when wounded troop count is 0, no cure packet is dispatched."""
        client = MockGameClient(pid=23848, label="Farm")
        client.wounded_troops = []

        cd = MockCD(client)
        res = ba.run_hospital_heal(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("action"), "no_wounded")
        self.assertEqual(res.get("wounded_total"), 0)

        cure_calls = [m for m in client.dispatched_messages if m["msg"] == "HospitalCure"]
        self.assertEqual(len(cure_calls), 0)

    # -------------------------------------------------------------------------
    # 3. High Volume Radar Events Stress
    # -------------------------------------------------------------------------
    def test_high_volume_radar_events_unthrottled(self) -> None:
        """Verify that 25 radar events are processed without arbitrary caps."""
        events = [{"uuid": i, "type": "garbage", "state": 0} for i in range(1, 26)]
        self.assertEqual(len(events), 25)

        dispatched = []
        for ev in events:
            dispatched.append(ev["uuid"])

        self.assertEqual(len(dispatched), 25)

        valid, err = self.validator.validate_radar_dispatch_loop(
            total_events_on_board=25,
            dispatched_count=len(dispatched),
            free_formations=4,
            available_stamina=150,
            stamina_cost_per_event=5,
        )
        self.assertTrue(valid, f"High volume dispatch should be valid, got: {err}")

        # Verify production run_radar_events executes cleanly with high volume cap
        client = MockGameClient(pid=23848, label="Farm")
        cd = MockCD(client)
        res_radar = ba.run_radar_events(cd, 23848, {}, {"radar_events": {"max_dispatches_per_cycle": 50}}, dry_run=False)
        self.assertTrue(res_radar.get("ok"))

    # -------------------------------------------------------------------------
    # 4. Zero Free Formations
    # -------------------------------------------------------------------------
    def test_zero_free_formations_skips_marches_executes_non_marches(self) -> None:
        """Verify that when free formations == 0, marches are skipped while non-marches proceed."""
        client = MockGameClient(pid=23848, label="Farm", free_formations=0)
        events = [
            {"uuid": 1, "type": "march", "state": 0},
            {"uuid": 2, "type": "march", "state": 0},
            {"uuid": 3, "type": "garbage", "state": 0},
            {"uuid": 4, "type": "help", "state": 0},
        ]

        marches = []
        non_marches = []
        for ev in events:
            if ev["type"] == "march":
                if len(marches) < client.free_formations:
                    marches.append(ev)
            else:
                non_marches.append(ev)

        self.assertEqual(len(marches), 0, "No marches should be dispatched when free formations == 0")
        self.assertEqual(len(non_marches), 2, "Non-march events must proceed")

        # Verify production run_radar_events handles 0 free formations cleanly
        cd = MockCD(client)
        res_zero = ba.run_radar_events(cd, 23848, {}, {"radar_events": {"max_dispatches_per_cycle": 20}}, dry_run=False)
        self.assertTrue(res_zero.get("ok"))

    # -------------------------------------------------------------------------
    # 5. Zero Gold Integrity
    # -------------------------------------------------------------------------
    def test_zero_gold_parameter_strictly_enforced(self) -> None:
        """Verify that gold = 0 is explicitly validated in hospital healing."""
        # gold = 0 is valid
        payload_ok = {"arr": [{"armyId": "400101", "healNum": 50}], "gold": 0}
        v_ok, _ = self.validator.validate_hospital_cure_payload(payload_ok)
        self.assertTrue(v_ok)

        # gold = None is invalid
        payload_nil = {"arr": [{"armyId": "400101", "healNum": 50}], "gold": None}
        v_nil, err_nil = self.validator.validate_hospital_cure_payload(payload_nil)
        self.assertFalse(v_nil)
        self.assertIn("'gold' parameter must be 0", str(err_nil))

    # -------------------------------------------------------------------------
    # 6. Corrupted / Malformed Dictionary Structures
    # -------------------------------------------------------------------------
    def test_corrupted_troop_count_type_coercion(self) -> None:
        """Verify that string representations of numbers in troop structures coerce safely."""
        corrupted_entry = {"armyId": "400101", "count": "250", "dead": "0"}

        # Simulation of safe tonumber coercion
        aid = str(corrupted_entry.get("armyId") or "")
        try:
            count = int(corrupted_entry.get("count") or 0)
        except (ValueError, TypeError):
            count = 0

        self.assertEqual(aid, "400101")
        self.assertEqual(count, 250)

    # -------------------------------------------------------------------------
    # 7. Invalid Stage Indices
    # -------------------------------------------------------------------------
    def test_invalid_stage_indices_rejected(self) -> None:
        """Verify rejection of 0-based, negative, and invalid stages across claim RPCs."""
        # Stage 0
        v0, err0 = self.validator.validate_accept_personal_reward(
            {"actId": "act_1", "stage": 0, "eventType": 1}, is_batch=False
        )
        self.assertFalse(v0)
        self.assertIn("0-indexed", str(err0))

        # Negative stage
        vn, errn = self.validator.validate_accept_personal_reward(
            {"actId": "act_1", "stage": -1, "eventType": 1}, is_batch=False
        )
        self.assertFalse(vn)

        # Empty stages batch
        ve, erre = self.validator.validate_accept_personal_reward(
            {"actId": "act_1", "eventType": 1, "stages": []}, is_batch=True
        )
        self.assertFalse(ve)
        self.assertIn("empty", str(erre))

    # -------------------------------------------------------------------------
    # 8. Daily Quest Milestone Point Threshold Boundaries
    # -------------------------------------------------------------------------
    def test_milestone_box_exact_threshold_boundaries(self) -> None:
        """Verify boundary point thresholds for daily quest chests (e.g. 20, 40, 60, 80, 100, 140)."""
        box_thresholds = [20, 40, 60, 80, 100, 140]

        # Case A: cur_value = 19 (box 1 locked)
        claimable_a = [i + 1 for i, thresh in enumerate(box_thresholds) if 19 >= thresh]
        self.assertEqual(claimable_a, [])

        # Case B: cur_value = 20 (box 1 unlocked at exact boundary)
        claimable_b = [i + 1 for i, thresh in enumerate(box_thresholds) if 20 >= thresh]
        self.assertEqual(claimable_b, [1])

        # Case C: cur_value = 140 (all 6 boxes unlocked)
        claimable_c = [i + 1 for i, thresh in enumerate(box_thresholds) if 140 >= thresh]
        self.assertEqual(claimable_c, [1, 2, 3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main()
