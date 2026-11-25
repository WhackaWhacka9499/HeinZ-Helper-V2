# Domain Quick-Card: Formations, Marches & World Map (`formations_marches_world`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain formations_marches_world`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **1** tasks / **9** bot fns / **2** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **106** packets |
| `DataCenter` Managers & Singletons | **28** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **70** windows / **4** active HUD buttons / **18** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **14** tables / **102** enums / **64** live events / **109** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Task Key | Title | Tag |
|---|---|---|
| `war_safety` | War Safety Guard | `Shield + Recall` |

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `_used_formations_lua` | `L725-L729` | - | - |
| `_record_used_formations` | `L732-L739` | - | - |
| `snapshot_client` | `L1237-L1256` | - | StatusManager, WorldPointManager |
| `ensure_world_scene` | `L1281-L1304` | - | - |
| `run_auto_gather` | `L4457-L4615` | - | WorldPointManager |
| `run_trucks` | `L5554-L6027` | CollectTrainReward, GetMyStationData | ArmyFormationDataManager, ArmyManager, HeroDataManager, ItemData, L... |
| `snapshot_formations_and_gear` | `L6685-L6877` | - | ArmyFormationDataManager, ArmyFormationManager, HeroDataManager, He... |
| `restore_formations_and_gear` | `L6880-L6937` | HeroEquipInstall | HeroDataManager, HeroEquipManager |
| `_load_bot_mine_melee_module` | `L13088-L13104` | - | - |

**Hub `action_id` Routes:** `export_map` (L4872), `open_map_summary` (L4885)

## 2. `DataCenter` Managers & Outgoing Links (28)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `_G.GoToUtil` | 142 | MsgDefines.FindDesertPoint, MsgDefines.FindEnemyPoint, MsgDefi... | GOTO_SCIENCE, GoTroopListShow, MainToDailyAct, MainT... | MainUI_SU, UIActivityCenterTable, UIAircraftMain | TableName.Desert, TableName.TradePost |
| `DataCenter.LWMyStationDataManager` | 107 | MsgDefines.AttackTrain, MsgDefines.ChangeTrain, MsgDefines.Col... | ChangeTrainSuccess, EnemyTruckWeaponDataArrive, OnUp... | - | TableName.GoodsTab, TableName.LW_Train_Para |
| `DataCenter.ArmyFormationDataManager` | 94 | MsgDefines.GetMyStationData, MsgDefines.SaveFormationTempHero,... | FormationInfoUpdate, FormationSoldierUpdate, Receive... | - | - |
| `DataCenter.CarChipManager` | 86 | MsgDefines.CarChipGetInfoMessage, MsgDefines.CarChipInstall, M... | CarChipDataChanged, CarChipGroupSettingChanged, CarC... | UICarChipUpgradePopup | TableName.CarMicrochipBox, TableName.EffectNumDesc |
| `DataCenter.WorldShoutManager` | 76 | MsgDefines.GetBroadcastSticky, MsgDefines.SendBroadcastMsg, Ms... | TOP_BROADCAST_UPDATE, WORLD_SHOUT_HIDE_CARD, WORLD_S... | UIWorldShoutTips | - |
| `DataCenter.SimpleModeManager` | 71 | - | CombatModeChange, HideTroopHead, HideTroopName, OnEn... | - | - |
| `SlgDataCenter.DefendFormationManager` | 71 | MsgDefines.GetDefenseHero | DefendFormationNewDefendingUpdate, DefendFormationNe... | - | - |
| `DataCenter.WorldMissileManager` | 53 | MsgDefines.WorldMissileInfo | WorldMissileInfoRefresh | UIDeclareWarCountDownTitle | TableName.StateSkill |
| `DataCenter.BaubleManager` | 47 | MsgDefines.MoveBauble, MsgDefines.PlaceBauble, MsgDefines.Upgr... | BAUBLE_UPGRADE_Refresh, InitAllBauble, RefreshBauble... | UIBaubleLevelUpPopup | TableName.Bauble |
| `_G.SceneManager` | 46 | MsgDefines.LeaveWorld | SU_ChangeScreen, SU_MainUIReInit, SceneChanged | MainUI_SU | - |
| `DataCenter.GirlBehaviorManager` | 35 | MsgDefines.SUCancelCollectGarbage, MsgDefines.SUConfirmGarbage... | AddCollectQueue, GarbageTriggerFinish, RemoveCollect... | UISpeed | TableName.PVETrigger |
| `DataCenter.BagGridDataManager` | 34 | MsgDefines.BagCommonModify, MsgDefines.BagGridSingleMove, MsgD... | Survival_EquipDurableChanged, Survival_EquipSlotChan... | - | TableName.C_Equips |
| `DataCenter.WorldNoticeManager` | 33 | MsgDefines.GetNoticeList, MsgDefines.ReadNotice, MsgDefines.Re... | ChangeShowTranslatedNotice, GetNoticeList, RefreshNo... | UIActivityNoticeTip | - |
| `DataCenter.WorldNewsDataManager` | 31 | MsgDefines.GetWorldNewInfo | AttackerInfoUpdate, OnEnterWorld, UpdateWorldZoneNew... | - | - |
| `DataCenter.CollectResourceManager` | 20 | - | - | - | - |
| `DataCenter.SV_MapItemInfoManager` | 15 | - | - | - | TableName.PVETrigger |
| `DataCenter.FakeCollectGarbageMarchManager` | 14 | - | OnEnterWorld | - | - |
| `DataCenter.FakeHelperMarchManager` | 14 | - | OnEnterWorld | - | - |
| `DataCenter.FakeRescueMarchManager` | 14 | - | OnEnterWorld | - | - |
| `DataCenter.MapRewardBoxManager` | 14 | - | - | - | TableName.PVETrigger |
| `_G.FormationUtil` | 13 | - | - | - | TableName.WorldCity |
| `DataCenter.BirthPointTemplateManager` | 12 | - | - | - | TableName.WorldCity |
| `DataCenter.GovernmentWorldBubbleManager` | 12 | - | CheckShowGovPos | - | - |
| `DataCenter.WorldMyMarchDataManager` | 12 | MsgDefines.WorldGetMarchInfos | - | - | - |
| `DataCenter.CollectRewardDataManager` | 7 | - | MonsterRewardCreate | - | - |
| `DataCenter.WorldMarchDataManager` | 7 | - | - | - | - |
| `DataCenter.PVETriggerGatherTemplateManager` | 4 | - | - | - | TableName.PVETriggerGather |
| `DataCenter.FormationAssistanceDataManager` | 3 | - | UpdateAssistanceLeader | - | - |

## 3. Key Wire Packets (106 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `assistance.team.retreat` | AssistanceTeamRetreat | `p=3` PutLong, PutInt | FormationAssistanceDataManager.UpdateAssistanceData | CancelAllianceTeam |
| `car.compon.red.point.push` | CarComponRedPointPush | `p=1`  | GarageComponManager.UpdateCanEquipRed | - |
| `change.assistance.team.leader` | ChangeAssistanceTeamLeader | `p=3` PutLong, PutUtfString, PutInt | FormationAssistanceDataManager.ChangeAssistanceLeader | - |
| `clean.trade.bank.item` | StorageShopRemoveGoods | `p=2` PutLong | StorageShopManager.OnRecvRemoveGoods | - |
| `collect.new.cross.desert.box` | GetCrossDesertBox | `p=3` PutInt | RewardManager.AddOneReward | - |
| `collect.trade.bank.item` | StorageShopClaimMoney | `p=2` PutLong | StorageShopManager.OnRecvClaimMoneyBack | - |
| `find.desert.point` | FindDesertPoint | `p=2` PutInt | WorldGotoManager.FindDesertPointHandle | GuideWaitMessage |
| `formation.name.save.fb` | FormationName | `p=3` PutLong, PutUtfString | ArmyFormationDataManager.InitArmyFormationListData | - |
| `formation.save.template` | FormationSave | `p=6` PutInt, PutSFSArray, PutLong | ArmyFormationDataManager.UpdateTemplateFormationListData | ArmyFormatUpdate |
| `gather.collect.reward` | GatherCollectReward | `p=2` PutSFSArray | RewardManager.ReturnRewardParamForMessage | OnClaimCollectRewardSucc |
| `gather.reward.packet` | GatherRewardPacket | `p=2` PutLong | RewardManager.ShowCommonReward | - |
| `get.black.land.ruin.record` | GetBlackLandRuinRecord | `p=2` PutLong | WorldPointDetailManager.UpdateBlackLandRuin | GetBlackLandRuinResponse |
| `get.broadcast.sticky` | GetBroadcastSticky | `p=2` PutUtfString | WorldShoutManager.OnBroadcastStickyResponse | - |
| `get.cross.server.info` | GetCrossServerInfo | `p=2` PutInt | AllWorldsManager.onServerList | OnGetServerDataRefresh |
| `get.defense.hero` | GetDefenseHero | `p=1`  | ArmyFormationDataManager.ReceiveGetDefenseHeroMessage | - |
| `get.dragon.boss.health` | GetDragonBossHealth | `p=2` PutInt, PutLong | WorldPointManager.GetPointInfoByUuid | GetDragonBossHpMax |
| `get.march.plunder.res` | GetMarchPlunderRes | `p=1`  | PrivilegeEffectManager.SetTodayMoneyRob | - |
| `get.notice.list` | GetNoticeList | `p=1`  | WorldNoticeManager.ParseNoticeList | - |
| `get.single.march.info` | GetSingleMarchInfo | `p=4` PutInt, PutLong | WorldMarchDataManager.OnGetSingleMarchInfoError | - |
| `get.world.attacker.info` | GetWorldAttackerInfo | `p=2` PutInt | WorldNewsDataManager.UpdateAttackerInfoPointMsg | AttackInfoForMinimap |
| `get.world.news.info` | GetWorldNewInfo | `p=1` PutInt | WorldNewsDataManager.UpdateWorldNewsData | - |
| `hero.poster.exchange` | HeroPosterExchange | `p=2` PutSFSArray | HeroDataManager.RemoveHeroes | PosterExchangeSuccess |
| `hotNews.land.info` | HotNewsLandInfo | `p=3` PutLong, PutInt | WorldHotNewsManager.HandleHotNewsInfo | - |
| `move.bauble` | MoveBauble | `p=2` PutLong, PutInt | BaubleManager.MoveBaubleHandle | - |
| `push.all.broadcast` | PushAllBroadcast | `p=1`  | WorldShoutManager.OnNetPush | - |
| `push.area.hot.news.add` | PushAreaHotNewAdd | `p=1`  | WorldNewsDataManager.PushAreaHotNewAddHandle | - |
| `push.army.return` | PushArmyReturn | `p=1`  | ArmyFormationDataManager.InitArmyFormationListData | ArmyFormatUpdate |
| `push.assistance.team.leader.change` | PushAssistanceTeamLeaderChange | `p=1`  | FormationAssistanceDataManager.ChangeAssistanceLeader | - |
| `push.battle.finish` | PushBattleFinish | `p=1`  | WorldMarchBattleManager.BattleFinish | - |
| `push.battle.finish.batch` | PushBattleFinishBatch | `p=1`  | WorldMarchBattleManager.BattleFinishBatch | - |
| `push.battle.round.batch` | PushBattleRoundBatch | `p=1`  | WorldMarchBattleManager.WorldMarchBattleUpdateBatch | - |
| `push.battle.round.group` | PushBattleRoundGroup | `p=1`  | WorldMarchBattleManager.WorldMarchBattleUpdateGroupBatch | - |
| `push.battle.round.info` | PushBattleRoundInfo | `p=1`  | WorldMarchBattleManager.WorldMarchBattleUpdateBytesHandle | - |
| `push.black.ruin.durability` | PushBlackRuinDurability | `p=1`  | WorldPointDetailManager.UpdateBlackLandRuinDurability | PushBlackLandDurability |
| `push.black.ruin.result` | PushBlackRuinResult | `p=1`  | WorldPointDetailManager.UpdateBlackLandRuin | PushBlackLandRuinResult |
| `push.collect.extra.reward` | PushCollectExtraReward | `p=1`  | RewardManager.AddOneReward | - |
| `push.defend.formation.update.new` | PushDefendFormationUpdateNew | `p=1`  | ArmyFormationDataManager.InitArmyFormationListData | ArmyFormatUpdate |
| `push.delete.notice` | PushDeleteNotice | `p=1`  | WorldNoticeManager.DeleteNoticeHandle | - |
| `push.desert.collect.time.update` | PushDesertCollectTimeUpdate | `p=1`  | DesertDataManager.SetLastCollectTime | GatherSeasonResTimeChange |
| `push.energy.move.change` | PushEnergyMoveChange | `p=1`  | MasteryManager.PushEnergyMoveChange | - |
| `push.formation.status.add` | PushFormationStatusAdd | `p=1`  | FormStatusManager.HandleAdd | - |
| `push.formation.status.del` | PushFormationStatusDel | `p=1`  | FormStatusManager.HandleDel | - |
| `push.formation.update.new` | PushArmyFormationUpdate | `p=1`  | ArmyFormationDataManager.InitArmyFormationListData | ArmyFormatUpdate |
| `push.hero.delete` | PushHeroDelete | `p=1`  | HeroDataManager.RemoveOneHeroByUuid | - |
| `push.hot.news` | PushHotNews | `p=1`  | WorldHotNewsManager.HandlePushNotify | - |
| `push.march.continue.win` | PushMarchContinueWin | `p=1`  | ContinueWinDataManager.AddKillRecord | - |
| `push.new.notice` | PushNewNotice | `p=1`  | WorldNoticeManager.NewNoticeHandle | - |
| `push.receive.reward` | PushReceiveReward | `p=7`  | RewardManager.ShowCommonReward | - |
| `push.ser.world.mark.add` | PushSerWorldMarkAdd | `p=1`  | WorldFavoDataManager.SerWorldMarkToClientType | - |
| `push.ser.world.mark.del` | PushSerWorldMarkDel | `p=1`  | WorldFavoDataManager.SerWorldMarkToClientType | - |
| `push.ser.world.mark.update` | PushSerWorldMarkUpdate | `p=1`  | WorldFavoDataManager.OnUpdateCrossWonderMarkPush | - |
| `push.trebuchet.attack` | PushTrebuchetAttack | `p=2`  | WorldFortManager.AddToAtkList | - |
| `push.trends.red.num` | PushTrendsRedNum | `p=2`  | WorldTrendManager.SetWorldTrendRedNum | - |
| `push.user.collect.reward.create` | PushUserCollectRewardCreate | `p=1`  | CollectRewardDataManager.UpdateOneReward | RefreshMonsterRewardBag |
| `push.user.collect.reward.refresh` | PushUserCollectRewardRefresh | `p=1`  | CollectRewardDataManager.UpdateCollectRewardList | RefreshMonsterRewardBag |
| `push.user.collect.reward.remove` | PushUserCollectRewardRemove | `p=1`  | CollectRewardDataManager.RemoveOneReward | RefreshMonsterRewardBag |
| `push.user.lost.desert` | PushUserLostDesert | `p=1`  | DesertDataManager.RemoveMyDesert | UserLostDesert |
| `push.world.desert.first.occupy.update` | PushWorldDesertFirstOccupyUpdate | `p=1`  | DesertDataManager.UpdateDesertFirst | - |
| `push.world.desert.update` | PushWorldDesertUpdate | `p=1`  | WorldPointManager.HandleViewTileUpdateNotify | WorldGrid_UpdateBuild |
| `push.world.march.batch` | PushWorldMarchBatch | `p=1`  | WorldMarchDataManager.WorldMarchBatchUpdateHandle | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (70 windows)

**Active HUD Buttons:** `TroopCell_3` [] @ (115.5%,67.9%), `TroopCell_2` [2h8m] @ (115.5%,62.4%), `TroopCell_1` [1h34m] @ (115.5%,56.9%), `TroopCell` [] @ (115.5%,51.3%)

**`GoToUtil` Routers:** `GoToResLack.GotoMasteryPoint` -> ['UIResourceLackNew1'], `GoToUtil.DoCollectedGarbage` -> [], `GoToUtil.DoGoTile` -> [], `GoToUtil.GoAttackMonster` -> [], `GoToUtil.GoFormation` -> [], `GoToUtil.GoLockMonster` -> ['UIWorldPoint'], `GoToUtil.GoSelfDesert` -> ['UIWorldPoint'], `GoToUtil.GoUnlockedTile` -> [], `GoToUtil.GoWorldToSearch` -> [], `GoToUtil.GotoBossMonsterBetweenLv` -> [], `GoToUtil.GotoGuluBox` -> [], `GoToUtil.GotoMonsterReward` -> ['UISearch']

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIFormationTableNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationTableN...` | Music_Effect_Button, RefreshBottomBtns, Root/UICarCh... | - |
| `UISpearWorldPoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpear/UISpearWorldPoint.prefab` | AddBtnTimer, BtnAnim, BtnAnimTime, BtnCellCircle, Bu... | - |
| `UIPositionAdd` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIPositionAdd.prefab` | ClearToggleCallbacks, InitToggleCallbacks, OnClickDe... | MsgDefines.WorldFavoDel |
| `UIPositionFavorite` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionFavorite.prefab` | ToggleControlBorS, UIButton, UIToggle, close_btn, cl... | - |
| `UIBookMark` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BookMark/UIBookMark.prefab` | ToggleControlBorS, UIButton, UIToggle, close_btn, cl... | - |
| `UIWorldCollectMessageTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISearch/UIWorldCollectMessag...` | BtnGo/LeftBtn, BtnGo/LeftBtn/LeftBtnName, BtnGo/Righ... | - |
| `UICarChipDetailPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipDetailPop...` | LayoutBtn/BtnDelete, LayoutBtn/BtnRefresh, LayoutBtn... | - |
| `UIPositionShareConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionShareConfirm....` | ShouldShowNoMoreTipToggle, UIButton, back_toggle, bt... | MsgDefines.ChatPushNotice, MsgDefines.ThanksGiv... |
| `UIBaubleUpgradePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationColl...` | Music_Effect_Button, OnButtonCloseClicked, OnButtonI... | - |
| `UIBookMarkPositionCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BookMark/UIBookMarkPositionCo...` | Music_Effect_Button, UIButton, btn, btn_book_mark, b... | - |
| `UICarChipSelectChipPopup` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipSelectChi...` | Music_Effect_Button, OnButtonCloseClicked, ToggleGro... | - |
| `UIFormationShare` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationShareP...` | Music_Effect_Button, UIButton, atk_btn, camp_btn, cl... | - |
| `UIPositionTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionTips.prefab` | Music_Effect_Button, UIButton, btn, btn_favorite, bt... | - |
| `UISettingPointsReward` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISetting/UISettingPointsRewa...` | PGS_REWARD_CLAIM_BTN, UIButton, claimBtn, claimBtnTe... | - |
| `UIWorldBattleNews` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/WorldBattleNewsView.prefab` | ToggleControlBorS, UIButton, UIToggle, close_btn, cl... | - |
| `UIFormationAddStamina` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationAddSta...` | CloseMoreBtn, GetMoreBtnParent, Music_Effect_Speed_B... | MsgDefines.ItemUse |
| `UICarChipFormationPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipFormation...` | OnButtonModifyClicked, Tips/BtnClose, Tips/BtnGo, Ti... | - |
| `UIFormationSoldierChoose` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationSoldie...` | Music_Effect_Button, UIButton, one_key_btn, one_key_... | - |
| `UIWorldNewsTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBattleNewsTip.pr...` | Root/Button, Root/Button/btnTxt, Root/desText/btn_al... | - |
| `UILWTrainDeparture` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainDepartur...` | GF_click_departure_btn, GF_click_random_btn, OnChang... | - |
| `UIWorldBossTroop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossTroopView.pr...` | UIButton, close_btn, close_btn_path, return_btn, ret... | MsgDefines.UserGetActBossMarch |
| `UIPositionShare` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionShare.prefab` | UIButton, close_btn, copy_btn, return_btn | MsgDefines.ChatPushNotice |
| `UIMoreInformation` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMoreInformation/UIMoreI...` | GetTabBtnData, RefreshTabBtns, tabBtnData, tab_btns | - |
| `UIFormationState` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationStateN...` | UIButton, return_btn, return_btn_path | - |
| `UITowerRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UITowerRecord.prefab` | ToggleControlBorS_1, ToggleControlBorS_2, toggleList | - |
| `UIVolcanoSetAttack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoMap/UIVolc...` | Music_Effect_Button, mToggle1, mToggle2 | - |
| `UIWorldMarchDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIForcesDetail/UITroopDetail....` | RefreshToggle, toggleIndex, toggleTable | - |
| `UIWorldNewsAbbrDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldNewsAbbrDetail.p...` | UIButton, return_btn, return_btn_path | - |
| `UIWorldCupExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupExch...` | isMaxBtn, maxBtnN | - |
| `UIWorldDeclareList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldDeclareList.prefab` | UIButton, btnPanel | - |
| `UIBlackLandRuinRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIBlackLandRuinReco...` | - | MsgDefines.GetBlackLandRuinRecord |
| `UICheckServer` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIInterstellarMigration/UIInt...` | - | MsgDefines.GetMigrateItem |
| `UICollectReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICollectReward/UICollectRewa...` | - | MsgDefines.GatherCollectReward |
| `UICrossWonderCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonderCollect/UICrossW...` | - | MsgDefines.WorldGetDetail |
| `UICrossWonderMarkRemindNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMainNotice/UICrossWonderMar...` | Music_Effect_Button | - |
| `UIMainMiniMap` | `UIContainer/UIRes...` | `-` | - | MsgDefines.GetWorldAttackerInfo |
| `UIRuinRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIRuinRecord.prefab` | toggleList | - |
| `UIWorldCupPredictionConfirmPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopu...` | GetAddDecBtnState | - |
| `UIWorldCupUserMatchSharePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopu...` | PLayerInfoButtonType | - |
| `UIWorldDeclareWarInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldDeclareWarInfo.p...` | _tips_btn | - |
| `CastleAdventureMapReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleA...` | - | - |
| `UIDeclareWarCountDownTitle` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/UIGlory/UIDeclareWarCountDown...` | - | - |
| `UIDeclareWarList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIDeclareWarList.prefab` | - | - |
| `UIDisconnect` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Common/DisconnectView.prefab` | - | - |
| `UIFormationLackPower` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIFormationLackPower.pr...` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `birth_coordinate_0` | TableName.BirthPoint | 361 | id, X, Y, resource |
| `lw_path_point` | TableName.LW_PathPoint | 275 | id, point_type, para |
| `aps_singlemap_position` | TableName.SingleMapPosition | 223 | id, UnitType, Pos, Wave, UnitID |
| `world_scene` | TableName.WorldLod | 221 | id, type, path, lod, isMain, Fading |
| `hero_battle` | TableName.LOMap | 150 | id, name, chapter, trigger, camp, show_reward, show_first_reward, power, army_level, lock |
| `aps_gather_resource` | TableName.GatherResource | 121 | id, resource_type, param, level, reserve, size, expire, gathering, show_gathering, collect_p... |
| `c_trigger_gather` | TableName.PVETriggerGather | 105 | id, type, reward, step, name, soundtype, action, cd, expPerStep, tools |
| `pve_world` | TableName.SU_PveWorld | 60 | id, type, level, diffculty, recommend_power, pve_id, name, pic, model, desc |
| `aps_singlemap_pioneer` | TableName.APS_SINGLEMAP_PIONEER | 23 | id, NextID, UnclockFog, Noviceboot, Pos, UnclockType, UnclockPara, ShowPos, TagType, Tagpara |
| `formation_status` | SlgTableName.FormStatus, TableName.... | 6 | id, type, type2, time, group, priority, name, description, icon, effect |
| `push_map` | TableName.StoryMap | 6 | id, level, level_num, reward, name |
| `resources_collect` | TableName.ResourcesCollect | 5 | id, name, desc, icon, unlock_science, gathering, show_gathering, collect_power |
| `aps_collect_resource` | TableName.CollectResource | 3 | id, resourceType, para, diffPoint, model |
| `world_packet_reward` | TableName.WorldPacketReward | 2 | id, name, type, rewardId, box_reward, expire, pickTimes, model, panel_banner |

**Enums:** `WorldPointBtnType` (176), `WorldPointBtnTypeImage` (174), `WorldPointBtnName` (159), `SlgMarchTargetType` (156), `WorldPointBtnSortType` (153), `MarchTargetType` (113), `WorldTileBtnType` (110), `WorldTileBtnTypeImage` (106), `WorldTileBtnTypName` (93), `WorldPointUIType` (61), `SlgWorldPointType` (49), `SlgNewMarchType` (46), `NewMarchType` (37), `WorldPointType` (37), `SlgMarchStatus` (35), `MarchStatus` (30), `WorldExtraType` (22), `WorldMarchTileBtnType` (17), `UserSayCodeMap` (15), `FormationSetting` (14), `WorldMarchBtnTypeImage` (11), `WorldMarchBtnTypeName` (11), `FormationAddSoldierType` (10), `MarchPriorityState` (10), `SerWorldMarkIconName` (10)
