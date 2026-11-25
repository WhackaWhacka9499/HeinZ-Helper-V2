# Volume 06: HeinZ Control Hub API Routes, Web UI DOM & Bot Engine Architecture

> **Generated:** `2026-11-23 10:42:43 UTC` | **Source:** AST & DOM extraction of `LastZ-PC-Master-Overhaul` -> `megamind/raw/heinz_architecture.json`

## 1. HeinZ Platform Architecture Summary

| Component | Verified Count | Primary Source File |
|---|---:|---|
| `HubBackend` Public RPC Endpoints | **30** | `launcher/heinz_hub_web.py` (5,586 lines) |
| Action Dispatch Routes (`action_id`) | **51** | `HubBackend.run_action` / `trigger_action` |
| `TASK_CATALOG` Automation Cards | **25** | `launcher/heinz_hub_web.py` |
| Frontend Views / Modals | **7** Views / **5** Modals | `launcher/web/index.html` (4,925 lines) |
| Frontend Interactive Buttons | **107** | `launcher/web/index.html` |
| Frontend Inputs / Selects | **17** Inputs / **12** Selects | `launcher/web/index.html` |
| Frontend JavaScript Functions | **98** | Inline JS in `launcher/web/index.html` |
| `doAction(...)` Routes Called from UI | **42** | `pywebview.api` calls: **9** |
| Canonical Sequential Stages / Tasks | **5** Stages / **29** Tasks | `tools/multi client bot.py` |
| Bot Engine Action Functions | **74** | `tools/bot actions.py` (13,398 lines) |
| Total Repository Files | **123** | `LastZ-PC-Master-Overhaul/` |

## 2. Complete `HubBackend` RPC API Reference (`launcher/heinz_hub_web.py`)

| RPC Endpoint (`window.pywebview.api.<method>`) | Arguments | Lines | Description |
|---|---|---|---|
| `set_window` | `self, win` | `L1148-L1149` | - |
| `log` | `self, msg, kind, category, is_tip` | `L1199-L1271` | - |
| `clear_logs` | `self` | `L1289-L1292` | - |
| `start_monitors` | `self` | `L1294-L1297` | - |
| `toggle_always_on_daemon` | `self, enabled` | `L1574-L1603` | - |
| `toggle_hospital_watcher` | `self, target, enabled` | `L1605-L1643` | - |
| `toggle_alliance_help_watcher` | `self, enabled` | `L1645-L1667` | - |
| `toggle_alliance_tech_watcher` | `self, enabled` | `L1669-L1690` | - |
| `find_script` | `self, name` | `L2632-L2650` | - |
| `find_file` | `self, name` | `L2652-L2664` | - |
| `inspect_setup` | `self, base_dir` | `L3027-L3028` | - |
| `ensure_daemon_running` | `self` | `L3246-L3263` | - |
| `get_state` | `self` | `L3296-L3325` | - |
| `select_target_client` | `self, choice` | `L3327-L3366` | - |
| `save_bot_config` | `self, payload` | `L3368-L3414` | - |
| `save_event_rules` | `self, rules_payload` | `L3416-L3432` | - |
| `browse_folder` | `self` | `L3434-L3442` | - |
| `query_map_targets` | `self, search, category, max_results` | `L3444-L3520` | Search accumulated bases and seasonal tiles from CSV cache for instant UI display. |
| `jump_to_coordinate` | `self, x, y, server_id` | `L3522-L3540` | Snap in-game camera to specific map coordinates in the active Last Z client. |
| `get_account_inventory` | `self, pid, force_live` | `L3542-L3777` | Fetch and return categorized, visually formatted inventory items for target client. |
| `get_tech_calculator_data` | `self, pid, force_live` | `L3797-L3993` | Calculate invested and remaining courage badges per tier and whole tree, with live client sync. |
| `get_migration_calculator_data` | `self, state_id, player_query` | `L3995-L4154` | Return migration score, pass costs, tier matrix, and top alliance rosters for target state. |
| `quick_shield` | `self, pid` | `L4156-L4238` | Activate a peace shield immediately from bag using passive Lua invocation. |
| `quick_recall` | `self, pid` | `L4240-L4284` | Recall all gathering or field marches back to base immediately. |
| `get_troops_overview` | `self, pid, force_live` | `L4286-L4481` | Extract or retrieve cached drill ground troops, formations, and hospital wounded status. |
| `get_alliance_deltas` | `self, state_id, force_snapshot` | `L4483-L4602` | Compute power deltas, member shifts, and rank movements across state alliances. |
| `get_presets` | `self` | `L4604-L4614` | Load saved automation presets from data/bot_presets.json. |
| `save_preset` | `self, name, tasks, desc` | `L4616-L4636` | Save current task configuration as a named preset. |
| `delete_preset` | `self, name` | `L4638-L4656` | Delete a custom preset from data/bot_presets.json. |
| `run_action` | `self, action_id, payload` | `L4658-L4770` | - |

## 3. Complete Action Dispatch Routes (`action_id` - 51 Routes)

| `action_id` | Line | Payload Keys |
|---|---:|---|
| `toggle_always_on_daemon` | 4660 | `desc`, `dry_run`, `enabled`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `target`, `task`, `tasks` |
| `toggle_hospital_watcher` | 4664 | `desc`, `dry_run`, `enabled`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `target`, `task`, `tasks` |
| `toggle_alliance_help_watcher` | 4669 | `desc`, `dry_run`, `enabled`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `target`, `task`, `tasks` |
| `toggle_alliance_tech_watcher` | 4673 | `desc`, `dry_run`, `enabled`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `target`, `task`, `tasks` |
| `run_single_task` | 4677 | `desc`, `dry_run`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `target`, `task`, `tasks` |
| `quick_shield` | 4679 | `desc`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `tasks` |
| `quick_recall` | 4681 | `desc`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `tasks` |
| `get_troops_overview` | 4683 | `desc`, `force_live`, `force_snapshot`, `name`, `pid`, `state_id`, `tasks` |
| `get_alliance_deltas` | 4685 | `desc`, `force_snapshot`, `name`, `state_id`, `tasks` |
| `get_presets` | 4687 | `desc`, `name`, `tasks` |
| `save_preset` | 4689 | `desc`, `name`, `tasks` |
| `delete_preset` | 4691 | `name` |
| `open_inventory_excel` | 4693 | - |
| `open_google_roster` | 4704 | - |
| `open_scratch_folder` | 4708 | - |
| `open_data_folder` | 4711 | - |
| `open_vs_excel` | 4716 | - |
| `open_all_bases` | 4719 | - |
| `open_all_resources` | 4722 | `state` |
| `open_unshielded_excel` | 4725 | `state` |
| `open_active_migration` | 4728 | `state` |
| `export_top10` | 4741 | `state` |
| `open_selected_bracket_state` | 4754 | `state` |
| `open_bracket_folder` | 4765 | - |
| `apply_engine` | 4789 | - |
| `flush_ram` | 4795 | - |
| `run_always_on_sweep_now` | 4803 | - |
| `restart_daemon` | 4815 | - |
| `export_inventory` | 4823 | - |
| `export_tech` | 4836 | - |
| `export_vs` | 4844 | - |
| `export_roster` | 4850 | - |
| `export_alliance_members` | 4863 | `lvl_str`, `res_type` |
| `export_map` | 4872 | `lvl_str`, `res_type` |
| `open_map_summary` | 4885 | `lvl_str`, `res_type` |
| `export_mines` | 4931 | `base_dir` |
| `scan_fleet` | 4937 | `base_dir` |
| `setup_base_install` | 4954 | `base_dir`, `label`, `mode`, `wait_xlua` |
| `launch_single_client` | 4980 | `label`, `mode`, `wait_xlua` |
| `stop_single_client` | 5003 | `label`, `mode` |
| `sync_farm_builds` | 5012 | `mode` |
| `launch_all_farms` | 5031 | `mode` |
| `stop_all_farms` | 5109 | `create_shortcut`, `exe_name`, `label`, `launch_after`, `main_game_dir`, `profile`, `root_dir` |
| `provision_farm` | 5125 | `create_shortcut`, `exe_name`, `label`, `launch_after`, `main_game_dir`, `profile`, `root_dir` |
| `run_bot_cycle` | 5159 | `dry_run`, `scope` |
| `run_single_task` | 5212 | `dry_run`, `target`, `task` |
| `start_bot_daemon` | 5355 | - |
| `stop_bot_daemon` | 5362 | - |
| `install_bot_task` | 5368 | - |
| `uninstall_bot_task` | 5373 | - |
| `sync_google_bracket` | 5378 | - |

## 4. `TASK_CATALOG` Cards (25 Cards)

| Task Key | Title | Category | Tag | Description |
|---|---|---|---|---|
| `alliance_daily` | Alliance Red Packets & Tasks | Daily Care & Alliance | `Packets + Task Boxes` | Grabs alliance red packets and collects finished alliance task & exploit milestone boxes. (Alliance Te... |
| `radar_events` | Radar Events (Scan + All Types) | Daily Care & Alliance | `Scan + All 4 Types` | Triggers the top-left radar scan button first, claims finished rewards, and handles ALL radar task typ... |
| `daily_tasks_complete` | Daily Tasks (Complete All) | Daily Care & Alliance | `One-Go Auto-Complete` | Scans your live Daily Tasks popup and completes ALL actionable tasks in one go (Post Likes, Hero EXP, ... |
| `daily_claims` | Daily Tasks & Passes | Daily Care & Alliance | `Tasks + Chests + Passes` | Claims all completed Daily Tasks, Daily Activity Milestone Chests (1-6), achievements, chapter tasks, ... |
| `vip_store_rewards` | VIP & Store Freebies | Daily Care & Alliance | `Daily Rewards` | Collects your daily VIP login points, VIP freebies chest, and the free reward in the 2nd tab of the St... |
| `war_safety` | War Safety Guard | Protection & War | `Shield + Recall` | Watches for incoming enemy marches on your base or resource tiles, pulls exposed gathering squads home... |
| `rf_hq_under_attack` | Reinforce Attacked Allies | Protection & War | `Defense` | Sends reinforcement troops to alliance members or protected accounts when their base comes under attack. |
| `arena` | Arena Battles (x5) | Combat & Events | `70%+ Win Odds` | Builds 1v1 or 3v3 pure-faction top-5 hero lineups, skips tough fights, and only challenges opponents w... |
| `hero_battlefield` | Hero Battlefield (Quick Deploy + Auto... | Combat & Events | `Quick Deploy • Auto-Skip` | Uses Quick Deploy / Sweep where unlocked, auto-fills strongest faction heroes, and immediately trigger... |
| `area_exploration` | Area Exploration (Auto-Skip) | Combat & Events | `HQ Solo • Auto-Skip` | Collects idle stage chest rewards, executes batch jumps, and runs solo HQ Explore battles with automat... |
| `furylord` | Furylord Boss (03:00) | Combat & Events | `Squad 1 x4` | Targets the scheduled 03:00 Furylord window using Squad 1 so all daily boss damage rewards are secured... |
| `tyrant_event` | Tyrant Rally | Combat & Events | `F1 Host + Join` | Claims free Tyrant rewards, hosts a Squad 1 rally, joins open alliance Tyrant rallies with extra squad... |
| `boomer_runs` | Boomer Rallies | Combat & Events | `Auto-Join + Host` | Joins open alliance Boomer rallies or starts new ones within your stamina reserve for hero EXP and ral... |
| `mining_event` | Mining Event (Mon / Tue) | Combat & Events | `Lv7 Empty Nodes` | Looks for unoccupied XP or Gold event mines on Mondays and Tuesdays so farms gather event rewards safe... |
| `alliance_boss_mine` | Bear Trap & Alliance Mine | Combat & Events | `Event + Gather` | Claims Bear Trap rewards when available, joins active Bear battles, and keeps an idle squad gathering ... |
| `treasure_helicopter` | Treasure Helicopter | Progression & Farming | `Map Dig` | Claims helicopter supply drops and marches squads to active treasure digs nearby. |
| `research_queue` | Research Queue | Progression & Farming | `Tech Lab` | Collects completed technologies, starts recommended or priority research automatically, applies free s... |
| `free_recruits` | Free Recruits & Safe Chests | Progression & Farming | `Timer + Drops Only` | Uses strictly free timer hero recruits and opens safe non-choice drop chests in your bag without touch... |
| `garage_upgrades` | Garage Upgrades (Monday) | Progression & Farming | `Mondays Only` | Every Monday, equips stronger APC vehicle parts, merges matching parts, and performs free refits for e... |
| `full_preparedness` | Full Preparedness | Progression & Farming | `Milestone Boxes` | Collects Full Preparedness point chests and aligns timed progression actions with active daily event w... |
| `speedups` | Smart Speedups | Progression & Farming | `Main: Free Only` | Hits free speedup buttons as soon as timers drop into the free window; on farms, optionally spends sma... |
| `troop_training` | Train Troops (Event Speed-Zoom) | Progression & Farming | `All Barracks • FP/VS Zoom` | Collects finished soldiers, trains your highest unlocked tier across all barracks, and automatically s... |
| `building_upgrades` | Upgrade HQ & Buildings | Progression & Farming | `HQ Priority` | Harvests city resources, starts HQ or required prerequisite buildings when builders are free, and requ... |
| `bounties` | Gold Bounties (Lock Orange + Ally Hel... | Progression & Farming | `3-in-1 • Lock Orange` | Unified 3-in-1 bounty engine: locks Orange/Gold missions before rolling, dispatches all golden bountie... |
| `trucks` | Trade Trucks (Claim + Send Gold) | Progression & Farming | `Claim + Roll Gold` | Claims completed golden/old trade trucks first, waits for server sync, rolls for golden trucks, dispat... |

## 5. 5-Stage Sequential Bot State Machine (`tools/multi client bot.py`)

| Stage | Key | Name | Cooldown (s) | Pacing (s) | Preempt | Canonical Tasks |
|---:|---|---|---:|---:|---|---|
| **1** | `stage_1_war_safety` | War Safety & Emergency Shields | 0.0 | 0.6 | YES | `war_safety`, `rf_hq_under_attack` |
| **2** | `stage_2_casualty_recovery` | Casualty Recovery & Hospital | 15.0 | 0.6 | no | `hospital_heal` |
| **3** | `stage_3_resource_gathering` | Resource Gathering & Mine Melee Refresh | 30.0 | 0.8 | no | `mine_melee_refresh`, `mining_event`, `alliance_boss_mine` |
| **4** | `stage_4_base_production` | Base Production & Upgrades | 20.0 | 0.8 | no | `troop_training`, `building_upgrades`, `research_queue`, `garage_upgrades`, `speedups` |
| **5** | `stage_5_alliance_dailies` | Alliance & Dailies | 30.0 | 0.5 | no | `auto_help`, `alliance_daily`, `radar_events`, `treasure_helicopter`, `trucks`, `bounties`, `bounty_steal`, `arena`, `hero_battlefield`, `area_exploration`, `boomer_runs`, `furylord`, `tyrant_event`, `full_preparedness`, `vip_store_rewards`, `free_recruits`, `daily_tasks_complete`, `daily_claims` |

### Default Daemon Configuration (`DEFAULT_CONFIG`)
```json
{
  "version": 2,
  "cycle_interval_seconds": 180,
  "inter_client_delay_seconds": 1.5,
  "auto_launch_stopped_clients": false,
  "auto_launch_mode": "eco",
  "discovered_protected_uids": [],
  "stage_machine": {
    "enabled": true,
    "enforce_cooldowns": true,
    "preempt_on_attack": true,
    "strict_emergency_preempt": true,
    "inter_stage_delay_seconds": 0.6,
    "inter_task_delay_seconds": 0.25,
    "verify_client_between_stages": true,
    "include_extended_tasks": false,
    "stage_cooldowns_seconds": {
      "1": 0.0,
      "2": 15.0,
      "3": 30.0,
      "4": 20.0,
      "5": 30.0
    }
  },
  "schedule": {
    "task_name": "LastZ_MultiClient_Bot",
    "legacy_task_names": [],
    "interval_minutes": 15,
    "auto_launch_in_task": true,
    "launch_mode": "hidden"
  },
  "client_defaults": {
    "main": {
      "enabled": true,
      "role": "main",
      "launch_mode": "windowed",
      "formation_reserve": 1,
      "min_stamina": 120,
      "tasks": {
        "auto_help": true,
        "rf_hq_under_attack": true,
        "treasure_helicopter": true,
        "full_preparedness": true,
        "speedups": true,
        "troop_training": true,
        "building_upgrades": true,
        "tyrant_event": true,
        "boomer_runs": true,
        "auto_gather": true,
        "mine_melee_refresh": true,
        "furylord": true,
        "bounties": true,
        "bounty_steal": true,
        "trucks": true,
        "mining_event": true,
        "vip_store_rewards": true,
        "sync_ruby_shop": true,
        "area_exploration": true,
        "hero_battlefield": true,
        "arena": true,
        "war_safety": true,
        "hospital_heal": true,
        "alliance_daily": true,
        "research_queue": false,
        "radar_events": true,
        "daily_tasks_complete": true,
        "daily_claims": true,
        "free_recruits": false,
        "garage_upgrades": false,
        "alliance_boss_mine": true
      },
      "always_on_daemon": {
        "enabled": true,
        "interval_sec": 15
      },
      "auto_help": {
        "always_on": true,
        "interval_sec": 15,
        "help_allies": true,
        "call_help_queues": true,
        "claim_alliance_chests": true
      },
      "speedups": {
        "use_free_speed": true,
        "collect_finished": true,
        "use_items": false,
        "align_with_preparedness": true,
        "reserve_minutes": 600,
        "max_items_per_cycle": 5,
        "categories": {
          "build": true,
          "research": true,
          "train": false,
          "heal": true
        }
      },
      "troop_training": {
        "collect_finished": true,
        "train_highest_tier": true,
        "barracks": [
          "CarSoldier",
          "FootSoldier",
          "BowSoldier"
        ],
        "batch_count": 0,
        "event_speed_zoom": true,
        "max_zoom_batches": 50,
        "zoom_use_universal_speedups": false
      },
      "building_upgrades": {
        "collect_resources": true,
        "hq_priority": true,
        "auto_prerequisites": true,
        "call_alliance_help": true,
        "priority_building_types": [
          400000,
          403000,
          423000,
          424000,
          425000,
          411000
        ]
      },
      "auto_gather": {
        "resource_priority": [
          "Oil",
          "Metal",
          "Wood",
          "Electricity"
        ],
        "min_level": 3,
        "max_level": 9,
        "max_distance": 150,
        "formation_index": 0
      },
      "mine_melee_refresh": {
        "refresh_threshold_sec": 300,
        "min_payload_pct": 10.0,
        "reserve_formations": 1,
        "alliance_mine_priority": true,
        "recall_depleted": true
      },
      "boomer_runs": {
        "join_open_rallies": true,
        "auto_start_rally": true,
        "min_level": 1,
        "max_level": 5,
        "rally_wait_minutes": 5,
        "stamina_cost": 20,
        "min_stamina": 120
      },
      "tyrant_event": {
        "claim_free_reward": true,
        "claim_alliance_reward": true,
        "join_or_attack": true,
        "prefer_rally": true,
        "f1_always_host_rally": true,
        "other_formations_join_rallies": true,
        "repeat_when_free": true,
        "fast_repeat_sec": 10
      },
      "rf_hq_under_attack": {
        "reinforce_protected_uids": true,
        "reinforce_alliance_members": true,
        "alert_on_self_attack": true,
        "auto_shield_on_self_attack": false,
        "max_incoming_eta_seconds": 900
      },
      "treasure_helicopter": {
        "march_to_dig": true,
        "auto_claim_chat_treasures": true,
        "jitter_min_ms": 110,
        "jitter_max_ms": 240,
        "burst_clicks": 6,
        "lead_window_seconds": 2.0
      },
      "full_preparedness": {
        "execute_tasks": true,
        "claim_boxes": true,
        "claim_daily_quests": true,
        "claim_daily_chests": true
      },
      "furylord": {
        "exact_hour": 3,
        "exact_minute": 0,
        "window_minutes": 20,
        "max_attacks": 4,
        "formation_index": 1,
        "prefer_rally": true,
        "claim_rewards": true
      },
      "bounties": {
        "only_golden": true,
        "lock_orange": true,
        "help_allies_golden": true,
        "plunder_bounties": true,
        "min_color": 4,
        "use_free": true,
        "use_tickets": true,
        "use_diamonds": false,
        "stop_when_no_free_or_ticket": true,
        "claim_completed": true,
        "max_refreshes_per_cycle": 8,
        "cross_state_only": true,
        "min_level": 5,
        "max_daily_steals": 5,
        "max_servers_scan": 16
      },
      "bounty_steal": {
        "cross_state_only": true,
        "only_golden": true,
        "min_color": 4,
        "min_level": 5,
        "max_daily_steals": 5,
        "max_servers_scan": 16
      },
      "trucks": {
        "daily_sends": 4,
        "slots": [
          {
            "quality": 5,
            "formation": 1
          },
          {
            "quality": 5,
            "formation": 2
          },
          {
            "quality": 5,
            "formation": 3
          },
          {
            "quality": 5,
            "formation": 4
          }
        ],
        "reroll_with_items": true,
        "reroll_with_diamonds": false,
        "max_rerolls_per_truck": 6,
        "claim_completed": true,
        "attack_enabled": true,
        "attack_daily_limit": 4,
        "attack_cross_state_only": true,
        "attack_power_margin_below_f1": 20000000
      },
      "mining_event": {
        "weekdays": [
          0,
          1
        ],
        "mine_type": 2,
        "mine_reward": "xp",
        "mine_level": 7,
        "skip_occupied_players": true,
        "claim_finished": true,
        "max_refreshes": 3
      },
      "vip_store_rewards": {
        "claim_vip_points": true,
        "claim_vip_daily_freebie": true,
        "claim_store_vip_tab_free": true,
        "claim_weekly_gift_freebie": true
      },
      "area_exploration": {
        "claim_hangup_rewards": true,
        "auto_jump": true,
        "auto_battle": true,
        "auto_skip_battle": true,
        "max_battles_per_cycle": 5,
        "stop_on_fail": true
      },
      "hero_battlefield": {
        "auto_prefill_strongest_faction": true,
        "use_quick_deploy": true,
        "auto_skip_battle": true,
        "max_battles_per_faction": 5,
        "stop_on_fail": true,
        "skip_if_failed_this_period": true
      },
      "arena": {
        "max_battles_per_cycle": 5,
        "refresh_opponents": true,
        "auto_free_refresh": true,
        "pure_faction_teams": true,
        "pick_weakest": true,
        "min_win_odds_pct": 70,
        "min_power_advantage_ratio": 1.0
      },
      "war_safety": {
        "auto_shield_on_attack": true,
        "respect_war_fever": true,
        "recall_gatherers_on_attack": true,
        "max_eta_seconds": 300
      },
      "hospital_heal": {
        "collect_finished": true,
        "batch_minutes": 30,
        "min_batch_troops": 25,
        "max_batch_troops": 1500,
        "call_alliance_help": true,
        "use_speedups": false,
        "max_speedup_mins": 0,
        "max_chain_batches": 5,
        "persistent_watcher_enabled": false
      },
      "alliance_daily": {
        "donate_tech": true,
        "auto_tech_always_on": true,
        "use_gold_donate": false,
        "claim_gifts": true,
        "claim_red_packets": true,
        "claim_tasks": true
      },
      "research_queue": {
        "prefer_recommended": true,
        "call_alliance_help": true,
        "use_free_speed": true,
        "priority_tabs": [
          5,
          1,
          2,
          3,
          4
        ]
      },
      "radar_events": {
        "trigger_scan": true,
        "claim_finished": true,
        "auto_dispatch": true,
        "auto_skip_battle": true,
        "max_dispatches_per_cycle": 20
      },
      "daily_tasks_complete": {
        "allow_pvp_hq_attack": false
      },
      "daily_claims": {
        "claim_daily_tasks": true,
        "claim_achievements": true,
        "claim_battle_pass": true,
        "claim_chapter_tasks": true
      },
      "free_recruits": {
        "claim_hero_recruits": true,
        "claim_small_people": true,
        "open_safe_chests": true,
        "max_chests_per_cycle": 20
      },
      "garage_upgrades": {
        "only_monday": true,
        "upgrade_refit": true,
        "use_refit_free_only": true,
        "install_better_components": true,
        "merge_components": true,
        "max_refit_steps_per_cycle": 5
      },
      "alliance_boss_mine": {
        "bear_claim_rewards": true,
        "bear_donate": false,
        "bear_join_or_rally": true,
        "alliance_mine_dispatch": true
      }
    },
    "farm": {
      "enabled": true,
      "role": "farm",
      "launch_mode": "eco",
      "formation_reserve": 0,
      "min_stamina": 60,
      "tasks": {
        "auto_help": true,
        "rf_hq_under_attack": true,
        "treasure_helicopter": true,
        "full_preparedness": true,
        "speedups": true,
        "troop_training": true,
        "building_upgrades": true,
        "tyrant_event": true,
        "boomer_runs": true,
        "auto_gather": true,
        "mine_melee_refresh": true,
        "furylord": true,
        "bounties": true,
        "bounty_steal": true,
        "trucks": true,
        "mining_event": true,
        "vip_store_rewards": true,
        "sync_ruby_shop": true,
        "area_exploration": true,
        "hero_battlefield": true,
        "arena": true,
        "war_safety": true,
        "hospital_heal": true,
        "alliance_daily": true,
        "research_queue": true,
        "radar_events": true,
        "daily_tasks_complete": true,
        "daily_claims": true,
        "free_recruits": true,
        "garage_upgrades": true,
        "alliance_boss_mine": true
      },
      "always_on_daemon": {
        "enabled": true,
        "interval_sec": 15
      },
      "auto_help": {
        "always_on": true,
        "interval_sec": 15,
        "help_allies": true,
        "call_help_queues": true,
        "claim_alliance_chests": true
      },
      "speedups": {
        "use_free_speed": true,
        "collect_finished": true,
        "use_items": true,
        "align_with_preparedness": true,
        "reserve_minutes": 120,
        "max_items_per_cycle": 10,
        "categories": {
          "build": true,
          "research": true,
          "train": false,
          "heal": true
        }
      },
      "troop_training": {
        "collect_finished": true,
        "train_highest_tier": true,
        "barracks": [
          "CarSoldier",
          "FootSoldier",
          "BowSoldier"
        ],
        "batch_count": 0,
        "event_speed_zoom": true,
        "max_zoom_batches": 50,
        "zoom_use_universal_speedups": false
      },
      "building_upgrades": {
        "collect_resources": true,
        "hq_priority": true,
        "auto_prerequisites": true,
        "call_alliance_help": true,
        "priority_building_types": [
          400000,
          403000,
          423000,
          424000,
          425000,
          411000
        ]
      },
      "auto_gather": {
        "resource_priority": [
          "Oil",
          "Metal",
          "Wood",
          "Electricity"
        ],
        "min_level": 3,
        "max_level": 9,
        "max_distance": 150,
        "formation_index": 0
      },
      "mine_melee_refresh": {
        "refresh_threshold_sec": 300,
        "min_payload_pct": 10.0,
        "reserve_formations": 0,
        "alliance_mine_priority": true,
        "recall_depleted": true
      },
      "boomer_runs": {
        "join_open_rallies": true,
        "auto_start_rally": true,
        "min_level": 1,
        "max_level": 5,
        "rally_wait_minutes": 5,
        "stamina_cost": 20,
        "min_stamina": 120
      },
      "tyrant_event": {
        "claim_free_reward": true,
        "claim_alliance_reward": true,
        "join_or_attack": true,
        "prefer_rally": true,
        "f1_always_host_rally": true,
        "other_formations_join_rallies": true,
        "repeat_when_free": true,
        "fast_repeat_sec": 10
      },
      "rf_hq_under_attack": {
        "reinforce_protected_uids": true,
        "reinforce_alliance_members": true,
        "alert_on_self_attack": true,
        "auto_shield_on_self_attack": true,
        "max_incoming_eta_seconds": 900
      },
      "treasure_helicopter": {
        "march_to_dig": true,
        "auto_claim_chat_treasures": true,
        "jitter_min_ms": 110,
        "jitter_max_ms": 240,
        "burst_clicks": 6,
        "lead_window_seconds": 2.0
      },
      "full_preparedness": {
        "execute_tasks": true,
        "claim_boxes": true,
        "claim_daily_quests": true,
        "claim_daily_chests": true
      },
      "furylord": {
        "exact_hour": 3,
        "exact_minute": 0,
        "window_minutes": 20,
        "max_attacks": 4,
        "formation_index": 1,
        "prefer_rally": true,
        "claim_rewards": true
      },
      "bounties": {
        "only_golden": true,
        "lock_orange": true,
        "help_allies_golden": true,
        "plunder_bounties": true,
        "min_color": 4,
        "use_free": true,
        "use_tickets": true,
        "use_diamonds": false,
        "stop_when_no_free_or_ticket": true,
        "claim_completed": true,
        "max_refreshes_per_cycle": 8,
        "cross_state_only": true,
        "min_level": 5,
        "max_daily_steals": 5,
        "max_servers_scan": 16
      },
      "bounty_steal": {
        "cross_state_only": true,
        "only_golden": true,
        "min_color": 4,
        "min_level": 5,
        "max_daily_steals": 5,
        "max_servers_scan": 16
      },
      "trucks": {
        "daily_sends": 4,
        "slots": [
          {
            "quality": 5,
            "formation": 1
          },
          {
            "quality": 5,
            "formation": 2
          },
          {
            "quality": 5,
            "formation": 3
          },
          {
            "quality": 5,
            "formation": 4
          }
        ],
        "reroll_with_items": true,
        "reroll_with_diamonds": false,
        "max_rerolls_per_truck": 6,
        "claim_completed": true,
        "attack_enabled": true,
        "attack_daily_limit": 4,
        "attack_cross_state_only": true,
        "attack_power_margin_below_f1": 20000000
      },
      "mining_event": {
        "weekdays": [
          0,
          1
        ],
        "mine_type": 2,
        "mine_reward": "xp",
        "mine_level": 7,
        "skip_occupied_players": true,
        "claim_finished": true,
        "max_refreshes": 3
      },
      "vip_store_rewards": {
        "claim_vip_points": true,
        "claim_vip_daily_freebie": true,
        "claim_store_vip_tab_free": true,
        "claim_weekly_gift_freebie": true
      },
      "area_exploration": {
        "claim_hangup_rewards": true,
        "auto_jump": true,
        "auto_battle": true,
        "auto_skip_battle": true,
        "max_battles_per_cycle": 5,
        "stop_on_fail": true
      },
      "hero_battlefield": {
        "auto_prefill_strongest_faction": true,
        "use_quick_deploy": true,
        "auto_skip_battle": true,
        "max_battles_per_faction": 5,
        "stop_on_fail": true,
        "skip_if_failed_this_period": true
      },
      "arena": {
        "max_battles_per_cycle": 5,
        "refresh_opponents": true,
        "auto_free_refresh": true,
        "pure_faction_teams": true,
        "pick_weakest": true,
        "min_win_odds_pct": 70,
        "min_power_advantage_ratio": 1.0
      },
      "war_safety": {
        "auto_shield_on_attack": true,
        "respect_war_fever": true,
        "recall_gatherers_on_attack": true,
        "max_eta_seconds": 300
      },
      "hospital_heal": {
        "collect_finished": true,
        "batch_minutes": 30,
        "min_batch_troops": 25,
        "max_batch_troops": 1500,
        "call_alliance_help": true,
        "use_speedups": false,
        "max_speedup_mins": 0,
        "max_chain_batches": 5,
        "persistent_watcher_enabled": false
      },
      "alliance_daily": {
        "donate_tech": true,
        "auto_tech_always_on": true,
        "use_gold_donate": false,
        "claim_gifts": true,
        "claim_red_packets": true,
        "claim_tasks": true
      },
      "research_queue": {
        "prefer_recommended": true,
        "call_alliance_help": true,
        "use_free_speed": true,
        "priority_tabs": [
          5,
          1,
          2,
          3,
          4
        ]
      },
      "radar_events": {
        "trigger_scan": true,
        "claim_finished": true,
        "auto_dispatch": true,
        "auto_skip_battle": true,
        "max_dispatches_per_cycle": 20
      },
      "daily_tasks_complete": {
        "allow_pvp_hq_attack": false
      },
      "daily_claims": {
        "claim_daily_tasks": true,
        "claim_achievements": true,
        "claim_battle_pass": true,
        "claim_chapter_tasks": true
      },
      "free_recruits": {
        "claim_hero_recruits": true,
        "claim_small_people": true,
        "open_safe_chests": true,
        "max_chests_per_cycle": 20
      },
      "garage_upgrades": {
        "only_monday": true,
        "upgrade_refit": true,
        "use_refit_free_only": true,
        "install_better_components": true,
        "merge_components": true,
        "max_refit_steps_per_cycle": 5
      },
      "alliance_boss_mine": {
        "bear_claim_rewards": true,
        "bear_donate": false,
        "bear_join_or_rally": true,
        "alliance_mine_dispatch": true
      }
    }
  },
  "profiles": {}
}
```

## 6. All Bot Engine Action Functions (`tools/bot actions.py` - 74 Functions)

| Function Name | Lines | Parameters | `MsgDefines` Used | `DataCenter` Managers Used | `TableName` / `UIWindowNames` |
|---|---|---|---|---|---|
| `_clean_in_game_tips` | `L21-L36` | `tips` | - | - | - |
| `_load_english_dialog` | `L44-L76` | `` | - | - | - |
| `_localize_id` | `L79-L86` | `val` | - | - | - |
| `_used_formations_lua` | `L725-L729` | `context, pid` | - | - | - |
| `_record_used_formations` | `L732-L739` | `context, pid, uuids` | - | - | - |
| `_normalize_eval_payload` | `L742-L772` | `payload` | - | - | - |
| `_build_detail_lines` | `L775-L1186` | `task_name, res` | - | - | - |
| `_finalize_task_result` | `L1189-L1206` | `task_name, res` | - | - | - |
| `_with_task_telemetry` | `L1209-L1217` | `task_name` | - | - | - |
| `_eval_json` | `L1220-L1234` | `cd, pid, lua_body, timeout` | - | - | - |
| `snapshot_client` | `L1237-L1256` | `cd, pid` | - | StatusManager, WorldPointManager | - |
| `dismiss_all_popups` | `L1259-L1278` | `cd, pid, client_state, cfg, dry_run, context` | - | - | - |
| `ensure_world_scene` | `L1281-L1304` | `cd, pid, wait_seconds` | - | - | - |
| `_lua_claim_alliance_gifts_block` | `L1307-L1499` | `dry_run_var, flag_var` | AllianceGiftGetReward, AllianceReceiveAllGift, ReceiveGiftDail... | AllianceGiftDataManager | - |
| `run_auto_help` | `L1502-L1687` | `cd, pid, client_state, cfg, dry_run, context` | AlHelpAll, AllianceCallHelp, AllianceGiftList | AllianceGiftDataManager, AllianceHelpDataManager, BuildManager, QueueDat... | - |
| `run_rf_hq_under_attack` | `L1690-L1889` | `cd, pid, client_state, cfg, dry_run, context` | ItemUse | AllianceAlertDataManager, ItemData, ItemTemplateManager, RadarAlarmDataM... | - |
| `run_treasure_helicopter` | `L1892-L2103` | `cd, pid, client_state, cfg, dry_run, context` | GetDigTreasureReward, WorldGetDetail | DigTreasureDataManager, WorldPointManager | - |
| `_now_dt` | `L2106-L2109` | `context` | - | - | - |
| `_daily_state_path` | `L2112-L2114` | `context` | - | - | - |
| `_client_key` | `L2117-L2119` | `client_state, pid` | - | - | - |
| `_load_daily_state` | `L2122-L2129` | `path` | - | - | - |
| `_get_daily_count` | `L2132-L2146` | `context, client_state, pid, metric, now_dt` | - | - | - |
| `_increment_daily_count` | `L2149-L2176` | `context, client_state, pid, metric, delta, now_dt` | - | - | - |
| `_probe_preparedness_phase` | `L2179-L2523` | `cd, pid` | ActivityEventInfoGet | ActPersonalArmsInfo, ActTimeCompeDataManager, ActivityListDataManager, A... | - |
| `_detect_training_event_boost` | `L2526-L2630` | `cd, pid, probe` | - | - | - |
| `_try_start_research` | `L2633-L2699` | `cd, pid, dry_run` | ScienceResearchNew | BuildManager, ScienceManager | - |
| `_match_preparedness_actions` | `L2715-L2753` | `probe` | - | - | - |
| `_run_scoped_speedup` | `L2756-L2773` | `cd, pid, client_state, cfg, category, dry_run, context` | - | - | - |
| `_execute_preparedness_actions` | `L2776-L2822` | `cd, pid, client_state, cfg, dry_run, context, probe` | - | - | - |
| `run_full_preparedness` | `L2825-L2879` | `cd, pid, client_state, cfg, dry_run, context` | - | - | - |
| `_claim_full_preparedness` | `L2882-L3029` | `cd, pid, client_state, cfg, dry_run, context` | AcceptPersonalReward, AcceptPersonalRewardBatch | ActPersonalArmsInfo, ActivityController, ActivityListDataManager | - |
| `run_speedups` | `L3032-L3311` | `cd, pid, client_state, cfg, dry_run, context` | BuildCcdMNew, QueueCcdMNew, QueueFinish | ActPersonalArmsInfo, ActivityListDataManager, AllianceCompeteDataManager... | - |
| `run_troop_training` | `L3314-L3863` | `cd, pid, client_state, cfg, dry_run, context` | ArmyAdd, QueueCcdMNew, QueueFinish | ArmyManager, BuildManager, ItemData, ItemTemplateManager, QueueDataManager | - |
| `run_building_upgrades` | `L3866-L4124` | `cd, pid, client_state, cfg, dry_run, context` | AllianceCallHelp, FreeBuildingUpNew | AllianceHelpDataManager, BuildManager, BuildQueueManager, BuildTemplateM... | - |
| `run_tyrant_event` | `L4127-L4308` | `cd, pid, client_state, cfg, dry_run, context` | ReceiveAllianceBossAllianceReward | AllianceBossManager, AllianceWarDataManager, WorldPointManager | - |
| `run_boomer_runs` | `L4311-L4454` | `cd, pid, client_state, cfg, dry_run, context` | FindMonster | AllianceWarDataManager, WorldPointManager | Monster |
| `run_auto_gather` | `L4457-L4615` | `cd, pid, client_state, cfg, dry_run, context` | - | WorldPointManager | GatherResource |
| `run_furylord` | `L4618-L4770` | `cd, pid, client_state, cfg, dry_run, context` | - | ActRoamingBossManager, WorldPointManager | - |
| `run_bounties` | `L4773-L5242` | `cd, pid, client_state, cfg, dry_run, context` | DispatchAssist, DispatchRewardAll, DispatchStart, DispatchTask... | ActDispatchTaskDataManager, ActivityListDataManager, ItemData | LwDispatchTask |
| `run_bounty_steal` | `L5245-L5551` | `cd, pid, client_state, cfg, dry_run, context` | DispatchSteal | ActDispatchTaskDataManager, WorldPointManager | LwDispatchTask |
| `run_trucks` | `L5554-L6027` | `cd, pid, client_state, cfg, dry_run, context` | CollectTrainReward, GetMyStationData | ArmyFormationDataManager, ArmyManager, HeroDataManager, ItemData, LWMySt... | - |
| `run_mining_event` | `L6030-L6541` | `cd, pid, client_state, cfg, dry_run, context` | BeginPvpCaveFight, ClaimMineCaveReward, GetMineCaveInfo, Refre... | ActivityListDataManager, ArmyFormationDataManager, MineCaveManager | - |
| `run_vip_store_rewards` | `L6547-L6682` | `cd, pid, snapshot, ccfg, dry_run, context` | BuyCommonShopGoods, BuyFreeWeeklyPackage | CommonShopManager, VIPManager | - |
| `snapshot_formations_and_gear` | `L6685-L6877` | `cd, pid` | - | ArmyFormationDataManager, ArmyFormationManager, HeroDataManager, HeroEqu... | - |
| `restore_formations_and_gear` | `L6880-L6937` | `cd, pid` | HeroEquipInstall | HeroDataManager, HeroEquipManager | - |
| `run_hero_battlefield` | `L6940-L7489` | `cd, pid, snapshot, ccfg, dry_run, context` | - | ArmyFormationDataManager, ArmyFormationManager, BattleLevel, CarChipMana... | - |
| `_arena_round_win_prob` | `L7492-L7499` | `my_pwr, opp_pwr` | - | - | - |
| `_arena_best_matchup` | `L7502-L7570` | `is_3v3, pure_camps, opp` | - | - | - |
| `run_arena` | `L7573-L8097` | `cd, pid, snapshot, ccfg, dry_run, context` | GetArenaInfo, GetCrossArenaInfo, RefreshArenaChallenge, Refres... | ArenaManager, BattleLevel, CrossArenaManager, HeroDataManager, TowerClim... | - |
| `run_area_exploration` | `L8100-L8410` | `cd, pid, snapshot, ccfg, dry_run, context` | UserStartBarrelPushBatch | BattleLevel, LWBattleManager, StoryManager, TowerClimbingManager | UIJeepAdventureMain, UIPVEResult, UIPVEScene, UIPark... |
| `run_war_safety` | `L8487-L8644` | `cd, pid, client_state, cfg, dry_run, context` | ItemUse | AllianceAlertDataManager, ItemData, ItemTemplateManager, RadarAlarmDataM... | - |
| `run_hospital_heal` | `L8647-L9805` | `cd, pid, client_state, cfg, dry_run, context, use_sp...` | HospitalCure, QueueCcdMNew | ArmyManager, ArmyTemplateManager, HospitalManager, ItemData, QueueDataMa... | - |
| `run_alliance_daily` | `L9811-L10046` | `cd, pid, client_state, cfg, dry_run, context, tech_only` | AlHelpAll, AlScienceDonate, AlScienceGoldDonate, AllianceGiftL... | AlContributeManager, AllianceGiftDataManager, AllianceHelpDataManager, A... | - |
| `run_research_queue` | `L10049-L10176` | `cd, pid, client_state, cfg, dry_run, context` | FreeSpeedQueue, ScienceResearchNew | QueueDataManager, ScienceManager, ScienceTemplateManager | - |
| `_lua_trigger_pve_skip_snippet` | `L10179-L10270` | `` | - | BattleLevel, LWBattleManager | UIPVEScene |
| `_ensure_exited_pve_cleanly` | `L10273-L10326` | `cd, pid, only_if_stuck` | - | BattleLevel, LWBattleManager | UIJeepAdventureMain, UIPVEResult, UIPVEScene, UIPark... |
| `_skip_active_pve_after_delay` | `L10329-L10342` | `cd, pid, delay_sec` | - | - | - |
| `run_radar_events` | `L10345-L11148` | `cd, pid, client_state, cfg, dry_run, context` | AutoFinishDetectEvent, BatchDetectEventRewardReceive, ClickCre... | BuildManager, DetectEventTemplateManager, FakeHelperMarchManager, FakeRe... | UIDetectEvent |
| `run_daily_claims` | `L11151-L11648` | `cd, pid, client_state, cfg, dry_run, context` | AchievementRewardGet, AllClaimWeekCardReward, ClaimAllSeasonPa... | AchievementManager, ActBattlePassData, ActSeasonWeekCardData, ActivityLi... | - |
| `_scan_daily_tasks_live` | `L11651-L11752` | `cd, pid` | - | DailyTaskManager | DailyQuest |
| `_classify_daily_task_kind` | `L11755-L11805` | `t` | - | - | - |
| `_do_daily_social_likes` | `L11808-L11880` | `cd, pid, needed, dry_run` | - | MomentManager | - |
| `_do_daily_hero_exp` | `L11883-L11947` | `cd, pid, needed, dry_run` | HeroLvUp | HeroDataManager, ItemData, ItemTemplateManager | - |
| `_do_daily_ticket_recruit` | `L11950-L12027` | `cd, pid, needed, dry_run` | LotteryHeroCard | ItemData, LotteryDataManager | - |
| `_do_daily_boss_rally` | `L12030-L12218` | `cd, pid, needed, target_keyword, cfg, dry_run, context` | FindMonster, FindMonsterBoss | AllianceWarDataManager, MonsterManager, WorldPointManager | Monster |
| `_do_daily_gather_acts` | `L12221-L12352` | `cd, pid, needed, cfg, dry_run, context` | FindResourcePoint | CollectResourceManager, WorldPointManager | GatherResource |
| `_claim_all_daily_tasks_and_boxes` | `L12355-L12423` | `cd, pid, dry_run` | DailyQuestGetAllReward, DailyQuestReward, DailyTaskReward | DailyTaskManager | - |
| `run_daily_tasks_complete` | `L12426-L12740` | `cd, pid, client_state, cfg, dry_run, context` | FindMonster | BuildManager, DailyTaskManager, WorldPointManager | Monster |
| `run_free_recruits` | `L12743-L12843` | `cd, pid, client_state, cfg, dry_run, context` | ItemUse, LotteryHeroCard | ItemData, ItemTemplateManager, LotteryDataManager, SmallPeopleRecruitDat... | - |
| `run_garage_upgrades` | `L12846-L12959` | `cd, pid, client_state, cfg, dry_run, context` | CarComponInstallAll, CarComponUpgradeAll, GarageRefit, GarageR... | GarageComponManager, GarageRefitManager | - |
| `run_alliance_boss_mine` | `L12962-L13085` | `cd, pid, client_state, cfg, dry_run, context` | ReceiveAllianceBossFreeReward | AllianceBossBearManager, AllianceMineManager | - |
| `_load_bot_mine_melee_module` | `L13088-L13104` | `` | - | - | - |
| `action_mine_melee_refresh` | `L13107-L13176` | `cd, pid, client_state, cfg, dry_run, context, refres...` | - | - | - |
| `_cli_main` | `L13256-L13394` | `` | - | - | - |

## 7. Frontend Web UI DOM & JavaScript Reference (`launcher/web/index.html`)

- **Views (7):** `{'id': 'view-overview', 'class': 'view-pane active'}`, `{'id': 'view-game', 'class': 'view-pane'}`, `{'id': 'view-alliances', 'class': 'view-pane'}`, `{'id': 'view-map', 'class': 'view-pane'}`, `{'id': 'view-bots', 'class': 'view-pane'}`, `{'id': 'view-inventory', 'class': 'view-pane'}`, `{'id': 'view-calculators', 'class': 'view-pane'}`
- **Modals (5):** `{'id': 'setup-modal', 'class': 'modal-backdrop'}`, `{'id': 'provision-modal', 'class': 'modal-backdrop'}`, `{'id': 'rules-modal', 'class': 'modal-backdrop'}`, `{'id': 'rules-modal-body', 'class': 'modal-body'}`, `{'id': 'troops-modal', 'class': 'modal-backdrop'}`
- **Direct `pywebview.api` Calls (9):** `browse_folder`, `clear_logs`, `inspect_setup`, `jump_to_coordinate`, `query_map_targets`, `run_action`, `save_bot_config`, `save_event_rules`, `select_target_client`
- **`doAction` Routes Invoked (42):** `apply_engine`, `export_alliance_members`, `export_elite_radar`, `export_inventory`, `export_map`, `export_mines`, `export_radar`, `export_roster`, `export_tech`, `export_top10`, `export_vs`, `flush_ram`, `install_bot_task`, `launch_all_farms`, `launch_single_client`, `open_active_migration`, `open_all_bases`, `open_all_resources`, `open_bracket_folder`, `open_data_folder`, `open_google_roster`, `open_inventory_excel`, `open_map_summary`, `open_scratch_folder`, `open_selected_bracket_state`, `open_unshielded_excel`, `open_vs_excel`, `provision_farm`, `restart_daemon`, `run_alliance_help_now`, `run_always_on_sweep_now`, `run_bot_cycle`, `run_single_task`, `scan_fleet`, `setup_base_install`, `start_bot_daemon`, `stop_all_farms`, `stop_bot_daemon`, `stop_single_client`, `sync_farm_builds`, `sync_google_bracket`, `uninstall_bot_task`

### All Frontend Buttons (107 Buttons in `launcher/web/index.html`)
| Section / View | DOM ID | Label | `onclick` Handler | Data Attrs |
|---|---|---|---|---|
| `nav` | `-` | Home / Overview | `switchView('overview')` | `data-view=overview` |
| `nav` | `-` | Game & Engine | `switchView('game')` | `data-view=game` |
| `nav` | `-` | Alliances & VS | `switchView('alliances')` | `data-view=alliances` |
| `nav` | `-` | Map & Scouting | `switchView('map')` | `data-view=map` |
| `nav` | `-` | Vault & Inventory | `switchView('inventory')` | `data-view=inventory` |
| `nav` | `-` | Calculators | `switchView('calculators')` | `data-view=calculators` |
| `nav` | `-` | Farms & Bot | `switchView('bots')` | `data-view=bots` |
| `view-overview` | `-` | Install / Check Setup | `openSetupModal()` | `-` |
| `view-overview` | `-` | + Add Account | `openProvisionModal()` | `-` |
| `view-overview` | `-` | Setup & Patch Base Game | `openSetupModal()` | `-` |
| `view-overview` | `-` | Complete Daily Tasks | `runSingleTask('daily_tasks_complete', false)` | `-` |
| `view-overview` | `-` | Run Bot Cycle Now | `doAction('run_bot_cycle', {dry_run:false, scope:'All Runn...` | `-` |
| `view-overview` | `-` | Launch Farm Clients | `doAction('launch_all_farms', {mode: cfgLaunchMode()})` | `-` |
| `view-overview` | `-` | Main Account | `setOverviewRole('main')` | `data-ov-role=main` |
| `view-overview` | `-` | Farm Accounts | `setOverviewRole('farm')` | `data-ov-role=farm` |
| `view-game` | `-` | Apply 180 FPS & Smooth Preloader | `doAction('apply_engine')` | `-` |
| `view-game` | `-` | Flush RAM Now | `doAction('flush_ram')` | `-` |
| `view-game` | `-` | Restart Auto-Engine Daemon | `doAction('restart_daemon')` | `-` |
| `view-game` | `-` | Export Bag Inventory | `doAction('export_inventory')` | `-` |
| `view-game` | `-` | Export Tech Tree | `doAction('export_tech')` | `-` |
| `view-game` | `-` | Open Data Folder | `doAction('open_data_folder')` | `-` |
| `view-game` | `-` | Open Working Folder | `doAction('open_scratch_folder')` | `-` |
| `view-alliances` | `-` | 📸 Save Baseline | `loadAllianceDeltas(true)` | `-` |
| `view-alliances` | `-` | 🔄 Refresh | `loadAllianceDeltas(false)` | `-` |
| `view-alliances` | `btn-export-vs` | Export VS Duel (Excel) | `doAction('export_vs')` | `-` |
| `view-alliances` | `-` | Open VS Workbook | `doAction('open_vs_excel')` | `-` |
| `view-alliances` | `btn-export-roster` | Export Alliance Roster | `doAction('export_roster')` | `-` |
| `view-alliances` | `-` | Export Members Master | `doAction('export_alliance_members')` | `-` |
| `view-alliances` | `-` | Google Sheet Roster | `doAction('open_google_roster')` | `-` |
| `view-alliances` | `btn-active-mig` | Open Active State Migration | `doAction('open_active_migration')` | `-` |
| `view-alliances` | `-` | Open Top 10 Alliances Master | `doAction('export_top10')` | `-` |
| `view-alliances` | `-` | Open Selected State | `doAction('open_selected_bracket_state', {state: document....` | `-` |
| `view-alliances` | `-` | All 16 Workbooks Folder | `doAction('open_bracket_folder')` | `-` |
| `view-map` | `-` | Jump Camera In-Game | `doResourceNav(false)` | `-` |
| `view-map` | `-` | Dispatch Free Squad | `doResourceNav(true)` | `-` |
| `view-map` | `-` | Scan & Export Map | `doAction('export_map')` | `-` |
| `view-map` | `-` | All Bases (Excel) | `doAction('open_all_bases')` | `-` |
| `view-map` | `-` | All Resources (CSV) | `doAction('open_all_resources')` | `-` |
| `view-map` | `-` | Map Summary | `doAction('open_map_summary')` | `-` |
| `view-map` | `-` | Export Unshielded (HQ 25+) | `doAction('export_radar')` | `-` |
| `view-map` | `-` | Export Elite (HQ 30+) | `doAction('export_elite_radar')` | `-` |
| `view-map` | `-` | High-Tier Mines | `doAction('export_mines')` | `-` |
| `view-map` | `-` | Open Targets Excel | `doAction('open_unshielded_excel')` | `-` |
| `view-map` | `-` | Refresh | `refreshMapTable()` | `-` |
| `view-bots` | `-` | Apply Preset | `applySelectedPreset()` | `-` |
| `view-bots` | `-` | + Save As... | `saveCurrentAsPreset()` | `-` |
| `view-bots` | `-` | 🗑️ | `deleteSelectedPreset()` | `-` |
| `view-bots` | `-` | Run Bot Cycle | `runCycleClick(false)` | `-` |
| `view-bots` | `-` | 🚀 Launch All Farms | `doAction('launch_all_farms', {mode: cfgLaunchMode()})` | `-` |
| `view-bots` | `-` | ⏹ Stop All Farms | `doAction('stop_all_farms')` | `-` |
| `view-bots` | `-` | ⚙️ Fleet Tools ▾ | `toggleFleetToolsMenu(event)` | `-` |
| `view-bots` | `-` | 🔍 Scan Active Clients | `doAction('scan_fleet'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | 🛠️ Setup / Patch Base Game | `openSetupModal(); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | 🔄 Sync Farm Game Builds | `doAction('sync_farm_builds'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | ➕ Add Account / Clone Farm | `openProvisionModal(); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | 📋 Detailed Rules & Trucks... | `openRulesModal(); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | 📊 Sync 16 Bracket Sheets | `doAction('sync_google_bracket'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | 🟢 Start Background Loop Daemon | `doAction('start_bot_daemon'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | 🔴 Stop Background Loop Daemon | `doAction('stop_bot_daemon'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | ⏱️ Register Windows Task Scheduler | `doAction('install_bot_task'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | ❌ Remove Windows Schedule | `doAction('uninstall_bot_task'); toggleFleetToolsMenu();` | `-` |
| `view-bots` | `-` | Save Settings | `saveBotSettings(false)` | `-` |
| `view-bots` | `-` | All | `setConsoleFilter('all')` | `data-console-filter=all` |
| `view-bots` | `-` | Errors & Tips | `setConsoleFilter('errors_tips')` | `data-console-filter=errors_tips` |
| `view-bots` | `-` | Steps | `setConsoleFilter('steps')` | `data-console-filter=steps` |
| `view-bots` | `-` | Details | `setConsoleFilter('details')` | `data-console-filter=details` |
| `view-bots` | `-` | Auto-Scroll: ON | `toggleConsoleAutoScroll()` | `data-autoscroll-btn=None` |
| `view-bots` | `-` | Copy Log | `copyConsoleLogs(this)` | `-` |
| `view-bots` | `-` | Clear | `clearLogs()` | `-` |
| `view-bots` | `-` | Farm Accounts | `setEditRole('farm')` | `data-edit-role=farm` |
| `view-bots` | `-` | Main Account | `setEditRole('main')` | `data-edit-role=main` |
| `view-inventory` | `-` | Sync Live from Game | `refreshInventoryView(true)` | `-` |
| `view-inventory` | `-` | Export Excel | `doAction('open_inventory_excel')` | `-` |
| `view-inventory` | `-` | All Items 0 | `setInventoryCategory('all')` | `data-cat=all` |
| `view-inventory` | `-` | Speedups 0 | `setInventoryCategory('speedups')` | `data-cat=speedups` |
| `view-inventory` | `-` | Crates & Chests 0 | `setInventoryCategory('chests')` | `data-cat=chests` |
| `view-inventory` | `-` | Heroes & Shards 0 | `setInventoryCategory('heroes')` | `data-cat=heroes` |
| `view-inventory` | `-` | Gear & Badges 0 | `setInventoryCategory('gear')` | `data-cat=gear` |
| `view-inventory` | `-` | Utilities & Passes 0 | `setInventoryCategory('other')` | `data-cat=other` |
| `view-calculators` | `btn-calc-subtab-tech` | Tech Tree & Courage Badges | `switchCalcSubTab('tech')` | `-` |
| `view-calculators` | `btn-calc-subtab-migration` | State Migration & Passes | `switchCalcSubTab('migration')` | `-` |
| `view-calculators` | `-` | Sync Live from Game | `refreshTechCalculator(true)` | `-` |
| `root` | `-` | All | `setConsoleFilter('all')` | `data-console-filter=all` |
| `root` | `-` | Errors & Tips | `setConsoleFilter('errors_tips')` | `data-console-filter=errors_tips` |
| `root` | `-` | Steps | `setConsoleFilter('steps')` | `data-console-filter=steps` |
| `root` | `-` | Details | `setConsoleFilter('details')` | `data-console-filter=details` |
| `root` | `-` | Auto-Scroll: ON | `toggleConsoleAutoScroll()` | `data-autoscroll-btn=None` |
| `root` | `-` | Copy Log | `copyConsoleLogs(this)` | `-` |
| `root` | `-` | Clear | `clearLogs()` | `-` |
| `root` | `btn-drawer-tall` | Tall | `toggleConsoleTall()` | `-` |
| `root` | `btn-drawer-toggle` | Collapse | `toggleLogDrawer()` | `-` |
| `setup-modal` | `-` | Close | `closeSetupModal()` | `-` |
| `setup-modal` | `-` | Auto-Detect | `recheckSetupStatus()` | `-` |
| `setup-modal` | `-` | Browse | `browseSetupBase()` | `-` |
| `setup-modal` | `-` | Close | `closeSetupModal()` | `-` |
| `setup-modal` | `-` | + Add 2nd / 3rd Account... | `closeSetupModal(); openProvisionModal();` | `-` |
| `setup-modal` | `-` | Install / Mend Base Game Setup | `runBaseSetupInstall()` | `-` |
| `provision-modal` | `-` | Close | `closeProvisionModal()` | `-` |
| `provision-modal` | `-` | Browse | `browseProvFolder()` | `-` |
| `provision-modal` | `-` | Cancel | `closeProvisionModal()` | `-` |
| `provision-modal` | `-` | Create Account Instance | `submitProvision()` | `-` |
| `rules-modal` | `-` | Close | `closeRulesModal()` | `-` |
| `rules-modal-body` | `-` | Cancel | `closeRulesModal()` | `-` |
| `rules-modal-body` | `-` | Save All Rules | `saveRulesModal()` | `-` |
| `troops-modal` | `-` | Close | `closeTroopsModal()` | `-` |
| `troops-modal` | `-` | Close | `closeTroopsModal()` | `-` |
| `troops-modal` | `-` | 🔄 Sync Live from Game | `refreshTroopsOverview(true)` | `-` |

### All Frontend JavaScript Functions (98 Functions)
| Function Name | Parameters | Line |
|---|---|---:|
| `api` | `` | 2552 |
| `callApi` | `method, ...args` | 2556 |
| `esc` | `s` | 2567 |
| `switchView` | `viewId` | 2573 |
| `toggleLogDrawer` | `` | 2588 |
| `toggleConsoleTall` | `` | 2599 |
| `normalizeLogKind` | `entry` | 2609 |
| `normalizeLogCat` | `entry, kindClass` | 2619 |
| `matchesConsoleFilter` | `entry, filterMode` | 2624 |
| `buildLogEntryEl` | `entry` | 2651 |
| `updateConsoleCountPills` | `visibleCount, totalCount` | 2666 |
| `renderAllLogsFromBuffer` | `` | 2676 |
| `setConsoleFilter` | `mode` | 2707 |
| `toggleConsoleAutoScroll` | `` | 2715 |
| `copyConsoleLogs` | `btnEl` | 2730 |
| `clearLogs` | `` | 2760 |
| `syncLogs` | `logs` | 2775 |
| `cfgLaunchMode` | `` | 2844 |
| `doAction` | `actionId, payload` | 2849 |
| `doResourceNav` | `dispatch` | 2855 |
| `runCycleClick` | `dryRun` | 2862 |
| `showToast` | `msg, kind = "info"` | 2876 |
| `resolveCurrentScopeTarget` | `` | 2882 |
| `applyAlwaysOnResponse` | `res` | 2903 |
| `toggleAlwaysOnDaemon` | `enabled` | 2922 |
| `toggleHospitalWatcher` | `enabled` | 2937 |
| `toggleAllianceHelpWatcher` | `enabled` | 2954 |
| `toggleAllianceTechWatcher` | `enabled` | 2969 |
| `triggerAlwaysOnSweepNow` | `` | 2984 |
| `triggerAllianceHelpNow` | `` | 2989 |
| `runSingleTask` | `taskKey, dryRun` | 2994 |
| `setOverviewRole` | `r` | 3036 |
| `setEditRole` | `r` | 3042 |
| `setCategory` | `cat` | 3048 |
| `toggleTask` | `key, role, checked` | 3054 |
| `saveBotSettings` | `quiet` | 3069 |
| `loadBotPresets` | `` | 3086 |
| `applySelectedPreset` | `` | 3111 |
| `saveCurrentAsPreset` | `` | 3132 |
| `deleteSelectedPreset` | `` | 3154 |
| `toggleFleetToolsMenu` | `event` | 3168 |
| `populateBracketDropdown` | `serverId` | 3184 |
| `renderOverviewFleet` | `` | 3197 |
| `getAlwaysOnSig` | `s` | 3275 |
| `renderAlwaysOnPanelHtml` | `s` | 3301 |
| `renderAlwaysOnPanels` | `` | 3483 |
| `updateAlwaysOnSidebar` | `s` | 3495 |
| `renderTaskCardHtml` | `t, role, enabled` | 3563 |
| `renderOverviewHighlights` | `` | 3589 |
| `renderCategoryFilters` | `` | 3600 |
| `renderTaskCards` | `` | 3609 |
| `renderState` | `s` | 3622 |
| `refreshState` | `` | 3717 |
| `renderSetupModalBody` | `su` | 3725 |
| `openSetupModal` | `` | 3753 |
| `closeSetupModal` | `` | 3758 |
| `recheckSetupStatus` | `` | 3761 |
| `browseSetupBase` | `` | 3768 |
| `runBaseSetupInstall` | `` | 3776 |
| `openProvisionModal` | `` | 3783 |
| `closeProvisionModal` | `` | 3796 |
| `browseProvFolder` | `` | 3799 |
| `submitProvision` | `` | 3804 |
| `openRulesModal` | `` | 3825 |
| `closeRulesModal` | `` | 3927 |
| `saveRulesModal` | `` | 3930 |
| `onMapSearchChanged` | `` | 4012 |
| `refreshMapTable` | `` | 4019 |
| `snapToCoords` | `x, y, serverId` | 4067 |
| `refreshInventoryView` | `forceLive = false` | 4101 |
| `renderInventoryDashboard` | `` | 4117 |
| `getRaritySvg` | `category, rarity` | 4181 |
| `renderInventoryGrid` | `` | 4194 |
| `setInventoryCategory` | `cat` | 4278 |
| `onInventorySearchChanged` | `` | 4287 |
| `onInventorySortChanged` | `` | 4296 |
| `switchCalcSubTab` | `tab` | 4310 |
| `loadCalculatorsView` | `` | 4323 |
| `refreshTechCalculator` | `forceLive = false` | 4332 |
| `renderTechCalculator` | `` | 4345 |
| `onTechTreeSelectChanged` | `val` | 4390 |
| `toggleHideMaxedTiers` | `checked` | 4395 |
| `renderSelectedTechTree` | `` | 4400 |
| `refreshMigrationCalculator` | `stateId = 694, playerQuery = ""` | 4499 |
| `renderMigrationCalculator` | `` | 4506 |
| `onHeldPassesChanged` | `` | 4603 |
| `onMigrationStateSelectChanged` | `val` | 4619 |
| `onMigrationSearchInput` | `` | 4623 |
| `selectSearchedCommander` | `idx` | 4659 |
| `doQuickShield` | `pid` | 4670 |
| `doQuickRecall` | `pid` | 4678 |
| `openTroopsModal` | `pid` | 4690 |
| `closeTroopsModal` | `` | 4696 |
| `refreshTroopsOverview` | `forceLive = false` | 4700 |
| `renderTroopsModal` | `d` | 4713 |
| `initDeltaStateDropdown` | `` | 4819 |
| `loadAllianceDeltas` | `forceSnapshot = false` | 4833 |
| `renderAllianceDeltas` | `d` | 4856 |

## 8. Complete Repository File Inventory (123 Files)

| Relative Path | Folder | Size (bytes) | Ext |
|---|---|---:|---|
| `tools/all_inventory_with_tpl.json` | `tools` | 12,535 | `.json` |
| `tools/analyze gear vehicle.py` | `tools` | 2,290 | `.py` |
| `tools/analyze science progress.py` | `tools` | 3,587 | `.py` |
| `tools/analyze session.py` | `tools` | 2,444 | `.py` |
| `tools/analyze traffic log.py` | `tools` | 1,290 | `.py` |
| `tools/apply remediation.py` | `tools` | 20,378 | `.py` |
| `tools/auto detect environment.py` | `tools` | 8,209 | `.py` |
| `tools/bot actions.py` | `tools` | 596,821 | `.py` |
| `tools/bot_mine_melee.py` | `tools` | 51,357 | `.py` |
| `tools/build all bracket native sheets.py` | `tools` | 28,127 | `.py` |
| `tools/build top10 excel.py` | `tools` | 20,948 | `.py` |
| `tools/client discovery.py` | `tools` | 41,057 | `.py` |
| `tools/create styled excel.py` | `tools` | 8,401 | `.py` |
| `tools/detected_environment.json` | `tools` | 646 | `.json` |
| `tools/disasm monster.py` | `tools` | 2,891 | `.py` |
| `tools/disasm wmo full.py` | `tools` | 2,691 | `.py` |
| `tools/disasm wpo.py` | `tools` | 3,123 | `.py` |
| `tools/disassemble wpm.py` | `tools` | 4,877 | `.py` |
| `tools/dump all buildings.py` | `tools` | 4,925 | `.py` |
| `tools/dump all inventory.py` | `tools` | 5,204 | `.py` |
| `tools/dump all player assets complete.py` | `tools` | 13,339 | `.py` |
| `tools/dump extra wpm.py` | `tools` | 2,273 | `.py` |
| `tools/dump heroes armies.py` | `tools` | 7,277 | `.py` |
| `tools/dump optizone.py` | `tools` | 2,321 | `.py` |
| `tools/dump science full.py` | `tools` | 5,808 | `.py` |
| `tools/dump wpm functions.py` | `tools` | 4,423 | `.py` |
| `tools/export alliance members excel.py` | `tools` | 4,973 | `.py` |
| `tools/export alliance roster excel.py` | `tools` | 3,921 | `.py` |
| `tools/export high tier resources.py` | `tools` | 4,121 | `.py` |
| `tools/export inventory excel.py` | `tools` | 5,855 | `.py` |
| `tools/export map intelligence.py` | `tools` | 14,651 | `.py` |
| `tools/export map summary excel.py` | `tools` | 4,474 | `.py` |
| `tools/export tech tree excel.py` | `tools` | 8,020 | `.py` |
| `tools/export unshielded targets.py` | `tools` | 4,523 | `.py` |
| `tools/export vs duel excel.py` | `tools` | 10,635 | `.py` |
| `tools/export vs rankings.py` | `tools` | 9,951 | `.py` |
| `tools/fetch all bracket alliances.py` | `tools` | 8,420 | `.py` |
| `tools/fetch all bracket rosters.py` | `tools` | 9,674 | `.py` |
| `tools/fetch top10 rosters.py` | `tools` | 8,132 | `.py` |
| `tools/flush game memory.py` | `tools` | 3,837 | `.py` |
| `tools/generate bracket sheets.py` | `tools` | 20,460 | `.py` |
| `tools/heinz_diagnostics.py` | `tools` | 32,230 | `.py` |
| `tools/inspect adjusters.py` | `tools` | 3,188 | `.py` |
| `tools/inspect autoadjustlod.py` | `tools` | 2,419 | `.py` |
| `tools/inspect buildasync upvalues.py` | `tools` | 3,748 | `.py` |
| `tools/inspect deep urp and timers.py` | `tools` | 6,046 | `.py` |
| `tools/inspect fow details.py` | `tools` | 3,392 | `.py` |
| `tools/inspect input ui boomers.py` | `tools` | 1,886 | `.py` |
| `tools/inspect lights fow.py` | `tools` | 3,351 | `.py` |
| `tools/inspect lod methods.py` | `tools` | 3,204 | `.py` |
| `tools/inspect monster.py` | `tools` | 2,207 | `.py` |
| `tools/inspect optizone and close.py` | `tools` | 4,532 | `.py` |
| `tools/inspect visibility gates.py` | `tools` | 5,358 | `.py` |
| `tools/inspect wbo.py` | `tools` | 2,192 | `.py` |
| `tools/inspect wir.py` | `tools` | 1,971 | `.py` |
| `tools/inspect wpm internals.py` | `tools` | 6,851 | `.py` |
| `tools/jump to target.py` | `tools` | 2,368 | `.py` |
| `tools/launch_game.py` | `tools` | 536 | `.py` |
| `tools/list wpm fns.py` | `tools` | 2,034 | `.py` |
| `tools/multi client bot.py` | `tools` | 86,557 | `.py` |
| `tools/navigate to resource.py` | `tools` | 14,626 | `.py` |
| `tools/print full tech trees.py` | `tools` | 2,936 | `.py` |
| `tools/print heroes.py` | `tools` | 563 | `.py` |
| `tools/print resolved inventory.py` | `tools` | 1,376 | `.py` |
| `tools/probe world camera.py` | `tools` | 3,446 | `.py` |
| `tools/run enhanced diagnostics.py` | `tools` | 29,939 | `.py` |
| `tools/sync all bracket states.py` | `tools` | 1,919 | `.py` |
| `tools/sync bracket drive sheets.py` | `tools` | 48,822 | `.py` |
| `tools/sync farm clients.py` | `tools` | 42,368 | `.py` |
| `tools/test relief.py` | `tools` | 4,548 | `.py` |
| `tools/test tile math.py` | `tools` | 2,303 | `.py` |
| `tools/test urp patch.py` | `tools` | 4,438 | `.py` |
| `tools/trace wpm build.py` | `tools` | 4,202 | `.py` |
| `launcher/app.py` | `launcher` | 121,754 | `.py` |
| `launcher/assets/tech_badge_matrix.json` | `launcher` | 75,881 | `.json` |
| `launcher/Check LastZ Engine Status.bat` | `launcher` | 412 | `.bat` |
| `launcher/HeinZ Control Hub.py` | `launcher` | 121,754 | `.py` |
| `launcher/HeinZ.spec` | `launcher` | 2,670 | `.spec` |
| `launcher/heinz_hub_web.py` | `launcher` | 271,702 | `.py` |
| `launcher/Launch HeinZ.bat` | `launcher` | 1,497 | `.bat` |
| `launcher/Run Diagnostics.bat` | `launcher` | 847 | `.bat` |
| `launcher/Start LastZ Watcher.bat` | `launcher` | 444 | `.bat` |
| `launcher/web/index.html` | `launcher` | 220,232 | `.html` |
| `api/batch fetch migration scores.py` | `api` | 11,444 | `.py` |
| `api/batch fetch top10 scores.py` | `api` | 12,743 | `.py` |
| `api/call dorequest.py` | `api` | 1,879 | `.py` |
| `api/dump dorequest.py` | `api` | 2,428 | `.py` |
| `api/GoogleAppsScript_SyncReceiver.js` | `api` | 7,333 | `.js` |
| `api/inspect cs sfsnetwork.py` | `api` | 2,782 | `.py` |
| `api/inspect network assistant.py` | `api` | 2,792 | `.py` |
| `api/inspect network callers.py` | `api` | 3,057 | `.py` |
| `api/inspect sfs network.py` | `api` | 2,356 | `.py` |
| `api/inspect sfs network2.py` | `api` | 2,815 | `.py` |
| `api/sync state deep profiles.py` | `api` | 33,207 | `.py` |
| `api/test call dorequest.py` | `api` | 1,881 | `.py` |
| `api/test network assistant keys.py` | `api` | 2,329 | `.py` |
| `api/test network assistant methods.py` | `api` | 2,542 | `.py` |
| `api/trace protocal caller.py` | `api` | 1,771 | `.py` |
| `api/trigger helicopter help.py` | `api` | 4,164 | `.py` |
| `daemon/apply widescreen smooth map.py` | `daemon` | 72,331 | `.py` |
| `daemon/lastz auto engine daemon.py` | `daemon` | 77,481 | `.py` |
| `telemetry/check update and ui.py` | `telemetry` | 1,791 | `.py` |
| `telemetry/check v7 status.py` | `telemetry` | 3,444 | `.py` |
| `telemetry/diag map preload.py` | `telemetry` | 4,956 | `.py` |
| `telemetry/diag perf.py` | `telemetry` | 3,510 | `.py` |
| `telemetry/inspect cam and renderers.py` | `telemetry` | 4,694 | `.py` |
| `telemetry/inspect overlay state.py` | `telemetry` | 2,126 | `.py` |
| `telemetry/inspect scenes.py` | `telemetry` | 3,187 | `.py` |
| `telemetry/inspect tm.py` | `telemetry` | 3,712 | `.py` |
| `telemetry/inspect uimanager.py` | `telemetry` | 1,824 | `.py` |
| `telemetry/inspect windows.py` | `telemetry` | 2,151 | `.py` |
| `telemetry/profile frame bottlenecks.py` | `telemetry` | 2,202 | `.py` |
| `tests/__init__.py` | `tests` | 272 | `.py` |
| `tests/run_all_tests.py` | `tests` | 5,238 | `.py` |
| `tests/test_adversarial_probes.py` | `tests` | 44,215 | `.py` |
| `tests/test_boundary_corner_cases.py` | `tests` | 9,850 | `.py` |
| `tests/test_cross_feature_combinations.py` | `tests` | 7,337 | `.py` |
| `tests/test_dialog_dismissal.py` | `tests` | 5,031 | `.py` |
| `tests/test_empirical_challenger.py` | `tests` | 14,826 | `.py` |
| `tests/test_harness.py` | `tests` | 30,505 | `.py` |
| `tests/test_packet_contracts.py` | `tests` | 31,324 | `.py` |
| `tests/test_radar_hospital_logic.py` | `tests` | 12,092 | `.py` |
| `tests/test_real_world_scenarios.py` | `tests` | 8,921 | `.py` |
