# Domain Quick-Card: Chat, Moments & Mail (`chat_moments_mail`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain chat_moments_mail`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **1** bot fns / **0** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **136** packets |
| `DataCenter` Managers & Singletons | **21** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **154** windows / **7** active HUD buttons / **9** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **13** tables / **62** enums / **18** live events / **80** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `dismiss_all_popups` | `L1259-L1278` | - | - |

## 2. `DataCenter` Managers & Outgoing Links (21)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `DataCenter.MailShim` | 179 | - | MailDetailReady | UIBattleReportInfo, UICampBonusMailTip, UIMailB... | - |
| `DataCenter.MomentManager` | 128 | ChatMsgDefines.ModifyGiftShow, ChatMsgDefines.MomentComment, C... | MomentUpdateBubbleChanged, RefreshChatMomentList, Re... | UIGiftPackage, UIMomentDetail, UIMomentPost | - |
| `_G.GiftPackageData` | 119 | MsgDefines.ClaimFirstPayReward, MsgDefines.ExchangeInfo, MsgDe... | CustomChoiceItem, FreeWeeklyPackage, OnPackageInfoUp... | UIFirstPay, UIPiggyBank | - |
| `DataCenter.LWBattleManager` | 108 | MsgDefines.MailGetFightReportDetail, MsgDefines.StatTT, MsgDef... | Barrel_StartLevelResponse, BeforeReleaseCity, GF_pve... | LWPVPArenaMain, MainUI_SU, UIDetectEvent | TableName.PVELevelOld |
| `DataCenter.MailFacade` | 92 | MsgDefines.MailBatchDel | MailDetailReady, MailPush, Mail_DeleteBatchMailDone,... | - | - |
| `DataCenter.AccountManager` | 91 | MsgDefines.AccountLoginNewGlobal, MsgDefines.ChangeMail, MsgDe... | AccountBindEvent, AccountBindOKEvent, AccountChangeM... | UIAccountVerify, UIBindSendMail, UIGameCenterCh... | - |
| `DataCenter.FoodFestivalEatManager` | 71 | ChatMsgDefines.ChatRoom, MsgDefines.BanquetAddMealRecords, Msg... | FoodFestivalEatSendToChat, RefreshUIWorldPointView | UIFoodFestivalEatPreviewTipView, UIWorldPoint | TableName.ActivityPanel, TableName.FoodFestival... |
| `DataCenter.FishingCatalogDataManager` | 65 | ChatMsgDefines.GetUserInfoMulti, MsgDefines.SendFish, MsgDefin... | ChatPrivateRoomCreated, FishingCatalogAtlasRewardUpd... | UIFishingCatalogGiveGift, UIFishingCatalogGiveG... | TableName.IceCaveInfo |
| `DataCenter.PresentManager` | 49 | MsgDefines.GetGiftDetail, MsgDefines.GetGiftRewardInfo, MsgDef... | RefreshPresentHistory, RefreshPresentInfo, RefreshPr... | UIPresentBigShow, UIPresentSend, UIPresentSendTips | TableName.Present, TableName.PresentSP |
| `DataCenter.LoveNewsletterDataManager` | 43 | MsgDefines.SurvivalHeroMessage, MsgDefines.SurvivalHeroMessage... | HeroChatMessageOutTime, UpdateHeroBatteryPower, Upda... | UILoveNewsletterMM | TableName.LoveMessageHero |
| `DataCenter.CarnivalMomentManager` | 36 | MsgDefines.GetShowtimePackInfo, MsgDefines.ShowtimePackCheerin... | CarnivalCheerSuccess, CarnivalDanmakuPush, CarnivalD... | UICarnivalLuckySpin | - |
| `DataCenter.FriendManager` | 30 | MsgDefines.DeleteFriend, MsgDefines.FriendApply, MsgDefines.Fr... | DeleteFriend, FriendGroupChat, RefreshFriend, Refres... | - | - |
| `DataCenter.ActGiftBoxData` | 29 | - | ActGiftBoxDrawReward, ActGiftBoxGetInfo, ActGiftBoxL... | - | - |
| `DataCenter.HeroSkinShopManager` | 29 | MsgDefines.GiftVouchersRewardList, MsgDefines.RevGiftVouchersF... | SkinShopRefresh, SkinShopTicketRefresh | UIMultiBuy | TableName.Hero_Skin_Shop |
| `DataCenter.VipRoomAnnouncementManager` | 28 | ChatMsgDefines.RoomGroupDelNotice, ChatMsgDefines.RoomGroupLik... | ChatAllianceAnnouncementAdd, ChatAllianceAnnouncemen... | - | - |
| `DataCenter.MailShowTemplateManager` | 20 | - | - | - | TableName.MailShow |
| `DataCenter.MarchEmojiDataManager` | 20 | MsgDefines.SendMarchEmoji, MsgDefines.SetEmoji | MarchEmojiSettingUpdate, SendMarchEmojiTimeUpdate | - | TableName.ShelterEmoji |
| `DataCenter.BattlePresentationLodManager` | 18 | - | - | - | - |
| `DataCenter.MailGroupTemplateManager` | 7 | - | - | - | TableName.MailGroup |
| `DataCenter.LoveNewsletterTemplateManager` | 6 | - | - | - | TableName.LoveMessageHero |
| `_G.ChatManager2` | 5 | - | - | - | - |

## 3. Key Wire Packets (136 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `account.mail.bind.verify` | AccountVerify | `p=2` PutUtfString | AccountManager.ApplyServerPgsBind | - |
| `activity.get.spin.lottery.count` | - | `p=2` PutInt | SlgDC.SlgTreasureBoxTypeManager.GiftBoxLotteryCount | - |
| `activity.gift.box.lottery` | ActivityGiftBoxLottery | `p=4` PutInt | ActGiftBoxData.GiftBoxLotteryHandle | - |
| `activity.open.spin.box` | - | `p=3` PutInt, PutLong | SlgDC.SlgTreasureBoxTypeManager.OpenGiftBoxHandle | - |
| `activity.spin.give.up` | - | `p=3` PutInt, PutLong | SlgDC.SlgTreasureBoxTypeManager.GiveUpActivityGiftBox | - |
| `activity.spin.receive.stage.reward` | - | `p=3` PutInt | SlgDC.SlgTreasureBoxTypeManager.GetGiftBoxProgressReward | - |
| `add.like` | AddLike | `p=3` PutUtfString, PutInt | LikeManager.Like_Type | LikeRefresh |
| `az.account.changemail` | AccountChangeMail | `p=2` PutUtfString | AccountManager.AccountChangeMailHandle | - |
| `az.account.mailconfirmed` | PushAccountFirmed | `p=2`  | AccountManager.PushAccountFirmedHandle | - |
| `cancel.like` | CancelLike | `p=5` PutUtfString, PutInt | LikeManager.HandleCancelLike | - |
| `chat.get.new.mails.v4` | MailGetNewMailsV4 | `p=3` PutUtfString, PutLong | MailFacade.OnV4NewMailsResponse | - |
| `chat.get.system.mails` | MailGetMuti | `p=5` PutUtfString, PutLong, PutInt | MailFacade.IsUseNewSystem | - |
| `chat.get.system.mails.v3` | MailGetMutiV3 | `p=4` PutLong, PutInt, PutUtfString | MailFacade.IsUseNewSystem | - |
| `chat.get.system.mails.v3.tab` | MailGetMutiV3Tab | `p=5` PutInt, PutIntArray, PutLong | MailFacade.IsUseNewSystem | - |
| `chat.get.system.mails.v4` | MailGetMutiV4 | `p=4` PutLong, PutInt, PutUtfString | MailFacade.OnV4FirstScreenResponse | - |
| `chat.get.system.mails.v4.tab` | MailGetMutiV4Tab | `p=5` PutInt, PutIntArray, PutLong | MailFacade.OnV4MoreResponse | - |
| `clear.friend.alias` | ClearFriendAlias | `p=2` PutUtfString | FriendManager.ClearFriendAlias | - |
| `create.group.chat.check` | CreateGroupChatCheck | `p=2` PutSFSArray | FriendManager.OnOnlyFriendGroupChat | - |
| `delete.friend` | DeleteFriend | `p=2` PutUtfString | FriendManager.DeleteFriend | - |
| `dragon.history.like` | DragonHistoryLike | `p=5` PutUtfString, PutLong, PutInt | ActDragonManager.HandleAddLike | - |
| `eliteNew.main.viewreport` | ACT_CHAMPIONBATTLE_REPORT_DESC | `p=3` PutLong, PutUtfString | MailInfoShim.NewFromRawData | ChampionBattleReportDataBack |
| `friend.apply` | FriendApply | `p=2` PutUtfString | FriendManager.SendFriendApply | RefreshFriendApply |
| `friend.apply.agree` | FriendApplyAgree | `p=2` PutSFSArray | FriendManager.AgreeApply | - |
| `friend.apply.refuse` | FriendApplyRefuse | `p=2` PutSFSArray | FriendManager.RefuseApply | - |
| `get.activity.gift.box.info` | GetActivityGiftBoxInfo | `p=2` PutInt | ActGiftBoxData.ParseActivityData | - |
| `get.activity.gift.box.lottery.count` | GetActivityGiftBoxLotteryCount | `p=2` PutInt | ActGiftBoxData.GiftBoxLotteryCount | - |
| `get.activity.gift.box.reward` | GetGiftBoxProgressReward | `p=3` PutInt | ActGiftBoxData.GetGiftBoxProgressReward | - |
| `get.bind.mail.reward` | GetBindMailReward | `p=1`  | AccountManager.SaveBindAccountReward | - |
| `get.del.mail.list` | MailGetNeedDelList | `p=1`  | MailFacade.IsUseNewSystem | - |
| `get.friend.apply.list` | GetFriendApplyList | `p=1`  | FriendManager.InitApplyList | - |
| `get.friend.list` | GetFriendList | `p=2` PutBool | FriendManager.InitFriendList | - |
| `get.friend.moments.like.info` | MomentFriendLikeInfo | `p=1`  | MomentManager.HandleFriendMomentsLikeInfo | - |
| `get.friend.moments.like.reward` | MomentFriendLikeReward | `p=3` PutInt | MomentManager.HandleFriendMomentsLikeRewardFailed | - |
| `get.gift.detail` | GetGiftDetail | `p=3` PutUtfString, PutInt | PresentManager.HandlePresentHistory | - |
| `get.gift.reward.info` | GetGiftRewardInfo | `p=1`  | PresentManager.HandleScore | - |
| `get.like.info` | GetLikeInfo | `p=1`  | LikeManager.HandleGetLikeInfo | - |
| `get.mine.cave.report` | UserGetMineCaveReport | `p=2` PutLong | MailInfoShim.NewFromRawData | - |
| `get.recharge.roll.info` | GetPaidLotteryData | `p=2` PutInt | PaidLotteryManager.OnRecvPaidLotteryInfoResp | - |
| `get.skin.activity.info` | GetSkinActivityInfo | `p=2` PutInt | DecorationGiftPackageManager.GetActivityDataHandler | - |
| `get.translate.rate.reward` | GetTranslateRateReward | `p=2` PutSFSArray, PutUtfString, PutInt | RewardManager.AddOneReward | - |
| `get.week.card.info` | GetWeekCardList | `p=1`  | WeekCardManager.UpdateWeekCardList | - |
| `gift.show.info` | GiftShowInfo | `p=1`  | PresentManager.HandlePresentShowInfo | - |
| `gift.vouchers.reward.list` | GiftVouchersRewardList | `p=1`  | HeroSkinShopManager.UpdateTicketData | - |
| `give.up.activity.gift.box` | GiveUpActivityGiftBox | `p=3` PutInt, PutLong | ActGiftBoxData.GiveUpActivityGiftBox | - |
| `halloween.draw.receive.gift` | LotteryMachineActivityReceiveGift | `p=2` PutInt | HalloweenLotteryInfo.ParseMessage | LotteryMachineActivityReceiveGift |
| `like.goblin.treasure` | LikeGoblinTreasure | `p=2` PutLong | GoblinTreasureManager.HandleLikeErrorResponse | - |
| `mail.cancel.save` | MailCancelFavor | `p=3` PutUtfString, PutInt | MailFacade.OnFavorResponse | - |
| `mail.favorite.list` | MailFavoriteList | `p=1`  | MailFacade.IsUseNewSystem | - |
| `mail.favorite.read` | MailFavoriteRead | `p=2` PutSFSArray | MailFacade.IsUseNewSystem | - |
| `mail.like` | MailLike | `p=3` PutUtfString, PutInt | LikeManager.HandelMailLike | - |
| `mail.read` | MailGet | `p=4` PutUtfString | MailFacade.IsUseNewSystem | - |
| `mail.reward.batch` | MailRewardBatch | `p=2` PutUtfString | MailFacade.IsUseNewSystem | ReadOneMailRespond |
| `mail.save` | MailAddFavor | `p=3` PutUtfString, PutInt | MailFacade.OnFavorResponse | - |
| `mail.translate` | MailTranslate | `p=4` PutUtfString | MailFacade.IsUseNewSystem | - |
| `modify.gift.show` | ModifyGiftShow | `p=2` PutUtfString, PutSFSObject | PresentManager.SendGetShowList | - |
| `open.activity.gift.box` | OpenActivityGiftBox | `p=3` PutInt, PutLong | ActGiftBoxData.OpenGiftBoxHandle | - |
| `post.friend.moments` | MomentFriendPost | `p=1`  | MomentManager.HandlePostFriendMoments | - |
| `push.add.emoji` | PushAddEmoji | `p=1`  | MarchEmojiDataManager.PushAddEmojiHandler | - |
| `push.add.like` | PushAddLike | `p=3`  | LikeManager.HandlePushAddLike | - |
| `push.del.mail` | PushNeedDelMail | `p=1`  | MailFacade.IsUseNewSystem | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (154 windows)

**Active HUD Buttons:** `btnMail` [Mail] @ (98.0%,81.7%), `Btn` [] @ (92.0%,89.9%), `GroupIcon2` [] @ (92.5%,90.3%), `GroupIcon1` [] @ (91.5%,90.3%), `GroupIcon4` [] @ (92.5%,88.4%), `GroupIcon3` [] @ (91.5%,88.4%), `chatObj` [Evatrix:] @ (50.0%,96.9%)

**`GoToUtil` Routers:** `GoToResLack.GotoLovelyFavor` -> ['UIResourceLackNew'], `GoToResLack.GotoMarchEmoji` -> [], `GoToUtil.GoGiftMall` -> ['UIGiftPackage'], `GoToUtil.GoNewsletterView` -> ['UILoveNewsletter'], `GoToUtil.GoNewsletterViewToStory` -> ['UILoveNewsletter'], `GoToUtil.GoToMonthCard` -> ['UIGiftPackage'], `GoToUtil.GotoGiftPackView` -> ['UIScrollPack'], `GoToUtil.GotoOpenItemTipWindow` -> ['UIItemChatTitleTip'], `GoToUtil.GotoPay` -> ['UIGiftPackage']

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIChatInviteToJoin` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatInviteToJoin/...` | DefineToggle, Music_Effect_Button, OnInfoBtnClick, R... | MsgDefines.CreateGroupChatCheck |
| `UIChatPlayerSetNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISetting/UIChatSet.prefab` | BTN_GRAY_PATH, BTN_NORMAL_PATH, UIButton, addFriendB... | ChatMsgDefines.ChatLock, MsgDefines.AllianceInv... |
| `UIChatWorldShoutAtSomeOne` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatInviteToJoin/...` | DefineToggle, Music_Effect_Button, OnInfoBtnClick, R... | MsgDefines.CreateGroupChatCheck |
| `UICommon18PlusPopupEmail` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Common/UICommon18PlusPopupEma...` | Music_Effect_Button, OnCloseBtnClick, OnDoAuthBtnCli... | - |
| `UIChatSetLevelLimit` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatSetLevelLimit...` | Music_Effect_Button, UIButton, btnInfoBtn, btnInfoCl... | MsgDefines.GolloesShareControl, MsgDefines.SetC... |
| `UIMomentPost` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UICha...` | InitButtonState, Root/BigBtnBlue, Root/BigBtnBlue/bt... | - |
| `UIChatItemOperatorView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatItemOperator/...` | OnClickReportDataBtn, OnTranslationBtn, _btnAt, _btn... | ChatMsgDefines.ChatRevert |
| `UIChatRoomManagerSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoomManagerSe...` | Music_Effect_Button, OnBtnClick, UIButton, addBtn, a... | ChatMsgDefines.RoomGroupManagerAdd |
| `UILoveNewsletterFilter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatLoveFilterBox....` | RefreshToggles, campAllToggle, campToggle1, campTogg... | - |
| `UIMailTroopInfoListView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/TroopInfoL...` | OnClickBtnAlive, OnClickBtnClose, OnClickBtnInjure, ... | - |
| `UILuckyRollTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/UILu...` | OnClickUseBtn, UIButton, UIToggle, _close_btn, back_... | - |
| `UIMailTroopInfoListView4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/TroopInfoL...` | OnClickBtnAlive, OnClickBtnClose, OnClickBtnInjure, ... | - |
| `UIChatVoteCreatTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIChatVo...` | BtnClose, UIToggle, root/ToggleGroupSubTab/Toggle1, ... | - |
| `UIChatRemoveMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRemoveMember/...` | Music_Effect_Button, OnRemoveBtnClick, UIButton, btn... | - |
| `UIChatVoteCreat` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIChatVo...` | UIButton, UpdateBtnState, anonSwitchBtn, anon_help_b... | - |
| `UIEmojiSettingStateTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIEmojiSetting/UIEmojiSetting...` | Music_Effect_Button, OnCloseBtnClick, ShowBtn, Updat... | MsgDefines.ItemUse |
| `UIMomentDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UICha...` | CanShowAutoTraBtn, SetChatBtnInternal, UIButton, UIC... | - |
| `UIFishingCatalogGiftHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/GiftHistory/...` | DefineToggles, Music_Effect_Button, ToggleControlBor... | MsgDefines.GetSendFishRecord |
| `UIMailSend` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailSend.prefab` | OnClickSendBtn, OnClickSwitchBtn, UIButton, closeBtn... | MsgDefines.MailSend |
| `UIMailSend4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailSend.prefab` | OnClickSendBtn, OnClickSwitchBtn, UIButton, closeBtn... | MsgDefines.MailSend |
| `UIPublishALAnnouncement` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIPublis...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | - |
| `UIRedenvelopeView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeView...` | Music_Effect_Button, OnInfoBtnClick, UIButton, btn_c... | MsgDefines.GetRedPack |
| `UIShareMail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIShareMail.prefab` | CheckShowShareBtn, OnClickBtnClose, OnClickShareBtn,... | - |
| `CardGetReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/WeekCard/CardGetR...` | UIButton, close_btn, close_btn_path, onekey_btn_path... | MsgDefines.ClaimGolloesDailyReward, MsgDefines.... |
| `MailVerificationPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPayPassword/MailVerificatio...` | OnButtonCloseClicked, OnButtonConfirmClicked, UIButt... | MsgDefines.CheckPayPwdCode |
| `UIChangeChatRoomName` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoom/UIChange...` | InitButtonState, Music_Effect_Button, UIButton, btn_... | MsgDefines.AlName, MsgDefines.AllianceChangeAtt... |
| `UIMailInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailInfo.prefab` | Music_Effect_Button, OnClickReplayBtnNew, RefreshToB... | - |
| `UIMailInfo4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailInfo.prefab` | Music_Effect_Button, OnClickReplayBtnNew, RefreshToB... | - |
| `UIMailNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailMainPanel.prefab` | Music_Effect_Button, OnClickBtnBatchCancel, ShowJump... | - |
| `UIMailNew4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailMainPanel.prefab` | Music_Effect_Button, OnClickBtnBatchCancel, ShowJump... | - |
| `UIRedenvelopeSelectView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatNew/UIRedenvelopeSelectVi...` | ImgBg/BigBtnChoose, ImgBg/BigBtnChoose/btnText, Musi... | - |
| `UIRedenvelopeSend` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeSend...` | Music_Effect_Button, UIButton, _sendRed_btn, btn_bg,... | MsgDefines.SendRedPack |
| `UIChangeFriendName` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Friend/UIChangeFriendName...` | Music_Effect_Button, UIButton, clear_btn, close_btn,... | MsgDefines.CheckFriendAlias, MsgDefines.SetFrie... |
| `UIChatImgShow` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatImgShow.prefab` | Music_Effect_Button, OnClickReportBtn, UIButton, _bt... | - |
| `UILoveNewsletter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatLove.prefab` | RefreshToggle, Toggle1, Toggle2, ToggleTag, toggle1 | MsgDefines.SurvivalHeroMessagePowerBuy |
| `UIMainNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMainNotice/UIMainNotice.prefab` | ToggleControlBorS, _btnToBottom, btnGetReward, isBtn... | - |
| `UILWTrainScene` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainScene.pr...` | MailToggleGroupTruck, Music_Effect_Button, RefreshSc... | - |
| `UILikeHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeHistory.prefab` | Right/ToggleGroupBg, UIButton, UICommonPopUpTitle/Cl... | - |
| `UIMailDetailReportView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/MailDetail...` | OnClickBtnClose, OnClickBtnCloseAllRound, UIButton, ... | - |
| `UIMomentCommentOperatorView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatItemOperator/...` | _btnAt, _btnCopy, _btnDel, _btnReply, _btnRevert | - |
| `ThanksGivingTurkeySelectPlayerPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingTur...` | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle | - |
| `UIGivingRoses2FlowerSelectPlayerPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses...` | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle | - |
| `UIHalloweenGiftRecommendView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/GiveGif...` | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle | - |
| `UIMailDetailReportView4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/old/BattleReport/MailDe...` | OnClickBtnClose, OnClickBtnCloseAllRound, UIButton, ... | - |
| `UIRedenvelopeRageListPopupView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeRage...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `love_message_story` | TableName.LoveMessageStory | 1,249 | id, next_id, time, chat_type, chat_person, chat_text, show_time, photo_num, battery, chat_pic |
| `mistress_chat` | TableName.MistressChat | 772 | id, mistress_id, group_id, trigger_name, trigger_order, triggertype, triggerpara, chat_id, n... |
| `mail_show_id` | TableName.MailShowId | 197 | id, banner, icon_read, icon_unread, superscript, bg_read, bg_unread, icon_win, icon_lose |
| `love_message_date` | TableName.LoveMessageData | 157 | id, next_id, type, time, name, text, bg_pic |
| `gift_reward` | TableName.PresentLevel | 100 | id, level, exp, good |
| `scrolling_announcement` | TableName.Announcement | 79 | id, type, content, priority, base, block, para1, loop |
| `mail_show` | TableName.MailShow | 37 | id, tab, show_id, sub_type |
| `love_message_hero` | TableName.LoveMessageHero | 33 | id, hero_id, head_pic, name, chat_id, chat_name, chat_pic, unlock_pic, unlock_pic_j, chat_un... |
| `chat` | TableName.PveChat | 24 | id, chat_group_id, dialogID, view_time, chat_object |
| `wonder_gift` | TableName.WonderGift | 24 | id, name, type, reward, num, season, worth, icon |
| `mail_group` | TableName.MailGroup | 17 | id, order, type, name, show |
| `gift_special` | TableName.PresentSP | 15 | id, use_good, count, special_text, type, buff, special_desc |
| `gift` | TableName.Present | 13 | id, name, good_id, show_type, shop_pic, shop_pic_special, like, gift_exp, panel_type, festiv... |

**Enums:** `ChatClass_Enum` (230), `MailType` (180), `ChatEmojiNames` (138), `ChatEventEnum` (91), `ChatMsgMap` (88), `ChatPrefab_Enum` (38), `PresentTextIds` (35), `ChatGroupType` (22), `ChatGroupId` (19), `MailInternalGroup` (19), `MainViewChatBubbleType` (17), `PresentClass` (17), `ScoutMailTargetType` (17), `ChatReportBigType` (14), `MistressChatTriggerType` (13), `SlgGiftPackType` (11), `ChatReportType` (10), `eMailDetailActionType` (10), `ChatGroupTypeImg` (9), `ChatReportEntrance` (8), `MailToggleName` (8), `ChangeMailStatus` (7), `MailFightRoundReportType` (7), `TruckMailReportBG` (7), `WeekGiftCardType` (7)
