# Domain Quick-Card: Army, Troops & Hospital (`army_troops_hospital`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain army_troops_hospital`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **0** bot fns / **1** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **16** packets |
| `DataCenter` Managers & Singletons | **6** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **26** windows / **1** active HUD buttons / **1** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **9** tables / **26** enums / **25** live events / **7** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

**Hub `action_id` Routes:** `get_troops_overview` (L4683)

## 2. `DataCenter` Managers & Outgoing Links (6)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.GolloesCampManager` | 62 | MsgDefines.ClaimGolloesRewardNew, MsgDefines.GolloesNewDataGet... | GarbageCollectStart, GetGolloesRewardState, GolloesD... | - | - |
| `DataCenter.ArmyTemplateManager` | 53 | - | - | - | TableName.ArmsTab |
| `DataCenter.LWTrainDataManager` | 28 | MsgDefines.GetTrainList, MsgDefines.TrainStatus | RefreshTrainListData, TrainStatusResponse | - | TableName.LW_Train_Property |
| `DataCenter.DeadArmyRecordManager` | 12 | MsgDefines.GetDeadArmyRecord | RefreshDeadArmyRecord, RefreshDeadArmyRecordRedDot | - | - |
| `DataCenter.CampEffectManager` | 10 | - | - | - | - |
| `DataCenter.SegmentedHealthBarManager` | 10 | - | ShowSegmentedHealthBarHead | - | - |

## 3. Key Wire Packets (16 total; top 16 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `army.add` | ArmyAdd | `p=2` PutUtfString, PutBool, PutInt | ArmyManager.ArmyAddMessageHandle | GuideWaitMessage |
| `get.dead.army.record` | GetDeadArmyRecord | `p=2`  | DeadArmyRecordManager.GetDeadArmyRecordHandle | - |
| `overlord.cure` | OverlordCureMessage | `p=4` PutLong, PutUtfString, PutInt | OverlordManager.HandleOverlordCureResponse | OverlordCureResponse |
| `overlord.train` | OverlordTrainMessage | `p=2` PutLong | OverlordManager.HandleOverlordData | OverlordTrainResponse |
| `push.army.change` | PushArmyChange | `p=2`  | ArmyManager.PushArmyChangeHandle | - |
| `push.golloes.data` | PushGolloesData | `p=1`  | GolloesCampManager.UpdateGolloesInfo | - |
| `push.golloes.data.new` | PushGolloesDataNew | `p=1`  | GolloesCampManager.UpdateGolloesInfoNew | - |
| `push.volcano.battle.camp.effect.change` | PushVolcanoBattleCampEffectChange | `p=1`  | VolcanoWarManager.UpdateVolcanoEffect | - |
| `push.volcano.battle.camp.score.change` | PushVolcanoBattleCampScoreChange | `p=1`  | VolcanoWarManager.HandleCampScoreChange | - |
| `soldier.up` | SoldierUp | `p=2` PutUtfString, PutBool, PutInt | ArmyManager.SoldierUpMessageHandle | - |
| `train.attack` | AttackTrain | `p=10` PutLong, PutInt, PutSFSArray | LWBattleManager.Exit | TruckInfoUpdate |
| `train.info.now` | TrainInfoNow | `p=3` PutLong, PutInt | LWTrainDataManager.AddOrUpdateTrain | - |
| `train.list` | GetTrainList | `p=3` PutBool | LWTrainDataManager.OnTrainListGet | - |
| `train.status` | TrainStatus | `p=3` PutInt, PutLong | LWTrainDataManager.OnTrainStatusResponse | - |
| `push.cross.fill.army.times` | PushCrossFillArmyTimes | `p=1`  | - | - |
| `user.fill.cross.worm.army` | UserFillCrossWormArmy | `p=2` PutUtfString, PutInt, PutSFSArray | - | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (26 windows)

**Active HUD Buttons:** `Panel` [Troop 1 is back.] @ (50.0%,31.9%)

**`GoToUtil` Routers:** `GoToUtil.GoBarracks` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIGolloesTraderRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesCamp/UIGolloesTrader...` | Tab/Toggle1, Tab/Toggle2, UIButton, UICommonMidPopUp... | MsgDefines.GetGolloesCaravanRecord |
| `UIMilitaryForceLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMillitary/UIMilitaryForceLo...` | Music_Effect_Button, addBtn, reserveBtn, reserveDeta... | - |
| `UIHospitalGetMore` | `UIContainer/Normal` | `Assets/SlgEngine/Main/Prefabs/UI/UIHospital/UIHospit...` | Music_Effect_Button, WorldTileBtnType | - |
| `UIHospitalLack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalLack.prefab` | Music_Effect_Button, WorldTileBtnType | - |
| `UIReserveCamp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmyCamp.prefab` | reserve_btn, reserve_info_btn | - |
| `UITrainBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UITrainBuy.prefab` | - | MsgDefines.AllianceTrainBuy |
| `UITrainDriverInvite` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UITrainDriverInvi...` | - | MsgDefines.AllianceTrainAssign |
| `UIArmyInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmyInfo.prefab` | - | - |
| `UIArmySelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmySelect.prefab` | - | - |
| `UIArmyTipView3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips3.prefab` | - | - |
| `UIArmyTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips.prefab` | - | - |
| `UIArmyTips1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips1.prefab` | - | - |
| `UIArmyTips2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips2.prefab` | - | - |
| `UIArmyUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITrain/UIArmyUnlock.prefab` | - | - |
| `UICampBonus` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UICamp/UICampBonus.prefab` | - | - |
| `UIDeadArmyRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIDeadArmyRecord.prefab` | - | - |
| `UIHospitalDeath` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHostpitalDeath.prefab` | - | - |
| `UIHospitalDetial` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalDetial Var...` | - | - |
| `UIHospitalHelpTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalHelpTips.p...` | - | - |
| `UILWTrainDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainDetail.p...` | - | - |
| `UILWTrainList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainList.prefab` | - | - |
| `UILWTrainReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainReward.p...` | - | - |
| `UIMasterySoldier` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySoldier.pr...` | - | - |
| `UIReserveToSoldier` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmyCampConvert....` | - | - |
| `UISelectArmy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISelectArmy/UISelectArmy.prefab` | - | - |
| `UITrainBattleRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UITrainBattleReco...` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `army` | TableName.Army | 7,578 | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1 |
| `army_b` | TableName.Army_B | 6,858 | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1 |
| `army_c` | TableName.Army_C | 6,858 | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1 |
| `overlord_train` | TableName.OverlordTrain | 2,004 | id, overlord, type, level, additional_effect, additional_effect_num, is_critical, exp, add_e... |
| `lw_train_property` | TableName.LW_Train_Property | 480 | id, quality, HQLevel, Guard_max, length, speed, lowest_reward, train_route_length, reward1, ... |
| `lw_train_para` | TableName.LW_Train_Para | 39 | id, 说明, val |
| `camp_effect` | TableName.CampEffect | 4 | id, camp_type, camp_effect, icon, des |
| `camp_effect_b` | TableName.CampEffect_B | 4 | id, camp_type, camp_effect, icon, des |
| `overlord_cure` | TableName.OverlordCure | 3 | id, cure_point, cure_state, cure_state_icon, font_color, spine |

**Enums:** `ExtraInfoMsgType` (19), `SoldierLevelImage` (11), `SlgTroopCategory` (10), `QualityTrainBigBgPath` (7), `EnumDemonHunterCampStatus` (6), `QualityTrainBgPath` (6), `UITrainDetailType` (6), `UITrainDetailTypeIcon` (6), `CampEffectType` (5), `TroopType` (5), `UITrainDetailTypeList` (5), `CampImage` (4), `PVECamp` (4), `TrainKeyFrameType` (4), `TrainPlatformState` (4), `TrainTab` (4), `TroopIconShowState` (4), `EdenCamp` (3), `HospitalPanelStateType` (3), `SoldierType` (3), `TrainState` (3), `TrainType` (3), `UITrainState` (3), `ArmyDeadType` (2), `ArmyTrainType` (2)
