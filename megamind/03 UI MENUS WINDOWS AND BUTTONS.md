# Volume 03: Last Z UI Menus, Windows, Click Handlers & Live Button Screen Map

> **Generated:** `2026-11-23 10:42:43 UTC` | **Screen Resolution Captured:** `2560x1440` | **Source:** `megamind/raw/ui_windows_and_buttons.json`

## 1. UI System Summary

| UI Component | Verified Count | Notes |
|---|---:|---|
| `UIWindowNames` | **1,697** | Master window ID registry |
| `SlgUIWindowNames` | **181** | SLG engine window IDs |
| `UIConfig` Mappings | **1,625** | Window -> Lua Config module path |
| `UIConfig_SLG` Mappings | **48** | SLG window config paths |
| `UIManager` Layers | **11** | `UIContainer/*` z-ordering layers |
| Active Unity Canvases | **40** | Live HUD & overlay Canvas components |
| Live HUD & Cached `UIContainer` Buttons | **294** | **43** active visible + **251** cached panel buttons |
| Loaded UI View/Ctrl Modules Inspected | **304** | `package.loaded` UI classes |
| Mapped UI Click / Action Handlers | **1,052** | With outgoing `UIWindowNames` / `MsgDefines` / `DataCenter` targets |

## 2. UI Layer Hierarchy & Live Unity Canvases

### UIManager Layers
| Layer Path | Layer Properties |
|---|---|
| `UIContainer/Background` | __ctype=2, __name=UIContainer/Background, __var_arg=UIContainer/Background, activeSelf=True, isCreated=True, isFlexib... |
| `UIContainer/Dialog` | __ctype=2, __name=UIContainer/Dialog, __var_arg=UIContainer/Dialog, activeSelf=True, isCreated=True, isFlexible=True |
| `UIContainer/Guide` | __ctype=2, __name=UIContainer/Guide, __var_arg=UIContainer/Guide, activeSelf=True, isCreated=True, isFlexible=False |
| `UIContainer/Info` | __ctype=2, __name=UIContainer/Info, __var_arg=UIContainer/Info, activeSelf=True, isCreated=True, isFlexible=True |
| `UIContainer/Normal` | __ctype=2, __name=UIContainer/Normal, __var_arg=UIContainer/Normal, activeSelf=True, isCreated=True, isFlexible=True |
| `UIContainer/Scene` | __ctype=2, __name=UIContainer/Scene, __var_arg=UIContainer/Scene, activeSelf=True, isCreated=True, isFlexible=False |
| `UIContainer/TopCanvas` | __ctype=2, __name=UIContainer/TopCanvas, __var_arg=UIContainer/TopCanvas, activeSelf=True, isCreated=True, isFlexible... |
| `UIContainer/TopMax` | __ctype=2, __name=UIContainer/TopMax, __var_arg=UIContainer/TopMax, activeSelf=True, isCreated=True, isFlexible=False |
| `UIContainer/TopMost` | __ctype=2, __name=UIContainer/TopMost, __var_arg=UIContainer/TopMost, activeSelf=True, isCreated=True, isFlexible=False |
| `UIContainer/UIResource` | __ctype=2, __name=UIContainer/UIResource, __var_arg=UIContainer/UIResource, activeSelf=True, isCreated=True, isFlexib... |
| `WorldUIContainer` | __ctype=2, __name=WorldUIContainer, __var_arg=WorldUIContainer, activeSelf=True, isCreated=True, isFlexible=False |

## 3. Live On-Screen HUD Button Placement Map (43 Active Buttons @ 2560x1440)

> Coordinates use standard top-left origin (`x_pct: 0%..100%` left-to-right, `y_pct: 0%..100%` top-to-bottom). Buttons with `x_pct > 100%` or `< 0%` are off-screen collapsed drawers (e.g., slide-out Troop march panel).

### Screen Quadrant Overview (Active Buttons)
| Quadrant | Count | Visible Buttons (`Name [Label] @ x%,y%`) |
|---|---:|---|
| **Top-Left** | 9 | `PowerBtn` [166,160,000] (8.0%,2.3%), `14` [843.2M] (15.4%,2.4%), `1` [270.9M] (21.7%,2.4%), `2` [274.7M] (28.1%,2.4%), `PlayerObj` (2.1%,3.9%), `ItemBar_1` [16] (7.3%,5.7%), `VipBtn` [7] (1.6%,11.8%), `BuildQueueListBtn` [0/3] (1.7%,18.2%), `BuildScienceListBtn` [1/2] (1.7%,25.0%) |
| **Top-Center** | 2 | `12` [62.7M] (34.2%,2.4%), `Panel` [Troop 1 is back.] (50.0%,31.9%) |
| **Top-Right** | 8 | `goldStoreIcon` [4,947] (96.3%,2.4%), `btnAllPack` [15:30:39] (93.9%,8.3%), `btnActivity` [Event Center] (97.8%,8.3%), `holidayBtn` [Thanksgiving] (93.9%,15.2%), `limitBtn` [Hot Events] (97.8%,15.2%), `BtnCrossThrone` [State Ruler] (93.9%,22.0%), `UIMain_icon_AlCompete` [15:30:39] (97.8%,22.0%), `SeasonBtn` [01d 21h] (97.8%,28.8%) |
| **Middle-Left** | 1 | `truckBtn` (1.8%,62.2%) |
| **Middle-Center** | 1 | `UIPlayerHead` (39.6%,34.3%) |
| **Middle-Right** | 3 | `TroopCell` (115.5%,51.3%), `TroopCell_1` [1h34m] (115.5%,56.9%), `TroopCell_2` [2h8m] (115.5%,62.4%) |
| **Bottom-Left** | 7 | `dispatchBtn` (1.8%,68.6%), `radarObj` (1.8%,74.9%), `buildBtn` [2] (5.3%,80.8%), `btnBuild` (1.8%,81.0%), `HeadVX` (1.8%,87.5%), `RightBtn` (10.0%,88.4%), `btnHero` [Hero] (2.9%,96.2%) |
| **Bottom-Center** | 1 | `chatObj` [Evatrix:] (50.0%,96.9%) |
| **Bottom-Right** | 11 | `TroopCell_3` (115.5%,67.9%), `help` (94.4%,75.5%), `btnAlliance` [Alliance] (98.0%,75.5%), `btnMail` [Mail] (98.0%,81.7%), `GoodsBtn` [Warehouse] (98.0%,87.9%), `GroupIcon3` (91.5%,88.4%), `GroupIcon4` (92.5%,88.4%), `Btn` (92.0%,89.9%), `GroupIcon1` (91.5%,90.3%), `GroupIcon2` (92.5%,90.3%), `btn` (97.1%,96.2%) |

### Complete Active HUD Buttons Table
| Button Name | Label | Type | Quadrant | Center `(x%, y%)` | Pixels `(x, y, w×h)` | Unity Hierarchy Path |
|---|---|---|---|---|---|---|
| `chatObj` | Evatrix: | `NewButton` | Bottom-Center | `(50.0%, 96.9%)` | `(1280, 1396, 2266×89)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/chatObj` |
| `dispatchBtn` | - | `NewButton` | Bottom-Left | `(1.8%, 68.6%)` | `(45, 987, 89×89)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/dispatchBtn` |
| `radarObj` | - | `NewButton` | Bottom-Left | `(1.8%, 74.9%)` | `(45, 1078, 89×89)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/radarObj` |
| `buildBtn` | 2 | `NewButton` | Bottom-Left | `(5.3%, 80.8%)` | `(136, 1163, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/Layo...` |
| `btnBuild` | - | `NewButton` | Bottom-Left | `(1.8%, 81.0%)` | `(45, 1166, 89×89)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/btnBuild` |
| `HeadVX` | - | `NewButton` | Bottom-Left | `(1.8%, 87.5%)` | `(47, 1261, 68×78)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainQuest/Normal/HeadVX` |
| `RightBtn` | - | `NewButton` | Bottom-Left | `(10.0%, 88.4%)` | `(256, 1273, 343×61)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainQuest/Normal/Righ...` |
| `btnHero` | Hero | `NewButton` | Bottom-Left | `(2.9%, 96.2%)` | `(74, 1386, 147×108)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/btnHero` |
| `TroopCell_3` | - | `NewButton` | Bottom-Right | `(115.5%, 67.9%)` | `(2958, 978, 71×71)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopLi...` |
| `help` | - | `NewButton` | Bottom-Right | `(94.4%, 75.5%)` | `(2416, 1088, 74×74)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAll...` |
| `btnAlliance` | Alliance | `NewButton` | Bottom-Right | `(98.0%, 75.5%)` | `(2509, 1088, 90×90)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAll...` |
| `btnMail` | Mail | `NewButton` | Bottom-Right | `(98.0%, 81.7%)` | `(2509, 1177, 90×90)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnMail` |
| `GoodsBtn` | Warehouse | `NewButton` | Bottom-Right | `(98.0%, 87.9%)` | `(2509, 1266, 90×90)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/GoodsBtn` |
| `GroupIcon3` | - | `NewButton` | Bottom-Right | `(91.5%, 88.4%)` | `(2342, 1273, 25×25)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/Priva...` |
| `GroupIcon4` | - | `NewButton` | Bottom-Right | `(92.5%, 88.4%)` | `(2367, 1273, 25×25)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/Priva...` |
| `Btn` | - | `NewButton` | Bottom-Right | `(92.0%, 89.9%)` | `(2354, 1294, 81×96)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/Priva...` |
| `GroupIcon1` | - | `NewButton` | Bottom-Right | `(91.5%, 90.3%)` | `(2342, 1300, 25×25)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/Priva...` |
| `GroupIcon2` | - | `NewButton` | Bottom-Right | `(92.5%, 90.3%)` | `(2367, 1300, 25×25)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/Priva...` |
| `btn` | - | `NewButton` | Bottom-Right | `(97.1%, 96.2%)` | `(2486, 1386, 149×108)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/changeSceneObj/change...` |
| `UIPlayerHead` | - | `NewButton` | Middle-Center | `(39.6%, 34.3%)` | `(1014, 494, 71×71)` | `GameFramework/UI/UIContainer/TopMax/UICommonMessageBar/Panel/msgItem2/doTween/UIPlayerHead` |
| `truckBtn` | - | `NewButton` | Middle-Left | `(1.8%, 62.2%)` | `(45, 896, 89×89)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/truckBtn` |
| `TroopCell` | - | `NewButton` | Middle-Right | `(115.5%, 51.3%)` | `(2958, 739, 71×71)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopLi...` |
| `TroopCell_1` | 1h34m | `NewButton` | Middle-Right | `(115.5%, 56.9%)` | `(2958, 819, 71×71)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopLi...` |
| `TroopCell_2` | 2h8m | `NewButton` | Middle-Right | `(115.5%, 62.4%)` | `(2958, 899, 71×71)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopLi...` |
| `12` | 62.7M | `NewButton` | Top-Center | `(34.2%, 2.4%)` | `(875, 35, 141×39)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pi...` |
| `Panel` | Troop 1 is back. | `NewButton` | Top-Center | `(50.0%, 31.9%)` | `(1280, 459, 665×48)` | `GameFramework/UI/UIContainer/TopMax/UICommonMessageBar/Panel` |
| `PowerBtn` | 166,160,000 | `NewButton` | Top-Left | `(8.0%, 2.3%)` | `(205, 34, 208×51)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/Powe...` |
| `14` | 843.2M | `NewButton` | Top-Left | `(15.4%, 2.4%)` | `(394, 35, 154×39)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pi...` |
| `1` | 270.9M | `NewButton` | Top-Left | `(21.7%, 2.4%)` | `(556, 35, 154×39)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pi...` |
| `2` | 274.7M | `NewButton` | Top-Left | `(28.1%, 2.4%)` | `(719, 35, 154×39)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pi...` |
| `PlayerObj` | - | `NewButton` | Top-Left | `(2.1%, 3.9%)` | `(53, 56, 106×112)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/Head_Pivot/PlayerObj` |
| `ItemBar_1` | 16 | `NewButton` | Top-Left | `(7.3%, 5.7%)` | `(187, 82, 162×31)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_...` |
| `VipBtn` | 7 | `NewButton` | Top-Left | `(1.6%, 11.8%)` | `(42, 170, 81×86)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/VipBtn` |
| `BuildQueueListBtn` | 0/3 | `NewButton` | Top-Left | `(1.7%, 18.2%)` | `(44, 262, 92×92)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/BuildQueueListBtn` |
| `BuildScienceListBtn` | 1/2 | `NewButton` | Top-Left | `(1.7%, 25.0%)` | `(44, 360, 92×92)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/BuildScienceListBtn` |
| `goldStoreIcon` | 4,947 | `NewButton` | Top-Right | `(96.3%, 2.4%)` | `(2465, 35, 188×60)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pi...` |
| `btnAllPack` | 15:30:39 | `NewButton` | Top-Right | `(93.9%, 8.3%)` | `(2404, 120, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/pa...` |
| `btnActivity` | Event Center | `NewButton` | Top-Right | `(97.8%, 8.3%)` | `(2505, 120, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/bt...` |
| `holidayBtn` | Thanksgiving | `NewButton` | Top-Right | `(93.9%, 15.2%)` | `(2404, 218, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/pa...` |
| `limitBtn` | Hot Events | `NewButton` | Top-Right | `(97.8%, 15.2%)` | `(2505, 218, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/li...` |
| `BtnCrossThrone` | State Ruler | `NewButton` | Top-Right | `(93.9%, 22.0%)` | `(2404, 317, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/Bt...` |
| `UIMain_icon_AlCompete` | 15:30:39 | `NewButton` | Top-Right | `(97.8%, 22.0%)` | `(2505, 317, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/UI...` |
| `SeasonBtn` | 01d 21h | `NewButton` | Top-Right | `(97.8%, 28.8%)` | `(2505, 415, 94×94)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/Se...` |

### Cached / Panel Buttons Inside `UIContainer` (251 Buttons)
| Button Name | Label | Quadrant | Center `(x%, y%)` | Unity Hierarchy Path |
|---|---|---|---|---|
| `UIPlayerHead` | - | Bottom-Center | `(44.1%, 91.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/HotNewsNode/UIPlayerHead` |
| `HotNewsNode` | 热点新闻：联盟爆发超级战争！！ | Bottom-Center | `(48.9%, 91.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/HotNewsNode` |
| `WaitTimeObj_1` | 22:41:21 | Bottom-Left | `(5.7%, 69.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/BtnScout/UIFor...` |
| `WaitTimeObj_2` | 22:41:21 | Bottom-Left | `(5.7%, 74.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/BtnScout/UIFor...` |
| `ChatLoveBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/ChatLoveBtn` |
| `actBoss` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/actBoss` |
| `AllianceBoss` | 2d 08:45:39 | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/AllianceBoss` |
| `killMonsterBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/killMonsterBtn` |
| `killMonsterAlBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/killMonsterAlBtn` |
| `arenaBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/arenaBtn` |
| `DragonBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/DragonBtn` |
| `GloryDeclareBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/GloryDeclareBtn` |
| `migrateQuick` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/migrateQuick` |
| `btn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIFoodFestivalEat/b...` |
| `UIRotationBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIRotationBtn` |
| `btn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIIceCaveBubble/bg/btn` |
| `GovernmentBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/GovernmentBtn` |
| `UIDinosaurBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIDinosaurBtn` |
| `btn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UITradePostBubble/b...` |
| `ThroneBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/ThroneBtn` |
| `TerritoryCapturerBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/TerritoryCapturerBtn` |
| `CrossWonderBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/CrossWonderBtn` |
| `GovernmentPrepareBtn` | Name | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/GovernmentPrepareBtn` |
| `btn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIVolcanoBubble/bg/btn` |
| `btn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIVolcanoCommand/bg...` |
| `DragonSwapBtn` | Reward | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/DragonSwapBtn` |
| `PhonograpAttackBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/PhonograpAttackBtn` |
| `PhonograpHelpBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/PhonograpHelpBtn` |
| `GloryExchange` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/GloryExchange` |
| `GloryExchangeReceive` | Reward | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/GloryExchangeReceive` |
| `playBtn` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIWorldSiegeEntry/p...` |
| `UIWorldSiegeEntry` | - | Bottom-Left | `(0.0%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIWorldSiegeEntry` |
| `tips` | Your alliance hasn't declar... | Bottom-Left | `(8.5%, 78.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIWorldSiegeEntry/tips` |
| `buildBtn` | - | Bottom-Left | `(12.4%, 80.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/LayoutWarning/...` |
| `SearchBtn` | - | Bottom-Left | `(1.7%, 81.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/bottomLeft/Sea...` |
| `btnFightReward` | - | Bottom-Left | `(1.7%, 81.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/bottomLeft/btn...` |
| `BtnScout` | 0/3 | Bottom-Left | `(5.3%, 81.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/BtnScout` |
| `buildBtn` | - | Bottom-Left | `(5.3%, 81.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/LayoutWarning/...` |
| `valentineBtn` | - | Bottom-Left | `(3.6%, 84.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/LayoutWarning/...` |
| `hospitalBtn` | 2% | Bottom-Left | `(0.0%, 84.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/hospitalObj/ho...` |
| `HeadVX` | - | Bottom-Left | `(2.3%, 87.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainQuest/Advanced/HeadVX` |
| `RightBtn` | - | Bottom-Left | `(9.7%, 88.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainQuest/Advanced/RightBtn` |
| `Image` | - | Bottom-Left | `(11.3%, 93.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainQuest/UIArrow/RotationGo/Image` |
| `Image_1` | - | Bottom-Left | `(11.3%, 93.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainQuest/UIArrow/RotationGo/Im...` |
| `IconWeapon` | - | Bottom-Left | `(7.0%, 93.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/btnHero/btnHero_Pivot/btnHeroSP...` |
| `BlackKnightBtn` | 23s | Bottom-Left | `(0.0%, 100.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/BlackKnightBtn` |
| `enterBtn` | March | Bottom-Right | `(103.9%, 67.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `editBtn` | 0 | Bottom-Right | `(103.9%, 67.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `settingBtn` | - | Bottom-Right | `(111.3%, 67.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `BtnActive` | - | Bottom-Right | `(95.9%, 67.6%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `help_2` | Automatic help has been pro... | Bottom-Right | `(90.2%, 75.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAlliance/btnA...` |
| `haggle` | Favorited Items Arrival! | Bottom-Right | `(90.5%, 75.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAlliance/btnA...` |
| `autoJoin` | - | Bottom-Right | `(94.4%, 75.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAlliance/btnA...` |
| `newSkill` | - | Bottom-Right | `(94.4%, 75.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAlliance/btnA...` |
| `help_1` | - | Bottom-Right | `(94.9%, 75.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnAlliance/btnA...` |
| `ReportBg` | - | Bottom-Right | `(89.4%, 81.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnMail/ReportBg` |
| `PresidentBg` | - | Bottom-Right | `(94.4%, 81.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/LayoutBtnRight/btnMail/PresidentBg` |
| `PositionImg` | - | Bottom-Right | `(92.0%, 87.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/PrivateChatBubb...` |
| `PositionImg` | - | Bottom-Right | `(92.0%, 87.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `PositionImg` | - | Bottom-Right | `(91.5%, 88.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/PrivateChatBubb...` |
| `PositionImg` | - | Bottom-Right | `(91.5%, 88.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `Icon` | - | Bottom-Right | `(92.0%, 88.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlHitTurkeyNode/AlHitTurkeyBubb...` |
| `Icon` | - | Bottom-Right | `(92.0%, 88.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlHitTurkeyNode2/AlHitTurkeyBub...` |
| `PositionImg` | - | Bottom-Right | `(92.5%, 88.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/PrivateChatBubb...` |
| `PositionImg` | - | Bottom-Right | `(92.5%, 88.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `GroupIcon3` | - | Bottom-Right | `(91.5%, 88.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `Icon` | - | Bottom-Right | `(92.0%, 88.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlDigTreasureNode/AlDigTreasure...` |
| `Icon` | - | Bottom-Right | `(92.0%, 88.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PhonographNode/RadioStationChat...` |
| `GroupIcon4` | - | Bottom-Right | `(92.5%, 88.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `Icon` | - | Bottom-Right | `(91.8%, 88.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/TreasureChatNode/TreasureChatBu...` |
| `ChatHead` | - | Bottom-Right | `(92.0%, 88.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/PrivateChatBubb...` |
| `ChatHead` | - | Bottom-Right | `(92.0%, 88.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `Icon` | - | Bottom-Right | `(92.0%, 89.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlMoveChatNode/AlMoveChatBubble...` |
| `Icon` | - | Bottom-Right | `(92.0%, 89.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/ZendeskNode/ZendeskBubble/Icon` |
| `Bg` | - | Bottom-Right | `(91.8%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/TreasureChatNode/TreasureChatBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/TradepostNode/UITradepostBubble/Bg` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/RedenvelopeNode/UIRedenvelopeBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/RedenvelopeNode/UIRedenvelopeBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/RedenvelopeNode/UIRedenvelopeBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/RedenvelopeNode/UIRedenvelopeBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/RedenvelopeNode/UIRedenvelopeBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/RedenvelopeNode/UIRedenvelopeBu...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlMoveChatNode/AlMoveChatBubble/Bg` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/ZendeskNode/ZendeskBubble/Bg` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlDigTreasureNode/AlDigTreasure...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlHitTurkeyNode/AlHitTurkeyBubb...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/AlHitTurkeyNode2/AlHitTurkeyBub...` |
| `Bg` | - | Bottom-Right | `(92.0%, 89.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PhonographNode/RadioStationChat...` |
| `PositionImg` | - | Bottom-Right | `(91.5%, 89.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/PrivateChatBubb...` |
| `PositionImg` | - | Bottom-Right | `(91.5%, 89.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `Btn` | - | Bottom-Right | `(92.0%, 89.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `PositionImg` | - | Bottom-Right | `(92.5%, 89.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/PrivateChatNode/PrivateChatBubb...` |
| `PositionImg` | - | Bottom-Right | `(92.5%, 89.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `GroupIcon1` | - | Bottom-Right | `(91.5%, 90.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `GroupIcon2` | - | Bottom-Right | `(92.5%, 90.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/GolloesRewardChatNode/GolloesRe...` |
| `btnNotice` | Notice | Bottom-Right | `(96.4%, 95.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/SLGObject/Btns/btnNotice` |
| `btnStory` | Adventure | Bottom-Right | `(100.4%, 95.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/SLGObject/Btns/btnStory` |
| `btnLevel` | Stage | Bottom-Right | `(104.5%, 95.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/SLGObject/Btns/btnLevel` |
| `UIHeroCellSmall` | - | Middle-Center | `(42.3%, 34.3%)` | `GameFramework/UI/UIContainer/TopMax/UICommonMessageBar/Panel/msgItem2/doTween/Text/UIHeroCellSmall` |
| `WorldCenterBackBtn` | - | Middle-Center | `(50.0%, 50.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/centerLayer/WorldCenterBackBtn` |
| `panel` | - | Middle-Center | `(50.0%, 50.0%)` | `GameFramework/UI/UIContainer/TopMax/UIMultiLanguageFloatingBall/panel` |
| `secretObj` | - | Middle-Left | `(1.7%, 34.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/secretList/layout/allianceSecret1...` |
| `btn` | - | Middle-Left | `(1.7%, 38.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/SweepBubble/bg/btn` |
| `buildBtn` | - | Middle-Left | `(1.7%, 39.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/returnServerObj/buildBtn` |
| `Image` | - | Middle-Left | `(7.0%, 40.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/GloryAllianceCenterTips/Image` |
| `secretObj` | - | Middle-Left | `(1.7%, 41.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/secretList/layout/allianceSecret2...` |
| `MidBtnRed` | Disable Display | Middle-Left | `(-9.3%, 47.4%)` | `GameFramework/UI/UIContainer/TopMax/UIMultiLanguageFloatingBall/safeArea/BtnScore/BtnTip1/MidBtnRed` |
| `MidBtnBlue` | Text Rating | Middle-Left | `(-9.3%, 47.4%)` | `GameFramework/UI/UIContainer/TopMax/UIMultiLanguageFloatingBall/safeArea/BtnScore/BtnTip1/MidBtnBlue` |
| `MidBtnRed` | Disable Display | Middle-Left | `(3.2%, 47.4%)` | `GameFramework/UI/UIContainer/TopMax/UIMultiLanguageFloatingBall/safeArea/BtnScore/BtnTip/MidBtnRed` |
| `MidBtnBlue` | Text Rating | Middle-Left | `(3.2%, 47.4%)` | `GameFramework/UI/UIContainer/TopMax/UIMultiLanguageFloatingBall/safeArea/BtnScore/BtnTip/MidBtnBlue` |
| `SimpleBtn` | - | Middle-Left | `(12.5%, 49.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/SimpleBtn` |
| `KingdomSwapBtn` | Name | Middle-Left | `(19.6%, 49.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/KingdomSwapBtn` |
| `BtnScore` | Text Rating | Middle-Left | `(1.6%, 50.0%)` | `GameFramework/UI/UIContainer/TopMax/UIMultiLanguageFloatingBall/safeArea/BtnScore` |
| `btn` | - | Middle-Left | `(16.0%, 55.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIGhostGeneralBubbl...` |
| `btn` | - | Middle-Left | `(16.0%, 55.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIGhostKingBubble/b...` |
| `btn` | - | Middle-Left | `(16.0%, 55.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/UIDemonHunterBubble...` |
| `Btn` | Enable Low Graphics | Middle-Left | `(14.6%, 61.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft2/SimpleBtn/Expend/Bt...` |
| `WaitTimeObj` | 22:41:21 | Middle-Left | `(5.7%, 64.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/BtnScout/UIFor...` |
| `btnRank` | - | Middle-Right | `(97.5%, 35.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `killMonsterBtn` | - | Middle-Right | `(98.3%, 35.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `BtnSend` | - | Middle-Right | `(101.8%, 39.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `shareBtn` | - | Middle-Right | `(111.1%, 39.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `cancelButton` | - | Middle-Right | `(111.0%, 39.6%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `goBtn` | Go | Middle-Right | `(112.8%, 41.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(114.0%, 41.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `Info` | - | Middle-Right | `(110.5%, 41.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `UIPlayerHead` | - | Middle-Right | `(101.4%, 43.6%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(101.4%, 43.6%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `left` | Nameplayer [WAR] | Middle-Right | `(105.4%, 44.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `teamBtn` | - | Middle-Right | `(103.1%, 46.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `ShowBtn` | - | Middle-Right | `(115.5%, 47.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/ShowBtn` |
| `Button` | - | Middle-Right | `(115.5%, 47.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/bg/Button` |
| `HideBtn` | - | Middle-Right | `(123.5%, 47.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/HideBtn` |
| `RightUIPlayerHead` | - | Middle-Right | `(97.0%, 47.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `HideBtn` | - | Middle-Right | `(114.8%, 47.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/HideBtn` |
| `right` | Boomer | Middle-Right | `(97.0%, 47.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `posBtn` | - | Middle-Right | `(97.0%, 47.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `UIPlayerHead` | - | Middle-Right | `(101.2%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(101.2%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `UIPlayerHead` | - | Middle-Right | `(103.6%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(103.6%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `UIPlayerHead` | - | Middle-Right | `(106.0%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(106.0%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `UIPlayerHead` | - | Middle-Right | `(108.4%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(108.4%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `UIPlayerHead` | - | Middle-Right | `(110.8%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `join_btn` | - | Middle-Right | `(110.8%, 48.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `scoutFormation1` | - | Middle-Right | `(124.2%, 51.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `marchObj` | - | Middle-Right | `(124.2%, 51.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `lockObj` | - | Middle-Right | `(124.2%, 51.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `VIVIENBtn` | - | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `CarChipBtn` | Plugin Launch | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `RedEquipmentBtn` | Mythic Equipment | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `RedEquipmentBtn` | Mythic Forging | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `CarComponBtn` | Module Launch | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `CarComponBtn` | Doomsday Club | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `holidayBtn` | - | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `ironAgeBtn` | - | Middle-Right | `(96.1%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrancesMulti/entranc...` |
| `TeamLimit` | 1/13 | Middle-Right | `(104.4%, 52.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `Button_go` | Go | Middle-Right | `(107.2%, 53.5%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `loadBtn` | - | Middle-Right | `(95.8%, 54.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `funBtn` | - | Middle-Right | `(105.0%, 54.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `addBtn` | - | Middle-Right | `(107.9%, 54.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `battle_state_btn` | - | Middle-Right | `(112.0%, 54.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `enterBtn` | 0 | Middle-Right | `(108.0%, 55.7%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/CreateA...` |
| `BtnSend` | Rapid Strike | Middle-Right | `(103.1%, 55.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `stateBtn` | - | Middle-Right | `(95.3%, 56.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `addButton` | - | Middle-Right | `(110.3%, 56.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `scoutFormation2` | - | Middle-Right | `(124.2%, 56.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `marchObj` | - | Middle-Right | `(124.2%, 56.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `lockObj` | - | Middle-Right | `(124.2%, 56.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `ExpandBtn` | - | Middle-Right | `(93.0%, 57.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/SLGObject/ExpandBtn` |
| `Button_details` | Details | Middle-Right | `(99.0%, 57.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `Button_go` | Continue | Middle-Right | `(107.2%, 57.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `Common_duihao_kuang` | - | Middle-Right | `(96.8%, 58.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `enterBtn` | - | Middle-Right | `(103.3%, 58.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/RallyAr...` |
| `SmallBtnBlue` | Set | Middle-Right | `(110.5%, 59.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `Button_quit` | Quit | Middle-Right | `(113.2%, 60.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Allianc...` |
| `scoutFormation3` | - | Middle-Right | `(124.2%, 62.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `marchObj` | - | Middle-Right | `(124.2%, 62.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `lockObj` | - | Middle-Right | `(124.2%, 62.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/layout/sc...` |
| `BtnInfo` | - | Middle-Right | `(111.8%, 63.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/troopList/Formati...` |
| `InvestigateBtn` | Level up | Middle-Right | `(116.6%, 64.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/TroopFormation/scoutBg/ScoutSele...` |
| `BtnAdd` | - | Top-Center | `(37.7%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `UIPlayerHead` | - | Top-Center | `(39.6%, 27.6%)` | `GameFramework/UI/UIContainer/TopMax/UICommonMessageBar/Panel/msgItem1/doTween/UIPlayerHead` |
| `UIHeroCellSmall` | - | Top-Center | `(42.3%, 27.6%)` | `GameFramework/UI/UIContainer/TopMax/UICommonMessageBar/Panel/msgItem1/doTween/Text/UIHeroCellSmall` |
| `BtnAdd` | - | Top-Left | `(18.6%, 2.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `UIEnergySlider` | 8450/150 | Top-Left | `(12.4%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `Add` | - | Top-Left | `(14.1%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `goldObj` | 4,947 | Top-Left | `(15.3%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `objSoldier` | 17.7K | Top-Left | `(15.4%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `peopleObj` | 222.0k | Top-Left | `(15.4%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `BtnAdd` | - | Top-Left | `(18.6%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `BtnAdd` | - | Top-Left | `(18.6%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `Common_btn_add` | - | Top-Left | `(18.6%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `BtnAdd` | - | Top-Left | `(24.9%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `BtnAdd` | - | Top-Left | `(31.3%, 2.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/ResourceBar_Pivot/Resour...` |
| `ExitBtn` | - | Top-Left | `(18.6%, 4.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/Head_Pivot/ExitBtn` |
| `BtnAdd` | - | Top-Left | `(9.8%, 6.1%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `ItemBar_2` | -11445 | Top-Left | `(3.9%, 6.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `seasonBtn` | 8/10 | Top-Left | `(3.9%, 6.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `InfoBtn` | - | Top-Left | `(4.1%, 6.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `BtnAdd` | - | Top-Left | `(9.6%, 7.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `BtnAdd` | - | Top-Left | `(9.6%, 7.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `DayNightS5` | Dark Time | Top-Left | `(8.9%, 8.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `WarFeverBtn` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `WarDefenceBtn` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_loot` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_Buff` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_DragonBoss` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_PresentBuff` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_Bufftips` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_OfficialBuff` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_AlCompetePoint` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Btn_AllianceDeclare` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `thanksgivingStarBtn` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `PhonographBuff1` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `PhonographBuff2` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `PhonographBuff3` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `VolcanoBuff1` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `VolcanoBuff2` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `svsBuff1` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `svsBuff2` | - | Top-Left | `(3.9%, 10.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `BtnInfo` | - | Top-Left | `(8.8%, 11.6%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/topLayer/SLGObject/SLG_Pivot/SLG_BtnList_Pi...` |
| `Panel` | - | Top-Left | `(6.4%, 13.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/bottomLeft_Pivot/BtnScout/UIFor...` |
| `CrossFightBack` | - | Top-Left | `(13.8%, 14.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/bottomLayer/CrossFight/CrossFightBack` |
| `SnowBtn` | 22:26 | Top-Left | `(1.7%, 19.9%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/SnowBtn` |
| `troopBtn` | - | Top-Left | `(12.7%, 26.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/troopLayout/troopObj/troopBtn` |
| `troopBtn` | - | Top-Left | `(12.7%, 26.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/troopLayout/scoutTroopObj/troopBtn` |
| `troopBtn` | - | Top-Left | `(12.7%, 26.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/troopLayout/helpTroopObj/troopBtn` |
| `fishingTroopObj` | Fishing Queue | Top-Left | `(5.0%, 26.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/troopLayout/fishingTroopList/fish...` |
| `troopObj` | March1 | Top-Left | `(6.1%, 26.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/troopLayout/troopObj` |
| `scoutTroopObj` | March1 | Top-Left | `(6.1%, 26.4%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/troopLayout/scoutTroopObj` |
| `SpearMainBtn` | 1 | Top-Left | `(1.7%, 29.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/SpearMainBtn` |
| `Arrow` | - | Top-Left | `(11.1%, 30.6%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/leftLayer/UIMainPiontSpear/Arrow` |
| `ShowActivityBtn2` | - | Top-Right | `(91.0%, 8.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/ShowActivity...` |
| `UIMain_icon_firstPay` | 1st Buy | Top-Right | `(93.9%, 8.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/UIMain_icon_...` |
| `UIMain_AccountBind` | Account | Top-Right | `(93.9%, 8.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/UIMain_Accou...` |
| `ChainPayBtn` | - | Top-Right | `(93.9%, 8.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/ChainPayBtn` |
| `ShowActivityBtn1` | - | Top-Right | `(97.8%, 8.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/ShowActivityBtn1` |
| `btnChampionBattle` | Champion Duel | Top-Right | `(97.8%, 8.3%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/btnChampionB...` |
| `SevenDayBtn` | - | Top-Right | `(93.9%, 15.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/SevenDayBtn` |
| `VolcanoWarBtn` | - | Top-Right | `(93.9%, 15.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/VolcanoWarBtn` |
| `btnFirstPay` | 1st Buy | Top-Right | `(93.9%, 15.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/packageGridL...` |
| `btnGiftPackage` | Pack Shop | Top-Right | `(97.8%, 15.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/btnGiftPackage` |
| `UIMain_QuestionNaire` | Survey | Top-Right | `(97.8%, 15.2%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/UIMain_Quest...` |
| `strongCommanderBtn` | - | Top-Right | `(97.8%, 22.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/strongComman...` |
| `BtnDragon` | Canyon Clash | Top-Right | `(97.8%, 22.0%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/BtnDragon` |
| `BtnThrone` | Capital Clash | Top-Right | `(97.8%, 28.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/BtnThrone` |
| `btnPopPack` | - | Top-Right | `(97.8%, 28.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/btnPopPack` |
| `fireStarBtn` | Rate Us | Top-Right | `(97.8%, 28.8%)` | `GameFramework/UI/UIContainer/Background/MainUI_SU/safeArea/rightLayer/SLGObject/entrances/fireStarBtn` |

## 4. UI View / Controller Click & Action Handler Routing (1,052 Handlers)

| UI Module | Handler Method | Params | Opens `UIWindowNames` | Sends `MsgDefines` | Calls `DataCenter.*` |
|---|---|---:|---|---|---|
| `Net.Msgs.RecycleSkinItem` | `OnCreate` | 3 | - | - | - |
| `Net.Msgs.SurvivalHeroCollectionRewardView` | `OnCreate` | 1 | - | - | - |
| `Slg.DataCenter.DesertData.SeasonRewardItem` | `GetSelfRewardData` | 1 | - | - | DesertData |
| `Slg.DataCenter.DesertData.SeasonRewardItem` | `ReceiveSelfReward` | 1 | - | - | DesertData |
| `Slg.DataCenter.MailDataV4.Resolver.MailReward...` | `InstantiateRewardItem` | 3 | - | - | MailDataV4 |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `OnClickGrid` | 1 | - | - | CastleAdventureManager |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `SetDataByAnchoredPos` | 5 | - | - | CastleAdventureManager |
| `Slg.UI.CastleAdventure.CastleAdventureMap.Com...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasActSevenDaySignI...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasActSevenDaySignI...` | `OnInfoClick` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasActSevenDaySignI...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasActSevenDaySignI...` | `OnGetClick` | 1 | - | - | ActSevenLoginBuyData |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnClickClaimRewardBtn` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnClickGetFree` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnClickGetMore` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnClickGetMoreProtect` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnClickGotoBase` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnClickUseProtectItem` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `OnInfoClick` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasDecoration.Chris...` | `UpdateGetFreeBtnState` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasParkour.Christma...` | `OnClickJumpBtn` | 1 | ChristmasParkourAnimal | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Christma...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Christma...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Christma...` | `OnLevelUpClick` | 1 | ChristmasParkourAttribute | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Shop.Com...` | `ConfirmProcessPurchase` | 1 | - | BuyCommonShopGoods | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Shop.Com...` | `OnBuySuccCallBack` | 2 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Shop.Com...` | `OnClickBuyBtn` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Shop.Com...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasParkour.Shop.Com...` | `TryToBuy` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasPr...` | `GetActReward` | 2 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `BtnClick_JoinAl` | 1 | UIAllianceIntro | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnClickGotoTree` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnClickPass` | 1 | ChristmasActReward | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnClickRank` | 1 | UIChristmasRankPanel | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnClickReward` | 1 | ChristmasActPersonReward | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnClickTask` | 1 | ChristmasActTask | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnclickPresent` | 1 | - | - | ChristmasActManager |
| `Slg.UI.ChristmasAct.ChristmasWood.ChristmasWo...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `BlindBoxStageRewardCallback` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `GetProgressRewardPoint` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `GetRewardCount` | 3 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `InitBlindBoxReward` | 1 | - | - | BlindBoxManager |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `InitSelect` | 1 | - | - | BlindBoxManager |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickAutoBtn` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickBoxRewardBtn` | 1 | UIBlindBoxRewardOpenView | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickChangeBtn` | 1 | UIBlindBoxSelectBoxChristmasView | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickGiftBtn` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickInfoBtn` | 1 | UIBlindBoxRuleChristmasView | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickPackage` | 1 | UIGiftBoxPackageList | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickRewardBtn` | 1 | UIChristmasLevelRewardPanel | - | BlindBoxManager |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickShopBtn` | 1 | UIBlindBoxShopView | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickSpeedBtn` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnClickStartBtn` | 2 | UIBlindBoxSelectBoxChristmasView | - | BlindBoxManager |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `ReceiveBlindBoxTempRewardCallback` | 2 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `RefreshBoxRewardRed` | 1 | - | - | BlindBoxManager |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `RefreshSelect` | 2 | - | - | - |
| `Slg.UI.ChristmasAct.UIChristmasBlindBoxPanel....` | `UpdateRewardState` | 1 | - | - | BlindBoxManager |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnClickCheckBoxBtn` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnClickGetGiftBtn` | 1 | - | - | TurkeyCookManager |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnClickInfoBtn` | 1 | UIFoodFestivalCommonIntroPanel | - | - |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnGetBtnClick` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `ShopItemClickCallBack` | 2 | - | - | - |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `ConfirmProcessPurchase` | 1 | - | BuyCommonShopGoods | - |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnBuySuccCallBack` | 2 | - | - | RewardManager |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnClickBuyBtn` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActExchangeShopPanel...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActItemDropPanel.Act...` | `OnClickInfoBtn` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActItemDropPanel.Act...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActItemDropPanel.Act...` | `OnCreateCell` | 3 | - | - | - |
| `Slg.UI.CommActivityPanel.ActItemDropPanel.Act...` | `OnClickJumpBtn` | 1 | - | - | QuestTemplateManager |
| `Slg.UI.CommActivityPanel.ActItemDropPanel.Act...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnClickBoxLock` | 1 | UIBattlePassGiftPackagePopUp | - | - |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnClickBuyBtn` | 1 | UIActivityCenterTable | - | ActBattlePassData |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnClickInfoBtn` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnClickOneGet` | 1 | - | ReceiveBattlePassAllReward | ActBattlePassData |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnClickSelect` | 1 | UIBPSelectPack | - | - |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.CommActivityPanel.ActPassPanel.ActPass...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Easter.EasterSevenDay.SevenDayVipAttSn...` | `GetCurTabAllRedNum` | 2 | - | - | TaskManager |
| `Slg.UI.Easter.EasterSevenDay.SevenDayVipAttSn...` | `GetSevenDayTaskReward` | 2 | - | TaskRewardGet | - |
| `Slg.UI.Easter.EasterSevenDay.SevenDayVipAttSn...` | `RewardItemList` | 2 | - | - | ItemTemplateManager |
| `Slg.UI.Easter.EasterSevenDay.UIActivitySevenD...` | `OnClickGo` | 1 | - | - | QuestTemplateManager |
| `Slg.UI.Easter.EasterSevenDay.UIActivitySevenD...` | `OnClickReward` | 1 | - | - | - |
| `Slg.UI.Easter.EasterSevenDay.UIActivitySevenD...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Easter.EasterSevenDay.UIActivitySevenD...` | `QuestRewardSuccess` | 2 | - | - | - |
| `Slg.UI.Easter.EasterSevenDay.UIActivitySevenD...` | `RefreshReward` | 2 | - | - | - |
| `Slg.UI.Easter.EasterSevenDay.UIActivitySevenD...` | `TaskRewardInfoUpdate` | 1 | - | - | - |
| `Slg.UI.Easter.UIBlindBoxEaster.Component.UIBl...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.FestivalAct.Holiday.Thanksgiving2026.T...` | `GetActReward` | 2 | - | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickBuildBtn` | 1 | UIAllianceCity | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickBuyBtn` | 1 | UIFoodFestivalEatExchangeView | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickBuyRecordBtn` | 1 | UIFoodFestivalEatExchangeRecordView | - | AllianceMineManager |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickEatBtn` | 1 | - | - | AllianceMineManager |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickGoBtn` | 1 | - | - | ActivityListDataManager |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickInfoBtn` | 1 | UIFoodFestivalEatRuleView | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickJoinAllianceBtn` | 1 | UIAllianceIntro | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickListBtn` | 1 | UIFoodFestivalEatListView | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickRankBtn` | 1 | UIThanksGivingRankPanel | - | TurkeyCookManager |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickRecordBtn` | 1 | UIFoodFestivalEatSelfRecordView | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickReserveBtn` | 1 | UIFoodFestivalEatReserveView | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnClickRewardBtn` | 1 | UIFoodFestivalEatRuleView | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.FoodFestivalEat.UIFoodFestivalEatView....` | `SetEatTableInfo` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.C...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `BlindBoxStageRewardCallback` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `GetProgressRewardPoint` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `GetRewardCount` | 3 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `InitSelect` | 1 | - | - | BlindBoxManager |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickAutoBtn` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickBoxRewardBtn` | 1 | UIBlindBoxRewardOpenView | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickChangeBtn` | 1 | UIBlindBoxSelectBoxView | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickGiftBtn` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickInfoBtn` | 1 | UIBlindBoxRuleView | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickRewardBtn` | 1 | UIBlindBoxScoreView | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickShopBtn` | 1 | UIBlindBoxShopView | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickSpeedBtn` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnClickStartBtn` | 2 | - | - | BlindBoxManager |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `ReceiveBlindBoxTempRewardCallback` | 2 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `RefreshBoxRewardRed` | 1 | - | - | BlindBoxManager |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `RefreshSelect` | 2 | - | - | - |
| `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxPanel.V...` | `UpdateRewardState` | 1 | - | - | BlindBoxManager |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnClickGotoBtn` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnClickInfoBtn` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnClickItemBtn` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnClickListBtn` | 1 | UIConcertListView | - | - |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnClickRewardBtn` | 1 | UIConcertRateView | - | - |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnClickUseBtn` | 1 | - | ConcertItemUse | ItemData |
| `Slg.UI.Oktoberfest.Concert.UIConcertView.View...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.UIMusicMainPanel.Component...` | `OnCreate` | 3 | - | - | - |
| `Slg.UI.Oktoberfest.UIMusicMainPanel.Component...` | `OnCreate` | 2 | - | - | - |
| `Slg.UI.Oktoberfest.UIMusicMainPanel.Component...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Oktoberfest.UIMusicMainPanel.Component...` | `OnInfoClick` | 1 | - | - | ActivityListDataManager |
| `Slg.UI.Oktoberfest.UIMusicMainPanel.Component...` | `OnPreBtnClick` | 1 | UIMusicFestivalGameScene | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookAnim...` | `OnClickStopBtn` | 1 | - | - | TurkeyCookManager |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookAnim...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookFini...` | `OnClickBtn` | 1 | UIThanksGivingRankPanel | - | TurkeyCookManager |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookFini...` | `OnClickCookRequest` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookFini...` | `OnClickSubmit` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookFini...` | `OnClickUseBag` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookFini...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookInfo...` | `OnClickCook` | 1 | UITurkeyCookDetailsPanel | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookInfo...` | `OnClickGiftBtn` | 1 | UIGiftBoxPackageList | - | TurkeyCookManager |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookInfo...` | `OnClickSendTurkey` | 1 | ThanksGivingTurkeySelectPlayerPanel | - | TurkeyCookManager |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookInfo...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookPanel` | `OnClickCookRequest` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookPanel` | `OnClickInfo` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookPanel` | `OnClickSubmit` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookPanel` | `OnClickUseBag` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookPanel` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.UIThanksgivingStarView.Vi...` | `OnClickInfoBtn` | 1 | - | - | - |
| `Slg.UI.Thanksgiving.UIThanksgivingStarView.Vi...` | `OnClickListBtn` | 1 | UIThanksgivingStarListView | - | - |
| `Slg.UI.Thanksgiving.UIThanksgivingStarView.Vi...` | `OnClickRankBtn` | 1 | UIThanksgivingStarRankView | - | - |
| `Slg.UI.Thanksgiving.UIThanksgivingStarView.Vi...` | `OnClickReceivedBtn` | 1 | UIThanksgivingStarScoreView | - | - |
| `Slg.UI.Thanksgiving.UIThanksgivingStarView.Vi...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIAlarm.View.UIAlarmView` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarDetail.Compone...` | `OnCancelClick` | 1 | - | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarDetail.Compone...` | `OnCreate` | 2 | - | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnBtnSendClick` | 1 | - | - | AllianceWarDataManager |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnCancelClick` | 1 | - | - | AllianceWarDataManager |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnCreate` | 2 | - | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnDetailClick` | 1 | UIAllianceWarInfoView | AllianceMarchArmyInfo | AllianceWarDataManager |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnGoBtnClick` | 1 | - | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnJoinBtnClick` | 1 | - | - | AllianceWarDataManager |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnRightPosClick` | 1 | - | - | AllianceWarDataManager |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `OnShareClick` | 1 | UIPositionShare | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `RefreshJoinBtn` | 1 | - | - | - |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `RefreshManualMarchBtn` | 1 | - | - | AllianceWarDataManager |
| `Slg.UI.UIAlliance.UIAllianceWarMainTable.Comp...` | `SendDirectMove` | 2 | - | AllianceTeamDirectMove | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnClickFoodEat` | 1 | - | - | ActivityListDataManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnClickInfo` | 1 | UIFoodFestivalCommonIntroPanel | - | ActivityListDataManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnClickRankBtn` | 1 | UIFoodFestivalRankPanel | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnClickReward` | 1 | UIFoodFestivalRewardPanel | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnInfoClick` | 1 | UIFoodFestivalCommonIntroPanel | - | ActivityListDataManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnBtnClick` | 1 | - | ReceiveBalloonPuzzleReward | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnClickTask` | 1 | - | - | TaskManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.F...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickStopBtn` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickBg` | 1 | UIFoodFestivalCookDetailsPanel | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickCookRequest` | 1 | UIFoodFestivalExchangePanel | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickInfo` | 1 | UIFoodFestivalCookRule | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickSubmit` | 1 | - | - | ActivityListDataManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickUseBag` | 1 | - | ItemUse | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickUseBag2` | 1 | - | ItemUse | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `SetCookBtnPos` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickCookRequest` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickInfo` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickSubmit` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickUseBag` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickCheckBoxBtn` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickInfoBtn` | 1 | UIFoodFestivalCommonIntroPanel | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnGetBtnClick` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `ShopItemClickCallBack` | 2 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `ConfirmProcessPurchase` | 1 | - | BuyCommonShopGoods | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnBuySuccCallBack` | 2 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickBuyBtn` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickInfoBtn` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickJumpBtn` | 1 | - | - | QuestTemplateManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickReward` | 1 | - | - | CumulativeRechargeManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickSkin` | 1 | UIPreviewSkinPanel | - | ItemTemplateManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreateCell` | 3 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `RewardUpdate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `FoodFestivalUpdateFreeReward` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickGotoCook` | 1 | - | - | ActivityListDataManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickInfo` | 1 | UIFoodFestivalCommonIntroPanel | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickRank` | 1 | UIFoodFestivalRewardPanel | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickRankBtn` | 1 | UIFoodFestivalRankPanel | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `SetFirstFoodSubmitBtnPos` | 1 | - | - | FoodFestivalManager |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnClickBtn` | 1 | UIFoodFestivalUseFoodPanel | - | - |
| `Slg.UI.UIFoodFestivalActListPanel.Component.U...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGeneralComponent.UIActGeneralPreview...` | `GetActReward` | 2 | - | - | - |
| `Slg.UI.UIGeneralComponent.UIActGeneralPreview...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGeneralComponent.UIActGeneralPreview...` | `OnInfoClick` | 1 | - | - | ActivityListDataManager |
| `Slg.UI.UIGeneralComponent.UIActivityTopCtrl` | `OnClickInfo` | 1 | - | - | - |
| `Slg.UI.UIGeneralComponent.UIActivityTopCtrl` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGeneralComponent.UIConsumeBarItem` | `OnClickBtn` | 1 | - | - | - |
| `Slg.UI.UIGeneralComponent.UIConsumeBarItem` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnChangePartBtnClick` | 1 | - | - | GivingRosesActManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickGetMore` | 1 | - | - | GivingRosesActManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickRewardBtn` | 1 | GivingRoseLevelRewardPanel | - | GivingRosesActManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnIntroBtnClick` | 1 | UICommonIntroTipActGivingRoses | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnRewardBtnClick` | 1 | UIGivingRosesRewardPanel | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnViewAllRankBtnClick` | 1 | UIGivingRosesSelectPlayerPanel | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `RefreshLevelReward` | 1 | - | - | GivingRosesActManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnGiveBtnClick` | 1 | - | - | DecorationDataManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnHistoryBtnClick` | 1 | UIGivingRosesHistoryPanel | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnShareBtnClick` | 1 | - | - | GivingRosesActManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnShowBntClick` | 1 | UIOtherPlayerInfo | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnShareBtnClick` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnShowBntClick` | 1 | UIOtherPlayerInfo | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickInfoBtn` | 1 | UICommonIntroTipActGivingRoses | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickJumpBtn` | 1 | - | - | QuestTemplateManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnGiveBtnClick` | 1 | - | - | DecorationDataManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnHistoryBtnClick` | 1 | UIGivingRosesHistoryPanel | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnRceiverClick` | 1 | UIOtherPlayerInfo | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnSenderClick` | 1 | UIOtherPlayerInfo | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `CycleRewardCallBack` | 2 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `DefaultSelectBox` | 1 | - | - | ItemData |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `DefineToggle` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `LevelRewardCallBack` | 2 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnBuyPackageSuccess` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickCycleRewardBtn` | 1 | - | CycleBoxReceiveCycleReward | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickGiftBtn` | 1 | UICycleBoxExchangeView | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickInfoBtn` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickLeftBtn` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickLockBtn` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickOpenBtn` | 1 | - | - | ItemData |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickPreviewBtn` | 1 | UICycleBoxRewardPreView | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickRewardViewBtn` | 1 | UICycleBoxScoreRewardView | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnClickRightBtn` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `RefreshLevelReward` | 1 | - | - | RewardManager |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `RefreshShowRewards` | 1 | - | - | - |
| `Slg.UI.UIGivingRosesAct.UIGivingRosesActListP...` | `ToggleControlBorS` | 2 | - | - | - |
| `Slg.UI.UIMailNew.UIMailMainPanel.Component.Ma...` | `OnBtnClick` | 1 | - | - | RewardManager |
| `Slg.UI.UIMailNew.UIMailMainPanel.Component.Ma...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIMailNew.UIMailMainPanel.Component.Ma...` | `OnBtnClick` | 1 | UIOtherPlayerInfo | - | - |
| `Slg.UI.UIMailNew.UIMailMainPanel.Component.Ma...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIMailNew4.UIMailMainPanel.Component.M...` | `OnBtnClick` | 1 | - | - | RewardManager |
| `Slg.UI.UIMailNew4.UIMailMainPanel.Component.M...` | `OnCreate` | 1 | - | - | - |
| `Slg.UI.UIMailNew4.UIMailMainPanel.Component.M...` | `OnBtnClick` | 1 | UIOtherPlayerInfo | - | - |
| `Slg.UI.UIMailNew4.UIMailMainPanel.Component.M...` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Framework.UI.Base.UIBaseView` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Framework.UI.Component.GridInfinity...` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Framework.UI.Component.HorizontalIn...` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Framework.UI.Component.UICenterScro...` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Framework.UI.Component.UIScrollView` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Framework.UI.Component.UIUnlimitedS...` | `OnCreate` | 1 | - | - | - |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchE...` | `HideBtns` | 1 | - | - | - |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchE...` | `OnBtnClick` | 2 | - | - | MarchEmojiDataManager |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchE...` | `OnSettingBtnClick` | 1 | UIEmojiSettingPanel | - | - |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchE...` | `SetEmojiSendState` | 2 | - | - | - |
| `SlgEngine.Scene.WorldMarchEmotion.WorldMarchE...` | `ShowBtns` | 1 | - | - | MarchEmojiDataManager |
| `UI.BuildBubbleTip.View.BuildBubbleTip` | `CreateClickEffect` | 1 | - | - | - |
| `UI.BuildBubbleTip.View.BuildBubbleTip` | `DoCloseBuildBtnView` | 1 | - | - | BattleLevel |
| `UI.BuildBubbleTip.View.BuildBubbleTip` | `DoOpenBuildBtnView` | 1 | - | - | BattleLevel |
| `UI.BuildBubbleTip.View.BuildBubbleTip` | `OnClick` | 1 | - | - | BattleLevel |
| `UI.BuildBubbleTip.View.BuildBubbleTip` | `OnCreate` | 2 | - | - | - |
| `UI.BuildBubbleTip.View.BuildBubbleTip` | `OnDoubleClick` | 1 | - | - | - |
| `UI.BuildBubbleTip.View.BuildBubbleTipBase` | `DoCloseBuildBtnView` | 1 | - | - | - |
| `UI.BuildBubbleTip.View.BuildBubbleTipBase` | `DoOpenBuildBtnView` | 1 | - | - | - |
| `UI.BuildBubbleTip.View.BuildBubbleTipBase` | `OnCreate` | 2 | - | - | BattleLevel |
| `UI.BuildBubbleTip.View.BuildBubbleTipBase` | `OnMainUIBubbleBtnCallback` | 1 | - | - | BattleLevel |
| `UI.BuildBubbleTip.View.BuildBubbleTipBase` | `SetClickPriority` | 1 | - | - | - |
| `UI.BuildBubbleTip.View.GarageBuildBubble` | `OnCreate` | 2 | - | - | - |
| `UI.BuildBubbleTip.View.GuideBoxBubble` | `InvalidateClick` | 1 | - | - | - |
| `UI.BuildBubbleTip.View.GuideBoxBubble` | `OnCreate` | 2 | - | - | - |
| `UI.BuildBubbleTip.View.GuideBoxBubble` | `OnPointerClick` | 1 | UIGuideArrow | - | GuideManager |
| `UI.BuildBubbleTip.View.GuideTalkBubble` | `OnCreate` | 2 | - | - | - |
| `UI.BuildBubbleTip.View.ResidentCheerBubble` | `OnCreate` | 2 | - | - | - |
| `UI.BuildCanUpgradeEffect.BuildCanUpgradeEffect` | `OnCreate` | 2 | - | - | - |
| `UI.BuildConfirmFinishEffect.BuildConfirmFinis...` | `OnCreate` | 2 | - | - | - |
| `UI.BuildConfirmFinishEffect.BuildConfirmFinis...` | `OnPointerClick` | 1 | - | - | BuildManager |
| `UI.BuildConfirmFinishEffect.BuildConfirmFinis...` | `RegisterPointerClick` | 1 | - | - | - |
| `UI.BuildIdleEffect.View.BuildIdleEffect` | `OnCreate` | 2 | - | - | - |
| `UI.BuildInUpgradingEffect.BuildInUpgradingEffect` | `OnCreate` | 2 | - | - | - |
| `UI.BuildUpgradeCompleteEffect.View.BuildUpgra...` | `OnCreate` | 2 | - | - | - |
| `UI.DecResourceEffect.View.DecResourceEffect` | `OnCreate` | 2 | - | - | - |
| `UI.DetectEventBubble.DetectEventBubble` | `OnClick` | 1 | - | - | - |
| `UI.DetectEventBubble.DetectEventBubble` | `OnCreate` | 2 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattleBu...` | `BtnClick_Buff` | 1 | - | - | DragonBuildTemplateManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattleBu...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_Change` | 1 | UIDragonMemberSwap | AlRank | ActDragonManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_CountDown` | 1 | UIDragoMemberSwapConfig | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_Enter` | 1 | - | - | ActDragonManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_Hospital` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_MoveCity` | 1 | UIDragonMoveCityConform | - | ActDragonManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_ReturnServer` | 1 | - | - | ActDragonManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `BtnClick_Score` | 1 | UIDragonBattleScore | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `CheckBtnEnter` | 1 | - | - | ActDragonManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `CheckShowHospitalBtn` | 1 | - | - | HospitalManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `OnDragonSwapConfirmShow` | 1 | UIDragoMemberSwapConfig | - | LWBattleManager |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `OnOpenUI` | 2 | UIMoveCity | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBattling...` | `ShowSwapConfirmPanel` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonBossDamage` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandP...` | `BtnClick_Command` | 1 | UICommandPanel | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandP...` | `CheckWorldSignBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandP...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandP...` | `OnOpenUI` | 2 | UISignOfCommand | - | MailShim |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandTip` | `BtnClick_Auto` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandTip` | `BtnClick_Close` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandTip` | `BtnClick_Goto` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandTip` | `BtnClick_Translate` | 1 | - | - | WorldNoticeManager |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandTip` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonCommandTip` | `UpdateAutoSelectObj` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonSpicalSh...` | `BtnCLick_WarBuild` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonSpicalSh...` | `BtnClick_BossBorn` | 1 | UIWorldSiegePoint | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonSpicalSh...` | `BtnClick_SecretBorn` | 1 | - | - | BuildManager |
| `UI.MainUI_SU.Component.Dynamic.DragonSpicalSh...` | `GetAbbrStr` | 2 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.DragonSpicalSh...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIDragonGoHomeBtn` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIDragonGoHomeBtn` | `SetWorldGoHomeBtnVisible` | 2 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIDragonGoHomeBtn` | `SetWorldWorldCenterBackBtnPosition` | 3 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIDragonGoHomeBtn` | `SetWorldWorldCenterBackBtnRotation` | 2 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIWorldDagonCo...` | `BtnClick_Command` | 1 | - | - | BattleCommandManager |
| `UI.MainUI_SU.Component.Dynamic.UIWorldDagonCo...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIWorldDagonCo...` | `SetWorldWorldCenterBackBtnPosition` | 3 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIWorldDagonCo...` | `SetWorldWorldCenterBackBtnRotation` | 2 | - | - | - |
| `UI.MainUI_SU.Component.Dynamic.UIWorldDagonCo...` | `SignBtnShow` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UINetworkState` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBattleFocus` | `OnClickSoldierCell` | 1 | UIArmyInfo | - | GuideManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.AlDigT...` | `OnClickBtn` | 1 | UIChatNew | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.AlDigT...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.AlHitT...` | `OnClickBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.AlHitT...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.AlMove...` | `OnClickBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.AlMove...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.BtnSco...` | `OnBtnScoutClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.BtnSco...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.BtnSco...` | `OnPanelClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.BtnSco...` | `OnSelectTroopBtnClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.BtnSco...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.BtnSco...` | `OnSelectBtnClick` | 1 | - | - | WorldMarchDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.DemonH...` | `OnClickBtn` | 1 | UIDemonHunterEntrust | - | DemonHunterDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.DemonH...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Dinosa...` | `OnClickBtn` | 1 | - | - | ActDinosaurBossDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Dinosa...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.FoodFe...` | `OnClickBtn` | 1 | - | - | AllianceMineManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.FoodFe...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.GhostG...` | `OnClickBtn` | 1 | - | - | NightBaronessManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.GhostG...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.GhostK...` | `OnClickBtn` | 1 | UIActivityCenterTable | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.GhostK...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Golloe...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Golloe...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.HotNew...` | `OnClickBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.HotNew...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.IceCav...` | `OnClickBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.IceCav...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Migrat...` | `OnClickBtn` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Migrat...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Phonog...` | `OnClickBtnClick` | 1 | UIPhonographBuffDetail | - | PhonographManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Phonog...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Privat...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Privat...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.RadioS...` | `OnClickBtn` | 1 | - | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.RadioS...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.ShowRa...` | `OnBtnClick` | 1 | - | - | AllianceWarDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.ShowRa...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Simple...` | `OnClickBtn` | 1 | UIBattleground | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Simple...` | `OnClickChangeQuality` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Simple...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.TradeP...` | `OnClickBtn` | 1 | UIActivityCenterTable | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.TradeP...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Treasu...` | `OnClickBtn` | 1 | UIChatNew | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Treasu...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `OnClick` | 1 | - | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `OnLeftClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `OnRightClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `UpdateTogSelect` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `OnClick` | 1 | UIDetectEvent | - | ArrowManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `AddDragonBtnTimer` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckArenaBtnShow` | 1 | - | - | BuildManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckBtnScout` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckBtnShow` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckCrossWonderBtn` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckDinosaurBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckDispatchBtnShow` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckDragonBtnShow` | 1 | - | - | ActDragonManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckGloryDeclareBtnShow` | 1 | - | - | GloryManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckGovernmentBtn` | 1 | - | - | GovernmentManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckGovernmentPrepareBtn` | 1 | - | - | GovernmentManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckKillMonsterAlBtnShow` | 1 | - | - | ActMonsterTowerData |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckKillMonsterBtnShow` | 1 | - | - | ActMonsterTowerData |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckPhonograpBtnsShow` | 1 | - | - | PhonographManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckShowHeroBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckShowHospitalBtn` | 1 | - | - | HospitalManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckTerritoryCapturerBtn` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckThroneBtn` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckTruckBtnShow` | 1 | - | - | LWMyStationDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckUIRotationBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `CheckValentineRewardShow` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ClickExpandBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `GetRadarBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `GetSearchBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnActBossClick` | 1 | UIActivityCenterTable | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnAllianceHaggleBtnClick` | 1 | UICommonShop | - | AllianceShopPlusDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnAlliance` | 1 | UIAllianceMainTable | AlBeLeaderCheck | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnAllianceHelp` | 1 | - | AlHelpAll | AllianceHelpDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnBluePrintClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnBuild` | 1 | UIBuildList | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnHeroClick` | 1 | UIHeroList | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnHeroSPEquipClick` | 1 | UIHeroInfo | - | HeroSPEquipManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnBtnHomeClick` | 1 | - | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickBtnGoodsSLG` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickBtnLevel` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickBtnStory` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickChatLove` | 1 | UILoveNewsletter | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickDispatch` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickDog` | 1 | UIRescueDog | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickDragonBtn` | 1 | UIActivityCenterTable | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickDragonSwapBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickGloryDeclareBtn` | 1 | UIActivityCenterTable | - | GloryManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickGloryExchangeBtn` | 1 | UIDemolishChangeConfirm | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickGloryExchangeReceiveBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickGloryWarSwapBtn` | 1 | UIGloryWarSwapTip | - | GloryWarSwapManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickGovernmentPrepareBtn` | 1 | UIPresidentTakesTips | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickHospitalBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickKillMonster` | 1 | - | - | ActMonsterTowerData |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickKillMonsterAl` | 1 | - | - | ActMonsterTowerData |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickRotationBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickSearch` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickTruckBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClickValentineBtn` | 1 | - | - | ValentineDecorationManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnDragonSwapConfirmShow` | 1 | UIDragoMemberSwapConfig | - | LWBattleManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnFightRewardClick` | 1 | UICollectReward | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnGloryExchangeConfirmShow` | 1 | UIDemolishChangeConfirm | - | LWBattleManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshAllianceAutoJoinReward` | 1 | - | - | AllianceBaseDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshBuildUpBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshDragonSwapBtn` | 1 | - | - | DragonSwapManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshFightReward` | 1 | - | - | CollectRewardDataManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshGloryExchangeBtn` | 1 | - | - | GloryWarSwapManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshGloryWarSwapBtn` | 1 | - | - | GloryWarSwapManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RefreshKingdomSwapBtn` | 1 | - | - | KingdomSwapManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `RemoveDragonBtnTimer` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowAllianceBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowChatBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowChatLoveBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowFunctionBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowGoodsBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowHeroBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowLevelBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowMailBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowRadarBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowStoryBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `ShowWorldBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `UpdateDragonBtnTimer` | 1 | - | - | ActDragonManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnCreate` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnPresidentBtnClick` | 1 | - | - | MailShim |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIPVEM...` | `OnReportBtnClick` | 1 | - | - | MailShim |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnClickBtn` | 1 | UIChatNew | - | CreditManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIRede...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UITrad...` | `OnClickBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UITrad...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.UIVolc...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Volcan...` | `OnClickBtn` | 1 | UIVolcanoMoveRule | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Volcan...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Volcan...` | `OnClickBtn` | 1 | UIVolcanoSetAttack | - | VolcanoWarManager |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Volcan...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Zendes...` | `OnClickBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainBottom.Zendes...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainCenter.UIPVEM...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainCenter.UIPVEM...` | `SetWorldGoHomeBtnActiveWithMainUI` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainCenter.UIWorl...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainCenter.UIWorl...` | `SetWorldGoHomeBtnVisible` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainCenter.UIWorl...` | `SetWorldWorldCenterBackBtnPosition` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainCenter.UIWorl...` | `SetWorldWorldCenterBackBtnRotation` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnSelectClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnAtkClick` | 1 | - | QueueFinish | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnCheckClick` | 1 | - | QueueFinish | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnClickView` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.FishingT...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.GloryAll...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.GloryAll...` | `OnImageBtnClick` | 1 | - | - | GloryManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.GloryMis...` | `OnBtnClick` | 1 | - | - | AllianceSkillManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.GloryMis...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.SvsMissi...` | `OnArrowClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.SvsMissi...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.SvsMissi...` | `OnJumpClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.SweepBubble` | `OnClickBtn` | 1 | UIOneClickSweepReport | - | SweepManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.SweepBubble` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIBlackK...` | `OnButtonSelfClicked` | 1 | UIActivityCenterTable | - | ActBlackKnightManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIBlackK...` | `OnCreate` | 1 | - | - | SeasonConfigManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainDr...` | `BtnClick_Boss` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainDr...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainDr...` | `SetBtnActive` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `AddNormalCompleteClickEffect` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `DoClickAnim` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `OnBgBtnClick` | 1 | - | - | QuestArrowManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `OnLeftBtnClick` | 1 | UIMainChapterTask | - | QuestArrowManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `OnOpenUISignal` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainQuest` | `RemoveNormalCompleteClickEffect` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSe...` | `OnClick` | 1 | - | - | WorldMarchDataManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSe...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSn...` | `AddSnowBtnTimer` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSn...` | `DelSnowBtnTimer` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSn...` | `OnClickSnowBtn` | 1 | UISnowCountDown | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSn...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSn...` | `RefreshSnowBtn` | 1 | - | - | SnowManManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIMainSn...` | `RefreshSnowBtnTime` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `CanShowZombieWaveBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `CheckBtnShow` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `CheckShowSnowBtn` | 1 | - | - | SnowManManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `OnBtnBuild` | 1 | UIBuildList | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `OnBtnBuildQueueClick` | 1 | UIBuildQueueList | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `OnBtnScienceClick` | 1 | UIScienceTab | - | BuildManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `OnReturnServerClick` | 1 | - | - | WorldFavoDataManager |
| `UI.MainUI_SU.Component.UIPVEMainLeft.UIPVEMai...` | `ShowFunctionBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Allianc...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Allianc...` | `OnGoBtnClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Allianc...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Allianc...` | `OnDetailBtnClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Allianc...` | `OnGoBtnClick` | 1 | - | - | AllianceWarDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.Allianc...` | `OnQuitBtnClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.BottomA...` | `OnClick` | 1 | UIWorldSiegePoint | - | AllianceBossManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.BottomA...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Compone...` | `OnClickLoot` | 1 | UIVolcanoMain | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.Compone...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UICarCh...` | `OnButtonClicked` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UICarCh...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UICarCo...` | `OnButtonClicked` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UICarCo...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIChain...` | `OnClick` | 1 | UIChainPay | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIChain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainA...` | `OnClick` | 1 | UIAllianceWarMainTable | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainA...` | `OnCreate` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainP...` | `OnClick` | 1 | UIPopupPackage | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainP...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainP...` | `OnClick` | 1 | UIPopupPackage | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainP...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainR...` | `OnCreate` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainR...` | `OnDynamicBtnEntranceStateChanged` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainR...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainW...` | `OnClick` | 1 | UIAllianceWarMainTable | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIMainW...` | `OnCreate` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CheckAllPopupPackBtnShow` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CheckBtnShow` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CheckKillMonsterBtnShow` | 1 | - | - | ActMonsterTowerData |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CheckSevenDayBtn` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CheckShowRankBtn` | 1 | - | - | ActTimeCompeDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CheckStrongCommanderBtn` | 1 | - | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CreateChainPayPackageBtn` | 1 | - | - | ChainPayManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `CreatePopupPackageBtn` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `DestroyAllPopupPackageBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `DestroyChainPayPopupPackageBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `DestroyPopupPackageBtn` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `DrakeBoss2BtnTimerAction` | 1 | - | - | DrakeBoss2Manager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `GetActivityBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `GetAlCompeteBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `HideSevenDayBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `InitEnterBtnState` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnAccountBindClick` | 1 | UIMainAccountBind | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnAtkClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnBtnDragonClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickAllianceCompeteBtn` | 1 | UIAllianceCompeteNew | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickBtnActivity` | 1 | UIActivityCenterTable | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickBtnFirstPay` | 1 | UIFirstPay | - | PayManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickChampionBtn` | 1 | UIChampionBattleMain | - | ActChampionBattleManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickCrossThroneBtn` | 1 | UICrossWonderAct | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickFirstChargeBtn` | 1 | - | - | ActFirstChargeData |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickGift` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickKillMonster` | 1 | - | - | ActMonsterTowerData |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickPopupPackage` | 1 | UIPopupPackage | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickScoutTroopItem` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickStartInvestigate` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickStrongCommanderBtn` | 1 | UIStrongCommanderPre | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnClickThroneBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnCreateClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnDrakeBoss2Click` | 1 | UIDrakaBoss2Pre | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnEditClick` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnFiveStarClick` | 1 | - | - | FiveStarManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnHolidayActivityBtnClick` | 1 | UIActivityCenterTable | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnIronAgeActivityBtnClick` | 1 | UIActivityCenterTable | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnLimitClick` | 1 | UIActivityCenterTable | - | ActivityListDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnQuestionnaireClick` | 1 | UIMainAccountBind | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnRefreshCellBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnSeasonBtnClick` | 1 | UISeasonEntrance | - | SeasonDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnSelectClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnSevenDayBtnClick` | 1 | UISevenDayNew | - | RadarCenterDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnShowActivityBtn1Click` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `OnShowActivityBtn2Click` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `PopupPackageBtnTimerAction` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `RankBtnPlayAni` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `RefreshAllianceCompeteBtn` | 1 | - | - | AllianceCompeteDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `RefreshChainPayPopupPackageBtn` | 2 | - | - | ChainPayManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `RefreshPopupPackageBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `ResetScoutSelectTipPosition` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `ShowFormationCreateTip` | 4 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `ShowFunctionBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `ShowSevenDayBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIPVEMa...` | `isShowBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIRedEq...` | `OnButtonClicked` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIRedEq...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UISteel...` | `OnButtonClicked` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UISteel...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `HideFormationSelect` | 2 | - | - | WorldMarchDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnAtkClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnClickDetailBtn` | 1 | UIWorldMarchDetail | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnClickScoutTroopItem` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnClickStartInvestigate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnCreateClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnEditClick` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnHideClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnHideClick2` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnSelectClick` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `OnShowClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `ResetScoutSelectTipPosition` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `SelectFormationForRallyTips` | 2 | - | - | WorldMarchDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `ShowFormationCreateTip` | 4 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UITroop...` | `ShowFormationSelect` | 2 | - | - | WorldMarchDataManager |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIWebPu...` | `OnButtonClicked` | 1 | - | LoginThirdPartWeb | - |
| `UI.MainUI_SU.Component.UIPVEMainRight.UIWebPu...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.MainViewD...` | `OnClick` | 1 | UISeasonNightFallsClockS5 | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.MainViewD...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.PVELevelBar` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIDesertB...` | `OnClick` | 1 | UIDesertOperateBuffList | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIDesertB...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIDesertB...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnClickInfoBtn` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnClickLoot` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnOpenTipsView` | 1 | UIWorldReminderTips | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnBtnClick` | 1 | UIItemTips | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `CanControlVisibleByBtnType` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `CheckBtnShow` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `CheckClickedByDay` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `GetBtnByBtnType` | 2 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `GetGoldBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `GetGoldStoreBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `GetGoldStoreBtnRectTrans` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `GetPeopleBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `GetStaminaBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnClickEnergy` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnClickGoldBtn` | 1 | UIGiftPackage | - | GuideManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnClickGoldStoreBtn` | 2 | UIGiftPackage | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `SetBtnVisible` | 3 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `SetGoldStoreBtnVisibleSignal` | 2 | CheckIfHasPack | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnClickResourceBtn` | 2 | UIResourceBag | - | GuideManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMain...` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `BtnClick_PtInfo` | 1 | UICreditMainPanel2 | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `CheckBtnShow` | 2 | - | - | SimpleModeManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `CheckShowSeasonBtn` | 1 | - | - | SimpleModeManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `GetGoldStoreBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `GetGoldStoreBtnRectTrans` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickAlCompeteScoreAddBtn` | 1 | - | - | StatusManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickAllianceRejoinPunishBuff` | 1 | - | - | AllianceBaseDataManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickBuff` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickDeclare` | 1 | UIWorldDeclareWarInfo | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickDragonBoss` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickOfficialBuff` | 1 | - | - | GovernmentManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickPhonographBuff` | 2 | - | - | PhonographManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickPresentBuff` | 1 | - | - | StatusManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickThanksgivingStar` | 1 | - | - | ThanksgivingStarInfo |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickVip` | 1 | UIVip | - | BuildManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickWarDefence` | 1 | - | - | StatusManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickWarFever` | 1 | - | - | StatusManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnClickWarFlagBuff` | 2 | - | - | CrossWonderManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnPt1Click` | 1 | UIHeroTip | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnPtClick` | 1 | - | - | - |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnVolcanoBuffClick` | 1 | - | - | VolcanoWarManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `OnVolcanoBuildBuffClick` | 1 | UIWorldBuff | - | VolcanoWarManager |
| `UI.MainUI_SU.Component.UIPVEMainTop.UIPVEMainTop` | `ShowFunctionBtn` | 3 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnAtkClick` | 1 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickBackHomeBtn` | 2 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickExitBtn` | 1 | - | - | BattleLevel |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickGoldBtn` | 1 | UIGiftPackage | - | GuideManager |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickGoldStoreBtn` | 2 | UIGiftPackage | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickGotoBtn` | 1 | UISearch | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickItemBtn` | 2 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickResourceBtn` | 2 | UIResourceBag | - | GuideManager |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnClickResourceItemBtn` | 2 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnCreateClick` | 1 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnCreateMarchInGuide` | 3 | UIFormationTableNew | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnEditClick` | 3 | UIFormationTableNew | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnFunctionClick` | 2 | UIHeroList | - | HeroDataManager |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `OnWarningBallClick` | 2 | - | - | - |
| `UI.MainUI_SU.Controller.UIPVEMainCtrl` | `SetSelectFormationUuid` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `DoRefreshBuildUpBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `GetClickFastObject` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `GetKillMonsterBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `GetLimitBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `GetRadarBtnPos` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnAtkClick` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnCheckKillMonsterBtnShow` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnClickScoutTroopItem` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnClickStartInvestigate` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnCreate` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnCreateClick` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnEditClick` | 3 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `OnSelectClick` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `PlayFirstChargeBtnFlyEffect` | 2 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `RefreshAllianceCompeteBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `RefreshBuildUpBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `RefreshCompeRankBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `RefreshFightReward` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `RefreshTroopBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `ResetScoutSelectTipPosition` | 3 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `SetGoldStoreBtnVisibleSignal` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `ShowAllFunctionBtn` | 1 | - | - | - |
| `UI.MainUI_SU.View.UIPVEMainView` | `ShowFormationCreateTip` | 4 | - | - | - |
| `UI.RedPoint.RedPoint` | `OnCreate` | 1 | - | - | - |
| `UI.TouchScreenEffect.View.TouchScreenEffectView` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.ActivityRe...` | `OnBtnClick` | 1 | UIItemTips | - | - |
| `UI.UIActivityCenterTable.Component.ActivityRe...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnClickBarterBtn` | 1 | - | - | DecorationDataManager |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnClickExchangeSome` | 3 | - | - | ItemTemplateManager |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `RefreshExchangeBtnShow` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnClickInfoBtn` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnDecorationClick` | 1 | - | - | DecorationTemplateManager |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnBtnClick` | 1 | UIItemTips | - | RewardManager |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnBtnClick` | 1 | - | - | ItemTemplateManager |
| `UI.UIActivityCenterTable.Component.BarterShop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnGoToClick` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnStoryClick` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnBoxClick` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OpenRewardTip` | 1 | UIActivityRewardTip | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnClickBuyBtn` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnClickBuyBtn` | 1 | - | - | ItemTemplateManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `TryToBuy` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnActInfoClick` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnClickGiftBtn` | 1 | UIGiftBoxPackageList | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnClickSkinBtn` | 1 | UIItemBaubleTip | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnExchangeTipClick` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCastleAdventureLevelRewardGet` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnInfoClick` | 1 | - | - | ActivityListDataManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnOpenGift` | 1 | UIGiftBoxPackageList | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnOpenHelp` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnOpenRank` | 1 | CastleAdventureMapRank | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnOpenReward` | 1 | CastleAdventureMapReward | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnActInfoClick` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnOpenMap` | 2 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnSkipAnimToggle` | 2 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnUpdateCastleAdventureExchangeMa...` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `RefreshBottomBtn` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `ShowOpenMapReward` | 1 | - | - | RewardManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 2 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnUpdateCastleAdventureExchangeMa...` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `ShowProgressStageRewards` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnClickBtn` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnSendGetReward` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OpenRewardTip` | 1 | UIActivityRewardTip | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `GetIsCanClickGrid` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `GetIsCanClickGrid` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `DoShowLevelReward` | 2 | CastleAdventureRewardGet | - | RewardManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `GetIsCanClickGrid` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnOpenGift` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `GetActReward` | 2 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnChallengeClick` | 1 | - | - | CastleAdventureManager |
| `UI.UIActivityCenterTable.Component.CastleAdve...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnClickBtn` | 1 | UIActivityRewardTip | - | RedPacketManager |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnClickBuy` | 1 | - | - | RedPacketManager |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnClickChange` | 1 | UIRedenvelopeSelectView | - | - |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnClickRank` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnRewardClick` | 1 | - | - | RedPacketManager |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `RefreshReward` | 1 | - | - | RedPacketManager |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.RedEnvelop...` | `ShowProgressStageRewards` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.ThanksGivi...` | `BtnClick_Gift` | 1 | UIPopupPackage | - | ThanksGivingCatchHitManager |
| `UI.UIActivityCenterTable.Component.ThanksGivi...` | `BtnClick_Info` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.ThanksGivi...` | `BtnClick_JoinAl` | 1 | UIAllianceIntro | - | - |
| `UI.UIActivityCenterTable.Component.ThanksGivi...` | `BtnClick_Rank` | 1 | UIHitTurkeyRank | - | - |
| `UI.UIActivityCenterTable.Component.ThanksGivi...` | `BtnClick_Summon` | 1 | - | - | WorldFavoDataManager |
| `UI.UIActivityCenterTable.Component.ThanksGivi...` | `OnCreate` | 1 | - | - | ThanksGivingCatchHitManager |
| `UI.UIActivityCenterTable.Component.UIPurplePa...` | `OnCreate` | 1 | - | - | - |
| `UI.UIActivityCenterTable.Component.UIPurplePa...` | `OnRewardClick` | 1 | - | ReceiveBattlePassStageReward | ActBattlePassData |
| `UI.UIActivityCenterTable.Component.UIPurplePa...` | `SetBuyData` | 2 | - | - | RewardManager |
| `UI.UIActivityCenterTable.Component.UIPurplePa...` | `OnCreate` | 1 | - | - | - |
| `UI.UIAlliance.UIAllianceFlag.Component.Allian...` | `BtnClick` | 1 | - | - | - |
| `UI.UIAlliance.UIAllianceFlag.Component.Allian...` | `OnCreate` | 1 | - | - | - |
| `UI.UIBuildNameTip.BuildNameTip` | `OnCreate` | 2 | - | - | - |
| `UI.UICapacityBoxSelect.Component.UICapacityBo...` | `OnBtnClick` | 1 | - | - | - |
| `UI.UICapacityBoxSelect.Component.UICapacityBo...` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonIcon.UICommonPlayerHead` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonItem.UICommonItem` | `OnBtnClick` | 2 | - | - | ItemTemplateManager |
| `UI.UICommonItem.UICommonItem` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonItem.UICommonItem` | `SetBtnEnable` | 2 | - | - | - |
| `UI.UICommonItem.UICommonItem` | `SetOnClickCallback` | 2 | - | - | - |
| `UI.UICommonMessageBar.View.CommonMessageBarItem` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonMessageBar.View.UICommonMessageBar...` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonResItem.CarChipTag` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonResItem.UICommonResItem` | `OnBtnClick` | 1 | - | - | ItemTemplateManager |
| `UI.UICommonResItem.UICommonResItem` | `OnBuffClick` | 2 | UIItemTips | - | - |
| `UI.UICommonResItem.UICommonResItem` | `OnCreate` | 1 | - | - | - |
| `UI.UICommonResItem.UICommonResItem` | `OnExchangeBtnClick` | 1 | UIGiftPackageRewardSelect | - | - |
| `UI.UICommonResItem.UICommonResItem` | `SetBtnEnable` | 2 | - | - | - |
| `UI.UICommonResItem.UICommonResItem` | `SetForbidClick` | 2 | - | - | - |
| `UI.UIDecoration.UIDecorationMain.Component.Ef...` | `OnCreate` | 1 | - | - | - |
| `UI.UIDecoration.UIDecorationMain.Component.Ef...` | `OnCreate` | 1 | - | - | - |
| `UI.UIEnergySlider.UIEnergySlider` | `OnAddClick` | 1 | UIFormationAddStamina | - | - |
| `UI.UIEnergySlider.UIEnergySlider` | `OnClick` | 1 | - | - | - |
| `UI.UIEnergySlider.UIEnergySlider` | `OnCreate` | 1 | - | - | - |
| `UI.UIEnergySlider.UIEnergySlider` | `SetOnClick` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnAtkClick` | 1 | - | - | WorldMarchDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnBattleStateClick` | 1 | - | - | WorldMarchDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnClickPrivilege` | 1 | UIGiftPackage | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCollectAddClick` | 1 | UIHeroTip | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnEditClick` | 1 | - | - | WorldMarchDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnPowerClick` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnPowerLimitSettingClick` | 1 | UIAllianceRallyInputPop | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnPowerLimitToggleChanged` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnSetClick` | 1 | - | - | WorldMarchDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnSoliderNumClick` | 1 | UIHeroTip | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `RefreshBtnActive` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `RefreshEditBtnText` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `ToggleControlBorS` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnEditClick` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `RefreshEditBtnText` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `ToggleControlBorS` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnInfoClick` | 1 | UIHeroTip | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `SetSendCount` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnSelectClick` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `SetClickCallBack` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnEditClick` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `RefreshEditBtnText` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `ToggleControlBorS` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnClickLockBtn` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnSelectBtnClick` | 1 | - | - | WorldMarchDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `SetSelected` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnClickStartInvestigate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnSelectTroopBtnClick` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `RefreshScoutSelectItems` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `RefreshTipOnSelectChange` | 1 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `TrySelectReadyFormation` | 1 | - | - | ArmyFormationDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnAtkClick` | 2 | - | - | WorldMarchDataManager |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnCreate` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `OnSelectClick` | 2 | - | - | - |
| `UI.UIFormation.UIFormationSelectListNew.Compo...` | `TryHandleRallyManualClick` | 4 | - | - | - |
| `UI.UIGiftPackage.Component.UICumulativeReward...` | `OnBtnClick` | 1 | - | - | - |
| `UI.UIGiftPackage.Component.UICumulativeReward...` | `OnCreate` | 1 | - | - | - |
| `UI.UIGiftPackage.Component.UIGiftPackagePoint` | `OnCreate` | 1 | - | - | - |
| `UI.UIGuidePickGarbageBubble.UIGuidePickGarbag...` | `OnClick` | 1 | - | - | CityPointDataManager |
| `UI.UIGuidePickGarbageBubble.UIGuidePickGarbag...` | `OnCreate` | 2 | - | - | - |
| `UI.UIGuidePickGarbageBubble.UIGuidePickGarbag...` | `OnCreate` | 2 | - | - | - |
| `UI.UIHero2.Common.UIHeroCellSmall` | `OnBtnClick` | 1 | - | - | - |
| `UI.UIHero2.Common.UIHeroCellSmall` | `OnCreate` | 2 | - | - | - |
| `UI.UIHero2.Common.UIHeroCellSmall` | `ToggleLevel` | 2 | - | - | - |
| `UI.UIHero2.Common.UIHeroCellSmall` | `ToggleRayCast` | 2 | - | - | - |
| `UI.UIHero2.Common.UIHeroStars` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.Common.UIHeroStarsOneIcon` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroAdvance.HeroAdvanceController` | `IsAlreadySelect` | 2 | - | - | - |
| `UI.UIHero2.UIHeroAdvance.HeroAdvanceController` | `OnToggleDogFood` | 2 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.HeroModelView2D` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.HeroModelView2D` | `ToggleSceneVisible` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `GetBtnUpSizeDelta` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `GetMilitaryRankNewBtn` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnBtnArmyClick` | 1 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnBtnAtkClick` | 1 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnBtnDefClick` | 1 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnBtnPowerClick` | 1 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnBtnSkillClick` | 2 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnClickBtnGoto` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnClickBtnHeroUpgrade` | 1 | - | - | CreditManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnLongPressClick` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnPieceItemGetClick` | 1 | - | HeroExchange | ItemTemplateManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnSkillUpBtnClick` | 1 | UIHeroSkillUpgrade | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnStarSkinBtnClick` | 2 | - | - | HeroSkinManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoDetail` | `OnStarUpBtnClick` | 1 | UIHeroMilitaryRank | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoLeft` | `OnBtnCampClick` | 1 | UIHeroCampRestraint | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoLeft` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroInfoLeft` | `OnTagClick` | 2 | UIHeroTip | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroSkill` | `OnClickSkillTag` | 1 | UIHeroTip | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroSkill` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroSkill` | `SetClickCallback` | 2 | - | - | - |
| `UI.UIHero2.UIHeroInfo.Component.UIHeroSkinPre...` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `CheckArrowBtns` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `GetHeroDataByHeroId` | 2 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `GetHeroDataByHeroUuid` | 2 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `OnBtnSkinClick` | 2 | - | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `OnClickTab` | 2 | UIHeroSkillUpgrade | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `OnCreate` | 1 | - | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `OnOpen` | 2 | - | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `OnOpenUI` | 2 | UIHeroSPEquip | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `OnToggleUI` | 2 | - | - | - |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `RefreshToggle` | 1 | - | - | HeroDataManager |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `ShowBtnArrow` | 1 | - | - | ArrowManager |
| `UI.UIHero2.UIHeroInfo.View.UIHeroInfoView` | `SwitchTab` | 2 | - | - | - |
| `UI.UIHero2.UIHeroTip.View.UIHeroTipView` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipCell` | `OnClick` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipCell` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipCell` | `SetSelect` | 2 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipGemNew` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipNode` | `DefineBtn` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipNode` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipNode` | `OnInstallBtnClick` | 1 | - | - | CreditManager |
| `UI.UIHeroEquip.Component.UIHeroEquipNode` | `OnUninstallBtnClick` | 1 | - | - | CreditManager |
| `UI.UIHeroEquip.Component.UIHeroEquipNode` | `RefreshSelect` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipNode` | `ResetSelect` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipSlot` | `OnClick` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroEquipSlot` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroEquip.Component.UIHeroSPEquipNode` | `OnBtnClick` | 1 | UIHeroSPEquip | - | HeroSPEquipManager |
| `UI.UIHeroEquip.Component.UIHeroSPEquipNode` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroTips.View.UIHeroTipsView` | `OnBtnSkillClick` | 2 | UIHeroSkillTip | - | - |
| `UI.UIHeroTips.View.UIHeroTipsView` | `OnClickCheckHeroBtn` | 1 | UIHeroInfo | - | - |
| `UI.UIHeroTips.View.UIHeroTipsView` | `OnCreate` | 1 | - | - | - |
| `UI.UIHeroTips.View.UIHeroTipsView` | `OnTagClick` | 2 | UIHeroTip | - | - |
| `UI.UIHospital.Component.UIHospitalMainInjured...` | `OnCreate` | 1 | - | - | - |
| `UI.UIHospital.Component.UIHospitalMainInjured...` | `OnBtnClick` | 1 | UIResourceBag | - | - |
| `UI.UIHospital.Component.UIHospitalMainInjured...` | `OnCreate` | 1 | - | - | - |
| `UI.UIHospital.Component.UIHospitalMainWorking...` | `OnCreate` | 1 | - | - | - |
| `UI.UIHospital.Component.UIHospitalMainWorking...` | `OnCreate` | 1 | - | - | - |
| `UI.UIHospital.Component.UIHospitalMainWorking...` | `OnToggleClick` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `GreenBtnClick` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `ImmediatelyBtnClick` | 1 | - | - | HospitalManager |
| `UI.UIHospital.View.UIHospitalMainView` | `ImmediatelySpeedBtnClick` | 1 | - | - | HospitalManager |
| `UI.UIHospital.View.UIHospitalMainView` | `OnCreate` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `OnDeadRecordBtnClick` | 1 | UIHospitalDeath | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `OnHelpLimitInfoBtnClick` | 1 | UIHospitalHelpTips | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `OnHelpLimitTimeEndInfoBtnClick` | 1 | UIHospitalHelpTips | - | MonthCardNewManager |
| `UI.UIHospital.View.UIHospitalMainView` | `OnHospitalCureReasonCloseClick` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `OnHospitalCureReasonInfoClick` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `OnMaxAddBtnClick` | 1 | UIHospitalLack | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `OnMaxDetailBtnClick` | 1 | UICommonIntro2 | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `QuicklyOpBtnClick` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `RefreshDataOnClickQuicklyOpBtn` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `RefreshSelectCount` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `SetImmediatelyBtnCostMode` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `SetImmediatelyBtnName` | 2 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `SetImmediatelyBtnSpendColor` | 2 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `SetImmediatelyBtnSpendText` | 2 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `SetSpeedBtnName` | 2 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `SpeedBtnClick` | 1 | UISpeed | - | BuildManager |
| `UI.UIHospital.View.UIHospitalMainView` | `TreatBtnClick` | 1 | - | - | - |
| `UI.UIHospital.View.UIHospitalMainView` | `YellowBtnClick` | 1 | - | - | - |
| `UI.UIMultiLanguageFeedback.UIMultiLanguageFlo...` | `OnClickBtnRed` | 1 | - | - | - |
| `UI.UIMultiLanguageFeedback.UIMultiLanguageFlo...` | `OnClickBtnScore` | 1 | - | - | - |
| `UI.UIMultiLanguageFeedback.UIMultiLanguageFlo...` | `OnClickPanel` | 1 | - | - | - |
| `UI.UIMultiLanguageFeedback.UIMultiLanguageFlo...` | `OnClickbtnBlue` | 1 | UIMultiLanguagePop | - | - |
| `UI.UIMultiLanguageFeedback.UIMultiLanguageFlo...` | `OnCreate` | 1 | - | - | - |
| `UI.UIMultiLanguageFeedback.UIMultiLanguageFlo...` | `OnOpenUISignal` | 2 | MainUI_SU | - | - |
| `UI.UINoticeTips.View.UINoticeTipsView` | `OnCreate` | 1 | - | - | - |
| `UI.UINpcQABubble.UINpcQABubble` | `OnClick` | 1 | UINpcQA | - | GuideManager |
| `UI.UINpcQABubble.UINpcQABubble` | `OnCreate` | 2 | - | - | - |
| `UI.UIScience.Component.UIScienceAttrTip` | `OnCreate` | 1 | - | - | - |
| `UI.UIScience.Component.UIScienceAttrTipCell` | `OnCreate` | 1 | - | - | - |
| `UI.UIScience.Component.UIScienceAttrTipItem` | `OnCreate` | 1 | - | - | - |
| `UI.UIScienceTab.Component.ScienceBottom` | `OnBtnAttributeClick` | 1 | - | - | ScienceManager |
| `UI.UIScienceTab.Component.ScienceBottom` | `OnCreate` | 1 | - | - | - |
| `UI.UIScienceTab.Component.ScienceBottom` | `OnResearchingBtnClick` | 5 | - | - | ArrowManager |
| `UI.UIScienceTab.Component.ScienceBottom` | `RefreshBtnAttribute` | 3 | - | - | ScienceManager |
| `UI.UIScienceTab.Component.ScienceTabCell` | `OnBtnClick` | 1 | UIScience | - | ScienceTemplateManager |
| `UI.UIScienceTab.Component.ScienceTabCell` | `OnCreate` | 1 | - | - | - |
| `UI.UIScienceTab.Component.ScienceTabCell` | `SetBtnImg` | 3 | - | - | - |
| `UI.UIScienceTab.Component.ScienceTabNewPanel....` | `OnCreate` | 1 | - | - | - |
| `UI.UIScienceTab.Component.ScienceTabNewPanel....` | `UpdateSteelEraScienceTabSignal` | 1 | - | - | - |
| `UI.UIScienceTab.Component.SecondScienceRecharge` | `OnBuyBtnClick` | 1 | UIBuildList | - | QueueDataManager |
| `UI.UIScienceTab.Component.SecondScienceRecharge` | `OnCreate` | 1 | - | - | - |
| `UI.UIScienceTab.View.UIScienceTabView` | `OnClickCloseBtn` | 1 | - | - | - |
| `UI.UIScienceTab.View.UIScienceTabView` | `OnCreate` | 1 | - | - | - |
| `UI.UIScreenCenterTips.View.UIScreenCenterTips...` | `OnClickBtn` | 1 | - | - | - |
| `UI.UIScreenCenterTips.View.UIScreenCenterTips...` | `OnCreate` | 1 | - | - | - |
| `UI.UIShowReason.UIShowReasonDesCell` | `OnCreate` | 1 | - | - | - |
| `UI.WorldSiege.UIWorldSiegeEntry` | `PlayEntryClickSound` | 1 | - | - | - |

## 5. Complete `UIWindowNames` & `UIConfig` Directory (1,697 Windows)

### Alliance & Territory (173 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `CastleAdventureChatHelp` | `CastleAdventureChatHelp` | `Slg.UI.CastleAdventure.CastleAdventureChatHelp.Config` |
| `CastleAdventureTreasureShowHelp` | `CastleAdventureTreasureShowHelp` | `Slg.UI.CastleAdventure.CastleAdventureTreasureShowHelp.Config` |
| `ChristmasParkourAnimal` | `ChristmasParkourAnimal` | `Slg.UI.ChristmasAct.ChristmasParkour.Animal.Config` |
| `FoodFestivalCookResultPanel` | `FoodFestivalCookResultPanel` | `Slg.UI.FoodFestival.FoodFestivalCookResultPanel.Config` |
| `FoodFestivalRedEnvelopeSuccess` | `FoodFestivalRedEnvelopeSuccess` | `Slg.UI.FoodFestival.FoodFestivalRedEnvelopeSuccess.Config` |
| `ThroneDefendView` | `ThroneDefendView` | `UI.ThroneDefend.Config` |
| `ThronePopupView` | `ThronePopupView` | `UI.ThronePopup.Config` |
| `ThroneRankView` | `ThroneRankView` | `UI.UIThroneRanking.Config` |
| `ThroneRecordView` | `ThroneRecordView` | `Slg.UI.UIThroneRecord.Config` |
| `ThroneRewardView` | `ThroneRewardView` | `UI.UIThroneReward.Config` |
| `UIAlLeaderCandidates` | `UIAlLeaderCandidates` | `UI.UIAlliance.UIAlLeaderCandidates.Config` |
| `UIAlLeaderCongratulate` | `UIAlLeaderCongratulate` | `UI.UIAlliance.UIAlLeaderCongratulate.Config` |
| `UIAlLeaderElectResult` | `UIAlLeaderElectResult` | `UI.UIAlliance.UIAlLeaderElectResult.Config` |
| `UIAlLeaderElectSignUp` | `UIAlLeaderElectSignUp` | `UI.UIAlliance.UIAlLeaderElectSignUp.Config` |
| `UIAlLeaderVote` | `UIAlLeaderVote` | `UI.UIAlliance.UIAlLeaderVote.Config` |
| `UIAlMemberRecommend` | `UIAlMemberRecommend` | `Slg.UI.UIAlliance.UIAlMemberRecommend.Config` |
| `UIAllianceAlertDetail` | `UIAllianceAlertDetail` | `UI.UIAlliance.UIAllianceAlertDetail.Config` |
| `UIAllianceAnnouncementEdit` | `UIAllianceAnnouncementEdit` | `Slg.UI.UIAlliance.UIAllianceAnnouncementEdit.Config` |
| `UIAllianceAnnouncementUrgentReleaseView` | `UIAllianceAnnouncementUrgentReleaseView` | `Slg.UI.UIAlliance.UIAllianceAnnouncementUrgentReleaseView.Config` |
| `UIAllianceApplyList` | `UIAllianceApplyList` | `Slg.UI.UIAlliance.UIAllianceApplyList.Config` |
| `UIAllianceAssemble` | `UIAllianceAssemble` | `UI.UIAlliance.UIAllianceAssemble.Config` |
| `UIAllianceAssembleBox` | `UIAllianceAssembleBox` | `UI.UIAlliance.UIAllianceAssembleBox.Config` |
| `UIAllianceAssembleConfirm` | `UIAllianceAssembleConfirm` | `UI.UIAlliance.UIAllianceAssembleConfirm.Config` |
| `UIAllianceAutoJoinRally` | `UIAllianceAutoJoinRally` | `UI.UIAlliance.UIAllianceAutoJoinRally.Config` |
| `UIAllianceBossAllianceRewardPanel` | `UIAllianceBossAllianceRewardPanel` | `UI.UIAllianceBoss.UIAllianceBossAllianceRewardPanel.Config` |
| `UIAllianceBossBounsTipsPanel` | `UIAllianceBossBounsTipsPanel` | `UI.UIAllianceBoss.UIAllianceBossBounsTipsPanel.Config` |
| `UIAllianceBossMain` | `UIAllianceBossMain` | `UI.UIAllianceBoss.UIAllianceBossMain.Config` |
| `UIAllianceBossRankNew` | `UIAllianceBossRankNew` | `UI.UIAllianceBoss.UIAllianceBossRankNew.Config` |
| `UIAllianceBossRewardAndRankPanel` | `UIAllianceBossRewardAndRankPanel` | `UI.UIAllianceBoss.UIAllianceBossRewardAndRankPanel.Config` |
| `UIAllianceBossViewPanel` | `UIAllianceBossViewPanel` | `UI.UIAllianceBoss.UIAllianceBossViewPanel.Config` |
| `UIAllianceBossWorldPointTipPanel` | `UIAllianceBossWorldPointTipPanel` | `UI.UIAllianceBoss.UIAllianceBossWorldPointTipPanel.Config` |
| `UIAllianceBuildingCollect` | `UIAllianceBuildingCollect` | `UI.UIAllianceBuildingCollect.Config` |
| `UIAllianceCareerEdit` | `UIAllianceCareerEdit` | `UI.UIAlliance.UIAllianceCareer.Config` |
| `UIAllianceCareerEffectTip` | `UIAllianceCareerEffectTip` | `UI.UIAlliance.UIAllianceCareerEffectTip.Config` |
| `UIAllianceChangeAbbr` | `UIAllianceChangeAbbr` | `UI.UIAlliance.UIAllianceChangeAbbr.Config` |
| `UIAllianceChangeAnnounce` | `UIAllianceChangeAnnounce` | `Slg.UI.UIAlliance.UIAllianceChangeAnnounce.Config` |
| `UIAllianceChangeLanguage` | `UIAllianceChangeLanguage` | `UI.UIAlliance.UIAllianceChangeLanguage.Config` |
| `UIAllianceChangeName` | `UIAllianceChangeName` | `UI.UIAlliance.UIAllianceChangeName.Config` |
| `UIAllianceChangeRankName` | `UIAllianceChangeRankName` | `Slg.UI.UIAlliance.UIAllianceChangeRankName.Config` |
| `UIAllianceChangeRestriction` | `UIAllianceChangeRestriction` | `UI.UIAlliance.UIAllianceChangeRestriction.Config` |
| `UIAllianceCity` | `UIAllianceCity` | `Slg.UI.UIAlliance.UIAllianceCity.Config` |
| `UIAllianceCityBar` | `UIAllianceCityBar` | `UI.UIAllianceCityBar.Config` |
| `UIAllianceCityBuffBox` | `UIAllianceCityBuffBox` | `Slg.UI.UIAlliance.UIAllianceCityBuffBox.Config` |
| `UIAllianceCitySelect` | `UIAllianceCitySelect` | `-` |
| `UIAllianceClearMember` | `UIAllianceClearMember` | `Slg.UI.UIAlliance.UIAllianceClearMember.Config` |
| `UIAllianceCompeteDayTaskPop` | `UIAllianceCompeteDayTaskPop` | `UI.UIAllianceCompeteDayTaskPop.Config` |
| `UIAllianceCompeteDayTaskPopNew` | `UIAllianceCompeteDayTaskPopNew` | `UI.UIAllianceCompeteDayTaskPopNew.Config` |
| `UIAllianceCompeteDayTaskTip` | `UIAllianceCompeteDayTaskTip` | `UI.UIAllianceCompeteDayTaskTip.Config` |
| `UIAllianceCompeteFightNotice` | `UIAllianceCompeteFightNotice` | `UI.UIAllianceCompeteFightNotice.Config` |
| `UIAllianceCompeteMemberScore` | `UIAllianceCompeteMemberScore` | `UI.UIAllianceCompeteMemberScore.Config` |
| `UIAllianceCompeteNew` | `UIAllianceCompeteNew` | `UI.UIAllianceCompeteNew.Config` |
| `UIAllianceCompetePopInfo` | `UIAllianceCompetePopInfo` | `UI.UIAllianceCompetePopInfo.Config` |
| `UIAllianceCompeteRank` | `UIAllianceCompeteRank` | `UI.UIAllianceCompete.UIAllianceCompeteRank.Config` |
| `UIAllianceCompeteReward` | `UIAllianceCompeteReward` | `UI.UIAllianceCompete.UIAllianceCompeteReward.Config` |
| `UIAllianceCompeteTaskTip` | `UIAllianceCompeteTaskTip` | `UI.UIAllianceCompeteTaskTip.Config` |
| `UIAllianceCompeteTaskTip2` | `UIAllianceCompeteTaskTip2` | `UI.UIAllianceCompeteTaskTip2.Config` |
| `UIAllianceCompeteWinOrLoss` | `UIAllianceCompeteWinOrLoss` | `UI.UIAllianceCompeteWinOrLoss.Config` |
| `UIAllianceCreatePopUp` | `UIAllianceCreatePopUp` | `UI.UIAlliance.UIAllianceCreatePopUp.Config` |
| `UIAllianceDetail` | `UIAllianceDetail` | `Slg.UI.UIAlliance.UIAllianceDetail.Config` |
| `UIAllianceDismiss` | `UIAllianceDismiss` | `Slg.UI.UIAlliance.UIAllianceDismiss.Config` |
| `UIAllianceDissolving` | `UIAllianceDissolving` | `Slg.UI.UIAlliance.UIAllianceDissolving.Config` |
| `UIAllianceEveryDayTask` | `UIAllianceEveryDayTask` | `UI.UIAlliance.UIAllianceEveryDayTask.Config` |
| `UIAllianceExitTip` | `UIAllianceExitTip` | `UI.UIAlliance.UIAllianceExitTip.Config` |
| `UIAllianceFlag` | `UIAllianceFlag` | `Slg.UI.UIAlliance.UIAllianceFlag.Config` |
| `UIAllianceGift` | `UIAllianceGift` | `Slg.UI.UIAlliance.UIAllianceGift.Config` |
| `UIAllianceGiftInfo` | `UIAllianceGiftInfo` | `UI.UIAlliance.UIAllianceGiftInfo.Config` |
| `UIAllianceGiftReward` | `UIAllianceGiftReward` | `Slg.UI.UIAlliance.UIAllianceGiftReward.Config` |
| `UIAllianceGiftRule` | `UIAllianceGiftRule` | `Slg.UI.UIAlliance.UIAllianceGiftRule.Config` |
| `UIAllianceHaggleMain` | `UIAllianceHaggleMain` | `UI.AllianceHaggle.Config` |
| `UIAllianceHaggleMember` | `UIAllianceHaggleMember` | `UI.AllianceHaggle.AllianceHaggleMember.Config` |
| `UIAllianceHaggleSlot` | `UIAllianceHaggleSlot` | `UI.AllianceHaggle.AllianceHaggleSlot.Config` |
| `UIAllianceHelp` | `UIAllianceHelp` | `Slg.UI.UIAlliance.UIAllianceHelp.Config` |
| `UIAllianceIntro` | `UIAllianceIntro` | `Slg.UI.UIAllianceIntro.Config` |
| `UIAllianceIntroFirstTime` | `UIAllianceIntroFirstTime` | `-` |
| `UIAllianceInviteList` | `UIAllianceInviteList` | `-` |
| `UIAllianceInviteTip` | `UIAllianceInviteTip` | `Slg.UI.UIAlliance.UIAllianceInviteTip.Config` |
| `UIAllianceJoinCondition` | `UIAllianceJoinCondition` | `Slg.UI.UIAlliance.UIAllianceJoinCondition.Config` |
| `UIAllianceKickMemberView` | `UIAllianceKickMemberView` | `Slg.UI.UIAlliance.UIAllianceKickMember.Config` |
| `UIAllianceLeaderReward` | `UIAllianceLeaderReward` | `UI.UIAllianceLeaderReward.Config` |
| `UIAllianceLog` | `UIAllianceLog` | `Slg.UI.UIAlliance.UIAllianceLog.Config` |
| `UIAllianceLogEx` | `UIAllianceLogEx` | `Slg.UI.UIAlliance.UIAllianceLogEx.Config` |
| `UIAllianceMainTable` | `UIAllianceMainTable` | `Slg.UI.UIAlliance.UIAllianceMainTable.Config` |
| `UIAllianceMark` | `UIAllianceMark` | `Slg.UI.UIAllianceMark_SLG.Config` |
| `UIAllianceMarkRemindNotice` | `UIAllianceMarkRemindNotice` | `Slg.UI.UIAllianceMarkRemindNotice_SLG.Config` |
| `UIAllianceMarkTip` | `UIAllianceMarkTip` | `UI.UIAllianceMarkTip.Config` |
| `UIAllianceMemberDetail` | `UIAllianceMemberDetail` | `Slg.UI.UIAlliance.UIAllianceMemberDetail.Config` |
| `UIAllianceMemberTip` | `UIAllianceMemberTip` | `Slg.UI.UIAlliance.UIAllianceMemberTip.Config` |
| `UIAllianceMerge` | `UIAllianceMerge` | `UI.UIAllianceMerge.Config` |
| `UIAllianceOfficeSelect` | `UIAllianceOfficeSelect` | `-` |
| `UIAllianceOfficialSkill` | `UIAllianceOfficialSkill` | `Slg.UI.UIAlliance.UIAllianceOfficialSkill.Config` |
| `UIAllianceOfficialSkillPop` | `UIAllianceOfficialSkillPop` | `Slg.UI.UIAlliance.UIAllianceOfficialSkillPop.Config` |
| `UIAllianceOfficialSkillRule` | `UIAllianceOfficialSkillRule` | `Slg.UI.UIAlliance.UIAllianceOfficialSkillRule.Config` |
| `UIAlliancePVEView` | `UIAlliancePVEView` | `Slg.UI.UIAlliance.UIAlliancePVEView.Config` |
| `UIAllianceQa` | `UIAllianceQa` | `UI.UIAlliance.UIAllianceQa.Config` |
| `UIAllianceRallyInputPop` | `UIAllianceRallyInputPop` | `UI.UIAlliance.UIAllianceRallyInputPop.Config` |
| `UIAllianceRallyOperate` | `UIAllianceRallyOperate` | `UI.UIAlliance.UIAllianceRallyOperate.Config` |
| `UIAllianceRankDetailList` | `UIAllianceRankDetailList` | `-` |
| `UIAllianceRankReward` | `UIAllianceRankReward` | `Slg.UI.UIAlliance.UIAllianceRankReward.Config` |
| `UIAllianceRankSelect` | `UIAllianceRankSelect` | `Slg.UI.UIAlliance.UIAllianceRankSelect.Config` |
| `UIAllianceRankTable` | `UIAllianceRankTable` | `Slg.UI.UIAlliance.UIAllianceRankTable.Config` |
| `UIAllianceScience` | `UIAllianceScience` | `Slg.UI.UIAlliance.UIAllianceScience.Config` |
| `UIAllianceScienceDetail` | `UIAllianceScienceDetail` | `Slg.UI.UIAlliance.UIAllianceScienceDetail.Config` |
| `UIAllianceScienceInfo` | `UIAllianceScienceInfo` | `Slg.UI.UIAlliance.UIAllianceScienceInfo.Config` |
| `UIAllianceSelectRole` | `UIAllianceSelectRole` | `Slg.UI.UIAlliance.UIAllianceSelectRole.Config` |
| `UIAllianceShop` | `UIAllianceShop` | `Slg.UI.UIAlliance.UIAllianceShop.Config` |
| `UIAllianceShopAddPanel` | `UIAllianceShopAddPanel` | `UI.UIAllianceShopPlus.UIAllianceShopAddPanel.Config` |
| `UIAllianceShopBuyPanel` | `UIAllianceShopBuyPanel` | `Slg.UI.UIAlliance.UIAllianceShopBuyPanel.Config` |
| `UIAllianceShopLevelUpNotice` | `UIAllianceShopLevelUpNotice` | `UI.UIAllianceShopPlus.UIAllianceShopLevelUpNotice.Config` |
| `UIAllianceShopPlusBuy` | `UIAllianceShopPlusBuy` | `UI.UIAllianceShopPlus.UIAllianceShopPlusBuy.Config` |
| `UIAllianceShopPlusLaunch` | `UIAllianceShopPlusLaunch` | `UI.UIAllianceShopPlus.UIAllianceShopPlusLaunch.Config` |
| `UIAllianceShopPlusRecordTips` | `UIAllianceShopPlusRecordTips` | `UI.UIAllianceShopPlus.UIAllianceShopPlusRecordTips.Config` |
| `UIAllianceShopRecord` | `UIAllianceShopRecord` | `UI.UIAllianceShopPlus.UIAllianceShopRecord.Config` |
| `UIAllianceStorage` | `UIAllianceStorage` | `-` |
| `UIAllianceTask` | `UIAllianceTask` | `UI.UIAlliance.UIAllianceTask.Config` |
| `UIAllianceWarDetail` | `UIAllianceWarDetail` | `UI.UIAlliance.UIAllianceWarDetail.Config` |
| `UIAllianceWarInfoView` | `UIAllianceWarInfoView` | `Slg.UI.UIAlliance.UIAllianceWarInfo.Config` |
| `UIAllianceWarIntelligence` | `UIAllianceWarIntelligence` | `Slg.UI.UIAlliance.UIAllianceWarIntelligence.Config` |
| `UIAllianceWarMainTable` | `UIAllianceWarMainTable` | `Slg.UI.UIAlliance.UIAllianceWarMainTable.Config` |
| `UIAllianceWarPersonalList` | `UIAllianceWarPersonalList` | `Slg.UI.UIAlliance.UIAllianceWarPersonalList.Config` |
| `UIAssistanceThrone` | `UIAssistanceThrone` | `UI.UIAssistanceThrone.Config` |
| `UIChangeAllianceCityName` | `UIChangeAllianceCityName` | `UI.UIChangeAllianceCityName.Config` |
| `UIChatJoinAllianceInform` | `UIChatJoinAllianceInform` | `Slg.UI.UIChatJoinAllianceInform.Config` |
| `UICheckAlliance` | `UICheckAlliance` | `Slg.UI.UIAlliance.UICheckAlliance.Config` |
| `UICommonModal` | `UICommonModal` | `UI.UICommonModal.Config` |
| `UICreateAlliance` | `UICreateAlliance` | `UI.UIAlliance.UICreateAlliance.Config` |
| `UICreateSetAlliance` | `UICreateSetAlliance` | `UI.UIAlliance.UICreateSetAlliance.Config` |
| `UIDragonAllianceSelectMember` | `UIDragonAllianceSelectMember` | `-` |
| `UIFoodFestivalCommonIntroPanel` | `UIFoodFestivalCommonIntroPanel` | `Slg.UI.FoodFestival.UIFoodFestivalCommonIntroPanel.Config` |
| `UIFoodFestivalCookDetailsPanel` | `UIFoodFestivalCookDetailsPanel` | `Slg.UI.FoodFestival.UIFoodFestivalCookDetailsPanel.Config` |
| `UIFoodFestivalCookRule` | `UIFoodFestivalCookRule` | `Slg.UI.FoodFestival.UIFoodFestivalCookRule.Config` |
| `UIFoodFestivalDailyRewardPanel` | `UIFoodFestivalDailyRewardPanel` | `Slg.UI.FoodFestival.UIFoodFestivalDailyRewardPanel.Config` |
| `UIFoodFestivalExchangeCancelPanel` | `UIFoodFestivalExchangeCancelPanel` | `Slg.UI.FoodFestival.UIFoodFestivalExchangeCancelPanel.Config` |
| `UIFoodFestivalExchangePanel` | `UIFoodFestivalExchangePanel` | `Slg.UI.FoodFestival.UIFoodFestivalExchangePanel.Config` |
| `UIFoodFestivalExchangeSelectPanel` | `UIFoodFestivalExchangeSelectPanel` | `Slg.UI.FoodFestival.UIFoodFestivalExchangeSelectPanel.Config` |
| `UIFoodFestivalExchangeShopBuyPanel` | `UIFoodFestivalExchangeShopBuyPanelJuly` | `Slg.UI.FoodFestival.UIFoodFestivalExchangeShopBuyPanel.Config` |
| `UIFoodFestivalFoodDropTip` | `UIFoodFestivalFoodDropTip` | `Slg.UI.FoodFestival.UIFoodFestivalFoodDropTip.Config` |
| `UIFoodFestivalPuzzleTaskPanel` | `UIFoodFestivalPuzzleTaskPanel` | `Slg.UI.FoodFestival.UIFoodFestivalPuzzleTaskPanel.Config` |
| `UIFoodFestivalRankPanel` | `UIFoodFestivalRankPanel` | `Slg.UI.FoodFestival.UIFoodFestivalRankPanel.Config` |
| `UIFoodFestivalRewardPanel` | `UIFoodFestivalRewardPanel` | `Slg.UI.FoodFestival.UIFoodFestivalRewardPanel.Config` |
| `UIFoodFestivalUseFoodPanel` | `UIFoodFestivalUseFoodPanel` | `Slg.UI.FoodFestival.UIFoodFestivalUseFoodPanel.Config` |
| `UIFoodRedenvelopeSelectView` | `UIFoodRedenvelopeSelectView` | `Slg.UI.FoodFestival.FoodFestivalRedEnvelopeSelect.Config` |
| `UIGloryAllianceDeclareRecord` | `UIGloryAllianceDeclareRecord` | `UI.UIGlory.UIGloryAllianceDeclareRecord.Config` |
| `UIGloryAllianceSetTruce` | `UIGloryAllianceSetTruce` | `Slg.UI.UIGlory.UIGloryAllianceSetTruce.Config` |
| `UIHeroOfficial` | `UIHeroOfficial` | `UI.UIHeroOfficial.Config` |
| `UIHospital` | `UIHospital` | `UI.UIHospital.Config` |
| `UIHospitalDetial` | `UIHospitalDetial` | `UI.UIHospitalDetial.Config` |
| `UIJoinAlliance` | `UIJoinAlliance` | `UI.UIAlliance.UIJoinAlliance.Config` |
| `UILeagueMatchAlliances` | `UILeagueMatchAlliances` | `UI.LeagueMatch.UILeagueMatchAlliances.Config` |
| `UIMoveCityAssemble` | `UIMoveCityAssemble` | `UI.UIAlliance.UIMoveCityAssemble.Config` |
| `UIPVEDetectSpecialJumpLevel` | `UIPVEDetectSpecialJumpLevel` | `UI.UIRadarCenter.UIPVEDetectSpecial.JumpLevel.Config` |
| `UIPVEDetectSpecialJumpResult` | `UIPVEDetectSpecialJumpResult` | `UI.UIRadarCenter.UIPVEDetectSpecial.JumpResult.Config` |
| `UIPresidentTakesTips` | `UIPresidentTakesTips` | `UI.UIThrone.UIPresidentTakesTips.Config` |
| `UIRedEquipBossRallyReward` | `UIRedEquipBossRallyReward` | `UI.UIActivityCenterTable.Component.UIRedEquipBossRally.UIRedEquipBossRal...` |
| `UIRedenvelopeReceiveInfoCarAlliance` | `UIRedenvelopeReceiveInfoCarAlliance` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveInfoCarAlliance.Config` |
| `UIRefundDeductOptional` | `UIRefundDeductOptional` | `Slg.UI.UICreditMainPanel.RefundDeduct.Optional.Config` |
| `UISeasonAllianceReward` | `UISeasonAllianceReward` | `-` |
| `UISeasonAllianceSelectMember` | `UISeasonAllianceSelectMember` | `-` |
| `UISeasonIceCaveAllianceOccupyRank` | `UISeasonIceCaveAllianceOccupyRank` | `Slg.UI.UISeason.UISeasonIceCave.UISeasonIceCaveAllianceOccupyRank.Config` |
| `UISetAlOfficialPos` | `UISetAlOfficialPos` | `Slg.UI.UIAlliance.UISetAlOfficialPos.Config` |
| `UISettingAlliance` | `UISettingAlliance` | `Slg.UI.UIAlliance.UISettingAlliance.Config` |
| `UIThroneAllianceAddPopup` | `UIThroneAllianceAddPopup` | `UI.UIGovernment.UIThroneAllianceAddPopup.Config` |
| `UIThroneAllianceAppointmentPopup` | `UIThroneAllianceAppointmentPopup` | `UI.UIGovernment.UIThroneAllianceAppointmentPopup.Config` |
| `UIThroneKingdomApplyPos` | `UIThroneKingdomApplyPos` | `UI.UIGovernment.UIThroneKingdomApplyPos.Config` |
| `UIThroneKingdomApplyPosHistory` | `UIThroneKingdomApplyPosHistory` | `UI.UIGovernment.UIThroneKingdomApplyPosHistory.Config` |
| `UIThroneKingdomAssumedsuccessfull` | `UIThroneKingdomAssumedsuccessfull` | `UI.UIGovernment.UIThroneKingdomAssumedsuccessfull.Config` |
| `UIThronePosition` | `UIThronePosition` | `UI.UIGovernment.UIThronePosition.Config` |
| `UIThronePositionApplyCondition` | `UIThronePositionApplyCondition` | `UI.UIGovernment.UIThronePositionApplyCondition.Config` |
| `UIThronePresidentHonour` | `UIThronePresidentHonour` | `UI.UIGovernment.UIThronePresidentHonour.Config` |
| `UIThronePresidentReward` | `UIThronePresidentReward` | `UI.UIGovernment.UIThronePresidentReward.Config` |
| `UIThroneRewardSelectMember` | `UIThroneRewardSelectMember` | `UI.UIGovernment.UIThroneRewardSelectMember.Config` |
| `UIThroneSendList` | `UIThroneSendList` | `UI.UIGovernment.UIThroneSendList.Config` |
| `UIVolcanoAllianceMarkTip` | `UIVolcanoAllianceMarkTip` | `UI.UIVolcanoAllianceMarkTip.Config` |
| `UIWorldAllianceBossTip` | `UIWorldAllianceBossTip` | `UI.UIAllianceBoss.UIWorldAllianceBossTip.Config` |

### Arena & PVP (118 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `CastleAdventureMapRank` | `CastleAdventureMapRank` | `Slg.UI.CastleAdventure.CastleAdventureMapRank.Config` |
| `ChristmasParkourRankReward` | `ChristmasParkourRankReward` | `Slg.UI.ChristmasAct.ChristmasParkour.RankReward.Config` |
| `UIActMonsterTowerRank` | `UIActMonsterTowerRank` | `UI.UIActMonsterTowerRank.Config` |
| `UIAircraftGradingRank` | `UIAircraftGradingRank` | `-` |
| `UIAircraftRank` | `UIAircraftRank` | `UI.UIAircraftRank.Config` |
| `UIAircraftRankingMain` | `UIAircraftRankingMain` | `UI.UIAircraftRankingMain.Config` |
| `UIArena3V3Battle` | `UIArena3V3Battle` | `Slg.UI.UIArena3V3.Battle.Config` |
| `UIArena3V3BattleReport` | `UIArena3V3BattleReport` | `Slg.UI.UIArena3V3.BattleReport.Config` |
| `UIArena3V3Challenge` | `UIArena3V3Challenge` | `Slg.UI.UIArena3V3.Challenge.Config` |
| `UIArena3V3Entrance` | `UIArena3V3Entrance` | `Slg.UI.UIArena3V3.Entrance.Config` |
| `UIArena3V3History` | `UIArena3V3History` | `Slg.UI.UIArena3V3.History.Config` |
| `UIArena3V3Popup` | `UIArena3V3Popup` | `Slg.UI.UIArena3V3.Popup.Config` |
| `UIArena3V3Result` | `UIArena3V3Result` | `Slg.UI.UIArena3V3.Result.Config` |
| `UIArenaChallenge` | `UIArenaChallenge` | `UI.UIArenaChallenge.Config` |
| `UIArenaConfirm` | `UIArenaConfirm` | `UI.UIArenaConfirm.Config` |
| `UIArenaHistory` | `UIArenaHistory` | `UI.UIArenaHistory.Config` |
| `UIArenaPanel` | `UIArenaPanel` | `UI.UIArenaPanel.Config` |
| `UIArenaPlayerArmy` | `UIArenaPlayerArmy` | `Slg.UI.UIArenaPlayerArmy.Config` |
| `UIArenaPlayerEquipInfo` | `UIArenaPlayerEquipInfo` | `Slg.UI.UIArenaPlayerEquipInfo.Config` |
| `UIArenaRankPop` | `UIArenaRankPop` | `UI.UIArenaRankPop.Config` |
| `UIArenaReward` | `UIArenaReward` | `UI.UIArenaReward.Config` |
| `UIArenaSeasonResetPopup` | `UIArenaSeasonResetPopup` | `UI.UIArenaSeasonResetPopup.Config` |
| `UIBlackKnightRank` | `UIBlackKnightRank` | `UI.UIBlackKnightRank.Config` |
| `UICarChipActivityPowerRankPopup` | `UICarChipActivityPowerRankPopup` | `Slg.UI.CarChipActivity.UICarChipActivityPowerRankPopup.Config` |
| `UICarComponActivityPowerRankPopup` | `UICarComponActivityPowerRankPopup` | `Slg.UI.CarComponActivity.UICarComponActivityPowerRankPopup.Config` |
| `UIChampionBattleRankView` | `UIChampionBattleRankView` | `Slg.UI.UIChampionBattleView.UIChampionBattleRankView.Config` |
| `UIChristmasRankPanel` | `UIChristmasRankPanel` | `Slg.UI.ChristmasAct.UIChristmasRankPanel.Config` |
| `UIChristmasRankRewardPanel` | `UIChristmasRankRewardPanel` | `Slg.UI.ChristmasAct.UIChristmasRankRewardPanel.Config` |
| `UICityAttackRank` | `UICityAttackRank` | `SlgEngine.UI.WorldSiege.UICityAttackRank.Config` |
| `UICrossWonderActRankList` | `UICrossWonderActRankList` | `UI.UICrossWonder.UICrossWonderActRankList.Config` |
| `UICrossWonderContributeRank` | `UICrossWonderContributeRank` | `UI.UICrossWonder.UICrossWonderContributeRank.Config` |
| `UICrossWonderPointRank` | `UICrossWonderPointRank` | `UI.UICrossWonder.UICrossWonderPointRank.Config` |
| `UICrossWonderRank` | `UICrossWonderRank` | `UI.UICrossWonder.UICrossWonderRank.Config` |
| `UIDigActivityRank` | `UIDigActivityRank` | `UI.UIDigActivityRank.Config` |
| `UIDonateSoldierRank` | `UIDonateSoldierRank` | `UI.UIDonateSoldierRank.Config` |
| `UIFormationArena3V3New` | `UIFormationArena3V3New` | `Slg.UI.UIArena3V3.Formation.UIFormationTableNew2.Config` |
| `UIFormationOfBattlefield` | `UIFormationOfBattlefield` | `UI.BattleCommand.FormationOfBattlefield.Config` |
| `UIFormationOfBattlefieldNoTeam` | `UIFormationOfBattlefieldNoTeam` | `UI.BattleCommand.FormationOfBattlefieldNoTeam.Config` |
| `UIFormationOfBattlefieldTeam` | `UIFormationOfBattlefieldTeam` | `UI.BattleCommand.FormationOfBattlefieldTeam.Config` |
| `UIFormationofBattlefieldCommand` | `UIFormationofBattlefieldCommand` | `UI.BattleCommand.UIFormationofBattlefieldCommand.Config` |
| `UIFrozenLandSaveRank` | `UIFrozenLandSaveRank` | `UI.FrozenLandActivity.UIFrozenLandSaveRank.Config` |
| `UIGiftBoxRank` | `UIGiftBoxRank` | `UI.UIGiftBoxRank.Config` |
| `UIGivingRoses2FlowerRankView` | `UIGivingRoses2FlowerRankView` | `Slg.UI.ValentineAct.UIGivingRoses2FlowerRankView.Config` |
| `UIGivingRosesRankPanel` | `UIGivingRosesRankPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesRankPanel.Config` |
| `UIGloryPersonalRank` | `UIGloryPersonalRank` | `UI.UIGlory.UIGloryPersonalRank.Config` |
| `UIGloryRankReward` | `UIGloryRankReward` | `UI.UIGlory.UIGloryRankReward.Config` |
| `UIGolloesCardsRank` | `UIGolloesCardsRank` | `UI.UIGolloesCardsRank.Config` |
| `UIGotoAllowTracking` | `UIGotoAllowTracking` | `UI.UISetting.UIGotoAllowTracking.Config` |
| `UIHalloweenGiftRank` | `UIHalloweenGiftRank` | `Slg.UI.UIHalloweenGift.UIHalloweenGiftRank.Config` |
| `UIHeroEquipRank` | `UIHeroEquipRank` | `UI.UIHeroEquipRank.Config` |
| `UIHeroMilitaryRank` | `UIHeroMilitaryRank` | `UI.UIHero2.UIHeroMilitaryRank.Config` |
| `UIHeroMilitaryRankIntro` | `UIHeroMilitaryRankIntro` | `UI.UIHero2.UIHeroMilitaryRankIntro.Config` |
| `UIHeroMilitaryRankIntroNew` | `UIHeroMilitaryRankIntroNew` | `UI.UIHero2.UIHeroMilitaryRankIntroNew.Config` |
| `UIHeroRankList` | `UIHeroRankList` | `Slg.UI.UIRank.UIHeroRankList.Config` |
| `UIHitTurkeyRank` | `UIHitTurkeyRank` | `UI.UIActivityCenterTable.Component.ThanksGiving.HitTurkeyRank.Config` |
| `UIKingdomSwapHistoryPopup` | `UIKingdomSwapHistoryPopup` | `UI.UIKingdomSwap.UIKingdomSwapHistoryPopup.Config` |
| `UIKingdomSwapPopup` | `UIKingdomSwapPopup` | `UI.UIKingdomSwap.UIKingdomSwapPopup.Config` |
| `UIKingdomSwapSelectPopup` | `UIKingdomSwapSelectPopup` | `UI.UIKingdomSwap.UIKingdomSwapSelectPopup.Config` |
| `UIKingdomSwapTip` | `UIKingdomSwapTip` | `UI.UIKingdomSwap.UIKingdomSwapTip.Config` |
| `UIKingdomSwapUsePopup` | `UIKingdomSwapUsePopup` | `UI.UIKingdomSwap.UIKingdomSwapUsePopup.Config` |
| `UILikeActRank` | `UILikeActRank` | `UI.UIActivityCenterTable.Component.LikeRankAct.UILikeActRank.Config` |
| `UILikeActRule` | `UILikeActRule` | `UI.UIActivityCenterTable.Component.LikeRankAct.UILikeActRule.Config` |
| `UILikeRank` | `UILikeRank` | `UI.UILike.UILikeRank.Config` |
| `UILuckyRollHeroBigRewardRank` | `UILuckyRollHeroBigRewardRank` | `UI.UILuckyRollHeroBigRewardRank.Config` |
| `UILuckyRollHeroRank` | `UILuckyRollHeroRank` | `-` |
| `UILuckyRollRank` | `UILuckyRollRank` | `UI.UILuckyRollRank.Config` |
| `UILuckyShopRank` | `UILuckyShopRank` | `UI.UILuckyShopRank.Config` |
| `UIMonsterSuperChallengeRank` | `UIMonsterSuperChallengeRank` | `UI.UIMonsterSuperChallengeRank.Config` |
| `UIMonsterSuperChallengeRank02` | `UIMonsterSuperChallengeRank02` | `UI.UIMonsterSuperChallengeRank02.Config` |
| `UIMusicFestivalRankPanel` | `UIMusicFestivalRankPanel` | `Slg.UI.Oktoberfest.UIMusicFestivalRankPanel.Config` |
| `UIOverlordRankPreviewPopup` | `UIOverlordRankPreviewPopup` | `UI.Overlord.UIOverlordRankPreviewPopup.Config` |
| `UIPVEStartFightVS` | `UIPVPStartFightVS` | `UI.UIPVPStartFightVS.Config` |
| `UIPVPDamageDate` | `UIPVPDamageDate` | `UI.UIPVPDamageDate.Config` |
| `UIPVPStartFight` | `UIPVPStartFight` | `UI.UIPVPStartFight.Config` |
| `UIPuzzleMonsterRank` | `UIPuzzleMonsterRank` | `UI.UIPuzzleMonster.UIPuzzleMonsterRank.Config` |
| `UIPveActRank` | `UIPveActRank` | `UI.UIPveAct.UIPveActRank.Config` |
| `UIRankDetailList` | `UIRankDetailList` | `Slg.UI.UIRank.UIRankDetailList.Config` |
| `UIRankNew` | `UIRankNew` | `UI.UIRank.UIRankNew.Config` |
| `UIRankTable` | `UIRankTable` | `Slg.UI.UIRank.UIRankTable.Config` |
| `UIRoamingBossRankReward` | `UIRoamingBossRankReward` | `UI.UIRoamingBoss.RankReward.Config` |
| `UIRuinsRankDetail` | `UIRuinsRankDetail` | `UI.UIRuinsRankDetail.Config` |
| `UISeason4DinosaurBossRank` | `UISeason4DinosaurBossRank` | `UI.DinosaurBoss.UISeason4DinosaurBossRank.Config` |
| `UISeason4DinosaurBossRewardAndRankPanel` | `UISeason4DinosaurBossRewardAndRankPanel` | `UI.DinosaurBoss.UISeason4DinosaurBossRewardAndRankPanel.Config` |
| `UISeason4DinosaurEggHatchRank` | `UISeason4DinosaurEggHatchRank` | `UI.UISeason4DinosaurEggHatchRank.Config` |
| `UISeasonEarlBattleTimeS5` | `UISeasonEarlBattleTimeS5` | `Slg.UI.UISeason.UISeasonBaronessMain.UISeasonGhostKingSetTime.Config` |
| `UISeasonForceRank` | `UISeasonForceRank` | `Slg.UI.UISeason.UISeasonForceRank.Config` |
| `UISeasonGhostKingLevel` | `UISeasonGhostKingLevel` | `UI.UIActivityCenterTable.Component.UISeason5GhostKing.UISeasonGhostKingL...` |
| `UISeasonGhostKingRank` | `UISeasonGhostKingRank` | `UI.UIActivityCenterTable.Component.UISeason5GhostKing.UISeasonGhostKingR...` |
| `UISeasonIceCaveUserOccupyRank` | `UISeasonIceCaveUserOccupyRank` | `Slg.UI.UISeason.UISeasonIceCave.UISeasonIceCaveUserOccupyRank.Config` |
| `UISeasonIceCaveWorldRank` | `UISeasonIceCaveWorldRank` | `Slg.UI.UISeason.UISeasonIceCave.WorldRank.Config` |
| `UISeasonNightFallsRank` | `UISeasonNightFallsRank` | `UI.UISeason.UISeasonNightFallsRank.Config` |
| `UISeasonNightSacrificeRankRewardS5` | `UISeasonNightSacrificeRankRewardS5` | `UI.ActivityCenter.Season5.NightSacrifice.UISeasonNightSacrificeRankRewar...` |
| `UISeasonRank` | `UISeasonRank` | `Slg.UI.UISeason.UISeasonRank.Config` |
| `UISeasonRankList` | `UISeasonRankList` | `Slg.UI.UIRank.UISeasonRankList.Config` |
| `UISeasonRankReward` | `UISeasonRankReward` | `UI.UISeasonRankReward.Config` |
| `UISeasonTradeMasterRankView` | `UISeasonTradeMasterRankView` | `Slg.UI.UISeason.UISeasonTradePost.MasterRank.Config` |
| `UISeasonTradeMasterRankViewS5` | `UISeasonTradeMasterRankViewS5` | `Slg.UI.UISeason.UISeasonTradePostS5.MasterRank.Config` |
| `UISeasonTradePostRankView` | `UISeasonTradePostRankView` | `Slg.UI.UISeason.UISeasonTradePost.Rank.Config` |
| `UISeasonTradePostRankViewS5` | `UISeasonTradePostRankViewS5` | `Slg.UI.UISeason.UISeasonTradePostS5.Rank.Config` |
| `UISeasonTrialRank` | `UISeasonTrialRank` | `UI.ActivityCenter.Season3.SeasonSacrifice.UISeasonTrialRank.Config` |
| `UISnowManRank` | `UISnowManRank` | `UI.UISnowManRank.Config` |
| `UISpearPersonalRank` | `UISpearPersonalRank` | `UI.UISpear.UISpearPersonalRank.Config` |
| `UISpearWarzoneRank` | `UISpearWarzoneRank` | `UI.UISpear.UISpearWarzoneRank.Config` |
| `UIStoryRank` | `UIStoryRank` | `UI.UIStory.UIStoryRank.Config` |
| `UIStrongCommanderRank` | `UIStrongCommanderRank` | `UI.UIStrongCommander.UIStrongCommanderRank.Config` |
| `UIStrongCommanderRankGivingRoses` | `UIStrongCommanderRankGivingRoses` | `Slg.UI.UIGivingRosesAct.UIStrongCommanderRankGivingRoses.Config` |
| `UIThanksGivingRankPanel` | `UIThanksGivingRankPanel` | `Slg.UI.Thanksgiving.UIThanksGivingRankPanel.Config` |
| `UIThanksgivingStarRankView` | `UIThanksgivingStarRankView` | `Slg.UI.Thanksgiving.UIThanksgivingStarRankView.Config` |
| `UITimeCompeRank` | `UITimeCompeRank` | `UI.UITimeCompeRank.Config` |
| `UIValentineFoxGloryPersonalRank` | `UIValentineFoxGloryPersonalRank` | `Slg.UI.ValentineNew.UIValentineFoxGloryPersonalRank.Config` |
| `UIVolcanoRank` | `UIVolcanoRank` | `UI.UIVolcanoWar.VolcanoRank.Config` |
| `UIWeekendChallengeCarRank` | `UIWeekendChallengeCarRank` | `UI.UIActivityCenterTable.Component.WeekendChallengeCar.UIWeekendChalleng...` |
| `UIWeekendChallengeRank` | `UIWeekendChallengeRank` | `UI.UIActivityCenterTable.Component.WeekendChallenge.UIWeekendChallengeRa...` |
| `UIWorldBossRank` | `UIWorldBossRank` | `UI.UIWorldBossRank.Config` |
| `UIWorldBossRankPop` | `UIWorldBossRankPop` | `UI.UIWorldBossRankPop.Config` |
| `UIWorldBossRankS5` | `UIWorldBossRankS5` | `UI.UIWorldBossRankS5.Config` |
| `UIWorldTrendRank` | `UIWorldTrendRank` | `UI.UIWorldTrend.UIWorldTrendRank.Config` |
| `UiWorldCupGuessRankAndRewardPanel` | `UiWorldCupGuessRankAndRewardPanel` | `Slg.UI.WorldCup.UIWorldCupGuessRankAndRewardPanel.Config` |

### Army, Troops & Hospital (39 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `UIArmyInfo` | `UIArmyInfo` | `UI.UIArmyInfo.Config` |
| `UIArmySelect` | `UIArmySelect` | `UI.UIArmySelect.Config` |
| `UIArmyTipView3` | `UIArmyTipView3` | `Slg.UI.UIArmyTipView3.Config` |
| `UIArmyTips1` | `UIArmyTips1` | `UI.UIArmyTips1.Config` |
| `UIArmyTips2` | `UIArmyTips2` | `UI.UIArmyTips2.Config` |
| `UIArmyUnlock` | `UIArmyUnlock` | `UI.UIArmyUnlock.Config` |
| `UICampBonus` | `UICampBonus` | `UI.UICampBonus.Config` |
| `UIDeadArmyRecord` | `UIDeadArmyRecord` | `UI.UIDeadArmyRecord.Config` |
| `UIDeadly` | `UIDeadly` | `-` |
| `UIDonateSoldierInfo` | `UIDonateSoldierInfo` | `UI.UIDonateSoldierInfo.Config` |
| `UIDonateSoldierOpenReward` | `UIDonateSoldierOpenReward` | `UI.UIDonateSoldierOpenReward.Config` |
| `UIDonateSoldierReservation` | `UIDonateSoldierReservation` | `UI.UIDonateSoldierReservation.Config` |
| `UIDonateSoldierReward` | `UIDonateSoldierReward` | `UI.UIDonateSoldierReward.Config` |
| `UIDonateSoldierSelect` | `UIDonateSoldierSelect` | `UI.UIDonateSoldierSelect.Config` |
| `UIGolloesCamp` | `UIGolloesCamp` | `UI.UIGolloesCamp.Config` |
| `UIGolloesCamp2` | `UIGolloesCamp2` | `UI.UIGolloesCamp2.Config` |
| `UIHospitalDeath` | `UIHospitalDeath` | `UI.UIHospitalDeath.Config` |
| `UIHospitalGetMore` | `UIHospitalGetMore` | `UI.UIHospitalGetMore.Config` |
| `UIHospitalHelpTips` | `UIHospitalHelpTips` | `UI.UIHospitalHelpTips.Config` |
| `UIHospitalLack` | `UIHospitalLack` | `UI.UIHospitalLack.Config` |
| `UILOCampUnlock` | `UILOCampUnlock` | `UI.UILandingOperation.UILOCampUnlock.Config` |
| `UILWTrainDeparture` | `UILWTrainDeparture` | `UI.UILWRailway.UILWTrainDeparture.Config` |
| `UILWTrainDepartureScienceTips` | `UILWTrainDepartureScienceTips` | `-` |
| `UILWTrainDetail` | `UILWTrainDetail` | `UI.UILWRailway.UILWTrainDetail.Config` |
| `UILWTrainList` | `UILWTrainList` | `UI.UILWRailway.UILWTrainList.Config` |
| `UILWTrainRefreshBox` | `UILWTrainRefreshBox` | `UI.UILWRailway.UILWTrainRefreshBox.Config` |
| `UILWTrainReward` | `UILWTrainReward` | `UI.UILWRailway.UILWTrainReward.Config` |
| `UILWTrainScene` | `UILWTrainScene` | `UI.UILWRailway.UILWTrainScene.Config` |
| `UIMasterySoldier` | `UIMasterySoldier` | `UI.UIMasterySoldier.Config` |
| `UIPveBattleSoldierList` | `UIPveBattleSoldierList` | `UI.UIPVE.UIPveBattleSoldierList.Config` |
| `UIReserveCamp` | `UIReserveCamp` | `UI.UIReserveCamp.Config` |
| `UIReserveToSoldier` | `UIReserveToSoldier` | `UI.UIReServeToSoldier.Config` |
| `UISelectArmy` | `UISelectArmy` | `UI.UISelectArmy.Config` |
| `UITrain` | `UITrain` | `UI.UITrain.Config` |
| `UITrain3V3BattleResult` | `UITrain3V3BattleResult` | `-` |
| `UITrainBattleRecord` | `UITrainBattleRecord` | `UI.UILWRailway.UITrainBattleRecord.Config` |
| `UITrainBuy` | `UITrainBuy` | `UI.UILWRailway.UITrainBuy.Config` |
| `UITrainDriverInvite` | `UITrainDriverInvite` | `UI.UILWRailway.UITrainDriverInvite.Config` |
| `UITrainInfo` | `UITrainInfo` | `UI.UILWRailway.UITrainInfo.Config` |

### Buildings & City (61 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `MainBuildUpgradeSuccess` | `MainBuildUpgradeSuccess` | `-` |
| `UCityCaptureSuccess` | `UCityCaptureSuccess` | `UI.WorldSiege.UCityCaptureSuccess.Config` |
| `UIBarrelHeroBottomInfo` | `UIBarrelHeroBottomInfo` | `UI.UIParkour.UIBarrelHeroBottomInfo.Config` |
| `UIBuildDes` | `UIBuildDes` | `UI.UIBuildDes.Config` |
| `UIBuildDetailList` | `UIBuildDetailList` | `UI.SU_UIBuildDetailList.Config` |
| `UIBuildDetails` | `UIBuildDetails` | `UI.UIBuildDetails.Config` |
| `UIBuildList` | `UIBuildList` | `UI.SU_UIBuildList.Config` |
| `UIBuildQueue` | `UIBuildQueue` | `UI.UIBuildQueue.Config` |
| `UIBuildQueueLease` | `UIBuildQueueLease` | `UI.UIBuildQueueLease.Config` |
| `UIBuildQueueList` | `UIBuildQueueList` | `UI.UIBuildQueueList.Config` |
| `UIBuildTimeOfChange` | `UIBuildTimeOfChange` | `UI.UIBuildTimeOfChange.Config` |
| `UIBuildUnlock` | `UIBuildUnlock` | `UI.UIBuildUnlock.Config` |
| `UIBuildUpUnlock` | `UIBuildUpUnlock` | `UI.UIBuildUpUnlock.Config` |
| `UIBuildUpgrade` | `UIBuildUpgrade` | `-` |
| `UIBuildUpgradeAddDes` | `UIBuildUpgradeAddDes` | `UI.UIBuildUpgradeAddDes.Config` |
| `UIBuildUpgradeSuccess` | `UIBuildUpgradeSuccess` | `UI.UIBuildUpgradeSuccess.Config` |
| `UIBuildUpgradeTip` | `UIBuildUpgradeTip` | `UI.UIBuildUpgradeTip.Config` |
| `UICapacityAdd` | `UICapacityAdd` | `UI.UICapacityAdd.Config` |
| `UICapacityBoxSelect` | `UICapacityBoxSelect` | `UI.UICapacityBoxSelect.Config` |
| `UICapacityFull` | `UICapacityFull` | `UI.UICapacityFull.Config` |
| `UICityBattleActivityPopup` | `UICityBattleActivityPopup` | `UI.WorldSiege.UICityBattleActivityPopup.Config` |
| `UICityMainTip` | `UICityMainTip` | `UI.UICityMainTip.Config` |
| `UICityManage` | `UICityManage` | `UI.UICityManage.Config` |
| `UICityWarBookAdjustAssemblyPoint` | `UICityWarBookAdjustAssemblyPoint` | `UI.WorldSiege.UICityWarBookAdjustAssemblyPoint.Config` |
| `UICityWarBookSuccessDialogPopup` | `UICityWarBookSuccessDialogPopup` | `UI.WorldSiege.UICityWarBookSuccessDialogPopup.Config` |
| `UICityWeather` | `UICityWeather` | `UI.UICityWeather.Config` |
| `UICommonIntroWorldCityDeclare` | `UICommonIntroWorldCityDeclare` | `UI.WorldSiege.UICommonIntroWorldCityDeclare.Config` |
| `UICompletePoliceStation` | `UICompletePoliceStation` | `UI.UICompletePoliceStation.Config` |
| `UICompletePoliceStationUpgrade` | `UICompletePoliceStationUpgrade` | `UI.UICompletePoliceStationUpgrade.Config` |
| `UICrossWonderMoveCityTips` | `UICrossWonderMoveCityTips` | `UI.UICrossWonder.UICrossWonderMoveCityTips.Config` |
| `UIDragonMoveCityConform` | `UIDragonMoveCityConform` | `UI.UIDragonMoveCityConform.Config` |
| `UIFormationDefenceNew` | `UIFormationDefenceNew` | `UI.UIFormationDefence.UIFormationDefenceNew.UIFormationDefenceNew_Config` |
| `UIFormationDefenceTable` | `UIFormationDefenceTable` | `UI.UIFormationDefence.UIFormationDefenceTable.Config` |
| `UIGetPolicewoman` | `UIGetPolicewoman` | `UI.UIGetPolicewoman.Config` |
| `UIGuideWaitToBuildFence` | `UIGuideWaitToBuildFence` | `UI.UIGuideWaitToBuildFence.Config` |
| `UILoadEditorBuild` | `UILoadEditorBuild` | `UI.UILoadEditorBuild.Config` |
| `UILovelyFavor` | `UILovelyFavor` | `UI.UIRobotPack.LovelyFavor.Config` |
| `UIMoveCity` | `UIMoveCity` | `UI.UIMoveCity.Config` |
| `UIMoveCityTip` | `UIMoveCityTip` | `UI.UIMoveCityTip.Config` |
| `UINewBuildUpgrade` | `UINewBuildUpgrade` | `UI.SU_UINewBuildUpgrade.Config` |
| `UIPasture` | `UIPasture` | `UI.UIPasture.Config` |
| `UIPhotoWall` | `UIPhotoWall` | `UI.UIPhotoWall.Config` |
| `UIPhotoWallBox` | `UIPhotoWallBox` | `UI.UIPhotoWallBox.Config` |
| `UIPhotoWallDetail` | `UIPhotoWallDetail` | `UI.UIPhotoWallDetail.Config` |
| `UIPlaceBuild` | `UIPlaceBuild` | `UI.SU_UIPlaceBuild.Config` |
| `UIPlaceBuildWorld` | `UIPlaceBuildWorld` | `UI.SU_UIPlaceBuildWorld.Config` |
| `UIPlaceWorldBuild` | `UIPlaceWorldBuild` | `UI.UIPlaceWorldBuild.Config` |
| `UIPoliceInsigniaShow` | `UIPoliceInsigniaShow` | `UI.UIPoliceInsigniaShow.Config` |
| `UIPoliceStation` | `UIPoliceStation` | `UI.UIPoliceStation.Config` |
| `UIRobotPack` | `UIRobotPack` | `UI.UIRobotPack.RobotPack.Config` |
| `UIRobotWarsRule` | `UIRobotWarsRule` | `UI.UIRobotWarsRule.Config` |
| `UIRuinCityLog` | `UIRuinCityLog` | `Slg.UI.UIRuinCityLog.Config` |
| `UIScienceBuildList` | `UIScienceBuildList` | `UI.UIScienceBuildList.Config` |
| `UISmallPeopleBuildInfo` | `UISmallPeopleBuildInfo` | `UI.UIHseroSmallPeople.UISmallPeopleBuildInfo.Config` |
| `UITutorialAnimation` | `UITutorialAnimation` | `UI.UICityScene.UITutorialAnimation.Config` |
| `UITutorialAnimation1` | `UITutorialAnimation1` | `UI.UICityScene.UITutorialAnimation1.Config` |
| `UITutorialAnimation2` | `UITutorialAnimation2` | `UI.UICityScene.UITutorialAnimation2.Config` |
| `UIWorldBuildList` | `UIWorldBuildList` | `UI.UIWorldBuildList.Config` |
| `UIWorldCityFull` | `UIWorldCityFull` | `UI.UIWorldCityFull.Config` |
| `UI_BuildUseFullScreenDialog` | `UI_BuildUseFullScreenDialog` | `UI.UIGuide.UI_BuildUseFullScreenDialog.Config` |
| `UI_SUBuildRepair` | `UI_SUBuildRepair` | `UI.UIBuildRepair.Config` |

### Chat, Moments & Social (162 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `CardGetReward` | `CardGetReward` | `UI.UIGiftPackage.Component.WeekCard.CardGetReward.Config` |
| `ChatAtMember` | `ChatAtMember` | `Slg.UI.UIChatAtMember.Config` |
| `DecorationGiftRewardIntro` | `DecorationGiftRewardIntro` | `-` |
| `DecorationGiftRewardSend` | `DecorationGiftRewardSend` | `-` |
| `DecorationGiftRewardSendSearch` | `DecorationGiftRewardSendSearch` | `-` |
| `DigTreasureGift` | `DigTreasureGift` | `UI.DigTreasureGift.Config` |
| `GodzillaGift` | `GodzillaGift` | `UI.GodzillaGift.Config` |
| `MailHospitalDetail` | `MailHospitalDetail` | `-` |
| `MailVerificationPopup` | `MailVerificationPopup` | `UI.PayPassword.MailVerificationPopup.Config` |
| `UIActGiftBoxOpen` | `UIActGiftBoxOpen` | `UI.UIActGiftBox.UIActGiftBoxOpen.Config` |
| `UIActGiftBoxReward` | `UIActGiftBoxReward` | `UI.UIActGiftBox.UIActGiftBoxReward.Config` |
| `UIBattlePassGiftPackagePopUp` | `UIBattlePassGiftPackagePopUp` | `UI.UIBattlePassGiftPackagePopUp.Config` |
| `UIBattleReportInfo` | `UIBattleReportInfo` | `Slg.UI.UIMailNew.UIBattleReportInfo.Config` |
| `UIBattleReportInfo4` | `UIBattleReportInfo4` | `Slg.UI.UIMailNew4.UIBattleReportInfo.Config` |
| `UIBindSendMail` | `UIBindSendMail` | `-` |
| `UIBlackChangeMask` | `UIBlackChangeMask` | `UI.UIBlackChangeMask.Config` |
| `UIBlackGradientWindow` | `UIBlackGradientWindow` | `UI.UIBlackGradientWindow.Config` |
| `UIBlackHoleMask` | `UIBlackHoleMask` | `UI.UIBlackHoleMask.Config` |
| `UIBlackKnighReservation` | `UIBlackKnighReservation` | `UI.UIBlackKnighReservation.Config` |
| `UIBlackKnightComing` | `UIBlackKnightComing` | `UI.UIBlackKnightComing.Config` |
| `UIBlackKnightInfo` | `UIBlackKnightInfo` | `UI.UIBlackKnightInfo.Config` |
| `UIBlackKnightMemberInfoMenu` | `UIBlackKnightMemberInfoMenu` | `UI.UIBlackKnightMemberInfoMenu.Config` |
| `UIBlackKnightMemberInfoPopup` | `UIBlackKnightMemberInfoPopup` | `UI.UIBlackKnightMemberInfoPopup.Config` |
| `UIBlackKnightPlayerTips` | `UIBlackKnightPlayerTips` | `UI.UIBlackKnightPlayerTips.Config` |
| `UIBlackLandRuinRecord` | `UIBlackLandRuinRecord` | `Slg.UI.UIBlackLandRuinRecord.Config` |
| `UIBlackView` | `UIBlackView` | `UI.UIBlackView.Config` |
| `UIBlindBoxGiftView` | `UIBlindBoxGiftView` | `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxGiftView.Config` |
| `UICampBonusMailTip` | `UICampBonusMailTip` | `Slg.UI.UIMailNew.UICampBonusMailTip.Config` |
| `UICampBonusMailTip4` | `UICampBonusMailTip4` | `Slg.UI.UIMailNew4.UICampBonusMailTip.Config` |
| `UICarnivalMomentMain` | `UICarnivalMomentMain` | `Slg.UI.UICarnivalMomentMain.Config` |
| `UIChangeChatRoomName` | `UIChangeChatRoomName` | `Slg.UI.UIChatRoom.UIChangeChatRoomName.Config` |
| `UIChangeFriendName` | `UIChangeFriendName` | `Slg.UI.UIFriend.UIChangeFriendName.Config` |
| `UIChangeMail` | `UIChangeMail` | `UI.UIAccount2.UIChangeMail.Config` |
| `UIChat` | `UIChat` | `-` |
| `UIChatCommanderTips` | `UIChatCommanderTips` | `Slg.UI.UIChatCommanderTips.Config` |
| `UIChatEmojiTip` | `UIChatEmojiTip` | `Slg.UI.UIChatRoom.UIChatEmojiTip.Config` |
| `UIChatImgShow` | `UIChatImgShow` | `Slg.UI.UIChatImgShow.Config` |
| `UIChatInviteToJoin` | `UIChatInviteToJoin` | `Slg.UI.UIChatInviteToJoin.Config` |
| `UIChatItemOperatorView` | `UIChatItemOperatorView` | `Slg.UI.UIChatItemOperatorView.Config` |
| `UIChatKickUser` | `UIChatKickUser` | `UI.UIChatNew.UIChatKickUser.Config` |
| `UIChatMomentMotivation` | `UIChatMomentMotivation` | `UI.Moment.UIChatMomentMotivation.Config` |
| `UIChatNew` | `UIChatNew` | `Slg.UI.UIChatNew.Config` |
| `UIChatNew2` | `UIChatNew2` | `-` |
| `UIChatPlayerSetNew` | `UIChatPlayerSetNew` | `Slg.UI.UIChatPlayerSetNew.Config` |
| `UIChatPrivateRoomSet` | `UIChatPrivateRoomSet` | `Slg.UI.UIChatPrivateRoomSet.Config` |
| `UIChatPrivateSet` | `UIChatPrivateSet` | `Slg.UI.UIChatPrivateSet.Config` |
| `UIChatRemoveMember` | `UIChatRemoveMember` | `Slg.UI.UIChatRoom.UIChatRemoveMember.Config` |
| `UIChatReport` | `UIChatReport` | `Slg.UI.UIChatReport.Config` |
| `UIChatRoomManagerSet` | `UIChatRoomManagerSet` | `Slg.UI.UIChatRoomManagerSet.Config` |
| `UIChatRoomPlayerTip` | `UIChatRoomPlayerTip` | `Slg.UI.UIChatRoom.UIChatRoomPlayerTip.Config` |
| `UIChatRoomSetting` | `UIChatRoomSetting` | `Slg.UI.UIChatRoom.UIChatRoomSetting.Config` |
| `UIChatSetLevelLimit` | `UIChatSetLevelLimit` | `Slg.UI.UIChatSetLevelLimit.Config` |
| `UIChatTrumpetPop` | `UIChatTrumpetPop` | `UI.UIChatTrumpetPop.Config` |
| `UIChatVoteCreat` | `UIChatVoteCreat` | `Slg.UI.UIChatVoteCreat.Config` |
| `UIChatVoteCreatTips` | `UIChatVoteCreatTips` | `Slg.UI.UIChatVoteCreatTips.Config` |
| `UIChatVoteMember` | `UIChatVoteMember` | `Slg.UI.UIChatVoteMember.Config` |
| `UIChatVoteMemberInfo` | `UIChatVoteMemberInfo` | `Slg.UI.UIChatVoteMemberInfo.Config` |
| `UIChatWorldShoutAtSomeOne` | `UIChatWorldShoutAtSomeOne` | `Slg.UI.UIChatWorldShoutAtSomeOne.Config` |
| `UICommon18PlusPopupEmail` | `UICommon18PlusPopupEmail` | `UI.UICommon18PlusPopupEmail.Config` |
| `UIDecorationGift` | `UIDecorationGift` | `UI.UIDecorationGift.Config` |
| `UIEmojiSettingPanel` | `UIEmojiSettingPanel` | `UI.UIEmojiSetting.Config` |
| `UIEmojiSettingStateTip` | `UIEmojiSettingStateTip` | `UI.UIEmojiSettingStateTip.Config` |
| `UIFadeBlack` | `UIFadeBlack` | `UI.UIFadeBlack.Config` |
| `UIFishingCatalogGiftHistory` | `UIFishingCatalogGiftHistory` | `UI.UIFishingCatalog.UIFishingCatalogGiftHistory.Config` |
| `UIFishingCatalogGiveGift` | `UIFishingCatalogGiveGift` | `UI.UIFishingCatalog.UIFishingCatalogGiveGift.Config` |
| `UIFishingCatalogGiveGiftSuccess` | `UIFishingCatalogGiveGiftSuccess` | `UI.UIFishingCatalog.UIFishingCatalogGiveGiftSuccess.Config` |
| `UIFriendApply` | `UIFriendApply` | `Slg.UI.UIFriend.UIFriendApply.Config` |
| `UIFriendFind` | `UIFriendFindView` | `Slg.UI.UIFriend.UIFriendFind.Config` |
| `UIFullScreenBlackBG` | `UIFullScreenBlackBG` | `UI.UIPVE.UIFullScreenBlackBG.Config` |
| `UIGiftBoxPackageList` | `UIGiftBoxPackageList` | `UI.UIActGiftBox.UIGiftBoxPackageList.Config` |
| `UIGiftBoxProgressReward` | `UIGiftBoxProgressReward` | `UI.UIGiftBoxProgressReward.Config` |
| `UIGiftPackage` | `UIGiftPackage` | `UI.UIGiftPackage.Config` |
| `UIGiftPackageRewardGet` | `UIGiftPackageRewardGet` | `UI.UIGiftPackageRewardGet.Config` |
| `UIGiftPackageRewardSelect` | `UIGiftPackageRewardSelect` | `UI.UIGiftPackageRewardSelect.Config` |
| `UIGiftPackageSelfSelect` | `UIGiftPackageSelfSelect` | `UI.UIGiftPackageSelfSelect.Config` |
| `UIGiftScoreTips` | `UIGiftScoreTips` | `UI.UIGiftScoreTips.Config` |
| `UIGiftVipPackage` | `UIGiftVipPackage` | `UI.UIGiftVipPackage.Config` |
| `UIGivingRosesGiftAniPanel` | `UIGivingRosesGiftAniPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesGiftAniPanel.Config` |
| `UIGivingRosesGiftPackList` | `UIGivingRosesGiftPackList` | `Slg.UI.UIGivingRosesAct.UIGivingRosesGiftPackList.Config` |
| `UIGivingRosesSendGiftPanel` | `UIGivingRosesSendGiftPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesSendGiftPanel.Config` |
| `UIGuideLoadBlackMask` | `UIGuideLoadBlackMask` | `UI.UIGuideLoadBlackMask.Config` |
| `UIHalloweenGiftRecommendView` | `UIHalloweenGiftRecommendView` | `Slg.UI.UIHalloweenGift.UIHalloweenGiftRecommendView.Config` |
| `UIHalloweenGiftResultView` | `UIHalloweenGiftResultView` | `Slg.UI.UIHalloweenGift.UIHalloweenGiftResultView.Config` |
| `UIHitTurkeyGift` | `UIHitTurkeyGift` | `UI.UIActivityCenterTable.Component.ThanksGiving.HitTurkeyGift.Config` |
| `UIItemChatTitleTip` | `UIItemChatTitleTip` | `UI.UIItemChatTitleTip.Config` |
| `UILensBlackEdge` | `UILensBlackEdge` | `UI.UILensBlackEdge.Config` |
| `UILike` | `UILike` | `UI.UILike.Config` |
| `UILikeHistory` | `UILikeHistory` | `UI.UILike.UILikeHistory.Config` |
| `UILikeMessageBigTips` | `UILikeMessageBigTips` | `UI.UILike.UILikeMessageBigTips.Config` |
| `UILikeMessageTips` | `UILikeMessageTips` | `UI.UILike.UILikeMessageTips.Config` |
| `UILikeRemainTips` | `UILikeRemainTips` | `UI.UILike.UILikeRemainTips.Config` |
| `UILoveNewsletter` | `UILoveNewsletter` | `UI.UILoveNewsletter.Config` |
| `UILoveNewsletterFilter` | `UILoveNewsletterFilter` | `UI.UILoveNewsletterFilter.Config` |
| `UILoveNewsletterMM` | `UILoveNewsletterMM` | `UI.UILoveNewsletterMM.Config` |
| `UILoveNewsletterUnlockPic` | `UILoveNewsletterUnlockPic` | `UI.UILoveNewsletterUnlockPic.Config` |
| `UILoveVideoCall` | `UILoveVideoCall` | `UI.UILoveVideoCall.Config` |
| `UILuckyRollGiftPackList` | `UILuckyRollGiftPackList` | `UI.UILuckyRollGiftPackList.Config` |
| `UILuckyRollHeroGiftPackList` | `UILuckyRollHeroGiftPackList` | `-` |
| `UIMail` | `UIMail` | `-` |
| `UIMailAllUserHeroesView` | `UIMailAllUserHeroesView` | `Slg.UI.UIMailNew.UIMailAllUserHeroesView.Config` |
| `UIMailAuthenticate` | `UIMailAuthenticate` | `UI.UIAccount2.UIMailAuthenticate.Config` |
| `UIMailBattleAttrDetail` | `UIMailBattleAttrDetail` | `Slg.UI.UIMailNew.UIMailBattleAttrDetail.Config` |
| `UIMailBattleAttrDetail4` | `UIMailBattleAttrDetail4` | `Slg.UI.UIMailNew4.UIMailBattleAttrDetail.Config` |
| `UIMailBattleReportDetail` | `UIMailBattleReportDetail` | `UI.UIMailBattleReportDetail.Config` |
| `UIMailCampRestraintDetail` | `UIMailCampRestraintDetail` | `UI.UIFormation.UIMailCampRestraintDetail.Config` |
| `UIMailDetailReportView` | `UIMailDetailReportView` | `Slg.UI.UIMailNew.UIMailDetailReportView.Config` |
| `UIMailDetailReportView4` | `UIMailDetailReportView4` | `Slg.UI.UIMailNew4.UIMailDetailReportView.Config` |
| `UIMailFightContent` | `UIMailFightContent` | `-` |
| `UIMailInfo` | `UIMailInfo` | `Slg.UI.UIMailNew.UIMailInfo.Config` |
| `UIMailInfo4` | `UIMailInfo4` | `Slg.UI.UIMailNew4.UIMailInfo.Config` |
| `UIMailNew` | `UIMailNew` | `Slg.UI.UIMailNew.UIMailMainPanel.Config` |
| `UIMailNew4` | `UIMailNew4` | `Slg.UI.UIMailNew4.UIMailMainPanel.Config` |
| `UIMailReturn` | `UIMailReturn` | `-` |
| `UIMailSend` | `UIMailSend` | `Slg.UI.UIMailNew.UIMailSend.Config` |
| `UIMailSend4` | `UIMailSend4` | `Slg.UI.UIMailNew4.UIMailSend.Config` |
| `UIMailSoldierTips` | `UIMailSoldierTips` | `Slg.UI.UIMailNew.UIMailSoldierTips.Config` |
| `UIMailTroopBuffAddPanel` | `UIMailTroopBuffAddPanel` | `Slg.UI.UIMailNew.UIMailTroopBuffAddPanel.Config` |
| `UIMailTroopInfoListView` | `UIMailTroopInfoListView` | `Slg.UI.UIMailNew.UIMailTroopInfoListView.Config` |
| `UIMailTroopInfoListView4` | `UIMailTroopInfoListView4` | `Slg.UI.UIMailNew4.UIMailTroopInfoListView.Config` |
| `UIMailVerify` | `UIMailVerify` | `UI.UIAccount2.UIMailVerify.Config` |
| `UIMarchEmojiTip` | `UIMarchEmojiTip` | `UI.UIMarchEmojiTip.Config` |
| `UIMasteryPopGift` | `UIMasteryPopGift` | `-` |
| `UIMigrateGiftView` | `UIMigrateGiftView` | `Slg.UI.UIMigrateGift.Config` |
| `UIMomentCommentOperatorView` | `UIMomentCommentOperatorView` | `UI.Moment.UIMomentCommentOperatorView.Config` |
| `UIMomentDetail` | `UIMomentDetail` | `UI.Moment.UIMomentDetail.Config` |
| `UIMomentFollowList` | `UIMomentFollowList` | `UI.Moment.UIMomentFollowList.Config` |
| `UIMomentLikeHistory` | `UIMomentLikeHistory` | `UI.Moment.UIMomentLikeHistory.Config` |
| `UIMomentNotice` | `UIMomentNotice` | `UI.Moment.UIMomentNotice.Config` |
| `UIMomentPost` | `UIMomentPost` | `UI.Moment.UIMomentPost.Config` |
| `UIMomentPostNew` | `UIMomentPostNew` | `UI.Moment.UIMomentPostNew.Config` |
| `UIMomentSet` | `UIMomentSet` | `UI.Moment.UIMomentSet.Config` |
| `UIPINVerifyMailCode` | `UIPINVerifyMailCode` | `UI.UIAccount2.UIPINVerifyMailCode.Config` |
| `UIPresentBigShow` | `UIPresentBigShow` | `UI.UIPresent.UIPresentBigShow.Config` |
| `UIPresentEgg` | `UIPresentEgg` | `UI.UIPresent.UIPresentEgg.Config` |
| `UIPresentGetRewardView` | `UIPresentGetRewardView` | `UI.UIPresent.UIPresentGetRewardView.Config` |
| `UIPresentHistory` | `UIPresentHistory` | `UI.UIPresent.UIPresentHistory.Config` |
| `UIPresentLevel` | `UIPresentLevel` | `UI.UIPresent.UIPresentLevel.Config` |
| `UIPresentList` | `UIPresentList` | `UI.UIPresent.UIPresentList.Config` |
| `UIPresentSend` | `UIPresentSend` | `UI.UIPresent.UIPresentSend.Config` |
| `UIPresentSendTips` | `UIPresentSendTips` | `UI.UIPresent.UIPresentSendTips.Config` |
| `UIPresentShowList` | `UIPresentShowList` | `UI.UIPresent.UIPresentShowList.Config` |
| `UIPrivilegeShopProbabilityPopup` | `UIPrivilegeShopProbabilityPopup` | `UI.UIGiftPackage.Component.PrivilegeShop.PrivilegeShopProbabilityPopup.C...` |
| `UIPublishALAnnouncement` | `UIPublishALAnnouncement` | `Slg.UI.UIPublishALAnnouncement.Config` |
| `UIReportEquipTip` | `UIReportEquipTip` | `Slg.UI.UIMailNew.UIReportEquipTip.Config` |
| `UIReportEquipTip4` | `UIReportEquipTip4` | `Slg.UI.UIMailNew4.UIReportEquipTip.Config` |
| `UIReportResourceIncomeTips` | `UIReportResourceIncomeTips` | `Slg.UI.UIMailNew4_SLG.UIReportResourceIncomeTips.Config` |
| `UIReportWeaponTip` | `UIReportWeaponTip` | `Slg.UI.UIMailNew.UIReportWeaponTip.Config` |
| `UIReportWeaponTip4` | `UIReportWeaponTip4` | `Slg.UI.UIMailNew4.UIReportWeaponTip.Config` |
| `UISettingBlock` | `UISettingBlock` | `Slg.UI.UIFriend.UISettingBlock.Config` |
| `UIShareMail` | `UIShareMail` | `Slg.UI.UIMailNew.UIShareMail.Config` |
| `UIShareMail4` | `UIShareMail4` | `Slg.UI.UIMailNew4.UIShareMail.Config` |
| `UIShowBlack` | `UIShowBlack` | `UI.UIShowBlack.Config` |
| `UIThanksgivingStarNoticePresentTips` | `UIThanksgivingStarNoticePresentTips` | `UI.UIThanksgivingStarNoticePresentTips.Config` |
| `UIValentineFoxGiftBoxReward` | `UIValentineFoxGiftBoxReward` | `Slg.UI.ValentineNew.UIValentineFoxGiftBoxReward.Config` |
| `UIValentineFoxTeamQuickChat` | `UIValentineFoxTeamQuickChat` | `Slg.UI.ValentineNew.UIValentineFoxTeamQuickChat.Config` |
| `UIValentineSendGiftBigShow` | `UIValentineSendGiftBigShow` | `Slg.UI.ValentineNew.UIValentineSendGiftBigShow.Config` |
| `UIValentineSendGiftCardPop` | `UIValentineSendGiftCardPop` | `Slg.UI.ValentineNew.UIValentineSendGiftCardPop.Config` |
| `UIValentineSendGiftConfirmPop` | `UIValentineSendGiftConfirmPop` | `Slg.UI.ValentineNew.UIValentineSendGiftConfirmPop.Config` |
| `UIValentineSendGiftFinalConfirmPop` | `UIValentineSendGiftFinalConfirmPop` | `Slg.UI.ValentineNew.UIValentineSendGiftFinalConfirmPop.Config` |
| `UIValentineSendGiftFriendPop` | `UIValentineSendGiftFriendPop` | `Slg.UI.ValentineNew.UIValentineSendGiftFriendPop.Config` |
| `UIVerifyMail` | `UIVerifyMail` | `UI.UIAccount.UIVerifyMail.Config` |
| `UIWorldBlackTile` | `UIWorldBlackTile` | `UI.UIWorldBlackTile.Config` |

### Core System, Auth & Miscellaneous (407 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `CastleAdventureRewardGet` | `CastleAdventureRewardGet` | `Slg.UI.CastleAdventure.CastleAdventureRewardGet.Config` |
| `MainUI_SU` | `MainUI_SU` | `UI.MainUI_SU.Config` |
| `SevenDayBox` | `SevenDayBox` | `UI.SevenDayBox.Config` |
| `SevenDayBoxNew` | `SevenDayBoxNew` | `UI.SevenDayBoxNew.Config` |
| `ThanksGivingTurkeySelectPlayerPanel` | `ThanksGivingTurkeySelectPlayerPanel` | `Slg.UI.Thanksgiving.TurkeyCook.ThanksGivingTurkeySelectPlayerPanel.Config` |
| `UIAccountBan` | `UIAccountBan` | `UI.UIAccount.UIAccountBan.Config` |
| `UIAccountDeleteVerify` | `UIAccountDeleteVerify` | `UI.UIAccount2.UIAccountDeleteVerify.Config` |
| `UIAccountList` | `UIAccountList` | `UI.UIAccount2.UIAccountList.Config` |
| `UIAccountUnbind` | `UIAccountUnbind` | `UI.UIAccount2.UIAccountUnbind.Config` |
| `UIAccountVerify` | `UIAccountVerify` | `UI.UIAccount2.UIAccountVerify.Config` |
| `UIAddAccount` | `UIAddAccount` | `UI.UIAccount2.UIAddAccount.Config` |
| `UIAddAccountBefore` | `UIAddAccountBefore` | `UI.UIAccount2.UIAddAccountBefore.Config` |
| `UIAddStamina` | `UIAddStamina` | `UI.UIAddStamina.Config` |
| `UIAircraftGradingTip` | `UIAircraftGradingTip` | `UI.UIAircraftGradingTip.Config` |
| `UIAircraftMain` | `UIAircraftMain` | `UI.UIAircraftMain.Config` |
| `UIAircraftMainPreview` | `UIAircraftMainPreview` | `UI.UIAircraftMainPreview.Config` |
| `UIAircraftMainTip` | `UIAircraftMainTip` | `UI.UIAircraftMainTip.Config` |
| `UIAircraftUpgrade` | `UIAircraftUpgrade` | `UI.UIAircraftUpgrade.Config` |
| `UIAircraftUpgradePreview` | `UIAircraftUpgradePreview` | `UI.UIAircraftUpgradePreview.Config` |
| `UIAlCompeteBarrage` | `UIAlCompeteBarrage` | `Slg.UI.UIAlCompeteBarrage.Config` |
| `UIAlCompeteBarrageTip` | `UIAlCompeteBarrageTip` | `Slg.UI.UIAlCompeteBarrageTip.Config` |
| `UIAlCompeteTips` | `UIAlCompeteTips` | `UI.UIAlCompeteTips.Config` |
| `UIArrow` | `UIArrow` | `UI.UIArrow.Config` |
| `UIAutoProductChoose` | `UIAutoProductChoose` | `-` |
| `UIAutoProductList` | `UIAutoProductList` | `-` |
| `UIAutoProductTip` | `UIAutoProductTip` | `-` |
| `UIBaubleInfo` | `UIBaubleInfo` | `UI.UIBauble.UIBaubleInfo.Config` |
| `UIBaubleInfoPopup` | `UIBaubleInfoPopup` | `UI.UIBauble.UIBaubleInfoPopup.Config` |
| `UIBaubleLevelUpPopup` | `UIBaubleLevelUpPopup` | `UI.UIBauble.UIBaubleLevelUpPopup.Config` |
| `UIBaubleLibrary` | `UIBaubleLibrary` | `UI.UIBauble.UIBaubleLibrary.Config` |
| `UIBaubleRatingPopup` | `UIBaubleRatingPopup` | `UI.UIBauble.UIBaubleRatingPopup.Config` |
| `UIBaubleUpgrade` | `UIBaubleUpgrade` | `UI.UIBauble.UIBaubleUpgrade.Config` |
| `UIBaubleUpgradePopup` | `UIBaubleUpgradePopup` | `UI.UIBauble.UIBaubleUpgradePopup.Config` |
| `UIBaubleUpgradeSuccessPopup` | `UIBaubleUpgradeSuccessPopup` | `UI.UIBauble.UIBaubleUpgradeSuccessPopup.Config` |
| `UIBindAccount` | `UIBindAccount` | `UI.UIAccount2.UIBindAccount.Config` |
| `UIBindAccountAlready` | `UIBindAccountAlready` | `UI.UIAccount.UIBindAccountAlready.Config` |
| `UIBindAccountCreate` | `UIBindAccountCreate` | `UI.UIAccount.UIBindAccountCreate.Config` |
| `UIBindAccountDes` | `UIBindAccountDes` | `-` |
| `UIBindSuccess` | `UIBindSuccess` | `UI.UIAccount2.UIBindSuccess.Config` |
| `UIBlindBoxRewardOpenView` | `UIBlindBoxRewardOpenView` | `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxRewardOpenView.Config` |
| `UIBlindBoxRuleView` | `UIBlindBoxRuleView` | `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxRuleView.Config` |
| `UIBlindBoxScoreView` | `UIBlindBoxScoreView` | `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxScoreView.Config` |
| `UIBlindBoxSelectBoxEasterView` | `UIBlindBoxSelectBoxEasterView` | `Slg.UI.Easter.UIBlindBoxSelectBoxEasterView.Config` |
| `UIBlindBoxSelectBoxView` | `UIBlindBoxSelectBoxView` | `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxSelectBoxView.Config` |
| `UIBookMark` | `UIBookMark` | `UI.UIBookMark.Config` |
| `UIBookMarkAdd` | `UIBookMarkAdd` | `UI.UIBookMarkAdd.Config` |
| `UICameraInfo` | `UICameraInfo` | `UI.UICameraInfo.Config` |
| `UIChangeName` | `UIChangeName` | `UI.UIChangeName.Config` |
| `UIChangeNameGender` | `UIChangeNameGender` | `UI.UIChangeNameGender.Config` |
| `UIChapterSwitch` | `UIChapterSwitch` | `UI.UIChapterSwitch.Config` |
| `UICheckServer` | `UICheckServer` | `UI.UICheckServer.Config` |
| `UIChooseServer` | `UIChooseServerView` | `Slg.UI.UISetting.UIChooseServer.Config` |
| `UIChooseServerAccountList` | `UIChooseServerAccountList` | `UI.UILoading.UIChooseServerAccountList.Config` |
| `UIChoseRollBySelf` | `UIChoseRollBySelf` | `UI.UIChoseRollBySelf.Config` |
| `UICommon18PlusPopupAge` | `UICommon18PlusPopupAge` | `UI.UICommon18PlusPopupAge.Config` |
| `UICommonAttrTip` | `UICommonAttrTip` | `UI.UICommonAttrTip.Config` |
| `UICommonChangeValue` | `UICommonChangeValue` | `UI.Common.UICommonChangeValue.Config` |
| `UICommonCostConfirm` | `UICommonCostConfirm` | `UI.UICommonCostConfirm.Config` |
| `UICommonCountTimeMessageTip` | `UICommonCountTimeMessageTip` | `UI.UICommonCountTimeMessageTip.Config` |
| `UICommonCredit` | `UICommonCredit` | `Slg.UI.UICommonCredit.Config` |
| `UICommonCredit2` | `UICommonCredit2` | `Slg.UI.UICommonCredit2.Config` |
| `UICommonDesTip` | `UICommonDesTip` | `UI.UICommonDesTip.Config` |
| `UICommonHeadTip` | `UICommonHeadTip` | `UI.UICommonHeadTip.Config` |
| `UICommonIntro2` | `UICommonIntro2` | `UI.UICommonIntro2.Config` |
| `UICommonIntroTip` | `UICommonIntroTip` | `UI.UICommonIntroTip.Config` |
| `UICommonKVTip` | `UICommonKVTip` | `UI.Common.UICommonKVTip.Config` |
| `UICommonMessageBar` | `UICommonMessageBar` | `UI.UICommonMessageBar.Config` |
| `UICommonMessageSpecialBar` | `UICommonMessageSpecialBar` | `UI.UICommonMessageSpecialBar.Config` |
| `UICommonMessageTip` | `UICommonMessageTip` | `UI.UICommonMessageTip.Config` |
| `UICommonMessageTipBig` | `UICommonMessageTipBig` | `UI.UICommonMessageTipBig.Config` |
| `UICommonRuleImg` | `UICommonRuleImg` | `UI.UICommonRuleImg.Config` |
| `UICommonSingleMsgBar` | `UICommonSingleMsgBar` | `UI.UICommonSingleMsgBar.Config` |
| `UICommonTextTips` | `UICommonTextTips` | `UI.UICommonTextTips.Config` |
| `UICommonTipView` | `UICommonTipView` | `UI.UICommonTipView.Config` |
| `UICommonTipWithNoMind` | `UICommonTipWithNoMind` | `Slg.UI.UICommonTipWithNoMind.Config` |
| `UICommonWait` | `UICommonWait` | `UI.CommonWait.Config` |
| `UIComplexTip` | `UIComplexTip` | `UI.UIComplexTip.Config` |
| `UIConcertListView` | `UIConcertListView` | `Slg.UI.Oktoberfest.Concert.UIConcertListView.Config` |
| `UIConcertPositionShareConfirmView` | `UIConcertPositionShareConfirmView` | `Slg.UI.Oktoberfest.Concert.UIConcertPositionShareConfirmView.Config` |
| `UIConcertPositionShareView` | `UIConcertPositionShareView` | `Slg.UI.Oktoberfest.Concert.UIConcertPositionShareView.Config` |
| `UIConcertRateView` | `UIConcertRateView` | `Slg.UI.Oktoberfest.Concert.UIConcertRateView.Config` |
| `UIConcertTipView` | `UIConcertTipView` | `Slg.UI.Oktoberfest.Concert.UIConcertTipView.Config` |
| `UICreateAccount` | `UICreateAccount` | `UI.UIAccount2.UICreateAccount.Config` |
| `UICreditMainPanel` | `UICreditMainPanel` | `Slg.UI.UICreditMainPanel.Config` |
| `UICreditMainPanel2` | `UICreditMainPanel2` | `Slg.UI.UICreditMainPanel2.Config` |
| `UICreditTip` | `UICreditTip` | `Slg.UI.UICreditTip.Config` |
| `UICrossDisconnect` | `UICrossDisconnect` | `UI.UICrossDisconnect.Config` |
| `UICrossServerList` | `UICrossServerList` | `UI.UICrossServerList.Config` |
| `UICrossWonderBadge` | `UICrossWonderBadge` | `UI.UICrossWonder.UICrossWonderBadge.Config` |
| `UICrossWonderCountdownPanel` | `UICrossWonderCountdownPanel` | `UI.UICrossWonder.UICrossWonderCountdownPanel.Config` |
| `UICrossWonderHistory` | `UICrossWonderHistory` | `UI.UICrossWonder.UICrossWonderHistory.Config` |
| `UICrossWonderMarkRemindNotice` | `UICrossWonderMarkRemindNotice` | `UI.UICrossWonderMarkRemindNotice.Config` |
| `UICrossWonderPreviewRule1` | `UICrossWonderPreviewRule1` | `UI.UICrossWonder.UICrossWonderPreviewRule1.Config` |
| `UICrossWonderPreviewRule2` | `UICrossWonderPreviewRule2` | `UI.UICrossWonder.UICrossWonderPreviewRule2.Config` |
| `UICrossWonderReward` | `UICrossWonderReward` | `UI.UICrossWonder.UICrossWonderReward.Config` |
| `UICrossWonderRule` | `UICrossWonderRule` | `UI.UICrossWonder.UICrossWonderRule.Config` |
| `UICrossWonderTarget` | `UICrossWonderTarget` | `UI.UICrossWonder.UICrossWonderTarget.Config` |
| `UICrossWorm` | `UICrossWorm` | `-` |
| `UICycleBoxRewardPreView` | `UICycleBoxRewardPreView` | `Slg.UI.CycleBox.UICycleBoxRewardPreView.Config` |
| `UICycleBoxScoreRewardView` | `UICycleBoxScoreRewardView` | `Slg.UI.CycleBox.UICycleBoxScoreRewardView.Config` |
| `UIDebugChooseServer` | `UIDebugChooseServer` | `UI.UILoading.UIDebugChooseServer.Config` |
| `UIDeclareWarCountDownTitle` | `UIDeclareWarCountDownTitle` | `UI.UIGlory.UIDeclareWarCountDownTitle.Config` |
| `UIDeclareWarList` | `UIDeclareWarList` | `UI.UIDeclareWarList.Config` |
| `UIDecorateUnlock` | `UIDecorateUnlock` | `UI.UIDecoration.UIDecorateUnlock.Config` |
| `UIDecorationMain` | `UIDecorationMain` | `UI.UIDecoration.UIDecorationMain.Config` |
| `UIDecorationUpgradeInfoPopup` | `UIDecorationUpgradeInfoPopup` | `UI.UIDecoration.UIDecorationUpgradeInfoPopup.Config` |
| `UIDecorationUpgradePopup` | `UIDecorationUpgradePopup` | `UI.UIDecoration.UIDecorationUpgradePopup.Config` |
| `UIDecorationUpgradeSuccess` | `UIDecorationUpgradeSuccess` | `UI.UIDecoration.UIDecorationUpgradeSuccess.Config` |
| `UIDeleteAccountConfirm` | `UIDeleteAccountConfirm` | `UI.UISetting.UIDeleteAccountConfirm.Config` |
| `UIDeleteAccountIntro` | `UIDeleteAccountIntro` | `UI.UISetting.UIDeleteAccountIntro.Config` |
| `UIDeleteAccountIntroNew` | `UIDeleteAccountIntroNew` | `UI.UISetting.UIDeleteAccountIntroNew.Config` |
| `UIDeleteAccountNotice` | `UIDeleteAccountNotice` | `UI.UISetting.UIDeleteAccountNotice.Config` |
| `UIDeleteAccountNoticeNew` | `UIDeleteAccountNoticeNew` | `UI.UISetting.UIDeleteAccountNoticeNew.Config` |
| `UIDemolishChangeConfirm` | `UIDemolishChangeConfirm` | `UI.UIDemolish.DemolishChangePanel.Config` |
| `UIDemolishChangeLog` | `UIDemolishChangeLog` | `UI.UIDemolish.DemolishChangeLogPanel.Config` |
| `UIDemolishSelectMember` | `UIDemolishSelectMember` | `UI.UIDemolish.DemolishSelectMemberPanel.Config` |
| `UIDemonHunterEntrust` | `UIDemonHunterEntrust` | `UI.DemonHunter.UIDemonHunterEntrust.Config` |
| `UIDemonHunterTalk` | `UIDemonHunterTalk` | `UI.DemonHunter.UIDemonHunterTalk.Config` |
| `UIDesertOperate` | `UIDesertOperate` | `UI.UIDesertOperate.Config` |
| `UIDesertPercent` | `UIDesertPercent` | `-` |
| `UIDisconnect` | `UIDisconnect` | `UI.SU_UIDisconnect.Config` |
| `UIDispatchRewardGet` | `UIDispatchRewardGet` | `UI.UIDispatchRewardGet.Config` |
| `UIDomeUpdate` | `UIDomeUpdate` | `UI.UIDomeUpdate.Config` |
| `UIDragoMemberSwapConfig` | `UIDragoMemberSwapConfig` | `UI.UIDragonSwap.DragoMemberSwapConfigPanel.Config` |
| `UIDragonCommand` | `UIDragonCommand` | `UI.UIDragonCommand.Config` |
| `UIDragonEggHatch` | `UIDragonEggHatch` | `UI.UIDragonEggHatch.Config` |
| `UIDragonEggPreview` | `UIDragonEggPreview` | `UI.UIDragonEggPreview.Config` |
| `UIDragonExplainCommand` | `UIDragonExplainCommand` | `UI.UIDragonExplain.Command.Config` |
| `UIDragonExplainPlay` | `UIDragonExplainPlay` | `UI.UIDragonExplain.Play.Config` |
| `UIDragonHistoryScore` | `UIDragonHistoryScore` | `UI.UIDragonHistoryScore.Config` |
| `UIDragonMark` | `UIDragonMark` | `UI.UIDragonMark.Config` |
| `UIDragonMemberSwap` | `UIDragonMemberSwap` | `UI.UIDragonSwap.DragonMemberSwapPanel.Config` |
| `UIDragonMemberSwapRecord` | `UIDragonMemberSwapRecord` | `UI.UIDragonSwap.DragonMemberSwapRecordPanel.Config` |
| `UIDragonMemberSwapSelect` | `UIDragonMemberSwapSelect` | `UI.UIDragonSwap.DragonMemberSelectPanel.Config` |
| `UIDragonMessageTip` | `UIDragonMessageTip` | `UI.UIDragonMessageTip.Config` |
| `UIDragonSelectMember` | `UIDragonSelectMember` | `UI.UIDragonSelectMember.Config` |
| `UIDragonSelectMemberAllinOne` | `UIDragonSelectMemberAllinOne` | `UI.UIDragonSelectMemberAllinOne.Config` |
| `UIDragonSelectMemberNoTeam` | `UIDragonSelectMemberNoTeam` | `UI.UIDragonSelectMemberNoTeam.Config` |
| `UIDragonSelectMemberSortFilter` | `UIDragonSelectMemberSortFilter` | `UI.UIDragonSelectMemberSortFilter.Config` |
| `UIDragonSelectMemberTeam` | `UIDragonSelectMemberTeam` | `UI.UIDragonSelectMemberTeam.Config` |
| `UIDynamicRewardRate` | `UIDynamicRewardRate` | `UI.UIDynamicRewardRate.Config` |
| `UIEasterBlindBoxLevelRewardPanel` | `UIEasterBlindBoxLevelRewardPanel` | `Slg.UI.Easter.UIEasterLevelRewardPanel.Config` |
| `UIEasterBlindBoxRuleView` | `UIEasterBlindBoxRuleView` | `Slg.UI.Easter.UIBlindBoxRuleEasterView.Config` |
| `UIEnergyBank` | `UIEnergyBank` | `UI.UIEnergyBank.Config` |
| `UIEnergyBankTip` | `UIEnergyBankTip` | `UI.UIEnergyBankTip.Config` |
| `UIFinalWaveTip` | `UIFinalWaveTip` | `UI.UIParkour.UIFinalWaveTip.Config` |
| `UIFingerArrow` | `UIFingerArrow` | `UI.UIFingerArrow.Config` |
| `UIFirstCharge` | `UIFirstCharge` | `UI.UIFirstCharge.UIFirstCharge.Config` |
| `UIFirstCharge2` | `UIFirstCharge2` | `UI.UIFirstCharge2.Config` |
| `UIFirstChargeTip` | `UIFirstChargeTip` | `UI.UIFirstCharge.UIFirstChargeTip.Config` |
| `UIFishingCatalogDetail` | `UIFishingCatalogDetail` | `UI.UIFishingCatalog.UIFishingCatalogDetail.Config` |
| `UIFishingCatalogMain` | `UIFishingCatalogMain` | `UI.UIFishingCatalog.UIFishingCatalogMain.Config` |
| `UIFishingCatalogUnlock` | `UIFishingCatalogUnlock` | `UI.UIFishingCatalog.UIFishingCatalogUnlock.Config` |
| `UIForcesDetail` | `UIForcesDetail` | `UI.UIForcesDetail.Config` |
| `UIFoxHello` | `UIFoxHello` | `UI.UIFoxHello.Config` |
| `UIFullScreenTranslationPopup` | `UIFullScreenTranslationPopup` | `UI.UIFullScreenTranslationPopup.Config` |
| `UIGGUnBindAccount` | `UIGGUnBindAccount` | `UI.UIAccount2.UIGGUnBindAccount.Config` |
| `UIGameCenterChangeBind` | `UIGameCenterChangeBind` | `UI.UISetting.UIGameCenterChangeBind.Config` |
| `UIGetPickaxe` | `UIGetPickaxe` | `UI.UIGetPickaxe.Config` |
| `UIGetRewardView` | `UIGetRewardView` | `UI.UIGetRewardView.Config` |
| `UIGirlSelect` | `UIGirlSelect` | `UI.UIGirlSelect.Config` |
| `UIGive` | `UIGive` | `UI.UIGive.Config` |
| `UIGivingRoseRewardGet` | `UIGivingRoseRewardGet` | `UI.UIGivingRoseRewardGet.Config` |
| `UIGivingRoses2Castle` | `UIGivingRoses2Castle` | `UI.UIValentine.Config` |
| `UIGloryDeclare` | `UIGloryDeclare` | `UI.UIGlory.UIGloryDeclare.Config` |
| `UIGloryDeclareWarLastHit` | `UIGloryDeclareWarLastHit` | `UI.UIGloryDeclareWarLastHit.Config` |
| `UIGloryDeclareWarPop` | `UIGloryDeclareWarPop` | `UI.UIGloryDeclareWarPop.Config` |
| `UIGloryDeclareWarPopTips` | `UIGloryDeclareWarPopTips` | `UI.UIGlory.UIGloryDeclareWarPopTips.Config` |
| `UIGloryGroup` | `UIGloryGroup` | `UI.UIGlory.UIGloryGroup.Config` |
| `UIGloryInfo` | `UIGloryInfo` | `UI.UIGlory.UIGloryInfo.Config` |
| `UIGloryMatch` | `UIGloryMatch` | `Slg.UI.UIGlory.UIGloryMatch.Config` |
| `UIGloryReward` | `UIGloryReward` | `UI.UIGlory.UIGloryReward.UIGloryReward.Config` |
| `UIGloryRule` | `UIGloryRule` | `UI.UIGlory.UIGloryRule.Config` |
| `UIGlorySetTruceRecord` | `UIGlorySetTruceRecord` | `Slg.UI.UIGlory.UIGlorySetTruceRecord.Config` |
| `UIGloryWarSwapHistoryPopup` | `UIGloryWarSwapHistoryPopup` | `UI.UIGloryWarSwap.UIGloryWarSwapHistoryPopup.Config` |
| `UIGloryWarSwapSelectMember` | `UIGloryWarSwapSelectMember` | `UI.UIGloryWarSwap.UIGloryWarSwapSelectMember.Config` |
| `UIGloryWarSwapTip` | `UIGloryWarSwapTip` | `UI.UIGloryWarSwap.UIGloryWarSwapTip.Config` |
| `UIGloryWarSwapUsePopup` | `UIGloryWarSwapUsePopup` | `UI.UIGloryWarSwap.UIGloryWarSwapUsePopup.Config` |
| `UIGolloesUnlockReward` | `UIGolloesUnlockReward` | `UI.UIGolloesUnlockReward.Config` |
| `UIGovernmentInfo` | `UIGovernmentInfo` | `UI.UIGovernment.UIGovernmentInfo.Config` |
| `UIGovernmentMain` | `UIGovernmentMain` | `UI.UIGovernment.UIGovernmentMain.Config` |
| `UIGridDebug` | `UIGridDebug` | `UI.UIGridDebug.Config` |
| `UIHHShowTip` | `UIHHShowTip` | `UI.UIHHShowTip.Config` |
| `UIHalloweenDrawLotteryDetailView` | `UIHalloweenDrawLotteryDetailView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawLotteryDetailView.Config` |
| `UIHalloweenDrawLotteryListView` | `UIHalloweenDrawLotteryListView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawLotteryListView.Config` |
| `UIHalloweenDrawLotteryLogView` | `UIHalloweenDrawLotteryLogView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawLotteryLogView.Config` |
| `UIHalloweenDrawRewardView` | `UIHalloweenDrawRewardView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawRewardView.Config` |
| `UIHalloweenMarbleRecord` | `UIHalloweenMarbleRecord` | `Slg.UI.HalloweenMarble.UIHalloweenMarbleRecord.Config` |
| `UIHalloweenMarbleRewardloop` | `UIHalloweenMarbleRewardloop` | `Slg.UI.HalloweenMarble.UIHalloweenMarbleRewardloop.Config` |
| `UIHalloweenMarbleSliderReward` | `UIHalloweenMarbleSliderReward` | `Slg.UI.HalloweenMarble.UIHalloweenMarbleSliderReward.Config` |
| `UIHalloweenPopNotice` | `UIHalloweenPopNotice` | `Slg.UI.HalloweenMarble.UIHalloweenPopNotice.Config` |
| `UIHeadIconShow` | `UIHeadIconShow` | `UI.UIHeadIconShow.Config` |
| `UIHeadTalk` | `UIHeadTalk` | `UI.UIHeadTalk.Config` |
| `UIIronAgeNotice` | `UIIronAgeNotice` | `UI.UIIronAgeNotice.Config` |
| `UIJeepAdventureMain` | `UIJeepAdventureMain` | `UI.UIJeepAdventure.UIJeepAdventureMain.Config` |
| `UIJoinGroupTip` | `UIJoinGroupTip` | `Slg.UI.UIJoinGroupTip.Config` |
| `UIJoystick` | `UIJoystick` | `UI.UIJoystick.Config` |
| `UIKonbini` | `UIKonbini` | `UI.UIKonbini.Config` |
| `UILandLockEnter` | `UILandLockEnter` | `-` |
| `UILandLockTips` | `UILandLockTips` | `UI.UI_LandLockTips.Config` |
| `UILandLockTips1` | `UILandLockTips1` | `UI.UI_LandLockTips1.Config` |
| `UILeagueMatchReward` | `UILeagueMatchReward` | `UI.LeagueMatch.UILeagueMatchReward.Config` |
| `UILetterBoxing` | `UILetterBoxing` | `UI.UIParkour.UILetterBoxing.Config` |
| `UILevelUp` | `UILevelUp` | `UI.UILevelUp.Config` |
| `UILoPowerLack` | `UILoPowerLack` | `UI.UILandingOperation.UILOPowerLack.Config` |
| `UILuckyRollRewardGet` | `UILuckyRollRewardGet` | `UI.UILuckyRollRewardGet.Config` |
| `UILuckyRollRewardSelect` | `UILuckyRollRewardSelect` | `-` |
| `UILuckyRollRewardTip` | `UILuckyRollRewardTip` | `UI.UILuckyRollRewardTip.Config` |
| `UILuckyRollTip` | `UILuckyRollTip` | `UI.UILuckyRollTip.Config` |
| `UIMain` | `MainUI_SU` | `UI.MainUI_SU.Config` |
| `UIMainAccountBind` | `UIMainAccountBind` | `UI.UIMainAccountBind.Config` |
| `UIMainMsgView` | `UIMainMsgView` | `UI.UIMainMsgView.Config` |
| `UIMainNotice` | `UIMainNotice` | `UI.UIMainNotice.Config` |
| `UIMainPlayerReportTable` | `UIMainPlayerReportTable` | `UI.UIMainPlayerReportTable.Config` |
| `UIMainPromptView` | `UIMainPromptView` | `UI.UIMainPromptView.Config` |
| `UIMedalGet` | `UIMedalGet` | `UI.UIMedalGet.Config` |
| `UIMigrateApp` | `UIMigrateApp` | `Slg.UI.UIMigrate.UIMigrateApp.Config` |
| `UIMigrateDetail` | `UIMigrateDetail` | `Slg.UI.UIMigrate.UIMigrateDetail.Config` |
| `UIMigrateFinish` | `UIMigrateFinish` | `Slg.UI.UIMigrate.UIMigrateFinish.Config` |
| `UIMigrateInvite` | `UIMigrateInvite` | `Slg.UI.UIMigrate.UIMigrateInvite.Config` |
| `UIMigrateInviteList` | `UIMigrateInviteList` | `Slg.UI.UIMigrate.UIMigrateInviteList.Config` |
| `UIMigrateLevelTip` | `UIMigrateLevelTip` | `Slg.UI.UIMigrate.UIMigrateLevelTip.Config` |
| `UIMigrateList` | `UIMigrateList` | `Slg.UI.UIMigrate.UIMigrateList.Config` |
| `UIMigrateToServer` | `UIMigrateToServer` | `Slg.UI.UIMigrate.UIMigrateToServer.Config` |
| `UIMigrating` | `UIMigrating` | `UI.UIMigrating.Config` |
| `UIMilitaryForceLog` | `UIMilitaryForceLog` | `UI.UIMilitaryForceLog.Config` |
| `UIMilitaryLack` | `UIMilitaryLack` | `UI.UIMilitaryLack.Config` |
| `UIModifySuccess` | `UIModifySuccess` | `UI.UIAccount2.UIModifySuccess.Config` |
| `UIMoving` | `UIMoving` | `UI.UIMoving.Config` |
| `UIMsgAwait` | `UIMsgAwait` | `Slg.UI.UIMsgAwait.Config` |
| `UIMultiLanguageFloatingBall` | `UIMultiLanguageFloatingBall` | `UI.UIMultiLanguageFeedback.UIMultiLanguageFloatingBall.Config` |
| `UIMultiLanguagePop` | `UIMultiLanguagePop` | `UI.UIMultiLanguageFeedback.UIMultiLanguagePop.Config` |
| `UIMultiLanguagePush` | `UIMultiLanguagePush` | `UI.UIMultiLanguageFeedback.UIMultiLanguagePush.Config` |
| `UINoInput` | `UINoInput` | `UI.UINoInput.Config` |
| `UINoticeAlCompeteTips` | `UINoticeAlCompeteTips` | `UI.UINoticeAlCompeteTips.Config` |
| `UINoticePhonographTips` | `UINoticePhonographTips` | `UI.UINoticePhonographTips.Config` |
| `UINoticeTips` | `UINoticeTips` | `UI.UINoticeTips.Config` |
| `UINpcQN` | `UINpcQN` | `UI.UINpcQN.Config` |
| `UIOneClickSweepMain` | `UIOneClickSweepMain` | `Slg.UI.OneClickSweep.Config` |
| `UIOneClickSweepNotice` | `UIOneClickSweepNotice` | `Slg.UI.OneClickSweep.Notice.Config` |
| `UIOneClickSweepRule` | `UIOneClickSweepRule` | `Slg.UI.OneClickSweep.Rule.Config` |
| `UIOtherPlayerInfo` | `UIOtherPlayerInfo` | `Slg.UI.UIOtherPlayerInfo.Config` |
| `UIOverlord` | `UIOverlord` | `UI.Overlord.UIOverlord.Config` |
| `UIOverlordArchivePopup` | `UIOverlordArchivePopup` | `UI.Overlord.UIOverlordArchivePopup.Config` |
| `UIOverlordChallengePop` | `UIOverlordChallengePop` | `UI.Overlord.UIOverlordChallengePop.Config` |
| `UIOverlordChangeNamePopup` | `UIOverlordChangeNamePopup` | `UI.Overlord.UIOverlordChangeNamePopup.Config` |
| `UIOverlordFilePopup` | `UIOverlordFilePopup` | `UI.Overlord.UIOverlordFilePopup.Config` |
| `UIOverlordHuntMilestone` | `UIOverlordHuntMilestone` | `UI.Overlord.UIOverlordHuntMilestone.Config` |
| `UIOverlordMilitaryRatingPreviewPopup` | `UIOverlordMilitaryRatingPreviewPopup` | `UI.Overlord.UIOverlordMilitaryRatingPreviewPopup.Config` |
| `UIOverlordMilitaryUpgradePopup` | `UIOverlordMilitaryUpgradePopup` | `UI.Overlord.UIOverlordMilitaryUpgradePopup.Config` |
| `UIOverlordPropertyPopup` | `UIOverlordPropertyPopup` | `UI.Overlord.UIOverlordPropertyPopup.Config` |
| `UIOverlordSelectPopup` | `UIOverlordSelectPopup` | `UI.Overlord.UIOverlordSelectPopup.Config` |
| `UIOverlordTreatment` | `UIOverlordTreatment` | `UI.Overlord.UIOverlordTreatment.Config` |
| `UIPCWebView` | `UIPCWebView` | `UI.UIPCWebView.Config` |
| `UIPINCodeInput` | `UIPINCodeInput` | `UI.UIAccount2.UIPINCodeInput.Config` |
| `UIParkourThreeChoices` | `UIParkourThreeChoices` | `UI.UIParkour.ThreeChoicesUI.Config` |
| `UIPathArrow` | `UIPathArrow` | `UI.UIPathArrow.Config` |
| `UIPersonalWar` | `UIPersonalWar` | `-` |
| `UIPhonographMain` | `UIPhonographMain` | `UI.UIPhonograp.UIPhonographMain.Config` |
| `UIPhonographMarquee` | `UIPhonographMarquee` | `UI.UIPhonograp.UIPhonographMarquee.Config` |
| `UIPhonographPlayTips` | `UIPhonographPlayTips` | `UI.UIPhonograp.UIPhonographPlayTips.Config` |
| `UIPhonographRecord` | `UIPhonographRecord` | `UI.UIPhonograp.UIPhonographRecord.Config` |
| `UIPiggyBank` | `UIPiggyBank` | `UI.UIPiggyBank.Config` |
| `UIPiggyBankTip` | `UIPiggyBankTip` | `UI.UIPiggyBankTip.Config` |
| `UIPinForget` | `UIPinForget` | `UI.UIPin.UIPinForget.Config` |
| `UIPinInput` | `UIPinInput` | `UI.UIPin.UIPinInput.Config` |
| `UIPinSet` | `UIPinSet` | `UI.UIPin.UIPinSet.Config` |
| `UIPinUseSet` | `UIPinUseSet` | `UI.UIPin.UIPinUseSet.Config` |
| `UIPing` | `UIPing` | `UI.UISetting.UIPing.Config` |
| `UIPlaceBauble` | `UIPlaceBauble` | `UI.UIPlaceBauble.Config` |
| `UIPlayerChangeHeadIcon` | `UIPlayerChangeHeadIcon` | `Slg.UI.UIPlayerChangeHeadIcon.Config` |
| `UIPlayerGenderSelect` | `UIPlayerGenderSelect` | `Slg.UI.UIPlayerGenderSelect.Config` |
| `UIPlayerHeadIconSelect` | `UIPlayerHeadIconSelect` | `Slg.UI.UIPlayerHeadIconSelect.Config` |
| `UIPlayerInfo` | `UIPlayerInfo` | `Slg.UI.UIPlayerInfo.Config` |
| `UIPositionAdd` | `UIPositionAdd` | `Slg.UI.UIPositionAdd.Config` |
| `UIPositionFavorite` | `UIPositionFavorite` | `UI.UIPositionFavorite.Config` |
| `UIPositionShare` | `UIPositionShare` | `UI.UIPositionShare.Config` |
| `UIPositionShareConfirm` | `UIPositionShareConfirm` | `UI.UIPositionShareConfirm.Config` |
| `UIPositionTip` | `UIPositionTip` | `UI.UIPositionTip.Config` |
| `UIPowerChangeTip` | `UIPowerChangeTip` | `-` |
| `UIPrivacy` | `UIPrivacy` | `UI.UIPrivacy.Config` |
| `UIPrivacy2` | `UIPrivacy2` | `UI.UIPrivacy2.Config` |
| `UIPrivacy3` | `UIPrivacy3` | `UI.UIPrivacy3.Config` |
| `UIPrograssBar` | `UIPrograssBar` | `UI.UIPrograssBar.Config` |
| `UIProsperPopup` | `UIProsperPopup` | `UI.UIProsperPopup.Config` |
| `UIQAWebview` | `UIQAWebview` | `UI.UIAccount2.UIQAWebview.Config` |
| `UIQRScanner` | `UIQRScanner` | `UI.UIQRScanner.Config` |
| `UIQTEView` | `UIQTEView` | `UI.UIQTEView.Config` |
| `UIRedenvelopeEggReceive` | `UIRedenvelopeEggReceive` | `Slg.UI.UIRedenvelope.UIRedenvelopeEggReceive.Config` |
| `UIRedenvelopeRageListPopupView` | `UIRedenvelopeRageListPopupView` | `Slg.UI.UIRedenvelope.UIRedenvelopeRageListPopup.Config` |
| `UIRedenvelopeReceive` | `UIRedenvelopeReceive` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceive.Config` |
| `UIRedenvelopeReceiveInfo` | `UIRedenvelopeReceiveInfo` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveInfo.Config` |
| `UIRedenvelopeReceiveInfoNew` | `UIRedenvelopeReceiveInfoNew` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveInfoNew.Config` |
| `UIRedenvelopeReceiveNew` | `UIRedenvelopeReceiveNew` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveNew.Config` |
| `UIRedenvelopeSend` | `UIRedenvelopeSend` | `Slg.UI.UIRedenvelope.UIRedenvelopeSend.Config` |
| `UIRedenvelopeSend1` | `UIRedenvelopeSend1` | `Slg.UI.UIRedenvelope.UIRedenvelopeSend1.Config` |
| `UIRedenvelopeView` | `UIRedenvelopeView` | `Slg.UI.UIRedenvelope.UIRedenvelopeView.Config` |
| `UIRefundDeductAll` | `UIRefundDeductAll` | `Slg.UI.UICreditMainPanel.RefundDeduct.All.Config` |
| `UIRefundDeductHistory` | `UIRefundDeductHistory` | `Slg.UI.UICreditMainPanel.RefundDeduct.History.Config` |
| `UIRefundDeductTransition` | `UIRefundDeductTransition` | `Slg.UI.UICreditMainPanel.RefundDeduct.Transition.Config` |
| `UIReviewFishHandbook` | `UIReviewFishHandbook` | `Slg.UI.UIReviewFishHandbook.Config` |
| `UIReviewFossilHandbook` | `UIReviewFossilHandbook` | `Slg.UI.UIReviewFossilHandbook.Config` |
| `UIReviewFossilHandbookPreview` | `UIReviewFossilHandbookPreview` | `Slg.UI.UIReviewFossilHandbookPreview.Config` |
| `UIRewardBox` | `UIRewardBox` | `UI.UIRewardBox.Config` |
| `UIRewardLevelUp` | `UIRewardLevelUp` | `UI.UIRewardLevelUp.Config` |
| `UIRewardParkourConfirm` | `UIRewardParkourConfirm` | `UI.UIRewardParkour.UIRewardParkourConfirm.Config` |
| `UIRewardParkourMain` | `UIRewardParkourMain` | `UI.UIRewardParkour.UIRewardParkourMain.Config` |
| `UIRewardVListTip` | `UIRewardVListTip` | `UI.UIRewardVListTip.Config` |
| `UIRocketFailedLanding` | `UIRocketFailedLanding` | `UI.UIRocketFailedLanding.Config` |
| `UIRoleCreate` | `UIRoleCreate` | `UI.UISetting.UIRoleCreate.Config` |
| `UIRoles` | `UIRoles` | `UI.UISetting.UIRoles.Config` |
| `UIRotationNotice` | `UIRotationNotice` | `UI.UIRotationNotice.Config` |
| `UIRuinRecord` | `UIRuinRecord` | `Slg.UI.UIRuinRecord.Config` |
| `UIRuinRewardDetail` | `UIRuinRewardDetail` | `UI.UIRuinRewardDetail.Config` |
| `UIRuinsHistoryRecord` | `UIRuinsHistoryRecord` | `UI.UIRuinsHistoryRecord.Config` |
| `UIRuinsReward` | `UIRuinsReward` | `UI.UIRuinsReward.Config` |
| `UISceneCloud` | `UISceneCloud` | `UI.UISceneCloud.Config` |
| `UISceneNoInput` | `UISceneNoInput` | `UI.UISceneNoInput.Config` |
| `UIScreenCenterTips` | `UIScreenCenterTips` | `UI.UIScreenCenterTips.Config` |
| `UISearch` | `UISearch` | `UI.UISearch.Config` |
| `UISearchLod` | `UISearchLod` | `UI.UISearchLod.Config` |
| `UISelectLevel` | `UISelectLevel` | `UI.UISelectLevel.Config` |
| `UISetAttackTimes` | `UISetAttackTimes` | `UI.UISetAttackTimes.Config` |
| `UISetPlayerNation` | `UISetPlayerNation` | `UI.UISetPlayerNation.Config` |
| `UISetPushNotification` | `UISetPushNotification` | `UI.UISetting.UISetPushNotification.Config` |
| `UISetting` | `UISetting` | `UI.UISetting.UISetting.Config` |
| `UISettingAccount` | `UISettingAccount` | `UI.UIAccount2.UISettingAccount.Config` |
| `UISettingAccount1` | `UISettingAccount1` | `UI.UIAccount2.UISettingAccount1.Config` |
| `UISettingAccount2` | `UISettingAccount2` | `UI.UIAccount2.UISettingAccount2.Config` |
| `UISettingChangeUid` | `UISettingChangeUid` | `UI.UISetting.UISettingChangeUid.Config` |
| `UISettingConsole` | `UISettingConsole` | `UI.UISetting.UISettingConsole.Config` |
| `UISettingDebugReward` | `UISettingDebugReward` | `UI.UISetting.UISettingDebugReward.Config` |
| `UISettingFlag` | `UISettingFlag` | `UI.UISetting.UISettingFlag.Config` |
| `UISettingGameSpeed` | `UISettingGameSpeed` | `UI.UISetting.UISettingGameSpeed.Config` |
| `UISettingLanguage` | `UISettingLanguage` | `UI.UISetting.UISettingLanguage.Config` |
| `UISettingNotice` | `UISettingNotice` | `UI.UISetting.UISettingNotice.Config` |
| `UISettingRedemptionCode` | `UISettingRedemptionCode` | `UI.UISetting.UISettingRedemptionCode.Config` |
| `UISettingSet` | `UISettingSet` | `Slg.UI.UISetting.UISettingSet.Config` |
| `UISettingSoundTest` | `UISettingSoundTest` | `UI.UISetting.UISettingSoundTest.Config` |
| `UISettingTimeControl` | `UISettingTimeControl` | `UI.UISetting.UISettingTimeControl.Config` |
| `UISettingVietCommunityPanel` | `UISettingVietCommunityPanel` | `UI.UISetting.UISettingVietCommunityPanel.Config` |
| `UISevenDay` | `UISevenDay` | `UI.UISevenDay.Config` |
| `UISevenDayNew` | `UISevenDayNew` | `UI.UISevenDayNew.Config` |
| `UISkirmishMain` | `UISkirmishMain` | `-` |
| `UISmallPeopleBook` | `UISmallPeopleBook` | `UI.UIHseroSmallPeople.UISmallPeopleBook.Config` |
| `UISmallPeopleBox` | `UISmallPeopleBox` | `UI.UIHseroSmallPeople.UISmallPeopleBox.Config` |
| `UISmallPeopleFilter` | `UISmallPeopleFilter` | `UI.UIHseroSmallPeople.UISmallPeopleFilter.Config` |
| `UISmallPeopleReplaceConfirm` | `UISmallPeopleReplaceConfirm` | `UI.UIHseroSmallPeople.UISmallPeopleReplaceConfirm.Config` |
| `UISmallPeopleReward` | `UISmallPeopleReward` | `UI.UISmallPeopleReward.Config` |
| `UISmallPeopleSurvivors` | `UISmallPeopleSurvivors` | `UI.UIHseroSmallPeople.UISmallPeopleSurvivors.Config` |
| `UISmallPeopleSurvivorsList` | `UISmallPeopleSurvivorsList` | `UI.UIHseroSmallPeople.UISmallPeopleSurvivorsList.Config` |
| `UISmallPeopleVisit` | `UISmallPeopleVisit` | `UI.UIHseroSmallPeople.UISmallPeopleVisit.Config` |
| `UISnowCountDown` | `UISnowCountDown` | `UI.UISnowCountdown.Config` |
| `UISnowManBubbleTips` | `UISnowManBubbleTips` | `UI.UISnowManBubbleTips.Config` |
| `UISnowManLogs` | `UISnowManLogs` | `UI.UISnowManLogs.Config` |
| `UISoliderGetTip` | `UISoliderGetTip` | `UI.UISoliderGetTip.Config` |
| `UISpearLevelUpNotice` | `UISpearLevelUpNotice` | `UI.UISpear.UISpearLevelUpNotice.Config` |
| `UISpeed` | `UISpeed` | `UI.UISpeed.Config` |
| `UISpeedAutoSelect` | `UISpeedAutoSelect` | `UI.UISpeedAutoSelect.Config` |
| `UISpeedUpConfirm` | `UISpeedUpConfirm` | `UI.UISpeedUpConfirm.Config` |
| `UIStoryHangup` | `UIStoryHangup` | `UI.UIStory.UIStoryHangup.Config` |
| `UIStoryHangupChange` | `UIStoryHangupChange` | `UI.UIStory.UIStoryHangupChange.Config` |
| `UIStorySelectLevel` | `UIStorySelectLevel` | `UI.UIStory.UIStorySelectLevel.Config` |
| `UIStrongCommander` | `UIStrongCommander` | `UI.UIStrongCommanderMain.Config` |
| `UIStrongCommanderPop` | `UIStrongCommanderPop` | `UI.UIStrongCommander.UIStrongCommanderPop.Config` |
| `UIStrongCommanderPre` | `UIStrongCommanderPre` | `UI.UIStrongCommander.UIStrongCommanderPre.Config` |
| `UISubtitle` | `UISubtitle` | `UI.UISubtitle.Config` |
| `UIThanksGivingTurkeyRewardGet` | `UIThanksGivingTurkeyRewardGet` | `Slg.UI.Thanksgiving.TurkeyCook.UIThanksGivingTurkeyRewardGet.Config` |
| `UITimeCompePop` | `UITimeCompePop` | `UI.UITimeCompePop.Config` |
| `UITimelineJump` | `UITimelineJump` | `UI.UITimelineJump.Config` |
| `UITimelineMask` | `UITimelineMask` | `UI.UITimelineMask.Config` |
| `UITimelineMaskNoInput` | `UITimelineMaskNoInput` | `UI.UITimelineMaskNoInput.Config` |
| `UITitleDetail` | `UITitleDetail` | `UI.UITitleDetail.Config` |
| `UITrialDifficultyReward` | `UITrialDifficultyReward` | `UI.UITrialDifficultyReward.Config` |
| `UITurkeyCookDetailsPanel` | `UITurkeyCookDetailsPanel` | `Slg.UI.Thanksgiving.TurkeyCook.UITurkeyCookDetailsPanel.Config` |
| `UIUnLockNewFunc` | `UIUnLockNewFunc` | `-` |
| `UIUnLockSuccess` | `UIUnLockSuccess` | `UI.UIUnLockSuccess.Config` |
| `UIUnlockCompetition` | `UIUnlockCompetition` | `UI.UIUnlockCompetition.Config` |
| `UIUpPower` | `UIUpPower` | `UI.UIUpPower.Config` |
| `UIValentineFoxTeamDynamicPop` | `UIValentineFoxTeamDynamicPop` | `Slg.UI.ValentineNew.UIValentineFoxTeamDynamicPop.Config` |
| `UIValentineFoxTeamSuccessPop` | `UIValentineFoxTeamSuccessPop` | `Slg.UI.ValentineNew.UIValentineFoxTeamSuccessPop.Config` |
| `UIVolcanoAllocableReward` | `UIVolcanoAllocableReward` | `UI.UIVolcanoWar.UIVolcanoAllocableReward.Config` |
| `UIVolcanoCountdown` | `UIVolcanoCountdown` | `UI.UIVolcanoWar.UIVolcanoCountdown.Config` |
| `UIVolcanoDistributionPop` | `UIVolcanoDistributionPop` | `UI.UIVolcanoWar.UIVolcanoDistributionPop.Config` |
| `UIVolcanoEditorAttack` | `UIVolcanoEditorAttack` | `UI.UIVolcanoWar.UIVolcanoEditorAttack.Config` |
| `UIVolcanoMain` | `UIVolcanoMain` | `UI.UIVolcanoWar.UIVolcanoMain.Config` |
| `UIVolcanoPush` | `UIVolcanoPush` | `UI.UIVolcanoWar.UIVolcanoPush.Config` |
| `UIVolcanoReward` | `UIVolcanoReward` | `UI.UIVolcanoWar.VolcanoReward.Config` |
| `UIVolcanoRewardCount` | `UIVolcanoRewardCount` | `UI.UIVolcanoWar.UIVolcanoRewardCount.Config` |
| `UIVolcanoRewardRecord` | `UIVolcanoRewardRecord` | `UI.UIVolcanoWar.UIVolcanoRewardRecord.Config` |
| `UIVolcanoSetAttack` | `UIVolcanoSetAttack` | `UI.UIVolcanoWar.UIVolcanoSetAttack.Config` |
| `UIVolcanoToast` | `UIVolcanoToast` | `UI.UIVolcanoWar.UIVolcanoToast.Config` |
| `UIVolcanoWarCommand` | `UIVolcanoWarCommand` | `UI.UIVolcanoWar.UIVolcanoWarCommand.Config` |
| `UIVolcanoWarCommonder` | `UIVolcanoWarCommonder` | `UI.UIVolcanoWar.UIVolcanoWarCommonder.Config` |
| `UIVolcanoWarInfo` | `UIVolcanoWarInfo` | `UI.UIVolcanoWar.VolcanoWarInfo.Config` |
| `UIVolcanoWarInvitation` | `UIVolcanoWarInvitation` | `UI.UIVolcanoWar.UIVolcanoWarInvitation.Config` |
| `UIVolcanoWarPopupChallenge` | `UIVolcanoWarPopupChallenge` | `UI.UIVolcanoWar.UIVolcanoWarPopupChallenge.Config` |
| `UIVolcanoWarPopupTips` | `UIVolcanoWarPopupTips` | `UI.UIVolcanoWar.UIVolcanoWarPopupTips.Config` |
| `UIVolcanoWarWarZoneList` | `UIVolcanoWarWarZoneList` | `UI.UIVolcanoWar.UIVolcanoWarWarZoneList.Config` |
| `UIWarGuardLog` | `UIWarGuardLog` | `UI.UIWarGuardLog.Config` |
| `UIWoundedCompensate` | `UIWoundedCompensate` | `UI.UIWoundedCompensate.Config` |
| `UI_GetRewardTips` | `UI_GetRewardTips` | `UI.UI_GetRewardTips.Config` |
| `UI_VideoPlayer` | `UI_VideoPlayer` | `UI.UIVideoLayer.Config` |
| `UnlockGirl` | `UnlockGirl` | `UI.SU_UnlockGirl.Config` |
| `UnlockNewFunction` | `UnlockNewFunction` | `UI.SU_UnlockNewFunction.Config` |
| `__cname` | `UIWindowNames` | `UIConfig` |
| `__tostring` | `function: 000001EFDC6212F0` | `-` |

### Daily Tasks & Quests (68 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `AttZombiePuzzleTaskPanel` | `AttZombiePuzzleTaskPanel` | `UI.AttZombiePuzzleTaskPanel.Config` |
| `ChristmasActTask` | `ChristmasActTask` | `Slg.UI.ChristmasAct.ChristmasWood.ChristmasActTask.Config` |
| `DispatchOneKey` | `DispatchOneKey` | `UI.UIActivityCenterTable.Component.DispatchTask.DispatchOneKey.Config` |
| `DispatchRefreshBox` | `DispatchRefreshBox` | `UI.UIActivityCenterTable.Component.DispatchTask.DispatchRefreshBox.Config` |
| `DispatchStealDescBox` | `DispatchStealDescBox` | `UI.UIActivityCenterTable.Component.DispatchTask.DispatchStealDescBox.Config` |
| `UIActMonsterTowerTask` | `UIActMonsterTowerTask` | `UI.UIActMonsterTowerTask.Config` |
| `UIBarterShopNoticeTask` | `UIBarterShopNoticeTask` | `UI.UIBarterShopNoticeTask.Config` |
| `UICarChipGuidePopup` | `UICarChipGuidePopup` | `UI.UICarChipGuidePopup.Config` |
| `UICommonActivityTask` | `UICommonActivityTask` | `UI.UICommonActivityTask.Config` |
| `UICommonGuideTalk` | `UICommonGuideTalk` | `UI.UICommonGuideTalk.Config` |
| `UIDailyActivity` | `UIDailyActivity` | `UI.UIDailyActivity.Config` |
| `UIDailyPackageChangePanel` | `UIDailyPackageChangePanel` | `UI.UIDailyPackageChangePanel.Config` |
| `UIDawnTaskProgressReward` | `UIDawnTaskProgressReward` | `UI.UIDawnTaskProgressReward.Config` |
| `UIDragonExplainSign` | `UIDragonExplainSign` | `UI.UIDragonExplain.Sign.Config` |
| `UIFormationDispatchTask` | `UIFormationDispatchTask` | `UI.UIFormation.UIFormationDispatchTask.Config` |
| `UIGuideArrow` | `UIGuideArrow` | `UI.SU_GuideArrow.Config` |
| `UIGuideArrowNew` | `UIGuideArrowNew` | `UI.SU_GuideArrowNew.Config` |
| `UIGuideCommunicationTalk` | `UIGuideCommunicationTalk` | `UI.UIGuideCommunicationTalk.Config` |
| `UIGuideGarbage` | `UIGuideGarbage` | `UI.UIGuideGarbage.Config` |
| `UIGuideGurtain` | `UIGuideGurtain` | `UI.UIGuideGurtain.Config` |
| `UIGuideHeadTalk` | `UIGuideHeadTalk` | `UI.UIGuideHeadTalk.Config` |
| `UIGuideIntroBubble` | `UIGuideIntroBubble` | `UI.UIGuide.UIGuideIntroBubble.Config` |
| `UIGuideIntroBubble1` | `UIGuideIntroBubble1` | `UI.UIGuide.UIGuideIntroBubble1.Config` |
| `UIGuideLoadMask` | `UIGuideLoadMask` | `UI.UIGuideLoadMask.Config` |
| `UIGuideMoveArrow` | `UIGuideMoveArrow` | `UI.UIGuideMoveArrow.Config` |
| `UIGuideNoNpcTalk` | `UIGuideNoNpcTalk` | `UI.UIGuideNoNpcTalk.Config` |
| `UIGuideShowDogItem` | `UIGuideShowDogItem` | `UI.UIGuideShowDogItem.Config` |
| `UIGuideTalk` | `UIGuideTalk` | `UI.UIGuideTalk.Config` |
| `UIGuideTalk2` | `UIGuideTalk2` | `UI.UIGuideTalk2.Config` |
| `UIGuideTalk3` | `UIGuideTalk3` | `UI.UIGuideTalk3.Config` |
| `UIGuideTalk4` | `UIGuideTalk4` | `UI.UIGuideTalk4.Config` |
| `UIGuideTalk5` | `UIGuideTalk5` | `UI.UIGuideTalk5.Config` |
| `UIGuideTip` | `UIGuideTip` | `UI.UIGuideTip.Config` |
| `UIGuideUnlockMask` | `UIGuideUnlockMask` | `UI.UIGuideUnlockMask.Config` |
| `UIGuideVideo` | `UIGuideVideo` | `UI.UIGuideVideo.Config` |
| `UIHeroBountyTask` | `UIHeroBountyTask` | `UI.UIHeroBountyTask.Config` |
| `UIJeepAdventureTask` | `UIJeepAdventureTask` | `UI.UIJeepAdventure.UIJeepAdventureTask.Config` |
| `UILWDispatchTaskLog` | `UILWDispatchTaskLog` | `UI.UILWDispatchTaskLog.Config` |
| `UILogin` | `UILogin` | `UI.UIAccount.UILogin.Config` |
| `UILoginConfirm` | `UILoginConfirm` | `UI.UIAccount2.UILoginConfirm.Config` |
| `UIMainChapterTask` | `UIMainChapterTask` | `UI.SU_MainChapterTask.Config` |
| `UIMainTask` | `UIMainTask` | `UI.UIMainTask.Config` |
| `UIMusicFestivalGameGuide` | `UIMusicFestivalGameGuide` | `Slg.UI.Oktoberfest.UIMusicFestivalGameGuide.Config` |
| `UIMusicFestivalTask` | `UIMusicFestivalTask` | `Slg.UI.Oktoberfest.UIMusicFestivalTask.Config` |
| `UIRoleLogin` | `UIRoleLogin` | `UI.UISetting.UIRoleLogin.Config` |
| `UIRubyAchievementTitlePopup` | `UIRubyAchievementTitlePopup` | `Slg.UI.UIAchievement.TitlePopup.Config` |
| `UISeason4DinosaurEggHatchMission` | `UISeason4DinosaurEggHatchMission` | `UI.UISeason4DinosaurEggHatchMission.Config` |
| `UISeasonActGuideTips` | `UISeasonActGuideTips` | `UI.UISeasonActGuideTips.Config` |
| `UISeasonBaronessTask` | `UISeasonBaronessTask` | `Slg.UI.UISeason.UISeasonBaronessMain.UISeasonBaronessTask.Config` |
| `UISeasonIceCaveGuide` | `UISeasonIceCaveGuide` | `Slg.UI.UISeason.UISeasonIceCave.UISeasonIceCaveGuide.Config` |
| `UISeasonNightFallsTask` | `UISeasonNightFallsTask` | `UI.UISeason.UISeasonNightFallsTask.Config` |
| `UISevenDayNewGuide` | `UISevenDayNewGuide` | `UI.UISevenDayNewGuide.Config` |
| `UISevenLogin` | `UISevenLogin` | `UI.UISevenLogin.Config` |
| `UISignOfCommand` | `UISignOfCommand` | `UI.BattleCommand.UISignOfCommand.Config` |
| `UISmallPeopleTask` | `UISmallPeopleTask` | `UI.UIHseroSmallPeople.UISmallPeopleTask.Config` |
| `UISmallPeopleTaskDispatch` | `UISmallPeopleTaskDispatch` | `UI.UIHseroSmallPeople.UISmallPeopleTaskDispatch.Config` |
| `UIStrongCommanderTask` | `UIStrongCommanderTask` | `UI.UIStrongCommander.UIStrongCommanderTask.Config` |
| `UITaskPromptTips` | `UITaskPromptTips` | `UI.UITaskPromptTips.Config` |
| `UIThanksgivingStarAchievementView` | `UIThanksgivingStarAchievementView` | `Slg.UI.Thanksgiving.UIThanksgivingStarAchievementView.Config` |
| `UIVIP19Task` | `UIVIP19Task` | `Slg.UI.UIVip.UIVIP19Task.Config` |
| `UIValentineFoxTeamDailyTaskPop` | `UIValentineFoxTeamDailyTaskPop` | `Slg.UI.ValentineNew.UIValentineFoxTeamDailyTaskPop.Config` |
| `UIVolcanoGuideWindow` | `UIVolcanoGuideWindow` | `UI.UIVolcanoWar.UIVolcanoGuideWindow.Config` |
| `UIVolcanoRequestTip` | `UIVolcanoRequestTip` | `UI.UIVolcanoWar.UIVolcanoRequestTip.Config` |
| `UI_DayNight` | `UI_DayNight` | `UI.UIGuide.UI_DayNight.Config` |
| `UI_GuideFullScreenDialog` | `UI_GuideFullScreenDialog` | `UI.UIGuide.UI_GuideFullScreenDialog.Config` |
| `UI_GuideMoviePrologue` | `UI_GuideMoviePrologue` | `UI.UIGuide.UI_GuideMoviePrologue.Config` |
| `UI_PicGuide` | `UI_PicGuide` | `UI.UIGuide.UI_PicGuide.Config` |
| `UI_PicGuideList` | `UI_PicGuideList` | `UI.UIGuide.UI_PicGuideList.Config` |

### Events & Activities (246 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `BarterShopNotice2Stage` | `BarterShopNotice2Stage` | `UI.UIActivityCenterTable.Component.BarterShopNotice.BarterShopNotice2Sta...` |
| `ChristmasActDecorationUseItemPanel` | `ChristmasActDecorationUseItemPanel` | `Slg.UI.ChristmasAct.ChristmasDecoration.ChristmasActDecorationUseItemPan...` |
| `ChristmasActPersonReward` | `ChristmasActPersonReward` | `Slg.UI.ChristmasAct.ChristmasWood.ChristmasActPersonReward.Config` |
| `ChristmasActReward` | `ChristmasActReward` | `Slg.UI.ChristmasAct.ChristmasWood.ChristmasActReward.Config` |
| `ChristmasDecorationRewardGetPanel` | `ChristmasDecorationRewardGetPanel` | `Slg.UI.ChristmasAct.ChristmasDecoration.ChristmasDecorationRewardGetPane...` |
| `ChristmasParkourAnimalTip` | `ChristmasParkourAnimalTip` | `Slg.UI.ChristmasAct.ChristmasParkour.AnimalTip.Config` |
| `ChristmasParkourAttribute` | `ChristmasParkourAttribute` | `Slg.UI.ChristmasAct.ChristmasParkour.Attribute.Config` |
| `ChristmasParkourIdleReward` | `ChristmasParkourIdleReward` | `Slg.UI.ChristmasAct.ChristmasParkour.IdleReward.Config` |
| `ChristmasParkourShop` | `ChristmasParkourShop` | `Slg.UI.ChristmasAct.ChristmasParkour.Shop.Config` |
| `ChristmasShopBuyPanel` | `ChristmasShopBuyPanel` | `Slg.UI.ChristmasAct.ChristmasParkour.ShopBuy.Config` |
| `GivingRoseLevelRewardPanel` | `GivingRoseLevelRewardPanel` | `Slg.UI.UIGivingRosesAct.GivingRoseLevelRewardPanel.Config` |
| `GivingRosesExchange` | `GivingRosesExchange` | `Slg.UI.UIGivingRosesAct.GivingRosesExchange.Config` |
| `HalloweenZombieBossComingPanel` | `HalloweenZombieBossComingPanel` | `Slg.UI.HalloweenAct.HalloweenZombieBossComingPanel.Config` |
| `HeroLevelExchangeConfirmPopup` | `HeroLevelExchangeConfirmPopup` | `UI.ActHeroLevelExchange.HeroLevelExchangeConfirmPopup.Config` |
| `HeroLevelExchangeResult` | `HeroLevelExchangeResult` | `UI.ActHeroLevelExchange.HeroLevelExchangeResult.Config` |
| `HeroLevelExchangeSelectList` | `HeroLevelExchangeSelectList` | `UI.ActHeroLevelExchange.HeroLevelExchangeSelectList.Config` |
| `MonopolyActivityDrawStageReward` | `MonopolyActivityDrawStageReward` | `UI.MonopolyActivity.MonopolyActivityDrawStageReward.Config` |
| `PayPasswordInputPopup` | `PayPasswordInputPopup` | `UI.PayPassword.PayPasswordInputPopup.Config` |
| `SetPayPasswordPopup` | `SetPayPasswordPopup` | `UI.PayPassword.SetPayPasswordPopup.Config` |
| `UIActBossTips` | `UIActBossTips` | `UI.UIActBossTips.Config` |
| `UIActDragonBattleTime` | `UIActDragonBattleTime` | `UI.UIActDragon.UIActDragonBattleTime.Config` |
| `UIActDragonHistory` | `UIActDragonHistory` | `UI.UIActDragon.UIActDragonHistory.Config` |
| `UIActDragonRule` | `UIActDragonRule` | `UI.UIActDragon.UIActDragonRule.Config` |
| `UIActExchangeMainView` | `UIActExchangeMainView` | `Slg.UI.UIActExchange.UIActExchangeMainView.Config` |
| `UIActMonsterTowerDiffTips` | `UIActMonsterTowerDiffTips` | `UI.UIActMonsterTowerDiffTips.Config` |
| `UIActMonsterTowerReward` | `UIActMonsterTowerReward` | `UI.UIActMonsterTowerReward.Config` |
| `UIActivityCenterTable` | `UIActivityCenterTable` | `UI.UIActivityCenterTable.Config` |
| `UIActivityEdenWarTips` | `UIActivityEdenWarTips` | `UI.UIActivityEdenWarTips.Config` |
| `UIActivityNoticeTip` | `UIActivityNoticeTip` | `UI.UIActivityNoticeTip.Config` |
| `UIActivityNoticeTip02` | `UIActivityNoticeTip02` | `UI.UIActivityNoticeTip02.Config` |
| `UIActivityOverview` | `UIActivityOverview` | `UI.UIActivityOverview.Config` |
| `UIActivityRewardTip` | `UIActivityRewardTip` | `UI.UIActivityRewardTip.Config` |
| `UIActivitySummary` | `UIActivitySummary` | `UI.UIActivitySummary.Config` |
| `UIActivitySummaryPreview` | `UIActivitySummaryPreview` | `UI.UIActivitySummaryPreview.Config` |
| `UIActivitySummaryReward` | `UIActivitySummaryReward` | `UI.UIActivitySummaryReward.Config` |
| `UIActivityTip` | `ActivityTip` | `UI.UIActivityTip.Config` |
| `UIBPSelectPack` | `UIBPSelectPack` | `UI.UIBPSelectPack.Config` |
| `UIBattlePassBuy` | `UIBattlePassBuy` | `UI.UIBattlePassBuy.Config` |
| `UIBattlePassGifSeasonPopUp` | `UIBattlePassGifSeasonPopUp` | `Slg.UI.UIBattlePassGifSeasonPopUp.Config` |
| `UIBattlePassPrivilege` | `UIBattlePassPrivilege` | `Slg.UI.UIBattlePassPrivilege.Config` |
| `UIBlindBoxRuleChristmasView` | `UIBlindBoxRuleChristmasView` | `Slg.UI.ChristmasAct.BlindBoxChristmas.UIBlindBoxRuleChristmasView.Config` |
| `UIBlindBoxScoreChristmasView` | `UIBlindBoxScoreChristmasView` | `Slg.UI.ChristmasAct.BlindBoxChristmas.UIBlindBoxScoreChristmasView.Config` |
| `UIBlindBoxSelectBoxChristmasView` | `UIBlindBoxSelectBoxChristmasView` | `Slg.UI.ChristmasAct.BlindBoxChristmas.UIBlindBoxSelectBoxChristmasView.C...` |
| `UICarChipActivityMonsterBossMember` | `UICarChipActivityMonsterBossMember` | `Slg.UI.CarChipActivity.UICarChipActivityMonsterBossMember.Config` |
| `UICarChipActivityMonsterBossReward` | `UICarChipActivityMonsterBossReward` | `Slg.UI.CarChipActivity.UICarChipActivityMonsterBossReward.Config` |
| `UICarChipActivityUpcomingPopup` | `UICarChipActivityUpcomingPopup` | `UI.UICarChipActivityUpcomingPopup.Config` |
| `UICarComponActivityMonsterBossMember` | `UICarComponActivityMonsterBossMember` | `Slg.UI.CarComponActivity.UICarComponActivityMonsterBossMember.Config` |
| `UICarComponActivityMonsterBossReward` | `UICarComponActivityMonsterBossReward` | `Slg.UI.CarComponActivity.UICarComponActivityMonsterBossReward.Config` |
| `UICarComponActivityUpcomingPopup` | `UICarComponActivityUpcomingPopup` | `UI.UICarComponActivityUpcomingPopup.Config` |
| `UICarnivalBulletScreen` | `UICarnivalBulletScreen` | `Slg.UI.UICarnivalBulletScreen.Config` |
| `UICarnivalInfoWorld` | `UICarnivalInfoWorld` | `Slg.UI.UICarnivalInfoWorld.Config` |
| `UICarnivalLuckySpin` | `UICarnivalLuckySpin` | `Slg.UI.UICarnivalLuckySpin.Config` |
| `UICarnivalPreviewPopup` | `UICarnivalPreviewPopup` | `Slg.UI.UICarnivalPreviewPopup.Config` |
| `UICarnivalSendOption` | `UICarnivalSendOption` | `Slg.UI.UICarnivalSendOption.Config` |
| `UICarnivalSendWorld` | `UICarnivalSendWorld` | `Slg.UI.UICarnivalSendWorld.Config` |
| `UICarnivalWorld` | `UICarnivalWorld` | `Slg.UI.UICarnivalWorld.Config` |
| `UIChristmasLevelRewardPanel` | `UIChristmasLevelRewardPanel` | `Slg.UI.ChristmasAct.BlindBoxChristmas.UIChristmasLevelRewardPanel.Config` |
| `UICombatActivityPop` | `UICombatActivityPop` | `UI.UICombatActivityPopView.Config` |
| `UICommonIntroTipActGivingRoses` | `UICommonIntroTipActGivingRoses` | `Slg.UI.UIGivingRosesAct.UICommonIntroTipActGivingRoses.Config` |
| `UICrossWonderAct` | `UICrossWonderAct` | `UI.UICrossWonder.UICrossWonderAct.Config` |
| `UICrossWonderActLog` | `UICrossWonderActLog` | `UI.UICrossWonder.UICrossWonderActLog.Config` |
| `UICrossWonderActRewardPopup` | `UICrossWonderActRewardPopup` | `UI.UICrossWonder.UICrossWonderActRewardPopup.Config` |
| `UIDesertForceList` | `UIDesertForceList` | `UI.UISeason.UIDesertForceList.Config` |
| `UIDetectEvent` | `UIDetectEvent` | `UI.UIRadarCenter.UIDetectEvent.Config` |
| `UIDetectEventLevelUpgrade` | `UIDetectEventLevelUpgrade` | `UI.UIRadarCenter.UIDetectEventLevelUpgrade.Config` |
| `UIDetectEventPowerUpgrade` | `UIDetectEventPowerUpgrade` | `UI.UIRadarCenter.UIDetectEventPowerUpgrade.Config` |
| `UIDetectEventRewardFlyEffect` | `UIDetectEventRewardFlyEffect` | `UI.UIDetectEventRewardFlyEffect.Config` |
| `UIDigLevelReward` | `UIDigLevelReward` | `UI.UIDigLevelReward.Config` |
| `UIDigReward` | `UIDigReward` | `UI.UIDigReward.Config` |
| `UIDragonActionRecord` | `UIDragonActionRecord` | `UI.UIDragonActionRecord.Config` |
| `UIDrakaBoss2Pre` | `UIDrakaBoss2Pre` | `UI.UIActivityCenterTable.Component.UIDrakaBoss2.UIDrakaBoss2Pre.Config` |
| `UIDroppedTreasureTips` | `UIDroppedTreasureTips` | `UI.DroppedTreasure.UIDroppedTreasureTips.Config` |
| `UIExchangeConfirmView` | `UIExchangeConfirmView` | `Slg.UI.UIActExchange.UIExchangeConfirmView.Config` |
| `UIExchangeRecordView` | `UIExchangeRecordView` | `Slg.UI.UIActExchange.UIExchangeRecordView.Config` |
| `UIExchangeView` | `UIExchangeView` | `Slg.UI.UIActExchange.UIExchangeView.Config` |
| `UIFactoryAddTip` | `UIFactoryAddTip` | `UI.UIFactoryAddTip.Config` |
| `UIFishRewardGet` | `UIFishRewardGet` | `Slg.UI.UISeason.UISeasonIceCave.FishReward.Config` |
| `UIFlipFunHelpList` | `UIFlipFunHelpList` | `Slg.UI.UIActFlipFun.UIFlipFunHelpList.Config` |
| `UIFlipFunMainview` | `UIFlipFunMainview` | `Slg.UI.UIActFlipFun.UIFlipFunMainView.Config` |
| `UIFoodFestivalActListPanel` | `UIFoodFestivalActListPanel` | `Slg.UI.UIFoodFestivalActListPanel.Config` |
| `UIFoodFestivalEatExchangeRecordView` | `UIFoodFestivalEatExchangeRecordView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatExchangeRecordView.Config` |
| `UIFoodFestivalEatExchangeView` | `UIFoodFestivalEatExchangeView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatExchangeView.Config` |
| `UIFoodFestivalEatListView` | `UIFoodFestivalEatListView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatListView.Config` |
| `UIFoodFestivalEatNoticeView` | `UIFoodFestivalEatNoticeView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatNoticeView.Config` |
| `UIFoodFestivalEatPreviewTipView` | `UIFoodFestivalEatPreviewTipView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatPreviewTipView.Config` |
| `UIFoodFestivalEatRecordView` | `UIFoodFestivalEatRecordView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatRecordView.Config` |
| `UIFoodFestivalEatReserveView` | `UIFoodFestivalEatReserveView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatReserveView.Config` |
| `UIFoodFestivalEatRuleView` | `UIFoodFestivalEatRuleView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatRuleView.Config` |
| `UIFoodFestivalEatSelfRecordView` | `UIFoodFestivalEatSelfRecordView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatSelfRecordView.Config` |
| `UIFoodFestivalEatTableTipView` | `UIFoodFestivalEatTableTipView` | `Slg.UI.FoodFestivalEat.UIFoodFestivalEatTableTipView.Config` |
| `UIForgetPassword` | `UIForgetPassword` | `UI.UIAccount2.UIForgetPassword.Config` |
| `UIFrozenLandIntroduce` | `UIFrozenLandIntroduce` | `UI.FrozenLandActivity.UIFrozenLandIntroduce.Config` |
| `UIFrozenLandPreview` | `UIFrozenLandPreview` | `UI.FrozenLandActivity.UIFrozenLandPreview.Config` |
| `UIGivingRoseShare` | `UIGivingRoseShare` | `Slg.UI.UIGivingRosesAct.UIGivingRoseShare.Config` |
| `UIGivingRoses2ExchangeShopBuy` | `UIGivingRoses2ExchangeShopBuy` | `Slg.UI.ValentineAct.UIGivingRoses2ExchangeShopBuy.Config` |
| `UIGivingRoses2FlowerHistory` | `UIGivingRoses2FlowerHistory` | `Slg.UI.ValentineAct.UIGivingRoses2FlowerHistory.Config` |
| `UIGivingRoses2FlowerRewardGet` | `UIGivingRoses2FlowerRewardGet` | `Slg.UI.ValentineAct.UIGivingRoses2FlowerRewardGet.Config` |
| `UIGivingRoses2FlowerSelectPlayerPanel` | `UIGivingRoses2FlowerSelectPlayerPanel` | `Slg.UI.ValentineAct.UIGivingRoses2FlowerSelectPlayerPanel.Config` |
| `UIGivingRoses2PockerGet` | `UIGivingRoses2PockerGet` | `Slg.UI.ValentineAct.UIGivingRoses2PockerGet.Config` |
| `UIGivingRoses2PockerPreview` | `UIGivingRoses2PockerPreview` | `Slg.UI.ValentineAct.UIGivingRoses2PockerPreview.Config` |
| `UIGivingRoses2PockerShow` | `UIGivingRoses2PockerShow` | `Slg.UI.ValentineAct.UIGivingRoses2PockerShow.Config` |
| `UIGivingRoses2RewardAndRewardPanel` | `UIGivingRoses2RewardAndRewardPanel` | `Slg.UI.ValentineAct.UIGivingRoses2RewardAndRewardPanel.Config` |
| `UIGivingRosesActListPanel` | `UIGivingRosesActListPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesActListPanel.Config` |
| `UIGivingRosesExchangeShopBuy` | `UIGivingRosesExchangeShopBuy` | `Slg.UI.UIGivingRosesAct.UIGivingRosesExchangeShopBuy.Config` |
| `UIGivingRosesHistoryPanel` | `UIGivingRosesHistoryPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesHistoryPanel.Config` |
| `UIGivingRosesMyHistoryPanel` | `UIGivingRosesMyHistoryPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesMyHistoryPanel.Config` |
| `UIGivingRosesRewardPanel` | `UIGivingRosesRewardPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesRewardPanel.Config` |
| `UIGivingRosesSearchResultPanel` | `UIGivingRosesSearchResultPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesSearchResultPanel.Config` |
| `UIGivingRosesSelectPlayerPanel` | `UIGivingRosesSelectPlayerPanel` | `Slg.UI.UIGivingRosesAct.UIGivingRosesSelectPlayerPanel.Config` |
| `UIGivingRosesWindow` | `UIGivingRosesWindow` | `Slg.UI.UIGivingRosesAct.UIGivingRosesWindow.Config` |
| `UIGroundPassUnlock` | `UIGroundPassUnlock` | `UI.UIGroundPass.UIGroundPassUnlock.Config` |
| `UIHalloween2026PassBuyPop` | `UIHalloween2026PassBuyPop` | `Slg.UI.HalloweenMarble.UIHalloween2026Pass.UIHalloween2026PassBuyPopConfig` |
| `UIHalloweenCommonIntroPanel` | `UIHalloweenCommonIntroPanel` | `Slg.UI.HalloweenAct.UIHalloweenCommonIntroPanel.Config` |
| `UIHalloweenExchangeShopBuyPanel` | `UIHalloweenExchangeShopBuyPanel` | `Slg.UI.HalloweenAct.UIHalloweenExchangeShopBuyPanel.Config` |
| `UIHalloweenLevelReward` | `UIHalloweenLevelReward` | `Slg.UI.HalloweenAct.UIHalloweenLevelReward.Config` |
| `UIHalloweenPopTip` | `UIHalloweenPopTip` | `Slg.UI.HalloweenAct.UIHalloweenPopTip.Config` |
| `UIHalloweenRewardGet` | `UIHalloweenRewardGet` | `Slg.UI.HalloweenAct.UIHalloweenRewardGet.Config` |
| `UIHalloweenRewardTip` | `UIHalloweenRewardTip` | `Slg.UI.HalloweenAct.UIHalloweenRewardTip.Config` |
| `UIHeroBattlePassPop` | `UIHeroBattlePassPop` | `UI.UIHeroBattlePassPop.Config` |
| `UIHeroEquipReplace` | `UIHeroEquipReplace` | `UI.UIHeroEquipReplace.Config` |
| `UIHitTurkeyGameMsgBox` | `UIHitTurkeyGameMsgBox` | `UI.UIActivityCenterTable.Component.ThanksGiving.HitTurkeyGameMsgBox.Config` |
| `UIHitTurkeyNotice` | `UIHitTurkeyNotice` | `UI.UIActivityCenterTable.Component.ThanksGiving.HitTurkeyNotice.Config` |
| `UIHitTurkeyOperate` | `UIHitTurkeyOperate` | `UI.UIActivityCenterTable.Component.ThanksGiving.HitTurkeyOperate.Config` |
| `UIMigrateActTips` | `UIMigrateActTips` | `Slg.UI.UIMigrate.UIMigrateActTips.Config` |
| `UIModifyPassword` | `UIModifyPassword` | `UI.UIAccount2.UIModifyPassword.Config` |
| `UIMonthCardPopup` | `UIMonthCardPopup` | `Slg.UI.MonthCardActivity.UIMonthCardPopup.Config` |
| `UIMonthMsgPass` | `UIMonthMsgPass` | `UI.UIMonthMsgPass.Config` |
| `UIMusicFestivalGameGrade` | `UIMusicFestivalGameGrade` | `Slg.UI.Oktoberfest.UIMusicFestivalGameGrade.Config` |
| `UIMusicFestivalGameScene` | `UIMusicFestivalGameScene` | `Slg.UI.Oktoberfest.UIMusicFestivalGameScene.Config` |
| `UIMusicFestivalRulesScore` | `UIMusicFestivalRulesScore` | `Slg.UI.Oktoberfest.UIMusicFestivalRulesScore.Config` |
| `UINoticeGivingRoseTips` | `UINoticeGivingRoseTips` | `Slg.UI.UIGivingRosesAct.UINoticeGivingRoseTips.Config` |
| `UINoticeValentineFoxTips` | `UINoticeValentineFoxTips` | `Slg.UI.UIGivingRosesAct.UINoticeValentineFoxTips.Config` |
| `UIOneClickSweepReport` | `UIOneClickSweepReport` | `Slg.UI.OneClickSweep.Report.Config` |
| `UIPayPasswordCodeInput` | `UIPayPasswordCodeInput` | `-` |
| `UIPersonalArmsConvert` | `UIPersonalArmsConvert` | `UI.UIPersonalArmsConvert.Config` |
| `UIPersonalArmsProbability` | `UIPersonalArmsProbability` | `UI.UIPersonalArmsProbability.Config` |
| `UIPersonalArmsReward` | `UIPersonalArmsReward` | `UI.UIPersonalArmsReward.Config` |
| `UIPersonalArmsScore` | `UIPersonalArmsScore` | `UI.UIPersonalArmsScore.Config` |
| `UIPlayerMarketEarnPopup` | `UIPlayerMarketEarnPopup` | `Slg.UI.FestivalAct.Act.PlayerMarket.MarketEarnPopup.Config` |
| `UIPlayerMarketRpsPopup` | `UIPlayerMarketRpsPopup` | `Slg.UI.FestivalAct.Act.PlayerMarket.MarketRpsPopup.Config` |
| `UIPlayerMarketSellPopup` | `UIPlayerMarketSellPopup` | `Slg.UI.FestivalAct.Act.PlayerMarket.MarketSellPopup.Config` |
| `UIPreviewMineCave` | `UIPreviewMineCave` | `UI.UIActivityCenterTable.Component.MineCave.PreviewMineCave.Config` |
| `UIPuzzleMonsterCreate` | `UIPuzzleMonsterCreate` | `UI.UIPuzzleMonster.UIPuzzleMonsterCreate.Config` |
| `UIPuzzleMonsterList` | `UIPuzzleMonsterList` | `UI.UIPuzzleMonster.UIPuzzleMonsterList.Config` |
| `UIPveActMain` | `UIPveActMain` | `UI.UIPveAct.UIPveActMain.Config` |
| `UIRedEquipmentActivityUpcomingPopup` | `UIRedEquipmentActivityUpcomingPopup` | `UI.UIRedEquipmentActivityUpcomingPopup.Config` |
| `UIRedenvelopeSelectView` | `UIRedenvelopeSelectView` | `UI.UIActivityCenterTable.Component.RedEnvelope.RedEnvelopeSelect.Config` |
| `UIRedenvelopeSuccess` | `UIRedenvelopeSuccess` | `UI.UIActivityCenterTable.Component.RedEnvelope.RedEnvelopeSuccess.Config` |
| `UISeason4DinosaurBossPreview` | `UISeason4DinosaurBossPreview` | `UI.DinosaurBoss.UISeason4DinosaurBossPreview.Config` |
| `UISeason4DinosaurBossShow` | `UISeason4DinosaurBossShow` | `UI.DinosaurBoss.UISeason4DinosaurBossShow.Config` |
| `UISeason4DinosaurEggHatchConfirm` | `UISeason4DinosaurEggHatchConfirm` | `UI.UISeason4DinosaurEggHatchConfirm.Config` |
| `UISeason4DinosaurEggHatchCutto` | `UISeason4DinosaurEggHatchCutto` | `UI.UISeason4DinosaurEggHatchCutto.Config` |
| `UISeason4DinosaurEggHatchLog` | `UISeason4DinosaurEggHatchLog` | `UI.UISeason4DinosaurEggHatchLog.Config` |
| `UISeason4FossilCollection` | `UISeason4FossilCollection` | `UI.UISeason4FossilCollection.Config` |
| `UISeason4FossilCollectionConvert` | `UISeason4FossilCollectionConvert` | `UI.UISeason4FossilCollectionConvert.Config` |
| `UISeason4FossilCollectionObtain` | `UISeason4FossilCollectionObtain` | `UI.UISeason4FossilCollectionObtain.Config` |
| `UISeasonBaronessInfoS5` | `UISeasonBaronessInfoS5` | `Slg.UI.UISeason.UISeasonBaronessMain.UISeasonBaronessInfoS5.Config` |
| `UISeasonBaronessPushS5` | `UISeasonBaronessPushS5` | `Slg.UI.UISeason.UISeasonBaronessMain.UISeasonBaronessPushS5.Config` |
| `UISeasonEarlDonatePopS5` | `UISeasonEarlDonatePopS5` | `Slg.UI.UISeason.UISeasonBaronessMain.UISeasonEarlDonatePopS5.Config` |
| `UISeasonEntrance` | `UISeasonEntrance` | `UI.UISeasonEntrance.Config` |
| `UISeasonForceLackView` | `UISeasonForceLackView` | `UI.UISeason.UISeasonForceLackView.Config` |
| `UISeasonForceList` | `UISeasonForceList` | `Slg.UI.UISeason.UISeasonForceList.Config` |
| `UISeasonForceReward` | `UISeasonForceReward` | `Slg.UI.UISeason.UISeasonForceReward.Config` |
| `UISeasonForceRewardDetail` | `UISeasonForceRewardDetail` | `UI.UISeason.UISeasonForceRewardDetail.Config` |
| `UISeasonForceStageReward` | `UISeasonForceStageReward` | `UI.UISeason.UISeasonForceStageReward.Config` |
| `UISeasonForceStageReward01` | `UISeasonForceStageReward01` | `UI.UISeason.UISeasonForceStageReward01.Config` |
| `UISeasonForceTitleUnlock` | `UISeasonForceTitleUnlock` | `UI.UISeasonForceTitleUnlock.Config` |
| `UISeasonGloryDeclareEndPopup` | `UISeasonGloryDeclareEndPopup` | `UI.UISeasonGloryDeclareEndPopup.Config` |
| `UISeasonGloryGroup` | `UISeasonGloryGroup` | `Slg.UI.UISeason.UISeasonGloryGroup.Config` |
| `UISeasonGloryGroupS3` | `UISeasonGloryGroupS3` | `Slg.UI.UISeason.UISeasonGloryGroup.S3.Config` |
| `UISeasonGloryGroupS4` | `UISeasonGloryGroupS4` | `Slg.UI.UISeason.UISeasonGloryGroup.S4.Config` |
| `UISeasonGloryGroupS5` | `UISeasonGloryGroupS5` | `Slg.UI.UISeason.UISeasonGloryGroup.S5.Config` |
| `UISeasonGloryRecord` | `UISeasonGloryRecord` | `Slg.UI.UISeason.UISeasonGloryRecord.Config` |
| `UISeasonGloryReward` | `UISeasonGloryReward` | `Slg.UI.UISeason.UISeasonGloryReward.Config.S2.Config` |
| `UISeasonGloryRewardAllot` | `UISeasonGloryRewardAllot` | `Slg.UI.UISeason.UISeasonGloryRewardAllot.Config.S2.Config` |
| `UISeasonGloryRewardAllotS3` | `UISeasonGloryRewardAllotS3` | `Slg.UI.UISeason.UISeasonGloryRewardAllot.Config.S3.Config` |
| `UISeasonGloryRewardAllotS4` | `UISeasonGloryRewardAllotS4` | `Slg.UI.UISeason.UISeasonGloryRewardAllot.Config.S4.Config` |
| `UISeasonGloryRewardAllotS5` | `UISeasonGloryRewardAllotS5` | `Slg.UI.UISeason.UISeasonGloryRewardAllot.Config.S5.Config` |
| `UISeasonGloryRewardS3` | `UISeasonGloryRewardS3` | `Slg.UI.UISeason.UISeasonGloryReward.Config.S3.Config` |
| `UISeasonGloryRewardS4` | `UISeasonGloryRewardS4` | `Slg.UI.UISeason.UISeasonGloryReward.Config.S4.Config` |
| `UISeasonGloryRewardS5` | `UISeasonGloryRewardS5` | `Slg.UI.UISeason.UISeasonGloryReward.Config.S5.Config` |
| `UISeasonGloryRule` | `UISeasonGloryRule` | `Slg.UI.UISeason.UISeasonGloryRule.Config` |
| `UISeasonGlorySelectMember` | `UISeasonGlorySelectMember` | `Slg.UI.UISeason.UISeasonGlorySelectMember.Config` |
| `UISeasonGlorySelectMemberS3` | `UISeasonGlorySelectMemberS3` | `Slg.UI.UISeason.UISeasonGlorySelectMember.S3.Config` |
| `UISeasonGlorySelectMemberS4` | `UISeasonGlorySelectMemberS4` | `Slg.UI.UISeason.UISeasonGlorySelectMember.S4.Config` |
| `UISeasonGlorySelectMemberS5` | `UISeasonGlorySelectMemberS5` | `Slg.UI.UISeason.UISeasonGlorySelectMember.S5.Config` |
| `UISeasonGlorySweep` | `UISeasonGlorySweep` | `Slg.UI.UISeason.UISeasonGlorySweep.Config` |
| `UISeasonGrading` | `UISeasonGrading` | `UI.UISeason.UISeasonGrading.Config` |
| `UISeasonGradingS3` | `UISeasonGradingS3` | `UI.UISeason.UISeasonGrading.S3.Config` |
| `UISeasonGradingS4` | `UISeasonGradingS4` | `UI.UISeason.UISeasonGrading.S4.Config` |
| `UISeasonGradingS5` | `UISeasonGradingS5` | `UI.UISeason.UISeasonGrading.S5.Config` |
| `UISeasonGroundManage` | `UISeasonGroundManage` | `Slg.UI.UISeason.UISeasonGroundManage.Config` |
| `UISeasonGroundManageS3` | `UISeasonGroundManageS3` | `Slg.UI.UISeason.UISeasonGroundManageS3.Config` |
| `UISeasonGroundManageS4` | `UISeasonGroundManageS4` | `Slg.UI.UISeason.UISeasonGroundManageS3.S4.Config` |
| `UISeasonGroundManageS5` | `UISeasonGroundManageS5` | `Slg.UI.UISeason.UISeasonGroundManageS3.S5.Config` |
| `UISeasonHeroPreview` | `UISeasonHeroPreview` | `UI.UISeasonHeroPreview.Config` |
| `UISeasonHint` | `UISeasonHint` | `UI.UISeasonHint.Config` |
| `UISeasonIceCaveCandidate` | `UISeasonIceCaveCandidate` | `Slg.UI.UISeason.UISeasonIceCave.Candidate.Config` |
| `UISeasonIceCaveInfoPanel` | `UISeasonIceCaveInfoPanel` | `Slg.UI.UISeason.UISeasonIceCave.UISeasonIceCaveInfoPanel.Config` |
| `UISeasonIceCaveInfoPop` | `UISeasonIceCaveInfoPop` | `Slg.UI.UISeason.UISeasonIceCave.UISeasonIceCaveInfoPop.Config` |
| `UISeasonIceCaveLog` | `UISeasonIceCaveLog` | `Slg.UI.UISeason.UISeasonIceCave.UISeasonIceCaveLog.Config` |
| `UISeasonIceCaveRecord` | `UISeasonIceCaveRecord` | `Slg.UI.UISeason.UISeasonIceCave.Record.Config` |
| `UISeasonIntro` | `UISeasonIntro` | `-` |
| `UISeasonMoonlightAttrPreviewS5` | `UISeasonMoonlightAttrPreviewS5` | `UI.Moonlight.UISeasonMoonlightAttrPreviewS5.Config` |
| `UISeasonMoonlightAttrS5` | `UISeasonMoonlightAttrS5` | `UI.Moonlight.UISeasonMoonlightAttrS5.Config` |
| `UISeasonMoonlightGetS5` | `UISeasonMoonlightGetS5` | `UI.Moonlight.UISeasonMoonlightGetS5.Config` |
| `UISeasonMoonlightLevelUpS5` | `UISeasonMoonlightLevelUpS5` | `UI.Moonlight.UISeasonMoonlightLevelUpS5.Config` |
| `UISeasonMoonlightLogS5` | `UISeasonMoonlightLogS5` | `UI.Moonlight.UISeasonMoonlightLogS5.Config` |
| `UISeasonMoonlightRuleS5` | `UISeasonMoonlightRuleS5` | `UI.Moonlight.UISeasonMoonlightRuleS5.Config` |
| `UISeasonMoonlightSelectS5` | `UISeasonMoonlightSelectS5` | `UI.Moonlight.UISeasonMoonlightSelectS5.Config` |
| `UISeasonMoonlightSummonResultS5` | `UISeasonMoonlightSummonResultS5` | `UI.Moonlight.UISeasonMoonlightSummonResultS5.Config` |
| `UISeasonMultExchange` | `UISeasonMultExchange` | `Slg.UI.UISeason.UISeasonMultExchange.Config` |
| `UISeasonNightFallsClockS5` | `UISeasonNightFallsClockS5` | `UI.UISeasonNightFallsClockS5.Config` |
| `UISeasonNightFallsComing` | `UISeasonNightFallsComing` | `UI.UISeason.UISeasonNightFallsComing.Config` |
| `UISeasonNightFallsRule` | `UISeasonNightFallsRule` | `UI.UISeasonNightFallsRule.Config` |
| `UISeasonNightSacrificePushS5` | `UISeasonNightSacrificePushS5` | `UI.NightSacrifice.UISeasonNightSacrificePushS5.Config` |
| `UISeasonReview` | `UISeasonReview` | `Slg.UI.UISeasonReview.Config` |
| `UISeasonReviewRecord` | `UISeasonReviewRecord` | `Slg.UI.UISeasonReviewRecord.Config` |
| `UISeasonReviewRule` | `UISeasonReviewRule` | `Slg.UI.UISeasonReviewRule.Config` |
| `UISeasonTradePostInfoView` | `UISeasonTradePostInfoView` | `Slg.UI.UISeason.UISeasonTradePost.Info.Config` |
| `UISeasonTradePostInfoViewS5` | `UISeasonTradePostInfoViewS5` | `Slg.UI.UISeason.UISeasonTradePostS5.Info.Config` |
| `UISeasonTradePostLogView` | `UISeasonTradePostLogView` | `Slg.UI.UISeason.UISeasonTradePost.Log.Config` |
| `UISeasonTradePostLogViewS5` | `UISeasonTradePostLogViewS5` | `Slg.UI.UISeason.UISeasonTradePostS5.Log.Config` |
| `UISeasonTradePostRecord` | `UISeasonTradePostRecord` | `Slg.UI.UISeason.UISeasonTradePost.Record.Config` |
| `UISeasonTradePostRecordS5` | `UISeasonTradePostRecordS5` | `Slg.UI.UISeason.UISeasonTradePostS5.Record.Config` |
| `UISeasonTradePostStore` | `UISeasonTradePostStore` | `Slg.UI.UISeason.UISeasonTradePost.Store.Config` |
| `UISeasonTradePostStoreS5` | `UISeasonTradePostStoreS5` | `Slg.UI.UISeason.UISeasonTradePostS5.Store.Config` |
| `UISeasonViewReward` | `UISeasonViewReward` | `UI.UISeason.UISeasonViewReward.Config` |
| `UISeasonWeek` | `UISeasonWeek` | `Slg.UI.UISeasonWeek.Config` |
| `UISelectDigFinalReward` | `UISelectDigFinalReward` | `UI.UISelectDigFinalReward.Config` |
| `UIStrongCommanderRewardGivingRoses` | `UIStrongCommanderRewardGivingRoses` | `Slg.UI.UIGivingRosesAct.UIStrongCommanderRewardGivingRoses.Config` |
| `UITrainPrepare` | `UITrainPrepare` | `UI.UILWRailway.UITrainPrepare.Config` |
| `UITreasureHuntBigRewardSelect` | `UITreasureHuntBigRewardSelect` | `-` |
| `UITreasureHuntShop` | `UITreasureHuntShop` | `-` |
| `UITreasureHuntTips` | `UITreasureHuntTips` | `-` |
| `UIValentineEventPop` | `UIValentineEventPop` | `Slg.UI.ValentineNew.UIValentineEventPop.Config` |
| `UIValentinePassBuyPop` | `UIValentinePassBuyPop` | `Slg.UI.ValentineNew.UIValentineFoxPass.UIValentinePassBuyPopConfig` |
| `UIWebPush` | `UIWebPush` | `UI.UIWebPush.Config` |
| `UIWeekendChallengeCarGetAche` | `UIWeekendChallengeCarGetAche` | `UI.UIActivityCenterTable.Component.WeekendChallengeCar.UIWeekendChalleng...` |
| `UIWeekendChallengeCarResult` | `UIWeekendChallengCareResult` | `UI.UIActivityCenterTable.Component.WeekendChallengeCar.UIWeekendChalleng...` |
| `UIWeekendChallengeCarReward` | `UIWeekendChallengeCarReward` | `UI.UIActivityCenterTable.Component.WeekendChallengeCar.UIWeekendChalleng...` |
| `UIWeekendChallengeResult` | `UIWeekendChallengeResult` | `UI.UIActivityCenterTable.Component.WeekendChallenge.UIWeekendChallengeRe...` |
| `UIWeekendChallengeReward` | `UIWeekendChallengeReward` | `UI.UIActivityCenterTable.Component.WeekendChallenge.UIWeekendChallengeRe...` |
| `UiChrsitmasExchangeShopBuyPanel` | `UiChrsitmasExchangeShopBuyPanel` | `Slg.UI.ChristmasAct.UiChrsitmasExchangeShopBuyPanel.Config` |
| `WeekendChallengeCarStageReward` | `WeekendChallengeCarStageReward` | `UI.UIActivityCenterTable.Component.WeekendChallengeCar.WeekendChallengeC...` |
| `WeekendChallengeStageReward` | `WeekendChallengeStageReward` | `UI.UIActivityCenterTable.Component.WeekendChallenge.WeekendChallengeStag...` |

### Formations, Marches & World Map (98 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `CastleAdventureExchangeMapRecord` | `CastleAdventureExchangeMapRecord` | `Slg.UI.CastleAdventure.CastleAdventureExchangeMapRecord.Config` |
| `CastleAdventureMap` | `CastleAdventureMap` | `Slg.UI.CastleAdventure.CastleAdventureMap.Config` |
| `CastleAdventureMapReward` | `CastleAdventureMapReward` | `Slg.UI.CastleAdventure.CastleAdventureMapReward.Config` |
| `LWCountBattleMap` | `LWCountBattleMap` | `-` |
| `UIArmyTips` | `UIArmyTips` | `UI.UIFormation.UIArmyTips.Config` |
| `UIBookMarkPositionCollect` | `UIBookMarkPositionCollect` | `UI.UIBookMarkPositionCollect.Config` |
| `UICarChipFormationPopup` | `UICarChipFormationPopup` | `UI.UICarChipFormationPopup.Config` |
| `UIChampionBattleFormation` | `UIChampionBattleFormation` | `Slg.UI.UIChampionBattleView.UIChampionBattleFormationView.Config` |
| `UICollectReward` | `UICollectReward` | `UI.UICollectReward.Config` |
| `UICrossWonderCollect` | `UICrossWonderCollect` | `UI.UICrossWonderCollect.Config` |
| `UIDemonHunterMapPointTips` | `UIDemonHunterMapPointTips` | `UI.DemonHunter.UIDemonHunterMapPointTips.Config` |
| `UIEnterDragonWorld` | `UIEnterDragonWorld` | `UI.UIEnterDragonWorld.Config` |
| `UIFormationAddStamina` | `UIFormationAddStamina` | `UI.UIFormation.UIFormationAddStamina.Config` |
| `UIFormationAssistance` | `UIFormationAssistance` | `UI.UIFormationAssistance.Config` |
| `UIFormationBuff` | `UIFormationBuff` | `UI.UIFormationBuff.Config` |
| `UIFormationBuffInfo` | `UIFormationBuffInfo` | `UI.UIFormationBuffInfo.Config` |
| `UIFormationDispatchTip` | `UIFormationDispatchTip` | `UI.UIFormation.UIFormationDispatchTip.Config` |
| `UIFormationLackPower` | `UIFormationLackPower` | `UI.UIFormationLackPower.Config` |
| `UIFormationRestraint` | `UIFormationRestraint` | `UI.UIFormation.UIFormationRestraint.Config` |
| `UIFormationSelectListNew` | `UIFormationSelectListNew` | `UI.UIFormation.UIFormationSelectListNew.Config` |
| `UIFormationShare` | `UIFormationShare` | `UI.UIFormationShare.Config` |
| `UIFormationSoldierChoose` | `UIFormationSoldierChoose` | `UI.UIFormation.UIFormationSoldierChoose.Config` |
| `UIFormationState` | `UIFormationState` | `UI.UIFormation.UIFormationState.Config` |
| `UIFormationTableNew` | `UIFormationTableNew` | `UI.UIFormation.UIFormationTableNew2.Config` |
| `UIFormationTip` | `UIFormationTip` | `UI.UIFormation.UIFormationTip.Config` |
| `UIHeroCampRestraint` | `UIHeroCampRestraint` | `UI.UIFormation.UIHeroCampRestraint.Config` |
| `UIHotNewsPointDetail` | `UIHotNewsPointDetail` | `UI.UIHotNewsPointDetail.Config` |
| `UILoMap` | `UILoMap` | `UI.UILandingOperation.UILOMap.Config` |
| `UIMainMapLaunch` | `UIMainMapLaunch` | `UI.UIMainMapLaunch.Config` |
| `UIMainMapPointCell` | `UIMainMapPointCell` | `UI.UIMainMapPoint.Config` |
| `UIMainMiniMap` | `UIMainMiniMap` | `UI.UIMainMiniMap.Config` |
| `UIMarchCancelDragMsgBar` | `UIMarchCancelDragMsgBar` | `UI.UIMarchCancelDragMsgBar.Config` |
| `UIMineCaveCross` | `UIMineCaveCross` | `UI.UIMineCaveCross.Config` |
| `UIMineCaveCrossTip` | `UIMineCaveCrossTip` | `UI.UIMineCaveCrossTip.Config` |
| `UIMineCaveLog` | `UIMineCaveLog` | `UI.UIMineCaveLog.Config` |
| `UIMineCavePopNotice` | `UIMineCavePopNotice` | `UI.UIMineCavePopNotice.Config` |
| `UIMineCaveScoreTip` | `UIMineCaveScoreTip` | `UI.UIMineCaveScoreTip.Config` |
| `UIMineCaveTips` | `UIMineCaveTips` | `UI.UIMineCaveTips.Config` |
| `UIMineCaveUnlock` | `UIMineCaveUnlock` | `UI.UIMineCaveUnlock.Config` |
| `UIMineCountTipsPanel` | `UIMineCountTipsPanel` | `UI.UIMinePlunder.UIMineCountTipsPanel.Config` |
| `UIMinePlunderCrossPanel` | `UIMinePlunderCrossPanel` | `UI.UIMinePlunder.UIMinePlunderCrossPanel.Config` |
| `UIMinePlunderDispatch` | `UIMinePlunderDispatch` | `UI.UIMinePlunder.UIMinePlunderDispatch.Config` |
| `UIMineTips` | `UIMineTips` | `UI.UIMinePlunder.UIMineTipsPanel.Config` |
| `UIMoreInformation` | `UIMoreInformation` | `Slg.UI.UIMoreInformation.Config` |
| `UIParkourFormation` | `UIParkourFormation` | `UI.UIParkour.FormationUI.Config` |
| `UIParkourMap` | `UIParkourMap` | `UI.UIParkour.MapUI.Config` |
| `UIPointOrigin` | `UIPointOrigin` | `UI.UIPointOrigin.Config` |
| `UIPositionAppointSearch` | `UIPositionAppointSearch` | `UI.UIGovernment.UIPositionAppointSearch.Config` |
| `UIPresidentAppoint` | `UIPresidentAppoint` | `UI.UIGovernment.UIPresidentAppoint.Config` |
| `UIRedenvelopeReceiveInfoCarWorld` | `UIRedenvelopeReceiveInfoCarWorld` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveInfoCarWorld.Config` |
| `UIRedenvelopeReceiveInfoWorld` | `UIRedenvelopeReceiveInfoWorld` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveInfoWorld.Config` |
| `UIRedenvelopeReceiveWorld` | `UIRedenvelopeReceiveWorld` | `Slg.UI.UIRedenvelope.UIRedenvelopeReceiveWorld.Config` |
| `UIRedenvelopeSendWorld` | `UIRedenvelopeSendWorld` | `Slg.UI.UIRedenvelope.UIRedenvelopeSendWorld.Config` |
| `UIRuinsRewardPreview` | `UIRuinsRewardPreview` | `UI.WorldSiege.UIRuinsRewardPreview.Config` |
| `UISUWorldCollect` | `UISUWorldCollect` | `UI.UISUWorldCollect.Config` |
| `UISettingPointsReward` | `UISettingPointsReward` | `UI.UISettingPointsReward.Config` |
| `UISpearWorldPoint` | `UISpearWorldPoint` | `Slg.UI.UISpearWorldPoint.Config` |
| `UIVolcanoMoveRule` | `UIVolcanoMoveRule` | `UI.UIVolcanoWar.UIVolcanoMoveRule.Config` |
| `UIWorldBattleNews` | `UIWorldBattleNews` | `UI.UIWorldBattleNews.Config` |
| `UIWorldBossTroop` | `UIWorldBossTroop` | `UI.UIWorldBossTroop.Config` |
| `UIWorldBuff` | `UIWorldBuff` | `Slg.UI.World.UIWorldBuff.Config` |
| `UIWorldCollectMessageTip` | `UIWorldCollectMessageTip` | `UI.UIWorldCollect.UIWorldCollectMessageTip.Config` |
| `UIWorldCupExchangeShopBuy` | `UIWorldCupExchangeShopBuy` | `Slg.UI.WorldCup.UIWorldCupExchangeShopBuyPanel.Config` |
| `UIWorldCupMatchDiscussionPanel` | `UIWorldCupMatchDiscussionPanel` | `Slg.UI.WorldCup.UIWorldCupMatchDiscussionPanel.Config` |
| `UIWorldCupPredictionConfirmPopup` | `UIWorldCupPredictionConfirmPopup` | `Slg.UI.WorldCup.UIWorldCupPredictionConfirmPopup.Config` |
| `UIWorldCupRecommendedMatchPopup` | `UIWorldCupRecommendedMatchPopup` | `Slg.UI.WorldCup.UIWorldCupRecommendedMatchPopup.Config` |
| `UIWorldCupRewardGet` | `UIWorldCupRewardGet` | `Slg.UI.WorldCup.UIWorldCupRewardGet.Config` |
| `UIWorldCupStreakSuccessPopup` | `UIWorldCupStreakSuccessPopup` | `Slg.UI.WorldCup.UIWorldCupStreakSuccessPopup.Config` |
| `UIWorldCupUserMatchSharePopup` | `UIWorldCupUserMatchSharePopup` | `Slg.UI.WorldCup.UIWorldCupUserMatchSharePopup.Config` |
| `UIWorldCupZombieIntroPanel` | `UIWorldCupZombieIntroPanel` | `Slg.UI.WorldCup.UIWorldCupZombieIntroPanel.Config` |
| `UIWorldCupZombieLevelReward` | `UIWorldCupZombieLevelReward` | `Slg.UI.WorldCup.WorldCupZombieLevelRewardPanel.Config` |
| `UIWorldCupZombiePopTip` | `UIWorldCupZombiePopTip` | `Slg.UI.WorldCup.UIWorldCupZombiePopTip.Config` |
| `UIWorldCupZombieRewardTip` | `UIWorldCupZombieRewardTip` | `Slg.UI.WorldCup.UIWorldCupZombieRewardTip.Config` |
| `UIWorldDeclareList` | `UIWorldDeclareList` | `UI.UIWorldDeclareList.Config` |
| `UIWorldDeclareWar` | `UIWorldDeclareWar` | `UI.UIWorldDeclareWar.Config` |
| `UIWorldDeclareWarConditionList` | `UIWorldDeclareWarConditionList` | `UI.UIWorldDeclareWarConditionList.Config` |
| `UIWorldDeclareWarInfo` | `UIWorldDeclareWarInfo` | `UI.UIWorldDeclareWarInfo.Config` |
| `UIWorldDeclareWarRe` | `UIWorldDeclareWarRe` | `UI.UIWorldDeclareWarRe.Config` |
| `UIWorldExplorePointUI` | `UIWorldExplorePointUI` | `UI.UIWorldExplorePointUI.Config` |
| `UIWorldFortPoint` | `UIWorldFortPoint` | `UI.UIWorldFortPoint.Config` |
| `UIWorldGarbagePointUI` | `UIWorldGarbagePointUI` | `UI.UIWorldGarbage.Config` |
| `UIWorldMarchDetail` | `UIWorldMarchDetail` | `UI.UIWorldMarchDetail.Config` |
| `UIWorldMultiSelect` | `UIWorldMultiSelect` | `UI.UIWorldMultiSelect.Config` |
| `UIWorldNewsAbbrDetail` | `UIWorldNewsAbbrDetail` | `UI.UIWorldNewsAbbrDetail.Config` |
| `UIWorldNewsTips` | `UIWorldNewsTips` | `UI.UIWorldNewsTips.Config` |
| `UIWorldNoSelectable` | `UIWorldNoSelectable` | `UI.UIWorldNoSelectable.Config` |
| `UIWorldOccupyFirst` | `UIWorldOccupyFirst` | `UI.UIWorldOccupyFirst.Config` |
| `UIWorldOccupyMessageBar` | `UIWorldOccupyMessageBar` | `UI.UIWorldOccupyMessageBar.Config` |
| `UIWorldPoint` | `UIWorldPoint` | `Slg.UI.UIWorldPoint.Config` |
| `UIWorldReminderTips` | `UIWorldReminderTips` | `UI.UIWorldReminder.Config` |
| `UIWorldResistanceTips` | `UIWorldResistanceTips` | `UI.UIWorldResistanceTips.Config` |
| `UIWorldRuinsPopUp` | `UIWorldRuinsPopUp` | `UI.UIWorldRuinsPopUp.Config` |
| `UIWorldSamplePointUI` | `UIWorldSamplePointUI` | `UI.UIWorldSamplePointUI.Config` |
| `UIWorldShoutTips` | `UIWorldShoutTips` | `UI.UIWorldShoutTips.Config` |
| `UIWorldSiegePoint` | `UIWorldSiegePoint` | `Slg.UI.UIWorldSiegePoint.Config` |
| `UIWorldTileUI` | `UIWorldTileUI` | `UI.SU_UIWorldTileUI.Config` |
| `WorldCupZombieBossComingPanel` | `WorldCupZombieBossComingPanel` | `Slg.UI.WorldCup.WorldCupZombieBossComingPanel.Config` |
| `WorldDesUI` | `WorldDesUI` | `-` |

### Garage, Vehicles & Chips (38 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `UIAircraftComponInfo` | `UIAircraftComponInfo` | `UI.UIAircraftComponInfo.Config` |
| `UIAircraftComponMerge` | `UIAircraftComponMerge` | `UI.UIAircraftComponMerge.Config` |
| `UIAircraftComponPartPanel` | `UIAircraftComponPartPanel` | `UI.UIAircraftComponPartPanel.Config` |
| `UIAircraftComponPartTip` | `UIAircraftComponPartTip` | `UI.UIAircraftComponPartTip.Config` |
| `UIAircraftComponPreviewPanel` | `UIAircraftComponPreviewPanel` | `UI.UIAircraftComponPreviewPanel.Config` |
| `UIAircraftMainComponentTips` | `UIAircraftMainComponentTips` | `UI.UIAircraftMain_ComponentTips.Config` |
| `UIBarrelCarFightTip` | `UIBarrelCarFightTip` | `UI.UIParkour.UIBarrelHeroFightTip.CarConfig` |
| `UICarChipBag` | `UICarChipBag` | `UI.UICarChipBag.Config` |
| `UICarChipBox` | `UICarChipBox` | `UI.UICarChipBoxPopup.Config` |
| `UICarChipDetailPopup` | `UICarChipDetailPopup` | `UI.UICarChipDetailPopup.Config` |
| `UICarChipGradingPopup` | `UICarChipGradingPopup` | `UI.UICarChipGradingPopup.Config` |
| `UICarChipGradingUpgradePopup` | `UICarChipGradingUpgradePopup` | `UI.UICarChipGradingUpgradePopup.Config` |
| `UICarChipHandbookPopup` | `UICarChipHandbookPopup` | `UI.UICarChipHandbookPopup.Config` |
| `UICarChipItemProbability` | `UICarChipItemProbability` | `UI.UICarChipItemProbability.Config` |
| `UICarChipMainTips` | `UICarChipMainTips` | `UI.UICarChipMainTips.Config` |
| `UICarChipResetPopup` | `UICarChipResetPopup` | `UI.UICarChipResetPopup.Config` |
| `UICarChipSelectCampPopup` | `UICarChipSelectCampPopup` | `UI.UICarChipSelectCampPopup.Config` |
| `UICarChipSelectCampVX` | `UICarChipSelectCampVX` | `UI.UICarChipSelectCampVX.Config` |
| `UICarChipSelectChipPopup` | `UICarChipSelectChipPopup` | `UI.UICarChipSelectChipPopup.Config` |
| `UICarChipStarLevelUpPopup` | `UICarChipStarLevelUpPopup` | `UI.UICarChipStarLevelUpPopup.Config` |
| `UICarChipUpgradePopup` | `UICarChipUpgradePopup` | `UI.UICarChipUpgradePopup.Config` |
| `UICarParkourSelect` | `UICarParkourSelect` | `UI.UIPVE.UICarParkour.UICarParkourSelect.Config` |
| `UICarParkourWarning` | `UICarParkourWarning` | `UI.UIPVE.UICarParkour.UICarParkourWarning.Config` |
| `UIChampionBattleCard` | `UIChampionBattleCard` | `UI.UIChampionBattleCard.Config` |
| `UIChoseHeroMonthCard` | `UIChoseHeroMonthCard` | `UI.UIChoseHeroMonthCard.Config` |
| `UIChoseWeekCard` | `UIChoseWeekCard` | `UI.UIChoseWeekCard.Config` |
| `UIGarageRefit` | `UIGarageRefit` | `-` |
| `UIGolloesCardsExShop` | `UIGolloesCardsExShop` | `UI.UIGolloesCardsExShop.Config` |
| `UIGolloesCardsRP` | `UIGolloesCardsRP` | `UI.UIGolloesCardsRP.Config` |
| `UIGolloesMonthCard` | `UIGolloesMonthCard` | `UI.UIGolloesMonthCard.Config` |
| `UIGolloesMonthCardPopUp` | `UIGolloesMonthCardPopUp` | `UI.UIGolloesMonthCardPopUp.Config` |
| `UIHalloweenDrawCardView` | `UIHalloweenDrawCardView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawCardView.Config` |
| `UIHalloweenMarbleCardReward` | `UIHalloweenMarbleCardReward` | `Slg.UI.HalloweenMarble.UIHalloweenMarbleCardRewardConfig` |
| `UIHeroMonthCard` | `UIHeroMonthCard` | `UI.UIHeroMonthCard.Config` |
| `UIIDCardAgeTips` | `UIIDCardAgeTips` | `UI.UIIDCardAgeTips.Config` |
| `UIIDCardAuthenticate` | `UIIDCardAuthenticate` | `UI.UIIDCardAuthenticate.Config` |
| `UIIDCardDesTips` | `UIIDCardDesTips` | `UI.UIIDCardDesTips.Config` |
| `UIMedalGetCar` | `UIMedalGetCar` | `UI.UIMedalGetCar.Config` |

### Heroes, Skills & Equipment (106 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `SU_NewHero` | `SU_NewHero` | `UI.UIHero2.SU_NewHero.Config` |
| `UIAircraftPreviewSkillWindow` | `UIAircraftPreviewSkillWindow` | `UI.UIAircraftPreviewSkillWindow.Config` |
| `UIAircraftSkillTip` | `UIAircraftSkillTip` | `UI.UIAircraftSkillTip.Config` |
| `UIAssistanceHeroSelect` | `UIAssistanceHeroSelect` | `UI.UIAssistanceHeroSelect.Config` |
| `UIAssistanceHeroSettle` | `UIAssistanceHeroSettle` | `UI.UIAssistanceHeroSettle.Config` |
| `UIAssistanceHeroShareConfirm` | `UIAssistanceHeroShareConfirm` | `UI.UIAssistanceHeroShareConfirm.Config` |
| `UIBarrelHeroFightTip` | `UIBarrelHeroFightTip` | `UI.UIParkour.UIBarrelHeroFightTip.Config` |
| `UICampPveHeroInfo` | `UICampPveHeroInfo` | `Slg.UI.UICampPveHeroInfo.Config` |
| `UICrossWormHero` | `UICrossWormHero` | `-` |
| `UIEquipBreakSkillTip` | `UIEquipBreakSkillTip` | `UI.UIHero2.UIEquipBreakSkillTip.Config` |
| `UIFiveStarFeedBack` | `UIFiveStarFeedBack` | `UI.UIFiveStarFeedBack.Config` |
| `UIFiveStarGet` | `UIFiveStarGet` | `UI.SU_FiveStarGet.Config` |
| `UIGetDress` | `UIGetDress` | `UI.UIHero2.UIHeroDress.UIGetDress.Config` |
| `UIHeroBag` | `UIHeroBag` | `UI.UIHero2.UIHeroBag.Config` |
| `UIHeroBeyond` | `UIHeroBeyond` | `UI.UIHero2.UIHeroBeyond.Config` |
| `UIHeroBountyMain` | `UIHeroBountyMain` | `UI.UIHeroBountyMain.Config` |
| `UIHeroBreak` | `UIHeroBreak` | `UI.UIHero2.UIHeroBreak.Config` |
| `UIHeroBreakSuccess` | `UIHeroBreakSuccess` | `UI.UIHero2.UIHeroBreakSuccess.Config` |
| `UIHeroChangeTalentName` | `UIHeroChangeTalentName` | `-` |
| `UIHeroDebrisExchange` | `UIHeroDebrisExchange` | `UI.UIHero2.UIHeroDebrisExchange.Config` |
| `UIHeroDecompose` | `UIHeroDecompose` | `UI.UIHero2.UIHeroDecompose.Config` |
| `UIHeroDecomposeBatch` | `UIHeroDecomposeBatch` | `UI.UIHero2.UIHeroDecomposeBatch.Config` |
| `UIHeroDetailTips` | `UIHeroDetailTips` | `UI.UIHeroDetailTips.Config` |
| `UIHeroDressFilter` | `UIHeroDressFilter` | `UI.UIHero2.UIHeroDress.UIHeroDressFilter.Config` |
| `UIHeroDressList` | `UIHeroDressList` | `UI.UIHero2.UIHeroDress.UIHeroDressList.Config` |
| `UIHeroEffectSkillTips` | `UIHeroEffectSkillTips` | `UI.UIHeroEffectSkillTips.Config` |
| `UIHeroEffectSkillTipsBackground` | `UIHeroEffectSkillTipsBackground` | `UI.UIHeroEffectSkillTips.ConfigBackground` |
| `UIHeroEntrust` | `UIHeroEntrust` | `UI.UIHeroEntrust.Config` |
| `UIHeroEquip` | `UIHeroEquip` | `UI.UIHeroEquip.Config` |
| `UIHeroEquipEvolutionSuccess` | `UIHeroEquipEvolutionSuccess` | `UI.UIHeroEquipEvolutionSuccess.Config` |
| `UIHeroEquipForgeMain` | `UIHeroEquipForgeMain` | `UI.UIHeroEquipForgeMain.Config` |
| `UIHeroEquipForgePreview` | `UIHeroEquipForgePreview` | `UI.UIHeroEquipForgePreview.Config` |
| `UIHeroEquipForgingSuccessful` | `UIHeroEquipForgingSuccessful` | `UI.UIHeroEquipForgingSuccessful.Config` |
| `UIHeroEquipInfo` | `UIHeroEquipInfo` | `UI.UIHeroEquipInfo.Config` |
| `UIHeroEquipPromotion` | `UIHeroEquipPromotion` | `UI.UIHeroEquipPromotion.Config` |
| `UIHeroEquipPromotionSelect` | `UIHeroEquipPromotionSelect` | `UI.UIHeroEquipPromotionSelect.Config` |
| `UIHeroEquipReset` | `UIHeroEquipReset` | `Slg.UI.UIHeroEquipReset.Config` |
| `UIHeroEquipStrength` | `UIHeroEquipStrength` | `UI.UIHeroEquipStrength.Config` |
| `UIHeroEquipTips` | `UIHeroEquipTips` | `UI.UIHeroEquipTips.Config` |
| `UIHeroExchange` | `UIHeroExchange` | `UI.UIHeroExchange.Config` |
| `UIHeroInfo` | `UIHeroInfo` | `UI.UIHero2.UIHeroInfo.Config` |
| `UIHeroInfoEquipInfoNew` | `UIHeroInfoEquipInfoNew` | `UI.UIHeroInfoEquipInfoNew.Config` |
| `UIHeroInfoPageSkin` | `UIHeroInfoPageSkin` | `UI.UIHero2.UIHeroInfoPageSkin.Config` |
| `UIHeroIntensify` | `UIHeroIntensify` | `UI.UIHeroIntensify.Config` |
| `UIHeroIntensifyInfo` | `UIHeroIntensifyInfo` | `UI.UIHeroIntensifyInfo.Config` |
| `UIHeroIntensifyTip` | `UIHeroIntensifyTip` | `UI.UIHeroIntensifyTip.Config` |
| `UIHeroJigsawReward` | `UIHeroJigsawReward` | `UI.UIHero2.UIHeroJigsawReward.Config` |
| `UIHeroLackTips` | `UIHeroLackTips` | `UI.UIHeroLackTips.Config` |
| `UIHeroLevelUseExp` | `UIHeroLevelUseExp` | `-` |
| `UIHeroList` | `UIHeroList` | `UI.UIHero2.SU_UIHeroList.Config` |
| `UIHeroLvUp` | `UIHeroLvUp` | `UI.UIHero2.UIHeroLvUp.Config` |
| `UIHeroMedalExchange` | `UIHeroMedalExchange` | `UI.UIHero2.UIHeroMedalExchange.Config` |
| `UIHeroMilitaryAdvanceSuccess` | `UIHeroMilitaryAdvanceSuccess` | `UI.UIHero2.UIHeroMilitaryAdvanceSuccess.Config` |
| `UIHeroPosterExchangeMain` | `UIHeroPosterExchangeMain` | `UI.UIHero2.UIHeroPosterExchangeMain.Config` |
| `UIHeroPosterExchangePop` | `UIHeroPosterExchangePop` | `UI.UIHero2.UIHeroPosterExchangePop.Config` |
| `UIHeroPreviewSkillWindow` | `UIHeroPreviewSkillWindow` | `UI.UIHero2.UIHeroPreviewSkillWindow.Config` |
| `UIHeroRecruit` | `UIHeroRecruit` | `UI.UIHero2.UIHeroRecruit.Config` |
| `UIHeroRecruitChangeCamp` | `UIHeroRecruitChangeCamp` | `UI.UIHero2.UIHeroRecruitChangeCamp.Config` |
| `UIHeroRecruitReward` | `UIHeroRecruitReward` | `UI.UIHero2.UIHeroRecruitReward.Config` |
| `UIHeroRecruitTip` | `UIHeroRecruitTip` | `UI.UIHero2.UIHeroRecruitTip.Config` |
| `UIHeroResetShop` | `UIHeroResetShop` | `UI.UIHeroResetShop.Config` |
| `UIHeroResetSuccess` | `UIHeroResetSuccess` | `UI.UIHero2.UIHeroResetSuccess.Config` |
| `UIHeroSPEquip` | `UIHeroSPEquip` | `UI.UIHeroSPEquip.Config` |
| `UIHeroSPEquipSuccess` | `UIHeroSPEquipSuccess` | `UI.UIHeroSPEquipSuccess.Config` |
| `UIHeroSkillAdvance` | `UIHeroSkillAdvance` | `UI.UIHero2.UIHeroSkillAdvance.Config` |
| `UIHeroSkillAdvanceSuccess` | `UIHeroSkillAdvanceSuccess` | `UI.UIHero2.UIHeroSkillAdvanceSuccess.Config` |
| `UIHeroSkillTip` | `UIHeroSkillTip` | `UI.UIHero2.UIHeroSkillTip.Config` |
| `UIHeroSkillUpgrade` | `UIHeroSkillUpgrade` | `UI.UIHero2.UIHeroSkillUpgrade.Config` |
| `UIHeroSkillUpgradeSuccess` | `UIHeroSkillUpgradeSuccess` | `UI.UIHero2.UIHeroSkillUpgradeSuccess.Config` |
| `UIHeroSkinUseItem` | `UIHeroSkinUseItem` | `UI.UIHero2.UIHeroSkinUseItem.Config` |
| `UIHeroTalent` | `UIHeroTalent` | `-` |
| `UIHeroTalentUseItem` | `UIHeroTalentUseItem` | `-` |
| `UIHeroTip` | `UIHeroTip` | `UI.UIHero2.UIHeroTip.Config` |
| `UIHeroTips` | `UIHeroTips` | `UI.UIHeroTips.Config` |
| `UIHeroTips2` | `UIHeroTips2` | `UI.UIHeroTips2.Config` |
| `UIHeroTrialMain` | `HeroTrialMain` | `-` |
| `UIHeroTrialReward` | `HeroTrialReward` | `UI.UIHeroTrialReward.Config` |
| `UIItemHeroBreakTips` | `UIItemHeroBreakTips` | `UI.SU_HeroBreakTips.Config` |
| `UIItemHeroEquipBreakTips` | `UIItemHeroEquipBreakTips` | `UI.SU_ItemHeroEquipBreakTips.Config` |
| `UIItemHeroSkinTips` | `UIItemHeroSkinTips` | `UI.SU_ItemHeroSkinTips.Config` |
| `UILuckyRollHeroExchangeShop` | `UILuckyRollHeroExchangeShop` | `-` |
| `UILuckyRollHeroExchangeShopBuy` | `UILuckyRollHeroExchangeShopBuy` | `-` |
| `UILuckyRollHeroPop` | `UILuckyRollHeroPop` | `UI.UILuckyRollHeroPop.Config` |
| `UILuckyRollHeroRewardPreview` | `UILuckyRollHeroRewardPreview` | `UI.UILuckyRollHeroRewardPreview.Config` |
| `UILuckyRollHeroTip` | `UILuckyRollHeroTip` | `-` |
| `UIMasterySkill` | `UIMasterySkill` | `UI.UIMasterySkill.Config` |
| `UIMasterySkillIntro` | `UIMasterySkillIntro` | `-` |
| `UIMasterySkillUse` | `UIMasterySkillUse` | `UI.UIMasterySkillUse.Config` |
| `UIMasterySkillUseResultShow` | `UIMasterySkillUseResultShow` | `UI.UIMasterySkillUseResultShow.Config` |
| `UINewHero` | `UINewHero` | `UI.UIHero2.UINewHero.Config` |
| `UINoticeEquipTips` | `UINoticeEquipTips` | `UI.UINoticeEquipTips.Config` |
| `UINoticeHeroTips` | `UINoticeHeroTips` | `UI.UINoticeHeroTips.Config` |
| `UIOverlordSkillTipPopup` | `UIOverlordSkillTipPopup` | `UI.Overlord.UIOverlordSkillTipPopup.Config` |
| `UIOverlordStarLevelUpPopup` | `UIOverlordStarLevelUpPopup` | `UI.Overlord.UIOverlordStarLevelUpPopup.Config` |
| `UIPVEHeroBossFightStart` | `UIPVEHeroBossFightStart` | `UI.UIPVE.UIPVEHeroBossFightStart.Config` |
| `UIRecruitLotteryTip` | `UIRecruitLotteryTip` | `UI.UIHero2.UIRecruitLotteryTip.Config` |
| `UIShowFakeNewHero` | `UIShowFakeNewHero` | `UI.UIShowFakeNewHero.Config` |
| `UISkinChoiceChest` | `UISkinChoiceChest` | `UI.UISkinChoiceChest.Config` |
| `UISkinChoiceChestHero` | `UISkinChoiceChestHero` | `UI.UISkinChoiceChestHero.Config` |
| `UISkinShop` | `UISkinShop` | `UI.UISkinShop.Config` |
| `UISpearPreviewSkillWindow` | `UISpearPreviewSkillWindow` | `UI.UISpear.UISpearPreviewSkillWindow.Config` |
| `UIThanksgivingStarListView` | `UIThanksgivingStarListView` | `Slg.UI.Thanksgiving.UIThanksgivingStarListView.Config` |
| `UIThanksgivingStarRewardView` | `UIThanksgivingStarRewardView` | `Slg.UI.Thanksgiving.UIThanksgivingStarRewardView.Config` |
| `UIThanksgivingStarScoreView` | `UIThanksgivingStarScoreView` | `Slg.UI.Thanksgiving.UIThanksgivingStarScoreView.Config` |
| `UIVIPPopupSkinInfo` | `UIVIPPopupSkinInfo` | `Slg.UI.UIVip.UIVIPPopupSkinInfo.Config` |
| `UnlockNewSkill` | `UnlockNewSkill` | `UI.SU_UnlockNewSkill.Config` |

### Items, Bag, Shops & Economy (102 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `CastleAdventureExchange` | `CastleAdventureExchange` | `Slg.UI.CastleAdventure.CastleAdventureExchange.Config` |
| `CastleAdventureExchangeFrageComfirm` | `CastleAdventureExchangeFrageComfirm` | `Slg.UI.CastleAdventure.CastleAdventureExchangeFrageComfirm.Config` |
| `CastleAdventureShopBuy` | `CastleAdventureShopBuy` | `Slg.UI.CastleAdventure.CastleAdventureShopBuy.Config` |
| `ShowItemTips` | `ShowItemTips` | `UI.SU_ShowItemTips.Config` |
| `ThanksGivingExchangeShopBuyPanel` | `ThanksGivingExchangeShopBuyPanel` | `Slg.UI.Thanksgiving.TurkeyCook.ThanksGivingExchangeShopBuyPanel.Config` |
| `TurkeyCookResultPanel` | `TurkeyCookResultPanel` | `Slg.UI.Thanksgiving.TurkeyCook.TurkeyCookResultPanel.Config` |
| `UIBagPickUp` | `UIBagPickUp` | `UI.UIBagPickUp.Config` |
| `UIBagPropStatis` | `UIBagPropStatis` | `UI.UIBagPropStatis.Config` |
| `UIBagSplit` | `UIBagSplit` | `UI.UIBagSplit.Config` |
| `UIBagUpgrade` | `UIBagUpgrade` | `UI.UIBagUpgrade.Config` |
| `UIBagView` | `UIBagView` | `UI.UIBagView.Config` |
| `UIBaubleExchange` | `UIBaubleExchange` | `UI.UIBauble.UIBaubleExchange.Config` |
| `UIBlindBoxShopView` | `UIBlindBoxShopView` | `Slg.UI.Oktoberfest.BlindBox.UIBlindBoxShopView.Config` |
| `UIChainPay` | `UIChainPay` | `UI.UIChainPay.Config` |
| `UIChainPayHalloween` | `UIChainPayHalloween` | `UI.UIChainPayHalloween.Config` |
| `UIChampionBattleResultHintView` | `UIChampionBattleResultHintView` | `UI.UIChampionBattleView.UIChampionBattleResultHintView.Config` |
| `UIChristmasParkourResult` | `UIChristmasParkourResult` | `UI.UIPVE.UIChristmasParkourResult.Config` |
| `UICommonBuyItem` | `UICommonBuyItem` | `UI.UICommonBuyItem.Config` |
| `UICommonItemProbability` | `UICommonItemProbability` | `UI.UICommonItemProbability.Config` |
| `UICommonItemProbabilityNew` | `UICommonItemProbabilityNew` | `UI.UICommonItemProbabilityNew.Config` |
| `UICommonResourceComfirmView` | `UICommonResourceComfirmView` | `Slg.UI.UICommonResourceComfirm.Config` |
| `UICommonShop` | `UICommonShop` | `UI.UICommonShop.Config` |
| `UICommonUseItemTip` | `UICommonUseItemTip` | `UI.UICommonUseItemTip.Config` |
| `UICommonUseResItemTips` | `UICommonUseResItemTips` | `UI.UICommonUseResItemTips.Config` |
| `UIConsumeItem` | `UIConsumeItem` | `UI.UIConsumeItem.Config` |
| `UICrossWormItemList` | `UICrossWormItemList` | `-` |
| `UICycleBoxExchangeView` | `UICycleBoxExchangeView` | `Slg.UI.CycleBox.UICycleBoxExchangeView.Config` |
| `UIDetectNpcDinosaurRescue` | `UIDetectNpcDinosaurRescue` | `UI.UIDetectNpcDinosaurRescue.Config` |
| `UIDownloadProgress` | `UIDownloadProgress` | `UI.UIDownloadProgress.Config` |
| `UIDragonBattleResult` | `UIDragonBattleResult` | `UI.UIDragonBattleResult.Config` |
| `UIDrakeBossUseItem` | `UIDrakeBossUseItem` | `UI.UIDrakeBossUseItem.Config` |
| `UIEasterExchangeShopBuy` | `UIEasterExchangeShopBuy` | `Slg.UI.Easter.UiEasterExchangeShopBuyPanel.Config` |
| `UIFirstPay` | `UIFirstPay` | `UI.UIFirstPay.Config` |
| `UIFirstPayNew` | `UIFirstPayNew` | `UI.UIFirstPayNew.Config` |
| `UIFirstPayNewNvJing` | `UIFirstPayNewNvJing` | `UI.UIFirstPayNewNvJing.Config` |
| `UIGarbageRewardShow` | `UIGarbageRewardShow` | `UI.UIGarbageRewardShow.Config` |
| `UIGoldInsufficientPopup` | `UIGoldInsufficientPopup` | `UI.UIGoldInsufficientPopup.Config` |
| `UIGolloesTraderRecord` | `UIGolloesTraderRecord` | `UI.UIGolloesTraderRecord.Config` |
| `UIGroceryStore` | `UIGroceryStore` | `UI.UIGroceryStore.Config` |
| `UIHalloweenDrawLotteryResultView` | `UIHalloweenDrawLotteryResultView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawLotteryResultView.Config` |
| `UIHalloweenDrawResultView` | `UIHalloweenDrawResultView` | `Slg.UI.UIHalloweenDraw.UIHalloweenDrawResultView.Config` |
| `UIHalloweenNewExchangeShopBuy` | `UIHalloweenNewExchangeShopBuy` | `Slg.UI.HalloweenMarble.UIHalloweenNewExchangeShopBuyPanel.Config` |
| `UIItemBaubleTip` | `UIItemBaubleTip` | `UI.UIItemBaubleTip.Config` |
| `UIItemPurchases` | `UIItemPurchases` | `UI.UIItemPurchases.Config` |
| `UIItemTips` | `UIItemTips` | `UI.SU_ItemTips.Config` |
| `UIItemTips02` | `UIItemTips02` | `UI.SU_ItemTips02.Config` |
| `UILOResult` | `UILOResult` | `UI.UILandingOperation.UILOResult.Config` |
| `UILOShop` | `UILOShop` | `UI.UILandingOperation.UILOShop.Config` |
| `UILeagueMatchResult` | `UILeagueMatchResult` | `UI.LeagueMatch.UILeagueMatchResult.Config` |
| `UILuckyShopPreview` | `UILuckyShopPreview` | `UI.UILuckyShopPreview.Config` |
| `UILuckyShopProgressReward` | `UILuckyShopProgressReward` | `UI.UILuckyShopProgressReward.Config` |
| `UIMasterySelectRes` | `UIMasterySelectRes` | `UI.UIMasterySelectRes.Config` |
| `UIMultiBuy` | `UIMultiBuy` | `UI.UIMultiBuy.Config` |
| `UINewNvJingBuyResult` | `UINewNvJingBuyResult` | `UI.UIFirstPayNewNvJing.SubView.Config` |
| `UIPVEResult` | `UIPVEResult` | `UI.UIPVE.UIPVEResult.Config` |
| `UIPVEShop` | `UIPVEShop` | `UI.UIPVE.UIPVEShop.Config` |
| `UIPackageContentTip` | `UIPackageContentTip` | `UI.UIPackageContentTip.Config` |
| `UIPhonographPayment` | `UIPhonographPayment` | `UI.UIPhonograp.UIPhonographPayment.Config` |
| `UIPopupPackage` | `UIPopupPackage` | `UI.UIPopupPackage.Config` |
| `UIRefundDeductGold` | `UIRefundDeductGold` | `Slg.UI.UICreditMainPanel.RefundDeduct.Gold.Config` |
| `UIRefundDeductItem` | `UIRefundDeductItem` | `Slg.UI.UICreditMainPanel.RefundDeduct.Item.Config` |
| `UIResSupport` | `UIResSupport` | `UI.UIResSupport.Config` |
| `UIResidentOrder` | `UIResidentOrder` | `-` |
| `UIResourceBag` | `UIResourceBag` | `UI.UIResourceBag.Config` |
| `UIResourceCost` | `UIResourceCost` | `UI.UIResourceCost.Config` |
| `UIResourceExchange` | `UIResourceExchange` | `UI.UIResourceExchange.Config` |
| `UIResourceGetTip` | `UIResourceGetTip` | `UI.UIResourceGetTip.Config` |
| `UIResourceItemLack` | `UIResourceItemLack` | `UI.UIResourceItemLack.Config` |
| `UIResourceLack` | `UIResourceLack` | `UI.UIResourceLack.Config` |
| `UIResourceLackNew` | `UIResourceLackNew` | `UI.UIResourceLackNew.Config` |
| `UIResourceLackNew1` | `UIResourceLackNew1` | `UI.UIResourceLackNew1.Config` |
| `UIResourceLackNew2` | `UIResourceLackNew2` | `UI.UIResourceLackNew2.Config` |
| `UIResourceReplenish` | `UIResourceReplenish` | `UI.UIResourceReplenish.Config` |
| `UIResourceReport` | `UIResourceReport` | `UI.UIResourceReport.Config` |
| `UIRewardParkourResult` | `UIRewardParkourResult` | `UI.UIRewardParkour.UIRewardParkourResult.Config` |
| `UIRubyStore` | `UIRubyStore` | `-` |
| `UIScrollPack` | `UIScrollPack` | `UI.UIScrollPack.Config` |
| `UIScrollPackNew` | `UIScrollPackNew` | `UI.UIScrollPackNew.Config` |
| `UISellConfirm` | `UISellConfirm` | `UI.UISellConfirm.Config` |
| `UISkirmishResult` | `UISkirmishResult` | `-` |
| `UIStorageShop` | `UIStorageShop` | `UI.UIStorageShop.Config` |
| `UIStorageShopHistory` | `UIStorageShopHistory` | `UI.UIStorageShopHistory.Config` |
| `UIStorageShopList` | `UIStorageShopList` | `UI.UIStorageShopList.Config` |
| `UIStorageShopMain` | `UIStorageShopMain` | `UI.UIStorageShopMain.Config` |
| `UIStorageShopRetrieve` | `UIStorageShopRetrieve` | `UI.UIStorageShopRetrieve.Config` |
| `UIStorageShopRetrieveNew` | `UIStorageShopRetrieveNew` | `UI.UIStorageShopRetrieveNew.Config` |
| `UIStorageShopSelect` | `UIStorageShopSelect` | `UI.UIStorageShopSelect.Config` |
| `UIStoryResult` | `UIStoryResult` | `UI.UIStory.UIStoryResult.Config` |
| `UIThirdPaymentInfo` | `UIThirdPaymentInfo` | `UI.UIThirdPaymentInfo.Config` |
| `UIThirdPaymentShop` | `UIThirdPaymentShop` | `UI.UIThirdPaymentShop.Config` |
| `UIThirdPaymentShopPop` | `UIThirdPaymentShopPop` | `UI.UIThirdPaymentShopPop.Config` |
| `UITradeCenter` | `UITradeCenter` | `UI.UITradeCenter.Config` |
| `UITriggerGiveItem` | `UITriggerGiveItem` | `UI.UITriggerGiveItem.Config` |
| `UIVIP19RewardBox` | `UIVIP19RewardBox` | `Slg.UI.UIVip.UIVIP19RewardBox.Config` |
| `UIVIP19Rule` | `UIVIP19Rule` | `Slg.UI.UIVip.UIVIP19Rule.Config` |
| `UIVIPRewardPopUp` | `UIVIPRewardPopUp` | `Slg.UI.UIVip.UIVIPRewardPopUp.Config` |
| `UIVIPUpgradePopUp` | `UIVIPUpgradePopUp` | `Slg.UI.UIVip.UIVIPUpgradePopUp.Config` |
| `UIValentineNewExchangeShopBuy` | `UIValentineNewExchangeShopBuy` | `Slg.UI.ValentineNew.UIValentineNewExchangeShopBuyPanel.Config` |
| `UIVip` | `UIVip` | `Slg.UI.UIVip.Config` |
| `UIVipAddTime` | `UIVipAddTime` | `Slg.UI.UIVipAddTime.Config` |
| `UIVipPurchase` | `UIVipPurchase` | `Slg.UI.UIVip.UIVipPurchase.Config` |
| `UIVipRewardTip` | `UIVipRewardTip` | `Slg.UI.UIVip.UIVipRewardTip.Config` |

### PVE, Exploration & Monsters (58 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `ChampionBattleBetting` | `ChampionBattleBetting` | `Slg.UI.UIChampionBattleView.ChampionBattleBetting.Config` |
| `ChampionBattleBettingrecord` | `ChampionBattleBettingrecord` | `Slg.UI.UIChampionBattleView.UIChampionBattleBettingrecordView.Config` |
| `ChampionServerRewardGet` | `ChampionServerRewardGet` | `Slg.UI.UIChampionBattleView.ChampionServerRewardView.Config` |
| `LFChampionBattleFight` | `LFChampionBattleFight` | `Slg.UI.UIChampionBattleView.UIChampionBattleFight.Config` |
| `LFChampionBattleReport` | `LFChampionBattleReport` | `Slg.UI.UIChampionBattleView.UIChampionBattleReport.Config` |
| `LWCountBattleLose` | `LWCountBattleLose` | `-` |
| `LWCountBattleMain` | `LWCountBattleMain` | `-` |
| `LWCountBattleWin` | `LWCountBattleWin` | `-` |
| `UIAlCompeteDecisiveBattle` | `UIAlCompeteDecisiveBattle` | `UI.UIAlCompeteDecisiveBattle.Config` |
| `UIBarrelBoxRewardGet` | `UIBarrelBoxRewardGet` | `UI.UIBarrelBoxRewardGet.Config` |
| `UIBarrelGetStronger` | `UIBarrelGetStronger` | `UI.UIParkour.GetStronger.Config` |
| `UIBattleground` | `UIBattleground` | `UI.UIBattleground.Config` |
| `UIBossDamageRecord` | `UIBossDamageRecord` | `UI.UIBossDamageRecord.Config` |
| `UIBossRunAway` | `UIBossRunAway` | `UI.UIBossRunAway.Config` |
| `UIChampionBattleBattleInfo` | `UIChampionBattleBattleInfo` | `Slg.UI.UIChampionBattleView.UIChampionBattleBattleInfo.Config` |
| `UIChampionBattleChampionView` | `UIChampionBattleChampionView` | `Slg.UI.UIChampionBattleView.UIChampionBattleChampionView.Config` |
| `UIChampionBattleGuessPopupView` | `UIChampionBattleGuessPopupView` | `Slg.UI.UIChampionBattleView.UIChampionBattleGuessPopup.Config` |
| `UIChampionBattleInvitationLetterView` | `UIChampionBattleInvitationLetterView` | `Slg.UI.UIChampionBattleView.UIChampionBattleInvitationLetterView.Config` |
| `UIChampionBattleMain` | `UIChampionBattleMain` | `Slg.UI.UIChampionBattleView.UIChampionBattleMainView.Config` |
| `UIChampionBattleManifestoView` | `UIChampionBattleManifestoView` | `Slg.UI.UIChampionBattleView.UIChampionBattleManifestoView.Config` |
| `UIChampionBattleReward` | `UIChampionBattleReward` | `Slg.UI.UIChampionBattleView.UIChampionBattleRewardView.Config` |
| `UIChampionBattleReward4Server` | `UIChampionBattleReward4Server` | `Slg.UI.UIChampionBattleView.UIChampionBattleRewardView4Server.Config` |
| `UIChampionBattleRuleView` | `UIChampionBattleRuleView` | `Slg.UI.UIChampionBattleView.UIChampionBattleRuleView.Config` |
| `UIChampionBattleSettlementView` | `UIChampionBattleSettlementView` | `UI.UIChampionBattleView.UIChampionBattleSettlementView.Config` |
| `UIChampionpropaganda` | `UIChampionpropaganda` | `Slg.UI.UIChampionBattleView.Championpropaganda.Config` |
| `UIChoiceOfCommander` | `UIChoiceOfCommander` | `UI.BattleCommand.UIChoiceOfCommander.Config` |
| `UIChristmasParkourMain` | `UIChristmasParkourMain` | `UI.UIPVE.UIChristmasParkourMain.Config` |
| `UICommandPanel` | `UICommandPanel` | `UI.BattleCommand.UICommandPanel.Config` |
| `UIDemonHunterMonsterSelect` | `UIDemonHunterMonsterSelect` | `UI.DemonHunter.UIDemonHunterMonsterSelect.Config` |
| `UIDragonBattleScore` | `UIDragonBattleScore` | `UI.UIDragonBattleScore.Config` |
| `UIDrakeBossAutoJoinTips` | `UIDrakeBossAutoJoinTips` | `UI.UIDrakeBossAutoJoinTips.Config` |
| `UIDrakeBossRewardTip` | `UIDrakeBossRewardTip` | `UI.UIDrakeBossRewardTip.Config` |
| `UIEditDragonCommandMsg` | `UIEditDragonCommandMsg` | `UI.BattleCommand.EditDragonCommandMsg.Config` |
| `UIMonsterTowerAlFightRecord` | `UIMonsterTowerAlFightRecord` | `UI.UIMonsterTowerAlFightRecord.Config` |
| `UIMonsterTowerAlLVRewardInfo` | `UIMonsterTowerAlLVRewardInfo` | `UI.UIMonsterTowerAlLVRewardInfo.Config` |
| `UIMonsterTowerComing` | `UIMonsterTowerComing` | `UI.UIMonsterTowerComing.Config` |
| `UIMonsterTowerRewardGet` | `UIMonsterTowerRewardGet` | `UI.UIMonsterTowerRewardGet.Config` |
| `UIMonsterTowerTips` | `UIMonsterTowerTips` | `UI.UIMonsterTowerTips.Config` |
| `UIPVEChallengeWarning` | `UIPVEChallengeWarning` | `UI.UIPVE.UIPVEChallengeWarning.Config` |
| `UIPVEEnterLevel` | `UIPVEEnterLevel` | `UI.UIPVE.UIPVEEnterLevel.Config` |
| `UIPVELevelLoading` | `UIPVELevelLoading` | `UI.UIPVE.UIPVELevelLoading.Config` |
| `UIPVELevelReward_SU` | `UIPVELevelReward_SU` | `UI.UIPVE.UIPVELevelReward_SU.Config` |
| `UIPVELoading` | `UIPVELoading` | `UI.UIPVE.UIPVELoading.Config` |
| `UIPVEMonsterToLevel` | `UIPVEMonsterToLevel` | `UI.UIPVE.UIPVEMonsterToLevel.Config` |
| `UIPVEScene` | `UIPVEScene` | `UI.UIPVE.UIPVEScene.Config` |
| `UIPVETowerClimbJump` | `UIPVETowerClimbJump` | `UI.UIPVE.UIPVETowerClimbJump.Config` |
| `UIPVETowerClimbJumpReward` | `UIPVETowerClimbJumpReward` | `UI.UIPVE.UIPVETowerClimbJumpReward.Config` |
| `UIParkourBattleLose` | `UIParkourBattleLose` | `UI.UIParkour.LoseUI.Config` |
| `UIParkourBattleMain` | `UIParkourBattleMain` | `UI.UIParkour.MainUI.Config` |
| `UIParkourBattleWin` | `UIParkourBattleWin` | `UI.UIParkour.WinUI.Config` |
| `UIRoamingBossNotice` | `UIRoamingBossNotice` | `UI.UIRoamingBoss.Notice.Config` |
| `UIRoamingBossRecord` | `UIRoamingBossRecord` | `UI.UIRoamingBoss.Record.Config` |
| `UIRoamingBossRewardPreview` | `UIRoamingBossRewardPreview` | `UI.UIRoamingBoss.RewardPreview.Config` |
| `UISearchMonster` | `UISearchMonster` | `UI.UISearchMonster.Config` |
| `UITowerRecord` | `UITowerRecord` | `Slg.UI.UITowerRecord.Config` |
| `UITowerupBattleLose` | `UITowerupBattleLose` | `-` |
| `UIZombieBattleHangUpReward` | `UIZombieBattleHangUpReward` | `-` |
| `UIZombieBattleMain` | `UIZombieBattleMain` | `UI.UIZombieBattle.Config` |

### Radar & Detect Events (5 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `UIAlarm` | `UIAlarm` | `Slg.UI.UIAlarm.Config` |
| `UIDemonHunterRadar` | `UIDemonHunterRadar` | `UI.DemonHunter.UIDemonHunterRadar.Config` |
| `UIDetectHelpMessageBar` | `UIDetectHelpMessageBar` | `UI.UIDetectHelpMessageBar.Config` |
| `UIDetectNpc` | `UIDetectNpc` | `UI.UIRadarCenter.UIDetectNpc.Config` |
| `UIRadarCloud` | `UIRadarCloud` | `UI.UIRadarCloud.Config` |

### Science, Research & Talents (14 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `TouchScreenEffect` | `TouchScreenEffect` | `UI.TouchScreenEffect.Config` |
| `UIDecorationEffect` | `UIDecorationEffect` | `UI.UIDecoration.UIDecorationEffect.Config` |
| `UIDesertOperateBuffList` | `UIDesertOperateBuffList` | `UI.UIDesertOperateBuffList.Config` |
| `UIMastery` | `UIMastery` | `UI.UIMastery.Config` |
| `UIMasteryCast` | `UIMasteryCast` | `-` |
| `UIMasteryDetail` | `UIMasteryDetail` | `UI.UIMasteryDetail.Config` |
| `UIMasteryExpTip` | `UIMasteryExpTip` | `UI.UIMasteryExpTip.Config` |
| `UIMasterySelect` | `UIMasterySelect` | `UI.UIMasterySelect.Config` |
| `UIMasteryTree` | `UIMasteryTree` | `UI.UIMasteryTree.Config` |
| `UIPhonographBuffDetail` | `UIPhonographBuffDetail` | `UI.UIPhonograp.UIPhonograpBuffDetail.Config` |
| `UIScience` | `UIScience` | `UI.UIScience.Config` |
| `UIScienceInfo` | `UIScienceInfo` | `UI.UIScienceInfo.Config` |
| `UIScienceTab` | `UIScienceTab` | `UI.UIScienceTab.Config` |
| `UIScienceTabLock` | `UIScienceTabLock` | `UI.UIScienceTabLock.Config` |

### Trucks & Escort (2 windows)

| `UIWindowNames` Key | Window String Value | `UIConfig` Module Path |
|---|---|---|
| `UIHalloweenMarbleProbability` | `UIHalloweenMarbleProbability` | `Slg.UI.HalloweenMarble.UIHalloweenMarbleProbability.Config` |
| `UIXmasLuckyRollProb` | `UIXmasLuckyRollProb` | `UI.UIXmasLuckyRollProb.Config` |

## 6. Complete All-Window Deep Extraction (1,549 / 1,627 Windows - Prefabs, Layers, Views, Controllers & Button Refs)

> **Updated:** `2026-11-23 11:03:26 UTC` | **Source:** `megamind/raw/ui_complete_all_windows.json` (read-only `require` of all `UIConfig` modules - **zero unopened-window blind spots!**)

| Deep UI Metric | Verified Count |
|---|---:|
| UI Window Configs Fully Extracted | **1,549** / 1,627 |
| Unity Prefab Asset Paths Mapped | **1,547** |
| Total UI View / Ctrl / Model Methods | **28,672** |
| Total Mapped UI Click / Action Handlers | **7,177** |
| Total Internal Button / Toggle Object References | **3,899** |
| Extra Live `UIContainer` Controls (Toggle/Slider/ScrollRect/Input) | **19** (`InputField=0, ScrollRect=0, Slider=12, TMP_InputField=0, Toggle=7`) |

### Complete Window Prefab, Layer, Handler & Button Reference Catalog (All 1,549 Windows)
| Window Name | Layer | Prefab Path | View/Ctrl Methods | Action Handlers | Key Button Refs (`btn*`) | Outgoing `MsgDefines` / `UIWindowNames` |
|---|---|---|---:|---:|---|---|
| `ActivityTip` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/ActivityTip/Activ...` | 10 | 2 | Music_Effect_Button, OnClickGotoBtn, UIButton, banner_btn, banner... | - |
| `AttZombiePuzzleTaskPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/AttZombiePuzzle/A...` | 15 | 5 | Music_Effect_Button | MSG:MsgDefines.TaskRewardGet ; UI:UIActivityListPanel,self |
| `BarterShopNotice2Stage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/BarterShopNotice/...` | 14 | 4 | OnClickCloseBtn, UIButton, bgBtnN, bgBtn_path, closeBtnN, closeBt... | UI:UILuckyShopPreview |
| `CardGetReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/WeekCard/CardGetRewa...` | 15 | 5 | UIButton, close_btn, close_btn_path, onekey_btn_path, onekey_btn_... | MSG:MsgDefines.ClaimGolloesDailyReward,MsgDefines.ClaimGolloesFreeReward |
| `CastleAdventureChatHelp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleAdve...` | 8 | 3 | btnNum, toggleAction, toggleText | UI:self |
| `CastleAdventureExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/CastleAdventu...` | 14 | 6 | - | UI:CastleAdventureExchangeMapRecord,self |
| `CastleAdventureExchangeFrageComfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/CastleAdventu...` | 8 | 1 | - | UI:self |
| `CastleAdventureExchangeMapRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/CastleAdventu...` | 19 | 7 | Music_Effect_Button, OnClickToggle, toggles | UI:self |
| `CastleAdventureMap` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleAdve...` | 12 | 3 | - | UI:UIPositionShare,self |
| `CastleAdventureMapRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleAdve...` | 10 | 2 | Music_Effect_Button, UIButton, closeBtn, costBtn_path, panelBtn | UI:self |
| `CastleAdventureMapReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleAdve...` | 9 | 1 | - | UI:self |
| `CastleAdventureRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleAdve...` | 24 | 3 | - | UI:self |
| `CastleAdventureShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/CastleAdventu...` | 23 | 7 | isMaxBtn, maxBtnN | UI:self |
| `CastleAdventureTreasureShowHelp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CastleAdventure/UICastleAdve...` | 3 | 1 | - | - |
| `ChampionBattleBetting` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampionB...` | 2 | 2 | - | UI:self |
| `ChampionServerRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionb...` | 31 | 5 | RefreshLikeBtn, getBtn | UI:ChampionServerRewardGet |
| `ChatAtMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatAtMember/ChatAtM...` | 13 | 2 | Music_Effect_Button, UIButton, close_btn, close_btn_path | UI:ChatAtMember |
| `ChristmasActDecorationUseItemPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDecorati...` | 14 | 2 | - | UI:self |
| `ChristmasActPersonReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonate/U...` | 18 | 3 | - | UI:self |
| `ChristmasActReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonate/U...` | 21 | 5 | - | UI:UIActivityCenterTable,self |
| `ChristmasActTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonate/U...` | 18 | 5 | - | MSG:MsgDefines.TaskRewardBatch ; UI:self |
| `ChristmasDecorationRewardGetPanel` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDecorati...` | 27 | 3 | - | UI:self |
| `ChristmasParkourAnimal` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParkour/...` | 23 | 6 | Music_Effect_Button | UI:ChristmasParkourAnimal,UIGiftPackageRewardGet |
| `ChristmasParkourAnimalTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParkour/...` | 12 | 3 | - | UI:ChristmasParkourAnimalTip |
| `ChristmasParkourAttribute` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParkour/...` | 14 | 3 | - | UI:ChristmasParkourAttribute |
| `ChristmasParkourIdleReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParkour/...` | 30 | 8 | Music_Effect_Button, getBtn, toggleBtnMark | UI:ChristmasParkourIdleReward |
| `ChristmasParkourRankReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParkour/...` | 16 | 5 | ToggleType, toggleData, toggles | UI:ChristmasParkourRankReward |
| `ChristmasParkourShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasParkour/...` | 17 | 5 | Music_Effect_Button, toggleBtnMark | UI:ChristmasParkourShop |
| `ChristmasShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasExchange...` | 20 | 6 | isMaxBtn, maxBtnN | UI:ChristmasShopBuyPanel |
| `DigTreasureGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/DigTreasureGift/DigTrea...` | 18 | 4 | - | MSG:MsgDefines.TreasureRewardRecord ; UI:UIOtherPlayerInfo |
| `DispatchOneKey` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/UIDi...` | 16 | 5 | GetColorsForToggle, IsTaskBelongToToggle, RefreshAllToggleState, ... | - |
| `DispatchRefreshBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/UIDi...` | 12 | 0 | - | - |
| `DispatchStealDescBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/UIDi...` | 12 | 0 | - | - |
| `FoodFestivalCookResultPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/FoodFestivalCookRe...` | 14 | 3 | - | UI:self |
| `FoodFestivalRedEnvelopeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/FoodFestivalRedEnv...` | 9 | 1 | Music_Effect_Button, UIButton, _sendRed_btn, btn_sendRed_path, re... | - |
| `GivingRoseLevelRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/LevelReward/Givin...` | 17 | 3 | - | UI:self |
| `GodzillaGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/GodzillaGift/GodzillaGi...` | 17 | 3 | - | MSG:MsgDefines.TreasureRewardRecord ; UI:UIOtherPlayerInfo |
| `HalloweenZombieBossComingPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 13 | 2 | - | UI:self |
| `HeroLevelExchangeConfirmPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroLevelExChangeCo...` | 18 | 6 | SetBtnState, btnConfirm, btnGray | - |
| `HeroLevelExchangeResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroLevelExChangeSu...` | 11 | 0 | - | - |
| `HeroLevelExchangeSelectList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroLevelExChangeHe...` | 18 | 5 | - | - |
| `HeroTrialReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/HeroTrial/HeroTri...` | 15 | 3 | - | UI:self |
| `LFChampionBattleFight` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampionB...` | 15 | 2 | - | UI:LFChampionBattleFight |
| `LFChampionBattleReport` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampionB...` | 13 | 2 | - | UI:LFChampionBattleReport |
| `MailVerificationPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPayPassword/MailVerificationPo...` | 8 | 3 | OnButtonCloseClicked, OnButtonConfirmClicked, UIButton, UICommonM... | MSG:MsgDefines.CheckPayPwdCode |
| `MainUI_SU` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/SU_Main/UIPVEMainTableNew.prefab` | 225 | 40 | CheckBtnShow, CheckKillMonsterBtnShow, CheckShowRankBtn, Function... | UI:UIFormationTableNew,UIGiftPackage,UIHeroList |
| `MonopolyActivityDrawStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonopolyActivity/...` | 15 | 3 | RefreshToggle, Toggle1, Toggle2, ToggleTag, toggleTag | UI:self |
| `PayPasswordInputPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPayPassword/PayPasswordInputPo...` | 7 | 3 | Music_Effect_Button, OnButtonCloseClicked, OnButtonConfirmClicked... | - |
| `SU_NewHero` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIHero/New/SU_NewHero.prefab` | 16 | 4 | ToggleRecruitScene | UI:self |
| `SetPayPasswordPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPayPassword/SetPayPasswordPopu...` | 9 | 3 | Music_Effect_Button, OnButtonCloseClicked, OnButtonConfirmClicked... | MSG:MsgDefines.SetPayPwd |
| `SevenDayBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/SevenDay/SevenDay...` | 12 | 2 | UIButton, UICommonMidPopUpTitle/CloseBtn, _close_btn, return_btn | - |
| `SevenDayBoxNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/SevenDay/SevenDay...` | 16 | 4 | ReceiveBtnClick, UIButton, UICommonPopUpTitle/CloseBtn, _close_bt... | - |
| `ShowItemTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/SU_ShowItemTips.prefab` | 8 | 0 | - | - |
| `ThanksGivingExchangeShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingTurkey...` | 18 | 6 | isMaxBtn, maxBtnN | UI:self |
| `ThanksGivingTurkeySelectPlayerPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingTurkey...` | 25 | 5 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `ThroneDefendView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThroneDefend/UIThroneDefendVie...` | 26 | 6 | - | MSG:MsgDefines.AssistanceTeamRetreat ; UI:ThroneDefendView |
| `ThronePopupView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThronePopup/UIThronePopupView....` | 12 | 3 | - | - |
| `ThroneRankView` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneRanking.prefab` | 11 | 2 | UIButton, closeBtn, close_btn_path, returnBtn, return_btn_path | UI:ThroneRankView |
| `ThroneRecordView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIThroneRecord.prefab` | 26 | 7 | ToggleControlBorS_1, ToggleControlBorS_2, toggleList | UI:ThroneRecordView |
| `ThroneRewardView` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneReward.prefab` | 10 | 2 | UIButton, closeBtn, close_btn_path, returnBtn, return_btn_path | UI:ThroneRewardView |
| `TouchScreenEffect` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/TouchScreenEffect.prefab` | 5 | 1 | - | - |
| `TurkeyCookResultPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/FoodFestivalCookRe...` | 14 | 3 | - | UI:self |
| `UCityCaptureSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UCityCaptureSuccess.pr...` | 0 | 0 | - | - |
| `UIAccountBan` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIAccount/UIAccountBan.prefab` | 13 | 3 | - | - |
| `UIAccountDeleteVerify` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISetting/UIDeleteAccountVerify....` | 7 | 3 | - | MSG:MsgDefines.UserBindCancel ; UI:self |
| `UIAccountUnbind` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UISettingAccountNewTip...` | 14 | 6 | Music_Effect_Button | MSG:MsgDefines.GameCenterUnBind ; UI:UIChangeMail,self |
| `UIAccountVerify` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UIAccountVerify.prefab` | 10 | 4 | btnChangeMail | MSG:MsgDefines.AccountLoginNew ; UI:UIAddAccount,self |
| `UIActBossTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossTip.prefab` | 11 | 2 | Root/Button, Root/Button/btnTxt, UIButton, btn, btnPanel, btn_txt | - |
| `UIActDragonBattleTime` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 12 | 3 | - | UI:self |
| `UIActDragonHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 14 | 2 | - | - |
| `UIActDragonRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 14 | 5 | toggleBase, toggleReward, toggleRule | UI:UIDragonExplainPlay |
| `UIActExchangeMainView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIMatchingGame/UI...` | 22 | 9 | btnBtn, btnBtncheck, btnRedPoint | UI:UIActivityRewardTip,self |
| `UIActGiftBoxOpen` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIActGift...` | 18 | 3 | - | MSG:MsgDefines.OpenActivityGiftBox ; UI:UIGiftBoxPackageList |
| `UIActGiftBoxReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIActGift...` | 17 | 5 | - | UI:self |
| `UIActMonsterTowerDiffTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIAc...` | 11 | 2 | UIButton, _choice_btn, btn_choice_path, return_btn, return_btn_path | MSG:MsgDefines.ChooseChallengeActDifficulty |
| `UIActMonsterTowerRank` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIAc...` | 12 | 2 | UIButton, UICommonMidPopUpTitle/CloseBtn, _close_btn | UI:UIPlayerInfo |
| `UIActMonsterTowerReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIAc...` | 18 | 4 | - | UI:self |
| `UIActMonsterTowerTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIAc...` | 15 | 1 | - | - |
| `UIActivityCenterTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIActivityCenterT...` | 76 | 19 | Music_Effect_Button, UIButton, bottomCloseBtn | MSG:MsgDefines.ReceiveDonateArmyTaskReward,MsgDefines.TaskRewardGet,MsgD... |
| `UIActivityEdenWarTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/EdenWar/UIActivit...` | 6 | 0 | Music_Effect_Button, UIButton, UICommonPopUpTitle/CloseBtn, close... | - |
| `UIActivityNoticeTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMainNotice/UIActivityNoticeTip...` | 18 | 4 | - | UI:UICrossWonderAct |
| `UIActivityNoticeTip02` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMainNotice/UIActivityNoticeTip...` | 17 | 2 | - | UI:UICrossWonderAct |
| `UIActivityOverview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIActivityOverview/UIActivityOve...` | 14 | 4 | - | UI:OpenWinAnimTrue |
| `UIActivityRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIActivityRewardT...` | 18 | 7 | UIButton, return_btn | MSG:MsgDefines.SurvivalBigBox ; UI:OpenWinAnimTrue |
| `UIActivitySummary` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIActivitySummary/UIActivitySumm...` | 14 | 4 | - | UI:anim |
| `UIActivitySummaryPreview` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIActivitySummary/UIActivitySumm...` | 13 | 3 | - | UI:anim |
| `UIActivitySummaryReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIActivitySummary/UIActivitySumm...` | 11 | 2 | - | - |
| `UIAddAccount` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UIAddAccount.prefab` | 13 | 4 | Music_Effect_Button | MSG:MsgDefines.AccountLoginSendVerifyCode ; UI:self |
| `UIAddAccountBefore` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UISettingAccountBindin...` | 7 | 3 | Music_Effect_Button | UI:UIAddAccount |
| `UIAddStamina` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIRepairBuildingPopUp.prefab` | 12 | 3 | InitButtonState, Music_Effect_Button, UIButton, btn_image, close_... | MSG:MsgDefines.UserRecoverBuildingStamina |
| `UIAircraftComponInfo` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponInfo....` | 11 | 0 | - | - |
| `UIAircraftComponMerge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponMerge...` | 5 | 1 | - | - |
| `UIAircraftComponPartTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponPartT...` | 9 | 0 | - | - |
| `UIAircraftComponPreviewPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftComponPrevi...` | 11 | 1 | - | - |
| `UIAircraftGradingTip` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftGradingTip....` | 18 | 5 | - | UI:UIAircraftRankingMain,self |
| `UIAircraftMain` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftMain.prefab` | 55 | 9 | LeftToggleClick, ToggleFogVisible, ToggleMainCamera, Toggle_uSkyP... | UI:UIAircraftSkillTip |
| `UIAircraftMainComponentTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftMain_Compon...` | 9 | 0 | - | - |
| `UIAircraftMainPreview` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftPreview.prefab` | 13 | 3 | skillBtn | UI:UIAircraftSkillTip |
| `UIAircraftMainTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraUnLockTips.pr...` | 5 | 0 | - | - |
| `UIAircraftPreviewSkillWindow` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraftPreviewSkillWindow/UIA...` | 31 | 5 | FunctionBtnType, btnCanClickTime, checkBtnCanClick | MSG:MsgDefines.GarageRefitTalentStudy ; UI:UnlockNewSkill |
| `UIAircraftRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftRank.prefab` | 18 | 1 | - | UI:self |
| `UIAircraftRankingMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftRankingMain...` | 21 | 4 | BtnLock, InitToggleData, Root/ToggleGroupTop/Toggle, ToggleContro... | UI:DataCenter |
| `UIAircraftSkillTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/AircraftSkillTip.prefab` | 9 | 1 | - | UI:UIAircraftPreviewSkillWindow |
| `UIAircraftUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftUpgrade.prefab` | 18 | 2 | - | UI:SwitchShowPanel |
| `UIAircraftUpgradePreview` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftUpgradePrev...` | 10 | 3 | LeftToggleClick | - |
| `UIAlCompeteBarrage` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/AlCompeteBa...` | 38 | 8 | btn_show_hideNode | UI:UIAlCompeteBarrageTip,self |
| `UIAlCompeteBarrageTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/AlCompeteBa...` | 15 | 4 | BtnClick_Close | UI:UIAllianceCompeteNew |
| `UIAlCompeteDecisiveBattle` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/AlCompeteDe...` | 3 | 1 | - | UI:_ENV |
| `UIAlCompeteTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompete/UIAlCompeteTip...` | 13 | 6 | UIButton, UICommonPopUpTitle/CloseBtn, close_btn, return_btn | MSG:MsgDefines.CrossGetAlliancePoint |
| `UIAlLeaderCandidates` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAlLeaderCandidates.pr...` | 0 | 0 | - | - |
| `UIAlLeaderCongratulate` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAlLeaderCongratulate....` | 0 | 0 | - | - |
| `UIAlLeaderElectResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAlLeaderElectResult.p...` | 0 | 0 | - | - |
| `UIAlLeaderElectSignUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAlLeaderElectSignUp.p...` | 0 | 0 | - | - |
| `UIAlLeaderVote` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAlLeaderVote.prefab` | 0 | 0 | - | - |
| `UIAlMemberRecommend` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAlMemberRecommend...` | 13 | 1 | - | UI:self |
| `UIAlarm` | `UIContainer/Dialog` | `Assets/Main/Prefabs/Slg/UI/UIAlarm/UIAlarm.prefab` | 11 | 1 | - | - |
| `UIAllianceAnnouncementEdit` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatALAnnouncementEd...` | 0 | 0 | - | - |
| `UIAllianceAnnouncementUrgentReleaseView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIAllianceAnnounceme...` | 1 | 0 | - | - |
| `UIAllianceApplyList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceApplyList...` | 18 | 8 | Music_Effect_Button, UIButton, close_btn, close_btn_path, refuse_... | MSG:MsgDefines.AcceptAllianceApply,MsgDefines.AllianceApplyRefuseAll,Msg... |
| `UIAllianceAssemble` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceAssemble.prefab` | 2 | 1 | OnRallyBtnClick | - |
| `UIAllianceAssembleBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceAssembleBox.p...` | 0 | 0 | - | - |
| `UIAllianceAssembleConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceAssembleConfi...` | 0 | 0 | - | - |
| `UIAllianceAutoJoinRally` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceAutoJoinRally...` | 0 | 0 | - | - |
| `UIAllianceBossAllianceRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 14 | 2 | - | UI:self |
| `UIAllianceBossBounsTipsPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 15 | 2 | - | UI:self |
| `UIAllianceBossMain` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 11 | 2 | - | UI:UIAllianceBossViewPanel,self |
| `UIAllianceBossRankNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 19 | 3 | defaultToggleIndex | UI:self |
| `UIAllianceBossRewardAndRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 23 | 5 | defaultToggleIndex | UI:self |
| `UIAllianceBossViewPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 29 | 6 | - | UI:self |
| `UIAllianceBossWorldPointTipPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIAllianceBoss/UI...` | 11 | 2 | - | UI:self |
| `UIAllianceBuildingCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCitySelect/UIAllianceB...` | 22 | 7 | info_btn | UI:UIHeroTip,self |
| `UIAllianceChangeAbbr` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIChangeAllianceAbbr.pr...` | 0 | 0 | - | - |
| `UIAllianceChangeAnnounce` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceChangeAnn...` | 0 | 0 | - | - |
| `UIAllianceChangeLanguage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIChangeAllianceLanguag...` | 2 | 0 | - | - |
| `UIAllianceChangeName` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIChangeAllianceName.pr...` | 0 | 0 | - | - |
| `UIAllianceChangeRankName` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceChangeRan...` | 0 | 0 | - | - |
| `UIAllianceChangeRestriction` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceChangeRestric...` | 0 | 0 | - | - |
| `UIAllianceCity` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceCity.prefab` | 47 | 15 | _hideContent_btn, _showContent_btn, _tips_btn, buffBtn, recordBtn... | UI:UIAllianceCityBuffBox,UIAllianceMainTable,UIRobotWarsRule |
| `UIAllianceCityBar` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Common/UIAllianceCityBar.prefab` | 21 | 3 | - | UI:anim |
| `UIAllianceCityBuffBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceCityBuffB...` | 4 | 0 | - | - |
| `UIAllianceClearMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceClearMemb...` | 3 | 0 | - | - |
| `UIAllianceCompeteDayTaskPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 22 | 6 | - | UI:self |
| `UIAllianceCompeteDayTaskPopNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 23 | 6 | - | UI:self |
| `UIAllianceCompeteDayTaskTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 19 | 4 | infoBtn | UI:UIAllianceCompeteMemberScore,UICommonHeadTip,self |
| `UIAllianceCompeteFightNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAlCompete...` | 12 | 2 | - | UI:self |
| `UIAllianceCompeteMemberScore` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 22 | 3 | refreshBtnRed | - |
| `UIAllianceCompeteNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 34 | 12 | RefreshHelpBtn, alliance_btn_help, toggleN, togglesLast, togglesTbN | MSG:MsgDefines.AlHelpAll,MsgDefines.AllianceCompeteRankList,MsgDefines.E... |
| `UIAllianceCompetePopInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 10 | 1 | - | UI:self |
| `UIAllianceCompeteRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompete/UIAllianceComp...` | 30 | 8 | Music_Effect_Button, infoBtn, selfTipBtn | UI:UIHeroTip |
| `UIAllianceCompeteReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompete/UIAllianceComp...` | 14 | 4 | - | - |
| `UIAllianceCompeteTaskTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 8 | 3 | - | UI:self |
| `UIAllianceCompeteTaskTip2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceC...` | 8 | 3 | - | UI:self |
| `UIAllianceCompeteWinOrLoss` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceCompeteNew/UIAllianceW...` | 17 | 3 | - | MSG:MsgDefines.GetAlBattleDayVsInfo ; UI:self |
| `UIAllianceCreatePopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceCreatePopUp.p...` | 2 | 2 | WorldTileBtnType | - |
| `UIAllianceDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceDetail.pr...` | 22 | 10 | ImgBg/Align/commentButton/goTextMat, UIButton, commentBtnImg, com... | MSG:MsgDefines.AlCancelApply,MsgDefines.AlSearch,MsgDefines.GetAllianceI... |
| `UIAllianceDismiss` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceDissolveP...` | 15 | 4 | - | UI:UIAllianceMainTable,self |
| `UIAllianceDissolving` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceDissolveP...` | 18 | 4 | - | UI:self |
| `UIAllianceEveryDayTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceEveryDayTask....` | 15 | 1 | - | - |
| `UIAllianceExitTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceExitTip.prefab` | 15 | 3 | BtnClick_Close | MSG:MsgDefines.AlLeave ; UI:UIAllianceMainTable,self |
| `UIAllianceFlag` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceFlag.prefab` | 28 | 9 | CheckSetBtnOrSeasonEffectBtn, setBtnCostN, setBtnFreeTxtN | UI:self |
| `UIAllianceGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceGift.prefab` | 43 | 17 | OnDelAllBtnClick, OnGetAllBtnClick, UIButton, UIToggle, btnGiftBu... | MSG:MsgDefines.AllianceAllGiftRemove,MsgDefines.AllianceGiftGetReward,Ms... |
| `UIAllianceGiftInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceGiftInfo.prefab` | 15 | 4 | Music_Effect_Button, UIButton, close_btn, close_btn_path, get_btn... | MSG:MsgDefines.AllianceGiftGetReward ; UI:self |
| `UIAllianceGiftReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceGiftRewar...` | 14 | 2 | - | UI:self |
| `UIAllianceGiftRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceGiftRule....` | 12 | 1 | - | - |
| `UIAllianceHaggleMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceHaggle/UI...` | 30 | 12 | Music_Effect_Button | UI:UIAllianceHaggleMain,UIAllianceHaggleMember,UIAllianceIntro |
| `UIAllianceHaggleMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceHaggle/UI...` | 18 | 6 | Music_Effect_Button | UI:UIAllianceHaggleMember |
| `UIAllianceHaggleSlot` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceHaggle/UI...` | 12 | 3 | Music_Effect_Button | UI:UIAllianceHaggleSlot |
| `UIAllianceHelp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceHelp.prefab` | 29 | 9 | Music_Effect_Button, OnClickInfoBtn, OnClickPersonalScoreBtn, OnD... | MSG:MsgDefines.AlHelpAll,MsgDefines.AllianceRenderHelp ; UI:OpenWinAnimT... |
| `UIAllianceIntro` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceIntro.prefab` | 3 | 0 | - | - |
| `UIAllianceInviteTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceInviteTip...` | 7 | 4 | OnClickCloseBtn, OnClickConfirmBtn, UIButton, closeBtnN, closeBtn... | UI:UIPositionShare,self |
| `UIAllianceJoinCondition` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceJoinCondi...` | 10 | 2 | Music_Effect_Button, UIButton, btnText, btnText_path, btn_image, ... | UI:self |
| `UIAllianceKickMemberView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceKickMembe...` | 6 | 0 | - | - |
| `UIAllianceLeaderReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceBenefits.prefab` | 31 | 15 | UpdateDailyGetBtnState, dayGetBtn, dayGetBtnTxt | UI:self |
| `UIAllianceLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceLog.prefab` | 11 | 1 | - | - |
| `UIAllianceLogEx` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/AllianceLogEx/UIAll...` | 21 | 1 | - | - |
| `UIAllianceMainTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceMainTable...` | 54 | 14 | AllianceButtonType, _defaultToggle, _guideBtn, _toggle1, _toggle2... | MSG:MsgDefines.AlLeaveItem ; UI:GetInstance,UIAllianceChangeAnnounce,UIA... |
| `UIAllianceMark` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIAllianceMark.prefab` | 29 | 5 | PUSH_TOGGLE_DIALOG_ID | - |
| `UIAllianceMarkRemindNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMainNotice/UIAllianceMarkNotic...` | 10 | 3 | Music_Effect_Button, OnGoBtnClick | - |
| `UIAllianceMarkTip` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceMarkTip.prefab` | 9 | 1 | - | - |
| `UIAllianceMemberDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceMemberDet...` | 6 | 0 | - | - |
| `UIAllianceMemberTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceMemberTip...` | 5 | 2 | - | MSG:MsgDefines.GetNewUserInfo ; UI:UIAllianceMemberDetail |
| `UIAllianceMerge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/AllianceMerge/UIAllianc...` | 16 | 4 | - | UI:self |
| `UIAllianceOfficialSkill` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceOfficialS...` | 29 | 3 | - | - |
| `UIAllianceOfficialSkillPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceOfficialS...` | 26 | 3 | - | - |
| `UIAllianceOfficialSkillRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceOfficialS...` | 17 | 1 | - | - |
| `UIAlliancePVEView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllyAvatar/UIAllyClearanceView...` | 13 | 0 | - | - |
| `UIAllianceQa` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceQa.prefab` | 17 | 4 | - | - |
| `UIAllianceRallyInputPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceRallynputPop....` | 19 | 6 | Root/Btn, Root/Btn/btnText, Root/Toggle, Root/Toggle/Name, UIButt... | UI:OnSaveClick,self |
| `UIAllianceRallyOperate` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIMoveCity2.prefab` | 0 | 0 | - | - |
| `UIAllianceRankReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceRankRewar...` | 8 | 2 | - | - |
| `UIAllianceRankSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceRankSelec...` | 4 | 2 | - | - |
| `UIAllianceRankTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceRankTable...` | 10 | 5 | RefreshToggleState, SetContributeBtnVisible, SetRewardBtnVisible,... | MSG:MsgDefines.DailyAllianceDonaterRank ; UI:UIAllianceScience,UIOtherPl... |
| `UIAllianceScience` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceScience/U...` | 9 | 3 | Music_Effect_Button | - |
| `UIAllianceScienceDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceScience/U...` | 4 | 0 | - | - |
| `UIAllianceScienceInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceScience/U...` | 19 | 5 | Music_Effect_Button | - |
| `UIAllianceSelectRole` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceSelectRol...` | 12 | 3 | RoleBtnType | UI:self |
| `UIAllianceShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceShop.prefab` | 28 | 10 | GetCurButtonState, ToggleControlBorS, UIButton, UIToggle, alPoint... | MSG:MsgDefines.AlShopBuyUsr ; UI:UIHeroTip,UIItemTips,UIMultiBuy |
| `UIAllianceShopAddPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/AllianceShopP...` | 18 | 5 | - | UI:self |
| `UIAllianceShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIAllianceShopBuyPanel/UIAll...` | 26 | 9 | - | MSG:MsgDefines.AlShopBuyAl,MsgDefines.AlShopBuyUsr ; UI:self |
| `UIAllianceShopLevelUpNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/UIAllianceSho...` | 11 | 3 | box01BtnN, box02BtnN | UI:self |
| `UIAllianceShopPlusBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/UIAllianceSho...` | 33 | 11 | btnNum, maxBtn, toggleAction, toggleText | UI:self |
| `UIAllianceShopPlusLaunch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/UIAllianceSho...` | 26 | 11 | Music_Effect_Button, OnToggleValueChanged, addBtnN, maxBtn, subBt... | UI:self |
| `UIAllianceShopPlusRecordTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/UIAllianceSho...` | 17 | 3 | - | UI:self |
| `UIAllianceShopRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAllianceShopPlus/UIAllianceSho...` | 20 | 5 | - | UI:self |
| `UIAllianceTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceTask.prefab` | 16 | 3 | WorldTileBtnType | UI:UIActivityCenterTable,self |
| `UIAllianceWarDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceWarDetail.prefab` | 37 | 17 | Music_Effect_Button, UIButton, _info_btn, close_btn, return_btn, ... | MSG:MsgDefines.AllianceWarCancel,MsgDefines.AllianceWarRetreat,MsgDefine... |
| `UIAllianceWarIntelligence` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceWar/UIAll...` | 43 | 8 | AttackSetBtn, ScoutSetBtn | UI:UIOtherPlayerInfo,self |
| `UIAllianceWarMainTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceWarMainTa...` | 70 | 23 | PlayRefreshBtnPanelAnim, REFRESH_BTN_ANIM_CLIP, REFRESH_BTN_ANIM_... | MSG:MsgDefines.AllianceWarRetreat,MsgDefines.GetAllianceAlertMarch ; UI:... |
| `UIAllianceWarPersonalList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceWarPerson...` | 31 | 7 | AttackSetBtn, ScoutSetBtn | UI:UIOtherPlayerInfo,self |
| `UIArena3V3Battle` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3BattleV...` | 26 | 7 | SetChangeTeamBtnVisible | UI:UIArena3V3Battle,UIArenaPanel |
| `UIArena3V3BattleReport` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3BattleR...` | 13 | 2 | - | UI:UIArena3V3BattleReport |
| `UIArena3V3Challenge` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Challen...` | 22 | 6 | refreshBtnCostN, refreshBtnCostNum, refreshBtnTxtN | MSG:MsgDefines.BuyCrossArenaTicket,MsgDefines.RefreshCrossArenaChallenge... |
| `UIArena3V3Entrance` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Entranc...` | 16 | 3 | - | UI:UIArena3V3Entrance |
| `UIArena3V3History` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3History...` | 18 | 6 | buttonInfo | MSG:MsgDefines.BuyCrossArenaTicket,MsgDefines.GetCrossArenaBattleHistory... |
| `UIArena3V3Popup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Popup.p...` | 13 | 4 | Music_Effect_Button | UI:UIArena3V3Popup,UIArenaPanel |
| `UIArena3V3Result` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Result....` | 30 | 16 | UIButton, WorldTileBtnType, btn, rightBtnRoot, rightReplayBtn, ri... | MSG:MsgDefines.GetCrossArenaInfo ; UI:UIArena3V3Challenge,UIArena3V3Resu... |
| `UIArenaChallenge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArena/UIArenaChallenge.prefab` | 22 | 6 | refreshBtnCostN, refreshBtnCostNum, refreshBtnTxtN | MSG:MsgDefines.BuyCrossArenaTicket,MsgDefines.RefreshCrossArenaChallenge... |
| `UIArenaConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonComfirm.prefab` | 12 | 3 | - | - |
| `UIArenaHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArena/UIArenaHistory.prefab` | 18 | 6 | buttonInfo | MSG:MsgDefines.BuyCrossArenaTicket,MsgDefines.GetCrossArenaBattleHistory... |
| `UIArenaPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArenaPanel/UIArenaPanel.prefab` | 23 | 5 | RefreshToggle, toggleGroup | UI:UIArena3V3Popup |
| `UIArenaPlayerArmy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena/UIArenaPlayerArmy.pr...` | 7 | 2 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | UI:self |
| `UIArenaRankPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArenaRankPop/UIArenaRankPop.pr...` | 16 | 2 | - | - |
| `UIArenaReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Arena/UIArenaRewa...` | 21 | 6 | Music_Effect_Button, defaultToggleIndex | UI:self |
| `UIArenaSeasonResetPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArena/UIArenaSeasonResetPopup....` | 10 | 1 | toggle | - |
| `UIArmyInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmyInfo.prefab` | 14 | 2 | - | - |
| `UIArmySelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmySelect.prefab` | 8 | 1 | - | UI:anim |
| `UIArmyTipView3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips3.prefab` | 12 | 1 | - | UI:self |
| `UIArmyTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips.prefab` | 8 | 1 | - | UI:self |
| `UIArmyTips1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips1.prefab` | 10 | 1 | - | UI:self |
| `UIArmyTips2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIArmyTips2.prefab` | 6 | 1 | - | UI:self |
| `UIArmyUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITrain/UIArmyUnlock.prefab` | 6 | 0 | - | - |
| `UIArrow` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIArrow.prefab` | 19 | 1 | - | - |
| `UIAssistanceHeroSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAssistanceHero/UIAssistanceHer...` | 30 | 9 | - | UI:UICapacityBoxSelect |
| `UIAssistanceHeroSettle` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAssistanceHero/UIAssistanceHer...` | 16 | 4 | btnLike | UI:UIHeroEquipForgingSuccessful |
| `UIAssistanceHeroShareConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAssistanceHero/UIAssistanceHer...` | 21 | 9 | ShouldShowNoMoreTipToggle, UIButton, back_toggle, btnYesCost, btn... | MSG:MsgDefines.ChatPushNotice,MsgDefines.ThanksGivingStarLevelShare ; UI... |
| `UIAssistanceThrone` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAssistanceThroneMain....` | 27 | 8 | - | MSG:MsgDefines.AssistanceTeamRetreat ; UI:OpenWinAnimTrue,UIThroneDetail |
| `UIBPSelectPack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBPSelectPack/UIBPSelectPack.pr...` | 13 | 1 | infoBtn | UI:UIItemTips |
| `UIBagPickUp` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/Survival/UIBag/UIBagPickUp.prefab` | 22 | 7 | - | MSG:MsgDefines.BagGridMoveAll ; UI:self |
| `UIBagPropStatis` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIBagStatis/UIBagPropStatisV...` | 22 | 4 | Music_Effect_Button | UI:self |
| `UIBagSplit` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UIBag/UIBagSplit.prefab` | 13 | 6 | - | UI:self |
| `UIBagUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UIBag/UIBagUpgrade.prefab` | 11 | 6 | - | UI:self |
| `UIBagView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIBagView/UIBagView.prefab` | 46 | 15 | toggleIndexToType, toggleName, toggle_btn | UI:UIBagPropStatis,self |
| `UIBarrelBoxRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/GiftPackage/UIBoxRewardGet.prefab` | 13 | 2 | - | - |
| `UIBarrelCarFightTip` | `UIContainer/Info` | `Assets/Main/Prefabs/Guide2/UIGuideTalk7FightBubble.prefab` | 6 | 0 | - | - |
| `UIBarrelGetStronger` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIBarrelGetStronger.prefab` | 6 | 1 | - | - |
| `UIBarrelHeroBottomInfo` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Barrel/UIBarrelHeroBottomInfo.pr...` | 14 | 1 | - | - |
| `UIBarrelHeroFightTip` | `UIContainer/Info` | `Assets/Main/Prefabs/Guide2/UIGuideTalk6FightBubble.prefab` | 6 | 0 | - | - |
| `UIBarterShopNoticeTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBarterShopNoticeTask/UIBarterS...` | 15 | 1 | - | - |
| `UIBattlePassBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/BattlePass/UIBatt...` | 19 | 4 | - | MSG:MsgDefines.BuyBattlePassLevel |
| `UIBattlePassGifSeasonPopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/BattlePass/UI...` | 21 | 4 | - | UI:UIBattlePassGiftPackagePopUpDev,self |
| `UIBattlePassGiftPackagePopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/BattlePass/UIBatt...` | 22 | 2 | - | UI:_ENV |
| `UIBattlePassPrivilege` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/BattlePassSea...` | 18 | 4 | - | UI:UIBattlePassGifSeasonPopUp,self |
| `UIBattleReportInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/BattleReportI...` | 11 | 2 | - | UI:self |
| `UIBattleReportInfo4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/old/BattleReport/BattleRep...` | 11 | 2 | - | - |
| `UIBattleground` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Main/UIBattleground.prefab` | 29 | 10 | Music_Effect_Button, Setting/SwitchObj/GameObject/BtnInfo, Settin... | UI:self |
| `UIBaubleExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBauble/UIBaubleExchange.prefab` | 17 | 4 | - | UI:self |
| `UIBaubleInfo` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIBauble/UIBaubleInfo.prefab` | 18 | 4 | - | UI:self |
| `UIBaubleInfoPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIBaubleInfoPopup.p...` | 11 | 0 | - | - |
| `UIBaubleLevelUpPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIBaubleLevelUpPopu...` | 4 | 0 | Ani/continueBtn/countinueTxt, UIButton, buttonClose | - |
| `UIBaubleLibrary` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIBaubleLibrary.prefab` | 8 | 3 | Music_Effect_Button, OnButtonCloseClicked, UIButton, UICommonFull... | - |
| `UIBaubleRatingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIBaubleRatingPopup...` | 6 | 1 | OnButtonCloseClicked, UIButton, UICommonPopUpTitle/bg_mid/CloseBt... | - |
| `UIBaubleUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBauble/UIBaubleUpgrade.prefab` | 23 | 7 | exchange_btn | UI:UIBaubleExchange,self |
| `UIBaubleUpgradePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationCollect...` | 19 | 8 | Music_Effect_Button, OnButtonCloseClicked, OnButtonInfoClicked, R... | UI:UIBaubleInfoPopup,UIBaubleLibrary |
| `UIBaubleUpgradeSuccessPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBauble/UIBaubleUpgradeSuccessP...` | 2 | 0 | - | - |
| `UIBindAccount` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIBindAccount.prefab` | 11 | 6 | textBtnEmail | UI:UICreateAccount |
| `UIBindAccountAlready` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIBindAccountAlready.p...` | 8 | 1 | - | UI:UIBindAccountCreate |
| `UIBindAccountCreate` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIBindAccountCreate.pr...` | 16 | 4 | - | MSG:MsgDefines.AccountChangePassword ; UI:self |
| `UIBindSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIBindSuccess.prefab` | 5 | 1 | - | - |
| `UIBlackChangeMask` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/UIBlackChangeMask/UIBlackChangeM...` | 14 | 0 | - | - |
| `UIBlackGradientWindow` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBlackGradientWindow/UIBlackGra...` | 5 | 0 | - | - |
| `UIBlackHoleMask` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIBlackHoleMask.prefab` | 18 | 1 | - | - |
| `UIBlackKnighReservation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/UIB...` | 25 | 4 | - | UI:UIActivityCenterTable |
| `UIBlackKnightComing` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/BossComing/UIBlac...` | 8 | 1 | - | - |
| `UIBlackKnightInfo` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/UIB...` | 20 | 5 | - | UI:UIAllianceIntro,UIAllianceWarPersonalList |
| `UIBlackKnightMemberInfoMenu` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/UIB...` | 7 | 5 | OnButtonCloseClick, OnButtonDetailClicked, OnButtonGoToClicked, O... | UI:UIFormationAssistance,UIOtherPlayerInfo |
| `UIBlackKnightMemberInfoPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/UIB...` | 10 | 4 | BtnRefresh, BtnRefresh/btnText, OnButtonIntelligenceClicked, UIBu... | UI:UIBlackKnightMemberInfoMenu |
| `UIBlackKnightPlayerTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/UIB...` | 8 | 3 | BtnClose, OnButtonCloseClick, Root/Btn, Root/Btn/btnText, UIButto... | UI:self |
| `UIBlackKnightRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIBlackKnight/UIB...` | 17 | 4 | SetToggleChoose, toggle | - |
| `UIBlackLandRuinRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIBlackLandRuinRecord....` | 13 | 3 | - | MSG:MsgDefines.GetBlackLandRuinRecord |
| `UIBlackView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Guide/UIShowBlack.prefab` | 5 | 0 | - | - |
| `UIBlindBoxGiftView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIBlindBoxPanel/UIBlindBoxGiftV...` | 21 | 5 | - | UI:UIGiftPackage,self |
| `UIBlindBoxRewardOpenView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIBlindBoxPanel/UIBlindBoxRewar...` | 24 | 6 | mOpenBtnNewButton | UI:UIBlindBoxRuleView,self |
| `UIBlindBoxRuleChristmasView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasBlindBox...` | 14 | 3 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `UIBlindBoxRuleView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIBlindBoxPanel/UIBlindBoxRuleV...` | 14 | 3 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `UIBlindBoxScoreView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIBlindBoxPanel/UIBlindBoxScore...` | 28 | 12 | SetRewardBtn, UpdateBigRewardJumpBtn, mBtnJumUpActive, mBtnJumpDo... | UI:self |
| `UIBlindBoxSelectBoxChristmasView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasBlindBox...` | 18 | 3 | - | UI:self |
| `UIBlindBoxSelectBoxEasterView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIEaster/UIEasterBlindBox/UIEas...` | 18 | 3 | - | UI:self |
| `UIBlindBoxSelectBoxView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIBlindBoxPanel/UIBlindBoxSelec...` | 18 | 3 | - | UI:self |
| `UIBlindBoxShopView` | `UIContainer/Normal` | `Assets/Main/Prefab_Dir/UI/UIBlindBoxPanel/UIBlindBoxSho...` | 18 | 3 | - | UI:self |
| `UIBookMark` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BookMark/UIBookMark.prefab` | 16 | 6 | ToggleControlBorS, UIButton, UIToggle, close_btn, close_btn_path,... | UI:anim |
| `UIBookMarkAdd` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BookMark/UIBookMarkAdd.prefab` | 14 | 5 | Music_Effect_Button, ToggleControlBorS, UIButton, UIToggle, close... | UI:anim |
| `UIBookMarkPositionCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BookMark/UIBookMarkPositionColle...` | 15 | 5 | Music_Effect_Button, UIButton, btn, btn_book_mark, btn_book_mark_... | UI:UIBookMark,self |
| `UIBossDamageRecord` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIBossDamageRecord/UIBossDamageR...` | 9 | 0 | - | - |
| `UIBossRunAway` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBossRunAway/UIBossRunAway.prefab` | 3 | 0 | - | - |
| `UIBuildDes` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIBuildDes.prefab` | 16 | 1 | WorldTileBtnType | UI:UIResourceBag |
| `UIBuildDetailList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_BuildUpgrade/UIBuildDetailLis...` | 26 | 7 | BtnLock, OnSortToggleClick, OnTabToggleClick, UIToggle, curSortTo... | UI:UIBuildDetailList |
| `UIBuildDetails` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIBuildDetails.pr...` | 12 | 1 | - | - |
| `UIBuildList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_BuildUpgrade/UIBuildList.prefab` | 55 | 15 | WorldTileBtnType | UI:UIBuildList,UIMain |
| `UIBuildQueue` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIBuildQueuePanel.prefab` | 17 | 1 | - | - |
| `UIBuildQueueLease` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildQueue/UIBuildQueueLease.p...` | 18 | 6 | - | MSG:MsgDefines.UnlockBuildingQueue,MsgDefines.UserNewbieRobotUnlock ; UI... |
| `UIBuildQueueList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildQueue/UIBuildQueueList.pr...` | 13 | 2 | - | UI:self |
| `UIBuildTimeOfChange` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/SU_NewBuildUpgrade/UIUpgradeStat...` | 8 | 0 | - | - |
| `UIBuildUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIBuildUnlock.prefab` | 16 | 0 | - | - |
| `UIBuildUpUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpUnlock/UIBuildUpUnlock....` | 18 | 6 | - | UI:UIItemTips |
| `UIBuildUpgradeAddDes` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIBuildUpgradeAddDes.prefab` | 13 | 0 | - | - |
| `UIBuildUpgradeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIBuildUpgradeSuc...` | 11 | 1 | UIMainTopBtnType, hideBtnList | UI:noUseResetResource |
| `UIBuildUpgradeTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIUpgradeSuccess.prefab` | 7 | 1 | - | - |
| `UICameraInfo` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICameraInfo/UICameraInfo.prefab` | 12 | 1 | - | UI:self |
| `UICampBonus` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UICamp/UICampBonus.prefab` | 10 | 1 | - | UI:self |
| `UICampBonusMailTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICamp/UICampBonusMail.prefab` | 6 | 1 | - | UI:self |
| `UICampBonusMailTip4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICamp/UICampBonusMail.prefab` | 6 | 1 | - | - |
| `UICampPveHeroInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena/UICampPveHeroInfo.pr...` | 15 | 4 | - | UI:UIArenaPlayerArmy,UIOtherPlayerInfo,anim |
| `UICapacityAdd` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIMain/UICapacityAdd.prefab` | 12 | 2 | - | UI:self |
| `UICapacityBoxSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICapacity/UICapacityBoxSelect.p...` | 38 | 9 | Layout/Toggles/ToggleGroupSubTab/Toggle, ToggleControlBorS, UITog... | UI:UIBaubleInfo,UIHeroIntensifyInfo,self |
| `UICarChipActivityMonsterBossMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 22 | 5 | infoBtnN | UI:UIHeroTip,self |
| `UICarChipActivityMonsterBossReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 16 | 3 | - | MSG:MsgDefines.TaskRewardBatch |
| `UICarChipActivityPowerRankPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 16 | 2 | - | - |
| `UICarChipActivityUpcomingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 6 | 1 | OnButtonGotoClicked, Root/Btn, Root/Btn/btnText, UIButton, button... | UI:UIActivityCenterTable |
| `UICarChipBag` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipBag.prefab` | 5 | 2 | Music_Effect_Button, OnButtonCloseClicked, Root/CloseBtn, Root/To... | - |
| `UICarChipBox` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipBoxPopup.prefab` | 19 | 7 | Btns/Slider, Btns/TextDsc, Music_Effect_Button, UIButton, UICommo... | MSG:MsgDefines.ItemUse ; UI:UICapacityBoxSelect,UICommonItemProbabilityNew |
| `UICarChipDetailPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipDetailPopup....` | 6 | 3 | LayoutBtn/BtnDelete, LayoutBtn/BtnRefresh, LayoutBtn/BtnRefresh/R... | UI:UICarChipSelectChipPopup,UICarChipUpgradePopup |
| `UICarChipFormationPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipFormationPop...` | 7 | 4 | OnButtonModifyClicked, Tips/BtnClose, Tips/BtnGo, Tips/BtnGo/btnT... | UI:UIAircraftMain |
| `UICarChipGradingPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipGradingPopup...` | 6 | 1 | Music_Effect_Button, OnButtonCloseClicked, UIButton, UICommonPopU... | - |
| `UICarChipGradingUpgradePopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipGradingUpgra...` | 5 | 1 | Music_Effect_Button, OnButtonCloseClicked, UIButton, buttonClose | - |
| `UICarChipGuidePopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipGuidePopup.p...` | 2 | 0 | UIButton, UICommonActGuide/BtnClose, buttonClose | - |
| `UICarChipHandbookPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipHandbookPopu...` | 8 | 3 | OnButtonCloseClicked, OnToggleArmyTypeChanged, Root/ToggleGroupSu... | UI:UICarChipDetailPopup |
| `UICarChipItemProbability` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAircraft/UICarchipItemProbabil...` | 13 | 2 | Root/panel_01/title/BtnInfo, Root/panel_01/title/BtnInfo/Tips, Ro... | UI:self |
| `UICarChipMainTips` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipMainTips.prefab` | 9 | 0 | - | - |
| `UICarChipResetPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipResetPopupVi...` | 15 | 4 | BtnReset, BtnReset/btnText, OnButtonCloseClicked, OnButtonResetCl... | - |
| `UICarChipSelectCampPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipSelectCampPo...` | 6 | 3 | BtnGray, BtnGray/btnText, BtnSteup, BtnSteup/btnText, Camp/BtnCam... | UI:UICarChipSelectCampVX |
| `UICarChipSelectCampVX` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UIAircraftClipCampVie...` | 4 | 1 | - | UI:_ENV |
| `UICarChipSelectChipPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipSelectChipPo...` | 11 | 5 | Music_Effect_Button, OnButtonCloseClicked, ToggleGroupSubTab/Togg... | - |
| `UICarChipStarLevelUpPopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipStarLevelUpP...` | 4 | 1 | OnButtonCloseClicked, UIButton, buttonClose | - |
| `UICarChipUpgradePopup` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIAircraft/UICarChipUpgradePopup...` | 16 | 7 | Music_Effect_Button | UI:UICarChipBox,UICarChipDetailPopup |
| `UICarComponActivityMonsterBossMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 22 | 5 | infoBtnN | UI:UIHeroTip,self |
| `UICarComponActivityMonsterBossReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 16 | 3 | - | MSG:MsgDefines.TaskRewardBatch |
| `UICarComponActivityPowerRankPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarChipActivity/U...` | 16 | 2 | - | - |
| `UICarComponActivityUpcomingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/CarComponActivity...` | 6 | 1 | OnButtonGotoClicked, Root/Btn, Root/Btn/btnText, UIButton, button... | UI:UIActivityCenterTable |
| `UICarParkourSelect` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIParkour/UICarParkourSelect.prefab` | 16 | 3 | - | - |
| `UICarParkourWarning` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UICarParkourWarning.pr...` | 11 | 0 | - | - |
| `UICarnivalBulletScreen` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalBulletScre...` | 11 | 0 | - | - |
| `UICarnivalInfoWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalInfoWorld....` | 17 | 1 | - | UI:self |
| `UICarnivalLuckySpin` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalLuckySpin....` | 25 | 7 | buyBtnComp | UI:UICarnivalPreviewPopup,UICarnivalSendOption,UICarnivalSendWorld |
| `UICarnivalMomentMain` | `UIContainer/TopMost` | `Assets/Main/Prefabs/Slg/UI/UICarnival/UICarnivalMomentM...` | 41 | 8 | StopCloseBtnTimer, closeBtn, closeBtnTimer | UI:UICarnivalWorld,self |
| `UICarnivalPreviewPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalPreviewPop...` | 13 | 1 | - | UI:self |
| `UICarnivalSendOption` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalSendOption...` | 6 | 2 | - | UI:UICarnivalSendWorld,self |
| `UICarnivalSendWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalSendWorld....` | 23 | 11 | - | UI:UICarnivalLuckySpin,self |
| `UICarnivalWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UICarnivalWorld.prefab` | 19 | 7 | sendRedBtn | MSG:MsgDefines.GetRedPack ; UI:UICarnivalInfoWorld,self |
| `UIChainPay` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIChainPay/UIChainPay.prefab` | 24 | 7 | - | UI:self |
| `UIChainPayHalloween` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/HalloweenC...` | 24 | 7 | - | UI:self |
| `UIChampionBattleBattleInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 41 | 8 | Root/TodayGuess/p_BtnSelect, Root/ToggleGroupSubTab/p_Toggle1, Ro... | - |
| `UIChampionBattleCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/Group_expla...` | 10 | 2 | - | UI:self |
| `UIChampionBattleChampionView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 8 | 3 | - | UI:self |
| `UIChampionBattleGuessPopupView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/ChampionBat...` | 14 | 7 | OnCloseBtnClick | UI:UIChampionBattleGuessPopupView |
| `UIChampionBattleInvitationLetterView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 15 | 4 | - | UI:UIChampionBattleMain,self |
| `UIChampionBattleMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampionB...` | 50 | 10 | SetHideButtons, SetShowRankBtn, SetShowRecordBtn, ShowButtons, to... | UI:UIChampionBattleMain,UIChampionBattleRankView,UIChampionBattleReward4... |
| `UIChampionBattleManifestoView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 17 | 4 | - | UI:self |
| `UIChampionBattleRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 23 | 3 | - | UI:self |
| `UIChampionBattleReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 28 | 7 | - | UI:UIChampionBattleReward |
| `UIChampionBattleReward4Server` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/UIChampionB...` | 44 | 14 | goSubToggle, goToggleRedPoint3, toggle1, toggle1Sub, toggle2, tog... | UI:UIChampionBattleReward4Server |
| `UIChampionBattleRuleView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/ChampionBat...` | 16 | 2 | - | UI:self |
| `UIChampionpropaganda` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIChampionBattle/LFChampionp...` | 12 | 3 | - | UI:UIChampionpropaganda |
| `UIChangeAllianceCityName` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIChangeAllianceCityName.p...` | 23 | 6 | InitButtonState, Music_Effect_Button, Root/BigBtnBlue, Root/BigBt... | MSG:MsgDefines.WorldChangeAllianceCityName,MsgDefines.WorldCheckAlliance... |
| `UIChangeChatRoomName` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoom/UIChangeCha...` | 13 | 5 | InitButtonState, Music_Effect_Button, UIButton, btn_image, close_... | MSG:MsgDefines.AlName,MsgDefines.AllianceChangeAttributes ; UI:self |
| `UIChangeFriendName` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Friend/UIChangeFriendName.pr...` | 19 | 8 | Music_Effect_Button, UIButton, clear_btn, close_btn, return_btn, ... | MSG:MsgDefines.CheckFriendAlias,MsgDefines.SetFriendAlias ; UI:self |
| `UIChangeMail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIChangeMail.prefab` | 12 | 4 | - | UI:self |
| `UIChangeName` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIChangeName.prefab` | 17 | 6 | InitButtonState, Music_Effect_Button, UIButton, close_btn, return... | MSG:MsgDefines.NickNameChange,MsgDefines.NickNameCheck ; UI:self |
| `UIChangeNameGender` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIChangeNameGender....` | 30 | 9 | InitButtonState, UIButton, close_btn, return_btn, use_btn | MSG:MsgDefines.NickNameChange,MsgDefines.NickNameChangeFree,MsgDefines.N... |
| `UIChapterSwitch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatNew/UIChapterTransfer.prefab` | 10 | 2 | - | UI:anim |
| `UIChatCommanderTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatCommanderTips....` | 28 | 15 | _btnChatRestrict, _btnChatUnRestrict, _btnInviteN, addBtn, aliasB... | MSG:MsgDefines.AllianceInvitePlayer ; UI:UIAllianceDetail,UIOtherPlayerI... |
| `UIChatEmojiTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoom/UIChatEmoji...` | 10 | 4 | - | MSG:MsgDefines.ItemUse ; UI:self |
| `UIChatImgShow` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatImgShow.prefab` | 31 | 2 | Music_Effect_Button, OnClickReportBtn, UIButton, _btnBg, btnRepor... | UI:UIChatReport,self |
| `UIChatInviteToJoin` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatInviteToJoin/Cha...` | 30 | 9 | DefineToggle, Music_Effect_Button, OnInfoBtnClick, RefreshToggle,... | MSG:MsgDefines.CreateGroupChatCheck ; UI:anim |
| `UIChatItemOperatorView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatItemOperator/UIC...` | 29 | 13 | OnClickReportDataBtn, OnTranslationBtn, _btnAt, _btnCopy, _btnDow... | MSG:ChatMsgDefines.ChatRevert ; UI:UIChatReport,self |
| `UIChatJoinAllianceInform` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatJoinAllianceIn...` | 12 | 3 | - | MSG:MsgDefines.ChatStatisticsHandle ; UI:anim |
| `UIChatMomentMotivation` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatMo...` | 25 | 10 | extraBtnClaim, extraBtnGray, extraBtnInfo | UI:UIItemTips,self |
| `UIChatNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatNew.prefab` | 236 | 85 | ActivityToggleControlBorS, AddTreasureBtnRefreshTimer, AllianceTo... | MSG:MsgDefines.AlHelpAll,MsgDefines.VoteAllianceNotice ; UI:ChatAtMember... |
| `UIChatPlayerSetNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISetting/UIChatSet.prefab` | 35 | 17 | BTN_GRAY_PATH, BTN_NORMAL_PATH, UIButton, addFriendBtn, blockswit... | MSG:ChatMsgDefines.ChatLock,MsgDefines.AllianceInvitePlayer,MsgDefines.C... |
| `UIChatPrivateRoomSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatPrivateRoomSet/U...` | 20 | 10 | Music_Effect_Button, UIButton, _cp_avatorBtn, addFriendBtn, chang... | MSG:ChatMsgDefines.ChatLock,MsgDefines.AllianceInvitePlayer ; UI:UIOther... |
| `UIChatPrivateSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatPrivateSet.prefab` | 14 | 4 | - | UI:UIFriendFind,self |
| `UIChatRemoveMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRemoveMember/UIC...` | 24 | 5 | Music_Effect_Button, OnRemoveBtnClick, UIButton, btnText, btnText... | UI:anim |
| `UIChatReport` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIChatReport/UIChatReport.prefab` | 15 | 7 | RefreshReportBtn, YellowBtnShadowGrayColor, YellowBtnShadowLightC... | UI:self |
| `UIChatRoomManagerSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoomManagerSet/C...` | 19 | 4 | Music_Effect_Button, OnBtnClick, UIButton, addBtn, addBtnText, ad... | MSG:ChatMsgDefines.RoomGroupManagerAdd |
| `UIChatRoomPlayerTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoom/UIChatRoomP...` | 15 | 8 | - | UI:UIOtherPlayerInfo,self |
| `UIChatRoomSetting` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatRoom/UIChatRoomS...` | 32 | 10 | - | UI:UIChatInviteToJoin,UIChatKick,UIChatRemoveMember |
| `UIChatSetLevelLimit` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatSetLevelLimit/UI...` | 26 | 12 | Music_Effect_Button, UIButton, btnInfoBtn, btnInfoCloseMask, btnI... | MSG:MsgDefines.GolloesShareControl,MsgDefines.SetChatLevelLimit |
| `UIChatTrumpetPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatTrumpetPop.prefab` | 9 | 3 | UIButton, _closeBtn, close_btn_path | UI:self |
| `UIChatVoteCreat` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIChatVoteC...` | 30 | 7 | UIButton, UpdateBtnState, anonSwitchBtn, anon_help_btn, close_btn... | - |
| `UIChatVoteCreatTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIChatVoteC...` | 17 | 4 | BtnClose, UIToggle, root/ToggleGroupSubTab/Toggle1, root/ToggleGr... | UI:self |
| `UIChatVoteMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIChatVoteM...` | 12 | 2 | - | UI:anim |
| `UIChatVoteMemberInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIChatVoteM...` | 17 | 1 | - | - |
| `UIChatWorldShoutAtSomeOne` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatInviteToJoin/Cha...` | 30 | 9 | DefineToggle, Music_Effect_Button, OnInfoBtnClick, RefreshToggle,... | MSG:MsgDefines.CreateGroupChatCheck ; UI:anim |
| `UICheckAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceCheckList...` | 10 | 4 | Music_Effect_Button, UIButton, btnRank, btnRankTxt, close_btn, cl... | MSG:MsgDefines.AlSearch ; UI:UIRankDetailList,self |
| `UICheckServer` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIInterstellarMigration/UIInters...` | 21 | 7 | - | MSG:MsgDefines.GetMigrateItem ; UI:UIMigrateServer,self |
| `UIChoiceOfCommander` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UICho...` | 21 | 3 | BtnClick_Close | UI:self |
| `UIChooseServerAccountList` | `UIContainer/TopMost` | `Assets/Main/Prefabs/Debug_AccountList/UIChooseServerAcc...` | 12 | 5 | UIButton, closeBtnPath | UI:self |
| `UIChooseServerView` | `UIContainer/TopMost` | `Assets/Main/Prefabs/Slg/UI/UISetting/UIChooseServer.prefab` | 25 | 4 | - | MSG:MsgDefines.AccountGetAllServer ; UI:self |
| `UIChoseHeroMonthCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/HeroMonthCard/UIChoo...` | 16 | 1 | - | - |
| `UIChoseRollBySelf` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/WeeklyCardByM...` | 19 | 5 | - | UI:self |
| `UIChoseWeekCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/WeeklyCardByM...` | 17 | 2 | - | UI:self |
| `UIChristmasLevelRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasBlindBox...` | 17 | 3 | - | UI:self |
| `UIChristmasParkourMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIChristmasParkourView...` | 37 | 4 | barrel/sound_btn_back | - |
| `UIChristmasParkourResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIChristmasParkourResu...` | 22 | 6 | Music_Effect_Button | UI:UIPositionShare |
| `UIChristmasRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonate/U...` | 21 | 6 | ToggleControlBorS, UIButton, UIFoodFestivalPopUpTitle/Bg_mid/Clos... | UI:self |
| `UIChristmasRankRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasDonate/U...` | 19 | 7 | ToggleControlBorS, UIButton, UIFoodFestivalPopUpTitle/Bg_mid/Clos... | UI:self |
| `UICityAttackRank` | `UIContainer/Normal` | `Assets/SlgEngine/Main/Prefabs/UI/UICity/UICityAttackRan...` | 18 | 2 | Music_Effect_Button | UI:UIRuinsRankDetail |
| `UICityBattleActivityPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UICityBattleActivityPo...` | 19 | 7 | Music_Effect_Button, actionBtnText | UI:UIHeroInfo |
| `UICityMainTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/CityManage/UICityMainTips.prefab` | 11 | 2 | - | UI:OpenWinAnimTrue |
| `UICityManage` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CityManage/UIFormationCityBu...` | 16 | 4 | - | UI:GetInstance,anim |
| `UICityWarBookAdjustAssemblyPoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UICityWarBookAdjustAss...` | 1 | 0 | - | - |
| `UICityWarBookSuccessDialogPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UICityWarBookSuccessDi...` | 6 | 1 | - | - |
| `UICityWeather` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/UICityWeather/UICityWeather.prefab` | 12 | 1 | - | UI:self |
| `UICollectReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICollectReward/UICollectReward....` | 20 | 4 | - | MSG:MsgDefines.GatherCollectReward ; UI:UICapacityFull,self |
| `UICombatActivityPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecorationGift/UIDecorationGif...` | 11 | 4 | - | UI:UICombatActivityPop |
| `UICommandPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UICom...` | 16 | 4 | btnInfo, toggle, toggleList | UI:UIItemTips,self |
| `UICommon18PlusPopupAge` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Common/UICommon18PlusPopupAge.pr...` | 5 | 2 | Music_Effect_Button, OnCloseBtnClick, OnGoBtnClick, Panel/bg_mid/... | - |
| `UICommon18PlusPopupEmail` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Common/UICommon18PlusPopupEmail....` | 12 | 6 | Music_Effect_Button, OnCloseBtnClick, OnDoAuthBtnClick, OnDoBtnCl... | - |
| `UICommonActivityTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICommonActivityTask/UICommonAct...` | 12 | 1 | - | - |
| `UICommonAttrTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonAttrTip.prefab` | 13 | 1 | - | UI:self |
| `UICommonBuyItem` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonBuyItem.prefab` | 16 | 4 | Music_Effect_Button, OnBtnClick, UIButton, btn, btnPrice_1_txt, b... | UI:UIItemTips,anim |
| `UICommonChangeValue` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonChangeValue.prefab` | 7 | 1 | - | - |
| `UICommonCostConfirm` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonCostConfirm.prefab` | 10 | 2 | - | UI:self |
| `UICommonCountTimeMessageTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonCountTimeMessageT...` | 17 | 4 | - | UI:self |
| `UICommonCredit` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CreditSystem/UICommonCredit....` | 15 | 4 | - | UI:anim,self |
| `UICommonCredit2` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CreditSystem/UICommonCredit2...` | 12 | 1 | - | - |
| `UICommonDesTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonDesTip.prefab` | 5 | 1 | - | UI:self |
| `UICommonGuideTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UICommonGuideTalk.prefab` | 43 | 12 | OnBtnClick, OnSevenDayNoteBtnClick, RefreshAutoBtn, UIButton, sev... | UI:anim |
| `UICommonHeadTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonHeadTip.prefab` | 12 | 1 | - | UI:self |
| `UICommonIntro2` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonActGuide.prefab` | 11 | 2 | - | UI:self |
| `UICommonIntroTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonIntroTip.prefab` | 21 | 7 | BtnClick_Cancel, BtnClick_Config, Content/BtnRoot, Content/BtnRoo... | UI:self |
| `UICommonIntroTipActGivingRoses` | `UIContainer/Dialog` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UICommonIntroTipA...` | 16 | 2 | Music_Effect_Button | UI:self |
| `UICommonIntroWorldCityDeclare` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/World/UICommonIntroWorldCity...` | 5 | 1 | - | UI:self |
| `UICommonItemProbability` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonItemProbability.p...` | 12 | 4 | Music_Effect_Button, UIButton, UICommonMidPopUpTitle/CloseBtn, cl... | UI:self |
| `UICommonItemProbabilityNew` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonItemProbabilityNe...` | 10 | 2 | Music_Effect_Button, UIButton, UICommonMidPopUpTitle/bg_mid/Close... | UI:self |
| `UICommonKVTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Common/UICommonKVTip/UICommo...` | 7 | 0 | - | - |
| `UICommonMessageBar` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/UICommonMessageBar.prefab` | 23 | 3 | UIButton, closeBtnN, closeBtn_path | UI:anim |
| `UICommonMessageSpecialBar` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonMessageSpecialBar...` | 14 | 2 | UIButton, closeBtnN, closeBtn_path | UI:anim |
| `UICommonMessageTip` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/UICommonMessageTip.prefab` | 12 | 3 | UIButton, btnGoN, btnRoot_path, btn_1, btn_1_path, btn_1_txt | UI:anim |
| `UICommonMessageTipBig` | `UIContainer/TopCanvas` | `Assets/Main/Prefabs/UI/Common/UICommonMessageTip5.prefab` | 12 | 3 | UIButton, btnGoN, btnRoot_path, btn_1, btn_1_path, btn_1_txt | UI:anim |
| `UICommonModal` | `UIContainer/TopCanvas` | `Assets/Main/Prefabs/UI/Common/UICommonModal.prefab` | 12 | 3 | UIButton, btnGoN, btnRoot_path, btn_1, btn_1_path, btn_1_txt | UI:anim |
| `UICommonResourceComfirmView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonResourceComfirm.p...` | 16 | 7 | OnCloseBtnClick | UI:UICommonResourceComfirmView |
| `UICommonRuleImg` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonRuleImg.prefab` | 5 | 0 | - | - |
| `UICommonShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICommonShop/UICommonShop.prefab` | 36 | 16 | GOLD_BTN_ORDER_MULTI_BUY, GOLD_BTN_ORDER_NORMAL, RefreshToggleRed... | UI:UIGiftPackage,UIMultiBuy,anim |
| `UICommonSingleMsgBar` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonSingleMsgBar.prefab` | 5 | 2 | - | UI:anim |
| `UICommonTextTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonTextTips.prefab` | 8 | 1 | - | UI:self |
| `UICommonTipView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonTips.prefab` | 5 | 1 | goto_btn | UI:self |
| `UICommonTipWithNoMind` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonMessageTip4.prefab` | 14 | 3 | BtnClick_Close | - |
| `UICommonUseItemTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonUseItemTip.prefab` | 17 | 4 | - | UI:self |
| `UICommonUseResItemTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonUseResItemTips.pr...` | 23 | 5 | Music_Effect_Button, OnBtnClick, UIButton, add_btn, btn, btn_2 | MSG:MsgDefines.ItemUse ; UI:UIItemTips,anim |
| `UICommonWait` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonWaiting.prefab` | 9 | 0 | - | - |
| `UICompletePoliceStation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICompletePoliceStation/UIComple...` | 4 | 0 | - | - |
| `UICompletePoliceStationUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICompletePoliceStation/UIComple...` | 4 | 0 | - | - |
| `UIComplexTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIComplexTip/UIComplexTip.prefab` | 14 | 2 | - | UI:anim |
| `UIConcertListView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIConcert/UIConcertListView.prefab` | 16 | 1 | - | UI:self |
| `UIConcertPositionShareConfirmView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIConcert/UIConcertPositionShar...` | 10 | 3 | Music_Effect_Button, OnClickConfirmBtn, UIButton, btnYesCost, btn... | MSG:MsgDefines.ConcertShare ; UI:self |
| `UIConcertPositionShareView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIConcert/UIConcertPositionShar...` | 14 | 4 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | UI:UIConcertPositionShareConfirmView,self |
| `UIConcertRateView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIConcert/UIConcertRateView.prefab` | 14 | 1 | - | UI:self |
| `UIConcertTipView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIConcert/UIConcertTipView.prefab` | 12 | 1 | - | UI:self |
| `UIConsumeItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMoveCityTip/UIConsumeItem.prefab` | 18 | 5 | - | MSG:MsgDefines.AllianceMoveCity ; UI:anim |
| `UICreateAccount` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UICreateAccount.prefab` | 15 | 3 | - | MSG:MsgDefines.AccountBind ; UI:self |
| `UICreateAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UICreateAlliance.prefab` | 5 | 0 | - | - |
| `UICreateSetAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UICreateSetAlliance.prefab` | 4 | 1 | - | UI:UIAllianceFlag |
| `UICreditMainPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CreditSystem/CreditMainPanel...` | 19 | 5 | infoBtn | UI:UISettingAccount,anim |
| `UICreditMainPanel2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundAccountAnomaly....` | 19 | 7 | btnInfo | UI:UIAddAccount,UICommonCredit2,UIItemTips |
| `UICreditTip` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UICreditTip/UICreditTip.prefab` | 10 | 2 | - | UI:GetInstance |
| `UICrossDisconnect` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UICrossDisconnectView.prefab` | 13 | 4 | - | UI:self |
| `UICrossServerList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UIServerList.prefab` | 21 | 4 | - | UI:self |
| `UICrossWonderAct` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 44 | 17 | IsRecordBtnVisible, LastClickMailBtn, Music_Effect_Button, OnMail... | UI:UICrossWonderBadge,UICrossWonderHistory,UICrossWonderReward |
| `UICrossWonderActLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderActLo...` | 18 | 4 | BtnInfo, Music_Effect_Button | UI:UIHeroTip |
| `UICrossWonderActRankList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 16 | 5 | infobtn | UI:UIHeroTip |
| `UICrossWonderActRewardPopup` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 15 | 4 | - | - |
| `UICrossWonderBadge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 11 | 0 | - | - |
| `UICrossWonderCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonderCollect/UICrossWond...` | 18 | 4 | - | MSG:MsgDefines.WorldGetDetail |
| `UICrossWonderContributeRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 11 | 2 | - | UI:self |
| `UICrossWonderCountdownPanel` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 12 | 2 | - | - |
| `UICrossWonderHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 12 | 2 | - | - |
| `UICrossWonderMarkRemindNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMainNotice/UICrossWonderMarkNo...` | 24 | 7 | Music_Effect_Button | UI:self |
| `UICrossWonderMoveCityTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 3 | 1 | - | - |
| `UICrossWonderPointRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 14 | 2 | - | UI:self |
| `UICrossWonderPreviewRule1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 11 | 2 | Music_Effect_Button | UI:UICrossWonderPreviewRule2,self |
| `UICrossWonderPreviewRule2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 20 | 3 | _toggleCheckTxts | UI:self |
| `UICrossWonderRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderRank/...` | 17 | 3 | - | UI:self |
| `UICrossWonderReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderRewar...` | 9 | 1 | - | UI:self |
| `UICrossWonderRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderRule/...` | 7 | 0 | - | - |
| `UICrossWonderTarget` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderTarge...` | 17 | 3 | - | MSG:MsgDefines.TaskRewardGet ; UI:self |
| `UICycleBoxExchangeView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UICycleBox/UICycleBoxExchang...` | 17 | 3 | - | UI:self |
| `UICycleBoxRewardPreView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UICycleBox/UICycleBoxRewardP...` | 23 | 4 | BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `UICycleBoxScoreRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UICycleBox/UICycleBoxScoreRe...` | 17 | 3 | - | UI:self |
| `UIDailyActivity` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIDailyActivity/UIDailyActivity....` | 16 | 4 | - | UI:anim |
| `UIDailyPackageChangePanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/DailyPackage/New/UID...` | 27 | 8 | btnNum, toggle, toggleAction, toggleText | MSG:MsgDefines.DailyPackageSelectHero ; UI:UIHeroSPEquip,self |
| `UIDawnTaskProgressReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDawnTaskPanel/U...` | 10 | 2 | UIButton, closeBtn | - |
| `UIDeadArmyRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIDeadArmyRecord.prefab` | 17 | 2 | - | UI:self |
| `UIDebugChooseServer` | `UIContainer/TopMost` | `Assets/Main/Prefabs/Debug_ChooseServer/UIDebugChooseSer...` | 33 | 9 | SyncProtocalToggle, ToggleControlBorS, UIButton, back_toggle, con... | UI:self |
| `UIDeclareWarCountDownTitle` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/UIGlory/UIDeclareWarCountDownTit...` | 6 | 1 | - | - |
| `UIDeclareWarList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIDeclareWarList.prefab` | 14 | 1 | - | UI:self |
| `UIDecorateUnlock` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorateUnlock.pr...` | 20 | 2 | - | UI:self |
| `UIDecorationEffect` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationEffect....` | 15 | 1 | - | UI:self |
| `UIDecorationGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecorationGift/UIDecorationGif...` | 14 | 2 | - | UI:UIActivityCenterTable,self |
| `UIDecorationMain` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationMainVie...` | 69 | 21 | Music_Effect_Button, RefreshBtn, city_toggle, onSkinBtnCallBack, ... | MSG:MsgDefines.GetSnowManActInfo ; UI:UIDecorationEffect,UIDecorationUpg... |
| `UIDecorationUpgradeInfoPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationUpgrade...` | 11 | 0 | - | - |
| `UIDecorationUpgradePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationUpgrade...` | 17 | 5 | Music_Effect_Button, OnButtonCloseClicked, OnButtonInfoClicked, R... | UI:UIDecorateUnlock,UIDecorationUpgradeInfoPopup |
| `UIDecorationUpgradeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorationUpgrade...` | 10 | 2 | Ani/bgBtn, Ani/continueBtn/countinueTxt, Music_Effect_Button, OnB... | - |
| `UIDeleteAccountConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UIDeleteAccountConfirm...` | 15 | 3 | btnSubmit | MSG:MsgDefines.BindCancelVerifyCode,MsgDefines.UserBindCancel ; UI:self |
| `UIDeleteAccountIntro` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UIDeleteAccountIntro.p...` | 28 | 8 | - | MSG:MsgDefines.UserBindCancel ; UI:UIDeleteAccountConfirm,self |
| `UIDeleteAccountIntroNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UIDeleteAccountIntroNe...` | 19 | 6 | delete_btn | MSG:MsgDefines.UserBindCancelNew ; UI:UIDeleteAccountConfirm,self |
| `UIDeleteAccountNotice` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIDeleteAccountNotice....` | 11 | 2 | - | UI:UIDeleteAccountIntro,self |
| `UIDeleteAccountNoticeNew` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIDeleteAccountNoticeN...` | 17 | 5 | - | MSG:MsgDefines.UserBindCancelNew ; UI:UIRoles,self |
| `UIDemolishChangeConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDemolish/UIDemolishChangeConfi...` | 27 | 7 | btnAccept, btnRefuse | UI:UIDemolishChangeLog,UIDemolishSelectMember |
| `UIDemolishChangeLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDemolish/UDemolishChangeLog.pr...` | 12 | 2 | - | - |
| `UIDemolishSelectMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDemolish/UIDemolishSelectMembe...` | 19 | 6 | toggleArenaPower | - |
| `UIDemonHunterEntrust` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/DemonHunt...` | 21 | 9 | btnNum | MSG:MsgDefines.SubmitDemonHunterQuest ; UI:self |
| `UIDemonHunterMapPointTips` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/DemonHunt...` | 14 | 3 | - | - |
| `UIDemonHunterMonsterSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/DemonHunt...` | 19 | 4 | showGotoBtn | UI:self |
| `UIDemonHunterRadar` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/DemonHunt...` | 12 | 4 | - | UI:self |
| `UIDemonHunterTalk` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/DemonHunt...` | 18 | 6 | - | MSG:MsgDefines.SubmitDemonHunterQuest ; UI:UIDemonHunterMonsterSelect,self |
| `UIDesertForceList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonForceList/UISea...` | 18 | 1 | - | - |
| `UIDesertOperate` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDesertOperate/UIDesertOperate....` | 16 | 1 | - | - |
| `UIDesertOperateBuffList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDesertOperateBuffList/UIDesert...` | 13 | 0 | - | - |
| `UIDetectEvent` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRadarCenter/UIDetectEvent.prefab` | 116 | 32 | CompleteAllBtnClickTimer, GetAllRewardBtnClickTimer, Music_Effect... | MSG:MsgDefines.BatchDetectEventRewardReceive,MsgDefines.ClickCreateTreas... |
| `UIDetectEventLevelUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRadarCenter/UIDetectEventLevel...` | 7 | 2 | - | - |
| `UIDetectEventPowerUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRadarCenter/UIDetectEventPower...` | 11 | 3 | - | UI:self |
| `UIDetectHelpMessageBar` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIDetectHelpMessageBar.pr...` | 16 | 1 | UIButton, closeBtnN, closeBtn_path | - |
| `UIDetectNpc` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRadarCenter/UIDetectNpcEvent.p...` | 19 | 7 | - | MSG:MsgDefines.SU_ActCityPeople ; UI:UISmallPeopleReward |
| `UIDetectNpcDinosaurRescue` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurR...` | 22 | 8 | rewardBtn | MSG:MsgDefines.SU_ActCityPeople ; UI:UIItemTips |
| `UIDigActivityRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIGiftBox...` | 17 | 6 | toggleList | UI:self |
| `UIDigLevelReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDigLevelReward/UIDigLevelRewar...` | 14 | 0 | - | - |
| `UIDigReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDigReward/UIDigReward2.prefab` | 17 | 6 | ToggleControlBorS_1, ToggleControlBorS_2, toggleList | UI:self |
| `UIDisconnect` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Common/DisconnectView.prefab` | 27 | 4 | - | - |
| `UIDispatchRewardGet` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/UIAc...` | 24 | 2 | - | UI:EventManager |
| `UIDomeUpdate` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIDomeUpdate.prefab` | 8 | 4 | Music_Effect_Button, UIButton, cancel_btn, cancel_btn_path, close... | UI:self |
| `UIDonateSoldierInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldier/U...` | 22 | 6 | - | UI:UIActivityCenterTable,UIAllianceWarPersonalList,self |
| `UIDonateSoldierOpenReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldier/U...` | 16 | 4 | - | UI:self |
| `UIDonateSoldierRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldier/U...` | 17 | 5 | SetToggleChoose, toggle | UI:self |
| `UIDonateSoldierReservation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldier/U...` | 23 | 3 | - | - |
| `UIDonateSoldierReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldier/U...` | 24 | 9 | CheckBtnState, get_advance_reward_btn, get_advance_reward_btn_lab... | MSG:MsgDefines.ReceiveDonateArmyStageReward ; UI:UIDonateSoldierOpenRewa... |
| `UIDonateSoldierSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIDonateSoldier/U...` | 33 | 5 | - | MSG:MsgDefines.DonateArmy ; UI:self |
| `UIDownloadProgress` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Survival/UIDownloadProgress.prefab` | 9 | 2 | - | UI:self |
| `UIDragoMemberSwapConfig` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 24 | 4 | - | UI:UIDragonMessageTip |
| `UIDragonActionRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 18 | 2 | - | - |
| `UIDragonBattleResult` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonBattleResult.pr...` | 9 | 4 | Music_Effect_Button, OnReturnBtnClick, UIButton, return_btn, retu... | MSG:MsgDefines.ExitDragonServer ; UI:UIArrow,anim |
| `UIDragonBattleScore` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonAllianceScore.p...` | 22 | 6 | UIButton, close_btn, return_btn | MSG:MsgDefines.ExitDragonServer ; UI:UIActDragonRule |
| `UIDragonCommand` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Battlefield/UIDragonCommand.prefab` | 18 | 3 | - | UI:self |
| `UIDragonEggHatch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 28 | 8 | Root/ActivityTopRightBtns, dragonEggBtns | UI:UIActivityCenterTable,UIDragonEggPreview |
| `UIDragonEggPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 24 | 12 | Btns/BtnGet, Btns/BtnGet/btnText, OnClickCloseBtn, SelectStage/Bt... | UI:UISeason4DinosaurEggHatchConfirm,self |
| `UIDragonExplainCommand` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonExplain_Command...` | 15 | 3 | isShowToggle, toggle, toggleTxt | - |
| `UIDragonExplainPlay` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonExplain_Play.pr...` | 17 | 4 | isShowToggle, toggle, toggleTxt | - |
| `UIDragonExplainSign` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonExplain_Sign.pr...` | 15 | 3 | isShowToggle, toggle, toggleTxt | - |
| `UIDragonHistoryScore` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonHistoryScore.pr...` | 16 | 2 | - | - |
| `UIDragonMark` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIDragonMark.prefab` | 15 | 4 | BtnClick_Close | UI:self |
| `UIDragonMemberSwap` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 10 | 2 | - | - |
| `UIDragonMemberSwapRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 16 | 3 | - | - |
| `UIDragonMemberSwapSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DragonAct/UIActDr...` | 19 | 4 | toggleArenaPower | - |
| `UIDragonMessageTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonMessageTip2.prefab` | 14 | 3 | BtnClick_Close | - |
| `UIDragonMoveCityConform` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Battlefield/UIBattlefieldCityMov...` | 16 | 4 | BtnClick_Close | UI:self |
| `UIDragonSelectMemberAllinOne` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonSelectMemberTea...` | 50 | 17 | BtnClick_SwitchPower, CheckTeamToggle, CheckToggle, RefreshSortFi... | MSG:MsgDefines.AlArenaPower ; UI:UIDragonExplainSign,UIDragonSelectMembe... |
| `UIDragonSelectMemberNoTeam` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonAllianceSelectM...` | 34 | 9 | BtnClick_SwitchPower, btnExplain, switchBtnRoot | MSG:MsgDefines.AlArenaPower ; UI:UIDragonExplainSign |
| `UIDragonSelectMemberSortFilter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonSelectMemberFil...` | 28 | 12 | InitTimeToggles, RefreshTimeTypeBtnUI, _notVotedBtnItem, _timeBtn... | - |
| `UIDragonSelectMemberTeam` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDragon/UIDragonSelectMemberTea...` | 37 | 11 | BtnClick_SwitchPower, CheckToggle, btnExplain, switchBtnRoot, tea... | MSG:MsgDefines.AlArenaPower ; UI:UIDragonExplainSign |
| `UIDrakaBoss2Pre` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DrakeBoss/UIVivie...` | 17 | 4 | btn_goto | - |
| `UIDrakeBossAutoJoinTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DrakeBoss/UIDrake...` | 13 | 1 | - | UI:self |
| `UIDrakeBossRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DrakeBoss/UIDrake...` | 24 | 2 | - | UI:self |
| `UIDrakeBossUseItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIItem/UIDrakeBossUseItem.prefab` | 19 | 5 | - | MSG:MsgDefines.ItemUse ; UI:self |
| `UIDroppedTreasureTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DroppedTreasure/U...` | 12 | 1 | toggle | - |
| `UIDynamicRewardRate` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIDynamicRewardRate/UIDynamicRew...` | 24 | 1 | - | UI:self |
| `UIEasterBlindBoxLevelRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIEaster/UIEasterBlindBox/UIEas...` | 18 | 3 | - | UI:UIEasterBlindBoxLevelRewardPanel |
| `UIEasterBlindBoxRuleView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIEaster/UIEasterBlindBox/UIEas...` | 14 | 3 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:UIEasterBlindBoxRuleView |
| `UIEasterExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIEaster/UIEasterExchangeShop/U...` | 18 | 6 | isMaxBtn, maxBtnN | UI:UIEasterExchangeShopBuy |
| `UIEditDragonCommandMsg` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UIEdi...` | 15 | 3 | BtnClick_Close | UI:UIEditDragonCommandMsg |
| `UIEmojiSettingPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIEmojiSetting/UIEmojiSettingPan...` | 25 | 7 | Music_Effect_Button | MSG:MsgDefines.SetEmoji ; UI:UIEmojiSettingPanel |
| `UIEmojiSettingStateTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIEmojiSetting/UIEmojiSettingSta...` | 25 | 12 | Music_Effect_Button, OnCloseBtnClick, ShowBtn, UpdateBtnState, Up... | MSG:MsgDefines.ItemUse ; UI:UIEmojiSettingPanel,self |
| `UIEnergyBank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIEnergyBank/UIEnergyBank.prefab` | 12 | 2 | - | UI:self |
| `UIEnergyBankTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIEnergyBank/UIEnergyBankTip.prefab` | 19 | 3 | - | UI:UIGiftPackage,self |
| `UIEquipBreakSkillTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIEquipBreakSkillTip....` | 12 | 1 | - | UI:self |
| `UIExchangeConfirmView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIMatchingGame/UI...` | 9 | 2 | - | UI:self |
| `UIExchangeRecordView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIMatchingGame/UI...` | 20 | 8 | Music_Effect_Button, OnClickToggle, toggles | UI:self |
| `UIExchangeView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIMatchingGame/UI...` | 13 | 7 | - | UI:UIExchangeRecordView,self |
| `UIFadeBlack` | `UIContainer/Normal` | `Assets/Main/Prefabs/Guide/UIFadeBlack.prefab` | 17 | 1 | - | UI:anim |
| `UIFinalWaveTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIFinalWaveTip.prefab` | 2 | 1 | - | UI:self |
| `UIFingerArrow` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIArrowFinger.prefab` | 18 | 2 | - | UI:self |
| `UIFirstCharge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstCharge/UIFirstCharge.prefab` | 8 | 2 | - | UI:self |
| `UIFirstCharge2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstCharge/UIFirstCharge2.prefab` | 6 | 0 | - | - |
| `UIFirstChargeTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstCharge/UIFirstChargeTip.p...` | 14 | 5 | - | UI:self |
| `UIFirstPay` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIFirstPay/UIFirstPay.prefab` | 13 | 5 | - | UI:self |
| `UIFirstPayNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstPay/UIFirstPayNew.prefab` | 14 | 1 | - | - |
| `UIFirstPayNewNvJing` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstPay/UIFirstPayNewNvJing.p...` | 26 | 7 | boxBtn | UI:UINewNvJingBuyResult,UIRewardVListTip |
| `UIFishRewardGet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/Fis...` | 26 | 3 | - | UI:UIFishRewardGet |
| `UIFishingCatalogDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/UIFishingCatalo...` | 24 | 3 | Music_Effect_Button | MSG:MsgDefines.SeasonGoldActiveFish ; UI:self |
| `UIFishingCatalogGiftHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/GiftHistory/UIF...` | 14 | 6 | DefineToggles, Music_Effect_Button, ToggleControlBorS, UIButton, ... | MSG:MsgDefines.GetSendFishRecord ; UI:anim |
| `UIFishingCatalogGiveGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/GiveGift/UIFish...` | 29 | 6 | - | MSG:MsgDefines.SendContactGiftSearch ; UI:anim |
| `UIFishingCatalogGiveGiftSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/GiveGift/UIFish...` | 12 | 3 | - | UI:noticeType |
| `UIFishingCatalogMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/UIFishingCatalo...` | 38 | 8 | GetShowBtnState, UnlockBtnLockType, UnlockBtnManager, UnlockBtnTy... | UI:UIGiftPackage,anim |
| `UIFishingCatalogUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFishingCatalog/UIFishingCatalo...` | 22 | 4 | - | UI:self |
| `UIFiveStarFeedBack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMain/UIFiveStarFeedBack.prefab` | 10 | 4 | Music_Effect_Button, UIButton, close_btn, close_btn_path, return_... | MSG:MsgDefines.FiveStar ; UI:self |
| `UIFiveStarGet` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMain/UIFiveStarGet.prefab` | 11 | 2 | - | UI:UIFiveStarFeedBack |
| `UIFlipFunHelpList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIMatchingGame/UI...` | 13 | 4 | - | UI:self |
| `UIFlipFunMainview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIMatchingGame/UI...` | 30 | 6 | btnBtnStart, btnShare | UI:UIFlipFunHelpList,UIFlipFunMainview |
| `UIFoodFestivalEatExchangeView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIFoodFestivalEat/UIFoodFestiva...` | 17 | 3 | - | UI:self |
| `UIFoodFestivalEatPreviewTipView` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UIFoodFestivalEat/UIFoodFestiva...` | 16 | 2 | - | UI:self |
| `UIFoodRedenvelopeSelectView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/FoodFestivalRedEnv...` | 15 | 2 | ImgBg/BigBtnChoose, ImgBg/BigBtnChoose/btnText, Music_Effect_Butt... | - |
| `UIForcesDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIForcesDetail/UIForcesDetail.pr...` | 16 | 5 | Common_btn_tab_down, Common_btn_tab_up, UIForcesDetail_btn_detail... | UI:UIPlayerInfo,anim |
| `UIForgetPassword` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIForgetPassword.prefab` | 13 | 5 | - | MSG:MsgDefines.AccountForgetPassword ; UI:UIAddAccount,self |
| `UIFormationAddStamina` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationAddStamin...` | 31 | 8 | CloseMoreBtn, GetMoreBtnParent, Music_Effect_Speed_Button, ShowMo... | MSG:MsgDefines.ItemUse ; UI:UIFormationTip,self |
| `UIFormationArena3V3New` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIArena3v3/UIArena3V3Formati...` | 139 | 40 | Music_Effect_Button, RefreshBottomBtns, _campToggleBtns, _toggleB... | UI:UIArmyTips2,UICampBonus,UIFormationArena3V3New |
| `UIFormationAssistance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormationDefence/UIFormationAs...` | 40 | 3 | info_btn | UI:UIItemTips |
| `UIFormationBuff` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIFormationDefence/UIFormati...` | 18 | 2 | - | UI:anim |
| `UIFormationBuffInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIGarrisonCityWallPo...` | 28 | 4 | - | UI:UIWarGuardLog,anim |
| `UIFormationDefenceNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormationDefence/UIFormationDe...` | 27 | 7 | CAMP_BTN_BASE_Y, CAMP_BTN_DEFENSE_OFFSET_Y, RESTRAINT_BTN_BASE_Y,... | UI:UICampBonus,UIFormationRestraint |
| `UIFormationDefenceTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIFormationDefence/UIFormati...` | 96 | 30 | TOGGLE_FORMATION_DIFF, _campBtn, _restraintBtn, _soldierInfoBtn, ... | MSG:MsgDefines.AssistanceTeamRetreat ; UI:OpenWinAnimFalse,UIArmyTips,UI... |
| `UIFormationDispatchTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroOfferReward1.pr...` | 28 | 9 | rarity_btn | MSG:MsgDefines.DispatchStart ; UI:UIHeroTip,self |
| `UIFormationDispatchTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/Form...` | 14 | 1 | - | UI:self |
| `UIFormationLackPower` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIFormationLackPower.prefab` | 12 | 2 | - | UI:self |
| `UIFormationOfBattlefield` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UIFor...` | 15 | 4 | btnInfo, toggle, toggleList | UI:UIFormationOfBattlefield,UIItemTips |
| `UIFormationOfBattlefieldNoTeam` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UIFor...` | 14 | 3 | btnInfo, toggle, toggleList | UI:UIItemTips |
| `UIFormationOfBattlefieldTeam` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UIFor...` | 20 | 8 | BtnClick_Cancel, CheckTeamBtn, ToggleControlBorS, btnInfo, btnSwi... | UI:UIItemTips |
| `UIFormationRestraint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationRestraint...` | 9 | 3 | - | UI:self |
| `UIFormationSelectListNew` | `UIContainer/Normal` | `-` | 118 | 21 | Music_Effect_Button, OnClickExchangeBtn, OnSelectTroopBtnClick, U... | UI:UIFormationTableNew,self |
| `UIFormationShare` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationSharePopU...` | 12 | 6 | Music_Effect_Button, UIButton, atk_btn, camp_btn, close_btn, clos... | UI:UICampBonus,UIHeroTip,self |
| `UIFormationSoldierChoose` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationSoldierCh...` | 21 | 5 | Music_Effect_Button, UIButton, one_key_btn, one_key_btn_path, ret... | UI:self |
| `UIFormationState` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationStateNew....` | 7 | 2 | UIButton, return_btn, return_btn_path | UI:self |
| `UIFormationTableNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFormation/UIFormationTableNewP...` | 134 | 39 | Music_Effect_Button, RefreshBottomBtns, Root/UICarChipFormationBt... | UI:UIArmyTips2,UICampBonus,UIFormationRestraint |
| `UIFormationTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIFormationTip.prefab` | 11 | 1 | - | UI:self |
| `UIFormationofBattlefieldCommand` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UIFor...` | 21 | 4 | toggle, toggleList | UI:self |
| `UIFoxHello` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Ti...` | 13 | 1 | - | UI:self |
| `UIFriendApply` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Friend/UIFriendApply.prefab` | 19 | 5 | - | UI:self |
| `UIFriendFindView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Friend/UIFriendFind.prefab` | 19 | 5 | - | MSG:MsgDefines.SendContactGiftSearch ; UI:self |
| `UIFrozenLandIntroduce` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/FrozenLan...` | 21 | 3 | toggle | UI:self |
| `UIFrozenLandPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/FrozenLan...` | 19 | 2 | ToggleOutlineRenderFeature | UI:UIFrozenLandIntroduce,self |
| `UIFrozenLandSaveRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/FrozenLan...` | 15 | 3 | - | UI:UIFrozenLandPreview |
| `UIFullScreenBlackBG` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/UIPVE/UIFullScreenBlackBG.prefab` | 4 | 3 | - | UI:self |
| `UIFullScreenTranslationPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/UIFullScreenTranslat...` | 4 | 0 | - | - |
| `UIGGUnBindAccount` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UISettingLinke.prefab` | 8 | 4 | - | MSG:MsgDefines.GameCenterUnBind |
| `UIGameCenterChangeBind` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISetting/UIGameCenterChangeBind...` | 12 | 3 | - | UI:self |
| `UIGarbageRewardShow` | `UIContainer/Normal` | `Assets/Main/Prefabs/CityScene/UIGarbageRewardShow.prefab` | 16 | 4 | - | UI:OpenWinAnimTrue |
| `UIGetDress` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroDress/UIGetDressView.prefab` | 11 | 0 | - | - |
| `UIGetPickaxe` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGetPickaxe/UIGetPickaxe.prefab` | 20 | 6 | - | UI:UIActivityCenterTable,ctrl,self |
| `UIGetPolicewoman` | `UIContainer/Normal` | `Assets/Main/Prefabs/Guide2/UIGuideTalk5NvJing.prefab` | 3 | 0 | - | - |
| `UIGetRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/UIGetRewardView.prefab` | 23 | 2 | - | UI:self |
| `UIGiftBoxPackageList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIGiftBox...` | 16 | 7 | Music_Effect_Button, UIButton, UICommonMidPopUpTitle/CloseBtn, _c... | UI:self |
| `UIGiftBoxProgressReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIGiftBox...` | 11 | 3 | UIButton, closeBtn | UI:self |
| `UIGiftBoxRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GiftBox/UIGiftBox...` | 17 | 7 | ToggleGroupSubTab/Toggle1, ToggleGroupSubTab/Toggle1/checkText1, ... | UI:UIPlayerInfo,self |
| `UIGiftPackage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/GiftPackage/UIGiftPackagePopUpVi...` | 66 | 13 | GetGoldBricksPayBtnShow, GetTypeButtonList, GotoButtonType, btnSw... | UI:UIThirdPaymentShop,self |
| `UIGiftPackageRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/GiftPackage/UIGiftPackageRewardG...` | 26 | 2 | - | UI:EventManager |
| `UIGiftPackageRewardSelect` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/GiftPackage/UIGiftPackageRewardS...` | 17 | 5 | _use_btn | UI:self |
| `UIGiftPackageSelfSelect` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIGiftPackageSelfSelect/UIGiftPa...` | 21 | 4 | _use_btn | MSG:MsgDefines.CustomChooseReward ; UI:self |
| `UIGiftScoreTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIGiftScoreTips.prefab` | 9 | 2 | - | UI:UIActivityCenterTable,self |
| `UIGiftVipPackage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGiftVipPackage/UIGiftVipPackag...` | 9 | 0 | - | - |
| `UIGirlSelect` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIGirlCollect/UIGirlSelect.prefab` | 14 | 5 | ToggleBlinkEffect, __toggleGarbageCircle | UI:UIBuildQueueList,self |
| `UIGive` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageTrade.prefab` | 6 | 3 | btnStr | UI:self |
| `UIGivingRoseRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRoseRewar...` | 27 | 2 | - | UI:self |
| `UIGivingRoseShare` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRoseShare...` | 14 | 4 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | UI:UIPositionShareConfirm,self |
| `UIGivingRoses2Castle` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Ca...` | 16 | 6 | Music_Effect_Button, OnCloseBtnClick | UI:UIGivingRoses2Castle |
| `UIGivingRoses2ExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Ex...` | 18 | 6 | isMaxBtn, maxBtnN | UI:self |
| `UIGivingRoses2FlowerHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Fl...` | 21 | 5 | toggle, toggleList | UI:UIChatNew,self |
| `UIGivingRoses2FlowerRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Fl...` | 29 | 7 | ToggleControlBorS, toggle, toggle1, toggle2, toggleList | UI:UIGivingRosesRewardPanel,self |
| `UIGivingRoses2FlowerRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Fl...` | 27 | 2 | - | UI:self |
| `UIGivingRoses2FlowerSelectPlayerPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Fl...` | 25 | 5 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `UIGivingRoses2PockerGet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Po...` | 15 | 3 | - | UI:self |
| `UIGivingRoses2PockerPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Po...` | 23 | 7 | - | UI:UIGivingRoses2PockerShow,self |
| `UIGivingRoses2PockerShow` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Po...` | 17 | 3 | - | UI:self |
| `UIGivingRoses2RewardAndRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses2/UIGivingRoses2Fl...` | 12 | 2 | - | UI:self |
| `UIGivingRosesHistoryPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesHist...` | 18 | 4 | - | UI:UIChatNew,self |
| `UIGivingRosesMyHistoryPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesMyHi...` | 21 | 5 | toggle, toggleList | UI:UIChatNew,self |
| `UIGivingRosesRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesRank...` | 29 | 7 | ToggleControlBorS, toggle, toggle1, toggle2, toggleList | UI:UIGivingRosesRewardPanel,self |
| `UIGivingRosesRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesRewa...` | 24 | 4 | ToggleControlBorS, toggle, toggle1, toggle2, toggleList | UI:UIGivingRoses2FlowerRankView,self |
| `UIGivingRosesSearchResultPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesSear...` | 16 | 2 | - | UI:self |
| `UIGivingRosesSelectPlayerPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesSele...` | 21 | 5 | toggle, toggleList | UI:self |
| `UIGivingRosesWindow` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UIGivingRosesWind...` | 18 | 7 | - | UI:self |
| `UIGloryAllianceDeclareRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryAllianceDeclareRe...` | 21 | 4 | SetToggleTabSelect, toggle | UI:self |
| `UIGloryAllianceSetTruce` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIGloryAllianceSetTruce/UIGl...` | 23 | 7 | record_btn_red_dot, save_btn | UI:UIGlorySetTruceRecord,self |
| `UIGloryDeclare` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryDeclare/UIGloryDe...` | 18 | 3 | - | UI:UIGloryMatch,self |
| `UIGloryDeclareWarLastHit` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryDeclareWarLastHit...` | 9 | 0 | - | - |
| `UIGloryDeclareWarPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryDeclareWarPop/UIG...` | 8 | 1 | - | - |
| `UIGloryDeclareWarPopTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryDeclareWarPopTips...` | 9 | 0 | - | - |
| `UIGloryGroup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryGroup/UIGloryGrou...` | 16 | 0 | - | - |
| `UIGloryInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryInfo/UIGloryInfo....` | 14 | 2 | - | UI:self |
| `UIGloryMatch` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIGloryMatch/UIGloryMatch.pr...` | 21 | 6 | can_be_plundered_btn | UI:UIHeroTips,self |
| `UIGloryPersonalRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryPersonalRank/UIGl...` | 21 | 7 | - | MSG:MsgDefines.AllianceDeclareWarPersonalReward |
| `UIGloryRankReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryRankRewards/UIGlo...` | 15 | 3 | toggles | MSG:MsgDefines.GetSeasonDeclareRewardInfo |
| `UIGloryReward` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryReward/UIGloryRew...` | 21 | 10 | - | MSG:MsgDefines.AllianceDeclareWarPersonalReward |
| `UIGloryRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGlory/UIGloryRule.prefab` | 11 | 0 | - | - |
| `UIGlorySetTruceRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGlory/UIGlo...` | 13 | 1 | - | - |
| `UIGloryWarSwapHistoryPopup` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIGloryWarSwap/UIGloryWarSwapHis...` | 8 | 2 | - | - |
| `UIGloryWarSwapSelectMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIReplaceMemberMain...` | 21 | 6 | toggleArenaPower | - |
| `UIGloryWarSwapTip` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/UIGloryWarSwap/UIGloryWarSwapTip...` | 18 | 6 | - | - |
| `UIGloryWarSwapUsePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGloryWarSwap/UIGloryWarSwapUse...` | 18 | 5 | RefreshExecButton | UI:UIGloryWarSwapHistoryPopup,UIGloryWarSwapSelectMember |
| `UIGoldInsufficientPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/ThirdPayment/UITh...` | 16 | 8 | Music_Effect_Button, OnBtnBuyClick, OnBtnCloseClick, OnBtnOtherCl... | UI:UIThirdPaymentShopPop,anim,self |
| `UIGolloesCamp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesCamp/UIGolloesCamp.prefab` | 52 | 24 | SetSendBtnState, YellowBtnShadowGrayColor, YellowBtnShadowLightCo... | MSG:MsgDefines.ClaimGolloesDailyReward,MsgDefines.ClaimGolloesFreeReward... |
| `UIGolloesCamp2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesCamp/UIGolloesCamp2.prefab` | 68 | 24 | Common_btn_gray_M, Common_btn_yellow_M, RefreshBtnShow, btnClaim,... | MSG:MsgDefines.ClaimGolloesDailyReward,MsgDefines.ClaimGolloesFreeReward... |
| `UIGolloesCardsExShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GolloesCards/UIGo...` | 14 | 3 | UIButton, UICommonPopUpTitle/CloseBtn, _close_btn | UI:self |
| `UIGolloesCardsRP` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/GolloesCards/UIGo...` | 14 | 3 | toggle, toggleList | UI:self |
| `UIGolloesCardsRank` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/GolloesCards/UIGo...` | 16 | 4 | UIButton, UICommonPopUpTitle/CloseBtn, _close_btn, _selfHead_btn | UI:UIPlayerInfo,self |
| `UIGolloesMonthCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesMonthCard/UIGolloesMont...` | 14 | 3 | - | UI:self |
| `UIGolloesMonthCardPopUp` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/GiftPackage/UIGolloesMonthCardPo...` | 15 | 1 | - | UI:self |
| `UIGolloesTraderRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGolloesCamp/UIGolloesTraderRec...` | 17 | 7 | Tab/Toggle1, Tab/Toggle2, UIButton, UICommonMidPopUpTitle/CloseBt... | MSG:MsgDefines.GetGolloesCaravanRecord ; UI:UIGiftPackage,self |
| `UIGolloesUnlockReward` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIGolloesUnlockReward/UIGolloesU...` | 5 | 1 | btns | UI:UIHeroTip |
| `UIGotoAllowTracking` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UIGotoAllowTracking.pr...` | 6 | 2 | OnBtnClick, UIButton, close_btn, close_btn_path, goto_btn_path, u... | UI:UIPlayerInfo,self |
| `UIGovernmentInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIGovernmentInfo.prefab` | 25 | 8 | Music_Effect_Button | UI:UIOtherPlayerInfo,UIPositionAppointSearch,UIThroneKingdomApplyPos |
| `UIGovernmentMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePresident.prefab` | 18 | 6 | - | UI:self |
| `UIGridDebug` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Common/UIGridDebug.prefab` | 8 | 2 | - | MSG:MsgDefines.BagDebugAdd ; UI:self |
| `UIGroceryStore` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIGroceryStore/UIGroceryStore.pr...` | 47 | 14 | deliver_normal_get_more_btn, deliver_normal_item_info_btn | UI:UIHeroTip,self |
| `UIGroundPassUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/PurplePass/UIPurp...` | 15 | 2 | - | - |
| `UIGuideArrow` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideArrow.prefab` | 49 | 10 | Button, OnClickJoystickBtn, OnClickNpcGirlGiveBtn, SU_ClickJoysti... | - |
| `UIGuideArrowNew` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideArrow.prefab` | 43 | 10 | Button, OnClickJoystickBtn, OnClickNpcGirlGiveBtn, SU_ClickJoysti... | - |
| `UIGuideCommunicationTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideCommunicationTalk.prefab` | 27 | 6 | btn_arrow | UI:anim |
| `UIGuideGurtain` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide2/UIGuideGurtain.prefab` | 5 | 2 | - | - |
| `UIGuideHeadTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideHeadTalk.prefab` | 21 | 3 | - | UI:anim |
| `UIGuideIntroBubble` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UIGuideIntroBubble.prefab` | 46 | 9 | Button, Toggle, UIButton, UIToggle, btn, onBtnClick | UI:self |
| `UIGuideIntroBubble1` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UIGuideIntroBubble1.prefab` | 44 | 10 | Button, OnClickJoystickBtn, OnClickNpcGirlGiveBtn, SU_ClickJoysti... | UI:self |
| `UIGuideLoadBlackMask` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideLoadBlackMask.prefab` | 12 | 1 | - | UI:anim |
| `UIGuideLoadMask` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideLoadMask.prefab` | 12 | 1 | - | UI:anim |
| `UIGuideMoveArrow` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideMoveArrow.prefab` | 28 | 4 | - | UI:anim |
| `UIGuideNoNpcTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideNoNpcTalk.prefab` | 20 | 6 | Music_Effect_Button | UI:self |
| `UIGuideShowDogItem` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide2/UIGuideShowDogItem.prefab` | 16 | 2 | - | UI:MainUI_SU,anim |
| `UIGuideTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideTalk1.prefab` | 39 | 9 | RefreshAutoBtn, btnAuto1, btnAuto2 | UI:anim |
| `UIGuideTalk2` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideTalk2.prefab` | 16 | 3 | - | UI:anim |
| `UIGuideTalk3` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide2/UIGuideTalk3.prefab` | 17 | 3 | - | UI:anim |
| `UIGuideTalk4` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide2/UIGuideTalk4.prefab` | 16 | 3 | - | UI:anim |
| `UIGuideTalk5` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide2/UIGuideTalk5.prefab` | 16 | 3 | - | UI:anim |
| `UIGuideTip` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIGuideTip.prefab` | 23 | 6 | - | UI:anim |
| `UIGuideUnlockMask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIGuideUnlockMask/UIGuideUnlockM...` | 12 | 1 | - | UI:anim |
| `UIGuideVideo` | `UIContainer/Info` | `Assets/Main/Prefabs/Guide/GuideVideo.prefab` | 27 | 5 | skip_btn | UI:anim |
| `UIGuideWaitToBuildFence` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/UIGuideWaitToBuildFence/UIGuideW...` | 4 | 1 | - | - |
| `UIHHShowTip` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIHHshowTip/UIHHshowTip.prefab` | 10 | 2 | UIButton | UI:self |
| `UIHalloween2026PassBuyPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 1 | 0 | - | - |
| `UIHalloweenCommonIntroPanel` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 16 | 2 | Music_Effect_Button | UI:self |
| `UIHalloweenDrawCardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 26 | 9 | SetBtnSkipStatus, mBtnLotter10Image, mBtnLotter1Image, mBtnSkipNe... | MSG:MsgDefines.LotteryMachineActivityLottery ; UI:self |
| `UIHalloweenDrawLotteryDetailView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 22 | 7 | - | UI:self |
| `UIHalloweenDrawLotteryListView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 17 | 2 | - | UI:self |
| `UIHalloweenDrawLotteryLogView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 23 | 5 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | MSG:MsgDefines.LotteryMachineActivityGiftRecord ; UI:self |
| `UIHalloweenDrawLotteryResultView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 22 | 7 | - | UI:self |
| `UIHalloweenDrawResultView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 13 | 2 | - | UI:self |
| `UIHalloweenDrawRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/LuckyDraw/...` | 26 | 8 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `UIHalloweenExchangeShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/HalloweenE...` | 18 | 6 | isMaxBtn, maxBtnN | UI:self |
| `UIHalloweenGiftRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/GiveGift/R...` | 17 | 9 | ToggleGroup/ToggleGroupSubTab/Toggle1, ToggleGroup/ToggleGroupSub... | UI:self |
| `UIHalloweenGiftRecommendView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/GiveGift/U...` | 25 | 5 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | UI:self |
| `UIHalloweenGiftResultView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/GiveGift/U...` | 12 | 1 | - | UI:self |
| `UIHalloweenLevelReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 28 | 12 | SetRewardBtn, UpdateBigRewardJumpBtn, mBtnJumUpActive, mBtnJumpDo... | UI:self |
| `UIHalloweenMarbleCardReward` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 10 | 3 | UIButton, _close_btn | - |
| `UIHalloweenMarbleProbability` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 23 | 5 | - | - |
| `UIHalloweenMarbleRecord` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 17 | 2 | - | - |
| `UIHalloweenMarbleRewardloop` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 14 | 2 | - | - |
| `UIHalloweenMarbleSliderReward` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 23 | 5 | BtnClick_Close | - |
| `UIHalloweenNewExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 1 | 1 | - | UI:UIHalloweenNewExchangeShopBuy |
| `UIHalloweenPopNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween2026/UIHall...` | 16 | 3 | - | - |
| `UIHalloweenPopTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 16 | 2 | - | UI:self |
| `UIHalloweenRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 25 | 2 | - | UI:self |
| `UIHalloweenRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 12 | 1 | - | UI:self |
| `UIHeadIconShow` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/ChatNew/UIHeadIconShow.prefab` | 10 | 1 | UIButton, _btnBg | UI:self |
| `UIHeadTalk` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIHeadTalk.prefab` | 24 | 6 | - | UI:anim |
| `UIHeroBattlePassPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIHeroBattlePass/...` | 19 | 2 | btn | UI:UIHeroSkillTip |
| `UIHeroBeyond` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroBeyond.prefab` | 13 | 6 | - | MSG:MsgDefines.HeroLvBeyond ; UI:UIHeroInfo,self |
| `UIHeroBountyMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroOfferRewardFirs...` | 14 | 7 | UIButton, close_btn, close_btn_path, extra_desc_intro_btn, extra_... | MSG:MsgDefines.GetHeroBountyInfo ; UI:UIHeroTip,self |
| `UIHeroBountyTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroOfferReward.prefab` | 40 | 18 | UIButton, close_btn, extra_desc_intro_btn, info_btn, rarity_btn, ... | MSG:MsgDefines.RefreshHeroBountyTask,MsgDefines.StartHeroBountyTask ; UI... |
| `UIHeroBreak` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroBreakPop.prefab` | 18 | 4 | /BtnGo, /BtnGo/btnText, Music_Effect_Button, Root/BigBtnYellow, R... | MSG:MsgDefines.HeroRankUpgrade ; UI:UIHeroMilitaryRank |
| `UIHeroBreakSuccess` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroBreakTime.prefab` | 17 | 4 | ToggleRecruitScene | UI:self |
| `UIHeroCampRestraint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroCampRestraint.p...` | 8 | 2 | UIButton, return_btn | UI:self |
| `UIHeroDetailTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIHeroDetailTips.prefab` | 15 | 1 | btnSkills | UI:self |
| `UIHeroDressFilter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroDress/UIHeroDressFilterBox...` | 13 | 3 | - | - |
| `UIHeroDressList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroDress/UIHeroDressList.prefab` | 18 | 4 | - | UI:UIHeroDressFilter |
| `UIHeroEffectSkillTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISkillFeedbackTips.pr...` | 14 | 1 | - | UI:self |
| `UIHeroEffectSkillTipsBackground` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UISetting/UISkillFeedbackTips.pr...` | 14 | 1 | - | UI:self |
| `UIHeroEquip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipView...` | 21 | 7 | BtnName, BtnType, Music_Effect_Button, OnClickGoldBtn, ToggleCont... | UI:UIResourceBag,self |
| `UIHeroEquipEvolutionSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipEvol...` | 6 | 1 | - | UI:UIHeroMilitaryAdvanceSuccess |
| `UIHeroEquipForgeMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipForg...` | 54 | 18 | Music_Effect_Button, OnClickInfoBtn, OnClickItemBtn, OnClickResou... | UI:UIBagView,UICapacityBoxSelect,UIHeroEquipForgePreview |
| `UIHeroEquipForgePreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipRed....` | 12 | 1 | - | UI:UIHeroEquipForgingSuccessful |
| `UIHeroEquipForgingSuccessful` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipForg...` | 6 | 1 | - | UI:self |
| `UIHeroEquipInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipInfo...` | 26 | 9 | Music_Effect_Button, OnDownBtnClick, OnPromotionBtnClick, OnRepla... | UI:UIHeroEquipPromotion,UIHeroEquipReplace,_ENV |
| `UIHeroEquipPromotion` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipProm...` | 35 | 6 | Music_Effect_Button, OnPromotionBtnClick, UIButton, closeBtn, clo... | UI:UIResourceBag,_ENV |
| `UIHeroEquipPromotionSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIEquipaAddItem...` | 21 | 6 | - | UI:self |
| `UIHeroEquipRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipList...` | 22 | 8 | Music_Effect_Button, UIButton, closeAll_btn, close_btn, self_btn | UI:UIAllianceDetail,UIHeroEquipTips,UIOtherPlayerInfo |
| `UIHeroEquipReplace` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipRepl...` | 23 | 4 | Music_Effect_Button, OnDownBtnClick, OnGetEquipBtnClick, UIButton... | UI:self |
| `UIHeroEquipReset` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipRese...` | 28 | 6 | - | UI:UICommonCostConfirm,self |
| `UIHeroEquipStrength` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipNew....` | 27 | 3 | toggle, togglelist | UI:self |
| `UIHeroEquipTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipTips...` | 24 | 2 | - | - |
| `UIHeroExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroResetShop/UIHeroExchange.p...` | 15 | 5 | OnClickCloseBtn, hero_btn | MSG:MsgDefines.BuyCommonShopGoods ; UI:UIHeroTips,self |
| `UIHeroInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroInfo.prefab` | 58 | 16 | CheckArrowBtns, GetBtnUpSizeDelta, OnBtnSkinClick, RefreshToggle,... | UI:UIHeroInfoPageSkin,UIHeroSPEquip,UIHeroSkillUpgrade |
| `UIHeroInfoEquipInfoNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroEquip/View/UIHeroEquipProm...` | 33 | 10 | promotionBtn, resetBtn, shareBtn, strengthBtn, toggle, togglelist | UI:UIHeroEquipRank,UIHeroEquipReplace,UIHeroEquipReset |
| `UIHeroInfoPageSkin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroInfoPageSkin.pr...` | 10 | 3 | - | UI:self |
| `UIHeroIntensify` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroHall/UIHeroPalaceMain.prefab` | 38 | 12 | BtnType, IsOneKeyUpgradeBtnUnlock, Music_Effect_Button, ToggleCon... | UI:UICommonTipWithNoMind,UIHeroIntensifyInfo,UIHeroIntensifyTip |
| `UIHeroIntensifyInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroHall/UIHeroPalaceLevelUp.p...` | 40 | 12 | Music_Effect_Button, OnQualityBtnRightClick, WorldTileBtnType, bt... | MSG:MsgDefines.HeroIntensify ; UI:UIHeroMedalExchange,UIItemTips,self |
| `UIHeroIntensifyTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroHall/UIHeroPalaceAttr.prefab` | 12 | 1 | - | UI:self |
| `UIHeroJigsawReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroJigsawReward.pr...` | 10 | 2 | - | UI:self |
| `UIHeroLackTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroLackTips/UIHeroLackTips.pr...` | 18 | 2 | - | UI:self |
| `UIHeroList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroList.prefab` | 39 | 11 | GetHeroCellAdvanceGuideBtn, advanceBtn | UI:UIHeroAdvance,UIHeroDressList,UIHeroList |
| `UIHeroLvUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroLvUp.prefab` | 38 | 10 | CloseMoreBtn, MoreBtnLocalPosX, MoreBtnPos, ShowMoreBtn, ToggleMo... | MSG:MsgDefines.HeroLvUp ; UI:UIHeroBeyond,self |
| `UIHeroMedalExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMedalExchange.p...` | 13 | 7 | Music_Effect_Button, OnShortCutBtnClick, toggle_rect | MSG:MsgDefines.HeroSPEquipItemExchange ; UI:self |
| `UIHeroMilitaryAdvanceSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMilitaryAdvance...` | 7 | 2 | btn | UI:UIHeroSkillTip,self |
| `UIHeroMilitaryRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMilitaryRank.pr...` | 59 | 26 | CheckArrowBtns, Music_Effect_Button, OnClickBtnGoto, ShowBtnArrow... | MSG:MsgDefines.GetHeroWakeSkin,MsgDefines.HeroRankUpgrade ; UI:UIHeroBre... |
| `UIHeroMilitaryRankIntro` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMilitaryRankInt...` | 18 | 2 | btn, btnSkills | UI:UIHeroSkillTip,self |
| `UIHeroMilitaryRankIntroNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroMilitaryRankInt...` | 14 | 1 | - | UI:self |
| `UIHeroMonthCard` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroMonthCard/UIHeroMonthCard....` | 12 | 2 | - | UI:self |
| `UIHeroOfficial` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroOfficial/UIHeroOfficial.pr...` | 22 | 8 | - | UI:self |
| `UIHeroPosterExchangeMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroPosterExchangeM...` | 25 | 7 | btnInfo, toggleList | UI:UIHeroPosterExchangePop,UIHeroTip,self |
| `UIHeroPosterExchangePop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroPosterExchangeP...` | 13 | 6 | - | MSG:MsgDefines.HeroPosterExchange ; UI:self |
| `UIHeroPreviewSkillWindow` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroPreviewSkillWin...` | 14 | 4 | - | UI:self |
| `UIHeroRankList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/UIHeroRankList.prefab` | 22 | 7 | UIButton, closeAll_btn, close_btn, toggleN, togglesTbN | UI:UIAllianceDetail,UIOtherPlayerInfo,self |
| `UIHeroRecruit` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruit.prefab` | 74 | 18 | Music_Effect_Button, btnRecruitOne, btnRecruitOneImg, btnRecruitT... | MSG:MsgDefines.LotteryHeroCard ; UI:UIHeroRecruitChangeCamp,UIHeroRecrui... |
| `UIHeroRecruitChangeCamp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruitChangeCa...` | 15 | 5 | ToggleSelect | MSG:MsgDefines.LotteryHeroSwitch ; UI:self |
| `UIHeroRecruitReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruitReward.p...` | 27 | 10 | OnToggleRecruitScene, ToggleRecruitScene, btnClose, btnClose1 | MSG:MsgDefines.LotteryHeroCard ; UI:UIResourceLackNew,self |
| `UIHeroRecruitTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroRecruitTip.prefab` | 29 | 5 | Music_Effect_Button, toggleList | UI:UIItemTips,self |
| `UIHeroResetShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHeroResetShop/UIHeroResetShop....` | 17 | 6 | - | UI:EventManager,anim |
| `UIHeroResetSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroResetSuccess.pr...` | 5 | 1 | - | UI:self |
| `UIHeroSPEquip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroInfoWeapon.prefab` | 49 | 14 | Music_Effect_Button, OnClickBtnGoto, WorldTileBtnType, allToggle,... | MSG:MsgDefines.HeroSPEquipUnlock ; UI:UIHeroIntensify,UIHeroMedalExchang... |
| `UIHeroSPEquipSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroinfoWeaponSucce...` | 9 | 2 | Music_Effect_Button, btn, btnSkills | UI:UIEquipBreakSkillTip,UIHeroSkillTip |
| `UIHeroSkillAdvance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillAdvance.pr...` | 16 | 6 | btn | MSG:MsgDefines.HeroSkillUpgrade ; UI:UIHeroMedalExchange,UIHeroSkillTip,... |
| `UIHeroSkillAdvanceSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillAdvanceSuc...` | 12 | 1 | - | UI:self |
| `UIHeroSkillTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillTip.prefab` | 12 | 1 | - | UI:self |
| `UIHeroSkillUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillUpgrade.pr...` | 33 | 8 | Music_Effect_Button, ShowBtnArrow, bigtogglebackimg, btnLeft, btn... | MSG:MsgDefines.HeroSkillUpgrade ; UI:UIHeroInfo,UIHeroMilitaryRank |
| `UIHeroSkillUpgradeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroSkillUpgradeSuc...` | 8 | 2 | - | UI:self |
| `UIHeroSkinUseItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UIDecorateUnlock.pr...` | 18 | 1 | - | - |
| `UIHeroTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIHero/New/UIHeroTip.prefab` | 5 | 1 | goto_btn | UI:self |
| `UIHeroTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIHeroTips.prefab` | 11 | 4 | btn, btnSkills | UI:UIHeroInfo,UIHeroSkillTip,UIHeroTip |
| `UIHeroTips2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIHeroTips2.prefab` | 14 | 4 | btn, btnSkills | UI:UIBattlePassGiftPackagePopUp,UIHeroCampRestraint,UIHeroSkillTip |
| `UIHitTurkeyGameMsgBox` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UICommonMessageTip3.prefab` | 17 | 3 | BtnClick_Close | UI:UIHitTurkeyOperate |
| `UIHitTurkeyGift` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingCatch/...` | 22 | 3 | - | - |
| `UIHitTurkeyNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingCatch/...` | 12 | 1 | - | - |
| `UIHitTurkeyOperate` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingCatch/...` | 16 | 1 | - | - |
| `UIHitTurkeyRank` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/FoodFestival/UIFoodFestivalRank...` | 16 | 2 | - | - |
| `UIHospital` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalMain.prefab` | 97 | 24 | ImmediatelyBtnClick, ImmediatelySpeedBtnClick, SpeedBtnClick, Tre... | MSG:MsgDefines.HospitalCure,MsgDefines.QueueCcdMNew ; UI:UICommonIntro2,... |
| `UIHospitalDeath` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHostpitalDeath.prefab` | 26 | 2 | - | UI:anim |
| `UIHospitalDetial` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalDetial Varian...` | 30 | 3 | - | UI:anim |
| `UIHospitalGetMore` | `UIContainer/Normal` | `Assets/SlgEngine/Main/Prefabs/UI/UIHospital/UIHospitalG...` | 10 | 5 | Music_Effect_Button, WorldTileBtnType | UI:anim |
| `UIHospitalHelpTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalHelpTips.prefab` | 7 | 1 | - | UI:self |
| `UIHospitalLack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRepair/UIHospitalLack.prefab` | 10 | 5 | Music_Effect_Button, WorldTileBtnType | UI:anim |
| `UIHotNewsPointDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHotNews/UIHotNewRank.prefab` | 31 | 9 | Music_Effect_Button, btn, iconBtn, toggleCount, toggleListData | UI:UIHeroTip,UIPositionShare,self |
| `UIIDCardAgeTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAccount/UIIDCardAgeTips.prefab` | 6 | 3 | - | UI:UIIDCardAuthenticate,UIIDCardDesTips |
| `UIIDCardAuthenticate` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAccount/UIIDCardAuthenticate.p...` | 11 | 5 | - | MSG:MsgDefines.IDCardAuthenticate ; UI:UIIDCardDesTips,self |
| `UIIDCardDesTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIAccount/UIIDCardDesTips.prefab` | 6 | 2 | - | UI:self |
| `UIIronAgeNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/IronAge/IronAgePush/...` | 11 | 1 | - | UI:UIActivityCenterTable |
| `UIItemBaubleTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIBauble/UIItemBaubleTip.prefab` | 31 | 3 | - | UI:UIBaubleInfo,self |
| `UIItemChatTitleTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIItemChatTitleTip.prefab` | 14 | 1 | - | - |
| `UIItemHeroBreakTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/SU_ItemHeroBreakTips.prefab` | 10 | 0 | - | - |
| `UIItemHeroEquipBreakTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/SU_ItemHeroBreakTips.prefab` | 11 | 1 | Music_Effect_Button, btnCamp | UI:UIHeroCampRestraint |
| `UIItemHeroSkinTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/SU_ItemHeroSkinTips.prefab` | 9 | 0 | - | - |
| `UIItemPurchases` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIItem/UIItemPurchases.prefab` | 26 | 6 | - | MSG:MsgDefines.UIShopBuy ; UI:self |
| `UIItemTips` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/SU_ItemTips.prefab` | 24 | 5 | - | UI:UICapacityBoxSelect,UICommonItemProbabilityNew |
| `UIItemTips02` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/Common/SU_ItemTips02.prefab` | 8 | 0 | - | - |
| `UIJeepAdventureMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIJeepAdventureM...` | 32 | 11 | gotoBtn, jumpLevelBtn, jumpLevelBtnText, rewardBtn | UI:OpenWinAnimTrue,UIJeepAdventureTask,UIPVETowerClimbJump |
| `UIJeepAdventureTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIJeepAdventureT...` | 12 | 5 | - | UI:self |
| `UIJoinAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIJoinAlliance.prefab` | 23 | 12 | Music_Effect_Button, ToggleControlBorS, UIButton, UICommonPopUpTi... | MSG:MsgDefines.AlApply,MsgDefines.AlCancelApply,MsgDefines.AlSearch ; UI... |
| `UIJoinGroupTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIJoinGroup/UIJoinGroupTips.prefab` | 16 | 1 | - | MSG:ChatMsgDefines.RoomAgreeInvite |
| `UIJoystick` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIJoystick.prefab` | 9 | 1 | - | UI:self |
| `UIKingdomSwapHistoryPopup` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 8 | 2 | - | - |
| `UIKingdomSwapPopup` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 11 | 5 | - | UI:UIKingdomSwapHistoryPopup |
| `UIKingdomSwapSelectPopup` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 14 | 3 | - | - |
| `UIKingdomSwapTip` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 18 | 6 | - | - |
| `UIKingdomSwapUsePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UICrossWonder/UICrossWonderAct/U...` | 14 | 5 | - | UI:UIKingdomSwapHistoryPopup,UIKingdomSwapSelectPopup |
| `UIKonbini` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIKonbini/UIKonbini.prefab` | 23 | 6 | - | UI:UICapacityFull,self |
| `UILOCampUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LandingOperations...` | 9 | 1 | - | UI:self |
| `UILOResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LandingOperations...` | 22 | 8 | - | UI:UILoMap,self |
| `UILOShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LandingOperations...` | 12 | 3 | - | UI:anim |
| `UILWDispatchTaskLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/UILW...` | 16 | 4 | toggle1, toggleGroup | UI:self |
| `UILWTrainDeparture` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainDeparture.p...` | 76 | 15 | GF_click_departure_btn, GF_click_random_btn, OnChangeHeroBtnClick... | UI:UIFormationTableNew,UIHeroPVPFormation,self |
| `UILWTrainDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainDetail.prefab` | 16 | 3 | - | UI:self |
| `UILWTrainList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainList.prefab` | 19 | 7 | - | UI:self |
| `UILWTrainRefreshBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/DispatchTask/UIDi...` | 12 | 0 | - | - |
| `UILWTrainReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainReward.prefab` | 15 | 4 | - | UI:self |
| `UILWTrainScene` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UILWRailway/UILWTrainScene.prefab` | 39 | 17 | MailToggleGroupTruck, Music_Effect_Button, RefreshScienceBtnState... | UI:UILWTrainDeparture |
| `UILandLockTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILandLock/UILandLockTips.prefab` | 11 | 1 | - | - |
| `UILandLockTips1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILandLock/UILandLockTips1.prefab` | 8 | 1 | - | - |
| `UILeagueMatchAlliances` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/LeagueMatch/UILeagueMatchAllianc...` | 15 | 4 | - | UI:self |
| `UILeagueMatchResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/LeagueMatch/UILeagueMatchResult/...` | 17 | 3 | - | UI:self |
| `UILeagueMatchReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/LeagueMatch/UILeagueMatchReward/...` | 18 | 8 | Music_Effect_Button, toggle | UI:self |
| `UILensBlackEdge` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILensBlackEdge/UILensBlackEdge....` | 15 | 3 | - | UI:self |
| `UILetterBoxing` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Barrel/UILetterBoxing.prefab` | 1 | 0 | - | - |
| `UILike` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILike.prefab` | 18 | 0 | - | - |
| `UILikeActRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeRanking/UILikeRanki...` | 20 | 7 | Root/ToggleGroup/ToggleGroupSubTab/Toggle1, Root/ToggleGroup/Togg... | UI:UIPlayerInfo,self |
| `UILikeActRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UICommonRuleImgSubtab.prefab` | 18 | 2 | - | - |
| `UILikeHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeHistory.prefab` | 14 | 1 | Right/ToggleGroupBg, UIButton, UICommonPopUpTitle/CloseBtn, close... | - |
| `UILikeMessageBigTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UILike/UILikeTipsBig.prefab` | 15 | 0 | - | - |
| `UILikeMessageTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeTips.prefab` | 13 | 0 | - | - |
| `UILikeRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UILikeRank.prefab` | 14 | 2 | Music_Effect_Button, Panel/UICommonPopUpTitle/CloseBtn, Panel/UIP... | UI:UIHeadIconShow |
| `UILikeRemainTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UILike/UILikeRemainTips.prefab` | 13 | 0 | - | - |
| `UILoMap` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LandingOperations...` | 25 | 7 | DoFlyToShopBtn, _fight_btn | MSG:MsgDefines.ClientEvent ; UI:UICommonShop,UILoMap |
| `UILoPowerLack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LandingOperations...` | 12 | 3 | - | UI:UILoPowerLack |
| `UILoadEditorBuild` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/LoadEditorBuild.prefab` | 10 | 3 | - | UI:self |
| `UILogin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UILogin.prefab` | 15 | 3 | - | MSG:MsgDefines.AccountLogin ; UI:self |
| `UILoginConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UILoginConfirm.prefab` | 6 | 2 | - | - |
| `UILoveNewsletter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatLove.prefab` | 53 | 12 | RefreshToggle, Toggle1, Toggle2, ToggleTag, toggle1, toggle2 | MSG:MsgDefines.SurvivalHeroMessagePowerBuy ; UI:_ENV |
| `UILoveNewsletterFilter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatLoveFilterBox.prefab` | 18 | 6 | RefreshToggles, campAllToggle, campToggle1, campToggle2, campTogg... | - |
| `UILoveNewsletterMM` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatLoveMM.prefab` | 12 | 0 | - | - |
| `UILoveNewsletterUnlockPic` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatLove/UIChatLoveItemUnlock.pr...` | 14 | 1 | - | UI:self |
| `UILoveVideoCall` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UILoveVideoCall.prefab` | 6 | 0 | - | - |
| `UILovelyFavor` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRobotPack/UILovelyFavor.prefab` | 14 | 3 | - | UI:UILovelyFavor |
| `UILuckyRollGiftPackList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/UILucky...` | 13 | 4 | UIButton, _close_btn, safeArea/GiftList/topRes/btnClose | UI:self |
| `UILuckyRollHeroBigRewardRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/LuckyRo...` | 17 | 6 | - | MSG:MsgDefines.GetLuckyRollNotice ; UI:UILuckyRollRank,self |
| `UILuckyRollHeroPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/LuckyRo...` | 20 | 2 | btn | UI:UIHeroSkillTip |
| `UILuckyRollHeroRewardPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/LuckyRo...` | 19 | 6 | - | UI:UILuckyRollRank,self |
| `UILuckyRollRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/UILucky...` | 19 | 7 | ToggleGroupSubTab/Toggle1, ToggleGroupSubTab/Toggle1/checkText1, ... | UI:UIPlayerInfo,self |
| `UILuckyRollRewardGet` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILuckyRollRewardGet/UILuckyRoll...` | 9 | 0 | - | - |
| `UILuckyRollRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/AttZombiePuzzle/U...` | 13 | 7 | UIButton, return_btn | MSG:MsgDefines.SurvivalBigBox ; UI:OpenWinAnimTrue |
| `UILuckyRollTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LuckyRoll/UILucky...` | 9 | 4 | OnClickUseBtn, UIButton, UIToggle, _close_btn, back_toggle, back_... | UI:self |
| `UILuckyShopPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UILuckyShop/UILuc...` | 15 | 4 | ToggleGroupBg, UIButton, bgBtnN, closeBtnN, toggleGroupRoot, toggleN | UI:self |
| `UILuckyShopProgressReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UILuckyShop/UILuc...` | 11 | 3 | UIButton, closeBtn | UI:self |
| `UILuckyShopRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILuckyShopRank/UILuckyShopRank....` | 18 | 4 | - | UI:self |
| `UIMailAuthenticate` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UIMailAuthenticate.prefab` | 8 | 4 | - | MSG:MsgDefines.AccountVerifyDevice,MsgDefines.NewAccount ; UI:UIMailVeri... |
| `UIMailBattleAttrDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/ObjMail/MailP...` | 48 | 3 | - | UI:self |
| `UIMailBattleAttrDetail4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/ObjMail/MailP...` | 48 | 3 | - | - |
| `UIMailCampRestraintDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIMailCampRestraintDe...` | 8 | 2 | UIButton, return_btn, return_btn_path | UI:self |
| `UIMailDetailReportView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/MailDetailVie...` | 22 | 7 | OnClickBtnClose, OnClickBtnCloseAllRound, UIButton, _btnClose, _b... | UI:self |
| `UIMailDetailReportView4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/old/BattleReport/MailDetai...` | 22 | 7 | OnClickBtnClose, OnClickBtnCloseAllRound, UIButton, _btnClose, _b... | - |
| `UIMailInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailInfo.prefab` | 61 | 23 | Music_Effect_Button, OnClickReplayBtnNew, RefreshToBottomBtnNew, ... | UI:OpenWinAnimFalse,UIMailReturn,UIMailSend |
| `UIMailInfo4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailInfo.prefab` | 72 | 23 | Music_Effect_Button, OnClickReplayBtnNew, RefreshToBottomBtnNew, ... | UI:UIMailReturn,UIMailSend |
| `UIMailNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailMainPanel.prefab` | 81 | 27 | Music_Effect_Button, OnClickBtnBatchCancel, ShowJumpBtnRewardMail... | UI:UIMailInfo,UIMailReturn,UIMailSend |
| `UIMailNew4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailMainPanel.prefab` | 82 | 27 | Music_Effect_Button, OnClickBtnBatchCancel, ShowJumpBtnRewardMail... | UI:UIMailReturn,UIMailSend |
| `UIMailSend` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailSend.prefab` | 17 | 6 | OnClickSendBtn, OnClickSwitchBtn, UIButton, closeBtnN, posBtnN, p... | MSG:MsgDefines.MailSend ; UI:UIChatVoteCreatTips,self |
| `UIMailSend4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIMailSend.prefab` | 17 | 6 | OnClickSendBtn, OnClickSwitchBtn, UIButton, closeBtnN, posBtnN, p... | MSG:MsgDefines.MailSend ; UI:UIChatVoteCreatTips,self |
| `UIMailTroopInfoListView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/TroopInfoList...` | 10 | 5 | OnClickBtnAlive, OnClickBtnClose, OnClickBtnInjure, OnClickBtnWou... | UI:UIHeroTip,self |
| `UIMailTroopInfoListView4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/BattleReport/TroopInfoList...` | 10 | 5 | OnClickBtnAlive, OnClickBtnClose, OnClickBtnInjure, OnClickBtnWou... | UI:UIHeroTip |
| `UIMailVerify` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UIMailVerify.prefab` | 8 | 2 | - | MSG:MsgDefines.AccountVerifyDevice ; UI:self |
| `UIMainAccountBind` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMain/UIMainAccountBind.prefab` | 10 | 5 | - | UI:UIPlayerInfo,self |
| `UIMainChapterTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_MainTask/UIMainChapterTask1.p...` | 26 | 3 | toggle | - |
| `UIMainMapLaunch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMiniMap/UIMainMapLaunch.prefab` | 26 | 6 | Music_Effect_Button, OnClickServerIdBtn, UIButton, btnNum, clickS... | UI:self |
| `UIMainMapPointCell` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/UIMiniMap/UIMainMapPointCell.prefab` | 18 | 2 | - | UI:UIMainMapPointCell |
| `UIMainMiniMap` | `UIContainer/UIResource` | `-` | 43 | 5 | - | MSG:MsgDefines.GetWorldAttackerInfo ; UI:self |
| `UIMainMsgView` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/SU_Common/UIMainMsg.prefab` | 15 | 1 | - | UI:self |
| `UIMainNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMainNotice/UIMainNotice.prefab` | 38 | 12 | ToggleControlBorS, _btnToBottom, btnGetReward, isBtnReward, toggl... | - |
| `UIMainPromptView` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/Survival/UIMainPrompt.prefab` | 23 | 1 | - | UI:self |
| `UIMarchCancelDragMsgBar` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/World/UIMarchCancelDragMsgBar.pr...` | 5 | 2 | - | UI:anim |
| `UIMarchEmojiTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UIMarchEmojiTip.prefab` | 15 | 2 | - | UI:self |
| `UIMastery` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMastery.prefab` | 16 | 6 | Music_Effect_Button | UI:UIMasterySelect,UIMasterySkill,UIMasteryTree |
| `UIMasteryDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasteryDetail.prefab` | 28 | 6 | Music_Effect_Button | UI:OpenWinAnimTrue,anim |
| `UIMasteryExpTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIMastery/UIMasteryTips.prefab` | 17 | 4 | - | - |
| `UIMasterySelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySelect.prefab` | 26 | 12 | Music_Effect_Button, ToggleBattle, ToggleBuild, battleBtn, btnNum... | MSG:MsgDefines.MasteryChangePlan ; UI:OpenWinAnimFalse,UIResourceLackNew... |
| `UIMasterySelectRes` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySelectRes.prefab` | 10 | 2 | - | - |
| `UIMasterySkill` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySkill.prefab` | 16 | 3 | DesertOperateBtnState, GetBtnState, btnState | UI:self |
| `UIMasterySkillUse` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySkillUse.prefab` | 6 | 2 | back_toggle | - |
| `UIMasterySkillUseResultShow` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySkillUseResul...` | 5 | 0 | - | - |
| `UIMasterySoldier` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasterySoldier.prefab` | 6 | 2 | - | UI:UIMasterySkillUseResultShow |
| `UIMasteryTree` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMastery/UIMasteryTree.prefab` | 31 | 6 | BtnInfo, Music_Effect_Button, btnNum, leftBtnPicName, leftBtnPicText | UI:UIResourceLackNew,self |
| `UIMedalGet` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIMedalGet/UIMedalGet.prefab` | 13 | 1 | - | - |
| `UIMedalGetCar` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIMedalGet/UIMedalGetCar.prefab` | 10 | 1 | - | - |
| `UIMigrateActTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateActTips.p...` | 8 | 3 | - | UI:self |
| `UIMigrateApp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateAppList.p...` | 20 | 6 | - | MSG:MsgDefines.MigrateApprove ; UI:UIOtherPlayerInfo,self |
| `UIMigrateDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateDetail.pr...` | 24 | 8 | info_btn, info_request_btn | MSG:MsgDefines.MigrateApply ; UI:UIGiftBoxPackageList,UIHeroTips,UIRankD... |
| `UIMigrateFinish` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateFinish.pr...` | 6 | 2 | - | UI:self |
| `UIMigrateInvite` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateInvite.pr...` | 23 | 6 | Music_Effect_Button | UI:self |
| `UIMigrateInviteList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateInviteLis...` | 19 | 3 | - | UI:self |
| `UIMigrateLevelTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateLevelTip....` | 6 | 2 | - | UI:self |
| `UIMigrateList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateServerLis...` | 18 | 5 | is_language_toggle, is_power_toggle | UI:self |
| `UIMigrateToServer` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMigrate/UIMigrateToServer....` | 10 | 4 | to_btn | MSG:MsgDefines.MigrateToServer ; UI:self |
| `UIMigrating` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIMigrating.prefab` | 12 | 3 | - | UI:anim |
| `UIMilitaryForceLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMillitary/UIMilitaryForceLogPo...` | 33 | 12 | Music_Effect_Button, addBtn, reserveBtn, reserveDetailBtn, toggle... | UI:UIHeroTip,UIMilitaryLack,UIReserveToSoldier |
| `UIMilitaryLack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMillitary/UIMilitaryLack.prefab` | 11 | 4 | Music_Effect_Button, WorldTileBtnType | UI:UIMasteryDetail |
| `UIMineCaveCross` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MineCave/UIMineCa...` | 9 | 0 | - | - |
| `UIMineCaveCrossTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MineCave/UIMineCa...` | 9 | 0 | - | - |
| `UIMineCaveLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMineCave/UIMineCaveLog.prefab` | 16 | 5 | - | UI:anim |
| `UIMineCavePopNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/MineCave/MineCave...` | 10 | 1 | - | - |
| `UIMineCaveScoreTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/MineCave/UIMineCa...` | 6 | 0 | - | - |
| `UIMineCaveTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMineCave/UIMineCaveTips.prefab` | 20 | 4 | - | UI:UIOtherPlayerInfo,anim |
| `UIMineCaveUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMineCave/UIMineCaveUnlock.prefab` | 13 | 3 | - | UI:Instance |
| `UIMineCountTipsPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MinePlunder/UIMin...` | 11 | 0 | - | - |
| `UIMinePlunderCrossPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MinePlunder/UIMin...` | 17 | 1 | - | - |
| `UIMinePlunderDispatch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MinePlunder/UIMin...` | 19 | 2 | - | - |
| `UIMineTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MinePlunder/UIMin...` | 16 | 4 | - | UI:UIMineTips |
| `UIModifyPassword` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIModifyPassword.prefab` | 16 | 6 | btnForget | MSG:MsgDefines.AccountForgetPassword,MsgDefines.CheckAccountPassword ; U... |
| `UIModifySuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIModifySuccess.prefab` | 5 | 1 | - | - |
| `UIMomentCommentOperatorView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatItemOperator/UIC...` | 29 | 10 | _btnAt, _btnCopy, _btnDel, _btnReply, _btnRevert, _btnShowReply | UI:UIChatReport,self |
| `UIMomentDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatVi...` | 53 | 18 | CanShowAutoTraBtn, SetChatBtnInternal, UIButton, UICommonFullTop/... | UI:UIChatReport,self |
| `UIMomentFollowList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatMo...` | 15 | 3 | UIButton, return_btn, return_btn_path | UI:self |
| `UIMomentLikeHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatMo...` | 15 | 3 | UIButton, return_btn, return_btn_path | UI:self |
| `UIMomentNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatVi...` | 16 | 4 | UIButton, return_btn, return_btn_path | UI:self |
| `UIMomentPost` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatPo...` | 23 | 8 | InitButtonState, Root/BigBtnBlue, Root/BigBtnBlue/btnText, Root/B... | UI:self |
| `UIMomentPostNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatPo...` | 34 | 8 | InitButtonState | UI:self |
| `UIMomentSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatMoments/UIChatVi...` | 15 | 5 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | UI:UIChatPrivateRoomSet |
| `UIMonsterSuperChallengeRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 14 | 3 | - | MSG:MsgDefines.CallChallengeActEndlessBoss |
| `UIMonsterSuperChallengeRank02` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 24 | 6 | Music_Effect_Button, rankToggle, rewardToggle | - |
| `UIMonsterTowerAlFightRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 15 | 1 | - | - |
| `UIMonsterTowerAlLVRewardInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 14 | 0 | - | - |
| `UIMonsterTowerComing` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 12 | 1 | - | - |
| `UIMonsterTowerRewardGet` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 18 | 5 | - | - |
| `UIMonsterTowerTips` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UIMo...` | 11 | 1 | ClickBtn, UIButton, btn_choice_path, return_btn, return_btn_path,... | - |
| `UIMonthCardPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMonthCardActivity/UIMonthCardP...` | 5 | 1 | OnButtonCloseClicked, UIButton, buttonClose, buttonPanel | - |
| `UIMonthMsgPass` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/WeeklyCardByM...` | 24 | 3 | - | UI:UIPopupPackage,self |
| `UIMoreInformation` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIMoreInformation/UIMoreInfo...` | 28 | 11 | GetTabBtnData, RefreshTabBtns, tabBtnData, tab_btns | UI:self |
| `UIMoveCity` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIMoveCity.prefab` | 52 | 15 | OnCancelBtnClick, OnConfirmBtnClickReal, btnNum | MSG:MsgDefines.MoveCrossServer ; UI:anim |
| `UIMoveCityAssemble` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMoveCityTip/UIMoveCityAssemble...` | 0 | 0 | - | - |
| `UIMoveCityTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMoveCityTip/UIMoveCityTip.prefab` | 10 | 3 | - | UI:anim |
| `UIMoving` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIMoving.prefab` | 12 | 3 | - | UI:anim |
| `UIMsgAwait` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Common/DisconnectView.prefab` | 9 | 2 | - | UI:self |
| `UIMultiBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMultiBuy/UIMultiBuy.prefab` | 24 | 9 | maxBtn | UI:self |
| `UIMultiLanguageFloatingBall` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/UIMultiLanguageFeedback/UIMultiL...` | 18 | 7 | Music_Effect_Button, OnClickBtnScore, btnScore, btnTip, btnTip1 | UI:MainUI_SU,UIMultiLanguagePop |
| `UIMultiLanguagePop` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/UIMultiLanguageFeedback/UIMultiL...` | 13 | 5 | Music_Effect_Button | MSG:MsgDefines.GetTranslateRateReward |
| `UIMultiLanguagePush` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMultiLanguageFeedback/UIMultiL...` | 7 | 2 | Music_Effect_Button | UI:UIActivityCenterTable |
| `UIMusicFestivalGameGrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestivalGa...` | 15 | 4 | - | UI:self |
| `UIMusicFestivalGameGuide` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestivalGa...` | 12 | 2 | - | UI:self |
| `UIMusicFestivalGameScene` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestivalGa...` | 29 | 8 | - | UI:self |
| `UIMusicFestivalRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestivalRa...` | 14 | 4 | - | UI:self |
| `UIMusicFestivalRulesScore` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestivalRu...` | 21 | 3 | ToggleControlBorS, toggle, toggle1, toggleList | UI:self |
| `UIMusicFestivalTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIOktoberFest/UIMusicFestivalTa...` | 18 | 5 | mBtnClaimAll | MSG:MsgDefines.TaskRewardBatch ; UI:self |
| `UINewBuildUpgrade` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_NewBuildUpgrade/UINewBuildUpg...` | 69 | 10 | SU_ToggleBuildBubble, tabBtns | UI:UIBuildDetails,UIGiftPackage,UIItemTips |
| `UINewHero` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UINewHero.prefab` | 13 | 5 | ToggleRecruitScene, tabButtons | UI:self |
| `UINewNvJingBuyResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstPay/UIFirstPayNewNvJingRe...` | 12 | 1 | - | - |
| `UINoInput` | `UIContainer/Dialog` | `Assets/Main/Prefabs/Guide/UINoInput.prefab` | 15 | 3 | - | UI:anim |
| `UINoticeAlCompeteTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UINoticeAlCompeteTips.prefab` | 21 | 3 | - | UI:anim |
| `UINoticeEquipTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UINoticeEquipTips.prefab` | 21 | 3 | - | UI:anim |
| `UINoticeGivingRoseTips` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UINoticeGivingRos...` | 25 | 5 | - | UI:anim |
| `UINoticeHeroTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UINoticeHeroTips.prefab` | 19 | 3 | - | UI:anim |
| `UINoticePhonographTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographTips03....` | 18 | 3 | - | UI:anim |
| `UINoticeTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/Common/UINoticeTips.prefab` | 19 | 3 | - | UI:anim |
| `UINoticeValentineFoxTips` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UIGivingRoses/UINoticeValentine...` | 18 | 3 | - | UI:anim |
| `UINpcQN` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UINpcQA/UINpcQN.prefab` | 16 | 6 | _next_btn | MSG:MsgDefines.UserNpcQuestionnaire ; UI:self |
| `UIOneClickSweepMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/OneClickSweep/UIOneClickSwee...` | 25 | 11 | SweepToggleItem_ | UI:UIOneClickSweepReport,UIOneClickSweepRule |
| `UIOneClickSweepNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/OneClickSweep/UIOneClickSwee...` | 9 | 1 | cond2InfoBtn | UI:UIHeroTip |
| `UIOneClickSweepReport` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/OneClickSweep/UIOneClickSwee...` | 22 | 7 | - | - |
| `UIOneClickSweepRule` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/OneClickSweep/UIOneClickSwee...` | 6 | 0 | - | - |
| `UIOtherPlayerInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIPlayerInfoView.prefab` | 27 | 11 | Music_Effect_Button, PLayerInfoButtonType, UIButton, backBtn | UI:UIChangeName,UIHeadIconShow,UIMoreInformation |
| `UIOverlord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordMain.prefab` | 13 | 3 | Music_Effect_Button, OnButtonCloseClick, Root/Bottom/CloseBtn, UI... | - |
| `UIOverlordArchivePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordArchivePopup....` | 12 | 4 | Music_Effect_Button, OnButtonCloseClicked, UIButton, buttonClose | UI:UIOverlordFilePopup |
| `UIOverlordChallengePop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordChallengePop....` | 18 | 10 | Music_Effect_Button, OnButtonChestClick, OnButtonCloseClick, OnBu... | UI:UIOverlordHuntMilestone,self |
| `UIOverlordChangeNamePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordChangeNamePop...` | 6 | 3 | Music_Effect_Button, OnButtonChangeClicked, OnButtonCloseClicked,... | - |
| `UIOverlordFilePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordFilePopup.prefab` | 9 | 4 | Music_Effect_Button, OnButtonCloseClicked, Root/CommonBtnCircle, ... | MSG:MsgDefines.OverlordFileRewardGet ; UI:UIActivityRewardTip |
| `UIOverlordHuntMilestone` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordHuntMilestone...` | 14 | 5 | - | UI:self |
| `UIOverlordMilitaryRatingPreviewPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordMilitaryRatin...` | 6 | 1 | Music_Effect_Button, OnButtonCloseClicked, UIButton, UICommonPopU... | - |
| `UIOverlordMilitaryUpgradePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordMilitaryUpgra...` | 16 | 6 | Music_Effect_Button, OnButtonCloseClicked, OnButtonMarchPropertyT... | UI:UIOverlordMilitaryRatingPreviewPopup |
| `UIOverlordPropertyPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordPropertyPopup...` | 6 | 1 | Music_Effect_Button, OnButtonCloseClicked, UIButton, UICommonMidP... | - |
| `UIOverlordRankPreviewPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordRankPreviewPo...` | 8 | 3 | Music_Effect_Button, OnButtonCloseClicked, Root/Bottom/CloseBtn, ... | - |
| `UIOverlordSelectPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordSelectPopup.p...` | 7 | 5 | BtnClose, Music_Effect_Button, OnButtonCloseClicked, OnConfirmBtn... | - |
| `UIOverlordSkillTipPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordSkillTipPopup...` | 5 | 0 | UIButton, buttonClose | - |
| `UIOverlordStarLevelUpPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordStarLevelUpPo...` | 10 | 1 | Music_Effect_Button, OnButtonCloseClicked, UIButton, buttonClose | - |
| `UIOverlordTreatment` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Overlord/UIOverlordTreatment.prefab` | 14 | 5 | Music_Effect_Button, OnButtonArchiveClicked, OnButtonCloseClicked... | UI:UIOverlordArchivePopup |
| `UIPCWebView` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIPCWebView/UIPCWebView.prefab` | 2 | 0 | Middle/TitleBar/btnClose, UIButton, btnClose | - |
| `UIPINCodeInput` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UIPINCodeInput.prefab` | 18 | 5 | - | MSG:MsgDefines.SendSetPasswordVerifyCode,MsgDefines.UserPasswordCheck ; ... |
| `UIPINVerifyMailCode` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIAccount/UIPINVerifyMailCode.pr...` | 13 | 3 | - | MSG:MsgDefines.CheckPasswordVerifyCode ; UI:self |
| `UIPVEChallengeWarning` | `UIContainer/Info` | `Assets/Main/Prefabs/PVE/UIPVPStartFightBox.prefab` | 25 | 6 | BtnClick_Close, todayToggle | UI:self |
| `UIPVEDetectSpecialJumpLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVEDetectSpeci...` | 11 | 2 | BtnClick_Close | MSG:MsgDefines.DetectEventPveBatch ; UI:UIDetectEvent |
| `UIPVEDetectSpecialJumpResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVEDetectSpeci...` | 14 | 2 | - | UI:UIDetectEvent |
| `UIPVEEnterLevel` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPVE/UIPVEEnterLevel.prefab` | 6 | 2 | OnBtnClick, UIButton, UIToggle, close_btn, close_btn_path, panelC... | UI:UISetting,self |
| `UIPVEHeroBossFightStart` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIPVE/UIPVEHeroBossFightStart.pr...` | 3 | 2 | - | UI:self |
| `UIPVELevelLoading` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIPVE/UIPVELevelLoading.prefab` | 6 | 2 | - | UI:self |
| `UIPVELevelReward_SU` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPVE/UIPVELevelReward.prefab` | 23 | 4 | - | UI:anim |
| `UIPVELoading` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UIPVE/UIPVELoading.prefab` | 16 | 2 | - | - |
| `UIPVEMonsterToLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPVE/UIPVEMonsterToLevel.prefab` | 13 | 4 | - | UI:self |
| `UIPVEResult` | `UIContainer/Background` | `Assets/Main/Prefabs/Guide2/UIGuidePioneerResult.prefab` | 35 | 19 | UIButton, WorldTileBtnType, btn, continueBtnText, functionBtnRoot... | UI:ArenaBattle,UIHeroList,UIPVPDamageDate |
| `UIPVEScene` | `UIContainer/Background` | `Assets/Main/Prefabs/Guide2/UIGuidePioneer.prefab` | 212 | 65 | Barrel_ToggleFormationHeroLevelBar, CheckOnekeyFillHeroBtn, FastC... | UI:UIArenaPanel,UICampBonus,UICommonShop |
| `UIPVETowerClimbJump` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVETowerClimbJ...` | 5 | 1 | - | MSG:MsgDefines.UserStartBarrelPushBatch |
| `UIPVETowerClimbJumpReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIJeepAdventure/UIPVETowerClimbJ...` | 11 | 1 | - | - |
| `UIPVPDamageDate` | `UIContainer/Normal` | `Assets/Main/Prefabs/PVE/UIPVPDamageDate.prefab` | 19 | 2 | - | UI:self |
| `UIPVPStartFight` | `UIContainer/Normal` | `Assets/Main/Prefabs/PVE/UIPVPStartFight.prefab` | 23 | 4 | - | UI:self |
| `UIPVPStartFightVS` | `UIContainer/Normal` | `Assets/Main/Prefabs/PVE/UIPVEStartFightVS.prefab` | 2 | 1 | - | - |
| `UIPackageContentTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFirstPay/UIPackageContentTip.p...` | 13 | 5 | - | UI:self |
| `UIParkourBattleLose` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIParkourBattleLose.prefab` | 23 | 8 | Barrel_BtnFeedBackClick, OnBtnBackClick, barrel/sound_btn_back, b... | UI:UIAssistanceHeroSettle,UIFiveStarFeedBack |
| `UIParkourBattleMain` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ParkourBattle/UIParkourBattleMai...` | 66 | 16 | Barrel_ShowBtnDefence, Common_Btn_Defence_out, PlayFirstPayBtnUnl... | UI:UIFirstCharge,UIFirstCharge2,UIParkourBattleMain |
| `UIParkourBattleWin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Barrel/UIParkourBattleWin.prefab` | 57 | 18 | OnBtnContinueClick, autoContinueBtnText, btnContinue, btnGoldCont... | UI:UIArmyTips,UIAssistanceHeroSettle,UIPVEResult |
| `UIParkourMap` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ParkourBattle/ParkourMapPanel.pr...` | 17 | 4 | - | UI:UIParkourMap |
| `UIParkourThreeChoices` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ParkourBattle/UIParkourThreeChoi...` | 10 | 1 | - | - |
| `UIPathArrow` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIPathArrow.prefab` | 19 | 2 | - | UI:anim |
| `UIPersonalArmsConvert` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIPersonalArmsCon...` | 0 | 0 | - | - |
| `UIPersonalArmsProbability` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/PersonalArms/UIPe...` | 0 | 0 | - | - |
| `UIPersonalArmsReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/PersonalArms/UIPe...` | 0 | 0 | - | - |
| `UIPersonalArmsScore` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIPersonalArmsSco...` | 0 | 0 | - | - |
| `UIPhonographBuffDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographBuffDet...` | 13 | 3 | - | UI:UIPhonographBuffDetail |
| `UIPhonographMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographMain.pr...` | 38 | 12 | btnNum, presentBtn, toggleAction, toggleText | UI:UIRecordPlayer |
| `UIPhonographMarquee` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographMarquee...` | 17 | 5 | - | UI:anim |
| `UIPhonographPayment` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographPayment...` | 8 | 1 | - | UI:OpenWinAnimFalse |
| `UIPhonographPlayTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographTips02....` | 7 | 0 | - | - |
| `UIPhonographRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhonograph/UIPhonographRecord....` | 14 | 2 | - | UI:OpenWinAnimFalse |
| `UIPhotoWall` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhotoWall/UIPhotoWall.prefab` | 21 | 4 | Music_Effect_Button, RefreshToggle, Toggle1, ToggleTag, toggleTag... | UI:self |
| `UIPhotoWallBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhotoWall/UIPhotoWallBox.prefab` | 15 | 2 | - | MSG:MsgDefines.SurvivalHeroCollectionRewardView |
| `UIPhotoWallDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPhotoWall/UIHeroPhotoList.prefab` | 23 | 2 | - | UI:self |
| `UIPiggyBank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPiggyBank/UIPiggyBank.prefab` | 12 | 2 | - | UI:self |
| `UIPiggyBankTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPiggyBank/UIPiggyBankTip.prefab` | 19 | 3 | - | UI:UIGiftPackage,self |
| `UIPinForget` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPin/UIPinForget.prefab` | 14 | 3 | - | MSG:MsgDefines.PinPwdForget ; UI:self |
| `UIPinInput` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPin/UIPinInput.prefab` | 21 | 8 | - | MSG:MsgDefines.NewAccount ; UI:UIPinForget,self |
| `UIPinSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPin/UIPinSet.prefab` | 17 | 7 | - | UI:UIPinForget,UIPinInput,UIPinUseSet |
| `UIPinUseSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPin/UIPinUseSet.prefab` | 13 | 3 | - | MSG:MsgDefines.PinPwdCheckFrequency ; UI:self |
| `UIPing` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/UIPing.prefab` | 12 | 3 | OnRedemptionBtnClick, UIButton, close_btn, redemption_btn, redemp... | UI:self |
| `UIPlaceBauble` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuild.prefab` | 30 | 11 | OnCancelBtnClick | UI:anim |
| `UIPlaceBuild` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuild.prefab` | 41 | 14 | OnCancelBtnClick, cancel_btn | MSG:MsgDefines.FindMainBuildInitPosition,MsgDefines.FreeBuildingPlaceMai... |
| `UIPlaceBuildWorld` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuildWorld.prefab` | 42 | 12 | OnCancelBtnClick, cancel_btn | MSG:MsgDefines.FindMainBuildInitPosition,MsgDefines.FreeBuildingPlaceMai... |
| `UIPlaceWorldBuild` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Build/UIPlaceBuildWorld.prefab` | 34 | 11 | OnCancelBtnClick | MSG:MsgDefines.WorldMoveAllianceBuilding ; UI:anim |
| `UIPlayerChangeHeadIcon` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIPlayerChangeHeadIc...` | 30 | 13 | OnBtnIconClick, UIButton, close_btn, frame_btn, frame_btn_redDot,... | MSG:MsgDefines.UserChangePic,MsgDefines.UserDeletePicFromOld ; UI:UIHead... |
| `UIPlayerGenderSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIPlayerGenderSelect...` | 18 | 4 | - | UI:self |
| `UIPlayerHeadIconSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIPlayerHeadIconSele...` | 8 | 4 | Music_Effect_Button, UIButton, close_btn, close_btn_path, headIco... | UI:self |
| `UIPlayerInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIPlayerInfoView.prefab` | 28 | 9 | Music_Effect_Button, PLayerInfoButtonType | UI:UIChangeNameGender,UIHeadIconShow,UIMoreInformation |
| `UIPlayerMarketEarnPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Thanksgiving2026/UIT...` | 12 | 3 | - | - |
| `UIPlayerMarketRpsPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Thanksgiving2026/UIT...` | 40 | 9 | Button, Music_Effect_Button, UIButton, btn, unity_uibutton | UI:UIPlayerMarketSellPopup |
| `UIPlayerMarketSellPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/BigActivity/Thanksgiving2026/UIT...` | 43 | 6 | btnNum | - |
| `UIPointOrigin` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/WeeklyCardByM...` | 17 | 2 | - | UI:self |
| `UIPoliceInsigniaShow` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPoliceInsigniaShow/UIPoliceIns...` | 5 | 0 | - | - |
| `UIPoliceStation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIPoliceStation.p...` | 16 | 4 | info_btn | UI:UIHeroTip,self |
| `UIPopupPackage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPopupPackage/UIPopupPackage.pr...` | 25 | 5 | ShowLeftRotateButton | UI:self |
| `UIPositionAdd` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIPositionAdd.prefab` | 53 | 15 | ClearToggleCallbacks, InitToggleCallbacks, OnClickDelBtn, PlayBut... | MSG:MsgDefines.WorldFavoDel ; UI:UIItemTips |
| `UIPositionAppointSearch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneAppointmentSele...` | 21 | 8 | Music_Effect_Button, RefreshBtn, UIButton, close_btn, confirm_btn... | MSG:MsgDefines.AllianceRankList,MsgDefines.SendContactGiftSearch |
| `UIPositionFavorite` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionFavorite.prefab` | 17 | 6 | ToggleControlBorS, UIButton, UIToggle, close_btn, close_btn_path,... | UI:anim |
| `UIPositionShare` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionShare.prefab` | 20 | 7 | UIButton, close_btn, copy_btn, return_btn | MSG:MsgDefines.ChatPushNotice ; UI:UIPositionShareConfirm,self |
| `UIPositionShareConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionShareConfirm.prefab` | 21 | 9 | ShouldShowNoMoreTipToggle, UIButton, back_toggle, btnYesCost, btn... | MSG:MsgDefines.ChatPushNotice,MsgDefines.ThanksGivingStarLevelShare ; UI... |
| `UIPositionTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIPositionTips.prefab` | 16 | 6 | Music_Effect_Button, UIButton, btn, btn_favorite, btn_favorite_tx... | UI:UIPositionFavorite,UISearch,self |
| `UIPresentBigShow` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentBigShow.prefab` | 14 | 2 | - | UI:UIPresentList |
| `UIPresentEgg` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentEgg.prefab` | 8 | 2 | - | - |
| `UIPresentGetRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentGetReward.prefab` | 24 | 3 | - | UI:UIGiftPackageRewardGet,UIPositionShare |
| `UIPresentHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILike/UIPresentHistory.prefab` | 17 | 1 | UIButton, UICommonPopUpTitle/CloseBtn, closeBtn | - |
| `UIPresentLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentLevel.prefab` | 29 | 5 | - | UI:UIGiftPackageRewardGet |
| `UIPresentList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentList.prefab` | 25 | 6 | RefreshBtn, sendBtnTxt | UI:UIGiftPackageRewardGet,UIPresentSend |
| `UIPresentSend` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentSend.prefab` | 36 | 9 | RefreshBtn, sendBtnTxt | UI:self |
| `UIPresentSendTips` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentSendTips.prefab` | 18 | 4 | - | - |
| `UIPresentShowList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentPreview.prefab` | 27 | 8 | RefreshBtn, okBtn, okBtnTxt | UI:UIGiftPackageRewardGet |
| `UIPresidentAppoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePresidentAppoin...` | 16 | 5 | Music_Effect_Button, UIButton, close_btn, close_btn_path, confirm... | UI:self |
| `UIPresidentTakesTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIThrone/UIPresidentTakesTips.pr...` | 17 | 4 | - | - |
| `UIPreviewMineCave` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MineCave/MineCave...` | 19 | 4 | - | - |
| `UIPrivacy` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIPrivacy.prefab` | 9 | 6 | Align/node_age/toggle, Align/node_age/toggle/Background/VX, Align... | UI:self |
| `UIPrivacy2` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIAgreementSign.prefab` | 5 | 4 | Root/BigBtnAgree, Root/BigBtnAgree/btnText, Root/CommonCloseBtnWh... | MSG:MsgDefines.UserAgreeTos |
| `UIPrivacy3` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIPrivacy3.prefab` | 4 | 3 | BtnGo/LeftBtn, BtnGo/LeftBtn/LeftBtnName, BtnGo/RightBtn, BtnGo/R... | - |
| `UIPrivilegeShopProbabilityPopup` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/GiftPackage/PrivilegeShop/Privil...` | 8 | 1 | - | UI:UIPrivilegeShopProbabilityPopup |
| `UIPrograssBar` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/Survival/UIPrograssBar.prefab` | 7 | 0 | - | - |
| `UIProsperPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIProsper/UIProsperPopup.prefab` | 3 | 0 | - | - |
| `UIPublishALAnnouncement` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/ChatVote/UIPublishAL...` | 8 | 2 | Music_Effect_Button, UIButton, close_btn, close_btn_path, return_... | UI:self |
| `UIPuzzleMonsterCreate` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPuzzleMonster/UIPuzzleMonsterC...` | 15 | 5 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | UI:self |
| `UIPuzzleMonsterList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPuzzleMonster/UIPuzzleMonsterL...` | 12 | 3 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | UI:self |
| `UIPuzzleMonsterRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPuzzleMonster/UIPuzzleMonsterR...` | 11 | 5 | ToggleControlBorS, UIButton, UIToggle, close_btn, close_btn_path,... | UI:self |
| `UIPveActMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPveAct/UIPveActMain.prefab` | 27 | 6 | - | UI:self |
| `UIPveActRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPveAct/UIPveActRank.prefab` | 21 | 4 | - | UI:self |
| `UIPveBattleSoldierList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Guide2/UIPveBattleSoliderList.prefab` | 7 | 1 | - | UI:self |
| `UIQAWebview` | `UIContainer/TopMax` | `Assets/Main/Prefabs/UI/UIAccount/UIQAWebview.prefab` | 6 | 1 | - | - |
| `UIQRScanner` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Common/UIQRScanner.prefab` | 6 | 0 | - | - |
| `UIQTEView` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/Survival/UIQTE/UIQTEView.prefab` | 8 | 1 | - | UI:OpenWinAnimFalse |
| `UIRadarCloud` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRadarCloud/UIRadarCloud.prefab` | 4 | 0 | - | - |
| `UIRankDetailList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/UIRankDetailList.prefab` | 26 | 9 | UIButton, closeAll_btn, close_btn | MSG:MsgDefines.CampPveHeroInfo ; UI:UIAllianceDetail,UIOtherPlayerInfo,self |
| `UIRankNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Set/UIRankNew.prefab` | 24 | 10 | RefreshTypeBtnSelect, UIButton, buttonListInType, close_btn | UI:GetInstance,UIAllianceDetail,UIOtherPlayerInfo |
| `UIRankTable` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/UIRankTable.prefab` | 18 | 7 | UIButton, close_btn, toggleN, togglesTbN | UI:GetInstance,UIHeroRankList,self |
| `UIRecruitLotteryTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIHero/New/UIRecruitLotteryTip.p...` | 8 | 3 | - | UI:UIHeroRecruit,anim |
| `UIRedEquipBossRallyReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMythic/UIMythicGearRallyPopup....` | 10 | 1 | - | - |
| `UIRedEquipmentActivityUpcomingPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRedGear/UIRedGearPopuop.prefab` | 6 | 1 | OnButtonGotoClicked, Root/BigBtnYellow, Root/BigBtnYellow/btnText... | - |
| `UIRedenvelopeEggReceive` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeEggRece...` | 16 | 4 | - | UI:self |
| `UIRedenvelopeRageListPopupView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeRageLis...` | 7 | 0 | Music_Effect_Button, UIButton, close_btn, close_btn_path, panel_b... | - |
| `UIRedenvelopeReceive` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 17 | 5 | - | MSG:MsgDefines.GetRedPack ; UI:self |
| `UIRedenvelopeReceiveInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 22 | 6 | - | MSG:MsgDefines.GetRedPack ; UI:self |
| `UIRedenvelopeReceiveInfoCarAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 21 | 5 | - | MSG:MsgDefines.GetRedPack ; UI:_self |
| `UIRedenvelopeReceiveInfoCarWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 21 | 6 | - | MSG:MsgDefines.GetRedPack ; UI:_self |
| `UIRedenvelopeReceiveInfoNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 21 | 5 | - | MSG:MsgDefines.GetRedPack ; UI:self |
| `UIRedenvelopeReceiveInfoWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 21 | 6 | - | MSG:MsgDefines.GetRedPack ; UI:self |
| `UIRedenvelopeReceiveNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 16 | 4 | - | MSG:MsgDefines.GetRedPack ; UI:self |
| `UIRedenvelopeReceiveWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeReceive...` | 16 | 4 | - | MSG:MsgDefines.GetRedPack ; UI:self |
| `UIRedenvelopeSelectView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ChatNew/UIRedenvelopeSelectView....` | 15 | 2 | ImgBg/BigBtnChoose, ImgBg/BigBtnChoose/btnText, Music_Effect_Butt... | - |
| `UIRedenvelopeSend` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeSend.pr...` | 14 | 6 | Music_Effect_Button, UIButton, _sendRed_btn, btn_bg, closeBtn, cl... | MSG:MsgDefines.SendRedPack ; UI:self |
| `UIRedenvelopeSend1` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeSend1.p...` | 40 | 15 | ToggleControlBorS, ToggleGroupTop/Toggle, UIToggle, toggle, toggl... | MSG:MsgDefines.QueryAllianceMemberActRecords,MsgDefines.SendRedPack ; UI... |
| `UIRedenvelopeSendWorld` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeSendWor...` | 36 | 14 | RedPacket/ToggleGroup/CheckBox_, TextToggle, ToggleControlBorS, U... | MSG:MsgDefines.SendRedPack ; UI:UIRedenvelopeSend |
| `UIRedenvelopeSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRedEnvelope/UIRedenvelopeSendS...` | 9 | 1 | Music_Effect_Button, UIButton, _sendRed_btn, btn_sendRed_path, re... | - |
| `UIRedenvelopeView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIRedenvelopeView.pr...` | 16 | 5 | Music_Effect_Button, OnInfoBtnClick, UIButton, btn_close, btn_clo... | MSG:MsgDefines.GetRedPack ; UI:UIHeroTip,self |
| `UIRefundDeductAll` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundDeductAll.prefab` | 15 | 3 | - | MSG:MsgDefines.CheckedRefundDeduct ; UI:UIRefundDeductHistory |
| `UIRefundDeductGold` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundDeductGold.prefab` | 12 | 3 | - | MSG:MsgDefines.CheckedRefundDeduct ; UI:UIRefundDeductHistory |
| `UIRefundDeductHistory` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundRecord.prefab` | 19 | 3 | - | - |
| `UIRefundDeductItem` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundDeductItem.prefab` | 15 | 3 | - | MSG:MsgDefines.CheckedRefundDeduct ; UI:UIRefundDeductHistory |
| `UIRefundDeductOptional` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundDeductItem.prefab` | 32 | 12 | - | UI:UIAddAccount |
| `UIRefundDeductTransition` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIRefund/UIRefundExchange.prefab` | 10 | 1 | - | - |
| `UIReportEquipTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/SU_ItemEquipTips.prefab` | 16 | 2 | - | UI:self |
| `UIReportEquipTip4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/SU_ItemEquipTips.prefab` | 16 | 2 | - | UI:self |
| `UIReportResourceIncomeTips` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/Mail/UIReportResourceIncomeTips...` | 3 | 1 | Music_Effect_Button | - |
| `UIReportWeaponTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/SU_ItemWeaponTips.prefab` | 13 | 1 | - | - |
| `UIReportWeaponTip4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Common/SU_ItemWeaponTips.prefab` | 13 | 1 | - | - |
| `UIResSupport` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIAllianceResAssist.prefab` | 29 | 5 | Music_Effect_Button, OnClickConfirmBtn, OnClickTaxBtn, SetButtonS... | UI:self |
| `UIReserveCamp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmyCamp.prefab` | 17 | 5 | reserve_btn, reserve_info_btn | UI:UIHeroTip,UIReserveToSoldier |
| `UIReserveToSoldier` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIArmyInfo/UIArmyCampConvert.prefab` | 16 | 2 | - | UI:UIReserveToSoldier |
| `UIResourceBag` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceBag.prefab` | 52 | 21 | CloseMoreBtn, GetMoreBtnParent, HideMoreBtn, Music_Effect_Button,... | MSG:MsgDefines.ItemBuyAndUse,MsgDefines.ItemUse ; UI:self |
| `UIResourceCost` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UITransportRes/UIResourceCostPan...` | 19 | 2 | - | - |
| `UIResourceExchange` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIResource/UIResourceExchange.pr...` | 16 | 2 | Music_Effect_Button, UIButton, add_btn, btn_2, btn_2_path, btn_2_txt | UI:UICapacityFull |
| `UIResourceGetTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIResource/UIResourceGetTip.prefab` | 5 | 1 | - | - |
| `UIResourceItemLack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResourceItemLack/UIResourceIte...` | 11 | 1 | - | - |
| `UIResourceLack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceLackView.pr...` | 11 | 1 | - | UI:UIResourceLackNew |
| `UIResourceLackNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceLackNew.prefab` | 26 | 9 | infoBtnN, toggleIndex, toggleList | MSG:MsgDefines.UseResItemMulti ; UI:UIFormationTip,UIResourceBag,UIResou... |
| `UIResourceLackNew1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceLackNew1.pr...` | 37 | 15 | CloseMoreBtn, GetMoreBtnParent, OnBuyBtnClick, OnSelectResourceLa... | MSG:MsgDefines.UseResItemMulti ; UI:UIFormationTip,UIResourceBag,UIResou... |
| `UIResourceLackNew2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceLackNew2.pr...` | 16 | 4 | - | UI:self |
| `UIResourceReplenish` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIResource/UIResourceReplenish.p...` | 31 | 6 | SelectResourceLackToggleIndex | MSG:MsgDefines.UseResItemMulti ; UI:OpenWinAnimTrue,UIResourceLackNew1 |
| `UIReviewFishHandbook` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonReview/UISeasonReviewHan...` | 21 | 8 | toggles | MSG:MsgDefines.GetFishAtlasInfo ; UI:self |
| `UIReviewFossilHandbook` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonReview/UISeasonReviewHan...` | 14 | 4 | - | MSG:MsgDefines.GetSeason4FossilBookInfo ; UI:UIReviewFossilHandbookPrevi... |
| `UIReviewFossilHandbookPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonReview/UISeasonReviewHan...` | 14 | 4 | - | MSG:MsgDefines.SeasonGoldActiveFossil ; UI:self |
| `UIRewardBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRewardBox/UIRewardBox.prefab` | 15 | 2 | OnClickBtn, UIButton, btn | - |
| `UIRewardLevelUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/BarterShopNotice/...` | 35 | 3 | Music_Effect_Button | - |
| `UIRewardParkourConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIParkourConfirm.prefab` | 11 | 0 | - | - |
| `UIRewardParkourMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIParkourView.prefab` | 16 | 2 | barrel/sound_btn_back | - |
| `UIRewardParkourResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIParkour/UIParkourResult.prefab` | 17 | 2 | leftBtn, leftBtnText, rightBtn, rightBtnEffect, rightBtnText | UI:UIRewardParkourMain |
| `UIRewardVListTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRewardVListTip/UIRewardVListTi...` | 13 | 5 | UIButton, return_btn, return_btn_path | MSG:MsgDefines.SurvivalBigBox ; UI:OpenWinAnimTrue |
| `UIRoamingBossNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMonst...` | 4 | 2 | - | UI:UIActivityCenterTable,UIRoamingBossNotice |
| `UIRoamingBossRankReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMonst...` | 7 | 1 | - | - |
| `UIRoamingBossRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMonst...` | 10 | 2 | - | - |
| `UIRoamingBossRewardPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMonst...` | 10 | 3 | - | - |
| `UIRobotPack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRobotPack/UIRobotPack.prefab` | 15 | 4 | - | UI:MainUI_SU,self |
| `UIRobotWarsRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/RobotWars/UIRobot...` | 1 | 0 | - | - |
| `UIRocketFailedLanding` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIRocketFailedLanding/UIRocketFa...` | 19 | 1 | - | UI:anim |
| `UIRoleCreate` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIRoleCreate.prefab` | 12 | 3 | - | MSG:MsgDefines.NewAccount ; UI:self |
| `UIRoleLogin` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIRoleLogin.prefab` | 12 | 3 | - | MSG:MsgDefines.UserCleanPost ; UI:self |
| `UIRoles` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UISetting/UIRoles.prefab` | 20 | 4 | - | UI:self |
| `UIRotationNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UIVerticalSwitchPop....` | 9 | 2 | - | - |
| `UIRubyAchievementTitlePopup` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/UIRudy/UIRubyAchievementTitl...` | 14 | 4 | - | UI:UIRubyAchievementTitlePopup |
| `UIRuinCityLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UIAllianceLog.prefab` | 14 | 4 | UIButton, close_btn, close_btn_path | UI:self |
| `UIRuinRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIRuinRecord.prefab` | 16 | 5 | toggleList | UI:self |
| `UIRuinRewardDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/RuinsKillingEnemy...` | 13 | 5 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | MSG:MsgDefines.WorldGetAllianceCityDetail ; UI:self |
| `UIRuinsHistoryRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/RobotWars/UIRobot...` | 13 | 1 | - | UI:self |
| `UIRuinsRankDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/RobotWars/UIRobot...` | 12 | 1 | - | UI:self |
| `UIRuinsReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UISiegeReward.prefab` | 17 | 3 | - | UI:self |
| `UIRuinsRewardPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIRobotWarsReward.prefab` | 4 | 3 | - | UI:self |
| `UISUWorldCollect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldCollect.prefab` | 35 | 10 | Music_Effect_Button | UI:UIPositionShare,UISearch,anim |
| `UISceneCloud` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UICrossDisconnectView.prefab` | 9 | 1 | - | - |
| `UISceneNoInput` | `UIContainer/Scene` | `Assets/Main/Prefabs/Guide/UINoInput.prefab` | 14 | 3 | - | UI:anim |
| `UIScience` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScience.prefab` | 49 | 8 | GetGuideBtn | UI:UISpeed,self |
| `UIScienceBuildList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceBuildList.prefab` | 13 | 2 | - | UI:self |
| `UIScienceInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceInfoPortrait....` | 58 | 10 | add_speed_btn_text, btnGoActive, btn_go, immediatelyBtnSpendColor... | MSG:MsgDefines.QueueCcdMNew,MsgDefines.ScienceResearchNew ; UI:UISpeed |
| `UIScienceTab` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceTab.prefab` | 12 | 1 | - | - |
| `UIScienceTabLock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScience/UIScienceTabLock.prefab` | 19 | 3 | - | UI:self |
| `UIScreenCenterTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIScreenCenterTips/UIScreenCente...` | 12 | 3 | - | UI:self |
| `UIScrollPack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScrollPack/UIScrollPack.prefab` | 14 | 3 | - | UI:self |
| `UIScrollPackNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIScrollPackNew/UIScrollPackNew....` | 27 | 3 | - | UI:self |
| `UISearch` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UISearch/UISearch.prefab` | 46 | 15 | UIButton, UIToggle, boss_btn, close_btn | MSG:MsgDefines.FindMonster ; UI:anim |
| `UISearchLod` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISearch/UISearchLod.prefab` | 20 | 4 | - | UI:self |
| `UISearchMonster` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UISearch/UISearchMonster.prefab` | 48 | 15 | UIButton, UIToggle, boss_btn, close_btn | MSG:MsgDefines.FindMonster ; UI:anim |
| `UISeason4DinosaurBossPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/AncientDi...` | 23 | 4 | Music_Effect_Button | UI:self |
| `UISeason4DinosaurBossRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/AncientDi...` | 15 | 3 | - | UI:self |
| `UISeason4DinosaurBossRewardAndRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/AncientDi...` | 19 | 9 | Music_Effect_Button, toggle1, toggle2 | UI:self |
| `UISeason4DinosaurBossShow` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/AncientDi...` | 6 | 1 | - | UI:_ENV |
| `UISeason4DinosaurEggHatchConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 9 | 4 | Btns/BtnBack, Btns/BtnBack/btnText, Btns/BtnConfirm, Btns/BtnConf... | MSG:MsgDefines.SnowManReceiveSnowMan ; UI:self |
| `UISeason4DinosaurEggHatchCutto` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 8 | 2 | Music_Effect_Button, OnClickCloseBtn, UIButton, closeBtn | UI:self |
| `UISeason4DinosaurEggHatchLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 14 | 2 | - | - |
| `UISeason4DinosaurEggHatchMission` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 17 | 2 | - | - |
| `UISeason4DinosaurEggHatchRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/DinosaurE...` | 16 | 3 | lvInfoBtn | UI:UIHeroTip |
| `UISeason4FossilCollection` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/FossilCol...` | 37 | 17 | Music_Effect_Button, RefreshRedBtn, btnLeft, btnRight, btnToNew, ... | MSG:MsgDefines.GetSeason4FossilBookInfo ; UI:UIAllianceBuildingCollect,U... |
| `UISeason4FossilCollectionConvert` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/FossilCol...` | 21 | 6 | Music_Effect_Button | MSG:MsgDefines.ExchangeSeason4FossilBookItem ; UI:self |
| `UISeason4FossilCollectionObtain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/FossilCol...` | 16 | 4 | Music_Effect_Button | MSG:MsgDefines.Season4FossilBookReward ; UI:UISeason4FossilCollectionCon... |
| `UISeasonActGuideTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/SeasonActivity/UI...` | 15 | 2 | - | UI:anim |
| `UISeasonBaronessInfoS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Baroness/...` | 20 | 3 | - | UI:self |
| `UISeasonBaronessPushS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Baroness/...` | 15 | 1 | - | - |
| `UISeasonBaronessTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Baroness/...` | 15 | 1 | - | - |
| `UISeasonEarlBattleTimeS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Earl/UISe...` | 20 | 5 | save_btn | - |
| `UISeasonEarlDonatePopS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Earl/UISe...` | 17 | 2 | - | - |
| `UISeasonEntrance` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonEntrance/UISeasonEntranc...` | 17 | 2 | - | UI:UISeasonGlory |
| `UISeasonForceLackView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonForceLackView.p...` | 8 | 1 | - | - |
| `UISeasonForceList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonForceList/U...` | 18 | 2 | - | UI:self |
| `UISeasonForceRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonForceRank/U...` | 18 | 3 | - | UI:self |
| `UISeasonForceReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonForceReward...` | 22 | 7 | - | MSG:MsgDefines.SeasonForceGetAllReward ; UI:self |
| `UISeasonForceRewardDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonGroundManageBox...` | 19 | 3 | - | - |
| `UISeasonForceStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonForceStageRewar...` | 16 | 3 | - | - |
| `UISeasonForceStageReward01` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISeason/UISeasonForceStageRewar...` | 16 | 6 | - | - |
| `UISeasonForceTitleUnlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonGroundManage/UI...` | 12 | 0 | - | - |
| `UISeasonGhostKingLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Earl/UISe...` | 7 | 0 | - | - |
| `UISeasonGhostKingRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossRankView.prefab` | 10 | 4 | BtnGM, Music_Effect_Button, ToggleControlBorS, UIButton, UIToggle... | - |
| `UISeasonGloryDeclareEndPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonGlory/UISeasonG...` | 18 | 4 | - | UI:self |
| `UISeasonGloryGroup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGloryGroup/...` | 16 | 2 | - | - |
| `UISeasonGloryGroupS3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/basic/UIS...` | 16 | 2 | - | - |
| `UISeasonGloryGroupS4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Basic/UIS...` | 16 | 2 | - | - |
| `UISeasonGloryGroupS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Basic/UIS...` | 16 | 2 | - | - |
| `UISeasonGloryRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGloryRecord...` | 18 | 2 | - | UI:self |
| `UISeasonGloryReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGloryReward...` | 22 | 9 | RefreshBtnState, allotBtn, joinBtn | MSG:MsgDefines.SeasonBalancePackageViewOpen |
| `UISeasonGloryRewardAllot` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGloryReward...` | 20 | 8 | receiveBtn, recordBtn | MSG:MsgDefines.SeasonBalanceReceivePackage ; UI:UISeasonGloryRecord |
| `UISeasonGloryRewardAllotS3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/basic/UIS...` | 20 | 8 | receiveBtn, recordBtn | MSG:MsgDefines.SeasonBalanceReceivePackage ; UI:UISeasonGloryRecord |
| `UISeasonGloryRewardAllotS4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Basic/UIS...` | 20 | 8 | receiveBtn, recordBtn | MSG:MsgDefines.SeasonBalanceReceivePackage ; UI:UISeasonGloryRecord |
| `UISeasonGloryRewardAllotS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Basic/UIS...` | 20 | 8 | receiveBtn, recordBtn | MSG:MsgDefines.SeasonBalanceReceivePackage ; UI:UISeasonGloryRecord |
| `UISeasonGloryRewardS3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/basic/UIS...` | 22 | 9 | RefreshBtnState, allotBtn, joinBtn | MSG:MsgDefines.SeasonBalancePackageViewOpen |
| `UISeasonGloryRewardS4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Basic/UIS...` | 22 | 9 | RefreshBtnState, allotBtn, joinBtn | MSG:MsgDefines.SeasonBalancePackageViewOpen |
| `UISeasonGloryRewardS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Basic/UIS...` | 22 | 9 | RefreshBtnState, allotBtn, joinBtn | MSG:MsgDefines.SeasonBalancePackageViewOpen |
| `UISeasonGloryRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGloryRule/U...` | 17 | 4 | - | MSG:MsgDefines.ClientTriggerTask ; UI:self |
| `UISeasonGlorySelectMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGlorySelect...` | 19 | 6 | - | MSG:MsgDefines.SeasonBalanceGiveAlliesPackages,MsgDefines.SeasonBalanceM... |
| `UISeasonGlorySelectMemberS3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/basic/UIS...` | 19 | 6 | - | MSG:MsgDefines.SeasonBalanceGiveAlliesPackages,MsgDefines.SeasonBalanceM... |
| `UISeasonGlorySelectMemberS4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Basic/UIS...` | 19 | 6 | - | MSG:MsgDefines.SeasonBalanceGiveAlliesPackages,MsgDefines.SeasonBalanceM... |
| `UISeasonGlorySelectMemberS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Basic/UIS...` | 19 | 6 | - | MSG:MsgDefines.SeasonBalanceGiveAlliesPackages,MsgDefines.SeasonBalanceM... |
| `UISeasonGlorySweep` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGlorySweep/...` | 19 | 2 | - | UI:self |
| `UISeasonGrading` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeason/UISeasonGroundManage/UI...` | 13 | 1 | - | - |
| `UISeasonGradingS3` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/basic/UIS...` | 13 | 1 | - | - |
| `UISeasonGradingS4` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Basic/UIS...` | 13 | 1 | - | - |
| `UISeasonGradingS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Basic/UIS...` | 13 | 1 | - | - |
| `UISeasonGroundManage` | `UIContainer/Background` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonGroundManag...` | 48 | 11 | - | MSG:MsgDefines.SeasonForceReward |
| `UISeasonGroundManageS3` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/basic/UIS...` | 46 | 11 | - | MSG:MsgDefines.SeasonForceReward |
| `UISeasonGroundManageS4` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/Basic/UIS...` | 46 | 11 | - | MSG:MsgDefines.SeasonForceReward |
| `UISeasonGroundManageS5` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Basic/UIS...` | 46 | 11 | - | MSG:MsgDefines.SeasonForceReward |
| `UISeasonHeroPreview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonHeroPreview/UISeasonHero...` | 16 | 5 | - | UI:UIHeroInfo,self |
| `UISeasonHint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonHint/UISeasonHint.prefab` | 17 | 1 | - | - |
| `UISeasonIceCaveAllianceOccupyRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/UIS...` | 17 | 5 | ToggleControlBorS, UIButton, UICommonPopUpTitle/CloseBtn, _bg_Clo... | UI:self |
| `UISeasonIceCaveCandidate` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/Can...` | 23 | 8 | RefreshSureBtnState, sureBtn | MSG:MsgDefines.SetIceCaveCandidate ; UI:UISeasonIceCaveCandidate |
| `UISeasonIceCaveGuide` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/Ice...` | 12 | 1 | - | UI:self |
| `UISeasonIceCaveInfoPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/UIS...` | 23 | 11 | ClearToggleScrollView, IceCaveToggleType, ToggleClick, UIButton, ... | UI:self |
| `UISeasonIceCaveInfoPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/UIS...` | 21 | 6 | - | UI:self |
| `UISeasonIceCaveLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/UIS...` | 15 | 3 | Music_Effect_Button, UIButton, close_btn, toggleN, togglesTbN | UI:self |
| `UISeasonIceCaveRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/Rec...` | 30 | 11 | diamondInfoBtn, redPocketBtn, ticketBtn, tipsInfoBtn | MSG:MsgDefines.IceCaveOpenFishing ; UI:UIHeroTip,UIOtherPlayerInfo,UISea... |
| `UISeasonIceCaveUserOccupyRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/UIS...` | 15 | 4 | Music_Effect_Button, UIButton, close_btn, close_btn_path | UI:self |
| `UISeasonIceCaveWorldRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonIceCave/Wor...` | 27 | 5 | tipsBtn | UI:UIHeroTip,UISeasonIceCaveWorldRank |
| `UISeasonMoonlightAttrPreviewS5` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 11 | 2 | btn_Effect | UI:UIHeroTip,self |
| `UISeasonMoonlightAttrS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 13 | 1 | - | UI:self |
| `UISeasonMoonlightGetS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 12 | 2 | - | UI:self |
| `UISeasonMoonlightLevelUpS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 8 | 3 | - | UI:self |
| `UISeasonMoonlightLogS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 10 | 2 | - | UI:self |
| `UISeasonMoonlightRuleS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 16 | 7 | tab_toggles | UI:self |
| `UISeasonMoonlightSelectS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 22 | 11 | Music_Effect_Button, ToggleFilterList, btnNum, btn_deploy, btn_re... | MSG:MsgDefines.MoonlightCollectionDeploy ; UI:self |
| `UISeasonMoonlightSummonResultS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/Moonlight...` | 8 | 3 | - | UI:self |
| `UISeasonMultExchange` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeason/UISeasonMultExchang...` | 21 | 6 | - | MSG:MsgDefines.BarterShopExchange ; UI:self |
| `UISeasonNightFallsClockS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightFall...` | 46 | 5 | Music_Effect_Button | UI:UISeasonNightFallsRule |
| `UISeasonNightFallsComing` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightFall...` | 20 | 3 | Music_Effect_Button | - |
| `UISeasonNightFallsRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightFall...` | 9 | 3 | Music_Effect_Button, OnClickBtnInfo, ToggleControlBorS, UIButton,... | UI:UIHeroTip |
| `UISeasonNightFallsRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightFall...` | 21 | 3 | Music_Effect_Button | - |
| `UISeasonNightFallsTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightFall...` | 16 | 2 | - | - |
| `UISeasonNightSacrificePushS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightSacr...` | 15 | 3 | - | MSG:MsgDefines.FindBloodMoonFloatMonster |
| `UISeasonNightSacrificeRankRewardS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/NightSacr...` | 23 | 7 | - | - |
| `UISeasonRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/SeasonRank/UI...` | 18 | 5 | Music_Effect_Button, UIButton, UICommonPopUpTitle/bg_mid/CloseBtn... | UI:UIHeroTips,UISeasonRankReward,self |
| `UISeasonRankList` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/UISeasonRankL...` | 7 | 3 | Music_Effect_Button, UIButton, closeAll_btn, close_btn, toggle, t... | UI:self |
| `UISeasonRankReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/ActivityCenter/SeasonRank/UI...` | 14 | 3 | - | UI:UISeasonRank |
| `UISeasonReview` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonReview/UISeasonReviewMai...` | 28 | 12 | - | MSG:MsgDefines.SeasonAllianceSnapShot ; UI:UIReviewFishHandbook,UISeason... |
| `UISeasonReviewRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonReview/UISeasonReviewRes...` | 12 | 3 | Root/ToggleGroupSubTab/Toggle, ToggleControlBorS, UIToggle, toggle | UI:self |
| `UISeasonReviewRule` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISeasonReview/UISeasonReviewRul...` | 14 | 1 | - | UI:self |
| `UISeasonTradeMasterRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeasonT...` | 15 | 4 | Music_Effect_Button, UIButton, close_btn, close_btn_path | UI:UISeasonTradeMasterRankView |
| `UISeasonTradeMasterRankViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradePost...` | 15 | 4 | Music_Effect_Button, UIButton, close_btn, close_btn_path | UI:UISeasonTradeMasterRankView |
| `UISeasonTradePostInfoView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeasonT...` | 26 | 13 | ClearToggleScrollView, Music_Effect_Button, OnToggleMoveIn, OnTog... | UI:UISeasonTradePostInfoView |
| `UISeasonTradePostInfoViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradePost...` | 26 | 13 | ClearToggleScrollView, Music_Effect_Button, OnToggleMoveIn, OnTog... | UI:UISeasonTradePostInfoView |
| `UISeasonTradePostLogView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeasonT...` | 15 | 3 | Music_Effect_Button, UIButton, close_btn, toggleN, togglesTbN | UI:UISeasonTradePostLogView |
| `UISeasonTradePostLogViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradePost...` | 15 | 3 | Music_Effect_Button, UIButton, close_btn, toggleN, togglesTbN | UI:UISeasonTradePostLogView |
| `UISeasonTradePostRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeasonT...` | 17 | 5 | ToggleControlBorS, UIButton, UICommonPopUpTitle/bg_mid/CloseBtn, ... | UI:UISeasonTradePostRankView |
| `UISeasonTradePostRankViewS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradePost...` | 17 | 5 | ToggleControlBorS, UIButton, UICommonPopUpTitle/bg_mid/CloseBtn, ... | UI:UISeasonTradePostRankView |
| `UISeasonTradePostRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeasonT...` | 23 | 4 | - | UI:UISeasonTradePostRecord |
| `UISeasonTradePostRecordS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradePost...` | 23 | 4 | - | UI:UISeasonTradePostRecord |
| `UISeasonTradePostStore` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season4/UISeasonT...` | 35 | 11 | buyNumBtn, openBtn, saleBtn, taxBtn | MSG:MsgDefines.TradeStoreBuyItem,MsgDefines.TradeStoreOpen ; UI:UIGiftPa... |
| `UISeasonTradePostStoreS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/TradePost...` | 35 | 11 | buyNumBtn, openBtn, saleBtn, taxBtn | MSG:MsgDefines.TradeStoreBuyItem,MsgDefines.TradeStoreOpen ; UI:UIGiftPa... |
| `UISeasonTrialRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SeasonSac...` | 16 | 6 | - | - |
| `UISeasonWeek` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISeasonWeek/UISeasonWeek.pr...` | 24 | 6 | pic_btn | UI:UIHeroTip,self |
| `UISelectArmy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISelectArmy/UISelectArmy.prefab` | 27 | 4 | - | UI:self |
| `UISelectDigFinalReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISelectDigFinalReward/UISelectD...` | 20 | 8 | GetRewardInfoBackToggle, SaveRewardInfoBackToggle | UI:self |
| `UISelectLevel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UISelectLevel/UIThrough...` | 23 | 2 | - | UI:self |
| `UISellConfirm` | `UIContainer/TopCanvas` | `Assets/Main/Prefabs/UI/UICapacity/UISellConfirm.prefab` | 18 | 8 | back_toggle | MSG:MsgDefines.SoldResourceItem ; UI:self |
| `UISetAlOfficialPos` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/AlliancePosition/UI...` | 2 | 0 | - | - |
| `UISetAttackTimes` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetAttackTimes/UISetAttackTime...` | 13 | 4 | OnClickCloseBtn | UI:self |
| `UISetPlayerNation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetPlayerNation/UISetPlayerNat...` | 2 | 1 | Music_Effect_Button | - |
| `UISetPushNotification` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Set/New/UISetPushNotificatio...` | 18 | 3 | - | UI:SetPushNotification |
| `UISetting` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISetting.prefab` | 27 | 4 | - | UI:UIPlayerInfo,self |
| `UISettingAccount` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UISettingAccount.prefab` | 24 | 13 | Music_Effect_Button, gameCenterTextInfoBtn | UI:GetInstance,UIAccountUnbind,UIAddAccount |
| `UISettingAccount1` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UISettingAccount02.prefab` | 16 | 9 | Music_Effect_Button, gameCenterTextInfoBtn | UI:UIAccountUnbind,UIAddAccountBefore,UICreateAccount |
| `UISettingAccount2` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UISettingAccountNew.pr...` | 32 | 19 | Music_Effect_Button, bottomBtnLayout, managementBtn, pgsRewardBtn | UI:GetInstance,UIAccountUnbind,UIAddAccountBefore |
| `UISettingAlliance` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Alliance/UISettingAlliance.p...` | 42 | 25 | SetCountryBtnN, UIButton, abbr_change_btn, announce_btn, changeAl... | MSG:MsgDefines.AllianceChangeAttributes ; UI:UIAllianceChangeAbbr,UIAlli... |
| `UISettingBlock` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/Friend/UISettingBlock.prefab` | 20 | 4 | toggle, toggleList | UI:self |
| `UISettingChangeUid` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingChangeUid.prefab` | 13 | 6 | ToggleControlBorS, back_toggle | UI:self |
| `UISettingConsole` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingConsole.prefab` | 32 | 18 | RefreshBtnBarrelGMInfo, RefreshBtnLuaProfiler, ToggleConsole, Tog... | UI:SU_NewHero,UIQRScanner,self |
| `UISettingDebugReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Common/UISettingDebugReward.p...` | 1 | 1 | Btn, UIButton, btn, btnClose | MSG:MsgDefines.SurvivalDebugReward |
| `UISettingFlag` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingFlag.prefab` | 18 | 2 | - | UI:self |
| `UISettingGameSpeed` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingGameSpeed.prefab` | 14 | 2 | - | UI:self |
| `UISettingLanguage` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingLanguage.prefab` | 25 | 6 | Music_Effect_Button | UI:self |
| `UISettingNotice` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingNotice.prefab` | 19 | 2 | - | UI:self |
| `UISettingPointsReward` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISetting/UISettingPointsReward....` | 23 | 15 | PGS_REWARD_CLAIM_BTN, UIButton, claimBtn, claimBtnText, claim_btn... | UI:self |
| `UISettingRedemptionCode` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingRedemptionCod...` | 15 | 3 | - | UI:self |
| `UISettingSet` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UISetting/UISettingSet.prefab` | 16 | 3 | - | UI:self |
| `UISettingSoundTest` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingSoundTest.prefab` | 13 | 6 | ToggleControlBorS, back_toggle | UI:SUSoundUtil |
| `UISettingTimeControl` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingTimeControl.p...` | 13 | 0 | - | - |
| `UISettingVietCommunityPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISetting/UISettingVietCommunity...` | 19 | 6 | - | UI:self |
| `UISevenDay` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISevenDay/UISevenDay.prefab` | 45 | 21 | clickBtn/ItemIcon, gotoBtn, receiveAllBtn, receiveAllBtnGrayText,... | MSG:MsgDefines.UserDayActInfo ; UI:SevenDayBox,UIGiftPackageRewardGet,UI... |
| `UISevenDayNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISevenDay/UISevenDayNew.prefab` | 64 | 28 | challengeSkinBtn, clickBtn/ItemIcon, close_btn, funBtn, funMainBt... | MSG:MsgDefines.DetectEventLauraRewardReceive,MsgDefines.DetectEventRewar... |
| `UISevenDayNewGuide` | `UIContainer/Normal` | `Assets/Main/Prefabs/Guide2/UIGuideTalkSevenDay.prefab` | 7 | 2 | - | - |
| `UISevenLogin` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISevenLogin/UISevenLogin.prefab` | 17 | 5 | Music_Effect_Button | MSG:MsgDefines.ReceiveSevenDayLoginReward ; UI:self |
| `UIShareMail` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIShareMail.prefab` | 13 | 6 | CheckShowShareBtn, OnClickBtnClose, OnClickShareBtn, UIButton, _b... | UI:UIChatNew,UIPositionShare,self |
| `UIShareMail4` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Mail/UIShareMail.prefab` | 24 | 7 | CheckShowShareBtn, _btnShare | UI:UIChatNew,UIPositionShare |
| `UIShowBlack` | `UIContainer/Guide` | `Assets/Main/Prefabs/Guide/UIShowBlack.prefab` | 25 | 6 | BtnCanClickTime, DeleteBtnTimer, btnTimer, next_btn, timer_btn_ac... | UI:anim |
| `UIShowFakeNewHero` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UIShowFakeNewHero.prefab` | 16 | 5 | Music_Effect_Button | UI:self |
| `UISignOfCommand` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIPlanOfBattlefieldCommand/UISig...` | 18 | 4 | BtnClick_Close, btnInfo | UI:UIItemTips,self |
| `UISkinChoiceChest` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISkinBox/UISkinChoiceChestPopup...` | 48 | 14 | RefreshBtnState, SetBtnClaimEnabled, btnClaim, btnPending | MSG:MsgDefines.ItemUse ; UI:self |
| `UISkinChoiceChestHero` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISkinBox/UISkinChoiceChestHeroP...` | 43 | 14 | RefreshBtnState, SetBtnClaimEnabled, btnClaim, btnPending | MSG:MsgDefines.ItemUse ; UI:self |
| `UISkinShop` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIDecoration/UISkinShop.prefab` | 42 | 13 | Music_Effect_Button, OnCityToggleClick, city_toggle, togglelistty... | UI:GetInstance,UIDecorateUnlock,UIDecorationEffect |
| `UISmallPeopleBook` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleBook....` | 10 | 2 | btnClose, btnSave | - |
| `UISmallPeopleBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleVisit...` | 25 | 3 | - | - |
| `UISmallPeopleBuildInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleBuild...` | 16 | 4 | Music_Effect_Button | UI:UISmallPeopleSurvivorsList |
| `UISmallPeopleFilter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleFilte...` | 6 | 2 | upgradeToggles, workingToggles | UI:self |
| `UISmallPeopleReplaceConfirm` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleRepla...` | 9 | 2 | - | - |
| `UISmallPeopleReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIHero/New/UISmallPeopleReward.p...` | 3 | 0 | - | - |
| `UISmallPeopleSurvivors` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleSurvi...` | 10 | 1 | - | - |
| `UISmallPeopleSurvivorsList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleSurvi...` | 16 | 4 | SwitchBtnCanUse, btnSend, btnSendTxt | UI:UISmallPeopleReplaceConfirm |
| `UISmallPeopleTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleTask....` | 10 | 0 | - | - |
| `UISmallPeopleTaskDispatch` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleTaskD...` | 13 | 0 | - | - |
| `UISmallPeopleVisit` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISmallPeople/UISmallPeopleVisit...` | 8 | 1 | - | - |
| `UISnowCountDown` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UISnowCountdown.prefab` | 13 | 1 | - | - |
| `UISnowManBubbleTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMan/U...` | 15 | 2 | - | UI:UIActivityCenterTable |
| `UISnowManLogs` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMan/U...` | 14 | 2 | - | - |
| `UISnowManRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season3/SnowMan/U...` | 16 | 3 | lvInfoBtn | UI:UIHeroTip |
| `UISoliderGetTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISoliderGetTip/UISoliderGetTip....` | 10 | 2 | - | UI:anim |
| `UISpearLevelUpNotice` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISpear/UISpearLevelUpNotice.prefab` | 10 | 4 | - | - |
| `UISpearPersonalRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpear/UISpearPersonalRank.prefab` | 29 | 7 | toggle | UI:self |
| `UISpearPreviewSkillWindow` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UISpear/UISpearPreviewSkillWindo...` | 6 | 0 | - | - |
| `UISpearWarzoneRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpear/UISpearWarzoneRank.prefab` | 27 | 8 | toggle | UI:self |
| `UISpearWorldPoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpear/UISpearWorldPoint.prefab` | 60 | 18 | AddBtnTimer, BtnAnim, BtnAnimTime, BtnCellCircle, BuildBtnList, C... | UI:UIActivityCenterTable,UIPositionAdd,UIPositionShare |
| `UISpeed` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpeed/UISpeed.prefab` | 70 | 24 | CheckIfShowVsBtn, CloseMoreBtn, GetAllianceVsBtnIcon, GetMoreBtnP... | MSG:MsgDefines.BuildCcdMNew,MsgDefines.GirlCollectSpeedUp ; UI:UISpeedRe... |
| `UISpeedAutoSelect` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISpeed/UISpeedAutoSelect.prefab` | 26 | 8 | second_tip_tipbutton | MSG:MsgDefines.ArmyAdd,MsgDefines.FreeBuildingUpNew,MsgDefines.ScienceRe... |
| `UISpeedUpConfirm` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/UISpeedUpConfirm/UISpeedUpConfir...` | 16 | 4 | - | MSG:MsgDefines.QueueCcdMNew ; UI:self |
| `UIStorageShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShop.prefab` | 21 | 7 | - | UI:UIPositionShare,UIStorageShopList,self |
| `UIStorageShopHistory` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopHisto...` | 17 | 2 | - | UI:self |
| `UIStorageShopList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopList....` | 20 | 4 | - | MSG:MsgDefines.StorageShopGetShopList ; UI:self |
| `UIStorageShopMain` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopMain....` | 21 | 9 | history_btn_name, toggleNList | UI:UIPositionShare,UIStorageShopHistory,self |
| `UIStorageShopRetrieve` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopRetri...` | 12 | 3 | - | MSG:MsgDefines.StorageShopRemoveGoods ; UI:self |
| `UIStorageShopRetrieveNew` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UIStorageShopRetri...` | 16 | 7 | - | MSG:MsgDefines.StorageShopGolloesBuy,MsgDefines.StorageShopRemoveGoods ;... |
| `UIStoryHangup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStory/UIStoryHangup.prefab` | 21 | 4 | receive_btn | - |
| `UIStoryHangupChange` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStory/UIStoryHangupChange.prefab` | 11 | 0 | - | - |
| `UIStoryRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStory/UIStoryRank.prefab` | 15 | 1 | - | - |
| `UIStoryResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStory/UIStoryResult.prefab` | 19 | 4 | - | - |
| `UIStrongCommander` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/StrongCommander/U...` | 47 | 19 | - | UI:UIActivityCenter,UIOtherPlayerInfo,UIPersonalArmsScore |
| `UIStrongCommanderPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/StrongCommander/U...` | 19 | 7 | - | UI:self |
| `UIStrongCommanderPre` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/StrongCommander/U...` | 19 | 3 | - | UI:self |
| `UIStrongCommanderRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/StrongCommander/U...` | 26 | 10 | ToggleControlBorS, dayToggleGroupN, dayToggleList, toggle, toggle... | UI:UIPlayerInfo,self |
| `UIStrongCommanderTask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/StrongCommander/U...` | 15 | 2 | - | UI:self |
| `UISubtitle` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISubtitle/UISubtitle.prefab` | 15 | 2 | - | UI:self |
| `UITaskPromptTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/SU_MainTask/UITaskPromptTips.prefab` | 6 | 1 | - | UI:self |
| `UIThanksGivingRankPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/FoodFestival/UIFoodFestivalRank...` | 21 | 6 | ToggleControlBorS, UIButton, UIFoodFestivalPopUpTitle/Bg_mid/Clos... | UI:self |
| `UIThanksGivingTurkeyRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingTurkey...` | 27 | 3 | - | UI:self |
| `UIThanksgivingStarAchievementView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingStar...` | 18 | 3 | - | MSG:MsgDefines.ThanksGivingStarLevelReward ; UI:self |
| `UIThanksgivingStarListView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingStar...` | 17 | 2 | - | UI:self |
| `UIThanksgivingStarNoticePresentTips` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingStar...` | 18 | 3 | - | UI:anim |
| `UIThanksgivingStarRankView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingStar...` | 24 | 5 | BtnName, BtnTab1, BtnType, ToggleControlBorS, UIToggle, toggle | MSG:MsgDefines.ThanksGivingStarRankInfo ; UI:UIThanksgivingStarRewardVie... |
| `UIThanksgivingStarRewardView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingStar...` | 23 | 5 | BtnName, BtnType, ToggleControlBorS, UIToggle, toggle, toggle_path | MSG:MsgDefines.ThanksGivingStarRankReward ; UI:UIThanksgivingStarRankVie... |
| `UIThanksgivingStarScoreView` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/UIThanksgivingStar...` | 17 | 2 | - | UI:self |
| `UIThirdPaymentInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/ThirdPayment/UITh...` | 11 | 2 | - | UI:self |
| `UIThirdPaymentShop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/ThirdPayment/UITh...` | 23 | 6 | - | UI:UICapacityBoxSelect |
| `UIThirdPaymentShopPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/ThirdPayment/UITh...` | 25 | 6 | - | UI:UICapacityBoxSelect |
| `UIThroneAllianceAddPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneAllianceAddPopu...` | 7 | 2 | - | - |
| `UIThroneKingdomApplyPos` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneKingdomApplyPos...` | 12 | 6 | Music_Effect_Button, ToggleControlBorS, UIButton, UIToggle, back_... | - |
| `UIThroneKingdomApplyPosHistory` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneKingdomApplyPos...` | 6 | 3 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | - |
| `UIThroneKingdomAssumedsuccessfull` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneKingdomAssumeds...` | 5 | 0 | - | - |
| `UIThronePosition` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePosition.prefab` | 15 | 5 | - | UI:UIRankTable,UIThronePositionApplyCondition,self |
| `UIThronePositionApplyCondition` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePositionApplyCo...` | 19 | 6 | - | MSG:MsgDefines.AllianceRankList ; UI:UICommonChangeValue |
| `UIThronePresidentHonour` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePresidentHonour...` | 20 | 3 | - | UI:UIOtherPlayerInfo,self |
| `UIThronePresidentReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThronePresidentReward...` | 16 | 4 | - | UI:UIThroneRewardSelectMember,UIThroneSendList,self |
| `UIThroneRewardSelectMember` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneRewardSelectMem...` | 24 | 8 | - | MSG:MsgDefines.SendContactGiftSearch ; UI:self |
| `UIThroneSendList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneSendList.prefab` | 18 | 2 | - | UI:self |
| `UITimeCompePop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITimeCompePop/UITimeCompePop.pr...` | 14 | 2 | - | UI:self |
| `UITimeCompeRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITimeCompeRank/UITimeCompeRank....` | 15 | 4 | - | UI:self |
| `UITimelineJump` | `UIContainer/TopMost` | `Assets/Main/Prefabs/Guide/UITimelineJump.prefab` | 13 | 2 | skip_btn | - |
| `UITimelineMask` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITimelineMask/UITimelineMask.pr...` | 2 | 2 | - | UI:UITimeCompeRank |
| `UITimelineMaskNoInput` | `UIContainer/Dialog` | `Assets/Main/Prefabs/Guide/UITimelineMaskNoInput.prefab` | 0 | 0 | - | - |
| `UITitleDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIDecoration/UITitleDetail.prefab` | 18 | 4 | - | UI:UIPositionShare,anim |
| `UITowerRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UITowerRecord.prefab` | 21 | 6 | ToggleControlBorS_1, ToggleControlBorS_2, toggleList | UI:self |
| `UITradeCenter` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UITradingCenter/UITradeCenter.pr...` | 27 | 7 | Music_Effect_Button, ToggleControlBorS, UIButton, UIToggle, btn, ... | MSG:MsgDefines.TradingBuy,MsgDefines.TradingSell ; UI:anim |
| `UITrain` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UITrain/UITrain.prefab` | 92 | 38 | GoToBtnClick, ImmediatelyBtnClick, ImmediatelySpeedBtnClick, Musi... | MSG:MsgDefines.ArmyAdd ; UI:UISpeed |
| `UITrainBattleRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UITrainBattleRecord....` | 14 | 3 | - | UI:UITrain3V3BattleResult,self |
| `UITrainBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UITrainBuy.prefab` | 17 | 9 | - | MSG:MsgDefines.AllianceTrainBuy ; UI:CloseSelf,self |
| `UITrainDriverInvite` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UILWRailway/UITrainDriverInvite....` | 15 | 6 | - | MSG:MsgDefines.AllianceTrainAssign ; UI:self |
| `UITrialDifficultyReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/MonsterTower/UITr...` | 17 | 6 | - | - |
| `UITriggerGiveItem` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIStorageShop/UITriggerGiveItem....` | 6 | 3 | - | MSG:MsgDefines.SU_PveTriggerSubmitItem ; UI:self |
| `UITurkeyCookDetailsPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/Thanksgiving/ThanksGivingTurkey...` | 24 | 6 | - | UI:self |
| `UITutorialAnimation` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICityScene/UITutorialAnimation....` | 7 | 3 | - | UI:self |
| `UITutorialAnimation1` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICityScene/UITutorialAnimation1...` | 8 | 0 | - | - |
| `UITutorialAnimation2` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UICityScene/UITutorialAnimation2...` | 3 | 0 | - | - |
| `UIUnLockSuccess` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIFactory/UIUnLockSuccess.prefab` | 20 | 3 | GuideBtn, Music_Effect_Button | UI:self |
| `UIUnlockCompetition` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIUnlockCompetition/UIUnlockComp...` | 6 | 3 | OnBtnOkClick, UIButton, _cp_btnOk, btnClose, m_btnOk | UI:self |
| `UIUpPower` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/LeadingQuest/UIUp...` | 14 | 2 | - | UI:self |
| `UIVIP19RewardBox` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVIP19RewardBox.prefab` | 10 | 2 | - | UI:self |
| `UIVIP19Rule` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVIP19Rule.prefab` | 12 | 1 | - | UI:self |
| `UIVIP19Task` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVIP19Task.prefab` | 13 | 2 | - | UI:UIVIP19Rule,self |
| `UIVIPPopupSkinInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVIPPopupSkinInfo.prefab` | 14 | 3 | Music_Effect_Button, likeBtn | UI:self |
| `UIVIPRewardPopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVIPRewardPopUp.prefab` | 8 | 1 | - | UI:self |
| `UIVIPUpgradePopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVIPUpgradePopUp.prefab` | 8 | 1 | - | UI:self |
| `UIValentineEventPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxTe...` | 19 | 3 | - | UI:self |
| `UIValentineFoxGiftBoxReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxTe...` | 21 | 8 | Music_Effect_Button, rewardToggle, rulesToggle | UI:self |
| `UIValentineFoxGloryPersonalRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxTe...` | 17 | 8 | rewardToggle | UI:self |
| `UIValentineFoxTeamDailyTaskPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxTe...` | 17 | 2 | - | UI:self |
| `UIValentineFoxTeamDynamicPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxTe...` | 15 | 2 | - | UI:self |
| `UIValentineFoxTeamQuickChat` | `UIContainer/TopMost` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxCa...` | 12 | 3 | Music_Effect_Button | UI:self |
| `UIValentineFoxTeamSuccessPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxTe...` | 15 | 4 | Music_Effect_Button | UI:self |
| `UIValentineNewExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineNewEx...` | 18 | 6 | isMaxBtn, maxBtnN | UI:UIValentineNewExchangeShopBuy |
| `UIValentinePassBuyPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxPa...` | 18 | 3 | - | - |
| `UIValentineSendGiftBigShow` | `UIContainer/TopMost` | `Assets/Main/Prefabs/UI/UIPresent/UIPresentBigShow.prefab` | 9 | 2 | - | - |
| `UIValentineSendGiftCardPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxCa...` | 18 | 11 | ClaimBtn, RefreshClaimBtn, claimBtn, claimBtnText | UI:self |
| `UIValentineSendGiftConfirmPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxCa...` | 18 | 2 | - | UI:UIValentineSendGiftFinalConfirmPop,self |
| `UIValentineSendGiftFinalConfirmPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxCa...` | 16 | 4 | - | UI:self |
| `UIValentineSendGiftFriendPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIValentineFox/UIValentineFoxCa...` | 28 | 6 | - | UI:UIValentineSendGiftConfirmPop,self |
| `UIVerifyMail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIAccount/UIVerifyMail.prefab` | 28 | 10 | - | MSG:MsgDefines.AccountResendMail,MsgDefines.UserBindCancel ; UI:UIAccoun... |
| `UIVip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVip.prefab` | 54 | 12 | info_btn | UI:UICommonShop,UIGiftPackage,UIHeroTip |
| `UIVipAddTime` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVipAddTime.prefab` | 21 | 4 | - | UI:self |
| `UIVipPurchase` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVipPurchases.prefab` | 24 | 7 | FunctionBtnType | UI:UIGiftPackage,UIVIPUpgradePopUp,self |
| `UIVipRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIVip/UIVipRewardTip.prefab` | 9 | 3 | UIButton, return_btn, return_btn_path | UI:OpenWinAnimTrue |
| `UIVolcanoAllianceMarkTip` | `UIContainer/UIResource` | `Assets/Main/Prefabs/UI/UIVolcano/UIVoIcanMainTips.prefab` | 37 | 9 | Btn, BtnClick_Translate | UI:MainUI_SU,UIWorldBlackTile |
| `UIVolcanoAllocableReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoD...` | 32 | 9 | - | UI:UIVolcanoRewardCount,self |
| `UIVolcanoCountdown` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoCountdown/UIV...` | 15 | 1 | - | UI:self |
| `UIVolcanoDistributionPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoDistributionPop...` | 25 | 11 | personToggle | UI:UIVolcanoRank,self |
| `UIVolcanoEditorAttack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoMap/UIVolcano...` | 6 | 2 | - | UI:self |
| `UIVolcanoGuideWindow` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoR...` | 11 | 2 | - | UI:self |
| `UIVolcanoMain` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoMain.prefab` | 71 | 26 | Music_Effect_Button, OnBuffBtnClick, OnGotoBtnClick, RefreshVolca... | UI:UIChatNew,UIHeroTip,UIItemTips |
| `UIVolcanoMoveRule` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoM...` | 14 | 2 | - | UI:self |
| `UIVolcanoPush` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoPush/UIVolcan...` | 12 | 1 | - | UI:self |
| `UIVolcanoRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoRank/UIVolcanoR...` | 25 | 6 | SubToggleControlBorS, Toggle, ToggleControlBorS, personToggle, su... | UI:UIVolcanoRank |
| `UIVolcanoRequestTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoR...` | 15 | 2 | - | UI:self |
| `UIVolcanoReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoReward/UIVolcan...` | 17 | 3 | ToggleControlBorS, toggle, toggle1, toggle2, toggle3, toggleList | UI:UIVolcanoReward |
| `UIVolcanoRewardCount` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVoLcanoGetBoxPopup.p...` | 17 | 2 | - | UI:self |
| `UIVolcanoRewardRecord` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoRewadRecordVi...` | 16 | 3 | - | UI:self |
| `UIVolcanoSetAttack` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoMap/UIVolcano...` | 25 | 9 | Music_Effect_Button, mToggle1, mToggle2 | UI:UIVolcanoGuideWindow,UIVolcanoWarCommonder,self |
| `UIVolcanoToast` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIVolcano/UIVolcanoToast/UIVolca...` | 26 | 6 | - | UI:anim |
| `UIVolcanoWarCommand` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIThrone/UIThroneAppointmentSele...` | 8 | 3 | - | MSG:MsgDefines.AllianceRankList |
| `UIVolcanoWarCommonder` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoC...` | 15 | 3 | - | UI:self |
| `UIVolcanoWarInfo` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoW...` | 13 | 3 | toggleBase, toggleReward, toggleRule | UI:UIDragonExplainPlay,UIVolcanoMain |
| `UIVolcanoWarInvitation` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoW...` | 21 | 2 | - | UI:self |
| `UIVolcanoWarPopupChallenge` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoW...` | 16 | 3 | knowBtn | UI:self |
| `UIVolcanoWarPopupTips` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoW...` | 15 | 3 | challengeBtn | UI:self |
| `UIVolcanoWarWarZoneList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIVolcano/VolcanoInfo/UIVolcanoW...` | 19 | 2 | - | UI:self |
| `UIWarGuardLog` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/CityManage/UIWarGuardLog.prefab` | 14 | 3 | - | - |
| `UIWebPush` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIMain/UIMainWebPush.prefab` | 10 | 3 | Music_Effect_Button, panelCloseBtn | UI:self |
| `UIWeekendChallengCareResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 25 | 11 | OnContinueBtnClick, UIButton | UI:UIPositionShare,UIWeekChallengeResult |
| `UIWeekendChallengeCarGetAche` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/UIMedalGet/UIMedalGetCar.prefab` | 10 | 1 | - | - |
| `UIWeekendChallengeCarRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 32 | 9 | infoBtn, selfTipBtn | UI:UIHeroTip |
| `UIWeekendChallengeCarReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 23 | 8 | infoBtn, selfTipBtn | UI:UIHeroTip,UIWorldBossRank |
| `UIWeekendChallengeRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 32 | 9 | infoBtn, selfTipBtn | UI:UIHeroTip,UIWorldBossRank |
| `UIWeekendChallengeResult` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 23 | 11 | OnContinueBtnClick, UIButton | UI:UIPositionShare,UIWeekChallengeResult |
| `UIWeekendChallengeReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 23 | 8 | infoBtn, selfTipBtn | UI:UIHeroTip,UIWorldBossRank |
| `UIWorldAllianceBossTip` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/World/UIWorldAllianceBossTip.prefab` | 14 | 3 | - | UI:self |
| `UIWorldBattleNews` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/WorldBattleNewsView.prefab` | 17 | 4 | ToggleControlBorS, UIButton, UIToggle, close_btn, close_btn_path,... | UI:self |
| `UIWorldBlackTile` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISearch/UIWorldBlackTile.prefab` | 38 | 20 | CanShowWorldMarkBtn, ImgBg/Btn_mark, ImgBg/Btn_mark/Icon, ImgBg/B... | UI:OpenWinAnimTrue,UIDragonMark,UIMasterySkill |
| `UIWorldBossRank` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossRankView.prefab` | 14 | 7 | BtnGM, Music_Effect_Button, OnBtnGMClick, ToggleControlBorS, UIBu... | MSG:MsgDefines.UserGetActBossRank ; UI:self |
| `UIWorldBossRankPop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossRankPop.prefab` | 18 | 6 | - | MSG:MsgDefines.UserGetActBossMarch ; UI:self |
| `UIWorldBossRankS5` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/Season5/WorldBoss...` | 14 | 7 | BtnGM, Music_Effect_Button, OnBtnGMClick, ToggleControlBorS, UIBu... | MSG:MsgDefines.UserGetActBossRank ; UI:self |
| `UIWorldBossTroop` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBossTroopView.prefab` | 12 | 3 | UIButton, close_btn, close_btn_path, return_btn, return_btn_path | MSG:MsgDefines.UserGetActBossMarch ; UI:self |
| `UIWorldBuff` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldBuff.prefab` | 13 | 1 | - | - |
| `UIWorldBuildList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIWorldBuildList/UIWorldBuildLis...` | 20 | 2 | - | UI:self |
| `UIWorldCityFull` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldCityFull.prefab` | 16 | 3 | - | UI:UIAllianceCity,UIAllianceScienceInfo |
| `UIWorldCollectMessageTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISearch/UIWorldCollectMessageTi...` | 9 | 3 | BtnGo/LeftBtn, BtnGo/LeftBtn/LeftBtnName, BtnGo/RightBtn, BtnGo/R... | UI:OpenWinAnimTrue |
| `UIWorldCupExchangeShopBuy` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupExchang...` | 18 | 6 | isMaxBtn, maxBtnN | UI:UIWorldCupExchangeShopBuy |
| `UIWorldCupMatchDiscussionPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopup/U...` | 37 | 11 | - | UI:self |
| `UIWorldCupPredictionConfirmPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopup/U...` | 24 | 7 | GetAddDecBtnState | UI:self |
| `UIWorldCupRecommendedMatchPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopup/U...` | 20 | 6 | - | UI:self |
| `UIWorldCupRewardGet` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupZombie/...` | 25 | 2 | - | UI:self |
| `UIWorldCupStreakSuccessPopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopup/U...` | 12 | 3 | - | UI:self |
| `UIWorldCupUserMatchSharePopup` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopup/U...` | 24 | 4 | PLayerInfoButtonType | UI:UIChatNew,self |
| `UIWorldCupZombieIntroPanel` | `UIContainer/Dialog` | `Assets/Main/Prefabs/UI/BigActivity/Halloween/UIHallowee...` | 16 | 2 | Music_Effect_Button | UI:self |
| `UIWorldCupZombieLevelReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupZombie/...` | 19 | 4 | - | UI:UIWorldCupZombieLevelReward |
| `UIWorldCupZombiePopTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupZombie/...` | 16 | 2 | - | UI:self |
| `UIWorldCupZombieRewardTip` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupZombie/...` | 12 | 1 | - | UI:self |
| `UIWorldDeclareList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldDeclareList.prefab` | 13 | 2 | UIButton, btnPanel | UI:self |
| `UIWorldDeclareWar` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldDeclareWar.prefab` | 6 | 2 | - | UI:self |
| `UIWorldDeclareWarConditionList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldDeclareWarCondition...` | 7 | 0 | - | - |
| `UIWorldDeclareWarInfo` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldDeclareWarInfo.prefab` | 16 | 4 | _tips_btn | UI:UIItemTips,self |
| `UIWorldDeclareWarRe` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/RobotWars/UIRobot...` | 2 | 1 | - | UI:self |
| `UIWorldMarchDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIForcesDetail/UITroopDetail.prefab` | 26 | 5 | RefreshToggle, toggleIndex, toggleTable | UI:self |
| `UIWorldMultiSelect` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/World/UIWorldMultiSelect.prefab` | 11 | 1 | - | UI:self |
| `UIWorldNewsAbbrDetail` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldNewsAbbrDetail.prefab` | 11 | 2 | UIButton, return_btn, return_btn_path | UI:self |
| `UIWorldNewsTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldBattleNewsTip.prefab` | 13 | 4 | Root/Button, Root/Button/btnTxt, Root/desText/btn_alliance, UIBut... | UI:UIWorldNewsAbbrDetail,self |
| `UIWorldNoSelectable` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UISearch/UIWorldNoSelectable.prefab` | 9 | 2 | - | - |
| `UIWorldOccupyFirst` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIWorldOccupy/UIWorldOccupyFirst...` | 17 | 1 | - | - |
| `UIWorldOccupyMessageBar` | `UIContainer/Info` | `Assets/Main/Prefabs/UI/UIWorldOccupy/UIWorldOccupyMessa...` | 8 | 1 | - | - |
| `UIWorldPoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldPoint.prefab` | 113 | 27 | RefreshBtnName, RefreshGloryWarSwapBtn, RefreshKingdomSwapBtn, Wo... | UI:EventManager,OpenWinAnimFalse,UIDragonMark |
| `UIWorldReminderTips` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldReminder.prefab` | 17 | 3 | - | UI:UIWorldReminderTips |
| `UIWorldResistanceTips` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/World/UIWorldResistanceTips.prefab` | 17 | 7 | buildingGotoBtnLabel | UI:UIActivityCenterTable,UIWorldBuildList |
| `UIWorldRuinsPopUp` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Alliance/UIWorldRuinsPopUp.prefab` | 7 | 2 | UIButton, click_btn, click_btn_path, close_btn, close_btn_path, r... | UI:self |
| `UIWorldShoutTips` | `UIContainer/Info` | `Assets/Main/Prefabs/Slg/UI/ChatNew/UIChatTrumpetNotice....` | 33 | 11 | btnLike, likeBtn | UI:UIChatReport,UIPlayerInfo |
| `UIWorldSiegePoint` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/World/UIWorldSiegePoint.prefab` | 40 | 12 | BtnAnimTime, ClearPendingSiegePointGuideBtnArrow, TakePendingSieg... | UI:UIPositionAdd,UIPositionShare,self |
| `UIWorldTileUI` | `UIContainer/Scene` | `Assets/Main/Prefabs/UI/World/UIWorldTileUI.prefab` | 53 | 14 | BtnBg, GetBuildBtn, GetBuildBtnEnumName, GetFakeBuildBtn, UIWorld... | UI:UIAddStamina,UINewBuildUpgrade,UIWorldTileUI |
| `UIWoundedCompensate` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIWoundedCompensate/UIWoundedCom...` | 23 | 4 | - | MSG:MsgDefines.UserGetDefendWallCompensate ; UI:OpenWinAnimTrue |
| `UIXmasLuckyRollProb` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIXmasLuckyRollProb/UIXmasLuckyR...` | 10 | 0 | - | - |
| `UIZombieBattleMain` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/ParkourBattle/UIZombieBattleMain...` | 35 | 6 | - | UI:UIZombieBattleMain |
| `UI_BuildUseFullScreenDialog` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UI_BuildUseFullScreenDi...` | 6 | 2 | OnClickBtn, UIButton, _cp_btn, m_btn | UI:self |
| `UI_DayNight` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/UIGuideUnlockMask/UIDayNight.prefab` | 7 | 4 | - | UI:self |
| `UI_GetRewardTips` | `UIContainer/Background` | `Assets/Main/Prefabs/UI/Survival/UI_GetRewardTips.prefab` | 4 | 1 | OnBtnOkClick, UIButton, btnClose, m_btnOk | - |
| `UI_GuideFullScreenDialog` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/SU_Common/UI_GuideFullScreenDial...` | 28 | 6 | OnClickBtn, OnClickSkipBtn, UIButton, m_btn, m_skip_btn, m_skip_b... | UI:self |
| `UI_GuideMoviePrologue` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UI_GuideMoviePrologue.p...` | 9 | 3 | OnClickBtn, UIButton, m_btn | UI:self |
| `UI_PicGuide` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/Survival/UI_PicGuide_New.prefab` | 16 | 7 | UIButton, close_btn, close_btn_path, close_btn_text, close_btn_te... | UI:self |
| `UI_PicGuideList` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/Survival/UI_PicGuideList.prefab` | 11 | 3 | UIButton, closeBtn, closeBtn1 | UI:self |
| `UI_SUBuildRepair` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/UIBuildUpgrade/UIBuildRecover.pr...` | 11 | 1 | - | MSG:MsgDefines.SU_BuildRepair |
| `UI_VideoPlayer` | `UIContainer/Guide` | `Assets/Main/Prefabs/UI/SU_Common/UIVideoLayer.prefab` | 16 | 4 | OnClickBtnSkip, UIButton, btnShowSkip, m_btnSkip | UI:UI_VideoPlayer |
| `UiChrsitmasExchangeShopBuyPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UIChristmas/UIChristmasExchange...` | 18 | 6 | isMaxBtn, maxBtnN | UI:self |
| `UiWorldCupGuessRankAndRewardPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupPopup/U...` | 13 | 3 | toggle1 | UI:UiWorldCupGuessRankAndRewardPanel |
| `UnlockGirl` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Common/UnlockGirl.prefab` | 9 | 2 | - | - |
| `UnlockNewFunction` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Common/UnlockNewFunction.prefab` | 6 | 1 | FunctionBtnType | UI:UIPVEScene |
| `UnlockNewSkill` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/SU_Common/UnlockNewSkill.prefab` | 6 | 1 | - | - |
| `WeekendChallengeCarStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 15 | 5 | BtnCliam, BtnCliam/btnText, OnClickCloseBtn, UIButton, bgBtnN, bg... | - |
| `WeekendChallengeStageReward` | `UIContainer/Normal` | `Assets/Main/Prefabs/UI/ActivityCenter/UIWeekendChalleng...` | 15 | 5 | BtnCliam, BtnCliam/btnText, OnClickCloseBtn, UIButton, bgBtnN, bg... | - |
| `WorldCupZombieBossComingPanel` | `UIContainer/Normal` | `Assets/Main/Prefabs/Slg/UI/UIWorldCup/UIWorldCupZombie/...` | 13 | 2 | - | UI:self |
