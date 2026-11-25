# Domain Quick-Card: Items, Bag, Shops, Speedups & VIP (`items_bag_shops_vip`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain items_bag_shops_vip`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **2** bot fns / **4** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **134** packets |
| `DataCenter` Managers & Singletons | **29** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **80** windows / **9** active HUD buttons / **12** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **22** tables / **94** enums / **76** live events / **37** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `_localize_id` | `L79-L86` | - | - |
| `_run_scoped_speedup` | `L2756-L2773` | - | - |

**Hub `action_id` Routes:** `get_presets` (L4687), `save_preset` (L4689), `delete_preset` (L4691), `open_all_resources` (L4722)

## 2. `DataCenter` Managers & Outgoing Links (29)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.PhonographManager` | 124 | MsgDefines.ClaimRecordReward, MsgDefines.ItemUse, MsgDefines.P... | OnReceivePhonographBuff, PaySuccess, PhonographFreeC... | UIPhonographBuffDetail, UIPhonographMain, UIPho... | TableName.Phonograph, TableName.StatusTab |
| `_G.CommonUtil` | 105 | MsgDefines.GoldGetUpdate, MsgDefines.UserAgreeTos | Disconnect | UIActivityRewardTip, UIDeleteAccountNoticeNew, ... | TableName.LandLock |
| `DataCenter.PayManager` | 98 | MsgDefines.ClaimFirstPayReward, MsgDefines.Pay, MsgDefines.Pay... | FirstPayStatusChange, OnPackageInfoUpdated, PlayGame... | PayPasswordInputPopup, UIFirstPay, UIThirdPayme... | - |
| `DataCenter.BattleCommandManager` | 68 | MsgDefines.DragonChangeCommander, MsgDefines.DragonGetCommandL... | DeleteOneDragonCommandSign, EnterDragonWorld, MiniMa... | - | - |
| `DataCenter.ItemData` | 43 | - | OnCheckNewDecorate, OnGoodsRedState, RefreshGirlTipI... | UIParkourBattleMain | - |
| `DataCenter.StorageShopManager` | 41 | MsgDefines.ShareCdCheck, MsgDefines.StorageShopBuyGoods, MsgDe... | RefreshStorageShopHistory, StorageShopAddGoods, Stor... | - | - |
| `DataCenter.ItemTemplateManager` | 36 | - | - | - | TableName.AllianceGiftGroup, TableName.GoodsTab |
| `DataCenter.ResourceItemDataManager` | 33 | MsgDefines.UseResItem, MsgDefines.UserGetAllResourceItem | OnGoodsRedState, RefreshResourceItem | UICapacityFull | TableName.Aps_Resource_Item |
| `DataCenter.ResLackManager` | 23 | - | - | - | TableName.Res_Lack_Tips |
| `DataCenter.TalentDataManager` | 23 | MsgDefines.ChooseBaseTalent, MsgDefines.RefreshBaseTalent, Msg... | TalentDataChange, UpdateGold | - | TableName.PlayerLevel |
| `DataCenter.FormStatusManager` | 22 | MsgDefines.ItemUse | FormStatusUpdate | - | - |
| `DataCenter.CreditManager` | 21 | MsgDefines.PayCreditStat, MsgDefines.RefundDeductHistory | CreditUpdate, UpdateGold, UpdateRefundHistory | UICreditMainPanel, UIRefundDeductGold, UISolide... | - |
| `DataCenter.ChainPayManager` | 20 | MsgDefines.ChainPayGetInfo, MsgDefines.ChainPayReceiveReward, ... | ChainPayGetInfo, ChainPayReceiveReward, ChainPayRefr... | - | - |
| `DataCenter.GroceryStoreOrderDataManager` | 19 | MsgDefines.PurchaseOrderDelete, MsgDefines.PurchaseOrderFinish... | DelayRefreshResource, RefreshGroceryStoreOrder | - | - |
| `DataCenter.StatusManager` | 19 | - | MSG_ITME_STATUS_TIME_CHANGE | - | TableName.StatusTab |
| `DataCenter.CommonShopManager` | 18 | MsgDefines.GetCommonShopInfo, MsgDefines.GetCommonShopInfoMulti | CheckPubBubble, OnCommonShopRedChange, UpdateOneComm... | - | - |
| `DataCenter.RubyStoreManager` | 18 | MsgDefines.UIShopBuy | OnCommonShopRedChange, RubyStoreLicenseExpired, Ruby... | - | - |
| `DataCenter.CumulativeRechargeManager` | 17 | MsgDefines.GetRechargeInfo, MsgDefines.ReceiveRechargeReward | CumulativeReward, RefreshDailyCumulative | - | TableName.Recharge |
| `DataCenter.RescueDogManager` | 17 | MsgDefines.RescueDogSubmitItem | Barrel_RescueDogRemoveHero, RefreshRescueDog | - | - |
| `DataCenter.TradeCenterDataManager` | 15 | - | - | - | - |
| `DataCenter.VIPTemplateManager` | 15 | - | - | - | TableName.EffectNumDesc, TableName.VipTemp |
| `DataCenter.ItemManager` | 14 | - | RefreshItems, UpdateGold, UseItemSuccess | UIPhonographMain | - |
| `DataCenter.KeepPayManager` | 12 | MsgDefines.GetRechargeInfo, MsgDefines.ReceiveRechargeReward | KeepPayUpdate | - | - |
| `DataCenter.EffectGetItemDataManager` | 9 | - | HeroExpEffectChange | - | - |
| `DataCenter.ResourceManager` | 7 | - | - | - | - |
| `DataCenter.GoldTrackManager` | 6 | - | LevelSceneLoadDone | - | - |
| `DataCenter.ItemConfig` | 4 | - | - | - | - |
| `DataCenter.DecResourceEffectManager` | 3 | - | - | - | - |
| `DataCenter.ResourceTemplateManager` | 2 | - | - | - | TableName.Resource |

## 3. Key Wire Packets (134 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `auto.use.item.result` | ItemUsePush | `p=2`  | ItemManager.ItemUseHandle | - |
| `buy.in.discount.shop` | BuyInDiscountShop | `p=3` PutInt | LuckyShopManager.BuyItemHandler | - |
| `buy.trade.bank.item` | StorageShopBuyGoods | `p=2` PutLong, PutUtfString, PutInt | StorageShopManager.OnRecvBuyFail | - |
| `change.vip.show` | ChangeVIPShow | `p=2` PutInt | VIPManager.UpdateVipInfo | VipDataRefresh |
| `check.share.trade.bank` | ShareCdCheck | `p=2` PutInt | StorageShopManager.OnRecvShareCheckResult | - |
| `claim.record.reward` | ClaimRecordReward | `p=1`  | PhonographManager.HandleClaimRecordRewardResponse | - |
| `dragon.member.status.info` | DragonMemberStatusInfo | `p=2` PutInt | DragonSwapManager.OnMemberStatusInfoResponse | - |
| `dragon.swap.record.info` | DragonSwapRecordInfo | `p=2` PutInt | DragonSwapManager.OnSwapRecordInfoResponse | - |
| `dragon.swap.respond` | DragonSwapRespond | `p=4` PutUtfString, PutInt | DragonSwapManager.OnSwapRespondResponse | - |
| `firstpay.reward` | ClaimFirstPayReward | `p=1`  | PayManager.UpdateFirstPayStatus | PlayerChangeHeadRedPot |
| `get.continuous.package.info` | ChainPayGetInfo | `p=2` PutInt | ChainPayManager.HandleGetInfo | - |
| `get.discount.shop.buy.record` | GetDisCountShopBuyRecord | `p=2` PutInt | LuckyShopManager.RefreshShopRecordHandler | - |
| `get.discount.shop.info` | GetDiscountShopInfo | `p=2` PutInt | LuckyShopManager.GetShopInfoHandler | - |
| `get.grocery.order` | GetGroceryOrder | `p=1`  | GroceryStoreOrderDataManager.GetGroceryStoreOrderHandle | - |
| `get.migrate.item` | GetMigrateItem | `p=2` PutInt | MigrateDataManager.RefreshServerDetailData | - |
| `get.migrate.servers` | GetMigrateServers | `p=1`  | MigrateDataManager.OnRefreshServerList | - |
| `get.migrate.servers.detail` | GetMigrateServersDetail | `p=1`  | MigrateDataManager.OnRefreshServerListDetail | - |
| `get.new.user.info` | GetNewUserInfo | `p=2` PutUtfString | PlayerInfoDataManager.RefreshPlayerData | GetNewUserInfoSucc |
| `get.radio.buff.info` | PhonographRadioBuffInfo | `p=2` PutInt | PhonographManager.OnRadioBuffInfoResponse | - |
| `get.recharge.info` | GetRechargeInfo | `p=2` PutInt | CumulativeRechargeManager.UpdateRechargeStageInfo | - |
| `get.shop.info.multi` | GetCommonShopInfoMulti | `p=1` PutIntArray | CommonShopManager.UpdateShopInfoMulti | - |
| `item.buy` | UIShopBuy | `p=2` PutUtfString, PutInt | ItemManager.ItemBuyHandle | - |
| `item.buyAndUse` | ItemBuyAndUse | `p=2` PutUtfString, PutInt | ItemManager.ItemBuyAndUseHandle | - |
| `item.recycle` | RecycleItem | `p=3` PutUtfString, PutInt | RewardManager.AddOneReward | - |
| `item.use` | ItemUse | `p=2` PutUtfString, PutInt, PutLong | ItemManager.ItemUseHandle | CLICK_RESOURCE_ITEM |
| `kill.monster.stage.reward` | KillMonsterStageReward | `p=3` PutInt | BarterShopNoticeManager.HandleRewardInfo | - |
| `migrate.invite` | MigrateInvite | `p=2` PutUtfString | MigrateDataManager.RefreshMigrateInviteData | - |
| `migrate.invite.refuse` | MigrateInviteRefuse | `p=2` PutInt | MigrateDataManager.OnRefreshMyInviteData | - |
| `migrate.user.info` | GetMigrateUserInfo | `p=2` PutUtfString | MigrateDataManager.RefreshInviteUserInfoData | - |
| `pay` | Pay | `p=2` PutUtfString | PayManager.PayMessageHandle | - |
| `pay.amazon` | PayAmazon | `p=2` PutUtfString | PayManager.PayMessageHandle | - |
| `pay.before.check` | PayBeforeCheck | `p=11` PutUtfString, PutInt | PayManager.__EndBeforeCheck | - |
| `pay.ios` | PayIOS | `p=2` PutUtfString | PayManager.PayMessageHandle | - |
| `pay.ptGold` | PayPtGold | `p=2` PutUtfString, PutBool | PayManager.PayPtGoldMessageHandle | - |
| `pay.steam` | PaySteam | `p=2` PutUtfString | PayManager.PayMessageHandle | - |
| `pay.test` | PayTest | `p=2` PutUtfString | PayManager.PayMessageHandle | - |
| `pay.trigger.res.item` | PayTriggerResItem | `p=2` PutInt | BattleLevel.OnPayTriggerResItemHandler | - |
| `pay.tstore` | PayTstore | `p=2` PutUtfString | PayManager.PayTstoreMessageHandle | - |
| `pinball.machine.info` | PinballMachineInfo | `p=2` PutInt | HalloweenMarbleManager.OnPinballMachineInfoResponse | - |
| `pinball.machine.record` | PinballMachineRecord | `p=2` PutInt | HalloweenMarbleManager.OnPinballMachineRecordResponse | - |
| `player.market.info` | PlayerMarketInfo | `p=2` PutInt | PlayerMarketManager.HandleMyInfo | - |
| `player.market.record` | PlayerMarketRecord | `p=2` PutInt | PlayerMarketManager.HandleRecord | - |
| `player.market.sell` | PlayerMarketSell | `p=5` PutInt, PutUtfString | PlayerMarketManager.OnSellFailed | - |
| `purchase.order.delete` | PurchaseOrderDelete | `p=2` PutLong, PutInt | GroceryStoreOrderDataManager.DeleteOrderFinishHandle | - |
| `purchase.order.refresh` | PurchaseOrderRefresh | `p=2` PutInt | GroceryStoreOrderDataManager.GetGroceryStoreOrderHandle | RefreshResidentOrder |
| `push.continuous.package.state` | ChainPayUpdateState | `p=2`  | ChainPayManager.HandleUpdateState | - |
| `push.dragon.swap.update` | PushDragonSwapResult | `p=1`  | DragonSwapManager.OnPushSwapResult | - |
| `push.first.pay.reward` | FirstPayRewardStatePush | `p=1`  | PayManager.UpdateFirstPayStatus | - |
| `push.item.add` | PushItemAdd | `p=2`  | ItemData.UpdateOneItem | - |
| `push.item.del` | PushItemDel | `p=2`  | ItemManager.PushItemDelHandle | - |
| `push.item.update` | PushItemUpdate | `p=1`  | ItemManager.PushItemUpdateHandle | - |
| `push.migrate.new.apply` | PushMigrateNewApply | `p=1`  | MigrateDataManager.OnRefreshApplyData | - |
| `push.migrate.new.invite` | PushMIgrateNNewInvite | `p=1`  | MigrateDataManager.OnRefreshMyInviteData | - |
| `push.new.recharge` | PushNewRecharge | `p=2`  | CumulativeRechargeManager.PushNewRechargeHandle | - |
| `push.pay.credit.update` | PayCreditUpdate | `p=1`  | CreditManager.HandleInfoUpdate | - |
| `push.pick.garbage.reward` | PushPickGarbageReward | `p=1`  | RewardManager.ReturnRewardParamForMessage | ShowPickGarbageResource |
| `push.purchase.order.update` | PushPurchaseOrderUpdate | `p=1`  | GroceryStoreOrderDataManager.DoWhenUpdateHandle | - |
| `push.recharge.score` | PushRechargeScore | `p=2`  | CumulativeRechargeManager.PushRechargeScoreHandle | - |
| `push.refund.deduct` | PushRefundDeduct | `p=1`  | CreditManager.ShowDeductResource | - |
| `push.rescue.dog` | PushRescueDog | `p=1`  | RescueDogManager.PushRescueDogHandle | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (80 windows)

**Active HUD Buttons:** `UIPlayerHead` [] @ (39.6%,34.3%), `12` [62.7M] @ (34.2%,2.4%), `2` [274.7M] @ (28.1%,2.4%), `14` [843.2M] @ (15.4%,2.4%), `1` [270.9M] @ (21.7%,2.4%), `btnAllPack` [15:30:39] @ (93.9%,8.3%), `ItemBar_1` [16] @ (7.3%,5.7%), `VipBtn` [7] @ (1.6%,11.8%), `goldStoreIcon` [4,947] @ (96.3%,2.4%)

**`GoToUtil` Routers:** `GoToResLack.CheckGarbageCanPick` -> [], `GoToResLack.GoToItemResLack` -> [], `GoToResLack.GoToItemResLackList` -> ['UIResourceLackNew'], `GoToResLack.GotoPickupGarbage` -> [], `GoToResLack.GotoSpeedLackList` -> ['UIResourceLackNew2'], `GoToUtil.GetSourceByResourceItem` -> [], `GoToUtil.GoBagPackUseItem` -> [], `GoToUtil.GoGarbage` -> [], `GoToUtil.GoToStorageShop` -> ['UIStorageShopMain'], `GoToUtil.GoWeeklyPackageNew` -> [], `GoToUtil.GotoColdStorage` -> [], `GoToUtil.GotoPayTips` -> []

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UICommonBuyItem` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonBuyItem.prefab` | Music_Effect_Button, OnBtnClick, UIButton, btn, btnP... | - |
| `UICommonUseResItemTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonUseResItemTips...` | Music_Effect_Button, OnBtnClick, UIButton, add_btn, btn | MsgDefines.ItemUse |
| `UIResourceLackNew1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceLackNew1...` | CloseMoreBtn, GetMoreBtnParent, OnBuyBtnClick, OnSel... | MsgDefines.UseResItemMulti |
| `UIScienceInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceInfoPortra...` | add_speed_btn_text, btnGoActive, btn_go, immediately... | MsgDefines.QueueCcdMNew, MsgDefines.ScienceRese... |
| `UIResourceExchange` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIResource/UIResourceExchange...` | Music_Effect_Button, UIButton, add_btn, btn_2, btn_2... | - |
| `UITradeCenter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITradingCenter/UITradeCenter...` | Music_Effect_Button, ToggleControlBorS, UIButton, UI... | MsgDefines.TradingBuy, MsgDefines.TradingSell |
| `UICommonItemProbability` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonItemProbabilit...` | Music_Effect_Button, UIButton, UICommonMidPopUpTitle... | - |
| `UICommonItemProbabilityNew` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonItemProbabilit...` | Music_Effect_Button, UIButton, UICommonMidPopUpTitle... | - |
| `UIMasteryTree` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasteryTree.prefab` | BtnInfo, Music_Effect_Button, btnNum, leftBtnPicName... | - |
| `UIRewardParkourResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIParkourResult.prefab` | leftBtn, leftBtnText, rightBtn, rightBtnEffect, righ... | - |
| `UIResourceLackNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceLackNew....` | infoBtnN, toggleIndex, toggleList | MsgDefines.UseResItemMulti |
| `UISettingAccount2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UISettingAccountNew...` | Music_Effect_Button, bottomBtnLayout, managementBtn,... | - |
| `UIBagView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIBagView/UIBagView.prefab` | toggleIndexToType, toggleName, toggle_btn | - |
| `UIMigrateDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateDetail...` | info_btn, info_request_btn | MsgDefines.MigrateApply |
| `UIVipRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVipRewardTip.prefab` | UIButton, return_btn, return_btn_path | - |
| `ChristmasShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasExcha...` | isMaxBtn, maxBtnN | - |
| `ThanksGivingExchangeShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingTur...` | isMaxBtn, maxBtnN | - |
| `UIEasterExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIEaster/UIEasterExchangeSho...` | isMaxBtn, maxBtnN | - |
| `UIGivingRoses2ExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses...` | isMaxBtn, maxBtnN | - |
| `UIResourceReplenish` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceReplenis...` | SelectResourceLackToggleIndex | MsgDefines.UseResItemMulti |
| `UIStorageShopMain` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopMa...` | history_btn_name, toggleNList | - |
| `UIStorageShopRetrieveNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopRe...` | - | MsgDefines.StorageShopGolloesBuy, MsgDefines.St... |
| `UIValentineNewExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineNe...` | isMaxBtn, maxBtnN | - |
| `UiChrsitmasExchangeShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasExcha...` | isMaxBtn, maxBtnN | - |
| `UIBagPickUp` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/Survival/UIBag/UIBagPickUp.pr...` | - | MsgDefines.BagGridMoveAll |
| `UIBagPropStatis` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIBagStatis/UIBagPropStat...` | Music_Effect_Button | - |
| `UICommonResourceComfirmView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonResourceComfir...` | OnCloseBtnClick | - |
| `UIDrakeBossUseItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIItem/UIDrakeBossUseItem.prefab` | - | MsgDefines.ItemUse |
| `UIGive` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageTrade....` | btnStr | - |
| `UIItemPurchases` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIItem/UIItemPurchases.prefab` | - | MsgDefines.UIShopBuy |
| `UIMultiBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMultiBuy/UIMultiBuy.prefab` | maxBtn | - |
| `UIPopupPackage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPopupPackage/UIPopupPackage...` | ShowLeftRotateButton | - |
| `UIRefundDeductGold` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundDeductGold.p...` | - | MsgDefines.CheckedRefundDeduct |
| `UIRefundDeductItem` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundDeductItem.p...` | - | MsgDefines.CheckedRefundDeduct |
| `UIStorageShopList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopLi...` | - | MsgDefines.StorageShopGetShopList |
| `UIStorageShopRetrieve` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopRe...` | - | MsgDefines.StorageShopRemoveGoods |
| `UITriggerGiveItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UITriggerGiveIt...` | - | MsgDefines.SU_PveTriggerSubmitItem |
| `UIVip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVip.prefab` | info_btn | - |
| `ShowItemTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/SU_ShowItemTips.prefab` | - | - |
| `UIBagSplit` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UIBag/UIBagSplit.prefab` | - | - |
| `UIBagUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UIBag/UIBagUpgrade.p...` | - | - |
| `UIBaubleExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBauble/UIBaubleExchange.prefab` | - | - |
| `UIBlindBoxShopView` | `UIContainer/Normal` | `Assets/Main/Prefab_Dir/UI/UIBlindBoxPanel/UIBlindBox...` | - | - |
| `UIChainPay` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIChainPay/UIChainPay.prefab` | - | - |
| `UICommonCredit` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CreditSystem/UICommonCred...` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `aps_shop` | TableName.APS_shop | 3,056 | id, shop_id, goods, goods_num, currency, currency_num, server, order, cycle, cycle_times |
| `res_lack_tips` | TableName.Res_Lack_Tips | 1,509 | id, goods, tips, order, name, btn_name, base, pic, level, group |
| `lw_trigger_item` | TableName.LW_Trigger_Item | 1,414 | id, type, para, dead_effect, is_weapon, prefab_path, location, rotation, size, icon |
| `goods` | TableName.GoodsTab | 1,025 | id, name, name_value, icon, description, type, lv, lv_limit, para, color |
| `trade_post_shopitem` | TableName.TradePostShopItem | 141 | id, goods_id, goods_num, sell_quantity, price, is_for_owner, is_for_member, owner_discount, ... |
| `popup_package_ui` | TableName.PopupPackageUI | 122 | id, type, name, main_icon, tab_pic, bg_pic, bg_pic2, title_top_color, title_bottom_color, ou... |
| `recycle_items` | TableName.RecycleItems | 88 | id, server_id, activity_id, recycle_type, rewardgoods_id, num, activity_special_type |
| `desert_refresh` | TableName.DesertRefresh | 87 | id, city_id, em_desertid, desertid, num, desert_lv_range |
| `aps_resource_item` | TableName.Aps_Resource_Item | 78 | id, type, itemType, building, name, desc, order, price, price_diamond, trade_num |
| `night_lunarlight_sorceress` | TableName.NightLunarLightSorceress | 60 | id, true_level, favor_level, favor_stage, favor_desc, favor_value, stage_reward, show_reward... |
| `recharge` | TableName.Recharge | 54 | id, type, order, hot, name, icon, para1, tab_icon, para2, image2 |
| `c_item_source_tip` | TableName.SU_ItemSourceTip | 50 | id, levelId, buildId |
| `trade_post` | TableName.TradePost | 40 | id, season, world_season, level, group, model, banner, name, desc, icon |
| `aps_resources` | TableName.Resource | 26 | id, icon, name, description, order, out_building |
| `vip` | TableName.Vip | 20 | id, point, icon, reward1, reward2, reward2_new, display, gift_pic, freebie_banner, effect |
| `vip_temp` | TableName.VipTemp | 17 | id, point, icon, reward1, reward2, reward2_new, display, effect |
| `trade_title` | TableName.TradePostTitle | 9 | id, level, world_season, icon, name, desc |
| `volcano_res` | TableName.VolcanoRes | 9 | id, res_type, type, order, size, time_points, complete_points, name, desc, pic |
| `speedup_config` | TableName.SpeedUpConfig | 7 | id, speedup_goods, max, min |
| `dog_catwoman_stage` | TableName.RescueDog | 6 | id, item_id, chapter_name, chapter_desc, idle_spine, random_language, noviceboot, tips, bg, ... |
| `night_lunarnight_pack` | TableName.NightLunarLightPack | 6 | id, name, unlock_time, deck |
| `trade_post_open` | TableName.TradePostOpen | 4 | id, preview_opentime, activity_opentime, group, tradepost_opentime, tradepost_opentime_serve... |

**Enums:** `GOODS_TYPE` (79), `ResLackGoToType` (73), `ResourceType` (33), `SteamLanguageToPay` (29), `CommonShopType` (27), `ResourceTypeIconName` (19), `ResTypeToReward` (17), `ItemSpdMenu` (16), `ResLackType` (16), `ResourceTypeTxt` (16), `RewardToResType` (16), `ResourceTabName` (11), `DeclareState` (9), `PackTimeType` (8), `ResourceTabSelectImage` (8), `ResourceTabUnSelectImage` (8), `ItemColor` (7), `MigrateShowItem` (6), `ResourceItem` (6), `ResourceLackOpenWinType` (6), `TradePostFightState` (6), `UIResourceBagBtnType` (6), `BagTabSelectImage` (5), `BagTabUnSelectImage` (5), `GOODS_TYPE2` (5)
