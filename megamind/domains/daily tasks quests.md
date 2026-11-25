# Domain Quick-Card: Daily Tasks & Quests (`daily_tasks_quests`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain daily_tasks_quests`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **1** tasks / **17** bot fns / **4** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **134** packets |
| `DataCenter` Managers & Singletons | **23** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **109** windows / **2** active HUD buttons / **9** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **10** tables / **69** enums / **38** live events / **33** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Task Key | Title | Tag |
|---|---|---|
| `furylord` | Furylord Boss (03:00) | `Squad 1 x4` |

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `_finalize_task_result` | `L1189-L1206` | - | - |
| `_with_task_telemetry` | `L1209-L1217` | - | - |
| `_daily_state_path` | `L2112-L2114` | - | - |
| `_load_daily_state` | `L2122-L2129` | - | - |
| `_get_daily_count` | `L2132-L2146` | - | - |
| `_increment_daily_count` | `L2149-L2176` | - | - |
| `run_furylord` | `L4618-L4770` | - | ActRoamingBossManager, WorldPointManager |
| `run_bounties` | `L4773-L5242` | DispatchAssist, DispatchRewardAll, DispatchStart, DispatchTaskRefresh | ActDispatchTaskDataManager, ActivityListDataManager, ItemData |
| `run_bounty_steal` | `L5245-L5551` | DispatchSteal | ActDispatchTaskDataManager, WorldPointManager |
| `run_vip_store_rewards` | `L6547-L6682` | BuyCommonShopGoods, BuyFreeWeeklyPackage | CommonShopManager, VIPManager |
| `run_daily_claims` | `L11151-L11648` | AchievementRewardGet, AllClaimWeekCardReward, ClaimAllSeasonPassRew... | AchievementManager, ActBattlePassData, ActSeasonWeekCardData, Activ... |
| `_scan_daily_tasks_live` | `L11651-L11752` | - | DailyTaskManager |
| `_classify_daily_task_kind` | `L11755-L11805` | - | - |
| `_do_daily_hero_exp` | `L11883-L11947` | HeroLvUp | HeroDataManager, ItemData, ItemTemplateManager |
| `_do_daily_ticket_recruit` | `L11950-L12027` | LotteryHeroCard | ItemData, LotteryDataManager |
| `_do_daily_gather_acts` | `L12221-L12352` | FindResourcePoint | CollectResourceManager, WorldPointManager |
| `_claim_all_daily_tasks_and_boxes` | `L12355-L12423` | DailyQuestGetAllReward, DailyQuestReward, DailyTaskReward | DailyTaskManager |

**Hub `action_id` Routes:** `run_single_task` (L4677), `run_single_task` (L5212), `install_bot_task` (L5368), `uninstall_bot_task` (L5373)

## 2. `DataCenter` Managers & Outgoing Links (23)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.GuideManager` | 225 | MsgDefines.SaveGuide, MsgDefines.StatTT | Barrel_PauseOrResumeUnitAni, ClickFarmBuildShow, Gui... | MainUI_SU, UIBuildList, UICommonMessageTip | - |
| `DataCenter.TaskManager` | 86 | MsgDefines.GetTaskNormalRewardInfo | MainTaskSuccess, OnOneActivityOverviewRedChange, OnR... | UIDailyActivity | - |
| `DataCenter.DemonHunterDataManager` | 80 | MsgDefines.GetDemonHunterInfo, MsgDefines.SubmitDemonHunterQuest | DemonHunterHunterUpdate, DemonHunterInfoUpdate, Demo... | UICommonMessageBar, UIDemonHunterMapPointTips, ... | TableName.DemonHunterInfo, TableName.DemonHunte... |
| `DataCenter.PlayerMarketManager` | 71 | MsgDefines.PlayerMarketGame, MsgDefines.PlayerMarketInfo, MsgD... | PlayerMarketGameResult, PlayerMarketInfoUpdate, Play... | UIActivityCenterTable | TableName.ActivityPanel |
| `DataCenter.ChapterTaskManager` | 45 | MsgDefines.GetAllChapterInfo | ChapterTask, ChapterTaskGetReward | GetWindow, UITaskPromptTips | TableName.Chapter |
| `DataCenter.TalkTaskDataManager` | 43 | MsgDefines.DetectEventRewardReceive, MsgDefines.SU_DialogStep | BuildLevelUp, DetectInfoChange, DetectNpcGetReward, ... | - | TableName.Option_Config |
| `DataCenter.VIPManager` | 43 | MsgDefines.VipAddLoginScore, MsgDefines.VipGetEveryDayReward, ... | VipRefreshFree | - | - |
| `DataCenter.DragonSwapManager` | 39 | MsgDefines.DragonKickMember, MsgDefines.DragonMemberStatusInfo... | DragonSwapEntryUpdate, DragonSwapPanelRefresh, Drago... | - | - |
| `DataCenter.MonopolyActivityDataManager` | 34 | MsgDefines.BuyActivityMonopolyGoods, MsgDefines.GetMonopolyAct... | OnRevMonopolyStageReward, OnRollMonopolyActivity, Re... | UIMultiBuy | - |
| `DataCenter.DailyTaskManager` | 29 | MsgDefines.DailyQuestLs | DailyQuestLs, DailyQuestReward, OnPassDay, ResourceU... | UIPresentGetRewardView | - |
| `DataCenter.ActBossDataManager` | 28 | MsgDefines.TaskRewardInfo, MsgDefines.UserGetActBossMarch | RefreshPersonalTaskRewards | - | - |
| `DataCenter.LoginPopManager` | 21 | - | LevelSceneLoadDone, OnLoginPopped, RefreshWelfareRedDot | UIFirstCharge, UIGolloesMonthCardPopUp, UIPrivacy2 | - |
| `DataCenter.HeroBountyDataManager` | 19 | MsgDefines.ReceiveHeroBountyTaskReward | OnHeroBountyOneTaskRefresh, OnHeroBountyTaskRefresh,... | - | - |
| `DataCenter.GuidePickGarbageBubbleManager` | 17 | - | - | - | - |
| `DataCenter.DeeplinkManager` | 16 | MsgDefines.LoginThirdPartWeb | WebLoginResult | - | - |
| `DataCenter.QuestArrowManager` | 15 | - | RefreshGuide, SU_QuestArrowStateChange | MainUI_SU | - |
| `DataCenter.NpcQAManager` | 11 | MsgDefines.UserNpcQuestion | - | - | - |
| `DataCenter.DailyMustBuyManager` | 10 | MsgDefines.DailyMustBuyList, MsgDefines.DailyMustBuyReward | OnDailyMustBuyDataChanged | - | - |
| `DataCenter.DailyPackageManager` | 10 | MsgDefines.GetDailyPackageInfos | RefreshWelfareRedDot | - | - |
| `DataCenter.QNManager` | 9 | MsgDefines.UserGetQuestionnaireList | QuestionnaireRefresh | - | - |
| `DataCenter.QuestTemplateManager` | 8 | - | - | - | TableName.QuestXml, TableName.getValue |
| `DataCenter.GuideTemplateManager` | 5 | - | - | - | TableName.Guide |
| `DataCenter.DailyTaskTemplateManager` | 2 | - | - | - | TableName.DailyQuest |

## 3. Key Wire Packets (134 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `account.login.new` | AccountLoginNew | `p=3` PutUtfString, PutInt | AccountManager.AccountLoginHandle | - |
| `achievement.info` | AchievementInfo | `p=1`  | AchievementManager.infoRequested | AchievementInfoUpdated |
| `achievement.reward.get` | AchievementRewardGet | `p=2` PutInt | AchievementManager.ApplyReward | AchievementInfoUpdated |
| `achievement.trophy.reward` | AchievementTrophyReward | `p=2` PutInt | AchievementManager.ApplyTrophyReward | AchievementInfoUpdated |
| `activity.engine.lucky.roll.receive.dail...` | - | `p=2` PutInt | ActLuckyRollInfo.UpdateStage | - |
| `activity.get.seven.day.login.info` | - | `p=2` PutInt | SlgDC.SlgSevenDayLoginData.ParseActivityData | - |
| `activity.missile.unlock.receive.daily.r...` | MissileUnlockReceiveDailyReward | `p=1`  | MissileUnlockManager.HandleReceiveDailyReward | - |
| `activity.missile.unlock.receive.state.d...` | MissileUnlockReceiveStateDailyReward | `p=1`  | MissileUnlockManager.HandleReceiveDailyReward | - |
| `activity.receive.seven.day.login.reward` | - | `p=4` PutInt | SlgDC.SlgSevenDayLoginData.GetRewardState | - |
| `activity.trade.swap.request` | SwapRequestMsg | `p=5` PutInt | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.swap.request.cancel` | SwapRequestCancelMsg | `p=3` PutInt, PutUtfString | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.swap.request.list` | SwapRequestListMsg | `p=2` PutInt | CastleAdventureManager.GetExchangeInfo | - |
| `assist.dispatch.mission` | DispatchAssist | `p=2` PutLong | RewardManager.ShowCommonReward | - |
| `az.account.login` | AccountLogin | `p=2` PutUtfString | AccountManager.AccountLoginHandle | - |
| `cake.team.task.change.push` | PushCakeTeamTaskChange | `p=1`  | CakeTeamManager.OnPushCakeTeamTaskChange | - |
| `cake.team.task.reward` | CakeTeamTaskReward | `p=3` PutInt | CakeTeamManager.OnCakeTeamTaskRewardResponse | - |
| `chapter.task` | ChapterTask | `p=2` PutUtfString, PutBool | ChapterTaskManager.ChapterTaskHandle | - |
| `custom.daily.package.preview` | GetDailyPackageInfos | `p=1`  | DailyPackageManager.UpdateDailyPackage | GetDailyPackageInfos |
| `custom.daily.package.select` | DailyPackageSelectHero | `p=2` PutUtfString | DailyPackageManager.OnChooseUpdate | DailyPackageSelectHero |
| `daily.must.list` | DailyMustBuyList | `p=1`  | DailyMustBuyManager.UpdateData | - |
| `daily.must.reward` | DailyMustBuyReward | `p=2` PutInt | RewardManager.ShowCommonReward | - |
| `daily.quest.ls` | DailyQuestLs | `p=1`  | DailyTaskManager.DailyQuestLsMessageHandle | - |
| `daily.quest.reward` | DailyQuestReward | `p=2` PutInt | DailyTaskManager.DailyQuestRewardMessageHandle | - |
| `daily.quest.reward.multi` | DailyQuestRewardMulti | `p=2` PutSFSArray | DailyTaskManager.DailyQuestRewardMessageHandle | - |
| `demon.hunter.quest.accept` | AcceptDemonHunterQuest | `p=3` PutLong | DemonHunterDataManager.HandleAcceptQuest | - |
| `demon.hunter.quest.drop` | DropDemonHunterQuest | `p=2` PutLong | DemonHunterDataManager.HandleDropQuest | - |
| `demon.hunter.quest.submit` | SubmitDemonHunterQuest | `p=2` PutLong | DemonHunterDataManager.HandleSubmitQuest | - |
| `dispatch.mission.status` | DispatchMissionStatus | `p=3` PutInt, PutLong | ActDispatchTaskDataManager.OnDispatchMissionStatusResponse | - |
| `dragon.assign.player` | DragonAssignPlayer | `p=4` PutUtfString, PutInt | ActDragonManager.SendGetPlayerList | - |
| `dragon.assign.player.info` | DragonAssignPlayerInfo | `p=1`  | ActDragonManager.HandleGetPlayerList | - |
| `dragon.auto.assign.player` | DragonAutoAssignPlayer | `p=2` PutInt | ActDragonManager.HandleGetPlayerList | - |
| `dragon.battle.sign.up` | DragonBattleSignUp | `p=3` PutInt | ActDragonManager.HandleSignUp | - |
| `dragon.change.commander` | DragonChangeCommander | `p=5` PutInt, PutLong, PutUtfString | BattleCommandManager.OnHandleUpdateCommandSign | - |
| `dragon.get.command.list` | DragonGetCommandList | `p=2` PutInt | BattleCommandManager.OnHandleGetAllCommandSign | - |
| `dragon.kick.member` | DragonKickMember | `p=3` PutUtfString, PutInt | DragonSwapManager.RequestMemberStatusInfo | - |
| `dragon.publish.commander` | DragonPublishCommander | `p=9` PutInt, PutUtfString, PutLong | BattleCommandManager.OnHandleSendCommandSign | - |
| `dragon.response.commander` | DragonResponseCommander | `p=4` PutUtfString, PutLong, PutInt | BattleCommandManager.OnHandleSendResponseSign | - |
| `dragon.swap.request` | DragonSwapRequest | `p=4` PutUtfString, PutInt | DragonSwapManager.OnSwapRequestResponse | - |
| `elite.new.receive.task.reward` | ChampionTaskReceive | `p=2` PutUtfString | ActChampionBattleManager.OnReceiveTaskReward | - |
| `elite.new.task.info` | ChampionTaskInfo | `p=1`  | ActChampionBattleManager.OnTaskInfoResponse | - |
| `exchange.enter.dragon.server` | ExchangeEnterDragonServer | `p=1`  | DragonSwapManager.ClearSwapRequest | EnterDragonWorld |
| `find.resource.point` | FindResourcePoint | `p=4` PutInt, PutUtfString | GuideManager.InGuide | END_SEARCH |
| `flip.fun.daily.reward` | FlipFunDailyReward | `p=2` PutInt | FlipFunManager.OnClaimDailyRewardResponse | - |
| `flip.fun.get.info` | FlipFunGetInfo | `p=2` PutInt | FlipFunManager.OnRequestInfoResponse | - |
| `get.all.chapter.info` | GetAllChapterInfo | `p=2`  | ChapterTaskManager.GetAllChapterInfoHandle | - |
| `get.challenge.act.task.info` | GetChallengeActTaskInfo | `p=2` PutInt | ActMonsterTowerData.GetActTaskInfoHandle | - |
| `get.dawn.day.act.info` | GetDawnDayActInfo | `p=2` PutInt | DawnTaskManager.GetDawnDayActInfoMessage | - |
| `get.dispatch.mission.info` | DispatchGetTasks | `p=1`  | ActDispatchTaskDataManager.UpdateAllSingleTasks | - |
| `get.dispatch.mission.record` | DispatchGetLog | `p=2` PutBool | ActDispatchTaskDataManager.GetTaskLog | - |
| `get.explore.pve.info` | LevelExploreGetInfo | `p=1`  | GuideManager.SetWaitingMessage | GuideWaitMessage |
| `get.guide.detect.event.info` | GetGuideDetectEventInfo | `p=2`  | GuideDetectEventManager.GetGuideDetectEventInfoHandle | - |
| `get.hero.assistance.info` | GetHeroAssistanceInfo | `p=1`  | AssistanceHeroDataManager.OnRequestFailed | - |
| `get.pve.push.level.info` | GetPvePushLevelInfo | `p=1`  | PveTaskManager.GetPveTaskHandle | - |
| `get.seven.day.buy.login.info` | GetSevenDayBuyLoginInfo | `p=2` PutInt | ActSevenLoginBuyData.ParseActivityData | - |
| `get.seven.day.login.info` | GetSevenDayLoginInfo | `p=2` PutInt | ActSevenLoginData.ParseActivityData | - |
| `get.wander.task` | GetWanderTask | `p=1`  | ActRoamingBossManager.HandleGetTaskInfo | - |
| `get.wander.task.reward` | GetWanderTaskReward | `p=2` PutSFSArray | RewardManager.AddRewards | - |
| `month.card.reward` | ClaimGolloesDailyReward | `p=2` PutUtfString | RewardManager.ShowCommonReward | - |
| `pinball.machine.daily.progress.reward` | PinballMachineDailyProgressReward | `p=3` PutInt | HalloweenMarbleManager.OnPinballMachineDailyProgressRewar... | - |
| `pinball.machine.emission` | PinballMachineEmission | `p=4` PutInt | HalloweenMarbleManager.OnPinballMachineEmissionResponse | HalloweenMarbleLaunchFailed |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (109 windows)

**Active HUD Buttons:** `RightBtn` [] @ (10.0%,88.4%), `HeadVX` [] @ (1.8%,87.5%)

**`GoToUtil` Routers:** `GoToUtil.GoDailyUI` -> [], `GoToUtil.GoDispatchTaskWindow` -> [], `GoToUtil.GotoQuestNew` -> ['UIHeroRecruit', 'UISearch'], `LuaWebRequest.DisposeRequest` -> [], `LuaWebRequest.OnRequestFailure` -> [], `LuaWebRequest.OnRequestSuccess` -> [], `LuaWebRequest.OnRequestTimeout` -> [], `LuaWebRequest.SendRequest` -> [], `LuaWebRequest.SetRequestHeader` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `MainUI_SU` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/SU_Main/UIPVEMainTableNew.prefab` | CheckBtnShow, CheckKillMonsterBtnShow, CheckShowRank... | - |
| `UIGuideArrow` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideArrow.prefab` | Button, OnClickJoystickBtn, OnClickNpcGirlGiveBtn, S... | - |
| `UIGuideArrowNew` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideArrow.prefab` | Button, OnClickJoystickBtn, OnClickNpcGirlGiveBtn, S... | - |
| `UIGuideIntroBubble1` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UIGuideIntroBubble1....` | Button, OnClickJoystickBtn, OnClickNpcGirlGiveBtn, S... | - |
| `UIHeroBountyTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroOfferReward....` | UIButton, close_btn, extra_desc_intro_btn, info_btn,... | MsgDefines.RefreshHeroBountyTask, MsgDefines.St... |
| `UIPrivacy2` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIAgreementSign.prefab` | Root/BigBtnAgree, Root/BigBtnAgree/btnText, Root/Com... | MsgDefines.UserAgreeTos |
| `UI_PicGuide` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UI_PicGuide_New.prefab` | UIButton, close_btn, close_btn_path, close_btn_text,... | - |
| `DispatchOneKey` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/U...` | GetColorsForToggle, IsTaskBelongToToggle, RefreshAll... | - |
| `WeekendChallengeCarStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChall...` | BtnCliam, BtnCliam/btnText, OnClickCloseBtn, UIButto... | - |
| `WeekendChallengeStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChall...` | BtnCliam, BtnCliam/btnText, OnClickCloseBtn, UIButto... | - |
| `UICommonGuideTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UICommonGuideTalk.prefab` | OnBtnClick, OnSevenDayNoteBtnClick, RefreshAutoBtn, ... | - |
| `UIFormationSelectListNew` | `UIContainer/Normal` | `-` | Music_Effect_Button, OnClickExchangeBtn, OnSelectTro... | - |
| `UIGuideIntroBubble` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UIGuideIntroBubble.p...` | Button, Toggle, UIButton, UIToggle, btn | - |
| `UIHeroEquipForgeMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipF...` | Music_Effect_Button, OnClickInfoBtn, OnClickItemBtn,... | - |
| `UIHeroRecruit` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruit.prefab` | Music_Effect_Button, btnRecruitOne, btnRecruitOneImg... | MsgDefines.LotteryHeroCard |
| `UI_GuideFullScreenDialog` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/SU_Common/UI_GuideFullScreenD...` | OnClickBtn, OnClickSkipBtn, UIButton, m_btn, m_skip_btn | - |
| `UIParkourBattleWin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIParkourBattleWin.prefab` | OnBtnContinueClick, autoContinueBtnText, btnContinue... | - |
| `UIShowBlack` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIShowBlack.prefab` | BtnCanClickTime, DeleteBtnTimer, btnTimer, next_btn,... | - |
| `UIJeepAdventureMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIJeepAdventu...` | gotoBtn, jumpLevelBtn, jumpLevelBtnText, rewardBtn | - |
| `UIPhonographMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographMain...` | btnNum, presentBtn, toggleAction, toggleText | - |
| `UI_VideoPlayer` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/SU_Common/UIVideoLayer.prefab` | OnClickBtnSkip, UIButton, btnShowSkip, m_btnSkip | - |
| `UICarChipGuidePopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipGuidePopu...` | UIButton, UICommonActGuide/BtnClose, buttonClose | - |
| `UIDragonExplainSign` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonExplain_Sign...` | isShowToggle, toggle, toggleTxt | - |
| `UIGuideTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideTalk1.prefab` | RefreshAutoBtn, btnAuto1, btnAuto2 | - |
| `UI_GuideMoviePrologue` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UI_GuideMoviePrologu...` | OnClickBtn, UIButton, m_btn | - |
| `UI_PicGuideList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UI_PicGuideList.prefab` | UIButton, closeBtn, closeBtn1 | - |
| `AttZombiePuzzleTaskPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/AttZombiePuzzl...` | Music_Effect_Button | MsgDefines.TaskRewardGet |
| `UIDawnTaskProgressReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDawnTaskPane...` | UIButton, closeBtn | - |
| `UIDetectNpcDinosaurRescue` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Dinosa...` | rewardBtn | MsgDefines.SU_ActCityPeople |
| `UIFormationDispatchTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroOfferReward1...` | rarity_btn | MsgDefines.DispatchStart |
| `UILWDispatchTaskLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/U...` | toggle1, toggleGroup | - |
| `UIMusicFestivalTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestiva...` | mBtnClaimAll | MsgDefines.TaskRewardBatch |
| `UISevenLogin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISevenLogin/UISevenLogin.prefab` | Music_Effect_Button | MsgDefines.ReceiveSevenDayLoginReward |
| `ChristmasActTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonat...` | - | MsgDefines.TaskRewardBatch |
| `UICarChipActivityMonsterBossReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivit...` | - | MsgDefines.TaskRewardBatch |
| `UICarComponActivityMonsterBossReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivit...` | - | MsgDefines.TaskRewardBatch |
| `UICrossWonderTarget` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderTa...` | - | MsgDefines.TaskRewardGet |
| `UIDetectNpc` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRadarCenter/UIDetectNpcEven...` | - | MsgDefines.SU_ActCityPeople |
| `UIGuideCommunicationTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideCommunicationTalk.p...` | btn_arrow | - |
| `UIGuideNoNpcTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideNoNpcTalk.prefab` | Music_Effect_Button | - |
| `UIGuideVideo` | `UIContainer/Info` | `Assets/Main/Prefabs/Guide/GuideVideo.prefab` | skip_btn | - |
| `UILogin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UILogin.prefab` | - | MsgDefines.AccountLogin |
| `UIMainChapterTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_MainTask/UIMainChapterTask...` | toggle | - |
| `UIRoleLogin` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIRoleLogin.prefab` | - | MsgDefines.UserCleanPost |
| `UISpeedUpConfirm` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UISpeedUpConfirm/UISpeedUpCon...` | - | MsgDefines.QueueCcdMNew |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `c_quest` | TableName.QuestXml | 8,828 | id, type, name, name_text, desc, desctype, para1, para2, order, position |
| `noviceboot` | TableName.Guide | 1,246 | id, returnstepid, savedoneid, jumptype, jumppara, jumpid, nextid, triggertype, triggerpara, ... |
| `noviceboot_B` | TableName.GuideB | 1,131 | id, returnstepid, savedoneid, jumptype, jumppara, jumpid, nextid, triggertype, triggerpara, ... |
| `world_quest` | TableName.WorldQuest | 168 | id, type, activity, desc, para1, para2, order |
| `questionAndAnswer` | TableName.QuestionAndAnswer | 128 | id, type, question, answers, answer, fraction, follow_time, level, reward_true |
| `aps_dispatch_tasks` | TableName.LwDispatchTask | 96 | id, name, desc, icon, model_name, color, task_star, refresh_pool, world_open, level |
| `daily_quest` | TableName.DailyQuest | 52 | id, accept1, name, desc, point, para2, gotype, gotype2, go, gobuild |
| `custom_dailypackage` | xmlValue.custom_dailypackage | 48 | id, item, condition, hero, hero_location, is_equip, arms_location, arms_location_2, is_wake,... |
| `night_demon_hunter_quest` | TableName.DemonHunterQuest | 13 | id, quest_pool, weight, quest_id, quest_name, quest_desc, quest_icon_small, quest_icon, ques... |
| `c_guide_pic` | TableName.SU_Guide_Pic | 6 | id, name, des, dub, noviceboot |

**Enums:** `GuideType` (250), `GuideTriggerType` (152), `QuestGoType` (98), `GuideJumpType` (79), `GuidePlayMovieType` (74), `GuideAnimObjectType` (68), `QuestDescType` (32), `LoginErrorMessage` (31), `LoginErrorCode` (25), `GuideMoveCameraType` (14), `SpecialGuideLogType` (13), `DragonSignState` (12), `SlgEnumDestinationSignalType` (10), `ActivityDailyType` (8), `EnumDestinationSignalType` (8), `GuideState` (8), `GuideTimeLineShowMarkerType` (8), `QuestType` (8), `HeroAdvanceGuideSignalType` (7), `WorldBlackTileGuideBtnType` (7), `DailyBoxActive` (5), `GuideArrowStyle` (5), `HeroGrowthTaskStatus` (5), `QuestDoType` (5), `SnowManTaskState` (5)
