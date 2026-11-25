"""Permanent Regression Test Suite for RSS Gathering & Map Kills Automation.

Covers all 4 verification layers with real execution:
1. TestRssAndMapKillsMegamindContracts:
   - RSS_RESOURCE_TYPE_IDS & aliases vs megamind/raw/xml tables/aps gather resource.json & localization en.json
   - FindResourcePoint (4), FindMonster (6), CallChallengeActBoss (2), MarchTargetType,
     MonsterSpecialType, AllianceTeamType, RoamingBossRewardType, and DataCenter managers
     against megamind/raw/*.json
2. TestRssAndMapKillsLuaBehavior:
   - lupa (Lua 5.4) execution of run_rss_gather_step, run_standalone_npc_step, run_boomer_runs,
     run_saga_kill_step, run_tyrant_event, run_furylord, and detect_map_kill_targets
3. TestContinuousFarmLoopEngine:
   - Real HubBackend continuous loop engine, state transitions, 4+1 search step-down,
     waiting while active_marches > 0, all_chain & boss prioritization, C1 phantom-dispatch
     rollback/blacklisting, atomic Stop+Start & per-PID lock, Saga 60s cooldown, multi-PID
     scoping, dry_run auto-stop, and shutdown()
4. TestRssAndMapKillsUiContracts:
   - #view-rss & #view-kills DOM cards/pills, Node.js execution of JS option clamping & scoping,
     zero duplicate HTML IDs, node --check exit 0, and zero prohibited terminology.
"""

from __future__ import annotations

import ast
import copy
import importlib
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
from typing import Any
from unittest.mock import patch

from lupa import LuaRuntime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ba = importlib.import_module("tools.bot actions")
mcb = importlib.import_module("tools.multi client bot")

MEGAMIND_RAW_DIR = PROJECT_ROOT / "megamind" / "raw"
INDEX_HTML_PATH = PROJECT_ROOT / "launcher" / "web" / "index.html"
HUB_PY_PATH = PROJECT_ROOT / "launcher" / "heinzhubweb.py"
BOT_ACTIONS_PY_PATH = PROJECT_ROOT / "tools" / "bot actions.py"


def _load_hub_module():
    mod_name = "test_hub_rss_kills_mod"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, str(HUB_PY_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {HUB_PY_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _read_json(rel_path: str) -> Any:
    return json.loads((MEGAMIND_RAW_DIR / rel_path).read_text(encoding="utf-8"))


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
    in_line_comment = False
    in_block_comment = False
    escaped = False
    n = len(html)
    idx = brace_start
    while idx < n:
        ch = html[idx]
        nxt = html[idx + 1] if idx + 1 < n else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            idx += 1
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                idx += 2
                continue
            idx += 1
            continue
        if in_str is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_str:
                in_str = None
            idx += 1
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            idx += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            idx += 2
            continue
        if ch in ('"', "'", "`"):
            in_str = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return html[start : idx + 1]
        idx += 1
    return html[start:]


# =============================================================================
# Lua 5.4 (lupa) World Harness for Layer 2 Behavioral Tests
# =============================================================================
class _LupaWorldMockCD:
    """MockCD executing real Lua chunks from tools/bot actions.py inside Lua 5.4 (lupa)."""

    def __init__(self) -> None:
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.eval_history: list[str] = []
        self._init_base_globals()

    def _init_base_globals(self) -> None:
        self.lua.execute(
            r"""
            _G._testState = {
                uid = '1001001',
                name = 'TestPlayer',
                serverId = 702,
                homeServerId = 702,
                mainPos = 450500, -- x=499, y=450
                stamina = 120,
                inWorld = true,
                inAlliance = true,
                allianceUid = 'ally_702',
                allianceAbbr = 'HZ1',
                freeFormations = 2,
                unlockFormations = 2,
                formations = {
                    { uuid = '10001', index = 1, state = 0, soldiers = 1000 },
                    { uuid = '10002', index = 2, state = 0, soldiers = 1000 },
                },
                inMarchUuids = {},
                myMarches = {},
                viewPoints = {},
                pointInfoById = {},
                findResPoint = 0,
                gatherRows = {
                    -- Diamonds (15)
                    ['305'] = { resource_type = 15, level = 5 },
                    ['308'] = { resource_type = 15, level = 8 },
                    ['310'] = { resource_type = 15, level = 10 },
                    ['311'] = { resource_type = 15, level = 11 },
                    ['312'] = { resource_type = 15, level = 12 },
                    ['314'] = { resource_type = 15, level = 14 },
                    ['315'] = { resource_type = 15, level = 15 },
                    -- Electricity (12)
                    ['508'] = { resource_type = 12, level = 8 },
                    -- Zent (14)
                    ['208'] = { resource_type = 14, level = 8 },
                    -- Wood (2)
                    ['405'] = { resource_type = 2, level = 5 },
                    ['408'] = { resource_type = 2, level = 8 },
                    -- Food (1)
                    ['115'] = { resource_type = 1, level = 15 },
                },
                monsterRows = {
                    ['1018'] = { boss = 0, special = 0, level = 18 },
                    ['1022'] = { boss = 0, special = 0, level = 22 },
                    ['1028'] = { boss = 0, special = 0, level = 28 },
                    ['2004'] = { boss = 1, special = 0, level = 4 },
                    ['2005'] = { boss = 1, special = 0, level = 5 },
                    ['2007'] = { boss = 1, special = 0, level = 7 },
                    ['3004'] = { boss = 0, special = 4, level = 20 },
                    ['3040'] = { boss = 1, special = 40, level = 25 },
                    ['4027'] = { boss = 1, special = 27, level = 30 },
                    ['4028'] = { boss = 1, special = 28, level = 35 },
                },
                maxNpcLevel = 25,
                maxBoomerFindLevel = 5,
                maxBoomerAtkLevel = 6,
                restBoomerKills = 8,
                allianceWars = {},
                alreadyJoinedWars = {},
                saga = {
                    activeInfo = nil,
                    allActs = nil,
                    endedByAct = {},
                    diffSelectedByAct = {},
                    canRally = false,
                    haveAlBoss = false,
                    alActInfoByAct = {},
                },
                tyrant = {
                    isOpen = false,
                    inBattle = false,
                    actId = 8001,
                    bossInfo = {},
                    canFreeReward = false,
                    canAllyReward = false,
                },
                furylord = {
                    isOpen = false,
                    inAct = false,
                    rewardCount = 0,
                    maxRewardCount = 4,
                    bossList = {},
                },
                -- Spy logs for assertions
                calls = {
                    sendCreateMarch = {},
                    sendMessage = {},
                    changeToWorld = 0,
                    joinRallyFallback = {},
                    autoAddSoldier = {},
                    tyrantFreeReward = 0,
                    furylordGetReward = 0,
                    furylordGetBossInfo = 0,
                },
            }

            _G.PointType = { WorldMonster = 4, WorldBoss = 5, WorldResource = 7 }
            _G.MarchTargetType = {
                ATTACK_MONSTER = 1,
                COLLECT = 2,
                JOIN_RALLY = 6,
                RALLY_FOR_BOSS = 7,
                ATTACK_ALLIANCE_BOSS = 53,
                RALLY_FOR_ALLIANCE_BOSS = 74,
                RALLY_FOR_ROAMING_BOSS = 93,
            }
            _G.MonsterSpecialType = {
                Normal = 0,
                ChallengeBoss = 4,
                RoamingBossNormal = 27,
                RoamingBossSpecial = 28,
                MonsterTowerAlBoss = 40,
            }
            _G.AllianceTeamType = {
                ATTACK_BOSS = 0,
                ATTACK_ALLIANCE_BOSS = 10,
                ATTACK_ROAMING_BOSS = 14,
            }
            _G.RoamingBossRewardType = { First = 1, Normal = 2, Special = 3, Join = 4 }
            _G.TableName = { GatherResource = 'aps_gather_resource', Monster = 'monster' }
            _G.MsgDefines = {
                FindResourcePoint = 'find.resource.point',
                FindMonster = 'find.monster',
                CallChallengeActBoss = 'call.challenge.act.boss',
                ReceiveAllianceBossAllianceReward = 'receive.alliance.boss.alliance.reward',
            }
            _G.ChatInterface = {}
            _G.BuildingTypes = { FUN_BUILD_MAIN = 400000 }
            _G.UITimeManager = {
                GetInstance = function()
                    return { GetServerSeconds = function() return 1700000000 end }
                end
            }
            _G.SceneManager = {
                IsInWorld = function(self) return _G._testState.inWorld end,
                ChangeToWorld = function(self)
                    _G._testState.calls.changeToWorld = _G._testState.calls.changeToWorld + 1
                    _G._testState.inWorld = true
                end,
            }
            _G.LuaEntry = {
                Player = {
                    GetUid = function(self) return _G._testState.uid end,
                    GetName = function(self) return _G._testState.name end,
                    GetCurServerId = function(self) return _G._testState.serverId end,
                    GetSelfServerId = function(self) return _G._testState.homeServerId end,
                    GetMainWorldPos = function(self) return _G._testState.mainPos end,
                    GetCurStamina = function(self) return _G._testState.stamina end,
                    IsInAlliance = function(self) return _G._testState.inAlliance end,
                    GetAllianceUid = function(self) return _G._testState.allianceUid end,
                    GetAllianceAbbr = function(self) return _G._testState.allianceAbbr end,
                    GetPower = function(self) return 15000000 end,
                }
            }
            _G.LocalController = {
                instance = function()
                    return {
                        getLine = function(self, tblName, key)
                            local rowTbl = nil
                            if tblName == _G.TableName.GatherResource then
                                rowTbl = _G._testState.gatherRows[tostring(key)]
                            elseif tblName == _G.TableName.Monster then
                                rowTbl = _G._testState.monsterRows[tostring(key)]
                            end
                            if not rowTbl then return nil end
                            return {
                                getValue = function(r, col)
                                    return rowTbl[tostring(col)]
                                end
                            }
                        end
                    }
                end
            }
            _G.SFSNetwork = {
                SendMessage = function(cmd, ...)
                    local n = select('#', ...)
                    local args = {}
                    for i = 1, n do args[i] = select(i, ...) end
                    table.insert(_G._testState.calls.sendMessage, {
                        cmd = cmd,
                        args = args,
                        nargs = n + 1, -- total args incl. cmd
                    })
                end
            }
            _G.MarchUtil = {
                SendCreateMarchMessage = function(formUuid, marchType, ptId, extraId, rallyFlag, a6, a7, srvId)
                    table.insert(_G._testState.calls.sendCreateMarch, {
                        formUuid = formUuid,
                        marchType = marchType,
                        ptId = ptId,
                        extraId = extraId,
                        rallyFlag = rallyFlag,
                        a6 = a6,
                        a7 = a7,
                        srvId = srvId,
                    })
                end,
                CheckWorldPointHasMyTroop = function(pt)
                    return false
                end,
            }
            _G.PBController = {
                ParsePbFromBytes = function(pbType, raw)
                    if type(raw) == 'table' then return raw end
                    return nil
                end
            }
            _G.DataCenter = {
                BuildManager = { MainLv = 25 },
                ArmyFormationDataManager = {
                    GetFreeFormationCount = function(self) return _G._testState.freeFormations end,
                    GetUnlockFormationCount = function(self) return _G._testState.unlockFormations end,
                    GetArmyFormationList = function(self) return _G._testState.formations end,
                    GetInMarchArmyFormationUuids = function(self) return _G._testState.inMarchUuids end,
                    GetInMarchArmyFormationCount = function(self)
                        local c = 0
                        for _ in pairs(_G._testState.inMarchUuids) do c = c + 1 end
                        return c
                    end,
                    GetCurSoldierNum = function(self, uuid)
                        for _, f in ipairs(_G._testState.formations) do
                            if tostring(f.uuid) == tostring(uuid) then
                                return tonumber(f.soldiers or 0) or 0
                            end
                        end
                        return 0
                    end,
                    AutoAddSoldier = function(self, uuid)
                        table.insert(_G._testState.calls.autoAddSoldier, tostring(uuid))
                    end,
                },
                WorldMyMarchDataManager = {
                    GetAllMarches = function(self) return _G._testState.myMarches end,
                },
                WorldPointManager = {
                    allViewPoints = _G._testState.viewPoints,
                    GetPointInfo = function(self, pnum)
                        return _G._testState.pointInfoById[tonumber(pnum)] or _G._testState.viewPoints[tonumber(pnum)]
                    end,
                },
                CollectResourceManager = {
                    GetFindResPoint = function(self) return _G._testState.findResPoint end,
                },
                MonsterManager = {
                    GetCanFindMonsterMaxLevel = function(self) return _G._testState.maxNpcLevel end,
                    GetCanFindBossMaxLevel = function(self, kind) return _G._testState.maxBoomerFindLevel end,
                    GetCurCanAttackBossMaxLevel = function(self) return _G._testState.maxBoomerAtkLevel end,
                    GetRestKillBossNum = function(self) return _G._testState.restBoomerKills end,
                },
                AllianceWarDataManager = {
                    GetAllAllianceWar = function(self) return _G._testState.allianceWars end,
                    HasRallyFormationForInfo = function(self, w)
                        return _G._testState.alreadyJoinedWars[tostring(w and w.uuid or '')] and true or false
                    end,
                    JoinRally = function(self, warUuid)
                        table.insert(_G._testState.calls.joinRallyFallback, tostring(warUuid))
                    end,
                },
                ActMonsterTowerData = {
                    GetActiveChallengeInfo = function(self) return _G._testState.saga.activeInfo end,
                    GetInfoActAll = function(self) return _G._testState.saga.allActs end,
                    CheckIfIsToEnd = function(self, actId)
                        return _G._testState.saga.endedByAct[tonumber(actId)] and true or false
                    end,
                    HasSelectedDifficulty = function(self, actId)
                        return _G._testState.saga.diffSelectedByAct[tonumber(actId)] and true or false
                    end,
                    CanShowChallengeBossRally = function(self) return _G._testState.saga.canRally end,
                    CheckHaveAlBossAct = function(self) return _G._testState.saga.haveAlBoss end,
                    GetAllianceActInfo = function(self, actId) return _G._testState.saga.alActInfoByAct[tonumber(actId)] end,
                },
                AllianceBossManager = {
                    IsAllianceBossActivityOpen = function(self) return _G._testState.tyrant.isOpen end,
                    GetIsInBattle = function(self) return _G._testState.tyrant.inBattle end,
                    GetCurrActivityId = function(self) return _G._testState.tyrant.actId end,
                    GetBossInfo = function(self) return _G._testState.tyrant.bossInfo end,
                    GetIsFreeRewardCanReceive = function(self) return _G._testState.tyrant.canFreeReward end,
                    CanReceivedAllianceReward = function(self) return _G._testState.tyrant.canAllyReward end,
                    OnSendReceiveAllianceBossFreeRewardMessage = function(self)
                        _G._testState.calls.tyrantFreeReward = _G._testState.calls.tyrantFreeReward + 1
                    end,
                },
                ActRoamingBossManager = {
                    IsActOpen = function(self) return _G._testState.furylord.isOpen end,
                    IsInAct = function(self) return _G._testState.furylord.inAct end,
                    GetBossRewardCount = function(self, rType) return _G._testState.furylord.rewardCount end,
                    GetMaxBossRewardCount = function(self, rType) return _G._testState.furylord.maxRewardCount end,
                    GetBossInfoListNew = function(self) return _G._testState.furylord.bossList end,
                    SendGetBossReward = function(self, arg)
                        _G._testState.calls.furylordGetReward = _G._testState.calls.furylordGetReward + 1
                    end,
                    SendGetBossInfo = function(self)
                        _G._testState.calls.furylordGetBossInfo = _G._testState.calls.furylordGetBossInfo + 1
                    end,
                },
            }
            """
        )

    def frida_eval_lua(self, pid: int, lua_code: str, timeout: float = 8.0) -> tuple[bool, str]:
        self.eval_history.append(lua_code)
        raw = self.lua.execute(lua_code)
        return True, str(raw)

    def seed_hq_viewpoint(self, pt: int = 450500) -> None:
        self.lua.execute(
            f"""
            local pt = {int(pt)}
            local info = {{ pointType = 6, pointIndex = pt, mainIndex = pt }}
            _G._testState.pointInfoById[pt] = info
            _G._testState.viewPoints[pt] = info
            """
        )

    def add_resource_point(
        self,
        pt: int,
        resource_id: int,
        *,
        gather_uuid: int = 0,
        owner_uid: str = "",
        in_viewport: bool = True,
    ) -> None:
        self.lua.execute(
            f"""
            local pt = {int(pt)}
            local info = {{
                pointType = _G.PointType.WorldResource,
                pointIndex = pt,
                mainIndex = pt,
                resourceInfo = {{
                    resourceId = {int(resource_id)},
                    gatherUuid = {int(gather_uuid)},
                    ownerUid = {json.dumps(str(owner_uid))},
                }},
            }}
            _G._testState.pointInfoById[pt] = info
            if {str(in_viewport).lower()} then
                _G._testState.viewPoints[pt] = info
            end
            """
        )

    def add_monster_point(
        self,
        pt: int,
        monster_id: int,
        *,
        uuid: int = 500001,
        boss_owner_uid: str = "",
        alliance_id: str = "",
    ) -> None:
        self.lua.execute(
            f"""
            local pt = {int(pt)}
            local info = {{
                pointType = _G.PointType.WorldMonster,
                pointIndex = pt,
                mainIndex = pt,
                uuid = {int(uuid)},
                _parsedExtra = {{
                    monsterId = {int(monster_id)},
                    uuid = {int(uuid)},
                    bossOwnerUid = {json.dumps(str(boss_owner_uid))},
                    allianceId = {json.dumps(str(alliance_id))},
                }},
            }}
            _G._testState.pointInfoById[pt] = info
            _G._testState.viewPoints[pt] = info
            """
        )

    def get_calls(self, key: str) -> list[dict[str, Any]] | int:
        val = self.lua.eval(f"_G._testState.calls.{key}")
        if isinstance(val, (int, float)):
            return int(val)
        out: list[dict[str, Any]] = []
        if val is not None:
            for i in range(1, len(val) + 1):
                item = val[i]
                if hasattr(item, "items"):
                    d: dict[str, Any] = {}
                    for k, v in item.items():
                        if hasattr(v, "items"):
                            d[str(k)] = [v[j] for j in range(1, len(v) + 1)]
                        else:
                            d[str(k)] = v
                    out.append(d)
                else:
                    out.append({"value": item})
        return out


# =============================================================================
# Layer 1: Megamind Protocol & Resource Parity Contracts
# =============================================================================
class TestRssAndMapKillsMegamindContracts(unittest.TestCase):
    """Tier 1: Verify bot actions & Hub protocol/resource constants against megamind/raw/*.json."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.hub = _load_hub_module()
        cls.aps_gather = _read_json("xml tables/aps gather resource.json")
        cls.loc_en = _read_json("localization en.json")["strings"]
        cls.enums = _read_json("enums complete.json")["enums"]
        cls.packets_data = _read_json("packets complete.json")
        cls.dc_managers = _read_json("datacenter managers.json")

    def test_rss_resource_type_ids_and_levels_match_aps_gather_resource_and_localization(self) -> None:
        """Verify RSS_RESOURCE_TYPE_IDS (15/12/14/2/1) match aps gather resource.json & localization en.json."""
        expected_ids = {
            "Diamonds": 15,
            "Electricity": 12,
            "Zent": 14,
            "Wood": 2,
            "Food": 1,
        }
        self.assertEqual(ba.RSS_RESOURCE_TYPE_IDS, expected_ids)
        self.assertEqual(ba.RSS_RESOURCE_ID_TO_NAME, {v: k for k, v in expected_ids.items()})
        self.assertEqual(ba.RESOURCE_TYPE_NAMES, ba.RSS_RESOURCE_ID_TO_NAME)
        self.assertEqual(
            self.hub.HubBackend._VALID_RSS_LOOP_MODES,
            ("diamonds", "electricity", "zent", "wood", "food", "priority_queue"),
        )

        cols = self.aps_gather["columns"]
        rt_idx = cols.index("resource_type")
        lv_idx = cols.index("level")
        name_idx = cols.index("name")

        by_type_names: dict[int, set[str]] = {}
        by_type_levels: dict[int, set[int]] = {}
        for row in self.aps_gather["rows"].values():
            rt = int(row[rt_idx])
            lv = int(row[lv_idx])
            loc_key = str(row[name_idx])
            loc_name = str(self.loc_en.get(loc_key, ""))
            by_type_names.setdefault(rt, set()).add(loc_name)
            by_type_levels.setdefault(rt, set()).add(lv)

        expected_loc_names = {
            15: "Diamond",
            12: "Power Plant",
            14: "Zent Mine",
            2: "Wood",
            1: "Farmland",
        }
        for canonical_name, rt_id in expected_ids.items():
            self.assertIn(rt_id, by_type_names, f"Missing resource_type={rt_id} ({canonical_name}) in aps gather resource.json")
            self.assertIn(expected_loc_names[rt_id], by_type_names[rt_id])
            if rt_id == 15:
                self.assertEqual(max(by_type_levels[rt_id]), 15)
            else:
                self.assertEqual(max(by_type_levels[rt_id]), 10)
            self.assertEqual(min(by_type_levels[rt_id]), 1)

    def test_normalize_rss_resource_name_aliases_and_priority_resolution(self) -> None:
        """Verify normalize_rss_resource_name handles canonical names, legacy aliases, numeric IDs, and invalid inputs."""
        cases = {
            "Diamonds": "Diamonds",
            "diamonds": "Diamonds",
            "diamond": "Diamonds",
            "gold": "Diamonds",
            "gem": "Diamonds",
            "gems": "Diamonds",
            "15": "Diamonds",
            15: "Diamonds",
            "Electricity": "Electricity",
            "power": "Electricity",
            "power plant": "Electricity",
            "power_plant": "Electricity",
            "power-plant": "Electricity",
            "powerplant": "Electricity",
            "elec": "Electricity",
            "12": "Electricity",
            12: "Electricity",
            "Zent": "Zent",
            "zent mine": "Zent",
            "zent_mine": "Zent",
            "zentmine": "Zent",
            "money": "Zent",
            "cash": "Zent",
            "coin": "Zent",
            "coins": "Zent",
            "mine": "Zent",
            "14": "Zent",
            14: "Zent",
            "Wood": "Wood",
            "lumber": "Wood",
            "lumberyard": "Wood",
            "timber": "Wood",
            "2": "Wood",
            2: "Wood",
            "Food": "Food",
            "farmland": "Food",
            "farm": "Food",
            "metal": "Food",
            "oil": "Food",
            "steel": "Food",
            "iron": "Food",
            "1": "Food",
            "0": "Food",
            1: "Food",
            0: "Food",
        }
        for raw_val, expected in cases.items():
            self.assertEqual(ba.normalize_rss_resource_name(raw_val), expected, f"Failed alias: {raw_val!r}")

        for bad_val in (None, "", "   ", True, False, 999, "uranium", -1):
            self.assertEqual(ba.normalize_rss_resource_name(bad_val), "", f"Expected empty for {bad_val!r}")

        # Priority deduplication & comma-separated parsing
        self.assertEqual(
            ba._resolve_rss_resource_list("gold, power plant, diamond, timber, steel"),
            ["Diamonds", "Electricity", "Wood", "Food"],
        )
        self.assertEqual(
            ba._resolve_rss_resource_list(None, resource_types=["14", "zent", "1"]),
            ["Zent", "Food"],
        )

    def test_sfs_packet_contracts_against_megamind_packets_complete(self) -> None:
        """Verify FindResourcePoint (4), FindMonster (6), and CallChallengeActBoss (2) against packets complete.json."""
        msg_defs = self.packets_data["msg_defines"]
        packets = self.packets_data["packets"]

        # FindResourcePoint (nparams=4)
        self.assertEqual(msg_defs.get("FindResourcePoint"), "find.resource.point")
        frp = packets["find.resource.point"]
        self.assertIn("FindResourcePoint", frp.get("aliases", []))
        self.assertEqual(frp["outgoing"]["nparams"], 4)
        for tok in ("type", "level", "param", "PutInt", "PutUtfString"):
            self.assertIn(tok, frp["outgoing"]["tokens"])
        self.assertIn("SetFindResPoint", frp["incoming"]["tokens"])
        self.assertIn("CollectResourceManager", frp["incoming"]["tokens"])

        # FindMonster (nparams=6)
        self.assertEqual(msg_defs.get("FindMonster"), "find.monster")
        fm = packets["find.monster"]
        self.assertIn("FindMonster", fm.get("aliases", []))
        self.assertEqual(fm["outgoing"]["nparams"], 6)
        for tok in ("pointId", "level", "isBoss", "searchRange", "special", "PutInt", "PutBool"):
            self.assertIn(tok, fm["outgoing"]["tokens"])

        # CallChallengeActBoss (nparams=2)
        self.assertEqual(msg_defs.get("CallChallengeActBoss"), "call.challenge.act.boss")
        ccab = packets["call.challenge.act.boss"]
        self.assertIn("CallChallengeActBoss", ccab.get("aliases", []))
        self.assertEqual(ccab["outgoing"]["nparams"], 2)
        for tok in ("activityId", "PutInt"):
            self.assertIn(tok, ccab["outgoing"]["tokens"])

    def test_protocol_enums_against_megamind_enums_complete(self) -> None:
        """Verify MarchTargetType, MonsterSpecialType, AllianceTeamType, RoamingBossRewardType, WorldPointType."""
        mtt = self.enums["MarchTargetType"]
        self.assertEqual(mtt["ATTACK_MONSTER"], 1)
        self.assertEqual(mtt["COLLECT"], 2)
        self.assertEqual(mtt["JOIN_RALLY"], 6)
        self.assertEqual(mtt["RALLY_FOR_BOSS"], 7)
        self.assertEqual(mtt["ATTACK_ALLIANCE_BOSS"], 53)
        self.assertEqual(mtt["RALLY_FOR_ALLIANCE_BOSS"], 74)
        self.assertEqual(mtt["RALLY_FOR_ROAMING_BOSS"], 93)

        mst = self.enums["MonsterSpecialType"]
        self.assertEqual(mst["Normal"], 0)
        self.assertEqual(mst["ChallengeBoss"], 4)
        self.assertEqual(mst["RoamingBossNormal"], 27)
        self.assertEqual(mst["RoamingBossSpecial"], 28)
        self.assertEqual(mst["MonsterTowerAlBoss"], 40)

        att = self.enums["AllianceTeamType"]
        self.assertEqual(att["ATTACK_BOSS"], 0)
        self.assertEqual(att["ATTACK_ALLIANCE_BOSS"], 10)
        self.assertEqual(att["ATTACK_ROAMING_BOSS"], 14)

        rbrt = self.enums["RoamingBossRewardType"]
        self.assertEqual(rbrt["Normal"], 2)

        wpt = self.enums["WorldPointType"]
        self.assertEqual(wpt["WorldMonster"], 4)
        self.assertEqual(wpt["WorldResource"], 7)

    def test_datacenter_manager_methods_against_megamind_datacenter_managers(self) -> None:
        """Verify all DataCenter & global manager methods used by RSS/Map Kills exist in datacenter managers.json."""
        dc = self.dc_managers["datacenter"]
        gs = self.dc_managers["globals_singletons"]

        def _method_map(container: dict[str, Any], name: str) -> dict[str, int]:
            return {m["name"]: int(m["nparams"]) for m in container[name]["methods"]}

        crm_m = _method_map(dc, "CollectResourceManager")
        self.assertEqual(crm_m["GetFindResPoint"], 1)

        mm_m = _method_map(dc, "MonsterManager")
        self.assertEqual(mm_m["GetCanFindMonsterMaxLevel"], 1)
        self.assertEqual(mm_m["GetCanFindBossMaxLevel"], 2)
        self.assertEqual(mm_m["GetCurCanAttackBossMaxLevel"], 1)
        self.assertEqual(mm_m["GetRestKillBossNum"], 1)

        mtd_m = _method_map(dc, "ActMonsterTowerData")
        for m_name, nparams in (
            ("GetActiveChallengeInfo", 1),
            ("GetInfoActAll", 1),
            ("CheckIfIsToEnd", 2),
            ("HasSelectedDifficulty", 2),
            ("CanShowChallengeBossRally", 1),
            ("CheckHaveAlBossAct", 1),
            ("GetAllianceActInfo", 2),
        ):
            self.assertEqual(mtd_m[m_name], nparams)

        abm_m = _method_map(dc, "AllianceBossManager")
        for m_name, nparams in (
            ("IsAllianceBossActivityOpen", 1),
            ("GetIsInBattle", 1),
            ("GetCurrActivityId", 1),
            ("GetBossInfo", 1),
            ("GetIsFreeRewardCanReceive", 1),
            ("CanReceivedAllianceReward", 1),
        ):
            self.assertEqual(abm_m[m_name], nparams)

        rbm_m = _method_map(dc, "ActRoamingBossManager")
        for m_name, nparams in (
            ("IsActOpen", 1),
            ("IsInAct", 1),
            ("GetBossRewardCount", 2),
            ("GetMaxBossRewardCount", 2),
            ("GetBossInfoListNew", 1),
            ("SendGetBossReward", 2),
            ("SendGetBossInfo", 1),
        ):
            self.assertEqual(rbm_m[m_name], nparams)

        mu_m = _method_map(gs, "MarchUtil")
        self.assertEqual(mu_m["SendCreateMarchMessage"], 13)

    def test_step_contract_and_task_handlers_registration(self) -> None:
        """Verify TASK_HANDLERS exposes all RSS & Map Kills actions and _ensure_step_contract enforces invariants."""
        for key in ("rss_gather", "standalone_npc", "saga_boss", "boomer_runs", "tyrant_event", "furylord"):
            self.assertIn(key, ba.TASK_HANDLERS)
            self.assertTrue(callable(ba.TASK_HANDLERS[key]))

        # Non-physical status clears stop_reason; physical_limit preserves stop_reason
        ok_disp = ba._ensure_step_contract({"ok": True, "dispatched": [{"pointId": 100}], "stop_reason": "stale"}, task_name="rss_gather")
        self.assertEqual(ok_disp["status"], "dispatched")
        self.assertEqual(ok_disp["dispatched_count"], 1)
        self.assertEqual(ok_disp["stop_reason"], "")

        limit = ba._ensure_step_contract({"ok": True, "status": "physical_limit", "reason": "out_of_stamina"}, task_name="boomer_runs")
        self.assertEqual(limit["status"], "physical_limit")
        self.assertEqual(limit["stop_reason"], "out_of_stamina")


# =============================================================================
# Layer 2: lupa-Backed Lua Behavioral Tests
# =============================================================================
class TestRssAndMapKillsLuaBehavior(unittest.TestCase):
    """Tier 1: Real Lua 5.4 (lupa) behavioral tests of tools/bot actions.py world actions."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.daily_state_path = str(Path(self._tmp.name) / "daily_task_state.json")
        self.cd = _LupaWorldMockCD()
        self.pid = 99001

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_rss_gather_dispatches_highest_unoccupied_and_skips_occupied_self_blacklisted(self) -> None:
        """Verify run_rss_gather_step picks highest unoccupied tile, skips occupied/self/blacklisted, and honors priority."""
        self.cd.add_resource_point(451501, 315, gather_uuid=88001, owner_uid="ally_99")  # Lv15 occupied (gatherUuid)
        self.cd.add_resource_point(451502, 314, gather_uuid=0, owner_uid="enemy_77")    # Lv14 occupied (ownerUid)
        self.cd.add_resource_point(451503, 312, gather_uuid=0, owner_uid="")            # Lv12 self-march target
        self.cd.add_resource_point(451504, 311, gather_uuid=0, owner_uid="")            # Lv11 blacklisted
        self.cd.add_resource_point(451505, 308, gather_uuid=0, owner_uid="")            # Lv8 Diamonds unoccupied
        self.cd.add_resource_point(451506, 310, gather_uuid=0, owner_uid="")            # Lv10 Diamonds unoccupied (best valid!)
        self.cd.add_resource_point(451507, 115, gather_uuid=0, owner_uid="")            # Lv15 Food (wrong resource)

        self.cd.lua.execute(
            """
            _G._testState.freeFormations = 1
            _G._testState.unlockFormations = 2
            _G._testState.formations = {
                { uuid = '10001', index = 1, state = 0, soldiers = 1000 },
                { uuid = '10002', index = 2, state = 1, soldiers = 1000 },
            }
            _G._testState.inMarchUuids = { ['10002'] = true }
            _G._testState.myMarches = { { targetPos = 451503 } }
            """
        )

        ctx: dict[str, Any] = {"blacklisted_points": ["451504"]}
        res = ba.run_rss_gather_step(
            self.cd,
            self.pid,
            {},
            {},
            resource_type="Diamonds",
            min_level=1,
            max_level=15,
            max_distance=150.0,
            reserve=0,
            dry_run=False,
            context=ctx,
        )

        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "dispatched")
        self.assertEqual(res["stop_reason"], "")
        self.assertEqual(res["dispatched_count"], 1)
        self.assertEqual(res["occupied_skipped"], 2)
        d0 = res["dispatched"][0]
        self.assertEqual(d0["pointId"], 451506)
        self.assertEqual(d0["level"], 10)
        self.assertEqual(d0["resourceType"], "Diamonds")
        self.assertEqual(d0["resourceTypeId"], 15)
        self.assertIn("702:451506", ctx["claimed_gather_points"])

        march_calls = self.cd.get_calls("sendCreateMarch")
        assert isinstance(march_calls, list)
        self.assertEqual(len(march_calls), 1)
        self.assertEqual(march_calls[0]["marchType"], 2)  # MarchTargetType.COLLECT
        self.assertEqual(march_calls[0]["ptId"], 451506)
        self.assertEqual(march_calls[0]["formUuid"], 10001)

        # Priority queue check: Diamonds (Lv8) beats higher-level Wood (Lv8 / Lv5) when Diamonds is ranked 1st
        cd2 = _LupaWorldMockCD()
        cd2.add_resource_point(451601, 408)  # Lv8 Wood
        cd2.add_resource_point(451602, 305)  # Lv5 Diamonds
        cd2.lua.execute("_G._testState.freeFormations = 1; _G._testState.unlockFormations = 1; _G._testState.formations = { { uuid = '10001', index = 1, state = 0, soldiers = 1000 } }")
        res_pq = ba.run_rss_gather_step(
            cd2,
            self.pid + 1,
            {},
            {},
            resource_types=["Diamonds", "Wood"],
            min_level=1,
            max_level=15,
            context={},
        )
        self.assertEqual(res_pq["status"], "dispatched")
        self.assertEqual(res_pq["dispatched"][0]["pointId"], 451602)
        self.assertEqual(res_pq["dispatched"][0]["resourceType"], "Diamonds")

    def test_rss_gather_find_res_point_and_positional_find_resource_point_search(self) -> None:
        """Verify CollectResourceManager:GetFindResPoint() dispatch & positional FindResourcePoint(resType, level, '')."""
        # Part A: GetFindResPoint() points to an unoccupied tile within max_distance, not in allViewPoints
        self.cd.seed_hq_viewpoint(450500)
        self.cd.add_resource_point(450520, 314, in_viewport=False)
        self.cd.lua.execute("_G._testState.findResPoint = 450520")

        res_frp = ba.run_rss_gather_step(
            self.cd,
            self.pid,
            {},
            {},
            resource_type="Diamonds",
            min_level=1,
            max_level=15,
            context={},
        )
        self.assertEqual(res_frp["status"], "dispatched")
        self.assertEqual(res_frp["find_res_point"], 450520)
        self.assertEqual(res_frp["dispatched"][0]["pointId"], 450520)
        self.assertTrue(res_frp["dispatched"][0]["fromFindRes"])
        self.assertEqual(self.cd.get_calls("sendMessage"), [])

        # Part B: Empty resource viewport & GetFindResPoint()==0 -> positional FindResourcePoint(resType=12, level=7, '')
        cd_empty = _LupaWorldMockCD()
        cd_empty.seed_hq_viewpoint(450500)
        res_search = ba.run_rss_gather_step(
            cd_empty,
            self.pid + 2,
            {},
            {},
            resource_type="Electricity",
            min_level=1,
            max_level=10,
            search_level=7,
            context={},
        )
        self.assertEqual(res_search["status"], "searching")
        self.assertTrue(res_search["searched"])
        self.assertEqual(res_search["searched_level"], 7)
        self.assertEqual(res_search["searched_resource_id"], 12)
        pkts = cd_empty.get_calls("sendMessage")
        assert isinstance(pkts, list)
        self.assertEqual(len(pkts), 1)
        self.assertEqual(pkts[0]["cmd"], "find.resource.point")
        self.assertEqual(pkts[0]["nargs"], 4)  # FindResourcePoint nparams=4
        self.assertEqual(pkts[0]["args"], [12, 7, ""])

        # Part C: Server just populated GetFindResPoint() from recent _G.__hzFindResReq before GetPointInfo loaded
        cd_empty.lua.execute("_G._testState.findResPoint = 450530")
        res_pending_ri = ba.run_rss_gather_step(
            cd_empty,
            self.pid + 2,
            {},
            {},
            resource_type="Electricity",
            min_level=1,
            max_level=10,
            search_level=7,
            context={},
        )
        self.assertEqual(res_pending_ri["status"], "dispatched")
        self.assertEqual(res_pending_ri["dispatched"][0]["pointId"], 450530)
        self.assertTrue(res_pending_ri["dispatched"][0]["fromFindRes"])

    def test_rss_gather_skips_ensure_world_scene_when_waiting_for_squad(self) -> None:
        """Verify _precheck_world_step_readiness returns waiting_for_squad in City view WITHOUT calling ensure_world_scene."""
        self.cd.lua.execute(
            """
            _G._testState.inWorld = false
            _G._testState.freeFormations = 0
            _G._testState.unlockFormations = 2
            _G._testState.inMarchUuids = { ['10001'] = true, ['10002'] = true }
            _G._testState.formations = {
                { uuid = '10001', index = 1, state = 1, soldiers = 1000 },
                { uuid = '10002', index = 2, state = 1, soldiers = 1000 },
            }
            _G._testState.myMarches = { { targetPos = 451100 }, { targetPos = 451200 } }
            """
        )

        with patch.object(ba, "ensure_world_scene", wraps=ba.ensure_world_scene) as spy_ews:
            res = ba.run_rss_gather_step(
                self.cd,
                self.pid,
                {},
                {},
                resource_type="Diamonds",
                min_level=1,
                max_level=15,
                context={},
            )

        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "waiting_for_squad")
        self.assertEqual(res["stop_reason"], "")
        self.assertEqual(res["active_marches"], 2)
        self.assertEqual(spy_ews.call_count, 0, "Must NEVER call ensure_world_scene when all squads are busy")
        self.assertEqual(self.cd.get_calls("changeToWorld"), 0, "Must NEVER yank city camera to World Map")
        self.assertFalse(self.cd.lua.eval("_G._testState.inWorld"))

    def test_standalone_npc_level_cap_and_attack_monster(self) -> None:
        """Verify run_standalone_npc_step caps at GetCanFindMonsterMaxLevel() and attacks boss=0, special=0 via ATTACK_MONSTER=1."""
        self.cd.lua.execute("_G._testState.maxNpcLevel = 24")
        self.cd.add_monster_point(451511, 1028)  # Lv28 normal NPC -> exceeds cap 24 (MUST skip)
        self.cd.add_monster_point(451512, 2004)  # Lv4 Boomer (boss=1, special=0 -> MUST skip)
        self.cd.add_monster_point(451513, 3004)  # Lv20 ChallengeBoss (special=4 -> MUST skip)
        self.cd.add_monster_point(451514, 1018)  # Lv18 standalone NPC
        self.cd.add_monster_point(451515, 1022, uuid=991022)  # Lv22 standalone NPC (best valid!)

        self.cd.lua.execute(
            """
            _G._testState.freeFormations = 1
            _G._testState.unlockFormations = 1
            _G._testState.formations = { { uuid = '10001', index = 1, state = 0, soldiers = 1000 } }
            """
        )

        res = ba.run_standalone_npc_step(
            self.cd,
            self.pid,
            {},
            {},
            min_level=1,
            max_level=40,
            stamina_cost=10,
            context={},
        )
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "dispatched")
        self.assertEqual(res["unlocked_max_level"], 24)
        self.assertEqual(res["effective_max_level"], 24)
        self.assertEqual(res["dispatched_count"], 1)
        self.assertEqual(res["dispatched"][0]["pointId"], 451515)
        self.assertEqual(res["dispatched"][0]["level"], 22)

        march_calls = self.cd.get_calls("sendCreateMarch")
        assert isinstance(march_calls, list)
        self.assertEqual(len(march_calls), 1)
        self.assertEqual(march_calls[0]["marchType"], 1)  # MarchTargetType.ATTACK_MONSTER
        self.assertEqual(march_calls[0]["ptId"], 451515)
        self.assertEqual(march_calls[0]["extraId"], 991022)

    def test_standalone_npc_out_of_stamina_and_six_arg_find_monster(self) -> None:
        """Verify out_of_stamina stop_reason when fuel < cost/reserve and 6-arg FindMonster(..., false, 0, 0) when empty."""
        # Case A: stamina < stamina_cost (and in City view -> no camera yank)
        self.cd.lua.execute("_G._testState.stamina = 8; _G._testState.inWorld = false")
        res_low = ba.run_standalone_npc_step(self.cd, self.pid, {}, {}, min_stamina=0, stamina_cost=10, context={})
        self.assertEqual(res_low["status"], "physical_limit")
        self.assertEqual(res_low["stop_reason"], "out_of_stamina")
        self.assertEqual(self.cd.get_calls("changeToWorld"), 0)

        # Case B: stamina < min_stamina + stamina_cost
        self.cd.lua.execute("_G._testState.stamina = 65; _G._testState.inWorld = true")
        res_resv = ba.run_standalone_npc_step(self.cd, self.pid, {}, {}, min_stamina=60, stamina_cost=10, context={})
        self.assertEqual(res_resv["status"], "physical_limit")
        self.assertEqual(res_resv["stop_reason"], "out_of_stamina")

        # Case C: Empty monster viewport -> FindMonster (nparams=6: mainPos, targetLevel, false, 0, 0)
        self.cd.seed_hq_viewpoint(450500)
        self.cd.lua.execute("_G._testState.stamina = 120; _G._testState.maxNpcLevel = 24")
        res_search = ba.run_standalone_npc_step(
            self.cd,
            self.pid,
            {},
            {},
            min_level=1,
            max_level=30,
            search_level=20,
            stamina_cost=10,
            context={},
        )
        self.assertEqual(res_search["status"], "searching")
        self.assertTrue(res_search["searched"])
        self.assertEqual(res_search["searched_level"], 20)
        pkts = self.cd.get_calls("sendMessage")
        assert isinstance(pkts, list)
        self.assertEqual(len(pkts), 1)
        self.assertEqual(pkts[0]["cmd"], "find.monster")
        self.assertEqual(pkts[0]["nargs"], 6)
        self.assertEqual(pkts[0]["args"], [450500, 20, False, 0, 0])

    def test_boomer_runs_level_cap_headless_join_rally_and_host_rally(self) -> None:
        """Verify run_boomer_runs caps level at GetCanFindBossMaxLevel(0), joins via JOIN_RALLY=6, and hosts via RALLY_FOR_BOSS=7."""
        # Part A: Open Boomer rally -> headless SendCreateMarchMessage with JOIN_RALLY=6
        self.cd.seed_hq_viewpoint(450500)
        self.cd.lua.execute(
            """
            _G._testState.maxBoomerFindLevel = 5
            _G._testState.maxBoomerAtkLevel = 7
            _G._testState.freeFormations = 1
            _G._testState.unlockFormations = 1
            _G._testState.formations = { { uuid = '10001', index = 1, state = 0, soldiers = 1000 } }
            _G._testState.allianceWars = {
                { uuid = 'war_bm_open', type = 0, targetPointId = 454100, attackUid = 'ally_leader_1' },
                { uuid = 'war_bm_self', type = 0, targetPointId = 454101, attackUid = '1001001' },
                { uuid = 'war_bm_joined', type = 0, targetPointId = 454102, attackUid = 'ally_leader_2' },
            }
            _G._testState.alreadyJoinedWars = { ['war_bm_joined'] = true }
            """
        )
        cfg = {
            "boomer_runs": {
                "join_open_rallies": True,
                "auto_start_rally": True,
                "min_level": 1,
                "max_level": 10,
                "stamina_cost": 20,
                "min_stamina": 0,
            }
        }
        res_join = ba.run_boomer_runs(self.cd, self.pid, {}, cfg, dry_run=False, context={})
        self.assertTrue(res_join["ok"])
        self.assertEqual(res_join["status"], "dispatched")
        self.assertEqual(res_join["unlocked_max_level"], 5)
        self.assertEqual(res_join["effective_max_level"], 5)
        self.assertIsInstance(res_join["joined"], dict)
        self.assertEqual(res_join["joined"]["warUuid"], "war_bm_open")
        self.assertEqual(res_join["joined"]["joinMethod"], "send_create_march")
        self.assertEqual(self.cd.get_calls("joinRallyFallback"), [])

        join_marches = self.cd.get_calls("sendCreateMarch")
        assert isinstance(join_marches, list)
        self.assertEqual(len(join_marches), 1)
        self.assertEqual(join_marches[0]["marchType"], 6)  # MarchTargetType.JOIN_RALLY
        self.assertEqual(join_marches[0]["ptId"], 454100)
        self.assertEqual(join_marches[0]["extraId"], "war_bm_open")

        # Part B: No open rallies -> host viewport Boomer capped at Lv5 (skip Lv7) via RALLY_FOR_BOSS=7
        cd_host = _LupaWorldMockCD()
        cd_host.lua.execute(
            """
            _G._testState.maxBoomerFindLevel = 5
            _G._testState.maxBoomerAtkLevel = 8
            _G._testState.freeFormations = 1
            _G._testState.unlockFormations = 1
            _G._testState.formations = { { uuid = '10001', index = 1, state = 0, soldiers = 1000 } }
            """
        )
        cd_host.add_monster_point(454201, 2007, uuid=772007)  # Lv7 Boomer (> cap 5)
        cd_host.add_monster_point(454202, 2005, uuid=772005)  # Lv5 Boomer (within cap)

        res_host = ba.run_boomer_runs(cd_host, self.pid + 1, {}, cfg, dry_run=False, context={})
        self.assertEqual(res_host["status"], "dispatched")
        self.assertEqual(res_host["started_rally"]["mode"], "host_rally")
        self.assertEqual(res_host["started_rally"]["pointId"], 454202)
        self.assertEqual(res_host["started_rally"]["level"], 5)

        host_marches = cd_host.get_calls("sendCreateMarch")
        assert isinstance(host_marches, list)
        self.assertEqual(len(host_marches), 1)
        self.assertEqual(host_marches[0]["marchType"], 7)  # MarchTargetType.RALLY_FOR_BOSS
        self.assertEqual(host_marches[0]["ptId"], 454202)
        self.assertEqual(host_marches[0]["rallyFlag"], 1)

    def test_saga_kill_step_detection_strict_summon_guard_and_inactive(self) -> None:
        """Verify run_saga_kill_step detects ActMonsterTowerData + special=4/40, guards CallChallengeActBoss, and returns not_detected when inactive."""
        self.cd.seed_hq_viewpoint(450500)
        # Part A: Inactive Saga -> not_detected
        res_inactive = ba.run_saga_kill_step(self.cd, self.pid, {}, {}, context={})
        self.assertEqual(res_inactive["status"], "physical_limit")
        self.assertEqual(res_inactive["stop_reason"], "not_detected")
        self.assertFalse(res_inactive["detected"])

        # Part B: Active Saga with difficulty selected, boss_count == 0, open_rallies == 0 -> calls CallChallengeActBoss(actId)
        self.cd.lua.execute(
            """
            _G._testState.saga.activeInfo = { actId = 7001 }
            _G._testState.saga.diffSelectedByAct[7001] = true
            _G._testState.freeFormations = 1
            _G._testState.unlockFormations = 1
            _G._testState.formations = { { uuid = '10001', index = 1, state = 0, soldiers = 1000 } }
            """
        )
        res_summon = ba.run_saga_kill_step(self.cd, self.pid, {}, {}, allow_summon=True, context={})
        self.assertEqual(res_summon["status"], "searching")
        self.assertTrue(res_summon["summoned"])
        self.assertTrue(res_summon["detected"])
        self.assertEqual(res_summon["act_id"], 7001)
        pkts_sum = self.cd.get_calls("sendMessage")
        assert isinstance(pkts_sum, list)
        self.assertEqual(len(pkts_sum), 1)
        self.assertEqual(pkts_sum[0]["cmd"], "call.challenge.act.boss")
        self.assertEqual(pkts_sum[0]["nargs"], 2)  # CallChallengeActBoss nparams=2
        self.assertEqual(pkts_sum[0]["args"], [7001])

        # Part C: summon_cooldown_active=True MUST prevent CallChallengeActBoss and fall back to FindMonster(..., 4)
        self.cd.lua.execute("_G._testState.calls.sendMessage = {}")
        res_cd_active = ba.run_saga_kill_step(
            self.cd,
            self.pid,
            {},
            {},
            allow_summon=True,
            context={"summon_cooldown_active": True},
        )
        self.assertFalse(res_cd_active["summoned"])
        pkts_cool = self.cd.get_calls("sendMessage")
        assert isinstance(pkts_cool, list)
        self.assertEqual(len(pkts_cool), 1)
        self.assertEqual(pkts_cool[0]["cmd"], "find.monster")
        self.assertEqual(pkts_cool[0]["args"][4], 4)  # ChallengeBoss=4

        # Part D: Map has special==4 (ChallengeBoss) and special==40 (MonsterTowerAlBoss) -> dispatches & never calls CallChallengeActBoss
        cd_bosses = _LupaWorldMockCD()
        cd_bosses.lua.execute(
            """
            _G._testState.saga.activeInfo = { actId = 7001 }
            _G._testState.saga.diffSelectedByAct[7001] = true
            _G._testState.freeFormations = 2
            _G._testState.unlockFormations = 2
            _G._testState.formations = {
                { uuid = '10001', index = 1, state = 0, soldiers = 1000 },
                { uuid = '10002', index = 2, state = 0, soldiers = 1000 },
            }
            """
        )
        cd_bosses.add_monster_point(455001, 3004, uuid=883004, boss_owner_uid="1001001")  # special=4 (own)
        cd_bosses.add_monster_point(455002, 3040, uuid=883040, alliance_id="ally_702")   # special=40 (AlBoss)

        res_boss = ba.run_saga_kill_step(cd_bosses, self.pid + 3, {}, {}, allow_summon=True, context={})
        self.assertEqual(res_boss["status"], "dispatched")
        self.assertTrue(res_boss["detected"])
        self.assertEqual(res_boss["boss_count"], 2)
        self.assertEqual(res_boss["dispatched_count"], 2)
        self.assertFalse(res_boss["summoned"])
        self.assertEqual(cd_bosses.get_calls("sendMessage"), [])
        marches = cd_bosses.get_calls("sendCreateMarch")
        assert isinstance(marches, list)
        self.assertEqual(marches[0]["marchType"], 1)  # ATTACK_MONSTER for ChallengeBoss (canRally=false)
        self.assertEqual(marches[1]["marchType"], 7)  # RALLY_FOR_BOSS for MonsterTowerAlBoss (isAlBoss=true)

    def test_tyrant_f1_before_reserve_and_status_phases(self) -> None:
        """Verify run_tyrant_event returns not_detected vs event_not_in_battle and picks F1 before reserve."""
        # Phase 1: not open -> not_detected
        self.cd.lua.execute("_G._testState.tyrant.isOpen = false; _G._testState.tyrant.inBattle = false")
        res_closed = ba.run_tyrant_event(self.cd, self.pid, {}, {}, context={})
        self.assertEqual(res_closed["status"], "physical_limit")
        self.assertEqual(res_closed["stop_reason"], "not_detected")

        # Phase 2: open, not in battle -> event_not_in_battle
        self.cd.lua.execute("_G._testState.tyrant.isOpen = true; _G._testState.tyrant.inBattle = false")
        res_wait_battle = ba.run_tyrant_event(self.cd, self.pid, {}, {}, context={})
        self.assertEqual(res_wait_battle["status"], "physical_limit")
        self.assertEqual(res_wait_battle["stop_reason"], "event_not_in_battle")

        # Phase 3: in battle with 2 formations and reserve=1 -> F1 hosts rally while F2 stays reserved (even with open rally!)
        self.cd.lua.execute(
            """
            _G._testState.tyrant.isOpen = true
            _G._testState.tyrant.inBattle = true
            _G._testState.tyrant.bossInfo = { pointId = 456001, uuid = 990074 }
            _G._testState.freeFormations = 2
            _G._testState.unlockFormations = 2
            _G._testState.formations = {
                { uuid = '10001', index = 1, state = 0, soldiers = 1000 },
                { uuid = '10002', index = 2, state = 0, soldiers = 1000 },
            }
            _G._testState.allianceWars = {
                { uuid = 'war_tyrant_1', type = 10, targetPointId = 456001, attackUid = 'ally_9' },
            }
            """
        )
        res_resv1 = ba.run_tyrant_event(
            self.cd,
            self.pid,
            {},
            {"formation_reserve": 1},
            context={},
        )
        self.assertEqual(res_resv1["status"], "dispatched")
        self.assertEqual(res_resv1["dispatched_count"], 1)
        self.assertEqual(res_resv1["hosted"]["formationIndex"], 1)
        self.assertEqual(res_resv1["joined"], [])  # F2 kept in reserve!
        marches = self.cd.get_calls("sendCreateMarch")
        assert isinstance(marches, list)
        self.assertEqual(len(marches), 1)
        self.assertEqual(marches[0]["marchType"], 74)  # RALLY_FOR_ALLIANCE_BOSS
        self.assertEqual(marches[0]["formUuid"], 10001)

        # Phase 4: reserve == total_formations (2) -> all reserved -> no_troops_or_formations
        cd_full_resv = _LupaWorldMockCD()
        cd_full_resv.lua.execute(
            """
            _G._testState.tyrant.isOpen = true
            _G._testState.tyrant.inBattle = true
            _G._testState.tyrant.bossInfo = { pointId = 456001, uuid = 990074 }
            _G._testState.freeFormations = 2
            _G._testState.unlockFormations = 2
            _G._testState.formations = {
                { uuid = '10001', index = 1, state = 0, soldiers = 1000 },
                { uuid = '10002', index = 2, state = 0, soldiers = 1000 },
            }
            """
        )
        res_resv2 = ba.run_tyrant_event(cd_full_resv, self.pid + 4, {}, {"formation_reserve": 2}, context={})
        self.assertEqual(res_resv2["status"], "physical_limit")
        self.assertEqual(res_resv2["stop_reason"], "no_troops_or_formations")
        self.assertEqual(cd_full_resv.get_calls("sendCreateMarch"), [])

    def test_furylord_live_reward_cap_and_f1_before_reserve(self) -> None:
        """Verify GetBossRewardCount(2) >= GetMaxBossRewardCount(2) stops with daily_limit_reached and F1 precedes reserve."""
        # Part A: Live game reward counter reached -> daily_limit_reached even if file daily counter is 0
        self.cd.lua.execute(
            """
            _G._testState.furylord.isOpen = true
            _G._testState.furylord.inAct = true
            _G._testState.furylord.rewardCount = 4
            _G._testState.furylord.maxRewardCount = 4
            _G._testState.furylord.bossList = { { pointId = 457001, uuid = 990093 } }
            """
        )
        ctx_capped = {"force_furylord": True, "daily_state_path": self.daily_state_path}
        res_cap = ba.run_furylord(self.cd, self.pid, {"uid": "1001001"}, {}, context=ctx_capped)
        self.assertEqual(res_cap["status"], "physical_limit")
        self.assertEqual(res_cap["stop_reason"], "daily_limit_reached")
        self.assertEqual(res_cap["reward_count"], 4)
        self.assertEqual(res_cap["max_reward_count"], 4)
        self.assertEqual(self.cd.get_calls("sendCreateMarch"), [])

        # Part B: Uncapped (rewardCount=1 < 4), 2 formations with reserve=1 -> F1 hosts rally via RALLY_FOR_ROAMING_BOSS=93
        cd_ok = _LupaWorldMockCD()
        cd_ok.lua.execute(
            """
            _G._testState.furylord.isOpen = true
            _G._testState.furylord.inAct = true
            _G._testState.furylord.rewardCount = 1
            _G._testState.furylord.maxRewardCount = 4
            _G._testState.furylord.bossList = { { pointId = 457002, uuid = 990094 } }
            _G._testState.freeFormations = 2
            _G._testState.unlockFormations = 2
            _G._testState.formations = {
                { uuid = '10001', index = 1, state = 0, soldiers = 1000 },
                { uuid = '10002', index = 2, state = 0, soldiers = 1000 },
            }
            _G._testState.allianceWars = {
                { uuid = 'war_fl_1', type = 14, targetPointId = 457002, attackUid = 'ally_9' },
            }
            """
        )
        ctx_ok = {
            "force_furylord": True,
            "reserve_override": 1,
            "daily_state_path": self.daily_state_path,
        }
        res_go = ba.run_furylord(cd_ok, self.pid + 5, {"uid": "1001001"}, {}, context=ctx_ok)
        self.assertEqual(res_go["status"], "dispatched")
        self.assertEqual(res_go["dispatched_count"], 1)
        self.assertEqual(res_go["dispatched"][0]["formationIndex"], 1)
        self.assertEqual(res_go["joined_rallies"], [])  # F2 stayed reserved
        self.assertGreaterEqual(res_go["used_today"], 1)
        marches = cd_ok.get_calls("sendCreateMarch")
        assert isinstance(marches, list)
        self.assertEqual(len(marches), 1)
        self.assertEqual(marches[0]["marchType"], 93)  # RALLY_FOR_ROAMING_BOSS
        self.assertEqual(marches[0]["formUuid"], 10001)

    def test_detect_map_kill_targets_is_strictly_read_only(self) -> None:
        """Verify detect_map_kill_targets reads all 5 categories accurately with zero network/march/scene mutations."""
        self.cd.lua.execute(
            """
            _G._testState.inWorld = false
            _G._testState.stamina = 95
            _G._testState.freeFormations = 2
            _G._testState.unlockFormations = 3
            _G._testState.maxNpcLevel = 26
            _G._testState.maxBoomerFindLevel = 5
            _G._testState.restBoomerKills = 7
            _G._testState.saga.activeInfo = { actId = 7001 }
            _G._testState.saga.diffSelectedByAct[7001] = true
            _G._testState.tyrant.isOpen = true
            _G._testState.tyrant.inBattle = true
            _G._testState.tyrant.bossInfo = { pointId = 456001 }
            _G._testState.furylord.isOpen = true
            _G._testState.furylord.inAct = true
            _G._testState.furylord.rewardCount = 2
            _G._testState.furylord.maxRewardCount = 4
            _G._testState.furylord.bossList = { { pointId = 457001 } }
            _G._testState.allianceWars = {
                { uuid = 'w_bm', type = 0, targetPointId = 454001 },
                { uuid = 'w_ty', type = 10, targetPointId = 456001 },
                { uuid = 'w_fl', type = 14, targetPointId = 457001 },
            }
            """
        )
        self.cd.add_monster_point(453101, 1022)  # NPC
        self.cd.add_monster_point(454101, 2005)  # Boomer
        self.cd.add_monster_point(455101, 3004)  # Saga

        det = ba.detect_map_kill_targets(self.cd, self.pid)
        self.assertTrue(det["ok"])
        self.assertEqual(det["stamina"], 95)
        self.assertEqual(det["free_formations"], 2)
        self.assertEqual(det["active_marches"], 1)
        self.assertEqual(det["total_formations"], 3)
        self.assertEqual(det["max_npc_level"], 26)
        self.assertEqual(det["max_boomer_level"], 5)
        self.assertEqual(det["rest_boomer_kills"], 7)

        self.assertTrue(det["boomers"]["detected"])
        self.assertEqual(det["boomers"]["open_rallies"], 1)
        self.assertEqual(det["boomers"]["viewport_count"], 1)
        self.assertTrue(det["standalone_npc"]["detected"])
        self.assertEqual(det["standalone_npc"]["viewport_count"], 1)
        self.assertTrue(det["saga"]["detected"])
        self.assertEqual(det["saga"]["boss_count"], 1)
        self.assertTrue(det["tyrant"]["detected"])
        self.assertEqual(det["tyrant"]["boss_point_id"], 456001)
        self.assertTrue(det["furylord"]["detected"])
        self.assertEqual(det["furylord"]["reward_count"], 2)
        self.assertEqual(det["furylord"]["max_reward_count"], 4)

        # Strictly read-only assertions
        self.assertEqual(self.cd.get_calls("sendMessage"), [])
        self.assertEqual(self.cd.get_calls("sendCreateMarch"), [])
        self.assertEqual(self.cd.get_calls("changeToWorld"), 0)
        self.assertEqual(self.cd.get_calls("joinRallyFallback"), [])
        self.assertEqual(self.cd.get_calls("autoAddSoldier"), [])
        self.assertEqual(self.cd.get_calls("tyrantFreeReward"), 0)
        self.assertEqual(self.cd.get_calls("furylordGetReward"), 0)
        self.assertEqual(self.cd.get_calls("furylordGetBossInfo"), 0)

    def test_blacklisted_points_and_dry_run_prevent_mutations(self) -> None:
        """Verify blacklisted points are skipped across RSS/NPC/Boomer/Saga and dry_run never sends packets."""
        self.cd.add_resource_point(451541, 310)
        self.cd.add_monster_point(451542, 1022)
        self.cd.add_monster_point(451543, 2005)
        self.cd.add_monster_point(451544, 3004)
        self.cd.lua.execute("_G._testState.saga.activeInfo = { actId = 7001 }; _G._testState.saga.diffSelectedByAct[7001] = true")

        ctx = {"blacklisted_points": ["451541", "451542", "451543", "451544"]}
        r_rss = ba.run_rss_gather_step(self.cd, self.pid, {}, {}, resource_type="Diamonds", dry_run=True, context=ctx)
        r_npc = ba.run_standalone_npc_step(self.cd, self.pid, {}, {}, dry_run=True, context=ctx)
        r_bm = ba.run_boomer_runs(self.cd, self.pid, {}, {}, dry_run=True, context=ctx)
        r_sg = ba.run_saga_kill_step(self.cd, self.pid, {}, {}, dry_run=True, context=ctx)

        self.assertEqual(r_rss["candidates_found"], 0)
        self.assertEqual(r_npc["candidates_found"], 0)
        self.assertIsNone(r_bm.get("started_rally"))
        self.assertEqual(r_sg["dispatched_count"], 0)
        self.assertEqual(self.cd.get_calls("sendCreateMarch"), [])
        self.assertEqual(self.cd.get_calls("sendMessage"), [])


# =============================================================================
# Layer 3: Hub Continuous Loop Engine Tests
# =============================================================================
class TestContinuousFarmLoopEngine(unittest.TestCase):
    """Tier 3: Real threaded HubBackend continuous RSS & Map Kills loop engine tests."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = self._tmp.name
        self.hub = _load_hub_module()
        self.cfg_file = Path(self.tmp_dir) / "bot config.json"
        self.cfg_file.write_text(json.dumps(mcb.default_config()), encoding="utf-8")

        self._orig_data = self.hub.DATA_DIR
        self._orig_heinz_data = self.hub.HEINZ_DATA_DIR
        self._orig_ba = self.hub.bot_actions
        self._orig_cd = self.hub.client_discovery
        self._hub_mcb = self.hub.multi_client_bot
        self._orig_load_cfg = self._hub_mcb.load_config
        self._orig_save_cfg = self._hub_mcb.save_config
        self._orig_cfg_path = getattr(self._hub_mcb, "CONFIG_PATH", None)

        self.hub.DATA_DIR = self.tmp_dir
        self.hub.HEINZ_DATA_DIR = self.tmp_dir
        self._hub_mcb.CONFIG_PATH = self.cfg_file
        self._hub_mcb.load_config = lambda config_path=self.cfg_file: self._orig_load_cfg(self.cfg_file)
        self._hub_mcb.save_config = lambda cfg, config_path=self.cfg_file: self._orig_save_cfg(cfg, self.cfg_file)

        self.backend = self._make_backend()
        self.addCleanup(self._cleanup_backend_and_globals)

    def _cleanup_backend_and_globals(self) -> None:
        try:
            self.backend.shutdown()
        finally:
            self.hub.DATA_DIR = self._orig_data
            self.hub.HEINZ_DATA_DIR = self._orig_heinz_data
            self.hub.bot_actions = self._orig_ba
            self.hub.client_discovery = self._orig_cd
            self._hub_mcb.load_config = self._orig_load_cfg
            self._hub_mcb.save_config = self._orig_save_cfg
            if self._orig_cfg_path is not None:
                self._hub_mcb.CONFIG_PATH = self._orig_cfg_path
            self._tmp.cleanup()

    def _make_backend(self) -> Any:
        backend = self.hub.HubBackend.__new__(self.hub.HubBackend)
        backend._lock = threading.RLock()
        backend._log_seq = 0
        backend._log_epoch = 0
        backend._logs_cleared_seq = 0
        backend.logs = []
        backend.is_monitoring = True
        backend._window = None
        backend.target_pid = None
        backend.selected_client_pid = None
        backend.selected_client_label = None
        backend.discovered_clients = []
        backend.running_clients = []
        backend._live_info_by_pid = {}
        backend._uid_name_cache = {}
        backend._active_actions = set()
        backend._last_env_pid = None
        backend._last_env_ts = 0.0
        backend._live_sync_ts = {}
        backend._hotkey_thread = None
        backend._hotkey_thread_id = None
        backend._daemon_proc = None
        backend._config_snapshot_cache = None
        backend._last_good_config_snapshot = None
        backend._config_version = 1
        backend._log_dir_ready = False
        backend.is_online = True
        backend.status_text = "Online"
        backend.fps_text = "180 FPS"
        backend.dropdown_values = ["Auto"]
        backend.selected_dropdown = "Auto"
        backend.finder_status = {"text": "", "tone": "muted"}
        backend.env = {}
        backend.setup_status = {}
        backend.fleet_state = {"clients": []}
        backend._always_on_daemon_enabled = False
        backend._always_on_daemon_state = "paused"
        backend._always_on_wake = threading.Event()
        backend._hospital_watcher_enabled = False
        backend._hospital_watcher_state = "off"
        backend._hospital_watcher_last_summary = {}
        backend._alliance_help_watcher_enabled = False
        backend._alliance_help_watcher_state = "paused"
        backend._alliance_help_interval_sec = 15.0
        backend._alliance_help_stats = {}
        backend._alliance_tech_watcher_enabled = False
        backend._alliance_tech_watcher_state = "paused"
        backend._alliance_tech_interval_sec = 45.0
        backend._alliance_tech_stats = {}
        backend._ensure_farm_loop_attrs()
        return backend

    def _set_clients(self, procs: list[dict[str, Any]]) -> None:
        self.backend._discover_running_clients = lambda: list(procs)
        self.backend._client_display_name = lambda p: str(p.get("label") or f"PID {p.get('pid')}") if p else ""
        self.hub.client_discovery = type("_FakeCD", (), {"_xlua_loaded": staticmethod(lambda pid: True)})

    @staticmethod
    def _wait_until(pred, timeout: float = 5.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if pred():
                return True
            time.sleep(0.01)
        return bool(pred())

    def test_rss_loop_transitions_get_state_persistence_and_user_stop(self) -> None:
        """Verify dispatched -> waiting_for_squad -> dispatched -> physical_limit persists stop_reason in get_state()['farm_loops'] and stop_rss_gather_loop works."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        steps = [
            {
                "ok": True,
                "status": "dispatched",
                "dispatched_count": 1,
                "dispatched": [{"formationUuid": "f1", "pointId": 1001, "claimKey": "702:1001", "resourceType": "Diamonds"}],
                "free_formations": 1,
                "active_marches": 1,
                "total_formations": 2,
                "stamina": 100,
            },
            {
                "ok": True,
                "status": "waiting_for_squad",
                "dispatched_count": 0,
                "dispatched": [],
                "free_formations": 0,
                "active_marches": 2,
                "total_formations": 2,
                "stamina": 100,
            },
            {
                "ok": True,
                "status": "dispatched",
                "dispatched_count": 1,
                "dispatched": [{"formationUuid": "f2", "pointId": 1002, "claimKey": "702:1002", "resourceType": "Diamonds"}],
                "free_formations": 1,
                "active_marches": 1,
                "total_formations": 2,
                "stamina": 100,
            },
            {
                "ok": True,
                "status": "physical_limit",
                "stop_reason": "no_troops_or_formations",
                "dispatched_count": 0,
                "dispatched": [],
                "free_formations": 0,
                "active_marches": 0,
                "total_formations": 2,
                "stamina": 100,
            },
        ]
        idx = {"i": 0}
        seen_statuses: list[str] = []

        class _FakeBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                i = idx["i"]
                idx["i"] = i + 1
                res = copy.deepcopy(steps[min(i, len(steps) - 1)])
                seen_statuses.append(res["status"])
                return res

        self.hub.bot_actions = _FakeBA
        res = self.backend.start_rss_gather_loop(
            "diamonds",
            {
                "pid": 1001,
                "min_level": 1,
                "max_level": 15,
                "_dispatch_delay_sec": 0.01,
                "_wait_squad_delay_sec": 0.01,
                "_search_delay_sec": 0.01,
            },
        )
        self.assertTrue(res["ok"])
        self.assertTrue(
            self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["rss"]["running"]),
            "RSS loop should reach physical_limit and stop",
        )
        self.assertEqual(seen_statuses, ["dispatched", "waiting_for_squad", "dispatched", "physical_limit"])

        fl = self.backend.get_state()["farm_loops"]
        self.assertEqual(fl["active_loops"], [])
        rss = fl["rss"]
        self.assertFalse(rss["running"])
        self.assertEqual(rss["state"], "stopped")
        self.assertEqual(rss["stop_reason"], "no_troops_or_formations")
        self.assertEqual(rss["total_dispatched"], 2)
        self.assertEqual(rss["by_target"].get("diamonds"), 2)

        # Active user stop test
        gate = threading.Event()
        entered = threading.Event()

        class _WaitBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                entered.set()
                gate.wait(timeout=0.05)
                return {"ok": True, "status": "waiting_for_squad", "active_marches": 1, "total_formations": 2}

        self.hub.bot_actions = _WaitBA
        start2 = self.backend.start_rss_gather_loop("wood", {"pid": 1001, "_wait_squad_delay_sec": 0.5})
        self.assertTrue(start2["ok"])
        self.assertTrue(entered.wait(timeout=2.0))
        stop2 = self.backend.stop_rss_gather_loop(pid=1001)
        gate.set()
        self.assertTrue(stop2["ok"])
        self.assertTrue(stop2["stopped"])
        self.assertIn(1001, stop2["stopped_pids"])
        self.assertEqual(self.backend.get_state()["farm_loops"]["rss"]["stop_reason"], "user_stopped")

    def test_rss_loop_search_level_step_down_4_plus_1_and_waits_while_active_marches(self) -> None:
        """Verify 4+1 search_level step-down [15,10,5,1,1] and waiting instead of stopping while active_marches > 0."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        # Part A: 4+1 step down with 0 active marches -> exact levels [15, 10, 5, 1, 1] -> no_targets_found
        recorded_levels: list[int | None] = []

        class _SearchBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                recorded_levels.append(kwargs.get("search_level"))
                return {
                    "ok": True,
                    "status": "searching",
                    "searched": True,
                    "searched_level": kwargs.get("search_level"),
                    "active_marches": 0,
                    "free_formations": 2,
                    "total_formations": 2,
                }

        self.hub.bot_actions = _SearchBA
        self.backend.start_rss_gather_loop(
            "diamonds",
            {
                "pid": 1001,
                "min_level": 1,
                "max_level": 15,
                "_search_delay_sec": 0.01,
            },
        )
        self.assertTrue(
            self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["rss"]["running"], timeout=6.0),
            "4+1 search cycle should finish cleanly",
        )
        self.assertEqual(recorded_levels, [15, 10, 5, 1, 1])
        self.assertEqual(self.backend.get_state()["farm_loops"]["rss"]["stop_reason"], "no_targets_found")

        # Part B: active_marches > 0 when no_targets_found -> MUST wait instead of stopping, then resume & dispatch!
        phase = {"calls": 0}
        saw_waiting = threading.Event()

        class _ActiveWaitBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                phase["calls"] += 1
                if phase["calls"] == 1:
                    # Exhausted search while 1 squad still marching
                    return {
                        "ok": True,
                        "status": "physical_limit",
                        "stop_reason": "no_targets_found",
                        "active_marches": 1,
                        "free_formations": 1,
                        "total_formations": 2,
                    }
                if phase["calls"] == 2:
                    saw_waiting.set()
                    return {
                        "ok": True,
                        "status": "dispatched",
                        "dispatched_count": 1,
                        "dispatched": [{"formationUuid": "f1", "pointId": 2001, "claimKey": "702:2001", "resourceType": "Diamonds"}],
                        "active_marches": 1,
                        "free_formations": 1,
                        "total_formations": 2,
                    }
                return {
                    "ok": True,
                    "status": "physical_limit",
                    "stop_reason": "no_troops_or_formations",
                    "active_marches": 0,
                    "free_formations": 0,
                    "total_formations": 2,
                }

        self.hub.bot_actions = _ActiveWaitBA
        self.backend.start_rss_gather_loop(
            "diamonds",
            {
                "pid": 1001,
                "_search_delay_sec": 0.01,
                "_dispatch_delay_sec": 0.01,
                "_exhausted_backoff_sec": 0.02,
            },
        )
        self.assertTrue(saw_waiting.wait(timeout=3.0), "Loop should keep running after no_targets_found while active_marches > 0")
        self.assertTrue(
            self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["rss"]["running"]),
        )
        rss = self.backend.get_state()["farm_loops"]["rss"]
        self.assertEqual(rss["total_dispatched"], 1)
        self.assertEqual(rss["stop_reason"], "no_troops_or_formations")

    def test_map_kills_single_mode_and_tyrant_pre_battle_polling(self) -> None:
        """Verify single Map Kills mode lifecycle and Tyrant event_not_in_battle polling."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        calls = {"n": 0}

        class _BoomerBA:
            @staticmethod
            def run_boomer_runs(cd, pid, cs, cfg, dry_run=False, context=None):
                calls["n"] += 1
                if calls["n"] == 1:
                    return {
                        "ok": True,
                        "status": "dispatched",
                        "dispatched_count": 1,
                        "dispatched": [{"formationUuid": "f1", "pointId": 5001, "claimKey": "702:5001"}],
                        "stamina": 50,
                        "free_formations": 1,
                        "active_marches": 1,
                        "total_formations": 2,
                    }
                return {
                    "ok": True,
                    "status": "physical_limit",
                    "stop_reason": "out_of_stamina",
                    "stamina": 10,
                    "free_formations": 2,
                    "active_marches": 0,
                    "total_formations": 2,
                }

        self.hub.bot_actions = _BoomerBA
        res = self.backend.start_map_kills_loop("boomers", {"pid": 1001, "_dispatch_delay_sec": 0.01})
        self.assertTrue(res["ok"])
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        kills = self.backend.get_state()["farm_loops"]["kills"]
        self.assertEqual(kills["stop_reason"], "out_of_stamina")
        self.assertEqual(kills["total_dispatched"], 1)
        self.assertEqual(kills["by_target"].get("boomers"), 1)

        # Tyrant event_not_in_battle keeps polling in waiting_for_squad instead of stopping
        tyrant_entered = threading.Event()

        class _TyrantWaitBA:
            @staticmethod
            def run_tyrant_event(cd, pid, cs, cfg, dry_run=False, context=None):
                tyrant_entered.set()
                return {
                    "ok": True,
                    "status": "physical_limit",
                    "stop_reason": "event_not_in_battle",
                    "is_open": True,
                    "in_battle": False,
                }

        self.hub.bot_actions = _TyrantWaitBA
        self.backend.start_map_kills_loop("tyrant", {"pid": 1001, "_probe_interval_sec": 0.01})
        self.assertTrue(tyrant_entered.wait(timeout=2.0))
        self.assertTrue(
            self._wait_until(lambda: self.backend.get_state()["farm_loops"]["kills"]["state"] == "waiting_for_squad"),
        )
        self.assertTrue(self.backend.get_state()["farm_loops"]["kills"]["running"])
        stop_t = self.backend.stop_map_kills_loop(pid=1001)
        self.assertTrue(stop_t["stopped"])
        self.assertEqual(self.backend.get_state()["farm_loops"]["kills"]["stop_reason"], "user_stopped")

    def test_map_kills_all_chain_order_skips_undetected_and_prioritizes_bosses(self) -> None:
        """Verify all_chain default order, undetected boss skipping, and prioritize_detected_bosses ordering."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        # Part A: Conditional bosses undetected -> ONLY boomers & standalone_npc run (exact order)
        called_modes_a: list[str] = []

        class _ChainSkipBA:
            @staticmethod
            def detect_map_kill_targets(cd, pid):
                return {
                    "ok": True,
                    "stamina": 100,
                    "free_formations": 2,
                    "active_marches": 0,
                    "total_formations": 2,
                    "in_alliance": True,
                    "boomers": {"detected": True, "open_rallies": 0, "viewport_count": 1},
                    "standalone_npc": {"detected": True, "viewport_count": 1, "max_level": 20},
                    "saga": {"detected": False},
                    "tyrant": {"detected": False},
                    "furylord": {"detected": False},
                }

            @staticmethod
            def run_boomer_runs(cd, pid, cs, cfg, dry_run=False, context=None):
                called_modes_a.append("boomers")
                return {"ok": True, "status": "physical_limit", "stop_reason": "not_in_alliance", "active_marches": 0}

            @staticmethod
            def run_standalone_npc_step(cd, pid, cs, cfg, **kwargs):
                called_modes_a.append("standalone_npc")
                return {"ok": True, "status": "physical_limit", "stop_reason": "out_of_stamina", "active_marches": 0}

            @staticmethod
            def run_saga_kill_step(*args, **kwargs):
                called_modes_a.append("saga")
                return {"ok": True, "status": "physical_limit", "stop_reason": "not_detected"}

            @staticmethod
            def run_tyrant_event(*args, **kwargs):
                called_modes_a.append("tyrant")
                return {"ok": True, "status": "physical_limit", "stop_reason": "not_detected"}

            @staticmethod
            def run_furylord(*args, **kwargs):
                called_modes_a.append("furylord")
                return {"ok": True, "status": "physical_limit", "stop_reason": "not_detected"}

        self.hub.bot_actions = _ChainSkipBA
        self.backend.start_map_kills_loop(
            "all_chain",
            {"pid": 1001, "prioritize_detected_bosses": False, "_search_delay_sec": 0.01},
        )
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        self.assertEqual(called_modes_a, ["boomers", "standalone_npc"])
        self.assertNotIn("saga", called_modes_a)
        self.assertNotIn("tyrant", called_modes_a)
        self.assertNotIn("furylord", called_modes_a)

        # Part B: All bosses detected + prioritize_detected_bosses=True -> tyrant -> furylord -> saga -> boomers -> standalone_npc
        self.backend._last_kill_detection_by_pid.clear()
        called_modes_b: list[str] = []

        class _ChainPrioBA:
            @staticmethod
            def detect_map_kill_targets(cd, pid):
                return {
                    "ok": True,
                    "stamina": 100,
                    "free_formations": 2,
                    "active_marches": 0,
                    "total_formations": 2,
                    "in_alliance": True,
                    "boomers": {"detected": True},
                    "standalone_npc": {"detected": True},
                    "saga": {"detected": True, "active": True},
                    "tyrant": {"detected": True, "is_open": True, "in_battle": True},
                    "furylord": {"detected": True, "is_open": True, "in_act": True},
                }

            @staticmethod
            def run_tyrant_event(*args, **kwargs):
                called_modes_b.append("tyrant")
                return {"ok": True, "status": "physical_limit", "stop_reason": "daily_limit_reached", "active_marches": 0}

            @staticmethod
            def run_furylord(*args, **kwargs):
                called_modes_b.append("furylord")
                return {"ok": True, "status": "physical_limit", "stop_reason": "daily_limit_reached", "active_marches": 0}

            @staticmethod
            def run_saga_kill_step(*args, **kwargs):
                called_modes_b.append("saga")
                return {"ok": True, "status": "physical_limit", "stop_reason": "daily_limit_reached", "active_marches": 0}

            @staticmethod
            def run_boomer_runs(*args, **kwargs):
                called_modes_b.append("boomers")
                return {"ok": True, "status": "physical_limit", "stop_reason": "daily_limit_reached", "active_marches": 0}

            @staticmethod
            def run_standalone_npc_step(*args, **kwargs):
                called_modes_b.append("standalone_npc")
                return {"ok": True, "status": "physical_limit", "stop_reason": "daily_limit_reached", "active_marches": 0}

        self.hub.bot_actions = _ChainPrioBA
        self.backend.start_map_kills_loop(
            "all_chain",
            {"pid": 1001, "prioritize_detected_bosses": True, "_search_delay_sec": 0.01},
        )
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        self.assertEqual(called_modes_b, ["tyrant", "furylord", "saga", "boomers", "standalone_npc"])

    def test_map_kills_all_chain_exhausted_modes_and_preserves_other_counters(self) -> None:
        """Verify exhausted modes enter cooldown cleanly and waiting_for_squad on one mode does NOT reset other modes' search counters."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        counts = {"boomers": 0, "standalone_npc": 0, "tyrant": 0}

        class _CounterChainBA:
            @staticmethod
            def detect_map_kill_targets(cd, pid):
                return {
                    "ok": True,
                    "stamina": 100,
                    "free_formations": 1,
                    "active_marches": 0,
                    "total_formations": 2,
                    "in_alliance": True,
                    "boomers": {"detected": True},
                    "standalone_npc": {"detected": True},
                    "saga": {"detected": False},
                    "tyrant": {"detected": True, "is_open": True, "in_battle": True},
                    "furylord": {"detected": False},
                }

            @staticmethod
            def run_boomer_runs(*args, **kwargs):
                counts["boomers"] += 1
                return {"ok": True, "status": "searching", "searched": True, "searched_level": 5, "free_formations": 1, "active_marches": 0}

            @staticmethod
            def run_standalone_npc_step(*args, **kwargs):
                counts["standalone_npc"] += 1
                # Returns searching 3 times, then stops with out_of_stamina on 4th? Wait: keep searching so 4+1 completes!
                # First 2 calls: searching (counter=1, 2); then 3 more searching (3, 4, 5 -> exhausted!)
                return {"ok": True, "status": "searching", "searched": True, "searched_level": 10, "free_formations": 1, "active_marches": 0}

            @staticmethod
            def run_tyrant_event(*args, **kwargs):
                counts["tyrant"] += 1
                # On pass 2, return waiting_for_squad with free_formations=0 (triggers saw_waiting & breaks pass);
                # after pass 2, return daily_limit_reached so chain can exit cleanly once others exhaust.
                if counts["tyrant"] == 2:
                    return {"ok": True, "status": "waiting_for_squad", "free_formations": 0, "active_marches": 2}
                return {"ok": True, "status": "physical_limit", "stop_reason": "daily_limit_reached", "free_formations": 1, "active_marches": 0}

        self.hub.bot_actions = _CounterChainBA
        self.backend.start_map_kills_loop(
            "all_chain",
            {
                "pid": 1001,
                "chain": ["boomers", "standalone_npc", "tyrant"],
                "_search_delay_sec": 0.01,
                "_wait_squad_delay_sec": 0.01,
                "_exhausted_backoff_sec": 30.0,
            },
        )
        self.assertTrue(
            self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]),
        )
        # Each searching mode gets exactly 5 calls (4 searches + 1 verification -> exhausted), NOT reset by tyrant waiting_for_squad on pass 2!
        self.assertEqual(counts["boomers"], 5)
        self.assertEqual(counts["standalone_npc"], 5)

    def test_phantom_dispatch_c1_rollback_blacklist_and_stop(self) -> None:
        """Verify C1 phantom-dispatch detection rolls back fake count, blacklists target, and stops at 3 rejections."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        seen_blacklists: list[list[str]] = []

        class _PhantomBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                bl = list((kwargs.get("context") or {}).get("blacklisted_points") or [])
                seen_blacklists.append(bl)
                # Always claims f1 dispatched to 7777 with active_marches=1 (never advances!)
                return {
                    "ok": True,
                    "status": "dispatched",
                    "dispatched_count": 1,
                    "dispatched": [{"formationUuid": "f1", "pointId": 7777, "claimKey": "702:7777", "resourceType": "Diamonds"}],
                    "active_marches": 1,
                    "free_formations": 1,
                    "total_formations": 2,
                    "stamina": 100,
                }

        self.hub.bot_actions = _PhantomBA
        self.backend.start_rss_gather_loop(
            "diamonds",
            {"pid": 1001, "_dispatch_delay_sec": 0.01, "_search_delay_sec": 0.01},
        )
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["rss"]["running"]))

        rss = self.backend.get_state()["farm_loops"]["rss"]
        self.assertEqual(rss["stop_reason"], "dispatch_rejected")
        self.assertEqual(rss["total_dispatched"], 0, "Fake count must be rolled back to 0")
        self.assertEqual(rss["by_target"].get("diamonds", 0), 0)
        # Step 1 (initial) -> Step 2 (1st phantom triggers blacklist) -> Step 3 sees '7777' & '702:7777' blacklisted!
        self.assertGreaterEqual(len(seen_blacklists), 4)
        self.assertIn("7777", seen_blacklists[2])
        self.assertIn("702:7777", seen_blacklists[2])

        # Also verify Map Kills C1 phantom detection stops with dispatch_rejected & rolls back
        seen_kill_bl: list[list[str]] = []

        class _PhantomKillBA:
            @staticmethod
            def run_boomer_runs(cd, pid, cs, cfg, dry_run=False, context=None):
                seen_kill_bl.append(list((context or {}).get("blacklisted_points") or []))
                return {
                    "ok": True,
                    "status": "dispatched",
                    "dispatched_count": 1,
                    "dispatched": [{"formationUuid": "f1", "pointId": 8888, "claimKey": "702:8888"}],
                    "active_marches": 1,
                    "free_formations": 1,
                    "total_formations": 2,
                }

        self.hub.bot_actions = _PhantomKillBA
        self.backend.start_map_kills_loop("boomers", {"pid": 1001, "_dispatch_delay_sec": 0.01, "_search_delay_sec": 0.01})
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        kills = self.backend.get_state()["farm_loops"]["kills"]
        self.assertEqual(kills["stop_reason"], "dispatch_rejected")
        self.assertEqual(kills["total_dispatched"], 0)
        self.assertIn("8888", seen_kill_bl[2])

    def test_atomic_stop_start_and_per_pid_exec_lock(self) -> None:
        """Verify atomic Stop+Start replacement and per-PID exec lock (max 1 concurrent step per PID, parallel across PIDs)."""
        self._set_clients([
            {"pid": 1001, "role": "main", "label": "Main"},
            {"pid": 1002, "role": "farm", "label": "Farm1"},
        ])

        slow_entered = threading.Event()
        slow_release = threading.Event()
        concurrent_lock = threading.Lock()
        in_flight: dict[int, int] = {1001: 0, 1002: 0}
        max_concurrent: dict[int, int] = {1001: 0, 1002: 0}
        disjoint_parallel_observed = threading.Event()
        steps_by_pid: dict[int, list[str]] = {1001: [], 1002: []}

        class _LockProbeBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                res_name = str(kwargs.get("resource_type") or "")
                with concurrent_lock:
                    in_flight[pid] = in_flight.get(pid, 0) + 1
                    max_concurrent[pid] = max(max_concurrent.get(pid, 0), in_flight[pid])
                    if in_flight.get(1001, 0) >= 1 and in_flight.get(1002, 0) >= 1:
                        disjoint_parallel_observed.set()
                try:
                    steps_by_pid[pid].append(res_name)
                    if pid == 1001 and res_name == "Food":
                        slow_entered.set()
                        slow_release.wait(timeout=3.0)
                        return {"ok": True, "status": "waiting_for_squad", "active_marches": 1, "total_formations": 2}
                    if pid == 1002:
                        # Block until 1001 is also in-flight to verify disjoint PIDs do NOT serialize
                        slow_entered.wait(timeout=2.0)
                        time.sleep(0.05)
                    return {"ok": True, "status": "physical_limit", "stop_reason": "no_troops_or_formations", "active_marches": 0}
                finally:
                    with concurrent_lock:
                        in_flight[pid] -= 1

        self.hub.bot_actions = _LockProbeBA
        r1 = self.backend.start_rss_gather_loop("food", {"pid": 1001, "_wait_squad_delay_sec": 0.01})
        self.assertTrue(r1["ok"])
        self.assertTrue(slow_entered.wait(timeout=2.0))

        # Start disjoint PID 1002 concurrently while PID 1001 is inside slow step
        r2 = self.backend.start_rss_gather_loop("wood", {"pid": 1002, "_search_delay_sec": 0.01})
        self.assertTrue(r2["ok"])
        self.assertTrue(disjoint_parallel_observed.wait(timeout=2.0), "Disjoint PIDs must execute in parallel")

        # Atomically replace PID 1001 while old step is still in-flight!
        r_replace = self.backend.start_rss_gather_loop("diamonds", {"pid": 1001, "_search_delay_sec": 0.01})
        self.assertTrue(r_replace["ok"])
        self.assertIsNotNone(r_replace["replaced_loop"])
        self.assertEqual(r_replace["replaced_loop"]["stop_reason"], "replaced")
        self.assertEqual(r_replace["replaced_loop"]["mode"], "food")

        # Release old worker and verify max_concurrent[1001] stayed strictly <= 1
        slow_release.set()
        self.assertTrue(self._wait_until(lambda: len(self.backend.get_state()["farm_loops"]["active_loops"]) == 0))
        self.assertEqual(max_concurrent[1001], 1, "Per-PID exec lock must forbid concurrent steps on same PID")
        self.assertIn("Diamonds", steps_by_pid[1001])

    def test_saga_60s_summon_cooldown_across_steps_and_loop_restart(self) -> None:
        """Verify Saga 60s summon cooldown sets allow_summon=False across steps AND across loop restarts."""
        self._set_clients([{"pid": 1001, "role": "main", "label": "Main"}])
        self.backend.selected_client_pid = 1001

        calls: list[dict[str, Any]] = []

        class _SagaCooldownBA:
            @staticmethod
            def run_saga_kill_step(cd, pid, cs, cfg, allow_summon=True, dry_run=False, context=None, **kwargs):
                calls.append({
                    "allow_summon": allow_summon,
                    "cooldown": bool((context or {}).get("summon_cooldown_active")),
                })
                if len(calls) == 1:
                    return {"ok": True, "status": "searching", "summoned": True, "active": True, "detected": True}
                return {"ok": True, "status": "physical_limit", "stop_reason": "no_targets_found", "active_marches": 0}

        self.hub.bot_actions = _SagaCooldownBA
        self.backend.start_map_kills_loop("saga", {"pid": 1001, "allow_summon_saga": True, "_search_delay_sec": 0.01})
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))

        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0]["allow_summon"])
        self.assertFalse(calls[0]["cooldown"])
        self.assertFalse(calls[1]["allow_summon"])
        self.assertTrue(calls[1]["cooldown"])

        # Restart a new Saga loop on the same PID within 60s -> cooldown MUST still be enforced!
        self.backend.start_map_kills_loop("saga", {"pid": 1001, "allow_summon_saga": True, "_search_delay_sec": 0.01})
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        self.assertEqual(len(calls), 3)
        self.assertFalse(calls[2]["allow_summon"])
        self.assertTrue(calls[2]["cooldown"])

        # After 60s elapsed, cooldown lifts cleanly
        self.backend._get_farm_pid_state(1001)["last_saga_summon_ts"] = time.monotonic() - 61.0
        self.backend.start_map_kills_loop("saga", {"pid": 1001, "allow_summon_saga": True, "_search_delay_sec": 0.01})
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        self.assertTrue(calls[3]["allow_summon"])
        self.assertFalse(calls[3]["cooldown"])

    def test_multi_account_pid_scoping_in_farm_loops_snapshot(self) -> None:
        """Verify rss.pid, kills.pid, and detection scope cleanly to selected_client_pid across multiple clients."""
        self._set_clients([
            {"pid": 2001, "role": "main", "label": "Main"},
            {"pid": 2002, "role": "farm", "label": "Farm1"},
        ])

        ready_2001 = threading.Event()
        ready_2002 = threading.Event()

        class _MultiPidBA:
            @staticmethod
            def detect_map_kill_targets(cd, pid):
                return {
                    "ok": True,
                    "stamina": 100 if pid == 2001 else 55,
                    "free_formations": 2,
                    "active_marches": 0,
                    "total_formations": 2,
                    "in_alliance": True,
                    "boomers": {"detected": True},
                    "standalone_npc": {"detected": True},
                    "saga": {"detected": pid == 2001},
                    "tyrant": {"detected": False},
                    "furylord": {"detected": False},
                }

            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                ready_2001.set()
                return {"ok": True, "status": "waiting_for_squad", "active_marches": 2, "total_formations": 2}

            @staticmethod
            def run_boomer_runs(cd, pid, cs, cfg, **kwargs):
                ready_2002.set()
                return {"ok": True, "status": "waiting_for_squad", "active_marches": 1, "total_formations": 2}

        self.hub.bot_actions = _MultiPidBA
        self.backend.probe_map_kills_status(pid=2001)
        self.backend.probe_map_kills_status(pid=2002)
        self.backend.start_rss_gather_loop("diamonds", {"pid": 2001, "_wait_squad_delay_sec": 0.2})
        self.backend.start_map_kills_loop("boomers", {"pid": 2002, "_wait_squad_delay_sec": 0.2})
        self.assertTrue(ready_2001.wait(timeout=2.0))
        self.assertTrue(ready_2002.wait(timeout=2.0))

        # Select PID 2001 -> must NOT leak PID 2002's active kills loop or detection!
        self.backend.selected_client_pid = 2001
        fl_2001 = self.backend.get_state()["farm_loops"]
        self.assertEqual(len(fl_2001["active_loops"]), 2)
        self.assertEqual(fl_2001["selected_pid"], 2001)
        self.assertEqual(fl_2001["rss"]["pid"], 2001)
        self.assertTrue(fl_2001["rss"]["running"])
        self.assertEqual(fl_2001["kills"]["pid"], 2001)
        self.assertFalse(fl_2001["kills"]["running"])
        self.assertEqual(fl_2001["detection"]["pid"], 2001)
        self.assertTrue(fl_2001["detection"]["saga"]["detected"])

        # Switch to PID 2002 -> must show 2002's kills loop & detection, and idle RSS for 2002!
        self.backend.selected_client_pid = 2002
        fl_2002 = self.backend.get_state()["farm_loops"]
        self.assertEqual(fl_2002["selected_pid"], 2002)
        self.assertEqual(fl_2002["rss"]["pid"], 2002)
        self.assertFalse(fl_2002["rss"]["running"])
        self.assertEqual(fl_2002["kills"]["pid"], 2002)
        self.assertTrue(fl_2002["kills"]["running"])
        self.assertEqual(fl_2002["detection"]["pid"], 2002)
        self.assertFalse(fl_2002["detection"]["saga"]["detected"])

        stop_all = self.backend.stop_all_farm_loops()
        self.assertTrue(stop_all["ok"])
        self.assertEqual(set(stop_all["stopped_pids"]), {2001, 2002})

    def test_dry_run_auto_stops_and_shutdown_stops_all_active_loops(self) -> None:
        """Verify dry_run=True auto-stops with dry_run_complete and shutdown() stops all active loops cleanly."""
        self._set_clients([
            {"pid": 3001, "role": "main", "label": "Main"},
            {"pid": 3002, "role": "farm", "label": "Farm1"},
        ])
        self.backend.selected_client_pid = 3001
        dry_flags: list[bool] = []

        class _DryAndShutdownBA:
            @staticmethod
            def detect_map_kill_targets(cd, pid):
                return {"ok": True, "boomers": {"detected": True}, "standalone_npc": {"detected": True}, "saga": {"detected": False}, "tyrant": {"detected": False}, "furylord": {"detected": False}}

            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                dry_flags.append(bool(kwargs.get("dry_run")))
                return {
                    "ok": True,
                    "status": "dispatched",
                    "dispatched_count": 1,
                    "dispatched": [{"formationUuid": "f1", "pointId": 9101, "resourceType": kwargs.get("resource_type", "Diamonds")}],
                }

            @staticmethod
            def run_boomer_runs(cd, pid, cs, cfg, dry_run=False, context=None):
                dry_flags.append(bool(dry_run))
                return {"ok": True, "status": "dispatched", "dispatched_count": 1, "dispatched": [{"formationUuid": "f1", "pointId": 9102}]}

            @staticmethod
            def run_standalone_npc_step(cd, pid, cs, cfg, dry_run=False, context=None, **kwargs):
                dry_flags.append(bool(dry_run))
                return {"ok": True, "status": "dispatched", "dispatched_count": 1, "dispatched": [{"formationUuid": "f2", "pointId": 9103}]}

        self.hub.bot_actions = _DryAndShutdownBA
        # 1. Dry-run RSS priority queue
        self.backend.start_rss_gather_loop("priority_queue", {"pid": 3001, "priority": ["Diamonds", "Wood"], "dry_run": True})
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["rss"]["running"]))
        self.assertEqual(self.backend.get_state()["farm_loops"]["rss"]["stop_reason"], "dry_run_complete")

        # 2. Dry-run Map Kills chain
        self.backend.start_map_kills_loop("all_chain", {"pid": 3001, "dry_run": True})
        self.assertTrue(self._wait_until(lambda: not self.backend.get_state()["farm_loops"]["kills"]["running"]))
        self.assertEqual(self.backend.get_state()["farm_loops"]["kills"]["stop_reason"], "dry_run_complete")
        self.assertTrue(all(dry_flags) and len(dry_flags) >= 4)

        # 3. Live loops on 3001 & 3002 stopped cleanly by shutdown()
        w1 = threading.Event()
        w2 = threading.Event()

        class _SlowWaitBA:
            @staticmethod
            def run_rss_gather_step(cd, pid, cs, cfg, **kwargs):
                w1.set()
                return {"ok": True, "status": "waiting_for_squad", "active_marches": 1, "total_formations": 2}

            @staticmethod
            def run_boomer_runs(cd, pid, cs, cfg, **kwargs):
                w2.set()
                return {"ok": True, "status": "waiting_for_squad", "active_marches": 1, "total_formations": 2}

        self.hub.bot_actions = _SlowWaitBA
        self.backend.start_rss_gather_loop("diamonds", {"pid": 3001, "_wait_squad_delay_sec": 5.0})
        self.backend.start_map_kills_loop("boomers", {"pid": 3002, "_wait_squad_delay_sec": 5.0})
        self.assertTrue(w1.wait(timeout=2.0) and w2.wait(timeout=2.0))
        self.assertEqual(len(self.backend.get_state()["farm_loops"]["active_loops"]), 2)

        self.backend.shutdown()
        fl_after = self.backend.get_state()["farm_loops"]
        self.assertEqual(fl_after["active_loops"], [])
        self.backend.selected_client_pid = 3001
        self.assertEqual(self.backend.get_state()["farm_loops"]["rss"]["stop_reason"], "shutdown")
        self.backend.selected_client_pid = 3002
        self.assertEqual(self.backend.get_state()["farm_loops"]["kills"]["stop_reason"], "shutdown")


# =============================================================================
# Layer 4: UI & Guardrail Contracts
# =============================================================================
class TestRssAndMapKillsUiContracts(unittest.TestCase):
    """Tier 2: Verify #view-rss, #view-kills, JS clamping/scoping via Node, HTML uniqueness, and zero prohibited terms."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX_HTML_PATH.read_text(encoding="utf-8")
        cls.hub_src = HUB_PY_PATH.read_text(encoding="utf-8")
        cls.ba_src = BOT_ACTIONS_PY_PATH.read_text(encoding="utf-8")
        cls.node_bin = shutil.which("node")
        if not cls.node_bin:
            raise AssertionError("node executable is required on PATH for UI JS validation")

    def test_view_rss_and_view_kills_dom_cards_pills_and_controls(self) -> None:
        """Verify #view-rss and #view-kills sections, all resource/kill cards, live pills, and stopAllFarmLoops."""
        self.assertIn('data-view="rss"', self.html)
        self.assertIn('data-view="kills"', self.html)
        self.assertIn('id="nav-dot-rss"', self.html)
        self.assertIn('id="nav-dot-kills"', self.html)

        m_rss = re.search(r'<section[^>]*id="view-rss".*?</section>', self.html, flags=re.S)
        m_kills = re.search(r'<section[^>]*id="view-kills".*?</section>', self.html, flags=re.S)
        self.assertIsNotNone(m_rss, "#view-rss section missing")
        self.assertIsNotNone(m_kills, "#view-kills section missing")
        rss_html = m_rss.group(0)
        kills_html = m_kills.group(0)

        for mode in ("diamonds", "electricity", "zent", "wood", "food", "priority_queue"):
            self.assertIn(f'data-rss-mode="{mode}"', rss_html)
            self.assertIn(f'id="btn-rss-{mode}"', rss_html)
            self.assertIn(f'id="rss-count-{mode}"', rss_html)
        for res_id in ("rss-prio-diamonds", "rss-prio-electricity", "rss-prio-zent", "rss-prio-wood", "rss-prio-food"):
            self.assertIn(f'id="{res_id}"', rss_html)
        self.assertRegex(rss_html, re.compile(r'id="rss-min-lvl"[^>]*min="1"[^>]*max="15"'))
        self.assertRegex(rss_html, re.compile(r'id="rss-max-lvl"[^>]*min="1"[^>]*max="15"'))
        self.assertIn('onclick="stopAllFarmLoops()"', rss_html)

        for mode in ("boomers", "standalone_npc", "saga", "tyrant", "furylord", "all_chain"):
            self.assertIn(f'data-kill-mode="{mode}"', kills_html)
            self.assertIn(f'id="btn-kills-{mode}"', kills_html)
            self.assertIn(f'id="kills-count-{mode}"', kills_html)
        for pill_id in ("det-boomers", "det-npc", "det-saga", "det-tyrant", "det-furylord"):
            self.assertIn(f'id="{pill_id}"', kills_html)
        for badge_id in ("kills-det-boomers", "kills-det-standalone_npc", "kills-det-saga", "kills-det-tyrant", "kills-det-furylord"):
            self.assertIn(f'id="{badge_id}"', kills_html)
        for cb_id in ("chain-boomers", "chain-standalone_npc", "chain-saga", "chain-tyrant", "chain-furylord", "kills-prio-bosses", "kills-saga-summon"):
            self.assertIn(f'id="{cb_id}"', kills_html)
        self.assertRegex(kills_html, re.compile(r'id="kills-min-stamina"[^>]*min="0"[^>]*max="5000"'))
        self.assertIn('onclick="stopAllFarmLoops()"', kills_html)

    def test_js_clamping_scoping_and_stop_all_farm_loops_execution_in_node(self) -> None:
        """Execute extracted JS functions in Node.js to prove Lv1..15 cap, 5000 stamina clamp, PID scoping, and stopAllFarmLoops()."""
        needed_fns = [
            _extract_js_function(self.html, r"function\s+_farmSelectedPid\s*\("),
            _extract_js_function(self.html, r"function\s+_farmScopePid\s*\("),
            _extract_js_function(self.html, r"function\s+_farmLoopForTarget\s*\("),
            _extract_js_function(self.html, r"function\s+_farmDetectionForTarget\s*\("),
            _extract_js_function(self.html, r"function\s+_clampLoopInt\s*\("),
            _extract_js_function(self.html, r"function\s+readRssLoopOptions\s*\("),
            _extract_js_function(self.html, r"function\s+readKillLoopOptions\s*\("),
            _extract_js_function(self.html, r"async\s+function\s+stopAllFarmLoops\s*\("),
        ]
        for fn_src in needed_fns:
            self.assertTrue(fn_src, "Missing expected JS helper in index.html")

        m_meta = re.search(r"const _RSS_LOOP_META\s*=\s*\{.*?\};", self.html, flags=re.S)
        self.assertIsNotNone(m_meta)

        harness_js = "\n".join(
            [
                "const assert = require('assert');",
                m_meta.group(0),
                "const _dom = {};",
                "function _domRef(id) { return _dom[id] || null; }",
                "let _liveKillDetection = {};",
                "let _farmLoopTransientErr = { rss: 'stale err', kills: 'stale err2' };",
                "const _apiCalls = [];",
                "let _refreshCount = 0;",
                "async function callApi(name, ...args) { _apiCalls.push({ name, args }); return { ok: true }; }",
                "async function refreshState() { _refreshCount += 1; }",
                *needed_fns,
                """
                (async () => {
                  // 1. RSS level cap 1..15 + min/max swap + priority checkboxes
                  _dom['rss-min-lvl'] = { value: '99' };
                  _dom['rss-max-lvl'] = { value: '0' };
                  _dom['rss-max-dist'] = { value: '99999' };
                  _dom['rss-reserve'] = { value: '-3' };
                  _dom['rss-prio-diamonds'] = { checked: true };
                  _dom['rss-prio-electricity'] = { checked: false };
                  _dom['rss-prio-zent'] = { checked: true };
                  _dom['rss-prio-wood'] = { checked: false };
                  _dom['rss-prio-food'] = { checked: true };

                  const rOpts = readRssLoopOptions('priority_queue');
                  assert.strictEqual(rOpts.min_level, 1);
                  assert.strictEqual(rOpts.max_level, 15);
                  assert.strictEqual(rOpts.max_distance, 1500);
                  assert.strictEqual(rOpts.reserve, 0);
                  assert.deepStrictEqual(rOpts.priority, ['Diamonds', 'Zent', 'Food']);

                  // Swaps when min > max inside valid bounds
                  _dom['rss-min-lvl'] = { value: '12' };
                  _dom['rss-max-lvl'] = { value: '4' };
                  const rSwap = readRssLoopOptions('diamonds');
                  assert.strictEqual(rSwap.min_level, 4);
                  assert.strictEqual(rSwap.max_level, 12);
                  assert.deepStrictEqual(rSwap.priority, ['Diamonds']);

                  // 2. Kill options 5000 stamina clamp + chain checkboxes
                  _dom['kills-min-stamina'] = { value: '12345' };
                  _dom['kills-reserve'] = { value: '25' };
                  _dom['kills-boomer-min'] = { value: '0' };
                  _dom['kills-boomer-max'] = { value: '99' };
                  _dom['kills-npc-min'] = { value: '30' };
                  _dom['kills-npc-max'] = { value: '15' };
                  _dom['kills-saga-summon'] = { checked: true };
                  _dom['kills-prio-bosses'] = { checked: true };
                  _dom['chain-boomers'] = { checked: true };
                  _dom['chain-standalone_npc'] = { checked: false };
                  _dom['chain-saga'] = { checked: true };
                  _dom['chain-tyrant'] = { checked: true };
                  _dom['chain-furylord'] = { checked: false };

                  const kOpts = readKillLoopOptions();
                  assert.strictEqual(kOpts.min_stamina, 5000);
                  assert.strictEqual(kOpts.reserve, 10);
                  assert.strictEqual(kOpts.boomer_min_level, 1);
                  assert.strictEqual(kOpts.boomer_max_level, 10);
                  assert.strictEqual(kOpts.npc_min_level, 15);
                  assert.strictEqual(kOpts.npc_max_level, 30);
                  assert.strictEqual(kOpts.allow_summon_saga, true);
                  assert.strictEqual(kOpts.prioritize_detected_bosses, true);
                  assert.deepStrictEqual(kOpts.chain, ['boomers', 'saga', 'tyrant']);

                  // 3. Multi-account PID scoping never leaks another PID's loop or detection
                  const flMismatch = {
                    selected_pid: 2001,
                    rss: { pid: 2002, running: true, mode: 'diamonds' },
                    detection: { pid: 2002, ok: true, saga: { detected: true } },
                  };
                  const scopedLoop = _farmLoopForTarget(flMismatch, 'rss');
                  assert.strictEqual(scopedLoop.pid, 2001);
                  assert.strictEqual(scopedLoop.running, false);
                  assert.deepStrictEqual(_farmDetectionForTarget(flMismatch), {});

                  // 4. stopAllFarmLoops clears transient errors and invokes stop_all_farm_loops
                  await stopAllFarmLoops();
                  assert.strictEqual(_farmLoopTransientErr.rss, '');
                  assert.strictEqual(_farmLoopTransientErr.kills, '');
                  assert.strictEqual(_apiCalls.length, 1);
                  assert.strictEqual(_apiCalls[0].name, 'stop_all_farm_loops');
                  assert.strictEqual(_refreshCount, 1);
                })().catch((e) => { console.error(e); process.exit(1); });
                """,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            js_file = Path(tmp) / "testFarmUi.js"
            js_file.write_text(harness_js, encoding="utf-8")
            proc = subprocess.run(
                [self.node_bin, str(js_file)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0, f"Node UI test failed:\n{proc.stderr}\n{proc.stdout}")

    def test_index_html_zero_duplicate_ids(self) -> None:
        """Verify launcher/web/index.html has zero duplicate HTML id attributes."""
        all_ids = re.findall(r'\bid\s*=\s*"([^"]+)"', self.html)
        counts: dict[str, int] = {}
        for item in all_ids:
            counts[item] = counts.get(item, 0) + 1
        dups = {k: v for k, v in counts.items() if v > 1}
        self.assertEqual(dups, {}, f"Duplicate HTML IDs in index.html: {dups}")

    def test_index_html_node_check_exits_zero(self) -> None:
        """Verify every <script> block in launcher/web/index.html passes `node --check` with exit 0."""
        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", self.html, flags=re.S | re.I)
        self.assertGreater(len(scripts), 0)
        with tempfile.TemporaryDirectory() as tmp:
            for idx, body in enumerate(scripts):
                if not body.strip():
                    continue
                js_path = Path(tmp) / f"script_{idx}.js"
                js_path.write_text(body, encoding="utf-8")
                proc = subprocess.run(
                    [self.node_bin, "--check", str(js_path)],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(
                    proc.returncode,
                    0,
                    f"node --check failed on <script> #{idx}:\n{proc.stderr}\n{proc.stdout}",
                )

    def test_zero_forbidden_terms_in_farm_ui_hub_bot_and_suite(self) -> None:
        """Verify zero forbidden terminology across RSS/Map Kills UI, Hub loop engine, bot actions, and this test file."""
        term1_re = re.compile(r"\bcom" + r"mander\b", re.I)
        term2_re = re.compile(r"cour" + r"age\s+bad" + r"ges?", re.I)

        snippets: list[tuple[str, str]] = []
        for view_id in ("view-rss", "view-kills"):
            m = re.search(rf'<section[^>]*id="{view_id}".*?</section>', self.html, flags=re.S)
            self.assertIsNotNone(m)
            snippets.append((f"index.html#{view_id}", m.group(0)))

        js_start = self.html.find("/* === RSS GATHERING & MAP KILLS CONTINUOUS LOOP ENGINE === */")
        self.assertNotEqual(js_start, -1)
        snippets.append(("index.html#farm_js", self.html[js_start:]))

        for fn in (
            ba.run_rss_gather_step,
            ba.run_standalone_npc_step,
            ba.run_boomer_runs,
            ba.run_saga_kill_step,
            ba.run_tyrant_event,
            ba.run_furylord,
            ba.detect_map_kill_targets,
        ):
            snippets.append((f"bot_actions.{fn.__name__}", inspect.getsource(fn)))

        hub_mod = _load_hub_module()
        for fn_name in (
            "start_rss_gather_loop",
            "_rss_gather_loop_worker",
            "stop_rss_gather_loop",
            "probe_map_kills_status",
            "start_map_kills_loop",
            "_map_kills_loop_worker",
            "stop_map_kills_loop",
            "stop_all_farm_loops",
        ):
            snippets.append((f"hub.{fn_name}", inspect.getsource(getattr(hub_mod.HubBackend, fn_name))))

        snippets.append(("testRssAndMapKills.py", Path(__file__).read_text(encoding="utf-8")))

        violations: list[str] = []
        for label, text in snippets:
            if term1_re.search(text) or term2_re.search(text):
                violations.append(label)
        self.assertEqual(violations, [], f"Forbidden terminology found in: {violations}")

    def test_zero_em_dashes_across_ui_hub_and_bot_actions(self) -> None:
        """Verify zero em dashes (U+2014 or HTML entities) remain across UI, Hub backend, and bot actions."""
        targets = [
            PROJECT_ROOT / "launcher" / "web" / "index.html",
            PROJECT_ROOT / "launcher" / "heinzhubweb.py",
            PROJECT_ROOT / "tools" / "bot actions.py",
        ]
        bad_patterns = (
            ("U+2014", "\u2014"),
            ("&" + "mdash;", "&" + "mdash;"),
            ("&#8212;", "&#8212;"),
            ("&#x2014;", "&#x2014;"),
        )
        violations: list[str] = []
        for path in targets:
            text = path.read_text(encoding="utf-8")
            low = text.lower()
            for label, needle in bad_patterns:
                if needle in (text if label == "U+2014" else low):
                    violations.append(f"{path.name}:{label}")
        self.assertEqual(violations, [], f"Em dashes found in: {violations}")

    def test_game_icons_bootstrap_injection_and_hydrated_node_check(self) -> None:
        """Verify _load_html_with_assets() injects real Last Z game icons and hydrated JS passes node --check."""
        hub_mod = _load_hub_module()
        manifest_path = PROJECT_ROOT / "launcher" / "assets" / "game icons" / "manifest.json"
        self.assertTrue(manifest_path.is_file(), f"Missing game icons manifest: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        core_keys = set(manifest.get("core", {}).keys())
        for req_key in (
            "zent", "diamonds", "electricity", "wood", "food", "fuel",
            "boomer", "npc", "saga", "tyrant", "furylord", "map_kills_chain",
            "shield", "hospital", "hq", "radar", "troops", "tech", "chest", "badge",
        ):
            self.assertIn(req_key, core_keys, f"Missing required core game icon key: {req_key}")

        hydrated_html = hub_mod._load_html_with_assets()
        self.assertNotIn("/*__GAME_ICONS_BOOTSTRAP__*/", hydrated_html)
        self.assertIn("window.__GAME_ICONS__", hydrated_html)
        self.assertIn("window.__GAME_HERO_ICONS__", hydrated_html)
        self.assertIn("window.__GAME_ITEM_ICONS__", hydrated_html)
        self.assertIn("data:image/webp;base64,", hydrated_html)

        # Verify all static data-game-icon keys in HTML exist in manifest.core
        static_keys = set(re.findall(r'data-game-icon="([^"]+)"', self.html))
        self.assertGreaterEqual(len(static_keys), 20)
        missing_keys = sorted(k for k in static_keys if k not in core_keys)
        self.assertEqual(missing_keys, [], f"Unknown data-game-icon keys in index.html: {missing_keys}")

        # Verify hydrated <script> passes node --check
        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", hydrated_html, flags=re.S | re.I)
        self.assertGreater(len(scripts), 0)
        with tempfile.TemporaryDirectory() as tmp:
            for idx, body in enumerate(scripts):
                if not body.strip():
                    continue
                js_path = Path(tmp) / f"hydrated_script_{idx}.js"
                js_path.write_text(body, encoding="utf-8")
                proc = subprocess.run(
                    [self.node_bin, "--check", str(js_path)],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(proc.returncode, 0, f"Hydrated node --check failed:\n{proc.stderr}")

        # Verify WebView2 Navigate(file:///) cache writer + <2MB NavigateToString compact fallback
        ui_url = hub_mod._write_hydrated_html_cache(hydrated_html)
        self.assertTrue(ui_url.startswith("file:///"), f"Expected file:/// URI, got: {ui_url}")
        compact_html = hub_mod._load_html_with_assets(include_heavy_packs=False)
        self.assertLess(
            len(compact_html.encode("utf-8")),
            1_950_000,
            "Compact fallback HTML must stay under WebView2's 2 MB NavigateToString limit",
        )


if __name__ == "__main__":
    unittest.main()
