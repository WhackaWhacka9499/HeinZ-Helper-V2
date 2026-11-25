# Domain Quick-Card: Trucks, Caravans & Hero Bounties (`trucks_bounties`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain trucks_bounties`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **0** bot fns / **0** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **2** packets |
| `DataCenter` Managers & Singletons | **0** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **1** windows / **2** active HUD buttons / **0** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **0** tables / **5** enums / **3** live events / **1** engine mods |

## 3. Key Wire Packets (2 total; top 2 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `get.mine.cave.record` | GetMineCavePlunderLog | `p=1`  | MineCaveManager.UpdatePlunderList | - |
| `push.new.mine.record` | PushNewMineCavePlunderLog | `p=1`  | MineCaveManager.OnRecvNewPlunderLog | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (1 windows)

**Active HUD Buttons:** `truckBtn` [] @ (1.8%,62.2%), `PlayerObj` [] @ (2.1%,3.9%)

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIXmasLuckyRollProb` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIXmasLuckyRollProb/UIXmasLuc...` | - | - |

## 5. Full XML Tables & Enums

**Enums:** `QualityTruckImagePath` (7), `NotPlunderReason` (6), `TruckQualityName` (5), `MineCavePlunderType` (4), `TruckIndexName` (4)
