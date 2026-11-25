# 00: HeinZ Task-to-Engine Playbooks & Active Fix Dossiers

> **Generated:** `2026-11-23 11:43:28 UTC` | **Refreshed:** `2026-11-23 (M3 Sync - 29 Stage Tasks / 31 TASK_ORDER / 32 TASK_REGISTRY)` | **Purpose:** Instant single-page jump table connecting EVERY HeinZ 5-Stage task straight to its `bot actions.py` lines, Last Z `DataCenter` managers, `MsgDefines` wire packets, XML tables, and Domain Quick-Card.

## 1. 5-Stage Sequential State Machine - Complete Task-to-Engine Map

### Stage 1: War Safety & Emergency Shields (`stage_1_war_safety` | cooldown=0.0s | pacing=0.6s)
| Task Key | Domain Card | `tools/bot actions.py` Function & Lines | `DataCenter` Managers Used | `MsgDefines` Packets Used |
|---|---|---|---|---|
| `war_safety` | [`core_engine.md`](domains/core_engine.md) | `run_war_safety` (`L8645-L8802`) | AllianceAlertDataManager, ItemData, ItemTemplateManager, Radar... | ItemUse |
| `rf_hq_under_attack` | [`buildings_city.md`](domains/buildings_city.md) | `run_war_safety` (`L8645-L8802`) | AllianceAlertDataManager, ItemData, ItemTemplateManager, Radar... | ItemUse |

### Stage 2: Casualty Recovery & Hospital (`stage_2_casualty_recovery` | cooldown=15.0s | pacing=0.6s)
| Task Key | Domain Card | `tools/bot actions.py` Function & Lines | `DataCenter` Managers Used | `MsgDefines` Packets Used |
|---|---|---|---|---|
| `hospital_heal` | [`alliance.md`](domains/alliance.md) | `run_hospital_heal` (`L8805-L9963`) | ArmyManager, ArmyTemplateManager, HospitalManager, ItemData, Q... | HospitalCure, QueueCcdMNew |

### Stage 3: Resource Gathering & Event Mines (`stage_3_resource_gathering` | cooldown=30.0s | pacing=0.8s)
| Task Key | Domain Card | `tools/bot actions.py` Function & Lines | `DataCenter` Managers Used | `MsgDefines` Packets Used |
|---|---|---|---|---|
| `mining_event` | [`events_fullprep.md`](domains/events_fullprep.md) | `run_mining_event` (`L6164-L6675`) | ActivityListDataManager, ArmyFormationDataManager, MineCaveMan... | BeginPvpCaveFight, ClaimMineCaveReward, GetMineCaveInfo, RefreshMin... |
| `mine_melee_refresh` | [`formations_marches_world.md`](domains/formations_marches_world.md) | `action_mine_melee_refresh` (`tools/bot_mine_melee.py`) | WorldMarchDataManager, ArmyFormationDataManager | - |

### Stage 4: Base Production & Upgrades (`stage_4_base_production` | cooldown=20.0s | pacing=0.8s)
| Task Key | Domain Card | `tools/bot actions.py` Function & Lines | `DataCenter` Managers Used | `MsgDefines` Packets Used |
|---|---|---|---|---|
| `troop_training` | [`army_troops_hospital.md`](domains/army_troops_hospital.md) | `run_troop_training` (`L3427-L3976`) | ArmyManager, BuildManager, ItemData, ItemTemplateManager, Queu... | ArmyAdd, QueueCcdMNew, QueueFinish |
| `building_upgrades` | [`buildings_city.md`](domains/buildings_city.md) | `run_building_upgrades` (`L3979-L4237`) | AllianceHelpDataManager, BuildManager, BuildQueueManager, Buil... | AllianceCallHelp, FreeBuildingUpNew |
| `research_queue` | [`buildings_city.md`](domains/buildings_city.md) | `run_research_queue` (`L10207-L10334`) | QueueDataManager, ScienceManager, ScienceTemplateManager | FreeSpeedQueue, ScienceResearchNew |
| `garage_upgrades` | [`garage_vehicles.md`](domains/garage_vehicles.md) | `run_garage_upgrades` (`L13111-L13240`) | GarageComponManager, GarageRefitManager | CarComponInstallAll, CarComponUpgradeAll, GarageRefit, GarageRefitN... |
| `hero_progression` | [`heroes_skills_equip.md`](domains/heroes_skills_equip.md) | `run_hero_progression` (`L13864-L14606`) | ActPersonalArmsInfo, ActivityListDataManager, AllianceCompeteDataManager, ArmyFormationDataManager, HeroDataManager, HeroEquipManager, HeroEquipTemplateManager, HeroLevelUpTemplateManager, HeroSPEquipManager, ItemData, ItemTemplateManager (+ `_G.HeroUtils`) | HeroEquipInstall, HeroEquipPromoteUp, HeroEquipUpgrade, HeroLvBeyond, HeroLvUp, HeroRankUpgrade, HeroSPEquipBreak, HeroSPEquipUpgrade, HeroSkillUpgrade |
| `speedups` | [`items_bag_shops_vip.md`](domains/items_bag_shops_vip.md) | `run_speedups` (`L3123-L3424`) | ActPersonalArmsInfo, ActivityListDataManager, AllianceCompeteD... | BuildCcdMNew, QueueCcdMNew, QueueFinish |

### Stage 5: Alliance & Dailies (`stage_5_alliance_dailies` | cooldown=30.0s | pacing=0.5s)
| Task Key | Domain Card | `tools/bot actions.py` Function & Lines | `DataCenter` Managers Used | `MsgDefines` Packets Used |
|---|---|---|---|---|
| `auto_help` | [`core_engine.md`](domains/core_engine.md) | `run_auto_help` (`L1556-L1741`) | AllianceGiftDataManager, AllianceHelpDataManager, BuildManager... | AlHelpAll, AllianceCallHelp, AllianceGiftList |
| `alliance_daily` | [`alliance.md`](domains/alliance.md) | `run_alliance_daily` (`L9969-L10204`) | AlContributeManager, AllianceGiftDataManager, AllianceHelpData... | AlHelpAll, AlScienceDonate, AlScienceGoldDonate, AllianceGiftList, ... |
| `radar_events` | [`events_fullprep.md`](domains/events_fullprep.md) | `run_radar_events` (`L10513-L11316`) | BuildManager, DetectEventTemplateManager, FakeHelperMarchManag... | AutoFinishDetectEvent, BatchDetectEventRewardReceive, ClickCreateTr... |
| `treasure_helicopter` | [`events_fullprep.md`](domains/events_fullprep.md) | `run_treasure_helicopter` (`L1946-L2157`) | DigTreasureDataManager, WorldPointManager | GetDigTreasureReward, WorldGetDetail |
| `trucks` | [`trucks_bounties.md`](domains/trucks_bounties.md) | `run_trucks` (`L5667-L6161`) | ArmyFormationDataManager, ArmyManager, HeroDataManager, ItemDa... | CollectTrainReward, GetMyStationData |
| `bounties` | [`core_engine.md`](domains/core_engine.md) | `run_bounties` (`L4886-L5355`) | ActDispatchTaskDataManager, ActivityListDataManager, ItemData | DispatchAssist, DispatchRewardAll, DispatchStart, DispatchTaskRefresh |
| `bounty_steal` | [`trucks_bounties.md`](domains/trucks_bounties.md) | `run_bounty_steal` (`L5358-L5664`) | ActDispatchTaskDataManager, WorldPointManager | DispatchSteal |
| `arena` | [`arena_pvp.md`](domains/arena_pvp.md) | `run_arena` (`L7717-L8241`) | ArenaManager, BattleLevel, CrossArenaManager, HeroDataManager,... | GetArenaInfo, GetCrossArenaInfo, RefreshArenaChallenge, RefreshCros... |
| `hero_battlefield` | [`arena_pvp.md`](domains/arena_pvp.md) | `run_hero_battlefield` (`L7074-L7633`) | ArmyFormationDataManager, ArmyFormationManager, BattleLevel, C... | - |
| `area_exploration` | [`core_engine.md`](domains/core_engine.md) | `run_area_exploration` (`L8244-L8568`) | BattleLevel, LWBattleManager, StoryManager, TowerClimbingManager | UserStartBarrelPushBatch |
| `boomer_runs` | [`pve_exploration_bosses.md`](domains/pve_exploration_bosses.md) | `run_boomer_runs` (`L4424-L4567`) | AllianceWarDataManager, WorldPointManager | FindMonster |
| `furylord` | [`core_engine.md`](domains/core_engine.md) | `run_furylord` (`L4731-L4883`) | ActRoamingBossManager, WorldPointManager | - |
| `tyrant_event` | [`events_fullprep.md`](domains/events_fullprep.md) | `run_tyrant_event` (`L4240-L4421`) | AllianceBossManager, AllianceWarDataManager, WorldPointManager | ReceiveAllianceBossAllianceReward |
| `full_preparedness` | [`events_fullprep.md`](domains/events_fullprep.md) | `run_full_preparedness` (`L2882-L2936`) | - | - |
| `vip_store_rewards` | [`items_bag_shops_vip.md`](domains/items_bag_shops_vip.md) | `run_vip_store_rewards` (`L6681-L6816`) | CommonShopManager, VIPManager | BuyCommonShopGoods, BuyFreeWeeklyPackage |
| `free_recruits` | [`heroes_skills_equip.md`](domains/heroes_skills_equip.md) | `run_free_recruits` (`L13008-L13108`) | ItemData, ItemTemplateManager, LotteryDataManager, SmallPeople... | ItemUse, LotteryHeroCard |
| `daily_tasks_complete` | [`daily_tasks_quests.md`](domains/daily_tasks_quests.md) | `run_daily_tasks_complete` (`L12634-L13005`) | BuildManager, DailyTaskManager, WorldPointManager | FindMonster |
| `daily_claims` | [`daily_tasks_quests.md`](domains/daily_tasks_quests.md) | `run_daily_claims` (`L11319-L11816`) | AchievementManager, ActBattlePassData, ActSeasonWeekCardData, ... | AchievementRewardGet, AllClaimWeekCardReward, ClaimAllSeasonPassRew... |

> **Registry Parity Note:** `STAGE_TASK_ORDER` covers `29` stage tasks; `TASK_ORDER` (`tools/bot actions.py:L88-L120`) adds `auto_gather` and `alliance_boss_mine` (`31` total), and `TASK_REGISTRY` (`L14859-L14892`) adds `dismiss_popups` (`32` total).

## 2. Resolved & Verified Dossiers for All 9 Bot Fixes

> All 9 issues below were resolved against Megamind-verified Last Z symbols and verified by `test_all_9_queued_bot_fixes_verified` (`96/96` baseline tests passing).

| # | Issue | Status | Resolution Implemented |
|---:|---|---|---|
| **1** | **Formation Starvation (`mine_melee_refresh` eating squads)** | **FIXED** | Reordered Stage 3 (`mining_event` before `mine_melee_refresh`) + added `_compute_effective_gather_reserve()` in `tools/multi client bot.py` reserving `>= 1` squad when downstream march tasks are enabled. |
| **2** | **Off-Theme Speedup Spending (`Age of Science` spending Build/Train)** | **FIXED** | Added `_resolve_theme_speedup_categories()` in `tools/bot actions.py` intersecting configured categories with active Full Preparedness / Alliance Duel theme (`run_speedups`). |
| **3** | **Daily Task `1000052` ("Like 3 different Posts") returning `available=0`** | **FIXED** | Upgraded `_do_daily_social_likes()` to collect from `GetChatMomentRecommendsList`, `GetChatMomentList`, `GetFriendMomentsInfo`, and trigger `ResetChatMomentListRequestState` + `SendGetChatMomentList` + `SendGetMomentList` on empty caches. |
| **4** | **Battle Auto-Skip Hardening (Regional Exploration / Hero Battlefield)** | **FIXED** | Hardened `_lua_trigger_pve_skip_snippet()` with `PveActorMgr1` & `CarBattlePveManager:SkipLevel()` fallbacks while keeping exact `startPlay` + `ShowResult(true)` -> `ForceShowResultFlag()` order. |
| **5** | **Intercity Trade Trucks (`trucks`) leaving `remaining_slots=1`** | **FIXED** | Added `TryGetMyStationData()` refresh on empty spare cache, `_form_has_heroes()` helper, and live `canAffordReroll` check so trucks never strand when refresh contracts = `0` and diamonds are disabled. |
| **6** | **Mod Vehicle Upgrades (`garage_upgrades`) Monday free-only vs Wrenches** | **FIXED** | Fixed `GetGarageFreeCount(1)` argument, added `GetUsedFreeCount()` + `GetCanClickUpgradeCount()` + explicit `free_refits_exhausted_wrench_guard_active` telemetry and `refit_mode`/`refit_source`. |
| **7** | **Daily Task `1000042` ("Attack Headquarters 1 times") opt-in toggle** | **FIXED** | Added safe opt-in `elif kind == "attack_hq":` handler (never breaks own Peace Shield, skips allies & shielded bases), wired `daily_tasks_complete` into `_RULE_KEYS` and the Rules modal (unchecked by default). |
| **8** | **Regional Exploration summary showing `stage=645->645` instead of `stage=645->650`** | **FIXED** | Tracked `start_order` and `end_order` / `order_after_battles` in `run_area_exploration()` and updated `_build_detail_lines("area_exploration")` to render `stage={start_order}->{end_order}`. |
| **9** | **Hero Battlefield logging `enemy=0` & benign toasts at `[WARN]`** | **FIXED** | Resolved chapter enemy power from `hero_battle` `map.power` (with `GetMapTemplateByLevelId` fallback) and added word-boundary `_classify_in_game_tip()` in `launcher/heinz_hub_web.py` so normal toasts log at `[DETAIL]`. |

## 3. Feature Dossier: Hero Progression Automation (`hero_progression`)

### 3.1 Cross-Module Wiring & Entrypoints
- **`tools/bot actions.py`**:
  - `TASK_ORDER` (`L112`, between `garage_upgrades` and `bounties`), `_build_detail_lines("hero_progression")` (`L1084-L1123`), `_probe_preparedness_phase` (`L2233-L2580`, including `tonumber(acm.rushDataDay)` fallback at `L2460-L2462`), `_HERO_EVENT_KEYWORD_PATTERNS` (`L13264-L13267`), `_is_hero_progression_event_active` (`L13270-L13296`), `_filter_hero_progression_targets` (`L13299-L13342`), `inspect_hero_progression` (`L13345-L13823`), `_VALID_HERO_MODULES` (`L13826`), `_lua_quote` (`L13829-L13839`), `_promote_core_cost_for_level` (`L13842-L13861`), `run_hero_progression` (`L13864-L14606`), `action_hero_progression` (`L14849`), `TASK_REGISTRY["hero_progression"]` (`L14883`).
- **`tools/multi client bot.py`**:
  - `STAGE_DEFINITIONS` Stage 4 (`stage_4_base_production`, `L74`), `STAGE_TASK_ORDER` (`L114-L116`), `default_config()` `shared_rules["hero_progression"]` (`L248-L272`) & `main_tasks["hero_progression"] = False` (`L284`; `farm_tasks` inherits `True` at `L286`), `_format_task_summary` (`L843-L853`).
- **`launcher/heinz_hub_web.py`**:
  - `TASK_CATALOG` (`L1429`), `_resolve_hero_progression_pids` (`L3292-L3305`), `_begin_hero_progression_lock` (`L3307-L3324`), `_end_hero_progression_lock` (`L3326-L3331`), `HubBackend._RULE_KEYS` (`L4014`), `_sanitize_hero_progression_rules` (`L5802`), `get_heroes_overview` (`L5908`), `save_hero_progression_rules` (`L6056`), `run_hero_progression_now` (`L6097`), `run_single_task` (`L7038`).
- **`launcher/web/index.html`**:
  - Dedicated `Heroes` tab (`data-view="heroes"`, `#view-heroes`) with KPI bento cards, VS Hero Day badge, Automation Control Strip, and filterable Hero Roster.

### 3.2 Verified `DataCenter` Managers & Singletons
- `DataCenter.HeroDataManager`, `DataCenter.HeroEquipManager`, `DataCenter.HeroSPEquipManager`, `DataCenter.ItemData`, `DataCenter.ItemTemplateManager`, `DataCenter.ArmyFormationDataManager`, `DataCenter.HeroLevelUpTemplateManager`, `DataCenter.HeroEquipTemplateManager`, `DataCenter.AllianceCompeteDataManager`, `DataCenter.ActPersonalArmsInfo`, `DataCenter.ActivityListDataManager`, `DataCenter.ActTimeCompeDataManager`, `_G.HeroUtils`.

### 3.3 `MsgDefines` Wire Packets (9 Packets)
| `MsgDefines` Alias | Wire Cmd | `nparams` | `sfs_puts` | Incoming `DataCenter` Handler | `EventId` | Module (`Net.Msgs.*`) |
|---|---|---:|---|---|---|---|
| `HeroRankUpgrade` | `upgrade.hero.rank` | 3 | `PutLong, PutInt` | `HeroDataManager.UpdateOneHero` | `HeroRankUpFail` | `Net.Msgs.HeroAbout.HeroRankUpgradeMessage` |
| `HeroLvUp` | `hero.exp` | 4 | `PutLong, PutUtfString, PutInt` | `HeroDataManager.UpdateOneHero` | `HeroLvUpSuccess` | `Net.Msgs.HeroAbout.HeroLvUpMessage` |
| `HeroLvBeyond` | `upgrade.hero` | 2 | `PutLong` | `HeroDataManager.UpdateOneHero` | `HeroLvUpSuccess` | `Net.Msgs.HeroAbout.HeroLvBeyondMessage` |
| `HeroSkillUpgrade` | `survival.hero.skill.upgrade` | 3 | `PutLong, PutInt` | `HeroDataManager.UpdateOneHero` | `SkillUpgradeEnd` | `Net.Msgs.HeroAbout.HeroSkillUpgradeMessage` |
| `HeroEquipInstall` | `hero.equip.install` | 3 | `PutInt, PutSFSArray` | `HeroEquipManager.HeroEquipInstallHandler` | `-` | `Net.Msgs.HeroEquip.HeroEquipInstallMessage` |
| `HeroEquipUpgrade` | `hero.equip.upgrade` | 4 | `PutLong, PutSFSArray, PutUtfString, PutInt` | `HeroEquipManager.HeroEquipUpgradeHandler` | `-` | `Net.Msgs.HeroEquip.HeroEquipUpgradeMessage` |
| `HeroEquipPromoteUp` | `hero.equip.promote.up` | 4 | `PutLong, PutSFSArray, PutInt` | `HeroEquipManager.HeroEquipPromoteHandler` | `-` | `Net.Msgs.HeroEquip.HeroEquipPromoteMessage` |
| `HeroSPEquipUpgrade` | `hero.equip.unique.upgrade` | 4 | `PutInt` | `HeroSPEquipManager.HeroEquipUpgradeHandler` | `-` | `Net.Msgs.HeroSPEquip.HeroSPEquipUpgradeMessage` |
| `HeroSPEquipBreak` | `hero.equip.unique.break` | 4 | `PutInt` | `HeroSPEquipManager.HeroEquipBreakHandler` | `-` | `Net.Msgs.HeroSPEquip.HeroSPEquipBreakMessage` |

### 3.4 XML Tables, Safety Guards & Live Verification Caveat
- **`ds_equip_promote.json` (`31` rows)**: Levels `0..22` consume Power Cores (`230109`: `100..1000`) + Zent (`cost_equips=''`). Levels `23..29` consume `1500..3000` Power Cores and `cost_equips='5;1'` (lv `23..25`), `'5;2'` (lv `26..28`), `'5;3'` (lv `29`), guarded by `use_replacement_equip=False` + Universal Equipment Material (`230126`) and `costEquipArr={}` (real gear is never foddered).
- **Default Safety Guards**: `main_tasks["hero_progression"] = False`, `only_hero_day=True` (VS Day 4 / Hero Preparedness, word-boundary `_HERO_EVENT_KEYWORD_PATTERNS` so `"Start Building"` does not match `"star"`, `vs_day in (0, 4)` label isolation), `use_universal_shards=False` (`universal_shard_reserve=50`), `allow_gear_promote=False`, `allow_sp_equip=False`, and `tonumber(...)` numeric UUID validation before `PutLong` / `PutSFSArray`.
- **Live Frida `string.dump` Caveat**: `HeroEquipUpgradeMessage.OnCreate` (`costGoods` struct array shape), `HeroSkillUpgrade` (`skillIndex` 1-based vs 0-based), and `HeroSPEquipBreak` wire serialization are statically verified against Megamind and queued for first-run live Frida `string.dump` confirmation on an attached `Survival.exe` client.
