# Survival.exe & HeinZ Helper Change Log

This document tracks all runtime modifications injected into `Survival.exe` via Frida and xLua, as well as the HeinZ Helper desktop interface.

---

## Recent Updates (v7.9)

### 1. In-Game Resource Locator & Direct Navigator
- Added `navigate to resource.py` with direct game camera control.
- Supported resource types: Mine, Lumberyard, Farm, Diamonds, Windmill (electricity).
- Level selector: Level 3 through Level 8, or Any Level.
- Live march tracking: Queries `DataCenter.WorldMarchDataManager.allMarches` in real time to filter out nodes currently being gathered by active marches.
- Direct jump: Calls `GoToUtil.MoveToWorldPointAndOpen(pointIndex)` in `xlua.dll`, flying the camera to the coordinate and opening the tile in-game.

### 2. Full 16-State Bracket Explorer
- Expanded the state explorer dropdown to include all 16 states in Bracket 16 (`State 689` through `State 704`).
- Added instant open button for each state's formatted migration workbook.
- Default selection dynamically tracks the active connected server state (e.g. State 702).

### 3. Google Sheets-Styled Excel Exporters
- Replaced all raw JSON buttons and console dumps with clean openpyxl workbooks styled to match Google Sheets.
- **`Alliance Members Master.xlsx`**: Complete 14,602 player roster across all 16 states and 161 alliances, sorted by power with HQ levels and kill counts.
- **`Tech Tree Progress.xlsx`**: Detailed laboratory research tree breakdown with completion percentages and speedups.
- **`Map Intelligence Summary.xlsx`**: Structured map overview tracking all 2,180 bases, centers, and resource tiers.
- Removed obsolete third-party endpoints.

### 4. Interface & Dashboard Polish
- Streamlined interface layout with high-contrast metric indicators.
- Standardized button terminology: "Export Inventory", "Export Alliance Members", "Export Full Map Data".
- Reworded reconnaissance module to "TARGET RECONNAISSANCE & SCOUT RADAR".
- Multi-path file resolver: Automatically resolves data and scripts whether launched from the repository, launcher directory, or standalone.
- Auto-attaching engine watcher: Automatically starts the background daemon on launch if not already running.

---

## What Changed in Survival.exe

### 1. Memory & Garbage Collection
- Replaced the stock `IsNull(o)` function. Stock code called `pcall(function() return CS.UnityEngine.Object.op_Equality(o, nil) end)`, allocating a new Lua table closure on every single check. Across 80k world points, this created gigabytes of garbage. Replaced it with native `o == nil or (type(o) == "userdata" and o:Equals(nil))`. Runs 10x faster with 0 heap allocations.
- Tuned Lua GC pause and step multiplier to 200/200.
- Added incremental garbage collection (`collectgarbage("step", 60)`) on the heartbeat timer instead of letting the game run into multi-second stop-the-world GC pauses.
- When toggling entities off, unneeded game objects are destroyed right away instead of lingering in RAM.

### 2. Camera & LOD Zoom Stutter
- The game had 12,639 listeners on `EventId.ChangeCameraLod`. Every zoom tick forced Unity to call all 12k objects, causing an 89ms freeze.
- Hooked `WorldInstancedRepresentation._InstancedOnLodChanged` and `WorldBuildObject.LodChange`. If the old and new zoom level are both far out (`oldLod >= 3 and lod >= 3`), the rebuild call is skipped instantly.
- Zoom hitch dropped from 89ms to under 10ms.
- Cached tile X/Y on objects so they stop recalculating tile math every frame.
- Unlocked camera panning max velocity to 1600.0 and damp to 700.0. Snappy mouse wheel response (`zoomTime = 0.06`).
- Set camera clipping to `nearClipPlane = 20.0` and `farClipPlane = 12000.0`. This 600:1 ratio fixed shadow flickering, twitching icons, and depth fighting.

### 3. Graphics & Framerate
- Framerate unlocked to 144 FPS when focused, 30 FPS when backgrounded or alt-tabbed.
- Disabled VSync (`vSyncCount = 0`).
- Forced 2x MSAA in both QualitySettings and URP asset.
- Shadows set to 120m distance, 2 cascades, and 2048 shadowmap resolution.
- Set streaming buffers: `asyncUploadTimeSlice = 16`, `asyncUploadBufferSize = 256MB`.
- Neutralized `QualitySettingUtil.OnLowFps` so the game stops automatically dropping quality settings.

### 4. HUD Overlay & Hotkeys
- Created a custom top-center HUD bar on `m_topCanvas` layer 5 using the game's native TextMeshProUGUI font.
- Click-through enabled (`raycastTarget = false`) so it never blocks map clicks.
- Added 40Hz input poller for keyboard toggles:
  - `F1`: Master map overhaul on/off
  - `F2`: Wandering zombies on/off
  - `F3`: Resource nodes on/off
  - `F4`: Boomers and bosses on/off
  - `F5`: Player HQs on/off
  - `Home`: Show/hide top HUD bar

### 5. World Map Preload & Persistence
- Stored all discovered world points in `_PersistentWorldPointCache` (37,000+ points).
- In vanilla, opening your City destroyed the world map cache. Returning to map view made you wait for server packets. Now, returning to map view restores all 37k points instantly in under 0.5s.
- Expanded map view bounds to `[-100000, 100000]` so tiles do not despawn when panning away.
- Forced server request LOD to 0 to keep full detail cached.

### 6. Smart Culling Radius
- Essential landmarks (Radar, Cities, Alliance Centers, Bosses) are 100% global and never despawn.
- Player HQs keep a 380-tile build radius and 520-tile evict radius.
- Standard zombies keep a 170-tile build radius and 240-tile evict radius.
- Small seasonal virus buildings keep a 180-tile build radius and 250-tile evict radius.
- Idle animations disabled on far-off zombies and buildings to save CPU cycles.

---

## What's Better

1. **Framerate:** Runs at a clean 144 FPS instead of struggling around 30-45 FPS.
2. **RAM usage:** Process memory dropped from 8.3 GB down to roughly 3.9 GB.
3. **No map reloads:** Switching between City view and World view keeps all discovered tiles intact.
4. **Fast zoom:** Mouse wheel zoom no longer freezes the screen for 89ms on each step.
5. **Direct in-game navigation:** Jump immediately to any un-manned resource node without hunting manually across the map.
6. **Complete bracket intelligence:** Access rosters and power stats for 14,602 players across all 16 bracket states directly from Excel.
7. **On-the-fly toggles:** Can turn off zombies and resource nodes with F2/F3 during war, dropping active objects to ~2,400 for maximum smoothness.
8. **Background friendly:** Automatically drops to 30 FPS when you alt-tab, saving GPU power and laptop battery.
9. **No shadow flickering:** 20.0 near-plane stops ground textures and base shields from fighting.

---

## What's Worse

1. **Initial discovery spike:** Panning across completely unexplored parts of the 1000x1000 map for the first time sends bursts of server packets. Frame pacing can dip briefly while parsing hundreds of incoming tiles.
2. **RAM is still ~4 GB:** While half of vanilla's 8.3 GB leak, caching 37k points in Lua memory means it will not drop below ~3.5 GB. Machines with 8 GB total RAM need to keep pagefile enabled.
3. **Frida dependency:** Requires Python and `frida` installed on the host machine. If antivirus flags Frida DLL injection, an exclusion is required.
4. **Game updates:** If the developers recompile `xlua.dll` or rename core Lua managers (`WorldPointManager`, `SceneManager`), the hook offsets or table lookups will need a quick update.

---

## What We Can Improve On

- [ ] **Config file for hotkeys:** Move keybindings out of Lua code into an external `config.json` so users can change F1-F5 without touching code.
- [ ] **HUD positioning:** Add a drag handle or settings toggle to move the HUD bar for multi-monitor or ultra-wide setups.
- [ ] **Direct C++ hook DLL:** Build a native proxy DLL (e.g. `version.dll` or `d3d11.dll`) to load the Lua payload directly on startup, dropping the need for Python and Frida altogether.
- [ ] **Smarter packet throttler:** Spread initial tile discovery over 4-5 frames during high-speed map dragging to eliminate the small initial parsing dip.
- [ ] **Auto-reconnect watcher:** Make the background daemon automatically re-hook if the game disconnects and reloads the Unity scene without closing `Survival.exe`.
