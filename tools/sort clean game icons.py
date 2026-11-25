#!/usr/bin/env python3
"""
Reorganize extracted Last Z edge-to-edge PNG icons by Season and clean Category.

Features:
- Reads existing verified assets/icons/icons_catalog.json (no AssetBundle re-extraction).
- Resolves official Last Z Seasons (Pre-Season 1, Season 1..6) using game XML tables under
  megamind/raw/xml tables/ (explicitly distinguishing 0-based world_season tables where
  world_season + 1 = official Season from 1-based hero/item season tables), guarded sprite
  tags, verified seasonal Unity paths/bundles, and official season theme names.
- Maps all 22 categories to clean space-separated Title Case folder names (zero underscores).
- Generates concise, real English display filenames (<= 55 chars before .png) with ZERO
  underscores and ZERO em dashes anywhere under assets/icons/.
- Resolves case-insensitive collisions on Windows by pixel area descending so the highest-res
  icon gets <Name>.png and variants get <Name> (2).png, <Name> (3).png, etc.
- Defaults to --dry-run; pass --apply to execute moves, clean old directories/catalogs, and
  write Icons Catalog.json, Icons Catalog.csv, and README.md.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths and Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(r".")
ICONS_ROOT = PROJECT_ROOT / "assets" / "icons"
OLD_CATALOG_JSON = ICONS_ROOT / "icons_catalog.json"
OLD_CATALOG_CSV = ICONS_ROOT / "icons_catalog.csv"
NEW_CATALOG_JSON = ICONS_ROOT / "Icons Catalog.json"
NEW_CATALOG_CSV = ICONS_ROOT / "Icons Catalog.csv"
README_PATH = ICONS_ROOT / "README.md"

XML_TABLES_DIR = PROJECT_ROOT / "megamind" / "raw" / "xml tables"
LOCALIZATION_JSON_PATH = PROJECT_ROOT / "megamind" / "raw" / "localization en.json"
ENGLISH_DIALOG_PATH = PROJECT_ROOT / "launcher" / "assets" / "english-dialog.txt"

SEASON_BUCKETS = [
    "Pre-Season 1",
    "Season 1",
    "Season 2",
    "Season 3",
    "Season 4",
    "Season 5",
    "Season 6",
]

SEASON_NUM_TO_BUCKET = {
    0: "Pre-Season 1",
    1: "Season 1",
    2: "Season 2",
    3: "Season 3",
    4: "Season 4",
    5: "Season 5",
    6: "Season 6",
}

CATEGORY_MAP: dict[str, str] = {
    "resources": "Resources",
    "items": "Items",
    "hero_portraits_round": "Hero Portraits Round",
    "hero_portraits_small": "Hero Portraits Small",
    "hero_portraits_large": "Hero Portraits Large",
    "hero_fullbody": "Hero Fullbody",
    "hero_fragments": "Hero Fragments",
    "hero_medals": "Hero Medals",
    "hero_equipment": "Hero Equipment",
    "skills": "Skills",
    "science_and_tech": "Science and Tech",
    "buildings": "Buildings",
    "troops_and_soldiers": "Troops and Soldiers",
    "vehicles_and_aircraft": "Vehicles and Aircraft",
    "monsters_and_bosses": "Monsters and Bosses",
    "activities_and_events": "Activities and Events",
    "alliance_and_world": "Alliance and World",
    "flags": "Flags",
    "emojis": "Emojis",
    "collectibles_and_fishing": "Collectibles and Fishing",
    "ui_hud": "UI HUD",
    "misc": "Misc",
}

CATEGORY_ORDER = list(CATEGORY_MAP.values())

MAX_STEM_LEN = 55

RESERVED_WIN_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}

ROMAN_UNICODE_MAP = {
    "\u2160": " I",
    "\u2161": " II",
    "\u2162": " III",
    "\u2163": " IV",
    "\u2164": " V",
    "\u2165": " VI",
    "\u2166": " VII",
    "\u2167": " VIII",
    "\u2168": " IX",
    "\u2169": " X",
}

# Internal dev/pinyin english_name values discovered in icons_catalog.json
DEV_ENGLISH_NAME_OVERRIDES: dict[str, str] = {
    "seaon_res": "",
    "season_res0": "",
    "season_res13": "",
    "season_specialization": "Season Specialization",
    "season_specialization2": "Season Specialization Talent",
    "beauty02": "",
    "beauty03": "",
    "people1": "Worker Build",
    "people2": "Worker Train",
    "people3": "Worker Treatment",
    "people_token": "Survivor Token",
    "chengjian": "City Construction",
    "ziyuan": "Resources",
    "xingmen": "Stargate",
    "jinzita": "Pyramid",
    "zhaiyue": "Ramadan",
    "valentine_box": "Valentine Box",
    "valentine_ring": "Valentine Ring",
    "car_chips": "Vehicle Chips",
    "car_part1": "Vehicle Part 1",
    "car_part2": "Vehicle Part 2",
    "cyber_week": "Cyber Week",
    "ying_weapon": "Hero Weapon",
    "mid_autumn": "Mid-Autumn",
    "weekend_select": "Weekend Select",
    "turkey_2025": "Thanksgiving Turkey 2025",
    "turkeyfood_2025": "Thanksgiving Feast 2025",
    "summer_food": "Summer Feast",
    "firstpay_1": "First Recharge",
    "buildbuilding": "Building Construction",
    "children1": "Children's Day Card 1",
    "children2": "Children's Day Card 2",
    "equipment": "Equipment",
    "equipment2": "Equipment 2",
    "exp": "EXP",
    "fullmoon": "Full Moon",
    "diwali": "Diwali",
    "holi": "Holi",
    "newyear": "New Year",
    "summer": "Summer",
    "tech": "Tech",
    "training": "Training",
    "scientific": "Research",
    "treasure": "Treasure",
    "alliance center must be placed.": "Season Alliance Center",
    "alliance center must be placed": "Season Alliance Center",
}

# Additional short flag code names not matched in initial extraction
EXTRA_FLAG_NAMES: dict[str, str] = {
    "eng": "England",
    "sct": "Scotland",
    "sco": "Scotland",
    "wls": "Wales",
    "nir": "Northern Ireland",
    "sam": "Samoa",
    "ukl": "United Kingdom",
    "yu": "Yugoslavia",
    "usa": "United States",
    "gbr": "United Kingdom",
    "uae": "United Arab Emirates",
    "kor": "South Korea",
    "jpn": "Japan",
    "chn": "China",
    "fra": "France",
    "deu": "Germany",
    "ger": "Germany",
    "esp": "Spain",
    "ita": "Italy",
    "rus": "Russia",
    "bra": "Brazil",
    "can": "Canada",
    "aus": "Australia",
    "mex": "Mexico",
    "ind": "India",
    "tur": "Turkey",
    "pol": "Poland",
    "nld": "Netherlands",
    "swe": "Sweden",
    "nor": "Norway",
    "fin": "Finland",
    "dnk": "Denmark",
    "che": "Switzerland",
    "aut": "Austria",
    "bel": "Belgium",
    "prt": "Portugal",
    "grc": "Greece",
    "irl": "Ireland",
    "nzl": "New Zealand",
    "sgp": "Singapore",
    "mys": "Malaysia",
    "tha": "Thailand",
    "vnm": "Vietnam",
    "phl": "Philippines",
    "idn": "Indonesia",
    "sau": "Saudi Arabia",
    "egy": "Egypt",
    "zaf": "South Africa",
    "arg": "Argentina",
    "chl": "Chile",
    "col": "Colombia",
    "per": "Peru",
    "ukr": "Ukraine",
    "rou": "Romania",
    "hun": "Hungary",
    "cze": "Czechia",
    "isr": "Israel",
    "twn": "Taiwan",
    "hkg": "Hong Kong",
}

ACRONYM_MAP: dict[str, str] = {
    "hq": "HQ",
    "vip": "VIP",
    "pve": "PVE",
    "pvp": "PVP",
    "gvg": "GVG",
    "svs": "SVS",
    "ur": "UR",
    "ssr": "SSR",
    "sr": "SR",
    "hp": "HP",
    "atk": "ATK",
    "def": "DEF",
    "exp": "EXP",
    "npc": "NPC",
    "ui": "UI",
    "hud": "HUD",
    "bg": "BG",
    "fx": "FX",
    "vfx": "VFX",
    "ok": "OK",
    "vs": "VS",
    "mp": "MP",
    "cd": "CD",
    "lv": "Lv",
    "mvp": "MVP",
    "s1": "S1",
    "s2": "S2",
    "s3": "S3",
    "s4": "S4",
    "s5": "S5",
    "s6": "S6",
    "s7": "S7",
    "s8": "S8",
    "s9": "S9",
    "2d": "2D",
    "3d": "3D",
    "tnt": "TNT",
    "ai": "AI",
    "tv": "TV",
    "ko": "KO",
    "qa": "QA",
    "slg": "SLG",
    "lod": "LOD",
    "diy": "DIY",
    "faq": "FAQ",
    "xp": "XP",
    "bp": "BP",
    "em": "EM",
    "mr": "Mr",
    "ms": "Ms",
    "dr": "Dr",
    "ii": "II",
    "iii": "III",
    "iv": "IV",
    "vi": "VI",
    "vii": "VII",
    "viii": "VIII",
    "ix": "IX",
    "rss": "RSS",
    "svr": "Server",
    "btn": "Button",
    "img": "Image",
    "pic": "Picture",
    "cfg": "Config",
    "msg": "Message",
    "num": "Number",
    "pos": "Pos",
    "res": "Resource",
    "unselect": "Unselect",
}

# Leading boilerplate tokens to strip from non-matched Unity sprite names when remainder stays descriptive
STRIP_LEADING_TOKENS = {
    "c", "ui", "common", "img", "icon", "btn", "pic", "texture", "uibuild",
    "uimain", "uisl", "g", "dz", "slg", "vx", "eff", "sp", "uicommon",
    "uicom", "uiicon", "a", "new",
}

# Compound UI prefixes where stripping leading "ui" preserves the meaningful domain noun
UI_PREFIX_KEEP_NOUN_RE = re.compile(
    r"^ui(alliance|build|main|mail|chat|shop|bag|hero|world|map|season\d*|activity|popup|scroll|fishing|day|night|portrait|talent|tech|technology|arms|army|arms|army|title|frame|rank|guild|war|battle|boss|monster|car|vehicle|troop|soldier|lab|research|science|skill|equip|item|gift|pack|pass|event|quest|task|mission|reward|store|market|trade|desert|wasteland|ice|snow|dino|moon|blood|robot|pasture|farm|mine|radar|city|base|camp|fort|tower|gate|wall|flag|banner|badge|medal|avatar|head|face|skin|dress|love|friend|social|team|squad|march|rally|duel|arena|league|server|state|capital|throne|glory|ground|review|guide|notice|tip|tips|help|info|setting|login|load|loading|start|menu|hud|bar|tab|panel|page|view|window|dialog|alert|confirm|select|list|grid|slot|box|chest|card|wheel|spin|draw|gacha|recruit|summon|lottery|bingo|puzzle|flip|parkour|race|rush|sprint|trial|challenge|saga|pirate|halloween|christmas|xmas|valentine|summer|spring|autumn|winter|thanks|easter|lunar|newyear|ageofiron|ironage|master|detect|country|nation|immigration|dominate|redenvelope|pve|pvp|heroappear|heromilitaryrank|leagueduel|pickup|pointssprint|fossick|exchange|fristpay|firstpay|s\d)",
    re.IGNORECASE,
)

# Regex helpers
RICH_TAG_RE = re.compile(r"<[^>]+>")
ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
WIN_FORBIDDEN_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTI_SPACE_RE = re.compile(r"\s+")
MULTI_HYPHEN_RE = re.compile(r"-{2,}")


# ---------------------------------------------------------------------------
# XML & Localization Loading
# ---------------------------------------------------------------------------

def strip_em_dashes(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-")


def load_localization() -> dict[str, str]:
    loc: dict[str, str] = {}
    if LOCALIZATION_JSON_PATH.exists():
        data = json.loads(LOCALIZATION_JSON_PATH.read_text(encoding="utf-8", errors="replace"))
        src = data.get("strings", data) if isinstance(data, dict) else {}
        if isinstance(src, dict):
            for k, v in src.items():
                s = strip_em_dashes(RICH_TAG_RE.sub("", str(v))).strip()
                if s:
                    loc[str(k).strip()] = s
    if ENGLISH_DIALOG_PATH.exists():
        with ENGLISH_DIALOG_PATH.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                s = strip_em_dashes(RICH_TAG_RE.sub("", v)).strip()
                if k and s:
                    loc[k] = s
    return loc


def load_xml_rows(table_name: str) -> list[tuple[str, dict[str, str]]]:
    p = XML_TABLES_DIR / f"{table_name}.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    out: list[tuple[str, dict[str, str]]] = []
    if isinstance(data, dict) and "columns" in data and "rows" in data:
        cols = [str(c) for c in data["columns"]]
        rows = data["rows"]
        if isinstance(rows, dict):
            for rid, rvals in rows.items():
                if isinstance(rvals, list):
                    out.append((
                        str(rid),
                        {cols[i]: ("" if rvals[i] is None else str(rvals[i])) for i in range(min(len(cols), len(rvals)))},
                    ))
                elif isinstance(rvals, dict):
                    out.append((str(rid), {str(k): ("" if v is None else str(v)) for k, v in rvals.items()}))
        elif isinstance(rows, list):
            for idx, rvals in enumerate(rows):
                if isinstance(rvals, list):
                    d = {cols[i]: ("" if rvals[i] is None else str(rvals[i])) for i in range(min(len(cols), len(rvals)))}
                    out.append((str(d.get("id", idx)), d))
                elif isinstance(rvals, dict):
                    out.append((str(rvals.get("id", idx)), {str(k): ("" if v is None else str(v)) for k, v in rvals.items()}))
    return out


def split_icon_tokens(raw_val: str) -> list[str]:
    if not raw_val:
        return []
    s = str(raw_val).strip()
    if not s or s == "0" or s.startswith("table:"):
        return []
    out: list[str] = []
    for part in re.split(r"[;|,]", s):
        part = part.strip()
        if not part or part == "0":
            continue
        if ":" in part and not part.lower().startswith("http"):
            part = part.split(":")[-1].strip()
        part = part.replace("\\", "/").split("/")[-1]
        if part.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".tga")):
            part = part.rsplit(".", 1)[0]
        part = part.strip()
        if part and not part.isdigit() and len(part) >= 2:
            out.append(part.lower())
    return out


def parse_single_int(val: str) -> int | None:
    s = str(val or "").strip()
    if s.isdigit():
        return int(s)
    return None


# ---------------------------------------------------------------------------
# Data-Driven Season Resolution Engine
# ---------------------------------------------------------------------------

class SeasonResolver:
    """
    Resolve official Last Z Season (0=Pre-Season 1, 1..6=Season 1..6) for every icon
    using verified XML tables, hero propagation, guarded sprite tags, and Unity paths.
    """

    def __init__(self, loc: dict[str, str]) -> None:
        self.loc = loc
        # sprite_lower -> (season_int, source_reason, priority)
        self.sprite_season: dict[str, tuple[int, str, int]] = {}
        # hero art code (e.g. "10", "41", "52") -> (season_int, hero_name)
        self.hero_code_season: dict[str, tuple[int, str]] = {}
        # hero_id -> (season_int, hero_name)
        self.hero_id_season: dict[str, tuple[int, str]] = {}
        # monster english name lower -> season_int (for seasonal monsters only)
        self.monster_name_season: dict[str, int] = {}
        # sprite_lower -> authoritative English display name override (e.g. seasonal resources from season_dialog)
        self.sprite_name_override: dict[str, str] = {}

        self._build_from_xml()

    def _register_sprite(self, sprite_key: str, season: int, source: str, prio: int) -> None:
        if season < 0 or season > 6:
            return
        sk = sprite_key.strip().lower()
        if not sk:
            return
        prev = self.sprite_season.get(sk)
        if prev is None or prio > prev[2]:
            self.sprite_season[sk] = (season, source, prio)

    def _register_unique_table_map(
        self,
        sprite_to_seasons: dict[str, set[int]],
        source: str,
        prio: int,
        use_min_if_multi: bool = False,
    ) -> None:
        for sk, seasons in sprite_to_seasons.items():
            valid = {s for s in seasons if 1 <= s <= 6}
            if len(valid) == 1:
                self._register_sprite(sk, next(iter(valid)), source, prio)
            elif use_min_if_multi and valid:
                self._register_sprite(sk, min(valid), source, prio)

    def _build_from_xml(self) -> None:
        # ------------------------------------------------------------------
        # 1. Playable Heroes (aps_new_heroes + aps_new_heroes_client_B)
        #    1-based: season 0 = Pre-Season 1, 1..6 = Season 1..6
        # ------------------------------------------------------------------
        goods_rows = load_xml_rows("goods")
        goods_by_id = {rid: r for rid, r in goods_rows}

        equip_rows = load_xml_rows("heroes_exclusive_equip")
        equip_by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
        for _, r in equip_rows:
            grp = r.get("group", "").strip()
            if grp:
                equip_by_group[grp].append(r)

        lw_skills = {rid: r for rid, r in load_xml_rows("lw_hero_skill")}
        std_skills = {rid: r for rid, r in load_xml_rows("skill")}

        hero_skill_seasons: dict[str, set[int]] = defaultdict(set)
        hero_rows_all = load_xml_rows("aps_new_heroes") + load_xml_rows("aps_new_heroes_client_B")

        for rid, r in hero_rows_all:
            hi = r.get("hero_icon", "").strip()
            ri = r.get("round_hero_icon", "").strip()
            if hi == "herohead_S_01" or ri.startswith("round_hero_icon_"):
                continue
            s_int = parse_single_int(r.get("season", "0"))
            if s_int is None or s_int > 6:
                continue
            hname = self.loc.get(r.get("name", "").strip(), r.get("name", "").strip())

            prev_id = self.hero_id_season.get(rid)
            if prev_id is None or s_int > prev_id[0]:
                self.hero_id_season[rid] = (s_int, hname)

            m = re.match(r"^hero_round_(\d+)(?:_[a-z0-9]+)?$", ri, re.I) or re.match(
                r"^hero_head_s_(\d+)(?:_[a-z0-9]+)?$", hi, re.I
            )
            if m:
                code_num = int(m.group(1))
                for ck in (str(code_num), f"{code_num:02d}"):
                    prev_c = self.hero_code_season.get(ck)
                    if prev_c is None or s_int > prev_c[0]:
                        self.hero_code_season[ck] = (s_int, hname)

            # Track skill icons used by ALL heroes (0..6) so shared Pre-Season skills stay Pre-Season 1
            for scol in ("skill_b", "skill_barrel", "skill"):
                val = r.get(scol, "")
                if not val or val.startswith("table:"):
                    continue
                for sid in re.findall(r"\d+", val):
                    for tbl in (lw_skills, std_skills):
                        srow = tbl.get(sid)
                        if not srow:
                            continue
                        for ic_col in ("icon", "skill_icon", "pic"):
                            for tok in split_icon_tokens(srow.get(ic_col, "")):
                                hero_skill_seasons[tok].add(s_int)

            # Hero fragments from hero_pieces -> goods.icon (authoritative for ALL playable heroes 0..6!)
            hp_val = r.get("hero_pieces", "")
            if hp_val and hname:
                gid_hp = hp_val.split("|")[0].strip()
                grow_hp = goods_by_id.get(gid_hp)
                if grow_hp:
                    for tok in split_icon_tokens(grow_hp.get("icon", "")):
                        self.sprite_name_override[tok] = f"{hname} Fragment"
                        self._register_sprite(tok, s_int, f"xml:hero_pieces:{hname}", 115)

            # Propagate seasonal heroes (1..6) to fragments, medals, portraits, exclusive gear
            if 1 <= s_int <= 6:
                for ic_col in ("hero_icon", "round_hero_icon", "hero_body", "hero_body_2D", "hero_halfbody"):
                    for tok in split_icon_tokens(r.get(ic_col, "")):
                        self._register_sprite(tok, s_int, f"xml:aps_new_heroes:{hname}", 110)

                # skill_levelup_item -> goods.icon
                gval = r.get("skill_levelup_item", "")
                for gid in re.findall(r"\d+", gval.split("|")[0] if "|" in gval else gval):
                    grow = goods_by_id.get(gid)
                    if grow:
                        for tok in split_icon_tokens(grow.get("icon", "")):
                            self._register_sprite(tok, s_int, f"xml:hero_pieces:{hname}", 110)

                # Exclusive equipment (heroes_exclusive_equip) -> icon, image, cost_item fragment
                eq_grp = r.get("exclusive_equip", "").strip()
                if eq_grp and eq_grp in equip_by_group:
                    for erow in equip_by_group[eq_grp]:
                        for ecol in ("icon", "image"):
                            for tok in split_icon_tokens(erow.get(ecol, "")):
                                self._register_sprite(tok, s_int, f"xml:heroes_exclusive_equip:{hname}", 112)
                        cid = erow.get("cost_item", "").strip()
                        if cid and cid in goods_by_id:
                            for tok in split_icon_tokens(goods_by_id[cid].get("icon", "")):
                                self._register_sprite(tok, s_int, f"xml:exclusive_equip_frag:{hname}", 112)

        # Register derived hero art code sprites for seasonal heroes (1..6)
        # Note: hero_fragment_* is mapped authoritatively via hero_pieces -> goods.icon above (not art code!)
        for code, (s_int, hname) in self.hero_code_season.items():
            if 1 <= s_int <= 6:
                for prefix in (
                    "hero_round_", "hero_head_s_", "hero_head_l_", "hero_troops_",
                    "hero_medal_", "herohead_medal_", "hero_refresh_", "hero_",
                ):
                    self._register_sprite(f"{prefix}{code}", s_int, f"xml:hero_code:{hname}", 108)

        # Register hero-specific skills ONLY if exclusively used by a single season (1..6)
        for sk, seasons in hero_skill_seasons.items():
            if len(seasons) == 1:
                only_s = next(iter(seasons))
                if 1 <= only_s <= 6:
                    self._register_sprite(sk, only_s, "xml:hero_skill", 104)

        # Propagate hero skins (aps_new_heros_skin) via hero_id -> official hero season
        for _, r in load_xml_rows("aps_new_heros_skin"):
            hid = r.get("hero_id", "").strip()
            info = self.hero_id_season.get(hid)
            if info and 1 <= info[0] <= 6:
                s_int, hname = info
                for ic_col in (
                    "skin_icon", "hero_icon", "round_hero_icon", "hero_body",
                    "hero_halfbody", "hero_body_2D", "skin_icon_ME", "round_hero_icon_ME",
                ):
                    for tok in split_icon_tokens(r.get(ic_col, "")):
                        self._register_sprite(tok, s_int, f"xml:aps_new_heros_skin:{hname}", 109)

        # Propagate love_message_hero via hero_id path or explicit season column (1-based)
        for _, r in load_xml_rows("love_message_hero"):
            lm_s = parse_single_int(r.get("season", ""))
            hid_from_path = ""
            for col in ("chat_pic", "unlock_pic", "summary_pic"):
                m = re.search(r"/(\d+)/love_message_", r.get(col, ""))
                if m:
                    hid_from_path = m.group(1)
                    break
            resolved_s = 0
            reason = ""
            if hid_from_path and hid_from_path in self.hero_id_season and self.hero_id_season[hid_from_path][0] > 0:
                resolved_s, hname = self.hero_id_season[hid_from_path]
                reason = f"xml:love_message_hero:{hname}"
            elif lm_s and 1 <= lm_s <= 6:
                resolved_s = lm_s
                reason = "xml:love_message_hero"
            if 1 <= resolved_s <= 6:
                for col in ("head_pic", "chat_pic", "unlock_pic", "unlock_pic_j", "summary_pic"):
                    for tok in split_icon_tokens(r.get(col, "")):
                        self._register_sprite(tok, resolved_s, reason, 107)

        # ------------------------------------------------------------------
        # 2. Hero Awakening & Exclusive Equipment Breakthrough -> Season 5
        #    Verified: exclusive_equip_breakthrough.season = 4 (world_season 4 = S5),
        #    aps_new_heroes.awakening_season = 4|..., goods 263201 S5 Awakening Badge Box
        #    & 264201 S5 Breakthrough Mineral Box. Overrides S1 Oliveira/Scarlett/Evelyn!
        # ------------------------------------------------------------------
        for _, r in load_xml_rows("exclusive_equip_breakthrough"):
            ws = parse_single_int(r.get("season", ""))
            if ws is not None and 0 <= ws <= 5:
                s_off = ws + 1
                for col in ("icon", "image", "skill_icon"):
                    for tok in split_icon_tokens(r.get(col, "")):
                        self._register_sprite(tok, s_off, "xml:exclusive_equip_breakthrough", 118)

        for rid, r in goods_rows:
            gnm = self.loc.get(r.get("name", "").strip(), "")
            gdesc = self.loc.get(r.get("description", "").strip(), "")
            low = f"{gnm} {gdesc}".lower()
            ic_toks = split_icon_tokens(r.get("icon", "")) + split_icon_tokens(r.get("icon_big", ""))
            if not ic_toks:
                continue
            # Awakening Badges & Breakthrough Minerals (Season 5 feature)
            if "awakening badge" in low or "breakthrough mineral" in low:
                for tok in ic_toks:
                    self._register_sprite(tok, 5, "xml:goods:s5_awakening_breakthrough", 119)
                continue
            # Explicit S1..S6 / Season 1..6 in goods name
            m_s = re.search(r"\b(?:S|Season\s*)([1-6])\b", gnm, re.I)
            if m_s:
                gs = int(m_s.group(1))
                for tok in ic_toks:
                    self._register_sprite(tok, gs, f"xml:goods:S{gs}", 115)

        # ------------------------------------------------------------------
        # 3. Verified 0-Based World-Season XML Tables (world_season + 1 = Season)
        # ------------------------------------------------------------------

        # 3a. aps_season (season 0..4 -> S1..S5)
        aps_season_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("aps_season"):
            ws = parse_single_int(r.get("season", ""))
            if ws is None or ws > 5:
                continue
            s_off = ws + 1
            for col in ("season_list_icon", "icon", "bg"):
                for tok in split_icon_tokens(r.get(col, "")):
                    aps_season_map[tok].add(s_off)
            # Extract c_texture_saiji* from hint without grabbing shared UIseason_rulesicon01
            for tok in split_icon_tokens(r.get("hint", "")):
                if "saiji" in tok or "season" in tok:
                    aps_season_map[tok].add(s_off)
        self._register_unique_table_map(aps_season_map, "xml:aps_season", 114)

        # 3b. aps_season_group (world_season 1..4 -> S2..S5; season=0 & empty ws -> S1)
        sg_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("aps_season_group"):
            ws = parse_single_int(r.get("world_season", ""))
            s_raw = parse_single_int(r.get("season", ""))
            if ws is not None and 0 <= ws <= 5:
                s_off = ws + 1
            elif s_raw == 0:
                s_off = 1
            else:
                continue
            for col in ("season_icon", "season_list_icon"):
                for tok in split_icon_tokens(r.get(col, "")):
                    sg_map[tok].add(s_off)
        self._register_unique_table_map(sg_map, "xml:aps_season_group", 113)

        # 3c. building.json (building_season / season 1..4 -> S2..S5)
        #     Verified: 1=A_Build_*_S1_D (Virus Lab/Land Office = S2),
        #     2=A_Build_*_S3_D (Icy Arsenal/Bio Lab = S3),
        #     3=UIseason4_build_* (Dino = S4), 4=UIseason5_build_* (Moonlit = S5)
        bld_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("building"):
            bs = parse_single_int(r.get("building_season", "") or r.get("season", ""))
            if bs is None or bs == 0 or bs > 5:
                continue
            s_off = bs + 1
            for col in ("pic", "icon", "build_icon", "pic_b"):
                for tok in split_icon_tokens(r.get(col, "")):
                    bld_map[tok].add(s_off)
        self._register_unique_table_map(bld_map, "xml:building", 116)

        # 3d. desert.json (season=1 -> world_season 1 = Season 2 Wastes Watcher)
        for _, r in load_xml_rows("desert"):
            ds = parse_single_int(r.get("season", ""))
            if ds is not None and 1 <= ds <= 5:
                s_off = ds + 1
                for tok in split_icon_tokens(r.get("icon", "")):
                    self._register_sprite(tok, s_off, "xml:desert", 114)

        # 3e. APS monster.json (world_season 1..4 -> S2..S5; exclude generic Zombie/Boomer/Elite Zombie)
        generic_monsters = {"zombie", "boomer", "elite zombie", "creep", "elite creep", "chief creep"}
        mon_name_seasons: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("APS_monster"):
            ws = parse_single_int(r.get("world_season", ""))
            if ws is None or ws == 0 or ws > 5:
                continue
            s_off = ws + 1
            mnm = self.loc.get(r.get("name", "").strip(), "").strip()
            if mnm and mnm.lower() not in generic_monsters:
                mon_name_seasons[mnm.lower()].add(s_off)
        for mnm_low, seasons in mon_name_seasons.items():
            if len(seasons) == 1:
                self.monster_name_season[mnm_low] = next(iter(seasons))

        # 3f. activity_panel.json (activity_season 1..4 -> S2..S5; unique sprites only)
        ap_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("activity_panel"):
            as_val = parse_single_int(r.get("activity_season", ""))
            if as_val is None or as_val == 0 or as_val > 5:
                continue
            s_off = as_val + 1
            for col in ("list_icon", "Advertise_pic", "activity_pic", "mainUI_icon"):
                for tok in split_icon_tokens(r.get(col, "")):
                    ap_map[tok].add(s_off)
        self._register_unique_table_map(ap_map, "xml:activity_panel", 102)

        # 3g. season_activity_panel.json (world_season 2..4 -> S3..S5; unique sprites only)
        sap_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("season_activity_panel"):
            ws = parse_single_int(r.get("world_season", ""))
            if ws is None or ws == 0 or ws > 5:
                continue
            s_off = ws + 1
            for col in ("preview_pic", "pic"):
                for tok in split_icon_tokens(r.get(col, "")):
                    sap_map[tok].add(s_off)
        self._register_unique_table_map(sap_map, "xml:season_activity_panel", 103)

        # 3h. flag_effect.json (world_season 2..4 -> S3..S5)
        fe_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("flag_effect"):
            ws = parse_single_int(r.get("world_season", ""))
            if ws is None or ws == 0 or ws > 5:
                continue
            s_off = ws + 1
            for col in ("flag_effect_bg", "flag_effect_pic", "flag_effect_season"):
                for tok in split_icon_tokens(r.get(col, "")):
                    fe_map[tok].add(s_off)
        self._register_unique_table_map(fe_map, "xml:flag_effect", 112)

        # 3i. roaming_boss_reward_show.json (world_season 2..4 -> S3..S5)
        rb_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("roaming_boss_reward_show"):
            ws = parse_single_int(r.get("world_season", ""))
            if ws is None or ws == 0 or ws > 5:
                continue
            s_off = ws + 1
            for col in ("mons_img", "boss_img"):
                for tok in split_icon_tokens(r.get(col, "")):
                    rb_map[tok].add(s_off)
        self._register_unique_table_map(rb_map, "xml:roaming_boss_reward_show", 110)

        # 3j. season_mastery & season_mastery_b (world_season 1..4 -> S2..S5)
        #     Use earliest world_season where each mastery tech icon debuted!
        sm_map: dict[str, set[int]] = defaultdict(set)
        for tname in ("season_mastery", "season_mastery_b"):
            for _, r in load_xml_rows(tname):
                ws = parse_single_int(r.get("world_season", ""))
                if ws is None or ws == 0 or ws > 5:
                    continue
                s_off = ws + 1
                for tok in split_icon_tokens(r.get("icon", "")):
                    sm_map[tok].add(s_off)
        self._register_unique_table_map(sm_map, "xml:season_mastery", 106, use_min_if_multi=True)

        # 3k. trade_post & trade_title (world_season 3->S4, 4->S5)
        tp_map: dict[str, set[int]] = defaultdict(set)
        for tname in ("trade_post", "trade_title"):
            for _, r in load_xml_rows(tname):
                ws = parse_single_int(r.get("world_season", ""))
                if ws is None or ws == 0 or ws > 5:
                    continue
                s_off = ws + 1
                for tok in split_icon_tokens(r.get("icon", "")):
                    tp_map[tok].add(s_off)
        self._register_unique_table_map(tp_map, "xml:trade_post_title", 111)

        # 3l. aps_resources rows 0 & 13: ordered seasonal resource icon arrays [S2, S3, S4, S5]
        #     Cross-reference season_dialog.json for exact official display names per season:
        #     S2: Sapphire/Sandsoul, S3: Frost Core/Icebloom, S4: Cretaceous Scale/Fernleaf, S5: Sanguine Crystal/Holy Water
        season_dialog_rows = {rid: r for rid, r in load_xml_rows("season_dialog")}
        for rid, r in load_xml_rows("aps_resources"):
            if rid in ("0", "13"):
                toks = split_icon_tokens(r.get("icon", ""))
                base_name_id = r.get("name", "").strip()
                sd_row = season_dialog_rows.get(base_name_id, {})
                ws_to_name: dict[int, str] = {}
                for part in sd_row.get("season_dialog", "").split("|"):
                    if ";" in part:
                        ws_s, loc_id = part.split(";", 1)
                        ws_i = parse_single_int(ws_s)
                        if ws_i is not None and loc_id.strip() in self.loc:
                            ws_to_name[ws_i] = self.loc[loc_id.strip()]
                for idx, tok in enumerate(toks):
                    ws_i = 1 + idx
                    s_off = 2 + idx
                    if s_off <= 6:
                        self._register_sprite(tok, s_off, "xml:aps_resources", 115)
                        if ws_i in ws_to_name:
                            self.sprite_name_override[tok] = ws_to_name[ws_i]

        # 3m. fossil_book -> Season 4 (Dinosaur Origin)
        for _, r in load_xml_rows("fossil_book"):
            for col in ("pic_got", "icon", "pic_bef"):
                for tok in split_icon_tokens(r.get(col, "")):
                    self._register_sprite(tok, 4, "xml:fossil_book", 116)

        # 3n. icecave_fish -> Season 3 (Everfrost Era: Arctic Ice Pit activity_season=2,
        #     res_lack_tips.season=3 Ice Fishing Master Pack). Overrides S4_ filename prefix!
        for _, r in load_xml_rows("icecave_fish"):
            for col in ("pic", "pic_none"):
                for tok in split_icon_tokens(r.get(col, "")):
                    self._register_sprite(tok, 3, "xml:icecave_fish:everfrost", 120)

        # ------------------------------------------------------------------
        # 4. Verified 1-Based Season XML Tables (1..6 -> Season 1..6)
        # ------------------------------------------------------------------

        # 4a. res_lack_tips (verified 1-based: 1=S1, 2=S2 Virus Lab, 3=S3 Ice Fishing/Bio Lab,
        #     4=S4 Stegosaurs/Velociraptors, 5=S5 Werewolves/Succubi/Serum Lab)
        rlt_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("res_lack_tips"):
            rs = parse_single_int(r.get("season", ""))
            if rs is None or rs < 1 or rs > 6:
                continue
            for tok in split_icon_tokens(r.get("pic", "")):
                rlt_map[tok].add(rs)
        self._register_unique_table_map(rlt_map, "xml:res_lack_tips", 101)

        # 4b. decoration (verified 1-based: season=4 -> Dino Hunter / Ankylosaurus = S4)
        dec_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("decoration"):
            ds = parse_single_int(r.get("season", ""))
            if ds is None or ds < 1 or ds > 6:
                continue
            for col in ("icon", "image", "preview_image", "image_other"):
                for tok in split_icon_tokens(r.get(col, "")):
                    dec_map[tok].add(ds)
        self._register_unique_table_map(dec_map, "xml:decoration", 112)

        # 4c. c_quest (quest_season 2..4 -> world_season 2..4 = S3..S5 for unique icons)
        cq_map: dict[str, set[int]] = defaultdict(set)
        for _, r in load_xml_rows("c_quest"):
            qs = parse_single_int(r.get("quest_season", ""))
            if qs is None or qs < 1 or qs > 5:
                continue
            for tok in split_icon_tokens(r.get("icon", "")):
                cq_map[tok].add(qs + 1)
        self._register_unique_table_map(cq_map, "xml:c_quest", 98)

    def resolve(self, icon: dict[str, Any]) -> tuple[str, str]:
        """Return (season_bucket_name, evidence_source)."""
        sn = ZERO_WIDTH_RE.sub("", str(icon.get("sprite_name", ""))).strip()
        sn_low = sn.lower()
        en = str(icon.get("english_name", "")).strip()
        en_low = en.lower()
        up = str(icon.get("unity_path", "")).replace("\\", "/")
        up_low = up.lower()
        bn_low = str(icon.get("source_bundle", "")).lower()
        cat_low = str(icon.get("category", "")).lower()

        # 1. Exact XML sprite registration (highest authority)
        #    Special guard: A_Build_LianMengZhongXin_S1_D_s3/s4/s5 explicit trailing season overrides base S1_D
        m_bld_override = re.match(r"^a_build_.*_s1_d_s([3-6])$", sn_low)
        if m_bld_override:
            s_num = int(m_bld_override.group(1))
            return SEASON_NUM_TO_BUCKET[s_num], f"sprite_tag:a_build_s{s_num}"

        if sn_low in self.sprite_season:
            s_num, reason, _ = self.sprite_season[sn_low]
            return SEASON_NUM_TO_BUCKET[s_num], reason

        # Also check sprite without trailing " 1" or "_repeatN" or "_empty" or "_me" or "_unselect"
        sn_base = re.sub(r"(?:\s+\d+|_repeat\d+|_empty|_me|_unselect|_select)$", "", sn_low)
        if sn_base and sn_base != sn_low and sn_base in self.sprite_season:
            s_num, reason, _ = self.sprite_season[sn_base]
            return SEASON_NUM_TO_BUCKET[s_num], f"{reason}:variant"

        # 2. Hero art code propagation (catches any skin/variant like hero_head_l_43_b, hero_round_10_1)
        #    Exclude hero_fragment_* since fragment numbers follow goods.icon via hero_pieces, not round icon code
        m_hero = re.match(
            r"^(?:hero_round|hero_head_[sl]|hero_medal|herohead_medal|hero_troops|hero_refresh|hero)_(\d+)(?:_[a-z0-9]+)*$",
            sn_low,
        )
        if m_hero:
            code_num = int(m_hero.group(1))
            hinfo = self.hero_code_season.get(f"{code_num:02d}") or self.hero_code_season.get(str(code_num))
            if hinfo and 1 <= hinfo[0] <= 6:
                return SEASON_NUM_TO_BUCKET[hinfo[0]], f"hero_code_variant:{hinfo[1]}"

        # 3. Seasonal monster name match from APS_monster (Everfrost / Dino / Moonlit monsters)
        if en_low and en_low in self.monster_name_season:
            s_num = self.monster_name_season[en_low]
            return SEASON_NUM_TO_BUCKET[s_num], f"xml:APS_monster:{en}"

        # 4. Guarded A_Build_*_S1_D / _S3_D check (S1_D = Season 2 Wastes Watcher, S3_D = Season 3 Everfrost)
        if re.match(r"^a_build_.*_s1_d(?:_.*)?$", sn_low):
            return "Season 2", "building_code:A_Build_S1_D_world_season_1"
        if re.match(r"^a_build_.*_s3_d(?:_.*)?$", sn_low):
            return "Season 3", "building_code:A_Build_S3_D_world_season_2"

        # 5. FishingCatalog / FishIcons -> Verified Season 3 (Everfrost Era Arctic Ice Pit)
        if (
            "/fishicons/" in up_low
            or "/fishingcatalog/" in up_low
            or "fishingcatalog" in bn_low
            or "fishicons" in bn_low
            or sn_low.startswith("s4_icecave_fish_")
            or "icecave" in sn_low
        ):
            return "Season 3", "xml_verified_feature:everfrost_icecave_fishing"

        # 6. Explicit season number patterns in sprite_name (strictly guarded against false positives)
        #    Note: S7/S8/S9 future placeholder mastery tokens stay in Pre-Season 1 (no S7..S9 folders)
        if re.search(r"(?:orange|purple)s[7-9]$", sn_low):
            return "Pre-Season 1", "future_placeholder:s7_s9_mastery"

        # Check explicit "seasonN" / "seasonsN" / "season0N" / "seaxonN" / "saijiN"
        m_sn = re.search(r"(?:seasons?|seaxon|saiji)[_\-]?0?([1-6])(?![0-9])", sn_low)
        if m_sn:
            # Special case: UIseasons2_Technology_icon_* already checked in season_mastery above;
            # any remaining unreferenced ones belong to Season 2 where season mastery launched.
            s_num = int(m_sn.group(1))
            return SEASON_NUM_TO_BUCKET[s_num], f"sprite_tag:season{s_num}"

        # Check explicit S1..S6 tokens in sprite_name (avoiding head_S_XX, boss4 without S, etc.)
        s_tag_patterns = [
            r"bosss([1-6])(?![0-9])",
            r"(?:orange|purple)s([1-6])$",
            r"tab_s([1-6])(?:_|0[1-9]|$)",
            r"dabjs([1-6])(?![0-9])",
            r"recruit_icon_s([1-6])(?:_|$)",
            r"seasonshop_s([1-6])(?:_|$)",
            r"(?:^|_)u?i?s([1-6])(?:monthlycard|sauhu|xueyue)(?:_|$)",
            r"^s([1-6])_(?:entrance|xueyue|uimail|roam)",
            r"(?:^|_)mail_s([1-6])_",
            r"hero_round_s([1-6])_",
            r"boss_head_s([1-6])_",
            r"(?:^|_)s([1-6])(?:_|$)",
        ]
        for pat in s_tag_patterns:
            m_tag = re.search(pat, sn_low)
            if m_tag:
                s_num = int(m_tag.group(1))
                # Extra guard: ignore S1 inside "A_Build_*_S1_D" (already handled above)
                return SEASON_NUM_TO_BUCKET[s_num], f"sprite_tag:s{s_num}"

        # 7. Explicit "Season N" or "SN" in real English name
        if en:
            m_en = re.search(r"\b(?:Season\s*|S)([1-6])\b", en)
            if m_en and not re.search(r"\bS[7-9]\b", en):
                s_num = int(m_en.group(1))
                return SEASON_NUM_TO_BUCKET[s_num], f"english_name:S{s_num}"

        # 8. Verified Official Season Theme Keywords in english_name / sprite_name
        #    (Grounded directly in aps_season.json & XML tables)
        if en_low:
            if "clash of thrones" in en_low:
                return "Season 1", "theme:clash_of_thrones"
            if any(k in en_low for k in ("wastes watcher", "wastes ore", "sandsoul", "sapphire mine", "virus lab", "land office")):
                return "Season 2", "theme:wastes_watcher"
            if any(k in en_low for k in (
                "everfrost", "arctic ice", "ice fishing", "frost warden", "chiller chief",
                "sovereign of snow", "snowman mania", "smart greenhouse", "icy arsenal", "icy fort",
                "frostbane", "glacier kong", "hunter yeti", "snow leopard", "tundra titan",
                "chill trunk", "frost fox", "cold hoof", "ice snout", "frost core",
            )):
                return "Season 3", "theme:everfrost_era"
            if any(k in en_low for k in (
                "dinosaur", "dino egg", "dino rescue", "dino hunter", "dino scale",
                "spinosaurus", "ankylosaurus", "stegosaurus", "velociraptor", "t-rex",
                "pterosaur", "dimetrodon", "herbivorous dino", "carnivorous dino",
                "bones & eggs", "bio greenhouse", "primeval trader", "hatch of legends",
            )):
                return "Season 4", "theme:dinosaur_origin"
            if any(k in en_low for k in (
                "moonlit elegy", "blood moon", "sanguine crystal", "endless night duke",
                "night countess", "night succubus", "night priest", "night gargoyle",
                "vampire raid", "vampire guard", "moon shop", "moonlight collection",
                "shadow spring", "serum lab", "until dawn", "moonlit wayfarer",
                "awakening badge", "breakthrough mineral",
            )):
                return "Season 5", "theme:moonlit_elegy"

        # 8b. Specific Everfrost Snowman Mania sprites (excluding Christmas event sprites) & S5 Breakthrough UI
        if ("snowman" in sn_low or "saoxue" in sn_low) and "christmas" not in sn_low and "christmas" not in up_low and "bauble" not in up_low:
            return "Season 3", "theme:everfrost_snowman"
        if "breakthrough" in sn_low:
            return "Season 5", "theme:s5_breakthrough"

        # 9. Verified Season-Specific Unity Paths & AssetBundle Names
        #    Note: HeroIconsSmall_S1 is explicitly excluded (core Pre-Season 1 monsters!)
        #    and ActivityIcons_S1 is mixed (individual items already resolved above).
        if "/seasondesert/" in up_low or "seasondesert" in bn_low or "uiwasteland" in sn_low:
            return "Season 2", "unity_folder:SeasonDesert"

        if any(k in up_low for k in (
            "/activityicons_s3/", "/heroiconssmall_s3/", "/uiworldpoint_s3/",
            "/uitextureseason3entrance/", "/uiportraitseason/frozenland/",
            "/uiportraitseason/", "/uitextureseason/",
        )) or any(k in bn_low for k in (
            "activityicons_s3_", "heroiconssmall_s3_", "uiworldpoint_s3_",
            "uitextureseason3entrance_", "uiportraitseason_", "uitextureseason_",
        )):
            # Guard: do NOT match UIPortraitSeason4 / UIPortraitSeason5 / UITextureSeason4 / 5 / Review / Talent
            if not re.search(r"season[456]|seasonreview|seasontalent", up_low + " " + bn_low):
                return "Season 3", "unity_folder:Season3_Everfrost"

        if any(k in up_low for k in (
            "/activityicons_s4/", "/heroiconssmall_s4/", "/itemicons_s4/",
            "/uiworldpoint_s4/", "/uiportraitseason4/", "/uitextureseason4",
        )) or any(k in bn_low for k in (
            "activityicons_s4_", "heroiconssmall_s4_", "itemicons_s4_",
            "uiworldpoint_s4_", "uiportraitseason4_", "uitextureseason4",
        )):
            return "Season 4", "unity_folder:Season4_Dinosaur"

        if any(k in up_low for k in (
            "/activityicons_s5/", "/heroiconssmall_s5/", "/uiworldpoint_s5/",
            "/uiportraitseason5/", "/uitextureseason5", "/uiredenvelope_c_season5/",
            "/uiseasonbloodmoon/", "/uidaynight/",
        )) or any(k in bn_low for k in (
            "activityicons_s5_", "heroiconssmall_s5_", "uiworldpoint_s5_",
            "uiportraitseason5_", "uitextureseason5", "uiredenvelope_c_season5_",
            "uiseasonbloodmoon_", "uidaynight_",
        )):
            return "Season 5", "unity_folder:Season5_Moonlit"

        # 10. Default: Core launch / non-seasonal / shared base icons -> Pre-Season 1
        return "Pre-Season 1", "default:core_base"


# ---------------------------------------------------------------------------
# Clean Concise Zero-Underscore Naming Engine
# ---------------------------------------------------------------------------

def normalize_unicode_clean(text: str) -> str:
    """Normalize rich tags, zero-width chars, Roman numerals, dashes, dots, and quotes."""
    s = ZERO_WIDTH_RE.sub("", text)
    s = RICH_TAG_RE.sub("", s)
    s = s.replace("\\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = strip_em_dashes(s)
    for uni_rom, ascii_rom in ROMAN_UNICODE_MAP.items():
        s = s.replace(uni_rom, ascii_rom)
    s = s.replace("\u00b7", " ").replace("\u2022", " ").replace("\u2026", " ")
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", " ").replace("\u201d", " ")
    s = s.replace("\u00d7", "x")
    s = s.replace("_", " ")
    s = WIN_FORBIDDEN_RE.sub(" ", s)
    s = MULTI_HYPHEN_RE.sub("-", s)
    s = MULTI_SPACE_RE.sub(" ", s).strip()
    return s


def truncate_word_boundary(text: str, max_len: int) -> str:
    """Truncate text cleanly at a word boundary to <= max_len chars."""
    s = text.strip(" .-_")
    if len(s) <= max_len:
        return s
    cut = s[:max_len]
    if " " in cut:
        last_sp = cut.rfind(" ")
        if last_sp >= max(10, max_len // 2):
            cut = cut[:last_sp]
    return cut.rstrip(" .-_,;:!&-")


def is_usable_english_name(raw_en: str) -> str:
    """
    Validate and clean an english_name from the catalog.
    Returns cleaned English display string or '' if it should fall back to sprite naming.
    """
    if not raw_en:
        return ""
    raw_stripped = raw_en.strip()
    low = raw_stripped.lower()
    if low in DEV_ENGLISH_NAME_OVERRIDES:
        override = DEV_ENGLISH_NAME_OVERRIDES[low]
        if not override:
            return ""
        raw_stripped = override

    # Reject raw numeric IDs or unresolved format templates
    if raw_stripped.isdigit():
        return ""
    if any(tok in raw_stripped for tok in ("{0}", "{1}", "{2}", "%s", "%d", "table:")):
        return ""

    s = normalize_unicode_clean(raw_stripped)
    # Clean "Hero - Awakening Badge" -> "Hero Awakening Badge" for extra conciseness
    s = re.sub(r"\s+-\s+(Awakening Badge|Breakthrough Mineral)\b", r" \1", s)
    # Clean stray spacing around hyphens like "Armor II- Blood Rose" -> "Armor II - Blood Rose"
    s = re.sub(r"([A-Za-z0-9])-\s+", r"\1 - ", s)
    s = re.sub(r"\s+-([A-Za-z0-9])", r" - \1", s)
    s = MULTI_SPACE_RE.sub(" ", s).strip()
    # Strip trailing non-meaningful punctuation (keep internal dots like "Ms. Wrecker")
    s = s.rstrip(" ,;:!-").lstrip(" .,-;:!")
    if s.endswith(".") and not re.search(r"\b(?:Mr|Ms|Mrs|Dr|St|Jr|Sr)\.$", s):
        s = s.rstrip(".")
    s = s.strip()
    if len(s) < 2 or not any(ch.isalpha() for ch in s):
        return ""
    return s


def split_camel_and_digits(token: str) -> list[str]:
    """Split a camelCase / alphanumeric token while preserving S1..S9, 2D/3D, T1..T12, X2..X10, unSelect, Lv."""
    if not token:
        return []
    low = token.lower()
    if low in ("unselect", "unselected"):
        return ["Unselect"]
    # Protect special compact tokens (S1..S9, 2D/3D, T1..T12, X2..X99, Lv/Lv1)
    if re.fullmatch(r"s[1-9]|2d|3d|t\d{1,2}|x\d{1,2}|lv\d*", low):
        return [token]
    # Split camelCase boundaries: fooBar -> foo Bar, UIMain -> UI Main, orangeS6 -> orange S6
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", token)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    # Keep S1..S9, T1..T12, X2..X99 intact when splitting letters and digits
    s = re.sub(r"(?<![SsTtXx])([A-Za-z])(\d)", r"\1 \2", s)
    s = re.sub(r"(\d)([A-Za-z])", lambda m: m.group(0) if m.group(0).lower() in ("2d", "3d") else f"{m.group(1)} {m.group(2)}", s)
    # Fix accidental split of "S 1".."S 9" when preceded by another letter like "orange S 6" -> "orange S6"
    s = re.sub(r"\b([Ss])\s+([1-9])\b", r"\1\2", s)
    return [p for p in s.split() if p]


def format_word(word: str) -> str:
    low = word.lower()
    if low in ACRONYM_MAP:
        return ACRONYM_MAP[low]
    if re.fullmatch(r"s[1-9]", low):
        return f"S{low[1]}"
    if re.fullmatch(r"t\d{1,2}", low):
        return f"T{low[1:]}"
    if re.fullmatch(r"x\d{1,2}", low):
        return f"X{low[1:]}"
    if re.fullmatch(r"lv\d+", low):
        return f"Lv {low[2:]}"
    if word.isdigit():
        return word
    return word[0].upper() + word[1:].lower() if word else ""


def humanize_sprite_name(sprite_name: str, unity_path: str, category_clean: str) -> str:
    """Convert an unmatched Unity sprite name into a clean, concise Title Case name with ZERO underscores."""
    raw = normalize_unicode_clean(sprite_name)
    if not raw:
        raw = category_clean

    # Special handling for pure-digit sprite names (e.g. "4", "33"): prepend clean parent Unity folder
    if raw.isdigit() and unity_path:
        parent = unity_path.replace("\\", "/").split("/")[-2] if "/" in unity_path else ""
        if parent:
            raw = f"{parent} {raw}"

    # Split on whitespace and hyphens
    raw_tokens = [t for t in re.split(r"[\s\-]+", raw) if t]

    # Strip compound UI prefix on leading tokens (e.g. UIAlliance -> Alliance, UIseason5 -> season5)
    processed_tokens: list[str] = []
    for idx, tok in enumerate(raw_tokens):
        if idx <= 2 and UI_PREFIX_KEEP_NOUN_RE.match(tok):
            tok = tok[2:]  # drop leading "ui" / "UI"
        elif tok.lower().startswith("ulseason"):
            # Typo in game asset: Ulseason_tab_S5 -> Season tab S5
            tok = tok[2:]
        processed_tokens.append(tok)

    # Expand camelCase & digit boundaries
    expanded: list[str] = []
    for tok in processed_tokens:
        expanded.extend(split_camel_and_digits(tok))

    # Strip redundant leading boilerplate tokens ONLY while remainder stays descriptive
    while len(expanded) >= 2:
        head_low = expanded[0].lower()
        rest = expanded[1:]
        rest_alpha = any(any(c.isalpha() for c in t) for t in rest)
        if head_low in STRIP_LEADING_TOKENS and rest_alpha:
            expanded = rest
            continue
        # Strip leading "a build" -> "Build" or drop "a"
        if head_low == "a" and rest_alpha:
            expanded = rest
            continue
        break

    # Remove redundant internal boilerplate words ("Img", "Pic", "Icon", "Texture") when surrounded by descriptive words
    if len(expanded) >= 4:
        filtered: list[str] = []
        for i, tok in enumerate(expanded):
            tl = tok.lower()
            if tl in ("c", "texture", "img", "pic") and i > 0 and i < len(expanded) - 1:
                continue
            filtered.append(tok)
        if any(any(c.isalpha() for c in t) for t in filtered):
            expanded = filtered

    # Format each token cleanly & collapse adjacent duplicate words
    words: list[str] = []
    for tok in expanded:
        fw = format_word(tok)
        if not fw:
            continue
        # Re-split if format_word returned "Lv 2"
        for sub in fw.split():
            if words and words[-1].lower() == sub.lower():
                continue
            words.append(sub)

    result = " ".join(words).strip()
    if not result:
        result = f"{category_clean} Icon"

    # Guard Windows reserved device names
    if result.lower() in RESERVED_WIN_NAMES:
        result = f"{category_clean} {result}"

    return result


def build_clean_base_name(
    icon: dict[str, Any],
    category_clean: str,
    resolver: SeasonResolver,
) -> tuple[str, bool]:
    """
    Build clean base display name (<= MAX_STEM_LEN chars, ZERO underscores, ZERO em dashes).
    Returns (clean_base_name, used_english_name).
    """
    sn = ZERO_WIDTH_RE.sub("", str(icon.get("sprite_name", ""))).strip()
    sn_low = sn.lower()
    en = str(icon.get("english_name", "")).strip()
    up = str(icon.get("unity_path", "")).strip()

    # Authoritative seasonal resource name override from season_dialog + aps_resources
    if sn_low in resolver.sprite_name_override:
        en = resolver.sprite_name_override[sn_low]

    # Propagate real hero English name to unnamed hero variant sprites (hero_head_L_10_1 -> Oliveira, etc.)
    if not en:
        m_hero = re.match(
            r"^(hero_round|hero_head_[sl]|hero_medal|herohead_medal|hero_troops|hero_refresh|hero)_(\d+)(?:_[a-z0-9]+)*$",
            sn_low,
        )
        if m_hero:
            kind = m_hero.group(1)
            code_num = int(m_hero.group(2))
            hinfo = resolver.hero_code_season.get(f"{code_num:02d}") or resolver.hero_code_season.get(str(code_num))
            if hinfo and hinfo[1]:
                hname = hinfo[1]
                if kind in ("hero_medal", "herohead_medal"):
                    en = f"{hname} Medal"
                else:
                    en = hname

    # Check extra flag overrides if category is Flags and english_name is empty
    if not en and category_clean == "Flags":
        en_flag = EXTRA_FLAG_NAMES.get(sn_low, "")
        if en_flag:
            en = en_flag

    cleaned_en = is_usable_english_name(en)
    if cleaned_en:
        base = truncate_word_boundary(cleaned_en, MAX_STEM_LEN)
        if base.lower() in RESERVED_WIN_NAMES:
            base = f"{category_clean} {base}"
        # Absolute guarantee: zero underscores and zero em dashes
        base = strip_em_dashes(base).replace("_", " ")
        base = MULTI_SPACE_RE.sub(" ", base).strip(" .")
        return base, True

    base = humanize_sprite_name(sn, up, category_clean)
    base = truncate_word_boundary(base, MAX_STEM_LEN)
    base = strip_em_dashes(base).replace("_", " ")
    base = MULTI_SPACE_RE.sub(" ", base).strip(" .")
    if not base or base.lower() in RESERVED_WIN_NAMES:
        base = f"{category_clean} Icon"
    return base, False


# ---------------------------------------------------------------------------
# Reorganization Planner, Executor, and Verifier
# ---------------------------------------------------------------------------

def plan_reorganization(catalog: dict[str, Any], resolver: SeasonResolver) -> list[dict[str, Any]]:
    """
    Produce complete move & rename plan for every icon in catalog.
    Resolves case-insensitive collisions within each (Season, Category) sorted by
    pixel area descending so highest-resolution version gets <Name>.png.
    """
    icons = catalog["icons"]
    staged: list[dict[str, Any]] = []

    for idx, ic in enumerate(icons):
        old_cat = str(ic["category"])
        clean_cat = CATEGORY_MAP[old_cat]
        season_bucket, season_source = resolver.resolve(ic)
        base_name, used_english = build_clean_base_name(ic, clean_cat, resolver)
        area = int(ic.get("crop_width", 0)) * int(ic.get("crop_height", 0))
        old_rel = str(ic["relative_path"]).replace("\\", "/")
        src_path = ICONS_ROOT / old_rel

        staged.append({
            "orig_idx": idx,
            "icon": ic,
            "src_path": src_path,
            "old_category": old_cat,
            "season": season_bucket,
            "season_source": season_source,
            "category": clean_cat,
            "base_name": base_name,
            "used_english": used_english,
            "pixel_area": area,
        })

    # Group by (season, category, base_name_lower) for case-insensitive Windows collision resolution
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in staged:
        groups[(item["season"], item["category"], item["base_name"].lower())].append(item)

    # Track ALL claimed lowercase filenames per (season, category) to guarantee zero collisions even after truncation
    claimed_lower: dict[tuple[str, str], set[str]] = defaultdict(set)

    # Assign filenames deterministically: highest pixel area first, then sprite_name for stability
    for key in sorted(groups.keys()):
        season_b, cat_b, _ = key
        grp = groups[key]
        grp.sort(key=lambda x: (-x["pixel_area"], -int(x["icon"].get("file_size_bytes", 0)), str(x["icon"]["sprite_name"]).lower()))
        bucket_claimed = claimed_lower[(season_b, cat_b)]

        for rank, item in enumerate(grp, start=1):
            base = item["base_name"]
            if rank == 1:
                stem = truncate_word_boundary(base, MAX_STEM_LEN)
                if stem.lower() not in bucket_claimed:
                    final_stem = stem
                else:
                    n = 2
                    while True:
                        suffix = f" ({n})"
                        cand = f"{truncate_word_boundary(base, MAX_STEM_LEN - len(suffix))}{suffix}"
                        if cand.lower() not in bucket_claimed:
                            final_stem = cand
                            break
                        n += 1
            else:
                n = rank
                while True:
                    suffix = f" ({n})"
                    cand = f"{truncate_word_boundary(base, MAX_STEM_LEN - len(suffix))}{suffix}"
                    if cand.lower() not in bucket_claimed:
                        final_stem = cand
                        break
                    n += 1

            # Final hard safety guarantees
            final_stem = strip_em_dashes(final_stem).replace("_", " ")
            final_stem = MULTI_SPACE_RE.sub(" ", final_stem).strip(" .")
            assert "_" not in final_stem, f"Underscore leaked into stem: {final_stem!r}"
            assert "\u2014" not in final_stem, f"Em dash leaked into stem: {final_stem!r}"
            assert len(final_stem) <= MAX_STEM_LEN, f"Stem exceeded {MAX_STEM_LEN}: {final_stem!r} ({len(final_stem)})"

            bucket_claimed.add(final_stem.lower())
            filename = f"{final_stem}.png"
            rel_path = f"{season_b}/{cat_b}/{filename}"
            item["clean_name"] = final_stem
            item["new_filename"] = filename
            item["new_relative_path"] = rel_path
            item["dst_path"] = ICONS_ROOT / season_b / cat_b / filename

    # Sort final plan nicely by Season order, Category order, then clean filename
    season_rank = {s: i for i, s in enumerate(SEASON_BUCKETS)}
    cat_rank = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    staged.sort(key=lambda x: (season_rank[x["season"]], cat_rank[x["category"]], x["new_filename"].lower()))
    return staged


def write_catalogs_and_readme(
    old_catalog: dict[str, Any],
    plan: list[dict[str, Any]],
) -> None:
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    season_counts: dict[str, dict[str, Any]] = {}
    category_counts: dict[str, dict[str, int]] = {}
    new_icons_rows: list[dict[str, Any]] = []

    for item in plan:
        ic = item["icon"]
        sb = item["season"]
        cb = item["category"]
        used_en = item["used_english"]

        if sb not in season_counts:
            season_counts[sb] = {"total": 0, "english_named": 0, "sprite_cleaned": 0, "categories": {}}
        season_counts[sb]["total"] += 1
        season_counts[sb]["english_named" if used_en else "sprite_cleaned"] += 1
        season_counts[sb]["categories"][cb] = season_counts[sb]["categories"].get(cb, 0) + 1

        if cb not in category_counts:
            category_counts[cb] = {"total": 0, "english_named": 0, "sprite_cleaned": 0}
        category_counts[cb]["total"] += 1
        category_counts[cb]["english_named" if used_en else "sprite_cleaned"] += 1

        row = {
            "season": sb,
            "season_source": item["season_source"],
            "category": cb,
            "filename": item["new_filename"],
            "relative_path": item["new_relative_path"],
            "clean_name": item["clean_name"],
            "used_english_name": used_en,
            "english_name": item["base_name"] if used_en else strip_em_dashes(str(ic.get("english_name", ""))),
            "sprite_name": strip_em_dashes(ZERO_WIDTH_RE.sub("", str(ic.get("sprite_name", "")))),
            "xml_table": str(ic.get("xml_table", "")),
            "xml_id": str(ic.get("xml_id", "")),
            "source_bundle": str(ic.get("source_bundle", "")),
            "unity_path": strip_em_dashes(ZERO_WIDTH_RE.sub("", str(ic.get("unity_path", "")))),
            "asset_type": str(ic.get("asset_type", "")),
            "orig_width": int(ic.get("orig_width", 0)),
            "orig_height": int(ic.get("orig_height", 0)),
            "crop_width": int(ic.get("crop_width", 0)),
            "crop_height": int(ic.get("crop_height", 0)),
            "file_size_bytes": int(ic.get("file_size_bytes", 0)),
        }
        new_icons_rows.append(row)

    ordered_seasons = {s: season_counts[s] for s in SEASON_BUCKETS if s in season_counts}
    ordered_cats = {c: category_counts[c] for c in CATEGORY_ORDER if c in category_counts}

    total_icons = len(new_icons_rows)
    total_en = sum(1 for r in new_icons_rows if r["used_english_name"])
    total_cleaned = total_icons - total_en
    stem_lens = [len(r["clean_name"]) for r in new_icons_rows]
    avg_stem_len = round(sum(stem_lens) / total_icons, 2) if total_icons else 0.0
    max_stem_len = max(stem_lens) if stem_lens else 0

    new_catalog = {
        "generated_at_utc": now_utc,
        "extracted_at_utc": old_catalog.get("generated_at_utc", ""),
        "source_assetbundles_dir": old_catalog.get("source_assetbundles_dir", ""),
        "source_resources_assets": old_catalog.get("source_resources_assets", ""),
        "bundles_scanned": old_catalog.get("bundles_scanned", 0),
        "total_icons": total_icons,
        "total_english_named": total_en,
        "total_sprite_cleaned": total_cleaned,
        "avg_filename_stem_length": avg_stem_len,
        "max_filename_stem_length": max_stem_len,
        "layout": "<Season>/<Category>/<Clean Name>.png",
        "seasons": ordered_seasons,
        "categories": ordered_cats,
        "icons": new_icons_rows,
    }

    json_text = json.dumps(new_catalog, indent=2, ensure_ascii=False)
    assert "\u2014" not in json_text, "Em dash detected in Icons Catalog.json!"
    NEW_CATALOG_JSON.write_text(json_text, encoding="utf-8")

    csv_fields = [
        "season", "season_source", "category", "filename", "relative_path",
        "clean_name", "used_english_name", "english_name", "sprite_name",
        "xml_table", "xml_id", "source_bundle", "unity_path", "asset_type",
        "orig_width", "orig_height", "crop_width", "crop_height", "file_size_bytes",
    ]
    with NEW_CATALOG_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for r in new_icons_rows:
            writer.writerow(r)

    # Write clean README.md (zero em dashes)
    lines = [
        "# Last Z Complete Game Icons (Season Sorted)",
        "",
        f"Reorganized UTC: `{now_utc}`",
        "",
        "## Summary",
        "",
        f"- **Total Verified Edge-to-Edge PNG Icons:** `{total_icons:,}`",
        f"- **Real English Display Names Used:** `{total_en:,}` ({(total_en / total_icons * 100):.1f}%)",
        f"- **Cleaned Title Case Sprite Names:** `{total_cleaned:,}` ({(total_cleaned / total_icons * 100):.1f}%)",
        f"- **Filename Length (before `.png`):** average `{avg_stem_len:.1f}` chars, max `{max_stem_len}` chars",
        "- **Naming Rules:** Zero underscores in any filename or folder name, zero em dashes, collision variants resolved by pixel area descending (`<Name>.png`, `<Name> (2).png`, ...)",
        "- **Folder Layout:** `assets/icons/<Season>/<Category>/<Clean Name>.png`",
        "",
        "## Per-Season Breakdown",
        "",
        "| Season | Theme / Scope | Total Icons | English Named | Cleaned Sprite |",
        "|---|---|---:|---:|---:|",
    ]
    theme_notes = {
        "Pre-Season 1": "Core launch assets, base heroes, shared UI/HUD, flags, emojis",
        "Season 1": "Clash of Thrones + S1 heroes (Oliveira, Scarlett, Evelyn, Selena, Nyx, Sakura)",
        "Season 2": "Wastes Watcher (Desert, Virus Lab, Land Office) + S2 heroes (Alma, Bella, Harleyna)",
        "Season 3": "Everfrost Era (Ice, Snow, Arctic Ice Pit Fishing) + S3 heroes (Licia, Liliana, Dodomeki)",
        "Season 4": "Dinosaur Origin (Dinosaurs, Fossils, Trade Hub) + S4 heroes (Yu Chan, Queenie, Amber)",
        "Season 5": "Moonlit Elegy (Day/Night, Vampires, Awakening & Breakthrough, S5 Cards)",
        "Season 6": "Season 6 Mastery Points",
    }
    for sb, stats in ordered_seasons.items():
        lines.append(
            f"| `{sb}` | {theme_notes.get(sb, '')} | {stats['total']:,} | {stats['english_named']:,} | {stats['sprite_cleaned']:,} |"
        )
    lines.append(f"| **TOTAL** | All Verified Icons | **{total_icons:,}** | **{total_en:,}** | **{total_cleaned:,}** |")

    lines.extend([
        "",
        "## Per-Category Breakdown",
        "",
        "| Category | Total Icons | English Named | Cleaned Sprite |",
        "|---|---:|---:|---:|",
    ])
    for cb, stats in ordered_cats.items():
        lines.append(f"| `{cb}` | {stats['total']:,} | {stats['english_named']:,} | {stats['sprite_cleaned']:,} |")
    lines.append(f"| **TOTAL** | **{total_icons:,}** | **{total_en:,}** | **{total_cleaned:,}** |")

    lines.extend([
        "",
        "## Catalog Files",
        "",
        "- `Icons Catalog.json` - Full structured metadata with season provenance, clean name, original sprite name, dimensions, and XML/Unity traceability",
        "- `Icons Catalog.csv` - Spreadsheet-ready tabular catalog",
        "",
        "## Scripts",
        "",
        "- Extraction: `tools/extract all game icons.py`",
        "- Season sorting & clean naming: `tools/sort clean game icons.py`",
        "",
    ])
    readme_text = "\n".join(lines)
    assert "\u2014" not in readme_text, "Em dash detected in README.md!"
    README_PATH.write_text(readme_text, encoding="utf-8")


def audit_disk_state(expected_count: int) -> dict[str, Any]:
    """Run strict post-reorganization verification across assets/icons/."""
    all_pngs: list[Path] = []
    underscore_paths: list[str] = []
    em_dash_paths: list[str] = []

    for dirpath, dirnames, filenames in os.walk(ICONS_ROOT):
        rel_dir = Path(dirpath).relative_to(ICONS_ROOT)
        for d in dirnames:
            rel_d = str((rel_dir / d).as_posix())
            if "_" in d:
                underscore_paths.append(f"DIR: {rel_d}")
            if "\u2014" in d:
                em_dash_paths.append(f"DIR: {rel_d}")
        for fn in filenames:
            rel_f = str((rel_dir / fn).as_posix()) if str(rel_dir) != "." else fn
            if "_" in fn:
                underscore_paths.append(f"FILE: {rel_f}")
            if "\u2014" in fn:
                em_dash_paths.append(f"FILE: {rel_f}")
            if fn.lower().endswith(".png"):
                all_pngs.append(Path(dirpath) / fn)

    json_rows = json.loads(NEW_CATALOG_JSON.read_text(encoding="utf-8"))["icons"]
    with NEW_CATALOG_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))

    # Check zero em dashes in catalog files, README, and this script
    em_dash_files: list[str] = []
    for p in (NEW_CATALOG_JSON, NEW_CATALOG_CSV, README_PATH, Path(__file__)):
        if p.exists() and "\u2014" in p.read_text(encoding="utf-8", errors="replace"):
            em_dash_files.append(str(p))

    stem_lens = [len(p.stem) for p in all_pngs]
    return {
        "expected_count": expected_count,
        "disk_png_count": len(all_pngs),
        "json_row_count": len(json_rows),
        "csv_row_count": len(csv_rows),
        "underscore_paths": underscore_paths,
        "em_dash_paths": em_dash_paths,
        "em_dash_files": em_dash_files,
        "avg_stem_len": round(sum(stem_lens) / len(stem_lens), 2) if stem_lens else 0.0,
        "max_stem_len": max(stem_lens) if stem_lens else 0,
        "top_level_entries": sorted(p.name for p in ICONS_ROOT.iterdir()),
    }


def print_plan_summary(plan: list[dict[str, Any]]) -> None:
    season_counts = Counter(x["season"] for x in plan)
    season_en = Counter(x["season"] for x in plan if x["used_english"])
    source_counts = Counter(x["season_source"].split(":")[0] for x in plan)
    stem_lens = [len(x["clean_name"]) for x in plan]
    max_item = max(plan, key=lambda x: len(x["clean_name"]))
    collisions = sum(1 for x in plan if re.search(r" \(\d+\)$", x["clean_name"]))

    print(f"\n=== PLAN SUMMARY ({len(plan):,} icons) ===")
    print(f"  Real English named:   {sum(1 for x in plan if x['used_english']):,} ({sum(1 for x in plan if x['used_english'])/len(plan)*100:.1f}%)")
    print(f"  Cleaned sprite named: {sum(1 for x in plan if not x['used_english']):,}")
    print(f"  Collision suffixes:   {collisions:,}")
    print(f"  Avg stem length:      {sum(stem_lens)/len(stem_lens):.2f} chars")
    print(f"  Max stem length:      {max(stem_lens)} chars (example: {max_item['new_relative_path']})")
    print("\n  Per-Season Counts:")
    for sb in SEASON_BUCKETS:
        if season_counts[sb]:
            print(f"    {sb:<15} {season_counts[sb]:>6,}  (English: {season_en[sb]:>5,})")
    print("\n  Resolution Provenance Summary:")
    for k, c in source_counts.most_common(20):
        print(f"    {k:<28} {c:>6,}")

    # Pick 25 diverse examples across all present seasons & categories
    print("\n  25 Diverse Example Final Paths:")
    by_season: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for x in plan:
        by_season[x["season"]].append(x)

    picks: list[dict[str, Any]] = []
    # Desired quotas across Pre-Season 1 .. Season 6
    quotas = [
        ("Pre-Season 1", 6),
        ("Season 1", 4),
        ("Season 2", 4),
        ("Season 3", 4),
        ("Season 4", 4),
        ("Season 5", 4),
        ("Season 6", 2),
    ]
    for sb, q in quotas:
        pool = by_season.get(sb, [])
        if not pool:
            continue
        # Prefer diverse categories, mix of English and cleaned sprite names
        seen_cats: set[str] = set()
        picked_sb: list[dict[str, Any]] = []
        # First pass: English-named from distinct categories
        for item in pool:
            if item["used_english"] and item["category"] not in seen_cats:
                picked_sb.append(item)
                seen_cats.add(item["category"])
                if len(picked_sb) >= max(1, q - 1):
                    break
        # Second pass: cleaned sprite name from distinct category
        for item in pool:
            if not item["used_english"] and item["category"] not in seen_cats:
                picked_sb.append(item)
                seen_cats.add(item["category"])
                if len(picked_sb) >= q:
                    break
        # Fill remainder if needed
        for item in pool:
            if item not in picked_sb:
                picked_sb.append(item)
                if len(picked_sb) >= q:
                    break
        picks.extend(picked_sb[:q])

    for i, item in enumerate(picks[:25], start=1):
        print(f"    {i:>2}. assets/icons/{item['new_relative_path']}  [{item['season_source']}]")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sort Last Z extracted PNG icons by Season and clean Category with zero underscores."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute file moves, remove old empty underscore dirs/catalogs, and write clean catalogs.",
    )
    args = parser.parse_args()

    if not OLD_CATALOG_JSON.exists():
        print(f"[ERROR] Source catalog not found: {OLD_CATALOG_JSON}", file=sys.stderr)
        return 1

    print("[1/5] Loading localization and XML season tables...")
    loc = load_localization()
    resolver = SeasonResolver(loc)
    print(f"      Loaded {len(loc):,} localization entries, {len(resolver.sprite_season):,} XML sprite->season rules, {len(resolver.hero_code_season):,} hero codes.")

    print("[2/5] Loading existing icons_catalog.json...")
    old_catalog = json.loads(OLD_CATALOG_JSON.read_text(encoding="utf-8"))
    expected_count = len(old_catalog["icons"])
    print(f"      Catalog contains {expected_count:,} icons.")

    print("[3/5] Computing season buckets and zero-underscore clean filenames...")
    plan = plan_reorganization(old_catalog, resolver)

    # Pre-flight validation before any filesystem change
    missing_sources = [x["src_path"] for x in plan if not x["src_path"].exists()]
    if missing_sources:
        print(f"[ERROR] {len(missing_sources)} source PNG files missing! First 5: {missing_sources[:5]}", file=sys.stderr)
        return 1

    dst_lower_set = {str(x["dst_path"]).lower() for x in plan}
    if len(dst_lower_set) != expected_count:
        print(f"[ERROR] Destination collision detected: {len(dst_lower_set)} unique vs {expected_count} expected!", file=sys.stderr)
        return 1

    bad_u = [x["new_relative_path"] for x in plan if "_" in x["new_relative_path"]]
    bad_em = [x["new_relative_path"] for x in plan if "\u2014" in x["new_relative_path"]]
    if bad_u or bad_em:
        print(f"[ERROR] Forbidden chars in plan! underscores={len(bad_u)}, em_dashes={len(bad_em)}", file=sys.stderr)
        return 1

    print_plan_summary(plan)

    if not args.apply:
        print("\n[DRY-RUN] Pre-flight checks passed 100%. Re-run with --apply to move files.")
        return 0

    print("\n[4/5] Moving 17,049 verified PNGs into Season/Category directories...")
    created_dirs: set[Path] = set()
    moved = 0
    for item in plan:
        dst: Path = item["dst_path"]
        parent = dst.parent
        if parent not in created_dirs:
            parent.mkdir(parents=True, exist_ok=True)
            created_dirs.add(parent)
        shutil.move(str(item["src_path"]), str(dst))
        moved += 1
    print(f"      Moved {moved:,} PNG files into {len(created_dirs)} Season/Category folders.")

    # Remove old underscore category folders (only if empty!) and old underscore catalog files
    removed_dirs = 0
    leftover_files: list[Path] = []
    for old_cat in CATEGORY_MAP.keys():
        old_dir = ICONS_ROOT / old_cat
        if old_dir.exists() and old_dir.is_dir():
            rem = list(old_dir.rglob("*"))
            if rem:
                leftover_files.extend(rem)
            else:
                old_dir.rmdir()
                removed_dirs += 1

    if leftover_files:
        print(f"[WARN] {len(leftover_files)} unexpected leftover entries in old dirs: {leftover_files[:5]}")

    for old_meta in (OLD_CATALOG_JSON, OLD_CATALOG_CSV):
        if old_meta.exists():
            old_meta.unlink()
    print(f"      Removed {removed_dirs} empty old category directories and old underscore catalog files.")

    print("[5/5] Writing Icons Catalog.json, Icons Catalog.csv, README.md, and running final audit...")
    write_catalogs_and_readme(old_catalog, plan)
    audit = audit_disk_state(expected_count)

    print("\n=== FINAL VERIFICATION AUDIT ===")
    print(f"  Expected icons:      {audit['expected_count']:,}")
    print(f"  PNGs on disk:        {audit['disk_png_count']:,}")
    print(f"  JSON catalog rows:   {audit['json_row_count']:,}")
    print(f"  CSV catalog rows:    {audit['csv_row_count']:,}")
    print(f"  Underscore paths:    {len(audit['underscore_paths'])}")
    print(f"  Em dash paths:       {len(audit['em_dash_paths'])}")
    print(f"  Em dash files:       {len(audit['em_dash_files'])}")
    print(f"  Avg stem length:     {audit['avg_stem_len']:.2f} chars")
    print(f"  Max stem length:     {audit['max_stem_len']} chars")
    print(f"  Top-level entries:   {audit['top_level_entries']}")

    ok = (
        audit["disk_png_count"] == expected_count
        and audit["json_row_count"] == expected_count
        and audit["csv_row_count"] == expected_count
        and len(audit["underscore_paths"]) == 0
        and len(audit["em_dash_paths"]) == 0
        and len(audit["em_dash_files"]) == 0
    )
    if not ok:
        print("[ERROR] Audit failed!", audit, file=sys.stderr)
        return 1

    print("\n[SUCCESS] All verification checks passed with 100% fidelity!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
