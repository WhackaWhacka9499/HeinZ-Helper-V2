# Domain Quick-Card: Science, Research, Talents & Buffs (`science_research_talents`)

> **Auto-Compiled Unified Slice:** `2026-11-23 11:43:28 UTC` | **Instant CLI:** `python megamind/megamind_query.py fts <query> --domain science_research_talents`

| Layer | Count in This Domain |
|---|---:|
| HeinZ Tasks / Bot Functions / Routes | **0** tasks / **0** bot fns / **1** routes |
| Wire Packets (`MsgMap` + `SlgMsgMap`) | **11** packets |
| `DataCenter` Managers & Singletons | **0** managers |
| UI Windows & Prefabs / Active HUD Buttons / `GoToUtil` | **10** windows / **0** active HUD buttons / **1** jumps |
| Full XML Tables / Global Enums / Live `EventId`s / Engine Mods | **9** tables / **45** enums / **16** live events / **9** engine mods |

## 1. HeinZ Bot Tasks, Functions & Hub Routes

**Hub `action_id` Routes:** `export_tech` (L4836)

## 3. Key Wire Packets (11 total; top 11 shown)

| Wire Cmd | Alias(es) | Outgoing `Put*` | Incoming `DataCenter` | `EventId` |
|---|---|---|---|---|
| `change.desert.talent.page` | MasteryChangePlan | `p=2` PutInt | MasteryManager.HandleChangePlan | - |
| `change.desert.talent.page.name` | ChangeDesertTalentPageName | `p=3` PutInt, PutUtfString | MasteryManager.HandleChangePageName | - |
| `choose.base.talent` | ChooseBaseTalent | `p=2` PutInt | TalentDataManager.TalentChooseHandler | - |
| `learn.desert.talent.new` | MasteryLearn | `p=3` PutUtfString, PutInt | MasteryManager.HandleLearn | - |
| `push.base.talent` | PushBaseTalent | `p=1`  | TalentDataManager.TalentPushHandler | - |
| `push.desert.talent.extra.page.num` | PushDesertTalentExtraPageNum | `p=1`  | MasteryManager.HandleExtraPageNum | - |
| `push.desert.talent.level.info` | MasteryUpdate | `p=1`  | MasteryManager.HandleUpdate | - |
| `push.science.change` | PushScienceChange | `p=2`  | ScienceManager.PushScienceChangeHandle | - |
| `desert.talent.page.name.check` | DesertTalentPageNameCheck | `p=2` PutUtfString | - | PageNameCheckEvent |
| `push.dragon.server.effect.update` | PushDragonServerEffectUpdate | `p=1`  | - | - |
| `user.get.server.effect` | UserGetServerEffect | `p=1`  | - | - |

## 4. UI Windows, Prefabs, Live HUD Buttons & `GoToUtil` (10 windows)

**`GoToUtil` Routers:** `GoToUtil.OpenSciencePanel` -> ['UIScience']

| Window Name | Layer | Prefab Path | Key `btn*` Refs | Sends `MsgDefines` |
|---|---|---|---|---|
| `UIMasterySelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySelect.prefab` | Music_Effect_Button, ToggleBattle, ToggleBuild, batt... | MsgDefines.MasteryChangePlan |
| `UIMastery` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMastery.prefab` | Music_Effect_Button | - |
| `UIMasteryDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasteryDetail.prefab` | Music_Effect_Button | - |
| `TouchScreenEffect` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/TouchScreenEffect.prefab` | - | - |
| `UIDecorationEffect` | `UIContainer/Backg...` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationEffe...` | - | - |
| `UIDesertOperateBuffList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDesertOperateBuffList/UIDes...` | - | - |
| `UIMasteryExpTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMastery/UIMasteryTips.prefab` | - | - |
| `UIPhonographBuffDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographBuff...` | - | - |
| `UIScienceTab` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceTab.prefab` | - | - |
| `UIScienceTabLock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceTabLock.pr...` | - | - |

## 5. Full XML Tables & Enums

| XML Table | Aliases | Exact Rows | Columns |
|---|---|---:|---|
| `APS_science` | TableName.ScienceNew | 4,483 | id, science_id, level, max_level, tab, name, description, icon, color, position |
| `APS_talent` | TableName.Talent | 900 | id, talent_id, max_level, effect, level, type, name, desc, pos_x, pos_y |
| `effect_num_des` | TableName.EffectNumDesc | 747 | id, type, des, class, class_order, icon |
| `lw_buff` | TableName.LW_Buff | 355 | id, type, sub_type, para, buff_time, additive_type, max_level, group, active_effect, activin... |
| `masteryExp` | TableName.MasteryExp | 180 | id, level, Exp |
| `talent` | TableName.Talent_New | 35 | id, type, group, order, lv, name, effect_value, description, icon, resource |
| `effect` | xmlValue.effect | 22 | id, arm_all, arm_1, arm_2, arm_3 |
| `aps_science_tab` | TableName.APSScienceTab | 21 | id, name, position, order, quality, type, para1, unlock_level, building, icon_start |
| `talent_type` | TableName.TalentType | 4 | id, name, order |

**Enums:** `EffectDefine` (250), `GameEffectReason` (50), `EffectReasonType` (40), `EffectCoupleType` (20), `BuffType` (11), `EffectLocalType` (10), `MasteryTipState` (10), `EffectStateDefine` (8), `BuffReasonIcon` (6), `ScienceTab` (6), `BulletBuffType` (5), `EffectCategory` (5), `WeatherEffectOrder` (5), `WeatherEffectType` (5), `BuffSubType` (4), `EffectLocalTypeInEffectDesc` (4), `FogCanUnlockEffectAnimName` (4), `FogCanUnlockEffectAnimSort` (4), `ScienceColorBg` (4), `ScienceNameLockColor` (4), `ScienceNameUnlockColor` (4), `ScienceTabState` (4), `ScienceTabUnlockType` (4), `APSDamageEffectType` (3), `ChristmasParkourBuffType` (3)
