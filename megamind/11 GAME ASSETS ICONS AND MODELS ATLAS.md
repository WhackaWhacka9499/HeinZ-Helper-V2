# Volume 11: Extracted Game Icons, Hub UI Sprites, 3D Models, 2D Spine Skins & World Maps Atlas

> **Generated:** `2026-11-24 16:07:38 UTC` | **Indexed Entities:** **`57,525`** (`9,501` edges, `41.11 MB` SQLite) | **Sources:** `assets/icons/Icons Catalog.json`, `models/Models Catalog.json`, `models/Hero Skins Spine Catalog.csv`, `maps/Maps Catalog.json`, `maps/Maps Catalog.csv`, `launcher/assets/game_icons/manifest.json`, `megamind/raw/game_assets_icons_and_models.json`

## 1. Complete Game Assets Inventory & Storage Map

| Asset Layer | Verified Count | Disk Footprint | Root Directory | Master Catalog / Manifest | SQLite Layer(s) |
|---|---:|---:|---|---|---|
| **Extracted Game Icons (PNG)** | **17,049** PNGs (`3,827` EN / `13,222` cleaned) | `1,120.61 MB` | `assets/icons/<Season>/<Category>/` | `assets/icons/Icons Catalog.json` (+ `.csv`, `README.md`) | `game_icon` (`17,049` rows) |
| **Extracted 3D Models (GLB + OBJ)** | **493** models (`3,069` OBJs, `3,354` PNGs; incl. `28` HQ Skins, `28` Vehicle Skins) | `582.52 MB` (GLBs) | `models/<Season>/<Faction or Skin Category>/<Model>/` | `models/Models Catalog.json` (+ `.csv`, `README.md`) | `game_model` (`493` rows) |
| **Extracted 2D Spine Hero Skins** | **110** bundles (`118` atlas PNGs, `236` `.atlas.txt`/`.skel.bytes`) | `149.69 MB` | `models/<Season>/<Faction>/Hero Skins 2D Spine/` | `models/Models Catalog.json` + `models/Hero Skins Spine Catalog.csv` | `hero_skin_spine` (`110` rows) |
| **Exported World, Seasonal, Event, City & Terrain Maps (PNG)** | **499** PNGs (`5` categories, `26` subcategories, `7` season buckets; `5`x `4K` stitched, `19` decoded topology/tier maps, `87` provinces) | `314.40 MB` | `maps/<Category>/<Subcategory or Season>/` | `maps/Maps Catalog.json` (+ `.csv`, `README.md`) | `game_map` (`499` rows) |
| **HeinZ Hub UI Sprite Pack (WebP)** | **197** WebPs (`47` core + `35` hero + `115` item) | `546.1 KB` | `launcher/assets/game_icons/` | `launcher/assets/game_icons/manifest.json` | `hub_game_icon` (`47` core rows) |
| **Megamind Raw Asset Manifest** | **1** unified JSON (`603` model/skin + `499` map summary assets) | `240.2 KB` | `megamind/raw/` | `megamind/raw/game_assets_icons_and_models.json` | Indexed by `megamind/update_assets_index.py` |

### Naming & Hygiene Guarantees
- **Zero underscores (`_`)** in any folder or filename under `assets/icons/`, `models/`, and `maps/` (raw Unity sprite, prefab, texture, and bundle names remain searchable inside SQLite FTS5 `summary` & `body`).
- **Zero em dashes (`U+2014`)** anywhere in filenames, catalogs, manifests, scripts, or Megamind volumes.
- **Icon cropping & collisions:** Every PNG under `assets/icons/` is tightly cropped edge-to-edge (`alpha > 4` threshold, min `4x4` px); filename stems average `19.32` chars (`max 54`); collisions resolve by pixel area descending (`<Name>.png`, `<Name> (2).png`, ...).
- **3D model completeness (`493` models across `12` folders):** All `493` exported 3D AssetBundles (`620` scanned, `127` non-mesh skipped: `89` 2D/texture-only, `27` prefab/cubemap, `9` animation-only, `2` audio) contain a self-contained textured `<Model Name>.glb` plus per-submesh `.obj`, `materials.mtl`, `textures/*.png`, and `model-info.json`. Up from `482` via `11` reconstructed/split/extracted 3D models (`Heartfelt Fox`, `Heartfelt Fox World`, `Heartbound Fox`, `Heartbound Fox World`, `Santa Chaos`, `Santa Chaos World`, `Santa Chaos S3`, `Blackland Ruin`, etc.).
- **2D Spine Hero Skin completeness (`110` bundles):** All `110` `art_lastday_spine_hero_*.bundle` files are verified to contain zero real 3D meshes (`no_mesh_objects` or flat `z_min=0, z_max=0` Spine quads) and are exported cleanly as `.png` atlas sheets (`118`), `.atlas.txt` + `.skel.bytes` (`236`), and `skin-info.json` (`493 + 110 = 603` total cataloged model/skin assets).

## 2. Season Folder Hierarchy (`Pre-Season 1` through `Season 6`)

### 2.1 Extracted Icons by Season (`assets/icons/<Season>/`)
| Season | Theme / Scope | Total Icons | English Named | Cleaned Sprite |
|---|---|---:|---:|---:|
| `Pre-Season 1` | Core launch roster, shelter buildings, HQ & vehicle skins, zombies, shared UI/HUD | **14,864** | 2,721 | 12,143 |
| `Season 1` | Clash of Thrones + S1 heroes (Oliveira, Selena, Nyx, Scarlett, Evelyn, Sakura) | **224** | 208 | 16 |
| `Season 2` | Wastes Watcher (Desert, Virus Lab, Land Office) + S2 heroes (Bella, Alma, Harleyna) | **234** | 184 | 50 |
| `Season 3` | Everfrost Era (Ice, Snow, Glacier bosses, Ice Pit fishing, S3 HQ skins) + S3 heroes | **524** | 208 | 316 |
| `Season 4` | Dinosaur Origin (Dinosaurs, Fossils, Hero Awakenings, Dino march skins) + S4 heroes | **525** | 220 | 305 |
| `Season 5` | Moonlit Elegy (Gothic bosses, Vampires, Werewolves, S5 Cards, Breakthrough) | **676** | 285 | 391 |
| `Season 6` | Season 6 Mastery Points & early S6 icons | **2** | 1 | 1 |
| **TOTAL** | All Verified Seasons | **17,049** | **3,827** | **13,222** |

### 2.2 Extracted 3D Models by Season (`models/<Season>/`)
| Season | Theme / Scope | Models / GLBs | Sub-Mesh OBJs | PNG Textures | Total Vertices | Total Faces |
|---|---|---:|---:|---:|---:|---:|
| `Pre-Season 1` | Core launch roster, shelter buildings, HQ & vehicle skins, zombies, shared UI/HUD | **407** | 2,776 | 2,829 | 2,457,081 | 2,216,788 |
| `Season 1` | Clash of Thrones + S1 heroes (Oliveira, Selena, Nyx, Scarlett, Evelyn, Sakura) | **7** | 23 | 40 | 38,883 | 49,015 |
| `Season 2` | Wastes Watcher (Desert, Virus Lab, Land Office) + S2 heroes (Bella, Alma, Harleyna) | **6** | 11 | 33 | 27,480 | 34,944 |
| `Season 3` | Everfrost Era (Ice, Snow, Glacier bosses, Ice Pit fishing, S3 HQ skins) + S3 heroes | **38** | 166 | 215 | 149,088 | 187,245 |
| `Season 4` | Dinosaur Origin (Dinosaurs, Fossils, Hero Awakenings, Dino march skins) + S4 heroes | **22** | 64 | 116 | 103,289 | 129,551 |
| `Season 5` | Moonlit Elegy (Gothic bosses, Vampires, Werewolves, S5 Cards, Breakthrough) | **13** | 29 | 121 | 50,172 | 74,324 |
| **TOTAL** | All Active 3D Seasons (`Pre-Season 1`..`Season 5`) | **493** | **3,069** | **3,354** | **2,825,993** | **2,691,867** |

### 2.3 Extracted 2D Spine Hero Skins by Season (`models/<Season>/<Faction>/Hero Skins 2D Spine/`)
| Season | Blood Rose | Wings of Dawn | Guard of Order | NPCs and Survivors | Total Spine Bundles |
|---|---:|---:|---:|---:|---:|
| `Pre-Season 1` | 20 | 20 | 16 | 1 | **57** |
| `Season 1` | 8 | 8 | 8 | 0 | **24** |
| `Season 2` | 3 | 2 | 2 | 0 | **7** |
| `Season 3` | 2 | 3 | 2 | 0 | **7** |
| `Season 4` | 5 | 5 | 5 | 0 | **15** |
| **TOTAL** | **38** | **38** | **33** | **1** | **110** |

## 3. Extracted PNG Icons: All 22 Categories (`assets/icons/<Season>/<Category>/`)

| Category Folder | Total Icons | English Named | Cleaned Sprite | Megamind Domain Slug | Active Seasons |
|---|---:|---:|---:|---|---|
| `Resources` | **53** | 25 | 28 | `items_bag_shops_vip` | Pre-S1 (37), S2 (4), S3 (8), S4 (2), S5 (2) |
| `Items` | **649** | 448 | 201 | `items_bag_shops_vip` | Pre-S1 (548), S1 (6), S2 (4), S3 (12), S4 (54), S5 (25) |
| `Hero Portraits Round` | **82** | 60 | 22 | `heroes_skills_equip` | Pre-S1 (56), S1 (15), S2 (4), S3 (4), S4 (3) |
| `Hero Portraits Small` | **415** | 304 | 111 | `heroes_skills_equip` | Pre-S1 (330), S1 (30), S2 (10), S3 (10), S4 (12), S5 (23) |
| `Hero Portraits Large` | **402** | 254 | 148 | `heroes_skills_equip` | Pre-S1 (336), S1 (42), S2 (8), S3 (8), S4 (8) |
| `Hero Fullbody` | **289** | 201 | 88 | `heroes_skills_equip` | Pre-S1 (186), S1 (62), S2 (17), S3 (21), S4 (3) |
| `Hero Fragments` | **86** | 79 | 7 | `heroes_skills_equip` | Pre-S1 (49), S1 (11), S2 (6), S3 (6), S4 (6), S5 (8) |
| `Hero Medals` | **75** | 43 | 32 | `heroes_skills_equip` | Pre-S1 (69), S1 (6) |
| `Hero Equipment` | **192** | 78 | 114 | `heroes_skills_equip` | Pre-S1 (155), S1 (12), S2 (6), S3 (6), S4 (6), S5 (7) |
| `Skills` | **324** | 219 | 105 | `heroes_skills_equip` | Pre-S1 (251), S1 (16), S2 (30), S3 (12), S4 (12), S5 (3) |
| `Science and Tech` | **381** | 220 | 161 | `science_research_talents` | Pre-S1 (304), S1 (2), S2 (55), S3 (5), S4 (7), S5 (6), S6 (2) |
| `Buildings` | **794** | 144 | 650 | `buildings_city` | Pre-S1 (736), S2 (21), S3 (11), S4 (12), S5 (14) |
| `Troops and Soldiers` | **183** | 44 | 139 | `army_troops_hospital` | Pre-S1 (183) |
| `Vehicles and Aircraft` | **427** | 63 | 364 | `garage_vehicles` | Pre-S1 (427) |
| `Monsters and Bosses` | **838** | 154 | 684 | `pve_exploration_bosses` | Pre-S1 (670), S2 (2), S3 (38), S4 (98), S5 (30) |
| `Activities and Events` | **5,425** | 584 | 4,841 | `events_fullprep` | Pre-S1 (4,627), S1 (12), S2 (42), S3 (223), S4 (200), S5 (321) |
| `Alliance and World` | **1,632** | 51 | 1,581 | `alliance` | Pre-S1 (1,465), S1 (2), S2 (13), S3 (46), S4 (47), S5 (59) |
| `Flags` | **199** | 128 | 71 | `alliance` | Pre-S1 (187), S3 (3), S4 (4), S5 (5) |
| `Emojis` | **247** | 176 | 71 | `chat_moments_mail` | Pre-S1 (247) |
| `Collectibles and Fishing` | **427** | 202 | 225 | `events_fullprep` | Pre-S1 (214), S3 (79), S5 (134) |
| `UI HUD` | **3,764** | 211 | 3,553 | `core_engine` | Pre-S1 (3,653), S1 (4), S2 (10), S3 (22), S4 (44), S5 (31) |
| `Misc` | **165** | 139 | 26 | `core_engine` | Pre-S1 (134), S1 (4), S2 (2), S3 (10), S4 (7), S5 (8) |
| **TOTAL (22 Categories)** | **17,049** | **3,827** | **13,222** | - | `Pre-Season 1`..`Season 6` |

## 4. Extracted 3D Models: All 12 Factions & Skin Categories + Season x Faction Matrix

### 4.1 Faction & Skin Category Totals & Geometry Metrics
| Folder (`models/<Season>/<Folder>/`) | Models / GLBs | Sub-Mesh OBJs | PNG Textures | Vertices | Triangles | Megamind Domain Slug |
|---|---:|---:|---:|---:|---:|---|
| `Blood Rose` | **16** | 48 | 89 | 81,990 | 105,025 | `heroes_skills_equip` |
| `Wings of Dawn` | **13** | 41 | 83 | 76,622 | 96,054 | `heroes_skills_equip` |
| `Guard of Order` | **13** | 36 | 83 | 68,741 | 84,328 | `heroes_skills_equip` |
| `HQ Skins` | **28** | 207 | 228 | 170,389 | 180,522 | `buildings_city` |
| `Vehicle Skins` | **28** | 338 | 390 | 671,019 | 540,440 | `garage_vehicles` |
| `Zombies and Monsters` | **76** | 210 | 316 | 298,703 | 409,294 | `pve_exploration_bosses` |
| `Blood Hand and Raiders` | **7** | 11 | 17 | 15,572 | 20,684 | `pve_exploration_bosses` |
| `Troops and Soldiers` | **26** | 72 | 131 | 55,831 | 71,085 | `army_troops_hospital` |
| `Vehicles and Tanks` | **16** | 58 | 88 | 112,399 | 102,317 | `garage_vehicles` |
| `NPCs and Survivors` | **16** | 21 | 25 | 21,108 | 29,095 | `buildings_city` |
| `Weapons` | **46** | 84 | 151 | 64,545 | 58,557 | `heroes_skills_equip` |
| `Buildings and Environment` | **208** | 1,943 | 1,753 | 1,189,074 | 994,466 | `buildings_city` |
| **TOTAL (12 Folders)** | **493** | **3,069** | **3,354** | **2,825,993** | **2,691,867** | - |

### 4.2 Season x Faction & Skin Category Model Matrix
| Season | Blood Rose | Wings of Dawn | Guard of Order | HQ Skins | Vehicle Skins | Zombies & Monsters | Blood Hand | Troops | Vehicles | NPCs | Weapons | Buildings & Env | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `Pre-Season 1` | 8 | 7 | 7 | 25 | 25 | 45 | 5 | 26 | 12 | 16 | 46 | 185 | **407** |
| `Season 1` | 3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **7** |
| `Season 2` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | **6** |
| `Season 3` | 1 | 1 | 1 | 3 | 0 | 12 | 0 | 0 | 1 | 0 | 0 | 19 | **38** |
| `Season 4` | 2 | 2 | 2 | 0 | 3 | 8 | 2 | 0 | 2 | 0 | 0 | 1 | **22** |
| `Season 5` | 0 | 0 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 2 | **13** |
| **TOTAL** | **16** | **13** | **13** | **28** | **28** | **76** | **7** | **26** | **16** | **16** | **46** | **208** | **493** |

## 5. Complete Playable Hero-to-Season / Faction / Icon / 3D Model Lookup Table

All **42** playable hero model entries (`37` unique base heroes + `3` Awakened variants + `2` companion/mount summons) cross-linked to their `assets/icons/` PNGs, `launcher/assets/game_icons/heroes/` Hub WebPs, and `models/` GLB paths:

| Season | Faction | Hero ID | Hero / Model Name | Round Icon (`assets/icons/...`) | Fullbody Icon (`assets/icons/...`) | Fragment Icon (`assets/icons/...`) | Hub WebP | 3D Model (`models/...`) | Meshes / Faces |
|---|---|---:|---|---|---|---|---|---|---:|
| `Pre-Season 1` | `Blood Rose` | 1007 | **Audrey** | `assets/icons/Pre-Season 1/Hero Portraits Round/Audrey.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Audrey.png` | `assets/icons/Pre-Season 1/Hero Fragments/Audrey Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_15.webp` | `models/Pre-Season 1/Blood Rose/Audrey/Audrey.glb` | 2m / 4,475f |
| `Pre-Season 1` | `Blood Rose` | 1016 | **Ava** | `assets/icons/Pre-Season 1/Hero Portraits Round/Ava.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Ava.png` | `assets/icons/Pre-Season 1/Hero Fragments/Ava Fragment (2).png` | `launcher/assets/game_icons/heroes/hero_round_37.webp` | `models/Pre-Season 1/Blood Rose/Ava/Ava.glb` | 9m / 6,036f |
| `Pre-Season 1` | `Blood Rose` | 1011 | **Giselle** | `assets/icons/Pre-Season 1/Hero Portraits Round/Giselle (2).png` | `assets/icons/Pre-Season 1/Hero Fullbody/Giselle.png` | `assets/icons/Pre-Season 1/Hero Fragments/Giselle Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_29.webp` | `models/Pre-Season 1/Blood Rose/Giselle/Giselle.glb` | 2m / 4,104f |
| `Pre-Season 1` | `Blood Rose` | 2025 | **Katrina** | `assets/icons/Pre-Season 1/Hero Portraits Round/Katrina (3).png` | `assets/icons/Pre-Season 1/Hero Fullbody/Katrina.png` | `assets/icons/Pre-Season 1/Hero Fragments/Katrina Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_33.webp` | `models/Pre-Season 1/Blood Rose/Katrina/Katrina.glb` | 3m / 6,766f |
| `Pre-Season 1` | `Blood Rose` | 11001 | **Katrina Tactical** | `assets/icons/Pre-Season 1/Hero Portraits Round/Katrina.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Katrina.png` | `assets/icons/Pre-Season 1/Hero Fragments/Katrina Fragment (3).png` | `launcher/assets/game_icons/heroes/hero_round_33_1.webp` | `models/Pre-Season 1/Blood Rose/Katrina Tactical/Katrina Tactical.glb` | 3m / 6,591f |
| `Pre-Season 1` | `Blood Rose` | 1002 | **Miranda** | `assets/icons/Pre-Season 1/Hero Portraits Round/Miranda.png` | - | `assets/icons/Pre-Season 1/Hero Fragments/Miranda Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_08.webp` | `models/Pre-Season 1/Blood Rose/Miranda/Miranda.glb` | 6m / 11,058f |
| `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia** | `assets/icons/Pre-Season 1/Hero Portraits Round/Sophia (2).png` | `assets/icons/Pre-Season 1/Hero Fullbody/Sophia.png` | `assets/icons/Pre-Season 1/Hero Fragments/Sophia Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_25.webp` | `models/Pre-Season 1/Blood Rose/Sophia/Sophia.glb` | 2m / 4,724f |
| `Pre-Season 1` | `Blood Rose` | 1008 | **Vivian** | - | `assets/icons/Pre-Season 1/Hero Fullbody/Vivian.png` | `assets/icons/Pre-Season 1/Hero Fragments/Vivian Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_36.webp` | `models/Pre-Season 1/Blood Rose/Vivian/Vivian.glb` | 5m / 5,600f |
| `Pre-Season 1` | `Wings of Dawn` | 22001 | **Amelia** | `assets/icons/Pre-Season 1/Hero Portraits Round/Amelia.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Amelia.png` | `assets/icons/Pre-Season 1/Hero Fragments/Amelia Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_01.webp` | `models/Pre-Season 1/Wings of Dawn/Amelia/Amelia.glb` | 2m / 5,308f |
| `Pre-Season 1` | `Wings of Dawn` | 22003 | **Angelina** | `assets/icons/Pre-Season 1/Hero Portraits Round/Angelina.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Angelina.png` | `assets/icons/Pre-Season 1/Hero Fragments/Angelina Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_34.webp` | `models/Pre-Season 1/Wings of Dawn/Angelina/Angelina.glb` | 3m / 6,304f |
| `Pre-Season 1` | `Wings of Dawn` | 12001 | **Christina** | `assets/icons/Pre-Season 1/Hero Portraits Round/Christina.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Christina.png` | `assets/icons/Pre-Season 1/Hero Fragments/Christina Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_39.webp` | `models/Pre-Season 1/Wings of Dawn/Christina/Christina.glb` | 3m / 8,285f |
| `Pre-Season 1` | `Wings of Dawn` | 22002 | **Fiona** | `assets/icons/Pre-Season 1/Hero Portraits Round/Fiona.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Fiona.png` | `assets/icons/Pre-Season 1/Hero Fragments/Fiona Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_35.webp` | `models/Pre-Season 1/Wings of Dawn/Fiona/Fiona.glb` | 3m / 7,790f |
| `Pre-Season 1` | `Wings of Dawn` | 33001 | **Isabella** | `assets/icons/Pre-Season 1/Hero Portraits Round/Isabella.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Isabella.png` | `assets/icons/Pre-Season 1/Hero Fragments/Isabella Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_16.webp` | `models/Pre-Season 1/Wings of Dawn/Isabella/Isabella.glb` | 2m / 4,995f |
| `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura** | `assets/icons/Pre-Season 1/Hero Portraits Round/Laura.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Laura.png` | `assets/icons/Pre-Season 1/Hero Fragments/Laura Fragment (2).png` | `launcher/assets/game_icons/heroes/hero_round_40.webp` | `models/Pre-Season 1/Wings of Dawn/Laura/Laura.glb` | 5m / 9,584f |
| `Pre-Season 1` | `Wings of Dawn` | 1021 | **Natalie** | `assets/icons/Pre-Season 1/Hero Portraits Round/Natalie.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Natalie.png` | `assets/icons/Pre-Season 1/Hero Fragments/Natalie Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_28.webp` | `models/Pre-Season 1/Wings of Dawn/Natalie/Natalie.glb` | 3m / 7,713f |
| `Pre-Season 1` | `Guard of Order` | 33002 | **Athena** | `assets/icons/Pre-Season 1/Hero Portraits Round/Athena.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Athena.png` | `assets/icons/Pre-Season 1/Hero Fragments/Athena Fragment (2).png` | `launcher/assets/game_icons/heroes/hero_round_38.webp` | `models/Pre-Season 1/Guard of Order/Athena/Athena.glb` | 2m / 5,642f |
| `Pre-Season 1` | `Guard of Order` | 1003 | **Chinatsu** | `assets/icons/Pre-Season 1/Hero Portraits Round/Chinatsu.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Chinatsu.png` | `assets/icons/Pre-Season 1/Hero Fragments/Chinatsu Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_05.webp` | `models/Pre-Season 1/Guard of Order/Chinatsu/Chinatsu.glb` | 2m / 5,182f |
| `Pre-Season 1` | `Guard of Order` | 1018 | **Elizabeth** | `assets/icons/Pre-Season 1/Hero Portraits Round/Elizabeth.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Elizabeth.png` | `assets/icons/Pre-Season 1/Hero Fragments/Elizabeth Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_06.webp` | `models/Pre-Season 1/Guard of Order/Elizabeth/Elizabeth.glb` | 2m / 4,589f |
| `Pre-Season 1` | `Guard of Order` | 1019 | **Leah** | `assets/icons/Pre-Season 1/Hero Portraits Round/Leah.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Leah.png` | `assets/icons/Pre-Season 1/Hero Fragments/Leah Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_22.webp` | `models/Pre-Season 1/Guard of Order/Leah/Leah.glb` | 4m / 7,631f |
| `Pre-Season 1` | `Guard of Order` | 1015 | **Maria** | `assets/icons/Pre-Season 1/Hero Portraits Round/Maria.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Maria.png` | `assets/icons/Pre-Season 1/Hero Fragments/Maria Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_20.webp` | `models/Pre-Season 1/Guard of Order/Maria/Maria.glb` | 2m / 4,478f |
| `Pre-Season 1` | `Guard of Order` | 1017 | **Mia** | `assets/icons/Pre-Season 1/Hero Portraits Round/Mia.png` | `assets/icons/Pre-Season 1/Hero Fullbody/Mia.png` | `assets/icons/Pre-Season 1/Hero Fragments/Mia Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_07.webp` | `models/Pre-Season 1/Guard of Order/Mia/Mia.glb` | 3m / 6,060f |
| `Pre-Season 1` | `Guard of Order` | 32001 | **William** | `assets/icons/Pre-Season 1/Hero Portraits Round/William.png` | `assets/icons/Pre-Season 1/Hero Fullbody/William.png` | `assets/icons/Pre-Season 1/Hero Fragments/William Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_03.webp` | `models/Pre-Season 1/Guard of Order/William/William.glb` | 4m / 7,564f |
| `Season 1` | `Blood Rose` | 1004 | **Oliveira** | `assets/icons/Season 1/Hero Portraits Round/Oliveira.png` | `assets/icons/Season 1/Hero Fullbody/Oliveira.png` | `assets/icons/Season 1/Hero Fragments/Oliveira Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_10.webp` | `models/Season 1/Blood Rose/Oliveira/Oliveira.glb` | 2m / 7,516f |
| `Season 1` | `Blood Rose` | 5000 | **Selena** | `assets/icons/Season 1/Hero Portraits Round/Selena.png` | `assets/icons/Season 1/Hero Fullbody/Selena.png` | `assets/icons/Season 1/Hero Fragments/Selena Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_41.webp` | `models/Season 1/Blood Rose/Selena/Selena.glb` | 3m / 5,424f |
| `Season 1` | `Blood Rose` | 5000 | **Selena Bear Companion** | `assets/icons/Season 1/Hero Portraits Round/Selena.png` | `assets/icons/Season 1/Hero Fullbody/Selena.png` | `assets/icons/Season 1/Hero Fragments/Selena Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_41.webp` | `models/Season 1/Blood Rose/Selena Bear Companion/Selena Bear Companion.glb` | 1m / 3,570f |
| `Season 1` | `Wings of Dawn` | 5001 | **Nyx** | `assets/icons/Season 1/Hero Portraits Round/Nyx.png` | `assets/icons/Season 1/Hero Fullbody/Nyx.png` | `assets/icons/Season 1/Hero Fragments/Nyx Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_42.webp` | `models/Season 1/Wings of Dawn/Nyx/Nyx.glb` | 4m / 7,666f |
| `Season 1` | `Wings of Dawn` | 21001 | **Scarlett** | `assets/icons/Season 1/Hero Portraits Round/Scarlett.png` | `assets/icons/Season 1/Hero Fullbody/Scarlett.png` | `assets/icons/Season 1/Hero Fragments/Scarlett Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_19.webp` | `models/Season 1/Wings of Dawn/Scarlett/Scarlett.glb` | 5m / 9,037f |
| `Season 1` | `Guard of Order` | 33003 | **Evelyn** | `assets/icons/Season 1/Hero Portraits Round/Evelyn.png` | `assets/icons/Season 1/Hero Fullbody/Evelyn.png` | `assets/icons/Season 1/Hero Fragments/Evelyn Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_27.webp` | `models/Season 1/Guard of Order/Evelyn/Evelyn.glb` | 3m / 4,704f |
| `Season 1` | `Guard of Order` | 5002 | **Sakura** | `assets/icons/Season 1/Hero Portraits Round/Sakura.png` | `assets/icons/Season 1/Hero Fullbody/Sakura.png` | `assets/icons/Season 1/Hero Fragments/Sakura Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_43.webp` | `models/Season 1/Guard of Order/Sakura/Sakura.glb` | 5m / 11,098f |
| `Season 2` | `Blood Rose` | 5003 | **Bella** | `assets/icons/Season 2/Hero Portraits Round/Bella.png` | `assets/icons/Season 2/Hero Fullbody/Bella.png` | `assets/icons/Season 2/Hero Fragments/Bella Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_45.webp` | `models/Season 2/Blood Rose/Bella/Bella.glb` | 2m / 10,973f |
| `Season 2` | `Blood Rose` | 5003 | **Bella Horse Stampede** | `assets/icons/Season 2/Hero Portraits Round/Bella.png` | `assets/icons/Season 2/Hero Fullbody/Bella.png` | `assets/icons/Season 2/Hero Fragments/Bella Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_45.webp` | `models/Season 2/Blood Rose/Bella Horse Stampede/Bella Horse Stampede.glb` | 1m / 4,576f |
| `Season 2` | `Wings of Dawn` | 5004 | **Alma** | `assets/icons/Season 2/Hero Portraits Round/Alma.png` | `assets/icons/Season 2/Hero Fullbody/Alma.png` | `assets/icons/Season 2/Hero Fragments/Alma Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_44.webp` | `models/Season 2/Wings of Dawn/Alma/Alma.glb` | 2m / 5,952f |
| `Season 2` | `Guard of Order` | 5005 | **Harleyna** | `assets/icons/Season 2/Hero Portraits Round/Harleyna.png` | `assets/icons/Season 2/Hero Fullbody/Harleyna.png` | `assets/icons/Season 2/Hero Fragments/Harleyna Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_46.webp` | `models/Season 2/Guard of Order/Harleyna/Harleyna.glb` | 2m / 7,652f |
| `Season 3` | `Blood Rose` | 5006 | **Licia** | `assets/icons/Season 3/Hero Portraits Round/Licia.png` | `assets/icons/Season 3/Hero Fullbody/Licia.png` | `assets/icons/Season 3/Hero Fragments/Licia Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_47.webp` | `models/Season 3/Blood Rose/Licia/Licia.glb` | 1m / 10,108f |
| `Season 3` | `Wings of Dawn` | 5007 | **Liliana** | `assets/icons/Season 3/Hero Portraits Round/Liliana.png` | `assets/icons/Season 3/Hero Fullbody/Liliana.png` | `assets/icons/Season 3/Hero Fragments/Liliana Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_48.webp` | `models/Season 3/Wings of Dawn/Liliana/Liliana.glb` | 3m / 10,513f |
| `Season 3` | `Guard of Order` | 5008 | **Dodomeki** | `assets/icons/Season 3/Hero Portraits Round/Dodomeki.png` | `assets/icons/Season 3/Hero Fullbody/Dodomeki.png` | `assets/icons/Season 3/Hero Fragments/Dodomeki Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_49.webp` | `models/Season 3/Guard of Order/Dodomeki/Dodomeki.glb` | 1m / 8,982f |
| `Season 4` | `Blood Rose` | 1004 | **Oliveira Awakened** | `assets/icons/Season 1/Hero Portraits Round/Oliveira.png` | `assets/icons/Season 1/Hero Fullbody/Oliveira.png` | `assets/icons/Season 1/Hero Fragments/Oliveira Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_10.webp` | `models/Season 4/Blood Rose/Oliveira Awakened/Oliveira Awakened.glb` | 3m / 7,464f |
| `Season 4` | `Blood Rose` | 5009 | **Yu Chan** | `assets/icons/Season 4/Hero Portraits Round/Yu Chan.png` | `assets/icons/Season 4/Hero Fullbody/Yu Chan.png` | `assets/icons/Season 4/Hero Fragments/Yu Chan Fragment.png` | - | `models/Season 4/Blood Rose/Yu Chan/Yu Chan.glb` | 3m / 6,040f |
| `Season 4` | `Wings of Dawn` | 5010 | **Queenie** | `assets/icons/Season 4/Hero Portraits Round/Queenie.png` | `assets/icons/Season 4/Hero Fullbody/Queenie.png` | `assets/icons/Season 4/Hero Fragments/Queenie Fragment.png` | - | `models/Season 4/Wings of Dawn/Queenie/Queenie.glb` | 3m / 6,483f |
| `Season 4` | `Wings of Dawn` | 21001 | **Scarlett Awakened** | `assets/icons/Season 1/Hero Portraits Round/Scarlett.png` | `assets/icons/Season 1/Hero Fullbody/Scarlett.png` | `assets/icons/Season 1/Hero Fragments/Scarlett Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_19.webp` | `models/Season 4/Wings of Dawn/Scarlett Awakened/Scarlett Awakened.glb` | 3m / 6,424f |
| `Season 4` | `Guard of Order` | 5011 | **Amber** | `assets/icons/Season 4/Hero Portraits Round/Amber.png` | `assets/icons/Season 4/Hero Fullbody/Amber.png` | `assets/icons/Season 4/Hero Fragments/Amber Fragment.png` | - | `models/Season 4/Guard of Order/Amber/Amber.glb` | 3m / 4,850f |
| `Season 4` | `Guard of Order` | 33003 | **Evelyn Awakened** | `assets/icons/Season 1/Hero Portraits Round/Evelyn.png` | `assets/icons/Season 1/Hero Fullbody/Evelyn.png` | `assets/icons/Season 1/Hero Fragments/Evelyn Fragment.png` | `launcher/assets/game_icons/heroes/hero_round_27.webp` | `models/Season 4/Guard of Order/Evelyn Awakened/Evelyn Awakened.glb` | 3m / 5,896f |

### Legacy & Additional Hub `hero_id_to_sprite` Entries (No Dedicated Hero 3D Model)
The following `7` hero IDs appear in `launcher/assets/game_icons/manifest.json` (`hero_id_to_sprite`) as alternate/starter roster IDs sharing generic or base sprites:

| Hero ID | XML Name (`aps_new_heroes`) | Camp | Hub WebP (`launcher/assets/game_icons/heroes/...`) | Sprite Name |
|---:|---|---:|---|---|
| 1009 | Anthony | 3 | `launcher/assets/game_icons/heroes/hero_round_09.webp` | `hero_round_09` |
| 1013 | Claire | 2 | `launcher/assets/game_icons/heroes/hero_round_09.webp` | `hero_round_09` |
| 2000 | Audrey | 2 | `launcher/assets/game_icons/heroes/hero_round_09.webp` | `hero_round_09` |
| 3000 | Audrey | 2 | `launcher/assets/game_icons/heroes/hero_round_15.webp` | `hero_round_15` |
| 13001 | Giselle | 1 | `launcher/assets/game_icons/heroes/hero_round_09.webp` | `hero_round_09` |
| 13003 | Emma | 1 | `launcher/assets/game_icons/heroes/hero_round_09.webp` | `hero_round_09` |
| 33004 | Lucas | 3 | `launcher/assets/game_icons/heroes/hero_round_09.webp` | `hero_round_09` |

## 6. 3D Purchasable & Event HQ Skins (`28` Models in `HQ Skins`)

All **28** 3D HQ skins (`25` in `Pre-Season 1/HQ Skins/` + `3` Everfrost snow variants in `Season 3/HQ Skins/`), including reconstructed/split skins (`Heartfelt Fox`, `Heartfelt Fox World`, `Heartbound Fox`, `Heartbound Fox World`, `Santa Chaos`, `Santa Chaos World`, `Santa Chaos S3`). Note also `Blackland Ruin` (`Pre-Season 1/Buildings and Environment/Blackland Ruin/Blackland Ruin.glb`, `3m / 608f`) extracted alongside the HQ skin bundle pass.

| # | Season | HQ Skin Name | GLB Path (`models/...`) | Meshes / Textures | Triangles | Evidence Source |
|---:|---|---|---|---:|---:|---|
| 1 | `Pre-Season 1` | **Battle Fortress** | `models/Pre-Season 1/HQ Skins/Battle Fortress/Battle Fortress.glb` | 14m / 13t | 12,567 | decoration.json(id=10002, type=1, name='Battle Fortress', model='A_Build_PiFu01') -> main_prefabs_building_a_build_pifu01 -> a_build_kaifupifu |
| 2 | `Pre-Season 1` | **Bear Wick HQ** | `models/Pre-Season 1/HQ Skins/Bear Wick HQ/Bear Wick HQ.glb` | 13m / 13t | 10,654 | decoration.json(id=10021, type=1, name='Bear Wick', model='A_build_WhiteBear_A') -> whitebear_a_hq + whitebear_common materials |
| 3 | `Pre-Season 1` | **Bear Wick HQ Tier 2** | `models/Pre-Season 1/HQ Skins/Bear Wick HQ Tier 2/Bear Wick HQ Tier 2.glb` | 12m / 11t | 11,656 | decoration.json(id=10021, type=1, name='Bear Wick') Tier B HQ variant (whitebear_b_hq + whitebear_common materials) |
| 4 | `Pre-Season 1` | **Bear Wick Pedestal** | `models/Pre-Season 1/HQ Skins/Bear Wick Pedestal/Bear Wick Pedestal.glb` | 3m / 33t | 836 | decoration.json(id=10021, type=1, name='Bear Wick') shared HQ pedestal (whitebear_common) |
| 5 | `Pre-Season 1` | **Bear Wick World** | `models/Pre-Season 1/HQ Skins/Bear Wick World/Bear Wick World.glb` | 12m / 14t | 6,015 | decoration.json(id=10021, type=1, name='Bear Wick', model_world='A_build_WhiteBear_A_World') -> whitebear_a_world + whitebear_common materials |
| 6 | `Pre-Season 1` | **Bear Wick World Tier 2** | `models/Pre-Season 1/HQ Skins/Bear Wick World Tier 2/Bear Wick World Tier 2.glb` | 10m / 10t | 6,674 | decoration.json(id=10021, type=1, name='Bear Wick') Tier B World variant (whitebear_b_world + whitebear_common materials) |
| 7 | `Pre-Season 1` | **Boom Show** | `models/Pre-Season 1/HQ Skins/Boom Show/Boom Show.glb` | 5m / 12t | 11,526 | decoration.json(id=10016, type=1, name='Boom Show', model='A_build_yurenjiexiaochoupifu_01') |
| 8 | `Pre-Season 1` | **Boxing T-Rex** | `models/Pre-Season 1/HQ Skins/Boxing T-Rex/Boxing T-Rex.glb` | 6m / 8t | 11,167 | decoration.json(id=10017, type=1, name='Boxing T-Rex', model='A_build_quanjilong_01') |
| 9 | `Pre-Season 1` | **Disco Ball** | `models/Pre-Season 1/HQ Skins/Disco Ball/Disco Ball.glb` | 1m / 4t | 407 | decoration.json(id=10019, type=10, name='Disco Ball', model_world='World_pijiujie_01') -> world_resource_01_world_pijiujie_01 |
| 10 | `Pre-Season 1` | **Disco Ball Snowman** | `models/Pre-Season 1/HQ Skins/Disco Ball Snowman/Disco Ball Snowman.glb` | 1m / 1t | 820 | decoration.json(id=10023, type=10, name='Disco Ball', model_world='A_build_ChristmasSnowMan') -> main_prefabs_building_a_build_christmassnowman |
| 11 | `Pre-Season 1` | **Disco Ball World** | `models/Pre-Season 1/HQ Skins/Disco Ball World/Disco Ball World.glb` | 4m / 4t | 413 | decoration.json(id=10019, type=10, name='Disco Ball', model_world='World_pijiujie_01') -> main_prefabs_building_world_pijiujie_01 |
| 12 | `Pre-Season 1` | **Heartbound Fox** | `models/Pre-Season 1/HQ Skins/Heartbound Fox/Heartbound Fox.glb` | 10m / 6t | 8,403 | decoration.json(id=10025, type=1, name='Heartbound Fox', model='A_build_Valentine_Fox_A') -> valentine_fox::A_build_Valentine_Fox_A.prefab |
| 13 | `Pre-Season 1` | **Heartbound Fox World** | `models/Pre-Season 1/HQ Skins/Heartbound Fox World/Heartbound Fox World.glb` | 9m / 6t | 5,709 | decoration.json(id=10025, type=1, name='Heartbound Fox', model_world='A_build_Valentine_Fox_A_world') -> valentine_fox::A_build_Valentine_Fox_A_world.prefab |
| 14 | `Pre-Season 1` | **Heartfelt Fox** | `models/Pre-Season 1/HQ Skins/Heartfelt Fox/Heartfelt Fox.glb` | 10m / 6t | 8,415 | decoration.json(id=10026, type=1, name='Heartfelt Fox', model='A_build_Valentine_WhiteFox_A') -> valentine_fox::A_build_Valentine_WhiteFox_A.prefab |
| 15 | `Pre-Season 1` | **Heartfelt Fox World** | `models/Pre-Season 1/HQ Skins/Heartfelt Fox World/Heartfelt Fox World.glb` | 10m / 6t | 5,761 | decoration.json(id=10026, type=1, name='Heartfelt Fox', model_world='A_build_Valentine_WhiteFox_A_world') -> valentine_fox::A_build_Valentine_WhiteFox_A_world.prefab |
| 16 | `Pre-Season 1` | **Santa Chaos** | `models/Pre-Season 1/HQ Skins/Santa Chaos/Santa Chaos.glb` | 6m / 6t | 12 | decoration.json(id=10003, type=1, name='Santa Chaos', model='A_Build_ShengSanJiePiFu_01') -> main_prefabs_building_a_build_shengsanjiepifu_01 + a_build_shengsanjiepifu_01 materials |
| 17 | `Pre-Season 1` | **Santa Chaos World** | `models/Pre-Season 1/HQ Skins/Santa Chaos World/Santa Chaos World.glb` | 6m / 6t | 12 | decoration.json(id=10003, type=1, name='Santa Chaos', model_world='A_Build_ShengSanJiePiFu_01_world') -> main_prefabs_building_a_build_shengsanjiepifu_01_world |
| 18 | `Pre-Season 1` | **Snowlaf** | `models/Pre-Season 1/HQ Skins/Snowlaf/Snowlaf.glb` | 1m / 1t | 820 | decoration.json(id=10024, type=1, name='Snowlaf', model_world='World_Shengdanjiexueren_01') -> main_prefabs_building_world_shengdanjiexueren_01 |
| 19 | `Pre-Season 1` | **Snowlaf World** | `models/Pre-Season 1/HQ Skins/Snowlaf World/Snowlaf World.glb` | 1m / 1t | 820 | decoration.json(id=10024, type=1, name='Snowlaf', model_world='World_Shengdanjiexueren_01') -> world_resource_01_world_shengdanjiexueren_01 |
| 20 | `Pre-Season 1` | **Thanksgiving Roast Turkey** | `models/Pre-Season 1/HQ Skins/Thanksgiving Roast Turkey/Thanksgiving Roast Turkey.glb` | 1m / 1t | 665 | Holiday HQ decoration bundle (a_build_huoji_01 / Thanksgiving Turkey) |
| 21 | `Pre-Season 1` | **Thanksgiving Roast Turkey World** | `models/Pre-Season 1/HQ Skins/Thanksgiving Roast Turkey World/Thanksgiving Roast Turkey World.glb` | 1m / 1t | 665 | world_resource_01_world_huoji_01 + a_build_huoji_01::Turkey_Material |
| 22 | `Pre-Season 1` | **Thanksgiving Turkey Event** | `models/Pre-Season 1/HQ Skins/Thanksgiving Turkey Event/Thanksgiving Turkey Event.glb` | 1m / 1t | 665 | main_prefabs_building_world_turkey -> World_HuoJi_01_Spine + a_build_huoji_01::Turkey_Material |
| 23 | `Pre-Season 1` | **The Inferno** | `models/Pre-Season 1/HQ Skins/The Inferno/The Inferno.glb` | 23m / 19t | 13,701 | decoration.json(id=10027, type=1, name='The Inferno', model='A_build_DragonCastle') |
| 24 | `Pre-Season 1` | **The Nightmare** | `models/Pre-Season 1/HQ Skins/The Nightmare/The Nightmare.glb` | 13m / 10t | 16,729 | decoration.json(id=10020, type=1, name='The Nightmare', model='A_build_halloween_dragon') |
| 25 | `Pre-Season 1` | **The Purr-cussion** | `models/Pre-Season 1/HQ Skins/The Purr-cussion/The Purr-cussion.glb` | 18m / 10t | 17,094 | decoration.json(id=10018, type=1, name='The Purr-cussion', model='A_build_beer_cat02') |
| 26 | `Season 3` | **Boom Show S3** | `models/Season 3/HQ Skins/Boom Show S3/Boom Show S3.glb` | 7m / 14t | 18,835 | decoration.json(id=10016, type=1, name='Boom Show') Everfrost Era S3 snow variant (a_build_yurenjiexiaochoupifu_01_s3) |
| 27 | `Season 3` | **Boxing T-Rex S3** | `models/Season 3/HQ Skins/Boxing T-Rex S3/Boxing T-Rex S3.glb` | 3m / 5t | 9,469 | decoration.json(id=10017, type=1, name='Boxing T-Rex') Everfrost Era S3 snow variant (a_build_quanjilong_01_s3) |
| 28 | `Season 3` | **Santa Chaos S3** | `models/Season 3/HQ Skins/Santa Chaos S3/Santa Chaos S3.glb` | 6m / 6t | 12 | decoration.json(id=10003, type=1, name='Santa Chaos') Everfrost Era S3 snow variant (a_build_shengsanjiepifu_s3_01) |

## 7. 3D Purchasable & Upgradeable Vehicle Skins (`28` Models in `Vehicle Skins`)

All **28** 3D vehicle & march skins (`25` in `Pre-Season 1/Vehicle Skins/` covering `Cheetah Armored Vehicle`, `Conqueror`, `Destroyer`, `Destroyer Rocket`, `Destroyer-EX`, `Hercules` + `3` Season 4 Dinosaur march skins `Ankylosaurus`, `T-Rex`, `Triceratops` in `Season 4/Vehicle Skins/`):

| # | Season | Vehicle Skin Name | GLB Path (`models/...`) | Meshes / Textures | Triangles | Evidence Source |
|---:|---|---|---|---:|---:|---|
| 1 | `Pre-Season 1` | **Cheetah Armored Vehicle Classic** | `models/Pre-Season 1/Vehicle Skins/Cheetah Armored Vehicle Classic/Cheetah Armored Vehicle Classic.glb` | 12m / 16t | 12,737 | decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle') base garage model (a_vehicle_zhuangjiache_01) |
| 2 | `Pre-Season 1` | **Cheetah Armored Vehicle Showcase** | `models/Pre-Season 1/Vehicle Skins/Cheetah Armored Vehicle Showcase/Cheetah Armored Vehicle Showcase.glb` | 20m / 22t | 23,440 | decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle', model='WorldTroop_002..Up2') + main_prefabs_building_worldtroop_002(A_vehicle_zhuangjaiche_01..03) + car_show.json(id=2) |
| 3 | `Pre-Season 1` | **Cheetah Armored Vehicle Stage** | `models/Pre-Season 1/Vehicle Skins/Cheetah Armored Vehicle Stage/Cheetah Armored Vehicle Stage.glb` | 8m / 8t | 15,256 | decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle') + car_show_barrel.json(A_vehicle_zhuangjiache_guanka_01..03) |
| 4 | `Pre-Season 1` | **Cheetah Armored Vehicle World** | `models/Pre-Season 1/Vehicle Skins/Cheetah Armored Vehicle World/Cheetah Armored Vehicle World.glb` | 23m / 13t | 21,766 | decoration.json(id=50002/50006/50010, type=4, name='Cheetah Armored Vehicle') -> a_vehicle_zhuangjiache_01_shijie world march model |
| 5 | `Pre-Season 1` | **Conqueror Showcase** | `models/Pre-Season 1/Vehicle Skins/Conqueror Showcase/Conqueror Showcase.glb` | 24m / 20t | 26,025 | decoration.json(id=50001/50005/50009, type=4, name='Conqueror', model='WorldTroop_001..Up2') + main_prefabs_building_worldtroop_001(A_vehicle_dajiaoche_01..03) + car_show.json(id=1) |
| 6 | `Pre-Season 1` | **Conqueror Stage** | `models/Pre-Season 1/Vehicle Skins/Conqueror Stage/Conqueror Stage.glb` | 8m / 10t | 15,256 | decoration.json(id=50001/50005/50009, type=4, name='Conqueror') + car_show_barrel.json(A_vehicle_dajiaoche_guanka_01..03) |
| 7 | `Pre-Season 1` | **Conqueror World** | `models/Pre-Season 1/Vehicle Skins/Conqueror World/Conqueror World.glb` | 12m / 10t | 13,044 | decoration.json(id=50001/50005/50009, type=4, name='Conqueror', model='WorldTroop_001..Up2') -> a_vehicle_dajiaoche_01_shijie world march model |
| 8 | `Pre-Season 1` | **Destroyer Rocket Classic** | `models/Pre-Season 1/Vehicle Skins/Destroyer Rocket Classic/Destroyer Rocket Classic.glb` | 15m / 19t | 15,798 | decoration.json(id=50004, type=4, name='Destroyer') classic showcase model (a_vehicle_huojianche) |
| 9 | `Pre-Season 1` | **Destroyer Rocket Classic Stage** | `models/Pre-Season 1/Vehicle Skins/Destroyer Rocket Classic Stage/Destroyer Rocket Classic Stage.glb` | 1m / 2t | 5,841 | decoration.json(id=50004, type=4, name='Destroyer') + car_show_barrel.json(A_vehicle_huojianche_guanka) |
| 10 | `Pre-Season 1` | **Destroyer Rocket Classic World** | `models/Pre-Season 1/Vehicle Skins/Destroyer Rocket Classic World/Destroyer Rocket Classic World.glb` | 6m / 9t | 9,932 | decoration.json(id=50004, type=4, name='Destroyer') Tier 1 world march model (a_vehicle_huojianche_shijie) |
| 11 | `Pre-Season 1` | **Destroyer Rocket Showcase** | `models/Pre-Season 1/Vehicle Skins/Destroyer Rocket Showcase/Destroyer Rocket Showcase.glb` | 24m / 16t | 55,292 | decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + main_prefabs_building_worldtroop_004(A_vehicle_huojianche_01..03) -> a_vehicle_huojianche_zhanshi_formal |
| 12 | `Pre-Season 1` | **Destroyer Rocket Stage** | `models/Pre-Season 1/Vehicle Skins/Destroyer Rocket Stage/Destroyer Rocket Stage.glb` | 4m / 5t | 14,820 | decoration.json(id=50004/50008/50012, type=4, name='Destroyer') -> a_vehicle_huojianche_guanka_formal stage model |
| 13 | `Pre-Season 1` | **Destroyer Rocket World** | `models/Pre-Season 1/Vehicle Skins/Destroyer Rocket World/Destroyer Rocket World.glb` | 5m / 15t | 9,761 | decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + main_prefabs_building_worldtroop_005 -> a_vehicle_huojianche_shijie_formal |
| 14 | `Pre-Season 1` | **Destroyer Showcase** | `models/Pre-Season 1/Vehicle Skins/Destroyer Showcase/Destroyer Showcase.glb` | 20m / 33t | 42,825 | decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + car_show.json(id=4, model='A_vehicle_daodanche_02..03_zhanshi') |
| 15 | `Pre-Season 1` | **Destroyer Stage** | `models/Pre-Season 1/Vehicle Skins/Destroyer Stage/Destroyer Stage.glb` | 6m / 13t | 12,769 | decoration.json(id=50004/50008/50012, type=4, name='Destroyer') + car_show_barrel.json(A_vehicle_daodanche_02..03_guanka) |
| 16 | `Pre-Season 1` | **Destroyer Tier 1 Showcase** | `models/Pre-Season 1/Vehicle Skins/Destroyer Tier 1 Showcase/Destroyer Tier 1 Showcase.glb` | 10m / 5t | 19,095 | decoration.json(id=50004, type=4, name='Destroyer', model='WorldTroop_004') + car_show.json(id=4, Tier 1 model='A_vehicle_huojianche_zhanshi_linshi') |
| 17 | `Pre-Season 1` | **Destroyer World** | `models/Pre-Season 1/Vehicle Skins/Destroyer World/Destroyer World.glb` | 18m / 12t | 25,504 | decoration.json(id=50004/50008/50012, type=4, name='Destroyer') -> a_vehicle_daodanche_world world march model |
| 18 | `Pre-Season 1` | **Destroyer-EX Showcase** | `models/Pre-Season 1/Vehicle Skins/Destroyer-EX Showcase/Destroyer-EX Showcase.glb` | 37m / 52t | 58,768 | decoration.json(id=50014/50015/50016, type=4, name='Destroyer-EX', model='WorldTroop_005_new..Up2') + car_show.json(id=5, model='A_vehicle_daodanche_EX_01..03_zhanshi') |
| 19 | `Pre-Season 1` | **Destroyer-EX Stage** | `models/Pre-Season 1/Vehicle Skins/Destroyer-EX Stage/Destroyer-EX Stage.glb` | 13m / 23t | 19,083 | decoration.json(id=50014/50015/50016, type=4, name='Destroyer-EX') + car_show_barrel.json(A_vehicle_daodanche_EX_01..03_guanka) |
| 20 | `Pre-Season 1` | **Destroyer-EX World** | `models/Pre-Season 1/Vehicle Skins/Destroyer-EX World/Destroyer-EX World.glb` | 18m / 19t | 20,282 | decoration.json(id=50014/50015/50016, type=4, name='Destroyer-EX') + main_prefabs_building_worldtroop_005_newup2 -> a_vehicle_daodanche_ex_world |
| 21 | `Pre-Season 1` | **Hercules Classic** | `models/Pre-Season 1/Vehicle Skins/Hercules Classic/Hercules Classic.glb` | 9m / 17t | 15,687 | decoration.json(id=50003/50007/50011, type=4, name='Hercules') base garage tank (a_vehicle_tanke) |
| 22 | `Pre-Season 1` | **Hercules Classic Stage** | `models/Pre-Season 1/Vehicle Skins/Hercules Classic Stage/Hercules Classic Stage.glb` | 2m / 2t | 4,970 | decoration.json(id=50003/50007/50011, type=4, name='Hercules') stage tank (a_vehicle_tanke_guanka) |
| 23 | `Pre-Season 1` | **Hercules Showcase** | `models/Pre-Season 1/Vehicle Skins/Hercules Showcase/Hercules Showcase.glb` | 13m / 21t | 22,382 | decoration.json(id=50003/50007/50011, type=4, name='Hercules', model='WorldTroop_003..Up2') + main_prefabs_building_worldtroop_003(A_vehicle_tanke_01..03) + car_show.json(id=3) |
| 24 | `Pre-Season 1` | **Hercules Stage** | `models/Pre-Season 1/Vehicle Skins/Hercules Stage/Hercules Stage.glb` | 3m / 4t | 13,845 | decoration.json(id=50003/50007/50011, type=4, name='Hercules') + car_show_barrel.json(A_vehicle_tanke_guanka_01..03_formal) |
| 25 | `Pre-Season 1` | **Hercules World** | `models/Pre-Season 1/Vehicle Skins/Hercules World/Hercules World.glb` | 21m / 12t | 30,288 | decoration.json(id=50003/50007/50011, type=4, name='Hercules') -> a_vehicle_tanke_shijie_formal world march model |
| 26 | `Season 4` | **Ankylosaurus** | `models/Season 4/Vehicle Skins/Ankylosaurus/Ankylosaurus.glb` | 2m / 4t | 5,352 | decoration.json(id=40007, type=4, season=4, name='Ankylosaurus', model='Vehicle_JiaLong_S4_Variant') |
| 27 | `Season 4` | **T-Rex** | `models/Season 4/Vehicle Skins/T-Rex/T-Rex.glb` | 2m / 4t | 5,350 | decoration.json(id=40005, type=4, season=4, name='T-Rex', model='Vehicle_BaWangLong_S4_Variant') |
| 28 | `Season 4` | **Triceratops** | `models/Season 4/Vehicle Skins/Triceratops/Triceratops.glb` | 2m / 4t | 5,272 | decoration.json(id=40006, type=4, season=4, name='Triceratops', model='Vehicle_SanJiaoLong_S4_Variant') |

## 8. 2D Spine Hero Skins (`110` Bundles in `Hero Skins 2D Spine`)

All **110** `art_lastday_spine_hero_*.bundle` packages indexed in SQLite as `layer='hero_skin_spine'` and stored at `models/<Season>/<Faction>/Hero Skins 2D Spine/<Hero Name> - <Skin Name>/` (`118` `.png` atlas sheets, `236` `.atlas.txt`/`.skel.bytes` files, `110` `skin-info.json` manifests; `0` real 3D meshes).

### 8.1 Unlock Category Breakdown
| Skin Category (`skin_category`) | Bundle Count | Description |
|---|---:|---|
| `default` | **39** | Base playable hero & NPC default Spine rigs (`Spine_Hero_<id>`) |
| `affection` | **23** | Hero affection / intimacy tier unlock skins (I / II / III) |
| `purchasable` | **22** | Shop & event purchasable skins linked to `aps_new_heros_skin_shop.json` (`shop_id`) |
| `stage_variant` | **1** | Stage combat Spine variant (`Sophia - Stage Battle`) |
| `regional_default` | **1** | Regional ME default variant (`Angelina - Default ME`) |
| `exclusive_weapon` | **15** | Hero exclusive weapon unlock Spine animations (`heroes_exclusive_equip.json`) |
| `awakening` | **6** | Season 4 hero awakening & awakened appearance Spine rigs (`Oliveira`, `Scarlett`, `Evelyn`) |
| `awakened_exclusive_weapon` | **3** | Season 4 awakened exclusive weapon Spine rigs (`Oliveira`, `Scarlett`, `Evelyn`) |
| **TOTAL** | **110** | All 110 2D Spine hero skin bundles |

### 8.2 Complete 110-Bundle 2D Spine Hero Skins Catalog
| # | Season | Faction | Hero ID | Display Name (`hero_skin_spine`) | Category | Skin / Shop / Weapon | Folder (`models/...`) | Atlas & Spine Files |
|---:|---|---|---:|---|---|---|---|---|
| 1 | `Pre-Season 1` | `Blood Rose` | 1007 | **Audrey - Default** | `default` | - | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Audrey - Default/` | `Hero-Muay-Thai-Girl-Game.png` (2 spine files) |
| 2 | `Pre-Season 1` | `Blood Rose` | 1016 | **Ava - Ava's Unconventional Outfit I** | `affection` | skin=2502 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Ava - Ava's Unconventional Outfit I/` | `hero-37-1.png` (2 spine files) |
| 3 | `Pre-Season 1` | `Blood Rose` | 1016 | **Ava - Default** | `default` | skin=2501 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Ava - Default/` | `Hero-ava-game.png, Hero-ava-game-R.png` (4 spine files) |
| 4 | `Pre-Season 1` | `Blood Rose` | 1011 | **Giselle - Default** | `default` | - | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Giselle - Default/` | `Hero-Crowbar-Girl-Game.png` (2 spine files) |
| 5 | `Pre-Season 1` | `Blood Rose` | 11001 | **Katrina - Default** | `default` | skin=2101 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Katrina - Default/` | `Hero-nvjingcha-high-game.png, Hero-nvjingcha-high-game-R.png` (4 spine files) |
| 6 | `Pre-Season 1` | `Blood Rose` | 11001 | **Katrina - Electro Diva** | `purchasable` | skin=2105, shop=1001013 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Katrina - Electro Diva/` | `hero-33-6-full.png` (2 spine files) |
| 7 | `Pre-Season 1` | `Blood Rose` | 11001 | **Katrina - Katrina's Gown II** | `affection` | skin=2103 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Katrina - Katrina's Gown II/` | `hero-33-3.png` (2 spine files) |
| 8 | `Pre-Season 1` | `Blood Rose` | 11001 | **Katrina - Katrina's Gown III** | `affection` | skin=2104 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Katrina - Katrina's Gown III/` | `hero-33-4.png` (2 spine files) |
| 9 | `Pre-Season 1` | `Blood Rose` | 11001 | **Katrina - Outfit 5** | `purchasable` | - | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Katrina - Outfit 5/` | `hero-33-7-full.png` (2 spine files) |
| 10 | `Pre-Season 1` | `Blood Rose` | 2025 | **Katrina Classic - Default** | `default` | - | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Katrina Classic - Default/` | `Hero-nvjingcha-low.png` (2 spine files) |
| 11 | `Pre-Season 1` | `Blood Rose` | 1002 | **Miranda - Default** | `default` | skin=1301 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Miranda - Default/` | `Hero-Blond-Spy.png` (2 spine files) |
| 12 | `Pre-Season 1` | `Blood Rose` | 1002 | **Miranda - Miranda's Passion I** | `affection` | skin=1302 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Miranda - Miranda's Passion I/` | `hero-08-1.png` (2 spine files) |
| 13 | `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia - Default** | `default` | skin=1901 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Sophia - Default/` | `Hero-Tujinv.png` (2 spine files) |
| 14 | `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia - Magic of Fate** | `purchasable` | skin=1914, shop=1001004 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Sophia - Magic of Fate/` | `hero-25-5-full.png` (2 spine files) |
| 15 | `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia - Sophia's Training I** | `affection` | skin=1902 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Sophia - Sophia's Training I/` | `hero-25-2.png` (2 spine files) |
| 16 | `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia - Sophia's Training II** | `affection` | skin=1903 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Sophia - Sophia's Training II/` | `hero-25-3.png` (2 spine files) |
| 17 | `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia - Sophia's Training III** | `affection` | skin=1904 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Sophia - Sophia's Training III/` | `hero-25-4.png` (2 spine files) |
| 18 | `Pre-Season 1` | `Blood Rose` | 1006 | **Sophia - Stage Battle** | `stage_variant` | - | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Sophia - Stage Battle/` | `Hero-tujinv-game.png` (2 spine files) |
| 19 | `Pre-Season 1` | `Blood Rose` | 1008 | **Vivian - Default** | `default` | skin=2401 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Vivian - Default/` | `Hero-tunvlang-game.png, Hero-tunvlang-game-R.png` (4 spine files) |
| 20 | `Pre-Season 1` | `Blood Rose` | 1008 | **Vivian - Vivian's Other Side I** | `affection` | skin=2402 | `models/Pre-Season 1/Blood Rose/Hero Skins 2D Spine/Vivian - Vivian's Other Side I/` | `hero-36-1.png` (2 spine files) |
| 21 | `Pre-Season 1` | `Guard of Order` | 33002 | **Athena - Default** | `default` | - | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Athena - Default/` | `Hero-Athena-game.png` (2 spine files) |
| 22 | `Pre-Season 1` | `Guard of Order` | 1003 | **Chinatsu - Chinatsu's Hug III** | `affection` | skin=2804 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Chinatsu - Chinatsu's Hug III/` | `hero-05-3.png` (2 spine files) |
| 23 | `Pre-Season 1` | `Guard of Order` | 1003 | **Chinatsu - Default** | `default` | skin=2801 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Chinatsu - Default/` | `Hero-JK-Girl.png` (2 spine files) |
| 24 | `Pre-Season 1` | `Guard of Order` | 1003 | **Chinatsu - New Year Greeting** | `purchasable` | skin=2805, shop=1001015 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Chinatsu - New Year Greeting/` | `hero-05-4-full.png` (2 spine files) |
| 25 | `Pre-Season 1` | `Guard of Order` | 1003 | **Chinatsu - Sailor Set** | `purchasable` | skin=2803, shop=1001005 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Chinatsu - Sailor Set/` | `hero-05-2.png` (2 spine files) |
| 26 | `Pre-Season 1` | `Guard of Order` | 1018 | **Elizabeth - Default** | `default` | skin=1101 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Elizabeth - Default/` | `Hero-Suncha-Girl.png` (2 spine files) |
| 27 | `Pre-Season 1` | `Guard of Order` | 1018 | **Elizabeth - Elizabeth's Wildness I** | `affection` | skin=1102 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Elizabeth - Elizabeth's Wildness I/` | `hero-06-1.png` (2 spine files) |
| 28 | `Pre-Season 1` | `Guard of Order` | 1019 | **Leah - Default** | `default` | skin=1801 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Leah - Default/` | `Hero-Female-Archer-Game.png` (2 spine files) |
| 29 | `Pre-Season 1` | `Guard of Order` | 1019 | **Leah - Leah's Bind I** | `affection` | skin=1802 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Leah - Leah's Bind I/` | `hero-22-1.png` (2 spine files) |
| 30 | `Pre-Season 1` | `Guard of Order` | 1015 | **Maria - Default** | `default` | skin=1701 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Maria - Default/` | `Hero-Xiunv-Game.png` (2 spine files) |
| 31 | `Pre-Season 1` | `Guard of Order` | 1015 | **Maria - Maria's Confession I** | `affection` | skin=1702 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Maria - Maria's Confession I/` | `hero-20-1.png` (2 spine files) |
| 32 | `Pre-Season 1` | `Guard of Order` | 1017 | **Mia - Bavarian Maid** | `purchasable` | skin=1205, shop=1001014 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Mia - Bavarian Maid/` | `hero-07-4.png` (2 spine files) |
| 33 | `Pre-Season 1` | `Guard of Order` | 1017 | **Mia - Default** | `default` | skin=1201 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Mia - Default/` | `Hero-Chain-Girl-game.png` (2 spine files) |
| 34 | `Pre-Season 1` | `Guard of Order` | 1017 | **Mia - Mia's Pride II** | `affection` | skin=1203 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Mia - Mia's Pride II/` | `hero-07-2.png` (2 spine files) |
| 35 | `Pre-Season 1` | `Guard of Order` | 1017 | **Mia - Mia's Pride III** | `affection` | skin=1204 | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/Mia - Mia's Pride III/` | `hero-07-3.png` (2 spine files) |
| 36 | `Pre-Season 1` | `Guard of Order` | 32001 | **William - Default** | `default` | - | `models/Pre-Season 1/Guard of Order/Hero Skins 2D Spine/William - Default/` | `Hero-nanzhu-game.png, Hero-nanzhu-game-full.png` (4 spine files) |
| 37 | `Pre-Season 1` | `NPCs and Survivors` | 1007 | **Survivor Nurse - Default** | `default` | - | `models/Pre-Season 1/NPCs and Survivors/Hero Skins 2D Spine/Survivor Nurse - Default/` | `Hero-Fenhushi-Game.png` (2 spine files) |
| 38 | `Pre-Season 1` | `Wings of Dawn` | 22001 | **Amelia - Amelia's Gentle Blush II** | `affection` | skin=1003 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Amelia - Amelia's Gentle Blush II/` | `hero-01-2.png` (2 spine files) |
| 39 | `Pre-Season 1` | `Wings of Dawn` | 22001 | **Amelia - Amelia's Gentle Blush III** | `affection` | skin=1004 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Amelia - Amelia's Gentle Blush III/` | `hero-01-3.png` (2 spine files) |
| 40 | `Pre-Season 1` | `Wings of Dawn` | 22001 | **Amelia - Default** | `default` | skin=1001 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Amelia - Default/` | `Hero-Nvjvjishou.png` (2 spine files) |
| 41 | `Pre-Season 1` | `Wings of Dawn` | 22001 | **Amelia - Silver Surf** | `purchasable` | skin=1005, shop=1001012 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Amelia - Silver Surf/` | `hero-01-4-full.png` (2 spine files) |
| 42 | `Pre-Season 1` | `Wings of Dawn` | 22003 | **Angelina - Angelina's Wet & Wild I** | `affection` | skin=2302 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Angelina - Angelina's Wet & Wild I/` | `Hero-hushi-v2-game.png` (2 spine files) |
| 43 | `Pre-Season 1` | `Wings of Dawn` | 22003 | **Angelina - Default** | `default` | skin=2301 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Angelina - Default/` | `Hero-hushi-game.png` (2 spine files) |
| 44 | `Pre-Season 1` | `Wings of Dawn` | 22003 | **Angelina - Default ME** | `regional_default` | skin=2301 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Angelina - Default ME/` | `Hero-hushi-game.png` (2 spine files) |
| 45 | `Pre-Season 1` | `Wings of Dawn` | 12001 | **Christina - Christina's Chill Vibe I** | `affection` | skin=2602 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Christina - Christina's Chill Vibe I/` | `hero-39-1.png` (2 spine files) |
| 46 | `Pre-Season 1` | `Wings of Dawn` | 12001 | **Christina - Default** | `default` | skin=2601 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Christina - Default/` | `Hero-wuzhe-game.png` (2 spine files) |
| 47 | `Pre-Season 1` | `Wings of Dawn` | 22002 | **Fiona - Default** | `default` | skin=2303 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Fiona - Default/` | `Hero-Spitfire-Woman.png, Hero-Spitfire-Woman-R.png` (4 spine files) |
| 48 | `Pre-Season 1` | `Wings of Dawn` | 22002 | **Fiona - Fiona's New Style I** | `affection` | skin=2304 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Fiona - Fiona's New Style I/` | `hero-35-12.png` (2 spine files) |
| 49 | `Pre-Season 1` | `Wings of Dawn` | 33001 | **Isabella - Default** | `default` | skin=1501 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Isabella - Default/` | `Hero-Widow-spy.png` (2 spine files) |
| 50 | `Pre-Season 1` | `Wings of Dawn` | 33001 | **Isabella - Nightstalker** | `purchasable` | skin=1502, shop=1001006 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Isabella - Nightstalker/` | `hero-16-1.png` (2 spine files) |
| 51 | `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura - Avenging Angel** | `purchasable` | skin=2706, shop=1001002 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Laura - Avenging Angel/` | `hero-40-5-full.png` (2 spine files) |
| 52 | `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura - Coastal Chill** | `purchasable` | skin=2707, shop=1001011 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Laura - Coastal Chill/` | `hero-40-6-full.png` (2 spine files) |
| 53 | `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura - Default** | `default` | skin=2701 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Laura - Default/` | `Hero-nvlieshou-game.png` (2 spine files) |
| 54 | `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura - Laura's Xmas** | `purchasable` | skin=2705, shop=1001001 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Laura - Laura's Xmas/` | `hero-40-4-full.png` (2 spine files) |
| 55 | `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura - Rebel** | `purchasable` | skin=2704, shop=1001010 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Laura - Rebel/` | `hero-40-3.png` (2 spine files) |
| 56 | `Pre-Season 1` | `Wings of Dawn` | 1012 | **Laura - Red Flash** | `purchasable` | skin=2703, shop=1001009 | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Laura - Red Flash/` | `hero-40-2.png` (2 spine files) |
| 57 | `Pre-Season 1` | `Wings of Dawn` | 1021 | **Natalie - Default** | `default` | - | `models/Pre-Season 1/Wings of Dawn/Hero Skins 2D Spine/Natalie - Default/` | `Hero-Crossbow-Girl-Game.png` (2 spine files) |
| 58 | `Season 1` | `Blood Rose` | 1004 | **Oliveira - Bad Girl** | `purchasable` | skin=1403, shop=1001007 | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Oliveira - Bad Girl/` | `hero-10-2.png` (2 spine files) |
| 59 | `Season 1` | `Blood Rose` | 1004 | **Oliveira - Default** | `default` | skin=1401 | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Oliveira - Default/` | `hero-10.png` (2 spine files) |
| 60 | `Season 1` | `Blood Rose` | 1004 | **Oliveira - Exclusive Weapon** | `exclusive_weapon` | weapon=Oli's Sugar Stick | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Oliveira - Exclusive Weapon/` | `hero-10-ExclusiveEquip.png` (2 spine files) |
| 61 | `Season 1` | `Blood Rose` | 1004 | **Oliveira - Fool's Folly** | `purchasable` | skin=1405, shop=1001003 | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Oliveira - Fool's Folly/` | `hero-10-4-full.png` (2 spine files) |
| 62 | `Season 1` | `Blood Rose` | 1004 | **Oliveira - Subtle Hippie** | `purchasable` | skin=1404, shop=1001008 | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Oliveira - Subtle Hippie/` | `hero-10-3.png` (2 spine files) |
| 63 | `Season 1` | `Blood Rose` | 5000 | **Selena - Default** | `default` | skin=2901 | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Selena - Default/` | `hero-41-full.png` (2 spine files) |
| 64 | `Season 1` | `Blood Rose` | 5000 | **Selena - Exclusive Weapon** | `exclusive_weapon` | weapon=IronHeart | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Selena - Exclusive Weapon/` | `hero-41-full-ExclusiveEquip.png` (2 spine files) |
| 65 | `Season 1` | `Blood Rose` | 5000 | **Selena - Jingle Bear** | `purchasable` | skin=2902 | `models/Season 1/Blood Rose/Hero Skins 2D Spine/Selena - Jingle Bear/` | `hero-41-1-full.png` (2 spine files) |
| 66 | `Season 1` | `Guard of Order` | 33003 | **Evelyn - Default** | `default` | skin=2001 | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Evelyn - Default/` | `Hero-Female-Gunner-Game.png` (2 spine files) |
| 67 | `Season 1` | `Guard of Order` | 33003 | **Evelyn - Evelyn's Tactical Underwear II** | `affection` | skin=2003 | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Evelyn - Evelyn's Tactical Underwear II/` | `hero-27-2.png` (2 spine files) |
| 68 | `Season 1` | `Guard of Order` | 33003 | **Evelyn - Evelyn's Tactical Underwear III** | `affection` | skin=2004 | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Evelyn - Evelyn's Tactical Underwear III/` | `hero-27-3.png` (2 spine files) |
| 69 | `Season 1` | `Guard of Order` | 33003 | **Evelyn - Exclusive Weapon** | `exclusive_weapon` | weapon=Starlight | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Evelyn - Exclusive Weapon/` | `Hero-Female-Gunner-Game-ExclusiveEquip.png` (2 spine files) |
| 70 | `Season 1` | `Guard of Order` | 33003 | **Evelyn - Turkey Temptress** | `purchasable` | skin=2005 | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Evelyn - Turkey Temptress/` | `hero-27-4-full.png` (2 spine files) |
| 71 | `Season 1` | `Guard of Order` | 5002 | **Sakura - Default** | `default` | skin=3701 | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Sakura - Default/` | `hero-43-full.png` (2 spine files) |
| 72 | `Season 1` | `Guard of Order` | 5002 | **Sakura - Exclusive Weapon** | `exclusive_weapon` | weapon=Kien | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Sakura - Exclusive Weapon/` | `hero-42-full-ExclusiveEquip.png` (2 spine files) |
| 73 | `Season 1` | `Guard of Order` | 5002 | **Sakura - Football Cutie** | `purchasable` | skin=3702 | `models/Season 1/Guard of Order/Hero Skins 2D Spine/Sakura - Football Cutie/` | `hero-43-b.png` (2 spine files) |
| 74 | `Season 1` | `Wings of Dawn` | 5001 | **Nyx - Default** | `default` | skin=3001 | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Nyx - Default/` | `hero-42-full.png` (2 spine files) |
| 75 | `Season 1` | `Wings of Dawn` | 5001 | **Nyx - Exclusive Weapon** | `exclusive_weapon` | weapon=Barbie-Kill | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Nyx - Exclusive Weapon/` | `hero-43-full-ExclusiveEquip.png` (2 spine files) |
| 76 | `Season 1` | `Wings of Dawn` | 5001 | **Nyx - Scarlet Prophet** | `purchasable` | skin=3002 | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Nyx - Scarlet Prophet/` | `hero-3001-1-full.png` (2 spine files) |
| 77 | `Season 1` | `Wings of Dawn` | 21001 | **Scarlett - Default** | `default` | skin=1601 | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Default/` | `Hero-Maid-Game.png` (2 spine files) |
| 78 | `Season 1` | `Wings of Dawn` | 21001 | **Scarlett - Exclusive Weapon** | `exclusive_weapon` | weapon=Chomp Champ | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Exclusive Weapon/` | `Hero-Maid-Game-ExclusiveEquip.png` (2 spine files) |
| 79 | `Season 1` | `Wings of Dawn` | 21001 | **Scarlett - Scarlett's Unwind II** | `affection` | skin=1603 | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Scarlett's Unwind II/` | `hero-19-2.png` (2 spine files) |
| 80 | `Season 1` | `Wings of Dawn` | 21001 | **Scarlett - Scarlett's Unwind III** | `affection` | skin=1604 | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Scarlett's Unwind III/` | `hero-19-3.png` (2 spine files) |
| 81 | `Season 1` | `Wings of Dawn` | 21001 | **Scarlett - Witch's Lure** | `purchasable` | skin=1605 | `models/Season 1/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Witch's Lure/` | `hero-19-4.png` (2 spine files) |
| 82 | `Season 2` | `Blood Rose` | 5003 | **Bella - Default** | `default` | skin=3101 | `models/Season 2/Blood Rose/Hero Skins 2D Spine/Bella - Default/` | `hero-45-full.png` (2 spine files) |
| 83 | `Season 2` | `Blood Rose` | 5003 | **Bella - Exclusive Weapon** | `exclusive_weapon` | weapon=Midnight | `models/Season 2/Blood Rose/Hero Skins 2D Spine/Bella - Exclusive Weapon/` | `hero-45-full-ExclusiveEquip.png` (2 spine files) |
| 84 | `Season 2` | `Blood Rose` | 5003 | **Bella - Goddess of Love** | `purchasable` | skin=3102 | `models/Season 2/Blood Rose/Hero Skins 2D Spine/Bella - Goddess of Love/` | `hero-45-1.png` (2 spine files) |
| 85 | `Season 2` | `Guard of Order` | 5005 | **Harleyna - Default** | `default` | skin=3301 | `models/Season 2/Guard of Order/Hero Skins 2D Spine/Harleyna - Default/` | `hero-46-full.png` (2 spine files) |
| 86 | `Season 2` | `Guard of Order` | 5005 | **Harleyna - Exclusive Weapon** | `exclusive_weapon` | weapon=Ms. Wrecker | `models/Season 2/Guard of Order/Hero Skins 2D Spine/Harleyna - Exclusive Weapon/` | `hero-46-full-ExclusiveEquip.png` (2 spine files) |
| 87 | `Season 2` | `Wings of Dawn` | 5004 | **Alma - Default** | `default` | skin=3201 | `models/Season 2/Wings of Dawn/Hero Skins 2D Spine/Alma - Default/` | `hero-44-full.png` (2 spine files) |
| 88 | `Season 2` | `Wings of Dawn` | 5004 | **Alma - Exclusive Weapon** | `exclusive_weapon` | weapon=Kiss of Eden | `models/Season 2/Wings of Dawn/Hero Skins 2D Spine/Alma - Exclusive Weapon/` | `hero-44-full-ExclusiveEquip.png` (2 spine files) |
| 89 | `Season 3` | `Blood Rose` | 5006 | **Licia - Default** | `default` | skin=3401 | `models/Season 3/Blood Rose/Hero Skins 2D Spine/Licia - Default/` | `hero-47-full.png` (2 spine files) |
| 90 | `Season 3` | `Blood Rose` | 5006 | **Licia - Exclusive Weapon** | `exclusive_weapon` | weapon=Claw of Isis | `models/Season 3/Blood Rose/Hero Skins 2D Spine/Licia - Exclusive Weapon/` | `hero-47-full-ExclusiveEquip.png` (2 spine files) |
| 91 | `Season 3` | `Guard of Order` | 5008 | **Dodomeki - Default** | `default` | skin=3601 | `models/Season 3/Guard of Order/Hero Skins 2D Spine/Dodomeki - Default/` | `hero-49.png` (2 spine files) |
| 92 | `Season 3` | `Guard of Order` | 5008 | **Dodomeki - Exclusive Weapon** | `exclusive_weapon` | weapon=YAMATO | `models/Season 3/Guard of Order/Hero Skins 2D Spine/Dodomeki - Exclusive Weapon/` | `hero-49-ExclusiveEquip.png` (2 spine files) |
| 93 | `Season 3` | `Wings of Dawn` | 5007 | **Liliana - Default** | `default` | skin=3501 | `models/Season 3/Wings of Dawn/Hero Skins 2D Spine/Liliana - Default/` | `hero-48-full.png` (2 spine files) |
| 94 | `Season 3` | `Wings of Dawn` | 5007 | **Liliana - Exclusive Weapon** | `exclusive_weapon` | weapon=Child of Leviathan | `models/Season 3/Wings of Dawn/Hero Skins 2D Spine/Liliana - Exclusive Weapon/` | `hero-48-full-ExclusiveEquip.png` (2 spine files) |
| 95 | `Season 3` | `Wings of Dawn` | 2009 | **Victor - Default** | `default` | - | `models/Season 3/Wings of Dawn/Hero Skins 2D Spine/Victor - Default/` | `hero-VictorEverlast-full.png` (2 spine files) |
| 96 | `Season 4` | `Blood Rose` | 1004 | **Oliveira - Awakened Appearance** | `awakening` | skin=1406 | `models/Season 4/Blood Rose/Hero Skins 2D Spine/Oliveira - Awakened Appearance/` | `hero-1004-Wakeup-ExclusiveEquipWeapon.png` (2 spine files) |
| 97 | `Season 4` | `Blood Rose` | 1004 | **Oliveira - Awakened Exclusive Weapon** | `awakened_exclusive_weapon` | weapon=Oli's Sugar Stick | `models/Season 4/Blood Rose/Hero Skins 2D Spine/Oliveira - Awakened Exclusive Weapon/` | `hero-10-ExclusiveEquip-Wakeup.png` (2 spine files) |
| 98 | `Season 4` | `Blood Rose` | 1004 | **Oliveira - Awakening** | `awakening` | - | `models/Season 4/Blood Rose/Hero Skins 2D Spine/Oliveira - Awakening/` | `hero-1004-Wakeup01.png, hero-1004-Wakeup02.png` (4 spine files) |
| 99 | `Season 4` | `Blood Rose` | 5009 | **Yu Chan - Default** | `default` | - | `models/Season 4/Blood Rose/Hero Skins 2D Spine/Yu Chan - Default/` | `hero-50.png` (2 spine files) |
| 100 | `Season 4` | `Blood Rose` | 5009 | **Yu Chan - Exclusive Weapon** | `exclusive_weapon` | weapon=Azure Rime | `models/Season 4/Blood Rose/Hero Skins 2D Spine/Yu Chan - Exclusive Weapon/` | `hero-50-a.png` (2 spine files) |
| 101 | `Season 4` | `Guard of Order` | 5011 | **Amber - Default** | `default` | - | `models/Season 4/Guard of Order/Hero Skins 2D Spine/Amber - Default/` | `hero-52-full.png` (2 spine files) |
| 102 | `Season 4` | `Guard of Order` | 5011 | **Amber - Exclusive Weapon** | `exclusive_weapon` | weapon=Ifrit | `models/Season 4/Guard of Order/Hero Skins 2D Spine/Amber - Exclusive Weapon/` | `hero-52-full-ExclusiveEquip.png` (2 spine files) |
| 103 | `Season 4` | `Guard of Order` | 33003 | **Evelyn - Awakened Appearance** | `awakening` | skin=2006 | `models/Season 4/Guard of Order/Hero Skins 2D Spine/Evelyn - Awakened Appearance/` | `33003-Wakeup01-ExclusiveEquipWeapon.png` (2 spine files) |
| 104 | `Season 4` | `Guard of Order` | 33003 | **Evelyn - Awakened Exclusive Weapon** | `awakened_exclusive_weapon` | weapon=Starlight | `models/Season 4/Guard of Order/Hero Skins 2D Spine/Evelyn - Awakened Exclusive Weapon/` | `Hero-Female-Gunner-Game-ExclusiveEquip-RedWeapon.png` (2 spine files) |
| 105 | `Season 4` | `Guard of Order` | 33003 | **Evelyn - Awakening** | `awakening` | - | `models/Season 4/Guard of Order/Hero Skins 2D Spine/Evelyn - Awakening/` | `33003-Wakeup01.png, 33003-Wakeup02.png` (4 spine files) |
| 106 | `Season 4` | `Wings of Dawn` | 5010 | **Queenie - Default** | `default` | - | `models/Season 4/Wings of Dawn/Hero Skins 2D Spine/Queenie - Default/` | `hero-51.png` (2 spine files) |
| 107 | `Season 4` | `Wings of Dawn` | 5010 | **Queenie - Exclusive Weapon** | `exclusive_weapon` | weapon=Atropos | `models/Season 4/Wings of Dawn/Hero Skins 2D Spine/Queenie - Exclusive Weapon/` | `hero-51-full-ExclusiveEquip.png` (2 spine files) |
| 108 | `Season 4` | `Wings of Dawn` | 21001 | **Scarlett - Awakened Appearance** | `awakening` | skin=1606 | `models/Season 4/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Awakened Appearance/` | `hero-19-Wakeup-ExclusiveEquipWeapon.png` (2 spine files) |
| 109 | `Season 4` | `Wings of Dawn` | 21001 | **Scarlett - Awakened Exclusive Weapon** | `awakened_exclusive_weapon` | weapon=Chomp Champ | `models/Season 4/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Awakened Exclusive Weapon/` | `Hero-Maid-Game-ExclusiveEquip-RedWeapon.png` (2 spine files) |
| 110 | `Season 4` | `Wings of Dawn` | 21001 | **Scarlett - Awakening** | `awakening` | - | `models/Season 4/Wings of Dawn/Hero Skins 2D Spine/Scarlett - Awakening/` | `hero-19-Wakeup-01.png, hero-19-Wakeup-02.png` (4 spine files) |

## 9. HeinZ Hub Lightweight UI Sprite Pack (`launcher/assets/game_icons/`)

- **Core UI & Task Sprites:** `47` WebPs at `launcher/assets/game_icons/<key>.webp` (indexed in SQLite as `layer='hub_game_icon'`).
- **Hero Portrait Sprites:** `35` unique WebPs at `launcher/assets/game_icons/heroes/<sprite>.webp` covering `41` hero IDs.
- **Item Sprites:** `115` unique WebPs at `launcher/assets/game_icons/items/<sprite>.webp` covering `194` item IDs.

### All 47 Core Hub Sprites (`hub_game_icon`)
| Core Key | Unity Sprite Name | Domain | Hub WebP Path | Matched `assets/icons/` PNG | Bytes |
|---|---|---|---|---|---:|
| `diamonds` | `Common_icon_gold` | `items_bag_shops_vip` | `launcher/assets/game_icons/diamonds.webp` | `assets/icons/Pre-Season 1/Resources/Diamonds.png` | 2,536 |
| `electricity` | `Common_icon_electricity` | `items_bag_shops_vip` | `launcher/assets/game_icons/electricity.webp` | `assets/icons/Pre-Season 1/Resources/Electricity.png` | 2,472 |
| `zent` | `Common_icon_money` | `items_bag_shops_vip` | `launcher/assets/game_icons/zent.webp` | `assets/icons/Pre-Season 1/Resources/Zent.png` | 3,142 |
| `wood` | `Common_icon_wood` | `items_bag_shops_vip` | `launcher/assets/game_icons/wood.webp` | `assets/icons/Pre-Season 1/Resources/Wood.png` | 2,888 |
| `food` | `UI_Icon_shiwu` | `items_bag_shops_vip` | `launcher/assets/game_icons/food.webp` | `assets/icons/Pre-Season 1/Resources/Food.png` | 3,072 |
| `fuel` | `Common_icon_stamina` | `items_bag_shops_vip` | `launcher/assets/game_icons/fuel.webp` | `assets/icons/Pre-Season 1/Resources/Fuel.png` | 2,392 |
| `steel` | `Common_icon_steel` | `items_bag_shops_vip` | `launcher/assets/game_icons/steel.webp` | `assets/icons/Pre-Season 1/Resources/Steel.png` | 2,660 |
| `rss_box` | `Common_icon_foodbox01` | `items_bag_shops_vip` | `launcher/assets/game_icons/rss_box.webp` | `assets/icons/Pre-Season 1/Items/Blue Food Leveled Chest.png` | 3,558 |
| `boomer` | `hero_round_monster_2` | `pve_exploration_bosses` | `launcher/assets/game_icons/boomer.webp` | `assets/icons/Pre-Season 1/Monsters and Bosses/Elite Zombie.png` | 2,850 |
| `npc` | `hero_round_monster_1` | `pve_exploration_bosses` | `launcher/assets/game_icons/npc.webp` | `assets/icons/Pre-Season 1/Monsters and Bosses/Chief Creep.png` | 3,064 |
| `saga` | `c_common_img_boss5_2` | `pve_exploration_bosses` | `launcher/assets/game_icons/saga.webp` | `assets/icons/Pre-Season 1/Monsters and Bosses/Saga Zombie.png` | 2,698 |
| `tyrant` | `hero_round_monster_6` | `pve_exploration_bosses` | `launcher/assets/game_icons/tyrant.webp` | `assets/icons/Pre-Season 1/Monsters and Bosses/The Tyrant.png` | 2,956 |
| `furylord` | `hero_round_monster_11_1` | `pve_exploration_bosses` | `launcher/assets/game_icons/furylord.webp` | `assets/icons/Season 3/Monsters and Bosses/Hunter Yeti.png` | 2,880 |
| `map_kills_chain` | `UImail_icon_city_boss` | `pve_exploration_bosses` | `launcher/assets/game_icons/map_kills_chain.webp` | `assets/icons/Pre-Season 1/Alliance and World/Mail Icon City Boss.png` | 3,530 |
| `radar` | `Common_icon_radar` | `radar_detect` | `launcher/assets/game_icons/radar.webp` | `assets/icons/Pre-Season 1/Resources/Radar Energy.png` | 3,266 |
| `speedup` | `res_jaisu` | `items_bag_shops_vip` | `launcher/assets/game_icons/speedup.webp` | `assets/icons/Pre-Season 1/Items/1-hr Speedup Choice Box.png` | 4,018 |
| `badge` | `item200034` | `heroes_skills_equip` | `launcher/assets/game_icons/badge.webp` | `assets/icons/Pre-Season 1/Items/Badge.png` | 3,238 |
| `skill_book` | `Skill_Badge_orange` | `heroes_skills_equip` | `launcher/assets/game_icons/skill_book.webp` | `assets/icons/Pre-Season 1/Items/Orange Skill Book.png` | 3,302 |
| `alloy` | `item_material02` | `items_bag_shops_vip` | `launcher/assets/game_icons/alloy.webp` | `assets/icons/Pre-Season 1/Items/Enhancement Alloy.png` | 3,008 |
| `power_core` | `item_material05` | `items_bag_shops_vip` | `launcher/assets/game_icons/power_core.webp` | `assets/icons/Pre-Season 1/Items/Power Core.png` | 3,722 |
| `wrench` | `item230112` | `items_bag_shops_vip` | `launcher/assets/game_icons/wrench.webp` | `assets/icons/Pre-Season 1/Items/Golden Wrench.png` | 2,942 |
| `hero_exp` | `item230001` | `heroes_skills_equip` | `launcher/assets/game_icons/hero_exp.webp` | `assets/icons/Pre-Season 1/Items/Hero EXP.png` | 2,902 |
| `hero_shard` | `hero_fragment_orange` | `heroes_skills_equip` | `launcher/assets/game_icons/hero_shard.webp` | `assets/icons/Pre-Season 1/Hero Fragments/Universal Orange Hero Fragment.png` | 3,966 |
| `recruit` | `Recruit_icon_S4` | `heroes_skills_equip` | `launcher/assets/game_icons/recruit.webp` | `assets/icons/Season 4/Items/S4 Recruitment Ticket.png` | 3,326 |
| `hospital` | `c_dominate_Mid` | `army_troops_hospital` | `launcher/assets/game_icons/hospital.webp` | `assets/icons/Pre-Season 1/Items/Healing Potion.png` | 4,274 |
| `alliance_gift` | `alliancegift_icon_04_01` | `alliance` | `launcher/assets/game_icons/alliance_gift.webp` | `assets/icons/Pre-Season 1/Items/Alliance Basic Supply Chest.png` | 2,720 |
| `alliance_duel` | `UIallianceduel_icon_duel_Integral` | `alliance` | `launcher/assets/game_icons/alliance_duel.webp` | `assets/icons/Pre-Season 1/Alliance and World/Allianceduel Icon Duel Integral.png` | 1,580 |
| `alliance_rank` | `c_icon_AllianceRank` | `alliance` | `launcher/assets/game_icons/alliance_rank.webp` | `assets/icons/Pre-Season 1/Alliance and World/Alliance Rank.png` | 2,678 |
| `alliance_team` | `activity_icon_Allianceteam` | `alliance` | `launcher/assets/game_icons/alliance_team.webp` | `assets/icons/Pre-Season 1/Activities and Events/Activity Icon Allianceteam.png` | 1,712 |
| `red_packet` | `UIcomment_icon_redpacket` | `chat_moments_mail` | `launcher/assets/game_icons/red_packet.webp` | `assets/icons/Pre-Season 1/Items/Diamond Red Packet (Alliance).png` | 2,844 |
| `troops` | `UI_icon_soldier` | `army_troops_hospital` | `launcher/assets/game_icons/troops.webp` | `assets/icons/Pre-Season 1/Items/Soldier.png` | 2,986 |
| `bounty` | `Icon_Bounty_SS` | `trucks_bounties` | `launcher/assets/game_icons/bounty.webp` | `assets/icons/Pre-Season 1/UI HUD/Bounty Ss.png` | 3,506 |
| `truck` | `item200184` | `trucks_bounties` | `launcher/assets/game_icons/truck.webp` | `assets/icons/Pre-Season 1/Items/Trade Contract.png` | 2,742 |
| `dig` | `c_castle_dig_drop_tubiao` | `buildings_city` | `launcher/assets/game_icons/dig.webp` | `assets/icons/Pre-Season 1/Items/Alloy Pickaxe.png` | 2,866 |
| `arena` | `UImail_icon_city_arena` | `arena_pvp` | `launcher/assets/game_icons/arena.webp` | `assets/icons/Pre-Season 1/Alliance and World/Mail Icon City Arena.png` | 2,968 |
| `vip` | `vip_icon2` | `items_bag_shops_vip` | `launcher/assets/game_icons/vip.webp` | `assets/icons/Pre-Season 1/Alliance and World/VIP Icon 2.png` | 3,652 |
| `tech` | `c_shijie_icon_Tech` | `science_research_talents` | `launcher/assets/game_icons/tech.webp` | `assets/icons/Pre-Season 1/Alliance and World/Shijie Icon Tech.png` | 2,916 |
| `teleport` | `item004` | `items_bag_shops_vip` | `launcher/assets/game_icons/teleport.webp` | `assets/icons/Pre-Season 1/Items/Advanced Teleporter.png` | 3,598 |
| `chest` | `alliancegift_icon_04_01` | `items_bag_shops_vip` | `launcher/assets/game_icons/chest.webp` | `assets/icons/Pre-Season 1/Items/Alliance Basic Supply Chest.png` | 2,720 |
| `equipment` | `equipment_icon_blue1` | `heroes_skills_equip` | `launcher/assets/game_icons/equipment.webp` | `assets/icons/Pre-Season 1/Items/Random Blue Equipment Chest.png` | 2,910 |
| `building` | `item_module_building` | `buildings_city` | `launcher/assets/game_icons/building.webp` | `assets/icons/Pre-Season 1/Buildings/Energy-Focus Hubcap.png` | 3,786 |
| `shield` | `UIworld_state_icon_Underprotection` | `alliance` | `launcher/assets/game_icons/shield.webp` | `assets/icons/Pre-Season 1/Alliance and World/World State Icon Underprotection.png` | 1,474 |
| `hq` | `UImail_icon_city_alliancecenter` | `alliance` | `launcher/assets/game_icons/hq.webp` | `assets/icons/Pre-Season 1/Alliance and World/Mail Icon City Alliancecenter.png` | 3,844 |
| `mine_event` | `UIgoldmine_tab_btn01` | `events_fullprep` | `launcher/assets/game_icons/mine_event.webp` | `assets/icons/Pre-Season 1/Activities and Events/Fertile Lands.png` | 1,742 |
| `hero_battle` | `UImail_icon_city_boss` | `pve_exploration_bosses` | `launcher/assets/game_icons/hero_battle.webp` | `assets/icons/Pre-Season 1/Alliance and World/Mail Icon City Boss.png` | 3,530 |
| `daily_tasks` | `UIbattlepass_badge01` | `daily_tasks_quests` | `launcher/assets/game_icons/daily_tasks.webp` | `assets/icons/Pre-Season 1/UI HUD/Skillful Craftsman (8).png` | 3,558 |
| `vehicle` | `UIMain2.0_icon_troopcarrier` | `garage_vehicles` | `launcher/assets/game_icons/vehicle.webp` | `assets/icons/Pre-Season 1/UI HUD/Main 2.0 Icon Troopcarrier.png` | 3,026 |

## 10. Extracted World, Seasonal, Event, City & Terrain Maps (`499` PNGs in `maps/`)

All **499** extracted, stitched, binary-decoded, and rendered map PNGs (`314.40 MB`) produced by `tools/extract_all_world_maps.py` and documented in `maps/Maps Catalog.json`, `maps/Maps Catalog.csv`, and `maps/README.md`, indexed in SQLite FTS5 as `layer='game_map'` with `191` cross-layer edges linking landmarks, XML tables (`worldcity`, `volcano_land`, `volcano_building`, `volcano_area`, `volcano_res`, `desert_refresh`, `desert`, `aps_season`, `season_influence`, `season_review`, `capital_war`, `mine`, `main_city_area`, `aps_landlock`, `explore_level`), DataCenter managers, and UI windows.

### 10.1 Maps Summary by Category (`5` Categories)
| Category (`maps/<Category>/`) | Maps | Primary Megamind Domain | Scope & Contents |
|---|---:|---|---|
| `Main World Maps` | **107** | `formations_marches_world` | `3` stitched 4K world maps, `5` world quadrants, `5` decoded topology & province maps, `7` official minimap overlays, `87` individual `Province Zones/` masks |
| `Seasonal Maps` | **32** | `formations_marches_world` | Primary seasonal decoded topology maps (`Pre-Season 1`..`Season 6`), raw `1000x1000` / `1600x1600` bitmaps, `S2` desert resource tiers, `S3`/`S4` stitched 4K maps & `8` quadrants, static world atlases |
| `Event Maps` | **209** | `events_fullprep` / `alliance` / `pve_exploration_bosses` | `12` event folders: `Season Influence Territories` (`73`), `World Boss and Seasonal Events` (`34`), `Volcano War` (`16`), `Capital War` (`15`), `Dispatch and Explore` (`13`), `Desert Battlefield` (`11`), `Castle Adventure` (`10`), `Cross Server War` (`10`), `World Siege` (`10`), `World Cup` (`8`), `Landing Operations` (`5`), `Mine Events` (`4`) |
| `City and Base Maps` | **46** | `buildings_city` | `26` `Base Expansion Districts/` (`UIland_img_bg01..19`), `10` `Fog Masks/`, `10` `Main City Ground/` (`chengnei_01/02`, `chengwai`, SLG grass/ruins/mask, `lightmap`) |
| `Terrain and Biomes` | **105** | `formations_marches_world` | Ground albedos, blackearth/scorched earth, splats, mountains, volcano rock (`huoshanyan`), and convoy road textures across `Pre-Season 1`..`Season 5` |
| **TOTAL** | **499** | - | `314.40 MB` across `26` distinct subcategories (`33` category/subcategory pairs) |

### 10.2 Maps Summary by Season (`7` Season Buckets)
| Season (`Maps Catalog.json`) | Maps | Highlights |
|---|---:|---|
| `All Seasons` | **234** | `Main World Map 4K`, `World Zones and Provinces Map`, `87` `Province Zones`, `City and Base Maps` (`46`), shared events (`Castle Adventure`, `Landing Operations`, `Capital War`, `Cross Server War`, `World Siege`, `World Cup`, `Mine Events`, `Dispatch and Explore`) |
| `Pre-Season 1 Clash of Thrones` | **32** | `Pre-Season 1 Topology Map` (`2000x1730`), `Raw 1K` (`1000x1000`), `World Static Atlas Shadow`, `2` Rule Map Diagrams, `26` Terrain & Biomes textures |
| `Season 2 Wastes Watcher` | **52** | `Season 2 Wastes Watcher Topology Map`, `Season 2 Desert Resource Tiers Map` (`desert_refresh.json`), `11` `Desert Battlefield` assets, `24` Influence Territories/Rule/Review diagrams, `12` Terrain textures |
| `Season 3 Everfrost Era` | **43** | `Season 3 Everfrost World Map 4K` (x2) + `4` quadrants, `Season 3 Everfrost Era Topology Map` + `Raw 1K`, `Ice Cave` & `Snow Monster` maps, `11` Influence/Review maps, `15` Terrain textures |
| `Season 4 Dinosaur Origin` | **90** | `Season 4 Dinosaur Origin World Map 4K` (x2) + `4` quadrants, `Season 4 Dinosaur Origin Topology Map` + `Raw 1K`, `16` `Volcano War` maps, `11` S4 Dino/World Boss/Fossil maps, `18` Influence/Review maps, `36` Terrain textures |
| `Season 5 Moonlit Elegy` | **45** | `Season 5 Moonlit Elegy Topology Map` + `Raw 1K`, `4` S5 Capital War maps, `Demon Hunter`/`Vampire`/`Nightfalls`/`Ghost King` maps, `17` Influence/Review maps, `16` Terrain textures |
| `Season 6` | **3** | `Season 6 World Topology Map` (`2400x2076`, mirrored under `Main World Maps/` & `Seasonal Maps/Season 6/`) + `Season 6 World Topology Raw 1600` (`1600x1600`) |
| **TOTAL** | **499** | Indexed in `megamind_index.sqlite` (`layer='game_map'`) |

### 10.3 Complete Subcategory Breakdown (`26` Subcategories / `33` Category Pairs)
| Category | Subcategory | Maps | Megamind Domain |
|---|---|---:|---|
| `Main World Maps` | `Province Zones` | 87 | `formations_marches_world` |
| `Main World Maps` | `Official Minimap Assets` | 7 | `formations_marches_world` |
| `Main World Maps` | `Decoded World Map` | 5 | `formations_marches_world` |
| `Main World Maps` | `World Map Quadrants` | 5 | `formations_marches_world` |
| `Main World Maps` | `Stitched 4K World Map` | 3 | `formations_marches_world` |
| `Seasonal Maps` | `World Map Quadrants` | 8 | `formations_marches_world` |
| `Seasonal Maps` | `Season 3 Everfrost Era` | 6 | `formations_marches_world` |
| `Seasonal Maps` | `Season 4 Dinosaur Origin` | 5 | `formations_marches_world` |
| `Seasonal Maps` | `Season 2 Wastes Watcher` | 4 | `formations_marches_world` |
| `Seasonal Maps` | `Pre-Season 1 Clash of Thrones` | 3 | `formations_marches_world` |
| `Seasonal Maps` | `Season 5 Moonlit Elegy` | 2 | `formations_marches_world` |
| `Seasonal Maps` | `Season 6` | 2 | `formations_marches_world` |
| `Seasonal Maps` | `Stitched 4K World Map` | 2 | `formations_marches_world` |
| `Event Maps` | `Season Influence Territories` | 73 | `alliance` |
| `Event Maps` | `World Boss and Seasonal Events` | 34 | `pve_exploration_bosses` |
| `Event Maps` | `Volcano War` | 16 | `alliance` |
| `Event Maps` | `Capital War` | 15 | `alliance` |
| `Event Maps` | `Dispatch and Explore` | 13 | `events_fullprep` |
| `Event Maps` | `Desert Battlefield` | 11 | `events_fullprep` |
| `Event Maps` | `Castle Adventure` | 10 | `events_fullprep` |
| `Event Maps` | `Cross Server War` | 10 | `alliance` |
| `Event Maps` | `World Siege` | 10 | `alliance` |
| `Event Maps` | `World Cup` | 8 | `events_fullprep` |
| `Event Maps` | `Landing Operations` | 5 | `events_fullprep` |
| `Event Maps` | `Mine Events` | 4 | `events_fullprep` |
| `City and Base Maps` | `Base Expansion Districts` | 26 | `buildings_city` |
| `City and Base Maps` | `Fog Masks` | 10 | `buildings_city` |
| `City and Base Maps` | `Main City Ground` | 10 | `buildings_city` |
| `Terrain and Biomes` | `Season 4 Dinosaur Origin` | 36 | `formations_marches_world` |
| `Terrain and Biomes` | `Pre-Season 1 Clash of Thrones` | 26 | `formations_marches_world` |
| `Terrain and Biomes` | `Season 5 Moonlit Elegy` | 16 | `formations_marches_world` |
| `Terrain and Biomes` | `Season 3 Everfrost Era` | 15 | `formations_marches_world` |
| `Terrain and Biomes` | `Season 2 Wastes Watcher` | 12 | `formations_marches_world` |

### 10.4 Key Stitched 4K, Decoded Topology & Annotated Event Maps
| Map Title | Resolution | Relative Path (`maps/...`) | Source Assets / XML Refs & Notes |
|---|---|---|---|
| **Main World Map 4K** | `4096x4096` | `maps/Main World Maps/Main World Map 4K.png` | `Worldmap_L2_01..04`; verified quadrant order `[01 TL, 02 TR / 03 BL, 04 BR]`, avg seam MAD `4.91` |
| **Season 3 Everfrost World Map 4K** | `4096x4096` | `maps/Seasonal Maps/Season 3 Everfrost Era/Season 3 Everfrost World Map 4K.png` | `Worldmap_L2_01_S3..04_S3`, avg seam MAD `2.50` (also mirrored under `maps/Main World Maps/`) |
| **Season 4 Dinosaur Origin World Map 4K** | `4096x4096` | `maps/Seasonal Maps/Season 4 Dinosaur Origin/Season 4 Dinosaur Origin World Map 4K.png` | `Worldmap_L2_01_S4..04_S4`, avg seam MAD `2.95` (also mirrored under `maps/Main World Maps/`) |
| **World Zones and Provinces Map** | `2000x1730` | `maps/Main World Maps/World Zones and Provinces Map.png` | `zone` RLE binary (`530,236 B`), `bigmap01`, `WorldBlockIndex_S0`, `worldcity.json` (`87` provinces + `90` cities/turrets) |
| **Pre-Season 1 Topology Map** | `2000x1730` | `maps/Seasonal Maps/Pre-Season 1 Clash of Thrones/Pre-Season 1 Topology Map.png` | `WorldBlockIndex_S0`, `WorldDecorateIndex_S0` (`1000x1000` LSB-first 1-bit decoded + `Raw 1K` + `Main World Maps/` mirror) |
| **Season 2 Wastes Watcher Topology Map** | `2000x1730` | `maps/Seasonal Maps/Season 2 Wastes Watcher/Season 2 Wastes Watcher Topology Map.png` | `WorldBlockIndex_S2`, `WorldDecorateIndex_S2` (+ `Raw 1K` + `Main World Maps/` mirror) |
| **Season 2 Desert Resource Tiers Map** | `2000x1730` | `maps/Seasonal Maps/Season 2 Wastes Watcher/Season 2 Desert Resource Tiers Map.png` | `zone`, `WorldBlockIndex_S2`, `desert_refresh.json` (Cactus/Crystal tile levels across `87` provinces; paired with `Desert Battlefield Resource Tiers Map`) |
| **Season 3 Everfrost Era Topology Map** | `2000x1730` | `maps/Seasonal Maps/Season 3 Everfrost Era/Season 3 Everfrost Era Topology Map.png` | `WorldBlockIndex_S3`, `WorldDecorateIndex_S3` (`1000x1000` LSB-first decoded + `Raw 1K`) |
| **Season 4 Dinosaur Origin Topology Map** | `2000x1730` | `maps/Seasonal Maps/Season 4 Dinosaur Origin/Season 4 Dinosaur Origin Topology Map.png` | `WorldBlockIndex_S4`, `WorldDecorateIndex_S4` (`1000x1000` LSB-first decoded + `Raw 1K`) |
| **Season 5 Moonlit Elegy Topology Map** | `2000x1730` | `maps/Seasonal Maps/Season 5 Moonlit Elegy/Season 5 Moonlit Elegy Topology Map.png` | `WorldBlockIndex_S5`, `WorldDecorateIndex_S5` (+ `Raw 1K` + `Main World Maps/` mirror) |
| **Season 6 World Topology Map** | `2400x2076` | `maps/Seasonal Maps/Season 6/Season 6 World Topology Map.png` | `WorldBlockIndex_S6`, `WorldDecorateIndex_S6` (`1600x1600` expanded world + `Raw 1600` + `Main World Maps/` mirror) |
| **Volcano War Tactical Map Annotated** | `1600x1186` | `maps/Event Maps/Volcano War/Volcano War Tactical Map Annotated.png` | `c_texture_vocano_map`, `c_vocano_map_select_01..05`, `volcano_land.json`, `volcano_building.json`, `volcano_area.json` (`10` sectors, energy rings, `11` Field Hospitals) |
| **Castle Adventure Map** | `1024x907` | `maps/Event Maps/Castle Adventure/Castle Adventure Map.png` | `c_texture_castle_map_base` + `c_castle_map_chip_01..05` assembled via `UICastleAdventureTreasureMapMain` RectTransform coordinates |
| **Landing Operations Full Map** | `864x6144` | `maps/Event Maps/Landing Operations/Landing Operations Full Map.png` | `LevelListBg1..3` stitched vertical 3-stage campaign map (`Landing Operations All Stages Overview` at `2592x2048`) |
| **Desert Battlefield Resource Tiers Map** | `2000x1730` | `maps/Event Maps/Desert Battlefield/Desert Battlefield Resource Tiers Map.png` | `zone`, `WorldBlockIndex_S2`, `desert_refresh.json` |

## 11. Extraction, Cleaning & Megamind Indexing Pipeline

| Step | Script | Lines | Role & Key Behavior |
|---|---|---:|---|
| **1. Extract Icons** | `tools/extract_all_game_icons.py` | 2,036 | Scans `498` AssetBundles + `resources.assets`, strips 8-byte `UnityRaw` header, extracts sliced `Sprite`s + `TMP_SpriteAsset` glyphs + standalone textures, crops edge-to-edge (`alpha > 4`), resolves English names from XML/loc. |
| **2. Sort & Clean Icons** | `tools/sort_clean_game_icons.py` | 1,789 | Resolves `Pre-Season 1`..`Season 6` (accounting for 0-based `world_season` vs 1-based hero/item seasons), maps 22 clean categories, enforces zero underscores/em-dashes & `<=55` char stems, resolves collisions by pixel area, writes `Icons Catalog.json`/`.csv`/`README.md`. |
| **3. Extract 3D Models** | `tools/extract_all_game_models.py` | 1,979 | Scans model AssetBundles, unpacks DXT5nm normal maps, writes wired `.obj` + `materials.mtl` + self-contained textured `.glb` + `model-info.json`. |
| **4. Sort & Clean Models** | `tools/sort_clean_game_models.py` | 1,193 | Reorganizes 3D models into `models/<Season>/<Faction>/<Clean Model Name>/`, rewires OBJ/MTL texture paths, verifies `trimesh` GLB geometry. |
| **5. Match & Extract Skins** | `tools/match_purchasable_skins.py` | 2,943 | Extracts/matches `28` `HQ Skins`, `28` `Vehicle Skins`, `Blackland Ruin` + `11` new/split 3D models (`493` total 3D), plus all `110` `Hero Skins 2D Spine` bundles (`603` total catalog assets), writes `Models Catalog.json`/`.csv`, `Hero Skins Spine Catalog.csv`, and `models/README.md`. |
| **6. Extract & Stitch Maps** | `tools/extract_all_world_maps.py` | 2,064 | Extracts, stitches (`4K` world quadrants, `Castle Adventure`, `Landing Operations`), decodes (`zone` RLE provinces, `WorldBlockIndex_S0..S6` LSB-first 1-bit topology), annotates (`Volcano War`, `Desert`), and exports `499` clean PNGs (`maps/`) + `Maps Catalog.json`/`.csv`/`README.md` using `worldcity`, `desert_refresh`, `volcano_land`/`building`/`area`/`res`. |
| **7. Update Megamind** | `megamind/update_assets_index.py` | 1,664 | Idempotently rebuilds `megamind/raw/game_assets_icons_and_models.json` and replaces `game_icon` (`17,049`), `game_model` (`493`), `hero_skin_spine` (`110`), `hub_game_icon` (`47`), and `game_map` (`499`) rows + `1,020` asset `edges` in `megamind/megamind_index.sqlite` with FTS5 parity verification. |
| **8. Query CLI** | `megamind/megamind_query.py` | 1,190 | Searches icons (`icon`), 3D models & 2D Spine skins (`model`), and exported maps (`map <query> [--category X] [--season Y]`), includes `game_map` in `trace` Section 9, and summarizes all asset + map totals in `summary`. |

## 12. `megamind_query.py` Usage Examples

```powershell
# Search extracted icons + Hub sprites by clean English name OR raw Unity sprite name
python megamind/megamind_query.py icon Zent
python megamind/megamind_query.py icon "Frost Core"
python megamind/megamind_query.py icon Common_icon_money
python megamind/megamind_query.py icon Oliveira --season "Season 1" --category "Hero Portraits Round"

# Search extracted 3D models AND 2D Spine Hero Skins (supports --season, --faction, --type)
python megamind/megamind_query.py model "The Inferno"
python megamind/megamind_query.py model "Destroyer-EX"
python megamind/megamind_query.py model "Magic of Fate"
python megamind/megamind_query.py model "Santa Chaos"
python megamind/megamind_query.py model "Heartfelt Fox"
python megamind/megamind_query.py model "Bad Girl"
python megamind/megamind_query.py model Oliveira
python megamind/megamind_query.py model "*" --faction "HQ Skins"
python megamind/megamind_query.py model "*" --type spine --season "Season 1"

# Search all 499 exported world, seasonal, event, city & terrain maps (supports --category, --season)
python megamind/megamind_query.py map "Everfrost 4K"
python megamind/megamind_query.py map "Volcano War"
python megamind/megamind_query.py map "Season 6"
python megamind/megamind_query.py map "Castle Adventure"
python megamind/megamind_query.py map "Landing Operations"
python megamind/megamind_query.py map "Provinces"
python megamind/megamind_query.py map "Desert"
python megamind/megamind_query.py map --category "Seasonal Maps" --season "Season 3"

# Cross-layer FTS5 & end-to-end trace (includes Section 9: Icons, 3D Models & World Maps)
python megamind/megamind_query.py fts "Magic of Fate" --layer hero_skin_spine
python megamind/megamind_query.py fts "Volcano War" --layer game_map
python megamind/megamind_query.py trace Volcano
python megamind/megamind_query.py trace Sophia
python megamind/megamind_query.py summary
```
