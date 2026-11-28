"""Offline verification suite for `tools/account launcher vault.py`.

Covers:
1. Email validation, duplicate rejection, and sequential `Hz01Z`/`Hz02Z` allocation.
2. First-time email verification code tracking (`needs_email_code` vs `verified`) with mock `reg_reader`
   and strict guarantee that raw `SeToken` bytes are never stored, returned, or logged.
3. Account update, unbind, verification reset, and discovered-profile sync preserving user edits.
4. Pure Vanilla (zero-attach) borderless launch vs Enhanced windowed/fullscreen launch using
   isolated `HEINZ_DATA_DIR`, mock `reg_reader`, and mock `popen_fn` (never touches real HKCU or
   spawns real game executables).
5. Background HeinZ daemon/translator termination guard and static hygiene guardrails.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import http.server
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT_SCRIPT_PATH = PROJECT_ROOT / "tools" / "account launcher vault.py"


def _load_vault_module(mod_name: str = "test_account_launcher_vault_mod"):
    spec = importlib.util.spec_from_file_location(mod_name, str(VAULT_SCRIPT_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {VAULT_SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeProcess:
    """Minimal mock process object for `stop_background_heinz_daemons` tests."""

    def __init__(self, pid: int, name: str, cmdline: list[str]) -> None:
        self.info = {"pid": pid, "name": name, "cmdline": cmdline}
        self.terminated = False
        self.killed = False
        self.waited = False

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        self.waited = True
        return 0


class _FakePopenResult:
    def __init__(self, pid: int = 42424) -> None:
        self.pid = pid


class TestAccountLauncherVault(unittest.TestCase):
    """Comprehensive hermetic unit tests for HeinZ V2 Account Launcher Vault."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name) / "heinz data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._orig_env = os.environ.get("HEINZ_DATA_DIR")
        os.environ["HEINZ_DATA_DIR"] = str(self.data_dir)
        self.vault_mod = _load_vault_module()
        # Prevent accidental loading of real sibling modules during hermetic tests.
        self.vault_mod._LOADED_MODULES.clear()

    def tearDown(self) -> None:
        if self._orig_env is None:
            os.environ.pop("HEINZ_DATA_DIR", None)
        else:
            os.environ["HEINZ_DATA_DIR"] = self._orig_env
        self.tmp.cleanup()

    def _make_fake_engine_manager(self, slots_root: Path):
        fake_gem = types.ModuleType("fake_game_engine_manager")

        def ensure_account_slot(
            unity_profile: str,
            exe_name: str,
            engine_root: Path | None = None,
            source_game_dir: str | None = None,
        ) -> dict:
            base = Path(engine_root) if engine_root is not None else slots_root
            game_dir = base / "slots" / unity_profile / "Game"
            game_dir.mkdir(parents=True, exist_ok=True)
            exe_file = game_dir / exe_name
            exe_file.write_bytes(b"MZ_FAKE_UNITY_EXE")
            return {
                "ok": True,
                "slot_ready": True,
                "game_dir": str(game_dir),
                "exe_path": str(exe_file),
                "message": f"Prepared isolated slot {unity_profile}",
            }

        fake_gem.ensure_account_slot = ensure_account_slot  # type: ignore[attr-defined]
        return fake_gem

    def test_resolve_vault_path_respects_heinz_data_dir(self) -> None:
        expected = self.data_dir / "json cache" / "bound accounts.json"
        self.assertEqual(self.vault_mod.resolve_vault_path(), expected)

    def test_validate_email_valid_and_invalid(self) -> None:
        ok, norm = self.vault_mod.validate_email("  Alpha.Player+01@Sub.Example.COM  ")
        self.assertTrue(ok)
        self.assertEqual(norm, "alpha.player+01@sub.example.com")

        invalid_samples = [
            "",
            "   ",
            "missing-at-symbol.com",
            "user@",
            "@example.com",
            "user@localhost",
            "user@domain.c",
            "two@@example.com",
            ".leading@example.com",
            "trailing.@example.com",
            "double..dot@example.com",
            "user@bad..domain.com",
            "has space@example.com",
        ]
        for bad in invalid_samples:
            is_ok, err = self.vault_mod.validate_email(bad)
            self.assertFalse(is_ok, f"Expected '{bad}' to be rejected")
            self.assertTrue(bool(err))

    def test_allocate_next_profile_skips_reserved_and_existing(self) -> None:
        prof1, exe1 = self.vault_mod.allocate_next_profile([])
        self.assertEqual((prof1, exe1), ("Hz01Z", "Hz01Game.exe"))
        self.assertEqual(len(prof1), 5)

        existing = [
            {"id": "lastz", "unity_profile": "LastZ", "exe_name": "Survival.exe"},
            {"id": "farmz", "unity_profile": "FarmZ", "exe_name": "FarmGame.exe"},
            {"id": "alt3z", "unity_profile": "Alt3Z", "exe_name": "Alt3Game.exe"},
            {"id": "hz01z", "unity_profile": "Hz01Z", "exe_name": "Hz01Game.exe"},
        ]
        prof2, exe2 = self.vault_mod.allocate_next_profile(existing)
        self.assertEqual((prof2, exe2), ("Hz02Z", "Hz02Game.exe"))
        self.assertEqual(len(prof2), 5)

        existing.append({"id": "hz02z", "unity_profile": "Hz02Z", "exe_name": "Hz02Game.exe"})
        prof3, exe3 = self.vault_mod.allocate_next_profile(existing)
        self.assertEqual((prof3, exe3), ("Hz03Z", "Hz03Game.exe"))

    def test_bind_new_account_allocates_rejects_duplicates_and_tracks_email_code(self) -> None:
        empty_reg = lambda _profile: {}
        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=None):
            res1 = self.vault_mod.bind_new_account(
                "Main.Player@Example.COM",
                label="",
                window_style="borderless",
                skip_registry_clear=True,
                reg_reader=empty_reg,
            )
            self.assertTrue(res1["ok"])
            self.assertTrue(res1["requires_email_code"])
            acc1 = res1["account"]
            self.assertEqual(acc1["id"], "hz01z")
            self.assertEqual(acc1["unity_profile"], "Hz01Z")
            self.assertEqual(acc1["exe_name"], "Hz01Game.exe")
            self.assertEqual(acc1["email"], "main.player@example.com")
            self.assertEqual(acc1["label"], "main.player")
            self.assertEqual(acc1["window_style"], "borderless")
            self.assertEqual(acc1["source"], "bound")
            self.assertFalse(acc1["verified"])
            self.assertTrue(acc1["needs_email_code"])
            self.assertFalse(acc1["slot_ready"])
            self.assertIn("Engine", res1["message"])

            # Case-insensitive duplicate rejection.
            dup = self.vault_mod.bind_new_account(
                "  main.player@example.com ",
                skip_registry_clear=True,
                reg_reader=empty_reg,
            )
            self.assertFalse(dup["ok"])
            self.assertIn("already bound", dup["error"].lower())

            # Second distinct email gets Hz02Z / Hz02Game.exe.
            res2 = self.vault_mod.bind_new_account(
                "farm.alt@example.com",
                label="Farm Squad",
                window_style="windowed",
                skip_registry_clear=True,
                reg_reader=empty_reg,
            )
            self.assertTrue(res2["ok"])
            self.assertEqual(res2["account"]["unity_profile"], "Hz02Z")
            self.assertEqual(res2["account"]["exe_name"], "Hz02Game.exe")
            self.assertEqual(res2["account"]["label"], "Farm Squad")
            self.assertEqual(res2["account"]["window_style"], "windowed")

        # Verify atomic persistence to isolated vault file.
        self.assertTrue(self.vault_mod.resolve_vault_path().is_file())
        listed = self.vault_mod.list_bound_accounts(sync_discovered=False, reg_reader=empty_reg)
        self.assertEqual([a["unity_profile"] for a in listed], ["Hz01Z", "Hz02Z"])

    def test_bind_calls_clear_profile_session_token_by_default(self) -> None:
        with (
            mock.patch.object(
                self.vault_mod,
                "clear_profile_session_token",
                return_value={"ok": True, "deleted_count": 1},
            ) as mock_clear,
            mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=None),
        ):
            res = self.vault_mod.bind_new_account(
                "fresh.user@example.com",
                skip_registry_clear=False,
                reg_reader=lambda _p: {},
            )
            self.assertTrue(res["ok"])
            mock_clear.assert_called_once_with("Hz01Z")

    def test_inspect_profile_session_verified_and_zero_raw_token_leak(self) -> None:
        # 1. Pre-parsed mock dict with has_token=True & uid="123456".
        sess = self.vault_mod.inspect_profile_session(
            "Hz01Z",
            reg_reader=lambda _p: {"has_token": True, "uid": "123456", "server_id": 777},
        )
        self.assertEqual(sess["unity_profile"], "Hz01Z")
        self.assertTrue(sess["has_token"])
        self.assertEqual(sess["uid"], "123456")
        self.assertEqual(sess["server_id"], 777)
        self.assertTrue(sess["verified"])
        self.assertFalse(sess["needs_email_code"])

        # 2. Raw registry-style mock dict containing sensitive SeToken bytes.
        sentinel_secret = "RAW_SETOKEN_SECRET_DO_NOT_LOG_991188"
        raw_reader = lambda _p: {
            "SeToken_h12345": sentinel_secret.encode("utf-8"),
            "Setting.GAME_UID_h222": b"123456\x00",
            "Setting.SERVER_ID_h333": b"409\x00",
        }
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            sess_raw = self.vault_mod.inspect_profile_session("Hz01Z", reg_reader=raw_reader)
            with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=None):
                self.vault_mod.bind_new_account(
                    "verified.user@example.com",
                    skip_registry_clear=True,
                    reg_reader=raw_reader,
                )
            listed = self.vault_mod.list_bound_accounts(sync_discovered=False, reg_reader=raw_reader)

        self.assertTrue(sess_raw["verified"])
        self.assertFalse(sess_raw["needs_email_code"])
        self.assertEqual(sess_raw["uid"], "123456")
        self.assertEqual(sess_raw["server_id"], 409)
        self.assertTrue(listed[0]["verified"])
        self.assertFalse(listed[0]["needs_email_code"])

        # Raw SeToken bytes must NEVER appear in returned data, saved JSON, or stdout/stderr.
        vault_text = self.vault_mod.resolve_vault_path().read_text(encoding="utf-8")
        combined_surface = (
            json.dumps(sess_raw)
            + json.dumps(listed)
            + vault_text
            + stdout_buf.getvalue()
            + stderr_buf.getvalue()
        )
        self.assertNotIn(sentinel_secret, combined_surface)

        # 3. Missing UID or empty SeToken remains unverified.
        sess_empty = self.vault_mod.inspect_profile_session(
            "Hz01Z",
            reg_reader=lambda _p: {"SeToken_h1": b"", "Setting.GAME_UID_h2": b"123456\x00"},
        )
        self.assertFalse(sess_empty["has_token"])
        self.assertFalse(sess_empty["verified"])
        self.assertTrue(sess_empty["needs_email_code"])

    def test_clear_profile_session_token_deletes_only_session_values_via_mock_winreg(self) -> None:
        # Reject path traversal or empty profile names before touching winreg.
        bad_res = self.vault_mod.clear_profile_session_token("..\\LastZ")
        self.assertFalse(bad_res["ok"])

        reg_store = {
            "SeToken_h100": b"SECRET_BYTES",
            "Setting.GAME_UID_h200": b"123456\x00",
            "GAME_ACCOUNT_h300": b"user@example.com\x00",
            "Screenmanager Resolution Width_h400": 1920,
        }
        opened_paths: list[str] = []

        class _FakeKey:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        fake_winreg = types.SimpleNamespace(
            HKEY_CURRENT_USER="HKCU",
            KEY_READ=1,
            KEY_SET_VALUE=2,
            OpenKey=lambda hive, path, _res=0, _acc=0: (opened_paths.append(path), _FakeKey())[1],
            QueryInfoKey=lambda _k: (0, len(reg_store), 0),
            EnumValue=lambda _k, idx: (list(reg_store.keys())[idx], list(reg_store.values())[idx], 3),
            DeleteValue=lambda _k, name: reg_store.pop(name),
        )

        with mock.patch.object(self.vault_mod, "winreg", fake_winreg):
            res = self.vault_mod.clear_profile_session_token("Hz01Z")

        self.assertTrue(res["ok"])
        self.assertEqual(opened_paths, [r"Software\ReadyGo\Hz01Z"])
        self.assertEqual(res["deleted_count"], 3)
        self.assertIn("Screenmanager Resolution Width_h400", reg_store)
        self.assertEqual(list(reg_store.keys()), ["Screenmanager Resolution Width_h400"])

    def test_update_unbind_and_reset_verification(self) -> None:
        empty_reg = lambda _p: {}
        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=None):
            b1 = self.vault_mod.bind_new_account(
                "one@example.com", label="First", skip_registry_clear=True, reg_reader=empty_reg
            )
            b2 = self.vault_mod.bind_new_account(
                "two@example.com", label="Second", skip_registry_clear=True, reg_reader=empty_reg
            )
        id1 = b1["account"]["id"]
        id2 = b2["account"]["id"]

        # Update email, label, and window_style cleanly.
        upd = self.vault_mod.update_account(
            id1,
            email="One.Updated@Example.com",
            label="Main Account",
            window_style="fullscreen",
            reg_reader=empty_reg,
        )
        self.assertTrue(upd["ok"])
        self.assertEqual(upd["account"]["email"], "one.updated@example.com")
        self.assertEqual(upd["account"]["label"], "Main Account")
        self.assertEqual(upd["account"]["window_style"], "fullscreen")

        # Updating to another account's email is rejected.
        dup_upd = self.vault_mod.update_account(id1, email="two@example.com", reg_reader=empty_reg)
        self.assertFalse(dup_upd["ok"])

        # Reset verification calls clear_profile_session_token for target profile.
        with mock.patch.object(
            self.vault_mod,
            "clear_profile_session_token",
            return_value={"ok": True, "deleted_count": 2},
        ) as mock_clear:
            rst = self.vault_mod.reset_account_verification(id1)
            self.assertTrue(rst["ok"])
            self.assertTrue(rst["requires_email_code"])
            mock_clear.assert_called_once_with("Hz01Z")

        # Unbind with clear_session=True removes entry and clears isolated profile token.
        with mock.patch.object(
            self.vault_mod,
            "clear_profile_session_token",
            return_value={"ok": True, "deleted_count": 1},
        ) as mock_clear:
            rem = self.vault_mod.unbind_account(id2, clear_session=True)
            self.assertTrue(rem["ok"])
            self.assertEqual(rem["removed_id"], id2)
            self.assertTrue(rem["session_cleared"])
            mock_clear.assert_called_once_with("Hz02Z")

        remaining = self.vault_mod.list_bound_accounts(sync_discovered=False, reg_reader=empty_reg)
        self.assertEqual([a["id"] for a in remaining], [id1])

    def test_sync_discovered_accounts_preserves_user_edits(self) -> None:
        fake_cd = types.ModuleType("fake_client_discovery")
        fake_cd.discover_clients = lambda save_cache=False: [  # type: ignore[attr-defined]
            {
                "id": "lastz",
                "label": "Main",
                "unity_profile": "LastZ",
                "exe_name": "Survival.exe",
                "game_dir": str(self.data_dir / "main_game"),
                "exe_path": str(self.data_dir / "main_game" / "Survival.exe"),
            },
            {
                "id": "farmz",
                "label": "Farm",
                "unity_profile": "FarmZ",
                "exe_name": "FarmGame.exe",
                "game_dir": str(self.data_dir / "farm_game"),
                "exe_path": str(self.data_dir / "farm_game" / "FarmGame.exe"),
            },
        ]

        with mock.patch.object(self.vault_mod, "_load_client_discovery", return_value=fake_cd):
            first = self.vault_mod.sync_discovered_accounts(save=True)
            self.assertEqual(len(first), 2)

            upd = self.vault_mod.update_account(
                "lastz",
                email="owner.main@example.com",
                label="My Custom Main",
                window_style="windowed",
                reg_reader=lambda _p: {},
            )
            self.assertTrue(upd["ok"])

            # Re-sync must preserve user email, label, and window_style.
            second = self.vault_mod.sync_discovered_accounts(save=True)
            main_entry = next(a for a in second if a["unity_profile"] == "LastZ")
            self.assertEqual(main_entry["email"], "owner.main@example.com")
            self.assertEqual(main_entry["label"], "My Custom Main")
            self.assertEqual(main_entry["window_style"], "windowed")

    def test_build_launch_args_for_all_window_styles(self) -> None:
        exe = Path(r"C:\MockGame\Hz01Game.exe")

        with mock.patch.object(self.vault_mod, "_detect_primary_monitor_size", return_value=(1920, 1080)):
            b_args = self.vault_mod.build_launch_args(exe, window_style="borderless")
        self.assertEqual(b_args[0], str(exe))
        self.assertTrue(b_args[1].startswith("--from-launcher="))
        decoded = base64.b64decode(b_args[1].split("=", 1)[1]).decode("utf-8")
        ts_part, suffix = decoded.split("|", 1)
        self.assertTrue(ts_part.isdigit())
        self.assertEqual(suffix, "LZ")
        self.assertEqual(
            b_args[2:],
            ["-popupwindow", "-screen-fullscreen", "0", "-screen-width", "1920", "-screen-height", "1080"],
        )

        w_args = self.vault_mod.build_launch_args(exe, window_style="windowed")
        self.assertNotIn("-popupwindow", w_args)
        self.assertEqual(
            w_args[2:],
            ["-screen-width", "1280", "-screen-height", "720", "-screen-fullscreen", "0"],
        )

        f_args = self.vault_mod.build_launch_args(exe, window_style="fullscreen")
        self.assertEqual(f_args[2:], ["-screen-fullscreen", "1"])

    def test_launch_vanilla_borderless_stops_daemons_and_zero_frida(self) -> None:
        engine_root = Path(self.tmp.name) / "engine"
        fake_gem = self._make_fake_engine_manager(engine_root)
        unverified_reg = lambda _p: {}

        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=fake_gem):
            bound = self.vault_mod.bind_new_account(
                "vanilla.player@example.com",
                label="Vanilla Main",
                window_style="borderless",
                engine_root=engine_root,
                skip_registry_clear=True,
                reg_reader=unverified_reg,
            )
        self.assertTrue(bound["ok"])
        self.assertTrue(bound["account"]["slot_ready"])
        acc_id = bound["account"]["id"]

        captured: dict = {}

        def fake_popen(args, **kwargs):
            captured["args"] = list(args)
            captured["kwargs"] = dict(kwargs)
            return _FakePopenResult(pid=55123)

        with (
            mock.patch.object(
                self.vault_mod,
                "stop_background_heinz_daemons",
                return_value={"ok": True, "stopped_count": 2, "stopped": [], "errors": []},
            ) as mock_stop,
            mock.patch.object(self.vault_mod, "_detect_primary_monitor_size", return_value=(2560, 1440)),
        ):
            res = self.vault_mod.launch_bound_account(
                acc_id,
                mode="vanilla",
                window_style="borderless",
                engine_root=engine_root,
                dry_run=False,
                popen_fn=fake_popen,
                reg_reader=unverified_reg,
            )

        self.assertTrue(res["ok"])
        self.assertEqual(res["mode"], "vanilla")
        self.assertTrue(res["should_exit_heinz"])
        self.assertEqual(res["pid"], 55123)
        self.assertEqual(res["daemons_stopped"], 2)
        self.assertTrue(res["needs_email_code"])
        self.assertEqual(res["window_style"], "borderless")
        mock_stop.assert_called_once()

        self.assertIn("-popupwindow", res["args"])
        self.assertTrue(any(arg.startswith("--from-launcher=") for arg in res["args"]))
        self.assertIn("2560", res["args"])
        self.assertIn("1440", res["args"])

        # Verify detached process flags and compatibility layer env var.
        expected_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200) | getattr(
            subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000
        )
        self.assertEqual(captured["kwargs"]["creationflags"], expected_flags)
        self.assertEqual(
            captured["kwargs"]["env"]["__COMPAT_LAYER"],
            "DISABLEDXMAXIMIZEDWINDOWEDMODE",
        )

        # Verify vault persisted last_mode and last_launched_at, and zero Frida dependency loaded.
        stored = self.vault_mod.load_vault()["accounts"][0]
        self.assertEqual(stored["last_mode"], "vanilla")
        self.assertGreater(stored["last_launched_at"], 0)
        self.assertNotIn("heinz_vault_sync_farm_clients", self.vault_mod._LOADED_MODULES)
        self.assertNotIn("heinz_vault_client_discovery", self.vault_mod._LOADED_MODULES)

    def test_launch_enhanced_windowed_does_not_stop_daemons_or_exit_heinz(self) -> None:
        engine_root = Path(self.tmp.name) / "engine"
        fake_gem = self._make_fake_engine_manager(engine_root)
        verified_reg = lambda _p: {"has_token": True, "uid": "987654", "server_id": 102}

        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=fake_gem):
            bound = self.vault_mod.bind_new_account(
                "enhanced.player@example.com",
                label="Enhanced Farm",
                window_style="borderless",
                engine_root=engine_root,
                skip_registry_clear=True,
                reg_reader=verified_reg,
            )
        acc_id = bound["account"]["id"]

        captured: dict = {}

        def fake_popen(args, **kwargs):
            captured["args"] = list(args)
            captured["kwargs"] = dict(kwargs)
            return _FakePopenResult(pid=66234)

        with mock.patch.object(
            self.vault_mod,
            "stop_background_heinz_daemons",
            return_value={"ok": True, "stopped_count": 99, "stopped": [], "errors": []},
        ) as mock_stop:
            res = self.vault_mod.launch_bound_account(
                acc_id,
                mode="enhanced",
                window_style="windowed",
                engine_root=engine_root,
                dry_run=False,
                popen_fn=fake_popen,
                reg_reader=verified_reg,
            )

        self.assertTrue(res["ok"])
        self.assertEqual(res["mode"], "enhanced")
        self.assertFalse(res["should_exit_heinz"])
        self.assertFalse(res["needs_email_code"])
        self.assertEqual(res["daemons_stopped"], 0)
        self.assertEqual(res["pid"], 66234)
        self.assertEqual(res["window_style"], "windowed")
        mock_stop.assert_not_called()

        self.assertNotIn("-popupwindow", res["args"])
        idx_w = res["args"].index("-screen-width")
        self.assertEqual(res["args"][idx_w + 1], "1280")
        idx_h = res["args"].index("-screen-height")
        self.assertEqual(res["args"][idx_h + 1], "720")

    def test_launch_dry_run_makes_zero_process_or_vault_mutations(self) -> None:
        engine_root = Path(self.tmp.name) / "engine"
        fake_gem = self._make_fake_engine_manager(engine_root)
        empty_reg = lambda _p: {}

        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=fake_gem):
            bound = self.vault_mod.bind_new_account(
                "dryrun@example.com",
                engine_root=engine_root,
                skip_registry_clear=True,
                reg_reader=empty_reg,
            )
        acc_id = bound["account"]["id"]
        popen_mock = mock.Mock()

        with mock.patch.object(self.vault_mod, "stop_background_heinz_daemons") as mock_stop:
            res = self.vault_mod.launch_bound_account(
                acc_id,
                mode="vanilla",
                window_style="borderless",
                dry_run=True,
                popen_fn=popen_mock,
                reg_reader=empty_reg,
            )

        self.assertTrue(res["ok"])
        self.assertTrue(res["should_exit_heinz"])
        self.assertEqual(res["pid"], 0)
        popen_mock.assert_not_called()
        mock_stop.assert_not_called()
        stored = self.vault_mod.load_vault()["accounts"][0]
        self.assertEqual(stored["last_launched_at"], 0)
        self.assertEqual(stored["last_mode"], "")

    def test_stop_background_heinz_daemons_targets_only_daemon_and_translator(self) -> None:
        cur_pid = os.getpid()
        p_self = _FakeProcess(cur_pid, "python.exe", ["python.exe", "daemon/lastz auto engine daemon.py"])
        p_surv = _FakeProcess(1001, "Survival.exe", [r"C:\Game\Survival.exe"])
        p_hz01 = _FakeProcess(1002, "Hz01Game.exe", [r"C:\Game\Hz01Game.exe"])
        p_daemon = _FakeProcess(2001, "pythonw.exe", ["pythonw.exe", r"G:\repo\daemon\lastz auto engine daemon.py"])
        p_trans = _FakeProcess(2002, "python.exe", ["python.exe", r"G:\repo\tools\live translator server.py"])
        p_other = _FakeProcess(3001, "python.exe", ["python.exe", "unrelated_script.py"])

        with mock.patch.object(
            self.vault_mod.psutil,
            "process_iter",
            return_value=[p_self, p_surv, p_hz01, p_daemon, p_trans, p_other],
        ):
            res = self.vault_mod.stop_background_heinz_daemons()

        self.assertTrue(res["ok"])
        self.assertEqual(res["stopped_count"], 2)
        self.assertTrue(p_daemon.terminated)
        self.assertTrue(p_trans.terminated)
        self.assertFalse(p_self.terminated)
        self.assertFalse(p_surv.terminated)
        self.assertFalse(p_hz01.terminated)
        self.assertFalse(p_other.terminated)

    def test_static_hygiene_guardrails(self) -> None:
        vault_src = VAULT_SCRIPT_PATH.read_text(encoding="utf-8")
        test_src = Path(__file__).read_text(encoding="utf-8")

        # Zero underscores in owned filenames.
        self.assertNotIn("_", VAULT_SCRIPT_PATH.name)
        self.assertNotIn("_", Path(__file__).name)

        # Zero em dashes or HTML mdash entities anywhere in either file.
        em_dash = chr(0x2014)
        html_mdash = "&md" + "ash;"
        for label, src in (("account launcher vault.py", vault_src), ("testAccountLauncherVault.py", test_src)):
            self.assertNotIn(em_dash, src, f"Em dash found in {label}")
            self.assertNotIn(html_mdash, src.lower(), f"HTML mdash entity found in {label}")

        # Zero forbidden terms in either file.
        forbidden_a = ("Comm" + "ander").lower()
        forbidden_b = ("Cour" + "age Badges").lower()
        for label, src in (("account launcher vault.py", vault_src), ("testAccountLauncherVault.py", test_src)):
            low = src.lower()
            self.assertNotIn(forbidden_a, low, f"Forbidden term found in {label}")
            self.assertNotIn(forbidden_b, low, f"Forbidden term found in {label}")

        # Vault module must never import frida directly or print/decode SeToken values.
        self.assertNotIn("import frida", vault_src)
        self.assertNotIn("from frida", vault_src)
        self.assertNotIn("frida.attach", vault_src)

    def test_real_game_engine_manager_interop_graceful_fallback_and_slot_ready(self) -> None:
        """Verify seamless interop with real `game engine manager.py` when empty vs populated."""
        gem_path = PROJECT_ROOT / "tools" / "game engine manager.py"
        if not gem_path.is_file():
            self.skipTest("game engine manager.py not present")

        empty_engine_root = Path(self.tmp.name) / "empty engine"
        empty_reg = lambda _p: {}

        # 1. Empty engine root falls back gracefully with slot_ready=False and Engine guidance.
        res_empty = self.vault_mod.bind_new_account(
            "noengine@example.com",
            engine_root=empty_engine_root,
            skip_registry_clear=True,
            reg_reader=empty_reg,
        )
        self.assertTrue(res_empty["ok"])
        self.assertFalse(res_empty["account"]["slot_ready"])
        self.assertTrue(res_empty["requires_email_code"])
        self.assertIn("Import or Download", res_empty["message"])

        # 2. Populated synthetic master engine provisions isolated Hz02Z slot with slot_ready=True.
        ready_engine_root = Path(self.tmp.name) / "ready engine"
        master_game = ready_engine_root / "Game"
        master_sd = master_game / "Survival_Data"
        master_sd.mkdir(parents=True, exist_ok=True)
        (master_game / "Survival.exe").write_bytes(b"MZ_SYNTHETIC_SURVIVAL")
        (master_game / "GameAssembly.dll").write_bytes(b"MZ_SYNTHETIC_GA")
        (master_sd / "app.info").write_text("ReadyGo\nLastZ", encoding="utf-8")
        (master_sd / "globalgamemanagers").write_bytes(
            b"\x00" * 32 + b"ReadyGo\x00\x05\x00\x00\x00LastZ" + b"\x00" * 64
        )

        res_ready = self.vault_mod.bind_new_account(
            "with.engine@example.com",
            label="Engine Ready",
            engine_root=ready_engine_root,
            skip_registry_clear=True,
            reg_reader=empty_reg,
        )
        self.assertTrue(res_ready["ok"])
        self.assertTrue(res_ready["account"]["slot_ready"])
        self.assertEqual(res_ready["account"]["unity_profile"], "Hz02Z")
        self.assertTrue(Path(res_ready["account"]["exe_path"]).is_file())

    def test_v2_delayed_boot_gate_zero_attach_and_dom_contracts(self) -> None:
        """Verify HubBackend(defer_enhanced=True) boots with zero hooks/monitors and V2 Gate DOM exists."""
        hub_path = PROJECT_ROOT / "launcher" / "heinzhubweb.py"
        html_path = PROJECT_ROOT / "launcher" / "web" / "index.html"
        spec = importlib.util.spec_from_file_location("test_v2_gate_hub_mod", str(hub_path))
        assert spec is not None and spec.loader is not None
        hub_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hub_mod)

        with (
            mock.patch.object(hub_mod.HubBackend, "_load_cached_state"),
            mock.patch.object(hub_mod.HubBackend, "_load_always_on_daemon_config"),
            mock.patch.object(hub_mod.HubBackend, "_start_always_on_daemon") as mock_start_ao,
            mock.patch.object(hub_mod.HubBackend, "log"),
        ):
            backend = hub_mod.HubBackend(defer_enhanced=True)
            self.assertFalse(backend._monitors_started)
            self.assertFalse(backend._enhanced_active)
            mock_start_ao.assert_not_called()

            boot = backend.get_launcher_boot_state(check_remote=False)
            self.assertTrue(boot["ok"])
            self.assertFalse(boot["enhanced_active"])
            self.assertIsInstance(boot["engine_status"], dict)
            self.assertIsInstance(boot["accounts"], list)
            self.assertIn("auth_state", boot)
            self.assertFalse(boot["auth_state"]["signed_in"])

            # Verify Login To Account RPC rejects bare password stub without OTP/device code and never writes secrets
            secret_pw = "SUPER_SECRET_NEVER_PERSIST_9911"
            login_res = backend.authenticate_heinz_account("player@example.com", secret_pw, remember=True, skip=False)
            self.assertFalse(login_res["ok"])
            self.assertFalse(login_res["signed_in"])
            self.assertEqual(login_res["code"], "AUTH_METHOD_REQUIRED")
            prefs_file = Path(backend._heinz_login_prefs_path())
            if prefs_file.is_file():
                self.assertNotIn(secret_pw, prefs_file.read_text(encoding="utf-8"))
            so_res = backend.sign_out_heinz_account()
            self.assertTrue(so_res["ok"])
            self.assertFalse(so_res["signed_in"])
            guest_res = backend.authenticate_heinz_account("", "", remember=False, skip=True)
            self.assertTrue(guest_res["ok"])
            self.assertEqual(guest_res["mode"], "guest")

            # Verify standalone window size presets (Login -> Unified Launcher -> Hub)
            r_login = backend.set_launcher_window_mode("login_step")
            self.assertTrue(r_login["ok"])
            self.assertEqual((r_login["width"], r_login["height"]), (440, 450))
            r_launch = backend.set_launcher_window_mode("launcher_step")
            self.assertEqual((r_launch["width"], r_launch["height"]), (540, 540))
            r_hub = backend.set_launcher_window_mode("hub")
            self.assertEqual((r_hub["width"], r_hub["height"]), (1240, 840))

        html = html_path.read_text(encoding="utf-8")
        self.assertIn('body class="launcher-standalone"', html)
        self.assertIn("body.launcher-standalone .app-shell", html)
        for dom_id in (
            "launcher-gate-overlay",
            "lg-step-login",
            "lg-auth-tab-pair",
            "lg-auth-tab-otp",
            "lg-btn-device-pair",
            "lg-device-user-code",
            "lg-btn-open-communityz",
            "lg-login-identifier",
            "lg-btn-send-otp",
            "lg-login-otp-code",
            "lg-btn-login-submit",
            "lg-btn-login-skip",
            "lg-step-launcher",
            "lg-account-select",
            "lg-card-vanilla",
            "lg-card-enhanced",
            "lg-bind-email",
            "lg-bind-pin",
            "lg-btn-bind-pin-toggle",
            "lg-btn-bind-pin-clear",
            "lg-bind-auto-pin",
            "lg-edit-pin",
            "lg-btn-edit-pin-toggle",
            "lg-btn-edit-pin-clear",
            "lg-edit-auto-pin",
            "lg-window-style",
            "lg-btn-import-engine",
            "lg-btn-download-engine",
            "btn-open-launcher-gate",
        ):
            self.assertIn(f'id="{dom_id}"', html, f"Missing V2 Startup Gate DOM id: {dom_id}")
        self.assertIn("Local Only - Encrypted on This PC, Never Uploaded", html)

    def test_concurrent_bind_update_and_launch_preserve_all_accounts(self) -> None:
        """Concurrent bind, update, and launch calls must not lose updates or collide on profiles."""
        engine_root = Path(self.tmp.name) / "engine concurrent"
        fake_gem = self._make_fake_engine_manager(engine_root)
        unverified_reg = lambda _p: {}

        errors: list[Exception] = []
        bound_ids: list[str] = []
        id_lock = threading.Lock()

        def _bind_worker(idx: int) -> None:
            try:
                res = self.vault_mod.bind_new_account(
                    f"worker{idx}@example.com",
                    label=f"Worker {idx}",
                    window_style="borderless",
                    engine_root=engine_root,
                    skip_registry_clear=True,
                    reg_reader=unverified_reg,
                )
                if not res.get("ok"):
                    raise AssertionError(res)
                with id_lock:
                    bound_ids.append(res["account"]["id"])
            except Exception as exc:
                errors.append(exc)

        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=fake_gem):
            threads = [threading.Thread(target=_bind_worker, args=(i,)) for i in range(6)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=10.0)

        self.assertEqual(errors, [])
        self.assertEqual(len(bound_ids), 6)
        self.assertEqual(len(set(bound_ids)), 6)
        stored = self.vault_mod.load_vault()["accounts"]
        self.assertEqual(len(stored), 6)

        # Concurrent update on account 0 + launch on account 1 preserves both mutations
        with (
            mock.patch.object(self.vault_mod, "stop_background_heinz_daemons", return_value={"ok": True, "stopped_count": 0}),
            mock.patch.object(self.vault_mod, "_find_running_game_pids", return_value={}),
        ):
            t_upd = threading.Thread(
                target=lambda: self.vault_mod.update_account(bound_ids[0], label="Renamed Zero", reg_reader=unverified_reg)
            )
            t_launch = threading.Thread(
                target=lambda: self.vault_mod.launch_bound_account(
                    bound_ids[1],
                    mode="enhanced",
                    engine_root=engine_root,
                    popen_fn=lambda args, **kw: _FakePopenResult(pid=77111),
                    reg_reader=unverified_reg,
                )
            )
            t_upd.start()
            t_launch.start()
            t_upd.join(timeout=5.0)
            t_launch.join(timeout=5.0)

        after = {a["id"]: a for a in self.vault_mod.load_vault()["accounts"]}
        self.assertEqual(after[bound_ids[0]]["label"], "Renamed Zero")
        self.assertEqual(after[bound_ids[1]]["last_mode"], "enhanced")
        self.assertGreater(after[bound_ids[1]]["last_launched_at"], 0)

    def test_load_vault_retries_permission_error_and_backs_up_corrupt_json(self) -> None:
        """load_vault retries transient PermissionError and moves corrupt JSON aside before returning empty."""
        vpath = self.vault_mod.resolve_vault_path()
        vpath.parent.mkdir(parents=True, exist_ok=True)
        vpath.write_text('{"schema_version": 1, "accounts": [{"id": "hz01z"}]}', encoding="utf-8")

        calls = {"n": 0}
        orig_read_text = Path.read_text

        def _flaky_read_text(path_obj: Path, *args, **kwargs):
            if path_obj == vpath and calls["n"] < 2:
                calls["n"] += 1
                raise PermissionError("Locked transiently")
            return orig_read_text(path_obj, *args, **kwargs)

        with mock.patch.object(Path, "read_text", autospec=True, side_effect=_flaky_read_text):
            loaded = self.vault_mod.load_vault()
        self.assertEqual(calls["n"], 2)
        self.assertEqual(len(loaded["accounts"]), 1)

        vpath.write_text("{corrupt json", encoding="utf-8")
        empty = self.vault_mod.load_vault()
        self.assertEqual(empty["accounts"], [])
        backups = list(vpath.parent.glob("bound accounts.corrupt.*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "{corrupt json")

    def test_stop_background_heinz_daemons_name_first_real_psutil_and_access_denied(self) -> None:
        """stop_background_heinz_daemons reads cmdline lazily by name and tolerates AccessDenied."""
        class _NameOnlyProc:
            def __init__(self, pid: int, name: str, cmdline: list[str] | None, deny: bool = False) -> None:
                self.info = {"pid": pid, "name": name}
                self._cmdline = cmdline
                self._deny = deny
                self.cmdline_called = False
                self.terminated = False
                self.waited = False

            def cmdline(self) -> list[str]:
                self.cmdline_called = True
                if self._deny:
                    raise psutil.AccessDenied(self.info["pid"])
                return list(self._cmdline or [])

            def terminate(self) -> None:
                self.terminated = True

            def wait(self, timeout: float | None = None) -> int:
                self.waited = True
                return 0

        import psutil
        non_py = _NameOnlyProc(9101, "explorer.exe", ["explorer.exe"])
        denied_py = _NameOnlyProc(9102, "python.exe", None, deny=True)
        target_daemon = _NameOnlyProc(9103, "python.exe", ["python.exe", "daemon/lastz auto engine daemon.py"])

        with mock.patch.object(self.vault_mod.psutil, "process_iter", return_value=[non_py, denied_py, target_daemon]):
            res = self.vault_mod.stop_background_heinz_daemons()

        self.assertTrue(res["ok"])
        self.assertFalse(non_py.cmdline_called)
        self.assertTrue(denied_py.cmdline_called)
        self.assertTrue(target_daemon.cmdline_called)
        self.assertTrue(target_daemon.terminated)
        self.assertEqual(res["stopped_count"], 1)

    def test_launch_bound_account_already_running_guard(self) -> None:
        """Duplicate live launch for an already running slot returns cleanly without spawning a duplicate."""
        engine_root = Path(self.tmp.name) / "engine dup"
        fake_gem = self._make_fake_engine_manager(engine_root)
        unverified_reg = lambda _p: {}

        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=fake_gem):
            bound = self.vault_mod.bind_new_account(
                "dup.guard@example.com",
                label="Dup Guard",
                window_style="borderless",
                engine_root=engine_root,
                skip_registry_clear=True,
                reg_reader=unverified_reg,
            )
        acc_id = bound["account"]["id"]
        spawn_calls = {"n": 0}

        def _spy_popen(args, **kw):
            spawn_calls["n"] += 1
            return _FakePopenResult(pid=88888)

        with mock.patch.object(self.vault_mod, "_find_running_game_pids", return_value={acc_id: 99123}):
            res = self.vault_mod.launch_bound_account(
                acc_id,
                mode="enhanced",
                engine_root=engine_root,
                dry_run=False,
                popen_fn=_spy_popen,
                reg_reader=unverified_reg,
            )
        self.assertTrue(res["ok"])
        self.assertTrue(res.get("already_running"))
        self.assertEqual(res["pid"], 99123)
        self.assertEqual(spawn_calls["n"], 0)

    def test_dpapi_protect_unprotect_roundtrip_and_vault_persistence(self) -> None:
        """Verify Windows DPAPI current-user encryption, gitignored local vault file, and failure paths."""
        dpapi_path = self.vault_mod.resolve_dpapi_vault_path()
        self.assertEqual(dpapi_path, self.data_dir / "json cache" / "local dpapi vault.json")
        self.assertNotIn("_", dpapi_path.name)

        gitignore_text = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("data/json cache/local dpapi vault.json", gitignore_text)
        self.assertIn("data/json cache/*.corrupt.*.json", gitignore_text)

        self.assertEqual(self.vault_mod.dpapi_protect_text(""), "")
        self.assertEqual(self.vault_mod.dpapi_unprotect_text(""), "")

        if os.name == "nt":
            sample_secret = "849201_TEST_SENTINEL"
            blob = self.vault_mod.dpapi_protect_text(sample_secret)
            self.assertTrue(bool(blob))
            self.assertNotIn(sample_secret, blob)
            self.assertEqual(self.vault_mod.dpapi_unprotect_text(blob), sample_secret)

            self.assertTrue(self.vault_mod.set_dpapi_secret("translator", "deepl_api_key", sample_secret))
            self.assertTrue(self.vault_mod.has_dpapi_secret("translator", "deepl_api_key"))
            self.assertEqual(self.vault_mod.get_dpapi_secret("translator", "deepl_api_key"), sample_secret)
            raw_file = dpapi_path.read_text(encoding="utf-8")
            self.assertNotIn(sample_secret, raw_file)

            self.assertTrue(self.vault_mod.delete_dpapi_secret("translator", "deepl_api_key"))
            self.assertFalse(self.vault_mod.has_dpapi_secret("translator", "deepl_api_key"))
            self.assertIsNone(self.vault_mod.get_dpapi_secret("translator", "deepl_api_key"))

        # Corrupt JSON in local dpapi vault.json must back up and recover cleanly.
        dpapi_path.parent.mkdir(parents=True, exist_ok=True)
        dpapi_path.write_text("{corrupt_dpapi", encoding="utf-8")
        self.assertFalse(self.vault_mod.has_dpapi_secret("account_pin", "hz01z"))
        self.assertEqual(len(list(dpapi_path.parent.glob("local dpapi vault.corrupt.*.json"))), 1)

        # Non-Windows platform guard and CryptUnprotectData failure handling.
        with mock.patch.object(self.vault_mod.os, "name", "posix"):
            with self.assertRaises(RuntimeError):
                self.vault_mod.dpapi_protect_text("1234")
        fake_crypt = mock.MagicMock()
        fake_crypt.CryptUnprotectData.return_value = 0
        fake_k32 = mock.MagicMock()
        with mock.patch.object(self.vault_mod, "_get_dpapi_libs", return_value=(fake_crypt, fake_k32)):
            with self.assertRaises(RuntimeError):
                self.vault_mod.dpapi_unprotect_text(base64.b64encode(b"bad_cipher").decode("ascii"))

    def test_forbidden_key_stripping_and_strip_local_secrets_for_sync(self) -> None:
        """Verify secret fragments are stripped while safe bool flags and ping/spin keys survive."""
        payload = {
            "account": {
                "id": "hz01z",
                "pin": "112233",
                "security_pin": "445566",  # TEST_SENTINEL
                "game_pin": "778899",  # TEST_SENTINEL
                "securityPin": "001122",
                "password": "pw",
                "passwd": "pw2",
                "setoken": "raw_st",
                "secret": "sec",
                "raw_token": "rt",
                "session_token": "st",
                "auth_token": "at",
                "access_token": "hz_dt_TEST_SENTINEL_EXAMPLE",
                "bearer": "TEST_SENTINEL_BEARER_EXAMPLE",
                "api_key": "key1",
                "deepl_api_key": "key2",
                "gemini_api_key": "key3",
                "has_security_pin": True,
                "auto_enter_pin": True,
                "has_deepl_key": False,
                "has_gemini_key": True,
                "ping_ms": 42,
                "spin_count": 3,
            },
            "items": [
                {"name": "ok", "ping": 15, "user_pin": "9999"},
                {"pin_code": "1234", "mapping_id": "m1"},
            ],
        }
        cleaned = self.vault_mod.strip_local_secrets_for_sync(payload)
        # Input must not be mutated in place.
        self.assertIn("security_pin", payload["account"])

        acc_clean = cleaned["account"]
        for forbidden in (
            "pin",
            "security_pin",
            "game_pin",
            "securityPin",
            "password",
            "passwd",
            "setoken",
            "secret",
            "raw_token",
            "session_token",
            "auth_token",
            "access_token",
            "bearer",
            "api_key",
            "deepl_api_key",
            "gemini_api_key",
        ):
            self.assertNotIn(forbidden, acc_clean)

        self.assertIs(acc_clean["has_security_pin"], True)
        self.assertIs(acc_clean["auto_enter_pin"], True)
        self.assertIs(acc_clean["has_deepl_key"], False)
        self.assertIs(acc_clean["has_gemini_key"], True)
        self.assertEqual(acc_clean["ping_ms"], 42)
        self.assertEqual(acc_clean["spin_count"], 3)
        self.assertEqual(cleaned["items"][0], {"name": "ok", "ping": 15})
        self.assertEqual(cleaned["items"][1], {"mapping_id": "m1"})

        # save_vault must also strip secrets while preserving auto_enter_pin bool.
        self.vault_mod.save_vault({"accounts": [dict(payload["account"])]})
        saved_acc = self.vault_mod.load_vault()["accounts"][0]
        self.assertNotIn("security_pin", saved_acc)
        self.assertNotIn("deepl_api_key", saved_acc)
        self.assertIs(saved_acc["auto_enter_pin"], True)

    def test_account_pin_crud_and_hub_rpc_never_expose_raw_pin(self) -> None:
        """Verify PIN bind/update/clear/unbind store encrypted DPAPI blobs and return booleans only."""
        empty_reg = lambda _p: {}
        pin_one = "739104"
        pin_two = "558219"

        hub_path = PROJECT_ROOT / "launcher" / "heinzhubweb.py"
        spec = importlib.util.spec_from_file_location("test_v2_pin_hub_mod", str(hub_path))
        assert spec is not None and spec.loader is not None
        hub_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hub_mod)

        with (
            mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=None),
            mock.patch.object(hub_mod.HubBackend, "_load_cached_state"),
            mock.patch.object(hub_mod.HubBackend, "_load_always_on_daemon_config"),
            mock.patch.object(hub_mod.HubBackend, "_start_always_on_daemon"),
            mock.patch.object(hub_mod.HubBackend, "log"),
        ):
            backend = hub_mod.HubBackend(defer_enhanced=True)
            backend._account_vault_mod_cache = self.vault_mod

            res_bind = backend.bind_email_account(
                "pin.user@example.com",
                "PinMain",
                "borderless",
                pin_one,
                True,
            )
            self.assertTrue(res_bind["ok"])
            acc = res_bind["account"]
            self.assertTrue(acc["has_security_pin"])
            self.assertTrue(acc["auto_enter_pin"])
            self.assertEqual(self.vault_mod.get_account_security_pin_for_launch(acc["id"]), pin_one)

            # Update PIN and auto_enter_pin via HubBackend.
            res_upd = backend.update_bound_account(
                acc["id"],
                security_pin=pin_two,
                auto_enter_pin=False,
            )
            self.assertTrue(res_upd["ok"])
            self.assertTrue(res_upd["account"]["has_security_pin"])
            self.assertFalse(res_upd["account"]["auto_enter_pin"])
            self.assertEqual(self.vault_mod.get_account_security_pin_for_launch(acc["id"]), pin_two)

            # Raw PIN must NEVER appear in bound accounts.json, DPAPI JSON, or list_bound_accounts.
            listed = self.vault_mod.list_bound_accounts(sync_discovered=False, reg_reader=empty_reg)
            vault_json = self.vault_mod.resolve_vault_path().read_text(encoding="utf-8")
            dpapi_json = self.vault_mod.resolve_dpapi_vault_path().read_text(encoding="utf-8")
            for raw_pin in (pin_one, pin_two):
                self.assertNotIn(raw_pin, json.dumps(listed))
                self.assertNotIn(raw_pin, vault_json)
                self.assertNotIn(raw_pin, dpapi_json)

            # Clear PIN via HubBackend.
            res_clr = backend.clear_bound_account_pin(acc["id"])
            self.assertTrue(res_clr["ok"])
            self.assertFalse(res_clr["has_security_pin"])
            self.assertIsNone(self.vault_mod.get_account_security_pin_for_launch(acc["id"]))

            # Unbind removes orphaned DPAPI PIN as well.
            self.vault_mod.set_account_security_pin(acc["id"], pin_one)
            self.assertTrue(self.vault_mod.has_account_security_pin(acc["id"]))
            rem = self.vault_mod.unbind_account(acc["id"], clear_session=False)
            self.assertTrue(rem["ok"])
            self.assertFalse(self.vault_mod.has_account_security_pin(acc["id"]))

    def test_enhanced_only_auto_pin_launch_gating_and_vanilla_isolation(self) -> None:
        """Vanilla NEVER decrypts PIN or touches Frida/client discovery; Enhanced schedules transient auto-PIN."""
        engine_root = Path(self.tmp.name) / "engine autopin"
        fake_gem = self._make_fake_engine_manager(engine_root)
        empty_reg = lambda _p: {}
        secret_pin = "614920"

        with mock.patch.object(self.vault_mod, "_load_game_engine_manager", return_value=fake_gem):
            bound = self.vault_mod.bind_new_account(
                "autopin@example.com",
                label="AutoPin",
                window_style="borderless",
                engine_root=engine_root,
                skip_registry_clear=True,
                reg_reader=empty_reg,
                security_pin=secret_pin,
                auto_enter_pin=True,
            )
        self.assertTrue(bound["ok"])
        acc_id = bound["account"]["id"]

        # 1. Pure Vanilla must NEVER decrypt PIN, schedule auto-PIN, or load client discovery.
        with (
            mock.patch.object(self.vault_mod, "stop_background_heinz_daemons", return_value={"ok": True, "stopped_count": 0}),
            mock.patch.object(self.vault_mod, "get_account_security_pin_for_launch") as mock_get_pin,
            mock.patch.object(self.vault_mod, "_schedule_enhanced_auto_pin") as mock_sched,
        ):
            v_res = self.vault_mod.launch_bound_account(
                acc_id,
                mode="vanilla",
                engine_root=engine_root,
                dry_run=False,
                popen_fn=lambda args, **kw: _FakePopenResult(pid=41001),
                reg_reader=empty_reg,
            )
        self.assertTrue(v_res["ok"])
        self.assertFalse(v_res["auto_pin_scheduled"])
        mock_get_pin.assert_not_called()
        mock_sched.assert_not_called()
        self.assertNotIn("heinz_vault_client_discovery", self.vault_mod._LOADED_MODULES)

        # 2. Enhanced mode with auto_enter_pin=True schedules transient auto-PIN hook.
        with mock.patch.object(self.vault_mod, "_schedule_enhanced_auto_pin") as mock_sched:
            e_res = self.vault_mod.launch_bound_account(
                acc_id,
                mode="enhanced",
                engine_root=engine_root,
                dry_run=False,
                popen_fn=lambda args, **kw: _FakePopenResult(pid=41002),
                reg_reader=empty_reg,
            )
        self.assertTrue(e_res["ok"])
        self.assertTrue(e_res["auto_pin_scheduled"])
        mock_sched.assert_called_once_with(41002, secret_pin)
        self.assertNotIn(secret_pin, json.dumps(e_res))

        # 3. Verify _run_enhanced_auto_pin_worker delegates via _load_client_discovery() -> frida_eval_lua.
        fake_cd = types.SimpleNamespace(
            _xlua_loaded=lambda pid, min_uptime_sec=2.0: True,
            frida_eval_lua=mock.Mock(return_value=(True, "SUBMITTED_UIPIN")),
        )
        with (
            mock.patch.object(self.vault_mod, "_load_client_discovery", return_value=fake_cd),
            mock.patch.object(self.vault_mod.psutil, "pid_exists", return_value=True),
        ):
            worker_status = self.vault_mod._run_enhanced_auto_pin_worker(41002, secret_pin, timeout_sec=2.0)
        self.assertEqual(worker_status, "SUBMITTED_UIPIN")
        fake_cd.frida_eval_lua.assert_called_once()
        lua_sent = fake_cd.frida_eval_lua.call_args[0][1]
        self.assertIn("UIPinInput", lua_sent)
        self.assertIn("UIPINCodeInput", lua_sent)
        self.assertIn("UserPasswordCheck", lua_sent)

        # 4. Enhanced mode with auto_enter_pin=False does NOT schedule auto-PIN.
        self.vault_mod.update_account(acc_id, auto_enter_pin=False, reg_reader=empty_reg)
        with mock.patch.object(self.vault_mod, "_schedule_enhanced_auto_pin") as mock_sched:
            e_off = self.vault_mod.launch_bound_account(
                acc_id,
                mode="enhanced",
                engine_root=engine_root,
                dry_run=False,
                popen_fn=lambda args, **kw: _FakePopenResult(pid=41003),
                reg_reader=empty_reg,
            )
        self.assertTrue(e_off["ok"])
        self.assertFalse(e_off["auto_pin_scheduled"])
        mock_sched.assert_not_called()

    def test_page1_communityz_auth_flows_against_mock_server(self) -> None:
        """Verify Page 1 CommunityZ Device-Code, PoW+OTP, Pro vs Free 403, 401 revoke, offline, and Guest."""
        state: dict[str, object] = {
            "device_status": "pending",
            "device_tier": "pro",
            "bootstrap_mode": "ok",
            "challenge_id": "ch_TEST_SENTINEL_1",
            "challenge_salt": "salt_EXAMPLE_99",
            "challenge_diff": 2,
            "otp_tier": "pro",
            "logout_called": False,
            "last_pow_website": None,
        }

        class _Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, _fmt: str, *_args) -> None:
                return

            def _send(self, status: int, body: dict, cookies: list[str] | None = None) -> None:
                raw = json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                for ck in cookies or []:
                    self.send_header("Set-Cookie", ck)
                self.end_headers()
                self.wfile.write(raw)

            def _read_json(self) -> dict:
                n = int(self.headers.get("Content-Length") or 0)
                if n <= 0:
                    return {}
                return json.loads(self.rfile.read(n).decode("utf-8"))

            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/api/auth/challenge":
                    self._send(
                        200,
                        {
                            "ok": True,
                            "challenge": {
                                "id": state["challenge_id"],
                                "salt": state["challenge_salt"],
                                "difficulty": state["challenge_diff"],
                                "algorithm": "SHA-256",
                            },
                        },
                    )
                    return
                if self.path == "/api/desktop/bootstrap":
                    auth_hdr = self.headers.get("Authorization") or ""
                    if auth_hdr != "Bearer hz_dt_TEST_SENTINEL_EXAMPLE_TOKEN":
                        self._send(401, {"ok": False, "error": "Desktop token invalid or revoked."})
                        return
                    if state["bootstrap_mode"] == "sub_req":
                        self._send(403, {"ok": False, "code": "SUBSCRIPTION_REQUIRED", "error": "Subscription inactive; Desktop Bridge paused."})
                        return
                    if state["bootstrap_mode"] == "revoked":
                        self._send(401, {"ok": False, "error": "Desktop token invalid or revoked."})
                        return
                    self._send(
                        200,
                        {
                            "ok": True,
                            "deviceName": "HeinZ V2 Desktop",
                            "user": {
                                "id": "usr_1",
                                "email": "sub@example.com",
                                "displayName": "ProSubscriber",
                                "tier": "pro",
                                "entitlements": {"tier": "pro", "desktopBridge": True},
                            },
                            "uids": [{"gameUid": "1092847561", "serverId": 694, "ign": "ProSubscriber", "isMain": True}],
                        },
                    )
                    return
                self._send(404, {"ok": False, "error": "Not found"})

            def do_POST(self) -> None:  # noqa: N802
                body = self._read_json()
                if self.path == "/api/desktop/device-code":
                    self._send(
                        200,
                        {
                            "ok": True,
                            "deviceCode": "dc_TEST_SENTINEL_1",
                            "userCode": "HZ-A7K-9M2",
                            "expiresInSeconds": 600,
                            "pollIntervalSeconds": 5,
                        },
                    )
                    return
                if self.path == "/api/desktop/authorize":
                    cookie_hdr = self.headers.get("Cookie") or ""
                    csrf_hdr = self.headers.get("X-CSRF-Token") or ""
                    if "heinz_sid=TEST_SENTINEL_SID_EXAMPLE" not in cookie_hdr or csrf_hdr != "TEST_SENTINEL_CSRF_EXAMPLE":
                        self._send(401, {"ok": False, "error": "Authentication required."})
                        return
                    state["device_status"] = "approved"
                    self._send(200, {"ok": True, "approved": True, "userCode": body.get("userCode")})
                    return
                if self.path == "/api/desktop/token":
                    ds = state["device_status"]
                    if ds == "pending":
                        self._send(202, {"ok": False, "code": "AUTHORIZATION_PENDING", "error": "Waiting for subscriber approval."})
                        return
                    if ds == "sub_req":
                        self._send(403, {"ok": False, "code": "SUBSCRIPTION_REQUIRED", "error": "Active Pro or Alliance subscription required."})
                        return
                    if ds == "expired":
                        self._send(400, {"ok": False, "code": "EXPIRED_TOKEN", "error": "Device code expired."})
                        return
                    self._send(
                        200,
                        {
                            "ok": True,
                            "accessToken": "hz_dt_TEST_SENTINEL_EXAMPLE_TOKEN",
                            "deviceId": "dev_1",
                            "user": {
                                "id": "usr_1",
                                "email": "sub@example.com",
                                "displayName": "ProSubscriber",
                                "tier": "pro",
                                "entitlements": {"tier": "pro", "desktopBridge": True},
                            },
                        },
                    )
                    return
                if self.path == "/api/auth/precheck":
                    self._send(200, {"ok": True, "email": str(body.get("email") or "").lower()})
                    return
                if self.path == "/api/auth/request-otp":
                    state["last_pow_website"] = body.get("website")
                    digest = hashlib.sha256(
                        f"{state['challenge_id']}:{state['challenge_salt']}:{body.get('powNonce')}".encode("utf-8")
                    ).hexdigest()
                    if not digest.startswith("0" * int(state["challenge_diff"])):  # type: ignore[arg-type]
                        self._send(400, {"ok": False, "error": "Invalid PoW"})
                        return
                    self._send(200, {"ok": True, "otpId": "otp_1", "email": body.get("email"), "expiresInSeconds": 600, "delivery": "local_dev", "devPreviewCode": "654321"})
                    return
                if self.path == "/api/auth/verify-otp":
                    tier = str(state["otp_tier"])
                    ent = {"tier": tier, "desktopBridge": tier in ("pro", "alliance", "admin")}
                    self._send(
                        200,
                        {
                            "ok": True,
                            "csrfToken": "TEST_SENTINEL_CSRF_EXAMPLE",
                            "user": {"id": "usr_1", "email": body.get("email"), "displayName": "ProSubscriber", "tier": tier, "entitlements": ent},
                        },
                        cookies=[
                            "heinz_sid=TEST_SENTINEL_SID_EXAMPLE; Path=/; HttpOnly",
                            "heinz_csrf=TEST_SENTINEL_CSRF_EXAMPLE; Path=/",
                        ],
                    )
                    return
                if self.path == "/api/auth/logout":
                    state["logout_called"] = True
                    self._send(200, {"ok": True})
                    return
                self._send(404, {"ok": False, "error": "Not found"})

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        port = server.server_address[1]
        srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
        srv_thread.start()

        hub_path = PROJECT_ROOT / "launcher" / "heinzhubweb.py"
        spec = importlib.util.spec_from_file_location("test_v2_cz_hub_mod", str(hub_path))
        assert spec is not None and spec.loader is not None
        hub_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hub_mod)

        orig_cz_url = os.environ.get("HEINZ_COMMUNITYZ_API_URL")
        os.environ["HEINZ_COMMUNITYZ_API_URL"] = f"http://127.0.0.1:{port}"
        try:
            with (
                mock.patch.object(hub_mod.HubBackend, "_load_cached_state"),
                mock.patch.object(hub_mod.HubBackend, "_load_always_on_daemon_config"),
                mock.patch.object(hub_mod.HubBackend, "_start_always_on_daemon"),
                mock.patch.object(hub_mod.HubBackend, "log"),
            ):
                backend = hub_mod.HubBackend(defer_enhanced=True)
                backend._account_vault_mod_cache = self.vault_mod

                # 1. Device-code pairing: pending -> approved -> boot verification.
                dc = backend.start_communityz_device_login("TestRig")
                self.assertTrue(dc["ok"])
                self.assertEqual(dc["user_code"], "HZ-A7K-9M2")

                pend = backend.poll_communityz_device_login(dc["device_code"])
                self.assertTrue(pend["ok"])
                self.assertEqual(pend["status"], "pending")

                state["device_status"] = "approved"
                auth_ok = backend.poll_communityz_device_login(dc["device_code"], remember=True)
                self.assertTrue(auth_ok["ok"])
                self.assertTrue(auth_ok["signed_in"])
                self.assertEqual(auth_ok["tier"], "pro")
                self.assertNotIn("accessToken", json.dumps(auth_ok))
                self.assertEqual(
                    self.vault_mod.get_communityz_bearer_token(),
                    "hz_dt_TEST_SENTINEL_EXAMPLE_TOKEN",
                )

                # Boot state auto-verifies DPAPI token via /api/desktop/bootstrap.
                boot_ok = backend.get_launcher_boot_state(check_remote=False)
                self.assertTrue(boot_ok["auth_state"]["signed_in"])
                self.assertEqual(boot_ok["auth_state"]["mode"], "communityz")

                # 403 SUBSCRIPTION_REQUIRED on bootstrap.
                state["bootstrap_mode"] = "sub_req"
                sub_err = backend.get_heinz_auth_status(verify_remote=True)
                self.assertFalse(sub_err["signed_in"])
                self.assertEqual(sub_err["code"], "SUBSCRIPTION_REQUIRED")
                self.assertTrue(self.vault_mod.has_dpapi_secret("communityz", "bearer_token"))

                # 401 revoked clears stale DPAPI token.
                state["bootstrap_mode"] = "revoked"
                rev_err = backend.get_heinz_auth_status(verify_remote=True)
                self.assertFalse(rev_err["signed_in"])
                self.assertEqual(rev_err["code"], "TOKEN_REVOKED")
                self.assertFalse(self.vault_mod.has_dpapi_secret("communityz", "bearer_token"))

                # 2. Email PoW + OTP flow: free tier gets 403 SUBSCRIPTION_REQUIRED; pro tier bridges cleanly.
                otp_req = backend.request_communityz_otp("sub@example.com")
                self.assertTrue(otp_req["ok"])
                self.assertEqual(state["last_pow_website"], "")
                self.assertEqual(otp_req.get("dev_preview_code"), "654321")

                state["otp_tier"] = "free"
                free_res = backend.verify_communityz_otp("sub@example.com", "654321")
                self.assertFalse(free_res["ok"])
                self.assertEqual(free_res["code"], "SUBSCRIPTION_REQUIRED")
                self.assertTrue(state["logout_called"])
                self.assertFalse(self.vault_mod.has_dpapi_secret("communityz", "bearer_token"))

                state["otp_tier"] = "pro"
                state["bootstrap_mode"] = "ok"
                pro_res = backend.verify_communityz_otp("sub@example.com", "654321")
                self.assertTrue(pro_res["ok"])
                self.assertTrue(pro_res["signed_in"])
                self.assertEqual(pro_res["tier"], "pro")
                self.assertTrue(self.vault_mod.has_dpapi_secret("communityz", "bearer_token"))

                # 3. Offline NETWORK_ERROR preserves DPAPI token.
                server.shutdown()
                off_res = backend.get_heinz_auth_status(verify_remote=True)
                self.assertFalse(off_res["signed_in"])
                self.assertTrue(off_res["network_offline"])
                self.assertTrue(self.vault_mod.has_dpapi_secret("communityz", "bearer_token"))

                # 4. Logout clears DPAPI token cleanly.
                out_res = backend.logout_heinz_account()
                self.assertTrue(out_res["ok"])
                self.assertFalse(out_res["signed_in"])
                self.assertFalse(self.vault_mod.has_dpapi_secret("communityz", "bearer_token"))
        finally:
            try:
                server.shutdown()
            except Exception:
                pass
            server.server_close()
            if orig_cz_url is None:
                os.environ.pop("HEINZ_COMMUNITYZ_API_URL", None)
            else:
                os.environ["HEINZ_COMMUNITYZ_API_URL"] = orig_cz_url

    def test_m1_extended_hygiene_no_dashes_or_emojis_in_owned_files(self) -> None:
        """All M1 owned files must contain zero em/en dashes, zero astral emojis, and clean M1 HTML/JS sections."""
        astral_emoji_re = re.compile(r"[\U0001F300-\U0001FAFF]")
        full_emoji_re = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
        owned = (
            PROJECT_ROOT / ".gitignore",
            PROJECT_ROOT / "tools" / "account launcher vault.py",
            PROJECT_ROOT / "launcher" / "heinzhubweb.py",
            PROJECT_ROOT / "launcher" / "web" / "index.html",
            PROJECT_ROOT / "tests" / "testAccountLauncherVault.py",
        )
        em_dash = chr(0x2014)
        en_dash = chr(0x2013)
        html_mdash = "&md" + "ash;"
        html_ndash = "&nd" + "ash;"
        for fp in owned:
            txt = fp.read_text(encoding="utf-8")
            self.assertNotIn(em_dash, txt, f"U+2014 em dash found in {fp.name}")
            self.assertNotIn(en_dash, txt, f"U+2013 en dash found in {fp.name}")
            self.assertIsNone(astral_emoji_re.search(txt), f"Astral emoji found in {fp.name}")
            if fp.suffix.lower() != ".html":
                self.assertNotIn(html_mdash, txt.lower(), f"HTML mdash entity found in {fp.name}")
                self.assertNotIn(html_ndash, txt.lower(), f"HTML ndash entity found in {fp.name}")
                self.assertIsNone(full_emoji_re.search(txt), f"Emoji/symbol found in {fp.name}")
            else:
                self.assertNotIn(html_mdash, txt.lower(), f"HTML mdash entity found in {fp.name}")
                m_gate = txt.split("<!-- V2 STANDALONE LAUNCHER POPUP", 1)[1].split('<div class="app-shell">', 1)[0]
                m_ctrl = txt.split("/* === V2 STANDALONE LAUNCHER GATE CONTROLLER === */", 1)[1]
                for seg_name, seg in (("gate_html", m_gate), ("gate_js", m_ctrl)):
                    self.assertNotIn(html_ndash, seg.lower(), f"HTML ndash entity found in {seg_name}")
                    self.assertIsNone(full_emoji_re.search(seg), f"Emoji/symbol found in {seg_name}")


if __name__ == "__main__":
    unittest.main()
