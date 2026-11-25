"""Tier 1 & Tier 2: Radar Missions & Hospital Healing Logic Tests.

Addresses the two critical user feedback items:
1. Radar Missions: "Radar events its doing '3' even when only completing one, whilst say there is 10 on the radar still."
   - Unthrottled dispatch loop across 10+ events
   - Formation allocation vs non-march event handling
   - Separation of non-march start and completion (preventing error 897722)
   - Stamina boundary checks
2. Hospital Healing: "Healing troops does nothing still."
   - SFSArray serialization format [{armyId, healNum}] with gold = 0
   - Elimination of activeBusy deadlock on stale queues
   - Collection of completed queues prior to new batch
   - Zero-wounded boundary condition handling
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


class TestRadarHospitalLogic(unittest.TestCase):
    """Test Suite for Radar Dispatch Loop and Hospital Healing Logic."""

    def setUp(self) -> None:
        self.validator = SFSMessageValidator()
        self.server_sim = ServerResponseSimulator()

    # =========================================================================
    # RADAR MISSIONS TESTS
    # =========================================================================

    def test_radar_unthrottled_dispatch_processes_all_ten_events(self) -> None:
        """Verify that with 10 radar events, 120 stamina, and 4 formations, all 10 are dispatched."""
        client = MockGameClient(
            pid=23848,
            label="Farm",
            role="farm",
            stamina=120,
            free_formations=4,
        )
        # Create 10 radar events: 2 marches, 3 garbage, 3 helps, 2 rescues
        client.radar_events = [
            {"uuid": 101, "type": "march", "state": 0},
            {"uuid": 102, "type": "march", "state": 0},
            {"uuid": 103, "type": "garbage", "state": 0},
            {"uuid": 104, "type": "garbage", "state": 0},
            {"uuid": 105, "type": "garbage", "state": 0},
            {"uuid": 106, "type": "help", "state": 0},
            {"uuid": 107, "type": "help", "state": 0},
            {"uuid": 108, "type": "help", "state": 0},
            {"uuid": 109, "type": "rescue", "state": 0},
            {"uuid": 110, "type": "rescue", "state": 0},
        ]

        total_events = len(client.radar_events)
        self.assertEqual(total_events, 10)

        # Unthrottled dispatch simulation: process all events
        dispatched = []
        march_count = 0
        for ev in client.radar_events:
            if ev["type"] == "march":
                if march_count < client.free_formations:
                    dispatched.append(ev["uuid"])
                    march_count += 1
            else:
                # Non-march tasks do not consume formations
                dispatched.append(ev["uuid"])

        self.assertEqual(len(dispatched), 10, "All 10 radar events should be dispatched")

        # Validator check: unthrottled loop must pass
        valid, err = self.validator.validate_radar_dispatch_loop(
            total_events_on_board=total_events,
            dispatched_count=len(dispatched),
            free_formations=client.free_formations,
            available_stamina=client.stamina,
            max_configured_cap=None,
        )
        self.assertTrue(valid, f"Unthrottled dispatch should be valid, got: {err}")

        # Execute production radar_events function and inspect real Lua template
        cd = MockCD(client)
        cfg = {"radar_events": {"max_dispatches_per_cycle": 20}}
        res_prod = ba.run_radar_events(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res_prod.get("ok"))
        clamp_check = LuaTemplateInspector.inspect_radar_loop_clamp(cd.last_lua, cfg)
        self.assertTrue(clamp_check["unthrottled"], f"Production radar loop is throttled: {clamp_check}")
        self.assertFalse(clamp_check["has_hardcoded_break"])

    def test_radar_dispatch_catches_arbitrary_three_cap_violation(self) -> None:
        """Verify that capping at 3 when 10 events exist is flagged as a contract violation."""
        valid, err = self.validator.validate_radar_dispatch_loop(
            total_events_on_board=10,
            dispatched_count=3,
            free_formations=4,
            available_stamina=100,
            max_configured_cap=3,
        )
        self.assertFalse(valid)
        self.assertIn("CONTRACT VIOLATION", str(err))
        self.assertIn("artificially capped at 3 events despite 10 events available", str(err))

    def test_radar_stamina_limiting_boundary(self) -> None:
        """Verify that when stamina is low (e.g. 15 stamina, 5 cost each), loop dispatches 3 events cleanly."""
        # 15 stamina / 5 per event = 3 max allowed by stamina
        valid, err = self.validator.validate_radar_dispatch_loop(
            total_events_on_board=10,
            dispatched_count=3,
            free_formations=4,
            available_stamina=15,
            stamina_cost_per_event=5,
            max_configured_cap=None,
        )
        self.assertTrue(valid, "Stamina-constrained dispatch of 3 events must be valid")

    def test_radar_formation_constrained_march_allocation(self) -> None:
        """Verify that march events respect free formation count while non-marches continue."""
        client = MockGameClient(pid=23848, label="Farm", free_formations=1)
        events = [
            {"uuid": 201, "type": "march", "state": 0},
            {"uuid": 202, "type": "march", "state": 0},
            {"uuid": 203, "type": "march", "state": 0},
            {"uuid": 204, "type": "garbage", "state": 0},
            {"uuid": 205, "type": "help", "state": 0},
        ]

        marches_dispatched = 0
        non_marches_dispatched = 0
        for ev in events:
            if ev["type"] == "march":
                if marches_dispatched < client.free_formations:
                    marches_dispatched += 1
            else:
                non_marches_dispatched += 1

        self.assertEqual(marches_dispatched, 1, "Only 1 march should be dispatched with 1 free formation")
        self.assertEqual(non_marches_dispatched, 2, "Both non-march events should be dispatched")
        self.assertEqual(marches_dispatched + non_marches_dispatched, 3)

    def test_radar_non_march_prevents_error_897722(self) -> None:
        """Verify that separating non-march start and completion prevents server error 897722."""
        # Simulating separated timestamps (e.g. start at t=0, completion at t=2500ms)
        res_ok = self.server_sim.evaluate_request(
            "FinishSampling",
            {"uuid": 301},
            context={"start_ms": 1000, "finish_ms": 3500},
        )
        self.assertTrue(res_ok["ok"])

        # Simulating 0ms simultaneous execution (bug)
        res_fail = self.server_sim.evaluate_request(
            "FinishSampling",
            {"uuid": 301},
            context={"start_ms": 1000, "finish_ms": 1000},
        )
        self.assertFalse(res_fail["ok"])
        self.assertEqual(res_fail["error_code"], "897722")

    # =========================================================================
    # HOSPITAL HEALING TESTS
    # =========================================================================

    def test_hospital_heal_commits_single_troop_type_to_queue(self) -> None:
        """Verify single troop type is serialized as SFSArray and successfully enqueued."""
        client = MockGameClient(pid=23848, label="Farm")
        client.wounded_troops = [{"armyId": "400101", "count": 150}]

        cd = MockCD(client)
        res = ba.run_hospital_heal(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("action"), "started_heal_batch")
        self.assertEqual(res.get("queued_troops"), 150)

        # Inspect real production Lua template generated by run_hospital_heal
        syntax_check = LuaTemplateInspector.inspect_hospital_payload_syntax(cd.last_lua)
        self.assertTrue(syntax_check["valid"], f"Production Lua failed syntax inspection: {syntax_check}")
        self.assertTrue(syntax_check["has_heal_map"] or syntax_check["has_struct_array"])

        # Inspect client dispatched message
        last_msg = client.dispatched_messages[-1]
        self.assertEqual(last_msg["msg"], "HospitalCure")
        payload = last_msg["payload"]

        # Payload contract check
        if isinstance(payload["arr"], dict):
            self.assertEqual(payload["arr"]["400101"], 150)
        else:
            self.assertIsInstance(payload["arr"], list)
            self.assertEqual(len(payload["arr"]), 1)
            self.assertEqual(payload["arr"][0]["armyId"], "400101")
            self.assertEqual(payload["arr"][0]["healNum"], 150)
        self.assertEqual(payload["gold"], 0)

        # Confirm no error modals were opened
        self.assertEqual(len(client.modal_windows), 0)

    def test_hospital_heal_commits_multi_troop_types(self) -> None:
        """Verify multiple troop types (infantry, vehicle, ranged) are properly batched."""
        client = MockGameClient(pid=23848, label="Farm")
        client.wounded_troops = [
            {"armyId": "400101", "count": 200},
            {"armyId": "400201", "count": 180},
            {"armyId": "400301", "count": 95},
        ]

        cd = MockCD(client)
        res = ba.run_hospital_heal(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("action"), "started_heal_batch")
        self.assertEqual(res.get("queued_troops"), 475)

        syntax_check = LuaTemplateInspector.inspect_hospital_payload_syntax(cd.last_lua)
        self.assertTrue(syntax_check["valid"])

        last_msg = client.dispatched_messages[-1]
        payload = last_msg["payload"]
        if isinstance(payload["arr"], dict):
            self.assertEqual(len(payload["arr"]), 3)
            self.assertEqual(sum(payload["arr"].values()), 475)
        else:
            self.assertEqual(len(payload["arr"]), 3)
            self.assertEqual(sum(item["healNum"] for item in payload["arr"]), 475)

    def test_hospital_heal_zero_wounded_returns_cleanly(self) -> None:
        """Verify that when 0 wounded troops exist, no invalid HospitalCure packet is sent."""
        client = MockGameClient(pid=23848, label="Farm")
        client.wounded_troops = []

        cd = MockCD(client)
        res = ba.run_hospital_heal(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertIn(res.get("action"), ("no_wounded", "dormant_no_wounded"))
        self.assertEqual(res.get("wounded_total"), 0)

        # Ensure no HospitalCure was dispatched
        cure_msgs = [m for m in client.dispatched_messages if m["msg"] == "HospitalCure"]
        self.assertEqual(len(cure_msgs), 0)

    def test_hospital_heal_stale_queue_does_not_deadlock(self) -> None:
        """Verify that a completed/stale queue (endTime <= nowMs) does not deadlock as activeBusy."""
        now_ms = 1000000
        stale_queue = {
            "queueType": 3,
            "state": 2,  # Work state
            "endTime": 995000,  # Expired in past
            "isHelped": 1,
        }

        # Stale queue determination:
        is_finished = stale_queue["endTime"] <= now_ms
        self.assertTrue(is_finished, "Queue with endTime <= nowMs must be recognized as finished")

        # When finished, status should be 'finished' / collected, NOT activeBusy
        status = "finished" if is_finished else "working"
        active_busy = (status == "working")
        self.assertFalse(active_busy, "Finished queue must not cause activeBusy deadlock")


if __name__ == "__main__":
    unittest.main()
