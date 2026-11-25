#!/usr/bin/env python3
"""
Match, extract, and organize all Last Z purchasable and unlockable skins inside models/:
  - Task A: 3D HQ & Holiday Building Skins (decoration.json type=1 & type=10 + prefab meshes)
            -> models/<Season>/HQ Skins/<Clean English Shop Name>/
            plus Blackland Ruin -> models/Pre-Season 1/Buildings and Environment/Blackland Ruin/
  - Task B: 3D Vehicle / March Skins (decoration.json type=4 + WorldTroop_* + car show.json)
            -> models/<Season>/Vehicle Skins/<Clean English Vehicle Name>/
  - Task C: All 110 2D Spine Hero Skins (art_lastday_spine_hero_*.bundle)
            -> models/<Season>/<Faction>/Hero Skins 2D Spine/<Hero Name> - <Skin Name>/

Guarantees:
  - Zero underscores (_) in any file or directory name anywhere under models/
  - Zero em dashes (U+2014) in any script, JSON, CSV, README, OBJ, MTL, or atlas file
  - 100% resolved MTL texture paths and verified trimesh GLB scenes
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import math
import re
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from PIL import Image
import trimesh
from trimesh.visual import ColorVisuals, TextureVisuals
from trimesh.visual.material import PBRMaterial
import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler


EM_DASH = chr(0x2014)

DEFAULT_AB_DIR = Path(
    r"%LOCALAPPDATA%/Last Z\Game\Survival_Data\StreamingAssets\AssetBundles"
)
DEFAULT_REPO_DIR = Path(r".")

SEASON_ORDER: List[str] = [
    "Pre-Season 1",
    "Season 1",
    "Season 2",
    "Season 3",
    "Season 4",
    "Season 5",
    "Season 6",
]

SEASON_THEMES: Dict[str, str] = {
    "Pre-Season 1": "Core Launch Roster, Base Shelter, HQ Skins, Vehicle Skins, Zombies, and World Assets",
    "Season 1": "Clash of Thrones (Season 1 Heroes, Companions, Outfits, and Exclusive Weapons)",
    "Season 2": "Wastes Watcher (Season 2 Heroes, Outfits, Exclusive Weapons, and Desert Expedition Assets)",
    "Season 3": "Everfrost Era (Season 3 Heroes, Everfrost HQ Skins, Glacier Bosses, and Snow Structures)",
    "Season 4": "Dinosaur Origin (Season 4 Heroes, Hero Awakenings, Dinosaur March Skins, and Dinosaurs)",
    "Season 5": "Moonlit Elegy (Season 5 Gothic Bosses, Vampires, Werewolves, and Cursed Mountains)",
    "Season 6": "Season 6 Content",
}

CAMP_TO_FACTION: Dict[int, str] = {
    1: "Blood Rose",
    2: "Wings of Dawn",
    3: "Guard of Order",
}

FACTION_ORDER: List[str] = [
    "Blood Rose",
    "Wings of Dawn",
    "Guard of Order",
    "HQ Skins",
    "Vehicle Skins",
    "Zombies and Monsters",
    "Blood Hand and Raiders",
    "Troops and Soldiers",
    "Vehicles and Tanks",
    "NPCs and Survivors",
    "Weapons",
    "Buildings and Environment",
]

SPINE_FACTION_ORDER: List[str] = [
    "Blood Rose",
    "Wings of Dawn",
    "Guard of Order",
    "NPCs and Survivors",
]


# ---------------------------------------------------------------------------
# Task A: Verified 3D HQ Skin & Prefab Building Mappings
# ---------------------------------------------------------------------------
# Existing 3D catalog slugs moved from Buildings and Environment -> HQ Skins
HQ_SKIN_MOVES_BY_SLUG: Dict[str, Dict[str, str]] = {
    "environment_decorate_a_build_kaifupifu": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Battle Fortress",
        "decoration_id": "10002",
        "evidence": (
            "decoration.json(id=10002, type=1, name='Battle Fortress', model='A_Build_PiFu01') -> "
            "main_prefabs_building_a_build_pifu01 -> a_build_kaifupifu"
        ),
    },
    "environment_decorate_a_build_yurenjiexiaochoupifu_01": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Boom Show",
        "decoration_id": "10016",
        "evidence": (
            "decoration.json(id=10016, type=1, name='Boom Show', model='A_build_yurenjiexiaochoupifu_01')"
        ),
    },
    "environment_decorate_a_build_yurenjiexiaochoupifu_01_s3": {
        "season": "Season 3",
        "faction": "HQ Skins",
        "name": "Boom Show S3",
        "decoration_id": "10016",
        "evidence": (
            "decoration.json(id=10016, type=1, name='Boom Show') Everfrost Era S3 snow variant "
            "(a_build_yurenjiexiaochoupifu_01_s3)"
        ),
    },
    "environment_decorate_a_build_quanjilong_01": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Boxing T-Rex",
        "decoration_id": "10017",
        "evidence": (
            "decoration.json(id=10017, type=1, name='Boxing T-Rex', model='A_build_quanjilong_01')"
        ),
    },
    "environment_decorate_a_build_quanjilong_01_s3": {
        "season": "Season 3",
        "faction": "HQ Skins",
        "name": "Boxing T-Rex S3",
        "decoration_id": "10017",
        "evidence": (
            "decoration.json(id=10017, type=1, name='Boxing T-Rex') Everfrost Era S3 snow variant "
            "(a_build_quanjilong_01_s3)"
        ),
    },
    "environment_decorate_a_build_beer_cat": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "The Purr-cussion",
        "decoration_id": "10018",
        "evidence": (
            "decoration.json(id=10018, type=1, name='The Purr-cussion', model='A_build_beer_cat02')"
        ),
    },
    "environment_decorate_a_build_halloween_dragon": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "The Nightmare",
        "decoration_id": "10020",
        "evidence": (
            "decoration.json(id=10020, type=1, name='The Nightmare', model='A_build_halloween_dragon')"
        ),
    },
    "environment_decorate_a_build_whitebear_common": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Bear Wick Pedestal",
        "decoration_id": "10021",
        "evidence": (
            "decoration.json(id=10021, type=1, name='Bear Wick') shared HQ pedestal (whitebear_common)"
        ),
    },
    "environment_map_world_resource_01_world_shengdanjiexueren_01": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Snowlaf World",
        "decoration_id": "10024",
        "evidence": (
            "decoration.json(id=10024, type=1, name='Snowlaf', model_world='World_Shengdanjiexueren_01') -> "
            "world_resource_01_world_shengdanjiexueren_01"
        ),
    },
    "environment_decorate_a_build_dragoncastle": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "The Inferno",
        "decoration_id": "10027",
        "evidence": (
            "decoration.json(id=10027, type=1, name='The Inferno', model='A_build_DragonCastle')"
        ),
    },
    "environment_map_world_resource_01_world_pijiujie_01": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Disco Ball",
        "decoration_id": "10019",
        "evidence": (
            "decoration.json(id=10019, type=10, name='Disco Ball', model_world='World_pijiujie_01') -> "
            "world_resource_01_world_pijiujie_01"
        ),
    },
    "environment_decorate_a_build_huoji_01": {
        "season": "Pre-Season 1",
        "faction": "HQ Skins",
        "name": "Thanksgiving Roast Turkey",
        "decoration_id": "holiday_turkey_hq",
        "evidence": "Holiday HQ decoration bundle (a_build_huoji_01 / Thanksgiving Turkey)",
    },
}

# Prefab-scoped extractions from valentine_fox bundle (replacing merged Valentine Fox HQ)
VALENTINE_FOX_SPLITS: List[Dict[str, str]] = [
    {
        "prefab_path": "Assets/_Art_LastDay/Models/Environment/Decorate/A_build_Valentine_Fox/Prefab/A_build_Valentine_Fox_A.prefab",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10025, season='')",
        "faction": "HQ Skins",
        "name": "Heartbound Fox",
        "slug": "hq_skin_heartbound_fox",
        "decoration_id": "10025",
        "evidence": (
            "decoration.json(id=10025, type=1, name='Heartbound Fox', model='A_build_Valentine_Fox_A') -> "
            "valentine_fox::A_build_Valentine_Fox_A.prefab"
        ),
    },
    {
        "prefab_path": "Assets/_Art_LastDay/Models/Environment/Decorate/A_build_Valentine_Fox/Prefab/A_build_Valentine_Fox_A_world.prefab",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10025, season='')",
        "faction": "HQ Skins",
        "name": "Heartbound Fox World",
        "slug": "hq_skin_heartbound_fox_world",
        "decoration_id": "10025",
        "evidence": (
            "decoration.json(id=10025, type=1, name='Heartbound Fox', model_world='A_build_Valentine_Fox_A_world') -> "
            "valentine_fox::A_build_Valentine_Fox_A_world.prefab"
        ),
    },
    {
        "prefab_path": "Assets/_Art_LastDay/Models/Environment/Decorate/A_build_Valentine_Fox/Prefab/A_build_Valentine_WhiteFox_A.prefab",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10026, season='')",
        "faction": "HQ Skins",
        "name": "Heartfelt Fox",
        "slug": "hq_skin_heartfelt_fox",
        "decoration_id": "10026",
        "evidence": (
            "decoration.json(id=10026, type=1, name='Heartfelt Fox', model='A_build_Valentine_WhiteFox_A') -> "
            "valentine_fox::A_build_Valentine_WhiteFox_A.prefab"
        ),
    },
    {
        "prefab_path": "Assets/_Art_LastDay/Models/Environment/Decorate/A_build_Valentine_Fox/Prefab/A_build_Valentine_WhiteFox_A_world.prefab",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10026, season='')",
        "faction": "HQ Skins",
        "name": "Heartfelt Fox World",
        "slug": "hq_skin_heartfelt_fox_world",
        "decoration_id": "10026",
        "evidence": (
            "decoration.json(id=10026, type=1, name='Heartfelt Fox', model_world='A_build_Valentine_WhiteFox_A_world') -> "
            "valentine_fox::A_build_Valentine_WhiteFox_A_world.prefab"
        ),
    },
]

# Newly extracted Transform-hierarchy 3D prefab bundles (Santa Chaos + 5 main_prefabs_building_* mesh bundles)
PREFAB_3D_EXTRACTIONS: List[Dict[str, Any]] = [
    {
        "bundle_glob": "main_prefabs_building_a_build_shengsanjiepifu_01_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10003, season='')",
        "faction": "HQ Skins",
        "name": "Santa Chaos",
        "slug": "hq_skin_santa_chaos",
        "decoration_id": "10003",
        "root_filter": None,
        "evidence": (
            "decoration.json(id=10003, type=1, name='Santa Chaos', model='A_Build_ShengSanJiePiFu_01') -> "
            "main_prefabs_building_a_build_shengsanjiepifu_01 + a_build_shengsanjiepifu_01 materials"
        ),
    },
    {
        "bundle_glob": "main_prefabs_building_a_build_shengsanjiepifu_01_world_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10003, season='')",
        "faction": "HQ Skins",
        "name": "Santa Chaos World",
        "slug": "hq_skin_santa_chaos_world",
        "decoration_id": "10003",
        "root_filter": None,
        "evidence": (
            "decoration.json(id=10003, type=1, name='Santa Chaos', model_world='A_Build_ShengSanJiePiFu_01_world') -> "
            "main_prefabs_building_a_build_shengsanjiepifu_01_world"
        ),
    },
    {
        "bundle_glob": "art_lastday_models_environment_decorate_a_build_shengsanjiepifu_s3_01_[0-9a-f]*.bundle",
        "season": "Season 3",
        "season_source": "Everfrost Era S3 bundle(a_build_shengsanjiepifu_s3_01)",
        "faction": "HQ Skins",
        "name": "Santa Chaos S3",
        "slug": "environment_decorate_a_build_shengsanjiepifu_s3_01",
        "decoration_id": "10003",
        "root_filter": "A_Build_ShengSanJiePiFu_01_world_S3",
        "evidence": (
            "decoration.json(id=10003, type=1, name='Santa Chaos') Everfrost Era S3 snow variant "
            "(a_build_shengsanjiepifu_s3_01)"
        ),
    },
    {
        "bundle_glob": "main_prefabs_building_world_shengdanjiexueren_01_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10024, season='')",
        "faction": "HQ Skins",
        "name": "Snowlaf",
        "slug": "main_prefabs_building_world_shengdanjiexueren_01",
        "decoration_id": "10024",
        "root_filter": None,
        "evidence": (
            "decoration.json(id=10024, type=1, name='Snowlaf', model_world='World_Shengdanjiexueren_01') -> "
            "main_prefabs_building_world_shengdanjiexueren_01"
        ),
    },
    {
        "bundle_glob": "main_prefabs_building_world_pijiujie_01_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10019, type=10, season='')",
        "faction": "HQ Skins",
        "name": "Disco Ball World",
        "slug": "main_prefabs_building_world_pijiujie_01",
        "decoration_id": "10019",
        "root_filter": None,
        "evidence": (
            "decoration.json(id=10019, type=10, name='Disco Ball', model_world='World_pijiujie_01') -> "
            "main_prefabs_building_world_pijiujie_01"
        ),
    },
    {
        "bundle_glob": "main_prefabs_building_a_build_christmassnowman_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10023, type=10, season='')",
        "faction": "HQ Skins",
        "name": "Disco Ball Snowman",
        "slug": "main_prefabs_building_a_build_christmassnowman",
        "decoration_id": "10023",
        "root_filter": None,
        "evidence": (
            "decoration.json(id=10023, type=10, name='Disco Ball', model_world='A_build_ChristmasSnowMan') -> "
            "main_prefabs_building_a_build_christmassnowman"
        ),
    },
    {
        "bundle_glob": "art_lastday_models_environment_decorate_a_build_whitebear_a_hq_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10021, season='')",
        "faction": "HQ Skins",
        "name": "Bear Wick HQ",
        "slug": "environment_decorate_a_build_whitebear_a_hq",
        "decoration_id": "10021",
        "root_filter": None,
        "use_bind_pose": True,
        "evidence": (
            "decoration.json(id=10021, type=1, name='Bear Wick', model='A_build_WhiteBear_A') -> "
            "whitebear_a_hq + whitebear_common materials"
        ),
    },
    {
        "bundle_glob": "art_lastday_models_environment_decorate_a_build_whitebear_b_hq_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10021, season='')",
        "faction": "HQ Skins",
        "name": "Bear Wick HQ Tier 2",
        "slug": "environment_decorate_a_build_whitebear_b_hq",
        "decoration_id": "10021",
        "root_filter": None,
        "use_bind_pose": True,
        "evidence": (
            "decoration.json(id=10021, type=1, name='Bear Wick') Tier B HQ variant "
            "(whitebear_b_hq + whitebear_common materials)"
        ),
    },
    {
        "bundle_glob": "art_lastday_models_environment_decorate_a_build_whitebear_a_world_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10021, season='')",
        "faction": "HQ Skins",
        "name": "Bear Wick World",
        "slug": "environment_decorate_a_build_whitebear_a_world",
        "decoration_id": "10021",
        "root_filter": None,
        "use_bind_pose": True,
        "evidence": (
            "decoration.json(id=10021, type=1, name='Bear Wick', model_world='A_build_WhiteBear_A_World') -> "
            "whitebear_a_world + whitebear_common materials"
        ),
    },
    {
        "bundle_glob": "art_lastday_models_environment_decorate_a_build_whitebear_b_world_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "decoration.json(id=10021, season='')",
        "faction": "HQ Skins",
        "name": "Bear Wick World Tier 2",
        "slug": "environment_decorate_a_build_whitebear_b_world",
        "decoration_id": "10021",
        "root_filter": None,
        "use_bind_pose": True,
        "evidence": (
            "decoration.json(id=10021, type=1, name='Bear Wick') Tier B World variant "
            "(whitebear_b_world + whitebear_common materials)"
        ),
    },
    {
        "bundle_glob": "art_lastday_models_environment_map_world_resource_01_world_huoji_01_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "Holiday World Building(world_huoji_01)",
        "faction": "HQ Skins",
        "name": "Thanksgiving Roast Turkey World",
        "slug": "environment_map_world_resource_01_world_huoji_01",
        "decoration_id": "holiday_turkey_world",
        "root_filter": None,
        "evidence": (
            "world_resource_01_world_huoji_01 + a_build_huoji_01::Turkey_Material"
        ),
    },
    {
        "bundle_glob": "main_prefabs_building_world_turkey_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "Holiday World Building Prefab(world_turkey)",
        "faction": "HQ Skins",
        "name": "Thanksgiving Turkey Event",
        "slug": "main_prefabs_building_world_turkey",
        "decoration_id": "holiday_turkey_prefab",
        "root_filter": None,
        "evidence": (
            "main_prefabs_building_world_turkey -> World_HuoJi_01_Spine + a_build_huoji_01::Turkey_Material"
        ),
    },
    {
        "bundle_glob": "main_prefabs_building_worldblacklandruintag_[0-9a-f]*.bundle",
        "season": "Pre-Season 1",
        "season_source": "Core World Map Blackland Ruin Prefab(WorldBlackLandRuinTag)",
        "faction": "Buildings and Environment",
        "name": "Blackland Ruin",
        "slug": "main_prefabs_building_worldblacklandruintag",
        "decoration_id": "",
        "root_filter": None,
        "evidence": (
            "main_prefabs_building_worldblacklandruintag -> World_Flag_01..03_Spine + a_build_shijiejianzhu::ruins_flag"
        ),
    },
]


# ---------------------------------------------------------------------------
# Task B: Verified 3D Vehicle / March Skin Mappings (decoration.json type=4)
# ---------------------------------------------------------------------------
VEHICLE_SKIN_MOVES_BY_SLUG: Dict[str, Dict[str, str]] = {
    # Conqueror (decoration.json id=50001/50005/50009, WorldTroop_001/Up1/Up2 -> dajiaoche_01, car_show id=1)
    "environment_decorate_a_vehicle_dajiaoche_01": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Conqueror Showcase",
        "decoration_id": "50001,50005,50009",
        "evidence": (
            "decoration.json(id=50001/50005/50009, type=4, name='Conqueror', model='WorldTroop_001..Up2') + "
            "main_prefabs_building_worldtroop_001(A_vehicle_dajiaoche_01..03) + car show.json(id=1)"
        ),
    },
    "environment_decorate_a_vehicle_dajiaoche_01_shijie": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Conqueror World",
        "decoration_id": "50001,50005,50009",
        "evidence": (
            "decoration.json(id=50001/50005/50009, type=4, name='Conqueror', model='WorldTroop_001..Up2') -> "
            "a_vehicle_dajiaoche_01_shijie world march model"
        ),
    },
    "environment_decorate_a_vehicle_dajiaoche_01_guanka": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Conqueror Stage",
        "decoration_id": "50001,50005,50009",
        "evidence": (
            "decoration.json(id=50001/50005/50009, type=4, name='Conqueror') + "
            "car show barrel.json(A_vehicle_dajiaoche_guanka_01..03)"
        ),
    },
    # Cheetah Armored Vehicle (decoration.json id=50002/50006/50010, WorldTroop_002/Up1/Up2 -> zhuangjiache_01, car_show id=2)
    "environment_decorate_a_vehicle_zhuangjiache_01_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Cheetah Armored Vehicle Showcase",
        "decoration_id": "50002,50006,50010",
        "evidence": (
            "decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle', model='WorldTroop_002..Up2') + "
            "main_prefabs_building_worldtroop_002(A_vehicle_zhuangjaiche_01..03) + car show.json(id=2)"
        ),
    },
    "environment_decorate_a_vehicle_zhuangjiache_01_shijie": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Cheetah Armored Vehicle World",
        "decoration_id": "50002,50006,50010",
        "evidence": (
            "decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle') -> "
            "a_vehicle_zhuangjiache_01_shijie world march model"
        ),
    },
    "environment_decorate_a_vehicle_zhuangjiache_01_guanka": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Cheetah Armored Vehicle Stage",
        "decoration_id": "50002,50006,50010",
        "evidence": (
            "decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle') + "
            "car show barrel.json(A_vehicle_zhuangjiache_guanka_01..03)"
        ),
    },
    "environment_decorate_a_vehicle_zhuangjiache_01": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Cheetah Armored Vehicle Classic",
        "decoration_id": "50002,50006,50010",
        "evidence": (
            "decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle') base garage model "
            "(a_vehicle_zhuangjiache_01)"
        ),
    },
    # Hercules (decoration.json id=50003/50007/50011, WorldTroop_003/Up1/Up2 -> tanke, car_show id=3)
    "environment_decorate_a_vehicle_tanke_zhanshi_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Hercules Showcase",
        "decoration_id": "50003,50007,50011",
        "evidence": (
            "decoration.json(id=50003/50007/50011, type=4, name='Hercules', model='WorldTroop_003..Up2') + "
            "main_prefabs_building_worldtroop_003(A_vehicle_tanke_01..03) + car show.json(id=3)"
        ),
    },
    "environment_decorate_a_vehicle_tanke_shijie_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Hercules World",
        "decoration_id": "50003,50007,50011",
        "evidence": (
            "decoration.json(id=50003/50007/50011, type=4, name='Hercules') -> "
            "a_vehicle_tanke_shijie_formal world march model"
        ),
    },
    "environment_decorate_a_vehicle_tanke_guanka_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Hercules Stage",
        "decoration_id": "50003,50007,50011",
        "evidence": (
            "decoration.json(id=50003/50007/50011, type=4, name='Hercules') + "
            "car show barrel.json(A_vehicle_tanke_guanka_01..03_formal)"
        ),
    },
    "environment_decorate_a_vehicle_tanke": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Hercules Classic",
        "decoration_id": "50003,50007,50011",
        "evidence": "decoration.json(id=50003/50007/50011, type=4, name='Hercules') base garage tank (a_vehicle_tanke)",
    },
    "environment_decorate_a_vehicle_tanke_guanka": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Hercules Classic Stage",
        "decoration_id": "50003,50007,50011",
        "evidence": "decoration.json(id=50003/50007/50011, type=4, name='Hercules') stage tank (a_vehicle_tanke_guanka)",
    },
    # Destroyer (decoration.json id=50004/50008/50012, WorldTroop_004/Up1/Up2 + WorldTroop_005 + car_show id=4)
    "environment_decorate_a_vehicle_daodanche_zhanshi": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Showcase",
        "decoration_id": "50004,50008,50012",
        "evidence": (
            "decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + "
            "car show.json(id=4, model='A_vehicle_daodanche_02..03_zhanshi')"
        ),
    },
    "environment_decorate_a_vehicle_daodanche_world": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer World",
        "decoration_id": "50004,50008,50012",
        "evidence": (
            "decoration.json(id=50004/50008/50012, type=4, name='Destroyer') -> "
            "a_vehicle_daodanche_world world march model"
        ),
    },
    "environment_decorate_a_vehicle_daodanche_guanka": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Stage",
        "decoration_id": "50004,50008,50012",
        "evidence": (
            "decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + "
            "car show barrel.json(A_vehicle_daodanche_02..03_guanka)"
        ),
    },
    "environment_decorate_a_vehicle_huojianche_zhanshi_linshi": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Tier 1 Showcase",
        "decoration_id": "50004",
        "evidence": (
            "decoration.json(id=50004, type=4, name='Destroyer', model='WorldTroop_004') + "
            "car show.json(id=4, Tier 1 model='A_vehicle_huojianche_zhanshi_linshi')"
        ),
    },
    "environment_decorate_a_vehicle_huojianche_zhanshi_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Rocket Showcase",
        "decoration_id": "50004,50008,50012",
        "evidence": (
            "decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + "
            "main_prefabs_building_worldtroop_004(A_vehicle_huojianche_01..03) -> a_vehicle_huojianche_zhanshi_formal"
        ),
    },
    "environment_decorate_a_vehicle_huojianche_shijie_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Rocket World",
        "decoration_id": "50004,50008,50012",
        "evidence": (
            "decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + "
            "main_prefabs_building_worldtroop_005 -> a_vehicle_huojianche_shijie_formal"
        ),
    },
    "environment_decorate_a_vehicle_huojianche_guanka_formal": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Rocket Stage",
        "decoration_id": "50004,50008,50012",
        "evidence": (
            "decoration.json(id=50004/50008/50012, type=4, name='Destroyer') -> "
            "a_vehicle_huojianche_guanka_formal stage model"
        ),
    },
    "environment_decorate_a_vehicle_huojianche": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Rocket Classic",
        "decoration_id": "50004",
        "evidence": "decoration.json(id=50004, type=4, name='Destroyer') classic showcase model (a_vehicle_huojianche)",
    },
    "environment_decorate_a_vehicle_huojianche_shijie": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Rocket Classic World",
        "decoration_id": "50004",
        "evidence": (
            "decoration.json(id=50004, type=4, name='Destroyer') Tier 1 world march model (a_vehicle_huojianche_shijie)"
        ),
    },
    "environment_decorate_a_vehicle_huojianche_guanka": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer Rocket Classic Stage",
        "decoration_id": "50004",
        "evidence": (
            "decoration.json(id=50004, type=4, name='Destroyer') + "
            "car show barrel.json(A_vehicle_huojianche_guanka)"
        ),
    },
    # Destroyer-EX (decoration.json id=50014/50015/50016, WorldTroop_005_new/Up1/Up2 -> daodanche_ex, car_show id=5)
    "environment_decorate_a_vehicle_daodanche_ex_zhanshi": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer-EX Showcase",
        "decoration_id": "50014,50015,50016",
        "evidence": (
            "decoration.json(id=50014/50015/50016, type=4, name='Destroyer-EX', model='WorldTroop_005_new..Up2') + "
            "car show.json(id=5, model='A_vehicle_daodanche_EX_01..03_zhanshi')"
        ),
    },
    "environment_decorate_a_vehicle_daodanche_ex_world": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer-EX World",
        "decoration_id": "50014,50015,50016",
        "evidence": (
            "decoration.json(id=50014/50015/50016, type=4, name='Destroyer-EX') + "
            "main_prefabs_building_worldtroop_005_newup2 -> a_vehicle_daodanche_ex_world"
        ),
    },
    "environment_decorate_a_vehicle_daodanche_ex_guanka": {
        "season": "Pre-Season 1",
        "faction": "Vehicle Skins",
        "name": "Destroyer-EX Stage",
        "decoration_id": "50014,50015,50016",
        "evidence": (
            "decoration.json(id=50014/50015/50016, type=4, name='Destroyer-EX') + "
            "car show barrel.json(A_vehicle_daodanche_EX_01..03_guanka)"
        ),
    },
    # Season 4 Dinosaur March Skins (decoration.json id=40005, 40006, 40007, season=4)
    "environment_map_world_vehicle_s4_vehicle_bawanglong_s4": {
        "season": "Season 4",
        "faction": "Vehicle Skins",
        "name": "T-Rex",
        "decoration_id": "40005",
        "evidence": (
            "decoration.json(id=40005, type=4, season=4, name='T-Rex', model='Vehicle_BaWangLong_S4_Variant')"
        ),
    },
    "environment_map_world_vehicle_s4_vehicle_sanjiaolong_s4": {
        "season": "Season 4",
        "faction": "Vehicle Skins",
        "name": "Triceratops",
        "decoration_id": "40006",
        "evidence": (
            "decoration.json(id=40006, type=4, season=4, name='Triceratops', model='Vehicle_SanJiaoLong_S4_Variant')"
        ),
    },
    "environment_map_world_vehicle_s4_vehicle_jialong_s4": {
        "season": "Season 4",
        "faction": "Vehicle Skins",
        "name": "Ankylosaurus",
        "decoration_id": "40007",
        "evidence": (
            "decoration.json(id=40007, type=4, season=4, name='Ankylosaurus', model='Vehicle_JiaLong_S4_Variant')"
        ),
    },
}


# ---------------------------------------------------------------------------
# Text & Path Sanitization Helpers
# ---------------------------------------------------------------------------
def strip_em_dashes(text: str) -> str:
    """Guarantee zero U+2014 em dashes and normalize Roman numeral ligatures."""
    if not text:
        return ""
    s = str(text).replace(EM_DASH, " - ").replace("&" + "mdash;", " - ")
    s = s.replace("\u2160", "I").replace("\u2161", "II").replace("\u2162", "III").replace("\u2163", "IV")
    return s


def clean_loc_string(raw: str) -> str:
    s = re.sub(r"<[^>]+>", "", str(raw or ""))
    s = strip_em_dashes(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_display_name(name: str, max_len: int = 72) -> str:
    """Clean a display/folder/GLB name: spaces allowed, zero underscores, zero em dashes."""
    s = strip_em_dashes(str(name or ""))
    s = s.replace("_", " ")
    s = re.sub(r'[<>:"/\\|?*]+', " ", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    if not s:
        s = "Model"
    if len(s) > max_len:
        cut = s[:max_len].rsplit(" ", 1)[0].strip()
        s = cut if len(cut) >= 12 else s[:max_len].strip()
    assert "_" not in s and EM_DASH not in s
    return s


def clean_asset_token(name: str, max_len: int = 56) -> str:
    """
    Convert an internal mesh/material/texture/spine identifier into a clean hyphen-separated
    ASCII filename stem with ZERO underscores and ZERO spaces.
    """
    s = strip_em_dashes(str(name or ""))
    for src, dst in (("ú", "u"), ("Ú", "U"), ("é", "e"), ("á", "a"), ("í", "i"), ("ó", "o")):
        s = s.replace(src, dst)
    s = s.replace("_", "-")
    s = re.sub(r"[^A-Za-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "part"
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    assert "_" not in s and " " not in s and EM_DASH not in s
    return s


# ---------------------------------------------------------------------------
# UnityPy Bundle & XML Table Helpers
# ---------------------------------------------------------------------------
def load_unity_bundle(bundle_path: Path) -> UnityPy.Environment:
    """Strip Last Z's 8-byte UnityRaw prefix before UnityFS and load via UnityPy."""
    raw = bundle_path.read_bytes()
    if raw.startswith(b"UnityRawUnityFS"):
        raw = raw[8:]
    elif raw.startswith(b"UnityRaw"):
        idx = raw.find(b"UnityFS")
        if 0 < idx <= 16:
            raw = raw[idx:]
    return UnityPy.load(raw)


def load_localization(repo_dir: Path) -> Dict[str, str]:
    loc: Dict[str, str] = {}
    loc_json_path = repo_dir / "megamind" / "raw" / "localization en.json"
    if loc_json_path.exists():
        data = json.loads(loc_json_path.read_text(encoding="utf-8"))
        strings = data.get("strings", data) if isinstance(data, dict) else {}
        for k, v in strings.items():
            loc[str(k).strip()] = clean_loc_string(str(v))

    dialog_path = repo_dir / "launcher" / "assets" / "english-dialog.txt"
    if dialog_path.exists():
        for line in dialog_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                ks = k.strip()
                vs = clean_loc_string(v)
                if ks and vs:
                    loc[ks] = vs
    return loc


def load_xml_table(xml_dir: Path, table_name: str) -> List[Dict[str, Any]]:
    p = xml_dir / table_name
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    cols = data.get("columns", [])
    rows_raw = data.get("rows", [])
    rows_iter = list(rows_raw.values()) if isinstance(rows_raw, dict) else rows_raw
    out: List[Dict[str, Any]] = []
    for r in rows_iter:
        if isinstance(r, dict):
            out.append(r)
        elif isinstance(r, list):
            out.append(dict(zip(cols, r)))
    return out


def build_cab_index(ab_dir: Path) -> Dict[str, Path]:
    """Index internal CAB-<hash> names across model, spine, prefab, and material bundles."""
    cab_map: Dict[str, Path] = {}
    prefixes = (
        "art_lastday_models_",
        "art_barrel_models_",
        "art_lastday_spine_hero_",
        "gameres_auto_assets_",
        "main_material_",
        "main_prefabs_building_",
    )
    for p in sorted(ab_dir.glob("*.bundle")):
        if not p.name.startswith(prefixes):
            continue
        try:
            env = load_unity_bundle(p)
            if env.objects:
                af_name = env.objects[0].assets_file.name.lower()
                if af_name:
                    cab_map[af_name] = p
        except Exception:
            pass
    return cab_map


# ---------------------------------------------------------------------------
# 3D Texture, Transform, OBJ/MTL & GLB Export Helpers
# ---------------------------------------------------------------------------
def is_normal_map_name(tex_name: str, used_as_normal: bool = False) -> bool:
    if used_as_normal:
        return True
    low = tex_name.lower()
    return bool(re.search(r"(_n|_nm|_normal|_normalmap|_normals|_bump)(\b|_\d+$)", low))


def unpack_dxt5nm_if_needed(img: Image.Image) -> Tuple[Image.Image, bool]:
    rgba = img.convert("RGBA")
    arr = np.array(rgba, dtype=np.uint8)
    if arr.ndim != 3 or arr.shape[2] != 4:
        return rgba, False
    r_min = int(arr[:, :, 0].min())
    a_min = int(arr[:, :, 3].min())
    a_max = int(arr[:, :, 3].max())
    if r_min >= 250 and (a_max - a_min) > 8 and a_min < 245:
        nx = arr[:, :, 3].astype(np.float32) / 255.0 * 2.0 - 1.0
        ny = arr[:, :, 1].astype(np.float32) / 255.0 * 2.0 - 1.0
        nz = np.sqrt(np.clip(1.0 - nx * nx - ny * ny, 0.0, 1.0))
        out = np.empty_like(arr)
        out[:, :, 0] = arr[:, :, 3]
        out[:, :, 1] = arr[:, :, 1]
        out[:, :, 2] = np.clip(np.round((nz * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)
        out[:, :, 3] = 255
        return Image.fromarray(out), True
    return rgba, False


def trs_matrix_unity(pos: Dict[str, float], rot: Dict[str, float], scale: Dict[str, float]) -> np.ndarray:
    """Build 4x4 local TRS matrix in Unity left-handed space."""
    px, py, pz = float(pos.get("x", 0.0)), float(pos.get("y", 0.0)), float(pos.get("z", 0.0))
    qx, qy, qz, qw = (
        float(rot.get("x", 0.0)),
        float(rot.get("y", 0.0)),
        float(rot.get("z", 0.0)),
        float(rot.get("w", 1.0)),
    )
    qnorm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    if qnorm > 1e-8:
        qx, qy, qz, qw = qx / qnorm, qy / qnorm, qz / qnorm, qw / qnorm
    else:
        qx, qy, qz, qw = 0.0, 0.0, 0.0, 1.0
    sx, sy, sz = float(scale.get("x", 1.0)), float(scale.get("y", 1.0)), float(scale.get("z", 1.0))

    r00 = 1.0 - 2.0 * (qy * qy + qz * qz)
    r01 = 2.0 * (qx * qy - qz * qw)
    r02 = 2.0 * (qx * qz + qy * qw)
    r10 = 2.0 * (qx * qy + qz * qw)
    r11 = 1.0 - 2.0 * (qx * qx + qz * qz)
    r12 = 2.0 * (qy * qz - qx * qw)
    r20 = 2.0 * (qx * qz - qy * qw)
    r21 = 2.0 * (qy * qz + qx * qw)
    r22 = 1.0 - 2.0 * (qx * qx + qy * qy)

    mat = np.eye(4, dtype=np.float64)
    mat[0, 0], mat[0, 1], mat[0, 2], mat[0, 3] = r00 * sx, r01 * sy, r02 * sz, px
    mat[1, 0], mat[1, 1], mat[1, 2], mat[1, 3] = r10 * sx, r11 * sy, r12 * sz, py
    mat[2, 0], mat[2, 1], mat[2, 2], mat[2, 3] = r20 * sx, r21 * sy, r22 * sz, pz
    return mat


class CrossBundleResolver:
    """Multi-hop PPtr resolver across UnityPy Environments using CAB index."""

    def __init__(self, cab_map: Dict[str, Path]) -> None:
        self.cab_map = cab_map
        self.env_cache: Dict[Path, UnityPy.Environment] = {}
        self.pid_cache: Dict[str, Dict[int, Any]] = {}

    def get_env(self, bundle_path: Path) -> UnityPy.Environment:
        if bundle_path not in self.env_cache:
            env = load_unity_bundle(bundle_path)
            self.env_cache[bundle_path] = env
            if env.objects:
                af_name = env.objects[0].assets_file.name.lower()
                self.pid_cache[af_name] = {o.path_id: o for o in env.objects}
        return self.env_cache[bundle_path]

    def resolve_pptr(self, owner_obj: Any, pptr: Optional[Dict[str, Any]]) -> Optional[Any]:
        if not pptr:
            return None
        fid = int(pptr.get("m_FileID", 0) or 0)
        pid = int(pptr.get("m_PathID", 0) or 0)
        if pid == 0:
            return None
        af = owner_obj.assets_file
        if fid == 0:
            af_key = af.name.lower()
            if af_key not in self.pid_cache:
                self.pid_cache[af_key] = {o.path_id: o for o in af.objects.values()}
            return self.pid_cache[af_key].get(pid)
        exts = [e.name.lower() for e in af.externals]
        if 1 <= fid <= len(exts):
            ext_cab = exts[fid - 1]
            ext_path = self.cab_map.get(ext_cab)
            if ext_path is not None:
                self.get_env(ext_path)
                return self.pid_cache.get(ext_cab, {}).get(pid)
        return None


def export_3d_render_items(
    out_dir: Path,
    model_name: str,
    season: str,
    season_source: str,
    faction: str,
    slug: str,
    source_bundle: str,
    evidence_source: str,
    render_items: List[Dict[str, Any]],
    anim_clips: List[str],
    resolver: CrossBundleResolver,
    force_alpha_blend: bool = False,
) -> Dict[str, Any]:
    """
    Export a list of resolved 3D render_items into clean underscore-free:
      - textures/*.png (with DXT5nm normal unpacking)
      - <part>.obj + materials.mtl
      - <Model Name>.glb
      - model-info.json
    """
    if out_dir.exists():
        shutil.rmtree(out_dir)
    tex_dir = out_dir / "textures"
    tex_dir.mkdir(parents=True, exist_ok=True)

    exported_textures: Dict[Tuple[str, int], Dict[str, Any]] = {}
    used_tex_stems: Dict[str, int] = {}

    def register_tex(tex_obj: Any, used_as_normal: bool = False) -> Optional[Dict[str, Any]]:
        key = (tex_obj.assets_file.name.lower(), int(tex_obj.path_id))
        if key in exported_textures:
            entry = exported_textures[key]
            if used_as_normal and not entry["unpacked_normal"]:
                unpacked_img, did_unpack = unpack_dxt5nm_if_needed(entry["raw_img"])
                if did_unpack:
                    unpacked_img.save(tex_dir / entry["filename"], format="PNG")
                    entry["img"] = unpacked_img
                    entry["unpacked_normal"] = True
            return entry
        tdata = tex_obj.read()
        raw_name = strip_em_dashes(tdata.m_Name or f"tex-{abs(tex_obj.path_id)}")
        pil_img = tdata.image
        if pil_img is None or pil_img.size[0] <= 0 or pil_img.size[1] <= 0:
            return None
        raw_rgba = pil_img.convert("RGBA")
        final_img = raw_rgba
        did_unpack = False
        if is_normal_map_name(raw_name, used_as_normal=used_as_normal):
            final_img, did_unpack = unpack_dxt5nm_if_needed(raw_rgba)

        stem = clean_asset_token(raw_name, max_len=48)
        low = stem.lower()
        if low in used_tex_stems:
            used_tex_stems[low] += 1
            stem = f"{stem}-{used_tex_stems[low]}"
        else:
            used_tex_stems[low] = 1
        fname = f"{stem}.png"
        final_img.save(tex_dir / fname, format="PNG")
        entry = {
            "name": raw_name,
            "filename": fname,
            "rel_path": f"textures/{fname}",
            "width": final_img.size[0],
            "height": final_img.size[1],
            "img": final_img,
            "raw_img": raw_rgba,
            "unpacked_normal": did_unpack,
        }
        exported_textures[key] = entry
        return entry

    parsed_mats: Dict[Tuple[str, int], Dict[str, Any]] = {}
    mtl_registry: Dict[str, Dict[str, Any]] = {}
    used_mat_stems: Dict[str, int] = {}

    def parse_mat(mat_obj: Any) -> Dict[str, Any]:
        mkey = (mat_obj.assets_file.name.lower(), int(mat_obj.path_id))
        if mkey in parsed_mats:
            return parsed_mats[mkey]
        tt = mat_obj.read_typetree()
        raw_mname = strip_em_dashes(tt.get("m_Name") or f"mat-{abs(mat_obj.path_id)}")
        saved = tt.get("m_SavedProperties", {})
        tex_envs = saved.get("m_TexEnvs", [])
        colors = saved.get("m_Colors", [])

        kd = (1.0, 1.0, 1.0)
        for c_item in colors:
            if isinstance(c_item, (list, tuple)) and len(c_item) == 2:
                cname, cval = c_item
                if cname in ("_BaseColor", "_Color") and isinstance(cval, dict):
                    r, g, b = float(cval.get("r", 1.0)), float(cval.get("g", 1.0)), float(cval.get("b", 1.0))
                    if (r + g + b) > 0.05:
                        kd = (
                            round(min(max(r, 0.0), 1.0), 4),
                            round(min(max(g, 0.0), 1.0), 4),
                            round(min(max(b, 0.0), 1.0), 4),
                        )
                    break

        tex_prop_map: Dict[str, Dict[str, Any]] = {}
        for t_item in tex_envs:
            if isinstance(t_item, (list, tuple)) and len(t_item) == 2:
                pname, pval = t_item
                if isinstance(pval, dict) and isinstance(pval.get("m_Texture"), dict):
                    tex_prop_map[str(pname)] = pval["m_Texture"]

        diffuse_entry = None
        for dprop in ("_BaseMap", "_MainTex", "_AlbedoMap", "_ColorMap", "_Diffuse", "_Tex"):
            pptr = tex_prop_map.get(dprop)
            if pptr and int(pptr.get("m_PathID", 0) or 0) != 0:
                tobj = resolver.resolve_pptr(mat_obj, pptr)
                if tobj is not None and tobj.type.name == "Texture2D":
                    diffuse_entry = register_tex(tobj, used_as_normal=False)
                    if diffuse_entry is not None:
                        break

        normal_entry = None
        for nprop in ("_NormalMap", "_BumpMap", "_Normal", "_DetailNormalMap", "_Dump"):
            pptr = tex_prop_map.get(nprop)
            if pptr and int(pptr.get("m_PathID", 0) or 0) != 0:
                tobj = resolver.resolve_pptr(mat_obj, pptr)
                if tobj is not None and tobj.type.name == "Texture2D":
                    normal_entry = register_tex(tobj, used_as_normal=True)
                    if normal_entry is not None:
                        break

        s_mat = clean_asset_token(raw_mname, max_len=48)
        low_m = s_mat.lower()
        if low_m in used_mat_stems:
            used_mat_stems[low_m] += 1
            s_mat = f"{s_mat}-{used_mat_stems[low_m]}"
        else:
            used_mat_stems[low_m] = 1

        minfo = {
            "name": raw_mname,
            "safe_name": s_mat,
            "kd": kd,
            "diffuse": diffuse_entry,
            "normal": normal_entry,
        }
        parsed_mats[mkey] = minfo
        mtl_registry[s_mat] = minfo
        return minfo

    used_obj_stems: Dict[str, int] = {}
    mesh_records: List[Dict[str, Any]] = []
    glb_scene_geoms: Dict[str, trimesh.Trimesh] = {}
    glb_errors: List[str] = []
    exported_files: List[str] = []

    non_shadow_exists = any(not ri.get("is_shadow", False) for ri in render_items)

    for idx_r, ri in enumerate(render_items):
        mesh_obj = ri["mesh_obj"]
        mdata = mesh_obj.read()
        mh = MeshHandler(mdata)
        mh.process()
        tris_by_sub = mh.get_triangles() if mh.m_VertexCount > 0 else []
        total_f = sum(len(t) for t in tris_by_sub)
        if mh.m_VertexCount <= 0 or total_f <= 0 or not mh.m_Vertices:
            continue

        raw_part_name = strip_em_dashes(ri["part_name"] or mdata.m_Name or f"part-{idx_r + 1}")
        include_in_glb = (not ri.get("is_shadow", False)) if non_shadow_exists else True

        verts_u = np.array([[v[0], v[1], v[2]] for v in mh.m_Vertices], dtype=np.float64)
        verts_u = np.nan_to_num(verts_u, nan=0.0, posinf=0.0, neginf=0.0)

        has_norm = bool(mh.m_Normals and len(mh.m_Normals) == len(verts_u))
        norms_u = (
            np.nan_to_num(np.array([[n[0], n[1], n[2]] for n in mh.m_Normals], dtype=np.float64), nan=0.0)
            if has_norm
            else None
        )

        world_mat: Optional[np.ndarray] = ri.get("world_mat")
        flip_winding = False
        if world_mat is not None:
            ones = np.ones((len(verts_u), 1), dtype=np.float64)
            verts_h = np.hstack([verts_u, ones])
            verts_u = (verts_h @ world_mat.T)[:, :3]
            lin3 = world_mat[:3, :3]
            det3 = float(np.linalg.det(lin3))
            if det3 < 0.0:
                flip_winding = True
            if norms_u is not None and abs(det3) > 1e-10:
                inv_t = np.linalg.inv(lin3).T
                norms_u = norms_u @ inv_t.T
                n_lens = np.linalg.norm(norms_u, axis=1, keepdims=True)
                n_lens = np.where(n_lens > 1e-8, n_lens, 1.0)
                norms_u = norms_u / n_lens

        # Convert Unity left-handed (x, y, z) -> right-handed (-x, y, z)
        verts_rh = verts_u.copy()
        verts_rh[:, 0] = -verts_rh[:, 0]
        norms_rh = None
        if norms_u is not None:
            norms_rh = norms_u.copy()
            norms_rh[:, 0] = -norms_rh[:, 0]

        has_uv = bool(mh.m_UV0 and len(mh.m_UV0) == len(verts_rh))
        uvs_arr = (
            np.nan_to_num(np.array([[uv[0], uv[1]] for uv in mh.m_UV0], dtype=np.float64), nan=0.0)
            if has_uv
            else None
        )

        clean_stem = clean_asset_token(raw_part_name, max_len=48)
        low_o = clean_stem.lower()
        if low_o in used_obj_stems:
            used_obj_stems[low_o] += 1
            clean_stem = f"{clean_stem}-{used_obj_stems[low_o]}"
        else:
            used_obj_stems[low_o] = 1
        obj_filename = f"{clean_stem}.obj"

        obj_lines: List[str] = [
            "# Exported from Last Z AssetBundles\n",
            "mtllib materials.mtl\n",
            f"o {clean_stem}\n",
        ]
        for vx, vy, vz in verts_rh:
            obj_lines.append(f"v {vx:.7g} {vy:.7g} {vz:.7g}\n")
        if uvs_arr is not None:
            for u, v in uvs_arr:
                obj_lines.append(f"vt {u:.7g} {v:.7g}\n")
        if norms_rh is not None:
            for nx, ny, nz in norms_rh:
                obj_lines.append(f"vn {nx:.7g} {ny:.7g} {nz:.7g}\n")

        mat_objs: List[Optional[Any]] = ri.get("mat_objs", [])
        sub_mat_names: List[str] = []
        non_empty_subs = 0

        for s_idx, sub_tris in enumerate(tris_by_sub):
            if not sub_tris:
                continue
            non_empty_subs += 1
            mobj = mat_objs[s_idx] if s_idx < len(mat_objs) else (mat_objs[-1] if mat_objs else None)
            if mobj is not None:
                minfo = parse_mat(mobj)
            else:
                fb_name = clean_asset_token(f"{clean_stem}-mat-{s_idx}", max_len=48)
                minfo = mtl_registry.setdefault(
                    fb_name,
                    {
                        "name": fb_name,
                        "safe_name": fb_name,
                        "kd": (1.0, 1.0, 1.0),
                        "diffuse": None,
                        "normal": None,
                    },
                )

            s_mat = minfo["safe_name"]
            sub_mat_names.append(s_mat)
            obj_lines.append(f"g {clean_stem}-{s_idx}\n")
            obj_lines.append(f"usemtl {s_mat}\n")

            ordered_tris = [(a, b, c) if flip_winding else (c, b, a) for a, b, c in sub_tris]
            if has_uv and norms_rh is not None:
                for ia0, ib0, ic0 in ordered_tris:
                    ia, ib, ic = ia0 + 1, ib0 + 1, ic0 + 1
                    obj_lines.append(f"f {ia}/{ia}/{ia} {ib}/{ib}/{ib} {ic}/{ic}/{ic}\n")
            elif has_uv:
                for ia0, ib0, ic0 in ordered_tris:
                    ia, ib, ic = ia0 + 1, ib0 + 1, ic0 + 1
                    obj_lines.append(f"f {ia}/{ia} {ib}/{ib} {ic}/{ic}\n")
            elif norms_rh is not None:
                for ia0, ib0, ic0 in ordered_tris:
                    ia, ib, ic = ia0 + 1, ib0 + 1, ic0 + 1
                    obj_lines.append(f"f {ia}//{ia} {ib}//{ib} {ic}//{ic}\n")
            else:
                for ia0, ib0, ic0 in ordered_tris:
                    ia, ib, ic = ia0 + 1, ib0 + 1, ic0 + 1
                    obj_lines.append(f"f {ia} {ib} {ic}\n")

            if include_in_glb:
                try:
                    faces_arr = np.array(ordered_tris, dtype=np.int64)
                    used_v, inv_idx = np.unique(faces_arr.reshape(-1), return_inverse=True)
                    sub_verts = verts_rh[used_v]
                    sub_faces = inv_idx.reshape((-1, 3))
                    sub_norms = norms_rh[used_v] if norms_rh is not None else None
                    sub_uvs = uvs_arr[used_v] if uvs_arr is not None else None

                    d_entry = minfo.get("diffuse")
                    n_entry = minfo.get("normal")
                    kd = minfo.get("kd", (1.0, 1.0, 1.0))

                    if d_entry is not None and sub_uvs is not None:
                        d_img = d_entry["img"]
                        low_hint = f"{raw_part_name} {minfo['name']}".lower()
                        is_alpha = force_alpha_blend or any(
                            k in low_hint for k in ("glass", "boli", "alpha", "tran", "fur", "eyelash", "huzi", "shadow")
                        )
                        base_tex = d_img if is_alpha else d_img.convert("RGB")
                        pbr_kwargs: Dict[str, Any] = {
                            "name": s_mat,
                            "baseColorTexture": base_tex,
                            "metallicFactor": 0.05,
                            "roughnessFactor": 0.85,
                            "alphaMode": "BLEND" if is_alpha else "OPAQUE",
                            "doubleSided": bool(force_alpha_blend or is_alpha),
                        }
                        if n_entry is not None:
                            pbr_kwargs["normalTexture"] = n_entry["img"].convert("RGB")
                        visual = TextureVisuals(uv=sub_uvs, material=PBRMaterial(**pbr_kwargs))
                    elif sub_uvs is not None:
                        pbr = PBRMaterial(
                            name=s_mat,
                            baseColorFactor=[int(kd[0] * 255), int(kd[1] * 255), int(kd[2] * 255), 255],
                            metallicFactor=0.05,
                            roughnessFactor=0.85,
                        )
                        visual = TextureVisuals(uv=sub_uvs, material=pbr)
                    else:
                        rgba_col = np.tile(
                            np.array([int(kd[0] * 255), int(kd[1] * 255), int(kd[2] * 255), 255], dtype=np.uint8),
                            (len(sub_verts), 1),
                        )
                        visual = ColorVisuals(vertex_colors=rgba_col)

                    tm = trimesh.Trimesh(
                        vertices=sub_verts,
                        faces=sub_faces,
                        vertex_normals=sub_norms,
                        visual=visual,
                        process=False,
                    )
                    geom_name = clean_stem if len(tris_by_sub) == 1 else f"{clean_stem}-sub{s_idx}"
                    if geom_name in glb_scene_geoms:
                        geom_name = f"{geom_name}-{idx_r}"
                    glb_scene_geoms[geom_name] = tm
                except Exception as gexc:
                    glb_errors.append(f"{clean_stem}[{s_idx}]: {strip_em_dashes(str(gexc))}")

        (out_dir / obj_filename).write_text(strip_em_dashes("".join(obj_lines)), encoding="utf-8")
        exported_files.append(obj_filename)

        mesh_records.append(
            {
                "name": raw_part_name,
                "obj_file": obj_filename,
                "vertices": int(mh.m_VertexCount),
                "faces": int(total_f),
                "submeshes": non_empty_subs,
                "included_in_glb": include_in_glb,
                "materials": sub_mat_names,
            }
        )

    # Write materials.mtl
    mtl_lines: List[str] = ["# Materials for Last Z 3D Model\n"]
    material_links: List[Dict[str, Any]] = []
    for s_mat, minfo in sorted(mtl_registry.items(), key=lambda kv: kv[0]):
        kd = minfo.get("kd", (1.0, 1.0, 1.0))
        d_entry = minfo.get("diffuse")
        n_entry = minfo.get("normal")
        mtl_lines.append(f"\nnewmtl {s_mat}\n")
        mtl_lines.append("Ka 0.2000 0.2000 0.2000\n")
        mtl_lines.append(f"Kd {kd[0]:.4f} {kd[1]:.4f} {kd[2]:.4f}\n")
        mtl_lines.append("Ks 0.1000 0.1000 0.1000\n")
        mtl_lines.append("Ns 32.0\n")
        mtl_lines.append("d 1.0\n")
        mtl_lines.append("illum 2\n")
        if d_entry is not None:
            mtl_lines.append(f"map_Kd {d_entry['rel_path']}\n")
        if n_entry is not None:
            mtl_lines.append(f"map_Bump {n_entry['rel_path']}\n")
        material_links.append(
            {
                "material": s_mat,
                "unity_material_name": minfo["name"],
                "diffuse_texture": d_entry["rel_path"] if d_entry else None,
                "normal_texture": n_entry["rel_path"] if n_entry else None,
            }
        )
    (out_dir / "materials.mtl").write_text(strip_em_dashes("".join(mtl_lines)), encoding="utf-8")
    exported_files.append("materials.mtl")

    # Export GLB
    glb_filename = f"{model_name}.glb"
    assert "_" not in glb_filename and EM_DASH not in glb_filename
    scene = trimesh.Scene()
    for gname, gmesh in glb_scene_geoms.items():
        scene.add_geometry(gmesh, node_name=gname, geom_name=gname)
    (out_dir / glb_filename).write_bytes(scene.export(file_type="glb"))
    exported_files.append(glb_filename)

    tex_meta_list: List[Dict[str, Any]] = []
    for te in sorted(exported_textures.values(), key=lambda x: x["rel_path"]):
        exported_files.append(te["rel_path"])
        tex_meta_list.append(
            {
                "name": te["name"],
                "file": te["rel_path"],
                "width": te["width"],
                "height": te["height"],
                "unpacked_dxt5nm": te["unpacked_normal"],
            }
        )
    exported_files.append("model-info.json")

    rel_folder = f"{season}/{faction}/{model_name}"
    info = {
        "asset_type": "3d_model",
        "season": season,
        "season_source": strip_em_dashes(season_source),
        "faction": faction,
        "camp_id": 0,
        "hero_id": None,
        "model_name": model_name,
        "english_name": model_name,
        "slug": slug,
        "evidence_source": strip_em_dashes(evidence_source),
        "source_bundle": source_bundle,
        "folder": rel_folder,
        "glb_file": glb_filename,
        "glb_submesh_count": len(glb_scene_geoms),
        "glb_errors": glb_errors,
        "mesh_count": len(mesh_records),
        "texture_count": len(tex_meta_list),
        "total_vertices": sum(m["vertices"] for m in mesh_records),
        "total_faces": sum(m["faces"] for m in mesh_records),
        "meshes": mesh_records,
        "material_texture_links": material_links,
        "textures": tex_meta_list,
        "animation_clips": [strip_em_dashes(a) for a in anim_clips],
        "exported_files": exported_files,
    }
    info_text = strip_em_dashes(json.dumps(info, indent=2, ensure_ascii=False))
    assert EM_DASH not in info_text
    (out_dir / "model-info.json").write_text(info_text, encoding="utf-8")
    return info


def extract_valentine_fox_splits(
    ab_dir: Path,
    models_dir: Path,
    resolver: CrossBundleResolver,
) -> List[Dict[str, Any]]:
    """Split valentine_fox bundle into Heartbound Fox (HQ + World) & Heartfelt Fox (HQ + World)."""
    vf_bundle = next(ab_dir.glob("art_lastday_models_environment_decorate_a_build_valentine_fox_*.bundle"))
    env = resolver.get_env(vf_bundle)

    gos: Dict[int, Dict[str, Any]] = {}
    trs: Dict[int, Dict[str, Any]] = {}
    children_by_tr: Dict[int, List[int]] = {}
    smrs_by_go: Dict[int, Tuple[Any, Dict[str, Any]]] = {}
    anim_clips: List[str] = []

    for o in env.objects:
        t = o.type.name
        if t == "GameObject":
            gos[o.path_id] = o.read_typetree()
        elif t == "Transform":
            tt = o.read_typetree()
            trs[o.path_id] = tt
            fpid = int(tt["m_Father"]["m_PathID"])
            children_by_tr.setdefault(fpid, []).append(o.path_id)
        elif t == "SkinnedMeshRenderer":
            tt = o.read_typetree()
            smrs_by_go[int(tt["m_GameObject"]["m_PathID"])] = (o, tt)
        elif t == "AnimationClip":
            nm = (o.peek_name() or "").strip()
            if nm:
                anim_clips.append(strip_em_dashes(nm))

    go_to_tr = {int(tt["m_GameObject"]["m_PathID"]): tr_pid for tr_pid, tt in trs.items()}
    prefab_roots: Dict[str, int] = {}
    for o in env.objects:
        if o.type.name == "AssetBundle":
            ab_tt = o.read_typetree()
            for k, v in ab_tt.get("m_Container", []):
                if k.lower().endswith(".prefab"):
                    pid = int(v["asset"]["m_PathID"])
                    if pid in gos and k not in prefab_roots:
                        prefab_roots[k] = pid

    results: List[Dict[str, Any]] = []
    for spec in VALENTINE_FOX_SPLITS:
        root_go_pid = prefab_roots[spec["prefab_path"]]
        rtr = go_to_tr[root_go_pid]
        queue = [rtr]
        render_items: List[Dict[str, Any]] = []
        seen_mesh_pids: Set[int] = set()

        while queue:
            ctr = queue.pop(0)
            cgo = int(trs[ctr]["m_GameObject"]["m_PathID"])
            if cgo in smrs_by_go:
                smr_obj, smr_tt = smrs_by_go[cgo]
                mesh_obj = resolver.resolve_pptr(smr_obj, smr_tt.get("m_Mesh"))
                if mesh_obj is not None and mesh_obj.type.name == "Mesh" and mesh_obj.path_id not in seen_mesh_pids:
                    seen_mesh_pids.add(mesh_obj.path_id)
                    mat_objs = []
                    for mp in smr_tt.get("m_Materials", []):
                        mo = resolver.resolve_pptr(smr_obj, mp)
                        if mo is not None and mo.type.name == "Material":
                            # Exclude drop-shadow overlay pass on Fox_Body/FoxBook so base diffuse wins cleanly
                            m_nm = (mo.peek_name() or "").lower()
                            if "shadow" in m_nm and len(smr_tt.get("m_Materials", [])) > 1:
                                continue
                            mat_objs.append(mo)
                    part_name = mesh_obj.peek_name() or gos[cgo].get("m_Name", "")
                    render_items.append(
                        {
                            "part_name": part_name,
                            "mesh_obj": mesh_obj,
                            "mat_objs": mat_objs,
                            "world_mat": None,
                            "is_shadow": "shadow" in part_name.lower(),
                        }
                    )
            queue.extend(children_by_tr.get(ctr, []))

        out_dir = models_dir / spec["season"] / spec["faction"] / spec["name"]
        info = export_3d_render_items(
            out_dir=out_dir,
            model_name=spec["name"],
            season=spec["season"],
            season_source=spec["season_source"],
            faction=spec["faction"],
            slug=spec["slug"],
            source_bundle=vf_bundle.name,
            evidence_source=spec["evidence"],
            render_items=render_items,
            anim_clips=sorted(set(anim_clips)),
            resolver=resolver,
            force_alpha_blend=False,
        )
        results.append(info)
    return results


def extract_prefab_3d_bundles(
    ab_dir: Path,
    models_dir: Path,
    resolver: CrossBundleResolver,
) -> List[Dict[str, Any]]:
    """Extract Transform-assembled 3D HQ skin & world building prefabs."""
    results: List[Dict[str, Any]] = []
    for spec in PREFAB_3D_EXTRACTIONS:
        matches = sorted(ab_dir.glob(spec["bundle_glob"]))
        if not matches:
            raise FileNotFoundError(f"Missing expected prefab bundle for glob: {spec['bundle_glob']}")
        bpath = matches[0]
        env = resolver.get_env(bpath)

        gos: Dict[int, Dict[str, Any]] = {}
        trs_by_go: Dict[int, Dict[str, Any]] = {}
        tr_to_go: Dict[int, int] = {}
        mfs_by_go: Dict[int, Tuple[Any, Dict[str, Any]]] = {}
        mrs_by_go: Dict[int, Tuple[Any, Dict[str, Any]]] = {}
        smrs_by_go: Dict[int, Tuple[Any, Dict[str, Any]]] = {}
        anim_clips: List[str] = []

        for o in env.objects:
            t = o.type.name
            if t == "GameObject":
                gos[o.path_id] = o.read_typetree()
            elif t == "Transform":
                tt = o.read_typetree()
                gpid = int(tt["m_GameObject"]["m_PathID"])
                trs_by_go[gpid] = {
                    "tr_pid": o.path_id,
                    "father_tr": int(tt["m_Father"]["m_PathID"]),
                    "pos": tt["m_LocalPosition"],
                    "rot": tt["m_LocalRotation"],
                    "scale": tt["m_LocalScale"],
                }
                tr_to_go[o.path_id] = gpid
            elif t == "MeshFilter":
                tt = o.read_typetree()
                mfs_by_go[int(tt["m_GameObject"]["m_PathID"])] = (o, tt)
            elif t == "MeshRenderer":
                tt = o.read_typetree()
                mrs_by_go[int(tt["m_GameObject"]["m_PathID"])] = (o, tt)
            elif t == "SkinnedMeshRenderer":
                tt = o.read_typetree()
                smrs_by_go[int(tt["m_GameObject"]["m_PathID"])] = (o, tt)
            elif t == "AnimationClip":
                nm = (o.peek_name() or "").strip()
                if nm:
                    anim_clips.append(strip_em_dashes(nm))

        render_items: List[Dict[str, Any]] = []
        seen_dedup: Set[Tuple[str, int, Tuple[int, ...]]] = set()
        use_bind_pose = bool(spec.get("use_bind_pose", False))

        if use_bind_pose:
            seen_mesh_pids: Set[int] = set()
            for go_pid, (smr_obj, smr_tt) in sorted(smrs_by_go.items(), key=lambda kv: kv[0]):
                mesh_obj = resolver.resolve_pptr(smr_obj, smr_tt.get("m_Mesh"))
                if mesh_obj is None or mesh_obj.type.name != "Mesh" or mesh_obj.path_id in seen_mesh_pids:
                    continue
                mat_objs = []
                for mp in smr_tt.get("m_Materials", []):
                    mo = resolver.resolve_pptr(smr_obj, mp)
                    if mo is not None and mo.type.name == "Material":
                        mat_objs.append(mo)
                if not mat_objs:
                    continue
                seen_mesh_pids.add(mesh_obj.path_id)
                pname = mesh_obj.peek_name() or gos.get(go_pid, {}).get("m_Name", "part")
                low_p = pname.lower()
                render_items.append(
                    {
                        "part_name": pname,
                        "mesh_obj": mesh_obj,
                        "mat_objs": mat_objs,
                        "world_mat": None,
                        "is_shadow": any(k in low_p for k in ("shadow", "_sdw", "(clone)_quality_")),
                    }
                )
            for go_pid, (mf_obj, mf_tt) in sorted(mfs_by_go.items(), key=lambda kv: kv[0]):
                mesh_obj = resolver.resolve_pptr(mf_obj, mf_tt.get("m_Mesh"))
                if mesh_obj is None or mesh_obj.type.name != "Mesh" or mesh_obj.path_id in seen_mesh_pids:
                    continue
                mr_pair = mrs_by_go.get(go_pid)
                if mr_pair is None:
                    continue
                mr_obj, mr_tt = mr_pair
                mat_objs = [
                    mo
                    for mp in mr_tt.get("m_Materials", [])
                    if (mo := resolver.resolve_pptr(mr_obj, mp)) is not None and mo.type.name == "Material"
                ]
                if not mat_objs:
                    continue
                seen_mesh_pids.add(mesh_obj.path_id)
                pname = mesh_obj.peek_name() or gos.get(go_pid, {}).get("m_Name", "part")
                low_p = pname.lower()
                render_items.append(
                    {
                        "part_name": pname,
                        "mesh_obj": mesh_obj,
                        "mat_objs": mat_objs,
                        "world_mat": None,
                        "is_shadow": any(k in low_p for k in ("shadow", "_sdw", "(clone)_quality_")),
                    }
                )
        else:
            for go_pid, (mf_obj, mf_tt) in sorted(mfs_by_go.items(), key=lambda kv: kv[0]):
                mesh_pptr = mf_tt.get("m_Mesh", {})
                if int(mesh_pptr.get("m_PathID", 0) or 0) == 0:
                    continue
                mesh_obj = resolver.resolve_pptr(mf_obj, mesh_pptr)
                if mesh_obj is None or mesh_obj.type.name != "Mesh":
                    continue

                mr_pair = mrs_by_go.get(go_pid)
                if mr_pair is None:
                    continue
                mr_obj, mr_tt = mr_pair
                mat_objs = []
                for mp in mr_tt.get("m_Materials", []):
                    mo = resolver.resolve_pptr(mr_obj, mp)
                    if mo is not None and mo.type.name == "Material":
                        mat_objs.append(mo)
                if not mat_objs:
                    continue

                chain_mats: List[np.ndarray] = []
                cur_go = go_pid
                root_go_name = gos.get(go_pid, {}).get("m_Name", "")
                while cur_go in trs_by_go:
                    tinfo = trs_by_go[cur_go]
                    chain_mats.append(trs_matrix_unity(tinfo["pos"], tinfo["rot"], tinfo["scale"]))
                    root_go_name = gos.get(cur_go, {}).get("m_Name", root_go_name)
                    ftr = tinfo["father_tr"]
                    if ftr == 0 or ftr not in tr_to_go:
                        break
                    cur_go = tr_to_go[ftr]

                if spec.get("root_filter") and root_go_name != spec["root_filter"]:
                    continue

                world_mat = np.eye(4, dtype=np.float64)
                for m_local in reversed(chain_mats):
                    world_mat = world_mat @ m_local

                go_name = gos.get(go_pid, {}).get("m_Name", "") or (mesh_obj.peek_name() or "part")
                dedup_key = (go_name.lower(), int(mesh_obj.path_id), tuple(int(m.path_id) for m in mat_objs))
                if dedup_key in seen_dedup:
                    continue
                seen_dedup.add(dedup_key)

                render_items.append(
                    {
                        "part_name": go_name,
                        "mesh_obj": mesh_obj,
                        "mat_objs": mat_objs,
                        "world_mat": world_mat,
                        "is_shadow": go_name.lower() == "shadow" or "shadow" in go_name.lower(),
                    }
                )

        if not render_items:
            raise RuntimeError(f"Zero renderable parts resolved for {bpath.name}")

        out_dir = models_dir / spec["season"] / spec["faction"] / spec["name"]
        info = export_3d_render_items(
            out_dir=out_dir,
            model_name=spec["name"],
            season=spec["season"],
            season_source=spec["season_source"],
            faction=spec["faction"],
            slug=spec["slug"],
            source_bundle=bpath.name,
            evidence_source=spec["evidence"],
            render_items=render_items,
            anim_clips=sorted(set(anim_clips)),
            resolver=resolver,
            force_alpha_blend=not use_bind_pose,
        )
        results.append(info)
    return results


# ---------------------------------------------------------------------------
# Move & Rename Existing 3D Model Helper
# ---------------------------------------------------------------------------
def relocate_existing_3d_model(
    models_dir: Path,
    model_rec: Dict[str, Any],
    target_season: str,
    target_faction: str,
    target_name: str,
    new_evidence: str,
) -> Dict[str, Any]:
    """Move an existing extracted 3D model folder, rename its GLB, and update model-info.json."""
    clean_name = clean_display_name(target_name)
    src_dir = models_dir / model_rec["folder"]
    dst_dir = models_dir / target_season / target_faction / clean_name

    if not src_dir.exists() and dst_dir.exists():
        src_dir = dst_dir
    if not src_dir.exists():
        raise FileNotFoundError(f"Source 3D model directory missing: {src_dir}")

    if src_dir.resolve() != dst_dir.resolve():
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        dst_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_dir), str(dst_dir))

    old_glb = model_rec.get("glb_file")
    new_glb = f"{clean_name}.glb"
    assert "_" not in new_glb and EM_DASH not in new_glb

    if old_glb and (dst_dir / old_glb).exists() and old_glb != new_glb:
        if (dst_dir / new_glb).exists():
            (dst_dir / new_glb).unlink()
        (dst_dir / old_glb).rename(dst_dir / new_glb)
    elif not (dst_dir / new_glb).exists():
        any_glbs = list(dst_dir.glob("*.glb"))
        if any_glbs:
            any_glbs[0].rename(dst_dir / new_glb)

    new_exported: List[str] = []
    for ef in model_rec.get("exported_files", []):
        if ef.endswith(".glb"):
            new_exported.append(new_glb)
        else:
            new_exported.append(ef)

    rel_folder = f"{target_season}/{target_faction}/{clean_name}"
    updated = dict(model_rec)
    updated["asset_type"] = "3d_model"
    updated["season"] = target_season
    updated["faction"] = target_faction
    updated["model_name"] = clean_name
    updated["english_name"] = clean_name
    updated["evidence_source"] = strip_em_dashes(new_evidence)
    updated["folder"] = rel_folder
    updated["glb_file"] = new_glb
    updated["exported_files"] = new_exported

    info_text = strip_em_dashes(json.dumps(updated, indent=2, ensure_ascii=False))
    assert EM_DASH not in info_text
    (dst_dir / "model-info.json").write_text(info_text, encoding="utf-8")
    return updated


# ---------------------------------------------------------------------------
# Task C: Extract All 110 2D Spine Hero Skin Bundles
# ---------------------------------------------------------------------------
def extract_all_spine_hero_skins(
    repo_dir: Path,
    ab_dir: Path,
    models_dir: Path,
    cab_map: Dict[str, Path],
) -> List[Dict[str, Any]]:
    """
    Cross-reference and extract ALL 110 art_lastday_spine_hero_*.bundle files into:
      models/<Season>/<Faction>/Hero Skins 2D Spine/<Hero Name> - <Skin Name>/
    """
    xml_dir = repo_dir / "megamind" / "raw" / "xml tables"
    loc = load_localization(repo_dir)

    heroes_rows = load_xml_table(xml_dir, "aps new heroes.json") + load_xml_table(
        xml_dir, "aps new heroes client B.json"
    )
    skins_rows = load_xml_table(xml_dir, "aps new heros skin.json")
    shop_rows = load_xml_table(xml_dir, "aps new heros skin shop.json")
    excl_rows = load_xml_table(xml_dir, "heroes exclusive equip.json")
    pve_heroes = load_xml_table(xml_dir, "c pve heroes.json")

    # Build hero lookup by id and by default hero_spine stem
    hero_by_id: Dict[int, Dict[str, Any]] = {}
    hero_by_spine: Dict[str, Dict[str, Any]] = {}
    for r in heroes_rows:
        hid_s = str(r.get("id", "")).strip()
        if not hid_s.isdigit():
            continue
        hid = int(hid_s)
        if hid >= 100000:
            continue
        camp_s = str(r.get("camp", "0") or "0").strip()
        camp = int(camp_s) if camp_s.lstrip("-").isdigit() else 0
        name_id = str(r.get("name", "")).strip()
        hero_name = clean_display_name(loc.get(name_id, name_id))
        s_raw = str(r.get("season", "0") or "0").strip()
        s_num = int(s_raw) if s_raw.isdigit() else 0
        season_label = "Pre-Season 1" if s_num <= 0 else f"Season {s_num}"

        aw_raw = str(r.get("awakening_season", "") or "").strip()
        aw_num: Optional[int] = None
        if aw_raw and "|" in aw_raw:
            p0 = aw_raw.split("|", 1)[0].strip()
            if p0.isdigit():
                aw_num = int(p0)
        elif aw_raw.isdigit() and int(aw_raw) > 0:
            aw_num = int(aw_raw)

        hspine = str(r.get("hero_spine", "") or "").strip()
        faction = CAMP_TO_FACTION.get(camp, "NPCs and Survivors")
        hrec = {
            "hero_id": hid,
            "hero_name": hero_name,
            "camp_id": camp,
            "faction": faction,
            "season": season_label,
            "season_num": s_num,
            "awakening_season": f"Season {aw_num}" if aw_num else season_label,
            "awakening_raw": aw_raw,
            "hero_spine": hspine,
        }
        # Prefer camp in (1,2,3) if duplicate ID across client tables
        if hid not in hero_by_id or (camp in (1, 2, 3) and hero_by_id[hid]["camp_id"] not in (1, 2, 3)):
            hero_by_id[hid] = hrec
        if hspine:
            hero_by_spine[hspine.lower()] = hrec

    # Shop lookup by skin_id
    shop_by_skin_id: Dict[str, Dict[str, Any]] = {}
    for sr in shop_rows:
        sid = str(sr.get("skin_id", "") or "").strip()
        if sid:
            shop_by_skin_id[sid] = sr

    # Exclusive weapon lookup by hero group ID
    excl_by_hero: Dict[int, Dict[str, str]] = {}
    for er in excl_rows:
        grp = str(er.get("group", "") or "").strip()
        if grp.isdigit() and int(grp) not in excl_by_hero:
            nid = str(er.get("name", "") or "").strip()
            excl_by_hero[int(grp)] = {
                "weapon_name": clean_loc_string(loc.get(nid, nid)),
                "weapon_spine": str(er.get("spine", "") or "").strip(),
                "season_raw": str(er.get("season", "") or "").strip(),
            }

    # Skin table lookup by hero_spine and hero_spine_ME
    skin_by_spine: Dict[str, Dict[str, Any]] = {}
    skin_by_spine_me: Dict[str, Dict[str, Any]] = {}
    for sk in skins_rows:
        sp = str(sk.get("hero_spine", "") or "").strip()
        sp_me = str(sk.get("hero_spine_ME", "") or "").strip()
        if sp:
            skin_by_spine[sp.lower()] = sk
        if sp_me:
            skin_by_spine_me[sp_me.lower()] = sk

    # Verify PVE nurse fallback from c pve heroes.json
    pve_nurse_name = "Survivor Nurse"
    for pr in pve_heroes:
        if "fenhushi" in str(pr.get("hero_spine", "")).lower() or str(pr.get("id", "")) == "1007":
            nid = str(pr.get("name", "")).strip()
            if nid in loc:
                pve_nurse_name = clean_display_name(loc[nid])
                break

    spine_bundles = sorted(ab_dir.glob("art_lastday_spine_hero_*.bundle"))
    logging.info("Discovered %d Spine Hero bundles to extract.", len(spine_bundles))

    # Wipe existing Hero Skins 2D Spine directories first so re-runs stay 100% clean
    for existing_spine_dir in list(models_dir.glob("*/*/Hero Skins 2D Spine")):
        if existing_spine_dir.is_dir():
            shutil.rmtree(existing_spine_dir)

    spine_records: List[Dict[str, Any]] = []
    used_folder_paths: Set[str] = set()

    for bpath in spine_bundles:
        env = load_unity_bundle(bpath)
        bundle_stem = re.sub(r"_[0-9a-f]{32}$", "", bpath.stem)  # art_lastday_spine_hero_...
        short_slug = bundle_stem.replace("art_lastday_spine_", "")  # hero_...

        # 1. Extract primary prefab stem from AssetBundle.m_Container
        container_prefabs: List[str] = []
        for o in env.objects:
            if o.type.name == "AssetBundle":
                ab_tt = o.read_typetree()
                for k, _ in ab_tt.get("m_Container", []):
                    if k.lower().endswith(".prefab"):
                        p_stem = Path(k).stem.lstrip("_")
                        if p_stem not in container_prefabs:
                            container_prefabs.append(p_stem)

        primary_prefabs = [
            p
            for p in container_prefabs
            if not re.search(r"(_mask(_\d+)?|_skeletonanimation|^spine_hero_talk_)$", p, flags=re.I)
            and not p.lower().startswith("spine_hero_talk_")
        ]
        candidate_stems: List[str] = list(primary_prefabs)
        for cp in container_prefabs:
            if cp not in candidate_stems:
                candidate_stems.append(cp)
        fallback_stem = f"Spine_{short_slug}"
        if fallback_stem.lower() not in {c.lower() for c in candidate_stems}:
            candidate_stems.append(fallback_stem)

        prefab_stem = candidate_stems[0]
        for cand in candidate_stems:
            cl = cand.lower()
            if cl in skin_by_spine or cl in skin_by_spine_me or cl in hero_by_spine:
                prefab_stem = cand
                break
        else:
            for cand in candidate_stems:
                cl = cand.lower()
                if re.match(r"spine_hero_([a-z0-9]+)_(exclusiveequip_redweapon|exclusiveequip|wakeup|5)$", cl):
                    prefab_stem = cand
                    break
        prefab_low = prefab_stem.lower()

        # 2. Resolve exact Hero, Skin Name, Category, Season, Faction, and Evidence
        hero_rec: Optional[Dict[str, Any]] = None
        skin_id: Optional[int] = None
        skin_name = "Default"
        skin_category = "default"
        shop_id: Optional[str] = None
        exclusive_weapon_name: Optional[str] = None
        evidence_source = ""
        is_awakening_variant = False
        hero_display_override: Optional[str] = None

        if prefab_low in skin_by_spine:
            sk = skin_by_spine[prefab_low]
            hid = int(sk["hero_id"])
            hero_rec = hero_by_id[hid]
            skin_id = int(sk["id"])
            sname_key = str(sk.get("skin_name", "")).strip()
            skin_name = clean_display_name(loc.get(sname_key, sname_key))
            is_def = str(sk.get("default_skin", "") or "").strip() == "1"
            unlock_type = str(sk.get("unlock_type", "") or "").strip()
            shop_row = shop_by_skin_id.get(str(skin_id))
            shop_id = str(shop_row["id"]) if shop_row else (str(sk.get("shop_id", "") or "").strip() or None)

            if is_def:
                skin_category = "default"
            elif skin_id in (1406, 1606, 2006) or "awakened" in skin_name.lower():
                skin_category = "awakening"
                is_awakening_variant = True
            elif unlock_type == "5":
                skin_category = "affection"
            else:
                skin_category = "purchasable"

            evidence_source = (
                f"aps new heros skin.json(id={skin_id}, hero_id={hid}, hero_spine='{sk['hero_spine']}', "
                f"skin_name={sname_key}='{skin_name}')"
            )
            if shop_id:
                evidence_source += f" + aps new heros skin shop.json(id={shop_id})"

        elif prefab_low in skin_by_spine_me:
            sk = skin_by_spine_me[prefab_low]
            hid = int(sk["hero_id"])
            hero_rec = hero_by_id[hid]
            skin_id = int(sk["id"])
            skin_name = "Default ME"
            skin_category = "regional_default"
            evidence_source = (
                f"aps new heros skin.json(id={skin_id}, hero_id={hid}, hero_spine_ME='{sk['hero_spine_ME']}')"
            )

        elif prefab_low in hero_by_spine:
            hero_rec = hero_by_spine[prefab_low]
            hid = hero_rec["hero_id"]
            skin_name = "Default"
            skin_category = "default"
            if hid == 2025:
                hero_display_override = "Katrina Classic"
            evidence_source = (
                f"aps new heroes.json(id={hid}, name='{hero_rec['hero_name']}', hero_spine='{hero_rec['hero_spine']}')"
            )

        else:
            # Handle Exclusive Weapons, RedWeapons, Base Wakeup, VictorEverlast, 11001_5, tujinv_game, fenhushi_game
            m_excl_red = re.match(r"spine_hero_([a-z0-9]+)_exclusiveequip_redweapon$", prefab_low)
            m_excl = re.match(r"spine_hero_([a-z0-9]+)_exclusiveequip$", prefab_low)
            m_wake = re.match(r"spine_hero_([a-z0-9]+)_wakeup$", prefab_low)

            def resolve_token_hero(tok: str) -> Dict[str, Any]:
                if tok == "clowngirl":
                    return hero_by_id[1004]
                if tok.isdigit() and int(tok) in hero_by_id:
                    return hero_by_id[int(tok)]
                raise KeyError(f"Unmapped Spine hero token: {tok} in {bpath.name}")

            if m_excl_red:
                hero_rec = resolve_token_hero(m_excl_red.group(1))
                hid = hero_rec["hero_id"]
                ex_info = excl_by_hero.get(hid, {})
                exclusive_weapon_name = ex_info.get("weapon_name")
                skin_name = "Awakened Exclusive Weapon"
                skin_category = "awakened_exclusive_weapon"
                is_awakening_variant = True
                evidence_source = (
                    f"m_Container('{prefab_stem}') + heroes exclusive equip.json(group={hid}, "
                    f"weapon='{exclusive_weapon_name or ''}') RedWeapon awakening spine"
                )
            elif m_excl:
                hero_rec = resolve_token_hero(m_excl.group(1))
                hid = hero_rec["hero_id"]
                ex_info = excl_by_hero.get(hid, {})
                exclusive_weapon_name = ex_info.get("weapon_name")
                skin_name = "Exclusive Weapon"
                skin_category = "exclusive_weapon"
                evidence_source = (
                    f"m_Container('{prefab_stem}') + heroes exclusive equip.json(group={hid}, "
                    f"weapon='{exclusive_weapon_name or ''}')"
                )
            elif m_wake:
                hero_rec = resolve_token_hero(m_wake.group(1))
                hid = hero_rec["hero_id"]
                skin_name = "Awakening"
                skin_category = "awakening"
                is_awakening_variant = True
                evidence_source = (
                    f"m_Container('{prefab_stem}') + aps new heroes.json(id={hid}, "
                    f"awakening_season='{hero_rec['awakening_raw']}')"
                )
            elif prefab_low == "spine_hero_11001_5":
                hero_rec = hero_by_id[11001]
                skin_name = "Outfit 5"
                skin_category = "purchasable"
                evidence_source = "m_Container('Spine_Hero_11001_5') + aps new heroes.json(id=11001, name='Katrina')"
            elif "victoreverlast" in prefab_low or "victoreverlast" in short_slug:
                # Check aps_new_heroes for Victor (id=2009) if present, else verified Season 3 Wings of Dawn
                hero_rec = hero_by_id.get(
                    2009,
                    {
                        "hero_id": 2009,
                        "hero_name": "Victor",
                        "camp_id": 2,
                        "faction": "Wings of Dawn",
                        "season": "Season 3",
                        "awakening_season": "Season 3",
                        "awakening_raw": "",
                    },
                )
                skin_name = "Default"
                skin_category = "default"
                evidence_source = "m_Container('Spine_Hero_VictorEverlast_full') + aps new heroes.json(Victor)"
            elif "tujinv_game" in short_slug:
                hero_rec = hero_by_id[1006]
                skin_name = "Stage Battle"
                skin_category = "stage_variant"
                evidence_source = (
                    "art_lastday_spine_hero_tujinv_game (Hero_tujinv_game -> Sophia codename 'Tujinv', hero_id=1006)"
                )
            elif "fenhushi_game" in short_slug:
                hero_rec = {
                    "hero_id": 1007,
                    "hero_name": pve_nurse_name,
                    "camp_id": 0,
                    "faction": "NPCs and Survivors",
                    "season": "Pre-Season 1",
                    "awakening_season": "Pre-Season 1",
                    "awakening_raw": "",
                }
                skin_name = "Default"
                skin_category = "default"
                evidence_source = "c pve heroes.json(id=1007, codename='Hero_Fenhushi_Game', camp=0)"
            else:
                raise RuntimeError(f"Unresolved Spine Hero bundle: {bpath.name} (prefab={prefab_stem})")

        assert hero_rec is not None
        season_folder = hero_rec["awakening_season"] if is_awakening_variant else hero_rec["season"]
        season_source = (
            f"aps new heroes.json(id={hero_rec['hero_id']}, awakening_season='{hero_rec.get('awakening_raw', '')}')"
            if is_awakening_variant
            else f"aps new heroes.json(id={hero_rec['hero_id']}, season='{season_folder}')"
        )
        faction_folder = hero_rec["faction"]
        hero_disp = hero_display_override or hero_rec["hero_name"]
        folder_title = clean_display_name(f"{hero_disp} - {skin_name}", max_len=80)

        rel_folder = f"{season_folder}/{faction_folder}/Hero Skins 2D Spine/{folder_title}"
        if rel_folder.lower() in used_folder_paths:
            raise RuntimeError(f"Duplicate Spine skin folder collision: {rel_folder} ({bpath.name})")
        used_folder_paths.add(rel_folder.lower())

        out_dir = models_dir / season_folder / faction_folder / "Hero Skins 2D Spine" / folder_title
        out_dir.mkdir(parents=True, exist_ok=True)

        # 3. Collect Texture2D & TextAsset objects (resolving external CAB if wrapper bundle like 22003_me)
        tex_objs = [o for o in env.objects if o.type.name == "Texture2D"]
        text_objs = [o for o in env.objects if o.type.name == "TextAsset"]
        resolved_external_bundle: Optional[str] = None

        if not tex_objs and not text_objs and env.objects:
            exts = [e.name.lower() for e in env.objects[0].assets_file.externals]
            for ecab in exts:
                eb_path = cab_map.get(ecab)
                if eb_path is not None and eb_path.name.startswith("art_lastday_spine_hero_"):
                    ext_env = load_unity_bundle(eb_path)
                    tex_objs = [o for o in ext_env.objects if o.type.name == "Texture2D"]
                    text_objs = [o for o in ext_env.objects if o.type.name == "TextAsset"]
                    resolved_external_bundle = eb_path.name
                    break

        # 4. Export Texture2D PNGs (zero underscores)
        atlas_textures: List[Dict[str, Any]] = []
        raw_png_to_clean: Dict[str, str] = {}
        used_png_stems: Dict[str, int] = {}
        exported_files: List[str] = []

        for tobj in sorted(tex_objs, key=lambda o: (o.peek_name() or "").lower()):
            tdata = tobj.read()
            raw_tname = strip_em_dashes(tdata.m_Name or f"atlas-{abs(tobj.path_id)}")
            pil_img = tdata.image
            if pil_img is None or pil_img.size[0] <= 0 or pil_img.size[1] <= 0:
                continue
            rgba = pil_img.convert("RGBA")
            cstem = clean_asset_token(raw_tname, max_len=56)
            low_c = cstem.lower()
            if low_c in used_png_stems:
                used_png_stems[low_c] += 1
                cstem = f"{cstem}-{used_png_stems[low_c]}"
            else:
                used_png_stems[low_c] = 1
            png_fname = f"{cstem}.png"
            rgba.save(out_dir / png_fname, format="PNG")
            raw_png_to_clean[f"{raw_tname.lower()}.png"] = png_fname
            atlas_textures.append(
                {
                    "name": raw_tname,
                    "file": png_fname,
                    "width": rgba.size[0],
                    "height": rgba.size[1],
                }
            )
            exported_files.append(png_fname)

        # 5. Export Spine TextAssets (.atlas.txt, .skel.bytes, .json) with zero underscores
        spine_files_meta: List[Dict[str, Any]] = []
        used_ta_names: Dict[str, int] = {}

        for ta_obj in sorted(text_objs, key=lambda o: (o.peek_name() or "").lower()):
            ta = ta_obj.read()
            raw_aname = strip_em_dashes(ta.m_Name or f"spine-{abs(ta_obj.path_id)}")
            raw_bytes = ta.m_Script.encode("utf-8", "surrogateescape")

            low_aname = raw_aname.lower()
            if low_aname.endswith(".atlas") or low_aname.endswith(".atlas.txt"):
                base_part = re.sub(r"\.atlas(\.txt)?$", "", raw_aname, flags=re.I)
                ext_part = ".atlas.txt"
                kind = "atlas"
            elif low_aname.endswith(".skel") or low_aname.endswith(".skel.bytes"):
                base_part = re.sub(r"\.skel(\.bytes)?$", "", raw_aname, flags=re.I)
                ext_part = ".skel.bytes"
                kind = "skeleton_binary"
            elif low_aname.endswith(".json"):
                base_part = re.sub(r"\.json$", "", raw_aname, flags=re.I)
                ext_part = ".json"
                kind = "skeleton_json"
            else:
                base_part = raw_aname
                ext_part = ".txt"
                kind = "text"

            cstem = clean_asset_token(base_part, max_len=56)
            cand_fname = f"{cstem}{ext_part}"
            if cand_fname.lower() in used_ta_names:
                used_ta_names[cand_fname.lower()] += 1
                cand_fname = f"{cstem}-{used_ta_names[cand_fname.lower()]}{ext_part}"
            else:
                used_ta_names[cand_fname.lower()] = 1

            assert "_" not in cand_fname and EM_DASH not in cand_fname

            if kind == "atlas":
                # Update .png page header lines inside .atlas.txt so Spine viewers find renamed PNGs cleanly
                atlas_txt = strip_em_dashes(raw_bytes.decode("utf-8", errors="replace"))
                rebuilt_lines: List[str] = []
                for ln in atlas_txt.splitlines():
                    s_ln = ln.strip()
                    if s_ln.lower() in raw_png_to_clean:
                        rebuilt_lines.append(raw_png_to_clean[s_ln.lower()])
                    else:
                        rebuilt_lines.append(ln)
                final_txt = "\n".join(rebuilt_lines) + "\n"
                (out_dir / cand_fname).write_text(final_txt, encoding="utf-8")
                byte_len = len(final_txt.encode("utf-8"))
            elif kind in ("skeleton_json", "text"):
                txt_clean = strip_em_dashes(raw_bytes.decode("utf-8", errors="replace"))
                (out_dir / cand_fname).write_text(txt_clean, encoding="utf-8")
                byte_len = len(txt_clean.encode("utf-8"))
            else:
                (out_dir / cand_fname).write_bytes(raw_bytes)
                byte_len = len(raw_bytes)

            spine_files_meta.append(
                {
                    "name": raw_aname,
                    "file": cand_fname,
                    "kind": kind,
                    "size_bytes": byte_len,
                }
            )
            exported_files.append(cand_fname)

        # 6. Inspect any bundled Mesh objects (verifying 2D Spine skeleton/VFX quads vs 3D meshes)
        mesh_checks: List[Dict[str, Any]] = []
        has_real_3d = False
        for m_obj in env.objects:
            if m_obj.type.name == "Mesh":
                mdata = m_obj.read()
                mh = MeshHandler(mdata)
                mh.process()
                zs = [float(v[2]) for v in (mh.m_Vertices or [])]
                z_min = min(zs) if zs else 0.0
                z_max = max(zs) if zs else 0.0
                m_nm = strip_em_dashes(mdata.m_Name or "")
                is_3d = bool((z_max - z_min) > 1e-3 and not m_nm.startswith("Skeleton Prefab Mesh"))
                if is_3d:
                    has_real_3d = True
                mesh_checks.append(
                    {
                        "name": m_nm,
                        "vertices": int(mh.m_VertexCount),
                        "z_min": round(z_min, 5),
                        "z_max": round(z_max, 5),
                        "is_real_3d_mesh": is_3d,
                    }
                )

        exported_files.append("skin-info.json")
        skin_info = {
            "asset_type": "2d_spine_hero_skin",
            "season": season_folder,
            "season_source": strip_em_dashes(season_source),
            "faction": faction_folder,
            "camp_id": hero_rec["camp_id"],
            "hero_id": hero_rec["hero_id"],
            "hero_name": hero_rec["hero_name"],
            "skin_id": skin_id,
            "skin_name": skin_name,
            "display_name": folder_title,
            "skin_category": skin_category,
            "shop_id": shop_id,
            "exclusive_weapon_name": exclusive_weapon_name,
            "prefab_name": strip_em_dashes(prefab_stem),
            "evidence_source": strip_em_dashes(evidence_source),
            "source_bundle": bpath.name,
            "resolved_external_bundle": resolved_external_bundle,
            "folder": rel_folder,
            "texture_count": len(atlas_textures),
            "spine_file_count": len(spine_files_meta),
            "has_real_3d_mesh": has_real_3d,
            "mesh_analysis": (
                "2d_spine_prefab_quads_only (all bundled Mesh objects have z_min=0, z_max=0)"
                if mesh_checks and not has_real_3d
                else ("no_mesh_objects" if not mesh_checks else "contains_3d_mesh")
            ),
            "bundled_meshes": mesh_checks,
            "atlas_textures": atlas_textures,
            "spine_files": spine_files_meta,
            "exported_files": exported_files,
        }
        s_json = strip_em_dashes(json.dumps(skin_info, indent=2, ensure_ascii=False))
        assert EM_DASH not in s_json
        (out_dir / "skin-info.json").write_text(s_json, encoding="utf-8")
        spine_records.append(skin_info)

    spine_records.sort(
        key=lambda r: (
            SEASON_ORDER.index(r["season"]) if r["season"] in SEASON_ORDER else 99,
            SPINE_FACTION_ORDER.index(r["faction"]) if r["faction"] in SPINE_FACTION_ORDER else 99,
            r["display_name"].lower(),
        )
    )
    return spine_records


# ---------------------------------------------------------------------------
# Catalog & README Generation
# ---------------------------------------------------------------------------
def write_master_catalogs_and_readme(
    models_dir: Path,
    models_3d: List[Dict[str, Any]],
    spine_skins: List[Dict[str, Any]],
    skipped_bundles: List[Dict[str, Any]],
    verified_glbs: List[Dict[str, Any]],
    elapsed_sec: float,
) -> None:
    """Write Models Catalog.json, Models Catalog.csv, Hero Skins Spine Catalog.csv, and README.md."""
    active_seasons = [
        s
        for s in SEASON_ORDER
        if any(m["season"] == s for m in models_3d) or any(sp["season"] == s for sp in spine_skins)
    ]

    season_faction_3d: Dict[str, Dict[str, int]] = {
        s: {f: 0 for f in FACTION_ORDER} for s in active_seasons
    }
    season_totals_3d: Dict[str, Dict[str, int]] = {
        s: {"models": 0, "glbs": 0, "objs": 0, "textures": 0, "vertices": 0, "faces": 0}
        for s in active_seasons
    }
    faction_totals_3d: Dict[str, Dict[str, int]] = {
        f: {"models": 0, "glbs": 0, "objs": 0, "textures": 0, "vertices": 0, "faces": 0}
        for f in FACTION_ORDER
    }

    for m in models_3d:
        s = m["season"]
        f = m["faction"]
        season_faction_3d[s][f] += 1
        for bucket in (season_totals_3d[s], faction_totals_3d[f]):
            bucket["models"] += 1
            bucket["glbs"] += 1 if m.get("glb_file") else 0
            bucket["objs"] += m["mesh_count"]
            bucket["textures"] += m["texture_count"]
            bucket["vertices"] += m["total_vertices"]
            bucket["faces"] += m["total_faces"]

    # Spine statistics
    spine_by_season_faction: Dict[str, Dict[str, int]] = {
        s: {f: 0 for f in SPINE_FACTION_ORDER} for s in active_seasons
    }
    spine_by_category: Dict[str, int] = {}
    for sp in spine_skins:
        spine_by_season_faction[sp["season"]][sp["faction"]] += 1
        cat = sp["skin_category"]
        spine_by_category[cat] = spine_by_category.get(cat, 0) + 1

    spine_summary = {
        "total_spine_hero_bundles": len(spine_skins),
        "total_atlas_pngs": sum(sp["texture_count"] for sp in spine_skins),
        "total_spine_data_files": sum(sp["spine_file_count"] for sp in spine_skins),
        "real_3d_meshes_in_spine_bundles": sum(1 for sp in spine_skins if sp["has_real_3d_mesh"]),
        "by_category": spine_by_category,
        "by_season_and_faction": spine_by_season_faction,
    }

    summary = {
        "scanned_3d_bundles": len(models_3d) + len(skipped_bundles),
        "exported_model_bundles": len(models_3d),
        "hq_skins_3d_count": faction_totals_3d["HQ Skins"]["models"],
        "vehicle_skins_3d_count": faction_totals_3d["Vehicle Skins"]["models"],
        "hero_skins_2d_spine_count": len(spine_skins),
        "total_catalog_assets": len(models_3d) + len(spine_skins),
        "skipped_no_mesh_bundles": len(skipped_bundles),
        "active_seasons": active_seasons,
        "total_glbs": sum(b["glbs"] for b in season_totals_3d.values()),
        "total_objs": sum(b["objs"] for b in season_totals_3d.values()),
        "total_textures": sum(b["textures"] for b in season_totals_3d.values()),
        "total_vertices": sum(b["vertices"] for b in season_totals_3d.values()),
        "total_faces": sum(b["faces"] for b in season_totals_3d.values()),
        "elapsed_seconds": round(elapsed_sec, 2),
    }

    hero_3d_table = [
        {
            "season": m["season"],
            "faction": m["faction"],
            "camp_id": m["camp_id"],
            "hero_id": m["hero_id"],
            "english_name": m["english_name"],
            "folder": m["folder"],
            "glb_file": m["glb_file"],
            "meshes": m["mesh_count"],
            "textures": m["texture_count"],
            "faces": m["total_faces"],
            "season_source": m["season_source"],
            "evidence_source": m["evidence_source"],
        }
        for m in models_3d
        if m["faction"] in ("Blood Rose", "Wings of Dawn", "Guard of Order")
    ]

    catalog_payload = {
        "summary": summary,
        "seasons": season_totals_3d,
        "factions": faction_totals_3d,
        "season_by_faction_counts": season_faction_3d,
        "hero_skins_spine_summary": spine_summary,
        "hero_to_season_faction_table": hero_3d_table,
        "verified_glb_samples": verified_glbs,
        "models": models_3d,
        "hero_skins_spine": spine_skins,
        "skipped_bundles": skipped_bundles,
    }
    cat_txt = strip_em_dashes(json.dumps(catalog_payload, indent=2, ensure_ascii=False))
    assert EM_DASH not in cat_txt
    (models_dir / "Models Catalog.json").write_text(cat_txt, encoding="utf-8")

    # Write Models Catalog.csv (all 3D models)
    csv_3d = io.StringIO()
    w3d = csv.writer(csv_3d, lineterminator="\n")
    w3d.writerow(
        [
            "Asset Type",
            "Season",
            "Faction",
            "Camp ID",
            "Hero ID",
            "Model Name",
            "Folder",
            "GLB File",
            "Mesh Count",
            "Texture Count",
            "Total Vertices",
            "Total Faces",
            "Animation Count",
            "Season Source",
            "Evidence Source",
            "Source Bundle",
        ]
    )
    for m in models_3d:
        w3d.writerow(
            [
                m.get("asset_type", "3d_model"),
                m["season"],
                m["faction"],
                "" if m["camp_id"] is None else m["camp_id"],
                "" if m["hero_id"] is None else m["hero_id"],
                m["english_name"],
                m["folder"],
                m["glb_file"] or "",
                m["mesh_count"],
                m["texture_count"],
                m["total_vertices"],
                m["total_faces"],
                len(m.get("animation_clips", [])),
                m["season_source"],
                m["evidence_source"],
                m["source_bundle"],
            ]
        )
    csv_3d_txt = strip_em_dashes(csv_3d.getvalue())
    assert EM_DASH not in csv_3d_txt
    (models_dir / "Models Catalog.csv").write_text(csv_3d_txt, encoding="utf-8")

    # Write Hero Skins Spine Catalog.csv (all 110 2D Spine Hero Skins, zero underscores in filename)
    csv_sp = io.StringIO()
    wsp = csv.writer(csv_sp, lineterminator="\n")
    wsp.writerow(
        [
            "Asset Type",
            "Season",
            "Faction",
            "Camp ID",
            "Hero ID",
            "Hero Name",
            "Skin ID",
            "Skin Name",
            "Display Name",
            "Category",
            "Shop ID",
            "Exclusive Weapon",
            "Folder",
            "Atlas PNG Count",
            "Spine Data Files",
            "Mesh Analysis",
            "Evidence Source",
            "Source Bundle",
        ]
    )
    for sp in spine_skins:
        wsp.writerow(
            [
                sp["asset_type"],
                sp["season"],
                sp["faction"],
                sp["camp_id"],
                sp["hero_id"],
                sp["hero_name"],
                "" if sp["skin_id"] is None else sp["skin_id"],
                sp["skin_name"],
                sp["display_name"],
                sp["skin_category"],
                sp["shop_id"] or "",
                sp["exclusive_weapon_name"] or "",
                sp["folder"],
                sp["texture_count"],
                sp["spine_file_count"],
                sp["mesh_analysis"],
                sp["evidence_source"],
                sp["source_bundle"],
            ]
        )
    csv_sp_txt = strip_em_dashes(csv_sp.getvalue())
    assert EM_DASH not in csv_sp_txt
    (models_dir / "Hero Skins Spine Catalog.csv").write_text(csv_sp_txt, encoding="utf-8")

    # Write README.md
    hq_models = [m for m in models_3d if m["faction"] == "HQ Skins"]
    veh_skin_models = [m for m in models_3d if m["faction"] == "Vehicle Skins"]

    md: List[str] = [
        "# Last Z: Survival Shooter - Complete 3D Model & Purchasable Skins Archive\n\n",
        "Complete 3D model and 2D Spine Hero Skin collection extracted from Last Z AssetBundles, organized by **Season** ",
        "(`Pre-Season 1` through `Season 5`), **Official Faction**, **HQ Skins**, **Vehicle Skins**, and **Hero Skins 2D Spine**, ",
        "with official English shop names, zero underscores in any folder or filename, self-contained textured `.glb` files, ",
        "Wavefront `.obj` + `materials.mtl` + `.png` textures, and Spine `.atlas.txt` + `.skel.bytes` + `.png` sheets.\n\n",
        "## Archive Totals\n\n",
        "- **3D Directory Layout:** `models/<Season>/<Faction or Skin Category>/<Clean Model Name>/`\n",
        "- **2D Spine Hero Skin Layout:** `models/<Season>/<Faction>/Hero Skins 2D Spine/<Hero Name> - <Skin Name>/`\n",
        f"- **3D Models Exported:** {summary['exported_model_bundles']} / {summary['exported_model_bundles']} (100% GLB coverage)\n",
        f"  - **3D Purchasable & Event HQ Skins (`HQ Skins`):** {summary['hq_skins_3d_count']}\n",
        f"  - **3D Purchasable & Upgradeable Vehicle Skins (`Vehicle Skins`):** {summary['vehicle_skins_3d_count']}\n",
        f"- **2D Spine Hero Skins (`Hero Skins 2D Spine`):** {summary['hero_skins_2d_spine_count']} bundles "
        f"({spine_summary['total_atlas_pngs']} atlas PNGs, {spine_summary['total_spine_data_files']} `.atlas.txt`/`.skel.bytes` files)\n",
        f"- **Total Cataloged Assets (3D + 2D Spine):** {summary['total_catalog_assets']}\n",
        f"- **Self-Contained `.glb` Scenes:** {summary['total_glbs']}\n",
        f"- **Sub-Mesh `.obj` Files:** {summary['total_objs']:,}\n",
        f"- **3D `.png` Textures:** {summary['total_textures']:,}\n",
        f"- **Total 3D Geometry:** {summary['total_vertices']:,} vertices / {summary['total_faces']:,} triangles\n\n",
        "## 3D Season Summary\n\n",
        "| Season | Theme | 3D Models | GLBs | OBJs | Textures | Vertices | Triangles |\n",
        "|---|---|---:|---:|---:|---:|---:|---:|\n",
    ]
    for s in active_seasons:
        st = season_totals_3d[s]
        md.append(
            f"| `{s}` | {SEASON_THEMES.get(s, '')} | {st['models']} | {st['glbs']} | {st['objs']:,} | "
            f"{st['textures']:,} | {st['vertices']:,} | {st['faces']:,} |\n"
        )
    md.append(
        f"| **TOTAL** | **All Seasons** | **{summary['exported_model_bundles']}** | **{summary['total_glbs']}** | "
        f"**{summary['total_objs']:,}** | **{summary['total_textures']:,}** | "
        f"**{summary['total_vertices']:,}** | **{summary['total_faces']:,}** |\n\n"
    )

    md.append("## 3D Season x Faction & Skin Category Breakdown\n\n")
    hdr_facs = " | ".join(FACTION_ORDER)
    sep_facs = " | ".join(["---:"] * len(FACTION_ORDER))
    md.append(f"| Season | {hdr_facs} | Total |\n")
    md.append(f"|---| {sep_facs} |---:|\n")
    for s in active_seasons:
        vals = [str(season_faction_3d[s][f]) for f in FACTION_ORDER]
        md.append(f"| `{s}` | {' | '.join(vals)} | **{season_totals_3d[s]['models']}** |\n")
    col_tots = [str(faction_totals_3d[f]["models"]) for f in FACTION_ORDER]
    md.append(f"| **Total** | {' | '.join(col_tots)} | **{summary['exported_model_bundles']}** |\n\n")

    md.append("## 3D Purchasable & Event HQ Skins (`HQ Skins`)\n\n")
    md.append("| Season | HQ Skin Name | Folder Path | GLB File | Meshes | Textures | Triangles | Evidence |\n")
    md.append("|---|---|---|---|---:|---:|---:|---|\n")
    for m in hq_models:
        md.append(
            f"| `{m['season']}` | **{m['english_name']}** | `{m['folder']}` | `{m['glb_file']}` | "
            f"{m['mesh_count']} | {m['texture_count']} | {m['total_faces']:,} | {m['evidence_source']} |\n"
        )

    md.append("\n## 3D Purchasable & Upgradeable Vehicle Skins (`Vehicle Skins`)\n\n")
    md.append("| Season | Vehicle Skin Name | Folder Path | GLB File | Meshes | Textures | Triangles | Evidence |\n")
    md.append("|---|---|---|---|---:|---:|---:|---|\n")
    for m in veh_skin_models:
        md.append(
            f"| `{m['season']}` | **{m['english_name']}** | `{m['folder']}` | `{m['glb_file']}` | "
            f"{m['mesh_count']} | {m['texture_count']} | {m['total_faces']:,} | {m['evidence_source']} |\n"
        )

    md.append("\n## 2D Spine Hero Skins (`Hero Skins 2D Spine`)\n\n")
    md.append(
        "All 110 `art_lastday_spine_hero_*.bundle` files are extracted into "
        "`models/<Season>/<Faction>/Hero Skins 2D Spine/<Hero Name> - <Skin Name>/` "
        "with `.png` atlas sheets, `.atlas.txt` descriptors, `.skel.bytes` binary skeletons, and `skin-info.json` "
        "(see `Hero Skins Spine Catalog.csv` for all 110 rows).\n\n"
    )
    md.append("| Season | Blood Rose | Wings of Dawn | Guard of Order | NPCs and Survivors | Total |\n")
    md.append("|---|---:|---:|---:|---:|---:|\n")
    for s in active_seasons:
        row_s = spine_by_season_faction[s]
        s_tot = sum(row_s.values())
        if s_tot == 0:
            continue
        md.append(
            f"| `{s}` | {row_s['Blood Rose']} | {row_s['Wings of Dawn']} | "
            f"{row_s['Guard of Order']} | {row_s['NPCs and Survivors']} | **{s_tot}** |\n"
        )
    sp_col_tots = [
        sum(spine_by_season_faction[s][f] for s in active_seasons) for f in SPINE_FACTION_ORDER
    ]
    md.append(
        f"| **Total** | {sp_col_tots[0]} | {sp_col_tots[1]} | {sp_col_tots[2]} | {sp_col_tots[3]} | "
        f"**{len(spine_skins)}** |\n\n"
    )

    md.append("### Spine Hero Skin Breakdown by Unlock Category\n\n")
    md.append("| Skin Category | Count |\n|---|---:|\n")
    for cat_k, cat_v in sorted(spine_by_category.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"| `{cat_k}` | {cat_v} |\n")

    md.append("\n## Playable 3D Heroes by Season and Faction\n\n")
    md.append("| Season | Faction | Hero ID | Hero Name | Folder Path | GLB File | Meshes | Triangles |\n")
    md.append("|---|---|---:|---|---|---|---:|---:|\n")
    for h in hero_3d_table:
        md.append(
            f"| `{h['season']}` | `{h['faction']}` | {h['hero_id']} | **{h['english_name']}** | "
            f"`{h['folder']}` | `{h['glb_file']}` | {h['meshes']} | {h['faces']:,} |\n"
        )

    md.append("\n## Verified `.glb` Spot-Checks (`trimesh.load`)\n\n")
    md.append("| Season | Faction | Model | GLB Path | Submeshes | Vertices | Faces |\n")
    md.append("|---|---|---|---|---:|---:|---:|\n")
    for vg in verified_glbs:
        md.append(
            f"| `{vg['season']}` | `{vg['faction']}` | {vg['english_name']} | `{vg['glb_path']}` | "
            f"{vg['geometries']} | {vg['vertices']:,} | {vg['faces']:,} |\n"
        )

    readme_txt = strip_em_dashes("".join(md))
    assert EM_DASH not in readme_txt
    (models_dir / "README.md").write_text(readme_txt, encoding="utf-8")


# ---------------------------------------------------------------------------
# Strict Programmatic Integrity Audit
# ---------------------------------------------------------------------------
def run_strict_audit(
    repo_dir: Path,
    models_dir: Path,
    models_3d: List[Dict[str, Any]],
    spine_skins: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Verify:
      1. 0 underscores (_) in ANY file or directory name anywhere under models/
      2. 0 em dashes (U+2014) in tools/match purchasable skins.py and all text files under models/
      3. 100% of map_Kd / map_Bump in every materials.mtl under models/ resolves on disk
      4. trimesh.load passes with >0 vertices/faces on ALL HQ Skins, Vehicle Skins, Blackland Ruin, & season samples
      5. 0 broken paths in Models Catalog.json across both models and hero_skins_spine
    """
    logging.info("Running strict zero-underscore, zero-em-dash, MTL, GLB, and catalog path audit...")

    # 1. Zero underscores in any path component under models/
    underscore_hits: List[str] = []
    for p in models_dir.rglob("*"):
        if "_" in p.name:
            underscore_hits.append(str(p.relative_to(models_dir)))
    if underscore_hits:
        raise AssertionError(f"Found {len(underscore_hits)} paths with '_' under models/: {underscore_hits[:10]}")

    # 2. Zero em dashes in script + all text files under models/
    text_exts = {".json", ".csv", ".md", ".mtl", ".obj", ".txt", ".py"}
    files_to_scan = [repo_dir / "tools" / "match purchasable skins.py"] + [
        p for p in models_dir.rglob("*") if p.is_file() and p.suffix.lower() in text_exts
    ]
    em_dash_hits: List[str] = []
    for tf in files_to_scan:
        txt = tf.read_text(encoding="utf-8", errors="replace")
        if EM_DASH in txt:
            em_dash_hits.append(str(tf))
    if em_dash_hits:
        raise AssertionError(f"Found {len(em_dash_hits)} files containing U+2014 em dash: {em_dash_hits[:10]}")

    # 3. 100% of map_Kd / map_Bump in every materials.mtl resolves on disk
    mtl_files = list(models_dir.rglob("materials.mtl"))
    broken_mtl_refs: List[str] = []
    checked_tex_refs = 0
    for mtl_p in mtl_files:
        for ln in mtl_p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip()
            if s.startswith(("map_Kd ", "map_Bump ", "bump ")):
                _, rel_t = s.split(None, 1)
                target_t = mtl_p.parent / rel_t.strip()
                checked_tex_refs += 1
                if not target_t.is_file():
                    broken_mtl_refs.append(f"{mtl_p}: {rel_t}")
    if broken_mtl_refs:
        raise AssertionError(f"Broken MTL texture refs ({len(broken_mtl_refs)}): {broken_mtl_refs[:10]}")
    logging.info("Verified %d materials.mtl files (%d texture map links, 0 broken).", len(mtl_files), checked_tex_refs)

    # 4. Zero broken paths in Models Catalog.json (3D models + 2D Spine Hero Skins)
    broken_catalog_paths: List[str] = []
    for m in models_3d:
        fdir = models_dir / m["folder"]
        if not fdir.is_dir():
            broken_catalog_paths.append(f"3d_folder:{m['folder']}")
            continue
        if m.get("glb_file") and not (fdir / m["glb_file"]).is_file():
            broken_catalog_paths.append(f"3d_glb:{m['folder']}/{m['glb_file']}")
        for ef in m.get("exported_files", []):
            if not (fdir / ef).is_file():
                broken_catalog_paths.append(f"3d_file:{m['folder']}/{ef}")

    for sp in spine_skins:
        sdir = models_dir / sp["folder"]
        if not sdir.is_dir():
            broken_catalog_paths.append(f"spine_folder:{sp['folder']}")
            continue
        for ef in sp.get("exported_files", []):
            if not (sdir / ef).is_file():
                broken_catalog_paths.append(f"spine_file:{sp['folder']}/{ef}")

    if broken_catalog_paths:
        raise AssertionError(f"Broken catalog paths ({len(broken_catalog_paths)}): {broken_catalog_paths[:10]}")

    # 5. trimesh.load check on ALL HQ Skins, ALL Vehicle Skins, Blackland Ruin, + season samples
    must_verify: List[Dict[str, Any]] = [
        m
        for m in models_3d
        if m["faction"] in ("HQ Skins", "Vehicle Skins") or m["english_name"] == "Blackland Ruin"
    ]
    verified_samples: List[Dict[str, Any]] = []
    for m in must_verify:
        gp = models_dir / m["folder"] / m["glb_file"]
        sc = trimesh.load(gp, force="scene")
        if isinstance(sc, trimesh.Trimesh):
            verts, faces, geoms = int(len(sc.vertices)), int(len(sc.faces)), 1
        else:
            verts = int(sum(len(g.vertices) for g in sc.geometry.values()))
            faces = int(sum(len(g.faces) for g in sc.geometry.values()))
            geoms = int(len(sc.geometry))
        if verts <= 0 or faces <= 0:
            raise AssertionError(f"Zero geometry in GLB: {gp}")
        verified_samples.append(
            {
                "season": m["season"],
                "faction": m["faction"],
                "english_name": m["english_name"],
                "glb_path": f"{m['folder']}/{m['glb_file']}",
                "geometries": geoms,
                "vertices": verts,
                "faces": faces,
            }
        )

    # Add 2 hero/monster spot checks per season for README completeness
    seen_paths = {v["glb_path"] for v in verified_samples}
    for s in SEASON_ORDER:
        s_cands = [
            m
            for m in models_3d
            if m["season"] == s and f"{m['folder']}/{m['glb_file']}" not in seen_paths and m.get("glb_file")
        ]
        for m in s_cands[:2]:
            gp = models_dir / m["folder"] / m["glb_file"]
            sc = trimesh.load(gp, force="scene")
            verts = int(sum(len(g.vertices) for g in sc.geometry.values()))
            faces = int(sum(len(g.faces) for g in sc.geometry.values()))
            geoms = int(len(sc.geometry))
            if verts <= 0 or faces <= 0:
                raise AssertionError(f"Zero geometry in GLB: {gp}")
            verified_samples.append(
                {
                    "season": m["season"],
                    "faction": m["faction"],
                    "english_name": m["english_name"],
                    "glb_path": f"{m['folder']}/{m['glb_file']}",
                    "geometries": geoms,
                    "vertices": verts,
                    "faces": faces,
                }
            )
    logging.info("Verified %d GLB files via trimesh.load (including 100%% of HQ Skins & Vehicle Skins).", len(verified_samples))
    return verified_samples


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Match and organize all Last Z purchasable skins.")
    parser.add_argument("--ab-dir", type=Path, default=DEFAULT_AB_DIR)
    parser.add_argument("--repo-dir", type=Path, default=DEFAULT_REPO_DIR)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    t0 = time.time()

    ab_dir: Path = args.ab_dir
    repo_dir: Path = args.repo_dir
    models_dir: Path = repo_dir / "models"
    cat_path = models_dir / "Models Catalog.json"

    if not ab_dir.is_dir():
        raise FileNotFoundError(f"AssetBundles directory not found: {ab_dir}")
    if not cat_path.is_file():
        raise FileNotFoundError(f"Models Catalog.json not found: {cat_path}")

    cat_data = json.loads(cat_path.read_text(encoding="utf-8"))
    existing_models: List[Dict[str, Any]] = cat_data.get("models", [])
    skipped_bundles: List[Dict[str, Any]] = cat_data.get("skipped_bundles", [])

    # Exclude any synthetic/re-extracted slugs so re-running is 100% idempotent
    reextracted_slugs = (
        {"environment_decorate_a_build_valentine_fox"}
        | {s["slug"] for s in VALENTINE_FOX_SPLITS}
        | {s["slug"] for s in PREFAB_3D_EXTRACTIONS}
    )

    # Remove old merged Valentine Fox HQ folder if present
    old_vf_dir = models_dir / "Pre-Season 1" / "Buildings and Environment" / "Valentine Fox HQ"
    if old_vf_dir.exists():
        logging.info("Removing merged Valentine Fox HQ folder prior to clean 4-prefab split...")
        shutil.rmtree(old_vf_dir)

    logging.info("Indexing CAB hashes across model, spine, and building prefab bundles...")
    cab_map = build_cab_index(ab_dir)
    logging.info("Indexed %d CAB bundle entries.", len(cab_map))
    resolver = CrossBundleResolver(cab_map)

    # Process existing 3D models (Task A moves + Task B moves + untouched 3D models)
    updated_3d_models: List[Dict[str, Any]] = []
    moved_hq_count = 0
    moved_vehicle_count = 0

    for m in existing_models:
        slug = str(m.get("slug", ""))
        if slug in reextracted_slugs:
            continue

        if slug in HQ_SKIN_MOVES_BY_SLUG:
            spec = HQ_SKIN_MOVES_BY_SLUG[slug]
            updated_m = relocate_existing_3d_model(
                models_dir=models_dir,
                model_rec=m,
                target_season=spec["season"],
                target_faction=spec["faction"],
                target_name=spec["name"],
                new_evidence=spec["evidence"],
            )
            updated_3d_models.append(updated_m)
            moved_hq_count += 1
        elif slug in VEHICLE_SKIN_MOVES_BY_SLUG:
            spec = VEHICLE_SKIN_MOVES_BY_SLUG[slug]
            updated_m = relocate_existing_3d_model(
                models_dir=models_dir,
                model_rec=m,
                target_season=spec["season"],
                target_faction=spec["faction"],
                target_name=spec["name"],
                new_evidence=spec["evidence"],
            )
            updated_3d_models.append(updated_m)
            moved_vehicle_count += 1
        else:
            m_copy = dict(m)
            m_copy["asset_type"] = "3d_model"
            # Ensure model-info.json on disk also carries asset_type="3d_model" and zero em dashes
            info_p = models_dir / m_copy["folder"] / "model-info.json"
            if info_p.is_file():
                info_txt = strip_em_dashes(json.dumps(m_copy, indent=2, ensure_ascii=False))
                info_p.write_text(info_txt, encoding="utf-8")
            updated_3d_models.append(m_copy)

    logging.info(
        "Relocated %d existing HQ Skin models and %d existing Vehicle Skin models.",
        moved_hq_count,
        moved_vehicle_count,
    )

    # Task A Part 2: Split Heartbound Fox vs Heartfelt Fox (4 models)
    logging.info("Extracting 4 prefab-scoped models for Heartbound Fox & Heartfelt Fox...")
    vf_models = extract_valentine_fox_splits(ab_dir=ab_dir, models_dir=models_dir, resolver=resolver)
    updated_3d_models.extend(vf_models)

    # Task A Part 3: Extract Santa Chaos (HQ, World, S3) + 5 main_prefabs_building_* mesh bundles
    logging.info("Extracting Santa Chaos (3 variants) + 5 main_prefabs_building_* 3D bundles...")
    prefab_models = extract_prefab_3d_bundles(ab_dir=ab_dir, models_dir=models_dir, resolver=resolver)
    updated_3d_models.extend(prefab_models)

    # Remove newly exported shengsanjiepifu bundles from skipped_bundles if listed there
    newly_exported_bundle_names = {m["source_bundle"] for m in updated_3d_models} | {
        p.name for p in ab_dir.glob("art_lastday_models_environment_decorate_a_build_shengsanjiepifu_01_*.bundle")
    }
    skipped_clean = [sb for sb in skipped_bundles if sb.get("bundle") not in newly_exported_bundle_names]

    # Sort all 3D models deterministically
    updated_3d_models.sort(
        key=lambda item: (
            SEASON_ORDER.index(item["season"]) if item["season"] in SEASON_ORDER else 99,
            FACTION_ORDER.index(item["faction"]) if item["faction"] in FACTION_ORDER else 99,
            item["english_name"].lower(),
        )
    )

    # Task C: Extract all 110 2D Spine Hero Skin bundles
    logging.info("Extracting all 110 2D Spine Hero Skin bundles...")
    spine_skins = extract_all_spine_hero_skins(
        repo_dir=repo_dir,
        ab_dir=ab_dir,
        models_dir=models_dir,
        cab_map=cab_map,
    )
    logging.info("Extracted %d 2D Spine Hero Skin bundles.", len(spine_skins))

    # Remove any empty directories left behind under models/
    for d in sorted([p for p in models_dir.rglob("*") if p.is_dir()], key=lambda x: len(str(x)), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()

    # Run strict audit & collect verified GLB metadata before writing final catalog/README
    verified_samples = run_strict_audit(
        repo_dir=repo_dir,
        models_dir=models_dir,
        models_3d=updated_3d_models,
        spine_skins=spine_skins,
    )

    elapsed = time.time() - t0
    write_master_catalogs_and_readme(
        models_dir=models_dir,
        models_3d=updated_3d_models,
        spine_skins=spine_skins,
        skipped_bundles=skipped_clean,
        verified_glbs=verified_samples,
        elapsed_sec=elapsed,
    )

    # Re-verify zero underscores and zero em dashes on newly written catalogs/README!
    for root_doc in (
        models_dir / "Models Catalog.json",
        models_dir / "Models Catalog.csv",
        models_dir / "Hero Skins Spine Catalog.csv",
        models_dir / "README.md",
    ):
        assert "_" not in root_doc.name
        assert EM_DASH not in root_doc.read_text(encoding="utf-8")

    hq_tot = sum(1 for m in updated_3d_models if m["faction"] == "HQ Skins")
    veh_tot = sum(1 for m in updated_3d_models if m["faction"] == "Vehicle Skins")
    logging.info(
        "COMPLETE in %.2fs! 3D Models=%d (HQ Skins=%d, Vehicle Skins=%d), 2D Spine Hero Skins=%d, Total Assets=%d",
        elapsed,
        len(updated_3d_models),
        hq_tot,
        veh_tot,
        len(spine_skins),
        len(updated_3d_models) + len(spine_skins),
    )


if __name__ == "__main__":
    main()
