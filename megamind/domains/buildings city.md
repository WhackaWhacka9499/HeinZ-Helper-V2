# Domain Quick-Card: Buildings & City (`buildings_city`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain buildings_city`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **8** tasks / **6** bot fns / **4** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **85** packets |
| `DataCenter` Managers & Singletons | **35** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **82** windows / **4** active HUD buttons / **51** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **21** tables / **117** enums / **110** live events / **157** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Task Key | Title | Tag |
|---|---|---|
| `area_exploration` | Area Exploration (Auto-Skip) | `HQ Solo • Auto-Skip` |
| `mining_event` | Mining Event (Mon / Tue) | `Lv7 Empty Nodes` |
| `treasure_helicopter` | Treasure Helicopter | `Map Dig` |
| `free_recruits` | Free Recruits & Safe Chests | `Timer + Drops Only` |
| `garage_upgrades` | Garage Upgrades (Monday) | `Mondays Only` |
| `full_preparedness` | Full Preparedness | `Milestone Boxes` |
| `speedups` | Smart Speedups | `Main: Free Only` |
| `trucks` | Trade Trucks (Claim + Send Gold) | `Claim + Roll Gold` |

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `_build_detail_lines` | `L775-L1186` | - | - |
| `_try_start_research` | `L2633-L2699` | ScienceResearchNew | BuildManager, ScienceManager |
| `run_troop_training` | `L3314-L3863` | ArmyAdd, QueueCcdMNew, QueueFinish | ArmyManager, BuildManager, ItemData, ItemTemplateManager, QueueData... |
| `run_research_queue` | `L10049-L10176` | FreeSpeedQueue, ScienceResearchNew | QueueDataManager, ScienceManager, ScienceTemplateManager |
| `run_radar_events` | `L10345-L11148` | AutoFinishDetectEvent, BatchDetectEventRewardReceive, ClickCreateTr... | BuildManager, DetectEventTemplateManager, FakeHelperMarchManager, F... |
| `run_daily_tasks_complete` | `L12426-L12740` | FindMonster | BuildManager, DailyTaskManager, WorldPointManager |

**Hub `action_id` Routes:** `sync_farm_builds` (L5012), `launch_all_farms` (L5031), `stop_all_farms` (L5109), `provision_farm` (L5125)

## 2. `DataCenter` Managers & Outgoing Links (35)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.BuildManager` | 256 | MsgDefines.AlBeLeaderCheck, MsgDefines.BuildCcdMNew, MsgDefine... | BUILD_IN_VIEW, BuildBoxOpenFinish, BuildRedDotRecord... | UIBuildUpUnlock, UIBuildUpgradeAddDes, UIBuildU... | TableName.Adaptive_Box, TableName.BaseUnlockBui... |
| `DataCenter.ActDragonManager` | 176 | MsgDefines.DragonActionRecord, MsgDefines.DragonActivityInfo, ... | CheckDragonMoveCity, DragonBattleHistory, DragonBatt... | UIAlCompeteBarrage, UIArrow, UIDragonHistoryScore | - |
| `DataCenter.BuildBubbleManager` | 170 | - | OverlordGrowUpItemChanged, PlayNormalBubbleAni | UIWorldTileUI | - |
| `DataCenter.HeroEquipManager` | 90 | MsgDefines.HeroEquipDecompose, MsgDefines.HeroEquipEvolution, ... | HeroEquipDecompose, HeroEquipInstall, HeroEquipMater... | UIHeroEquipEvolutionSuccess | - |
| `DataCenter.BuildPoliceInsigniaManager` | 89 | MsgDefines.FreeBuildingUpNew | SU_PoliceInsigniaBuildPack, SU_RefreshItemById | - | TableName.Init_Build |
| `DataCenter.BuildQueueManager` | 69 | - | BuildUpgradeStart, Build_Fix_Time_End, Build_Time_En... | - | TableName.Robot |
| `_G.BuildingUtils` | 68 | - | - | - | - |
| `DataCenter.ArmyManager` | 56 | MsgDefines.QueueCcdMNew, MsgDefines.QueueFinish | SoldierExchange, TrainArmyData, UnlockArmy, UpdateGold | UINoticeEquipTips, UISoliderGetTip | - |
| `DataCenter.QueueDataManager` | 55 | - | AddSpeedSuccess, DeletePastureQueue, GatherResourceI... | UIScienceTab, UISoliderGetTip, UISpeed | - |
| `DataCenter.BuildProcessControlManager` | 52 | - | GuideSaveFinish | UI_DayNight | - |
| `DataCenter.BuildTimeManager` | 49 | - | BuildFixStart, BuildPlace, RefreshBuildUpgradeEffect | UIPasture | - |
| `DataCenter.BuildUpgradeEffectManager` | 47 | - | BuildConfirmFinish, BuildObjectShowOpenBoxTimeline, ... | MainUI_SU | - |
| `DataCenter.GuideCityAnimManager` | 41 | - | GuideTimelineMarker | UITimelineJump | - |
| `DataCenter.GuideNeedLoadManager` | 34 | - | GuideTimelineMarker, NoticeMainViewUpdateMarch | - | - |
| `DataCenter.MainCityAreaDataManager` | 29 | - | LW_MainCityAreaFogUpdate, PlayBonFireAnim | - | TableName.Guide, TableName.SU_MainCityArea |
| `DataCenter.HospitalManager` | 28 | MsgDefines.QueueFinish | HospitalUpdate, UpdateGold | - | - |
| `DataCenter.ScienceManager` | 26 | MsgDefines.QueueFinish | UPDATE_SCIENCE_DATA, UpdateGold | - | TableName.EffectNumDesc |
| `DataCenter.BuildCanUpgradeEffectManager` | 21 | - | UPDATE_BUILD_DATA | - | - |
| `DataCenter.BuildTrainEffectManager` | 19 | - | TrainingArmyFinish | - | - |
| `DataCenter.CanUnlockFogManager` | 19 | MsgDefines.CityUnlockFog | UnlockFogAnim | - | - |
| `DataCenter.BuildTemplateManager` | 18 | - | - | - | TableName.Building, TableName.BuildingDes, Tabl... |
| `DataCenter.BuildIdleEffectManager` | 17 | - | BuildUpgradeStart | - | - |
| `DataCenter.BuildNameTipManager` | 16 | - | OnWorldInputDragBegin | UIWorldTileUI | - |
| `DataCenter.DefenceWallDataManager` | 16 | - | - | - | - |
| `DataCenter.CityCameraManager` | 14 | - | ChangeCameraInitZoom, OnEnterCity | - | - |
| `DataCenter.PhotoWallManager` | 14 | - | OnSurvivalHeroCollectionReward | - | - |
| `DataCenter.BuildZoneManager` | 13 | - | OpenUI | UIWorldTileUI | - |
| `DataCenter.SeasonPrologueManager` | 13 | MsgDefines.FindMainBuildInitPosition | REGET_MAIN_POSITION, UINoInput | UIVideoPlayer, UI_VideoPlayer | - |
| `DataCenter.BuildStatusManager` | 12 | - | BuildStatusUpdate | - | - |
| `DataCenter.SU_MainCityRoleTeam` | 11 | MsgDefines.SU_SaveMainCityRoleTeam | LWUpdateMainCityRoleTeam | - | - |
| `DataCenter.BuildUpgradeStockManager` | 9 | MsgDefines.UBStoreUpgrade | RefreshBuildUpgradeStock, UpdateGold | - | - |
| `DataCenter.BuildQueueTemplateManager` | 8 | - | - | - | TableName.Robot |
| `DataCenter.MainCityAreaTemplateManager` | 7 | - | - | - | TableName.SU_MainCityArea |
| `DataCenter.LoadEditorBuildManager` | 5 | - | ShowLoadEditorBuild | UILoadEditorBuild | - |
| `DataCenter.BuildQueueTalkManager` | 3 | - | - | - | - |

## 3. Key Wire Packets (85 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `back.building.collect.time` | BackBuildingCollectTime | `p=2` PutLong | BuildManager.BackBuildingCollectTimeMessageHandle | - |
| `black.land.user.city.swap.record` | BlackLandCitySwapRecord | `p=1`  | GloryCitySwapManager.OnSwapRecordResponse | - |
| `black.land.user.city.swap.req` | BlackLandCitySwapReq | `p=3` PutUtfString | GloryCitySwapManager.OnSwapReqResponse | UpdateGold |
| `black.land.user.city.swap.resp` | BlackLandCitySwapResp | `p=3` PutLong, PutInt | GloryCitySwapManager.OnSwapRespResponse | - |
| `build.ccd.m.new` | BuildCcdMNew | `p=3` PutLong, PutBool, PutUtfString | BuildManager.BuildCcdMNewHandle | - |
| `build.world.move.new` | BuildWorldMoveNew | `p=2` PutLong, PutInt | BuildManager.BuildWorldMoveNewHandle | - |
| `buy.citydef.add` | CityDefenceAdd | `p=1`  | DefenceWallDataManager.UpdateColdDownTime | UpdateGold |
| `city.pick.garbage` | CityPickGarbage | `p=2` PutLong | GuideCityManager.CityPickGarbageHandle | - |
| `city.pick.garbage.finish` | CityPickGarbageFinish | `p=2` PutLong | GuideCityManager.CityPickGarbageFinishHandle | - |
| `city.unlock.fog` | CityUnlockFog | `p=2` PutInt | GuideCityManager.isUnlockFog | OpenFogSuccess |
| `find.main.build.init.position` | FindMainBuildInitPosition | `p=2` PutInt | BuildManager.FindMainBuildInitPositionHandle | - |
| `find.monster.in.city` | FindMonsterInCity | `p=2` PutInt | CityPointDataManager.SetPointDataByUuid | END_SEARCH |
| `free.building.expend.dome` | FreeBuildingExpendDome | `p=1`  | BuildManager.FreeBuildingExpendDomeHandle | - |
| `free.building.fold.up.new` | FreeBuildingFoldUpNew | `p=2` PutLong | BuildManager.FreeBuildingFoldUpNewHandle | - |
| `free.building.place.main.building` | FreeBuildingPlaceMainBuilding | `p=2` PutInt | BuildManager.FreeBuildingPlaceMainBuildingHandle | - |
| `free.building.place.new` | FreeBuildingPlaceNew | `p=2` PutInt, PutUtfString, PutLong | BuildManager.FreeBuildingPlaceNewHandle | EnterDragonWorld |
| `free.building.replace.new` | FreeBuildingReplaceNew | `p=2` PutLong, PutInt | BuildManager.FreeBuildingReplaceNewHandle | - |
| `free.building.up.new` | FreeBuildingUpNew | `p=2` PutUtfString, PutInt, PutLong | BuildManager.FreeBuildingUpNewHandle | - |
| `free.building.upgrade.finish` | FreeBuildingUpgradeFinish | `p=2` PutLong | BuildManager.GetBuildingDataByUuid | SU_BuildGiftPackage |
| `free.building.world.move` | FreeBuildingWorldMove | `p=2` PutLong, PutInt | BuildManager.FreeBuildingReplaceNewHandle | - |
| `free.speed.queue` | FreeSpeedQueue | `p=2` PutSFSArray | QueueDataManager.FreeSpeedQueueHandle | - |
| `get.main.building.feed.reward` | ValentineGetFeedReward | `p=2` PutInt | ValentineDecorationManager.HandleGetFeedRewardMessage | - |
| `get.npc.city.info` | GetNpcCityInfo | `p=2` PutLong | NpcCityManager.HandleGetNpcCityInfo | - |
| `get.npc.city.msg` | GetNpcCityChat | `p=1`  | NpcCityManager.HandleGetNpcCityChat | - |
| `get.user.guard.army` | GetUserGuardArmy | `p=1`  | DefenceWallDataManager.UpdateGuardArmyInfo | GetPlayerPoliceStationData |
| `main.building.feed` | ValentineFeed | `p=2` PutUtfString | ValentineDecorationManager.GetCacheSkinId | UpdateGold |
| `main.building.greet` | ValentineHallow | `p=3` PutUtfString, PutInt | ValentineDecorationManager.UpdateHallowTime | - |
| `move.city.to.world` | MoveCityToWorld | `p=2` PutInt | RadarCenterDataManager.GetDetectEventData | - |
| `push.add.building` | PushAddBuilding | `p=1`  | BuildManager.PushAddBuildingHandle | - |
| `push.black.land.swap` | PushBlackLandSwap | `p=1`  | GloryCitySwapManager.OnPushSwap | - |
| `push.build.del` | PushBuildDelete | `p=1`  | BuildManager.PushBuildDeleteHandle | - |
| `push.build.fold.up` | PushBuildFoldUp | `p=2`  | BuildManager.PushBuildFoldUpHandle | - |
| `push.build.unlock.add` | PushBuildUnlockAdd | `p=1`  | BuildQueueManager.InitQueueList | - |
| `push.build.upgrade.finish` | PushBuildUpgradeFinish | `p=2`  | BuildManager.PushBuildUpgradeFinishHandle | - |
| `push.building.break.free.time` | PushBuildingBreakFreeTime | `p=1`  | BuildBreakManager.PushBuildingBreakFreeTimeHandle | - |
| `push.building.connect.status` | PushBuildingConnectStatus | `p=2`  | BuildManager.PushBuildingConnectStatusHandle | - |
| `push.building.info` | PushBuildingInfo | `p=2`  | BuildManager.GetBuildingDataByUuid | BuildUpdateRefreshView |
| `push.building.status.add` | PushBuildingStatusAdd | `p=1`  | BuildStatusManager.HandleAdd | - |
| `push.building.status.del` | PushBuildingStatusDel | `p=1`  | BuildStatusManager.HandleDel | - |
| `push.city.fight.result` | PushCityFightResult | `p=1`  | GuideCityManager.PushCityFightResultHandle | - |
| `push.city.point.refresh` | PushCityPointRefresh | `p=2`  | GuideCityManager.PushCityPointRefreshHandle | - |
| `push.defend.wall.compensate` | PushDefendWallCompensate | `p=1`  | WoundedCompensateData.UpdateData | - |
| `push.defend.wall.update` | PushDefenceWallUpdate | `p=1`  | DefenceWallDataManager.UpdateDefenceWallData | DefenceWallUpdate |
| `push.demon.hunter.quests` | PushDemonHunterQuests | `p=1`  | DemonHunterDataManager.HandlePushQuestsStatus | - |
| `push.donate.army.defence.result` | PushDonateArmyDefenceResult | `p=1`  | ActivityALVSDonateSoldierManager.OnHandlePushDonateArmyDe... | - |
| `push.dragon.player.move` | PushDragonPlayerMove | `p=1`  | BattleCommandManager.OnHandlePushPlayerMoveCityTime | - |
| `push.init.build` | PushInitBuild | `p=2`  | BuildManager.PushInitBuildHandle | - |
| `push.main.building.interactive` | PushValentineInteraction | `p=1`  | ValentineDecorationManager.HandlePushMessage | - |
| `push.npc.city.defend.change` | PushNpcCityDefendChange | `p=1`  | NpcCityManager.HandleNpcCityDefendChange | NpcCityBloodValueChange |
| `push.npc.city.new.msg` | PushNpcCityNewChat | `p=1`  | NpcCityManager.HandleNpcCityNewChat | - |
| `push.queue.add` | PushQueueAdd | `p=1`  | QueueDataManager.UpdateQueueData | - |
| `push.queue.del` | PushQueueDelete | `p=1`  | QueueDataManager.DeleteQueueByUuid | - |
| `push.queue.update` | PushQueueUpdate | `p=1`  | QueueDataManager.QueueFinishHandle | - |
| `push.robot.effect.change` | PushRobotEffectChange | `p=1`  | BuildQueueManager.UpdateRobotEffect | - |
| `push.ub.upgrade.stock.del` | PushUBUpgradeStockDel | `p=1`  | BuildUpgradeStockManager.PushUBUpgradeStockDelHandle | - |
| `push.user.defend.change` | PushUserDefenceChange | `p=1`  | DefenceWallDataManager.UpdateCurDurability | - |
| `push.world.mv` | PushWorldMove | `p=1`  | BuildManager.WorldMvHandle | UpdatePlayerHeadIcon |
| `push.world.mv.other` | PushWorldMoveOther | `p=1`  | BuildManager.WorldOtherMvHandle | - |
| `queue.ccd.m.new` | QueueCcdMNew | `p=3` PutLong, PutUtfString, PutInt | QueueDataManager.QueueCcsMNewHandle | DelayRefreshResource |
| `queue.finish` | QueueFinish | `p=2` PutLong | QueueDataManager.QueueFinishHandle | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (82 windows)

**Active HUD Buttons:** `GoodsBtn` [Warehouse] @ (98.0%,87.9%), `btnBuild` [] @ (1.8%,81.0%), `BuildScienceListBtn` [1/2] @ (1.7%,25.0%), `BuildQueueListBtn` [0/3] @ (1.7%,18.2%)

**`GoToUtil` Routers:** `GoToResLack.CheckMainLV` -> [], `GoToUtil.GetBuildState` -> [], `GoToUtil.GoBarracksByVS` -> [], `GoToUtil.GoBuildOpenUpgrade` -> ['UINewBuildUpgrade'], `GoToUtil.GoBusinessCenterWindow` -> [], `GoToUtil.GoCheckBuild` -> [], `GoToUtil.GoCityCollect` -> [], `GoToUtil.GoConnectBuild` -> [], `GoToUtil.GoFactoryWork` -> ['UIFactory'], `GoToUtil.GoGarageUpgradeNew` -> ['UIAircraftMain'], `GoToUtil.GoHeroBag` -> ['UIHeroBag'], `GoToUtil.GoHeroStation` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIHospital` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalMain.prefab` | ImmediatelyBtnClick, ImmediatelySpeedBtnClick, Speed... | MsgDefines.HospitalCure, MsgDefines.QueueCcdMNew |
| `UIWorldTileUI` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/World/UIWorldTileUI.prefab` | BtnBg, GetBuildBtn, GetBuildBtnEnumName, GetFakeBuil... | - |
| `UITrain` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UITrain/UITrain.prefab` | GoToBtnClick, ImmediatelyBtnClick, ImmediatelySpeedB... | MsgDefines.ArmyAdd |
| `UIResourceBag` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceBag.prefab` | CloseMoreBtn, GetMoreBtnParent, HideMoreBtn, Music_E... | MsgDefines.ItemBuyAndUse, MsgDefines.ItemUse |
| `UIWorldPoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldPoint.prefab` | RefreshBtnName, RefreshGloryWarSwapBtn, RefreshKingd... | - |
| `UIDecorationMain` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationMain...` | Music_Effect_Button, RefreshBtn, city_toggle, onSkin... | MsgDefines.GetSnowManActInfo |
| `UIHeroIntensify` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroHall/UIHeroPalaceMain.p...` | BtnType, IsOneKeyUpgradeBtnUnlock, Music_Effect_Butt... | - |
| `UIBuildDetailList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_BuildUpgrade/UIBuildDetail...` | BtnLock, OnSortToggleClick, OnTabToggleClick, UITogg... | - |
| `UIDomeUpdate` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIDomeUpdate.p...` | Music_Effect_Button, UIButton, cancel_btn, cancel_bt... | - |
| `UIHeroSPEquip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroInfoWeapon.p...` | Music_Effect_Button, OnClickBtnGoto, WorldTileBtnTyp... | MsgDefines.HeroSPEquipUnlock |
| `UICapacityBoxSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICapacity/UICapacityBoxSelec...` | Layout/Toggles/ToggleGroupSubTab/Toggle, ToggleContr... | - |
| `UIAddStamina` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIRepairBuildingPopUp.p...` | InitButtonState, Music_Effect_Button, UIButton, btn_... | MsgDefines.UserRecoverBuildingStamina |
| `UIFormationDefenceTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIFormationDefence/UIForm...` | TOGGLE_FORMATION_DIFF, _campBtn, _restraintBtn, _sol... | MsgDefines.AssistanceTeamRetreat |
| `UIFormationDefenceNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormationDefence/UIFormatio...` | CAMP_BTN_BASE_Y, CAMP_BTN_DEFENSE_OFFSET_Y, RESTRAIN... | - |
| `UIPhotoWall` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhotoWall/UIPhotoWall.prefab` | Music_Effect_Button, RefreshToggle, Toggle1, ToggleT... | - |
| `UISearch` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UISearch/UISearch.prefab` | UIButton, UIToggle, boss_btn, close_btn | MsgDefines.FindMonster |
| `UISearchMonster` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UISearch/UISearchMonster.prefab` | UIButton, UIToggle, boss_btn, close_btn | MsgDefines.FindMonster |
| `UISkinShop` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIDecoration/UISkinShop.prefab` | Music_Effect_Button, OnCityToggleClick, city_toggle,... | - |
| `UIPlaceBuild` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuild.prefab` | OnCancelBtnClick, cancel_btn | MsgDefines.FindMainBuildInitPosition, MsgDefine... |
| `UIPlaceBuildWorld` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuildWorld.prefab` | OnCancelBtnClick, cancel_btn | MsgDefines.FindMainBuildInitPosition, MsgDefine... |
| `UI_BuildUseFullScreenDialog` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UI_BuildUseFullScree...` | OnClickBtn, UIButton, _cp_btn, m_btn | - |
| `UIBuildQueueLease` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildQueue/UIBuildQueueLeas...` | - | MsgDefines.UnlockBuildingQueue, MsgDefines.User... |
| `UIBuildUpgradeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIBuildUpgrade...` | UIMainTopBtnType, hideBtnList | - |
| `UIDemolishChangeConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDemolish/UIDemolishChangeCo...` | btnAccept, btnRefuse | - |
| `UIGirlSelect` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIGirlCollect/UIGirlSelect.pr...` | ToggleBlinkEffect, __toggleGarbageCircle | - |
| `UINewBuildUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_NewBuildUpgrade/UINewBuild...` | SU_ToggleBuildBubble, tabBtns | - |
| `UISellConfirm` | `UIContainer/TopCa...` | `Assets/Main/Prefabs/UI/UICapacity/UISellConfirm.prefab` | back_toggle | MsgDefines.SoldResourceItem |
| `UIBuildDes` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIBuildDes.prefab` | WorldTileBtnType | - |
| `UIBuildList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_BuildUpgrade/UIBuildList.p...` | WorldTileBtnType | - |
| `UIConsumeItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMoveCityTip/UIConsumeItem.p...` | - | MsgDefines.AllianceMoveCity |
| `UIFormationAssistance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormationDefence/UIFormatio...` | info_btn | - |
| `UIPhotoWallBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhotoWall/UIPhotoWallBox.pr...` | - | MsgDefines.SurvivalHeroCollectionRewardView |
| `UIPlaceBauble` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuild.prefab` | OnCancelBtnClick | - |
| `UIPoliceStation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIPoliceStatio...` | info_btn | - |
| `UISUWorldCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldCollect.prefab` | Music_Effect_Button | - |
| `UIScience` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScience.prefab` | GetGuideBtn | - |
| `UISmallPeopleBuildInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleBu...` | Music_Effect_Button | - |
| `UIWorldResistanceTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldResistanceTips.p...` | buildingGotoBtnLabel | - |
| `UI_SUBuildRepair` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIBuildRecover...` | - | MsgDefines.SU_BuildRepair |
| `UCityCaptureSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UCityCaptureSuccess...` | - | - |
| `UIBarrelHeroBottomInfo` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Barrel/UIBarrelHeroBottomInfo...` | - | - |
| `UIBuildDetails` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIBuildDetails...` | - | - |
| `UIBuildQueue` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIBuildQueuePanel.prefab` | - | - |
| `UIBuildQueueList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildQueue/UIBuildQueueList...` | - | - |
| `UIBuildTimeOfChange` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/SU_NewBuildUpgrade/UIUpgradeS...` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `building` | TableName.Building | 4,089 | id, name, description, long_description, pic, model, model_world, scan, order, effect_local |
| `aps_buildzone` | TableName.BuildZone | 1,215 | id, pos, zone_type |
| `worldcity` | TableName.WorldCity | 90 | id, location, level, size, server_type, eden_city_type, belong_eden_camp, monster_id, monste... |
| `main_city_area` | TableName.SU_MainCityArea | 89 | id, name, entrance_name, all_tiles_rect, pve_level_id, contact_area, standPos, lock_type, ar... |
| `aps_singlemap_junk` | TableName.APS_SINGLEMAP_JUNK, Table... | 31 | id, Name, Desc, Show, Scale, Radius, Time, Dialog, Action, Reward |
| `build_fence` | TableName.Build_Fence | 31 | id, FencePath |
| `init_build` | TableName.Init_Build | 29 | id, sceneId, pointIndex, buildId, level, initHp, tiles, rotation, landlock, order |
| `shelter_emoji` | TableName.ShelterEmoji | 22 | id, name, free, sound, icon, animation, zoom, offset, para, good |
| `baseUnlockBuilding` | TableName.BaseUnlockBuilding | 15 | id, buildingId |
| `aps_farming` | TableName.Farming | 12 | id, product_name, build_id, order, unlock_order, group, unlock_type, unlock_condition, produ... |
| `volcano_building` | TableName.VolcanoBuilding | 11 | id, size, coordinates, area_id, name, des, alliance_point, circle_person_point |
| `building_des` | TableName.BuildingDes | 10 | id, order, effect_local, tab_type, max_level, tiles, unlock_num, building_show, put, red_dot |
| `aps_city_buff` | TableName.CityManage | 8 | id, name1, name2, name3, desc, icon, type, type2, group, status |
| `city_resident` | TableName.City_Resident | 8 | id, building |
| `dragon_building` | TableName.DragonBuilding | 7 | id, type, size, name, des, model, pic, circle_pic, coordinate, occupy_time |
| `robot` | TableName.Robot | 7 | id, unlockType, order, name, icon1, icon2, sculpture1, sculpture2, cv, cv_text |
| `aps_build_queue` | TableName.BuildQueue | 6 | id, name, uav_describe, gift |
| `building_status` | TableName.BuildStatus | 5 | id, type, type2, time, effect, effect_num, group, priority, name, description |
| `building_unlock_condition` | xmlValue.building_unlock_condition | 5 | id, unlock_condition |
| `building_direction` | TableName.BuildingDirection | 3 | id, name, icon, description, new_build |
| `building_break` | TableName.BuildingBreak | 1 | id, buildlv, show_lv, description, direction_id, condition1, condition2, condition3 |

**Enums:** `BuildingTypes` (208), `BuildBubbleType` (129), `BuildBubbleTypeOrder` (123), `BuildBubbleIconName` (120), `BuildPutState` (67), `BuildState` (29), `NewQueueType` (24), `FactoryBuild` (22), `PlaceBuildType` (18), `TaskGoBuild` (15), `WorldSeasonBuild` (14), `BuildTimeType` (12), `CityPointType` (12), `SlgVolcanoBuildingResource` (11), `VolcanoBuildingResource` (11), `BuildQueueState` (10), `CityLodArray` (8), `CityManageBuffType` (8), `MoveCityReason` (8), `UIBuildListTabType` (8), `DetectNpcCityEvenColorImage` (7), `DragonBuildingTypes` (7), `ItemProductBuild` (7), `ProductResourceItemBuildingTypes` (7), `RobotState` (7)
