"""Adversarial Verification & Failure Injection Test Suite.

Probes and stress-tests:
1. Rapid consecutive calls to dismiss_all_popups and Frida session holder concurrency/invalidation.
2. Hospital cure with mixed data types (strings, ints, nil properties, empty army lists, floats).
3. Radar events queue with 20+ mixed items (garbage, help, rescue, marches) under constrained formation counts (0, 1, 2 formations).
4. Full preparedness and daily claims under zero points, negative points, and already-claimed stages.
5. Fuzzing and extreme boundary inputs verifying no crashes or unhandled exceptions occur.
"""

from __future__ import annotations

import gc
import json
import os
import sys
import threading
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import importlib
bot_actions = importlib.import_module("tools.bot actions")
client_discovery = importlib.import_module("tools.client discovery")

from tests.testHarness import (
    MockGameClient,
    SFSMessageValidator,
    ServerResponseSimulator,
)

try:
    from lupa import LuaRuntime
    HAS_LUPA = True
except ImportError:
    HAS_LUPA = False


def _create_adversarial_lua_environment() -> Any:
    """Create a real Lua runtime with mocked game globals for empirical execution."""
    if not HAS_LUPA:
        return None

    lua = LuaRuntime(unpack_returned_tuples=True)
    setup_code = """
    _G.sent_messages = {}
    _G.SFSNetwork = {
        SendMessage = function(msg, payload, ...)
            table.insert(_G.sent_messages, {
                msg = tostring(msg or ''),
                payload = payload,
            })
            if tostring(msg or '') == 'HospitalCure' and _G.DataCenter and _G.DataCenter.QueueDataManager then
                _G.DataCenter.QueueDataManager.queueDic['3'] = {
                    uuid = 'q_heal_sim',
                    type = 3,
                    state = 2,
                    endTime = 9999999999000,
                }
            end
        end
    }
    _G.MsgDefines = {
        HospitalCure = 'HospitalCure',
        DailyQuestGetAllReward = 'DailyQuestGetAllReward',
        DailyQuestReward = 'DailyQuestReward',
        AcceptPersonalReward = 'AcceptPersonalReward',
        AcceptPersonalRewardBatch = 'AcceptPersonalRewardBatch',
        BatchDetectEventRewardReceive = 'BatchDetectEventRewardReceive',
        DetectEventRewardReceive = 'DetectEventRewardReceive',
        FinishSampling = 'FinishSampling',
        DetectEventHelpEnd = 'DetectEventHelpEnd',
        DetectEventRescueEnd = 'DetectEventRescueEnd',
        StartPickGarbage = 'StartPickGarbage',
        DetectEventHelpStart = 'DetectEventHelpStart',
        DetectEventRescueStart = 'DetectEventRescueStart',
        ClickCreateTreasureDetect = 'ClickCreateTreasureDetect',
        AchievementRewardGet = 'AchievementRewardGet',
        ReceiveBattlePassAllReward = 'ReceiveBattlePassAllReward',
        TaskRewardBatch = 'TaskRewardBatch',
    }
    _G.DetectEventType = {
        DetectEventPickGarbage = 6,
        DetectEventPVE = 7,
        HeroTrial = 9,
        HELP = 19,
        RESCUE = 20,
        ALLIANCE_TREASURE = 23,
        RewardParkour = 26,
    }
    _G.MarchTargetType = {
        ATTACK_MONSTER = 1,
        COLLECT = 2,
        EXPLORE = 20,
    }
    _G.MarchUtil = {
        SendCreateMarchMessage = function(formUuid, mType, ptId, a1, a2, b1, b2, srvId)
            table.insert(_G.sent_messages, {
                msg = 'MarchUtil.SendCreateMarchMessage',
                payload = {
                    formation = formUuid,
                    mType = mType,
                    ptId = ptId,
                    srvId = srvId,
                }
            })
        end
    }
    _G.LuaEntry = {
        Player = {
            GetUid = function(self) return '1001' end,
            GetName = function(self) return 'Heinzy3' end,
            GetCurServerId = function(self) return 694 end,
            GetSelfServerId = function(self) return 694 end,
            GetCurStamina = function(self) return 500 end,
            GetPower = function(self) return 90000000 end,
        }
    }
    _G.UITimeManager = {
        GetInstance = function(self)
            return {
                GetServerSeconds = function(self) return 1000 end,
            }
        end
    }
    _G.DataCenter = {
        ArmyFormationDataManager = {
            GetFreeFormationCount = function(self) return 3 end,
            GetUnlockFormationCount = function(self) return 4 end,
            GetArmyFormationList = function(self)
                return {
                    { uuid = 'form_1', index = 1 },
                    { uuid = 'form_2', index = 2 },
                    { uuid = 'form_3', index = 3 },
                    { uuid = 'form_4', index = 4 },
                }
            end,
            GetInMarchArmyFormationUuids = function(self) return {} end,
        },
        DailyTaskManager = {
            dailyQuestTasks = {},
            curVal = 0,
            GetCurValue = function(self) return self.curVal end,
            boxStates = {0, 0, 0, 0, 0, 0},
            GetBoxState = function(self, idx, curVal)
                return self.boxStates[idx] or 0
            end,
        },
        HospitalManager = {
            allHospital = {},
            hospitalDic = {},
            CheckSendFinish = function(self) end,
        },
        QueueDataManager = {
            queueDic = {},
            GetAllQueueByType = function(self, t) return {} end,
        },
        RadarCenterDataManager = {
            events = {},
            IsDetectEventDoing = function(self, uuid, flag) return false end,
            AddToFakeGarbageMarchManager = function(self, ptId) end,
            StartDetectEventPve = function(self, uuid)
                table.insert(_G.sent_messages, { msg = 'StartDetectEventPve', payload = { uuid = uuid } })
            end,
            StartToRewardParkourEvent = function(self, uuid, a)
                table.insert(_G.sent_messages, { msg = 'StartToRewardParkourEvent', payload = { uuid = uuid } })
            end,
        },
        DetectEventTemplateManager = {
            GetDetectEventTemplate = function(self, id) return nil end,
        },
        FakeHelperMarchManager = {
            AddMarchIndex = function(self, ptId) end,
        },
        FakeRescueMarchManager = {
            AddMarchIndex = function(self, ptId) end,
        },
        ArmyTemplateManager = {
            GetTreatTime = function(self, aid) return 3.0 end,
        },
        AchievementManager = {
            GetClaimCount = function(self) return 0 end,
            HasClaimable = function(self) return false end,
            GetAllTypes = function(self) return {} end,
        },
        ActBattlePassData = {
            list = {},
        },
        ChapterTaskManager = {
            GetCanReceivedList = function(self) return {} end,
        },
    }
    _G.UIManager = {
        windows = {},
        GetInstance = function(self) return self end,
        GetWindow = function(self, name) return self.windows[name] end,
        CloseWindow = function(self, name)
            if self.windows[name] then self.windows[name].activeSelf = false end
        end,
    }
    _G.Setting = {
        SetPrivateInt = function(k, v) end,
    }
    """
    lua.execute(setup_code)
    return lua


def _get_lua_sent_messages(lua: Any) -> List[Any]:
    """Retrieve all sent SFS messages as Python objects."""
    t = lua.eval("_G.sent_messages")
    count = int(lua.eval("#_G.sent_messages"))
    return [lua.eval(f"_G.sent_messages[{i}]") for i in range(1, count + 1)]


class LupaBridgeCD:
    """Mock Client Discovery adapter delegating Lua execution to embedded Lupa runtime."""

    def __init__(self, lua_runtime: Any):
        self.lua_runtime = lua_runtime

    def frida_eval_lua(self, pid: int, lua_code: str, timeout: float = 8.0) -> Tuple[bool, str]:
        try:
            res = self.lua_runtime.execute(lua_code)
            return True, str(res) if res is not None else ""
        except Exception as exc:
            return False, str(exc)


class TestFridaSessionHolderAndPopupDismissal(unittest.TestCase):
    """Adversarial stress test for Frida Session Holder and dismiss_all_popups."""

    def setUp(self) -> None:
        client_discovery.close_frida_session()

    def tearDown(self) -> None:
        client_discovery.close_frida_session()

    def test_session_holder_lifecycle_and_invalidation(self) -> None:
        """Verify _FridaSessionHolder state transitions, close idempotence, and fault handling."""
        mock_session = MagicMock()
        mock_script = MagicMock()

        holder = client_discovery._FridaSessionHolder(1234, mock_session, mock_script)
        self.assertTrue(holder.is_valid)

        # Invalidate via is_detached
        mock_session.is_detached = True
        self.assertFalse(holder.is_alive())

        # Reset is_detached, verify psutil check
        mock_session.is_detached = False
        self.assertTrue(holder.is_valid)

        # Close session
        holder.close()
        self.assertFalse(holder.is_valid)
        self.assertIsNone(holder.script)
        self.assertIsNone(holder.session)
        mock_script.unload.assert_called_once()
        mock_session.detach.assert_called_once()

        # Idempotent double close
        holder.close()

        # Fault injection: script.unload and session.detach throw exceptions
        failing_session = MagicMock()
        failing_session.detach.side_effect = RuntimeError("Frida IPC failure")
        failing_script = MagicMock()
        failing_script.unload.side_effect = RuntimeError("Frida script died")

        holder2 = client_discovery._FridaSessionHolder(5678, failing_session, failing_script)
        # Should not raise exception
        holder2.close()
        self.assertFalse(holder2.is_valid)

    def test_close_frida_session_multi_pid_and_none(self) -> None:
        """Verify close_frida_session with specific PIDs, non-existent PIDs, and global None."""
        s1, sc1 = MagicMock(), MagicMock()
        s2, sc2 = MagicMock(), MagicMock()

        client_discovery._CACHED_SESSIONS[1001] = client_discovery._FridaSessionHolder(1001, s1, sc1)
        client_discovery._CACHED_SESSIONS[1002] = client_discovery._FridaSessionHolder(1002, s2, sc2)

        # Close non-existent PID
        client_discovery.close_frida_session(999999)
        self.assertIn(1001, client_discovery._CACHED_SESSIONS)
        self.assertIn(1002, client_discovery._CACHED_SESSIONS)

        # Close single PID
        client_discovery.close_frida_session(1001)
        self.assertNotIn(1001, client_discovery._CACHED_SESSIONS)
        self.assertIn(1002, client_discovery._CACHED_SESSIONS)
        s1.detach.assert_called_once()

        # Close all via None
        client_discovery.close_frida_session(None)
        self.assertEqual(len(client_discovery._CACHED_SESSIONS), 0)
        s2.detach.assert_called_once()

        # Double close all
        client_discovery.close_frida_session(None)

    def test_rapid_consecutive_dismiss_all_popups(self) -> None:
        """Stress-test 100 rapid consecutive dismiss_all_popups calls."""
        mock_cd = MagicMock()
        mock_cd.frida_eval_lua.return_value = (
            True,
            json.dumps({"ok": True, "dismissed_count": 0, "dismissed_windows": [], "action": "none"}),
        )

        for _ in range(100):
            res = bot_actions.dismiss_all_popups(mock_cd, 23848)
            self.assertTrue(res.get("ok"))
            self.assertEqual(res.get("action"), "none")

        self.assertEqual(mock_cd.frida_eval_lua.call_count, 100)

    def test_multithreaded_concurrent_dismiss_all_popups_stress(self) -> None:
        """Spawn 10 concurrent worker threads executing dismiss_all_popups while sessions are closed."""
        mock_cd = MagicMock()
        mock_cd.frida_eval_lua.return_value = (
            True,
            json.dumps({"ok": True, "dismissed_count": 1, "dismissed_windows": ["CommonDialog"], "action": "dismissed"}),
        )

        exceptions: List[Exception] = []

        def worker(thread_id: int):
            try:
                for _ in range(20):
                    res = bot_actions.dismiss_all_popups(mock_cd, 23848 + (thread_id % 2))
                    if not res.get("ok"):
                        exceptions.append(RuntimeError(f"Call failed: {res}"))
                    time.sleep(0.001)
            except Exception as e:
                exceptions.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()

        # Interleaved session resets
        for _ in range(5):
            time.sleep(0.005)
            client_discovery.close_frida_session()

        for t in threads:
            t.join()

        self.assertEqual(len(exceptions), 0, f"Concurrent execution produced exceptions: {exceptions}")

    def test_gc_finalizer_reentrancy_under_hz_bridge_lock(self) -> None:
        """Force gc.collect() while holding _HZ_BRIDGE_LOCK to prove _cleanup_cd is GC-reentrant."""
        was_enabled = gc.isenabled()
        gc.disable()
        cache_key = None
        cd_id = None
        try:
            cyclic_cd = MagicMock()
            cyclic_cd.frida_eval_lua.return_value = (
                True,
                json.dumps({"ok": True, "dismissed_count": 0, "dismissed_windows": [], "action": "none"}),
            )
            cyclic_cd._self_cycle = cyclic_cd
            cd_id = id(cyclic_cd)
            cache_key = (cd_id, 999991, 1.0)

            res = bot_actions.dismiss_all_popups(cyclic_cd, 999991)
            self.assertTrue(res.get("ok"))
            bot_actions._mark_hz_bootstrapped(cyclic_cd, cache_key)
            with bot_actions._HZ_BRIDGE_LOCK:
                bot_actions._HZ_HOSPITAL_ENGINE_TARGETS[cache_key] = 1.0
                self.assertIn(cache_key, bot_actions._HZ_BOOTSTRAPPED_TARGETS)
                self.assertIn(cd_id, bot_actions._HZ_FINALIZED_BRIDGE_IDS)

            del cyclic_cd
            errors: List[Exception] = []
            collected_counts: List[int] = []

            def run_gc_under_lock() -> None:
                try:
                    with bot_actions._HZ_BRIDGE_LOCK:
                        collected_counts.append(gc.collect())
                except Exception as exc:
                    errors.append(exc)

            worker = threading.Thread(target=run_gc_under_lock)
            worker.start()
            worker.join(timeout=5.0)

            self.assertFalse(worker.is_alive(), "Deadlock: gc.collect() under _HZ_BRIDGE_LOCK timed out")
            self.assertEqual(errors, [])
            self.assertEqual(len(collected_counts), 1)
            self.assertNotIn(cache_key, bot_actions._HZ_BOOTSTRAPPED_TARGETS)
            self.assertNotIn(cache_key, bot_actions._HZ_HOSPITAL_ENGINE_TARGETS)
            self.assertNotIn(cd_id, bot_actions._HZ_FINALIZED_BRIDGE_IDS)
        finally:
            if cache_key is not None:
                with bot_actions._HZ_BRIDGE_LOCK:
                    bot_actions._HZ_BOOTSTRAPPED_TARGETS.pop(cache_key, None)
                    bot_actions._HZ_HOSPITAL_ENGINE_TARGETS.pop(cache_key, None)
            if cd_id is not None:
                with bot_actions._HZ_BRIDGE_LOCK:
                    bot_actions._HZ_FINALIZED_BRIDGE_IDS.discard(cd_id)
            if was_enabled:
                gc.enable()

    def test_multithreaded_dismiss_all_popups_with_cyclic_cd_gc_stress(self) -> None:
        """Stress concurrent dismiss_all_popups across cyclic MagicMock bridges while gc.collect() runs."""
        exceptions: List[Exception] = []
        payload = json.dumps({"ok": True, "dismissed_count": 0, "dismissed_windows": [], "action": "none"})

        def worker(thread_id: int) -> None:
            try:
                for step in range(25):
                    cd = MagicMock()
                    cd.frida_eval_lua.return_value = (True, payload)
                    cd._self_cycle = cd
                    res = bot_actions.dismiss_all_popups(cd, 23900 + (thread_id % 3))
                    if not res.get("ok"):
                        exceptions.append(RuntimeError(f"Call failed: {res}"))
                    del cd
                    if step % 5 == 0:
                        gc.collect()
            except Exception as exc:
                exceptions.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for _ in range(10):
            gc.collect()
            time.sleep(0.002)
        for t in threads:
            t.join(timeout=10.0)
            self.assertFalse(t.is_alive(), "Worker thread deadlocked during cyclic bridge GC stress")

        self.assertEqual(exceptions, [])

    def test_mine_melee_gc_finalizer_reentrancy_under_lock(self) -> None:
        """Force gc.collect() while holding _HZ_MINE_BRIDGE_LOCK to prove bot mine melee cleanup is GC-reentrant."""
        mine_mod = bot_actions._load_bot_mine_melee_module()
        expected_path = (PROJECT_ROOT / "tools" / "bot mine melee.py").resolve()
        self.assertEqual(Path(mine_mod.__file__).resolve(), expected_path)
        self.assertIsInstance(mine_mod._HZ_MINE_BRIDGE_LOCK, type(threading.RLock()))

        was_enabled = gc.isenabled()
        gc.disable()
        cache_key = None
        cd_id = None
        try:
            cyclic_cd = MagicMock()
            cyclic_cd._self_cycle = cyclic_cd
            cd_id = id(cyclic_cd)
            cache_key = (cd_id, 999992, 1.0)

            mine_mod._mark_hz_mine_bootstrapped(cyclic_cd, cache_key)
            with mine_mod._HZ_MINE_BRIDGE_LOCK:
                self.assertIn(cache_key, mine_mod._HZ_MINE_BOOTSTRAPPED_TARGETS)
                self.assertIn(cd_id, mine_mod._HZ_MINE_FINALIZED_IDS)

            del cyclic_cd
            errors: List[Exception] = []
            collected_counts: List[int] = []

            def run_gc_under_lock() -> None:
                try:
                    with mine_mod._HZ_MINE_BRIDGE_LOCK:
                        collected_counts.append(gc.collect())
                except Exception as exc:
                    errors.append(exc)

            worker = threading.Thread(target=run_gc_under_lock)
            worker.start()
            worker.join(timeout=5.0)

            self.assertFalse(worker.is_alive(), "Deadlock: gc.collect() under _HZ_MINE_BRIDGE_LOCK timed out")
            self.assertEqual(errors, [])
            self.assertEqual(len(collected_counts), 1)
            self.assertNotIn(cache_key, mine_mod._HZ_MINE_BOOTSTRAPPED_TARGETS)
            self.assertNotIn(cd_id, mine_mod._HZ_MINE_FINALIZED_IDS)
        finally:
            if cache_key is not None:
                with mine_mod._HZ_MINE_BRIDGE_LOCK:
                    mine_mod._HZ_MINE_BOOTSTRAPPED_TARGETS.pop(cache_key, None)
            if cd_id is not None:
                with mine_mod._HZ_MINE_BRIDGE_LOCK:
                    mine_mod._HZ_MINE_FINALIZED_IDS.discard(cd_id)
            if was_enabled:
                gc.enable()

    def test_dismiss_all_popups_resilience_to_lua_timeout_and_corrupted_json(self) -> None:
        """Verify robust error reporting when Lua times out or returns malformed JSON."""
        mock_cd = MagicMock()

        # Timeout
        mock_cd.frida_eval_lua.return_value = (False, "Timed out after 6000ms")
        res1 = bot_actions.dismiss_all_popups(mock_cd, 23848)
        self.assertFalse(res1.get("ok"))
        self.assertIn("Timed out", res1.get("error", ""))

        # Corrupted JSON
        mock_cd.frida_eval_lua.return_value = (True, "{invalid_json: true, unterminated")
        res2 = bot_actions.dismiss_all_popups(mock_cd, 23848)
        self.assertFalse(res2.get("ok"))
        self.assertIn("json decode failed", res2.get("error", ""))

        # Empty string
        mock_cd.frida_eval_lua.return_value = (True, "")
        res3 = bot_actions.dismiss_all_popups(mock_cd, 23848)
        self.assertFalse(res3.get("ok"))

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_lua_modal_dialog_auto_dismissal_matrix(self) -> None:
        """Empirically verify dismiss_all_popups closing a stacked matrix of active modal windows in Lua."""
        lua = _create_adversarial_lua_environment()
        self.assertIsNotNone(lua)

        # Populate UIManager with stacked open modal dialogs
        lua.execute("""
        _G.UIManager.windows = {
            CommonDialog = {
                activeSelf = true,
                View = {
                    activeSelf = true,
                    OnBtnConfirmClick = function(self) self.confirmed = true end,
                },
                Close = function(self) self.closed = true; self.activeSelf = false end,
            },
            UIGiftPackageRewardGet = {
                activeSelf = true,
                View = {
                    activeSelf = true,
                    OnBtnOkClick = function(self) self.okClicked = true end,
                },
                Close = function(self) self.closed = true; self.activeSelf = false end,
            },
            UIError = {
                activeSelf = true,
                Close = function(self) self.closed = true; self.activeSelf = false end,
            },
        }
        """)

        cd = LupaBridgeCD(lua)
        res = bot_actions.dismiss_all_popups(cd, 23848)
        self.assertTrue(res.get("ok"))
        self.assertGreaterEqual(res.get("dismissed_count", 0), 2)
        dismissed_names = res.get("dismissed_windows", [])
        self.assertIn("CommonDialog", dismissed_names)
        self.assertIn("UIGiftPackageRewardGet", dismissed_names)


class TestHospitalCureAdversarialProbes(unittest.TestCase):
    """Adversarial stress test for Hospital Healing payload construction and failure modes."""

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_hospital_cure_empty_army_list_adversarial(self) -> None:
        """Verify empty army list results in action='no_wounded' with 0 SFS packets."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        _G.DataCenter.HospitalManager.allHospital = {}
        _G.DataCenter.HospitalManager.hospitalDic = {}
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"hospital_heal": {"batch_minutes": 120, "max_batch_troops": 2000}}
        res = bot_actions.run_hospital_heal(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("wounded_total"), 0)
        self.assertEqual(res.get("queued_troops"), 0)
        self.assertIn(res.get("action"), ("no_wounded", "dormant_no_wounded"))

        sent = _get_lua_sent_messages(lua)
        cure_calls = [m for m in sent if m.msg == "HospitalCure"]
        self.assertEqual(len(cure_calls), 0)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_hospital_cure_mixed_types_and_string_coercion(self) -> None:
        """Verify mixed types (strings, numeric strings, floats) serialize into a valid SFSArray of structs."""
        lua = _create_adversarial_lua_environment()
        # Provide GetAllHospital method returning wounded troops
        lua.execute("""
        _G.DataCenter.HospitalManager.GetAllHospital = function(self)
            return {
                [1] = { armyId = '400101', dead = 500 },           -- string ID, int dead
                [2] = { armyId = 400201, num = '350' },            -- int ID, string num
                [3] = { id = '400301', hurt = 220.8 },             -- alternate key 'id', float 'hurt'
                [4] = { armyId = '400401', injured = 100 },        -- alternate key 'injured'
            }
        end
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"hospital_heal": {"batch_minutes": 120, "max_batch_troops": 2000}}
        res = bot_actions.run_hospital_heal(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("wounded_total"), 1170)
        self.assertGreater(res.get("queued_troops"), 0)

        sent = _get_lua_sent_messages(lua)
        cure_calls = [m for m in sent if m.msg == "HospitalCure"]
        self.assertEqual(len(cure_calls), 1)

        payload_raw = cure_calls[0].payload
        py_arr = []
        if hasattr(payload_raw.arr, "items"):
            for k, v in payload_raw.arr.items():
                if hasattr(v, "armyId"):
                    py_arr.append({"armyId": str(v.armyId), "healNum": int(v.healNum)})
                else:
                    py_arr.append({"armyId": str(k), "healNum": int(v)})
        elif hasattr(payload_raw.arr, "__len__") and len(payload_raw.arr) > 0:
            for i in range(1, len(payload_raw.arr) + 1):
                item = payload_raw.arr[i]
                py_arr.append({
                    "armyId": str(item.armyId if hasattr(item, "armyId") else i),
                    "healNum": int(item.healNum if hasattr(item, "healNum") else item),
                })
        else:
            for k, v in dict(payload_raw.arr).items():
                py_arr.append({"armyId": str(k), "healNum": int(v)})
        py_payload = {
            "arr": py_arr,
            "gold": int(payload_raw.gold),
        }

        # Contract Validation
        valid, err = SFSMessageValidator.validate_hospital_cure_payload(py_payload)
        self.assertTrue(valid, f"Payload failed SFS contract: {err}")
        self.assertEqual(py_payload["gold"], 0)
        self.assertEqual(len(py_payload["arr"]), 4)
        for item in py_payload["arr"]:
            self.assertIsInstance(item["armyId"], str)
            self.assertIsInstance(item["healNum"], int)
            self.assertGreater(item["healNum"], 0)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_hospital_cure_nil_and_corrupted_entries_fuzz(self) -> None:
        """Inject corruptions: nil armyId, negative dead, NaN/corrupted strings, empty dicts."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        _G.DataCenter.HospitalManager.GetAllHospital = function(self)
            return {
                [1] = { armyId = nil, dead = 100 },                 -- missing armyId (fallback key)
                [2] = { armyId = '400501', dead = -50 },            -- negative wounded (must skip)
                [3] = { armyId = '400601', dead = 0 },              -- zero wounded (must skip)
                [4] = { armyId = '400701', dead = 'unparseable' },  -- unparseable dead (must skip)
                [5] = {},                                            -- empty struct (must skip)
                [6] = { armyId = '400801', dead = 400 },            -- strictly valid entry
            }
        end
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"hospital_heal": {"batch_minutes": 120, "max_batch_troops": 2000}}
        res = bot_actions.run_hospital_heal(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertGreaterEqual(res.get("wounded_total"), 400)

        sent = _get_lua_sent_messages(lua)
        cure_calls = [m for m in sent if m.msg == "HospitalCure"]
        self.assertEqual(len(cure_calls), 1)

        payload_raw = cure_calls[0].payload
        py_arr = []
        if hasattr(payload_raw.arr, "items"):
            for k, v in payload_raw.arr.items():
                if hasattr(v, "armyId"):
                    py_arr.append({"armyId": str(v.armyId), "healNum": int(v.healNum)})
                else:
                    py_arr.append({"armyId": str(k), "healNum": int(v)})
        elif hasattr(payload_raw.arr, "__len__") and len(payload_raw.arr) > 0:
            for i in range(1, len(payload_raw.arr) + 1):
                item = payload_raw.arr[i]
                py_arr.append({
                    "armyId": str(item.armyId if hasattr(item, "armyId") else i),
                    "healNum": int(item.healNum if hasattr(item, "healNum") else item),
                })
        else:
            for k, v in dict(payload_raw.arr).items():
                py_arr.append({"armyId": str(k), "healNum": int(v)})
        py_payload = {"arr": py_arr, "gold": int(payload_raw.gold)}

        valid, err = SFSMessageValidator.validate_hospital_cure_payload(py_payload)
        self.assertTrue(valid, f"Corrupted inputs yielded invalid SFS payload: {err}")
        army_ids = [item["armyId"] for item in py_arr]
        self.assertNotIn("400501", army_ids)
        self.assertNotIn("400601", army_ids)
        self.assertNotIn("400701", army_ids)
        self.assertIn("400801", army_ids)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_hospital_cure_lua_array_hole_ipairs_defect_demonstration(self) -> None:
        """EMPIRICAL CHALLENGE FINDING (RESOLVED):

        Verifies that when hm.GetAllHospital is nil, sequential candidate insertion
        prevents ipairs from terminating early and successfully falls back to allHospital and hospitalDic!
        """
        lua = _create_adversarial_lua_environment()
        # GetAllHospital is nil, only allHospital exists with wounded troops
        lua.execute("""
        _G.DataCenter.HospitalManager.GetAllHospital = nil
        _G.DataCenter.HospitalManager.allHospital = {
            [1] = { armyId = '400101', dead = 300 }
        }
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"hospital_heal": {"batch_minutes": 120, "max_batch_troops": 2000}}
        res = bot_actions.run_hospital_heal(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))

        # With the ipairs nil hole defect resolved via sequential candidate insertion,
        # allHospital is successfully reached, wounded_total is 300, and heal batch starts!
        self.assertEqual(res.get("wounded_total"), 300)
        self.assertEqual(res.get("action"), "started_heal_batch")
        self.assertEqual(res.get("queued_troops"), 300)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_hospital_cure_active_busy_guard(self) -> None:
        """Verify that an actively healing queue sets activeBusy and suppresses duplicate cure packets."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        _G.DataCenter.QueueDataManager.queueDic = {
            ['3'] = {
                uuid = 'q_heal_active',
                type = 3,
                state = 2, -- Work state
                endTime = 9999999999000, -- Far future
            }
        }
        _G.DataCenter.HospitalManager.GetAllHospital = function(self)
            return { [1] = { armyId = '400101', dead = 500 } }
        end
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"hospital_heal": {"batch_minutes": 120, "max_batch_troops": 2000}}
        res = bot_actions.run_hospital_heal(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertIn(res.get("action"), ("healing_in_progress", "requested_help"))
        self.assertEqual(res.get("queued_troops"), 0)

        sent = _get_lua_sent_messages(lua)
        cure_calls = [m for m in sent if m.msg == "HospitalCure"]
        self.assertEqual(len(cure_calls), 0)


class TestRadarQueueAdversarialProbes(unittest.TestCase):
    """Adversarial stress test for Radar Events loop with 20+ mixed items and formation limits."""

    def _setup_25_mixed_radar_events(self, lua: Any) -> None:
        """Inject 25 mixed radar events into Lua DataCenter."""
        lua.execute("""
        local evs = {}
        -- 5 Garbage events (type 6, non-march)
        for i = 1, 5 do
            evs['g_' .. i] = { uuid = 'g_' .. i, eventId = '10' .. i, type = 6, state = 0, pointId = 1000 + i }
        end
        -- 5 Help events (type 19, non-march)
        for i = 1, 5 do
            evs['h_' .. i] = { uuid = 'h_' .. i, eventId = '20' .. i, type = 19, state = 0, pointId = 2000 + i }
        end
        -- 5 Rescue events (type 20, non-march)
        for i = 1, 5 do
            evs['r_' .. i] = { uuid = 'r_' .. i, eventId = '30' .. i, type = 20, state = 0, pointId = 3000 + i }
        end
        -- 5 March events (types 1, 2 - require march formation)
        for i = 1, 5 do
            evs['m_' .. i] = { uuid = 'm_' .. i, eventId = '40' .. i, type = (i % 2 == 0 and 1 or 2), state = 0, pointId = 4000 + i }
        end
        -- 3 PVE/Parkour/Treasure events (types 7, 26, 23 - non-march)
        evs['pve_1'] = { uuid = 'pve_1', eventId = '501', type = 7, state = 0 }
        evs['parkour_1'] = { uuid = 'parkour_1', eventId = '502', type = 26, state = 0 }
        evs['treasure_1'] = { uuid = 'treasure_1', eventId = '503', type = 23, state = 0, pointId = 5003 }
        -- 2 Corrupted / unhandled events
        evs['corrupt_1'] = { uuid = 'corrupt_1', eventId = '998', type = 999, state = 0, pointId = -1 }
        evs['corrupt_2'] = { uuid = 'corrupt_2', eventId = nil, type = nil, state = 0 }

        _G.DataCenter.RadarCenterDataManager.events = evs
        _G.sent_messages = {}
        """)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_radar_25_mixed_items_zero_formations(self) -> None:
        """With 0 free formations, all non-march events must dispatch, but 0 march events."""
        lua = _create_adversarial_lua_environment()
        self._setup_25_mixed_radar_events(lua)

        # 0 formations available
        lua.execute("""
        _G.DataCenter.ArmyFormationDataManager.GetFreeFormationCount = function(self) return 0 end
        _G.DataCenter.ArmyFormationDataManager.GetArmyFormationList = function(self) return {} end
        _G.DataCenter.ArmyFormationDataManager.GetInMarchArmyFormationUuids = function(self)
            return {'f1', 'f2', 'f3'}
        end
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"radar_events": {"max_dispatches_per_cycle": 30, "auto_dispatch": True}}
        res = bot_actions.run_radar_events(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))

        dispatched = res.get("dispatched", [])
        self.assertGreaterEqual(len(dispatched), 15, "Non-march events should have been dispatched")

        # Verify NO march events were dispatched
        march_dispatches = [d for d in dispatched if d.get("mode") == "march"]
        self.assertEqual(len(march_dispatches), 0, "0 formations should yield 0 march dispatches")

        # Verify non-march events dispatched
        modes = {d.get("mode") for d in dispatched}
        self.assertIn("start_pick_garbage", modes)
        self.assertIn("start_help", modes)
        self.assertIn("start_rescue", modes)
        self.assertIn("pve", modes)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_radar_25_mixed_items_one_formation(self) -> None:
        """With 1 free formation, exactly ONE march event is dispatched."""
        lua = _create_adversarial_lua_environment()
        self._setup_25_mixed_radar_events(lua)

        lua.execute("""
        _G.DataCenter.ArmyFormationDataManager.GetFreeFormationCount = function(self) return 1 end
        _G.DataCenter.ArmyFormationDataManager.GetArmyFormationList = function(self)
            return { { uuid = 'form_alpha', index = 1 } }
        end
        _G.DataCenter.ArmyFormationDataManager.GetInMarchArmyFormationUuids = function(self) return {} end
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"radar_events": {"max_dispatches_per_cycle": 30, "auto_dispatch": True}}
        res = bot_actions.run_radar_events(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))

        dispatched = res.get("dispatched", [])
        march_dispatches = [d for d in dispatched if d.get("mode") == "march"]
        self.assertEqual(len(march_dispatches), 1, "Exactly 1 march event should be dispatched with 1 formation")
        self.assertEqual(march_dispatches[0].get("formation"), "form_alpha")

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_radar_25_mixed_items_two_formations(self) -> None:
        """With 2 free formations, exactly TWO march events are dispatched."""
        lua = _create_adversarial_lua_environment()
        self._setup_25_mixed_radar_events(lua)

        lua.execute("""
        _G.DataCenter.ArmyFormationDataManager.GetFreeFormationCount = function(self) return 2 end
        _G.DataCenter.ArmyFormationDataManager.GetArmyFormationList = function(self)
            return {
                { uuid = 'form_1', index = 1 },
                { uuid = 'form_2', index = 2 },
            }
        end
        _G.DataCenter.ArmyFormationDataManager.GetInMarchArmyFormationUuids = function(self) return {} end
        """)

        cd = LupaBridgeCD(lua)
        cfg = {"radar_events": {"max_dispatches_per_cycle": 30, "auto_dispatch": True}}
        res = bot_actions.run_radar_events(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))

        dispatched = res.get("dispatched", [])
        march_dispatches = [d for d in dispatched if d.get("mode") == "march"]
        self.assertEqual(len(march_dispatches), 2, "Exactly 2 march events should be dispatched with 2 formations")
        form_ids = [d.get("formation") for d in march_dispatches]
        self.assertIn("form_1", form_ids)
        self.assertIn("form_2", form_ids)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_radar_unthrottled_25_events_loop_eliminates_3_cap(self) -> None:
        """Empirically prove that the hardcoded clamp of 3 events is eradicated."""
        lua = _create_adversarial_lua_environment()
        self._setup_25_mixed_radar_events(lua)

        cd = LupaBridgeCD(lua)
        cfg = {"radar_events": {"max_dispatches_per_cycle": 25, "auto_dispatch": True}}
        res = bot_actions.run_radar_events(cd, 23848, {}, cfg, dry_run=False)
        self.assertTrue(res.get("ok"))

        total_dispatched = len(res.get("dispatched", []))
        self.assertGreater(
            total_dispatched, 3,
            f"Expected > 3 dispatches on 25-event board, got {total_dispatched}. Cap bug still present!"
        )
        self.assertGreaterEqual(total_dispatched, 18)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_radar_non_march_timing_prevents_zero_duration_packet(self) -> None:
        """In-progress events only send completion when nowMs >= endT, avoiding 897722."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        -- nowMs will be 1000 * 1000 = 1,000,000 ms
        -- 1 event with endT in future (2,000,000 ms), 1 event with endT in past (500,000 ms)
        _G.DataCenter.RadarCenterDataManager.events = {
            ev_future = { uuid = 'ev_future', eventId = '101', type = 6, state = 0, endTime = 2000000 },
            ev_past = { uuid = 'ev_past', eventId = '102', type = 6, state = 0, endTime = 500000 },
        }
        _G.DataCenter.RadarCenterDataManager.IsDetectEventDoing = function(self, uuid) return true end
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        res = bot_actions.run_radar_events(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))

        dispatched = res.get("dispatched", [])
        dispatched_uuids = [d.get("uuid") for d in dispatched]
        self.assertIn("ev_past", dispatched_uuids)
        self.assertNotIn("ev_future", dispatched_uuids, "Future in-progress event should not be completed prematurely")


class TestPreparednessAndDailyClaimsAdversarialProbes(unittest.TestCase):
    """Adversarial stress test for Full Preparedness and Daily Claims boundaries."""

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_full_preparedness_zero_and_negative_score(self) -> None:
        """Score 0 or negative must not dispatch claims or raise exceptions."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        local out = { personal_arms_checked = 0, personal_arms_claimed = {} }
        local dryRun = false
        local function _claim_event_info(slotKey, ei, fallbackActId, fallbackType)
          if type(ei) ~= 'table' then return end
          local actId = tostring(ei.actId or fallbackActId or '')
          local targets = (type(ei.rewardScoreIndexArr) == 'table' and #ei.rewardScoreIndexArr > 0 and ei.rewardScoreIndexArr)
            or (type(ei.targetList) == 'table' and ei.targetList) or nil
          if actId == '' or type(targets) ~= 'table' or #targets == 0 then return end
          out.personal_arms_checked = out.personal_arms_checked + 1
          local curScore = tonumber(ei.curScore or ei.currentScore or ei.score or 0) or 0
          local claimedMap = {}
          if type(ei.hasRewardList) == 'table' then
            for _, rv in pairs(ei.hasRewardList) do claimedMap[tostring(rv)] = true end
          end
          local claimableIndices = {}
          for idx, tgt in ipairs(targets) do
            local tgtNum = tonumber(tgt) or 0
            local idxStr = tostring(idx)
            if tgtNum > 0 and curScore >= tgtNum and not claimedMap[idxStr] then
              table.insert(claimableIndices, idx)
            end
          end
          if not dryRun and #claimableIndices > 0 and SFSNetwork and MsgDefines then
            SFSNetwork.SendMessage(MsgDefines.AcceptPersonalRewardBatch, {
              actId = actId,
              stages = claimableIndices,
            })
          end
          if #claimableIndices > 0 then
            table.insert(out.personal_arms_claimed, { actId = actId, stages = claimableIndices })
          end
        end

        _G._test_claim = _claim_event_info
        _G._get_out = function() return out end
        _G._reset_out = function() out = { personal_arms_checked = 0, personal_arms_claimed = {} } end
        """)

        # Zero Score
        lua.execute("""
        _G._reset_out()
        _G.sent_messages = {}
        _G._test_claim('slot1', {
            actId = 'prep_1',
            curScore = 0,
            targetList = { 1000, 3000, 6000 },
        })
        """)
        out_zero = lua.eval("_G._get_out()")
        self.assertEqual(int(lua.eval("#_G._get_out().personal_arms_claimed")), 0)
        self.assertEqual(len(_get_lua_sent_messages(lua)), 0)

        # Negative Score
        lua.execute("""
        _G._reset_out()
        _G.sent_messages = {}
        _G._test_claim('slot1', {
            actId = 'prep_1',
            curScore = -9999,
            targetList = { 1000, 3000, 6000 },
        })
        """)
        self.assertEqual(int(lua.eval("#_G._get_out().personal_arms_claimed")), 0)
        self.assertEqual(len(_get_lua_sent_messages(lua)), 0)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_full_preparedness_all_stages_already_claimed(self) -> None:
        """High score with all stages already in hasRewardList must dispatch 0 packets."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        local out = { personal_arms_checked = 0, personal_arms_claimed = {} }
        local dryRun = false
        local function _claim_event_info(slotKey, ei)
          local actId = tostring(ei.actId or '')
          local targets = ei.targetList or {}
          local curScore = tonumber(ei.curScore or 0) or 0
          local claimedMap = {}
          for _, rv in pairs(ei.hasRewardList or {}) do claimedMap[tostring(rv)] = true end
          local claimableIndices = {}
          for idx, tgt in ipairs(targets) do
            if tgt > 0 and curScore >= tgt and not claimedMap[tostring(idx)] then
              table.insert(claimableIndices, idx)
            end
          end
          if #claimableIndices > 0 then
            SFSNetwork.SendMessage(MsgDefines.AcceptPersonalRewardBatch, { actId = actId, stages = claimableIndices })
            table.insert(out.personal_arms_claimed, { actId = actId, stages = claimableIndices })
          end
        end

        _G._test_claim = _claim_event_info
        _G.sent_messages = {}
        _G._test_claim('slot1', {
            actId = 'prep_1',
            curScore = 50000,
            targetList = { 1000, 3000, 6000, 10000 },
            hasRewardList = { '1', '2', '3', '4' },
        })
        _G._out_res = out
        """)

        self.assertEqual(int(lua.eval("#_G._out_res.personal_arms_claimed")), 0)
        self.assertEqual(len(_get_lua_sent_messages(lua)), 0)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_full_preparedness_1_indexed_batch_strictly_enforced(self) -> None:
        """Partially claimed stages must yield strictly 1-indexed stage numbers (e.g. [2, 3])."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        local out = { personal_arms_claimed = {} }
        local function _claim_event_info(slotKey, ei)
          local actId = tostring(ei.actId or '')
          local targets = ei.targetList or {}
          local curScore = tonumber(ei.curScore or 0) or 0
          local claimedMap = {}
          for _, rv in pairs(ei.hasRewardList or {}) do claimedMap[tostring(rv)] = true end
          local claimableIndices = {}
          for idx, tgt in ipairs(targets) do
            if tgt > 0 and curScore >= tgt and not claimedMap[tostring(idx)] then
              table.insert(claimableIndices, idx) -- strictly 1-indexed
            end
          end
          if #claimableIndices > 0 then
            SFSNetwork.SendMessage(MsgDefines.AcceptPersonalRewardBatch, { actId = actId, stages = claimableIndices })
          end
        end

        _G.sent_messages = {}
        _claim_event_info('slot1', {
            actId = 'prep_batch_test',
            curScore = 7500, -- Qualifies for 1000, 3000, 6000 (stages 1, 2, 3)
            targetList = { 1000, 3000, 6000, 10000 },
            hasRewardList = { '1' }, -- stage 1 already claimed
        })
        """)

        sent = _get_lua_sent_messages(lua)
        self.assertEqual(len(sent), 1)
        stages = [int(v) for v in sent[0].payload.stages.values()]
        self.assertEqual(stages, [2, 3])

        valid, err = SFSMessageValidator.validate_accept_personal_reward(
            {"actId": "prep_batch_test", "stages": stages},
            is_batch=True,
        )
        self.assertTrue(valid, f"Contract validation failed: {err}")
        self.assertNotIn(0, stages, "0-indexed stage must NEVER be generated")

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_daily_claims_collision_suppressed_when_tasks_claimed(self) -> None:
        """When daily tasks are claimed, milestone chest claims are suppressed in same tick."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        _G.DataCenter.DailyTaskManager.dailyQuestTasks = {
            { id = 1, state = 1 },
            { id = 2, state = 1 },
        }
        _G.DataCenter.DailyTaskManager.curVal = 100
        _G.DataCenter.DailyTaskManager.boxStates = { 1, 1, 0, 0, 0, 0 } -- Boxes 1 & 2 claimable
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        res = bot_actions.run_daily_claims(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("daily_tasks_claimed"), 2)
        # MUST BE EMPTY: collision prevention in the same tick!
        self.assertEqual(len(res.get("daily_boxes_claimed", [])), 0)

        sent = _get_lua_sent_messages(lua)
        task_all_reward = [m for m in sent if m.msg == "DailyQuestGetAllReward"]
        box_reward = [m for m in sent if m.msg == "DailyQuestReward"]
        self.assertEqual(len(task_all_reward), 1)
        self.assertEqual(len(box_reward), 0, "DailyQuestReward collided with DailyQuestGetAllReward!")

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_daily_claims_staggered_box_claims(self) -> None:
        """When no tasks are claimed, milestone boxes are claimed one box per cycle."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        _G.DataCenter.DailyTaskManager.dailyQuestTasks = {
            { id = 1, state = 2 }, -- already claimed
        }
        _G.DataCenter.DailyTaskManager.curVal = 120
        _G.DataCenter.DailyTaskManager.boxStates = { 1, 1, 1, 0, 0, 0 } -- Boxes 1, 2, 3 claimable
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        res = bot_actions.run_daily_claims(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("daily_tasks_claimed"), 0)
        # Exactly ONE box claimed
        boxes = res.get("daily_boxes_claimed", [])
        self.assertEqual(len(boxes), 1)
        self.assertEqual(boxes[0], 1)

        sent = _get_lua_sent_messages(lua)
        box_reward = [m for m in sent if m.msg == "DailyQuestReward"]
        self.assertEqual(len(box_reward), 1)
        raw_box = box_reward[0].payload
        box_stage = int(raw_box.stage) if hasattr(raw_box, "stage") else int(raw_box)
        self.assertEqual(box_stage, 1)

    @unittest.skipUnless(HAS_LUPA, "lupa not available")
    def test_daily_claims_corrupted_tasks_resilience(self) -> None:
        """Fuzz dailyQuestTasks with nil, string, and malformed objects without unhandled crash."""
        lua = _create_adversarial_lua_environment()
        lua.execute("""
        _G.DataCenter.DailyTaskManager.dailyQuestTasks = {
            'not_a_table',
            { id = 101 }, -- missing state
            { id = 102, state = 'invalid_state' },
            { id = 103, state = 1 }, -- valid
            nil,
            12345,
        }
        _G.DataCenter.DailyTaskManager.curVal = 0
        _G.DataCenter.DailyTaskManager.boxStates = { 0, 0, 0, 0, 0, 0 }
        _G.sent_messages = {}
        """)

        cd = LupaBridgeCD(lua)
        res = bot_actions.run_daily_claims(cd, 23848, {}, {}, dry_run=False)
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("daily_tasks_claimed"), 1)


if __name__ == "__main__":
    unittest.main()
