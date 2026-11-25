# Domain Quick-Card: Events, Activities & Full Preparedness (`events_fullprep`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain events_fullprep`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **10** bot fns / **1** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **471** packets |
| `DataCenter` Managers & Singletons | **37** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **296** windows / **4** active HUD buttons / **25** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **60** tables / **83** enums / **41** live events / **109** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `run_treasure_helicopter` | `L1892-L2103` | GetDigTreasureReward, WorldGetDetail | DigTreasureDataManager, WorldPointManager |
| `_match_preparedness_actions` | `L2715-L2753` | - | - |
| `_execute_preparedness_actions` | `L2776-L2822` | - | - |
| `run_full_preparedness` | `L2825-L2879` | - | - |
| `_claim_full_preparedness` | `L2882-L3029` | AcceptPersonalReward, AcceptPersonalRewardBatch | ActPersonalArmsInfo, ActivityController, ActivityListDataManager |
| `run_mining_event` | `L6030-L6541` | BeginPvpCaveFight, ClaimMineCaveReward, GetMineCaveInfo, RefreshMin... | ActivityListDataManager, ArmyFormationDataManager, MineCaveManager |
| `_lua_trigger_pve_skip_snippet` | `L10179-L10270` | - | BattleLevel, LWBattleManager |
| `_ensure_exited_pve_cleanly` | `L10273-L10326` | - | BattleLevel, LWBattleManager |
| `_skip_active_pve_after_delay` | `L10329-L10342` | - | - |
| `action_mine_melee_refresh` | `L13107-L13176` | - | - |

**Hub `action_id` Routes:** `open_active_migration` (L4728)

## 2. `DataCenter` Managers & Outgoing Links (37)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.RadarCenterDataManager` | 107 | MsgDefines.DetectEventPveBatch, MsgDefines.DetectInfoGet, MsgD... | UpdateGold, UpdateRadarLevelEventsInfo | UIDetectEvent, UIDetectEventLevelUpgrade, UIPVE... | TableName.Desert |
| `DataCenter.SeasonDataManager` | 92 | MsgDefines.GetSeasonGroupServerInfo, MsgDefines.SeasonBalanceP... | DesertForceRefresh | - | TableName.Desert, TableName.SeasonDialog, Table... |
| `DataCenter.SweepManager` | 75 | MsgDefines.SweepDetail, MsgDefines.SweepExecute, MsgDefines.Sw... | SweepDetailUpdate, SweepExecuteResult, SweepInfoUpda... | - | - |
| `DataCenter.ActMonsterTowerData` | 74 | MsgDefines.GetChallengeActInfo | ActMonTowerBossKilled, ActMonTowerCallHelp, ActMonTo... | UIChatNew, UIMonsterTowerComing | TableName.ActivityMonsterBoss |
| `DataCenter.MoonlightCollectionDataManager` | 66 | - | ActivityTipStateUpdate, MoonlightCollectionDeployUpd... | UIActivityCenterTable, UISeasonMoonlightGetS5, ... | TableName.NightLunarLightCard, TableName.NightL... |
| `DataCenter.NightFallManager` | 57 | MsgDefines.GetSnowManActInfo | CheckDayNightState, OnDayNightChange, RefreshActivit... | UILWTrainScene, UISeasonNightFallsComing | - |
| `DataCenter.FactoryDataManager` | 41 | MsgDefines.UserCancelFactoryPanel | CanGetProduct, FactoryDataCancel | - | TableName.Factory |
| `DataCenter.LeagueMatchManager` | 40 | MsgDefines.GetCurSeasonLeagueMatchGroupInfo, MsgDefines.GetLas... | OnLastLeagueMatchGroupInfoUpdate, OnLeagueMatchBaseI... | - | - |
| `DataCenter.TroopActionManager` | 39 | - | END_SEARCH, MarchEndWithReward, ShowTroopAction | UIDetectEvent | - |
| `DataCenter.ActLuckyRollInfo` | 34 | - | self | - | - |
| `DataCenter.NightSacrificeManager` | 29 | MsgDefines.GatherRewardPacket | RefreshPacketReward | UISeasonNightSacrificePushS5 | TableName.ActivityPanel |
| `DataCenter.WorldSeasonObjectManager` | 27 | MsgDefines.GetPlaceObjects | PUSH_INIT_OK | - | TableName.SeasonObject |
| `DataCenter.ActDinosaurBossDataManager` | 26 | - | - | - | TableName.DinosaurBoss |
| `DataCenter.ActDrakeBossManager` | 26 | MsgDefines.GetUserDrakeBoss, MsgDefines.ItemUse | RefreshActivityRedDot, RefreshDrakeBoss | UIDrakeBossUseItem | - |
| `DataCenter.SU_EventSystem` | 25 | MsgDefines.SU_UpdateEvent | - | - | TableName.SU_C_Event |
| `DataCenter.RedEquipmentActivityManager` | 20 | - | OnEnterCrossServer, RedEquipActivityStateUpdate | - | - |
| `DataCenter.DayRechargeMonthCardManager` | 19 | MsgDefines.GetMonthPayActInfo, MsgDefines.ReceiveAllMonthPayRe... | GetRechargeMonthCardAllReward, GetRechargeMonthCardI... | - | - |
| `DataCenter.SeasonConfigManager` | 19 | - | - | - | TableName.SeasonConfig |
| `DataCenter.MinePlunderManager` | 16 | MsgDefines.GetActWorldResInfo | OnReceiveMinePlunderActivityInfo | - | TableName.ActivityPanel |
| `DataCenter.MuseumManager` | 16 | MsgDefines.UseTreasureSkill | FormationStaminaUpdate, OnTreasureInfoUpdate, OnTrea... | - | TableName.Museum |
| `DataCenter.ActivityTipManager` | 15 | - | ActivityTipStateUpdate | MainUI_SU, UIActivityTip | TableName.ActivityTip |
| `DataCenter.ActFirstChargeData` | 14 | MsgDefines.GetFirstChargeInfo, MsgDefines.ReceiveFirstChargeDa... | PlayerChangeHeadRedPot, RefreshWelfareRedDot | UIFirstCharge | - |
| `DataCenter.ChangeNameAndPicManager` | 14 | MsgDefines.GetUploadPicActivityInfo, MsgDefines.ReceiveUploadP... | RefreshActivityRedDot, RefreshChangeNameAndPic | - | - |
| `DataCenter.EventBubbleManager` | 14 | - | SU_ChangeViewHeight | - | TableName.PVETrigger |
| `DataCenter.SeasonGroupManager` | 13 | - | - | - | TableName.SeasonGroup |
| `DataCenter.SeasonWeekManager` | 12 | MsgDefines.SeasonWeekBuffGetInfo, MsgDefines.SeasonWeekBuffRec... | SeasonWeekUpdate | - | - |
| `DataCenter.BarterShopNoticeManager` | 11 | MsgDefines.KillMonsterActInfo, MsgDefines.KillMonsterStageReward | OnPassDay, RefreshKillMonsterActInfo | - | - |
| `DataCenter.DetectEventBubbleManager` | 10 | - | GetAllDetectInfo | - | - |
| `_G.EventManager` | 10 | - | - | - | - |
| `DataCenter.DroppedTreasureDataManager` | 9 | MsgDefines.GetChildhoodTreasureInfo | RefreshDroppedTreasureActivityInfo | - | - |
| `DataCenter.GroundPassManager` | 8 | - | LandRewardCollected | UIGroundPassUnlock | TableName.LandLock |
| `DataCenter.ActivityController` | 7 | MsgDefines.AcceptPersonalReward, MsgDefines.AcceptPersonalRewa... | - | - | - |
| `DataCenter.SeasonActivityPanelTemplateManager` | 6 | - | - | - | TableName.SeasonActivityPanel |
| `DataCenter.CharacterInfoMgr` | 5 | - | - | - | - |
| `DataCenter.DetectEventTemplateManager` | 5 | - | - | - | TableName.DetectEvent |
| `DataCenter.TroopActionTemplateManager` | 4 | - | - | - | TableName.TroopAction |
| `DataCenter.ActPersonalArmsInfo` | 2 | - | - | - | - |

## 3. Key Wire Packets (471 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `account.change.password` | AccountChangePassword | `p=3` PutUtfString | AccountManager.AccountChangePasswordHandle | - |
| `account.forget.password` | AccountForgetPassword | `p=2` PutUtfString | AccountManager.AccountForgetPasswordHandle | - |
| `activate.fossil.book.reward` | Season4FossilBookReward | `p=3` PutInt | Season4FossilCollectionManager.UpdateOneFossilCollectionB... | - |
| `active.fish` | ActiveFish | `p=2` PutInt | FishingCatalogDataManager.UpdateFishInfo | - |
| `active.golloes.carvan.open` | GolloesNewDataGet | `p=2` PutInt | GolloesCampManager.UpdateGolloesInfoNew | - |
| `active.golloes.carvan.reward` | ClaimGolloesRewardNew | `p=4` PutInt, PutUtfString | RewardManager.AddOneReward | - |
| `active.golloes.carvan.share.control` | GolloesShareControl | `p=3` PutInt | GolloesCampManager.HandelReceiveStateMesssage | - |
| `active.golloes.carvan.share.stat` | GolloesShareCheckMyState | `p=2`  | GolloesCampManager.HandelReceiveStateMesssage | - |
| `active.golloes.func` | ActiveGolloesFunc | `p=3` PutInt | GolloesCampManager.UpdateGolloesInfo | - |
| `activity.engine.lucky.roll.choose.item` | - | `p=4` PutInt | ActLuckyRollInfo.ChooseItemHandle | - |
| `activity.engine.lucky.roll.info` | - | `p=2` PutInt | ActLuckyRollInfo.ParseEventData | ActLuckyRollUpdate |
| `activity.engine.lucky.roll.lottery` | - | `p=6` PutInt | ActLuckyRollInfo.UpdateRollInfo | ActLuckyRollGetReward |
| `activity.engine.lucky.roll.notice.record` | - | `p=2` PutInt | ActLuckyRollInfo.UpdateNoticeRecord | LuckyRollBigRewardRankUpdate |
| `activity.engine.lucky.roll.receive.stag...` | - | `p=3` PutInt | ActLuckyRollInfo.UpdateStage | - |
| `activity.engine.lucky.roll.select` | - | `p=3` PutInt | ActLuckyRollInfo.SetRollSelect | ActLuckyRollSelect |
| `activity.get.spin.info` | - | `p=2` PutInt | SlgDC.SlgTreasureBoxTypeManager.ParseActivityData | - |
| `activity.missile.unlock.donate` | MissileUnlockDonate | `p=2` PutInt | MissileUnlockManager.HandleDonate | - |
| `activity.missile.unlock.get.info` | MissileUnlockGetInfo | `p=1`  | MissileUnlockManager.HandleGetInfo | - |
| `activity.panel.info` | ActivityPanelInfo | `p=1`  | ActivityListDataManager.InitActivityListData | - |
| `activity.season.shop.info` | SeasonShopInfoGet | `p=2` PutInt | Season4SpeciesShopManager.UpdateOneShopInfo | - |
| `activity.season.shop.refresh` | SeasonShopInfoRefresh | `p=2` PutInt | Season4SpeciesShopManager.UpdateOneShopInfo | - |
| `activity.spin.give.up.all` | - | `p=2` PutInt | SlgDC.SlgTreasureBoxTypeManager.HandleGiveUpAllMsg | - |
| `activity.spin.lottery` | - | `p=4` PutInt | SlgDC.SlgTreasureBoxTypeManager.HandleLotteryError | - |
| `activity.spin.pre.choose` | - | `p=3` PutInt, PutUtfString | SlgDC.SlgTreasureBoxTypeManager.HandlePreChooseMsg | - |
| `activity.trade.clear` | SwapTradeClear | `p=2` PutInt | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.exchange` | ExchangeMsg | `p=3` PutInt | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.random.reward` | ActivityTradeRandomReward | `p=4` PutInt, PutUtfString | RewardManager.ShowCommonReward | - |
| `activity.trade.reward.receive` | ActivityTradeRewardReceive | `p=3` PutInt | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.share` | SwapTradeShare | `p=3` PutInt, PutUtfString | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.swap` | SwapMsg | `p=3` PutInt, PutUtfString | CastleAdventureManager.GetExchangeInfo | - |
| `activity.trade.swap.record` | SwapRecordMsg | `p=2` PutInt | CastleAdventureManager.GetExchangeInfo | - |
| `auto.activity.dig` | StartAutoDig | `p=2` PutInt | DigActivityManager.OnRecvAutoDigResult | - |
| `auto.activity.dig.vertical` | StartAutoDigVertical | `p=2` PutInt | DigActivityManager.OnRecvAutoDigResult | - |
| `auto.finish.detect.event` | AutoFinishDetectEvent | `p=2` PutSFSArray | RadarCenterDataManager.UpdateOneDetectEventInfo | DetectInfoChange |
| `az.account.password.changed` | PushAccountChangePwd | `p=2`  | AccountManager.PushAccountChangePwdHandle | - |
| `batch.receive.detect.event.reward` | BatchDetectEventRewardReceive | `p=2` PutSFSArray | RadarCenterDataManager.GetDetectEventRewardBack | DetectEventRewardGet |
| `buy.activity.dig.goods` | BuyDigTool | `p=3` PutInt | DigActivityManager.OnRecvBuyItemRet | UpdateGold |
| `buy.activity.monopoly.goods` | BuyActivityMonopolyGoods | `p=3` PutInt | MonopolyActivityDataManager.BuyActivityMonopolyGoodsHandler | - |
| `buy.battle.pass.level` | BuyBattlePassLevel | `p=3` PutInt | ActBattlePassData.BuyBattlePassLevelHandle | - |
| `cake.team.bless` | CakeTeamBless | `p=4` PutInt, PutUtfString | CakeTeamManager.OnCakeTeamBlessResponse | - |
| `cake.team.confirm` | CakeTeamConfirm | `p=2` PutInt | CakeTeamManager.OnCakeTeamConfirmResponse | - |
| `cake.team.dynamic.info` | CakeTeamDynamicInfo | `p=2` PutInt | CakeTeamManager.OnCakeTeamDynamicInfoResponse | - |
| `cake.team.event.info` | CakeTeamEventInfo | `p=3` PutInt, PutUtfString | CakeTeamManager.OnCakeTeamEventInfoResponse | - |
| `cake.team.event.refresh` | CakeTeamEventRefresh | `p=3` PutInt, PutUtfString | CakeTeamManager.OnCakeTeamEventRefreshResponse | - |
| `cake.team.event.refresh.push` | PushCakeTeamEventRefresh | `p=1`  | CakeTeamManager.OnPushCakeTeamEventRefresh | - |
| `cake.team.event.submit` | CakeTeamEventSubmit | `p=6` PutInt, PutUtfString | CakeTeamManager.OnCakeTeamEventSubmitResponse | - |
| `cake.team.has.team` | CakeTeamHasTeam | `p=3` PutInt, PutUtfString | CakeTeamManager.OnCakeTeamHasTeamError | - |
| `cake.team.info` | CakeTeamInfo | `p=2` PutInt | CakeTeamManager.OnCakeTeamInfoResponse | - |
| `cake.team.invite.join` | CakeTeamInviteJoin | `p=5` PutInt, PutUtfString, PutLong | CakeTeamManager.OnCakeTeamInviteJoinResponse | - |
| `cake.team.make` | CakeTeamMake | `p=3` PutInt | CakeTeamManager.OnCakeTeamMakeResponse | - |
| `cake.team.progress.reward` | CakeTeamProgressReward | `p=3` PutInt | CakeTeamManager.OnCakeTeamProgressRewardResponse | - |
| `cake.team.push` | PushCakeTeam | `p=1`  | CakeTeamManager.OnPushCakeTeam | - |
| `cake.team.quit` | CakeTeamQuit | `p=2` PutInt | CakeTeamManager.OnCakeTeamQuitResponse | - |
| `call.challenge.act.boss` | CallChallengeActBoss | `p=2` PutInt | ActMonsterTowerData.CallBossHandle | - |
| `call.challenge.act.endless.boss` | CallChallengeActEndlessBoss | `p=2` PutInt | ActMonsterTowerData.CallEndlessBossHandle | - |
| `call.challenge.act.help` | CallChallengeActHelp | `p=2` PutInt | ActMonsterTowerData.CallBossHelpHandle | - |
| `championBattle.bet.cancel` | ChampionBattleBetCancel | `p=2` PutUtfString | ActChampionBattleManager.OnBetCancel | - |
| `championBattle.bet.info` | ChampionBattleBetRefresh | `p=2` PutInt | ActChampionBattleManager.OnNewBattleBetResponse | - |
| `championBattle.bet.match` | ChampionBattleMatch | `p=1`  | ActChampionBattleManager.OnGetBetMatch | - |
| `championBattle.bet.receive.reward` | ChampionBattleClaimBetReward | `p=2` PutUtfString | ActChampionBattleManager.OnGetBetReward | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (296 windows)

**Active HUD Buttons:** `holidayBtn` [Thanksgiving] @ (93.9%,15.2%), `SeasonBtn` [01d 21h] @ (97.8%,28.8%), `limitBtn` [Hot Events] @ (97.8%,15.2%), `btnActivity` [Event Center] @ (97.8%,8.3%)

**`GoToUtil` Routers:** `GoToResLack.GotoPeopleSatisfactionLack` -> [], `GoToResLack.GotoSeasonForceLack` -> ['UIResourceLackNew'], `GoToResLack.GotoSeasonGroundLack` -> [], `GoToResLack.GotoSeasonRadiateLack` -> [], `GoToUtil.GoActWindow` -> ['UIActivityCenterTable'], `GoToUtil.GoActWindowByType` -> ['UIActivityCenterTable'], `GoToUtil.GoFactory` -> [], `GoToUtil.GoSeasonDesertMaxLv` -> [], `GoToUtil.GoSeasonManager` -> [], `GoToUtil.GotoCarBattlePve` -> ['UIActivityCenterTable'], `GoToUtil.GotoCarChipActivity` -> ['UIActivityCenterTable'], `GoToUtil.GotoCarComponActivity` -> ['UIActivityCenterTable']

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UICrossWonderAct` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAc...` | IsRecordBtnVisible, LastClickMailBtn, Music_Effect_B... | - |
| `UIChampionBattleBattleInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampi...` | Root/TodayGuess/p_BtnSelect, Root/ToggleGroupSubTab/... | - |
| `UIBlackKnightMemberInfoMenu` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/...` | OnButtonCloseClick, OnButtonDetailClicked, OnButtonG... | - |
| `PayPasswordInputPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPayPassword/PayPasswordInpu...` | Music_Effect_Button, OnButtonCloseClicked, OnButtonC... | - |
| `UIGoldInsufficientPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/ThirdPayment/U...` | Music_Effect_Button, OnBtnBuyClick, OnBtnCloseClick,... | - |
| `UISeasonTradePostInfoView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeas...` | ClearToggleScrollView, Music_Effect_Button, OnToggle... | - |
| `UISeasonTradePostInfoViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradeP...` | ClearToggleScrollView, Music_Effect_Button, OnToggle... | - |
| `UIPlayerChangeHeadIcon` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIPlayerChangeHea...` | OnBtnIconClick, UIButton, close_btn, frame_btn, fram... | MsgDefines.UserChangePic, MsgDefines.UserDelete... |
| `UISeason4DinosaurEggHatchConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Dinosa...` | Btns/BtnBack, Btns/BtnBack/btnText, Btns/BtnConfirm,... | MsgDefines.SnowManReceiveSnowMan |
| `SetPayPasswordPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPayPassword/SetPayPasswordP...` | Music_Effect_Button, OnButtonCloseClicked, OnButtonC... | MsgDefines.SetPayPwd |
| `UIChampionBattleMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampi...` | SetHideButtons, SetShowRankBtn, SetShowRecordBtn, Sh... | - |
| `UIDragonSelectMemberAllinOne` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonSelectMember...` | BtnClick_SwitchPower, CheckTeamToggle, CheckToggle, ... | MsgDefines.AlArenaPower |
| `UIHeroEquipReplace` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipR...` | Music_Effect_Button, OnDownBtnClick, OnGetEquipBtnCl... | - |
| `UISeasonIceCaveInfoPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/...` | ClearToggleScrollView, IceCaveToggleType, ToggleClic... | - |
| `UIDragonEggPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Dinosa...` | Btns/BtnGet, Btns/BtnGet/btnText, OnClickCloseBtn, S... | - |
| `UIBlackKnightMemberInfoPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/...` | BtnRefresh, BtnRefresh/btnText, OnButtonIntelligence... | - |
| `UIFoodRedenvelopeSelectView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/FoodFestivalRed...` | ImgBg/BigBtnChoose, ImgBg/BigBtnChoose/btnText, Musi... | - |
| `UIParkourBattleMain` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/ParkourBattle/UIParkourBattle...` | Barrel_ShowBtnDefence, Common_Btn_Defence_out, PlayF... | - |
| `UIRedEquipmentActivityUpcomingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRedGear/UIRedGearPopuop.prefab` | OnButtonGotoClicked, Root/BigBtnYellow, Root/BigBtnY... | - |
| `SevenDayBoxNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/SevenDay/Seven...` | ReceiveBtnClick, UIButton, UICommonPopUpTitle/CloseB... | - |
| `UIBlackKnightPlayerTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/...` | BtnClose, OnButtonCloseClick, Root/Btn, Root/Btn/btn... | - |
| `UICarChipActivityUpcomingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivit...` | OnButtonGotoClicked, Root/Btn, Root/Btn/btnText, UIB... | - |
| `UICarComponActivityUpcomingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarComponActiv...` | OnButtonGotoClicked, Root/Btn, Root/Btn/btnText, UIB... | - |
| `UISeason4FossilCollection` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Fossil...` | Music_Effect_Button, RefreshRedBtn, btnLeft, btnRigh... | MsgDefines.GetSeason4FossilBookInfo |
| `ActivityTip` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/ActivityCenter/ActivityTip/Ac...` | Music_Effect_Button, OnClickGotoBtn, UIButton, banne... | - |
| `UIChampionBattleReward4Server` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampi...` | goSubToggle, goToggleRedPoint3, toggle1, toggle1Sub,... | - |
| `UIHalloweenDrawLotteryLogView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDr...` | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle | MsgDefines.LotteryMachineActivityGiftRecord |
| `UILuckyShopPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UILuckyShop/UI...` | ToggleGroupBg, UIButton, bgBtnN, closeBtnN, toggleGr... | - |
| `UIMonsterTowerTips` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/U...` | ClickBtn, UIButton, btn_choice_path, return_btn, ret... | - |
| `BarterShopNotice2Stage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/BarterShopNoti...` | OnClickCloseBtn, UIButton, bgBtnN, bgBtn_path, close... | - |
| `FoodFestivalRedEnvelopeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/FoodFestivalRed...` | Music_Effect_Button, UIButton, _sendRed_btn, btn_sen... | - |
| `UIActBossTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossTip.prefab` | Root/Button, Root/Button/btnTxt, UIButton, btn, btnP... | - |
| `UIActMonsterTowerDiffTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/U...` | UIButton, _choice_btn, btn_choice_path, return_btn, ... | MsgDefines.ChooseChallengeActDifficulty |
| `UIActivityCenterTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIActivityCent...` | Music_Effect_Button, UIButton, bottomCloseBtn | MsgDefines.ReceiveDonateArmyTaskReward, MsgDefi... |
| `UIDonateSoldierReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldie...` | CheckBtnState, get_advance_reward_btn, get_advance_r... | MsgDefines.ReceiveDonateArmyStageReward |
| `UIDragonBattleResult` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonBattleResult...` | Music_Effect_Button, OnReturnBtnClick, UIButton, ret... | MsgDefines.ExitDragonServer |
| `UIDragonSelectMemberSortFilter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonSelectMember...` | InitTimeToggles, RefreshTimeTypeBtnUI, _notVotedBtnI... | - |
| `UIDragonSelectMemberTeam` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonSelectMember...` | BtnClick_SwitchPower, CheckToggle, btnExplain, switc... | MsgDefines.AlArenaPower |
| `UIHalloweenDrawCardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDr...` | SetBtnSkipStatus, mBtnLotter10Image, mBtnLotter1Imag... | MsgDefines.LotteryMachineActivityLottery |
| `UIHalloweenDrawRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDr...` | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle | - |
| `UIHalloweenLevelReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallo...` | SetRewardBtn, UpdateBigRewardJumpBtn, mBtnJumUpActiv... | - |
| `UISeasonMoonlightSelectS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonli...` | Music_Effect_Button, ToggleFilterList, btnNum, btn_d... | MsgDefines.MoonlightCollectionDeploy |
| `UISeasonTradePostStore` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeas...` | buyNumBtn, openBtn, saleBtn, taxBtn | MsgDefines.TradeStoreBuyItem, MsgDefines.TradeS... |
| `UISeasonTradePostStoreS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradeP...` | buyNumBtn, openBtn, saleBtn, taxBtn | MsgDefines.TradeStoreBuyItem, MsgDefines.TradeS... |
| `MonopolyActivityDrawStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonopolyActivi...` | RefreshToggle, Toggle1, Toggle2, ToggleTag, toggleTag | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `battlepass` | TableName.BattlePass | 4,201 | id, activity_panel_Id, level, levelup_exp, free_reward, pay_reward, highlight_reward, pay_it... |
| `detect_event` | TableName.DetectEvent | 3,275 | id, type, type2, name, description, quality, icon, banner_image, panel_banner, para |
| `activity_dig_para` | TableName.DigActivityPara | 2,125 | id, dig_id, level, goods_normal, rate, rate_rare, guarantee |
| `aps_season_group` | TableName.SeasonGroup | 1,351 | id, season, seasonPlayType, seasonPlayTypeclient, server, season_show, season_name, season_i... |
| `activity_panel` | TableName.ActivityPanel | 773 | id, type, age_restriction, name, order, desc_info, story, needMainCityLevel, list_icon, Adve... |
| `AcitivitySeven_New` | TableName.ActSeven | 620 | id, type1, type1_text, type2, type2_text, task |
| `lw_base_visitor_event` | TableName.LwBaseVisitorEvent | 480 | id, type, para, name, desc, hero_icon, hero_halfbody, color, model_path, dialog |
| `season_mastery_b` | xmlValue.season_mastery_b | 449 | id, group, home, type, name, detaildescription, description, icon, needLv, season |
| `season_mastery` | TableName.Mastery | 399 | id, group, home, type, name, detaildescription, description, icon, needLv, season |
| `APS_arms` | TableName.ArmsTab | 393 | id, name, description, quality, max_train, resource_need, time, treat_time, treat_resource, ... |
| `activity_barter` | TableName.ActivityBarter | 276 | id, activity_id, item1, item2, times, not_reset, vip, is_decoration_gift, gift_goods, gift_r... |
| `activity_cyclebox_para` | TableName.ActivityCycleboxPara | 162 | id, box_id, order, reward_group, goods, rate, show_rate, guarantee |
| `activity_treasure_hunt` | TableName.ActivityTreasureHunt | 160 | id, level, activity, layout_id, layout_rate, reward |
| `activity_treasure_hunt_para` | TableName.ActivityTreasureHuntPara | 116 | id, map_width, map_height, treasure_layout |
| `c_event` | TableName.SU_C_Event | 102 | id, level, pre_type, pre_para1, check_immediately, do_noviceboot, noviceboot_drive, do_type,... |
| `activity_boxopen_para` | TableName.ActivityBoxOpenPara | 101 | id, boxopen_id, type, goods, rate, guarantee_activity, order, reward_buy_time, reward_hold_t... |
| `activity_treasure_para` | TableName.ActivityTreasurePara | 97 | id, type, horizontal, vertical, picture, shape_pic, rotate, group, bomb, reward |
| `DayAct` | TableName.DayAct | 87 | id, type1, type1_text, type2, type2_text, title, dialog, daily_bg, reward_show |
| `activity_item_drop` | TableName.ActivityItemDrop | 86 | id, activity, type, good, limit, para, para1, para2, reward, icon |
| `season_dialog` | TableName.SeasonDialog | 62 | id, season_dialog |
| `season_activity_panel` | TableName.SeasonActivityPanel | 60 | id, title_group, season_panel_group, world_season, type, is_main, panel_id, order, size_type... |
| `aps_factory` | TableName.Factory | 45 | id, name, build_type, unlock_type, unlock_condition, input_resource_goods, time, get_resourc... |
| `c_vfx_act` | TableName.PveActVFX | 37 | id, name, atk_eff, behit_eff, death_act, atk_eff_right, atk_eff_sence, atk_eff_fire, fly_eff |
| `season_influence` | TableName.SeasonInfluence | 37 | id, influence, influence_b, influence_new, name, pic, star, box, resistance, reward |
| `season_active_skill` | TableName.MasterySkill | 33 | id, type, needId, goto, use_position, name, icon, description, des_value, CDType |
| `lw_hit_reaction` | TableName.LW_Hit_Reaction | 32 | id, hit_animation, dead_move, hit_shake, hit_zoom, death_effect_nomal, death_effect_nomal_fo... |
| `activity_santa_reward` | TableName.SantaStageReward | 31 | id, group_id, level, distance, reward_token, reward_other |
| `activity_spin_para` | SlgTableName.ActivityTreasureBoxPara | 26 | id, spin_id, pool_id, goods, spin_item, item_priority, spin_item_icon, spin_bg_icon, reward_... |
| `c_pveSkillAction` | TableName.SU_PveSKillAction | 24 | id, type, speed, action, actionEffect, attacktype, para1, para2, damage, para3 |
| `activity_santa_upgrade` | TableName.SantaStageUpgrade | 20 | id, group_id, level, power_add, power_consume, speed_add, speed_consume, shield_add, shield_... |
| `activity_monster` | TableName.ActivityMonster | 19 | id, difficulty_des, monster, description, monster_des, icon, difficulty_title, icon_detail, ... |
| `activity_santa_stage_data` | TableName.SantaStageData | 16 | id, para1, para2, length |
| `activity_cake_team_cake` | TableName.ActivityCakeTeamCake | 15 | id, cake_group_id, cake_level, cake_progress_value, cake_reward |
| `season_object` | TableName.SeasonObject | 14 | id, type, skill, value1, value2, value3, prefab, area, name, description |
| `troop_action` | TableName.TroopAction | 13 | id, type, dialogID, rate, stay_time, show_time |

**Enums:** `DetectEventType` (29), `ActPopUIType` (28), `ActMonsterTowerDiff` (18), `ActivityEventType` (16), `TreasureBoxSpinConfig` (16), `TroopActionType` (13), `SeasonConfigId` (11), `ActivityOverviewType` (10), `SerWorldMarkPrefabPath` (10), `ActivityShowLocation` (9), `ActivityTipConditionType` (9), `SlgActivityShowLocation` (9), `ActivityTipEntranceType` (7), `Activity_ChampionBattle_Elite_Stage_State` (7), `CrossWonderActState` (7), `DetectEventColor` (7), `DetectHelpEventColorImage` (7), `FoodFestivalEatStatus` (7), `IceCaveActOpenState` (7), `ActionPhase` (6), `Activity_ChampionBattle_Stage_State` (6), `AlCompeteActName` (6), `DragonActStage` (6), `OverviewToActType` (6), `SeasonStage` (6)
