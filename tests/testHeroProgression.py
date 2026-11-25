"""Hero Progression Automation & Heroes Hub Contract Tests (Milestone 3).

Covers:
1. Lua 5.4 (lupa) + MockCD wire-packet contracts for HeroEquipInstall, HeroRankUpgrade,
   HeroLvBeyond, HeroLvUp, HeroSkillUpgrade, HeroEquipUpgrade, HeroEquipPromoteUp,
   HeroSPEquipUpgrade, and HeroSPEquipBreak.
2. Strict safety guards: universal shard guard & reserve, EXP/book/alloy/Power Core
   reserves, Lv23+ promote material (230126) guard, opt-in SP weapon guard, empty costEquipArr.
3. VS Hero Day guard & word-boundary keyword matching (+ rushDataDay probe fallback).
4. Target scope filtering, invalid module rejection, detail_lines & summary formatting.
5. Hermetic HubBackend endpoints (get_heroes_overview, save_hero_progression_rules,
   run_hero_progression_now) with TemporaryDirectory + patched config I/O.
6. #view-heroes DOM IDs & zero forbidden terminology audit.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import os
import re
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ba = importlib.import_module("tools.bot actions")
mcb = importlib.import_module("tools.multi client bot")

try:
    from lupa import LuaRuntime
    HAS_LUPA = True
except ImportError:
    HAS_LUPA = False


def _load_hub_module():
    spec = importlib.util.spec_from_file_location("test_hub_hp_mod", str(PROJECT_ROOT / "launcher" / "heinzhubweb.py"))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _make_lupa_runtime() -> Any:
    """Create a Lua 5.4 runtime mocking Last Z globals for Hero Progression execution."""
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(
        """
        _G.sent_packets = {}
        _G.hem_calls = {}
        _G.hsp_calls = {}
        _G.__hzPopupLog = {}

        _G.MsgDefines = {
            HeroEquipInstall = 'hero.equip.install',
            HeroRankUpgrade = 'upgrade.hero.rank',
            HeroLvBeyond = 'upgrade.hero',
            HeroLvUp = 'hero.exp',
            HeroSkillUpgrade = 'survival.hero.skill.upgrade',
            HeroEquipUpgrade = 'hero.equip.upgrade',
            HeroEquipPromoteUp = 'hero.equip.promote.up',
            HeroSPEquipUpgrade = 'hero.equip.unique.upgrade',
            HeroSPEquipBreak = 'hero.equip.unique.break',
        }

        _G.SFSNetwork = {
            SendMessage = function(cmd, ...)
                local args = {...}
                table.insert(_G.sent_packets, {cmd = cmd, args = args, argc = select('#', ...)})
            end
        }

        _G.DataCenter = {
            HeroEquipManager = {
                HeroEquipInstall = function(self, hid, eqArr)
                    table.insert(_G.hem_calls, {method = 'HeroEquipInstall', hid = hid, eqArr = eqArr})
                end,
                HeroEquipUpgrade = function(self, eqNum, costGoods, costEquipArr)
                    table.insert(_G.hem_calls, {
                        method = 'HeroEquipUpgrade',
                        eqNum = eqNum,
                        costGoods = costGoods,
                        costEquipArr = costEquipArr,
                    })
                end,
                HeroEquipPromote = function(self, eqNum, costEquipArr, repNum)
                    table.insert(_G.hem_calls, {
                        method = 'HeroEquipPromote',
                        eqNum = eqNum,
                        costEquipArr = costEquipArr,
                        repNum = repNum,
                    })
                end,
            },
            HeroSPEquipManager = {
                HeroEquipUpgrade = function(self, hid, useUni, extra)
                    table.insert(_G.hsp_calls, {method = 'HeroEquipUpgrade', hid = hid, useUni = useUni, extra = extra})
                end,
            },
        }
        """
    )
    return lua


class _LupaHeroCD:
    """MockCD executing run_hero_progression action chunks in real Lua 5.4 (lupa)."""

    def __init__(
        self,
        inspection_payload: dict[str, Any],
        *,
        use_hem_methods: bool = True,
        probe_payload: dict[str, Any] | None = None,
    ) -> None:
        self.inspection_payload = inspection_payload
        self.probe_payload = probe_payload
        self.recorded_lua: list[str] = []
        self.lua = _make_lupa_runtime() if HAS_LUPA else None
        if self.lua is not None and not use_hem_methods:
            self.lua.execute("_G.DataCenter.HeroEquipManager = nil; _G.DataCenter.HeroSPEquipManager = nil")

    def frida_eval_lua(self, pid: int, lua_code: str, timeout: float = 8.0) -> tuple[bool, str]:
        self.recorded_lua.append(lua_code)
        # Inspection pass returns the synthetic hero/material snapshot
        if "HeroDataManager" in lua_code and "HeroLevelUpTemplateManager" in lua_code:
            return True, json.dumps(self.inspection_payload)
        # Lightweight server weekday probe (Fix 2)
        if "_get_server_weekday" in lua_code and "HeroDataManager" not in lua_code:
            wday = self.inspection_payload.get("server_wday", 5)
            dname = self.inspection_payload.get("server_day_name", "Thursday" if wday == 5 else "Wednesday")
            return True, json.dumps({"ok": True, "server_wday": wday, "server_day_name": dname})
        # Lightweight Full Preparedness / VS probe (Fix 1 / Fix 2)
        if "ActPersonalArmsInfo" in lua_code and "HeroDataManager" not in lua_code:
            if self.probe_payload is not None:
                return True, json.dumps(self.probe_payload)
            ev = self.inspection_payload.get("event_status") or {}
            if ev.get("hero_day_active"):
                return True, json.dumps({"theme": ev.get("active_theme") or "Hero Progression", "vs_day": 0})
            return True, json.dumps({"theme": "", "theme_raw": "", "vs_theme": "", "vs_open": False, "vs_day": 0})
        if self.lua is None:
            return True, json.dumps({"ok": True})
        raw = self.lua.execute(lua_code)
        return True, str(raw)


def _sample_inspection(
    *,
    server_wday: int = 5,
    hero_day_active: bool = True,
    heroes: list[dict[str, Any]] | None = None,
    materials: dict[str, Any] | None = None,
) -> dict[str, Any]:
    default_mats = {
        "hero_exp_total": 5_000_000,
        "hero_exp_items": [
            {"itemId": 220101, "uuid": "exp-item-uuid-1", "count": 100, "expVal": 100_000},
        ],
        "skill_books": {"orange": 50, "purple": 50, "blue": 50, "total": 150},
        "universal_shards": {"orange": 0, "purple": 0, "blue": 0, "total": 0, "by_color": {}},
        "enhancement_alloy_total": 500,
        "enhancement_alloy_exp_total": 50_000,
        "enhancement_alloy_items": [
            {"itemId": 230001, "count": 500, "expVal": 100},
        ],
        "power_cores": 2000,
        "universal_equip_materials": 0,
        "universal_sp_shards": 0,
        "universal_break_minerals": 0,
        "zent": 10_000_000,
    }
    if materials:
        default_mats.update(materials)
    return {
        "ok": True,
        "server_wday": server_wday,
        "server_day_name": "Thursday" if server_wday == 5 else "Wednesday",
        "hq_max_hero_level": 150,
        "materials": default_mats,
        "heroes": heroes if heroes is not None else [],
        "event_status": {
            "hero_day_active": hero_day_active,
            "reason": "vs_hero_day_thursday" if hero_day_active else "off_hero_day",
            "active_theme": "VS Day 4: Hero Initiative" if hero_day_active else "",
            "server_day_name": "Thursday" if server_wday == 5 else "Wednesday",
        },
        "summary": {},
    }


def _sample_hero(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "uuid": "900001001",
        "heroId": 101,
        "name": "Katrina",
        "rarity": 4,
        "formationIndex": 1,
        "level": 80,
        "curMaxLevel": 100,
        "needExp": 50_000,
        "canBreakthrough": False,
        "star": 3,
        "isStarMax": False,
        "needShards": 20,
        "ownedShards": 0,
        "hasBetterGear": False,
        "suggestGearUuids": [],
        "skills": [],
        "gear": [],
        "spEquip": {"has": False, "active": False, "level": 0, "canUpgrade": False, "canBreak": False},
    }
    base.update(overrides)
    return base


def _make_isolated_hub(hub_mod: Any, tmp_dir: str) -> Any:
    backend = hub_mod.HubBackend.__new__(hub_mod.HubBackend)
    backend._lock = threading.RLock()
    backend._log_seq = 0
    backend.logs = []
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
    backend.env = {}
    return backend


class TestHeroProgression(unittest.TestCase):
    """Tier 1: Hero Progression Automation & Heroes Hub Contracts."""

    # ------------------------------------------------------------------
    # 1. Lua & Packet Contracts (lupa 2.8 + MockCD)
    # ------------------------------------------------------------------
    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_equip_install_numeric_uuids(self) -> None:
        """Verify HeroEquipInstall converts numeric equip UUIDs via tonumber and rejects non-numeric/empty."""
        hero_ok = _sample_hero(hasBetterGear=True, suggestGearUuids=["81001", "81002", "bad_id"])
        insp_ok = _sample_inspection(heroes=[hero_ok])
        cd_ok = _LupaHeroCD(insp_ok, use_hem_methods=True)
        cfg = {"hero_progression": {"only_hero_day": True, "target_scope": "formation_1"}}

        with patch("time.sleep"):
            res = ba.run_hero_progression(cd_ok, 1001, {}, cfg, dry_run=False, context={"only_module": "gear"})

        self.assertTrue(res["ok"])
        self.assertEqual(len(res["gear_installed"]), 1)
        hem_calls = cd_ok.lua.eval("_G.hem_calls")
        self.assertEqual(len(hem_calls), 1)
        call = hem_calls[1]
        self.assertEqual(call["method"], "HeroEquipInstall")
        self.assertEqual(call["hid"], 101)
        eq_arr = [call["eqArr"][i] for i in range(1, len(call["eqArr"]) + 1)]
        self.assertEqual(eq_arr, [81001, 81002])
        self.assertTrue(all(isinstance(x, int) for x in eq_arr))

        # SFSNetwork fallback path when HeroEquipManager absent
        cd_sfs = _LupaHeroCD(insp_ok, use_hem_methods=False)
        with patch("time.sleep"):
            res_sfs = ba.run_hero_progression(cd_sfs, 1001, {}, cfg, dry_run=False, context={"only_module": "gear"})
        self.assertTrue(res_sfs["ok"])
        pkts = cd_sfs.lua.eval("_G.sent_packets")
        self.assertEqual(pkts[1]["cmd"], "hero.equip.install")

        # Non-numeric equip UUIDs must fail cleanly with 'No numeric equip UUIDs'
        hero_bad = _sample_hero(hasBetterGear=True, suggestGearUuids=["abc", "not-num"])
        cd_bad = _LupaHeroCD(_sample_inspection(heroes=[hero_bad]))
        with patch("time.sleep"):
            res_bad = ba.run_hero_progression(cd_bad, 1001, {}, cfg, dry_run=False, context={"only_module": "gear"})
        self.assertEqual(len(res_bad["gear_installed"]), 0)
        self.assertIn("No numeric equip UUIDs", res_bad["errors"])

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_rank_upgrade_numeric_uuid_and_packet(self) -> None:
        """Verify HeroRankUpgrade sends numeric hero UUID and rejects non-numeric hero UUIDs."""
        hero = _sample_hero(uuid="7700123456", needShards=10, ownedShards=15)
        cd = _LupaHeroCD(_sample_inspection(heroes=[hero]))
        cfg = {"hero_progression": {"only_hero_day": True, "target_scope": "formation_1"}}

        with patch("time.sleep"):
            res = ba.run_hero_progression(cd, 1001, {}, cfg, dry_run=False, context={"only_module": "star"})
        self.assertTrue(res["ok"])
        self.assertEqual(len(res["star_ups"]), 1)
        pkts = cd.lua.eval("_G.sent_packets")
        self.assertEqual(len(pkts), 1)
        self.assertEqual(pkts[1]["cmd"], "upgrade.hero.rank")
        self.assertEqual(pkts[1]["args"][1], 7700123456)
        self.assertIsInstance(pkts[1]["args"][1], int)
        self.assertEqual(pkts[1]["args"][2], 0)

        hero_bad = _sample_hero(uuid="non_numeric_uuid", needShards=10, ownedShards=15)
        cd_bad = _LupaHeroCD(_sample_inspection(heroes=[hero_bad]))
        with patch("time.sleep"):
            res_bad = ba.run_hero_progression(cd_bad, 1001, {}, cfg, dry_run=False, context={"only_module": "star"})
        self.assertEqual(len(res_bad["star_ups"]), 0)
        self.assertIn("Invalid numeric hero UUID", res_bad["errors"])

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_lv_up_and_breakthrough_packets_and_exp_reserve(self) -> None:
        """Verify HeroLvBeyond and HeroLvUp packets and exp_reserve_millions guard."""
        hero = _sample_hero(
            uuid="88001122",
            level=80,
            curMaxLevel=100,
            needExp=200_000,
            canBreakthrough=True,
        )
        # 5M EXP total with exp_reserve_millions=5 -> spendable=0 -> LvUp blocked, LvBeyond allowed
        insp = _sample_inspection(
            heroes=[hero],
            materials={
                "hero_exp_total": 5_000_000,
                "hero_exp_items": [{"itemId": 220101, "uuid": "exp-item-uuid-1", "count": 50, "expVal": 100_000}],
            },
        )
        cd = _LupaHeroCD(insp)
        cfg_blocked = {
            "hero_progression": {
                "only_hero_day": True,
                "exp_reserve_millions": 5,
            }
        }
        with patch("time.sleep"):
            res1 = ba.run_hero_progression(cd, 1001, {}, cfg_blocked, dry_run=False, context={"only_module": "level"})
        self.assertEqual(len(res1["breakthroughs"]), 1)
        self.assertEqual(len(res1["level_ups"]), 0)
        pkts1 = cd.lua.eval("_G.sent_packets")
        self.assertEqual(pkts1[1]["cmd"], "upgrade.hero")
        self.assertEqual(pkts1[1]["args"][1], 88001122)

        # With exp_reserve_millions=4 -> 1M spendable >= 200k needExp -> both LvBeyond and LvUp fire
        cd2 = _LupaHeroCD(insp)
        cfg_ok = {
            "hero_progression": {
                "only_hero_day": True,
                "exp_reserve_millions": 4,
            }
        }
        with patch("time.sleep"):
            res2 = ba.run_hero_progression(cd2, 1001, {}, cfg_ok, dry_run=False, context={"only_module": "level"})
        self.assertEqual(len(res2["breakthroughs"]), 1)
        self.assertEqual(len(res2["level_ups"]), 1)
        pkts2 = cd2.lua.eval("_G.sent_packets")
        self.assertEqual(pkts2[1]["cmd"], "upgrade.hero")
        self.assertEqual(pkts2[2]["cmd"], "hero.exp")
        self.assertEqual(pkts2[2]["args"][1], 88001122)
        self.assertEqual(pkts2[2]["args"][2], "exp-item-uuid-1")
        self.assertEqual(pkts2[2]["args"][3], 2)

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_skill_upgrade_packet_and_book_reserve(self) -> None:
        """Verify HeroSkillUpgrade packet, rem_books.setdefault tracking, and skill_book_reserve."""
        hero = _sample_hero(
            uuid="55112233",
            skills=[
                {"index": 1, "name": "Skill A", "level": 3, "canUpgrade": True, "itemId": 230999, "costNum": 15, "ownedItem": 30},
                {"index": 2, "name": "Skill B", "level": 2, "canUpgrade": True, "itemId": 230999, "costNum": 10, "ownedItem": 30},
            ],
        )
        cd = _LupaHeroCD(_sample_inspection(heroes=[hero]))
        # Reserve = 10 -> Skill 1: 30 - 15 = 15 >= 10 (allowed, rem becomes 15);
        # Skill 2: 15 - 10 = 5 < 10 (blocked via rem_books.setdefault tracking!)
        cfg = {"hero_progression": {"only_hero_day": True, "skill_book_reserve": 10}}
        with patch("time.sleep"):
            res = ba.run_hero_progression(cd, 1001, {}, cfg, dry_run=False, context={"only_module": "skill"})

        self.assertEqual(len(res["skill_ups"]), 1)
        self.assertEqual(res["skill_ups"][0]["skillIndex"], 1)
        pkts = cd.lua.eval("_G.sent_packets")
        self.assertEqual(len(pkts), 1)
        self.assertEqual(pkts[1]["cmd"], "survival.hero.skill.upgrade")
        self.assertEqual(pkts[1]["args"][1], 55112233)
        self.assertEqual(pkts[1]["args"][2], 1)

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_equip_upgrade_cost_goods_format_and_alloy_reserve(self) -> None:
        """Verify HeroEquipUpgrade costGoods is {{goodsId=..., num=...}}, costEquipArr={}, eqNum is numeric, and alloy_reserve works."""
        hero = _sample_hero(
            gear=[
                {"uuid": "99001", "slot": 1, "quality": 5, "level": 10, "maxLevel": 40, "needExp": 500, "canUpgrade": True},
                {"uuid": "99002", "slot": 2, "quality": 5, "level": 10, "maxLevel": 40, "needExp": 500, "canUpgrade": True},
            ]
        )
        insp = _sample_inspection(
            heroes=[hero],
            materials={
                "enhancement_alloy_total": 18,
                "enhancement_alloy_items": [{"itemId": 230001, "count": 18, "expVal": 100}],
            },
        )
        cd = _LupaHeroCD(insp, use_hem_methods=True)
        # Reserve 10 -> budget is 8 alloy -> slot 1 needs 5 (leaves 13), slot 2 needs 5 (13 - 10 = 3 < 5 -> skipped!)
        cfg = {"hero_progression": {"only_hero_day": True, "alloy_reserve": 10, "min_gear_quality": 5}}
        with patch("time.sleep"):
            res = ba.run_hero_progression(cd, 1001, {}, cfg, dry_run=False, context={"only_module": "gear"})

        self.assertEqual(len(res["gear_upgraded"]), 1)
        self.assertEqual(res["gear_upgraded"][0]["equipUuid"], "99001")
        self.assertEqual(res["gear_upgraded"][0]["alloyUsed"], 5)

        hem_calls = cd.lua.eval("_G.hem_calls")
        self.assertEqual(len(hem_calls), 1)
        call = hem_calls[1]
        self.assertEqual(call["method"], "HeroEquipUpgrade")
        self.assertEqual(call["eqNum"], 99001)
        self.assertIsInstance(call["eqNum"], int)
        # costEquipArr MUST be empty {}
        self.assertEqual(len(call["costEquipArr"]), 0)
        # costGoods MUST be array of {goodsId='230001', num=5}
        cg = call["costGoods"]
        self.assertEqual(len(cg), 1)
        self.assertEqual(cg[1]["goodsId"], "230001")
        self.assertEqual(cg[1]["num"], 5)

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_equip_promote_lv23_fodder_and_core_reserves(self) -> None:
        """Verify HeroEquipPromoteUp Lv<23 vs Lv>=23 replacement 230126 guard, power_core_reserve, and empty costEquipArr."""
        # Case A: promoteLevel=10 (<23), core cost=500, reserve=100, power_cores=600 -> succeeds with rep_num=0
        hero_a = _sample_hero(
            gear=[{"uuid": "91001", "slot": 1, "quality": 5, "promoteLevel": 10, "canPromote": True}]
        )
        cd_a = _LupaHeroCD(_sample_inspection(heroes=[hero_a], materials={"power_cores": 600, "universal_equip_materials": 0}))
        cfg_a = {"hero_progression": {"only_hero_day": True, "power_core_reserve": 100, "use_replacement_equip": False}}
        with patch("time.sleep"):
            res_a = ba.run_hero_progression(cd_a, 1001, {}, cfg_a, dry_run=False, context={"only_module": "gear_promote"})
        self.assertEqual(len(res_a["gear_promoted"]), 1)
        self.assertEqual(res_a["gear_promoted"][0]["replacementUsed"], 0)
        hem_a = cd_a.lua.eval("_G.hem_calls")[1]
        self.assertEqual(hem_a["method"], "HeroEquipPromote")
        self.assertEqual(len(hem_a["costEquipArr"]), 0)
        self.assertEqual(hem_a["repNum"], 0)

        # Case B: power_core_reserve blocks promote when cores < est_core_cost + reserve
        cd_low_core = _LupaHeroCD(_sample_inspection(heroes=[hero_a], materials={"power_cores": 550}))
        with patch("time.sleep"):
            res_low = ba.run_hero_progression(cd_low_core, 1001, {}, cfg_a, dry_run=False, context={"only_module": "gear_promote"})
        self.assertEqual(len(res_low["gear_promoted"]), 0)
        self.assertTrue(any("Power Cores below reserve" in s for s in res_low["skipped_reasons"]))

        # Case C: Lv23/26/29 require 1/2/3 Universal Equip Material (230126) and opt-in use_replacement_equip=True
        for prom_lv, req_rep in ((23, 1), (26, 2), (29, 3)):
            hero_hi = _sample_hero(
                gear=[{"uuid": "92001", "slot": 1, "quality": 5, "promoteLevel": prom_lv, "canPromote": True}]
            )
            # Disabled -> skipped
            cd_off = _LupaHeroCD(_sample_inspection(heroes=[hero_hi], materials={"power_cores": 5000, "universal_equip_materials": 5}))
            with patch("time.sleep"):
                res_off = ba.run_hero_progression(
                    cd_off, 1001, {},
                    {"hero_progression": {"only_hero_day": True, "use_replacement_equip": False}},
                    dry_run=False, context={"only_module": "gear_promote"},
                )
            self.assertEqual(len(res_off["gear_promoted"]), 0)
            self.assertTrue(any("use_replacement_equip" in s for s in res_off["skipped_reasons"]))

            # Enabled but insufficient 230126 -> skipped
            cd_short = _LupaHeroCD(_sample_inspection(heroes=[hero_hi], materials={"power_cores": 5000, "universal_equip_materials": req_rep - 1}))
            with patch("time.sleep"):
                res_short = ba.run_hero_progression(
                    cd_short, 1001, {},
                    {"hero_progression": {"only_hero_day": True, "use_replacement_equip": True}},
                    dry_run=False, context={"only_module": "gear_promote"},
                )
            self.assertEqual(len(res_short["gear_promoted"]), 0)
            self.assertTrue(any("230126" in s for s in res_short["skipped_reasons"]))

            # Enabled and sufficient -> fires with rep_num == req_rep and empty costEquipArr
            cd_ok = _LupaHeroCD(_sample_inspection(heroes=[hero_hi], materials={"power_cores": 5000, "universal_equip_materials": req_rep}))
            with patch("time.sleep"):
                res_ok = ba.run_hero_progression(
                    cd_ok, 1001, {},
                    {"hero_progression": {"only_hero_day": True, "use_replacement_equip": True}},
                    dry_run=False, context={"only_module": "gear_promote"},
                )
            self.assertEqual(len(res_ok["gear_promoted"]), 1)
            self.assertEqual(res_ok["gear_promoted"][0]["replacementUsed"], req_rep)
            hem_ok = cd_ok.lua.eval("_G.hem_calls")[1]
            self.assertEqual(len(hem_ok["costEquipArr"]), 0)
            self.assertEqual(hem_ok["repNum"], req_rep)

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_hero_sp_equip_upgrade_and_breakthrough(self) -> None:
        """Verify HeroSPEquipUpgrade (260000) and HeroSPEquipBreak (214000) opt-in & universal shard guards."""
        hero = _sample_hero(
            heroId=105,
            spEquip={"has": True, "active": True, "level": 5, "canUpgrade": True, "lackCount": 4, "canBreak": True, "breakLackCount": 2},
        )
        insp = _sample_inspection(
            heroes=[hero],
            materials={"universal_sp_shards": 5, "universal_break_minerals": 3},
        )

        # Default allow_sp_equip=False skips SP module when running full sweep
        cd_off = _LupaHeroCD(insp)
        with patch("time.sleep"):
            res_off = ba.run_hero_progression(
                cd_off, 1001, {},
                {"hero_progression": {"only_hero_day": True, "allow_sp_equip": False, "upgrade_levels": False, "upgrade_stars": False, "upgrade_skills": False, "auto_equip_best": False, "upgrade_gear": False}},
                dry_run=False,
            )
        self.assertEqual(len(res_off["sp_upgraded"]), 0)

        # only_module='sp_equip' with use_universal_sp_shards=False skips when lack > 0
        cd_no_uni = _LupaHeroCD(insp)
        with patch("time.sleep"):
            res_no_uni = ba.run_hero_progression(
                cd_no_uni, 1001, {},
                {"hero_progression": {"only_hero_day": True, "use_universal_sp_shards": False}},
                dry_run=False, context={"only_module": "sp_equip"},
            )
        self.assertEqual(len(res_no_uni["sp_upgraded"]), 0)
        self.assertTrue(any("260000" in s for s in res_no_uni["skipped_reasons"]))
        self.assertTrue(any("214000" in s for s in res_no_uni["skipped_reasons"]))

        # only_module='sp_equip' with use_universal_sp_shards=True fires both upgrade & break
        cd_uni = _LupaHeroCD(insp)
        with patch("time.sleep"):
            res_uni = ba.run_hero_progression(
                cd_uni, 1001, {},
                {"hero_progression": {"only_hero_day": True, "use_universal_sp_shards": True}},
                dry_run=False, context={"only_module": "sp_equip"},
            )
        self.assertEqual(len(res_uni["sp_upgraded"]), 2)
        hsp_calls = cd_uni.lua.eval("_G.hsp_calls")
        self.assertEqual(hsp_calls[1]["method"], "HeroEquipUpgrade")
        self.assertEqual(hsp_calls[1]["hid"], 105)
        self.assertEqual(hsp_calls[1]["useUni"], 4)
        pkts = cd_uni.lua.eval("_G.sent_packets")
        self.assertEqual(pkts[1]["cmd"], "hero.equip.unique.break")
        self.assertEqual(pkts[1]["args"][1], 105)
        self.assertEqual(pkts[1]["args"][2], 2)

    # ------------------------------------------------------------------
    # 2. Universal Shard Guard
    # ------------------------------------------------------------------
    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_universal_shard_guard_strict_default_and_reserve(self) -> None:
        """Verify universal shards are blocked by default and reserve is enforced across multiple heroes."""
        h1 = _sample_hero(uuid="7001", heroId=101, name="Hero1", rarity=4, needShards=30, ownedShards=10)  # deficit 20
        h2 = _sample_hero(uuid="7002", heroId=102, name="Hero2", rarity=4, needShards=20, ownedShards=10)  # deficit 10
        insp = _sample_inspection(
            heroes=[h1, h2],
            materials={"universal_shards": {"orange": 75, "purple": 0, "blue": 0, "total": 75}},
        )

        # Default use_universal_shards=False -> 0 star-ups
        cd_default = _LupaHeroCD(insp)
        with patch("time.sleep"):
            res_def = ba.run_hero_progression(
                cd_default, 1001, {}, {"hero_progression": {"only_hero_day": True}},
                dry_run=False, context={"only_module": "star"},
            )
        self.assertEqual(len(res_def["star_ups"]), 0)

        # Enabled with reserve=50 and pool=75 -> h1 uses 20 (remaining=55 >= 50 OK), h2 needs 10 (55-10=45 < 50 BLOCKED)
        cd_res = _LupaHeroCD(insp)
        with patch("time.sleep"):
            res_en = ba.run_hero_progression(
                cd_res, 1001, {},
                {"hero_progression": {"only_hero_day": True, "use_universal_shards": True, "universal_shard_reserve": 50}},
                dry_run=False, context={"only_module": "star"},
            )
        self.assertEqual(len(res_en["star_ups"]), 1)
        self.assertEqual(res_en["star_ups"][0]["heroId"], 101)
        self.assertEqual(res_en["star_ups"][0]["universalUsed"], 20)

    # ------------------------------------------------------------------
    # 3. VS Hero Day & Preparedness Probe Guard
    # ------------------------------------------------------------------
    def test_vs_hero_day_guard_and_word_boundary_keywords(self) -> None:
        """Verify VS Hero Day triggers, word-boundary keyword guards, day=2 isolation, force flag, and rushDataDay fallback."""
        act_thu, r_thu, _ = ba._is_hero_progression_event_active({}, server_wday=5)
        self.assertTrue(act_thu)
        self.assertEqual(r_thu, "vs_hero_day_thursday")

        act_vs4, r_vs4, _ = ba._is_hero_progression_event_active({"vs_open": True, "vs_day": 4}, server_wday=3)
        self.assertTrue(act_vs4)
        self.assertEqual(r_vs4, "vs_hero_day_4")

        act_fp, r_fp, _ = ba._is_hero_progression_event_active(
            {"ok": True, "theme": "Hero Progression", "score_labels": [], "vs_day": 0},
            server_wday=3,
        )
        self.assertTrue(act_fp)
        self.assertIn("active_theme:", r_fp)

        # Word-boundary guard: 'Start Building' / 'Starter Pack' must NOT match 'star'
        act_start, r_start, _ = ba._is_hero_progression_event_active(
            {"ok": True, "theme": "Start Building", "score_labels": ["Starter Pack"], "vs_day": 0},
            server_wday=3,
        )
        self.assertFalse(act_start)
        self.assertEqual(r_start, "off_hero_day")

        # vs_day == 2 labels must NOT trigger false positive
        act_vs2, _, _ = ba._is_hero_progression_event_active(
            {"ok": True, "theme": "Build Tech", "vs_day": 2, "vs_open": True, "vs_theme": "Hero Upgrade", "vs_score_labels": ["Hero Shard"]},
            server_wday=3,
        )
        self.assertFalse(act_vs2)

        # run_hero_progression skips on off-day unless force_ignore_day_guard=True
        off_insp = _sample_inspection(server_wday=3, hero_day_active=False, heroes=[_sample_hero(needShards=5, ownedShards=10)])
        cd_off = _LupaHeroCD(off_insp)
        with patch("time.sleep"):
            res_skip = ba.run_hero_progression(cd_off, 1001, {}, {"hero_progression": {"only_hero_day": True}}, dry_run=True)
        self.assertEqual(res_skip["action"], "skipped_not_hero_day")
        self.assertEqual(res_skip["total_actions"], 0)

        with patch("time.sleep"):
            res_force = ba.run_hero_progression(
                cd_off, 1001, {}, {"hero_progression": {"only_hero_day": True}},
                dry_run=True, context={"only_module": "star", "force_ignore_day_guard": True},
            )
        self.assertEqual(res_force["action"], "upgraded")
        self.assertEqual(len(res_force["star_ups"]), 1)

        # Verify _probe_preparedness_phase carries rushDataDay fallback
        src_probe = inspect.getsource(ba._probe_preparedness_phase)
        self.assertIn("tonumber(acm.rushDataDay)", src_probe)

    # ------------------------------------------------------------------
    # 4. Target Filtering, Invalid Module & Telemetry
    # ------------------------------------------------------------------
    def test_target_scope_filtering_and_invalid_module(self) -> None:
        """Verify _filter_hero_progression_targets, invalid only_module rejection, detail_lines, and task summary."""
        heroes = [
            _sample_hero(uuid="1001", heroId=1, name="F1Orange", rarity=4, formationIndex=1),
            _sample_hero(uuid="1002", heroId=2, name="F2Orange", rarity=4, formationIndex=2),
            _sample_hero(uuid="1003", heroId=3, name="IdlePurple", rarity=3, formationIndex=0),
            _sample_hero(uuid="1004", heroId=4, name="IdleBlue", rarity=2, formationIndex=0),
        ]

        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="formation_1", min_rarity=4)], [1])
        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="all_formations", min_rarity=4)], [1, 2])
        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="pinned", pinned_hero_ids=[3, 1])], [1, 3])
        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="all_orange", min_rarity=2)], [1, 2])
        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="all", min_rarity=3)], [1, 2, 3])
        self.assertEqual(ba._filter_hero_progression_targets(heroes, target_scope="hero_uuid", single_hero_uuid=""), [])
        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="hero_uuid", single_hero_uuid="1003")], [3])
        self.assertEqual([h["heroId"] for h in ba._filter_hero_progression_targets(heroes, target_scope="formation_1", single_hero_uuid="2")], [2])

        # Invalid module rejected cleanly
        cd_inv = _LupaHeroCD(_sample_inspection(heroes=heroes))
        res_inv = ba.run_hero_progression(cd_inv, 1001, {}, {}, dry_run=True, context={"only_module": "bogus"})
        self.assertFalse(res_inv["ok"])
        self.assertEqual(res_inv["action"], "invalid_module")

        # _build_detail_lines & _format_task_summary for active and skipped results
        active_res = {
            "ok": True,
            "action": "upgraded",
            "total_actions": 2,
            "level_ups": [{"heroName": "Katrina", "fromLv": 80, "count": 2, "expSpent": 200000}],
            "breakthroughs": [],
            "star_ups": [{"heroName": "Katrina", "star": 3, "universalUsed": 0}],
            "skill_ups": [],
            "gear_installed": [],
            "gear_upgraded": [],
            "gear_promoted": [],
            "sp_upgraded": [],
            "skipped_reasons": [],
            "server_day_name": "Thursday",
            "target_scope": "formation_1",
        }
        lines_act = ba._build_detail_lines("hero_progression", active_res)
        self.assertTrue(len(lines_act) >= 3)
        self.assertIn("total=2", lines_act[0])
        summary_act = mcb._format_task_summary("hero_progression", active_res)
        self.assertIn("hero progression 2 action(s)", summary_act)

        skip_res = {
            "ok": True,
            "action": "skipped_not_hero_day",
            "reason": "Waiting for Alliance Duel Day 4",
            "total_actions": 0,
            "skipped_reasons": ["Waiting for Alliance Duel Day 4"],
        }
        lines_skip = ba._build_detail_lines("hero_progression", skip_res)
        self.assertTrue(len(lines_skip) >= 1)
        self.assertIn("action=skipped_not_hero_day", lines_skip[0])
        summary_skip = mcb._format_task_summary("hero_progression", skip_res)
        self.assertIn("Waiting for Alliance Duel Day 4", summary_skip)

    # ------------------------------------------------------------------
    # 5. HubBackend Endpoints (Hermetic TemporaryDirectory)
    # ------------------------------------------------------------------
    def test_hub_get_heroes_overview_offline_cache_and_fallback(self) -> None:
        """Verify get_heroes_overview handles empty fallback and cached JSON without touching repo data/."""
        hub = _load_hub_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_file = Path(tmp_dir) / "bot config.json"
            cache_dir = Path(tmp_dir) / "json cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cfg_file.write_text(json.dumps(mcb.default_config()), encoding="utf-8")

            backend = _make_isolated_hub(hub, tmp_dir)
            backend._discover_running_clients = lambda: []

            orig_data, orig_heinz = hub.DATA_DIR, hub.HEINZ_DATA_DIR
            hub_mcb = hub.multi_client_bot
            orig_load, orig_save = hub_mcb.load_config, hub_mcb.save_config
            try:
                hub.DATA_DIR = tmp_dir
                hub.HEINZ_DATA_DIR = tmp_dir
                hub_mcb.load_config = lambda config_path=cfg_file: orig_load(cfg_file)
                hub_mcb.save_config = lambda cfg, config_path=cfg_file: orig_save(cfg, cfg_file)

                # Empty offline fallback
                ov_empty = backend.get_heroes_overview()
                self.assertTrue(ov_empty["ok"])
                self.assertFalse(ov_empty["is_linked"])
                self.assertFalse(ov_empty["is_live"])
                self.assertFalse(ov_empty["auto_run_main"])
                self.assertTrue(ov_empty["auto_run_farm"])

                # Seeded main_heroes_overview.json
                seeded = _sample_inspection(heroes=[_sample_hero(name="CachedHero")])
                seeded["account_name"] = "MainTest"
                (cache_dir / "main_heroes_overview.json").write_text(json.dumps(seeded), encoding="utf-8")

                ov_cached = backend.get_heroes_overview()
                self.assertTrue(ov_cached["ok"])
                self.assertTrue(ov_cached["is_linked"])
                self.assertFalse(ov_cached["is_live"])
                self.assertEqual(len(ov_cached["heroes"]), 1)
                self.assertEqual(ov_cached["heroes"][0]["name"], "CachedHero")
                self.assertFalse(ov_cached["auto_run_main"])
                self.assertTrue(ov_cached["auto_run_farm"])
            finally:
                hub.DATA_DIR, hub.HEINZ_DATA_DIR = orig_data, orig_heinz
                hub_mcb.load_config, hub_mcb.save_config = orig_load, orig_save

    def test_hub_save_hero_progression_rules_sanitization_and_preservation(self) -> None:
        """Verify save_hero_progression_rules sanitizes invalid fields and preserves main_tasks when omitted."""
        hub = _load_hub_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_file = Path(tmp_dir) / "bot config.json"
            cfg_file.write_text(json.dumps(mcb.default_config()), encoding="utf-8")
            backend = _make_isolated_hub(hub, tmp_dir)

            orig_data, orig_heinz = hub.DATA_DIR, hub.HEINZ_DATA_DIR
            hub_mcb = hub.multi_client_bot
            orig_load, orig_save = hub_mcb.load_config, hub_mcb.save_config
            try:
                hub.DATA_DIR = tmp_dir
                hub.HEINZ_DATA_DIR = tmp_dir
                hub_mcb.load_config = lambda config_path=cfg_file: orig_load(cfg_file)
                hub_mcb.save_config = lambda cfg, config_path=cfg_file: orig_save(cfg, cfg_file)

                bad_res = backend.save_hero_progression_rules(["not", "a", "dict"])  # type: ignore[arg-type]
                self.assertFalse(bad_res["ok"])
                self.assertIn("expected dict", bad_res["error"])

                dirty_payload = {
                    "only_hero_day": None,
                    "target_scope": "invalid_scope",
                    "min_rarity": 99,
                    "max_actions_per_cycle": 999,
                    "min_gear_quality": 0,
                    "pinned_hero_ids": 12345,  # non-iterable
                    "use_universal_shards": "false",
                    "universal_shard_reserve": True,  # bool rejected for int -> default 50
                }
                saved = backend.save_hero_progression_rules(dirty_payload)
                self.assertTrue(saved["ok"])
                self.assertFalse(saved["auto_run_main"])
                self.assertTrue(saved["auto_run_farm"])
                rules = saved["rules"]
                self.assertTrue(rules["only_hero_day"])
                self.assertEqual(rules["target_scope"], "formation_1")
                self.assertEqual(rules["min_rarity"], 5)
                self.assertEqual(rules["max_actions_per_cycle"], 100)
                self.assertEqual(rules["min_gear_quality"], 1)
                self.assertEqual(rules["pinned_hero_ids"], [])
                self.assertFalse(rules["use_universal_shards"])
                self.assertEqual(rules["universal_shard_reserve"], 50)

                # Explicit auto_run_main=True updates main_tasks
                saved2 = backend.save_hero_progression_rules({"auto_run_main": True, "pinned_hero_ids": [101, "102", True]})
                self.assertTrue(saved2["ok"])
                self.assertTrue(saved2["auto_run_main"])
                self.assertEqual(saved2["rules"]["pinned_hero_ids"], [101, 102])
            finally:
                hub.DATA_DIR, hub.HEINZ_DATA_DIR = orig_data, orig_heinz
                hub_mcb.load_config, hub_mcb.save_config = orig_load, orig_save

    def test_hub_run_hero_progression_now_modes_and_pid_isolation(self) -> None:
        """Verify run_hero_progression_now handles modes, strict PID isolation, and concurrency lock."""
        hub = _load_hub_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_file = Path(tmp_dir) / "bot config.json"
            cfg_file.write_text(json.dumps(mcb.default_config()), encoding="utf-8")
            backend = _make_isolated_hub(hub, tmp_dir)

            # Invalid module rejected immediately
            res_bad_mod = backend.run_hero_progression_now(only_module="unknown_mod")
            self.assertFalse(res_bad_mod["ok"])
            self.assertIn("Unknown only_module", res_bad_mod["error"])

            # Strict PID isolation: requesting non-running PID 99999 must NOT fall back to Main PID 23848
            main_proc = {"pid": 23848, "role": "main", "label": "Main", "exe": "LastZ.exe"}
            backend._discover_running_clients = lambda: [main_proc]
            backend._client_display_name = lambda p: p.get("label", "Main") if p else ""

            orig_data, orig_heinz = hub.DATA_DIR, hub.HEINZ_DATA_DIR
            hub_mcb = hub.multi_client_bot
            orig_load, orig_save = hub_mcb.load_config, hub_mcb.save_config
            orig_ba = hub.bot_actions
            orig_cd = hub.client_discovery

            class _FakeCD:
                @staticmethod
                def _xlua_loaded(pid: int) -> bool:
                    return pid == 23848

            calls_log: list[dict[str, Any]] = []

            class _FakeBA:
                @staticmethod
                def run_hero_progression(cd, pid, client_state, cfg, dry_run=False, context=None):
                    calls_log.append({"pid": pid, "dry_run": dry_run, "context": dict(context or {})})
                    return {
                        "ok": True,
                        "action": "upgraded",
                        "total_actions": 1,
                        "level_ups": [], "breakthroughs": [], "star_ups": [], "skill_ups": [],
                        "gear_installed": [], "gear_upgraded": [], "gear_promoted": [], "sp_upgraded": [],
                        "skipped_reasons": [],
                    }

            try:
                hub.DATA_DIR = tmp_dir
                hub.HEINZ_DATA_DIR = tmp_dir
                hub_mcb.load_config = lambda config_path=cfg_file: orig_load(cfg_file)
                hub_mcb.save_config = lambda cfg, config_path=cfg_file: orig_save(cfg, cfg_file)
                hub.bot_actions = _FakeBA
                hub.client_discovery = _FakeCD

                res_wrong_pid = backend.run_hero_progression_now(pid=99999, dry_run=True)
                self.assertFalse(res_wrong_pid["ok"])
                self.assertIn("99999", res_wrong_pid["error"])
                self.assertEqual(len(calls_log), 0)

                # Concurrency lock guard
                backend._active_actions.add("hero_progression:23848")
                res_locked = backend.run_hero_progression_now(pid=23848, dry_run=True)
                self.assertFalse(res_locked["ok"])
                self.assertIn("already running", res_locked["error"])
                backend._active_actions.clear()

                # Dry-run, single-hero, single-module, and full sweep
                r_dry = backend.run_hero_progression_now(pid=23848, dry_run=True)
                self.assertTrue(r_dry["ok"])
                self.assertTrue(r_dry["dry_run"])
                self.assertEqual(calls_log[-1]["pid"], 23848)
                self.assertTrue(calls_log[-1]["dry_run"])

                r_single = backend.run_hero_progression_now(pid=23848, dry_run=False, hero_uuid="90001", only_module="skill", force_ignore_day_guard=True)
                self.assertTrue(r_single["ok"])
                self.assertEqual(calls_log[-1]["context"], {"hero_uuid": "90001", "only_module": "skill", "force_ignore_day_guard": True})

                r_full = backend.run_hero_progression_now(pid=23848, dry_run=False)
                self.assertTrue(r_full["ok"])
                self.assertEqual(calls_log[-1]["context"], {"hero_uuid": "", "only_module": "", "force_ignore_day_guard": False})
            finally:
                hub.DATA_DIR, hub.HEINZ_DATA_DIR = orig_data, orig_heinz
                hub_mcb.load_config, hub_mcb.save_config = orig_load, orig_save
                hub.bot_actions = orig_ba
                hub.client_discovery = orig_cd

    # ------------------------------------------------------------------
    # 6. #view-heroes DOM & Terminology Contract
    # ------------------------------------------------------------------
    def test_view_heroes_dom_ids_and_zero_forbidden_terms(self) -> None:
        """Verify #view-heroes DOM IDs, uniqueness, and zero forbidden terminology across hero code & UI."""
        html = (PROJECT_ROOT / "launcher" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-view="heroes"', html)
        self.assertIn('id="view-heroes"', html)

        required_ids = [
            "heroes-account-pill", "heroes-event-badge", "heroes-kpi-grid",
            "heroes-kpi-exp", "heroes-kpi-shards", "heroes-kpi-skills", "heroes-kpi-gear",
            "hp-loop-main", "hp-loop-farm", "hp-only-hero-day", "hp-force-ignore-day",
            "hp-target-scope", "hp-min-rarity", "hp-max-actions",
            "hp-upgrade-levels", "hp-allow-breakthrough", "hp-target-level-cap", "hp-exp-reserve",
            "hp-upgrade-stars", "hp-use-universal-shards", "hp-universal-shard-reserve",
            "hp-upgrade-skills", "hp-skill-book-reserve",
            "hp-auto-equip-best", "hp-upgrade-gear", "hp-min-gear-quality", "hp-alloy-reserve",
            "hp-allow-gear-promote", "hp-power-core-reserve", "hp-use-replacement-equip",
            "hp-allow-sp-equip", "hp-use-universal-sp-shards",
            "heroes-run-result-panel", "heroes-filter-pills", "heroes-rarity-filter",
            "heroes-search-input", "heroes-sort-select", "heroes-roster-grid",
        ]
        all_ids = re.findall(r'\bid\s*=\s*"([^"]+)"', html)
        self.assertEqual(len(all_ids), len(set(all_ids)), "Duplicate HTML IDs found in index.html")
        for req_id in required_ids:
            self.assertIn(req_id, all_ids, f"Missing required #view-heroes ID: {req_id}")

        # Forbidden terminology checks (zero forbidden badge/rank terms in hero UI & hero_progression code)
        bad_badge_re = re.compile(r"courage\s+" + r"badge", re.I)
        bad_rank_re = re.compile(r"\bcomm" + r"ander\b", re.I)
        m_pane = re.search(r'<section[^>]*id="view-heroes".*?</section>', html, flags=re.S)
        self.assertIsNotNone(m_pane)
        pane_html = m_pane.group(0)
        self.assertNotRegex(pane_html, bad_badge_re)
        self.assertNotRegex(pane_html, bad_rank_re)

        hp_ba_src = inspect.getsource(ba.inspect_hero_progression) + "\n" + inspect.getsource(ba.run_hero_progression)
        self.assertNotRegex(hp_ba_src, bad_badge_re)
        self.assertNotRegex(hp_ba_src, bad_rank_re)

    # ------------------------------------------------------------------
    # 7. Regression Tests (Fixes 1-6)
    # ------------------------------------------------------------------
    def test_fix1_probe_missing_ok_and_theme_only_matching(self) -> None:
        """Fix 1: _is_hero_progression_event_active works without 'ok', rejects error dicts, and ignores score_labels."""
        # (a) Live-style probe dict omitting "ok"
        act_live, r_live, th_live = ba._is_hero_progression_event_active(
            {"theme": "Hero Progression", "vs_day": 0},
            server_wday=3,
        )
        self.assertTrue(act_live)
        self.assertEqual(r_live, "active_theme:hero")
        self.assertEqual(th_live, "Hero Progression")

        # (b) Non-hero theme with hero keywords in score_labels / vs_score_labels -> False
        act_lbl, r_lbl, _ = ba._is_hero_progression_event_active(
            {
                "theme": "Base Construction",
                "theme_raw": "1001",
                "vs_theme": "Building Speed",
                "score_labels": ["Hero Shard", "Recruit Hero"],
                "vs_score_labels": ["Hero Upgrade"],
                "vs_day": 0,
            },
            server_wday=3,
        )
        self.assertFalse(act_lbl)
        self.assertEqual(r_lbl, "off_hero_day")

        # (c) Error dict with hero theme -> False
        act_err, r_err, _ = ba._is_hero_progression_event_active(
            {"ok": False, "error": "timeout", "theme": "Hero Progression", "vs_day": 0},
            server_wday=3,
        )
        self.assertFalse(act_err)
        self.assertEqual(r_err, "off_hero_day")

    def test_fix2_off_day_early_exit_skips_full_roster_scan(self) -> None:
        """Fix 2: run_hero_progression exits before inspect_hero_progression on off-day (dry & live); force flag overrides."""
        off_insp = _sample_inspection(
            server_wday=3,
            hero_day_active=False,
            heroes=[_sample_hero(needShards=5, ownedShards=10)],
        )
        required_keys = {
            "ok", "task", "dry_run", "target_scope", "only_hero_day", "force_ignore_day_guard",
            "only_module", "hero_uuid", "event_active", "event_reason", "active_theme",
            "server_day_name", "heroes_scanned", "heroes_matched", "level_ups", "breakthroughs",
            "star_ups", "skill_ups", "gear_installed", "gear_upgraded", "gear_promoted",
            "sp_upgraded", "total_actions", "skipped_reasons", "skipped", "errors",
            "send_errors", "in_game_tips", "popped_modals", "action", "reason",
        }
        for dry_flag in (False, True):
            cd_off = _LupaHeroCD(off_insp)
            res = ba.run_hero_progression(cd_off, 1001, {}, {"hero_progression": {"only_hero_day": True}}, dry_run=dry_flag)
            self.assertTrue(res["ok"])
            self.assertEqual(res["action"], "skipped_not_hero_day")
            self.assertEqual(res["total_actions"], 0)
            self.assertTrue(required_keys.issubset(res.keys()))
            self.assertFalse(
                any("HeroDataManager" in lua for lua in cd_off.recorded_lua),
                f"Full roster scan should not execute on off-day (dry_run={dry_flag})",
            )

        # force_ignore_day_guard=True must still run inspect_hero_progression
        cd_force = _LupaHeroCD(off_insp)
        with patch("time.sleep"):
            res_force = ba.run_hero_progression(
                cd_force, 1001, {}, {"hero_progression": {"only_hero_day": True}},
                dry_run=True, context={"only_module": "star", "force_ignore_day_guard": True},
            )
        self.assertEqual(res_force["action"], "upgraded")
        self.assertTrue(any("HeroDataManager" in lua for lua in cd_force.recorded_lua))

        # Lightweight probe failure returns inspect_failed with full contract keys
        class _FailWdayCD:
            def frida_eval_lua(self, pid: int, lua_code: str, timeout: float = 8.0) -> tuple[bool, str]:
                return False, "frida timeout"

        res_fail = ba.run_hero_progression(_FailWdayCD(), 1001, {}, {"hero_progression": {"only_hero_day": True}}, dry_run=True)
        self.assertFalse(res_fail["ok"])
        self.assertEqual(res_fail["action"], "inspect_failed")
        self.assertTrue(required_keys.issubset(res_fail.keys()))

    def test_fix3_unified_hero_progression_per_pid_locks(self) -> None:
        """Fix 3: Unify per-PID Hero Progression locks across run_hero_progression_now, run_single_task, and run_bot_cycle."""
        hub = _load_hub_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_file = Path(tmp_dir) / "bot config.json"
            cfg_file.write_text(json.dumps(mcb.default_config()), encoding="utf-8")
            backend = _make_isolated_hub(hub, tmp_dir)

            main_proc = {"pid": 23848, "role": "main", "label": "Main", "exe": "LastZ.exe"}
            farm_proc = {"pid": 23849, "role": "farm", "label": "Farm1", "exe": "LastZ.exe"}
            backend._discover_running_clients = lambda: [main_proc, farm_proc]
            backend._client_display_name = lambda p: p.get("label", "") if p else ""
            backend._refresh_fleet_state = lambda: None

            orig_data, orig_heinz = hub.DATA_DIR, hub.HEINZ_DATA_DIR
            hub_mcb = hub.multi_client_bot
            orig_load, orig_save = hub_mcb.load_config, hub_mcb.save_config
            orig_ba, orig_cd = hub.bot_actions, hub.client_discovery

            class _FakeCD:
                @staticmethod
                def _xlua_loaded(pid: int) -> bool:
                    return pid in (23848, 23849)

            class _FakeBA:
                @staticmethod
                def run_hero_progression(cd, pid, client_state, cfg, dry_run=False, context=None):
                    return {
                        "ok": True, "action": "none", "total_actions": 0,
                        "level_ups": [], "breakthroughs": [], "star_ups": [], "skill_ups": [],
                        "gear_installed": [], "gear_upgraded": [], "gear_promoted": [], "sp_upgraded": [],
                        "skipped_reasons": [],
                    }

            stream_calls: list[Any] = []
            concurrent_results: dict[str, Any] = {}

            def _fake_stream(tool_name, extra, timeout=150, on_line=None):
                stream_calls.append((tool_name, list(extra)))
                # While single_task(Main=23848) holds hero_progression:23848:
                concurrent_results["same_pid"] = backend.run_hero_progression_now(pid=23848, dry_run=True)
                concurrent_results["other_pid"] = backend.run_hero_progression_now(pid=23849, dry_run=True)
                return type("R", (), {"returncode": 0, "stdout": '{"ok": true, "clients": []}', "stderr": ""})()

            try:
                hub.DATA_DIR = tmp_dir
                hub.HEINZ_DATA_DIR = tmp_dir
                hub_mcb.load_config = lambda config_path=cfg_file: orig_load(cfg_file)
                hub_mcb.save_config = lambda cfg, config_path=cfg_file: orig_save(cfg, cfg_file)
                hub.bot_actions = _FakeBA
                hub.client_discovery = _FakeCD
                backend._stream_tool = _fake_stream

                # (a) Active hero_progression:23848 blocks run_single_task(hero_progression, target=Main)
                backend._active_actions.add("hero_progression:23848")
                backend._exec_bg_action("run_single_task", {"task": "hero_progression", "target": "Main", "dry_run": True})
                self.assertEqual(len(stream_calls), 0)
                self.assertTrue(any("already running" in str(x.get("msg", "")).lower() for x in backend.logs))
                backend._active_actions.clear()

                # (b) & (c) run_single_task(hero_progression, Main) blocks pid=23848 but allows disjoint pid=23849
                backend._exec_bg_action("run_single_task", {"task": "hero_progression", "target": "Main", "dry_run": True})
                self.assertEqual(len(stream_calls), 1)
                self.assertFalse(concurrent_results["same_pid"]["ok"])
                self.assertIn("already running", concurrent_results["same_pid"]["error"].lower())
                self.assertTrue(concurrent_results["other_pid"]["ok"])
                self.assertEqual(backend._active_actions, set())
            finally:
                hub.DATA_DIR, hub.HEINZ_DATA_DIR = orig_data, orig_heinz
                hub_mcb.load_config, hub_mcb.save_config = orig_load, orig_save
                hub.bot_actions = orig_ba
                hub.client_discovery = orig_cd

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_fix4_universal_shard_excludes_hero_specific_tp62(self) -> None:
        """Fix 4: inspect_hero_progression classifies universal shards via commonDebrisSet/IsCommonHeroDebris, not tp==62."""
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(
            """
            _G.DataCenter = {
                HeroDataManager = { HeroInfos = {} },
                ItemData = {
                    ItemInfos = {
                        ["u1"] = { itemId = 210454, count = 10 },
                        ["u2"] = { itemId = 210453, count = 7 },
                        ["h1"] = { itemId = 211316, count = 40 },
                    }
                },
                ItemTemplateManager = {
                    GetItemTemplate = function(self, iid)
                        if iid == 210454 then return { type = 62, color = 4, name = "Gold Common Shard" } end
                        if iid == 210453 then return { type = 62, color = 3, name = "Purple Common Shard" } end
                        if iid == 211316 then return { type = 62, color = 4, name = "Katrina Shard" } end
                        return nil
                    end
                },
            }
            _G.HeroUtils = {
                GetAllCommonHeroDebris = function() return { 210454 } end,
                GetGoldHeroDebrisId = function() return 210454 end,
                IsCommonHeroDebris = function(iid) return iid == 210454 or iid == 210453 end,
            }
            """
        )

        class _LupaInspectCD:
            def frida_eval_lua(self, pid: int, lua_code: str, timeout: float = 12.0) -> tuple[bool, str]:
                return True, str(lua.execute(lua_code))

        res = ba.inspect_hero_progression(_LupaInspectCD(), 1001, include_probe=False)
        self.assertTrue(res["ok"])
        uni = res["materials"]["universal_shards"]
        self.assertEqual(uni["orange"], 10)
        self.assertEqual(uni["purple"], 7)
        self.assertEqual(uni["total"], 17)

    @unittest.skipUnless(HAS_LUPA, "lupa Lua 5.4 runtime required")
    def test_fix5_zero_reserves_and_min_rarity_respected(self) -> None:
        """Fix 5: Explicit 0 config values (universal_shard_reserve=0, min_rarity=0, etc.) are respected instead of truthy fallback."""
        h_blue = _sample_hero(uuid="7101", heroId=111, name="BlueHero", rarity=1, needShards=20, ownedShards=0)
        insp = _sample_inspection(
            heroes=[h_blue],
            materials={"universal_shards": {"orange": 20, "purple": 20, "blue": 20, "total": 60}},
        )
        cd = _LupaHeroCD(insp)
        cfg = {
            "hero_progression": {
                "only_hero_day": True,
                "target_scope": "all",
                "min_rarity": 0,
                "use_universal_shards": True,
                "universal_shard_reserve": 0,
                "skill_book_reserve": 0,
                "alloy_reserve": 0,
                "power_core_reserve": 0,
                "max_actions_per_cycle": 0,
            }
        }
        with patch("time.sleep"):
            res = ba.run_hero_progression(cd, 1001, {}, cfg, dry_run=False, context={"only_module": "star"})
        self.assertTrue(res["ok"])
        self.assertEqual(res["heroes_matched"], 1)
        self.assertEqual(len(res["star_ups"]), 1)
        self.assertEqual(res["star_ups"][0]["universalUsed"], 20)

    def test_fix6_heroes_ui_rules_loaded_guard_and_min_rarity_default(self) -> None:
        """Fix 6: #hp-min-rarity defaults to '4' and _heroesRulesLoaded guards save/pin/run against HTML default overwrites."""
        html = (PROJECT_ROOT / "launcher" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<option value="4" selected>Orange (SSR)</option>', html)
        self.assertIn("let _heroesRulesLoaded = false;", html)
        self.assertRegex(html, re.compile(r"if\s*\(\s*!res\s*\|\|\s*typeof res !== \"object\"\s*\|\|\s*res\.ok === false\s*\)\s*return;"))
        self.assertRegex(html, re.compile(r"populateHeroesRuleControls\(res\.rules\);\s*_heroesRulesLoaded\s*=\s*true;"))
        for fn_name in ("saveHeroProgressionRules", "toggleHeroPin", "runHeroesAction"):
            m_fn = re.search(rf"async function {fn_name}\b.*?\n\}}", html, flags=re.S)
            self.assertIsNotNone(m_fn, f"Missing JS function {fn_name}")
            self.assertIn("_heroesRulesLoaded", m_fn.group(0), f"{fn_name} must guard with _heroesRulesLoaded")


if __name__ == "__main__":
    unittest.main()
