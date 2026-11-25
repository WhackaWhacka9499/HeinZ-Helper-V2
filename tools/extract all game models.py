#!/usr/bin/env python3
"""
Extract all 3D game models from Last Z AssetBundles into faction-organized folders
with English names, PNG textures (including unpacked DXT5nm normal maps),
wired Wavefront OBJ + MTL files, self-contained textured GLB models, per-model
metadata (model info.json), and master catalog reports (JSON, CSV, README.md).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import io
import json
import logging
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image
import trimesh
from trimesh.visual import ColorVisuals, TextureVisuals
from trimesh.visual.material import PBRMaterial
import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler


DEFAULT_AB_DIR = Path(
    r"%LOCALAPPDATA%/Last Z\Game\Survival_Data\StreamingAssets\AssetBundles"
)
DEFAULT_REPO_DIR = Path(r".")

CAMP_TO_FACTION: Dict[int, str] = {
    1: "Blood_Rose",
    2: "Wings_of_Dawn",
    3: "Guard_of_Order",
}

FACTION_ORDER: List[str] = [
    "Blood_Rose",
    "Wings_of_Dawn",
    "Guard_of_Order",
    "Zombies_and_Monsters",
    "Blood_Hand_and_Raiders",
    "Troops_and_Soldiers",
    "Vehicles_and_Tanks",
    "NPCs_and_Survivors",
    "Weapons",
    "Buildings_and_Environment",
]

FACTION_DESCRIPTIONS: Dict[str, str] = {
    "Blood_Rose": "Official Playable Faction (camp = 1, HeroCamp.MAFIA, loc 158002)",
    "Wings_of_Dawn": "Official Playable Faction (camp = 2, HeroCamp.UNION, loc 158003)",
    "Guard_of_Order": "Official Playable Faction (camp = 3, HeroCamp.ZELOT, loc 158005)",
    "Zombies_and_Monsters": "Infected zombies, mutants, bosses, Overlord PVE beasts, and seasonal monsters",
    "Blood_Hand_and_Raiders": "Blood Hand gang bosses, elites, stooges, and wasteland bandits/raiders",
    "Troops_and_Soldiers": "Base military units, squad soldiers, tactical operators, and PVE troopers",
    "Vehicles_and_Tanks": "Armored vehicles, battle tanks, missile launchers, trucks, and mounts",
    "NPCs_and_Survivors": "Camp 0 neutral survivors, shelter residents, story NPCs, and citizens",
    "Weapons": "Standalone 3D hero weapons, firearms, melee weapons, turrets, and ordnance",
    "Buildings_and_Environment": "Headquarters, city/world buildings, Overlord world structures, obstacles, and props",
}

# Pinyin / asset token glossary used to enrich English display names when XML localization
# does not attach a direct row to an environment, vehicle, monster, or weapon asset slug.
PINYIN_GLOSSARY: List[Tuple[str, str]] = [
    ("daodanche_ex", "Destroyer-EX Missile Vehicle"),
    ("daodanche", "Destroyer Missile Vehicle"),
    ("huojianche", "Destroyer Rocket Vehicle"),
    ("zhuangjiache", "Cheetah Armored Vehicle"),
    ("dajiaoche", "Conqueror Bigfoot Truck"),
    ("tank_killer", "Anti-Tank Barricade"),
    ("tanke", "Hercules Battle Tank"),
    ("xingjunche", "Troop March Truck"),
    ("jijieche", "Alliance Rally Truck"),
    ("yunbingche", "Troop Carrier Truck"),
    ("xueqiaoche", "Arctic Snowmobile Sled"),
    ("changmaoche", "Spear War Chariot"),
    ("guanche", "Fuel Tanker Truck"),
    ("huoche", "Armored Train"),
    ("kache", "Supply Cargo Truck"),
    ("motuo", "Combat Motorcycle"),
    ("dinotruck", "Dinosaur Transport Truck"),
    ("bawanglong", "Tyrannosaurus Rex"),
    ("sanjiaolong", "Triceratops"),
    ("xunmenglong", "Velociraptor"),
    ("jianlong", "Stegosaurus"),
    ("jialong", "Ankylosaurus"),
    ("yichilong", "Yi Qi Wyvern"),
    ("yilong", "Pterosaur"),
    ("jilong", "棘龙 Spinosaurus".encode("ascii", "ignore").decode("ascii").strip() or "Spinosaurus"),
    ("konglong", "Dinosaur"),
    ("snowkingkong", " Frost Gorilla Boss".strip()),
    ("snowmonster", "Yeti Snow Monster Boss"),
    ("snowleopard", "Snow Leopard"),
    ("lceworm", "Ice Worm Boss"),
    ("hongmo", "Crimson Demon"),
    ("jisi", "Dark Cult Priest"),
    ("biochemistry_boss", "Biochemical Tyrant Boss"),
    ("blackfat", "Boomer Mutant Boss"),
    ("fatcop", "Infected Riot Officer"),
    ("policeshild", "Infected Shield Officer"),
    ("hugehand_zombie", "Mutant Claw Zombie"),
    ("greenvenom", "Venom Spitter Zombie"),
    ("feitu", "Wasteland Raider"),
    ("huairen", "Outlaw Bandit"),
    ("gangster_snake", "Blood Hand Viper Gangster"),
    ("bloodhand_boss", "Blood Hand Boss"),
    ("bloodhand_elite", "Blood Hand Elite"),
    ("bloodhand_stooge", "Blood Hand Enforcer"),
    ("jiatelin", "Gatling Minigun"),
    ("huojiantong", "Rocket Launcher RPG"),
    ("penhuoqiang", "Heavy Flamethrower"),
    ("penhuoqi", "Flamethrower"),
    ("diancipao", "EMP Rail Cannon"),
    ("dianciqiang", "EMP Pulse Rifle"),
    ("langyabang", "Spiked War Club"),
    ("sawfrisbee", "Sawblade Launcher"),
    ("electricsaw", "Chainsaw"),
    ("baoxiang", "Treasure Strongbox"),
    ("hongyoutong", "Explosive Red Fuel Barrel"),
    ("zawu", "Barricade Props"),
    ("daben", "Headquarters"),
    ("cheku", "Vehicle Garage"),
    ("canting", "Survivor Canteen"),
    ("gaojiaqiao", "Highway Overpass"),
    ("chengwaidalou", "Outskirts Highrise Ruin"),
    ("chengwaidiangan", "Utility Power Poles"),
    ("chengwailumian", "Outskirts Asphalt Road"),
    ("zhanshicheku", "Vehicle Showroom Hangar"),
    ("trainstation", "Train Station"),
    ("dragoncastle", "Dragon Castle"),
    ("beer_cat", "Oktoberfest Beer Cat Statue"),
    ("overlord_dinasour", "Overlord Mecha-Zilla"),
]


def strip_em_dashes(text: str) -> str:
    """Guarantee zero em dashes (U+2014) in any string written to disk."""
    if not text:
        return ""
    return text.replace("\u2014", " - ").replace("&" + "mdash;", " - ")


def clean_loc_string(raw: str) -> str:
    """Strip Unity rich-text tags and em dashes from a localized string."""
    s = re.sub(r"<[^>]+>", "", str(raw or ""))
    s = strip_em_dashes(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def safe_filename(name: str, max_len: int = 56) -> str:
    """Convert an arbitrary string into a clean Windows-safe path token."""
    s = strip_em_dashes(str(name or "")).strip()
    # Transliterate common accented characters cleanly
    s = (
        s.replace("ú", "u")
        .replace("Ú", "U")
        .replace("é", "e")
        .replace("á", "a")
        .replace("í", "i")
        .replace("ó", "o")
    )
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)
    if not s:
        s = "Unnamed"
    if len(s) > max_len:
        s = s[:max_len].rstrip("_")
    return s


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
    """Load and merge all English strings from localization en.json and english-dialog.txt."""
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
    """Parse an XML-converted JSON table supporting both dict and list row schemas."""
    p = xml_dir / table_name
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    cols = data.get("columns", [])
    rows_raw = data.get("rows", [])
    rows_iter = list(rows_raw.values()) if isinstance(rows_raw, dict) else rows_raw
    result: List[Dict[str, Any]] = []
    for r in rows_iter:
        if isinstance(r, dict):
            result.append(r)
        elif isinstance(r, list):
            result.append(dict(zip(cols, r)))
    return result


def bundle_slug(bundle_name: str) -> str:
    """Strip prefix and trailing 32-hex hash from an AssetBundle filename."""
    stem = bundle_name[:-7] if bundle_name.endswith(".bundle") else bundle_name
    stem = re.sub(r"_[0-9a-f]{32}$", "", stem)
    for pref in ("art_lastday_models_", "art_barrel_models_"):
        if stem.startswith(pref):
            stem = stem[len(pref) :]
            break
    return stem


def norm_key(s: str) -> str:
    """Lowercase alphanumeric key for exact codename matching."""
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


class GameMetadataResolver:
    """Evidence-based resolver linking Last Z 3D bundles to English names and official factions."""

    def __init__(self, repo_dir: Path, ab_dir: Path) -> None:
        self.repo_dir = repo_dir
        self.ab_dir = ab_dir
        self.xml_dir = repo_dir / "megamind" / "raw" / "xml tables"
        self.loc = load_localization(repo_dir)

        # Verify official HeroCamp enum values from enums complete.json
        self.camp_enum_names: Dict[int, str] = {1: "MAFIA", 2: "UNION", 3: "ZELOT"}
        enums_path = repo_dir / "megamind" / "raw" / "enums complete.json"
        if enums_path.exists():
            enums_raw = enums_path.read_text(encoding="utf-8", errors="replace")
            if "HeroCamp" in enums_raw:
                logging.info(
                    "Verified HeroCamp enum in enums complete.json and faction names: "
                    "1=%s (%s), 2=%s (%s), 3=%s (%s)",
                    self.loc.get("158002", "Blood Rose"),
                    CAMP_TO_FACTION[1],
                    self.loc.get("158003", "Wings of Dawn"),
                    CAMP_TO_FACTION[2],
                    self.loc.get("158005", "Guard of Order"),
                    CAMP_TO_FACTION[3],
                )

        self.hero_codename_map: Dict[str, Dict[str, Any]] = {}
        self.building_model_map: Dict[str, str] = {}
        self.vehicle_model_map: Dict[str, str] = {}
        self.monster_model_map: Dict[str, str] = {}
        self.npc_model_map: Dict[str, str] = {}
        self.prefab_cab_links: Dict[str, List[str]] = {}

        self._parse_all_tables()
        self._inspect_prefab_bundles()

    def _parse_all_tables(self) -> None:
        heroes_a = load_xml_table(self.xml_dir, "aps new heroes.json")
        heroes_b = load_xml_table(self.xml_dir, "aps new heroes client B.json")
        skins = load_xml_table(self.xml_dir, "aps new heros skin.json")
        lw_app = load_xml_table(self.xml_dir, "lw hero appearance.json")
        lw_skills = load_xml_table(self.xml_dir, "lw hero skill.json")
        lw_bullets = load_xml_table(self.xml_dir, "lw bullet.json")
        c_pve_heroes = load_xml_table(self.xml_dir, "c pve heroes.json")
        armies = (
            load_xml_table(self.xml_dir, "army.json")
            + load_xml_table(self.xml_dir, "army b.json")
            + load_xml_table(self.xml_dir, "army c.json")
        )
        car_show = load_xml_table(self.xml_dir, "car show.json")
        car_barrel = load_xml_table(self.xml_dir, "car show barrel.json")
        overlord_show = load_xml_table(self.xml_dir, "overlord show.json")
        aps_monster = load_xml_table(self.xml_dir, "APS monster.json")
        pve_zombie = load_xml_table(self.xml_dir, "aps pve zombie.json")
        barrel_monster = load_xml_table(self.xml_dir, "barrel monster base.json")
        npc_base = load_xml_table(self.xml_dir, "npc base.json")
        buildings = (
            load_xml_table(self.xml_dir, "building.json")
            + load_xml_table(self.xml_dir, "dragon building.json")
            + load_xml_table(self.xml_dir, "volcano building.json")
            + load_xml_table(self.xml_dir, "food festival building.json")
        )
        logging.info(
            "Loaded XML rows: heroes=%d+%d, skins=%d, appearances=%d, armies=%d, monsters=%d, buildings=%d",
            len(heroes_a),
            len(heroes_b),
            len(skins),
            len(lw_app),
            len(armies),
            len(aps_monster),
            len(buildings),
        )

        # Map appearance ID -> appearance row
        app_by_id: Dict[str, Dict[str, Any]] = {str(r.get("id", "")): r for r in lw_app}

        # Extract playable hero records, scoring official voiced Spine heroes (id < 900000)
        # above barrel stage template rows (900xxx/910xxx).
        app_best_hero: Dict[str, Tuple[int, Dict[str, Any]]] = {}
        hero_by_id: Dict[str, Dict[str, Any]] = {}

        for r in heroes_a + heroes_b:
            hid_str = str(r.get("id", "")).strip()
            if not hid_str.isdigit():
                continue
            hid = int(hid_str)
            camp_str = str(r.get("camp", "0") or "0").strip()
            camp = int(camp_str) if camp_str.lstrip("-").isdigit() else 0
            name_id = str(r.get("name", "")).strip()
            name_en = self.loc.get(name_id, name_id)
            spine = str(r.get("hero_spine", "") or "").strip()
            app = str(r.get("appearance", "") or "").strip()
            app_aw = str(r.get("appearance_awakening", "") or "").strip()
            skill_barrel = str(r.get("skill_barrel", "") or "").strip()

            # Score real playable heroes highest
            score = 0
            if camp in (1, 2, 3):
                score += 100
            if spine.startswith("Spine_Hero_"):
                score += 200
            if hid < 100000:
                score += 150
            if int(str(r.get("rarity", "0") or "0") or 0) <= 3:
                score += 20

            rec = {
                "hero_id": hid,
                "english_name": name_en,
                "camp_id": camp,
                "faction": CAMP_TO_FACTION.get(camp, "NPCs_and_Survivors"),
                "spine": spine,
                "appearance": app,
                "appearance_awakening": app_aw,
                "skill_barrel": skill_barrel,
                "prefab_high": str(r.get("prefab_high", "") or ""),
                "prefab_low": str(r.get("prefab_low", "") or ""),
            }
            if hid_str not in hero_by_id or score > hero_by_id[hid_str].get("_score", -1):
                rec["_score"] = score
                hero_by_id[hid_str] = rec

            for is_aw, aid in [(False, app), (True, app_aw)]:
                if not aid or aid == "0" or aid.startswith(("300", "400", "500", "600")):
                    # Note: 3100090, 3100120, 3100260 are 7-digit hero appearances!
                    if not (len(aid) == 7 and aid.startswith("3100")):
                        continue
                adj_score = score - (10 if is_aw else 0)
                prev = app_best_hero.get(aid)
                if prev is None or adj_score > prev[0]:
                    h_copy = dict(rec)
                    h_copy["is_awakened"] = is_aw
                    app_best_hero[aid] = (adj_score, h_copy)

        # Link appearance model paths & 2D folder paths to exact codenames
        for aid, (_, hrec) in sorted(app_best_hero.items(), key=lambda kv: (1 if kv[1][1].get("is_awakened") else 0)):
            arow = app_by_id.get(aid)
            if not arow:
                continue
            candidates: List[str] = []
            m2d = str(arow.get("simple_model2D_path", "") or "")
            if "/Soldier/" in m2d and not hrec.get("is_awakened"):
                seg = m2d.split("/Soldier/", 1)[1].split("/", 1)[0]
                candidates.append(seg)
            for path_col in ("model_path", "simple_model_path"):
                mp = str(arow.get(path_col, "") or "")
                if mp.endswith(".prefab"):
                    pstem = Path(mp).stem
                    # Strip common suffixes used in Barrel/SimpleHero prefabs
                    pclean = re.sub(r"(_game02|_game|_low_1|_low|_show)$", "", pstem, flags=re.I)
                    candidates.append(pclean)
                    candidates.append(pstem)

            disp_name = hrec["english_name"]
            if hrec.get("is_awakened"):
                disp_name = f"{disp_name} Awakened"
            elif hrec["hero_id"] == 11001 and disp_name == "Katrina":
                disp_name = "Katrina Tactical"

            for cand in candidates:
                nk = norm_key(cand)
                if not nk:
                    continue
                # Register both with and without leading 'hero'
                keys_to_set = {nk}
                if nk.startswith("hero"):
                    keys_to_set.add(nk[4:])
                else:
                    keys_to_set.add("hero" + nk)
                for k in keys_to_set:
                    if k not in self.hero_codename_map or hrec["_score"] >= self.hero_codename_map[k]["_score"]:
                        self.hero_codename_map[k] = {
                            "hero_id": hrec["hero_id"],
                            "english_name": disp_name,
                            "base_hero_name": hrec["english_name"],
                            "camp_id": hrec["camp_id"],
                            "faction": hrec["faction"],
                            "evidence_source": (
                                f"aps_new_heroes(id={hrec['hero_id']}, camp={hrec['camp_id']}) "
                                f"-> lw_hero_appearance(id={aid}, prefab={Path(str(arow.get('model_path',''))).name})"
                            ),
                            "_score": hrec["_score"],
                        }

        # Link hero skill companion summons via skill_barrel -> lw_hero_skill -> lw_bullet
        skill_group_to_hero: Dict[str, Dict[str, Any]] = {}
        for hrec in hero_by_id.values():
            if hrec["camp_id"] in (1, 2, 3) and hrec["skill_barrel"]:
                for sg in hrec["skill_barrel"].split(";"):
                    sg = sg.strip()
                    if sg:
                        skill_group_to_hero[sg] = hrec

        bullet_to_hero: Dict[str, Dict[str, Any]] = {}
        for srow in lw_skills:
            grp = str(srow.get("group", "")).strip()
            bul = str(srow.get("bullet", "")).strip()
            if grp in skill_group_to_hero and bul:
                bullet_to_hero[bul] = skill_group_to_hero[grp]

        for brow in lw_bullets:
            bid = str(brow.get("id", "")).strip()
            if bid in bullet_to_hero:
                bjson = json.dumps(brow).lower()
                owner = bullet_to_hero[bid]
                if "hero_bear" in bjson or "/bear" in bjson:
                    self.hero_codename_map["herobear"] = {
                        "hero_id": owner["hero_id"],
                        "english_name": f"{owner['english_name']} Bear Companion",
                        "base_hero_name": owner["english_name"],
                        "camp_id": owner["camp_id"],
                        "faction": owner["faction"],
                        "evidence_source": (
                            f"aps_new_heroes(id={owner['hero_id']}, {owner['english_name']}, camp={owner['camp_id']}) "
                            f"-> lw_hero_skill/lw_bullet(id={bid}, Hero_Bear summon)"
                        ),
                        "_score": 500,
                    }
                if "hurse_stuff" in bjson or "hurse" in bjson:
                    self.hero_codename_map["hursestuff"] = {
                        "hero_id": owner["hero_id"],
                        "english_name": f"{owner['english_name']} Horse Stampede",
                        "base_hero_name": owner["english_name"],
                        "camp_id": owner["camp_id"],
                        "faction": owner["faction"],
                        "evidence_source": (
                            f"aps_new_heroes(id={owner['hero_id']}, {owner['english_name']}, camp={owner['camp_id']}) "
                            f"-> lw_hero_skill/lw_bullet(id={bid}, Hurse_Stuff summon)"
                        ),
                        "_score": 500,
                    }

        # NPCs and neutral camp 0 characters from npc_base + lw_hero_appearance + c_pve_heroes
        for nrow in npc_base:
            nid = str(nrow.get("name", "")).strip()
            nen = self.loc.get(nid, "") if nid else ""
            for mcol in ("low_model", "high_model"):
                mval = str(nrow.get(mcol, "") or "").strip()
                if mval:
                    if "rebecca" in mval.lower():
                        self.npc_model_map["rebecca"] = nen or "Rebecca Survivor NPC"
                    elif nen:
                        self.npc_model_map[norm_key(mval)] = nen
        for crow in c_pve_heroes:
            pl = str(crow.get("prefab_low", "") or "").strip()
            if "fenhushi" in pl.lower():
                self.npc_model_map["herofenhushi"] = "Survivor Nurse"

        # Vehicles from car show.json and car show barrel.json
        for vrow in car_show:
            vn = self.loc.get(str(vrow.get("name", "")).strip(), "")
            if not vn:
                continue
            for col in ("model", "model_point"):
                for part in str(vrow.get(col, "") or "").split("|"):
                    if "/Decorate/" in part:
                        folder_tok = part.split("/Decorate/", 1)[1].split("/", 1)[0]
                        self.vehicle_model_map[norm_key(folder_tok)] = vn
        for cbrow in car_barrel:
            cbid = str(cbrow.get("id", "")).strip()
            h_veh = hero_by_id.get(cbid)
            hdm = str(cbrow.get("HD_model", "") or "")
            if h_veh and "/Decorate/" in hdm:
                folder_tok = hdm.split("/Decorate/", 1)[1].split("/", 1)[0]
                if h_veh["english_name"] and not h_veh["english_name"].isdigit():
                    self.vehicle_model_map.setdefault(norm_key(folder_tok), h_veh["english_name"])

        # Buildings from building.json + seasonal building tables
        for brow in buildings:
            bn = self.loc.get(str(brow.get("name", "")).strip(), "")
            if not bn or bn.isdigit():
                continue
            for col in ("model", "model_world", "s2_model"):
                mval = str(brow.get(col, "") or "").strip()
                if mval and not mval.startswith("table:"):
                    self.building_model_map.setdefault(norm_key(mval), bn)

        # Monsters from APS_monster + aps_pve_zombie + barrel_monster_base + overlord_show
        for mrow in aps_monster:
            mn = self.loc.get(str(mrow.get("name", "")).strip(), "")
            if not mn or mn.isdigit():
                continue
            for col in ("model_name", "model_name_new"):
                mval = str(mrow.get(col, "") or "").strip()
                if mval and not mval.startswith("table:"):
                    self.monster_model_map.setdefault(norm_key(mval), mn)
        for zrow in pve_zombie:
            mval = str(zrow.get("ModelName", "") or "").strip()
            if mval:
                self.monster_model_map.setdefault(norm_key(mval), mval.replace("_", " "))
        for bmrow in barrel_monster:
            asset = str(bmrow.get("asset", "") or "").strip()
            if asset.endswith(".prefab"):
                astem = Path(asset).stem
                self.monster_model_map.setdefault(norm_key(astem), astem.replace("_", " "))
        for orow in overlord_show:
            dn = self.loc.get(str(orow.get("default_name", "")).strip(), "") or "Overlord Mecha-Zilla"
            rank = str(orow.get("rank", "")).strip()
            for col in ("low_model", "middle_model", "high_model", "world_model"):
                mp = str(orow.get(col, "") or "").strip()
                if mp.endswith(".prefab"):
                    pstem = Path(mp).stem
                    self.monster_model_map[norm_key(pstem)] = f"{dn} Stage {rank}".strip()

    def _inspect_prefab_bundles(self) -> None:
        """Inspect hero_all, world_all, main_prefabs_barrel, and main_prefabs_simplehero bundles."""
        patterns = [
            "hero_all_*.bundle",
            "world_all_*.bundle",
            "main_prefabs_barrel_*.bundle",
            "main_prefabs_simplehero_*.bundle",
        ]
        for pat in patterns:
            for p in sorted(self.ab_dir.glob(pat)):
                try:
                    env = load_unity_bundle(p)
                    deps: List[str] = []
                    for o in env.objects:
                        if o.type.name == "AssetBundle":
                            tt = o.read_typetree()
                            deps = [str(d).lower() for d in tt.get("m_Dependencies", [])]
                            break
                    for cpath in env.container.keys():
                        self.prefab_cab_links[cpath] = deps
                except Exception as exc:
                    logging.warning("Failed inspecting prefab bundle %s: %s", p.name, exc)

    def humanize_slug(self, slug: str) -> str:
        """Produce a clean English display title from an asset slug + Pinyin glossary."""
        low = slug.lower()
        for tok, eng in PINYIN_GLOSSARY:
            if tok in low:
                # Preserve stage/tier/variant suffix details cleanly
                suffix_parts: List[str] = []
                for m in re.findall(r"(?:lv\d+|s[1-5]|10[1-6]|0[1-6]|pve|world|hq|ex|pro|formal)", low):
                    up = m.upper()
                    if up not in eng.upper() and up not in suffix_parts:
                        suffix_parts.append(up)
                if suffix_parts:
                    return f"{eng} ({' '.join(suffix_parts[:3])})"
                return eng

        # Clean standard prefixes and format nicely
        cleaned = slug
        for pref in (
            "environment_decorate_a_build_",
            "environment_decorate_a_vehicle_",
            "environment_decorate_",
            "environment_map_world_resource_",
            "environment_map_world_vehicle_",
            "environment_map_world_",
            "environment_map_",
            "environment_pve_a_build_",
            "environment_pve_a_vehicle_",
            "environment_pve_",
            "environment_ui_a_build_",
            "environment_ui_",
            "environment_world_",
            "environment_scenedisplay_",
            "overlord_environment_",
            "overlord_pve_",
            "soldier_weapon_",
            "soldier_lastdayactor_",
            "soldier_",
            "monster_s3_",
            "monster_s4_",
            "monster_s5_",
            "monster_",
            "npc_game_npc_gp_",
            "npc_game_",
            "buildings_a_build_",
            "buildings_",
        ):
            if cleaned.lower().startswith(pref):
                cleaned = cleaned[len(pref) :]
                break
        words = [w for w in re.split(r"[_\s]+", cleaned) if w]
        titled = " ".join(w.upper() if re.match(r"^(s\d|lv\d|pve|hq|ui|gp|ex|ak\d*|mp5|aa12|m4\d*|uav)$", w, re.I) else w.capitalize() for w in words)
        return titled or "Game Model"

    def resolve_bundle(self, bundle_name: str) -> Dict[str, Any]:
        """Resolve exact faction, camp_id, English name, hero_id, and evidence source for a bundle."""
        slug = bundle_slug(bundle_name)
        low_slug = slug.lower()
        nk_slug = norm_key(slug)

        # Strip category prefix to get core character/unit codename when inside soldier_*
        soldier_sub = ""
        if low_slug.startswith("soldier_"):
            soldier_sub = low_slug[len("soldier_") :]
        nk_soldier = norm_key(soldier_sub)

        # 1. Weapons (check before hero codenames so hero_katana / hero_electricsaw / blond_gun stay in Weapons!)
        if (
            low_slug.startswith("soldier_weapon_")
            or bundle_name.startswith("art_barrel_models_weapon_")
            or low_slug.startswith("a_hero_doss_01")
            or "npc_weapon_" in low_slug
        ):
            w_name = self.humanize_slug(slug)
            if low_slug.startswith("a_hero_doss_01"):
                w_name = "Doss Heavy Weapons"
            elif "npc_weapon_rifle_01" in low_slug:
                w_name = "Survivor Assault Rifle"
            return {
                "slug": slug,
                "english_name": w_name,
                "faction": "Weapons",
                "camp_id": None,
                "hero_id": None,
                "evidence_source": f"bundle_path({bundle_name}) -> Weapons asset category",
            }

        # 2. Exact Playable Hero & Hero Companion Resolution (Blood_Rose, Wings_of_Dawn, Guard_of_Order)
        if soldier_sub and not soldier_sub.startswith(("lastdayactor_", "bloodhand_", "item_", "soldier_")):
            # Note: nvlieshou_low_@normal is modular generic female troop suit (aps_pve_part_zombie Suit_woman_1)
            if "nvlieshou_low" not in soldier_sub:
                h_match = self.hero_codename_map.get(nk_soldier)
                if h_match and h_match["camp_id"] in (1, 2, 3):
                    return {
                        "slug": slug,
                        "english_name": h_match["english_name"],
                        "base_hero_name": h_match.get("base_hero_name", h_match["english_name"]),
                        "faction": h_match["faction"],
                        "camp_id": h_match["camp_id"],
                        "hero_id": h_match["hero_id"],
                        "evidence_source": h_match["evidence_source"],
                    }

        # 3. Blood Hand & Raiders
        if low_slug.startswith("soldier_bloodhand_") or any(
            r_tok in low_slug for r_tok in ("gangster_snake", "s4_feitu_", "huairen")
        ):
            return {
                "slug": slug,
                "english_name": self.humanize_slug(slug),
                "faction": "Blood_Hand_and_Raiders",
                "camp_id": -1,
                "hero_id": None,
                "evidence_source": f"bundle_path({bundle_name}) + enemy raider/Blood Hand table match",
            }

        # 4. Vehicles & Tanks
        if (
            low_slug.startswith(("tank", "vehicle_"))
            or "a_vehicle_" in low_slug
            or "world_vehicle_" in low_slug
            or "parkourbattlewin_vehicle" in low_slug
            or low_slug == "tank_killer"
            or low_slug.endswith("yunbingche")
        ):
            v_name = None
            for vk, vv in self.vehicle_model_map.items():
                if vk and vk in nk_slug:
                    v_name = f"{vv} ({self.humanize_slug(slug)})" if vv.lower() not in slug.lower() else vv
                    break
            return {
                "slug": slug,
                "english_name": v_name or self.humanize_slug(slug),
                "faction": "Vehicles_and_Tanks",
                "camp_id": 0,
                "hero_id": None,
                "evidence_source": "car_show / car_show_barrel / vehicle asset bundle classification",
            }

        # 5. Zombies & Monsters (including overlord_pve, monster_*, monster_snowman, and npc_game zombies)
        if (
            low_slug.startswith(("monster_", "overlord_pve_"))
            or "monster_snowman" in low_slug
            or (low_slug.startswith("npc_game_") and any(z in low_slug for z in ("zomb", "zob")))
        ):
            m_name = None
            if low_slug.startswith("overlord_pve_"):
                stage_m = re.search(r"10([1-6])", low_slug)
                st = f" Stage {stage_m.group(1)}" if stage_m else ""
                m_name = f"Overlord Mecha-Zilla PVE{st}"
            else:
                for mk, mv in self.monster_model_map.items():
                    if len(mk) >= 6 and mk in nk_slug:
                        m_name = mv
                        break
            if not m_name or m_name.lower() == slug.lower().replace("_", " "):
                m_name = self.humanize_slug(slug)
            return {
                "slug": slug,
                "english_name": m_name,
                "faction": "Zombies_and_Monsters",
                "camp_id": -1,
                "hero_id": None,
                "evidence_source": "APS_monster / aps_pve_zombie / barrel_monster_base / overlord_show",
            }

        # 6. NPCs & Survivors (human npc_game_* + Rebecca + Survivor Nurse fenhushi)
        if low_slug.startswith("npc_game_") or soldier_sub in ("rebecca", "hero_fenhushi"):
            n_name = self.npc_model_map.get(nk_soldier) or self.npc_model_map.get(nk_slug)
            if not n_name:
                if "npc_t1" in low_slug:
                    n_name = "Shelter Survivor NPC"
                elif "littlegirl" in low_slug:
                    n_name = "Survivor Little Girl"
                elif "fem" in low_slug:
                    n_name = f"Female Survivor ({self.humanize_slug(slug)})"
                elif "man" in low_slug:
                    n_name = f"Male Survivor ({self.humanize_slug(slug)})"
                else:
                    n_name = self.humanize_slug(slug)
            return {
                "slug": slug,
                "english_name": n_name,
                "faction": "NPCs_and_Survivors",
                "camp_id": 0,
                "hero_id": None,
                "evidence_source": "npc_base / camp=0 neutral survivor classification",
            }

        # 7. Soldier props (Drink01, Feed) -> Buildings_and_Environment; remaining soldier_* -> Troops_and_Soldiers
        if low_slug.startswith("soldier_item_"):
            return {
                "slug": slug,
                "english_name": f"Shelter Supply Prop ({self.humanize_slug(slug)})",
                "faction": "Buildings_and_Environment",
                "camp_id": 0,
                "hero_id": None,
                "evidence_source": "Soldier/Item prop asset classification",
            }

        if low_slug.startswith("soldier_"):
            t_name = self.humanize_slug(slug)
            if "nvlieshou_low" in low_slug:
                t_name = "Female Squad Trooper Base"
            elif soldier_sub == "lastdayactor_@normal":
                t_name = "Male Squad Trooper Base"
            elif "hero_uav_man" in low_slug:
                t_name = "Tactical Landmine Operator"
            return {
                "slug": slug,
                "english_name": t_name,
                "faction": "Troops_and_Soldiers",
                "camp_id": 0,
                "hero_id": None,
                "evidence_source": "Generic military / PVE soldier asset classification",
            }

        # 8. Buildings & Environment (buildings, environment_*, overlord_environment, barrel_*, props)
        b_name = None
        if low_slug.startswith("overlord_environment_"):
            stage_m = re.search(r"10([1-6])", low_slug)
            st = f" Stage {stage_m.group(1)}" if stage_m else ""
            b_name = f"Overlord HQ World Pedestal{st}"
        else:
            # Check exact or substring building.json model match
            tail = re.sub(r"^(environment_decorate_|environment_pve_|environment_ui_|buildings_)", "", low_slug)
            nk_tail = norm_key(tail)
            if nk_tail in self.building_model_map:
                b_name = self.building_model_map[nk_tail]
            else:
                for bk, bv in self.building_model_map.items():
                    if len(bk) >= 10 and bk in nk_tail:
                        b_name = bv
                        break
        return {
            "slug": slug,
            "english_name": b_name or self.humanize_slug(slug),
            "faction": "Buildings_and_Environment",
            "camp_id": 0,
            "hero_id": None,
            "evidence_source": "building.json / environment & prop asset classification",
        }


def is_normal_map_name(tex_name: str, used_as_normal: bool = False) -> bool:
    if used_as_normal:
        return True
    low = tex_name.lower()
    return bool(
        re.search(r"(_n|_nm|_normal|_normalmap|_normals|_bump)(\b|_\d+$)", low)
    )


def unpack_dxt5nm_if_needed(img: Image.Image) -> Tuple[Image.Image, bool]:
    """
    Detect Unity DXT5nm packed normal maps (R=255 constant, G=Y, A=X) and reconstruct
    standard tangent-space RGB normal maps (R=X, G=Y, B=Z, A=255) for OBJ/MTL and GLB.
    """
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
        nz_sq = np.clip(1.0 - nx * nx - ny * ny, 0.0, 1.0)
        nz = np.sqrt(nz_sq)
        out = np.empty_like(arr)
        out[:, :, 0] = arr[:, :, 3]
        out[:, :, 1] = arr[:, :, 1]
        out[:, :, 2] = np.clip(np.round((nz * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)
        out[:, :, 3] = 255
        return Image.fromarray(out, mode="RGBA"), True
    return rgba, False


def is_diffuse_candidate(tex_name: str) -> bool:
    low = tex_name.lower()
    bad_tokens = (
        "_n",
        "_nm",
        "normal",
        "_m",
        "_mm",
        "mask",
        "metafllic",
        "metallic",
        "_s",
        "_e",
        "emission",
        "_sdw",
        "shadow",
        "matrix",
        "gpuskin",
        "default-particle",
        "noise",
        "dissolve",
        "fog",
    )
    for bt in bad_tokens:
        if low.endswith(bt) or f"{bt}_" in low:
            return False
    return True


def score_diffuse_fallback(tex_name: str, target_hint: str, has_non_2d: bool) -> int:
    low = tex_name.lower()
    if not is_diffuse_candidate(tex_name):
        return -1000
    score = 0
    if has_non_2d and "_2d" in low:
        score -= 200
    if re.search(r"(_d|_basemap|_bsaemap|_albedo|_cm|_color)(\b|_)", low):
        score += 60
    hint_words = [w for w in re.split(r"[^a-z0-9]+", target_hint.lower()) if len(w) >= 3 and w not in ("hero", "mesh", "mat", "skin")]
    for hw in hint_words:
        if hw in low:
            score += 45
    return score


def is_auxiliary_glb_mesh(mesh_name: str, all_mesh_names_lower: List[str], vert_count: int) -> bool:
    """
    Identify LOD shells, GPU-skin duplicates, decimated clones, and flat ground shadow planes
    so the combined GLB contains clean primary geometry without z-fighting duplicates.
    """
    low = mesh_name.lower()
    if "(clone)_quality_" in low:
        return True
    if "_skin_mesh_" in low or "_gpu_mesh_" in low:
        return True
    if re.search(r"(_lod[1-9]|_lod$)", low):
        return True
    if re.search(r"(_sdw$|_shadow$|^shadow_|^yingzi$|^eff_mesh_|_zs_m$)", low):
        return True
    if vert_count <= 12 and any(k in low for k in ("plane", "dimian", "sdw", "shadow", "_m")):
        return True
    if low.startswith("bakedmesh") and any(n in ("body", "helmet", "torso") for n in all_mesh_names_lower):
        return True
    if "_low_body" in low and "body" in all_mesh_names_lower:
        return True
    if "_low_hair" in low and "hair" in all_mesh_names_lower:
        return True
    return False


def process_single_bundle(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker entrypoint: extract textures, OBJs, MTL, GLB, and model info.json for one bundle."""
    bundle_path = Path(task["bundle_path"])
    out_dir = Path(task["out_dir"])
    meta = task["meta"]
    cab_map: Dict[str, str] = task["cab_map"]

    try:
        env = load_unity_bundle(bundle_path)
    except Exception as exc:
        return {
            "status": "skipped",
            "bundle": bundle_path.name,
            "reason": f"bundle_load_error: {strip_em_dashes(str(exc))}",
            "meta": meta,
        }

    by_pid: Dict[int, Any] = {o.path_id: o for o in env.objects}
    af_externals: List[str] = []
    if env.objects:
        try:
            af_externals = [e.name.lower() for e in env.objects[0].assets_file.externals]
        except Exception:
            af_externals = []

    ext_env_cache: Dict[str, UnityPy.Environment] = {}

    def resolve_pptr_obj(pptr: Optional[Dict[str, Any]]) -> Optional[Any]:
        if not pptr:
            return None
        fid = int(pptr.get("m_FileID", 0) or 0)
        pid = int(pptr.get("m_PathID", 0) or 0)
        if pid == 0:
            return None
        if fid == 0:
            return by_pid.get(pid)
        if 1 <= fid <= len(af_externals):
            cab_name = af_externals[fid - 1]
            ext_bpath = cab_map.get(cab_name)
            if ext_bpath:
                if ext_bpath not in ext_env_cache:
                    try:
                        ext_env_cache[ext_bpath] = load_unity_bundle(Path(ext_bpath))
                    except Exception:
                        return None
                for eo in ext_env_cache[ext_bpath].objects:
                    if eo.path_id == pid:
                        return eo
        return None

    # 1. Inspect all Mesh objects first; skip bundle cleanly if zero non-empty meshes exist
    raw_meshes: List[Dict[str, Any]] = []
    for obj in env.objects:
        if obj.type.name == "Mesh":
            try:
                mdata = obj.read()
                mh = MeshHandler(mdata)
                mh.process()
                tris_by_sub = mh.get_triangles() if mh.m_VertexCount > 0 else []
                total_f = sum(len(t) for t in tris_by_sub)
                if mh.m_VertexCount > 0 and total_f > 0 and mh.m_Vertices:
                    raw_meshes.append(
                        {
                            "path_id": obj.path_id,
                            "raw_name": strip_em_dashes(mdata.m_Name or f"mesh_{abs(obj.path_id)}"),
                            "mh": mh,
                            "tris_by_sub": tris_by_sub,
                            "vert_count": int(mh.m_VertexCount),
                            "face_count": int(total_f),
                        }
                    )
            except Exception as exc:
                logging.debug("Mesh read error in %s: %s", bundle_path.name, exc)

    if not raw_meshes:
        obj_types: Dict[str, int] = {}
        for o in env.objects:
            t = o.type.name
            obj_types[t] = obj_types.get(t, 0) + 1
        if obj_types.get("AudioClip", 0) > 0:
            reason = f"no_mesh_audio_bundle (AudioClip={obj_types['AudioClip']})"
        elif obj_types.get("AnimationClip", 0) > 0 and obj_types.get("Texture2D", 0) == 0:
            reason = f"no_mesh_animation_only_bundle (AnimationClip={obj_types['AnimationClip']})"
        elif obj_types.get("Texture2D", 0) > 0:
            reason = f"no_mesh_2d_or_texture_bundle (Texture2D={obj_types['Texture2D']}, Material={obj_types.get('Material', 0)})"
        else:
            reason = f"no_mesh_prefab_or_cubemap_bundle (objects={sum(obj_types.values())})"
        return {
            "status": "skipped",
            "bundle": bundle_path.name,
            "reason": reason,
            "object_counts": obj_types,
            "meta": meta,
        }

    # Create output directories now that we know >= 1 valid Mesh exists
    tex_dir = out_dir / "textures"
    tex_dir.mkdir(parents=True, exist_ok=True)

    # 2. Collect AnimationClip names
    anim_clips: List[str] = sorted(
        {
            strip_em_dashes(o.peek_name() or "")
            for o in env.objects
            if o.type.name == "AnimationClip" and (o.peek_name() or "").strip()
        }
    )

    # 3. Export all bundled Texture2D assets + cache PIL images by (file_key, path_id)
    exported_textures: Dict[Tuple[str, int], Dict[str, Any]] = {}
    used_tex_filenames: Dict[str, int] = {}

    def register_texture_obj(tex_obj: Any, source_tag: str, used_as_normal: bool = False) -> Optional[Dict[str, Any]]:
        key = (source_tag, tex_obj.path_id)
        if key in exported_textures:
            # If newly discovered to be used as a normal map and not yet unpacked, upgrade it
            entry = exported_textures[key]
            if used_as_normal and not entry["unpacked_normal"]:
                unpacked_img, did_unpack = unpack_dxt5nm_if_needed(entry["raw_img"])
                if did_unpack:
                    unpacked_img.save(tex_dir / entry["filename"], format="PNG")
                    entry["img"] = unpacked_img
                    entry["unpacked_normal"] = True
            return entry
        try:
            tdata = tex_obj.read()
            raw_name = strip_em_dashes(tdata.m_Name or f"tex_{abs(tex_obj.path_id)}")
            pil_img = tdata.image
            if pil_img is None or pil_img.size[0] <= 0 or pil_img.size[1] <= 0:
                return None
            raw_rgba = pil_img.convert("RGBA")
            final_img = raw_rgba
            did_unpack = False
            if is_normal_map_name(raw_name, used_as_normal=used_as_normal):
                final_img, did_unpack = unpack_dxt5nm_if_needed(raw_rgba)

            base_fn = safe_filename(raw_name, max_len=48)
            low_fn = base_fn.lower()
            if low_fn in used_tex_filenames:
                used_tex_filenames[low_fn] += 1
                base_fn = f"{base_fn}_{used_tex_filenames[low_fn]}"
            else:
                used_tex_filenames[low_fn] = 1
            fname = f"{base_fn}.png"
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
        except Exception as exc:
            logging.debug("Texture export skipped in %s: %s", bundle_path.name, exc)
            return None

    for obj in env.objects:
        if obj.type.name == "Texture2D":
            register_texture_obj(obj, "local", used_as_normal=False)

    all_local_tex_entries = list(exported_textures.values())
    has_non_2d_tex = any("_2d" not in e["name"].lower() and is_diffuse_candidate(e["name"]) for e in all_local_tex_entries)

    # 4. Parse Materials (local and referenced external)
    parsed_materials: Dict[Tuple[str, int], Dict[str, Any]] = {}

    def parse_material_obj(mat_obj: Any, source_tag: str) -> Optional[Dict[str, Any]]:
        mkey = (source_tag, mat_obj.path_id)
        if mkey in parsed_materials:
            return parsed_materials[mkey]
        try:
            tt = mat_obj.read_typetree()
        except Exception:
            return None
        mname = strip_em_dashes(tt.get("m_Name") or f"mat_{abs(mat_obj.path_id)}")
        saved = tt.get("m_SavedProperties", {})
        tex_envs = saved.get("m_TexEnvs", [])
        colors = saved.get("m_Colors", [])

        kd = (1.0, 1.0, 1.0)
        for c_item in colors:
            if isinstance(c_item, (list, tuple)) and len(c_item) == 2:
                cname, cval = c_item
                if cname in ("_BaseColor", "_Color") and isinstance(cval, dict):
                    r = float(cval.get("r", 1.0))
                    g = float(cval.get("g", 1.0))
                    b = float(cval.get("b", 1.0))
                    if (r + g + b) > 0.05:
                        kd = (
                            round(min(max(r, 0.0), 1.0), 4),
                            round(min(max(g, 0.0), 1.0), 4),
                            round(min(max(b, 0.0), 1.0), 4),
                        )
                    break

        diffuse_entry: Optional[Dict[str, Any]] = None
        normal_entry: Optional[Dict[str, Any]] = None

        tex_prop_map: Dict[str, Dict[str, Any]] = {}
        for t_item in tex_envs:
            if isinstance(t_item, (list, tuple)) and len(t_item) == 2:
                pname, pval = t_item
                if isinstance(pval, dict) and isinstance(pval.get("m_Texture"), dict):
                    tex_prop_map[str(pname)] = pval["m_Texture"]

        for dprop in ("_BaseMap", "_MainTex", "_AlbedoMap", "_ColorMap", "_Diffuse", "_Tex"):
            pptr = tex_prop_map.get(dprop)
            if pptr and int(pptr.get("m_PathID", 0) or 0) != 0:
                tobj = resolve_pptr_obj(pptr)
                if tobj is not None and tobj.type.name == "Texture2D":
                    stag = "local" if int(pptr.get("m_FileID", 0) or 0) == 0 else f"ext_{pptr.get('m_FileID')}"
                    diffuse_entry = register_texture_obj(tobj, stag, used_as_normal=False)
                    if diffuse_entry is not None:
                        break

        for nprop in ("_NormalMap", "_BumpMap", "_Normal", "_DetailNormalMap", "_Dump"):
            pptr = tex_prop_map.get(nprop)
            if pptr and int(pptr.get("m_PathID", 0) or 0) != 0:
                tobj = resolve_pptr_obj(pptr)
                if tobj is not None and tobj.type.name == "Texture2D":
                    stag = "local" if int(pptr.get("m_FileID", 0) or 0) == 0 else f"ext_{pptr.get('m_FileID')}"
                    normal_entry = register_texture_obj(tobj, stag, used_as_normal=True)
                    if normal_entry is not None:
                        break

        mat_info = {
            "name": mname,
            "safe_name": safe_filename(mname, max_len=48),
            "kd": kd,
            "diffuse": diffuse_entry,
            "normal": normal_entry,
        }
        parsed_materials[mkey] = mat_info
        return mat_info

    local_materials: List[Dict[str, Any]] = []
    for obj in env.objects:
        if obj.type.name == "Material":
            minfo = parse_material_obj(obj, "local")
            if minfo is not None:
                local_materials.append(minfo)

    # 5. Link Renderers (SkinnedMeshRenderer & MeshFilter + MeshRenderer) -> Mesh path_id
    mf_by_go: Dict[int, int] = {}
    mr_by_go: Dict[int, List[Dict[str, Any]]] = {}
    mesh_renderers_map: Dict[int, List[Dict[str, Any]]] = {}

    for obj in env.objects:
        t = obj.type.name
        if t == "SkinnedMeshRenderer":
            try:
                tt = obj.read_typetree()
                m_pptr = tt.get("m_Mesh", {})
                if int(m_pptr.get("m_FileID", 0) or 0) == 0:
                    mpid = int(m_pptr.get("m_PathID", 0) or 0)
                    mats_resolved: List[Optional[Dict[str, Any]]] = []
                    local_mat_hits = 0
                    diffuse_hits = 0
                    for mp in tt.get("m_Materials", []):
                        mobj = resolve_pptr_obj(mp)
                        if mobj is not None and mobj.type.name == "Material":
                            stag = "local" if int(mp.get("m_FileID", 0) or 0) == 0 else f"ext_{mp.get('m_FileID')}"
                            mi = parse_material_obj(mobj, stag)
                            mats_resolved.append(mi)
                            if stag == "local":
                                local_mat_hits += 1
                            if mi and mi.get("diffuse"):
                                diffuse_hits += 1
                        else:
                            mats_resolved.append(None)
                    mesh_renderers_map.setdefault(mpid, []).append(
                        {
                            "is_smr": True,
                            "local_mat_hits": local_mat_hits,
                            "diffuse_hits": diffuse_hits,
                            "materials": mats_resolved,
                        }
                    )
            except Exception:
                pass
        elif t == "MeshFilter":
            try:
                tt = obj.read_typetree()
                go_pid = int(tt.get("m_GameObject", {}).get("m_PathID", 0) or 0)
                m_pptr = tt.get("m_Mesh", {})
                if go_pid and int(m_pptr.get("m_FileID", 0) or 0) == 0:
                    mpid = int(m_pptr.get("m_PathID", 0) or 0)
                    if mpid:
                        mf_by_go[go_pid] = mpid
            except Exception:
                pass
        elif t == "MeshRenderer":
            try:
                tt = obj.read_typetree()
                go_pid = int(tt.get("m_GameObject", {}).get("m_PathID", 0) or 0)
                if go_pid:
                    mr_by_go[go_pid] = tt.get("m_Materials", [])
            except Exception:
                pass

    for go_pid, mpid in mf_by_go.items():
        raw_mp_list = mr_by_go.get(go_pid, [])
        mats_resolved = []
        local_mat_hits = 0
        diffuse_hits = 0
        for mp in raw_mp_list:
            mobj = resolve_pptr_obj(mp)
            if mobj is not None and mobj.type.name == "Material":
                stag = "local" if int(mp.get("m_FileID", 0) or 0) == 0 else f"ext_{mp.get('m_FileID')}"
                mi = parse_material_obj(mobj, stag)
                mats_resolved.append(mi)
                if stag == "local":
                    local_mat_hits += 1
                if mi and mi.get("diffuse"):
                    diffuse_hits += 1
            else:
                mats_resolved.append(None)
        mesh_renderers_map.setdefault(mpid, []).append(
            {
                "is_smr": False,
                "local_mat_hits": local_mat_hits,
                "diffuse_hits": diffuse_hits,
                "materials": mats_resolved,
            }
        )

    # 6. Deduplicate exact-name meshes in the bundle, ranking SMR > diffuse mats > vertex count
    grouped_by_name: Dict[str, List[Dict[str, Any]]] = {}
    for rm in raw_meshes:
        r_cands = mesh_renderers_map.get(rm["path_id"], [])
        best_r = None
        if r_cands:
            best_r = max(
                r_cands,
                key=lambda rc: (rc["diffuse_hits"], rc["local_mat_hits"], 1 if rc["is_smr"] else 0),
            )
        rm["best_renderer"] = best_r
        rm["is_smr"] = bool(best_r and best_r["is_smr"])
        rm["diffuse_hits"] = int(best_r["diffuse_hits"]) if best_r else 0
        rm["local_mat_hits"] = int(best_r["local_mat_hits"]) if best_r else 0
        sname = safe_filename(rm["raw_name"], max_len=48)
        rm["safe_name"] = sname
        grouped_by_name.setdefault(sname.lower(), []).append(rm)

    unique_meshes: List[Dict[str, Any]] = []
    for _, candidates in sorted(grouped_by_name.items(), key=lambda kv: kv[0]):
        winner = max(
            candidates,
            key=lambda c: (
                1 if c["is_smr"] else 0,
                c["diffuse_hits"],
                c["local_mat_hits"],
                c["vert_count"],
                c["face_count"],
            ),
        )
        unique_meshes.append(winner)

    # Helper to resolve submesh material (with smart filename fallback if needed)
    mtl_registry: Dict[str, Dict[str, Any]] = {}

    def resolve_submesh_material(mesh_entry: Dict[str, Any], sub_idx: int) -> Dict[str, Any]:
        best_r = mesh_entry.get("best_renderer")
        mat_info: Optional[Dict[str, Any]] = None
        if best_r and best_r["materials"]:
            mlist = best_r["materials"]
            mat_info = mlist[sub_idx] if sub_idx < len(mlist) else mlist[-1]

        # Fallback: match local Material by mesh name if no renderer material was linked
        if mat_info is None and local_materials:
            non_2d_mats = [m for m in local_materials if not m["name"].lower().endswith("_2d")]
            pool = non_2d_mats or local_materials
            m_low = mesh_entry["raw_name"].lower()
            best_m = None
            best_m_score = -1
            for lm in pool:
                ln = lm["name"].lower()
                sc = (10 if lm.get("diffuse") else 0) + (25 if (ln in m_low or m_low in ln) else 0)
                if sc > best_m_score:
                    best_m_score = sc
                    best_m = lm
            mat_info = dict(best_m) if best_m else None

        if mat_info is None:
            mat_info = {
                "name": f"{mesh_entry['safe_name']}_mat_{sub_idx}",
                "safe_name": safe_filename(f"{mesh_entry['safe_name']}_mat_{sub_idx}", max_len=48),
                "kd": (1.0, 1.0, 1.0),
                "diffuse": None,
                "normal": None,
            }
        else:
            mat_info = dict(mat_info)

        # Smart diffuse texture filename fallback if material has no diffuse linked
        if mat_info.get("diffuse") is None and all_local_tex_entries:
            hint = f"{mesh_entry['raw_name']} {mat_info['name']}"
            ranked = sorted(
                all_local_tex_entries,
                key=lambda te: (
                    score_diffuse_fallback(te["name"], hint, has_non_2d_tex),
                    te["width"] * te["height"],
                ),
                reverse=True,
            )
            if ranked and score_diffuse_fallback(ranked[0]["name"], hint, has_non_2d_tex) >= 0:
                mat_info["diffuse"] = ranked[0]

        # Smart normal map fallback if material has no normal linked
        if mat_info.get("normal") is None and mat_info.get("diffuse") is not None:
            d_stem = re.sub(r"(_d|_basemap|_bsaemap|_albedo|_cm|_color)$", "", mat_info["diffuse"]["name"], flags=re.I).lower()
            for te in all_local_tex_entries:
                if is_normal_map_name(te["name"]) and te["name"].lower().startswith(d_stem) and len(d_stem) >= 3:
                    mat_info["normal"] = te
                    break

        # Register unique safe material name in MTL registry
        s_mat = mat_info["safe_name"]
        if s_mat in mtl_registry:
            prev = mtl_registry[s_mat]
            prev_d = prev["diffuse"]["filename"] if prev.get("diffuse") else None
            cur_d = mat_info["diffuse"]["filename"] if mat_info.get("diffuse") else None
            if prev_d != cur_d:
                s_mat = safe_filename(f"{s_mat}_{mesh_entry['safe_name']}_{sub_idx}", max_len=52)
                mat_info["safe_name"] = s_mat
        mtl_registry[s_mat] = mat_info
        return mat_info

    # 7. Export each unique Mesh to <mesh_name>.obj + decide GLB inclusion
    all_u_names_lower = [um["raw_name"].lower() for um in unique_meshes]
    primary_flags = [
        not is_auxiliary_glb_mesh(um["raw_name"], all_u_names_lower, um["vert_count"])
        for um in unique_meshes
    ]
    if not any(primary_flags):
        primary_flags = [True] * len(unique_meshes)

    mesh_records: List[Dict[str, Any]] = []
    glb_scene_geoms: Dict[str, trimesh.Trimesh] = {}
    glb_errors: List[str] = []
    exported_files: List[str] = []

    for idx_m, um in enumerate(unique_meshes):
        mh: MeshHandler = um["mh"]
        tris_by_sub = um["tris_by_sub"]
        include_in_glb = primary_flags[idx_m]

        verts_rh = np.array([[-v[0], v[1], v[2]] for v in mh.m_Vertices], dtype=np.float64)
        verts_rh = np.nan_to_num(verts_rh, nan=0.0, posinf=0.0, neginf=0.0)

        has_uv = bool(mh.m_UV0 and len(mh.m_UV0) == len(verts_rh))
        uvs_arr = (
            np.nan_to_num(np.array([[uv[0], uv[1]] for uv in mh.m_UV0], dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
            if has_uv
            else None
        )

        has_norm = bool(mh.m_Normals and len(mh.m_Normals) == len(verts_rh))
        norms_rh = (
            np.nan_to_num(np.array([[-n[0], n[1], n[2]] for n in mh.m_Normals], dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
            if has_norm
            else None
        )

        obj_filename = f"{um['safe_name']}.obj"
        obj_lines: List[str] = [
            "# Exported from Last Z AssetBundles\n",
            "mtllib materials.mtl\n",
            f"o {um['safe_name']}\n",
        ]
        for vx, vy, vz in verts_rh:
            obj_lines.append(f"v {vx:.7g} {vy:.7g} {vz:.7g}\n")
        if uvs_arr is not None:
            for u, v in uvs_arr:
                obj_lines.append(f"vt {u:.7g} {v:.7g}\n")
        if norms_rh is not None:
            for nx, ny, nz in norms_rh:
                obj_lines.append(f"vn {nx:.7g} {ny:.7g} {nz:.7g}\n")

        sub_mat_names: List[str] = []
        non_empty_subs = 0
        for s_idx, sub_tris in enumerate(tris_by_sub):
            if not sub_tris:
                continue
            non_empty_subs += 1
            minfo = resolve_submesh_material(um, s_idx)
            s_mat = minfo["safe_name"]
            sub_mat_names.append(s_mat)
            obj_lines.append(f"g {um['safe_name']}_{s_idx}\n")
            obj_lines.append(f"usemtl {s_mat}\n")
            if has_uv and has_norm:
                for a, b, c in sub_tris:
                    ia, ib, ic = c + 1, b + 1, a + 1
                    obj_lines.append(f"f {ia}/{ia}/{ia} {ib}/{ib}/{ib} {ic}/{ic}/{ic}\n")
            elif has_uv:
                for a, b, c in sub_tris:
                    ia, ib, ic = c + 1, b + 1, a + 1
                    obj_lines.append(f"f {ia}/{ia} {ib}/{ib} {ic}/{ic}\n")
            elif has_norm:
                for a, b, c in sub_tris:
                    ia, ib, ic = c + 1, b + 1, a + 1
                    obj_lines.append(f"f {ia}//{ia} {ib}//{ib} {ic}//{ic}\n")
            else:
                for a, b, c in sub_tris:
                    ia, ib, ic = c + 1, b + 1, a + 1
                    obj_lines.append(f"f {ia} {ib} {ic}\n")

            # Build compact submesh Trimesh for combined GLB
            if include_in_glb:
                try:
                    faces_arr = np.array([[c, b, a] for a, b, c in sub_tris], dtype=np.int64)
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
                        # Check if material/mesh is explicitly transparent glass/alpha cutout
                        low_hint = f"{um['raw_name']} {minfo['name']}".lower()
                        is_alpha_mat = any(k in low_hint for k in ("glass", "boli", "alpha", "tran"))
                        base_tex = d_img if is_alpha_mat else d_img.convert("RGB")
                        pbr_kwargs: Dict[str, Any] = {
                            "name": s_mat,
                            "baseColorTexture": base_tex,
                            "metallicFactor": 0.05,
                            "roughnessFactor": 0.85,
                            "alphaMode": "BLEND" if is_alpha_mat else "OPAQUE",
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
                    geom_name = um["safe_name"] if len(tris_by_sub) == 1 else f"{um['safe_name']}_sub{s_idx}"
                    if geom_name in glb_scene_geoms:
                        geom_name = f"{geom_name}_{idx_m}"
                    glb_scene_geoms[geom_name] = tm
                except Exception as gexc:
                    glb_errors.append(f"{um['safe_name']}[{s_idx}]: {strip_em_dashes(str(gexc))}")

        obj_text = strip_em_dashes("".join(obj_lines))
        (out_dir / obj_filename).write_text(obj_text, encoding="utf-8")
        exported_files.append(obj_filename)

        mesh_records.append(
            {
                "name": um["raw_name"],
                "obj_file": obj_filename,
                "vertices": um["vert_count"],
                "faces": um["face_count"],
                "submeshes": non_empty_subs,
                "included_in_glb": include_in_glb,
                "materials": sub_mat_names,
            }
        )

    # 8. Write materials.mtl
    mtl_lines: List[str] = ["# Materials for Last Z 3D Model\n"]
    material_links_summary: List[Dict[str, Any]] = []
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
        material_links_summary.append(
            {
                "material": s_mat,
                "unity_material_name": minfo["name"],
                "diffuse_texture": d_entry["rel_path"] if d_entry else None,
                "normal_texture": n_entry["rel_path"] if n_entry else None,
            }
        )

    mtl_text = strip_em_dashes("".join(mtl_lines))
    (out_dir / "materials.mtl").write_text(mtl_text, encoding="utf-8")
    exported_files.append("materials.mtl")

    # 9. Export combined self-contained textured GLB
    safe_model_base = task["safe_model_name"]
    glb_filename: Optional[str] = f"{safe_model_base}.glb"
    if glb_scene_geoms:
        try:
            scene = trimesh.Scene()
            for gname, gmesh in glb_scene_geoms.items():
                scene.add_geometry(gmesh, node_name=gname, geom_name=gname)
            glb_bytes = scene.export(file_type="glb")
            (out_dir / glb_filename).write_bytes(glb_bytes)
            exported_files.append(glb_filename)
        except Exception as gexc:
            glb_errors.append(f"scene_export_failed: {strip_em_dashes(str(gexc))}")
            glb_filename = None
    else:
        glb_errors.append("no_valid_submeshes_for_glb")
        glb_filename = None

    for te in sorted(exported_textures.values(), key=lambda x: x["rel_path"]):
        exported_files.append(te["rel_path"])

    total_verts = sum(m["vertices"] for m in mesh_records)
    total_faces = sum(m["faces"] for m in mesh_records)

    # 10. Write model info.json
    model_info = {
        "model_name": safe_model_base,
        "english_name": strip_em_dashes(meta["english_name"]),
        "slug": meta["slug"],
        "faction": meta["faction"],
        "camp_id": meta["camp_id"],
        "hero_id": meta["hero_id"],
        "evidence_source": strip_em_dashes(meta["evidence_source"]),
        "source_bundle": bundle_path.name,
        "folder": f"{meta['faction']}/{out_dir.name}",
        "glb_file": glb_filename,
        "glb_submesh_count": len(glb_scene_geoms),
        "glb_errors": glb_errors,
        "mesh_count": len(mesh_records),
        "texture_count": len(exported_textures),
        "total_vertices": total_verts,
        "total_faces": total_faces,
        "meshes": mesh_records,
        "material_texture_links": material_links_summary,
        "textures": [
            {
                "name": te["name"],
                "file": te["rel_path"],
                "width": te["width"],
                "height": te["height"],
                "unpacked_dxt5nm": te["unpacked_normal"],
            }
            for te in sorted(exported_textures.values(), key=lambda x: x["rel_path"])
        ],
        "animation_clips": anim_clips,
        "exported_files": exported_files + ["model info.json"],
    }
    info_json_str = strip_em_dashes(json.dumps(model_info, indent=2, ensure_ascii=False))
    assert "\u2014" not in info_json_str
    (out_dir / "model info.json").write_text(info_json_str, encoding="utf-8")

    return {
        "status": "exported",
        "bundle": bundle_path.name,
        "info": model_info,
    }


def build_cab_index(ab_dir: Path) -> Dict[str, str]:
    """Index CAB-<hash> internal serialized names across model, common, and auto-asset bundles."""
    cab_map: Dict[str, str] = {}
    candidates = (
        sorted(ab_dir.glob("art_lastday_models_*.bundle"))
        + sorted(ab_dir.glob("art_barrel_models_*.bundle"))
        + sorted(ab_dir.glob("gameres_auto_assets_*.bundle"))
        + sorted(ab_dir.glob("main_material_*.bundle"))
    )
    for p in candidates:
        try:
            env = load_unity_bundle(p)
            if env.objects:
                af_name = env.objects[0].assets_file.name.lower()
                if af_name:
                    cab_map[af_name] = str(p)
        except Exception:
            pass
    return cab_map


def verify_sample_glbs(models_dir: Path, exported_infos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Verify exported GLB models across all required factions using trimesh.load."""
    target_factions = [
        "Blood_Rose",
        "Wings_of_Dawn",
        "Guard_of_Order",
        "Zombies_and_Monsters",
        "Vehicles_and_Tanks",
        "Blood_Hand_and_Raiders",
        "Troops_and_Soldiers",
        "NPCs_and_Survivors",
        "Weapons",
        "Buildings_and_Environment",
    ]
    results: List[Dict[str, Any]] = []
    for fac in target_factions:
        fac_models = [m for m in exported_infos if m["faction"] == fac and m.get("glb_file")]
        for m in fac_models[:2]:
            glb_path = models_dir / m["folder"] / m["glb_file"]
            loaded = trimesh.load(glb_path, force="scene")
            if isinstance(loaded, trimesh.Trimesh):
                v_cnt = int(len(loaded.vertices))
                f_cnt = int(len(loaded.faces))
                g_cnt = 1
            else:
                v_cnt = int(sum(len(g.vertices) for g in loaded.geometry.values()))
                f_cnt = int(sum(len(g.faces) for g in loaded.geometry.values()))
                g_cnt = int(len(loaded.geometry))
            if v_cnt <= 0 or f_cnt <= 0:
                raise RuntimeError(f"GLB verification failed with zero geometry for {glb_path}")
            results.append(
                {
                    "faction": fac,
                    "english_name": m["english_name"],
                    "glb_path": f"{m['folder']}/{m['glb_file']}",
                    "size_bytes": glb_path.stat().st_size,
                    "geometries": g_cnt,
                    "vertices": v_cnt,
                    "faces": f_cnt,
                }
            )
    return results


def write_catalog_and_readme(
    models_dir: Path,
    exported_infos: List[Dict[str, Any]],
    skipped_bundles: List[Dict[str, Any]],
    verified_glbs: List[Dict[str, Any]],
    elapsed_sec: float,
) -> None:
    """Write models_catalog.json, models_catalog.csv, and README.md with zero em dashes."""
    faction_stats: Dict[str, Dict[str, int]] = {
        f: {"models": 0, "glbs": 0, "objs": 0, "textures": 0, "vertices": 0, "faces": 0}
        for f in FACTION_ORDER
    }
    for m in exported_infos:
        st = faction_stats[m["faction"]]
        st["models"] += 1
        st["glbs"] += 1 if m.get("glb_file") else 0
        st["objs"] += m["mesh_count"]
        st["textures"] += m["texture_count"]
        st["vertices"] += m["total_vertices"]
        st["faces"] += m["total_faces"]

    totals = {
        "scanned_bundles": len(exported_infos) + len(skipped_bundles),
        "exported_model_bundles": len(exported_infos),
        "skipped_no_mesh_bundles": len(skipped_bundles),
        "total_glbs": sum(s["glbs"] for s in faction_stats.values()),
        "total_objs": sum(s["objs"] for s in faction_stats.values()),
        "total_textures": sum(s["textures"] for s in faction_stats.values()),
        "total_vertices": sum(s["vertices"] for s in faction_stats.values()),
        "total_faces": sum(s["faces"] for s in faction_stats.values()),
        "elapsed_seconds": round(elapsed_sec, 2),
    }

    hero_roster = [
        {
            "faction": m["faction"],
            "camp_id": m["camp_id"],
            "hero_id": m["hero_id"],
            "english_name": m["english_name"],
            "slug": m["slug"],
            "folder": m["folder"],
            "glb_file": m["glb_file"],
            "meshes": m["mesh_count"],
            "textures": m["texture_count"],
            "vertices": m["total_vertices"],
            "faces": m["total_faces"],
            "evidence_source": m["evidence_source"],
        }
        for m in exported_infos
        if m["faction"] in ("Blood_Rose", "Wings_of_Dawn", "Guard_of_Order")
    ]

    catalog_payload = {
        "summary": totals,
        "factions": faction_stats,
        "hero_to_faction_table": hero_roster,
        "verified_glb_samples": verified_glbs,
        "models": exported_infos,
        "skipped_bundles": skipped_bundles,
    }
    cat_json_text = strip_em_dashes(json.dumps(catalog_payload, indent=2, ensure_ascii=False))
    assert "\u2014" not in cat_json_text
    (models_dir / "models_catalog.json").write_text(cat_json_text, encoding="utf-8")

    # Write models_catalog.csv
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf, lineterminator="\n")
    writer.writerow(
        [
            "faction",
            "camp_id",
            "hero_id",
            "english_name",
            "model_name",
            "slug",
            "folder",
            "glb_file",
            "mesh_count",
            "texture_count",
            "total_vertices",
            "total_faces",
            "animation_count",
            "source_bundle",
            "evidence_source",
        ]
    )
    for m in exported_infos:
        writer.writerow(
            [
                m["faction"],
                "" if m["camp_id"] is None else m["camp_id"],
                "" if m["hero_id"] is None else m["hero_id"],
                strip_em_dashes(m["english_name"]),
                strip_em_dashes(m["model_name"]),
                m["slug"],
                m["folder"],
                m["glb_file"] or "",
                m["mesh_count"],
                m["texture_count"],
                m["total_vertices"],
                m["total_faces"],
                len(m["animation_clips"]),
                m["source_bundle"],
                strip_em_dashes(m["evidence_source"]),
            ]
        )
    csv_text = strip_em_dashes(csv_buf.getvalue())
    assert "\u2014" not in csv_text
    (models_dir / "models_catalog.csv").write_text(csv_text, encoding="utf-8")

    # Write README.md
    md: List[str] = [
        "# Last Z: Survival Shooter - Complete 3D Model Archive\n\n",
        "Complete, faction-organized 3D model extraction from Last Z's Unity AssetBundles ",
        "with official English localization names, PNG textures (including unpacked DXT5nm tangent-space normal maps), ",
        "Wavefront `.obj` + `materials.mtl` exports, and self-contained textured `.glb` scenes ready for Windows 3D Viewer and Blender.\n\n",
        "## Extraction Summary\n\n",
        f"- **Total Candidate Bundles Scanned:** {totals['scanned_bundles']}\n",
        f"- **3D Model Bundles Exported:** {totals['exported_model_bundles']}\n",
        f"- **Skipped Non-Mesh Bundles (Audio / 2D / Anim-Only / Cubemap):** {totals['skipped_no_mesh_bundles']}\n",
        f"- **Combined Textured `.glb` Files:** {totals['total_glbs']}\n",
        f"- **Individual Sub-Mesh `.obj` Files:** {totals['total_objs']}\n",
        f"- **Exported `.png` Textures:** {totals['total_textures']}\n",
        f"- **Total 3D Vertices / Triangles:** {totals['total_vertices']:,} vertices / {totals['total_faces']:,} triangles\n\n",
        "## Per-Faction Model Counts\n\n",
        "| Faction Folder | Official Scope | Models | GLBs | OBJs | Textures | Vertices | Triangles |\n",
        "|---|---|---:|---:|---:|---:|---:|---:|\n",
    ]
    for fac in FACTION_ORDER:
        st = faction_stats[fac]
        md.append(
            f"| `{fac}` | {FACTION_DESCRIPTIONS[fac]} | {st['models']} | {st['glbs']} | {st['objs']} | "
            f"{st['textures']} | {st['vertices']:,} | {st['faces']:,} |\n"
        )
    md.append(
        f"| **TOTAL** | **All Factions & Categories** | **{totals['exported_model_bundles']}** | "
        f"**{totals['total_glbs']}** | **{totals['total_objs']}** | **{totals['total_textures']}** | "
        f"**{totals['total_vertices']:,}** | **{totals['total_faces']:,}** |\n\n"
    )

    md.append("## Verified Playable Hero-to-Faction Resolution Table\n\n")
    md.append(
        "All playable 3D hero bundles were cross-referenced against `aps new heroes.json`, "
        "`lw hero appearance.json`, `lw hero skill.json`, `enums complete.json`, and the 32,212 English localization strings:\n\n"
    )
    md.append("| Faction | Camp | Hero ID | English Name | Asset Slug | Folder | GLB | Meshes | Triangles |\n")
    md.append("|---|---:|---:|---|---|---|---|---:|---:|\n")
    for h in hero_roster:
        md.append(
            f"| `{h['faction']}` | {h['camp_id']} | {h['hero_id']} | **{h['english_name']}** | "
            f"`{h['slug']}` | `{h['folder']}` | `{h['glb_file']}` | {h['meshes']} | {h['faces']:,} |\n"
        )

    md.append("\n## Verified `.glb` Load Checks (`trimesh.load`)\n\n")
    md.append("| Faction | Model | GLB File | Size (KB) | Sub-Geometries | Vertices | Faces |\n")
    md.append("|---|---|---|---:|---:|---:|---:|\n")
    for vg in verified_glbs:
        md.append(
            f"| `{vg['faction']}` | {vg['english_name']} | `{vg['glb_path']}` | "
            f"{vg['size_bytes'] / 1024.0:.1f} | {vg['geometries']} | {vg['vertices']:,} | {vg['faces']:,} |\n"
        )

    md.append("\n## Skipped Bundles Summary (Zero `Mesh` Assets)\n\n")
    reason_buckets: Dict[str, int] = {}
    for sb in skipped_bundles:
        r_prefix = sb["reason"].split(" (", 1)[0]
        reason_buckets[r_prefix] = reason_buckets.get(r_prefix, 0) + 1
    md.append("| Skip Reason | Count |\n|---|---:|\n")
    for rk, rv in sorted(reason_buckets.items(), key=lambda x: -x[1]):
        md.append(f"| `{rk}` | {rv} |\n")

    md.append("\n<details>\n<summary>Full List of Skipped Non-Mesh Bundles</summary>\n\n")
    for sb in skipped_bundles:
        md.append(f"- `{sb['bundle']}`: {sb['reason']}\n")
    md.append("\n</details>\n")

    readme_text = strip_em_dashes("".join(md))
    assert "\u2014" not in readme_text
    (models_dir / "README.md").write_text(readme_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract all 3D models from Last Z AssetBundles.")
    parser.add_argument("--ab-dir", type=Path, default=DEFAULT_AB_DIR)
    parser.add_argument("--repo-dir", type=Path, default=DEFAULT_REPO_DIR)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 4))
    parser.add_argument("--clean", action="store_true", help="Clean existing models output directory before extraction")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    t_start = time.time()

    ab_dir: Path = args.ab_dir
    repo_dir: Path = args.repo_dir
    models_dir: Path = repo_dir / "models"

    if not ab_dir.exists():
        raise FileNotFoundError(f"AssetBundles directory not found: {ab_dir}")

    if args.clean and models_dir.exists():
        logging.info("Cleaning previous models directory: %s", models_dir)
        shutil.rmtree(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    for fac in FACTION_ORDER:
        (models_dir / fac).mkdir(parents=True, exist_ok=True)

    logging.info("Resolving Last Z XML tables, localization, and prefab links...")
    resolver = GameMetadataResolver(repo_dir=repo_dir, ab_dir=ab_dir)

    logging.info("Indexing internal CAB hashes across model bundles...")
    cab_map = build_cab_index(ab_dir)
    logging.info("Indexed %d CAB bundle entries.", len(cab_map))

    candidate_bundles = sorted(
        set(
            list(ab_dir.glob("art_lastday_models_*.bundle"))
            + list(ab_dir.glob("art_barrel_models_*.bundle"))
            + list(ab_dir.glob("hero_all_*.bundle"))
            + list(ab_dir.glob("world_all_*.bundle"))
        ),
        key=lambda p: p.name,
    )
    logging.info("Discovered %d candidate bundles to scan and extract.", len(candidate_bundles))

    # Build deterministic, collision-free folder assignments
    used_folder_paths: Dict[str, int] = {}
    tasks: List[Dict[str, Any]] = []
    for bpath in candidate_bundles:
        meta = resolver.resolve_bundle(bpath.name)
        safe_eng = safe_filename(meta["english_name"], max_len=34)
        safe_slg = safe_filename(meta["slug"], max_len=34)
        folder_base = f"{safe_eng}__{safe_slg}"
        rel_key = f"{meta['faction']}/{folder_base}".lower()
        if rel_key in used_folder_paths:
            used_folder_paths[rel_key] += 1
            folder_base = f"{folder_base}_{used_folder_paths[rel_key]}"
        else:
            used_folder_paths[rel_key] = 1

        tasks.append(
            {
                "bundle_path": str(bpath),
                "out_dir": str(models_dir / meta["faction"] / folder_base),
                "safe_model_name": safe_eng,
                "meta": meta,
                "cab_map": cab_map,
            }
        )

    exported_infos: List[Dict[str, Any]] = []
    skipped_bundles: List[Dict[str, Any]] = []

    logging.info("Extracting 3D meshes, PNG textures, OBJ/MTL, and GLB files with %d workers...", args.workers)
    done_count = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for res in pool.map(process_single_bundle, tasks, chunksize=4):
            done_count += 1
            if done_count % 100 == 0 or done_count == len(tasks):
                logging.info("Progress: %d / %d bundles processed...", done_count, len(tasks))
            if res["status"] == "exported":
                exported_infos.append(res["info"])
            else:
                skipped_bundles.append(
                    {
                        "bundle": res["bundle"],
                        "faction_candidate": res["meta"]["faction"],
                        "slug": res["meta"]["slug"],
                        "reason": strip_em_dashes(res["reason"]),
                    }
                )

    # Sort deterministically by faction order, then English name, then folder
    fac_rank = {f: i for i, f in enumerate(FACTION_ORDER)}
    exported_infos.sort(key=lambda m: (fac_rank.get(m["faction"], 99), m["english_name"].lower(), m["folder"].lower()))
    skipped_bundles.sort(key=lambda s: s["bundle"])

    logging.info("Verifying sample exported GLB models via trimesh.load...")
    verified_glbs = verify_sample_glbs(models_dir, exported_infos)
    logging.info("Verified %d sample GLBs across all factions cleanly!", len(verified_glbs))

    elapsed = time.time() - t_start
    write_catalog_and_readme(
        models_dir=models_dir,
        exported_infos=exported_infos,
        skipped_bundles=skipped_bundles,
        verified_glbs=verified_glbs,
        elapsed_sec=elapsed,
    )

    logging.info("Extraction complete in %.1fs!", elapsed)
    for fac in FACTION_ORDER:
        cnt = sum(1 for m in exported_infos if m["faction"] == fac)
        gcnt = sum(1 for m in exported_infos if m["faction"] == fac and m.get("glb_file"))
        logging.info("  %-26s : %3d models (%3d GLBs)", fac, cnt, gcnt)
    logging.info(
        "TOTAL: %d models exported, %d GLBs, %d OBJs, %d PNG textures, %d no-mesh bundles skipped.",
        len(exported_infos),
        sum(1 for m in exported_infos if m.get("glb_file")),
        sum(m["mesh_count"] for m in exported_infos),
        sum(m["texture_count"] for m in exported_infos),
        len(skipped_bundles),
    )


if __name__ == "__main__":
    main()
