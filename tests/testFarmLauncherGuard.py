"""Farm Launcher Auto-Heal Guard Verification Suite.

Covers post-update rotation recovery in `tools/sync farm clients.py`, daemon supervision
in `daemon/lastz auto engine daemon.py`, and Hub/UI contracts in `launcher/heinzhubweb.py`
and `launcher/web/index.html`:
1. Simulated Last Z updater rotation (`launcher/` -> `launcher_old_<hex>` + fresh vanilla `launcher/Launcher.exe`).
2. Total wipe recovery (missing `launcher_backup/` and `launcher_old_*`) with template script
   regeneration + cross-instance UTF-16LE `FarmLauncherHook.exe` binary patching.
3. Wrong-identity hook binary detection (`Alt3Game.exe`/`Alt3Z` planted inside Farm) and in-place repair.
4. Dry-run safety (zero writes on disk), idempotency on second run, and strict Main-client isolation.
5. Generated PowerShell script syntax validation via PowerShell AST parser.
6. Daemon, Hub, UI button, and static zero-underscore / zero-em-dash guardrails.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_sfc_module():
    path = PROJECT_ROOT / "tools" / "sync farm clients.py"
    spec = importlib.util.spec_from_file_location("test_sfc_guard_mod", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_fake_hook_binary(exe_name: str, unity_profile: str) -> bytes:
    """Create a realistic >1KB synthetic PE-like binary embedding UTF-16LE exe and profile markers."""
    header = b"MZ" + (b"\x00" * 510)
    body = b"HOOK_DATA:" + exe_name.encode("utf-16le") + (b"\x00" * 64) + unity_profile.encode("utf-16le") + (b"\x00" * 1024)
    return header + body


class TestFarmLauncherAutoHealGuard(unittest.TestCase):
    """Tier 1/2: Post-update Farm/Alt launcher wrapper and hook auto-heal verification."""

    def setUp(self) -> None:
        self.sfc = _load_sfc_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

        self.main_root = self.root / "MainLastZ"
        self.main_game = self.main_root / "Game"
        self.main_game.mkdir(parents=True)
        (self.main_game / "Survival.exe").write_bytes(b"MAIN_SURVIVAL_BIN")

        self.farm_root = self.root / "FarmLastZ"
        self.farm_game = self.farm_root / "Game"
        self.farm_game.mkdir(parents=True)
        (self.farm_game / "FarmGame.exe").write_bytes(b"FARM_EXE")

        self.third_root = self.root / "ThirdLastZ"
        self.third_game = self.third_root / "Game"
        self.third_game.mkdir(parents=True)
        (self.third_game / "Alt3Game.exe").write_bytes(b"THIRD_EXE")

        self.main_client = {
            "id": "lastz",
            "label": "Main",
            "role": "main",
            "unity_profile": "LastZ",
            "game_dir": str(self.main_game),
            "exe_path": str(self.main_game / "Survival.exe"),
            "exe_name": "Survival.exe",
        }
        self.farm_client = {
            "id": "farmz",
            "label": "Farm",
            "role": "farm",
            "unity_profile": "FarmZ",
            "game_dir": str(self.farm_game),
            "exe_path": str(self.farm_game / "FarmGame.exe"),
            "exe_name": "FarmGame.exe",
        }
        self.third_client = {
            "id": "alt3z",
            "label": "Third",
            "role": "farm",
            "unity_profile": "Alt3Z",
            "game_dir": str(self.third_game),
            "exe_path": str(self.third_game / "Alt3Game.exe"),
            "exe_name": "Alt3Game.exe",
        }
        self.all_clients = [self.main_client, self.farm_client, self.third_client]

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _seed_healthy_launcher(self, inst_root: Path, prefix: str, launcher_exe: str, exe_name: str, prof: str) -> Path:
        ldir = inst_root / "launcher"
        ldir.mkdir(parents=True, exist_ok=True)
        (ldir / f"{prefix}LauncherWrapper.vbs").write_text(f"VBS_{prefix}", encoding="ascii")
        (ldir / f"{prefix}LauncherWrapper.ps1").write_text(f"# PS1_{prefix}\n", encoding="utf-8")
        (ldir / f"{prefix}ProfileIdentity.ps1").write_text(f"# ID_{prefix}\n", encoding="utf-8")
        (ldir / launcher_exe).write_bytes(b"PATCHED_LAUNCHER_" + prefix.encode("ascii") + b"\x00" * 2048)
        (ldir / "FarmLauncherHook.exe").write_bytes(_make_fake_hook_binary(exe_name, prof))
        return ldir

    def test_simulated_updater_rotation_restores_all_five_files_byte_for_byte(self) -> None:
        """Simulate Last Z rotating launcher/ -> launcher_old_862ca5ce and verify full recovery."""
        farm_ldir = self._seed_healthy_launcher(self.farm_root, "Farm", "Launcher_Patched.exe", "FarmGame.exe", "FarmZ")
        orig_hook = (farm_ldir / "FarmLauncherHook.exe").read_bytes()
        orig_patched = (farm_ldir / "Launcher_Patched.exe").read_bytes()

        # First pass seeds launcher_backup/ proactively
        rep1 = self.sfc.heal_farm_launcher(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertTrue(rep1["ok"])
        self.assertFalse(rep1["healed"])
        self.assertEqual(len(rep1["backed_up_files"]), 5)
        self.assertTrue((self.farm_root / "launcher_backup" / "FarmLauncherWrapper.vbs").is_file())

        # Second pass is completely idempotent (zero writes)
        rep2 = self.sfc.heal_farm_launcher(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertFalse(rep2["healed"])
        self.assertEqual(rep2["backed_up_files"], [])

        # Simulate Last Z auto-updater rotating launcher/ -> launcher_old_862ca5ce & extracting fresh vanilla Launcher.exe
        rotated = self.farm_root / "launcher_old_862ca5ce"
        farm_ldir.rename(rotated)
        farm_ldir.mkdir()
        (farm_ldir / "Launcher.exe").write_bytes(b"VANILLA_NEW_LAUNCHER")

        # Health check immediately catches all 5 missing files
        h_before = self.sfc.inspect_farm_launcher_health(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertFalse(h_before["healthy"])
        self.assertTrue(h_before["needs_heal"])
        self.assertEqual(len(h_before["missing_files"]), 5)

        # Dry-run reports exact recovery plan without touching disk
        rep_dry = self.sfc.heal_farm_launcher(self.farm_client, main_client=self.main_client, all_clients=self.all_clients, dry_run=True)
        self.assertTrue(rep_dry["healed"])
        self.assertEqual(len(rep_dry["restored_files"]), 5)
        self.assertFalse((farm_ldir / "FarmLauncherWrapper.vbs").exists())

        # Live auto-heal restores all 5 files byte-for-byte
        rep_heal = self.sfc.heal_farm_launcher(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertTrue(rep_heal["ok"])
        self.assertTrue(rep_heal["healed"])
        self.assertEqual(set(rep_heal["restored_files"]), {
            "FarmLauncherWrapper.vbs",
            "FarmLauncherWrapper.ps1",
            "FarmProfileIdentity.ps1",
            "Launcher_Patched.exe",
            "FarmLauncherHook.exe",
        })
        self.assertEqual((farm_ldir / "FarmLauncherHook.exe").read_bytes(), orig_hook)
        self.assertEqual((farm_ldir / "Launcher_Patched.exe").read_bytes(), orig_patched)
        # Vanilla Launcher.exe is preserved alongside restored files
        self.assertTrue((farm_ldir / "Launcher.exe").is_file())

        h_after = self.sfc.inspect_farm_launcher_health(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertTrue(h_after["healthy"])
        self.assertTrue(h_after["hook_identity_ok"])

    def test_total_wipe_regenerates_valid_ps1_scripts_and_cross_patches_sibling_hook(self) -> None:
        """If both launcher_backup and launcher_old_* are gone, regenerate scripts and patch sibling hook."""
        # Third has a healthy launcher (with Alt3Game.exe / Alt3Z hook)
        self._seed_healthy_launcher(self.third_root, "Third", "Launcher_Third.exe", "Alt3Game.exe", "Alt3Z")

        # Farm only has a wiped vanilla launcher/ folder (no backup, no launcher_old_*)
        farm_ldir = self.farm_root / "launcher"
        farm_ldir.mkdir(parents=True)
        (farm_ldir / "Launcher.exe").write_bytes(b"VANILLA_ONLY")

        rep = self.sfc.heal_farm_launcher(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertTrue(rep["healed"])
        self.assertEqual(set(rep["regenerated_files"]), {
            "FarmLauncherWrapper.vbs",
            "FarmLauncherWrapper.ps1",
            "FarmProfileIdentity.ps1",
        })
        self.assertEqual(rep["patched_files"], ["FarmLauncherHook.exe"])

        # Verify patched hook has FarmGame.exe + FarmZ and ZERO Alt3 remnants
        hook_bytes = (farm_ldir / "FarmLauncherHook.exe").read_bytes()
        self.assertIn("FarmGame.exe".encode("utf-16le"), hook_bytes)
        self.assertIn("FarmZ".encode("utf-16le"), hook_bytes)
        self.assertNotIn("Alt3Game.exe".encode("utf-16le"), hook_bytes)
        self.assertNotIn("Alt3Z".encode("utf-16le"), hook_bytes)

        # Verify VBS points to exact FarmLauncherWrapper.ps1 path
        vbs_txt = (farm_ldir / "FarmLauncherWrapper.vbs").read_text(encoding="ascii")
        self.assertIn(str(farm_ldir / "FarmLauncherWrapper.ps1"), vbs_txt)

        # Verify both regenerated PS1 files parse cleanly in PowerShell AST (zero syntax errors)
        for ps1_name in ("FarmLauncherWrapper.ps1", "FarmProfileIdentity.ps1"):
            ps1_path = farm_ldir / ps1_name
            ps_cmd = (
                f"$err = $null; [void][System.Management.Automation.Language.Parser]::ParseFile('{str(ps1_path)}', [ref]$null, [ref]$err); "
                "if ($err -and $err.Count -gt 0) { $err | ForEach-Object { Write-Error $_.Message }; exit 1 }"
            )
            chk = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            self.assertEqual(chk.returncode, 0, f"PS1 syntax error in {ps1_name}: {chk.stderr}")

    def test_wrong_identity_hook_detected_and_repaired_in_place(self) -> None:
        """Detect a FarmLauncherHook.exe containing Alt3Z inside Farm and patch it cleanly to FarmZ."""
        farm_ldir = self._seed_healthy_launcher(self.farm_root, "Farm", "Launcher_Patched.exe", "Alt3Game.exe", "Alt3Z")
        health = self.sfc.inspect_farm_launcher_health(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertFalse(health["healthy"])
        self.assertFalse(health["hook_identity_ok"])
        self.assertIn("FarmLauncherHook.exe", health["missing_binaries"])

        rep = self.sfc.heal_farm_launcher(self.farm_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertTrue(rep["ok"])
        self.assertTrue(rep["healed"])
        self.assertEqual(rep["patched_files"], ["FarmLauncherHook.exe"])
        self.assertTrue(self.sfc._hook_binary_matches_identity(farm_ldir / "FarmLauncherHook.exe", "FarmGame.exe", "FarmZ"))

    def test_main_client_skipped_and_heal_all_aggregates_farms(self) -> None:
        """Main client is strictly skipped; heal_all_farm_launchers heals Farm & Third together."""
        self._seed_healthy_launcher(self.farm_root, "Farm", "Launcher_Patched.exe", "FarmGame.exe", "FarmZ")
        self._seed_healthy_launcher(self.third_root, "Third", "Launcher_Third.exe", "Alt3Game.exe", "Alt3Z")

        # Main should always be skipped even if it has a launcher folder
        (self.main_root / "launcher").mkdir(parents=True)
        h_main = self.sfc.inspect_farm_launcher_health(self.main_client, main_client=self.main_client, all_clients=self.all_clients)
        self.assertTrue(h_main["skipped"])
        self.assertTrue(h_main["healthy"])

        # Delete Third's VBS to simulate partial damage
        (self.third_root / "launcher" / "ThirdLauncherWrapper.vbs").unlink()
        agg = self.sfc.heal_all_farm_launchers(clients=self.all_clients, main_client=self.main_client)
        self.assertTrue(agg["ok"])
        self.assertEqual(agg["checked"], 2)
        self.assertEqual(agg["healed_count"], 1)
        self.assertEqual(agg["healthy_count"], 1)
        self.assertTrue((self.third_root / "launcher" / "ThirdLauncherWrapper.vbs").is_file())

    def test_daemon_hub_ui_wiring_and_guardrails(self) -> None:
        """Verify auto-heal guard is wired into daemon, Hub startup/actions, and UI buttons with zero em dashes."""
        daemon_src = (PROJECT_ROOT / "daemon" / "lastz auto engine daemon.py").read_text(encoding="utf-8")
        hub_src = (PROJECT_ROOT / "launcher" / "heinzhubweb.py").read_text(encoding="utf-8")
        html_src = (PROJECT_ROOT / "launcher" / "web" / "index.html").read_text(encoding="utf-8")
        sfc_src = (PROJECT_ROOT / "tools" / "sync farm clients.py").read_text(encoding="utf-8")

        self.assertIn("run_farm_launcher_guard", daemon_src)
        self.assertIn("launcher_guard_interval_sec", daemon_src)
        self.assertIn("_heal_farm_launchers_bg", hub_src)
        self.assertIn('action_id == "heal_farm_launchers"', hub_src)
        self.assertIn("heal_farm_launchers", html_src)
        self.assertIn("btn-heal-farm-launchers", html_src)

        bad_entity = "&md" + "ash;"
        for label, src in (("sync farm clients.py", sfc_src), ("daemon", daemon_src), ("testFarmLauncherGuard.py", Path(__file__).read_text(encoding="utf-8"))):
            self.assertNotIn("\u2014", src, f"Em dash found in {label}")
            self.assertNotIn(bad_entity, src.lower(), f"HTML mdash found in {label}")
        self.assertNotIn("_", Path(__file__).name)


if __name__ == "__main__":
    unittest.main()
