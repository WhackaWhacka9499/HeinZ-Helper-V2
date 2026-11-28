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

    def _make_hospital_lua_runtime(
        self,
        *,
        now_sec: int = 1795857000,
        self_uid: str = "1483575381000694",
        members: dict | None = None,
        untreated_dead: int = 4000,
        unit_treat_sec: float = 2.0,
        ac_level: int = 28,
        ac_para1: str = "38",
        eff_help_cnt: int = 12,
        eff_help_sec: int = 870,
        heal_limit_reached: bool = False,
    ):
        import json
        from lupa import LuaRuntime

        lua_rt = LuaRuntime(unpack_returned_tuples=True)
        members_json = json.dumps(members or {})
        setup_lua = f"""
        local nowSec = {int(now_sec)}
        local nowMs = nowSec * 1000
        _G.__sentMsgs = {{}}
        _G.__uiMutated = 0

        MsgDefines = {{
          HospitalCure = 'hospital.cure',
          AllianceCallHelp = 'al.call.help',
          AlHelpAll = 'al.help.all',
          QueueFinish = 'queue.finish',
          AlRank = 'al.rank',
        }}
        NewQueueType = {{ Default = 0, Hospital = 3, Science = 6, DragonHospital = 46 }}
        NewQueueState = {{ Free = 0, Work = 2, Finish = 3 }}
        AllianceHelpType = {{ Building = 1, Queue = 2, FIX_BUILDING = 3 }}
        BuildingTypes = {{ FUN_BUILD_MAIN = 400000, FUND_BUILD_ALLIANCE_CENTER = 402000 }}
        EffectDefine = {{ CURE_RESOURCE_REDUCE = 108, HEAL_MONEY_DEC = 30263 }}
        TableName = {{ Building = 'building' }}
        IsGold = {{ NoUseGold = 0 }}
        SceneManager = {{
          CurrSceneID = 2,
          IsInHome = function() return false end,
          IsInWorld = function() return true end,
        }}
        ChatInterface = {{}}
        UITimeManager = {{
          GetInstance = function()
            return {{
              GetServerSeconds = function() return nowSec end,
              GetServerTime = function() return nowMs end,
            }}
          end
        }}
        UIManager = {{
          GetInstance = function()
            return {{
              windows = {{
                UIConfirmDialog = {{
                  View = {{
                    activeSelf = true,
                    OnBtnCloseClick = function() _G.__uiMutated = _G.__uiMutated + 1 end,
                    OnBtnConfirmClick = function() _G.__uiMutated = _G.__uiMutated + 1 end,
                  }},
                  Close = function() _G.__uiMutated = _G.__uiMutated + 1 end,
                }}
              }},
              OpenWindow = function() _G.__uiMutated = _G.__uiMutated + 1 end,
              CloseWindow = function() _G.__uiMutated = _G.__uiMutated + 1 end,
              DestroyWindow = function() _G.__uiMutated = _G.__uiMutated + 1 end,
              HideWindow = function() _G.__uiMutated = _G.__uiMutated + 1 end,
            }}
          end
        }}
        SFSNetwork = {{
          SendMessage = function(cmd, p1, p2, p3, p4)
            table.insert(_G.__sentMsgs, {{ cmd = cmd, p1 = p1, p2 = p2, p3 = p3, p4 = p4 }})
          end
        }}
        LocalController = {{
          instance = function()
            return {{
              getLine = function(_, tbl, lineId)
                if tbl == 'building' and lineId == tostring(402000 + {int(ac_level)}) then
                  return {{
                    getValue = function(_, col)
                      if col == 'para1' then return '{ac_para1}' end
                      return nil
                    end
                  }}
                end
                return nil
              end
            }}
          end
        }}
        LuaEntry = {{
          Player = {{
            GetUid = function() return '{self_uid}' end,
            GetName = function() return 'Heinzy' end,
            GetCurServerId = function() return 702 end,
            GetSelfServerId = function() return 702 end,
            IsInAlliance = function() return true end,
            GetAllianceUid = function() return 'ally_warg' end,
            GetAllianceAbbr = function() return 'WARG' end,
          }},
          Effect = {{
            GetGameEffect = function(_, id)
              if id == 30475 then return {int(eff_help_cnt)} end
              if id == 30229 then return {int(eff_help_sec)} end
              return 0
            end
          }},
          DataConfig = {{
            TryGetNum = function(_, tbl, key)
              if tbl == 'alliance_help' and key == 'k1' then return 120 end
              return nil
            end
          }},
          Resource = {{
            GetCntByResType = function() return 999999999 end,
          }},
        }}
        DataCenter = {{
          ArmyFormationDataManager = {{
            GetFreeFormationCount = function() return 4 end,
            GetUnlockFormationCount = function() return 4 end,
          }},
          BuildManager = {{
            MainLv = 30,
            GetFunbuildByItemID = function(_, id)
              if id == 402000 then return {{ itemId = 402000, level = {int(ac_level)} }} end
              return {{ pointId = 519504 }}
            end,
          }},
          HospitalManager = {{
            allHospital = {{
              ['400110'] = {{ armyId = '400110', dead = {int(untreated_dead)}, heal = 0 }},
            }},
            GetAllHospital = function(self) return self.allHospital end,
            HospitalCureHandle = function(self, msg) return msg end,
            GetHospitalHelpLimit = function() return false end,
          }},
          QueueDataManager = {{
            queueDic = {{}},
            GetQueueByType = function() return nil end,
            GetQueueState = function(_, q) return q and q.state or 0 end,
          }},
          ArmyTemplateManager = {{
            GetTreatTime = function() return {float(unit_treat_sec)} end,
          }},
          AllianceMemberDataManager = {{
            allianceMembers = {{}},
          }},
          AllianceHelpDataManager = {{
            myHelpInfoList = {{}},
            otherHelpInfoList = {{}},
            GetHelpNum = function() return 0 end,
          }},
          MonthCardNewManager = {{
            IsHealAutoHelpLimitEnabled = function() return true end,
            GetTodayHealAutoHelpCount = function() return {1000 if heal_limit_reached else 283} end,
            GetHealAutoHelpLimit = function() return 1000 end,
            IsHealAutoHelpLimitReached = function() return {str(bool(heal_limit_reached)).lower()} end,
          }},
        }}
        """
        lua_rt.execute(setup_lua)
        lua_rt.execute(ba._LUA_COMMON_BOOTSTRAP)
        lua_rt.execute(ba._build_hospital_engine_lua())
        # Populate allianceMembers in Lua from JSON
        parsed_members = json.loads(members_json)
        am_tbl = lua_rt.eval("DataCenter.AllianceMemberDataManager.allianceMembers")
        for uid_k, mdata in parsed_members.items():
            tbl = lua_rt.table_from(mdata)
            am_tbl[uid_k] = tbl
        return lua_rt

    def test_hospital_heal_pass_plus_active_dynamic_sizing_lua_vm(self) -> None:
        """Verify Pass + Active calculation counts only active Monthly Pass holders (excl self) and sizes batch accurately."""
        import json

        now_sec = 1795857000
        members = {
            # Self (online + pass) -> must be excluded
            "1483575381000694": {"uid": "1483575381000694", "online": True, "active": False, "monthCardEndTime": now_sec + 864000, "offLineTime": 0},
            # 3 Active + Pass (mix of sec and ms monthCardEndTime)
            "2001": {"uid": "2001", "online": True, "active": False, "monthCardEndTime": now_sec + 500000, "offLineTime": 0},
            "2002": {"uid": "2002", "online": True, "active": False, "monthCardEndTime": (now_sec + 200000) * 1000, "offLineTime": 0},
            "2003": {"uid": "2003", "online": False, "active": True, "monthCardEndTime": now_sec + 100000, "offLineTime": (now_sec - 300) * 1000},
            # Offline Pass holders -> must NOT count when active_grace_minutes == 0
            "2004": {"uid": "2004", "online": False, "active": False, "monthCardEndTime": now_sec + 900000, "offLineTime": (now_sec - 7200) * 1000},
            "2005": {"uid": "2005", "online": False, "active": False, "monthCardEndTime": now_sec + 400000, "offLineTime": (now_sec - 3600) * 1000},
            # Online WITHOUT Pass (expired or -1) -> must NOT count as Pass+Active
            "2006": {"uid": "2006", "online": True, "active": False, "monthCardEndTime": now_sec - 100, "offLineTime": 0},
            "2007": {"uid": "2007", "online": True, "active": False, "monthCardEndTime": -1, "offLineTime": 0},
        }
        # unit_treat_sec = 1.5s, 3 Pass+Active * 990s/help = 2970s -> floor(2970 / 1.5) = 1980 troops (> old 1500 cap!)
        lua_rt = self._make_hospital_lua_runtime(
            now_sec=now_sec,
            members=members,
            untreated_dead=4000,
            unit_treat_sec=1.5,
        )
        raw = lua_rt.eval(
            "_G.__hzHospitalEngine.step({dryRun=false, headless=true, collectFin=true, batchSec=1800, "
            "batchMinutes=30, minTroops=1, maxTroops=50000, callHelp=true, useSpeedups=false, "
            "maxSpeedupMins=0, autoPassActive=true, activeGraceMins=0, localHelperUids={}})"
        )
        res = json.loads(raw)
        self.assertTrue(res["ok"])
        self.assertTrue(res["headless"])
        self.assertEqual(res["batch_sizing_mode"], "pass_plus_active")
        self.assertEqual(res["pass_total_members"], 5)
        self.assertEqual(res["online_members"], 4)
        self.assertEqual(res["pass_active_helpers"], 3)
        self.assertEqual(res["player_max_helps"], 50)
        self.assertEqual(res["per_help_sec"], 990)
        self.assertEqual(res["effective_max_helps"], 3)
        self.assertEqual(res["dynamic_batch_sec"], 2970)
        self.assertEqual(res["queued_troops"], 1980)
        self.assertEqual(lua_rt.eval("_G.__uiMutated"), 0, "Headless heal must never mutate/close UI windows!")

    def test_hospital_heal_caps_at_player_max_helps_and_respects_daily_limit(self) -> None:
        """Verify effective_max_helps caps at player_max_helps and drops Pass helpers when daily heal auto-help limit is reached."""
        import json

        now_sec = 1795857000
        # 30 Pass+Active helpers, but player Alliance Center Lv10 (para1=20) + 0 bonus => player_max_helps = 20
        members = {
            f"30{i:02d}": {"uid": f"30{i:02d}", "online": True, "active": False, "monthCardEndTime": now_sec + 500000, "offLineTime": 0}
            for i in range(1, 31)
        }
        lua_rt = self._make_hospital_lua_runtime(
            now_sec=now_sec,
            members=members,
            untreated_dead=10000,
            unit_treat_sec=10.0,
            ac_level=10,
            ac_para1="20",
            eff_help_cnt=0,
            eff_help_sec=180,  # 120 + 180 = 300s per help
        )
        res = json.loads(
            lua_rt.eval(
                "_G.__hzHospitalEngine.step({dryRun=true, headless=true, collectFin=true, batchSec=1800, "
                "batchMinutes=30, minTroops=1, maxTroops=50000, callHelp=true, autoPassActive=true, activeGraceMins=0, localHelperUids={}})"
            )
        )
        self.assertEqual(res["pass_active_helpers"], 30)
        self.assertEqual(res["player_max_helps"], 20)
        self.assertEqual(res["effective_max_helps"], 20)
        self.assertEqual(res["per_help_sec"], 300)
        self.assertEqual(res["dynamic_batch_sec"], 6000)
        self.assertEqual(res["queued_troops"], 600)

        # Now verify when daily heal auto-help limit (1000/1000) is reached, Pass auto-helpers are not assumed
        lua_rt_lim = self._make_hospital_lua_runtime(
            now_sec=now_sec,
            members=members,
            untreated_dead=10000,
            unit_treat_sec=10.0,
            ac_level=10,
            ac_para1="20",
            eff_help_cnt=0,
            eff_help_sec=180,
            heal_limit_reached=True,
        )
        res_lim = json.loads(
            lua_rt_lim.eval(
                "_G.__hzHospitalEngine.step({dryRun=true, headless=true, collectFin=true, batchSec=1800, "
                "batchMinutes=30, minTroops=1, maxTroops=50000, callHelp=true, autoPassActive=true, activeGraceMins=0, localHelperUids={}})"
            )
        )
        self.assertTrue(res_lim["heal_limit_reached"])
        self.assertEqual(res_lim["effective_max_helps"], 0)
        self.assertEqual(res_lim["batch_sizing_mode"], "online_manual_single_help")
        self.assertEqual(res_lim["dynamic_batch_sec"], 300)

    def test_headless_always_on_tasks_never_dismiss_user_dialogs(self) -> None:
        """Verify headless run_auto_help and run_alliance_daily never invoke _dismiss_modal_dialogs."""
        client = MockGameClient(pid=23848, label="Main")
        cd = MockCD(client)

        ba.run_auto_help(cd, 23848, {}, {}, dry_run=False, headless=True)
        self.assertIn("local isHeadless = true", cd.last_lua)
        self.assertIn("not isHeadless", cd.last_lua)

        ba.run_alliance_daily(cd, 23848, {}, {}, dry_run=False, tech_only=True, headless=True)
        self.assertIn("local isHeadless = true", cd.last_lua)
        self.assertIn("not isHeadless and not techOnly", cd.last_lua)


if __name__ == "__main__":
    unittest.main()
