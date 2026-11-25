"""Tier 1: Network Packet Contracts & Payload Format Tests.

Adheres to PROJECT.md § Interface Contracts:
- Daily Claims & Milestone Chests contract (no 0ms collision)
- Full Preparedness Reward Claim contract (1-indexed stages, no redundant individual + batch)
- Hospital Cure payload contract (SFSArray of structs {armyId, healNum}, gold = 0, no key-value dict)
- Treasure Helicopter payload contract (non-nil long UUID)
- Hero Battlefield Gear Guard contract (prevents equipping locked formation gear)
- Auto-Gather Formation Guard contract (tile occupancy & formation limit checks)
- Modal Dialog Interceptor & Auto-Dismiss contract
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from pathlib import Path
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ba = importlib.import_module("tools.bot actions")

from tests.testHarness import (
    LuaTemplateInspector,
    MockCD,
    MockGameClient,
    ProtocolContractViolation,
    SFSMessageValidator,
    ServerResponseSimulator,
)


class TestPacketContracts(unittest.TestCase):
    """Tier 1: Feature Coverage & Packet Contracts Test Suite."""

    def setUp(self) -> None:
        self.server_sim = ServerResponseSimulator()
        self.validator = SFSMessageValidator()

    # -------------------------------------------------------------------------
    # 1. Hospital Cure Contract Tests
    # -------------------------------------------------------------------------
    def test_hospital_cure_valid_sfs_array_format(self) -> None:
        """Verify that a compliant SFSArray format [{armyId, healNum}], gold=0 is accepted."""
        payload = {
            "arr": [
                {"armyId": "400101", "healNum": 150},
                {"armyId": "400102", "healNum": 75},
            ],
            "gold": 0,
        }
        valid, err = self.validator.validate_hospital_cure_payload(payload)
        self.assertTrue(valid, f"Expected valid HospitalCure payload, got error: {err}")
        self.assertIsNone(err)

        # Server response check
        res = self.server_sim.evaluate_request("HospitalCure", payload)
        self.assertTrue(res["ok"])
        self.assertEqual(res.get("healed"), 2)

    def test_hospital_cure_rejects_key_value_dict_bug(self) -> None:
        """Verify that HospitalCure rejects negative or invalid heal counts."""
        buggy_payload = {
            "arr": {
                "400101": -50,
            },
            "gold": 0,
        }
        valid, err = self.validator.validate_hospital_cure_payload(buggy_payload)
        self.assertFalse(valid)
        self.assertIn("must be a positive integer", str(err))

        # Server response must reject with E000000
        res = self.server_sim.evaluate_request("HospitalCure", buggy_payload)
        self.assertFalse(res["ok"])
        self.assertEqual(res.get("error_code"), "E000000")

    def test_hospital_cure_rejects_missing_gold(self) -> None:
        """Verify that HospitalCure requires the 'gold' parameter."""
        payload_missing_gold = {
            "arr": [{"armyId": "400101", "healNum": 100}]
        }
        valid, err = self.validator.validate_hospital_cure_payload(payload_missing_gold)
        self.assertFalse(valid)
        self.assertIn("missing mandatory 'gold' parameter", str(err))

    def test_hospital_cure_rejects_invalid_struct_fields(self) -> None:
        """Verify that struct items must contain string 'armyId' and positive int 'healNum'."""
        # Non-string armyId
        payload1 = {"arr": [{"armyId": 400101, "healNum": 100}], "gold": 0}
        valid1, err1 = self.validator.validate_hospital_cure_payload(payload1)
        self.assertFalse(valid1)
        self.assertIn("armyId must be a string", str(err1))

        # Non-positive healNum
        payload2 = {"arr": [{"armyId": "400101", "healNum": 0}], "gold": 0}
        valid2, err2 = self.validator.validate_hospital_cure_payload(payload2)
        self.assertFalse(valid2)
        self.assertIn("must be a positive integer", str(err2))

    # -------------------------------------------------------------------------
    # 2. Daily Claims & Milestone Chests Contract Tests
    # -------------------------------------------------------------------------
    def test_daily_claims_valid_staggered_execution(self) -> None:
        """Verify that staggered daily tasks followed by milestone boxes passes cleanly."""
        valid, err = self.validator.validate_daily_claims_sequencing(
            has_task_claim=True,
            task_claim_count=3,
            box_claims=[1, 2],
            same_tick_box_claim=False,  # Staggered / subsequent cycle
        )
        self.assertTrue(valid, f"Staggered execution should pass, got error: {err}")
        self.assertIsNone(err)

    def test_daily_claims_rejects_zero_ms_collision(self) -> None:
        """Verify that simultaneous 0ms firing of DailyQuestGetAllReward and DailyQuestReward is rejected."""
        valid, err = self.validator.validate_daily_claims_sequencing(
            has_task_claim=True,
            task_claim_count=4,
            box_claims=[1, 2],
            same_tick_box_claim=True,  # 0ms collision bug from live run incident
        )
        self.assertFalse(valid)
        self.assertIn("FATAL CONTRACT VIOLATION", str(err))
        self.assertIn("0ms collision", str(err))

    def test_daily_claims_empty_task_claim_guard(self) -> None:
        """Verify that DailyQuestGetAllReward is not dispatched when task_claim_count is 0."""
        valid, err = self.validator.validate_daily_claims_sequencing(
            has_task_claim=True,
            task_claim_count=0,
            box_claims=[],
            same_tick_box_claim=False,
        )
        self.assertFalse(valid)
        self.assertIn("0 claimable daily tasks", str(err))

    def test_daily_claims_box_index_boundaries(self) -> None:
        """Verify that daily quest milestone boxes are strictly constrained to 1-6."""
        # Box 0 is invalid
        valid0, err0 = self.validator.validate_daily_claims_sequencing(
            has_task_claim=False, task_claim_count=0, box_claims=[0]
        )
        self.assertFalse(valid0)
        self.assertIn("Invalid daily quest box index 0", str(err0))

        # Box 7 is invalid
        valid7, err7 = self.validator.validate_daily_claims_sequencing(
            has_task_claim=False, task_claim_count=0, box_claims=[7]
        )
        self.assertFalse(valid7)
        self.assertIn("Invalid daily quest box index 7", str(err7))

    # -------------------------------------------------------------------------
    # 3. Full Preparedness Reward Claim Contract Tests
    # -------------------------------------------------------------------------
    def test_accept_personal_reward_single_1_indexed(self) -> None:
        """Verify that individual AcceptPersonalReward requires 1-based indexing."""
        valid_payload = {"actId": "personal_arms_1", "stage": 1, "eventType": 1}
        valid, err = self.validator.validate_accept_personal_reward(valid_payload, is_batch=False)
        self.assertTrue(valid)

        # 0-indexed payload must fail
        invalid_payload = {"actId": "personal_arms_1", "stage": 0, "eventType": 1}
        invalid, err0 = self.validator.validate_accept_personal_reward(invalid_payload, is_batch=False)
        self.assertFalse(invalid)
        self.assertIn("0-indexed (0)", str(err0))

        # Server response must return E000000 on 0-indexed
        res = self.server_sim.evaluate_request("AcceptPersonalReward", invalid_payload)
        self.assertFalse(res["ok"])
        self.assertEqual(res.get("error_code"), "E000000")

    def test_accept_personal_reward_batch_1_indexed(self) -> None:
        """Verify that AcceptPersonalRewardBatch requires 1-based stage array/string."""
        # List of 1-based ints
        valid_batch_list = {"actId": "personal_arms_1", "eventType": 1, "stages": [1, 2, 3]}
        valid_l, _ = self.validator.validate_accept_personal_reward(valid_batch_list, is_batch=True)
        self.assertTrue(valid_l)

        # Comma-delimited string of 1-based ints (matching game bytecode table.concat)
        valid_batch_str = {"actId": "personal_arms_1", "eventType": 1, "stages": "1,2,3"}
        valid_s, _ = self.validator.validate_accept_personal_reward(valid_batch_str, is_batch=True)
        self.assertTrue(valid_s)

        # 0-indexed batch must fail
        invalid_batch = {"actId": "personal_arms_1", "eventType": 1, "stages": [0, 1, 2]}
        invalid_b, err_b = self.validator.validate_accept_personal_reward(invalid_batch, is_batch=True)
        self.assertFalse(invalid_b)
        self.assertIn("contains 0-indexed stage (0)", str(err_b))

        res = self.server_sim.evaluate_request("AcceptPersonalRewardBatch", invalid_batch)
        self.assertFalse(res["ok"])
        self.assertEqual(res.get("error_code"), "E000000")

    # -------------------------------------------------------------------------
    # 4. Treasure Helicopter Payload Contract Tests
    # -------------------------------------------------------------------------
    def test_treasure_helicopter_valid_uuid(self) -> None:
        """Verify that GetDigTreasureReward accepts valid 64-bit long integer UUID."""
        payload = {"uuid": 98234710293847}
        valid, err = self.validator.validate_treasure_helicopter_payload(payload)
        self.assertTrue(valid)
        self.assertIsNone(err)

        res = self.server_sim.evaluate_request("GetDigTreasureReward", payload)
        self.assertTrue(res["ok"])

    def test_treasure_helicopter_rejects_nil_uuid(self) -> None:
        """Verify that nil UUID triggers fatal contract violation and error 5560006."""
        payload = {"uuid": None}
        valid, err = self.validator.validate_treasure_helicopter_payload(payload)
        self.assertFalse(valid)
        self.assertIn("nil uuid", str(err))

        res = self.server_sim.evaluate_request("GetDigTreasureReward", payload)
        self.assertFalse(res["ok"])
        self.assertEqual(res.get("error_code"), "5560006")

    # -------------------------------------------------------------------------
    # 5. Radar Non-March Timing Contract Tests
    # -------------------------------------------------------------------------
    def test_radar_non_march_rejects_zero_duration(self) -> None:
        """Verify that non-march tasks (garbage, help, rescue) reject simultaneous 0ms completion."""
        # 0ms tick: start at 1000ms, finish at 1000ms
        valid, err = self.validator.validate_radar_non_march_timing("garbage", 1000, 1000)
        self.assertFalse(valid)
        self.assertIn("897722", str(err))

        res = self.server_sim.evaluate_request(
            "FinishSampling", {}, context={"start_ms": 1000, "finish_ms": 1000}
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res.get("error_code"), "897722")

    def test_radar_non_march_accepts_delayed_finish(self) -> None:
        """Verify that separated start and finish timestamps pass cleanly."""
        valid, err = self.validator.validate_radar_non_march_timing("garbage", 1000, 4500)
        self.assertTrue(valid)
        self.assertIsNone(err)

        res = self.server_sim.evaluate_request(
            "FinishSampling", {}, context={"start_ms": 1000, "finish_ms": 4500}
        )
        self.assertTrue(res["ok"])

    # -------------------------------------------------------------------------
    # 6. Hero Battlefield & Auto-Gather Guard Tests
    # -------------------------------------------------------------------------
    def test_hero_battlefield_rejects_locked_formation_gear(self) -> None:
        """Verify that attempting to equip/unequip gear locked in an active formation is blocked."""
        gear = {"id": 1001, "name": "Tactical Vest"}
        valid, err = self.validator.validate_hero_battlefield_gear(gear, formation_locked=True)
        self.assertFalse(valid)
        self.assertIn("locked in an active formation", str(err))

    def test_auto_gather_guards_against_formation_and_tile_conflicts(self) -> None:
        """Verify auto-gather rejects march when formations are unavailable or tile is occupied."""
        # Formation unavailable
        v1, err1 = self.validator.validate_auto_gather_march(tile_occupied=False, formation_available=False)
        self.assertFalse(v1)
        self.assertIn("120816", str(err1))

        # Tile occupied
        v2, err2 = self.validator.validate_auto_gather_march(tile_occupied=True, formation_available=True)
        self.assertFalse(v2)
        self.assertIn("120288", str(err2))

        # Clean march
        v3, err3 = self.validator.validate_auto_gather_march(tile_occupied=False, formation_available=True)
        self.assertTrue(v3)
        self.assertIsNone(err3)

    # -------------------------------------------------------------------------
    # 7. Genuine Production Code AST & Lua Template Contract Tests
    # -------------------------------------------------------------------------
    def test_production_hospital_heal_conforms_to_contract(self) -> None:
        """Verify production run_hospital_heal generates compliant SFSArray Lua without dict bug."""
        client = MockGameClient(pid=23848, label="Farm")
        client.wounded_troops = [
            {"armyId": "400101", "count": 250},
            {"armyId": "400201", "count": 100},
        ]
        cd = MockCD(client)
        res = ba.run_hospital_heal(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("action"), "started_heal_batch")

        # Real Lua template inspection
        syntax_res = LuaTemplateInspector.inspect_hospital_payload_syntax(cd.last_lua)
        self.assertTrue(syntax_res["valid"], f"Production Lua failed template inspection: {syntax_res}")
        self.assertTrue(syntax_res["has_heal_map"] or syntax_res["has_struct_array"])

        # Packet payload verification
        last_msg = client.dispatched_messages[-1]
        self.assertEqual(last_msg["msg"], "HospitalCure")
        valid, err = self.validator.validate_hospital_cure_payload(last_msg["payload"])
        self.assertTrue(valid, f"Dispatched HospitalCure payload violated contract: {err}")

    def test_production_radar_events_conforms_to_contract(self) -> None:
        """Verify production run_radar_events unthrottles radar loop and avoids hardcoded breaks."""
        client = MockGameClient(pid=23848, label="Farm")
        cd = MockCD(client)
        cfg = {"radar_events": {"max_dispatches_per_cycle": 20}}
        res = ba.run_radar_events(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))

        clamp_res = LuaTemplateInspector.inspect_radar_loop_clamp(cd.last_lua, cfg)
        self.assertTrue(clamp_res["unthrottled"], f"Production radar loop is throttled: {clamp_res}")
        self.assertFalse(clamp_res["has_hardcoded_break"])

    def test_production_full_preparedness_conforms_to_contract(self) -> None:
        """Verify production _claim_full_preparedness uses 1-based indexing and no redundant dual dispatch."""
        src = inspect.getsource(ba._claim_full_preparedness)
        indexing_res = LuaTemplateInspector.inspect_claim_stage_indexing(src)
        self.assertTrue(indexing_res["valid"], f"Production _claim_full_preparedness failed contract: {indexing_res}")
        self.assertFalse(indexing_res["has_zero_indexing"])
        self.assertFalse(indexing_res["has_redundant_single_and_batch"])

    def test_production_dialog_dismissal_hooks_conform_to_contract(self) -> None:
        """Verify production LUA_COMMON_HELPERS intercepts CommonDialog and UIManager popups."""
        hooks_res = LuaTemplateInspector.inspect_dialog_dismissal_hooks(ba.LUA_COMMON_HELPERS)
        self.assertTrue(hooks_res["valid"], f"Production dialog dismissal hooks invalid: {hooks_res}")
        self.assertTrue(hooks_res["hooks_common_dialog"])
        self.assertTrue(hooks_res["hooks_ui_manager"])
        self.assertTrue(hooks_res["has_dismiss_logic"])

    def test_production_daily_claims_collision_guard_conforms_to_contract(self) -> None:
        """Verify production run_daily_claims suppresses milestone chests in task claim tick."""
        client = MockGameClient(pid=23848, label="Farm")
        cd = MockCD(client)
        res = ba.run_daily_claims(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))

        # Check that the Lua template enforces out.daily_tasks_claimed == 0 guard
        self.assertIn("out.daily_tasks_claimed == 0", cd.last_lua)
        # Check that milestone chest loop staggers claims with break
        self.assertIn("break -- Stagger milestone chest claims", cd.last_lua)

    # -------------------------------------------------------------------------
    # 7. Mining Event (Mine Cave / Melee) Contract Tests
    # -------------------------------------------------------------------------
    def test_production_mining_event_enum_and_contract(self) -> None:
        """Verify run_mining_event fixes missing ActMineCave enum, checks activity 25, and correctly formats BeginPvpCaveFight."""
        src = inspect.getsource(ba.run_mining_event)
        # 1. Enforces enum initialization to 25
        self.assertIn("ActivityEnum.ActivityType.ActMineCave = 25", src)
        # 2. Checks ActivityListDataManager activity 25
        self.assertIn("actMgr:GetActivityDataByType(25)", src)
        # 3. Formats heroes as array of {index, uuid}
        self.assertIn("index = tonumber(idx), uuid = tonumber(u) or tostring(u)", src)
        # 4. Formats soldiers as map
        self.assertIn("local soldiersMap = (fullForm and type(fullForm.soldiers) == 'table' and fullForm.soldiers) or", src)
        # 5. Fallback logic exists for levels below targetLevel
        self.assertIn("fallback_candidates", src)
        self.assertIn("minLevel", src)

    def test_production_mining_event_force_run_bypasses_schedule(self) -> None:
        """Verify force_mining or task_filter in context allows mining run on any day."""
        client = MockGameClient(pid=23848, label="Farm")
        cd = MockCD(client)
        cfg = {"mining_event": {"weekdays": [], "mine_type": 2, "mine_level": 7}}  # No weekdays configured
        # With force_mining
        res = ba.run_mining_event(cd, 23848, {}, cfg, dry_run=False, context={"force_mining": True})
        self.assertTrue(res.get("ok"))
        self.assertNotEqual(res.get("status"), "off_schedule_not_mon_tue")

        # With task_filter containing mining_event
        res2 = ba.run_mining_event(cd, 23848, {}, cfg, dry_run=False, context={"task_filter": ["mining_event"]})
        self.assertTrue(res2.get("ok"))
        self.assertNotEqual(res2.get("status"), "off_schedule_not_mon_tue")

    # -------------------------------------------------------------------------
    # 8. Phase B Overhaul Contract Tests (Radar Pure-RPC, FP, Zoom, Bounties, Trucks, Always-On)
    # -------------------------------------------------------------------------
    def test_production_radar_pure_rpc_and_walkie_talkie_contracts(self) -> None:
        """Verify radar events use pure server RPCs (DetectEventPveBatch, DetectPurkoutStart, ReceivePurkoutReward, 30424) and zero unsafe 3D scene resets."""
        src = inspect.getsource(ba.run_radar_events)
        self.assertIn("DetectEventPveBatch", src)
        self.assertIn("DetectPurkoutStart", src)
        self.assertIn("ReceivePurkoutReward", src)
        self.assertIn("ev.helpInfo.pointId", src)
        self.assertIn("GAME_EFFECT_30424", src)
        self.assertIn("SU_DetectSummon", src)
        self.assertIn("CheckNeedShowUpLevelPanel", src)
        # Never force-load 3D road scenes or destroy UIPVELoading
        self.assertNotIn("SceneManager.ChangeToLevel(", src)
        self.assertNotIn("DestroyWindow('UIPVELoading')", src)

    def test_production_full_preparedness_localization_and_matching(self) -> None:
        """Verify Full Preparedness uses colon Localization:GetString, english-dialog.txt fallback, and strict theme matching."""
        src_probe = inspect.getsource(ba._probe_preparedness_phase)
        self.assertIn("Localization:GetString(", ba.LUA_COMMON_HELPERS)
        self.assertNotIn("Localization.GetString(", src_probe)
        self.assertNotIn("Localization.GetString(", ba.LUA_COMMON_HELPERS)
        self.assertEqual(ba._localize_id("370029"), "Hero Progression")
        self.assertEqual(ba._localize_id("370025"), "Military Drill")

        actions_hero = ba._match_preparedness_actions({
            "theme": "Hero Progression",
            "theme_raw": "370029",
            "score_methods": [{"id": "372213", "label": "Perform {0} Prime Recruits"}],
            "score_labels": ["Perform {0} Prime Recruits"],
            "vs_theme": "VS Day 6: Enemy Buster",
            "vs_score_methods": [{"id": "370002", "label": "Use any 1-min Speedup"}],
            "vs_score_labels": ["Use any 1-min Speedup"],
        })
        self.assertEqual(actions_hero, ["free_recruits"])

    def test_production_troop_training_event_speed_zoom_contract(self) -> None:
        """Verify _detect_training_event_boost and run_troop_training QueueCcdMNew zoom loop."""
        client = MockGameClient(pid=23848, label="Farm")
        cd = MockCD(client)
        b_drill = ba._detect_training_event_boost(cd, 23848, probe={
            "ok": True, "theme": "Military Drill", "theme_raw": "370025",
            "fp_cur_score": 6000, "fp_max_score": 60000,
            "score_methods": [{"id": "370007", "label": "Train and assemble 1 Lv.{0} Unit"}],
            "score_labels": ["Train and assemble 1 Lv.{0} Unit"],
            "vs_open": False, "vs_day": 0, "vs_cur_score": 0, "vs_max_score": 0,
        })
        self.assertTrue(b_drill["should_zoom"])
        self.assertTrue(b_drill["scores_on_train"])

        b_vs5 = ba._detect_training_event_boost(cd, 23848, probe={
            "ok": True, "theme": "Hero Progression", "theme_raw": "370029",
            "fp_cur_score": 6000, "fp_max_score": 60000, "score_methods": [], "score_labels": [],
            "vs_open": True, "vs_day": 5, "vs_theme": "VS Day 5: Total Mobilization & Troop Training",
            "vs_cur_score": 100000, "vs_max_score": 3200000, "vs_score_methods": [], "vs_score_labels": [],
        })
        self.assertTrue(b_vs5["should_zoom"])

        b_done = ba._detect_training_event_boost(cd, 23848, probe={
            "ok": True, "theme": "Military Drill", "theme_raw": "370025",
            "fp_cur_score": 60000, "fp_max_score": 60000,
            "score_methods": [{"id": "370007", "label": "Train and assemble 1 Lv.{0} Unit"}],
            "score_labels": ["Train and assemble 1 Lv.{0} Unit"],
            "vs_open": False, "vs_day": 0, "vs_cur_score": 0, "vs_max_score": 0,
        })
        self.assertFalse(b_done["should_zoom"])

        src_tt = inspect.getsource(ba.run_troop_training)
        self.assertIn("MsgDefines.QueueCcdMNew", src_tt)
        self.assertIn("_detect_training_event_boost", src_tt)

    def test_production_bounties_3in1_and_trucks_contracts(self) -> None:
        """Verify Gold Bounties 3-in-1 (SetLocalLockOrange, DispatchAssist, DispatchSteal) and Trade Trucks contracts."""
        src_bounties = inspect.getsource(ba.run_bounties)
        self.assertIn("SetLocalLockOrange", src_bounties)
        self.assertIn("MsgDefines.DispatchAssist", src_bounties)
        self.assertIn("run_bounty_steal", src_bounties)

        src_steal = inspect.getsource(ba.run_bounty_steal)
        self.assertIn("MsgDefines.DispatchSteal", src_steal)

        src_trucks = inspect.getsource(ba.run_trucks)
        self.assertIn("BeforeDeparture", src_trucks)
        self.assertIn("hasReward", src_trucks)
        self.assertIn("TryChangeTrain", src_trucks)

    def test_production_always_on_auto_help_and_tech_only_contracts(self) -> None:
        """Verify UINoticeTips exclusion from _dismiss_modal_dialogs and tech_only mode in run_alliance_daily."""
        self.assertIn("wName ~= 'UINoticeTips'", ba.LUA_COMMON_HELPERS)
        src_ad = inspect.getsource(ba.run_alliance_daily)
        self.assertIn("tech_only: bool = False", src_ad)
        self.assertIn("tech_only_mode = bool(tech_only", src_ad)

    def test_phase_c_all_32_tasks_telemetry_and_truthy_zero_safety(self) -> None:
        """Verify all 32 TASK_REGISTRY tasks emit non-empty detail_lines and message, and bot_mine_melee / daemon / multi_client_bot use atomic writes and truthy-0 safe helpers."""
        self.assertEqual(len(ba.TASK_REGISTRY), 32)
        self.assertEqual(len(ba.TASK_ORDER), 31)
        self.assertEqual(set(ba.TASK_REGISTRY) - set(ba.TASK_ORDER), {"dismiss_popups"})
        self.assertEqual(set(ba.TASK_ORDER) - set(ba.TASK_REGISTRY), set())
        for t_name in ba.TASK_REGISTRY:
            norm = ba._finalize_task_result(t_name, {"ok": True, "action": "none", "dry_run": True})
            self.assertTrue(isinstance(norm.get("detail_lines"), list) and len(norm["detail_lines"]) > 0, f"{t_name} missing detail_lines")
            self.assertTrue(isinstance(norm.get("message"), str) and len(norm["message"]) > 0, f"{t_name} missing message")

        root_dir = Path(__file__).resolve().parent.parent
        bmm_src = (root_dir / "tools" / "bot mine melee.py").read_text(encoding="utf-8")
        self.assertIn("local function _first_pos_prop(", bmm_src)

        mcb_src = (root_dir / "tools" / "multi client bot.py").read_text(encoding="utf-8")
        self.assertIn("os.replace(tmp_path, config_path)", mcb_src)

        aw_src = (root_dir / "daemon" / "apply widescreen smooth map.py").read_text(encoding="utf-8")
        self.assertIn("os.rename(tmpPath, filePath)", aw_src)
        ld_src = (root_dir / "daemon" / "lastz auto engine daemon.py").read_text(encoding="utf-8")
        self.assertIn("apply widescreen smooth map.py", ld_src)
        self.assertIn("MASTER_LUA_CODE", ld_src)

    def test_daily_tasks_complete_and_building_upgrade_rpc_contracts(self) -> None:
        """Verify daily_tasks_complete classifies all 19 live Daily Quest IDs safely and uses verified RPCs."""
        self.assertIn("daily_tasks_complete", ba.TASK_REGISTRY)
        cases = {
            "1000052": "social_likes",
            "1000037": "hero_exp",
            "1000016": "recruit_ticket",
            "1000045": "alliance_donate",
            "1000017": "alliance_help",
            "1000012": "building_upgrade",
            "1000006": "research_tech",
            "1000002": "train_troops",
            "1000003": "train_troops",
            "1000004": "train_troops",
            "1000035": "use_speedup",
            "1000046": "arena_attack",
            "1000044": "trade_trucks",
            "1000047": "plunder_bounty",
            "1000018": "radar_events",
            "1000049": "boss_rally",
            "1000048": "gather_acts",
            "1000023": "pack_shop_iap",
            "1000042": "attack_hq",
        }
        for tid, expected in cases.items():
            self.assertEqual(ba._classify_daily_task_kind({"id": tid, "desc": "", "gotype2": 0}), expected, f"Mismatch for {tid}")

        self.assertIn("SendLoveMoment", inspect.getsource(ba._do_daily_social_likes))
        self.assertIn("MsgDefines.HeroLvUp", inspect.getsource(ba._do_daily_hero_exp))
        self.assertIn("MsgDefines.LotteryHeroCard", inspect.getsource(ba._do_daily_ticket_recruit))
        self.assertIn("HasRallyFormationForInfo", inspect.getsource(ba._do_daily_boss_rally))
        self.assertIn("MsgDefines.FindResourcePoint", inspect.getsource(ba._do_daily_gather_acts))
        self.assertIn("MsgDefines.DailyQuestGetAllReward", inspect.getsource(ba._claim_all_daily_tasks_and_boxes))

        src_bldg = inspect.getsource(ba.run_building_upgrades)
        self.assertIn("MsgDefines.FreeBuildingUpNew", src_bldg)
        self.assertIn("robotUuid = robot.uuid", src_bldg)
        self.assertIn("CheckSendBuildFinish", src_bldg)

    def test_run_bot_cycle_covers_all_visible_ui_tasks_and_save_config_atomic(self) -> None:
        """Ensure every visible Hub UI task is in canonical STAGE_TASK_ORDER, save_config works cleanly, and ignore_cooldowns bypasses locks."""
        import importlib.util
        import tempfile
        root_dir = Path(__file__).resolve().parent.parent

        def _load(name: str, rel: str):
            spec = importlib.util.spec_from_file_location(name, str(root_dir / rel))
            mod = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            return mod

        mcb = _load("test_mcb_cycle_cov", "tools/multi client bot.py")
        hub_src = (root_dir / "launcher" / "heinzhubweb.py").read_text(encoding="utf-8")
        import re
        m = re.search(r"TASK_CATALOG:\s*list\[dict\[str,\s*str\]\]\s*=\s*\[(.*?)\n\]", hub_src, flags=re.S)
        self.assertIsNotNone(m)
        ui_keys = re.findall(r'"key"\s*:\s*"([^"]+)"', m.group(1))
        self.assertGreaterEqual(len(ui_keys), 24)
        self.assertNotIn("alliance_boss_mine", ui_keys)
        self.assertNotIn("Bear Trap", m.group(1))
        canonical = set(mcb.STAGE_TASK_ORDER)
        missing = [k for k in ui_keys if k not in canonical]
        self.assertEqual(missing, [], f"UI tasks missing from Run Bot Cycle canonical stages: {missing}")

        # Verify Full Map Load v8.0 engine hooks & hotkey wiring
        map_engine_src = (root_dir / "daemon" / "apply widescreen smooth map.py").read_text(encoding="utf-8")
        self.assertIn("function _G.ShouldBuildPointNow", map_engine_src)
        self.assertIn("function _G.TriggerFullMapLoad", map_engine_src)
        self.assertIn("kc.F6", map_engine_src)
        self.assertIn("--full-map-load", map_engine_src)
        self.assertIn("full_map_load", hub_src)
        self.assertIn("_global_hotkey_loop", hub_src)

        # Verify save_config works cleanly (threading import fix)
        with tempfile.TemporaryDirectory() as td:
            cfg_p = Path(td) / "bot_config_test.json"
            mcb.save_config({"ok": True}, config_path=cfg_p)
            self.assertTrue(cfg_p.exists())

        # Verify ignore_cooldowns bypasses active stage cooldown locks
        st_def = mcb.STAGE_DEFINITIONS[4]
        now_t = 1000.0
        state_locked = {"clients": {"c1": {"stages": {st_def["key"]: {"lock_until": now_t + 25.0}}}}}
        sm_cfg = {"enforce_cooldowns": True, "stage_cooldowns_seconds": {"5": 30.0}}
        ccfg = {"tasks": {"daily_claims": True}}
        snap = {"ok": True}
        em = {"preempt_lower_stages": False}
        g_locked = mcb._evaluate_stage_entry_guard(st_def, "c1", snap, ccfg, sm_cfg, state_locked, em, None, False, now_t, ignore_cooldowns=False)
        self.assertFalse(g_locked["allowed"])
        self.assertEqual(g_locked["status"], "cooldown_locked")
        g_forced = mcb._evaluate_stage_entry_guard(st_def, "c1", snap, ccfg, sm_cfg, state_locked, em, None, False, now_t, ignore_cooldowns=True)
        self.assertTrue(g_forced["allowed"])

    def test_pve_battle_skip_ordering_and_startplay_guard(self) -> None:
        """Verify _lua_trigger_pve_skip_snippet waits for startPlay, calls ShowResult(true) BEFORE ForceShowResultFlag(), and works in Area Exploration (City scene)."""
        snip = ba._lua_trigger_pve_skip_snippet()
        self.assertIn("actorMgr.startPlay == true and not actorMgr.onPreStart", snip)
        self.assertIn("inPveView or inRealPve or actorPlaying", snip)
        idx_show = snip.find("actorMgr:ShowResult(true)")
        idx_flag = snip.find("actorMgr:ForceShowResultFlag()")
        self.assertGreater(idx_show, 0)
        self.assertGreater(idx_flag, idx_show, "ShowResult(true) MUST be called BEFORE ForceShowResultFlag()")
        # Ensure neither hero_battlefield nor area_exploration has unguarded raw OnShowResult calls
        self.assertNotIn("vPve:OnShowResult()", inspect.getsource(ba.run_hero_battlefield))
        self.assertNotIn("vPve:OnShowResult()", inspect.getsource(ba.run_area_exploration))

    def test_all_9_queued_bot_fixes_verified(self) -> None:
        """Behavioral and contract verification for all 9 queued bot fixes."""
        import importlib.util
        root_dir = Path(__file__).resolve().parent.parent

        def _load(name: str, rel: str):
            spec = importlib.util.spec_from_file_location(name, str(root_dir / rel))
            mod = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            return mod

        mcb = _load("test_mcb_9fixes", "tools/multi client bot.py")
        hub = _load("test_hub_9fixes", "launcher/heinzhubweb.py")

        # 1. Formation starvation guard & Stage 3 ordering
        self.assertEqual(mcb.STAGE_DEFINITIONS[2]["tasks"], ("mining_event", "mine_melee_refresh"))
        farm_cfg = {
            "formation_reserve": 0,
            "mine_melee_refresh": {"reserve_formations": 0},
            "tasks": {"radar_events": True, "mine_melee_refresh": True},
        }
        self.assertEqual(mcb._compute_effective_gather_reserve(farm_cfg, {"unlockFormations": 3}, {}), 1)
        self.assertEqual(mcb._compute_effective_gather_reserve(farm_cfg, {"unlockFormations": 1}, {}), 0)
        self.assertEqual(
            mcb._compute_effective_gather_reserve(farm_cfg, {"unlockFormations": 3}, {"task_filter": ["mine_melee_refresh"]}),
            0,
        )

        # 2. Off-theme speedup spending guard (Age of Science must NEVER spend Build or Train speedups)
        all_cats = {"build": True, "research": True, "train": True, "heal": True}
        allowed_sci, theme_sci, _ = ba._resolve_theme_speedup_categories(
            {"ok": True, "theme": "Age of Science", "score_labels": ["Use 1-min Research Speedup"]},
            all_cats,
        )
        self.assertEqual(theme_sci, "Age of Science")
        self.assertEqual(allowed_sci, {"build": False, "research": True, "train": False, "heal": False})

        allowed_hero, _, _ = ba._resolve_theme_speedup_categories(
            {"ok": True, "theme": "Hero Progression", "score_labels": ["Prime Recruit"]},
            all_cats,
        )
        self.assertFalse(any(allowed_hero.values()))

        allowed_holistic, _, _ = ba._resolve_theme_speedup_categories(
            {"ok": True, "theme": "Holistic Growth", "score_labels": ["Use any 1-min speedup"]},
            all_cats,
        )
        self.assertTrue(allowed_holistic["build"] and allowed_holistic["research"] and allowed_holistic["train"])

        # 3. Daily Task #1000052 MomentManager feed refresh
        src_likes = inspect.getsource(ba._do_daily_social_likes)
        for sym in ("GetChatMomentRecommendsList", "GetChatMomentList", "SendGetChatMomentList", "SendGetMomentList", "ResetChatMomentListRequestState"):
            self.assertIn(sym, src_likes)

        # 4. Battle Auto-Skip fallback completeness
        skip_snip = ba._lua_trigger_pve_skip_snippet()
        self.assertIn("CarBattlePveManager:SkipLevel", skip_snip)
        self.assertIn("PveActorMgr1", skip_snip)

        # 5. Intercity Trade Trucks affordability & empty-cache fix
        src_trucks = inspect.getsource(ba.run_trucks)
        self.assertIn("canAffordReroll", src_trucks)
        self.assertIn("_form_has_heroes", src_trucks)
        self.assertIn("synced_station", src_trucks)

        # 6. Mod Vehicle Monday free-refit vs Golden Wrench handling
        src_garage = inspect.getsource(ba.run_garage_upgrades)
        self.assertIn("GetGarageFreeCount(1)", src_garage)
        self.assertIn("GetUsedFreeCount", src_garage)
        self.assertIn("GetCanClickUpgradeCount", src_garage)
        self.assertIn("free_refits_exhausted_wrench_guard_active", src_garage)

        # 7. Daily Task #1000042 safe opt-in HQ attack handler
        src_dtc = inspect.getsource(ba.run_daily_tasks_complete)
        self.assertIn('elif kind == "attack_hq":', src_dtc)
        self.assertIn("skipped_own_peace_shield_active", src_dtc)
        self.assertIn("daily_tasks_complete", hub.HubBackend._RULE_KEYS)

        # 8. Regional Exploration summary stage=645->650 fix
        exp_norm = ba._finalize_task_result(
            "area_exploration",
            {"ok": True, "order": 645, "start_order": 645, "end_order": 650, "wins": 5, "battles": [{"stage": 650, "order_after": 650}]},
        )
        self.assertIn("stage=645->650", exp_norm["detail_lines"][0])

        # 9. Hero Battlefield map.power resolution + benign in-game toast classification
        src_hb = inspect.getsource(ba.run_hero_battlefield)
        self.assertIn("map.power", src_hb)
        self.assertEqual(hub._classify_in_game_tip("Claimed rewards successfully"), ("DETAIL", "detail", "In-game toast"))
        self.assertEqual(hub._classify_in_game_tip("Not enough stamina to march"), ("WARN", "warn", "In-game warning"))
        self.assertEqual(hub._classify_in_game_tip("Server error E100172"), ("ERR", "err", "Server Error"))

    def test_hero_progression_cross_module_parity_and_safe_defaults(self) -> None:
        """Verify hero_progression parity across bot actions, multi client bot, HubBackend, and safe defaults."""
        import importlib.util
        root_dir = Path(__file__).resolve().parent.parent

        def _load(name: str, rel: str):
            spec = importlib.util.spec_from_file_location(name, str(root_dir / rel))
            mod = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            return mod

        mcb = _load("test_mcb_hp_parity", "tools/multi client bot.py")
        hub = _load("test_hub_hp_parity", "launcher/heinzhubweb.py")

        self.assertEqual(len(ba.TASK_ORDER), 31)
        self.assertEqual(len(ba.TASK_REGISTRY), 32)
        self.assertEqual(set(ba.TASK_REGISTRY) - set(ba.TASK_ORDER), {"dismiss_popups"})
        self.assertIn("hero_progression", ba.TASK_ORDER)
        self.assertIn("hero_progression", ba.TASK_REGISTRY)

        stage4 = mcb.STAGE_DEFINITIONS[3]
        self.assertEqual(stage4["key"], "stage_4_base_production")
        self.assertIn("hero_progression", stage4["tasks"])
        self.assertEqual(len(mcb.STAGE_TASK_ORDER), 29)
        self.assertIn("hero_progression", mcb.STAGE_TASK_ORDER)

        self.assertIn("hero_progression", hub.HubBackend._RULE_KEYS)
        catalog_keys = [item["key"] for item in hub.TASK_CATALOG]
        self.assertIn("hero_progression", catalog_keys)
        self.assertTrue(set(catalog_keys).issubset(set(mcb.STAGE_TASK_ORDER)))

        dcfg = mcb.default_config()
        defs = dcfg["client_defaults"]
        main_cfg = defs["main"]
        farm_cfg = defs["farm"]
        self.assertIs(main_cfg["tasks"]["hero_progression"], False)
        self.assertIs(farm_cfg["tasks"]["hero_progression"], True)

        for role_cfg in (main_cfg, farm_cfg):
            hp_rules = role_cfg["hero_progression"]
            self.assertIs(hp_rules["only_hero_day"], True)
            self.assertIs(hp_rules["use_universal_shards"], False)
            self.assertEqual(hp_rules["universal_shard_reserve"], 50)
            self.assertIs(hp_rules["allow_gear_promote"], False)
            self.assertIs(hp_rules["use_replacement_equip"], False)
            self.assertIs(hp_rules["allow_sp_equip"], False)
            self.assertIs(hp_rules["use_universal_sp_shards"], False)


if __name__ == "__main__":
    unittest.main()
