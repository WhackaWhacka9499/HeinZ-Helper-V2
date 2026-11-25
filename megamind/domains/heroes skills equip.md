# Domain Quick-Card: Heroes, Skills & Equipment (`heroes_skills_equip`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain heroes_skills_equip`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **1** task / **3** bot fns / **5** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **97** packets |
| `DataCenter` Managers & Singletons | **26** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **89** windows / **1** active HUD buttons / **10** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **42** tables / **67** enums / **42** live events / **30** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `run_free_recruits` | `L13008-L13108` | ItemUse, LotteryHeroCard | ItemData, ItemTemplateManager, LotteryDataManager, SmallPeopleRecru... |
| `inspect_hero_progression` | `L13345-L13823` | ActivityEventInfoGet *(probe fallback)* | ActPersonalArmsInfo, ActivityListDataManager, AllianceCompeteDataManager, ArmyFormationDataManager, HeroDataManager, HeroEquipManager, HeroEquipTemplateManager, HeroLevelUpTemplateManager, HeroSPEquipManager, ItemData, ItemTemplateManager (+ `_G.HeroUtils`) |
| `run_hero_progression` | `L13864-L14606` | HeroEquipInstall, HeroEquipPromoteUp, HeroEquipUpgrade, HeroLvBeyond, HeroLvUp, HeroRankUpgrade, HeroSPEquipBreak, HeroSPEquipUpgrade, HeroSkillUpgrade | HeroDataManager, HeroEquipManager, HeroSPEquipManager *(via `inspect_hero_progression`)* |

**Hub `action_id` Routes & Heroes JS-API:** `get_heroes_overview` (`L5908`), `save_hero_progression_rules` (`L6056`), `run_hero_progression_now` (`L6097`), `restart_daemon` (`L6513`), `start_bot_daemon` (`L7093`)

## 2. `DataCenter` Managers & Outgoing Links (26)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `_G.HeroUtils` | 214 | - | - | UIHeroInfo | TableName.BattleBuff, TableName.CampEffect_B, T... |
| `DataCenter.LandLockManager` | 116 | MsgDefines.FinishUserLand, MsgDefines.ReceiveLandReward, MsgDe... | LandLockInView, LandLockInit, LandLockOutView, LandL... | SU_NewHero, UIWorldTileUI | TableName.LandLock_B, TableName.PVETrigger |
| `DataCenter.HeroEquipManager` | 90 | MsgDefines.HeroEquipDecompose, MsgDefines.HeroEquipEvolution, MsgDefines.HeroEquipInstall, MsgDefines.HeroEquipPromoteUp, MsgDefines.HeroEquipReset, MsgDefines.HeroEquipUninstall, MsgDefines.HeroEquipUpgrade... | HeroEquipDecompose, HeroEquipInstall, HeroEquipPromotion, HeroEquipUpgrade... | UIHeroEquipEvolutionSuccess | - |
| `DataCenter.MasteryManager` | 81 | MsgDefines.ItemUse, MsgDefines.MasteryChangePlan, MsgDefines.M... | AddSpeedSuccess, MasteryChangePlan, MasteryExpUpdate... | UICapacityFull, UIMastery, UIMasteryExpTip | TableName.Mastery, TableName.SeasonObject |
| `DataCenter.HeroSmallPeopleDataManager` | 65 | MsgDefines.HeroStationSaveMessage | BuildStationChange | UIScreenCenterTips | TableName.SkillTab |
| `DataCenter.HeroStationManager` | 65 | MsgDefines.HeroStationSaveMessage, MsgDefines.HeroStationUseSk... | HeroStationSave, HeroStationUpdate, HeroStationUseSkill | - | - |
| `DataCenter.MistressLvTemplateManager` | 51 | - | RefreshUIBuildQueue | - | - |
| `DataCenter.HeroDataManager` | 50 | - | GetLastSeasonHeroRecordInfoSuccess | UIHeroBeyond, UIHeroMilitaryRank | TableName.HeroMilitaryRank |
| `DataCenter.HeroSPEquipManager` | 50 | MsgDefines.HeroSPEquipUpgrade | HeroSPEquipBreak, HeroSPEquipCheck, HeroSPEquipUpdate | - | TableName.HeroSPEquip, TableName.SkillTab |
| `DataCenter.HeroSkinManager` | 34 | MsgDefines.SurvivalHeroSkinSwitch, MsgDefines.SurvivalHeroSkin... | CloseUI, HeroSkinRed, HeroSkinRefresh | UIGetDress | TableName.EffectNumDesc |
| `DataCenter.HeroIntensifyManager` | 29 | MsgDefines.HeroIntensify, MsgDefines.HeroIntensifyOneKey | HeroIntensifyUpgrade | - | TableName.EffectNumDesc, TableName.HeroIntensify |
| `DataCenter.HeroEquipTemplateManager` | 28 | - | - | - | TableName.Equip |
| `DataCenter.SteelAndRedEquipManager` | 28 | - | SteelAndRedEquipDataRefresh, SteelAndRedEquipOneUpda... | - | - |
| `DataCenter.AssistanceHeroDataManager` | 23 | MsgDefines.GetHeroAssistanceInfo | InitAllAssistanceHero | UIPositionShare | - |
| `DataCenter.HeroOfficialManager` | 22 | - | SetHeroOfficial | - | - |
| `DataCenter.LWMyStationManager` | 22 | - | BUILD_IN_VIEW | - | - |
| `DataCenter.SU_MistressEffectManager` | 20 | MsgDefines.UseHeroEffectSkill | SU_RefreshMistressEffect | UICapacityFull | - |
| `DataCenter.HeroEffectSkillManager` | 18 | MsgDefines.UseHeroEffectSkill | RefreshHeroEffectSkill | UICapacityFull, UIHeroEffectSkillTips | - |
| `DataCenter.ThanksgivingStarInfo` | 11 | - | - | UIPositionShare | - |
| `DataCenter.HeroLevelUpTemplateManager` | 10 | - | - | - | TableName.NewHeroesLevelUp_B |
| `DataCenter.HeroTemplateManager` | 10 | - | - | - | TableName.LW_Hero |
| `DataCenter.FiveStarManager` | 9 | - | MainLvUp | UIFiveStarGet | - |
| `DataCenter.OfficialNavigationManager` | 9 | MsgDefines.GetOfficialNavigationInfo, MsgDefines.GetOfficialNa... | RefreshActivityRedDot, RefreshOfficialNavigation | - | - |
| `DataCenter.SteelAndRedEquipTemplateManager` | 9 | - | - | - | TableName.Trends, TableName.TrendsFunction |
| `DataCenter.HeroStationTemplateManager` | 7 | - | - | - | TableName.Hero_Station |
| `DataCenter.PveHeroTemplateManager` | 4 | - | - | - | TableName.PveHero, TableName.SU_HeroesLevelUp, ... |

## 3. Key Wire Packets (97 total; 62 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `army.info` | PushArmyInfo | `p=1`  | HeroDataManager.UpdateHeroes | PushArmyInfoEvent |
| `check.desert.talent.skill.buff` | MasteryCheckSkillBuff | `p=3` PutUtfString | MasteryManager.HandleCheckSkillBuff | - |
| `conver.skin` | CoverSkin | `p=3` PutInt | DecorationDataManager.CovertSkinHandler | - |
| `equip.up.quality` | EquipUpQuality | `p=2` PutLong | EquipmentDataManager.EquipmentQualityUpHandler | - |
| `get.hero.bounty.info` | GetHeroBountyInfo | `p=1`  | HeroBountyDataManager.UpdateAllData | - |
| `get.hero.lottery.info` | GetHeroLotteryInfo | `p=1`  | LotteryDataManager.UpdateLotteryData | HeroLotteryInfoUpdate |
| `get.hero.wake.skin` | GetHeroWakeSkin | `p=2` PutLong | HeroDataManager.UpdateOneHero | HeroAwakeSkinRefresh |
| `hero.assistance.share` | HeroAssistanceShare | `p=2` PutInt | AssistanceHeroDataManager.SetAssistanceHeroInfoTableShare... | - |
| `hero.decompose.piece` | HeroDecomposePiece | `p=2` PutInt, PutSFSArray | RewardManager.ShowCommonReward | - |
| `hero.equip.decompose` | HeroEquipDecompose | `p=2` PutSFSArray | HeroEquipManager.HeroEquipDecomposeHandler | - |
| `hero.equip.evolution` | HeroEquipEvolution | `p=2` PutLong | HeroEquipManager.HeroEquipEvolutionHandler | - |
| `hero.equip.install` | HeroEquipInstall | `p=3` PutInt, PutSFSArray | HeroEquipManager.HeroEquipInstallHandler | - |
| `hero.equip.promote.up` | HeroEquipPromoteUp | `p=4` PutLong, PutSFSArray, PutInt | HeroEquipManager.HeroEquipPromoteHandler | - |
| `hero.equip.reset` | HeroEquipReset | `p=2` PutLong | HeroEquipManager.HeroEquipResetHandler | - |
| `hero.equip.uninstall` | HeroEquipUninstall | `p=3` PutInt, PutSFSArray | HeroEquipManager.HeroEquipUninstallHandler | - |
| `hero.equip.unique.break` | HeroSPEquipBreak | `p=4` PutInt | HeroSPEquipManager.HeroEquipBreakHandler | - |
| `hero.equip.unique.unlock` | HeroSPEquipUnlock | `p=2` PutLong | HeroSPEquipManager.HeroEquipUnlockHandler | - |
| `hero.equip.unique.upgrade` | HeroSPEquipUpgrade | `p=4` PutInt | HeroSPEquipManager.HeroEquipUpgradeHandler | - |
| `hero.equip.upgrade` | HeroEquipUpgrade | `p=4` PutLong, PutSFSArray, PutUtfString, PutInt | HeroEquipManager.HeroEquipUpgradeHandler | - |
| `hero.exp` | HeroLvUp | `p=4` PutLong, PutUtfString, PutInt | HeroDataManager.UpdateOneHero | HeroLvUpSuccess |
| `hero.intensify` | HeroIntensify | `p=9` PutLong, PutInt | HeroIntensifyManager.isInHeroIntensifyReq | RefreshActivityRedDot |
| `hero.intensify.batch` | HeroIntensifyOneKey | `p=2` PutLong, PutInt, PutSFSArray | HeroIntensifyManager.isInHeroIntensifyReq | - |
| `hero.intensify.random.effect` | HeroIntensifyRandomEffect | `p=2` PutInt | HeroIntensifyManager.HandleIntensifyRandomEffect | - |
| `hero.qua.up` | HeroAdvance | `p=3` PutLong, PutLongArray | HeroStationManager.CheckStationEffectOldVal | CheckPubBubble |
| `hero.reset.lv` | HeroReset | `p=2` PutLong | HeroDataManager.UpdateOneHero | UpdateGold |
| `hero.star.up` | HeroStarUp | `p=2` PutLong, PutUtfString, PutInt | HeroDataManager.UpdateOneHero | HeroStarUpBack |
| `overlord.upgrade.skill` | OverlordUpgradeSkillMessage | `p=3` PutInt, PutLong | OverlordManager.HandleOverlordData | OverlordUpgradeSkillResponse |
| `player.market.otherOne` | PlayerMarketOtherOne | `p=3` PutInt, PutUtfString | PlayerMarketManager.OnOtherOneFailed | - |
| `push.batch.effect.change` | PushBatchEffectChange | `p=1`  | EffectGetItemDataManager.GetHeroExpEffect | HeroExpEffectChange |
| `push.effect.change` | PushEffectChange | `p=1`  | HeroEffectSkillManager.GetData | RefreshHeroEffectSkill |
| `push.equip.effect.change` | EquipEffectChangePush | `p=1`  | EquipmentDataManager.EquipEffectChangePushHandler | - |
| `push.hero.data` | PushHeroData | `p=1`  | HeroDataManager.GetHeroByUuid | CheckPubBubble |
| `push.hero.station.update` | HeroStationUpdateMessage | `p=1`  | HeroSmallPeopleDataManager.UpdateHeroStation | - |
| `push.init.other` | PushInitOther | `p=2`  | HeroDataManager.InitData | PUSH_INIT_OK |
| `push.refresh.hero.lottery` | PushHeroLottery | `p=1`  | LotteryDataManager.InitData | CheckPubBubble |
| `push.refresh.hero.switch` | PushHeroLotterySwitch | `p=1`  | LotteryDataManager.SetCampChangeInfo | RecruitCampChange |
| `push.skill.info.change` | PushSkillInfoChange | `p=1`  | MasteryManager.OnPushSkillInfoChange | - |
| `push.skin.update` | PushSkinUpdate | `p=1`  | DecorationDataManager.PushSkinUpdateHandler | - |
| `push.thanks.giving.star.levelup` | PushThanksGivingStarLevelup | `p=3` PutInt | ThanksgivingStarInfo.ParseMessage | PushThanksGivingStarLevelup |
| `push.train.data` | PushMyStationData | `p=1`  | LWMyStationDataManager.OnMyStationDataPush | - |
| `push.user.hero.equip.add` | PushUserHeroEquipAdd | `p=2` PutLong | HeroEquipManager.HeroEquipAddPushHandler | - |
| `push.user.hero.equip.unique.add` | PushHeroSPEquipAdd | `p=2` PutLong | HeroSPEquipManager.HeroEquipAddPushHandler | - |
| `recycle.skin.item` | RecycleSkinItem | `p=3` PutUtfString, PutInt | RewardManager.AddOneReward | UpdateGold |
| `survival.hero.skill.upgrade` | HeroSkillUpgrade | `p=3` PutLong, PutInt | HeroDataManager.UpdateOneHero | SkillUpgradeEnd |
| `save.hero.station` | HeroStationSaveMessage | `p=2` PutLong, PutInt, PutSFSArray | HeroSmallPeopleDataManager.UpdateHeroStation | - |
| `set.hero.official` | SetHeroOfficial | `p=3` PutInt, PutLong | HeroOfficialManager.SetHeroOfficialHandle | - |
| `start.explore.pve` | LevelExploreStart | `p=3` PutInt, PutUtfString, PutSFSArray | BattleLevel.OnStartLevelMessage | - |
| `start.product.hero.equip` | StartProductHeroEquip | `p=3` PutLong, PutInt | HeroEquipManager.HeroEquipStartProductHandler | - |
| `start.story.pve.level` | StartStoryPveLevel | `p=3` PutInt | StoryManager.HandleStart | - |
| `takeoff.skin` | TakeOffSkin | `p=2` PutInt, PutLong | DecorationDataManager.TakeOffSkinHandler | - |
| `thanks.giving.star.info` | ThanksGivingStarInfo | `p=2` PutInt | ThanksgivingStarInfo.ParseMessage | ThanksGivingStarInfo |
| `thanks.giving.star.level.reward` | ThanksGivingStarLevelReward | `p=3` PutInt | RewardManager.ShowCommonReward | - |
| `thanks.giving.star.visit` | ThanksGivingStarVisit | `p=3` PutInt, PutUtfString | RewardManager.ShowCommonReward | ThanksGivingStarVisit |
| `train.change` | ChangeTrain | `p=3` PutLong, PutInt | LWMyStationDataManager.OnTrainChanged | UpdateGold |
| `train.change.super` | TrainChangeSuper | `p=3` PutInt | LWMyStationDataManager.SuperRefreshStationData | - |
| `train.data` | GetMyStationData | `p=1`  | LWMyStationDataManager.OnMyStationDataGet | - |
| `train.send` | DepartureTrain | `p=9` PutLong, PutInt, PutSFSArray | LWMyStationDataManager.OnMyTrainDeparture | - |
| `train.supply.army` | ReinforceTrain | `p=1`  | LWMyStationDataManager.OnReinforceSend | - |
| `upgrade.hero` | HeroLvBeyond | `p=2` PutLong | HeroDataManager.UpdateOneHero | HeroLvUpSuccess |
| `upgrade.hero.rank` | HeroRankUpgrade | `p=3` PutLong, PutInt | HeroDataManager.UpdateOneHero | HeroRankUpFail |
| `upgrade.skin` | UpgradeSkin | `p=2` PutInt | DecorationDataManager.UpgradeSkinHandler | - |
| `use.desert.talent.skill` | MasteryUseSkill | `p=3` PutUtfString, PutLong, PutInt | MasteryManager.HandleUseSkill | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (89 windows)

**Active HUD Buttons:** `btnHero` [Hero] @ (2.9%,96.2%)

**`GoToUtil` Routers:** `GoToResLack.GoToHeroLvUp` -> [], `GoToResLack.GotoEquip` -> ['UIResourceLackNew'], `GoToResLack.GotoHeroEquip` -> ['UIResourceLackNew'], `GoToUtil.GoHeroSkill` -> ['UIHeroInfo'], `GoToUtil.GoHeroTrust` -> [], `GoToUtil.GotoHeroEquipForgeMain` -> ['UIHeroEquipForgeMain'], `GoToUtil.GotoHeroSpEquioView` -> ['UIHeroSPEquip'], `GoToUtil.GotoRedEquipForge` -> [], `GoToUtil.GotoSkinShopView` -> ['UISkinShop'], `GoToUtil.HeroStar` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIHeroEquipInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipI...` | Music_Effect_Button, OnDownBtnClick, OnPromotionBtnC... | - |
| `UIHeroInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroInfo.prefab` | CheckArrowBtns, GetBtnUpSizeDelta, OnBtnSkinClick, R... | - |
| `UIHeroBountyMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroOfferRewardF...` | UIButton, close_btn, close_btn_path, extra_desc_intr... | MsgDefines.GetHeroBountyInfo |
| `UIHeroBreak` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroBreakPop.prefab` | /BtnGo, /BtnGo/btnText, Music_Effect_Button, Root/Bi... | MsgDefines.HeroRankUpgrade |
| `UIAssistanceHeroShareConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAssistanceHero/UIAssistance...` | ShouldShowNoMoreTipToggle, UIButton, back_toggle, bt... | MsgDefines.ChatPushNotice, MsgDefines.ThanksGiv... |
| `UIHeroEquip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipV...` | BtnName, BtnType, Music_Effect_Button, OnClickGoldBt... | - |
| `UIHeroSkillUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillUpgrade...` | Music_Effect_Button, ShowBtnArrow, bigtogglebackimg,... | MsgDefines.HeroSkillUpgrade |
| `UIHeroLvUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroLvUp.prefab` | CloseMoreBtn, MoreBtnLocalPosX, MoreBtnPos, ShowMore... | MsgDefines.HeroLvUp |
| `UIFiveStarFeedBack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMain/UIFiveStarFeedBack.prefab` | Music_Effect_Button, UIButton, close_btn, close_btn_... | MsgDefines.FiveStar |
| `UIHeroEquipPromotion` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipP...` | Music_Effect_Button, OnPromotionBtnClick, UIButton, ... | - |
| `UIThanksgivingStarRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingS...` | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle | MsgDefines.ThanksGivingStarRankReward |
| `UIHeroInfoEquipInfoNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipP...` | promotionBtn, resetBtn, shareBtn, strengthBtn, toggle | - |
| `UIHeroIntensifyInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroHall/UIHeroPalaceLevelU...` | Music_Effect_Button, OnQualityBtnRightClick, WorldTi... | MsgDefines.HeroIntensify |
| `UIHeroRecruitReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruitRewar...` | OnToggleRecruitScene, ToggleRecruitScene, btnClose, ... | MsgDefines.LotteryHeroCard |
| `UISkinChoiceChest` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISkinBox/UISkinChoiceChestPo...` | RefreshBtnState, SetBtnClaimEnabled, btnClaim, btnPe... | MsgDefines.ItemUse |
| `UISkinChoiceChestHero` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISkinBox/UISkinChoiceChestHe...` | RefreshBtnState, SetBtnClaimEnabled, btnClaim, btnPe... | MsgDefines.ItemUse |
| `UISpeedAutoSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpeed/UISpeedAutoSelect.prefab` | second_tip_tipbutton | MsgDefines.ArmyAdd, MsgDefines.FreeBuildingUpNe... |
| `UIHeroMedalExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMedalExchang...` | Music_Effect_Button, OnShortCutBtnClick, toggle_rect | MsgDefines.HeroSPEquipItemExchange |
| `UIOverlordStarLevelUpPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordStarLevelU...` | Music_Effect_Button, OnButtonCloseClicked, UIButton,... | - |
| `HeroLevelExchangeConfirmPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroLevelExChang...` | SetBtnState, btnConfirm, btnGray | - |
| `UIHeroExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroResetShop/UIHeroExchang...` | OnClickCloseBtn, hero_btn | MsgDefines.BuyCommonShopGoods |
| `UIHeroSPEquipSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroinfoWeaponSu...` | Music_Effect_Button, btn, btnSkills | - |
| `UIMasterySkill` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySkill.prefab` | DesertOperateBtnState, GetBtnState, btnState | - |
| `UISmallPeopleSurvivorsList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleSu...` | SwitchBtnCanUse, btnSend, btnSendTxt | - |
| `UIGroceryStore` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIGroceryStore/UIGroceryStore...` | deliver_normal_get_more_btn, deliver_normal_item_inf... | - |
| `UIHeroCampRestraint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroCampRestrain...` | UIButton, return_btn | - |
| `UIHeroEquipStrength` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipN...` | toggle, togglelist | - |
| `UIHeroPosterExchangeMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroPosterExchan...` | btnInfo, toggleList | - |
| `UIHeroRecruitChangeCamp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruitChang...` | ToggleSelect | MsgDefines.LotteryHeroSwitch |
| `UIHeroRecruitTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruitTip.p...` | Music_Effect_Button, toggleList | - |
| `UIHeroSkillAdvance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillAdvance...` | btn | MsgDefines.HeroSkillUpgrade |
| `UIHeroTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIHeroTips.prefab` | btn, btnSkills | - |
| `UIHeroTips2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIHeroTips2.prefab` | btn, btnSkills | - |
| `UIItemHeroEquipBreakTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/SU_ItemHeroBreakTips.p...` | Music_Effect_Button, btnCamp | - |
| `UINewHero` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UINewHero.prefab` | ToggleRecruitScene, tabButtons | - |
| `UIOverlordSkillTipPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordSkillTipPo...` | UIButton, buttonClose | - |
| `SU_NewHero` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIHero/New/SU_NewHero.prefab` | ToggleRecruitScene | - |
| `UIHeroBeyond` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroBeyond.prefab` | - | MsgDefines.HeroLvBeyond |
| `UIHeroBreakSuccess` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroBreakTime.pr...` | ToggleRecruitScene | - |
| `UIHeroDetailTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIHeroDetailTips.prefab` | btnSkills | - |
| `UIHeroMilitaryAdvanceSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMilitaryAdva...` | btn | - |
| `UIHeroPosterExchangePop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroPosterExchan...` | - | MsgDefines.HeroPosterExchange |
| `UIHeroTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroTip.prefab` | goto_btn | - |
| `UIMasterySkillUse` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySkillUse.p...` | back_toggle | - |
| `UIShowFakeNewHero` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIShowFakeNewHero....` | Music_Effect_Button | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `hero_camp_intensify` | TableName.HeroIntensify | 10,521 | id, group, lv, season, max_lv, cost, power, effect, camp, effect_ext |
| `ds_equip_attribute` | TableName.EquipAttribute | 2,924 | id, effects, power, pve_hp |
| `skill` | TableName.SkillTab | 2,054 | id, skill_source_group, type, level, object, object_num, scale, effect, effect_num, name |
| `hero_camp_random` | TableName.HeroIntensifyRandomEffect | 1,212 | id, name, description, pic, effect_value, tips |
| `aps_new_heroes` | TableName.NewHeroes | 1,142 | id, state, season, season_show, season_server, camp, rarity, init_level, init_level_b, max_l... |
| `aps_new_heroes_client_B` | TableName.NewHeroesB | 974 | id, state, season, season_show, season_server, camp, rarity, init_level, init_level_b, max_l... |
| `lw_hero_skill` | TableName.LW_Skill, TableName.LW_He... | 968 | id, name, desc, maxLevel, star, group, power, pre_cd, attack_interval, priority |
| `heroes_exclusive_equip` | TableName.HeroSPEquip | 390 | id, group, level, name, effect, cost_item, cost_num, icon, image, special_effects |
| `heroes_levelup` | TableName.NewHeroesLevelUp | 200 | id, exp, lv_attr_atk1, lv_attr_atk2, lv_attr_atk3, lv_attr_atk4, lv_attr_def1, lv_attr_def2,... |
| `c_pve_heroes` | TableName.PveHero | 195 | id, atk_type, animations, prefab_low, moveSpeed_stage, move_range_stage, attack_range_stage,... |
| `lw_hero_skill_effect` | TableName.LW_Skill_Effect | 141 | id, fire_effect, fire_effect_time, fire_delay, fire_shake, cast_effect, cast_sound, shake_pr... |
| `lw_hero_appearance` | TableName.HeroAppearance | 129 | id, model_path, simple_model_path, model_size, hero_effect, fire_path, city_model_path, hero... |
| `c_heroes_levelup` | TableName.SU_HeroesLevelUp | 100 | id, legend_atk, epic_atk, rare_atk, normal_atk, lord_atk, legend_def, epic_def, rare_def, no... |
| `exclusive_equip_breakthrough` | TableName.HeroSPEquipBreak | 78 | id, group, level, name, effect, cost_item, cost_num, require_rank, max_level, unlock_skill |
| `aps_new_heros_skin` | TableName.Hero_Skin | 75 | id, hero_id, sorting, hero_spine, skin_icon, skin_name, default_skin, hero_icon, round_hero_... |
| `hero_bounty` | TableName.HeroBounty | 72 | id, name, description, rarity, function, time_h, hero_num, camp_requirements, exp_hero, exp |
| `lw_hero_effect` | TableName.LW_Hero_Effect | 67 | id, hit_effect_direction, death_effect_nomal, death_sound, hit_sound, death_effect_fire, dea... |
| `c_equips` | TableName.C_Equips | 63 | id, type, melee, model, range, attack, defense, duration, randomDuration, animation |
| `mistress_lv` | TableName.MistressLv | 60 | id, mistress_id, pre_event_id, love_lv, love_lv_name, love_value, mistress_view_id, tap_num,... |
| `hero_official` | TableName.HeroOfficial | 54 | id, camp, type, official_position, official_name, unlock_lv, effect, max_value, max_hero_pow... |
| `hero_lack_tips` | TableName.Hero_Lack_Tips | 42 | id, heroid, fragmentid, tips, order, name, btn_name, base, pic, para1 |
| `lw_hero` | TableName.LW_Hero | 41 | id, type, title_name, first_name, quality, template_id, base_hp, base_patk, base_pdef, base_acc |
| `aps_heroes_quality` | TableName.NewHeroesQuality | 39 | id, consume1, levelup_adv, reset_season, level, type, consume, name, name_UI, color |
| `aps_new_heros_skin_shop` | TableName.Hero_Skin_Shop | 34 | id, type, type_para, goods, price_type, price_type_para, show_type, show_service, time_type,... |
| `ds_equip_promote` | TableName.EquipPromote | 31 | id, level, rank, grade, level_up, cost_goods, cost_resource, reset_goods, cost_equips, retur... |
| `mistress` | TableName.Mistress | 30 | id, mistressNPC_id, room_mod, hold_animation, hold_cv, hold_text, head, head_animation, head... |
| `hero_tag` | TableName.NewHeroesTag | 26 | id, name, pic, desc |
| `ds_equip` | TableName.Equip | 18 | id, desc, name, quality, slot, army_type, icon, img, basic_attributes, break_exp |
| `hero_station` | TableName.HeroStation, TableName.He... | 16 | id, build_id, career, people_unit_limit, order |
| `ds_equip_upgrade` | TableName.EquipUpgrade | 12 | id, quality, slot, army_type, highest_level, stone_upgrade_cost |
| `c_pveSkill` | TableName.SU_PveSkill | 10 | id, skillAction, range |
| `officer_recruit` | TableName.HeroRecruit | 9 | id, type, quest_recruit_type, order, item, function, name, time, rate1, rate2 |
| `ds_equip_mythical` | TableName.EquipForgeMythical | 7 | id, level, level_limit, promote_limit, cost_goods, cost_resource, reset_goods |
| `hero_core` | TableName.HeroArkCore | 7 | id, core_type, condition, effect |
| `APS_hero_color` | TableName.HeroColor | 6 | id, star_limit_level_1, star_limit_level_2, star_limit_level_3, star_limit_level_4, star_lim... |

**Enums:** `HeroEffectDefine` (111), `MasterySkill` (17), `HeroSkillType` (10), `SkinType` (9), `HeroEquipConst` (8), `HeroLackTipsType` (8), `SkinPoolType` (7), `SteelAndRedEquipFunctionType` (7), `EquipSlotReq` (6), `HeroBountyRarity` (6), `HeroStationEffectType` (6), `MasterySkillState` (6), `RailwayStationState` (6), `SkillType` (6), `SurvivalEquipType` (6), `AlSkillStatus` (5), `CheckHeroCampAddEffectList` (5), `CheckHeroRestraintEffectList` (5), `HeroCamp` (5), `HeroIntensifyState` (5), `HeroIntensifyTabState` (5), `HeroSkillToHeroId` (5), `HeroStationState` (5), `HeroType` (5), `HeroXmlState` (5)
