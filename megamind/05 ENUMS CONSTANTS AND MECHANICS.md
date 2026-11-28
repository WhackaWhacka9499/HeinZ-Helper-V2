# Volume 05: Game Enums, Constants & Verified Engine Mechanics

> **Generated:** `2026-11-23 10:42:43 UTC` | **Source:** `megamind/raw/enums_complete.json` + Empirical Runtime Verification on `Alt3Game.exe` (`v579`)

## 1. Empirically Verified Unity / xLua / SFS Game Engine Mechanics

| Subsystem | Verified Mechanism & Exact Rule |
|---|---|
| **Frida xLua Bridge** | Single persistent `Interceptor.attach` hook on `xlua.dll!lua_pcallk` executes queued Lua jobs on Unity's main thread without trampoline detach races (`0xC0000005`). |
| **Lua Class VTables** | `BaseClass` classes store methods on `getmetatable(cls).__index` (`vtbl`), NOT directly on the instance table. Always inspect both `obj` and `getmetatable(obj).__index`. |
| **Network Dispatch** | `SFSNetwork.SendMessage(cmd, ...)` resolves `cmd` via upvalue `GetMsgType` (`MsgMap` 2,192 + `SlgMsgMap` 271 + `SlgMsgMapOverride` 193), instantiates class `OnCreate`, sends `SFSObject`, and dispatches server response to `HandleMessage`. |
| **Scene Contexts (`SceneManager.CurrSceneID`)** | `1` = City / Base scene; `2` = World Map scene; PVE battle scenes run overlay logic (`BattleLevel`, `PveActorMgr`, `LWBattleManager`). Some operations (like `BuildManager:UpgradeBuilding`) assume City scene and fail with `robotUuid=0` from World scene unless sending `MsgDefines.FreeBuildingUpNew` directly with a free `robotUuid`. |
| **Building Completion & Upgrades** | Completed builds require `DataCenter.BuildManager:CheckSendBuildFinish(uuid, false, true)` to flush state. Upgrades via `MsgDefines.FreeBuildingUpNew` must supply an actually free builder `robotUuid` from `BuildQueueManager`. |
| **PVE Auto-Skip Mechanics** | In Area Exploration & Hero Battlefield, `SceneManager:IsInPVE()` may be `false` even while a PVE fight is live. Safe skip requires `PveActorMgr.startPlay == true and not PveActorMgr.onPreStart`, calling `PveActorMgr:ShowResult(true)` **before** `ForceShowResultFlag()`, or `DataCenter.LWBattleManager:Skip()` where supported. |
| **Formation & March Accounting** | Total unlocked formations come from `DataCenter.ArmyFormationDataManager:GetUnlockFormationCount()`; free formations from `GetFreeFormationCount()` reconciled against `DataCenter.WorldMarchDataManager.allMarches`. Tasks consuming squads (Mine Melee, Radar, Boomer, Gather, Trucks) share this pool. |
| **Daily Tasks & Chests** | `DataCenter.DailyTaskManager` tracks `dailyQuestTasks`, `GetDailyCurValue()` / `GetDailyMaxValue()` (`150`), and 5 milestone chests (`rewardList`). Daily quest metadata lives in `TableName.DailyQuest` (`52` rows). |
| **Full Preparedness / Arms Race Themes** | `DataCenter.ActPersonalArmsInfo.list` tracks the active hourly/daily Full Preparedness theme (`Age of Science`, `Shelter Upgrade`, `Hero Initiative`, `Mod Vehicle Boost`, `Unit Progression`). Speedups must be matched strictly to the active theme to avoid off-theme waste. |
| **UI & Button Components** | Clickable HUD buttons use `CS.NewButton` (subclass of `UnityEngine.UI.Button`) with `CS.NewTMPText` labels under `UIContainer/*` (`11` layers, `40` active Canvases). `UI.Config.UIConfig` maps window names to lazy Lua `*.Config` modules. |
| **XML Table Access** | `LocalController.instance():getTable(TableName.<X>)` returns `{ index = { col = [idx, type] }, data = { id = ... } }`; rows are read via `lc:getLine(xml, tostring(id))[col]` and localized via `Localization.GetString(id)`. |

## 2. Priority Core Gameplay Enums (Selected from 1,274 Total Enum Tables)

### `AllianceCityBattleType` (3 entries)
| Key | Value |
|---|---|
| `None` | `0` |
| `SelfServer` | `1` |
| `CrossServer` | `2` |

### `ArmyFormationState` (2 entries)
| Key | Value |
|---|---|
| `Free` | `0` |
| `March` | `1` |

### `BattleType` (51 entries)
| Key | Value |
|---|---|
| `None` | `0` |
| `Formation` | `1` |
| `Building` | `2` |
| `Turret` | `3` |
| `Monster` | `4` |
| `RallyFormation` | `5` |
| `Boss` | `6` |
| `City` | `7` |
| `Road` | `8` |
| `Explore` | `9` |
| `ALLIANCE_NEUTRAL_CITY` | `10` |
| `ALLIANCE_OCCUPIED_CITY` | `11` |
| `ELITE_FIGHT_MAIL` | `12` |
| `PVE_MARCH` | `13` |
| `PVE_MONSTER` | `14` |
| `ACT_BOSS` | `15` |
| `PUZZLE_BOSS` | `16` |
| `CHALLENGE_BOSS` | `17` |
| `Desert` | `18` |
| `TRAIN_DESERT` | `19` |
| `ALLIANCE_BUILDING` | `20` |
| `NpcCity` | `21` |
| `ALLIANCE_CITY_GUARD` | `22` |
| `CITY_GUARD` | `23` |
| `ALLIANCE_BUILD_GUARD` | `24` |
| `NPC_CITY_GUARD` | `25` |
| `BLACK_KNIGHT` | `26` |
| `THRONE_ARMY` | `27` |
| `CROSS_WORM` | `28` |
| `AllianceBoss` | `30` |
| `DRAGON_BUILDING` | `33` |
| `Train_March` | `36` |
| `ALLIANCE_THRONE_TOWER` | `37` |
| `DRAGON_BOSS` | `38` |
| `ACT_RESOURCE` | `39` |
| `TRADE_POST` | `40` |
| `ROAMING_BOSS` | `41` |
| `ICE_CAVE_BOSS` | `42` |
| `ICE_CAVE_BOSS_SHIELD` | `43` |
| `GOBLIN_TREASURE_SHIELD` | `44` |
| `CAR_CHIP_TRAIL_BOSS` | `45` |
| `SEASON_ACT_BOSS_DEFEND_WALL` | `46` |
| `MonsterTower_AlBoss` | `47` |
| `BLACK_LAND_RUIN` | `48` |
| `BLOOD_MOON_BOSS` | `50` |
| `GHOST_KING` | `51` |
| `PARADE_FLOAT` | `52` |
| `BLOOD_MOON_GENERAL` | `53` |
| `PARADE_FLOAT_PRIEST` | `54` |
| `GHOST_KING_SHIELD` | `55` |
| `VOLCANO_BUILDING` | `56` |

### `BuildSceneType` (4 entries)
| Key | Value |
|---|---|
| `City` | `1` |
| `World` | `2` |
| `Fake` | `3` |
| `Alliance` | `4` |

### `BuildingTypes` (208 entries)
| Key | Value |
|---|---|
| `ALLIANCE_RES_1` | `10000` |
| `ALLIANCE_RES_2` | `11000` |
| `ALLIANCE_RES_3` | `12000` |
| `ALLIANCE_RES_4` | `20000` |
| `ALLIANCE_RES_5` | `21000` |
| `ALLIANCE_RES_6` | `22000` |
| `ALLIANCE_RES_7` | `30000` |
| `ALLIANCE_RES_8` | `31000` |
| `ALLIANCE_RES_9` | `32000` |
| `ALLIANCE_FLAG_BUILD` | `40000` |
| `ALLIANCE_CENTER_1` | `41000` |
| `ALLIANCE_CENTER_2` | `42000` |
| `ALLIANCE_CENTER_2_1` | `42001` |
| `ALLIANCE_CENTER_3` | `43000` |
| `ALLIANCE_CENTER_3_1` | `43002` |
| `ALLIANCE_CENTER_4` | `44000` |
| `ALLIANCE_CENTER_4_1` | `44003` |
| `ALLIANCE_FRONT_BUILD_1` | `45000` |
| `ALLIANCE_FRONT_BUILD_2` | `46000` |
| `ALLIANCE_FRONT_BUILD_3` | `47000` |
| `Survival_ShabbyTruck` | `100000` |
| `Survival_Cabinet` | `101000` |
| `Survival_Hearth` | `102000` |
| `Survival_AirDryRack` | `103000` |
| `Survival_WaterCollector` | `104000` |
| `Survival_WoodTable` | `105000` |
| `Survival_VegetableFarm` | `106000` |
| `Survival_LeatherRack` | `107000` |
| `Survival_MasonryTable` | `108000` |
| `Survival_ClothTable` | `109000` |
| `Survival_MeltingPot` | `110000` |
| `Survival_ArrowTower` | `120000` |
| `Survival_Fence1` | `121000` |
| `Survival_WatchTower` | `122000` |
| `Survival_Fence2` | `123000` |
| `Survival_Fence3` | `124000` |
| `Survival_Fence4` | `125000` |
| `Survival_Fence5` | `128000` |
| `Survival_Fence6` | `129000` |
| `Survival_Radio` | `131000` |
| `Survival_Bed` | `134000` |
| `Survival_WeaponFactory` | `135000` |
| `Survival_EquipFactory` | `136000` |
| `Survival_Mail` | `137000` |
| `Survival_Home` | `138000` |
| `Survival_Bar` | `139000` |
| `Survival_Home_Floor` | `139000` |
| `Survival_Bathe` | `140000` |
| `Survival_Cabinet_Newbie` | `147000` |
| `Survival_Home_Wall` | `148000` |
| `SUB_BUILD_BED` | `155000` |
| `SUB_BUILD_WEAPON` | `183000` |
| `LW_BUILD_SOFA` | `184000` |
| `FUN_BUILD_RECYCLE_BIN` | `300000` |
| `Survival_Restaurant` | `301000` |
| `Survival_Intelligence` | `302000` |
| `HERO_DISPATCH_CENTER` | `303000` |
| `BUILD_FACTION_1` | `304000` |
| `BUILD_FACTION_2` | `305000` |
| `BUILD_FACTION_3` | `306000` |
| `GARAGEREFIT_DRONE` | `307000` |
| `ALLIANCE_MARK_13_FAKE` | `308000` |
| `HEROSMALL_TALENT_CENTER` | `310000` |
| `BUILD_MASTERY` | `320000` |
| `FUN_BUILD_MAIN` | `400000` |
| `FUN_BUILD_BUSINESS_CENTER` | `401000` |
| `FUND_BUILD_ALLIANCE_CENTER` | `402000` |
| `FUN_BUILD_SCIENE` | `403000` |
| `FUN_BUILD_SMITHY` | `407000` |
| `FUN_BUILD_CONDOMINIUM` | `409000` |
| `FUN_BUILD_HOSPITAL` | `411000` |
| `FUN_BUILD_STONE` | `412000` |
| `FUN_BUILD_OIL` | `413000` |
| `FUN_BUILD_STEEL` | `414000` |
| `FUN_EmergencyCenter` | `415000` |
| `FUN_BUILD_RADAR_CENTER` | `417000` |
| `FUN_BUILD_ARROW_TOWER` | `418000` |
| `FUN_BUILD_MASTERY_ARROW_TOWER` | `419000` |
| `FUN_BUILD_CAR_BARRACK` | `423000` |
| `FUN_BUILD_INFANTRY_BARRACK` | `424000` |
| `FUN_BUILD_AIRCRAFT_BARRACK` | `425000` |
| `FUN_BUILD_TRAINFIELD_1` | `427000` |
| `LW_BUILD_TRUCK_STATION_1` | `427000` |
| `FUN_BUILD_FORGE` | `429000` |
| `FUN_BUILD_ELECTRICITY` | `431000` |
| `FUN_BUILD_WATER` | `432000` |
| `FUN_BUILD_MARKET` | `435000` |
| `FUN_BUILD_ROAD` | `436000` |
| `FUN_BUILD_ELECTRICITY_STORAGE` | `437000` |
| `FUN_BUILD_WATER_STORAGE` | `438000` |
| `Survival_WareHouse` | `438000` |
| `FUN_BUILD_OIL_STORAGE` | `439000` |
| `FUN_BUILD_IRON_STORAGE` | `441000` |
| `FUN_BUILD_WIND_TURBINE` | `444000` |
| `FUN_BUILD_RECHARGE_GARAGE` | `445000` |
| `FUN_BUILD_HONOR_HALL` | `446000` |
| `FUN_BUILD_SOLAR_POWER_STATION` | `447000` |
| `FUN_BUILD_BUILDING_CENTER` | `448000` |
| `FUN_BUILD_DOME` | `449000` |
| `OVERLORD_CENTER` | `458000` |
| `OVERLORD_RESOURCE_BUILD` | `459000` |
| `DS_EQUIP_FORGE_FACTORY` | `460000` |
| `FUN_BUILD_DRONE` | `477000` |
| `FUN_BUILD_OFFICER` | `483000` |
| `FUN_BUILD_VILLA` | `700000` |
| `APS_BUILD_FARM` | `701000` |
| `APS_BUILD_FARM_FIELD` | `702000` |
| `APS_BUILD_PASTURE` | `703000` |
| `APS_BUILD_PASTURE_FIELD` | `704000` |
| `FUN_BUILD_FACTORY_STONE` | `705000` |
| `FUN_BUILD_ORE_FACTORY_2` | `705000` |
| `FUN_BUILD_METALLURGY` | `706000` |
| `FUN_BUILD_FOOD` | `707000` |
| `FUN_BUILD_OIL_REFINERY` | `708000` |
| `FUN_BUILD_INTEGRATED_FACTORY` | `709000` |
| `FUN_BUILD_ORE_FACTORY_1` | `709000` |
| `FUN_BUILD_TRADING_CENTER` | `710000` |
| `FUN_BUILD_FOODSHOP` | `711000` |
| `FUN_BUILD_PRINT_FACTORY` | `712000` |
| `FUN_BUILD_INFORMATION_CENTER` | `713000` |
| `FUN_BUILD_COLD_STORAGE` | `714000` |
| `FUN_BUILD_COMPREHENSIVE_STORAGE` | `715000` |
| `FUN_BUILD_DEFENCE_CENTER` | `716000` |
| `FUN_BUILD_FOOD_1` | `717000` |
| `FUN_BUILD_FOOD_2` | `718000` |
| `APS_BUILD_PASTURE_OSTRICH` | `719000` |
| `APS_BUILD_PASTURE_CATTLE` | `720000` |
| `APS_BUILD_PASTURE_SANDWORM` | `721000` |
| `APS_BUILD_PUB` | `722000` |
| `FUN_BUILD_PVE_FACTORY` | `723000` |
| `FUN_BUILD_GROCERY_STORE` | `724000` |
| `FUN_BUILD_SCIENCE_PART` | `725000` |
| `FUN_BUILD_POLICE_STATION` | `726000` |
| `FUN_BUILD_MARS_CAMP` | `727000` |
| `FUN_BUILD_LIBRARY` | `728000` |
| `FUN_BUILD_KONBINI` | `729000` |
| `FUN_BUILD_GREEN_CRYSTAL` | `730000` |
| `FUN_BUILD_HERO_MONUMENT` | `731000` |
| `FUN_BUILD_HERO_BOUNTY` | `732000` |
| `FUN_BUILD_HERO_OFFICE` | `733000` |
| `FUN_BUILD_HERO_BAR` | `734000` |
| `WORM_HOLE_CROSS` | `735000` |
| `FUN_BUILD_OUT_WOOD` | `736000` |
| `FUN_BUILD_OUT_STONE` | `737000` |
| `FUN_BUILD_BOOK` | `738000` |
| `FUN_BUILD_Reserve` | `739000` |
| `FUN_BUILD_BAUBLE` | `740000` |
| `SEASON_DESERT_RESISTANCE_1` | `741000` |
| `SEASON_DESERT_MAX_DESERT_1` | `742000` |
| `SEASON_DESERT_MAX_FORMATION_SIZE_1` | `743000` |
| `SEASON_DESERT_ARMY_ATTACK_1` | `744000` |
| `SEASON_DESERT_ARMY_DEFEND_1` | `745000` |
| `SEASON_DESERT_RESISTANCE_2` | `746000` |
| `SEASON_DESERT_RESISTANCE_3` | `747000` |
| `SEASON_DESERT_RESISTANCE_4` | `748000` |
| `SEASON_DESERT_MAX_DESERT_2` | `749000` |
| `SEASON_DESERT_MAX_FORMATION_SIZE_2` | `750000` |
| `SEASON_DESERT_ARMY_ATTACK_2` | `751000` |
| `SEASON_DESERT_ARMY_DEFEND_2` | `752000` |
| `SEASON_DESERT_BUILD_DRONE_1` | `753000` |
| `SEASON_DESERT_BUILD_DRONE_2` | `754000` |
| `S3_MILITARY_COMMAND_CENTER_765000` | `765000` |
| `S3_ICE_ARMY_ARMORED_BASE_766000` | `766000` |
| `S3_ICE_ARMY_BARRACKS_767000` | `767000` |
| `S3_BUILD_768000` | `768000` |
| `S3_BUILD_769000` | `769000` |
| `FUN_BUILD_DOOR` | `779000` |
| `APS_BUILD_WORMHOLE_MAIN` | `791000` |
| `APS_BUILD_WORMHOLE_SUB` | `792000` |
| `APS_BUILD_WORMHOLE_EXPORT` | `792001` |
| `FUN_BUILD_TRAINFIELD_2` | `793000` |
| `LW_BUILD_TRUCK_STATION_2` | `793000` |
| `FUN_BUILD_TRAINFIELD_3` | `794000` |
| `LW_BUILD_TRUCK_STATION_3` | `794000` |
| `FUN_BUILD_TRAINFIELD_4` | `795000` |
| `LW_BUILD_TRUCK_STATION_4` | `795000` |
| `FUN_BUILD_TEMP_WIND_POWER_PLANT` | `796000` |
| `FUN_BUILD_BARRACKS` | `797000` |
| `BAUBLE_LIBRARY` | `800000` |
| `DS_EQUIP_FACTORY` | `811000` |
| `DS_EQUIP_SMELTING_FACTORY` | `812000` |
| `DS_EQUIP_MATERIAL_FACTORY` | `813000` |
| `DS_EQUIP_SMELTING_FACTORY_2` | `814000` |
| `S4_BUILD_850000` | `850000` |
| `S3_CONTROL_GREENHOUSE_851000` | `851000` |
| `S3_CONTROL_GREENHOUSE_852000` | `852000` |
| `S3_CONTROL_GREENHOUSE_853000` | `853000` |
| `S3_CONTROL_GREENHOUSE_854000` | `854000` |
| `S3_CONTROL_GREENHOUSE_855000` | `855000` |
| `SEASON_RESOURCE_EXTRA_BUILD_S3` | `855000` |
| `S3_BIO_MEDICAL_RESEARCH_CENTER_856000` | `856000` |
| `S4_BUILD_857000` | `857000` |
| `S4_BUILD_858000` | `858000` |
| `S4_BUILD_859000` | `859000` |
| `S4_BUILD_860000` | `860000` |
| `S4_BUILD_861000` | `861000` |
| `S4_BUILD_862000` | `862000` |
| `S4_BUILD_863000` | `863000` |
| `S4_BUILD_864000` | `864000` |
| `S4_BUILD_865000` | `865000` |
| `S4_BUILD_866000` | `866000` |
| `S4_BUILD_867000` | `867000` |
| `S5_BUILD_869000` | `869000` |
| `S5_BUILD_870000` | `870000` |
| `SEASON_5_RESOURCE_BUILD_875000` | `875000` |
| `S5_BUILD_877000` | `877000` |
| `S5_BUILD_878000` | `878000` |
| `S5_BUILD_879000` | `879000` |

### `ChatChannelType` (4 entries)
| Key | Value |
|---|---|
| `CHAT_CHANNEL_COUNTRY` | `0` |
| `CHAT_CHANNEL_ALLIANCE` | `1` |
| `CHAT_CHANNEL_USER` | `2` |
| `CHAT_CHANNEL_ROOM` | `3` |

### `CommonShopType` (27 entries)
| Key | Value |
|---|---|
| `Goods` | `1` |
| `Vip` | `2` |
| `LimitTime` | `3` |
| `HeroReset` | `4` |
| `Adventure` | `5` |
| `GolloesShop` | `6` |
| `DiscountShop` | `7` |
| `AlContribute` | `8` |
| `SeasonShop` | `10` |
| `Honor` | `14` |
| `LO` | `16` |
| `FoodFestivalExchangeShop` | `21` |
| `SpeciesExchangeShopS4` | `23` |
| `HalloweenExchangeShop` | `24` |
| `ThanksGivingExchangeShop` | `25` |
| `ChristmasParkourExchangeShop` | `26` |
| `ChristmasActExchangeShop` | `27` |
| `CastleAdventureShop` | `29` |
| `ValentineExchangeShop` | `30` |
| `EasterExchangeShop` | `31` |
| `RubyShop` | `32` |
| `WorldCupExchangeShop` | `33` |
| `WorldCupZombieExchangeShop` | `34` |
| `AllianceShopPlus` | `35` |
| `ValentineNewExchangeShopFake` | `37` |
| `ValentineNewExchangeShop` | `38` |
| `HalloweenMarbleExchangeShop` | `39` |

### `ConsumeItemType` (2 entries)
| Key | Value |
|---|---|
| `AlMoveCity_LeaderInvite` | `1` |
| `AlMoveCity_SysInvite` | `2` |

### `DawnTaskState` (4 entries)
| Key | Value |
|---|---|
| `NoComplete` | `0` |
| `Received` | `1` |
| `CanReceive` | `2` |
| `Lock` | `3` |

### `DecorationSceneType` (2 entries)
| Key | Value |
|---|---|
| `Normal` | `1` |
| `MarchS4Skin` | `2` |

### `DesertAnnexItemType` (3 entries)
| Key | Value |
|---|---|
| `None` | `0` |
| `Mine` | `1` |
| `BuildStatus` | `2` |

### `DetectEventBlueColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.92941` |
| `g` | `0.63921` |
| `r` | `0.37254` |

### `DetectEventColor` (7 entries)
| Key | Value |
|---|---|
| `DETECT_EVENT_WHITE` | `1` |
| `DETECT_EVENT_GREEN` | `2` |
| `DETECT_EVENT_BLUE` | `3` |
| `DETECT_EVENT_PURPLE` | `4` |
| `DETECT_EVENT_ORANGE` | `5` |
| `DETECT_EVENT_GOLDEN` | `6` |
| `DETECT_EVENT_RED` | `7` |

### `DetectEventCompleteImage` (5 entries)
| Key | Value |
|---|---|
| `1` | `Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_l...` |
| `2` | `Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_l...` |
| `3` | `Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_l...` |
| `4` | `Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_l...` |
| `5` | `Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_l...` |

### `DetectEventGoldenColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.2196` |
| `g` | `0.80392` |
| `r` | `0.98823` |

### `DetectEventGreenColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.2196` |
| `g` | `0.88235` |
| `r` | `0.58039` |

### `DetectEventOrangeColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.26274` |
| `g` | `0.53333` |
| `r` | `0.98039` |

### `DetectEventPurpleColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.94117` |
| `g` | `0.42352` |
| `r` | `0.65098` |

### `DetectEventRedColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.40392` |
| `g` | `0.41568` |
| `r` | `0.94901` |

### `DetectEventState` (5 entries)
| Key | Value |
|---|---|
| `DETECT_EVENT_STATE_NOT_FINISH` | `0` |
| `DETECT_EVENT_STATE_FINISHED` | `1` |
| `DETECT_EVENT_STATE_REWARDED` | `2` |
| `DETECT_EVENT_STATE_EXPIRED` | `3` |
| `DETECT_EVENT_STATE_HIDDEN` | `4` |

### `DetectEventType` (29 entries)
| Key | Value |
|---|---|
| `DetectEventTypeSpecial` | `1` |
| `DetectEventTypeNormal` | `2` |
| `DetectEventRadarRally` | `5` |
| `DetectEventPickGarbage` | `6` |
| `DetectEventPVE` | `7` |
| `DetectEventTypeBoss` | `8` |
| `HeroTrial` | `9` |
| `SPECIAL_OPS` | `10` |
| `SWEEP_FIELD` | `11` |
| `OCCUPY_FIELD` | `12` |
| `GUIDE_PVE_LEVEL` | `13` |
| `GUIDE_MONSTER` | `14` |
| `DetectTalkCity` | `16` |
| `DetectTalkWorld` | `17` |
| `PLOT` | `18` |
| `HELP` | `19` |
| `RESCUE` | `20` |
| `COLLECT` | `21` |
| `NPC_CITY` | `22` |
| `ALLIANCE_TREASURE` | `23` |
| `DetectEvent_SevenDay` | `24` |
| `Doomwalker` | `25` |
| `RewardParkour` | `26` |
| `OVERLORD_RESCUE` | `27` |
| `OVERLORD_BATTLE` | `28` |
| `OVERLORD_HUNTER` | `29` |
| `MISSILE_UNLOCK_SEARCH` | `30` |
| `MISSILE_UNLOCK_DONATE` | `31` |
| `MISSILE_UNLOCK_FAST_DONATE` | `32` |

### `DetectEventWhiteColor` (4 entries)
| Key | Value |
|---|---|
| `a` | `1` |
| `b` | `0.75294` |
| `g` | `0.71764` |
| `r` | `0.74509` |

### `DragonBuildingTypes` (7 entries)
| Key | Value |
|---|---|
| `DragonEmptyBuild` | `10000` |
| `DragonWarBuild` | `10010` |
| `DragonCenterBuild` | `10020` |
| `DragonAllianceFlagSelf` | `10030` |
| `DragonAllianceFlagOther` | `10040` |
| `DragonHospitalBuild` | `10050` |
| `DragonBoss` | `10060` |

### `GhostKingMonsterType` (2 entries)
| Key | Value |
|---|---|
| `NoDie` | `0` |
| `Die` | `1` |

### `GuideSceneType` (3 entries)
| Key | Value |
|---|---|
| `City` | `1` |
| `World` | `2` |
| `Pve` | `3` |

### `LuckyShopItemType` (2 entries)
| Key | Value |
|---|---|
| `LuckyShopItemType_Resource` | `1` |
| `LuckyShopItemType_Item` | `2` |

### `MailType` (180 entries)
| Key | Value |
|---|---|
| `MAIL_SYSTEM` | `2` |
| `MAIL_SYSTEM_EXTRA` | `3` |
| `MAIL_FIGHT` | `7` |
| `MAIL_SCOUT_RESULT` | `8` |
| `MAIL_SCOUT_ALERT` | `9` |
| `RESOURCE_HELP` | `10` |
| `MAIL_WOUNDED` | `11` |
| `WORLD_NEW_EXPLORE` | `12` |
| `MAIL_GM` | `13` |
| `MAIL_WORLD_NEW_EXPLORE` | `13` |
| `MAIL_FRESHER` | `14` |
| `MAIL_SysNotice` | `15` |
| `MAIL_UPDATE` | `16` |
| `MAIL_AllianceInvite` | `17` |
| `MAIL_WORLD_MONSTER` | `18` |
| `MAIL_ALLIANCE_ALL` | `20` |
| `MAIL_SELF_SEND` | `21` |
| `MAIL_USER` | `22` |
| `MAIL_ModSend` | `23` |
| `MAIL_ModPersonal` | `24` |
| `MAIL_AllianceApply` | `25` |
| `MAIL_InviteMovePoint` | `26` |
| `MAIL_KickAllianceUser` | `27` |
| `MAIL_GIFT` | `28` |
| `MAIL_GIFT_EXCHANGE` | `29` |
| `MAIL_MONSTER_BOSS` | `30` |
| `MAIL_Alliance_Unsign` | `31` |
| `MAIL_AllianceOfficalset` | `32` |
| `MAIL_UserHeroMail` | `33` |
| `RefuseAllianceApply` | `33` |
| `GIFT_BUY_EXCHANGE` | `34` |
| `MAIL_CHAT_ROOM` | `35` |
| `MAIL_BOSS_REWARD` | `36` |
| `MAIL_RefuseAllianceApply` | `37` |
| `MAIL_GIFT_ALLIANCE` | `38` |
| `MAIL_WORLD_DISCOVETY` | `39` |
| `MAIL_MISSILE_ATTACK` | `40` |
| `MAIL_PRESENT_ARMY` | `41` |
| `AL_DONATE_REWARD` | `42` |
| `MAIL_ALLIACNE_COMPENSATION` | `43` |
| `MAIL_MV_CROSS_INVITE` | `44` |
| `MAIL_PRESIDENT_SEND` | `45` |
| `MAIL_RECEIVE_Gift` | `46` |
| `MAIL_VOTE` | `47` |
| `MAIL_WORLD_FORTRESS` | `48` |
| `MAIL_AC_WHEEL_FIGHT` | `49` |
| `MAIL_LS_PLAYER_CITY` | `50` |
| `MAIL_LS_MONSTER_SIEGE` | `51` |
| `MAIL_LS_RESOURCE_FIGHT` | `52` |
| `MAIL_LS_SPACE_FIGHT` | `53` |
| `MAIL_LS_FIELD_MONSTER_FIGHT` | `54` |
| `MAIL_LS_DOMAIN_FIGHT` | `55` |
| `MAIL_ACTIVITY` | `56` |
| `MAIL_LS_USER_WORLD_BUILDING` | `57` |
| `MAIL_LS_NEW_SCOUT` | `58` |
| `MAIL_LS_MONSTER_BOSS` | `59` |
| `MAIL_ALLIANCE_RECOMMEND` | `60` |
| `MAIL_KINGDOM_REWARD` | `61` |
| `MAIL_LS_KINGDOM_SEASON` | `62` |
| `MAIL_HEROBATTLE_FB` | `63` |
| `MAIN_CITY_LV_UP` | `64` |
| `MAIL_ARMY_DETAIL` | `65` |
| `MAIL_LS_ACTIVITY` | `66` |
| `MAIL_LS_CITY_EXPLORE` | `67` |
| `MAIL_OFFICE_MAIL` | `68` |
| `MAIL_LS_DOMAIN_OCCUPY_CITY` | `69` |
| `MAIL_BOMB_ATTACK` | `70` |
| `MAIL_ESPIONAGE_ATTACK` | `71` |
| `NEW_FIGHT` | `72` |
| `NEW_COLLECT_MAIL` | `73` |
| `MAIL_FIRST_JOIN_ALLIANCE` | `74` |
| `MAIL_JOIN_ALLIANCE` | `75` |
| `MAIL_NEW_PLUNDER_RES_MAIL` | `76` |
| `MAIL_ALCOMPETE_REWARD` | `77` |
| `MAIL_ALCOMPETE_WEEK_REPORT` | `78` |
| `ALLIANCE_CITY_OCCUPIED_REWARD` | `79` |
| `MAIL_ALLIANCE_MARK_ADD` | `80` |
| `MAIL_PICK_GARBAGE` | `81` |
| `MAIL_EXPLORE` | `82` |
| `RESOURCE_HELP_FROM` | `83` |
| `RESOURCE_HELP_TO` | `84` |
| `RESOURCE_HELP_FAIL` | `85` |
| `MAIL_AL_LEADER_ELECT` | `86` |
| `MAIL_AL_LEADER_VOTE` | `87` |
| `MAIL_AL_AL_COMMON` | `88` |
| `MAIL_AL_LEADER_CHANGE` | `89` |
| `MONSTER_COLLECT_REWARD` | `90` |
| `MARCH_DESTROY_MAIL` | `91` |
| `MARCH_STAMINA_BACK` | `92` |
| `RETURN_POWER` | `92` |
| `ELITE_FIGHT_MAIL` | `93` |
| `ALLIANCE_CITY_RANK` | `94` |
| `MAIL_AL_ELECT_RESULT_R4` | `95` |
| `MAIL_AL_ELECT_RESULT_LEADER` | `96` |
| `MAIL_GOLLOES_TRADE_REWARDS` | `97` |
| `MAIL_ALLIANCE_INVITE` | `98` |
| `MAIL_MINE_PLUNDER` | `99` |
| `COLLECT_ADDITION_REWARD` | `100` |
| `CHALLENGE_BOSS_REWARD` | `101` |
| `COLLECT_OVER_FLOW_MAIL` | `102` |
| `MAIL_GIFT_RECEIVE` | `103` |
| `PLACE_ALLIANCE_BUILD_MAIL` | `104` |
| `MAIL_MONSTER_SIEGE` | `105` |
| `OFFICIAL_APPOINT_MAIL` | `106` |
| `BE_KING` | `107` |
| `MIGRATE_APPLY` | `108` |
| `SHORT_KEEP_FIGHT_MAIL` | `109` |
| `PERSON_ARMS_RANK_REWARD` | `110` |
| `MAIL_ALLIANCE_ALL_R4` | `111` |
| `MAIL_ALLIANCE_ALL_R5` | `112` |
| `TRUCK` | `113` |
| `R5_ALLIANCE_MARK` | `114` |
| `R4_ALLIANCE_MARK` | `115` |
| `R5_ALLIANCE_BOSS` | `116` |
| `R4_ALLIANCE_BOSS` | `117` |
| `ALLIANCE_BOSS_RANK` | `118` |
| `TRAIN_NOTIFY` | `119` |
| `TRAIN_ARRIVE` | `120` |
| `TRAIN_REWARD` | `121` |
| `TRAIN_DEPARTURE` | `122` |
| `TRAIN_BATTLE` | `123` |
| `MAIL_ALLIANCE_Recommend` | `124` |
| `MAIL_ALLIANCE_Vote` | `125` |
| `TRUCK_FIGHT` | `126` |
| `THRONE_REWARD` | `127` |
| `OCCUPY_THRONE_SUCCESS` | `128` |
| `HOSPITAL_OUT_OF_MAX` | `129` |
| `ALLIANCE_DUEL_NEW` | `130` |
| `PERSONAL_SCORE` | `131` |
| `CHALLENGE_BOSS` | `132` |
| `ARENA_BATTLE` | `133` |
| `ELITE_BATTLE_MAIL` | `134` |
| `MONSTER_SIEGE_NEW` | `135` |
| `WORLD_BOSS` | `135` |
| `ALLIANCE_BOSS_REWARD` | `136` |
| `ALLIANCE_COMMON` | `137` |
| `STRONGCOMMANDER` | `137` |
| `AllianceMobilization` | `138` |
| `RalyyBoss` | `139` |
| `KingdomRank` | `140` |
| `ProtectShieldOut` | `141` |
| `FORTRESS_GIFT` | `142` |
| `FORTRESS_RESULT` | `143` |
| `CHANGE_ALLIANCE_INVITE` | `144` |
| `AUTO_JOIN_ALLIANCE` | `145` |
| `CancelReDeclareWar` | `146` |
| `STRONG_KINGDOM` | `146` |
| `DRAGON_ALLIANCE_REWARD` | `147` |
| `DRAGON_PERSONAL_REWARD` | `148` |
| `ALLIANCE_BOSS_BEAR` | `149` |
| `ALLIANCE_BOSS_BEAR_REWARD` | `150` |
| `ALLIANCE_BOSS_BEAR_RANK` | `151` |
| `ALLIANCE_BOSS_BEAR_RESERVE_R5` | `152` |
| `ALLIANCE_BOSS_BEAR_RESERVE_R4` | `153` |
| `MAIL_DECLARE` | `154` |
| `MAIL_ALLIACNCE_PERSONAL_REWARD` | `155` |
| `DRAGON_SIGN_RESULT` | `156` |
| `TOWER_ATTACK_MAIL` | `157` |
| `GM_DISSOLVE_ALLIANCE` | `158` |
| `CROSS_HIT_BLOCK_REWARD` | `159` |
| `FOOD_FESTIVAL_EAT_RECORD` | `160` |
| `MAIL_SYSTEM_2` | `161` |
| `MAIL_SYSTEM_3` | `162` |
| `THRONE_KINGDOM` | `165` |
| `NEW_FIGHT_ERROR` | `167` |
| `BUY_PLATFORM_TOKEN` | `168` |
| `MIGRATE_INVITE` | `169` |
| `MIGRATE_INVITE_REFUSE` | `170` |
| `MAIL_ROAMING_BOSS` | `171` |
| `MAIL_ICECAVE_ACT` | `176` |
| `ARENA_SETTLE_NEW` | `180` |
| `MonsterTower_AlBoss` | `200` |
| `NEW_FIGHT_EXPEDITIONARY_DUEL` | `996` |
| `NEW_FIGHT_BLACK_KNIGHT` | `997` |
| `NEW_FIGHT_ARENA` | `998` |
| `NEW_FIGHT_MINECAVE` | `999` |
| `NEW_FIGHT_DESTROY_BUILD` | `1000` |
| `MARCH_DESTROY_PVE` | `10091` |
| `BLACK_KNIGHT_FIGHT` | `20109` |
| `MARCH_DESTROY_BUILD` | `40091` |

### `MonsterType` (5 entries)
| Key | Value |
|---|---|
| `Normal` | `1` |
| `RedZombie` | `2` |
| `WorldBoss` | `3` |
| `Dog` | `4` |
| `Bucket` | `5` |

### `NewMarchType` (37 entries)
| Key | Value |
|---|---|
| `DEFAULT` | `-1` |
| `NORMAL` | `0` |
| `ASSEMBLY_MARCH` | `1` |
| `MONSTER` | `2` |
| `BOSS` | `3` |
| `SCOUT` | `4` |
| `EXPLORE` | `5` |
| `RESOURCE_HELP` | `6` |
| `GOLLOES_EXPLORE` | `7` |
| `GOLLOES_TRADE` | `8` |
| `ACT_BOSS` | `9` |
| `PUZZLE_BOSS` | `10` |
| `DIRECT_MOVE_MARCH` | `11` |
| `CHALLENGE_BOSS` | `12` |
| `MONSTER_SIEGE` | `13` |
| `ALLIANCE_BOSS` | `14` |
| `TRAIN` | `15` |
| `ASSEMBLY_MARCH_NOT_ATTACK` | `16` |
| `GodzillaGift` | `17` |
| `DRAGON_MARK_SHARE` | `18` |
| `DRAGON_POINT_SHARE` | `19` |
| `FOOD_FESTIVAL_EAT` | `20` |
| `ROAMING_BOSS` | `21` |
| `RESCUE_ANIMAL` | `22` |
| `GOBLIN_TREASURE` | `23` |
| `TRADE_POST` | `24` |
| `CAR_CHIP_TRAIL_BOSS` | `25` |
| `GOLLOES_CARAVAN_NEW` | `26` |
| `DIRECT_MOVE_SEASON_BOSS_MARCH` | `27` |
| `MonsterTowerAlBoss` | `28` |
| `BLOOD_MOON_MONSTER` | `29` |
| `BLOOD_MOON_BOSS` | `30` |
| `PARADE_FLOAT` | `31` |
| `Night_BARONESS` | `32` |
| `MISSILE_UNLOCK_TRUCK` | `33` |
| `MISSILE_UNLOCK_FUEL_PLANE` | `34` |
| `MISSILE_UNLOCK_SCOUT` | `35` |

### `NewQueueType` (24 entries)
| Key | Value |
|---|---|
| `Default` | `0` |
| `CarSoldier` | `1` |
| `Hospital` | `3` |
| `Science` | `6` |
| `FootSoldier` | `8` |
| `BowSoldier` | `9` |
| `ProductEquip` | `11` |
| `ArmyUpgrade` | `34` |
| `DomainHospital` | `35` |
| `EquipMaterial` | `36` |
| `Field` | `39` |
| `Barn` | `40` |
| `OstrichBarn` | `41` |
| `CattleBarn` | `42` |
| `SandWormBarn` | `43` |
| `FISH` | `45` |
| `DragonHospital` | `46` |
| `TransportRes` | `104` |
| `Equip` | `107` |
| `BlastMissile` | `111` |
| `GasMissile` | `112` |
| `FreezingMissile` | `113` |
| `CombustionMissile` | `114` |
| `IlluminationMissile` | `115` |

### `OrderItemType` (5 entries)
| Key | Value |
|---|---|
| `ORDER_ITEM_TYPE_RESOURCE_ITEM` | `0` |
| `ORDER_ITEM_TYPE_GOODS` | `1` |
| `ORDER_ITEM_TYPE_RESOURCE` | `2` |
| `ORDER_ITEM_TYPE_MONSTER` | `3` |
| `ORDER_ITEM_TYPE_SPECIAL_MONSTER` | `4` |

### `OutResourceTypeIconName` (5 entries)
| Key | Value |
|---|---|
| `0` | `Assets/Main/Sprites/UI/UIBuildBubble/bubble_icon_oil...` |
| `1` | `Assets/Main/Sprites/UI/UIBuildBubble/bubble_icon_met...` |
| `11` | `Assets/Main/Sprites/UI/UIBuildBubble/bubble_icon_wat...` |
| `12` | `Assets/Main/Sprites/UI/UIBuildBubble/bubble_icon_ele...` |
| `14` | `Assets/Main/Sprites/UI/Common/Common_icon_money_1.png` |

### `ProductResourceItemBuildingTypes` (7 entries)
| Key | Value |
|---|---|
| `5` | `432000` |
| `4` | `728000` |
| `3` | `731000` |
| `1` | `736000` |
| `2` | `737000` |
| `7` | `812000` |
| `6` | `813000` |

### `PuzzleTaskState` (3 entries)
| Key | Value |
|---|---|
| `PuzzleTaskState_UnComplete` | `0` |
| `PuzzleTaskState_Complete` | `1` |
| `PuzzleTaskState_Reward_Get` | `2` |

### `ResourceItemType` (2 entries)
| Key | Value |
|---|---|
| `Farming` | `0` |
| `Industry` | `1` |

### `ResourceType` (33 entries)
| Key | Value |
|---|---|
| `None` | `-1` |
| `Oil` | `0` |
| `Metal` | `1` |
| `Wood` | `2` |
| `PVE_STAMINA` | `3` |
| `People` | `4` |
| `Water` | `11` |
| `Electricity` | `12` |
| `FLINT` | `13` |
| `Money` | `14` |
| `Gold` | `15` |
| `Ruby` | `16` |
| `PvePoint` | `17` |
| `MedalOfWisdom` | `18` |
| `FarmBox` | `19` |
| `DETECT_EVENT` | `20` |
| `FORMATION_STAMINA` | `21` |
| `BattlePass` | `22` |
| `LZ_Steel` | `29` |
| `LM_food` | `30` |
| `LM_metal` | `31` |
| `Max` | `100` |
| `BlackKnight` | `9001` |
| `MasteryPoint` | `9002` |
| `VolcanoOrePoint` | `9004` |
| `ResourceItem` | `10000` |
| `Item` | `10001` |
| `Prop` | `10001` |
| `Survival_People` | `10002` |
| `SeasonRadiate` | `200000` |
| `SeasonGroundNum` | `200001` |
| `HeroExp` | `200394` |
| `Steel` | `230104` |

### `ResourceTypeIconName` (19 entries)
| Key | Value |
|---|---|
| `0` | `Assets/Main/Sprites/ItemIcons/Common_icon_shuijing.png` |
| `1` | `Assets/Main/Sprites/ItemIcons/UI_Icon_shiwu.png` |
| `11` | `Assets/Main/Sprites/UI/Common/Common_icon_water.png` |
| `12` | `Assets/Main/Sprites/ItemIcons/Common_icon_electricit...` |
| `13` | `Assets/Main/Sprites/ItemIcons/Common_icon_xianrenzha...` |
| `14` | `Assets/Main/Sprites/ItemIcons/Common_icon_money.png` |
| `15` | `Assets/Main/Sprites/UI/Common/Common_icon_gold_1.png` |
| `17` | `Assets/Main/Sprites/UI/Common/Common_icon_pvecode.png` |
| `18` | `Assets/Main/Sprites/ItemIcons/item210454.png` |
| `19` | `Assets/Main/Sprites/UI/Common/item200150.png` |
| `2` | `Assets/Main/Sprites/ItemIcons/Common_icon_wood.png` |
| `20` | `Assets/Main/Sprites/UI/Common/Common_icon_radar.png` |
| `21` | `Assets/Main/Sprites/UI/Common/Common_icon_stamina_1.png` |
| `29` | `Assets/Main/Sprites/ItemIcons/Common_icon_steel.png` |
| `3` | `Assets/Main/Sprites/UI/Common/Common_icon_stamina_1.png` |
| `30` | `Assets/Main/Sprites/ItemIcons/UI_Icon_shiwu.png` |
| `31` | `Assets/Main/Sprites/ItemIcons/res_300041.png` |
| `4` | `Assets/Main/Sprites/UI/Common/Common_icon_people.png` |
| `9002` | `Assets/Main/Sprites/ItemIcons/item_EXP_icon_01.png` |

### `ResourceTypePickUpEffectName` (5 entries)
| Key | Value |
|---|---|
| `0` | `Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouq...` |
| `1` | `Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouq...` |
| `11` | `Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouq...` |
| `12` | `Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouq...` |
| `14` | `Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouq...` |

### `ResourceTypeScience` (3 entries)
| Key | Value |
|---|---|
| `1` | `731000` |
| `11` | `732000` |
| `0` | `751000` |

### `ResourceTypeTxt` (16 entries)
| Key | Value |
|---|---|
| `20` | `100000` |
| `21` | `100002` |
| `0` | `100014` |
| `6` | `100180` |
| `15` | `100183` |
| `5` | `100183` |
| `30` | `100510` |
| `32` | `100510` |
| `19` | `100546` |
| `36` | `110353` |
| `29` | `140073` |
| `31` | `180265` |
| `42` | `180370` |
| `1003` | `390967` |
| `28` | `400011` |
| `1` | `722034` |

### `SceneManagerSceneID` (6 entries)
| Key | Value |
|---|---|
| `None` | `0` |
| `City` | `1` |
| `World` | `2` |
| `PVE` | `3` |
| `Bridge` | `4` |
| `Barrel` | `5` |

### `SceneType` (4 entries)
| Key | Value |
|---|---|
| `None` | `0` |
| `City` | `1` |
| `World` | `2` |
| `PVE` | `3` |

### `ShopType2PanelTab` (5 entries)
| Key | Value |
|---|---|
| `3` | `1` |
| `2` | `2` |
| `1` | `3` |
| `14` | `4` |
| `16` | `5` |

### `SlgBattleType` (66 entries)
| Key | Value |
|---|---|
| `ACT_ALLIANCE_MINE` | `-1` |
| `ALLIANCE_BOSS_BEAR` | `-1` |
| `ALLIANCE_FORTRESS` | `-1` |
| `ALLIANCE_FORTRESS_MIX` | `-1` |
| `ALLIANCE_THRONE_MIX` | `-1` |
| `ALLIANCE_TOWER_MIX` | `-1` |
| `BIG_WORM` | `-1` |
| `BLOOD_MOON_MONSTER` | `-1` |
| `CITY_TRAP` | `-1` |
| `RALLY_TEAM_MIX` | `-1` |
| `SUPER_WORM` | `-1` |
| `TRAIN_MARCH` | `-1` |
| `TRIAL_PVE` | `-1` |
| `None` | `0` |
| `Formation` | `1` |
| `Building` | `2` |
| `Turret` | `3` |
| `Monster` | `4` |
| `RallyFormation` | `5` |
| `Boss` | `6` |
| `City` | `7` |
| `Road` | `8` |
| `Explore` | `9` |
| `ALLIANCE_NEUTRAL_CITY` | `10` |
| `ALLIANCE_OCCUPIED_CITY` | `11` |
| `ELITE_FIGHT_MAIL` | `12` |
| `PVE_MARCH` | `13` |
| `PVE_MONSTER` | `14` |
| `ACT_BOSS` | `15` |
| `PUZZLE_BOSS` | `16` |
| `CHALLENGE_BOSS` | `17` |
| `Desert` | `18` |
| `TRAIN_DESERT` | `19` |
| `ALLIANCE_BUILDING` | `20` |
| `NpcCity` | `21` |
| `ALLIANCE_CITY_GUARD` | `22` |
| `CITY_GUARD` | `23` |
| `ALLIANCE_BUILD_GUARD` | `24` |
| `NPC_CITY_GUARD` | `25` |
| `BLACK_KNIGHT` | `26` |
| `THRONE_ARMY` | `27` |
| `CROSS_WORM` | `28` |
| `AllianceBoss` | `30` |
| `DRAGON_BUILDING` | `33` |
| `Train_March` | `36` |
| `ALLIANCE_THRONE_TOWER` | `37` |
| `DRAGON_BOSS` | `38` |
| `ACT_RESOURCE` | `39` |
| `TRADE_POST` | `40` |
| `ROAMING_BOSS` | `41` |
| `ICE_CAVE_BOSS` | `42` |
| `ICE_CAVE_BOSS_SHIELD` | `43` |
| `GOBLIN_TREASURE_SHIELD` | `44` |
| `CAR_CHIP_TRAIL_BOSS` | `45` |
| `SEASON_ACT_BOSS_DEFEND_WALL` | `46` |
| `MonsterTower_AlBoss` | `47` |
| `BLACK_LAND_RUIN` | `48` |
| `BLOOD_MOON_BOSS` | `50` |
| `GHOST_KING` | `51` |
| `PARADE_FLOAT` | `52` |
| `BLOOD_MOON_GENERAL` | `53` |
| `PARADE_FLOAT_PRIEST` | `54` |
| `GHOST_KING_SHIELD` | `55` |
| `VOLCANO_BUILDING` | `56` |
| `CANYON_BUILDING` | `931` |
| `CANYON_BOSS` | `932` |

### `SlgNewMarchType` (46 entries)
| Key | Value |
|---|---|
| `ALLIANCE_BOSS_BEAR` | `-1` |
| `BIG_WORM` | `-1` |
| `BLOOD_MOON_GENERAL` | `-1` |
| `DEFAULT` | `-1` |
| `ICE_ANIMAL_MONSTER` | `-1` |
| `SMALL_WORM` | `-1` |
| `SUPER_WORM` | `-1` |
| `TRAIN_TRANSPORT` | `-1` |
| `ZOMBIE_SIEGE_BOSS` | `-1` |
| `ZOMBIE_SIEGE_BOSS_MARCH` | `-1` |
| `ZOMBIE_SIEGE_MONSTER` | `-1` |
| `NORMAL` | `0` |
| `ASSEMBLY_MARCH` | `1` |
| `MONSTER` | `2` |
| `BOSS` | `3` |
| `SCOUT` | `4` |
| `EXPLORE` | `5` |
| `RESOURCE_HELP` | `6` |
| `GOLLOES_EXPLORE` | `7` |
| `GOLLOES_TRADE` | `8` |
| `ACT_BOSS` | `9` |
| `PUZZLE_BOSS` | `10` |
| `DIRECT_MOVE_MARCH` | `11` |
| `CHALLENGE_BOSS` | `12` |
| `MONSTER_SIEGE` | `13` |
| `ALLIANCE_BOSS` | `14` |
| `TRAIN` | `15` |
| `ASSEMBLY_MARCH_NOT_ATTACK` | `16` |
| `GodzillaGift` | `17` |
| `DRAGON_MARK_SHARE` | `18` |
| `DRAGON_POINT_SHARE` | `19` |
| `FOOD_FESTIVAL_EAT` | `20` |
| `ROAMING_BOSS` | `21` |
| `RESCUE_ANIMAL` | `22` |
| `GOBLIN_TREASURE` | `23` |
| `TRADE_POST` | `24` |
| `CAR_CHIP_TRAIL_BOSS` | `25` |
| `GOLLOES_CARAVAN_NEW` | `26` |
| `DIRECT_MOVE_SEASON_BOSS_MARCH` | `27` |
| `MonsterTowerAlBoss` | `28` |
| `BLOOD_MOON_MONSTER` | `29` |
| `BLOOD_MOON_BOSS` | `30` |
| `PARADE_FLOAT` | `31` |
| `Night_BARONESS` | `32` |
| `CANYON_MARK_SHARE` | `921` |
| `CANYON_POINT_SHARE` | `922` |

### `SlgWorldActResourceType` (2 entries)
| Key | Value |
|---|---|
| `CROSS_FIGHT_WINNER` | `3` |
| `GHOST_KING` | `5` |

### `SlgWorldPointType` (49 entries)
| Key | Value |
|---|---|
| `CROSS_THRONE_BUILD` | `-1` |
| `GOD_RELICS` | `-1` |
| `LUCKY_CAT` | `-1` |
| `MONEY_TREE` | `-1` |
| `PLAYER_BASE` | `-1` |
| `PRAY_TREE` | `-1` |
| `WORLD_ALLIANCE_FORTRESS` | `-1` |
| `WORLD_ALLIANCE_TOWER` | `-1` |
| `ZOMBIE_SIEGE_BORN` | `-1` |
| `Other` | `0` |
| `WorldCollectResource` | `1` |
| `PlayerRoad` | `2` |
| `PlayerBoard` | `3` |
| `WorldMonster` | `4` |
| `WorldBoss` | `5` |
| `PlayerBuilding` | `6` |
| `WorldResource` | `7` |
| `EXPLORE_POINT` | `8` |
| `SAMPLE_POINT` | `9` |
| `GARBAGE` | `10` |
| `WORLD_ALLIANCE_CITY` | `11` |
| `MONSTER_REWARD` | `12` |
| `SAMPLE_POINT_NEW` | `13` |
| `DETECT_EVENT_PVE` | `14` |
| `WORLD_ALLIANCE_BUILD` | `15` |
| `NPC_CITY` | `16` |
| `WorldRuinPoint` | `17` |
| `DRAGON_BUILDING` | `18` |
| `SECRET_KEY` | `19` |
| `WORLD_TALK_TASK` | `21` |
| `HERO_DISPATCH` | `22` |
| `GodzillaGift` | `23` |
| `ACT_RESOURCE` | `25` |
| `WORLD_ICE_ANIMAL` | `26` |
| `DRAGON_BOSS` | `27` |
| `FoodFestivalEatTable` | `28` |
| `WORLD_ICE_CAVE` | `29` |
| `FISH_MISSION` | `30` |
| `DetectRewardParkour` | `31` |
| `GOBLIN_TREASURE` | `32` |
| `WORLD_TRADE_POST` | `33` |
| `CHRISTMAS_ACT_TREE` | `34` |
| `BLACK_LAND_RUIN` | `35` |
| `DemonHunterCamp` | `36` |
| `REWARD_PACKET` | `37` |
| `VOLCANO_BUILDING` | `38` |
| `CANYON_BUILDING` | `911` |
| `CANYON_SECRET_KEY` | `912` |
| `CANYON_BOSS` | `913` |

### `SnowManTaskState` (5 entries)
| Key | Value |
|---|---|
| `NoComplete` | `0` |
| `CanReveive` | `1` |
| `Received` | `2` |
| `CanReceivedByThief` | `3` |
| `WaitReceiveTime` | `4` |

### `SpeedUpType` (2 entries)
| Key | Value |
|---|---|
| `Build` | `1` |
| `Science` | `2` |

### `SurvivalItemType` (4 entries)
| Key | Value |
|---|---|
| `Sundries` | `80` |
| `Material` | `81` |
| `Equip` | `82` |
| `Feed` | `83` |

### `TalkTaskState` (2 entries)
| Key | Value |
|---|---|
| `Finish` | `1` |
| `Start` | `2` |

### `TaskResourceType` (4 entries)
| Key | Value |
|---|---|
| `1` | `0` |
| `2` | `1` |
| `3` | `11` |
| `4` | `12` |

### `TaskRewardItemType` (4 entries)
| Key | Value |
|---|---|
| `DigAct` | `1` |
| `DawnTask` | `2` |
| `SeasonBuild` | `3` |
| `Monopoly` | `4` |

### `TaskState` (3 entries)
| Key | Value |
|---|---|
| `NoComplete` | `0` |
| `CanReceive` | `1` |
| `Received` | `2` |

### `TaskStateOrder` (3 entries)
| Key | Value |
|---|---|
| `1` | `1` |
| `0` | `2` |
| `2` | `3` |

### `UICapacityTableResourceType` (2 entries)
| Key | Value |
|---|---|
| `1` | `11` |
| `2` | `12` |

### `WorldActResourceType` (2 entries)
| Key | Value |
|---|---|
| `CROSS_FIGHT_WINNER` | `3` |
| `GHOST_KING` | `5` |

### `WorldPointType` (37 entries)
| Key | Value |
|---|---|
| `Other` | `0` |
| `WorldCollectResource` | `1` |
| `PlayerRoad` | `2` |
| `PlayerBoard` | `3` |
| `WorldMonster` | `4` |
| `WorldBoss` | `5` |
| `PlayerBuilding` | `6` |
| `WorldResource` | `7` |
| `EXPLORE_POINT` | `8` |
| `SAMPLE_POINT` | `9` |
| `GARBAGE` | `10` |
| `WORLD_ALLIANCE_CITY` | `11` |
| `MONSTER_REWARD` | `12` |
| `SAMPLE_POINT_NEW` | `13` |
| `DETECT_EVENT_PVE` | `14` |
| `WORLD_ALLIANCE_BUILD` | `15` |
| `NPC_CITY` | `16` |
| `WorldRuinPoint` | `17` |
| `DRAGON_BUILDING` | `18` |
| `SECRET_KEY` | `19` |
| `WORLD_TALK_TASK` | `21` |
| `HERO_DISPATCH` | `22` |
| `GodzillaGift` | `23` |
| `ACT_RESOURCE` | `25` |
| `WORLD_ICE_ANIMAL` | `26` |
| `DRAGON_BOSS` | `27` |
| `FoodFestivalEatTable` | `28` |
| `WORLD_ICE_CAVE` | `29` |
| `FISH_MISSION` | `30` |
| `DetectRewardParkour` | `31` |
| `GOBLIN_TREASURE` | `32` |
| `WORLD_TRADE_POST` | `33` |
| `CHRISTMAS_ACT_TREE` | `34` |
| `BLACK_LAND_RUIN` | `35` |
| `DemonHunterCamp` | `36` |
| `REWARD_PACKET` | `37` |
| `VOLCANO_BUILDING` | `38` |

### `eMailDetailItemType` (5 entries)
| Key | Value |
|---|---|
| `Title_Summary` | `0` |
| `Title_Self` | `1` |
| `Title_Other` | `2` |
| `Content` | `3` |
| `Title_Result` | `4` |

## 3. Complete Index of All 1,274 Global Enum & Constant Tables

> Query any enum table or value instantly with `python megamind_query.py enum <query>`.

| Enum Table Name | Entries | Sample Key=Value Pairs |
|---|---:|---|
| `ABTestType` | 2 | `A=0`, `B=1` |
| `APSDamageEffectType` | 3 | `CRIT=1`, `DEFAULT=0`, `MISS=2` |
| `AccountBandState` | 3 | `Band=2`, `UnBand=0`, `UnCheck=1` |
| `AccountBindType` | 2 | `Bind=1`, `Change=2` |
| `AccountCheckState` | 2 | `Check=1`, `UnCheck=0` |
| `AccountCreateType` | 2 | `ChangePassword=1`, `Register=0` |
| `AccountViewType` | 2 | `Bind=1`, `Question=2` |
| `ActMonsterTowerDiff` | 18 | `1=G_js_huizhang01`, `10=G_js_huizhang01_hard`, `11=G_js_huizhang02_hard`, `12=G_js_huizhang03_hard`, `13=G_js_huizhang04_hard`, `14=G_js_huizhang05_hard`, `... |
| `ActPopUIType` | 28 | `AllianceCompete=6`, `Arena=2`, `Arena3V3=23`, `CarComponPush=22`, `CarMicrochipPush=21`, `ChampionBattle=8`, `ChampionBattleChampion=17`, `ChampionBattleInv... |
| `ActionPhase` | 6 | `Buff=3`, `Cast=1`, `Damage=2`, `Dot=4`, `FIRE_BULLET=5`, `Prepare=0` |
| `ActivityDailyType` | 8 | `CarChipActivity=10`, `CarComponActivity=12`, `Default=0`, `IronAgeActivity=9`, `PrivateContent=5`, `RedEquipmentActivity=13`, `RedEquipmentAndIronAgeMergeAc... |
| `ActivityEventType` | 16 | `ALLIANCE=2`, `ALLIANCE_ORDER=16`, `BF_PERSONAL=7`, `INDIVIDUAL_ORDER=19`, `KINGDOM_ALLIANCE=4`, `KINGDOM_PERSONAL=3`, `KINGDOM_WARMUP_ALLIANCE=13`, `KINGDOM... |
| `ActivityOverviewType` | 10 | `Adventure=9`, `AllianceOrder=7`, `Arena=8`, `ChampionBattle=4`, `EarthOrder=1`, `EverydayTask=10`, `IndividualOrder=3`, `MineCave=5` *(+2 more)* |
| `ActivityRewardStatus` | 2 | `Claimed=1`, `UnClaimed=0` |
| `ActivityShowLocation` | 9 | `Easter=16`, `FoodFestival=15`, `HitMonster=12`, `HitSnowMan=13`, `Monopoly=17`, `Season=4`, `Valentines=14`, `bellowsBall=11` *(+1 more)* |
| `ActivityTipConditionType` | 9 | `CycleActivityEveryTime=4`, `EveryTime=3`, `FirstActivityId=0`, `FirstActivityType=1`, `LoginInEveryDay=2`, `Monday=113`, `MondayToSaturday=116`, `Saturday=1... |
| `ActivityTipEntranceType` | 7 | `Another=100`, `activityEntrance=1`, `allianceCompete=5`, `expose=3`, `sevenDay=7`, `strongCommander=4`, `welfareCenterEntrance=2` |
| `Activity_ChampionBattle_Elite_Stage_State` | 7 | `FINAL_PHASE=6`, `GROUP_FINAL_PHASE=3`, `GROUP_QUARTER_PHASE=1`, `GROUP_SEMI_PHASE=2`, `QUARTER_PHASE=4`, `SEMI_PHASE=5`, `WAIT_START_PHASE=0` |
| `Activity_ChampionBattle_Stage_State` | 6 | `Auditions=2`, `None=0`, `Settlement=5`, `SingUp=1`, `Strongest=4`, `Strongest_64=3` |
| `AdventureRaidState` | 4 | `LevelMaxed=4`, `NeedLevel=2`, `Ready=1`, `Started=3` |
| `AdventureState` | 4 | `Lost=4`, `Playing=2`, `Ready=1`, `Won=3` |
| `AdventureType` | 5 | `Box=4`, `Buff=2`, `Default=0`, `Monster=1`, `Reward=3` |
| `AircraftLevelBg` | 4 | `1=Assets/Main/Sprites/UI/UIAircraft/UIModified_img_linebg3.png`, `2=Assets/Main/Sprites/UI/UIAircraft/UIModified_img_linebg4.png`, `3=Assets/Main/Sprites/UI... |
| `AlCompeteActName` | 6 | `BuildShelter=370026`, `DefeatEnemy=370030`, `FullDevelop=370027`, `ResearchTech=370024`, `TrainHero=370029`, `UpgradeCar=371024` |
| `AlCompeteSide` | 2 | `Enemy=2`, `Self=1` |
| `AlMineConditionType` | 5 | `MemberCount=1`, `Monster=4`, `Power=2`, `PreBuild=5`, `RuinLv=3` |
| `AlMoveInviteType` | 5 | `AlwaysLeader=4`, `InviteTip=3`, `LeaderInvite=2`, `None=0`, `SystemInvite=1` |
| `AlSkillStatus` | 5 | `CD=5`, `Effect=3`, `Penalty=4`, `Prepare=2`, `Use=1` |
| `AllianceAlertType` | 6 | `ALLIANCE_BUILD=4`, `ALLIANCE_CITY=2`, `BUILDING=0`, `COLLECT=1`, `DESERT=3`, `VOLCANO_BUILDING=7` |
| `AllianceBounsRecordType` | 3 | `AllianceDuelBox=3`, `DailyQuest=1`, `WarPrepareBox=2` |
| `AllianceBuildingMoveFailureReason` | 4 | `MoveCooldown=move_cooldown`, `NotAdmin=not_admin`, `Unrepaired=unrepaired`, `Upgrading=upgrading` |
| `AllianceBuildingResourceCollectType` | 2 | `Food=2`, `Wood=1` |
| `AllianceBuildingState` | 5 | `Building=1`, `Normal=0`, `Paralyzed=2`, `Repairing=4`, `Ruin=3` |
| `AllianceBuildingStatus` | 3 | `Destroy=2`, `Normal=0`, `Upgrade=1` |
| `AllianceButtonType` | 34 | `AlLeaderElect=20`, `AllianceAllyMail=31`, `AllianceAnnounce=15`, `AllianceBattle=1`, `AllianceBuilding=2`, `AllianceCancelDismiss=33`, `AllianceCheck=11`, `... |
| `AllianceCareerEffectDescriptionType` | 4 | `AddCount=2`, `AddPercent=4`, `SubCount=3`, `SubPercent=5` |
| `AllianceCareerPosType` | 2 | `No=0`, `Yes=1` |
| `AllianceCareerSelfColor` | 4 | `a=1`, `b=0.6509804`, `g=0.8156863`, `r=0.3607843` |
| `AllianceCityBattleType` | 3 | `CrossServer=2`, `None=0`, `SelfServer=1` |
| `AllianceCityNewsType` | 3 | `FIRST_NEUTRAL_CITY=2`, `OCCUPY_NEUTRAL_CITY=0`, `OCCUPY_OCCUPIED_CITY=1` |
| `AllianceCityRecordState` | 3 | `CURRENT=0`, `HISTORY=1`, `HISTORY_FIRST_OCCUPY=2` |
| `AllianceCityShowTimeState` | 9 | `Contesting=7`, `Lock=1`, `None=0`, `Occupied=8`, `Recover=3`, `ThroneAttack=5`, `ThroneNotOpen=6`, `ThroneProtect=4` *(+1 more)* |
| `AllianceCityState` | 3 | `InProgress=2`, `NEUTRAL=0`, `OCCUPIED=1` |
| `AllianceCompeteItemIdToEffect` | 3 | `230109=30450`, `230111=30448`, `230112=30449` |
| `AllianceCompeteScoreUp` | 14 | `101=30128`, `102=30131`, `103=30131`, `105=30130`, `106=30130`, `107=30127`, `108=30126`, `26=30129` *(+6 more)* |
| `AllianceDonateRankType` | 4 | `None=0`, `RankDay=1`, `RankHistory=3`, `RankWeek=2` |
| `AllianceDonateState` | 5 | `Attaking=1`, `End=2`, `Lose=4`, `Victory=3`, `Waiting=0` |
| `AllianceHelpSelfTabColor` | 4 | `a=0.8`, `b=0.3280972`, `g=0.7125727`, `r=0.9528302` |
| `AllianceHelpState` | 4 | `No=0`, `RuinsHelped=2`, `UpgradeAndRuinsHelped=3`, `UpgradeHelped=1` |
| `AllianceHelpType` | 4 | `Building=0`, `FIX_BUILDING=2`, `None=-1`, `Queue=1` |
| `AllianceLogMemberType` | 33 | `ACCEPT_INVITE=18`, `AGREE_JOIN_ALLIANCE=6`, `ALLIANCE_CITY_BE_ATTACK=11`, `ALLIANCE_CITY_BE_RALLY_ATTACK=12`, `ALLIANCE_MEMBER_BE_ATTACK=13`, `ALLIANCE_MEMB... |
| `AllianceLogTabType` | 3 | `Activity=2`, `Normal=1`, `War=3` |
| `AllianceMarkIconName` | 58 | `10=UIAlliance_mark_10`, `100=c_alliance _marker_icon_v1`, `101=c_alliance _marker_icon_v2`, `102=c_alliance _marker_icon_v3`, `103=c_alliance _marker_icon_v... |
| `AllianceMarkName` | 57 | `10=391110`, `100=5660002`, `101=5660003`, `102=5660004`, `103=5810036`, `104=5810037`, `11=391111`, `12=391112` *(+49 more)* |
| `AllianceMarkPrefabPath` | 58 | `10=Assets/Main/Prefabs/UI/AllianceWorldMark/AllianceWorldMark_10.prefab`, `100=Assets/Main/Prefabs/UI/AllianceWorldMark/AllianceWorldMark_16.prefab`, `101=A... |
| `AllianceMemberManageType` | 10 | `GolloesTrade=8`, `GotoCoordinate=10`, `LeaderReplace=4`, `LeaderTrans=3`, `Mail=6`, `MemberData=1`, `MemberQuit=5`, `MemberRankChange=2` *(+2 more)* |
| `AllianceMemberOpenType` | 5 | `AllianceMember=1`, `GolloesTrande=3`, `OtherAlMember=4`, `ResSupport=2`, `SnapShot=5` |
| `AllianceMemberStageType` | 3 | `BuildingAlliance=3`, `CrossServer=2`, `Normal=1` |
| `AllianceMineStatus` | 3 | `Constructing=1`, `Normal=0`, `Ruin=2` |
| `AllianceOfficialPos` | 4 | `Pos1=1`, `Pos2=2`, `Pos3=3`, `Pos4=4` |
| `AllianceScienceRecommendState` | 2 | `No=0`, `Yes=1` |
| `AllianceTaskFuncType` | 4 | `AllianceCareer=4`, `AllianceMoveCity=2`, `AllianceOrder=1`, `AllianceScience=3` |
| `AllianceTeamType` | 18 | `ASSISTANCE_THRONE=7`, `ATTACK_ACT_RESOURCE=11`, `ATTACK_ALLIANCE_BOSS=10`, `ATTACK_ALLIANCE_BOSS_BEAR=12`, `ATTACK_AL_BUILD=4`, `ATTACK_AL_CITY=3`, `ATTACK_... |
| `AllianceWarStage` | 3 | `BookedStatus=2`, `NoReservationStatus=1`, `None=3` |
| `AllianceWarTabType` | 3 | `Alliance=3`, `Attacker=1`, `Team=2` |
| `AllianceWarTipType` | 5 | `Attacking=3`, `Booked=2`, `CanBook=1`, `CanDeclareWar=4`, `None=0` |
| `AnimName` | 23 | `Aim=idle`, `Attack=attack`, `AttackMove=attack_move`, `AttackMoveBack=run_back`, `Attack_Idle=attack_idle`, `Attack_PVP=attack_pvp`, `Born=born`, `Cheer=che... |
| `AnimalAnimationState` | 7 | `Feed=2`, `Finish=4`, `Fly=5`, `Free=1`, `GuideShow=6`, `None=0`, `Walk=3` |
| `AnimalQIdToAreaId` | 5 | `1=5`, `2=1`, `3=3`, `4=7`, `5=9` |
| `AnimationType` | 11 | `Attack=attack`, `Dead=dead`, `DeadEnd=deadEnd`, `Idle=idle`, `InertialIdle=intertialIdle`, `Move=move`, `Run=walk`, `Sneak=sneak` *(+3 more)* |
| `ApproveMigrateState` | 2 | `AGREE=1`, `REFUSE=2` |
| `ArmType` | 5 | `Plane=3`, `Robot=2`, `Tank=1`, `Type4=4`, `Type5=5` |
| `ArmyDeadType` | 2 | `Fight=1`, `Hospital=0` |
| `ArmyFormationState` | 2 | `Free=0`, `March=1` |
| `ArmyTrainType` | 2 | `ArmyTrainType_Normal=0`, `ArmyTrainType_Reserve=1` |
| `ArrowSecondType` | 12 | `AdventureTask=11`, `AllianceScience=1`, `AllianceScienceDonate=5`, `HeroInfo=3`, `HeroList=2`, `HeroStar=4`, `MainTaskEveryDayTab=10`, `MainWorld=7` *(+4 mo... |
| `ArrowType` | 24 | `BuildBox=5`, `BuildBtn=18`, `BuildBubble=17`, `Building=3`, `Capacity=2`, `Chapter=8`, `ChapterGetReward=11`, `CollectMoney=15` *(+16 more)* |
| `ArrowTypeHero` | 3 | `HeroUid=1`, `LvUpHero=2`, `RankUp=3` |
| `AssistanceHeroType` | 3 | `Alliance=1`, `Chat=2`, `None=0` |
| `AssistanceIconType` | 7 | `AllianceCenter=5`, `AllianceCityLv1_2=3`, `AllianceCityLv3_6=4`, `DragonBuild=6`, `Fort=2`, `Throne=1`, `VolcanoBuild=7` |
| `AssistanceType` | 11 | `ASSISTANCE_TRADE_POST=10`, `ASSISTANCE_VOLCANO_BUILDING=11`, `AllianceBuild=4`, `AllianceCity=2`, `Build=0`, `Desert=3`, `DragonBuilding=7`, `MainCity=1` *(... |
| `AtkDefReason` | 9 | `BUILDING=4`, `CAMP_VALUE=5`, `FORMATION_STATUS=6`, `HERO=0`, `SCIENCE=3`, `SOLDIER_NUM=2`, `SOLDIER_TOTAL=1`, `TOWER_DMG=7` *(+1 more)* |
| `AtlasAssets` | 44 | `CommonDefault=UI_CommonDefault`, `CountryFlag=CountryFlag`, `DynamicAtlas=DynamicAtlas0`, `EquipAtlas=Equip`, `HUP=HUP`, `ItemAtlas=ItemIcons`, `ItemAtlas1=... |
| `AttackAnimDirection` | 3 | `Circle=3`, `LeftToRight=1`, `RightToLeft=2` |
| `AttackSettingKeys` | 3 | `1=AttackWarning_Assistance`, `2=AttackWarning_WorldTroop`, `3=AttackWarning_Home` |
| `AttackState` | 5 | `AutoAttack=2`, `HoldFire=4`, `StationAttack=3`, `StraightAttack=1`, `Ultimate=5` |
| `AuditionsBoxState` | 4 | `CanReceive=1`, `Fail=-1`, `HasReceived=2`, `NotStart=0` |
| `AutoFarmNpcStatus` | 3 | `AutoFarmNpcStatus_ALL_FREE=1`, `AutoFarmNpcStatus_PRODUCTING=2`, `AutoFarmNpcStatus_WAITING_FOR_GATHER=3` |
| `AutoFarmStatus` | 2 | `AutoFarmStatus_FREE=0`, `AutoFarmStatus_PRODUCT=1` |
| `AutoFarmType` | 4 | `AutoFarmType_FACTORY=3`, `AutoFarmType_FARM=1`, `AutoFarmType_FREE=0`, `AutoFarmType_PASTURE=2` |
| `BIND_TYPE` | 8 | `APPSTORE=4`, `CUSTOM=3`, `DEVICE=0`, `FACEBOOK=1`, `GOOGLEPLAY=2`, `OICQ=6`, `WEIBO=7`, `WX=8` |
| `BRAgeVerPopType` | 2 | `Act=1`, `None=0` |
| `BackingPowerType` | 4 | `AllianceCenter=3`, `AllianceCity=0`, `Throne=1`, `Turret=2` |
| `BagTabSelectImage` | 5 | `0=Assets/Main/Sprites/UI/Common/Common_img_freeze_select`, `1=Assets/Main/Sprites/UI/Common/Common_img_warehouse_select`, `2=Assets/Main/Sprites/UI/Common/C... |
| `BagTabUnSelectImage` | 5 | `0=Assets/Main/Sprites/UI/Common/Common_img_freeze_unselect`, `1=Assets/Main/Sprites/UI/Common/Common_img_warehouse_unselect`, `2=Assets/Main/Sprites/UI/Comm... |
| `BarracksBuild` | 3 | `1=423000`, `2=424000`, `3=425000` |
| `BarracksBuildToBtnType` | 3 | `423000=30`, `424000=29`, `425000=28` |
| `BarrageState` | 6 | `AutoAttack=2`, `Exit=5`, `Lose=6`, `PreExit=4`, `Prepare=0`, `Push=1` |
| `BarrelLevelType` | 3 | `Car=3`, `Hero=2`, `Novice=1` |
| `BarrelMapBorder` | 2 | `Max=41`, `Min=30.5` |
| `BarrelMemberType` | 8 | `BarrelCar=32`, `BarrelGirl=2`, `BarrelTank=4`, `Hero=1`, `None=0`, `Overlord=64`, `SummonSoldier=16`, `VehicleTank=8` |
| `BaseExpansionType` | 3 | `None=0`, `Road=1`, `Tree=2` |
| `BattleBuffGroup` | 2 | `Adventure=1`, `Default=0` |
| `BattleBuffTimeType` | 3 | `Battle=1`, `Normal=0`, `Time=2` |
| `BattleBuffType` | 5 | `AdventureHp=2`, `DisableHero=3`, `Effect=0`, `HireHero=4`, `Skill=1` |
| `BattleCommandPlayerSortLogic` | 3 | `Battling_Commander=3`, `Battling_Formation=2`, `BeforeBattle_Formation=1` |
| `BattleNewsType` | 2 | `AllianceCity=1`, `Battle=0` |
| `BattleReportShowType` | 12 | `Atk=1`, `CampValue=8`, `Def=2`, `EdenSignal=9`, `Health=7`, `HeroAtk=5`, `HeroDef=6`, `SkillPower=10` *(+4 more)* |
| `BattleSubTitleShowType` | 18 | `AttackAdd=3`, `BackHurtAdd=9`, `BackHurtDec=12`, `Curve=13`, `Damage=14`, `DefenceAdd=4`, `HealthAdd=5`, `HeroAttack=1` *(+10 more)* |
| `BattleTeamFlag` | 5 | `None=0`, `TeamA=1`, `TeamB=2`, `TeamC=3`, `TeamD=4` |
| `BattleType` | 51 | `ACT_BOSS=15`, `ACT_RESOURCE=39`, `ALLIANCE_BUILDING=20`, `ALLIANCE_BUILD_GUARD=24`, `ALLIANCE_CITY_GUARD=22`, `ALLIANCE_NEUTRAL_CITY=10`, `ALLIANCE_OCCUPIED... |
| `BattleUnitType` | 2 | `Hero=1`, `TacticalWeapon=2` |
| `BaubleQuality` | 5 | `Blue=2`, `Green=1`, `Orange=4`, `Purple=3`, `White=0` |
| `BindSuccessType` | 2 | `BindAccount=0`, `ChangePassword=1` |
| `BlackColor` | 4 | `a=1`, `b=0`, `g=0`, `r=0` |
| `BlackFogColor` | 4 | `a=1`, `b=0.003921569`, `g=0.01176471`, `r=0.04313726` |
| `BlackKnightState` | 7 | `CLOSED=5`, `CLOSING=3`, `END=0`, `NoAlliance=100`, `OPEN=2`, `READY=1`, `REWARD=4` |
| `BlackKnightUserState` | 3 | `ACTIVITY_JOIN=1`, `NORMAL=0`, `ORDER_ALLIANCE_ACTIVITY=2` |
| `BlackKnightWarningState` | 2 | `Close=1`, `Open=0` |
| `BlockPos` | 3 | `x=0`, `y=0.03`, `z=0` |
| `BloodMoonStage` | 4 | `Stage1=1`, `Stage2=2`, `Stage3=3`, `Stage4=4` |
| `BlueBtnColor` | 4 | `a=1`, `b=0.30980392156863`, `g=0.17647058823529`, `r=0.003921568627451` |
| `BlueBtnShadowLightColor` | 4 | `a=1`, `b=0.94901960784314`, `g=0.87450980392157`, `r=0.6` |
| `BlueColor` | 4 | `a=1`, `b=0.89803921568627`, `g=0.6`, `r=0.3843137254902` |
| `BlueColor32` | 4 | `a=255`, `b=255`, `g=149`, `r=23` |
| `BlueColor32_S3` | 4 | `a=255`, `b=255`, `g=197`, `r=74` |
| `BlueColor_Normal` | 4 | `a=1`, `b=1`, `g=0.5843138`, `r=0.09019608` |
| `BlueColor_S3` | 4 | `a=1`, `b=1`, `g=0.77254901960784`, `r=0.29019607843137` |
| `BlueTMPColor` | 4 | `a=1`, `b=0.31`, `g=0.176`, `r=0.004` |
| `BookMarkNameArrCountType` | 3 | `Default=1`, `WithDialog=2`, `WithLevelDialog=3` |
| `BrownColor` | 4 | `a=1`, `b=0.2393`, `g=0.298`, `r=0.4196` |
| `BtnWidth` | 2 | `1=380`, `2=320` |
| `BubbleShowType` | 2 | `Hide=2`, `Show=1` |
| `BubbleState` | 2 | `Normal=1`, `Road=2` |
| `BuffReasonIcon` | 6 | `-1=Assets/Main/Sprites/UI/UIBuild/UIBuild_icon_robot_other`, `0=Assets/Main/Sprites/UI/UIBuild/UIBuild_icon_robot_technology`, `1=Assets/Main/Sprites/UI/UIB... |
| `BuffSubType` | 4 | `Default=0`, `ReduceDamage=1`, `ShieldFromCasterHp=2`, `ShieldFromValue=3` |
| `BuffType` | 11 | `BeTaunt=7`, `Dot=2`, `FiniteSkill=8`, `Halo=0`, `Hot=3`, `Imprison=5`, `Property=1`, `Shield=9` *(+3 more)* |
| `BuildBanMoveType` | 2 | `No=1`, `Yes=0` |
| `BuildBubbleIconName` | 120 | `Aircraft=bubble_icon_aircraft`, `AllianceApply=bubble_icon_alliance_apply`, `AllianceBattle=bubble_icon_alliance_battle`, `AllianceCareer=bubble_icon_allian... |
| `BuildBubbleType` | 129 | `AllianceApply=49`, `AllianceBattle=32`, `AllianceCareer=48`, `AllianceCityDeclareWar=57`, `AllianceGift=34`, `AllianceHelp=26`, `AllianceShopRestock=280`, `... |
| `BuildBubbleTypeOrder` | 123 | `0=0`, `1=1`, `10=11`, `11=9.9`, `12=13`, `13=11.9`, `14=14`, `15=15` *(+115 more)* |
| `BuildConnectRoadDirection` | 5 | `Down=4`, `Left=3`, `None=0`, `Right=2`, `Top=1` |
| `BuildGetResourceState` | 3 | `Add=2`, `Full=3`, `No=1` |
| `BuildGrayColor` | 4 | `a=1`, `b=0.52`, `g=0.52`, `r=0.52` |
| `BuildInside` | 3 | `All=2`, `In=0`, `Out=1` |
| `BuildKeyType` | 2 | `No=0`, `Yes=1` |
| `BuildLevelUpShowType` | 3 | `AddNum=3`, `New=1`, `Unlock=2` |
| `BuildLevelUpUnlockType` | 2 | `Build=1`, `ResourceItem=2` |
| `BuildListBuffType` | 3 | `BuildListBuffType_Free=2`, `BuildListBuffType_Max=3`, `BuildListBuffType_SpeedUp=1` |
| `BuildMaxNumType` | 4 | `Chapter=4`, `Cur=1`, `Guide=2`, `Quest=3` |
| `BuildNeedMonth` | 2 | `No=0`, `Yes=1` |
| `BuildNoQueue` | 2 | `No=0`, `Yes=1` |
| `BuildPoliceInsigniaType` | 4 | `Normal=0`, `OnProcess=2`, `Ready=1`, `Ruins=3` |
| `BuildPutState` | 67 | `AlCityBuilding=37`, `AlResNotEnough=36`, `AllianceCenterDistanceNotEnough=68`, `AllianceCenterEdgeLess9=57`, `AllianceCenterNearCapital=58`, `AllianceCenter... |
| `BuildPutType` | 2 | `Default=0`, `Lv0=1` |
| `BuildQueueState` | 10 | `CURE_ARMY=2`, `DEFAULT=0`, `FACTORY=6`, `FARMING=4`, `FEEDING=5`, `RESEARCH=3`, `Ruins=128`, `STORAGE_SHOP=7` *(+2 more)* |
| `BuildQueueTalkShowType` | 3 | `EndQueue=3`, `Free=1`, `StartQueue=2` |
| `BuildQueueUnlockType` | 6 | `Build=1`, `Favorability=5`, `Gift=2`, `Mastery=4`, `Talent=3`, `Unknown=0` |
| `BuildRedDotType` | 3 | `AllShow=1`, `No=0`, `Once=2` |
| `BuildScanAnim` | 3 | `No=0`, `NoFly=2`, `Play=1` |
| `BuildSceneType` | 4 | `Alliance=4`, `City=1`, `Fake=3`, `World=2` |
| `BuildState` | 29 | `BUILD_LIST_LACK_EFFECTID=29`, `BUILD_LIST_LACK_PEOPLE=3`, `BUILD_LIST_LACK_RESOURCE=4`, `BUILD_LIST_NEED_ALLIANCE_CENTER_FOR_BUILD=26`, `BUILD_LIST_NEED_ALL... |
| `BuildStatusType` | 2 | `FrequencyBase=1`, `TimeBase=0` |
| `BuildTilesSize` | 6 | `Five=5`, `Four=4`, `One=1`, `Seven=7`, `Three=3`, `Two=2` |
| `BuildTilesType` | 3 | `One=1`, `Three=3`, `Two=2` |
| `BuildTimeType` | 12 | `BuildTime_BowSoldier=3`, `BuildTime_CarSoldier=2`, `BuildTime_Farm=6`, `BuildTime_Fixing=9`, `BuildTime_FootSoldier=1`, `BuildTime_HeroEquip=10`, `BuildTime... |
| `BuildType` | 4 | `Main=1`, `Normal=0`, `Second=2`, `Third=3` |
| `BuildUpgradeEffectType` | 2 | `ConfirmBox=2`, `Upgradeing=1` |
| `BuildUpgradeUseGoldType` | 4 | `Free=3`, `No=0`, `Speed=4`, `Yes=2` |
| `BuildZoneMainType` | 2 | `Main=1`, `Sub=0` |
| `BuildZoneName` | 4 | `1=100810`, `2=100811`, `3=100812`, `4=100813` |
| `BuildZoneType` | 6 | `All=0`, `Hero=2`, `Military=4`, `No=-1`, `Tower=1`, `Trade=3` |
| `BuildingConnectState` | 2 | `Connect=1`, `UnConnect=0` |
| `BuildingSpecialGroupType` | 5 | `EDEN_WORM_HOLE_B_1=1002`, `EDEN_WORM_HOLE_B_2=1003`, `EDEN_WORM_HOLE_B_3=1004`, `WORM_HOLE_B=1000`, `WORM_HOLE_CROSS=1001` |
| `BuildingStateType` | 4 | `FoldUp=2`, `Normal=0`, `PAUSE_Upgrading=3`, `Upgrading=1` |
| `BuildingTypes` | 208 | `ALLIANCE_CENTER_1=41000`, `ALLIANCE_CENTER_2=42000`, `ALLIANCE_CENTER_2_1=42001`, `ALLIANCE_CENTER_3=43000`, `ALLIANCE_CENTER_3_1=43002`, `ALLIANCE_CENTER_4... |
| `BuildingUpgradeTabType` | 5 | `TabType_Cooking=3`, `TabType_Food=4`, `TabType_Normal=1`, `TabType_PoliceInsignia=5`, `TabType_Station=2` |
| `BuildingWorkerStatus` | 3 | `Worker_Status_Free=2`, `Worker_Status_Locked=1`, `Worker_Status_Working=3` |
| `BulletBuffType` | 5 | `None=0`, `OnCastToCaster=4`, `OnHit=1`, `OnHitByChance=2`, `OnKill=3` |
| `BulletDurabilityType` | 3 | `Collide=1`, `CollideInfinity=-1`, `Time=0` |
| `BulletMoveType` | 7 | `AreaBomb=7`, `Follow=4`, `Laser=6`, `Parabola=2`, `Ray=5`, `Static=0`, `Straight=1` |
| `BusinessBubbleState` | 3 | `No=0`, `NoSubmit=1`, `Yes=2` |
| `BusinessRereshType` | 4 | `DeleteOrderFinish=1`, `ImmediateRefresh=3`, `InitOrderFinish=0`, `PurchaseOrderFinish=2` |
| `ButtonRedTextColor` | 4 | `a=1`, `b=0`, `g=0`, `r=0.6` |
| `BuyFlag` | 2 | `BUY=1`, `NOT_BUY=0` |
| `CHAT_UPLOAD_STATUS` | 5 | `FAILED=0`, `PICK_END=1`, `UPLOAD_END=3`, `UPLOAD_PROCESS=2`, `VERIFY_END=4` |
| `CallBossUseType` | 2 | `CallBoss=0`, `GetReward=1` |
| `CampEffectType` | 5 | `Fetter_3=1`, `Fetter_3_2=2`, `Fetter_4=3`, `Fetter_5=4`, `None=0` |
| `CampImage` | 4 | `0=Assets/Main/Sprites/UI/Common/ui_camp_0.png`, `1=Assets/Main/Sprites/UI/UIHeroBattlefield/UIHeroscape_icon_camp01.png`, `2=Assets/Main/Sprites/UI/UIHeroBa... |
| `CanUnlockFogSmallDirection` | 4 | `LeftDown=1`, `LeftTop=4`, `RightDown=2`, `RightTop=3` |
| `CanUnlockFogSmallState` | 2 | `DeepColor=1`, `WeakColor=2` |
| `CarChipActivityColorGreen` | 4 | `a=1`, `b=0.031372549019608`, `g=0.44313725490196`, `r=0.0` |
| `CarChipActivityColorRed` | 4 | `a=1`, `b=0.003921568627451`, `g=0.003921568627451`, `r=0.87058823529412` |
| `CarColorBlue` | 4 | `a=1`, `b=0.9921568627451`, `g=0.61960784313725`, `r=0.31372549019608` |
| `CarColorGreen` | 4 | `a=1`, `b=0.18039215686275`, `g=0.55686274509804`, `r=0.031372549019608` |
| `CarColorOrange` | 4 | `a=1`, `b=0.14117647058824`, `g=0.67058823529412`, `r=0.96862745098039` |
| `CarColorPurple` | 4 | `a=1`, `b=0.9921568627451`, `g=0.3843137254902`, `r=0.82352941176471` |
| `CarColorWrite` | 4 | `a=1`, `b=1`, `g=1`, `r=1` |
| `CarParts` | 5 | `BackDoor=4`, `FrontWindshield=3`, `Gear=5`, `Init=1`, `TopGun=2` |
| `CarQualityType` | 5 | `Blue=3`, `Green=2`, `Orange=5`, `Purple=4`, `Write=1` |
| `CarRankType` | 4 | `Chip=4`, `Component=3`, `Refit=2`, `Summary=1` |
| `CareerSkillState` | 4 | `Ready=1`, `Unknown=0`, `Used=3`, `Using=2` |
| `CareerSkillType` | 2 | `AdmiralTroopSkill=1`, `Unknown=0` |
| `CareerType` | 6 | `Admiral=1`, `Farmer=4`, `Guard=5`, `Merchant=3`, `None=0`, `Raider=2` |
| `CarriageState` | 5 | `Hide=2`, `PullIn=1`, `PullOut=3`, `Straight=4`, `Turn=5` |
| `ChainPayBoxState` | 3 | `Default=0`, `Received=2`, `Unlocked=1` |
| `ChampionBattlePosterType` | 5 | `None=0`, `Strongest_Eight=1`, `Strongest_Four=2`, `Strongest_King=4`, `Strongest_Two=3` |
| `ChangeMailStatus` | 7 | `InCd=100`, `None=0`, `SendBindNewMail=3`, `SendBindNewMailCode=4`, `SendBindOldMail=1`, `SendBindOldMailCode=2`, `Success=101` |
| `ChangeNameAndPicType` | 2 | `No=0`, `Yes=1` |
| `CharacterType` | 5 | `Hero=Hero`, `Npc=Npc`, `Player=Player`, `TeamPlayer=TeamPlayer`, `Zombie=Zombie` |
| `ChatAddLayoutCommonType` | 4 | `CarnivalMoment=6`, `PrivateGift=5`, `RecordPlayer=4`, `RedPacket=3` |
| `ChatAddLayoutCommonTypeOrder` | 4 | `1=3`, `2=4`, `3=5`, `4=6` |
| `ChatChannelType` | 4 | `CHAT_CHANNEL_ALLIANCE=1`, `CHAT_CHANNEL_COUNTRY=0`, `CHAT_CHANNEL_ROOM=3`, `CHAT_CHANNEL_USER=2` |
| `ChatClass_Enum` | 230 | `ChangeChatRoomName_Ctrl=SlgEngine.Chat.UI.UIChatRoom.UIChangeChatRoomName.Controller.UIChangeChatRoomNameCtrlBase`, `ChangeChatRoomName_View=SlgEngine.Chat.... |
| `ChatColorAlliance` | 4 | `a=1`, `b=1.0`, `g=0.7921568627451`, `r=0.32941176470588` |
| `ChatColorAlliance1` | 4 | `a=1`, `b=0.91372549019608`, `g=0.69803921568627`, `r=0.23137254901961` |
| `ChatColorNormal` | 4 | `a=1`, `b=0.88235294117647`, `g=0.90980392156863`, `r=0.92941176470588` |
| `ChatColorNormal1` | 4 | `a=1`, `b=0.72549019607843`, `g=0.77254901960784`, `r=0.80392156862745` |
| `ChatEmojiNames` | 138 | `1=:emoji_1:`, `10=:emoji_10:`, `100=:emoji_100:`, `101=:emoji_101:`, `102=:emoji_102:`, `103=:emoji_103:`, `104=:emoji_104:`, `105=:emoji_105:` *(+130 more)* |
| `ChatEventEnum` | 91 | `CHAT_ADD_MEMBER_CHANGE=100053`, `CHAT_AUTO_TRA=100204`, `CHAT_BAN_COMMAND=100034`, `CHAT_BLOCK_COMMAND=100001`, `CHAT_CHECK_UI_MAIN_RED_POINT=100021`, `CHAT... |
| `ChatGroupId` | 19 | `alliance=1`, `alliance_adv=11`, `country=0`, `custom=6`, `custom_crossbattle_=4`, `custom_eden_camp_=2`, `custom_migrate=-2`, `custom_season=-1` *(+11 more)* |
| `ChatGroupType` | 22 | `GROUP_ALLIANCE=alliance`, `GROUP_AL_AUTO_INVITE=alAutoInvite`, `GROUP_COUNTRY=country`, `GROUP_CROSS_SERVER=custom_crossbattle_`, `GROUP_CUSTOM=custom`, `GR... |
| `ChatGroupTypeImg` | 9 | `alliance=UIchat_tabicon_alliance02`, `alliance_adv=UIchat_tabicon_alliance02`, `country=UIchat_tabicon_world02`, `custom_migrate=UIchat_tabicon_world02`, `c... |
| `ChatMessageType` | 4 | `COMMON=0`, `FESTIVAL=2`, `GM=3`, `SYSTEM=1` |
| `ChatMsgMap` | 88 | `al.msg=SlgEngine.Chat.NetMessage.ChatShareCommandBase`, `another.login=SlgEngine.Chat.WebMessage.Push.PushAnotherLoginMessageBase`, `chat.ban=SlgEngine.Chat... |
| `ChatMsgState` | 4 | `Normal=0`, `Translated=1`, `TranslatedEx=2`, `TranslatedGoogle=3` |
| `ChatNewsType` | 2 | `HotPoint=1`, `None=0` |
| `ChatNoticePushType` | 3 | `At=1`, `PrivateContent=2`, `PrivateOther=3` |
| `ChatPrefab_Enum` | 38 | `ChangeChatRoomName=Assets/SlgEngine/Main/Prefabs/Slg/UI/ChatNew/ChatRoom/UIChangeChatRoomName.prefab`, `ChatAtMember=Assets/SlgEngine/Main/Prefabs/Slg/UI/Ch... |
| `ChatReportBigType` | 14 | `AllianceAbbr=8`, `AllianceName=7`, `AllianceNoticePic=14`, `AllianceOther=10`, `AllianceWord=6`, `ChatPic=2`, `ChatText=0`, `Moment=13` *(+6 more)* |
| `ChatReportEntrance` | 8 | `AlDanMu=7`, `AllianceInfo=3`, `AllianceNoticePic=8`, `Chat=1`, `Moment=5`, `MomentComment=4`, `MomentPic=6`, `PlayerInfo=2` |
| `ChatReportType` | 10 | `Ads=2`, `Attack=6`, `Gambling=3`, `Gm=4`, `HeadIcon=8`, `NickName=7`, `Other=9`, `Politics=1` *(+2 more)* |
| `ChatShareChannel` | 4 | `TO_ALLIANCE=1`, `TO_COUNTRY=0`, `TO_COUNTRY_LANG=3`, `TO_PERSON=2` |
| `ChatSprite_Enum` | 5 | `ChatHead_AllianceRankPrefix=Assets/Main/Sprites/UI/UIAlliance/UIAlliance_icon_R`, `ChatHead_GmHead=Assets/Main/Sprites/UI/UIHeadIcon/player_head_GM.png`, `C... |
| `ChatVipRoomInviteStatus` | 2 | `EXPIRED=-1`, `NORMAL=0` |
| `ChatVipRoomMyStatus` | 2 | `IN_ROOM=0`, `NOT_IN_ROOM=-1` |
| `ChatVipRoomStatus` | 2 | `DISMISS=-1`, `NORMAL=0` |
| `CheckHeroCampAddEffectList` | 5 | `1=35306`, `2=35307`, `3=35308`, `4=35309`, `5=35322` |
| `CheckHeroRestraintEffectList` | 5 | `1=35325`, `2=35288`, `3=35289`, `4=35290`, `5=35284` |
| `CheckNameType` | 7 | `Exist=5`, `IllegalChar=3`, `MaxNameChar=2`, `MinNameChar=1`, `None=0`, `SensitiveWords=4`, `Unchanged=6` |
| `ChristmasParkourAnimal` | 4 | `Bear=241635`, `Bird=241636`, `Dog=241634`, `Elk=241633` |
| `ChristmasParkourAnimalAddType` | 3 | `GoldAdd=2`, `IdleReward=3`, `Item=1` |
| `ChristmasParkourBuffType` | 3 | `Power=1`, `Shield=3`, `Speed=2` |
| `CityFightResult` | 2 | `Fail=2`, `Success=1` |
| `CityGarbageResult` | 2 | `None=0`, `Reward=1` |
| `CityGarbageResultShowType` | 3 | `NoUseItem=3`, `People=1`, `UseItem=2` |
| `CityLabelTextColor_Blue` | 4 | `a=1.0`, `b=0.94901960784314`, `g=0.76862745098039`, `r=0.32941176470588` |
| `CityLabelTextColor_Blue32` | 4 | `a=255`, `b=242`, `g=196`, `r=84` |
| `CityLabelTextColor_Green` | 4 | `a=1.0`, `b=0.1921568627451`, `g=0.97254901960784`, `r=0.70980392156863` |
| `CityLabelTextColor_Green32` | 4 | `a=255`, `b=49`, `g=248`, `r=181` |
| `CityLabelTextColor_Purple` | 4 | `a=1.0`, `b=0.94117647058824`, `g=0.42352941176471`, `r=0.65490196078431` |
| `CityLabelTextColor_Purple32` | 4 | `a=255`, `b=240`, `g=108`, `r=167` |
| `CityLabelTextColor_Red` | 4 | `a=1.0`, `b=0.49411764705882`, `g=0.49411764705882`, `r=0.99607843137255` |
| `CityLabelTextColor_Red32` | 4 | `a=255`, `b=126`, `g=126`, `r=254` |
| `CityLabelTextColor_White` | 4 | `a=1.0`, `b=0.89411764705882`, `g=0.89411764705882`, `r=0.89411764705882` |
| `CityLabelTextColor_White32` | 4 | `a=255`, `b=228`, `g=228`, `r=228` |
| `CityLabelTextColor_Yellow` | 4 | `a=1`, `b=0.11372549019608`, `g=0.83137254901961`, `r=0.96470588235294` |
| `CityLabelTextColor_Yellow32` | 4 | `a=255`, `b=29`, `g=212`, `r=246` |
| `CityLodArray` | 8 | `0=0`, `1=30`, `2=50`, `3=70`, `4=150`, `5=300`, `6=300`, `7=1050` |
| `CityManageBuffType` | 8 | `AlCompeteScoreAdd1=100006`, `AlCompeteScoreAdd2=100007`, `CapitalPositions=100008`, `CityFever=100001`, `DirectAttackCity=100005`, `GolloesFever=100003`, `G... |
| `CityPeopleAndCarVisibleType` | 2 | `AllHide=2`, `AllShow=1` |
| `CityPointType` | 12 | `Building=100`, `Collect=104`, `CollectRange=105`, `Fog=102`, `Garbage=1`, `GarbageReward=4`, `LandLock=103`, `LandLockReward=5` *(+4 more)* |
| `CityPrologueBuildType` | 4 | `Get=Get`, `Normal=Normal`, `Plant=Plant`, `Ruins=Ruins` |
| `CityWarFeverStatu` | 2 | `CityWarFeverMax=500192`, `CityWarFeverMin=500172` |
| `ClassType` | 2 | `class=1`, `instance=2` |
| `ClickTypeHero` | 3 | `MaxLevel=2`, `MaxPower=1`, `MaxStar=3` |
| `ClickUINeedCloseExtraWorldUI` | 6 | `1=UIPasture`, `2=UIWorldTileUI`, `3=UIResourceCost`, `4=UIWorldSiegePoint`, `5=UISpearWorldPoint`, `6=UIFingerArrow` |
| `ClickUISpecialBtnType` | 16 | `UIBuildUpgradeLackResource=9`, `UIFormationDeleteHero=2`, `UIFormationSelectHero=1`, `UIFormationTableAddHero=3`, `UIHeroAdvanceMainHero=10`, `UIHeroAdvance... |
| `ClickWorldNeedCloseWorldUI` | 8 | `1=UISearch`, `2=UISearchMonster`, `3=UIWorldBlackTile`, `4=UIWorldNoSelectable`, `5=UIWorldExplorePointUI`, `6=UIWorldSamplePointUI`, `7=UIWorldGarbagePoint... |
| `ClickWorldType` | 2 | `Collider=1`, `Ground=0` |
| `CloseUIType` | 3 | `ClickUI=2`, `ClickWorld=1`, `DragWorld=3` |
| `CollectionMailTitleColor_Green` | 4 | `a=1.0`, `b=0.0`, `g=0.41176470588235`, `r=0.30196078431373` |
| `ColliderType` | 2 | `Capsule=2`, `Sphere=1` |
| `CommonCostNeedType` | 6 | `Build=4`, `Goods=3`, `RefreshAll=100`, `Resource=1`, `ResourceItem=2`, `Science=5` |
| `CommonDirection` | 4 | `LeftDown=1`, `LeftTop=4`, `RightDown=2`, `RightTop=3` |
| `CommonQualityColorBlue` | 4 | `a=1`, `b=0.9490196`, `g=0.7882353`, `r=0.6` |
| `CommonQualityColorGreen` | 4 | `a=1`, `b=0.1647059`, `g=0.9764706`, `r=0.6431373` |
| `CommonQualityColorPurple` | 4 | `a=1`, `b=1`, `g=0.5843138`, `r=0.7882353` |
| `CommonQualityColorWhite` | 4 | `a=1`, `b=0.5882353`, `g=0.6392157`, `r=0.7372549` |
| `CommonQualityColorYellow` | 4 | `a=1`, `b=0`, `g=0.4`, `r=0.8470588` |
| `CommonShopCurrencyId` | 2 | `HonorBadge=254000`, `Ruby=242040` |
| `CommonShopType` | 27 | `Adventure=5`, `AlContribute=8`, `AllianceShopPlus=35`, `CastleAdventureShop=29`, `ChristmasActExchangeShop=27`, `ChristmasParkourExchangeShop=26`, `Discount... |
| `ComplexTipType` | 3 | `Hero=3`, `Image=2`, `Text=1` |
| `ComponentUpgradeType` | 2 | `Exp=2`, `Merge=1` |
| `ConnectDirection` | 16 | `Down=16`, `DownToLeft=7`, `DownToRight=9`, `DownToTop=8`, `Left=13`, `LeftToDown=4`, `LeftToRight=5`, `LeftToTop=6` *(+8 more)* |
| `Const_Color_Gray` | 4 | `a=1`, `b=0.48627450980392`, `g=0.48627450980392`, `r=0.48627450980392` |
| `Const_Color_Green` | 4 | `a=1`, `b=0.0`, `g=0.41176470588235`, `r=0.30196078431373` |
| `Const_Color_Red` | 4 | `a=1`, `b=0.2156862745098`, `g=0.26666666666667`, `r=0.83137254901961` |
| `Const_Green_Outline` | 4 | `a=1`, `b=0.074509803921569`, `g=0.43137254901961`, `r=0.30980392156863` |
| `Const_Red_Outline` | 4 | `a=1`, `b=0.066666666666667`, `g=0.066666666666667`, `r=0.59607843137255` |
| `ConsumeItemType` | 2 | `AlMoveCity_LeaderInvite=1`, `AlMoveCity_SysInvite=2` |
| `ConsumeType` | 4 | `ConsumeType_Item=3`, `ConsumeType_Nil=0`, `ConsumeType_Resource=2`, `ConsumeType_Resource_Item=1` |
| `CountryCode` | 115 | `1=AE`, `10=BD`, `100=SCO`, `101=SV`, `102=TH`, `103=TN`, `104=TR`, `105=TW` *(+107 more)* |
| `CountryCodeToLanguage` | 23 | `AE=3`, `AF=3`, `AR=45`, `BR=37`, `CN=8`, `DE=20`, `ENG=14`, `ES=45` *(+15 more)* |
| `CreditStateType` | 2 | `Normal=0`, `Restrict=1` |
| `CrossHitBlockFightType` | 3 | `Fight=2`, `None=0`, `WaitFight=1` |
| `CrossHitBlockType` | 7 | `BattlePhaseOne=3`, `BattlePhaseTwo=4`, `MatchingPhaseOne=1`, `MatchingPhaseTwo=5`, `PremonitoryPhaseOne=2`, `PremonitoryPhaseTwo=6`, `WaitEnd=7` |
| `CrossWonderActState` | 7 | `Close=5`, `End=6`, `None=0`, `Play=3`, `Prepare=2`, `Preview=1`, `Settle=4` |
| `CrossWonderBadgeStarImage` | 3 | `bg=Assets/Main/Sprites/UI/UIPortrait/UIPortraitActivity/c_activity_corss_world_bg_star.png`, `red=Assets/Main/Sprites/UI/UIPortrait/UIPortraitActivity/c_act... |
| `CrossWonderScoreDetailKeys` | 7 | `1=0`, `2=1`, `3=2`, `4=3`, `5=4`, `6=5`, `7=6` |
| `CrossWonderScoreDetailKeys2608` | 8 | `1=0`, `2=1`, `3=2`, `4=3`, `5=4`, `6=5`, `7=6`, `8=7` |
| `CrossWonderScoreKeys` | 7 | `1=type0`, `2=type1`, `3=type2`, `4=type3`, `5=type4`, `6=type5`, `7=type6` |
| `CrossWonderScoreKeys2608` | 8 | `1=type0`, `2=type1`, `3=type2`, `4=type3`, `5=type7`, `6=type4`, `7=type5`, `8=type6` |
| `CrossWonderScoreTips` | 7 | `1=510160`, `2=510161`, `3=510163`, `4=510165`, `5=510162`, `6=511325`, `7=913444` |
| `CrossWonderScoreTips2608` | 8 | `1=510160`, `2=510161`, `3=510163`, `4=510165`, `5=5600175`, `6=510162`, `7=511325`, `8=913444` |
| `CrossWonderScoreType` | 5 | `Arena=arena`, `BurstBoss=burst_boss`, `Fp=fp`, `Truck=truck`, `Vs=vs` |
| `CyanColor32` | 4 | `a=255`, `b=255`, `g=255`, `r=0` |
| `DailyBoxActive` | 5 | `1=30`, `2=70`, `3=120`, `4=180`, `5=260` |
| `DamageTextType` | 10 | `CarHpChange=9`, `Common1=10`, `GetBuff=7`, `GetItem=8`, `HeroNormalAttack=1`, `HeroUltimate=2`, `Miss=6`, `ReduceDamageBuff=5` *(+2 more)* |
| `DamageType` | 2 | `Magic=1`, `Physics=0` |
| `DamageYellowColor32` | 4 | `a=255`, `b=87`, `g=221`, `r=255` |
| `DarkBlueColor` | 4 | `a=1`, `b=0.71`, `g=0.42`, `r=0.24` |
| `DarkRedColor` | 4 | `a=1`, `b=0.10980392156863`, `g=0.2156862745098`, `r=0.8` |
| `DawnTaskState` | 4 | `CanReceive=2`, `Lock=3`, `NoComplete=0`, `Received=1` |
| `DeclareRecordType` | 2 | `Alliance=1`, `ServerZone=2` |
| `DeclareState` | 9 | `Battle=6`, `BattleAdvanceEnd=7`, `BattleNoPlayer=5`, `BattleWaitStart=4`, `End=8`, `None=0`, `Prepare=1`, `SelectPlayer=2` *(+1 more)* |
| `DecorationActivityRewardState` | 3 | `DecorationActivityRewardState_Can_Receive=1`, `DecorationActivityRewardState_Normal=0`, `DecorationActivityRewardState_Received=2` |
| `DecorationChatTitleType` | 2 | `Normal=0`, `Rank=1` |
| `DecorationGainType` | 9 | `DecorationGainType_Arena=5`, `DecorationGainType_Champions=4`, `DecorationGainType_Default=1`, `DecorationGainType_Female=3`, `DecorationGainType_Item_Excha... |
| `DecorationQuality` | 4 | `DecorationGainType_Epic=3`, `DecorationGainType_Legend=4`, `DecorationGainType_Rare=2`, `DecorationQuality_Normal=1` |
| `DecorationSceneType` | 2 | `MarchS4Skin=2`, `Normal=1` |
| `DecorationShowGroup` | 2 | `City=0`, `TacticalWeapon=1` |
| `DecorationSkinType` | 3 | `DragonCastleUpgradeSkinId=10027`, `ValentineFemaleSkinId=10026`, `ValentineMaleSkinId=10025` |
| `DecorationType` | 9 | `DecorationType_ChatBg=8`, `DecorationType_ChatTitle=9`, `DecorationType_Halo=5`, `DecorationType_Head_Frame=2`, `DecorationType_Main_City=1`, `DecorationTyp... |
| `DefaultScreen` | 2 | `x=1920`, `y=1080` |
| `DesertAnnexItemType` | 3 | `BuildStatus=2`, `Mine=1`, `None=0` |
| `DesertLevelFlagIndex` | 21 | `ALL=0`, `Lv1=1`, `Lv10=10`, `Lv11=11`, `Lv12=12`, `Lv13=13`, `Lv14=14`, `Lv15=15` *(+13 more)* |
| `DesertOperateBtnState` | 5 | `Gray=3`, `Green=1`, `None=0`, `NotMeetCondition=4`, `Yellow=2` |
| `DesertResFlagIndex` | 2 | `Cactus=1`, `Crystal=0` |
| `DestroyBuildType` | 2 | `Other=1`, `Self=0` |
| `DestroyRankType` | 2 | `Blood=0`, `Stamina=1` |
| `DetectEvenColorImage` | 7 | `1=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_grey.png`, `2=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_green.png`, `3=Assets/Main/Sprites/UI/... |
| `DetectEvenColorSpecialImage` | 7 | `1=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_grey04.png`, `2=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_green04.png`, `3=Assets/Main/Sprites... |
| `DetectEventBlueColor` | 4 | `a=1`, `b=0.92941`, `g=0.63921`, `r=0.37254` |
| `DetectEventColor` | 7 | `DETECT_EVENT_BLUE=3`, `DETECT_EVENT_GOLDEN=6`, `DETECT_EVENT_GREEN=2`, `DETECT_EVENT_ORANGE=5`, `DETECT_EVENT_PURPLE=4`, `DETECT_EVENT_RED=7`, `DETECT_EVENT... |
| `DetectEventCompleteImage` | 5 | `1=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_light01s.png`, `2=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_light01.png`, `3=Assets/Main/Sprit... |
| `DetectEventGoldenColor` | 4 | `a=1`, `b=0.2196`, `g=0.80392`, `r=0.98823` |
| `DetectEventGreenColor` | 4 | `a=1`, `b=0.2196`, `g=0.88235`, `r=0.58039` |
| `DetectEventOrangeColor` | 4 | `a=1`, `b=0.26274`, `g=0.53333`, `r=0.98039` |
| `DetectEventPurpleColor` | 4 | `a=1`, `b=0.94117`, `g=0.42352`, `r=0.65098` |
| `DetectEventRedColor` | 4 | `a=1`, `b=0.40392`, `g=0.41568`, `r=0.94901` |
| `DetectEventState` | 5 | `DETECT_EVENT_STATE_EXPIRED=3`, `DETECT_EVENT_STATE_FINISHED=1`, `DETECT_EVENT_STATE_HIDDEN=4`, `DETECT_EVENT_STATE_NOT_FINISH=0`, `DETECT_EVENT_STATE_REWARD... |
| `DetectEventType` | 29 | `ALLIANCE_TREASURE=23`, `COLLECT=21`, `DetectEventPVE=7`, `DetectEventPickGarbage=6`, `DetectEventRadarRally=5`, `DetectEventTypeBoss=8`, `DetectEventTypeNor... |
| `DetectEventWhiteColor` | 4 | `a=1`, `b=0.75294`, `g=0.71764`, `r=0.74509` |
| `DetectHelpEventColorImage` | 7 | `1=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_grey03.png`, `2=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_green03.png`, `3=Assets/Main/Sprites... |
| `DetectNpcCityEvenColorImage` | 7 | `1=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_grey02.png`, `2=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_green02.png`, `3=Assets/Main/Sprites... |
| `DetectOverlordEvenColorImage` | 7 | `1=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_grey02.png`, `2=Assets/Main/Sprites/UI/UIRadarCenter2/Detect_event_green02.png`, `3=Assets/Main/Sprites... |
| `DinosaurRescueState` | 3 | `Cure=3`, `Normal=1`, `Rescue=2` |
| `DirectionDown` | 3 | `x=0`, `y=0`, `z=-1` |
| `DirectionLeft` | 3 | `x=-1`, `y=0`, `z=0` |
| `DirectionRight` | 3 | `x=1`, `y=0`, `z=0` |
| `DirectionTop` | 3 | `x=0`, `y=0`, `z=1` |
| `DirectionType` | 4 | `Down=4`, `Left=3`, `Right=2`, `Top=1` |
| `DmaCountry` | 31 | `1=AT`, `10=FI`, `11=FR`, `12=GR`, `13=HR`, `14=HU`, `15=IE`, `16=IT` *(+23 more)* |
| `DomeLevel` | 4 | `0=0`, `1=2`, `2=3`, `3=1` |
| `DomeRadius` | 4 | `0=0`, `1=34`, `2=44`, `3=18` |
| `DomeRange` | 4 | `Max=2`, `Middle=1`, `Min=3`, `Zero=0` |
| `DragWorldNeedCloseExtraWorldUI` | 9 | `1=UIPasture`, `2=UIPasture`, `3=UIWorldSiegePoint`, `4=UISpearWorldPoint`, `5=UIWorldNewsTips`, `6=UIWorldPoint`, `7=UIWorldNewsAbbrDetail`, `8=UIActBossTip... |
| `DragonActStage` | 6 | `Battle=4`, `Battle2=5`, `Matching=3`, `None=0`, `Sign=2`, `Vote=1` |
| `DragonApply` | 2 | `ApplyForBattle=1`, `NotParticipating=2` |
| `DragonBossState` | 3 | `Born=2`, `Dead=3`, `Hide=0` |
| `DragonBuildingTypes` | 7 | `DragonAllianceFlagOther=10040`, `DragonAllianceFlagSelf=10030`, `DragonBoss=10060`, `DragonCenterBuild=10020`, `DragonEmptyBuild=10000`, `DragonHospitalBuil... |
| `DragonPlayerState` | 3 | `Main=1`, `None=0`, `Sub=2` |
| `DragonSecretState` | 4 | `Cool_Down=3`, `Enemy_Escort=2`, `Free=0`, `Our_Escort=1` |
| `DragonSignState` | 12 | `ActiveNotEnough=11`, `AssignNotEnough=10`, `Expire=7`, `HasSign=1`, `LastWeekScoreNotEnough=12`, `MemberNotEnough=8`, `NO_ALLIANCE=3`, `NotR4R5=2` *(+4 more)* |
| `DragonTimeState` | 4 | `Battle=2`, `End=3`, `None=0`, `Prepare=1` |
| `EAgeGameState` | 2 | `Loading=1`, `MainCity=2` |
| `ESidebarType` | 5 | `AllianceDonate=4`, `HeroRecruit=5`, `Science=1`, `Training=3`, `Work=2` |
| `ESimpleModeReasonMask` | 4 | `None=0`, `Stutter=2`, `TroopCount=1`, `Volcano=4` |
| `EWorldBossRankTabIndex` | 3 | `Person=2`, `Rank=0`, `Reward=1` |
| `EdenAreaType` | 4 | `DEFAULT=0`, `FIGHT_AREA=1`, `NORTH_BORN_AREA=2`, `SOUTH_BORN_AREA=3` |
| `EdenCamp` | 3 | `DEFAULT=0`, `NORTH=1`, `SOUTH=2` |
| `EffectAttrType` | 3 | `Flag_Add=2`, `Normal=0`, `Talent_Skill_Send=1` |
| `EffectCategory` | 5 | `Battle=1`, `Develop=2`, `Max=3`, `Min=1`, `Others=3` |
| `EffectCoupleType` | 20 | `ATTACK_ALLIANCE_NEUTRAL_CITY_ATTACK=100701`, `ATTACK_ALLIANCE_NEUTRAL_CITY_DEFEND=100702`, `ATTACK_BUILD_ATTACK=100401`, `ATTACK_BUILD_DEFEND=100402`, `ATTA... |
| `EffectDefine` | 250 | `ADD_BUILD_ARROW_TOWER_NUM=31013`, `ADD_CAMP_RESTRAINT_35230=35230`, `ADD_CAN_BUILD_NUM=30095`, `ADD_FACTORY_SPEED=30107`, `ADD_FARM_SPEED=30105`, `ADD_FORMA... |
| `EffectLocalType` | 10 | `Dialog=4`, `NegativeNum=6`, `NegativePercent=10`, `NegativeTime=8`, `Num=1`, `Percent=3`, `PositiveNum=5`, `PositivePercent=9` *(+2 more)* |
| `EffectLocalTypeInEffectDesc` | 4 | `NegativePercent=4`, `Num=0`, `Percent=1`, `Thousandth=2` |
| `EffectObjType` | 3 | `AlignCollider=2`, `Normal=0`, `Sprite=1` |
| `EffectReasonType` | 40 | `ARMY_SKILL=27`, `ARTIFACT=18`, `Alliance_Career=13`, `Alliance_Science=8`, `BASE_TALENT=16`, `BUABLE=26`, `Building=1`, `CAR_EQUIP=24` *(+32 more)* |
| `EffectStateDefine` | 8 | `CHINESE_WIND_SKIN=500526`, `LORD_SKILL_PROTECTED=501051`, `NEW_PLAYER_PROTECTED=500009`, `PLAYER_PROTECTED_TIME1=500000`, `PLAYER_PROTECTED_TIME2=500001`, `... |
| `EggSubType` | 6 | `Aircraft=4`, `Fish=2`, `Levels=3`, `Migrant=5`, `TradePost=1`, `TradePostSliver=6` |
| `EntityAssets` | 2 | `CollectGarbageUI=Assets/Main/Prefabs/March/CollectGarbageUI.prefab`, `TroopLineDrag=Assets/Main/Prefabs/March/TroopLineDrag.prefab` |
| `EnumActivityStatus` | 3 | `Close=3`, `Open=2`, `Preview=1` |
| `EnumDemonHunterCampStatus` | 6 | `AllFinished=5`, `CanAccept=2`, `CanSubmit=4`, `InTask=3`, `None=6`, `NotUnlock=1` |
| `EnumDestinationSignalType` | 8 | `Alliance=3`, `EmptyGround=1`, `EnemyBuild=4`, `EnemyMarch=7`, `My=2`, `None=0`, `Other=5`, `UnReachAble=6` |
| `EnumItemId` | 3 | `Heart=301042`, `LauraFragment=210302`, `MoonCoin=248103` |
| `EnumQualityLevel` | 4 | `High=3`, `Low=1`, `Middle=2`, `Off=0` |
| `EnumQualitySetting` | 9 | `FPS=QualitySetting.FPS`, `PostProcess_Bloom=QualitySetting.PostProcess.Bloom`, `PostProcess_ColorAdjustments=QualitySetting.PostProcess.ColorAdjustments`, `... |
| `EquipSlotReq` | 6 | `0=hat`, `1=cloth`, `2=trousers`, `3=shoe`, `4=weapon`, `5=bag` |
| `EventBubbleType` | 3 | `CityNpcBubble=2`, `TriggerBubble=1`, `TriggerNpcBubble=3` |
| `ExDamageType` | 2 | `attackPercent=1`, `hpPercent=2` |
| `ExchangeDefine` | 2 | `MONTH_CARD_ID=9007`, `SUB_MONTH_CARD_ID=9012` |
| `ExitDragonType` | 6 | `FromExchange=6`, `FromKick=5`, `FromLeaveAlliance=4`, `FromPlayer=1`, `FromResult=3`, `FromScorePanel=2` |
| `ExpSource` | 10 | `Army=5`, `Building=3`, `Factory=2`, `Farming=1`, `GM=0`, `KillMonster=9`, `Order=6`, `Pasture=8` *(+2 more)* |
| `ExtraInfoMsgType` | 19 | `ALLIANCE_ABBR=104`, `ALLIANCE_ANNOUNCEMENT=106`, `ALLIANCE_CHANNEL=203`, `ALLIANCE_CHAT_ANNOUNCEMENT=107`, `ALLIANCE_DECLARATION=105`, `ALLIANCE_MAIL=204`, ... |
| `FactoryBuild` | 22 | `1=711000`, `10=102000`, `11=103000`, `12=106000`, `13=104000`, `14=105000`, `15=106000`, `16=107000` *(+14 more)* |
| `FactoryDataType` | 2 | `FactoryDataType_Normal=0`, `FactoryDataType_PVE=1` |
| `FactoryIdToProductEffectId` | 5 | `707000=30114`, `708000=30117`, `711000=30113`, `717000=30115`, `718000=30116` |
| `FactoryProductType` | 4 | `FactoryProductType_Item=1`, `FactoryProductType_Resource=2`, `FactoryProductType_Resource_Item=0`, `FactoryProductType_Score=3` |
| `FactoryWorkState` | 4 | `Free=0`, `Full=2`, `NotOpen=3`, `Work=1` |
| `FakeAttackPos` | 3 | `x=100`, `y=0`, `z=100` |
| `FakePVPStage` | 5 | `End=4`, `Fight=3`, `Lineup=0`, `Load=1`, `Opening=2` |
| `FalseVisiblePos` | 3 | `x=10000`, `y=1000`, `z=0` |
| `FarmAdjust` | 4 | `bottom=300`, `left=520`, `right=500`, `top=450` |
| `FarmingEnoughType` | 2 | `Feed=2`, `Plant=1` |
| `FightResult` | 4 | `DEFAULT=-1`, `DRAW=2`, `OTHER_WIN=1`, `SELF_WIN=0` |
| `FirstJoinAllianceType` | 2 | `No=0`, `Yes=1` |
| `FirstPayType` | 3 | `GetOnce=1`, `ThreeDayOneBox=3`, `ThreeDayThreeBox=2` |
| `FishPoolState` | 2 | `Close=0`, `Open=1` |
| `FlipEulerAngles` | 3 | `x=0`, `y=0`, `z=180` |
| `FlyGetResourceDelta` | 3 | `x=0`, `y=4`, `z=0` |
| `FogCanUnlockEffectAnimName` | 4 | `CanLockToUnlock=CanLockToUnlock`, `CanUnlockIdle=CanUnlockIdle`, `LockIdle=LockIdle`, `LockToCanUnlock=LockToCanUnlock` |
| `FogCanUnlockEffectAnimSort` | 4 | `CanLockToUnlock=1`, `CanUnlockIdle=2`, `LockIdle=4`, `LockToCanUnlock=3` |
| `FogType` | 2 | `Black=0`, `White=1` |
| `FoodFestivalCookState` | 3 | `fail=0`, `normal=1`, `perfect=2` |
| `FoodFestivalEatStage` | 5 | `Close=4`, `Open=3`, `Reserve=2`, `UnBuild=0`, `UnReserve=1` |
| `FoodFestivalEatStatus` | 7 | `Close=0`, `End=4`, `Finish=3`, `NoAlliance=-1`, `NotOnList=5`, `Ready=1`, `Start=2` |
| `ForceChangeScene` | 2 | `City=0`, `World=1` |
| `FormStatusType` | 2 | `FrequencyBase=1`, `TimeBase=0` |
| `FormStatusType2` | 3 | `Default=0`, `DirectAttackCity=1`, `MarchBuff=2` |
| `FormationAddSoldierType` | 10 | `BuildUpgrade=2022`, `FormationScience=17`, `GoFirstPackage=61`, `HeroExchange=25`, `HeroUpgrade=24`, `KillMonster=15`, `RadarMonster=16`, `ThirdHeroBuild=14... |
| `FormationName` | 3 | `1=302032`, `2=302033`, `3=302034` |
| `FormationOpenType` | 3 | `Arena3V3Battle=1`, `Arena3V3Defense=2`, `None=0` |
| `FormationSaveType` | 4 | `PVESquad=1`, `PVESquadAuto=0`, `TruckAttackSquad=8`, `TruckDefenceSquad=4` |
| `FormationSetting` | 14 | `Arena=3`, `Arena3V3Battle=9`, `Arena3V3Defense=10`, `CanNotModify=100`, `Defense=6`, `Elite=4`, `Invalid=0`, `LandingOperation=8` *(+6 more)* |
| `FormationSettingServer` | 4 | `BATCH_ARENA=3`, `DEFEND=1`, `ELITE=2`, `NORMAL=0` |
| `FortAtkState` | 3 | `Atk=2`, `Done=3`, `Wait=1` |
| `FoxAnimA` | 10 | `Anim_Born=A_born`, `Anim_Born_Away=A_born_away`, `Anim_Born_Into=A_born_into`, `Anim_Born_Out=A_born_out`, `Anim_Click=click`, `Anim_Feed=feeding`, `Anim_Gr... |
| `FoxAnimB` | 3 | `Anim_BornL=B_born_L`, `Anim_BornR=B_born_R`, `Anim_Greet=greet` |
| `FrameType` | 2 | `Common=1`, `HeroFrame=0` |
| `FreeTimeBubbleType` | 3 | `Build=3`, `Girl=1`, `Hero=2` |
| `FunctionBtnType` | 65 | `Activity=16`, `Aircraft=56`, `Alliance=6`, `AutoAI=14`, `BluePrint=15`, `BuildListBtn=53`, `CampBonus=51`, `CampRestraint=52` *(+57 more)* |
| `GMSettings` | 4 | `1=7`, `2=22`, `3=25`, `4=26` |
| `GOODS_TYPE` | 79 | `BUILD_BAUBLE=120`, `CALL_BOSS_OR_REWARD=126`, `FILL_UP_EVENT_NUM=113`, `GOODS_TYPE_0=0`, `GOODS_TYPE_1=1`, `GOODS_TYPE_102=102`, `GOODS_TYPE_106=106`, `GOOD... |
| `GOODS_TYPE2` | 5 | `HeroExp=20`, `MarchSpeedItem=22`, `PVEEnergy=3`, `ResourceItem=1`, `StaminaItem=21` |
| `GameEffectReason` | 50 | `ARMY_SKILL=27`, `ARTIFACT=18`, `Alliance_Career=13`, `Alliance_Science=8`, `BASE_TALENT=16`, `BUABLE=26`, `Building=1`, `CAR_EQUIP=24` *(+42 more)* |
| `GarageBuildIds` | 4 | `1=427000`, `2=793000`, `3=794000`, `4=795000` |
| `GarageRefitTalentType` | 2 | `Normal=1`, `Skill=2` |
| `GarbageResourceAnim` | 3 | `Idle=idle`, `Open=open`, `Reward=reward` |
| `GatherAdjust` | 4 | `bottom=100`, `left=200`, `right=200`, `top=200` |
| `GetRewardTitleType` | 2 | `BattleFail=2`, `Common=1` |
| `GhostKingBornType` | 5 | `CountDown=1`, `Donate=0`, `Failed=4`, `Opened=2`, `Success=3` |
| `GhostKingMonsterType` | 2 | `Die=1`, `NoDie=0` |
| `GhostKingRankTabIndex` | 2 | `Rank=0`, `Reward=1` |
| `GiftPackType` | 6 | `HeroMonthCard=8`, `MonthCard=5`, `PromotionPay=3`, `RedPacket=11`, `Unknown=-1`, `WeekCard=6` |
| `GirlCollectBubbleType` | 3 | `Confirm=2`, `FreeToFinish=3`, `Progress=1` |
| `GlobalShaderLod` | 3 | `HIGH=2`, `LOW=0`, `MIDDLE=1` |
| `GloryBattleDetailType` | 8 | `CrashBuilding=4`, `CrashCenter=5`, `Default=0`, `FoldUpFlag=2`, `MISSILE_ATTACK_MAIN=7`, `Occupy=3`, `PlaceFlag=1`, `Win=6` |
| `GloryBattleResult` | 3 | `Lose=2`, `None=0`, `Win=1` |
| `GloryBattleState` | 4 | `After=3`, `Before=1`, `None=0`, `Ongoing=2` |
| `GloryContributionType` | 5 | `DECLARE_SCORE=4`, `DONATE_ALLIANCE_STORE=3`, `OCCUPY_DESERT=1`, `OCCUPY_ENEMY_DESERT=5`, `SEASON_BUILDING=2` |
| `GloryDeclareRecordAtkType` | 2 | `Attack=1`, `Defence=2` |
| `GloryDeclareRecordKoType` | 2 | `Ko=1`, `No=0` |
| `GloryDeclareRecordWinType` | 2 | `Lose=0`, `Win=1` |
| `GloryDeclareType` | 2 | `List=2`, `Match=1` |
| `GloryInfoTab` | 6 | `History=5`, `None=0`, `Rank=3`, `RankHistory=4`, `Summary=1`, `SummaryHistory=2` |
| `GloryPeriod` | 5 | `None=0`, `Prepare=2`, `Settle=4`, `Start=3`, `Unopened=1` |
| `GloryScoreRankType` | 2 | `Season=0`, `Week=1` |
| `GlorySeverType` | 3 | `Opponent=2`, `Other=3`, `Self=1` |
| `GlorySwapPanelMode` | 2 | `Confirm=2`, `Initiate=1` |
| `GlorySwapResult` | 3 | `Doing=0`, `Fail=2`, `Success=1` |
| `GlorySwapStatus` | 3 | `Agree=1`, `Refuse=2`, `Requesting=0` |
| `GoToChangeNameType` | 2 | `chat=2`, `player=1` |
| `GoToType` | 3 | `GotoBuilding=0`, `GotoUI=1`, `None=-1` |
| `GoType` | 12 | `BuildList=5`, `BuildRoad=43`, `CollectResource=45`, `DailyBarn=52`, `DailyBuildUp=51`, `DailyFoodFactory=53`, `Farm=40`, `Go=2` *(+4 more)* |
| `GolloBoxItemId` | 4 | `1=200185`, `2=200185`, `3=200185`, `4=200186` |
| `GolloesSound` | 4 | `1=Effect_Golloes_worker`, `2=Effect_Golloes_explorer`, `3=Effect_Golloes_trader`, `4=Effect_Golloes_warrior` |
| `GolloesType` | 5 | `Caravan=5`, `Explorer=2`, `Trader=3`, `Warrior=4`, `Worker=1` |
| `GotoArenaAimToType` | 3 | `None=1`, `RewardPreview_Daily=2`, `RewardPreview_Final=3` |
| `GotoItemTipType` | 2 | `Bauble=2`, `Common=1` |
| `GotoType` | 4 | `Activity=4`, `Build=1`, `Package=3`, `Science=2` |
| `GrayBtnColor` | 4 | `a=1`, `b=0.26274509803922`, `g=0.26274509803922`, `r=0.26274509803922` |
| `GrayColor` | 4 | `a=1`, `b=0.45`, `g=0.45`, `r=0.45` |
| `GrayTMPColor` | 4 | `a=1`, `b=0.145`, `g=0.145`, `r=0.145` |
| `GreenBtnColor` | 4 | `a=1`, `b=0.003921568627451`, `g=0.21960784313725`, `r=0.050980392156863` |
| `GreenBtnShadowLightColor` | 4 | `a=1`, `b=0.6156862745098`, `g=0.96470588235294`, `r=0.75686274509804` |
| `GreenColor` | 4 | `a=1`, `b=0.30196078431373`, `g=0.74901960784314`, `r=0.56470588235294` |
| `GreenColor32` | 4 | `a=255`, `b=26`, `g=250`, `r=166` |
| `GreenColor32_S3` | 4 | `a=255`, `b=51`, `g=216`, `r=0` |
| `GreenColor_Normal` | 4 | `a=1`, `b=0.1019608`, `g=0.9803922`, `r=0.6509804` |
| `GreenColor_S3` | 4 | `a=1`, `b=0.2`, `g=0.84705882352941`, `r=0` |
| `GreenTMPColor` | 4 | `a=1`, `b=0.004`, `g=0.219`, `r=0.051` |
| `GuideAnimObjectType` | 68 | `Chapter2CameraMoveScene=40`, `EndPrologueBridgeScene=45`, `ExploreMonster=3`, `FightOnBoardQTETimeline1=51`, `FightOnBoardQTETimeline2=52`, `FirstExpandDome... |
| `GuideArrowDirection` | 2 | `LeftDown=1`, `RightDown=0` |
| `GuideArrowPositionStyle` | 4 | `Position_Down=0`, `Position_Left=3`, `Position_Right=2`, `Position_Up=1` |
| `GuideArrowStyle` | 5 | `ClickCallAirDrop=3`, `Finger=0`, `Green=2`, `NOArrow=4`, `Yellow=1` |
| `GuideBuildState` | 3 | `Box=3`, `NeedConnect=2`, `Normal=1` |
| `GuideCameraShowUIMainType` | 3 | `Hide=1`, `None=0`, `Show=2` |
| `GuideCanDoType` | 2 | `No=2`, `Yes=1` |
| `GuideEndShowQuestType` | 2 | `No=1`, `Show=0` |
| `GuideFingerPositionStyle` | 4 | `Position_Down=0`, `Position_Left=3`, `Position_Right=2`, `Position_Up=1` |
| `GuideForceType` | 2 | `Force=1`, `Soft=0` |
| `GuideGoType` | 2 | `Build=1`, `None=0` |
| `GuideJumpType` | 79 | `AllianceLeader=23`, `AllianceMember=13`, `AttackLevelMonster=41`, `Bubble=40`, `BuildBubble=53`, `BuildLevel=11`, `BuildPlace=1`, `BuildRoad=16` *(+71 more)* |
| `GuideJumpUnlockBtnType` | 3 | `1=1`, `2=2`, `3=4` |
| `GuideMoveArrowPlayAnimName` | 2 | `Down=1`, `Up=2` |
| `GuideMoveCameraType` | 14 | `AllianceChief=4`, `AllianceMember=5`, `BattleLevelArea=30`, `Build=2`, `CityTroop=3`, `CollectResource=9`, `FollowNpc=8`, `Garbage=10` *(+6 more)* |
| `GuideMoveSeasonDesertType` | 4 | `AllianceBlock=3`, `Any=4`, `Block=2`, `OwnLevel=1` |
| `GuideNpcDoNextType` | 3 | `Auto=0`, `WaitWalk=1`, `WaitWalkDelete=2` |
| `GuideNpcPosition` | 2 | `Left=1`, `Right=2` |
| `GuideOrderState` | 4 | `CanSubmit=2`, `Delete=4`, `Finish=3`, `NoSubmit=1` |
| `GuideOrderType` | 3 | `CanSubmit=1`, `NoSubmit=3`, `OrderItemType=2` |
| `GuideOverheadDialogType` | 2 | `Player=6`, `Trigger=1` |
| `GuidePlayMovieType` | 74 | `BaseZeroUpgrade=11`, `BuildBuilding=8`, `BusinessPlaneArrive=16`, `Chapter2CameraMoveScene=63`, `FactoryShowFreeBtn=40`, `Farm=1`, `FarmWithoutTimeLine=15`,... |
| `GuidePrologueFlag` | 2 | `End=1`, `Start=0` |
| `GuideSceneType` | 3 | `City=1`, `Pve=3`, `World=2` |
| `GuideSetNormalVisible` | 2 | `Hide=2`, `Show=1` |
| `GuideState` | 8 | `CityCopter=3`, `LevelOne=1`, `Normal=0`, `OpeningDebut=2`, `Over=-1`, `Soldier=4`, `UnLanlockTwo=5`, `UnLanlockTwoShowTime=6` |
| `GuideTimeLineBubbleType` | 4 | `Cow=4`, `Migrate=3`, `OstrichEgg=1`, `ZeroRocket=2` |
| `GuideTimeLineShowMarkerType` | 8 | `End=999`, `Five=5`, `Four=4`, `One=1`, `Start=998`, `Three=3`, `Two=2`, `Zero=0` |
| `GuideTipPosition` | 4 | `LeftDown=3`, `LeftUp=1`, `RightDown=4`, `RightUp=2` |
| `GuideTriggerType` | 152 | `AfterCityDomeExpend=83`, `AllianceAutoMoveCity=21`, `BackCityAfterRecruit=46`, `BagFullInPve=71`, `BarrelCarEnter=240`, `BridgeClickStart=113`, `BridgeFinis... |
| `GuideType` | 250 | `ActiveNpc=537`, `AddHeroTrialHero=589`, `AircraftMainToggleClick=629`, `AttackPveMonster=551`, `BA_StopZombieWave=557`, `BA_UpgradeBuild=552`, `BA_ZombieKic... |
| `GuideUIMainShowType` | 2 | `Hide=1`, `Show=2` |
| `HandbookType` | 2 | `Fish=1`, `Fossil=2` |
| `HaveAllianceType` | 2 | `No=2`, `Yes=1` |
| `HeroAdvanceConsumeType` | 2 | `ConsumeType_Same_Camp=2`, `ConsumeType_Same_Hero=1` |
| `HeroAdvanceGuideSignalType` | 7 | `Enter=1`, `HideHeroStarUpBlack=7`, `HideMainHeroBlack=3`, `HideSubHeroBlack=5`, `ShowHeroStarUpBlack=6`, `ShowMainHeroBlack=2`, `ShowSubHeroBlack=4` |
| `HeroBountyRarity` | 6 | `Blue=3`, `Green=2`, `Orange=5`, `Purple=4`, `Red=6`, `White=1` |
| `HeroCamp` | 5 | `All=-1`, `MAFIA=1`, `NEW_HUMAN=0`, `UNION=2`, `ZELOT=3` |
| `HeroCampBuildToCamp` | 3 | `304000=2`, `305000=3`, `306000=1` |
| `HeroCampCampToBuild` | 3 | `1=306000`, `2=304000`, `3=305000` |
| `HeroCampName` | 3 | `1=158002`, `2=158003`, `3=158005` |
| `HeroCellSmallStyle` | 2 | `Normal=0`, `Weapon=1` |
| `HeroColor` | 4 | `BLUE=3`, `GREEN=4`, `ORANGE=1`, `PURPLE=2` |
| `HeroEffectDefine` | 111 | `AgilityRate=71002`, `AircraftAttackAddRate=75155`, `AircraftBuildingAttack=50054`, `AircraftBuildingDefence=50056`, `AircraftBuildingLastAttack=50055`, `Air... |
| `HeroEntrustNeedType` | 3 | `Goods=3`, `Resource=2`, `ResourceItem=1` |
| `HeroEntrustState` | 2 | `No=0`, `Yes=1` |
| `HeroEquipConst` | 8 | `EQUIP_ICON=110100`, `EquipPromoteStage=6`, `EquipSlot=4`, `SPEquipMaxLevel=25`, `SPEquipMaxStar=5`, `SPEquipStage=5`, `UpgradeItemType=211`, `UpgradeItemTyp... |
| `HeroGrowthTaskStatus` | 5 | `Complete=4`, `LackHero=1`, `LackSkill=2`, `Rewarded=5`, `SkillLvUnfit=3` |
| `HeroInfoViewType` | 2 | `HeroList=1`, `HeroPreview=2` |
| `HeroIntensifyCostType` | 3 | `Medal=2`, `Open=3`, `Poster=1` |
| `HeroIntensifySlotType` | 2 | `Normal=0`, `Random=1` |
| `HeroIntensifyState` | 5 | `NeedBuildingLevel=4`, `NeedSeason=5`, `Normal=1`, `ToRandom=3`, `Unlocked=2` |
| `HeroIntensifyTabState` | 5 | `Hide=2`, `NeedBuildingLevel=3`, `NeedHeroMaxed=5`, `NeedSeason=4`, `Normal=1` |
| `HeroJob` | 3 | `Defense=1`, `exportation=2`, `subsidiary=3` |
| `HeroLackTipsType` | 8 | `HeroLackTipsType_Activity=6`, `HeroLackTipsType_Debris_Exchange=2`, `HeroLackTipsType_Detect_Event=7`, `HeroLackTipsType_First_Charge=3`, `HeroLackTipsType_... |
| `HeroListSortType` | 3 | `Level=1`, `Power=2`, `Quality=0` |
| `HeroListSortTypeSort` | 3 | `1=0`, `2=1`, `3=2` |
| `HeroMonthCardRewardState` | 4 | `REWARD_STATE_CAN_RECEIVE=1`, `REWARD_STATE_LOCK=2`, `REWARD_STATE_RECEIVED=3`, `REWARD_STATE_UNRECEIVED=4` |
| `HeroSkillState` | 3 | `CanLock=2`, `Lock=1`, `Unlock=0` |
| `HeroSkillToHeroId` | 5 | `BuildFreeTime=1006`, `Energy=11001`, `Gear=1012`, `RefitPaper=1017`, `ScienceFreeTime=22001` |
| `HeroSkillType` | 10 | `DEFAULT=0`, `FIX_ROUND_SKILL=24`, `FORMATION_SKILL=2`, `GLOBAL_SKILL=1`, `NORMAL_SKILL=10`, `RAGE_SKILL=11`, `ROBOT_SKILL=3`, `SPECIAL_HERO_ADD_SKILL=13` *(... |
| `HeroStarUseCommon` | 2 | `No=0`, `Yes=1` |
| `HeroStarUseType` | 3 | `OnlySameColor=3`, `SameCampAndSameColor=2`, `UseSelf=1` |
| `HeroState` | 4 | `FormationInCity=8`, `FormationMarch=1`, `Free=0`, `StationBuilding=7` |
| `HeroStationEffectType` | 6 | `GlobalMoney=1`, `HeroExp=3`, `Normal=0`, `StorageLimit=2`, `TradeCenterMoney=10001`, `TroopLimit=4` |
| `HeroStationSkillEffectType` | 4 | `1000=1`, `1001=2`, `1002=4`, `1003=3` |
| `HeroStationState` | 5 | `Current=1`, `Disabled=5`, `Idle=2`, `Namesake=4`, `Other=3` |
| `HeroTalentCellIconType` | 2 | `Big=1`, `Small=2` |
| `HeroTalentCellState` | 3 | `NoPre=0`, `Pre=1`, `Yes=2` |
| `HeroTalentColor` | 3 | `Blue=3`, `Orange=2`, `Red=1` |
| `HeroTalentLineCellState` | 2 | `Gray=0`, `Light=1` |
| `HeroTalentUseType` | 2 | `Change=2`, `Reset=1` |
| `HeroType` | 5 | `Aircraft=3`, `All=0`, `Missile=2`, `None=-1`, `Tank=1` |
| `HeroXmlState` | 5 | `HeroXMLState_Hide=3`, `HeroXMLState_Max=5`, `HeroXMLState_NeverGet=4`, `HeroXMLState_Normal=1`, `HeroXMLState_Prepare=2` |
| `HideCountryFlag` | 4 | `1=TW`, `2=HK`, `3=MO`, `4=CN` |
| `HospitalPanelStateType` | 3 | `NoSoldier=0`, `Select=2`, `Treating=1` |
| `IceAnimalsCreateType` | 2 | `Default=1`, `DinosaurRescue=3` |
| `IceCaveActOpenState` | 7 | `Fight=2`, `FightEnd=3`, `Preview=0`, `PreviewToFight=6`, `ToSeasonEnd=4`, `Wait=1`, `WaitToFight=5` |
| `IceCaveEventType` | 4 | `IceCaveFishingEnd=2`, `IceCaveOccupySuccess=1`, `IceCaveTax=3`, `IceCaveTaxRedPacket=4` |
| `IceCaveLogType` | 3 | `IceCaveFight=1`, `IceCaveFishing=2`, `IceCaveTaxation=3` |
| `IceCaveStatus` | 4 | `Fighting=2`, `NotOpen=1`, `Occupy=3`, `Priview=0` |
| `IceCaveToggleType` | 5 | `All=1`, `AllianceOccupy=2`, `MyOccupy=3`, `None=0`, `Opening=4` |
| `IdVerFuncType` | 2 | `CHAT=2`, `PAY=1` |
| `IdVerKidAuthType` | 3 | `BEFORE_GAME=2`, `KID=1`, `NONE=0` |
| `IdVerStatus` | 2 | `PASS=1`, `UNVERIFIED=0` |
| `IrrigationType` | 2 | `Farmland=1`, `Pasture=2` |
| `IsGold` | 2 | `NoUseGold=0`, `UseGold=1` |
| `ItemColor` | 7 | `BLUE=2`, `GOLDEN=5`, `GREEN=1`, `ORANGE=4`, `PURPLE=3`, `SSS=6`, `WHITE=0` |
| `ItemHotPage` | 2 | `No=0`, `Yes=1` |
| `ItemProductBuild` | 7 | `1=736000`, `2=737000`, `3=731000`, `4=728000`, `5=432000`, `6=813000`, `7=812000` |
| `ItemRewardType` | 5 | `BLUE=1`, `FIXED=0`, `GOLD=4`, `ORANGE=3`, `PURPLE=2` |
| `ItemSpdMenu` | 16 | `ItemSpdMenu_ALL=1`, `ItemSpdMenu_City=7`, `ItemSpdMenu_Desert_Heal=21`, `ItemSpdMenu_DuanZao=8`, `ItemSpdMenu_Fix_Ruins=22`, `ItemSpdMenu_GirlCollect=24`, `... |
| `JoyStickMode` | 3 | `Fixed=1`, `Half=2`, `Unfixed=0` |
| `KingWinNumStarImage` | 2 | `3=Assets/Main/Sprites/UI/UIPortrait/UIPortraitActivity/c_activity_cross_wrold_city_star2.png`, `5=Assets/Main/Sprites/UI/UIPortrait/UIPortraitActivity/c_act... |
| `KingdomCdReason` | 8 | `Apply=4`, `Cancel=2`, `Def=-1`, `Delete=3`, `Level=6`, `None=0`, `Prepare=5`, `Reject=1` |
| `KingdomPositionConditionType` | 3 | `All=1`, `AllianceList=2`, `AllianceListR5R4=3` |
| `LWSoundAssets` | 41 | `AddSoldiers=Add_Soldiers`, `AutoBattle01=Auto_Battle_01`, `AutoBattle02=Auto_Battle_02`, `CitySoldierClick=army_soldier`, `Click_Action=Click_Action`, `Clic... |
| `LandLockBubbleState` | 7 | `Bridge=Bridge`, `Hide=Hide`, `Locked=Locked`, `None=None`, `Pay=Pay`, `Pve=Pve`, `Unlocked=Unlocked` |
| `LandLockBubbleType` | 6 | `Axe=2`, `Green=0`, `Help=1`, `Red=3`, `Wood=5`, `Yellow=4` |
| `LandLockBubbleVisibleType` | 2 | `Hide=1`, `Show=2` |
| `LandLockCondition` | 11 | `NeedBuilding=5`, `NeedChapter=6`, `NeedItem=3`, `NeedPrior=7`, `NeedResource=2`, `NeedResourceItem=4`, `Ok=1`, `ToFinish=10` *(+3 more)* |
| `LandLockDomeExRadius` | 4 | `0=0`, `1=-1.2`, `2=-1.0`, `3=-1.2` |
| `LandLockRewardType` | 5 | `Call=4`, `CallChest=2`, `CallSoldier=3`, `Chest=1`, `None=0` |
| `LandLockState` | 5 | `Any=-1`, `Finished=5`, `Hide=1`, `Locked=2`, `Unlocked=4` |
| `LandLockTopIcon` | 3 | `None=None`, `Red=Red`, `Yellow=Yellow` |
| `LandLockUnlockAnim` | 3 | `ChopTree=1`, `None=0`, `SoldierWalk=2` |
| `Language` | 51 | `Afrikaans=1`, `Albanian=2`, `Arabic=3`, `Basque=4`, `Belarusian=5`, `Bulgarian=6`, `Catalan=7`, `ChineseSimplified=8` *(+43 more)* |
| `LanguageName` | 50 | `1=Afrikaans`, `10=Croatian`, `11=Czech`, `12=Danish`, `13=Dutch`, `14=English`, `15=Estonian`, `16=Faroese` *(+42 more)* |
| `LanguageToIndex` | 13 | `ar=3`, `de=20`, `en=14`, `es=45`, `fr=18`, `it=26`, `ja=27`, `ko=28` *(+5 more)* |
| `LanguageToShortCode` | 4 | `14=en`, `27=ja`, `28=ko`, `9=zh_TW` |
| `LayerType` | 3 | `Junk=Junk`, `Member=Member`, `Zombie=Zombie` |
| `LeagueMatchStage` | 7 | `Compete=5`, `DrawLots=3`, `DrawLotsFinished=4`, `FinalSummary=7`, `None=1`, `Notice=2`, `WeeklySummary=6` |
| `LeagueMatchTab` | 8 | `Activity=1`, `AllianceRank=3`, `Compete=2`, `CrossServer=6`, `CrossServerDesert=7`, `DrawLots=4`, `LimitTimeGift=8`, `Notice=5` |
| `LeftEulerAngles` | 3 | `x=0`, `y=0`, `z=-90` |
| `LeftQuaternion` | 4 | `w=0.70710678118655`, `x=-0.0`, `y=-0.70710678118655`, `z=-0.0` |
| `LevelExploreSpecial` | 2 | `Activity=activity`, `HeroExp=exp` |
| `LevelExploreState` | 5 | `Doing=2`, `Finish=4`, `Hide=1`, `Locked=3`, `Sweep=5` |
| `LevelId` | 6 | `Car10003=10003`, `Main=10001`, `NewUserLevel=107`, `Runner=-1`, `TestLevel=2001`, `XuZhang=10002` |
| `LevelState` | 5 | `Created=2`, `Destroyed=4`, `Destroying=3`, `Init=0`, `RequestInfo=1` |
| `LightGreenColor` | 4 | `a=1`, `b=0`, `g=1`, `r=0` |
| `LineType` | 7 | `LD=1`, `LT=2`, `M=7`, `ML=5`, `MR=6`, `RD=3`, `RT=4` |
| `LoadPath` | 250 | `ActivityIconPath=Assets/Main/Sprites/ActivityIcons/%s.png`, `AvatorFolder=Assets/Main/Sprites/UI/UIChatNew/%s.png`, `BarrelPrefabPath=Assets/Main/Prefabs/Ba... |
| `LocalizationType` | 2 | `CV=2`, `Lang=1` |
| `LocationCondition` | 7 | `BackOnly=6`, `Default=3`, `FrontOnly=5`, `None=0`, `Random=4`, `Same=2`, `Self=1` |
| `LocationType` | 3 | `Back=2`, `Front=1`, `None=0` |
| `Lock_Color` | 4 | `a=1`, `b=0.31764705882353`, `g=0.4156862745098`, `r=1.0` |
| `LodArray` | 11 | `0=0`, `1=150`, `10=7001`, `2=240`, `3=500`, `4=800`, `5=1200`, `6=2200` *(+3 more)* |
| `LodType` | 60 | `AllianceBoss=10101`, `CityLabel=5001`, `Custom=1`, `Desert=5003`, `DetectEvent_WorldMonster=2100`, `DisPatchTask=2001`, `DisPatchTaskIdle=5042`, `Explore=20... |
| `LoginErrorCode` | 25 | `ERROR_BANID=4`, `ERROR_CONNECT=error connect error`, `ERROR_CONN_LOST=error connect lost`, `ERROR_DATA=E104`, `ERROR_DEVICEBLACK=44`, `ERROR_DOWNLOAD_UPDATE... |
| `LoginErrorMessage` | 31 | `ERROR_ACCOUNT_ERR=ERROR_ACCOUNT_ERR`, `ERROR_BANID=ERROR_BANID`, `ERROR_CHECK_VERSION_FAILED=ERROR_CHECK_VERSION_FAILED`, `ERROR_CHECK_VERSION_TIMEOUT=ERROR... |
| `LookAtFocusState` | 8 | `BuildRoad=7`, `Dome=4`, `EarthOrder=3`, `FarmPlant=1`, `Formation=6`, `MoveCity=5`, `None=0`, `PlaceBuild=2` |
| `LoopListMoveType` | 3 | `Horizontal=1`, `Not=3`, `Vertical=2` |
| `LotteryClassType` | 2 | `LotteryClassType_Expert=101`, `LotteryClassType_NORMAL=100` |
| `LotteryTimeType` | 2 | `LotteryTimeType_Expert=3`, `LotteryTimeType_Normal=0` |
| `LuckyShopItemType` | 2 | `LuckyShopItemType_Item=2`, `LuckyShopItemType_Resource=1` |
| `MailChannelType` | 4 | `Mail_Channel_Chat=2`, `Mail_Channel_Fight=1`, `Mail_Channel_Self=3`, `Mail_Channel_System=0` |
| `MailCombatUnitType` | 4 | `ArmyCombatUnit=1`, `CombineCombatUnit=2`, `SimpleCombatUnit=3`, `Unknow=4` |
| `MailFightRoundReportType` | 7 | `ADD_EFFECT=6`, `COUNTER_ATTACK=2`, `DEFAULT=0`, `DO_DAMAGE=4`, `NORMAL_ATTACK=1`, `RECOVER_DAMAGE=5`, `USE_SKILL=3` |
| `MailInternalGroup` | 19 | `MAIL_IN_Activity=15`, `MAIL_IN_MAX=99`, `MAIL_IN_MyTruck=13`, `MAIL_IN_MyTruckReport=14`, `MAIL_IN_Recharge=17`, `MAIL_IN_Season=16`, `MAIL_IN_alliance=4`, ... |
| `MailIsReportType` | 5 | `BlackKnight=2`, `Destroy=4`, `ExpeditionaryDuel=3`, `None=0`, `Report=1` |
| `MailSubTitleColorNew` | 4 | `a=1`, `b=0.37254901960784`, `g=0.4`, `r=0.43529411764706` |
| `MailTimeColorNew` | 4 | `a=1`, `b=0.4078431372549`, `g=0.43921568627451`, `r=0.47450980392157` |
| `MailTitleColorNew` | 4 | `a=1`, `b=0.090196078431373`, `g=0.16470588235294`, `r=0.25098039215686` |
| `MailTitleColor_Normal` | 4 | `a=1.0`, `b=0.2078431372549`, `g=0.2078431372549`, `r=0.21960784313725` |
| `MailToggleGroupDefault` | 6 | `1=10`, `2=2`, `3=4`, `4=1`, `5=17`, `6=5` |
| `MailToggleGroupTruck` | 2 | `1=13`, `2=14` |
| `MailToggleName` | 8 | `1=310002`, `10=310101`, `13=469017`, `14=469018`, `17=450335`, `2=150093`, `4=390002`, `5=310102` |
| `MailType` | 180 | `ALLIANCE_BOSS_BEAR=149`, `ALLIANCE_BOSS_BEAR_RANK=151`, `ALLIANCE_BOSS_BEAR_RESERVE_R4=153`, `ALLIANCE_BOSS_BEAR_RESERVE_R5=152`, `ALLIANCE_BOSS_BEAR_REWARD... |
| `MainBuildOrder` | 5 | `Ally=23`, `Enemy=22`, `Leader=24`, `Other=21`, `Self=25` |
| `MainBuildTimelineOffset` | 3 | `x=0`, `y=0`, `z=-5.85` |
| `MainViewChatBubbleType` | 17 | `AlDigTreasure=1`, `AlMove=4`, `CarnivalHighPerform=13`, `CarnivalLowPerform=12`, `CarnivalRuby=11`, `Golloes=7`, `HitTurkey=6`, `HitTurkey2=6` *(+9 more)* |
| `MarchArmsType` | 3 | `CROSS_DRAGON=2`, `Cross=1`, `Free=0` |
| `MarchAutoBackType` | 2 | `Back=1`, `NoBack=0` |
| `MarchPrefabType` | 4 | `Alliance=2`, `Camp=3`, `Other=4`, `Self=1` |
| `MarchPriorityState` | 10 | `Back=3`, `Battle=5`, `Collect=7`, `Dead=6`, `Free=1`, `Move=4`, `None=0`, `Rally=8` *(+2 more)* |
| `MarchStatus` | 30 | `ASSISTANCE=8`, `ATTACKING=2`, `BACK_HOME=4`, `BUILD_ALLIANCE_BUILDING=15`, `BUILD_WORM_HOLE=13`, `CHASING=5`, `COLLECTING=3`, `COLLECTING_ASSISTANCE=19` *(+... |
| `MarchTargetType` | 113 | `ASSISTANCE_ALLIANCE_BUILDING=45`, `ASSISTANCE_ALLIANCE_CENTER=132`, `ASSISTANCE_ALLIANCE_CITY=26`, `ASSISTANCE_BUILD=13`, `ASSISTANCE_CITY=14`, `ASSISTANCE_... |
| `MarkType` | 61 | `Alliance_10=10`, `Alliance_11=11`, `Alliance_12=12`, `Alliance_6=6`, `Alliance_7=7`, `Alliance_8=8`, `Alliance_9=9`, `Alliance_Attack=3` *(+53 more)* |
| `MasteryCdShow` | 3 | `Hour=3`, `Min=2`, `Sec=1` |
| `MasteryCdType` | 2 | `Countdown=1`, `Everyday=2` |
| `MasteryCondType` | 2 | `And=0`, `Or=1` |
| `MasteryHome` | 3 | `Battle=1`, `Build=2`, `Gather=3` |
| `MasteryHomeTitle` | 3 | `1=110718`, `2=110717`, `3=110716` |
| `MasteryNodeState` | 3 | `Hide=hide`, `Off=off`, `On=on` |
| `MasterySkill` | 17 | `AssistConstruction=2001`, `AssistMedical=2012`, `AssistScience=2004`, `Camouflage=2009`, `ChargeFlag=2006`, `ChargeMoveCity=2014`, `DegenerateRay=2008`, `Fr... |
| `MasterySkillLocation` | 5 | `ActiveSkill=1`, `None=0`, `WorldBuild=2`, `WorldDesert=3`, `WorldFormation=4` |
| `MasterySkillState` | 6 | `CD=3`, `Closed=4`, `Locked=2`, `NoUse=5`, `None=0`, `Normal=1` |
| `MasteryTipState` | 10 | `CanLearn=1`, `Closed=7`, `Maxed=2`, `NeedLv=3`, `NeedPoint=4`, `NeedPrior=5`, `NeedUsePoint=6`, `None=0` *(+2 more)* |
| `MediumFontMaterialType` | 22 | `Blue=Oswald-SemiBold Atlas BtnCommon`, `Bold=Oswald-SemiBold Atlas BtnCommon`, `BoldPack=NotoSansSC-Bold Atlas Pack`, `BoldSDF=NotoSansSC-Bold SDF`, `Gray=O... |
| `MemberAnim` | 5 | `Aim=idle`, `Attack=attack`, `Dead=dead`, `Idle=idle`, `Run=run` |
| `MemberCommand` | 5 | `AutoAttack=3`, `Move=2`, `StationAttack=4`, `Stay=1`, `Ultimate=5` |
| `MemberState` | 3 | `Dead=3`, `Move=2`, `Stay=1` |
| `MessageBallType` | 22 | `ArmyQueueFree=19`, `BagMax=23`, `BuildingComplete=16`, `BuildingUpgrade=1`, `CanGatherFarm=4`, `CanGatherPasture=6`, `ElectricityFull=15`, `EmptyFarm=3` *(+... |
| `MessageBarCostColor` | 4 | `a=1`, `b=0.6745`, `g=0.8666`, `r=1` |
| `MessageBarGetColor` | 4 | `a=1`, `b=0.6745`, `g=0.8666`, `r=1` |
| `MessageBarLackColor` | 4 | `a=1`, `b=0.1529`, `g=0.1529`, `r=0.5647` |
| `MessageBarType` | 3 | `Cost=1`, `Get=0`, `Lack=2` |
| `MigrateActState` | 4 | `Free=4`, `Invite=2`, `None=0`, `Ready=1` |
| `MigrateApplyType` | 6 | `AGREE=1`, `APPLY=0`, `MIGRATE=3`, `NONE=-1`, `OVERTIME=-2`, `REFUSE=2` |
| `MigrateConditionSetting` | 4 | `Alliance=4`, `BuildLevel=3`, `Power=2`, `Season=1` |
| `MigrateInviteType` | 5 | `APPLY=0`, `MIGRATE=2`, `NONE=-1`, `OVERTIME=-2`, `REFUSE=1` |
| `MigrateLevel` | 4 | `High=2`, `Mid=3`, `Normal=0`, `Special=1` |
| `MigrateServerType` | 3 | `Normal=1`, `Strong=0`, `Weak=2` |
| `MigrateShowItem` | 6 | `ServerName=1`, `ServerOpenTime=2`, `ServerPower=5`, `ServerPresident=6`, `ServerSeason=3`, `ServerState=4` |
| `MineCavePlunderType` | 4 | `AttackFail=4`, `AttackWin=3`, `DefenseFail=1`, `DefenseWin=2` |
| `MissileUnlockBtnTempText` | 4 | `182=5600129`, `183=5600103`, `184=470097`, `185=5600113` |
| `MissileUnlockDailyType` | 2 | `Personal=1`, `State=2` |
| `MissileUnlockDonateType` | 3 | `Diamond=2`, `Gold=1`, `None=0` |
| `MissileUnlockMainState` | 4 | `Finish=3`, `None=0`, `Notice=1`, `Ongoing=2` |
| `MissileUnlockStage` | 5 | `None=-1`, `Notice=0`, `Stage1=1`, `Stage2=2`, `Stage3=3` |
| `MissileUnlockStageNodeState` | 3 | `Doing=2`, `Finish=3`, `Lock=1` |
| `MistressChatTriggerType` | 13 | `Bubble=10`, `Chat=5`, `Date=7`, `Drink=1`, `Event=3`, `Gift=11`, `LoveLv=4`, `Next=0` *(+5 more)* |
| `MomentTextIds` | 3 | `MomentFollowSuccess=913570`, `MomentSendSuccess=913597`, `MomentUnFollowSuccess=913569` |
| `MonsterLockBubbleState` | 3 | `Pay=Pay`, `Pve=Pve`, `Unlocked=Unlocked` |
| `MonsterLockState` | 3 | `BUY=1`, `Finished=2`, `NOT_BUY=0` |
| `MonsterSpecialType` | 28 | `ActBoss=2`, `AllianceBoss=8`, `BigWorm=17`, `BlackKnight=5`, `BloodMoonMonster=30`, `BloodMoonRallyBoss=31`, `CarChipTrailBoss=29`, `ChallengeBoss=4` *(+20 ... |
| `MonsterTowerAlBossState` | 4 | `Failed=-2`, `NotSummoned=-1`, `Succeeded=1`, `Summoned=0` |
| `MonsterTowerAlChallengeState` | 3 | `isFinish=2`, `isLock=0`, `isTodo=1` |
| `MonsterType` | 5 | `Bucket=5`, `Dog=4`, `Normal=1`, `RedZombie=2`, `WorldBoss=3` |
| `MoveCityReason` | 8 | `ALLIANCE_MISSILE=7`, `Cross=6`, `Default=0`, `Fight=1`, `Free=3`, `Item=2`, `Login=4`, `Missile=5` |
| `MoveCityTipType` | 5 | `AlMoveInvite=0`, `CommonMove=1`, `LeaderInvite=3`, `RallyCheck=4`, `SystemInvite=2` |
| `MoveCrossServerType` | 3 | `Declare=5`, `MinePlunder=6`, `Volcano=10` |
| `MoveToWorldJoinAllianceType` | 2 | `Join=1`, `No=2` |
| `NationType` | 3 | `America=3`, `China=2`, `UnitedNations=1` |
| `NewMarchType` | 37 | `ACT_BOSS=9`, `ALLIANCE_BOSS=14`, `ASSEMBLY_MARCH=1`, `ASSEMBLY_MARCH_NOT_ATTACK=16`, `BLOOD_MOON_BOSS=30`, `BLOOD_MOON_MONSTER=29`, `BOSS=3`, `CAR_CHIP_TRAI... |
| `NewPositionShareType` | 3 | `AllianceAnnounce=AllianceAnnounce`, `AllianceMail=AllianceMail`, `GovernmentDecree=GovernmentDecree` |
| `NewQueueState` | 4 | `Finish=3`, `Free=0`, `Prepare=1`, `Work=2` |
| `NewQueueType` | 24 | `ArmyUpgrade=34`, `Barn=40`, `BlastMissile=111`, `BowSoldier=9`, `CarSoldier=1`, `CattleBarn=42`, `CombustionMissile=114`, `Default=0` *(+16 more)* |
| `NewRedColor` | 4 | `a=255`, `b=0.4078431372549`, `g=0.4078431372549`, `r=1.0` |
| `NewUserWorld` | 3 | `Ing=1`, `Pass=2`, `Skip=0` |
| `NextBusinessComeType` | 3 | `EARTH_ORDER=0`, `GROCERY_STORE=1`, `RESIDENT_ORDER=2` |
| `NightBaronessStateType` | 3 | `Lock=1`, `None=0`, `UnLock=2` |
| `NoSecondConfirmType` | 3 | `JoinAlliance=JoinAlliance`, `OpenMomentPost=OpenMomentPost`, `ProductReserve1=ProductReserve1` |
| `NotPlunderReason` | 6 | `CITY_PROTECT=5`, `DAILY_FULL=2`, `DEFAULT=0`, `MARCH_FULL=1`, `MOVE_CITY_BROKEN=3`, `NO_CARRY=4` |
| `NoteState` | 5 | `Approaching=1`, `Good=3`, `Miss=4`, `Normal=0`, `Perfect=2` |
| `NoticeBubbleType` | 2 | `Activity=1`, `Notice=2` |
| `NoticeCalendarIconPath` | 6 | `IceCave=Assets/Main/Sprites/UI/UIMain2.0/main_icon_notice_01.png`, `Level1CityWar=Assets/Main/Sprites/UI/UIMain2.0/main_icon_notice_04.png`, `TradePostS4=As... |
| `NoticeEquipDelays` | 2 | `UIRecruitLotteryTip=3`, `UISoliderGetTip=3` |
| `NoticeGovernmentIconPath` | 8 | `10002=Assets/Main/Sprites/UI/UIMain2.0/main_icon_notice_07.png`, `10003=Assets/Main/Sprites/UI/UIMain2.0/main_icon_notice_14.png`, `10004=Assets/Main/Sprite... |
| `NoticeTab` | 7 | `Attack=1`, `Building=4`, `DefenseWall=7`, `Hangup=6`, `Research=5`, `Scout=2`, `StaminaFull=3` |
| `NoticeTipIconPath` | 9 | `153=Assets/Main/Sprites/UI/UIMain2.0/UIMainNew/UIMain_icon_capitalwarserver.png`, `155=Assets/Main/Sprites/UI/UINewSeason/UIMain_icon_alliancewar.png`, `156... |
| `NoticeType` | 54 | `AcquireHero=9`, `ActBossClose=12`, `ActBossOpen=11`, `AlElectResult=10`, `AllianceCityBegin=14`, `CapitalBattleBegin=31`, `CapitalOccupied=30`, `ChangeOccup... |
| `NpcBubbleStayType` | 3 | `All=2`, `Time=3`, `Trigger=1` |
| `NpcTalkType` | 3 | `HeroEntrust=3`, `Left=1`, `Right=2` |
| `OfficerListConditionType` | 2 | `Condition_Hero=1`, `Condition_Server=2` |
| `OnlineSuportedLanguages` | 2 | `1=14`, `2=8` |
| `OrangeColor` | 4 | `a=1`, `b=0.12`, `g=0.44`, `r=0.63` |
| `OrangeYellowColor` | 4 | `a=1`, `b=0`, `g=0.5`, `r=1` |
| `OrderAllFinished` | 2 | `No=0`, `Yes=1` |
| `OrderItemType` | 5 | `ORDER_ITEM_TYPE_GOODS=1`, `ORDER_ITEM_TYPE_MONSTER=3`, `ORDER_ITEM_TYPE_RESOURCE=2`, `ORDER_ITEM_TYPE_RESOURCE_ITEM=0`, `ORDER_ITEM_TYPE_SPECIAL_MONSTER=4` |
| `OrderPriorShowType` | 2 | `Normal=0`, `Prior=1` |
| `OrderType` | 3 | `Earth=1`, `GROCERY_ORDER=2`, `Resident=0` |
| `OriType` | 5 | `Down=3`, `Error=4`, `Left=0`, `Right=1`, `Up=2` |
| `OtherBuildBubbleIcon` | 2 | `CommonBg=bubble_bg_unselect`, `StorageShop=bubble_icon_trading_bank2` |
| `OutResourceTypeIconName` | 5 | `0=Assets/Main/Sprites/UI/UIBuildBubble/bubble_icon_oil.png`, `1=Assets/Main/Sprites/UI/UIBuildBubble/bubble_icon_metal.png`, `11=Assets/Main/Sprites/UI/UIBu... |
| `OverlordFileRewardState` | 3 | `CanReceive=1`, `None=0`, `Received=2` |
| `OverviewToActType` | 6 | `2=21`, `3=19`, `5=25`, `6=22`, `7=16`, `8=26` |
| `PBTypeDict` | 18 | `1=.protobuf.AllianceCityPointInfo`, `10=.protobuf.ChallengeBossInfo`, `11=.protobuf.AllianceBossInfo`, `13=.protobuf.WorldPointMonster`, `14=.protobuf.Monst... |
| `PLayerInfoArrowType` | 3 | `BandAccount=2`, `ChangeName=1`, `ChangePic=3` |
| `PLayerInfoButtonType` | 15 | `Account=5`, `ActivityCenter=4`, `Alliance=8`, `Citybuff=9`, `Faq=6`, `Like=11`, `LikeHistory=13`, `MoreMessage=1` *(+7 more)* |
| `PVECamp` | 4 | `Ally=1`, `Enemy=0`, `Neutral=2`, `Self=3` |
| `PVEEnterType` | 10 | `ActivityArena=8`, `Arena3V3=7`, `Default=1`, `GM=0`, `Monopoly=6`, `PVPArena=5`, `Radar=2`, `TowerupJeepAdventure=3` *(+2 more)* |
| `PVELevelState` | 2 | `Finish=1`, `Start=2` |
| `PVEType` | 11 | `Arena3V3=7`, `Barrage=1001`, `ChristmasParkour=1005`, `Count=1003`, `FakePVP=6`, `None=-1`, `Parkour=1000`, `Preview=3` *(+3 more)* |
| `PVPType` | 2 | `2=1`, `6=2` |
| `PackTimeType` | 8 | `Always=2`, `AlwaysByWeek=6`, `AlwaysHideTime=8`, `ByTrigger=5`, `Conditional=3`, `Controlled=7`, `Periodic=9`, `Regular=1` |
| `PackageImgPath` | 5 | `CommonBg=Assets/Main/UITexture/UICommonPackageBig/CommonPackageBig_img_%s`, `PackageBg=Assets/Main/UITexture/UIPopupPackage/UIPopupPackage_%s.png`, `Package... |
| `PackageStatusIdMap` | 4 | `10000=590004`, `10001=590005`, `10002=590006`, `10003=590007` |
| `PassType` | 3 | `ALLIANCE_CITY_PASS=2`, `DEFAULT=0`, `NONE_CITY_PASS=1` |
| `PastureAdjust` | 4 | `bottom=300`, `left=500`, `right=400`, `top=400` |
| `PathPointType` | 2 | `Corner=2`, `Station=1` |
| `PayActivityRankRemindSettingKeys` | 4 | `24=LUCKY_ROLL_RANK_REMIND`, `35=DIG_RANK_REMIND`, `36=GIFT_BOX_RANK_REMIND`, `44=LUCKY_SHOP_RANK_REMIND` |
| `PermissionType` | 3 | `Accept=1`, `Refuse=3`, `Request=2` |
| `PersonalEventType` | 3 | `Daily=1`, `Kill=2`, `Permanent=3` |
| `PhonographBuffType` | 2 | `Attack=1`, `Help=2` |
| `PhonographEffectType` | 2 | `ALLIANCE=0`, `WORLD=1` |
| `PickResEffectLevel` | 3 | `High=3`, `Low=1`, `Middle=2` |
| `PinPwdStatus` | 2 | `Have=1`, `NoHave=0` |
| `PlaceBuildType` | 18 | `Build=1`, `Move=2`, `MoveCity=4`, `MoveCity_Al=5`, `MoveCity_Cmn=6`, `MoveCity_Cross=7`, `MoveCity_CrossDragon=11`, `MoveCity_CrossWonder=8` *(+10 more)* |
| `PlaceRoadFlagState` | 3 | `End=2`, `None=0`, `Start=1` |
| `PlaceRoadState` | 2 | `Build=1`, `Remove=2` |
| `PlantPosLogIndex` | 4 | `1=1106`, `2=1107`, `3=1108`, `4=1109` |
| `PlayBackEndJumpType` | 4 | `Arena=3`, `Chat=2`, `Mail=1`, `MineCave=4` |
| `PlayerAnimationName` | 18 | `Attack=atk1_kongshou`, `Build=Build`, `Cut=Cut`, `CutIdle=CutIdle`, `Dead=die`, `Dig=Dig`, `Duck=Duck`, `Idle=std_kongshou` *(+10 more)* |
| `PlayerBehavior` | 3 | `Bathe=1`, `Pee=3`, `Stool=2` |
| `PlayerDesertAttr` | 9 | `Buff=3`, `Force=7`, `ForceRank=8`, `Ground=9`, `OtherCount=2`, `ResNum=5`, `ResSpeedFlint=6`, `ResSpeedGas=4` *(+1 more)* |
| `PlayerType` | 6 | `PlayerAlliance=1`, `PlayerAllianceLeader=3`, `PlayerCamp=4`, `PlayerNone=-1`, `PlayerOther=2`, `PlayerSelf=0` |
| `PopWindowSortOrder` | 3 | `UIBuildUpUnlock=50`, `UIPhonographBuffDetail=55`, `UIPopupPackage=51` |
| `PositionType` | 3 | `PointId=3`, `Screen=2`, `World=1` |
| `PositionUnitType` | 3 | `DefaultRoad=1`, `InCityCanBuildPoint=5`, `NoBuildPoint=6` |
| `PostType` | 190 | `AllianceGiftLuckyShare=730`, `AssistanceHeroShare=656`, `CONTINUE_WIN=65`, `CarnivalPerformance=672`, `CarnivalShare=673`, `CastleAdventureHelpResult=662`, ... |
| `PresentClass` | 17 | `Manager=SlgEngine.DataCenter.Present.PresentManagerBase`, `UINoticePresentTipsCtrl=SlgEngine.UI.UIPresent.UINoticePresentTips.UINoticePresentTipsCtrlBase`, ... |
| `PresentTextIds` | 35 | `BigShowTip=400028`, `BigShowTipsDesc=799290`, `BigShowTipsDisplayTxt=912413`, `EffectDescGiftExp=900510`, `EffectDescLike=900508`, `EggDesc=900525`, `GetRew... |
| `PriorityType` | 5 | `All=0`, `Farthest=3`, `LowestHP=2`, `Nearest=1`, `Random=4` |
| `ProductResourceItemBuildingTypes` | 7 | `1=736000`, `2=737000`, `3=731000`, `4=728000`, `5=432000`, `6=813000`, `7=812000` |
| `PurchaseOrderState` | 4 | `DELETE=2`, `FINISH=3`, `LOCKED=1`, `NORMAL=0` |
| `PurchaseOrderType` | 3 | `ENERGY_ORDER=2`, `GROCERY_ORDER=1`, `PURCHASE_ORDER=0` |
| `PurpleColor32` | 4 | `a=255`, `b=240`, `g=108`, `r=167` |
| `PurpleColor32_S3` | 4 | `a=255`, `b=240`, `g=108`, `r=167` |
| `PurpleColor_Normal` | 4 | `a=1`, `b=0.9411765`, `g=0.4235294`, `r=0.654902` |
| `PurpleColor_S3` | 4 | `a=1`, `b=0.94117647058824`, `g=0.42352941176471`, `r=0.65490196078431` |
| `PushType` | 14 | `NOT_CHECK=99`, `PUSH_ACTIVITY=6`, `PUSH_ALLIANCE=5`, `PUSH_ATTACK=11`, `PUSH_CHAT=8`, `PUSH_GM=0`, `PUSH_MAIL=3`, `PUSH_QUEUE=1` *(+6 more)* |
| `PuzzleStageRewardState` | 2 | `PuzzleStageRewardState_Get=1`, `PuzzleStageRewardState_UnGet=0` |
| `PuzzleTaskState` | 3 | `PuzzleTaskState_Complete=1`, `PuzzleTaskState_Reward_Get=2`, `PuzzleTaskState_UnComplete=0` |
| `PveAtomType` | 2 | `Stone=1`, `Tree=0` |
| `PveBuffTimeType` | 2 | `Always=2`, `Time=1` |
| `PveBuffType` | 8 | `AddAttack=6`, `AttackAnim=2`, `AttackQuick=5`, `No=0`, `Player=4`, `Speed=1`, `Stun=7`, `WeaponBigger=3` |
| `PveBuildTriggerDirection` | 4 | `Bottom=1`, `Left=2`, `Right=4`, `Top=3` |
| `PveEntrance` | 28 | `Adventure=9`, `AdventureSetting=10`, `ApsTest=100`, `Arena3v3Battle=25`, `ArenaBattle=6`, `ArenaSetting=7`, `BattlePlayBack=8`, `BattlePve=16` *(+20 more)* |
| `PveExitType` | 3 | `DetectEventExitBtn=2`, `ExitBtn=1`, `TowerupExitBtn=3` |
| `PveHasUseBattleHeroType` | 5 | `Any=1`, `HeroId=2`, `HeroIdWithoutMax=4`, `HeroQuality=3`, `HeroQualityWithoutMax=5` |
| `PveLevelType` | 15 | `AdventureLevel=8`, `ArmyLevel=11`, `BarrageLevel=12`, `BattleExpLevel=5`, `BattlePlayBackLevel=7`, `FightLevel=3`, `GuideLevel=14`, `HeroExpLevel=2` *(+7 mo... |
| `PveLoadingAnimType` | 3 | `Black=1`, `Circle=3`, `Yellow=2` |
| `PveObjectSelectEffectColor` | 5 | `Blue=4`, `Green=0`, `Red=1`, `White=3`, `Yellow=2` |
| `PvePowerLackTipType` | 19 | `FirstPay=61`, `GetHeroExpBook=2014`, `GiftPackage=80`, `GiftRecommend=2013`, `HeroBeyond=60`, `HeroExpBook=53`, `HeroExpLevel=65`, `HeroExpOrBeyond=-53` *(+... |
| `PvePowerLackType` | 6 | `ArenaPve=5`, `Army=2`, `Fail=4`, `Hero=3`, `None=0`, `Power=1` |
| `PveResultShowType` | 2 | `Normal=0`, `Pass=1` |
| `PveSelectionType` | 2 | `DropReward=2`, `Trigger=1` |
| `PveShowBloodType` | 2 | `No=0`, `Show=1` |
| `PveShowSkill` | 2 | `No=1`, `Show=0` |
| `PveStatus` | 3 | `Finish=2`, `FirstStart=0`, `MultiStart=1` |
| `PveSweepType` | 2 | `No=0`, `Yes=1` |
| `PveTriggerVisibleType` | 2 | `Hide=2`, `Show=1` |
| `QualityImagePath` | 7 | `1=Assets/Main/Sprites/UI/UIPortrait/UIPortraitExplore/c_explore_truck_quality_01.png`, `10=Assets/Main/Sprites/UI/UIPortrait/UIPortraitExplore/c_explore_tru... |
| `QualityTrainBgPath` | 6 | `1=Assets/Main/UITexture/UILWRailway/lrb_chengjimaoyi_huocheN_bg.png`, `10=Assets/Main/UITexture/UILWRailway/lrb_chengjimaoyi_huocheUR_bg.png`, `2=Assets/Mai... |
| `QualityTrainBigBgPath` | 7 | `1=Assets/Main/UITexture/UILWRailway/zyf_cjmy_hui.png`, `10=Assets/Main/UITexture/UILWRailway/zyf_cjmy_cheng.png`, `2=Assets/Main/UITexture/UILWRailway/zyf_c... |
| `QualityTruckImagePath` | 7 | `1=Assets/Main/UITexture/UITextureExplore/c_texture_explore_truckmaillist_01.png`, `10=Assets/Main/UITexture/UITextureExplore/c_texture_explore_truckmaillist... |
| `QuestBubbleType` | 3 | `None=0`, `Pve=2`, `World=1` |
| `QuestDescType` | 32 | `Blueprint=18`, `Build=2`, `Building=20`, `ChangeLevel=17`, `Destroy_=19`, `Dialog1=32`, `DoGuide=23`, `Factory=5` *(+24 more)* |
| `QuestDoType` | 5 | `Build=4`, `Collect=2`, `Monster=3`, `NPC=1`, `Position=5` |
| `QuestGoType` | 98 | `AllianceHelp=17`, `AttackMonster=16`, `BuildBtn=1`, `BuildList=7`, `BuildRoad=10`, `ChangePlayerName=19`, `CollectGarbage=21`, `CollectResource=12` *(+90 mo... |
| `QuestListType` | 3 | `List1=1`, `List2=2`, `None=0` |
| `QuestShowType` | 2 | `No=0`, `Show=1` |
| `QuestType` | 8 | `Chapter=2`, `Daily=3`, `JeepAdventure=203`, `Main=1`, `PVE=9`, `PveAct=11`, `RalyyBoss=202`, `SeasonChapter=99` |
| `QuestType2` | 4 | `NpcItem=513`, `NpcTalk=503`, `WorldBossMainTask=514`, `WorldBossMainTaskScaled=515` |
| `QuestionAndAnswerType` | 2 | `Q_A_TYPE_NPC=2`, `Q_A_TYPE_NPC_ALL_RIGHT=3` |
| `QueueProductState` | 3 | `DEFAULT=0`, `PASTURE_BY_PRODUCT=2`, `PASTURE_MATURE=1` |
| `R1R5ImgPath` | 5 | `1=Assets/Main/Sprites/UI/UIAlliance/UIAlliance_icon_R1.png`, `2=Assets/Main/Sprites/UI/UIAlliance/UIAlliance_icon_R2.png`, `3=Assets/Main/Sprites/UI/UIAllia... |
| `RailwayStationState` | 6 | `CanRob=10`, `CannotRob=11`, `Disable=1`, `FirstReward=4`, `Fog=3`, `WarmUp=2` |
| `RankItemBg` | 5 | `1=Assets/Main/Sprites/UI/UIPortrait/UIPortraitCommon/c_common_RankYellowD.png`, `2=Assets/Main/Sprites/UI/UIPortrait/UIPortraitCommon/c_common_RankBlueD.png... |
| `RankType` | 24 | `Achievement=130`, `ActLeadingQuestAllianceRank=26`, `AllianceKill=1`, `AllianceOrder=6`, `AlliancePower=2`, `AllianceSeasonForce=15`, `CommanderBase=5`, `Co... |
| `RankingRangeType` | 3 | `ALLIANCE_DUEL=1`, `GLOBAL=2`, `Local=0` |
| `RaycastBits` | 6 | `ALL=31`, `Collider=1`, `Normal=2`, `Point=4`, `Rigidbody=8`, `Transform=16` |
| `RechargeType` | 3 | `Daily=2`, `KeepPay=1`, `Normal=0` |
| `RecommendShowAnimName` | 2 | `1=UIRecommendDefault`, `2=UIRecommendShow` |
| `RecommendShowAnimType` | 2 | `Default=1`, `Show=2` |
| `RecommendShowImgAnimName` | 2 | `1=UIRecommendLightDefault`, `2=UIRecommendLightShow` |
| `RecommendShowState` | 2 | `ShowBuild=1`, `ShowPanel=2` |
| `RecommendShowType` | 3 | `FarmGet=2`, `FarmPlant=1`, `FeedOstrich=3` |
| `RecordResultState` | 5 | `MICROPHONE_UNAVAILABLE=-1`, `OK=0`, `RECORD_SAVE_ERROR=-4`, `RECORD_TOO_SHORT=-2`, `RECORD_USER_CANCELED=-3` |
| `RedBtnColor` | 4 | `a=1`, `b=0.0`, `g=0.0`, `r=0.35294117647059` |
| `RedColor` | 4 | `a=1`, `b=0.2156862745098`, `g=0.26666666666667`, `r=0.83137254901961` |
| `RedColor2` | 4 | `a=1`, `b=0.27450980392157`, `g=0.4`, `r=1.0` |
| `RedColor32` | 4 | `a=255`, `b=104`, `g=104`, `r=255` |
| `RedColor32_S3` | 4 | `a=255`, `b=90`, `g=85`, `r=253` |
| `RedColor_Normal` | 4 | `a=1`, `b=0.05882353`, `g=0`, `r=1` |
| `RedColor_S3` | 4 | `a=1`, `b=0.35294117647059`, `g=0.33333333333333`, `r=0.9921568627451` |
| `RedEnvelopeType` | 16 | `ActReward=3`, `Aircraft=11`, `Build=1`, `CarnivalRuby=22`, `Chat=8`, `Egg=7`, `EndLess=14`, `Gift=2` *(+8 more)* |
| `RedPackageState` | 4 | `AlreadyGet=0`, `Cost_All=2`, `TimeOut=3`, `Valid=1` |
| `RedPackageType` | 3 | `Hero_Quality_4=2`, `Hero_Quality_7=3`, `LevelUp=1` |
| `RedPacketActType` | 2 | `RobotWars=2`, `Tyrant=1` |
| `RedPacketState` | 5 | `ALREADY_GET=0`, `COST_ALL=2`, `PREPARE_SEND=4`, `TIMEOUT=3`, `VALID=1` |
| `RedTMPColor` | 4 | `a=1`, `b=0.21176470588235`, `g=0.21176470588235`, `r=0.95294117647059` |
| `ResExchangeResItem` | 3 | `1=10001`, `2=10000`, `31=300041` |
| `ResLackGoToType` | 73 | `Activity=2015`, `AllianceHelpNoBtn=2037`, `AllianceScience=2036`, `BaubleLibraryRating=2029`, `BuildBuyItem=41`, `BuyFirstPay=9998`, `BuyGiftGroup=87`, `Buy... |
| `ResLackResTypeOrder` | 3 | `Adapt=2`, `Custom=3`, `Normal=1` |
| `ResLackType` | 16 | `CarChip=17`, `DesertNum=6`, `Equip=9`, `Favor=11`, `GarageCompon=16`, `HeroEquip=13`, `HeroExp=4`, `Item=2` *(+8 more)* |
| `ResPointType` | 2 | `Alliance=1`, `Normal=0` |
| `ResTypeToReward` | 17 | `0=0`, `1=1`, `11=19`, `12=21`, `13=36`, `14=20`, `15=5`, `17=28` *(+9 more)* |
| `ResetEulerAngles` | 3 | `x=0`, `y=0`, `z=0` |
| `ResetPosition` | 3 | `x=0`, `y=0`, `z=0` |
| `ResetScale` | 3 | `x=1`, `y=1`, `z=1` |
| `ResidentOrderState` | 3 | `CanBuy=2`, `No=0`, `Yes=1` |
| `ResourceCanNotChangeByDiamond` | 3 | `0=1`, `13=1`, `29=1` |
| `ResourceItem` | 6 | `DroneMaterialDrawing=230111`, `DroneMaterialWrench=230112`, `Metal=300041`, `PoliceInsignia=200034`, `Stone=10001`, `Wood=10000` |
| `ResourceItemMonsterJumpType` | 2 | `MonsterJumpType_Boss=2`, `MonsterJumpType_Monster=1` |
| `ResourceItemOutType` | 3 | `Farm=0`, `Food=2`, `Pasture=1` |
| `ResourceItemShowType` | 2 | `No=0`, `Show=1` |
| `ResourceItemType` | 2 | `Farming=0`, `Industry=1` |
| `ResourceLackOpenWinType` | 6 | `FurnitureLevelup=2`, `HeroEquip=4`, `HeroLevelup=1`, `ModifyCarItemAdd=3`, `SeasonLack=5`, `SeasonWorldCost=6` |
| `ResourceTabName` | 11 | `0=110352`, `1=722034`, `11=100546`, `12=100002`, `13=110353`, `14=100000`, `2=104283`, `29=180370` *(+3 more)* |
| `ResourceTabSelectImage` | 8 | `0=Assets/Main/Sprites/Resource/Oil_select.png`, `1=Assets/Main/Sprites/UI/UIDecoration2/btn_tab_shiwu2.png`, `11=Assets/Main/Sprites/Resource/Water_select.p... |
| `ResourceTabSelectImage1` | 5 | `1=Assets/Main/Sprites/UI/UIGiftPackageNew/G_ziyuanbuzu_03.png`, `12=Assets/Main/Sprites/UI/UIGiftPackageNew/G_ziyuanbuzu_04.png`, `14=Assets/Main/Sprites/UI... |
| `ResourceTabUnSelectImage` | 8 | `0=Assets/Main/Sprites/Resource/Oil_unSelect.png`, `1=Assets/Main/Sprites/UI/UIDecoration2/btn_tab_shiwu.png`, `11=Assets/Main/Sprites/Resource/Water_unSelec... |
| `ResourceTabUnSelectImage1` | 5 | `1=Assets/Main/Sprites/UI/UIGiftPackageNew/G_ziyuanbuzu_03.png`, `12=Assets/Main/Sprites/UI/UIGiftPackageNew/G_ziyuanbuzu_04.png`, `14=Assets/Main/Sprites/UI... |
| `ResourceType` | 33 | `BattlePass=22`, `BlackKnight=9001`, `DETECT_EVENT=20`, `Electricity=12`, `FLINT=13`, `FORMATION_STAMINA=21`, `FarmBox=19`, `Gold=15` *(+25 more)* |
| `ResourceTypeIconName` | 19 | `0=Assets/Main/Sprites/ItemIcons/Common_icon_shuijing.png`, `1=Assets/Main/Sprites/ItemIcons/UI_Icon_shiwu.png`, `11=Assets/Main/Sprites/UI/Common/Common_ico... |
| `ResourceTypePickUpEffectName` | 5 | `0=Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouqu_wasi.prefab`, `1=Assets/_Art_LastDay/Effect/Prefab/UI/VFX_ziyuanshouqu_shuijing.prefab`, `11=Assets/... |
| `ResourceTypeScience` | 3 | `0=751000`, `1=731000`, `11=732000` |
| `ResourceTypeTxt` | 16 | `0=100014`, `1=722034`, `1003=390967`, `15=100183`, `19=100546`, `20=100000`, `21=100002`, `28=400011` *(+8 more)* |
| `RestrictType` | 2 | `BAN=2`, `BLOCK=1` |
| `RewardFlagType` | 2 | `First_Pass=1`, `Normal=0` |
| `RewardNumControlNumType` | 3 | `Item=0`, `ResourceItem=1`, `UseGoods=2` |
| `RewardToResType` | 16 | `0=0`, `1=1`, `19=11`, `20=14`, `21=12`, `22=4`, `28=17`, `29=20` *(+8 more)* |
| `RewardType` | 69 | `ALLIANCE_DONATE=1004`, `ALLIANCE_POINT=11`, `ALLIANCE_SCIENCE_TECH_POINT=1005`, `ARM=23`, `ActFakeItem=1021`, `ActGiftBox=240010`, `BATTLE_HONOR=18`, `BATTL... |
| `RightEulerAngles` | 3 | `x=0`, `y=0`, `z=90` |
| `RightQuaternion` | 4 | `w=0.70710678118655`, `x=0.0`, `y=0.70710678118655`, `z=0.0` |
| `RoadDirectType` | 7 | `EAST_TO_WEST=3`, `HORIZONTAL=0`, `NORTH_TO_SOUTH=4`, `None=-1`, `PORTRAIT=1`, `SOUTH_TO_NORTH=5`, `WEST_TO_EAST=2` |
| `RoadPathType` | 3 | `MAIN_ROAD=2`, `NORMAL=0`, `VIADUCT=1` |
| `RoadState` | 2 | `Normal=0`, `Updating=1` |
| `RoamingBossDiscovererRelation` | 3 | `Alliance=1`, `Other=2`, `Self=0` |
| `RoamingBossRewardType` | 4 | `First=1`, `Join=4`, `Normal=2`, `Special=3` |
| `RobotSkillType` | 5 | `BUILD=1`, `DEFAULT=0`, `FACTORY=4`, `FARM=3`, `SCIENCE=2` |
| `RobotState` | 7 | `BUILD=1`, `FACTORY=4`, `FARM=3`, `FREE=0`, `PASTURE=5`, `SCIENCE=2`, `SU_Collect=6` |
| `RocketBombRewardState` | 2 | `No=0`, `Yes=1` |
| `RocketStatus` | 2 | `RocketStatus_Normal=0`, `RocketStatus_Preview=1` |
| `RomeNum` | 23 | `1=I`, `10=X`, `11=XI`, `12=XII`, `13=XIII`, `14=XIV`, `15=XV`, `16=XVI` *(+15 more)* |
| `RunBubbleType` | 2 | `Build=2`, `Collect=1` |
| `RuntimePlatform` | 17 | `Android=11`, `IPhonePlayer=8`, `LinuxEditor=16`, `LinuxPlayer=13`, `Lumin=33`, `OSXEditor=0`, `OSXPlayer=1`, `PS4=25` *(+9 more)* |
| `Runtime_Mode` | 2 | `Editor=1`, `RunTime=2` |
| `SCORE_TYPE` | 7 | `ALLIANCE_DUAL_MVP=1`, `ALLIANCE_DUAL_WIN=0`, `BOSS_DAMAGE=6`, `CROSS_ARENA_MVP=3`, `CROSS_TRAIN_WIN=4`, `DELITE_MVP=5`, `PERSON_ACT_MVP=2` |
| `SCORE_TYPE_DIALOG` | 7 | `0=510160`, `1=510161`, `2=510163`, `3=510165`, `4=510162`, `5=511325`, `6=913444` |
| `SLGCameraPosType` | 2 | `ConfigPos=2`, `FollowPlayer=1` |
| `SU_PveLevelType` | 14 | `ApsAutoLevel=7`, `AutoHeroLevel=6`, `BarrageLevel=12`, `Barrel_Detect=103`, `Barrel_Pve=102`, `BranchLevel=2`, `CountMaster=101`, `HeroLevel=3` *(+6 more)* |
| `SceneManagerSceneID` | 6 | `Barrel=5`, `Bridge=4`, `City=1`, `None=0`, `PVE=3`, `World=2` |
| `SceneType` | 4 | `City=1`, `None=0`, `PVE=3`, `World=2` |
| `ScienceColorBg` | 4 | `1=keji_bg_icondi`, `2=keji_bg_icondi`, `3=keji_bg_icondi`, `4=keji_bg_icondi` |
| `ScienceLineDirectionState` | 3 | `L=1`, `M=2`, `R=3` |
| `ScienceLineState` | 3 | `Dark=2`, `Light=3`, `No=1` |
| `ScienceNameLockColor` | 4 | `a=1`, `b=0.92`, `g=0.87`, `r=0.8` |
| `ScienceNameUnlockColor` | 4 | `a=1`, `b=1`, `g=0.7686275`, `r=0.6196079` |
| `ScienceRecommedType` | 2 | `Battle=2`, `Economy=1` |
| `ScienceResearchUseGold` | 4 | `Free=2`, `NoUseGold=0`, `Speed=3`, `UseGold=1` |
| `ScienceShowTag` | 2 | `No=0`, `Recommend=1` |
| `ScienceTab` | 6 | `AllianceBuild=104`, `AllianceDefense=103`, `AllianceDevelop=101`, `AllianceFight=102`, `Fight=2`, `Resource=1` |
| `ScienceTabShowConditionType` | 2 | `AllianceBattle=1`, `Season=2` |
| `ScienceTabState` | 4 | `CanUnlock=2`, `Lock=0`, `LockShow=3`, `UnLock=1` |
| `ScienceTabUnlockType` | 4 | `PreBuildingLevel=3`, `PreScienceLevel=2`, `PreScienceTreePro=1`, `RequireActivityId=4` |
| `ScienceType` | 2 | `Alliance=2`, `Build=1` |
| `ScoutMailTargetType` | 17 | `ALLIANCE_BUILD=ALLIANCE_BULID`, `ALLIANCE_CITY=ALLIANCE_CITY`, `ALLIANCE_FORTRESS=ALLIANCE_FORTRESS`, `ALLIANCE_TOWER=ALLIANCE_TOWER`, `BUILDING=BUILDING`, ... |
| `ScoutReportVisibleState` | 4 | `DEFAULT=0`, `DISABLE=2`, `ENABLE=1`, `NOT_MATCH=3` |
| `ScoutSettingKeys` | 3 | `1=ScoutWarning_Assistance`, `2=ScoutWarning_WorldTroop`, `3=ScoutWarning_Home` |
| `ScreenType` | 2 | `Landscape=1`, `Portrait=0` |
| `SeasonConfigId` | 11 | `BlackKnightSeasonActIds=3`, `HeroSeasonIcon=11`, `MiniMapMonsterNameId=1`, `OasisTradeCastellanIcon=10`, `RecruitIconOverride=5`, `ReinforceUIIcon=9`, `Roam... |
| `SeasonDesertCity` | 3 | `Alliance=1`, `Block=3`, `Other=2` |
| `SeasonEntranceActState` | 4 | `endAct=3`, `inAct=2`, `none=0`, `preview=1` |
| `SeasonEnum` | 5 | `Enum1=1`, `Enum2=2`, `Enum3=3`, `Enum4=4`, `Enum5=5` |
| `SeasonForceRewardPackageType` | 2 | `CRYSTAL_BOX=0`, `MONEY=1` |
| `SeasonForceRewardStatus` | 3 | `BATTLE_PASS_RECEIVED=2`, `NOT_RECEIVE=0`, `RECEIVED=1` |
| `SeasonMapType` | 2 | `Desert=1`, `Snow=2` |
| `SeasonObjectType` | 3 | `ChargeFlag=2`, `GoblinTreasure=3`, `Landmine=1` |
| `SeasonPassRewardType` | 2 | `NormalReward=0`, `SpecialReward=1` |
| `SeasonPlayType` | 5 | `DEFAULT=0`, `DESERT=1`, `DESERT_NO_CONNECT=3`, `EDEN=2`, `MONSTER=4` |
| `SeasonPlayTypeClient` | 2 | `AttackMonsterPlay=4`, `DeclareWarPlay=3` |
| `SeasonStage` | 6 | `Finished=5`, `None=0`, `Open=2`, `Preview=1`, `ToFinish=4`, `toSettle=3` |
| `SeasonType` | 5 | `ActivitySeason=4`, `BuildingSeason=3`, `MergeSeason=99`, `QuestSeason=2`, `WorldSeason=1` |
| `Season_Ground_TabType` | 3 | `Build=3`, `Force=1`, `Res=2` |
| `Season_Reward_BoxIcon` | 6 | `1=alliancegift_icon_05`, `2=alliancegift_icon_04`, `3=alliancegift_icon_03`, `4=alliancegift_icon_02`, `5=alliancegift_icon_01`, `6=alliancegift_icon_01` |
| `Season_Reward_SubDesc` | 4 | `1=511231`, `2=582006`, `3=582007`, `4=582008` |
| `Season_Reward_SubTab` | 4 | `1=361021`, `2=361022`, `3=361023`, `4=361024` |
| `Season_Reward_Tab` | 4 | `1=361021`, `2=361022`, `3=361023`, `4=361024` |
| `SegmentType` | 4 | `Diamond=3`, `Gold=2`, `None=0`, `Silver=1` |
| `SelectTextColor` | 4 | `a=1`, `b=0.37`, `g=0.15`, `r=0` |
| `SendStateType` | 3 | `FAILED=2`, `OK=0`, `PENDING=1` |
| `SerWorldMarkIconName` | 10 | `201=UIAlliance_mark_03`, `202=UIAlliance_mark_04`, `203=UIAlliance_mark_05`, `204=UIAlliance_mark_06`, `205=UIAlliance_mark_13`, `206=UIAlliance_mark_08`, `... |
| `SerWorldMarkPrefabPath` | 10 | `201=Assets/Main/Prefabs/UI/AllianceWorldMark/AllianceWorldMark_CrossWonder_01.prefab`, `202=Assets/Main/Prefabs/UI/AllianceWorldMark/AllianceWorldMark_Cross... |
| `SerWorldMarkType` | 10 | `Attack=201`, `Collect=203`, `Defend=202`, `Mark10=210`, `Mark7=207`, `Mark8=208`, `Mark9=209`, `Missile=206` *(+2 more)* |
| `ServerSeasonPlayTypes` | 4 | `Default=0`, `Desert=1`, `Eden1=2`, `Eden2=3` |
| `ServerType` | 4 | `CROSS_THRONE=10`, `DRAGON_BATTLE_FIGHT_SERVER=8`, `EDEN_SERVER=9`, `NORMAL=0` |
| `SetAttackGuideFlag` | 2 | `NoBackAndWaitResult=1`, `WaitResult=2` |
| `SettingKeys` | 250 | `ACCOUNT_LIST_DEBUG=ACCOUNT_LIST_DEBUG`, `ACCOUNT_PWD=Setting.ACCOUNT_PWD`, `ACCOUNT_SENDMIL_AGAINTIME=Setting.ACCOUNT_SENDMIL_AGAINTIME`, `ACCOUNT_STATUS=Se... |
| `SettingNoticeStatus` | 2 | `Off=0`, `On=1` |
| `SettingNoticeType` | 14 | `NOT_CHECK=99`, `PUSH_ACTIVITY=6`, `PUSH_ALLIANCE=5`, `PUSH_ATTACK=11`, `PUSH_CHAT=8`, `PUSH_GM=0`, `PUSH_MAIL=3`, `PUSH_QUEUE=1` *(+6 more)* |
| `SettingNoticeTypeSort` | 9 | `1=2`, `2=3`, `3=5`, `4=6`, `5=7`, `6=8`, `7=9`, `8=11` *(+1 more)* |
| `SettingNoticeUnlock` | 2 | `Lock=0`, `UnLock=1` |
| `SettingScreenResolutionTypeSort` | 2 | `1=31`, `2=32` |
| `SettingSetClearTypeSort` | 4 | `1=3`, `2=44`, `3=43`, `4=48` |
| `SettingSetPerformanceTypeSort` | 5 | `1=17`, `2=7`, `3=26`, `4=25`, `5=33` |
| `SettingSetPrivilegeTypeSort` | 2 | `1=38`, `2=39` |
| `SettingSetPromptTypeSort` | 9 | `1=18`, `2=47`, `3=49`, `4=59`, `5=40`, `6=50`, `7=51`, `8=52` *(+1 more)* |
| `SettingSetResolutionTypeSort` | 2 | `1=10`, `2=11` |
| `SettingSetSoundTypeSort` | 4 | `1=0`, `2=1`, `3=46`, `4=21` |
| `SettingSetType` | 50 | `Build=13`, `ChatShowVip=39`, `ClearDevice=43`, `ClearSimpleMode=48`, `DebugChooseServer=7`, `Decorations=14`, `DeleteMail=44`, `Diamond=18` *(+42 more)* |
| `SettingShowTypes` | 4 | `1=1`, `2=2`, `3=5`, `4=11` |
| `SettingType` | 68 | `Activity=42`, `AddItem=27`, `AllowTracking=19`, `ApsPVE=43`, `ArtTest=46`, `AutoAttack=41`, `Ban=7`, `ChangeId=16` *(+60 more)* |
| `SettingTypeSort` | 48 | `1=2`, `10=64`, `11=56`, `12=19`, `13=20`, `14=27`, `15=24`, `16=28` *(+40 more)* |
| `SevenAllianceCityCenterWorldPos` | 3 | `x=993`, `y=0`, `z=993` |
| `SevenAllianceCityWorldPos` | 3 | `x=1000`, `y=0`, `z=1000` |
| `SexType` | 4 | `Man=1`, `None=0`, `NotShow=3`, `Woman=2` |
| `ShareCheckType` | 4 | `AllianceAnnouncement=4`, `MailBattleReport=2`, `MailScoutResult=1`, `StorageShop=0` |
| `ShareFightMailResultState` | 3 | `Draw=2`, `Fail=0`, `Win=1` |
| `ShopType2PanelTab` | 5 | `1=3`, `14=4`, `16=5`, `2=2`, `3=1` |
| `ShowCircleType` | 2 | `No=1`, `Show=0` |
| `ShowFakePlayerFlagType` | 2 | `Hide=2`, `Show=1` |
| `ShowHeroListType` | 4 | `Own=2`, `OwnTitle=1`, `UnOwn=4`, `UnOwnTitle=3` |
| `ShowLandLockType` | 2 | `Hide=2`, `Show=1` |
| `ShowLoadMaskType` | 2 | `Hide=2`, `Show=1` |
| `ShowWorldArrowType` | 2 | `FarmFree=2`, `FarmGet=1` |
| `ShowWorldCollectPointType` | 2 | `Hide=2`, `Show=1` |
| `SkillAPType` | 2 | `Active=0`, `Passive=1` |
| `SkillCastState` | 5 | `BackSwing=4`, `Chant=3`, `Cooldown=0`, `FrontSwing=2`, `Ready=1` |
| `SkillSourceType` | 3 | `HERO=1`, `MARCH_CAR=2`, `OVERLORD=3` |
| `SkillType` | 6 | `Buff=2`, `Bullet=1`, `CityIdle=5`, `Halo=3`, `PassiveDeath=4`, `WorldZone=6` |
| `SkinPoolType` | 7 | `ChatBg=8`, `ChatTitle=9`, `Halo=5`, `HeadFrame=2`, `HeroSkin=100`, `MainCity=1`, `Title=3` |
| `SkinType` | 9 | `ACTIVITY_SKIN_1=10`, `BASE_SKIN=1`, `ChatBg=8`, `ChatTitle=9`, `FoxSkin=12`, `HALO=5`, `HEAD_SKIN=2`, `SnowManSkin=11` *(+1 more)* |
| `SkirmishFireState` | 5 | `Aim=1`, `Auto=5`, `Casting=2`, `Die=4`, `Idle=3` |
| `SkirmishMoveState` | 2 | `Path=2`, `Stay=1` |
| `SkirmishStage` | 4 | `End=4`, `Fight=3`, `Load=1`, `Opening=2` |
| `SlgActivityShowLocation` | 9 | `Easter=16`, `FoodFestival=15`, `HitMonster=12`, `HitSnowMan=13`, `Monopoly=17`, `Season=4`, `Valentines=14`, `bellowsBall=11` *(+1 more)* |
| `SlgActivitySource` | 2 | `activity=1`, `shop=2` |
| `SlgActivityStateType` | 4 | `Later=2`, `None=0`, `Now=1`, `Over=4` |
| `SlgAllianceBuildingId` | 4 | `CommandCenter=1001`, `ResearchCenter=2001`, `Shop=2002`, `Warehouse=2003` |
| `SlgAllianceFunctionType` | 40 | `AlLeaderElect=111`, `AllianceAllyMail=118`, `AllianceAnnounce=12`, `AllianceBattle=16`, `AllianceBuilding=101`, `AllianceCancelDismiss=121`, `AllianceCheck=... |
| `SlgAllianceTierNodeState` | 3 | `Current=2`, `Locked=3`, `Unlocked=1` |
| `SlgAllianceTierRewardState` | 3 | `Claimable=2`, `Claimed=3`, `Locked=1` |
| `SlgBattleType` | 66 | `ACT_ALLIANCE_MINE=-1`, `ACT_BOSS=15`, `ACT_RESOURCE=39`, `ALLIANCE_BOSS_BEAR=-1`, `ALLIANCE_BUILDING=20`, `ALLIANCE_BUILD_GUARD=24`, `ALLIANCE_CITY_GUARD=22... |
| `SlgCanyonBossState` | 3 | `Born=2`, `Dead=3`, `Hide=0` |
| `SlgDragonBossState` | 3 | `Born=2`, `Dead=3`, `Hide=0` |
| `SlgEffectAttrType` | 3 | `Flag_Add=2`, `Normal=0`, `Talent_Skill_Send=1` |
| `SlgEnumDestinationSignalType` | 10 | `Alliance=3`, `AllianceMain=-1`, `EmptyGround=1`, `EnemyBuild=4`, `EnemyMain=-1`, `EnemyMarch=7`, `My=2`, `None=0` *(+2 more)* |
| `SlgFormationBackState` | 4 | `Default=0`, `Mid=2`, `Off=1`, `On=3` |
| `SlgGiftPackType` | 11 | `ActivityTimeLimitGift=-1`, `DailLimitGift=-1`, `GraveyardGift=-1`, `HeroMonthCard=8`, `LifetimeGift=-1`, `MigrateGift=-1`, `MonthCard=5`, `PromotionPay=3` *... |
| `SlgMarchAutoBackType` | 2 | `Back=1`, `NoBack=0` |
| `SlgMarchStatus` | 35 | `ASSISTANCE=8`, `ATTACKING=2`, `BACK_HOME=4`, `BUILD_ALLIANCE_BUILDING=15`, `BUILD_LUCKY_CAT=-999`, `BUILD_MONEY_TREE=-999`, `BUILD_WORM_HOLE=13`, `CHASING=5... |
| `SlgMarchTargetType` | 156 | `ASSISTANCE_ALLIANCE_BUILDING=45`, `ASSISTANCE_ALLIANCE_CENTER=132`, `ASSISTANCE_ALLIANCE_CITY=26`, `ASSISTANCE_BUILD=13`, `ASSISTANCE_CANYON_BUILDING=904`, ... |
| `SlgMsgDefines` | 250 | `AdvAllianceNotice=adv.alliance.notice`, `AlAttrXInfo=al.attr.x.info`, `AlAttrXSkillUse=al.attr.x.skill.use`, `AlAttrXUp=al.attr.x.up`, `AlBeLeaderCheck=chec... |
| `SlgNewMarchType` | 46 | `ACT_BOSS=9`, `ALLIANCE_BOSS=14`, `ALLIANCE_BOSS_BEAR=-1`, `ASSEMBLY_MARCH=1`, `ASSEMBLY_MARCH_NOT_ATTACK=16`, `BIG_WORM=-1`, `BLOOD_MOON_BOSS=30`, `BLOOD_MO... |
| `SlgPersonalEventType` | 3 | `Daily=1`, `Kill=2`, `Permanent=3` |
| `SlgPlayerType` | 6 | `PlayerAlliance=1`, `PlayerAllianceLeader=3`, `PlayerCamp=4`, `PlayerNone=-1`, `PlayerOther=2`, `PlayerSelf=0` |
| `SlgSettingKeys` | 2 | `DefendFormationSquadUnlockAnimPrefix=DefendFormationSquadUnlockAnimPlayed_`, `DefendFormationUnlockRead=DefendFormationNewUnlockRead` |
| `SlgTableName` | 10 | `ActivityTreasureBox=activity_spin`, `ActivityTreasureBoxPara=activity_spin_para`, `AllianceAttrXLevel=alliance_attribute_x_level`, `AllianceAttrXLine=allian... |
| `SlgTodayNoSecondConfirmType` | 6 | `ActGiftBoxRemindFull=slg_ActGiftBoxRemindFull`, `ActGiftBoxRemoveBox=slg_ActGiftBoxRemoveBox`, `AllianceRecruitUseDiamond=slg_AllianceRecruitUseDiamond`, `B... |
| `SlgTroopCategory` | 10 | `AboutMissileLauncher=8`, `AttackMe=2`, `MyAlliance=10`, `MyEnemy=11`, `MySelf=1`, `None=0`, `Other=128`, `Rally=9` *(+2 more)* |
| `SlgUnlockBtnLockType` | 4 | `Hide=0`, `Lock=1`, `Normal=2`, `Show=10` |
| `SlgUnlockBtnType` | 11 | `Build=2`, `Building=7`, `CityTroop=3`, `FastBuild=5`, `Quest=1`, `Resource=4`, `Search=6`, `Tool_Goods=100` *(+3 more)* |
| `SlgVolcanoBuildingResource` | 11 | `VolcanoBuilding_CoreMineBuilding=10`, `VolcanoBuilding_DamageBuilding=7`, `VolcanoBuilding_DemolitionBuilding=9`, `VolcanoBuilding_ScoreBuilding=8`, `Volcan... |
| `SlgWelfareTagType` | 74 | `AccumulatedRecharge=-1`, `BigBuildPanelGift=-1`, `BigPanelGift=-1`, `BirthDay=-1`, `BlackFriday=-1`, `ChainPay=24`, `CherryBlossomFestRecharge=-1`, `ChipSel... |
| `SlgWorldActResourceType` | 2 | `CROSS_FIGHT_WINNER=3`, `GHOST_KING=5` |
| `SlgWorldPointType` | 49 | `ACT_RESOURCE=25`, `BLACK_LAND_RUIN=35`, `CANYON_BOSS=913`, `CANYON_BUILDING=911`, `CANYON_SECRET_KEY=912`, `CHRISTMAS_ACT_TREE=34`, `CROSS_THRONE_BUILD=-1`,... |
| `SlgWorldTroopColor` | 5 | `Blue=3`, `Green=2`, `Red=5`, `White=1`, `Yellow=4` |
| `SlgWorldTroopType` | 3 | `DinosaurRescue=2`, `NightSacrifice=3`, `Normal=1` |
| `SlotState` | 2 | `Lock=0`, `UnLock=1` |
| `SmallPeopleCardItemState` | 5 | `Back=1`, `BackWithGlow=2`, `Front=3`, `FrontAlreadyGet=5`, `FrontGet=4` |
| `SmallPeopleType` | 4 | `Build=3`, `Build_List=4`, `List=1`, `Task=2` |
| `SnowManTaskState` | 5 | `CanReceivedByThief=3`, `CanReveive=1`, `NoComplete=0`, `Received=2`, `WaitReceiveTime=4` |
| `SoldierLevelImage` | 11 | `1=UItroops_img_LV01`, `10=UItroops_img_LV10`, `11=UItroops_img_LV11`, `2=UItroops_img_LV02`, `3=UItroops_img_LV03`, `4=UItroops_img_LV04`, `5=UItroops_img_L... |
| `SoldierType` | 3 | `BowSoldier=2`, `CarSoldier=3`, `FootSoldier=1` |
| `SoundAssets` | 250 | `ActWorldBossOP=ui/ui_furylord_op`, `ActivityTab=ui/activity_tab`, `Alliance_Duel_First_Entry=ui/alliance_duel_first_entry`, `Arena3V3MainEnter=effect_arena_... |
| `SoundGround` | 15 | `Barrel=Barrel`, `BarrelSpecialSound=BarrelSpecialSound`, `Dub=Dub`, `Effect=Effect`, `Gatling=Gatling`, `Hero=Hero`, `LevelWeatherGroup=LevelWeatherGroup`, ... |
| `SoundLimitType` | 8 | `BulletCreate=3`, `BulletHit=2`, `DropGold=4`, `MAX=5`, `ReplayNew=6`, `SingleEffectMax=7`, `UnitCrash=8`, `UnitDeath=1` |
| `SpecialGuideLogType` | 13 | `DragPlantFarm=1105`, `PlaneRuinTimelineHello=1201`, `PlaneRuinTimelineJump=1112`, `PlaneRuinTimelineRuin=1202`, `PlaneRuinTimelineShow=1200`, `PlantFarmPosL... |
| `SpecialItemId` | 5 | `GoldRedPacket=242004`, `ITEM_ALLIANCE_CITY_MOVE=200005`, `ITEM_BLACK_DESERT_CITY_MOVE=200003`, `ITEM_MOVE_CITY=200002`, `ITEM_MOVE_RANDOM=200001` |
| `SpecialSettingNoticeTab` | 2 | `LocClock=-1001`, `Sdk=-1000` |
| `SpecialUnitType` | 26 | `ACT_ALLIANCE_MINE_GUARD=21`, `ACT_BOSS=8`, `ALLIANCE_BOSS=19`, `ALLIANCE_BUILD_POLICE_NPC=14`, `ALLIANCE_CITY_NPC=1`, `ALLIANCE_CITY_POLICE_NPC=13`, `ARENA_... |
| `SpeedUpType` | 2 | `Build=1`, `Science=2` |
| `SquadState` | 3 | `Exit=3`, `Move=2`, `Stay=1` |
| `StatTTType` | 23 | `BeginShowVideo=beginvideo`, `BridgeLevelFinish=bridgeLevelFinish`, `BridgeStageFail=bridgeStageFail`, `BridgeStageFinish=bridgeStageFinish`, `BridgeStageRes... |
| `StationBuildId` | 4 | `1=400000`, `2=417000`, `3=701000`, `4=710000` |
| `StationIdList` | 4 | `1=1`, `2=3`, `3=4`, `4=2` |
| `SteamLanguageToPay` | 29 | `arabic=ar`, `brazilian=pt-BR`, `bulgarian=bg`, `czech=cs`, `danish=da`, `dutch=nl`, `english=en`, `finnish=fi` *(+21 more)* |
| `SteelAndRedEquipFunctionType` | 7 | `AllServerArenaCount=406`, `AllServerDispatchCount=407`, `AllServerKillZombie=403`, `AllServerRadarQuest=404`, `AllServerScienceCount=402`, `AllServerSteelGa... |
| `SteelAndRedEquipPhase` | 2 | `MythEquip=2`, `SteelEra=1` |
| `StorageShopListType` | 2 | `Alliance=1`, `World=0` |
| `StorageShopSlotState` | 4 | `Cleaning=2`, `Empty=0`, `OnSell=1`, `SoldOut=3` |
| `StoryLevelState` | 7 | `Finished=2`, `Locked=3`, `NeedChapter=5`, `NeedMainLevel=4`, `NeedQuest=6`, `None=0`, `Normal=1` |
| `StoryStageRewardState` | 2 | `Normal=0`, `Received=1` |
| `StrongKingdomStateType` | 7 | `End=6`, `Fight=4`, `Match=2`, `None=0`, `Preview=1`, `Ready=3`, `Recover=5` |
| `StrongKingdomWorldPlayerCityMark` | 5 | `Attack=3`, `Defend=4`, `Expedition=1`, `Invasion=2`, `None=0` |
| `SuccessMarchFlagType` | 2 | `No=0`, `Yes=1` |
| `SuportedCV` | 4 | `1=14`, `2=28`, `3=27`, `4=9` |
| `SuportedLanguages` | 15 | `1=14`, `10=25`, `11=9`, `12=8`, `13=26`, `14=3`, `15=50`, `2=18` *(+7 more)* |
| `SuportedLanguagesLocalName` | 18 | `13=390768`, `14=390752`, `18=390754`, `20=390756`, `25=115625`, `26=390760`, `27=390766`, `28=390758` *(+10 more)* |
| `SuportedLanguagesName` | 18 | `13=Nederlands`, `14=English`, `18=Français`, `20=Deutsch`, `25=Indonesia`, `26=Italiano`, `27=日本語`, `28=한국어` *(+10 more)* |
| `SurvivalAreaState` | 4 | `Complete=3`, `Default=0`, `Finish=1`, `Start=2` |
| `SurvivalEquipType` | 6 | `Bag=bag`, `Cloth=cloth`, `Hat=hat`, `Shoe=shoe`, `Trousers=trousers`, `Weapon=weapon` |
| `SurvivalFenceBuild` | 6 | `1=121000`, `2=123000`, `3=124000`, `4=125000`, `5=128000`, `6=129000` |
| `SurvivalGroundType` | 4 | `Floor=3`, `HideFootprint=2`, `None=0`, `Puddle=1` |
| `SurvivalItemType` | 4 | `Equip=82`, `Feed=83`, `Material=81`, `Sundries=80` |
| `SurvivalRewardType` | 2 | `Default=0`, `Rewarded=1` |
| `SweepEntryActionType` | 3 | `Notice=2`, `Open=1`, `Unavailable=3` |
| `SweepFunctionType` | 7 | `AreaExplore=5`, `BurstBoss=1`, `HeroBattle=7`, `MineContend=3`, `MonsterSweep=2`, `Radar=4`, `SurvivalTrial=6` |
| `SysAlState` | 9 | `LeaderElect=3`, `LeaderResult=4`, `MergeTime_1=5`, `MergeTime_2=6`, `Normal=-1`, `R4Elect=1`, `R4Reuslt=2`, `SignUp=0` *(+1 more)* |
| `TabNoMoveSelectColor` | 4 | `a=1`, `b=0.07843138`, `g=0.3764706`, `r=0.7176492` |
| `TabNoMoveUnSelectColor` | 4 | `a=1`, `b=0.9764706`, `g=0.6980392`, `r=0.5490196` |
| `TabSelectColor` | 4 | `a=1`, `b=0.95686274509804`, `g=0.94901960784314`, `r=0.94901960784314` |
| `TabSelectHeightVec` | 2 | `x=0`, `y=0` |
| `TabSelectShadow` | 4 | `a=1`, `b=0.050980392156863`, `g=0.03921568627451`, `r=0.031372549019608` |
| `TabUnSelectColor` | 4 | `a=1`, `b=0.81176470588235`, `g=0.78039215686275`, `r=0.75686274509804` |
| `TabUnSelectHeightVec` | 2 | `x=0`, `y=0` |
| `TableName` | 250 | `APSScienceTab=aps_science_tab`, `APS_PUSH=APS_push`, `APS_Season=aps_season`, `ActSeven=AcitivitySeven_New`, `ActivityBarter=activity_barter`, `ActivityCake... |
| `TacticalWeaponPageType` | 3 | `Basic=1`, `Equip=2`, `Skin=3` |
| `TalkTaskState` | 2 | `Finish=1`, `Start=2` |
| `TalkTaskType` | 5 | `Building_Bubble=3`, `CommonQuest_Finish=5`, `Detect=1`, `Detect_World=2`, `Trigger_Bubble=4` |
| `TalkTaskUnlockType` | 3 | `Area_Unlock=4`, `Building_LevelUp=3`, `CommonQuest_Finish=5` |
| `TankShowType` | 2 | `Back=2`, `Show=1` |
| `TaskGoBuild` | 15 | `BuyAnimal=10`, `EarthOrder=16`, `FeedAnimal=11`, `FoodFactory=5`, `GetAnimal=12`, `GetResource=17`, `GetResourceRandom=18`, `HeroGet=13` *(+7 more)* |
| `TaskGoBuild44Type` | 4 | `Gas=2`, `Metal=3`, `Monster=1`, `Water=4` |
| `TaskResourceType` | 4 | `1=0`, `2=1`, `3=11`, `4=12` |
| `TaskRewardItemType` | 4 | `DawnTask=2`, `DigAct=1`, `Monopoly=4`, `SeasonBuild=3` |
| `TaskState` | 3 | `CanReceive=1`, `NoComplete=0`, `Received=2` |
| `TaskStateOrder` | 3 | `0=2`, `1=1`, `2=3` |
| `TaskType` | 3 | `Chapter=1`, `Daily=3`, `Main=2` |
| `TeamDialogType` | 4 | `GotoBattle=2`, `Idle=3`, `Lose=4`, `Win=1` |
| `TemplateUnlockType` | 6 | `Build=0`, `Career=2`, `Mastery=5`, `MonthCard=2`, `Science=1`, `Talent=4` |
| `TextAnchor` | 9 | `LowerCenter=7`, `LowerLeft=6`, `LowerRight=8`, `MiddleCenter=4`, `MiddleLeft=3`, `MiddleRight=5`, `UpperCenter=1`, `UpperLeft=0` *(+1 more)* |
| `ThronePopupType` | 3 | `Battle=1`, `End=2`, `Preview=0` |
| `ThroneState` | 2 | `Battle=2`, `Idle=1` |
| `TipsDirection` | 4 | `Bottom=4`, `Left=1`, `Right=2`, `Top=3` |
| `ToPortraitReason` | 3 | `Accept=2`, `Self=1`, `SignActivity=3` |
| `TodayNoSecondConfirmType` | 94 | `ActCallBigBossWarning=ActCallBigBossWarning`, `ActGiftBoxRemindFull=ActGiftBoxRemindFull`, `ActGiftBoxRemoveBox=ActGiftBoxRemoveBox`, `ActivityEndAlert=acti... |
| `TouchBits` | 4 | `ALL=7`, `DeltaPosition=1`, `Position=2`, `RawPosition=4` |
| `TouchPhase` | 5 | `Began=0`, `Canceled=4`, `Ended=3`, `Moved=1`, `Stationary=2` |
| `TradePostEventType` | 5 | `TradePostBuyGoods=2`, `TradePostBuyGoodsForFriend=3`, `TradePostMadeCityLord=1`, `TradePostTax=4`, `TradePostTaxRedPacket=5` |
| `TradePostFightState` | 6 | `Fight=2`, `FightEnd=3`, `Preview=0`, `PreviewToFight=6`, `Wait=1`, `WaitToFight=5` |
| `TradePostLogType` | 3 | `TradePostFight=1`, `TradePostShopping=2`, `TradePostTaxation=3` |
| `TradePostToggleType` | 5 | `None=0`, `TradePosted=3`, `TradePostedAll=1`, `TradePostedAlliance=4`, `TradePosting=2` |
| `TradeStoreState` | 4 | `AllOpen=2`, `AllianceOpen=1`, `Replenish=0`, `SoldOut=3` |
| `TrainKeyFrameType` | 4 | `PullIn=1`, `PullOut=2`, `TurnIn=3`, `TurnOut=4` |
| `TrainPlatformState` | 4 | `NoTrain=0`, `TrainNoDriver=1`, `TrainWithDriver=2`, `TrainWithPassenger=3` |
| `TrainPreparePage` | 2 | `Driver=1`, `Passenger=2` |
| `TrainState` | 3 | `ArrivedFinal=3`, `BeforeDeparture=1`, `Travelling=2` |
| `TrainStationType` | 2 | `City=2`, `Main=1` |
| `TrainTab` | 4 | `Ally=3`, `Enemy=1`, `MAX=3`, `Mine=2` |
| `TrainType` | 3 | `ItemTruck=3`, `Train=2`, `Truck=1` |
| `TrainUIOpenType` | 2 | `Departure=2`, `Prepare=1` |
| `TranslateType` | 2 | `ChatMessage=2`, `MailInfo=1` |
| `TranslateUrlList` | 2 | `1=https://translate-lm.omnilojoapps.com/client.php`, `2=http://translate-lm.omnilojoapps.com/client.php` |
| `TreasureBoxSpinConfig` | 16 | `accelDuration=0.5`, `brightAngleRange=20`, `decelDuration=1.0`, `defaultDirection=1`, `defaultSpeed=10`, `fastSpinDuration=0.3`, `maxMaskAlpha=0.9`, `maxSca... |
| `TriggerNeedType` | 3 | `Goods=3`, `Resource=1`, `ResourceItem=2` |
| `TroopActionType` | 13 | `CITY_TROOP_ACTION_CLICK_ON_HEAD=201`, `CITY_TROOP_ACTION_COLLECT_GARBAGE=202`, `CITY_TROOP_ACTION_GROCERY_STORE_HINT=20`, `TROOP_ACTION_TYPE_ALL_FREE=7`, `T... |
| `TroopIconShowState` | 4 | `Broken=2`, `Hide=0`, `Idle=1`, `Wait=3` |
| `TroopLineWorldBlueColor` | 4 | `a=1`, `b=1`, `g=0.5843138`, `r=0.09019608` |
| `TroopLineWorldBlueColor32` | 4 | `a=255`, `b=255`, `g=149`, `r=23` |
| `TroopLineWorldGreenColor` | 4 | `a=1`, `b=0.1019608`, `g=0.9803922`, `r=0.6509804` |
| `TroopLineWorldGreenColor32` | 4 | `a=255`, `b=26`, `g=250`, `r=166` |
| `TroopLineWorldPurpleColor` | 4 | `a=1`, `b=0.9411765`, `g=0.4235294`, `r=0.654902` |
| `TroopLineWorldPurpleColor32` | 4 | `a=255`, `b=240`, `g=108`, `r=167` |
| `TroopLineWorldRedColor` | 4 | `a=1`, `b=0.05882353`, `g=0`, `r=1` |
| `TroopLineWorldRedColor32` | 4 | `a=255`, `b=104`, `g=104`, `r=255` |
| `TroopLineWorldWhiteColor` | 4 | `a=1`, `b=0.8431373`, `g=0.8431373`, `r=0.8431373` |
| `TroopLineWorldWhiteColor32` | 4 | `a=255`, `b=215`, `g=215`, `r=215` |
| `TroopLineWorldYellowColor` | 4 | `a=1`, `b=0.11372549019608`, `g=0.83137254901961`, `r=0.96470588235294` |
| `TroopLineWorldYellowColor32` | 4 | `a=255`, `b=29`, `g=212`, `r=246` |
| `TroopType` | 5 | `Inside=2`, `Outside=3`, `Redif=5`, `Total=1`, `Turret=4` |
| `TruckIndexName` | 4 | `1=469000`, `2=469001`, `3=469002`, `4=469003` |
| `TruckMailReportBG` | 7 | `1=Assets/Main/UITexture/UITextureExplore/c_texture_explore_truck_report_bg_01.png`, `10=Assets/Main/UITexture/UITextureExplore/c_texture_explore_truck_repor... |
| `TruckQualityName` | 5 | `1=469004`, `2=469005`, `3=469006`, `4=469007`, `5=469008` |
| `TruckStationState` | 5 | `Exhausted=2`, `Lock=0`, `Ready=1`, `Reward=4`, `Travelling=3` |
| `TurkeyBuildingState` | 5 | `Finish=4`, `GameOver=3`, `Hit=2`, `Idle=0`, `Warning=1` |
| `Type3v3` | 2 | `Arena=1`, `Train=2` |
| `UIAllianceCityTabType` | 5 | `Build=4`, `City=2`, `FoodFestival=5`, `Mine=1`, `Resource=3` |
| `UIArrowDirection` | 4 | `ABOVE=1`, `BELOW=2`, `LEFT=3`, `RIGHT=4` |
| `UIAssetTimeLine` | 25 | `100=Assets/_Art_LastDay/Timeline/ShouchongshengqiA_Timeline/prefab/ShouchongshengqiA_Timeline.prefab`, `101=Assets/_Art_LastDay/Timeline/Xueshoulaixi_A2_Tim... |
| `UIAssetTimeLineB` | 4 | `101=Assets/_Art_Barrel/Timeline/Xueshoulaixi_A_Timeline/prefab/Xueshoulaixi_A_Timeline.prefab`, `102=Assets/_Art_Barrel/Timeline/Xueshoulaixi_B_TimelineB/pr... |
| `UIAssetTimeLineC2B` | 2 | `90=Assets/Main/C2/Main2/Prefabs/TimeLine/C2_Nvjingchadengchang_Timeline.prefab`, `OpeningAnimation=Assets/_Art_LastDay/C2/_Art/Timeline/KCdonghua/prefab/C2_... |
| `UIAssets` | 250 | `ALVSBattlePrefabPath=Assets/Main/Prefabs/UI/ActivityCenter/UIALVSDonateSoldier/AttackStateSafeArea.prefab`, `AllianceCityTip_Fort=Assets/Main/Prefabs/UI/All... |
| `UIBagBtnType` | 5 | `Buff=2`, `Hot=0`, `Other=4`, `Resource=3`, `War=1` |
| `UIBuildDetailTabType` | 2 | `Build=1`, `Detail=2` |
| `UIBuildListBuildType` | 4 | `Build=3`, `BuildRoad=1`, `RemoveRoad=2`, `Robot=4` |
| `UIBuildListTabType` | 8 | `InBuild=1`, `Military=3`, `OutBuild=2`, `Road=0`, `Robot=10`, `SeasonBuild=4`, `SeasonRobot=11`, `WallOrFloor=5` |
| `UIBuildListTabTypeSort` | 5 | `1=10`, `2=1`, `3=2`, `4=3`, `5=0` |
| `UIBuildQueueEnterType` | 4 | `Build=1`, `None=0`, `Science=3`, `Upgrade=2` |
| `UIBuildQueueState` | 3 | `Free=1`, `None=0`, `Work=2` |
| `UIBuildQueueUnlockType` | 2 | `Buy=1`, `Upgrade=0` |
| `UIBuildTimeTextShowType` | 2 | `Des=2`, `Time=1` |
| `UICapacityTableResourceType` | 2 | `1=11`, `2=12` |
| `UICapacityTableTab` | 6 | `Farming=4`, `Hero=6`, `HeroEquip=5`, `Industry=2`, `Item=4`, `Resource=3` |
| `UIEnterDragonType` | 2 | `Close=2`, `Open=1` |
| `UIFiveStarGetEnterReason` | 2 | `NewHero=1`, `None=0` |
| `UIGiftTypeButtonType` | 2 | `Diamond=Diamond`, `Hot=Hot` |
| `UIGuideCloseType` | 2 | `Click=1`, `Time=2` |
| `UIGuideMoveArrowNeedWaitType` | 2 | `No=0`, `Yes=1` |
| `UIHeroListState` | 2 | `HeroList=0`, `Star=1` |
| `UIHeroListUpStarStarState` | 2 | `No=1`, `Yes=0` |
| `UIMainAnimType` | 5 | `AllHide=OutWithResource`, `AllShow=EnterWithResource`, `ChangeAllShow=ChangeAllShow`, `LeftRightBottomHide=OutWithoutResource`, `LeftRightBottomShow=EnterWi... |
| `UIMainBuildQueueAnimName` | 2 | `0=BuildQueueEmpty`, `1=BuildQueueFree` |
| `UIMainBuildQueueAnimState` | 2 | `Empty=0`, `Free=1` |
| `UIMainFunctionInfo` | 20 | `Activity=8`, `AllianceTaskShare=20`, `Build=12`, `ChapterTask=19`, `Chat=11`, `FastBuild=17`, `Goods=2`, `Hero=9` *(+12 more)* |
| `UIMainIconPrefab` | 27 | `EnergyBank=Assets/Main/Prefabs/UI/UIMain/UIMain_icon_EnergyBank.prefab`, `PiggyBank=Assets/Main/Prefabs/UI/UIMain/UIMain_icon_PiggyBank.prefab`, `Robot0=Ass... |
| `UIMainLeftBottomState` | 11 | `AllianceTaskShare=11`, `AllianceWar=7`, `BubbleQuest=12`, `ChapterReward=6`, `ChatAndQuest=3`, `OnlyChat=4`, `Quest=8`, `RedPacket=10` *(+3 more)* |
| `UIMainLeftBottomType` | 6 | `AllianceWar=5`, `Chat=3`, `HeroStation=6`, `Quest=2`, `WarningBall=1`, `radarAlarm=4` |
| `UIMainLeftButtonType` | 2 | `March=1`, `None=0` |
| `UIMainResourceSort` | 3 | `11=3`, `14=5`, `31=4` |
| `UIMainSavePosType` | 16 | `Activity=16`, `AllianceCompete=15`, `Build=2`, `CityTroop=3`, `FastBuild=4`, `Gold=11`, `Goods=5`, `LM_food=13` *(+8 more)* |
| `UIMainShowTextType` | 4 | `Chat=2`, `Quest=1`, `RedPacket=4`, `radarAlarm=3` |
| `UIMainTopBtnType` | 5 | `Army=Army`, `ArmyTrap=ArmyTrap`, `Gold=Gold`, `Goods=Goods`, `Stamina=Stamina` |
| `UIMainTopResourceChangeType` | 2 | `ChangeLevel=1`, `Normal=0` |
| `UIMigrateType` | 2 | `Close=2`, `Open=1` |
| `UIMovingType` | 2 | `Close=2`, `Open=1` |
| `UINoInputType` | 3 | `Close=3`, `ShowNoScene=1`, `ShowNoUI=2` |
| `UIPinInputType` | 3 | `Change=2`, `Enter=0`, `Set=1` |
| `UIPinOpenState` | 2 | `Close=2`, `Open=0` |
| `UIPveSelectBuffOrder` | 3 | `1=6`, `2=1`, `3=4` |
| `UIQuitDragonType` | 2 | `Close=2`, `Open=1` |
| `UIResourceBagBtnType` | 6 | `Build=4`, `Buy=2`, `Go=5`, `LackResMode=6`, `PickUp=3`, `Use=1` |
| `UIResourceCostState` | 2 | `Animation=2`, `Normal=1` |
| `UIScienceSortList` | 2 | `1=1`, `2=2` |
| `UIScienceTopBtnType` | 3 | `Electricity=1`, `Gold=3`, `Money=2` |
| `UISearchType` | 18 | `BloodMoonMonster=17`, `BloodMoonRallyBoss=18`, `Boss=2`, `Electricity=5`, `Food=3`, `Metal=6`, `Money=7`, `Monster=1` *(+10 more)* |
| `UISeasonGloryRuleType` | 4 | `Build=2`, `Declare=3`, `Reward=4`, `Rule=1` |
| `UISetEdenType` | 2 | `Close=2`, `Open=1` |
| `UITipDirection` | 4 | `ABOVE=1`, `BELOW=2`, `LEFT=3`, `RIGHT=4` |
| `UITrainDetailType` | 6 | `Attack=1`, `Blood=3`, `Defense=2`, `Load=5`, `Power=6`, `Speed=4` |
| `UITrainDetailTypeIcon` | 6 | `1=Assets/Main/Sprites/UI/Common/Soldier/SoldierIcons_icon_gongjili.png`, `2=Assets/Main/Sprites/UI/Common/Soldier/SoldierIcons_icon_fangyu.png`, `3=Assets/M... |
| `UITrainDetailTypeList` | 5 | `1=6`, `2=1`, `3=2`, `4=3`, `5=5` |
| `UITrainState` | 3 | `NoReason=3`, `Select=1`, `Training=2` |
| `UIWorldBuildStateOrder` | 4 | `CanPut=1`, `Max=4`, `Pre=3`, `Resource=2` |
| `UIWorldTileTopBtnImage` | 4 | `1=Assets/Main/Sprites/UI/Common/New/Common_btn_share_position.png`, `2=Assets/Main/Sprites/UI/UISearch/UISearch_btn_collect.png`, `3=Assets/Main/Sprites/UI/... |
| `UIWorldTileTopBtnSort` | 2 | `1=1`, `2=2` |
| `UIWorldTileTopBtnType` | 4 | `Book=2`, `Emoji=3`, `PackUp=4`, `Share=1` |
| `UIWorldTileUIViewFromType` | 3 | `Bauble=2`, `Build=1`, `BuildingDetailList=3` |
| `UnLock_Color` | 4 | `a=1`, `b=0.3921568627451`, `g=0.81960784313725`, `r=0.34117647058824` |
| `UnitType` | 8 | `All=15`, `Junk=4`, `Member=2`, `Neutral=32`, `None=0`, `Plot=8`, `TacticalWeapon=16`, `Zombie=1` |
| `UnitType2String` | 5 | `1=丧尸`, `16=战术武器`, `2=英雄`, `4=杂物`, `8=NPC` |
| `UnlockBtnIconPath` | 6 | `1=Assets/Main/Sprites/UI/UIMain/UIMainNew/UIMain_icon_task`, `2=Assets/Main/Sprites/UI/UIMain/UIMainNew/UIMain_btn_robot`, `3=Assets/Main/Sprites/UI/UIMain/... |
| `UnlockBtnLockType` | 4 | `Hide=0`, `Lock=1`, `Normal=2`, `Show=10` |
| `UnlockBtnType` | 11 | `Build=2`, `Building=7`, `CityTroop=3`, `FastBuild=5`, `Quest=1`, `Resource=4`, `Search=6`, `Tool_Goods=100` *(+3 more)* |
| `UnlockFogDirection` | 5 | `Down=5`, `Left=2`, `Own=1`, `Right=3`, `Top=4` |
| `UnlockWindowType` | 5 | `Activity=4`, `Building=2`, `GuideBtn=3`, `None=0`, `Product=1` |
| `UseABTestCountry` | 5 | `1=IN`, `2=CN`, `3=PH`, `4=ID`, `5=GB` |
| `UserSayCodeMap` | 15 | `ar=تم حظر الحساب`, `cn=账号被封停___*禁言*___*封号*`, `de=Konto verbannt`, `en=Account Banned`, `es=Cuenta bloqueada`, `fr=Compte bloqué`, `id=Akun Diblokir`, `it=Ac... |
| `VFXAssets` | 99 | `CrossWonderSliderEff=Assets/_Art_LastDay/Effect/Prefab/UI/UICrossWonderAct/Eff_UIControversyPanel_light.prefab`, `DailyMustBuyCellBgEff=Assets/_Art_LastDay/... |
| `VFXType` | 4 | `Normal=1`, `Shield=4`, `TimerPause=2`, `WeaponTrack=3` |
| `VSGoType` | 20 | `GoAllianceBoss=12`, `GoBagAndUseChip=18`, `GoBagAndUsePart=17`, `GoBarracksByVS=5`, `GoBuildById=19`, `GoBuildWindow=1`, `GoCrossServerKillDay=4`, `GoDetect... |
| `ValentineInteractionType` | 4 | `Feed=1`, `Hallow=2`, `None=0`, `SpecialHallow=3` |
| `ValentineRewardType` | 2 | `Get=2`, `View=1` |
| `VecOne` | 3 | `x=1`, `y=1`, `z=1` |
| `VecZero` | 3 | `x=0`, `y=0`, `z=0` |
| `ViewMode` | 2 | `RPG=0`, `SLG=1` |
| `VipPayGoodState` | 4 | `CanBuy=2`, `CanGet=3`, `HasGet=4`, `Lock=1` |
| `VolcanoBoxRewardType` | 7 | `Alliance=6`, `Atk=3`, `AtkSee=1`, `Def=4`, `DefSee=2`, `None=0`, `President=5` |
| `VolcanoBuildingResource` | 11 | `VolcanoBuilding_CoreMineBuilding=10`, `VolcanoBuilding_DamageBuilding=7`, `VolcanoBuilding_DemolitionBuilding=9`, `VolcanoBuilding_ScoreBuilding=8`, `Volcan... |
| `VolcanoGuideWindowType` | 3 | `BattleDayTips=3`, `RulePreview=1`, `SetAttackPreview=2` |
| `VolcanoServerState` | 3 | `VolcanoServerState_Attack=1`, `VolcanoServerState_Defense=2`, `VolcanoServerState_None=0` |
| `VolcanoState` | 12 | `VolcanoState_AllianceAward=21`, `VolcanoState_Battle=15`, `VolcanoState_BattleEnd=17`, `VolcanoState_Communication=7`, `VolcanoState_Draw=3`, `VolcanoState_... |
| `WaitForClickType` | 2 | `Goto_Train=2`, `MarchStatus_ASSISTANCE=1` |
| `WaitMessageFinishType` | 18 | `AllianceMember=5`, `BackSceneFinish=16`, `DetectEventRewardReceive=27`, `FeedAnim=4`, `FindDesertPoint=36`, `FirstJoinAlliance=7`, `GetAnim=3`, `LevelExplor... |
| `WarningBallState` | 5 | `Cold=1`, `Free=0`, `Show=3`, `ShowOnce=4`, `Wait=2` |
| `WarningType` | 7 | `AllianceAlert=7`, `AllianceAttack=6`, `Assistance=4`, `Attack=2`, `Meteorite=1`, `ResourceAssistance=5`, `Scout=3` |
| `Wasteland_PlantState` | 3 | `ToPlant=1`, `ToReap=3`, `ToWater=2` |
| `WeatherEffectOrder` | 5 | `0=99999`, `1=2`, `2=11`, `3=3`, `4=1` |
| `WeatherEffectType` | 5 | `Frozen=2`, `Leaf=3`, `Normal=0`, `Snow=1`, `Volcano=4` |
| `WeekDayName` | 7 | `1=302789`, `2=302790`, `3=302791`, `4=302792`, `5=302793`, `6=302794`, `7=302795` |
| `WeekGiftCardType` | 7 | `Coin=3`, `Custom=7`, `Diamond=1`, `El=5`, `Exp=2`, `Food=4`, `Wood=6` |
| `WeekGiftType` | 3 | `normal=1`, `normalInScroll=3`, `select=2` |
| `WeekTabDialog` | 7 | `1=302789`, `2=302790`, `3=302791`, `4=302792`, `5=302793`, `6=302794`, `7=302795` |
| `WeekType` | 7 | `1=372307`, `2=372308`, `3=372309`, `4=372310`, `5=372311`, `6=372312`, `7=372313` |
| `WeekTypeSimple` | 7 | `1=912400`, `2=912401`, `3=912402`, `4=912403`, `5=912404`, `6=912405`, `7=912406` |
| `WelfareTagType` | 38 | `ChainPay=24`, `CreditGift=38`, `CumulativeRecharge=8`, `DailyCumulativeRecharge=26`, `DailyMustBuy=102`, `DailyPackage=19`, `DailyPackage1=103`, `EnergyBank... |
| `White1Color` | 4 | `a=1`, `b=0.91764705882353`, `g=0.96470588235294`, `r=1.0` |
| `WhiteColor` | 4 | `a=1`, `b=1`, `g=1`, `r=1` |
| `WhiteColor32` | 4 | `a=255`, `b=215`, `g=215`, `r=215` |
| `WhiteColor32_S3` | 4 | `a=255`, `b=255`, `g=255`, `r=255` |
| `WhiteColor_Normal` | 4 | `a=1`, `b=0.8431373`, `g=0.8431373`, `r=0.8431373` |
| `WhiteColor_S3` | 4 | `a=1`, `b=1`, `g=1`, `r=1` |
| `WhiteFogColor` | 4 | `a=1`, `b=1`, `g=1`, `r=1` |
| `WorldActResourceType` | 2 | `CROSS_FIGHT_WINNER=3`, `GHOST_KING=5` |
| `WorldBlackTileBtnType` | 6 | `Attack=1`, `Command=6`, `Mastery=5`, `MoveCity=2`, `Rally=3`, `SeasonBuild=4` |
| `WorldBlackTileGuideBtnType` | 7 | `Attack=1`, `Command=6`, `Mastery=5`, `MoveCity=2`, `None=0`, `Rally=3`, `SeasonBuild=4` |
| `WorldBlueColor` | 4 | `a=1`, `b=0.949`, `g=0.768627`, `r=0.3294` |
| `WorldBlueColor32` | 4 | `a=255`, `b=242`, `g=196`, `r=84` |
| `WorldBuildTopBubbleType` | 3 | `HelperDetect=1`, `None=0`, `NpcCity=2` |
| `WorldCityType` | 3 | `AllianceCity=0`, `AlliancePass=1`, `StrongHold=2` |
| `WorldDonateBuildType` | 4 | `MissileUnlockForge=4`, `PrayTree=1`, `SacredGhostKing=3`, `SacredMountain=2` |
| `WorldDownEulerAngles` | 3 | `x=0`, `y=0`, `z=0` |
| `WorldExtraType` | 22 | `DemonHunterCamp=22`, `EXTRA_ALLIANCE_BOSS=11`, `EXTRA_CHALLENGE_BOSS=10`, `EXTRA_CROSS_THRONE_BUILDING=7`, `EXTRA_DISPATCH_MISSION=8`, `EXTRA_DRAGON_BUILDIN... |
| `WorldGreenColor` | 4 | `a=1`, `b=0.19215`, `g=0.97`, `r=0.71` |
| `WorldGreenColor32` | 4 | `a=255`, `b=49`, `g=248`, `r=181` |
| `WorldLeftEulerAngles` | 3 | `x=0`, `y=90`, `z=0` |
| `WorldMarchBtnTypeImage` | 11 | `1=uibuild_btn_info_des`, `16=common_btn_MarchAttack`, `2=uibuild_btn_station`, `2.5=uibuild_btn_return_immediately`, `3=icon_emote`, `4=uibuild_btn_return`,... |
| `WorldMarchBtnTypeName` | 11 | `1=100092`, `16=5790001`, `2=400069`, `2.5=111301`, `3=493013`, `4=300520`, `5=300038`, `6=100150` *(+3 more)* |
| `WorldMarchEmotionCommandType` | 5 | `HideBtns=2`, `HideEmo=4`, `None=0`, `ShowBtns=1`, `ShowEmo=3` |
| `WorldMarchEmotionTargetType` | 3 | `Building=1`, `March=0`, `None=-1` |
| `WorldMarchTileBtnType` | 17 | `March_AssistTrain=11`, `March_Attack=6`, `March_AttackTrain=13`, `March_AutoAttack=16`, `March_Callback=4`, `March_Emotion=3`, `March_Operate=9`, `March_Qui... |
| `WorldPointBtnName` | 159 | `-1=100092`, `-2=320557`, `-3=100092`, `-4=900162`, `0.9=390040`, `1=100150`, `1.5=100150`, `10=300037` *(+151 more)* |
| `WorldPointBtnSortType` | 153 | `-1=-1`, `-2=-2`, `-3=-3`, `-4=936`, `0=0`, `0.9=1115`, `1=10`, `1.5=340` *(+145 more)* |
| `WorldPointBtnType` | 176 | `ALVSDonateSoldier=63`, `ActDinosaurBoss=161`, `AllianceBossAllianceReward=91.9`, `AllianceBossRank=66`, `AllianceBossReward=93`, `AllianceBossViewOpen=92.1`... |
| `WorldPointBtnTypeImage` | 174 | `-1=uibuild_btn_info_des`, `-2=uibuild_btn_skin`, `-3=uibuild_btn_info_des`, `-4=uibuild_btn_outfire`, `0.9=uibuild_btn_bossRank`, `1=uibuild_btn_attack`, `1... |
| `WorldPointLodType` | 3 | `Monster=1`, `Resource=2`, `SeasonRes=3` |
| `WorldPointType` | 37 | `ACT_RESOURCE=25`, `BLACK_LAND_RUIN=35`, `CHRISTMAS_ACT_TREE=34`, `DETECT_EVENT_PVE=14`, `DRAGON_BOSS=27`, `DRAGON_BUILDING=18`, `DemonHunterCamp=36`, `Detec... |
| `WorldPointUIType` | 61 | `ActBoss=15`, `ActResource=35`, `AllianceBoss=25`, `AllianceBuild=23`, `AllianceCollectPoint=14`, `AllianceMine=21`, `BloodMoonBoss=54`, `BloodMoonMonster=53... |
| `WorldPurpleColor` | 4 | `a=1`, `b=0.94117`, `g=0.42352`, `r=0.65098` |
| `WorldPurpleColor32` | 4 | `a=255`, `b=240`, `g=108`, `r=167` |
| `WorldRedColor` | 4 | `a=1`, `b=0.49411764705882`, `g=0.49411764705882`, `r=0.99607843137255` |
| `WorldRedColor32` | 4 | `a=255`, `b=77`, `g=81`, `r=252` |
| `WorldRightEulerAngles` | 3 | `x=0`, `y=-90`, `z=0` |
| `WorldSeasonBuild` | 14 | `741000=1`, `742000=2`, `743000=3`, `744000=4`, `745000=5`, `746000=6`, `747000=7`, `748000=8` *(+6 more)* |
| `WorldSeasonType` | 5 | `Desert=1`, `Dinosaur=3`, `Night=4`, `Snow=2`, `Start=0` |
| `WorldTileBtnTypName` | 93 | `1=860102`, `10=860110`, `1000=100091`, `1001=100092`, `1002=110126`, `1003=821076`, `1004=899039`, `1005=900637` *(+85 more)* |
| `WorldTileBtnType` | 110 | `ARMY=44`, `ActivityTrain=188`, `AllianceBattle=41`, `AllianceEntrance=40`, `AllianceResSupport=39`, `AssistanceSeasonBuild=3`, `Barrel_Pve=186`, `BaubleChan... |
| `WorldTileBtnTypeImage` | 106 | `1=uibuild_btn_repair`, `10=uibuild_btn_science`, `1000=uibuild_btn_up`, `1001=uibuild_btn_info_des`, `1002=uibuild_btn_refresh`, `1003=uibuild_btn_fashion`,... |
| `WorldTrackDeltaPosition` | 3 | `x=0`, `y=0`, `z=6` |
| `WorldTroopColor` | 5 | `Blue=3`, `Green=2`, `Red=5`, `White=1`, `Yellow=4` |
| `WorldTroopType` | 3 | `DinosaurRescue=2`, `NightSacrifice=3`, `Normal=1` |
| `WorldType` | 2 | `Dragon=1`, `Normal=0` |
| `WorldUIEuler` | 3 | `x=30`, `y=0`, `z=0` |
| `WorldUIScale` | 3 | `x=0.01`, `y=0.01`, `z=0.01` |
| `WorldUpEulerAngles` | 3 | `x=0`, `y=180`, `z=0` |
| `WorldWhiteColor` | 4 | `a=1`, `b=0.972549`, `g=1`, `r=0.99215` |
| `WorldWhiteColor32` | 4 | `a=255`, `b=248`, `g=255`, `r=253` |
| `WorldYellowColor` | 4 | `a=1`, `b=0.1529`, `g=0.5215`, `r=1` |
| `WorldYellowColor32` | 4 | `a=255`, `b=39`, `g=133`, `r=255` |
| `YellowBtnColor` | 4 | `a=1`, `b=0.0`, `g=0.094117647058824`, `r=0.35294117647059` |
| `YellowBtnShadowGrayColor` | 4 | `a=1`, `b=0.70196078431373`, `g=0.70196078431373`, `r=0.70196078431373` |
| `YellowBtnShadowLightColor` | 4 | `a=1`, `b=0.64313725490196`, `g=0.88235294117647`, `r=0.9921568627451` |
| `YellowColor` | 4 | `a=1`, `b=0`, `g=0.909`, `r=1` |
| `YellowColor32` | 4 | `a=255`, `b=20`, `g=133`, `r=255` |
| `YellowColor32_S3` | 4 | `a=255`, `b=0`, `g=191`, `r=255` |
| `YellowColor_Normal` | 4 | `a=1`, `b=0.07843138`, `g=0.5215687`, `r=1` |
| `YellowColor_S3` | 4 | `a=1`, `b=0`, `g=0.74901960784314`, `r=1` |
| `YellowTMPColor` | 4 | `a=1`, `b=0`, `g=0.094`, `r=0.352` |
| `YellowTradePostColor` | 4 | `a=1`, `b=0.69019607843137`, `g=0.95294117647059`, `r=1.0` |
| `ZombieAnim` | 12 | `Attack=attack`, `Born=born`, `Dead=dead`, `Dead_Fire=dead_fire`, `DropShield=drop_shield`, `Hurt=hurt`, `Idle=idle`, `Run=run` *(+4 more)* |
| `ZombieState` | 14 | `Attack=3`, `Born=0`, `DefenseRun=7`, `Die=4`, `DropShield=8`, `HardControl=10`, `Hurt=5`, `Idle=1` *(+6 more)* |
| `description1_color` | 4 | `a=1`, `b=0.81176470588235`, `g=0.78039215686275`, `r=0.75686274509804` |
| `eMailDetailActionType` | 10 | `ADD_ANGER=8`, `ADD_EFFECT=6`, `ADD_MARKER=12`, `ATTACK=1`, `COUNTER_ATTACK=2`, `DEFAULT=0`, `RECOVER_DAMAGE=5`, `SHIELD=4` *(+2 more)* |
| `eMailDetailItemType` | 5 | `Content=3`, `Title_Other=2`, `Title_Result=4`, `Title_Self=1`, `Title_Summary=0` |
| `eMailDetailTroopSide` | 2 | `Other=1`, `Self=0` |
| `eMailDetailTxtColor` | 3 | `End=</color>`, `Green_Start=<color=#228B22>`, `Red_Start=<color=#CD2626>` |
| `eMailSoldierAttr` | 6 | `Cure=cure`, `Dead=dead`, `Injured=injured`, `Lost=lost`, `Total=total`, `Wounded=wounded` |
| `effects` | 2 | `35000=30`, `35004=30` |
