# Volume 07: Native C# Engine, HTTP/CDN Endpoints, Protobuf Schemas, GoTo Router & Call Graphs

> **Generated:** `2026-11-23 11:03:26 UTC` | **Sources:** `megamind/raw/csharp_and_http_endpoints.json` + `megamind/raw/datacenter_callgraph_and_protocols.json`

## 1. Deep Engine Layer Summary

| Layer | Verified Metric |
|---|---:|
| Native C# Loaded Assemblies | **98** assemblies |
| Reflected C# Game & HTTP Types | **3,772** clean classes/structs/enums (`3,177` in `Assembly-CSharp`) |
| Reflected C# Methods / Fields | **24,774** methods / **14,102** fields |
| Protobuf (`pb`) Message & Enum Schemas | **269** types (every field number & type) |
| Client HTTP / HTTPS / CDN / Upload URLs | **33** verified endpoints (secrets redacted) |
| `GoToUtil` / `GoToResLack` Jump Methods | **142** / **22** jump routers |
| DataCenter & Singleton Call Graph | **375** managers, **14,020** methods scanned, **6,613** linked |
| Call-Graph Cross-Edges | **811** Packet / **1,007** Event / **375** UI / **256** Table / **1,204** DC edges |
| Chat WebSocket & Mail V4 Modules | **21** `WebMessage` modules + **3** Mail V4 protocol modules |

## 2. Complete Client HTTP / HTTPS / CDN / Store / Telemetry Endpoints

| Endpoint URL | Source (Lua Module or C# Static Field) |
|---|---|
| `http://10.7.88.22:85/upload_img.php` | `C#:UploadImageManager.PHOTO_UPLOAD_URL_DEBUG` |
| `http://10.7.88.22:89/img/` | `SlgEngine.Framework.UI.Component.UIPlayerHead.OnCreate()` |
| `http://10.7.89.169:85/s3_upload.php` | `C#:UploadImageManager.CHAT_UPLAOD_URL_DEBUG` |
| `http://lm-s3.omnilojoapps.com:8086/ds/img/` | `C#:UrlUtils.HEAD_URL_MID` |
| `https://analyse-lm.omnilojoapps.com/ballevent.php` | `DataCenter.Global.LuaEntry.Init()` |
| `https://cdn-lm.omnilojo.app/hotupdate/` | `C#:VEngine.Versions.<DownloadURL>k__BackingField` |
| `https://cp.hhgame.vn` | `C#:HHIdentityUtil.Domain` |
| `https://firebase-lm.omnilojoapps.com/kidaction.php` | `DataCenter.AccountData.Auth.KIDAuth.GetHost()` |
| `https://firebase-lm.omnilojoapps.com/kidaction.php?` | `DataCenter.PayManager.PayManager_GetLocalPrice.GetHost()` |
| `https://gsl-lm.omnilojoapps.com/gameservice/getuidinfo.php?gameuid=` | `UI.UISetting.UISettingChangeUid.Controller.UISettingChangeUidCtrl.OnClick()` |
| `https://img-test.florereapps.com/alannment/` | `C#:ResourceExtention.ALANMT_URL_DEBUG` |
| `https://img-test.florereapps.com/chat/` | `C#:ResourceExtention.CHAT_URL_DEBUG` |
| `https://img-test.florereapps.com/moment/` | `C#:ResourceExtention.MOMENT_URL_DEBUG` |
| `https://last-z.com/#/customerService?uid=` | `Util.ZendeskUtil.ShowMessage()` |
| `https://last-z.com/?uid=` | `Slg.UI.UIPlayerInfo.Component.PlayerContent.OnWebLoginResult()` |
| `https://last-z.com/jpcotr.html` | `Util.CommonUtil.OpenJapaneseBillUrl()` |
| `https://last-z.com/jpfunds.html` | `Util.CommonUtil.OpenJapaneseBillUrl()` |
| `https://last-z.com/terms/` | `UI.UIPrivacy3.View.UIPrivacyView.OnPointerClick()` |
| `https://lm-s3.omnilojoapps.com/alannment/` | `C#:ResourceExtention.ALANMT_IMG_URL` |
| `https://lm-s3.omnilojoapps.com/chat/` | `SlgEngine.Chat.ChatManager2Base.GetChatImgUrl()` |
| `https://lm-s3.omnilojoapps.com/ds/img/` | `C#:UrlUtils.HEAD_URL` |
| `https://lm-s3.omnilojoapps.com/headicon/` | `C#:UIPlayerHead.HEAD_URL` |
| `https://lm-s3.omnilojoapps.com/moment/` | `C#:ResourceExtention.MOMENT_IMG_URL` |
| `https://naver.me/FFqfdW8F` | `Slg.UI.UIMailNew4.UIMailMainPanel.Component.MailTypeContent.MailSystem.OnClickBtnG...` |
| `https://statistics-lm.omnilojoapps.com/ballevent.php` | `C#:PostEventLog.POSTURL_Loading` |
| `https://store.last-z.com/#/order/mobileGame` | `UI.UIActivityCenterTable.Component.UIThirdPaymentAct.UIThirdPaymentAct.OnClickGoto...` |
| `https://store.last-z.com/getpcuser.php?uid=` | `DataCenter.PayManager.PayManager_GetLocalPrice.GetLocalPrice()` |
| `https://upload-img-lm.omnilojoapps.com/s3_upload.php` | `C#:UploadImageManager.CHAT_UPLAOD_URL` |
| `https://upload-img-lm.omnilojoapps.com/upload_img.php` | `Slg.UI.UIPlayerHeadIconSelect.Config.UIPlayerHeadIconSelect.Ctrl.__init()` |
| `ws://game-lm-ws-aws.omnilojoapps.com/` | `LuaDatatable.server_ip.data.1.13` |
| `ws://game-lm-ws.omnilojoapps.com/` | `LuaDatatable.server_ip.data.1.11` |
| `wss://game-lm-ws-aws.omnilojoapps.com/` | `LuaDatatable.server_ip.data.1.14` |
| `wss://game-lm-ws.omnilojoapps.com/` | `LuaDatatable.server_ip.data.1.12` |

### `LuaEntry` Network & Global Config Scalars
- **`LuaEntry.CrossNetwork`:** `__ctype=2`, `connectStartTime=0`, `connectTimeout=8`, `lastPingPongTime=0`, `lastPingSendRealtime=0`, `lastRtt=0`, `offMaxTime=15`, `retryCount=0`, `retryLimit=10`, `rttAlpha=0.3`, `sendPingPongCounter=0`, `sendPingPongInterval=1`, `smoothedRtt=0`
- **`LuaEntry.DataConfig`:** `__ctype=2`, `itemMd5=69428189d293f103ce61c3aa8903fdab241_434892d2424a218a8e3ec0b17d68d5380_1.250.733`
- **`LuaEntry.GlobalData`:** `IsChild=False`, `IsNeedIdentification=False`, `__ctype=2`, `allianceChat=`, `db_timezone_offset=0`, `db_utc_timestamp=0`, `downloadurl=`, `eu_state=0`, `gaid=`, `hasLogged=True`, `hotUpVersion=`, `isBindAcount=True`, `isCn=False`, `isUploadChatImg=False`, `lastChatInput=`, `nowGameCnt=0`, `pushO...
- **`LuaEntry.Network`:** `GameServerPort=8794`, `GameServerUrl=game-lm-r1.metapoint.club`, `Uid=1848029704000694`, `ZoneName=APS694`, `__ctype=2`, `bigBuffer=false`, `blackListEnabled=False`, `firstConnectDirectPending=False`, `isConnecting=False`, `lastUpdateTime=2325.5722954418`, `lineStatusInfo=`, `receiveBufferSizeCh...

## 3. Complete Protobuf (`pb`) Schema Registry (All 269 Types)

| Protobuf Type | Kind | Fields (`#num name:type`) |
|---|---|---|
| `.HotNews.HotNewsInfo` | `message` | `#1 uuid:int64`, `#2 point:int32`, `#3 totalDmg:int64`, `#4 joinCnt:int32`, `#5 startTime:int64`, `#6 endTime:int64`, `#7 mvpInfo:.HotNews.MvpInfo` |
| `.HotNews.LandInfo` | `message` | `#1 landId:int32`, `#2 hotNewsInfos:.HotNews.HotNewsInfo` |
| `.HotNews.MvpInfo` | `message` | `#1 name:string`, `#2 pic:string`, `#3 picVer:int32`, `#4 headSkinId:int32`, `#5 headSkinET:int64`, `#6 uid:string`, `#7 dmg:int64` |
| `.HotNews.WorldAllLandInfo` | `message` | `#1 landInfos:.HotNews.LandInfo` |
| `.google.protobuf.BoolValue` | `message` | `#1 value:bool` |
| `.google.protobuf.BytesValue` | `message` | `#1 value:bytes` |
| `.google.protobuf.DescriptorProto` | `message` | `#1 name:string`, `#2 field:.google.protobuf.FieldDescriptorProto`, `#3 nested_type:.google.protobuf.DescriptorProto`, `#4 enum_type:.google.protobuf.EnumDescriptorProto`, `#5 extension_range:.google.protobuf.Descript... |
| `.google.protobuf.DescriptorProto.ExtensionRange` | `message` | `#1 start:int32`, `#2 end:int32` |
| `.google.protobuf.DoubleValue` | `message` | `#1 value:double` |
| `.google.protobuf.EnumDescriptorProto` | `message` | `#1 name:string`, `#2 value:.google.protobuf.EnumValueDescriptorProto`, `#3 options:.google.protobuf.EnumOptions` |
| `.google.protobuf.EnumOptions` | `message` | `#2 allow_alias:bool`, `#3 deprecated:bool`, `#999 uninterpreted_option:.google.protobuf.UninterpretedOption` |
| `.google.protobuf.EnumValueDescriptorProto` | `message` | `#1 name:string`, `#2 number:int32`, `#3 options:.google.protobuf.EnumValueOptions` |
| `.google.protobuf.EnumValueOptions` | `message` | `#1 deprecated:bool`, `#999 uninterpreted_option:.google.protobuf.UninterpretedOption` |
| `.google.protobuf.FieldDescriptorProto` | `message` | `#1 name:string`, `#2 extendee:string`, `#3 number:int32`, `#4 label:.google.protobuf.FieldDescriptorProto.Label`, `#5 type:.google.protobuf.FieldDescriptorProto.Type`, `#6 type_name:string`, `#7 default_value:string`... |
| `.google.protobuf.FieldDescriptorProto.Label` | `enum` | `#1 LABEL_OPTIONAL:.google.protobuf.FieldDescriptorProto.Label`, `#2 LABEL_REQUIRED:.google.protobuf.FieldDescriptorProto.Label`, `#3 LABEL_REPEATED:.google.protobuf.FieldDescriptorProto.Label` |
| `.google.protobuf.FieldDescriptorProto.Type` | `enum` | `#1 TYPE_DOUBLE:.google.protobuf.FieldDescriptorProto.Type`, `#2 TYPE_FLOAT:.google.protobuf.FieldDescriptorProto.Type`, `#3 TYPE_INT64:.google.protobuf.FieldDescriptorProto.Type`, `#4 TYPE_UINT64:.google.protobuf.Fie... |
| `.google.protobuf.FieldOptions` | `message` | `#1 ctype:.google.protobuf.FieldOptions.CType`, `#2 packed:bool`, `#3 deprecated:bool`, `#5 lazy:bool`, `#10 weak:bool`, `#999 uninterpreted_option:.google.protobuf.UninterpretedOption` |
| `.google.protobuf.FieldOptions.CType` | `enum` | `#0 STRING:.google.protobuf.FieldOptions.CType`, `#1 CORD:.google.protobuf.FieldOptions.CType`, `#2 STRING_PIECE:.google.protobuf.FieldOptions.CType` |
| `.google.protobuf.FileDescriptorProto` | `message` | `#1 name:string`, `#2 package:string`, `#3 dependency:string`, `#4 message_type:.google.protobuf.DescriptorProto`, `#5 enum_type:.google.protobuf.EnumDescriptorProto`, `#6 service:.google.protobuf.ServiceDescriptorPro... |
| `.google.protobuf.FileDescriptorSet` | `message` | `#1 file:.google.protobuf.FileDescriptorProto` |
| `.google.protobuf.FileOptions` | `message` | `#1 java_package:string`, `#8 java_outer_classname:string`, `#9 optimize_for:.google.protobuf.FileOptions.OptimizeMode`, `#10 java_multiple_files:bool`, `#11 go_package:string`, `#16 cc_generic_services:bool`, `#17 ja... |
| `.google.protobuf.FileOptions.OptimizeMode` | `enum` | `#1 SPEED:.google.protobuf.FileOptions.OptimizeMode`, `#2 CODE_SIZE:.google.protobuf.FileOptions.OptimizeMode`, `#3 LITE_RUNTIME:.google.protobuf.FileOptions.OptimizeMode` |
| `.google.protobuf.FloatValue` | `message` | `#1 value:float` |
| `.google.protobuf.Int32Value` | `message` | `#1 value:int32` |
| `.google.protobuf.Int64Value` | `message` | `#1 value:int64` |
| `.google.protobuf.MessageOptions` | `message` | `#1 message_set_wire_format:bool`, `#2 no_standard_descriptor_accessor:bool`, `#3 deprecated:bool`, `#7 map_entry:bool`, `#999 uninterpreted_option:.google.protobuf.UninterpretedOption` |
| `.google.protobuf.MethodDescriptorProto` | `message` | `#1 name:string`, `#2 input_type:string`, `#3 output_type:string`, `#4 options:.google.protobuf.MethodOptions`, `#5 client_streaming:bool`, `#6 server_streaming:bool` |
| `.google.protobuf.MethodOptions` | `message` | `#33 deprecated:bool`, `#999 uninterpreted_option:.google.protobuf.UninterpretedOption` |
| `.google.protobuf.OneofDescriptorProto` | `message` | `#1 name:string` |
| `.google.protobuf.ServiceDescriptorProto` | `message` | `#1 name:string`, `#2 method:.google.protobuf.MethodDescriptorProto`, `#3 options:.google.protobuf.ServiceOptions` |
| `.google.protobuf.ServiceOptions` | `message` | `#33 deprecated:bool`, `#999 uninterpreted_option:.google.protobuf.UninterpretedOption` |
| `.google.protobuf.SourceCodeInfo` | `message` | `#1 location:.google.protobuf.SourceCodeInfo.Location` |
| `.google.protobuf.SourceCodeInfo.Location` | `message` | `#1 path:int32`, `#2 span:int32`, `#3 leading_comments:string`, `#4 trailing_comments:string`, `#6 leading_detached_comments:string` |
| `.google.protobuf.StringValue` | `message` | `#1 value:string` |
| `.google.protobuf.UInt32Value` | `message` | `#1 value:uint32` |
| `.google.protobuf.UInt64Value` | `message` | `#1 value:uint64` |
| `.google.protobuf.UninterpretedOption` | `message` | `#2 name:.google.protobuf.UninterpretedOption.NamePart`, `#3 identifier_value:string`, `#4 positive_int_value:uint64`, `#5 negative_int_value:int64`, `#6 double_value:double`, `#7 string_value:bytes`, `#8 aggregate_va... |
| `.google.protobuf.UninterpretedOption.NamePart` | `message` | `#1 name_part:string`, `#2 is_extension:bool` |
| `.protobuf.ActResouceArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 buildId:int32`, `#3 index:int32` |
| `.protobuf.ActResource` | `message` | `#1 configId:int32`, `#2 startTime:int64`, `#3 endTime:int64`, `#4 index:int32`, `#5 battlestarttime:int64` |
| `.protobuf.Activation` | `message` | `#1 code:string` |
| `.protobuf.AllFightLost` | `message` | `#1 lost:.protobuf.FightLost`, `#2 uuid:int64` |
| `.protobuf.AllReportReward` | `message` | `#1 reward:.protobuf.ReportReward`, `#2 uuid:int64` |
| `.protobuf.Alliance` | `message` | `#1 abbr:string`, `#2 name:string` |
| `.protobuf.AllianceBossInfo` | `message` | `#1 allianceId:string`, `#2 allianceAbbr:string`, `#3 allianceIcon:string`, `#4 level:int32` |
| `.protobuf.AllianceBuildArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 buildId:int32`, `#3 health:int32`, `#4 initHealth:int32`, `#5 afterHealth:int32`, `#6 buildLevel:int32` |
| `.protobuf.AllianceBuildingPointInfo` | `message` | `#1 uuid:int64`, `#2 buildId:int32`, `#3 level:int32`, `#4 state:int32`, `#5 alAbbr:string`, `#6 allianceId:string`, `#7 durability:int32`, `#8 lastDurabilityTime:int64`, `#9 durabilitySpeed:float`, `#10 alSrcServer:i... |
| `.protobuf.AllianceCityArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 cityId:int32`, `#3 health:int32`, `#4 initHealth:int32`, `#5 afterHealth:int32`, `#6 cityName:string` |
| `.protobuf.AllianceCityOccupyInfo` | `message` | `#1 cityId:int32`, `#2 abbr:string`, `#3 allainceId:string`, `#4 color:int32`, `#5 cityName:string`, `#6 icon:string`, `#7 buildPoint:int64`, `#8 buildStartTime:int64`, `#9 giveUpTime:int64`, `#10 protectTime:int64`, ... |
| `.protobuf.AllianceCityPointInfo` | `message` | `#1 cityId:int32`, `#2 openTime:int32`, `#3 state:int32`, `#4 protectTime:int32`, `#5 alAbbr:string`, `#7 allianceId:string`, `#8 durability:int32`, `#9 lastDurabilityTime:int32`, `#10 alName:string`, `#11 giveUpTime:... |
| `.protobuf.AllianceCityRecordProto` | `message` | `#1 killUserRecords:.protobuf.AllianceCityUserRecord`, `#2 destroyUserRecords:.protobuf.AllianceCityUserRecord` |
| `.protobuf.AllianceCityUserRecord` | `message` | `#1 uid:string`, `#2 point:int32`, `#3 longPoint:int64` |
| `.protobuf.AllianceFortressArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 fortressId:int32` |
| `.protobuf.AllianceInfo` | `message` | `#1 uid:string`, `#2 name:string`, `#3 abbr:string`, `#4 lang:string`, `#5 icon:string`, `#6 curMember:.google.protobuf.Int32Value`, `#7 maxMember:.google.protobuf.Int32Value`, `#8 fightPower:.google.protobuf.Int64Val... |
| `.protobuf.AllianceInvite` | `message` | `#1 expireTime:.google.protobuf.Int64Value` |
| `.protobuf.AllianceInviteMove` | `message` | `#1 inviteeUid:string`, `#2 inviteeName:string`, `#3 inviterUid:string`, `#4 inviterName:string`, `#5 targetPoint:.google.protobuf.Int32Value`, `#6 serverId:.google.protobuf.Int32Value` |
| `.protobuf.ArmyAttrInfo` | `message` | `#1 reason:int32`, `#2 value:float` |
| `.protobuf.ArmyCombatUnit` | `message` | `#1 simpleCombatUnit:.protobuf.SimpleCombatUnit`, `#2 armyInfo:.protobuf.ArmyUnitInfo`, `#3 specialArmyType:int32`, `#4 formationIndex:int32`, `#5 inAllianceTerritory:int32`, `#6 param:string`, `#7 edenSignal:float` |
| `.protobuf.ArmyDBUnitInfo` | `message` | `#1 uid:string`, `#2 soldiers:.protobuf.SoldierProto`, `#3 heroes:.protobuf.HeroInfoProto`, `#4 effectInfo:.protobuf.ArmyUnitEffectInfoProto`, `#5 formationIndex:int32`, `#6 suits:.protobuf.SuitInfoProto`, `#7 soldier... |
| `.protobuf.ArmyResult` | `message` | `#1 type:int32`, `#2 isDefeat:bool`, `#3 buildArmyResult:.protobuf.BuildArmyResult`, `#4 cityArmyResult:.protobuf.CityArmyResult`, `#5 simpleArmyResult:.protobuf.ArmyResultBase`, `#6 monsterArmyResult:.protobuf.Monste... |
| `.protobuf.ArmyResultBase` | `message` | `#1 pointId:int32`, `#2 armyObj:.protobuf.CombatUnit`, `#3 afterArmyObj:.protobuf.CombatUnit`, `#4 destroyValue:int32`, `#5 damagePercent:.protobuf.DamagePercentInfo` |
| `.protobuf.ArmyUnitBuff` | `message` | `#1 buffId:int32`, `#2 effectId:int32`, `#3 value:float`, `#4 expireTime:int32` |
| `.protobuf.ArmyUnitEffectInfoProto` | `message` | `#1 playerEffect:float`, `#2 formationEffect:float`, `#3 unitEffectReasons:.protobuf.UnitEffectReason`, `#4 unitBuffs:.protobuf.ArmyUnitBuff`, `#5 formationBuffs:.protobuf.ArmyUnitFormationBuff`, `#6 specialServerEffe... |
| `.protobuf.ArmyUnitFormationBuff` | `message` | `#1 buffId:int32`, `#2 effectId:int32`, `#3 value:float`, `#4 expireTime:int32`, `#5 timeType:int32`, `#6 type2:int32` |
| `.protobuf.ArmyUnitInfo` | `message` | `#1 soldiers:.protobuf.SoldierProto`, `#2 heroes:.protobuf.HeroInfoProto`, `#3 name:string`, `#4 alAbbr:string`, `#5 pic:string`, `#6 picVer:int32`, `#7 headFrame:int32`, `#8 careerType:int32`, `#9 careerLv:int32`, `#... |
| `.protobuf.BaseRoundReport` | `message` | `#1 triggerIndex:int32`, `#2 round:int32`, `#3 value:int32`, `#4 type:int32`, `#5 skillId:int32`, `#6 skillLevel:int32`, `#7 heroId:int32`, `#8 targetIndex:int32`, `#9 health:int32`, `#10 param:int32`, `#11 specialPar... |
| `.protobuf.BaseRoundReportPush` | `message` | `#1 roundReport:.protobuf.BaseRoundReport`, `#2 triggerUuid:int64`, `#3 targetUuid:int64` |
| `.protobuf.BattleDetailInfo` | `message` | `#1 roundReports:.protobuf.BaseRoundReport`, `#2 effectReports:.protobuf.EffectRoundReport`, `#3 playerInfos:.protobuf.DetailReportPlayerInfo` |
| `.protobuf.BattleEffectGroup` | `message` | `#1 memberUuid:int64`, `#2 battleEffectInfos:.protobuf.BattleEffectInfo`, `#3 heroBattleEffects:.protobuf.HeroBattleEffect` |
| `.protobuf.BattleEffectInfo` | `message` | `#1 effectId:int32`, `#2 value:float`, `#3 reasons:.protobuf.BattleEffectReason` |
| `.protobuf.BattleEffectReason` | `message` | `#1 value:float`, `#2 reason:int32` |
| `.protobuf.BattlePointInfo` | `message` | `#1 battleServerId:int32`, `#2 serverType:int32`, `#3 pointId:int32`, `#4 worldId:int32` |
| `.protobuf.BattleReport` | `message` | `#1 battleResult:int32`, `#2 startTime:int64`, `#3 startRound:int32`, `#4 battlePointInfo:.protobuf.BattlePointInfo`, `#5 fightReports:.protobuf.FightReport`, `#6 fightLost:.protobuf.FightLost`, `#7 selfBattleEffectGr... |
| `.protobuf.BattleReportAndDetail` | `message` | `#1 battle:.protobuf.BattleReport`, `#2 detail:.protobuf.BattleDetailInfo` |
| `.protobuf.BattleRoundPushInfo` | `message` | `#1 type:int32`, `#2 simpleArmyInfo:.protobuf.SimpleSelfArmyInfo`, `#3 combineArmyInfo:.protobuf.CombineSelfArmyInfo`, `#4 outRange:bool`, `#5 roundReports:.protobuf.BaseRoundReportPush`, `#6 selfBesieged:bool`, `#7 t... |
| `.protobuf.BlackLandRuinPointInfo` | `message` | `#1 state:int32`, `#2 alAbbr:string`, `#3 allianceId:string`, `#4 durability:int64`, `#5 endtime:int64`, `#6 alName:string`, `#7 icon:string`, `#8 aliserverId:int32` |
| `.protobuf.BloodMoonFloatInfo` | `message` | `#1 status:int32`, `#2 currentHp:int32`, `#3 initHp:int32` |
| `.protobuf.BloodMoonGeneralInfo` | `message` | `#1 allianceId:string`, `#2 allianceAbbr:string`, `#3 allianceIcon:string`, `#4 cityId:int32` |
| `.protobuf.BuildArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 level:int32`, `#3 buildId:int32` |
| `.protobuf.BuildInfo` | `message` | `#1 ownerUid:string`, `#2 uuid:int64`, `#3 buildId:int32`, `#4 level:int32`, `#5 buildState:int32`, `#6 queueState:int32`, `#7 allianceId:string`, `#8 updateEndTime:int32`, `#9 updateStartTime:int32`, `#10 lastHpTime:... |
| `.protobuf.BuildingBreak` | `message` | `#1 breakId:int32`, `#2 direction:int32` |
| `.protobuf.BuildingExtraInfo` | `message` | `#1 concertInfo:.protobuf.ConertActInfo`, `#2 thanksgivingInfo:.protobuf.ThanksStarInfo` |
| `.protobuf.ChallengeBossInfo` | `message` | `#1 bossOwnerUid:string`, `#2 callHelp:int32`, `#3 allianceId:string` |
| `.protobuf.ChangeAllianceInvite` | `message` | `#1 allianceId:string`, `#2 expireTime:int64`, `#3 status:int32`, `#4 targetAllianceType:int32`, `#5 configId:int32` |
| `.protobuf.ChristmasTreeInfo` | `message` | `#1 activityId:int32`, `#2 allianceId:string`, `#3 allianceName:string`, `#4 abbr:string`, `#5 level:int32`, `#6 topExp:int32` |
| `.protobuf.CityArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 level:int32`, `#3 isDirect:bool`, `#4 hospitalLeft:int32`, `#5 hasHospitalInfo:bool` |
| `.protobuf.CollectResourceInfo` | `message` | `#1 resourceType:int32`, `#2 level:int32`, `#3 type:int32`, `#4 attachId:int32` |
| `.protobuf.CollectRewardInfo` | `message` | `#1 ownerUid:string`, `#2 uuid:int64`, `#3 expireTime:int64`, `#4 contentId:int32` |
| `.protobuf.CombatUnit` | `message` | `#1 type:int32`, `#2 armyCombatUnit:.protobuf.ArmyCombatUnit`, `#3 combineCombatUnit:.protobuf.CombineCombatUnit`, `#4 simpleCombatUnit:.protobuf.SimpleCombatUnit` |
| `.protobuf.CombineCombatUnit` | `message` | `#1 simpleCombatUnit:.protobuf.SimpleCombatUnit`, `#2 members:.protobuf.ArmyCombatUnit` |
| `.protobuf.CombineSelfArmyInfo` | `message` | `#1 members:.protobuf.SimpleSelfArmyInfo`, `#2 targetInfo:.protobuf.SimpleCombatUnitPushObj` |
| `.protobuf.CompactNum` | `message` | `#1 num:int64` |
| `.protobuf.ConertActInfo` | `message` | `#1 concertEndTime:int64`, `#2 concertJoinUids:string` |
| `.protobuf.CrossPlunderData` | `message` | `#1 plunderRes:.protobuf.PlunderRes`, `#2 plunderResItem:.protobuf.PlunderResItem`, `#3 plunderItem:.protobuf.PlunderItem` |
| `.protobuf.CrossThroneBuildArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 buildId:int32` |
| `.protobuf.CrossThroneBuildPointInfo` | `message` | `#1 uuid:int64`, `#2 buildId:int32`, `#3 alAbbr:string`, `#4 allianceId:string`, `#5 openTime:int64`, `#6 startTime:int64` |
| `.protobuf.CrossThroneBuilding` | `message` | `#1 id:int32` |
| `.protobuf.DamagePercentInfo` | `message` | `#1 targetUuid:int64`, `#2 damagePercent:float`, `#3 woundedPercent:float`, `#4 injuredPercent:float`, `#5 deadPercent:float`, `#6 selfUuid:int64` |
| `.protobuf.DateTime` | `message` | `#1 milliseconds:.google.protobuf.Int64Value`, `#2 seconds:.google.protobuf.Int32Value` |
| `.protobuf.DefendArmyInfo` | `message` | `#1 defends:.protobuf.ArmyDBUnitInfo` |
| `.protobuf.DeliteFightReport` | `message` | `#1 uuid:int64`, `#2 selfArmyResult:.protobuf.ArmyResult`, `#3 otherArmyResult:.protobuf.ArmyResult`, `#4 fightResult:int32`, `#5 selfBattleEffectGroups:.protobuf.BattleEffectGroup`, `#6 otherBattleEffectGroups:.proto... |
| `.protobuf.DeliteReport` | `message` | `#1 battleResult:int32`, `#2 startTime:int64`, `#3 selfInfo:.protobuf.ReportPlayerInfo`, `#4 otherInfo:.protobuf.ReportPlayerInfo`, `#5 fightReports:.protobuf.DeliteFightReport`, `#6 parse:int32`, `#7 round:int32`, `#... |
| `.protobuf.DemonHunterInfo` | `message` | `#1 confId:int32` |
| `.protobuf.DesertArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 desertId:int32`, `#3 mineId:int32` |
| `.protobuf.DesertInfo` | `message` | `#1 id:int32`, `#2 uuid:int64`, `#3 desertId:int32`, `#4 protectEndTime:int32`, `#5 uid:string`, `#6 allianceId:string`, `#7 serverId:int32`, `#8 hasAssistance:bool`, `#9 mineId:int32`, `#10 ownerServer:int32`, `#11 o... |
| `.protobuf.DestroyMail` | `message` | `#1 time:int64`, `#2 type:int32`, `#3 pointId:int32`, `#4 destroyPlayerInfo:.protobuf.ReportPlayerInfo`, `#5 destroyUnitInfo:.protobuf.DestroyUnitInfo`, `#6 attackType:int32`, `#7 allianceInfo:.protobuf.ReportAlliance... |
| `.protobuf.DestroyUnitInfo` | `message` | `#1 type:int32`, `#2 itemId:int32`, `#3 initDurability:int32`, `#4 durability:int32`, `#5 dmg:int32`, `#6 level:int32`, `#7 extraInfo:string` |
| `.protobuf.DetailReportPlayerInfo` | `message` | `#1 index:int32`, `#2 name:string`, `#3 alAbbr:string`, `#4 isSelf:bool`, `#5 infoType:int32`, `#6 uuid:int64` |
| `.protobuf.Dialog` | `message` | `#1 id:string`, `#2 params:.protobuf.Message` |
| `.protobuf.DialogColor` | `enum` | `#0 DEFAULT_COLOR:.protobuf.DialogColor`, `#1 BLACK:.protobuf.DialogColor`, `#2 WHITE:.protobuf.DialogColor`, `#3 RED:.protobuf.DialogColor`, `#4 GREEN:.protobuf.DialogColor`, `#5 YELLOW:.protobuf.DialogColor`, `#6 BL... |
| `.protobuf.DispatchMission` | `message` | `#1 uuid:int64`, `#2 missionId:int32`, `#3 ownerUid:string`, `#4 allianceId:string`, `#5 startTime:int64`, `#6 finishTime:int64`, `#7 stealUids:string`, `#8 doubleReward:int32` |
| `.protobuf.DragonBuildArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 buildId:int32` |
| `.protobuf.DragonBuilding` | `message` | `#1 id:int32` |
| `.protobuf.DragonBuildingPointInfo` | `message` | `#1 uuid:int64`, `#2 buildId:int32`, `#3 state:int32`, `#4 alAbbr:string`, `#5 allianceId:string`, `#6 occupyTime:int64`, `#7 openTime:int64`, `#8 startTime:int64`, `#9 protectTime:int64`, `#10 rewardCount:int32`, `#1... |
| `.protobuf.DragonSecretKeyPointInfo` | `redacted/scalar` | `<REDACTED_SECRET>` |
| `.protobuf.Effect` | `message` | `#1 effectStr:string` |
| `.protobuf.EffectReason` | `message` | `#1 reason:int32`, `#2 value:float` |
| `.protobuf.EffectRoundReport` | `message` | `#1 baseReport:.protobuf.BaseRoundReport`, `#2 time:int32` |
| `.protobuf.EffectRoundReportPush` | `message` | `#1 roundReport:.protobuf.EffectRoundReport`, `#2 triggerUuid:int64`, `#3 targetUuid:int64` |
| `.protobuf.EquipInfoProto` | `message` | `#1 equipId:int32`, `#2 lv:int32` |
| `.protobuf.ExplorePointInfo` | `message` | `#1 ownerUid:string`, `#2 uuid:int64`, `#3 eventId:string` |
| `.protobuf.FightItemLost` | `message` | `#1 itemId:string`, `#2 value:int32` |
| `.protobuf.FightLost` | `message` | `#1 resLostArr:.protobuf.FightResLost`, `#2 resItemLostArr:.protobuf.FightResItemLost`, `#3 itemLostArr:.protobuf.FightItemLost` |
| `.protobuf.FightReport` | `message` | `#1 uuid:int64`, `#2 selfInfo:.protobuf.ReportPlayerInfo`, `#3 otherInfo:.protobuf.ReportPlayerInfo`, `#4 selfArmyResult:.protobuf.ArmyResult`, `#5 otherArmyResult:.protobuf.ArmyResult`, `#6 reward:.protobuf.ReportRew... |
| `.protobuf.FightReportShare` | `message` | `#1 contents:string`, `#2 createTime:int64`, `#3 uuid:int64`, `#4 toUser:string` |
| `.protobuf.FightResItemLost` | `message` | `#1 itemId:int32`, `#2 value:int32` |
| `.protobuf.FightResLost` | `message` | `#1 type:int32`, `#2 value:int32`, `#3 longValue:int64` |
| `.protobuf.FinishMissionInfo` | `message` | `#1 uuid:int64`, `#2 caveId:int32`, `#3 pointId:int32`, `#4 startTime:int64`, `#5 finishTime:int64` |
| `.protobuf.GarbagePointInfo` | `message` | `#1 ownerUid:string`, `#2 uuid:int64`, `#3 eventId:string`, `#4 endTime:int64` |
| `.protobuf.GhostKing` | `message` | `#1 uuid:int64`, `#2 status:int32`, `#3 startBattleTime:int64`, `#4 endBattleTime:int64`, `#5 monsterId:int32`, `#6 battleStageTime:int64`, `#7 durability:int64`, `#8 maxDurability:int64`, `#9 shieldUuid:int64` |
| `.protobuf.GoblinTreasure` | `message` | `#1 uuid:int64`, `#2 treasureId:int32`, `#3 ownerUid:string`, `#4 allianceId:string`, `#5 attNum:int32`, `#6 load:int32`, `#7 endTime:int64`, `#8 allianceAbbr:string`, `#9 likeNum:int32` |
| `.protobuf.HeroBattleEffect` | `message` | `#1 heroId:int32`, `#2 battleEffectInfos:.protobuf.BattleEffectInfo` |
| `.protobuf.HeroEquipInfoProto` | `message` | `#1 equipId:int32`, `#2 equipLv:int32`, `#3 promote:int32`, `#4 mythical:int32` |
| `.protobuf.HeroEquipUniqueInfoProto` | `message` | `#1 equipId:int32`, `#2 equipLv:int32`, `#3 promote:int32`, `#4 mythical:int32`, `#5 breakLv:int32` |
| `.protobuf.HeroInfoProto` | `message` | `#1 heroId:int32`, `#2 heroLevel:int32`, `#3 heroQuality:int32`, `#4 index:int32`, `#5 skillInfos:.protobuf.HeroSkillInfoProto`, `#6 heroUuid:int64`, `#7 maxLevel:int32`, `#8 rankLv:int32`, `#9 stage:int32`, `#10 plug... |
| `.protobuf.HeroSkillInfoProto` | `message` | `#1 skillId:int32`, `#2 skillLv:int32` |
| `.protobuf.HeroUnitEffect` | `message` | `#1 heroId:int32`, `#2 unitEffects:.protobuf.UnitEffect` |
| `.protobuf.IceAnimal` | `message` | `#1 uuid:int64`, `#2 configId:int32`, `#3 startTime:int64`, `#4 rewardTime:int64`, `#5 endTime:int64`, `#6 hasRewardNums:int32`, `#7 rewarduids:string`, `#8 state:int32`, `#9 allianceId:string` |
| `.protobuf.IntegerWithSpearated` | `message` | `#1 value:.google.protobuf.Int64Value` |
| `.protobuf.LandPointInfo` | `message` | `#1 id:int32`, `#2 landId:int32`, `#3 serverId:int32` |
| `.protobuf.LightCardInfo` | `message` | `#1 id:int32` |
| `.protobuf.Mail` | `message` | `#1 header:.protobuf.MailHeader`, `#2 body:.protobuf.MailBody`, `#3 custom:.protobuf.MailCustom` |
| `.protobuf.MailActResource` | `message` | `#1 id:int32`, `#2 index:.google.protobuf.Int32Value` |
| `.protobuf.MailBody` | `message` | `#1 content:.protobuf.Message`, `#2 pay:.protobuf.Pay`, `#3 reward:.protobuf.Reward`, `#4 userInfo:.protobuf.UserInfo`, `#5 allianceInfo:.protobuf.AllianceInfo`, `#6 allianceInviteMove:.protobuf.AllianceInviteMove`, `... |
| `.protobuf.MailCustom` | `message` | `#1 reply:int32`, `#2 share:int32`, `#3 like:int32`, `#4 activity:string`, `#5 deal:int32`, `#6 delUuid:int64`, `#7 xmlId:string` |
| `.protobuf.MailHeader` | `message` | `#1 title:.protobuf.Message`, `#2 subTitle:.protobuf.Message` |
| `.protobuf.MapAllIceCaveInfo` | `message` | `#1 infos:.protobuf.MapIceCaveInfo` |
| `.protobuf.MapAllTradePostInfo` | `message` | `#1 infos:.protobuf.MapTradePostInfo` |
| `.protobuf.MapIceCaveInfo` | `message` | `#1 caveId:int32`, `#2 pointId:int32`, `#3 abbr:string`, `#4 allianceId:string`, `#5 pic:string`, `#6 picVer:int32`, `#7 headSkinId:int32`, `#8 headSkinET:int64`, `#9 ownerUid:string`, `#10 serverId:int32`, `#11 name:... |
| `.protobuf.MapTradePostInfo` | `message` | `#1 buildingId:int32`, `#2 pointId:int32`, `#3 abbr:string`, `#4 allainceId:string`, `#5 pic:string`, `#6 picVer:int32`, `#7 headSkinId:int32`, `#8 headSkinET:int64`, `#9 ownerUid:string`, `#10 serverId:int32`, `#11 n... |
| `.protobuf.Message` | `message` | `#1 color:.protobuf.DialogColor`, `#2 bold:bool`, `#101 text:string`, `#102 dialog:.protobuf.Dialog`, `#103 point:.protobuf.PointInfo`, `#104 user:.protobuf.User`, `#105 alliance:.protobuf.Alliance`, `#106 monster:.pr... |
| `.protobuf.MinePlunderInfo` | `message` | `#1 userName:string`, `#2 rewardType:.google.protobuf.Int32Value`, `#3 itemId:string`, `#4 plunderRewardNum:.google.protobuf.Int32Value` |
| `.protobuf.Monster` | `message` | `#1 id:string` |
| `.protobuf.MonsterArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 monsterId:int32` |
| `.protobuf.MonsterCollectRewardMail` | `message` | `#1 startTime:int64`, `#2 monsterId:int32`, `#3 needCollectReward:.protobuf.ReportRewardNeedCollect` |
| `.protobuf.MonsterOwnerInfo` | `message` | `#1 name:string`, `#2 allianceAbbr:string` |
| `.protobuf.NormalMonsterInfo` | `message` | `#1 eventId:string` |
| `.protobuf.NpcCityArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 health:int32`, `#3 initHealth:int32`, `#4 afterHealth:int32`, `#5 npcPlayerInfo:.protobuf.NpcPlayerInfo`, `#6 isDirect:bool` |
| `.protobuf.NpcCityPointInfo` | `message` | `#1 uuid:int64`, `#2 npcId:int32`, `#3 lastHpTime:int32`, `#4 currentHp:int32`, `#5 name:string`, `#6 ownerUid:string`, `#7 eventId:string`, `#8 expireTime:int64` |
| `.protobuf.NpcPlayerInfo` | `message` | `#1 name:string`, `#2 pic:string`, `#3 srcServerId:int32`, `#4 pointId:int32`, `#5 npcId:int32`, `#6 country:string`, `#7 killNum:int32`, `#8 power:int32`, `#9 win:int32`, `#10 lose:int32`, `#11 deadNum:int32`, `#12 d... |
| `.protobuf.OverlordInfo` | `message` | `#1 overlordId:int32`, `#2 attackLv:int32`, `#3 defendLv:int32`, `#4 healthLv:int32`, `#5 rank:int32`, `#6 stage:int32`, `#7 militaryRank:int32`, `#8 militaryStage:int32`, `#9 power:int32`, `#10 skillInfo:.protobuf.Ov... |
| `.protobuf.OverlordInfoProto` | `message` | `#1 overlordId:int32`, `#2 attackLv:int32`, `#3 defendLv:int32`, `#4 healthLv:int32`, `#5 rank:int32`, `#6 stage:int32`, `#7 militaryRank:int32`, `#8 militaryStage:int32`, `#9 tankPower:int32`, `#10 skillInfo:.protobu... |
| `.protobuf.OverlordSkillInfoProto` | `message` | `#1 skillId:int32`, `#2 skillLv:int32` |
| `.protobuf.Pay` | `message` | `#1 gold:.google.protobuf.Int32Value`, `#2 choose:.google.protobuf.Int32Value`, `#3 redPacketId:string` |
| `.protobuf.PerRankInfo` | `message` | `#1 rewardInfo:.protobuf.RewardInfo`, `#2 scord:int64`, `#3 rank:int32`, `#101 playerInfo:.protobuf.RankUserInfo`, `#102 allianceInfo:.protobuf.RankAllianceInfo` |
| `.protobuf.PerSpecialDmgRecord` | `message` | `#1 uuid:int64`, `#2 dmg:int64` |
| `.protobuf.Percent` | `message` | `#1 intValue:.google.protobuf.Int32Value`, `#2 doubleValue:.google.protobuf.DoubleValue` |
| `.protobuf.PlunderItem` | `message` | `#1 itemId:string`, `#2 value:int32` |
| `.protobuf.PlunderRes` | `message` | `#1 type:int32`, `#2 value:int64` |
| `.protobuf.PlunderResItem` | `message` | `#1 itemId:int32`, `#2 value:int32` |
| `.protobuf.PointInfo` | `message` | `#1 server:.google.protobuf.Int32Value`, `#2 x:.google.protobuf.Int32Value`, `#3 y:.google.protobuf.Int32Value`, `#4 worldId:.google.protobuf.Int32Value` |
| `.protobuf.PveArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 monsterId:int32` |
| `.protobuf.RankAllianceInfo` | `message` | `#1 allianceId:string`, `#2 alAbbr:string`, `#3 alName:string`, `#4 alIcon:string` |
| `.protobuf.RankInfo` | `message` | `#1 rankType:.protobuf.RankInfo.RankType`, `#2 rankInfos:.protobuf.PerRankInfo` |
| `.protobuf.RankInfo.RankType` | `enum` | `#0 DEFAULT:.protobuf.RankInfo.RankType`, `#1 USER:.protobuf.RankInfo.RankType`, `#2 ALLIANCE:.protobuf.RankInfo.RankType` |
| `.protobuf.RankUserInfo` | `message` | `#1 uid:string`, `#2 name:string`, `#3 pic:string`, `#4 picVer:int32`, `#5 srcServerId:int32`, `#6 allianceInfo:.protobuf.RankAllianceInfo`, `#7 headFrame:int32`, `#8 careerType:int32`, `#9 careerLv:int32`, `#10 headS... |
| `.protobuf.ReportAllianceInfo` | `message` | `#1 allianceId:string`, `#2 alAbbr:string`, `#3 alName:string`, `#4 alIcon:string` |
| `.protobuf.ReportPlayerInfo` | `message` | `#1 uid:string`, `#2 name:string`, `#3 pic:string`, `#4 picVer:int32`, `#5 srcServerId:int32`, `#6 pointId:int32`, `#7 allianceInfo:.protobuf.ReportAllianceInfo`, `#8 headFrame:int32`, `#9 careerType:int32`, `#10 care... |
| `.protobuf.ReportReward` | `message` | `#1 rewardItems:.protobuf.ReportRewardItem`, `#2 rewardResourceItems:.protobuf.ReportRewardItem`, `#3 rewardHeroExps:.protobuf.ReportRewardHeroExp`, `#4 rewardResources:.protobuf.ReportRewardResource`, `#5 plunderResR... |
| `.protobuf.ReportRewardHeroExp` | `message` | `#1 heroId:int32`, `#2 level:int32`, `#3 expAdd:int32`, `#4 nowExp:int32`, `#5 oldExp:int32`, `#6 heroUuid:int64`, `#7 expAdd2:int64`, `#8 nowExp2:int64`, `#9 oldExp2:int64` |
| `.protobuf.ReportRewardItem` | `message` | `#1 type:string`, `#2 value:int32` |
| `.protobuf.ReportRewardNeedCollect` | `message` | `#1 pointId:int32`, `#2 inUserWorld:bool`, `#3 rewardUuid:int64` |
| `.protobuf.ReportRewardResource` | `message` | `#1 type:int32`, `#2 value:int32`, `#3 longValue:int64` |
| `.protobuf.Resource` | `message` | `#1 type:.google.protobuf.Int32Value`, `#2 value:.google.protobuf.Int32Value`, `#3 id:.google.protobuf.Int32Value`, `#4 longValue:.google.protobuf.Int64Value` |
| `.protobuf.ResourceInfo` | `message` | `#1 resourceId:int32`, `#2 state:int32`, `#3 gatherUuid:int64`, `#4 ownerUid:string`, `#5 eventId:string`, `#6 cooldownEndTime:int64`, `#7 ext:string` |
| `.protobuf.Reward` | `message` | `#1 reward:string`, `#2 rewardLevel:.google.protobuf.Int32Value`, `#3 rewardVersion:string`, `#4 rewardModule:.google.protobuf.Int32Value`, `#5 rewardInfo:.protobuf.RewardInfo` |
| `.protobuf.RewardInfo` | `message` | `#1 type:.google.protobuf.Int32Value`, `#2 id:.google.protobuf.StringValue`, `#3 num:.google.protobuf.Int64Value` |
| `.protobuf.RoadInfo` | `message` | `#1 ownerUid:string`, `#2 uuid:int64`, `#3 roadState:int32`, `#4 inside:int32`, `#5 currentHp:int32`, `#6 allianceId:string` |
| `.protobuf.RoundStatusInfo` | `message` | `#1 statusId:int32`, `#2 time:int32` |
| `.protobuf.SamplePointInfo` | `message` | `#1 ownerUid:string`, `#2 uuid:int64`, `#3 eventId:string` |
| `.protobuf.ScienceGroupInfo` | `message` | `#1 uuid:int64`, `#2 scienceGroups:.protobuf.ScienceGroupProto` |
| `.protobuf.ScienceGroupProto` | `message` | `#1 id:int32`, `#2 sumLevel:int32`, `#3 sumLevelMax:int32`, `#4 percent:float`, `#5 power:float`, `#6 scienceInfo:.protobuf.ScienceProto` |
| `.protobuf.ScienceProto` | `message` | `#1 id:int32`, `#2 level:int32`, `#3 levelMax:int32`, `#4 power:float` |
| `.protobuf.ScountDesert` | `message` | `#1 des_id:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo` |
| `.protobuf.ScountNpcCity` | `message` | `#1 name:string`, `#2 pic:string`, `#3 srcServerId:int32`, `#4 pointId:int32`, `#5 npcId:int32`, `#6 country:string`, `#7 killNum:int32`, `#8 power:int32`, `#9 win:int32`, `#10 lose:int32`, `#11 deadNum:int32`, `#12 d... |
| `.protobuf.ScountNpcCityWall` | `message` | `#1 hp:.google.protobuf.Int32Value`, `#2 hpMax:.google.protobuf.Int32Value`, `#3 visible:.google.protobuf.Int32Value` |
| `.protobuf.Scout` | `message` | `#1 target:.protobuf.Scout.Target`, `#2 targetId:string` |
| `.protobuf.Scout.Target` | `enum` | `#0 DEFAULT:.protobuf.Scout.Target`, `#1 BASE:.protobuf.Scout.Target`, `#2 BUILDING:.protobuf.Scout.Target`, `#3 ARMY:.protobuf.Scout.Target`, `#4 ALLIANCE_CITY:.protobuf.Scout.Target`, `#5 DESERT:.protobuf.Scout.Targ... |
| `.protobuf.ScoutActResource` | `message` | `#1 buildId:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 rewardType:.google.protobuf.Int32Value`, `#4 plunderRewardNum:.google.protobuf.Int64Value`, `#5 index:.google.protobuf.Int32Value` |
| `.protobuf.ScoutAllianceBuild` | `message` | `#1 buildId:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 abbr:string`, `#4 name:string`, `#5 level:.google.protobuf.Int32Value` |
| `.protobuf.ScoutAllianceBuildWall` | `message` | `#1 hp:.google.protobuf.Int32Value`, `#2 hpMax:.google.protobuf.Int32Value`, `#3 visible:.google.protobuf.Int32Value` |
| `.protobuf.ScoutAllianceCity` | `message` | `#1 city_id:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 abbr:string`, `#4 name:string`, `#5 cityName:string` |
| `.protobuf.ScoutAllianceCityWall` | `message` | `#1 hp:.google.protobuf.Int32Value`, `#2 hpMax:.google.protobuf.Int32Value`, `#3 visible:.google.protobuf.Int32Value`, `#4 waitMemberCount:.google.protobuf.Int32Value` |
| `.protobuf.ScoutArmy` | `message` | `#1 target:.protobuf.ScoutTargetArmyUnit`, `#2 help:.protobuf.ScoutHelpArmy`, `#3 targetTotal:.protobuf.ScoutTargetArmyTotal` |
| `.protobuf.ScoutCrossThroneBuilding` | `message` | `#1 buildId:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 abbr:string`, `#4 name:string` |
| `.protobuf.ScoutDragonBuilding` | `message` | `#1 buildId:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 abbr:string`, `#4 name:string` |
| `.protobuf.ScoutFormation` | `message` | `#1 soldierTotal:.google.protobuf.Int32Value`, `#2 hero:.protobuf.ScoutHero`, `#3 soldier:.protobuf.ScoutSoldier`, `#4 specialUnitType:.google.protobuf.Int32Value` |
| `.protobuf.ScoutHelpArmy` | `message` | `#1 formation:.protobuf.ScoutHelpArmyUnit`, `#2 visible:.google.protobuf.Int32Value` |
| `.protobuf.ScoutHelpArmyUnit` | `message` | `#1 formation:.protobuf.ScoutFormation`, `#2 user:.protobuf.User`, `#3 teamUuid:.google.protobuf.Int64Value`, `#4 collectValue:.google.protobuf.Int32Value` |
| `.protobuf.ScoutHero` | `message` | `#1 heroId:.google.protobuf.Int32Value`, `#2 heroLevel:.google.protobuf.Int32Value`, `#3 heroQuality:.google.protobuf.Int32Value`, `#4 heroRankLevel:.google.protobuf.Int32Value`, `#5 camp:.google.protobuf.Int32Value`,... |
| `.protobuf.ScoutReport` | `message` | `#1 targetUser:.protobuf.ScoutUser`, `#2 userWall:.protobuf.ScoutUserWall`, `#3 resource:.protobuf.ScoutResource`, `#4 army:.protobuf.ScoutArmy`, `#5 tower:.protobuf.ScoutTower`, `#6 targetAllianceCity:.protobuf.Scout... |
| `.protobuf.ScoutReport.TargetType` | `enum` | `#0 DEFAULT:.protobuf.ScoutReport.TargetType`, `#1 MAIN_BUILDING:.protobuf.ScoutReport.TargetType`, `#2 STORAGE:.protobuf.ScoutReport.TargetType`, `#3 COLLECT_BUILDING:.protobuf.ScoutReport.TargetType`, `#4 TOWER:.pro... |
| `.protobuf.ScoutResource` | `message` | `#1 data:.protobuf.Resource`, `#2 visible:.google.protobuf.Int32Value`, `#3 plunderResRate:.google.protobuf.Int32Value`, `#4 resourceItemCount:.google.protobuf.Int32Value` |
| `.protobuf.ScoutSoldier` | `message` | `#1 armsId:string`, `#2 type:.google.protobuf.Int32Value`, `#3 total:.google.protobuf.Int32Value` |
| `.protobuf.ScoutTargetArmyTotal` | `message` | `#1 visible:.google.protobuf.Int32Value`, `#2 total:.google.protobuf.Int64Value` |
| `.protobuf.ScoutTargetArmyUnit` | `message` | `#1 formation:.protobuf.ScoutFormation`, `#2 visible:.google.protobuf.Int32Value` |
| `.protobuf.ScoutTower` | `message` | `#1 tower:.protobuf.ScoutTowerUnit`, `#2 visible:.google.protobuf.Int32Value` |
| `.protobuf.ScoutTowerUnit` | `message` | `#1 level:.google.protobuf.Int32Value`, `#2 attack:.google.protobuf.Int32Value`, `#3 hp:.google.protobuf.Int32Value`, `#4 hpMax:.google.protobuf.Int32Value` |
| `.protobuf.ScoutTradePost` | `message` | `#1 buildingId:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 abbr:string`, `#4 name:string` |
| `.protobuf.ScoutUser` | `message` | `#1 abbr:string`, `#2 name:string`, `#3 pic:string`, `#4 picVer:.google.protobuf.Int32Value`, `#5 point:.protobuf.PointInfo`, `#6 uid:string`, `#7 careerType:int32`, `#8 careerLv:int32`, `#9 headSkinId:int32`, `#10 he... |
| `.protobuf.ScoutUserWall` | `message` | `#1 hp:.google.protobuf.Int32Value`, `#2 hpMax:.google.protobuf.Int32Value`, `#3 visible:.google.protobuf.Int32Value`, `#4 buildingId:string`, `#5 buildingLevel:.google.protobuf.Int32Value`, `#6 stateId:.google.protob... |
| `.protobuf.ScoutVisible` | `enum` | `#0 DEFAULT:.protobuf.ScoutVisible`, `#1 ENABLE:.protobuf.ScoutVisible`, `#2 DISABLE:.protobuf.ScoutVisible`, `#3 NOT_MATCH:.protobuf.ScoutVisible`, `#4 ENABLE_EMPTY:.protobuf.ScoutVisible` |
| `.protobuf.ScoutVolcanoBuilding` | `message` | `#1 buildId:.google.protobuf.Int32Value`, `#2 point:.protobuf.PointInfo`, `#3 abbr:string`, `#4 name:string` |
| `.protobuf.SimpleCombatUnit` | `message` | `#1 initHealth:int32`, `#2 health:int32`, `#3 uuid:int64`, `#4 uid:string`, `#6 longInitHealth:int64`, `#7 longHealth:int64` |
| `.protobuf.SimpleCombatUnitPushObj` | `message` | `#1 armyInfo:.protobuf.SimpleCombatUnit`, `#2 type:int32`, `#3 topUuid:int64`, `#4 topPointId:int32`, `#5 specialArmyType:int32` |
| `.protobuf.SimpleSelfArmyInfo` | `message` | `#1 armyInfo:.protobuf.SimpleCombatUnitPushObj`, `#2 targetInfo:.protobuf.SimpleCombatUnitPushObj`, `#3 hurt:int32`, `#4 heal:int32`, `#5 shieldHurt:int32`, `#6 shield:int32`, `#7 anger:int32`, `#8 statusInfo:.protobu... |
| `.protobuf.SkillAttrInfo` | `message` | `#1 skillType:int32`, `#2 skillId:int32`, `#3 skillPower:double`, `#4 heroId:int32` |
| `.protobuf.Skin` | `message` | `#1 skinId:int32`, `#2 type:int32`, `#3 skinET:int64`, `#4 sortLocal:int64` |
| `.protobuf.SoldierProto` | `message` | `#1 armsId:string`, `#2 type:int32`, `#3 total:int32`, `#4 lost:int32`, `#5 wounded:int32`, `#6 injured:int32`, `#7 dead:int32`, `#8 cure:int32` |
| `.protobuf.SuitInfoProto` | `message` | `#1 carIndex:int32`, `#2 suitType:int32`, `#3 equipInfos:.protobuf.EquipInfoProto`, `#4 skillInfos:.protobuf.HeroSkillInfoProto` |
| `.protobuf.TankChipInfo` | `message` | `#1 id:int32`, `#2 rank:int32`, `#3 grade:int32`, `#4 slot:int32`, `#5 quality:int32`, `#6 skill:int32`, `#7 skillLevel:int32` |
| `.protobuf.TankComponInfo` | `message` | `#1 id:int32`, `#2 level:int32`, `#3 quality:int32`, `#4 pos:int32` |
| `.protobuf.TankNewInfo` | `message` | `#1 tankId:int32`, `#2 tankLv:int32`, `#3 tankDecoration:int32`, `#4 tankSkill:int32`, `#5 tankBarellSkill:int32`, `#6 power:int32`, `#7 compons:.protobuf.TankComponInfo`, `#8 chips:.protobuf.TankChipInfo` |
| `.protobuf.TankNewInfoProto` | `message` | `#1 tankId:int32`, `#2 tankLv:int32`, `#3 tankDecoration:int32`, `#4 tankSkill:int32`, `#5 tankBarellSkill:int32`, `#6 power:int32`, `#7 compons:.protobuf.TankComponInfo`, `#8 chips:.protobuf.TankChipInfo`, `#9 tankPo... |
| `.protobuf.TextWithParams` | `message` | `#1 text:string`, `#2 params:.protobuf.Message` |
| `.protobuf.ThanksStarInfo` | `message` | `#1 activityId:int32`, `#2 starLevel:int32` |
| `.protobuf.TradePostArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 buildingId:int32` |
| `.protobuf.Treasure` | `message` | `#1 uuid:int64`, `#2 configId:int32`, `#3 ownerUid:string`, `#4 name:string`, `#5 allianceAbbr:string`, `#6 startTime:int64`, `#7 rewardTime:int64`, `#8 endTime:int64`, `#9 hasRewardNums:int32`, `#10 rewarduids:string... |
| `.protobuf.UnitAttrInfo` | `message` | `#1 uuid:int64`, `#4 atkInfo:.protobuf.ArmyAttrInfo`, `#5 defInfo:.protobuf.ArmyAttrInfo`, `#6 skillInfo:.protobuf.SkillAttrInfo` |
| `.protobuf.UnitEffect` | `message` | `#1 effectId:int32`, `#2 value:float` |
| `.protobuf.UnitEffectReason` | `message` | `#1 effectId:int32`, `#2 reasons:.protobuf.EffectReason` |
| `.protobuf.Url` | `message` | `#1 href:string`, `#2 text:string` |
| `.protobuf.User` | `message` | `#1 abbr:string`, `#2 name:string`, `#3 uid:string`, `#4 pic:string`, `#5 picVer:int32`, `#6 headSkinId:int32`, `#7 headSkinET:int64` |
| `.protobuf.UserInfo` | `message` | `#1 uid:string`, `#2 name:string`, `#3 pic:string`, `#4 picVer:.google.protobuf.Int32Value` |
| `.protobuf.VolcanoBuildArmyResult` | `message` | `#1 base:.protobuf.ArmyResultBase`, `#2 buildId:int32` |
| `.protobuf.VolcanoBuilding` | `message` | `#1 id:int32` |
| `.protobuf.VolcanoBuildingPointInfo` | `message` | `#1 uuid:int64`, `#2 buildId:int32`, `#3 alAbbr:string`, `#4 allianceId:string`, `#5 openTime:int64`, `#6 createTime:int64`, `#7 uid:string`, `#8 pic:string`, `#9 picVer:int32`, `#10 headSkinId:int32`, `#11 headSkinET... |
| `.protobuf.WorldAllAllianceCityInfo` | `message` | `#1 infoes:.protobuf.AllianceCityOccupyInfo` |
| `.protobuf.WorldAllianceBuild` | `message` | `#1 id:int32`, `#2 level:int32` |
| `.protobuf.WorldAllianceCity` | `message` | `#1 id:int32`, `#2 cityName:string` |
| `.protobuf.WorldAllianceFortress` | `message` | `#1 id:int32` |
| `.protobuf.WorldBanquetTable` | `message` | `#1 tableId:int32` |
| `.protobuf.WorldBanquetTableEatInfo` | `message` | `#1 uid:string` |
| `.protobuf.WorldBanquetTableInfo` | `message` | `#1 tableId:int32`, `#2 eatNum:int32`, `#3 vanishTime:int64`, `#4 alAbbr:string`, `#5 allianceId:string`, `#6 alName:string`, `#7 isAdd:bool`, `#8 ownerUid:string`, `#9 pic:string`, `#10 picVer:int32`, `#11 name:string` |
| `.protobuf.WorldCityRankInfo` | `message` | `#1 playerInfo:.protobuf.ReportPlayerInfo`, `#2 rewardInfo:.protobuf.RewardInfo`, `#3 scord:int64`, `#4 rank:int32` |
| `.protobuf.WorldCityRankMail` | `message` | `#1 time:int64`, `#2 type:int32`, `#3 cityId:int32`, `#4 cityName:string`, `#5 rankInfos:.protobuf.WorldCityRankInfo` |
| `.protobuf.WorldDesert` | `message` | `#1 id:int32`, `#2 pointId:int32` |
| `.protobuf.WorldFishMissionInfo` | `message` | `#1 caveId:int32`, `#2 startTime:int64`, `#3 finishTime:int64`, `#4 allianceId:string`, `#5 abbr:string`, `#6 ownerUid:string`, `#7 name:string`, `#8 serverId:int32`, `#9 startPoint:int32` |
| `.protobuf.WorldIceCave` | `message` | `#1 id:int32` |
| `.protobuf.WorldIceCaveInfo` | `message` | `#1 caveId:int32`, `#2 state:int32`, `#3 startTime:int64`, `#4 endTime:int64`, `#5 allianceId:string`, `#6 abbr:string`, `#7 ownerUid:string`, `#8 pic:string`, `#9 picVer:int32`, `#10 headSkinId:int32`, `#11 headSkinE... |
| `.protobuf.WorldPointInfo` | `message` | `#1 id:int32`, `#2 pointType:int32`, `#3 buildInfo:.protobuf.BuildInfo`, `#4 roadInfo:.protobuf.RoadInfo`, `#5 collectResourceInfo:.protobuf.CollectResourceInfo`, `#6 resourceInfo:.protobuf.ResourceInfo`, `#7 exploreP... |
| `.protobuf.WorldPointInfoBatch` | `message` | `#1 infos:bytes` |
| `.protobuf.WorldPointMonster` | `message` | `#1 uuid:int64`, `#2 monsterId:int32`, `#3 isBoss:bool`, `#4 type:int32`, `#5 diffPoint:string`, `#6 refreshTime:int32`, `#7 belongUid:string`, `#8 monsterExtraInfo:bytes`, `#9 monsterExtraInfoType:int32` |
| `.protobuf.WorldResource` | `message` | `#1 id:int32` |
| `.protobuf.WorldRewardPacketInfo` | `message` | `#1 uuid:int64`, `#2 packetId:int32`, `#3 initNum:int32`, `#4 collectUsers:string`, `#5 expireTime:int64`, `#6 attachInfo:string` |
| `.protobuf.WorldRuinPointInfo` | `message` | `#1 uuid:int64`, `#2 size:int32`, `#3 type:int32`, `#4 param:string`, `#5 startTime:int32`, `#6 endTime:int32` |
| `.protobuf.WorldTradePost` | `message` | `#1 id:int32` |
| `.protobuf.WorldTradePostInfo` | `message` | `#1 buildingId:int32`, `#2 state:int32`, `#3 startTime:int64`, `#4 endTime:int64`, `#5 allainceId:string`, `#6 abbr:string`, `#7 ownerUid:string`, `#8 pic:string`, `#9 picVer:int32`, `#10 headSkinId:int32`, `#11 headS... |
| `.protobuf.WorldUserBuild` | `message` | `#1 id:int32`, `#2 level:int32` |

## 4. `Util.GoToUtil` Complete Navigation & Jump Router (142 Methods)

| `GoToUtil` Method | Params | Opens `UIWindowNames` | Target `BuildingTypes` | Calls `DataCenter.*` | Sends `MsgDefines` |
|---|---:|---|---|---|---|
| `CloseAllWindows` | 0 | - | - | - | - |
| `DoCollectedGarbage` | 0 | - | - | SV_MapItemInfoManager, BattleLevel | - |
| `DoGoLandLock` | 2 | - | - | LandLockManager | - |
| `DoGoTile` | 2 | - | - | LandLockManager | - |
| `FindMonster` | 1 | - | - | - | FindMonster |
| `GetBuildState` | 1 | - | - | BuildManager | - |
| `GetSourceByResourceItem` | 1 | - | - | ResourceItemDataManager | - |
| `GoActWindow` | 3 | UIActivityCenterTable | - | FoodFestivalManager | - |
| `GoActWindowByType` | 2 | UIActivityCenterTable | - | ActivityListDataManager | - |
| `GoAllianceBossByVS` | 0 | UISearch | - | MonsterManager | - |
| `GoAttackMonster` | 0 | - | - | WorldMarchDataManager | - |
| `GoBagPackUseItem` | 1 | - | - | - | - |
| `GoBarracks` | 0 | - | - | ArmyManager | - |
| `GoBarracksByVS` | 0 | - | - | BuildManager | - |
| `GoBuildOpenUpgrade` | 2 | UINewBuildUpgrade | - | BuildManager | - |
| `GoBusinessCenterWindow` | 0 | - | FUN_BUILD_BUSINESS_CENTER | BuildManager | - |
| `GoCheckBuild` | 2 | - | - | - | - |
| `GoCityCollect` | 1 | - | - | CollectResourceTemplateManager | - |
| `GoConnectBuild` | 1 | - | - | BuildManager | - |
| `GoDailyUI` | 0 | - | - | - | - |
| `GoDispatchTaskWindow` | 0 | - | - | ActivityListDataManager | - |
| `GoEnergy` | 1 | - | - | - | - |
| `GoFactory` | 0 | - | FUN_BUILD_FOODSHOP | FactoryDataManager | - |
| `GoFactoryWork` | 2 | UIFactory | - | FactoryDataManager, HasBuildByIdAndLevel, ArrowManager | - |
| `GoFlint` | 2 | - | - | - | FindDesertPoint |
| `GoFormation` | 1 | - | - | - | - |
| `GoGarageUpgrade` | 1 | - | - | GarageRefitManager | - |
| `GoGarageUpgradeNew` | 1 | UIAircraftMain | GARAGEREFIT_DRONE | BuildManager | - |
| `GoGarbage` | 1 | - | - | - | GetGarbageInfo |
| `GoGiftMall` | 0 | UIGiftPackage | - | - | - |
| `GoHeroBag` | 0 | UIHeroBag | APS_BUILD_PUB | BuildManager | - |
| `GoHeroSkill` | 3 | UIHeroInfo | - | HeroDataManager | - |
| `GoHeroStation` | 1 | - | - | BuildManager | - |
| `GoHeroStationScores` | 1 | - | - | BuildManager | - |
| `GoHeroTrust` | 1 | - | - | - | - |
| `GoHospital` | 1 | UIHospital | - | BuildManager | - |
| `GoLandLockById` | 2 | - | - | LandLockManager | - |
| `GoLandPve` | 1 | - | - | BattleLevel | - |
| `GoLockMonster` | 1 | UIWorldPoint | - | MonsterLockDataManager, MonsterLockBubbleManager | - |
| `GoNewsletterView` | 1 | UILoveNewsletter | - | LoveNewsletterDataManager | - |
| `GoNewsletterViewToStory` | 3 | UILoveNewsletter | - | LoveNewsletterDataManager | - |
| `GoPveLevel` | 1 | - | - | - | - |
| `GoRadarProbe` | 3 | UIDetectEvent | FUN_BUILD_RADAR_CENTER | BuildManager, RadarCenterDataManager | - |
| `GoRadarView` | 0 | UIDetectEvent | FUN_BUILD_RADAR_CENTER | BuildManager | - |
| `GoSearchEnemy` | 1 | - | - | - | FindEnemyPoint |
| `GoSeasonDesertMaxLv` | 1 | - | - | WorldPointManager, DesertDataManager | - |
| `GoSeasonManager` | 1 | - | - | DesertDataManager | - |
| `GoSelfDesert` | 1 | UIWorldPoint | - | DesertDataManager, ArrowManager | - |
| `GoToByQuestId` | 2 | UIHeroList, UIAllianceHelp, UIChatNew, UISearch, UIA... | APS_BUILD_PASTURE_OSTRICH | BuildManager, MomentManager, ArrowManager | - |
| `GoToByVSId` | 1 | UIBuildQueueList, UIHeroList, UISearch | - | ArrowManager, ItemData, MonsterManager | - |
| `GoToCareerSelect` | 1 | - | - | - | - |
| `GoToCityBuildByQuest` | 3 | - | - | BuildManager | - |
| `GoToGarageRefit` | 1 | UIAircraftMain | - | GarageRefitManager | - |
| `GoToMainCityArea` | 1 | - | - | BattleLevel | - |
| `GoToMonthCard` | 1 | UIGiftPackage | - | - | - |
| `GoToPlayerCareer` | 0 | - | - | - | - |
| `GoToPlayerLevel` | 1 | - | - | PlayerLevelManager | - |
| `GoToPoliceInsigniaBuild` | 1 | - | - | BuildPoliceInsigniaManager | - |
| `GoToPoliceInsigniaBuildAndClickUp` | 2 | - | - | BuildManager, BuildPoliceInsigniaManager | - |
| `GoToPoliceInsigniaBuildAndLevelUp` | 1 | - | - | BuildPoliceInsigniaManager | - |
| `GoToRandomCanUpgradeBuild` | 2 | - | - | BuildManager | - |
| `GoToStorageShop` | 2 | UIStorageShopMain | - | - | - |
| `GoToTalkTaskEventBubble` | 1 | - | - | BuildManager, BuildBubbleManager | - |
| `GoTriggerPve` | 1 | - | - | - | - |
| `GoUnlockedTile` | 0 | - | - | LandLockManager | - |
| `GoWeeklyPackageNew` | 1 | - | - | - | - |
| `GoWorldBuildList` | 1 | UIWorldBuildList | - | BuildManager | - |
| `GoWorldCity` | 1 | - | - | AllianceCityTemplateManager | - |
| `GoWorldToSearch` | 0 | - | - | - | - |
| `GotoAllianceIntroView` | 0 | UIAllianceIntro | - | - | - |
| `GotoAlliancePersonalWarIntelligence` | 0 | UIAllianceWarIntelligence | - | - | - |
| `GotoAllianceTeam` | 1 | UIAllianceWarMainTable | - | - | - |
| `GotoBossMonsterBetweenLv` | 3 | - | - | WorldMarchDataManager | - |
| `GotoBuildListByBuildId` | 1 | UIBuildList | - | BuildManager | - |
| `GotoBuildListRobotByRobotId` | 1 | UIBuildList | - | - | - |
| `GotoBuildRoad` | 3 | - | - | - | - |
| `GotoCarBattlePve` | 2 | UIActivityCenterTable | - | LandingOperationsDataManager | - |
| `GotoCarChipActivity` | 0 | UIActivityCenterTable | - | CarChipActivityManager | - |
| `GotoCarComponActivity` | 0 | UIActivityCenterTable | - | CarComponActivityManager | - |
| `GotoCity` | 0 | - | - | CityCameraManager | - |
| `GotoCityByBarracksState` | 1 | UITrain | - | ArmyManager | - |
| `GotoCityByBuildId` | 3 | - | GARAGEREFIT_DRONE | GarageRefitManager | - |
| `GotoCityByBuildUuid` | 4 | MainUI_SU, UINewBuildUpgrade | FUN_BUILD_RADAR_CENTER, FUN_BUILD_MAIN | BuildManager, BuildTemplateManager, BuildPoliceInsig... | - |
| `GotoCityByTriggerId` | 1 | - | - | BattleLevel | - |
| `GotoCityPos` | 4 | - | - | - | - |
| `GotoCityTroopAndPointToGarbage` | 0 | - | - | WorldMarchDataManager | - |
| `GotoColdStorage` | 1 | - | APS_BUILD_FARM_FIELD | BattleLevel, ResourceItemDataManager | - |
| `GotoCrossWorm` | 0 | - | WORM_HOLE_CROSS | BuildManager | - |
| `GotoDragonPos` | 7 | - | - | - | - |
| `GotoFarm` | 1 | - | - | - | - |
| `GotoFarmGet` | 3 | - | - | - | - |
| `GotoFastBuildList` | 1 | UIMain | - | - | - |
| `GotoGiftPackView` | 2 | UIScrollPack | - | - | - |
| `GotoGuluBox` | 1 | - | - | CollectRewardDataManager | - |
| `GotoHeroEquipForgeMain` | 0 | UIHeroEquipForgeMain | - | HeroEquipManager | - |
| `GotoHeroSpEquioView` | 1 | UIHeroSPEquip | - | HeroSPEquipManager | - |
| `GotoIceCaveRecordWindow` | 2 | UISeasonIceCaveRecord | - | - | - |
| `GotoLandLock` | 1 | - | - | - | - |
| `GotoMainBuildPos` | 1 | - | FUN_BUILD_MAIN | BuildManager | - |
| `GotoMonsterReward` | 0 | UISearch | - | CollectRewardDataManager, MonsterManager | - |
| `GotoOpenBuildQueueWindow` | 1 | UIBuildQueueList | - | BuildQueueManager | - |
| `GotoOpenItemTipWindow` | 1 | UIItemChatTitleTip | - | ItemTemplateManager | - |
| `GotoOpenView` | 1 | UISearch | - | - | - |
| `GotoPasture` | 2 | - | - | - | - |
| `GotoPastureByUuid` | 1 | - | - | - | - |
| `GotoPay` | 0 | UIGiftPackage | - | MonthCardNewManager | - |
| `GotoPayTips` | 0 | - | - | - | - |
| `GotoPos` | 9 | - | - | AccountManager, BattleLevel | - |
| `GotoPushPveLevel` | 0 | UIJeepAdventureMain, UIStoryHangup | - | LandLockManager | - |
| `GotoQuestNew` | 1 | UIHeroRecruit, UISearch | - | GuideManager, ChapterTaskManager | - |
| `GotoRedEquipForge` | 1 | - | - | HeroEquipManager | - |
| `GotoRedEquipmentActivity` | 0 | UIActivityCenterTable | - | RedEquipmentActivityManager | - |
| `GotoResourceBuild` | 0 | - | - | BuildManager | - |
| `GotoScience` | 6 | - | FUN_BUILD_SCIENE | BuildManager | - |
| `GotoScienceByVS` | 0 | UIScienceTab | FUN_BUILD_SCIENE | BuildManager | - |
| `GotoSeasonGlorySelectMemberWindow` | 0 | UISeasonGlorySelectMember | - | - | - |
| `GotoSeasonGradingWindow` | 0 | UISeasonGrading | - | - | - |
| `GotoSeasonGroundManageWindow` | 2 | UISeasonGroundManage | - | - | - |
| `GotoSeasonMainWindow` | 2 | UIActivityCenterTable | - | - | - |
| `GotoSeasonRewardAllotWindow` | 0 | UISeasonGloryRewardAllot | - | - | - |
| `GotoSeasonRewardWindow` | 0 | UISeasonGloryReward | - | - | - |
| `GotoSeasonWeekCardWindow` | 0 | UIActivityCenterTable | - | ActivityListDataManager | - |
| `GotoSkinShopView` | 2 | UISkinShop | - | - | - |
| `GotoSteelAndRedEquipActivity` | 0 | UIActivityCenterTable | - | CarChipActivityManager | - |
| `GotoTradePostStoreWindow` | 3 | UISeasonTradePostStore | - | ActTradePostManager | - |
| `GotoTrainSolider` | 1 | UITrain | FUN_BUILD_CAR_BARRACK | BuildManager | - |
| `GotoUISeasonGloryGroup` | 0 | UISeasonGloryGroup | - | - | - |
| `GotoUpgradeBuildRecommend` | 0 | - | - | BuildManager | - |
| `GotoWorldBuildAndOpenUI` | 5 | UIWorldTileUI | FUN_BUILD_MAIN, FUN_BUILD_BUSINESS_CENTER | BuildTemplateManager, ArrowManager | - |
| `GotoWorldPointId` | 1 | - | - | - | - |
| `GotoWorldPos` | 7 | - | - | - | - |
| `GotoWorldResource` | 1 | - | FUN_BUILD_MAIN | BuildManager | FindResourcePoint |
| `HeroStar` | 0 | - | - | - | - |
| `LookAtFirstCanUnlockLandLockByPve` | 1 | - | - | LandLockManager | - |
| `MoveToWorldPoint` | 4 | - | - | - | - |
| `MoveToWorldPointAndOpen` | 8 | - | - | WorldGotoManager | - |
| `MoveToWorldTroopAndOpen` | 2 | - | - | WorldGotoManager | - |
| `OpenFireMissileView` | 2 | UIMainMapLaunch | - | GloryManager | - |
| `OpenInCity` | 2 | - | FUN_BUILD_MAIN | BuildManager | - |
| `OpenSciencePanel` | 6 | UIScience | - | - | - |
| `OpenScienceTabPanel` | 3 | UIScienceTab | - | CreditManager | - |
| `__tostring` | 1 | - | - | - | - |

## 5. Chat WebSocket (`WebMessage` - 21 Modules) & Mail V4 Protocol (3 Modules)

| Protocol Module | Methods (Params) |
|---|---|
| `Net.Msgs.LoginThirdPartWeb.LoginThirdPartWebMessage` | `HandleMessage(2)`, `OnCreate(2)` |
| `Slg.Chat_SLG.WebMessage.Push.PushChatMessage` | `HandleMessage(2)`, `IsProjectPostTypeAllowed(2)` |
| `Slg.Chat_SLG.WebMessage.SetUserInfoCommand` | `OnCreate(2)` |
| `Slg.DataCenter.MailDataV4.Protocol.MailProtocolRouter` | `GetV4Handler(1)`, `Init(6)`, `IsRequestFailed(1)`, `IsRequestOver(1)`, `IsUseNewSystem(1)`, `MarkRequestFailed(1)`, `MarkRequestOver(1)`, `RequestDetail(3)`... |
| `Slg.DataCenter.MailDataV4.Protocol.MailPushHandler` | `FlushQueue(1)`, `GetQueueCount(1)`, `IsInitComplete(1)`, `OnPushReceived(2)`, `SetDetailResolver(2)`, `SetGMMailLogger(2)`, `SetInitComplete(2)`, `SetRedDot... |
| `Slg.DataCenter.MailDataV4.Protocol.MailV4Handler` | `Destroy(1)`, `OnDetailResponse(2)`, `OnFirstScreenResponse(2)`, `OnGetNewMailsV4(2)`, `OnMoreResponse(2)`, `RequestDetail(3)`, `RequestFirstScreen(1)`, `Req... |
| `SlgEngine.Chat.WebMessage.ChatRoomGroupListNoticeCommandBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Config.WebSocketBaseMessageBase` | `HandleMessage(2)`, `NewEmpty(2)`, `NewMessage(2)`, `OnCreate(1)`, `OnDestroy(1)` |
| `SlgEngine.Chat.WebMessage.GetCustomRoomListCommandBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.GetHistoryMsgsCommandBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.JoinRoomMultiCommandBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentFollowGiftMessageBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentFollowListMessageBase` | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentNoticeLastMessageBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentSetInfoMessageBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentStatMessageBase` | `HandleMessage(2)`, `OnCreate(3)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentUserBlackListMessageBase` | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Moment.MomentUserBlockListMessageBase` | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.Push.PushChatMessageBase` | `HandleMessage(2)`, `IsProjectPostTypeAllowed(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Push.PushChatUpMessageBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.Push.PushLoginSuccessBase` | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.SetSwitchFlagCommandBase` | `HandleMessage(2)`, `OnCreate(2)` |
| `SlgEngine.Chat.WebMessage.SetUserInfo2CommandBase` | `HandleMessage(2)`, `OnCreate(1)` |
| `SlgEngine.Chat.WebMessage.SetUserInfoCommandBase` | `HandleMessage(2)`, `OnCreate(2)` |

## 6. DataCenter & Singleton End-to-End Call Graph (375 Managers, 14,020 Methods)

> Query any specific method's exact outgoing links with `python megamind/megamind_query.py callgraph <query>`.

| Manager / Singleton | Linked / Total Methods | Outgoing `MsgDefines` / `ChatMsg` | `EventId` Bus | Opens `UIWindowNames` | Reads `TableName` | Cross-DC Deps |
|---|---:|---|---|---|---|---|
| `DataCenter.AccountListManager` | 11/12 | - | - | - | - | AccountData |
| `DataCenter.AccountManager` | 36/91 | MsgDefines.AccountLoginNewGlobal, MsgDefines.ChangeMail, MsgDe... | AccountBindEvent, AccountBindOKEvent, AccountChangeMailEv... | UIAccountVerify, UIBindSendMail, UIGameCenterChangeB... | - | BuildManager, PayManager |
| `DataCenter.AchievementManager` | 2/45 | MsgDefines.AchievementInfo, MsgDefines.AchievementRank | - | - | - | - |
| `DataCenter.ActBlackKnightManager` | 25/52 | MsgDefines.GetRank, MsgDefines.MonsterSiegeActivityInfo, MsgDe... | BlackKnightAllianceMemberInfoUpdated, BlackKnightRank, Bl... | UIBlackKnightComing | - | ActivityListDataManager, AllianceBaseDataManager, SeasonC... |
| `DataCenter.ActBloodMoonManager` | 52/118 | MsgDefines.BloodMoonRankGet, MsgDefines.FindBloodMoonMonster, ... | OnEnterWorld, RefreshBloodMoonInfo, RefreshBloodMoonRank,... | UIActivityCenterTable, UISearch | TableName.GoodsTab, TableName.SeasonDonateBuilding, ... | ActivityListDataManager, GovernmentManager, MonsterTempla... |
| `DataCenter.ActBossDataManager` | 11/28 | MsgDefines.TaskRewardInfo, MsgDefines.UserGetActBossMarch | RefreshPersonalTaskRewards | - | - | ActivityListDataManager, BuildManager, QuestTemplateManag... |
| `DataCenter.ActChampionBattleManager` | 111/112 | MsgDefines.ACT_CHAMPIONBATTLE_BET, MsgDefines.ACT_CHAMPIONBATT... | ChampionBattleBetMatchRefresh, ChampionBattleBetRecordRef... | ChampionServerRewardGet, LFChampionBattleFight | - | ActivityListDataManager, AllianceCompeteDataManager, Buil... |
| `DataCenter.ActDinosaurBossDataManager` | 6/26 | - | - | - | TableName.DinosaurBoss | ActivityListDataManager, RewardManager |
| `DataCenter.ActDispatchTaskDataManager` | 29/65 | MsgDefines.DispatchGetAllianceTasks, MsgDefines.DispatchGetLog... | BuildBoxOpenFinish, DispatchMissionStatusResponse, Dispat... | UIDispatchRewardGet | TableName.ActivityPanel, TableName.LwDispatchSetting... | ActDispatchTaskFakeMarchManager, ActivityListDataManager,... |
| `DataCenter.ActDragonManager` | 76/176 | MsgDefines.DragonActionRecord, MsgDefines.DragonActivityInfo, ... | CheckDragonMoveCity, DragonBattleHistory, DragonBattleTim... | UIAlCompeteBarrage, UIArrow, UIDragonHistoryScore, U... | - | ActivityListDataManager, AllianceBaseDataManager, ArmyFor... |
| `DataCenter.ActDrakeBossManager` | 8/26 | MsgDefines.GetUserDrakeBoss, MsgDefines.ItemUse | RefreshActivityRedDot, RefreshDrakeBoss | UIDrakeBossUseItem | - | ActivityListDataManager, HeroDataManager, ItemData, ItemT... |
| `DataCenter.ActFirstChargeData` | 6/14 | MsgDefines.GetFirstChargeInfo, MsgDefines.ReceiveFirstChargeDa... | PlayerChangeHeadRedPot, RefreshWelfareRedDot | UIFirstCharge | - | RewardManager |
| `DataCenter.ActGiftBoxData` | 7/29 | - | ActGiftBoxDrawReward, ActGiftBoxGetInfo, ActGiftBoxLotter... | - | - | RewardManager |
| `DataCenter.ActIceCaveManager` | 34/67 | MsgDefines.GetIceCaveAllianceRankInfo, MsgDefines.GetIceCaveEv... | RefreshFishingNum, RefreshIceCaveAllianceRank, RefreshIce... | UIFishRewardGet, UIFishingCatalogUnlock | TableName.IceCaveInfo | FishingCatalogDataManager, ItemData, QueueDataManager, Re... |
| `DataCenter.ActLuckyRollInfo` | 6/34 | - | self | - | - | ActivityListDataManager, ItemData, RewardManager |
| `DataCenter.ActMonsterTowerData` | 29/74 | MsgDefines.GetChallengeActInfo | ActMonTowerBossKilled, ActMonTowerCallHelp, ActMonTowerCh... | UIChatNew, UIMonsterTowerComing | TableName.ActivityMonsterBoss | ActivityListDataManager, AllianceBaseDataManager, RewardM... |
| `DataCenter.ActRoamingBossManager` | 24/68 | MsgDefines.GetWanderBossRecord, MsgDefines.GetWanderDmgRank, M... | OnTalkToAnimalReward, RoamingBossGeTBossInfo, RoamingBoss... | UIDetectNpcDinosaurRescue, UIPositionShare | TableName.Monster, TableName.RoamingBossRewardShow | ActivityListDataManager, BuildManager, FrozenLandDataMana... |
| `DataCenter.ActTimeCompeDataManager` | 10/26 | MsgDefines.TimeCompetitionRank | LWLandLockFinish, RefreshCompeRankData | UIGiftPackageRewardGet | TableName.FakePlayer | LandLockManager, RewardManager |
| `DataCenter.ActTradePostManager` | 31/71 | MsgDefines.GetTradeAllianceRankInfo, MsgDefines.GetTradeCityRa... | CheckDayNightState, RefreshTradeAllianceRank, RefreshTrad... | UISeasonTradePostStore | TableName.SeasonGroup, TableName.TradePost, TableNam... | ActivityListDataManager, NightFallManager, SeasonDataMana... |
| `DataCenter.ActivityALVSDonateSoldierMan...` | 29/60 | MsgDefines.ALVSDonateArmyDeclareWar, MsgDefines.ALVSDonateArmy... | ALVSDeclareAllianceListReturn, ALVSDonateArmyBattleInfoRe... | - | - | ActivityListDataManager, RewardManager |
| `DataCenter.ActivityController` | 5/7 | MsgDefines.AcceptPersonalReward, MsgDefines.AcceptPersonalRewa... | - | - | - | ActivityListDataManager |
| `DataCenter.ActivityDonateSoldierManager` | 22/47 | MsgDefines.GetDonateArmyActivityInfo, MsgDefines.GetDonateArmy... | DonateSoldier, GetDonateArmyActivityInfo, GetDonateArmySc... | - | - | ActivityListDataManager, AllianceCompeteDataManager, Rewa... |
| `DataCenter.ActivityListDataManager` | 37/96 | MsgDefines.ActivityEventInfoGet, MsgDefines.GetAlBattleDayVsIn... | AllianceCompeteRefreshUIScore, AllianceCumulativeBatchCla... | UINoticeAlCompeteTips, UINoticeEquipTips | TableName.ActivityBarter, TableName.ActivityPanel | ActBossDataManager, ActChampionBattleManager, ActDispatch... |
| `DataCenter.ActivityTipManager` | 10/15 | - | ActivityTipStateUpdate | MainUI_SU, UIActivityTip | TableName.ActivityTip | ActivityListDataManager |
| `DataCenter.AlContributeManager` | 8/33 | MsgDefines.ClaimAlContributeBoxReward, MsgDefines.GetAlContrib... | OnAlContributeBoxStatusChange, OnAlContributeRankInfoUpda... | - | - | ActivityListDataManager, RewardManager |
| `DataCenter.AllianceAlertDataManager` | 6/24 | MsgDefines.GetAllianceAlertInfo | UpdateAlertData | - | - | BuildManager, WorldMarchDataManager |
| `DataCenter.AllianceAnnouncementManager` | 48/49 | MsgDefines.AdvAllianceNotice, MsgDefines.CommentAllianceNotice... | AllianceApplySuccess, ChatAllianceAnnouncementAdd, ChatAl... | UIPositionShare | - | AllianceAnnouncement, AllianceBaseDataManager, LikeManager |
| `DataCenter.AllianceAutoInviteManager` | 5/14 | MsgDefines.AcceptAllianceAutoInvite, MsgDefines.GetAllianceAut... | OnGetNewAllianceAutoInvite | - | - | - |
| `DataCenter.AllianceBaseDataManager` | 95/96 | MsgDefines.AlFlagSpecialItem, MsgDefines.AlMoveInviteGetPoints... | AlWaitMergeStatusChange, AllianceAnnouncementTranslate, A... | UIChat, UICreateSetAlliance, UIJoinAlliance, UIMain | - | ActivityListDataManager, AllianceData, AllianceLeaderMana... |
| `DataCenter.AllianceBossBearManager` | 74/75 | MsgDefines.AllianceBossSelectTimeNew, MsgDefines.GetAllianceBo... | CallAllianceBossBear, GetAllianceBossBearActivityInfo, Ge... | - | - | ActivityListData, ActivityListDataManager, DecorationData... |
| `DataCenter.AllianceBossManager` | 33/100 | MsgDefines.AllianceBossDonate, MsgDefines.AllianceBossSelectTi... | AllianceBossDonate, CallAllianceBoss, GetAllianceBossActi... | - | - | ActivityListDataManager, AllianceBaseDataManager, ItemTem... |
| `DataCenter.AllianceCareerManager` | 6/11 | MsgDefines.SetAllianceCareerPos | - | - | - | AllianceBaseDataManager, AllianceMemberDataManager |
| `DataCenter.AllianceCityLogManager` | 2/12 | MsgDefines.ViewAllianceLog | AllianceCityLogUpdate | - | - | - |
| `DataCenter.AllianceCityTemplateManager` | 3/5 | - | - | - | TableName.WorldCity | ItemTemplateManager, SeasonDataManager |
| `DataCenter.AllianceCityTipManager` | 8/33 | MsgDefines.UserGetActBossMarch | ChangeCameraLod | UIAllianceCityBar | - | ActivityListDataManager, AllianceCityTemplateManager |
| `DataCenter.AllianceDanMuManager` | 6/21 | MsgDefines.SendAlDanMu | AllianceDanMuShowEvent, PushDanMuDataEvent, SceneChanged | UIAlCompeteBarrage | - | ActivityListDataManager, LeagueMatchManager, LoginPopManager |
| `DataCenter.AllianceDissolutionManager` | 42/43 | MsgDefines.AlCancelDismiss, MsgDefines.AlConfirmDismiss, MsgDe... | AllianceDismissStatusChanged, AllianceKickOverLimit, Alli... | - | - | AllianceBaseDataManager, AllianceData |
| `DataCenter.AllianceGiftDataManager` | 21/22 | - | UpdateMainAllianceRedCount | - | - | AllianceData, BuildManager |
| `DataCenter.AllianceHaggleManager` | 9/25 | MsgDefines.AllianceHaggle, MsgDefines.AllianceHaggleBuy, MsgDe... | RefreshActivityRedDot | UIActivityCenterTable | TableName.AllianceHaggle | ActivityListDataManager |
| `DataCenter.AllianceHelpDataManager` | 21/22 | MsgDefines.AlHelpAll, MsgDefines.AlHelpFromAll, MsgDefines.All... | AllianceBuildHelpNew, UpdateMainAllianceRedCount | - | - | AllianceData, AllianceShopDataManager, BuildManager, Mont... |
| `DataCenter.AllianceHelpVirtualMarchManager` | 4/25 | - | NoticeMainViewUpdateMarch, OnEnterCity, PveLevelEnter | - | - | - |
| `DataCenter.AllianceLeaderRewardManager` | 8/35 | MsgDefines.GetAllianceWelfareInfo, MsgDefines.ReceiveAllianceW... | AllianceLeaderStageRewardReceived, UpdateGold | - | - | AllianceBaseDataManager, RewardManager |
| `DataCenter.AllianceMainManager` | 2/15 | MsgDefines.ViewAllianceLog | AllianceLogUpdate | - | - | AllianceWarLogManager |
| `DataCenter.AllianceMemberDataManager` | 64/65 | MsgDefines.AlRank, MsgDefines.DonateRankReward | OnAllianceOfficialPosChange, OnGetNewAlJoinReq, PlayerRan... | UIAlMemberRecommend | - | AllianceBaseDataManager, AllianceData, BuildManager |
| `DataCenter.AllianceMineManager` | 50/51 | MsgDefines.GetAllAllianceMineList, MsgDefines.GetAllMarchesOfA... | AllianceFlagUpdate, AllianceFrontUpdate, AllianceMemberPv... | - | TableName.AllianceMine, TableName.AllianceResBuild | AllianceBaseDataManager, AllianceMine, GloryManager, Seas... |
| `DataCenter.AllianceRedPacketManager` | 43/45 | MsgDefines.GetAllianceRedPacket, MsgDefines.GetRedPack, MsgDef... | GetRedPacketUpdate, UpdateGold | - | TableName.SysRedPacket | AllianceBaseDataManager, BuildManager, ResourceTemplateMa... |
| `DataCenter.AllianceRedPointManager` | 2/3 | - | - | - | - | AllianceBaseDataManager |
| `DataCenter.AllianceScienceDataManager` | 29/30 | MsgDefines.AlScienceNumFresh | AllianceScienceDonate, OnAlScienceRecommendChange | - | TableName.AlScienceTab | AllianceBaseDataManager, AllianceData |
| `DataCenter.AllianceShopDataManager` | 1/12 | - | - | - | - | ItemTemplateManager |
| `DataCenter.AllianceShopPlusDataManager` | 18/69 | MsgDefines.AlShopNewBuyAl, MsgDefines.AlShopNewBuyRecords, Msg... | AllianceShopPlusRestockBubble | - | TableName.APS_shop | AllianceGiftDataManager, AllianceShopDataManager, ItemTem... |
| `DataCenter.AllianceSkillManager` | 17/18 | MsgDefines.KingdomSkillUse, MsgDefines.WorldMissileInfo | - | - | - | AllianceSkillTemplateManager, WorldMissileManager |
| `DataCenter.AllianceSkillTemplateManager` | 8/9 | - | - | - | - | AllianceSkillManager, SeasonDataManager |
| `DataCenter.AllianceStorageManager` | 3/9 | MsgDefines.GetAllianceStorageInfo | OnRecvAllianceStorageInfo | - | - | AllianceBaseDataManager |
| `DataCenter.AllianceTaskManager` | 7/18 | MsgDefines.GetAllianceTaskInfo | OnAllianceTaskRedChange, OnUpdateAllianceTask, UpdateMain... | - | TableName.AllianceTask | AllianceBaseDataManager |
| `DataCenter.AllianceTempListManager` | 20/21 | - | SetALRankName | - | - | AllianceData |
| `DataCenter.AllianceWarDataManager` | 53/54 | MsgDefines.AllianceWarCancel, MsgDefines.AllianceWarRetreat, M... | AllianceWarInfoUpdate, AllianceWarNewStatusChanged, Check... | UIAllianceWarInfoView, UIAllianceWarMainTable | TableName.HeroMilitaryRank, TableName.WorldCity | AllianceData, BuildManager, FormationAssistanceDataManage... |
| `DataCenter.AllianceWarLogManager` | 4/10 | MsgDefines.ViewAllianceWarLog, MsgDefines.ViewAllianceWarLogDe... | AllianceWarLogDetailUpdate, AllianceWarLogUpdate | - | - | - |
| `DataCenter.AppearanceTemplateManager` | 1/2 | - | - | - | TableName.HeroAppearance | - |
| `DataCenter.ArenaManager` | 11/22 | MsgDefines.GetArenaInfo, MsgDefines.GetArenaLatestInfo, MsgDef... | AreanRankDataUpdated | - | - | ActivityListDataManager, RewardManager, SecondConfirmManager |
| `DataCenter.ArmyFormationDataManager` | 29/94 | MsgDefines.GetMyStationData, MsgDefines.SaveFormationTempHero,... | FormationInfoUpdate, FormationSoldierUpdate, ReceiveGetDe... | - | - | ArmyManager, BuildTemplateManager, HeroDataManager, Month... |
| `DataCenter.ArmyManager` | 30/56 | MsgDefines.QueueCcdMNew, MsgDefines.QueueFinish | SoldierExchange, TrainArmyData, UnlockArmy, UpdateGold | UINoticeEquipTips, UISoliderGetTip | - | ArmyTemplateManager, BuildManager, BuildTemplateManager, ... |
| `DataCenter.ArmyTemplateManager` | 52/53 | - | - | - | TableName.ArmsTab | ArmyManager, HonorPhaseManager, VolcanoWarManager |
| `DataCenter.AssistanceHeroDataManager` | 4/23 | MsgDefines.GetHeroAssistanceInfo | InitAllAssistanceHero | UIPositionShare | - | BuildManager, StoryManager |
| `DataCenter.BagGridDataManager` | 14/34 | MsgDefines.BagCommonModify, MsgDefines.BagGridSingleMove, MsgD... | Survival_EquipDurableChanged, Survival_EquipSlotChanged, ... | - | TableName.C_Equips | BattleLevel, BuildManager, ItemTemplateManager |
| `DataCenter.BarterShopNoticeManager` | 7/11 | MsgDefines.KillMonsterActInfo, MsgDefines.KillMonsterStageReward | OnPassDay, RefreshKillMonsterActInfo | - | - | RewardManager |
| `DataCenter.BaseExpansionTemplateManager` | 5/10 | - | - | - | TableName.BaseExpansion, TableName.SingleMapPosition | BuildManager |
| `DataCenter.BattleCommandManager` | 39/68 | MsgDefines.DragonChangeCommander, MsgDefines.DragonGetCommandL... | DeleteOneDragonCommandSign, EnterDragonWorld, MiniMapShow... | - | - | ActDragonManager, AllianceMemberDataManager, DragonSwapMa... |
| `DataCenter.BattleLevel` | 26/144 | MsgDefines.SU_HeartBeat | LevelSceneLoadDone, OnEnterCity, SU_ChangeViewHeight, SU_... | MainUI_SU, SU_NewHero, UIArenaPanel, UIPVELoading | TableName.SU_PveType | BuildManager, ChapterTaskManager, ControlTriggerManager, ... |
| `DataCenter.BaubleLibraryManager` | 10/33 | MsgDefines.ClaimBaubleReward, MsgDefines.GetBaubleRewardInfo | BaubleLibraryRedPointRefreshed, BaubleStatusChanged, SU_R... | - | TableName.BaubleRating, TableName.EffectNumDesc | BaubleManager, BuildManager, RewardManager |
| `DataCenter.BaubleManager` | 22/47 | MsgDefines.MoveBauble, MsgDefines.PlaceBauble, MsgDefines.Upgr... | BAUBLE_UPGRADE_Refresh, InitAllBauble, RefreshBauble, Rem... | UIBaubleLevelUpPopup | TableName.Bauble | BattleLevel, BaubleLibraryManager, BaubleObjectManager, B... |
| `DataCenter.BaubleObjectManager` | 5/17 | - | LevelSceneLoadDone | - | - | BattleLevel, BaubleManager |
| `DataCenter.BirthPointTemplateManager` | 2/12 | - | - | - | TableName.WorldCity | BuildManager |
| `DataCenter.BoardManager` | 8/29 | - | RefreshCityRoadArr, UpdateRoadData | - | - | BuildManager, BuildTemplateManager |
| `DataCenter.BuildBubbleManager` | 71/170 | - | OverlordGrowUpItemChanged, PlayNormalBubbleAni | UIWorldTileUI | - | BattleLevel, BaubleManager, BuildManager, BuildPoliceInsi... |
| `DataCenter.BuildCanUpgradeEffectManager` | 12/21 | - | UPDATE_BUILD_DATA | - | - | BaubleManager, BuildManager |
| `DataCenter.BuildIdleEffectManager` | 11/17 | - | BuildUpgradeStart | - | - | BuildManager, BuildTemplateManager |
| `DataCenter.BuildManager` | 125/256 | MsgDefines.AlBeLeaderCheck, MsgDefines.BuildCcdMNew, MsgDefine... | BUILD_IN_VIEW, BuildBoxOpenFinish, BuildRedDotRecord, Bui... | UIBuildUpUnlock, UIBuildUpgradeAddDes, UIBuildUpgrad... | TableName.Adaptive_Box, TableName.BaseUnlockBuilding... | ArmyManager, BattleLevel, BoardManager, BuildPoliceInsign... |
| `DataCenter.BuildNameTipManager` | 8/16 | - | OnWorldInputDragBegin | UIWorldTileUI | - | BuildManager, BuildTemplateManager |
| `DataCenter.BuildPoliceInsigniaManager` | 44/89 | MsgDefines.FreeBuildingUpNew | SU_PoliceInsigniaBuildPack, SU_RefreshItemById | - | TableName.Init_Build | BuildManager, BuildProcessControlManager, BuildTemplateMa... |
| `DataCenter.BuildProcessControlManager` | 17/52 | - | GuideSaveFinish | UI_DayNight | - | BattleLevel, BuildManager, GuideManager |
| `DataCenter.BuildQueueManager` | 23/69 | - | BuildUpgradeStart, Build_Fix_Time_End, Build_Time_End, Re... | - | TableName.Robot | BuildManager, BuildQueueTalkManager, BuildQueueTemplateMa... |
| `DataCenter.BuildQueueTalkManager` | 1/3 | - | - | - | - | UavDialogueTemplateManager |
| `DataCenter.BuildQueueTemplateManager` | 1/8 | - | - | - | TableName.Robot | BuildQueueManager |
| `DataCenter.BuildStatusManager` | 5/12 | - | BuildStatusUpdate | - | - | BuildManager |
| `DataCenter.BuildTemplateManager` | 4/18 | - | - | - | TableName.Building, TableName.BuildingDes, TableName... | BuildQueueManager |
| `DataCenter.BuildTimeManager` | 34/49 | - | BuildFixStart, BuildPlace, RefreshBuildUpgradeEffect | UIPasture | - | BattleLevel, BuildManager, GuideManager |
| `DataCenter.BuildTrainEffectManager` | 5/19 | - | TrainingArmyFinish | - | - | BuildManager, QueueDataManager |
| `DataCenter.BuildUpgradeEffectManager` | 29/47 | - | BuildConfirmFinish, BuildObjectShowOpenBoxTimeline, Build... | MainUI_SU | - | BattleLevel, BuildManager, BuildPoliceInsigniaManager, Bu... |
| `DataCenter.BuildUpgradeStockManager` | 5/9 | MsgDefines.UBStoreUpgrade | RefreshBuildUpgradeStock, UpdateGold | - | - | BuildPoliceInsigniaManager |
| `DataCenter.BuildZoneManager` | 6/13 | - | OpenUI | UIWorldTileUI | - | BuildManager, BuildTemplateManager |
| `DataCenter.CampEffectManager` | 3/10 | - | - | - | - | BattleLevel, BuildManager |
| `DataCenter.CanUnlockFogManager` | 9/19 | MsgDefines.CityUnlockFog | UnlockFogAnim | - | - | GuideManager |
| `DataCenter.CarBattlePveManager` | 7/25 | MsgDefines.UserSkipPveTrigger | CarBattlePveSkipLevel | UIPositionShare | TableName.Barrel_PVE | ActivityListDataManager, BuildManager |
| `DataCenter.CarChipActivityManager` | 13/25 | MsgDefines.CarChipActivityClaimPreviewReward, MsgDefines.CarCh... | CarChipActivityChipMemberInfoUpdate, CarChipActivityChipP... | - | - | ActivityListDataManager, AllianceBaseDataManager, CarChip... |
| `DataCenter.CarChipManager` | 28/86 | MsgDefines.CarChipGetInfoMessage, MsgDefines.CarChipInstall, M... | CarChipDataChanged, CarChipGroupSettingChanged, CarChipIn... | UICarChipUpgradePopup | TableName.CarMicrochipBox, TableName.EffectNumDesc | ActivityListDataManager, CarChipTemplateManager, ItemData... |
| `DataCenter.CarChipTemplateManager` | 4/17 | - | - | - | TableName.CarMicrochip, TableName.CarMicrochipAttrib... | - |
| `DataCenter.CarComponActivityManager` | 13/25 | MsgDefines.CarChipActivityClaimPreviewReward, MsgDefines.CarCh... | CarComponActivityClaimRewardResponse, CarComponActivityCo... | - | - | ActivityListDataManager, AllianceBaseDataManager, GarageC... |
| `DataCenter.CarnivalMomentManager` | 35/36 | MsgDefines.GetShowtimePackInfo, MsgDefines.ShowtimePackCheerin... | CarnivalCheerSuccess, CarnivalDanmakuPush, CarnivalDayRes... | UICarnivalLuckySpin | - | AllianceRedPacketManager, BuildManager, CarnivalMoment, I... |
| `DataCenter.CastleAdventureManager` | 5/22 | MsgDefines.GetCastleAdventureAllianceProgress | OnPassDay, UpdateCastleAdventureAllianceHelp | - | - | ActivityListDataManager |
| `DataCenter.ChainPayManager` | 14/20 | MsgDefines.ChainPayGetInfo, MsgDefines.ChainPayReceiveReward, ... | ChainPayGetInfo, ChainPayReceiveReward, ChainPayRefresh, ... | - | - | ActivityListDataManager, RewardManager |
| `DataCenter.ChangeNameAndPicManager` | 7/14 | MsgDefines.GetUploadPicActivityInfo, MsgDefines.ReceiveUploadP... | RefreshActivityRedDot, RefreshChangeNameAndPic | - | - | ActivityListDataManager, RewardManager |
| `DataCenter.ChapterTaskManager` | 18/45 | MsgDefines.GetAllChapterInfo | ChapterTask, ChapterTaskGetReward | GetWindow, UITaskPromptTips | TableName.Chapter | BattleLevel, ChapterTemplateManager, QuestTemplateManager... |
| `DataCenter.ChapterTemplateManager` | 2/3 | - | - | - | TableName.Chapter | - |
| `DataCenter.CityCameraManager` | 5/14 | - | ChangeCameraInitZoom, OnEnterCity | - | - | BuildManager, DecorationTemplateManager |
| `DataCenter.CollectResourceManager` | 3/20 | - | - | - | - | CollectResourceTemplateManager |
| `DataCenter.CollectRewardDataManager` | 1/7 | - | MonsterRewardCreate | - | - | - |
| `DataCenter.CommonShopManager` | 7/18 | MsgDefines.GetCommonShopInfo, MsgDefines.GetCommonShopInfoMulti | CheckPubBubble, OnCommonShopRedChange, UpdateOneCommonSho... | - | - | BuildManager |
| `DataCenter.ControlTriggerManager` | 8/14 | - | SU_UpdateTriggerState | - | - | BattleLevel, SV_MapItemInfoManager |
| `DataCenter.CreditManager` | 8/21 | MsgDefines.PayCreditStat, MsgDefines.RefundDeductHistory | CreditUpdate, UpdateGold, UpdateRefundHistory | UICreditMainPanel, UIRefundDeductGold, UISoliderGetTip | - | ActivityListDataManager |
| `DataCenter.CrossArenaManager` | 8/14 | MsgDefines.GetCrossArenaInfo, MsgDefines.GetCrossArenaLatestIn... | AreanRankDataUpdated | - | - | ActivityListDataManager |
| `DataCenter.CrossHitBlockManager` | 36/37 | MsgDefines.GetCrossDesertBox, MsgDefines.GetCrossDesertInfo, M... | UpdateDesertRank, UpdateHitBlockBoxReward, UpdateHitBlock... | - | - | ActivityListDataManager, BuildManager, SeasonCrossHitBlock |
| `DataCenter.CrossWonderManager` | 63/149 | MsgDefines.BattleUserScoreRanklist, MsgDefines.GetServerBattle... | AlSkillInfoUpdate, CrossWonderGetInfo, CrossWonderWarFlag... | UICommonHeadTip, UICrossWonderCountdownPanel, UIGift... | TableName.Servers_Wonder_War, TableName.State_Ruler_... | ActivityListDataManager, AllianceCompeteDataManager, Alli... |
| `DataCenter.CrossWonderTemplateManager` | 2/3 | - | - | - | TableName.Server_Capital_Reward, TableName.Servers_W... | - |
| `DataCenter.CumulativeRechargeManager` | 7/17 | MsgDefines.GetRechargeInfo, MsgDefines.ReceiveRechargeReward | CumulativeReward, RefreshDailyCumulative | - | TableName.Recharge | RewardManager |
| `DataCenter.DailyMustBuyManager` | 6/10 | MsgDefines.DailyMustBuyList, MsgDefines.DailyMustBuyReward | OnDailyMustBuyDataChanged | - | - | ItemData, RewardManager |
| `DataCenter.DailyPackageManager` | 3/10 | MsgDefines.GetDailyPackageInfos | RefreshWelfareRedDot | - | - | - |
| `DataCenter.DailyTaskManager` | 15/29 | MsgDefines.DailyQuestLs | DailyQuestLs, DailyQuestReward, OnPassDay, ResourceUpdated | UIPresentGetRewardView | - | ActIceCaveManager, ActivityListDataManager, DailyTaskTemp... |
| `DataCenter.DailyTaskTemplateManager` | 1/2 | - | - | - | TableName.DailyQuest | - |
| `DataCenter.DayRechargeMonthCardManager` | 8/19 | MsgDefines.GetMonthPayActInfo, MsgDefines.ReceiveAllMonthPayRe... | GetRechargeMonthCardAllReward, GetRechargeMonthCardInfo, ... | - | - | RewardManager |
| `DataCenter.DeadArmyRecordManager` | 3/12 | MsgDefines.GetDeadArmyRecord | RefreshDeadArmyRecord, RefreshDeadArmyRecordRedDot | - | - | - |
| `DataCenter.DecResourceEffectManager` | 1/3 | - | - | - | - | BattleLevel |
| `DataCenter.DecorationDataManager` | 35/52 | MsgDefines.CoverSkin, MsgDefines.GetTitleRank, MsgDefines.Take... | ChangeSex, UpdatePlayerHeadIcon, UserSkinUpdate | UIDecorationUpgradeSuccess, UITitleDetail, UnlockNew... | TableName.Decoration | BuildManager, DecorationTemplateManager, ItemData, MonthC... |
| `DataCenter.DecorationTemplateManager` | 2/21 | - | - | - | TableName.Decoration | VIPManager |
| `DataCenter.DeeplinkManager` | 4/16 | MsgDefines.LoginThirdPartWeb | WebLoginResult | - | - | ChristmasActManager |
| `DataCenter.DefenceWallDataManager` | 5/16 | - | - | - | - | BuildManager, BuildTemplateManager, PushNoticeManager |
| `DataCenter.DemonHunterDataManager` | 28/80 | MsgDefines.GetDemonHunterInfo, MsgDefines.SubmitDemonHunterQuest | DemonHunterHunterUpdate, DemonHunterInfoUpdate, DemonHunt... | UICommonMessageBar, UIDemonHunterMapPointTips, UIDem... | TableName.DemonHunterInfo, TableName.DemonHunterQuest | ActivityListDataManager, QuestTemplateManager, RewardMana... |
| `DataCenter.DesertDataManager` | 135/136 | MsgDefines.AlRank, MsgDefines.UserCancelGiveUpDesert, MsgDefin... | ActDesertForceGroupRank, CheckGatherSeasonResRedDot, Forc... | RemoveDesertOccupyDelayTimer, UIAlNoticeScoreTips, U... | TableName.Desert, TableName.SeasonInfluence | AllianceBaseDataManager, AllianceMemberDataManager, Build... |
| `DataCenter.DetectEventBubbleManager` | 6/10 | - | GetAllDetectInfo | - | - | RadarCenterDataManager |
| `DataCenter.DetectEventTemplateManager` | 4/5 | - | - | - | TableName.DetectEvent | - |
| `DataCenter.DigActivityManager` | 31/86 | MsgDefines.BuyDigTool, MsgDefines.DigOneBlockVertical, MsgDefi... | CheckDigRewardRedPoint, GetBalloonPuzzleInfo, OnDigActFin... | UIGiftBoxPackageList, UIMultiBuy | TableName.ActivityPanel, TableName.DigActivityDig | ActivityController, ActivityListDataManager, AllianceBase... |
| `DataCenter.DigTreasureDataManager` | 6/19 | MsgDefines.GetAllianceTreasure | OnDigTreasureTipEvent | - | - | AllianceBaseDataManager, RadarCenterDataManager |
| `DataCenter.DragonSwapManager` | 18/39 | MsgDefines.DragonKickMember, MsgDefines.DragonMemberStatusInfo... | DragonSwapEntryUpdate, DragonSwapPanelRefresh, DragonSwap... | - | - | ActDragonManager |
| `DataCenter.DrakeBoss2Manager` | 13/37 | MsgDefines.ActivityRallyBossInfo, MsgDefines.ActivityRallyBoss... | DrakeBoss2InfoUpdate, RefreshActivityRedDot | UIBagView, UIDrakeBossUseItem | - | ActivityListDataManager, BuildManager, HeroDataManager, I... |
| `DataCenter.DroppedTreasureDataManager` | 4/9 | MsgDefines.GetChildhoodTreasureInfo | RefreshDroppedTreasureActivityInfo | - | - | ActivityListDataManager |
| `DataCenter.EffectGetItemDataManager` | 3/9 | - | HeroExpEffectChange | - | - | ArmyManager, ItemTemplateManager, RewardManager |
| `DataCenter.EquipmentDataManager` | 18/31 | MsgDefines.CarEquipExp, MsgDefines.EquipUpQuality, MsgDefines.... | EquipDataUpdate, EquipSuitDataUpdate | UIEquipmentAdvanceSuccess | - | BuildManager, EquipmentSuitTemplateManager, EquipmentTemp... |
| `DataCenter.EventBubbleManager` | 5/14 | - | SU_ChangeViewHeight | - | TableName.PVETrigger | GirlBehaviorManager, SV_MapItemInfoManager |
| `DataCenter.FactoryDataManager` | 16/41 | MsgDefines.UserCancelFactoryPanel | CanGetProduct, FactoryDataCancel | - | TableName.Factory | BattleLevel, BuildManager, BuildTemplateManager, Resource... |
| `DataCenter.FakeCollectGarbageMarchManager` | 4/14 | - | OnEnterWorld | - | - | RadarCenterDataManager, WorldPointManager |
| `DataCenter.FakeHelperMarchManager` | 4/14 | - | OnEnterWorld | - | - | RadarCenterDataManager, WorldPointManager |
| `DataCenter.FakeRescueMarchManager` | 4/14 | - | OnEnterWorld | - | - | RadarCenterDataManager, WorldPointManager |
| `DataCenter.FishingCatalogDataManager` | 25/65 | ChatMsgDefines.GetUserInfoMulti, MsgDefines.SendFish, MsgDefin... | ChatPrivateRoomCreated, FishingCatalogAtlasRewardUpdate, ... | UIFishingCatalogGiveGift, UIFishingCatalogGiveGiftSu... | TableName.IceCaveInfo | ActIceCaveManager, DecorationDataManager, GuideManager, I... |
| `DataCenter.FiveStarManager` | 8/9 | - | MainLvUp | UIFiveStarGet | - | BuildManager, UIPopWindowManager |
| `DataCenter.FlyController` | 11/25 | - | SU_FlyObjFirst, UpdatePlayerExp | - | - | - |
| `DataCenter.FoodFestivalEatManager` | 70/71 | ChatMsgDefines.ChatRoom, MsgDefines.BanquetAddMealRecords, Msg... | FoodFestivalEatSendToChat, RefreshUIWorldPointView | UIFoodFestivalEatPreviewTipView, UIWorldPoint | TableName.ActivityPanel, TableName.FoodFestivalEatBu... | ActivityListDataManager, AllianceMineManager, FoodFestiva... |
| `DataCenter.FormStatusManager` | 8/22 | MsgDefines.ItemUse | FormStatusUpdate | - | - | ItemTemplateManager, WorldMarchDataManager |
| `DataCenter.FormationAssistanceDataManager` | 1/3 | - | UpdateAssistanceLeader | - | - | - |
| `DataCenter.FriendManager` | 29/30 | MsgDefines.DeleteFriend, MsgDefines.FriendApply, MsgDefines.Fr... | DeleteFriend, FriendGroupChat, RefreshFriend, RefreshFrie... | - | - | FriendData |
| `DataCenter.FrozenLandDataManager` | 25/52 | MsgDefines.CallHelpAnimal, MsgDefines.FindIceAnimal, MsgDefine... | LoadMapDataFromFileFinish, OnGetFrozenLandStageReward, On... | UIDetectNpc | TableName.IceAnimals, TableName.WorldCity | ActivityListDataManager, GuideManager, RewardManager, Wor... |
| `DataCenter.GarageComponManager` | 13/57 | MsgDefines.CarComponInstall, MsgDefines.CarComponInstallAll, M... | CarComponEquipChanged, CarComponPartsChanged | - | TableName.CarCompon | BuildManager, GarageRefitManager |
| `DataCenter.GarageRefitManager` | 23/113 | - | CarTalentGradingTimeChange, GarageRefitTalentUnlock | - | TableName.CarTalent, TableName.GaragePart, TableName... | BuildBubbleManager, BuildManager, GarageComponManager, It... |
| `DataCenter.GhostKingBornManager` | 25/58 | MsgDefines.GhostKingInfo, MsgDefines.GhostKingRankInfo, MsgDef... | GhostKingBornActInfo, RefreshGhostKingRank, RefreshGhostK... | - | TableName.GhostKingDonate, TableName.GhostKingInfo, ... | ActivityListDataManager, AllianceCityTemplateManager, Ite... |
| `DataCenter.GirlBehaviorManager` | 27/35 | MsgDefines.SUCancelCollectGarbage, MsgDefines.SUConfirmGarbage... | AddCollectQueue, GarbageTriggerFinish, RemoveCollectQueue | UISpeed | TableName.PVETrigger | BattleLevel, BuildManager, BuildQueueManager, BuildQueueT... |
| `DataCenter.GloryManager` | 78/171 | MsgDefines.AlBattleEvent, MsgDefines.AlFightActInfo, MsgDefine... | EdenCampScore, EdenUserRank, GloryDeclareStateRefresh, Gl... | UIGloryDeclareWarPopTips | TableName.APS_Season, TableName.AllianceResBuild, Ta... | ActivityListDataManager, AllianceBaseDataManager, Allianc... |
| `DataCenter.GloryWarSwapManager` | 22/55 | MsgDefines.KingdomSwapExec, MsgDefines.KingdomSwapInfo, MsgDef... | GloryWarSwapExecFailed, GloryWarSwapExecSuccess, GloryWar... | UIGloryWarSwapTip | - | AllianceBaseDataManager, AllianceMemberDataManager, Allia... |
| `DataCenter.GoldTrackManager` | 1/6 | - | LevelSceneLoadDone | - | - | - |
| `DataCenter.GolloesCampManager` | 29/62 | MsgDefines.ClaimGolloesRewardNew, MsgDefines.GolloesNewDataGet... | GarbageCollectStart, GetGolloesRewardState, GolloesDataCh... | - | - | ArmyFormationDataManager, BuildManager |
| `DataCenter.GovernmentManager` | 56/107 | MsgDefines.ChooseKing, MsgDefines.GetKingHistory, MsgDefines.G... | ApplyPosConditionSet, GovernmentHistoryRecordRefresh, Gov... | UIThroneKingdomAssumedsuccessfull, UITransferKing | TableName.EffectNumDesc | AllianceBaseDataManager, BuildManager, GovernmentTemplate... |
| `DataCenter.GovernmentTemplateManager` | 1/13 | - | - | - | TableName.Government | - |
| `DataCenter.GovernmentWorldBubbleManager` | 7/12 | - | CheckShowGovPos | - | - | WorldPointManager |
| `DataCenter.GroceryStoreOrderDataManager` | 8/19 | MsgDefines.PurchaseOrderDelete, MsgDefines.PurchaseOrderFinish... | DelayRefreshResource, RefreshGroceryStoreOrder | - | - | ItemData |
| `DataCenter.GroundPassManager` | 4/8 | - | LandRewardCollected | UIGroundPassUnlock | TableName.LandLock | ActBattlePassData, ActivityListDataManager |
| `DataCenter.GuideAllianceMemberEffectMan...` | 2/7 | - | - | - | - | AllianceBaseDataManager, GuideManager |
| `DataCenter.GuideCityAnimManager` | 11/41 | - | GuideTimelineMarker | UITimelineJump | - | BuildProcessControlManager, GuideManager, LWBattleManager... |
| `DataCenter.GuideManager` | 80/225 | MsgDefines.SaveGuide, MsgDefines.StatTT | Barrel_PauseOrResumeUnitAni, ClickFarmBuildShow, GuideBre... | MainUI_SU, UIBuildList, UICommonMessageTip, UIGuideH... | - | BattleLevel, BuildManager, BuildQueueManager, ChapterTask... |
| `DataCenter.GuideNeedLoadManager` | 8/34 | - | GuideTimelineMarker, NoticeMainViewUpdateMarch | - | - | GuideManager |
| `DataCenter.GuidePickGarbageBubbleManager` | 3/17 | - | - | - | - | CityPointDataManager, PickGarbageDataManager |
| `DataCenter.GuideTemplateManager` | 1/5 | - | - | - | TableName.Guide | - |
| `DataCenter.HeroBountyDataManager` | 8/19 | MsgDefines.ReceiveHeroBountyTaskReward | OnHeroBountyOneTaskRefresh, OnHeroBountyTaskRefresh, Refr... | - | - | BuildManager, HeroDataManager, RewardManager |
| `DataCenter.HeroDataManager` | 14/50 | - | GetLastSeasonHeroRecordInfoSuccess | UIHeroBeyond, UIHeroMilitaryRank | TableName.HeroMilitaryRank | BuildManager, GuideManager, HeroEffectSkillManager, HeroS... |
| `DataCenter.HeroEffectSkillManager` | 5/18 | MsgDefines.UseHeroEffectSkill | RefreshHeroEffectSkill | UICapacityFull, UIHeroEffectSkillTips | - | ArmyManager, RewardManager |
| `DataCenter.HeroEquipManager` | 47/90 | MsgDefines.HeroEquipDecompose, MsgDefines.HeroEquipEvolution, ... | HeroEquipDecompose, HeroEquipInstall, HeroEquipMaterialCo... | UIHeroEquipEvolutionSuccess | - | BuildManager, GuideManager, HeroEquipForgePromoteTemplate... |
| `DataCenter.HeroEquipTemplateManager` | 17/28 | - | - | - | TableName.Equip | BuildManager, HeroEquipUpgradeTemplateManager, ItemData, ... |
| `DataCenter.HeroIntensifyManager` | 16/29 | MsgDefines.HeroIntensify, MsgDefines.HeroIntensifyOneKey | HeroIntensifyUpgrade | - | TableName.EffectNumDesc, TableName.HeroIntensify | BuildTemplateManager, HeroDataManager |
| `DataCenter.HeroLevelUpTemplateManager` | 4/10 | - | - | - | TableName.NewHeroesLevelUp_B | BuildManager, BuildTemplateManager |
| `DataCenter.HeroMonthCardManager` | 17/18 | MsgDefines.GetHeroMonthCardInfo, MsgDefines.GetHeroMonthCardRe... | RefreshHeroMonthCard, RefreshHeroMonthCardAll, RefreshHer... | - | - | RewardManager |
| `DataCenter.HeroOfficialManager` | 8/22 | - | SetHeroOfficial | - | - | BuildManager, HeroDataManager |
| `DataCenter.HeroSPEquipManager` | 19/50 | MsgDefines.HeroSPEquipUpgrade | HeroSPEquipBreak, HeroSPEquipCheck, HeroSPEquipUpdate | - | TableName.HeroSPEquip, TableName.SkillTab | BuildManager, HeroDataManager, HeroSkinManager, ItemData,... |
| `DataCenter.HeroSkinManager` | 23/34 | MsgDefines.SurvivalHeroSkinSwitch, MsgDefines.SurvivalHeroSkin... | CloseUI, HeroSkinRed, HeroSkinRefresh | UIGetDress | TableName.EffectNumDesc | HeroDataManager, HeroTemplateManager |
| `DataCenter.HeroSkinShopManager` | 13/29 | MsgDefines.GiftVouchersRewardList, MsgDefines.RevGiftVouchersF... | SkinShopRefresh, SkinShopTicketRefresh | UIMultiBuy | TableName.Hero_Skin_Shop | HeroSkinManager, ResourceManager, RewardManager |
| `DataCenter.HeroSmallPeopleDataManager` | 25/65 | MsgDefines.HeroStationSaveMessage | BuildStationChange | UIScreenCenterTips | TableName.SkillTab | BuildBubbleManager, BuildManager, HeroEffectSkillManager,... |
| `DataCenter.HeroStationManager` | 20/65 | MsgDefines.HeroStationSaveMessage, MsgDefines.HeroStationUseSk... | HeroStationSave, HeroStationUpdate, HeroStationUseSkill | - | - | BuildBubbleManager, BuildManager, DecResourceEffectManage... |
| `DataCenter.HeroStationTemplateManager` | 1/7 | - | - | - | TableName.Hero_Station | - |
| `DataCenter.HeroTemplateManager` | 3/10 | - | - | - | TableName.LW_Hero | HeroDataManager |
| `DataCenter.HonorPhaseManager` | 29/30 | - | PUSH_INIT_OK | UIHonorPhaseCG | TableName.ArmyHonor | ArmyTemplateManager, BuildManager, BuildTemplateManager |
| `DataCenter.HospitalManager` | 27/28 | MsgDefines.QueueFinish | HospitalUpdate, UpdateGold | - | - | ArmyTemplateManager, HospitalData, QueueDataManager |
| `DataCenter.HotUpdatePrefetchManager` | 1/20 | - | - | - | - | - |
| `DataCenter.IdVerManager` | 1/11 | MsgDefines.AdultVerificate | - | - | - | - |
| `DataCenter.ItemData` | 23/43 | - | OnCheckNewDecorate, OnGoodsRedState, RefreshGirlTipItem, ... | UIParkourBattleMain | - | ItemTemplateManager |
| `DataCenter.ItemManager` | 8/14 | - | RefreshItems, UpdateGold, UseItemSuccess | UIPhonographMain | - | ItemData, ItemTemplateManager |
| `DataCenter.ItemTemplateManager` | 8/36 | - | - | - | TableName.AllianceGiftGroup, TableName.GoodsTab | AllianceShopDataManager, BuildManager |
| `DataCenter.KeepPayManager` | 7/12 | MsgDefines.GetRechargeInfo, MsgDefines.ReceiveRechargeReward | KeepPayUpdate | - | - | RewardManager |
| `DataCenter.KingdomSwapManager` | 46/47 | MsgDefines.KingdomSwapExec, MsgDefines.KingdomSwapFavorite, Ms... | KingdomSwapExecSuccess, KingdomSwapFavorUpdate, KingdomSw... | UIKingdomSwapTip | - | CrossWonderManager, GovernmentManager, KingdomSwap, UIPop... |
| `DataCenter.LWAllyStationDataManager` | 8/36 | MsgDefines.AllianceTrainInfo | AllianceTrainBuySuccess, Arena3V3BattleFinish, DelAllyTra... | - | TableName.LW_Train_Para | LW3V3Manager, MonopolyManager |
| `DataCenter.LWBattleManager` | 27/108 | MsgDefines.MailGetFightReportDetail, MsgDefines.StatTT, MsgDef... | Barrel_StartLevelResponse, BeforeReleaseCity, GF_pve_batt... | LWPVPArenaMain, MainUI_SU, UIDetectEvent, UIJeepAdve... | TableName.PVELevelOld | GuideManager, IsValid, LWSceneStateManager, LWSoundManage... |
| `DataCenter.LWMyStationDataManager` | 37/107 | MsgDefines.AttackTrain, MsgDefines.ChangeTrain, MsgDefines.Col... | ChangeTrainSuccess, EnemyTruckWeaponDataArrive, OnUpdateA... | - | TableName.GoodsTab, TableName.LW_Train_Para | ActivityListDataManager, ArmyFormationDataManager, ArmyMa... |
| `DataCenter.LWMyStationManager` | 7/22 | - | BUILD_IN_VIEW | - | - | BuildManager, LWMyStationDataManager |
| `DataCenter.LWTrainDataManager` | 6/28 | MsgDefines.GetTrainList, MsgDefines.TrainStatus | RefreshTrainListData, TrainStatusResponse | - | TableName.LW_Train_Property | LWMyStationDataManager |
| `DataCenter.LandLockBubbleManager` | 11/21 | - | LandLockInView, ResetQuestArrow | UIWorldTileUI | - | BuildManager, LandLockManager, RecommendShowManager |
| `DataCenter.LandLockManager` | 56/116 | MsgDefines.FinishUserLand, MsgDefines.ReceiveLandReward, MsgDe... | LandLockInView, LandLockInit, LandLockOutView, LandLockSt... | SU_NewHero, UIWorldTileUI | TableName.LandLock_B, TableName.PVETrigger | ArmyManager, BattleLevel, BuildManager, ChapterTaskManage... |
| `DataCenter.LandingOperationsDataManager` | 19/58 | MsgDefines.GetHeroBattleRank, MsgDefines.HeroBattleSetTargetCh... | LandingOperationQuickFightEnd, LandingOperationRank, Land... | - | - | ActivityListDataManager, BattleLevel, CarChipManager, Rew... |
| `DataCenter.LeagueMatchManager` | 17/40 | MsgDefines.GetCurSeasonLeagueMatchGroupInfo, MsgDefines.GetLas... | OnLastLeagueMatchGroupInfoUpdate, OnLeagueMatchBaseInfoUp... | - | - | ActivityListDataManager, AllianceCompeteDataManager |
| `DataCenter.LikeManager` | 22/50 | MsgDefines.AddLike, MsgDefines.CancelLike, MsgDefines.GetGiftL... | DemonHunterLikeUpdate, MainLvUp, RefreshAddLike, RefreshM... | UILike, UILikeMessageBigTips, UILikeMessageTips, UIL... | - | AllianceAnnouncementManager, BuildManager, DecorationData... |
| `DataCenter.LoadEditorBuildManager` | 3/5 | - | ShowLoadEditorBuild | UILoadEditorBuild | - | - |
| `DataCenter.LoginPopManager` | 15/21 | - | LevelSceneLoadDone, OnLoginPopped, RefreshWelfareRedDot | UIFirstCharge, UIGolloesMonthCardPopUp, UIPrivacy2, ... | - | ActFirstChargeData, ActivityListDataManager, ActivityTipM... |
| `DataCenter.LotteryDataManager` | 3/26 | - | CheckPubBubble | - | TableName.HeroRecruit | ItemData |
| `DataCenter.LoveNewsletterDataManager` | 17/43 | MsgDefines.SurvivalHeroMessage, MsgDefines.SurvivalHeroMessage... | HeroChatMessageOutTime, UpdateHeroBatteryPower, UpdateHer... | UILoveNewsletterMM | TableName.LoveMessageHero | HeroDataManager, LoveNewsletterTemplateManager, RewardMan... |
| `DataCenter.LoveNewsletterTemplateManager` | 1/6 | - | - | - | TableName.LoveMessageHero | - |
| `DataCenter.LowFxModeManager` | 1/13 | - | OnEnterWorld | - | - | - |
| `DataCenter.MailFacade` | 91/92 | MsgDefines.MailBatchDel | MailDetailReady, MailPush, Mail_DeleteBatchMailDone, Mail... | - | - | MailDataV4 |
| `DataCenter.MailGroupTemplateManager` | 6/7 | - | - | - | TableName.MailGroup | MailDataV4 |
| `DataCenter.MailShim` | 178/179 | - | MailDetailReady | UIBattleReportInfo, UICampBonusMailTip, UIMailBattle... | - | MailDataManager, MailDataV4, MailFacade, MailShareManager... |
| `DataCenter.MailShowTemplateManager` | 19/20 | - | - | - | TableName.MailShow | ActBlackKnightManager, MailDataV4 |
| `DataCenter.MainCityAreaDataManager` | 11/29 | - | LW_MainCityAreaFogUpdate, PlayBonFireAnim | - | TableName.Guide, TableName.SU_MainCityArea | ChapterTaskManager, GuideManager, MainCityAreaTemplateMan... |
| `DataCenter.MainCityAreaTemplateManager` | 1/7 | - | - | - | TableName.SU_MainCityArea | - |
| `DataCenter.MapRewardBoxManager` | 3/14 | - | - | - | TableName.PVETrigger | SV_MapItemInfoManager |
| `DataCenter.MarchEmojiDataManager` | 8/20 | MsgDefines.SendMarchEmoji, MsgDefines.SetEmoji | MarchEmojiSettingUpdate, SendMarchEmojiTimeUpdate | - | TableName.ShelterEmoji | ItemData |
| `DataCenter.MasteryManager` | 29/81 | MsgDefines.ItemUse, MsgDefines.MasteryChangePlan, MsgDefines.M... | AddSpeedSuccess, MasteryChangePlan, MasteryExpUpdate, Mas... | UICapacityFull, UIMastery, UIMasteryExpTip, UIMaster... | TableName.Mastery, TableName.SeasonObject | BuildManager, BuildTemplateManager, ItemData, RewardManag... |
| `DataCenter.MemoryPolicyManager` | 2/6 | - | OpenUI2 | - | - | - |
| `DataCenter.MigrateDataManager` | 51/52 | MsgDefines.GetMigrateServers, MsgDefines.GetMigrateUserInfo, M... | GetMigrateApplyList, GetMigrateList, GetMigrateServerDeta... | - | - | ActivityListDataManager |
| `DataCenter.MineCaveManager` | 16/54 | MsgDefines.GetMineCaveInfo, MsgDefines.SetMineCaveCross | OnPassDay, OnRecvMineCavePlunderLog, PveMineCaveInfoUpdat... | UIMineCaveCrossTip | TableName.MineCave | ActivityListDataManager, ArmyFormationDataManager, Decora... |
| `DataCenter.MinePlunderManager` | 6/16 | MsgDefines.GetActWorldResInfo | OnReceiveMinePlunderActivityInfo | - | TableName.ActivityPanel | ActivityListDataManager, AllianceCompeteDataManager, Worl... |
| `DataCenter.MistressLvTemplateManager` | 6/51 | - | RefreshUIBuildQueue | - | - | BuildManager, BuildQueueManager, ItemData, ItemTemplateMa... |
| `DataCenter.MomentManager` | 67/128 | ChatMsgDefines.ModifyGiftShow, ChatMsgDefines.MomentComment, C... | MomentUpdateBubbleChanged, RefreshChatMomentList, Refresh... | UIGiftPackage, UIMomentDetail, UIMomentPost | - | AllianceMemberDataManager, BuildManager, PrivilegeEffectM... |
| `DataCenter.MonopolyActivityDataManager` | 11/34 | MsgDefines.BuyActivityMonopolyGoods, MsgDefines.GetMonopolyAct... | OnRevMonopolyStageReward, OnRollMonopolyActivity, RevMono... | UIMultiBuy | - | ActivityListDataManager, RewardManager |
| `DataCenter.MonsterLockDataManager` | 13/28 | MsgDefines.ReceivePveMonsterReward | MonsterLockStateUpdate, OnEnterCity, RefreshMonsterRewardBag | UIPVEMonsterToLevel | - | BattleLevel, BuildManager, MonsterLockTemplateManager, Re... |
| `DataCenter.MonsterManager` | 9/27 | - | - | - | - | ActivityListDataManager, MissileUnlockManager, MonsterTem... |
| `DataCenter.MonsterTemplateManager` | 1/2 | - | - | - | - | ActivityListDataManager |
| `DataCenter.MonthCardNewManager` | 6/38 | - | AutoHelpReachThreshold, ColloesCaravanRecord, OnPackageIn... | - | - | - |
| `DataCenter.MonthMsgCardManager` | 7/15 | MsgDefines.GetMonthDetectCard, MsgDefines.GetWeekDiscountCard,... | RefreshActivityRedDot | - | - | - |
| `DataCenter.MoonlightCollectionDataManager` | 38/66 | - | ActivityTipStateUpdate, MoonlightCollectionDeployUpdate, ... | UIActivityCenterTable, UISeasonMoonlightGetS5, UISea... | TableName.NightLunarLightCard, TableName.NightLunarL... | ActivityListDataManager, ItemData, ItemTemplateManager, R... |
| `DataCenter.MuseumManager` | 8/16 | MsgDefines.UseTreasureSkill | FormationStaminaUpdate, OnTreasureInfoUpdate, OnTreasureS... | - | TableName.Museum | DecResourceEffectManager, RewardManager |
| `DataCenter.NationTemplateManager` | 10/11 | - | - | - | TableName.NationConf | - |
| `DataCenter.NightBaronessManager` | 28/29 | MsgDefines.AlBeLeaderCheck, MsgDefines.SealCityBossInfo, MsgDe... | RefreshBloodMoonGeneral, RefreshWorldDeleteAllGhostGeneral | UIAllianceCity, UISeasonBaronessPushS5 | TableName.WorldCity | QuestTemplateManager, SeasonManager, TaskManager, UIPopWi... |
| `DataCenter.NightFallManager` | 10/57 | MsgDefines.GetSnowManActInfo | CheckDayNightState, OnDayNightChange, RefreshActivityRedDot | UILWTrainScene, UISeasonNightFallsComing | - | TrainSceneManager, UIPopWindowManager |
| `DataCenter.NightSacrificeManager` | 28/29 | MsgDefines.GatherRewardPacket | RefreshPacketReward | UISeasonNightSacrificePushS5 | TableName.ActivityPanel | ActivityListDataManager, SeasonManager, WorldPointManager |
| `DataCenter.NpcQABubbleManager` | 4/9 | - | NPCQuestBubbleNeedRefresh | - | - | CityNpcManager, NpcQAManager |
| `DataCenter.NpcQAManager` | 6/11 | MsgDefines.UserNpcQuestion | - | - | - | NpcQABubbleManager, NpcQATemplateManager, RewardManager |
| `DataCenter.OfficialNavigationManager` | 5/9 | MsgDefines.GetOfficialNavigationInfo, MsgDefines.GetOfficialNa... | RefreshActivityRedDot, RefreshOfficialNavigation | - | - | - |
| `DataCenter.OverlordManager` | 29/63 | MsgDefines.OverlordChangeNameMessage, MsgDefines.OverlordCureM... | BuildRedDotRecord, OverlordDataUpdated, OverlordFileState... | UIOverlordChallengePop | - | ActivityListDataManager, ArmyFormationDataManager, ItemDa... |
| `DataCenter.OverlordTemplateManager` | 16/34 | - | - | - | TableName.OverlordCure, TableName.OverlordFile, Tabl... | OverlordManager |
| `DataCenter.PVETriggerGatherTemplateManager` | 1/4 | - | - | - | TableName.PVETriggerGather | - |
| `DataCenter.PaidLotteryManager` | 10/20 | MsgDefines.BeginPaidLotteryRoll, MsgDefines.ClaimPaidLotteryTi... | OnClaimPaidLotteryTicketSucc, OnGetPaidLotteryRollResult,... | - | - | ActivityListDataManager, RewardManager |
| `DataCenter.PayManager` | 22/98 | MsgDefines.ClaimFirstPayReward, MsgDefines.Pay, MsgDefines.Pay... | FirstPayStatusChange, OnPackageInfoUpdated, PlayGamesRewa... | PayPasswordInputPopup, UIFirstPay, UIThirdPaymentShop | - | BuildManager, CreditManager, PhonographManager, RewardMan... |
| `DataCenter.PhonographManager` | 38/124 | MsgDefines.ClaimRecordReward, MsgDefines.ItemUse, MsgDefines.P... | OnReceivePhonographBuff, PaySuccess, PhonographFreeCountU... | UIPhonographBuffDetail, UIPhonographMain, UIPhonogra... | TableName.Phonograph, TableName.StatusTab | BuildManager, GuideManager, ItemData, ItemTemplateManager... |
| `DataCenter.PhotoWallManager` | 4/14 | - | OnSurvivalHeroCollectionReward | - | - | BuildManager, HeroSkinManager, RewardManager |
| `DataCenter.PlayerInfoDataManager` | 6/18 | MsgDefines.GetNewUserInfo | - | - | - | MigrateDataManager, NpcCityManager |
| `DataCenter.PlayerLevelManager` | 7/33 | - | CloseUI, ReceiveLevelReward, UpdatePlayerExp | UIBuildDetails, UILevelUp | TableName.EffectNumDesc | BuildTemplateManager, GuideManager, RewardManager |
| `DataCenter.PlayerMarketManager` | 70/71 | MsgDefines.PlayerMarketGame, MsgDefines.PlayerMarketInfo, MsgD... | PlayerMarketGameResult, PlayerMarketInfoUpdate, PlayerMar... | UIActivityCenterTable | TableName.ActivityPanel | ActivityListDataManager, FestivalAct, ItemData, RewardMan... |
| `DataCenter.PresentManager` | 20/49 | MsgDefines.GetGiftDetail, MsgDefines.GetGiftRewardInfo, MsgDef... | RefreshPresentHistory, RefreshPresentInfo, RefreshPresent... | UIPresentBigShow, UIPresentSend, UIPresentSendTips | TableName.Present, TableName.PresentSP | ItemData, ItemTemplateManager, RewardManager |
| `DataCenter.PrivilegeEffectManager` | 4/15 | - | - | - | - | BuildManager, VIPManager |
| `DataCenter.PushNoticeManager` | 27/37 | MsgDefines.UpdatePushSwitch | NoticePushSettingUpdate, WillEnterForeground | UISetPushNotification | TableName.APS_PUSH | BuildManager, GuideManager, PushUtil |
| `DataCenter.PushUtil` | 1/4 | - | - | - | TableName.APS_PUSH | - |
| `DataCenter.PveAnimationTemplateManager` | 1/2 | - | - | - | TableName.C_Animations | - |
| `DataCenter.PveHeroTemplateManager` | 3/4 | - | - | - | TableName.PveHero, TableName.SU_HeroesLevelUp, Table... | - |
| `DataCenter.PveLevelTemplateManager` | 2/4 | - | - | - | TableName.PVELevelOld, TableName.SU_PveType | - |
| `DataCenter.PveNpcTemplateManager` | 1/4 | - | - | - | TableName.PveNpc | - |
| `DataCenter.PveZombieTemplateManager` | 2/4 | - | - | - | TableName.PVEZombie, TableName.PVEZombieWave | - |
| `DataCenter.QNManager` | 2/9 | MsgDefines.UserGetQuestionnaireList | QuestionnaireRefresh | - | - | - |
| `DataCenter.QuestArrowManager` | 5/15 | - | RefreshGuide, SU_QuestArrowStateChange | MainUI_SU | - | GuideManager |
| `DataCenter.QuestTemplateManager` | 3/8 | - | - | - | TableName.QuestXml, TableName.getValue | BuildTemplateManager |
| `DataCenter.QueueDataManager` | 15/55 | - | AddSpeedSuccess, DeletePastureQueue, GatherResourceItemFi... | UIScienceTab, UISoliderGetTip, UISpeed | - | ArmyTemplateManager, BuildBubbleManager, BuildManager, Bu... |
| `DataCenter.RadarAlarmDataManager` | 6/19 | - | RefreshAlarm | - | - | ActBlackKnightManager, AllianceAlertDataManager, BuildMan... |
| `DataCenter.RadarCenterDataManager` | 40/107 | MsgDefines.DetectEventPveBatch, MsgDefines.DetectInfoGet, MsgD... | UpdateGold, UpdateRadarLevelEventsInfo | UIDetectEvent, UIDetectEventLevelUpgrade, UIPVEDetec... | TableName.Desert | BuildManager, DetectEventTemplateManager, FakeCollectGarb... |
| `DataCenter.RankDataManager` | 14/15 | - | - | - | - | RankData |
| `DataCenter.RecommendShowManager` | 17/29 | - | BuildResourcesStart, RefreshRecommendShow, RefreshUIGuide... | UIFarm, UIGuideHeadTalk | - | BuildManager, GuideManager, QueueDataManager |
| `DataCenter.RedEquipBossRallyDataManager` | 13/22 | MsgDefines.GetAllianceMythicalEquipBossRallyInfo, MsgDefines.I... | RedEquipBossRallyRewardUpdate, RedEquipBossRallyUpdate, R... | - | - | ItemData, ItemTemplateManager, RewardManager |
| `DataCenter.RedEquipmentActivityManager` | 6/20 | - | OnEnterCrossServer, RedEquipActivityStateUpdate | - | - | ActivityListDataManager, AllianceBaseDataManager |
| `DataCenter.RedPacketManager` | 12/29 | MsgDefines.ActivityRedPacketChoose, MsgDefines.GetActivityRedP... | ActivityRedPacketRefresh, ActivityRedPacketRefreshChoose,... | - | TableName.SysRedPacket | AllianceBaseDataManager, RewardManager |
| `DataCenter.ResLackManager` | 4/23 | - | - | - | TableName.Res_Lack_Tips | BuildManager |
| `DataCenter.RescueDogManager` | 4/17 | MsgDefines.RescueDogSubmitItem | Barrel_RescueDogRemoveHero, RefreshRescueDog | - | - | GuideManager, HeroDataManager, RewardManager |
| `DataCenter.ResourceItemDataManager` | 12/33 | MsgDefines.UseResItem, MsgDefines.UserGetAllResourceItem | OnGoodsRedState, RefreshResourceItem | UICapacityFull | TableName.Aps_Resource_Item | BagGridDataManager, BattleLevel |
| `DataCenter.ResourceManager` | 5/7 | - | - | - | - | BuildManager, ResourceTemplateManager |
| `DataCenter.ResourceTemplateManager` | 1/2 | - | - | - | TableName.Resource | - |
| `DataCenter.RewardManager` | 29/49 | MsgDefines.RealRewardInfo | CloseUI, GetRealRewardInfo, ResourceUpdated | UICarnivalLuckySpin, UICarnivalSendWorld, UIGetRewar... | TableName.NightLunarLightCard, TableName.StatusTab | ActGiftBoxData, BuildManager, GuideManager, ItemData, Ite... |
| `DataCenter.RubyStoreManager` | 17/18 | MsgDefines.UIShopBuy | OnCommonShopRedChange, RubyStoreLicenseExpired, RubyStore... | - | - | BuildBubbleManager, CarnivalMomentManager, ItemData, Ruby... |
| `DataCenter.SUPveLevelDataManager` | 3/12 | - | - | - | TableName.Land_Lock_Property | LandLockManager, PveLevelTemplateManager, SU_MainCityRole... |
| `DataCenter.SUSidebarTemplateManager` | 1/4 | - | - | - | TableName.Sidebar | - |
| `DataCenter.SUSidebarTypeTemplateManager` | 1/4 | - | - | - | TableName.SidebarType | - |
| `DataCenter.SU_EventSystem` | 4/25 | MsgDefines.SU_UpdateEvent | - | - | TableName.SU_C_Event | LandLockManager, PveLevelTemplateManager |
| `DataCenter.SU_MainCityRoleTeam` | 6/11 | MsgDefines.SU_SaveMainCityRoleTeam | LWUpdateMainCityRoleTeam | - | - | HeroDataManager |
| `DataCenter.SU_MistressEffectManager` | 6/20 | MsgDefines.UseHeroEffectSkill | SU_RefreshMistressEffect | UICapacityFull | - | ArmyManager, ItemTemplateManager, MistressLvTemplateManag... |
| `DataCenter.SV_MapItemInfoManager` | 6/15 | - | - | - | TableName.PVETrigger | BattleLevel, PveLevelTemplateManager |
| `DataCenter.ScienceDataManager` | 1/6 | - | - | - | - | ArmyManager |
| `DataCenter.ScienceManager` | 22/26 | MsgDefines.QueueFinish | UPDATE_SCIENCE_DATA, UpdateGold | - | TableName.EffectNumDesc | BuildTemplateManager, HeroDataManager, ItemData, QueueDat... |
| `DataCenter.ScienceTemplateManager` | 8/17 | - | - | - | TableName.APSScienceTab, TableName.ScienceNew | BuildManager, ScienceDataManager, ScienceManager |
| `DataCenter.SearchLodManager` | 6/16 | - | ChangeCameraLod | UIMainMiniMap | - | - |
| `DataCenter.SeasonActivityPanelTemplateM...` | 2/6 | - | - | - | TableName.SeasonActivityPanel | SeasonDataManager |
| `DataCenter.SeasonConfigManager` | 8/19 | - | - | - | TableName.SeasonConfig | - |
| `DataCenter.SeasonDataManager` | 91/92 | MsgDefines.GetSeasonGroupServerInfo, MsgDefines.SeasonBalanceP... | DesertForceRefresh | - | TableName.Desert, TableName.SeasonDialog, TableName.... | AccountManager, ActivityListDataManager, AllianceBaseData... |
| `DataCenter.SeasonGroupManager` | 12/13 | - | - | - | TableName.SeasonGroup | SeasonGroup |
| `DataCenter.SeasonPrologueManager` | 10/13 | MsgDefines.FindMainBuildInitPosition | REGET_MAIN_POSITION, UINoInput | UIVideoPlayer, UI_VideoPlayer | - | GuideManager, SeasonDataManager, WorldPointManager |
| `DataCenter.SeasonWeekManager` | 7/12 | MsgDefines.SeasonWeekBuffGetInfo, MsgDefines.SeasonWeekBuffRec... | SeasonWeekUpdate | - | - | RewardManager, SeasonDataManager |
| `DataCenter.SegmentedHealthBarManager` | 3/10 | - | ShowSegmentedHealthBarHead | - | - | WorldPointManager |
| `DataCenter.ShareMsgManager` | 14/15 | MsgDefines.ShareMsg, MsgDefines.ShareMsgSend | RefreshAssistanceHeroChatCell | - | - | - |
| `DataCenter.SidebarManager` | 3/12 | - | - | - | - | AllianceScienceDataManager, BuildManager, SUSidebarTempla... |
| `DataCenter.SimpleModeManager` | 18/71 | - | CombatModeChange, HideTroopHead, HideTroopName, OnEnterWo... | - | - | VolcanoWarManager, WorldMarchDataManager |
| `DataCenter.SmallPeopleDataManager` | 9/21 | MsgDefines.SmallPeopleUpgradeRank, MsgDefines.SurvivalVisitorR... | SmallPeopleAddNew, SmallPeopleDelete | - | TableName.HeroAppearance, TableName.LwBaseVisitorEvent | RewardManager |
| `DataCenter.SnowManManager` | 22/52 | MsgDefines.GetSnowManActInfo, MsgDefines.SnowManAddExp, MsgDef... | OpenUI, RefreshActivityRedDot, SnowManUpdateRedCount, Sno... | UIWorldPoint | TableName.SnowMan | AllianceBaseDataManager, RewardManager |
| `DataCenter.StatusManager` | 9/19 | - | MSG_ITME_STATUS_TIME_CHANGE | - | TableName.StatusTab | - |
| `DataCenter.SteelAndRedEquipManager` | 11/28 | - | SteelAndRedEquipDataRefresh, SteelAndRedEquipOneUpdate, S... | - | - | CarChipActivityManager, RewardManager, SteelAndRedEquipTe... |
| `DataCenter.SteelAndRedEquipTemplateManager` | 2/9 | - | - | - | TableName.Trends, TableName.TrendsFunction | - |
| `DataCenter.StorageShopManager` | 17/41 | MsgDefines.ShareCdCheck, MsgDefines.StorageShopBuyGoods, MsgDe... | RefreshStorageShopHistory, StorageShopAddGoods, StorageSh... | - | - | ResourceItemDataManager |
| `DataCenter.StoryManager` | 34/74 | MsgDefines.GetStoryInfo, MsgDefines.GetStoryRank, MsgDefines.G... | ChangeStoryScene, MainLvUp, StoryGetInfo, StoryGetRank, S... | - | - | BuildManager, LandLockManager, PushNoticeManager, PveLeve... |
| `DataCenter.SweepManager` | 25/75 | MsgDefines.SweepDetail, MsgDefines.SweepExecute, MsgDefines.Sw... | SweepDetailUpdate, SweepExecuteResult, SweepInfoUpdate, S... | - | - | ActMonsterTowerData, AllianceBaseDataManager, AllianceGif... |
| `DataCenter.TalentDataManager` | 13/23 | MsgDefines.ChooseBaseTalent, MsgDefines.RefreshBaseTalent, Msg... | TalentDataChange, UpdateGold | - | TableName.PlayerLevel | BattleLevel, BuildManager, TalentTemplateManager |
| `DataCenter.TalkTaskDataManager` | 23/43 | MsgDefines.DetectEventRewardReceive, MsgDefines.SU_DialogStep | BuildLevelUp, DetectInfoChange, DetectNpcGetReward, TalkT... | - | TableName.Option_Config | BuildBubbleManager, BuildManager, GuideManager, MainCityA... |
| `DataCenter.TaskManager` | 40/86 | MsgDefines.GetTaskNormalRewardInfo | MainTaskSuccess, OnOneActivityOverviewRedChange, OnRallyB... | UIDailyActivity | - | ActivityListDataManager, BattleLevel, BuildManager, Chapt... |
| `DataCenter.ThanksGivingCatchHitManager` | 19/47 | MsgDefines.GetAllianceTreasure, MsgDefines.TurkeyHuntAllianceL... | PlayHitTurkeyAnimation, TurkeyGaming, UpdateHitTurkeyAct,... | UIHitTurkeyNotice | - | AllianceBaseDataManager |
| `DataCenter.ThanksgivingStarInfo` | 10/11 | - | - | UIPositionShare | - | ActivityListDataManager, Thanksgiving |
| `DataCenter.ThroneActManager` | 19/44 | - | RefreshActivityRedDot, RefreshThroneEntrance, ThroneActUp... | ThronePopupView | TableName.ActivityPanel | ActivityListDataManager, BuildManager, GovernmentManager |
| `DataCenter.TowerClimbingManager` | 7/31 | - | - | UIPVETowerClimbJumpReward | TableName.StoryMap | ArmyManager, HeroDataManager, PveLevelTemplateManager, Re... |
| `DataCenter.TradeCenterDataManager` | 2/15 | - | - | - | - | BuildManager |
| `DataCenter.TroopActionManager` | 19/39 | - | END_SEARCH, MarchEndWithReward, ShowTroopAction | UIDetectEvent | - | ArmyFormationDataManager, BuildManager, TroopActionTempla... |
| `DataCenter.TroopActionTemplateManager` | 1/4 | - | - | - | TableName.TroopAction | - |
| `DataCenter.UINoInputManager` | 6/10 | - | UINoInput | UIMigrating, UIMoving, UISceneNoInput | - | - |
| `DataCenter.UIPopWindowManager` | 12/24 | - | PveLevelEnter | UIBuildUpUnlock, UIMainAccountBind, UIRedenvelopeSend | - | GuideManager |
| `DataCenter.UavDialogueTemplateManager` | 1/3 | - | - | - | TableName.UavDialogue | - |
| `DataCenter.VIPManager` | 42/43 | MsgDefines.VipAddLoginScore, MsgDefines.VipGetEveryDayReward, ... | VipRefreshFree | - | - | BuildManager, CommonShopManager, LandLockManager, RewardM... |
| `DataCenter.VIPTemplateManager` | 14/15 | - | - | - | TableName.EffectNumDesc, TableName.VipTemp | VIPData |
| `DataCenter.ValentineDecorationManager` | 8/27 | MsgDefines.ValentineFeed, MsgDefines.ValentineGetFeedReward, M... | ValentineRewardShow, ValentineTipsShow, WorldBuildSelfAni... | UIFoxHello, UIGivingRoses2Castle | - | DecorationDataManager, RewardManager, WorldPointManager |
| `DataCenter.VipRoomAnnouncementManager` | 27/28 | ChatMsgDefines.RoomGroupDelNotice, ChatMsgDefines.RoomGroupLik... | ChatAllianceAnnouncementAdd, ChatAllianceAnnouncementDel,... | - | - | AllianceAnnouncement |
| `DataCenter.VolcanoIconNameManager` | 4/13 | - | OnEnterWorld | - | - | VolcanoWarManager, WorldPointManager |
| `DataCenter.VolcanoWarManager` | 75/163 | MsgDefines.VolcanoBattleAllianceAllocateRewardRecord, MsgDefin... | VolcanoBattleCampScoreChange, VolcanoBattleCommandChangeR... | UIActivityRewardTip, UIAllianceMarkTip | TableName.EffectNumDesc, TableName.GatherResource, T... | ActivityListDataManager, CrossWonderManager, GovernmentMa... |
| `DataCenter.WeekCardManager` | 6/17 | MsgDefines.GetWeekCardList, MsgDefines.SetWeekCardCustomRewards | OnWeekCardCustomRewardUpdate, OnWeekCardInfoChange, OnWee... | - | - | - |
| `DataCenter.WorldAllianceCityDataManager` | 3/7 | - | - | - | TableName.WorldCity | AllianceBaseDataManager, AllianceDeclareWarManager |
| `DataCenter.WorldAllianceCityRecordManager` | 4/11 | MsgDefines.GetAllianceCityRecordRedPoint | RefreshActivityRedDot, WorldAllianceCityRecordUpdate | - | - | - |
| `DataCenter.WorldAllianceFortressDataMan...` | 47/48 | MsgDefines.FortressCancelSignUp, MsgDefines.FortressRewardMemb... | WorldFortressActivityUpdate, WorldFortressOwnerInfoChange... | - | TableName.WorldFortressRewardGroup | ActivityListDataManager, AllianceBaseDataManager |
| `DataCenter.WorldAtkSeasonAllianceBuildM...` | 2/8 | - | CheckCanAtkSeasonBuild | - | - | - |
| `DataCenter.WorldFavoDataManager` | 21/107 | MsgDefines.WorldAddAllianceMark, MsgDefines.WorldAddWorldMark,... | AllianceRallyRedPoint, CheckDragonMark, PveLevelEnter, Up... | UIAllianceMarkTip | - | UIPopWindowManager |
| `DataCenter.WorldHotNewsManager` | 9/37 | MsgDefines.HotNewsLandInfo, MsgDefines.HotNewsRankInfo | ChangeCameraLod, ChatNewsUpdate, RefreshHotPoint, Refresh... | UIHotNewsPointDetail | - | - |
| `DataCenter.WorldMissileManager` | 11/53 | MsgDefines.WorldMissileInfo | WorldMissileInfoRefresh | UIDeclareWarCountDownTitle | TableName.StateSkill | AllianceSkillTemplateManager, GloryManager, WorldPointMan... |
| `DataCenter.WorldMyMarchDataManager` | 2/12 | MsgDefines.WorldGetMarchInfos | - | - | - | ArmyFormationDataManager |
| `DataCenter.WorldNewsDataManager` | 11/31 | MsgDefines.GetWorldNewInfo | AttackerInfoUpdate, OnEnterWorld, UpdateWorldZoneNews, Wo... | - | - | BuildManager |
| `DataCenter.WorldNoticeManager` | 13/33 | MsgDefines.GetNoticeList, MsgDefines.ReadNotice, MsgDefines.Re... | ChangeShowTranslatedNotice, GetNoticeList, RefreshNotice | UIActivityNoticeTip | - | ActivityListDataManager, RewardManager, UIPopWindowManager |
| `DataCenter.WorldSeasonObjectManager` | 8/27 | MsgDefines.GetPlaceObjects | PUSH_INIT_OK | - | TableName.SeasonObject | BirthPointTemplateManager |
| `DataCenter.WorldShoutManager` | 17/76 | MsgDefines.GetBroadcastSticky, MsgDefines.SendBroadcastMsg, Ms... | TOP_BROADCAST_UPDATE, WORLD_SHOUT_HIDE_CARD, WORLD_SHOUT_... | UIWorldShoutTips | - | ActivityListDataManager, BuildManager, GovernmentManager,... |
| `DataCenter.WorldTrendManager` | 10/21 | MsgDefines.ServerTrendsInfo, MsgDefines.ServerTrendsRank, MsgD... | WorldTrendRedUpdate, WorldTrendRefresh, WorldTrendRefresh... | - | - | BuildManager, RewardManager, SteelAndRedEquipManager, Ste... |
| `DataCenter.WoundedCompensateData` | 3/5 | - | - | - | - | RewardManager |
| `DataCenter.XiaoRenRankTemplateManager` | 1/5 | - | - | - | TableName.XiaoRenRank | - |
| `SlgDataCenter.DefendFormationManager` | 23/71 | MsgDefines.GetDefenseHero | DefendFormationNewDefendingUpdate, DefendFormationNewRedD... | - | - | ArmyFormationDataManager, ArmyManager, BuildManager, Buil... |
| `_G.BuildingUtils` | 40/68 | - | - | - | - | BaubleManager, BoardManager, BuildManager, BuildTemplateM... |
| `_G.CommonUtil` | 39/105 | MsgDefines.GoldGetUpdate, MsgDefines.UserAgreeTos | Disconnect | UIActivityRewardTip, UIDeleteAccountNoticeNew, UIThi... | TableName.LandLock | ActDragonManager, ActTradePostManager, ActivityListDataMa... |
| `_G.FormationUtil` | 10/13 | - | - | - | TableName.WorldCity | ArmyFormationDataManager, BuildTemplateManager, MonthCard... |
| `_G.GiftPackageData` | 22/119 | MsgDefines.ClaimFirstPayReward, MsgDefines.ExchangeInfo, MsgDe... | CustomChoiceItem, FreeWeeklyPackage, OnPackageInfoUpdated... | UIFirstPay, UIPiggyBank | - | BuildManager, GuideManager, HeroDataManager, LandLockMana... |
| `_G.GoToUtil` | 118/142 | MsgDefines.FindDesertPoint, MsgDefines.FindEnemyPoint, MsgDefi... | GOTO_SCIENCE, GoTroopListShow, MainToDailyAct, MainToWorl... | MainUI_SU, UIActivityCenterTable, UIAircraftMain, UI... | TableName.Desert, TableName.TradePost | AccountManager, ActTradePostManager, ActivityListDataMana... |
| `_G.HeroUtils` | 86/214 | - | - | UIHeroInfo | TableName.BattleBuff, TableName.CampEffect_B, TableN... | ArmyFormationDataManager, BattleLevel, BaubleLibraryManag... |
| `_G.LuaEntry` | 9/20 | - | DidEnterBackground, OnCameraEnterIdle, WillEnterForeground | UIChatNew, UICommonMessageBar | - | DeeplinkManager, DeleteAll, LWBattleManager, MailFacade, ... |
| `_G.MarchUtil` | 109/170 | MsgDefines.AllianceWarCancel, MsgDefines.AssistanceTeamRetreat... | MonthCardFourthGuide, RefreshUIWorldPointView, ShowMainUI... | UIAllianceIntro, UIFormationLackPower, UIFormationSe... | TableName.Aps_Resource_Item, TableName.Desert, Table... | ActDragonManager, ActIceCaveManager, AllianceBuildingConf... |
| `_G.PveActorMgr` | 65/185 | MsgDefines.BeginPvpCaveFight, MsgDefines.GetCrossArenaUserEffe... | OnEmBattleHeroChanged, PVEBattleSetLeftBuffData, PVE_Line... | UIBarrelHeroBottomInfo, UIPVEHeroAppear, UIPVEHeroBo... | TableName.Army_B, TableName.Car_Show_Barrel, TableNa... | BattleLevel, CrossArenaManager, GuideManager, HeroDataMan... |
| `_G.PveUtil` | 12/37 | - | - | MainUI_SU, UIHeroList, UISearch | TableName.Monster | ActFirstChargeData, BattleLevel, BuildManager, ChapterTas... |
| `_G.SceneManager` | 11/46 | MsgDefines.LeaveWorld | SU_ChangeScreen, SU_MainUIReInit, SceneChanged | MainUI_SU | - | AccountManager, BattleLevel, BuildManager, PveLevelTempla... |
| `_G.SceneUtils` | 7/45 | - | - | - | TableName.WorldCity | ActIceCaveManager, BirthPointTemplateManager, BuildManage... |
| `_G.UIManager` | 10/109 | - | BeforeCloseUI, CloseUI, OnKeyCodeEscape, OpenUI | UIAlarm, UIPVEScene, UIParkourBattleLose, tostring | - | GuideManager |
| `_G.UIUtil` | 127/230 | ChatMsgDefines.==, ChatMsgDefines.do, MsgDefines.==, MsgDefine... | ==, ClickAny, ClickFarmBuildHide, HideMarchTip, RefreshCh... | DigTreasureGift, MainUI_SU, TryGetStr, UIActivityCen... | TableName.EffectNumDesc, TableName.GatherResource, T... | ActDispatchTaskDataManager, ActivityListDataManager, Alli... |

## 7. Native Unity C# Engine Atlas (98 Loaded Assemblies, 3,772 Reflected Types)

### 7.1 Loaded C# Assemblies Overview (Top 35 by Type Count)
| Assembly Name | Total Types | Deep Reflected in Megamind |
|---|---:|---|
| `Assembly-CSharp` | 3,665 | **YES (Full Methods/Fields)** |
| `mscorlib` | 2,047 | Inventory only |
| `SixLabors.ImageSharp` | 1,496 | Inventory only |
| `System` | 911 | Inventory only |
| `System.Xml` | 910 | Inventory only |
| `UnityEngine.CoreModule` | 858 | Inventory only |
| `UnityEngine.UIElementsModule` | 783 | Inventory only |
| `System.Core` | 760 | Inventory only |
| `Unity.Zendesk` | 746 | Inventory only |
| `Unity.InputSystem` | 647 | Inventory only |
| `Unity.Zendesk.MessagingCore` | 613 | Inventory only |
| `Unity.RenderPipelines.Universal.Runtime` | 528 | Inventory only |
| `Newtonsoft.Json` | 495 | Inventory only |
| `Unity.RenderPipelines.Core.Runtime` | 407 | Inventory only |
| `com.Tivadar.Best.HTTP` | 392 | **YES (Full Methods/Fields)** |
| `zxing.unity` | 377 | Inventory only |
| `Unity.Collections` | 345 | Inventory only |
| `TheDesk.PlayerSupport` | 309 | Inventory only |
| `Cinemachine` | 237 | Inventory only |
| `System.Data` | 231 | Inventory only |
| `MeshBakerCore` | 222 | Inventory only |
| `UnityEngine.UI` | 203 | Inventory only |
| `DOTween` | 190 | Inventory only |
| `Unity.TextMeshPro` | 172 | Inventory only |
| `Vuplex.WebView` | 159 | **YES (Full Methods/Fields)** |
| `spine-unity` | 122 | Inventory only |
| `Unity.Timeline` | 120 | Inventory only |
| `spine-csharp` | 118 | Inventory only |
| `UniWebView-CSharp` | 104 | **YES (Full Methods/Fields)** |
| `Mono.Security` | 103 | Inventory only |
| `Unity.Mathematics` | 97 | Inventory only |
| `Unity.Burst` | 96 | Inventory only |
| `Assembly-CSharp-firstpass` | 94 | **YES (Full Methods/Fields)** |
| `UnityEngine.ParticleSystemModule` | 85 | Inventory only |
| `NTextCat` | 83 | Inventory only |

### 7.2 `Assembly-CSharp` Namespace Breakdown (3,177 Clean Types across 87 Namespaces)
| C# Namespace | Types | Total Methods | Representative Classes |
|---|---:|---:|---|
| `(Global / Root)` | 949 | 4,661 | `AES`, `AESHelper`, `APSDamageEffectType`, `APSSpecialUnitType`, `AdjustmentScreenSize`, `AesEncryptor`, `AndroidMemoryTelemetr... |
| `XLua` | 650 | 2,208 | `AdditionalPropertiesAttribute`, `BlackListAttribute`, `CSharpCallLuaAttribute`, `CopyByValue`, `CopyByValue_Gen`, `DelegateBri... |
| `XLua.CSObjectWrap` | 552 | 9,886 | `AnimationCurveListWrap`, `ApplicationLaunchWrap`, `AutoAdjustLodWrap`, `AutoAdjustScreenPosWrap`, `AutoDoMovePosWrap`, `AutoFa... |
| `Protobuf` | 95 | 712 | `AllFightLost`, `AllReportReward`, `AllianceBuildArmyResult`, `AllianceBuildingPointInfo`, `AllianceCityArmyResult`, `AllianceC... |
| `Google.Protobuf.Reflection` | 83 | 513 | `CustomOptions`, `DescriptorBase`, `DescriptorDeclaration`, `DescriptorPool`, `DescriptorProto`, `Types`, `ExtensionRange`, `Re... |
| `Google.Protobuf` | 53 | 420 | `ByteArray`, `ByteString`, `Unsafe`, `CodedInputStream`, `CodedOutputStream`, `OutOfSpaceException`, `Extension`, `ExtensionReg... |
| `Pinball` | 49 | 113 | `PinballAdaptiveSearch`, `PinballAdaptiveSearchSettings`, `PinballBakedEvent`, `PinballBakedTrajectory`, `PinballBallBinding`, ... |
| `VEngine` | 46 | 290 | `AllBundledAsset`, `AllBundledDependencies`, `Asset`, `AssetInfo`, `Assets`, `BuiltinManifestFile`, `Bundle`, `BundleInfo`, `Bu... |
| `Google.Protobuf.WellKnownTypes` | 44 | 265 | `Any`, `AnyReflection`, `Api`, `ApiReflection`, `BoolValue`, `BytesValue`, `DoubleValue`, `Duration`, `DurationReflection`, `Em... |
| `usky` | 41 | 134 | `AmbientGradientSettings`, `CameraOrbit2`, `DayNightCycleSettings`, `DayTime`, `DefaultTimelineSettings`, `DemoGUI`, `DepthSamp... |
| `EPOOutline` | 38 | 89 | `BlitUtility`, `MeshSetupResult`, `Vertex`, `BlurType`, `BoundsMode`, `BufferSizeMode`, `CameraUtility`, `ColorMask`, `ComplexM... |
| `RealisticEyeMovements` | 36 | 197 | `BlinkingComponent`, `BlinkState`, `ControlData`, `BlendshapesConfig`, `BlendshapesConfigForExport`, `ControlDataForExport`, `E... |
| `BitBenderGames` | 34 | 173 | `AutoScrollDampMode`, `FocusCameraOnItem`, `MobilePickingController`, `MobileTouchCamera`, `State`, `ZoomParam`, `MobileTouchCa... |
| `FIMSpace.FProceduralAnimation` | 28 | 190 | `Demo_Ragd_BonesPoseRotator`, `BoneController`, `ELimit`, `RagdollAnimator`, `RagdollAutoDestroy`, `RagdollAnimatorGeneratorMet... |
| `LitJson` | 24 | 221 | `ArrayMetadata`, `Condition`, `ExporterFunc`, `ExporterFunc`1`, `FsmContext`, `IJsonWrapper`, `ImporterFunc`, `ImporterFunc`2`,... |
| `GameKit.Base` | 23 | 172 | `ComponentExtensions`, `GameObjectPool`, `GameObjectPoolExtensions`, `INetProxy`, `ItemWrap`, `NetProxy`, `ProxyStatus`, `Secur... |
| `RTLTMPro` | 20 | 56 | `ArabicGeneralLetters`, `ArabicIsolatedLetters`, `Char32Utils`, `EnglishNumbers`, `FarsiNumbers`, `FastStringBuilder`, `GlyphFi... |
| `SDK` | 19 | 69 | `ITikTokBusiness`, `TTCurrency`, `TTEventName`, `TikTokAdRevenueEvent`, `TikTokAddToCartEvent`, `TikTokAddToWishlistEvent`, `Ti... |
| `SuperScrollView` | 18 | 161 | `ClickEventListener`, `ItemCornerEnum`, `ItemLazyAssetStatus`, `ItemLazyPool`, `ItemPool`, `ItemPosMgr`, `ItemPrefabConfData`, ... |
| `EnhancedUI.EnhancedScroller` | 17 | 88 | `CellViewInstantiated`, `CellViewReused`, `CellViewVisibilityChangedDelegate`, `CellViewWillRecycleDelegate`, `EnhancedScroller... |
| `RVO_DOTS` | 17 | 96 | `Agent`, `AgentPair`, `AgentPtr`, `AgentTreeNode`, `FloatPair`, `KdTree`, `Line`, `Obstacle`, `ObstaclePair`, `ObstaclePtr` |
| `FIMSpace.RagdollAnimatorDemo` | 15 | 44 | `Demo_Ragd_AdaptFallBlend`, `Demo_Ragd_CollisionLayers`, `Demo_Ragd_DamageExample`, `Demo_Ragd_DelayedImpact`, `Demo_Ragd_Faint... |
| `Sfs2X.Core.Sockets` | 14 | 69 | `AsyncTCPSocketLayer`, `BaseSocketLayer`, `States`, `Transitions`, `BestHttpWebSocketLayer`, `ConnectionDelegate`, `ISocketLaye... |
| `UnityEngine.UI` | 14 | 71 | `ArabicImageMirror`, `MirrorType`, `Button_LongPress`, `Empty4Raycast`, `Gradient`, `GraphicConnector`, `GraphicConnectorExtens... |
| `Google.Protobuf.Collections` | 13 | 104 | `Lists`, `MapField`2`, `Codec`, `MessageAdapter`, `DictionaryEnumerator`, `MapView`1`, `ProtobufEqualityComparers`, `BitwiseDou... |
| `Sfs2X.Bitswarm` | 12 | 51 | `BaseController`, `BitSwarmClient`, `BitSwarmEvent`, `ConnectionModes`, `IController`, `IMessage`, `ISocketClient`, `IoHandler`... |
| `Coffee.UIParticleExtensions` | 11 | 34 | `BakingCamera`, `CombineInstanceArrayPool`, `CombineInstanceEx`, `ListExtensions`, `MeshExtensions`, `MeshHelper`, `MeshPool`, ... |
| `RVO` | 11 | 93 | `Agent`, `KdTree`, `AgentTreeNode`, `FloatPair`, `ObstacleTreeNode`, `Line`, `Obstacle`, `RVOMath`, `Simulator`, `Worker` |
| `XLua.Cast` | 11 | 0 | `Any`1`, `Byte`, `Char`, `Float`, `Int16`, `Int32`, `Int64`, `SByte`, `UInt16`, `UInt32` |
| `Sfs2X.Core` | 10 | 34 | `BaseEvent`, `EventDispatcher`, `EventListenerDelegate`, `ExtensionEvent`, `IDispatchable`, `IPacketEncrypter`, `PacketHeader`,... |
| `Sfs2X.Entities.Data` | 10 | 267 | `ISFSArray`, `ISFSObject`, `SFSArray`, `SFSArrayEnumerator`, `SFSArrayLite`, `SFSDataType`, `SFSDataWrapper`, `SFSObject`, `SFS... |
| `Sfs2X.Util` | 10 | 57 | `ApsZstdV1`, `ArrayPoolHelper`, `ByteArray`, `CompressionAlgorithm`, `ByteArrayPool`, `ClientDisconnectionReason`, `Compression... |
| `TroopLineDrawMesh` | 10 | 37 | `Entry`, `Line`, `Point`, `Segment`, `Snapshot`, `TroopLineBackend`, `EntryComparer`, `TroopLineBatches`, `Batch`, `TroopLineGe... |
| `LW.CountBattle` | 9 | 57 | `Box`, `Circle`, `Shape`, `SteerCollider`, `SteerDisplay`, `SyncState`, `SteerGroup`, `SpawnTask`, `SteerUnit` |
| `Main.Scripts.Scene.PVE` | 9 | 32 | `FIGridManager`, `Node`, `FallSrcTargetDataScriptable`, `FallSrcTargetPair`, `PathGridCoord`, `PveStaticDebug`, `RectArea`, `Re... |
| `Sfs2X.Requests` | 9 | 15 | `BaseRequest`, `ExtensionRequest`, `HandshakeRequest`, `IRequest`, `LoginRequest`, `LogoutRequest`, `ManualDisconnectionRequest... |
| `BitBenderGames.CameraState` | 8 | 41 | `CameraStateBase`, `CameraStateFocus`, `CameraStateFollow`, `CameraStateFreeLook`, `CameraStateIdle`, `CameraStateMoveTo`, `Mov... |
| `CurveRoute` | 8 | 54 | `CRConst`, `CRGraphData`, `PointData`, `CRPath`, `CRPoint`, `CRPointManager`, `Node`, `CRSegment` |
| `GameOldBoy.Rendering` | 8 | 16 | `RenderingMode`, `TAA`, `HaltonSequence`, `TAACameraPass`, `TAAPass`, `TAATextureSwap`, `TAAComponent`, `TAAQuality` |
| `Mopsicus.Plugins` | 8 | 51 | `IPlugin`, `MobileInput`, `ShowDelegate`, `MobileInputField`, `MobileInputConfig`, `ReturnKeyType`, `MobileInputReceiver`, `Plu... |
| `FIMSpace` | 7 | 120 | `FAnimatorMethods`, `FDebug_PerformanceTest`, `FEngineering`, `FLogicMethods`, `FStringMethods`, `FTransformMethods`, `FVectorM... |
| `ArabicSupport` | 6 | 19 | `ArabicFixer`, `ArabicFixerSpec`, `GeneralArabicLetters`, `IsolatedArabicLetters`, `ArabicLineFixer`, `UGUITextLines` |
| `GFX.Particle` | 6 | 36 | `ManagedEffect`, `ParticleEffectIO`, `ParticleEffectImportanceGroups`, `ParticleEffectQualityControl`, `ParticleEffectQualityMa... |
| `GameFramework` | 6 | 19 | `FileWriter`, `GameFrameworkEventArgs`, `GameFrameworkException`, `Log`, `LogFile`, `LogLevel` |
| `Main.Scripts.Network` | 6 | 36 | `FutureManager`, `LatencyReporter`, `LatencyRecord`, `MessageSendInfo`, `NetProxyStatus`, `TrafficRecord` |
| `Coffee.UIExtensions` | 5 | 36 | `AnimatableProperty`, `ShaderPropertyType`, `UIParticle`, `UIParticleUpdater`, `UITrail` |
| `Experiment.Steer` | 5 | 25 | `SteerManager`, `Box`, `Circle`, `Shape`, `Unit` |
| `LuaPerfect` | 5 | 25 | `ClassInfoItem`, `ObjectCache`, `ObjectFormater`, `ObjectItem`, `ObjectRef` |
| `Sfs2X.Protocol.Serialization` | 5 | 133 | `DefaultObjectDumpFormatter`, `DefaultSFSDataSerializer`, `ISFSDataSerializer`, `SerializableSFSType`, `UnrealDefaultSFSDataSer... |
| `UnityEngine.Rendering.Universal` | 5 | 12 | `DOFUrp`, `DOFSettings`, `DepthMethod`, `DOFUrpPass`, `PlanarURP` |
| `UnityGameFramework.Runtime` | 5 | 17 | `BaseComponent`, `EventComponent`, `ObjectPool`1`, `EventPoolMode`, `GameFrameworkComponent` |
| `XLua.TemplateEngine` | 5 | 10 | `Chunk`, `LuaTemplate`, `Parser`, `TemplateFormatException`, `TokenType` |
| `FIMSpace.Basics` | 4 | 21 | `Demo_Ragd_BlendLegsOnHit`, `Demo_Ragd_UpdateSkinnedBounds`, `FAnimationClips`, `FAnimator` |
| `NiceJson` | 4 | 38 | `JsonArray`, `JsonBasic`, `JsonNode`, `JsonObject` |
| `PowerUtilities` | 4 | 10 | `MaterialGroupTools`, `GroupInfo`, `PresetBlendMode`, `PresetBlendModeTools` |
| `FIMSpace.AnimationTools` | 3 | 10 | `SkeletonRecognize`, `EWhatIsIt`, `SkeletonInfo` |
| `MapEditor` | 3 | 10 | `MapEditorUtil`, `PveSceneHeroPosOffset`, `SceneConfigEditor` |
| `Sfs2X.Controllers` | 3 | 13 | `ExtensionController`, `RequestDelegate`, `SystemController` |
| `Sfs2X.Exceptions` | 3 | 0 | `SFSCodecError`, `SFSError`, `SFSValidationError` |
| `Sfs2X.FSM` | 3 | 14 | `FSMState`, `FiniteStateMachine`, `OnStateChangeDelegate` |
| `Sfs2X.Logging` | 3 | 10 | `LogLevel`, `Logger`, `LoggerEvent` |
| `Testing` | 3 | 16 | `BulletTestManager`, `BulletInfoTest`, `BulletTestTool` |
| `Unity.IL2CPP.CompilerServices` | 3 | 0 | `Il2CppEagerStaticClassConstructionAttribute`, `Il2CppSetOptionAttribute`, `Option` |
| `World.LFTerrain` | 3 | 0 | `LowTerrain`, `TerrainDataScriptableObject`, `TileData` |
| `XLua.LuaDLL` | 3 | 66 | `Lua`, `UnityLogger`, `lua_CSFunction` |
| `Balaso` | 2 | 4 | `AppTrackingTransparency`, `AuthorizationStatus` |
| `DevTools` | 2 | 5 | `Description`, `GameObjectDescriptions` |
| `Framework.Utils.UnityEx` | 2 | 14 | `ScreenToucher`, `TouchInfo` |
| `GEgineRunTime` | 2 | 4 | `TouchObjectAnim`, `WorldTerrainUVScaleScriptableObject` |
| `Google.Protobuf.Compatibility` | 2 | 5 | `PropertyInfoExtensions`, `TypeExtensions` |
| `Main.Scripts.Application.LoadingState` | 2 | 4 | `HttpRequest`, `WebRequestCertificateHandler` |
| `Main.Scripts.Framework` | 2 | 2 | `ArabAutoFlip`, `ArabLayoutSwap` |
| `Main.Scripts.UI` | 2 | 8 | `ClampedContentSizeFitter`, `UIButtonCommonAnim` |
| `RockEngine` | 2 | 8 | `SkyRenderFeature`, `SkyRenderPass` |
| `UnityGameFramework.SDK` | 2 | 29 | `AnalyticsEvent`, `HelpManager` |
| `VolumetricFogAndMist2` | 2 | 7 | `VolumetricFog`, `VolumetricFogShape` |
| `EnhancedUI` | 1 | 12 | `SmallList`1` |
| `FIMSpace.FEditor` | 1 | 8 | `FGUI_Finders` |
| `GameFramework.Localization` | 1 | 0 | `Language` |
| `LuaScriptInterface` | 1 | 3 | `UIManager` |
| `Main.Scripts.Common.UIExtension` | 1 | 2 | `ProfilerHelper` |
| `Main.Scripts.Scene` | 1 | 0 | `TerrainSetting` |
| `NexgenDragon` | 1 | 3 | `SceneColorToShader` |
| `Sfs2X` | 1 | 37 | `SmartFox` |
| `Sfs2X.Protocol` | 1 | 3 | `IProtocolCodec` |
| `usky.Internal` | 1 | 45 | `uSkyInternal` |
| `usky.PrecomputeUtil` | 1 | 5 | `uSkyPrecomputeUtil` |

### 7.3 Key `Assembly-CSharp` Engine, Network, xLua, UI & PVE Classes (1383 Highlighted; All 3,177 Queryable via `megamind_query.py csharp`)
| C# Type | Kind / Base | Methods | Fields | Sample Methods |
|---|---|---:|---:|---|
| `AssetBundleCleaner` | `class` : `Object` | 8 | 5 | Startup(1)->Void, Shutdown(0)->Void, BuildValidFileSet(1)->HashSet`1, NeedClean(0)->Boolean, GetLastCleanupVersion(0)->Str... |
| `AutoAdjustLod+LuaLoadFadeInOrOutCallback` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(1)->Void, BeginInvoke(3)->IAsyncResult, EndInvoke(1)->Void |
| `BattleDecBloodTip` | `class` : `MonoBehaviour` | 3 | 10 | CSShow(2)->Void, StartPlay(0)->Void, Update(0)->Void |
| `BigMapUVSetting` | `class` : `MonoBehaviour` | 2 | 1 | Start(0)->Void, Update(0)->Void |
| `ChangeSceneCircleSlider` | `class` : `MonoBehaviour` | 6 | 11 | Awake(0)->Void, ResetValue(0)->Void, Init(2)->Void, Update(0)->Void, RefreshValue(0)->Void, GetRefreshDuring(0)->Int32 |
| `DefaultNewButtonCurve` | `class` : `Object` | 2 | 4 | LoadDefaultCurve(1)->Void, ReleaseDefaultCurve(0)->Void |
| `DynamicAsset` | `class` : `Object` | 4 | 4 | Load(0)->Object, Release(0)->Void, Update(0)->Void, TryDestroy(0)->Boolean |
| `GameFramework.FileWriter` | `class` : `Object` | 2 | 2 | WriteLine(1)->Void, ClearFile(0)->Void |
| `GameFramework.Log` | `class` : `Object` | 15 | 1 | GetWriteLogLevel(0)->Int32, SetWriteLogLevel(1)->Void, Debug(1)->Void, Debug(2)->Void, Debug(3)->Void, Debug(4)->Void, Inf... |
| `GameFramework.LogFile` | `class` : `Object` | 2 | 2 | Write(3)->Void, ClearOld(0)->Void |
| `GameKit.Base.WebRequestManager` | `class` : `SingletonBehaviour`1` | 18 | 10 | OnDisable(0)->Void, IsDownloadResult(2)->Boolean, LoadTexture(5)->Void, LoadTexture(6)->Void, Get(5)->Void, Post(6)->Void,... |
| `GameKit.Base.WebRequestManager+OnWebRequestCallback` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(3)->Void, BeginInvoke(5)->IAsyncResult, EndInvoke(1)->Void |
| `GameKit.Base.WebRequestManager+OnWebRequestProgre...` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(2)->Void, BeginInvoke(4)->IAsyncResult, EndInvoke(1)->Void |
| `Google.Protobuf.Collections.MapField`2` | `class` : `Object` | 34 | 4 | Clone(0)->MapField`2, Add(2)->Void, ContainsKey(1)->Boolean, ContainsValue(1)->Boolean, Remove(1)->Boolean, TryGetValue(2)... |
| `Google.Protobuf.Collections.MapField`2+Codec+Mess...` | `class` : `Object` | 5 | 2 | Reset(0)->Void, MergeFrom(1)->Void, WriteTo(1)->Void, CalculateSize(0)->Int32, Google.Protobuf.IMessage.get_Descriptor(0)-... |
| `Google.Protobuf.Collections.MapField`2+Dictionary...` | `class` : `Object` | 2 | 1 | MoveNext(0)->Boolean, Reset(0)->Void |
| `Google.Protobuf.Collections.MapField`2+MapView`1` | `class` : `Object` | 7 | 3 | Add(1)->Void, Clear(0)->Void, Contains(1)->Boolean, CopyTo(2)->Void, GetEnumerator(0)->IEnumerator`1, Remove(1)->Boolean, ... |
| `Google.Protobuf.Reflection.MapFieldAccessor` | `class` : `FieldAccessorBase` | 3 | 0 | Clear(1)->Void, HasValue(1)->Boolean, SetValue(2)->Void |
| `HHIdentityUtil+WebViewPauseHandler` | `class` : `MonoBehaviour` | 2 | 4 | OnApplicationPause(1)->Void, DelayResume(0)->IEnumerator |
| `LW.CountBattle.Box` | `class` : `Shape` | 10 | 1 | Get_size(2)->Void, Set_size(2)->Void, GetLocalCorners(0)->Vector2[], GetWorldCorners(0)->Vector2[], World2Local(1)->Vector... |
| `LW.CountBattle.Circle` | `class` : `Shape` | 5 | 1 | World2Local(1)->Vector2, Local2World(1)->Vector2, Contains(1)->Boolean, Overlap(1)->Boolean, ToString(0)->String |
| `LW.CountBattle.Shape` | `class` : `Object` | 7 | 2 | World2Local(1)->Vector2, Local2World(1)->Vector2, Contains(1)->Boolean, Overlap(1)->Boolean, SetPos(2)->Void, Get_pos(2)->... |
| `LW.CountBattle.SteerDisplay` | `class` : `Object` | 2 | 7 | Push(2)->Void, Update(1)->Void |
| `LW.CountBattle.SteerGroup` | `class` : `MonoBehaviour` | 25 | 19 | Awake(0)->Void, OnDestroy(0)->Void, SetPosX(1)->Void, SetPosY(1)->Void, SetPosXZ(2)->Void, SetPos(3)->Void, SetVelocity(2)... |
| `LW.CountBattle.SteerUnit` | `class` : `Object` | 7 | 10 | Destroy(0)->Void, SetPos(2)->Void, Move(1)->Void, Kill(0)->Void, Tick(2)->Void, Update(1)->Void, Sync(1)->Void |
| `LWBattleRVOAgent` | `class` : `MonoBehaviour` | 9 | 7 | Awake(0)->Void, Update(0)->Void, SetActive(1)->Void, OnDestroy(0)->Void, GetSpeedRatio(0)->Single, SetTargetPosition(2)->V... |
| `LWBattleRVOAgent_DOTS` | `class` : `MonoBehaviour` | 9 | 6 | Awake(0)->Void, Update(0)->Void, SetActive(1)->Void, GetSpeedRatio(0)->Single, OnDestroy(0)->Void, SetTargetPosition(2)->V... |
| `LWBattleRVOManager` | `class` : `Object` | 6 | 2 | InitLW(7)->Void, ProcessObstacles(0)->Void, OnDestroy(0)->Void, Update(2)->Void, AddAgent(4)->Int32, DeleteAgent(1)->Void |
| `LWBattleRVOManager_DOTS` | `class` : `Object` | 8 | 1 | InitLW(7)->Void, ProcessObstacles(0)->Void, OnDestroy(0)->Void, OnApplicationQuit(0)->Void, Update(2)->Void, LateUpdate(0)... |
| `LitJson.JsonMapper` | `class` : `Object` | 21 | 16 | AddArrayMetadata(1)->Void, AddObjectMetadata(1)->Void, AddTypeProperties(1)->Void, GetConvOp(2)->MethodInfo, ReadValue(2)-... |
| `LuaClientProfiler` | `class` : `Object` | 5 | 3 | BeginSample(1)->Void, BeginSample(2)->Void, EndSample(0)->Void, Attach(0)->Void, Detach(0)->Void |
| `LuaDatabaseManager` | `class` : `Object` | 12 | 1 | SetDBHighPriorityWork(1)->Void, InitDataBase(2)->Void, SetTimeReportThresholdMs(1)->Void, SetRowCountReportThreshold(1)->V... |
| `LuaMonoBase` | `class` : `MonoBehaviour` | 12 | 11 | MakeLuaBytes(2)->Void, CallLuaFunc(3)->Void, GetFunction(1)->Int32, GetFunctionInternal(1)->Int32, ReleaseLuaTable(0)->Voi... |
| `LuaMonoConfig` | `class` : `LuaMonoBase` | 13 | 14 | Awake(0)->Void, OnApplicationQuit(0)->Void, OnDestroy(0)->Void, OnEnable(0)->Void, OnDisable(0)->Void, OnCollisionEnter(1)... |
| `LuaPerfect.ObjectCache` | `class` : `Object` | 3 | 2 | SaveObject(1)->Int32, GetObject(1)->Object, ClearAll(0)->Void |
| `LuaPerfect.ObjectFormater` | `class` : `Object` | 10 | 1 | IsBasicType(1)->Boolean, GetAllFields(1)->List`1, FindProperty(2)->Boolean, GetAllProperties(1)->List`1, GetClassFullName(... |
| `LuaPerfect.ObjectItem` | `class` : `Object` | 12 | 3 | GetChildCount(0)->Int32, GetChildName(1)->String, SetValue(1)->Void, GetValue(0)->String, AddChild(2)->Void, GetChildObjec... |
| `LuaScriptInterface.UIManager` | `interface` : `` | 3 | 0 | OpenWindow(2)->Void, DestroyWindow(2)->Void, IsWindowOpen(1)->Boolean |
| `LuaStackTable` | `struct` : `ValueType` | 17 | 3 | SetInt(2)->Void, SetLong(2)->Void, SetDouble(2)->Void, SetString(2)->Void, SetBool(2)->Void, SetULong(2)->Void, SetByte(2)... |
| `LuaStringLookupTable` | `class` : `Object` | 4 | 2 | Init(1)->Void, Add(1)->Int32, Get(1)->String, Clear(0)->Void |
| `LuaUpdater` | `class` : `MonoBehaviour` | 4 | 1 | OnInit(1)->Void, Restart(1)->Void, Update(0)->Void, Dispose(0)->Void |
| `Main.Scripts.Application.LoadingState.HttpRequest` | `class` : `Object` | 3 | 13 | SendRequest(0)->Void, Dispose(0)->Void, OnUpdate(0)->Void |
| `Main.Scripts.Network.FutureManager` | `class` : `Object` | 6 | 2 | FlushLatencyReports(0)->Void, reset(0)->Void, getFutureId(0)->Int32, onSendRequest(3)->Void, onServerMsgCome(9)->Void, Get... |
| `Main.Scripts.Network.LatencyReporter` | `class` : `Object` | 4 | 9 | Record(9)->Void, Flush(0)->Void, RecycleRecords(0)->Void, AppendRecord(2)->Void |
| `Main.Scripts.Network.NetProxyStatus` | `class` : `Object` | 26 | 22 | GetLatency(0)->Int64, PurgeExpiredRecords(0)->Void, GetRecentServerTimeMax(0)->Int64, GetRecentServerTimeMaxCmd(0)->String... |
| `Main.Scripts.Scene.PVE.FIGridManager` | `class` : `Object` | 12 | 11 | IsValidNode(2)->Boolean, IsInOpenSet(1)->Boolean, IsInCloseSet(1)->Boolean, ProcessNode(3)->Void, BuildPath(1)->List`1, Se... |
| `Main.Scripts.Scene.PVE.FIGridManager+Node` | `class` : `Object` | 2 | 6 | Distance(1)->Single, SetParent(1)->Void |
| `Main.Scripts.Scene.PVE.PathGridCoord` | `class` : `Object` | 7 | 2 | PathGrid_IndexToGridPos(1)->Vector2Int, PathGrid_GridPosToIndex(1)->Int32, PathGrid_GridIndexToWorld(1)->Vector3, PathGrid... |
| `Main.Scripts.Scene.PVE.PveStaticDebug` | `class` : `MonoBehaviour` | 5 | 4 | SetDesc(1)->Void, Test(0)->Void, ScreenPointToRay(1)->Ray, ScreenPointToWorld(2)->Vector3, GetTouchPoint(0)->Vector3 |
| `Main.Scripts.Scene.PVE.SkillIndicator` | `class` : `MonoBehaviour` | 5 | 5 | SetTotalTime(1)->Void, SetCircleData(1)->Void, SetArcData(3)->Void, SetLineData(3)->Void, Update(0)->Void |
| `MapEditor.MapEditorUtil` | `class` : `Object` | 10 | 8 | InitXLua(0)->Void, EndXLua(0)->Void, CustomLoader(1)->LuaFileInfo, GetBuildAttrFromCfg(2)->String, GetCfgForLua(3)->String... |
| `NetworkManager` | `class` : `Object` | 24 | 4 | GetGameServerUrl(0)->String, GetGameServerPort(0)->Int32, GetUid(0)->String, OnUpdate(1)->Void, Shutdown(0)->Void, GetWorl... |
| `NewButton` | `class` : `Button` | 8 | 5 | OnDestroy(0)->Void, SetGrayMaterial(1)->Void, DoStateTransition(2)->Void, StartColorTween(2)->Void, DoSpriteSwap(1)->Void,... |
| `NewTMPText` | `class` : `TextMeshProUGUI` | 15 | 16 | OnPointerClick(1)->Void, GetLinkRect(1)->Rect, ConvertAlignFormat(2)->TextAlignmentOptions, HasArabic(2)->Boolean, CheckAr... |
| `NexgenDragon.SceneColorToShader` | `class` : `MonoBehaviour` | 3 | 8 | Awake(0)->Void, OnDestroy(0)->Void, CamCapture(0)->Void |
| `PCWebView` | `class` : `MonoBehaviour` | 2 | 2 | Awake(0)->Void, LoadUrl(1)->Void |
| `PVEStaticManager` | `class` : `Object` | 8 | 15 | SetSceneObj(1)->Void, Init(4)->Void, UnInit(0)->Void, OnUpdate(2)->Void, UpdateView(2)->Void, TilePosToChunkCoord(1)->Vect... |
| `PVEStaticManager+StaticObject` | `class` : `Object` | 3 | 6 | Load(1)->Void, Unload(0)->Void, SetVisible(1)->Void |
| `PrefabLightmapData` | `class` : `MonoBehaviour` | 2 | 2 | Awake(0)->Void, ApplyRendererInfo(2)->Void |
| `Protobuf.BattleDetailInfo` | `class` : `Object` | 8 | 11 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattleDetailInfo, Equals(1)->Boolean, GetHash... |
| `Protobuf.BattleEffectGroup` | `class` : `Object` | 8 | 7 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattleEffectGroup, Equals(1)->Boolean, GetHas... |
| `Protobuf.BattleEffectInfo` | `class` : `Object` | 8 | 9 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattleEffectInfo, Equals(1)->Boolean, GetHash... |
| `Protobuf.BattleEffectReason` | `class` : `Object` | 8 | 6 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattleEffectReason, Equals(1)->Boolean, GetHa... |
| `Protobuf.BattlePointInfo` | `class` : `Object` | 8 | 10 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattlePointInfo, Equals(1)->Boolean, GetHashC... |
| `Protobuf.BattleReport` | `class` : `Object` | 8 | 25 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattleReport, Equals(1)->Boolean, GetHashCode... |
| `Protobuf.BattleRoundPushInfo` | `class` : `Object` | 8 | 17 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->BattleRoundPushInfo, Equals(1)->Boolean, GetH... |
| `Protobuf.PveArmyResult` | `class` : `Object` | 8 | 6 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->PveArmyResult, Equals(1)->Boolean, GetHashCod... |
| `Protobuf.WorldAllAllianceCityInfo` | `class` : `Object` | 8 | 5 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->WorldAllAllianceCityInfo, Equals(1)->Boolean,... |
| `Protobuf.WorldPointInfo` | `class` : `Object` | 8 | 30 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->WorldPointInfo, Equals(1)->Boolean, GetHashCo... |
| `Protobuf.WorldRuinPointInfo` | `class` : `Object` | 8 | 14 | pb::Google.Protobuf.IMessage.get_Descriptor(0)->MessageDescriptor, Clone(0)->WorldRuinPointInfo, Equals(1)->Boolean, GetHa... |
| `RenderSceneSetting` | `class` : `MonoBehaviour` | 3 | 6 | OnEnable(0)->Void, OnDisable(0)->Void, SetSH(0)->Void |
| `SFSObjectLua` | `class` : `Object` | 20 | 0 | PutNull(2)->Void, PutBool(3)->Void, PutByte(3)->Void, PutShort(3)->Void, PutInt(3)->Void, PutLong(3)->Void, PutFloat(3)->V... |
| `SU_BuildSelectWorld` | `class` : `MonoBehaviour` | 4 | 9 | Awake(0)->Void, Init(1)->Void, InitBlocks(1)->Void, ChangeColor(1)->Void |
| `SceneLowFpsMonitor` | `class` : `MonoBehaviour` | 2 | 11 | StartStats(0)->Void, Update(0)->Void |
| `SceneManager` | `class` : `Object` | 3 | 1 | SetWorldObj(1)->Void, IsInWorld(0)->Boolean, IsInCity(0)->Boolean |
| `SceneQualitySetting` | `class` : `Object` | 7 | 1 | ChangeQualitySetting(0)->Void, GetScale(0)->Single, CheckLowMemory(0)->Boolean, SetResolutionQuality(0)->Void, SetPixelHei... |
| `SceneSpriteSlider` | `class` : `MonoBehaviour` | 6 | 11 | Awake(0)->Void, SetColorType(1)->Void, SetBattleFocusBrightness(1)->Void, Init(2)->Void, SetProgressValue(1)->Void, ApplyB... |
| `SceneViewerGFXPanel` | `class` : `BaseGFXPanel` | 8 | 6 | DrawGUI(0)->Void, DrawSceneList(0)->Void, DrawTransformList(0)->Void, DrawTransform(1)->Void, DrawDetail(0)->Void, DumpOne... |
| `Scene_Node_Observer` | `class` : `MonoBehaviour` | 5 | 2 | Awake(0)->Void, OnEnable(0)->Void, OnDestroy(0)->Void, OnTimelinePlay(0)->Void, OnTimelineStop(0)->Void |
| `Sfs2X.Bitswarm.BitSwarmClient` | `class` : `Object` | 30 | 23 | GetReceiveBufferRate(0)->Single, GetReceiveBufferSize(0)->Int32, SetReceiveBufferSize(1)->Void, Init(0)->Void, Destroy(0)-... |
| `Sfs2X.Bitswarm.ISocketClient` | `interface` : `` | 15 | 0 | Init(0)->Void, Destroy(0)->Void, GetController(1)->IController, Connect(0)->Void, Connect(2)->Void, Send(1)->Void, SendBin... |
| `Sfs2X.Bitswarm.IoHandler` | `interface` : `` | 3 | 0 | OnDataRead(1)->Void, OnDataWrite(1)->Void, OnDataWrite(2)->Void |
| `Sfs2X.Controllers.ExtensionController` | `class` : `BaseController` | 2 | 3 | HandleMessage(1)->Void, HandleExtensionResponse(2)->Void |
| `Sfs2X.Controllers.RequestDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(1)->Void, BeginInvoke(3)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Controllers.SystemController` | `class` : `BaseController` | 8 | 2 | InitRequestHandlers(0)->Void, HandleMessage(1)->Void, FnHandshake(1)->Void, FnLogin(1)->Void, FnLogout(1)->Void, FnPingPon... |
| `Sfs2X.Core.BaseEvent` | `class` : `Object` | 2 | 3 | ToString(0)->String, Clone(0)->BaseEvent |
| `Sfs2X.Core.EventDispatcher` | `class` : `Object` | 4 | 2 | AddEventListener(2)->Void, RemoveEventListener(2)->Void, DispatchEvent(1)->Void, RemoveAll(0)->Void |
| `Sfs2X.Core.EventListenerDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(1)->Void, BeginInvoke(3)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Core.IPacketEncrypter` | `interface` : `` | 2 | 0 | Encrypt(1)->Void, Decrypt(1)->Void |
| `Sfs2X.Core.PacketHeader` | `struct` : `ValueType` | 3 | 5 | FromBinary(1)->PacketHeader, Encode(0)->Byte, ToString(0)->String |
| `Sfs2X.Core.SFSIOHandler` | `class` : `Object` | 14 | 14 | InitStates(0)->Void, OnDataRead(1)->Void, HandleNewPacket(1)->ByteArray, HandleDataSize(1)->ByteArray, HandleDataSizeFragm... |
| `Sfs2X.Core.SFSProtocolCodec` | `class` : `Object` | 5 | 8 | OnPacketRead(1)->Void, OnPacketWrite(1)->Void, OnPacketWrite(2)->Void, PrepareTCPPacket(1)->ISFSObject, DispatchRequest(1)... |
| `Sfs2X.Core.Sockets.AsyncTCPSocketLayer` | `class` : `BaseSocketLayer` | 23 | 13 | LogError(1)->Void, HandleError(2)->Void, HandleDisconnection(1)->Void, HandleBinaryData(2)->Void, IsIPv6Address(1)->Boolea... |
| `Sfs2X.Core.Sockets.BestHttpWebSocketLayer` | `class` : `BaseSocketLayer` | 18 | 9 | Connect(2)->Void, Disconnect(0)->Void, Disconnect(1)->Void, Kill(0)->Void, Write(3)->Void, Write(1)->Void, OnOpen(1)->Void... |
| `Sfs2X.Core.Sockets.ConnectionDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(0)->Void, BeginInvoke(2)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Core.Sockets.ISocketLayer` | `interface` : `` | 9 | 0 | Connect(2)->Void, Disconnect(0)->Void, Disconnect(1)->Void, Write(3)->Void, Write(1)->Void, Kill(0)->Void, GetReceiveBuffe... |
| `Sfs2X.Core.Sockets.ObjectPool`1` | `class` : `Object` | 2 | 2 | GetObject(0)->T, ReturnObject(1)->Void |
| `Sfs2X.Core.Sockets.OnCumstomDataDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(1)->Void, BeginInvoke(3)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Core.Sockets.OnDataDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(1)->Void, BeginInvoke(3)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Core.Sockets.OnErrorDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(2)->Void, BeginInvoke(4)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Core.Sockets.OnStringDataDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(1)->Void, BeginInvoke(3)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Entities.Data.ISFSArray` | `interface` : `` | 53 | 0 | Contains(1)->Boolean, GetElementAt(1)->Object, GetWrappedElementAt(1)->SFSDataWrapper, RemoveElementAt(1)->Object, Size(0)... |
| `Sfs2X.Entities.Data.ISFSObject` | `interface` : `` | 55 | 0 | IsNull(1)->Boolean, ContainsKey(1)->Boolean, RemoveElement(1)->Void, GetKeys(0)->String[], Traverse(1)->Void, Size(0)->Int... |
| `Sfs2X.Entities.Data.SFSArray` | `class` : `Object` | 60 | 2 | NewFromBinaryData(1)->SFSArray, NewFromJsonData(1)->ISFSArray, NewInstance(0)->SFSArray, Contains(1)->Boolean, GetWrappedE... |
| `Sfs2X.Entities.Data.SFSArrayEnumerator` | `class` : `Object` | 3 | 2 | System.Collections.IEnumerator.Reset(0)->Void, System.Collections.IEnumerator.MoveNext(0)->Boolean, System.Collections.IEn... |
| `Sfs2X.Entities.Data.SFSArrayLite` | `class` : `SFSArray` | 14 | 0 | NewInstance(0)->ISFSArray, GetClass(1)->Object, GetByte(1)->Byte, GetShort(1)->Int16, GetLong(1)->Int64, GetFloat(1)->Sing... |
| `Sfs2X.Entities.Data.SFSObject` | `class` : `Object` | 60 | 2 | NewFromBinaryData(1)->SFSObject, NewFromJsonData(1)->ISFSObject, NewInstance(0)->SFSObject, Dump(0)->String, GetValue(1)->... |
| `Sfs2X.Entities.Data.SFSObjectLite` | `class` : `SFSObject` | 14 | 0 | NewInstance(0)->ISFSObject, GetClass(1)->Object, GetByte(1)->Byte, GetShort(1)->Int16, GetLong(1)->Int64, GetFloat(1)->Sin... |
| `Sfs2X.Entities.Data.Vec3D` | `class` : `Object` | 7 | 7 | fromArray(1)->Vec3D, fromIntArray(1)->Vec3D, fromFloatArray(1)->Vec3D, IsFloat(0)->Boolean, ToIntArray(0)->Int32[], ToFloa... |
| `Sfs2X.FSM.FSMState` | `class` : `Object` | 4 | 2 | SetStateName(1)->Void, GetStateName(0)->Int32, AddTransition(2)->Void, ApplyTransition(1)->Int32 |
| `Sfs2X.FSM.FiniteStateMachine` | `class` : `Object` | 7 | 4 | AddState(1)->Void, AddAllStates(1)->Void, AddStateTransition(3)->Void, ApplyTransition(1)->Int32, GetCurrentState(0)->Int3... |
| `Sfs2X.FSM.FiniteStateMachine+OnStateChangeDelegate` | `class` : `MulticastDelegate` | 3 | 0 | Invoke(2)->Void, BeginInvoke(4)->IAsyncResult, EndInvoke(1)->Void |
| `Sfs2X.Logging.Logger` | `class` : `Object` | 7 | 4 | Debug(1)->Void, Info(1)->Void, Warn(1)->Void, Error(1)->Void, Log(2)->Void, AddEventListener(2)->Void, RemoveEventListener... |
| `Sfs2X.Logging.LoggerEvent` | `class` : `BaseEvent` | 3 | 1 | LogEventType(1)->String, ToString(0)->String, Clone(0)->Object |
| `Sfs2X.Protocol.IProtocolCodec` | `interface` : `` | 3 | 0 | OnPacketRead(1)->Void, OnPacketWrite(1)->Void, OnPacketWrite(2)->Void |
| `Sfs2X.Protocol.Serialization.DefaultObjectDumpFor...` | `class` : `Object` | 5 | 8 | PrettyPrintDump(1)->String, GetFormatTabs(1)->String, StrFill(2)->String, HexDump(1)->String, HexDump(2)->String |
| `Sfs2X.Protocol.Serialization.DefaultSFSDataSerial...` | `class` : `Object` | 60 | 6 | Object2Binary(2)->ByteArray, Obj2bin(2)->ByteArray, Array2Binary(2)->ByteArray, Arr2bin(2)->ByteArray, Binary2Object(1)->I... |
| `Sfs2X.Protocol.Serialization.ISFSDataSerializer` | `interface` : `` | 8 | 0 | Object2Binary(2)->ByteArray, Array2Binary(2)->ByteArray, Binary2Object(1)->ISFSObject, Binary2Array(1)->ISFSArray, Object2... |
| `Sfs2X.Protocol.Serialization.UnrealDefaultSFSData...` | `class` : `Object` | 60 | 6 | Object2Binary(2)->ByteArray, Obj2bin(2)->ByteArray, Array2Binary(2)->ByteArray, Arr2bin(2)->ByteArray, ParseHeaderAndCmd(1... |
| `Sfs2X.Requests.BaseRequest` | `class` : `Object` | 2 | 5 | Validate(1)->Void, Execute(1)->Void |
| `Sfs2X.Requests.ExtensionRequest` | `class` : `BaseRequest` | 3 | 6 | Init(3)->Void, Validate(1)->Void, Execute(1)->Void |
| `Sfs2X.Requests.IRequest` | `interface` : `` | 2 | 0 | Validate(1)->Void, Execute(1)->Void |
| `Sfs2X.Requests.LoginRequest` | `class` : `BaseRequest` | 3 | 10 | Init(4)->Void, Execute(1)->Void, Validate(1)->Void |
| `Sfs2X.Requests.ManualDisconnectionRequest` | `class` : `BaseRequest` | 2 | 0 | Validate(1)->Void, Execute(1)->Void |
| `Sfs2X.Requests.PingPongRequest` | `class` : `BaseRequest` | 2 | 0 | Validate(1)->Void, Execute(1)->Void |
| `Sfs2X.SmartFox` | `class` : `Object` | 37 | 24 | SetSendLogFlag(1)->Void, Initialize(1)->Void, Reset(0)->Void, GetSocketEngine(0)->ISocketClient, KillConnection(0)->Void, ... |
| `Sfs2X.Util.ApsZstdV1` | `class` : `Object` | 7 | 18 | InitPadState(3)->Void, Compress(1)->Void, RestoreStandardFrame(3)->ArraySegment`1, XorPrefix(3)->Void, CopyState(2)->Void,... |
| `Sfs2X.Util.ArrayPoolHelper` | `class` : `Object` | 2 | 1 | SpawnByteArrayFromPool(1)->Byte[], RecycleByteArrayToPool(1)->Void |
| `Sfs2X.Util.ByteArray` | `class` : `Object` | 42 | 12 | GetCompressionAlgorithm(1)->CompressionAlgorithm, Reset(0)->Void, SetData(3)->Void, GetByte(1)->Byte, GetRawBytes(0)->Byte... |
| `Sfs2X.Util.ByteArrayPool` | `class` : `Object` | 2 | 1 | Rent(1)->ByteArray, Recycle(1)->Void |
| `Sfs2X.Util.SFSErrorCodes` | `class` : `Object` | 2 | 1 | SetErrorMessage(2)->Void, GetErrorMessage(3)->String |
| `TileCoordWorld` | `class` : `Object` | 34 | 0 | TileFloatToWorld(1)->Vector3, TileFloatToWorld(2)->Vector3, WorldToTileFloat(1)->Vector2, WorldXYZToTileFloatXY(5)->Void, ... |
| `UIWorldLabel` | `class` : `MonoBehaviour` | 14 | 19 | Awake(0)->Void, SetLevel(1)->Void, SetCamp(1)->Void, SetCountry(1)->Void, SetLevel(2)->Void, SetName(1)->Void, SetName(2)-... |
| `UnityGameFramework.Runtime.BaseComponent` | `class` : `GameFrameworkComponent` | 6 | 8 | OnApplicationPause(1)->Void, Awake(0)->Void, Start(0)->Void, PauseGame(0)->Void, ResumeGame(0)->Void, ResetNormalGameSpeed... |
| `UnityGameFramework.Runtime.EventComponent` | `class` : `Object` | 7 | 3 | OnUpdate(1)->Void, Shutdown(0)->Void, Check(2)->Boolean, Subscribe(2)->Void, Unsubscribe(2)->Void, Fire(2)->Void, HandleEv... |
| `UnityGameFramework.Runtime.EventComponent+ObjectP...` | `class` : `Object` | 3 | 2 | Get(0)->T, Return(1)->Void, Count(0)->Int32 |
| `UnityGameFramework.SDK.AnalyticsEvent` | `class` : `Object` | 13 | 30 | TutorialComplete(2)->Void, FirstOpenAppsflyer(0)->Void, Login(3)->Void, TriggerEventPurchase(4)->Void, LevelUp(1)->Void, C... |
| `UnityGameFramework.SDK.HelpManager` | `class` : `Object` | 16 | 1 | Purge(0)->Void, init(0)->Void, setUserData(0)->Void, showHelpShiftFAQ(0)->Void, showHelpShiftFAQ(1)->Void, showSingleFAQ(1... |
| `UploadImageManager` | `class` : `Object` | 19 | 18 | Purge(0)->Void, OnUploadImage(3)->Void, OnImagePathOk(1)->Void, UploadHeadImage(4)->Void, GetHeadPath(2)->String, Download... |
| `VEngine.AllBundledAsset` | `class` : `Asset` | 7 | 2 | Create(1)->AllBundledAsset, OnLoad(0)->Void, OnUnload(0)->Void, LoadImmediate(0)->Void, OnUpdate(0)->Void, UpdateLoading(0... |
| `VEngine.Asset` | `class` : `Loadable` | 15 | 4 | MoveNext(0)->Boolean, Reset(0)->Void, Get(0)->T, OnComplete(0)->Void, OnUnused(0)->Void, LoadAsync(3)->Asset, LoadAllAsset... |
| `VEngine.Assets` | `class` : `Object` | 6 | 4 | SetQueueSize(2)->Void, Enqueue(3)->Asset, Preload(3)->Asset, GetAsset(1)->T, GetProgress(0)->Single, Clear(0)->Void |
| `VEngine.BundledAsset` | `class` : `Asset` | 10 | 3 | Create(2)->BundledAsset, IsAssetDownloaded(1)->Boolean, OnLoad(0)->Void, OnUnload(0)->Void, LoadImmediate(0)->Void, OnUpda... |
| `VEngine.BundledScene` | `class` : `Scene` | 5 | 1 | OnUpdate(0)->Void, UpdateDependencies(0)->Void, OnUnload(0)->Void, OnLoad(0)->Void, Create(2)->Scene |
| `VEngine.ClearVersions` | `class` : `Operation` | 2 | 3 | Start(0)->Void, Update(0)->Void |
| `VEngine.DownloadVersions` | `class` : `Operation` | 4 | 3 | Start(0)->Void, AddDownloadSize(1)->Void, Stop(0)->Void, Update(0)->Void |
| `VEngine.InitializeVersions` | `class` : `Operation` | 2 | 5 | Start(0)->Void, Update(0)->Void |
| `VEngine.Scene` | `class` : `Loadable` | 12 | 7 | MoveNext(0)->Boolean, Reset(0)->Void, LoadAsync(3)->Scene, LoadAdditiveAsync(2)->Scene, OnUpdate(0)->Void, UpdateLoading(0... |
| `VEngine.SceneObject` | `class` : `Loadable` | 15 | 11 | MoveNext(0)->Boolean, Reset(0)->Void, SetTransformParent(2)->Void, SetActive(1)->Void, RemoveAction(1)->Boolean, RunAction... |
| `VEngine.UpdateVersions` | `class` : `Operation` | 6 | 3 | GetManifest(1)->Manifest, Start(0)->Void, Override(0)->Void, Dispose(0)->Void, Update(0)->Void, SplitVersionFile(1)->Void |
| `VEngine.Versions` | `class` : `Object` | 37 | 15 | GetManifest(1)->Manifest, CreateAsset(2)->Asset, IsAssetDownloaded(1)->Boolean, CreateScene(2)->Scene, CreateManifest(2)->... |
| `WebSocketItem3` | `class` : `WebSocketItemBase` | 12 | 6 | CalcSign(3)->String, SetCallBack(1)->Void, IsOpen(0)->Boolean, Connect(5)->Boolean, Send(1)->Void, Process(0)->Void, Close... |
| `WebSocketItemBase` | `class` : `Object` | 6 | 0 | SetCallBack(1)->Void, IsOpen(0)->Boolean, Connect(5)->Boolean, Process(0)->Void, Send(1)->Void, Close(0)->Void |
| `WebViewHost` | `class` : `MonoBehaviour` | 17 | 12 | Awake(0)->Void, OpenPage(2)->Void, CloseWebView(1)->Void, RegisterCommandCallback(1)->Void, RegisterPageStartedCallback(1)... |
| `WebViewInterface` | `class` : `MonoBehaviour` | 14 | 13 | OpenUrl(1)->Void, Start(0)->Void, OnPageStarted(2)->Void, OnPageFinished(3)->Void, OnPageErrorReceived(4)->Void, InitWebVi... |
| `WorldAllianceBuilding` | `class` : `MonoBehaviour` | 27 | 35 | CSInit(1)->Void, CSUninit(0)->Void, refeshDate(0)->Void, SetTilePos1(2)->Void, SetTouchPickAblePos(0)->Void, FromUILoad(0)... |
| `WorldAreaMapData` | `class` : `Object` | 3 | 7 | Load(1)->Void, GetAreaData(1)->EdenAreaInfo, GetAreaByPosId(1)->EdenAreaInfo |
| `WorldAutoMonoManager` | `class` : `WorldManagerBase` | 5 | 3 | OnUpdate(1)->Void, AddAutoFace(1)->Void, RemoveAutoFace(1)->Void, AddAutoScale(1)->Void, RemoveAutoScale(1)->Void |
| `WorldBuilding` | `class` : `MonoBehaviour` | 60 | 39 | Awake(0)->Void, CSInit(1)->Void, CSUninit(0)->Void, CSUpdate(1)->Void, InitLod(1)->Void, DoFoldUpAnim(0)->Single, DoExtend... |
| `WorldCulling` | `class` : `WorldManagerBase` | 7 | 3 | Init(0)->Void, UnInit(0)->Void, OnUpdate(1)->Void, AddCullingBounds(1)->Void, RemoveCullingBounds(1)->Void, UpdateCullingB... |
| `WorldCulling+ICullingObject` | `interface` : `` | 2 | 0 | GetBoundingSphere(0)->BoundingSphere, OnCullingStateVisible(1)->Void |
| `WorldEdenAreaManager` | `class` : `WorldManagerBase` | 13 | 2 | Init(0)->Void, LoadMapDataFromFile(1)->Void, InitPassData(0)->Void, UnInit(0)->Void, OnUpdate(1)->Void, OnPassOwnerInfoRec... |
| `WorldGoTransAdj` | `class` : `MonoBehaviour` | 2 | 5 | Start(0)->Void, Update(0)->Void |
| `WorldLodManager` | `class` : `WorldManagerBase` | 8 | 5 | Init(0)->Void, UnInit(0)->Void, AddLodAdjuster(1)->Void, RemoveLodAdjuster(1)->Void, OnUpdate(1)->Void, OnLodChanged(1)->V... |
| `WorldManagerBase` | `class` : `Object` | 3 | 1 | Init(0)->Void, UnInit(0)->Void, OnUpdate(1)->Void |
| `WorldMapZoneManager` | `class` : `WorldManagerBase` | 33 | 38 | GetEdgeMaterial(2)->Material, GetZoneMaterial(1)->Material, IsFuncOpen(0)->Boolean, ShowZoneMap(0)->Void, HideZoneMap(0)->... |
| `WorldMessageProcessor` | `class` : `Object` | 18 | 9 | Start(0)->Void, Stop(0)->Void, Clear(0)->Void, InitPbTreeMap(0)->Void, IsWorldMsg(1)->Boolean, PushMessage(2)->Void, PopMe... |
| `WorldScene` | `class` : `MonoBehaviour` | 59 | 30 | RegisterPhysics(1)->Void, UnregisterPhysics(1)->Void, AddLodAdjuster(1)->Void, RemoveLodAdjuster(1)->Void, GetLodConfigs(1... |
| `WorldSceneDesc` | `class` : `Object` | 5 | 12 | Load(1)->Void, LoadWorldStatic(1)->Void, LoadWithReturn(1)->List`1, Save(1)->Void, SaveWorldStaic(1)->Void |
| `WorldSceneDesc+GridDesc` | `class` : `Object` | 2 | 4 | Load(1)->Void, Save(1)->Void |
| `WorldSceneDesc+ObjectDesc` | `class` : `Object` | 8 | 13 | Load(1)->Void, LoadWorldStatic(1)->Void, LoadWorldOptimize(2)->Void, SaveWorldStatic(1)->Void, Save(1)->Void, SaveWorldOpt... |
| `WorldStaticManager` | `class` : `WorldManagerBase` | 41 | 41 | Init(0)->Void, UnInit(0)->Void, ShowStaticModel(0)->Void, HideStaticModel(0)->Void, OnRemoveObject(0)->Void, OnInitObject(... |
| `WorldStaticManager+Block` | `class` : `Object` | 4 | 4 | Init(3)->Void, Uninit(0)->Void, GetChunkObjList(1)->List`1, IsTileWalkable(1)->Boolean |
| `WorldStaticManager+StaticObject` | `class` : `Object` | 3 | 6 | Load(1)->Void, Unload(0)->Void, SetVisible(1)->Void |
| `WorldStaticQuadBatch` | `class` : `Object` | 13 | 14 | GetOrCreate(1)->SourceQuad, RegisterQuadVertex(14)->Void, RegisterQuadTriangles(7)->Void, IsQuadRegistered(1)->Boolean, Co... |
| `WorldTerrain` | `class` : `MonoBehaviour` | 3 | 6 | Create(1)->Void, Awake(0)->Void, CreateMesh(1)->Mesh |
| `WorldTouchEffect` | `class` : `MonoBehaviour` | 2 | 2 | FadeIn(0)->Void, CoFadeIn(0)->IEnumerator |
| `WorldTroopBattleHeadFollow` | `class` : `MonoBehaviour` | 34 | 28 | Setup(0)->Void, Release(0)->Void, SetBattleFlowOptions(12)->Void, ClearBattleFlowOptions(0)->Void, SetAppearForward(1)->Vo... |
| `WorldTroopLine` | `class` : `MonoBehaviour` | 18 | 30 | SetDisplayOffset(3)->Void, Clear(0)->Void, FadeIn(0)->Void, FadeOut(0)->Void, IsFadeOutFinish(0)->Boolean, SetDragPath(2)-... |
| `WorldTroopLineMove` | `class` : `MonoBehaviour` | 19 | 26 | SetDisplayOffset(3)->Void, Init(0)->Void, Clear(0)->Void, HideLine(0)->Void, SetPath(1)->Void, Awake(0)->Void, DrawLine(3)... |
| `WorldTroopMove` | `class` : `MonoBehaviour` | 16 | 26 | SetRotationTarget(6)->Void, UpdateSmoothRotation(0)->Void, SetDisplayOffset(2)->Void, StartMove(8)->Void, StartMoveWorldPo... |
| `WorldTroopRotation` | `class` : `MonoBehaviour` | 2 | 4 | Awake(0)->Void, Update(0)->Void |
| `WorldZone` | `class` : `Object` | 16 | 41 | Reset(0)->Void, SetEdgePosition(1)->Void, ToggleEdge(1)->Void, CreateEdge(0)->Void, DelayActive(0)->IEnumerator, ToggleZon... |
| `WorldZoneData` | `class` : `Object` | 2 | 4 | IsNeighborZone(1)->Boolean, Load(1)->Void |
| `WorldZoneMapData` | `class` : `Object` | 5 | 5 | Load(1)->Void, LoadByBytes(1)->Void, GetZoneData(1)->WorldZoneData, GetZoneByPosId(1)->WorldZoneData, DumpZones(0)->Void |
| `WorldZoneTreeNode` | `class` : `Object` | 4 | 3 | CrateSubNodes(1)->Void, IsRectIntersect(2)->Boolean, AddZone(1)->Void, FindZone(3)->Void |
| `XLua.CSObjectWrap.AnimationCurveListWrap` | `class` : `Object` | 4 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_animationCurve1(1)->Int32, _s_set_animationCurve1(1)->Int32 |
| `XLua.CSObjectWrap.ApplicationLaunchWrap` | `class` : `Object` | 33 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_GetObjectCull(1)->Int32, _m_RotateDoneToAwake(1)->Int32, _m_GetDeepLin... |
| `XLua.CSObjectWrap.AutoAdjustLodWrap` | `class` : `Object` | 14 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_SetLodCallback(1)->Int32, _m_SetLodType(1)->Int32, _m_GetLodType(1)->I... |
| `XLua.CSObjectWrap.AutoAdjustScreenPosWrap` | `class` : `Object` | 7 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_Init(1)->Int32, _g_get_debug(1)->Int32, _g_get_ignoreCameraClamp(1)->I... |
| `XLua.CSObjectWrap.AutoDoMovePosWrap` | `class` : `Object` | 16 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_Init(1)->Int32, _m_GetDownTime(1)->Int32, _m_GetUpTime(1)->Int32, _m_G... |
| `XLua.CSObjectWrap.AutoFaceToCameraWrap` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32 |
| `XLua.CSObjectWrap.BattleDecBloodTipWrap` | `class` : `Object` | 5 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_CSShow(1)->Int32, _g_get_duringTime(1)->Int32, _s_set_duringTime(1)->I... |
| `XLua.CSObjectWrap.BezierUtilsWrap` | `class` : `Object` | 3 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_Bezier2Path_xlua_st_(1)->Int32 |
| `XLua.CSObjectWrap.BitBenderGamesMobileTouchCamera...` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CastFrom(1)->Int32 |
| `XLua.CSObjectWrap.BitBenderGamesMobileTouchCamera...` | `class` : `Object` | 60 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_Clone(1)->Int32, _m_IsOrth(1)->Int32, _m_SetYRotation(1)->Int32, _m_Ca... |
| `XLua.CSObjectWrap.BitBenderGamesMobileTouchCamera...` | `class` : `Object` | 8 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_posY(1)->Int32, _g_get_offsetZ(1)->Int32, _g_get_sensitivity(1)->I... |
| `XLua.CSObjectWrap.BitBenderGamesMonoBehaviourWrap...` | `class` : `Object` | 4 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_Transform(1)->Int32, _g_get_GameObject(1)->Int32 |
| `XLua.CSObjectWrap.BitBenderGamesTouchInputControl...` | `class` : `Object` | 26 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_SetDragThresholdValue(1)->Int32, _m_ClearDelegate(1)->Int32, _m_OnEven... |
| `XLua.CSObjectWrap.BitBenderGamesTouchWrapperWrap` | `class` : `Object` | 8 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_UseMouseInput(1)->Int32, _g_get_TouchCount(1)->Int32, _g_get_Touch... |
| `XLua.CSObjectWrap.BitBenderGamesWrappedTouchWrap` | `class` : `Object` | 7 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_FromTouch_xlua_st_(1)->Int32, _g_get_Position(1)->Int32, _g_get_Finger... |
| `XLua.CSObjectWrap.BitSetWrap` | `class` : `Object` | 8 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_LoadAsync_xlua_st_(1)->Int32, _m_Load_xlua_st_(1)->Int32, _m_Remove_xl... |
| `XLua.CSObjectWrap.BlurURPWrap` | `class` : `Object` | 6 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_AddRenderPasses(1)->Int32, _m_Create(1)->Int32, _m_EnableFeature_xlua_... |
| `XLua.CSObjectWrap.BuildFenceDoorWrap` | `class` : `Object` | 4 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_bounds(1)->Int32, _s_set_bounds(1)->Int32 |
| `XLua.CSObjectWrap.BuildLabelInstancedBatchRendere...` | `class` : `Object` | 13 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_SetShared(1)->Int32, _m_Clear(1)->Int32, _m_ConfigAdaptive(1)->Int32, ... |
| `XLua.CSObjectWrap.BuildSelectWrap` | `class` : `Object` | 3 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_ChangeColor(1)->Int32 |
| `XLua.CSObjectWrap.BuildingGrowEffectWrap` | `class` : `Object` | 18 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_StartBuild(1)->Int32, _m_DisappearBuild(1)->Int32, _m_ShowNormal(1)->I... |
| `XLua.CSObjectWrap.BuildingStateWrap` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CastFrom(1)->Int32 |
| `XLua.CSObjectWrap.BulletCollisionJobSystemWrap` | `class` : `Object` | 11 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_ExecuteCollisionCheck(1)->Int32, _m_GetNextHit(1)->Int32, _g_get_Insta... |
| `XLua.CSObjectWrap.BulletMoveDriverWrap` | `class` : `Object` | 10 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_useSubStep(1)->Int32, _g_get_fixedStep(1)->Int32, _g_get_maxSubSte... |
| `XLua.CSObjectWrap.BulletMoveSystemWrap` | `class` : `Object` | 28 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_Register_xlua_st_(1)->Int32, _m_RegisterWithRender_xlua_st_(1)->Int32,... |
| `XLua.CSObjectWrap.BulletZombieCollisionTestWrap` | `class` : `Object` | 18 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _g_get_zombieCount(1)->Int32, _g_get_bulletsPerFrame(1)->Int32, _g_get_sp... |
| `XLua.CSObjectWrap.BypassCertificateWrap` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32 |
| `XLua.CSObjectWrap.CSUtilsWrap` | `class` : `Object` | 21 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_SetPositionFromInput_xlua_st_(1)->Int32, _m_WorldPositionToUISpacePosi... |
| `XLua.CSObjectWrap.CameraAniHandlerWrap` | `class` : `Object` | 6 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_Enter(1)->Int32, _m_Exit(1)->Int32, _g_get_pauseAtFirstFrame(1)->Int32... |
| `XLua.CSObjectWrap.CameraMoveWrap` | `class` : `Object` | 5 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_SetMoveToNpc(1)->Int32, _m_MoveToTarget(1)->Int32, _m_ResumeFromTarget... |
| `XLua.CSObjectWrap.CatmullRomUtilsWrap` | `class` : `Object` | 4 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32, _m_CalcCatmullRomCurve_xlua_st_(1)->Int32, _m_CalcCurve_xlua_st_(1)->Int32 |
| `XLua.CSObjectWrap.CenterScrollViewMovementTypeWrap` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CastFrom(1)->Int32 |
| `XLua.CSObjectWrap.CenterScrollViewScrollRectEvent...` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CreateInstance(1)->Int32 |
| `XLua.CSObjectWrap.CenterScrollViewScrollViewLayou...` | `class` : `Object` | 2 | 0 | __Register(1)->Void, __CastFrom(1)->Int32 |
