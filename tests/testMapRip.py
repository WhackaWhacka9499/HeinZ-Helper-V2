"""Interactive Map Rip Target Finder Backend & UI Contract Tests (Milestone 3).

Covers:
1. _fast_index_to_xy (TileCountX=1000) & _safe_int / _safe_float edge cases.
2. Binary UTF-8 (errors='replace') parsing of world_map_cache_*.json, dummy/non-HQ
   exclusion, buildId==400000 HQ filtering, (serverId, ownerUid) aoiVersion dedup,
   and _s*.json priority vs world_map_cache.json fallback.
3. Exact 121-row _DEFAULT_GATHER_RESOURCE_TABLE vs aps gather resource.json parity,
   RSS occupancy (gatherUuid / ownerUid), special event nodes (1206/1605/1708), and dedup.
4. top10_alliance_rosters.json power enrichment, corrupt file/member isolation, and
   power=None filtering/sorting (None last in both asc & desc).
5. Iterative Dense-Core Hive Extraction alliance clusters (radius, min_members, clamping,
   empty-tag exclusion, scattered rejection).
6. query_map_rip_targets filters/modes/sorts/distance/radar 3000-cap, get_map_rip_overview,
   backward-compatible query_map_targets + CSV fallback, and jump_to_coordinate.
7. #view-map DOM/IDs (all 8 legacy IDs intact), zero duplicate HTML IDs, _mapQuerySeq & esc() XSS guard.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_hub_module():
    spec = importlib.util.spec_from_file_location("test_hub_map_rip_mod", str(PROJECT_ROOT / "launcher" / "heinzhubweb.py"))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


hub = _load_hub_module()


def _xy_to_idx(x: int, y: int, tile_count_x: int = 1000) -> int:
    return y * tile_count_x + x + 1


def _webp_dimensions(raw: bytes) -> tuple[int, int]:
    """Parse (width, height) from a VP8, VP8L, or VP8X WebP RIFF container without external libraries."""
    if len(raw) < 30 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        raise ValueError("Not a valid WebP RIFF payload")
    chunk = raw[12:16]
    if chunk == b"VP8 ":
        if raw[23:26] != b"\x9d\x01\x2a":
            raise ValueError("Invalid VP8 keyframe start code")
        w, h = struct.unpack_from("<HH", raw, 26)
        return (w & 0x3FFF, h & 0x3FFF)
    if chunk == b"VP8L":
        bits = struct.unpack_from("<I", raw, 21)[0]
        return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    if chunk == b"VP8X":
        w = 1 + int.from_bytes(raw[24:27], "little")
        h = 1 + int.from_bytes(raw[27:30], "little")
        return (w, h)
    raise ValueError(f"Unsupported WebP chunk: {chunk!r}")


def _hq_entry(
    idx: int,
    *,
    uid: str,
    name: str = "Player",
    tag: str = "ABC",
    level: int = 25,
    server_id: int = 702,
    protect_end_time: int = 0,
    aoi_version: int = 10,
    last_hp_time: int = 100,
    build_id: int = 400000,
    main_index: int | None = None,
) -> dict[str, Any]:
    return {
        "pointType": 6,
        "serverId": server_id,
        "mainIndex": idx if main_index is None else main_index,
        "pointIndex": idx,
        "aoiVersion": aoi_version,
        "buildInfo": {
            "buildId": build_id,
            "ownerUid": uid,
            "name": name,
            "alAbbr": tag,
            "allianceId": f"al_{tag}" if tag else "",
            "level": level,
            "protectEndTime": protect_end_time,
            "lastHpTime": last_hp_time,
            "buildState": 0,
            "currentHp": 1000,
            "fireEndTime": 0,
        },
    }


def _rss_entry(
    idx: int,
    *,
    resource_id: int,
    server_id: int = 702,
    gather_uuid: int = 0,
    owner_uid: str = "",
    event_id: str = "",
    aoi_version: int = 10,
) -> dict[str, Any]:
    return {
        "pointType": 7,
        "serverId": server_id,
        "mainIndex": idx,
        "pointIndex": idx,
        "aoiVersion": aoi_version,
        "resourceInfo": {
            "resourceId": resource_id,
            "gatherUuid": gather_uuid,
            "ownerUid": owner_uid,
            "eventId": event_id,
        },
    }


class TestMapRipBackend(unittest.TestCase):
    """Tier 1: Hermetic Map Rip backend parser, clustering, query, and jump tests."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = self._tmp.name
        self.cache_dir = Path(self.tmp_dir) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._orig_data_dir = hub.DATA_DIR
        self._orig_heinz_data_dir = hub.HEINZ_DATA_DIR
        self._orig_env_heinz = os.environ.get("HEINZ_DATA_DIR")

        hub.DATA_DIR = self.tmp_dir
        hub.HEINZ_DATA_DIR = self.tmp_dir
        os.environ["HEINZ_DATA_DIR"] = self.tmp_dir
        with hub._MAP_INDEX_LOCK:
            hub._WORLD_MAP_INDEX_CACHE.clear()
        with hub._WORLD_MAPS_LOCK:
            hub._WORLD_MAPS_CACHE["manifest"] = None
            hub._WORLD_MAPS_CACHE["webp"].clear()

        self.backend = hub.HubBackend.__new__(hub.HubBackend)
        self.backend._lock = threading.RLock()
        self.backend._log_seq = 0
        self.backend.logs = []
        self.backend.target_pid = None
        self.backend.selected_client_pid = None
        self.backend.selected_client_label = None
        self.backend._live_info_by_pid = {}
        self.backend._uid_name_cache = {}
        self.backend.env = {}
        self.backend._active_actions = set()
        self.backend._live_sync_ts = {}
        self.backend._world_season_live_cache = {}
        self.backend._discover_running_clients = lambda *a, **kw: []

    def tearDown(self) -> None:
        with hub._MAP_INDEX_LOCK:
            hub._WORLD_MAP_INDEX_CACHE.clear()
        with hub._WORLD_MAPS_LOCK:
            hub._WORLD_MAPS_CACHE["manifest"] = None
            hub._WORLD_MAPS_CACHE["webp"].clear()
        hub.DATA_DIR = self._orig_data_dir
        hub.HEINZ_DATA_DIR = self._orig_heinz_data_dir
        if self._orig_env_heinz is None:
            os.environ.pop("HEINZ_DATA_DIR", None)
        else:
            os.environ["HEINZ_DATA_DIR"] = self._orig_env_heinz
        self._tmp.cleanup()

    def _write_cache_json(self, filename: str, payload: dict[str, Any], raw_bytes: bytes | None = None) -> Path:
        p = self.cache_dir / filename
        if raw_bytes is not None:
            p.write_bytes(raw_bytes)
        else:
            p.write_text(json.dumps(payload), encoding="utf-8")
        return p

    # ------------------------------------------------------------------
    # 1. Coordinate Math & Safe Numeric Parsers
    # ------------------------------------------------------------------
    def test_fast_index_to_xy_and_safe_parsers(self) -> None:
        """Verify _fast_index_to_xy (TileCountX=1000) and _safe_int / _safe_float edge cases."""
        self.assertEqual(hub._fast_index_to_xy(1), (0, 0))
        self.assertEqual(hub._fast_index_to_xy(1001), (0, 1))
        self.assertEqual(hub._fast_index_to_xy(500501), (500, 500))
        self.assertEqual(hub._fast_index_to_xy(0), (0, 0))
        self.assertEqual(hub._fast_index_to_xy(-5), (0, 0))

        for bad in (None, True, False, float("nan"), float("inf"), "1e999", "abc", ""):
            self.assertEqual(hub._safe_int(bad, -99), -99, f"_safe_int failed on {bad!r}")
            self.assertEqual(hub._safe_float(bad, -9.5), -9.5, f"_safe_float failed on {bad!r}")

        self.assertEqual(hub._safe_int("42", 0), 42)
        self.assertEqual(hub._safe_int("42.9", 0), 42)
        self.assertAlmostEqual(hub._safe_float("12.5", 0.0), 12.5)

    # ------------------------------------------------------------------
    # 2. Binary UTF-8 Cache Parsing, HQ Filtering & Dedup
    # ------------------------------------------------------------------
    def test_world_map_cache_binary_utf8_hq_filtering_and_dedup(self) -> None:
        """Verify errors='replace' binary UTF-8 decode, dummy/non-HQ filtering, aoiVersion dedup, and fallback."""
        idx1 = _xy_to_idx(120, 240)
        idx2 = _xy_to_idx(125, 245)
        raw_dict = {
            "123456": {"test": True, "pointType": 6, "serverId": 702, "buildInfo": None},
            str(_xy_to_idx(10, 10)): {
                "pointType": 6, "serverId": 702, "mainIndex": _xy_to_idx(10, 10),
                "buildInfo": {"buildId": 851000, "ownerUid": "u_fort", "name": "Fortress", "level": 30},
            },
            str(_xy_to_idx(20, 20)): {
                "pointType": 6, "serverId": 702, "mainIndex": _xy_to_idx(20, 20),
                "buildInfo": {"buildId": 765000, "ownerUid": "u_struct", "name": "AllianceStruct", "level": 5},
            },
            # Duplicate HQ entries for u100: older vs newer aoiVersion
            str(idx1): _hq_entry(idx1, uid="u100", name="__BAD_UTF8__", tag="TOP", level=26, aoi_version=10, last_hp_time=50),
            str(idx2): _hq_entry(idx2, uid="u100", name="NewPosName", tag="TOP", level=27, aoi_version=25, last_hp_time=100),
        }
        raw_bytes = json.dumps(raw_dict).encode("utf-8").replace(b"__BAD_UTF8__", b"Bad\xff\xfeName")
        self._write_cache_json("world_map_cache_s702.json", {}, raw_bytes=raw_bytes)
        # Also write fallback world_map_cache.json with a distinct player to verify _s*.json takes priority
        self._write_cache_json("world_map_cache.json", {
            str(_xy_to_idx(300, 300)): _hq_entry(_xy_to_idx(300, 300), uid="u_fallback", name="FallbackHQ", level=25)
        })

        idx_dedup = hub._get_world_map_index(self.tmp_dir, dedup_by_uid=True)
        self.assertTrue(idx_dedup["has_world_cache"])
        self.assertEqual(idx_dedup["selected_files"], ["world_map_cache_s702.json"])
        self.assertEqual(idx_dedup["raw_hq_count"], 2)
        self.assertEqual(idx_dedup["deduped_hq_count"], 1)
        self.assertEqual(idx_dedup["collapsed_duplicates"], 1)
        self.assertEqual(len(idx_dedup["hqs"]), 1)
        self.assertEqual((idx_dedup["hqs"][0]["x"], idx_dedup["hqs"][0]["y"]), (125, 245))
        self.assertEqual(idx_dedup["hqs"][0]["level"], 27)

        # dedup_by_uid=False returns all raw HQ tiles while preserving deduped_hq_count=1 and replacement char
        idx_raw = hub._get_world_map_index(self.tmp_dir, dedup_by_uid=False)
        self.assertEqual(len(idx_raw["hqs"]), 2)
        self.assertEqual(idx_raw["deduped_hq_count"], 1)
        self.assertTrue(any("\ufffd" in h["name"] for h in idx_raw["hqs"]))

        # Remove _s702.json -> falls back to world_map_cache.json
        (self.cache_dir / "world_map_cache_s702.json").unlink()
        idx_fb = hub._get_world_map_index(self.tmp_dir, dedup_by_uid=True)
        self.assertEqual(idx_fb["selected_files"], ["world_map_cache.json"])
        self.assertEqual([h["uid"] for h in idx_fb["hqs"]], ["u_fallback"])

    # ------------------------------------------------------------------
    # 3. Gather Resource Table Parity & RSS Occupancy
    # ------------------------------------------------------------------
    def test_gather_resource_table_parity_and_rss_occupancy(self) -> None:
        """Verify 121-row _DEFAULT_GATHER_RESOURCE_TABLE parity with aps gather resource.json and RSS parsing."""
        xml_path = PROJECT_ROOT / "megamind" / "raw" / "xml tables" / "aps gather resource.json"
        rows = json.loads(xml_path.read_text(encoding="utf-8"))["rows"]
        self.assertEqual(len(rows), 121)
        self.assertEqual(len(hub._DEFAULT_GATHER_RESOURCE_TABLE), 121)
        for k, v in rows.items():
            rid = int(k)
            expected_ev = bool(len(v) > 15 and str(v[15] or "").strip()) or (rid in hub._SPECIAL_EVENT_RESOURCE_IDS)
            self.assertEqual(
                hub._DEFAULT_GATHER_RESOURCE_TABLE[rid],
                (int(v[1]), int(v[3]), int(v[4]), expected_ev),
                f"Mismatch for resourceId {rid}",
            )

        idx_open1 = _xy_to_idx(100, 100)
        idx_open2 = _xy_to_idx(101, 100)
        idx_occ_g = _xy_to_idx(102, 100)
        idx_occ_u = _xy_to_idx(103, 100)
        idx_ev1 = _xy_to_idx(104, 100)
        idx_ev2 = _xy_to_idx(105, 100)
        idx_ev3 = _xy_to_idx(106, 100)
        self._write_cache_json("world_map_cache_s702.json", {
            # Duplicate tile at idx_open1: stale occupied vs newer open aoiVersion
            "dup_old": _rss_entry(idx_open1, resource_id=408, gather_uuid=777, owner_uid="888", aoi_version=5),
            str(idx_open1): _rss_entry(idx_open1, resource_id=408, gather_uuid=0, owner_uid="", aoi_version=15),
            str(idx_open2): _rss_entry(idx_open2, resource_id=508, gather_uuid=0, owner_uid="0", aoi_version=10),
            str(idx_occ_g): _rss_entry(idx_occ_g, resource_id=208, gather_uuid=9001, owner_uid="", aoi_version=10),
            str(idx_occ_u): _rss_entry(idx_occ_u, resource_id=308, gather_uuid=0, owner_uid="999", aoi_version=10),
            str(idx_ev1): _rss_entry(idx_ev1, resource_id=1206, gather_uuid=0, owner_uid="", aoi_version=10),
            str(idx_ev2): _rss_entry(idx_ev2, resource_id=1605, gather_uuid=0, owner_uid="", aoi_version=10),
            str(idx_ev3): _rss_entry(idx_ev3, resource_id=1708, gather_uuid=0, owner_uid="", aoi_version=10),
        })

        index = hub._get_world_map_index(self.tmp_dir)
        by_uid = {r["uid"]: r for r in index["rss"]}
        self.assertEqual(len(by_uid), 7)

        r_open1 = by_uid[f"rss:702:{idx_open1}"]
        self.assertFalse(r_open1["occupied"])
        self.assertEqual(r_open1["resource_type"], 2)
        self.assertEqual(r_open1["level"], 8)
        self.assertEqual(r_open1["reserve"], 6_000_000)
        self.assertFalse(r_open1["is_event_node"])

        self.assertFalse(by_uid[f"rss:702:{idx_open2}"]["occupied"])
        self.assertTrue(by_uid[f"rss:702:{idx_occ_g}"]["occupied"])
        self.assertTrue(by_uid[f"rss:702:{idx_occ_u}"]["occupied"])

        for ev_idx in (idx_ev1, idx_ev2, idx_ev3):
            self.assertTrue(by_uid[f"rss:702:{ev_idx}"]["is_event_node"])

    # ------------------------------------------------------------------
    # 4. Roster Power Enrichment, Filtering & Sorting
    # ------------------------------------------------------------------
    def test_roster_power_enrichment_filtering_and_sorting(self) -> None:
        """Verify Top-10 roster power enrichment, corrupt isolation, and power=None filter/sort behavior."""
        roster_dir = Path(self.tmp_dir) / "json cache" / "bracket data" / "state_702"
        roster_dir.mkdir(parents=True, exist_ok=True)
        (roster_dir / "top10_alliance_rosters.json").write_text(
            json.dumps([
                {
                    "rank": 1,
                    "members": [
                        {"uid": "u1", "power": 85_000_000, "armyKill": 1234, "online": True, "curServerId": 702},
                        {"uid": "u2", "power": 42_000_000, "armyKill": 500, "online": False, "curServerId": 702},
                        "corrupt_member_not_dict",
                        {"uid": "", "power": 999},
                    ],
                },
            ]),
            encoding="utf-8",
        )
        # Corrupt JSON in state_703 must not crash enrichment
        bad_dir = Path(self.tmp_dir) / "json cache" / "bracket data" / "state_703"
        bad_dir.mkdir(parents=True, exist_ok=True)
        (bad_dir / "top10_alliance_rosters.json").write_bytes(b"{corrupt json \xff\xfe")

        self._write_cache_json("world_map_cache_s702.json", {
            "1": _hq_entry(_xy_to_idx(100, 100), uid="u1", name="LiveOne", tag="LIVE", level=30),
            "2": _hq_entry(_xy_to_idx(110, 100), uid="u2", name="LiveTwo", tag="LIVE", level=28),
            "3": _hq_entry(_xy_to_idx(120, 100), uid="u3", name="UnknownPwr", tag="OUT", level=29),
        })

        index = hub._get_world_map_index(self.tmp_dir)
        self.assertEqual(index["roster_matched_count"], 2)
        hqs = index["hqs_by_uid"]
        self.assertEqual(hqs["u1"]["power"], 85_000_000)
        self.assertTrue(hqs["u1"]["known_power"])
        self.assertEqual(hqs["u1"]["tag"], "LIVE")
        self.assertEqual(hqs["u1"]["level"], 30)
        self.assertIsNone(hqs["u3"]["power"])
        self.assertFalse(hqs["u3"]["known_power"])

        # min_power > 0 excludes power=None by default
        res_min = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 1, "min_power": 50_000_000})
        self.assertEqual([t["uid"] for t in res_min["targets"]], ["u1"])

        # include_unknown_power=True retains power=None alongside power >= min_power
        res_inc = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 1, "min_power": 50_000_000, "include_unknown_power": True})
        self.assertEqual({t["uid"] for t in res_inc["targets"]}, {"u1", "u3"})

        # known_power_only=True excludes power=None
        res_known = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 1, "known_power_only": True})
        self.assertEqual({t["uid"] for t in res_known["targets"]}, {"u1", "u2"})

        # sort_by='power' places power=None LAST in both asc and desc
        res_desc = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 1, "sort_by": "power", "sort_dir": "desc"})
        self.assertEqual([t["uid"] for t in res_desc["targets"]], ["u1", "u2", "u3"])
        res_asc = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 1, "sort_by": "power", "sort_dir": "asc"})
        self.assertEqual([t["uid"] for t in res_asc["targets"]], ["u2", "u1", "u3"])

    # ------------------------------------------------------------------
    # 5. Iterative Dense-Core Alliance Clusters
    # ------------------------------------------------------------------
    def test_dense_core_alliance_clusters(self) -> None:
        """Verify dense-core hive detection, empty tag / scattered exclusion, and threshold clamping."""
        now_future = int(time.time()) + 3600
        entries: dict[str, Any] = {}
        # Tight hive HIVE (6 members within radius ~15 around (200, 200); 4 unshielded, 2 shielded)
        for i, (dx, dy) in enumerate(((0, 0), (5, 0), (-5, 0), (0, 6), (8, 8), (-7, 6))):
            idx = _xy_to_idx(200 + dx, 200 + dy)
            entries[str(idx)] = _hq_entry(
                idx, uid=f"hive_{i}", tag="HIVE", level=25 + (i % 3),
                protect_end_time=now_future if i >= 4 else 0,
            )
        # Scattered alliance SCAT (5 members spaced >120 apart -> never forms dense core at radius=45)
        for i in range(5):
            idx = _xy_to_idx(50 + i * 150, 700)
            entries[str(idx)] = _hq_entry(idx, uid=f"scat_{i}", tag="SCAT", level=26)
        # Empty-tag tight cluster -> must be excluded
        for i in range(6):
            idx = _xy_to_idx(800 + i * 2, 800)
            entries[str(idx)] = _hq_entry(idx, uid=f"notag_{i}", tag="", level=25)

        self._write_cache_json("world_map_cache_s702.json", entries)

        res = self.backend.get_map_rip_clusters(cluster_radius=45.0, min_members=5)
        self.assertTrue(res["ok"])
        self.assertEqual(res["count"], 1)
        c = res["clusters"][0]
        self.assertEqual(c["tag"], "HIVE")
        self.assertEqual(c["core_count"], 6)
        self.assertEqual(c["unshielded_count"], 4)
        self.assertIn("med_r", c)
        self.assertIn("p80_r", c)

        # Clamping bounds: radius < 5 -> 5.0, min_members < 2 -> 2
        res_clamped = self.backend.get_map_rip_clusters(cluster_radius=1.0, min_members=1)
        self.assertEqual(res_clamped["cluster_radius"], 5.0)
        self.assertEqual(res_clamped["min_members"], 2)

        # Increasing min_members=7 filters out 6-member hive
        res_strict = self.backend.get_map_rip_clusters(cluster_radius=45.0, min_members=7)
        self.assertEqual(res_strict["count"], 0)

    # ------------------------------------------------------------------
    # 6. query_map_rip_targets Filters, Modes, Overview & 3000 Radar Cap
    # ------------------------------------------------------------------
    def test_query_map_rip_targets_filters_modes_and_radar_cap(self) -> None:
        """Verify modes, RSS aliases, distance, HQ-only RSS skip, get_map_rip_overview, and 3000 radar cap."""
        now_future = int(time.time()) + 3600
        entries: dict[str, Any] = {
            "h1": _hq_entry(_xy_to_idx(510, 500), uid="h1", name="Alpha", tag="WAR", level=28, server_id=702, protect_end_time=0),
            "h2": _hq_entry(_xy_to_idx(600, 600), uid="h2", name="Shielded", tag="DEF", level=30, server_id=703, protect_end_time=now_future),
            "r_wood": _rss_entry(_xy_to_idx(505, 500), resource_id=408, server_id=702, gather_uuid=0, owner_uid=""),
            "r_elec": _rss_entry(_xy_to_idx(520, 500), resource_id=508, server_id=702, gather_uuid=0, owner_uid=""),
            "r_zent": _rss_entry(_xy_to_idx(530, 500), resource_id=208, server_id=702, gather_uuid=0, owner_uid=""),
            "r_diam": _rss_entry(_xy_to_idx(540, 500), resource_id=308, server_id=702, gather_uuid=123, owner_uid=""),
        }
        self._write_cache_json("world_map_cache_s702.json", entries)

        ov = self.backend.get_map_rip_overview()
        self.assertTrue(ov["ok"])
        self.assertTrue(ov["has_world_cache"])
        self.assertEqual(ov["counts"]["deduped_hqs"], 2)
        self.assertEqual(ov["counts"]["unshielded_hqs"], 1)
        self.assertEqual(ov["counts"]["rss_total"], 4)
        self.assertEqual(ov["counts"]["rss_unoccupied"], 3)

        # Modes
        r_unsh = self.backend.query_map_rip_targets({"mode": "unshielded", "min_hq": 25})
        self.assertEqual([t["uid"] for t in r_unsh["targets"]], ["h1"])

        r_hqs = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 25, "shield_state": "shielded", "server_id": 703})
        self.assertEqual([t["uid"] for t in r_hqs["targets"]], ["h2"])

        # RSS alias normalization (lumber -> Wood(2), electricity -> 12, gold -> Diamond(15))
        r_wood = self.backend.query_map_rip_targets({"mode": "rss", "rss_type": "lumber", "rss_min_level": 8, "unoccupied_only": True})
        self.assertEqual(len(r_wood["targets"]), 1)
        self.assertEqual(r_wood["targets"][0]["resource_type"], 2)

        r_elec = self.backend.query_map_rip_targets({"mode": "rss", "rss_type": "electricity", "rss_min_level": 8})
        self.assertEqual(len(r_elec["targets"]), 1)
        self.assertEqual(r_elec["targets"][0]["resource_type"], 12)

        r_diam = self.backend.query_map_rip_targets({"mode": "rss", "rss_type": "gold", "rss_min_level": 8, "unoccupied_only": False})
        self.assertEqual(len(r_diam["targets"]), 1)
        self.assertTrue(r_diam["targets"][0]["occupied"])

        # HQ-only filter ('alliance') skips RSS in mode='all'
        r_al = self.backend.query_map_rip_targets({"mode": "all", "alliance": "WAR", "min_hq": 1})
        self.assertEqual(r_al["counts"]["rss"], 0)
        self.assertEqual([t["uid"] for t in r_al["targets"]], ["h1"])

        # max_distance filter from custom origin
        r_dist = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 1, "origin_x": 500, "origin_y": 500, "max_distance": 20})
        self.assertEqual([t["uid"] for t in r_dist["targets"]], ["h1"])

        # Radar 3000-point truncation cap
        big_entries: dict[str, Any] = {}
        for i in range(3050):
            idx = _xy_to_idx(i % 1000, i // 1000)
            big_entries[str(idx)] = _hq_entry(idx, uid=f"big_{i}", level=25, tag="BIG")
        self._write_cache_json("world_map_cache_s702.json", big_entries)
        with hub._MAP_INDEX_LOCK:
            hub._WORLD_MAP_INDEX_CACHE.clear()
        r_big = self.backend.query_map_rip_targets({"mode": "hqs", "min_hq": 25, "include_radar_points": True, "limit": 100})
        self.assertTrue(r_big["radar_truncated"])
        self.assertEqual(len(r_big["radar_points"]), 3000)

    # ------------------------------------------------------------------
    # 7. Backward-Compatible query_map_targets & CSV Fallback
    # ------------------------------------------------------------------
    def test_query_map_targets_backward_compat_and_csv_fallback(self) -> None:
        """Verify legacy query_map_targets works on world_map_cache and falls back to CSV when cache is empty."""
        now_future = int(time.time()) + 3600
        entries: dict[str, Any] = {
            "1": _hq_entry(_xy_to_idx(100, 100), uid="b1", name="BaseOpen", tag="T1", level=26, protect_end_time=0),
            "2": _hq_entry(_xy_to_idx(101, 100), uid="b2", name="BaseShield", tag="T1", level=27, protect_end_time=now_future),
            "3": _rss_entry(_xy_to_idx(102, 100), resource_id=408, server_id=702),
            "4": {"pointType": 11, "serverId": 702, "mainIndex": _xy_to_idx(105, 105), "aoiVersion": 1},
        }
        for i in range(5):
            idx = _xy_to_idx(200 + i * 2, 200)
            entries[f"c{i}"] = _hq_entry(idx, uid=f"c_{i}", tag="CLU", level=25)
        self._write_cache_json("world_map_cache_s702.json", entries)

        for cat in ("all", "unshielded", "bases", "rss", "clusters", "seasonal"):
            res = self.backend.query_map_targets(search="", category=cat, max_results=50)
            self.assertTrue(res["ok"])
            self.assertEqual(res["source"], "world_map_cache")
            self.assertTrue(res["has_world_cache"])
            self.assertGreater(res["count"], 0, f"Expected results for category={cat}")

        # Remove JSON cache and verify CSV fallback
        (self.cache_dir / "world_map_cache_s702.json").unlink()
        with hub._MAP_INDEX_LOCK:
            hub._WORLD_MAP_INDEX_CACHE.clear()
        (Path(self.tmp_dir) / "map all bases.csv").write_text(
            "name,alliance_tag,alliance_name,level,x,y,has_shield,server_id\n"
            "CsvRaider,CSV,CsvAlliance,28,321,654,false,702\n",
            encoding="utf-8",
        )
        (Path(self.tmp_dir) / "map all seasonal structures.csv").write_text(
            "name,alliance_tag,level,x,y\n"
            "SeasonTower,CSV,5,400,400\n",
            encoding="utf-8",
        )
        res_csv = self.backend.query_map_targets(search="", category="all", max_results=50)
        self.assertTrue(res_csv["ok"])
        self.assertEqual(res_csv["source"], "csv")
        self.assertFalse(res_csv["has_world_cache"])
        self.assertEqual(res_csv["count"], 2)

    # ------------------------------------------------------------------
    # 8. jump_to_coordinate Contracts
    # ------------------------------------------------------------------
    def test_jump_to_coordinate_contracts(self) -> None:
        """Verify jump_to_coordinate handles JUMP_OK, stderr Navigated to, bare exit-0 False, and TimeoutExpired."""
        self.backend.find_script = lambda name: str(PROJECT_ROOT / "tools" / name)
        self.backend._pid_args = lambda: []
        self.backend._subprocess_env = lambda: {}

        # Case 1: stdout JUMP_OK
        self.backend._subproc_run = lambda cmd, timeout=12, env=None: SimpleNamespace(returncode=0, stdout="JUMP_OK (120, 340)\n", stderr="")
        r1 = self.backend.jump_to_coordinate(120, 340, server_id=702)
        self.assertTrue(r1["ok"])

        # Case 2: stderr Navigated to
        self.backend._subproc_run = lambda cmd, timeout=12, env=None: SimpleNamespace(returncode=0, stdout="", stderr="Navigated to (120, 340)\n")
        r2 = self.backend.jump_to_coordinate(120, 340)
        self.assertTrue(r2["ok"])

        # Case 3: bare exit 0 without confirmation marker -> ok=False
        self.backend._subproc_run = lambda cmd, timeout=12, env=None: SimpleNamespace(returncode=0, stdout="something else", stderr="")
        r3 = self.backend.jump_to_coordinate(120, 340)
        self.assertFalse(r3["ok"])

        # Case 4: TimeoutExpired -> ok=False, timed out in error
        def _raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="jump", timeout=12)

        self.backend._subproc_run = _raise_timeout
        r4 = self.backend.jump_to_coordinate(120, 340)
        self.assertFalse(r4["ok"])
        self.assertIn("timed out", r4["error"].lower())

    # ------------------------------------------------------------------
    # 9. Cross-Model Fix 8 Regression: jump_to_coordinate Validation
    # ------------------------------------------------------------------
    def test_fix8_jump_to_coordinate_invalid_inputs_rejected_cleanly(self) -> None:
        """Fix 8: Reject None, NaN, Inf, non-numeric, bool, and out-of-range coords without spawning subprocess."""
        spawn_calls: list[Any] = []
        self.backend.find_script = lambda name: str(PROJECT_ROOT / "tools" / name)
        self.backend._pid_args = lambda: []
        self.backend._subprocess_env = lambda: {}

        def _track_subproc(cmd, timeout=12, env=None):
            spawn_calls.append(cmd)
            return SimpleNamespace(returncode=0, stdout="JUMP_OK (0, 999)\n", stderr="")

        self.backend._subproc_run = _track_subproc

        bad_pairs = [
            (None, 500),
            (500, None),
            (float("nan"), 100),
            (100, float("inf")),
            ("abc", 100),
            (True, 100),
            (-1, 500),
            (500, 1000),
        ]
        for bx, by in bad_pairs:
            res = self.backend.jump_to_coordinate(bx, by)  # type: ignore[arg-type]
            self.assertFalse(res["ok"], f"Expected ok=False for ({bx!r}, {by!r})")
            self.assertIn("invalid map coordinates", res["error"].lower())
        self.assertEqual(len(spawn_calls), 0)

        # Boundary (0, 999) succeeds cleanly
        res_ok = self.backend.jump_to_coordinate(0, 999, server_id=-5)
        self.assertTrue(res_ok["ok"])
        self.assertEqual(len(spawn_calls), 1)

    # ------------------------------------------------------------------
    # 10. World Map Backdrop Assets, Manifest SHA-256 & WebP Dimensions
    # ------------------------------------------------------------------
    def test_world_maps_manifest_assets_hashes_and_dimensions(self) -> None:
        """Verify manifest.json + all 7 WebP files exist, match SHA-256 hashes & 1024x1024 dimensions, and stay lazy."""
        maps_dir = PROJECT_ROOT / "launcher" / "assets" / "world maps"
        manifest_path = maps_dir / "manifest.json"
        self.assertTrue(manifest_path.is_file(), "world_maps/manifest.json missing")

        manifest = hub._load_world_maps_manifest(str(maps_dir))
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(manifest["y_origin"], "top")
        self.assertEqual(len(manifest["maps"]), 6)
        self.assertEqual(len(manifest["major_cities"]), 8)
        self.assertTrue(
            any(c["x"] == 500 and c["y"] == 500 and c["level"] == 7 for c in manifest["major_cities"]),
            "Capitol (500, 500) Lv.7 missing from major_cities",
        )

        # Verify all 6 seasonal maps + zones_overlay.webp
        asset_entries = list(manifest["maps"]) + [manifest["zones_overlay"]]
        self.assertEqual(len(asset_entries), 7)
        for entry in asset_entries:
            fpath = maps_dir / entry["file"]
            self.assertTrue(fpath.is_file(), f"Missing world map asset: {entry['file']}")
            raw = fpath.read_bytes()
            self.assertEqual(len(raw), entry["size_bytes"], f"Size mismatch for {entry['file']}")
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(digest, entry["sha256"], f"SHA-256 mismatch for {entry['file']}")
            w, h = _webp_dimensions(raw)
            self.assertEqual((w, h), (1024, 1024), f"Unexpected dimensions for {entry['file']}: {(w, h)}")
            self.assertEqual((entry["width"], entry["height"]), (1024, 1024))

        # Ensure startup HTML never inlines any of the 7 world_maps WebP payloads
        startup_html = hub._load_html_with_assets(include_heavy_packs=False)
        for entry in asset_entries:
            b64_head = base64.b64encode((maps_dir / entry["file"]).read_bytes()[:48]).decode("ascii")
            self.assertFalse(
                b64_head in startup_html,
                f"Startup HTML unexpectedly inlined world_maps asset {entry['file']}",
            )

    # ------------------------------------------------------------------
    # 11. WorldSeasonType Enum Mapping & Grid Sizes (1000 vs 1600)
    # ------------------------------------------------------------------
    def test_world_season_enum_mapping_and_grid_sizes(self) -> None:
        """Verify WorldSeasonType enum 0..5 -> pre_season_1..season_6 and 1000 vs 1600 grid sizes."""
        expected_enum = {
            0: "pre_season_1",
            1: "season_2",
            2: "season_3",
            3: "season_4",
            4: "season_5",
            5: "season_6",
        }
        self.assertEqual(hub._WORLD_SEASON_ENUM_MAP, expected_enum)

        manifest = hub._load_world_maps_manifest()
        self.assertEqual(hub._world_season_enum_from_manifest(manifest), expected_enum)

        by_key = hub._world_maps_by_key(manifest)
        for ws_id, key in expected_enum.items():
            self.assertIn(key, by_key)
            entry = by_key[key]
            self.assertIn(ws_id, entry["world_season_ids"])
            if key == "season_6":
                self.assertEqual(entry["grid_size"], 1600)
                self.assertFalse(entry["supports_zones"])
            else:
                self.assertEqual(entry["grid_size"], 1000)
                self.assertTrue(entry["supports_zones"])

    # ------------------------------------------------------------------
    # 12. Offline World Season PointType & Coordinate Inference
    # ------------------------------------------------------------------
    def test_offline_world_season_inference_and_s6_coord_bounds(self) -> None:
        """Verify PointType 26/29 -> S3, 38 -> S4, 35/36 -> S5, coord >= 1000 / pointIndex >= 1M -> S6, plus S6 jump/origin bounds."""
        # Empty cache -> None inference, default pre_season_1
        self.assertIsNone(hub._infer_world_season_from_map_cache(self.tmp_dir))
        det_default = self.backend._detect_world_season()
        self.assertEqual(det_default["season_key"], "pre_season_1")
        self.assertEqual(det_default["world_season_id"], 0)
        self.assertEqual(det_default["source"], "default")
        self.assertFalse(det_default["is_live"])

        cases = [
            (
                "pt29_s3",
                {"p1": {"pointType": 29, "serverId": 702, "pointIndex": _xy_to_idx(400, 400)}},
                "season_3",
                2,
                1000,
            ),
            (
                "pt26_s3",
                {"p1": {"pointType": 26, "serverId": 702, "pointIndex": _xy_to_idx(410, 410)}},
                "season_3",
                2,
                1000,
            ),
            (
                "pt38_s4",
                {"p1": {"pointType": 38, "serverId": 702, "pointIndex": _xy_to_idx(420, 420)}},
                "season_4",
                3,
                1000,
            ),
            (
                "pt35_s5",
                {"p1": {"pointType": 35, "serverId": 702, "pointIndex": _xy_to_idx(430, 430)}},
                "season_5",
                4,
                1000,
            ),
            (
                "pt36_s5",
                {"p1": {"pointType": 36, "serverId": 702, "pointIndex": _xy_to_idx(440, 440)}},
                "season_5",
                4,
                1000,
            ),
            (
                "coord_1000_s6",
                {"p1": {"pointType": 6, "serverId": 702, "x": 1250, "y": 800, "pointIndex": _xy_to_idx(500, 500)}},
                "season_6",
                5,
                1600,
            ),
            (
                "pidx_1m_s6",
                {"p1": {"pointType": 4, "serverId": 702, "pointIndex": 1_200_500}},
                "season_6",
                5,
                1600,
            ),
        ]
        for label, payload, exp_key, exp_ws_id, exp_grid in cases:
            with self.subTest(case=label):
                self._write_cache_json("world_map_cache.json", payload)
                with hub._MAP_INDEX_LOCK:
                    hub._WORLD_MAP_INDEX_CACHE.clear()
                inf = hub._infer_world_season_from_map_cache(self.tmp_dir)
                self.assertIsNotNone(inf)
                self.assertEqual(inf["season_key"], exp_key)
                self.assertEqual(inf["world_season_id"], exp_ws_id)

                det = self.backend._detect_world_season()
                self.assertEqual(det["season_key"], exp_key)
                self.assertEqual(det["world_season_id"], exp_ws_id)
                self.assertEqual(det["grid_size"], exp_grid)
                self.assertEqual(det["source"], "world_map_cache")
                self.assertFalse(det["is_live"])

        # On active Season 6 cache (from last subTest), verify 0..1599 bounds in origin, query, and jump_to_coordinate
        self.backend.find_script = lambda name: str(PROJECT_ROOT / "tools" / name)
        self.backend._pid_args = lambda: []
        self.backend._subprocess_env = lambda: {}
        self.backend._subproc_run = lambda cmd, timeout=12, env=None: SimpleNamespace(
            returncode=0, stdout="JUMP_OK (1250, 1450)\n", stderr=""
        )
        res_s6_ok = self.backend.jump_to_coordinate(1250, 1450)
        self.assertTrue(res_s6_ok["ok"])
        res_s6_bad = self.backend.jump_to_coordinate(1600, 500)
        self.assertFalse(res_s6_bad["ok"])
        self.assertIn("0..1599", res_s6_bad["error"])

        idx_s6 = hub._get_world_map_index(self.tmp_dir)
        origin_s6 = self.backend._resolve_map_origin(idx_s6, origin_x=1300, origin_y=1500)
        self.assertEqual((origin_s6["x"], origin_s6["y"]), (1300, 1500))
        origin_s6_center = self.backend._resolve_map_origin(idx_s6)
        self.assertEqual((origin_s6_center["x"], origin_s6_center["y"]), (800, 800))

        q_s6 = self.backend.query_map_rip_targets({"mode": "hqs", "origin_x": 1200, "origin_y": 1400})
        self.assertTrue(q_s6["ok"])
        self.assertEqual((q_s6["origin"]["x"], q_s6["origin"]["y"]), (1200, 1400))

    # ------------------------------------------------------------------
    # 13. Live SeasonDataManager Mock, 60s TTL & Per-Account Isolation
    # ------------------------------------------------------------------
    def test_live_season_query_cache_persistence_and_account_isolation(self) -> None:
        """Verify live DataCenter.SeasonDataManager mock query, 60s TTL, atomic persistence, and account isolation."""
        orig_cd = hub.client_discovery
        lua_calls: list[int] = []
        live_responses: dict[int, dict[str, Any]] = {
            1001: {
                "world_season": 2,
                "season": 3,
                "config_season": 3,
                "is_using_season_asset": True,
                "season_show_name": "Everfrost Era",
                "server_id": 702,
            },
            2002: {
                "world_season": 5,
                "season": 6,
                "config_season": 6,
                "is_using_season_asset": True,
                "season_show_name": "Archipelago",
                "server_id": 905,
            },
        }
        running_procs: list[dict[str, Any]] = [
            {"pid": 1001, "label": "MainAcc", "role": "main", "serverId": 702},
            {"pid": 2002, "label": "FarmAcc", "role": "farm", "serverId": 905},
        ]

        class _FakeClientDiscovery:
            @staticmethod
            def _xlua_loaded(pid: int) -> bool:
                return pid in live_responses

            @staticmethod
            def frida_eval_lua(pid: int, script: str, timeout: float = 5.0) -> tuple[bool, str]:
                lua_calls.append(pid)
                self.assertIn("SeasonDataManager", script)
                self.assertIn("GetWorldSeason", script)
                self.assertIn("AccountManager", script)
                return True, json.dumps(live_responses[pid])

        try:
            hub.client_discovery = _FakeClientDiscovery()
            self.backend._discover_running_clients = lambda *a, **kw: list(running_procs)

            # Live query Account A (PID 1001 -> S3)
            res_a = self.backend._detect_world_season(pid=1001)
            self.assertEqual(res_a["season_key"], "season_3")
            self.assertEqual(res_a["world_season_id"], 2)
            self.assertEqual(res_a["source"], "live")
            self.assertTrue(res_a["is_live"])
            self.assertEqual(res_a["season_show_name"], "Everfrost Era")
            self.assertEqual(lua_calls, [1001])

            # Verify atomic persistence for MainAcc and world_season_last.json
            json_cache_dir = Path(self.tmp_dir) / "json cache"
            main_cache = json.loads((json_cache_dir / "mainacc_world_season.json").read_text(encoding="utf-8"))
            self.assertEqual(main_cache["world_season_id"], 2)
            self.assertEqual(main_cache["season_key"], "season_3")
            self.assertEqual(main_cache["server_id"], 702)
            self.assertEqual(main_cache["account_label"], "MainAcc")
            self.assertIn("timestamp", main_cache)

            # 60s TTL cache avoids duplicate Lua eval when force_live=False
            res_a_ttl = self.backend._detect_world_season(pid=1001, force_live=False)
            self.assertEqual(res_a_ttl["season_key"], "season_3")
            self.assertEqual(res_a_ttl["source"], "live")
            self.assertTrue(res_a_ttl["is_live"])
            self.assertEqual(lua_calls, [1001])

            # force_live=True bypasses 60s TTL
            res_a_force = self.backend._detect_world_season(pid=1001, force_live=True)
            self.assertEqual(res_a_force["season_key"], "season_3")
            self.assertEqual(lua_calls, [1001, 1001])

            # Live query Account B (PID 2002 -> S6, 1600x1600)
            res_b = self.backend._detect_world_season(pid=2002)
            self.assertEqual(res_b["season_key"], "season_6")
            self.assertEqual(res_b["world_season_id"], 5)
            self.assertEqual(res_b["grid_size"], 1600)
            self.assertFalse(res_b["supports_zones"])
            self.assertEqual(res_b["source"], "live")
            self.assertTrue(res_b["is_live"])
            self.assertTrue((json_cache_dir / "farmacc_world_season.json").is_file())
            last_cache = json.loads((json_cache_dir / "world_season_last.json").read_text(encoding="utf-8"))
            self.assertEqual(last_cache["server_id"], 905)
            self.assertEqual(last_cache["season_key"], "season_6")

            # Simulate clients closed (offline): verify strict per-account cache isolation
            running_procs.clear()
            self.backend.selected_client_label = "MainAcc"
            off_a = self.backend._detect_world_season()
            self.assertEqual(off_a["season_key"], "season_3")
            self.assertEqual(off_a["source"], "account_cache")
            self.assertFalse(off_a["is_live"])

            self.backend.selected_client_label = "FarmAcc"
            off_b = self.backend._detect_world_season()
            self.assertEqual(off_b["season_key"], "season_6")
            self.assertEqual(off_b["grid_size"], 1600)
            self.assertEqual(off_b["source"], "account_cache")
            self.assertFalse(off_b["is_live"])

            # Unseen account Alt3Acc must NOT inherit FarmAcc's world_season_last.json
            self.backend.selected_client_label = "Alt3Acc"
            off_c = self.backend._detect_world_season()
            self.assertEqual(off_c["season_key"], "pre_season_1")
            self.assertEqual(off_c["source"], "default")

            # No selected account + matching server cache -> uses world_season_last.json
            self.backend.selected_client_label = None
            self._write_cache_json("world_map_cache_s905.json", {
                "1": _hq_entry(_xy_to_idx(200, 200), uid="u905", server_id=905),
            })
            with hub._MAP_INDEX_LOCK:
                hub._WORLD_MAP_INDEX_CACHE.clear()
            off_match = self.backend._detect_world_season()
            self.assertEqual(off_match["season_key"], "season_6")
            self.assertEqual(off_match["source"], "account_cache")

            # No selected account + mismatched server cache (777 with Pt 38) -> rejects last cache, uses Tier 3
            (self.cache_dir / "world_map_cache_s905.json").unlink()
            self._write_cache_json("world_map_cache_s777.json", {
                "1": _hq_entry(_xy_to_idx(200, 200), uid="u777", server_id=777),
                "2": {"pointType": 38, "serverId": 777, "pointIndex": _xy_to_idx(250, 250)},
            })
            with hub._MAP_INDEX_LOCK:
                hub._WORLD_MAP_INDEX_CACHE.clear()
            off_mismatch = self.backend._detect_world_season()
            self.assertEqual(off_mismatch["season_key"], "season_4")
            self.assertEqual(off_mismatch["source"], "world_map_cache")
        finally:
            hub.client_discovery = orig_cd

    # ------------------------------------------------------------------
    # 14. get_world_map_backdrop("auto" & Explicit Keys) + Overview Metadata
    # ------------------------------------------------------------------
    def test_get_world_map_backdrop_and_overview_world_season(self) -> None:
        """Verify get_world_map_backdrop for auto/explicit keys and world_season inclusion in get_map_rip_overview."""
        self._write_cache_json("world_map_cache_s702.json", {
            "h1": _hq_entry(_xy_to_idx(510, 500), uid="h1", name="Alpha", tag="WAR", level=28, server_id=702),
            "ice1": {"pointType": 29, "serverId": 702, "pointIndex": _xy_to_idx(450, 450)},
        })

        # Overview includes world_season metadata
        ov = self.backend.get_map_rip_overview()
        self.assertTrue(ov["ok"])
        self.assertIn("world_season", ov)
        ws = ov["world_season"]
        self.assertEqual(ws["season_key"], "season_3")
        self.assertEqual(ws["world_season_id"], 2)
        self.assertEqual(ws["grid_size"], 1000)
        self.assertEqual(ws["y_origin"], "top")
        self.assertTrue(ws["supports_zones"])
        self.assertEqual(ws["source"], "world_map_cache")
        self.assertFalse(ws["is_live"])
        self.assertEqual(len(ws["available_maps"]), 6)

        # Auto, empty, and unrecognized keys fall back to detected season_3
        for req_k in ("auto", "", "nonexistent_map"):
            res_auto = self.backend.get_world_map_backdrop(req_k)
            self.assertTrue(res_auto["ok"])
            self.assertEqual(res_auto["season_key"], "season_3")
            self.assertEqual(res_auto["world_season_id"], 2)
            self.assertEqual(res_auto["source"], "world_map_cache")
            self.assertTrue(res_auto["image_data_uri"].startswith("data:image/webp;base64,"))
            self.assertTrue(res_auto["zones_data_uri"].startswith("data:image/webp;base64,"))
            self.assertEqual(res_auto["grid_size"], 1000)
            self.assertEqual(res_auto["y_origin"], "top")
            self.assertEqual((res_auto["width"], res_auto["height"]), (1024, 1024))
            self.assertTrue(
                any(c["x"] == 500 and c["y"] == 500 and c["level"] == 7 for c in res_auto["major_cities"])
            )

        # Explicit keys pre_season_1 .. season_6
        expected_keys = ("pre_season_1", "season_2", "season_3", "season_4", "season_5", "season_6")
        for idx_id, key in enumerate(expected_keys):
            res = self.backend.get_world_map_backdrop(key, include_zones=True)
            self.assertTrue(res["ok"], f"Backdrop failed for {key}")
            self.assertEqual(res["requested_key"], key)
            self.assertEqual(res["season_key"], key)
            self.assertEqual(res["world_season_id"], idx_id)
            self.assertEqual(res["source"], "manual")
            self.assertEqual(res["y_origin"], "top")
            self.assertEqual((res["width"], res["height"]), (1024, 1024))
            self.assertTrue(res["image_data_uri"].startswith("data:image/webp;base64,"))
            raw_img = base64.b64decode(res["image_data_uri"].split(",", 1)[1])
            self.assertEqual(_webp_dimensions(raw_img), (1024, 1024))
            self.assertEqual(len(res["available_maps"]), 6)

            if key == "season_6":
                self.assertEqual(res["grid_size"], 1600)
                self.assertFalse(res["supports_zones"])
                self.assertEqual(res["zones_data_uri"], "")
                self.assertEqual(res["major_cities"], [])
            else:
                self.assertEqual(res["grid_size"], 1000)
                self.assertTrue(res["supports_zones"])
                self.assertTrue(res["zones_data_uri"].startswith("data:image/webp;base64,"))
                raw_zones = base64.b64decode(res["zones_data_uri"].split(",", 1)[1])
                self.assertEqual(_webp_dimensions(raw_zones), (1024, 1024))
                self.assertTrue(
                    any(c["x"] == 500 and c["y"] == 500 and c["level"] == 7 for c in res["major_cities"])
                )

                # include_zones=False omits zones_data_uri
                res_no_z = self.backend.get_world_map_backdrop(key, include_zones=False)
                self.assertEqual(res_no_z["zones_data_uri"], "")

        # Verify module-level WebP cache populated all 7 files
        with hub._WORLD_MAPS_LOCK:
            self.assertIsNotNone(hub._WORLD_MAPS_CACHE["manifest"])
            self.assertEqual(len(hub._WORLD_MAPS_CACHE["webp"]), 7)

    # ------------------------------------------------------------------
    # 15. On-Map Quick Player Search & Snap Lookup
    # ------------------------------------------------------------------
    def test_search_map_players_ranking_unfiltered_and_coords(self) -> None:
        """Verify search_map_players finds shielded/low-HQ players, ranks exact/prefix/substring, and supports coords."""
        now_ts = int(time.time())
        self._write_cache_json("world_map_cache_s702.json", {
            "p1": _hq_entry(_xy_to_idx(214, 554), uid="u1", name="Hay King", tag="WARG", level=35, server_id=702, protect_end_time=0),
            "p2": _hq_entry(_xy_to_idx(300, 400), uid="u2", name="Haymaker", tag="ROA", level=29, server_id=702, protect_end_time=now_ts + 7200),
            "p3": _hq_entry(_xy_to_idx(410, 510), uid="u3", name="TinyHay", tag="FARM", level=14, server_id=702, protect_end_time=now_ts + 3600),
            "p4": _hq_entry(_xy_to_idx(505, 505), uid="u4", name="Heinzy", tag="WARG", level=32, server_id=702, protect_end_time=now_ts + 5000),
        })

        # Empty query returns empty cleanly
        empty = self.backend.search_map_players("")
        self.assertTrue(empty["ok"])
        self.assertEqual(empty["count"], 0)
        self.assertEqual(empty["results"], [])

        # Prefix + substring ranking includes shielded & low-HQ targets (unfiltered)
        res = self.backend.search_map_players("hay", limit=10)
        self.assertTrue(res["ok"])
        self.assertEqual([r["name"] for r in res["results"]], ["Hay King", "Haymaker", "TinyHay"])
        self.assertFalse(res["results"][0]["has_shield"])
        self.assertTrue(res["results"][1]["has_shield"])
        self.assertGreater(res["results"][1]["shield_left_sec"], 0)
        self.assertEqual(res["results"][2]["level"], 14)

        # Exact match beats prefix match even if lower level
        exact = self.backend.search_map_players("heinzy")
        self.assertEqual(exact["results"][0]["name"], "Heinzy")
        self.assertEqual((exact["results"][0]["x"], exact["results"][0]["y"]), (505, 505))
        self.assertEqual(exact["results"][0]["match_rank"], 0)

        # Bracketed [TAG] Name query works
        tagged = self.backend.search_map_players("[WARG] Hay")
        self.assertGreaterEqual(tagged["count"], 1)
        self.assertEqual(tagged["results"][0]["name"], "Hay King")

        # Direct coordinate query: exact HQ tile returns that HQ
        coord_hit = self.backend.search_map_players("214, 554")
        self.assertEqual(coord_hit["results"][0]["kind"], "hq")
        self.assertEqual(coord_hit["results"][0]["name"], "Hay King")

        # Direct coordinate query on empty tile returns synthetic coordinate snap target
        coord_open = self.backend.search_map_players("777 888")
        self.assertEqual(coord_open["results"][0]["kind"], "coord")
        self.assertEqual((coord_open["results"][0]["x"], coord_open["results"][0]["y"]), (777, 888))

    # ------------------------------------------------------------------
    # 16. Shield-Drop Watchlist & Countdown Pins
    # ------------------------------------------------------------------
    def test_shield_watchlist_pin_sort_alliance_and_clear(self) -> None:
        """Verify Shield-Drop Watchlist pins players/alliances, sorts soonest expiry first, and classifies statuses."""
        now_ts = int(time.time())
        self._write_cache_json("world_map_cache_s702.json", {
            "p_crit": _hq_entry(_xy_to_idx(210, 550), uid="u_crit", name="CritTarget", tag="ENMY", level=34, server_id=702, protect_end_time=now_ts + 240),
            "p_soon": _hq_entry(_xy_to_idx(220, 555), uid="u_soon", name="SoonTarget", tag="ENMY", level=31, server_id=702, protect_end_time=now_ts + 1200),
            "p_long": _hq_entry(_xy_to_idx(230, 560), uid="u_long", name="LongShield", tag="SAFE", level=35, server_id=702, protect_end_time=now_ts + 14400),
            "p_drop": _hq_entry(_xy_to_idx(240, 565), uid="u_drop", name="DroppedHQ", tag="ENMY", level=30, server_id=702, protect_end_time=now_ts - 60),
        })

        # Empty initially
        empty = self.backend.get_shield_watchlist()
        self.assertTrue(empty["ok"])
        self.assertEqual(empty["counts"]["total"], 0)

        # Pin individual long-shield player + pin entire ENMY alliance
        r1 = self.backend.toggle_watchlist_player("u_long", {"name": "LongShield", "tag": "SAFE", "x": 230, "y": 560, "level": 35})
        self.assertEqual(r1["action"], "pinned")
        self.assertEqual(r1["counts"]["shielded"], 1)

        r2 = self.backend.toggle_watchlist_alliance("ENMY")
        self.assertEqual(r2["action"], "pinned")
        self.assertEqual(r2["counts"], {"total": 4, "critical": 1, "soon": 1, "shielded": 1, "dropped": 1})
        # Exact sort order: critical (240s) -> soon (1200s) -> shielded (14400s) -> dropped
        self.assertEqual([i["uid"] for i in r2["items"]], ["u_crit", "u_soon", "u_long", "u_drop"])
        self.assertEqual([i["status"] for i in r2["items"]], ["critical", "soon", "shielded", "dropped"])

        # Unpin player toggles off cleanly
        r3 = self.backend.toggle_watchlist_player("u_long")
        self.assertEqual(r3["action"], "unpinned")
        self.assertEqual(r3["counts"]["total"], 3)

        # Clear empties all
        r4 = self.backend.clear_shield_watchlist()
        self.assertEqual(r4["action"], "cleared")
        self.assertEqual(r4["counts"]["total"], 0)

    def test_ui_locales_and_translator_loader(self) -> None:
        """Verify HubBackend loads all 18 official Last Z UI locales and live translator module cleanly."""
        loc = self.backend.get_ui_locales()
        self.assertTrue(loc["ok"])
        self.assertEqual(len(loc["languages"]), 18)
        self.assertIn("ar", loc["translations"])
        self.assertIn("es", loc["translations"])

        tr_mod = self.backend._load_translator_mod()
        self.assertIsNotNone(tr_mod)
        self.assertTrue(callable(getattr(tr_mod, "ensure_server_running", None)))
        self.assertTrue(callable(getattr(tr_mod, "translate_text", None)))


class TestMapRipUiContracts(unittest.TestCase):
    """Tier 2: #view-map DOM IDs, JS wiring, XSS escaping, and terminology contracts."""

    def test_view_map_dom_ids_and_js_contracts(self) -> None:
        """Verify #view-map preserves all 8 legacy IDs, has zero duplicate HTML IDs, and wires _mapQuerySeq + esc()."""
        html = (PROJECT_ROOT / "launcher" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-view="map"', html)
        self.assertIn('id="view-map"', html)

        all_ids = re.findall(r'\bid\s*=\s*"([^"]+)"', html)
        self.assertEqual(len(all_ids), len(set(all_ids)), "Duplicate HTML IDs found in index.html")

        legacy_ids = [
            "view-map", "sel-res-type", "sel-res-lvl", "finder-status",
            "map-search-input", "map-category-select", "map-table-body", "map-table-status",
        ]
        new_ids = [
            "map-cache-badge", "map-kpi-grid", "map-mode-pills",
            "map-radar-canvas", "map-radar-tooltip", "map-inspector-card", "map-table-head",
            "map-quick-find", "map-quick-find-input", "map-quick-find-results", "map-quick-find-go",
            "map-watchlist-card", "map-layer-watchlist", "map-wl-verify-btn", "map-wl-clear-btn",
            "hdr-lang-select", "card-live-translator", "tr-status-pill", "tr-target-lang", "tr-test-input",
        ]
        for req_id in legacy_ids + new_ids:
            self.assertIn(req_id, all_ids, f"Missing required #view-map ID: {req_id}")

        # JS wiring & race/XSS guards
        for sym in (
            "_mapQuerySeq", "query_map_rip_targets", "get_map_rip_overview", "search_map_players",
            "snapToQuickFindItem", "jump_to_coordinate", "esc(",
            "get_shield_watchlist", "toggle_watchlist_player", "toggle_watchlist_alliance",
            "get_ui_locales", "set_ui_language", "get_translator_status", "save_translator_config", "test_live_translator",
            "color-scheme: dark;", "select option, select optgroup",
        ):
            self.assertIn(sym, html)

        # Forbidden terminology check in #view-map pane
        bad_badge_re = re.compile(r"courage\s+" + r"badge", re.I)
        bad_rank_re = re.compile(r"\bcomm" + r"ander\b", re.I)
        m_map = re.search(r'<section[^>]*id="view-map".*?</section>', html, flags=re.S)
        self.assertIsNotNone(m_map)
        self.assertNotRegex(m_map.group(0), bad_badge_re)
        self.assertNotRegex(m_map.group(0), bad_rank_re)

    def test_fix7_refresh_map_table_seq_guard_and_fix8_snap_try_catch(self) -> None:
        """Fix 7 & Fix 8 UI contracts: refreshMapTable guards _mapQuerySeq and snapToCoords validates 0..999 with try/catch."""
        html = (PROJECT_ROOT / "launcher" / "web" / "index.html").read_text(encoding="utf-8")

        m_finder = re.search(r"async function refreshMapFinder\b.*?\n\}", html, flags=re.S)
        self.assertIsNotNone(m_finder)
        self.assertRegex(m_finder.group(0), re.compile(r"if\s*\(\s*seq\s*!==\s*_mapQuerySeq\s*\)\s*return;\s*await\s+refreshMapTable\(seq\);"))

        m_tbl = re.search(r"async function refreshMapTable\b.*?\n\}", html, flags=re.S)
        self.assertIsNotNone(m_tbl)
        tbl_src = m_tbl.group(0)
        self.assertIn("expectedSeq = null", tbl_src)
        self.assertGreaterEqual(tbl_src.count("seq !== _mapQuerySeq"), 3)

        m_snap = re.search(r"async function snapToCoords\b.*?\n\}", html, flags=re.S)
        self.assertIsNotNone(m_snap)
        snap_src = m_snap.group(0)
        self.assertIn("Number.isFinite", snap_src)
        self.assertIn("999", snap_src)
        self.assertIn("try {", snap_src)
        self.assertIn("catch (err)", snap_src)
        self.assertNotIn("Number(snapBtn.dataset.x || 0)", html)


if __name__ == "__main__":
    unittest.main()
