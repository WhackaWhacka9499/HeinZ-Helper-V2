"""Unit and integration tests for the Last Z always-on Live Translator bridge.

All unit & localhost HTTP server tests run 100% offline using mocked HTTP
providers and isolated temporary SQLite caches on ephemeral ports (port=0).
"""

from __future__ import annotations

import contextlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import threading
import unittest
from unittest import mock
import urllib.parse
import urllib.request

from lupa import LuaRuntime

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_mod(mod_name: str, rel_path: str):
    full_path = PROJECT_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(mod_name, str(full_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module at {full_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TR_MOD = _load_mod("test_live_translator_server", "tools/live translator server.py")
DAEMON_MOD = _load_mod("test_live_translator_daemon", "daemon/lastz auto engine daemon.py")


class TestGameTokenProtector(unittest.TestCase):
    """Verify Last Z rich text, emojis, alliance tags, coords, and acronyms survive translation."""

    def test_protect_and_restore_all_token_classes(self) -> None:
        sample = (
            "<e:7/> <color=#FF0000>Hi</color> <b>rally</b> [WARG] (214, 554) "
            "SvS HQ RSS NAP KE VS R4 R5 T8 T9 T10 AP BP S1 S6 (500:500)"
        )
        protected, tokens = TR_MOD.protect_game_tokens(sample)
        expected_tokens = [
            "<e:7/>",
            "<color=#FF0000>",
            "</color>",
            "<b>",
            "</b>",
            "[WARG]",
            "(214, 554)",
            "SvS",
            "HQ",
            "RSS",
            "NAP",
            "KE",
            "VS",
            "R4",
            "R5",
            "T8",
            "T9",
            "T10",
            "AP",
            "BP",
            "S1",
            "S6",
            "(500:500)",
        ]
        self.assertEqual(tokens, expected_tokens)
        for tok in expected_tokens:
            self.assertNotIn(tok, protected)
        self.assertIn("ZZTOK0ZZ", protected)
        self.assertEqual(TR_MOD.restore_game_tokens(protected, tokens), sample)

    def test_case_insensitive_and_spaced_placeholder_restoration(self) -> None:
        protected, tokens = TR_MOD.protect_game_tokens("hola [WARG] rally (214, 554) HQ")
        self.assertEqual(tokens, ["[WARG]", "(214, 554)", "HQ"])
        mangled = "hello zztok0zz rally ZZTOK 1 ZZ ZzTok2Zz"
        self.assertEqual(
            TR_MOD.restore_game_tokens(mangled, tokens),
            "hello [WARG] rally (214, 554) HQ",
        )

    def test_cjk_and_hangul_adjacent_acronyms_protected_without_false_english_hits(self) -> None:
        kr_text = "집결 시작합니다 HQ (500, 500) T10"
        protected_kr, tokens_kr = TR_MOD.protect_game_tokens(kr_text)
        self.assertEqual(tokens_kr, ["HQ", "(500, 500)", "T10"])
        self.assertEqual(TR_MOD.restore_game_tokens(protected_kr, tokens_kr), kr_text)

        zh_text = "攻打HQ和T10准备SvS"
        protected_zh, tokens_zh = TR_MOD.protect_game_tokens(zh_text)
        self.assertEqual(tokens_zh, ["HQ", "T10", "SvS"])
        self.assertEqual(TR_MOD.restore_game_tokens(protected_zh, tokens_zh), zh_text)

        plain_english = "taking a nap before we kept the snapshot rsvp"
        protected_en, tokens_en = TR_MOD.protect_game_tokens(plain_english)
        self.assertEqual(tokens_en, [])
        self.assertEqual(protected_en, plain_english)


class TestLanguageNormalization(unittest.TestCase):
    """Verify normalization across all 18 official Last Z languages and client quirks."""

    def test_all_18_official_languages_and_aliases(self) -> None:
        self.assertEqual(len(TR_MOD.OFFICIAL_LASTZ_LANGUAGES), 18)
        for code in TR_MOD.OFFICIAL_LASTZ_LANGUAGES:
            self.assertEqual(TR_MOD.normalize_lang_code(code), code)

        quirks = {
            "zh-Hant": "zh-TW",
            "zh_hant": "zh-TW",
            "zh-TW": "zh-TW",
            "zh-HK": "zh-TW",
            "zh-Hans": "zh-CN",
            "zh_CN": "zh-CN",
            "zh": "zh-CN",
            "vn": "vi",
            "VI_VN": "vi",
            "kr": "ko",
            "ko-KR": "ko",
            "jp": "ja",
            "ja-JP": "ja",
            "pt-BR": "pt",
            "es-MX": "es",
            "fr-CA": "fr",
            "de-AT": "de",
            "en-US": "en",
            "ar-SA": "ar",
            "in": "id",
            "auto": "en",
            "": "en",
        }
        for raw, expected in quirks.items():
            self.assertEqual(TR_MOD.normalize_lang_code(raw), expected, f"Failed for {raw}")


class TestProviderCascadeAndCache(unittest.TestCase):
    """Verify 4-tier cascade, optional API keys, skip logic, and LRU + SQLite cache."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.db_path = Path(self._td.name) / "translation cache.sqlite"
        self.cache = TR_MOD.TranslationCache(db_path=self.db_path, max_memory_entries=64, max_sqlite_rows=100)
        self.stats = TR_MOD.TranslatorStats()
        self.base_cfg = {
            "enabled": True,
            "auto_translate_chat": True,
            "target_lang": "auto",
            "deepl_api_key": "",
            "gemini_api_key": "",
        }

    def tearDown(self) -> None:
        self.cache.close()
        self._td.cleanup()

    def test_skip_pure_symbols_emojis_and_coords(self) -> None:
        with mock.patch.object(TR_MOD, "_http_request_json") as mock_http:
            for txt in ("", "   ", "12345!!!", "<e:7/> <e:12/>", "[WARG] HQ (214, 554)"):
                res = TR_MOD.translate_text(txt, target_lang="en", config=self.base_cfg, cache=self.cache, stats=self.stats)
                self.assertEqual(res["code"], 0)
                self.assertEqual(res["translateMsg"], txt)
                self.assertEqual(res["provider"], "skip")
            mock_http.assert_not_called()

    def test_tier1_google_gtx_success_and_token_preservation(self) -> None:
        def fake_http(url: str, **kwargs):
            self.assertIn("translate.googleapis.com/translate_a/single", url)
            qs = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            sent_q = qs["q"][0]
            # Wire text uses script-neutral markers so sl=auto is never skewed by Latin placeholder text
            self.assertNotIn("ZZTOK", sent_q)
            self.assertIn("\u27e60\u27e7", sent_q)
            self.assertIn("\u27e61\u27e7", sent_q)
            return [[["hello friends \u27e60\u27e7 rally \u27e61\u27e7", sent_q]], None, "es"]

        with mock.patch.object(TR_MOD, "_http_request_json", side_effect=fake_http) as mock_http:
            res = TR_MOD.translate_text(
                "hola amigos [WARG] rally (214, 554)",
                target_lang="en",
                config=self.base_cfg,
                cache=self.cache,
                stats=self.stats,
            )
            self.assertEqual(res["code"], 0)
            self.assertEqual(res["provider"], "google_gtx")
            self.assertEqual(res["originalLang"], "es")
            self.assertEqual(res["translateMsg"], "hello friends [WARG] rally (214, 554)")
            self.assertFalse(res["cached"])
            self.assertEqual(mock_http.call_count, 1)

    def test_cascade_tier1_fail_to_tier2_google_dict(self) -> None:
        calls: list[str] = []

        def fake_http(url: str, **kwargs):
            calls.append(url)
            if "translate.googleapis.com" in url:
                raise OSError("tier1 timeout")
            if "clients5.google.com" in url:
                return [["good morning ZZTOK0ZZ", "fr"]]
            raise AssertionError(f"Unexpected call: {url}")

        with mock.patch.object(TR_MOD, "_http_request_json", side_effect=fake_http):
            res = TR_MOD.translate_text(
                "bonjour HQ",
                target_lang="en",
                config=self.base_cfg,
                cache=self.cache,
                stats=self.stats,
            )
            self.assertEqual(res["provider"], "google_dict")
            self.assertEqual(res["originalLang"], "fr")
            self.assertEqual(res["translateMsg"], "good morning HQ")
            self.assertEqual(len(calls), 2)

    def test_cascade_tier1_tier2_fail_to_tier3_mymemory_script_heuristic(self) -> None:
        seen_langpair: list[str] = []

        def fake_http(url: str, **kwargs):
            if "translate.googleapis.com" in url or "clients5.google.com" in url:
                raise OSError("google unavailable")
            if "api.mymemory.translated.net" in url:
                qs = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
                seen_langpair.extend(qs.get("langpair", []))
                return {
                    "responseStatus": 200,
                    "responseData": {"translatedText": "Starting rally ZZTOK0ZZ ZZTOK1ZZ"},
                }
            raise AssertionError(f"Unexpected call: {url}")

        with mock.patch.object(TR_MOD, "_http_request_json", side_effect=fake_http):
            res = TR_MOD.translate_text(
                "집결 시작합니다 HQ (500, 500)",
                target_lang="en",
                config=self.base_cfg,
                cache=self.cache,
                stats=self.stats,
            )
            self.assertEqual(res["provider"], "mymemory")
            self.assertEqual(res["originalLang"], "ko")
            self.assertEqual(res["translateMsg"], "Starting rally HQ (500, 500)")
            self.assertEqual(seen_langpair, ["ko|en"])

    def test_cascade_falls_back_to_tier4_lastz_upstream(self) -> None:
        def fake_http(url: str, **kwargs):
            if "translate-lm.omnilojoapps.com" in url:
                return {"code": 0, "originalLang": "ru", "targetLang": "en", "translateMsg": "Attack now ZZTOK0ZZ"}
            raise OSError("tier failed")

        with mock.patch.object(TR_MOD, "_http_request_json", side_effect=fake_http):
            res = TR_MOD.translate_text(
                "Атакуем сейчас HQ",
                target_lang="en",
                config=self.base_cfg,
                cache=self.cache,
                stats=self.stats,
            )
            self.assertEqual(res["provider"], "lastz_upstream")
            self.assertEqual(res["originalLang"], "ru")
            self.assertEqual(res["translateMsg"], "Attack now HQ")

    def test_all_offline_returns_passthrough_and_never_caches_failure(self) -> None:
        with mock.patch.object(TR_MOD, "_http_request_json", side_effect=OSError("network down")) as mock_http:
            res = TR_MOD.translate_text(
                "hola todos",
                target_lang="en",
                config=self.base_cfg,
                cache=self.cache,
                stats=self.stats,
            )
            self.assertEqual(res["code"], 0)
            self.assertEqual(res["provider"], "passthrough")
            self.assertEqual(res["translateMsg"], "hola todos")
            self.assertFalse(res["cached"])
            self.assertGreaterEqual(mock_http.call_count, 4)

        # Ensure failure was NOT persisted in cache
        self.assertIsNone(self.cache.get("en", "hola todos"))

    def test_optional_deepl_key_used_only_when_configured(self) -> None:
        cfg_deepl = dict(self.base_cfg, deepl_api_key="test-key-123:fx")

        def fake_http(url: str, **kwargs):
            self.assertIn("api-free.deepl.com/v2/translate", url)
            return {"translations": [{"text": "Hello team ZZTOK0ZZ", "detected_source_language": "DE"}]}

        with mock.patch.object(TR_MOD, "_http_request_json", side_effect=fake_http) as mock_http:
            res = TR_MOD.translate_text(
                "Hallo Team [WARG]",
                target_lang="en",
                config=cfg_deepl,
                cache=self.cache,
                stats=self.stats,
            )
            self.assertEqual(res["provider"], "deepl")
            self.assertEqual(res["originalLang"], "de")
            self.assertEqual(res["translateMsg"], "Hello team [WARG]")
            self.assertEqual(mock_http.call_count, 1)

    def test_memory_and_sqlite_persistent_cache_hits_and_pruning(self) -> None:
        # 1st call hits provider; 2nd call hits memory cache; fresh cache instance hits SQLite
        with mock.patch.object(
            TR_MOD,
            "_http_request_json",
            return_value=[[["Good evening", "Buenas noches"]], None, "es"],
        ) as mock_http:
            r1 = TR_MOD.translate_text("Buenas noches", target_lang="en", config=self.base_cfg, cache=self.cache, stats=self.stats)
            self.assertFalse(r1["cached"])
            self.assertEqual(mock_http.call_count, 1)

            r2 = TR_MOD.translate_text("Buenas noches", target_lang="en", config=self.base_cfg, cache=self.cache, stats=self.stats)
            self.assertTrue(r2["cached"])
            self.assertEqual(r2["translateMsg"], "Good evening")
            self.assertEqual(mock_http.call_count, 1)

            cache2 = TR_MOD.TranslationCache(db_path=self.db_path)
            try:
                r3 = TR_MOD.translate_text("Buenas noches", target_lang="en", config=self.base_cfg, cache=cache2, stats=self.stats)
                self.assertTrue(r3["cached"])
                self.assertEqual(r3["translateMsg"], "Good evening")
                self.assertEqual(mock_http.call_count, 1)
            finally:
                cache2.close()

        # Verify WAL mode enabled on SQLite DB
        conn = sqlite3.connect(str(self.db_path))
        try:
            mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            self.assertEqual(str(mode).lower(), "wal")
        finally:
            conn.close()

        # Verify pruning caps SQLite rows at max_sqlite_rows
        prune_db = Path(self._td.name) / "prune cache.sqlite"
        small_cache = TR_MOD.TranslationCache(db_path=prune_db, max_memory_entries=4, max_sqlite_rows=5)
        try:
            for i in range(12):
                small_cache.put("en", f"msg {i}", "es", f"trans {i}", "google_gtx")
            self.assertLessEqual(small_cache.count_sqlite_rows(), 5)
        finally:
            small_cache.close()

    def test_load_translator_config_caches_by_path_mtime_and_size(self) -> None:
        cfg_path = Path(self._td.name) / "translator_cache_test.json"
        with TR_MOD._CONFIG_CACHE_LOCK:
            TR_MOD._CONFIG_CACHE_STATE.update({"path": None, "mtime_ns": -1, "size": -1, "cfg": None})
        try:
            missing = TR_MOD.load_translator_config(cfg_path)
            self.assertEqual(missing["target_lang"], "auto")

            cfg_path.write_text(json.dumps({"enabled": True, "target_lang": "es"}), encoding="utf-8")
            st0 = cfg_path.stat()
            c1 = TR_MOD.load_translator_config(cfg_path)
            self.assertEqual(c1["target_lang"], "es")

            with mock.patch.object(TR_MOD.json, "load", side_effect=AssertionError("cache miss on identical stat")):
                c2 = TR_MOD.load_translator_config(cfg_path)
                self.assertEqual(c2["target_lang"], "es")

            # Change file content/size while preserving exact st_atime_ns and st_mtime_ns
            cfg_path.write_text(json.dumps({"enabled": True, "target_lang": "zh-TW"}), encoding="utf-8")
            os.utime(cfg_path, ns=(st0.st_atime_ns, st0.st_mtime_ns))
            st1 = cfg_path.stat()
            self.assertEqual(int(st1.st_mtime_ns), int(st0.st_mtime_ns))
            self.assertNotEqual(int(st1.st_size), int(st0.st_size))

            c3 = TR_MOD.load_translator_config(cfg_path)
            self.assertEqual(c3["target_lang"], "zh-TW")

            # save_translator_config updates cache with resolved path, mtime_ns, and size
            TR_MOD.save_translator_config({"enabled": False, "target_lang": "fr"}, config_path=cfg_path)
            with mock.patch.object(TR_MOD.json, "load", side_effect=AssertionError("save must populate cache")):
                c4 = TR_MOD.load_translator_config(cfg_path)
                self.assertFalse(c4["enabled"])
                self.assertEqual(c4["target_lang"], "fr")

            # Deleting cached file invalidates cache and returns defaults
            cfg_path.unlink()
            c5 = TR_MOD.load_translator_config(cfg_path)
            self.assertEqual(c5["target_lang"], "auto")
            self.assertTrue(c5["enabled"])
        finally:
            with TR_MOD._CONFIG_CACHE_LOCK:
                TR_MOD._CONFIG_CACHE_STATE.update(
                    {
                        "path": None,
                        "mtime_ns": -1,
                        "size": -1,
                        "dpapi_path": None,
                        "dpapi_mtime_ns": -1,
                        "dpapi_size": -1,
                        "cfg": None,
                    }
                )

    def test_dpapi_key_storage_legacy_migration_and_sanitize(self) -> None:
        cfg_path = Path(self._td.name) / "translator config.json"
        dpapi_path = TR_MOD.get_dpapi_keys_path(cfg_path)
        self.assertEqual(dpapi_path.name, "translator config.dpapi.json")

        # Default path resolves into json cache/translator dpapi keys.json
        self.assertEqual(TR_MOD.get_dpapi_keys_path().name, "translator dpapi keys.json")

        with TR_MOD._CONFIG_CACHE_LOCK:
            TR_MOD._CONFIG_CACHE_STATE.update(
                {
                    "path": None,
                    "mtime_ns": -1,
                    "size": -1,
                    "dpapi_path": None,
                    "dpapi_mtime_ns": -1,
                    "dpapi_size": -1,
                    "cfg": None,
                }
            )
        try:
            deepl_secret = "11112222-3333-4444-5555-666677778888:fx"
            gemini_secret = "AIzaSyTestExampleKey9876543210abcdefg"

            saved = TR_MOD.save_translator_config(
                {
                    "enabled": True,
                    "auto_translate_chat": True,
                    "target_lang": "es",
                    "deepl_api_key": deepl_secret,
                    "gemini_api_key": gemini_secret,
                },
                config_path=cfg_path,
            )
            self.assertEqual(saved["deepl_api_key"], deepl_secret)
            self.assertEqual(saved["gemini_api_key"], gemini_secret)

            # Plaintext keys must NEVER appear in translator config.json or on disk in DPAPI file
            cfg_text = cfg_path.read_text(encoding="utf-8")
            self.assertNotIn(deepl_secret, cfg_text)
            self.assertNotIn(gemini_secret, cfg_text)
            self.assertNotIn("deepl_api_key", cfg_text)
            self.assertNotIn("gemini_api_key", cfg_text)

            self.assertTrue(dpapi_path.is_file())
            dpapi_text = dpapi_path.read_text(encoding="utf-8")
            self.assertNotIn(deepl_secret, dpapi_text)
            self.assertNotIn(gemini_secret, dpapi_text)

            # Cold load decrypts keys cleanly
            with TR_MOD._CONFIG_CACHE_LOCK:
                TR_MOD._CONFIG_CACHE_STATE.update(
                    {
                        "path": None,
                        "mtime_ns": -1,
                        "size": -1,
                        "dpapi_path": None,
                        "dpapi_mtime_ns": -1,
                        "dpapi_size": -1,
                        "cfg": None,
                    }
                )
            loaded = TR_MOD.load_translator_config(cfg_path)
            self.assertEqual(loaded["deepl_api_key"], deepl_secret)
            self.assertEqual(loaded["gemini_api_key"], gemini_secret)

            sanitized = TR_MOD.sanitize_translator_config(loaded)
            self.assertEqual(
                sanitized,
                {
                    "enabled": True,
                    "auto_translate_chat": True,
                    "target_lang": "es",
                    "has_deepl_key": True,
                    "has_gemini_key": True,
                },
            )
            self.assertNotIn("deepl_api_key", sanitized)
            self.assertNotIn("gemini_api_key", sanitized)

            # Legacy plaintext migration scrubs translator config.json and encrypts into DPAPI file
            legacy_cfg = Path(self._td.name) / "legacy translator config.json"
            legacy_dpapi = TR_MOD.get_dpapi_keys_path(legacy_cfg)
            legacy_cfg.write_text(
                json.dumps(
                    {
                        "enabled": True,
                        "auto_translate_chat": False,
                        "target_lang": "fr",
                        "deepl_api_key": deepl_secret,
                        "gemini_api_key": gemini_secret,
                    }
                ),
                encoding="utf-8",
            )
            migrated = TR_MOD.load_translator_config(legacy_cfg)
            self.assertEqual(migrated["deepl_api_key"], deepl_secret)
            self.assertEqual(migrated["gemini_api_key"], gemini_secret)
            self.assertEqual(migrated["target_lang"], "fr")
            self.assertFalse(migrated["auto_translate_chat"])

            scrubbed_text = legacy_cfg.read_text(encoding="utf-8")
            self.assertNotIn(deepl_secret, scrubbed_text)
            self.assertNotIn(gemini_secret, scrubbed_text)
            self.assertNotIn("deepl_api_key", scrubbed_text)
            self.assertTrue(legacy_dpapi.is_file())
            self.assertNotIn(deepl_secret, legacy_dpapi.read_text(encoding="utf-8"))

            # If DPAPI write fails during legacy migration, translator config.json must NOT be scrubbed
            fail_cfg = Path(self._td.name) / "fail legacy config.json"
            fail_cfg.write_text(
                json.dumps({"enabled": True, "target_lang": "es", "deepl_api_key": deepl_secret}),
                encoding="utf-8",
            )
            with mock.patch.object(TR_MOD, "_save_dpapi_keys", side_effect=RuntimeError("dpapi unavailable")):
                preserved = TR_MOD.load_translator_config(fail_cfg)
            self.assertEqual(preserved["deepl_api_key"], deepl_secret)
            self.assertIn(deepl_secret, fail_cfg.read_text(encoding="utf-8"))
        finally:
            with TR_MOD._CONFIG_CACHE_LOCK:
                TR_MOD._CONFIG_CACHE_STATE.update(
                    {
                        "path": None,
                        "mtime_ns": -1,
                        "size": -1,
                        "dpapi_path": None,
                        "dpapi_mtime_ns": -1,
                        "dpapi_size": -1,
                        "cfg": None,
                    }
                )

    def test_concurrent_config_save_and_load_zero_errors(self) -> None:
        cfg_path = Path(self._td.name) / "concurrent translator config.json"
        with TR_MOD._CONFIG_CACHE_LOCK:
            TR_MOD._CONFIG_CACHE_STATE.update(
                {
                    "path": None,
                    "mtime_ns": -1,
                    "size": -1,
                    "dpapi_path": None,
                    "dpapi_mtime_ns": -1,
                    "dpapi_size": -1,
                    "cfg": None,
                }
            )
        errors: list[BaseException] = []
        barrier = threading.Barrier(12)

        def worker(tid: int) -> None:
            try:
                barrier.wait(timeout=5.0)
                for idx in range(15):
                    TR_MOD.save_translator_config(
                        {
                            "enabled": True,
                            "auto_translate_chat": (idx % 2 == 0),
                            "target_lang": "es" if (tid + idx) % 2 == 0 else "fr",
                            "deepl_api_key": f"11112222-3333-4444-5555-66667777{tid:02d}{idx:02d}:fx",
                            "gemini_api_key": f"AIzaSyConcurrentTestKey{tid:02d}{idx:02d}abcdef",
                        },
                        config_path=cfg_path,
                    )
                    loaded = TR_MOD.load_translator_config(cfg_path)
                    if loaded["target_lang"] not in ("es", "fr"):
                        raise AssertionError(f"Unexpected target_lang: {loaded['target_lang']}")
            except BaseException as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(12)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30.0)
        self.assertEqual(errors, [])
        self.assertFalse(any(t.is_alive() for t in threads))


class TestLocalHttpServerRoundtrip(unittest.TestCase):
    """Real localhost HTTP server tests on an ephemeral port (port=0) with mocked upstream provider."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        td_path = Path(self._td.name)
        self.cfg_path = td_path / "translator config.json"
        self.bridge_path = td_path / "translator bridge.json"
        self.db_path = td_path / "translation cache.sqlite"
        TR_MOD.save_translator_config(
            {"enabled": True, "auto_translate_chat": True, "target_lang": "auto"},
            config_path=self.cfg_path,
        )
        self.cache = TR_MOD.TranslationCache(db_path=self.db_path)
        self.stats = TR_MOD.TranslatorStats()
        self.server = TR_MOD.LiveTranslatorServer(
            host="127.0.0.1",
            port=0,
            cache=self.cache,
            stats=self.stats,
            config_path=self.cfg_path,
            bridge_path=self.bridge_path,
            write_bridge=True,
        )
        self.info = self.server.start()
        self.base_url = f"http://127.0.0.1:{self.info['port']}"

    def tearDown(self) -> None:
        self.server.stop()
        self.cache.close()
        self._td.cleanup()

    def test_client_php_form_get_health_stats_and_translate(self) -> None:
        # Bridge file written atomically
        self.assertTrue(self.bridge_path.exists())
        bridge_data = json.loads(self.bridge_path.read_text(encoding="utf-8"))
        self.assertTrue(bridge_data["running"])
        self.assertEqual(bridge_data["port"], self.info["port"])

        def fake_provider(text: str, tl: str, sl: str, timeout: float = 4.0):
            return (f"TR({tl}): {text}", "es")

        with mock.patch.object(TR_MOD, "_provider_google_gtx", side_effect=fake_provider):
            # 1. Exact Last Z POST /client.php form request
            form = urllib.parse.urlencode(
                {
                    "sf": "",
                    "tf": "en",
                    "sc": "hola amigos [WARG] (214, 554)",
                    "uid": "1848029704000694",
                    "ui": "en",
                    "ch": "alliance",
                    "scene": "1",
                    "mod": "chat",
                    "google": "1",
                    "tk": "abc123",
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/client.php",
                data=form,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                self.assertEqual(resp.status, 200)
                self.assertIn("application/json", resp.headers.get("Content-Type", ""))
                body = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(
                body,
                {
                    "code": 0,
                    "originalLang": "es",
                    "targetLang": "en",
                    "translateMsg": "TR(en): hola amigos [WARG] (214, 554)",
                },
            )

            # 2. zh-Hant request normalizes to zh-TW internally while echoing targetLang=zh-Hant
            form_tw = urllib.parse.urlencode({"sf": "", "tf": "zh-Hant", "sc": "hola"}).encode("utf-8")
            req_tw = urllib.request.Request(
                f"{self.base_url}/client.php",
                data=form_tw,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req_tw, timeout=5.0) as resp_tw:
                body_tw = json.loads(resp_tw.read().decode("utf-8"))
            self.assertEqual(body_tw["code"], 0)
            self.assertEqual(body_tw["targetLang"], "zh-Hant")
            self.assertEqual(body_tw["translateMsg"], "TR(zh-TW): hola")

            # 3. GET /client.php?sc=...&tf=en (hits cache from call #1!)
            qs = urllib.parse.urlencode({"sc": "hola amigos [WARG] (214, 554)", "tf": "en"})
            with urllib.request.urlopen(f"{self.base_url}/client.php?{qs}", timeout=5.0) as resp_get:
                body_get = json.loads(resp_get.read().decode("utf-8"))
            self.assertEqual(body_get["code"], 0)
            self.assertEqual(body_get["translateMsg"], "TR(en): hola amigos [WARG] (214, 554)")

            # 4. POST /translate (Hub UI Test Box endpoint)
            req_tr = urllib.request.Request(
                f"{self.base_url}/translate",
                data=json.dumps({"text": "buenos dias HQ", "target_lang": "en"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_tr, timeout=5.0) as resp_tr:
                body_tr = json.loads(resp_tr.read().decode("utf-8"))
            self.assertTrue(body_tr["ok"])
            self.assertEqual(body_tr["provider"], "google_gtx")
            self.assertEqual(body_tr["translateMsg"], "TR(en): buenos dias HQ")
            self.assertIn("elapsed_ms", body_tr)

            # 5. GET /health
            with urllib.request.urlopen(f"{self.base_url}/health", timeout=5.0) as resp_h:
                body_h = json.loads(resp_h.read().decode("utf-8"))
            self.assertTrue(body_h["ok"])
            self.assertEqual(body_h["port"], self.info["port"])
            self.assertTrue(body_h["enabled"])
            self.assertEqual(body_h["target_lang"], "auto")

            # 6. GET /stats
            with urllib.request.urlopen(f"{self.base_url}/stats", timeout=5.0) as resp_s:
                body_s = json.loads(resp_s.read().decode("utf-8"))
            self.assertTrue(body_s["ok"])
            self.assertEqual(body_s["total_requests"], 4)
            self.assertEqual(body_s["cache_hits"], 1)
            self.assertIn("avg_ms", body_s)
            self.assertEqual(len(body_s["recent"]), 4)


class TestLuaHookGeneratorAndBehavior(unittest.TestCase):
    """Execute generated Lua hooks inside lupa to verify idempotency, rate limiting, and restore."""

    def test_enable_idempotency_auto_translate_and_disable_restore(self) -> None:
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(
            r"""
            _G.TranslateUrlList = { "https://translate-lm.omnilojoapps.com/client.php" }
            _G._translatedCalls = {}
            _G._origLangCalls = 0
            _G._origHandleCalls = 0

            local tm = {}
            function tm:GetLangString()
                _G._origLangCalls = _G._origLangCalls + 1
                return "en"
            end
            function tm:DoTranslate(msg)
                _G._translatedCalls[#_G._translatedCalls + 1] = msg.seqId
                msg.isTranslating = 1
            end

            local cm = { Translate = tm }
            function cm:OnHandleMessage(cmd, payload)
                _G._origHandleCalls = _G._origHandleCalls + 1
                return "HANDLED:" .. tostring(cmd)
            end

            _G.ChatManager2 = { Instance = cm }
            """
        )

        # 1. Enable hook with explicit target override "es" and auto_translate_chat=True
        hook_on = TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="es", auto_translate_chat=True)
        res1 = lua.execute(hook_on)
        self.assertEqual(res1, "TRANSLATOR_HOOK_ENABLED:18765:es")
        self.assertEqual(lua.eval("_G.TranslateUrlList[1]"), "http://127.0.0.1:18765/client.php")
        self.assertEqual(lua.eval("_G.__HEINZ_ORIG_TRANSLATE_URLS__[1]"), "https://translate-lm.omnilojoapps.com/client.php")
        self.assertEqual(lua.eval("_G.ChatManager2.Instance.Translate:GetLangString()"), "es")

        # 2. Re-running hook is idempotent (original URLs preserved, no double wrap)
        hook_on_2 = TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="auto", auto_translate_chat=True)
        res2 = lua.execute(hook_on_2)
        self.assertEqual(res2, "TRANSLATOR_HOOK_ENABLED:18765:auto")
        self.assertEqual(lua.eval("_G.__HEINZ_ORIG_TRANSLATE_URLS__[1]"), "https://translate-lm.omnilojoapps.com/client.php")
        self.assertEqual(lua.eval("_G.ChatManager2.Instance.Translate:GetLangString()"), "en")
        self.assertEqual(lua.eval("_G._origLangCalls"), 1)

        # 3. Incoming user messages auto-translate, dedupe by seqId, filter non-user, and cap at 3/sec
        lua.execute(
            r"""
            local cm = _G.ChatManager2.Instance
            -- Eligible messages 1..4 (4th should be rate-limited in same second)
            cm:OnHandleMessage("push", { type = 0, msg = "hola 1", translateMsg = "", isTranslating = 0, seqId = 101 })
            cm:OnHandleMessage("push", { type = 0, msg = "hola 1 dup", translateMsg = "", isTranslating = 0, seqId = 101 })
            cm:OnHandleMessage("push", { type = 2, msg = "system msg", translateMsg = "", isTranslating = 0, seqId = 102 })
            cm:OnHandleMessage("push", { type = 0, msg = "already done", translateMsg = "hi", isTranslating = 0, seqId = 103 })
            cm:OnHandleMessage("push", { type = 0, msg = "in flight", translateMsg = "", isTranslating = 1, seqId = 104 })
            cm:OnHandleMessage("push", { type = 0, msg = "hola 2", translateMsg = "", isTranslating = 0, seqId = 105 })
            cm:OnHandleMessage("push", { type = 0, msg = "hola 3", translateMsg = "", isTranslating = 0, seqId = 106 })
            cm:OnHandleMessage("push", { type = 0, msg = "hola 4 capped", translateMsg = "", isTranslating = 0, seqId = 107 })
            """
        )
        self.assertEqual(lua.eval("#_G._translatedCalls"), 3)
        self.assertEqual(lua.eval("_G._translatedCalls[1]"), 101)
        self.assertEqual(lua.eval("_G._translatedCalls[2]"), 105)
        self.assertEqual(lua.eval("_G._translatedCalls[3]"), 106)
        self.assertEqual(lua.eval("_G._origHandleCalls"), 8)

        # 4. Disable hook restores original URLs and disables auto-translate & override
        hook_off = TR_MOD.build_translator_lua_hook(18765, enabled=False, target_lang="es", auto_translate_chat=False)
        res_off = lua.execute(hook_off)
        self.assertEqual(res_off, "TRANSLATOR_HOOK_DISABLED")
        self.assertEqual(lua.eval("_G.TranslateUrlList[1]"), "https://translate-lm.omnilojoapps.com/client.php")
        self.assertFalse(lua.eval("_G.__HEINZ_TRANSLATOR_CFG__.enabled"))
        self.assertEqual(lua.eval("_G.ChatManager2.Instance.Translate:GetLangString()"), "en")

    def test_direct_singleton_getinstance_room_addchat_and_gate_bypass_restore(self) -> None:
        # 1. Direct _G.ChatManager2 singleton (NO .Instance) + ChatInterface.getTranslateMgr fallback + Room.AddChat + roomDic
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(
            r"""
            _G.TranslateUrlList = { "https://translate-lm.omnilojoapps.com/client.php" }
            _G._translatedMsgs = {}
            _G._dcSelfCalls = {}
            _G._cuKeyCalls = {}

            local tm = {}
            function tm:GetLangString()
                return "en"
            end
            function tm:DoTranslate(msg)
                _G._translatedMsgs[#_G._translatedMsgs + 1] = msg.seqId or msg.msg
            end

            _G.ChatInterface = {
                getTranslateMgr = function()
                    return tm
                end,
                GetAotuTra = function()
                    return false
                end,
            }

            local roomObj = { msgs = {} }
            local rm = {
                roomDic = { alliance = roomObj },
            }
            function rm:AddChat(roomId, msgObj)
                roomObj.msgs[#roomObj.msgs + 1] = msgObj
                return "ADDED:" .. tostring(roomId)
            end

            -- Direct singleton: no .Instance field
            _G.ChatManager2 = {
                Room = rm,
            }

            _G.LuaEntry = {
                DataConfig = {
                    CheckSwitch = function(self, key)
                        _G._dcSelfCalls[#_G._dcSelfCalls + 1] = { isSelf = (self == _G.LuaEntry.DataConfig), key = key }
                        if key == "war_detail" then return true end
                        return false
                    end,
                },
            }
            _G.ChatUtils = {
                CheckSwitch = function(key)
                    _G._cuKeyCalls[#_G._cuKeyCalls + 1] = tostring(key)
                    return false
                end,
            }
            _G.DataCenter = {
                MonthCardNewManager = {
                    CheckAutoTraActive = function(self)
                        return false
                    end,
                    CheckAutoTraAvailable = function(self)
                        return false
                    end,
                },
            }
            """
        )

        hook_on = TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="fr", auto_translate_chat=True)
        res = lua.execute(hook_on)
        self.assertEqual(res, "TRANSLATOR_HOOK_ENABLED:18765:fr")
        self.assertEqual(lua.eval("_G.ChatInterface.getTranslateMgr():GetLangString()"), "fr")

        # Switch & month card gates bypassed when enabled + auto_translate_chat
        self.assertTrue(lua.eval('_G.LuaEntry.DataConfig:CheckSwitch("screen_translation")'))
        self.assertTrue(lua.eval('_G.LuaEntry.DataConfig:CheckSwitch("war_detail")'))
        self.assertFalse(lua.eval('_G.LuaEntry.DataConfig:CheckSwitch("other_flag")'))
        self.assertEqual(lua.eval("#_G._dcSelfCalls"), 2)
        self.assertTrue(lua.eval("_G._dcSelfCalls[1].isSelf"))
        self.assertEqual(lua.eval("_G._dcSelfCalls[1].key"), "war_detail")

        self.assertTrue(lua.eval('_G.ChatUtils.CheckSwitch("screen_translation")'))
        self.assertFalse(lua.eval('_G.ChatUtils.CheckSwitch("other_chat_flag")'))
        self.assertEqual(lua.eval("#_G._cuKeyCalls"), 1)
        self.assertEqual(lua.eval("_G._cuKeyCalls[1]"), "other_chat_flag")

        self.assertTrue(lua.eval("_G.DataCenter.MonthCardNewManager:CheckAutoTraActive()"))
        self.assertTrue(lua.eval("_G.DataCenter.MonthCardNewManager:CheckAutoTraAvailable()"))
        self.assertTrue(lua.eval("_G.ChatInterface.GetAotuTra()"))

        # Room:AddChat translates message using getChatMessageType() even without msg.type
        ret_add = lua.eval(
            '_G.ChatManager2.Room:AddChat("alliance", { msg = "bonjour", seqId = 777, getChatMessageType = function(self) return 0 end })'
        )
        self.assertEqual(ret_add, "ADDED:alliance")
        self.assertEqual(lua.eval("#_G._translatedMsgs"), 1)
        self.assertEqual(lua.eval("_G._translatedMsgs[1]"), 777)

        # Non-mutating diagnostics JSON reflects real wrapped state
        diag_lua = TR_MOD.build_translator_diag_lua()
        diag = json.loads(lua.execute(diag_lua))
        self.assertTrue(diag["hooked"])
        self.assertTrue(diag["hasCm"])
        self.assertTrue(diag["hasTm"])
        self.assertTrue(diag["screenTranslation"])
        self.assertTrue(diag["autoTraActive"])
        self.assertEqual(diag["translateUrl"], "http://127.0.0.1:18765/client.php")

        # Turning off auto_translate_chat restores gates while keeping TranslateUrlList and GetLangString active
        res_manual = lua.execute(
            TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="fr", auto_translate_chat=False)
        )
        self.assertEqual(res_manual, "TRANSLATOR_HOOK_ENABLED:18765:fr")
        self.assertFalse(lua.eval('_G.LuaEntry.DataConfig:CheckSwitch("screen_translation")'))
        self.assertFalse(lua.eval('_G.ChatUtils.CheckSwitch("screen_translation")'))
        self.assertFalse(lua.eval("_G.DataCenter.MonthCardNewManager:CheckAutoTraActive()"))
        self.assertFalse(lua.eval("_G.ChatInterface.GetAotuTra()"))
        self.assertEqual(lua.eval("_G.ChatInterface.getTranslateMgr():GetLangString()"), "fr")

        # Disabling completely restores GetLangString and TranslateUrlList, and diag reports hooked=False
        res_off = lua.execute(TR_MOD.build_translator_lua_hook(18765, enabled=False, target_lang="fr", auto_translate_chat=False))
        self.assertEqual(res_off, "TRANSLATOR_HOOK_DISABLED")
        self.assertEqual(lua.eval("_G.ChatInterface.getTranslateMgr():GetLangString()"), "en")
        diag_off = json.loads(lua.execute(diag_lua))
        self.assertFalse(diag_off["hooked"])
        self.assertFalse(diag_off["screenTranslation"])
        self.assertFalse(diag_off["autoTraActive"])

    def test_getinstance_and_pending_status_when_no_targets(self) -> None:
        # 1. No ChatManager2 / TranslateManager -> TRANSLATOR_HOOK_PENDING (never falsely ENABLED)
        lua_empty = LuaRuntime(unpack_returned_tuples=True)
        res_pending = lua_empty.execute(
            TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="auto", auto_translate_chat=True)
        )
        self.assertEqual(res_pending, "TRANSLATOR_HOOK_PENDING:18765:auto")
        diag_empty = json.loads(lua_empty.execute(TR_MOD.build_translator_diag_lua()))
        self.assertFalse(diag_empty["hooked"])
        self.assertFalse(diag_empty["hasCm"])
        self.assertFalse(diag_empty["hasTm"])

        # 2. :GetInstance() + ChatUtils.GetTranslateManager() fallback
        lua_gi = LuaRuntime(unpack_returned_tuples=True)
        lua_gi.execute(
            r"""
            _G._giCalls = 0
            local tm = {
                GetLangString = function(self) return "en" end,
                DoTranslate = function(self, msg) end,
            }
            _G.ChatUtils = {
                GetTranslateManager = function() return tm end,
            }
            local inst = {
                OnHandleMessage = function(self, a1) return "OK" end,
            }
            _G.ChatManager2 = {
                GetInstance = function(self)
                    _G._giCalls = _G._giCalls + 1
                    return inst
                end,
            }
            """
        )
        res_gi = lua_gi.execute(
            TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="de", auto_translate_chat=True)
        )
        self.assertEqual(res_gi, "TRANSLATOR_HOOK_ENABLED:18765:de")
        self.assertGreaterEqual(lua_gi.eval("_G._giCalls"), 1)
        self.assertEqual(lua_gi.eval("_G.ChatUtils.GetTranslateManager():GetLangString()"), "de")

    def test_rehook_after_game_replaces_functions_and_diag_partial_unhook(self) -> None:
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(
            r"""
            _G.TranslateUrlList = { "https://translate-lm.omnilojoapps.com/client.php" }
            _G.doCalls = 0
            _G.newCmCalls = 0
            _G.newRmCalls = 0
            _G.newCheckCalls = 0

            local tm = {
                GetLangString = function(self) return "en" end,
                DoTranslate = function(self, msg) _G.doCalls = _G.doCalls + 1 end,
            }
            local rm = {
                AddChat = function(self, roomId, msgObj) return "OLD_RM" end,
            }
            local cm = {
                Translate = tm,
                Room = rm,
                OnHandleMessage = function(self, cmd, msgObj) return "OLD_CM" end,
            }
            _G.ChatManager2 = cm
            _G.LuaEntry = {
                DataConfig = {
                    CheckSwitch = function(self, key) return false end,
                },
            }
            """
        )

        hook_cmd = TR_MOD.build_translator_lua_hook(18765, enabled=True, target_lang="en", auto_translate_chat=True)
        diag_cmd = TR_MOD.build_translator_diag_lua()
        self.assertEqual(lua.execute(hook_cmd), "TRANSLATOR_HOOK_ENABLED:18765:en")
        self.assertTrue(json.loads(lua.execute(diag_cmd))["hooked"])

        # Game replaces cm.OnHandleMessage while tm.GetLangString and rm.AddChat stay wrapped
        lua.execute(
            r"""
            _G.ChatManager2.OnHandleMessage = function(self, cmd, msgObj)
                _G.newCmCalls = _G.newCmCalls + 1
                return "NEW_CM"
            end
            """
        )
        diag_partial_cm = json.loads(lua.execute(diag_cmd))
        self.assertFalse(diag_partial_cm["hooked"])

        # Re-hook must wrap the game's NEW OnHandleMessage (calling both new handler and DoTranslate)
        self.assertEqual(lua.execute(hook_cmd), "TRANSLATOR_HOOK_ENABLED:18765:en")
        self.assertTrue(json.loads(lua.execute(diag_cmd))["hooked"])
        ret_cm = lua.eval(
            '_G.ChatManager2:OnHandleMessage("push", { type = 0, msg = "hola nuevo", translateMsg = "", isTranslating = 0, seqId = 9001 })'
        )
        self.assertEqual(ret_cm, "NEW_CM")
        self.assertEqual(lua.eval("_G.newCmCalls"), 1)
        self.assertEqual(lua.eval("_G.doCalls"), 1)

        # Game replaces rm.AddChat and LuaEntry.DataConfig.CheckSwitch -> diag detects partial unhook, re-hook wraps new functions
        lua.execute(
            r"""
            _G.ChatManager2.Room.AddChat = function(self, roomId, msgObj)
                _G.newRmCalls = _G.newRmCalls + 1
                return "NEW_RM"
            end
            _G.LuaEntry.DataConfig.CheckSwitch = function(self, key)
                _G.newCheckCalls = _G.newCheckCalls + 1
                return key == "custom_switch"
            end
            """
        )
        diag_partial_rm = json.loads(lua.execute(diag_cmd))
        self.assertFalse(diag_partial_rm["hooked"])
        self.assertEqual(lua.eval("_G.newCheckCalls"), 1)

        self.assertEqual(lua.execute(hook_cmd), "TRANSLATOR_HOOK_ENABLED:18765:en")
        self.assertTrue(json.loads(lua.execute(diag_cmd))["hooked"])
        ret_rm = lua.eval(
            '_G.ChatManager2.Room:AddChat("world", { type = 0, msg = "salut nuevo", translateMsg = "", isTranslating = 0, seqId = 9002 })'
        )
        self.assertEqual(ret_rm, "NEW_RM")
        self.assertEqual(lua.eval("_G.newRmCalls"), 1)
        self.assertEqual(lua.eval("_G.doCalls"), 2)
        self.assertTrue(lua.eval('_G.LuaEntry.DataConfig:CheckSwitch("screen_translation")'))
        self.assertEqual(lua.eval("_G.newCheckCalls"), 1)
        self.assertTrue(lua.eval('_G.LuaEntry.DataConfig:CheckSwitch("custom_switch")'))
        self.assertEqual(lua.eval("_G.newCheckCalls"), 2)


class TestDaemonWiringAndGuardrails(unittest.TestCase):
    """Verify daemon translator integration, Hub RPCs, DOM contracts, and repo guardrails."""

    def test_daemon_sync_translator_hook_routes_via_frida_eval_lua(self) -> None:
        fake_cd = mock.MagicMock()
        fake_cd._xlua_loaded.return_value = True
        fake_cd.frida_eval_lua.return_value = (True, "TRANSLATOR_HOOK_ENABLED:18765:auto")
        ok, res = DAEMON_MOD.sync_translator_hook(
            fake_cd,
            4321,
            TR_MOD,
            18765,
            {"enabled": True, "target_lang": "auto", "auto_translate_chat": True},
        )
        self.assertTrue(ok)
        self.assertEqual(res, "TRANSLATOR_HOOK_ENABLED:18765:auto")
        fake_cd.frida_eval_lua.assert_called_once()
        self.assertIn("http://127.0.0.1:18765/client.php", fake_cd.frida_eval_lua.call_args[0][1])

    def test_daemon_hook_version_invalidation_and_pending_retry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "translator config.json"
            cfg_path.write_text(json.dumps({"enabled": True, "target_lang": "en", "auto_translate_chat": True}), encoding="utf-8")

            fake_tr = mock.MagicMock()
            fake_tr.TRANSLATOR_HOOK_VERSION = 1
            fake_tr.get_config_path.return_value = cfg_path
            fake_tr.ensure_server_running.return_value = {"running": True, "port": 18765, "external": False}

            patched_pids = {101: {"pid": 101, "exe_name": "Survival.exe", "label": "Main"}}
            hook_sig: dict = {}
            retry_after: dict = {}
            tr_state = {"port": 0, "started_here": False, "last_probe_at": 0.0, "prev_enabled": True}
            cfg_cache: dict = {}

            # 1. PENDING result must NOT cache translator_hook_sig and must set retry cooldown (+5.0s)
            with mock.patch.object(DAEMON_MOD, "sync_translator_hook", return_value=(True, "TRANSLATOR_HOOK_PENDING:18765:en")) as mock_sync:
                DAEMON_MOD._sync_translator_tick(
                    None, fake_tr, {101}, patched_pids, hook_sig, retry_after, tr_state, cfg_cache, now_mono=100.0
                )
                self.assertEqual(mock_sync.call_count, 1)
                self.assertNotIn(101, hook_sig)
                self.assertAlmostEqual(retry_after[101], 105.0)

                # Within cooldown (t=102.0) does not retry yet
                DAEMON_MOD._sync_translator_tick(
                    None, fake_tr, {101}, patched_pids, hook_sig, retry_after, tr_state, cfg_cache, now_mono=102.0
                )
                self.assertEqual(mock_sync.call_count, 1)

            # 2. NO_TARGET also does not cache
            with mock.patch.object(DAEMON_MOD, "sync_translator_hook", return_value=(True, "TRANSLATOR_HOOK_NO_TARGET:18765")) as mock_sync:
                DAEMON_MOD._sync_translator_tick(
                    None, fake_tr, {101}, patched_pids, hook_sig, retry_after, tr_state, cfg_cache, now_mono=106.0
                )
                self.assertEqual(mock_sync.call_count, 1)
                self.assertNotIn(101, hook_sig)

            # 3. ENABLED caches sig; bumping TRANSLATOR_HOOK_VERSION invalidates sig and re-hooks
            with mock.patch.object(DAEMON_MOD, "sync_translator_hook", return_value=(True, "TRANSLATOR_HOOK_ENABLED:18765:en")) as mock_sync:
                DAEMON_MOD._sync_translator_tick(
                    None, fake_tr, {101}, patched_pids, hook_sig, retry_after, tr_state, cfg_cache, now_mono=112.0
                )
                self.assertEqual(mock_sync.call_count, 1)
                self.assertIn(101, hook_sig)
                self.assertEqual(hook_sig[101][0], 1)

                # Same version -> cached, no call
                DAEMON_MOD._sync_translator_tick(
                    None, fake_tr, {101}, patched_pids, hook_sig, retry_after, tr_state, cfg_cache, now_mono=113.0
                )
                self.assertEqual(mock_sync.call_count, 1)

                # Bump TRANSLATOR_HOOK_VERSION -> re-syncs immediately
                fake_tr.TRANSLATOR_HOOK_VERSION = 2
                DAEMON_MOD._sync_translator_tick(
                    None, fake_tr, {101}, patched_pids, hook_sig, retry_after, tr_state, cfg_cache, now_mono=114.0
                )
                self.assertEqual(mock_sync.call_count, 2)
                self.assertEqual(hook_sig[101][0], 2)

    def test_hub_translator_status_rehook_and_redaction(self) -> None:
        hub_mod = _load_mod("test_hub_live_translator_mod", "launcher/heinzhubweb.py")

        deepl_secret = "abcdef12-3456-7890-abcd-ef1234567890:fx"
        gemini_secret = "AIzaSyTEST_SENTINEL_1234567890abcdefghi"
        redacted = hub_mod._redact_text(
            f"err deepl_api_key={deepl_secret} DeepL-Auth-Key {deepl_secret} x-goog-api-key: {gemini_secret} {gemini_secret}"
        )
        self.assertNotIn(deepl_secret, redacted)
        self.assertNotIn(gemini_secret, redacted)

        bearer_redacted = hub_mod._redact_text("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9+abc/def==")
        self.assertEqual(bearer_redacted, "Authorization: <REDACTED>")
        self.assertNotIn("+abc/def==", bearer_redacted)

        init_params = inspect.signature(hub_mod.HubBackend.__init__).parameters
        kwargs = {"defer_enhanced": True} if "defer_enhanced" in init_params else {}
        with contextlib.ExitStack() as stack:
            for attr_name in (
                "_load_cached_state",
                "_load_always_on_daemon_config",
                "_start_always_on_daemon",
                "_ensure_translator_bg",
                "log",
            ):
                if hasattr(hub_mod.HubBackend, attr_name):
                    stack.enter_context(mock.patch.object(hub_mod.HubBackend, attr_name))
            backend = hub_mod.HubBackend(**kwargs)

        fake_tr = mock.MagicMock()
        fake_tr.load_translator_config.return_value = {
            "enabled": True,
            "auto_translate_chat": True,
            "target_lang": "en",
            "deepl_api_key": deepl_secret,
            "gemini_api_key": gemini_secret,
        }
        fake_tr.ensure_server_running.return_value = {
            "running": True,
            "port": 18765,
            "url": "http://127.0.0.1:18765/client.php",
        }
        fake_tr.get_stats.return_value = {
            "ok": True,
            "total_requests": 2,
            "cache_hits": 1,
            "avg_ms": 12.5,
            "recent": [
                {"src": "newest src", "dst": "newest dst", "provider": "google_gtx"},
                {"src": "older src", "dst": "older dst", "provider": "cache"},
            ],
        }
        fake_tr.build_translator_diag_lua.return_value = "return '{}'"
        fake_tr.build_translator_lua_hook.return_value = "return 'TRANSLATOR_HOOK_ENABLED:18765:en'"

        backend._translator_mod_cache = fake_tr

        # 1. Offline / 0 clients fallback
        with mock.patch.object(hub_mod, "client_discovery", None), \
             mock.patch.object(backend, "_discover_running_clients", return_value=[]):
            st_empty = backend.get_translator_status()
            self.assertTrue(st_empty["ok"])
            self.assertEqual(st_empty["attached_pids"], [])
            self.assertEqual(st_empty["hooked_pids"], [])
            self.assertIsNone(st_empty["screen_translation"])
            self.assertEqual(st_empty["last_preview"]["dst"], "newest dst")
            self.assertTrue(st_empty["has_deepl_key"])
            self.assertTrue(st_empty["has_gemini_key"])
            self.assertNotIn(deepl_secret, json.dumps(st_empty))
            self.assertNotIn(gemini_secret, json.dumps(st_empty))

        # 2. Live clients with mock frida_eval_lua WITHOUT retries kwarg (tests TypeError fallback)
        fake_cd = mock.MagicMock()
        fake_cd._xlua_loaded.side_effect = lambda pid: pid in (101, 102)

        def simple_frida_eval(pid, code, timeout=4.0):
            if "TRANSLATOR_HOOK_ENABLED" in code:
                return (True, "TRANSLATOR_HOOK_ENABLED:18765:en")
            if pid == 101:
                return (True, json.dumps({"hooked": True, "hasCm": True, "hasTm": True, "screenTranslation": True, "autoTraActive": True}))
            return (True, json.dumps({"hooked": False, "hasCm": True, "hasTm": False, "screenTranslation": False, "autoTraActive": False}))

        fake_cd.frida_eval_lua = simple_frida_eval
        with mock.patch.object(hub_mod, "client_discovery", fake_cd), \
             mock.patch.object(backend, "_discover_running_clients", return_value=[{"pid": 101}, {"pid": 102}, {"pid": 103}]):
            st_live = backend.get_translator_status()
            self.assertEqual(st_live["attached_pids"], [101, 102])
            self.assertEqual(st_live["hooked_pids"], [101])
            self.assertTrue(st_live["screen_translation"])
            self.assertTrue(st_live["auto_tra_active"])

            logged_msgs: list[str] = []
            with mock.patch.object(backend, "log", side_effect=lambda msg, lvl="info": logged_msgs.append(str(msg))):
                rehook_res = backend.rehook_translator()
            self.assertTrue(rehook_res["ok"])
            self.assertTrue(rehook_res["rehooked"])
            self.assertEqual(rehook_res["hooked_pids"], [101, 102])
            self.assertEqual(rehook_res["rehook_errors"], [])
            combined_out = json.dumps(rehook_res) + "\n".join(logged_msgs)
            self.assertNotIn(deepl_secret, combined_out)
            self.assertNotIn(gemini_secret, combined_out)

    def test_index_html_live_translator_dom_and_xss_contracts(self) -> None:
        html = (PROJECT_ROOT / "launcher" / "web" / "index.html").read_text(encoding="utf-8")

        # Duplicate ID check
        all_ids = re.findall(r'\bid\s*=\s*"([^"]+)"', html)
        self.assertEqual(len(all_ids), len(set(all_ids)), "Duplicate HTML IDs found in index.html")

        # Zero translator quick-toggle pill in <header class="hero-header">
        m_hdr = re.search(r'<header[^>]*class="hero-header"[^>]*>.*?</header>', html, flags=re.S)
        self.assertIsNotNone(m_hdr)
        hdr_html = m_hdr.group(0).lower()
        for forbidden in ("translator", "auto-tr", "rehook", "tr-status", "tr-pid"):
            self.assertNotIn(forbidden, hdr_html)

        # Required elements strictly inside #card-live-translator
        m_card = re.search(r'<div[^>]*id="card-live-translator".*?<div class="card-grid-2">', html, flags=re.S)
        self.assertIsNotNone(m_card)
        card_html = m_card.group(0)
        for req_id in ("tr-status-pill", "tr-pid-badge", "tr-pid-text", "tr-switch-badge", "tr-rehook-btn", "tr-last-preview"):
            self.assertIn(f'id="{req_id}"', card_html)
        self.assertIn('onclick="rehookTranslator()"', card_html)

        # JS recent[0] fix, esc() XSS escaping, and rehook_translator RPC call
        self.assertNotIn("recentArr[recentArr.length - 1]", html)
        self.assertIn("recentArr[0]", html)
        self.assertIn('callApi("rehook_translator")', html)
        m_render = re.search(r"function _renderTranslatorStatus\(st\).*?async function rehookTranslator", html, flags=re.S)
        self.assertIsNotNone(m_render)
        self.assertIn("esc(", m_render.group(0))

    def test_zero_em_dashes_and_zero_prohibited_terms(self) -> None:
        term1_re = re.compile(r"\bcom" + r"mander\b", re.I)
        term2_re = re.compile(r"cour" + r"age\s+bad" + r"ges?", re.I)
        em_dash = "\u2014"
        en_dash = "\u2013"
        mdash_entity = "&" + "mdash;"
        owned = [
            PROJECT_ROOT / "tools" / "live translator server.py",
            PROJECT_ROOT / "tests" / "testLiveTranslator.py",
            PROJECT_ROOT / "daemon" / "lastz auto engine daemon.py",
        ]
        for path in owned:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(em_dash, text, f"Em dash found in {path.name}")
            self.assertNotIn(en_dash, text, f"En dash found in {path.name}")
            self.assertNotIn(mdash_entity, text, f"HTML mdash entity found in {path.name}")
            self.assertIsNone(term1_re.search(text), f"Forbidden term 1 in {path.name}")
            self.assertIsNone(term2_re.search(text), f"Forbidden term 2 in {path.name}")


if __name__ == "__main__":
    unittest.main()
