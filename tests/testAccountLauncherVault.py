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
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
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

            # Verify Login To Account RPC never stores passwords to disk
            secret_pw = "SUPER_SECRET_NEVER_PERSIST_9911"
            login_res = backend.authenticate_heinz_account("player@example.com", secret_pw, remember=True, skip=False)
            self.assertTrue(login_res["ok"])
            self.assertTrue(login_res["signed_in"])
            self.assertEqual(login_res["identifier"], "player@example.com")
            prefs_file = Path(backend._heinz_login_prefs_path())
            self.assertTrue(prefs_file.is_file())
            prefs_text = prefs_file.read_text(encoding="utf-8")
            self.assertNotIn(secret_pw, prefs_text)
            self.assertIn("player@example.com", prefs_text)
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
            "lg-login-identifier",
            "lg-login-password",
            "lg-btn-login-submit",
            "lg-btn-login-skip",
            "lg-step-launcher",
            "lg-account-select",
            "lg-card-vanilla",
            "lg-card-enhanced",
            "lg-bind-email",
            "lg-window-style",
            "lg-btn-import-engine",
            "lg-btn-download-engine",
            "btn-open-launcher-gate",
        ):
            self.assertIn(f'id="{dom_id}"', html, f"Missing V2 Startup Gate DOM id: {dom_id}")


if __name__ == "__main__":
    unittest.main()
