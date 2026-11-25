# Domain Quick-Card: Radar & Detect Events (`radar_detect`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain radar_detect`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **0** bot fns / **0** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **3** packets |
| `DataCenter` Managers & Singletons | **0** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **3** windows / **1** active HUD buttons / **0** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **0** tables / **3** enums / **3** live events / **0** engine mods |

## 3. Key Wire Packets (3 total; top 3 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `receive.detect.level.reward` | ReceiveDetectLevelReward | `p=1`  | RewardManager.ShowCommonReward | DetectInfoChangeClaimLevelReward |
| `upgrade.detect.power` | DetectPowerUpgrade | `p=1`  | RadarCenterDataManager.UpgradeDetectPowerInfo | UpgradeDetectPower |
| `finish.sampling` | FinishSampling | `p=2` PutLong | - | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (3 windows)

**Active HUD Buttons:** `radarObj` [] @ (1.8%,74.9%)

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIDetectHelpMessageBar` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIDetectHelpMessageBar...` | UIButton, closeBtnN, closeBtn_path | - |
| `UIAlarm` | `UIContainer/Dialog` | `Assets/Main/Prefabs/Slg/UI/UIAlarm/UIAlarm.prefab` | - | - |
| `UIRadarCloud` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRadarCloud/UIRadarCloud.prefab` | - | - |

## 5. Full XML Tables & Enums

**Enums:** `DetectEvenColorImage` (7), `DetectEvenColorSpecialImage` (7), `DetectOverlordEvenColorImage` (7)
