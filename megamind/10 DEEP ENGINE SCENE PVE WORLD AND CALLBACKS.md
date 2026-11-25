# Volume 10: Deep Game Engine - C#-to-Lua Callbacks, PVE/Battle, World Scene, Framework, RedDot, Unity Runtime & Native DLLs

> **Generated:** `2026-11-23 11:35:28 UTC` | **Sources:** `megamind/raw/deep_engine_scene_pve_world.json` + `megamind/raw/lua_package_loaded_all_12010.json`

## 1. Deep Engine Summary

| Engine Subsystem | Verified Count |
|---|---:|
| Total Loaded Lua Modules Indexed (`package.loaded`) | **12,079** modules |
| Global Lua Engine / Model / Utility Classes (`_G.*`) | **306** classes (**6,142** methods) |
| `CSharpCallLuaInterface` C#-to-Lua Callbacks | **186** callbacks |
| Deep Engine Subsystems Inspected (PVE / Scene / Framework / Chat / Util / RedDot) | **936** modules (**15,869** methods) |
| Live Unity Scenes / Cameras / Scene Graph Nodes | **1** scene / **2** cameras / **65** root-child nodes |
| Native Process DLLs (`Alt3Game.exe`) | **119** total (**9** game/Unity/xLua DLLs) |

## 2. Unity Engine Runtime, Cameras, Graphics & Native DLLs

### Unity Runtime & Graphics Configuration
| Setting | Live Value |
|---|---|
| Unity Version / App Version | `2021.3.33f1` / `1.250.733` (`Alt3Z`, ``) |
| Target FPS / Run In Background | `targetFrameRate=60` / `runInBackground=True` |
| Screen Resolution & Mode | `2560×1369` @ `96.0 DPI` (`Windowed: 3`, fullScreen=`False`) |
| QualitySettings | level=`2`, vSync=`1`, AA=`0`, lodBias=`0.0099999997764826`, shadows=`HardOnly: 1` (dist `150.0`), aniso=`Disable: 0` |
| GPU / Hardware | `NVIDIA GeForce RTX 4080 SUPER` (`Direct3D11: 2`, `16045 MB` VRAM), `16` CPUs, `31860 MB` RAM |

### Live Unity Cameras
| Camera | Depth | Projection | FOV / OrthoSize | Clip (Near-Far) | World Pos | Euler Rot | CullingMask |
|---|---:|---|---|---|---|---|---:|
| `Main Camera` | 0.0 | Perspective | `fov=10.0` | `10.0-500.0` | `1243.00,110.00,-1022.75` | `45.8,-0.0,-0.0` | `123387735` |
| `UICamera` | 90.0 | Ortho | `ortho=684.0` | `-400.0-1000.0` | `1280.00,684.00,10.00` | `-0.0,0.0,0.0` | `32800` |

### Game / Unity / xLua Native Binaries Loaded (9 Core Binaries; 119 Total DLLs)
| Binary | RSS (KB) | Path |
|---|---:|---|
| `Alt3Game.exe` | 660 | `G:\Last Z_Third\Game\Alt3Game.exe` |
| `baselib.dll` | 412 | `G:\Last Z_Third\Game\baselib.dll` |
| `frida-agent.dll` | 23,292 | `%TEMP%/frida-050b7695313eeea81cd239ac1ae2538d\x86_64\frida-agent.dll` |
| `GameAssembly.dll` | 123,712 | `G:\Last Z_Third\Game\GameAssembly.dll` |
| `lib_burst_generated.dll` | 120 | `G:\Last Z_Third\Game\Survival_Data\Plugins\x86_64\lib_burst_generated.dll` |
| `sqlite3New.dll` | 8,932 | `G:\Last Z_Third\Game\Survival_Data\Plugins\x86_64\sqlite3New.dll` |
| `UnityPlayer.dll` | 29,692 | `G:\Last Z_Third\Game\UnityPlayer.dll` |
| `VuplexWebViewWindows.dll` | 416 | `G:\Last Z_Third\Game\Survival_Data\Plugins\x86_64\VuplexWebViewWindows.dll` |
| `xlua.dll` | 1,288 | `G:\Last Z_Third\Game\Survival_Data\Plugins\x86_64\xlua.dll` |

### Live Unity `Launch` Scene Hierarchy (65 Root & Child Nodes)
```text
SoundComponent | active=true | children=15 | comps=Transform,AudioListener | sub=SoundGroup_Music(0); SoundGroup_Hero(0); SoundGroup_UISeasonS4MainLoop(0); SoundGroup_UISeasonS4MainEnter(0); SoundGroup_BarrelSpecialSound(0); SoundGroup_LoopEffect(0); SoundGroup_Effect(0); SoundGroup_TerritoryTriumph_Burning(0); SoundGroup_TerritoryTriumph_Cooper(0); SoundGroup_Barrel(0); SoundGroup_Gatling(0); SoundGroup_Dub(0); SoundGroup_LevelWeatherGroup(0); SoundGroup_WorldScope(0); SoundGroup_LoopSound(0)
  -> SoundGroup_Music | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_Hero | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_UISeasonS4MainLoop | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_UISeasonS4MainEnter | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_BarrelSpecialSound | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_LoopEffect | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_Effect | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_TerritoryTriumph_Burning | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_TerritoryTriumph_Cooper | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_Barrel | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_Gatling | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_Dub | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_LevelWeatherGroup | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_WorldScope | active=true | children=0 | comps=Transform,AudioSource
  -> SoundGroup_LoopSound | active=true | children=0 | comps=Transform,AudioSource
ArabUtilMono(Clone) | active=true | children=0 | comps=Transform,ArabUtilMono
GuidePreload | active=true | children=0 | comps=Transform
Surviva_PVE_Light | active=true | children=3 | comps=Transform | sub=Volume [inactive](0); Directional Light [inactive](0); hq_light [inactive](0)
  -> Volume | active=false | children=0 | comps=Transform,Volume
  -> Directional Light | active=false | children=0 | comps=Transform,Light,UniversalAdditionalLightData
  -> hq_light | active=false | children=0 | comps=Transform,Light,UniversalAdditionalLightData
uSkyPro | active=false | children=6 | comps=Transform,uSkyTimeline,uSkyLighting,Animator | sub=Moon(0); Sun(0); sunEntity(0); moonEntity(0); ActorFlow(0); Volume(0)
  -> Moon | active=false | children=0 | comps=Transform,Light,uSkyMoon,UniversalAdditionalLightData
  -> Sun | active=false | children=0 | comps=Transform,Light,uSkySun,UniversalAdditionalLightData
  -> sunEntity | active=false | children=0 | comps=Transform
  -> moonEntity | active=false | children=0 | comps=Transform
  -> ActorFlow | active=false | children=0 | comps=Transform
  -> Volume | active=false | children=0 | comps=Transform,Volume
FOWSystem | active=false | children=1 | comps=Transform,FowSystem2 | sub=FogVolume(Clone)(0)
  -> FogVolume(Clone) | active=false | children=0 | comps=Transform,MeshFilter,MeshRenderer,VolumetricFog
GuideGM(Clone) | active=true | children=0 | comps=Transform,GuideGM
BakingCamera | active=false | children=0 | comps=Transform,BakingCamera,Camera
World | active=true | children=4 | comps=Transform,WorldScene | sub=Static(23); ZoneMapRoot(Clone)(2); Scene_World_S3(Clone)(7); WorldBigMap_S3(Clone)(1)
  -> Static | active=true | children=23 | comps=Transform | sub=World_Treen_Snow_08(Clone)(3); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_07(Clone)(3); World_Treen_Snow_07(Clone) [inactive](3); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_09(Clone)(3); World_Treen_Snow_07(Clone)(3); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_08(Clone)(3); P_World_Mountain_01_S3(Clone)(2); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_05(Clone)(3); World_Treen_Snow_01(Clone)(3); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_04(Clone)(3); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_05(Clone)(3); World_Treen_Snow_04(Clone)(3); World_Treen_Snow_07(Clone)(3); World_Treen_Snow_08(Clone)(3); World_Treen_Snow_03(Clone)(3); P_World_IcePlane_03_S3(Clone)(1); World_Treen_Snow_03(Clone)(3)
  -> ZoneMapRoot(Clone) | active=true | children=2 | comps=Transform,WorldZoneMapRoot,AutoAdjustLod | sub=EdgeRoot(4); ZoneRoot [inactive](3)
  -> Scene_World_S3(Clone) | active=true | children=7 | comps=Transform,SceneLowFpsMonitor,RenderSettingAuto | sub=WorldScene(0); PostProcessVolume [inactive](0); Directional Light(0); Terrain(0); Road Network_1(2); BlackBlock(1); MainCityObjectLight(0)
  -> WorldBigMap_S3(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=Worldmap_L2_S3 [inactive](9)
dynamicObj | active=true | children=109 | comps=Transform | sub=buildBubbleNode(0); AllianceCityTip(Clone)(12); AllianceCityTip(Clone)(12); AllianceCityTip(Clone)(12); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); WorldIceCaveTip(Clone)(1); AllianceWorldMark_CrossWonder_07(Clone)(3); AllianceWorldMark_CrossWonder_02(Clone)(3); AllianceWorldMark_CrossWonder_10(Clone)(3); AllianceWorldMark_6(Clone)(3); AllianceWorldMark_13(Clone)(3); A_Build_PiFu01_SJ(Clone)(3); building_400009_world(Clone)(3); A_Build_PiFu01_SJ(Clone)(3); building_400009_world(Clone)(3); building_400009_world(Clone)(3); building_400009_world(Clone)(3); building_400009_world(Clone)(3)
  -> buildBubbleNode | active=true | children=0 | comps=Transform
  -> AllianceCityTip(Clone) | active=true | children=12 | comps=Transform,AutoFaceToCamera,AutoAdjustScale,AutoAdjustLod | sub=NameLabel(1); LevelLabel(4); actBoss [inactive](2); kingShowCollider [inactive](0); kingIcon [inactive](1); ghostIcon [inactive](1); DeclareWar [inactive](2); CenterLevelLabel [inactive](2); giveUpState [inactive](1); desertLvTip [inactive](2); ColdWaveMark [inactive](0); TimeCountDown [inactive](1)
  -> AllianceCityTip(Clone) | active=true | children=12 | comps=Transform,AutoFaceToCamera,AutoAdjustScale,AutoAdjustLod | sub=NameLabel(1); LevelLabel(4); actBoss [inactive](2); kingShowCollider [inactive](0); kingIcon [inactive](1); ghostIcon [inactive](1); DeclareWar [inactive](2); CenterLevelLabel [inactive](2); giveUpState [inactive](1); desertLvTip [inactive](2); ColdWaveMark [inactive](0); TimeCountDown [inactive](1)
  -> AllianceCityTip(Clone) | active=true | children=12 | comps=Transform,AutoFaceToCamera,AutoAdjustScale,AutoAdjustLod | sub=NameLabel(1); LevelLabel(4); actBoss [inactive](2); kingShowCollider [inactive](0); kingIcon [inactive](1); ghostIcon [inactive](1); DeclareWar [inactive](2); CenterLevelLabel [inactive](2); giveUpState [inactive](1); desertLvTip [inactive](2); ColdWaveMark [inactive](0); TimeCountDown [inactive](1)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> WorldIceCaveTip(Clone) | active=true | children=1 | comps=Transform,AutoAdjustLod | sub=adjustObj(5)
  -> AllianceWorldMark_CrossWonder_07(Clone) | active=true | children=3 | comps=Transform,AutoFaceToCamera,WorldGoTransAdj,ParticleEffectImportanceGroups | sub=eff_circle(6); eff_line(4); mark(2)
  -> AllianceWorldMark_CrossWonder_02(Clone) | active=true | children=3 | comps=Transform,AutoFaceToCamera,WorldGoTransAdj,ParticleEffectImportanceGroups | sub=eff_circle(6); eff_line(4); mark(2)
  -> AllianceWorldMark_CrossWonder_10(Clone) | active=true | children=3 | comps=Transform,AutoFaceToCamera,WorldGoTransAdj,ParticleEffectImportanceGroups | sub=eff_circle(6); eff_line(4); mark(2)
  -> AllianceWorldMark_6(Clone) | active=true | children=3 | comps=Transform,AutoFaceToCamera,WorldGoTransAdj | sub=eff_circle(2); eff_line(2); mark(2)
  -> AllianceWorldMark_13(Clone) | active=true | children=3 | comps=Transform,AutoFaceToCamera,WorldGoTransAdj | sub=eff_circle(4); eff_line(2); mark(2)
  -> A_Build_PiFu01_SJ(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
  -> building_400009_world(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
  -> A_Build_PiFu01_SJ(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
  -> building_400009_world(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
  -> building_400009_world(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
  -> building_400009_world(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
  -> building_400009_world(Clone) | active=true | children=3 | comps=Transform,WorldBuilding,BuildingGrowEffect,CapsuleCollider,AutoAdjustLod,TouchObjectEventTrigger | sub=Icon [inactive](2); ModelGo(6); FoldUpGo(0)
```

## 3. Complete `CSharpCallLuaInterface` Callback Bridge (186 Callbacks)

> **Source:** `C:/Projects/barrel/Assets\Main/LuaScripts/Util\CSharpCallLuaInterface.lua`
- **Calls `DataCenter.*`:** `AllianceBaseDataManager`, `AllianceCompeteDataManager`, `AllianceTeamAssembleManager`, `BattleLevel`, `BirthPointTemplateManager`, `BoardManager`, `BuildManager`, `BuildTemplateManager`, `CityPointDataManager`, `CityPointManager`, `CollectResourceManager`, `DecorationTemplateManager`, `FrozenLandDataManager`, `GuideManager`, `LandLockManager`, `MonsterLockDataManager`, `SingleMapJunkTemplateManager`, `StatusManager`, `WorldAllianceCityDataManager`, `WorldLodManager`, `WorldMarchDataManager`, `WorldPointManager`
- **Broadcasts `EventId.*`:** `MainPosChanged`
- **Opens `UIWindowNames.*`:** -

### All 186 Callback Signatures
`AddAfterUpdate(1)`, `AddIgnoreCameraClamp(0)`, `BackFromRunner(0)`, `CanMoveBuild(1)`, `CanShowCityLabel(0)`, `CanShowLandLock(0)`, `CheckIfIsMainUIOpenOnly(0)`, `CheckIsInBasementRange(1)`, `CheckIsInBuildRange(5)`, `CheckIsInWorldBuildRange(5)`, `CheckReplaceMain(0)`, `CheckSwitch(1)`, `ClearEventRef(1)`, `ClickLandLockById(1)`, `ClickMonsterLockById(1)`, `ClickOtherLandLockById(2)`, `ClickSelfLandLock(1)`, `CloseMarch(0)`, `CloseWorldPoint(0)`, `DecreaseEventRef(1)`, `DeferCameraClamp(0)`, `ForceRequestPoint(0)`, `GetAllBuildOffset(0)`, `GetAllBuildTileByItemId(0)`, `GetAllCityPointData(0)`, `GetAllInBaseTruckShowBuild(1)`, `GetAllLodTemplates(0)`, `GetAllLuaBuildWithoutFoldUp(1)`, `GetAllPathRoadData(0)`, `GetAllProxy(0)`, `GetAllRoadData(0)`, `GetAllShowRoadData(0)`, `GetAllianceBuildTileIndex(2)`, `GetAllianceCityIdByPointInfo(1)`, `GetAllianceCityList(0)`, `GetAllianceCitySimpleDataByPointInfo(1)`, `GetAllianceColorList(0)`, `GetAllianceLeaderUid(0)`, `GetBlackDesertDecSpeed(0)`, `GetBlockCount(1)`, `GetBlockSize(1)`, `GetBoardData(1)`, `GetBoardDataByPointId(1)`, `GetBuffPerformanceInfo(1)`, `GetBuildCollectMaxOther(2)`, `GetBuildCollectMaxSelf(2)`, `GetBuildCollectSpeed(2)`, `GetBuildDataResourcePercent(1)`, `GetBuildMainVecByModelCenter(2)`, `GetBuildMaxRadius(0)`, `GetBuildModelCenter(2)`, `GetBuildModelCenterVec(2)`, `GetBuildQueueState(1)`, `GetBuildStartTimeAndEndTime(1)`, `GetBuildTileIndex(2)`, `GetBuildingDataByBuildId(1)`, `GetBuildingDataByUuid(1)`, `GetBuildingDataParamByBuildId(1)`, `GetBuildingDataParamByUuid(1)`, `GetCanShowBlackLand(0)`, `GetCityBuildingModelName(2)`, `GetCityLodArray(0)`, `GetCityPointDataByPointId(1)`, `GetCityPointSize(1)`, `GetCityPointType(1)`, `GetCollectMaxEffectByBuildId(1)`, `GetCollectRangeInfoByIndex(1)`, `GetCollectRangePoint(2)`, `GetConfigMd5(0)`, `GetConfigNum(2)`, `GetConfigStr(2)`, `GetCreateBulletMaxCount(0)`, `GetDataTableCount(1)`, `GetDirByPos(3)`, `GetDomeRange(0)`, `GetFightAllianceId(0)`, `GetHeroIcon(1)`, `GetHeroQuality(2)`, `GetIceZoneColor(0)`, `GetIceZoneIdList(0)`, `GetIsAllianceCityOpen(0)`, `GetIsUseNetRaw(0)`, `GetLandLockDataById(1)`, `GetLandLockDataByPointId(1)`, `GetLandLockDataListByState(1)`, `GetLodArray(0)`, `GetLodTemplates(1)`, `GetMainLv(0)`, `GetMainPos(0)`, `GetMarchSkinNameBySkinId(1)`, `GetMarchStateIcon(1)`, `GetMonsterLockDataList(1)`, `GetNextChangeTimeByResourceUuid(2)`, `GetOnMovingBuildUuid(0)`, `GetOtherLimitRadius(0)`, `GetOutermostIndexByIndex(4)`, `GetPBTypeDict(0)`, `GetPathRoadData(1)`, `GetPlayerMaxPicVer(0)`, `GetPlayerPic(0)`, `GetPlayerPicVer(0)`, `GetPlayerUid(0)`, `GetPointDataByUuid(1)`, `GetPointInfo(1)`, `GetResourceNameByType(1)`, `GetResourcePercent(4)`, `GetResourceTypeByBuildId(1)`, `GetRoadBuildTime(0)`, `GetShowBubblePercent(2)`, `GetShowObjectModelParam(0)`, `GetShowRoadDataByPointId(1)`, `GetSingleMapJunkTemplate(1)`, `GetTemplateData(3)`, `GetTitleNameDeltaX(1)`, `GetTouchPickablePos(0)`, `GetTrainingTypeAndBuildingType(1)`, `GetTroopCount(0)`, `GetUnloadUnusedResourceMinTime(0)`, `GetWorldBuildMainVecByModelCenter(2)`, `GetWorldBuildModelCenterVec(2)`, `GetWorldBuildTileIndex(2)`, `GetWorldBuildingModelName(1)`, `GetWorldMainPos(0)`, `GetWorldMarchDetail(0)`, `GetWorldMsgPbTreeMap(0)`, `GetWorldPointModelPath(1)`, `GetWorldPointTileSize(1)`, `HideSunshine(0)`, `IncreaseEventRef(1)`, `IndexToTilePos(1)`, `InitCityPointData(1)`, `InitRoadData(1)`, `IsArabicAutoMirrorOpen(0)`, `IsBuildWork(1)`, `IsCanPutDownByAllianceBuild(2)`, `IsCanPutDownByBuild(4)`, `IsCanPutDownByWorldBuild(4)`, `IsCanShowBuildBtn(0)`, `IsCanShowCollectGreenByPoint(1)`, `IsCollectRangePoint(1)`, `IsInMyBaseInsideRange(1)`, `IsInNewUserWorld(0)`, `IsNight(0)`, `IsRoad(1)`, `IsShowBuildFlyPath(0)`, `IsShowWorldCollectPoint(0)`, `IsTileWalkable(2)`, `IsTruckRoad(1)`, `IsUseLuaWorldPoint(0)`, `IsUseNewAlarmFunction(0)`, `IsWorldWithPBMessage(1)`, `LandLockTimeLineFinish(2)`, `MarchErrorLog(0)`, `NeedUnloadUnusedResource(0)`, `OnAddCalendarResult(1)`, `OnBeginDragMarch(1)`, `OnGotoSpecialWorld(0)`, `OnKidAuthResult(1)`, `OnPointDownMarch(1)`, `OnPointUpMarch(1)`, `OnUploadPicResult(2)`, `OnUploadPicStart(0)`, `RemoveAfterUpdate(1)`, `RemoveCityPointDataByPointId(1)`, `RemoveCityPointDataByUuid(1)`, `RemoveIgnoreCameraClamp(0)`, `ResetBoard(0)`, `SendErrorMessageToServer(1)`, `SendFindMainBuildInitPositionMessage(0)`, `SetIsInCity(1)`, `SetMainPos(0)`, `SetTouchPickablePos(1)`, `ShowSunshine(0)`, `StartMarchInit(0)`, `StartUpWorldPoint(0)`, `StartViewRequest(0)`, `TileIndexToWorld(1)`, `TilePosToIndex(1)`, `UnloadRunnerBundle(0)`, `UpdateBuildings(1)`, `WorldMarchBattleUpdateBytesHandle(1)`, `WorldMarchDelHandle(1)`, `WorldMarchGetReq(0)`, `WorldMarchUpdateHandle(1)`, `WorldToTile(1)`, `__tostring(1)`

## 4. All 306 Global Lua Engine, Model & Utility Classes (`_G.*` - 6,142 Methods)

| Global Class | Methods | Fields | Outgoing `MsgDefines` / `EventId` / `DataCenter` | Sample Methods |
|---|---:|---:|---|---|
| `HeroUtils` | 214 | 25 | DC:ArmyFormationDataManager,BattleLevel,BaubleLibraryManager | `AddModelViewShowNum(0)`, `AlreadyHasTrialHero(1)`, `CanBeUpgraded(1)`, `CheckIsCareer(1)`, `GenTrialHeroDataByIndex(1)`, `GenTrialHeroDataByLevelI... |
| `PveActorMgr` | 187 | 23 | MSG:MsgDefines.BeginPvpCaveFight,MsgDefines.GetCrossArenaUserEffect,MsgDefine... | `AddAtkTotalHp(2)`, `AddCarObject(5)`, `AddDefTotalHp(2)`, `AddListener(3)`, `AddUpdateTimer(1)`, `Barrel_SetGamePause(2)`, `CalculatePowerRatio(3)... |
| `CSharpCallLuaInterface` | 186 | 1 | MSG:MsgDefines.FindMainBuildInitPosition ; EV:MainPosChanged ; DC:AllianceBas... | `AddAfterUpdate(1)`, `AddIgnoreCameraClamp(0)`, `BackFromRunner(0)`, `CanMoveBuild(1)`, `CanShowCityLabel(0)`, `CanShowLandLock(0)`, `CheckIfIsMain... |
| `MarchUtil` | 170 | 1 | MSG:MsgDefines.AllianceWarCancel,MsgDefines.AssistanceTeamRetreat,MsgDefines.... | `AssistantThrone(2)`, `CanStartAllianceBuildingBuild(1)`, `CanStartAllianceBuildingGarrison(2)`, `CheckCollectInBlackRange(2)`, `CheckCrossThroneAt... |
| `GoToUtil` | 142 | 1 | MSG:MsgDefines.FindDesertPoint,MsgDefines.FindEnemyPoint,MsgDefines.FindMonst... | `CloseAllWindows(0)`, `DoCollectedGarbage(0)`, `DoGoLandLock(2)`, `DoGoTile(2)`, `FindMonster(1)`, `GetBuildState(1)`, `GetSourceByResourceItem(1)`... |
| `GiftPackManager` | 119 | 2 | MSG:MsgDefines.ClaimFirstPayReward,MsgDefines.ExchangeInfo,MsgDefines.FreeExc... | `CheckIfHasFreeWeeklyPackage(0)`, `CheckIfHasNewHeroMedalPack(0)`, `CheckIfIsOnlyPopupPackage(1)`, `CheckIfIsPopupPackage(1)`, `CheckIfNewWeeklyPac... |
| `GiftPackageData` | 119 | 2 | MSG:MsgDefines.ClaimFirstPayReward,MsgDefines.ExchangeInfo,MsgDefines.FreeExc... | `CheckIfHasFreeWeeklyPackage(0)`, `CheckIfHasNewHeroMedalPack(0)`, `CheckIfIsOnlyPopupPackage(1)`, `CheckIfIsPopupPackage(1)`, `CheckIfNewWeeklyPac... |
| `CommonUtil` | 105 | 1 | MSG:MsgDefines.GoldGetUpdate,MsgDefines.UserAgreeTos ; EV:Disconnect ; DC:Act... | `BackCityOrWorldGameBgMusic(0)`, `ChatIsMultiLine(0)`, `CheckIsBuildEnough(2)`, `CheckIsNewWorld(0)`, `CheckIsResourceEnough(2)`, `CheckIsResourceG... |
| `AppStartupLoading` | 103 | 32 | MSG:MsgDefines.ClientLog ; EV:CloseDisconnectView,PUSH_INIT_OK,string | `BeginConnectFlow(1)`, `CancelAllPendingRequests(1)`, `CheckServerStateStop(1)`, `CheckUsePreload(1)`, `CloseUILoading(1)`, `CreateBlurObj(1)`, `De... |
| `SlgActivityListDataManager` | 91 | 1 | EV:OnPassDay,RefreshActivityRedDot,TryCatch ; DC:ActChampionBattleManager,Act... | `ActivityByIdTime(2)`, `AddOneActivity(3)`, `AddOneDelayTimer(4)`, `AddOneSlgActivity(2)`, `CheckIfActivityOpen(3)`, `CheckIfAnyoneIsToEnd(1)`, `Ch... |
| `ChatMessage` | 82 | 2 | - | `ApplyAtTranslation(3)`, `CanShowAt(1)`, `CanShowCopy(1)`, `CanShowDown(1)`, `CanShowReply(1)`, `CanShowReport(1)`, `CanShowRevert(1)`, `CanShowTra... |
| `HeroInfo` | 82 | 1 | DC:ArmyFormationDataManager,BuildManager,HeroData | `CanAdvanceEatOther(3)`, `CanBeyond(1)`, `CanBreakRank(1)`, `CanIntensifyUp(1)`, `CanSPEquip(1)`, `CanShowGroup(1)`, `CanUpMilitaryRank(2)`, `Check... |
| `SUSoundUtil` | 74 | 1 | DC:MonsterTemplateManager,PhonographManager | `FinalPlaySound(1)`, `GetBuildingSound(2)`, `GetCurPlayMusicName(0)`, `GetSoundInternal(3)`, `GetSoundLength(1)`, `GetSoundName(1)`, `GetSoundStatu... |
| `SoundUtil` | 74 | 1 | DC:MonsterTemplateManager,PhonographManager | `FinalPlaySound(1)`, `GetBuildingSound(2)`, `GetCurPlayMusicName(0)`, `GetSoundInternal(3)`, `GetSoundLength(1)`, `GetSoundName(1)`, `GetSoundStatu... |
| `BuildingUtils` | 68 | 1 | DC:BaubleManager,BoardManager,BuildManager | `CheckIsInBuildRange(5)`, `CorrectionFenceBuildModelCenterVec(2)`, `FindAValidPlacePosForSubBuild(2)`, `GetAllCanPutPointsByBuildId(3)`, `GetAllIll... |
| `ChatInterface` | 67 | 0 | DC:ActivityListDataManager,AllianceBaseDataManager,BuildManager | `ChatShareMsg(5)`, `CheckCreatePrivateRoom(1)`, `CheckRichText(1)`, `CheckRoomSendLevel(2)`, `CollectAllianceATra(2)`, `DoAsynTranslate(2)`, `Flush... |
| `PlatformGameService` | 62 | 1 | EV:OnPGSAuthResult,OnPGSAuthSuccess,OnPGSCloudLoadResult ; DC:AccountManager | `ApplyCloudProfileForLogin(1)`, `Authenticate(2)`, `CanReportAchievement(1)`, `ClearCloudRestoreLoginSideEffects(0)`, `CloudLoad(1)`, `CloudSave(2)... |
| `WorldBuildHeadUIManager` | 60 | 2 | EV:ShowAllianceCitySoldierBlood ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `ChangeCameraLodSignalCallback(0)`, `CheckShowAllianceBuildEffect(4)`, `CheckShowCollectEffect(6)`, `... |
| `Vector3` | 57 | 0 | - | `Add(2)`, `Angle(2)`, `AngleAroundAxis(3)`, `ClampMagnitude(2)`, `Clone(1)`, `ConstNew(3)`, `ConvertFromCS(2)`, `Cross(2)`, `Deserialize(1)`, `Dist... |
| `SFSObject` | 52 | 0 | - | `ContainsKey(2)`, `GetBool(2)`, `GetBoolArray(2)`, `GetByte(2)`, `GetByteArray(2)`, `GetData(2)`, `GetDouble(2)`, `GetDoubleArray(2)`, `GetFloat(2)... |
| `MailShowHelper` | 51 | 0 | DC:MailData,MailInfoShim,MailShareManager | `GetAbstractCreateTime(1)`, `GetBlackKnightRoundName(2)`, `GetMailContent_MigrateInVite(1)`, `GetMailContent_MigrateInViteRefuse(1)`, `GetMailConte... |
| `RenderSetting` | 51 | 2 | - | `AddUpdater(0)`, `DumpSphericalHarmonicsL2(0)`, `GetAfterSceneUIOpaqueFeatureState(0)`, `GetAfterSceneUITransparentFeatureState(0)`, `GetPvpSkillPP... |
| `SceneUtils` | 51 | 1 | DC:ActIceCaveManager,ActTradePostManager,BirthPointTemplateManager | `CalcMoveOnPath(3)`, `CalculateDistanceV3(1)`, `ChangeToCity(0)`, `ChangeToWorld(0)`, `CheckCanGotoWorld(0)`, `CheckIsWorldUnlock(0)`, `ClampTilePo... |
| `WorldBuildUtil` | 51 | 1 | DC:ActBlackKnightManager,ActDragonManager,AllianceBaseDataManager | `CheckActBalckning(1)`, `CheckInRange(3)`, `CheckInRangeByPointId(3)`, `CheckIsInBasementRange(1)`, `CheckIsInBuildRange(5)`, `CheckMoveCityItem(3)... |
| `AgeVerificationManager` | 50 | 4 | EV:Age_InputAgeDone,ConfirmPrivacy ; DC:AgeVerification | `AddListener(3)`, `AddListenerList(1)`, `CancelAllPendingRequests(1)`, `CheckAgeDone(1)`, `CheckState(2)`, `Delete(1)`, `DisableUpdate_Http(1)`, `E... |
| `SFSArray` | 50 | 0 | - | `Add(2)`, `AddBool(2)`, `AddBoolArray(2)`, `AddByte(2)`, `AddByteArray(2)`, `AddDouble(2)`, `AddDoubleArray(2)`, `AddFloat(2)`, `AddFloatArray(2)`,... |
| `Mathf` | 47 | 6 | - | `Abs(0)`, `Acos(0)`, `Approximately(2)`, `Asin(0)`, `Atan(0)`, `Atan2(2)`, `Ceil(0)`, `Clamp(3)`, `Clamp01(1)`, `Cos(0)` *(+37)* |
| `WorldPointObject` | 47 | 1 | EV:DesertEffectInView,DesertOutView,MarchItemUpdateSelf ; DC:SearchLodManager... | `AddListener(3)`, `AddOldObject(1)`, `CheckShowDesertTile(1)`, `CheckShowTroopDestination(1)`, `ClearDelayInvokeMap(1)`, `ClearOldObject(1)`, `Crea... |
| `SceneManager` | 46 | 13 | MSG:MsgDefines.LeaveWorld ; EV:SU_ChangeScreen,SU_MainUIReInit,SceneChanged ;... | `ChangeCameraParamTo(2)`, `ChangeToCity(2)`, `ChangeToLastLevel(1)`, `ChangeToLevel(3)`, `ChangeToLevelById(1)`, `ChangeToMainLevel(1)`, `ChangeToW... |
| `App` | 45 | 0 | - | `ClearOldAssetBundles(1)`, `EnableVulkanForNextLaunch(1)`, `GetAnalyticID(0)`, `GetDeviceUid(0)`, `GetFromCountry(0)`, `GetLanguageName(0)`, `GetNa... |
| `DOTween` | 43 | 1 | - | `Clear(0)`, `ClearCachedTweens(0)`, `Complete(0)`, `CompleteAll(0)`, `Flip(0)`, `FlipAll(0)`, `Goto(0)`, `GotoAll(0)`, `Init(0)`, `IsTweening(0)` *... |
| `BuildingDesTemplate` | 42 | 1 | DC:BuildManager,BuildTemplateManager,ChapterTaskManager | `CanMove(1)`, `CanOverlap(1)`, `CanShow(1)`, `CanShowInBuildList(1)`, `CanShowSeasonBuild(1)`, `GetAllianceCenterId(2)`, `GetAreaId(1)`, `GetBuildM... |
| `ArmyFormationInfo` | 39 | 1 | EV:FormationSoldierUpdate ; DC:ArmyFormationData,HeroDataManager,LW3V3Manager | `CheckLoacalRemoteDiff(1)`, `ConscriptSoldier(1)`, `ConscriptSoldierNew(1)`, `Copy(2)`, `GetAllHeroSoldierCapacity(1)`, `GetAllHeroes(1)`, `GetAllS... |
| `BuildBloodManager` | 39 | 1 | EV:PveLevelEnter ; DC:GloryManager,WorldPointManager | `AddListener(1)`, `Delete(1)`, `GetBloodTipPrefab(1)`, `GetNpcCityBloodTipPrefab(1)`, `IsBloodTargetValid(3)`, `New(0)`, `OnAllianceCenterDelete(2)... |
| `SeasonUtil` | 38 | 1 | MSG:MsgDefines.SeasonBuildingResQuick ; EV:CheckCanAtkSeasonBuild ; DC:Activi... | `CanAttackAllianceBuild(1)`, `CanAttackBuild(2)`, `CheckSeasonBuild(1)`, `CheckSeasonHornIn(0)`, `GetAllianceCenterIcon(0)`, `GetConfigSeason(2)`, ... |
| `PveUtil` | 37 | 1 | DC:ActFirstChargeData,BattleLevel,BuildManager | `BattleReplyFromMail(2)`, `CanShowPowerLack(1)`, `CheckCannonLookAt(2)`, `CheckConfigChanged(0)`, `CheckHasBossInSphereRange(6)`, `CheckHasUnitInSp... |
| `AllianceBuildBloodManager` | 36 | 3 | MSG:MsgDefines.WorldGetAllianceCityDetail ; EV:PveLevelEnter ; DC:ActivityALV... | `AllianceCityInViewSignal(2)`, `ChangeCameraLodSignal(2)`, `Close(1)`, `Delete(1)`, `GetCityBloodData(3)`, `HideAllianceCitySoliderBloodEffect(2)`,... |
| `Quaternion` | 36 | 0 | - | `Angle(2)`, `AngleAxis(2)`, `Clone(1)`, `Dot(2)`, `Equals(2)`, `Euler(3)`, `EulerToQuat(3)`, `FastLookRotation(2)`, `Forward(1)`, `FromToRotation(2... |
| `RailwayUtil` | 36 | 1 | MSG:MsgDefines.AllianceTrainBattleRecord,MsgDefines.AllianceTrainFormation,Ms... | `ApplyArriveReward(1)`, `BuyAllyTrain(0)`, `CheckCanBuyTrain(0)`, `CheckTrainInMatchServer(1)`, `ClickAttackTrain(1)`, `ClickCityTrain(1)`, `ClickT... |
| `Vector2` | 36 | 0 | - | `Add(2)`, `Angle(2)`, `ClampMagnitude(2)`, `Clone(1)`, `Distance(2)`, `Div(2)`, `Dot(2)`, `FastDistance(2)`, `Get(1)`, `Lerp(3)` *(+26)* |
| `WorldBossBloodTipManager` | 35 | 3 | EV:ShowActBossHeadInBattle ; DC:WorldPointManager | `AddListener(1)`, `AddToBloodCacheList(2)`, `ChangeCameraLodSignal(2)`, `ChangeCameraLodSignalCallback(0)`, `Delete(1)`, `GetBloodCacheByUuid(2)`, ... |
| `LocalController` | 34 | 1 | - | `GetABTestTableName(2)`, `GetCacheTable(2)`, `GetTableIndex(3)`, `GetTableLength(2)`, `HasColumn(3)`, `HasTableInMem(2)`, `LoadTable(2)`, `New(0)`,... |
| `SnowCityEffectManager` | 33 | 1 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `BuildInViewSignal(1)`, `BuildOutViewSignal(1)`, `CheckShowClearSnowEffect(2)`, `CheckShowEffect(2)`, `CheckShowGetSnowBallTip(4)... |
| `BuildingLevelTemplate` | 32 | 1 | DC:BuildManager,BuildTemplateManager,SU_BuildManager | `GetAllianceCenterId(1)`, `GetAreaId(1)`, `GetBuildSeason(1)`, `GetBuildTime(1)`, `GetCityModelName(1)`, `GetCollectMax(1)`, `GetCollectMaxOthers(1... |
| `Setting` | 32 | 0 | - | `GenPrivateKey(2)`, `GetBool(2)`, `GetFloat(2)`, `GetInt(2)`, `GetPrivateBool(2)`, `GetPrivateFloat(2)`, `GetPrivateInt(2)`, `GetPrivateString(3)`,... |
| `WorldCityTipManager` | 31 | 2 | EV:ChangeCameraLod ; DC:AllianceCityTemplateManager | `AddListener(1)`, `AllianceCityInViewSignal(1)`, `AllianceCityNameChange(1)`, `AllianceCityOutViewSignal(1)`, `AllianceCityRefreshDeclare(1)`, `Cha... |
| `BagUtil` | 30 | 6 | MSG:MsgDefines.SU_SurvivalGridSyncCount ; EV:SU_RefreshMiniMapIcon ; DC:BagGr... | `CanDropBag(1)`, `CanPutItemInPocket(3)`, `CanWareBag(1)`, `ExpandNumber(2)`, `GetCabinetBuildList(1)`, `GetCabinetGridUuid(1)`, `GetDurableColor(1... |
| `Vector4` | 30 | 0 | - | `Add(2)`, `Distance(2)`, `Div(2)`, `Dot(2)`, `Get(1)`, `Lerp(3)`, `Magnitude(1)`, `Max(2)`, `Min(2)`, `MoveTowards(3)` *(+20)* |
| `BuildFireEffectManager` | 29 | 1 | EV:ShowIsOnFire ; DC:NpcCityManager,WorldPointManager | `AddListener(1)`, `BuildOutViewSignal(2)`, `ChangeShowEffect(2)`, `CheckShowEffect(2)`, `CheckShowEffectForNpcCity(2)`, `Delete(1)`, `New(0)`, `Npc... |
| `HeroAdvanceController` | 29 | 2 | EV:CheckPubBubble,HeroAdvanceSuccess,OnOneKeyAdvanceSuccess ; DC:BuildManager... | `CanEatHero(3)`, `CanShowAdvanceBubble(1)`, `Delete(1)`, `GetAdvanceConfigByQuality(2)`, `GetAdvanceHeroData(1)`, `GetAdvanceHeroNum(3)`, `GetAdvan... |
| `TileCoordWorld` | 29 | 1 | DC:BirthPointTemplateManager | `CalcMoveOnPath(3)`, `CreatePathSegment(1)`, `GetApproximateMinMaxTile(3)`, `GetCrossPointByTroopLineAndBlackRange(2)`, `GetMarchCurPos(1)`, `Index... |
| `WorldDetectEventItemObject` | 29 | 1 | EV:UPDATE_POINTS_DATA ; DC:DetectEventTemplateManager,WorldPointManager | `AddTimer(1)`, `BindCollectBubbleUI(2)`, `CreateGameObject(1)`, `DeleteTimer(1)`, `Destroy(1)`, `DoWhenCreateComplete(2)`, `DoWhenMarchInfoChange(2... |
| `CrossServerUtil` | 28 | 1 | MSG:MsgDefines.ExitDragonServer,MsgDefines.LeaveWorld,MsgDefines.MoveCrossSer... | `CanMoveCityCrossServer(1)`, `CanPlaceCrossSubway(2)`, `CanShowCrossSubwayBuildBtn(1)`, `CanShowCrossSubwayInMainUI(1)`, `CheckCanUseInDeclareWarTa... |
| `WelfareTagInfo` | 28 | 3 | DC:BuildManager,WelfareData | `GetIsOff(1)`, `GetPveShowLevels(1)`, `GetPveShowPacks(1)`, `GetTabIcon(1)`, `New(0)`, `ctor(1)`, `getBgName(1)`, `getDailyType(1)`, `getID(1)`, `g... |
| `WorldAllianceBossDamageSliderManager` | 28 | 3 | EV:HideAllianceBossHead ; DC:AllianceBossBearManager,AllianceBossManager,Worl... | `AddListener(1)`, `AddToTimeCacheList(2)`, `ChangeCameraLodSignal(1)`, `Delete(1)`, `HideAllianceBossTime(1)`, `HideAllianceBossTimeUI(2)`, `HideHe... |
| `VolcanoWarWorldManager` | 27 | 7 | EV:OnEnterWorld,PveLevelBeforeEnter ; DC:VolcanoWar,VolcanoWarManager | `AddListener(1)`, `AddTimer(1)`, `AutoRefreshMapData(1)`, `CheckShowAllEffect(1)`, `Delete(1)`, `DeleteTime(1)`, `New(0)`, `OnEnterCity(1)`, `OnEnt... |
| `WorldCountDownTImeTipsManager` | 27 | 3 | EV:AllianceBossTimeShow ; DC:WorldPointManager | `AddListener(1)`, `AddToTimeCacheList(2)`, `ChangeCameraLodSignal(2)`, `ChangeCameraLodSignalCallback(0)`, `Delete(1)`, `HideAllianceBossTime(2)`, ... |
| `ChatMessageHelper` | 26 | 2 | DC:AllianceMilestoneManager | `DecodeAtMentionTags(1)`, `DecodeAtMsg(4)`, `DecodeBase64(1)`, `EncodeAtMentions(2)`, `EncodeCoordinates(1)`, `GetShareDecode(1)`, `GetShareEncode(... |
| `WorldDesertEffectManager` | 26 | 2 | EV:DesertEffectInView ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `ChangeCameraLodSignalCallback(0)`, `CheckShowDesert(2)`, `Delete(1)`, `HideDesertSignal(2)`, `HideDe... |
| `AllianceBossBloodTipManager` | 25 | 2 | EV:ShowAllianceBossHeadInBattle ; DC:WorldPointManager | `AddListener(1)`, `AddToBloodCacheList(2)`, `ChangeCameraLodSignal(1)`, `Delete(1)`, `GetBloodCacheByUuid(2)`, `HideHeadUI(2)`, `HideTroopHead(1)`,... |
| `ChatUtils` | 25 | 0 | DC:AccountManager,ActRoamingBossManager,AllianceBaseDataManager | `CheckSwitch(1)`, `GetAccountManager(0)`, `GetActRoamingBossManager(0)`, `GetAllianceHaggleManager(0)`, `GetAllianceJoinTime(0)`, `GetBuildManager(... |
| `WorldMarchEmotionManager` | 25 | 2 | EV:WORLD_BUILD_OUT_VIEW ; DC:MarchEmojiDataManager,WorldMarchDataManager | `AddListener(1)`, `AddTimer(1)`, `AllPanelSetActive(2)`, `BindOnWorldBuildOutView(0)`, `CheckPlayEffect(4)`, `Command(2)`, `Delete(1)`, `DeleteTime... |
| `WorldMonsterBloodTipManager` | 25 | 2 | EV:ShowMonsterHeadInBattle ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CreateCacheBattleHeadList(1)`, `Delete(1)`, `GetHeadUIClass(1)`, `GetMonsterOffSetY(1)`, `HideHeadUI... |
| `CityDomeProtectEffectManager` | 24 | 1 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `AllianceCityInViewSignal(2)`, `BuildInViewSignal(2)`, `BuildOutViewSignal(2)`, `CheckShowEffect(2)`, `CityDomeHideSignal(2)`, `C... |
| `ArmyTemplate` | 23 | 1 | DC:ArmyManager,VolcanoWarManager | `GetAddValueEffectName(1)`, `GetAttackAddValue(1)`, `GetDefenceAddValue(1)`, `GetHealthAddValue(1)`, `GetLoadAddValue(1)`, `GetMaxTrainValue(1)`, `... |
| `Bounds` | 23 | 0 | - | `ClosestPoint(2)`, `Contains(2)`, `Destroy(1)`, `Encapsulate(2)`, `Expand(2)`, `Get(1)`, `GetCenter(1)`, `GetMax(2)`, `GetMin(2)`, `GetSize(1)` *(+... |
| `HeadUtil` | 23 | 2 | DC:DecorationTemplateManager,PlayerInfoDataManager | `DestroyAllBackgroundFrameSpineForMultiByPath_Except(2)`, `DestroyAllHeadFrameSpineByPathForMulti(2)`, `DestroyAllHeadFrameSpineByPathForMultiByPat... |
| `MinePlunderInfoManager` | 23 | 2 | EV:OnBeforeEnterCity ; DC:WorldPointManager | `AddListener(1)`, `Delete(1)`, `GetMinePlunderByUuid(2)`, `New(0)`, `OnChangeCameraLodSignal(2)`, `OnMinePlunderObjectInViewChange(2)`, `OnMinePlun... |
| `TroopNameLabelManager` | 23 | 2 | EV:ShowTroopName ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowEffect(2)`, `CheckTroopStateIcon(2)`, `CheckTroopStateIconSignal(2)`, `CreateCacheNameList(... |
| `WorldDesertModelManager` | 23 | 2 | EV:ShowDesertSoldierAttack ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `Delete(1)`, `HideDesertSignal(1)`, `New(0)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `RemoveAllEffect(1... |
| `WorldIceCaveTipManager` | 23 | 2 | EV:WorldPointManagerClose ; DC:ActIceCaveManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `ChangeCameraLodSignalCallback(0)`, `CheckShowAllEffect(1)`, `Delete(1)`, `New(0)`, `OnCrossServerSig... |
| `WorldTradePostTipManager` | 23 | 2 | EV:WorldPointManagerClose ; DC:ActTradePostManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowAllEffect(1)`, `Delete(1)`, `New(0)`, `OnCrossServerSignal(1)`, `OnEnterCity(2)`, `OnEnterW... |
| `GoToResLack` | 22 | 1 | EV:UIMAIN_VISIBLE ; DC:BattleLevel,BuildManager,DesertDataManager | `CheckGarbageCanPick(2)`, `CheckMainLV(0)`, `GoToHeroLvUp(1)`, `GoToItemResLack(2)`, `GoToItemResLackList(8)`, `GoToMonstCard(0)`, `GotoAddStamina(... |
| `WeatherEffectManager` | 22 | 2 | EV:PveLevelEnter | `AddListener(1)`, `AddUpdate(1)`, `Delete(1)`, `IfUpdateLoaderStrategy(2)`, `New(0)`, `OnEnterCity(1)`, `OnEnterCityCallback(0)`, `OnEnterWorld(1)`... |
| `WorldDemonHunterTipManager` | 22 | 2 | EV:WorldPointManagerClose ; DC:DemonHunterDataManager,NightFallManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `ChangeCameraLodSignalCallback(0)`, `CheckShowAllEffect(1)`, `Delete(1)`, `IsNightCanShowTip(1)`, `Ne... |
| `HeroIntensifyUtil` | 21 | 2 | DC:BuildManager,HeroDataManager,HeroIntensify | `BuildBatchHeroListEntry(2)`, `CanIntensifyUp(2)`, `CanOneKeyUpgradeByHero(2)`, `CanUseBatchEquipUniquePiece(2)`, `CanUseBatchUniqueBreak(2)`, `Can... |
| `SlgProjectBridge` | 21 | 0 | DC:ArmyManager,BuildManager,FlyController | `AddOneReward(1)`, `DoFlyItem(1)`, `DoFlySimpleFunc(6)`, `GetAllBuildSoliderMaxLevel(0)`, `GetBackSound(0)`, `GetCommonClickSound(0)`, `GetCurCanAt... |
| `ThroneHudManager` | 21 | 3 | EV:ChangeCameraLod ; DC:WorldPointManager | `BuildInViewSignal(2)`, `BuildOutViewSignal(2)`, `CheckShowEffect(2)`, `Delete(1)`, `DeleteActTimer(1)`, `New(0)`, `OnAddListeners(1)`, `OnEnterCit... |
| `LuaEntry` | 20 | 5 | EV:DidEnterBackground,OnCameraEnterIdle,WillEnterForeground ; DC:DeeplinkMana... | `ApplicationDidEnterBackground(1)`, `ApplicationWillEnterForeground(1)`, `ClearAllCacheExceptGSL(1)`, `ClearGSLCache(1)`, `ClearMessageBar(1)`, `En... |
| `MissileUnlockWorldManager` | 20 | 1 | EV:OnEnterWorld ; DC:MissileUnlock,MissileUnlockManager | `AddListener(1)`, `AddTimer(1)`, `CheckShowAllEffect(1)`, `Delete(1)`, `DeleteTime(1)`, `New(0)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `OnTimeUpdat... |
| `TroopNameLabelManagerInstance` | 20 | 1 | EV:ShowTroopName ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowEffect(2)`, `CheckTroopStateIcon(2)`, `CheckTroopStateIconSignal(2)`, `CreateCacheNameList(... |
| `WorldDesertSelectEffectManager` | 20 | 1 | EV:PveLevelEnter | `AddListener(1)`, `Delete(1)`, `HidePos(1)`, `New(0)`, `OnEnterCity(1)`, `OnEnterCityCallback(0)`, `OnEnterWorld(1)`, `OnEnterWorldCallback(0)`, `R... |
| `DecorationUtil` | 19 | 1 | DC:AllianceBaseDataManager,BuildManager,DecorationTemplateManager | `GetCityPos(0)`, `GetCityPosBig(0)`, `GetEffectDesc(1)`, `GetEffectDescList(1)`, `GetEffectNumWithType(2)`, `GetMarchPos(0)`, `GetQualityBG(1)`, `G... |
| `PayManager_GetLocalPrice` | 19 | 2 | DC:PayManager | `CancelAllPendingRequests(1)`, `Delete(1)`, `DisableUpdate_Http(1)`, `EnableUpdate_Http(1)`, `GetHost(1)`, `GetLocalPrice(2)`, `InitHttpRequestMana... |
| `WorldDesertBattleManager` | 19 | 2 | EV:ShowDesertAttackHeadUI ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckShowDesertBlood(4)`, `CheckShowDesertHeadEffect(5)`, `Delete(1)`, `HideDesertAttackHeadUISignal... |
| `WorldRoamingBossBloodTipManager` | 19 | 2 | EV:WorldTroopGameObjectCreateFinish ; DC:WorldMarchDataManager | `AddListeners(1)`, `Create(2)`, `Delete(1)`, `Destroy(2)`, `DestroyAll(1)`, `GetInstance(1)`, `New(0)`, `OnLodChanged(2)`, `OnMarchUpdate(2)`, `OnT... |
| `AllianceBaseInfo` | 18 | 1 | DC:AllianceData,AllianceShopDataManager,DecorationDataManager | `CheckIfAllianceFuncOpen(2)`, `CheckIfIsVirtualLeader(1)`, `GetBackingPowerByType(2)`, `GetBackingPowerList(1)`, `GetCountryFlagTemplate(1)`, `GetH... |
| `CityMovingEffectManager` | 18 | 1 | EV:ShowDomeShowEffect | `AddListener(1)`, `Delete(1)`, `GetHideEffectClass(1)`, `GetHideEffectPrefab(2)`, `GetShowEffectPrefab(1)`, `New(0)`, `PrepareHideEffectParams(4)`,... |
| `Color` | 18 | 0 | - | `Equals(2)`, `FromHex(1)`, `Get(1)`, `GrayScale(1)`, `HSVToRGB(4)`, `Lerp(3)`, `LerpUnclamped(3)`, `New(4)`, `RGBToHSV(1)`, `Set(5)` *(+8)* |
| `Color32` | 18 | 0 | - | `Equals(2)`, `FromHex(1)`, `Get(1)`, `GrayScale(1)`, `HSVToRGB(4)`, `Lerp(3)`, `LerpUnclamped(3)`, `New(4)`, `RGBToHSV(1)`, `Set(5)` *(+8)* |
| `DragonRangeEffectManager` | 18 | 1 | EV:PveLevelEnter ; DC:ActDragonManager | `AddListener(1)`, `Delete(1)`, `New(0)`, `OnEnterCity(2)`, `OnEnterWorld(2)`, `RemoveAllEffect(1)`, `RemoveAllTips(2)`, `RemoveEffect(1)`, `RemoveL... |
| `OpBase` | 18 | 2 | DC:BuildManager,DesertOperate | `CanShow(1)`, `GetBtnState(1)`, `GetBtnText(1)`, `GetDesc(1)`, `GetIcon(1)`, `GetMaskDesc(1)`, `GetMaskPercent(1)`, `GetOrder(1)`, `GetTitle(1)`, `... |
| `ThroneTroopHeadManager` | 18 | 2 | EV:ThroneTroopShowHead ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLod(1)`, `CheckShowEffect(2)`, `CreateCacheHeadList(1)`, `Delete(1)`, `HideTroopHeadSignal(1)`, `New(0)`, `OnEnterCi... |
| `TouchObjectEventTrigger` | 18 | 1 | - | `GetClickType(1)`, `HasComponent(1)`, `New(0)`, `SetClickType(2)`, `SetOnBeginDrag(2)`, `SetOnBeginLongTap(2)`, `SetOnClick(2)`, `SetOnDoubleClick(... |
| `TroopHeadUIManager` | 18 | 8 | - | `ChangeCameraLodSignalCallback(0)`, `Delete(1)`, `GetTroopHeadUICreateConfig(1)`, `HideExploreHeadCallback(0)`, `HideTroopHeadCallback(0)`, `New(0)... |
| `WorldBattleBuffManager` | 18 | 2 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckRemove(2)`, `CheckShowBattleBuff(2)`, `Delete(1)`, `HideBattleBuffSignal(1)`, `New(0)`, `OnEnte... |
| `list` | 18 | 0 | - | `clear(1)`, `clone(1)`, `erase(2)`, `find(3)`, `findByIndex(2)`, `findlast(3)`, `head(1)`, `insert(3)`, `new(1)`, `next(2)` *(+8)* |
| `BuildTopBubbleManager` | 17 | 1 | EV:WorldBuildTopBubblePlot ; DC:RadarCenterDataManager,WorldPointManager | `AddListener(1)`, `AddNeedRefreshBuildUuidTime(3)`, `AddTimer(1)`, `BuildOutViewSignal(1)`, `CheckDomeOpen(1)`, `CheckShowEffect(3)`, `Delete(1)`, ... |
| `ChatImageManager` | 17 | 3 | - | `CheckPermissionThen(2)`, `ImgsPermissionOK(3)`, `IsNotPC(1)`, `New(0)`, `OnChatImageUpload(4)`, `OnChatImgPick(2)`, `OnChatImgPickErrorHint(2)`, `... |
| `NoticeTipsManager` | 17 | 2 | EV:ShowActBossOpen,UI_SHOWNOTICE ; DC:BuildManager,LWBattleManager,WorldAllia... | `AddItem(2)`, `CheckNotice(1)`, `CheckShowAllianceCityTip(6)`, `Clear(1)`, `Delete(1)`, `DeleteTime(1)`, `GetNotice(3)`, `NetPush(2)`, `New(0)`, `O... |
| `SeasonSnowEffectManager` | 17 | 2 | EV:PveLevelEnter | `AddListener(1)`, `AddUpdate(1)`, `Delete(1)`, `DeleteShowItem(1)`, `New(0)`, `OnEnterCity(0)`, `OnEnterWorld(0)`, `OnModelRefresh(0)`, `OnPveLevel... |
| `WelfareController` | 17 | 0 | DC:WelfareData | `HasShowTag(0)`, `InitConfigTemplate(1)`, `_sortByPopup(1)`, `checkTagCanShow(1)`, `getModelClass(1)`, `getPopupPacks(0)`, `getSelectedID(0)`, `get... |
| `WorldAllianceBuildUtil` | 17 | 1 | DC:AllianceCityTemplateManager,AllianceMineManager,BirthPointTemplateManager | `CheckAllianceCenterSpecialRange(1)`, `ClearAllianceCenterSpecialRangeCache(0)`, `GetAllianceCenterDistanceRegionList(1)`, `GetAllianceCenterRange(... |
| `xlua` | 17 | 0 | - | `access(0)`, `cast(0)`, `genaccessor(0)`, `get_generic_method(0)`, `getmetatable(1)`, `hotfix(3)`, `import_generic_type(0)`, `import_type(0)`, `loa... |
| `EquipmentUtil` | 16 | 0 | DC:BuildManager,EquipmentManager,EquipmentSuitTemplateManager | `EquipmentInfoPanelLeftOrRight(2)`, `GetColorText(1)`, `GetEffectNumWithType(2)`, `GetEquipmentAttr(1)`, `GetEquipmentEmptyIcon(3)`, `GetEquipmentI... |
| `FoodFestivalEatBuildHudManager` | 16 | 2 | EV:ChangeCameraLod ; DC:WorldPointManager | `AddListener(1)`, `CheckShowHud(2)`, `Delete(1)`, `DestroyAll(1)`, `New(0)`, `RefreshHud(2)`, `RemoveBuildHud(2)`, `RemoveListener(1)`, `ShowBuildH... |
| `FoodFestivalEatTableHudManager` | 16 | 2 | EV:ChangeCameraLod ; DC:WorldPointManager | `AddListener(1)`, `CheckShowHud(2)`, `Delete(1)`, `DestroyAll(1)`, `New(0)`, `RefreshHud(2)`, `RemoveListener(1)`, `RemoveTableHud(2)`, `ShowTableH... |
| `SmallPeopleUtil` | 16 | 1 | DC:HeroSmallPeopleDataManager,MainCityAreaDataManager | `CheckHeroRedPoints(0)`, `CheckIsCareerByHeroId(1)`, `CheckIsCareerByUuid(1)`, `CheckIsOwned(1)`, `GetAttributeDescription(1)`, `GetSmallPeopleBoxB... |
| `ThroneBloodManager` | 16 | 2 | EV:ShowThroneArmyHeadUI | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckShowThroneBlood(4)`, `Delete(1)`, `HideThroneArmyHeadUISignal(1)`, `New(0)`, `OnEnterCity(1)`, ... |
| `WorldNewsTipsManager` | 16 | 2 | EV:PveLevelEnter ; DC:WorldNewsDataManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `Delete(1)`, `InitShowList(1)`, `New(0)`, `RemoveAllShowIcon(1)`, `RemoveAllTips(2)`, `RemoveListener... |
| `WorldTerrainSelectEffectManager` | 16 | 1 | EV:PveLevelBeforeEnter | `AddListener(1)`, `Delete(1)`, `HidePos(1)`, `New(0)`, `OnEnterCity(2)`, `OnEnterWorld(2)`, `RemoveAllEffect(1)`, `RemoveAllTips(2)`, `RemoveEffect... |
| `WorldTroopAttackBuildIconManager` | 16 | 2 | EV:ShowTroopAtkBuildIcon ; DC:WorldMarchDataManager | `AddListener(1)`, `CheckShowEffect(2)`, `Delete(1)`, `HideTroopAtkBuildIconSignal(1)`, `New(0)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `OnRefreshTro... |
| `WorldTroopLineManager` | 16 | 6 | - | `Close(1)`, `CreateTroopLine(3)`, `Delete(1)`, `GetDrawMeshRenderer(1)`, `InitDrawMeshMode(1)`, `IsDrawMeshTroopLineEnabled(1)`, `IsTroopLineCreate... |
| `BarrelAttackContext` | 15 | 4 | DC:LWBattle,PveHitReactionTemplateManager | `Acquire(0)`, `ClearPool(0)`, `GetBulletHitLabel(1)`, `GetBulletId(1)`, `GetDamageTextPrefab(1)`, `GetDeathMaterialColName(2)`, `GetDeathMaterialPa... |
| `FactoryTemplate` | 15 | 1 | DC:BuildManager,FactoryDataManager,ResourceItemDataManager | `GetMainProduct(1)`, `GetNeedGoods(1)`, `GetNumProductName(1)`, `GetProductList(1)`, `GetProductResourceItemNum(1)`, `GetProductShowIcon(1)`, `GetP... |
| `LuaWebRequest` | 15 | 1 | - | `DisposeRequest(1)`, `Get(1)`, `New(0)`, `OnRequestFailure(2)`, `OnRequestSuccess(2)`, `OnRequestTimeout(1)`, `OnUpdate(1)`, `Post(2)`, `PostJson(2... |
| `ThroneWinHudManager` | 15 | 2 | EV:ChangeCameraLod ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckShowEffect(2)`, `Delete(1)`, `New(0)`, `OnEnterCity(0)`, `RemoveAllEffect(1)`, `RemoveAllTips(0... |
| `TikTokUtil` | 15 | 1 | - | `AddNewSSR(1)`, `InitSdk(0)`, `TrackBattleResult(2)`, `TrackEvent(2)`, `TrackFormationAddSSR(1)`, `TrackMainBuildLevelUp(1)`, `TrackPlayerCostGold(... |
| `TimeUpManager` | 15 | 1 | - | `AddListenerBySimple(11)`, `AddListenerByTimeStamp(6)`, `CheckContains(3)`, `Delete(1)`, `Dispose(1)`, `New(0)`, `RemoveAllListener(2)`, `RemoveOne... |
| `WarningBallData` | 15 | 1 | DC:BuildManager,GuideManager,WarningBallManager | `ChangeCDReset(1)`, `ChangeNeedCheckFlag(2)`, `CheckIsCanCheck(2)`, `CheckIsShow(2)`, `GetPara(1)`, `InitData(3)`, `IsInGuide(1)`, `New(0)`, `OnAct... |
| `WorldArrowManager` | 15 | 2 | EV:ArrowShow ; DC:ArrowTipTemplateManager | `CheckCanShowAndSaveToLocal(2)`, `Delete(1)`, `GetArrowClass(1)`, `GetArrowParam(1)`, `GetGuidState(1)`, `GetSettingKey(2)`, `IsCreateWorldArrow(1)... |
| `WorldChristmasActTreeHudManager` | 15 | 2 | EV:ChangeCameraLod ; DC:WorldPointManager | `AddListener(1)`, `CheckShowHud(2)`, `Delete(1)`, `DestroyAll(1)`, `New(0)`, `RefreshHud(2)`, `RemoveBuildHud(2)`, `RemoveListener(1)`, `ShowBuildH... |
| `WorldMarchTileUIManager` | 15 | 2 | EV:ArmyFormatUpdate,HideFormationSelect,ShowCreateCrossWormHole ; DC:MasteryM... | `AddListener(1)`, `Delete(1)`, `New(0)`, `OnBtnClick(3)`, `OnInputDragBegin(0)`, `OnUpdateMarchSignal(0)`, `OnWorldTroopCreate(1)`, `RefreshTroop(3... |
| `WorldMoveCityAllGridManager` | 15 | 7 | EV:MissileUnlockBuildingChanged ; DC:MissileUnlockManager | `AddListener(1)`, `ClearAllMatrix(1)`, `Delete(1)`, `DrawGrid(1)`, `New(0)`, `ReBuildMissileList(1)`, `RemoveListener(1)`, `ResetMissileBuild(1)`, ... |
| `AllianceMemberInfo` | 14 | 1 | DC:AllianceData,AllianceMemberDataManager,DecorationDataManager | `CheckIfIsInactivePlayer(1)`, `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `GetOfflineTimeDesc(1)`, `GetPower(1)`, `GetPveLevel(1)`, `GetRank(1)`, `New(... |
| `DragonEffectManager` | 14 | 1 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `BuildInViewSignal(1)`, `BuildOutViewSignal(1)`, `CheckShowEffect(2)`, `Delete(1)`, `New(0)`, `RemoveAllEffect(1)`, `RemoveAllTip... |
| `FactoryData` | 14 | 1 | DC:BuildManager,FactoryDataManager,SU_FactoryDataManager | `AutoPlant(1)`, `CheckCanGetProduct(1)`, `GetAutoPlantId(1)`, `GetAutoSwitch(1)`, `GetFirstProducingProductId(1)`, `GetLatestQueueData(1)`, `GetLat... |
| `GhostKingHudManager` | 14 | 1 | EV:ThroneActAllianceCityInView ; DC:WorldPointManager | `BuildInViewSignal(2)`, `BuildOutViewSignal(2)`, `CheckShowEffect(2)`, `Delete(1)`, `New(0)`, `OnAddListeners(1)`, `OnEnterCity(1)`, `OnRemoveListe... |
| `MonthCardManager` | 14 | 0 | EV:LFMonthCardRefresh,PlayerInfoUpdated ; DC:MonthCardData | `_addListener(0)`, `_removeListener(0)`, `buy(1)`, `canBuyCard(2)`, `get(1)`, `getDefault(0)`, `hasBoughtCard(2)`, `hasBoughtSomeCard(0)`, `init(1)... |
| `QueueInfo` | 14 | 1 | DC:PushNoticeManager,QueueData | `CheckIfIrrigated(1)`, `CheckNoticePush(1)`, `GetFuncUuid(1)`, `GetParaState(1)`, `GetQueueState(1)`, `IsEnd(1)`, `New(0)`, `ParseData(2)`, `ResetQ... |
| `WorldTroopManager` | 14 | 9 | DC:WorldMarchDataManager | `Close(1)`, `CreateTroopByTier(3)`, `CreateTroopsAsync(1)`, `Delete(1)`, `GetTroopClassByType(3)`, `IsMarchIconVetoed(3)`, `New(0)`, `RefreshMonste... |
| `WorldTroopTransIconManager` | 14 | 1 | EV:ShowMarchTrans ; DC:WorldMarchDataManager | `AddListener(1)`, `CheckShowEffect(2)`, `Delete(1)`, `HideMarchTransIconSignal(1)`, `New(0)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `RemoveAllEffect... |
| `ActivityInfoData` | 13 | 1 | DC:ActivityListData,ActivityListDataManager,CarComponActivityManager | `CheckIfIsToEnd(1)`, `GetExtraActivityData(1)`, `GetOrder(1)`, `GetPersonRankRewardList(1)`, `GetRankRewardList(1)`, `GetRewardStatus(1)`, `GetRewa... |
| `ActivitySevenDayInfo` | 13 | 1 | EV:SevenDayGetReward ; DC:ActivityListData,TaskManager,VIPManager | `CheckIsSevenDayTask(2)`, `CheckRedDot(1)`, `GetBoxRewardRed(1)`, `GetRewardItemListByDay(2)`, `GetScoreByIndex(2)`, `New(0)`, `ParseActivityData(2... |
| `AllianceWarInfo` | 13 | 1 | DC:AllianceData,DecorationDataManager,WorldMarchDataManager | `CheckCanJoinAllianceWar(1)`, `EachMemberArmyInfo(3)`, `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `GetLeaderMarchUuid(1)`, `IsAllyBeRally(1)`, `IsFull... |
| `BoardData` | 13 | 1 | DC:Board,BuildManager | `GetMainRoadDirection(1)`, `GetPathRoadData(1)`, `GetRangeRoadPoints(1)`, `GetRoadPathTypeAndDirectionType(1)`, `GetShowRoadModelData(1)`, `GetViad... |
| `EasterPanelConfig` | 13 | 1 | DC:ActivityListDataManager,EasterManager | `ActIsInThisPanel(2)`, `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetOpenParam(1)`, `GetPanelData(2)`, `GetPanelDataByT... |
| `EventManager` | 13 | 1 | - | `AddListener(3)`, `Broadcast(3)`, `ClearCSRef(1)`, `DecreaseCSRef(2)`, `Delete(1)`, `DispatchCSEvent(3)`, `DispatchCSEventSFSObject(3)`, `GetCSRefe... |
| `FormationUtil` | 13 | 0 | DC:ArmyFormationDataManager,BuildTemplateManager,MonthCardNewManager | `GetAllMarch(0)`, `GetAllScoutFormations(0)`, `GetElecCost(2)`, `GetFormationBuildNameByIndex(1)`, `GetFormationItemData(2)`, `GetFormationListData... |
| `HalloweenPanelConfig` | 13 | 1 | DC:ActivityListDataManager,BasePanelConfig.lua | `ActIsInThisPanel(2)`, `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetOpenParam(1)`, `GetPanelData(2)`, `GetPanelDataByT... |
| `HeroEquipUtil` | 13 | 0 | DC:HeroEquipManager,HeroEquipTemplateManager | `CheckComposeSwitch(1)`, `CheckSwitch(1)`, `GetEquipmentIcon(3)`, `GetEquipmentIconForgingSuccessful(3)`, `GetEquipmentName(2)`, `GetEquipmentNameC... |
| `LuaDBInterface` | 13 | 3 | - | `CreateOneTable(3)`, `ExecuteMultiSQL(3)`, `ExecuteMultiSQLAfter(3)`, `ExecuteSQL(2)`, `ExecuteSQLAfter(2)`, `ExecuteSTMT(4)`, `ExecuteSTMTAfter(4)... |
| `Messenger` | 13 | 1 | - | `AddListener(3)`, `Broadcast(2)`, `BroadcastInternal(2)`, `Cleanup(1)`, `DelayBroadcast(3)`, `Dump(1)`, `New(0)`, `RemoveListener(3)`, `RemoveListe... |
| `MonthCardNewInfo` | 13 | 1 | DC:MonthCardNewManager,PayManager | `GetId(1)`, `GetPackageData(1)`, `GetPrice(1)`, `GetPriceText(1)`, `GetProductID(1)`, `IsBought(1)`, `IsTimeValid(1)`, `IsTodayClaimed(1)`, `New(0)... |
| `OpMasterySkillBase` | 13 | 3 | DC:DesertOperate,MasteryManager | `CanShow(1)`, `GetBtnState(1)`, `GetBtnText(1)`, `GetDesc(1)`, `GetIcon(1)`, `GetMaskPercent(1)`, `GetOrder(1)`, `GetTitle(1)`, `Init(2)`, `IsMeetC... |
| `Thanksgiving2026PanelConfig` | 13 | 1 | DC:ActivityListDataManager,BasePanelConfig.lua | `ActIsInThisPanel(2)`, `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetOpenParam(1)`, `GetPanelData(2)`, `GetPanelDataByT... |
| `TimerManager` | 13 | 4 | - | `Cleanup(1)`, `DelayFrameInvoke(4)`, `DelayInvoke(4)`, `DelayNextFrameAction(2)`, `Delete(1)`, `Dispose(1)`, `GetCoTimer(7)`, `GetTimer(7)`, `New(0... |
| `ValentineNewPanelConfig` | 13 | 1 | DC:ActivityListDataManager,BasePanelConfig.lua | `ActIsInThisPanel(2)`, `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetOpenParam(1)`, `GetPanelData(2)`, `GetPanelDataByT... |
| `WorldCupPanelConfig` | 13 | 1 | DC:ActivityListDataManager,BasePanelConfig.lua | `ActIsInThisPanel(2)`, `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetOpenParam(1)`, `GetPanelData(2)`, `GetPanelDataByT... |
| `WorldTroopManagerInstance` | 13 | 6 | DC:WorldMarchDataManager | `Close(1)`, `CreateTroopByTier(3)`, `CreateTroopsAsync(1)`, `Delete(1)`, `GetTroopClassByType(3)`, `IsMarchIconVetoed(3)`, `RefreshMonsterFilter(1)... |
| `WorldTroopPartManager` | 13 | 1 | DC:WorldMarchDataManager | `CreatePart(3)`, `Delete(1)`, `DestroyPart(3)`, `DoSkill(5)`, `GetTroopPartDefinitions(1)`, `New(0)`, `OnAttack(2)`, `OnLodChanged(3)`, `OnTroopCre... |
| `GameMain` | 12 | 0 | DC:FlyResourceEffectManager,IsValid,PayManager | `DispatchCSEvent(2)`, `Exit(0)`, `GetTemplateData(3)`, `OnApplicationFocus(1)`, `OnApplicationPause(1)`, `Protocal(2)`, `ProtocalImpl(2)`, `ShowFol... |
| `TheDeskUtil` | 12 | 0 | MSG:MsgDefines.JwtFunction | `Hide(0)`, `IsAvailable(0)`, `IsIdentityAvailable(0)`, `IsMatchGray(0)`, `IsWhiteList(0)`, `Login(1)`, `LoginForGame(1)`, `OnJwtReceived(1)`, `Requ... |
| `WorldSandwormMoveControlManager` | 12 | 1 | EV:OnEnterWorld | `AddListener(1)`, `CheckAll(1)`, `CheckAllEffect(1)`, `Delete(1)`, `New(0)`, `RemoveAll(1)`, `RemoveAllEffect(1)`, `RemoveListener(1)`, `__delete(1... |
| `BasePlayerInfo` | 11 | 1 | DC:DecorationDataManager,NationTemplateManager,PlayerData | `ChangeMoodStr(2)`, `ChangeSelfName(2)`, `GetCountryFlagTemplate(1)`, `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `GetPositionId(1)`, `New(0)`, `ParseD... |
| `ChristmasPanelConfig` | 11 | 1 | DC:ActivityListDataManager,ChristmasAct | `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetPanelData(2)`, `GetPanelDataByType(2)`, `GetPanelDatas(1)`, `GetPanelIdBy... |
| `FSM` | 11 | 1 | - | `AddState(3)`, `ChangeState(2)`, `GetCurState(1)`, `GetStateIndex(1)`, `HandleInput(1)`, `New(0)`, `OnUpdate(1)`, `RemoveState(2)`, `ReplaceState(3... |
| `GridInfinityScrollView` | 11 | 3 | - | `Dispose(1)`, `ForceUpdate(1)`, `Init(5)`, `LaterItemByIndex(4)`, `MoveItemByIndex(3)`, `New(0)`, `OnCreate(1)`, `OnDestroy(1)`, `Remark(2)`, `SetI... |
| `Logger` | 11 | 0 | - | `Debug(0)`, `DebugFormat(1)`, `GetLogLevel(0)`, `Log(0)`, `LogError(0)`, `LogErrorFormat(1)`, `LogFormat(1)`, `LogTable(3)`, `LogWarning(0)`, `SetL... |
| `OktoberfestPanelConfig` | 11 | 1 | DC:ActivityListDataManager,Oktoberfest | `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetPanelData(2)`, `GetPanelDataByType(2)`, `GetPanelDatas(1)`, `GetPanelIdBy... |
| `SnowManChangeSkinEffectManager` | 11 | 1 | EV:ShowSnowManChangeSkin | `AddListener(1)`, `Delete(1)`, `New(0)`, `RemoveAll(1)`, `RemoveAllTips(1)`, `RemoveCityDomeHideEffect(2)`, `RemoveListener(1)`, `ShowDomeHideEffec... |
| `ThanksGivingPanelConfig` | 11 | 1 | DC:ActivityListData,ActivityListDataManager | `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetPanelData(2)`, `GetPanelDataByType(2)`, `GetPanelDatas(1)`, `GetPanelIdBy... |
| `Timer` | 11 | 2 | - | `ForceOver(1)`, `Init(7)`, `IsOver(1)`, `New(0)`, `Pause(1)`, `Reset(1)`, `Resume(1)`, `Start(1)`, `Stop(1)`, `Update(3)` *(+1)* |
| `ValentinePanelConfig` | 11 | 1 | DC:ActivityListDataManager,ValentineAct | `CheckHaveActivityOpen(1)`, `GetActivityKey(1)`, `GetMainActType(1)`, `GetPanelData(2)`, `GetPanelDataByType(2)`, `GetPanelDatas(1)`, `GetPanelIdBy... |
| `cutils` | 11 | 2 | - | `Bin2Hex(0)`, `Binary2LuaTable(0)`, `CalcChatSign(0)`, `Compress(0)`, `Distance2D(0)`, `Distance3D(0)`, `Hex2Bin(0)`, `LuaTable2Binary(0)`, `LuaTab... |
| `ActivityEventInfo` | 10 | 1 | DC:ActivityListData,DecorationDataManager,RewardManager | `CheckIfShowCrossDesert(1)`, `CheckIfShowCrossServer(1)`, `GetCanReceiveCount(1)`, `GetRewardScience(2)`, `GetStateByScoreIndex(2)`, `New(0)`, `Par... |
| `BarrelUtils` | 10 | 0 | DC:LWBattleManager | `CalculateBulletPositions(2)`, `CalculateDamage(6)`, `CalculateHeroDamage(6)`, `GetBezierPoint(4)`, `GetEvenDistributionPointsInRectangle(1)`, `Get... |
| `BuildLabelTipManager` | 10 | 1 | EV:CheckShowMainBuildLabel ; DC:WorldPointManager | `AddListener(1)`, `BuildInViewSignal(1)`, `BuildOutViewSignal(1)`, `CheckShowEffect(2)`, `Delete(1)`, `New(0)`, `RemoveListener(1)`, `RemoveOneEffe... |
| `EventManagerInstance` | 10 | 0 | - | `AddListener(3)`, `Broadcast(3)`, `ClearCSRef(1)`, `DecreaseCSRef(2)`, `Delete(1)`, `DispatchCSEvent(3)`, `DispatchCSEventSFSObject(3)`, `GetCSRefe... |
| `FileLogger` | 10 | 2 | - | `close(0)`, `debug(1)`, `error(1)`, `get_date_str(0)`, `get_time_str(0)`, `info(1)`, `open_log_file(0)`, `set_level(1)`, `warn(1)`, `write(2)` |
| `FloatingTextHelper` | 10 | 3 | - | `ClearAll(0)`, `ClearDamageTextQueues(0)`, `CreateFloatText(5)`, `CreateFloatTextWithColor(9)`, `IsNewSystemEnabled(0)`, `SetEnabled(1)`, `SetUseNe... |
| `Localization` | 10 | 0 | - | `GetLanguage(0)`, `GetLanguageName(0)`, `GetLocalCv(0)`, `GetLocalCvName(0)`, `GetRealId(1)`, `GetString(2)`, `IsInitDone(0)`, `Reset(1)`, `SetLang... |
| `Plane` | 10 | 0 | - | `Get(1)`, `GetDistanceToPoint(2)`, `GetSide(2)`, `New(2)`, `Raycast(2)`, `SameSide(3)`, `Set3Points(4)`, `SetNormalAndPosition(3)`, `__call(2)`, `_... |
| `SlgActivityTypeBaseManager` | 10 | 1 | DC:ActivityListData | `GetActRed(2)`, `IsActivityNew(2)`, `NeedLoadDataFromServer(2)`, `New(0)`, `ParseActivityData(2)`, `RemoveActivity(2)`, `ReqActivityData(2)`, `SetA... |
| `TimerManagerInstance` | 10 | 3 | - | `Cleanup(1)`, `DelayFrameInvoke(4)`, `DelayInvoke(4)`, `DelayNextFrameAction(2)`, `Delete(1)`, `Dispose(1)`, `GetCoTimer(7)`, `GetTimer(7)`, `Start... |
| `WorldCanBuildEffectManager` | 10 | 1 | EV:ShowCanBuildEffect | `AddListener(1)`, `Delete(1)`, `HideEffectSignal(1)`, `New(0)`, `RemoveEffect(1)`, `RemoveListener(1)`, `ShowEffect(1)`, `ShowEffectSignal(1)`, `__... |
| `ZendeskUtil` | 10 | 0 | MSG:MsgDefines.JwtFunction ; EV:HideZendeskWindow | `InitSDK(0)`, `IsShowDebugButton(1)`, `IsUnlock(0)`, `Login(1)`, `LoginForGame(1)`, `OnGetUnreadCount(1)`, `RealShowMessage(0)`, `SetTicketField(1)... |
| `util` | 10 | 0 | - | `GetPersistentDataPath(0)`, `compare_values(2)`, `file_init(0)`, `file_load(1)`, `file_save(2)`, `file_write(1)`, `run_script(2)`, `run_test(5)`, `... |
| `AllianceAutoInviteData` | 9 | 1 | DC:AllianceData,DecorationDataManager | `CheckIfIsValid(1)`, `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)`, `getSenderName(1)`, `getSenderNa... |
| `AllianceHelpInfo` | 9 | 1 | DC:AllianceData,DecorationDataManager | `CheckIsFinish(1)`, `CheckStats(1)`, `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `New(0)`, `ParseData(2)`, `SetNowCount(2)`, `__delete(1)`, `__init(1)` |
| `ArenaArmyFormationInfo` | 9 | 1 | DC:ArmyManager,HeroDataManager,LW3V3ArenaManager | `CheckLoacalRemoteDiff(1)`, `ConscriptSoldier(1)`, `GetHeroDataByUuid(2)`, `GetHeroesCapacity(1)`, `New(0)`, `ParseData(2)`, `SetHighestSolderData(... |
| `BuildBoxFinishEffectManager` | 9 | 1 | EV:BuildBoxOpenFinish ; DC:BuildManager | `AddListener(1)`, `BuildBoxOpenFinishSignal(1)`, `Delete(1)`, `New(0)`, `RemoveListener(1)`, `RemoveOneEffect(2)`, `ShowOneEffect(4)`, `__delete(1)... |
| `ChapterTaskInfo` | 9 | 1 | DC:QuestTemplateManager,RewardManager,SUChapterTaskData | `GetDescType(1)`, `GetQuestTemplate(1)`, `IsNeedServerReward(1)`, `New(0)`, `SetTaskRewardState(1)`, `UpdateInfo(2)`, `UpdateRewardFromServer(2)`, ... |
| `FoodFestivalPanelNewConfig` | 9 | 1 | DC:ActivityListDataManager,FoodFestival | `GetMainActType(1)`, `GetPanelData(2)`, `GetPanelDataByType(2)`, `GetPanelDatas(1)`, `GetPanelIdByType(3)`, `GetPanelIds(1)`, `GetPopPanelPath(2)`,... |
| `GivingRosesPanelConfig` | 9 | 1 | DC:ActivityListDataManager,GivingRoses | `GetMainActType(1)`, `GetPanelData(2)`, `GetPanelDataByType(2)`, `GetPanelDatas(1)`, `GetPanelIdByType(3)`, `GetPanelIds(1)`, `GetPopPanelPath(2)`,... |
| `ItemTemplate` | 9 | 1 | DC:ItemManager | `GetAttributeDescList(1)`, `GetDescParaList(1)`, `GetIconPath(1)`, `GetJoinInfo(1)`, `GetSoundGroupId(1)`, `GetSubTableKey(2)`, `InitData(2)`, `New... |
| `MonsterRewardBoxEffectManager` | 9 | 1 | EV:MonsterRewardCreate | `AddListener(1)`, `Delete(1)`, `MonsterRewardCreateSignal(1)`, `New(0)`, `RemoveListener(1)`, `RemoveOneEffect(2)`, `ShowOneEffect(2)`, `__delete(1... |
| `PlatformGameServiceDefine` | 9 | 6 | - | `GetChannelName(1)`, `IsGoogleAchievementsStatsEnabled(0)`, `IsLogEnabled(0)`, `Log(0)`, `Logf(1)`, `PostAchDrop(2)`, `PostStat(2)`, `SetLogEnabled... |
| `RobotBuildTipManager` | 9 | 1 | DC:BuildBubbleManager,BuildQueueManager | `AddListener(1)`, `Delete(1)`, `New(0)`, `RemoveListener(1)`, `RemoveOneEffect(2)`, `ShowBuildRobotTip(2)`, `ShowOneEffect(7)`, `__delete(1)`, `__i... |
| `SFSBaseMessage` | 9 | 1 | - | `HandleMessage(2)`, `New(0)`, `NewEmpty(2)`, `NewMessage(2)`, `OnCreate(1)`, `OnDestroy(1)`, `ToBinary(1)`, `__delete(1)`, `__init(3)` |
| `SingletonListenerHandler` | 9 | 1 | - | `AddDelayEvent(3)`, `AddListener(3)`, `Delete(1)`, `New(0)`, `RemoveAllDelayEvents(1)`, `RemoveAllListeners(1)`, `RemoveListener(2)`, `__delete(1)`... |
| `UpdateManager` | 9 | 1 | - | `AddUpdate(2)`, `Cleanup(1)`, `Delete(1)`, `Dispose(1)`, `New(0)`, `RemoveUpdate(2)`, `Startup(1)`, `__delete(1)`, `__init(1)` |
| `ValentineTipsManager` | 9 | 1 | EV:ValentineTipsShow | `AddListener(1)`, `Delete(1)`, `New(0)`, `RemoveFeedTips(2)`, `RemoveListener(1)`, `ShowFeedTips(2)`, `__delete(1)`, `__init(1)`, `onShowFeedTips(1)` |
| `AllianceWarLeaderData` | 8 | 1 | DC:AllianceData,DecorationDataManager | `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `GetMarchStatus(1)`, `New(0)`, `ParseData(2)`, `UpdateArmyInfo(2)`, `__delete(1)`, `__init(1)` |
| `AllianceWarMemberData` | 8 | 1 | DC:AllianceData,DecorationDataManager | `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `GetPower(1)`, `New(0)`, `ParseData(2)`, `UpdateArmyInfo(2)`, `__delete(1)`, `__init(1)` |
| `HeroStationSkillTemplate` | 8 | 1 | DC:HeroStation,HeroStationManager | `GetDescription(2)`, `GetDescriptionUnlock(1)`, `GetEffectDescription(1)`, `GetUnlockTips(1)`, `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `ListenerHandler` | 8 | 1 | - | `AddDelayEvent(3)`, `AddListener(3)`, `New(0)`, `RemoveAllDelayEvents(1)`, `RemoveAllListeners(1)`, `RemoveListener(2)`, `__delete(1)`, `__init(1)` |
| `ObjectPool` | 8 | 1 | - | `Clear(2)`, `ClearAll(1)`, `Delete(1)`, `Load(2)`, `New(0)`, `Save(2)`, `__delete(1)`, `__init(1)` |
| `OrderTemplate` | 8 | 1 | DC:OrderData | `GetAddItem(1)`, `GetEarthOrderMoney(2)`, `GetNeedResourceItem(1)`, `GetResidentOrderMoney(1)`, `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `ScienceTemplate` | 8 | 1 | DC:ScienceData | `GetNeedBuild(1)`, `GetNeedItem(1)`, `GetNeedResource(1)`, `GetNeedResourceItem(1)`, `GetScienceTime(1)`, `InitData(2)`, `New(0)`, `__delete(1)` |
| `SexUtil` | 8 | 1 | MSG:MsgDefines.UserModifySex ; EV:UpdateGold ; DC:BuildManager | `GetModifySexCostNum(1)`, `GetSexIconName(1)`, `IsShowSexRed(0)`, `IsUnLockSex(0)`, `SendModifySexMessage(1)`, `TestSendChangeMessage(0)`, `UserMod... |
| `TaskInfo` | 8 | 1 | DC:RewardManager,SU_TaskData,TaskManager | `IsNeedServerReward(1)`, `New(0)`, `SetTaskRewardState(1)`, `SetTaskShowState(1)`, `UpdateInfo(2)`, `UpdateRewardFromServer(2)`, `__delete(1)`, `__... |
| `WorldAllianceCityData` | 8 | 1 | DC:ArmyTemplateManager,WorldPointDetail | `GetBattleType(1)`, `GetBattleTypeForThrone(1)`, `New(0)`, `ParseData(2)`, `SetArmyBlood(1)`, `UpdateKillArmy(2)`, `__delete(1)`, `__init(1)` |
| `WorldTroopStateBase` | 8 | 1 | - | `ChangeState(2)`, `New(0)`, `OnStateEnter(1)`, `OnStateLeave(1)`, `OnStateUpdate(1)`, `OnTroopChange(1)`, `__delete(1)`, `__init(3)` |
| `AccountInfo` | 7 | 1 | DC:AccountData | `IsEqual(2)`, `New(0)`, `ParseFromString(2)`, `SetData(8)`, `ToString(1)`, `__delete(1)`, `__init(1)` |
| `ApsRandom` | 7 | 1 | - | `GetSeed(1)`, `New(0)`, `Next(2)`, `NextInt(2)`, `SetSeed(2)`, `__delete(1)`, `__init(2)` |
| `ArenaRankData` | 7 | 1 | DC:ArenaManager,DecorationDataManager | `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `New(0)`, `ParseData(2)`, `ParseUpdateData(2)`, `__delete(1)`, `__init(1)` |
| `BlackLandRuinData` | 7 | 1 | DC:WorldPointDetail,WorldPointManager | `GetCurDurability(1)`, `GetOldDurability(1)`, `New(0)`, `ParseData(2)`, `ParseDurabilityData(2)`, `__delete(1)`, `__init(1)` |
| `BuildQueueTemplate` | 7 | 1 | DC:SU_BuildQueueManager | `GetMistressId(1)`, `GetNpcId(1)`, `InitData(2)`, `IsHide(1)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `CUIList` | 7 | 3 | - | `ClearList(1)`, `GetItemByIndex(2)`, `GetItemCount(1)`, `New(0)`, `OnCreate(1)`, `OnDestroy(1)`, `SetData(6)` |
| `ChatRoomData` | 7 | 2 | DC:FriendManager | `AddReplyChatData(2)`, `GetReplyChatDataBySeqId(2)`, `IsShowFriendTips(1)`, `LoadPersistedRoomBubble(1)`, `LoadPersistedRoomTop(1)`, `New(0)`, `__i... |
| `FSMachine` | 7 | 0 | - | `Add(3)`, `Create(1)`, `Dispose(1)`, `Init(2)`, `Reset(1)`, `Switch(2)`, `Update(2)` |
| `FormationAssistanceData` | 7 | 1 | DC:FormationAssistanceDataManager | `GetMemberCount(1)`, `IsFull(1)`, `IsMyAssistance(1)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `GroceryStoreOrderInfo` | 7 | 1 | DC:OrderData,ResourceItemDataManager | `CanDelete(1)`, `CanSend(1)`, `HasOrderTypeOrder(5)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `GuideTemplate` | 7 | 2 | DC:ChapterTaskCellManager,GuideManager | `CanShowQuest(1)`, `CanStrongBrake(1)`, `GetAutoDoNextTime(1)`, `InitData(2)`, `IsBrakeOff(1)`, `New(0)`, `__delete(1)` |
| `HorizontalInfinityScrollView` | 7 | 3 | - | `ForceUpdate(1)`, `Init(5)`, `MoveItemByIndex(3)`, `New(0)`, `OnCreate(1)`, `OnDestroy(1)`, `SetItemCount(2)` |
| `LayerMask` | 7 | 0 | - | `Get(1)`, `GetMask(0)`, `LayerToName(1)`, `NameToLayer(1)`, `New(1)`, `__call(2)`, `__index(2)` |
| `MonsterTemplate` | 7 | 1 | DC:MonsterManager | `GetFirstShowReward(1)`, `GetShowReward(1)`, `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)`, `getValue(2)` |
| `PBController` | 7 | 3 | - | `CreateArrayUserData(1)`, `InitBytes(1)`, `InitPBConfig(0)`, `LoadBytes(1)`, `New(0)`, `ParsePb1(2)`, `ParsePbFromBytes(2)` |
| `PlayerRankData` | 7 | 1 | DC:DecorationDataManager,RankData | `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `New(0)`, `ParseData(3)`, `SetRank(2)`, `__delete(1)`, `__init(1)` |
| `SkillInfo` | 7 | 1 | DC:HeroData | `GetLevel(1)`, `IsUnlock(1)`, `New(0)`, `SetLevel(2)`, `SetServerLock(2)`, `__delete(1)`, `__init(7)` |
| `AlLeaderCandidateData` | 6 | 1 | DC:AllianceData,DecorationDataManager | `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `AllianceStorageRecordData` | 6 | 1 | DC:AllianceData,DecorationDataManager | `GetHeadBgImg(1)`, `GetHeadBgSpine(1)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `ArmyInfo` | 6 | 1 | DC:ArmyManager,ArmyTemplateManager | `GetAddValueEffectName(1)`, `New(0)`, `UpdateFree(2)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `ChatManager2` | 6 | 6 | - | `CreateDBManager(1)`, `CreateNetManager(1)`, `CreateRoomManager(1)`, `CreateTranslateManager(1)`, `Delete(1)`, `New(0)` |
| `CoUpdateBeat` | 6 | 2 | - | `AddListener(2)`, `Clear(1)`, `Count(1)`, `CreateListener(3)`, `RemoveListener(2)`, `__call(1)` |
| `DefenceWallData` | 6 | 1 | DC:DefenceWallDataManager | `New(0)`, `ParseData(2)`, `SetColdDownTime(2)`, `SetCurDurability(2)`, `__delete(1)`, `__init(1)` |
| `DetectEventTemplate` | 6 | 1 | DC:DetectEvent,PveLevelTemplateManager | `GetRealName(1)`, `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)`, `getValue(2)` |
| `Hex` | 6 | 6 | - | `CubeToOffset(3)`, `OddROffsetNeighbor(3)`, `OffsetToCube(2)`, `OffsetToWorld(2)`, `TileDistance(4)`, `WorldToOffset(3)` |
| `InputHelper` | 6 | 0 | - | `GetMouseButton(1)`, `GetMouseButtonDown(1)`, `GetMouseButtonUp(1)`, `GetScrollWheel(0)`, `GetTouch(1)`, `IsPointerOverUI(0)` |
| `NpcCityUtil` | 6 | 0 | DC:NpcCityManager | `IsNpcUid(1)`, `IsNpcUuid(1)`, `NpcUidToChatRoomId(1)`, `NpcUidToUuid(1)`, `NpcUuidToChatRoomId(1)`, `UuidToNpcUid(1)` |
| `Ray` | 6 | 0 | - | `Get(1)`, `GetPoint(2)`, `New(2)`, `__call(3)`, `__index(2)`, `__tostring(1)` |
| `RaycastHit` | 6 | 0 | - | `Destroy(1)`, `Get(1)`, `GetMask(0)`, `Init(7)`, `New(6)`, `__index(2)` |
| `ResourceItemTemplate` | 6 | 1 | DC:BuildManager,MonsterManager,ResourceItemData | `GetMonsterJumpParam(1)`, `InitData(2)`, `New(0)`, `ShowInCapacity(1)`, `__delete(1)`, `__init(1)` |
| `ScienceTabTemplate` | 6 | 1 | DC:BuildManager,ScienceData,ScienceTemplateManager | `InitData(2)`, `IsLockSee(1)`, `IsLockSeeBuilding(1)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `ShareDecode` | 6 | 0 | - | `CreateDecodeTable(0)`, `Decode(3)`, `GetDecodeTable(0)`, `IsGmMode(1)`, `RealDecode(4)`, `UpdateDecodeTable(3)` |
| `Singleton` | 6 | 1 | - | `Delete(1)`, `GetInstance(1)`, `New(0)`, `Startup(1)`, `__delete(1)`, `__init(1)` |
| `SlgActivityInfoData` | 6 | 1 | DC:ActivityListData | `New(0)`, `ParseActivityData(2)`, `ParseServerBaseFields(2)`, `ParseTabDataCommon(2)`, `__delete(1)`, `__init(1)` |
| `StorageShopSlotData` | 6 | 1 | DC:StorageShopManager | `New(0)`, `ParseData(2)`, `SetState(2)`, `TryAdjustState(1)`, `__delete(1)`, `__init(1)` |
| `StringPool` | 6 | 1 | - | `First(1)`, `GetRandom(1)`, `New(0)`, `Sequence(1)`, `__delete(1)`, `__init(3)` |
| `TimeUper` | 6 | 1 | - | `Clear(1)`, `Init(11)`, `New(0)`, `Update(7)`, `__delete(1)`, `__init(1)` |
| `UpdateBeat` | 6 | 2 | - | `AddListener(2)`, `Clear(1)`, `Count(1)`, `CreateListener(3)`, `RemoveListener(2)`, `__call(1)` |
| `WorldPointDetailData` | 6 | 1 | DC:RewardManager,WorldPointDetail | `GetDragProtectEndTime(1)`, `IsNpc(1)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `AllianceDonateRankData` | 5 | 1 | DC:AllianceData | `New(0)`, `ParseData(2)`, `SetRank(2)`, `__delete(1)`, `__init(1)` |
| `AllianceRankData` | 5 | 1 | DC:RankData | `New(0)`, `ParseData(3)`, `SetRank(2)`, `__delete(1)`, `__init(1)` |
| `AsyncInstanceCallback` | 5 | 0 | - | `Cancel(1)`, `GetRequest(1)`, `Init(0)`, `Register(3)`, `Request(4)` |
| `CircleImage` | 5 | 3 | - | `LoadSprite(3)`, `New(0)`, `OnCreate(1)`, `OnDestroy(1)`, `SetIsCircle(2)` |
| `CustomerServiceUtil` | 5 | 0 | - | `IsTheDesk(0)`, `LoginForGame(1)`, `OnJwtReceived(1)`, `RealShowMessage(0)`, `ShowMessage(0)` |
| `DetectEventInfo` | 5 | 1 | DC:RadarCenterDataManager,RewardManager | `New(0)`, `ParseData(2)`, `SetDetectEventInfoState(2)`, `__delete(1)`, `__init(1)` |
| `MD5` | 5 | 0 | - | `finish(0)`, `init(0)`, `sum_binary(0)`, `sum_str(0)`, `update(0)` |
| `ResourceItemData` | 5 | 1 | DC:ResourceItemData | `InitData(2)`, `New(0)`, `RefreshData(2)`, `__delete(1)`, `__init(1)` |
| `ShareEncode` | 5 | 0 | - | `CreateEncodeTable(0)`, `Encode(1)`, `GetEncodeTable(0)`, `RealEncode(2)`, `UpdateEncodeTable(3)` |
| `ShareExecute` | 5 | 0 | - | `CreateExecuteTable(0)`, `Execute(2)`, `GetExecuteTable(0)`, `RealExecute(3)`, `UpdateExecuteTable(3)` |
| `StorageShopData` | 5 | 1 | DC:AllianceBaseDataManager,StorageShopManager | `GetOnSaleSlots(2)`, `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `Time` | 5 | 11 | - | `GetTimestamp(1)`, `SetDeltaTime(3)`, `SetFixedDelta(2)`, `SetFrameCount(1)`, `SetTimeScale(2)` |
| `Touch` | 5 | 0 | - | `Destroy(1)`, `GetMask(0)`, `Init(8)`, `New(7)`, `__index(2)` |
| `TroopActionTemplate` | 5 | 1 | DC:TroopAction | `GetShowDialog(1)`, `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `UnlockData` | 5 | 1 | DC:UnlockData | `New(0)`, `UpdateData(6)`, `UpdateGuideBtnData(4)`, `__delete(1)`, `__init(1)` |
| `uint64` | 5 | 0 | - | `compare(0)`, `divide(0)`, `parse(0)`, `remainder(0)`, `tostring(0)` |
| `ActivityEventRankRewardInfo` | 4 | 1 | DC:ActivityListData,RewardManager | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `ActivityScoreInfo` | 4 | 1 | DC:ActivityListData | `New(0)`, `__delete(1)`, `__init(1)`, `parseServerData(2)` |
| `AllianceGiftData` | 4 | 1 | DC:AllianceData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `AllianceInviteMemberData` | 4 | 1 | DC:AllianceData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `AllianceMarkData` | 4 | 1 | DC:WorldFavoData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `AllianceScienceData` | 4 | 1 | DC:AllianceData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `AllianceTaskTemplate` | 4 | 1 | DC:AllianceData | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `BirthPointTemplate` | 4 | 1 | DC:BirthPointManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `BookMark` | 4 | 1 | DC:WorldFavoData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `CSResourceManager` | 4 | 3 | - | `Delete(1)`, `IsAssetDownloaded(2)`, `New(0)`, `Startup(1)` |
| `CityManageData` | 4 | 1 | DC:CityManageData | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `CityManageDataManager` | 4 | 1 | DC:CityManageData | `GetAllCityManageData(1)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `GameCenterUtil` | 4 | 1 | DC:AccountManager | `IsOpen(0)`, `ReportAchievement(2)`, `ReportRankScore(2)`, `__tostring(1)` |
| `GetHDRIntensity` | 4 | 3 | - | `Init(2)`, `New(0)`, `OnCreate(1)`, `OnDestroy(1)` |
| `GlobalCache` | 4 | 0 | - | `Animator_StringToHash(1)`, `GetState0xString(1)`, `GetStatexString(1)`, `Init(0)` |
| `HeroBattleSkillTemplate` | 4 | 1 | DC:HeroBattleSkillManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `HospitalInfo` | 4 | 1 | DC:HospitalData | `New(0)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `LevelUpTemplate` | 4 | 1 | DC:SU_BuildManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `PVETriggerGatherTemplate` | 4 | 1 | DC:PVETriggerGatherManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `PersonalRankData` | 4 | 1 | DC:ActivityListData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `ProfilerUtil` | 4 | 0 | - | `BeginSample(1)`, `BeginSample2(1)`, `EndSample(0)`, `EndSample2(0)` |
| `PushInfo` | 4 | 1 | DC:PushSettingData | `New(0)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `PushSettingInfo` | 4 | 1 | DC:PushSettingData | `New(0)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `ResidentOrderInfo` | 4 | 1 | DC:OrderData | `New(0)`, `ParseData(2)`, `__delete(1)`, `__init(1)` |
| `ResourceTemplate` | 4 | 1 | DC:ResourceManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `ResourceUtils` | 4 | 1 | - | `GetResourceImagePath(1)`, `GetRewardTypeImagePath(1)`, `GetRewardTypeName(1)`, `__tostring(1)` |
| `ScienceInfo` | 4 | 1 | DC:ScienceData | `New(0)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `ScoutUtil` | 4 | 0 | DC:ArmyFormationDataManager,WorldPointManager | `GetInvesFormationInfoByIndex(1)`, `GotoScout(3)`, `IsCanStartInvestigateByIndex(1)`, `StartInvestigate(4)` |
| `SingleMapJunkTemplate` | 4 | 1 | DC:SingleMapJunkManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `StatusItem` | 4 | 1 | DC:ItemData | `New(0)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `TradeCenterInfo` | 4 | 1 | DC:TradeCenterData | `New(0)`, `UpdateInfo(2)`, `__delete(1)`, `__init(1)` |
| `UavDialogueTemplate` | 4 | 1 | DC:BuildQueueTalkManager | `InitData(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `Updatable` | 4 | 1 | - | `EnableUpdate(2)`, `New(0)`, `__delete(1)`, `__init(1)` |
| `base64` | 4 | 0 | - | `decode(3)`, `encode(3)`, `makedecoder(3)`, `makeencoder(3)` |
| `CalendarUtil` | 3 | 1 | - | `AddEvent(2)`, `IsSupport(0)`, `OnNativeResult(1)` |
| `ChatNewsInfo` | 3 | 2 | - | `New(0)`, `SetData(2)`, `__init(1)` |
| `ChatShieldInfo` | 3 | 2 | - | `New(0)`, `__init(1)`, `onParseServerData(2)` |
| `FireBaseLog` | 3 | 0 | - | `CrashlyticsAddLog(1)`, `CrashlyticsSetUserId(1)`, `SetCustomValue(2)` |
| `LuaMonoBase` | 3 | 3 | - | `New(0)`, `StartCoroutine(2)`, `StopCoroutine(2)` |
| `PBNODE` | 3 | 1 | - | `create_pbn_ud(0)`, `reset_stats(0)`, `stats(0)` |
| `SFSNetwork` | 3 | 0 | - | `HandleMessage(2)`, `SendCrossMessage(1)`, `SendMessage(1)` |
| `Screen` | 3 | 0 | - | `GetDisplayLayout(0)`, `MoveMainWindowTo(0)`, `SetResolution(0)` |
| `SlgActivityLogicInfoBase` | 3 | 1 | DC:ActivityListData | `New(0)`, `__delete(1)`, `__init(1)` |
| `SlgCanyonUtil` | 3 | 0 | - | `GetCanyonAnimSpeed(1)`, `IsCanyonMarch(1)`, `IsInCanyonActivity(1)` |
| `TimeBarUtil` | 3 | 1 | - | `CheckIsNeedChangeBar(4)`, `CheckIsNeedChangeText(2)`, `__tostring(1)` |
| `TranslateManager` | 3 | 2 | - | `GetMsg(2)`, `New(0)`, `__init(1)` |
| `rg_async` | 3 | 2 | - | `Async_Init(0)`, `Async_Uninit(0)`, `Async_Update(0)` |

## 5. Deep Engine Subsystems (936 Modules, 15,869 Methods)

| Subsystem | Modules | Total Methods |
|---|---:|---:|
| Camera, Render, Audio & Other Engine Modules | 15 | 164 |
| Chat & Moment Engine (`SlgEngine.Chat.*`) | 74 | 1,134 |
| Core Engine Utilities (`Util.*`) | 63 | 1,948 |
| Core Framework, Common & Global Runtime | 136 | 2,211 |
| Generated SLG Engine Modules (`Slg.Generated.*`) | 115 | 1,150 |
| PVE Battle Level Engine (`Scene.PVEBattleLevel.*`) | 224 | 4,140 |
| RedDot Notification & Tutorial Guide Systems | 8 | 30 |
| Tactical Battle PVE Engine (`Scene.BattlePveModule.*`) | 59 | 1,249 |
| World Map & City Scene Engine (`SlgEngine.Scene.*` / `Scene.*`) | 242 | 3,843 |

### Camera, Render, Audio & Other Engine Modules (15 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `DataCenter.CityCameraManager.CityCameraManager` | 13 | EV:ChangeCameraInitZoom,OnEnterCity ; DC:BuildManager,CityCameraManager,Decor... | `AddListener(1)`, `GetCurZoom(1)`, `GetDecorationMainViewCameraZoom(2)`, `GetDecorationWorldViewCameraZoom(1)`, `GetDefaultDeco... |
| `DataCenter.ShaderEffectManager.ShaderEffectManager` | 5 | DC:ShaderEffectManager | `AddOneWhiteEffect(2)`, `GetMaterialByShaderType(2)`, `Startup(1)`, `__delete(1)`, `__init(1)` |
| `Loading.LoadingState.WarmUpShaderState` | 6 | EV:BeginWarmUpShader,EndWarmUpShader | `DoNext(1)`, `GetCurWarmUpQueueCount(1)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `StartWarmUp(1)` |
| `Net.Msgs.Alliance.AllianceRenderHelpMessage` | 2 | EV:AllianceHelpSever ; DC:AllianceHelpDataManager | `HandleMessage(2)`, `OnCreate(3)` |
| `SlgEngine.DataCenter.WorldPointManager.BuildIconInstanceRen...` | 23 | DC:WorldPointManager | `AddIcon(4)`, `Clear(1)`, `GetCount(1)`, `RemoveIcon(2)`, `Render(2)`, `UpdateIcon(5)`, `_AddLegacy(5)`, `_AddToBatch(5)` *(+15)* |
| `SlgEngine.DataCenter.WorldPointManager.BuildLabelInstanceRe...` | 23 | DC:WorldPointManager | `AddLabel(4)`, `CheckReady(1)`, `Clear(1)`, `EnableAdaptive(5)`, `GetCount(1)`, `GetQuadMesh(1)`, `LoadBgTexture(1)`, `LoadNumA... |
| `SlgEngine.DataCenter.WorldPointManager.BuildTileInstanceRen...` | 22 | DC:WorldPointManager | `AddTile(6)`, `Clear(1)`, `CollectMeshParts(3)`, `ComputeMatrix(4)`, `ComputePartMatrix(4)`, `ComputeShadowMatrix(4)`, `FindBes... |
| `SlgEngine.DataCenter.WorldPointManager.SeasonTileInstanceRe...` | 13 | DC:WorldPointManager | `Acquire(3)`, `Clear(1)`, `GetCount(1)`, `Release(2)`, `Render(2)`, `UpdatePosition(3)`, `_ComputeMatrix(2)`, `_FinishWithTextu... |
| `SlgEngine.DataCenter.WorldPointManager.WorldStaticQuadAtlas...` | 17 | DC:WorldPointManager | `AddModel(3)`, `Clear(1)`, `GetCount(1)`, `IsModelSupported(2)`, `RemoveModel(2)`, `Render(2)`, `_AddParts(4)`, `_FlushPendingF... |
| `UI.UIAircraftMain.Component.CameraSphereMove` | 12 | - | `AddUpdateTimer(1)`, `ConvertToCartesian(3)`, `ConvertToSpherical(2)`, `Destroy(1)`, `Exit(1)`, `Init(4)`, `InitPartsPoint(1)`,... |
| `UI.UICameraInfo.Config` | 0 | - |  |
| `UI.UICameraInfo.Controller.UICameraInfoCtrl` | 1 | UI:UICameraInfo | `CloseSelf(1)` |
| `UI.UICameraInfo.View.UICameraInfoView` | 11 | - | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `GetCamera(1)`, `OnCreate(1)`, `OnDestroy(1)`, `OnDisable(1)`, `OnE... |
| `UI.UILWRailway.UILWTrainDeparture.Component.UILWTrainScienc...` | 6 | UI:UILWTrainDepartureScienceTips ; DC:ScienceManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnBtnClick(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetData(2)` |
| `UI.UISetting.UISettingGameSpeed.Component.UISettingCameraIn...` | 10 | UI:UICameraInfo | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnCreate(1)`, `OnDestroy(1)`, `OnDisable(1)`, ... |

### Chat & Moment Engine (`SlgEngine.Chat.*`) (74 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `SlgEngine.Chat.ChatInterfaceBase` | 67 | UI:UIChatNew ; DC:ActivityListDataManager,AllianceBaseDataManager,BuildManager | `ChatShareMsg(5)`, `CheckCreatePrivateRoom(1)`, `CheckRichText(1)`, `CheckRoomSendLevel(2)`, `CollectAllianceATra(2)`, `DoAsynT... |
| `SlgEngine.Chat.ChatManager2Base` | 113 | MSG:ChatMsgDefines.ChatRoom,ChatMsgDefines.ChatUpRoom,ChatMsgDefines.RoomJoin... | `BuildReportContent(6)`, `CanCancelLike(2)`, `ChatMsgFix(2)`, `CheckHasReported(3)`, `CheckIfReported(2)`, `CheckReportTime(1)`... |
| `SlgEngine.Chat.ChatUtilsBase` | 25 | DC:AccountManager,ActRoamingBossManager,AllianceBaseDataManager | `CheckSwitch(1)`, `GetAccountManager(0)`, `GetActRoamingBossManager(0)`, `GetAllianceHaggleManager(0)`, `GetAllianceJoinTime(0)... |
| `SlgEngine.Chat.Controller.ChatAtManagerBase` | 15 | - | `AddAtInfo(2)`, `AddRoomId(2)`, `CheackRoomId(2)`, `CheckAtUserList(2)`, `CheckRichText(2)`, `Clear(1)`, `GetAtInfoByName(2)`, ... |
| `SlgEngine.Chat.Controller.ChatControllerBase` | 60 | MSG:ChatMsgDefines.ChatBan,ChatMsgDefines.ChatLock,ChatMsgDefines.ChatRoom ; ... | `AddListener(3)`, `ChatRoomRequestHistoryMsg(3)`, `GetAllianceMember(1)`, `GetChatMessageHelper(1)`, `GetRedPacketInfos(1)`, `I... |
| `SlgEngine.Chat.Controller.ChatDBManagerBase` | 28 | - | `CreateChatMessage(1)`, `CreateUserInfo(1)`, `GetInsertUserInfoSQL(1)`, `GetPlayerUid(1)`, `GetRoomData(2)`, `GetSingleUserInfo... |
| `SlgEngine.Chat.Controller.ChatImageManagerBase` | 16 | - | `CheckPermissionThen(2)`, `ImgsPermissionOK(3)`, `IsNotPC(1)`, `OnChatImageUpload(4)`, `OnChatImgPick(2)`, `OnChatImgPickErrorH... |
| `SlgEngine.Chat.Controller.ChatNetManagerBase` | 43 | MSG:ChatMsgDefines.RoomJoinMulti | `CacheVerifyCode(3)`, `ClearJoinRoomCodeQueue(1)`, `ClearVerifyCodeCache(1)`, `CloseWebSocket(1)`, `CollectRoomIds(3)`, `Connec... |
| `SlgEngine.Chat.Controller.ChatNewsManagerBase` | 8 | - | `AddNews(2)`, `Clear(1)`, `GetTopNewsMainShow(1)`, `RemoveNews(2)`, `RemoveNewsByType(2)`, `RemoveTopNewsMainShow(1)`, `__init(... |
| `SlgEngine.Chat.Controller.ChatRedMangerBase` | 4 | EV:RefreshMainChatRed | `CheckRed(1)`, `Uninit(1)`, `__init(1)`, `addMsg(3)` |
| `SlgEngine.Chat.Controller.ChatReplyManagerBase` | 5 | - | `AddReplyInfo(3)`, `Clear(1)`, `GetReplyInfo(2)`, `__init(1)`, `resetData(1)` |
| `SlgEngine.Chat.Controller.ChatRestrictManagerBase` | 21 | - | `CreateChatShieldInfo(1)`, `GetGiveLikeAnim(2)`, `GetGiveLikeMsgTime(2)`, `GetMaxShield(1)`, `GetRestrictUuid(3)`, `GetShieldIn... |
| `SlgEngine.Chat.Controller.ChatRoomManagerBase` | 175 | MSG:ChatMsgDefines.HistoryRoomsV2,ChatMsgDefines.RoomInviteInfo,MsgDefines.Ch... | `AddAllianceAnnouncementRoom(3)`, `AddAllianceRoom(2)`, `AddChat(3)`, `AddCrossServerRoom(2)`, `AddDragonRoom(2)`, `AddDragonTe... |
| `SlgEngine.Chat.Controller.FilterWordsManagerBase` | 9 | - | `IsHaveSensitiveWord(2)`, `__init(1)`, `addFilterWorld(2)`, `filterSensitiveWord(2)`, `getBadWordFileName(1)`, `initBadWords(1)... |
| `SlgEngine.Chat.Controller.TranslateManagerBase` | 20 | DC:VIPManager | `AsynTranslate(3)`, `ClearDatas(1)`, `DoTranslate(2)`, `DoTranslateEx(2)`, `DoTranslateGoogle(2)`, `GetLangString(2)`, `GetMsg(... |
| `SlgEngine.Chat.Controller.UserManagerBase` | 32 | MSG:ChatMsgDefines.GetUserInfoMulti ; EV:PlayerMessageInfo,UPDATE_MSG_USERINFO | `AddTimer(1)`, `CheckUserNameAndPicVer(6)`, `CreateUserInfo(1)`, `DeleteTimer(1)`, `GetUserInfoHeadPic(2)`, `OnCacheRequestUids... |
| `SlgEngine.Chat.Model.ChatMessageBase` | 81 | - | `ApplyAtTranslation(3)`, `CanShowAt(1)`, `CanShowCopy(1)`, `CanShowDown(1)`, `CanShowReply(1)`, `CanShowReport(1)`, `CanShowRev... |
| `SlgEngine.Chat.Model.ChatNewsInfoBase` | 2 | - | `SetData(2)`, `__init(1)` |
| `SlgEngine.Chat.Model.ChatRoomDataBase` | 122 | MSG:MsgDefines.ChatSetTopOp ; EV:SetChatRoomClickTime,privateChatBubble ; DC:... | `AddManagers(2)`, `AfterInitRoomState(1)`, `AfterSetLastClickTime(1)`, `CanCountAsNewMessage(2)`, `CanReceiveGolloesReward(2)`,... |
| `SlgEngine.Chat.Model.ChatShieldInfoBase` | 2 | - | `__init(1)`, `onParseServerData(2)` |
| `SlgEngine.Chat.Model.ChatUserInfoBase` | 19 | DC:DecorationDataManager,PlayerInfoDataManager,VIPManager | `CheackUpdateInfo(2)`, `CheckIfShowStorageBtn(1)`, `CheckUpdateInfo(3)`, `GetChatBgImg(1)`, `GetChatLevelLimit(1)`, `GetGMIcon(... |
| `SlgEngine.Chat.NetMessage.GetMultiUserInfoCommandBase` | 2 | - | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.NetMessage.GetRedPacketStatusCommandBase` | 3 | - | `HandleMessage(2)`, `OnCreate(2)`, `create(2)` |
| `SlgEngine.Chat.NetMessage.RedPacketUidsGetCommandBase` | 3 | - | `HandleMessage(2)`, `OnCreate(2)`, `create(0)` |
| `SlgEngine.Chat.NetMessage.RedPacketsGetCommandBase` | 2 | - | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.NetMessage.ReportPlayChatCommandBase` | 3 | - | `HandleMessage(2)`, `OnCreate(2)`, `create(1)` |
| `SlgEngine.Chat.Other.AllianceMarkShareBase` | 8 | - | `BuildAttachmentId(4)`, `GetAllianceRoomId(1)`, `GetLangString(1)`, `IsPlayerInAlliance(1)`, `IsPlayerR4orR5(1)`, `ParseAttachm... |
| `SlgEngine.Chat.Other.ChatMessageHelperBase` | 26 | DC:AllianceMilestoneManager | `DecodeAtMentionTags(1)`, `DecodeAtMsg(4)`, `DecodeBase64(1)`, `EncodeAtMentions(2)`, `EncodeCoordinates(1)`, `GetShareDecode(1... |
| `SlgEngine.Chat.Other.ExecuteLinkBase` | 2 | - | `CreateLink(2)`, `ExecuteLink(3)` |
| `SlgEngine.Chat.Other.ShareDecodeBase` | 6 | - | `CreateDecodeTable(0)`, `Decode(3)`, `GetDecodeTable(0)`, `IsGmMode(1)`, `RealDecode(4)`, `UpdateDecodeTable(3)` |
| `SlgEngine.Chat.Other.ShareEncodeBase` | 5 | - | `CreateEncodeTable(0)`, `Encode(1)`, `GetEncodeTable(0)`, `RealEncode(2)`, `UpdateEncodeTable(3)` |
| `SlgEngine.Chat.Other.ShareExecuteBase` | 5 | - | `CreateExecuteTable(0)`, `Execute(2)`, `GetExecuteTable(0)`, `RealExecute(3)`, `UpdateExecuteTable(3)` |
| `SlgEngine.Chat.UI.UIChatAtMember.Controller.UIChatAtMemberC...` | 8 | MSG:MsgDefines.AlRank ; UI:ChatAtMember ; DC:AllianceBaseDataManager,Alliance... | `Close(1)`, `CloseSelf(1)`, `GetAllianceId(1)`, `GetMemberListByRank(3)`, `GetRankData(2)`, `GetRoomMumbers(2)`, `GetSelfIsR4or... |
| `SlgEngine.Chat.UI.UIChatCommanderTips.Controller.UIChatComm...` | 2 | UI:UIChatCommanderTips | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatImgShow.Controller.UIChatImgShowCtr...` | 1 | UI:UIChatImgShow | `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatInviteToJoin.Controller.UIChatInvit...` | 15 | MSG:MsgDefines.AlRank,MsgDefines.CreateGroupChatCheck ; UI:UIChatInviteToJoin... | `AddUid(2)`, `CheackUid(2)`, `Close(1)`, `CloseSelf(1)`, `GetAllianceId(1)`, `GetMaxMemberCount(1)`, `GetMemberListByRank(2)`, ... |
| `SlgEngine.Chat.UI.UIChatItemOperatorView.Controller.UIChatI...` | 1 | UI:UIChatItemOperatorView | `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatJoinAllianceInform.Controller.UICha...` | 3 | UI:UIChatJoinAllianceInform | `Close(2)`, `CloseSelf(2)`, `GetContentListByType(2)` |
| `SlgEngine.Chat.UI.UIChatNew.Controller.ChatViewUtils` | 47 | DC:AllianceRedPacketManager | `BeginEnvelopeJump(3)`, `BeginTreasureJump(4)`, `CanEditVipAnnouncement(1)`, `ClearEnvelopeJumpSession(2)`, `ClearTreasureJumpS... |
| `SlgEngine.Chat.UI.UIChatNew.Controller.UIChatCtrlBase` | 9 | MSG:MsgDefines.VoteAllianceNotice ; UI:UIChatImgShow,UIChatNew ; DC:AllianceA... | `AddIndex(2)`, `CheackIndex(2)`, `CloseSelf(1)`, `InitData(2)`, `IsAdd(1)`, `OnChatImgClick(3)`, `RemoveIndex(2)`, `ResendChatI... |
| `SlgEngine.Chat.UI.UIChatPlayerSetNew.Controller.UIChatPlaye...` | 2 | UI:UIChatPrivateRoomSet | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatPrivateRoomSet.Controller.UIChatPri...` | 2 | UI:UIChatPrivateRoomSet | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatPrivateSet.Controller.UIChatPrivate...` | 1 | UI:UIChatPrivateSet | `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatReport.Controller.UIChatReportCtrlBase` | 2 | UI:UIChatReport | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatRoom.UIChangeChatRoomName.Controlle...` | 5 | MSG:MsgDefines.AlName,MsgDefines.AllianceChangeAttributes ; UI:UIChangeChatRo... | `CheckName(2)`, `Close(1)`, `CloseSelf(1)`, `SendChangeNameMessage(2)`, `SendCheckNameMessage(2)` |
| `SlgEngine.Chat.UI.UIChatRoom.UIChatEmojiTip.Controller.UICh...` | 2 | UI:UIChatEmojiTip | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatRoom.UIChatRemoveMember.Controller....` | 7 | UI:UIChatRemoveMember | `AddUid(2)`, `CheackUid(2)`, `Close(1)`, `CloseSelf(1)`, `InitData(1)`, `OnRemoveClick(2)`, `RemoveUid(2)` |
| `SlgEngine.Chat.UI.UIChatRoom.UIChatRoomPlayerTip.Controller...` | 2 | UI:UIChatRoomPlayerTip | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatRoom.UIChatRoomSetting.Controller.U...` | 4 | UI:UIOtherPlayerInfo | `CheckName(2)`, `Close(1)`, `CloseSelf(1)`, `OpenOtherInfo(2)` |
| `SlgEngine.Chat.UI.UIChatRoomManagerSet.Controller.UIChatRoo...` | 8 | MSG:ChatMsgDefines.RoomGroupManagerAdd | `AddUid(2)`, `CheackUid(2)`, `Close(1)`, `CloseSelf(1)`, `GetGroupData(2)`, `InitData(2)`, `OnBtnClick(3)`, `RemoveUid(2)` |
| `SlgEngine.Chat.UI.UIChatSetLevelLimit.Controller.UIChatSetL...` | 2 | - | `Close(1)`, `CloseSelf(1)` |
| `SlgEngine.Chat.UI.UIChatVoteCreat.Controller.UIChatVoteCrea...` | 14 | MSG:MsgDefines.UpdateAllianceVote ; UI:UIChatVoteCreat ; DC:AllianceBaseDataM... | `AddOptions(1)`, `ChangeInputByIndex(3)`, `CheckAdd(2)`, `CheckRemove(1)`, `ClearSaveData(1)`, `Close(1)`, `CloseSelf(1)`, `Cre... |
| `SlgEngine.Chat.UI.UIChatVoteCreatTips.Controller.UIChatVote...` | 3 | UI:UIChatVoteCreatTips ; DC:WorldFavoDataManager | `Close(1)`, `CloseSelf(1)`, `GetMarkListByTab(2)` |
| `SlgEngine.Chat.UI.UIChatVoteMember.Controller.UIChatVoteMem...` | 3 | UI:UIChatVoteMember ; DC:AllianceMemberDataManager | `Close(1)`, `CloseSelf(1)`, `GetMemberList(2)` |
| `SlgEngine.Chat.UI.UIChatWorldShoutAtSomeOne.Controller.UICh...` | 15 | MSG:MsgDefines.AlRank,MsgDefines.CreateGroupChatCheck ; UI:UIChatWorldShoutAt... | `AddUid(2)`, `CheackUid(2)`, `Close(1)`, `CloseSelf(1)`, `GetAllianceId(1)`, `GetMaxMemberCount(1)`, `GetMemberListByRank(2)`, ... |
| `SlgEngine.Chat.WebMessage.ChatRoomGroupListNoticeCommandBase` | 2 | DC:VipRoomAnnouncementManager | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Config.WebSocketBaseMessageBase` | 7 | - | `HandleMessage(2)`, `NewEmpty(2)`, `NewMessage(2)`, `OnCreate(1)`, `OnDestroy(1)`, `__delete(1)`, `__init(3)` |
| `SlgEngine.Chat.WebMessage.GetCustomRoomListCommandBase` | 2 | DC:VipRoomAnnouncementManager | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.GetHistoryMsgsCommandBase` | 2 | DC:DigTreasureDataManager | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.JoinRoomMultiCommandBase` | 2 | - | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentFollowGiftMessageBase` | 2 | EV:MomentFollowGiftResult | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentFollowListMessageBase` | 2 | DC:MomentManager | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentNoticeLastMessageBase` | 2 | DC:MomentManager | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentSetInfoMessageBase` | 2 | DC:MomentManager | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentStatMessageBase` | 2 | - | `HandleMessage(2)`, `OnCreate(3)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentUserBlackListMessage...` | 2 | DC:MomentManager | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentUserBlockListMessage...` | 2 | DC:MomentManager | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Push.PushChatMessageBase` | 3 | MSG:MsgDefines.GetAllianceRedPacket ; EV:CarnivalBulletScreenShow ; UI:UIChat... | `HandleMessage(2)`, `IsProjectPostTypeAllowed(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Push.PushChatRevertRoomMessageBase` | 2 | EV:ChatMsgRevert ; DC:AllianceAnnouncementManager | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Push.PushChatUpMessageBase` | 2 | - | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Push.PushLoginSuccessBase` | 2 | - | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.SetSwitchFlagCommandBase` | 2 | - | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.SetUserInfo2CommandBase` | 2 | DC:VIPManager | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.SetUserInfoCommandBase` | 2 | - | `HandleMessage(2)`, `OnCreate(2)` |

### Core Engine Utilities (`Util.*`) (63 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `Util.ActivityReservationOverlapUtil` | 1 | - | `ConfirmIfOverlapOrProceed(3)` |
| `Util.AsyncInstanceCallback` | 5 | - | `Cancel(1)`, `GetRequest(1)`, `Init(0)`, `Register(3)`, `Request(4)` |
| `Util.BagUtil` | 30 | MSG:MsgDefines.SU_SurvivalGridSyncCount ; EV:SU_RefreshMiniMapIcon ; UI:UIBag... | `CanDropBag(1)`, `CanPutItemInPocket(3)`, `CanWareBag(1)`, `ExpandNumber(2)`, `GetCabinetBuildList(1)`, `GetCabinetGridUuid(1)`... |
| `Util.BuildingUtils` | 68 | DC:BaubleManager,BoardManager,BuildManager | `CheckIsInBuildRange(5)`, `CorrectionFenceBuildModelCenterVec(2)`, `FindAValidPlacePosForSubBuild(2)`, `GetAllCanPutPointsByBui... |
| `Util.CSResourceManager` | 2 | - | `IsAssetDownloaded(2)`, `Startup(1)` |
| `Util.CSharpCallLuaInterface` | 186 | MSG:MsgDefines.FindMainBuildInitPosition ; EV:MainPosChanged ; DC:AllianceBas... | `AddAfterUpdate(1)`, `AddIgnoreCameraClamp(0)`, `BackFromRunner(0)`, `CanMoveBuild(1)`, `CanShowCityLabel(0)`, `CanShowLandLock... |
| `Util.CalendarUtil` | 3 | - | `AddEvent(2)`, `IsSupport(0)`, `OnNativeResult(1)` |
| `Util.CommonUtil` | 105 | MSG:MsgDefines.GoldGetUpdate,MsgDefines.UserAgreeTos ; EV:Disconnect ; UI:UIA... | `BackCityOrWorldGameBgMusic(0)`, `ChatIsMultiLine(0)`, `CheckIsBuildEnough(2)`, `CheckIsNewWorld(0)`, `CheckIsResourceEnough(2)... |
| `Util.CrossServerOtaUtil` | 3 | - | `CheckAndCrossServer(4)`, `CheckAndGo(4)`, `GetOtaGroupsForServer(1)` |
| `Util.CrossServerUtil` | 28 | MSG:MsgDefines.ExitDragonServer,MsgDefines.LeaveWorld,MsgDefines.MoveCrossSer... | `CanMoveCityCrossServer(1)`, `CanPlaceCrossSubway(2)`, `CanShowCrossSubwayBuildBtn(1)`, `CanShowCrossSubwayInMainUI(1)`, `Check... |
| `Util.CustomerServiceUtil` | 5 | - | `IsTheDesk(0)`, `LoginForGame(1)`, `OnJwtReceived(1)`, `RealShowMessage(0)`, `ShowMessage(0)` |
| `Util.EmailCorrection` | 3 | - | `CalculateLevenshteinDistance(2)`, `GetSuggestedEmail(2)`, `SuggestDomainCorrection(2)` |
| `Util.FormationPowerCalcUtil` | 2 | DC:MoonlightCollectionDataManager | `CalcFullFormationPower(1)`, `GetParams(0)` |
| `Util.FormationUtil` | 13 | DC:ArmyFormationDataManager,BuildTemplateManager,MonthCardNewManager | `GetAllMarch(0)`, `GetAllScoutFormations(0)`, `GetElecCost(2)`, `GetFormationBuildNameByIndex(1)`, `GetFormationItemData(2)`, `... |
| `Util.GameCenterUtil` | 4 | DC:AccountManager | `IsOpen(0)`, `ReportAchievement(2)`, `ReportRankScore(2)`, `__tostring(1)` |
| `Util.GoToResLack` | 22 | EV:UIMAIN_VISIBLE ; UI:UIResourceLackNew,UIResourceLackNew1,UIResourceLackNew... | `CheckGarbageCanPick(2)`, `CheckMainLV(0)`, `GoToHeroLvUp(1)`, `GoToItemResLack(2)`, `GoToItemResLackList(8)`, `GoToMonstCard(0... |
| `Util.GoToUtil` | 142 | MSG:MsgDefines.FindDesertPoint,MsgDefines.FindEnemyPoint,MsgDefines.FindMonst... | `CloseAllWindows(0)`, `DoCollectedGarbage(0)`, `DoGoLandLock(2)`, `DoGoTile(2)`, `FindMonster(1)`, `GetBuildState(1)`, `GetSour... |
| `Util.HeadUtil` | 23 | DC:DecorationTemplateManager,PlayerInfoDataManager | `DestroyAllBackgroundFrameSpineForMultiByPath_Except(2)`, `DestroyAllHeadFrameSpineByPathForMulti(2)`, `DestroyAllHeadFrameSpin... |
| `Util.HeroUtils` | 214 | UI:UIHeroInfo ; DC:ArmyFormationDataManager,BattleLevel,BaubleLibraryManager | `AddModelViewShowNum(0)`, `AlreadyHasTrialHero(1)`, `CanBeUpgraded(1)`, `CheckIsCareer(1)`, `GenTrialHeroDataByIndex(1)`, `GenT... |
| `Util.Hex` | 6 | - | `CubeToOffset(3)`, `OddROffsetNeighbor(3)`, `OffsetToCube(2)`, `OffsetToWorld(2)`, `TileDistance(4)`, `WorldToOffset(3)` |
| `Util.HotUpdatePrefetchUtil` | 10 | - | `BuildVersionRequestParams(0)`, `ClearRecord(0)`, `GetCacheDir(0)`, `GetCheckVersionHostList(0)`, `GetRecordPath(0)`, `IsEnable... |
| `Util.ImageCacheCleaner` | 5 | - | `CleanChatImgCache(1)`, `CleanHeadCache(1)`, `DoDeleteByWhitelist(2)`, `InitTable(0)`, `TryCleanup(0)` |
| `Util.InputHelper` | 6 | - | `GetMouseButton(1)`, `GetMouseButtonDown(1)`, `GetMouseButtonUp(1)`, `GetScrollWheel(0)`, `GetTouch(1)`, `IsPointerOverUI(0)` |
| `Util.Iterator` | 11 | - | `GetCount(1)`, `GetNext(1)`, `GetPrev(1)`, `GetRandom(1)`, `IsAvailable(1)`, `IsDone(1)`, `Push(2)`, `ResetToBottom(1)` *(+3)* |
| `Util.KeyboardDiagLog` | 3 | - | `RecordChatHide(2)`, `RecordChatKbd(3)`, `SyncKbDiagTargetUid(0)` |
| `Util.MarchUtil_SLG` | 170 | MSG:MsgDefines.AllianceWarCancel,MsgDefines.AssistanceTeamRetreat,MsgDefines.... | `AssistantThrone(2)`, `CanStartAllianceBuildingBuild(1)`, `CanStartAllianceBuildingGarrison(2)`, `CheckCollectInBlackRange(2)`,... |
| `Util.MoveCityEffectUtil` | 7 | EV:CrossServerMoveCityReveal | `ClearPendingCrossServer(0)`, `ForcePlaySelfMoveCityEffect(0)`, `IsCrossServerMoving(0)`, `MarkPendingCrossServer(2)`, `NotifyC... |
| `Util.PlatformGameService.Adapters.AppleGameServiceAdapter` | 12 | - | `Authenticate(1)`, `CloudLoad(1)`, `CloudSave(2)`, `GetCapabilities(0)`, `GetChannelId(0)`, `HasAchievement(1)`, `Init(0)`, `Is... |
| `Util.PlatformGameService.Adapters.GoogleGameServiceAdapter` | 17 | - | `Authenticate(2)`, `CloudLoad(1)`, `CloudSave(2)`, `GetCapabilities(0)`, `GetChannelId(0)`, `GetDisplayName(0)`, `GetPlayerId(0... |
| `Util.PlatformGameService.Adapters.StubGameServiceAdapter` | 12 | - | `Authenticate(1)`, `CloudLoad(1)`, `CloudSave(2)`, `GetCapabilities(0)`, `GetChannelId(0)`, `HasAchievement(1)`, `Init(0)`, `Is... |
| `Util.PlatformGameService.PgsCloudLoginProfile` | 6 | - | `BuildCurrent(0)`, `BuildTokenDeviceUpdate(2)`, `CanUpdateTokenAndDeviceId(2)`, `IsSameUid(2)`, `NormalizeServerId(2)`, `Parse(1)` |
| `Util.PlatformGameService.PlatformGameAchievementUtil` | 5 | - | `GetPlatformId(2)`, `IsUploadEnabled(2)`, `LogMissingPlatformId(2)`, `ResolvePlatformAchievement(3)`, `__tostring(1)` |
| `Util.PlatformGameService.PlatformGameProgressReporter` | 18 | DC:AchievementManager,LandLockManager,TowerClimbingManager | `GetHero(2)`, `JoinAlliance(1)`, `LoginDays(1)`, `MarkServerProgressReported(2)`, `OnLevelCompleted(2)`, `PassLevels(2)`, `Proc... |
| `Util.PlatformGameService.PlatformGameService` | 62 | EV:OnPGSAuthResult,OnPGSAuthSuccess,OnPGSCloudLoadResult ; DC:AccountManager | `ApplyCloudProfileForLogin(1)`, `Authenticate(2)`, `CanReportAchievement(1)`, `ClearCloudRestoreLoginSideEffects(0)`, `CloudLoa... |
| `Util.PlatformGameService.PlatformGameServiceDefine` | 9 | - | `GetChannelName(1)`, `IsGoogleAchievementsStatsEnabled(0)`, `IsLogEnabled(0)`, `Log(0)`, `Logf(1)`, `PostAchDrop(2)`, `PostStat... |
| `Util.ProfilerUtil` | 4 | - | `BeginSample(1)`, `BeginSample2(1)`, `EndSample(0)`, `EndSample2(0)` |
| `Util.PveUtil` | 37 | UI:MainUI_SU,UIHeroList,UISearch ; DC:ActFirstChargeData,BattleLevel,BuildMan... | `BattleReplyFromMail(2)`, `CanShowPowerLack(1)`, `CheckCannonLookAt(2)`, `CheckConfigChanged(0)`, `CheckHasBossInSphereRange(6)... |
| `Util.QualitySettingUtil` | 12 | MSG:MsgDefines.UserSetHd ; EV:QualityChange | `ApplyParticleQualitySwitch(0)`, `ChangePiplineToCheku(0)`, `GetDeviceLevel(0)`, `GetGraphicLvStr(1)`, `GetSettingGroup(1)`, `G... |
| `Util.RallyManualMarchUtil` | 19 | MSG:MsgDefines.AllianceTeamManualMarch ; DC:AllianceWarDataManager,WorldMarch... | `ConfirmRetreat(2)`, `EvaluateTeamClick(1)`, `GetJoinNum(1)`, `GetLeaderMarchSeconds(1)`, `GetNotReadyTipId(1)`, `GetRallyTarge... |
| `Util.ResourceUtils` | 4 | - | `GetResourceImagePath(1)`, `GetRewardTypeImagePath(1)`, `GetRewardTypeName(1)`, `__tostring(1)` |
| `Util.RewardUtil` | 6 | DC:ItemTemplateManager | `DoFlyReward(3)`, `GetPic(2)`, `GetRewardColor(1)`, `SortRewardList(1)`, `SortRewardListByType(1)`, `__tostring(1)` |
| `Util.RuntimeDownloadLoading` | 14 | DC:BundleDownloadManager | `CheckAndDownload(3)`, `CheckOtaAndDownload(3)`, `ForceClose(0)`, `IsShowing(0)`, `_Close(1)`, `_CompleteAndFinish(1)`, `_Descr... |
| `Util.SUSoundUtil` | 74 | UI:UICommonMessageBar ; DC:MonsterTemplateManager,PhonographManager | `FinalPlaySound(1)`, `GetBuildingSound(2)`, `GetCurPlayMusicName(0)`, `GetSoundInternal(3)`, `GetSoundLength(1)`, `GetSoundName... |
| `Util.SceneUtils` | 45 | DC:ActIceCaveManager,BirthPointTemplateManager,BuildManager | `CalcMoveOnPath(3)`, `CalculateDistanceV3(1)`, `ChangeToCity(2)`, `ChangeToWorld(0)`, `CheckCanGotoWorld(0)`, `CheckIsWorldUnlo... |
| `Util.SceneUtils2` | 51 | DC:ActIceCaveManager,ActTradePostManager,BirthPointTemplateManager | `CalcMoveOnPath(3)`, `CalculateDistanceV3(1)`, `ChangeToCity(0)`, `ChangeToWorld(0)`, `CheckCanGotoWorld(0)`, `CheckIsWorldUnlo... |
| `Util.ScoutUtil` | 4 | DC:ArmyFormationDataManager,WorldPointManager | `GetInvesFormationInfoByIndex(1)`, `GotoScout(3)`, `IsCanStartInvestigateByIndex(1)`, `StartInvestigate(4)` |
| `Util.ScreenSafeAreaUtil` | 2 | - | `Apply(1)`, `IsNoCompensationModel(1)` |
| `Util.SeasonUtil` | 38 | MSG:MsgDefines.SeasonBuildingResQuick ; EV:CheckCanAtkSeasonBuild ; UI:UISeas... | `CanAttackAllianceBuild(1)`, `CanAttackBuild(2)`, `CheckSeasonBuild(1)`, `CheckSeasonHornIn(0)`, `GetAllianceCenterIcon(0)`, `G... |
| `Util.SexUtil` | 8 | MSG:MsgDefines.UserModifySex ; EV:UpdateGold ; DC:BuildManager | `GetModifySexCostNum(1)`, `GetSexIconName(1)`, `IsShowSexRed(0)`, `IsUnLockSex(0)`, `SendModifySexMessage(1)`, `TestSendChangeM... |
| `Util.SmallPeopleUtil` | 16 | DC:HeroSmallPeopleDataManager,MainCityAreaDataManager | `CheckHeroRedPoints(0)`, `CheckIsCareerByHeroId(1)`, `CheckIsCareerByUuid(1)`, `CheckIsOwned(1)`, `GetAttributeDescription(1)`,... |
| `Util.States` | 14 | - | `AddState(5)`, `Agent(4)`, `CurrentStateEqual(2)`, `Dispose(1)`, `Enter(1)`, `Exit(1)`, `ExitCurrentState(1)`, `GetCurrentState... |
| `Util.TheDeskUtil` | 12 | MSG:MsgDefines.JwtFunction | `Hide(0)`, `IsAvailable(0)`, `IsIdentityAvailable(0)`, `IsMatchGray(0)`, `IsWhiteList(0)`, `Login(1)`, `LoginForGame(1)`, `OnJw... |
| `Util.ThrottleByKey` | 4 | - | `Call(2)`, `Clear(1)`, `_Fire(2)`, `__init(4)` |
| `Util.TikTokUtil` | 15 | - | `AddNewSSR(1)`, `InitSdk(0)`, `TrackBattleResult(2)`, `TrackEvent(2)`, `TrackFormationAddSSR(1)`, `TrackMainBuildLevelUp(1)`, `... |
| `Util.TileCoordWorld` | 29 | DC:BirthPointTemplateManager | `CalcMoveOnPath(3)`, `CreatePathSegment(1)`, `GetApproximateMinMaxTile(3)`, `GetCrossPointByTroopLineAndBlackRange(2)`, `GetMar... |
| `Util.TimeBarUtil` | 3 | - | `CheckIsNeedChangeBar(4)`, `CheckIsNeedChangeText(2)`, `__tostring(1)` |
| `Util.TroopPowerLimitUtil` | 20 | DC:AllianceBaseDataManager,ArmyFormationDataManager,WorldMarchDataManager | `CheckFormationPower(3)`, `GetFormationPower(1)`, `GetNoRallyFormationTip(0)`, `GetRallyCategory(2)`, `GetRallyDisplayText(1)`,... |
| `Util.UILinkUtil` | 3 | - | `ProcessLinkClick(3)`, `RegisterHandler(2)`, `__tostring(1)` |
| `Util.UIStrCache` | 5 | - | `PromptView_BarText(1)`, `PromptView_ItemIcon(1)`, `PromptView_PText(1)`, `PromptView_Z(1)`, `PromptView_ZText(1)` |
| `Util.UIUtil` | 230 | MSG:MsgDefines.AllianceMoveCity,MsgDefines.DispatchReward,MsgDefines.FreeBuil... | `BuildUpgrade(1)`, `CalcConstructMilePointer(5)`, `CalcConstructMilePointerIgnoreInView(4)`, `CalcMilePointer(3)`, `CalculateAr... |
| `Util.WebUtil` | 0 | - |  |
| `Util.WorldBuildUtil_SLG` | 51 | DC:ActBlackKnightManager,ActDragonManager,AllianceBaseDataManager | `CheckActBalckning(1)`, `CheckInRange(3)`, `CheckInRangeByPointId(3)`, `CheckIsInBasementRange(1)`, `CheckIsInBuildRange(5)`, `... |
| `Util.ZendeskUtil` | 10 | MSG:MsgDefines.JwtFunction ; EV:HideZendeskWindow ; UI:UIPCWebView | `InitSDK(0)`, `IsShowDebugButton(1)`, `IsUnlock(0)`, `Login(1)`, `LoginForGame(1)`, `OnGetUnreadCount(1)`, `RealShowMessage(0)`... |

### Core Framework, Common & Global Runtime (136 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `Common.FloatingTextHelper` | 10 | - | `ClearAll(0)`, `ClearDamageTextQueues(0)`, `CreateFloatText(5)`, `CreateFloatTextWithColor(9)`, `IsNewSystemEnabled(0)`, `SetEn... |
| `Framework.Render.RenderSetting` | 51 | - | `AddUpdater(0)`, `DumpSphericalHarmonicsL2(0)`, `GetAfterSceneUIOpaqueFeatureState(0)`, `GetAfterSceneUITransparentFeatureState... |
| `Framework.UI.Message.EventId` | 1 | - | `__tostring(1)` |
| `Global.App` | 45 | - | `ClearOldAssetBundles(1)`, `EnableVulkanForNextLaunch(1)`, `GetAnalyticID(0)`, `GetDeviceUid(0)`, `GetFromCountry(0)`, `GetLang... |
| `Global.Cache` | 4 | - | `Animator_StringToHash(1)`, `GetState0xString(1)`, `GetStatexString(1)`, `Init(0)` |
| `Global.Config` | 0 | - |  |
| `Global.ConstDefine` | 1 | - | `__tostring(1)` |
| `Global.EnumType` | 1 | - | `__tostring(1)` |
| `Global.GameDialogDefine` | 1 | - | `__tostring(1)` |
| `Global.LazyTemplate` | 6 | - | `getIntValue(2)`, `getValue(2)`, `get_meta_value(2)`, `get_value(2)`, `set_lazy_parser(3)`, `set_meta_value(4)` |
| `Global.ListenerHandler` | 7 | - | `AddDelayEvent(3)`, `AddListener(3)`, `RemoveAllDelayEvents(1)`, `RemoveAllListeners(1)`, `RemoveListener(2)`, `__delete(1)`, `... |
| `Global.Localization` | 10 | - | `GetLanguage(0)`, `GetLanguageName(0)`, `GetLocalCv(0)`, `GetLocalCvName(0)`, `GetRealId(1)`, `GetString(2)`, `IsInitDone(0)`, ... |
| `Global.LuaWebRequest` | 14 | - | `DisposeRequest(1)`, `Get(1)`, `OnRequestFailure(2)`, `OnRequestSuccess(2)`, `OnRequestTimeout(1)`, `OnUpdate(1)`, `Post(2)`, `... |
| `Global.MailClassOverride` | 0 | - |  |
| `Global.SceneManager` | 46 | MSG:MsgDefines.LeaveWorld ; EV:SU_ChangeScreen,SU_MainUIReInit,SceneChanged ;... | `ChangeCameraParamTo(2)`, `ChangeToCity(2)`, `ChangeToLastLevel(1)`, `ChangeToLevel(3)`, `ChangeToLevelById(1)`, `ChangeToMainL... |
| `Global.SettingManager` | 32 | - | `GenPrivateKey(2)`, `GetBool(2)`, `GetFloat(2)`, `GetInt(2)`, `GetPrivateBool(2)`, `GetPrivateFloat(2)`, `GetPrivateInt(2)`, `G... |
| `Global.SingletonListenerHandler` | 7 | - | `AddDelayEvent(3)`, `AddListener(3)`, `RemoveAllDelayEvents(1)`, `RemoveAllListeners(1)`, `RemoveListener(2)`, `__delete(1)`, `... |
| `Global.SlgMailResConfigOverride` | 0 | - |  |
| `Global.SlgUIPrefabsOverride` | 0 | - |  |
| `Global.StringLookupTable` | 2 | - | `Get(1)`, `Init(0)` |
| `Global.UIManagerOverrides` | 110 | EV:BeforeCloseUI,CloseUI,OnKeyCodeEscape ; UI:UIAlarm,UIPVEScene,UIParkourBat... | `AddBlur(2)`, `AddListener(1)`, `AddPCPackageParticleSetUp(3)`, `AddPCUIMask(1)`, `AddUIListener(1)`, `AdjustPCPackageBgSize(4)... |
| `SlgEngine.Common.ApsRandom` | 6 | - | `GetSeed(1)`, `Next(2)`, `NextInt(2)`, `SetSeed(2)`, `__delete(1)`, `__init(2)` |
| `SlgEngine.Common.Data.SFSArray` | 49 | - | `Add(2)`, `AddBool(2)`, `AddBoolArray(2)`, `AddByte(2)`, `AddByteArray(2)`, `AddDouble(2)`, `AddDoubleArray(2)`, `AddFloat(2)` ... |
| `SlgEngine.Common.Data.SFSDataSerializer` | 4 | - | `Array2Binary(1)`, `Binary2Array(1)`, `Binary2Object(1)`, `Object2Binary(1)` |
| `SlgEngine.Common.Data.SFSDataType` | 0 | - |  |
| `SlgEngine.Common.Data.SFSObject` | 51 | - | `ContainsKey(2)`, `GetBool(2)`, `GetBoolArray(2)`, `GetByte(2)`, `GetByteArray(2)`, `GetData(2)`, `GetDouble(2)`, `GetDoubleArr... |
| `SlgEngine.Common.FSMachine` | 7 | - | `Add(3)`, `Create(1)`, `Dispose(1)`, `Init(2)`, `Reset(1)`, `Switch(2)`, `Update(2)` |
| `SlgEngine.Common.LocalController` | 33 | - | `GetABTestTableName(2)`, `GetCacheTable(2)`, `GetTableIndex(3)`, `GetTableLength(2)`, `HasColumn(3)`, `HasTableInMem(2)`, `Load... |
| `SlgEngine.Common.LuaDBInterface` | 13 | - | `CreateOneTable(3)`, `ExecuteMultiSQL(3)`, `ExecuteMultiSQLAfter(3)`, `ExecuteSQL(2)`, `ExecuteSQLAfter(2)`, `ExecuteSTMT(4)`, ... |
| `SlgEngine.Common.ObjectPool` | 6 | - | `Clear(2)`, `ClearAll(1)`, `Load(2)`, `Save(2)`, `__delete(1)`, `__init(1)` |
| `SlgEngine.Common.PosConverse` | 2 | - | `ScreenToUIPos(3)`, `WorldToScreenPos(2)` |
| `SlgEngine.Common.StringPool` | 5 | - | `First(1)`, `GetRandom(1)`, `Sequence(1)`, `__delete(1)`, `__init(3)` |
| `SlgEngine.Common.Tools.UnityEngine.Bounds` | 22 | - | `ClosestPoint(2)`, `Contains(2)`, `Destroy(1)`, `Encapsulate(2)`, `Expand(2)`, `Get(1)`, `GetCenter(1)`, `GetMax(2)` *(+14)* |
| `SlgEngine.Common.Tools.UnityEngine.Color` | 17 | - | `Equals(2)`, `FromHex(1)`, `Get(1)`, `GrayScale(1)`, `HSVToRGB(4)`, `Lerp(3)`, `LerpUnclamped(3)`, `RGBToHSV(1)` *(+9)* |
| `SlgEngine.Common.Tools.UnityEngine.Color32` | 17 | - | `Equals(2)`, `FromHex(1)`, `Get(1)`, `GrayScale(1)`, `HSVToRGB(4)`, `Lerp(3)`, `LerpUnclamped(3)`, `RGBToHSV(1)` *(+9)* |
| `SlgEngine.Common.Tools.UnityEngine.LayerMask` | 6 | - | `Get(1)`, `GetMask(0)`, `LayerToName(1)`, `NameToLayer(1)`, `__call(2)`, `__index(2)` |
| `SlgEngine.Common.Tools.UnityEngine.Mathf` | 47 | - | `Abs(0)`, `Acos(0)`, `Approximately(2)`, `Asin(0)`, `Atan(0)`, `Atan2(2)`, `Ceil(0)`, `Clamp(3)` *(+39)* |
| `SlgEngine.Common.Tools.UnityEngine.Plane` | 9 | - | `Get(1)`, `GetDistanceToPoint(2)`, `GetSide(2)`, `Raycast(2)`, `SameSide(3)`, `Set3Points(4)`, `SetNormalAndPosition(3)`, `__ca... |
| `SlgEngine.Common.Tools.UnityEngine.Quaternion` | 35 | - | `Angle(2)`, `AngleAxis(2)`, `Clone(1)`, `Dot(2)`, `Equals(2)`, `Euler(3)`, `EulerToQuat(3)`, `FastLookRotation(2)` *(+27)* |
| `SlgEngine.Common.Tools.UnityEngine.Ray` | 5 | - | `Get(1)`, `GetPoint(2)`, `__call(3)`, `__index(2)`, `__tostring(1)` |
| `SlgEngine.Common.Tools.UnityEngine.RaycastHit` | 5 | - | `Destroy(1)`, `Get(1)`, `GetMask(0)`, `Init(7)`, `__index(2)` |
| `SlgEngine.Common.Tools.UnityEngine.Time` | 5 | - | `GetTimestamp(1)`, `SetDeltaTime(3)`, `SetFixedDelta(2)`, `SetFrameCount(1)`, `SetTimeScale(2)` |
| `SlgEngine.Common.Tools.UnityEngine.Touch` | 4 | - | `Destroy(1)`, `GetMask(0)`, `Init(8)`, `__index(2)` |
| `SlgEngine.Common.Tools.UnityEngine.Vector2` | 35 | - | `Add(2)`, `Angle(2)`, `ClampMagnitude(2)`, `Clone(1)`, `Distance(2)`, `Div(2)`, `Dot(2)`, `FastDistance(2)` *(+27)* |
| `SlgEngine.Common.Tools.UnityEngine.Vector3` | 56 | - | `Add(2)`, `Angle(2)`, `AngleAroundAxis(3)`, `ClampMagnitude(2)`, `Clone(1)`, `ConstNew(3)`, `ConvertFromCS(2)`, `Cross(2)` *(+48)* |
| `SlgEngine.Common.Tools.UnityEngine.Vector4` | 29 | - | `Add(2)`, `Distance(2)`, `Div(2)`, `Dot(2)`, `Get(1)`, `Lerp(3)`, `Magnitude(1)`, `Max(2)` *(+21)* |
| `SlgEngine.Common.Tools.cjson.util` | 10 | - | `GetPersistentDataPath(0)`, `compare_values(2)`, `file_init(0)`, `file_load(1)`, `file_save(2)`, `file_write(1)`, `run_script(2... |
| `SlgEngine.Common.Tools.list` | 18 | - | `clear(1)`, `clone(1)`, `erase(2)`, `find(3)`, `findByIndex(2)`, `findlast(3)`, `head(1)`, `insert(3)` *(+10)* |
| `SlgEngine.Common.Tools.queue` | 1 | - | `new(0)` |
| `SlgEngine.Common.protoc` | 13 | - | `ConvertToBinary(3)`, `addpath(2)`, `compile(3)`, `compilefile(2)`, `error(2)`, `load(3)`, `loadBytes(2)`, `loadfile(2)` *(+5)* |
| `SlgEngine.Framework.Common.FSM` | 10 | - | `AddState(3)`, `ChangeState(2)`, `GetCurState(1)`, `GetStateIndex(1)`, `HandleInput(1)`, `OnUpdate(1)`, `RemoveState(2)`, `Repl... |
| `SlgEngine.Framework.Common.Messenger` | 12 | - | `AddListener(3)`, `Broadcast(2)`, `BroadcastInternal(2)`, `Cleanup(1)`, `DelayBroadcast(3)`, `Dump(1)`, `RemoveListener(3)`, `R... |
| `SlgEngine.Framework.Common.PathUtil` | 2 | - | `GetFileNameWithoutExtension(1)`, `__tostring(1)` |
| `SlgEngine.Framework.Common.Singleton` | 4 | - | `GetInstance(1)`, `Startup(1)`, `__delete(1)`, `__init(1)` |
| `SlgEngine.Framework.Common.Updatable` | 3 | - | `EnableUpdate(2)`, `__delete(1)`, `__init(1)` |
| `SlgEngine.Framework.Common.base64` | 4 | - | `decode(3)`, `encode(3)`, `makedecoder(3)`, `makeencoder(3)` |
| `SlgEngine.Framework.Logger.FileLogger` | 10 | - | `close(0)`, `debug(1)`, `error(1)`, `get_date_str(0)`, `get_time_str(0)`, `info(1)`, `open_log_file(0)`, `set_level(1)` *(+2)* |
| `SlgEngine.Framework.Logger.FireBaseLog` | 3 | - | `CrashlyticsAddLog(1)`, `CrashlyticsSetUserId(1)`, `SetCustomValue(2)` |
| `SlgEngine.Framework.Logger.Logger` | 11 | - | `Debug(0)`, `DebugFormat(1)`, `GetLogLevel(0)`, `Log(0)`, `LogError(0)`, `LogErrorFormat(1)`, `LogFormat(1)`, `LogTable(3)` *(+3)* |
| `SlgEngine.Framework.Logger.PostEventLog` | 2 | - | `Record(1)`, `Track(1)` |
| `SlgEngine.Framework.LuaMono.LuaMonoBase` | 2 | - | `StartCoroutine(2)`, `StopCoroutine(2)` |
| `SlgEngine.Framework.Scene.Component.TouchObjectEventTrigger` | 17 | - | `GetClickType(1)`, `HasComponent(1)`, `SetClickType(2)`, `SetOnBeginDrag(2)`, `SetOnBeginLongTap(2)`, `SetOnClick(2)`, `SetOnDo... |
| `SlgEngine.Framework.UI.Base.UIBaseComponent` | 75 | - | `AddUIEffect(4)`, `DestroyChildNode(1)`, `ForceRefreshParticleSet(1)`, `ForceRefreshSurvivalParticleSet(2)`, `GameObjectDestroy... |
| `SlgEngine.Framework.UI.Base.UIBaseContainer` | 34 | - | `AddComponent(3)`, `AddComponentEx(3)`, `AddNewRecordIfNeeded(2)`, `AddTimerAction(4)`, `AddUIListener(3)`, `AutoDelayInvoke(4)... |
| `SlgEngine.Framework.UI.Base.UIBaseCtrl` | 0 | - |  |
| `SlgEngine.Framework.UI.Base.UIBaseView` | 28 | DC:LWBattleManager | `AddIgnorePath(2)`, `ClearDynamicLoadEffectList(1)`, `CloseSelf(2)`, `ForceRefreshParticleSet(1)`, `ForceRefreshParticleSetForH... |
| `SlgEngine.Framework.UI.Component.CUIList` | 6 | - | `ClearList(1)`, `GetItemByIndex(2)`, `GetItemCount(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetData(6)` |
| `SlgEngine.Framework.UI.Component.CircleImage` | 4 | - | `LoadSprite(3)`, `OnCreate(1)`, `OnDestroy(1)`, `SetIsCircle(2)` |
| `SlgEngine.Framework.UI.Component.GetHDRIntensity` | 3 | - | `Init(2)`, `OnCreate(1)`, `OnDestroy(1)` |
| `SlgEngine.Framework.UI.Component.GridInfinityScrollView` | 10 | - | `Dispose(1)`, `ForceUpdate(1)`, `Init(5)`, `LaterItemByIndex(4)`, `MoveItemByIndex(3)`, `OnCreate(1)`, `OnDestroy(1)`, `Remark(... |
| `SlgEngine.Framework.UI.Component.HorizontalInfinityScrollView` | 6 | - | `ForceUpdate(1)`, `Init(5)`, `MoveItemByIndex(3)`, `OnCreate(1)`, `OnDestroy(1)`, `SetItemCount(2)` |
| `SlgEngine.Framework.UI.Component.UIAnimation` | 5 | - | `Enable(2)`, `OnCreate(1)`, `OnDestroy(1)`, `Play(2)`, `Replay(2)` |
| `SlgEngine.Framework.UI.Component.UIAnimator` | 19 | - | `AddEnterListener(3)`, `AddLoopListener(3)`, `Enable(2)`, `GetAnimationReturnTime(2)`, `GetCurrentAnimatorClipInfo(2)`, `GetFlo... |
| `SlgEngine.Framework.UI.Component.UIBoxCollider2D` | 3 | - | `GetBounds(1)`, `OnCreate(1)`, `OnDestroy(1)` |
| `SlgEngine.Framework.UI.Component.UIButton` | 19 | EV:OnButtonClick | `AddRef(1)`, `Click(1)`, `DecRef(1)`, `GetButtonImageComponent(1)`, `GetColor(1)`, `GetColorRGBA(1)`, `GetParam(1)`, `LoadSprit... |
| `SlgEngine.Framework.UI.Component.UIButton_LongPress` | 16 | - | `AddRef(2)`, `ClickCallback(1)`, `DecRef(1)`, `GetRef(1)`, `LongPressCallback(1)`, `OnCreate(1)`, `OnDestroy(1)`, `RemoveClickA... |
| `SlgEngine.Framework.UI.Component.UICanvas` | 2 | - | `OnCreate(1)`, `OnDestroy(1)` |
| `SlgEngine.Framework.UI.Component.UICanvasGroup` | 7 | - | `DOFade(4)`, `DOKill(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetAlpha(2)`, `SetBlocksRaycasts(2)`, `SetInteractable(2)` |
| `SlgEngine.Framework.UI.Component.UICenterScrollView` | 32 | - | `ClearCells(1)`, `GetChildCount(1)`, `GetHorizontalNormalizedPosition(1)`, `GetIndex(1)`, `GetIsInMove(1)`, `GetVerticalNormali... |
| `SlgEngine.Framework.UI.Component.UICommonHead` | 25 | EV:PlayCloseUIAnim ; UI:UIPlayerInfo ; DC:DecorationDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `GetIsSystemHead(1)`, `HideLoadingAinmation(1)`... |
| `SlgEngine.Framework.UI.Component.UICommonHeadFrameSpine` | 12 | EV:PlayCloseUIAnim ; DC:DecorationDataManager | `ComponentDefine(1)`, `OnAddListener(1)`, `OnCloseUIAnim(2)`, `OnCreate(1)`, `OnDestroy(1)`, `OnDisable(1)`, `OnEnable(1)`, `On... |
| `SlgEngine.Framework.UI.Component.UIDropdown` | 11 | - | `Add(2)`, `AddList(2)`, `Clear(1)`, `GetText(1)`, `GetValue(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetOnValueChanged(2)` *(+3)* |
| `SlgEngine.Framework.UI.Component.UIDynamicLoadEffect` | 6 | - | `AddLoadedEvent(2)`, `IsAllLoaded(1)`, `OnCreate(1)`, `OnDestroy(1)`, `RemoveLoadedEvent(2)`, `TriggerLoadedCallbacks(1)` |
| `SlgEngine.Framework.UI.Component.UIEffect` | 4 | - | `Clear(1)`, `Load(3)`, `OnCreate(1)`, `OnDestroy(1)` |
| `SlgEngine.Framework.UI.Component.UIEmpty4Raycast` | 11 | - | `GetColor(1)`, `GetColorRGBA(1)`, `GetMaterial(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetAlpha(2)`, `SetColor(2)`, `SetColorRGBA(... |
| `SlgEngine.Framework.UI.Component.UIEventTrigger` | 15 | - | `OnBeginDrag(2)`, `OnCreate(1)`, `OnDestroy(1)`, `OnDrag(2)`, `OnDrop(2)`, `OnEndDrag(2)`, `OnLongPress(2)`, `OnPointerClick(2)... |
| `SlgEngine.Framework.UI.Component.UIGridLayoutGroup` | 12 | - | `GetCellSize(1)`, `GetPadding(1)`, `GetSpacing(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetCellSize(2)`, `SetConstraintCount(2)`, `... |
| `SlgEngine.Framework.UI.Component.UIHorizontalOrVerticalLayo...` | 11 | - | `GetPadding(1)`, `GetSpacing(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetAlignment(3)`, `SetChildAlignment(2)`, `SetPaddingBottom(2... |
| `SlgEngine.Framework.UI.Component.UIImage` | 26 | - | `ClearChatImgEx(2)`, `DOFade(3)`, `GetColor(1)`, `GetColorRGBA(1)`, `GetFillAmount(1)`, `GetImage(1)`, `GetMaterial(1)`, `LoadC... |
| `SlgEngine.Framework.UI.Component.UIInput` | 15 | - | `GetPreferredHeight(1)`, `GetText(1)`, `IsEnabled(2)`, `OnCreate(1)`, `OnDestroy(1)`, `Select(1)`, `SetEnable(2)`, `SetInteract... |
| `SlgEngine.Framework.UI.Component.UILayerComponent` | 5 | - | `ChangeOrientation(2)`, `GetActiveInHierarchy(1)`, `GetConfig(1)`, `GetOrderInLayer(1)`, `OnCreate(2)` |
| `SlgEngine.Framework.UI.Component.UILayoutElement` | 11 | - | `GetIgnored(1)`, `GetMinHeight(1)`, `GetMinWidth(1)`, `GetUnityHandler(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetIgnored(2)`, `Se... |
| `SlgEngine.Framework.UI.Component.UIList` | 19 | - | `AddItem(1)`, `AddItems(2)`, `Clear(1)`, `ClearList(1)`, `GetAllItem(1)`, `GetItem(2)`, `GetItemByIndex(2)`, `GetItemCount(1)` ... |
| `SlgEngine.Framework.UI.Component.UIListFixed` | 12 | - | `AddItem(1)`, `AddItems(2)`, `Clear(1)`, `GetAllItem(1)`, `GetItem(2)`, `Init(4)`, `OnCreate(1)`, `OnDestroy(1)` *(+4)* |
| `SlgEngine.Framework.UI.Component.UILoopListLazyView2` | 28 | - | `ClearAllItems(1)`, `ForceUpdate(1)`, `GetCurShowIndexes(1)`, `GetItemCornerPosInViewPort(2)`, `GetShownItemByItemIndex(2)`, `G... |
| `SlgEngine.Framework.UI.Component.UILoopListView2` | 31 | - | `ClearAllItems(1)`, `FinishSnapImmediately(1)`, `ForceUpdate(1)`, `GetCurShowIndexes(1)`, `GetCurSnapNearestItemIndex(1)`, `Get... |
| `SlgEngine.Framework.UI.Component.UINestedScrollRect` | 6 | - | `OnCreate(1)`, `OnDestroy(1)`, `_OnBeginDrag(2)`, `_OnDrag(2)`, `_OnEndDrag(2)`, `_ShouldRoute(2)` |
| `SlgEngine.Framework.UI.Component.UINewTMPText` | 23 | - | `ForceMeshUpdate(1)`, `GetColor(1)`, `GetHeight(1)`, `GetLinkInfo(1)`, `GetText(1)`, `GetTotalCharacterCount(1)`, `GetWidth(1)`... |
| `SlgEngine.Framework.UI.Component.UINewText` | 15 | - | `GetColor(1)`, `GetColorRGBA(1)`, `GetHeight(1)`, `GetText(1)`, `GetUnityText(1)`, `GetWidth(1)`, `OnCreate(1)`, `OnDestroy(1)`... |
| `SlgEngine.Framework.UI.Component.UIOutline` | 4 | - | `OnCreate(1)`, `OnDestroy(1)`, `SetColor(2)`, `SetEnable(2)` |
| `SlgEngine.Framework.UI.Component.UIPlayerHead` | 10 | DC:ShaderEffectManager | `GetSprite(1)`, `LoadSprite(2)`, `OnCreate(1)`, `OnDestroy(1)`, `OnDisable(1)`, `OnEnable(1)`, `SetCustomBigLoadCallback(2)`, `... |
| `SlgEngine.Framework.UI.Component.UIPlayerHeadNew` | 9 | UI:UIOtherPlayerInfo ; DC:DecorationDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnClick(1)`, `OnCreate(1)`, `OnDestroy(1)`, `S... |
| `SlgEngine.Framework.UI.Component.UIRTModel` | 7 | - | `ComponentDefine(1)`, `DataDefine(1)`, `DestroyRender(2)`, `LoadJustOneModel(2)`, `LoadModel(4)`, `OnCreate(1)`, `OnDestroy(1)` |
| `SlgEngine.Framework.UI.Component.UIRawImage` | 17 | - | `DOFade(3)`, `EnableMaterialKeyword(3)`, `GetColor(1)`, `GetColorRGBA(1)`, `GetMaterial(1)`, `GetTexture(1)`, `LoadSprite(4)`, ... |
| `SlgEngine.Framework.UI.Component.UIScrollPage` | 5 | - | `OnCreate(1)`, `OnDestroy(1)`, `PageTo(2)`, `Refresh(2)`, `RefreshByCell(2)` |
| `SlgEngine.Framework.UI.Component.UIScrollRect` | 25 | - | `AddValueChangeListener(2)`, `ClampContentPosY(2)`, `DoTweenMoveToNormalized(3)`, `GetHorizontalNormalizedPosition(1)`, `GetScr... |
| `SlgEngine.Framework.UI.Component.UIScrollView` | 32 | - | `ClearCells(1)`, `GetActualVisibleRange(1)`, `GetChildCount(1)`, `GetHorizontalNormalizedPosition(1)`, `GetIndex(1)`, `GetIsInM... |
| `SlgEngine.Framework.UI.Component.UIScrollViewEx` | 17 | - | `ClearCells(1)`, `GetCellByIndex(2)`, `GetCells(1)`, `GetComponentType(1)`, `OnCellMoveIn(3)`, `OnCellMoveOut(3)`, `OnCreate(2)... |
| `SlgEngine.Framework.UI.Component.UIScrollViewExclusive` | 8 | - | `OnBeginDrag(2)`, `OnCreate(1)`, `OnDestroy(1)`, `OnDrag(2)`, `OnEndDrag(2)`, `ReInit(4)`, `ReInitScrollRect(5)`, `ReInitScroll... |
| `SlgEngine.Framework.UI.Component.UIScrollViewV2` | 28 | - | `ClearCells(1)`, `GetChildCount(1)`, `GetHorizontalNormalizedPosition(1)`, `GetIndex(1)`, `GetVerticalNormalizedPosition(1)`, `... |
| `SlgEngine.Framework.UI.Component.UIShadow` | 5 | - | `AllEnable(2)`, `Enable(2)`, `OnCreate(1)`, `OnDestroy(1)`, `SetAllColor(2)` |
| `SlgEngine.Framework.UI.Component.UISimpleAnimation` | 13 | - | `CrossFade(3)`, `Enable(2)`, `GetAnimationReturnTime(2)`, `HasState(2)`, `IsPlaying(2)`, `OnCreate(1)`, `OnDestroy(1)`, `Play(2... |
| `SlgEngine.Framework.UI.Component.UISlider` | 11 | - | `DOKill(1)`, `DOValue(5)`, `GetValue(1)`, `IsNil(1)`, `OnCreate(1)`, `OnDestroy(1)`, `SetFillColor(2)`, `SetInteractable(2)` *(... |
| `SlgEngine.Framework.UI.Component.UISpine` | 15 | - | `AddAnimation(5)`, `ApplyFreezeState(2)`, `ApplyGrayState(2)`, `ApplyPendingStates(1)`, `ClearTracks(1)`, `IsFreeze(1)`, `IsGra... |
| `SlgEngine.Framework.UI.Component.UITMPDropdown` | 15 | - | `AddWithLocalText(2)`, `AddWithText(2)`, `Clear(1)`, `GetText(1)`, `GetValue(1)`, `LocateSelectedInTemplate(1)`, `OnCreate(1)`,... |
| `SlgEngine.Framework.UI.Component.UITMPInput` | 21 | - | `BindFixIOSTmpInput(2)`, `DeactivateInputField(1)`, `ForceLabelUpdate(1)`, `GetPreferredHeight(1)`, `GetText(1)`, `IsEnabled(2)... |
| `SlgEngine.Framework.UI.Component.UIText` | 18 | - | `GetAlpha(1)`, `GetColor(1)`, `GetColorRGBA(1)`, `GetHeight(1)`, `GetText(1)`, `GetUnityText(1)`, `GetWidth(1)`, `OnCreate(1)` ... |
| `SlgEngine.Framework.UI.Component.UITextMeshProUGUI` | 16 | - | `AddNumAniTimer(2)`, `DeleteNumAniTimer(1)`, `DoNumAni(4)`, `GetColor(1)`, `GetHeight(1)`, `GetLinkInfo(1)`, `GetText(1)`, `Get... |
| `SlgEngine.Framework.UI.Component.UITextMeshProUGUIEx` | 53 | - | `AddPrintTime(2)`, `AddSpeedPrint(1)`, `ForceMeshUpdate(1)`, `GetAlignment(1)`, `GetAlpha(1)`, `GetColor(1)`, `GetColorRGBA(1)`... |
| `SlgEngine.Framework.UI.Component.UIToggle` | 11 | - | `AddRef(1)`, `DecRef(1)`, `GetIsOn(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetAllowSwitchOff(2)`, `SetGroup(2)`, `SetInteractable(... |
| `SlgEngine.Framework.UI.Component.UITweenNumberText` | 23 | - | `DataDefine(1)`, `DataDestroy(1)`, `FromNumTweenToNum(7)`, `GetCurNum(1)`, `GetCutNum(2)`, `GetPrefix(1)`, `GetSequence(1)`, `G... |
| `SlgEngine.Framework.UI.Component.UITweenNumberText_TextMeshPro` | 25 | - | `DataDefine(1)`, `DataDestroy(1)`, `FromNumTweenToNum(7)`, `GetCurNum(1)`, `GetCutNum(2)`, `GetPrefix(1)`, `GetSequence(1)`, `G... |
| `SlgEngine.Framework.UI.Component.UIUnlimitedScrollView` | 8 | - | `AddItemWrap(3)`, `ClearItemWraps(1)`, `InsertItemWrap(4)`, `OnCreate(1)`, `OnDestroy(1)`, `RemoveItemWrap(2)`, `SetOnItemMoveI... |
| `SlgEngine.Framework.UI.Message.EventManager` | 11 | - | `AddListener(3)`, `Broadcast(3)`, `ClearCSRef(1)`, `DecreaseCSRef(2)`, `DispatchCSEvent(3)`, `DispatchCSEventSFSObject(3)`, `Ge... |
| `SlgEngine.Framework.UI.SlgUIManager` | 110 | EV:BeforeCloseUI,CloseUI,OnKeyCodeEscape ; UI:UIAlarm,UIPVEScene,UIParkourBat... | `AddBlur(2)`, `AddListener(1)`, `AddPCPackageParticleSetUp(3)`, `AddPCUIMask(1)`, `AddUIListener(1)`, `AdjustPCPackageBgSize(4)... |
| `SlgEngine.Framework.UI.Time.UITimeManager` | 99 | - | `AddDebugTimeOffset(2)`, `CheckIfIsSameWeek(2)`, `DateStrToServerMilliSecond(2)`, `FmtStringToMilliSecond(2)`, `GetBetweenDaysF... |
| `SlgEngine.Framework.UI.UILayer` | 0 | - |  |
| `SlgEngine.Framework.UI.UIManagerDefaults` | 32 | - | `AddBlur(2)`, `ApplyWorldScopeVolume(1)`, `CheckIfIsMainUIOpenOnly(4)`, `DestroyInstanceRequest(2)`, `DestroyWindowByLayer(3)`,... |
| `SlgEngine.Framework.UI.UIRotator` | 12 | UI:MainUI_SU | `ApplyCameraDefineIfNeeded(0)`, `ChangeOrientation(0)`, `GetNeedShowRotationNoticeView(0)`, `GetPortraitValue(0)`, `IsEnabled(0... |
| `SlgEngine.Framework.UI.UIWindow` | 0 | - |  |
| `SlgEngine.Framework.Updater.TimeUpEventId` | 1 | - | `__tostring(1)` |
| `SlgEngine.Framework.Updater.TimeUpManager` | 12 | - | `AddListenerBySimple(11)`, `AddListenerByTimeStamp(6)`, `CheckContains(3)`, `Dispose(1)`, `RemoveAllListener(2)`, `RemoveOneLis... |
| `SlgEngine.Framework.Updater.TimeUper` | 5 | - | `Clear(1)`, `Init(11)`, `Update(7)`, `__delete(1)`, `__init(1)` |
| `SlgEngine.Framework.Updater.Timer` | 10 | - | `ForceOver(1)`, `Init(7)`, `IsOver(1)`, `Pause(1)`, `Reset(1)`, `Resume(1)`, `Start(1)`, `Stop(1)` *(+2)* |
| `SlgEngine.Framework.Updater.TimerManager` | 11 | - | `Cleanup(1)`, `DelayFrameInvoke(4)`, `DelayInvoke(4)`, `DelayNextFrameAction(2)`, `Dispose(1)`, `GetCoTimer(7)`, `GetTimer(7)`,... |
| `SlgEngine.Framework.Updater.UpdateManager` | 7 | - | `AddUpdate(2)`, `Cleanup(1)`, `Dispose(1)`, `RemoveUpdate(2)`, `Startup(1)`, `__delete(1)`, `__init(1)` |

### Generated SLG Engine Modules (`Slg.Generated.*`) (115 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `Slg.Generated.ChristmasLevelRewardPanelGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.GivingRoseLevelRewardCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.GivingRoseLevelRewardPanelGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.MailFoodFestivalEatRecordAttrCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.MailFoodFestivalEatRecordAttrNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.MailFoodFestivalEatRecordGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.MailFoodFestivalEatRecordPlayerCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.MailFoodFestivalEatRecordPlayerNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxGiftCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxGiftViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxItemChristmasGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxPanelChristmasGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxPanelEasterGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxPanelGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRewardOpenViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleChristmasViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleEasterViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleIntroduceNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleItemChristmasGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleRewardPreCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleRewardPreItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleRewardPreNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxRuleViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxScoreBigRewardGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxScoreCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxScoreCellItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxScoreViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxSelectBoxItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxSelectBoxViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxShopCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIBlindBoxShopViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertListCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertListViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertRateCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertRateItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertRateViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertTipViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIConcertViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxExchangeCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxExchangeViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxRewardGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxRewardPreCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxRewardPreRateCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxRewardPreViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxScoreRewardCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxScoreRewardItemGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxScoreRewardViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UICycleBoxViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatBuildCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatBuildInfoCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatBuildInfoNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatBuildListNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatExchangeCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatExchangeRecordCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatExchangeRecordViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatExchangeViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatListCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatListViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatPreviewTipViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRecordCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRecordViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatReserveViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRewardPreviewNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleBuildCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleBuildNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleInfoNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleRewardCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleRewardCellListGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleRewardNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleTableCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleTableNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleTableTimeCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleTableTimeNodeGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatRuleViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatSelfRecordCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatSelfRecordViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIFoodFestivalEatViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIGivingRoses2GiftRecommendViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenBigRewardGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawCardCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawCardViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryDetailViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryGiftReceivedCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryListCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryListViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryLogCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryLogViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawLotteryResultViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawResultViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawRewardCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawRewardLotteryCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenDrawRewardViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenGiftMainGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenGiftRecommendCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenGiftRecommendViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIHalloweenGiftResultViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksGivingGiftRecommendViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarAchievementViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarListCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarListViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarMainRankGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarRankCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarRankViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarRewardCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarRewardViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarScoreCellGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarScoreViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.UIThanksgivingStarViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.WorldCupLevelRewardPanelGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.WorldFoodFestivalEatBuildGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.WorldFoodFestivalEatTableGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |
| `Slg.Generated.WorldNpcCityViewGen` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnAddListener(1)`, `OnCreate(1)`, `OnDestroy(1... |

### PVE Battle Level Engine (`Scene.PVEBattleLevel.*`) (224 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `Scene.PVEBattleLevel.Character.AI.HeroAI` | 19 | DC:BattleLevel | `AttackTarget_Enter(1)`, `CheckSkill(1)`, `Destroy(1)`, `FindEnemy(1)`, `Follow_Enter(1)`, `Follow_Exit(1)`, `Follow_Update(2)`... |
| `Scene.PVEBattleLevel.Character.AI.HeroAutoAI` | 18 | - | `AttackTarget_Enter(1)`, `CheckSkill(1)`, `Destroy(1)`, `FindEnemy(1)`, `FindTarget_Update(2)`, `GetAttackRadius(1)`, `GetModel... |
| `Scene.PVEBattleLevel.Character.AI.HeroMeleeAI` | 1 | - | `CheckFollowFindEnemy(2)` |
| `Scene.PVEBattleLevel.Character.AI.HeroRumbleAI` | 23 | DC:BattleLevel | `AttackTarget_Enter(1)`, `CanStartFollow(1)`, `CheckFollowFindEnemy(2)`, `CheckSkill(1)`, `Destroy(1)`, `FindEnemy(1)`, `Follow... |
| `Scene.PVEBattleLevel.Character.AI.NpcBaseAI` | 11 | DC:BattleLevel | `Destroy(1)`, `OnAIComplete(1)`, `OnStateComplete(3)`, `OnUpdate(2)`, `SetData(3)`, `SetToNearByPos(1)`, `Start(1)`, `Stop(1)` ... |
| `Scene.PVEBattleLevel.Character.AI.NpcBuildAI` | 12 | DC:BattleLevel,BuildManager,GirlBehaviorManager | `Destroy(1)`, `OnUpdate(2)`, `SetData(3)`, `Start(1)`, `__buildEnter(2)`, `__buildUpdate(1)`, `__changeToHammerKnock(1)`, `__ch... |
| `Scene.PVEBattleLevel.Character.AI.NpcCityAI` | 33 | DC:BattleLevel,GirlBehaviorManager | `CanTalk(1)`, `ChangeAction(2)`, `ChangePath(1)`, `CheckDestination(1)`, `CheckRest(1)`, `CheckTalk(1)`, `Collect_Enter(2)`, `D... |
| `Scene.PVEBattleLevel.Character.AI.NpcDefendAI` | 8 | - | `Attack_Enter(1)`, `CheckAttack_Update(2)`, `Destroy(1)`, `FindTarget_Update(2)`, `OnStateComplete(3)`, `SearchEnemyTarget(1)`,... |
| `Scene.PVEBattleLevel.Character.AI.NpcFollowerAI` | 9 | DC:BattleLevel | `Attack_Enter(1)`, `Destroy(1)`, `Follow_Enter(1)`, `Follow_Exit(1)`, `Follow_Update(2)`, `Move_Update(2)`, `OnStateComplete(3)... |
| `Scene.PVEBattleLevel.Character.AI.NpcMovePathAI` | 12 | DC:BattleLevel | `Complete_Enter(1)`, `Destroy(1)`, `Move_Enter(1)`, `Move_Exit(1)`, `Move_Update(2)`, `ParsePath(2)`, `SetData(3)`, `Start(1)` ... |
| `Scene.PVEBattleLevel.Character.AI.NpcRunToPointListAI` | 10 | - | `Complete_Enter(1)`, `Destroy(1)`, `Move_Enter(1)`, `Move_Exit(1)`, `Move_Update(2)`, `ParsePath(2)`, `SetData(3)`, `Start(1)` ... |
| `Scene.PVEBattleLevel.Character.AI.NpcStationWorkerAI` | 13 | DC:BuildManager,SV_MapItemInfoManager | `Destroy(1)`, `DoWhenBackHome(1)`, `OnUpdate(2)`, `SetData(3)`, `Start(1)`, `__buildEnter(2)`, `__changeToHammerKnock(1)`, `__g... |
| `Scene.PVEBattleLevel.Character.AI.PlayerLevelAutoAI` | 23 | EV:SU_PlayerStateDone,SU_PlayerTargetChange,SU_StopPlayerAutoAI ; DC:BattleLevel | `AddListener(3)`, `BeginToAttack(1)`, `BeginToCollect(1)`, `CheckInRange(1)`, `Destroy(1)`, `ExitMode(1)`, `FindEnemy(1)`, `Fin... |
| `Scene.PVEBattleLevel.Character.AI.PlayerSemiAutoAI` | 24 | EV:SU_PlayerTargetChange,SU_TriggerProductBuildBubble ; UI:UIBagPickUp,UIBuil... | `AutoAttack(1)`, `CheckTarget(1)`, `Destroy(1)`, `DoBuild(2)`, `DoCollect(2)`, `DoMove(3)`, `DoTalkNPC(1)`, `FindClosestEdge(5)... |
| `Scene.PVEBattleLevel.Character.AI.PreyAI` | 6 | - | `Destroy(1)`, `Move(2)`, `Move_Enter(1)`, `Move_Exit(1)`, `Move_Update(2)`, `OnStateComplete(3)` |
| `Scene.PVEBattleLevel.Character.AI.ResidentCheerAI` | 14 | DC:BattleLevel,BuildPoliceInsigniaManager,PveNpcTemplateManager | `Destroy(1)`, `GetCityResidentMgr(1)`, `MoveInteractionFinsih(1)`, `OnUpdate(2)`, `SetData(3)`, `ShowBubble(2)`, `ShowBubbleAnd... |
| `Scene.PVEBattleLevel.Character.AI.ResidentDefaultAI` | 4 | - | `Destroy(1)`, `Start(1)`, `Stop(1)`, `__init(3)` |
| `Scene.PVEBattleLevel.Character.AI.ResidentResetAI` | 11 | DC:BattleLevel,BuildPoliceInsigniaManager | `Destroy(1)`, `GetCityResidentMgr(1)`, `MoveFinish(1)`, `OnUpdate(2)`, `RandomPosAndMove(1)`, `SetData(3)`, `Start(1)`, `StartT... |
| `Scene.PVEBattleLevel.Character.AI.ResidentShowBubbleAI` | 8 | DC:BattleLevel,PveNpcTemplateManager | `Destroy(1)`, `GetCityResidentMgr(1)`, `HideBubble(1)`, `OnUpdate(2)`, `ShowBubble(1)`, `Start(1)`, `Stop(1)`, `__init(3)` |
| `Scene.PVEBattleLevel.Character.AI.ZombieAI` | 30 | - | `AttackTarget_Enter(1)`, `AttackTarget_Update(2)`, `CanPatrol(1)`, `CanPause(1)`, `CanVigilance(1)`, `CheckDisengageDistance(2)... |
| `Scene.PVEBattleLevel.Character.AI.ZombieBaseAI` | 14 | - | `BeAttack(1)`, `Destroy(1)`, `FindTarget_Update(2)`, `Move_Enter(1)`, `Move_Exit(1)`, `Move_Update(2)`, `OnStateComplete(3)`, `... |
| `Scene.PVEBattleLevel.Character.BarracksSoliderObj` | 14 | DC:BattleLevel | `AddCSharpComponent(1)`, `CheckAssetPath(1)`, `Destroy(1)`, `InitViewStatusHandler(2)`, `IsRenderVisible(1)`, `OnAnimComplete(1... |
| `Scene.PVEBattleLevel.Character.BonFireBoy.BonFireBoy` | 44 | EV:DroneTimelineShowHeroBubble,PlayEnterAnim ; DC:MainCityAreaDataManager | `AddCSharpComponent(1)`, `BonFireBoyPlayEnterAnim(2)`, `BonFireBoyResetToStart(2)`, `CreateDialogBubble(1)`, `DelayInvoke(3)`, ... |
| `Scene.PVEBattleLevel.Character.BonFireBoy.BonFireBoyBubble` | 14 | - | `Destroy(1)`, `DoDelayAction(3)`, `GetLocalScale(1)`, `LockBubble(2)`, `OnDestroy(1)`, `PlayDialogAction(1)`, `PlayDialogToGate... |
| `Scene.PVEBattleLevel.Character.CharacterBase` | 125 | DC:SV_MapItemInfoManager | `AddListener(3)`, `Attack(2)`, `AttackEnemy(2)`, `BeAttack(3)`, `CanLookAt(1)`, `Create(2)`, `CreateVFX(3)`, `DOMove(3)` *(+117)* |
| `Scene.PVEBattleLevel.Character.CharacterHP` | 16 | MSG:MsgDefines.SU_PvePlayerInfoUpdate,MsgDefines.SU_SurvivalPlayerDead ; EV:S... | `AddBuff(2)`, `AddCurBlood(3)`, `AddHpBar(4)`, `Destroy(1)`, `DestroyHpBar(1)`, `DoBuff(2)`, `GetCurBlood(1)`, `GetMaxBlood(1)`... |
| `Scene.PVEBattleLevel.Character.Component.TeamDialogBubble` | 8 | DC:ActFirstChargeData | `Destroy(1)`, `DoDelayAction(3)`, `DoNextSpeech(1)`, `SetData(2)`, `StopBubblePlay(1)`, `StopDelayAction(1)`, `__delete(1)`, `_... |
| `Scene.PVEBattleLevel.Character.Hero` | 38 | - | `AttackEnemy(3)`, `Destroy(1)`, `DestroyAI(1)`, `DestroySkill(1)`, `GenerateConcentricPosition(4)`, `GetAnimName(3)`, `GetAttac... |
| `Scene.PVEBattleLevel.Character.HeroTower` | 17 | DC:BattleLevel,HeroDataManager | `AddCSharpComponent(1)`, `Destroy(1)`, `GetDefaultAnimName(1)`, `GetGarageIndex(1)`, `GetHeroIndex(1)`, `GetTriggerId(1)`, `Get... |
| `Scene.PVEBattleLevel.Character.LadyRole` | 19 | UI:UIPrograssBar ; DC:BuildManager,BuildTemplateManager | `Destroy(1)`, `DoMove(3)`, `GetAnimatorPath(1)`, `GetDefaultAnimName(1)`, `GetMoveAnimName(1)`, `GetMoveSpeed(1)`, `GetPrefabNa... |
| `Scene.PVEBattleLevel.Character.MainCityHeroObj` | 50 | EV:LWTeamPartnerCreateDone,MainCityHeroObjVisible,SU_PlayerAttack ; DC:Battle... | `AddCSharpComponent(1)`, `AttackEnemy(2)`, `CheckOpenDoor(2)`, `ClearAI(1)`, `Destroy(1)`, `FireWeaponTrackVFX(3)`, `GetAI(1)`,... |
| `Scene.PVEBattleLevel.Character.MistressDailyRewardBubble` | 11 | DC:BattleLevel,SU_MistressEffectManager | `AddListener(1)`, `InitComponent(1)`, `LoadResource(1)`, `OnClick(1)`, `OnUpdate(1)`, `Refresh(1)`, `RemoveListener(1)`, `Reset... |
| `Scene.PVEBattleLevel.Character.Npc` | 68 | EV:SU_UpdateNpcTaskIcon ; UI:UITimeCompeRank ; DC:BattleLevel,BuildBubbleMana... | `AttackEnemy(2)`, `CanBuild(1)`, `CanLookAt(1)`, `CanTalk(1)`, `CheckAndShowCompeBubble(1)`, `CheckAndShowGiftBubble(1)`, `Chec... |
| `Scene.PVEBattleLevel.Character.NpcTaskIcon` | 7 | DC:BattleLevel | `Destroy(1)`, `OnUpdate(2)`, `SetComplete(2)`, `SetRotation(2)`, `UpdateIconActive(1)`, `__init(2)`, `__loadAsset(1)` |
| `Scene.PVEBattleLevel.Character.NpcTower` | 22 | EV:NpcTowerObjVisible | `AddCSharpComponent(1)`, `Destroy(1)`, `FireWeaponTrackVFX(3)`, `GetDefaultAnimName(1)`, `GetPrefabName(1)`, `GetRandomAttackCd... |
| `Scene.PVEBattleLevel.Character.Part.RolePart` | 26 | - | `BindBones(2)`, `Destroy(1)`, `DestroyBasePart(1)`, `DestroyEquip(1)`, `FindBoneByName(3)`, `FindTransformByName(2)`, `GetModel... |
| `Scene.PVEBattleLevel.Character.Player` | 118 | EV:SU_ClickToChangeViewMode,SU_PlayerAttack,SU_PlayerCreateComplete ; UI:UIBa... | `AddBloodEff(1)`, `AddBloodTimer(1)`, `Attack(2)`, `AttackEnemy(2)`, `BeAttack(3)`, `BeginToBuild(1)`, `BeginToPeeOrStool(1)`, ... |
| `Scene.PVEBattleLevel.Character.PlayerAutoAIModule` | 23 | EV:SU_PlayerStateDone,SU_PlayerTargetChange,SU_StopPlayerAutoAI ; DC:BattleLevel | `AddListener(3)`, `BeginToAttack(1)`, `BeginToCollect(1)`, `CheckInRange(1)`, `Destroy(1)`, `ExitMode(1)`, `FindEnemy(1)`, `Fin... |
| `Scene.PVEBattleLevel.Character.PlayerHunger` | 26 | MSG:MsgDefines.SU_PvePlayerInfoUpdate ; EV:SU_PlayerHpChanged,SU_PlayerHunger... | `AddBathe(2)`, `AddPee(2)`, `AddStool(2)`, `BatheChangeHP(1)`, `CheckIdleState(2)`, `Destroy(1)`, `GetBathe(1)`, `GetCurBlood(1... |
| `Scene.PVEBattleLevel.Character.PlayerLevel` | 8 | EV:SU_PlayerLevelUp ; DC:GuideManager | `AddExp(2)`, `Destroy(1)`, `GetAddExp(1)`, `GetCurLevelMaxExp(1)`, `GetExp(1)`, `GetLevel(1)`, `GetNextLevelExp(1)`, `__init(2)` |
| `Scene.PVEBattleLevel.Character.PlayerSkin` | 31 | DC:GuideManager | `Destroy(1)`, `DestroyAllEquip(1)`, `EquipSlotChanged(2)`, `GetPart(2)`, `GetWeaponArc(1)`, `GetWeaponAtkEffect(1)`, `GetWeapon... |
| `Scene.PVEBattleLevel.Character.PlayerTeam` | 38 | EV:LWUpdateMainCityRoleTeam ; DC:BattleLevel,HeroDataManager,LandLockManager | `AddHeroByUuid(3)`, `CheckLod(2)`, `CheckQuestDone(2)`, `CreateArrow(1)`, `CreateDialogBubble(1)`, `Destroy(1)`, `DestroyArrow(... |
| `Scene.PVEBattleLevel.Character.Resident` | 15 | DC:BattleLevel,BuildManager | `CheckNeedCheerAndTalk(1)`, `Cheer(2)`, `ClearAI(1)`, `Destroy(1)`, `GetBuildAndDoorInfo(1)`, `GetCityResidentMgr(1)`, `GetMode... |
| `Scene.PVEBattleLevel.Character.RoleSkin` | 17 | - | `AddPart(3)`, `Destroy(1)`, `GetPart(2)`, `GetPartId(1)`, `GetWeaponArc(1)`, `GetWeaponAtkEffect(1)`, `GetWeaponFireTransform(1... |
| `Scene.PVEBattleLevel.Character.Skill.Action.SkillBaseAction` | 7 | DC:PveSkillTemplateManager | `Complete(1)`, `CreateRangeObject(1)`, `Destroy(1)`, `OnUpdate(2)`, `SetData(2)`, `Start(1)`, `__init(4)` |
| `Scene.PVEBattleLevel.Character.Skill.Action.SkillPrepareAction` | 7 | - | `ClearIndicator(1)`, `Complete(1)`, `CreateIndicator(1)`, `Destroy(1)`, `OnUpdate(2)`, `SetIndicatorData(2)`, `Start(1)` |
| `Scene.PVEBattleLevel.Character.Skill.Action.SkillRangeAction` | 9 | DC:BattleLevel | `ClearEffect(1)`, `Complete(1)`, `Destroy(1)`, `PlayEffect(1)`, `Start(1)`, `__addEvent(1)`, `__onAnimPlayEnd(1)`, `__onAttackD... |
| `Scene.PVEBattleLevel.Character.Skill.Action.SkillSoleAction` | 6 | - | `Complete(1)`, `Start(1)`, `__addEvent(1)`, `__onAnimPlayEnd(1)`, `__onAttackDone(1)`, `__removeEvent(1)` |
| `Scene.PVEBattleLevel.Character.Skill.Range.BaseRange` | 1 | - | `ContainPoint(2)` |
| `Scene.PVEBattleLevel.Character.Skill.Range.FanRange` | 2 | - | `ContainPoint(2)`, `__init(5)` |
| `Scene.PVEBattleLevel.Character.Skill.Range.RectangleRange` | 2 | - | `ContainPoint(2)`, `__init(5)` |
| `Scene.PVEBattleLevel.Character.Skill.Range.RoundRange` | 2 | - | `ContainPoint(2)`, `__init(3)` |
| `Scene.PVEBattleLevel.Character.Skill.Skill` | 11 | DC:PveSkillTemplateManager | `Complete(1)`, `Destroy(1)`, `DestroyActions(1)`, `GetRange(1)`, `OnActionComplete(1)`, `OnUpdate(2)`, `SetTarget(2)`, `Start(1... |
| `Scene.PVEBattleLevel.Character.Skill.SkillEnum` | 0 | - |  |
| `Scene.PVEBattleLevel.Character.Skill.SkillManager` | 10 | - | `AddListener(3)`, `Broadcast(3)`, `Destroy(1)`, `DestroySkillList(1)`, `DoSkill(3)`, `OnSkillComplete(1)`, `OnUpdate(2)`, `Remo... |
| `Scene.PVEBattleLevel.Character.SmileyNpc` | 24 | EV:LW_MainCityAreaFogUpdate ; DC:BattleLevel,GuideManager,MainCityAreaDataMan... | `CheckCityAreaUnlockAnimNpcShowState(1)`, `Destroy(1)`, `GetTopBarPos(1)`, `GetUnlockPara2(1)`, `HideSadFence(1)`, `HideSmileyD... |
| `Scene.PVEBattleLevel.Character.State.CharacterBaseState` | 12 | - | `AllowStopByType(2)`, `ChangeCharacterState(1)`, `Destroy(1)`, `GetType(1)`, `IsOnly(1)`, `OnEnter(1)`, `OnExit(1)`, `OnStateCo... |
| `Scene.PVEBattleLevel.Character.State.CharacterDeadState` | 6 | - | `AllowStopByType(2)`, `ChangeCharacterState(1)`, `Destroy(1)`, `IsOnly(1)`, `OnEnter(1)`, `OnExit(1)` |
| `Scene.PVEBattleLevel.Character.State.CharacterDefaultState` | 7 | - | `ChangeCharacterState(1)`, `Destroy(1)`, `OnEnter(1)`, `OnExit(1)`, `__addEvent(1)`, `__onAnimPlayEnd(1)`, `__removeEvent(1)` |
| `Scene.PVEBattleLevel.Character.State.CharacterMoveTransform...` | 7 | - | `ChangeCharacterState(1)`, `OnEnter(1)`, `OnExit(2)`, `OnUpdate(2)`, `SetData(2)`, `__delete(1)`, `__init(4)` |
| `Scene.PVEBattleLevel.Character.State.CharacterStateManager` | 17 | - | `ChangeCharacterState(1)`, `Destroy(1)`, `ExitCurrentState(1)`, `GetCurrentState(1)`, `GetCurrentStateType(1)`, `GetNextStateTy... |
| `Scene.PVEBattleLevel.Character.State.CharacterStateType` | 0 | - |  |
| `Scene.PVEBattleLevel.Character.Zombie` | 99 | DC:BattleLevel,PveActVFXTemplateManager,PveZombieTemplateManager | `AddHungUpDropItem(1)`, `AttackEnemy(3)`, `BeAttack(3)`, `BeHit(2)`, `BeHitFlash(1)`, `CanPause(1)`, `ChangeState(2)`, `CheckCm... |
| `Scene.PVEBattleLevel.Const` | 0 | - |  |
| `Scene.PVEBattleLevel.ConstModelConfig` | 7 | - | `GetCircleRadius(1)`, `GetMiniMapIconName(1)`, `GetModelHeight(1)`, `GetModelOriginOffset(1)`, `GetModelRadius(1)`, `GetTiles(1... |
| `Scene.PVEBattleLevel.GirlCollect.Bubble.GirlCollectBubbleBase` | 14 | DC:BattleLevel,SV_MapItemInfoManager | `Create(1)`, `Destroy(1)`, `GetCameraZoom(1)`, `GetParentNode(1)`, `GetRewardList(2)`, `GetTarget(1)`, `GetTargetUuid(1)`, `__d... |
| `Scene.PVEBattleLevel.GirlCollect.Bubble.GirlCollectConfirmB...` | 8 | DC:GirlBehaviorManager | `Destroy(1)`, `OnTriggerClick(1)`, `OnTriggerPointerDown(1)`, `OnTriggerPointerUp(1)`, `SetTrigger(5)`, `__getPrefabPath(1)`, `... |
| `Scene.PVEBattleLevel.GirlCollect.Bubble.GirlCollectFreeSpee...` | 9 | MSG:MsgDefines.GirlCollectSpeedUp ; DC:BattleLevel | `Destroy(1)`, `OnTriggerClick(1)`, `OnTriggerPointerDown(1)`, `OnTriggerPointerUp(1)`, `SetTrigger(5)`, `__getPrefabPath(1)`, `... |
| `Scene.PVEBattleLevel.GirlCollect.Bubble.GirlCollectProgress...` | 15 | UI:UISpeed ; DC:BattleLevel | `AddTimer(1)`, `ChangeScale(1)`, `Destroy(1)`, `GetObjMaxScale(1)`, `GetObjScale(1)`, `OnAddSpeedClick(1)`, `OnUpdateFun(1)`, `... |
| `Scene.PVEBattleLevel.GirlCollect.GirlCollectLine` | 8 | DC:BattleLevel | `Create(1)`, `Destroy(1)`, `GetParentNode(1)`, `OnUpdate(1)`, `__destroyAsset(1)`, `__init(2)`, `__loadAssetAsync(1)`, `__onLoa... |
| `Scene.PVEBattleLevel.GirlCollect.GirlCollectManager` | 21 | EV:BuildUpgradeStart ; DC:BattleLevel,BuildManager,BuildQueueManager | `CheckBubbleState(2)`, `CheckGirlNpcForQueue(1)`, `CheckState(1)`, `DeleteDelayTimer(1)`, `GetBubble(3)`, `GetBuildPos(2)`, `Ge... |
| `Scene.PVEBattleLevel.Level.ApsAutoLevel` | 11 | MSG:MsgDefines.StartLandLockPVE ; EV:PveLevelEnter ; UI:UIArenaHistory,UILoMa... | `Destroy(1)`, `DoInitTrigger(1)`, `DoTrigger(2)`, `EnterBattle(2)`, `Exit(3)`, `GetHeroSelectHistory(2)`, `GetTriggerByTriggerI... |
| `Scene.PVEBattleLevel.Level.BaseLevel` | 30 | UI:MainUI_SU | `AddListener(3)`, `AddListeners(1)`, `AddSubModule(2)`, `CreatePlayer(1)`, `Destroy(1)`, `Exit(2)`, `GetCamera(1)`, `GetPlayer(... |
| `Scene.PVEBattleLevel.Level.HeroAutoLevel` | 12 | DC:HeroDataManager | `AddHero(3)`, `CreateTeamPosEffect(1)`, `Destroy(1)`, `DestroyTeamPosEffect(1)`, `Exit(1)`, `IsAutoLevel(1)`, `MovePlayer(4)`, ... |
| `Scene.PVEBattleLevel.Level.HeroLevel` | 13 | MSG:MsgDefines.SU_Pve_Level_Finish ; EV:MainTaskSuccess ; UI:UIPVEResult ; DC... | `AddHero(3)`, `AddListeners(1)`, `CheckHeroBossLevelEnd(1)`, `Destroy(1)`, `Exit(2)`, `IsAutoLevel(1)`, `MovePlayer(4)`, `OnRec... |
| `Scene.PVEBattleLevel.Level.MainLevel` | 17 | EV:SU_ChangeViewHeight ; DC:BuildIdleEffectManager,BuildManager,PayManager | `AddListeners(1)`, `CheckBuildStash(1)`, `CheckEndZombieWave(1)`, `Destroy(1)`, `GetHeroReviveTime(1)`, `Init(1)`, `InitZombieW... |
| `Scene.PVEBattleLevel.Level.NormalLevel` | 10 | MSG:MsgDefines.SU_Pve_Level_Finish ; EV:SU_PlayerCreateComplete ; UI:UIPVESta... | `AddListeners(1)`, `CheckShowLevelDesc(1)`, `Destroy(1)`, `Exit(2)`, `Init(1)`, `OnPlayerCreateComplete(1)`, `Prepare(1)`, `Rem... |
| `Scene.PVEBattleLevel.Level.Object.HeroTeamPosEffect` | 10 | - | `Destroy(1)`, `GetCircleQualityIconPath(2)`, `SetHeroData(2)`, `SetLocalPosition(4)`, `SetLocalScale(2)`, `SetParent(2)`, `SetP... |
| `Scene.PVEBattleLevel.Level.Object.SU_TriggerPoint` | 13 | - | `GetPosition(1)`, `GetRotation(1)`, `GetTilePos(1)`, `GetTriggerId(1)`, `InitData(1)`, `IsMonsterWithHp(1)`, `IsTypeAdventureSu... |
| `Scene.PVEBattleLevel.MainCityArea.MainCityAreaEntity` | 19 | EV:SU_UpdateFeixuDecorate ; DC:BattleLevel,MainCityAreaDataManager | `CheckShowQuyuFeixu(1)`, `CreateBorderEffect(1)`, `CreateHud(1)`, `Destroy(1)`, `DestroyBorderEffect(1)`, `DestroyHud(1)`, `Des... |
| `Scene.PVEBattleLevel.MainCityArea.MainCityAreaEntityHud` | 10 | MSG:MsgDefines.LW_AreaFinish ; DC:ArrowManager,BattleLevel,MainCityAreaDataMa... | `Destroy(1)`, `InitComponent(1)`, `InitComponent2(1)`, `LoadAsync(1)`, `OnClick(1)`, `OnClick2(1)`, `PlayUnlockAnimation(2)`, `... |
| `Scene.PVEBattleLevel.MainCityArea.MainCityAreaEntityMgr` | 16 | EV:UserAreaUnLock ; DC:BattleLevel,MainCityAreaDataManager,MainCityAreaTempla... | `ActiveMainCityAreaHud(2)`, `ClearAllEntities(1)`, `Create(1)`, `CreateAllEntities(1)`, `GetAreaEntity(2)`, `GetRootNode(1)`, `... |
| `Scene.PVEBattleLevel.MapObject.EventAction.EventAction_Base` | 3 | - | `DoAction(1)`, `GetLinkTriggerId(1)`, `__init(2)` |
| `Scene.PVEBattleLevel.MapObject.EventAction.EventAction_DoAn...` | 1 | MSG:MsgDefines.SU_PveTriggerUpdate ; DC:SV_MapItemInfoManager | `DoAction(1)` |
| `Scene.PVEBattleLevel.MapObject.EventAction.EventAction_GetW...` | 1 | MSG:MsgDefines.SU_ItemExchange ; UI:UIGive ; DC:BagGridDataManager | `DoAction(1)` |
| `Scene.PVEBattleLevel.MapObject.EventAction.EventAction_Remo...` | 1 | MSG:MsgDefines.SU_PveTriggerUpdate ; DC:SV_MapItemInfoManager | `DoAction(1)` |
| `Scene.PVEBattleLevel.MapObject.EventAction.EventAction_Remo...` | 1 | MSG:MsgDefines.SU_PveTriggerUpdate ; DC:SV_MapItemInfoManager | `DoAction(1)` |
| `Scene.PVEBattleLevel.MapObject.EventAction.MapObjectEventAc...` | 1 | - | `DoEvent(3)` |
| `Scene.PVEBattleLevel.MapObject.MapObjectEffect` | 13 | DC:BattleLevel | `ClearAllWorldText(1)`, `CreateClickableTip(1)`, `CreateEventPointEffect(3)`, `DestroyClickableTip(1)`, `DestroyEventPointEffec... |
| `Scene.PVEBattleLevel.MapObject.MapObjectEffect_ClickableTip` | 13 | EV:SU_BeginToPlayCollectAnim ; DC:BattleLevel | `AddListener(3)`, `Create(2)`, `CreateTip(1)`, `Destroy(1)`, `InitComponent(1)`, `InitData(1)`, `OnClick(1)`, `RemoveListener(3... |
| `Scene.PVEBattleLevel.MapObject.MapObjectEffect_EventTip` | 14 | EV:SU_BeginToPlayCollectAnim ; DC:BattleLevel | `AddListener(3)`, `CreateEventPointEffect(3)`, `Destroy(1)`, `HideEventPointEffect(1)`, `InitComponent(1)`, `RemoveListener(3)`... |
| `Scene.PVEBattleLevel.MapObject.MapObjectEffect_Select` | 14 | - | `Destroy(1)`, `SetLocalPosition(4)`, `SetLocalScale(2)`, `SetParent(2)`, `SetPosition(4)`, `ShowBlue(1)`, `ShowColor(2)`, `Show... |
| `Scene.PVEBattleLevel.MapObject.MapObjectHpBar` | 6 | - | `Destroy(1)`, `Instantiate(1)`, `RefreshHpbarRatio(1)`, `SetActive(2)`, `SetCurHp(2)`, `__init(4)` |
| `Scene.PVEBattleLevel.MapObject.MapObjectLLDropManager` | 17 | DC:BattleLevel | `AddGuideItem(3)`, `AddItem(2)`, `AddOneItem(2)`, `CheckCarState(3)`, `Destroy(1)`, `FlyToGuideBuildPos(3)`, `FlyToGuidePos(6)`... |
| `Scene.PVEBattleLevel.MapObject.MapObjectManager` | 167 | MSG:MsgDefines.SU_PveTriggerUpdate ; EV:BUILD_IN_VIEW,PlayBonFireAnim,Refresh... | `AddHungUpDropItem(2)`, `AddInteractiveByPointId(2)`, `AddObjToUpdateList(2)`, `BuildLevelUp(2)`, `BuildMove(2)`, `CheckBuildBo... |
| `Scene.PVEBattleLevel.MapObject.MapObjectMoveUtil` | 2 | - | `BackToPool(1)`, `GetMapObjectMoveComponent(0)` |
| `Scene.PVEBattleLevel.MapObject.Object.AllianceHelpFpv` | 24 | DC:BattleLevel,BuildManager,DecorationTemplateManager | `AddDelayTimer(1)`, `CreateModel(1)`, `DOMove(1)`, `DelDelayTimer(1)`, `Delay_CloseTxt(1)`, `Delay_ShowTxt(1)`, `Destroy(1)`, `... |
| `Scene.PVEBattleLevel.MapObject.Object.BonFire.MapObjectBonFire` | 14 | MSG:MsgDefines.SU_PveTriggerUpdate ; DC:BattleLevel,BonFireBoyTemplate,BuildM... | `CheckBoyCanWork(1)`, `Destroy(1)`, `DoDelayAction(3)`, `GetPointId(1)`, `GetPrefabName(1)`, `GetPrefabPath(1)`, `InitComponent... |
| `Scene.PVEBattleLevel.MapObject.Object.Build.Com.Object_Bullet` | 4 | - | `Destroy(1)`, `DoAction(1)`, `Instantiate(1)`, `__init(4)` |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Build` | 146 | MSG:MsgDefines.SU_ZombieBuildingDamage ; EV:BuildObjectShowOpenBoxTimeline,Ho... | `AddBarracksSoliderListener(1)`, `AddGarageListener(1)`, `AddOldObjReq(2)`, `AllowFocus(1)`, `BeAttack(2)`, `BindHealEffect(1)`... |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Build...` | 24 | EV:ClickFarmBuildHide,ShowLoadEditorBuild,StartMoveBuild ; UI:UIPlaceBauble ;... | `CanMove(1)`, `ChangePosByClick(3)`, `ChangeToMoveState(1)`, `ContainsPoint(2)`, `GetParentBuildData(1)`, `GetPointIdx(1)`, `Ge... |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Build...` | 7 | EV:RefreshMyTruck ; DC:LWMyStationDataManager | `Destroy(1)`, `InitComponent(1)`, `OnRefreshMyTruck(1)`, `RemoveAllTruck(1)`, `SetStateOffByIndex(2)`, `SetStateOnByIndex(3)`, ... |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Build_AI` | 4 | DC:BattleLevel | `InitAutoAttack(1)`, `OnUpdate(2)`, `OnUpdate_AutoAttack(2)`, `__init(2)` |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Build...` | 5 | - | `InitComponent(1)`, `IsNeedUpdateModel(1)`, `OnInitComplete(3)`, `SetPosAndRotation(1)`, `UpdateShow(1)` |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Build...` | 6 | EV:CarRefitFinish ; DC:GarageRefitManager | `Destroy(1)`, `DestroyCurGarage(1)`, `GetGaragePrefabPath(1)`, `InitComponent(1)`, `LoadGaragePrefab(1)`, `OnGarageUpdate(1)` |
| `Scene.PVEBattleLevel.MapObject.Object.Build.MapObject_Overlord` | 6 | EV:OverlordDataUpdated ; DC:OverlordManager | `Destroy(1)`, `DestroyModel(1)`, `InitComponent(1)`, `OnOverlordDataUpdated(1)`, `RefreshModel(1)`, `__init(2)` |
| `Scene.PVEBattleLevel.MapObject.Object.HeroSmallPeopleGotBui...` | 6 | DC:BuildManager,HeroDataManager | `Init(5)`, `LoadObj(1)`, `LoadOpenDoor(1)`, `OnDestroy(1)`, `OnUpdate(2)`, `SetPos(2)` |
| `Scene.PVEBattleLevel.MapObject.Object.HeroSmallPeopleHeroObj` | 22 | DC:BattleLevel,BuildManager,HeroDataManager | `Destroy(1)`, `GetObjMaxScale(1)`, `GetObjScale(1)`, `GotoBuild(3)`, `HideBubbleInfo(1)`, `Init(5)`, `InitBubbleScaleZoom(1)`, ... |
| `Scene.PVEBattleLevel.MapObject.Object.HeroSmallPeopleObj` | 21 | UI:UISmallPeopleVisit ; DC:BattleLevel,RewardManager,SmallPeopleDataManager | `Destroy(1)`, `Disappear(3)`, `GetObjMaxScale(1)`, `GetObjScale(1)`, `GetPos(1)`, `Init(7)`, `InitBubbleScaleZoom(1)`, `InitTop... |
| `Scene.PVEBattleLevel.MapObject.Object.HeroSmallPeopleObjMan...` | 35 | EV:SmallPeopleAddNew ; DC:HeroSmallPeopleDataManager,MainCityAreaDataManager,... | `AddListener(3)`, `AddOneHeroObj(2)`, `AddOneObj(2)`, `BuildStationChange(2)`, `CheckNeedShowStartSmallPeople(1)`, `DestroyHero... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectAreaZombie` | 24 | - | `AddListener(3)`, `CheckZombieMoveState(1)`, `Destroy(1)`, `EnterLoop(1)`, `GetPos(1)`, `GetRandomPos(3)`, `InitAI(1)`, `InitMo... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectAreaZombieMa...` | 17 | EV:LW_MainCityAreaUpdateState ; DC:MainCityAreaDataManager | `AddListener(3)`, `AddOneArea(2)`, `AddOneAreaFromConfig(2)`, `AddOneAreaZombie(3)`, `DelayRemoveAndShowEffectOneArea(2)`, `Des... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectBase` | 84 | DC:BattleLevel,BuildUpgradeEffectManager | `AddListener(3)`, `AddOldObject(2)`, `AddToUpdateList(1)`, `BeAttack(2)`, `ClearOldObject(1)`, `CreateGameObject(2)`, `CreateMi... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectBox` | 8 | EV:Survival_GetBagGridData | `Destroy(1)`, `DoActionWhenEmpty(1)`, `GetSelectEffectColor(1)`, `InitComponent(1)`, `RecvEvent(2)`, `ShowCurrentModel_Ex(1)`, ... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectDeadBody` | 13 | EV:Survival_PushUpdateBagGridData | `AddVFXEffect(2)`, `BagGridDataUpdate(1)`, `Destroy(1)`, `Focus(1)`, `GetAniName(4)`, `GetSelectEffectColor(1)`, `InitComponent... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectEmptyItem` | 13 | - | `Destroy(1)`, `GetGatherId(1)`, `GetMiniMapIconName(1)`, `GetObjectType(1)`, `GetPointId(1)`, `GetPrefabPath(1)`, `GetTriggerId... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectFence` | 80 | MSG:MsgDefines.SU_PveTriggerUpdate ; UI:UINoInput,UISmallPeopleBook ; DC:Batt... | `AddListener(3)`, `BuildTimeOfChange(2)`, `ChangeCameraView(2)`, `CheckDoorIsClose(1)`, `CheckDoorIsOpen(2)`, `CheckDoorOnEnter... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectFenceZombie` | 24 | DC:BuildProcessControlManager | `ChangeToIdle(1)`, `ChangeToSmashing(1)`, `ChangeToWalk(1)`, `CheckIsOnLod(1)`, `CheckToNextState(1)`, `Destroy(1)`, `DiedFinis... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectFenceZombieM...` | 26 | DC:BattleLevel,BuildProcessControlManager | `BackToPool(3)`, `DelayInvoker(3)`, `Destroy(1)`, `DestroyAllZombie(1)`, `GetIndex(1)`, `GetObjFromPool(2)`, `GetObjMgr(1)`, `G... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectGarbage` | 9 | DC:BattleLevel | `Destroy(1)`, `InitComponent(1)`, `PlayAnim(2)`, `SetActive(2)`, `SetConfigTriggerState(2)`, `SetDecorateActive(3)`, `StopDelay... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectGoArrow` | 5 | DC:BuildProcessControlManager | `CheckShowObj(1)`, `Destroy(1)`, `HideGoObj(1)`, `Init(1)`, `ShowGoObj(1)` |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectGuideObject` | 13 | EV:GuideSaveFinish ; UI:UITimelineMaskNoInput ; DC:BattleLevel,GuideCityAnimM... | `AddListener(3)`, `CheckShowGuideObject(1)`, `Destroy(1)`, `GetObjMgr(1)`, `HideGuideObject(3)`, `HideZombieFence(1)`, `Init(2)... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectGuideZombie` | 18 | - | `Destroy(1)`, `DiedFinish(1)`, `GetPos(1)`, `GetVector3_1(1)`, `GetVector3_2(1)`, `Init(9)`, `LoadObj(1)`, `MoveFinish(1)` *(+10)* |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectGuideZombieC...` | 9 | - | `Destroy(1)`, `GetVector(1)`, `HideCrater(1)`, `Init(10)`, `InitPos(1)`, `LoadObject(1)`, `OnUpdate(2)`, `SetActive(2)` *(+1)* |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectGuideZombieM...` | 22 | DC:BuildManager,BuildProcessControlManager | `BackToGuidePool(3)`, `DelayInvoker(3)`, `Destroy(1)`, `DiedGuideFinish(4)`, `EndShowZombies(1)`, `GetConfigIndex(1)`, `GetGuid... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectLLDropItem` | 8 | - | `Destroy(1)`, `DropStart(2)`, `FlyToBuild(2)`, `FlyToCar(6)`, `GetState(1)`, `InitRoot(1)`, `SetPos(2)`, `__init(7)` |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectLLFirstPayRe...` | 21 | EV:CheckFlagState ; UI:UIScrollPack ; DC:ActFirstChargeData,BattleLevel,Build... | `AddListener(3)`, `CheckFlagState(1)`, `Destroy(1)`, `FirstPayRewardShowState(2)`, `GetBubblePos(1)`, `GetMinRemainTime(1)`, `G... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectLLFirstPayRe...` | 13 | DC:BattleLevel,BuildManager | `CarLookAt(2)`, `Destroy(1)`, `GetBuildFence(1)`, `GetCarPos(1)`, `Init(2)`, `InitRoot(1)`, `MoveFinish(1)`, `MoveTo(2)` *(+5)* |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectLLHangUp` | 24 | EV:RefreshIntelligence,SU_GuideDone ; UI:UIStoryHangup ; DC:BattleLevel,Guide... | `AddListener(3)`, `ChangeHangUpState(1)`, `Destroy(1)`, `GetHangUpBubblePos(1)`, `GetHangUpRandomBuildPos(1)`, `GetObjMaxScale(... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectLLHangUpCar` | 34 | DC:BattleLevel,LandLockManager | `BackToMainBuild(1)`, `CarDisappear(1)`, `CarLookAt(2)`, `CarShow(1)`, `CheckCanStartHangUpCar(3)`, `ClearCarAnim(1)`, `Destroy... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectLLVip` | 23 | EV:LandLockFinished,VipDataRefresh ; UI:UIPopupPackage ; DC:BattleLevel,Guide... | `AddListener(3)`, `AddUpdateTimer(1)`, `DelayPlayAnim(1)`, `Destroy(1)`, `GetBubblePos(1)`, `GetObjMaxScale(1)`, `GetObjScale(1... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectMoveComponent` | 15 | - | `CallBack(1)`, `Destroy(1)`, `GetPos(2)`, `Init(2)`, `LookAtTarget(2)`, `OnMoving(2)`, `OnUpdate(2)`, `Pause(1)` *(+7)* |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectNewGuideModel` | 7 | MSG:MsgDefines.SU_PveTriggerUpdate ; DC:BattleLevel | `Destroy(1)`, `GetPrefabPath(1)`, `GetTriggerId(1)`, `InitComponent(1)`, `OnPointerClick(1)`, `RegisterPointerClick(1)`, `UnReg... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectNotice` | 21 | EV:GetNoticeList ; UI:UIMainNotice ; DC:WorldNoticeManager | `GetActBubbleHistory(1)`, `GetObjectNoticePos(1)`, `HideBubble(1)`, `Init(2)`, `InitComponents(1)`, `InitTimeText(1)`, `OnBubbl... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectPoliceInsignia` | 12 | EV:PlayerTeamInitFinish,SU_PoliceInsigniaRefresh ; DC:BuildPoliceInsigniaManager | `AddListener(3)`, `CheckNeedShowStartLevelPolice(1)`, `Destroy(1)`, `FlyToUp(2)`, `FlyToUpTopBar(3)`, `GetRandomDropPos(1)`, `I... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectPveRoute` | 27 | EV:GuideTimelineMarker,OpenSyncListener ; DC:BattleLevel,BuildManager,GuideCi... | `AddTriggerEvent(1)`, `CheckDelayAttack(1)`, `CheckDoorOpen(2)`, `Destroy(1)`, `GetBuildFence(1)`, `GetObjMgr(1)`, `GetObjectTy... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectRefreshMonster` | 13 | MSG:MsgDefines.SU_PveTriggerUpdate ; EV:ZombieDead ; DC:BattleLevel,SV_MapIte... | `CheckCreateMonster(2)`, `CheckFinish(1)`, `CreateMonster(2)`, `Destroy(1)`, `GetPrefabPath(1)`, `InitComponent(1)`, `IsWaveCom... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectResource` | 40 | EV:SU_OnTriggerFinish,SU_ToCreateSunShine ; DC:BattleLevel,GirlBehaviorManager | `ClearAnimationVfxTimer(1)`, `CreateMiniMapIcon(1)`, `Destroy(1)`, `DestroyTreeEffect(1)`, `Focus(1)`, `GetGatherId(1)`, `GetMi... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectSkyChange` | 9 | EV:SU_TimeOfDayChange ; DC:BuildManager | `AddListener(3)`, `CheckNeedShowByState(2)`, `CheckNeedShowNightLight(1)`, `HideNightLight(1)`, `Init(2)`, `OnTimeOfChangeDay(2... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectTalkTaskObj` | 26 | UI:UIDetectNpc ; DC:BattleLevel,TalkTaskDataManager | `Destroy(1)`, `GetBubblePos(1)`, `GetGroupId(1)`, `GetObjMaxScale(1)`, `GetObjScale(1)`, `GetPos(1)`, `GetUuid(1)`, `HideArrow(... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectTalkTaskObjM...` | 18 | EV:TalkTaskDataRefresh ; UI:UISmallPeopleReward ; DC:TalkTaskDataManager | `AddListener(3)`, `Destroy(1)`, `GetFirstBubblePos(1)`, `GetTaskObjeListByType(2)`, `GetTaskObjeListByTypeAndIndex(3)`, `Init(2... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectTimeOfChange` | 19 | EV:RefreshBuildMainUpdateStation ; UI:UICompletePoliceStationUpgrade,UINoInpu... | `AddListener(3)`, `CheckOnTimeofChange(3)`, `Destroy(1)`, `GetObjMgr(1)`, `Init(2)`, `InitWeilan(1)`, `LoadMainBuildUpgradeStat... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectWorkingPoint` | 13 | EV:SU_ToCreateSunShine | `Destroy(1)`, `GetGatherId(1)`, `GetObjectType(1)`, `GetPointId(1)`, `GetPrefabName(1)`, `GetPrefabPath(1)`, `GetStateObj(2)`, ... |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectZombieAssail...` | 4 | - | `GetCurBlood(1)`, `GetMaxBlood(1)`, `GetPrefabPath(1)`, `OnInitComplete(3)` |
| `Scene.PVEBattleLevel.MapObject.Object.MapObjectZombieBox` | 21 | DC:BattleLevel | `Destroy(1)`, `DestroyDeadVFX(1)`, `DisableNavMesh(1)`, `EnableCollider(2)`, `Focus(1)`, `GetGatherId(1)`, `GetMiniMapIconName(... |
| `Scene.PVEBattleLevel.MapObject.Object.MonsterLock.MapObject...` | 17 | EV:SU_ChangeViewHeight ; DC:BattleLevel,MonsterLockDataManager,MonsterLockTem... | `AddBubble(1)`, `Destroy(1)`, `GetInfo(1)`, `GetObjectType(1)`, `GetPointId(1)`, `GetPrefabName(1)`, `GetPrefabPath(1)`, `HasOb... |
| `Scene.PVEBattleLevel.MapObject.Object.MonsterLock.MapObject...` | 9 | DC:BattleLevel,MonsterLockDataManager | `InitComponent(1)`, `LoadResource(1)`, `OnClick(1)`, `OnUpdate(1)`, `RefreshTime(1)`, `ResetPositionAndScale(1)`, `SetRotation(... |
| `Scene.PVEBattleLevel.MapObject.Object.MonsterToLevel.MapObj...` | 22 | MSG:MsgDefines.SU_SurvivalMistressExchange ; EV:SU_RefreshItemById ; UI:Unloc... | `CheckBubble(1)`, `CheckCanShowUnlockEffect(2)`, `CheckItemEnouphParticle(1)`, `CreateBubble(1)`, `DestroyBubble(1)`, `DestroyL... |
| `Scene.PVEBattleLevel.MapObject.Object.MonsterToLevel.MapObj...` | 89 | MSG:MsgDefines.ReceiveLandReward,MsgDefines.StartLandLockPVE ; EV:LWCreateBub... | `AdviceToUpgradeBuild(3)`, `CheckAutoGotoCollectReward(1)`, `CheckBubble(1)`, `CheckCanShowUnlockEffect(2)`, `CheckHasLodScript... |
| `Scene.PVEBattleLevel.PveHeroManager` | 18 | MSG:MsgDefines.UserResetPVEHero ; DC:BattleLevel,HeroDataManager | `BanHero(2)`, `ClearBanHeroIds(1)`, `ClearCurHeroes(1)`, `ClearHiredHeroes(1)`, `GetCurHeroes(1)`, `GetHiredHeroByUuid(2)`, `Ge... |
| `Scene.PVEBattleLevel.SU_LevelMgr` | 144 | MSG:MsgDefines.SU_HeartBeat ; EV:LevelSceneLoadDone,OnEnterCity,SU_ChangeView... | `AddCollectPtToList(2)`, `AddShowTriggerid(2)`, `AddUpdateTimer(1)`, `AutoLookat(5)`, `CacheBeforeBattlePos(1)`, `CanConsumeEqu... |
| `Scene.PVEBattleLevel.SubModule.AllianceHelpFpvManager` | 28 | DC:BattleLevel,QueueDataManager | `AddHelpFpvData(2)`, `AddOrUpdateHelpCount(2)`, `AddTestFpv(1)`, `AddTimer(1)`, `DelTimer(1)`, `Destroy(1)`, `DestroyFpv(2)`, `... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelBuilding` | 8 | EV:MapObjectInitOK,SU_RefreshBuildingItem ; DC:BuildManager,FactoryDataManager | `BuildInViewSignal(2)`, `CheckBuilding_102000(3)`, `Init(1)`, `InitBuildingSound(2)`, `OnUpdate(2)`, `RemoveBuilding(2)`, `UnIn... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelCamera` | 94 | EV:OpenSyncListener,SU_PlayerLevelUp,WORLD_CAMERA_CHANGE_POINT ; DC:BattleLev... | `AddAfterUpdate(2)`, `AddIgnoreClamp(1)`, `AutoLookat(5)`, `AutoZoom(4)`, `CameraFollowLookat(3)`, `CanRotation(1)`, `ChangeToV... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelCollisionHandler` | 21 | EV:Barrel_OnEnterMine,Barrel_OnEnterSpiderweb,Barrel_OnExitSpiderweb ; DC:Bat... | `Init(1)`, `OnCameraAniEnter(2)`, `OnCameraAniExit(2)`, `OnCameraLerpSetEnter(4)`, `OnCollisionEnter(5)`, `OnCollisionExit(5)`,... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelFakeModel` | 20 | EV:UICreateFakePlaceBuild ; DC:BattleLevel,BaubleManager,BuildManager | `DestroyConstructMaterial(1)`, `DestroyFakeSubBuilding(1)`, `GetFakeSubBuildPos(1)`, `Init(1)`, `LoadConstructMaterial(1)`, `On... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelFollowCamera` | 11 | DC:BattleLevel | `ChangeOffsetY(1)`, `ChangeViewHeight(1)`, `Destroy(1)`, `GetTempOffset(1)`, `Init(1)`, `InitLevelCameraLookat(2)`, `OnUpdate(1... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelFollowFreeCamera` | 25 | - | `AddTouchEvent(1)`, `Init(1)`, `InitFreeCameraConfig(1)`, `IsFreeEnable(1)`, `IsTouchJoyStickArea(2)`, `OnDragStart(3)`, `OnDra... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelInput` | 33 | EV:CLOSE_LOADEDITORBUILD,HideMarchTip,OnCityInputPointDown ; UI:UIWorldTileUI... | `CanUseInput(1)`, `ClickWorld(1)`, `CloseUIWindows(1)`, `GetClosestPoint(2)`, `GetCurIndex(1)`, `GetIsPointerOverUIObject(1)`, ... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelNet` | 19 | MSG:MsgDefines.SU_PveTriggerUpdate,MsgDefines.SU_ZombieEventFinish,MsgDefines... | `HandleSpecialEnd(3)`, `Init(1)`, `OnBattleMessage(2)`, `OnFinishLevelMessage(2)`, `OnFinishTriggerMessage(2)`, `OnGetStageMess... |
| `Scene.PVEBattleLevel.SubModule.BattleLevelSkyFire` | 2 | - | `__delete(1)`, `__init(1)` |
| `Scene.PVEBattleLevel.SubModule.BattleLevelSkyRain` | 2 | - | `__delete(1)`, `__init(1)` |
| `Scene.PVEBattleLevel.SubModule.BattleLevelSkyTime` | 58 | EV:ChangeSkyTime,SU_TimeOfDayChange ; DC:BattleLevel,BuildManager,BuildProces... | `ApplyCurrentSeason(1)`, `CanShowRaine(1)`, `ChangeSlgTime(1)`, `ChangeWeatherByType(3)`, `CheckShowFire(1)`, `CheckShowRain(1)... |
| `Scene.PVEBattleLevel.SubModule.Env.SoldierWaitForRaiseFlag` | 4 | DC:ActFirstChargeData,GuideManager | `Destroy(1)`, `SetActive(2)`, `Show(1)`, `__init(1)` |
| `Scene.PVEBattleLevel.SubModule.SU_BattleLevelScene` | 12 | EV:QualityChange,SU_LevelSceneCreateDone | `CheckDrawMeshCao(1)`, `Destroy(1)`, `GetDyObjNode(1)`, `GetRootTransform(1)`, `GetSceneName(1)`, `GetStaticMgr(1)`, `Init(1)`,... |
| `Scene.PVEBattleLevel.SubModule.SU_BattleLevel_RoleMgr` | 119 | EV:PlayerTeamInitFinish,SU_GirlUnlock ; DC:BattleLevel,BuildManager,BuildQueu... | `AddBonFireBoy(3)`, `AddCityNpc(2)`, `AddHero(4)`, `AddHeroTower(6)`, `AddMainCityHeroObj(3)`, `AddNpc(6)`, `AddNpcTower(3)`, `... |
| `Scene.PVEBattleLevel.SubModule.SU_CameraEffectManager` | 5 | DC:BattleLevel | `Init(1)`, `SetCameraBlackEffectState(5)`, `SetCameraBlackScreenEffect(7)`, `UnInit(1)`, `UnLoadBlackScreenEffect(1)` |
| `Scene.PVEBattleLevel.SubModule.SU_City_ResidentMgr` | 34 | EV:MapObjectInitOK ; DC:BattleLevel,BuildManager,ChapterTaskManager | `ActiveResident(4)`, `BuildEndLoadEditor(1)`, `BuildStartLoadEditor(2)`, `ChackCanShowTaskBubble(3)`, `CheckObjMgr(1)`, `Cheer(... |
| `Scene.PVEBattleLevel.SubModule.SU_EnvironmentMgr` | 49 | EV:SU_RefreshTerrainDocorate,SU_ZoomAreaUnlock ; DC:BattleLevel,BaubleManager... | `CacheFogParam(1)`, `CheckShowMidAreaDecoration(1)`, `CreateDecoration(2)`, `CreateFogDecoration(2)`, `CreateOutsideDecorate(1)... |
| `Scene.PVEBattleLevel.SubModule.SU_Fog` | 17 | - | `ChangeStage(3)`, `InitFog(1)`, `LoadTexture(3)`, `OnFogLoadComplete(1)`, `PointIndexToFogPos(2)`, `RemoveAll(1)`, `SetFogPrope... |
| `Scene.PVEBattleLevel.SubModule.SU_FogConfig` | 0 | - |  |
| `Scene.PVEBattleLevel.SubModule.SU_LandLockWay` | 12 | EV:SU_DestroyLandLockWay ; DC:LandLockManager | `AddLineDataDFW(1)`, `AddLineDataPrologue(2)`, `Destroy(1)`, `DestroyDFWLine(1)`, `DestroyPrologue(1)`, `GetLandListPrologue(1)... |
| `Scene.PVEBattleLevel.SubModule.SU_ModuleBase` | 7 | - | `AddListener(3)`, `Destroy(1)`, `Init(1)`, `OnUpdate(1)`, `RemoveListener(3)`, `UnInit(1)`, `__init(2)` |
| `Scene.PVEBattleLevel.SubModule.SU_PveHeroManager` | 10 | DC:BattleLevel,BuildManager | `AddHero(2)`, `GetAllHeroPower(1)`, `GetAllTeamWorldPos(2)`, `GetMaxHeroCount(1)`, `GetTeamPos(2)`, `GetTeamTargetPos(4)`, `Ini... |
| `Scene.PVEBattleLevel.SubModule.SU_ZombieWaveMgr` | 16 | EV:SU_TimeOfDayChange,SU_ZombieSiege | `CheckEndZombieWave(1)`, `CheckStarZombieWave(1)`, `CheckSwitch(1)`, `EndZombieWave(1)`, `GetHeroReviveTime(1)`, `Init(1)`, `Is... |
| `Scene.PVEBattleLevel.Timeline.ArenaShowTimeline` | 5 | UI:UITimelineMaskNoInput ; DC:BattleLevel | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `ShowLandLockObj(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BarrelBattlePolicewoman` | 3 | EV:Barrel_MoveTeamToCenter,Barrel_PauseOrResumeUnitAni ; UI:UIGetPolicewoman,... | `OnCreate(3)`, `OnDestroy(1)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BarrelReceptTrailHero` | 6 | EV:Barrel_ToggleFormationHeroLevelBar,Barrel_TryPlayReplaceTrailHero ; UI:UIT... | `DestroyBulletToPool(1)`, `OnCreate(3)`, `OnDestroy(1)`, `OnUpdate(1)`, `PreloadLowBullet(1)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BattleFrontGateTimeline` | 8 | EV:RefreshGuide ; UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildManager,Guid... | `AddListener(1)`, `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `PauseOrResume(2)`, `RemoveListener(1)`, `SetTimeLineContinueP... |
| `Scene.PVEBattleLevel.Timeline.BloodyHandBrothersTimeline` | 4 | UI:UITimelineMaskNoInput ; DC:BattleLevel,MainCityAreaDataManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BloodyHandBrothersTimeline2` | 4 | UI:UITimelineMaskNoInput ; DC:BattleLevel,GuideManager,MainCityAreaDataManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BossRunAwayTimeline` | 3 | UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)` |
| `Scene.PVEBattleLevel.Timeline.BossShowingTimeline` | 5 | UI:UITimelineMaskNoInput ; DC:BattleLevel,SU_EventSystem | `OnCreate(3)`, `OnDestroy(1)`, `SetMainCityCamera(1)`, `ShowFieldZombie(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BuildFenceTimeline` | 6 | UI:UIGuideWaitToBuildFence,UITimelineMaskNoInput ; DC:BattleLevel,GuideManager | `Complete(1)`, `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `PauseOrResume(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BuildHousesTimeline` | 4 | UI:UINewBuildUpgrade,UITimelineMaskNoInput ; DC:BattleLevel,BuildProcessContr... | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.BuildTimeOfChangeTimeline` | 3 | UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildManager,BuildProcessControlMan... | `GetObjMgr(1)`, `OnDestroy(1)`, `ReInit(2)` |
| `Scene.PVEBattleLevel.Timeline.DroneTimeline` | 9 | EV:DroneTimelineShowHeroBubble ; UI:UITimelineMaskNoInput ; DC:BuildManager,G... | `Clear(1)`, `Complete(1)`, `Create(5)`, `OnDestroy(1)`, `ShowHeroBubble(3)`, `StopTimeLineLoop(1)`, `UnlockFogById(2)`, `Update... |
| `Scene.PVEBattleLevel.Timeline.FenceZombieWave` | 4 | UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.GoToTowerTimeline` | 4 | UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildProcessControlManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.HangUpCarTimeline` | 8 | EV:SU_ToggleBuildBubble ; UI:UITimelineMaskNoInput ; DC:BattleLevel,GuideManager | `Complete(1)`, `Create(4)`, `HangUpCarPauseOrResume(2)`, `OnDestroy(1)`, `SetFinishCamera(1)`, `ShowCarDropItem(1)`, `StopTimeL... |
| `Scene.PVEBattleLevel.Timeline.HeroKickDoorTimeline` | 6 | UI:UITimelineMaskNoInput | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `SetDoorVisible(2)`, `SetRoleVisible(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.HeroRescueGirlTimeline` | 6 | UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildProcessControlManager,GuideMan... | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(2)`, `SetBuildVisible(2)`, `SetRoleVisible(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.NpcGetGunTimeline` | 12 | UI:UITimelineMaskNoInput,UI_DayNight ; DC:BattleLevel,BuildManager,BuildProce... | `Complete(1)`, `ComponentDefine(1)`, `GetBubbleList(1)`, `GetCamera(1)`, `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `PauseO... |
| `Scene.PVEBattleLevel.Timeline.RestaurantTimeline` | 6 | UI:UINewBuildUpgrade,UITimelineMaskNoInput ; DC:BattleLevel,BuildManager | `GetBubbleList(1)`, `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `ShowBubble(2)`, `UpdateTimelineMarkerSignal(2)` |
| `Scene.PVEBattleLevel.Timeline.SoldierBuildsTimeline` | 4 | UI:UITimelineMaskNoInput ; DC:BattleLevel,BuildManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `SetParam(3)` |
| `Scene.PVEBattleLevel.Timeline.SoldierRaiseFlagTimeline` | 4 | EV:CheckFlagState,UIMAIN_VISIBLE ; UI:UITimelineMaskNoInput | `OnCreate(3)`, `OnDestroy(1)`, `UpdateTimelineMarkerSignal(2)`, `UseBProcess(1)` |
| `Scene.PVEBattleLevel.Timeline.SoldierRunToDabenTimeline` | 5 | EV:SetFlagRaiseTroopsState,UIMAIN_VISIBLE ; UI:UITimelineMaskNoInput ; DC:Bat... | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `UpdateTimelineMarkerSignal(2)`, `UseBProcess(1)` |
| `Scene.PVEBattleLevel.Timeline.TL_NpcToBuild` | 3 | DC:BuildManager | `CheckBuildStash(1)`, `Complete(1)`, `ComponentDefine(1)` |
| `Scene.PVEBattleLevel.Timeline.TL_ShowZombieComing` | 3 | - | `Complete(1)`, `ComponentDefine(1)`, `ShowFieldZombie(2)` |
| `Scene.PVEBattleLevel.Timeline.TimelineBase` | 32 | EV:SU_ShowHideBuildHpBar ; DC:BattleLevel,GuideManager | `AddEventListener(1)`, `AddUiToCameraStack(2)`, `AddUpdateTimer(1)`, `CheckShowNoviceboot(2)`, `Complete(1)`, `ComponentDefine(... |
| `Scene.PVEBattleLevel.Timeline.TrainingGroundTimeline` | 4 | UI:UITimelineMask,UITimelineMaskNoInput ; DC:BattleLevel,BuildManager | `GetObjMgr(1)`, `OnCreate(3)`, `OnDestroy(1)`, `RefreshBuildSoliderShow(1)` |
| `Scene.PVEBattleLevel.UI.PveHeroHpBar` | 12 | - | `AddUpdateTimer(1)`, `IsActive(1)`, `OnUpdate(2)`, `RemoveUpdateTimer(1)`, `SetActive(2)`, `SetIcon(2)`, `SetVal(4)`, `ShowChan... |
| `Scene.PVEBattleLevel.UI.PveHeroHungerBar` | 6 | DC:BattleLevel,GuideManager | `GetShowIconInfoTab(6)`, `IsShow(1)`, `OnCheck(7)`, `SetActive(2)`, `__delete(1)`, `__init(2)` |
| `Scene.PVEBattleLevel.Utils.BattleLevelCamera_ConfigUtil` | 14 | DC:BuildManager,ChapterTaskManager,QuestTemplateManager | `CheckBuildLevel(2)`, `CheckCurConfig(2)`, `CheckQuestDone(2)`, `GetCameraPosType(1)`, `GetCameraRange(1)`, `GetCurOffsetZoom(1... |
| `Scene.PVEBattleLevel.Utils.MiniMapUtil` | 6 | DC:BattleLevel,SV_MapItemInfoManager | `CreateMiniCircle(4)`, `CreateMiniIcon(1)`, `GetIntersectWithRect(3)`, `IsTaskZoneComplete(1)`, `IsTriggerComplete(1)`, `__tost... |
| `Scene.PVEBattleLevel.Utils.PathFinder` | 10 | - | `FindPath(4)`, `FindValidNavMeshPosition(4)`, `IsUseNavMesh(1)`, `IsValidPos(2)`, `LoadAsync(2)`, `NavMeshPathToPathList(2)`, `... |
| `Scene.PVEBattleLevel.Utils.SU_BuildRoofUtil` | 6 | DC:BattleLevel | `EnterRoom(2)`, `ExitRoom(2)`, `SetRoofActive(3)`, `__findBuildDataByPlayerPos(1)`, `__init(1)`, `__updateCurPlayerStayRoomUuid... |
| `Scene.PVEBattleLevel.Utils.SU_ColliderEventUtil` | 3 | MSG:MsgDefines.SU_PveTriggerUpdate ; DC:BattleLevel,DoGuide | `CheckShowNoviceboot(2)`, `OnTriggerEnter(2)`, `OnTriggerExit(2)` |
| `Scene.PVEBattleLevel.Utils.SU_FieldZombieWave` | 12 | EV:NpcTowerObjVisible,self ; DC:BattleLevel,BuildManager | `CheckSpawners(2)`, `GetRandomPos(5)`, `NewZombie(4)`, `NpcTowerObjVisible(2)`, `OnUpdate(2)`, `OnZombieMoveComplete(4)`, `SetA... |
| `Scene.PVEBattleLevel.Utils.SU_Util` | 17 | MSG:MsgDefines.SU_AreaStart ; DC:BagGridDataManager,BattleLevel,ItemConfig | `ChangeToLevel(2)`, `GenerateConcentricPosition(4)`, `GetAngle(2)`, `GetCurItemConfig(1)`, `GetExistResPath(2)`, `GetItemConfig... |
| `Scene.PVEBattleLevel.Utils.SU_ZombieComing` | 18 | EV:MainCityHeroObjVisible,TeamPlayDialogShow,self ; DC:BattleLevel,LandLockMa... | `CheckStartZombieComing(1)`, `GetRandomPos(1)`, `InitData(1)`, `IsZombieComing(1)`, `KillAllZombie(1)`, `MainCityHeroObjVisible... |
| `Scene.PVEBattleLevel.Utils.SearchInfo1` | 11 | DC:BagGridDataManager,BattleLevel,GuideManager | `DoAroundCheck(3)`, `DoAroundCheck2(3)`, `DoCheckAroundObject(2)`, `DoCheckCurrent(4)`, `DoCheckEnemy(2)`, `InitRadius(1)`, `Ob... |
| `Scene.PVEBattleLevel.VFX.BeHitFlashVFX` | 5 | - | `Destroy(1)`, `OnUpdate(2)`, `Play(1)`, `SetMaterialValue(2)`, `__init(2)` |
| `Scene.PVEBattleLevel.VFX.ShieldVFX` | 4 | - | `CheckComplete(1)`, `Destroy(1)`, `InitAsset(1)`, `PlayEnd(1)` |
| `Scene.PVEBattleLevel.VFX.TimerPauseVFX` | 5 | - | `CheckEndPause(1)`, `CheckStartPause(1)`, `ClearTimer(1)`, `Destroy(1)`, `InitAsset(1)` |
| `Scene.PVEBattleLevel.VFX.VFXAutoDestroy` | 2 | - | `OnUpdate(2)`, `__assetCreateComplete(1)` |
| `Scene.PVEBattleLevel.VFX.VFXBase` | 27 | DC:PveVFXTemplateManager | `CheckComplete(1)`, `CompleteEffect(1)`, `Create(1)`, `CreateByPrefabName(2)`, `Destroy(1)`, `GetId(1)`, `GetLazyPosition(1)`, ... |
| `Scene.PVEBattleLevel.VFX.VFXManager` | 9 | - | `CreateVFX(3)`, `Destroy(1)`, `DestroyParticles(1)`, `Init(1)`, `OnUpdate(2)`, `OnVFXComplete(2)`, `RemoveVFX(2)`, `RemoveVFXCa... |
| `Scene.PVEBattleLevel.VFX.WeaponTrackVFX` | 6 | - | `CheckComplete(1)`, `Destroy(1)`, `InitAsset(1)`, `MoveTargetPos(2)`, `OnUpdate(2)`, `SetData(2)` |
| `Scene.PVEBattleLevel.WayPoints.CenterInfo` | 5 | - | `Clear(1)`, `GetRandomWalkingPosition(1)`, `GetWalkingPosition(2)`, `InitPosition(2)`, `__init(1)` |
| `Scene.PVEBattleLevel.WayPoints.CityResidentWayPoint` | 2 | - | `Parse(3)`, `__init(1)` |
| `Scene.PVEBattleLevel.WayPoints.HouseInfo` | 17 | DC:BuildManager | `CanWalking(2)`, `ClearStartBedTempInfo(1)`, `ClearWalkingRoom(1)`, `GetBedInfo(2)`, `GetBedTransform(2)`, `GetRandomWalkingPos... |
| `Scene.PVEBattleLevel.WayPoints.ResidentBuildInfo` | 7 | - | `Destroy(1)`, `FindWayPoints(4)`, `GetRandomPosInfo(3)`, `GetSubBuildByIndex(2)`, `GetUuidByInOrOut(3)`, `InitPosition(2)`, `__... |
| `Scene.PVEBattleLevel.WayPoints.WayPointFinder` | 29 | DC:BuildManager,MainCityAreaDataManager | `FindAnyPath(3)`, `FindBuildingPath(4)`, `FindPath(5)`, `FindWayPoints(4)`, `GetBuildingDoorPos(2)`, `GetDoorWayPoint(2)`, `Get... |

### RedDot Notification & Tutorial Guide Systems (8 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `DataCenter.AllianceData.AllianceRedPointManager` | 4 | DC:AllianceBaseDataManager,AllianceData | `GetRedPotCount(2)`, `GetToggleRedPointCount(2)`, `__delete(1)`, `__init(1)` |
| `Net.Msgs.CarComponRedPointPushMessage` | 2 | DC:GarageComponManager | `HandleMessage(2)`, `OnCreate(1)` |
| `Net.Msgs.ChampionBattleActivity.ChampionPushRedPoint` | 2 | DC:ActChampionBattleManager | `HandleMessage(2)`, `OnCreate(1)` |
| `Net.Msgs.ChampionBattleActivity.PushChampionBattleRedPointM...` | 2 | DC:ActChampionBattleManager | `HandleMessage(2)`, `OnCreate(2)` |
| `Slg.DataCenter.MailDataV4.Manager.MailRedDotManager` | 15 | EV:MailPush ; DC:MailDataV4 | `GetGroupUnread(2)`, `GetTotalUnread(1)`, `GetUnreadCountAll(1)`, `IsAlwaysRead(2)`, `IsNoShowReward(1)`, `MarkGroupRead(2)`, `... |
| `SlgEngine.Net.Msgs.AllianceMilestone.PushAllianceMilestoneR...` | 1 | DC:AllianceMilestoneManager | `HandleMessage(2)` |
| `SlgEngine.Net.Msgs.World.GetAllianceCityRecordRedPointMessage` | 2 | DC:WorldAllianceCityRecordManager | `HandleMessage(2)`, `OnCreate(2)` |
| `UI.RedPoint.RedPoint` | 2 | - | `OnCreate(1)`, `SetCount(2)` |

### Tactical Battle PVE Engine (`Scene.BattlePveModule.*`) (59 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `Scene.BattlePveModule.ActorFireSkillShowHandler` | 24 | EV:UIBarrelHeroFireSkill ; UI:UIBarrelHeroFightTip ; DC:LWSoundManager | `AddBlackMaskForShow(1)`, `AddEventListeners(1)`, `AddShowParamForEmpty(1)`, `CheckCameraState(1)`, `CheckShowSkillFire(1)`, `C... |
| `Scene.BattlePveModule.Const` | 0 | - |  |
| `Scene.BattlePveModule.MailDetailParseModule.PveMailDetailAc...` | 33 | - | `AddSkillTarget(2)`, `GetActionItemType(1)`, `GetActionValue(1)`, `GetDesc(1)`, `GetDesc_AddAnger(1)`, `GetDesc_AddEffect(1)`, ... |
| `Scene.BattlePveModule.MailDetailParseModule.PveMailDetailBu...` | 4 | - | `AddBuffItem(3)`, `ClearData(1)`, `GetBuffListByRoundIndex(2)`, `InitData(1)` |
| `Scene.BattlePveModule.MailDetailParseModule.PveMailDetailRe...` | 16 | - | `AddActionData(4)`, `AddEffectData(3)`, `AnalyseRoundAndEffect(1)`, `ClearData(1)`, `GetActionList(2)`, `GetAtkInfoByIndex(2)`,... |
| `Scene.BattlePveModule.ModelModule.PveModelMgr` | 21 | - | `AddToModelList(3)`, `CreateModel(11)`, `Destroy(1)`, `DoAllBuff(1)`, `GetCreateModelOK(1)`, `GetModelListByCamp(2)`, `GetModel... |
| `Scene.BattlePveModule.ModelModule.SU_ModelObject` | 50 | DC:BattleLevel | `AddBuff(2)`, `BattleInit(1)`, `BeginAttack(1)`, `CreateBloodBar(1)`, `DelayHideHitEffect(1)`, `DelayHideShield(2)`, `Destroy(1... |
| `Scene.BattlePveModule.ModelModule.WeaponObject` | 11 | - | `AddWeapon(3)`, `Destroy(1)`, `GetModelResPath(1)`, `GetObjHeroHand(1)`, `GetTransform(1)`, `InitComponent(1)`, `InstantiateObj... |
| `Scene.BattlePveModule.PveActorAttributeLog` | 1 | - | `ShowLog(1)` |
| `Scene.BattlePveModule.PveActorCameraHandler` | 24 | EV:UIBarrelHeroBottomRefreshPos,UIBarrelHeroCameraMove ; DC:BattleLevel,LWBat... | `ClearCameraShakeTween(1)`, `ClearCameraTranslateTween(1)`, `Destroy(1)`, `DestroyCameraCurves(1)`, `GetAnimDuration(1)`, `GetB... |
| `Scene.BattlePveModule.PveActorMgr1` | 185 | MSG:MsgDefines.BeginPvpCaveFight,MsgDefines.GetCrossArenaUserEffect,MsgDefine... | `AddAtkTotalHp(2)`, `AddCarObject(5)`, `AddDefTotalHp(2)`, `AddListener(3)`, `AddUpdateTimer(1)`, `Barrel_SetGamePause(2)`, `Ca... |
| `Scene.BattlePveModule.PveLineup` | 28 | EV:PVE_Lineup_Init_End,PVE_Lineup_LoadOK ; DC:BattleLevel | `Destroy(1)`, `GetEnemyPosPosition(2)`, `GetMyAllPos(1)`, `GetMyPosPosition(2)`, `GetOverlordSkillPos(2)`, `GetRootPos(1)`, `Ge... |
| `Scene.BattlePveModule.PveLineupOverlordToNormalData` | 5 | - | `GetCarNormalPosition(2)`, `GetHeroNormalPosition(3)`, `InitData(2)`, `__delete(1)`, `__init(1)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletA...` | 6 | - | `Destroy(1)`, `GetPosition(1)`, `LogicDie(1)`, `OnShow(1)`, `OnUpdateCollision(1)`, `__init(12)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletBase` | 48 | DC:LWBattleManager,LWSoundManager | `ChangeLayer(2)`, `CheckBelong2Hero(3)`, `CheckDeath(1)`, `CheckShowForTrack(1)`, `CollisionDetection(1)`, `Create(1)`, `Create... |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletC...` | 12 | - | `CalculateBulletPositions(3)`, `CheckBelong2Hero(3)`, `Create(1)`, `CreateOneBullet(3)`, `Destroy(1)`, `GetAreaBombPos(1)`, `Ge... |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletC...` | 4 | - | `Destroy(1)`, `OnShow(1)`, `OnUpdateCollision(1)`, `OnUpdateTransform(1)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletC...` | 1 | - | `OnShow(1)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletF...` | 7 | - | `Destroy(1)`, `GetColliderCenterWorldPos(1)`, `GetPosition(1)`, `LogicDie(1)`, `OnShow(1)`, `OnUpdateTransform(1)`, `__init(12)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletL...` | 7 | - | `Destroy(1)`, `DoCollisionForBullet(1)`, `GetColliderCenterWorldPos(1)`, `GetPosition(1)`, `LogicDie(1)`, `OnShow(1)`, `__init(... |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletM...` | 20 | DC:PveBulletTemplateManager | `AddBullet(2)`, `AddCreator(2)`, `ClearAllSound(1)`, `CreateBulletCreator(4)`, `DealDamage(12)`, `Destroy(1)`, `GetNextObjId(1)... |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletRay` | 12 | - | `Destroy(1)`, `DoCollision(2)`, `DoCollisionForBullet(2)`, `DoCollisionForTarget(2)`, `FindMax(3)`, `FindMin(3)`, `OnShow(1)`, ... |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletS...` | 3 | - | `LogicDie(1)`, `Show(1)`, `__init(13)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletS...` | 4 | - | `Destroy(1)`, `OnShow(1)`, `OnUpdateTransform(1)`, `__init(1)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletS...` | 0 | - |  |
| `Scene.BattlePveModule.PveReportModule.Barrel.Bullet.BulletT...` | 7 | - | `Destroy(1)`, `DoCollisionForBullet(1)`, `DoCollisionForTarget(1)`, `OnShow(1)`, `OnUpdateCollision(1)`, `OnUpdateTransform(1)`... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 8 | UI:UIBarrelCarFightTip ; DC:GarageRefitManager,GuideManager | `ActiveCastSkill(3)`, `Destroy(1)`, `ShowBarrelCarWindow(1)`, `ShowCVSound(1)`, `ShowCarSound(1)`, `SkillAttack(1)`, `SkillStar... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 2 | DC:GarageRefitManager | `__delete(1)`, `__init(5)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 21 | - | `CheckIfTargetBySkillHeroId(2)`, `ComponentDefine(1)`, `ComponentDefineForCarHDModel(1)`, `Destroy(1)`, `DriftingMoveIn(3)`, `G... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 101 | EV:UIBarrelHeroBottomInfo ; UI:UIPVEScene ; DC:LWBattleManager | `AddBuff(3)`, `AddEffectToPlayQueue(2)`, `AddHaloBuff(4)`, `AfterBeAttack(10)`, `AttackEnemy(6)`, `BeAttack(2)`, `CanCreateBull... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 28 | EV:UIBarrelHeroFireSkill | `ActiveCastSkill(3)`, `Attack_Enter(2)`, `Attack_Update(2)`, `CheckIsIdleState(1)`, `CheckIsMoveAI(1)`, `CheckIsSkillState(1)`,... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 52 | DC:HeroDataManager | `CalculateAttack(1)`, `GetAllUnlockSkills(1)`, `GetAnimation(1)`, `GetAttack(1)`, `GetAttackCdStage(1)`, `GetAttackRange(1)`, `... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 11 | - | `AddTimer(3)`, `AddTimerToList(2)`, `Destroy(1)`, `GetTimerFromList(2)`, `Pause(1)`, `RemoveTimerFromList(2)`, `Resume(1)`, `St... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 15 | - | `CanCreateBulletForNormal(1)`, `CheckIfTargetBySkillHeroId(2)`, `ComponentDefine(1)`, `Destroy(1)`, `Die(1)`, `GetFirePoint(1)`... |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 5 | - | `ActiveCastSkill(3)`, `GetTargetGroup(2)`, `OnHeroFire(1)`, `Skill_Exit(1)`, `Skill_Update(2)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.PveReportBarre...` | 1 | - | `__init(5)` |
| `Scene.BattlePveModule.PveReportModule.Barrel.Skill` | 45 | EV:GF_zombie_battle_ult_ready ; DC:LWBuffTemplateManager,LWSoundManager,PveBu... | `Cast(3)`, `CheckCondition(1)`, `CheckTriggerParam(3)`, `CreateBullet(2)`, `DealBulletBuff(2)`, `Destroy(1)`, `ExecuteCastHandl... |
| `Scene.BattlePveModule.PveReportModule.Barrel.SkillManager` | 30 | - | `ActiveCast(4)`, `AddActiveSkill(3)`, `AddHaloSkill(3)`, `AddPassiveSkill(3)`, `AddSkill(5)`, `CheckUltimate(1)`, `DestroyData(... |
| `Scene.BattlePveModule.PveReportModule.Buff.BarrelBuff.BuffBase` | 12 | EV:LWBattleBuffEnd,LWBattleBuffStart | `Destroy(1)`, `End(1)`, `GetTransform(1)`, `OnEnd(1)`, `OnStart(1)`, `OnUpdate(1)`, `PlaySound(1)`, `Reset(1)` *(+4)* |
| `Scene.BattlePveModule.PveReportModule.Buff.BarrelBuff.BuffB...` | 6 | - | `Destroy(1)`, `OnEnd(1)`, `OnStart(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(7)` |
| `Scene.BattlePveModule.PveReportModule.Buff.BarrelBuff.BuffF...` | 4 | - | `OnEnd(1)`, `OnStart(1)`, `__delete(1)`, `__init(7)` |
| `Scene.BattlePveModule.PveReportModule.Buff.BarrelBuff.BuffM...` | 17 | EV:PVEBuffAdded,PVEBuffRemoved ; DC:LWBuffTemplateManager | `AddBuff(3)`, `AddHaloBuff(4)`, `Destroy(1)`, `GetNextUid(1)`, `GetPropertyBuff(2)`, `GetSubTypeBuffCount(2)`, `HasAnyBuffWithT... |
| `Scene.BattlePveModule.PveReportModule.Buff.BarrelBuff.BuffP...` | 6 | - | `Destroy(1)`, `GetPropertyValue(2)`, `OnEnd(1)`, `OnStart(1)`, `__delete(1)`, `__init(7)` |
| `Scene.BattlePveModule.PveReportModule.Buff.PveBuffManager` | 6 | - | `AddBuffs(2)`, `CheckBuffComplete(1)`, `CheckDoBuff(1)`, `Destroy(1)`, `OnUpdate(2)`, `__init(2)` |
| `Scene.BattlePveModule.PveReportModule.Buff.PveReportBuff` | 7 | - | `CheckComplete(1)`, `Destroy(1)`, `DestroyVFX(1)`, `__complete(1)`, `__init(3)`, `__loadEffect(2)`, `__showText(2)` |
| `Scene.BattlePveModule.PveReportModule.EffectObj.EffectObj` | 12 | DC:LWBattleManager | `ChangeLayer(2)`, `CheckIfBelong(3)`, `Destroy(1)`, `MoveTo(4)`, `OnUpdate(1)`, `ResetLayer(1)`, `SetBelongInfo(3)`, `SetLocalS... |
| `Scene.BattlePveModule.PveReportModule.EffectObj.EffectObjMa...` | 12 | - | `Destroy(1)`, `GetEffectObj(2)`, `GetLogic(1)`, `InnerRemove(2)`, `OnUpdate(1)`, `RemoveEffectObj(2)`, `ResetData(1)`, `SetEffe... |
| `Scene.BattlePveModule.PveReportModule.EffectObj.EffectSprite` | 2 | - | `OnUpdate(1)`, `Show(1)` |
| `Scene.BattlePveModule.PveReportModule.PveReportBattle` | 66 | EV:SU_PveReportDoSkill,UIBarrelHeroBottomInfo ; DC:BattleLevel,GarageRefitMan... | `AddCarObject(5)`, `AddEventListeners(1)`, `AddHero(12)`, `AssignHeroHealth(2)`, `AttackEnemy(7)`, `CalculatePowerRatio(3)`, `C... |
| `Scene.BattlePveModule.PveReportModule.PveReportCampData` | 30 | EV:SU_PveReportDoSkill | `AddRoundItem(2)`, `AddSkillDamage(3)`, `AddSkillDamageToAverage(3)`, `AssignNormalDamage(3)`, `CalculateNormalDamage(1)`, `Cal... |
| `Scene.BattlePveModule.PveReportModule.PveReportHeroAI` | 14 | - | `Attack_Enter(1)`, `Attack_Update(2)`, `Destroy(1)`, `DoSkill(1)`, `GetAttackRadius(1)`, `GetEnemy(1)`, `Move_Update(2)`, `OnSt... |
| `Scene.BattlePveModule.PveReportModule.PveReportHeroInfo` | 36 | DC:PveHeroTemplateManager | `CalculateAttack(1)`, `GetAnimation(1)`, `GetAttackCdStage(1)`, `GetAttackRange(1)`, `GetAttackSpeed(1)`, `GetCampType(1)`, `Ge... |
| `Scene.BattlePveModule.PveReportModule.PveReportHeroObject` | 40 | DC:PveActVFXTemplateManager | `AddBuff(2)`, `AttackEnemy(2)`, `BeAttack(2)`, `ChangeSkinPart(2)`, `Destroy(1)`, `Die(1)`, `DoDead(1)`, `DoReportSkill(1)` *(+... |
| `Scene.BattlePveModule.PveReportModule.PveReportItem` | 24 | - | `AddSkillTarget(2)`, `GetBuffTime(1)`, `GetDamage(1)`, `GetHealth(1)`, `GetHeroId(1)`, `GetParam(1)`, `GetRoundIndex(1)`, `GetS... |
| `Scene.BattlePveModule.PveReportModule.PveReportMgr` | 47 | EV:PVEBattleShowLeftBuff | `AddItem(3)`, `AddSkillDamage(3)`, `AssignNormalDamage(5)`, `BattleProgress(10)`, `CalculateAttackRatio(3)`, `CalculationDamage... |
| `Scene.BattlePveModule.PveReportModule.PveReportRound` | 19 | - | `AddItem(2)`, `AddNormalDamage(2)`, `AssignNormalDamage(3)`, `CalculateNormalDamage(1)`, `CalculateSkillDamage(1)`, `CheckAddBu... |
| `Scene.BattlePveModule.SkillModule.Buff` | 6 | - | `DoAction(1)`, `DoAction_Effect(1)`, `DoAction_Show(1)`, `RemoveBuff(1)`, `SetData(2)`, `__init(1)` |
| `Scene.BattlePveModule.SourceLayerRecorder` | 3 | - | `RestoreLayers(1)`, `__delete(1)`, `__init(2)` |
| `Scene.BattlePveModule.UI.BloodBar` | 28 | EV:OnPveHeroCancel ; DC:ArrowManager | `AddUpdateTimer(1)`, `ChangeLevelPos(2)`, `Destroy(1)`, `GetStarBgComponentName(2)`, `GetStarBgPath(2)`, `GetStarComponentName(... |

### World Map & City Scene Engine (`SlgEngine.Scene.*` / `Scene.*`) (242 modules)

| Lua Module | Methods | `MsgDefines` / `EventId` / `UI` / `DataCenter` Links | Sample Methods |
|---|---:|---|---|
| `Scene.AllianPVE.AllianPVEObjectManager` | 14 | EV:LW_CheckBattlePve ; DC:AllianceMemberDataManager,LandLockManager | `Clear(1)`, `GetAllianPVEData(1)`, `Init(1)`, `IsInCondition(2)`, `OnAllianceReresh(1)`, `OnAreaFinished(1)`, `OnCreatePVEBubbl... |
| `Scene.AllianceBossBloodTip.AllianceBossBloodTip` | 10 | DC:AllianceBossManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshSoldierData(1)`, `RefreshSoldierSlider(2)`,... |
| `Scene.AllianceBossBloodTip.AllianceBossBloodTipManager` | 23 | EV:ShowAllianceBossHeadInBattle ; DC:WorldPointManager | `AddListener(1)`, `AddToBloodCacheList(2)`, `ChangeCameraLodSignal(1)`, `GetBloodCacheByUuid(2)`, `HideHeadUI(2)`, `HideTroopHe... |
| `Scene.AllianceWorldMark.AllianceWorldMark` | 21 | DC:WorldFavoDataManager | `BindBtnPressScale(4)`, `CanDeleteMark(1)`, `ComponentDefine(1)`, `DisableEffStart(1)`, `DoTranslate(3)`, `GetDelConfirmDialogI... |
| `Scene.BaubleObject.BaubleObject` | 14 | EV:MapBaubleRefresh ; UI:UIWorldTileUI ; DC:BattleLevel,BaubleManager,BuildBu... | `Create(1)`, `Destroy(1)`, `GetPosition(1)`, `GetPrefabName(1)`, `GetTransform(2)`, `InitComponent(1)`, `LoadCallBack(1)`, `OnC... |
| `Scene.BuildBoxFinishEffect.BuildBoxFinishEffect` | 8 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `RemoveTimer(1)`, `Update(1)`, `Update... |
| `Scene.BuildBoxFinishEffect.BuildBoxFinishEffectManager` | 7 | EV:BuildBoxOpenFinish ; DC:BuildManager | `AddListener(1)`, `BuildBoxOpenFinishSignal(1)`, `RemoveListener(1)`, `RemoveOneEffect(2)`, `ShowOneEffect(4)`, `__delete(1)`, ... |
| `Scene.BuildLabel.BuildLabelTip` | 8 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `Sh... |
| `Scene.BuildLabel.BuildLabelTipManager` | 8 | EV:CheckShowMainBuildLabel ; DC:WorldPointManager | `AddListener(1)`, `BuildInViewSignal(1)`, `BuildOutViewSignal(1)`, `CheckShowEffect(2)`, `RemoveListener(1)`, `RemoveOneEffect(... |
| `Scene.BuildTimeTip.BuildCompleteTip` | 24 | EV:BuildConfirmFinish,BuildLevelUp,SetSimulateState ; DC:BattleLevel,BuildBub... | `AddListener(3)`, `BuildLevelUp(2)`, `CheckIfTimeTipExist(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `D... |
| `Scene.BuildTimeTip.BuildStateIcon` | 22 | DC:ArenaManager,WorldBuildBubbleManager | `CheckShowResourceCount(1)`, `ClearAnim(1)`, `ComponentDestroy(1)`, `GetObjScale(1)`, `Hide(1)`, `InitComponent(1)`, `OnClick(1... |
| `Scene.BuildTimeTip.BuildTimeTip` | 23 | MSG:MsgDefines.QueueCcdMNew ; EV:HideMainUIExtraResource,RefreshResidentOrder... | `ChangeShowTime(1)`, `CheckIfTimeTipExist(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, ... |
| `Scene.BuildTimeTip.BuildTimeTipTrainField` | 16 | - | `CheckIfTimeTipExist(2)`, `CheckTime(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DelA... |
| `Scene.BuildTimeTip.SU_BuildTimeUpgradingTip` | 25 | EV:SU_ChangeViewHeight,UPDATE_BUILD_DATA ; UI:UIWorldTileUI ; DC:BattleLevel,... | `ChangeViewHeightHandler(1)`, `CheckIfTimeTipExist(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDest... |
| `Scene.BuildTimeTip.SceneBuildTimeTipCircle` | 18 | EV:RefreshResidentOrder | `AddTime(1)`, `CheckIfTimeTipExist(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `Delete... |
| `Scene.BuildTrainEffect.BuildTrainCompleteEffect` | 13 | DC:BuildTrainEffectManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer(1)`, `Destroy(1)`, ... |
| `Scene.BuildTrainEffect.BuildTrainTimeFinishEffect` | 10 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `Destroy(1)`, `OnCreate(1)`, `ReInit(2)`, `SetV... |
| `Scene.BuildZoneEffect.BuildZoneMainEffect` | 5 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)` |
| `Scene.BuildZoneEffect.BuildZoneSubEffect` | 5 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)` |
| `Scene.ContinueWinTipsManager.ContinueWinTips` | 12 | DC:ContinueWinDataManager | `AddUpdate(1)`, `ComponentDefine(1)`, `Destroy(1)`, `GetTroopWorldPos(1)`, `OnCreate(3)`, `OnUpdate(1)`, `RemoveUpdate(1)`, `Re... |
| `Scene.ContinueWinTipsManager.ContinueWinTipsManager` | 5 | EV:ShowKillStreak ; DC:WorldMarchDataManager | `Destroy(1)`, `DestroyAllTips(1)`, `HideKillStreak(2)`, `Init(1)`, `ShowKillStreak(2)` |
| `Scene.DragonEffectManager.DragonBuildProtectEffect` | 14 | EV:ShowDragonBuildProtectTime | `AddTimer(1)`, `CheckIsFinish(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer... |
| `Scene.DragonEffectManager.DragonEffectManager` | 12 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `BuildInViewSignal(1)`, `BuildOutViewSignal(1)`, `CheckShowEffect(2)`, `RemoveAllEffect(1)`, `RemoveAllTips(1... |
| `Scene.FogCanUnlockEffect.FogCanUnlockEffect` | 11 | - | `CheckDoAnim(3)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `GetOriginalPos(1)`, `InitEff... |
| `Scene.FoodFestivalHudManager.FoodFestivalEatBuildHudManager` | 10 | EV:ChangeCameraLod ; DC:WorldPointManager | `AddListener(1)`, `CheckShowHud(2)`, `DestroyAll(1)`, `RefreshHud(2)`, `RemoveBuildHud(2)`, `RemoveListener(1)`, `ShowBuildHud(... |
| `Scene.FoodFestivalHudManager.FoodFestivalEatBuildHudUI` | 17 | DC:FoodFestivalEatManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer(1)`, `GetRefreshTab... |
| `Scene.FoodFestivalHudManager.FoodFestivalEatTableHudManager` | 10 | EV:ChangeCameraLod ; DC:WorldPointManager | `AddListener(1)`, `CheckShowHud(2)`, `DestroyAll(1)`, `RefreshHud(2)`, `RemoveListener(1)`, `RemoveTableHud(2)`, `ShowTableHud(... |
| `Scene.FoodFestivalHudManager.FoodFestivalEatTableHudUI` | 16 | DC:FoodFestivalEatManager,ItemTemplateManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer(1)`, `OnCreate(2)`,... |
| `Scene.GhostKingHudManager.GhostKingHudManager` | 12 | EV:ThroneActAllianceCityInView ; DC:WorldPointManager | `BuildInViewSignal(2)`, `BuildOutViewSignal(2)`, `CheckShowEffect(2)`, `OnAddListeners(1)`, `OnEnterCity(1)`, `OnRemoveListener... |
| `Scene.GhostKingHudManager.GhostKingHudUI` | 10 | DC:AllianceCityTemplateManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `RemoveTimer(1)`, `SetEndTime(1)`, `Se... |
| `Scene.GovernmentWorldBubble.GovernmentWorldBubble` | 7 | DC:GovernmentTemplateManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetData(2)` |
| `Scene.GuideAllianceMemberEffect.GuideAllianceMemberEffect` | 7 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)` |
| `Scene.GuideAnimScene.TradePostReplenish` | 13 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `Create(1)`, `DataDefine(1)`, `Destroy(1)`, `DestroyReq(1)`, `GotoTime(2)`, `Pause... |
| `Scene.LWBattle.AI.ZombieCommonAI` | 3 | - | `GetTarget(2)`, `__delete(1)`, `__init(2)` |
| `Scene.LWBattle.Buff.BuffBase` | 11 | EV:LWBattleBuffEnd,LWBattleBuffStart | `Destroy(1)`, `End(1)`, `OnEnd(1)`, `OnStart(1)`, `OnUpdate(1)`, `PlaySound(1)`, `Reset(1)`, `Start(2)` *(+3)* |
| `Scene.LWBattle.Buff.BuffBeTaunt` | 6 | - | `Destroy(1)`, `OnEnd(1)`, `OnStart(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(7)` |
| `Scene.LWBattle.Buff.BuffFiniteSkill` | 4 | - | `OnEnd(1)`, `OnStart(1)`, `__delete(1)`, `__init(7)` |
| `Scene.LWBattle.Buff.BuffManager` | 17 | EV:PVEBuffAdded,PVEBuffRemoved ; DC:LWBuffTemplateManager | `AddBuff(3)`, `AddHaloBuff(4)`, `Destroy(1)`, `GetNextUid(1)`, `GetPropertyBuff(2)`, `GetSubTypeBuffCount(2)`, `HasAnyBuffWithT... |
| `Scene.LWBattle.Buff.BuffProperty` | 6 | - | `Destroy(1)`, `GetPropertyValue(2)`, `OnEnd(1)`, `OnStart(1)`, `__delete(1)`, `__init(7)` |
| `Scene.LWBattle.Buff.BuffSummonSoldiers` | 4 | - | `OnEnd(1)`, `OnStart(1)`, `__delete(1)`, `__init(7)` |
| `Scene.LWBattle.Const` | 0 | - |  |
| `Scene.LWBattle.ParkourBattle.FresnelFlashVFX` | 7 | - | `ClearFlashTween(1)`, `Destroy(1)`, `DoFlash(1)`, `OnUpdate(1)`, `Play(1)`, `SetMaterialValue(2)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.Bucket` | 40 | DC:LWBattleManager,LWTriggerItemTemplateManager | `Attack(2)`, `BeAttack(2)`, `BeImpactFly(2)`, `CancelFlash(1)`, `CheckAttackedByRetreatCar(2)`, `ClearFlashTween(1)`, `ClearSca... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.ColliderMo...` | 13 | DC:LWBattleManager | `Attack(2)`, `CollidEffect(2)`, `DestroyView(1)`, `DisableScroll(1)`, `GetColliderTransform(1)`, `OnCollision(3)`, `OnLoadCompl... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.CommonAIMo...` | 66 | DC:HeroSkillTemplateManager,LWBattleManager,LWSoundManager | `AfterBeAttack(2)`, `BeAttack(2)`, `CanDisableSkeletonNode(1)`, `CancelFlash(1)`, `ChangeToAttack(3)`, `ChangeToPlaneShadow(1)`... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.Component....` | 11 | - | `CollisionDetect(1)`, `Destroy(1)`, `GetBoxColliderOriginSize(1)`, `InitCollider(4)`, `RemoveOnCollide(1)`, `ScaleCollider(2)`,... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.Component....` | 12 | DC:LWBattleManager | `DisableRagdoll(1)`, `DisableRagdollOnly(1)`, `EnableRagdoll(2)`, `InitRagdoll(1)`, `IsValid(1)`, `__delete(1)`, `__enableRagdo... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 18 | DC:LWBattleManager | `CalcProportionalPos(7)`, `IsInvincible(1)`, `LoadAndCalcFallCurve(1)`, `LoadFallZoneDictBySceneInfo(2)`, `OnEnter(1)`, `OnExit... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 5 | - | `OnEnter(3)`, `OnExit(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 8 | DC:LWBattleManager | `ClearHitBackTween(1)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `TryAppendDeathMaterial(2)`, `TryRemoveDeathMaterial(1)`, `__... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 6 | - | `OnEnter(2)`, `OnExit(1)`, `OnTransToSelf(2)`, `OnUpdate(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 7 | DC:LWBattleManager | `Dump(1)`, `OnEnter(1)`, `OnExit(1)`, `OnUpdate(1)`, `WalkAround(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 8 | DC:LWBattleManager | `CheckTargetInSight(1)`, `OnEnter(1)`, `OnExit(1)`, `OnUpdate(1)`, `WalkAround(1)`, `__IfNeedRally(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 6 | - | `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__delete(1)`, `__finish(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 21 | DC:LWBattleManager | `Dump(1)`, `OnEnter(1)`, `OnExit(1)`, `OnTransToSelf(1)`, `OnUpdate(1)`, `__delete(1)`, `__enterDetourMode(2)`, `__exitDetourMo... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 11 | DC:LWBattleManager | `OnEnter(1)`, `OnExit(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(3)`, `__normalEnter(1)`, `__normalUpdate(1)`, `__sprintEnter(1... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 8 | DC:LWBattleManager | `OnEnter(1)`, `OnExit(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(2)`, `__runToRallyPointEnter(1)`, `__runToRallyPointUpdate(1)`... |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.FSM.Common...` | 5 | - | `OnEnter(1)`, `OnExit(1)`, `OnTransToSelf(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.Monster.MonsterImpl.MonsterObj` | 36 | DC:LWBattleManager,LWTriggerItemTemplateManager,PveHeroEffectTemplateManager | `BeAttack(2)`, `BeImpactFly(2)`, `CalcHpByHurt(2)`, `CancelFlash(1)`, `ChangeToQuadShadow(1)`, `ComponentDefine(1)`, `Death(1)`... |
| `Scene.LWBattle.ParkourBattle.ParkourUnit` | 2 | - | `OnUpdate(1)`, `__init(2)` |
| `Scene.LWBattle.ParkourBattle.TriggerEvent.TriggerEnum` | 0 | - |  |
| `Scene.LWBattle.Skill.Skill` | 49 | EV:Barrel_ShowBigBossHitVFX,GF_zombie_battle_ult_ready ; DC:LWBuffTemplateMan... | `AddTimeLimitedBullet(2)`, `Cast(3)`, `CheckCondition(1)`, `CheckTriggerParam(3)`, `CreateBullet(2)`, `DealBulletBuff(2)`, `Des... |
| `Scene.LWBattle.Skill.SkillManager` | 34 | - | `ActiveCast(4)`, `AddActiveSkill(3)`, `AddHaloSkill(3)`, `AddPassiveSkill(3)`, `AddSkill(5)`, `AddTimeLimitedNormalBullet(2)`, ... |
| `Scene.LWBattle.UnitBase` | 77 | DC:LWBattleManager,LWSoundManager | `AddBuff(3)`, `AddHaloBuff(4)`, `AfterBeAttack(2)`, `BeAttack(2)`, `ClearHitEffect(1)`, `ClearMaterialEffect(1)`, `ComponentDef... |
| `Scene.LWBattle.Utils.BarrelUtils` | 10 | DC:LWBattleManager | `CalculateBulletPositions(2)`, `CalculateDamage(6)`, `CalculateHeroDamage(6)`, `GetBezierPoint(4)`, `GetEvenDistributionPointsI... |
| `Scene.LWRailway.PlaneTrain.CoachBubble` | 7 | DC:LWAllyStationDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnClick(1)`, `Refresh(1)`, `SetHead(2)`, `__delete(1)`, `__init(3)` |
| `Scene.LWRailway.PlaneTrain.LocomotiveBubble` | 10 | DC:LWAllyStationDataManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnClick(1)`, `Refresh(1)`, `RemoveTimer(1)`, `SetHead(2)`, `Update... |
| `Scene.LWRailway.PlaneTrain.PlaneCarriage` | 11 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `Destroy(1)`, `GetPrefabPath(1)`, `InitView(1)`, `OnUpdate(2)`, `RefreshView(1)`, ... |
| `Scene.LWRailway.PlaneTrain.PlaneCoach` | 2 | - | `ComponentDefine(1)`, `OnClick(1)` |
| `Scene.LWRailway.PlaneTrain.PlaneLocomotive` | 4 | - | `ComponentDefine(1)`, `Destroy(1)`, `OnClick(1)`, `RefreshView(1)` |
| `Scene.LWRailway.PlaneTrain.PlaneTrain` | 12 | - | `Destroy(1)`, `GetPosition(1)`, `GetPositionIndex(1)`, `Init(1)`, `OnUpdate(1)`, `Refresh(2)`, `SetActive(2)`, `SetLocalPositio... |
| `Scene.LWRailway.Station.LWMyStationManager` | 19 | EV:BUILD_IN_VIEW ; DC:BuildManager,LWMyStationDataManager | `AddListener(1)`, `AddTruckModel(3)`, `DepartureOneTruck(2)`, `Destroy(1)`, `OnExitCity(1)`, `RefreshBubble(2)`, `RefreshRail(2... |
| `Scene.LWRailway.Station.MyRailwayStation` | 6 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `Destroy(1)`, `OnClick(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWRailway.Station.PlatformBubble` | 7 | DC:LWAllyStationDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `Destroy(1)`, `OnClick(1)`, `Refresh(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWRailway.Station.Rail` | 6 | DC:LWAllyStationDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `Destroy(1)`, `OnClick(1)`, `__delete(1)`, `__init(2)` |
| `Scene.LWRailway.Station.TruckStationBubble` | 10 | DC:LWMyStationDataManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `Destroy(1)`, `OnClick(1)`, `OnUpdateSec(1)`, `Refresh(1)`, `Remove... |
| `Scene.MonsterRewardBoxEffect.MonsterRewardBoxEffect` | 8 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `RemoveTimer(1)`, `Update(1)`, `Update... |
| `Scene.MonsterRewardBoxEffect.MonsterRewardBoxEffectManager` | 7 | EV:MonsterRewardCreate | `AddListener(1)`, `MonsterRewardCreateSignal(1)`, `RemoveListener(1)`, `RemoveOneEffect(2)`, `ShowOneEffect(2)`, `__delete(1)`,... |
| `Scene.NoticeTipsManager.NoticeTipsManager` | 14 | EV:ShowActBossOpen,UI_SHOWNOTICE ; UI:UINoticeTips,UIWorldRuinsPopUp ; DC:Bui... | `AddItem(2)`, `CheckNotice(1)`, `CheckShowAllianceCityTip(6)`, `Clear(1)`, `DeleteTime(1)`, `GetNotice(3)`, `NetPush(2)`, `OnUp... |
| `Scene.ParkScene.ParkScene` | 19 | - | `AddListeners(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(2)`, `DataDestroy(1)`, `Destroy(1)`, `DestroyScene(... |
| `Scene.Pinball.BallBatchController` | 14 | EV:PinballPlaybackCompleted,PinballPlaybackPaused,PinballPlaybackResumed | `Append(2)`, `Complete(1)`, `Emit(7)`, `EnsureStarted(2)`, `FlushRecycle(2)`, `GetPendingBallCount(1)`, `Pause(1)`, `Resume(1)`... |
| `Scene.Pinball.BallTrajectoryPlayer` | 6 | - | `DispatchFinished(2)`, `Emit(7)`, `Render(3)`, `Step(4)`, `StepEvents(2)`, `new(5)` |
| `Scene.Pinball.PinballBallPool` | 7 | - | `Acquire(2)`, `Destroy(1)`, `GetActiveCount(1)`, `GetFreeCapacity(1)`, `Release(2)`, `ReleaseAll(1)`, `new(5)` |
| `Scene.Pinball.PinballBallView` | 6 | - | `ClearTrails(1)`, `Reset(1)`, `SetActive(2)`, `Set_localPosition(4)`, `Set_localSpin(2)`, `new(2)` |
| `Scene.Pinball.PinballBoardView` | 10 | - | `Bind(1)`, `Handle(3)`, `PlayBumperHit(2)`, `PlayPegHit(2)`, `PlayRewardRingHit(2)`, `PlaySlotEnter(2)`, `PlaySpecialTargetHit(... |
| `Scene.Pinball.PinballClock` | 5 | - | `GetTime(1)`, `Pause(1)`, `Resume(1)`, `Start(3)`, `new(1)` |
| `Scene.Pinball.PinballGame` | 29 | - | `AcquireBatch(2)`, `Append(3)`, `BuildCommands(3)`, `Cleanup(1)`, `ConsumePendingPlay(1)`, `CreateBallPool(1)`, `EnsureUpdate(1... |
| `Scene.Pinball.TrajectoryDecoder` | 6 | - | `Crc32(3)`, `Decode(2)`, `GetTemplate(2)`, `LoadCatalog(2)`, `SetData(2)`, `new(0)` |
| `Scene.RobotBuildTip.RobotBuildTip` | 9 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshShow(4)`, `RemoveTimer(1)`, `StartShowTip(2... |
| `Scene.RobotBuildTip.RobotBuildTipManager` | 7 | DC:BuildBubbleManager,BuildQueueManager | `AddListener(1)`, `RemoveListener(1)`, `RemoveOneEffect(2)`, `ShowBuildRobotTip(2)`, `ShowOneEffect(7)`, `__delete(1)`, `__init... |
| `Scene.SU_PlaceBuildGrid.PlaceBuildGridManager` | 5 | - | `DoDraw(1)`, `RedrawGrid(3)`, `ResetGridData(1)`, `__delete(1)`, `__init(1)` |
| `Scene.SeasonSnowEffectManager.SeasonLoaderBase` | 9 | - | `CheckIsShow(1)`, `GetEffectParentTf(1)`, `GetEffectPath(0)`, `GetScale(0)`, `OnDestroy(1)`, `ToHide(1)`, `ToShow(1)`, `__delet... |
| `Scene.SeasonSnowEffectManager.SeasonSnow2` | 3 | DC:SnowManManager | `CheckIsShow(1)`, `GetEffectPath(0)`, `__init(1)` |
| `Scene.SeasonSnowEffectManager.SeasonSnowEffectManager` | 14 | EV:PveLevelEnter | `AddListener(1)`, `AddUpdate(1)`, `DeleteShowItem(1)`, `OnEnterCity(0)`, `OnEnterWorld(0)`, `OnModelRefresh(0)`, `OnPveLevelEnt... |
| `Scene.SnowCityEffectManager.ClearSnowEffect` | 15 | - | `AddTimer(1)`, `CheckSnowLayer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTime... |
| `Scene.SnowCityEffectManager.GetSnowBallTip` | 16 | - | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer(1)`, `DoTweenAnim(1... |
| `Scene.SnowCityEffectManager.SnowCityEffect` | 16 | DC:WorldPointManager | `AddTimer(1)`, `CheckSnowLayer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTime... |
| `Scene.SnowCityEffectManager.SnowCityEffectManager` | 31 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `BuildInViewSignal(1)`, `BuildOutViewSignal(1)`, `CheckShowClearSnowEffect(2)`, `CheckShowEffect(2)`, `CheckS... |
| `Scene.SnowManChangeSkinEffect.SnowManChangeSkinEffect` | 11 | - | `AddTimer(1)`, `CheckIsFinish(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer... |
| `Scene.SnowManChangeSkinEffect.SnowManChangeSkinEffectManager` | 9 | EV:ShowSnowManChangeSkin | `AddListener(1)`, `RemoveAll(1)`, `RemoveAllTips(1)`, `RemoveCityDomeHideEffect(2)`, `RemoveListener(1)`, `ShowDomeHideEffect(3... |
| `Scene.ThroneBloodManager.ThroneBloodManager` | 14 | EV:ShowThroneArmyHeadUI | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckShowThroneBlood(4)`, `HideThroneArmyHeadUISignal(1)`, `OnEnterCity(1)`, `On... |
| `Scene.ThroneBloodManager.ThroneHeadUI` | 8 | DC:WorldMarchDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)`, `SetHP(3)`, `ShowBloodInfo(4)`, `... |
| `Scene.ThroneHudManager.ThroneHudManager` | 19 | EV:ChangeCameraLod ; DC:WorldPointManager | `BuildInViewSignal(2)`, `BuildOutViewSignal(2)`, `CheckShowEffect(2)`, `DeleteActTimer(1)`, `OnAddListeners(1)`, `OnEnterCity(1... |
| `Scene.ThroneHudManager.ThroneHudUI` | 28 | DC:GovernmentManager,ThroneActManager,WorldAllianceCityDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DeleteOccupyTimer(1)`, `DestroyHeadFrameSpineByPath(2)`, `GameObjectDestroy(2)`, ... |
| `Scene.ThroneTroopHeadManager.ThroneTroopHeadManager` | 16 | EV:ThroneTroopShowHead ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLod(1)`, `CheckShowEffect(2)`, `CreateCacheHeadList(1)`, `HideTroopHeadSignal(1)`, `OnEnterCity(... |
| `Scene.ThroneTroopHeadManager.ThroneTroopHeadUI` | 7 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetHead(2)`, `SetLodType(2)`, `SetLodTypeByMarchIn... |
| `Scene.ThroneWinHudManager.ThroneWinHudManager` | 13 | EV:ChangeCameraLod ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckShowEffect(2)`, `OnEnterCity(0)`, `RemoveAllEffect(1)`, `RemoveAllTips(0)`,... |
| `Scene.ThroneWinHudManager.ThroneWinHudUI` | 18 | - | `AddOneEffect(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DestoryEffect(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(4)`,... |
| `Scene.TroopHeadUI_SLG.TroopHeadUIManager` | 4 | - | `GetTroopHeadUICreateConfig(1)`, `OnHudCreateFailed(2)`, `__delete(1)`, `__init(1)` |
| `Scene.UIGuideTalkScene.UIGuideTalkScene` | 13 | DC:PreloadModelManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer(1)`, `DestroyModel(1)`, `OnCreate(... |
| `Scene.UIGuideTalkScene.UIGuideTalkSceneModel` | 12 | - | `AddIdleTimer(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteIdleTimer(1)`, `GetCl... |
| `Scene.Valentine.ValentineTips` | 7 | - | `ComponentDefine(2)`, `ComponentDestroy(1)`, `DeleteTimer(1)`, `OnCreate(3)`, `OnDestroy(1)`, `ShowPanel(2)`, `ShowTip(2)` |
| `Scene.Valentine.ValentineTipsManager` | 6 | EV:ValentineTipsShow | `AddListener(1)`, `RemoveFeedTips(2)`, `RemoveListener(1)`, `ShowFeedTips(2)`, `__delete(1)`, `__init(1)` |
| `Scene.WorldAllianceBossDamageSlider.WorldAllianceBossDamage...` | 26 | EV:HideAllianceBossHead ; DC:AllianceBossBearManager,AllianceBossManager,Worl... | `AddListener(1)`, `AddToTimeCacheList(2)`, `ChangeCameraLodSignal(1)`, `HideAllianceBossTime(1)`, `HideAllianceBossTimeUI(2)`, ... |
| `Scene.WorldAllianceBossDamageSlider.WorldAllianceBossDamage...` | 9 | DC:AllianceBossManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DeleteTimer(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshTime(1)`, ... |
| `Scene.WorldAllianceBossDamageSlider.WorldAllianceBossNewDam...` | 9 | DC:AllianceBossBearManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DeleteTimer(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshTime(1)`, ... |
| `Scene.WorldAttackPlayerScene.WorldAttackPlayerScene` | 10 | DC:GuideNeedLoadManager | `AddMoveTimer(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteMoveTimer(1)`, `MoveT... |
| `Scene.WorldCanBuildEffect.WorldCanBuildEffect` | 5 | DC:BuildManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(1)` |
| `Scene.WorldCanBuildEffect.WorldCanBuildEffectManager` | 8 | EV:ShowCanBuildEffect | `AddListener(1)`, `HideEffectSignal(1)`, `RemoveEffect(1)`, `RemoveListener(1)`, `ShowEffect(1)`, `ShowEffectSignal(1)`, `__del... |
| `Scene.WorldChristmasActTreeHudManager.WorldChristmasActTree...` | 10 | EV:ChangeCameraLod ; DC:WorldPointManager | `AddListener(1)`, `CheckShowHud(2)`, `DestroyAll(1)`, `RefreshHud(2)`, `RemoveBuildHud(2)`, `RemoveListener(1)`, `ShowBuildHud(... |
| `Scene.WorldChristmasActTreeHudManager.WorldChristmasActTree...` | 11 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `Se... |
| `Scene.WorldCityTip.AlliancePassTip` | 13 | UI:UIWorldDeclareList ; DC:AllianceDeclareWarManager,WorldAllianceCityDataMan... | `CheckCityDeclare(1)`, `OnClick(1)`, `OnClickDeclare(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetAllianceColor(2)`, `SetData(2)`, `... |
| `Scene.WorldCityTip.EdenAllianceCityTip` | 13 | UI:UIWorldDeclareList ; DC:AllianceDeclareWarManager,WorldAllianceCityDataMan... | `CheckCityDeclare(1)`, `OnClick(1)`, `OnClickDeclare(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetAllianceColor(2)`, `SetData(2)`, `... |
| `Scene.WorldCityTip.StrongHoldTip` | 13 | UI:UIWorldDeclareList ; DC:AllianceDeclareWarManager,WorldAllianceCityDataMan... | `CheckCityDeclare(1)`, `OnClick(1)`, `OnClickDeclare(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetAllianceColor(2)`, `SetData(2)`, `... |
| `Scene.WorldCityTip.WorldCityTipManager` | 29 | EV:ChangeCameraLod ; DC:AllianceCityTemplateManager | `AddListener(1)`, `AllianceCityInViewSignal(1)`, `AllianceCityNameChange(1)`, `AllianceCityOutViewSignal(1)`, `AllianceCityRefr... |
| `Scene.WorldDesertBattle.WorldDesertBattleManager` | 17 | EV:ShowDesertAttackHeadUI ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckShowDesertBlood(4)`, `CheckShowDesertHeadEffect(5)`, `HideDesertAttackHeadU... |
| `Scene.WorldDesertBattle.WorldDesertBlood` | 8 | DC:WorldPointManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)`, `SetHP(3)`, `ShowBloodInfo(4)`, `... |
| `Scene.WorldDesertBattle.WorldDesertHeadUI` | 6 | DC:WorldMarchDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `InitInfo(5)`, `OnCreate(2)`, `OnDestroy(1)`, `SetHP(3)` |
| `Scene.WorldDesertBattle.WorldDesertModel` | 12 | DC:WorldMarchDataManager,WorldPointManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `DoAttack(2)`, `DoBorn(1)`, `DoDie(1)`, `OnCreate(2)`, `OnDestroy(1)`, `OnInit(2)`... |
| `Scene.WorldDesertBattle.WorldDesertModelManager` | 21 | EV:ShowDesertSoldierAttack ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `HideDesertSignal(1)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `RemoveAllEffect(1)`,... |
| `Scene.WorldMarchTileUI.WorldMarchTileUI` | 16 | EV:OnClickMarch ; DC:WorldMarchDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `GetMarchUuid(1)`, `OnBtn1Click(1)`, `OnBtn2Click(1)`, `OnBtn3Click(1)`, `OnBtn4Cl... |
| `Scene.WorldMarchTileUI.WorldMarchTileUIManager` | 13 | EV:ArmyFormatUpdate,HideFormationSelect,ShowCreateCrossWormHole ; UI:UIFormat... | `AddListener(1)`, `OnBtnClick(3)`, `OnInputDragBegin(0)`, `OnUpdateMarchSignal(0)`, `OnWorldTroopCreate(1)`, `RefreshTroop(3)`,... |
| `Scene.WorldMoveCityAllGrid_SLG.WorldMoveCityAllGridManager` | 10 | EV:MissileUnlockBuildingChanged ; DC:MissileUnlockManager | `AddListener(1)`, `ClearAllMatrix(1)`, `DrawGrid(1)`, `ReBuildMissileList(1)`, `RemoveListener(1)`, `ResetMissileBuild(1)`, `Sh... |
| `Scene.WorldScene.BattleDecBloodTip` | 5 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ShowDamage(6)` |
| `Scene.WorldScene.BattleDecBloodTipManager` | 14 | EV:PveLevelBeforeEnter | `AddListener(1)`, `ClearAllTips(1)`, `CreateNewTip(7)`, `DestroyTip(2)`, `GetFromPool(1)`, `GetOrCreateTip(7)`, `GetPoolInfo(1)... |
| `Scene.WorldScene.SubModule.FakeModelManager` | 18 | EV:UICreateFakeAllianceBuild,UICreateFakePlaceBuild ; DC:BuildTemplateManager | `AddActionList(4)`, `Init(1)`, `InitMeta(1)`, `InitMetaAction(1)`, `InitPropertyAction(1)`, `IsInMoveCityMode(1)`, `UIChangeAll... |
| `Scene.WorldScene.SubModule.WorldCamera` | 76 | EV:WORLD_CAMERA_CHANGE_POINT | `AddActionList(4)`, `AddAfterUpdateAction(2)`, `AddIgnoreClamp(1)`, `AutoFocus(7)`, `AutoLookat(7)`, `AutoLookatEaseIn(7)`, `Au... |
| `Scene.WorldScene.SubModule.WorldInputManager` | 48 | EV:CLOSE_LOADEDITORBUILD,ChangeCameraLod,OnWorldInputDragBegin ; UI:UIMainMap... | `AddActionList(4)`, `CanUseInput(1)`, `ClickWorld(1)`, `GetClickWorldBulidingPos(1)`, `GetClosestPoint(2)`, `GetHighLodIconCity... |
| `Scene.WorldScene.SubModule.WorldSubModuleBase` | 3 | - | `Init(1)`, `UnInit(1)`, `__init(2)` |
| `Scene.WorldScene.WorldObject.WorldObject_Build` | 13 | EV:UIPlaceBuildChangePos ; UI:UIAllianceRallyOperate | `ChangeShowLayer(1)`, `CheckShowChargeFlag(1)`, `DestroyChargeFlag(1)`, `GetTiles(1)`, `Init(3)`, `OnDrag(2)`, `RefreshData(1)`... |
| `Scene.WorldScene.WorldScene` | 155 | EV:OnLeaveWorld,OnTroopDragonUpdatePos,UpdateWorldTerrain ; UI:UIMainMiniMap ... | `AddActionList(4)`, `AddAutoFace(2)`, `AddAutoScale(2)`, `AddBulletV2(16)`, `AddBulletV2ByPos(16)`, `AddLodAdjuster(2)`, `AddOl... |
| `Scene.WorldShoutManager.WorldShoutInfo` | 9 | - | `GetBadgeWinNums(1)`, `HasAllianceRecruit(1)`, `HasMigrateRecruit(1)`, `ParseRecruitAlliance(2)`, `ParseRecruitServer(2)`, `ToT... |
| `Scene.WorldShoutManager.WorldShoutManager` | 77 | MSG:MsgDefines.GetBroadcastSticky,MsgDefines.SendBroadcastMsg,MsgDefines.SetB... | `AddMessage(2)`, `CalcTopBroadcastRemainSec(2)`, `CheckCanApplyAlliance(2)`, `CheckCanSend(1)`, `CheckCrossServerVisible(2)`, `... |
| `Scene.WorldTroopAttackBuildIcon.WorldTroopAttackBuildIcon` | 8 | - | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)`, `SetShowTime(4)`, ... |
| `Scene.WorldTroopAttackBuildIcon.WorldTroopAttackBuildIconMa...` | 14 | EV:ShowTroopAtkBuildIcon ; DC:WorldMarchDataManager | `AddListener(1)`, `CheckShowEffect(2)`, `HideTroopAtkBuildIconSignal(1)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `OnRefreshTroopI... |
| `Scene.WorldTroopLineManager.DrawMesh.TroopLineAdapter` | 5 | DC:WorldMarchDataManager | `Destroy(1)`, `TryClear(1)`, `TryCreate(2)`, `TrySetColor(2)`, `TrySetMovePath(5)` |
| `Scene.WorldTroopLineManager.DrawMesh.TroopLineLifecycle` | 6 | - | `GetRenderer(1)`, `Init(1)`, `IsEnabled(0)`, `Render(1)`, `Reset(1)`, `StartUp(1)` |
| `Scene.WorldTroopLineManager_SLG.WorldTroopLine` | 7 | DC:SimpleModeManager | `Clear(1)`, `Destroy(1)`, `OnCreateMarchLine(3)`, `SetColor(1)`, `SetMovePath(5)`, `__delete(1)`, `__init(1)` |
| `Scene.WorldTroopLineManager_SLG.WorldTroopLineManager` | 11 | - | `Close(1)`, `CreateTroopLine(3)`, `GetDrawMeshRenderer(1)`, `InitDrawMeshMode(1)`, `IsDrawMeshTroopLineEnabled(1)`, `IsTroopLin... |
| `Scene.WorldTroopManager.WorldTroopFloatLodBloodTip` | 7 | - | `Create(1)`, `Destroy(1)`, `Refresh(2)`, `RefreshHp(3)`, `TimerAction(1)`, `__delete(1)`, `__init(2)` |
| `Scene.WorldTroopManager_SLG.WorldTroop` | 23 | EV:HideTroopHead ; DC:ArmyFormationDataManager,SimpleModeManager,WorldMarchDa... | `AddBulletV2(8)`, `ApplyMissileUnlockTruckIconOrder(1)`, `CanShowAttackEffect(1)`, `CanShowDelayedAttackBullet(1)`, `DestroyTro... |
| `Scene.WorldTroopManager_SLG.WorldTroopFireEffectLimiter` | 2 | - | `IsEnabled(0)`, `TryAcquire(3)` |
| `Scene.WorldTroopManager_SLG.WorldTroopManager` | 7 | DC:WorldMarchDataManager | `Close(1)`, `CreateTroopByTier(3)`, `CreateTroopsAsync(1)`, `GetTroopClassByType(3)`, `IsMarchIconVetoed(3)`, `RefreshMonsterFi... |
| `Scene.WorldTroopManager_SLG.WorldTroopRenderLimiter` | 9 | - | `IsEnabled(0)`, `IsShadowLimitEnabled(0)`, `IsTrailLimitEnabled(0)`, `ReleaseShadow(1)`, `ReleaseTrail(1)`, `ReleaseTroop(1)`, ... |
| `Scene.WorldTroopTransIcon.WorldTroopTransIcon` | 8 | - | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)`, `SetShowTime(4)`, ... |
| `Scene.WorldTroopTransIcon.WorldTroopTransIconManager` | 12 | EV:ShowMarchTrans ; DC:WorldMarchDataManager | `AddListener(1)`, `CheckShowEffect(2)`, `HideMarchTransIconSignal(1)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `RemoveAllEffect(1)... |
| `SlgEngine.Scene.AllianceBuildBloodTip.AllianceBuildBloodMan...` | 34 | MSG:MsgDefines.WorldGetAllianceCityDetail ; EV:PveLevelEnter ; DC:ActivityALV... | `AllianceCityInViewSignal(2)`, `ChangeCameraLodSignal(2)`, `Close(1)`, `GetCityBloodData(3)`, `HideAllianceCitySoliderBloodEffe... |
| `SlgEngine.Scene.AllianceBuildBloodTip.AllianceBuildBloodTip` | 27 | EV:UIShowAllianceCityBlood,UIShowAllianceCitySolider | `CheckIsFullHealth(1)`, `CheckRemove(1)`, `CheckShowSoldierSlider(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `GetBuildMo... |
| `SlgEngine.Scene.AllianceHelpVirtualMarch.AllianceHelpVirtua...` | 14 | DC:BuildTemplateManager | `Create(1)`, `CreateTroopLine(1)`, `Destroy(1)`, `DestroyModel(1)`, `DestroyTroopLine(1)`, `GetVirtualMemberShowParam(1)`, `Ini... |
| `SlgEngine.Scene.AllianceWorldMark.AllianceWorldMarkBase` | 26 | DC:AllianceBaseDataManager,WorldFavoDataManager | `ComponentDefine(1)`, `DoDelAllianceMark(2)`, `DoTranslate(3)`, `GetCountDownTextComponent(2)`, `GetCountDownWidth(1)`, `GetDel... |
| `SlgEngine.Scene.BuildBloodTip.AllianceCitySoldierTips` | 8 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshData(3)`, `RefreshSlider(1)`, `StartShowBlo... |
| `SlgEngine.Scene.BuildBloodTip.BuildBloodManager` | 27 | EV:PveLevelEnter ; DC:GloryManager,WorldPointManager | `AddListener(1)`, `GetBloodTipPrefab(1)`, `GetNpcCityBloodTipPrefab(1)`, `IsBloodTargetValid(3)`, `OnAllianceCenterDelete(2)`, ... |
| `SlgEngine.Scene.BuildBloodTip.BuildBloodTip` | 12 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshSlider(2)`, `RemoveTimer(1)`, `SetActive(2)... |
| `SlgEngine.Scene.BuildBloodTip.GloryAllianceCenterBloodTip` | 13 | DC:GloryManager | `IsSecondTick(1)`, `OnCreate(2)`, `OnDestroy(1)`, `PlayHurt(4)`, `RefreshBloodText(4)`, `SetAllianceSide(2)`, `SetCoverBase(2)`... |
| `SlgEngine.Scene.BuildFireEffect.BuildFireEffect` | 12 | - | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer(1)`, `OnCreate(2)`,... |
| `SlgEngine.Scene.BuildFireEffect.BuildFireEffectManager` | 22 | EV:ShowIsOnFire ; DC:NpcCityManager,WorldPointManager | `AddListener(1)`, `BuildOutViewSignal(2)`, `ChangeShowEffect(2)`, `CheckShowEffect(2)`, `CheckShowEffectForNpcCity(2)`, `NpcCit... |
| `SlgEngine.Scene.BuildFireEffect.BuildOutfireEffect` | 8 | DC:BuildManager,WorldPointManager | `ComponentDefine(2)`, `ComponentDestroy(1)`, `DeleteTimer(1)`, `OnCreate(3)`, `OnDestroy(1)`, `ShowPanel(2)`, `ShowTip(2)`, `St... |
| `SlgEngine.Scene.BuildTopBubble.BuildTopBubbleManager` | 15 | EV:WorldBuildTopBubblePlot ; DC:RadarCenterDataManager,WorldPointManager | `AddListener(1)`, `AddNeedRefreshBuildUuidTime(3)`, `AddTimer(1)`, `BuildOutViewSignal(1)`, `CheckDomeOpen(1)`, `CheckShowEffec... |
| `SlgEngine.Scene.CityDomeProtectEffect.CityDomeProtectEffect` | 16 | - | `AddTimer(1)`, `CheckIsFinish(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer... |
| `SlgEngine.Scene.CityDomeProtectEffect.CityDomeProtectEffect...` | 18 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `AllianceCityInViewSignal(2)`, `BuildInViewSignal(2)`, `BuildOutViewSignal(2)`, `CheckShowEffect(2)`, `CityDo... |
| `SlgEngine.Scene.CityMovingEffect.CityDomeHideEffect` | 11 | - | `AddTimer(1)`, `CheckIsFinish(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer... |
| `SlgEngine.Scene.CityMovingEffect.CityDomeShowEffect` | 11 | - | `AddTimer(1)`, `CheckIsFinish(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteTimer... |
| `SlgEngine.Scene.CityMovingEffect.CityMovingEffectManager` | 14 | EV:ShowDomeShowEffect | `AddListener(1)`, `GetHideEffectClass(1)`, `GetHideEffectPrefab(2)`, `GetShowEffectPrefab(1)`, `PrepareHideEffectParams(4)`, `R... |
| `SlgEngine.Scene.DragonRangeEffect.DragonRangeEffectManager` | 12 | EV:PveLevelEnter ; DC:ActDragonManager | `AddListener(1)`, `OnEnterCity(2)`, `OnEnterWorld(2)`, `RemoveAllEffect(1)`, `RemoveAllTips(2)`, `RemoveEffect(1)`, `RemoveList... |
| `SlgEngine.Scene.GhostGeneralBloodTip.WorldGhostGeneralBloodTip` | 17 | EV:RefreshGhostGeneralBlood ; DC:GhostKingBornManager | `AddListener(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshBlood(2)`, `RefreshGhostK... |
| `SlgEngine.Scene.MinePlunderInfo.MinePlunderInfo` | 14 | DC:MinePlunderManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)`, `SetBattleState(2)... |
| `SlgEngine.Scene.MinePlunderInfo.MinePlunderInfoManager` | 16 | EV:OnBeforeEnterCity ; DC:WorldPointManager | `AddListener(1)`, `GetMinePlunderByUuid(2)`, `OnChangeCameraLodSignal(2)`, `OnMinePlunderObjectInViewChange(2)`, `OnMinePlunder... |
| `SlgEngine.Scene.TroopHeadUI.MonsterHeadUI` | 21 | DC:DetectEventTemplateManager,MonsterTemplateManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `HideSkillHeadEffect(1)`, `Hit(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)... |
| `SlgEngine.Scene.TroopHeadUI.TroopHeadUI` | 39 | EV:ShowFormationBlood ; DC:DetectEventTemplateManager,MonsterTemplateManager,... | `AddTimer(1)`, `ClearGuideLine(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `CreateUseSkillEffect(3)`, `DOResurgence(1)`, ... |
| `SlgEngine.Scene.TroopHeadUI.TroopHeadUIManager` | 53 | EV:ShowTroopBattleValue,ShowTroopHeadInBattle ; DC:SimpleModeManager,WorldMar... | `AddListener(1)`, `BeginBattleHeadAppear(3)`, `ChangeCameraLodSignal(2)`, `ClearBattleHeadAppear(2)`, `CreateCacheBattleHeadLis... |
| `SlgEngine.Scene.TroopHeadUI.TroopHeadUIV3` | 76 | EV:ShowFormationBlood ; DC:DetectEventTemplateManager,MonsterTemplateManager,... | `AddTimer(1)`, `ApplyBattleFocusBarBrightness(1)`, `ApplyBattleFocusScale(1)`, `ApplyBattleNameLayout(1)`, `ApplyBattleRelation... |
| `SlgEngine.Scene.TroopNameLabel.TroopNameLabel` | 25 | EV:ChangeDragMarchNameColor ; DC:AllianceBuildingConfigManager,AllianceBuildi... | `AddListener(1)`, `ChangeDragNameColor(2)`, `CheckAllianceBuildingName(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `FadeA... |
| `SlgEngine.Scene.TroopNameLabel.TroopNameLabelManager` | 17 | EV:ShowTroopName ; DC:WorldMarchDataManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowEffect(2)`, `CheckTroopStateIcon(2)`, `CheckTroopStateIconSignal(2)`, `... |
| `SlgEngine.Scene.WeatherEffect.WeatherEffectManager` | 15 | EV:PveLevelEnter | `AddListener(1)`, `AddUpdate(1)`, `IfUpdateLoaderStrategy(2)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `OnModelRefresh(1)`, `OnPve... |
| `SlgEngine.Scene.WeatherEffect.WeatherFrozen` | 12 | EV:AllianceCityInView ; DC:FrozenLandDataManager | `CheckIsShow(1)`, `ForceHide(1)`, `GetEffectParentTf(1)`, `GetEffectPath(0)`, `HideAnimation(1)`, `OnAllianceCityInViewSignal(2... |
| `SlgEngine.Scene.WeatherEffect.WeatherLeaf` | 10 | - | `CheckIsShow(1)`, `GetEffectPath(0)`, `RefitLunkuo(1)`, `StartLunkuoFit(1)`, `StopLunkuoFit(1)`, `ToHide(1)`, `ToShow(1)`, `Upd... |
| `SlgEngine.Scene.WeatherEffect.WeatherLoaderBase` | 10 | - | `CheckIsShow(1)`, `GetEffectParentTf(1)`, `GetEffectPath(0)`, `GetOrder(1)`, `GetScale(0)`, `OnDestroy(1)`, `ToHide(1)`, `ToSho... |
| `SlgEngine.Scene.WeatherEffect.WeatherNormal` | 2 | - | `CheckIsShow(1)`, `__init(1)` |
| `SlgEngine.Scene.WeatherEffect.WeatherSnow` | 3 | DC:SnowManManager | `CheckIsShow(1)`, `GetEffectPath(0)`, `__init(1)` |
| `SlgEngine.Scene.WeatherEffect.WeatherVolcano` | 4 | DC:VolcanoWarManager | `CheckIsShow(1)`, `GetEffectPath(0)`, `IsScreenCenterInVolcanoRange(1)`, `__init(1)` |
| `SlgEngine.Scene.WorldArrow.WorldArrow` | 12 | DC:ArrowTipTemplateManager,BattleLevel | `AdjustArrowScale(2)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `GetArrowZoomBase(1)`, `GetDefaultArrowOffset(1)`, `GetLand... |
| `SlgEngine.Scene.WorldArrow.WorldArrowManager` | 13 | EV:ArrowShow ; DC:ArrowTipTemplateManager | `CheckCanShowAndSaveToLocal(2)`, `GetArrowClass(1)`, `GetArrowParam(1)`, `GetGuidState(1)`, `GetSettingKey(2)`, `IsCreateWorldA... |
| `SlgEngine.Scene.WorldBattleBuff.WorldBattleBuff` | 7 | - | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `RemoveTimer(1)`, `Update(1)` |
| `SlgEngine.Scene.WorldBattleBuff.WorldBattleBuffManager` | 16 | EV:PveLevelEnter ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(1)`, `CheckRemove(2)`, `CheckShowBattleBuff(2)`, `HideBattleBuffSignal(1)`, `OnEnterCi... |
| `SlgEngine.Scene.WorldBossBloodTip.WorldBossBloodTipManager` | 25 | EV:ShowActBossHeadInBattle ; DC:WorldPointManager | `AddListener(1)`, `AddToBloodCacheList(2)`, `ChangeCameraLodSignal(2)`, `GetBloodCacheByUuid(2)`, `GetHeadUIClass(1)`, `HideHea... |
| `SlgEngine.Scene.WorldBuildHeadUI.WorldBuildHeadUI` | 43 | DC:AllianceMineManager,DragonBuildTemplateManager,VolcanoWarManager | `AddTimer(1)`, `ApplyDefaultHeadBorder(1)`, `ApplyHeroQualityFrame(3)`, `ApplyHeroRoundIcon(2)`, `ApplyV3CameraBias(2)`, `Apply... |
| `SlgEngine.Scene.WorldBuildHeadUI.WorldBuildHeadUIManager` | 38 | EV:ShowAllianceCitySoldierBlood ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowAllianceBuildEffect(4)`, `CheckShowCollectEffect(6)`, `CheckShowDragonB... |
| `SlgEngine.Scene.WorldCountDownTime.WorldCountDownTImeTipsMa...` | 19 | EV:AllianceBossTimeShow ; DC:WorldPointManager | `AddListener(1)`, `AddToTimeCacheList(2)`, `ChangeCameraLodSignal(2)`, `HideAllianceBossTime(2)`, `HideAllianceBossTimeUI(2)`, ... |
| `SlgEngine.Scene.WorldCountDownTime.WorldCountDownTimeTips` | 8 | DC:AllianceBossManager | `AddTimer(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DeleteTimer(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RefreshTime(1)`, ... |
| `SlgEngine.Scene.WorldDemonHunterTip.WorldDemonHunterTip` | 5 | DC:DemonHunterDataManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)` |
| `SlgEngine.Scene.WorldDemonHunterTip.WorldDemonHunterTipManager` | 15 | EV:WorldPointManagerClose ; DC:DemonHunterDataManager,NightFallManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowAllEffect(1)`, `IsNightCanShowTip(1)`, `OnCrossServerSignal(1)`, `OnEnt... |
| `SlgEngine.Scene.WorldDesertEffect.WorldDesertEffectManager` | 19 | EV:DesertEffectInView ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowDesert(2)`, `HideDesertSignal(2)`, `OnEnterCity(1)`, `OnEnterWorld(1)`,... |
| `SlgEngine.Scene.WorldDesertEffect.WorldDesertGiveUpEffect` | 6 | - | `AddTimer(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(4)`, `RemoveTimer(1)`, `UpdateTime(1)` |
| `SlgEngine.Scene.WorldDesertEffect.WorldDesertProtectEffect` | 6 | - | `AddTimer(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(4)`, `RemoveTimer(1)`, `UpdateTime(1)` |
| `SlgEngine.Scene.WorldDesertSelect.WorldDesertSelectEffectMa...` | 15 | EV:PveLevelEnter | `AddListener(1)`, `HidePos(1)`, `OnEnterCity(1)`, `OnEnterWorld(1)`, `RemoveAlBuildWarnEffect(1)`, `RemoveAllEffect(1)`, `Remov... |
| `SlgEngine.Scene.WorldIceCaveTip.WorldIceCaveTip` | 14 | DC:ActIceCaveManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `SetLevel(2)`, `SetLevelActive(2)`, `S... |
| `SlgEngine.Scene.WorldIceCaveTip.WorldIceCaveTipManager` | 16 | EV:WorldPointManagerClose ; DC:ActIceCaveManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowAllEffect(1)`, `OnCrossServerSignal(1)`, `OnEnterCity(1)`, `OnEnterWorl... |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchEmotionCommand` | 1 | - | `__init(1)` |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchEmotionManager` | 21 | EV:WORLD_BUILD_OUT_VIEW ; DC:MarchEmojiDataManager,WorldMarchDataManager | `AddListener(1)`, `AddTimer(1)`, `AllPanelSetActive(2)`, `CheckPlayEffect(4)`, `Command(2)`, `DeleteTimer(1)`, `Destroy(1)`, `D... |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchEmotionPanel` | 27 | UI:UIEmojiSettingPanel ; DC:MarchEmojiDataManager,WorldMarchDataManager | `AddTimer(1)`, `CheckCd(1)`, `CheckRedPoint(1)`, `Create(1)`, `DeleteTimer(1)`, `Destroy(1)`, `DestroyEmoji(1)`, `DoCommand(1)`... |
| `SlgEngine.Scene.WorldMonsterBloodTip.WorldMonsterBloodTip` | 22 | DC:MonsterTemplateManager,WorldPointManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `HideSkillHeadEffect(1)`, `Hit(1)`, `OnCreate(2)`, `OnDestroy(1)`, `RemoveTimer(1)... |
| `SlgEngine.Scene.WorldMonsterBloodTip.WorldMonsterBloodTipMa...` | 19 | EV:ShowMonsterHeadInBattle ; DC:WorldPointManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CreateCacheBattleHeadList(1)`, `GetHeadUIClass(1)`, `GetMonsterOffSetY(1)`, `Hid... |
| `SlgEngine.Scene.WorldMoveCityAllGrid.WorldMoveCityAllGridMa...` | 47 | EV:WorldGrid_UpdateBuild ; DC:VolcanoWarManager,WorldPointManager | `AddCurMidCityId(3)`, `AddListener(1)`, `AddPtToSpecialMatrixFast(3)`, `AddUpdate(1)`, `AddVolcanoBuildPt(3)`, `AddVolcanoPt(3)... |
| `SlgEngine.Scene.WorldNewsTip.WorldNewsTips` | 5 | UI:UIWorldNewsTips | `OnClick(1)`, `OnCreate(2)`, `OnDestroy(1)`, `SetData(2)`, `SetPos(2)` |
| `SlgEngine.Scene.WorldNewsTip.WorldNewsTipsManager` | 11 | EV:PveLevelEnter ; DC:WorldNewsDataManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `InitShowList(1)`, `RemoveAllShowIcon(1)`, `RemoveAllTips(2)`, `RemoveListener(1)... |
| `SlgEngine.Scene.WorldRoamingBossBloodTip.WorldRoamingBossBl...` | 8 | DC:WorldMarchDataManager | `ApplyBloodTipConfig(1)`, `Create(1)`, `Destroy(1)`, `Refresh(1)`, `RefreshParent(1)`, `TimerAction(1)`, `__delete(1)`, `__init... |
| `SlgEngine.Scene.WorldRoamingBossBloodTip.WorldRoamingBossBl...` | 13 | EV:WorldTroopGameObjectCreateFinish ; DC:WorldMarchDataManager | `AddListeners(1)`, `Create(2)`, `Destroy(2)`, `DestroyAll(1)`, `GetInstance(1)`, `OnLodChanged(2)`, `OnMarchUpdate(2)`, `OnTroo... |
| `SlgEngine.Scene.WorldSandwormMoveControl.WorldSandwormMoveC...` | 17 | - | `AddTimer(3)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `DataDefine(1)`, `DataDestroy(1)`, `DeleteMoveMono(1)`, `DeleteTime... |
| `SlgEngine.Scene.WorldSandwormMoveControl.WorldSandwormMoveC...` | 8 | EV:OnEnterWorld | `AddListener(1)`, `CheckAll(1)`, `CheckAllEffect(1)`, `RemoveAll(1)`, `RemoveAllEffect(1)`, `RemoveListener(1)`, `__delete(1)`,... |
| `SlgEngine.Scene.WorldTerrainSelect.WorldTerrainSelectEffect...` | 11 | EV:PveLevelBeforeEnter | `AddListener(1)`, `HidePos(1)`, `OnEnterCity(2)`, `OnEnterWorld(2)`, `RemoveAllEffect(1)`, `RemoveAllTips(2)`, `RemoveEffect(1)... |
| `SlgEngine.Scene.WorldTradePostTip.WorldTradePostTip` | 13 | DC:ActTradePostManager | `ComponentDefine(1)`, `ComponentDestroy(1)`, `OnCreate(2)`, `OnDestroy(1)`, `ReInit(2)`, `SetLevel(2)`, `SetLevelActive(2)`, `S... |
| `SlgEngine.Scene.WorldTradePostTip.WorldTradePostTipManager` | 16 | EV:WorldPointManagerClose ; DC:ActTradePostManager | `AddListener(1)`, `ChangeCameraLodSignal(2)`, `CheckShowAllEffect(1)`, `OnCrossServerSignal(1)`, `OnEnterCity(2)`, `OnEnterWorl... |
| `SlgEngine.Scene.WorldTroopLineManager.WorldDragTroopLine` | 7 | - | `Destroy(1)`, `OnCreateLine(3)`, `SetColor(2)`, `SetDragPath(3)`, `StartMove(9)`, `__delete(1)`, `__init(1)` |
| `SlgEngine.Scene.WorldTroopLineManager.WorldTroopDestination...` | 17 | DC:WorldPointManager | `ApplyDisplayOffset(1)`, `ComponentDefine(1)`, `ComponentDestroy(1)`, `GetCircleEffIndex(2)`, `GetFinalPos(3)`, `GetOperateIcon... |
| `SlgEngine.Scene.WorldTroopLineManager.WorldTroopLine` | 8 | DC:SimpleModeManager,WorldMarchDataManager | `Clear(1)`, `Destroy(1)`, `GetTroopLineColor(1)`, `OnCreateMarchLine(2)`, `SetColor(1)`, `SetMovePath(5)`, `__delete(1)`, `__in... |
| `SlgEngine.Scene.WorldTroopLineManager.WorldTroopLineManager` | 24 | EV:ChangeDragMarchNameColor,OnTroopDragonUpdatePos ; UI:UIMarchCancelDragMsgB... | `AddListener(1)`, `AddUpdate(1)`, `Close(1)`, `CreateTroopDestination(1)`, `CreateTroopLine(3)`, `DestroyAll(1)`, `DestroyTroop... |
| `SlgEngine.Scene.WorldTroopManager.Const` | 0 | - |  |
| `SlgEngine.Scene.WorldTroopManager.OverlordMark.OverlordMark` | 10 | - | `ClampLevel(1)`, `Explode(1)`, `Init(7)`, `OnCreate(1)`, `OnDestroy(1)`, `RefreshLevelText(1)`, `SetLevel(2)`, `SetVisible(2)` ... |
| `SlgEngine.Scene.WorldTroopManager.OverlordMark.OverlordMark...` | 11 | EV:WorldTroopGameObjectDestroyFinish ; DC:SimpleModeManager,WorldPointManager | `GetMarkAnchorLayout(2)`, `GetTargetAnchor(2)`, `OnBattleFinish(2)`, `OnLodChanged(2)`, `OnSkillHit(5)`, `OnTargetDestroyed(2)`... |
| `SlgEngine.Scene.WorldTroopManager.TroopState.WorldTroopStat...` | 14 | EV:HideTroopName ; DC:SimpleModeManager,WorldMarchDataManager | `CheckFaceEnemyState(2)`, `FinishMove(1)`, `OnStateEnter(1)`, `OnStateLeave(1)`, `OnStateUpdate(1)`, `OnTroopChange(1)`, `PlayA... |
| `SlgEngine.Scene.WorldTroopManager.TroopState.WorldTroopStat...` | 7 | - | `ChangeState(2)`, `OnStateEnter(1)`, `OnStateLeave(1)`, `OnStateUpdate(1)`, `OnTroopChange(1)`, `__delete(1)`, `__init(3)` |
| `SlgEngine.Scene.WorldTroopManager.TroopState.WorldTroopStat...` | 6 | EV:HideTroopHead ; DC:GloryManager | `OnStateEnter(1)`, `OnStateLeave(1)`, `OnStateUpdate(1)`, `OnTroopChange(1)`, `__delete(1)`, `__init(3)` |
| `SlgEngine.Scene.WorldTroopManager.TroopState.WorldTroopStat...` | 8 | EV:CheckTroopStateIcon ; DC:WorldMarchDataManager | `ClearAnimQueue(1)`, `OnStateEnter(2)`, `OnStateLeave(1)`, `OnStateUpdate(1)`, `OnTroopChange(1)`, `StartAnimQueue(2)`, `__dele... |
| `SlgEngine.Scene.WorldTroopManager.TroopState.WorldTroopStat...` | 9 | EV:HideTroopAtkBuildIcon ; DC:GloryManager,WorldMarchDataManager | `FinishMove(1)`, `OnStateEnter(1)`, `OnStateLeave(1)`, `OnStateUpdate(1)`, `OnTroopChange(1)`, `SetStartPosToMove(1)`, `StartMo... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroop` | 191 | EV:DragonSecretShow,HideTroopAtkBuildIcon,HideTroopHead ; DC:ActDinosaurBossD... | `AddBulletV2(8)`, `AddCheckTimer(1)`, `AddShield(1)`, `AddSkillShield(3)`, `ApplyMissileUnlockTruckIconOrder(1)`, `Attack(1)`, ... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopManager` | 51 | EV:ChangeCameraLod ; DC:WorldMarchDataManager | `AddListener(1)`, `AddToUpdateList(2)`, `CanUseParticleTemplate(1)`, `CheckGigantismExpire(2)`, `CheckPlayEffect(4)`, `ClearGig... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopPart.Impl.Overl...` | 15 | DC:WorldMarchDataManager | `DoSkill(2)`, `GetModelPath(1)`, `GetShowTemplate(1)`, `IsModelVisible(1)`, `OnCreate(1)`, `OnDestroy(1)`, `OnLodChanged(2)`, `... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopPart.Impl.Overl...` | 1 | DC:OverlordTemplateManager | `CheckCreateCondition(2)` |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopPart.WorldTroop...` | 11 | EV:WorldMarchData_MoveStart ; DC:WorldMarchDataManager | `ChangeStatus(2)`, `OnAttack(1)`, `OnCreate(1)`, `OnDestroy(1)`, `OnLodChanged(2)`, `OnStatusChanged(2)`, `OnWorldMarchData_InB... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopPart.WorldTroop...` | 11 | DC:WorldMarchDataManager | `CreatePart(3)`, `DestroyPart(3)`, `DoSkill(5)`, `GetTroopPartDefinitions(1)`, `OnAttack(2)`, `OnLodChanged(3)`, `OnTroopCreate... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopSoundHelper` | 10 | - | `AddOtherMarchSound(3)`, `AddOtherMarchSounds(2)`, `AddSeasonSounds(3)`, `AddSound(4)`, `GetAnimSound(2)`, `GetCurrentSeasonId(... |
| `SlgEngine.Scene.WorldTroopManager.WorldTroopStateMachine` | 10 | EV:CheckTroopStateIcon | `ChangeState(2)`, `GetCurrentState(1)`, `GetOrCreateState(2)`, `GetStateClassMap(1)`, `GetStatePreloadOrder(1)`, `OnTroopChange... |
