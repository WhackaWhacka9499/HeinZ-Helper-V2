# HeinZ Helper V2

Standalone Windows launcher, performance optimizer, multi-account manager, live translator, and map/alliance intelligence suite for Last Z PC.

## What Is Included

- `launcher/` - Desktop UI (`heinzhubweb.py`, `web/index.html`), 2-page startup popup (Page 1 Account Login -> Page 2 Unified Launcher), 18-language UI locales (`assets/locales/`), and PyInstaller build spec (`HeinZ.spec`).
- `tools/` - Built-in ReadyGo CDN game engine manager (`game engine manager.py`) with HTTP Keep-Alive pooling, parallel Range downloads for large binaries, and multi-threaded MD5 verification; isolated multi-account vault (`account launcher vault.py`); `/MT:16` fast farm sync (`sync farm clients.py`); live in-game translator (`live translator server.py`); bot automation, map radar, and Excel/CSV exporters.
- `daemon/` - Background engine guard, 180 FPS optimization daemon, and farm launcher recovery guard.
- `api/`, `listeners/`, `patches/`, `telemetry/` - Network inspection utilities, runtime patches, and diagnostics.
- `megamind/` - Indexed Last Z protocol, manager, UI, and table reference library (`megamind query.py`).
- `tests/` - 5-tier automated verification suite (`run all tests.py`).

## Quick Start (From Source)

1. Install Python 3.11+ and required packages:
   ```powershell
   pip install pywebview requests psutil openpyxl frida pyinstaller
   ```
2. Launch the desktop UI:
   ```powershell
   python launcher/heinzhubweb.py
   ```
3. Run the verification suite:
   ```powershell
   python "tests/run all tests.py"
   ```
4. Build the standalone portable Windows executable (`dist/HeinZ/HeinZ.exe`):
   ```powershell
   pyinstaller --noconfirm launcher/HeinZ.spec
   ```

## Engine & Multi-Account Flow

- **Page 1 (Login):** Account sign-in gate with zero game hooks active while signing in (supports local guest mode for development).
- **Page 2 (Launcher):** Import an existing local Last Z installation or download/update directly from ReadyGo's official CDN into `<engine>/Game`, then launch isolated accounts (`Hz01Z`..`Hz99Z`) in Pure Vanilla (zero hooks) or Enhanced (HeinZ Helper) mode.
