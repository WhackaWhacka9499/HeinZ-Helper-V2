# Domain Quick-Card: Garage, Vehicles & Chips (`garage_vehicles`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain garage_vehicles`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **1** bot fns / **0** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **52** packets |
| `DataCenter` Managers & Singletons | **9** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **33** windows / **0** active HUD buttons / **7** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **16** tables / **16** enums / **10** live events / **65** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `run_garage_upgrades` | `L12846-L12959` | CarComponInstallAll, CarComponUpgradeAll, GarageRefit, GarageRefitN... | GarageComponManager, GarageRefitManager |

## 2. `DataCenter` Managers & Outgoing Links (9)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.GarageRefitManager` | 113 | - | CarTalentGradingTimeChange, GarageRefitTalentUnlock | - | TableName.CarTalent, TableName.GaragePart, Tabl... |
| `DataCenter.GarageComponManager` | 57 | MsgDefines.CarComponInstall, MsgDefines.CarComponInstallAll, M... | CarComponEquipChanged, CarComponPartsChanged | - | TableName.CarCompon |
| `DataCenter.MonthCardNewManager` | 38 | - | AutoHelpReachThreshold, ColloesCaravanRecord, OnPack... | - | - |
| `DataCenter.EquipmentDataManager` | 31 | MsgDefines.CarEquipExp, MsgDefines.EquipUpQuality, MsgDefines.... | EquipDataUpdate, EquipSuitDataUpdate | UIEquipmentAdvanceSuccess | - |
| `DataCenter.CarBattlePveManager` | 25 | MsgDefines.UserSkipPveTrigger | CarBattlePveSkipLevel | UIPositionShare | TableName.Barrel_PVE |
| `DataCenter.HeroMonthCardManager` | 18 | MsgDefines.GetHeroMonthCardInfo, MsgDefines.GetHeroMonthCardRe... | RefreshHeroMonthCard, RefreshHeroMonthCardAll, Refre... | - | - |
| `DataCenter.CarChipTemplateManager` | 17 | - | - | - | TableName.CarMicrochip, TableName.CarMicrochipA... |
| `DataCenter.WeekCardManager` | 17 | MsgDefines.GetWeekCardList, MsgDefines.SetWeekCardCustomRewards | OnWeekCardCustomRewardUpdate, OnWeekCardInfoChange, ... | - | - |
| `DataCenter.MonthMsgCardManager` | 15 | MsgDefines.GetMonthDetectCard, MsgDefines.GetWeekDiscountCard,... | RefreshActivityRedDot | - | - |

## 3. Key Wire Packets (52 total; top 52 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `car.compon.install` | CarComponInstall | `p=2` PutLong, PutBool | GarageComponManager.UpdatePower | CarComponDataChanged |
| `car.compon.install.all` | CarComponInstallAll | `p=1`  | GarageComponManager.UpdatePower | CarComponDataChanged |
| `car.compon.levelup` | CarComponLevelUp | `p=3` PutLong, PutSFSArray | GarageComponManager.UpdatePower | CarComponDataChanged |
| `car.compon.upgrade` | CarComponUpgrade | `p=2` PutLong | GarageComponManager.UpdatePower | CarComponDataChanged |
| `car.compon.upgrade.all` | CarComponUpgradeAll | `p=2` PutInt | GarageComponManager.UpdatePower | CarComponDataChanged |
| `car.equip.exp` | CarEquipExp | `p=4` PutUtfString, PutInt, PutLong | EquipmentDataManager.EquipmentAddExpHandler | - |
| `choose.hero.month.card.reward` | ChooseHeroMonthCardReward | `p=2` PutInt | HeroMonthCardManager.SetRewardGroup | RefreshHeroMonthCardAll |
| `get.car.compon.info` | GetCarComponInfo | `p=1`  | GarageComponManager.UpdateParts | CarComponDataChanged |
| `get.golloes.caravan.record` | GetGolloesCaravanRecord | `p=1`  | MonthCardNewManager.InitCaravanRecord | - |
| `get.hero.month.card.info` | GetHeroMonthCardInfo | `p=1`  | HeroMonthCardManager.DoWhenAllDataBack | - |
| `lottery.hero.card` | LotteryHeroCard | `p=6` PutUtfString, PutInt | LotteryDataManager.UpdateOneLottery | HeroicRecruitmentData |
| `lottery.hero.card.switch` | LotteryHeroSwitch | `p=3` PutUtfString | LotteryDataManager.SetCampChangeInfo | RecruitCampChange |
| `lottery.hero.career.buy` | SmallPeopleRecruit | `p=4` PutUtfString, PutInt | SmallPeopleRecruitDataManager.UpdateDatas | SmallPeopleRecruitFail |
| `lottery.hero.career.info` | SmallPeopleRecruitInfo | `p=2` PutUtfString | SmallPeopleRecruitDataManager.InitData | SmallPeopleRecruitInfoFail |
| `lottery.hero.career.refresh` | SmallPeopleRecruitRefresh | `p=3` PutUtfString, PutInt | SmallPeopleRecruitDataManager.UpdateDatas | SmallPeopleRecruitRefreshFail |
| `lottery.hero.career.refresh.item` | SmallPeopleUseItemRefresh | `p=3` PutUtfString | SmallPeopleRecruitDataManager.UpdateDatas | SmallPeopleItemRefreshFail |
| `push.chip.box.num` | PushChipBoxNum | `p=1`  | CarChipManager.UpdateChipBoxNum | - |
| `push.golloes.carvan.start` | PushGolloesCarvanStart | `p=1`  | GolloesCampManager.HandelGolloesStartNotice | - |
| `push.hero.month.card.unlock` | BuyHeroMonthCardPush | `p=1`  | HeroMonthCardManager.SetRewardGroup | - |
| `push.month.card` | PushMonthCard | `p=1`  | MonthCardNewManager.UpdateMonthCardData | - |
| `push.new.car.equips` | NewCarEquipPush | `p=1`  | EquipmentDataManager.NewCarEquipPushHandler | - |
| `push.tank.chip.change` | PushCarChipChange | `p=1`  | CarChipManager.HandleChipDataChanged | - |
| `push.tank.chip.other.change` | PushTankChipOtherChange | `p=1`  | CarChipManager.ParseOtherCampInfoData | - |
| `push.tank.chip.unlock` | PushCarChipFunctionUnlockedMessage | `p=1`  | CarChipManager.FetchData | - |
| `push.update.user.tank` | GarageRefitUpdate | `p=1`  | GarageRefitManager.UpdateGarageRefit | GarageRefitUpdate |
| `push.update.user.tanknew` | GarageRefitUpdateNew | `p=1`  | GarageRefitManager.UpdateGarageRefitNew | GarageRefitNewUpdate |
| `push.user.car.compon.update` | PushUserCarComponUpdate | `p=1`  | GarageComponManager.ChangeParts | CarComponDataChanged |
| `query.golloes.my.caravan` | QueryGolloesRewardState | `p=2` PutLong | GolloesCampManager.SetSomeOneRewardState | - |
| `receive.all.hero.month.card.reward` | GetHeroMonthCardAllReward | `p=1`  | HeroMonthCardManager.DoWhenGetAllRewardBack | - |
| `receive.hero.month.card.reward` | GetHeroMonthCardReward | `p=2` PutLong | HeroMonthCardManager.DoWhenGetRewardBack | - |
| `take.off.car.equip` | TakeOffEquip | `p=4` PutInt, PutLong | EquipmentDataManager.TakeOffEquipHandler | - |
| `tank.chip.get.info` | CarChipGetInfoMessage | `p=1`  | CarChipManager.ParseData | - |
| `tank.chip.install` | CarChipInstall | `p=5` PutUtfString, PutInt | CarChipManager.HandleChipDataChanged | CarChipInstalled |
| `tank.chip.make` | CarChipMake | `p=3` PutUtfString, PutInt | CarChipManager.HandleChipDataChanged | CarChipMakeResponse |
| `tank.chip.reset` | CarChipReset | `p=2` PutLongArray | CarChipManager.HandleChipDataChanged | CarChipResetResponse |
| `tank.chip.uninstall` | CarChipUninstall | `p=3` PutUtfString | CarChipManager.HandleChipDataChanged | - |
| `tank.chip.upgrade` | CarChipUpgrade | `p=4` PutUtfString, PutLong, PutSFSArray | ItemData.UpdateOneItem | CarChipUpgradeResponse |
| `tank.discount.levelup` | TankDiscountLevelUp | `p=1`  | GarageRefitManager.CarTalentGradingDataManager | GarageGradingUpdate |
| `tank.new.addexp` | GarageRefitNewAddExp | `p=2` PutInt | ItemData.UpdateItems | GarageRefitNewUpdate |
| `tank.reform` | GarageRefit | `p=2` PutLong, PutInt | GarageRefitManager.UpdateGarageRefit | GarageRefitUpdate |
| `tank.talent.study` | GarageRefitTalentStudy | `p=2` PutInt | GarageRefitManager.UpdateTankTalent | CarTalentPreGradingChange |
| `user.finish.pve.trigger` | UserFinishPVETrigger | `p=2` PutInt, PutBool, PutLong | CarBattlePveManager.SetServerData | SU_ShowPVEReward |
| `user.skip.pve.trigger` | UserSkipPveTrigger | `p=2` PutInt | CarBattlePveManager.OnSkipTrigger | - |
| `wear.car.equip` | WearCarEquip | `p=4` PutInt, PutLong | EquipmentDataManager.WearCarEquipHandler | - |
| `career.up.level` | PlayerCareerLevelUp | `p=2` PutInt | - | PlayerCareerLevelUp |
| `choose.career` | PlayerCareerSelect | `p=2` PutInt | - | PlayerCareerSelect |
| `golloes.caraven.count.check` | GolloesTradeCheckTarget | `p=4` PutUtfString, PutInt | - | - |
| `golloes.caraven.count.check.new` | GolloesTradeCheckTargetNew | `p=3` PutUtfString, PutInt, PutSFSArray | - | - |
| `id.card.authenticate` | IDCardAuthenticate | `p=3` PutInt, PutUtfString | - | IDCardCheckFail |
| `push.career.free.change.time` | PushCareerFreeChangeTime | `p=2` PutInt | - | PlayerCareerFreeChangeUpdate |
| `tank.chip.info` | TankChipInfo | `p=1`  | - | - |
| `use.career.skill` | UseCareerSkill | `p=2` PutInt | - | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (33 windows)

**`GoToUtil` Routers:** `GoToResLack.GoToMonstCard` -> [], `GoToResLack.GotoCarChip` -> ['UIResourceLackNew'], `GoToResLack.GotoGarageCompon` -> ['UIResourceLackNew'], `GoToUtil.GoGarageUpgrade` -> [], `GoToUtil.GoToCareerSelect` -> [], `GoToUtil.GoToGarageRefit` -> ['UIAircraftMain'], `GoToUtil.GoToPlayerCareer` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UICarChipSelectCampPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipSelectCam...` | BtnGray, BtnGray/btnText, BtnSteup, BtnSteup/btnText... | - |
| `UICarChipBag` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipBag.prefab` | Music_Effect_Button, OnButtonCloseClicked, Root/Clos... | - |
| `UICarChipHandbookPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipHandbookP...` | OnButtonCloseClicked, OnToggleArmyTypeChanged, Root/... | - |
| `UICarChipBox` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipBoxPopup....` | Btns/Slider, Btns/TextDsc, Music_Effect_Button, UIBu... | MsgDefines.ItemUse |
| `UICarChipItemProbability` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAircraft/UICarchipItemProba...` | Root/panel_01/title/BtnInfo, Root/panel_01/title/Btn... | - |
| `UIGolloesCamp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesCamp/UIGolloesCamp.p...` | SetSendBtnState, YellowBtnShadowGrayColor, YellowBtn... | MsgDefines.ClaimGolloesDailyReward, MsgDefines.... |
| `UICarChipResetPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipResetPopu...` | BtnReset, BtnReset/btnText, OnButtonCloseClicked, On... | - |
| `UIAircraftMain` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftMain.prefab` | LeftToggleClick, ToggleFogVisible, ToggleMainCamera,... | - |
| `UICarChipGradingPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipGradingPo...` | Music_Effect_Button, OnButtonCloseClicked, UIButton,... | - |
| `UIAircraftPreviewSkillWindow` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraftPreviewSkillWindow/...` | FunctionBtnType, btnCanClickTime, checkBtnCanClick | MsgDefines.GarageRefitTalentStudy |
| `UICarChipGradingUpgradePopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipGradingUp...` | Music_Effect_Button, OnButtonCloseClicked, UIButton,... | - |
| `UICarChipStarLevelUpPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipStarLevel...` | OnButtonCloseClicked, UIButton, buttonClose | - |
| `UIAircraftMainPreview` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftPreview....` | skillBtn | - |
| `UICarChipUpgradePopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipUpgradePo...` | Music_Effect_Button | - |
| `UIIDCardAuthenticate` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAccount/UIIDCardAuthenticat...` | - | MsgDefines.IDCardAuthenticate |
| `UIAircraftComponInfo` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponIn...` | - | - |
| `UIAircraftComponMerge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponMe...` | - | - |
| `UIAircraftComponPartTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponPa...` | - | - |
| `UIAircraftComponPreviewPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponPr...` | - | - |
| `UIAircraftGradingTip` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftGradingT...` | - | - |
| `UIAircraftMainComponentTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftMain_Com...` | - | - |
| `UICarChipMainTips` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipMainTips....` | - | - |
| `UICarChipSelectCampVX` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftClipCamp...` | - | - |
| `UICarParkourSelect` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIParkour/UICarParkourSelect....` | - | - |
| `UICarParkourWarning` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UICarParkourWarning...` | - | - |
| `UIChampionBattleCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/Group_ex...` | - | - |
| `UIGolloesMonthCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesMonthCard/UIGolloesM...` | - | - |
| `UIHeroMonthCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroMonthCard/UIHeroMonthCa...` | - | - |
| `UIIDCardAgeTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAccount/UIIDCardAgeTips.prefab` | - | - |
| `UIIDCardDesTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAccount/UIIDCardDesTips.prefab` | - | - |
| `UIItemTips` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/SU_ItemTips.prefab` | - | - |
| `UIMedalGetCar` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIMedalGet/UIMedalGetCar.prefab` | - | - |
| `UIWeekendChallengeCarGetAche` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIMedalGet/UIMedalGetCar.prefab` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `car_microchip_attribute` | TableName.CarMicrochipAttribute | 1,968 | id, effects, microchip_id, rank, grade, power, id_next, skill, skill_level |
| `car_microchip_box` | TableName.CarMicrochipBox | 1,583 | id, goods_id, reward_id, num, odds |
| `car_talent` | TableName.CarTalent | 652 | id, level, max_level, type, cost, need_car_level, need_car_level_new, position, order, car_c... |
| `car_transform` | TableName.GaragePart | 600 | id, type, garage, max_level, level, effect, effect_num, name, icon |
| `car_modify_new` | TableName.GarageModify | 351 | id, level, garage, add_exp, exp, additional_effect, additional_effect_num, additional_effect... |
| `car_microchip_promote` | TableName.CarMicrochipPromote | 180 | id, quality, rank, grade, value_self, cost_goods, return_good, return_self, cost_self, cost_... |
| `car_compon` | TableName.CarCompon | 90 | id, icon, name, category, level, quality, combine_next, combine, combine_num, level_max |
| `hero_monthcard` | TableName.HeroMonthCard | 88 | id, name, description, sub_name, reward_pic, reward1_pic, reward2_pic, reward3_pic, reward4_... |
| `career_effect` | TableName.PlayerCareerEffect | 65 | id, type, name, description, icon, order, effect_value, show_type, cd_time, show |
| `night_lunarlight_card` | TableName.NightLunarLightCard | 58 | id, type, random_weight, reward, show_reward, color, order, number, name, desc |
| `player_career` | TableName.PlayerCareerXml, TableNam... | 50 | id, type, name, description, story, effect, require_item, require_lv, show_type, order |
| `car_microchip` | TableName.CarMicrochip | 48 | id, desc, name, quality, slot, army_type, icon, is_craft, craft_materials |
| `car_microchip_grading` | TableName.CarMicrochipGrading | 33 | id, name, star, type, color, effect, effect_num |
| `car_show_barrel` | TableName.Car_Show_Barrel | 30 | id, lock_enemy, drift_pos, drift_delay_time, stand_pos, stand_delay_time, stand_stay_time, s... |
| `car_talent_grading` | TableName.CarTalentGrading | 8 | id, name, desc, level, exp, car_level_tips, effect, effect_num, level_free, goods |
| `car_show` | TableName.CarShow | 5 | id, name, color, icon, icon_unlock, icon_army, cv_show, sound_idle, model, talent |

**Enums:** `CareerType` (6), `CarParts` (5), `CarQualityType` (5), `CarriageState` (5), `SmallPeopleCardItemState` (5), `CarColorBlue` (4), `CarColorGreen` (4), `CarColorOrange` (4), `CarColorPurple` (4), `CarColorWrite` (4), `CareerSkillState` (4), `HeroMonthCardRewardState` (4), `CareerSkillType` (2), `ComponentUpgradeType` (2), `GarageRefitTalentType` (2), `TankShowType` (2)
