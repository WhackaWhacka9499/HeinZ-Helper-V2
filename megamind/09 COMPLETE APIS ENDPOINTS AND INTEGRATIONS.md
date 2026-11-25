# Volume 09: Complete APIs, Endpoints, Network Gateways & Repository Integrations

> **Generated:** `2026-11-23 11:27:27 UTC` | **Sources:** `megamind/raw/apis_and_integrations_complete.json` + `csharp_and_http_endpoints.json` + `packets_complete.json` + `heinz_architecture.json`

## 1. Master API Surface Summary (Game Client + HeinZ Platform + External Integrations)

| API Layer | Protocol / Transport | Verified Count | Where Detailed |
|---|---|---:|---|
| **Last Z SmartFoxServer Game RPCs** | SmartFoxServer TCP (`SFSNetwork.SendMessage`) | **2,279 / 2,297** wire cmds (`2,245` `MsgDefines`) | Vol 01 & `packets_complete.json` |
| **Last Z Chat WebSocket API** | WebSocket (`ChatManager2` / `WebMessage`) | **90** `ChatMsgDefines` + **21** `WebMessage` modules | Vol 01 & Vol 07 |
| **Last Z Mail V4 & Protobuf API** | `pb` Protobuf + `MailProtocolRouter` | **269** Protobuf schemas + **3** Mail V4 modules | Vol 07 |
| **Last Z HTTP / HTTPS / CDN / PHP APIs** | `LuaWebRequest` / `Best.HTTP` / `UnityWebRequest` | **34** verified client URLs & PHP endpoints (redacted) | Section 2 below |
| **Last Z Login & Server Gateways** | `Loading.*` + `LuaDatatable.server_ip` + C# Network classes | **31** `Loading.*` modules, **20** C# Net classes, **11** `server_ip` rows | Sections 3-4 below |
| **HeinZ Hub Desktop/Web RPC API** | PyWebView JS-to-Python bridge (`HubBackend`) | **30** RPC methods + **51** `action_id` routes | Vol 06 |
| **Google Apps Script & External Webhooks** | HTTPS POST/GET (`GoogleAppsScript_SyncReceiver.js`, Sheets/Drive) | **8** repo URL bindings + **3** JS API files | Section 5 below |
| **All Repository Automation/API/Listener/Telemetry Scripts** | Python AST (`api/`, `listeners/`, `telemetry/`, `daemon/`, `tools/`, `launcher/`) | **114** Python modules fully AST-mapped | Section 6 below |

## 2. All Verified Last Z Client HTTP / HTTPS / CDN / PHP Endpoints

| Endpoint URL / Path | Source (Lua Module or C# Static Field) |
|---|---|
| `/gameservice/probe.php` | `Loading.AppStartupLoading.RequestServerStateUrl()` |
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

## 3. Last Z Login Pipeline, `LuaWebRequest` & Server Gateways (`server_ip`: 11 rows)

### `server_ip` Gateway Entries
| Row ID | Fields |
|---|---|
| `1` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r1.omnilojoapps.com`, `direct_ip=47.251.175.252`, `... |
| `2` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r1.omnilojoapps.com`, `direct_ip=47.251.175.252`, `... |
| `3` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r1.omnilojoapps.com`, `direct_ip=47.251.175.252`, `... |
| `4` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r1.omnilojoapps.com`, `direct_ip=47.251.175.252`, `... |
| `5` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r2.omnilojoapps.com`, `direct_ip=47.251.97.136`, `g... |
| `6` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r2.omnilojoapps.com`, `direct_ip=47.251.97.136`, `g... |
| `7` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r3.omnilojoapps.com`, `direct_ip=47.89.227.180`, `g... |
| `8` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r4.omnilojoapps.com`, `direct_ip=47.88.77.74`, `gcp... |
| `9` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r4.omnilojoapps.com`, `direct_ip=47.88.77.74`, `gcp... |
| `10` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r5.omnilojoapps.com`, `direct_ip=47.251.174.192`, `... |
| `11` | `aws=game-lm-aws-r1.omnilojoapps.com`, `aws_ip_1=15.197.67.229`, `aws_ip_2=3.33.205.129`, `direct=game-lm-r5.omnilojoapps.com`, `direct_ip=47.251.174.192`, `... |

### `Global.LuaWebRequest` API
| Method | Params | Line | Discovered Endpoints |
|---|---:|---:|---|
| `DisposeRequest` | 1 | 0 | - |
| `Get` | 1 | 0 | - |
| `New` | 0 | 0 | - |
| `OnRequestFailure` | 2 | 0 | - |
| `OnRequestSuccess` | 2 | 0 | - |
| `OnRequestTimeout` | 1 | 0 | - |
| `OnUpdate` | 1 | 0 | - |
| `Post` | 2 | 0 | - |
| `PostJson` | 2 | 0 | - |
| `SendRequest` | 1 | 0 | - |
| `SetCallback` | 4 | 0 | - |
| `SetRequestHeader` | 3 | 0 | - |
| `__applyCertificateHandler` | 1 | 0 | - |
| `__delete` | 1 | 0 | - |
| `__init` | 3 | 0 | - |

### `Loading.*` State Machine & Login Modules (31 Modules)
| Module | Methods | Scalar Config Fields |
|---|---|---|
| `Loading.AppStartupLoading` | `BeginConnectFlow(1)`, `CancelAllPendingRequests(1)`, `CheckServerStateStop(1)`, `CheckUsePreload(1)`, `Clo... | `__cname=AppStartupLoading`, `__ctype=1` |
| `Loading.Const` | - | - |
| `Loading.GetResVersionUtil` | `BuildRequestParams(1)`, `DisableUpdate(1)`, `EnableUpdate(1)`, `GetGMFlag(1)`, `GetPackageName(1)`, `New(0... | `__cname=GetResVersionUtil`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.AppUpdateState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `ShowAppUpgradeMessage(2)`, `__init(2)` | `__cname=AppUpdateState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.AuthPinState` | - | `<REDACTED_SECRET>` |
| `Loading.LoadingState.CNIdentifyState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `ShowAuthUI()`, `__init(2)` | `__cname=AuthPinState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.CheckMainLevelResState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__isLevelDownloaded(2)`, `__onDownloadComplete(1)`, `_... | `__cname=CheckMainLevelRes`, `__ctype=1`, `__delete=False`, `__init=False` |
| `Loading.LoadingState.CheckOtaResState` | `DoNext(1)`, `GetCurrentSeasonId(1)`, `GetOtaDependences(1)`, `Is3v3On(1)`, `IsActivityOpenByEnum(2)`, `IsA... | `__cname=CheckOtaResState`, `__ctype=1`, `__delete=False`, `__init=False` |
| `Loading.LoadingState.CheckResVersionState` | `AppendFailedReason(4)`, `BuildRequestParams(1)`, `GetGMFlag(1)`, `GetPackageName(1)`, `GetUploadFailedStr(... | `__cname=CheckResVersionState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.CloudState` | `ApplyAndFinish(3)`, `GoStartConnect(2)`, `HasLocalLoginCache(1)`, `New(0)`, `OnCloudProfileResult(2)`, `On... | `__cname=CloudState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.ConnectGameState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnGameConnection(3)`, `OnGameConnectionError(2)`, `OnUpdate(1)`, `__i... | `__cname=ConnectGameState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.DownloadManifestState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__init(2)` | `__cname=DownloadManifestState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.DownloadUpdateState` | `CheckDeviceStorage(2)`, `GetDownloadManifest(2)`, `New(0)`, `OnDownloadComplete(1)`, `OnEnter(2)`, `OnExit... | `__cname=DownloadUpdateState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.EnterGameState` | `CheckHHIdentity(1)`, `EnterGame(1)`, `New(0)`, `OnEnter(2)`, `OnEnterGame(1)`, `OnExit(1)`, `OnUpdate(1)`,... | `__cname=EnterGameState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.EuropeanUnionPrivacyState` | `DoNext(1)`, `New(0)`, `OnEnter(2)`, `OnExit(1)` | `__cname=EuropeanUnionPrivacyState`, `__ctype=1`, `__delete=False`, `__init=F... |
| `Loading.LoadingState.GetServerListState` | `AppendFailedReason(3)`, `BuildRequestParams(1)`, `DebugConnectGameServer(5)`, `DisposeRequest(1)`, `GetCur... | `__cname=GetServerListState`, `__ctype=1`, `__delete=False`, `__init=False` |
| `Loading.LoadingState.GetServerStatusState` | `DisposeRequest(1)`, `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnGetServerStatus(4)`, `OnUpdate(1)`, `__init(2)` | `__cname=GetServerStatusState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.LoadDataTableState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__init(2)` | `__cname=LoadDataTableState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.LoadSceneState` | `DoFirstEnter(1)`, `LoadScene(1)`, `LogCostTime(2)`, `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `_... | `__cname=LoadSceneState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.LoadingErrorState` | `GetErrorMsg(2)`, `GetExtraErrorMsg(1)`, `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__init(2)` | `__cname=LoadingErrorState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.LoadingStateBase` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(2)` | `__cname=LoadingStateBase`, `__ctype=1` |
| `Loading.LoadingState.LoginState` | `DoSendLogin(1)`, `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__delete(1)`, `__init(2)` | `__cname=LoginState`, `__ctype=1` |
| `Loading.LoadingState.LogoState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `__init(2)` | `__cname=LogoState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.MailIdentifyState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `ShowAuthUI()`, `__init(2)` | `__cname=MailIdentifyState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.PINIdentifyState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `ShowAuthUI()`, `__init(2)` | `__cname=PINIdentifyState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.PermissionState` | `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `ReloadGame(1)`, `StartDownLoadConfigZip(1)`, `__delete... | `__cname=PermissionState`, `__ctype=1` |
| `Loading.LoadingState.PushInitState` | `DoRetry(1)`, `New(0)`, `OnEnter(1)`, `OnExit(1)`, `OnLoginComplete(1)`, `OnUpdate(1)`, `__init(2)` | `__cname=PushInitState`, `__ctype=1`, `__delete=False` |
| `Loading.LoadingState.WarmUpShaderState` | `DoNext(1)`, `GetCurWarmUpQueueCount(1)`, `New(0)`, `OnEnter(2)`, `OnExit(1)`, `OnUpdate(1)`, `StartWarmUp(1)` | `__cname=WarmUpShaderState`, `__ctype=1`, `__delete=False`, `__init=False` |
| `Loading.LoadingView2` | `Awake(1)`, `Delete(1)`, `Destroy(1)`, `DoInit(1)`, `InitLoadTips(1)`, `InitStateText(1)`, `InitUIComponent... | `__ctype=2`, `_last_process=1.0`, `isJP=False`, `isKR=False`, `isRefreshLocal... |
| `Loading.LoginAddrHelper` | `DisableUpdate(1)`, `DisposeRequest(1)`, `DoRequest(1)`, `EnableUpdate(1)`, `OnUpdate(1)`, `Start(1)`, `Sta... | `isStarted=True` |
| `Loading.Versions` | `CopyTempManifestToDownLoadPath(1)`, `OverrideManifest(1)` | - |

## 4. Native C# Network, SFS & HTTP Classes (20 Classes in `Assembly-CSharp`)

| C# Class | Static String Constants (Redacted) | Methods |
|---|---|---|
| `GameKit.Base.WebRequestManager` | `FILE_NO_EXISTS=file no exists` | `OnDisable(0)->Void`, `IsDownloadResult(2)->Boolean`, `LoadTexture(5)->Void`, `LoadTexture(6)->Void`, `Get(5)->Void`, `Post(6)->Void`, `Post(6)->Void`, `Post... |
| `GameKit.Base.WebRequestManager+OnWebReques...` | - | `Invoke(3)->Void`, `BeginInvoke(5)->IAsyncResult`, `EndInvoke(1)->Void` |
| `GameKit.Base.WebRequestManager+OnWebReques...` | - | `Invoke(2)->Void`, `BeginInvoke(4)->IAsyncResult`, `EndInvoke(1)->Void` |
| `GameKit.Base.WebRequestManager+WebRequestP...` | - | - |
| `Main.Scripts.Application.LoadingState.Http...` | - | `get_Timeout(0)->Single`, `set_Timeout(1)->Void`, `get_TryCount(0)->Int32`, `set_TryCount(1)->Void`, `get_isDone(0)->Boolean`, `get_error(0)->String`, `get_d... |
| `Main.Scripts.Application.LoadingState.Http...` | - | `ValidateCertificate(1)->Boolean` |
| `PostEventLog` | `POSTURL=https://analyse-lm.omnilojoapps.com/ballevent.php`, `POSTURL_Loading=https://statistics-lm.omniloj... | `Retry(1)->Void`, `SetLuaCallback(1)->Void`, `RecordInThread_LUA(3)->Void`, `RecordInThread(3)->Void`, `UpdateThreadRecord(0)->Int32`, `getActionCount(1)->In... |
| `PostEventLog+Defines` | `APP_PAUSE=APP_PAUSE`, `APP_QUIT=APP_QUIT`, `APP_RESUME=APP_RESUME`, `CDN_SWITCH=CDN_SWITCH`, `CHECK_VERSIO... | - |
| `PostEventLog+RecordMessage` | - | - |
| `Sfs2X.Core.Sockets.BestHttpWebSocketLayer` | - | `Connect(2)->Void`, `Disconnect(0)->Void`, `Disconnect(1)->Void`, `Kill(0)->Void`, `Write(3)->Void`, `Write(1)->Void`, `get_IsConnected(0)->Boolean`, `get_Re... |
| `UploadImageManager` | `CHAT_IMG_LOCAL_FOLDER=LocalChatImg`, `CHAT_UPLAOD_URL=https://upload-img-lm.omnilojoapps.com/s3_upload.php... | `get_Instance(0)->UploadImageManager`, `Purge(0)->Void`, `get_PHOTO_UPLOAD_URL(0)->String`, `OnUploadImage(3)->Void`, `OnImagePathOk(1)->Void`, `UploadHeadIm... |
| `UploadImageManager+CHAT_REQ_TYPE` | - | - |
| `UploadImageManager+CHAT_UPLOAD_STATUS` | - | - |
| `UrlUtils` | `HEAD_URL=https://lm-s3.omnilojoapps.com/ds/img/`, `HEAD_URL_MID=http://lm-s3.omnilojoapps.com:8086/ds/img/` | `IsUseCustomPic(1)->Boolean`, `GenCustomPicUrl(4)->Boolean` |
| `XLua.CSObjectWrap.GameKitBaseWebRequestMan...` | - | `__Register(1)->Void`, `__CreateInstance(1)->Int32`, `_m_IsDownloadResult(1)->Int32`, `_m_LoadTexture(1)->Int32`, `_m_Get(1)->Int32`, `_m_Post(1)->Int32`, `_... |
| `XLua.CSObjectWrap.MainScriptsApplicationLo...` | - | `__Register(1)->Void`, `__CreateInstance(1)->Int32`, `_m_SendRequest(1)->Int32`, `_m_Dispose(1)->Int32`, `_m_OnUpdate(1)->Int32`, `_g_get_Timeout(1)->Int32`,... |
| `XLua.CSObjectWrap.PostEventLogWrap` | - | `__Register(1)->Void`, `__CreateInstance(1)->Int32`, `_m_Retry_xlua_st_(1)->Int32`, `_m_SetLuaCallback_xlua_st_(1)->Int32`, `_m_RecordInThread_LUA_xlua_st_(1... |
| `XLua.CSObjectWrap.UnityEngineNetworkingUni...` | - | `__Register(1)->Void`, `__CreateInstance(1)->Int32`, `_g_get_webRequest(1)->Int32` |
| `XLua.CSObjectWrap.UnityEngineNetworkingUni...` | - | `__Register(1)->Void`, `__CastFrom(1)->Int32` |
| `XLua.CSObjectWrap.UnityEngineNetworkingUni...` | - | `__Register(1)->Void`, `__CreateInstance(1)->Int32`, `_m_ClearCookieCache_xlua_st_(1)->Int32`, `_m_Dispose(1)->Int32`, `_m_SendWebRequest(1)->Int32`, `_m_Abo... |

## 5. External Repository Endpoints & Google Apps Script Webhooks

### Verified External URLs Referenced in Repo Code
| Source File | Endpoint URL (Redacted) |
|---|---|
| `launcher/HeinZ Control Hub.py` | `https://script.google.com/macros/s/AKfycbwMVcm76RExNGoxHzWR4afOhHDIVyz--A4m4cG8IJ6PVrYofuPl5cbdS4ADFvXyoqYDdg/exec` |
| `launcher/HeinZ Control Hub.py` | `https://script.google.com/macros/s/AKfycbyXojj8Br_cvFVPpdp5CZpUQfvN_YBMWOQPIutG_1FeeoghayTGizhyg40boiPAE2Y7OQ/exec` |
| `launcher/app.py` | `https://script.google.com/macros/s/AKfycbwMVcm76RExNGoxHzWR4afOhHDIVyz--A4m4cG8IJ6PVrYofuPl5cbdS4ADFvXyoqYDdg/exec` |
| `launcher/app.py` | `https://script.google.com/macros/s/AKfycbyXojj8Br_cvFVPpdp5CZpUQfvN_YBMWOQPIutG_1FeeoghayTGizhyg40boiPAE2Y7OQ/exec` |
| `launcher/heinz_hub_web.py` | `https://dotnet.microsoft.com/download/dotnet-framework/net48` |
| `launcher/heinz_hub_web.py` | `https://go.microsoft.com/fwlink/p/?LinkId=2124703` |
| `launcher/heinz_hub_web.py` | `https://script.google.com/macros/s/AKfycbwMVcm76RExNGoxHzWR4afOhHDIVyz--A4m4cG8IJ6PVrYofuPl5cbdS4ADFvXyoqYDdg/exec` |
| `tools/build all bracket native sheets.py` | `https://docs.google.com/spreadsheets/d/{sheet_id` |

### JavaScript APIs & Webhook Receivers (`api/GoogleAppsScript_SyncReceiver.js`, `listeners/*.js`)
| File | Lines | HTTP Entrypoints | Functions |
|---|---:|---|---|
| `api/GoogleAppsScript_SyncReceiver.js` | 210 | `doPost`, `doGet` | `doPost(e)`, `doGet(e)`, `updateAllianceSheet(ss, alliance, stateId)`, `updateOverviewSheet(ss, alliances, timestampUtc, stateId)`, `form... |
| `listeners/capture alliance roster.js` | 140 | - | `getFieldString(name)`, `field(L, index, key)`, `readNumber(L, index)`, `readString(L, index)`, `readBoolean(L, index)` |
| `listeners/passive signal listener.js` | 126 | - | `allocStr(s)`, `field(L, index, key)`, `getString(L, index, maxLen = 256)`, `getNumber(L, index)`, `dumpLuaTable(L, index, depth = 0, max... |

## 6. Complete Python Module API Map Across Repo (114 Modules)

| Relative Path | Folder | Lines | Classes | Top-Level Functions | `MsgDefines` Used | HTTP Calls |
|---|---|---:|---|---|---|---|
| `api/batch fetch migration scores.py` | `api` | 319 | - | `get_tier_and_passes`, `on_message` | - | - |
| `api/batch fetch top10 scores.py` | `api` | 324 | - | `get_tier_and_passes`, `main` | - | - |
| `api/call dorequest.py` | `api` | 55 | - | - | - | - |
| `api/dump dorequest.py` | `api` | 64 | - | - | - | - |
| `api/inspect cs sfsnetwork.py` | `api` | 71 | - | - | - | - |
| `api/inspect network assistant.py` | `api` | 78 | - | - | - | - |
| `api/inspect network callers.py` | `api` | 103 | - | `on_msg` | - | - |
| `api/inspect sfs network.py` | `api` | 67 | - | - | - | - |
| `api/inspect sfs network2.py` | `api` | 81 | - | - | - | - |
| `api/sync state deep profiles.py` | `api` | 707 | - | `_resolve_active_pid`, `load_cache`, `save_cache`, `get_tier_and_passes`, `role_str`, `fetch... | - | - |
| `api/test call dorequest.py` | `api` | 54 | - | - | - | - |
| `api/test network assistant keys.py` | `api` | 65 | - | - | - | - |
| `api/test network assistant methods.py` | `api` | 70 | - | - | - | - |
| `api/trace protocal caller.py` | `api` | 55 | - | - | - | - |
| `api/trigger helicopter help.py` | `api` | 130 | - | `_resolve_pid`, `trigger_help` | - | - |
| `daemon/apply widescreen smooth map.py` | `daemon` | 1,687 | - | `_resolve_target`, `main` | - | - |
| `daemon/lastz auto engine daemon.py` | `daemon` | 1,838 | - | `log`, `attempt_patch`, `_load_client_discovery`, `attempt_farm_eco_patch`, `main` | AlHelpAll | - |
| `launcher/HeinZ Control Hub.py` | `launcher` | 2,455 | `HeinZ` (67m) | `log_crash`, `_resolve_repo_root`, `_resolve_python_cli`, `_hidden_startupinfo`, `_load_tool... | - | - |
| `launcher/app.py` | `launcher` | 2,455 | `HeinZ` (67m) | `log_crash`, `_resolve_repo_root`, `_resolve_python_cli`, `_hidden_startupinfo`, `_load_tool... | - | - |
| `launcher/heinz_hub_web.py` | `launcher` | 5,586 | `HubBackend` (74m) | `_dir_is_writable`, `_resolve_data_dir`, `_migrate_legacy_data`, `_ensure_std_streams`, `_ma... | ItemUse | - |
| `listeners/capture alliance roster.py` | `listeners` | 66 | - | - | - | - |
| `listeners/capture full packet2.py` | `listeners` | 73 | - | `on_msg` | - | - |
| `listeners/capture login traffic.py` | `listeners` | 79 | - | `on_msg` | - | - |
| `listeners/decode packet2.py` | `listeners` | 134 | `SFSDecoder` (8m) | - | - | - |
| `listeners/parse sfs packets.py` | `listeners` | 47 | - | - | - | - |
| `listeners/run bracket passive listener.py` | `listeners` | 225 | - | `on_message` | - | - |
| `listeners/run passive listener.py` | `listeners` | 48 | - | `on_message` | - | - |
| `listeners/sniff al rank.py` | `listeners` | 57 | - | `on_msg` | AlRank | - |
| `listeners/sniff packets.py` | `listeners` | 56 | - | `on_msg` | - | - |
| `listeners/sniff recv.py` | `listeners` | 56 | - | `on_msg` | GetNewUserInfo | - |
| `listeners/sniff user info.py` | `listeners` | 57 | - | `on_msg` | GetNewUserInfo | - |
| `listeners/test wsarecv count.py` | `listeners` | 36 | - | - | - | - |
| `telemetry/check update and ui.py` | `telemetry` | 53 | - | - | - | - |
| `telemetry/check v7 status.py` | `telemetry` | 89 | - | - | - | - |
| `telemetry/diag map preload.py` | `telemetry` | 137 | - | `main` | - | - |
| `telemetry/diag perf.py` | `telemetry` | 95 | - | - | - | - |
| `telemetry/inspect cam and renderers.py` | `telemetry` | 132 | - | `main` | - | - |
| `telemetry/inspect overlay state.py` | `telemetry` | 61 | - | - | - | - |
| `telemetry/inspect scenes.py` | `telemetry` | 99 | - | `main` | - | - |
| `telemetry/inspect tm.py` | `telemetry` | 107 | - | `main` | - | - |
| `telemetry/inspect uimanager.py` | `telemetry` | 57 | - | - | - | - |
| `telemetry/inspect windows.py` | `telemetry` | 64 | - | - | - | - |
| `telemetry/profile frame bottlenecks.py` | `telemetry` | 70 | - | - | - | - |
| `tools/analyze gear vehicle.py` | `tools` | 52 | - | - | - | - |
| `tools/analyze science progress.py` | `tools` | 100 | - | - | - | - |
| `tools/analyze session.py` | `tools` | 60 | - | - | - | - |
| `tools/analyze traffic log.py` | `tools` | 38 | - | - | - | - |
| `tools/apply remediation.py` | `tools` | 88 | - | `main` | - | - |
| `tools/auto detect environment.py` | `tools` | 246 | - | `_get_cd`, `_read_cached_env`, `_resolve_target_pid`, `detect_environment` | - | - |
| `tools/bot actions.py` | `tools` | 13,398 | - | `_clean_in_game_tips`, `_load_english_dialog`, `_localize_id`, `_used_formations_lua`, `_rec... | AcceptPersonalReward, AcceptPersonalRewardBatch, Ach... | - |
| `tools/bot_mine_melee.py` | `tools` | 1,221 | - | `_eval_mine_lua`, `_used_formations_lua`, `_record_used_formations`, `action_mine_melee_refr... | - | - |
| `tools/build all bracket native sheets.py` | `tools` | 629 | - | `role_str`, `get_tier_and_passes`, `generate_state_master_excel`, `upload_native_sheet`, `cl... | - | - |
| `tools/build top10 excel.py` | `tools` | 490 | - | `role_str` | - | - |
| `tools/client discovery.py` | `tools` | 1,061 | `_FridaSessionHolder` (3m) | `_hidden_subproc_kwargs`, `_decode_reg_bytes`, `read_readygo_registry`, `_read_app_info`, `_... | - | - |
| `tools/create styled excel.py` | `tools` | 201 | - | - | - | - |
| `tools/disasm monster.py` | `tools` | 84 | - | - | - | - |
| `tools/disasm wmo full.py` | `tools` | 76 | - | - | - | - |
| `tools/disasm wpo.py` | `tools` | 87 | - | - | - | - |
| `tools/disassemble wpm.py` | `tools` | 108 | - | `parse54`, `disasm54` | - | - |
| `tools/dump all buildings.py` | `tools` | 129 | - | `on_message` | - | - |
| `tools/dump all inventory.py` | `tools` | 131 | - | `on_message` | - | - |
| `tools/dump all player assets complete.py` | `tools` | 288 | - | `on_message` | - | - |
| `tools/dump extra wpm.py` | `tools` | 57 | - | - | - | - |
| `tools/dump heroes armies.py` | `tools` | 175 | - | `on_m` | - | - |
| `tools/dump optizone.py` | `tools` | 57 | - | - | - | - |
| `tools/dump science full.py` | `tools` | 146 | - | `on_message` | - | - |
| `tools/dump wpm functions.py` | `tools` | 124 | - | `main` | - | - |
| `tools/export alliance members excel.py` | `tools` | 119 | - | `build_alliance_members_excel` | - | - |
| `tools/export alliance roster excel.py` | `tools` | 92 | - | `build_roster_excel` | - | - |
| `tools/export high tier resources.py` | `tools` | 102 | - | `export_high_tier_resources` | - | - |
| `tools/export inventory excel.py` | `tools` | 142 | - | `export_inventory` | - | - |
| `tools/export map intelligence.py` | `tools` | 368 | - | `_resolve_target_pid`, `main` | - | - |
| `tools/export map summary excel.py` | `tools` | 106 | - | `build_map_summary_excel` | - | - |
| `tools/export tech tree excel.py` | `tools` | 167 | - | `build_tech_tree_excel` | - | - |
| `tools/export unshielded targets.py` | `tools` | 107 | - | `export_unshielded_targets` | - | - |
| `tools/export vs duel excel.py` | `tools` | 284 | - | `_resolve_target_pid`, `main` | AllianceCompeteRankList | - |
| `tools/export vs rankings.py` | `tools` | 271 | - | `main` | AllianceCompeteRankList | - |
| `tools/fetch all bracket alliances.py` | `tools` | 222 | - | `on_message` | AllianceRankLimit | - |
| `tools/fetch all bracket rosters.py` | `tools` | 262 | - | `on_message` | AlRank | - |
| `tools/fetch top10 rosters.py` | `tools` | 216 | - | `on_message` | AlRank | - |
| `tools/flush game memory.py` | `tools` | 120 | - | `_resolve_pid`, `flush_memory` | - | - |
| `tools/generate bracket sheets.py` | `tools` | 430 | - | `get_tier_and_passes`, `role_str`, `generate_state_workbook`, `main` | - | - |
| `tools/heinz_diagnostics.py` | `tools` | 782 | - | `_norm_tokens`, `redact_text`, `resolve_desktop_dir`, `_dir_writable`, `_is_admin`, `_scan_z... | - | - |
| `tools/inspect adjusters.py` | `tools` | 86 | - | - | - | - |
| `tools/inspect autoadjustlod.py` | `tools` | 73 | - | - | - | - |
| `tools/inspect buildasync upvalues.py` | `tools` | 111 | - | `main` | - | - |
| `tools/inspect deep urp and timers.py` | `tools` | 162 | - | `main` | - | - |
| `tools/inspect fow details.py` | `tools` | 96 | - | `main` | - | - |
| `tools/inspect input ui boomers.py` | `tools` | 61 | - | - | - | - |
| `tools/inspect lights fow.py` | `tools` | 98 | - | `main` | - | - |
| `tools/inspect lod methods.py` | `tools` | 99 | - | `main` | - | - |
| `tools/inspect monster.py` | `tools` | 68 | - | - | - | - |
| `tools/inspect optizone and close.py` | `tools` | 116 | - | `main` | - | - |
| `tools/inspect visibility gates.py` | `tools` | 146 | - | `main` | - | - |
| `tools/inspect wbo.py` | `tools` | 66 | - | - | - | - |
| `tools/inspect wir.py` | `tools` | 59 | - | - | - | - |
| `tools/inspect wpm internals.py` | `tools` | 169 | - | `main` | - | - |
| `tools/jump to target.py` | `tools` | 63 | - | `jump_camera` | - | - |
| `tools/launch_game.py` | `tools` | 24 | - | - | - | - |
| `tools/list wpm fns.py` | `tools` | 66 | - | - | - | - |
| `tools/multi client bot.py` | `tools` | 1,957 | - | `_hidden_subproc_kwargs`, `_clean_tips_list`, `_load_module`, `_configure_logging`, `_deep_m... | - | - |
| `tools/navigate to resource.py` | `tools` | 410 | - | `_load_cd`, `_lua_safe_encoder`, `scan_live_viewport_nodes`, `ensure_world_scene`, `find_via... | FindResourcePoint | - |
| `tools/print full tech trees.py` | `tools` | 83 | - | - | - | - |
| `tools/print heroes.py` | `tools` | 13 | - | - | - | - |
| `tools/print resolved inventory.py` | `tools` | 35 | - | - | - | - |
| `tools/probe world camera.py` | `tools` | 111 | - | `on_msg` | - | - |
| `tools/run enhanced diagnostics.py` | `tools` | 623 | - | `main` | - | - |
| `tools/sync all bracket states.py` | `tools` | 49 | - | `_load_sync_module`, `main` | - | - |
| `tools/sync bracket drive sheets.py` | `tools` | 1,186 | - | `_load_cd`, `_gsheets_bin`, `_run_gsheets`, `load_manifest`, `load_profile_cache`, `_atomic_... | AlRank, AllianceRankLimit | - |
| `tools/sync farm clients.py` | `tools` | 1,034 | - | `_load_module`, `file_sha256`, `get_main_client`, `client_needs_sync`, `patch_unity_identity... | - | - |
| `tools/test relief.py` | `tools` | 114 | - | - | - | - |
| `tools/test tile math.py` | `tools` | 62 | - | - | - | - |
| `tools/test urp patch.py` | `tools` | 129 | - | `main` | - | - |
| `tools/trace wpm build.py` | `tools` | 124 | - | `main` | - | - |
