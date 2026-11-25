"""Verification suite for Last Z 18-language UI locale assets.

Covers:
1. manifest.json has all 18 official Last Z languages with exact code, game_id,
   native_name, english_name, rtl (`ar` True, others False), and translate_code.
2. Cross-checks all 18 game_id values against megamind `SuportedLanguagesName`.
3. translations.json has 100+ keys with exact 100% key parity across all 18
   languages, zero missing keys, zero empty strings, and genuine localization.
4. Zero em dashes and zero forbidden terms across locale files and builder script.
5. Zero underscores in filenames/folder names under launcher/assets/locales/.
6. Deterministic rebuild parity via `tools/build ui locales.py`.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = PROJECT_ROOT / "launcher" / "assets" / "locales"
MANIFEST_PATH = LOCALES_DIR / "manifest.json"
TRANSLATIONS_PATH = LOCALES_DIR / "translations.json"
BUILDER_PATH = PROJECT_ROOT / "tools" / "build ui locales.py"
ENUMS_PATH = PROJECT_ROOT / "megamind" / "raw" / "enums complete.json"

EM_DASH = chr(0x2014)
HTML_EM_DASH = "&" + "mdash;"
FORBIDDEN_TERMS = (
    "command" + "er",
    "courage " + "badges",
)

EXPECTED_LANGUAGES = [
    ("en", 14, "English", "English", False),
    ("zh-CN", 8, "简体中文", "Chinese Simplified", False),
    ("zh-TW", 9, "繁體中文", "Chinese Traditional", False),
    ("fr", 18, "Français", "French", False),
    ("de", 20, "Deutsch", "German", False),
    ("es", 45, "Español", "Spanish", False),
    ("pt", 37, "Português", "Portuguese", False),
    ("it", 26, "Italiano", "Italian", False),
    ("ru", 39, "Русский", "Russian", False),
    ("ko", 28, "한국어", "Korean", False),
    ("ja", 27, "日本語", "Japanese", False),
    ("th", 47, "ไทย", "Thai", False),
    ("tr", 48, "Türkçe", "Turkish", False),
    ("id", 25, "Bahasa Indonesia", "Indonesian", False),
    ("vi", 50, "Tiếng Việt", "Vietnamese", False),
    ("ar", 3, "العربية", "Arabic", True),
    ("pl", 35, "Polski", "Polish", False),
    ("nl", 13, "Nederlands", "Dutch", False),
]

REQUIRED_KEYS = [
    "nav.overview",
    "nav.rss",
    "nav.kills",
    "nav.perf",
    "nav.alliances",
    "nav.map",
    "nav.inventory",
    "nav.heroes",
    "nav.calculators",
    "nav.functions",
    "hdr.title",
    "hdr.target",
    "hdr.auto",
    "hdr.language",
    "hdr.online",
    "hdr.offline",
    "hdr.checking",
    "hdr.engine_active",
    "hdr.engine_idle",
    "hdr.expand_console",
    "hdr.collapse_console",
    "overview.title",
    "overview.subtitle",
    "overview.run_bot_cycle",
    "overview.complete_daily",
    "overview.launch_farms",
    "overview.patch_game",
    "overview.always_on",
    "overview.sweep_now",
    "overview.auto_help",
    "overview.auto_heal",
    "overview.alliance_donate",
    "overview.core_safe",
    "overview.main_account",
    "overview.farm_accounts",
    "overview.launch",
    "overview.stop",
    "overview.run",
    "overview.stopped",
    "overview.running",
    "overview.ready",
    "tasks.radar_events",
    "tasks.daily_tasks",
    "tasks.troop_training",
    "tasks.bounty_missions",
    "tasks.alliance_duel",
    "tasks.hero_upgrades",
    "tasks.full_prep",
    "rss.title",
    "rss.subtitle",
    "rss.start",
    "rss.stop",
    "rss.stop_all",
    "rss.diamonds",
    "rss.electricity",
    "rss.zent",
    "rss.wood",
    "rss.food",
    "rss.min_level",
    "rss.max_level",
    "rss.reserve_squads",
    "rss.priority_queue",
    "kills.title",
    "kills.subtitle",
    "kills.boomers",
    "kills.npc",
    "kills.saga",
    "kills.tyrant",
    "kills.furylord",
    "kills.min_stamina",
    "kills.start_hunting",
    "kills.stop_hunting",
    "perf.title",
    "perf.subtitle",
    "perf.translator_title",
    "perf.translator_desc",
    "perf.translator_enable",
    "perf.translator_auto_chat",
    "perf.translator_target_lang",
    "perf.translator_auto_game_lang",
    "perf.translator_test_placeholder",
    "perf.translator_test_btn",
    "perf.translator_status",
    "perf.translator_cache_hits",
    "perf.translator_avg_ms",
    "perf.translator_provider",
    "perf.translator_api_keys",
    "perf.translator_save",
    "map.title",
    "map.subtitle",
    "map.find_placeholder",
    "map.snap",
    "map.zoom_in",
    "map.zoom_out",
    "map.reset_view",
    "map.terrain",
    "map.world_map_terrain",
    "map.province_borders",
    "map.coord_grid",
    "map.unshielded",
    "map.shielded",
    "map.rss",
    "map.hive",
    "map.origin",
    "map.all_states",
    "map.pin",
    "map.pinned",
    "map.unpin",
    "map.watchlist_title",
    "map.watchlist_empty",
    "map.watchlist_pin_alliance",
    "map.watchlist_verify",
    "map.watchlist_clear",
    "map.watchlist_pins_layer",
    "map.shield_dropped",
    "map.shield_expiring_soon",
    "map.set_origin",
    "map.snap_camera",
    "map.refresh",
    "inv.title",
    "inv.subtitle",
    "inv.sync_live",
    "inv.search_placeholder",
    "heroes.title",
    "heroes.subtitle",
    "heroes.sync_live",
    "heroes.run_now",
    "heroes.save_rules",
    "calc.title",
    "calc.subtitle",
    "calc.sync_live",
    "calc.expand_all",
    "calc.collapse_all",
    "calc.badges_held",
    "calc.badges_invested",
    "calc.badges_remaining",
    "calc.badges_needed",
    "fn.title",
    "fn.subtitle",
    "fn.save",
    "fn.apply",
    "fn.reset",
]


def _load_builder_module():
    spec = importlib.util.spec_from_file_location("build_ui_locales_mod", str(BUILDER_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {BUILDER_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestUiLocales(unittest.TestCase):
    """Verify UI locale manifest, 18-language translations, and hygiene rules."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_raw = MANIFEST_PATH.read_text(encoding="utf-8")
        cls.translations_raw = TRANSLATIONS_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(cls.manifest_raw)
        cls.translations = json.loads(cls.translations_raw)

    def test_manifest_has_exact_18_official_languages(self) -> None:
        self.assertEqual(self.manifest.get("version"), 1)
        self.assertEqual(self.manifest.get("default"), "en")

        langs = self.manifest.get("languages", [])
        self.assertEqual(len(langs), 18)

        actual = [
            (
                entry["code"],
                entry["game_id"],
                entry["native_name"],
                entry["english_name"],
                entry["rtl"],
            )
            for entry in langs
        ]
        self.assertEqual(actual, EXPECTED_LANGUAGES)

        for entry in langs:
            self.assertIsInstance(entry["game_id"], int)
            self.assertIsInstance(entry["translate_code"], str)
            self.assertTrue(entry["translate_code"].strip())
            self.assertEqual(entry["rtl"], entry["code"] == "ar")

    def test_manifest_game_ids_match_megamind_enum(self) -> None:
        if not ENUMS_PATH.is_file():
            self.skipTest("megamind enums complete.json not present")
        enums_data = json.loads(ENUMS_PATH.read_text(encoding="utf-8"))
        supported = enums_data.get("enums", enums_data).get("SuportedLanguagesName", {})
        if not supported and "SuportedLanguagesName" in enums_data:
            supported = enums_data["SuportedLanguagesName"]
        if not supported:
            for val in enums_data.values():
                if isinstance(val, dict) and "SuportedLanguagesName" in val:
                    supported = val["SuportedLanguagesName"]
                    break
        self.assertTrue(supported, "SuportedLanguagesName not found in enums complete.json")

        megamind_ids = {int(k) for k in supported.keys()}
        manifest_ids = {int(entry["game_id"]) for entry in self.manifest["languages"]}
        self.assertEqual(manifest_ids, megamind_ids)

    def test_translations_100_percent_key_parity_and_non_empty(self) -> None:
        expected_codes = [item[0] for item in EXPECTED_LANGUAGES]
        self.assertEqual(list(self.translations.keys()), expected_codes)

        en_table = self.translations["en"]
        en_keys = set(en_table.keys())
        self.assertGreaterEqual(len(en_keys), 100)

        missing_required = [k for k in REQUIRED_KEYS if k not in en_keys]
        self.assertEqual(missing_required, [], f"Missing required keys: {missing_required}")

        for code in expected_codes:
            table = self.translations[code]
            self.assertEqual(
                set(table.keys()),
                en_keys,
                f"Key parity mismatch for language {code}",
            )
            for key, value in table.items():
                self.assertIsInstance(value, str, f"Non-string value at {code}.{key}")
                self.assertTrue(value.strip(), f"Empty translation at {code}.{key}")
                self.assertEqual(
                    value,
                    value.strip(),
                    f"Leading/trailing whitespace at {code}.{key}",
                )

    def test_non_english_locales_are_genuinely_localized(self) -> None:
        en_table = self.translations["en"]
        total_keys = len(en_table)
        for code in self.translations:
            if code == "en":
                continue
            table = self.translations[code]
            differing = sum(1 for k, v in table.items() if v != en_table[k])
            ratio = differing / total_keys
            self.assertGreaterEqual(
                ratio,
                0.85,
                f"Locale {code} appears under-translated ({differing}/{total_keys} differ from en)",
            )

    def test_zero_em_dashes_and_zero_forbidden_terms(self) -> None:
        builder_raw = BUILDER_PATH.read_text(encoding="utf-8")
        files_to_check = [
            ("manifest.json", self.manifest_raw),
            ("translations.json", self.translations_raw),
            ("build ui locales.py", builder_raw),
        ]
        for label, content in files_to_check:
            self.assertNotIn(EM_DASH, content, f"Em dash found in {label}")
            self.assertNotIn(HTML_EM_DASH, content.lower(), f"HTML em dash found in {label}")
            lower_content = content.lower()
            for term in FORBIDDEN_TERMS:
                self.assertNotIn(term, lower_content, f"Forbidden term {term!r} found in {label}")

    def test_zero_underscores_in_locale_filenames_and_folders(self) -> None:
        self.assertNotIn("_", LOCALES_DIR.name)
        self.assertNotIn("_", BUILDER_PATH.name)
        self.assertNotIn("_", Path(__file__).name)
        all_paths = list(LOCALES_DIR.rglob("*"))
        self.assertTrue(all_paths, "No files found under launcher/assets/locales/")
        for path in all_paths:
            rel = path.relative_to(LOCALES_DIR)
            for part in rel.parts:
                self.assertNotIn("_", part, f"Underscore found in locale path: {rel}")

    def test_builder_reproduces_identical_output(self) -> None:
        mod = _load_builder_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "locales"
            m_path, t_path = mod.write_locales(out_dir)
            self.assertEqual(m_path.read_text(encoding="utf-8"), self.manifest_raw)
            self.assertEqual(t_path.read_text(encoding="utf-8"), self.translations_raw)


if __name__ == "__main__":
    unittest.main()
