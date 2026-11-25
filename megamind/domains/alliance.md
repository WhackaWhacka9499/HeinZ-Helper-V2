# Domain Quick-Card: Alliance & Territory (`alliance`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain alliance`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **13** tasks / **17** bot fns / **5** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **645** packets |
| `DataCenter` Managers & Singletons | **62** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **196** windows / **4** active HUD buttons / **6** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **25** tables / **54** enums / **66** live events / **87** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

| Task Key | Title | Tag |
|---|---|---|
| `alliance_daily` | Alliance Red Packets & Tasks | `Packets + Task Boxes` |
| `radar_events` | Radar Events (Scan + All Types) | `Scan + All 4 Types` |
| `daily_tasks_complete` | Daily Tasks (Complete All) | `One-Go Auto-Complete` |
| `daily_claims` | Daily Tasks & Passes | `Tasks + Chests + Passes` |
| `vip_store_rewards` | VIP & Store Freebies | `Daily Rewards` |
| `rf_hq_under_attack` | Reinforce Attacked Allies | `Defense` |
| `tyrant_event` | Tyrant Rally | `F1 Host + Join` |
| `boomer_runs` | Boomer Rallies | `Auto-Join + Host` |
| `alliance_boss_mine` | Bear Trap & Alliance Mine | `Event + Gather` |
| `research_queue` | Research Queue | `Tech Lab` |
| `troop_training` | Train Troops (Event Speed-Zoom) | `All Barracks • FP/VS Zoom` |
| `building_upgrades` | Upgrade HQ & Buildings | `HQ Priority` |
| `bounties` | Gold Bounties (Lock Orange + Ally Help + P... | `3-in-1 • Lock Orange` |

| Bot Function (`tools/bot actions.py`) | Lines | `MsgDefines` Used | `DataCenter` Managers Used |
|---|---|---|---|
| `_normalize_eval_payload` | `L742-L772` | - | - |
| `_eval_json` | `L1220-L1234` | - | - |
| `_lua_claim_alliance_gifts_block` | `L1307-L1499` | AllianceGiftGetReward, AllianceReceiveAllGift, ReceiveGiftDailyRewa... | AllianceGiftDataManager |
| `run_auto_help` | `L1502-L1687` | AlHelpAll, AllianceCallHelp, AllianceGiftList | AllianceGiftDataManager, AllianceHelpDataManager, BuildManager, Que... |
| `run_rf_hq_under_attack` | `L1690-L1889` | ItemUse | AllianceAlertDataManager, ItemData, ItemTemplateManager, RadarAlarm... |
| `_probe_preparedness_phase` | `L2179-L2523` | ActivityEventInfoGet | ActPersonalArmsInfo, ActTimeCompeDataManager, ActivityListDataManag... |
| `_detect_training_event_boost` | `L2526-L2630` | - | - |
| `run_speedups` | `L3032-L3311` | BuildCcdMNew, QueueCcdMNew, QueueFinish | ActPersonalArmsInfo, ActivityListDataManager, AllianceCompeteDataMa... |
| `run_building_upgrades` | `L3866-L4124` | AllianceCallHelp, FreeBuildingUpNew | AllianceHelpDataManager, BuildManager, BuildQueueManager, BuildTemp... |
| `run_tyrant_event` | `L4127-L4308` | ReceiveAllianceBossAllianceReward | AllianceBossManager, AllianceWarDataManager, WorldPointManager |
| `run_boomer_runs` | `L4311-L4454` | FindMonster | AllianceWarDataManager, WorldPointManager |
| `run_war_safety` | `L8487-L8644` | ItemUse | AllianceAlertDataManager, ItemData, ItemTemplateManager, RadarAlarm... |
| `run_hospital_heal` | `L8647-L9805` | HospitalCure, QueueCcdMNew | ArmyManager, ArmyTemplateManager, HospitalManager, ItemData, QueueD... |
| `run_alliance_daily` | `L9811-L10046` | AlHelpAll, AlScienceDonate, AlScienceGoldDonate, AllianceGiftList, ... | AlContributeManager, AllianceGiftDataManager, AllianceHelpDataManag... |
| `_do_daily_social_likes` | `L11808-L11880` | - | MomentManager |
| `_do_daily_boss_rally` | `L12030-L12218` | FindMonster, FindMonsterBoss | AllianceWarDataManager, MonsterManager, WorldPointManager |
| `run_alliance_boss_mine` | `L12962-L13085` | ReceiveAllianceBossFreeReward | AllianceBossBearManager, AllianceMineManager |

**Hub `action_id` Routes:** `toggle_hospital_watcher` (L4664), `toggle_alliance_help_watcher` (L4669), `toggle_alliance_tech_watcher` (L4673), `get_alliance_deltas` (L4685), `export_alliance_members` (L4863)

## 2. `DataCenter` Managers & Outgoing Links (62)

| Manager | Methods | Outgoing `MsgDefines` | `EventId` Bus | Opens UI | XML Tables |
|---|---:|---|---|---|---|
| `_G.UIUtil` | 230 | ChatMsgDefines.==, ChatMsgDefines.do, MsgDefines.==, MsgDefine... | ==, ClickAny, ClickFarmBuildHide, HideMarchTip | DigTreasureGift, MainUI_SU, TryGetStr | TableName.EffectNumDesc, TableName.GatherResour... |
| `DataCenter.GloryManager` | 171 | MsgDefines.AlBattleEvent, MsgDefines.AlFightActInfo, MsgDefine... | EdenCampScore, EdenUserRank, GloryDeclareStateRefres... | UIGloryDeclareWarPopTips | TableName.APS_Season, TableName.AllianceResBuil... |
| `_G.MarchUtil` | 170 | MsgDefines.AllianceWarCancel, MsgDefines.AssistanceTeamRetreat... | MonthCardFourthGuide, RefreshUIWorldPointView, ShowM... | UIAllianceIntro, UIFormationLackPower, UIFormat... | TableName.Aps_Resource_Item, TableName.Desert, ... |
| `DataCenter.VolcanoWarManager` | 163 | MsgDefines.VolcanoBattleAllianceAllocateRewardRecord, MsgDefin... | VolcanoBattleCampScoreChange, VolcanoBattleCommandCh... | UIActivityRewardTip, UIAllianceMarkTip | TableName.EffectNumDesc, TableName.GatherResour... |
| `DataCenter.CrossWonderManager` | 149 | MsgDefines.BattleUserScoreRanklist, MsgDefines.GetServerBattle... | AlSkillInfoUpdate, CrossWonderGetInfo, CrossWonderWa... | UICommonHeadTip, UICrossWonderCountdownPanel, U... | TableName.Servers_Wonder_War, TableName.State_R... |
| `DataCenter.ActBloodMoonManager` | 118 | MsgDefines.BloodMoonRankGet, MsgDefines.FindBloodMoonMonster, ... | OnEnterWorld, RefreshBloodMoonInfo, RefreshBloodMoon... | UIActivityCenterTable, UISearch | TableName.GoodsTab, TableName.SeasonDonateBuild... |
| `DataCenter.WorldFavoDataManager` | 107 | MsgDefines.WorldAddAllianceMark, MsgDefines.WorldAddWorldMark,... | AllianceRallyRedPoint, CheckDragonMark, PveLevelEnte... | UIAllianceMarkTip | - |
| `DataCenter.AllianceBossManager` | 100 | MsgDefines.AllianceBossDonate, MsgDefines.AllianceBossSelectTi... | AllianceBossDonate, CallAllianceBoss, GetAllianceBos... | - | - |
| `DataCenter.ActivityListDataManager` | 96 | MsgDefines.ActivityEventInfoGet, MsgDefines.GetAlBattleDayVsIn... | AllianceCompeteRefreshUIScore, AllianceCumulativeBat... | UINoticeAlCompeteTips, UINoticeEquipTips | TableName.ActivityBarter, TableName.ActivityPanel |
| `DataCenter.AllianceBaseDataManager` | 96 | MsgDefines.AlFlagSpecialItem, MsgDefines.AlMoveInviteGetPoints... | AlWaitMergeStatusChange, AllianceAnnouncementTransla... | UIChat, UICreateSetAlliance, UIJoinAlliance | - |
| `DataCenter.AllianceBossBearManager` | 75 | MsgDefines.AllianceBossSelectTimeNew, MsgDefines.GetAllianceBo... | CallAllianceBossBear, GetAllianceBossBearActivityInf... | - | - |
| `DataCenter.ActTradePostManager` | 71 | MsgDefines.GetTradeAllianceRankInfo, MsgDefines.GetTradeCityRa... | CheckDayNightState, RefreshTradeAllianceRank, Refres... | UISeasonTradePostStore | TableName.SeasonGroup, TableName.TradePost, Tab... |
| `DataCenter.AllianceShopPlusDataManager` | 69 | MsgDefines.AlShopNewBuyAl, MsgDefines.AlShopNewBuyRecords, Msg... | AllianceShopPlusRestockBubble | - | TableName.APS_shop |
| `DataCenter.ActIceCaveManager` | 67 | MsgDefines.GetIceCaveAllianceRankInfo, MsgDefines.GetIceCaveEv... | RefreshFishingNum, RefreshIceCaveAllianceRank, Refre... | UIFishRewardGet, UIFishingCatalogUnlock | TableName.IceCaveInfo |
| `DataCenter.ActDispatchTaskDataManager` | 65 | MsgDefines.DispatchGetAllianceTasks, MsgDefines.DispatchGetLog... | BuildBoxOpenFinish, DispatchMissionStatusResponse, D... | UIDispatchRewardGet | TableName.ActivityPanel, TableName.LwDispatchSe... |
| `DataCenter.AllianceMemberDataManager` | 65 | MsgDefines.AlRank, MsgDefines.DonateRankReward | OnAllianceOfficialPosChange, OnGetNewAlJoinReq, Play... | UIAlMemberRecommend | - |
| `DataCenter.GhostKingBornManager` | 58 | MsgDefines.GhostKingInfo, MsgDefines.GhostKingRankInfo, MsgDef... | GhostKingBornActInfo, RefreshGhostKingRank, RefreshG... | - | TableName.GhostKingDonate, TableName.GhostKingI... |
| `DataCenter.AllianceWarDataManager` | 54 | MsgDefines.AllianceWarCancel, MsgDefines.AllianceWarRetreat, M... | AllianceWarInfoUpdate, AllianceWarNewStatusChanged, ... | UIAllianceWarInfoView, UIAllianceWarMainTable | TableName.HeroMilitaryRank, TableName.WorldCity |
| `DataCenter.ActBlackKnightManager` | 52 | MsgDefines.GetRank, MsgDefines.MonsterSiegeActivityInfo, MsgDe... | BlackKnightAllianceMemberInfoUpdated, BlackKnightRan... | UIBlackKnightComing | - |
| `DataCenter.AllianceMineManager` | 51 | MsgDefines.GetAllAllianceMineList, MsgDefines.GetAllMarchesOfA... | AllianceFlagUpdate, AllianceFrontUpdate, AllianceMem... | - | TableName.AllianceMine, TableName.AllianceResBuild |
| `DataCenter.AllianceAnnouncementManager` | 49 | MsgDefines.AdvAllianceNotice, MsgDefines.CommentAllianceNotice... | AllianceApplySuccess, ChatAllianceAnnouncementAdd, C... | UIPositionShare | - |
| `DataCenter.WorldAllianceFortressDataManager` | 48 | MsgDefines.FortressCancelSignUp, MsgDefines.FortressRewardMemb... | WorldFortressActivityUpdate, WorldFortressOwnerInfoC... | - | TableName.WorldFortressRewardGroup |
| `DataCenter.ThanksGivingCatchHitManager` | 47 | MsgDefines.GetAllianceTreasure, MsgDefines.TurkeyHuntAllianceL... | PlayHitTurkeyAnimation, TurkeyGaming, UpdateHitTurke... | UIHitTurkeyNotice | - |
| `DataCenter.AllianceRedPacketManager` | 45 | MsgDefines.GetAllianceRedPacket, MsgDefines.GetRedPack, MsgDef... | GetRedPacketUpdate, UpdateGold | - | TableName.SysRedPacket |
| `DataCenter.ThroneActManager` | 44 | - | RefreshActivityRedDot, RefreshThroneEntrance, Throne... | ThronePopupView | TableName.ActivityPanel |
| `DataCenter.AllianceDissolutionManager` | 43 | MsgDefines.AlCancelDismiss, MsgDefines.AlConfirmDismiss, MsgDe... | AllianceDismissStatusChanged, AllianceKickOverLimit,... | - | - |
| `DataCenter.DrakeBoss2Manager` | 37 | MsgDefines.ActivityRallyBossInfo, MsgDefines.ActivityRallyBoss... | DrakeBoss2InfoUpdate, RefreshActivityRedDot | UIBagView, UIDrakeBossUseItem | - |
| `DataCenter.LWAllyStationDataManager` | 36 | MsgDefines.AllianceTrainInfo | AllianceTrainBuySuccess, Arena3V3BattleFinish, DelAl... | - | TableName.LW_Train_Para |
| `DataCenter.AllianceLeaderRewardManager` | 35 | MsgDefines.GetAllianceWelfareInfo, MsgDefines.ReceiveAllianceW... | AllianceLeaderStageRewardReceived, UpdateGold | - | - |
| `DataCenter.AlContributeManager` | 33 | MsgDefines.ClaimAlContributeBoxReward, MsgDefines.GetAlContrib... | OnAlContributeBoxStatusChange, OnAlContributeRankInf... | - | - |
| `DataCenter.AllianceCityTipManager` | 33 | MsgDefines.UserGetActBossMarch | ChangeCameraLod | UIAllianceCityBar | - |
| `DataCenter.AllianceScienceDataManager` | 30 | MsgDefines.AlScienceNumFresh | AllianceScienceDonate, OnAlScienceRecommendChange | - | TableName.AlScienceTab |
| `DataCenter.NightBaronessManager` | 29 | MsgDefines.AlBeLeaderCheck, MsgDefines.SealCityBossInfo, MsgDe... | RefreshBloodMoonGeneral, RefreshWorldDeleteAllGhostG... | UIAllianceCity, UISeasonBaronessPushS5 | TableName.WorldCity |
| `DataCenter.RedPacketManager` | 29 | MsgDefines.ActivityRedPacketChoose, MsgDefines.GetActivityRedP... | ActivityRedPacketRefresh, ActivityRedPacketRefreshCh... | - | TableName.SysRedPacket |
| `DataCenter.AllianceHaggleManager` | 25 | MsgDefines.AllianceHaggle, MsgDefines.AllianceHaggleBuy, MsgDe... | RefreshActivityRedDot | UIActivityCenterTable | TableName.AllianceHaggle |
| `DataCenter.AllianceHelpVirtualMarchManager` | 25 | - | NoticeMainViewUpdateMarch, OnEnterCity, PveLevelEnter | - | - |
| `DataCenter.AllianceAlertDataManager` | 24 | MsgDefines.GetAllianceAlertInfo | UpdateAlertData | - | - |
| `DataCenter.AllianceGiftDataManager` | 22 | - | UpdateMainAllianceRedCount | - | - |
| `DataCenter.AllianceHelpDataManager` | 22 | MsgDefines.AlHelpAll, MsgDefines.AlHelpFromAll, MsgDefines.All... | AllianceBuildHelpNew, UpdateMainAllianceRedCount | - | - |
| `DataCenter.CastleAdventureManager` | 22 | MsgDefines.GetCastleAdventureAllianceProgress | OnPassDay, UpdateCastleAdventureAllianceHelp | - | - |
| `DataCenter.RedEquipBossRallyDataManager` | 22 | MsgDefines.GetAllianceMythicalEquipBossRallyInfo, MsgDefines.I... | RedEquipBossRallyRewardUpdate, RedEquipBossRallyUpda... | - | - |
| `DataCenter.AllianceDanMuManager` | 21 | MsgDefines.SendAlDanMu | AllianceDanMuShowEvent, PushDanMuDataEvent, SceneCha... | UIAlCompeteBarrage | - |
| `DataCenter.AllianceTempListManager` | 21 | - | SetALRankName | - | - |
| `DataCenter.DigTreasureDataManager` | 19 | MsgDefines.GetAllianceTreasure | OnDigTreasureTipEvent | - | - |
| `DataCenter.AllianceSkillManager` | 18 | MsgDefines.KingdomSkillUse, MsgDefines.WorldMissileInfo | - | - | - |

## 3. Key Wire Packets (645 total; top 60 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `push.challenge.alliance.boss.kill` | PushMonsterTowerAllianceBossKill | `p=1`  | ActMonsterTowerData.ParsePushAllianceBossKill | - |
| `survival.pve.level.finish` | SU_Pve_Level_Finish | `p=2` PutInt | SUPveLevelDataManager.SetLevelData | - |
| `accept.exploit.personal.reward` | ClaimAlContributeBoxReward | `p=3` PutUtfString, PutInt | AlContributeManager.OnRecvClaimBoxResp | - |
| `accept.kingdompersonal.reward` | StrongestCommandGetTodayReward | `p=4` PutUtfString, PutInt | RewardManager.ShowCommonReward | RefreshDataSingleScore |
| `accept.personal.reward` | AcceptPersonalReward | `p=2` PutUtfString, PutInt | ActPersonalArmsInfo.GetEventInfo | RefreshActivityRedDot |
| `act.city.people.dialog` | SU_ActCityPeople | `p=3` PutLong, PutUtfString | TalkTaskDataManager.UpdateFromDoomWalker | - |
| `activity.rally.boss.info` | ActivityRallyBossInfo | `p=2` PutInt | DrakeBoss2Manager.UpdateInfoHandle | - |
| `activity.rally.boss.update.stage` | ActivityRallyBossUpdateStage | `p=3` PutInt, PutUtfString | DrakeBoss2Manager.UpdateInfoHandle | - |
| `activity.red.packet.info` | GetActivityRedPacketInfo | `p=2` PutInt | RedPacketManager.UpdateStageInfo | - |
| `activity.red.packet.reward` | ReceiveActivityRedPacketReward | `p=3` PutInt | RedPacketManager.SendRewardHandle | - |
| `add.alliance.order.token.num` | AllianceOrderAddToken | `p=3` PutUtfString, PutInt | ActAllianceOrderManager.HandleMessageAddToken | - |
| `adv.alliance.notice` | AdvAllianceNotice | `p=3` PutLong, PutBool | AllianceAnnouncementManager.AdvAllianceNoticeHandler | - |
| `agree.alliance.auto.invite` | AcceptAllianceAutoInvite | `p=2` PutUtfString | AllianceAutoInviteManager.ClearAllInvite | - |
| `al.acceptapply` | AcceptAllianceApply | `p=2` PutUtfString | AllianceMemberDataManager.UpdateOneAllianceApply | AllianceMemberRedPoint |
| `al.apply` | AlApply | `p=4` PutUtfString, PutInt | AllianceBaseDataManager.UpdateAllianceBaseData | CLICK_ALLIANCE_ITEM |
| `al.applylist` | AlApplyList | `p=2` PutInt | AllianceMemberDataManager.UpdateAllianceApplyList | AllianceMemberRedPoint |
| `al.arena.power` | AlArenaPower | `p=2` PutUtfString | AllianceMemberDataManager.UpdateAllianceArenaPower | - |
| `al.attr` | AllianceChangeAttributes | `p=15` PutUtfString, PutInt, PutLong | AllianceBaseDataManager.UpdateAllianceSetting | UpdateGold |
| `al.attr.x.info` | - | `p=1`  | AllianceAttrXManager.OnAlAttrXInfoResponse | - |
| `al.attr.x.skill.use` | - | `p=2` PutInt | AllianceAttrXManager.OnAlAttrXSkillUseResponse | - |
| `al.attr.x.up` | - | `p=2` PutInt | AllianceAttrXManager.OnAlAttrXUpResponse | - |
| `al.battle.day.vs.info` | GetAlBattleDayVsInfo | `p=2` PutInt | AllianceCompeteDataManager.HandelDayVsInfo | - |
| `al.battle.event` | AlBattleEvent | `p=4` PutUtfString, PutLong, PutInt | GloryManager.HandleGetBattleDetail | - |
| `al.battle.live.like` | PushAlBattleLiveLike | `p=1`  | AllianceCompeteDataManager.UpdateLiveLikeNum | - |
| `al.battle.rank.info` | AllianceCompeteRankList | `p=2` PutLong | AllianceCompeteDataManager.RefreshRankList | - |
| `al.battle.rush.detail` | GetAlBattleRushDetail | `p=6` PutInt, PutLong | AllianceCompeteDataManager.HandelRushScoreDetail | - |
| `al.battle.week.result.info` | AllianceCompeteWeeklySummary | `p=1`  | AllianceCompeteDataManager.RefreshWeeklySummaryMsg | - |
| `al.battle.week.vs.info` | AllianceCompeteWeekResult | `p=1`  | AllianceCompeteDataManager.RefreshWeekResultVS | - |
| `al.call.help` | AllianceCallHelp | `p=5` PutLong, PutInt, PutUtfString | AllianceHelpDataManager.AddCheckHelpTimer | - |
| `al.cancelapply` | AlCancelApply | `p=2` PutUtfString | AllianceTempListManager.CancelApplyAllianceByUid | CLICK_ALLIANCE_ITEM |
| `al.cr.last.time` | AlCrLastTime | `p=1`  | AllianceMainManager.SetLastCreateTime | - |
| `al.create` | AlCreate | `p=8` PutUtfString, PutInt | AllianceBaseDataManager.UpdateAllianceBaseData | SetMovingUI |
| `al.dismiss` | AlDismiss | `p=1`  | AllianceDissolutionManager.IsFeatureEnabled | AllianceQuitOK |
| `al.donate.rank.all` | AllianceDonateRankAll | `p=1`  | AllianceDonateRankDataManager.UpdateRankHistoryList | AllianceDonateRankAll |
| `al.donate.rank.today` | AllianceDonateRankDay | `p=1`  | AllianceDonateRankDataManager.UpdateRankDayList | AllianceDonateRankDay |
| `al.donate.rank.week` | AllianceDonateRankWeek | `p=1`  | AllianceDonateRankDataManager.UpdateRankWeekList | AllianceDonateRankWeek |
| `al.duel.member.status` | AlDuelMemberStatus | `p=1`  | AllianceBaseDataManager.SetRejoinPunishInfo | OnAlDuelMemberStatusUpdate |
| `al.fight.act.info` | AlFightActInfo | `p=1`  | GloryManager.HandleGetAct | - |
| `al.fight.act.info.record` | AlFightActInfoRecord | `p=2` PutLong | GloryManager.HandleGetAct | - |
| `al.fight.act.member.score` | AlFightActMemberScore | `p=2` PutUtfString | GloryManager.HandleGetMemberRecord | - |
| `al.flag.special.item` | AlFlagSpecialItem | `p=2` PutLong | AllianceBaseDataManager.OnHandlerChangeSeasonEffect | - |
| `al.help.all` | AlHelpAll | `p=3` PutLong, PutBool | AllianceHelpDataManager.OnHelpAll | AllianceHelpSever |
| `al.kick` | AllianceKickMember | `p=2` PutUtfString | AllianceMemberDataManager.RemoveAllianceMemberByUid | AllianceMember |
| `al.kick.batch.result` | AlKickBatchResult | `p=1`  | AllianceDissolutionManager.IsFeatureEnabled | - |
| `al.leader.replace` | AllianceLeaderReplace | `p=2` PutUtfString | AllianceBaseDataManager.UpdateAllianceBaseData | UpdateGold |
| `al.leader.trans` | AllianceLeaderTrans | `p=2` PutUtfString | AllianceBaseDataManager.UpdateAllianceBaseData | AllianceMember |
| `al.leave` | AlLeave | `p=1`  | AllianceBaseDataManager.ResetAllianceData | AllianceQuitOK |
| `al.missile.create` | MissileCreate | `p=5` PutUtfString, PutLong, PutInt | MissileManager.MissileCreateHandler | - |
| `al.missile.info` | MissileInfoGet | `p=1`  | MissileManager.MissileInfoGetHandler | - |
| `al.offical.process` | AllianceDeleteOffical | `p=5` PutUtfString, PutInt | AllianceMemberDataManager.DeleteAllianceOfficial | AllianceMember |
| `al.rank` | AlRank | `p=2` PutUtfString | GuideManager.SetWaitingMessage | SelfAllianceMemberInfoPull |
| `al.refuseapply` | RefuseAllianceApply | `p=2` PutUtfString | AllianceMemberDataManager.UpdateOneAllianceApply | AllianceMemberRedPoint |
| `al.render.help` | AllianceRenderHelp | `p=3` PutUtfString | AllianceHelpDataManager.OnFinishAllianceHelp | AllianceHelpSever |
| `al.science.donate` | AlScienceDonate | `p=6` PutInt | AllianceScienceDataManager.EndRefreshAllScienceNum | ShowAlScienceCriticalHitRatio |
| `al.science.donate.gold` | AlScienceGoldDonate | `p=5` PutInt | AllianceScienceDataManager.EndRefreshAllScienceNum | UpdateGold |
| `al.science.fresh` | AlScienceFresh | `p=2` PutInt | AllianceScienceDataManager.EndRefreshAllScienceNum | AllianceTechnology |
| `al.science.recommend` | AlScienceRecommend | `p=3` PutInt | AllianceScienceDataManager.EndRefreshAllScienceNum | AllianceTechnology |
| `al.science.refreshNum` | AlScienceNumFresh | `p=2` PutInt | AllianceScienceDataManager.EndRefreshAllScienceNum | AllianceTechnology |
| `al.science.research` | AlScienceResearch | `p=2` PutInt | AllianceScienceDataManager.EndRefreshAllScienceNum | AllianceTechnology |
| `al.search` | AlSearch | `p=6` PutInt, PutUtfString, PutBool | AllianceTempListManager.RefreshSearchAllianceList | SearchAllianceSuccess |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (196 windows)

**Active HUD Buttons:** `BtnCrossThrone` [State Ruler] @ (93.9%,22.0%), `help` [] @ (94.4%,75.5%), `btnAlliance` [Alliance] @ (98.0%,75.5%), `buildBtn` [2] @ (5.3%,80.8%)

**`GoToUtil` Routers:** `GoToUtil.GoAllianceBossByVS` -> ['UISearch'], `GoToUtil.GoToByQuestId` -> ['UIHeroList', 'UIAllianceHelp', 'UIChatNew', 'UISearch', 'UIArenaPanel'], `GoToUtil.GoWorldCity` -> [], `GoToUtil.GotoAllianceIntroView` -> ['UIAllianceIntro'], `GoToUtil.GotoAlliancePersonalWarIntelligence` -> ['UIAllianceWarIntelligence'], `GoToUtil.GotoAllianceTeam` -> ['UIAllianceWarMainTable']

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIChatNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatNew.prefab` | ActivityToggleControlBorS, AddTreasureBtnRefreshTime... | MsgDefines.AlHelpAll, MsgDefines.VoteAllianceNo... |
| `UISpeed` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpeed/UISpeed.prefab` | CheckIfShowVsBtn, CloseMoreBtn, GetAllianceVsBtnIcon... | MsgDefines.BuildCcdMNew, MsgDefines.GirlCollect... |
| `UIAllianceGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceGift.p...` | OnDelAllBtnClick, OnGetAllBtnClick, UIButton, UITogg... | MsgDefines.AllianceAllGiftRemove, MsgDefines.Al... |
| `UIVolcanoMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoMain.prefab` | Music_Effect_Button, OnBuffBtnClick, OnGotoBtnClick,... | - |
| `UIWorldSiegePoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldSiegePoint.p...` | BtnAnimTime, ClearPendingSiegePointGuideBtnArrow, Ta... | - |
| `UIChangeAllianceCityName` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIChangeAllianceCityNam...` | InitButtonState, Music_Effect_Button, Root/BigBtnBlu... | MsgDefines.WorldChangeAllianceCityName, MsgDefi... |
| `UIChatPrivateRoomSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatPrivateRoomSe...` | Music_Effect_Button, UIButton, _cp_avatorBtn, addFri... | ChatMsgDefines.ChatLock, MsgDefines.AllianceInv... |
| `UICommonModal` | `UIContainer/TopCa...` | `Assets/Main/Prefabs/UI/Common/UICommonModal.prefab` | UIButton, btnGoN, btnRoot_path, btn_1, btn_1_path | - |
| `UIDetectEvent` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRadarCenter/UIDetectEvent.p...` | CompleteAllBtnClickTimer, GetAllRewardBtnClickTimer,... | MsgDefines.BatchDetectEventRewardReceive, MsgDe... |
| `UIAllianceHelp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceHelp.p...` | Music_Effect_Button, OnClickInfoBtn, OnClickPersonal... | MsgDefines.AlHelpAll, MsgDefines.AllianceRender... |
| `UISevenDayNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISevenDay/UISevenDayNew.prefab` | challengeSkinBtn, clickBtn/ItemIcon, close_btn, funB... | MsgDefines.DetectEventLauraRewardReceive, MsgDe... |
| `UIAllianceRallyInputPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceRallynputP...` | Root/Btn, Root/Btn/btnText, Root/Toggle, Root/Toggle... | - |
| `UIJoinAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIJoinAlliance.prefab` | Music_Effect_Button, ToggleControlBorS, UIButton, UI... | MsgDefines.AlApply, MsgDefines.AlCancelApply, M... |
| `UIMainMapLaunch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMiniMap/UIMainMapLaunch.prefab` | Music_Effect_Button, OnClickServerIdBtn, UIButton, b... | - |
| `UISettingAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UISettingAllianc...` | SetCountryBtnN, UIButton, abbr_change_btn, announce_... | MsgDefines.AllianceChangeAttributes |
| `UIThroneKingdomApplyPos` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneKingdomApply...` | Music_Effect_Button, ToggleControlBorS, UIButton, UI... | - |
| `UIAllianceApplyList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceApplyL...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | MsgDefines.AcceptAllianceApply, MsgDefines.Alli... |
| `UIAllianceJoinCondition` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceJoinCo...` | Music_Effect_Button, UIButton, btnText, btnText_path... | - |
| `UIAllianceWarMainTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceWarMai...` | PlayRefreshBtnPanelAnim, REFRESH_BTN_ANIM_CLIP, REFR... | MsgDefines.AllianceWarRetreat, MsgDefines.GetAl... |
| `UIAllianceShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceShop.p...` | GetCurButtonState, ToggleControlBorS, UIButton, UITo... | MsgDefines.AlShopBuyUsr |
| `UIGolloesCamp2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesCamp/UIGolloesCamp2....` | Common_btn_gray_M, Common_btn_yellow_M, RefreshBtnSh... | MsgDefines.ClaimGolloesDailyReward, MsgDefines.... |
| `UIPositionAppointSearch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneAppointmentS...` | Music_Effect_Button, RefreshBtn, UIButton, close_btn... | MsgDefines.AllianceRankList, MsgDefines.SendCon... |
| `UIWorldBlackTile` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISearch/UIWorldBlackTile.prefab` | CanShowWorldMarkBtn, ImgBg/Btn_mark, ImgBg/Btn_mark/... | - |
| `UIAllianceGiftInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceGiftInfo.p...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | MsgDefines.AllianceGiftGetReward |
| `UIAllianceInviteTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceInvite...` | OnClickCloseBtn, OnClickConfirmBtn, UIButton, closeB... | - |
| `UIAllianceWarDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceWarDetail....` | Music_Effect_Button, UIButton, _info_btn, close_btn,... | MsgDefines.AllianceWarCancel, MsgDefines.Allian... |
| `UIChangeNameGender` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIChangeNameGend...` | InitButtonState, UIButton, close_btn, return_btn, us... | MsgDefines.NickNameChange, MsgDefines.NickNameC... |
| `UICheckAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceCheckL...` | Music_Effect_Button, UIButton, btnRank, btnRankTxt, ... | MsgDefines.AlSearch |
| `UICommonShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICommonShop/UICommonShop.prefab` | GOLD_BTN_ORDER_MULTI_BUY, GOLD_BTN_ORDER_NORMAL, Ref... | - |
| `UIPresidentAppoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePresidentApp...` | Music_Effect_Button, UIButton, close_btn, close_btn_... | - |
| `UIResSupport` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceResAssist....` | Music_Effect_Button, OnClickConfirmBtn, OnClickTaxBt... | - |
| `UIAllianceCompeteNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllian...` | RefreshHelpBtn, alliance_btn_help, toggleN, togglesL... | MsgDefines.AlHelpAll, MsgDefines.AllianceCompet... |
| `UIAllianceDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceDetail...` | ImgBg/Align/commentButton/goTextMat, UIButton, comme... | MsgDefines.AlCancelApply, MsgDefines.AlSearch, ... |
| `UIAllianceMainTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceMainTa...` | AllianceButtonType, _defaultToggle, _guideBtn, _togg... | MsgDefines.AlLeaveItem |
| `UIChangeName` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIChangeName.prefab` | InitButtonState, Music_Effect_Button, UIButton, clos... | MsgDefines.NickNameChange, MsgDefines.NickNameC... |
| `UIChatCommanderTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatCommanderTi...` | _btnChatRestrict, _btnChatUnRestrict, _btnInviteN, a... | MsgDefines.AllianceInvitePlayer |
| `UIRedenvelopeSend1` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeSend...` | ToggleControlBorS, ToggleGroupTop/Toggle, UIToggle, ... | MsgDefines.QueryAllianceMemberActRecords, MsgDe... |
| `UIRedenvelopeSendWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeSend...` | RedPacket/ToggleGroup/CheckBox_, TextToggle, ToggleC... | MsgDefines.SendRedPack |
| `UIWorldRuinsPopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIWorldRuinsPopUp.pr...` | UIButton, click_btn, click_btn_path, close_btn, clos... | - |
| `UIAllianceCity` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceCity.p...` | _hideContent_btn, _showContent_btn, _tips_btn, buffB... | - |
| `UIAllianceRankTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceRankTa...` | RefreshToggleState, SetContributeBtnVisible, SetRewa... | MsgDefines.DailyAllianceDonaterRank |
| `UIAllianceShopPlusLaunch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/UIAlliance...` | Music_Effect_Button, OnToggleValueChanged, addBtnN, ... | - |
| `UIRuinRewardDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/RuinsKillingEn...` | UIButton, close_btn, close_btn_path, return_btn, ret... | MsgDefines.WorldGetAllianceCityDetail |
| `UISevenDay` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISevenDay/UISevenDay.prefab` | clickBtn/ItemIcon, gotoBtn, receiveAllBtn, receiveAl... | MsgDefines.UserDayActInfo |
| `ThroneRankView` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneRanking.prefab` | UIButton, closeBtn, close_btn_path, returnBtn, retur... | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `alliance_gift` | TableName.AllianceGift | 400 | id, level, exp, type, subtype, exceed_time, rewardId, scale, rate_show |
| `sys_red_packet` | TableName.SysRedPacket | 203 | id, type, building, level, desc, chat, num, res_type, gold, icon |
| `alScience` | TableName.AlScience | 150 | id, science_id, science_lv, max_lv, value, time, resource, donate, donate_price_start, donat... |
| `pvp_virtual_player` | TableName.NpcCity | 150 | id, duration, size, army, res, level, dialog, dialog_goto, dialog_win, dialog_lose |
| `alliance_haggle` | TableName.AllianceHaggle | 71 | id, unlock_level, members_num, group, rate, limit_servers, reward, haggle_type, price, lowes... |
| `alliance_gift_group` | TableName.AllianceGiftGroup | 67 | id, type, name, desc, color, icon, sender, title, each_exp, giftshow |
| `alScienceTab` | TableName.AlScienceTab | 51 | id, name, description, description_tip, icon, max_lv, position, relation, info, tab |
| `alliance_res_build` | TableName.AllianceResBuild, TableNa... | 37 | id, name, desc, model, icon, res_size, offter_range, level, res_durable, res_base_durable |
| `alliance_log` | TableName.AllianceLog | 33 | id, type, scale, icon, path |
| `alliance_resource` | TableName.AllianceResource | 24 | id, icon, name, description, city_level, alliance_gold_num, alliance_gold_capacity, alliance... |
| `food_festival_ingredients` | TableName.FoodFestivalIngredients | 24 | id, activity_id, good_id |
| `activity_treasure_alliance` | TableName.ActivityTreasureAlliance | 20 | id, activity, treasure_id, picture, collection, reward |
| `alliance_boss_property` | xmlValue.alliance_boss_property | 16 | id, difficulty, monsterId, name, alliance_reward, reward, alliance_bonus, alliance_reward_ne... |
| `alliance_task` | TableName.AllianceTask | 16 | id, unlock_time, name, description, type, para, times, reward, quest_pic, jump |
| `food_festival_table` | TableName.FoodFestivalEatTable | 16 | id, level, num, name, des, model, pic, pic_1, pic_2, quality |
| `exploit_rank` | xmlValue.exploit_rank | 12 | id, rank, score, reward, name, icon, star, rank_score_rate |
| `state_ruler_intro` | TableName.State_Ruler_Intro | 11 | id, level, exp, name, level_reward, buff_level_1, buff_level_2 |
| `night_eternal_duke_info` | TableName.GhostKingInfo | 7 | id, season_week, name, lv, threat_lv, desc, icon, spine_step, activity_icon, monster_id |
| `alliance_effect` | TableName.AlEffect | 6 | id, name, icon, description, description_value, description_type, order |
| `food_festival_building` | TableName.FoodFestivalEatBuild | 3 | id, quality, alliance_res_build_id, rank, table, name, pic, pic_1, des, world_des |
| `alliance_function` | TableName.AllianceFunction | 2 | id, lock_mode, id_tips, lock_condition |
| `night_eternal_duke_donate` | TableName.GhostKingDonate | 2 | id, donate_type, donate_stage, stage_reward, stage_reward_show, reissue_mail |
| `alliance_skill` | TableName.AllianceSkill | 1 | id, type, name, desc, rule, color, pre_time, during_time, prefab, punish_time |
| `capital_war` | TableName.CapitalWar | 1 | id, season, score_reward, rank_reward, kill_score, dead_score, occupy_score |
| `server_capital_reward` | TableName.Server_Capital_Reward | 1 | id, season, score_reward, reward_value, kill_score_inbuilding, kill_score, dead_score, kill_... |

**Enums:** `AllianceMarkIconName` (58), `AllianceMarkPrefabPath` (58), `AllianceMarkName` (57), `SlgAllianceFunctionType` (40), `AllianceButtonType` (34), `AllianceLogMemberType` (33), `AllianceTeamType` (18), `AllianceCompeteScoreUp` (14), `AllianceMemberManageType` (10), `AllianceCityShowTimeState` (9), `AllianceAlertType` (6), `AllianceBuildingState` (5), `AllianceDonateState` (5), `AllianceMemberOpenType` (5), `AllianceWarTipType` (5), `RedPacketState` (5), `UIAllianceCityTabType` (5), `AllianceBuildingMoveFailureReason` (4), `AllianceCareerEffectDescriptionType` (4), `AllianceCareerSelfColor` (4), `AllianceDonateRankType` (4), `AllianceHelpSelfTabColor` (4), `AllianceHelpState` (4), `AllianceHelpType` (4), `AllianceOfficialPos` (4)
