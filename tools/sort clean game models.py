#!/usr/bin/env python3
"""
Reorganize all 482 extracted Last Z 3D models inside models/ by Season first
(Pre-Season 1, Season 1..5), then clean space-separated Faction folders, with
concise real English names, zero underscores (_) in any file or directory name,
rewired OBJ/MTL material & texture references, and zero em dashes (U+2014).
"""

from __future__ import annotations

import csv
import io
import json
import logging
import re
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import trimesh


DEFAULT_REPO_DIR = Path(r".")

SEASON_ORDER: List[str] = [
    "Pre-Season 1",
    "Season 1",
    "Season 2",
    "Season 3",
    "Season 4",
    "Season 5",
    "Season 6",
]

SEASON_THEMES: Dict[str, str] = {
    "Pre-Season 1": "Core Launch Roster, Base Shelter, Vehicles, Zombies, and World Assets",
    "Season 1": "Clash of Thrones (Season 1 Heroes and Companions)",
    "Season 2": "Wastes Watcher (Season 2 Heroes and Desert Expedition Assets)",
    "Season 3": "Everfrost Era (Season 3 Heroes, Glacier Bosses, Arctic Beasts, and Snow Structures)",
    "Season 4": "Dinosaur Origin (Season 4 Heroes, Hero Awakenings, Dinosaurs, and Dino Vehicles)",
    "Season 5": "Moonlit Elegy (Season 5 Gothic Bosses, Vampires, Werewolves, and Cursed Mountains)",
    "Season 6": "Season 6 Content",
}

FACTION_CLEAN_MAP: Dict[str, str] = {
    "Blood_Rose": "Blood Rose",
    "Wings_of_Dawn": "Wings of Dawn",
    "Guard_of_Order": "Guard of Order",
    "Zombies_and_Monsters": "Zombies and Monsters",
    "Blood_Hand_and_Raiders": "Blood Hand and Raiders",
    "Troops_and_Soldiers": "Troops and Soldiers",
    "Vehicles_and_Tanks": "Vehicles and Tanks",
    "NPCs_and_Survivors": "NPCs and Survivors",
    "Weapons": "Weapons",
    "Buildings_and_Environment": "Buildings and Environment",
}

FACTION_ORDER: List[str] = [
    "Blood Rose",
    "Wings of Dawn",
    "Guard of Order",
    "Zombies and Monsters",
    "Blood Hand and Raiders",
    "Troops and Soldiers",
    "Vehicles and Tanks",
    "NPCs and Survivors",
    "Weapons",
    "Buildings and Environment",
]

# Exact clean English display names for specific asset slugs so zero raw Pinyin or
# awkward duplicated parenthetical names remain anywhere in models/.
EXACT_SLUG_NAMES: Dict[str, str] = {
    # Monsters & Zombies
    "monster_biochemistry_boss": "Biochemical Tyrant Boss",
    "monster_zombie_blackfat": "Boomer Mutant Boss",
    "monster_character_butcher": "Chainsaw Butcher Boss",
    "monster_zomb_gp_zomb_butcher": "Infected Butcher",
    "monster_character_crazy": "Frenzied Zombie",
    "monster_character_fat": "Bloated Zombie",
    "monster_character_mechanic": "Wrench Mechanic Zombie",
    "monster_common": "Monster Drop Shadow",
    "monster_s5_s5_hongmo": "Vampire Guard",
    "monster_s5_s5_hongmo_a": "Blaze Winged Demon",
    "monster_crow": "Mutant Crow",
    "monster_s5_s5_jisi": "Night Cult Priest",
    "monster_s4_s4_konglong_yichilong": "Yi Qi Wyvern",
    "monster_e_burst_01": "Exploder Zombie",
    "monster_s3_boss_snowkingkong_01_s3": "Glacier Kong Boss",
    "monster_godzilla": "Godzilla Mutant Boss",
    "monster_s3_boss_lceworm_01_s3": "Ice Worm Boss Stage 1",
    "monster_s3_boss_lceworm_02_s3": "Ice Worm Boss Stage 2",
    "monster_s3_boss_lceworm_03_s3": "Ice Worm Boss Stage 3",
    "monster_zombie_policeshild": "Infected Riot Shield Officer",
    "monster_hugehand_zombie": "Mutant Claw Zombie",
    "monster_n_police_01": "Infected Police Officer",
    "npc_game_npc_fem_zomb": "Infected Female Zombie",
    "npc_game_npc_fem_zomb_dead_ani": "Infected Female Corpse",
    "npc_game_npc_zob_rc": "Riot Infected Zombie",
    "npc_game_npc_zob_rc_dead": "Splitting Riot Zombie",
    "npc_game_npc_zomb_gp_01": "Wandering Zombie 1",
    "npc_game_npc_zomb_gp_02": "Wandering Zombie 2",
    "npc_game_npc_zomb_gp_03": "Wandering Zombie 3",
    "npc_game_npc_zombie_male_b": "Infected Male Zombie B",
    "npc_game_npc_zombie_male_c": "Infected Male Zombie C",
    "overlord_pve_overlord_dinasour_101_pve": "Overlord Mecha-Zilla Stage 1",
    "overlord_pve_overlord_dinasour_102_pve": "Overlord Mecha-Zilla Stage 2",
    "overlord_pve_overlord_dinasour_103_pve": "Overlord Mecha-Zilla Stage 3",
    "overlord_pve_overlord_dinasour_104_pve": "Overlord Mecha-Zilla Stage 4",
    "overlord_pve_overlord_dinasour_105_pve": "Overlord Mecha-Zilla Stage 5",
    "overlord_pve_overlord_dinasour_106_pve": "Overlord Mecha-Zilla Stage 6",
    "monster_s3_pet_deer_01_s3": "Arctic Caribou",
    "monster_s3_pet_fox_01_s3": "Arctic Snow Fox",
    "monster_s3_pet_mammoth_01_s3": "Woolly Mammoth",
    "monster_s3_pet_pig_01_s3": "Frost Wild Boar",
    "monster_s4_s4_konglong_yilong": "Pterosaur",
    "environment_map_world_resource_s3_monster_snowman_01": "Everfrost Snowman Monster",
    "monster_s5_s5_cerberus": "Cerberus Hellhound",
    "monster_s5_s5_countess": "Blood Countess",
    "monster_s5_s5_dracula": "Count Dracula",
    "monster_s5_s5_gargoyle": "Night Gargoyle",
    "monster_s5_s5_succubus": "Succubus",
    "monster_s5_s5_succubus_pro": "Night Succubus Boss",
    "monster_s5_s5_werewolf": "Werewolf",
    "monster_s5_s5_witch_world": "Moonlit Witch",
    "monster_zombie_boss_electricity": "Saga Electric Zombie Boss",
    "monster_s3_monster_snowleopard_01_s3": "Snow Leopard",
    "monster_s4_s4_konglong_jilong": "Spinosaurus",
    "monster_s4_s4_konglong_jianlong": "Stegosaurus",
    "monster_s4_s4_konglong_bawanglong": "Tyrannosaurus Rex",
    "monster_s4_s4_konglong_sanjiaolong": "Triceratops",
    "monster_s4_s4_konglong_xunmenglong": "Velociraptor",
    "npc_game_wanderingzombie_gpu": "Wandering Zombie Horde",
    "monster_wolf": "Infected Dire Wolf",
    "monster_s3_boss_snowmonster_01_s3": "Frostbane Yeti Boss",
    "monster_zomb_tanka": "Armored Tank Zombie Boss",
    "monster_zombie01": "Regular Zombie",
    "monster_zombie01_women": "Female Regular Zombie",
    "monster_s3_zombie_boss_ice_electricity": "Frost Electric Zombie Boss",
    "monster_zombie_creep": "Crawler Zombie",
    "monster_zombie_dog": "Zombie Hound",
    "monster_zombie_fastwalk": "Runner Zombie",
    "monster_zombie_fatcop": "Infected Riot Officer",
    "monster_zombie_fatcop_r1": "Infected Riot Officer Armored",
    "monster_zombie_greenvenom": "Venom Spitter Zombie",
    "npc_game_zombie_hazmat": "Hazmat Suit Zombie",
    "monster_zombie_slowwalk": "Shambler Zombie",
    "monster_zombie_tank": "Brute Tank Zombie",
    "monster_zombies007_pve": "PVE Mutant Zombie",
    # Blood Hand & Raiders
    "soldier_bloodhand_boss": "Blood Hand Boss",
    "soldier_bloodhand_elite": "Blood Hand Elite",
    "soldier_bloodhand_stooge": "Blood Hand Enforcer",
    "soldier_gangster_snake": "Blood Hand Viper Gangster",
    "soldier_lastdayactor_huairen01": "Outlaw Bandit",
    "soldier_s4_feitu_lv1": "Wasteland Raider Lv 1",
    "soldier_s4_feitu_lv2": "Wasteland Raider Lv 2",
    # Troops & Soldiers
    "soldier_lastdayactor_akman": "Rifleman Trooper",
    "soldier_lastdayactor_akman_soldier": "Armored Rifleman",
    "soldier_nvlieshou_low_@normal": "Female Squad Trooper",
    "soldier_lastdayactor_penhuoqiman": "Flamethrower Trooper",
    "soldier_lastdayactor_gatlingman": "Gatling Gunner",
    "soldier_lastdayactor_hero_chainman": "Chainsaw Heavy Trooper",
    "soldier_lastdayactor_hero_mp5_man": "MP5 Tactical Operator",
    "soldier_lastdayactor_hero_fatcop": "Police Riot Officer",
    "soldier_lastdayactor_@normal": "Male Squad Trooper",
    "soldier_marks": "Marksman Sniper",
    "soldier_lastdayactor_pistolman": "Pistol Scout",
    "soldier_police_male": "Patrol Officer",
    "soldier_soldier_ak": "Assault Rifle Soldier",
    "soldier_soldier_gatling": "Heavy Gatling Soldier",
    "soldier_soldier_low_a": "Infantry Soldier Tier 1",
    "soldier_soldier_low_b": "Infantry Soldier Tier 2",
    "soldier_soldier_low_c": "Infantry Soldier Tier 3",
    "soldier_soldier_low_d": "Infantry Soldier Tier 4",
    "soldier_soldier_santaclaus": "Holiday Santa Trooper",
    "soldier_soldier_winter": "Winter Angler Trooper",
    "soldier_lastdayactor_suit01": "Squad Uniform Tier 1",
    "soldier_lastdayactor_suit02": "Squad Uniform Tier 2",
    "soldier_lastdayactor_suit03": "Squad Uniform Tier 3",
    "soldier_lastdayactor_suit04": "Squad Uniform Tier 4",
    "soldier_hero_uav_man": "Landmine Sapper",
    "soldier_train_soldier": "Garrison Recruit",
    # Vehicles & Tanks
    "environment_decorate_a_vehicle_jijieche_01": "Alliance Rally Truck",
    "environment_map_world_vehicle_s4_vehicle_jialong_s4": "Ankylosaurus War Mount",
    "tank_killer": "Anti-Tank Barricade",
    "environment_map_world_vehicle_s3_a_vehicle_xueqiaoche_shijie": "Arctic Snowmobile Sled",
    "environment_pve_a_vehicle_huoche_pve_01": "Armored Supply Train",
    "environment_decorate_a_vehicle_zhuangjiache_01": "Cheetah Armored Vehicle",
    "environment_decorate_a_vehicle_zhuangjiache_01_guanka": "Cheetah Armored Vehicle PVE",
    "environment_decorate_a_vehicle_zhuangjiache_01_shijie": "Cheetah Armored Vehicle World",
    "environment_decorate_a_vehicle_zhuangjiache_01_formal": "Cheetah Armored Vehicle Showcase",
    "environment_decorate_a_vehicle_motuo_02": "Combat Motorcycle",
    "environment_decorate_a_vehicle_common": "Vehicle Wheel Assembly",
    "environment_decorate_a_vehicle_dajiaoche_01": "Conqueror Bigfoot Truck",
    "environment_decorate_a_vehicle_dajiaoche_01_guanka": "Conqueror Bigfoot Truck PVE",
    "environment_decorate_a_vehicle_dajiaoche_01_shijie": "Conqueror Bigfoot Truck World",
    "environment_pve_a_vehicle_dajiaoche_01_boss": "Conqueror Boss Truck",
    "environment_decorate_a_vehicle_daodanche_zhanshi": "Destroyer Missile Vehicle Showcase",
    "environment_decorate_a_vehicle_daodanche_guanka": "Destroyer Missile Vehicle PVE",
    "environment_decorate_a_vehicle_daodanche_world": "Destroyer Missile Vehicle World",
    "environment_decorate_a_vehicle_huojianche": "Destroyer Rocket Vehicle",
    "environment_decorate_a_vehicle_huojianche_guanka": "Destroyer Rocket Vehicle PVE",
    "environment_decorate_a_vehicle_huojianche_shijie": "Destroyer Rocket Vehicle World",
    "environment_decorate_a_vehicle_huojianche_zhanshi_linshi": "Destroyer Rocket Vehicle Prototype",
    "environment_decorate_a_vehicle_huojianche_guanka_formal": "Destroyer Rocket Vehicle PVE Formal",
    "environment_decorate_a_vehicle_huojianche_shijie_formal": "Destroyer Rocket Vehicle World Formal",
    "environment_decorate_a_vehicle_huojianche_zhanshi_formal": "Destroyer Rocket Vehicle Showcase",
    "environment_decorate_a_vehicle_daodanche_ex_zhanshi": "Destroyer-EX Showcase",
    "environment_decorate_a_vehicle_daodanche_ex_guanka": "Destroyer-EX PVE",
    "environment_decorate_a_vehicle_daodanche_ex_world": "Destroyer-EX World",
    "environment_map_world_vehicle_s4_a_vehicle_dinotruck_01_s4": "Dino Cage Transport Truck 1",
    "environment_map_world_vehicle_s4_a_vehicle_dinotruck_02_s4": "Dino Cage Transport Truck 2",
    "environment_decorate_a_vehicle_guanche_01": "Fuel Tanker Truck",
    "environment_decorate_a_vehicle_tanke_zhanshi_formal": "Hercules Battle Tank Showcase",
    "environment_decorate_a_vehicle_tanke": "Hercules Battle Tank",
    "environment_decorate_a_vehicle_tanke_guanka": "Hercules Battle Tank PVE",
    "environment_decorate_a_vehicle_tanke_guanka_formal": "Hercules Battle Tank PVE Formal",
    "environment_decorate_a_vehicle_tanke_shijie_formal": "Hercules Battle Tank World",
    "environment_decorate_a_vehicle_jeep_guanka": "Combat Jeep PVE",
    "environment_decorate_a_vehicle_kache_01": "Escort Cargo Truck",
    "tank": "Base Battle Tank",
    "environment_map_world_vehicle_s4_vehicle_sanjiaolong_s4": "Triceratops War Mount",
    "environment_world_yunbingche": "World Troop Carrier",
    "environment_decorate_a_vehicle_xingjunche_01": "Troop March Truck",
    "environment_map_world_vehicle_s4_vehicle_bawanglong_s4": "Tyrannosaurus War Mount",
    "vehicle_a_vehicle_camel": "Desert Camel Mount",
    # NPCs & Survivors
    "npc_game_npc_gp_fem01": "Female Shelter Resident 1",
    "npc_game_npc_gp_fem02": "Female Shelter Resident 2",
    "npc_game_npc_gp_npc_gp_fem01": "Female Survivor 1",
    "npc_game_npc_gp_npc_gp_fem02_halloween": "Female Survivor Halloween",
    "npc_game_npc_gp_npc_gp_fem02": "Female Survivor 2",
    "npc_game_npc_gp_npc_gp_fem03": "Female Survivor 3",
    "npc_game_npc_gp_npc_gp_man01": "Male Survivor 1",
    "npc_game_npc_gp_npc_gp_man02": "Male Survivor 2",
    "npc_game_npc_gp_npc_gp_man03": "Male Survivor 3",
    "npc_game_npc_gp_npc_gp_man04": "Male Survivor 4",
    "npc_game_npc_gp_npc_gp_man05": "Male Survivor 5",
    "soldier_rebecca": "Rebecca",
    "npc_game_npc_t1": "Shelter Survivor",
    "npc_game_npc_gp_stick": "Survivor Wooden Club",
    "npc_game_npc_littlegirl": "Survivor Little Girl",
    "soldier_hero_fenhushi": "Survivor Nurse",
    # Weapons
    "soldier_weapon_aa12": "AA12 Combat Shotgun",
    "soldier_weapon_ak47": "AK47 Assault Rifle",
    "soldier_weapon_beaker": "Ava Chemical Beaker",
    "soldier_weapon_blond_gun": "Miranda Dual Pistol",
    "soldier_weapon_bow": "Recurve Hunting Bow",
    "soldier_weapon_boxing_gloves": "Heavy Boxing Gloves",
    "soldier_weapon_butcher_axe": "Butcher Cleaver Axe",
    "soldier_weapon_hero_electricsaw": "Oliveira Chainsaw",
    "soldier_weapon_compound_bow": "Leah Compound Bow",
    "soldier_weapon_crossbow": "Natalie Tactical Crossbow",
    "soldier_weapon_crowbar": "Giselle Steel Crowbar",
    "a_hero_doss_01": "Doss Heavy Weapons",
    "soldier_weapon_dun": "Tactical Riot Shield",
    "soldier_weapon_dianciqiang": "EMP Pulse Rifle",
    "soldier_weapon_diancipao_02": "EMP Rail Cannon",
    "soldier_weapon_fbx": "Melee and Firearm Pack",
    "soldier_weapon_a_weapon_jiatelin": "Gatling Minigun",
    "soldier_weapon_jiatelin_02": "Heavy Gatling Minigun",
    "soldier_weapon_grenade": "Frag Grenade",
    "soldier_weapon_hammer": "War Sledgehammer",
    "soldier_weapon_harley": "Harleyna Mallet",
    "soldier_weapon_penhuoqiang": "Heavy Flamethrower",
    "soldier_weapon_hero_fenhushi_weapon": "Nurse Syringe Gun",
    "soldier_weapon_hero_katana": "Chinatsu Katana",
    "soldier_weapon_hero_rifle": "Tactical Battle Rifle",
    "soldier_weapon_long_spear": "Steel War Spear",
    "soldier_weapon_m202a1flash": "M202A1 Quad Rocket Launcher",
    "soldier_weapon_machinegun": "Scarlett Heavy Machine Gun",
    "soldier_weapon_mine": "Anti-Personnel Landmine",
    "soldier_weapon_mp5": "MP5 Submachine Gun",
    "soldier_weapon_nail_plate": "Spiked Nail Board",
    "soldier_weapon_og_bomb": "Tactical Gas Bomb",
    "soldier_weapon_pistol": "Service Pistol",
    "soldier_weapon_huojiantong": "RPG Rocket Launcher",
    "soldier_weapon_sawfrisbee": "Sawblade Disc Launcher",
    "soldier_weapon_sniper_rifle": "Amelia Sniper Rifle",
    "soldier_weapon_langyabang": "Spiked Kanabo Club",
    "soldier_weapon_spitfire": "Spitfire Flamethrower",
    "soldier_weapon_spy_plane": "Recon Spy Drone",
    "soldier_weapon_suncha_weapon": "Elizabeth Twin Sai",
    "npc_game_npc_weapon_rifle_01": "Survivor Assault Rifle",
    "soldier_weapon_uav": "Combat Quadcopter Drone",
    "soldier_weapon_walkie_talkie": "Tactical Walkie-Talkie",
    "weapon": "Barrel Projectiles and Turrets",
    "soldier_weapon_weapon_m416": "Sophia M416 Rifle",
    "soldier_weapon_widow_spy_weapon": "Isabella Submachine Gun",
    # Buildings & Environment
    "environment_map_world_resource_01_world_daodan_01": "World Missile Silo",
    "environment_map_world_resource_01_world_huoji_01": "World Roast Turkey",
    "environment_map_world_resource_01_world_pijiujie_01": "Oktoberfest Beer Pavilion",
    "environment_map_world_resource_01_world_shengdanjiexueren_01": "World Christmas Snowman",
    "environment_ui_a_gaizhuangche_qizhi_01": "Custom Garage Flag",
    "environment_pve_a_pve_obstacle_01": "Destructible Street Barricade",
    "environment_decorate_a_build_zhucheng_huochezhan": "City Train Station",
    "environment_decorate_pve_a_build_huocheguidao_01": "Railway Track Bridge",
    "barrel": "Barrel Obstacles and Pillars",
    "barrel_new": "Barrel Vaults and Crates",
    "environment_interactive_zawu": "Interactive Street Props",
    "zawu": "Forklift and Cargo Props",
    "environment_pve_a_build_bingkuai_01_pve_s3": "Glacier Ice Block",
    "environment_map_blackearth": "Scorched Black Earth",
    "environment_pve_a_build_caihongmen_01": "Festival Rainbow Arch",
    "characters": "Sandbag Bunker Props",
    "environment_decorate_a_build_dajinghui": "Police Crest Emblem",
    "environment_pve_a_build_danqiping_pve_01_s3": "Nitrous Boost Cylinder",
    "environment_pve_a_build_danyaoxiang_pvp_01": "PVP Ammunition Crate",
    "environment_decorate_a_build_daotajianzhu_01": "Collapsed Building Ruin",
    "environment_map_decorate": "Highway Road Segments",
    "environment_decorate_a_build_deng": "Ultraviolet Streetlamp",
    "environment_decorate_a_build_dengall": "Streetlight Set",
    "environment_pve_a_build_diamond_pve_01_s3": "Frost Diamond Crystal",
    "environment_pve_a_build_dianju_pve_01": "Rotary Sawblade Trap",
    "environment_pve_a_build_dici_01_pve_s3": "Frost Spike Trap",
    "environment_decorate_dizuo": "Showcase Display Pedestal",
    "environment_decorate_a_build_dragoncastle": "Dragon Castle",
    "environment_decorate_a_build_duihuanjuan": "Redemption Ticket",
    "environment_decorate_duijiangquan": "Prize Voucher",
    "environment": "Barrel Roadblocks and Traps",
    "environment_interactive_box": "Ammo and Cash Loot Boxes",
    "environment_interactive_feixu": "Interactive Rubble Debris",
    "environment_plant_a_plant_shu": "Woodland Tree",
    "environment_plant_shugan": "Campground Tree Stump",
    "environment_plant_shulin": "Forest Canopy Terrain",
    "environment_plant_yuanshu": "Distant Treeline",
    "hongyoutong": "Explosive Red Fuel Barrel",
    "environment_decorate_fangche": "Survivor RV Camper",
    "environment_decorate_a_build_feiqiche_01": "Wrecked Street Cars",
    "environment_decorate_a_build_bianduijianzhu": "Troop Formation Yard",
    "environment_decorate_a_build_fuzaizhongxin": "Load Capacity Center",
    "environment_decorate_a_build_guajijianglidian": "Idle Reward Supply Truck",
    "environment_decorate_a_build_guantou_01": "Canned Ration Prop",
    "environment_decorate_a_build_gusi_01": "Classic Luxury Sedan",
    "environment_decorate_a_build_haishanglaji": "Floating Ocean Salvage",
    "environment_decorate_a_build_halloween_dragon": "Halloween Bone Dragon",
    "environment_decorate_a_build_daben_01": "Headquarters Tier 1 Ruin",
    "environment_decorate_a_build_daben_01_new": "Headquarters Tier 1",
    "environment_decorate_a_build_daben_02": "Headquarters Tier 2 Exterior",
    "environment_decorate_a_build_daben_02_new": "Headquarters Tier 2 Interior",
    "environment_decorate_a_build_daben_03": "Headquarters Tier 3 Exterior",
    "environment_decorate_a_build_daben_03_new": "Headquarters Tier 3 Interior",
    "environment_decorate_a_build_dabenjianzhu": "Headquarters Complex",
    "environment_decorate_a_build_dabenfeixulumian_01": "Headquarters Ruined Road",
    "environment_decorate_a_build_dabenlumian_01": "Headquarters Paved Plaza",
    "environment_world_hex": "World Territory Hex Grid",
    "environment_decorate_a_build_gaojiaqiao_01": "Highway Overpass",
    "environment_decorate_pve_a_build_gaojiaqiao_01": "PVE Highway Overpass",
    "environment_decorate_a_build_zhensuofeixu_01_timeline": "Ruined Field Clinic",
    "environment_pve_a_build_houche_duanqiao_pve_01": "Bus Station Broken Bridge",
    "environment_pve_a_build_houche_feiche_pve_01": "Bus Station Wrecked Bus",
    "environment_pve_a_build_houche_guanggaopai_pve_01": "Bus Station Billboard",
    "environment_pve_a_build_houche_house_pve_02": "Bus Station Ruined Shop",
    "environment_pve_a_build_houche_house_pve_03": "Bus Station Overgrown House",
    "environment_pve_a_build_houche_ludeng_pve_01": "Bus Station Streetlamp",
    "environment_pve_a_build_houche_trafficlight_pve_01": "Bus Station Traffic Light",
    "environment_pve_a_build_house_01_pve": "PVE Suburban Houses",
    "environment_decorate_huodui": "Survivor Campfire",
    "environment_decorate_a_build_huoji_01": "Thanksgiving Roast Turkey",
    "environment_map_world_huoshanyan_ground": "Volcanic Basalt Ground",
    "environment_decorate_a_build_jianzaojiazi_new": "Construction Scaffolding",
    "environment_decorate_a_build_jianzaolihe_01": "Building Upgrade Crate",
    "environment_decorate_a_build_jianzaowanchengxiangzi": "Completed Building Crate",
    "environment_decorate_jianzaoxiangzhi": "Construction Timber Box",
    "environment_decorate_a_build_jifenpai": "Scoreboard Display",
    "environment_pve_a_build_jinbi_pve_01_s3": "Everfrost Gold Coin",
    "environment_decorate_a_build_jingjichang": "Combat Arena",
    "environment_decorate_a_build_jinxiangzi_01": "Golden Supply Chest",
    "environment_decorate_a_build_jiuba": "Ruined Tavern Bar",
    "environment_decorate_juminqu_build": "Residential Street",
    "environment_decorate_a_build_jundao_01": "Combat Bowie Knife",
    "environment_decorate_a_build_junshizhongxin": "Military Center Baseplate",
    "environment_decorate_a_build_kaifupifu": "Grand Opening HQ Skin",
    "environment_decorate_a_build_kuangdian_sj": "World Ore Deposit",
    "environment_decorate_a_build_laji": "Debris Ground Patch",
    "environment_world_lajixiang_sj": "World Street Dumpster",
    "environment_decorate_a_build_leida": "Radar Dish Ruin",
    "environment_decorate_a_build_leidajiuyuan_01": "Radar Rescue Compound",
    "environment_decorate_a_build_lianmengzhongxin": "Alliance Center Baseplate",
    "environment_decorate_a_build_louti_01": "Concrete Stairwell",
    "environment_decorate_a_build_luntai_01": "Tire Barricade",
    "environment_decorate_luzhang": "Wooden Street Barricade",
    "environment_decorate_a_build_luzhangdici_01": "Spike Strip Barricade",
    "environment_decorate_a_build_miehuowurenji_01": "Firefighting Drone",
    "environment_decorate_a_build_jiaochang_01": "Parade Drill Ground Ruin",
    "environment_decorate_a_build_jiaochang_01_new": "Military Center",
    "environment_decorate_a_build_minju": "Abandoned Houses",
    "environment_decorate_a_build_miwuqiao_01": "Misty Suspension Bridge",
    "environment_decorate_a_build_miwuqiao_01_s3": "Frozen Suspension Bridge",
    "environment_decorate_a_build_motorcycle_01": "Parked Motorcycle",
    "environment_decorate_a_build_nongchang": "Crop Farm",
    "npc_game": "Survivor Crowd Stand-Ins",
    "environment_decorate_o_env_chenneilu": "Inner Shelter Road",
    "environment_decorate_o_env_diji_01": "Barricade Foundation",
    "environment_decorate_o_env_lumian": "Shelter Sidewalk",
    "environment_decorate_a_build_beer_cat": "Oktoberfest Beer Cat HQ",
    "environment_decorate_a_build_chengwailumian_01_s3": "Snowy Outskirts Road",
    "environment_decorate_a_build_chengwailumian_01": "Outskirts Cracked Road",
    "environment_decorate_a_build_chengwailumianwanzheng_01": "Outskirts Intact Highway",
    "environment_decorate_a_build_chengwaidalou_01": "Outskirts Highrise Ruin",
    "overlord_environment_overlord_dinasour_101_hq_world": "Overlord HQ Enclosure Stage 1",
    "overlord_environment_overlord_dinasour_102_hq": "Overlord HQ Enclosure Stage 2",
    "overlord_environment_overlord_dinasour_103_hq": "Overlord HQ Enclosure Stage 3",
    "overlord_environment_overlord_dinasour_104_hq_world": "Overlord HQ Enclosure Stage 4",
    "overlord_environment_overlord_dinasour_105_hq_world": "Overlord HQ Enclosure Stage 5",
    "overlord_environment_overlord_dinasour_106_hq_world": "Overlord HQ Enclosure Stage 6",
    "environment_decorate_a_build_pingban_01": "Tactical Command Tablet",
    "environment_decorate_pve_a_build_chengmen_posun_01": "Breached Fortress Gate",
    "environment_decorate_pve_a_build_chengzhen_01": "PVE Town Overpass",
    "environment_decorate_pve_a_build_dalou_01_new": "PVE Office Tower 1",
    "environment_decorate_pve_a_build_dalou_02": "PVE Office Tower 2",
    "environment_decorate_pve_a_build_dalou_03": "PVE Office Tower 3",
    "environment_decorate_pve_a_build_daqiao_skyline_01": "Skyline Suspension Bridge",
    "environment_decorate_pve_a_build_pve_feixu_01": "PVE Collapsed Ruins",
    "environment_decorate_pve_a_build_shuiniluzhang_01": "Concrete Jersey Barrier",
    "environment_pve_pve_dianjuxianjing_01": "Chainsaw Corridor Trap",
    "environment_pve_pve_lihezuhe_01": "Holiday Gift Pile",
    "environment_pve_pve_shengdanshuzhuangshi_01": "Christmas Tree Ornaments",
    "environment_pve_pve_snowman_01": "Festive Snowman",
    "environment_decorate_a_build_qiche": "Rusted Sedan Wreck",
    "environment_decorate_a_build_qiganshengqi_01": "Alliance Flagpole",
    "environment_decorate_qizi": "Banner Cloth Plane",
    "environment_decorate_a_build_qizi_01": "War Banner Pennant",
    "environment_map_world_s3": "Everfrost Ice Plains",
    "environment_map_world_resource_s3_a_build_changmao_s3_01": "Frozen Spear Monument",
    "environment_map_world_resource_s3_a_build_snowball_s3_01": "World Snowball Node",
    "environment_map_world_resource_s3_o_worldmap_bingku_01_s3": "Glacier Ice Cavern",
    "environment_map_world_resource_s3_world_ice_01": "Arctic Iceberg Peaks",
    "environment_map_world_s4_mountain": "Prehistoric Dino Lake",
    "environment_map_world_resource_s5": "Moonlit Castle Ruin",
    "environment_map_world_s5_mountain": "Moonlit Gothic Peaks",
    "environment_map_saiji_shamo_moutains": "Desert Canyon Mountains",
    "environment_decorate_shan": "Craggy Cliffside",
    "environment_decorate_a_build_shangjingonghui_01": "Bounty Guild Baseplate",
    "environment_map_shanmai": "Distant Mountain Ridge",
    "soldier_item_drink01": "Energy Drink Bottles",
    "soldier_item_feed": "Animal Feed Sack",
    "environment_decorate_a_build_shijiejianzhu": "World Treasure Vault",
    "environment_decorate_a_build_shijiezaiju_01": "Convoy Escort Carriage",
    "environment_decorate_a_build_shiyanshi_01": "Research Laboratory",
    "environment_decorate_a_build_shouchongzhanche": "Vanguard War Chariot",
    "environment_decorate_shuini_dimian": "Concrete Yard Slab",
    "environment_decorate_a_build_shuyao_01": "Twisted Treant Statue",
    "environment_decorate_a_build_ronglianchang_01": "Smelting Plant",
    "environment_pve_a_build_snowball_pve_s3_01": "Rolling Snowball Hazard",
    "environment_decorate_a_build_quanjilong_01_s3": "Snowy Boxing Ring",
    "environment_decorate_a_build_quanjilong_01": "Boxing Ring Arena",
    "environment_decorate_a_build_kache_01": "Cargo Truck Debris",
    "environment_decorate_a_build_canting": "Survivor Canteen",
    "environment_decorate_a_build_paiqian": "Dispatch Center Baseplate",
    "environment_decorate_tengman": "Overgrown Shrubs",
    "environment_map_terrain_slg_new02": "World Terrain Mesh",
    "environment_pve_a_build_tiejuma_01_pve_s3": "Frozen Tank Traps",
    "environment_decorate_a_build_tieqiao_01": "Entrenching Shovel",
    "environment_pve_a_build_tiesiwangdamen_01_pve": "Barbed Wire Security Gate",
    "environment_decorate_a_build_tongyongfeixu": "Ruined Brick Building",
    "environment_decorate_a_build_tongyongfeixu_s3": "Snowy Ruined Building",
    "environment_ui_a_build_trainstation_01": "Metro Train Platform",
    "baoxiang": "Armored Strongbox",
    "environment_decorate_a_build_tujibingying": "Assault Barracks",
    "environment_decorate_a_build_chengwaidiangan_01": "Utility Power Poles",
    "environment_decorate_a_build_valentine_fox": "Valentine Fox HQ",
    "environment_decorate_a_build_cheku": "Vehicle Garage Tier 1",
    "environment_scenedisplay_zhanshicheku": "Vehicle Showroom Hangar",
    "environment_decorate_a_build_cheku_02": "Vehicle Garage Tier 2",
    "environment_decorate_a_build_cheku_02_feixu": "Ruined Vehicle Garage",
    "environment_decorate_a_build_villa": "Survivor Luxury Villa",
    "environment_decorate_a_build_weilan": "Sandbag Perimeter Fence",
    "environment_decorate_a_build_weilan_01_new": "Shelter Defense Wall",
    "environment_decorate_a_build_weilan_01_new_posun": "Damaged Defense Wall",
    "environment_pve_a_build_weilan_01_pve_s3": "Snowy Perimeter Fence",
    "environment_decorate_a_build_weilan_02": "Chainlink Security Gate 2",
    "environment_decorate_a_build_weilan_03": "Chainlink Security Gate 3",
    "environment_decorate_a_build_weilu_01": "Warmth Brazier Furnace",
    "environment_decorate_a_build_whitebear_a_hq": "Bear Wick HQ Tier 1",
    "environment_decorate_a_build_whitebear_a_world": "Bear Wick World Tier 1",
    "environment_decorate_a_build_whitebear_b_hq": "Bear Wick HQ Tier 2",
    "environment_decorate_a_build_whitebear_b_world": "Bear Wick World Tier 2",
    "environment_decorate_a_build_whitebear_common": "Bear Wick Pedestal",
    "environment_decorate_a_build_mucaichang": "Lumber Mill Ruin",
    "environment_decorate_wodejia": "Shelter Ground Plot",
    "environment_decorate_a_build_wurenchengmen": "Unmanned Outpost Gate",
    "environment_decorate_a_build_xiangzi": "Wooden Cargo Crates",
    "environment_decorate_a_build_xiaojinghui": "Small Police Crest",
    "environment_map_xindibiao_zhiwu": "Meadow Flowers and Grass",
    "environment_pve_a_build_xitieshi_pve_01_s3": "Magnet Powerup",
    "environment_decorate_a_build_xunlianchangfeixu_01": "Ruined Training Grounds",
    "environment_decorate_a_build_xunlianchangfeixu_s3_01": "Snowy Training Grounds",
    "environment_pve_a_build_yanti_01_s3": "Snowy Cover Barricade",
    "environment_decorate_a_build_yaoshi_01": "Golden Vault Key",
    "environment_decorate_a_build_yiji_01": "Outpost Ruins 1",
    "environment_decorate_a_build_yiji_03": "Outpost Ruins 3",
    "environment_decorate_a_build_yiji_04": "Outpost Ruins 4",
    "environment_decorate_a_build_yingxiongyihui": "Hero Council Chamber",
    "environment_decorate_a_build_yiyuan_01": "Shelter Medical Hospital",
    "environment_decorate_a_build_yurenjiexiaochoupifu_01": "Joker Clown HQ",
    "environment_decorate_a_build_yurenjiexiaochoupifu_01_s3": "Snowy Joker Clown HQ",
    "environment_decorate_zhalan": "Fortified Palisade Wall",
    "environment_decorate_a_build_zhangaixiangzi_01": "Barricade Supply Box",
    "environment_decorate_a_build_zhangpeng": "Field Command Tent",
    "environment_decorate_a_build_zhanlipaizi": "Combat Power Signboard",
    "environment_decorate_a_build_zhensuo": "Shelter First-Aid Clinic",
    "environment_decorate_a_build_zhishengji_01": "Evacuation Helicopter",
    "environment_decorate_a_build_zhucheng_nanguashouban": "Pumpkin Mascot Statue",
    "environment_decorate_a_build_zhucheng_qicheshouban": "Racer Mascot Statue",
    "environment_decorate_a_build_zhucheng_xiaoxiongshouban": "Teddy Mascot Statue",
    "environment_decorate_a_build_zhucheng_xiarishouban": "Summer Mascot Statue",
    "environment_decorate_a_build_zhuchengchengmen": "Main Shelter Gate",
    "environment_decorate_a_build_zhuchengjianzhu": "Wind Turbine Generator",
    "environment_decorate_a_build_zhuchengjianzhu_03": "Hero Equipment Forge",
    "environment_decorate_a_build_zhuchengjianzhu_04": "Rose Garden Fountain",
    "environment_decorate_a_build_zhuchengjingguan": "Shelter Guard Watchtower",
    "environment_decorate_a_build_zhuchengzhuangshi_01": "Shelter Plaza Statue",
    "environment_decorate_zuhelaji": "Urban Street Clutter",
}


def strip_em_dashes(text: str) -> str:
    if not text:
        return ""
    return text.replace("\u2014", " - ").replace("&" + "mdash;", " - ")


def clean_display_name(name: str, max_len: int = 50) -> str:
    """Clean a display/folder/GLB name: spaces allowed, zero underscores, zero em dashes."""
    s = strip_em_dashes(str(name or ""))
    s = s.replace("_", " ")
    s = re.sub(r'[<>:"/\\|?*]+', " ", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    if not s:
        s = "Model"
    if len(s) > max_len:
        cut = s[:max_len].rsplit(" ", 1)[0].strip()
        s = cut if len(cut) >= 12 else s[:max_len].strip()
    assert "_" not in s and "\u2014" not in s
    return s


def clean_asset_token(name: str, max_len: int = 52) -> str:
    """
    Convert an internal mesh/material/texture identifier to a clean hyphen-separated
    ASCII filename stem with ZERO underscores and ZERO spaces (100% OBJ/MTL parser safe).
    """
    s = strip_em_dashes(str(name or ""))
    s = (
        s.replace("ú", "u")
        .replace("Ú", "U")
        .replace("é", "e")
        .replace("á", "a")
        .replace("í", "i")
        .replace("ó", "o")
    )
    s = s.replace("_", "-")
    s = re.sub(r"[^A-Za-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "Part"
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    assert "_" not in s and " " not in s and "\u2014" not in s
    return s


def load_hero_seasons(repo_dir: Path) -> Dict[int, Dict[str, Any]]:
    """Load official hero season and awakening_season from aps new heroes.json."""
    p = repo_dir / "megamind" / "raw" / "xml tables" / "aps new heroes.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    cols = data["columns"]
    rows_raw = data["rows"]
    rows = list(rows_raw.values()) if isinstance(rows_raw, dict) else rows_raw

    hero_seasons: Dict[int, Dict[str, Any]] = {}
    for r in rows:
        rd = r if isinstance(r, dict) else dict(zip(cols, r))
        hid_s = str(rd.get("id", "")).strip()
        if not hid_s.isdigit():
            continue
        hid = int(hid_s)
        s_raw = str(rd.get("season", "0") or "0").strip()
        season_num = int(s_raw) if s_raw.isdigit() else 0
        aw_raw = str(rd.get("awakening_season", "") or "").strip()
        aw_season: Optional[int] = None
        if aw_raw and "|" in aw_raw:
            first = aw_raw.split("|", 1)[0].strip()
            if first.isdigit():
                aw_season = int(first)
        elif aw_raw.isdigit() and int(aw_raw) > 0:
            aw_season = int(aw_raw)
        hero_seasons[hid] = {
            "season": season_num,
            "awakening_season": aw_season,
            "awakening_raw": aw_raw,
        }
    return hero_seasons


def resolve_season(model: Dict[str, Any], hero_seasons: Dict[int, Dict[str, Any]]) -> Tuple[str, str]:
    """Resolve (Season Folder, Evidence Source) for an extracted 3D model."""
    hid = model.get("hero_id")
    eng_old = str(model.get("english_name", ""))
    slug = str(model.get("slug", "")).lower()

    # 1. Playable Heroes & Companions via aps new heroes.json
    if hid is not None and int(hid) in hero_seasons:
        hs = hero_seasons[int(hid)]
        if "awakened" in eng_old.lower() and hs["awakening_season"]:
            s_num = hs["awakening_season"]
            return (
                f"Season {s_num}",
                f"aps new heroes.json(id={hid}, awakening_season='{hs['awakening_raw']}')",
            )
        s_num = hs["season"]
        if s_num <= 0:
            return ("Pre-Season 1", f"aps new heroes.json(id={hid}, season=0)")
        return (f"Season {s_num}", f"aps new heroes.json(id={hid}, season={s_num})")

    # 2. Season 5 (Moonlit Elegy) monsters, bosses, and world mountains/resources
    if re.search(r"(^|_)s5($|_)", slug) or "worlds5" in slug:
        return ("Season 5", f"APS monster.json / building.json / Moonlit Elegy S5 bundle({slug})")

    # 3. Season 4 (Dinosaur Origin) dinosaurs, dino trucks, desert bandits, lake mountains
    if re.search(r"(^|_)s4($|_)", slug) or "konglong" in slug or "dinotruck" in slug:
        return ("Season 4", f"APS monster.json / decoration.json(season=4) / Dinosaur Origin S4 bundle({slug})")

    # 4. Season 3 (Everfrost Era) glacier bosses, snow beasts, snowmobiles, icy structures
    if re.search(r"(^|_)s3($|_)", slug) or slug.startswith("monster_s3_"):
        return ("Season 3", f"APS monster.json / building.json / Everfrost Era S3 bundle({slug})")

    # 5. Season 2 (Wastes Watcher) desert mountain & camel expedition assets
    if "saiji_shamo" in slug or slug == "vehicle_a_vehicle_camel":
        return ("Season 2", f"aps_season.json(Wastes Watcher) / desert.json desert bundle({slug})")

    # 6. Explicit s1 / s2 standalone tokens (guarded against building/tier numbers)
    if re.search(r"(^|_)(season1|seasons1)($|_)", slug):
        return ("Season 1", f"Season 1 bundle token({slug})")
    if re.search(r"(^|_)(season2|seasons2)($|_)", slug):
        return ("Season 2", f"Season 2 bundle token({slug})")

    # 7. Core / Launch game models
    return ("Pre-Season 1", "Core launch / base game 3D model bundle")


def resolve_clean_model_name(model: Dict[str, Any]) -> str:
    """Resolve concise, underscore-free real English display name for a model."""
    slug = str(model.get("slug", ""))
    if model.get("faction") in ("Blood_Rose", "Wings_of_Dawn", "Guard_of_Order"):
        return clean_display_name(model["english_name"], max_len=48)
    if slug in EXACT_SLUG_NAMES:
        return clean_display_name(EXACT_SLUG_NAMES[slug], max_len=48)
    # Fallback cleanup of existing English name
    raw = str(model.get("english_name", "") or slug)
    raw = re.sub(r"\((?:0[1-9]|S[1-6]|WORLD|PVE|FORMAL|\s)+\)", "", raw).strip()
    return clean_display_name(raw, max_len=48)


def rewrite_obj_and_mtl(
    src_dir: Path,
    dst_dir: Path,
    model: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """
    Copy/rename textures, rewrite materials.mtl and *.obj files so ZERO underscores
    exist in any filename or material identifier and 100% of MTL/OBJ links match.
    """
    dst_tex_dir = dst_dir / "textures"
    dst_tex_dir.mkdir(parents=True, exist_ok=True)

    # 1. Rename textures/*.png (underscore-free hyphenated stems)
    old_to_new_tex_rel: Dict[str, str] = {}
    used_tex_stems: Dict[str, int] = {}
    new_textures_meta: List[Dict[str, Any]] = []

    for t_entry in model.get("textures", []):
        old_rel = str(t_entry["file"])
        src_png = src_dir / old_rel
        raw_stem = Path(old_rel).stem
        clean_stem = clean_asset_token(raw_stem, max_len=48)
        low_s = clean_stem.lower()
        if low_s in used_tex_stems:
            used_tex_stems[low_s] += 1
            clean_stem = f"{clean_stem}-{used_tex_stems[low_s]}"
        else:
            used_tex_stems[low_s] = 1
        new_fname = f"{clean_stem}.png"
        new_rel = f"textures/{new_fname}"
        shutil.copy2(src_png, dst_tex_dir / new_fname)
        old_to_new_tex_rel[old_rel] = new_rel
        new_textures_meta.append(
            {
                "name": strip_em_dashes(t_entry["name"]),
                "file": new_rel,
                "width": t_entry["width"],
                "height": t_entry["height"],
                "unpacked_dxt5nm": t_entry.get("unpacked_dxt5nm", False),
            }
        )

    # 2. Map old material identifiers -> underscore-free material identifiers
    old_to_new_mat: Dict[str, str] = {}
    used_mat_names: Dict[str, int] = {}
    for ml in model.get("material_texture_links", []):
        old_m = str(ml["material"])
        if old_m in old_to_new_mat:
            continue
        clean_m = clean_asset_token(old_m, max_len=48)
        low_m = clean_m.lower()
        if low_m in used_mat_names:
            used_mat_names[low_m] += 1
            clean_m = f"{clean_m}-{used_mat_names[low_m]}"
        else:
            used_mat_names[low_m] = 1
        old_to_new_mat[old_m] = clean_m

    # 3. Rewrite materials.mtl
    src_mtl = src_dir / "materials.mtl"
    mtl_lines_out: List[str] = []
    if src_mtl.exists():
        for line in src_mtl.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("newmtl "):
                old_m = stripped.split(None, 1)[1].strip()
                new_m = old_to_new_mat.get(old_m) or clean_asset_token(old_m, max_len=48)
                old_to_new_mat[old_m] = new_m
                mtl_lines_out.append(f"newmtl {new_m}\n")
            elif stripped.startswith(("map_Kd ", "map_Bump ", "bump ")):
                cmd, old_tpath = stripped.split(None, 1)
                old_tpath = old_tpath.strip()
                new_tpath = old_to_new_tex_rel.get(old_tpath, old_tpath)
                mtl_lines_out.append(f"{cmd} {new_tpath}\n")
            else:
                mtl_lines_out.append(strip_em_dashes(line) + "\n")
    (dst_dir / "materials.mtl").write_text("".join(mtl_lines_out), encoding="utf-8")

    new_mat_links: List[Dict[str, Any]] = []
    for ml in model.get("material_texture_links", []):
        old_d = ml.get("diffuse_texture")
        old_n = ml.get("normal_texture")
        new_mat_links.append(
            {
                "material": old_to_new_mat.get(ml["material"], clean_asset_token(ml["material"])),
                "unity_material_name": strip_em_dashes(ml.get("unity_material_name", "")),
                "diffuse_texture": old_to_new_tex_rel.get(old_d) if old_d else None,
                "normal_texture": old_to_new_tex_rel.get(old_n) if old_n else None,
            }
        )

    # 4. Rename and rewrite every *.obj file
    used_obj_stems: Dict[str, int] = {}
    new_meshes_meta: List[Dict[str, Any]] = []
    exported_files: List[str] = []

    for m_rec in model.get("meshes", []):
        old_obj_name = str(m_rec["obj_file"])
        src_obj = src_dir / old_obj_name
        raw_stem = Path(old_obj_name).stem
        # Clean ugly Unity clone/LOD tokens in OBJ stem if present
        raw_stem_clean = re.sub(r"Clone[_-]*Quality[_-]*\d+", "LOD", raw_stem, flags=re.I)
        clean_stem = clean_asset_token(raw_stem_clean, max_len=48)
        low_o = clean_stem.lower()
        if low_o in used_obj_stems:
            used_obj_stems[low_o] += 1
            clean_stem = f"{clean_stem}-{used_obj_stems[low_o]}"
        else:
            used_obj_stems[low_o] = 1
        new_obj_name = f"{clean_stem}.obj"

        obj_out: List[str] = []
        for line in src_obj.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("usemtl "):
                old_m = line[7:].strip()
                new_m = old_to_new_mat.get(old_m) or clean_asset_token(old_m, max_len=48)
                obj_out.append(f"usemtl {new_m}\n")
            elif line.startswith("o "):
                obj_out.append(f"o {clean_stem}\n")
            elif line.startswith("g "):
                g_tok = clean_asset_token(line[2:].strip(), max_len=56)
                obj_out.append(f"g {g_tok}\n")
            elif line.startswith("mtllib "):
                obj_out.append("mtllib materials.mtl\n")
            else:
                obj_out.append(line + "\n")

        (dst_dir / new_obj_name).write_text(strip_em_dashes("".join(obj_out)), encoding="utf-8")
        exported_files.append(new_obj_name)

        new_meshes_meta.append(
            {
                "name": strip_em_dashes(m_rec["name"]),
                "obj_file": new_obj_name,
                "vertices": m_rec["vertices"],
                "faces": m_rec["faces"],
                "submeshes": m_rec["submeshes"],
                "included_in_glb": m_rec["included_in_glb"],
                "materials": [old_to_new_mat.get(x, clean_asset_token(x)) for x in m_rec.get("materials", [])],
            }
        )

    exported_files.append("materials.mtl")
    return new_meshes_meta, new_mat_links, new_textures_meta, exported_files


def write_clean_catalogs_and_readme(
    models_dir: Path,
    models_list: List[Dict[str, Any]],
    skipped_bundles: List[Dict[str, Any]],
    verified_glbs: List[Dict[str, Any]],
    elapsed_sec: float,
) -> None:
    """Write Models Catalog.json, Models Catalog.csv, and README.md with zero underscores in filenames."""
    active_seasons = [s for s in SEASON_ORDER if any(m["season"] == s for m in models_list)]

    season_faction_matrix: Dict[str, Dict[str, int]] = {
        s: {f: 0 for f in FACTION_ORDER} for s in active_seasons
    }
    season_totals: Dict[str, Dict[str, int]] = {
        s: {"models": 0, "glbs": 0, "objs": 0, "textures": 0, "vertices": 0, "faces": 0}
        for s in active_seasons
    }
    faction_totals: Dict[str, Dict[str, int]] = {
        f: {"models": 0, "glbs": 0, "objs": 0, "textures": 0, "vertices": 0, "faces": 0}
        for f in FACTION_ORDER
    }

    for m in models_list:
        s = m["season"]
        f = m["faction"]
        season_faction_matrix[s][f] += 1
        for bucket in (season_totals[s], faction_totals[f]):
            bucket["models"] += 1
            bucket["glbs"] += 1 if m.get("glb_file") else 0
            bucket["objs"] += m["mesh_count"]
            bucket["textures"] += m["texture_count"]
            bucket["vertices"] += m["total_vertices"]
            bucket["faces"] += m["total_faces"]

    summary = {
        "scanned_bundles": len(models_list) + len(skipped_bundles),
        "exported_model_bundles": len(models_list),
        "skipped_no_mesh_bundles": len(skipped_bundles),
        "active_seasons": active_seasons,
        "total_glbs": sum(b["glbs"] for b in season_totals.values()),
        "total_objs": sum(b["objs"] for b in season_totals.values()),
        "total_textures": sum(b["textures"] for b in season_totals.values()),
        "total_vertices": sum(b["vertices"] for b in season_totals.values()),
        "total_faces": sum(b["faces"] for b in season_totals.values()),
        "reorg_elapsed_seconds": round(elapsed_sec, 2),
    }

    hero_table = [
        {
            "season": m["season"],
            "faction": m["faction"],
            "camp_id": m["camp_id"],
            "hero_id": m["hero_id"],
            "english_name": m["english_name"],
            "folder": m["folder"],
            "glb_file": m["glb_file"],
            "meshes": m["mesh_count"],
            "textures": m["texture_count"],
            "faces": m["total_faces"],
            "season_source": m["season_source"],
            "evidence_source": m["evidence_source"],
        }
        for m in models_list
        if m["faction"] in ("Blood Rose", "Wings of Dawn", "Guard of Order")
    ]

    catalog = {
        "summary": summary,
        "seasons": season_totals,
        "factions": faction_totals,
        "season_by_faction_counts": season_faction_matrix,
        "hero_to_season_faction_table": hero_table,
        "verified_glb_samples": verified_glbs,
        "models": models_list,
        "skipped_bundles": skipped_bundles,
    }

    json_text = strip_em_dashes(json.dumps(catalog, indent=2, ensure_ascii=False))
    assert "\u2014" not in json_text
    (models_dir / "Models Catalog.json").write_text(json_text, encoding="utf-8")

    # CSV
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf, lineterminator="\n")
    writer.writerow(
        [
            "Season",
            "Faction",
            "Camp ID",
            "Hero ID",
            "Model Name",
            "Folder",
            "GLB File",
            "Mesh Count",
            "Texture Count",
            "Total Vertices",
            "Total Faces",
            "Animation Count",
            "Season Source",
            "Source Bundle",
        ]
    )
    for m in models_list:
        writer.writerow(
            [
                m["season"],
                m["faction"],
                "" if m["camp_id"] is None else m["camp_id"],
                "" if m["hero_id"] is None else m["hero_id"],
                m["english_name"],
                m["folder"],
                m["glb_file"] or "",
                m["mesh_count"],
                m["texture_count"],
                m["total_vertices"],
                m["total_faces"],
                len(m["animation_clips"]),
                m["season_source"],
                m["source_bundle"],
            ]
        )
    csv_text = strip_em_dashes(csv_buf.getvalue())
    assert "\u2014" not in csv_text
    (models_dir / "Models Catalog.csv").write_text(csv_text, encoding="utf-8")

    # README.md
    md: List[str] = [
        "# Last Z: Survival Shooter - Season and Faction 3D Model Archive\n\n",
        "Complete 3D model collection extracted from Last Z AssetBundles, organized by **Season** ",
        "(`Pre-Season 1` through `Season 5`) and **Official Faction**, with clean space-separated English names, ",
        "zero underscores in any folder or filename, self-contained textured `.glb` files, ",
        "and Wavefront `.obj` + `materials.mtl` + `.png` textures.\n\n",
        "## Archive Totals\n\n",
        f"- **Directory Layout:** `models/<Season>/<Faction>/<Clean Model Name>/`\n",
        f"- **3D Models Exported:** {summary['exported_model_bundles']} / {summary['exported_model_bundles']} (100% GLB coverage)\n",
        f"- **Self-Contained `.glb` Scenes:** {summary['total_glbs']}\n",
        f"- **Sub-Mesh `.obj` Files:** {summary['total_objs']:,}\n",
        f"- **Exported `.png` Textures:** {summary['total_textures']:,}\n",
        f"- **Total Geometry:** {summary['total_vertices']:,} vertices / {summary['total_faces']:,} triangles\n",
        f"- **Skipped Non-Mesh Bundles:** {summary['skipped_no_mesh_bundles']} (audio, 2D sprites, animation-only, cubemaps)\n\n",
        "## Season Summary\n\n",
        "| Season | Theme | Models | GLBs | OBJs | Textures | Vertices | Triangles |\n",
        "|---|---|---:|---:|---:|---:|---:|---:|\n",
    ]
    for s in active_seasons:
        st = season_totals[s]
        md.append(
            f"| `{s}` | {SEASON_THEMES.get(s, '')} | {st['models']} | {st['glbs']} | {st['objs']:,} | "
            f"{st['textures']:,} | {st['vertices']:,} | {st['faces']:,} |\n"
        )
    md.append(
        f"| **TOTAL** | **All Seasons** | **{summary['exported_model_bundles']}** | **{summary['total_glbs']}** | "
        f"**{summary['total_objs']:,}** | **{summary['total_textures']:,}** | "
        f"**{summary['total_vertices']:,}** | **{summary['total_faces']:,}** |\n\n"
    )

    md.append("## Season x Faction Breakdown\n\n")
    hdr_factions = " | ".join(FACTION_ORDER)
    sep_factions = " | ".join(["---:"] * len(FACTION_ORDER))
    md.append(f"| Season | {hdr_factions} | Total |\n")
    md.append(f"|---| {sep_factions} |---:|\n")
    for s in active_seasons:
        row_vals = [str(season_faction_matrix[s][f]) for f in FACTION_ORDER]
        md.append(f"| `{s}` | {' | '.join(row_vals)} | **{season_totals[s]['models']}** |\n")
    col_totals = [str(faction_totals[f]["models"]) for f in FACTION_ORDER]
    md.append(f"| **Total** | {' | '.join(col_totals)} | **{summary['exported_model_bundles']}** |\n\n")

    md.append("## Playable Heroes by Season and Faction\n\n")
    md.append("| Season | Faction | Hero ID | Hero Name | Folder Path | GLB File | Meshes | Triangles |\n")
    md.append("|---|---|---:|---|---|---|---:|---:|\n")
    for h in hero_table:
        md.append(
            f"| `{h['season']}` | `{h['faction']}` | {h['hero_id']} | **{h['english_name']}** | "
            f"`{h['folder']}` | `{h['glb_file']}` | {h['meshes']} | {h['faces']:,} |\n"
        )

    md.append("\n## Verified `.glb` Spot-Checks Across All Seasons\n\n")
    md.append("| Season | Faction | Model | GLB Path | Submeshes | Vertices | Faces |\n")
    md.append("|---|---|---|---|---:|---:|---:|\n")
    for vg in verified_glbs:
        md.append(
            f"| `{vg['season']}` | `{vg['faction']}` | {vg['english_name']} | `{vg['glb_path']}` | "
            f"{vg['geometries']} | {vg['vertices']:,} | {vg['faces']:,} |\n"
        )

    readme_text = strip_em_dashes("".join(md))
    assert "\u2014" not in readme_text
    (models_dir / "README.md").write_text(readme_text, encoding="utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    t0 = time.time()

    repo_dir = DEFAULT_REPO_DIR
    models_dir = repo_dir / "models"

    old_cat_path = models_dir / "models_catalog.json"
    new_cat_path = models_dir / "Models Catalog.json"
    if old_cat_path.exists():
        cat_data = json.loads(old_cat_path.read_text(encoding="utf-8"))
    elif new_cat_path.exists():
        cat_data = json.loads(new_cat_path.read_text(encoding="utf-8"))
    else:
        raise FileNotFoundError("No existing models catalog found in models/")

    old_models: List[Dict[str, Any]] = cat_data["models"]
    skipped_bundles: List[Dict[str, Any]] = cat_data.get("skipped_bundles", [])
    logging.info("Loaded %d verified 3D models from catalog.", len(old_models))

    hero_seasons = load_hero_seasons(repo_dir)

    # Stage clean build in a temporary directory next to models/ (inside models/.staging-reorg)
    staging_dir = models_dir / ".staging-reorg"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Pre-sort by vertex count descending so highest-detail variant claims primary name on collision
    enriched: List[Tuple[str, str, str, str, Dict[str, Any]]] = []
    for m in old_models:
        season_name, season_src = resolve_season(m, hero_seasons)
        raw_fac = str(m["faction"])
        clean_fac = FACTION_CLEAN_MAP.get(raw_fac, raw_fac.replace("_", " "))
        base_clean_name = resolve_clean_model_name(m)
        enriched.append((season_name, clean_fac, base_clean_name, season_src, m))

    enriched.sort(
        key=lambda item: (
            SEASON_ORDER.index(item[0]) if item[0] in SEASON_ORDER else 99,
            FACTION_ORDER.index(item[1]) if item[1] in FACTION_ORDER else 99,
            item[2].lower(),
            -int(item[4].get("total_vertices", 0)),
        )
    )

    used_model_names: Dict[Tuple[str, str, str], int] = {}
    new_models_list: List[Dict[str, Any]] = []

    for season_name, clean_fac, base_name, season_src, m in enriched:
        key = (season_name.lower(), clean_fac.lower(), base_name.lower())
        if key in used_model_names:
            used_model_names[key] += 1
            final_name = f"{base_name} ({used_model_names[key]})"
        else:
            used_model_names[key] = 1
            final_name = base_name

        assert "_" not in final_name and "\u2014" not in final_name

        src_folder = models_dir / m["folder"]
        dst_folder = staging_dir / season_name / clean_fac / final_name
        dst_folder.mkdir(parents=True, exist_ok=True)

        # 1. Copy/rename GLB
        old_glb = m.get("glb_file")
        new_glb_name: Optional[str] = None
        if old_glb and (src_folder / old_glb).exists():
            new_glb_name = f"{final_name}.glb"
            shutil.copy2(src_folder / old_glb, dst_folder / new_glb_name)

        # 2. Copy/rename textures and rewrite OBJ + MTL with zero underscores
        new_meshes, new_mat_links, new_texs, exp_files = rewrite_obj_and_mtl(
            src_dir=src_folder,
            dst_dir=dst_folder,
            model=m,
        )
        if new_glb_name:
            exp_files.append(new_glb_name)
        exp_files.extend([t["file"] for t in new_texs])
        exp_files.append("model-info.json")

        rel_folder = f"{season_name}/{clean_fac}/{final_name}"
        new_info = {
            "season": season_name,
            "season_source": strip_em_dashes(season_src),
            "faction": clean_fac,
            "camp_id": m.get("camp_id"),
            "hero_id": m.get("hero_id"),
            "model_name": final_name,
            "english_name": final_name,
            "slug": m.get("slug", ""),
            "evidence_source": strip_em_dashes(str(m.get("evidence_source", ""))),
            "source_bundle": m["source_bundle"],
            "folder": rel_folder,
            "glb_file": new_glb_name,
            "glb_submesh_count": m.get("glb_submesh_count", 0),
            "glb_errors": m.get("glb_errors", []),
            "mesh_count": len(new_meshes),
            "texture_count": len(new_texs),
            "total_vertices": m["total_vertices"],
            "total_faces": m["total_faces"],
            "meshes": new_meshes,
            "material_texture_links": new_mat_links,
            "textures": new_texs,
            "animation_clips": [strip_em_dashes(a) for a in m.get("animation_clips", [])],
            "exported_files": exp_files,
        }
        info_txt = strip_em_dashes(json.dumps(new_info, indent=2, ensure_ascii=False))
        assert "\u2014" not in info_txt
        (dst_folder / "model-info.json").write_text(info_txt, encoding="utf-8")
        new_models_list.append(new_info)

    # Sort final catalog by Season order -> Faction order -> English Name
    new_models_list.sort(
        key=lambda item: (
            SEASON_ORDER.index(item["season"]) if item["season"] in SEASON_ORDER else 99,
            FACTION_ORDER.index(item["faction"]) if item["faction"] in FACTION_ORDER else 99,
            item["english_name"].lower(),
        )
    )

    # Pre-swap integrity verification inside staging!
    st_glbs = list(staging_dir.rglob("*.glb"))
    st_objs = list(staging_dir.rglob("*.obj"))
    st_mtls = list(staging_dir.rglob("materials.mtl"))
    st_pngs = list(staging_dir.rglob("*.png"))
    st_infos = list(staging_dir.rglob("model-info.json"))
    logging.info(
        "Staging verified: models=%d, glbs=%d, objs=%d, mtls=%d, pngs=%d",
        len(st_infos),
        len(st_glbs),
        len(st_objs),
        len(st_mtls),
        len(st_pngs),
    )
    assert len(st_infos) == len(old_models) == 482
    assert len(st_glbs) == 482
    assert len(st_mtls) == 482
    assert len(st_objs) == 3035
    assert len(st_pngs) == 3287

    # Swap cleanly: remove everything in models/ except .staging-reorg, then move Season dirs out
    for child in list(models_dir.iterdir()):
        if child.name == ".staging-reorg":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    for season_child in list(staging_dir.iterdir()):
        shutil.move(str(season_child), str(models_dir / season_child.name))
    staging_dir.rmdir()

    # Verify GLB loading across every active season
    verified_glbs: List[Dict[str, Any]] = []
    active_seasons = [s for s in SEASON_ORDER if any(m["season"] == s for m in new_models_list)]
    for s in active_seasons:
        s_models = [m for m in new_models_list if m["season"] == s and m.get("glb_file")]
        for sample_m in s_models[:3]:
            gp = models_dir / sample_m["folder"] / sample_m["glb_file"]
            sc = trimesh.load(gp, force="scene")
            verts = int(sum(len(g.vertices) for g in sc.geometry.values()))
            faces = int(sum(len(g.faces) for g in sc.geometry.values()))
            if verts <= 0 or faces <= 0:
                raise RuntimeError(f"Zero geometry in verified GLB: {gp}")
            verified_glbs.append(
                {
                    "season": s,
                    "faction": sample_m["faction"],
                    "english_name": sample_m["english_name"],
                    "glb_path": f"{sample_m['folder']}/{sample_m['glb_file']}",
                    "geometries": len(sc.geometry),
                    "vertices": verts,
                    "faces": faces,
                }
            )

    elapsed = time.time() - t0
    write_clean_catalogs_and_readme(
        models_dir=models_dir,
        models_list=new_models_list,
        skipped_bundles=skipped_bundles,
        verified_glbs=verified_glbs,
        elapsed_sec=elapsed,
    )

    logging.info("Season + Clean Name reorganization completed in %.2fs!", elapsed)
    for s in active_seasons:
        cnt = sum(1 for m in new_models_list if m["season"] == s)
        logging.info("  %-14s : %3d models", s, cnt)


if __name__ == "__main__":
    main()
