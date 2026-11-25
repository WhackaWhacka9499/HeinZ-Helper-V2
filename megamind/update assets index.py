#!/usr/bin/env python3
"""
Idempotent Megamind Game Assets Indexer & Raw Manifest Builder.

Indexes every extracted Last Z game icon (`assets/icons/Icons Catalog.json`,
17,049 PNGs), Hub UI WebP core sprite (`launcher/assets/game icons/manifest.json`,
47 core + 35 hero + 115 item sprites), 3D model (`models/Models Catalog.json`,
493 GLB+OBJ scenes including 28 HQ Skins & 28 Vehicle Skins), 2D Spine Hero
Skin (`models/Models Catalog.json` -> `hero_skins_spine`, 110 bundles), and
exported World/Seasonal/Event/City/Terrain map (`maps/Maps Catalog.json`,
499 PNGs) into:
  1. `megamind/megamind index.sqlite` (layers `game_icon`, `game_model`,
     `hub_game_icon`, `hero_skin_spine`, `game_map` + unambiguous `edges` + FTS5 sync)
  2. `megamind/raw/game assets icons and models.json`

Usage:
  python megamind/update assets index.py
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import sqlite3
import sys
import time
from typing import Any

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MEGA_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = MEGA_DIR.parent
RAW_DIR = MEGA_DIR / "raw"
DB_PATH = MEGA_DIR / "megamind index.sqlite"

ICONS_CATALOG_PATH = REPO_ROOT / "assets" / "icons" / "Icons Catalog.json"
MODELS_CATALOG_PATH = REPO_ROOT / "models" / "Models Catalog.json"
MAPS_CATALOG_PATH = REPO_ROOT / "maps" / "Maps Catalog.json"
MAPS_DIR = REPO_ROOT / "maps"
HUB_MANIFEST_PATH = REPO_ROOT / "launcher" / "assets" / "game icons" / "manifest.json"
HUB_ICONS_DIR = REPO_ROOT / "launcher" / "assets" / "game icons"
RAW_ASSET_MANIFEST_PATH = RAW_DIR / "game assets icons and models.json"

XML_HEROES_PATH = RAW_DIR / "xml tables" / "aps new heroes.json"
XML_GOODS_PATH = RAW_DIR / "xml tables" / "goods.json"

ASSET_LAYERS = ("game_icon", "game_model", "hub_game_icon", "hero_skin_spine", "game_map")

ICON_CATEGORY_TO_DOMAIN: dict[str, str] = {
    "Resources": "items_bag_shops_vip",
    "Items": "items_bag_shops_vip",
    "Hero Portraits Round": "heroes_skills_equip",
    "Hero Portraits Small": "heroes_skills_equip",
    "Hero Portraits Large": "heroes_skills_equip",
    "Hero Fullbody": "heroes_skills_equip",
    "Hero Fragments": "heroes_skills_equip",
    "Hero Medals": "heroes_skills_equip",
    "Hero Equipment": "heroes_skills_equip",
    "Skills": "heroes_skills_equip",
    "Science and Tech": "science_research_talents",
    "Buildings": "buildings_city",
    "Troops and Soldiers": "army_troops_hospital",
    "Vehicles and Aircraft": "garage_vehicles",
    "Monsters and Bosses": "pve_exploration_bosses",
    "Activities and Events": "events_fullprep",
    "Alliance and World": "alliance",
    "Flags": "alliance",
    "Emojis": "chat_moments_mail",
    "Collectibles and Fishing": "events_fullprep",
    "UI HUD": "core_engine",
    "Misc": "core_engine",
}

MODEL_FACTION_TO_DOMAIN: dict[str, str] = {
    "Blood Rose": "heroes_skills_equip",
    "Wings of Dawn": "heroes_skills_equip",
    "Guard of Order": "heroes_skills_equip",
    "HQ Skins": "buildings_city",
    "Vehicle Skins": "garage_vehicles",
    "Zombies and Monsters": "pve_exploration_bosses",
    "Blood Hand and Raiders": "pve_exploration_bosses",
    "Troops and Soldiers": "army_troops_hospital",
    "Vehicles and Tanks": "garage_vehicles",
    "NPCs and Survivors": "buildings_city",
    "Weapons": "heroes_skills_equip",
    "Buildings and Environment": "buildings_city",
}

HUB_CORE_TO_DOMAIN: dict[str, str] = {
    "diamonds": "items_bag_shops_vip",
    "electricity": "items_bag_shops_vip",
    "zent": "items_bag_shops_vip",
    "wood": "items_bag_shops_vip",
    "food": "items_bag_shops_vip",
    "fuel": "items_bag_shops_vip",
    "steel": "items_bag_shops_vip",
    "rss_box": "items_bag_shops_vip",
    "boomer": "pve_exploration_bosses",
    "npc": "pve_exploration_bosses",
    "saga": "pve_exploration_bosses",
    "tyrant": "pve_exploration_bosses",
    "furylord": "pve_exploration_bosses",
    "map_kills_chain": "pve_exploration_bosses",
    "radar": "radar_detect",
    "speedup": "items_bag_shops_vip",
    "badge": "heroes_skills_equip",
    "skill_book": "heroes_skills_equip",
    "alloy": "items_bag_shops_vip",
    "power_core": "items_bag_shops_vip",
    "wrench": "items_bag_shops_vip",
    "hero_exp": "heroes_skills_equip",
    "hero_shard": "heroes_skills_equip",
    "recruit": "heroes_skills_equip",
    "hospital": "army_troops_hospital",
    "alliance_gift": "alliance",
    "alliance_duel": "alliance",
    "alliance_rank": "alliance",
    "alliance_team": "alliance",
    "red_packet": "chat_moments_mail",
    "troops": "army_troops_hospital",
    "bounty": "trucks_bounties",
    "truck": "trucks_bounties",
    "dig": "buildings_city",
    "arena": "arena_pvp",
    "vip": "items_bag_shops_vip",
    "tech": "science_research_talents",
    "teleport": "items_bag_shops_vip",
    "chest": "items_bag_shops_vip",
    "equipment": "heroes_skills_equip",
    "building": "buildings_city",
    "shield": "alliance",
    "hq": "alliance",
    "mine_event": "events_fullprep",
    "hero_battle": "pve_exploration_bosses",
    "daily_tasks": "daily_tasks_quests",
    "vehicle": "garage_vehicles",
}

XML_TABLE_TO_SQL_PREFIX: dict[str, str] = {
    "aps_new_heroes": "heroes",
    "APS_science": "science_techs",
    "aps_science_tab": "science_tabs",
    "alScienceTab": "alliance_science_tabs",
    "detect_event": "radar_detect_events",
    "APS_monster": "monsters",
    "APS_arms": "armies",
    "building": "buildings",
    "daily_quest": "daily_quests",
    "heroes_exclusive_equip": "hero_sp_equips",
    "ds_equip": "equips",
    "car_talent": "car_talents",
    "APS_talent": "commander_talents",
    "season_mastery": "mastery_skills",
    "skill": "core_skills",
    "alliance_skill": "alliance_skills",
    "state_skill": "state_skills",
}

MAP_CATEGORY_TO_DOMAIN: dict[str, str] = {
    "Main World Maps": "formations_marches_world",
    "Seasonal Maps": "formations_marches_world",
    "Terrain and Biomes": "formations_marches_world",
    "Event Maps": "events_fullprep",
    "City and Base Maps": "buildings_city",
}

MAP_SUBCATEGORY_TO_DOMAIN: dict[str, str] = {
    "Province Zones": "formations_marches_world",
    "Decoded World Map": "formations_marches_world",
    "Stitched 4K World Map": "formations_marches_world",
    "World Map Quadrants": "formations_marches_world",
    "Official Minimap Assets": "formations_marches_world",
    "Pre-Season 1 Clash of Thrones": "formations_marches_world",
    "Season 2 Wastes Watcher": "formations_marches_world",
    "Season 3 Everfrost Era": "formations_marches_world",
    "Season 4 Dinosaur Origin": "formations_marches_world",
    "Season 5 Moonlit Elegy": "formations_marches_world",
    "Season 6": "formations_marches_world",
    "Volcano War": "alliance",
    "Capital War": "alliance",
    "Cross Server War": "alliance",
    "World Siege": "alliance",
    "Season Influence Territories": "alliance",
    "Desert Battlefield": "events_fullprep",
    "Castle Adventure": "events_fullprep",
    "Landing Operations": "events_fullprep",
    "Mine Events": "events_fullprep",
    "World Cup": "events_fullprep",
    "Dispatch and Explore": "events_fullprep",
    "World Boss and Seasonal Events": "pve_exploration_bosses",
    "Main City Ground": "buildings_city",
    "Fog Masks": "buildings_city",
    "Base Expansion Districts": "buildings_city",
}


def _infer_map_xml_refs(m: dict[str, Any]) -> list[str]:
    """Derive verified XML table references associated with a map entry."""
    title = str(m.get("title") or "")
    cat = str(m.get("category") or "")
    sub = str(m.get("subcategory") or "")
    season = str(m.get("season") or "")
    src_assets = str(m.get("source_assets") or "")
    notes = str(m.get("notes") or "")
    combined = f"{src_assets} {notes}"

    refs: list[str] = []

    def add(name: str) -> None:
        if name and name not in refs:
            refs.append(name)

    if "volcano_land/building/area.json" in combined:
        for t in ("volcano_land", "volcano_building", "volcano_area", "volcano_res"):
            add(t)
    for hit in re.findall(r"\b([A-Za-z0-9_]+)\.json\b", combined):
        if hit not in ("area",):
            add(hit)

    if sub == "Volcano War":
        for t in ("volcano_land", "volcano_building", "volcano_area", "volcano_res"):
            add(t)
    elif sub == "Desert Battlefield" or "Desert Resource Tiers" in title:
        for t in ("desert_refresh", "desert"):
            add(t)
    elif sub == "Province Zones" or title == "World Zones and Provinces Map":
        add("worldcity")
        add("world_scene")
    elif sub in ("Decoded World Map", "Stitched 4K World Map", "World Map Quadrants", "Official Minimap Assets"):
        add("world_scene")
        if sub in ("Decoded World Map", "Stitched 4K World Map") or "Topology" in title:
            add("worldcity")
    elif sub == "Season Influence Territories":
        add("season_review" if "Review" in title else "season_influence")
        add("aps_season")
    elif sub == "Capital War":
        add("capital_war")
        add("server_capital_reward")
    elif sub == "Mine Events":
        add("mine")
    elif sub == "Dispatch and Explore":
        for t in ("explore_level", "explorer_entrance", "explorer_case"):
            add(t)
    elif sub == "Base Expansion Districts":
        for t in ("aps_landlock", "aps_landlock_b", "land_lock_property", "aps_buildzone"):
            add(t)
    elif sub in ("Main City Ground", "Fog Masks"):
        add("main_city_area")
    elif sub == "World Boss and Seasonal Events":
        t_low = title.lower()
        if any(k in t_low for k in ("dinosaur", "dino", "fossil", "jurassic")):
            add("dinosaur_boss")
        elif "barrel" in t_low:
            add("barrel_pve")
            add("barrel_monster")
        elif any(k in t_low for k in ("monster tower", "campaign push")):
            add("pve_world")
            add("push_map")
        elif any(k in t_low for k in ("arena", "champion")):
            add("pve_world")
        else:
            add("activity_monsterboss")

    if cat == "Seasonal Maps":
        add("aps_season")
        add("season_config")
        add("world_scene")
        if "Topology" in title:
            add("worldcity")
    elif cat == "Terrain and Biomes":
        add("world_scene")

    if season.startswith(("Pre-Season 1", "Season ")):
        add("aps_season")

    return refs


def strip_em_dashes(text: Any) -> str:
    """Ensure zero em dashes (U+2014) appear in any indexed text."""
    s = "" if text is None else str(text)
    if "\u2014" in s:
        s = s.replace("\u2014", " - ")
    if "&" + "mdash;" in s:
        s = s.replace("&" + "mdash;", " - ")
    return s


def _norm_tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 2}


def _load_xml_rows_map(path: pathlib.Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    cols = data.get("columns") or []
    rows = data.get("rows") or {}
    return {rid: dict(zip(cols, arr)) for rid, arr in rows.items()}


def inspect_sqlite_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    """Inspect entities, entities_fts, edges, and trigger setup before mutating."""
    objs = conn.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
    ).fetchall()
    tables: dict[str, str] = {}
    triggers: list[tuple[str, str, str]] = []
    for typ, name, tbl, sql in objs:
        if typ == "table":
            tables[name] = sql or ""
        elif typ == "trigger":
            triggers.append((name, tbl, sql or ""))

    for req in ("entities", "entities_fts", "edges", "meta"):
        if req not in tables:
            raise RuntimeError(f"Missing required SQLite table `{req}` in {DB_PATH}")

    fts_sql = tables["entities_fts"].lower()
    is_external_content = "content='entities'" in fts_sql or 'content="entities"' in fts_sql
    entity_triggers = [t for t in triggers if t[1] == "entities"]
    has_insert_trigger = any("insert" in t[2].lower() for t in entity_triggers)
    has_delete_trigger = any("delete" in t[2].lower() for t in entity_triggers)

    return {
        "is_external_content": is_external_content,
        "has_insert_trigger": has_insert_trigger,
        "has_delete_trigger": has_delete_trigger,
        "trigger_count": len(entity_triggers),
    }


def _build_hub_reverse_maps(
    hub_manifest: dict[str, Any],
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    core_by_sprite: dict[str, list[str]] = {}
    for key, sprite in (hub_manifest.get("core") or {}).items():
        core_by_sprite.setdefault(sprite.lower(), []).append(key)

    heroes_by_sprite: dict[str, list[str]] = {}
    for hid, sprite in (hub_manifest.get("hero_id_to_sprite") or {}).items():
        heroes_by_sprite.setdefault(sprite.lower(), []).append(str(hid))

    items_by_sprite: dict[str, list[str]] = {}
    for iid, sprite in (hub_manifest.get("item_id_to_sprite") or {}).items():
        items_by_sprite.setdefault(sprite.lower(), []).append(str(iid))

    return core_by_sprite, heroes_by_sprite, items_by_sprite


def _pick_best_icon(
    candidates: list[dict[str, Any]],
    prefer_category: str = "",
    require_name_substr: str = "",
) -> dict[str, Any] | None:
    pool = candidates
    if prefer_category:
        cat_hits = [c for c in pool if c.get("category") == prefer_category]
        if cat_hits:
            pool = cat_hits
    if require_name_substr:
        sub = require_name_substr.lower()
        name_hits = [
            c
            for c in pool
            if sub in (c.get("english_name") or "").lower()
            or sub in (c.get("clean_name") or "").lower()
        ]
        if not name_hits:
            return None
        pool = name_hits
    if not pool:
        return None

    def score(c: dict[str, Any]) -> tuple[int, int, int]:
        fn = c.get("filename") or ""
        has_suffix = 1 if re.search(r" \(\d+\)\.png$", fn) else 0
        has_xml = 1 if (c.get("xml_table") and c.get("xml_id")) else 0
        area = int(c.get("orig_width") or 0) * int(c.get("orig_height") or 0)
        return (has_suffix, -has_xml, -area)

    return sorted(pool, key=score)[0]


def build_raw_manifest(
    icons_cat: dict[str, Any],
    models_cat: dict[str, Any],
    maps_cat: dict[str, Any],
    hub_manifest: dict[str, Any],
    anh_rows: dict[str, dict[str, str]],
    goods_rows: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Build and write megamind/raw/game assets icons and models.json."""
    icons_list: list[dict[str, Any]] = icons_cat.get("icons") or []
    models_list: list[dict[str, Any]] = models_cat.get("models") or []
    spine_list: list[dict[str, Any]] = models_cat.get("hero_skins_spine") or []
    spine_summary: dict[str, Any] = models_cat.get("hero_skins_spine_summary") or {}
    maps_list: list[dict[str, Any]] = maps_cat.get("maps") or []

    by_sprite: dict[str, list[dict[str, Any]]] = {}
    by_cat_name: dict[tuple[str, str], list[dict[str, Any]]] = {}
    total_icon_bytes = 0
    for r in icons_list:
        total_icon_bytes += int(r.get("file_size_bytes") or 0)
        by_sprite.setdefault((r.get("sprite_name") or "").lower(), []).append(r)
        en = (r.get("english_name") or r.get("clean_name") or "").lower()
        by_cat_name.setdefault((r.get("category") or "", en), []).append(r)

    core_map = hub_manifest.get("core") or {}
    hero_map = hub_manifest.get("hero_id_to_sprite") or {}
    item_map = hub_manifest.get("item_id_to_sprite") or {}

    core_webp_files = list(HUB_ICONS_DIR.glob("*.webp"))
    hero_webp_files = list((HUB_ICONS_DIR / "heroes").glob("*.webp"))
    item_webp_files = list((HUB_ICONS_DIR / "items").glob("*.webp"))

    hub_core_entries: list[dict[str, Any]] = []
    for key, sprite in core_map.items():
        webp_path = HUB_ICONS_DIR / f"{key}.webp"
        icon_hit = _pick_best_icon(by_sprite.get(sprite.lower(), []))
        hub_core_entries.append(
            {
                "key": key,
                "sprite_name": sprite,
                "webp_path": f"launcher/assets/game icons/{key}.webp",
                "webp_bytes": webp_path.stat().st_size if webp_path.exists() else 0,
                "source_icon_path": f"assets/icons/{icon_hit['relative_path']}" if icon_hit else "",
                "english_name": strip_em_dashes(icon_hit.get("clean_name") if icon_hit else ""),
                "season": icon_hit.get("season", "") if icon_hit else "",
                "category": icon_hit.get("category", "") if icon_hit else "",
                "domain": HUB_CORE_TO_DOMAIN.get(key, "core_engine"),
            }
        )

    playable_heroes: list[dict[str, Any]] = []
    for h in models_cat.get("hero_to_season_faction_table") or []:
        hid = str(h["hero_id"])
        ename = strip_em_dashes(h["english_name"])
        base_name = (
            ename.replace(" Awakened", "")
            .replace(" Bear Companion", "")
            .replace(" Horse Stampede", "")
            .replace(" Tactical", "")
        )
        row = anh_rows.get(hid, {})

        r_sp = row.get("round_hero_icon") or ""
        s_sp = row.get("hero_icon") or ""
        l_sp = row.get("hero_body") or ""
        p_id = (row.get("hero_pieces") or "").split("|")[0]
        f_sp = (goods_rows.get(p_id) or {}).get("icon", "")

        r_ic = _pick_best_icon(by_sprite.get(r_sp.lower(), []), require_name_substr=base_name)
        if r_ic is None:
            r_ic = _pick_best_icon(
                by_cat_name.get(("Hero Portraits Round", base_name.lower()), []),
                require_name_substr=base_name,
            )

        s_ic = _pick_best_icon(by_sprite.get(s_sp.lower(), []), require_name_substr=base_name)
        if s_ic is None:
            s_ic = _pick_best_icon(
                by_cat_name.get(("Hero Portraits Small", base_name.lower()), []),
                require_name_substr=base_name,
            )

        l_ic = _pick_best_icon(by_sprite.get(l_sp.lower(), []), require_name_substr=base_name)
        if l_ic is None:
            l_ic = _pick_best_icon(
                by_cat_name.get(("Hero Portraits Large", base_name.lower()), []),
                require_name_substr=base_name,
            )

        fb_ic = _pick_best_icon(
            by_cat_name.get(("Hero Fullbody", base_name.lower()), []),
            require_name_substr=base_name,
        )
        frag_ic = _pick_best_icon(by_sprite.get(f_sp.lower(), []), require_name_substr=base_name)
        if frag_ic is None:
            frag_ic = _pick_best_icon(
                by_cat_name.get(("Hero Fragments", f"{base_name.lower()} fragment"), []),
                require_name_substr=base_name,
            )

        hub_hero_sp = hero_map.get(hid, "")
        hub_hero_webp = (
            f"launcher/assets/game icons/heroes/{hub_hero_sp}.webp"
            if hub_hero_sp and (HUB_ICONS_DIR / "heroes" / f"{hub_hero_sp}.webp").exists()
            else ""
        )

        playable_heroes.append(
            {
                "hero_id": int(h["hero_id"]),
                "english_name": ename,
                "season": h["season"],
                "faction": h["faction"],
                "camp_id": h["camp_id"],
                "model_folder": f"models/{h['folder']}",
                "glb_path": f"models/{h['folder']}/{h['glb_file']}",
                "meshes": h.get("meshes", 0),
                "textures": h.get("textures", 0),
                "faces": h.get("faces", 0),
                "round_icon": f"assets/icons/{r_ic['relative_path']}" if r_ic else "",
                "small_icon": f"assets/icons/{s_ic['relative_path']}" if s_ic else "",
                "large_icon": f"assets/icons/{l_ic['relative_path']}" if l_ic else "",
                "fullbody_icon": f"assets/icons/{fb_ic['relative_path']}" if fb_ic else "",
                "fragment_icon": f"assets/icons/{frag_ic['relative_path']}" if frag_ic else "",
                "hub_hero_sprite": hub_hero_webp,
                "season_source": strip_em_dashes(h.get("season_source", "")),
                "evidence_source": strip_em_dashes(h.get("evidence_source", "")),
            }
        )

    categories_out: dict[str, Any] = {}
    for cat, stats in (icons_cat.get("categories") or {}).items():
        categories_out[cat] = {
            **stats,
            "domain": ICON_CATEGORY_TO_DOMAIN.get(cat, "core_engine"),
        }

    factions_out: dict[str, Any] = {}
    for fac, stats in (models_cat.get("factions") or {}).items():
        factions_out[fac] = {
            **stats,
            "domain": MODEL_FACTION_TO_DOMAIN.get(fac, "core_engine"),
        }

    ms = models_cat.get("summary") or {}
    hq_skins_3d = [
        {
            "model_name": strip_em_dashes(m.get("model_name") or ""),
            "season": strip_em_dashes(m.get("season") or ""),
            "folder": f"models/{strip_em_dashes(m.get('folder') or '')}",
            "glb_path": f"models/{strip_em_dashes(m.get('folder') or '')}/{strip_em_dashes(m.get('glb_file') or '')}",
            "mesh_count": int(m.get("mesh_count") or 0),
            "texture_count": int(m.get("texture_count") or 0),
            "total_vertices": int(m.get("total_vertices") or 0),
            "total_faces": int(m.get("total_faces") or 0),
            "evidence_source": strip_em_dashes(m.get("evidence_source") or ""),
            "source_bundle": strip_em_dashes(m.get("source_bundle") or ""),
        }
        for m in models_list
        if m.get("faction") == "HQ Skins"
    ]
    vehicle_skins_3d = [
        {
            "model_name": strip_em_dashes(m.get("model_name") or ""),
            "season": strip_em_dashes(m.get("season") or ""),
            "folder": f"models/{strip_em_dashes(m.get('folder') or '')}",
            "glb_path": f"models/{strip_em_dashes(m.get('folder') or '')}/{strip_em_dashes(m.get('glb_file') or '')}",
            "mesh_count": int(m.get("mesh_count") or 0),
            "texture_count": int(m.get("texture_count") or 0),
            "total_vertices": int(m.get("total_vertices") or 0),
            "total_faces": int(m.get("total_faces") or 0),
            "evidence_source": strip_em_dashes(m.get("evidence_source") or ""),
            "source_bundle": strip_em_dashes(m.get("source_bundle") or ""),
        }
        for m in models_list
        if m.get("faction") == "Vehicle Skins"
    ]
    spine_entries = [
        {
            "display_name": strip_em_dashes(s.get("display_name") or ""),
            "hero_id": s.get("hero_id"),
            "hero_name": strip_em_dashes(s.get("hero_name") or ""),
            "skin_id": s.get("skin_id"),
            "skin_name": strip_em_dashes(s.get("skin_name") or ""),
            "skin_category": strip_em_dashes(s.get("skin_category") or ""),
            "shop_id": s.get("shop_id"),
            "exclusive_weapon_name": strip_em_dashes(s.get("exclusive_weapon_name") or "") or None,
            "season": strip_em_dashes(s.get("season") or ""),
            "faction": strip_em_dashes(s.get("faction") or ""),
            "camp_id": s.get("camp_id"),
            "folder": f"models/{strip_em_dashes(s.get('folder') or '')}",
            "prefab_name": strip_em_dashes(s.get("prefab_name") or ""),
            "source_bundle": strip_em_dashes(s.get("source_bundle") or ""),
            "resolved_external_bundle": strip_em_dashes(s.get("resolved_external_bundle") or "") or None,
            "atlas_pngs": [strip_em_dashes(t.get("file") or "") for t in (s.get("atlas_textures") or [])],
            "spine_files": [strip_em_dashes(f.get("file") or "") for f in (s.get("spine_files") or [])],
            "texture_count": int(s.get("texture_count") or 0),
            "spine_file_count": int(s.get("spine_file_count") or 0),
        }
        for s in spine_list
    ]

    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    maps_total_bytes = 0
    maps_by_category_out: dict[str, Any] = {}
    maps_by_subcat_counts: dict[tuple[str, str], int] = {}
    maps_by_asset_type: dict[str, int] = {}
    stitched_4k_maps: list[dict[str, Any]] = []
    decoded_topo_maps: list[dict[str, Any]] = []
    key_event_maps: list[dict[str, Any]] = []
    province_zones_count = 0

    for cat_name, cnt in sorted((maps_cat.get("counts_by_category") or {}).items()):
        maps_by_category_out[cat_name] = {
            "count": int(cnt),
            "domain": MAP_CATEGORY_TO_DOMAIN.get(cat_name, "formations_marches_world"),
        }

    for m in maps_list:
        rel_p = strip_em_dashes(m.get("relative_path") or "")
        fp = MAPS_DIR / pathlib.Path(rel_p)
        if fp.exists():
            maps_total_bytes += fp.stat().st_size
        cat = strip_em_dashes(m.get("category") or "")
        sub = strip_em_dashes(m.get("subcategory") or "")
        atype = strip_em_dashes(m.get("asset_type") or "")
        title = strip_em_dashes(m.get("title") or "")
        maps_by_subcat_counts[(cat, sub)] = maps_by_subcat_counts.get((cat, sub), 0) + 1
        if atype:
            maps_by_asset_type[atype] = maps_by_asset_type.get(atype, 0) + 1
        if sub == "Province Zones":
            province_zones_count += 1

        entry_brief = {
            "title": title,
            "category": cat,
            "subcategory": sub,
            "season": strip_em_dashes(m.get("season") or ""),
            "resolution": strip_em_dashes(m.get("resolution") or ""),
            "relative_path": f"maps/{rel_p}",
            "xml_refs": _infer_map_xml_refs(m),
        }
        if sub == "Stitched 4K World Map":
            stitched_4k_maps.append(entry_brief)
        elif "Decoded" in atype or "Topology" in title or "Resource Tier" in title:
            decoded_topo_maps.append(entry_brief)
        elif title in (
            "Volcano War Tactical Map Annotated",
            "Castle Adventure Map",
            "Landing Operations Full Map",
            "Landing Operations All Stages Overview",
            "Desert Battlefield Resource Tiers Map",
        ):
            key_event_maps.append(entry_brief)

    maps_subcategories_out = [
        {
            "category": cat,
            "subcategory": sub,
            "count": cnt,
            "domain": MAP_SUBCATEGORY_TO_DOMAIN.get(
                sub, MAP_CATEGORY_TO_DOMAIN.get(cat, "formations_marches_world")
            ),
        }
        for (cat, sub), cnt in sorted(maps_by_subcat_counts.items())
    ]
    maps_asset_types_out = dict(sorted(maps_by_asset_type.items(), key=lambda kv: (-kv[1], kv[0])))

    manifest_doc: dict[str, Any] = {
        "generated_at_utc": now_utc,
        "summary": {
            "total_game_icons": int(icons_cat.get("total_icons") or len(icons_list)),
            "icons_english_named": int(icons_cat.get("total_english_named") or 0),
            "icons_sprite_cleaned": int(icons_cat.get("total_sprite_cleaned") or 0),
            "icons_total_bytes": total_icon_bytes,
            "icons_bundles_scanned": int(icons_cat.get("bundles_scanned") or 0),
            "icons_categories_count": len(categories_out),
            "icons_seasons_count": len(icons_cat.get("seasons") or {}),
            "total_game_models": int(ms.get("exported_model_bundles") or len(models_list)),
            "models_scanned_bundles": int(ms.get("scanned_3d_bundles") or ms.get("scanned_bundles") or 0),
            "models_skipped_no_mesh_bundles": int(ms.get("skipped_no_mesh_bundles") or 0),
            "models_hq_skins_count": int(ms.get("hq_skins_3d_count") or len(hq_skins_3d)),
            "models_vehicle_skins_count": int(ms.get("vehicle_skins_3d_count") or len(vehicle_skins_3d)),
            "hero_skins_2d_spine_count": int(ms.get("hero_skins_2d_spine_count") or len(spine_entries)),
            "total_model_and_skin_assets": int(ms.get("total_catalog_assets") or (len(models_list) + len(spine_entries))),
            "spine_total_atlas_pngs": int(spine_summary.get("total_atlas_pngs") or 0),
            "spine_total_data_files": int(spine_summary.get("total_spine_data_files") or 0),
            "models_total_glbs": int(ms.get("total_glbs") or 0),
            "models_total_objs": int(ms.get("total_objs") or 0),
            "models_total_textures": int(ms.get("total_textures") or 0),
            "models_total_vertices": int(ms.get("total_vertices") or 0),
            "models_total_faces": int(ms.get("total_faces") or 0),
            "models_factions_count": len(factions_out),
            "models_seasons_count": len(models_cat.get("seasons") or {}),
            "total_game_maps": int(maps_cat.get("total_maps") or len(maps_list)),
            "maps_total_bytes": maps_total_bytes,
            "maps_categories_count": len(maps_by_category_out),
            "maps_subcategories_count": len({sub for _, sub in maps_by_subcat_counts}),
            "maps_seasons_count": len(maps_cat.get("counts_by_season") or {}),
            "maps_stitched_4k_count": len(stitched_4k_maps),
            "maps_decoded_topology_count": len(decoded_topo_maps),
            "maps_province_zones_count": province_zones_count,
            "hub_sprites_total_webp": len(core_webp_files) + len(hero_webp_files) + len(item_webp_files),
            "hub_core_sprites": len(core_map),
            "hub_hero_portrait_sprites": len(hero_webp_files),
            "hub_hero_ids_mapped": len(hero_map),
            "hub_item_sprites": len(item_webp_files),
            "hub_item_ids_mapped": len(item_map),
        },
        "directories_and_catalogs": {
            "icons_root": "assets/icons/",
            "icons_layout": icons_cat.get("layout", "<Season>/<Category>/<Clean Name>.png"),
            "icons_catalog_json": "assets/icons/Icons Catalog.json",
            "icons_catalog_csv": "assets/icons/Icons Catalog.csv",
            "icons_readme": "assets/icons/README.md",
            "models_root": "models/",
            "models_layout": "models/<Season>/<Faction or Skin Category>/<Clean Model Name>/",
            "hero_skins_spine_layout": "models/<Season>/<Faction>/Hero Skins 2D Spine/<Hero Name> - <Skin Name>/",
            "models_catalog_json": "models/Models Catalog.json",
            "models_catalog_csv": "models/Models Catalog.csv",
            "hero_skins_spine_csv": "models/Hero Skins Spine Catalog.csv",
            "models_readme": "models/README.md",
            "maps_root": "maps/",
            "maps_layout": "maps/<Category>/<Subcategory or Season>/<Clean Map Name>.png",
            "maps_catalog_json": "maps/Maps Catalog.json",
            "maps_catalog_csv": "maps/Maps Catalog.csv",
            "maps_readme": "maps/README.md",
            "hub_icons_root": "launcher/assets/game icons/",
            "hub_icons_manifest": "launcher/assets/game icons/manifest.json",
        },
        "pipeline_scripts": {
            "extract_icons": "tools/extract all game icons.py",
            "sort_icons": "tools/sort clean game icons.py",
            "extract_models": "tools/extract all game models.py",
            "sort_models": "tools/sort clean game models.py",
            "match_skins": "tools/match purchasable skins.py",
            "extract_maps": "tools/extract all world maps.py",
            "index_megamind": "megamind/update assets index.py",
        },
        "icons_by_season": icons_cat.get("seasons") or {},
        "icons_by_category": categories_out,
        "models_by_season": models_cat.get("seasons") or {},
        "models_by_faction": factions_out,
        "models_season_by_faction": models_cat.get("season_by_faction_counts") or {},
        "hero_skins_spine_summary": spine_summary,
        "maps": {
            "total_maps": int(maps_cat.get("total_maps") or len(maps_list)),
            "total_bytes": maps_total_bytes,
            "counts_by_category": maps_by_category_out,
            "counts_by_season": maps_cat.get("counts_by_season") or {},
            "counts_by_subcategory": maps_subcategories_out,
            "counts_by_asset_type": maps_asset_types_out,
            "stitched_4k_maps": stitched_4k_maps,
            "decoded_topology_maps": decoded_topo_maps,
            "key_stitched_event_maps": key_event_maps,
        },
        "hub_game_icons": {
            "core_count": len(hub_core_entries),
            "hero_portraits_count": len(hero_webp_files),
            "hero_ids_mapped_count": len(hero_map),
            "item_sprites_count": len(item_webp_files),
            "item_ids_mapped_count": len(item_map),
            "core": hub_core_entries,
            "hero_id_to_sprite": hero_map,
            "item_id_to_sprite": item_map,
        },
        "playable_heroes": playable_heroes,
        "hq_skins_3d": hq_skins_3d,
        "vehicle_skins_3d": vehicle_skins_3d,
        "hero_skins_spine": spine_entries,
    }

    text = strip_em_dashes(json.dumps(manifest_doc, indent=2, ensure_ascii=False))
    RAW_ASSET_MANIFEST_PATH.write_text(text + "\n", encoding="utf-8")
    return manifest_doc


def update_sqlite_index(
    icons_cat: dict[str, Any],
    models_cat: dict[str, Any],
    maps_cat: dict[str, Any],
    hub_manifest: dict[str, Any],
    anh_rows: dict[str, dict[str, str]],
    goods_rows: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Idempotently replace game asset entities/edges and verify FTS5 consistency."""
    t0 = time.perf_counter()
    icons_list: list[dict[str, Any]] = icons_cat.get("icons") or []
    models_list: list[dict[str, Any]] = models_cat.get("models") or []
    spine_list: list[dict[str, Any]] = models_cat.get("hero_skins_spine") or []
    maps_list: list[dict[str, Any]] = maps_cat.get("maps") or []
    core_map: dict[str, str] = hub_manifest.get("core") or {}

    core_by_sprite, heroes_by_sprite, items_by_sprite = _build_hub_reverse_maps(hub_manifest)

    by_sprite: dict[str, list[dict[str, Any]]] = {}
    by_cat_name: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in icons_list:
        by_sprite.setdefault((r.get("sprite_name") or "").lower(), []).append(r)
        en = (r.get("english_name") or r.get("clean_name") or "").lower()
        by_cat_name.setdefault((r.get("category") or "", en), []).append(r)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF")
    schema_info = inspect_sqlite_schema(conn)

    # Snapshot existing non-asset entities for accurate edge creation
    existing_xml_rows: dict[str, str] = {
        row[0]: row[1]
        for row in conn.execute("SELECT name, summary FROM entities WHERE layer = 'xml_row'")
    }
    existing_by_layer: dict[str, set[str]] = {}
    for elayer, ename in conn.execute(
        "SELECT layer, name FROM entities WHERE layer IN ('xml_table', 'datacenter', 'ui_window')"
    ):
        existing_by_layer.setdefault(elayer, set()).add(ename)
    existing_xml_tables = existing_by_layer.get("xml_table", set())
    existing_dcs = existing_by_layer.get("datacenter", set())
    existing_uis = existing_by_layer.get("ui_window", set())
    pre_total = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]

    try:
        conn.execute("BEGIN")

        # 1. Idempotently remove existing game asset entities + FTS5 entries + asset edges
        placeholders = ",".join("?" for _ in ASSET_LAYERS)
        old_rows = conn.execute(
            f"SELECT id, layer, domain, name, summary, body FROM entities WHERE layer IN ({placeholders})",
            ASSET_LAYERS,
        ).fetchall()

        if old_rows and schema_info["is_external_content"] and not schema_info["has_delete_trigger"]:
            conn.executemany(
                "INSERT INTO entities_fts(entities_fts, rowid, name, summary, body, layer, domain) "
                "VALUES('delete', ?, ?, ?, ?, ?, ?)",
                [(r[0], r[3], r[4], r[5], r[1], r[2]) for r in old_rows],
            )

        conn.execute(f"DELETE FROM entities WHERE layer IN ({placeholders})", ASSET_LAYERS)
        conn.execute(
            f"DELETE FROM edges WHERE src_layer IN ({placeholders}) OR dst_layer IN ({placeholders})",
            ASSET_LAYERS + ASSET_LAYERS,
        )

        # 2. Prepare entity records
        records: list[tuple[str, str, str, str, str, str]] = []

        # 2a. 17,049 game_icon entities
        for r in icons_list:
            season = strip_em_dashes(r.get("season") or "")
            season_source = strip_em_dashes(r.get("season_source") or "")
            category = strip_em_dashes(r.get("category") or "Misc")
            clean_name = strip_em_dashes(r.get("clean_name") or r.get("sprite_name") or "")
            english_name = strip_em_dashes(r.get("english_name") or "")
            sprite_name = strip_em_dashes(r.get("sprite_name") or "")
            rel_path = strip_em_dashes(r.get("relative_path") or "")
            filename = strip_em_dashes(r.get("filename") or "")
            xml_table = strip_em_dashes(r.get("xml_table") or "")
            xml_id = strip_em_dashes(r.get("xml_id") or "")
            source_bundle = strip_em_dashes(r.get("source_bundle") or "")
            unity_path = strip_em_dashes(r.get("unity_path") or "")
            asset_type = strip_em_dashes(r.get("asset_type") or "Sprite")
            ow = int(r.get("orig_width") or 0)
            oh = int(r.get("orig_height") or 0)
            cw = int(r.get("crop_width") or 0)
            ch = int(r.get("crop_height") or 0)
            fbytes = int(r.get("file_size_bytes") or 0)

            domain = ICON_CATEGORY_TO_DOMAIN.get(category, "core_engine")
            source_ref = f"assets/icons/{rel_path}"

            summary_parts = [
                season,
                category,
                f"sprite={sprite_name}",
                f"{ow}x{oh} (crop {cw}x{ch})",
            ]
            if xml_table and xml_id:
                summary_parts.append(f"xml={xml_table}#{xml_id}")
            elif xml_table:
                summary_parts.append(f"xml={xml_table}")
            if english_name and english_name.lower() != clean_name.lower():
                summary_parts.append(f"en={english_name}")
            summary = " | ".join(summary_parts)

            hub_notes: list[str] = []
            sp_low = sprite_name.lower()
            for hk in core_by_sprite.get(sp_low, []):
                hub_notes.append(f"hub_core={hk} launcher/assets/game icons/{hk}.webp")
            if sp_low in heroes_by_sprite:
                hids = ",".join(heroes_by_sprite[sp_low])
                hub_notes.append(
                    f"hub_hero_ids={hids} launcher/assets/game icons/heroes/{sprite_name}.webp"
                )
            if sp_low in items_by_sprite:
                iids = ",".join(items_by_sprite[sp_low][:12])
                hub_notes.append(
                    f"hub_item_ids={iids} launcher/assets/game icons/items/{sprite_name}.webp"
                )

            body_parts = [
                clean_name,
                english_name,
                sprite_name,
                season,
                season_source,
                category,
                source_ref,
                rel_path,
                filename,
                f"{xml_table}#{xml_id}" if (xml_table and xml_id) else xml_table,
                xml_table,
                xml_id,
                source_bundle,
                unity_path,
                asset_type,
                f"{ow}x{oh}",
                f"{cw}x{ch}",
                f"{fbytes}B",
                *hub_notes,
            ]
            body = " ".join(p for p in body_parts if p)
            records.append(("game_icon", domain, clean_name, summary, source_ref, body))

        # 2b. 493 game_model entities
        for m in models_list:
            season = strip_em_dashes(m.get("season") or "")
            season_source = strip_em_dashes(m.get("season_source") or "")
            faction = strip_em_dashes(m.get("faction") or "Buildings and Environment")
            model_name = strip_em_dashes(m.get("model_name") or m.get("english_name") or "")
            english_name = strip_em_dashes(m.get("english_name") or model_name)
            slug = strip_em_dashes(m.get("slug") or "")
            folder = strip_em_dashes(m.get("folder") or "")
            glb_file = strip_em_dashes(m.get("glb_file") or "")
            source_bundle = strip_em_dashes(m.get("source_bundle") or "")
            evidence_source = strip_em_dashes(m.get("evidence_source") or "")
            camp_id = m.get("camp_id")
            hero_id = m.get("hero_id")
            mesh_count = int(m.get("mesh_count") or 0)
            tex_count = int(m.get("texture_count") or 0)
            verts = int(m.get("total_vertices") or 0)
            faces = int(m.get("total_faces") or 0)
            anims = m.get("animation_clips") or []
            meshes = m.get("meshes") or []
            textures = m.get("textures") or []

            domain = MODEL_FACTION_TO_DOMAIN.get(faction, "core_engine")
            source_ref = f"models/{folder}/{glb_file}" if glb_file else f"models/{folder}/"

            summary_parts = [
                season,
                faction,
                f"slug={slug}",
                f"{mesh_count}m {verts:,}v {faces:,}f {tex_count}tex {len(anims)}anim",
            ]
            if hero_id is not None:
                summary_parts.append(f"hero_id={hero_id}")
            summary = " | ".join(summary_parts)

            obj_names = " ".join(strip_em_dashes(x.get("obj_file") or "") for x in meshes[:25])
            tex_names = " ".join(strip_em_dashes(t.get("name") or "") for t in textures[:25])
            anim_names = " ".join(strip_em_dashes(a) for a in anims[:30])
            body_parts = [
                model_name,
                english_name if english_name != model_name else "",
                slug,
                season,
                season_source,
                faction,
                f"camp_id={camp_id}" if camp_id is not None else "",
                f"hero_id={hero_id}" if hero_id is not None else "",
                source_ref,
                f"models/{folder}/",
                source_bundle,
                evidence_source,
                f"{verts} vertices {faces} faces {mesh_count} meshes {tex_count} textures",
                obj_names,
                tex_names,
                anim_names,
            ]
            body = " ".join(p for p in body_parts if p)
            records.append(("game_model", domain, model_name, summary, source_ref, body))

        # 2c. 47 hub_game_icon entities
        for key, sprite in core_map.items():
            sprite_clean = strip_em_dashes(sprite)
            domain = HUB_CORE_TO_DOMAIN.get(key, "core_engine")
            webp_path = HUB_ICONS_DIR / f"{key}.webp"
            webp_bytes = webp_path.stat().st_size if webp_path.exists() else 0
            source_ref = f"launcher/assets/game icons/{key}.webp"

            icon_hit = _pick_best_icon(by_sprite.get(sprite.lower(), []))
            if icon_hit:
                ic_season = strip_em_dashes(icon_hit.get("season") or "")
                ic_cat = strip_em_dashes(icon_hit.get("category") or "")
                ic_clean = strip_em_dashes(icon_hit.get("clean_name") or "")
                ic_en = strip_em_dashes(icon_hit.get("english_name") or "")
                ic_rel = strip_em_dashes(icon_hit.get("relative_path") or "")
                ic_xml_t = strip_em_dashes(icon_hit.get("xml_table") or "")
                ic_xml_i = strip_em_dashes(icon_hit.get("xml_id") or "")
                ic_bundle = strip_em_dashes(icon_hit.get("source_bundle") or "")
                ic_unity = strip_em_dashes(icon_hit.get("unity_path") or "")
                summary = (
                    f"Hub Core Sprite | key={key} | sprite={sprite_clean} | "
                    f"{ic_season} | {ic_cat} | en={ic_clean} | {webp_bytes:,}B"
                )
                body = " ".join(
                    p
                    for p in [
                        key,
                        sprite_clean,
                        source_ref,
                        "launcher/assets/game icons/manifest.json",
                        ic_clean,
                        ic_en,
                        ic_season,
                        ic_cat,
                        f"assets/icons/{ic_rel}",
                        f"{ic_xml_t}#{ic_xml_i}" if (ic_xml_t and ic_xml_i) else ic_xml_t,
                        ic_bundle,
                        ic_unity,
                        f"{webp_bytes}B",
                    ]
                    if p
                )
            else:
                summary = f"Hub Core Sprite | key={key} | sprite={sprite_clean} | {webp_bytes:,}B"
                body = f"{key} {sprite_clean} {source_ref} launcher/assets/game icons/manifest.json {webp_bytes}B"

            records.append(("hub_game_icon", domain, key, summary, source_ref, body))

        # 2d. 110 hero_skin_spine entities (2D Spine Hero Skins)
        for s in spine_list:
            season = strip_em_dashes(s.get("season") or "")
            season_source = strip_em_dashes(s.get("season_source") or "")
            faction = strip_em_dashes(s.get("faction") or "Blood Rose")
            hero_name = strip_em_dashes(s.get("hero_name") or "")
            skin_name = strip_em_dashes(s.get("skin_name") or "")
            display_name = strip_em_dashes(s.get("display_name") or f"{hero_name} - {skin_name}")
            skin_category = strip_em_dashes(s.get("skin_category") or "default")
            folder = strip_em_dashes(s.get("folder") or "")
            prefab_name = strip_em_dashes(s.get("prefab_name") or "")
            source_bundle = strip_em_dashes(s.get("source_bundle") or "")
            resolved_bundle = strip_em_dashes(s.get("resolved_external_bundle") or "")
            evidence_source = strip_em_dashes(s.get("evidence_source") or "")
            mesh_analysis = strip_em_dashes(s.get("mesh_analysis") or "")
            exclusive_weapon = strip_em_dashes(s.get("exclusive_weapon_name") or "")
            camp_id = s.get("camp_id")
            hero_id = s.get("hero_id")
            skin_id = s.get("skin_id")
            shop_id = s.get("shop_id")
            tex_count = int(s.get("texture_count") or 0)
            spine_count = int(s.get("spine_file_count") or 0)
            atlas_textures = s.get("atlas_textures") or []
            spine_files = s.get("spine_files") or []
            exported_files = s.get("exported_files") or []

            domain = MODEL_FACTION_TO_DOMAIN.get(faction, "heroes_skills_equip")
            source_ref = f"models/{folder}/"

            summary_parts = [
                season,
                faction,
                f"cat={skin_category}",
                f"hero={hero_name}",
                f"skin={skin_name}",
                f"{tex_count}png {spine_count}spine",
            ]
            if hero_id is not None:
                summary_parts.append(f"hero_id={hero_id}")
            if skin_id is not None:
                summary_parts.append(f"skin_id={skin_id}")
            if shop_id is not None:
                summary_parts.append(f"shop_id={shop_id}")
            if exclusive_weapon:
                summary_parts.append(f"weapon={exclusive_weapon}")
            summary = " | ".join(summary_parts)

            atlas_tokens = " ".join(
                f"{strip_em_dashes(t.get('name') or '')} {strip_em_dashes(t.get('file') or '')}"
                for t in atlas_textures
            )
            spine_tokens = " ".join(
                f"{strip_em_dashes(f.get('name') or '')} {strip_em_dashes(f.get('file') or '')}"
                for f in spine_files
            )
            exported_tokens = " ".join(strip_em_dashes(ef) for ef in exported_files)
            body_parts = [
                display_name,
                hero_name,
                skin_name,
                skin_category,
                "2d_spine_hero_skin Hero Skins 2D Spine",
                season,
                season_source,
                faction,
                f"camp_id={camp_id}" if camp_id is not None else "",
                f"hero_id={hero_id}" if hero_id is not None else "",
                f"skin_id={skin_id}" if skin_id is not None else "",
                f"shop_id={shop_id}" if shop_id is not None else "",
                exclusive_weapon,
                prefab_name,
                source_ref,
                folder,
                source_bundle,
                resolved_bundle,
                evidence_source,
                mesh_analysis,
                atlas_tokens,
                spine_tokens,
                exported_tokens,
            ]
            body = " ".join(p for p in body_parts if p)
            records.append(("hero_skin_spine", domain, display_name, summary, source_ref, body))

        # 2e. 499 game_map entities (World, Seasonal, Event, City/Base & Terrain Maps)
        map_xml_refs_by_ref: dict[str, list[str]] = {}
        map_records_meta: list[tuple[dict[str, Any], str]] = []
        for m in maps_list:
            title = strip_em_dashes(m.get("title") or "")
            category = strip_em_dashes(m.get("category") or "Main World Maps")
            subcategory = strip_em_dashes(m.get("subcategory") or "")
            season = strip_em_dashes(m.get("season") or "All Seasons")
            rel_path = strip_em_dashes(m.get("relative_path") or "")
            width = int(m.get("width") or 0)
            height = int(m.get("height") or 0)
            resolution = strip_em_dashes(m.get("resolution") or f"{width}x{height}")
            source_bundle = strip_em_dashes(m.get("source_bundle") or "")
            source_assets = strip_em_dashes(m.get("source_assets") or "")
            asset_type = strip_em_dashes(m.get("asset_type") or "")
            notes = strip_em_dashes(m.get("notes") or "")

            domain = MAP_SUBCATEGORY_TO_DOMAIN.get(
                subcategory, MAP_CATEGORY_TO_DOMAIN.get(category, "formations_marches_world")
            )
            source_ref = f"maps/{rel_path}"
            xml_refs = _infer_map_xml_refs(m)
            map_xml_refs_by_ref[source_ref] = xml_refs
            map_records_meta.append((m, source_ref))

            summary_parts = [
                season,
                f"{category} / {subcategory}" if subcategory else category,
                resolution,
                asset_type,
            ]
            if xml_refs:
                summary_parts.append(f"xml={','.join(xml_refs[:4])}")
            if notes:
                summary_parts.append(notes)
            summary = " | ".join(p for p in summary_parts if p)

            extra_tokens = []
            if subcategory == "Province Zones":
                extra_tokens.append("Provinces")
            if "4K" in title or resolution == "4096x4096":
                extra_tokens.append("4K")

            body_parts = [
                title,
                category,
                subcategory,
                season,
                source_ref,
                rel_path,
                resolution,
                f"{width}x{height}",
                f"{width} {height}",
                source_bundle,
                source_assets,
                asset_type,
                notes,
                " ".join(xml_refs),
                *extra_tokens,
            ]
            body = " ".join(p for p in body_parts if p)
            records.append(("game_map", domain, title, summary, source_ref, body))

        # Insert entities + manual FTS5 sync if external-content without trigger
        cur = conn.cursor()
        need_manual_fts = schema_info["is_external_content"] and not schema_info["has_insert_trigger"]
        for rec in records:
            layer, domain, name, summary, source_ref, body = rec
            cur.execute(
                "INSERT INTO entities(layer, domain, name, summary, source_ref, body) VALUES(?, ?, ?, ?, ?, ?)",
                (layer, domain, name, summary, source_ref, body),
            )
            if need_manual_fts:
                rowid = cur.lastrowid
                cur.execute(
                    "INSERT INTO entities_fts(rowid, name, summary, body, layer, domain) VALUES(?, ?, ?, ?, ?, ?)",
                    (rowid, name, summary, body, layer, domain),
                )

        # 3. Build unambiguous cross-system edges
        edges_set: set[tuple[str, str, str, str, str]] = set()

        # 3a. Hub core sprites -> extracted game_icon
        for key, sprite in core_map.items():
            icon_hit = _pick_best_icon(by_sprite.get(sprite.lower(), []))
            if icon_hit:
                edges_set.add(
                    ("hub_game_icon", key, "uses_sprite", "game_icon", f"assets/icons/{icon_hit['relative_path']}")
                )

        # 3b. Playable Heroes -> game_model + game_icon (round, fullbody, fragment)
        hero_model_names: set[str] = set()
        for h in models_cat.get("hero_to_season_faction_table") or []:
            hid = str(h["hero_id"])
            mname = strip_em_dashes(h["english_name"])
            hero_model_names.add(mname)
            base_name = (
                mname.replace(" Awakened", "")
                .replace(" Bear Companion", "")
                .replace(" Horse Stampede", "")
                .replace(" Tactical", "")
            )

            if f"heroes#{hid}" in existing_xml_rows:
                edges_set.add(("xml_row", f"heroes#{hid}", "has_3d_model", "game_model", mname))
            if f"lw_heroes#{hid}" in existing_xml_rows:
                edges_set.add(("xml_row", f"lw_heroes#{hid}", "has_3d_model", "game_model", mname))

            row = anh_rows.get(hid, {})
            r_sp = row.get("round_hero_icon") or ""
            p_id = (row.get("hero_pieces") or "").split("|")[0]
            f_sp = (goods_rows.get(p_id) or {}).get("icon", "")

            r_ic = None
            if mname.endswith("Awakened"):
                # Prefer Awakened portrait if extracted
                r_ic = _pick_best_icon(
                    [
                        c
                        for c in by_cat_name.get(("Hero Portraits Round", f"{base_name.lower()} - awakened appearance"), [])
                    ],
                    require_name_substr=base_name,
                )
            if r_ic is None and r_sp:
                r_ic = _pick_best_icon(by_sprite.get(r_sp.lower(), []), require_name_substr=base_name)
            if r_ic is None:
                r_ic = _pick_best_icon(
                    by_cat_name.get(("Hero Portraits Round", base_name.lower()), []),
                    require_name_substr=base_name,
                )
            if r_ic:
                r_path = f"assets/icons/{r_ic['relative_path']}"
                edges_set.add(("game_model", mname, "has_round_icon", "game_icon", r_path))
                if f"heroes#{hid}" in existing_xml_rows and not mname.endswith(("Awakened", "Companion", "Stampede")):
                    edges_set.add(("xml_row", f"heroes#{hid}", "has_round_icon", "game_icon", r_path))

            fb_ic = _pick_best_icon(
                by_cat_name.get(("Hero Fullbody", base_name.lower()), []),
                require_name_substr=base_name,
            )
            if fb_ic and not mname.endswith(("Companion", "Stampede")):
                edges_set.add(
                    ("game_model", mname, "has_fullbody_icon", "game_icon", f"assets/icons/{fb_ic['relative_path']}")
                )

            frag_ic = _pick_best_icon(by_sprite.get(f_sp.lower(), []), require_name_substr=base_name) if f_sp else None
            if frag_ic is None:
                frag_ic = _pick_best_icon(
                    by_cat_name.get(("Hero Fragments", f"{base_name.lower()} fragment"), []),
                    require_name_substr=base_name,
                )
            if frag_ic and not mname.endswith(("Companion", "Stampede")):
                edges_set.add(
                    ("game_model", mname, "has_fragment_icon", "game_icon", f"assets/icons/{frag_ic['relative_path']}")
                )

        # 3c. Hero Weapons -> Playable Hero game_model
        sorted_hero_names = sorted(hero_model_names, key=len, reverse=True)
        for m in models_list:
            if m.get("faction") != "Weapons":
                continue
            wname = strip_em_dashes(m.get("model_name") or "")
            for hname in sorted_hero_names:
                if " " not in hname and wname.startswith(f"{hname} "):
                    edges_set.add(("game_model", wname, "equipped_by", "game_model", hname))
                    break

        # 3d. Unambiguous xml_row monsters -> game_model
        model_by_lower: dict[str, list[str]] = {}
        for m in models_list:
            mn = strip_em_dashes(m.get("model_name") or "")
            model_by_lower.setdefault(mn.lower(), []).append(mn)
        for xname, xsummary in existing_xml_rows.items():
            if not xname.startswith("monsters#"):
                continue
            title = xsummary.split("|", 1)[0].strip().lower()
            matches = model_by_lower.get(title, [])
            if len(matches) == 1:
                edges_set.add(("xml_row", xname, "has_3d_model", "game_model", matches[0]))

        # 3e. Unambiguous xml_row -> game_icon (when XML table/ID and English title match)
        best_xml_icon: dict[str, dict[str, Any]] = {}
        for r in icons_list:
            xt = r.get("xml_table") or ""
            xi = r.get("xml_id") or ""
            mapped = XML_TABLE_TO_SQL_PREFIX.get(xt)
            if not mapped or not xi:
                continue
            xkey = f"{mapped}#{xi}"
            if xkey not in existing_xml_rows:
                continue
            xtitle = existing_xml_rows[xkey].split("|", 1)[0].strip()
            iname = strip_em_dashes(r.get("english_name") or r.get("clean_name") or "")
            if not xtitle or not iname:
                continue
            t_low, i_low = xtitle.lower(), iname.lower()
            if t_low == i_low or t_low in i_low or i_low in t_low or (
                _norm_tokens(t_low) and _norm_tokens(t_low).issubset(_norm_tokens(i_low))
            ):
                cur_best = best_xml_icon.get(xkey)
                if cur_best is None:
                    best_xml_icon[xkey] = r
                else:
                    picked = _pick_best_icon([cur_best, r])
                    if picked is not None:
                        best_xml_icon[xkey] = picked
        for xkey, r in best_xml_icon.items():
            edges_set.add(("xml_row", xkey, "has_icon", "game_icon", f"assets/icons/{r['relative_path']}"))

        # 3f. HQ Skins & Vehicle Skins -> game_icon
        for m in models_list:
            fac = m.get("faction") or ""
            mn = strip_em_dashes(m.get("model_name") or "")
            if fac == "HQ Skins":
                base = re.sub(
                    r"(?:\s+(?:World|Tier 1|Tier 2|S3|HQ|Pedestal|Event|Snowman))+$",
                    "",
                    mn,
                    flags=re.IGNORECASE,
                ).strip()
                hq_ic = _pick_best_icon(
                    by_cat_name.get(("Buildings", f"{base.lower()} (permanent)"), [])
                    or by_cat_name.get(("Buildings", base.lower()), [])
                    or by_cat_name.get(("Items", base.lower()), [])
                )
                if hq_ic:
                    edges_set.add(
                        ("game_model", mn, "has_icon", "game_icon", f"assets/icons/{hq_ic['relative_path']}")
                    )
            elif fac == "Vehicle Skins":
                base = re.sub(
                    r"(?:\s+(?:Showcase|Stage|World|Classic|Tier 1))+$",
                    "",
                    mn,
                    flags=re.IGNORECASE,
                ).strip()
                veh_ic = _pick_best_icon(
                    by_cat_name.get(("Vehicles and Aircraft", base.lower()), [])
                    or by_cat_name.get(("Monsters and Bosses", base.lower()), [])
                )
                if veh_ic:
                    edges_set.add(
                        ("game_model", mn, "has_icon", "game_icon", f"assets/icons/{veh_ic['relative_path']}")
                    )

        # 3g. 110 hero_skin_spine -> xml_row + game_model + game_icon
        hero_models_by_id: dict[str, list[str]] = {}
        for m in models_list:
            if m.get("hero_id") is not None:
                hero_models_by_id.setdefault(str(m["hero_id"]), []).append(
                    strip_em_dashes(m.get("model_name") or "")
                )

        generic_skin_names = {
            "default",
            "default me",
            "stage battle",
            "exclusive weapon",
            "awakening",
            "awakened exclusive weapon",
            "outfit 5",
        }
        for s in spine_list:
            display_name = strip_em_dashes(s.get("display_name") or "")
            faction = strip_em_dashes(s.get("faction") or "")
            hero_name = strip_em_dashes(s.get("hero_name") or "")
            skin_name = strip_em_dashes(s.get("skin_name") or "")
            skin_category = strip_em_dashes(s.get("skin_category") or "")
            hid = str(s["hero_id"]) if s.get("hero_id") is not None else ""
            ew_name = strip_em_dashes(s.get("exclusive_weapon_name") or "")

            if faction == "NPCs and Survivors":
                matches = model_by_lower.get(hero_name.lower(), [])
                if len(matches) == 1:
                    edges_set.add(("hero_skin_spine", display_name, "skin_for_model", "game_model", matches[0]))
                continue

            if hid:
                if f"heroes#{hid}" in existing_xml_rows:
                    edges_set.add(("xml_row", f"heroes#{hid}", "has_spine_skin", "hero_skin_spine", display_name))
                if f"lw_heroes#{hid}" in existing_xml_rows:
                    edges_set.add(("xml_row", f"lw_heroes#{hid}", "has_spine_skin", "hero_skin_spine", display_name))

            cands = [c for c in hero_models_by_id.get(hid, []) if not c.endswith(("Companion", "Stampede"))]
            target_model = ""
            if skin_category in ("awakening", "awakened_exclusive_weapon"):
                awak_cands = [c for c in cands if c.endswith("Awakened")]
                if awak_cands:
                    target_model = awak_cands[0]
            if not target_model:
                base_cands = [c for c in cands if not c.endswith("Awakened")]
                if base_cands:
                    target_model = base_cands[0]
            if target_model:
                edges_set.add(("hero_skin_spine", display_name, "skin_for_model", "game_model", target_model))

            if skin_name.lower() not in generic_skin_names:
                fb_ic = _pick_best_icon(
                    by_cat_name.get(("Hero Fullbody", display_name.lower()), [])
                    or by_cat_name.get(("Hero Fullbody", skin_name.lower()), [])
                )
                if fb_ic:
                    edges_set.add(
                        (
                            "hero_skin_spine",
                            display_name,
                            "has_fullbody_icon",
                            "game_icon",
                            f"assets/icons/{fb_ic['relative_path']}",
                        )
                    )

            r_ic = _pick_best_icon(by_cat_name.get(("Hero Portraits Round", display_name.lower()), []))
            if r_ic:
                edges_set.add(
                    (
                        "hero_skin_spine",
                        display_name,
                        "has_round_icon",
                        "game_icon",
                        f"assets/icons/{r_ic['relative_path']}",
                    )
                )

            if ew_name:
                ew_ic = _pick_best_icon(by_cat_name.get(("Hero Equipment", ew_name.lower()), []))
                if ew_ic:
                    edges_set.add(
                        (
                            "hero_skin_spine",
                            display_name,
                            "has_weapon_icon",
                            "game_icon",
                            f"assets/icons/{ew_ic['relative_path']}",
                        )
                    )
                if hid:
                    for suffix in ("00", "000"):
                        sp_key = f"hero_sp_equips#{hid}{suffix}"
                        if sp_key in existing_xml_rows and ew_name.lower() in existing_xml_rows[sp_key].lower():
                            edges_set.add(("hero_skin_spine", display_name, "has_weapon_xml", "xml_row", sp_key))
                            break

        # 3h. Landmark & primary game_map -> xml_table / datacenter / ui_window / mirror edges
        maps_by_title: dict[str, list[tuple[dict[str, Any], str]]] = {}
        for m_obj, m_ref in map_records_meta:
            maps_by_title.setdefault(strip_em_dashes(m_obj.get("title") or ""), []).append((m_obj, m_ref))

        for title_key, entries in maps_by_title.items():
            if len(entries) == 2:
                main_ref = next((ref for obj, ref in entries if obj.get("category") == "Main World Maps"), "")
                seas_ref = next((ref for obj, ref in entries if obj.get("category") == "Seasonal Maps"), "")
                if main_ref and seas_ref:
                    edges_set.add(("game_map", main_ref, "mirrors_map", "game_map", seas_ref))

        raw_to_topo_pairs = [
            ("Pre-Season 1 Topology Raw 1K", "Pre-Season 1 Topology Map"),
            ("Season 2 Wastes Watcher Topology Raw 1K", "Season 2 Wastes Watcher Topology Map"),
            ("Season 3 Everfrost Era Topology Raw 1K", "Season 3 Everfrost Era Topology Map"),
            ("Season 4 Dinosaur Origin Topology Raw 1K", "Season 4 Dinosaur Origin Topology Map"),
            ("Season 5 Moonlit Elegy Topology Raw 1K", "Season 5 Moonlit Elegy Topology Map"),
            ("Season 6 World Topology Raw 1600", "Season 6 World Topology Map"),
        ]
        for raw_title, topo_title in raw_to_topo_pairs:
            raw_ref = next((ref for _, ref in maps_by_title.get(raw_title, [])), "")
            topo_ref = next(
                (ref for obj, ref in maps_by_title.get(topo_title, []) if obj.get("category") == "Seasonal Maps"),
                "",
            )
            if raw_ref and topo_ref:
                edges_set.add(("game_map", raw_ref, "raw_bitmap_of", "game_map", topo_ref))

        landmark_titles = {
            "Main World Map 4K",
            "World Zones and Provinces Map",
            "Pre-Season 1 Topology Map",
            "Season 2 Wastes Watcher Topology Map",
            "Season 2 Desert Resource Tiers Map",
            "Season 3 Everfrost World Map 4K",
            "Season 3 Everfrost Era Topology Map",
            "Season 4 Dinosaur Origin World Map 4K",
            "Season 4 Dinosaur Origin Topology Map",
            "Season 5 Moonlit Elegy Topology Map",
            "Season 6 World Topology Map",
            "Volcano War Tactical Map Annotated",
            "Volcano War Map",
            "Volcano War Main Battlefield Background",
            "Desert Battlefield Resource Tiers Map",
            "Castle Adventure Map",
            "Castle Adventure Map Base",
            "Castle Adventure Dig Grid Map",
            "Landing Operations Full Map",
            "Landing Operations All Stages Overview",
            "Capital War Battlefield View 01",
            "Capital War Guide Map",
            "Cross Server War Battle Background",
            "World Siege Main Battlefield Background",
            "Gold Mine Event Map 01",
            "Season Mine Event Background",
            "World Cup Stadium Preview",
            "Dispatch World Map 01",
            "Main City Inner Ground 01",
            "Main City Inner Ground 02",
            "Main City Outer Ground",
            "Base District Expansion 01",
            "Season 3 Ice Cave Main Map",
            "Season 4 World Boss Arena Map",
        }
        subcat_to_dcs: dict[str, tuple[str, ...]] = {
            "Volcano War": ("DataCenter.VolcanoWarManager",),
            "Desert Battlefield": ("DataCenter.DesertDataManager",),
            "Castle Adventure": ("DataCenter.CastleAdventureManager",),
            "Landing Operations": ("DataCenter.LandingOperationsDataManager",),
            "Cross Server War": ("DataCenter.CrossWonderManager",),
            "Mine Events": ("DataCenter.MineCaveManager",),
            "Main City Ground": ("DataCenter.MainCityAreaDataManager",),
            "Base Expansion Districts": ("DataCenter.LandLockManager",),
            "Decoded World Map": ("DataCenter.SeasonDataManager",),
            "Stitched 4K World Map": ("DataCenter.SeasonDataManager",),
        }
        subcat_to_uis: dict[str, tuple[str, ...]] = {
            "Volcano War": ("UIVolcanoGuideWindow",),
            "Desert Battlefield": ("UIDesertOperate",),
            "Castle Adventure": ("CastleAdventureMap",),
            "Landing Operations": ("UILoMap",),
            "Cross Server War": ("UICrossWonderAct",),
            "World Siege": ("UIWorldSiegePoint",),
            "Mine Events": ("UIMineCaveUnlock",),
            "World Cup": ("WorldCupZombieBossComingPanel",),
            "Base Expansion Districts": ("UILandLockTips",),
            "Decoded World Map": ("UIMainMiniMap", "UISeasonEntrance"),
            "Stitched 4K World Map": ("UIMainMiniMap",),
        }

        for m_obj, m_ref in map_records_meta:
            m_title = strip_em_dashes(m_obj.get("title") or "")
            m_cat = strip_em_dashes(m_obj.get("category") or "")
            m_sub = strip_em_dashes(m_obj.get("subcategory") or "")
            is_primary_seasonal = (
                m_cat == "Seasonal Maps" and "Raw" not in m_title and "Quadrant" not in m_title
            )
            if m_title not in landmark_titles and not is_primary_seasonal:
                continue

            for xt in map_xml_refs_by_ref.get(m_ref, []):
                if xt in existing_xml_tables:
                    edges_set.add(("game_map", m_ref, "uses_xml_table", "xml_table", xt))
            for dc_name in subcat_to_dcs.get(m_sub, ()):
                if dc_name in existing_dcs:
                    edges_set.add(("game_map", m_ref, "linked_dc", "datacenter", dc_name))
            for ui_name in subcat_to_uis.get(m_sub, ()):
                if ui_name in existing_uis:
                    edges_set.add(("game_map", m_ref, "used_by_ui", "ui_window", ui_name))
            if m_title == "Season 2 Desert Resource Tiers Map" and "DataCenter.DesertDataManager" in existing_dcs:
                edges_set.add(("game_map", m_ref, "linked_dc", "datacenter", "DataCenter.DesertDataManager"))

        sorted_edges = sorted(edges_set)
        conn.executemany(
            "INSERT INTO edges(src_layer, src_name, relation, dst_layer, dst_name) VALUES(?, ?, ?, ?, ?)",
            sorted_edges,
        )

        # 4. Update meta table
        total_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('entity_count', ?)", (str(total_entities),))
        conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('edge_count', ?)", (str(total_edges),))
        conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('assets_indexed_utc', ?)", (now_utc,))

        conn.commit()
    except Exception:
        conn.rollback()
        raise

    conn.execute("INSERT INTO entities_fts(entities_fts) VALUES('optimize')")
    conn.commit()
    if old_rows:
        conn.execute("VACUUM")

    # 5. Verify PRAGMA integrity_check and FTS5 consistency
    integ = conn.execute("PRAGMA integrity_check").fetchall()
    if integ != [("ok",)]:
        conn.close()
        raise RuntimeError(f"SQLite PRAGMA integrity_check failed: {integ}")

    conn.execute("INSERT INTO entities_fts(entities_fts) VALUES('integrity-check')")
    cnt_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    cnt_fts = conn.execute("SELECT COUNT(*) FROM entities_fts").fetchone()[0]
    cnt_docsize = conn.execute("SELECT COUNT(*) FROM entities_fts_docsize").fetchone()[0]
    cnt_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    layer_counts = dict(
        conn.execute(
            f"SELECT layer, COUNT(*) FROM entities WHERE layer IN ({placeholders}) GROUP BY layer",
            ASSET_LAYERS,
        ).fetchall()
    )
    conn.close()

    if not (cnt_entities == cnt_fts == cnt_docsize):
        raise RuntimeError(
            f"FTS5 count mismatch: entities={cnt_entities}, entities_fts={cnt_fts}, docsize={cnt_docsize}"
        )

    elapsed = time.perf_counter() - t0
    return {
        "pre_existing_entities": pre_total,
        "removed_old_asset_entities": len(old_rows),
        "inserted_game_icons": layer_counts.get("game_icon", 0),
        "inserted_game_models": layer_counts.get("game_model", 0),
        "inserted_hub_game_icons": layer_counts.get("hub_game_icon", 0),
        "inserted_hero_skins_spine": layer_counts.get("hero_skin_spine", 0),
        "inserted_game_maps": layer_counts.get("game_map", 0),
        "inserted_asset_edges": len(sorted_edges),
        "total_entities": cnt_entities,
        "total_fts_rows": cnt_fts,
        "total_fts_docsize": cnt_docsize,
        "total_edges": cnt_edges,
        "integrity_check": "ok",
        "elapsed_seconds": round(elapsed, 3),
    }


def main() -> int:
    for p in (ICONS_CATALOG_PATH, MODELS_CATALOG_PATH, MAPS_CATALOG_PATH, HUB_MANIFEST_PATH, DB_PATH):
        if not p.exists():
            raise FileNotFoundError(f"Required input missing: {p}")

    icons_cat = json.loads(ICONS_CATALOG_PATH.read_text(encoding="utf-8"))
    models_cat = json.loads(MODELS_CATALOG_PATH.read_text(encoding="utf-8"))
    maps_cat = json.loads(MAPS_CATALOG_PATH.read_text(encoding="utf-8"))
    hub_manifest = json.loads(HUB_MANIFEST_PATH.read_text(encoding="utf-8"))
    anh_rows = _load_xml_rows_map(XML_HEROES_PATH)
    goods_rows = _load_xml_rows_map(XML_GOODS_PATH)

    manifest_doc = build_raw_manifest(icons_cat, models_cat, maps_cat, hub_manifest, anh_rows, goods_rows)
    stats = update_sqlite_index(icons_cat, models_cat, maps_cat, hub_manifest, anh_rows, goods_rows)

    print("=== MEGAMIND GAME ASSETS INDEX UPDATED ===")
    print(f"Raw manifest         : {RAW_ASSET_MANIFEST_PATH} ({RAW_ASSET_MANIFEST_PATH.stat().st_size:,} bytes)")
    print(f"SQLite database      : {DB_PATH} ({DB_PATH.stat().st_size / (1024 * 1024):.2f} MB)")
    print(f"Removed old rows     : {stats['removed_old_asset_entities']:,}")
    print(f"game_icon rows       : {stats['inserted_game_icons']:,}")
    print(f"game_model rows      : {stats['inserted_game_models']:,}")
    print(f"hero_skin_spine rows : {stats['inserted_hero_skins_spine']:,}")
    print(f"hub_game_icon rows   : {stats['inserted_hub_game_icons']:,}")
    print(f"game_map rows        : {stats['inserted_game_maps']:,}")
    print(f"Asset edges added    : {stats['inserted_asset_edges']:,}")
    print(f"Total entities       : {stats['total_entities']:,} (FTS5={stats['total_fts_rows']:,}, docsize={stats['total_fts_docsize']:,})")
    print(f"Total edges          : {stats['total_edges']:,}")
    print(f"PRAGMA integrity     : {stats['integrity_check']}")
    print(f"Hub manifest pack    : {manifest_doc['summary']['hub_sprites_total_webp']} WebPs (47 core + 35 heroes + 115 items)")
    print(f"Elapsed              : {stats['elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
