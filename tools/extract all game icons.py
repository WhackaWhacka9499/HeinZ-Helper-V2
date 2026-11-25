#!/usr/bin/env python3
"""
Extract every icon/sprite from Last Z AssetBundles and resources.assets.

Features:
- Strips the 8-byte b"UnityRaw" prefix before b"UnityFS" on Last Z .bundle files.
- Reads SpritePathCache (main_spritepathcache_all_*.bundle) for official Unity asset paths.
- Scans all main_atlas_*, main_sprites_*, main_emoji_all_*, icon/portrait/unit main_uitexture_*,
  main_loading_all_*, main_uilovemessage_*, and Survival_Data/resources.assets.
- Extracts individual sliced Sprites via UnityPy (spr.image), slices TMP_SpriteAsset ds_emoji
  glyphs cleanly, and exports standalone non-atlas Texture2Ds while strictly excluding raw uncut
  multi-icon SpriteAtlas texture sheets, font/number sheets, VFX masks, and opaque wallpapers.
- Tightly crops every icon edge-to-edge (alpha > 4 threshold, fallback getbbox(), min 4x4 px).
- Deduplicates by (category, sprite_name_lower) keeping the highest pixel-area image.
- Resolves official English names across english-dialog.txt, localization en.json, all XML JSON
  tables under megamind/raw/xml tables/, core resource overrides, ISO country codes, and Unicode
  emoji names.
- Outputs lossless PNGs under assets/icons/<category>/, plus icons_catalog.json,
  icons_catalog.csv, README.md, and a 48-icon verification contact sheet.
"""

from __future__ import annotations

import concurrent.futures
import csv
import datetime
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
import UnityPy


# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

GAME_DATA_DIR = Path(r"%LOCALAPPDATA%/Last Z\Game\Survival_Data")
ASSETBUNDLES_DIR = GAME_DATA_DIR / "StreamingAssets" / "AssetBundles"
RESOURCES_ASSETS = GAME_DATA_DIR / "resources.assets"

PROJECT_ROOT = Path(r".")
ENGLISH_DIALOG_PATH = PROJECT_ROOT / "launcher" / "assets" / "english-dialog.txt"
LOCALIZATION_JSON_PATH = PROJECT_ROOT / "megamind" / "raw" / "localization en.json"
XML_TABLES_DIR = PROJECT_ROOT / "megamind" / "raw" / "xml tables"

OUTPUT_ROOT = PROJECT_ROOT / "assets" / "icons"
CONTACT_SHEET_PATH = Path(
    r"data/cache/all_icons_sample_sheet.png"
)

CATEGORIES = [
    "resources",
    "items",
    "hero_portraits_round",
    "hero_portraits_small",
    "hero_portraits_large",
    "hero_fullbody",
    "hero_fragments",
    "hero_medals",
    "hero_equipment",
    "skills",
    "science_and_tech",
    "buildings",
    "troops_and_soldiers",
    "vehicles_and_aircraft",
    "monsters_and_bosses",
    "activities_and_events",
    "alliance_and_world",
    "flags",
    "emojis",
    "collectibles_and_fishing",
    "ui_hud",
    "misc",
]

# Bundles that are pure uncut atlas/font/3D world sheets (never icon sources)
SKIP_BUNDLE_SUBSTRINGS = (
    "main_sprites_worldstaticatlas_",
    "main_sprites_troopheadatlas_",
    "main_uitexture_floatingtext_",
)

# main_uitexture_* short names that are core icon/portrait/unit/card/building/hero bundles
# (never apply opaque wallpaper rejection to these)
ALWAYS_INCLUDE_UITEX = {
    "buildiconoutcity",
    "uiworldpoint",
    "uiworldpoint_s3",
    "uiworldpoint_s4",
    "uiworldpoint_s5",
    "itemheroskin",
    "herobody",
    "herobody2",
    "smallpeople",
    "fishingcatalog",
    "uitextureseason5card",
    "uidetectnpc",
    "uidog",
    "uisoildiernew",
    "uirobotex",
    "uiskinbox",
    "uitextureseason4dinosaur",
    "vx_ui_image",
}

# Core resource / currency official English overrides
CORE_RESOURCE_NAMES: dict[str, tuple[str, str, str]] = {
    "common_icon_money": ("Zent", "core_override", "14"),
    "common_icon_gold": ("Diamonds", "core_override", "15"),
    "common_icon_electricity": ("Electricity", "core_override", "12"),
    "common_icon_wood": ("Wood", "core_override", "2"),
    "ui_icon_shiwu": ("Food", "core_override", "1"),
    "common_icon_stamina": ("Fuel", "core_override", "3"),
    "common_icon_steel": ("Steel", "core_override", "29"),
    "common_icon_water": ("Water", "core_override", "11"),
    "common_icon_metal": ("Metal", "core_override", "9003"),
    "common_icon_people": ("Population", "core_override", "4"),
    "common_icon_radar": ("Radar Energy", "core_override", "20"),
    "common_icon_pvecode": ("PVE Code", "core_override", "17"),
    "common_icon_shuijing": ("Crystal", "core_override", "0"),
    "common_icon_xianrenzhang": ("Cactus", "core_override", "13"),
}

# Standard ISO 3166-1 alpha-2 country names (plus common Last Z flag codes)
ISO_COUNTRY_NAMES: dict[str, str] = {
    "ad": "Andorra", "ae": "United Arab Emirates", "af": "Afghanistan", "ag": "Antigua and Barbuda",
    "ai": "Anguilla", "al": "Albania", "am": "Armenia", "ao": "Angola", "aq": "Antarctica",
    "ar": "Argentina", "as": "American Samoa", "at": "Austria", "au": "Australia", "aw": "Aruba",
    "ax": "Aland Islands", "az": "Azerbaijan", "ba": "Bosnia and Herzegovina", "bb": "Barbados",
    "bd": "Bangladesh", "be": "Belgium", "bf": "Burkina Faso", "bg": "Bulgaria", "bh": "Bahrain",
    "bi": "Burundi", "bj": "Benin", "bl": "Saint Barthelemy", "bm": "Bermuda", "bn": "Brunei",
    "bo": "Bolivia", "bq": "Bonaire", "br": "Brazil", "bs": "Bahamas", "bt": "Bhutan",
    "bv": "Bouvet Island", "bw": "Botswana", "by": "Belarus", "bz": "Belize", "ca": "Canada",
    "cc": "Cocos Islands", "cd": "DR Congo", "cf": "Central African Republic", "cg": "Congo",
    "ch": "Switzerland", "ci": "Ivory Coast", "ck": "Cook Islands", "cl": "Chile", "cm": "Cameroon",
    "cn": "China", "co": "Colombia", "cp": "Clipperton Island", "cr": "Costa Rica", "cu": "Cuba",
    "cv": "Cape Verde", "cw": "Curacao", "cx": "Christmas Island", "cy": "Cyprus", "cz": "Czechia",
    "de": "Germany", "dj": "Djibouti", "dk": "Denmark", "dm": "Dominica", "do": "Dominican Republic",
    "dz": "Algeria", "ec": "Ecuador", "ee": "Estonia", "eg": "Egypt", "eh": "Western Sahara",
    "er": "Eritrea", "es": "Spain", "et": "Ethiopia", "eu": "European Union", "fi": "Finland",
    "fj": "Fiji", "fk": "Falkland Islands", "fm": "Micronesia", "fo": "Faroe Islands", "fr": "France",
    "ga": "Gabon", "gb": "United Kingdom", "gd": "Grenada", "ge": "Georgia", "gf": "French Guiana",
    "gg": "Guernsey", "gh": "Ghana", "gi": "Gibraltar", "gl": "Greenland", "gm": "Gambia",
    "gn": "Guinea", "gp": "Guadeloupe", "gq": "Equatorial Guinea", "gr": "Greece", "gs": "South Georgia",
    "gt": "Guatemala", "gu": "Guam", "gw": "Guinea-Bissau", "gy": "Guyana", "hk": "Hong Kong",
    "hm": "Heard Island", "hn": "Honduras", "hr": "Croatia", "ht": "Haiti", "hu": "Hungary",
    "id": "Indonesia", "ie": "Ireland", "il": "Israel", "im": "Isle of Man", "in": "India",
    "io": "British Indian Ocean Territory", "iq": "Iraq", "ir": "Iran", "is": "Iceland", "it": "Italy",
    "je": "Jersey", "jm": "Jamaica", "jo": "Jordan", "jp": "Japan", "ke": "Kenya", "kg": "Kyrgyzstan",
    "kh": "Cambodia", "ki": "Kiribati", "km": "Comoros", "kn": "Saint Kitts and Nevis",
    "kp": "North Korea", "kr": "South Korea", "kw": "Kuwait", "ky": "Cayman Islands",
    "kz": "Kazakhstan", "la": "Laos", "lb": "Lebanon", "lc": "Saint Lucia", "li": "Liechtenstein",
    "lk": "Sri Lanka", "lr": "Liberia", "ls": "Lesotho", "lt": "Lithuania", "lu": "Luxembourg",
    "lv": "Latvia", "ly": "Libya", "ma": "Morocco", "mc": "Monaco", "md": "Moldova",
    "me": "Montenegro", "mf": "Saint Martin", "mg": "Madagascar", "mh": "Marshall Islands",
    "mk": "North Macedonia", "ml": "Mali", "mm": "Myanmar", "mn": "Mongolia", "mo": "Macau",
    "mp": "Northern Mariana Islands", "mq": "Martinique", "mr": "Mauritania", "ms": "Montserrat",
    "mt": "Malta", "mu": "Mauritius", "mv": "Maldives", "mw": "Malawi", "mx": "Mexico",
    "my": "Malaysia", "mz": "Mozambique", "na": "Namibia", "nc": "New Caledonia", "ne": "Niger",
    "nf": "Norfolk Island", "ng": "Nigeria", "ni": "Nicaragua", "nl": "Netherlands", "no": "Norway",
    "np": "Nepal", "nr": "Nauru", "nu": "Niue", "nz": "New Zealand", "om": "Oman", "pa": "Panama",
    "pe": "Peru", "pf": "French Polynesia", "pg": "Papua New Guinea", "ph": "Philippines",
    "pk": "Pakistan", "pl": "Poland", "pm": "Saint Pierre and Miquelon", "pn": "Pitcairn",
    "pr": "Puerto Rico", "ps": "Palestine", "pt": "Portugal", "pw": "Palau", "py": "Paraguay",
    "qa": "Qatar", "re": "Reunion", "ro": "Romania", "rs": "Serbia", "ru": "Russia", "rw": "Rwanda",
    "sa": "Saudi Arabia", "sb": "Solomon Islands", "sc": "Seychelles", "sd": "Sudan", "se": "Sweden",
    "sg": "Singapore", "sh": "Saint Helena", "si": "Slovenia", "sj": "Svalbard", "sk": "Slovakia",
    "sl": "Sierra Leone", "sm": "San Marino", "sn": "Senegal", "so": "Somalia", "sr": "Suriname",
    "ss": "South Sudan", "st": "Sao Tome and Principe", "sv": "El Salvador", "sx": "Sint Maarten",
    "sy": "Syria", "sz": "Eswatini", "tc": "Turks and Caicos", "td": "Chad", "tf": "French Southern Territories",
    "tg": "Togo", "th": "Thailand", "tj": "Tajikistan", "tk": "Tokelau", "tl": "Timor-Leste",
    "tm": "Turkmenistan", "tn": "Tunisia", "to": "Tonga", "tr": "Turkey", "tt": "Trinidad and Tobago",
    "tv": "Tuvalu", "tw": "Taiwan", "tz": "Tanzania", "ua": "Ukraine", "ug": "Uganda",
    "uk": "United Kingdom", "um": "US Minor Outlying Islands", "un": "United Nations",
    "us": "United States", "uy": "Uruguay", "uz": "Uzbekistan", "va": "Vatican City",
    "vc": "Saint Vincent and the Grenadines", "ve": "Venezuela", "vg": "British Virgin Islands",
    "vi": "US Virgin Islands", "vn": "Vietnam", "vu": "Vanuatu", "wf": "Wallis and Futuna",
    "ws": "Samoa", "xk": "Kosovo", "ye": "Yemen", "yt": "Mayotte", "za": "South Africa",
    "zm": "Zambia", "zw": "Zimbabwe",
    "arabic": "Arabic", "england": "England", "scotland": "Scotland", "wales": "Wales",
    "flag_un": "United Nations", "other": "Other Region",
}

XML_TABLE_PRIORITY: dict[str, int] = {
    "aps_resources": 100,
    "aps_resource_item": 98,
    "goods": 95,
    "aps_new_heroes": 94,
    "aps_new_heros_skin": 92,
    "building": 91,
    "ds_equip": 90,
    "heroes_exclusive_equip": 90,
    "exclusive_equip_breakthrough": 89,
    "c_equips": 88,
    "lw_hero_skill": 88,
    "skill": 87,
    "season_active_skill": 86,
    "aps_science": 86,
    "alscience": 85,
    "alsciencetab": 84,
    "aps_science_tab": 84,
    "aps_talent": 84,
    "aps_arms": 83,
    "aps_monster": 82,
    "car_compon": 81,
    "car_microchip": 81,
    "car_show": 81,
    "car_talent": 80,
    "car_transform": 80,
    "icecave_fish": 80,
    "bauble": 80,
    "bauble_rating": 79,
    "shelter_emoji": 79,
    "aps_city_buff": 78,
    "alliance_gift_group": 77,
    "alliance_resource": 77,
    "alliance_res_build": 77,
    "alliance_skill": 77,
    "alliance_effect": 77,
    "alliance_task": 76,
    "love_message_hero": 76,
    "flag_effect": 76,
    "dragon_building": 75,
    "food_festival_building": 75,
    "activity_panel": 74,
    "activity_item_drop": 74,
    "activity_monster": 74,
    "aps_gather_resource": 73,
    "aps_factory": 73,
    "aps_farming": 73,
    "aps_dispatch_tasks": 72,
    "aps_landlock": 71,
    "aps_season": 70,
    "aps_season_group": 70,
    "aps_heroes_rank": 69,
    "aps_heroes_ranklv": 69,
    "hero_tag": 68,
    "building_direction": 67,
    "building_status": 67,
    "aps_country": 66,
}

RICH_TAG_RE = re.compile(r"<[^>]+>")
WIN_FORBIDDEN_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTI_SPACE_RE = re.compile(r"\s+")
HERO_BODY_NAME_RE = re.compile(r"^hero_\d+(?:_[a-z0-9]+)*$", re.IGNORECASE)
EMOJI_HEX_RE = re.compile(r"^[0-9a-f]{4,6}(?:-[0-9a-f]{4,6})*$", re.IGNORECASE)
RESERVED_WIN_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


# ---------------------------------------------------------------------------
# Helpers: Text cleaning, Unity loading, Localization & XML Name Resolver
# ---------------------------------------------------------------------------

def strip_em_dash(text: str) -> str:
    """Replace any em dash or en dash with plain ASCII hyphen."""
    return text.replace("\u2014", "-").replace("\u2013", "-")


def clean_display_text(text: str) -> str:
    """Strip Unity rich-text tags, newlines, control chars, and em dashes."""
    if not text:
        return ""
    s = RICH_TAG_RE.sub("", str(text))
    s = s.replace("\\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = strip_em_dash(s)
    s = MULTI_SPACE_RE.sub(" ", s).strip()
    return s


def sanitize_filename_part(text: str, max_len: int = 64) -> str:
    """Sanitize a string component for Windows filenames."""
    s = strip_em_dash(text)
    s = WIN_FORBIDDEN_RE.sub("_", s)
    s = s.replace(" ", "_")
    s = re.sub(r"_+", "_", s).strip("._ ")
    if len(s) > max_len:
        s = s[:max_len].rstrip("._ ")
    if not s or s.lower() in RESERVED_WIN_NAMES:
        s = f"icon_{s}" if s else "icon"
    return s


def build_safe_filename(english_name: str, sprite_name: str, max_total_len: int = 110) -> str:
    """Build Windows-safe filename <= max_total_len chars including .png."""
    ext = ".png"
    budget = max_total_len - len(ext)
    safe_sprite = sanitize_filename_part(sprite_name, max_len=budget)
    if english_name:
        # Reserve space for __<safe_sprite>
        sep = "__"
        if len(safe_sprite) > 52:
            safe_sprite = safe_sprite[:52].rstrip("._ ")
        eng_budget = max(16, budget - len(sep) - len(safe_sprite))
        safe_eng = sanitize_filename_part(english_name, max_len=eng_budget)
        if safe_eng and safe_eng.lower() != safe_sprite.lower():
            stem = f"{safe_eng}{sep}{safe_sprite}"
        else:
            stem = safe_sprite
    else:
        stem = safe_sprite
    if len(stem) > budget:
        stem = stem[:budget].rstrip("._ ")
    if stem.lower() in RESERVED_WIN_NAMES:
        stem = f"icon_{stem}"
    return stem + ext


def load_unity_env(path: Path) -> Any:
    """Load a Last Z .bundle (stripping UnityRaw prefix) or .assets file."""
    if path.suffix.lower() == ".bundle":
        raw = path.read_bytes()
        if raw.startswith(b"UnityRawUnityFS"):
            raw = raw[8:]
        return UnityPy.load(raw)
    return UnityPy.load(str(path))


def load_sprite_path_cache() -> dict[str, str]:
    """Read main_spritepathcache_all_*.bundle -> {fileName_lower: fullPath}."""
    matches = sorted(ASSETBUNDLES_DIR.glob("main_spritepathcache_all_*.bundle"))
    if not matches:
        print("[WARN] SpritePathCache bundle not found!")
        return {}
    env = load_unity_env(matches[0])
    cache: dict[str, str] = {}
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            entries = tree.get("entries", [])
            for entry in entries:
                fn = str(entry.get("fileName", "")).strip()
                fp = str(entry.get("fullPath", "")).replace("\\", "/").strip()
                if fn and fp:
                    key = fn.lower()
                    if key not in cache:
                        cache[key] = fp
    return cache


def load_english_strings() -> dict[str, str]:
    """Load and merge localization en.json and english-dialog.txt."""
    strings: dict[str, str] = {}
    if LOCALIZATION_JSON_PATH.exists():
        data = json.loads(LOCALIZATION_JSON_PATH.read_text(encoding="utf-8", errors="replace"))
        src = data.get("strings", data) if isinstance(data, dict) else {}
        if isinstance(src, dict):
            for k, v in src.items():
                cleaned = clean_display_text(str(v))
                if cleaned:
                    strings[str(k).strip()] = cleaned
    if ENGLISH_DIALOG_PATH.exists():
        with ENGLISH_DIALOG_PATH.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                cleaned = clean_display_text(v)
                if k and cleaned:
                    strings[k] = cleaned
    return strings


def is_valid_english_name(text: str) -> bool:
    """Filter out raw numeric IDs, Lua table dumps, unresolved templates, asset filenames, and long descriptions."""
    if not text or len(text) < 2 or len(text) > 78:
        return False
    tl = text.lower()
    if tl.startswith("table:") or tl in ("default", "none", "null", "0", "1", "test"):
        return False
    if text.isdigit():
        return False
    # Reject unresolved format-string templates like "{0} Fragment" or "Defeat {0} {1}"
    if "{0}" in text or "{1}" in text or "{2}" in text or "%s" in text or "%d" in text:
        return False
    if not any(ch.isalpha() for ch in text):
        return False
    # Reject obvious internal snake_case asset filenames (2+ underscores and no spaces)
    if " " not in text and text.count("_") >= 2:
        return False
    if " " not in text and tl.startswith(("ui_", "c_", "hero_", "building_", "arms_", "item_", "eff_", "vx_")):
        return False
    return True


def resolve_name_token(raw_val: str, loc: dict[str, str]) -> str:
    """Resolve a localization ID or clean literal English string."""
    if not raw_val:
        return ""
    s = str(raw_val).strip()
    if not s or s == "0" or s.startswith("table:"):
        return ""
    if s in loc:
        cand = loc[s]
        if is_valid_english_name(cand):
            return cand
        return ""
    # Sometimes a numeric id has trailing .0 or spaces
    if s.endswith(".0") and s[:-2] in loc:
        cand = loc[s[:-2]]
        if is_valid_english_name(cand):
            return cand
    # Literal text fallback
    cleaned = clean_display_text(s)
    if is_valid_english_name(cleaned):
        return cleaned
    return ""


def iter_xml_rows(data: Any) -> list[tuple[str, dict[str, str]]]:
    """Normalize any Last Z xml_tables JSON schema into [(row_id, {col: val_str})]."""
    out: list[tuple[str, dict[str, str]]] = []
    if isinstance(data, dict) and "columns" in data and "rows" in data:
        cols = [str(c) for c in data["columns"]]
        rows = data["rows"]
        if isinstance(rows, dict):
            for rid, rvals in rows.items():
                if isinstance(rvals, list):
                    row_dict = {cols[i]: ("" if rvals[i] is None else str(rvals[i])) for i in range(min(len(cols), len(rvals)))}
                    out.append((str(rid), row_dict))
                elif isinstance(rvals, dict):
                    out.append((str(rid), {str(k): ("" if v is None else str(v)) for k, v in rvals.items()}))
        elif isinstance(rows, list):
            for idx, rvals in enumerate(rows):
                if isinstance(rvals, list):
                    row_dict = {cols[i]: ("" if rvals[i] is None else str(rvals[i])) for i in range(min(len(cols), len(rvals)))}
                    rid = row_dict.get("id", str(idx))
                    out.append((str(rid), row_dict))
                elif isinstance(rvals, dict):
                    rid = str(rvals.get("id", idx))
                    out.append((rid, {str(k): ("" if v is None else str(v)) for k, v in rvals.items()}))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                rid = str(item.get("id", idx))
                out.append((rid, {str(k): ("" if v is None else str(v)) for k, v in item.items()}))
    elif isinstance(data, dict):
        for rid, item in data.items():
            if isinstance(item, dict):
                out.append((str(rid), {str(k): ("" if v is None else str(v)) for k, v in item.items()}))
    return out


def is_icon_column(col: str) -> bool:
    """Return True if an XML column likely stores sprite/icon asset names."""
    cl = col.lower()
    # Explicitly exclude non-icon columns
    bad_exact = {
        "icon_type", "alicon_height", "bg_pic", "image_bg", "spin_bg_icon", "reward_bg_icon",
        "bg_icon", "res_bg", "res_bg_gray", "flag_effect_bg", "chat_unlock_pic_type",
        "pic_none", "bg_pic_change", "icon_value", "model", "model_name", "model_name_new",
        "model_path", "simple_model_path", "city_model_path", "show_model_path",
        "model_world", "s2_model", "model_point", "model_size", "show_model_scale",
        "skin_name", "skin_cv", "default_skin", "awakening_skin", "flag_effect_title",
        "flag_effect_effect", "flag_effect_season", "res_size", "res_durable",
        "res_base_durable", "res_num", "res_durable_b", "res_base_durable_b",
        "resource_need", "treat_resource", "research_need", "resource_type",
        "resourcetype", "resource", "resource_goods", "resource_item", "input_resource",
        "input_resource_goods", "get_resource_goods", "get_by_resource_goods",
        "enter_resource_cost", "use_res_type", "use_res_param", "res_queue_stop",
        "restricted_reward", "partake_reward", "reward_participate", "medals_parm",
        "cost_medal", "featureicon", "iconlist", "topiclist",
    }
    if cl in bad_exact:
        return False
    if any(b in cl for b in ("_bg", "bg_", "_type", "_size", "_num", "_cost", "_count", "_rate", "_time", "_cd", "_height", "_scale", "_durable", "_need", "model", "spine", "prefab", "sound", "effect_id", "unlock_")):
        if cl not in ("unlock_pic", "unlock_pic_j", "unlock_image", "icon_unlock"):
            return False
    good_keys = (
        "icon", "pic", "sprite", "head", "avatar", "bust", "body", "halfbody", "wholebody",
        "portrait", "thumb", "badge", "medal", "image", "img", "photo", "flg", "flag",
        "hero_refresh",
    )
    return any(k in cl for k in good_keys)


NAME_COL_PREFERENCE = [
    "name", "skin_name", "hero_name", "item_name", "skill_name", "title", "name_new",
    "name1", "season_name", "map_name", "product_name", "reward_name", "landname",
    "chat_name", "difficulty_title", "flag_effect_title", "effect_title", "sub_name",
    "career_name", "btn_name",
]


def extract_sprite_tokens(raw_val: str) -> list[str]:
    """Parse one or more sprite names from an XML icon cell."""
    if not raw_val:
        return []
    s = str(raw_val).strip()
    if not s or s == "0" or s.startswith("table:"):
        return []
    tokens: list[str] = []
    for part in re.split(r"[;|,]", s):
        part = part.strip()
        if not part or part == "0":
            continue
        # Handle optional "path/to/sprite.png" or "weight:sprite"
        if ":" in part and not part.lower().startswith("http"):
            sub = part.split(":")[-1].strip()
            if sub:
                part = sub
        part = part.replace("\\", "/").split("/")[-1]
        if part.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".tga")):
            part = part.rsplit(".", 1)[0]
        part = part.strip()
        # Reject pure numbers or single-character garbage (except 2-char country codes)
        if not part or part.isdigit():
            continue
        if len(part) < 2:
            continue
        tokens.append(part)
    return tokens


def build_english_name_map(loc: dict[str, str]) -> dict[str, dict[str, Any]]:
    """
    Scan ALL XML JSON tables under megamind/raw/xml tables/ and build:
      sprite_name_lower -> {"english_name": str, "xml_table": str, "xml_id": str, "priority": int}
    """
    name_map: dict[str, dict[str, Any]] = {}

    def register(sprite_key: str, eng: str, table: str, rid: str, prio: int) -> None:
        sk = sprite_key.strip().lower()
        if not sk or not eng:
            return
        eng = clean_display_text(eng)
        if not is_valid_english_name(eng):
            return
        prev = name_map.get(sk)
        if prev is None or prio > prev["priority"]:
            name_map[sk] = {
                "english_name": eng,
                "xml_table": table,
                "xml_id": str(rid),
                "priority": prio,
            }

    # 1. Core resource overrides (highest priority)
    for sk, (eng, tbl, rid) in CORE_RESOURCE_NAMES.items():
        register(sk, eng, tbl, rid, 200)

    if not XML_TABLES_DIR.exists():
        print("[WARN] xml_tables dir not found!")
        return name_map

    xml_files = sorted(XML_TABLES_DIR.glob("*.json"))
    existing_stems = {p.stem.lower() for p in xml_files}

    # Pre-load real playable hero_id -> hero_name and hero_art_code -> hero_name from aps_new_heroes
    hero_id_to_name: dict[str, str] = {}
    hero_code_to_info: dict[str, tuple[str, str]] = {}  # code -> (hero_name, hero_id)
    heroes_path = XML_TABLES_DIR / "aps new heroes.json"
    if heroes_path.exists():
        try:
            hdata = json.loads(heroes_path.read_text(encoding="utf-8", errors="replace"))
            for rid, row in iter_xml_rows(hdata):
                hname = resolve_name_token(row.get("name", ""), loc)
                if not hname:
                    continue
                hero_id_to_name[rid] = hname
                if row.get("id"):
                    hero_id_to_name[row["id"]] = hname
                # Skip legacy placeholder rows (herohead_S_01 / round_hero_icon_*)
                hi = str(row.get("hero_icon", "")).strip()
                ri = str(row.get("round_hero_icon", "")).strip()
                if hi == "herohead_S_01" or ri.startswith("round_hero_icon_"):
                    continue
                m = re.match(r"^hero_round_(\d+(?:_[a-z0-9]+)?)$", ri, re.IGNORECASE)
                if not m:
                    m = re.match(r"^hero_head_s_(\d+(?:_[a-z0-9]+)?)$", hi, re.IGNORECASE)
                if m:
                    code = m.group(1).lower()
                    hero_code_to_info.setdefault(code, (hname, rid))
                    if code.isdigit():
                        num = int(code)
                        hero_code_to_info.setdefault(f"{num:02d}", (hname, rid))
                        hero_code_to_info.setdefault(f"{num:03d}", (hname, rid))
                        hero_code_to_info.setdefault(str(num), (hname, rid))
        except Exception:
            pass

    # Register derived hero fragment, medal, portrait, and fullbody names from verified real heroes
    for code, (hname, hid) in hero_code_to_info.items():
        register(f"hero_fragment_{code}", f"{hname} Fragment", "aps_new_heroes", hid, 97)
        register(f"hero_medal_{code}", f"{hname} Medal", "aps_new_heroes", hid, 97)
        register(f"herohead_medal_{code}", f"{hname} Medal", "aps_new_heroes", hid, 97)
        register(f"hero_round_{code}", hname, "aps_new_heroes", hid, 95)
        register(f"hero_head_s_{code}", hname, "aps_new_heroes", hid, 95)
        register(f"hero_head_l_{code}", hname, "aps_new_heroes", hid, 95)
        register(f"hero_troops_{code}", hname, "aps_new_heroes", hid, 95)
        register(f"hero_{code}", hname, "aps_new_heroes", hid, 95)
        register(f"hero_refresh_{code}", hname, "aps_new_heroes", hid, 95)

    tables_scanned = 0
    for xf in xml_files:
        stem = xf.stem
        stem_lower = stem.lower()
        # Skip duplicate luadatatable_LuaDatatable.<name>.json if <name>.json exists
        if stem_lower.startswith("luadatatable_luadatatable."):
            short = stem_lower[len("luadatatable_luadatatable."):]
            if short in existing_stems:
                continue
        tables_scanned += 1
        try:
            data = json.loads(xf.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

        rows = iter_xml_rows(data)
        if not rows:
            continue

        sample_cols = list(rows[0][1].keys())
        icon_cols = [c for c in sample_cols if is_icon_column(c)]
        if not icon_cols:
            continue

        # Ordered candidate name columns in this table
        col_lower_map = {c.lower(): c for c in sample_cols}
        name_cols: list[str] = []
        for pref in NAME_COL_PREFERENCE:
            if pref in col_lower_map:
                name_cols.append(col_lower_map[pref])
        # Also include any other *name*/*title* column that isn't an asset filename
        for c in sample_cols:
            cl = c.lower()
            if c not in name_cols and ("name" in cl or "title" in cl):
                if not any(bad in cl for bad in ("model", "pic", "file", "icon", "prefab", "spine", "atlas", "table", "anim", "audio", "sound", "cv")):
                    name_cols.append(c)

        if not name_cols:
            continue

        base_prio = XML_TABLE_PRIORITY.get(stem_lower, 50)
        if "_client_b" in stem_lower:
            base_prio -= 15
        if stem_lower.startswith("luadatatable_"):
            base_prio -= 10

        for rid, row in rows:
            # Skip legacy placeholder rows in aps_new_heroes* so they never poison real heroes
            if stem_lower in ("aps_new_heroes", "aps_new_heroes_client_b"):
                hi = str(row.get("hero_icon", "")).strip()
                ri = str(row.get("round_hero_icon", "")).strip()
                if hi == "herohead_S_01" or ri.startswith("round_hero_icon_"):
                    continue

            # Special handling for aps_new_heros_skin
            if stem_lower == "aps_new_heros_skin":
                hero_nm = hero_id_to_name.get(str(row.get("hero_id", "")), "")
                raw_skin = row.get("skin_name", "")
                skin_nm = loc.get(str(raw_skin).strip(), "") if raw_skin else ""
                skin_nm = clean_display_text(skin_nm)
                if skin_nm.lower() == "default" or not skin_nm:
                    resolved = hero_nm
                elif hero_nm and not skin_nm.lower().startswith(hero_nm.lower()):
                    resolved = f"{hero_nm} - {skin_nm}"
                else:
                    resolved = skin_nm
                if resolved:
                    for ic in icon_cols:
                        for tok in extract_sprite_tokens(row.get(ic, "")):
                            # Don't override base hero portrait from aps_new_heroes if prio is lower
                            register(tok, resolved, stem, rid, base_prio)
                continue

            # Special handling for exclusive_equip_breakthrough (pair skill_icon -> skill_name)
            skill_name_resolved = ""
            if "skill_name" in col_lower_map:
                skill_name_resolved = resolve_name_token(row.get(col_lower_map["skill_name"], ""), loc)

            # Resolve primary English name for this row
            row_name = ""
            raw_name_cell = ""
            for nc in name_cols:
                raw_v = row.get(nc, "")
                cand = resolve_name_token(raw_v, loc)
                if cand:
                    row_name = cand
                    raw_name_cell = raw_v
                    break

            # Special case: aps_country uses 2-letter code in 'name'/'flg'
            if stem_lower == "aps_country":
                code = str(row.get("flg") or row.get("country") or "").strip()
                if code:
                    cname = ISO_COUNTRY_NAMES.get(code.lower(), "")
                    if cname:
                        register(code, cname, stem, rid, base_prio)
                continue

            if not row_name and not skill_name_resolved:
                continue

            # Check if name cell is semicolon-separated list matching icon cell
            raw_name_parts = [p.strip() for p in re.split(r"[;|]", raw_name_cell)] if (raw_name_cell and (";" in raw_name_cell or "|" in raw_name_cell)) else []

            for ic in icon_cols:
                ic_val = row.get(ic, "")
                tokens = extract_sprite_tokens(ic_val)
                if not tokens:
                    continue
                is_skill_col = "skill" in ic.lower()
                for idx_t, tok in enumerate(tokens):
                    eng = skill_name_resolved if (is_skill_col and skill_name_resolved) else row_name
                    if raw_name_parts and idx_t < len(raw_name_parts):
                        paired = resolve_name_token(raw_name_parts[idx_t], loc)
                        if paired:
                            eng = paired
                    if eng:
                        # Slightly boost exact 'icon'/'pic'/'hero_icon' columns over secondary columns
                        col_boost = 2 if ic.lower() in ("icon", "pic", "hero_icon", "round_hero_icon", "skin_icon", "hero_body_2d") else 0
                        register(tok, eng, stem, rid, base_prio + col_boost)

    # 2. ISO country code fallbacks (only for keys not already mapped)
    for code, cname in ISO_COUNTRY_NAMES.items():
        register(code, cname, "iso_3166_country", code.upper(), 30)

    print(f"[INFO] Scanned {tables_scanned} XML tables -> {len(name_map)} sprite English name mappings.")
    return name_map


def lookup_emoji_english_name(sprite_name: str) -> str:
    """Resolve Unicode hex codepoint emoji names like 1f60e or 263a-fe0f via unicodedata."""
    s = sprite_name.strip().lower()
    if not EMOJI_HEX_RE.match(s):
        return ""
    parts = [p for p in s.split("-") if p not in ("fe0f", "200d")]
    if not parts:
        return ""
    names = []
    for p in parts:
        try:
            cp = int(p, 16)
            nm = unicodedata.name(chr(cp), "")
            if nm:
                names.append(nm.title())
        except Exception:
            pass
    if names:
        return clean_display_text(" ".join(names[:2]))
    return ""


# ---------------------------------------------------------------------------
# Categorization into exact 22 clean category folders
# ---------------------------------------------------------------------------

def classify_icon(
    sprite_name: str,
    unity_path: str,
    bundle_name: str,
    xml_table: str,
) -> str:
    """Classify an extracted icon into one of the 22 canonical categories."""
    sn = sprite_name.lower()
    up = unity_path.lower().replace("\\", "/")
    bn = bundle_name.lower()
    xt = xml_table.lower()

    # 1. Resources (pure resources, excluding ResLackIcons shortcut popups for activities/items/buildings)
    if (
        "/sprites/resource/" in up
        or sn in CORE_RESOURCE_NAMES
        or xt in ("aps_resources", "aps_resource_item", "aps_gather_resource")
        or any(sn.startswith(p) for p in ("res_season_", "c_season_icon_", "c_vocano_res_icon_", "common_icon_res_", "res_3000"))
        or bn.startswith("main_atlas_resource_")
        or bn.startswith("main_sprites_resource_")
    ):
        return "resources"

    # 2. Emojis
    if (
        "/itemicons_emoji/" in up
        or "/marchemoji/" in up
        or bn.startswith("main_emoji_all_")
        or "emoji" in bn
        or xt == "shelter_emoji"
        or sn.startswith(("alliancejoin_", "c_emoji_", "marchemoji", "emoji_"))
        or EMOJI_HEX_RE.match(sn)
    ):
        return "emojis"

    # 3. Flags
    if (
        "/countryflag/" in up
        or "/uiallianceflag/" in up
        or "/uiseasonallianceflag/" in up
        or "countryflag" in bn
        or "allianceflag" in bn
        or xt in ("flag_effect", "aps_country")
    ):
        return "flags"

    # 4. Hero Fragments
    if (
        "/itemicons_herofragment" in up
        or "herofragment" in bn
        or "hero_fragment" in sn
        or "herofragment" in sn
    ):
        return "hero_fragments"

    # 5. Hero Medals
    if (
        "/itemicons_heromedal" in up
        or "heromedal" in bn
        or "herohead_medal" in sn
        or "hero_medal" in sn
    ):
        return "hero_medals"

    # 6. Monsters & Bosses (before hero portraits so hero_round_monster_* lands here!)
    if (
        "/uimonstertower/" in up
        or "/uiportraitbosscoming/" in up
        or "/uidragon/" in up
        or "/uiportraitactdragon/" in up
        or "/uiattzombiepuzzle/" in up
        or "/uiportraitzombiepuzzle/" in up
        or "/uitextureseason4dinosaur/" in up
        or "/pvenew/" in up
        or "/uipvemain/" in up
        or "/uibarrel/" in up
        or "/uivolcano/" in up
        or any(k in bn for k in ("monster", "dragon", "zombie", "dinosaur", "bosscoming", "pvenew", "uipvemain", "uibarrel", "uivolcano"))
        or xt in ("aps_monster", "activity_monster", "activity_puzzle_monster", "aps_monsterlock", "aps_pve_zombie", "aps_pve_part_zombie")
        or any(k in sn for k in ("monster", "zombie", "dinosaur", "boss_"))
    ):
        return "monsters_and_bosses"

    # 7. Hero Portraits Round
    if (
        "/heroiconssmall_heroround/" in up
        or "heroround" in bn
        or sn.startswith("hero_round_")
    ):
        return "hero_portraits_round"

    # 8. Hero Portraits Small (exclude building skins like *_dajianzhu* in UIHeadIcon)
    if (
        (
            "/heroiconssmall" in up
            or "/girliconssmall/" in up
            or "/itemicons_skinhead/" in up
            or "/uiheadicon/" in up
            or any(k in bn for k in ("heroiconssmall", "girliconssmall", "skinhead", "uiheadicon"))
            or sn.startswith(("hero_head_s_", "hero_head_people_", "hero_refresh_", "girl_head_"))
        )
        and not any(bk in sn for bk in ("dajianzhu", "building_", "castle"))
    ):
        return "hero_portraits_small"

    # 9. Hero Portraits Large (exclude popup panel backgrounds c_xr_bg_tc* / dadiban)
    if (
        (
            "/heroiconsbig/" in up
            or "/devheroiconsbig/" in up
            or "/herobodytroops/" in up
            or "/smallpeople/" in up
            or "/uidetectnpc/" in up
            or any(k in bn for k in ("heroiconsbig", "devheroiconsbig", "herobodytroops", "smallpeople", "uidetectnpc"))
            or sn.startswith(("hero_head_l_", "hero_troops_", "detect_img_linshirole"))
        )
        and not any(bk in sn for bk in ("_bg_", "dadiban", "bg_tc"))
    ):
        return "hero_portraits_large"

    # 10. Hero Fullbody (actual hero fullbody art; NOT portrait-screen UI panels in UIPortraitHero!)
    if (
        "/uitexture/herobody" in up
        or "/uitexture/itemheroskin" in up
        or "/uiportrait/uiportraitgirlunlock" in up
        or "/uitexture/uitexturegirlunlock" in up
        or "/uiherodress/" in up
        or "/uigirlselect/" in up
        or bn.startswith(("main_uitexture_herobody_", "main_uitexture_herobody2_", "main_uitexture_itemheroskin_", "main_uilovemessage_", "main_uitexture_vx_ui_image_"))
        or any(k in bn for k in ("girlunlock", "uiherodress", "uigirlselect"))
        or HERO_BODY_NAME_RE.match(sn)
        or sn.startswith(("love_message_", "vx_season_hero_"))
    ):
        return "hero_fullbody"

    # 11. Hero Equipment (exclude UI panel frames/backgrounds like G_ZB_YOUCEDIKUANG / redgear_chenggong_di)
    if (
        (
            "/heroequipicons/" in up
            or "/itemicons_equip/" in up
            or "/uiheroequip/" in up
            or "/uiredgear/" in up
            or any(k in bn for k in ("heroequip", "itemicons_equip", "uiredgear"))
            or xt in ("c_equips", "ds_equip", "heroes_exclusive_equip", "exclusive_equip_breakthrough", "ds_equip_material", "ds_equip_mythical")
            or sn.startswith(("c_equip_", "equip_", "uiarms_icon_", "hero_equip_"))
        )
        and not any(bk in sn for bk in ("dikuang", "zhezhao", "chenggong_di", "_bg"))
    ):
        return "hero_equipment"

    # 12. Skills
    if (
        "/skillicons/" in up
        or "/sprites/ui/buff/" in up
        or "/sprites/ui/buff_trigger/" in up
        or any(k in bn for k in ("skillicons", "_ui_buff_", "_ui_buff_trigger_"))
        or xt in ("skill", "lw_hero_skill", "season_active_skill", "alliance_skill", "aps_city_buff", "aps_pve_buff", "aps_pve_battlebuff")
        or sn.startswith(("skill_icon", "pve_skill_", "buff_icon", "hero_skill_"))
    ):
        return "skills"

    # 13. Science & Tech
    if (
        "/scienceicons" in up
        or "/itemicons_seasontalent/" in up
        or "/uiscience/" in up
        or "/uiportraitseasontalent/" in up
        or "/uitextureseasontalent/" in up
        or "/uimastery/" in up
        or any(k in bn for k in ("scienceicons", "seasontalent", "uiscience", "uimastery"))
        or xt in ("aps_science", "alscience", "alsciencetab", "aps_science_tab", "aps_talent")
        or sn.startswith(("uitechnology_icon_", "science_", "tech_icon_"))
    ):
        return "science_and_tech"

    # 14. Buildings
    if (
        "/buildiconoutcity/" in up
        or "/itemicons_building/" in up
        or "/uibuild/" in up
        or "/uibuildbtns/" in up
        or "/uibuildbubble/" in up
        or "/uibuildupgradenew/" in up
        or any(k in bn for k in ("buildiconoutcity", "itemicons_building", "uibuild"))
        or xt in ("building", "dragon_building", "food_festival_building", "alliance_res_build", "building_direction", "building_status")
        or sn.startswith(("building_", "a_build_", "uiseason_icon_build", "uiseason4_build_", "uiseason5_build_"))
        or "dajianzhu" in sn
    ):
        return "buildings"

    # 15. Troops & Soldiers
    if (
        "/soldiericons/" in up
        or "/uitroopsnew/" in up
        or "/uiworldtroop/" in up
        or "/uisoildiernew/" in up
        or any(k in bn for k in ("soldiericons", "uitroopsnew", "uiworldtroop", "uisoildiernew"))
        or xt == "aps_arms"
        or xt.startswith("army")
        or sn.startswith(("arms_icon_", "arms_image_", "soldier_"))
    ):
        return "troops_and_soldiers"

    # 16. Vehicles & Aircraft
    if (
        "/tankworld2d/" in up
        or "/itemicons_aircraft/" in up
        or "/uiaircraft" in up
        or "/uijeepadvent" in up
        or "/heroiconssmall_cartalent/" in up
        or "uicarchip" in up
        or any(k in bn for k in ("tankworld2d", "aircraft", "uijeep", "cartalent", "carchip"))
        or xt.startswith("car_")
        or sn.startswith(("car_", "tank_", "aircraft_", "jeep_"))
    ):
        return "vehicles_and_aircraft"

    # 17. Collectibles & Fishing
    if (
        "/fishicons/" in up
        or "/fishingcatalog/" in up
        or "/baubleicon/" in up
        or "/uitextureseason5card/" in up
        or "/clueitem/" in up
        or "/uidog/" in up
        or "/uivivian/" in up
        or "/itemicons_vivien/" in up
        or "/uiportraitphonograph/" in up
        or "/uiportraitdecoration/" in up
        or "/uiportraitpresent/" in up
        or any(k in bn for k in ("fishicons", "fishingcatalog", "baubleicon", "season5card", "clueitem", "uidog", "vivien", "vivian", "phonograph", "uiportraitdecoration", "uiportraitpresent"))
        or xt in ("icecave_fish", "bauble", "bauble_rating")
        or any(k in sn for k in ("icecave_fish", "fishcard", "bauble", "moonlight_card", "item_collection_"))
    ):
        return "collectibles_and_fishing"

    # 18. Items (all remaining ItemIcons* and goods)
    if (
        "/sprites/itemicons" in up
        or "itemicons" in bn
        or (xt in ("goods", "aps_purchase_order", "aps_factory", "aps_farming") and not sn.startswith("activity_icon_"))
        or sn.startswith(("item_", "item4", "goods_"))
    ):
        return "items"

    # 19. Activities & Events
    if (
        "/sprites/activityicons" in up
        or "/uibigactivity/" in up
        or "/uiactivity" in up
        or "/uitextureactivity" in up
        or "/uiportraitactivity" in up
        or any(k in up for k in (
            "/uitexturechristmas", "/uiportraitchristmas", "/uitexturehalloween",
            "/uitextureoktoberfest", "/uitexturethanksgiving", "/uitexturefoodfestival",
            "/uifoodfestival", "/uitexturevalentinefox", "/uitextureeaster",
            "/uitexturegivingroses", "/uiportraitgivingroses", "/uicarnival",
            "/uiluckyroll", "/uixmasluckyroll", "/uiredenvelope",
            "/uiportraitworldcup", "/uitextureworldcup", "/uisevenday", "/uisevenlogin",
            "/battlepass", "/seasonpass", "/uiweekcard", "/uipopuppackage",
            "/uigiftpackage", "/uifirstpay", "/uiscrollpack", "/uitextureshop",
            "/uiportraitshop", "/uishop", "/uipersonalarms", "/uiportraitmatchinggame",
            "/uiportraitchampionbattle", "/uitexturechampionbattle", "/uitexturedominate",
            "/uiportraitexplore", "/uitextureexplore", "/uiworldtrend", "/uiradarcenter",
            "/uiminecave", "/uiagechange", "/uitexturecastle", "/uinewseason",
            "/uiseasonground", "/uiportraitseason", "/uitextureseason", "/uigolloescamp",
            "/uistrongcommander", "/uistrongkingdom", "/uipresent", "/uiweekendchallenge",
            "/uiportrait3v3", "/uiuiportraiit3v3", "/uitexture3v3arena", "/uiportraitleaguematch",
        ))
        or any(k in bn for k in (
            "activity", "christmas", "halloween", "oktober", "thanks", "foodfestival",
            "valentine", "easter", "roses", "carnival", "luckyroll", "redenvelope",
            "worldcup", "sevenday", "sevenlogin", "battlepass", "seasonpass",
            "season3", "season4", "season5", "newseason", "championbattle", "agechange",
            "radarcenter", "minecave", "strongcommander", "strongkingdom", "weekcard",
            "monthlycard", "monthcard", "firstpay", "giftpackage", "popuppackage",
            "scrollpack", "shop", "3v3", "leaguematch", "matchinggame", "castle",
            "dominate", "explore", "worldtrend", "goll", "personalarms",
        ))
        or xt.startswith(("activity_", "aps_season", "aps_dispatch"))
        or sn.startswith("activity_icon_")
    ):
        return "activities_and_events"

    # 20. Alliance & World
    if (
        "/sprites/slg/" in up
        or "/sprites/lodicon/" in up
        or "/sprites/lodatlas/" in up
        or "/uiworldpoint" in up
        or "/uialliance" in up
        or "/uiworldbattle/" in up
        or "/uithrone/" in up
        or "/uigovernment/" in up
        or "/uiportraitalliance/" in up
        or "/uiportraitglorydeclare/" in up
        or "/uiportraitimmigration/" in up
        or "/uitextureworldcitydeclare/" in up
        or "/uitextureimmigration/" in up
        or "/uisearch/" in up
        or "/uilandingoperations/" in up
        or "/sceneobjectui/" in up
        or "/usedlandscape/" in up
        or "/seasondesert/" in up
        or any(k in bn for k in (
            "uislg", "_slg_", "lodicon", "lodatlas", "uiworldpoint", "uialliance",
            "uiworldbattle", "throne", "government", "worldcitydeclare", "immigration",
            "glorydeclare", "uisearch", "landingoperations", "sceneobjectui",
            "usedlandscape", "seasondesert", "capitalwar",
        ))
        or xt.startswith(("alliance_", "aps_landlock"))
    ):
        return "alliance_and_world"

    # 21. UI HUD
    if (
        "/sprites/ui/" in up
        or "/loading/" in up
        or "/joystick/" in up
        or "/guide/" in up
        or "/uieffectres/" in up
        or bn.startswith((
            "main_atlas_ui_", "main_sprites_ui_", "main_atlas_uiportrait",
            "main_uitexture_ui", "main_uitexture_commonbg", "main_loading_all_",
        ))
        or bn == "resources.assets"
    ):
        return "ui_hud"

    # 22. Misc
    return "misc"


# ---------------------------------------------------------------------------
# Image filtering & edge-to-edge tight cropping
# ---------------------------------------------------------------------------

def is_excluded_asset_name(name: str, is_raw_tex: bool) -> bool:
    """Exclude atlas pages, font/number sheets, VFX masks, and solid white/blank blocks."""
    nl = name.strip().lower()
    if not nl:
        return True
    if nl.startswith("sactx-"):
        return True
    exact_bad = {
        "bgwhite", "ui_white_block", "white1px", "uimask", "font texture",
        "trialexpiredtexture", "ds_emoji", "emojidata_google_32",
        "playersupportemoji_atlas", "alliancejoin", "build_level_numbers",
        "high_lod_level_numbers", "world_lod_icon_atlas", "troop_head_icon_atlas",
        "glyph_atlas", "glyph_atlas_parkour",
    }
    if nl in exact_bad:
        return True
    if is_raw_tex:
        if any(k in nl for k in (
            "atlas", "spritesheet", "emojidata", "glyph", "font", "_sdf",
            "numbers", "_mask", "mask_", "vx_mask", "unlit_shadow", "unlit_daynight",
            "particle_", "eff_tex_", "noise_",
        )):
            return True
    else:
        # Even for Sprite objects, skip obvious number sheets / font atlases / solid blocks
        if any(k in nl for k in ("_numbers", "glyph_atlas", "font_atlas", "sactx-")):
            return True
    return False


def is_opaque_wallpaper(
    img_rgba: Image.Image,
    sprite_name: str,
    bundle_name: str,
    matched_in_xml: bool,
) -> bool:
    """
    Only used for generic/background main_uitexture_* and main_uilovemessage_* bundles.
    Skip huge opaque full-screen UI wallpapers/panel backgrounds while preserving all icons,
    portraits, transparent overlays, and XML-referenced graphics.
    """
    if matched_in_xml:
        return False
    w, h = img_rgba.size
    if max(w, h) < 400:
        return False

    # Sample alpha quickly via downscaled thumbnail (fast & accurate)
    thumb = img_rgba.getchannel("A").resize((64, 64), Image.Resampling.NEAREST)
    hist = thumb.histogram()
    total = 64 * 64
    opaque = sum(hist[245:])
    opaque_ratio = opaque / total

    nl = sprite_name.lower()
    bn = bundle_name.lower()

    # Large nearly-100%-opaque rectangles (>= 480x480 or area >= 300k px) are UI wallpapers/panels
    if ((w >= 480 and h >= 480) or (w * h >= 300_000)) and opaque_ratio >= 0.94:
        return True

    # Background/panel named textures in uitexture bundles with high opacity
    bg_hints = (
        "_bg", "bg_", "beijing", "diban", "commonbg", "wallpaper", "hengtiao",
        "titlebg", "folderbg", "mask", "shadow", "zhezhao", "ditiao", "tanchuang",
        "bg0", "bg1", "bg2", "bg3", "banner", "di_0", "di_1", "di_2", "_di1", "_di2",
        "paper", "panel", "scrollpack", "loading_buttom",
    )
    if any(k in nl for k in bg_hints) and opaque_ratio >= 0.80:
        return True
    if "commonbg" in bn and opaque_ratio >= 0.75:
        return True

    return False


def crop_edge_to_edge(img: Image.Image, reject_solid: bool = False) -> tuple[Image.Image | None, tuple[int, int], tuple[int, int]]:
    """
    Convert to RGBA, compute tight bounding box (alpha > 4, fallback getbbox()),
    reject < 4x4 or empty (and optionally solid flat-color blocks), and return cropped image.
    """
    rgba = img.convert("RGBA")
    orig_w, orig_h = rgba.size
    if orig_w < 4 or orig_h < 4:
        return None, (orig_w, orig_h), (0, 0)

    alpha = rgba.getchannel("A")
    mask = alpha.point(lambda p: 255 if p > 4 else 0)
    bbox = mask.getbbox()
    if bbox is None:
        bbox = rgba.getbbox()
    if bbox is None:
        return None, (orig_w, orig_h), (0, 0)

    cw = bbox[2] - bbox[0]
    ch = bbox[3] - bbox[1]
    if cw < 4 or ch < 4:
        return None, (orig_w, orig_h), (cw, ch)

    cropped = rgba.crop(bbox)
    if reject_solid:
        ext = cropped.getextrema()
        if all(lo == hi for lo, hi in ext):
            return None, (orig_w, orig_h), (cw, ch)

    return cropped, (orig_w, orig_h), (cw, ch)


# ---------------------------------------------------------------------------
# Parallel worker: process one bundle and write cropped PNGs to staging
# ---------------------------------------------------------------------------

# Global worker context populated via initializer to avoid re-pickling big dicts per task
_W_SPRITE_PATHS: dict[str, str] = {}
_W_NAME_MAP: dict[str, dict[str, Any]] = {}
_W_STAGING_DIR: str = ""


def _init_worker(sprite_paths: dict[str, str], name_map: dict[str, dict[str, Any]], staging_dir: str) -> None:
    global _W_SPRITE_PATHS, _W_NAME_MAP, _W_STAGING_DIR
    _W_SPRITE_PATHS = sprite_paths
    _W_NAME_MAP = name_map
    _W_STAGING_DIR = staging_dir


def _extract_bundle_worker(task: tuple[int, str]) -> dict[str, Any]:
    """Process a single AssetBundle or resources.assets file."""
    bundle_idx, bundle_path_str = task
    bundle_path = Path(bundle_path_str)
    bundle_name = bundle_path.name
    bundle_lower = bundle_name.lower()

    is_uitex = bundle_lower.startswith("main_uitexture_")
    is_lovemsg = bundle_lower.startswith("main_uilovemessage_")
    is_loading = bundle_lower.startswith("main_loading_all_")
    uitex_short = ""
    if is_uitex:
        uitex_short = bundle_lower[len("main_uitexture_"):].rsplit("_", 1)[0]
    apply_wallpaper_filter = (is_uitex and uitex_short not in ALWAYS_INCLUDE_UITEX) or is_lovemsg or is_loading

    records: list[dict[str, Any]] = []
    stats = Counter()

    try:
        env = load_unity_env(bundle_path)
    except Exception as ex:
        return {"bundle": bundle_name, "records": [], "stats": {"bundle_error": 1}, "error": str(ex)}

    # Pass 1: Collect all Texture2D path_ids referenced by SpriteAtlas, Sprite, or TMP_SpriteAsset
    atlas_or_sprite_tex_ids: set[int] = set()
    sprite_objs = []
    tex_objs = []
    ds_emoji_mb = None

    for obj in env.objects:
        tname = obj.type.name
        if tname == "SpriteAtlas":
            try:
                sa = obj.read()
                for _, v in sa.m_RenderDataMap:
                    if v.texture and v.texture.path_id:
                        atlas_or_sprite_tex_ids.add(v.texture.path_id)
                    if v.alphaTexture and v.alphaTexture.path_id:
                        atlas_or_sprite_tex_ids.add(v.alphaTexture.path_id)
            except Exception:
                pass
        elif tname == "Sprite":
            sprite_objs.append(obj)
        elif tname == "Texture2D":
            tex_objs.append(obj)
        elif tname == "MonoBehaviour":
            # Only inspect MonoBehaviours in emoji/resources bundles for TMP_SpriteAsset spriteSheet
            if "emoji" in bundle_lower or bundle_lower == "resources.assets":
                try:
                    tree = obj.read_typetree()
                    ss = tree.get("spriteSheet")
                    if isinstance(ss, dict) and ss.get("m_PathID"):
                        atlas_or_sprite_tex_ids.add(int(ss["m_PathID"]))
                        if str(tree.get("m_Name", "")).lower() == "ds_emoji" and ds_emoji_mb is None:
                            ds_emoji_mb = tree
                except Exception:
                    pass

    # Pre-scan Sprite texture references
    parsed_sprites = []
    for obj in sprite_objs:
        try:
            spr = obj.read()
            if spr.m_RD.texture and spr.m_RD.texture.path_id:
                atlas_or_sprite_tex_ids.add(spr.m_RD.texture.path_id)
            if spr.m_RD.alphaTexture and spr.m_RD.alphaTexture.path_id:
                atlas_or_sprite_tex_ids.add(spr.m_RD.alphaTexture.path_id)
            parsed_sprites.append((obj.path_id, spr))
        except Exception:
            stats["sprite_read_error"] += 1

    local_counter = 0

    def emit_candidate(
        img: Image.Image,
        sprite_name: str,
        asset_type: str,
        reject_solid: bool,
    ) -> None:
        nonlocal local_counter
        sn_clean = sprite_name.strip()
        if not sn_clean:
            stats["skip_empty_name"] += 1
            return
        sn_lower = sn_clean.lower()
        unity_path = _W_SPRITE_PATHS.get(sn_lower, "")

        # Skip loading Effect/Particle textures
        if is_loading and ("/loading/effect/" in unity_path.lower() or "/loading/bg/" in unity_path.lower()):
            stats["skip_loading_fx"] += 1
            return

        name_info = _W_NAME_MAP.get(sn_lower)
        eng_name = name_info["english_name"] if name_info else ""
        xml_table = name_info["xml_table"] if name_info else ""
        xml_id = name_info["xml_id"] if name_info else ""

        if not eng_name and EMOJI_HEX_RE.match(sn_lower):
            eng_name = lookup_emoji_english_name(sn_lower)
            if eng_name:
                xml_table = "unicode_emoji"
                xml_id = sn_lower.upper()

        rgba = img.convert("RGBA")
        if apply_wallpaper_filter and is_opaque_wallpaper(rgba, sn_clean, bundle_name, bool(name_info)):
            stats["skip_wallpaper"] += 1
            return

        cropped, (ow, oh), (cw, ch) = crop_edge_to_edge(rgba, reject_solid=reject_solid)
        if cropped is None:
            stats["skip_blank_or_tiny"] += 1
            return

        category = classify_icon(sn_clean, unity_path, bundle_name, xml_table)
        local_counter += 1
        staging_name = f"b{bundle_idx:04d}_{local_counter:05d}.png"
        staging_path = os.path.join(_W_STAGING_DIR, staging_name)
        cropped.save(staging_path, format="PNG", compress_level=1)

        records.append({
            "staging_path": staging_path,
            "sprite_name": sn_clean,
            "sprite_name_lower": sn_lower,
            "category": category,
            "english_name": eng_name,
            "xml_table": xml_table,
            "xml_id": xml_id,
            "source_bundle": bundle_name,
            "unity_path": unity_path,
            "asset_type": asset_type,
            "orig_width": ow,
            "orig_height": oh,
            "crop_width": cw,
            "crop_height": ch,
        })
        stats["extracted"] += 1

    # Pass 2: Extract every Sprite via spr.image (individual sliced sprites!)
    failed_cabs: list[tuple[str, str]] = []  # (sprite_name, missing_cab_name)
    cab_err_re = re.compile(r"File\s+(cab-[0-9a-f]+)\s+not found", re.IGNORECASE)

    for pid, spr in parsed_sprites:
        sname = getattr(spr, "m_Name", "") or f"sprite_{pid}"
        if is_excluded_asset_name(sname, is_raw_tex=False):
            stats["skip_excluded_name"] += 1
            continue
        try:
            im = spr.image
            if im is None:
                stats["skip_no_image"] += 1
                continue
            emit_candidate(im, sname, "Sprite", reject_solid=False)
        except Exception as ex:
            m_cab = cab_err_re.search(str(ex))
            if m_cab:
                failed_cabs.append((sname, m_cab.group(1).lower()))
            stats["sprite_image_error"] += 1

    # Pass 3: Slice crisp 128x128 ds_emoji icons cleanly from TMP_SpriteAsset (never uncut!)
    if ds_emoji_mb is not None and "main_emoji_all_" in bundle_lower:
        ss_pid = int(ds_emoji_mb["spriteSheet"]["m_PathID"])
        sheet_tex = None
        for tobj in tex_objs:
            if tobj.path_id == ss_pid:
                try:
                    sheet_tex = tobj.read().image.convert("RGBA")
                except Exception:
                    sheet_tex = None
                break
        if sheet_tex is not None:
            sw, sh = sheet_tex.size
            glyphs = {g["m_Index"]: g["m_GlyphRect"] for g in ds_emoji_mb.get("m_SpriteGlyphTable", [])}
            for ch_entry in ds_emoji_mb.get("m_SpriteCharacterTable", []):
                gidx = ch_entry.get("m_GlyphIndex")
                cname = str(ch_entry.get("m_Name", "")).strip()
                rect = glyphs.get(gidx)
                if not cname or not rect:
                    continue
                gx, gy, gw, gh = int(rect["m_X"]), int(rect["m_Y"]), int(rect["m_Width"]), int(rect["m_Height"])
                # Unity textures are bottom-up, PIL is top-down
                top = sh - (gy + gh)
                bottom = sh - gy
                if gx < 0 or top < 0 or gx + gw > sw or bottom > sh or gw < 4 or gh < 4:
                    continue
                tile = sheet_tex.crop((gx, top, gx + gw, bottom))
                emit_candidate(tile, cname, "TMP_SpriteGlyph", reject_solid=True)

    # Pass 4: Standalone unreferenced Texture2D assets (strictly excluding atlas pages)
    for tobj in tex_objs:
        if tobj.path_id in atlas_or_sprite_tex_ids:
            stats["skip_atlas_or_sprite_tex"] += 1
            continue
        try:
            tex = tobj.read()
        except Exception:
            stats["tex_read_error"] += 1
            continue
        tname = getattr(tex, "m_Name", "") or ""
        if is_excluded_asset_name(tname, is_raw_tex=True):
            stats["skip_excluded_tex"] += 1
            continue
        if tex.m_Width < 4 or tex.m_Height < 4:
            stats["skip_tiny_tex"] += 1
            continue
        # Guardrail: never export unreferenced giant >= 1024x1024 textures outside herobody
        if (tex.m_Width >= 1024 and tex.m_Height >= 1024) and uitex_short not in ("herobody", "herobody2"):
            stats["skip_giant_unref_tex"] += 1
            continue
        try:
            im = tex.image
            if im is None:
                stats["skip_no_image"] += 1
                continue
            emit_candidate(im, tname, "Texture2D", reject_solid=True)
        except Exception:
            stats["tex_image_error"] += 1

    return {
        "bundle": bundle_name,
        "bundle_path": bundle_path_str,
        "records": records,
        "stats": dict(stats),
        "failed_cabs": failed_cabs,
        "error": None,
    }


def rescue_cross_bundle_sprites(
    failed_by_bundle: dict[str, tuple[set[str], set[str]]],
    all_targets: list[Path],
    sprite_paths: dict[str, str],
    name_map: dict[str, dict[str, Any]],
    staging_dir: Path,
) -> tuple[list[dict[str, Any]], int]:
    """
    Rescue Sprite objects whose SpriteAtlas lives in another bundle (missing cab-*).
    Indexes cab-* names across target bundles, loads each failing bundle together with
    its companion cab-* bundle(s) into one UnityPy.Environment, and extracts the failed sprites.
    """
    needed_cabs: set[str] = set()
    for _snames, cabs in failed_by_bundle.values():
        needed_cabs.update(cabs)
    if not needed_cabs:
        return [], 0

    print(f"[INFO] Rescuing cross-bundle sprites across {len(failed_by_bundle)} bundles ({len(needed_cabs)} unique CABs)...")
    cab_to_bundle: dict[str, Path] = {}
    for bp in all_targets:
        if bp.suffix.lower() != ".bundle":
            continue
        try:
            env = load_unity_env(bp)
            for fname in env.file.files.keys():
                fl = str(fname).lower()
                if fl in needed_cabs:
                    cab_to_bundle[fl] = bp
            if len(cab_to_bundle) == len(needed_cabs):
                break
        except Exception:
            continue

    rescued_records: list[dict[str, Any]] = []
    still_failed = 0
    counter = 0

    for bundle_path_str, (target_snames, cabs) in failed_by_bundle.items():
        bp = Path(bundle_path_str)
        bundle_name = bp.name
        env = UnityPy.Environment()
        try:
            raw = bp.read_bytes()
            if raw.startswith(b"UnityRawUnityFS"):
                raw = raw[8:]
            env.load_file(raw, name=bundle_name)
        except Exception:
            still_failed += len(target_snames)
            continue

        loaded_companions = {bp}
        for c in cabs:
            comp = cab_to_bundle.get(c)
            if comp and comp not in loaded_companions:
                try:
                    craw = comp.read_bytes()
                    if craw.startswith(b"UnityRawUnityFS"):
                        craw = craw[8:]
                    env.load_file(craw, name=comp.name)
                    loaded_companions.add(comp)
                except Exception:
                    pass

        # Extract failed sprites belonging to the primary failing bundle
        primary_bf = env.files.get(bundle_name)
        if primary_bf is None:
            continue
        sub_files = list(primary_bf.files.values()) if hasattr(primary_bf, "files") else [primary_bf]
        for sf in sub_files:
            objs = sf.objects.values() if hasattr(sf, "objects") and isinstance(sf.objects, dict) else getattr(sf, "objects", [])
            for obj in objs:
                if obj.type.name != "Sprite":
                    continue
                try:
                    spr = obj.read()
                    sname = getattr(spr, "m_Name", "") or f"sprite_{obj.path_id}"
                    if sname.lower() not in target_snames:
                        continue
                    if is_excluded_asset_name(sname, is_raw_tex=False):
                        continue
                    im = spr.image
                    if im is None:
                        continue
                except Exception:
                    still_failed += 1
                    continue

                sn_clean = sname.strip()
                sn_lower = sn_clean.lower()
                unity_path = sprite_paths.get(sn_lower, "")
                name_info = name_map.get(sn_lower)
                eng_name = name_info["english_name"] if name_info else ""
                xml_table = name_info["xml_table"] if name_info else ""
                xml_id = name_info["xml_id"] if name_info else ""
                if not eng_name and EMOJI_HEX_RE.match(sn_lower):
                    eng_name = lookup_emoji_english_name(sn_lower)
                    if eng_name:
                        xml_table = "unicode_emoji"
                        xml_id = sn_lower.upper()

                cropped, (ow, oh), (cw, ch) = crop_edge_to_edge(im, reject_solid=False)
                if cropped is None:
                    continue

                category = classify_icon(sn_clean, unity_path, bundle_name, xml_table)
                counter += 1
                staging_path = str(staging_dir / f"rescue_{counter:05d}.png")
                cropped.save(staging_path, format="PNG", compress_level=1)
                rescued_records.append({
                    "staging_path": staging_path,
                    "sprite_name": sn_clean,
                    "sprite_name_lower": sn_lower,
                    "category": category,
                    "english_name": eng_name,
                    "xml_table": xml_table,
                    "xml_id": xml_id,
                    "source_bundle": bundle_name,
                    "unity_path": unity_path,
                    "asset_type": "Sprite_CrossBundle",
                    "orig_width": ow,
                    "orig_height": oh,
                    "crop_width": cw,
                    "crop_height": ch,
                })

    print(f"[INFO] Cross-bundle rescue recovered {len(rescued_records)} sprites (remaining errors: {still_failed}).")
    return rescued_records, still_failed


# ---------------------------------------------------------------------------
# Verification contact sheet generator (48 diverse icons)
# ---------------------------------------------------------------------------

def build_contact_sheet(winners: list[dict[str, Any]], out_path: Path) -> None:
    """Build a 48-icon (8x6) diverse verification contact sheet across categories."""
    by_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in winners:
        by_cat[rec["category"]].append(rec)

    # Target representation across key categories (sum = 48)
    quotas = [
        ("resources", 4),
        ("items", 4),
        ("hero_portraits_round", 3),
        ("hero_portraits_small", 3),
        ("hero_portraits_large", 2),
        ("hero_fullbody", 3),
        ("hero_fragments", 2),
        ("hero_medals", 2),
        ("hero_equipment", 3),
        ("skills", 3),
        ("science_and_tech", 3),
        ("buildings", 3),
        ("troops_and_soldiers", 2),
        ("vehicles_and_aircraft", 2),
        ("monsters_and_bosses", 3),
        ("activities_and_events", 1),
        ("alliance_and_world", 1),
        ("flags", 1),
        ("emojis", 1),
        ("collectibles_and_fishing", 1),
        ("ui_hud", 1),
    ]

    picks: list[dict[str, Any]] = []
    used_paths: set[str] = set()

    for cat, count in quotas:
        pool = by_cat.get(cat, [])
        if not pool:
            continue
        # Prefer English-named, visually crisp >= 24px icons for clear inspection
        crisp = [r for r in pool if min(r["crop_width"], r["crop_height"]) >= 24]
        if not crisp:
            crisp = pool
        named = [r for r in crisp if r["english_name"]]
        ordered = named + [r for r in crisp if not r["english_name"]]
        # Spread across pool for visual variety
        step = max(1, len(ordered) // max(1, count))
        chosen = 0
        for idx in range(0, len(ordered), step):
            r = ordered[idx]
            if r["abs_path"] not in used_paths:
                picks.append(r)
                used_paths.add(r["abs_path"])
                chosen += 1
                if chosen >= count:
                    break
        if chosen < count:
            for r in ordered:
                if r["abs_path"] not in used_paths:
                    picks.append(r)
                    used_paths.add(r["abs_path"])
                    chosen += 1
                    if chosen >= count:
                        break

    # Fill up to 48 if any category had fewer than quota
    if len(picks) < 48:
        for rec in winners:
            if rec["abs_path"] not in used_paths:
                picks.append(rec)
                used_paths.add(rec["abs_path"])
                if len(picks) >= 48:
                    break
    picks = picks[:48]

    cols, rows = 8, 6
    cell_w, cell_h = 210, 210
    pad = 12
    header_h = 56
    sheet_w = cols * cell_w + (cols + 1) * pad
    sheet_h = header_h + rows * cell_h + (rows + 1) * pad

    sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 27, 34))
    draw = ImageDraw.Draw(sheet)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_cat = ImageFont.truetype("arial.ttf", 12)
        font_lbl = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font_title = ImageFont.load_default()
        font_cat = font_title
        font_lbl = font_title

    draw.text(
        (pad, 16),
        f"Last Z Extracted Icons Verification Sheet (48 diverse edge-to-edge cropped samples across {len(by_cat)} categories)",
        fill=(240, 244, 250),
        font=font_title,
    )

    for idx, rec in enumerate(picks):
        r_idx = idx // cols
        c_idx = idx % cols
        x0 = pad + c_idx * (cell_w + pad)
        y0 = header_h + pad + r_idx * (cell_h + pad)

        # Card background + subtle checkerboard box for icon transparency visibility
        draw.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=(38, 42, 52), outline=(72, 80, 96), width=1)

        box_x0, box_y0 = x0 + 14, y0 + 22
        box_w, box_h = cell_w - 28, 134
        # Draw checkerboard behind icon so tight edge-to-edge crop is unmistakable
        sq = 10
        for cy in range(box_y0, box_y0 + box_h, sq):
            for cx in range(box_x0, box_x0 + box_w, sq):
                is_dark = ((cx - box_x0) // sq + (cy - box_y0) // sq) % 2 == 0
                c = (56, 61, 74) if is_dark else (70, 76, 92)
                draw.rectangle([cx, cy, min(cx + sq, box_x0 + box_w), min(cy + sq, box_y0 + box_h)], fill=c)

        try:
            with Image.open(rec["abs_path"]) as im:
                im_rgba = im.convert("RGBA")
                iw, ih = im_rgba.size
                scale = min(box_w / iw, box_h / ih)
                nw = max(1, int(round(iw * scale)))
                nh = max(1, int(round(ih * scale)))
                resized = im_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
                px = box_x0 + (box_w - nw) // 2
                py = box_y0 + (box_h - nh) // 2
                sheet.paste(resized, (px, py), resized)
                # Thin cyan border around exact pasted cropped icon edge to verify tight crop!
                draw.rectangle([px - 1, py - 1, px + nw, py + nh], outline=(0, 210, 255), width=1)
        except Exception:
            pass

        # Category label top
        draw.text((x0 + 6, y0 + 4), rec["category"][:26], fill=(130, 200, 255), font=font_cat)
        # Name & dims bottom
        label = rec["english_name"] if rec["english_name"] else rec["sprite_name"]
        label = strip_em_dash(label)
        if len(label) > 27:
            label = label[:26] + "."
        dims = f"{rec['crop_width']}x{rec['crop_height']} (src {rec['orig_width']}x{rec['orig_height']})"
        draw.text((x0 + 6, y0 + 162), label, fill=(245, 245, 245), font=font_lbl)
        draw.text((x0 + 6, y0 + 179), rec["sprite_name"][:27], fill=(170, 180, 195), font=font_lbl)
        draw.text((x0 + 6, y0 + 194), dims, fill=(140, 225, 165), font=font_lbl)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, format="PNG")
    print(f"[INFO] Wrote verification contact sheet: {out_path}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def discover_target_bundles() -> list[Path]:
    """Collect all icon/sprite/atlas/emoji/uitexture/loading/lovemessage bundles + resources.assets."""
    targets: list[Path] = []
    if ASSETBUNDLES_DIR.exists():
        for p in sorted(ASSETBUNDLES_DIR.iterdir()):
            if not p.is_file() or p.suffix.lower() != ".bundle":
                continue
            nl = p.name.lower()
            if any(s in nl for s in SKIP_BUNDLE_SUBSTRINGS):
                continue
            if nl.startswith((
                "main_atlas_",
                "main_sprites_",
                "main_emoji_all_",
                "main_uitexture_",
                "main_loading_all_",
                "main_uilovemessage_",
            )):
                targets.append(p)
    if RESOURCES_ASSETS.exists():
        targets.append(RESOURCES_ASSETS)
    return targets


def main() -> None:
    t0 = time.time()
    print("=== Last Z Full Game Icon Extractor ===")

    # 1. Read SpritePathCache
    sprite_paths = load_sprite_path_cache()
    print(f"[INFO] Loaded SpritePathCache entries: {len(sprite_paths)}")

    # 2. Load English localization + XML table mappings
    loc_strings = load_english_strings()
    print(f"[INFO] Loaded merged English localization strings: {len(loc_strings)}")
    name_map = build_english_name_map(loc_strings)

    # 3. Discover bundles
    targets = discover_target_bundles()
    print(f"[INFO] Discovered target asset sources: {len(targets)}")

    # 4. Prepare clean output directories & staging folder
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    staging_dir = OUTPUT_ROOT / "_staging_extract"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Clean existing category directories for a fresh deterministic export
    for cat in CATEGORIES:
        cat_dir = OUTPUT_ROOT / cat
        if cat_dir.exists():
            shutil.rmtree(cat_dir)
        cat_dir.mkdir(parents=True, exist_ok=True)

    # 5. Parallel extraction across CPU cores
    max_workers = min(8, max(2, (os.cpu_count() or 4)))
    print(f"[INFO] Extracting across {max_workers} worker processes...")

    all_candidates: list[dict[str, Any]] = []
    total_stats: Counter = Counter()
    bundle_errors: list[tuple[str, str]] = []
    failed_by_bundle: dict[str, tuple[set[str], set[str]]] = {}

    tasks = [(idx, str(p)) for idx, p in enumerate(targets)]
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_init_worker,
        initargs=(sprite_paths, name_map, str(staging_dir)),
    ) as pool:
        for done_i, res in enumerate(pool.map(_extract_bundle_worker, tasks, chunksize=4), start=1):
            all_candidates.extend(res["records"])
            for k, v in res["stats"].items():
                total_stats[k] += v
            for sname, cab_id in res.get("failed_cabs", []):
                bpath = res["bundle_path"]
                if bpath not in failed_by_bundle:
                    failed_by_bundle[bpath] = (set(), set())
                failed_by_bundle[bpath][0].add(sname.lower())
                failed_by_bundle[bpath][1].add(cab_id)
            if res["error"]:
                bundle_errors.append((res["bundle"], res["error"]))
            if done_i % 100 == 0 or done_i == len(tasks):
                elapsed = time.time() - t0
                print(f"  Progress: {done_i}/{len(tasks)} bundles ({len(all_candidates)} raw icons) [{elapsed:.1f}s]")

    # 5b. Rescue cross-bundle sprites whose SpriteAtlas resides in a companion bundle
    if failed_by_bundle:
        rescued_records, still_failed = rescue_cross_bundle_sprites(
            failed_by_bundle, targets, sprite_paths, name_map, staging_dir
        )
        all_candidates.extend(rescued_records)
        total_stats["rescued_cross_bundle"] = len(rescued_records)
        total_stats["unresolved_sprite_errors"] = still_failed

    print(f"[INFO] Raw extracted candidates: {len(all_candidates)}, stats: {dict(total_stats)}")

    # 6. Deduplicate by (category, sprite_name_lower) keeping highest pixel-area version
    best_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    losers: list[str] = []

    def rank_key(r: dict[str, Any]) -> tuple[int, int, int]:
        crop_area = r["crop_width"] * r["crop_height"]
        orig_area = r["orig_width"] * r["orig_height"]
        type_pref = 2 if r["asset_type"] == "Sprite" else (1 if r["asset_type"] == "TMP_SpriteGlyph" else 0)
        return (crop_area, orig_area, type_pref)

    for rec in all_candidates:
        dkey = (rec["category"], rec["sprite_name_lower"])
        prev = best_by_key.get(dkey)
        if prev is None:
            best_by_key[dkey] = rec
        elif rank_key(rec) > rank_key(prev):
            losers.append(prev["staging_path"])
            best_by_key[dkey] = rec
        else:
            losers.append(rec["staging_path"])

    # Remove duplicate staging files
    for lp in losers:
        try:
            os.remove(lp)
        except OSError:
            pass

    print(f"[INFO] Deduplicated: kept {len(best_by_key)} unique icons (dropped {len(losers)} duplicates).")

    # 7. Deterministic filename assignment + collision avoidance + atomic move
    winners = sorted(best_by_key.values(), key=lambda r: (r["category"], r["sprite_name_lower"]))
    used_names_per_cat: dict[str, set[str]] = defaultdict(set)

    catalog_rows: list[dict[str, Any]] = []
    cat_counts: Counter = Counter()
    cat_named_counts: Counter = Counter()

    for rec in winners:
        cat = rec["category"]
        base_fname = build_safe_filename(rec["english_name"], rec["sprite_name"], max_total_len=110)
        fname = base_fname
        stem, ext = os.path.splitext(base_fname)
        suffix_num = 2
        while fname.lower() in used_names_per_cat[cat]:
            suf = f"_{suffix_num}"
            trimmed = stem[: 110 - len(ext) - len(suf)].rstrip("._ ")
            fname = trimmed + suf + ext
            suffix_num += 1
        used_names_per_cat[cat].add(fname.lower())

        dest_path = OUTPUT_ROOT / cat / fname
        os.replace(rec["staging_path"], dest_path)

        rel_path = f"{cat}/{fname}"
        rec["filename"] = fname
        rec["relative_path"] = rel_path
        rec["abs_path"] = str(dest_path)

        cat_counts[cat] += 1
        if rec["english_name"]:
            cat_named_counts[cat] += 1

        catalog_rows.append({
            "category": cat,
            "filename": fname,
            "relative_path": rel_path,
            "sprite_name": strip_em_dash(rec["sprite_name"]),
            "english_name": strip_em_dash(rec["english_name"]),
            "xml_table": rec["xml_table"],
            "xml_id": rec["xml_id"],
            "source_bundle": rec["source_bundle"],
            "unity_path": strip_em_dash(rec["unity_path"]),
            "asset_type": rec["asset_type"],
            "orig_width": rec["orig_width"],
            "orig_height": rec["orig_height"],
            "crop_width": rec["crop_width"],
            "crop_height": rec["crop_height"],
            "file_size_bytes": dest_path.stat().st_size,
        })

    # Clean up empty staging directory
    try:
        shutil.rmtree(staging_dir)
    except OSError:
        pass

    # 8. Write icons_catalog.json
    total_icons = len(catalog_rows)
    total_named = sum(cat_named_counts.values())
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    summary_by_cat = {
        cat: {
            "total": cat_counts.get(cat, 0),
            "english_named": cat_named_counts.get(cat, 0),
            "unnamed": cat_counts.get(cat, 0) - cat_named_counts.get(cat, 0),
        }
        for cat in CATEGORIES
    }

    catalog_json = {
        "generated_at_utc": now_iso,
        "source_assetbundles_dir": str(ASSETBUNDLES_DIR),
        "source_resources_assets": str(RESOURCES_ASSETS),
        "bundles_scanned": len(targets),
        "sprite_path_cache_entries": len(sprite_paths),
        "english_localization_strings": len(loc_strings),
        "xml_sprite_name_mappings": len(name_map),
        "total_icons": total_icons,
        "total_english_named": total_named,
        "total_unnamed": total_icons - total_named,
        "duplicates_removed": len(losers),
        "extraction_stats": dict(total_stats),
        "bundle_errors": bundle_errors,
        "categories": summary_by_cat,
        "icons": catalog_rows,
    }

    json_path = OUTPUT_ROOT / "icons_catalog.json"
    json_path.write_text(
        strip_em_dash(json.dumps(catalog_json, indent=2, ensure_ascii=False)),
        encoding="utf-8",
    )

    # 9. Write icons_catalog.csv
    csv_path = OUTPUT_ROOT / "icons_catalog.csv"
    fieldnames = [
        "category", "filename", "relative_path", "sprite_name", "english_name",
        "xml_table", "xml_id", "source_bundle", "unity_path", "asset_type",
        "orig_width", "orig_height", "crop_width", "crop_height", "file_size_bytes",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for row in catalog_rows:
            writer.writerow(row)

    # 10. Write README.md
    readme_lines = [
        "# Last Z Complete Extracted Game Icons",
        "",
        f"Generated UTC: `{now_iso}`",
        "",
        "## Summary",
        "",
        f"- **Total Unique Icons Extracted:** `{total_icons:,}`",
        f"- **Official English Name Matched:** `{total_named:,}` ({(100.0 * total_named / max(1, total_icons)):.1f}%)",
        f"- **Original Sprite Name Only:** `{total_icons - total_named:,}`",
        f"- **Duplicate Entries Deduplicated:** `{len(losers):,}` (highest pixel-area version kept)",
        f"- **Asset Sources Scanned:** `{len(targets):,}` bundles + `resources.assets`",
        f"- **SpritePathCache Entries Loaded:** `{len(sprite_paths):,}`",
        f"- **Localization Strings Loaded:** `{len(loc_strings):,}`",
        f"- **XML Table Icon Mappings Built:** `{len(name_map):,}`",
        "- **Cropping:** Edge-to-edge RGBA crop (`alpha > 4` threshold, fallback `getbbox()`, minimum `4x4` px, lossless PNG)",
        "- **Atlas Protection:** Zero uncut SpriteAtlas pages, TMP_SpriteAsset sheets, font glyph sheets, or VFX masks exported",
        "",
        "## Per-Category Breakdown",
        "",
        "| Category | Total Icons | English Named | Sprite Name Only |",
        "|---|---:|---:|---:|",
    ]
    for cat in CATEGORIES:
        t = cat_counts.get(cat, 0)
        n = cat_named_counts.get(cat, 0)
        readme_lines.append(f"| `{cat}` | {t:,} | {n:,} | {t - n:,} |")
    readme_lines.extend([
        f"| **TOTAL** | **{total_icons:,}** | **{total_named:,}** | **{total_icons - total_named:,}** |",
        "",
        "## Filename Convention",
        "",
        "- Matched official English name: `<SafeEnglishName>__<SpriteName>.png`",
        "- Unmatched sprite name: `<SpriteName>.png`",
        "- Windows-safe characters only, maximum 110 characters, zero collisions per category.",
        "",
        "## Catalog Files",
        "",
        "- `icons_catalog.json` - Full structured metadata (dimensions before/after crop, source bundle, Unity path, XML table & ID)",
        "- `icons_catalog.csv` - Spreadsheet-ready tabular catalog",
        "",
        "## Extraction Script",
        "",
        "- `tools/extract all game icons.py`",
        "",
    ])
    readme_path = OUTPUT_ROOT / "README.md"
    readme_path.write_text(strip_em_dash("\n".join(readme_lines)), encoding="utf-8")

    # 11. Build 48-icon verification contact sheet
    build_contact_sheet(winners, CONTACT_SHEET_PATH)

    elapsed_total = time.time() - t0
    print(f"=== DONE in {elapsed_total:.1f}s: {total_icons:,} icons ({total_named:,} English-named) ===")


if __name__ == "__main__":
    main()
