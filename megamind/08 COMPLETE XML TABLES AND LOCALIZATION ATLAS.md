# Volume 08: Complete Untruncated XML Game Tables (189,844 Rows) & English Localization Atlas

> **Generated:** `2026-11-23 11:03:26 UTC` | **Sources:** `megamind/raw/xml_tables/` + `megamind/raw/xml_tables_manifest.json` + `megamind/raw/localization_en.json`

## 1. Zero-Truncation Data Dump Summary

| Dataset | Verified Count | Storage Location |
|---|---:|---|
| Complete XML Tables Dumped (100% of rows, zero caps) | **354** tables | `megamind/raw/xml_tables/*.json` |
| Exact Total XML Rows Preserved | **189,844** rows | Compact columnar-indexed JSON |
| `LuaDatatable.*` Runtime Modules Dumped | **355** files | `megamind/raw/xml_tables/luadatatable_*.json` |
| Combined Raw Table Data Size | **55.59 MB** | Full row-by-row fidelity |
| English Localization Dictionary (`Localization:GetString`) | **8,436** strings | `megamind/raw/localization_en.json` |

### How to Query Any Table or Localization String Instantly
```powershell
python megamind/megamind_query.py xml daily_quest
python megamind/megamind_query.py xml goods Speed
python megamind/megamind_query.py xml aps_new_heroes Katrina
python megamind/megamind_query.py loc "Like {0} different Posts"
python megamind/megamind_query.py loc 320078
```

## 2. Largest Game Data Tables (Top 30 by Row Count)

| XML Table | `TableName` Alias(es) | Exact Rows | Columns | JSON Size |
|---|---|---:|---:|---:|
| `barrel_monster` | `TableName.Barrel_Monster` | **31,899** | 3 | 1900.4 KB |
| `lw_monster_born` | `TableName.LW_Monster_Born` | **23,481** | 9 | 2729.2 KB |
| `hero_camp_intensify` | `TableName.HeroIntensify` | **10,521** | 10 | 905.0 KB |
| `c_quest` | `TableName.QuestXml` | **8,828** | 22 | 1172.6 KB |
| `APS_monster` | `TableName.Monster` | **7,882** | 65 | 3268.7 KB |
| `army` | `TableName.Army` | **7,578** | 14 | 1945.5 KB |
| `army_b` | `TableName.Army_B` | **6,858** | 14 | 1754.6 KB |
| `army_c` | `TableName.Army_C` | **6,858** | 14 | 1754.7 KB |
| `aps_pve_level_old` | `TableName.PVELevelOld` | **5,052** | 78 | 2546.9 KB |
| `aps_pve_trigger_old` | `TableName.PVETriggerOld` | **4,730** | 7 | 779.1 KB |
| `APS_science` | `TableName.ScienceNew` | **4,483** | 22 | 1102.4 KB |
| `battlepass` | `TableName.BattlePass` | **4,201** | 10 | 288.0 KB |
| `building` | `TableName.Building` | **4,089** | 75 | 2369.4 KB |
| `detect_event` | `TableName.DetectEvent` | **3,275** | 21 | 597.4 KB |
| `aps_shop` | `TableName.APS_shop` | **3,056** | 36 | 499.4 KB |
| `ds_equip_attribute` | `TableName.EquipAttribute` | **2,924** | 4 | 169.6 KB |
| `activity_dig_para` | `TableName.DigActivityPara` | **2,125** | 7 | 264.1 KB |
| `skill` | `TableName.SkillTab` | **2,054** | 62 | 1177.1 KB |
| `overlord_train` | `TableName.OverlordTrain` | **2,004** | 15 | 208.3 KB |
| `car_microchip_attribute` | `TableName.CarMicrochipAttribute` | **1,968** | 9 | 155.6 KB |
| `car_microchip_box` | `TableName.CarMicrochipBox` | **1,583** | 5 | 82.9 KB |
| `res_lack_tips` | `TableName.Res_Lack_Tips` | **1,509** | 25 | 217.3 KB |
| `fake_player` | `TableName.FakePlayer` | **1,430** | 6 | 60.3 KB |
| `lw_trigger_item` | `TableName.LW_Trigger_Item` | **1,414** | 17 | 408.2 KB |
| `aps_season_group` | `TableName.SeasonGroup` | **1,351** | 40 | 1356.3 KB |
| `love_message_story` | `TableName.LoveMessageStory` | **1,249** | 10 | 96.4 KB |
| `noviceboot` | `TableName.Guide` | **1,246** | 30 | 299.1 KB |
| `aps_buildzone` | `TableName.BuildZone` | **1,215** | 3 | 31.8 KB |
| `hero_camp_random` | `TableName.HeroIntensifyRandomEffect` | **1,212** | 6 | 94.0 KB |
| `aps_new_heroes` | `TableName.NewHeroes` | **1,142** | 103 | 1018.4 KB |

## 3. Complete Index of All 354 Full-Row XML Tables (`megamind/raw/xml_tables/`)

| XML Table | `TableName` Key(s) | Exact Rows | Size | Columns |
|---|---|---:|---:|---|
| `APS_arms` | `TableName.ArmsTab` | 393 | 186.4 KB | id, name, description, quality, max_train, resource_need, time, treat_time, treat_resource, unlock_train_build, unlock_upg... |
| `APS_global` | `TableName.Global` | 2 | 0.2 KB | id, k1, k2 |
| `APS_hero_color` | `TableName.HeroColor` | 6 | 0.6 KB | id, star_limit_level_1, star_limit_level_2, star_limit_level_3, star_limit_level_4, star_limit_level_5, star_up_1, star_up... |
| `APS_monster` | `TableName.Monster` | 7,882 | 3268.7 KB | id, level, army, size, light_injury_rate, injury_rate, attackRange, expire, deadTime, reward, speed, first_reward *(+53)* |
| `APS_push` | `TableName.APS_PUSH` | 62 | 6.1 KB | id, push_unlock, push_type, tag, type_value, dialogId, building, param_count, times, player_mark, push_time, push_tab *(+2)* |
| `APS_science` | `TableName.ScienceNew` | 4,483 | 1102.4 KB | id, science_id, level, max_level, tab, name, description, icon, color, position, science_condition, building_condition *(+... |
| `APS_talent` | `TableName.Talent` | 900 | 127.5 KB | id, talent_id, max_level, effect, level, type, name, desc, pos_x, pos_y, prerequisite, icon |
| `AcitivitySeven_New` | `TableName.ActSeven` | 620 | 44.3 KB | id, type1, type1_text, type2, type2_text, task |
| `Activity_Reward_Show` | `TableName.ActivityRewardShow` | 4 | 0.3 KB | id, activity, excess_reward_1, special_monster |
| `C_landlock_speech` | `TableName.LandLock_Speech` | 23 | 1.3 KB | id, next_id, head, text, time |
| `DayAct` | `TableName.DayAct` | 87 | 11.4 KB | id, type1, type1_text, type2, type2_text, title, dialog, daily_bg, reward_show |
| `activity_barter` | `TableName.ActivityBarter` | 276 | 25.3 KB | id, activity_id, item1, item2, times, not_reset, vip, is_decoration_gift, gift_goods, gift_require, time_type, start_time ... |
| `activity_boxopen` | `TableName.ActivityBoxOpen` | 4 | 0.9 KB | id, activity, cost_item, cost_1, cost_1_free, cost_5, draw_max_daily, box_num, unlock_goods, auto_rank, rank_reward, draw_... |
| `activity_boxopen_para` | `TableName.ActivityBoxOpenPara` | 101 | 9.7 KB | id, boxopen_id, type, goods, rate, guarantee_activity, order, reward_buy_time, reward_hold_time, reward_icon, reward_name,... |
| `activity_cake_team_cake` | `TableName.ActivityCakeTeamCake` | 15 | 0.8 KB | id, cake_group_id, cake_level, cake_progress_value, cake_reward |
| `activity_cake_team_event` | `TableName.ActivityCakeTeamEvent` | 11 | 1.3 KB | id, event_group_id, event_type_id, point_num, reward_id, event_cd, event_name, event_tips, event_para1, event_para2 |
| `activity_cake_team_main` | `TableName.ActivityCakeTeamMain` | 1 | 0.6 KB | id, act_id, need_goods_id, point_goods_id, spin_group_id, spin_times, event_group_id, event_rate, cake_group_id, team_lock... |
| `activity_cake_team_spin` | `TableName.ActivityCakeTeamSpin` | 10 | 0.7 KB | id, spin_group_id, goods_id, point_num, rate, guarantee_rule, probability |
| `activity_cyclebox` | `TableName.ActivityCyclebox` | 6 | 6.6 KB | id, activity_id, activity_relation, box_id, send_cost_id, box_score, box_score1, open_maxnum, point_item, initial_box, box... |
| `activity_cyclebox_para` | `TableName.ActivityCycleboxPara` | 162 | 9.3 KB | id, box_id, order, reward_group, goods, rate, show_rate, guarantee |
| `activity_dig` | `TableName.DigActivityDig` | 3 | 2.6 KB | id, activity, cost_goods, diamond_buy, activity_relation, level_big, goods_rare_small, small_recommend, goods_rare_big, bi... |
| `activity_dig_para` | `TableName.DigActivityPara` | 2,125 | 264.1 KB | id, dig_id, level, goods_normal, rate, rate_rare, guarantee |
| `activity_flip` | `TableName.ActivityFlip` | 5 | 3.8 KB | id, activity, cost_goods, first_gold, gold_goods, gold_rate, gold_range, purple_goods, purple_rate, purple_range, blue_goo... |
| `activity_item_drop` | `TableName.ActivityItemDrop` | 86 | 13.4 KB | id, activity, type, good, limit, para, para1, para2, reward, icon, name, desc *(+2)* |
| `activity_jigsaw` | `TableName.JigsawPuzzle` | 3 | 0.6 KB | id, activity, star_time, star_reward, rank_reward, name, image, condition |
| `activity_monster` | `TableName.ActivityMonster` | 19 | 4.8 KB | id, difficulty_des, monster, description, monster_des, icon, difficulty_title, icon_detail, monster_power, call_consume, s... |
| `activity_monsterboss` | `TableName.ActivityMonsterBoss` | 9 | 1.2 KB | id, difficulty, monster_id, condition, reward_alli_show, reward_solo_show, time |
| `activity_panel` | `TableName.ActivityPanel` | 773 | 205.8 KB | id, type, age_restriction, name, order, desc_info, story, needMainCityLevel, list_icon, Advertise_pic, activity_pic, show_... |
| `activity_puzzle_monster` | `TableName.ActivityPuzzleMonster` | 3 | 1.0 KB | id, name, color, time, monster_id, reward_show, reward_detail, ranking_reward, partake_reward, call_reward, consume, unlock |
| `activity_santa_animals` | `TableName.SantaAnimal` | 4 | 1.6 KB | id, goods_id, res_avatar, res_bg, res_bg_gray, buff_short_desc, ani_desc, popup_desc, anticheat_animal_buff, activate_time... |
| `activity_santa_data_group` | `TableName.SantaDataGroup` | 6 | 0.4 KB | id, stage_data_id, loot |
| `activity_santa_reward` | `TableName.SantaStageReward` | 31 | 1.8 KB | id, group_id, level, distance, reward_token, reward_other |
| `activity_santa_stage_config` | `TableName.SantaStageConfig` | 2 | 16.7 KB | id, activity_id, afk_group, reward_group, upgrade_group, anticheat_group, stage_group_sort, finish_check, base_scene, barr... |
| `activity_santa_stage_data` | `TableName.SantaStageData` | 16 | 10.2 KB | id, para1, para2, length |
| `activity_santa_upgrade` | `TableName.SantaStageUpgrade` | 20 | 1.4 KB | id, group_id, level, power_add, power_consume, speed_add, speed_consume, shield_add, shield_consume, upgrade_limit |
| `activity_showlist` | `TableName.ActivityOverview` | 8 | 1.0 KB | id, type, unlock, name, reward_show, image, unlock_image, order |
| `activity_spin` | `SlgTableName.ActivityTreasureBox` | 1 | 0.6 KB | id, activity, cost_item, spin_cost, daily_free_time, spin_cost_5, draw_max_daily, box_num, unlock_goods, auto_rank, rank_r... |
| `activity_spin_para` | `SlgTableName.ActivityTreasureBoxPara` | 26 | 4.6 KB | id, spin_id, pool_id, goods, spin_item, item_priority, spin_item_icon, spin_bg_icon, reward_icon, reward_name, rate, order... |
| `activity_tips` | `TableName.ActivityTip` | 1 | 0.4 KB | id, activity_type, type, priority, condition, iconlist, topiclist, showonce |
| `activity_treasure_alliance` | `TableName.ActivityTreasureAlliance` | 20 | 3.4 KB | id, activity, treasure_id, picture, collection, reward |
| `activity_treasure_hunt` | `TableName.ActivityTreasureHunt` | 160 | 26.1 KB | id, level, activity, layout_id, layout_rate, reward |
| `activity_treasure_hunt_para` | `TableName.ActivityTreasureHuntPara` | 116 | 7.1 KB | id, map_width, map_height, treasure_layout |
| `activity_treasure_para` | `TableName.ActivityTreasurePara` | 97 | 20.5 KB | id, type, horizontal, vertical, picture, shape_pic, rotate, group, bomb, reward, rate |
| `adaptive_box` | `TableName.Adaptive_Box` | 250 | 10.1 KB | id, group, level, type, base_itemid, base_num |
| `affect_num` | `TableName.Affect_Num` | 243 | 8.2 KB | id, des, negative, num_type |
| `alScience` | `TableName.AlScience` | 150 | 15.9 KB | id, science_id, science_lv, max_lv, value, time, resource, donate, donate_price_start, donate_price_add, donate_price_max,... |
| `alScienceTab` | `TableName.AlScienceTab` | 51 | 8.2 KB | id, name, description, description_tip, icon, max_lv, position, relation, info, tab, schedule, contribution |
| `alliance_boss_property` | `xmlValue.alliance_boss_property` | 16 | 3.6 KB | id, difficulty, monsterId, name, alliance_reward, reward, alliance_bonus, alliance_reward_new_show, reward_new_show, unloc... |
| `alliance_effect` | `TableName.AlEffect` | 6 | 0.7 KB | id, name, icon, description, description_value, description_type, order |
| `alliance_function` | `TableName.AllianceFunction` | 2 | 0.2 KB | id, lock_mode, id_tips, lock_condition |
| `alliance_gift` | `TableName.AllianceGift` | 400 | 84.3 KB | id, level, exp, type, subtype, exceed_time, rewardId, scale, rate_show |
| `alliance_gift_group` | `TableName.AllianceGiftGroup` | 67 | 9.5 KB | id, type, name, desc, color, icon, sender, title, each_exp, giftshow, othershow, key_exp *(+2)* |
| `alliance_haggle` | `TableName.AllianceHaggle` | 71 | 24.7 KB | id, unlock_level, members_num, group, rate, limit_servers, reward, haggle_type, price, lowest_price, min_number, haggle_mi... |
| `alliance_log` | `TableName.AllianceLog` | 33 | 1.9 KB | id, type, scale, icon, path |
| `alliance_res_build` | `TableName.AllianceResBuild, TableNa...` | 37 | 8.9 KB | id, name, desc, model, icon, res_size, offter_range, level, res_durable, res_base_durable, res_num, collect_type *(+22)* |
| `alliance_resource` | `TableName.AllianceResource` | 24 | 5.7 KB | id, icon, name, description, city_level, alliance_gold_num, alliance_gold_capacity, alliance_gold_gathering, alliance_meta... |
| `alliance_skill` | `TableName.AllianceSkill` | 1 | 0.6 KB | id, type, name, desc, rule, color, pre_time, during_time, prefab, punish_time, cd_time, effect_scope *(+12)* |
| `alliance_task` | `TableName.AllianceTask` | 16 | 2.0 KB | id, unlock_time, name, description, type, para, times, reward, quest_pic, jump, record, para2 |
| `aps_base_expansion` | `TableName.BaseExpansion` | 42 | 1.5 KB | id, x, y, range, is_only_road, treetype |
| `aps_build_queue` | `TableName.BuildQueue` | 6 | 0.3 KB | id, name, uav_describe, gift |
| `aps_buildzone` | `TableName.BuildZone` | 1,215 | 31.8 KB | id, pos, zone_type |
| `aps_city_buff` | `TableName.CityManage` | 8 | 0.9 KB | id, name1, name2, name3, desc, icon, type, type2, group, status, formation_status |
| `aps_collect_resource` | `TableName.CollectResource` | 3 | 0.3 KB | id, resourceType, para, diffPoint, model |
| `aps_country` | `TableName.NationConf` | 107 | 3.9 KB | id, country, name, flg, order, english_group |
| `aps_dispatch_settings` | `TableName.LwDispatchSetting` | 6 | 3.9 KB | id, baselv, max_taskqueue, aid_count, steal_count, refresh_item, refresh_diamond, task1_count, task1_pool, task2_count, ta... |
| `aps_dispatch_tasks` | `TableName.LwDispatchTask` | 96 | 29.4 KB | id, name, desc, icon, model_name, color, task_star, refresh_pool, world_open, level, is_special, protect_times *(+12)* |
| `aps_factory` | `TableName.Factory` | 45 | 8.7 KB | id, name, build_type, unlock_type, unlock_condition, input_resource_goods, time, get_resource_goods, icon, order, group, e... |
| `aps_farming` | `TableName.Farming` | 12 | 3.5 KB | id, product_name, build_id, order, unlock_order, group, unlock_type, unlock_condition, produce_time, get_resource_goods, i... |
| `aps_gather_resource` | `TableName.GatherResource` | 121 | 17.0 KB | id, resource_type, param, level, reserve, size, expire, gathering, show_gathering, collect_power, name, pic *(+4)* |
| `aps_heroes_quality` | `TableName.NewHeroesQuality` | 39 | 3.3 KB | id, consume1, levelup_adv, reset_season, level, type, consume, name, name_UI, color, consume2 |
| `aps_heroes_rank` | `TableName.HeroMilitaryRank` | 52 | 12.5 KB | id, level, stage, cost_medal, stage_show, name, icon, cost_coin, skill, require, atk, def *(+1)* |
| `aps_heroes_rankLv` | `TableName.HeroMilitaryRankLv` | 8 | 0.9 KB | id, level, skillLv, name, icon, atk, def, troop |
| `aps_landlock` | `TableName.LandLock` | 173 | 56.2 KB | id, bubble, icon, name, Pos, Tiles, Height, pve, order, pre_build, split_group, build_upgrade *(+19)* |
| `aps_landlock_b` | `TableName.LandLock_B` | 173 | 56.2 KB | id, bubble, icon, name, Pos, Tiles, Height, pve, order, pre_build, split_group, build_upgrade *(+19)* |
| `aps_monsterlock` | `TableName.MonsterLock` | 120 | 13.1 KB | id, level, name, pre_build, pre_quest, pre_misson, model, size, pve, need_army, duration, reward_type *(+2)* |
| `aps_new_heroes` | `TableName.NewHeroes` | 1,142 | 1018.4 KB | id, state, season, season_show, season_server, camp, rarity, init_level, init_level_b, max_level, max_rank_level, skill_le... |
| `aps_new_heroes_client_B` | `TableName.NewHeroesB` | 974 | 780.8 KB | id, state, season, season_show, season_server, camp, rarity, init_level, init_level_b, max_level, max_rank_level, skill_le... |
| `aps_new_heros_skin` | `TableName.Hero_Skin` | 75 | 17.5 KB | id, hero_id, sorting, hero_spine, skin_icon, skin_name, default_skin, hero_icon, round_hero_icon, hero_body, hero_halfbody... |
| `aps_new_heros_skin_shop` | `TableName.Hero_Skin_Shop` | 34 | 3.2 KB | id, type, type_para, goods, price_type, price_type_para, show_type, show_service, time_type, start_time, duration, show_ti... |
| `aps_prologue_bridge` | `TableName.PrologueBridge` | 3 | 0.4 KB | id, bridge_id, scale, pos, model, rotation, bubble_noviceboot, preid |
| `aps_purchase_order` | `TableName.Order` | 130 | 20.9 KB | id, condition_type, buildingLv, exp, weight, resource_goods, money, order_reward, icon, time, delete_time, refresh_time *(... |
| `aps_pve_ZombieWave` | `TableName.PVEZombieWave` | 1 | 0.3 KB | id, level, zombie_id, count, path, spawn_radius, delay, times, interval, isday |
| `aps_pve_atom` | `TableName.PVEAtom` | 13 | 0.8 KB | id, type, lv, hp, num, resource_item, energy_cost, item |
| `aps_pve_battlebuff` | `TableName.BattleBuff` | 71 | 5.1 KB | id, type, buffId, icon, LocalType, group, not_choose, show_group, timetype, time |
| `aps_pve_buff` | `TableName.PveBuff` | 55 | 3.6 KB | id, type_buff, para, time, time_type, pic, model, des |
| `aps_pve_level` | `TableName.PVELevel` | 152 | 20.1 KB | id, type, SpawnPos, SpawnRotation, RunPos, minPos, maxPos, Triggers, Scene, DayTime, WeatherType |
| `aps_pve_level_old` | `TableName.PVELevelOld` | 5,052 | 2546.9 KB | id, type, subtype, play_type, Triggers, para1, para2, para7, scene_show, reward, order, name *(+66)* |
| `aps_pve_monument` | `TableName.PVEMonument` | 687 | 207.8 KB | id, level, reEnter, build_condition, auto_move, enter_resource_cost, season, show_reward, use_b |
| `aps_pve_part_zombie` | `TableName.PveRolePart` | 18 | 2.0 KB | id, hat, head, cloth, pants, shoes, weapon |
| `aps_pve_trigger` | `TableName.PVETrigger` | 797 | 83.7 KB | id, UnclockType, UnclockPara, UnclockPara2, ModelName, Pos, Transform, State, RecoverCd, LinkTriggerId, IsGuidePt, GuideId... |
| `aps_pve_trigger_old` | `TableName.PVETriggerOld` | 4,730 | 779.1 KB | id, UnclockType, SideQuest, Pos, UnclockPara, ShowPos, UnclockFog |
| `aps_pve_zombie` | `TableName.PVEZombie` | 156 | 26.6 KB | id, type, group, ModelName, MoveSpeed, WalkSpeed, Blood, Attack, AttackRadius, AttackDropDistance, MoveRange, DisengageDis... |
| `aps_resource_item` | `TableName.Aps_Resource_Item` | 78 | 10.5 KB | id, type, itemType, building, name, desc, order, price, price_diamond, trade_num, weight, isrob *(+13)* |
| `aps_resources` | `TableName.Resource` | 26 | 2.2 KB | id, icon, name, description, order, out_building |
| `aps_sandRoad` | `TableName.VirtualRoad` | 86 | 4.4 KB | id, type, model, rotate, Pos, size |
| `aps_science_tab` | `TableName.APSScienceTab` | 21 | 6.4 KB | id, name, position, order, quality, type, para1, unlock_level, building, icon_start, icon, science *(+4)* |
| `aps_season` | `TableName.APS_Season` | 5 | 4.2 KB | id, season, season_list_icon, start_time, trendsId, mail_limit, pre_settle_time, pre_settle_mail, settle_time, settle_mail... |
| `aps_season_group` | `TableName.SeasonGroup` | 1,351 | 1356.3 KB | id, season, seasonPlayType, seasonPlayTypeclient, server, season_show, season_name, season_icon, seasoncount, seasonsend, ... |
| `aps_shop` | `TableName.APS_shop` | 3,056 | 499.4 KB | id, shop_id, goods, goods_num, currency, currency_num, server, order, cycle, cycle_times, vip_level, discount *(+24)* |
| `aps_singlemap_junk` | `TableName.APS_SINGLEMAP_JUNK, Table...` | 31 | 3.3 KB | id, Name, Desc, Show, Scale, Radius, Time, Dialog, Action, Reward, pic, Type |
| `aps_singlemap_pioneer` | `TableName.APS_SINGLEMAP_PIONEER` | 23 | 10.8 KB | id, NextID, UnclockFog, Noviceboot, Pos, UnclockType, UnclockPara, ShowPos, TagType, Tagpara, ArrowShow |
| `aps_singlemap_position` | `TableName.SingleMapPosition` | 223 | 12.0 KB | id, UnitType, Pos, Wave, UnitID |
| `aps_uav_dialogue` | `TableName.UavDialogue` | 8 | 0.6 KB | id, building, dialog, type, dialog_cd, public_cd, order |
| `aps_warning` | `TableName.Warning` | 15 | 1.8 KB | id, type, condition, Forbidden, land_cd, warn_cd, icon, icon_pre, order, describe, para1, world |
| `army` | `TableName.Army` | 7,578 | 1945.5 KB | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1, skill2, skill3 *(+2)* |
| `army_b` | `TableName.Army_B` | 6,858 | 1754.6 KB | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1, skill2, skill3 *(+2)* |
| `army_c` | `TableName.Army_C` | 6,858 | 1754.7 KB | id, hero1, hero2, hero3, arm, pve_power, effect, hero4, hero5, skill1, skill2, skill3 *(+2)* |
| `arrow_tips` | `TableName.ArrowTip` | 8 | 0.4 KB | id, type, number, base, order, time |
| `artifact` | `TableName.Museum` | 3 | 0.5 KB | id, name, description, icon, effect_description, effect_value, show_type, para1, cd_time |
| `barrel_monster` | `TableName.Barrel_Monster` | 31,899 | 1900.4 KB | id, baseId, property |
| `barrel_monster_base` | `TableName.Barrel_Monster_Base` | 349 | 127.1 KB | id, asset, model_size, relation_type, monster_type, is_boss, param, hp_bar_num, death_sound, is_attack, is_move, move_spee... |
| `barrel_pve` | `TableName.Barrel_PVE` | 40 | 2.2 KB | id, pve_level_id, level, lock, lock_time, lock_share, score_standard, if_difficult |
| `baseUnlockBuilding` | `TableName.BaseUnlockBuilding` | 15 | 0.5 KB | id, buildingId |
| `battlepass` | `TableName.BattlePass` | 4,201 | 288.0 KB | id, activity_panel_Id, level, levelup_exp, free_reward, pay_reward, highlight_reward, pay_item, free_item, highlight_locate |
| `bauble` | `TableName.Bauble` | 31 | 15.3 KB | id, name, description, icon, bg_pic, quality, max_lv, active_num, effect_new, effect_description, effect_value, power *(+17)* |
| `bauble_rating` | `TableName.BaubleRating` | 12 | 1.1 KB | id, name, rank, stage, stars, exp, icon, reward |
| `birth_coordinate_0` | `TableName.BirthPoint` | 361 | 10.1 KB | id, X, Y, resource |
| `build_fence` | `TableName.Build_Fence` | 31 | 0.9 KB | id, FencePath |
| `building` | `TableName.Building` | 4,089 | 2369.4 KB | id, name, description, long_description, pic, model, model_world, scan, order, effect_local, tab_type, build_type *(+63)* |
| `building_break` | `TableName.BuildingBreak` | 1 | 0.3 KB | id, buildlv, show_lv, description, direction_id, condition1, condition2, condition3 |
| `building_des` | `TableName.BuildingDes` | 10 | 0.9 KB | id, order, effect_local, tab_type, max_level, tiles, unlock_num, building_show, put, red_dot |
| `building_direction` | `TableName.BuildingDirection` | 3 | 0.4 KB | id, name, icon, description, new_build |
| `building_status` | `TableName.BuildStatus` | 5 | 0.7 KB | id, type, type2, time, effect, effect_num, group, priority, name, description, icon |
| `building_unlock_condition` | `xmlValue.building_unlock_condition` | 5 | 0.3 KB | id, unlock_condition |
| `c_animations` | `TableName.C_Animations` | 67 | 12.4 KB | id, idle, move, walk, attack, dead, sneakIdle, sneakMove, intertialIdle, sneak |
| `c_blueprint` | `TableName.C_BluePrint` | 13 | 1.1 KB | id, target, type, source, level, buildinglevel, order, need_talent |
| `c_camera_unlock` | `TableName.SU_SLG_Camera` | 2 | 0.4 KB | id, zoom, offset_zoom, rpg_range, range, slg_camera_pos_type, camera_pos, level, build_level |
| `c_camera_unlock_l` | `TableName.SU_SLG_Camera_L` | 2 | 0.4 KB | id, zoom, offset_zoom, rpg_range, range, slg_camera_pos_type, camera_pos, level, build_level |
| `c_equips` | `TableName.C_Equips` | 63 | 8.7 KB | id, type, melee, model, range, attack, defense, duration, randomDuration, animation, moveSpeed, attackSpeed *(+10)* |
| `c_event` | `TableName.SU_C_Event` | 102 | 9.4 KB | id, level, pre_type, pre_para1, check_immediately, do_noviceboot, noviceboot_drive, do_type, do_para1, recycle, do_para2, ... |
| `c_feed` | `TableName.SU_C_Feed` | 25 | 1.6 KB | id, hunger, thirsty, health, type, restorehealth, restorehealthdes, lootid, pee |
| `c_guide_pic` | `TableName.SU_Guide_Pic` | 6 | 0.6 KB | id, name, des, dub, noviceboot |
| `c_heroes_levelup` | `TableName.SU_HeroesLevelUp` | 100 | 8.6 KB | id, legend_atk, epic_atk, rare_atk, normal_atk, lord_atk, legend_def, epic_def, rare_def, normal_def, lord_def, legend_hp ... |
| `c_heroes_rank` | `TableName.SU_HeroesRank` | 46 | 2.7 KB | id, rank_atk, rank_def, rank_hp |
| `c_item_source_tip` | `TableName.SU_ItemSourceTip` | 50 | 1.7 KB | id, levelId, buildId |
| `c_pveSkill` | `TableName.SU_PveSkill` | 10 | 0.5 KB | id, skillAction, range |
| `c_pveSkillAction` | `TableName.SU_PveSKillAction` | 24 | 1.8 KB | id, type, speed, action, actionEffect, attacktype, para1, para2, damage, para3 |
| `c_pve_heroes` | `TableName.PveHero` | 195 | 50.1 KB | id, atk_type, animations, prefab_low, moveSpeed_stage, move_range_stage, attack_range_stage, attackSpeed_stage, skill_anim... |
| `c_quest` | `TableName.QuestXml` | 8,828 | 1172.6 KB | id, type, name, name_text, desc, desctype, para1, para2, order, position, list, progressshow *(+10)* |
| `c_reward_detail_tips` | `TableName.C_RewardDetailTips` | 68 | 4.1 KB | id, type, pic, title, desc |
| `c_sidebar` | `TableName.Sidebar` | 12 | 0.7 KB | id, name, icon, type, goto |
| `c_sidebar_type` | `TableName.SidebarType` | 5 | 0.4 KB | id, type_name, type_icon, type_order |
| `c_sound` | `TableName.C_Sound` | 285 | 22.3 KB | id, group, soundType, soundList, playType, Volume, Loop, SubType, param1, param2 |
| `c_trigger_gather` | `TableName.PVETriggerGather` | 105 | 8.8 KB | id, type, reward, step, name, soundtype, action, cd, expPerStep, tools, rewardid, slg_type |
| `c_vfx` | `TableName.PveVFX` | 61 | 3.3 KB | id, name, type, para1, para2 |
| `c_vfx_act` | `TableName.PveActVFX` | 37 | 2.7 KB | id, name, atk_eff, behit_eff, death_act, atk_eff_right, atk_eff_sence, atk_eff_fire, fly_eff |
| `camp_effect` | `TableName.CampEffect` | 4 | 0.3 KB | id, camp_type, camp_effect, icon, des |
| `camp_effect_b` | `TableName.CampEffect_B` | 4 | 0.3 KB | id, camp_type, camp_effect, icon, des |
| `capital_war` | `TableName.CapitalWar` | 1 | 0.6 KB | id, season, score_reward, rank_reward, kill_score, dead_score, occupy_score |
| `car_compon` | `TableName.CarCompon` | 90 | 19.7 KB | id, icon, name, category, level, quality, combine_next, combine, combine_num, level_max, effects, effect_num *(+12)* |
| `car_microchip` | `TableName.CarMicrochip` | 48 | 4.0 KB | id, desc, name, quality, slot, army_type, icon, is_craft, craft_materials |
| `car_microchip_attribute` | `TableName.CarMicrochipAttribute` | 1,968 | 155.6 KB | id, effects, microchip_id, rank, grade, power, id_next, skill, skill_level |
| `car_microchip_box` | `TableName.CarMicrochipBox` | 1,583 | 82.9 KB | id, goods_id, reward_id, num, odds |
| `car_microchip_grading` | `TableName.CarMicrochipGrading` | 33 | 2.0 KB | id, name, star, type, color, effect, effect_num |
| `car_microchip_promote` | `TableName.CarMicrochipPromote` | 180 | 13.1 KB | id, quality, rank, grade, value_self, cost_goods, return_good, return_self, cost_self, cost_item, return_item |
| `car_modify_new` | `TableName.GarageModify` | 351 | 36.5 KB | id, level, garage, add_exp, exp, additional_effect, additional_effect_num, additional_effect_num_show, item, power |
| `car_show` | `TableName.CarShow` | 5 | 19.8 KB | id, name, color, icon, icon_unlock, icon_army, cv_show, sound_idle, model, talent, model_point, talent_point *(+5)* |
| `car_show_barrel` | `TableName.Car_Show_Barrel` | 30 | 12.1 KB | id, lock_enemy, drift_pos, drift_delay_time, stand_pos, stand_delay_time, stand_stay_time, stand_abort_time, advance_pos, ... |
| `car_talent` | `TableName.CarTalent` | 652 | 135.7 KB | id, level, max_level, type, cost, need_car_level, need_car_level_new, position, order, car_condition, effect, effect_num *... |
| `car_talent_grading` | `TableName.CarTalentGrading` | 8 | 1.0 KB | id, name, desc, level, exp, car_level_tips, effect, effect_num, level_free, goods, desc_sp, effect_timeframe *(+2)* |
| `car_transform` | `TableName.GaragePart` | 600 | 46.3 KB | id, type, garage, max_level, level, effect, effect_num, name, icon |
| `career_effect` | `TableName.PlayerCareerEffect` | 65 | 5.4 KB | id, type, name, description, icon, order, effect_value, show_type, cd_time, show |
| `chapter_1` | `TableName.Chapter` | 1 | 0.7 KB | id, chapter, base_lv, name, tag, tag_text, description, pic, reward, quest, character, dialogue |
| `chat` | `TableName.PveChat` | 24 | 1.0 KB | id, chat_group_id, dialogID, view_time, chat_object |
| `city_resident` | `TableName.City_Resident` | 8 | 0.3 KB | id, building |
| `custom_dailypackage` | `xmlValue.custom_dailypackage` | 48 | 6.6 KB | id, item, condition, hero, hero_location, is_equip, arms_location, arms_location_2, is_wake, is_equip_wake |
| `d_season_intro` | `TableName.SeasonIntro` | 1 | 1.4 KB | id, season, interface |
| `daily_quest` | `TableName.DailyQuest` | 52 | 5.3 KB | id, accept1, name, desc, point, para2, gotype, gotype2, go, gobuild, icon, order *(+2)* |
| `decoration` | `TableName.Decoration` | 114 | 29.7 KB | id, type, name, icon, image, camera, camera2, type_gain, quality, order, bubble_param, model *(+27)* |
| `desert` | `TableName.Desert` | 31 | 14.1 KB | id, desert_type, season, desert_level, desert_res, neu_desert_army, desert_army, neu_desert_monster, desert_monster, force... |
| `desert_refresh` | `TableName.DesertRefresh` | 87 | 19.4 KB | id, city_id, em_desertid, desertid, num, desert_lv_range |
| `detect_event` | `TableName.DetectEvent` | 3,275 | 597.4 KB | id, type, type2, name, description, quality, icon, banner_image, panel_banner, para, image, pic *(+9)* |
| `dinosaur_boss` | `TableName.DinosaurBoss` | 5 | 2.0 KB | id, monster, title, reward, name, boss_frame, sfx_ui_wake, lop_strtime, sfx_ui_loop, loptime, sfx_wake, sfx_atk_02 *(+6)* |
| `dog_catwoman_stage` | `TableName.RescueDog` | 6 | 1.3 KB | id, item_id, chapter_name, chapter_desc, idle_spine, random_language, noviceboot, tips, bg, bubble_pos, task_head_spine, c... |
| `dragon_building` | `TableName.DragonBuilding` | 7 | 3.2 KB | id, type, size, name, des, model, pic, circle_pic, coordinate, occupy_time, open_time, circle *(+17)* |
| `ds_equip` | `TableName.Equip` | 18 | 20.2 KB | id, desc, name, quality, slot, army_type, icon, img, basic_attributes, break_exp, unlock_level, is_craft *(+11)* |
| `ds_equip_attribute` | `TableName.EquipAttribute` | 2,924 | 169.6 KB | id, effects, power, pve_hp |
| `ds_equip_material` | `TableName.EquipMaterial` | 5 | 0.3 KB | id, category, quality, combine, break |
| `ds_equip_mythical` | `TableName.EquipForgeMythical` | 7 | 0.6 KB | id, level, level_limit, promote_limit, cost_goods, cost_resource, reset_goods |
| `ds_equip_promote` | `TableName.EquipPromote` | 31 | 2.7 KB | id, level, rank, grade, level_up, cost_goods, cost_resource, reset_goods, cost_equips, return_good, reset_equips |
| `ds_equip_upgrade` | `TableName.EquipUpgrade` | 12 | 7.3 KB | id, quality, slot, army_type, highest_level, stone_upgrade_cost |
| `effect` | `xmlValue.effect` | 22 | 1.2 KB | id, arm_all, arm_1, arm_2, arm_3 |
| `effect_num_des` | `TableName.EffectNumDesc` | 747 | 29.7 KB | id, type, des, class, class_order, icon |
| `exclusive_equip_breakthrough` | `TableName.HeroSPEquipBreak` | 78 | 25.3 KB | id, group, level, name, effect, cost_item, cost_num, require_rank, max_level, unlock_skill, skill, barrel_skill *(+13)* |
| `exploit_rank` | `xmlValue.exploit_rank` | 12 | 1.4 KB | id, rank, score, reward, name, icon, star, rank_score_rate |
| `explore_level` | `TableName.LevelExplore` | 10 | 0.9 KB | id, level_order, name, name_value, level_id, hero_num, energy_cost, reward |
| `explorer_case` | `TableName.AdventureCase` | 150 | 18.2 KB | id, content, monster, buff, monster_showreward, reward, reward_show, random, randomdes |
| `explorer_entrance` | `TableName.AdventureEntrance` | 30 | 1.0 KB | id, pveLevel, reward |
| `fake_player` | `TableName.FakePlayer` | 1,430 | 60.3 KB | id, type, name, country, simple_name, alliance_num |
| `flag_effect` | `TableName.SeasonReward` | 9 | 1.7 KB | id, world_season, order, flag_effect_bg, flag_effect_title, flag_effect_effect, flag_effect_pic, flag_effect_season, effec... |
| `food_festival_building` | `TableName.FoodFestivalEatBuild` | 3 | 0.5 KB | id, quality, alliance_res_build_id, rank, table, name, pic, pic_1, des, world_des |
| `food_festival_ingredients` | `TableName.FoodFestivalIngredients` | 24 | 0.9 KB | id, activity_id, good_id |
| `food_festival_table` | `TableName.FoodFestivalEatTable` | 16 | 5.7 KB | id, level, num, name, des, model, pic, pic_1, pic_2, quality, reward, show_reward *(+7)* |
| `formation_status` | `SlgTableName.FormStatus, TableName....` | 6 | 0.7 KB | id, type, type2, time, group, priority, name, description, icon, effect, effect_num |
| `fossil_book` | `TableName.FossilBook` | 40 | 7.1 KB | id, num, name, goods, egg_num, des_got, des_bef, pic_got, icon, pic_bef, activity_id, reward *(+1)* |
| `function_view` | `TableName.SU_FunctionShow` | 38 | 2.5 KB | id, lock_mode, lock_condition, lock_guarantee, world_btn_show, slg_btn_show, rpg_btn_show, level_btn_show, boss_btn_show, ... |
| `gift` | `TableName.Present` | 13 | 2.9 KB | id, name, good_id, show_type, shop_pic, shop_pic_special, like, gift_exp, panel_type, festival_exp, eff_type, eff_para *(+... |
| `gift_reward` | `TableName.PresentLevel` | 100 | 3.1 KB | id, level, exp, good |
| `gift_special` | `TableName.PresentSP` | 15 | 0.9 KB | id, use_good, count, special_text, type, buff, special_desc |
| `goods` | `TableName.GoodsTab` | 1,025 | 247.4 KB | id, name, name_value, icon, description, type, lv, lv_limit, para, color, page, pages *(+31)* |
| `government` | `TableName.Government` | 19 | 1.9 KB | id, name, icon, effect, can_appoint, only_president_appoint, is_positive, title_name, type |
| `hero_battle` | `TableName.LOMap` | 150 | 36.9 KB | id, name, chapter, trigger, camp, show_reward, show_first_reward, power, army_level, lock |
| `hero_bounty` | `TableName.HeroBounty` | 72 | 7.5 KB | id, name, description, rarity, function, time_h, hero_num, camp_requirements, exp_hero, exp, item_show, reward *(+2)* |
| `hero_camp_intensify` | `TableName.HeroIntensify` | 10,521 | 905.0 KB | id, group, lv, season, max_lv, cost, power, effect, camp, effect_ext |
| `hero_camp_random` | `TableName.HeroIntensifyRandomEffect` | 1,212 | 94.0 KB | id, name, description, pic, effect_value, tips |
| `hero_core` | `TableName.HeroArkCore` | 7 | 0.3 KB | id, core_type, condition, effect |
| `hero_entrust` | `TableName.HeroEntrust` | 2 | 0.4 KB | id, Description, dub, Npc_Model, Position, Pre_quest, Demand, Reward_hero_fake, Npc_Pic |
| `hero_lack_tips` | `TableName.Hero_Lack_Tips` | 42 | 4.0 KB | id, heroid, fragmentid, tips, order, name, btn_name, base, pic, para1 |
| `hero_monthcard` | `TableName.HeroMonthCard` | 88 | 6.9 KB | id, name, description, sub_name, reward_pic, reward1_pic, reward2_pic, reward3_pic, reward4_pic, reward5_pic |
| `hero_official` | `TableName.HeroOfficial` | 54 | 4.1 KB | id, camp, type, official_position, official_name, unlock_lv, effect, max_value, max_hero_power, extra_condition, extra_val... |
| `hero_station` | `TableName.HeroStation, TableName.He...` | 16 | 0.8 KB | id, build_id, career, people_unit_limit, order |
| `hero_tag` | `TableName.NewHeroesTag` | 26 | 1.3 KB | id, name, pic, desc |
| `herobattle_skill` | `TableName.HeroBattle_Skill` | 21 | 2.2 KB | id, week, time, duration, hero, skill, hero_pic, tips |
| `heroes_exclusive_equip` | `TableName.HeroSPEquip` | 390 | 87.7 KB | id, group, level, name, effect, cost_item, cost_num, icon, image, special_effects, spine, require_rank *(+8)* |
| `heroes_levelup` | `TableName.NewHeroesLevelUp` | 200 | 23.7 KB | id, exp, lv_attr_atk1, lv_attr_atk2, lv_attr_atk3, lv_attr_atk4, lv_attr_def1, lv_attr_def2, lv_attr_def3, lv_attr_def4, a... |
| `ice_animals` | `TableName.IceAnimals` | 18 | 3.6 KB | id, create_type, activity_id, name, desc, downtime, size, type, model, tips_icon, ui_icon, dialog *(+6)* |
| `ice_snowman` | `TableName.SnowMan` | 228 | 22.4 KB | id, level, exp, name, prefab, activity_id, level_reward, type, stage, level_effect, milestone_unlock, skin_goods |
| `icecave_atlas_reward` | `TableName.IceCaveAtlasReward` | 7 | 0.5 KB | id, type, star_node, active_condition, active_reward, show_goods_id |
| `icecave_fish` | `TableName.IceCaveFish` | 65 | 7.6 KB | id, name, desc, color, pic, pic_none, star_num, atlas_diamond, file_number, can_get_from, unlock_cost_after_season, is_spe... |
| `icecave_fish_group` | `TableName.IceCaveFishGroup` | 10 | 1.8 KB | id, fish_produce_weight |
| `icecave_info` | `TableName.IceCaveInfo` | 10 | 2.3 KB | id, level, model, banner, name, desc, icon, xy, monster_id, durability, hp_bar_unit, dur_bar_unit *(+8)* |
| `icecave_open` | `TableName.IceCaveOpen` | 2 | 0.3 KB | id, preview_opentime, activity_opentime, icecave_opentime |
| `icecave_title` | `TableName.IceCaveTitle` | 3 | 0.3 KB | id, icon, name, desc |
| `init_build` | `TableName.Init_Build` | 29 | 3.7 KB | id, sceneId, pointIndex, buildId, level, initHp, tiles, rotation, landlock, order, dependencyorder, initUpState *(+8)* |
| `land_lock_property` | `TableName.Land_Lock_Property` | 167 | 10.0 KB | id, stand, battle, rotate, battleEffect, collectEffect, unlockEffect, guideStateEffect |
| `language_channel` | `TableName.CLanguageRoom` | 14 | 0.4 KB | id, channel_type, group |
| `level_up` | `TableName.LevelUp` | 38 | 1.9 KB | id, describe, building, APS_resource_item |
| `loadingTips` | `TableName.DateBaseOtherLoadingTips,...` | 23 | 1.1 KB | id, description, level_range, delay_time, rate |
| `love_message_date` | `TableName.LoveMessageData` | 157 | 13.4 KB | id, next_id, type, time, name, text, bg_pic |
| `love_message_hero` | `TableName.LoveMessageHero` | 33 | 9.4 KB | id, hero_id, head_pic, name, chat_id, chat_name, chat_pic, unlock_pic, unlock_pic_j, chat_unlock_pic_type, summary_text, s... |
| `love_message_story` | `TableName.LoveMessageStory` | 1,249 | 96.4 KB | id, next_id, time, chat_type, chat_person, chat_text, show_time, photo_num, battery, chat_pic |
| `lw_base_visitor_event` | `TableName.LwBaseVisitorEvent` | 480 | 81.3 KB | id, type, para, name, desc, hero_icon, hero_halfbody, color, model_path, dialog, btn_dialog, bubble_icon *(+1)* |
| `lw_base_visitor_welcome` | `TableName.VisitorWelcome` | 30 | 6.1 KB | id, trigger, type, name, desc, hero_icon, model_path, dialog, dialog_bubble_toward, action, dialog_to_gate, unlock_buildin... |
| `lw_buff` | `TableName.LW_Buff` | 355 | 57.3 KB | id, type, sub_type, para, buff_time, additive_type, max_level, group, active_effect, activing_effect, ignore_rotate, desc |
| `lw_bullet` | `TableName.LW_Bullet` | 1,036 | 475.1 KB | id, base_type, damage_type, damage_nature, damage, mvt_type, motion_curve, target_type, is_following, lifetime, bullet_fly... |
| `lw_count_stage` | `TableName.LW_Count_Stage` | 5 | 2.7 KB | id, order, name, desc, title, target, building_condition, stage_type, end_type, end_param3, end_z, a *(+14)* |
| `lw_count_stage_group` | `TableName.LW_Count_Stage_Group` | 11 | 3.9 KB | id, max_hp, unit_pt, class, move_speed, unit_radius, face_dir, unit_prefab, dead_vfx, hit_vfx, hp_bar_height, move_anim *(... |
| `lw_count_stage_soilder` | `TableName.LW_Count_Stage_Soilder` | 8 | 2.7 KB | id, point, radius, end_line_size, weapon, muzzle_bone, prefab, dead_vfx, march_anim, move_anim, contact_anim, aim_anim *(+2)* |
| `lw_count_stage_trap` | `TableName.LW_Count_Stage_Trap` | 56 | 17.9 KB | id, prefab, bubble_height, hit_vfx, motion_parts, motion_type, motion_param1, motion_param2, motion_param3, sleep_time, ma... |
| `lw_hero` | `TableName.LW_Hero` | 41 | 26.8 KB | id, type, title_name, first_name, quality, template_id, base_hp, base_patk, base_pdef, base_acc, base_crit, base_load *(+34)* |
| `lw_hero_appearance` | `TableName.HeroAppearance` | 129 | 94.9 KB | id, model_path, simple_model_path, model_size, hero_effect, fire_path, city_model_path, hero_detail_shadow_scale, hero_det... |
| `lw_hero_effect` | `TableName.LW_Hero_Effect` | 67 | 24.2 KB | id, hit_effect_direction, death_effect_nomal, death_sound, hit_sound, death_effect_fire, death_effect_elect, death_effect_... |
| `lw_hero_skill` | `TableName.LW_Skill, TableName.LW_He...` | 968 | 254.2 KB | id, name, desc, maxLevel, star, group, power, pre_cd, attack_interval, priority, target_type, is_normal_attack *(+25)* |
| `lw_hero_skill_effect` | `TableName.LW_Skill_Effect` | 141 | 16.7 KB | id, fire_effect, fire_effect_time, fire_delay, fire_shake, cast_effect, cast_sound, shake_priority, fire_audio, cast_effec... |
| `lw_hit_reaction` | `TableName.LW_Hit_Reaction` | 32 | 7.4 KB | id, hit_animation, dead_move, hit_shake, hit_zoom, death_effect_nomal, death_effect_nomal_follow, hit_type, para1, death_e... |
| `lw_monster_born` | `TableName.LW_Monster_Born` | 23,481 | 2729.2 KB | id, coord, type, para, monster, buff_item, para2, para3, para4 |
| `lw_path_point` | `TableName.LW_PathPoint` | 275 | 9.7 KB | id, point_type, para |
| `lw_scene` | `TableName.LW_Scene` | 76 | 29.0 KB | id, type, asset, scene_size, path_point, final_monster_group, normal_monster, auto_monster_group, start_monster_group, nor... |
| `lw_sound` | `TableName.LW_Sound` | 27 | 1.4 KB | id, is_cycle, sound |
| `lw_stage` | `TableName.LW_Stage` | 35 | 7.8 KB | id, order, name, desc, title, target, type, scene, trigger_item, trigger_plot, block_hp_bonus, stage_icon *(+7)* |
| `lw_stage_feature` | `TableName.LW_Stage_Feature` | 147 | 65.6 KB | id, order, name, desc, title, target, type, scene, scene_tail, birth_point, boss_line, boss_area *(+15)* |
| `lw_train_para` | `TableName.LW_Train_Para` | 39 | 1.9 KB | id, 说明, val |
| `lw_train_property` | `TableName.LW_Train_Property` | 480 | 257.6 KB | id, quality, HQLevel, Guard_max, length, speed, lowest_reward, train_route_length, reward1, slot_number, type, world_model... |
| `lw_trigger_item` | `TableName.LW_Trigger_Item` | 1,414 | 408.2 KB | id, type, para, dead_effect, is_weapon, prefab_path, location, rotation, size, icon, effect, is_soldier *(+5)* |
| `mail_group` | `TableName.MailGroup` | 17 | 0.7 KB | id, order, type, name, show |
| `mail_show` | `TableName.MailShow` | 37 | 1.4 KB | id, tab, show_id, sub_type |
| `mail_show_id` | `TableName.MailShowId` | 197 | 24.2 KB | id, banner, icon_read, icon_unread, superscript, bg_read, bg_unread, icon_win, icon_lose |
| `main_city_area` | `TableName.SU_MainCityArea` | 89 | 11.0 KB | id, name, entrance_name, all_tiles_rect, pve_level_id, contact_area, standPos, lock_type, area_type, order, rewardIds, cli... |
| `masteryExp` | `TableName.MasteryExp` | 180 | 5.1 KB | id, level, Exp |
| `mine` | `TableName.MineCave` | 192 | 40.1 KB | id, level, monster, time, type, name, icon, picture, reward_type, correspond_output, output, plunder *(+8)* |
| `missile` | `TableName.Missile` | 3 | 0.8 KB | id, name, des, color, pic, icon, icon_army, sound_idle, talent |
| `missile_unlock` | `TableName.MissileUnlock` | 3 | 1.3 KB | id, type, target, goods, target_desc, target_para1, daily_quest, daily_quest_desc, daily_quest_reward, daily_target, daily... |
| `mistress` | `TableName.Mistress` | 30 | 17.8 KB | id, mistressNPC_id, room_mod, hold_animation, hold_cv, hold_text, head, head_animation, head_cv, head_text, boob, boob_ani... |
| `mistress_base` | `TableName.MistressBase` | 6 | 1.9 KB | id, name, resource, high_resource, mistressRadarIcon_big, icon, icon_gray, smallIcon, BubblesIcon, unlock_condition, need_... |
| `mistress_chat` | `TableName.MistressChat` | 772 | 104.7 KB | id, mistress_id, group_id, trigger_name, trigger_order, triggertype, triggerpara, chat_id, next_chat, chat_type, chat_name... |
| `mistress_lv` | `TableName.MistressLv` | 60 | 16.2 KB | id, mistress_id, pre_event_id, love_lv, love_lv_name, love_value, mistress_view_id, tap_num, tap_love_value, tap_act, tap_... |
| `night_demon_hunter_info` | `TableName.DemonHunterInfo` | 12 | 2.6 KB | id, hunter_quality, weight, hunter_name, hunter_desc, hunter_icon, hunter_mission_icon, hunter_pic, map_dialogue_random, c... |
| `night_demon_hunter_quest` | `TableName.DemonHunterQuest` | 13 | 3.1 KB | id, quest_pool, weight, quest_id, quest_name, quest_desc, quest_icon_small, quest_icon, quest_reward, reward_show, quest_q... |
| `night_eternal_duke_donate` | `TableName.GhostKingDonate` | 2 | 0.4 KB | id, donate_type, donate_stage, stage_reward, stage_reward_show, reissue_mail |
| `night_eternal_duke_info` | `TableName.GhostKingInfo` | 7 | 2.7 KB | id, season_week, name, lv, threat_lv, desc, icon, spine_step, activity_icon, monster_id, durability, skill *(+3)* |
| `night_lunarlight_card` | `TableName.NightLunarLightCard` | 58 | 17.5 KB | id, type, random_weight, reward, show_reward, color, order, number, name, desc, pic, goods_pic *(+10)* |
| `night_lunarlight_sorceress` | `TableName.NightLunarLightSorceress` | 60 | 6.8 KB | id, true_level, favor_level, favor_stage, favor_desc, favor_value, stage_reward, show_reward, unlock_team_slot |
| `night_lunarnight_pack` | `TableName.NightLunarLightPack` | 6 | 0.5 KB | id, name, unlock_time, deck |
| `noviceboot` | `TableName.Guide` | 1,246 | 299.1 KB | id, returnstepid, savedoneid, jumptype, jumppara, jumpid, nextid, triggertype, triggerpara, forcetype, waittime, tipswaitt... |
| `noviceboot_B` | `TableName.GuideB` | 1,131 | 270.3 KB | id, returnstepid, savedoneid, jumptype, jumppara, jumpid, nextid, triggertype, triggerpara, forcetype, waittime, tipswaitt... |
| `npc_base` | `TableName.PveNpc` | 29 | 3.5 KB | id, type, name, icon_head, icon_head_S, low_model, high_model, action_group, aps_pve_zombie_id, walk_path, unlock_conditio... |
| `officer_list` | `TableName.OfficerList` | 842 | 59.8 KB | id, group_id, officer_id, show_rank, show_rate, goods, goods_num, server_time, show_rate_rank1, pity_show_rate, show_rate_... |
| `officer_recruit` | `TableName.HeroRecruit` | 9 | 19.2 KB | id, type, quest_recruit_type, order, item, function, name, time, rate1, rate2, class, pitypro *(+14)* |
| `optionconfig` | `TableName.Option_Config` | 320 | 52.0 KB | id, id_group, model, guide_id, picture, dialog_initial, option_dialog, cost_res, reward_icon, dialog_result, dialog_result... |
| `overlord_cure` | `TableName.OverlordCure` | 3 | 0.4 KB | id, cure_point, cure_state, cure_state_icon, font_color, spine |
| `overlord_file` | `TableName.OverlordFile` | 6 | 0.8 KB | id, unlock_cure, unlock_icon, file_title, file_text, file_sign, file_pic, reward |
| `overlord_military_rank` | `TableName.OverlordMilitaryRank` | 201 | 56.5 KB | id, overlord, rank, stage, name, self_effect, all_effect, nextId, item, icon, font_color, background_icon *(+10)* |
| `overlord_rank` | `TableName.OverlordRank` | 251 | 53.0 KB | id, overlord, stage, node, rank, icon, item, skill_unlock_lv, skill_unlock_star, spine, nextId, power *(+2)* |
| `overlord_show` | `TableName.OverlordShow` | 6 | 4.4 KB | id, overlord, rank, stage, default_name, color, spine, low_model, middle_model, high_model, in_sound, loop_sound *(+9)* |
| `overlord_train` | `TableName.OverlordTrain` | 2,004 | 208.3 KB | id, overlord, type, level, additional_effect, additional_effect_num, is_critical, exp, add_exp, item, upgrade_color, power... |
| `player_career` | `TableName.PlayerCareerXml, TableNam...` | 50 | 8.6 KB | id, type, name, description, story, effect, require_item, require_lv, show_type, order, career_tag, icon *(+3)* |
| `player_level` | `TableName.PlayerLevel` | 100 | 5.6 KB | id, level, exp, skillpoint, unlock_reward, box_icon, unlock_career, career_free |
| `popup_package_ui` | `TableName.PopupPackageUI` | 122 | 21.4 KB | id, type, name, main_icon, tab_pic, bg_pic, bg_pic2, title_top_color, title_bottom_color, outline_num, desc_text_color, an... |
| `push_map` | `TableName.StoryMap` | 6 | 7.5 KB | id, level, level_num, reward, name |
| `pve_type` | `TableName.SU_PveType` | 102 | 19.8 KB | id, type, name, order, resettype, level, cost, requirelevel, text, loading_tips, icon, pic *(+12)* |
| `pve_world` | `TableName.SU_PveWorld` | 60 | 9.0 KB | id, type, level, diffculty, recommend_power, pve_id, name, pic, model, desc, reward, reward_num *(+3)* |
| `pvp_virtual_player` | `TableName.NpcCity` | 150 | 31.8 KB | id, duration, size, army, res, level, dialog, dialog_goto, dialog_win, dialog_lose, name, head *(+9)* |
| `questionAndAnswer` | `TableName.QuestionAndAnswer` | 128 | 10.8 KB | id, type, question, answers, answer, fraction, follow_time, level, reward_true |
| `radio_station` | `TableName.Phonograph` | 3 | 1.4 KB | id, sort, buff_type, name, good_id, bgm, duration, cover_image, cover_image_select, record_image, payment_image, story_des... |
| `recharge` | `TableName.Recharge` | 54 | 7.2 KB | id, type, order, hot, name, icon, para1, tab_icon, para2, image2, onoff |
| `recycle_items` | `TableName.RecycleItems` | 88 | 9.5 KB | id, server_id, activity_id, recycle_type, rewardgoods_id, num, activity_special_type |
| `res_lack_tips` | `TableName.Res_Lack_Tips` | 1,509 | 217.3 KB | id, goods, tips, order, name, btn_name, base, pic, level, group, res, para1 *(+13)* |
| `resources_collect` | `TableName.ResourcesCollect` | 5 | 0.6 KB | id, name, desc, icon, unlock_science, gathering, show_gathering, collect_power |
| `roaming_boss_reward_show` | `TableName.RoamingBossRewardShow` | 3 | 2.0 KB | id, world_season, mons_name, mons_desc, mons_img, mons_id_list, mons_reward_kill, mons_reward_rally, boss_name, boss_desc,... |
| `robot` | `TableName.Robot` | 7 | 2.2 KB | id, unlockType, order, name, icon1, icon2, sculpture1, sculpture2, cv, cv_text, cv_job_done, unlockParam *(+8)* |
| `rocket_order` | `TableName.Rocket_Order` | 152 | 12.2 KB | id, type, product_id, group, state, condition_type, building_condition, product_num, order_reward, ext_order_reward, temp_... |
| `score` | `TableName.Score` | 579 | 45.6 KB | id, type, name, value, points, season_type, group, tips, gotoType, margeType, margeGroup, pic *(+3)* |
| `score_list` | `TableName.ScoreList` | 2 | 0.2 KB | id, score |
| `scrolling_announcement` | `TableName.Announcement` | 79 | 4.8 KB | id, type, content, priority, base, block, para1, loop |
| `season_active_skill` | `TableName.MasterySkill` | 33 | 6.5 KB | id, type, needId, goto, use_position, name, icon, description, des_value, CDType, cd_time, CD *(+10)* |
| `season_activity_panel` | `TableName.SeasonActivityPanel` | 60 | 10.0 KB | id, title_group, season_panel_group, world_season, type, is_main, panel_id, order, size_type, preview_pic, pic_type, pic *... |
| `season_config` | `TableName.SeasonConfig` | 11 | 0.5 KB | id, para1 |
| `season_dialog` | `TableName.SeasonDialog` | 62 | 3.5 KB | id, season_dialog |
| `season_influence` | `TableName.SeasonInfluence` | 37 | 12.4 KB | id, influence, influence_b, influence_new, name, pic, star, box, resistance, reward, effect |
| `season_mastery` | `TableName.Mastery` | 399 | 65.6 KB | id, group, home, type, name, detaildescription, description, icon, needLv, season, world_season, Lv *(+9)* |
| `season_mastery_b` | `xmlValue.season_mastery_b` | 449 | 67.4 KB | id, group, home, type, name, detaildescription, description, icon, needLv, season, world_season, Lv *(+9)* |
| `season_object` | `TableName.SeasonObject` | 14 | 1.6 KB | id, type, skill, value1, value2, value3, prefab, area, name, description, des_value, extra_des *(+1)* |
| `season_review` | `TableName.SeasonReviewRule` | 12 | 1.0 KB | id, season, event_name, event_desc, pic |
| `season_troopline` | `TableName.SeasonTroopLine` | 5 | 0.9 KB | id, TroopLine, TroopLineDrag, Green, White, Red, Blue, Purple, Yellow |
| `season_week` | `TableName.SeasonWeek` | 8 | 1.0 KB | id, season, season_begin_time, name, season_week_exchange, show, icon |
| `server_badge` | `TableName.Server_Badge` | 6 | 1.2 KB | id, name, description, icon, quality, order, icon_new, quality_new, condition, show_star, new_star, hide_on_legacy_logic *... |
| `server_capital_reward` | `TableName.Server_Capital_Reward` | 1 | 0.9 KB | id, season, score_reward, reward_value, kill_score_inbuilding, kill_score, dead_score, kill_score_other, dead_score_other,... |
| `server_ip` | `TableName.ServerIp` | 11 | 4.2 KB | id, severid_range, direct, aws, gcp, ip_v6, direct_ip, aws_ip_1, gcp_ip, aws_ip_2, ws, wss *(+2)* |
| `servers_wonder_war` | `TableName.Servers_Wonder_War` | 235 | 48.0 KB | id, server_ids, need_level, open_week, type, open_time, continue_time, show_day, cycle, score, war, duration *(+7)* |
| `shelter_emoji` | `TableName.ShelterEmoji` | 22 | 2.2 KB | id, name, free, sound, icon, animation, zoom, offset, para, good, isReverse |
| `skill` | `TableName.SkillTab` | 2,054 | 1177.1 KB | id, skill_source_group, type, level, object, object_num, scale, effect, effect_num, name, des, icon *(+50)* |
| `speedup_config` | `TableName.SpeedUpConfig` | 7 | 0.4 KB | id, speedup_goods, max, min |
| `state_ruler_intro` | `TableName.State_Ruler_Intro` | 11 | 0.9 KB | id, level, exp, name, level_reward, buff_level_1, buff_level_2 |
| `state_skill` | `TableName.StateSkill` | 1 | 0.4 KB | id, type, name, desc, rule, color, official, pre_time, launch_time, during_time, prefab, punish_time *(+4)* |
| `status` | `TableName.StatusTab` | 263 | 43.2 KB | id, type, type2, time, effect, effect_num, group, priority, name, description, subgroup, overlap *(+11)* |
| `suit_equip` | `TableName.Equip_Suit` | 3 | 1.0 KB | id, type, name, description, order, equip, effect_description1, value1, unlock_tips1, effect_condition1, effect_descriptio... |
| `sys_red_packet` | `TableName.SysRedPacket` | 203 | 57.1 KB | id, type, building, level, desc, chat, num, res_type, gold, icon, item, time *(+12)* |
| `talent` | `TableName.Talent_New` | 35 | 4.7 KB | id, type, group, order, lv, name, effect_value, description, icon, resource, color, special_rate |
| `talent_type` | `TableName.TalentType` | 4 | 0.2 KB | id, name, order |
| `time_bridge` | `TableName.TimeBridge` | 30 | 2.1 KB | id, level, level_id, buildlv, name, name_value, description, quality, reward |
| `trade_post` | `TableName.TradePost` | 40 | 8.9 KB | id, season, world_season, level, group, model, banner, name, desc, icon, xy, size *(+5)* |
| `trade_post_open` | `TableName.TradePostOpen` | 4 | 0.9 KB | id, preview_opentime, activity_opentime, group, tradepost_opentime, tradepost_opentime_server, tradepost_opentime_cross, f... |
| `trade_post_shopitem` | `TableName.TradePostShopItem` | 141 | 8.6 KB | id, goods_id, goods_num, sell_quantity, price, is_for_owner, is_for_member, owner_discount, alliance_discount, shop_type |
| `trade_title` | `TableName.TradePostTitle` | 9 | 0.8 KB | id, level, world_season, icon, name, desc |
| `trends` | `TableName.Trends` | 23 | 2.2 KB | id, name, description, description_value, pic, show_time, order, season, title_icon, type, phase, parent_id |
| `trends_function` | `TableName.TrendsFunction` | 41 | 2.4 KB | id, name, description, description_value, pic |
| `troop_action` | `TableName.TroopAction` | 13 | 0.7 KB | id, type, dialogID, rate, stay_time, show_time |
| `video_hero` | `TableName.VideoHero` | 1 | 0.1 KB | id, hero_id, video_id |
| `vip` | `TableName.Vip` | 20 | 4.9 KB | id, point, icon, reward1, reward2, reward2_new, display, gift_pic, freebie_banner, effect, need_hero |
| `vip_temp` | `TableName.VipTemp` | 17 | 3.5 KB | id, point, icon, reward1, reward2, reward2_new, display, effect |
| `volcano_area` | `TableName.VolcanoArea` | 6 | 0.6 KB | id, scope, interval_random, resource_id, interval_start, interval_start_time, interval_time, interval_number, interval_del... |
| `volcano_broadcast` | `TableName.VolcanoBroadcast` | 10 | 1.0 KB | id, type, para, score, scrolling_announcement_id, icon, bg |
| `volcano_building` | `TableName.VolcanoBuilding` | 11 | 0.9 KB | id, size, coordinates, area_id, name, des, alliance_point, circle_person_point |
| `volcano_land` | `TableName.VolcanoLand` | 10 | 0.4 KB | id, coordinates, res_id |
| `volcano_match` | `TableName.VolcanoMatch` | 41 | 5.8 KB | id, server, server_group, open_time, battle_start_time, battle_duration, trailer_time, draw_time, public_time, communicati... |
| `volcano_para` | `TableName.VolcanoPara` | 41 | 2.4 KB | id, 备注, para |
| `volcano_res` | `TableName.VolcanoRes` | 9 | 2.6 KB | id, res_type, type, order, size, time_points, complete_points, name, desc, pic, lod_none, lod_mine *(+8)* |
| `volcano_reward` | `TableName.VolcanoReward` | 6 | 4.7 KB | id, allocate_reward, atk_reward_number, atk_reward_add, def_reward_number, def_reward_add, atk_victory_reward, atk_fail_re... |
| `wonder_gift` | `TableName.WonderGift` | 24 | 2.0 KB | id, name, type, reward, num, season, worth, icon |
| `world_packet_reward` | `TableName.WorldPacketReward` | 2 | 0.6 KB | id, name, type, rewardId, box_reward, expire, pickTimes, model, panel_banner |
| `world_quest` | `TableName.WorldQuest` | 168 | 9.5 KB | id, type, activity, desc, para1, para2, order |
| `world_scene` | `TableName.WorldLod` | 221 | 10.4 KB | id, type, path, lod, isMain, Fading |
| `worldcity` | `TableName.WorldCity` | 90 | 289.8 KB | id, location, level, size, server_type, eden_city_type, belong_eden_camp, monster_id, monster_id_b, monster_num, buff, fir... |
| `xiaoren_rank` | `TableName.XiaoRenRank` | 26 | 1.4 KB | id, level, stage, cost_common, cost_self |
