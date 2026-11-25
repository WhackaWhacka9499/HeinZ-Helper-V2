# Domain Quick-Card: Arena & PVP (`arena_pvp`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain arena_pvp`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **2** tasks / **4** bot fns / **0** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **196** packets |
| `DataCenter` Managers & Singletons | **29** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **120** windows / **0** active HUD buttons / **0** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **7** tables / **20** enums / **16** live events / **13** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Task Key | Title | Tag |
|---|---|---|
| `arena` | Arena Battles (x5) | `70%+ Win Odds` |
| `hero_battlefield` | Hero Battlefield (Quick Deploy + Auto-Skip) | `Quick Deploy • Auto-Skip` |

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `run_hero_battlefield` | `L6940-L7489` | - | ArmyFormationDataManager, ArmyFormationManager, BattleLevel, CarChi... |
| `_arena_round_win_prob` | `L7492-L7499` | - | - |
| `_arena_best_matchup` | `L7502-L7570` | - | - |
| `run_arena` | `L7573-L8097` | GetArenaInfo, GetCrossArenaInfo, RefreshArenaChallenge, RefreshCros... | ArenaManager, BattleLevel, CrossArenaManager, HeroDataManager, Towe... |

## 2. `DataCenter` Managers & Outgoing Links (29)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `_G.PveActorMgr` | 185 | MsgDefines.BeginPvpCaveFight, MsgDefines.GetCrossArenaUserEffe... | OnEmBattleHeroChanged, PVEBattleSetLeftBuffData, PVE... | UIBarrelHeroBottomInfo, UIPVEHeroAppear, UIPVEH... | TableName.Army_B, TableName.Car_Show_Barrel, Ta... |
| `DataCenter.DesertDataManager` | 136 | MsgDefines.AlRank, MsgDefines.UserCancelGiveUpDesert, MsgDefin... | ActDesertForceGroupRank, CheckGatherSeasonResRedDot,... | RemoveDesertOccupyDelayTimer, UIAlNoticeScoreTi... | TableName.Desert, TableName.SeasonInfluence |
| `DataCenter.ActChampionBattleManager` | 112 | MsgDefines.ACT_CHAMPIONBATTLE_BET, MsgDefines.ACT_CHAMPIONBATT... | ChampionBattleBetMatchRefresh, ChampionBattleBetReco... | ChampionServerRewardGet, LFChampionBattleFight | - |
| `DataCenter.GovernmentManager` | 107 | MsgDefines.ChooseKing, MsgDefines.GetKingHistory, MsgDefines.G... | ApplyPosConditionSet, GovernmentHistoryRecordRefresh... | UIThroneKingdomAssumedsuccessfull, UITransferKing | TableName.EffectNumDesc |
| `DataCenter.DigActivityManager` | 86 | MsgDefines.BuyDigTool, MsgDefines.DigOneBlockVertical, MsgDefi... | CheckDigRewardRedPoint, GetBalloonPuzzleInfo, OnDigA... | UIGiftBoxPackageList, UIMultiBuy | TableName.ActivityPanel, TableName.DigActivityDig |
| `DataCenter.StoryManager` | 74 | MsgDefines.GetStoryInfo, MsgDefines.GetStoryRank, MsgDefines.G... | ChangeStoryScene, MainLvUp, StoryGetInfo, StoryGetRank | - | - |
| `DataCenter.ActRoamingBossManager` | 68 | MsgDefines.GetWanderBossRecord, MsgDefines.GetWanderDmgRank, M... | OnTalkToAnimalReward, RoamingBossGeTBossInfo, Roamin... | UIDetectNpcDinosaurRescue, UIPositionShare | TableName.Monster, TableName.RoamingBossRewardShow |
| `DataCenter.OverlordManager` | 63 | MsgDefines.OverlordChangeNameMessage, MsgDefines.OverlordCureM... | BuildRedDotRecord, OverlordDataUpdated, OverlordFile... | UIOverlordChallengePop | - |
| `DataCenter.ActivityALVSDonateSoldierManager` | 60 | MsgDefines.ALVSDonateArmyDeclareWar, MsgDefines.ALVSDonateArmy... | ALVSDeclareAllianceListReturn, ALVSDonateArmyBattleI... | - | - |
| `DataCenter.LandingOperationsDataManager` | 58 | MsgDefines.GetHeroBattleRank, MsgDefines.HeroBattleSetTargetCh... | LandingOperationQuickFightEnd, LandingOperationRank,... | - | - |
| `DataCenter.GloryWarSwapManager` | 55 | MsgDefines.KingdomSwapExec, MsgDefines.KingdomSwapInfo, MsgDef... | GloryWarSwapExecFailed, GloryWarSwapExecSuccess, Glo... | UIGloryWarSwapTip | - |
| `DataCenter.DecorationDataManager` | 52 | MsgDefines.CoverSkin, MsgDefines.GetTitleRank, MsgDefines.Take... | ChangeSex, UpdatePlayerHeadIcon, UserSkinUpdate | UIDecorationUpgradeSuccess, UITitleDetail, Unlo... | TableName.Decoration |
| `DataCenter.FrozenLandDataManager` | 52 | MsgDefines.CallHelpAnimal, MsgDefines.FindIceAnimal, MsgDefine... | LoadMapDataFromFileFinish, OnGetFrozenLandStageRewar... | UIDetectNpc | TableName.IceAnimals, TableName.WorldCity |
| `DataCenter.SnowManManager` | 52 | MsgDefines.GetSnowManActInfo, MsgDefines.SnowManAddExp, MsgDef... | OpenUI, RefreshActivityRedDot, SnowManUpdateRedCount... | UIWorldPoint | TableName.SnowMan |
| `DataCenter.LikeManager` | 50 | MsgDefines.AddLike, MsgDefines.CancelLike, MsgDefines.GetGiftL... | DemonHunterLikeUpdate, MainLvUp, RefreshAddLike, Ref... | UILike, UILikeMessageBigTips, UILikeMessageTips | - |
| `DataCenter.ActivityDonateSoldierManager` | 47 | MsgDefines.GetDonateArmyActivityInfo, MsgDefines.GetDonateArmy... | DonateSoldier, GetDonateArmyActivityInfo, GetDonateA... | - | - |
| `DataCenter.KingdomSwapManager` | 47 | MsgDefines.KingdomSwapExec, MsgDefines.KingdomSwapFavorite, Ms... | KingdomSwapExecSuccess, KingdomSwapFavorUpdate, King... | UIKingdomSwapTip | - |
| `DataCenter.AchievementManager` | 45 | MsgDefines.AchievementInfo, MsgDefines.AchievementRank | - | - | - |
| `DataCenter.CrossHitBlockManager` | 37 | MsgDefines.GetCrossDesertBox, MsgDefines.GetCrossDesertInfo, M... | UpdateDesertRank, UpdateHitBlockBoxReward, UpdateHit... | - | - |
| `DataCenter.WorldHotNewsManager` | 37 | MsgDefines.HotNewsLandInfo, MsgDefines.HotNewsRankInfo | ChangeCameraLod, ChatNewsUpdate, RefreshHotPoint, Re... | UIHotNewsPointDetail | - |
| `DataCenter.ActTimeCompeDataManager` | 26 | MsgDefines.TimeCompetitionRank | LWLandLockFinish, RefreshCompeRankData | UIGiftPackageRewardGet | TableName.FakePlayer |
| `DataCenter.CarChipActivityManager` | 25 | MsgDefines.CarChipActivityClaimPreviewReward, MsgDefines.CarCh... | CarChipActivityChipMemberInfoUpdate, CarChipActivity... | - | - |
| `DataCenter.CarComponActivityManager` | 25 | MsgDefines.CarChipActivityClaimPreviewReward, MsgDefines.CarCh... | CarComponActivityClaimRewardResponse, CarComponActiv... | - | - |
| `DataCenter.ArenaManager` | 22 | MsgDefines.GetArenaInfo, MsgDefines.GetArenaLatestInfo, MsgDef... | AreanRankDataUpdated | - | - |
| `DataCenter.SmallPeopleDataManager` | 21 | MsgDefines.SmallPeopleUpgradeRank, MsgDefines.SurvivalVisitorR... | SmallPeopleAddNew, SmallPeopleDelete | - | TableName.HeroAppearance, TableName.LwBaseVisit... |
| `DataCenter.WorldTrendManager` | 21 | MsgDefines.ServerTrendsInfo, MsgDefines.ServerTrendsRank, MsgD... | WorldTrendRedUpdate, WorldTrendRefresh, WorldTrendRe... | - | - |
| `DataCenter.RankDataManager` | 15 | - | - | - | - |
| `DataCenter.CrossArenaManager` | 14 | MsgDefines.GetCrossArenaInfo, MsgDefines.GetCrossArenaLatestIn... | AreanRankDataUpdated | - | - |
| `DataCenter.XiaoRenRankTemplateManager` | 5 | - | - | - | TableName.XiaoRenRank |

## 3. Key Wire Packets (196 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `achievement.rank` | AchievementRank | `p=1`  | AchievementManager.ApplyRank | AchievementRankUpdated |
| `activity.engine.lucky.roll.rank` | - | `p=2` PutInt | ActLuckyRollInfo.GetCardRankHandle | - |
| `activity.missile.unlock.get.player.rank` | MissileUnlockPlayerRank | `p=2` PutInt | MissileUnlockManager.HandlePlayerRank | - |
| `activity.missile.unlock.get.state.rank` | MissileUnlockStateRank | `p=2` PutInt | MissileUnlockManager.HandleStateRank | - |
| `activity.spin.rank` | - | `p=2` PutInt | SlgDC.SlgTreasureBoxTypeManager.GetBoxRankHandle | - |
| `blood.moon.rank.get` | BloodMoonRankGet | `p=3` PutInt, PutBool | ActBloodMoonManager.BloodMoonRankGetHandle | - |
| `building.rank` | PlayerBaseRankList | `p=3` PutInt | RankDataManager.ParsePlayerRankData | PlayerRank |
| `cake.team.rank.info` | CakeTeamRankInfo | `p=2` PutInt | CakeTeamManager.OnCakeTeamRankInfoResponse | - |
| `check.skin.own` | CheckSkinOwn | `p=4` PutInt, PutUtfString | SkinGiftManager.OnCheckSkinOwnResponse | - |
| `choose.king` | ChooseKing | `p=2` PutUtfString | GovernmentManager.ChooseKingHandler | - |
| `christmas.parkour.rank.info` | ChristmasParkourRankInfo | `p=3` PutInt | ChristmasActManager.UpdateParkourRankInfo | - |
| `christmas.parkour.rank.reward` | ChristmasParkourRankReward | `p=3` PutInt | ChristmasActManager.UpdateParkourRankReward | - |
| `christmas.tree2.rank.personal` | ChristmasTreeRankPersonal | `p=2` PutInt | ChristmasActManager.ReceiveChristmasTreeRankPersonal | - |
| `christmas.tree2.rank.reward` | ChristmasTreeRankReward | `p=3` PutInt | ChristmasActManager.ReceiveChristmasTreeRankReward | - |
| `cross.server.rank` | CrossServerRank | `p=2` PutInt | RankDataManager.ParsePlayerRankData | PlayerRank |
| `desert.force.self.rank` | DesertForceSelfRank | `p=1`  | DesertDataManager.SetSelfForceRank | ForceSelfRank |
| `desert.force.server.rank` | DesertForceServerRank | `p=3` PutInt | DesertDataManager.SetDesertRankList | - |
| `fill.individuel.order` | IndividualOrderFill | `p=4` PutLong, PutInt | ActIndividualOrderManager.HandleMessageFill | OnQuestRedCountChanged |
| `fill.individuel.order.batch` | IndividualOrderFillBatch | `p=2` PutSFSArray, PutLong, PutInt | ActIndividualOrderManager.HandleMessageFillBatch | OnQuestRedCountChanged |
| `get.activity.level.rank` | PveActGetRank | `p=2` PutInt | PveActManager.HandleGetRank | - |
| `get.blood.float.rank` | GetBloodFloatRank | `p=2` PutLong | ActBloodMoonManager.GetBloodFloatRankHandle | - |
| `get.challenge.act.endless.boss.rank` | GetChallengeActEndlessBossRank | `p=2` PutInt | ActMonsterTowerData.EndlessBossRankHandle | - |
| `get.dig.rank` | GetDigActivityRankInfo | `p=2` PutInt | DigActivityManager.OnRecvDigRankResp | - |
| `get.discount.shop.rank` | GetDiscountShopRank | `p=2` PutInt | LuckyShopManager.GetDiscountShopRank | - |
| `get.ghost.king.activity.info` | GhostKingInfo | `p=1`  | GhostKingBornManager.HandleGhostKingInfoMessage | - |
| `get.ghost.king.rank.info` | GhostKingRankInfo | `p=2` PutBool | GhostKingBornManager.HandleGhostKingRankMessage | - |
| `get.ghost.king.rank.reward` | GhostKingRewardInfo | `p=1`  | GhostKingBornManager.HandleGhostKingRewardMessage | - |
| `get.gift.box.rank` | GetGiftBoxRank | `p=2` PutInt | ActGiftBoxData.GetBoxRankHandle | - |
| `get.gift.like.rank` | GetGiftLikeRank | `p=2` PutUtfString | LikeManager.HandleGetLikeRank | - |
| `get.golloes.card.rank` | GetGolloesCardRank | `p=2` PutInt | ActGolloesCardData.GetCardRankHandle | - |
| `get.greeting.card.info` | GetGreetingCardInfo | `p=2` PutInt | SkinGiftManager.OnGetGreetingCardInfoResponse | - |
| `get.hero.battle.rank` | GetHeroBattleRank | `p=3` PutInt | LandingOperationsDataManager.ParseRankHandle | - |
| `get.hero.equip.rank` | GetHeroEquipRank | `p=1`  | HeroEquipRankManager.GetHeroEquipRankHandler | - |
| `get.hero.equip.rank.by.slot` | GetHeroEquipRankBySlot | `p=2` PutUtfString | HeroEquipRankManager.GetHeroEquipRankBySlotHandler | - |
| `get.history.king.record` | GetKingHistory | `p=3` PutInt | GovernmentManager.GetKingHistoryHandler | - |
| `get.ice.cave.user.rank.info` | GetIceCaveUserRankInfo | `p=1`  | ActIceCaveManager.GetaIceCaveUserRankInfoHandle | - |
| `get.individuel.order.info` | IndividualOrderGetInfo | `p=1`  | ActIndividualOrderManager.HandleMessageGetInfo | - |
| `get.jigsaw.rank` | GetJigsawRankInfo | `p=3` PutInt | JigsawPuzzleManager.UpdateRankInfo | - |
| `get.king.info` | GetKingInfo | `p=2` PutInt | GovernmentManager.GetKingInfoHandler | - |
| `get.kingdom.position.history` | GetKingdomPosHistory | `p=2` PutUtfString | GovernmentManager.GetKingdomPosHistoryHandler | - |
| `get.kingdom.positions` | GetKingdomPositions | `p=2` PutInt | GovernmentManager.GetKingdomPositionsHandler | - |
| `get.kingdom.present.info` | GetKingdomPresentInfo | `p=2` PutInt | GovernmentManager.GetKingdomPresentInfoHandler | - |
| `get.kingdom.present.record` | GetKingdomPresentRecord | `p=2` PutInt | GovernmentManager.GetKingdomPresentRecordHandler | - |
| `get.like.activity.rank` | GetLikeActivityRank | `p=2` PutInt | LikeRankActManager.HandleRankInfo | - |
| `get.luck.roll.rank` | GetLuckRollRank | `p=2` PutInt | ActLuckyRollInfo.GetCardRankHandle | - |
| `get.mysterious.rank` | GetMysteriousRankInfo | `p=2` PutInt | MysteriousManager.OnRecvRankInfo | - |
| `get.new.cross.desert.user.rank` | GetCrossDesertRank | `p=1`  | CrossHitBlockManager.UpdateDesertRank | - |
| `get.person.arms.group.rank` | PersonalArmsGetRank | `p=2` PutUtfString | PersonalArmsDataManager.OnRecvRankListResp | - |
| `get.person.arms.group.rank.reward` | PersonalArmsGetRankReward | `p=2` PutUtfString | PersonalArmsDataManager.OnRecvRankRewardListResp | - |
| `get.pirate.siege.rank.info` | GetDonateArmyRankMessage | `p=2` PutInt | ActivityDonateSoldierManager.OnGetDonateSoldierRankData | - |
| `get.puzzle.boss.rank.reward.info` | GetPuzzleBossRankRewardInfo | `p=2` PutLong | ActivityPuzzleDataManager.HandleMessageGetPuzzleBossRankR... | - |
| `get.refresh.desert.activity.info` | GetRefreshDesertActivityInfo | `p=2` PutInt | PresidentMineRefreshManager.GetRefreshDesertActivityInfoH... | - |
| `get.season.actboss.rankreward` | GetSeasonActBossRankReward | `p=1`  | ActDinosaurBossDataManager.SetRewardFromServer | RefreshDinosaurBossRank |
| `get.skin.gift.act.info` | GetSkinGiftActInfo | `p=2` PutInt | SkinGiftManager.OnGetSkinGiftActInfoResponse | - |
| `get.story.rank` | GetStoryRank | `p=1`  | StoryManager.HandleGetRank | - |
| `get.tank.chip.target.rank` | CarChipActivityGetChipPowerRank | `p=2` PutInt | ActivityListDataManager.GetActivityDataById | - |
| `get.trade.post.user.rank.info` | GetTradeCityRankInfo | `p=1`  | ActTradePostManager.GetCityRankInfoHandle | - |
| `get.wander.dmg.rank` | GetWanderDmgRank | `p=2` PutBool | ActRoamingBossManager.HandleGetRankInfo | - |
| `gift.skin` | GiftSkin | `p=5` PutInt, PutUtfString | SkinGiftManager.OnGiftSkinResponse | - |
| `hero.battle.set.target.chapter` | HeroBattleSetTargetChapter | `p=4` PutInt | LandingOperationsDataManager.HandleTargetChapter | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (120 windows)

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIPVEScene` | `UIContainer/Backg...` | `Assets/Main/Prefabs/Guide2/UIGuidePioneer.prefab` | Barrel_ToggleFormationHeroLevelBar, CheckOnekeyFillH... | - |
| `UIHeroMilitaryRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMilitaryRank...` | CheckArrowBtns, Music_Effect_Button, OnClickBtnGoto,... | MsgDefines.GetHeroWakeSkin, MsgDefines.HeroRank... |
| `UIGiftBoxRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIGift...` | ToggleGroupSubTab/Toggle1, ToggleGroupSubTab/Toggle1... | - |
| `UILuckyRollRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/UILu...` | ToggleGroupSubTab/Toggle1, ToggleGroupSubTab/Toggle1... | - |
| `UIFormationArena3V3New` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Form...` | Music_Effect_Button, RefreshBottomBtns, _campToggleB... | - |
| `UIHalloweenGiftRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/GiveGif...` | ToggleGroup/ToggleGroupSubTab/Toggle1, ToggleGroup/T... | - |
| `UISeasonNightFallsRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightF...` | Music_Effect_Button, OnClickBtnInfo, ToggleControlBo... | - |
| `UILikeActRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeRanking/UILikeRa...` | Root/ToggleGroup/ToggleGroupSubTab/Toggle1, Root/Tog... | - |
| `UIWorldBossRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossRankView.prefab` | BtnGM, Music_Effect_Button, OnBtnGMClick, ToggleCont... | MsgDefines.UserGetActBossRank |
| `UIWorldBossRankS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/WorldB...` | BtnGM, Music_Effect_Button, OnBtnGMClick, ToggleCont... | MsgDefines.UserGetActBossRank |
| `UIFormationOfBattlefieldTeam` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UI...` | BtnClick_Cancel, CheckTeamBtn, ToggleControlBorS, bt... | - |
| `UIPuzzleMonsterRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPuzzleMonster/UIPuzzleMonst...` | ToggleControlBorS, UIButton, UIToggle, close_btn, cl... | - |
| `UIVolcanoRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoRank/UIVolca...` | SubToggleControlBorS, Toggle, ToggleControlBorS, per... | - |
| `UIAircraftRankingMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftRankingM...` | BtnLock, InitToggleData, Root/ToggleGroupTop/Toggle,... | - |
| `UIChristmasRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonat...` | ToggleControlBorS, UIButton, UIFoodFestivalPopUpTitl... | - |
| `UIChristmasRankRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonat...` | ToggleControlBorS, UIButton, UIFoodFestivalPopUpTitl... | - |
| `UISeasonGhostKingRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossRankView.prefab` | BtnGM, Music_Effect_Button, ToggleControlBorS, UIBut... | - |
| `UIThanksGivingRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/UIFoodFestivalR...` | ToggleControlBorS, UIButton, UIFoodFestivalPopUpTitl... | - |
| `UIPVEResult` | `UIContainer/Backg...` | `Assets/Main/Prefabs/Guide2/UIGuidePioneerResult.prefab` | UIButton, WorldTileBtnType, btn, continueBtnText, fu... | - |
| `UIThanksgivingStarRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingS...` | BtnName, BtnTab1, BtnType, ToggleControlBorS, UIToggle | MsgDefines.ThanksGivingStarRankInfo |
| `UIArena3V3Result` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Resu...` | UIButton, WorldTileBtnType, btn, rightBtnRoot, right... | MsgDefines.GetCrossArenaInfo |
| `UISeasonRankList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/UISeasonRa...` | Music_Effect_Button, UIButton, closeAll_btn, close_b... | - |
| `UIGotoAllowTracking` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UIGotoAllowTracking...` | OnBtnClick, UIButton, close_btn, close_btn_path, got... | - |
| `UILikeRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeRank.prefab` | Music_Effect_Button, Panel/UICommonPopUpTitle/CloseB... | - |
| `UIOverlordRankPreviewPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordRankPrevie...` | Music_Effect_Button, OnButtonCloseClicked, Root/Bott... | - |
| `UISeasonRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/SeasonRank...` | Music_Effect_Button, UIButton, UICommonPopUpTitle/bg... | - |
| `CastleAdventureMapRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleA...` | Music_Effect_Button, UIButton, closeBtn, costBtn_pat... | - |
| `UIArena3V3Challenge` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Chal...` | refreshBtnCostN, refreshBtnCostNum, refreshBtnTxtN | MsgDefines.BuyCrossArenaTicket, MsgDefines.Refr... |
| `UIArenaChallenge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArena/UIArenaChallenge.prefab` | refreshBtnCostN, refreshBtnCostNum, refreshBtnTxtN | MsgDefines.BuyCrossArenaTicket, MsgDefines.Refr... |
| `UIArenaPlayerArmy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena/UIArenaPlayerArmy...` | UIButton, close_btn, close_btn_path, return_btn, ret... | - |
| `UIGivingRoses2FlowerRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses...` | ToggleControlBorS, toggle, toggle1, toggle2, toggleList | - |
| `UIGivingRosesRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesR...` | ToggleControlBorS, toggle, toggle1, toggle2, toggleList | - |
| `UIHotNewsPointDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHotNews/UIHotNewRank.prefab` | Music_Effect_Button, btn, iconBtn, toggleCount, togg... | - |
| `UISeasonTradePostRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeas...` | ToggleControlBorS, UIButton, UICommonPopUpTitle/bg_m... | - |
| `UISeasonTradePostRankViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradeP...` | ToggleControlBorS, UIButton, UICommonPopUpTitle/bg_m... | - |
| `UIStrongCommanderRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/StrongCommande...` | ToggleControlBorS, dayToggleGroupN, dayToggleList, t... | - |
| `UIGolloesCardsRank` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/ActivityCenter/GolloesCards/U...` | UIButton, UICommonPopUpTitle/CloseBtn, _close_btn, _... | - |
| `UISeasonIceCaveUserOccupyRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | - |
| `UISeasonTradeMasterRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeas...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | - |
| `UISeasonTradeMasterRankViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradeP...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | - |
| `UIValentineSendGiftCardPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFo...` | ClaimBtn, RefreshClaimBtn, claimBtn, claimBtnText | - |
| `ChristmasParkourRankReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParko...` | ToggleType, toggleData, toggles | - |
| `UIActMonsterTowerRank` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/U...` | UIButton, UICommonMidPopUpTitle/CloseBtn, _close_btn | - |
| `UIArena3V3History` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Hist...` | buttonInfo | MsgDefines.BuyCrossArenaTicket, MsgDefines.GetC... |
| `UIArenaHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArena/UIArenaHistory.prefab` | buttonInfo | MsgDefines.BuyCrossArenaTicket, MsgDefines.GetC... |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `overlord_rank` | TableName.OverlordRank | 251 | id, overlord, stage, node, rank, icon, item, skill_unlock_lv, skill_unlock_star, spine |
| `overlord_military_rank` | TableName.OverlordMilitaryRank | 201 | id, overlord, rank, stage, name, self_effect, all_effect, nextId, item, icon |
| `aps_heroes_rank` | TableName.HeroMilitaryRank | 52 | id, level, stage, cost_medal, stage_show, name, icon, cost_coin, skill, require |
| `c_heroes_rank` | TableName.SU_HeroesRank | 46 | id, rank_atk, rank_def, rank_hp |
| `xiaoren_rank` | TableName.XiaoRenRank | 26 | id, level, stage, cost_common, cost_self |
| `herobattle_skill` | TableName.HeroBattle_Skill | 21 | id, week, time, duration, hero, skill, hero_pic, tips |
| `aps_heroes_rankLv` | TableName.HeroMilitaryRankLv | 8 | id, level, skillLv, name, icon, atk, def, troop |

**Enums:** `RankType` (24), `KingdomCdReason` (8), `StrongKingdomStateType` (7), `FakePVPStage` (5), `GhostKingBornType` (5), `RankItemBg` (5), `StrongKingdomWorldPlayerCityMark` (5), `BackingPowerType` (4), `CarRankType` (4), `PayActivityRankRemindSettingKeys` (4), `EWorldBossRankTabIndex` (3), `GotoArenaAimToType` (3), `KingdomPositionConditionType` (3), `RankingRangeType` (3), `DestroyRankType` (2), `GhostKingMonsterType` (2), `GhostKingRankTabIndex` (2), `GloryScoreRankType` (2), `KingWinNumStarImage` (2), `PVPType` (2)
