# Domain Quick-Card: PVE, Area Exploration, Monsters & Bosses (`pve_exploration_bosses`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain pve_exploration_bosses`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **1** bot fns / **0** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **51** packets |
| `DataCenter` Managers & Singletons | **70** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **30** windows / **0** active HUD buttons / **7** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **31** tables / **58** enums / **32** live events / **79** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `run_area_exploration` | `L8100-L8410` | UserStartBarrelPushBatch | BattleLevel, LWBattleManager, StoryManager, TowerClimbingManager |

## 2. `DataCenter` Managers & Outgoing Links (70)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.BattleLevel` | 144 | MsgDefines.SU_HeartBeat | LevelSceneLoadDone, OnEnterCity, SU_ChangeViewHeight... | MainUI_SU, SU_NewHero, UIArenaPanel | TableName.SU_PveType |
| `_G.UIManager` | 109 | - | BeforeCloseUI, CloseUI, OnKeyCodeEscape, OpenUI | UIAlarm, UIPVEScene, UIParkourBattleLose | - |
| `DataCenter.MineCaveManager` | 54 | MsgDefines.GetMineCaveInfo, MsgDefines.SetMineCaveCross | OnPassDay, OnRecvMineCavePlunderLog, PveMineCaveInfo... | UIMineCaveCrossTip | TableName.MineCave |
| `DataCenter.MigrateDataManager` | 52 | MsgDefines.GetMigrateServers, MsgDefines.GetMigrateUserInfo, M... | GetMigrateApplyList, GetMigrateList, GetMigrateServe... | - | - |
| `DataCenter.RewardManager` | 49 | MsgDefines.RealRewardInfo | CloseUI, GetRealRewardInfo, ResourceUpdated | UICarnivalLuckySpin, UICarnivalSendWorld, UIGet... | TableName.NightLunarLightCard, TableName.StatusTab |
| `_G.SceneUtils` | 45 | - | - | - | TableName.WorldCity |
| `DataCenter.PushNoticeManager` | 37 | MsgDefines.UpdatePushSwitch | NoticePushSettingUpdate, WillEnterForeground | UISetPushNotification | TableName.APS_PUSH |
| `_G.PveUtil` | 37 | - | - | MainUI_SU, UIHeroList, UISearch | TableName.Monster |
| `DataCenter.OverlordTemplateManager` | 34 | - | - | - | TableName.OverlordCure, TableName.OverlordFile,... |
| `DataCenter.BaubleLibraryManager` | 33 | MsgDefines.ClaimBaubleReward, MsgDefines.GetBaubleRewardInfo | BaubleLibraryRedPointRefreshed, BaubleStatusChanged,... | - | TableName.BaubleRating, TableName.EffectNumDesc |
| `DataCenter.PlayerLevelManager` | 33 | - | CloseUI, ReceiveLevelReward, UpdatePlayerExp | UIBuildDetails, UILevelUp | TableName.EffectNumDesc |
| `_G.LocalController` | 32 | - | - | - | - |
| `DataCenter.TowerClimbingManager` | 31 | - | - | UIPVETowerClimbJumpReward | TableName.StoryMap |
| `DataCenter.HonorPhaseManager` | 30 | - | PUSH_INIT_OK | UIHonorPhaseCG | TableName.ArmyHonor |
| `DataCenter.BoardManager` | 29 | - | RefreshCityRoadArr, UpdateRoadData | - | - |
| `DataCenter.RecommendShowManager` | 29 | - | BuildResourcesStart, RefreshRecommendShow, RefreshUI... | UIFarm, UIGuideHeadTalk | - |
| `DataCenter.MonsterLockDataManager` | 28 | MsgDefines.ReceivePveMonsterReward | MonsterLockStateUpdate, OnEnterCity, RefreshMonsterR... | UIPVEMonsterToLevel | - |
| `DataCenter.MonsterManager` | 27 | - | - | - | - |
| `DataCenter.ValentineDecorationManager` | 27 | MsgDefines.ValentineFeed, MsgDefines.ValentineGetFeedReward, M... | ValentineRewardShow, ValentineTipsShow, WorldBuildSe... | UIFoxHello, UIGivingRoses2Castle | - |
| `DataCenter.LotteryDataManager` | 26 | - | CheckPubBubble | - | TableName.HeroRecruit |
| `DataCenter.FlyController` | 25 | - | SU_FlyObjFirst, UpdatePlayerExp | - | - |
| `DataCenter.UIPopWindowManager` | 24 | - | PveLevelEnter | UIBuildUpUnlock, UIMainAccountBind, UIRedenvelo... | - |
| `DataCenter.DecorationTemplateManager` | 21 | - | - | - | TableName.Decoration |
| `DataCenter.LandLockBubbleManager` | 21 | - | LandLockInView, ResetQuestArrow | UIWorldTileUI | - |
| `DataCenter.HotUpdatePrefetchManager` | 20 | - | - | - | - |
| `DataCenter.PaidLotteryManager` | 20 | MsgDefines.BeginPaidLotteryRoll, MsgDefines.ClaimPaidLotteryTi... | OnClaimPaidLotteryTicketSucc, OnGetPaidLotteryRollRe... | - | - |
| `_G.LuaEntry` | 20 | - | DidEnterBackground, OnCameraEnterIdle, WillEnterFore... | UIChatNew, UICommonMessageBar | - |
| `DataCenter.RadarAlarmDataManager` | 19 | - | RefreshAlarm | - | - |
| `DataCenter.PlayerInfoDataManager` | 18 | MsgDefines.GetNewUserInfo | - | - | - |
| `DataCenter.BaubleObjectManager` | 17 | - | LevelSceneLoadDone | - | - |
| `DataCenter.ScienceTemplateManager` | 17 | - | - | - | TableName.APSScienceTab, TableName.ScienceNew |
| `DataCenter.SearchLodManager` | 16 | - | ChangeCameraLod | UIMainMiniMap | - |
| `DataCenter.PrivilegeEffectManager` | 15 | - | - | - | - |
| `DataCenter.ShareMsgManager` | 15 | MsgDefines.ShareMsg, MsgDefines.ShareMsgSend | RefreshAssistanceHeroChatCell | - | - |
| `DataCenter.ControlTriggerManager` | 14 | - | SU_UpdateTriggerState | - | - |
| `DataCenter.GovernmentTemplateManager` | 13 | - | - | - | TableName.Government |
| `DataCenter.LowFxModeManager` | 13 | - | OnEnterWorld | - | - |
| `DataCenter.VolcanoIconNameManager` | 13 | - | OnEnterWorld | - | - |
| `DataCenter.AccountListManager` | 12 | - | - | - | - |
| `DataCenter.SUPveLevelDataManager` | 12 | - | - | - | TableName.Land_Lock_Property |
| `DataCenter.SidebarManager` | 12 | - | - | - | - |
| `DataCenter.IdVerManager` | 11 | MsgDefines.AdultVerificate | - | - | - |
| `DataCenter.NationTemplateManager` | 11 | - | - | - | TableName.NationConf |
| `DataCenter.BaseExpansionTemplateManager` | 10 | - | - | - | TableName.BaseExpansion, TableName.SingleMapPos... |
| `DataCenter.PushSettingData` | 10 | - | - | - | - |

## 3. Key Wire Packets (51 total; top 51 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `blind.box.stage.reward` | BlindBoxStageReward | `p=2` PutInt | BlindBoxManager.BlindBoxStateRewardMessage | - |
| `blind.box.stage.reward.new` | BlindBoxStageRewardNew | `p=4` PutInt, PutBool | BlindBoxManager.BlindBoxStateRewardMessage | - |
| `choose.pve.buff` | ChoosePveBuff | `p=4` PutInt | BattleLevel.UpdatePveBuffs | - |
| `clear.pve.trigger.reward.cd` | ClearPVETriggerRewardCD | `p=2` PutInt | BattleLevel.OnClearPVETriggerRewardCDHandler | - |
| `dragon.get.commander.list` | DragonGetCommanderList | `p=2` PutInt | BattleCommandManager.OnHandleGetAllCommander | - |
| `dragon.get.commander.team` | DragonGetCommanderTeam | `p=2` PutInt | BattleCommandManager.OnHandleGetAllTeam | - |
| `dragon.setting.commander` | DragonSettingCommander | `p=4` PutUtfString, PutInt | BattleCommandManager.OnHandleSendCommander | - |
| `dragon.setting.fight.commander` | DragonSettingFightCommander | `p=3` PutUtfStringArray, PutInt | BattleCommandManager.OnHandleSendFightCommander | - |
| `dragon.setting.group.member` | DragonSettingGroupMember | `p=2` PutSFSArray | BattleCommandManager.OnHandleSaveEditTeam | - |
| `find.monster.boss` | FindMonsterBoss | `p=4` PutInt | RadarCenterDataManager.HandleFindMonsterBossBack | - |
| `get.explore.pve.detail.info` | LevelExploreGetDetail | `p=2` PutInt | LevelExploreManager.HandleGetDetail | - |
| `get.trigger.reward` | GetTriggerReward | `p=2` PutInt | BattleLevel.self | - |
| `push.dragon.player.change` | PushDragonPlayerChange | `p=1`  | BattleCommandManager.OnHandlePushChangePlayer | - |
| `push.dragon.player.info` | PushDragonPlayerInfo | `p=1`  | BattleCommandManager.OnHandlePushAllPlayer | - |
| `push.dragon.team.change` | PushDragonTeamChange | `p=1`  | BattleCommandManager.OnHandlePushAllTeam | - |
| `push.init.small` | PushInitSmall | `p=2`  | DrakeBoss2Manager.InitData | PushInitSmallDone |
| `push.pve.level.finish` | PushPveLevelFinish | `p=1`  | BattleLevel.OnPushPveLevelFinish | - |
| `push.pve.monster.add` | PushPveMonsterAdd | `p=1`  | MonsterLockDataManager.UpdateAllMonster | - |
| `push.pve.monster.update` | PushPveMonsterUpdate | `p=1`  | MonsterLockDataManager.UpdateAllMonster | - |
| `push.server.battle.score` | PushServerBattleScore | `p=1`  | CrossWonderManager.HandlePushServerBattleScore | - |
| `push.volcano.battle.command.change` | PushVolcanoBattleCommandChange | `p=1`  | VolcanoWarManager.HandleVolcanoBattleCommandChange | - |
| `receive.pve.monster.reward` | ReceivePveMonsterReward | `p=2` PutInt | MonsterLockDataManager.DoWhenReceiveMonsterRewardBack | - |
| `receive.pve.trigger.reward` | ReceivePVETriggerReward | `p=2` PutInt, PutBool, PutFloat | BattleLevel.OnReceivePveTriggerRewardHandler | - |
| `receive.story.stage.reward` | ReceiveStoryStageReward | `p=3` PutInt | StoryManager.HandleReceiveStageReward | - |
| `skip.story.pve.level` | SkipStoryPveLevel | `p=3` PutInt | StoryManager.HandleSkip | - |
| `user.fight.pve.monster` | GetUserFightPve | `p=2` PutInt, PutBool, PutLong | BattleLevel.OnBattleMessage | - |
| `user.get.pve.stage` | UserGetPVEStage | `p=2` PutInt | BattleLevel.OnGetStageMessage | - |
| `user.select.fight.pve.monster` | PveDiffFight | `p=7` PutInt, PutLong, PutSFSArray | BattleLevel.OnBattleMessage | - |
| `user.select.pve.buff` | SelectPveBuff | `p=5` PutInt | BattleLevel.OnSelectPveBuffMessage | - |
| `volcano.battle.command.open` | VolcanoBattleCommandOpen | `p=2` PutInt | VolcanoWarManager.HandleVolcanoBattleCommandOpen | VolcanoBattleCommandOpenBack |
| `volcano.battle.command.set` | VolcanoBattleCommandSet | `p=3` PutInt, PutUtfString | VolcanoWarManager.UpdateCommandId | VolcanoBattleCommandSetBack |
| `volcano.battle.effect.list` | VolcanoBattleEffectList | `p=2` PutInt | VolcanoWarManager.UpdateVolcanoEffect | VolcanoBattleAllianceRewardRecord |
| `volcano.battle.open` | VolcanoBattleOpen | `p=2` PutInt | VolcanoWarManager.HandleStageInfo | - |
| `volcano.battle.reward.show` | VolcanoBattleRewardShow | `p=2` PutInt | VolcanoWarManager.HandleRewardShow | - |
| `volcano.battle.score.reward` | VolcanoBattleScoreReward | `p=3` PutInt | RewardManager.ShowCommonReward | - |
| `check.attack.boss` | CheckAttackBoss | `p=2` PutLong | - | CheckAttackBoss |
| `find.monster` | FindMonster | `p=6` PutInt, PutBool | - | - |
| `get.dragon.boss.damage` | GetDragonBossDamage | `p=2` PutInt, PutLong | - | UpdateDragonBossDamage |
| `get.tower.fight.record` | GetTowerFightRecord | `p=4` PutInt, PutLong | - | RefreshTowerFightRecord |
| `push.pve.stamina.update` | PushPveStaminaUpdate | `p=1`  | - | PveStaminaUpdate |
| `push.volcano.base.up` | pushVolcanoBaseUp | `p=1`  | - | - |
| `pve.trigger.cost` | PveTriggerCost | `p=2` PutInt | - | - |
| `user.fail.pve.level` | UserFailPveLevel | `p=3` PutInt, PutLong | - | - |
| `user.finish.pve.level` | UserFinishPVELevel | `p=4` PutInt, PutBool | - | - |
| `user.sweep.monument.pve` | UserSweepMonumentPVE | `p=2` PutInt | - | - |
| `volcano.battle.beInvite.confirm` | VolcanoBattleBeInviteConfirm | `p=4` PutInt, PutLong | - | VolcanoWarAcceptInvite |
| `volcano.battle.beInvite.record` | VolcanoBattleBeInviteRecord | `p=2` PutInt | - | VolcanoWarBeInvitedRecordUpdate |
| `volcano.battle.command.list` | VolcanoBattleCommandList | `p=2` PutInt | - | VolcanoBattleCommandListBack |
| `volcano.battle.invite.before` | VolcanoBattleInviteBefore | `p=3` PutInt | - | - |
| `volcano.battle.invite.list` | VolcanoBattleInviteList | `p=2` PutInt | - | - |
| `volcano.battle.invite.record` | VolcanoBattleInviteRecord | `p=2` PutInt | - | VolcanoWarInviteRecordUpdate |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (30 windows)

**`GoToUtil` Routers:** `GoToUtil.FindMonster` -> [], `GoToUtil.GoLandPve` -> [], `GoToUtil.GoPveLevel` -> [], `GoToUtil.GoTriggerPve` -> [], `GoToUtil.GotoPos` -> [], `GoToUtil.GotoPushPveLevel` -> ['UIJeepAdventureMain', 'UIStoryHangup'], `GoToUtil.LookAtFirstCanUnlockLandLockByPve` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIBattleground` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Main/UIBattleground.prefab` | Music_Effect_Button, Setting/SwitchObj/GameObject/Bt... | - |
| `UIPVEEnterLevel` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPVE/UIPVEEnterLevel.prefab` | OnBtnClick, UIButton, UIToggle, close_btn, close_btn... | - |
| `UIParkourBattleLose` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIParkourBattleLose.pr...` | Barrel_BtnFeedBackClick, OnBtnBackClick, barrel/soun... | - |
| `UISettingConsole` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingConsole.pr...` | RefreshBtnBarrelGMInfo, RefreshBtnLuaProfiler, Toggl... | - |
| `UI_GetRewardTips` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/Survival/UI_GetRewardTips.prefab` | OnBtnOkClick, UIButton, btnClose, m_btnOk | - |
| `UIPVEDetectSpecialJumpLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVEDetectSp...` | BtnClick_Close | MsgDefines.DetectEventPveBatch |
| `UIPVETowerClimbJump` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVETowerCli...` | - | MsgDefines.UserStartBarrelPushBatch |
| `UIRewardParkourMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIParkourView.prefab` | barrel/sound_btn_back | - |
| `ChampionBattleBetting` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampi...` | - | - |
| `LFChampionBattleFight` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampi...` | - | - |
| `LFChampionBattleReport` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampi...` | - | - |
| `UIBarrelGetStronger` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIBarrelGetStronger.pr...` | - | - |
| `UIBossDamageRecord` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIBossDamageRecord/UIBossDama...` | - | - |
| `UIBossRunAway` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBossRunAway/UIBossRunAway.p...` | - | - |
| `UIChampionBattleChampionView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampi...` | - | - |
| `UIChampionBattleRuleView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/Champion...` | - | - |
| `UIChampionpropaganda` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampi...` | - | - |
| `UIFinalWaveTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIFinalWaveTip.prefab` | - | - |
| `UIFullScreenBlackBG` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/UIPVE/UIFullScreenBlackBG.prefab` | - | - |
| `UILetterBoxing` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Barrel/UILetterBoxing.prefab` | - | - |
| `UIMainPromptView` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/Survival/UIMainPrompt.prefab` | - | - |
| `UIPVELevelLoading` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIPVE/UIPVELevelLoading.prefab` | - | - |
| `UIPVELevelReward_SU` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPVE/UIPVELevelReward.prefab` | - | - |
| `UIPVELoading` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIPVE/UIPVELoading.prefab` | - | - |
| `UIPVEMonsterToLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPVE/UIPVEMonsterToLevel.prefab` | - | - |
| `UIPVETowerClimbJumpReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVETowerCli...` | - | - |
| `UIPrograssBar` | `UIContainer/UIRes...` | `Assets/Main/Prefabs/UI/Survival/UIPrograssBar.prefab` | - | - |
| `UIQTEView` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Survival/UIQTE/UIQTEView.prefab` | - | - |
| `UISelectLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UISelectLevel/UIThro...` | - | - |
| `UIZombieBattleMain` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/ParkourBattle/UIZombieBattleM...` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `barrel_monster` | TableName.Barrel_Monster | 31,899 | id, baseId, property |
| `lw_monster_born` | TableName.LW_Monster_Born | 23,481 | id, coord, type, para, monster, buff_item, para2, para3, para4 |
| `APS_monster` | TableName.Monster | 7,882 | id, level, army, size, light_injury_rate, injury_rate, attackRange, expire, deadTime, reward |
| `aps_pve_level_old` | TableName.PVELevelOld | 5,052 | id, type, subtype, play_type, Triggers, para1, para2, para7, scene_show, reward |
| `aps_pve_trigger_old` | TableName.PVETriggerOld | 4,730 | id, UnclockType, SideQuest, Pos, UnclockPara, ShowPos, UnclockFog |
| `aps_pve_trigger` | TableName.PVETrigger | 797 | id, UnclockType, UnclockPara, UnclockPara2, ModelName, Pos, Transform, State, RecoverCd, Lin... |
| `aps_pve_monument` | TableName.PVEMonument | 687 | id, level, reEnter, build_condition, auto_move, enter_resource_cost, season, show_reward, use_b |
| `barrel_monster_base` | TableName.Barrel_Monster_Base | 349 | id, asset, model_size, relation_type, monster_type, is_boss, param, hp_bar_num, death_sound,... |
| `aps_pve_zombie` | TableName.PVEZombie | 156 | id, type, group, ModelName, MoveSpeed, WalkSpeed, Blood, Attack, AttackRadius, AttackDropDis... |
| `aps_pve_level` | TableName.PVELevel | 152 | id, type, SpawnPos, SpawnRotation, RunPos, minPos, maxPos, Triggers, Scene, DayTime |
| `explorer_case` | TableName.AdventureCase | 150 | id, content, monster, buff, monster_showreward, reward, reward_show, random, randomdes |
| `lw_stage_feature` | TableName.LW_Stage_Feature | 147 | id, order, name, desc, title, target, type, scene, scene_tail, birth_point |
| `aps_monsterlock` | TableName.MonsterLock | 120 | id, level, name, pre_build, pre_quest, pre_misson, model, size, pve, need_army |
| `pve_type` | TableName.SU_PveType | 102 | id, type, name, order, resettype, level, cost, requirelevel, text, loading_tips |
| `aps_pve_battlebuff` | TableName.BattleBuff | 71 | id, type, buffId, icon, LocalType, group, not_choose, show_group, timetype, time |
| `c_vfx` | TableName.PveVFX | 61 | id, name, type, para1, para2 |
| `lw_count_stage_trap` | TableName.LW_Count_Stage_Trap | 56 | id, prefab, bubble_height, hit_vfx, motion_parts, motion_type, motion_param1, motion_param2,... |
| `aps_pve_buff` | TableName.PveBuff | 55 | id, type_buff, para, time, time_type, pic, model, des |
| `barrel_pve` | TableName.Barrel_PVE | 40 | id, pve_level_id, level, lock, lock_time, lock_share, score_standard, if_difficult |
| `lw_stage` | TableName.LW_Stage | 35 | id, order, name, desc, title, target, type, scene, trigger_item, trigger_plot |
| `explorer_entrance` | TableName.AdventureEntrance | 30 | id, pveLevel, reward |
| `npc_base` | TableName.PveNpc | 29 | id, type, name, icon_head, icon_head_S, low_model, high_model, action_group, aps_pve_zombie_... |
| `aps_pve_part_zombie` | TableName.PveRolePart | 18 | id, hat, head, cloth, pants, shoes, weapon |
| `aps_pve_atom` | TableName.PVEAtom | 13 | id, type, lv, hp, num, resource_item, energy_cost, item |
| `lw_count_stage_group` | TableName.LW_Count_Stage_Group | 11 | id, max_hp, unit_pt, class, move_speed, unit_radius, face_dir, unit_prefab, dead_vfx, hit_vfx |
| `explore_level` | TableName.LevelExplore | 10 | id, level_order, name, name_value, level_id, hero_num, energy_cost, reward |
| `lw_count_stage_soilder` | TableName.LW_Count_Stage_Soilder | 8 | id, point, radius, end_line_size, weapon, muzzle_bone, prefab, dead_vfx, march_anim, move_anim |
| `dinosaur_boss` | TableName.DinosaurBoss | 5 | id, monster, title, reward, name, boss_frame, sfx_ui_wake, lop_strtime, sfx_ui_loop, loptime |
| `lw_count_stage` | TableName.LW_Count_Stage | 5 | id, order, name, desc, title, target, building_condition, stage_type, end_type, end_param3 |
| `roaming_boss_reward_show` | TableName.RoamingBossRewardShow | 3 | id, world_season, mons_name, mons_desc, mons_img, mons_id_list, mons_reward_kill, mons_rewar... |
| `aps_pve_ZombieWave` | TableName.PVEZombieWave | 1 | id, level, zombie_id, count, path, spawn_radius, delay, times, interval, isday |

**Enums:** `SlgBattleType` (66), `BattleType` (51), `MonsterSpecialType` (28), `PveEntrance` (28), `PvePowerLackTipType` (19), `BattleSubTitleShowType` (18), `PveLevelType` (15), `SU_PveLevelType` (14), `ZombieState` (14), `BattleReportShowType` (12), `ZombieAnim` (12), `PVEType` (11), `PVEEnterType` (10), `BarrelMemberType` (8), `GloryBattleDetailType` (8), `PveBuffType` (8), `LeagueMatchStage` (7), `PvePowerLackType` (6), `BattleBuffType` (5), `BattleTeamFlag` (5), `ChampionBattlePosterType` (5), `MissileUnlockStage` (5), `MonsterType` (5), `PveObjectSelectEffectColor` (5), `GloryBattleState` (4)
