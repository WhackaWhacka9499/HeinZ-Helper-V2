"""Offline unit test suite for `tools/game engine manager.py`.

Exercises:
1. Path resolution (env override, source checkout, simulated frozen portable vs LocalAppData).
2. Manifest path-traversal & malformed-entry rejection (`../evil.exe`, `/abs/path`, `C:\\bad`, etc.).
3. Differential CDN download against a local `http.server` mock CDN:
   - Full initial download + MD5 verification + metadata & version persistence
   - Zero-request skip on second run
   - Incremental 1-file update when version bumps
   - Retry on transient corruption & failure reporting on persistent MD5 mismatch
   - Cooperative `cancel_event` cancellation (pre-set and mid-download)
4. `import_local_engine` mirroring a synthetic local Last Z install, skipping custom EXEs /
   alt `*_Data` / `_heinz_backup`, resetting master `app.info` & `globalgamemanagers` to `LastZ`
   without mutating the source install.
5. `ensure_account_slot` provisioning lightweight isolated `Hz01Z` (`Hz01Game.exe`) &
   `Hz02Z` (`Hz02Game.exe`) slots with private identity files, shared heavy assets/junctions,
   and post-update resync.
6. Static hygiene guardrails (zero underscores in filenames, zero em dashes, zero forbidden terms).
"""

from __future__ import annotations

import hashlib
import http.server
import importlib.util
import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANAGER_PATH = PROJECT_ROOT / "tools" / "game engine manager.py"


def _load_manager():
    spec = importlib.util.spec_from_file_location("test_game_engine_manager_mod", str(MANAGER_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load {MANAGER_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_globalgamemanagers(profile: str = "LastZ", extra: bytes = b"") -> bytes:
    """Create a realistic synthetic Unity globalgamemanagers binary with ReadyGo record."""
    header = b"UNITY_GGM_HDR\x00\x00\x00" + (b"\x11" * 128)
    record = b"\x07\x00\x00\x00ReadyGo\x00\x05\x00\x00\x00" + profile.encode("ascii") + b"\x00\x00\x00"
    trailer = b"EXTRA_DATA:" + extra + (b"\x22" * 256)
    return header + record + trailer


def _md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest().lower()


def _build_synthetic_game_files(version: str = "581", profile: str = "LastZ") -> dict[str, bytes]:
    return {
        "Survival.exe": b"MZ_SURVIVAL_EXE_" + version.encode("ascii") + (b"\x00" * 512),
        "GameAssembly.dll": b"MZ_GAME_ASSEMBLY_" + version.encode("ascii") + (b"\xaa" * 2048),
        "UnityPlayer.dll": b"MZ_UNITY_PLAYER_" + (b"\xbb" * 1024),
        "baselib.dll": b"MZ_BASELIB_" + (b"\xcc" * 256),
        "UnityCrashHandler64.exe": b"MZ_CRASH_HANDLER_" + (b"\xdd" * 256),
        "config/Game_version.txt": version.encode("utf-8"),
        "LastZ_BurstDebugInformation_DoNotShip/burst.txt": b"burst_debug_payload",
        "Survival_Data/app.info": f"ReadyGo\n{profile}".encode("utf-8"),
        "Survival_Data/globalgamemanagers": _make_globalgamemanagers(profile, extra=version.encode("ascii")),
        "Survival_Data/boot.config": b"gfx-enable-gfx-jobs=1\n",
        "Survival_Data/level0": b"UNITY_LEVEL0_BYTES",
        "Survival_Data/resources.assets": b"RESOURCES_ASSETS_" + (b"\xee" * 1024),
        "Survival_Data/resources.assets.resS": b"RESOURCES_RESS_" + (b"\xff" * 1024),
        "Survival_Data/ScriptingAssemblies.json": b'{"names":["Assembly-CSharp.dll"]}',
        "Survival_Data/StreamingAssets/bundle 1.dat": b"STREAMING_BUNDLE_WITH_SPACE_IN_NAME",
        "Survival_Data/il2cpp_data/Metadata/global-metadata.dat": b"IL2CPP_META_BYTES",
        "Survival_Data/Plugins/x86_64/xlua.dll": b"XLUA_PLUGIN_BYTES",
        "Survival_Data/Resources/unity default resources": b"UNITY_RES_BYTES",
    }


def _write_file_map(base_dir: Path, file_map: dict[str, bytes]) -> None:
    for rel, content in file_map.items():
        fp = base_dir / Path(*rel.split("/"))
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_bytes(content)


class _MockCdnServer:
    """In-process threaded HTTP server simulating ReadyGo's version, manifest, and CDN endpoints."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.version = "581"
        self.files: dict[str, bytes] = {}
        self.custom_manifest: list | None = None
        self.cdn_requests: list[str] = []
        self.range_requests: list[str] = []
        self.support_ranges: bool = True
        self.corrupt_once: set[str] = set()
        self.corrupt_always: set[str] = set()
        self.per_file_delay: float = 0.0

        server_ref = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args) -> None:
                return

            def do_GET(self) -> None:
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path

                if path == "/version":
                    with server_ref.lock:
                        payload = server_ref.version.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return

                if path == "/manifest":
                    with server_ref.lock:
                        if server_ref.custom_manifest is not None:
                            manifest = server_ref.custom_manifest
                        else:
                            manifest = [
                                [rel, _md5_bytes(data), len(data)]
                                for rel, data in sorted(server_ref.files.items())
                            ]
                    payload = json.dumps(manifest).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return

                prefix = "/cdn/"
                if path.startswith(prefix):
                    rest = path[len(prefix) :]
                    parts = rest.split("/", 1)
                    if len(parts) == 2:
                        ver_folder = urllib.parse.unquote(parts[0])
                        rel_path = urllib.parse.unquote(parts[1])
                        with server_ref.lock:
                            expected_folder = f"Game_{server_ref.version}"
                            server_ref.cdn_requests.append(rel_path)
                            data = server_ref.files.get(rel_path) if ver_folder == expected_folder else None
                            delay = server_ref.per_file_delay
                            corrupt = False
                            if rel_path in server_ref.corrupt_always:
                                corrupt = True
                            elif rel_path in server_ref.corrupt_once:
                                server_ref.corrupt_once.remove(rel_path)
                                corrupt = True
                        if delay > 0:
                            import time
                            time.sleep(delay)
                        if data is not None:
                            out = (b"X" * len(data)) if corrupt else data
                            rng_hdr = self.headers.get("Range", "")
                            with server_ref.lock:
                                allow_rng = server_ref.support_ranges
                            if allow_rng and rng_hdr.startswith("bytes="):
                                spec = rng_hdr[len("bytes=") :].split(",", 1)[0].strip()
                                s_str, e_str = spec.split("-", 1)
                                start = int(s_str) if s_str else 0
                                end = int(e_str) if e_str else len(out) - 1
                                end = min(end, len(out) - 1)
                                chunk = out[start : end + 1]
                                with server_ref.lock:
                                    server_ref.range_requests.append(f"{rel_path}:{start}-{end}")
                                self.send_response(206)
                                self.send_header("Content-Type", "application/octet-stream")
                                self.send_header("Accept-Ranges", "bytes")
                                self.send_header("Content-Range", f"bytes {start}-{end}/{len(out)}")
                                self.send_header("Content-Length", str(len(chunk)))
                                self.end_headers()
                                self.wfile.write(chunk)
                                return
                            self.send_response(200)
                            self.send_header("Content-Type", "application/octet-stream")
                            if allow_rng:
                                self.send_header("Accept-Ranges", "bytes")
                            self.send_header("Content-Length", str(len(out)))
                            self.end_headers()
                            self.wfile.write(out)
                            return

                self.send_response(404)
                self.end_headers()

        class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
            daemon_threads = True
            allow_reuse_address = True

        self._httpd = ThreadingServer(("127.0.0.1", 0), Handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    @property
    def version_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/version"

    @property
    def manifest_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/manifest"

    @property
    def cdn_base(self) -> str:
        return f"http://127.0.0.1:{self.port}/cdn"

    def reset_requests(self) -> None:
        with self.lock:
            self.cdn_requests.clear()
            self.range_requests.clear()

    def close(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=2.0)


class TestGameEngineManager(unittest.TestCase):
    """Comprehensive offline verification for `tools/game engine manager.py`."""

    def setUp(self) -> None:
        self.gem = _load_manager()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.engine_root = self.root / "engine root"
        self.cdn = _MockCdnServer()

    def tearDown(self) -> None:
        self.cdn.close()
        # Cleanly remove any NTFS junctions inside temp dir before TemporaryDirectory cleanup
        if self.root.exists():
            for child in list(self.root.iterdir()):
                try:
                    self.gem._remove_dir_or_junction(child)
                except OSError:
                    pass
        self.tmp.cleanup()

    def test_path_resolution_and_validation_helpers(self) -> None:
        """Verify resolve_engine_root env override, frozen fallback, version reader, and game dir validation."""
        custom_env = str(self.root / "env engine")
        with mock.patch.dict(os.environ, {"HEINZ_ENGINE_DIR": custom_env}, clear=False):
            self.assertEqual(self.gem.resolve_engine_root(), Path(custom_env))
            self.assertEqual(self.gem.resolve_engine_game_dir(), Path(custom_env) / "Game")
            self.assertEqual(self.gem.resolve_accounts_root(), Path(custom_env) / "accounts")

        with mock.patch.dict(os.environ, {"HEINZ_ENGINE_DIR": ""}, clear=False):
            with mock.patch.object(sys, "frozen", False, create=True):
                self.assertEqual(self.gem.resolve_engine_root(), PROJECT_ROOT / "engine")

            fake_exe_dir = self.root / "frozen app"
            fake_exe_dir.mkdir(parents=True)
            fake_exe = fake_exe_dir / "HeinZ.exe"
            with (
                mock.patch.object(sys, "frozen", True, create=True),
                mock.patch.object(sys, "executable", str(fake_exe)),
            ):
                self.assertEqual(self.gem.resolve_engine_root(), fake_exe_dir / "engine")

                with (
                    mock.patch.object(self.gem, "_is_writable_dir", return_value=False),
                    mock.patch.dict(os.environ, {"LOCALAPPDATA": str(self.root / "LocalApp")}, clear=False),
                ):
                    self.assertEqual(
                        self.gem.resolve_engine_root(),
                        self.root / "LocalApp" / "HeinZ V2" / "engine",
                    )

        # Validation helpers
        gd = self.root / "empty game"
        gd.mkdir()
        self.assertFalse(self.gem.is_valid_game_dir(gd))
        self.assertEqual(self.gem.read_engine_version(gd), "")

        (gd / "Survival.exe").write_bytes(b"")
        (gd / "GameAssembly.dll").write_bytes(b"x")
        (gd / "Survival_Data").mkdir()
        (gd / "Survival_Data" / "globalgamemanagers").write_bytes(b"x")
        self.assertFalse(self.gem.is_valid_game_dir(gd))  # 0-byte Survival.exe rejected

        (gd / "Survival.exe").write_bytes(b"exe")
        self.assertTrue(self.gem.is_valid_game_dir(gd))

        (gd / "config").mkdir()
        (gd / "config" / "Game_version.txt").write_text("  582 \r\n", encoding="utf-8")
        self.assertEqual(self.gem.read_engine_version(gd), "582")

        # URL encoding preserves slashes and safely encodes spaces
        url = self.gem.build_cdn_file_url(
            "https://cdn.example.com/hotupdate/",
            "582",
            "Survival_Data/StreamingAssets/bundle 1.dat",
        )
        self.assertEqual(
            url,
            "https://cdn.example.com/hotupdate/Game_582/Survival_Data/StreamingAssets/bundle%201.dat",
        )

        # detect_existing_local_installs finds valid local install and excludes managed engine_game_dir
        fake_local = self.root / "MockLocalAppData"
        fake_vanilla = fake_local / "Last Z" / "Game"
        _write_file_map(fake_vanilla, _build_synthetic_game_files(version="581", profile="LastZ"))
        with (
            mock.patch.dict(os.environ, {"LOCALAPPDATA": str(fake_local)}, clear=False),
            mock.patch.object(self.gem, "_load_client_discovery_module", return_value=None),
        ):
            found = self.gem.detect_existing_local_installs(engine_root=self.engine_root)
            found_dirs = [str(Path(item["game_dir"]).resolve()).lower() for item in found]
            self.assertIn(str(fake_vanilla.resolve()).lower(), found_dirs)

            # When engine_root points at fake_local/Last Z, its Game/ dir is excluded
            excluded = self.gem.detect_existing_local_installs(engine_root=fake_local / "Last Z")
            excl_dirs = [str(Path(item["game_dir"]).resolve()).lower() for item in excluded]
            self.assertNotIn(str(fake_vanilla.resolve()).lower(), excl_dirs)

    def test_manifest_path_traversal_and_malformed_entries_rejected(self) -> None:
        """Reject ../evil.exe, /abs/path, C:\\bad, backslashes, null bytes, and invalid MD5/size."""
        good_md5 = _md5_bytes(b"abc")
        bad_paths = [
            "../evil.exe",
            "Survival_Data/../../evil.dll",
            "/abs/path",
            r"C:\bad",
            "C:/bad/file.dll",
            r"Survival_Data\sub.dll",
            "null\x00byte.dll",
            "./dot.dll",
            "a//b.dll",
            "",
        ]
        for bad in bad_paths:
            self.cdn.custom_manifest = [[bad, good_md5, 3]]
            with self.assertRaises(ValueError, msg=f"Should reject unsafe path: {bad!r}"):
                self.gem.fetch_remote_manifest(manifest_url=self.cdn.manifest_url)

        # Invalid MD5 rejected
        self.cdn.custom_manifest = [["Survival.exe", "not-a-valid-md5", 3]]
        with self.assertRaises(ValueError):
            self.gem.fetch_remote_manifest(manifest_url=self.cdn.manifest_url)

        # Negative size rejected
        self.cdn.custom_manifest = [["Survival.exe", good_md5, -1]]
        with self.assertRaises(ValueError):
            self.gem.fetch_remote_manifest(manifest_url=self.cdn.manifest_url)

        # Ensure download_or_update_engine also refuses path traversal without writing outside root
        self.cdn.custom_manifest = [["../escaped.exe", good_md5, 3]]
        with self.assertRaises(ValueError):
            self.gem.download_or_update_engine(
                engine_root=self.engine_root,
                version_url=self.cdn.version_url,
                manifest_url=self.cdn.manifest_url,
                cdn_base=self.cdn.cdn_base,
            )
        self.assertFalse((self.engine_root / "escaped.exe").exists())

    def test_differential_cdn_download_skip_update_retry_and_cancel(self) -> None:
        """Verify full download, skip on re-run, 1-file update, MD5 retry, corruption failure, and cancellation."""
        self.cdn.version = "581"
        self.cdn.files = _build_synthetic_game_files(version="581", profile="LastZ")
        file_count = len(self.cdn.files)

        progress_events: list[dict] = []
        res1 = self.gem.download_or_update_engine(
            engine_root=self.engine_root,
            progress_cb=progress_events.append,
            max_workers=4,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
        )
        self.assertTrue(res1["ok"], res1)
        self.assertFalse(res1["cancelled"])
        self.assertEqual(res1["version"], "581")
        self.assertEqual(res1["downloaded_files"], file_count)
        self.assertEqual(res1["skipped_files"], 0)
        self.assertEqual(res1["failed_files"], [])
        self.assertGreater(res1["downloaded_bytes"], 0)

        game_dir = Path(res1["engine_game_dir"])
        self.assertTrue(self.gem.is_valid_game_dir(game_dir))
        self.assertEqual(self.gem.read_engine_version(game_dir), "581")
        self.assertTrue((game_dir / "Survival_Data" / "StreamingAssets" / "bundle 1.dat").is_file())
        self.assertTrue((self.engine_root / "engine metadata.json").is_file())

        # Progress callback shape verification
        self.assertTrue(progress_events)
        required_prog_keys = {
            "stage",
            "done_files",
            "total_files",
            "done_bytes",
            "total_bytes",
            "pct",
            "current_file",
            "speed_mbps",
        }
        for ev in progress_events:
            self.assertTrue(required_prog_keys.issubset(ev.keys()))
        self.assertEqual(progress_events[-1]["stage"], "done")

        # Status check shows installed & up to date
        st_same = self.gem.get_engine_status(
            check_remote=True,
            engine_root=self.engine_root,
            version_url=self.cdn.version_url,
        )
        self.assertTrue(st_same["ok"])
        self.assertTrue(st_same["installed"])
        self.assertEqual(st_same["local_version"], "581")
        self.assertEqual(st_same["remote_version"], "581")
        self.assertFalse(st_same["update_available"])
        self.assertEqual(st_same["remote_error"], "")

        # Re-run with identical manifest skips every file and makes ZERO CDN file downloads
        self.cdn.reset_requests()
        res2 = self.gem.download_or_update_engine(
            engine_root=self.engine_root,
            max_workers=4,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
        )
        self.assertTrue(res2["ok"])
        self.assertEqual(res2["downloaded_files"], 0)
        self.assertEqual(res2["skipped_files"], file_count)
        self.assertEqual(self.cdn.cdn_requests, [])

        # Update when exactly 1 file changes + remote version bumps to 582
        self.cdn.version = "582"
        new_asm = b"MZ_GAME_ASSEMBLY_582_PATCHED" + (b"\x55" * 2048)
        self.cdn.files["GameAssembly.dll"] = new_asm
        # Remove config/Game_version.txt from manifest so we also verify automatic version txt update
        self.cdn.files.pop("config/Game_version.txt", None)
        expected_manifest_len = len(self.cdn.files)

        st_upd = self.gem.get_engine_status(
            check_remote=True,
            engine_root=self.engine_root,
            version_url=self.cdn.version_url,
        )
        self.assertTrue(st_upd["update_available"])
        self.assertEqual(st_upd["local_version"], "581")
        self.assertEqual(st_upd["remote_version"], "582")

        # Inject a single transient MD5 corruption to verify automatic retry succeeds
        self.cdn.reset_requests()
        self.cdn.corrupt_once.add("GameAssembly.dll")
        res3 = self.gem.download_or_update_engine(
            engine_root=self.engine_root,
            max_workers=4,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
        )
        self.assertTrue(res3["ok"], res3)
        self.assertEqual(res3["version"], "582")
        self.assertEqual(res3["downloaded_files"], 1)
        self.assertEqual(res3["skipped_files"], expected_manifest_len - 1)
        self.assertEqual((game_dir / "GameAssembly.dll").read_bytes(), new_asm)
        self.assertEqual(self.gem.read_engine_version(game_dir), "582")
        self.assertEqual(self.cdn.cdn_requests.count("GameAssembly.dll"), 2)

        # Persistent corruption fails cleanly after 3 retries and leaves no .part files
        self.cdn.files["baselib.dll"] = b"NEW_BASELIB_CONTENT_583"
        self.cdn.corrupt_always.add("baselib.dll")
        res_fail = self.gem.download_or_update_engine(
            engine_root=self.engine_root,
            max_workers=2,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
        )
        self.assertFalse(res_fail["ok"])
        self.assertEqual(len(res_fail["failed_files"]), 1)
        self.assertEqual(res_fail["failed_files"][0]["file"], "baselib.dll")
        self.assertEqual(list(game_dir.rglob("*.part")), [])
        self.cdn.corrupt_always.clear()

        # Pre-set cancel_event stops immediately
        fresh_engine = self.root / "cancel engine"
        pre_cancel = threading.Event()
        pre_cancel.set()
        res_pre = self.gem.download_or_update_engine(
            engine_root=fresh_engine,
            cancel_event=pre_cancel,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
        )
        self.assertFalse(res_pre["ok"])
        self.assertTrue(res_pre["cancelled"])
        self.assertEqual(res_pre["downloaded_files"], 0)

        # Mid-download cancellation stops cleanly with zero leftover .part files
        mid_cancel = threading.Event()
        self.cdn.per_file_delay = 0.03

        def _cancel_on_first_file(ev: dict) -> None:
            if ev.get("stage") == "downloading" and ev.get("done_files", 0) >= 1:
                mid_cancel.set()

        res_mid = self.gem.download_or_update_engine(
            engine_root=fresh_engine,
            progress_cb=_cancel_on_first_file,
            cancel_event=mid_cancel,
            max_workers=1,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
        )
        self.cdn.per_file_delay = 0.0
        self.assertFalse(res_mid["ok"])
        self.assertTrue(res_mid["cancelled"])
        self.assertLess(res_mid["downloaded_files"], expected_manifest_len)
        self.assertEqual(list(fresh_engine.rglob("*.part")), [])

    def test_import_local_engine_resets_identity_and_filters_extras(self) -> None:
        """Import a FarmZ local install, skip custom EXEs/alt *_Data/_heinz_backup, and reset master to LastZ."""
        local_src = self.root / "LocalLastZ" / "Game"
        src_files = _build_synthetic_game_files(version="581", profile="FarmZ")
        _write_file_map(local_src, src_files)

        # Plant unwanted artifacts that must be excluded during clean import
        (local_src / "FarmGame.exe").write_bytes(b"CUSTOM_FARM_EXE")
        (local_src / "Alt3Game.exe").write_bytes(b"CUSTOM_ALT3_EXE")
        (local_src / "FarmGame_Data").mkdir()
        (local_src / "FarmGame_Data" / "junk.txt").write_text("junk", encoding="utf-8")
        (local_src / "Survival_Data" / "_heinz_backup").mkdir()
        (local_src / "Survival_Data" / "_heinz_backup" / "globalgamemanagers.orig").write_bytes(b"ORIG")

        progress_events: list[dict] = []
        res = self.gem.import_local_engine(
            local_src,
            engine_root=self.engine_root,
            progress_cb=progress_events.append,
        )
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["local_version"], "581")
        self.assertEqual(res["copied_files"], len(src_files))
        self.assertGreater(res["total_bytes"], 0)
        self.assertTrue(progress_events)
        self.assertEqual(progress_events[-1]["stage"], "done")

        dst_dir = Path(res["engine_game_dir"])
        self.assertTrue(self.gem.is_valid_game_dir(dst_dir))
        self.assertFalse((dst_dir / "FarmGame.exe").exists())
        self.assertFalse((dst_dir / "Alt3Game.exe").exists())
        self.assertFalse((dst_dir / "FarmGame_Data").exists())
        self.assertFalse((dst_dir / "Survival_Data" / "_heinz_backup").exists())

        # Master identity was cleanly reset to LastZ
        self.assertEqual((dst_dir / "Survival_Data" / "app.info").read_text(encoding="utf-8"), "ReadyGo\nLastZ")
        master_ggm = (dst_dir / "Survival_Data" / "globalgamemanagers").read_bytes()
        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00LastZ", master_ggm)
        self.assertNotIn(b"ReadyGo\x00\x05\x00\x00\x00FarmZ", master_ggm)

        # Original source install was NOT mutated
        self.assertEqual((local_src / "Survival_Data" / "app.info").read_text(encoding="utf-8"), "ReadyGo\nFarmZ")
        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00FarmZ", (local_src / "Survival_Data" / "globalgamemanagers").read_bytes())

        # Metadata file recorded
        meta = json.loads((self.engine_root / "engine metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["version"], "581")
        self.assertEqual(meta["file_count"], len(src_files))
        self.assertEqual(meta["total_bytes"], res["total_bytes"])

        # Invalid source returns ok=False
        bad_res = self.gem.import_local_engine(self.root / "nonexistent", engine_root=self.engine_root)
        self.assertFalse(bad_res["ok"])

    def test_ensure_account_slot_isolation_and_shared_heavy_assets(self) -> None:
        """Provision Hz01Z & Hz02Z slots with private app.info/globalgamemanagers and shared heavy files."""
        master_dir = self.gem.resolve_engine_game_dir(self.engine_root)
        _write_file_map(master_dir, _build_synthetic_game_files(version="581", profile="LastZ"))

        slot1 = self.gem.ensure_account_slot("Hz01Z", "Hz01Game.exe", engine_root=self.engine_root)
        slot2 = self.gem.ensure_account_slot("Hz02Z", "Hz02Game.exe", engine_root=self.engine_root)

        self.assertTrue(slot1["ok"], slot1)
        self.assertTrue(slot2["ok"], slot2)
        self.assertEqual(slot1["unity_profile"], "Hz01Z")
        self.assertEqual(slot2["unity_profile"], "Hz02Z")
        self.assertEqual(slot1["version"], "581")
        self.assertEqual(slot2["version"], "581")
        self.assertIn(slot1["shared_mode"], ("junction_hardlink", "copy"))

        gd1 = Path(slot1["game_dir"])
        gd2 = Path(slot2["game_dir"])
        self.assertTrue(Path(slot1["exe_path"]).is_file())
        self.assertTrue(Path(slot2["exe_path"]).is_file())
        self.assertEqual(Path(slot1["exe_path"]).name, "Hz01Game.exe")
        self.assertEqual(Path(slot2["exe_path"]).name, "Hz02Game.exe")

        # Verify <ExeStem>_Data junctions point to each slot's own Survival_Data
        self.assertTrue((gd1 / "Hz01Game_Data").exists())
        self.assertTrue((gd2 / "Hz02Game_Data").exists())
        self.assertEqual((gd1 / "Hz01Game_Data").resolve(), (gd1 / "Survival_Data").resolve())
        self.assertEqual((gd2 / "Hz02Game_Data").resolve(), (gd2 / "Survival_Data").resolve())

        # Verify isolated Unity identity in each slot while master remains LastZ
        master_app = master_dir / "Survival_Data" / "app.info"
        master_ggm = master_dir / "Survival_Data" / "globalgamemanagers"
        app1 = gd1 / "Survival_Data" / "app.info"
        ggm1 = gd1 / "Survival_Data" / "globalgamemanagers"
        app2 = gd2 / "Survival_Data" / "app.info"
        ggm2 = gd2 / "Survival_Data" / "globalgamemanagers"

        self.assertEqual(master_app.read_text(encoding="utf-8"), "ReadyGo\nLastZ")
        self.assertEqual(app1.read_text(encoding="utf-8"), "ReadyGo\nHz01Z")
        self.assertEqual(app2.read_text(encoding="utf-8"), "ReadyGo\nHz02Z")

        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00LastZ", master_ggm.read_bytes())
        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00Hz01Z", ggm1.read_bytes())
        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00Hz02Z", ggm2.read_bytes())

        # Private files MUST NOT be hardlinked to master or to each other
        self.assertFalse(os.path.samefile(master_app, app1))
        self.assertFalse(os.path.samefile(master_app, app2))
        self.assertFalse(os.path.samefile(app1, app2))
        self.assertFalse(os.path.samefile(master_ggm, ggm1))
        self.assertFalse(os.path.samefile(master_ggm, ggm2))
        self.assertFalse(os.path.samefile(ggm1, ggm2))

        # Mutating Hz01Z's private files must NOT affect master or Hz02Z
        app1.write_text("MUTATED_CHECK", encoding="utf-8")
        self.assertEqual(master_app.read_text(encoding="utf-8"), "ReadyGo\nLastZ")
        self.assertEqual(app2.read_text(encoding="utf-8"), "ReadyGo\nHz02Z")

        # Heavy read-only files share via hardlink & subdirs via junction on NTFS
        if slot1["shared_mode"] == "junction_hardlink":
            self.assertTrue(os.path.samefile(master_dir / "GameAssembly.dll", gd1 / "GameAssembly.dll"))
            self.assertTrue(os.path.samefile(master_dir / "UnityPlayer.dll", gd1 / "UnityPlayer.dll"))
            self.assertTrue(
                os.path.samefile(
                    master_dir / "Survival_Data" / "resources.assets",
                    gd1 / "Survival_Data" / "resources.assets",
                )
            )
            self.assertTrue(self.gem._is_reparse_or_junction(gd1 / "Survival_Data" / "StreamingAssets"))
            self.assertEqual(
                (gd1 / "Survival_Data" / "StreamingAssets").resolve(),
                (master_dir / "Survival_Data" / "StreamingAssets").resolve(),
            )

        # Updating master atomically + calling ensure_account_slot resyncs Hz01Z cleanly
        updated_asm = b"MZ_GAME_ASSEMBLY_582_NEW" + (b"\x99" * 2048)
        self.gem._atomic_write_bytes(master_dir / "GameAssembly.dll", updated_asm)
        self.gem._atomic_write_bytes(
            master_ggm,
            _make_globalgamemanagers("LastZ", extra=b"582_UPDATED"),
        )
        self.gem._atomic_write_text(master_dir / "config" / "Game_version.txt", "582")

        resynced = self.gem.ensure_account_slot("Hz01Z", "Hz01Game.exe", engine_root=self.engine_root)
        self.assertTrue(resynced["ok"])
        self.assertEqual(resynced["version"], "582")
        self.assertEqual((gd1 / "GameAssembly.dll").read_bytes(), updated_asm)
        self.assertEqual(app1.read_text(encoding="utf-8"), "ReadyGo\nHz01Z")
        ggm1_after = ggm1.read_bytes()
        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00Hz01Z", ggm1_after)
        self.assertIn(b"582_UPDATED", ggm1_after)
        self.assertIn(b"ReadyGo\x00\x05\x00\x00\x00LastZ", master_ggm.read_bytes())

        # Validation errors on bad inputs
        for bad_prof in ("Hz1Z", "Hz001Z", "../aZ", "Hz-1Z", ""):
            with self.assertRaises(ValueError):
                self.gem.ensure_account_slot(bad_prof, "Hz01Game.exe", engine_root=self.engine_root)
        for bad_exe in ("Hz01Game.bat", "../evil.exe", ".exe", ""):
            with self.assertRaises(ValueError):
                self.gem.ensure_account_slot("Hz01Z", bad_exe, engine_root=self.engine_root)

    def test_parallel_range_chunked_download_and_200_fallback(self) -> None:
        """Verify parallel HTTP 206 Range chunked downloads for big files and seamless 200 OK fallback."""
        big_payload = bytes((i * 31) & 0xFF for i in range(420_000))
        files = _build_synthetic_game_files(version="583", profile="LastZ")
        files["GameAssembly.dll"] = big_payload
        self.cdn.version = "583"
        self.cdn.files = files
        self.cdn.support_ranges = True
        self.cdn.reset_requests()

        res = self.gem.download_or_update_engine(
            engine_root=self.engine_root,
            max_workers=4,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
            range_threshold_bytes=100_000,
            range_streams=4,
        )
        self.assertTrue(res["ok"], res)
        self.assertEqual((Path(res["engine_game_dir"]) / "GameAssembly.dll").read_bytes(), big_payload)
        ga_ranges = [r for r in self.cdn.range_requests if r.startswith("GameAssembly.dll:")]
        self.assertGreaterEqual(len(ga_ranges), 2, f"Expected parallel 206 Range slices, got {ga_ranges}")

        # Verify zero-waste 200 OK fallback when a server ignores Range headers
        fallback_root = self.root / "fallback engine"
        self.cdn.support_ranges = False
        self.cdn.reset_requests()
        res_fb = self.gem.download_or_update_engine(
            engine_root=fallback_root,
            max_workers=4,
            version_url=self.cdn.version_url,
            manifest_url=self.cdn.manifest_url,
            cdn_base=self.cdn.cdn_base,
            range_threshold_bytes=100_000,
            range_streams=4,
        )
        self.assertTrue(res_fb["ok"], res_fb)
        self.assertEqual((Path(res_fb["engine_game_dir"]) / "GameAssembly.dll").read_bytes(), big_payload)
        self.assertEqual(self.cdn.cdn_requests.count("GameAssembly.dll"), 1)
        self.assertEqual(self.cdn.range_requests, [])

    def test_ensure_account_slot_skips_redundant_ggm_patch_when_unchanged(self) -> None:
        """Idempotent re-runs of ensure_account_slot must not re-patch globalgamemanagers."""
        src_dir = self.root / "local source skip"
        for rel, data in _build_synthetic_game_files(version="585", profile="LastZ").items():
            fp = src_dir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_bytes(data)

        self.gem.import_local_engine(src_dir, engine_root=self.engine_root)
        slot1 = self.gem.ensure_account_slot("Hz01Z", "Hz01Game.exe", engine_root=self.engine_root)
        self.assertTrue(slot1["ok"], slot1)

        with mock.patch.object(self.gem, "patch_unity_identity", wraps=self.gem.patch_unity_identity) as mock_patch:
            slot2 = self.gem.ensure_account_slot("Hz01Z", "Hz01Game.exe", engine_root=self.engine_root)
        self.assertTrue(slot2["ok"], slot2)
        mock_patch.assert_not_called()

    def test_download_ranged_failure_rolls_back_bytes_and_recovers_single_stream(self) -> None:
        """Attempt 1 ranged failure rolls back done_bytes and recovers cleanly via single stream."""
        big_payload = bytes((i * 17) & 0xFF for i in range(320_000))
        files = _build_synthetic_game_files(version="586", profile="LastZ")
        files["GameAssembly.dll"] = big_payload
        self.cdn.version = "586"
        self.cdn.files = files
        self.cdn.support_ranges = True
        self.cdn.reset_requests()

        orig_open = open
        slice_fail_state = {"done": False}

        def _fail_once_ranged_open(file_arg, mode="r", *args, **kwargs):
            if mode == "r+b" and str(file_arg).endswith(".part") and not slice_fail_state["done"]:
                slice_fail_state["done"] = True
                raise OSError("Simulated slice IO error")
            return orig_open(file_arg, mode, *args, **kwargs)

        events: list[dict] = []
        with mock.patch("builtins.open", side_effect=_fail_once_ranged_open):
            res = self.gem.download_or_update_engine(
                engine_root=self.engine_root,
                max_workers=2,
                progress_cb=lambda ev: events.append(dict(ev)),
                version_url=self.cdn.version_url,
                manifest_url=self.cdn.manifest_url,
                cdn_base=self.cdn.cdn_base,
                range_threshold_bytes=100_000,
                range_streams=4,
            )

        self.assertTrue(res["ok"], res)
        self.assertTrue(slice_fail_state["done"])
        game_dir = Path(res["engine_game_dir"])
        self.assertEqual((game_dir / "GameAssembly.dll").read_bytes(), big_payload)
        self.assertEqual(list(game_dir.rglob("*.part")), [])
        done_evs = [e for e in events if e.get("stage") == "done"]
        self.assertTrue(done_evs)
        expected_total = sum(len(v) for v in files.values())
        self.assertEqual(done_evs[-1]["done_bytes"], expected_total)

    def test_import_local_engine_throttles_progress_and_handles_junctions(self) -> None:
        """Verify import_local_engine throttles rapid copying progress callbacks while always emitting done."""
        src_dir = self.root / "local source throttle"
        base_files = _build_synthetic_game_files(version="587", profile="LastZ")
        for i in range(40):
            base_files[f"StreamingAssets/chunk_{i:02d}.bin"] = b"DATA" * 8
        for rel, data in base_files.items():
            fp = src_dir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_bytes(data)

        # Create a stale junction in dst_dir prior to import to ensure safe rmdir without deleting source target
        stale_target = self.root / "stale junction target"
        stale_target.mkdir(parents=True, exist_ok=True)
        (stale_target / "keep.txt").write_text("preserve", encoding="utf-8")
        dst_game = self.engine_root / "game"
        dst_game.mkdir(parents=True, exist_ok=True)
        stale_link = dst_game / "OldLinkDir"
        subprocess.run(["cmd", "/c", "mklink", "/j", str(stale_link), str(stale_target)], capture_output=True)

        events: list[dict] = []
        res = self.gem.import_local_engine(
            src_dir,
            engine_root=self.engine_root,
            progress_cb=lambda ev: events.append(dict(ev)),
        )
        self.assertTrue(res["ok"], res)
        self.assertTrue((stale_target / "keep.txt").is_file())
        self.assertFalse(stale_link.exists())
        copy_evs = [e for e in events if e.get("stage") == "copying"]
        done_evs = [e for e in events if e.get("stage") == "done"]
        self.assertEqual(len(done_evs), 1)
        self.assertLess(len(copy_evs), len(base_files), f"Expected throttled copying events, got {len(copy_evs)}")

    def test_static_hygiene_and_strict_rules(self) -> None:
        """Enforce zero underscores in new filenames, zero em dashes, and zero forbidden terms."""
        targets = [
            MANAGER_PATH,
            Path(__file__).resolve(),
        ]
        bad_entity = "&md" + "ash;"
        forbidden_1 = ("comm" + "ander").lower()
        forbidden_2 = ("cour" + "age badges").lower()

        for path in targets:
            self.assertNotIn("_", path.name, f"Underscore forbidden in filename: {path.name}")
            src = path.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", src, f"Em dash found in {path.name}")
            self.assertNotIn(bad_entity, src.lower(), f"HTML mdash entity found in {path.name}")
            self.assertNotIn(forbidden_1, src.lower(), f"Forbidden term found in {path.name}")
            self.assertNotIn(forbidden_2, src.lower(), f"Forbidden term found in {path.name}")


if __name__ == "__main__":
    unittest.main()
