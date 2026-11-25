"""Unit and integration tests for the Last Z always-on Live Translator bridge.

All unit & localhost HTTP server tests run 100% offline using mocked HTTP
providers and isolated temporary SQLite caches on ephemeral ports (port=0).
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
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


class TestDaemonWiringAndGuardrails(unittest.TestCase):
    """Verify daemon translator integration uses frida_eval_lua and obeys repo guardrails."""

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

    def test_zero_em_dashes_and_zero_prohibited_terms(self) -> None:
        term1_re = re.compile(r"\bcom" + r"mander\b", re.I)
        term2_re = re.compile(r"cour" + r"age\s+bad" + r"ges?", re.I)
        em_dash = "\u2014"
        mdash_entity = "&" + "mdash;"
        owned = [
            PROJECT_ROOT / "tools" / "live translator server.py",
            PROJECT_ROOT / "tests" / "testLiveTranslator.py",
            PROJECT_ROOT / "daemon" / "lastz auto engine daemon.py",
        ]
        for path in owned:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(em_dash, text, f"Em dash found in {path.name}")
            self.assertNotIn(mdash_entity, text, f"HTML mdash entity found in {path.name}")
            self.assertIsNone(term1_re.search(text), f"Forbidden term 1 in {path.name}")
            self.assertIsNone(term2_re.search(text), f"Forbidden term 2 in {path.name}")


if __name__ == "__main__":
    unittest.main()
