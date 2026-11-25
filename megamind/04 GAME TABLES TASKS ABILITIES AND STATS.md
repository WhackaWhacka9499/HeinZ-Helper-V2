# Volume 04: Last Z XML Game Tables, Tasks, Abilities, Entities & Live Statistics

> **Generated:** `2026-11-23 10:42:43 UTC` | **Source:** `megamind/raw/game_tables_and_stats.json`

## 1. Live Account Statistics & Numbers Snapshot (`Alt3Game.exe` - Read-Only)

### Identity, Power Breakdown & Combat Statistics
| Metric | Live Value | Source Field |
|---|---:|---|
| Commander Name | **Heinzy²** | `PlayerInfoDataManager.selfPlayerData.name` |
| UID / Server | `1848029704000694` / Server **694** | `selfPlayerData.uid` / `serverId` |
| Alliance | **[DawN] NeW Day** | `selfPlayerData.allianceName` |
| HQ Level | **HQ 27** | `BuildManager.MainLv` / `baseLevel` |
| VIP Level / Score | **VIP 7** (70,420 pts) | `VIPManager.vipinfo` |
| Total Combat Power | **166,151,158** (Peak: **172,529,355**) | `selfPlayerData.power` |
| - Army Power | **74,943,120** | `selfPlayerData.armyPower` |
| - Building Power | **43,655,400** | `selfPlayerData.buildingPower` |
| - Hero Power | **31,601,430** | `selfPlayerData.heroPower` |
| - Science Power | **11,021,478** | `selfPlayerData.sciencePower` |
| - Tank / Vehicle Power | **4,929,730** (Components: 990,000) | `selfPlayerData.tankPower` |
| Battles Won / Lost | **22,001** W / **2,291** L | `battleWin` / `battleLose` |
| Troops Killed / Dead | **495,093** Killed / **429,350** Dead | `armyKill` / `armyDead` |
| Scout Count / Likes / Talent Lv | **2,701** Scouts / **2,210** Likes / Talent **Lv.28** | `selfPlayerData` |
| Formations | **0 / 3** Free (5 active marches) | `ArmyFormationDataManager` |
| Troops Ready / Wounded | **17,267** Troops / **1** Wounded | `ArmyManager` / `HospitalManager` |
| Placed Buildings / Owned Heroes | **84** Buildings / **27** Heroes (Max Lv.135) | `BuildManager` / `HeroDataManager` |
| Daily Tasks Score | **0 / 150** (19 tasks, 5 chests) | `DailyTaskManager` |
| Radar Status | Level **20** / **8** active events / **811** completed | `RadarCenterDataManager` |
| Arena | Score **1000** / Fight Times **5** / Rank **-1** | `ArenaManager.selfInfo` |
| Scene / Alliance Help Queue | Scene ID `1` / **9** pending alliance helps | `SceneManager` / `AllianceHelpDataManager` |

### Live Resource Balances (`LuaEntry.Resource` & `LuaEntry.Player`)
| Resource | Live Balance | Notes |
|---|---:|---|
| Zents (`money`) | **843,264,168** | Primary currency |
| Wood (`wood`) | **274,792,629** | Construction / upgrades |
| Food / Metal (`metal`) | **270,972,466** | Troops / upgrades |
| Electricity (`electricity`) | **62,750,011** | Base power resource |
| Flint (`flint`) | **1,224,512** | Cap: 15,000,000 |
| Steel (`steel`) | **1,170,000** | Specialty resource |
| Oil (`oil`) | **751,053** | Cap: 15,000,000 |
| Water (`water`) | **4,000** | Base utility |
| Diamonds (`gold`) | **4,947** | `LuaEntry.Player.gold` |
| Stamina (`stamina` / `actionPoint`) | **8,650** | World map action energy |

### Live Active Events (46 Active in `ActivityListDataManager`)
| Event ID | Localized Name | Type | End Timestamp |
|---|---|---|---:|
| `20001` | Mines Melee | `25` | `1795572000000` |
| `91055` | Weekly Promo Pass | `108` | `1795744800000` |
| `40004` | Furylord | `23` | `1795485599000` |
| `50101` | Intercity Trade | `150` | `61772589540000` |
| `40005` | Danger Lurks | `21` | `61772590740000` |
| `90016` | Season {0} Hero Achievements | `18` | `2636503199000` |
| `59506` | Lucky Choice Chest | `24` | `1795744799000` |
| `120015` | Dawn's Light | `112` | `1796349600000` |
| `30001` | Peak Match | `26` | `0` |
| `96001` | Survival Saga | `33` | `1795572000000` |
| `498284` | Obtain Turkeys | `210` | `1796090400000` |
| `59007` | Wild Treasure Hunt / Legendary Equipment | `1000` | `1796954400000` |
| `100009` | Bullseye Booty | `35` | `1796954400000` |
| `70024` | Lucky Discounter | `44` | `1797559200000` |
| `300006` | Doomsday Club | `277` | `61772589540000` |
| `59006` | Lucky Spin | `42` | `1796349600000` |
| `50201` | State Ruler | `153` | `1796608800000` |
| `40030` | The Tyrant | `62` | `1795658400000` |
| `111101` | Clash of Thrones | `160` | `1838340000000` |
| `40096` | Furylord | `18` | `1795485600000` |
| `498285` | Turkey Shop | `20` | `1796176800000` |
| `400001` | Bounty Missions | `201` | `61772589540000` |
| `498283` | Turkey Market | `211` | `1796090400000` |
| `59004` | Alliance Treasure Hunt | `1100` | `1795744800000` |
| `120038` | Follow Our Community | `1117` | `61772589540000` |
| `50002` | Full Preparedness | `12` | `1795485600000` |
| `100091` |  | `1002` | `61772589540000` |
| `40061` | Clash for Glory | `155` | `1793239200000` |
| `120004` | Camilla's Shop | `20` | `1795831200000` |
| `41001` | Zombie Siege | `3` | `1795658400000` |
| `120037` | Cheer Shop | `241` | `61782698340000` |
| `120036` | Cheer Shop | `20` | `1796695200000` |
| `40038` | Canyon Clash | `71` | `1795831200000` |
| `40142` | Battlefield Breakout | `240` | `1796004000000` |
| `120025` | Treasure Hunt | `21` | `1797559199000` |
| `40086` | Territory Triumph | `38` | `0` |
| `40131` | Spec Ops | `151` | `61772589540000` |
| `91018` | Apoca Treasure Guide | `1005` | `1797991200000` |
| `50000` | Full Preparedness | `12` | `1795442400000` |
| `98002` | Gacha Go | `36` | `1796349600000` |
| `59008` | Daily Treasure Hunt | `1001` | `1797559200000` |
| `55100` | Killing Spree Preview | `106` | `1795831200000` |
| `55000` | Alliance Duel | `14` | `1795485600000` |
| `40130` | Hero Battlefield | `101` | `61773021540000` |
| `30000` | Arena | `26` | `0` |
| `120005` | Zombie Hunter | `73` | `1795744800000` |

### Live Inventory Highlights (110 Unique Stacks, 1,724,283 Total Items - Top 30)
| Item ID | Localized Name | Quantity | Type |
|---|---|---:|---|
| `200394` | Hero EXP | **1,050,798** | `` |
| `230104` | Enhancement Alloy | **492,254** | `` |
| `210141` | 0 | **30,669** | `` |
| `249001` | Tactical Plugin EXP Card | **27,300** | `` |
| `230101` | Orange Skill Book | **21,948** | `` |
| `200034` | Badge | **17,496** | `` |
| `210130` | 0 | **15,429** | `` |
| `252016` | Valor Medal | **12,740** | `` |
| `252004` | Primary Resource Choice Box | **12,141** | `` |
| `211314` | Refugee Recruitment Ticket | **7,600** | `` |
| `210931` | Blue Wood Leveled Chest | **3,195** | `` |
| `210941` | Blue Food Leveled Chest | **3,184** | `` |
| `254000` | Glory Badge | **2,974** | `` |
| `230103` | Blue Skill Book | **2,630** | `` |
| `210120` | 0 | **2,590** | `` |
| `210951` | Blue Electricity Leveled Chest | **2,477** | `` |
| `230102` | Purple Skill Book | **2,182** | `` |
| `210129` | 0 | **2,038** | `` |
| `200395` | Hero EXP | **2,000** | `` |
| `230111` | Modification Blueprint | **1,209** | `` |
| `200194` | Snowflake | **1,147** | `` |
| `250000` | 0 | **1,048** | `` |
| `210961` | Blue Zent Leveled Chest | **664** | `` |
| `200184` | Trade Contract | **528** | `` |
| `242109` | Gift Progress Point | **479** | `` |
| `242108` | Reward Progress Point | **479** | `` |
| `211313` | Green Refugee Fragment | **470** | `` |
| `200211` | 0 | **446** | `` |
| `210319` | Purple Hero Fragment | **431** | `` |
| `242040` | Ruby | **410** | `` |

## 2. Complete Daily Quests Catalog (`TableName.DailyQuest` - All 52 Rows)

| Quest ID | English Title | Objective Description | Score | Target (`para2`) | GoType / GoBuild |
|---|---|---|---:|---:|---|
| `1000001` | Agricultural Giant | Harvest Crops {0} times | 5 | 30 | `gotype=2, gotype2=3, go=702000, gobuild=4` |
| `1000002` | Top Riders | Train {0} Riders | 10 | 20 | `gotype=2, gotype2=1, go=425000, gobuild=2` |
| `1000003` | Ace Assaulters | Train {0} Assaulters | 10 | 20 | `gotype=2, gotype2=1, go=424000, gobuild=2` |
| `1000004` | Super Shooters | Train {0} Shooters | 10 | 20 | `gotype=2, gotype2=1, go=423000, gobuild=2` |
| `1000005` | Gain Momentum | Defeat {0} Creeps | 10 | 5 | `gotype=44, gotype2=11, gobuild=1` |
| `1000006` | Tech Advancement | Research {0} Techs | 20 | 1 | `gotype=8, gotype2=1, go=403000` |
| `1000007` | Gain Momentum | Defeat {0} Creeps | 0 | 1 | `gotype=44, gotype2=11, gobuild=1` |
| `1000008` | Keep Expanding | Conduct {0} productions in Processing Plant | 5 | 15 | `gotype=53, gotype2=15` |
| `1000009` | Shared Aspirations | 170423 | 10 | 5 | `gotype=2, gotype2=1, go=401000, gobuild=15` |
| `1000010` | Order from Earth | 170424 | 5 | 6 | `gotype=2, gotype2=1, go=710000, gobuild=16` |
| `1000011` | Livestock Magnate | Conduct {0} harvests from Animal Farms | 5 | 30 | `gotype=52, gotype2=14` |
| `1000012` | Skillful Craftsman | Upgrade buildings {0} times | 20 | 1 | `gotype=51, gotype2=13` |
| `1000013` | Gain Momentum | Start a team-up and kill {0} Boomers | 20 | 2 | `gotype2=16` |
| `1000014` | Keep Expanding | Send troops to mine {0} Stones | 5 | 100 | `gotype=44, gotype2=12` |
| `1000015` | Keep Expanding | Send troops to gather {0} Wood | 0 | 100 | `gotype=44, gotype2=12` |
| `1000016` | Additional Hands | Use Recruitment Tickets to recruit {0} times | 10 | 1 | `gotype2=1, go=722000` |
| `1000017` | Road to Rule | Help allies {0} times | 10 | 15 | `gotype2=17, go=402000` |
| `1000018` | Gain Momentum | Complete {0} radar events | 10 | 5 | `gotype2=1, go=417000` |
| `1000019` | 170462 | 170463 | 5 | 10 | `gotype=2, gotype2=1, go=724000` |
| `1000020` | Arrays of Goods | Stock items {0} times in Black Market | 5 | 1 | `gotype=2, gotype2=1, go=729000` |
| `1000021` | Empty the Shelves | Make {0} purchases on black market | 5 | 3 | `gotype=2, gotype2=1, go=729000` |
| `1000022` | Coin Bonanza | Send troops to gather {0} Zents | 5 | 100 | `gotype=44, gotype2=12` |
| `1000023` | A Good Deal | Make any purchase at the Pack Shop | 30 | 1 | `gotype2=29` |
| `1000024` | Keep Growing | Use Warehouse resource items {0} times | 5 | 1 | `gotype2=30` |
| `1000025` | Top Riders | Train {0} Riders | 10 | 5 | `gotype=2, gotype2=1, go=423000, gobuild=2` |
| `1000026` | Ace Assaulters | Train {0} Assaulters | 10 | 5 | `gotype=2, gotype2=1, go=424000, gobuild=2` |
| `1000027` | Super Shooters | Train {0} Shooters | 10 | 5 | `gotype=2, gotype2=1, go=425000, gobuild=2` |
| `1000028` | Top Riders | Train {0} Riders | 10 | 10 | `gotype=2, gotype2=1, go=423000, gobuild=2` |
| `1000029` | Ace Assaulters | Train {0} Assaulters | 10 | 10 | `gotype=2, gotype2=1, go=424000, gobuild=2` |
| `1000030` | Super Shooters | Train {0} Shooters | 10 | 10 | `gotype=2, gotype2=1, go=425000, gobuild=2` |
| `1000031` | Top Riders | Train {0} Riders | 10 | 20 | `gotype=2, gotype2=1, go=423000, gobuild=2` |
| `1000032` | Ace Assaulters | Train {0} Assaulters | 10 | 20 | `gotype=2, gotype2=1, go=424000, gobuild=2` |
| `1000033` | Super Shooters | Train {0} Shooters | 10 | 20 | `gotype=2, gotype2=1, go=425000, gobuild=2` |
| `1000034` | Coin Bonanza | Complete {0} gathering acts | 30 | 6 | `gotype=44, gotype2=12` |
| `1000035` | Keep Growing | Use a total of {0}-Min Speedup | 10 | 1 | `gotype2=13` |
| `1000036` | Apocalyptic Tycoon | 170515 | 5 | 3 | `gotype2=1` |
| `1000037` | Hero Upgrade | Use {0} hero EXP items | 10 | 15 | `gotype=13, gotype2=9` |
| `1000038` | Star Up | Raise hero star {0} times | 10 | 3 | `gotype=2, gotype2=1, go=722000` |
| `1000039` | Hero Rank Up | Promote hero rank {0} times | 10 | 1 | `gotype=13, gotype2=9` |
| `1000040` | Sweep Tiles | Sweep tiles {0} times | 10 | 2 | `gotype2=60` |
| `1000041` | Sweep Tiles | Sweep tiles {0} times | 10 | 4 | `gotype2=60` |
| `1000042` | Apocalyptic Tycoon | Attack Headquarters {0} times | 30 | 1 | `gotype2=78` |
| `1000043` | Gain Momentum | Start a team-up and kill {0} Frostbanes | 20 | 2 | `gotype2=16` |
| `1000044` | - | Dispatch {0} Intercity Trade trucks | 20 | 3 | `gotype2=80` |
| `1000045` | - | Donate to Alliance Techs {0} times | 10 | 10 | `gotype2=81` |
| `1000046` | - | Complete {0} attacks in Arena | 20 | 1 | `gotype2=82` |
| `1000047` | - | Plunder others' Bounty Missions {0} times | 10 | 1 | `gotype2=83` |
| `1000048` | Coin Bonanza | Complete {0} gathering acts | 30 | 3 | `gotype=44, gotype2=12` |
| `1000049` | Gain Momentum | Start a team-up and kill {0} Frostbanes | 20 | 2 | `gotype2=16` |
| `1000050` | Gain Momentum | Start a team-up and kill {0} Stegosaurs | 20 | 2 | `gotype2=16` |
| `1000051` | Gain Momentum | Start a team-up and kill {0} Stegosaurs | 20 | 2 | `gotype2=16` |
| `1000052` | Social Pro | Like {0} different Posts | 5 | 3 | `gotype2=99` |

## 3. Buildings Catalog (`TableName.Building` - 200 Entries)

| Building ID | English Name | Type / Category | Max / Unlock Info | Description |
|---|---|---|---|---|
| `103000` | Bed | `0` | - | Can relieve fatigue. |
| `103001` | Bed | `0` | - | Can relieve fatigue. |
| `103002` | Bed | `0` | - | Can relieve fatigue. |
| `103003` | Bed | `0` | - | Can relieve fatigue. |
| `104000` | Desk | `0` | - | Can relieve fatigue. |
| `104001` | Desk | `0` | - | Can relieve fatigue. |
| `104002` | Desk | `0` | - | Can relieve fatigue. |
| `104003` | Desk | `0` | - | Can relieve fatigue. |
| `105000` | Sink | `0` | - | Can relieve fatigue. |
| `105001` | Sink | `0` | - | Can relieve fatigue. |
| `105002` | Sink | `0` | - | Can relieve fatigue. |
| `105003` | Sink | `0` | - | Can relieve fatigue. |
| `106000` | Bookshelf | `0` | - | Can relieve fatigue. |
| `106001` | Bookshelf | `0` | - | Can relieve fatigue. |
| `106002` | Bookshelf | `0` | - | Can relieve fatigue. |
| `106003` | Bookshelf | `0` | - | Can relieve fatigue. |
| `107000` | Weapon Rack | `0` | - | 721067 |
| `107001` | Weapon Rack | `0` | - | 721067 |
| `107002` | Weapon Rack | `0` | - | 721067 |
| `107003` | Weapon Rack | `0` | - | 721067 |
| `108000` | 720178 | `0` | - | 721067 |
| `108001` | 720178 | `0` | - | 721067 |
| `108002` | 720178 | `0` | - | 721067 |
| `108003` | 720178 | `0` | - | 721067 |
| `109000` | 720179 | `0` | - | 721067 |
| `109001` | 720179 | `0` | - | 721067 |
| `109002` | 720179 | `0` | - | 721067 |
| `109003` | 720179 | `0` | - | 721067 |
| `110000` | 720141 | `0` | - | 721071 |
| `110001` | 720141 | `0` | - | 721071 |
| `110002` | 720141 | `0` | - | 721071 |
| `110003` | 720141 | `0` | - | 721071 |
| `111000` | 720142 | `0` | - | 721072 |
| `111001` | 720142 | `0` | - | 721072 |
| `111002` | 720142 | `0` | - | 721072 |
| `111003` | 720142 | `0` | - | 721072 |
| `112000` | 720143 | `0` | - | 721073 |
| `112001` | 720143 | `0` | - | 721073 |
| `112002` | 720143 | `0` | - | 721073 |
| `112003` | 720143 | `0` | - | 721073 |
| `113000` | 720140 | `0` | - | 721070 |
| `113001` | 720140 | `0` | - | 721070 |
| `113002` | 720140 | `0` | - | 721070 |
| `113003` | 720140 | `0` | - | 721070 |
| `114000` | Sink | `0` | - | Can relieve fatigue. |
| `114001` | Sink | `0` | - | Can relieve fatigue. |
| `114002` | Sink | `0` | - | Can relieve fatigue. |
| `114003` | Sink | `0` | - | Can relieve fatigue. |
| `115000` | 720134 | `0` | - | 721064 |
| `115001` | 720134 | `0` | - | 721064 |
| `115002` | 720134 | `0` | - | 721064 |
| `115003` | 720134 | `0` | - | 721064 |
| `116000` | 720135 | `0` | - | 721065 |
| `116001` | 720135 | `0` | - | 721065 |
| `116002` | 720135 | `0` | - | 721065 |
| `116003` | 720135 | `0` | - | 721065 |
| `117000` | 720136 | `0` | - | 721066 |
| `117001` | 720136 | `0` | - | 721066 |
| `117002` | 720136 | `0` | - | 721066 |
| `117003` | 720136 | `0` | - | 721066 |
| `118000` | 720130 | `0` | - | 721060 |
| `118001` | 720130 | `0` | - | 721060 |
| `118002` | 720130 | `0` | - | 721060 |
| `118003` | 720130 | `0` | - | 721060 |
| `119000` | 720131 | `0` | - | 721061 |
| `119001` | 720131 | `0` | - | 721061 |
| `119002` | 720131 | `0` | - | 721061 |
| `119003` | 720131 | `0` | - | 721061 |
| `120000` | 720144 | `0` | - | 721074 |
| `120001` | 720144 | `0` | - | 721074 |
| `120002` | 720144 | `0` | - | 721074 |
| `120003` | 720144 | `0` | - | 721074 |
| `121000` | 720145 | `0` | - | 721075 |
| `121001` | 720145 | `0` | - | 721075 |
| `121002` | 720145 | `0` | - | 721075 |
| `121003` | 720145 | `0` | - | 721075 |
| `122000` | 720146 | `0` | - | 721076 |
| `122001` | 720146 | `0` | - | 721076 |
| `122002` | 720146 | `0` | - | 721076 |
| `122003` | 720146 | `0` | - | 721076 |
| `123000` | 720147 | `0` | - | 721077 |
| `123001` | 720147 | `0` | - | 721077 |
| `123002` | 720147 | `0` | - | 721077 |
| `123003` | 720147 | `0` | - | 721077 |
| `124000` | Weapon Rack | `0` | - | 721067 |
| `124001` | Weapon Rack | `0` | - | 721067 |
| `124002` | Weapon Rack | `0` | - | 721067 |
| `124003` | Weapon Rack | `0` | - | 721067 |
| `125000` | 720145 | `0` | - | 721075 |
| `125001` | 720145 | `0` | - | 721075 |
| `125002` | 720145 | `0` | - | 721075 |
| `125003` | 720145 | `0` | - | 721075 |
| `126000` | Wooden Crate | `0` | - | Can store cargo. |
| `126001` | Wooden Crate | `0` | - | Can store cargo. |
| `126002` | Wooden Crate | `0` | - | Can store cargo. |
| `126003` | Wooden Crate | `0` | - | Can store cargo. |
| `127000` | Barrel | `0` | - | Can store fuel. |
| `127001` | Barrel | `0` | - | Can store fuel. |
| `127002` | Barrel | `0` | - | Can store fuel. |
| `127003` | Barrel | `0` | - | Can store fuel. |
| `128000` | Shelf | `0` | - | Properly categorize resources. |
| `128001` | Shelf | `0` | - | Properly categorize resources. |
| `128002` | Shelf | `0` | - | Properly categorize resources. |
| `128003` | Shelf | `0` | - | Properly categorize resources. |
| `129000` | Forklift | `0` | - | Assist in loading and unloading. |
| `129001` | Forklift | `0` | - | Assist in loading and unloading. |
| `129002` | Forklift | `0` | - | Assist in loading and unloading. |
| `129003` | Forklift | `0` | - | Assist in loading and unloading. |
| `130000` | Cultivate Land | `0` | - | 721090 |
| `130001` | Cultivate Land | `0` | - | 721090 |
| `130002` | Cultivate Land | `0` | - | 721090 |
| `130003` | Cultivate Land | `0` | - | 721090 |
| `131000` | Grow | `0` | - | Grow crops |
| `131001` | Grow | `0` | - | Grow crops |
| `131002` | Grow | `0` | - | Grow crops |
| `131003` | Grow | `0` | - | Grow crops |
| `132000` | Fence | `0` | - | Build a farm fence |
| `132001` | Fence | `0` | - | Build a farm fence |
| `132002` | Fence | `0` | - | Build a farm fence |
| `132003` | Fence | `0` | - | Build a farm fence |

## 4. Heroes, Abilities, Skills, Talents, Equipment & Buffs

### 4.1 Combat Heroes (`TableName.LW_Hero` - 41 Heroes; `NewHeroes` has 250 sampled / 1,142 rows)
| Hero ID | Title / Name | Quality | Type | Base HP | Base ATK | Template ID |
|---|---|---|---|---:|---:|---|
| `1002` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1003` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1004` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1006` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1007` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1008` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1009` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1011` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1012` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1013` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1015` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1016` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1017` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1018` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1019` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `1021` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `2000` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `11001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `12001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `13001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `13003` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `21001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `22001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `22002` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `22003` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `32001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `33001` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `33002` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `33003` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `33004` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `900101` | Season Mastery EXP gains from season build... | `1` | `1` | 6000 | 5000 | `1` |
| `900102` | Season Mastery EXP gains from season build... | `1` | `1` | 6000 | 5000 | `1` |
| `900103` | Season Mastery EXP gains from season build... | `1` | `1` | 6000 | 5000 | `1` |
| `900104` | Season Mastery EXP gains from season build... | `1` | `1` | 6000 | 5000 | `1` |
| `900105` | Season Mastery EXP gains from season build... | `1` | `1` | 6000 | 5000 | `1` |
| `900201` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `900202` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `900203` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `900204` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `900205` | Season Mastery EXP gains from season build... | `1` | `1` | 3000 | 5000 | `1` |
| `900301` | Season Mastery EXP gains from season build... | `1` | `1` | 9000 | 5000 | `1` |

### 4.2 Hero Skills & Abilities (`TableName.LW_Hero_Skill` - 968 Total; Unique Skill Groups)
> Deduplicated **258** unique Hero Ability definitions from **968** level rows (all 968 rows preserved in `megamind/raw/game_tables_and_stats.json`).

| Skill ID | Group | English Name | Max Lv | Star | Pre-CD | Power | Description |
|---|---|---|---:|---:|---:|---:|---|
| `10001` | `10001` | 800255 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800255 |
| `10002` | `10002` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `10003` | `10003` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `10004` | `10004` | 800283 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800283 |
| `10005` | `10005` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `10006` | `10006` | 800285 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800285 |
| `10007` | `10007` | 800255 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800255 |
| `10011` | `10011` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `10012` | `10012` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `10013` | `10013` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `10101` | `10101` | 800255 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800255 |
| `10102` | `10102` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `10103` | `10103` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `10104` | `10104` | 800283 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800283 |
| `10105` | `10105` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `10106` | `10106` | 800285 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800285 |
| `10107` | `10107` | 800255 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800255 |
| `10108` | `10108` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `10109` | `10109` | 800283 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800283 |
| `10110` | `10110` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `10111` | `10111` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `10112` | `10112` | 800283 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800283 |
| `10113` | `10113` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `11001` | `11001` | 800255 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800255 |
| `11002` | `11002` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `11003` | `11003` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `12001` | `12001` | 800255 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800255 |
| `12002` | `12002` | 800257 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800257 |
| `12003` | `12003` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `20001` | `20001` | Coming Soon | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20002` | `20002` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20003` | `20003` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20004` | `20004` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20005` | `20005` | Coming Soon | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20011` | `20011` | Coming Soon | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20012` | `20012` | Coming Soon | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20013` | `20013` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20014` | `20014` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20015` | `20015` | Coming Soon | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20021` | `20021` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20022` | `20022` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20023` | `20023` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20024` | `20024` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20025` | `20025` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20026` | `20026` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20027` | `20027` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20028` | `20028` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20029` | `20029` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20030` | `20030` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20031` | `20031` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20032` | `20032` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20033` | `20033` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20034` | `20034` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20035` | `20035` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20036` | `20036` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20037` | `20037` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20038` | `20038` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20039` | `20039` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20040` | `20040` | 159002 | 1 | 1 | 6000 | table: 000001F05ECE1210 | - |
| `20041` | `20041` | 159002 | 1 | 1 | 12000 | table: 000001F05ECE1210 | - |
| `20042` | `20042` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20101` | `20101` | Coming Soon | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `20102` | `20102` | 159002 | 1 | 1 | 0 | table: 000001F05ECE1210 | - |
| `21038` | `21038` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `21039` | `21039` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `21040` | `21040` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `21041` | `21041` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `21042` | `21042` | 800275 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800275 |
| `22000` | `10000` | 800259 | 1 | 1 | 3000 | table: 000001F05ECE1210 | 800259 |
| `22080` | `22080` | 800257 | 0 | 0 | 5000 | table: 000001F05ECE1290 | - |
| `22100` | `22100` | 800255 | 0 | 0 | 5000 | table: 000001F05ECE1290 | - |
| `22200` | `22200` | 800255 | 0 | 0 | 5000 | table: 000001F05ECE1290 | - |
| `22270` | `22270` | 800257 | 0 | 0 | 5000 | table: 000001F05ECE1290 | - |
| `22290` | `22290` | 800255 | 0 | 0 | 5000 | table: 000001F05ECE1290 | - |
| `23080` | `23080` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `23100` | `23100` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `23200` | `23200` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `23270` | `23270` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `23290` | `23290` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31010` | `31010` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31020` | `31020` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31030` | `31030` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31040` | `31040` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31046` | `31046` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31050` | `31050` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31060` | `31060` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31070` | `31070` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31090` | `31090` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31110` | `31110` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31120` | `31120` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31130` | `31130` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31140` | `31140` | 800259 | 0 | 0 | 3000 | table: 000001F05ECE1290 | - |
| `31150` | `31150` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31160` | `31160` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31170` | `31170` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31180` | `31180` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31190` | `31190` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31210` | `31210` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31220` | `31220` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31230` | `31230` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31240` | `31240` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31250` | `31250` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31260` | `31260` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31280` | `31280` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31300` | `31300` | 800255 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31310` | `31310` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31330` | `31330` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31336` | `31336` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31360` | `31360` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31366` | `31366` | 800283 | 0 | 1 | 0 | table: 000001F05ECE1290 | - |
| `31400` | `31400` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31410` | `31410` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31420` | `31420` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31430` | `31430` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31440` | `31440` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31450` | `31450` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31460` | `31460` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31470` | `31470` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31480` | `31480` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31490` | `31490` | 800283 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31500` | `31500` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31510` | `31510` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `31520` | `31520` | 800257 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `32010` | `32010` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32020` | `32020` | 800255 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32030` | `32030` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32040` | `32040` | 800283 | 30 | 0 | 11500 | table: 000001F05ECE1290 | 800283 |
| `32050` | `32050` | 800257 | 0 | 0 | 6000 | table: 000001F05ECE1290 | - |
| `32060` | `32060` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32070` | `32070` | 800255 | 0 | 0 | 7000 | table: 000001F05ECE1290 | - |
| `32090` | `32090` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32110` | `32110` | 800259 | 0 | 0 | 8000 | table: 000001F05ECE1290 | - |
| `32120` | `32120` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32130` | `32130` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32140` | `32140` | 800259 | 0 | 0 | 10500 | table: 000001F05ECE1290 | - |
| `32150` | `32150` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32160` | `32160` | 800257 | 0 | 0 | 6000 | table: 000001F05ECE1290 | - |
| `32170` | `32170` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32180` | `32180` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32190` | `32190` | 800255 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32210` | `32210` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32220` | `32220` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32230` | `32230` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32240` | `32240` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32250` | `32250` | 800257 | 0 | 0 | 9500 | table: 000001F05ECE1290 | - |
| `32260` | `32260` | 800259 | 0 | 0 | 9800 | table: 000001F05ECE1290 | - |
| `32280` | `32280` | 800283 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32300` | `32300` | 800255 | 0 | 0 | 7000 | table: 000001F05ECE1290 | - |
| `32310` | `32310` | 800283 | 30 | 0 | 12000 | table: 000001F05ECE1290 | 800283 |
| `32316` | `32316` | 800259 | 1 | 1 | 0 | table: 000001F05ECE1210 | 800259 |
| `32330` | `32330` | 800259 | 0 | 0 | 9000 | table: 000001F05ECE1290 | - |
| `32360` | `32360` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32400` | `32400` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32410` | `32410` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32420` | `32420` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32430` | `32430` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32440` | `32440` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32450` | `32450` | 800259 | 0 | 0 | 10500 | table: 000001F05ECE1290 | - |
| `32460` | `32460` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32470` | `32470` | 800259 | 0 | 0 | 10500 | table: 000001F05ECE1290 | - |
| `32480` | `32480` | 800259 | 0 | 0 | 10500 | table: 000001F05ECE1290 | - |
| `32490` | `32490` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32500` | `32500` | 800259 | 0 | 0 | 11000 | table: 000001F05ECE1290 | - |
| `32510` | `32510` | 800259 | 0 | 0 | 10000 | table: 000001F05ECE1290 | - |
| `32520` | `32520` | 800259 | 0 | 0 | 11000 | table: 000001F05ECE1290 | - |
| `51122` | `51122` | 800259 | 0 | 3 | 0 | table: 000001F05ECE1290 | - |
| `62010` | `62010` | 800259 | 0 | 0 | 12000 | table: 000001F05ECE1290 | - |
| `62040` | `62040` | 800283 | 0 | 0 | 11000 | table: 000001F05ECE1290 | - |
| `62250` | `62250` | 800257 | 0 | 0 | 9500 | table: 000001F05ECE1290 | - |
| `62310` | `62310` | 800283 | 0 | 0 | 12000 | table: 000001F05ECE1290 | - |
| `91120` | `91120` | 800259 | 0 | 0 | 0 | table: 000001F05ECE1290 | - |
| `100001` | `100001` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100002` | `100002` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100003` | `100003` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100004` | `100004` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100005` | `100005` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100011` | `100011` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100012` | `100012` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100013` | `100013` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |
| `100014` | `100014` | 800259 | 1 | 1 | 8000 | table: 000001F05ECE1210 | 800259 |

### 4.3 Season Mastery Skills (`TableName.MasterySkill` - 33 Skills)
| ID | Name | Type | Use Position | GoTo | Description |
|---|---|---|---|---|---|
| `1001` | Thrive | `1001` | `1` | `1;101;1200101` | 110903 |
| `1002` | 110805 | `1002` | `1` | `1;101;1300101` | 110905 |
| `1003` | Cellar | `1003` | `1` | `1;102;2300101` | Upon releasing the skill, resources in the headquarters will be immune from being looted wit... |
| `1004` | Rapid Mining | `1004` | `1` | `1;101;1260101` | Instantly obtain abundant ({2}-h resource yields) Sandsouls and Sapphires. CD: {1}h. |
| `1005` | Industrial Development I | `1005` | `3` | `1;101;1270101` | Carry out industrial development on any captured tile, improving the tile's yield to {2}/h. |
| `1006` | Industrial Development Ⅱ | `1006` | `3` | `1;101;1280101` | Deploy 1 troop to a tile for 20 mins to get 24-h resource yields of the tile. CD: 24h. |
| `1007` | Demolition | `1007` | `1` | `1;102;2200101` | Upon use, Destruction in Siege Attacks +{2}% within {0}. CD: {1}h. |
| `1009` | Emergency Strengthening | `1009` | `2` | `1;102;2290101` | Put up a shield for season buildings for {0}. During the period, durability damage taken -{2... |
| `1011` | Landmine | `1011` | `3` | `1;102;2310101` | Place 1 landmine on your own tile (invisible to others). When an enemy troop attacks the til... |
| `1012` | Obsidian Purification | `1012` | `3` | `1;102;2110101` | Sapphire Yield |
| `1013` | Rapid Repair | `1013` | `2` | `1;102;2280101` | Restore {2}% of specific season building's durability. CD: {1}h. |
| `1015` | Not yet available | `1015` | `4` | `1;103;3360101` | Not yet available |
| `1016` | Cheer Up | `1016` | `1` | `1;103;3370101` | ATK of all heroes with a random faction +{2} for {0}. CD: {1}h. |
| `1017` | First Aid | `1017` | `4` | `1;103;3380101` | For next siege attack, {2}% of perished units (cannot exceed the maint depot's capacity) wil... |
| `1018` | Bumper Harvests | `1018` | `1` | `1;101;1310101` | Instantly obtain {2}hrs worth of yields of Lumberyard, Quarry, Power Plant, and Residence in... |
| `2001` | Construction Support | `2001` | `1` | `10501` | Use on an ally to boost construction speed for both sides by {0}% for {1} hrs. CD: {2} hrs. ... |
| `2002` | Shield Bond | `2002` | `1` | `10901` | Use on an ally, granting both sides a {0}-hr shield. CD: {1} hrs. (Effect cannot stack) |
| `2003` | Sabotage Mine | `2003` | `3` | `12001` | Usable in the home State. Upon detonation, kills {0} enemy units, and the explosive remains ... |
| `2004` | Research Assist | `2004` | `1` | `11701` | Use on an ally to boost research speed for both sides by {0}% for {1} hrs. CD: {2} hrs. (Eff... |
| `2005` | Unit Mobilization | `2005` | `1` | `20101` | Select a unit type to instantly receive {0} units of its highest unlocked level (within capa... |
| `2006` | Charge Banner | `2006` | `3` | `21301` | Deploy a Charge Banner, providing allied troops nearby a {0}% attack boost for {1} mins. CD:... |
| `2007` | Instant Recall | `2007` | `4` | `21401` | Instantly recalls one troop. Usable {0} times daily. |
| `2008` | Devolution Ray | `2008` | `1` | `22001` | Upon use, when dispatching troops for an attack, {0}% of enemy seriously injured units are d... |
| `2009` | Camouflage | `2009` | `1` | `20701` | Headquarters enters anti-scout mode, preventing enemies from getting intel from scouting, la... |
| `2010` | Vault Master | `2010` | `1` | `11301` | Deploys a vault for alliance members to loot. Active for 30 minutes and supports up to 100 l... |
| `2012` | Medical Aid | `2012` | `1` | `12901` | Use on an ally to boost the Hospital capacity for both sides by {0}% for {1} hrs. CD: {2} hr... |
| `2013` | Instant Build | `2013` | `1` | `12701` | Instantly reduces construction duration of all building queues by {0} minutes. CD: {1} days. |
| `2014` | Relocation Charger | `2014` | `2` | `22101` | Gain {1} points of Energy every {0} hrs, allowing for relocating anywhere on the world map. ... |
| `2015` | Rapid Strike | `2015` | `2` | `22001` | Rally Attacks can depart early. Usable {0} times per week; resets every Monday. |
| `2016` | Research Now | `2016` | `1` | `140801` | Instantly reduces research duration for all queues by {0} minutes. CD: {1} days. |
| `2017` | Arms Expert | `2017` | `1` | `141201` | In the Full Preparedness calendar, the current theme can be swapped with a subsequent day's ... |
| `2018` | Express Delivery | `2018` | `1` | `240101` | Can be used in the Trade interface to instantly deliver an active truck to its destination, ... |
| `2019` | Back for Revenge | `2019` | `1` | `240701` | When your troop loses a field battle against an enemy troop, it regroups on the spot for 2s.... |

### 4.4 Commander Talents (`TableName.Talent_New` - 35 Talents) & Player Careers (`PlayerCareer` - 50 / `PlayerCareerEffect` - 65)
| Talent ID | Name | Type | Group | Lv | Effect Value | Description |
|---|---|---|---|---:|---|---|
| `10000` | Rugged Tenacity | `1` | `10000` | 1 | `5` | 792016 |
| `10001` | Rugged Tenacity | `1` | `10000` | 2 | `5` | 792016 |
| `10002` | Rugged Tenacity | `1` | `10000` | 3 | `5` | 792016 |
| `10003` | Rugged Tenacity | `1` | `10000` | 4 | `5` | 792016 |
| `10004` | Rugged Tenacity | `1` | `10000` | 5 | `5` | 792016 |
| `10010` | Master Defender | `1` | `10010` | 1 | `1` | 792017 |
| `10011` | Master Defender | `1` | `10010` | 2 | `1` | 792017 |
| `10012` | Master Defender | `1` | `10010` | 3 | `1` | 792017 |
| `10013` | Master Defender | `1` | `10010` | 4 | `1` | 792017 |
| `10014` | Master Defender | `1` | `10010` | 5 | `1` | 792017 |
| `10020` | Slayer | `1` | `10020` | 1 | `1` | 792018 |
| `10021` | Slayer | `1` | `10020` | 2 | `1` | 792018 |
| `10022` | Slayer | `1` | `10020` | 3 | `1` | 792018 |
| `10023` | Slayer | `1` | `10020` | 4 | `1` | 792018 |
| `10024` | Slayer | `1` | `10020` | 5 | `1` | 792018 |
| `10030` | Strong Legs | `1` | `10030` | 1 | `1` | 792019 |
| `10031` | Strong Legs | `1` | `10030` | 2 | `1` | 792019 |
| `10032` | Strong Legs | `1` | `10030` | 3 | `2` | 792019 |
| `10033` | Strong Legs | `1` | `10030` | 4 | `2` | 792019 |
| `10034` | Strong Legs | `1` | `10030` | 5 | `3` | 792019 |
| `10035` | Lumberjack | `1` | `10035` | 1 | `-` | Learn to craft an axe |
| `10036` | Quarryman | `1` | `10036` | 1 | `-` | Learn to craft a pickaxe |
| `10037` | Sneak | `1` | `10037` | 1 | `-` | 792023 |
| `10038` | Backpack | `1` | `10038` | 1 | `-` | Learn to make a backpack |
| `10040` | Strict Diet | `1` | `10040` | 1 | `1` | 792020 |
| `10041` | Strict Diet | `1` | `10040` | 2 | `2` | 792020 |
| `10042` | Strict Diet | `1` | `10040` | 3 | `2` | 792020 |
| `10043` | Strict Diet | `1` | `10040` | 4 | `3` | 792020 |
| `10044` | Strict Diet | `1` | `10040` | 5 | `3` | 792020 |
| `10050` | Bandage | `1` | `10050` | 1 | `-` | Learn to make bandages |
| `10051` | Mace | `1` | `10051` | 1 | `-` | Learn to craft mace |
| `10052` | Simple Backpack | `1` | `10052` | 1 | `-` | 792027 |
| `10053` | Wooden Bow | `1` | `10053` | 1 | `-` | Learn to make a wooden bow |
| `10054` | Berry Liquor | `1` | `10054` | 1 | `-` | 792029 |
| `10055` | Medical Kit | `1` | `10055` | 1 | `-` | Learn to make medical kit |

### 4.5 Hero Equipment (`TableName.Equip` - 18) & Suits (`Equip_Suit` - 3)
| Equip ID | Name | Quality | Slot | Army Type | Description |
|---|---|---|---|---|---|
| `110100` | D2-Portable Pistol | `2` | `1` | `0` | A primary weapon, offering your hero a meager boost in firepower. |
| `110200` | D2-Simple Helmet | `2` | `2` | `0` | A primary helmet, offering your hero a meager boost in overall abilities. |
| `110300` | D2-Simple Armor | `2` | `3` | `0` | A primary armor, offering your hero a meager boost in defense. |
| `110400` | D2-Canvas Shoes | `2` | `4` | `0` | A pair of primary shoes, offering your hero a meager boost in overall abilities. |
| `210100` | D3-Pistol | `3` | `1` | `0` | A fine weapon, offering your hero a modest boost in firepower. |
| `210200` | D3-Helmet | `3` | `2` | `0` | A fine helmet, offering your hero a modest boost in overall abilities. |
| `210300` | D3-Armor | `3` | `3` | `0` | Fine armor, offering your hero a modest boost in defense ability. |
| `210400` | D3-Combat Boots | `3` | `4` | `0` | Fine shoes, offering your hero a modest boost in overall abilities. |
| `310100` | D4-Revolver | `4` | `1` | `0` | An advanced weapon, not only offering your hero abundant attack but also gran... |
| `310200` | D4-Helmet | `4` | `2` | `0` | An advanced helmet offers abundant overall capabilities, and excels particula... |
| `310300` | D4-Armor | `4` | `3` | `0` | Advanced armor, not only offering your hero abundant defense but also grantin... |
| `310400` | D4-Combat Boots | `4` | `4` | `0` | Advanced shoes offer abundant overall capabilities, and excel particularly in... |
| `410100` | D5-Submachine Gun | `5` | `1` | `0` | A great weapon, not only offering your hero massive attack but also granting ... |
| `410200` | D5-Helmet | `5` | `2` | `0` | A great helmet offers massive overall abilities, and excels particularly in s... |
| `410300` | D5-Heavy Armor | `5` | `3` | `0` | Great armor, not only offering your hero massive defense but also granting ex... |
| `410400` | D5-Power Boots | `5` | `4` | `0` | Great shoes offer massive overall abilities, and excel particularly in defense! |
| `490010` | Super Snowball Gun | `5` | `1` | `0` | A magical Xmas gift with the power to knock out zombies with ease. |
| `490020` | Cupid's Arrow | `5` | `1` | `0` | An Orange-tier hero weapon. Even in a world forsaken, love cuts deeper than a... |

## 5. Research Trees, Troops, Monsters, Resources, Radar & VIP

### 5.1 Science Research Trees (`TableName.APSScienceTab` - 21 Trees; `ScienceNew` has 350+ Techs)
| Tab ID | Tree Name | Order / Extra |
|---|---|---|
| `1` | New Home | building=403000;725000;777000, icon_start=G_KJ_beijing001, id=1, order |
| `4` | Alliance Recognition | building=403000;725000;777000, icon_start=G_KJ_beijing009, id=4, order |
| `5` | Fully Armed Alliance | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `6` | Shelter Building | building=403000;725000;777000, icon_start=G_KJ_beijing003, id=6, order |
| `7` | Elite Troops | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `8` | HQ Management | building=403000;725000;777000, icon_start=G_KJ_beijing010, id=8, order |
| `9` | Military Strategies | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `10` | Siege to Seize | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `11` | Peace Shield | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `12` | Rapid Growth | building=403000;725000;777000, icon_start=G_KJ_beijing007, id=12, orde |
| `13` | Field | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `14` | Army Building | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `21` | Unit Special Training | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `22` | Hero Training | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `23` | Rider Training | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `24` | Assaulter Training | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `25` | Shooter Training | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `26` | Age of Steel | building=403000;725000;777000, icon_start=G_KJ_beijing017, id=26, orde |
| `27` | Tactical Master | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `28` | Army Expansion | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |
| `29` | Leader's Will | battle_science=1, building=403000;725000;777000, icon_start=G_KJ_beiji |

### 5.2 Troops / Armies (`TableName.Army` - 150 Units)
| Army ID | Name | Level / Tier | Type | Power | Attack | Defense | HP | Load | Speed |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| `100101` | - | - | `111001;50` | - | - | - | - | - | - |
| `100102` | - | - | `111001;70` | - | - | - | - | - | - |
| `100103` | - | - | `111002;30|111001;70` | - | - | - | - | - | - |
| `100104` | - | - | `111002;80|111001;70` | - | - | - | - | - | - |
| `100105` | - | - | `111002;140|111001;60` | - | - | - | - | - | - |
| `100106` | - | - | `111002;250` | - | - | - | - | - | - |
| `100107` | - | - | `111003;90|111002;210` | - | - | - | - | - | - |
| `100108` | - | - | `111003;180|111002;170` | - | - | - | - | - | - |
| `100109` | - | - | `111003;280|111002;120` | - | - | - | - | - | - |
| `100110` | - | - | `111003;450` | - | - | - | - | - | - |
| `100111` | - | - | `111004;150|111003;350` | - | - | - | - | - | - |
| `100112` | - | - | `111004;300|111003;300` | - | - | - | - | - | - |
| `100113` | - | - | `111004;490|111003;210` | - | - | - | - | - | - |
| `100114` | - | - | `111004;800` | - | - | - | - | - | - |
| `100115` | - | - | `111005;270|111004;630` | - | - | - | - | - | - |
| `100116` | - | - | `111005;550|111004;550` | - | - | - | - | - | - |
| `100117` | - | - | `111005;910|111004;390` | - | - | - | - | - | - |
| `100118` | - | - | `111005;1500` | - | - | - | - | - | - |
| `100119` | - | - | `111006;510|111005;1190` | - | - | - | - | - | - |
| `100120` | - | - | `111006;950|111005;950` | - | - | - | - | - | - |
| `100121` | - | - | `111006;1470|111005;630` | - | - | - | - | - | - |
| `100122` | - | - | `111006;2300` | - | - | - | - | - | - |
| `100123` | - | - | `111007;750|111006;1750` | - | - | - | - | - | - |
| `100124` | - | - | `111007;1350|111006;1350` | - | - | - | - | - | - |
| `100125` | - | - | `111007;2100|111006;900` | - | - | - | - | - | - |
| `100126` | - | - | `111007;3300` | - | - | - | - | - | - |
| `100127` | - | - | `111008;1080|111007;2520` | - | - | - | - | - | - |
| `100128` | - | - | `111008;2730|111007;1170` | - | - | - | - | - | - |
| `100129` | - | - | `111008;4200` | - | - | - | - | - | - |
| `100130` | - | - | `111009;4500` | - | - | - | - | - | - |
| `100131` | - | - | `111001;100` | - | - | - | - | - | - |
| `100132` | - | - | `111002;300` | - | - | - | - | - | - |
| `100133` | - | - | `111003;500` | - | - | - | - | - | - |
| `100134` | - | - | `111004;700` | - | - | - | - | - | - |
| `100135` | - | - | `111005;1000` | - | - | - | - | - | - |
| `100136` | - | - | `111005;1500` | - | - | - | - | - | - |
| `100137` | - | - | `111006;2000` | - | - | - | - | - | - |
| `100138` | - | - | `111006;3000` | - | - | - | - | - | - |
| `100139` | - | - | `111007;5000` | - | - | - | - | - | - |
| `100140` | - | - | `111007;7000` | - | - | - | - | - | - |
| `101131` | - | - | `111009;6500` | - | - | - | - | - | - |
| `101132` | - | - | `111009;7000` | - | - | - | - | - | - |
| `101133` | - | - | `111009;7500` | - | - | - | - | - | - |
| `101134` | - | - | `111009;8000` | - | - | - | - | - | - |
| `101135` | - | - | `111009;8500` | - | - | - | - | - | - |
| `101136` | - | - | `111009;9000` | - | - | - | - | - | - |
| `101137` | - | - | `111009;9500` | - | - | - | - | - | - |
| `101138` | - | - | `111009;10000` | - | - | - | - | - | - |
| `101139` | - | - | `111009;10500` | - | - | - | - | - | - |
| `101140` | - | - | `111009;11000` | - | - | - | - | - | - |
| `101141` | - | - | `111009;11500` | - | - | - | - | - | - |
| `101142` | - | - | `111009;12000` | - | - | - | - | - | - |
| `101143` | - | - | `111009;12500` | - | - | - | - | - | - |
| `101144` | - | - | `111009;13000` | - | - | - | - | - | - |
| `101145` | - | - | `111009;13500` | - | - | - | - | - | - |
| `410001` | - | - | `111001;10` | - | - | - | - | - | - |
| `410002` | - | - | `111001;20` | - | - | - | - | - | - |
| `410003` | - | - | `111001;30` | - | - | - | - | - | - |
| `410004` | - | - | `111001;50` | - | - | - | - | - | - |
| `410005` | - | - | `111001;70` | - | - | - | - | - | - |
| `410006` | - | - | `111001;90` | - | - | - | - | - | - |
| `410007` | - | - | `111001;110` | - | - | - | - | - | - |
| `410008` | - | - | `111001;130` | - | - | - | - | - | - |
| `410009` | - | - | `111002;50|111001;100` | - | - | - | - | - | - |
| `410010` | - | - | `111002;90|111001;80` | - | - | - | - | - | - |
| `410011` | - | - | `111002;130|111001;60` | - | - | - | - | - | - |
| `410012` | - | - | `111002;210` | - | - | - | - | - | - |
| `410013` | - | - | `111003;70|111002;160` | - | - | - | - | - | - |
| `410014` | - | - | `111003;130|111002;120` | - | - | - | - | - | - |
| `410015` | - | - | `111003;190|111002;80` | - | - | - | - | - | - |
| `410016` | - | - | `111003;300` | - | - | - | - | - | - |
| `410017` | - | - | `111004;110|111003;240` | - | - | - | - | - | - |
| `410018` | - | - | `111004;200|111003;200` | - | - | - | - | - | - |
| `410019` | - | - | `111004;320|111003;130` | - | - | - | - | - | - |
| `410020` | - | - | `111004;500` | - | - | - | - | - | - |
| `410021` | - | - | `111005;170|111004;380` | - | - | - | - | - | - |
| `410022` | - | - | `111005;300|111004;300` | - | - | - | - | - | - |
| `410023` | - | - | `111005;460|111004;190` | - | - | - | - | - | - |
| `410024` | - | - | `111005;700` | - | - | - | - | - | - |
| `410025` | - | - | `111006;230|111005;520` | - | - | - | - | - | - |

### 5.3 World Monsters & Bosses (`TableName.Monster` - 250 sampled; `ActivityMonsterBoss` - 9)
| Monster ID | Name | Level | Type | Stamina / Energy | Power / Extra |
|---|---|---:|---|---:|---|
| `9` | Boomer | 1 | `-` | - | - |
| `10` | Boomer | 2 | `-` | - | - |
| `11` | Boomer | 3 | `-` | - | - |
| `12` | Boomer | 4 | `-` | - | - |
| `13` | Boomer | 5 | `-` | - | - |
| `14` | Boomer | 6 | `-` | - | - |
| `15` | Boomer | 7 | `-` | - | - |
| `16` | Boomer | 8 | `-` | - | - |
| `17` | Boomer | 9 | `-` | - | - |
| `18` | Boomer | 10 | `-` | - | - |
| `100201` | Zombie | 1 | `-` | - | - |
| `100202` | Zombie | 2 | `-` | - | - |
| `100203` | Zombie | 3 | `-` | - | - |
| `100204` | Zombie | 4 | `-` | - | - |
| `100205` | Zombie | 5 | `-` | - | - |
| `100206` | Zombie | 6 | `-` | - | - |
| `100207` | Zombie | 7 | `-` | - | - |
| `100208` | Zombie | 8 | `-` | - | - |
| `100209` | Zombie | 9 | `-` | - | - |
| `100210` | Zombie | 10 | `-` | - | - |
| `100211` | Zombie | 11 | `-` | - | - |
| `100212` | Zombie | 12 | `-` | - | - |
| `100213` | Zombie | 13 | `-` | - | - |
| `100214` | Zombie | 14 | `-` | - | - |
| `100215` | Zombie | 15 | `-` | - | - |
| `100216` | Zombie | 16 | `-` | - | - |
| `100217` | Zombie | 17 | `-` | - | - |
| `100218` | Zombie | 18 | `-` | - | - |
| `100219` | Zombie | 19 | `-` | - | - |
| `100220` | Zombie | 20 | `-` | - | - |
| `100221` | Zombie | 21 | `-` | - | - |
| `100222` | Zombie | 22 | `-` | - | - |
| `100223` | Zombie | 23 | `-` | - | - |
| `100224` | Zombie | 24 | `-` | - | - |
| `100225` | Zombie | 25 | `-` | - | - |
| `100226` | Zombie | 26 | `-` | - | - |
| `100227` | Zombie | 27 | `-` | - | - |
| `100228` | Zombie | 28 | `-` | - | - |
| `100229` | Zombie | 29 | `-` | - | - |
| `100230` | Zombie | 30 | `-` | - | - |
| `100231` | Elite Zombie | 31 | `-` | - | - |
| `100232` | Elite Zombie | 32 | `-` | - | - |
| `100233` | Elite Zombie | 33 | `-` | - | - |
| `100234` | Elite Zombie | 34 | `-` | - | - |
| `100235` | Elite Zombie | 35 | `-` | - | - |
| `100236` | Elite Zombie | 36 | `-` | - | - |
| `100237` | Elite Zombie | 37 | `-` | - | - |
| `100238` | Elite Zombie | 38 | `-` | - | - |
| `100239` | Elite Zombie | 39 | `-` | - | - |
| `100240` | Elite Zombie | 40 | `-` | - | - |
| `100241` | Elite Zombie | 41 | `-` | - | - |
| `100242` | Elite Zombie | 42 | `-` | - | - |
| `100243` | Elite Zombie | 43 | `-` | - | - |
| `100244` | Elite Zombie | 44 | `-` | - | - |
| `100245` | Elite Zombie | 45 | `-` | - | - |
| `100601` | Furylord | 1 | `-` | - | - |
| `100602` | Furylord | 1 | `-` | - | - |
| `100603` | Furylord | 1 | `-` | - | - |
| `100604` | Furylord | 1 | `-` | - | - |
| `100605` | Furylord | 1 | `-` | - | - |

### 5.4 Radar Detect Events (`TableName.DetectEvent` - 250 Sampled / 400+ Total)
| Event ID | Name | Type | Quality / Color | Stamina | Description |
|---|---|---|---|---:|---|
| `1000` | Area Cleansing | `2` | `1` | - | Some zombies are roaming around. Please send troops for cleanup ASAP! |
| `1001` | Zombie Clearance | `2` | `2` | - | Some zombies are roaming around. Please send troops for cleanup ASAP! |
| `1002` | Zombie Clearance | `2` | `3` | - | Many zombies are gathering near the town, please send troops for cleanup ASAP! |
| `1003` | Area Cleansing | `2` | `4` | - | Many zombies are gathering near the town, please send troops for cleanup ASAP! |
| `1004` | Area Cleansing | `2` | `5` | - | Many zombies are gathering near the town, please send troops for cleanup ASAP! |
| `1005` | Resource Scavenge | `6` | `1` | - | There are many useful resources in the urban ruins waiting to be explored and... |
| `1006` | Ruins Exploration | `6` | `2` | - | The owner of the resources is nowhere to be found. You can send troops to col... |
| `1007` | Ruins Exploration | `6` | `3` | - | There are many useful resources in the urban ruins waiting to be explored and... |
| `1008` | Resource Scavenge | `6` | `4` | - | The owner of the resources is nowhere to be found. You can send troops to col... |
| `1009` | Resource Scavenge | `6` | `5` | - | There are many useful resources in the urban ruins waiting to be explored and... |
| `1012` | Area Cleansing | `2` | `3` | - | Many zombies are gathering near the town, please send troops for cleanup ASAP! |
| `1013` | Zombie Clearance | `2` | `4` | - | Many zombies are gathering near the town, please send troops for cleanup ASAP! |
| `1015` | Ruins Exploration | `6` | `1` | - | There are many useful resources in the urban ruins waiting to be explored and... |
| `1018` | Ruins Exploration | `6` | `4` | - | There are many useful resources in the urban ruins waiting to be explored and... |

### 5.5 Hero Bounties (`TableName.HeroBounty` - 72 Tasks)
| Bounty ID | Name | Rarity | Duration (h) | Heroes Req | Camp Req |
|---|---|---|---:|---:|---|
| `1` | Land Cultivation | `1` | 1 | 2 | `1;1` |
| `2` | Treasure Seeker | `1` | 1 | 2 | `2;2` |
| `3` | Power Plant | `1` | 1 | 2 | `3;3` |
| `4` | Mine Detection | `1` | 1 | 2 | `1;2` |
| `5` | Spy Interrogation | `1` | 1 | 2 | `1;3` |
| `6` | Creep Crusher | `1` | 1 | 2 | `2;3` |
| `7` | Assassination | `2` | 3 | 2 | `1;1` |
| `8` | Quelling Munity | `2` | 3 | 2 | `2;2` |
| `9` | Military Intervention | `2` | 3 | 2 | `3;3` |
| `10` | Overheard | `2` | 3 | 2 | `1;2` |
| `11` | Final Trial | `2` | 3 | 2 | `1;3` |
| `12` | Business Negotiation | `2` | 3 | 2 | `2;3` |
| `13` | Corn Dealer | `3` | 6 | 2 | `1;1` |
| `14` | Alloy Dealer | `3` | 6 | 2 | `2;2` |
| `15` | 132014 | `3` | 6 | 2 | `3;3` |
| `16` | Satellite Launcher | `3` | 6 | 2 | `1;2` |
| `17` | Convincing Arms Dealer | `3` | 6 | 2 | `1;3` |
| `18` | Military Orders | `3` | 6 | 2 | `2;3` |
| `19` | Ammo Dealer | `4` | 8 | 3 | `3;2;2` |
| `20` | Weapons Dealer | `4` | 8 | 3 | `1;3;3` |
| `21` | Missile Deployment | `4` | 8 | 3 | `1;1;2` |
| `22` | Radar Maintenance | `4` | 8 | 3 | `1;2;3` |
| `23` | Rocket Launcher | `4` | 8 | 3 | `1;2;3` |
| `24` | Rocket Maintenance | `4` | 8 | 3 | `1;2;3` |
| `25` | Shooter Maintenance | `5` | 11 | 3 | `1;2;2` |
| `26` | Missile Interception | `5` | 11 | 3 | `1;3;3` |
| `27` | 132026 | `5` | 11 | 3 | `2;2;3` |
| `28` | Behind Enemy Lines | `5` | 11 | 3 | `2;3;3` |
| `29` | Drive A Wedge | `5` | 11 | 3 | `1;1;3` |
| `30` | Besiege Enemies | `5` | 11 | 3 | `1;1;2` |
| `31` | Sweep The Battlefield | `6` | 23 | 3 | `1;1;1` |
| `32` | World War | `6` | 23 | 3 | `2;2;2` |
| `33` | State Wars | `6` | 23 | 3 | `3;3;3` |
| `34` | Sink or Swim | `6` | 23 | 3 | `1;1;1` |
| `35` | Rise from Hopeless | `6` | 23 | 3 | `2;2;2` |
| `36` | Make or Break | `6` | 23 | 3 | `3;3;3` |
| `51` | Land Cultivation | `1` | 1 | 2 | `1;1` |
| `52` | Treasure Seeker | `1` | 1 | 2 | `2;2` |
| `53` | Power Plant | `1` | 1 | 2 | `3;3` |
| `54` | Mine Detection | `1` | 1 | 2 | `1;2` |
| `55` | Spy Interrogation | `1` | 1 | 2 | `1;3` |
| `56` | Creep Crusher | `1` | 1 | 2 | `2;3` |
| `57` | Assassination | `2` | 3 | 2 | `1;1` |
| `58` | Quelling Munity | `2` | 3 | 2 | `2;2` |
| `59` | Military Intervention | `2` | 3 | 2 | `3;3` |
| `60` | Overheard | `2` | 3 | 2 | `1;2` |
| `61` | Final Trial | `2` | 3 | 2 | `1;3` |
| `62` | Business Negotiation | `2` | 3 | 2 | `2;3` |
| `63` | Corn Dealer | `3` | 6 | 2 | `1;1` |
| `64` | Alloy Dealer | `3` | 6 | 2 | `2;2` |

### 5.6 Resource Gather Tiles (`TableName.GatherResource` - 121 Tiles) & VIP Levels (`TableName.Vip` - 20 Levels)
| VIP ID | Points Required | Key Perks / Fields |
|---|---:|---|
| `0` | 0 | display=30226\|30228, effect=30226;5\|30228;5, freebie_banner=vip_bg_banner1, gift_pic=UIVIP_img_... |
| `1` | 400 | display=30074, effect=30226;5\|30228;5\|30074;5, freebie_banner=vip_bg_banner1, gift_pic=UIVIP_im... |
| `2` | 2000 | display=30061\|30063, effect=30226;5\|30228;5\|30074;5\|30061;5\|30063;5, freebie_banner=vip_bg_b... |
| `3` | 5000 | display=30072\|30070, effect=30226;5\|30228;5\|30074;5\|30072;5\|30061;5\|30063;5\|30070;5, freeb... |
| `4` | 10000 | display=30071\|30319, effect=30226;5\|30228;5\|30074;5\|30072;5\|30061;5\|30063;5\|30070;5\|30071... |
| `5` | 18000 | display=31008\|310, effect=30226;5\|30228;5\|30074;5\|30072;5\|30061;5\|30063;5\|30070;5\|30071;5... |
| `6` | 30000 | display=30226\|30228\|30480, effect=30226;10\|30228;10\|30074;5\|30072;5\|30061;5\|30063;5\|30070... |
| `7` | 50000 | display=31008, effect=30226;10\|30228;10\|30074;5\|30072;5\|30061;5\|30063;5\|30070;5\|30071;5\|3... |
| `8` | 100000 | display=50001\|30472, effect=30226;10\|30228;10\|30074;10\|30072;5\|30061;5\|30063;5\|30070;10\|3... |
| `9` | 150000 | display=40020, effect=30226;10\|30228;10\|30074;10\|30072;10\|30061;5\|30063;5\|30070;10\|30071;1... |
| `10` | 250000 | display=40050, effect=30226;10\|30228;10\|30074;10\|30072;10\|30061;5\|30063;5\|30070;20\|30071;1... |
| `11` | 500000 | display=73, effect=30226;20\|30228;20\|30074;10\|30072;10\|30061;5\|30063;5\|30070;20\|30071;15\|... |
| `12` | 800000 | display=35000\|35004\|40049\|30470, effect=30226;20\|30228;20\|30074;10\|30072;10\|30061;5\|30063... |
| `13` | 1200000 | display=35000\|51001, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|... |
| `14` | 2000000 | display=35004, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|30071;2... |
| `15` | 3000000 | display=50005\|35012, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|... |
| `16` | 5000000 | display=50005\|35064, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|... |
| `17` | 15000000 | display=50005, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|30071;2... |
| `18` | 50000000 | display=51002, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|30071;2... |
| `19` | 120000000 | display=51003, effect=30226;20\|30228;20\|30074;20\|30072;20\|30061;5\|30063;5\|30070;30\|30071;2... |

## 6. Complete XML Table Schema Registry (All 421 Registered Tables - 190,423 Total Rows)

| Table Reference | XML Name | Loaded | Rows | Column Schema |
|---|---|---|---:|---|
| `SlgTableName.ActivityTreasureBox` | `activity_spin` | YES | 1 | id, activity, cost_item, spin_cost, daily_free_time, spin_cost_5, draw_max_daily, box_num, unlock_goods, auto_rank, rank_reward, stage_re... |
| `SlgTableName.ActivityTreasureBoxPara` | `activity_spin_para` | YES | 26 | id, spin_id, pool_id, goods, spin_item, item_priority, spin_item_icon, spin_bg_icon, reward_icon, reward_name, rate, order, guarantee_act... |
| `SlgTableName.AllianceAttrXLevel` | `alliance_attribute_x_level` | NO | 0 | - |
| `SlgTableName.AllianceAttrXLine` | `alliance_attribute_x_line` | NO | 0 | - |
| `SlgTableName.AllianceMilestoneAllianceTask` | `alliance_milestone_alliance_task` | NO | 0 | - |
| `SlgTableName.AllianceMilestoneManagementTask` | `alliance_milestone_management_task` | NO | 0 | - |
| `SlgTableName.AllianceMilestonePersonalTask` | `alliance_milestone_personal_task` | NO | 0 | - |
| `SlgTableName.AllianceMilestoneStage` | `alliance_milestone_stage` | NO | 0 | - |
| `SlgTableName.AllianceMilestoneTaskGuide` | `alliance_milestone_task_guide` | NO | 0 | - |
| `SlgTableName.FormStatus` | `formation_status` | YES | 6 | id, type, type2, time, group, priority, name, description, icon, effect, effect_num |
| `TableName.APSScienceTab` | `aps_science_tab` | YES | 21 | id, name, position, order, quality, type, para1, unlock_level, building, icon_start, icon, science, unlock_see, unlock_condition *(+2 cols)* |
| `TableName.APS_PUSH` | `APS_push` | YES | 62 | id, push_unlock, push_type, tag, type_value, dialogId, building, param_count, times, player_mark, push_time, push_tab, settingTitle, only_gm |
| `TableName.APS_SINGLEMAP_JUNK` | `aps_singlemap_junk` | YES | 31 | id, Name, Desc, Show, Scale, Radius, Time, Dialog, Action, Reward, pic, Type |
| `TableName.APS_SINGLEMAP_PIONEER` | `aps_singlemap_pioneer` | YES | 23 | id, NextID, UnclockFog, Noviceboot, Pos, UnclockType, UnclockPara, ShowPos, TagType, Tagpara, ArrowShow |
| `TableName.APS_Season` | `aps_season` | YES | 5 | id, season, season_list_icon, start_time, trendsId, mail_limit, pre_settle_time, pre_settle_mail, settle_time, settle_mail, pre_end_time,... |
| `TableName.APS_shop` | `aps_shop` | YES | 3,056 | id, shop_id, goods, goods_num, currency, currency_num, server, order, cycle, cycle_times, vip_level, discount, time_type, start_time *(+2... |
| `TableName.ActSeven` | `AcitivitySeven_New` | YES | 620 | id, type1, type1_text, type2, type2_text, task |
| `TableName.ActivityBarter` | `activity_barter` | YES | 276 | id, activity_id, item1, item2, times, not_reset, vip, is_decoration_gift, gift_goods, gift_require, time_type, start_time, duration, end_... |
| `TableName.ActivityBoxOpen` | `activity_boxopen` | YES | 4 | id, activity, cost_item, cost_1, cost_1_free, cost_5, draw_max_daily, box_num, unlock_goods, auto_rank, rank_reward, draw_reward, draw_re... |
| `TableName.ActivityBoxOpenPara` | `activity_boxopen_para` | YES | 101 | id, boxopen_id, type, goods, rate, guarantee_activity, order, reward_buy_time, reward_hold_time, reward_icon, reward_name, unlock_cost, u... |
| `TableName.ActivityCakeTeamCake` | `activity_cake_team_cake` | YES | 15 | id, cake_group_id, cake_level, cake_progress_value, cake_reward |
| `TableName.ActivityCakeTeamEvent` | `activity_cake_team_event` | YES | 11 | id, event_group_id, event_type_id, point_num, reward_id, event_cd, event_name, event_tips, event_para1, event_para2 |
| `TableName.ActivityCakeTeamMain` | `activity_cake_team_main` | YES | 1 | id, act_id, need_goods_id, point_goods_id, spin_group_id, spin_times, event_group_id, event_rate, cake_group_id, team_lock_cd, quick_chat... |
| `TableName.ActivityCakeTeamSpin` | `activity_cake_team_spin` | YES | 10 | id, spin_group_id, goods_id, point_num, rate, guarantee_rule, probability |
| `TableName.ActivityCyclebox` | `activity_cyclebox` | YES | 6 | id, activity_id, activity_relation, box_id, send_cost_id, box_score, box_score1, open_maxnum, point_item, initial_box, box_showreward2, b... |
| `TableName.ActivityCycleboxPara` | `activity_cyclebox_para` | YES | 162 | id, box_id, order, reward_group, goods, rate, show_rate, guarantee |
| `TableName.ActivityFlip` | `activity_flip` | YES | 5 | id, activity, cost_goods, first_gold, gold_goods, gold_rate, gold_range, purple_goods, purple_rate, purple_range, blue_goods, blue_rate, ... |
| `TableName.ActivityItemDrop` | `activity_item_drop` | YES | 86 | id, activity, type, good, limit, para, para1, para2, reward, icon, name, desc, tips, jumpType |
| `TableName.ActivityMonster` | `activity_monster` | YES | 19 | id, difficulty_des, monster, description, monster_des, icon, difficulty_title, icon_detail, monster_power, call_consume, season, difficul... |
| `TableName.ActivityMonsterBoss` | `activity_monsterboss` | YES | 9 | id, difficulty, monster_id, condition, reward_alli_show, reward_solo_show, time |
| `TableName.ActivityOverview` | `activity_showlist` | YES | 8 | id, type, unlock, name, reward_show, image, unlock_image, order |
| `TableName.ActivityPanel` | `activity_panel` | YES | 773 | id, type, age_restriction, name, order, desc_info, story, needMainCityLevel, list_icon, Advertise_pic, activity_pic, show_type, reward_go... |
| `TableName.ActivityPuzzleMonster` | `activity_puzzle_monster` | YES | 3 | id, name, color, time, monster_id, reward_show, reward_detail, ranking_reward, partake_reward, call_reward, consume, unlock |
| `TableName.ActivityRewardShow` | `Activity_Reward_Show` | YES | 4 | id, activity, excess_reward_1, special_monster |
| `TableName.ActivityShow` | `activity_show` | NO | 0 | - |
| `TableName.ActivityTip` | `activity_tips` | YES | 1 | id, activity_type, type, priority, condition, iconlist, topiclist, showonce |
| `TableName.ActivityTreasureAlliance` | `activity_treasure_alliance` | YES | 20 | id, activity, treasure_id, picture, collection, reward |
| `TableName.ActivityTreasureHunt` | `activity_treasure_hunt` | YES | 160 | id, level, activity, layout_id, layout_rate, reward |
| `TableName.ActivityTreasureHuntPara` | `activity_treasure_hunt_para` | YES | 116 | id, map_width, map_height, treasure_layout |
| `TableName.ActivityTreasurePara` | `activity_treasure_para` | YES | 97 | id, type, horizontal, vertical, picture, shape_pic, rotate, group, bomb, reward, rate |
| `TableName.Adaptive_Box` | `adaptive_box` | YES | 250 | id, group, level, type, base_itemid, base_num |
| `TableName.AdventureCase` | `explorer_case` | YES | 150 | id, content, monster, buff, monster_showreward, reward, reward_show, random, randomdes |
| `TableName.AdventureEntrance` | `explorer_entrance` | YES | 30 | id, pveLevel, reward |
| `TableName.Affect_Num` | `affect_num` | YES | 243 | id, des, negative, num_type |
| `TableName.AlEffect` | `alliance_effect` | YES | 6 | id, name, icon, description, description_value, description_type, order |
| `TableName.AlScience` | `alScience` | YES | 150 | id, science_id, science_lv, max_lv, value, time, resource, donate, donate_price_start, donate_price_add, donate_price_max, schedule, cont... |
| `TableName.AlScienceTab` | `alScienceTab` | YES | 51 | id, name, description, description_tip, icon, max_lv, position, relation, info, tab, schedule, contribution |
| `TableName.AllianceFunction` | `alliance_function` | YES | 2 | id, lock_mode, id_tips, lock_condition |
| `TableName.AllianceGift` | `alliance_gift` | YES | 400 | id, level, exp, type, subtype, exceed_time, rewardId, scale, rate_show |
| `TableName.AllianceGiftGroup` | `alliance_gift_group` | YES | 67 | id, type, name, desc, color, icon, sender, title, each_exp, giftshow, othershow, key_exp, boxshow, icon_open |
| `TableName.AllianceHaggle` | `alliance_haggle` | YES | 71 | id, unlock_level, members_num, group, rate, limit_servers, reward, haggle_type, price, lowest_price, min_number, haggle_min, min_diamonds... |
| `TableName.AllianceItemWarehouse` | `alliance_item_warehouse` | NO | 0 | - |
| `TableName.AllianceLog` | `alliance_log` | YES | 33 | id, type, scale, icon, path |
| `TableName.AllianceMine` | `alliance_res_build` | YES | 37 | id, name, desc, model, icon, res_size, offter_range, level, res_durable, res_base_durable, res_num, collect_type, param, collect_speed *(... |
| `TableName.AllianceResBuild` | `alliance_res_build` | YES | 37 | id, name, desc, model, icon, res_size, offter_range, level, res_durable, res_base_durable, res_num, collect_type, param, collect_speed *(... |
| `TableName.AllianceResource` | `alliance_resource` | YES | 24 | id, icon, name, description, city_level, alliance_gold_num, alliance_gold_capacity, alliance_gold_gathering, alliance_metal_num, alliance... |
| `TableName.AllianceSkill` | `alliance_skill` | YES | 1 | id, type, name, desc, rule, color, pre_time, during_time, prefab, punish_time, cd_time, effect_scope, effect_scope_newrule, season *(+10 ... |
| `TableName.AllianceTask` | `alliance_task` | YES | 16 | id, unlock_time, name, description, type, para, times, reward, quest_pic, jump, record, para2 |
| `TableName.Announcement` | `scrolling_announcement` | YES | 79 | id, type, content, priority, base, block, para1, loop |
| `TableName.Aps_Resource_Item` | `aps_resource_item` | YES | 78 | id, type, itemType, building, name, desc, order, price, price_diamond, trade_num, weight, isrob, show, pic *(+11 cols)* |
| `TableName.ArmsTab` | `APS_arms` | YES | 393 | id, name, description, quality, max_train, resource_need, time, treat_time, treat_resource, unlock_train_build, unlock_upgrade_build, arm... |
| `TableName.Army` | `army` | YES | 7,578 | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1, skill2, skill3, skill4, skill5 |
| `TableName.Army_B` | `army_b` | YES | 6,858 | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1, skill2, skill3, skill4, skill5 |
| `TableName.Army_C` | `army_c` | YES | 6,858 | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1, skill2, skill3, skill4, skill5 |
| `TableName.ArrowTip` | `arrow_tips` | YES | 8 | id, type, number, base, order, time |
| `TableName.Barrel_Monster` | `barrel_monster` | YES | 31,899 | id, baseId, property |
| `TableName.Barrel_Monster_Base` | `barrel_monster_base` | YES | 349 | id, asset, model_size, relation_type, monster_type, is_boss, param, hp_bar_num, death_sound, is_attack, is_move, move_speed, alert_range,... |
| `TableName.Barrel_PVE` | `barrel_pve` | YES | 40 | id, pve_level_id, level, lock, lock_time, lock_share, score_standard, if_difficult |
| `TableName.BaseExpansion` | `aps_base_expansion` | YES | 42 | id, x, y, range, is_only_road, treetype |
| `TableName.BaseUnlockBuilding` | `baseUnlockBuilding` | YES | 15 | id, buildingId |
| `TableName.BattleAnimation` | `battle_animation` | NO | 0 | - |
| `TableName.BattleBuff` | `aps_pve_battlebuff` | YES | 71 | id, type, buffId, icon, LocalType, group, not_choose, show_group, timetype, time |
| `TableName.BattlePass` | `battlepass` | YES | 4,201 | id, activity_panel_Id, level, levelup_exp, free_reward, pay_reward, highlight_reward, pay_item, free_item, highlight_locate |
| `TableName.Bauble` | `bauble` | YES | 31 | id, name, description, icon, bg_pic, quality, max_lv, active_num, effect_new, effect_description, effect_value, power, show_type, goods *... |
| `TableName.BaublePos` | `bauble_pos` | NO | 0 | - |
| `TableName.BaubleRating` | `bauble_rating` | YES | 12 | id, name, rank, stage, stars, exp, icon, reward |
| `TableName.BirthPoint` | `birth_coordinate_0` | YES | 361 | id, X, Y, resource |
| `TableName.BuildQueue` | `aps_build_queue` | YES | 6 | id, name, uav_describe, gift |
| `TableName.BuildStatus` | `building_status` | YES | 5 | id, type, type2, time, effect, effect_num, group, priority, name, description, icon |
| `TableName.BuildZone` | `aps_buildzone` | YES | 1,215 | id, pos, zone_type |
| `TableName.Build_Fence` | `build_fence` | YES | 31 | id, FencePath |
| `TableName.Building` | `building` | YES | 4,089 | id, name, description, long_description, pic, model, model_world, scan, order, effect_local, tab_type, build_type, max_level, honor_max_l... |
| `TableName.BuildingBreak` | `building_break` | YES | 1 | id, buildlv, show_lv, description, direction_id, condition1, condition2, condition3 |
| `TableName.BuildingDes` | `building_des` | YES | 10 | id, order, effect_local, tab_type, max_level, tiles, unlock_num, building_show, put, red_dot |
| `TableName.BuildingDirection` | `building_direction` | YES | 3 | id, name, icon, description, new_build |
| `TableName.CLanguageRoom` | `language_channel` | YES | 14 | id, channel_type, group |
| `TableName.C_Animations` | `c_animations` | YES | 67 | id, idle, move, walk, attack, dead, sneakIdle, sneakMove, intertialIdle, sneak |
| `TableName.C_BluePrint` | `c_blueprint` | YES | 13 | id, target, type, source, level, buildinglevel, order, need_talent |
| `TableName.C_Equips` | `c_equips` | YES | 63 | id, type, melee, model, range, attack, defense, duration, randomDuration, animation, moveSpeed, attackSpeed, cooldown, debuff *(+8 cols)* |
| `TableName.C_RewardDetailTips` | `c_reward_detail_tips` | YES | 68 | id, type, pic, title, desc |
| `TableName.C_Sound` | `c_sound` | YES | 285 | id, group, soundType, soundList, playType, Volume, Loop, SubType, param1, param2 |
| `TableName.CampEffect` | `camp_effect` | YES | 4 | id, camp_type, camp_effect, icon, des |
| `TableName.CampEffect_B` | `camp_effect_b` | YES | 4 | id, camp_type, camp_effect, icon, des |
| `TableName.CapitalWar` | `capital_war` | YES | 1 | id, season, score_reward, rank_reward, kill_score, dead_score, occupy_score |
| `TableName.CarCompon` | `car_compon` | YES | 90 | id, icon, name, category, level, quality, combine_next, combine, combine_num, level_max, effects, effect_num, level_exp_add, level_open *... |
| `TableName.CarMicrochip` | `car_microchip` | YES | 48 | id, desc, name, quality, slot, army_type, icon, is_craft, craft_materials |
| `TableName.CarMicrochipAttribute` | `car_microchip_attribute` | YES | 1,968 | id, effects, microchip_id, rank, grade, power, id_next, skill, skill_level |
| `TableName.CarMicrochipBox` | `car_microchip_box` | YES | 1,583 | id, goods_id, reward_id, num, odds |
| `TableName.CarMicrochipGrading` | `car_microchip_grading` | YES | 33 | id, name, star, type, color, effect, effect_num |
| `TableName.CarMicrochipPromote` | `car_microchip_promote` | YES | 180 | id, quality, rank, grade, value_self, cost_goods, return_good, return_self, cost_self, cost_item, return_item |
| `TableName.CarShow` | `car_show` | YES | 5 | id, name, color, icon, icon_unlock, icon_army, cv_show, sound_idle, model, talent, model_point, talent_point, nodal, nodal_effect *(+3 co... |
| `TableName.CarTalent` | `car_talent` | YES | 652 | id, level, max_level, type, cost, need_car_level, need_car_level_new, position, order, car_condition, effect, effect_num, color, icon *(+... |
| `TableName.CarTalentGrading` | `car_talent_grading` | YES | 8 | id, name, desc, level, exp, car_level_tips, effect, effect_num, level_free, goods, desc_sp, effect_timeframe, effect_num_timeframe, timef... |
| `TableName.Car_Show_Barrel` | `car_show_barrel` | YES | 30 | id, lock_enemy, drift_pos, drift_delay_time, stand_pos, stand_delay_time, stand_stay_time, stand_abort_time, advance_pos, advance_delay_t... |
| `TableName.Chapter` | `chapter_1` | YES | 1 | id, chapter, base_lv, name, tag, tag_text, description, pic, reward, quest, character, dialogue |
| `TableName.CityJunk` | `aps_singlemap_junk` | YES | 31 | id, Name, Desc, Show, Scale, Radius, Time, Dialog, Action, Reward, pic, Type |
| `TableName.CityManage` | `aps_city_buff` | YES | 8 | id, name1, name2, name3, desc, icon, type, type2, group, status, formation_status |
| `TableName.City_Resident` | `city_resident` | YES | 8 | id, building |
| `TableName.CollectResource` | `aps_collect_resource` | YES | 3 | id, resourceType, para, diffPoint, model |
| `TableName.DD_Season_Group` | `DD_season_group` | NO | 0 | - |
| `TableName.DailyQuest` | `daily_quest` | YES | 52 | id, accept1, name, desc, point, para2, gotype, gotype2, go, gobuild, icon, order, show, gopara |
| `TableName.DateBaseOtherLoadingTips` | `loadingTips` | YES | 23 | id, description, level_range, delay_time, rate |
| `TableName.DayAct` | `DayAct` | YES | 87 | id, type1, type1_text, type2, type2_text, title, dialog, daily_bg, reward_show |
| `TableName.Decompose` | `decompose` | NO | 0 | - |
| `TableName.Decoration` | `decoration` | YES | 114 | id, type, name, icon, image, camera, camera2, type_gain, quality, order, bubble_param, model, model_world, para_gain *(+25 cols)* |
| `TableName.DemonHunterInfo` | `night_demon_hunter_info` | YES | 12 | id, hunter_quality, weight, hunter_name, hunter_desc, hunter_icon, hunter_mission_icon, hunter_pic, map_dialogue_random, complete_config,... |
| `TableName.DemonHunterQuest` | `night_demon_hunter_quest` | YES | 13 | id, quest_pool, weight, quest_id, quest_name, quest_desc, quest_icon_small, quest_icon, quest_reward, reward_show, quest_quality, quest_i... |
| `TableName.Desert` | `desert` | YES | 31 | id, desert_type, season, desert_level, desert_res, neu_desert_army, desert_army, neu_desert_monster, desert_monster, forceScore, season_s... |
| `TableName.DesertGoldmineWar` | `DesertGoldmineWar` | NO | 0 | - |
| `TableName.DesertRefresh` | `desert_refresh` | YES | 87 | id, city_id, em_desertid, desertid, num, desert_lv_range |
| `TableName.DesertSkillXml` | `desertSkill` | NO | 0 | - |
| `TableName.DesertTalent` | `DesertTalent_DesertTalent` | NO | 0 | - |
| `TableName.DesertTalentStats` | `DesertTalentStats` | NO | 0 | - |
| `TableName.DetectEvent` | `detect_event` | YES | 3,275 | id, type, type2, name, description, quality, icon, banner_image, panel_banner, para, image, pic, name_value, season *(+7 cols)* |
| `TableName.Diary` | `diary` | NO | 0 | - |
| `TableName.DigActivityDig` | `activity_dig` | YES | 3 | id, activity, cost_goods, diamond_buy, activity_relation, level_big, goods_rare_small, small_recommend, goods_rare_big, big_recommend, go... |
| `TableName.DigActivityPara` | `activity_dig_para` | YES | 2,125 | id, dig_id, level, goods_normal, rate, rate_rare, guarantee |
| `TableName.DinosaurBoss` | `dinosaur_boss` | YES | 5 | id, monster, title, reward, name, boss_frame, sfx_ui_wake, lop_strtime, sfx_ui_loop, loptime, sfx_wake, sfx_atk_02, sfx_attack, sfx_death... |
| `TableName.DoomsDayNote` | `doomsdaynote_doomsdaynote` | NO | 0 | - |
| `TableName.DragonBuilding` | `dragon_building` | YES | 7 | id, type, size, name, des, model, pic, circle_pic, coordinate, occupy_time, open_time, circle, alliance_point, first_alliance_point *(+15... |
| `TableName.EffectNumDesc` | `effect_num_des` | YES | 747 | id, type, des, class, class_order, icon |
| `TableName.Equip` | `ds_equip` | YES | 18 | id, desc, name, quality, slot, army_type, icon, img, basic_attributes, break_exp, unlock_level, is_craft, time, craft_materials *(+9 cols)* |
| `TableName.EquipAttribute` | `ds_equip_attribute` | YES | 2,924 | id, effects, power, pve_hp |
| `TableName.EquipForgeMythical` | `ds_equip_mythical` | YES | 7 | id, level, level_limit, promote_limit, cost_goods, cost_resource, reset_goods |
| `TableName.EquipMaterial` | `ds_equip_material` | YES | 5 | id, category, quality, combine, break |
| `TableName.EquipPromote` | `ds_equip_promote` | YES | 31 | id, level, rank, grade, level_up, cost_goods, cost_resource, reset_goods, cost_equips, return_good, reset_equips |
| `TableName.EquipRandomEffect` | `equip_random_effect` | NO | 0 | - |
| `TableName.EquipUpgrade` | `ds_equip_upgrade` | YES | 12 | id, quality, slot, army_type, highest_level, stone_upgrade_cost |
| `TableName.Equip_Suit` | `suit_equip` | YES | 3 | id, type, name, description, order, equip, effect_description1, value1, unlock_tips1, effect_condition1, effect_description2, value2, unl... |
| `TableName.Factory` | `aps_factory` | YES | 45 | id, name, build_type, unlock_type, unlock_condition, input_resource_goods, time, get_resource_goods, icon, order, group, exp, show_num, s... |
| `TableName.FakePlayer` | `fake_player` | YES | 1,430 | id, type, name, country, simple_name, alliance_num |
| `TableName.Farming` | `aps_farming` | YES | 12 | id, product_name, build_id, order, unlock_order, group, unlock_type, unlock_condition, produce_time, get_resource_goods, icon, model_name... |
| `TableName.FieldMonster` | `field_monster` | NO | 0 | - |
| `TableName.FoodFestivalEatBuild` | `food_festival_building` | YES | 3 | id, quality, alliance_res_build_id, rank, table, name, pic, pic_1, des, world_des |
| `TableName.FoodFestivalEatTable` | `food_festival_table` | YES | 16 | id, level, num, name, des, model, pic, pic_1, pic_2, quality, reward, show_reward, reward_desc, reward_des2 *(+5 cols)* |
| `TableName.FoodFestivalIngredients` | `food_festival_ingredients` | YES | 24 | id, activity_id, good_id |
| `TableName.FormStatus` | `formation_status` | YES | 6 | id, type, type2, time, group, priority, name, description, icon, effect, effect_num |
| `TableName.FossilBook` | `fossil_book` | YES | 40 | id, num, name, goods, egg_num, des_got, des_bef, pic_got, icon, pic_bef, activity_id, reward, unlock_cost_after_season |
| `TableName.GarageModify` | `car_modify_new` | YES | 351 | id, level, garage, add_exp, exp, additional_effect, additional_effect_num, additional_effect_num_show, item, power |
| `TableName.GaragePart` | `car_transform` | YES | 600 | id, type, garage, max_level, level, effect, effect_num, name, icon |
| `TableName.GatherResource` | `aps_gather_resource` | YES | 121 | id, resource_type, param, level, reserve, size, expire, gathering, show_gathering, collect_power, name, pic, desc, model *(+2 cols)* |
| `TableName.GhostKingDonate` | `night_eternal_duke_donate` | YES | 2 | id, donate_type, donate_stage, stage_reward, stage_reward_show, reissue_mail |
| `TableName.GhostKingInfo` | `night_eternal_duke_info` | YES | 7 | id, season_week, name, lv, threat_lv, desc, icon, spine_step, activity_icon, monster_id, durability, skill, join_reward, join_reward_show... |
| `TableName.Global` | `APS_global` | YES | 2 | id, k1, k2 |
| `TableName.GoldrushBuilding` | `goldrush_building` | NO | 0 | - |
| `TableName.GoodsTab` | `goods` | YES | 1,025 | id, name, name_value, icon, description, type, lv, lv_limit, para, color, page, pages, use, useall *(+29 cols)* |
| `TableName.Government` | `government` | YES | 19 | id, name, icon, effect, can_appoint, only_president_appoint, is_positive, title_name, type |
| `TableName.Guide` | `noviceboot` | YES | 1,246 | id, returnstepid, savedoneid, jumptype, jumppara, jumpid, nextid, triggertype, triggerpara, forcetype, waittime, tipswaittime, type, para... |
| `TableName.GuideB` | `noviceboot_B` | YES | 1,131 | id, returnstepid, savedoneid, jumptype, jumppara, jumpid, nextid, triggertype, triggerpara, forcetype, waittime, tipswaittime, type, para... |
| `TableName.GuideStep` | `guide_step_GuideStep` | NO | 0 | - |
| `TableName.GuideStepContentInfo` | `guide_step_ContentInfo` | NO | 0 | - |
| `TableName.GuideTab` | `guide` | NO | 0 | - |
| `TableName.HeroAppearance` | `lw_hero_appearance` | YES | 129 | id, model_path, simple_model_path, model_size, hero_effect, fire_path, city_model_path, hero_detail_shadow_scale, hero_detail_shadow_pos,... |
| `TableName.HeroArkCore` | `hero_core` | YES | 7 | id, core_type, condition, effect |
| `TableName.HeroBattle_Skill` | `herobattle_skill` | YES | 21 | id, week, time, duration, hero, skill, hero_pic, tips |
| `TableName.HeroBounty` | `hero_bounty` | YES | 72 | id, name, description, rarity, function, time_h, hero_num, camp_requirements, exp_hero, exp, item_show, reward, rarity_requirements, star... |
| `TableName.HeroColor` | `APS_hero_color` | YES | 6 | id, star_limit_level_1, star_limit_level_2, star_limit_level_3, star_limit_level_4, star_limit_level_5, star_up_1, star_up_2, star_up_3, ... |
| `TableName.HeroEntrust` | `hero_entrust` | YES | 2 | id, Description, dub, Npc_Model, Position, Pre_quest, Demand, Reward_hero_fake, Npc_Pic |
| `TableName.HeroIntensify` | `hero_camp_intensify` | YES | 10,521 | id, group, lv, season, max_lv, cost, power, effect, camp, effect_ext |
| `TableName.HeroIntensifyRandomEffect` | `hero_camp_random` | YES | 1,212 | id, name, description, pic, effect_value, tips |
| `TableName.HeroMilitaryRank` | `aps_heroes_rank` | YES | 52 | id, level, stage, cost_medal, stage_show, name, icon, cost_coin, skill, require, atk, def, troop |
| `TableName.HeroMilitaryRankLv` | `aps_heroes_rankLv` | YES | 8 | id, level, skillLv, name, icon, atk, def, troop |
| `TableName.HeroMonthCard` | `hero_monthcard` | YES | 88 | id, name, description, sub_name, reward_pic, reward1_pic, reward2_pic, reward3_pic, reward4_pic, reward5_pic |
| `TableName.HeroOfficial` | `hero_official` | YES | 54 | id, camp, type, official_position, official_name, unlock_lv, effect, max_value, max_hero_power, extra_condition, extra_value, buff_lv |
| `TableName.HeroPreviewSKill` | `hero_preview_skill` | NO | 0 | - |
| `TableName.HeroRecruit` | `officer_recruit` | YES | 9 | id, type, quest_recruit_type, order, item, function, name, time, rate1, rate2, class, pitypro, limit_num, history_extract *(+12 cols)* |
| `TableName.HeroSPEquip` | `heroes_exclusive_equip` | YES | 390 | id, group, level, name, effect, cost_item, cost_num, icon, image, special_effects, spine, require_rank, unlock_skill, skill *(+6 cols)* |
| `TableName.HeroSPEquipBreak` | `exclusive_equip_breakthrough` | YES | 78 | id, group, level, name, effect, cost_item, cost_num, require_rank, max_level, unlock_skill, skill, barrel_skill, unlock_skill_new, skill_... |
| `TableName.HeroSkill` | `new_hero_skills` | NO | 0 | - |
| `TableName.HeroStation` | `hero_station` | YES | 16 | id, build_id, career, people_unit_limit, order |
| `TableName.HeroTab` | `new_heroes` | NO | 0 | - |
| `TableName.Hero_Lack_Tips` | `hero_lack_tips` | YES | 42 | id, heroid, fragmentid, tips, order, name, btn_name, base, pic, para1 |
| `TableName.Hero_Skin` | `aps_new_heros_skin` | YES | 75 | id, hero_id, sorting, hero_spine, skin_icon, skin_name, default_skin, hero_icon, round_hero_icon, hero_body, hero_halfbody, hero_body_2D,... |
| `TableName.Hero_Skin_Shop` | `aps_new_heros_skin_shop` | YES | 34 | id, type, type_para, goods, price_type, price_type_para, show_type, show_service, time_type, start_time, duration, show_tips, show_order |
| `TableName.Hero_Station` | `hero_station` | YES | 16 | id, build_id, career, people_unit_limit, order |
| `TableName.IceAnimals` | `ice_animals` | YES | 18 | id, create_type, activity_id, name, desc, downtime, size, type, model, tips_icon, ui_icon, dialog, direct_reward, digtime *(+4 cols)* |
| `TableName.IceCaveAtlasReward` | `icecave_atlas_reward` | YES | 7 | id, type, star_node, active_condition, active_reward, show_goods_id |
| `TableName.IceCaveFish` | `icecave_fish` | YES | 65 | id, name, desc, color, pic, pic_none, star_num, atlas_diamond, file_number, can_get_from, unlock_cost_after_season, is_special |
| `TableName.IceCaveFishGroup` | `icecave_fish_group` | YES | 10 | id, fish_produce_weight |
| `TableName.IceCaveInfo` | `icecave_info` | YES | 10 | id, level, model, banner, name, desc, icon, xy, monster_id, durability, hp_bar_unit, dur_bar_unit, size, plus_size *(+6 cols)* |
| `TableName.IceCaveOpen` | `icecave_open` | YES | 2 | id, preview_opentime, activity_opentime, icecave_opentime |
| `TableName.IceCaveTitle` | `icecave_title` | YES | 3 | id, icon, name, desc |
| `TableName.Init_Build` | `init_build` | YES | 29 | id, sceneId, pointIndex, buildId, level, initHp, tiles, rotation, landlock, order, dependencyorder, initUpState, unLockLandLockId, change... |
| `TableName.JigsawPuzzle` | `activity_jigsaw` | YES | 3 | id, activity, star_time, star_reward, rank_reward, name, image, condition |
| `TableName.LOMap` | `hero_battle` | YES | 150 | id, name, chapter, trigger, camp, show_reward, show_first_reward, power, army_level, lock |
| `TableName.LW_Buff` | `lw_buff` | YES | 355 | id, type, sub_type, para, buff_time, additive_type, max_level, group, active_effect, activing_effect, ignore_rotate, desc |
| `TableName.LW_Bullet` | `lw_bullet` | YES | 1,036 | id, base_type, damage_type, damage_nature, damage, mvt_type, motion_curve, target_type, is_following, lifetime, bullet_fly_speed, bullet_... |
| `TableName.LW_Count_Stage` | `lw_count_stage` | YES | 5 | id, order, name, desc, title, target, building_condition, stage_type, end_type, end_param3, end_z, a, base_score, scene_assets *(+12 cols)* |
| `TableName.LW_Count_Stage_Group` | `lw_count_stage_group` | YES | 11 | id, max_hp, unit_pt, class, move_speed, unit_radius, face_dir, unit_prefab, dead_vfx, hit_vfx, hp_bar_height, move_anim, engage_anim, con... |
| `TableName.LW_Count_Stage_Group_B` | `lw_count_stage_group_B` | NO | 0 | - |
| `TableName.LW_Count_Stage_Soilder` | `lw_count_stage_soilder` | YES | 8 | id, point, radius, end_line_size, weapon, muzzle_bone, prefab, dead_vfx, march_anim, move_anim, contact_anim, aim_anim, shoot_anim, idle_... |
| `TableName.LW_Count_Stage_Soilder_B` | `lw_count_stage_soilder_B` | NO | 0 | - |
| `TableName.LW_Count_Stage_Trap` | `lw_count_stage_trap` | YES | 56 | id, prefab, bubble_height, hit_vfx, motion_parts, motion_type, motion_param1, motion_param2, motion_param3, sleep_time, max_hp, max_pt, h... |
| `TableName.LW_Count_Stage_Trap_B` | `lw_count_stage_trap_B` | NO | 0 | - |
| `TableName.LW_Hero` | `lw_hero` | YES | 41 | id, type, title_name, first_name, quality, template_id, base_hp, base_patk, base_pdef, base_acc, base_crit, base_load, skills, skills_unl... |
| `TableName.LW_Hero_Effect` | `lw_hero_effect` | YES | 67 | id, hit_effect_direction, death_effect_nomal, death_sound, hit_sound, death_effect_fire, death_effect_elect, death_effect_poison, death_e... |
| `TableName.LW_Hero_Para` | `lw_hero_para` | NO | 0 | - |
| `TableName.LW_Hero_Skill` | `lw_hero_skill` | YES | 968 | id, name, desc, maxLevel, star, group, power, pre_cd, attack_interval, priority, target_type, is_normal_attack, damage_ratio, type *(+23 ... |
| `TableName.LW_Hit_Reaction` | `lw_hit_reaction` | YES | 32 | id, hit_animation, dead_move, hit_shake, hit_zoom, death_effect_nomal, death_effect_nomal_follow, hit_type, para1, death_effect_ground, p... |
| `TableName.LW_Monster_Born` | `lw_monster_born` | YES | 23,481 | id, coord, type, para, monster, buff_item, para2, para3, para4 |
| `TableName.LW_PathPoint` | `lw_path_point` | YES | 275 | id, point_type, para |
| `TableName.LW_PathPoint_B` | `lw_path_point_B` | NO | 0 | - |
| `TableName.LW_Replay_Distance` | `lw_replay_distance` | NO | 0 | - |
| `TableName.LW_Scene` | `lw_scene` | YES | 76 | id, type, asset, scene_size, path_point, final_monster_group, normal_monster, auto_monster_group, start_monster_group, normal_boss, trigg... |
| `TableName.LW_Scene_B` | `lw_scene_B` | NO | 0 | - |
| `TableName.LW_Skill` | `lw_hero_skill` | YES | 968 | id, name, desc, maxLevel, star, group, power, pre_cd, attack_interval, priority, target_type, is_normal_attack, damage_ratio, type *(+23 ... |
| `TableName.LW_Skill_Effect` | `lw_hero_skill_effect` | YES | 141 | id, fire_effect, fire_effect_time, fire_delay, fire_shake, cast_effect, cast_sound, shake_priority, fire_audio, cast_effect_time, shell_e... |
| `TableName.LW_Sound` | `lw_sound` | YES | 27 | id, is_cycle, sound |
| `TableName.LW_Stage` | `lw_stage` | YES | 35 | id, order, name, desc, title, target, type, scene, trigger_item, trigger_plot, block_hp_bonus, stage_icon, scene_tail, win_condition *(+5... |
| `TableName.LW_StageGroup` | `lw_stage_group` | NO | 0 | - |
| `TableName.LW_Stage_B` | `lw_stage_B` | NO | 0 | - |
| `TableName.LW_Stage_Feature` | `lw_stage_feature` | YES | 147 | id, order, name, desc, title, target, type, scene, scene_tail, birth_point, boss_line, boss_area, boss_control, farm_monster *(+13 cols)* |
| `TableName.LW_Template_Property` | `lw_template_property` | NO | 0 | - |
| `TableName.LW_Train_Para` | `lw_train_para` | YES | 39 | id, 说明, val |
| `TableName.LW_Train_Property` | `lw_train_property` | YES | 480 | id, quality, HQLevel, Guard_max, length, speed, lowest_reward, train_route_length, reward1, slot_number, type, world_model, city_model, i... |
| `TableName.LW_Trigger_Item` | `lw_trigger_item` | YES | 1,414 | id, type, para, dead_effect, is_weapon, prefab_path, location, rotation, size, icon, effect, is_soldier, text, desc *(+3 cols)* |
| `TableName.LW_UAV` | `lw_uav` | NO | 0 | - |
| `TableName.LW_UAV_LEVEL` | `lw_uav_level` | NO | 0 | - |
| `TableName.LW_Worker` | `lw_worker` | NO | 0 | - |
| `TableName.LandLock` | `aps_landlock` | YES | 173 | id, bubble, icon, name, Pos, Tiles, Height, pve, order, pre_build, split_group, build_upgrade, pre, reward_item *(+17 cols)* |
| `TableName.LandLock_B` | `aps_landlock_b` | YES | 173 | id, bubble, icon, name, Pos, Tiles, Height, pve, order, pre_build, split_group, build_upgrade, pre, reward_item *(+17 cols)* |
| `TableName.LandLock_Speech` | `C_landlock_speech` | YES | 23 | id, next_id, head, text, time |
| `TableName.Land_Lock_Property` | `land_lock_property` | YES | 167 | id, stand, battle, rotate, battleEffect, collectEffect, unlockEffect, guideStateEffect |
| `TableName.LevelExplore` | `explore_level` | YES | 10 | id, level_order, name, name_value, level_id, hero_num, energy_cost, reward |
| `TableName.LevelUp` | `level_up` | YES | 38 | id, describe, building, APS_resource_item |
| `TableName.LoadingTips` | `loadingTips` | YES | 23 | id, description, level_range, delay_time, rate |
| `TableName.LoveMessageData` | `love_message_date` | YES | 157 | id, next_id, type, time, name, text, bg_pic |
| `TableName.LoveMessageHero` | `love_message_hero` | YES | 33 | id, hero_id, head_pic, name, chat_id, chat_name, chat_pic, unlock_pic, unlock_pic_j, chat_unlock_pic_type, summary_text, summary_content,... |
| `TableName.LoveMessageStory` | `love_message_story` | YES | 1,249 | id, next_id, time, chat_type, chat_person, chat_text, show_time, photo_num, battery, chat_pic |
| `TableName.LwBaseVisitorEvent` | `lw_base_visitor_event` | YES | 480 | id, type, para, name, desc, hero_icon, hero_halfbody, color, model_path, dialog, btn_dialog, bubble_icon, need_building_level |
| `TableName.LwDispatchSetting` | `aps_dispatch_settings` | YES | 6 | id, baselv, max_taskqueue, aid_count, steal_count, refresh_item, refresh_diamond, task1_count, task1_pool, task2_count, task2_pool, task3... |
| `TableName.LwDispatchTask` | `aps_dispatch_tasks` | YES | 96 | id, name, desc, icon, model_name, color, task_star, refresh_pool, world_open, level, is_special, protect_times, conditions, times *(+10 c... |
| `TableName.MailConfig` | `mail_config` | NO | 0 | - |
| `TableName.MailGroup` | `mail_group` | YES | 17 | id, order, type, name, show |
| `TableName.MailShow` | `mail_show` | YES | 37 | id, tab, show_id, sub_type |
| `TableName.MailShowId` | `mail_show_id` | YES | 197 | id, banner, icon_read, icon_unread, superscript, bg_read, bg_unread, icon_win, icon_lose |
| `TableName.Mail_ChannelID` | `Mail_ChannelID` | NO | 0 | - |
| `TableName.Mastery` | `season_mastery` | YES | 399 | id, group, home, type, name, detaildescription, description, icon, needLv, season, world_season, Lv, maxLv, des_value *(+7 cols)* |
| `TableName.MasteryExp` | `masteryExp` | YES | 180 | id, level, Exp |
| `TableName.MasterySkill` | `season_active_skill` | YES | 33 | id, type, needId, goto, use_position, name, icon, description, des_value, CDType, cd_time, CD, time, value1 *(+8 cols)* |
| `TableName.MineCave` | `mine` | YES | 192 | id, level, monster, time, type, name, icon, picture, reward_type, correspond_output, output, plunder, excess_reward_show, excess_reward *... |
| `TableName.Missile` | `missile` | YES | 3 | id, name, des, color, pic, icon, icon_army, sound_idle, talent |
| `TableName.MissileUnlock` | `missile_unlock` | YES | 3 | id, type, target, goods, target_desc, target_para1, daily_quest, daily_quest_desc, daily_quest_reward, daily_target, daily_target_desc, d... |
| `TableName.Mistress` | `mistress` | YES | 30 | id, mistressNPC_id, room_mod, hold_animation, hold_cv, hold_text, head, head_animation, head_cv, head_text, boob, boob_animation, boob_cv... |
| `TableName.MistressBase` | `mistress_base` | YES | 6 | id, name, resource, high_resource, mistressRadarIcon_big, icon, icon_gray, smallIcon, BubblesIcon, unlock_condition, need_goods, need_goo... |
| `TableName.MistressChat` | `mistress_chat` | YES | 772 | id, mistress_id, group_id, trigger_name, trigger_order, triggertype, triggerpara, chat_id, next_chat, chat_type, chat_name, chat_text, ch... |
| `TableName.MistressLove` | `mistress_love` | NO | 0 | - |
| `TableName.MistressLv` | `mistress_lv` | YES | 60 | id, mistress_id, pre_event_id, love_lv, love_lv_name, love_value, mistress_view_id, tap_num, tap_love_value, tap_act, tap_chat, gift_good... |
| `TableName.Monster` | `APS_monster` | YES | 7,882 | id, level, army, size, light_injury_rate, injury_rate, attackRange, expire, deadTime, reward, speed, first_reward, excess_Reward, activit... |
| `TableName.MonsterLock` | `aps_monsterlock` | YES | 120 | id, level, name, pre_build, pre_quest, pre_misson, model, size, pve, need_army, duration, reward_type, reward, split_group |
| `TableName.Museum` | `artifact` | YES | 3 | id, name, description, icon, effect_description, effect_value, show_type, para1, cd_time |
| `TableName.NationConf` | `aps_country` | YES | 107 | id, country, name, flg, order, english_group |
| `TableName.NewHeroes` | `aps_new_heroes` | YES | 1,142 | id, state, season, season_show, season_server, camp, rarity, init_level, init_level_b, max_level, max_rank_level, skill_levelup_item, her... |
| `TableName.NewHeroesB` | `aps_new_heroes_client_B` | YES | 974 | id, state, season, season_show, season_server, camp, rarity, init_level, init_level_b, max_level, max_rank_level, skill_levelup_item, her... |
| `TableName.NewHeroesLevelUp` | `heroes_levelup` | YES | 200 | id, exp, lv_attr_atk1, lv_attr_atk2, lv_attr_atk3, lv_attr_atk4, lv_attr_def1, lv_attr_def2, lv_attr_def3, lv_attr_def4, army_num1, army_... |
| `TableName.NewHeroesLevelUp_B` | `heroes_levelup_B` | NO | 0 | - |
| `TableName.NewHeroesQuality` | `aps_heroes_quality` | YES | 39 | id, consume1, levelup_adv, reset_season, level, type, consume, name, name_UI, color, consume2 |
| `TableName.NewHeroesTag` | `hero_tag` | YES | 26 | id, name, pic, desc |
| `TableName.NightLunarLightCard` | `night_lunarlight_card` | YES | 58 | id, type, random_weight, reward, show_reward, color, order, number, name, desc, pic, goods_pic, frame, card_view_type *(+8 cols)* |
| `TableName.NightLunarLightPack` | `night_lunarnight_pack` | YES | 6 | id, name, unlock_time, deck |
| `TableName.NightLunarLightSorceress` | `night_lunarlight_sorceress` | YES | 60 | id, true_level, favor_level, favor_stage, favor_desc, favor_value, stage_reward, show_reward, unlock_team_slot |
| `TableName.NpcCity` | `pvp_virtual_player` | YES | 150 | id, duration, size, army, res, level, dialog, dialog_goto, dialog_win, dialog_lose, name, head, model, gender *(+7 cols)* |
| `TableName.Office` | `office` | NO | 0 | - |
| `TableName.OfficerList` | `officer_list` | YES | 842 | id, group_id, officer_id, show_rank, show_rate, goods, goods_num, server_time, show_rate_rank1, pity_show_rate, show_rate_guaranteed |
| `TableName.Option_Config` | `optionconfig` | YES | 320 | id, id_group, model, guide_id, picture, dialog_initial, option_dialog, cost_res, reward_icon, dialog_result, dialog_result_type, reward, ... |
| `TableName.Option_ConfigB` | `optionconfig_B` | NO | 0 | - |
| `TableName.Order` | `aps_purchase_order` | YES | 130 | id, condition_type, buildingLv, exp, weight, resource_goods, money, order_reward, icon, time, delete_time, refresh_time, random_value, np... |
| `TableName.OverlordCure` | `overlord_cure` | YES | 3 | id, cure_point, cure_state, cure_state_icon, font_color, spine |
| `TableName.OverlordFile` | `overlord_file` | YES | 6 | id, unlock_cure, unlock_icon, file_title, file_text, file_sign, file_pic, reward |
| `TableName.OverlordMilitaryRank` | `overlord_military_rank` | YES | 201 | id, overlord, rank, stage, name, self_effect, all_effect, nextId, item, icon, font_color, background_icon, preview_color, preview_dialog ... |
| `TableName.OverlordRank` | `overlord_rank` | YES | 251 | id, overlord, stage, node, rank, icon, item, skill_unlock_lv, skill_unlock_star, spine, nextId, power, effect, is_skill_show |
| `TableName.OverlordShow` | `overlord_show` | YES | 6 | id, overlord, rank, stage, default_name, color, spine, low_model, middle_model, high_model, in_sound, loop_sound, background, preview_ico... |
| `TableName.OverlordSkill` | `overlord_skill` | NO | 0 | - |
| `TableName.OverlordTrain` | `overlord_train` | YES | 2,004 | id, overlord, type, level, additional_effect, additional_effect_num, is_critical, exp, add_exp, item, upgrade_color, power, unlock_type, ... |
| `TableName.PVEAtom` | `aps_pve_atom` | YES | 13 | id, type, lv, hp, num, resource_item, energy_cost, item |
| `TableName.PVELevel` | `aps_pve_level` | YES | 152 | id, type, SpawnPos, SpawnRotation, RunPos, minPos, maxPos, Triggers, Scene, DayTime, WeatherType |
| `TableName.PVELevelOld` | `aps_pve_level_old` | YES | 5,052 | id, type, subtype, play_type, Triggers, para1, para2, para7, scene_show, reward, order, name, desc, title *(+64 cols)* |
| `TableName.PVEMonument` | `aps_pve_monument` | YES | 687 | id, level, reEnter, build_condition, auto_move, enter_resource_cost, season, show_reward, use_b |
| `TableName.PVETrigger` | `aps_pve_trigger` | YES | 797 | id, UnclockType, UnclockPara, UnclockPara2, ModelName, Pos, Transform, State, RecoverCd, LinkTriggerId, IsGuidePt, GuideId, SavePos, Pre_... |
| `TableName.PVETriggerGather` | `c_trigger_gather` | YES | 105 | id, type, reward, step, name, soundtype, action, cd, expPerStep, tools, rewardid, slg_type |
| `TableName.PVETriggerOld` | `aps_pve_trigger_old` | YES | 4,730 | id, UnclockType, SideQuest, Pos, UnclockPara, ShowPos, UnclockFog |
| `TableName.PVEZombie` | `aps_pve_zombie` | YES | 156 | id, type, group, ModelName, MoveSpeed, WalkSpeed, Blood, Attack, AttackRadius, AttackDropDistance, MoveRange, DisengageDistance, ChaseRad... |
| `TableName.PVEZombieWave` | `aps_pve_ZombieWave` | YES | 1 | id, level, zombie_id, count, path, spawn_radius, delay, times, interval, isday |
| `TableName.Phonograph` | `radio_station` | YES | 3 | id, sort, buff_type, name, good_id, bgm, duration, cover_image, cover_image_select, record_image, payment_image, story_desc, effect_desc,... |
| `TableName.PlayerCareer` | `player_career` | YES | 50 | id, type, name, description, story, effect, require_item, require_lv, show_type, order, career_tag, icon, image, effect_add *(+1 cols)* |
| `TableName.PlayerCareerEffect` | `career_effect` | YES | 65 | id, type, name, description, icon, order, effect_value, show_type, cd_time, show |
| `TableName.PlayerCareerXml` | `player_career` | YES | 50 | id, type, name, description, story, effect, require_item, require_lv, show_type, order, career_tag, icon, image, effect_add *(+1 cols)* |
| `TableName.PlayerLevel` | `player_level` | YES | 100 | id, level, exp, skillpoint, unlock_reward, box_icon, unlock_career, career_free |
| `TableName.PlotTab` | `plot` | NO | 0 | - |
| `TableName.PopupPackageUI` | `popup_package_ui` | YES | 122 | id, type, name, main_icon, tab_pic, bg_pic, bg_pic2, title_top_color, title_bottom_color, outline_num, desc_text_color, animation, item_p... |
| `TableName.Present` | `gift` | YES | 13 | id, name, good_id, show_type, shop_pic, shop_pic_special, like, gift_exp, panel_type, festival_exp, eff_type, eff_para, show_icon_1, show... |
| `TableName.PresentLevel` | `gift_reward` | YES | 100 | id, level, exp, good |
| `TableName.PresentSP` | `gift_special` | YES | 15 | id, use_good, count, special_text, type, buff, special_desc |
| `TableName.PrologueBridge` | `aps_prologue_bridge` | YES | 3 | id, bridge_id, scale, pos, model, rotation, bubble_noviceboot, preid |
| `TableName.PveActVFX` | `c_vfx_act` | YES | 37 | id, name, atk_eff, behit_eff, death_act, atk_eff_right, atk_eff_sence, atk_eff_fire, fly_eff |
| `TableName.PveBuff` | `aps_pve_buff` | YES | 55 | id, type_buff, para, time, time_type, pic, model, des |
| `TableName.PveChat` | `chat` | YES | 24 | id, chat_group_id, dialogID, view_time, chat_object |
| `TableName.PveHero` | `c_pve_heroes` | YES | 195 | id, atk_type, animations, prefab_low, moveSpeed_stage, move_range_stage, attack_range_stage, attackSpeed_stage, skill_animations_stage, a... |
| `TableName.PveNpc` | `npc_base` | YES | 29 | id, type, name, icon_head, icon_head_S, low_model, high_model, action_group, aps_pve_zombie_id, walk_path, unlock_condition, speed |
| `TableName.PveRolePart` | `aps_pve_part_zombie` | YES | 18 | id, hat, head, cloth, pants, shoes, weapon |
| `TableName.PveVFX` | `c_vfx` | YES | 61 | id, name, type, para1, para2 |
| `TableName.QuestXml` | `c_quest` | YES | 8,828 | id, type, name, name_text, desc, desctype, para1, para2, order, position, list, progressshow, icon, area *(+8 cols)* |
| `TableName.QuestionAndAnswer` | `questionAndAnswer` | YES | 128 | id, type, question, answers, answer, fraction, follow_time, level, reward_true |
| `TableName.Recharge` | `recharge` | YES | 54 | id, type, order, hot, name, icon, para1, tab_icon, para2, image2, onoff |
| `TableName.RecycleItems` | `recycle_items` | YES | 88 | id, server_id, activity_id, recycle_type, rewardgoods_id, num, activity_special_type |
| `TableName.Res_Lack_Tips` | `res_lack_tips` | YES | 1,509 | id, goods, tips, order, name, btn_name, base, pic, level, group, res, para1, monster_level_limit, server *(+11 cols)* |
| `TableName.RescueDog` | `dog_catwoman_stage` | YES | 6 | id, item_id, chapter_name, chapter_desc, idle_spine, random_language, noviceboot, tips, bg, bubble_pos, task_head_spine, clue_loc |
| `TableName.Resource` | `aps_resources` | YES | 26 | id, icon, name, description, order, out_building |
| `TableName.ResourcesCollect` | `resources_collect` | YES | 5 | id, name, desc, icon, unlock_science, gathering, show_gathering, collect_power |
| `TableName.RightsEffect` | `rights_effect` | NO | 0 | - |
| `TableName.RightsEffectLevel` | `rights_effect_level` | NO | 0 | - |
| `TableName.RoamingBossRewardShow` | `roaming_boss_reward_show` | YES | 3 | id, world_season, mons_name, mons_desc, mons_img, mons_id_list, mons_reward_kill, mons_reward_rally, boss_name, boss_desc, boss_img, boss... |
| `TableName.Robot` | `robot` | YES | 7 | id, unlockType, order, name, icon1, icon2, sculpture1, sculpture2, cv, cv_text, cv_job_done, unlockParam, unlockTime, gift *(+6 cols)* |
| `TableName.Rocket_Order` | `rocket_order` | YES | 152 | id, type, product_id, group, state, condition_type, building_condition, product_num, order_reward, ext_order_reward, temp_order_reward, r... |
| `TableName.Role` | `role` | NO | 0 | - |
| `TableName.SU_C_Event` | `c_event` | YES | 102 | id, level, pre_type, pre_para1, check_immediately, do_noviceboot, noviceboot_drive, do_type, do_para1, recycle, do_para2, do_para3 |
| `TableName.SU_C_Feed` | `c_feed` | YES | 25 | id, hunger, thirsty, health, type, restorehealth, restorehealthdes, lootid, pee |
| `TableName.SU_FunctionShow` | `function_view` | YES | 38 | id, lock_mode, lock_condition, lock_guarantee, world_btn_show, slg_btn_show, rpg_btn_show, level_btn_show, boss_btn_show, id_tips |
| `TableName.SU_Guide_Pic` | `c_guide_pic` | YES | 6 | id, name, des, dub, noviceboot |
| `TableName.SU_HeroesLevelUp` | `c_heroes_levelup` | YES | 100 | id, legend_atk, epic_atk, rare_atk, normal_atk, lord_atk, legend_def, epic_def, rare_def, normal_def, lord_def, legend_hp, epic_hp, rare_... |
| `TableName.SU_HeroesRank` | `c_heroes_rank` | YES | 46 | id, rank_atk, rank_def, rank_hp |
| `TableName.SU_ItemSourceTip` | `c_item_source_tip` | YES | 50 | id, levelId, buildId |
| `TableName.SU_MainCityArea` | `main_city_area` | YES | 89 | id, name, entrance_name, all_tiles_rect, pve_level_id, contact_area, standPos, lock_type, area_type, order, rewardIds, clientShowSmallPeo... |
| `TableName.SU_PveSKillAction` | `c_pveSkillAction` | YES | 24 | id, type, speed, action, actionEffect, attacktype, para1, para2, damage, para3 |
| `TableName.SU_PveSkill` | `c_pveSkill` | YES | 10 | id, skillAction, range |
| `TableName.SU_PveType` | `pve_type` | YES | 102 | id, type, name, order, resettype, level, cost, requirelevel, text, loading_tips, icon, pic, tag, quest *(+10 cols)* |
| `TableName.SU_PveWorld` | `pve_world` | YES | 60 | id, type, level, diffculty, recommend_power, pve_id, name, pic, model, desc, reward, reward_num, reward_time, size *(+1 cols)* |
| `TableName.SU_SLG_Camera` | `c_camera_unlock` | YES | 2 | id, zoom, offset_zoom, rpg_range, range, slg_camera_pos_type, camera_pos, level, build_level |
| `TableName.SU_SLG_Camera_L` | `c_camera_unlock_l` | YES | 2 | id, zoom, offset_zoom, rpg_range, range, slg_camera_pos_type, camera_pos, level, build_level |
| `TableName.SantaAnimal` | `activity_santa_animals` | YES | 4 | id, goods_id, res_avatar, res_bg, res_bg_gray, buff_short_desc, ani_desc, popup_desc, anticheat_animal_buff, activate_time, num_buff |
| `TableName.SantaDataGroup` | `activity_santa_data_group` | YES | 6 | id, stage_data_id, loot |
| `TableName.SantaStageConfig` | `activity_santa_stage_config` | YES | 2 | id, activity_id, afk_group, reward_group, upgrade_group, anticheat_group, stage_group_sort, finish_check, base_scene, barrel_scene, defau... |
| `TableName.SantaStageData` | `activity_santa_stage_data` | YES | 16 | id, para1, para2, length |
| `TableName.SantaStageReward` | `activity_santa_reward` | YES | 31 | id, group_id, level, distance, reward_token, reward_other |
| `TableName.SantaStageUpgrade` | `activity_santa_upgrade` | YES | 20 | id, group_id, level, power_add, power_consume, speed_add, speed_consume, shield_add, shield_consume, upgrade_limit |
| `TableName.Science` | `science2` | NO | 0 | - |
| `TableName.ScienceNew` | `APS_science` | YES | 4,483 | id, science_id, level, max_level, tab, name, description, icon, color, position, science_condition, building_condition, effect, research_... |
| `TableName.ScienceShow` | `scienceShow` | NO | 0 | - |
| `TableName.ScienceTab` | `scienceTab` | NO | 0 | - |
| `TableName.Score` | `score` | YES | 579 | id, type, name, value, points, season_type, group, tips, gotoType, margeType, margeGroup, pic, gotoPara, goods *(+1 cols)* |
| `TableName.ScoreList` | `score_list` | YES | 2 | id, score |
| `TableName.SeasonActivityPanel` | `season_activity_panel` | YES | 60 | id, title_group, season_panel_group, world_season, type, is_main, panel_id, order, size_type, preview_pic, pic_type, pic, spine, show_tim... |
| `TableName.SeasonConfig` | `season_config` | YES | 11 | id, para1 |
| `TableName.SeasonDialog` | `season_dialog` | YES | 62 | id, season_dialog |
| `TableName.SeasonGroup` | `aps_season_group` | YES | 1,351 | id, season, seasonPlayType, seasonPlayTypeclient, server, season_show, season_name, season_icon, seasoncount, seasonsend, nextseason, sea... |
| `TableName.SeasonInfluence` | `season_influence` | YES | 37 | id, influence, influence_b, influence_new, name, pic, star, box, resistance, reward, effect |
| `TableName.SeasonIntro` | `d_season_intro` | YES | 1 | id, season, interface |
| `TableName.SeasonObject` | `season_object` | YES | 14 | id, type, skill, value1, value2, value3, prefab, area, name, description, des_value, extra_des, value4 |
| `TableName.SeasonReviewRule` | `season_review` | YES | 12 | id, season, event_name, event_desc, pic |
| `TableName.SeasonReward` | `flag_effect` | YES | 9 | id, world_season, order, flag_effect_bg, flag_effect_title, flag_effect_effect, flag_effect_pic, flag_effect_season, effect_title, effect... |
| `TableName.SeasonTroopLine` | `season_troopline` | YES | 5 | id, TroopLine, TroopLineDrag, Green, White, Red, Blue, Purple, Yellow |
| `TableName.SeasonWeek` | `season_week` | YES | 8 | id, season, season_begin_time, name, season_week_exchange, show, icon |
| `TableName.ServerIp` | `server_ip` | YES | 11 | id, severid_range, direct, aws, gcp, ip_v6, direct_ip, aws_ip_1, gcp_ip, aws_ip_2, ws, wss, ws_1, wss_1 |
| `TableName.ServerPos` | `serverpos` | NO | 0 | - |
| `TableName.Server_Badge` | `server_badge` | YES | 6 | id, name, description, icon, quality, order, icon_new, quality_new, condition, show_star, new_star, hide_on_legacy_logic, show_reward, ti... |
| `TableName.Server_Capital_Reward` | `server_capital_reward` | YES | 1 | id, season, score_reward, reward_value, kill_score_inbuilding, kill_score, dead_score, kill_score_other, dead_score_other, atk_plant, atk... |
| `TableName.Servers_Wonder_War` | `servers_wonder_war` | YES | 235 | id, server_ids, need_level, open_week, type, open_time, continue_time, show_day, cycle, score, war, duration, win_reward, win_reward_diam... |
| `TableName.ShelterEmoji` | `shelter_emoji` | YES | 22 | id, name, free, sound, icon, animation, zoom, offset, para, good, isReverse |
| `TableName.Sidebar` | `c_sidebar` | YES | 12 | id, name, icon, type, goto |
| `TableName.SidebarType` | `c_sidebar_type` | YES | 5 | id, type_name, type_icon, type_order |
| `TableName.SiegeNPC` | `siegeNPC` | NO | 0 | - |
| `TableName.SingleMapPosition` | `aps_singlemap_position` | YES | 223 | id, UnitType, Pos, Wave, UnitID |
| `TableName.SkillTab` | `skill` | YES | 2,054 | id, skill_source_group, type, level, object, object_num, scale, effect, effect_num, name, des, icon, effect_des, effect_num_des *(+48 cols)* |
| `TableName.SnowMan` | `ice_snowman` | YES | 228 | id, level, exp, name, prefab, activity_id, level_reward, type, stage, level_effect, milestone_unlock, skin_goods |
| `TableName.SpeedUpConfig` | `speedup_config` | YES | 7 | id, speedup_goods, max, min |
| `TableName.StateSkill` | `state_skill` | YES | 1 | id, type, name, desc, rule, color, official, pre_time, launch_time, during_time, prefab, punish_time, cd_time, effect_scope *(+2 cols)* |
| `TableName.State_Ruler_Intro` | `state_ruler_intro` | YES | 11 | id, level, exp, name, level_reward, buff_level_1, buff_level_2 |
| `TableName.StatusTab` | `status` | YES | 263 | id, type, type2, time, effect, effect_num, group, priority, name, description, subgroup, overlap, desc_para, icon *(+9 cols)* |
| `TableName.StoryMap` | `push_map` | YES | 6 | id, level, level_num, reward, name |
| `TableName.SysRedPacket` | `sys_red_packet` | YES | 203 | id, type, building, level, desc, chat, num, res_type, gold, icon, item, time, chat_pic, main_top *(+10 cols)* |
| `TableName.Talent` | `APS_talent` | YES | 900 | id, talent_id, max_level, effect, level, type, name, desc, pos_x, pos_y, prerequisite, icon |
| `TableName.TalentHome` | `talentHome` | NO | 0 | - |
| `TableName.TalentShading` | `DesertTalent_Shading` | NO | 0 | - |
| `TableName.TalentType` | `talent_type` | YES | 4 | id, name, order |
| `TableName.Talent_New` | `talent` | YES | 35 | id, type, group, order, lv, name, effect_value, description, icon, resource, color, special_rate |
| `TableName.Territory` | `territory` | NO | 0 | - |
| `TableName.TerritoryEffect` | `territory_effect` | NO | 0 | - |
| `TableName.TimeBridge` | `time_bridge` | YES | 30 | id, level, level_id, buildlv, name, name_value, description, quality, reward |
| `TableName.TradePost` | `trade_post` | YES | 40 | id, season, world_season, level, group, model, banner, name, desc, icon, xy, size, plus_size, black_land_size *(+3 cols)* |
| `TableName.TradePostOpen` | `trade_post_open` | YES | 4 | id, preview_opentime, activity_opentime, group, tradepost_opentime, tradepost_opentime_server, tradepost_opentime_cross, first_reward_sho... |
| `TableName.TradePostShopItem` | `trade_post_shopitem` | YES | 141 | id, goods_id, goods_num, sell_quantity, price, is_for_owner, is_for_member, owner_discount, alliance_discount, shop_type |
| `TableName.TradePostTitle` | `trade_title` | YES | 9 | id, level, world_season, icon, name, desc |
| `TableName.Trends` | `trends` | YES | 23 | id, name, description, description_value, pic, show_time, order, season, title_icon, type, phase, parent_id |
| `TableName.TrendsFunction` | `trends_function` | YES | 41 | id, name, description, description_value, pic |
| `TableName.TroopAction` | `troop_action` | YES | 13 | id, type, dialogID, rate, stay_time, show_time |
| `TableName.UavDialogue` | `aps_uav_dialogue` | YES | 8 | id, building, dialog, type, dialog_cd, public_cd, order |
| `TableName.UnlockBtn` | `interfaceSetting` | YES | 0 | - |
| `TableName.VideoHero` | `video_hero` | YES | 1 | id, hero_id, video_id |
| `TableName.Vip` | `vip` | YES | 20 | id, point, icon, reward1, reward2, reward2_new, display, gift_pic, freebie_banner, effect, need_hero |
| `TableName.VipDetails` | `vipdetails` | NO | 0 | - |
| `TableName.VipStoreUnlock` | `vip_store_unlock` | NO | 0 | - |
| `TableName.VipTemp` | `vip_temp` | YES | 17 | id, point, icon, reward1, reward2, reward2_new, display, effect |
| `TableName.VirtualRoad` | `aps_sandRoad` | YES | 86 | id, type, model, rotate, Pos, size |
| `TableName.VisitorWelcome` | `lw_base_visitor_welcome` | YES | 30 | id, trigger, type, name, desc, hero_icon, model_path, dialog, dialog_bubble_toward, action, dialog_to_gate, unlock_building, relativePosE... |
| `TableName.VolcanoArea` | `volcano_area` | YES | 6 | id, scope, interval_random, resource_id, interval_start, interval_start_time, interval_time, interval_number, interval_delay, interval_max |
| `TableName.VolcanoBroadcast` | `volcano_broadcast` | YES | 10 | id, type, para, score, scrolling_announcement_id, icon, bg |
| `TableName.VolcanoBuilding` | `volcano_building` | YES | 11 | id, size, coordinates, area_id, name, des, alliance_point, circle_person_point |
| `TableName.VolcanoLand` | `volcano_land` | YES | 10 | id, coordinates, res_id |
| `TableName.VolcanoMatch` | `volcano_match` | YES | 41 | id, server, server_group, open_time, battle_start_time, battle_duration, trailer_time, draw_time, public_time, communication_time, invita... |
| `TableName.VolcanoPara` | `volcano_para` | YES | 41 | id, 备注, para |
| `TableName.VolcanoRes` | `volcano_res` | YES | 9 | id, res_type, type, order, size, time_points, complete_points, name, desc, pic, lod_none, lod_mine, lod_ally, lod_camp *(+6 cols)* |
| `TableName.VolcanoReward` | `volcano_reward` | YES | 6 | id, allocate_reward, atk_reward_number, atk_reward_add, def_reward_number, def_reward_add, atk_victory_reward, atk_fail_reward, def_victo... |
| `TableName.Warning` | `aps_warning` | YES | 15 | id, type, condition, Forbidden, land_cd, warn_cd, icon, icon_pre, order, describe, para1, world |
| `TableName.WonderGift` | `wonder_gift` | YES | 24 | id, name, type, reward, num, season, worth, icon |
| `TableName.WorldBuilding` | `building_world` | NO | 0 | - |
| `TableName.WorldCity` | `worldcity` | YES | 90 | id, location, level, size, server_type, eden_city_type, belong_eden_camp, monster_id, monster_id_b, monster_num, buff, first_reward, show... |
| `TableName.WorldLod` | `world_scene` | YES | 221 | id, type, path, lod, isMain, Fading |
| `TableName.WorldPacketReward` | `world_packet_reward` | YES | 2 | id, name, type, rewardId, box_reward, expire, pickTimes, model, panel_banner |
| `TableName.WorldQuest` | `world_quest` | YES | 168 | id, type, activity, desc, para1, para2, order |
| `TableName.WorldSeason` | `world_season` | NO | 0 | - |
| `TableName.XiaoRenRank` | `xiaoren_rank` | YES | 26 | id, level, stage, cost_common, cost_self |
