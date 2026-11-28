"""Multi-client Last Z orchestrator, scheduler, and status reporter."""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import logging
import math
import os
import re
import subprocess
import sys
import threading
import time
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

try:
    import psutil
except Exception:
    psutil = None  # type: ignore[assignment]

ROOT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "tools"
DATA_DIR = Path(os.environ["HEINZ_DATA_DIR"]) if os.environ.get("HEINZ_DATA_DIR", "").strip() else (ROOT_DIR / "data")
CONFIG_PATH = DATA_DIR / "bot config.json"
STATUS_PATH = DATA_DIR / "bot status.json"
STAGE_STATE_PATH = DATA_DIR / "bot_stage_state.json"
STOP_FLAG_PATH = DATA_DIR / "bot stop.flag"
PID_FILE_PATH = DATA_DIR / "bot daemon.pid"
LOG_PATH = DATA_DIR / "logs" / "multi_client_bot.log"

# ---------------------------------------------------------------------------
# 5-Stage Sequential State Machine Definitions
# ---------------------------------------------------------------------------
STAGE_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "stage_id": 1,
        "tag": "[STAGE 1/5]",
        "key": "stage_1_war_safety",
        "name": "War Safety & Emergency Shields",
        "tasks": ("war_safety", "rf_hq_under_attack"),
        "extended_tasks": (),
        "default_cooldown_sec": 0.0,
        "pacing_delay_sec": 0.25,
        "critical_preempt": True,
    },
    {
        "stage_id": 2,
        "tag": "[STAGE 2/5]",
        "key": "stage_2_casualty_recovery",
        "name": "Casualty Recovery & Hospital",
        "tasks": ("hospital_heal",),
        "extended_tasks": (),
        "default_cooldown_sec": 15.0,
        "pacing_delay_sec": 0.25,
        "critical_preempt": False,
    },
    {
        "stage_id": 3,
        "tag": "[STAGE 3/5]",
        "key": "stage_3_resource_gathering",
        "name": "Resource Gathering & Event Mines",
        "tasks": ("mining_event", "mine_melee_refresh"),
        "extended_tasks": ("auto_gather",),
        "default_cooldown_sec": 30.0,
        "pacing_delay_sec": 0.35,
        "critical_preempt": False,
    },
    {
        "stage_id": 4,
        "tag": "[STAGE 4/5]",
        "key": "stage_4_base_production",
        "name": "Base Production & Upgrades",
        "tasks": ("troop_training", "building_upgrades", "research_queue", "garage_upgrades", "hero_progression", "speedups"),
        "extended_tasks": (),
        "default_cooldown_sec": 20.0,
        "pacing_delay_sec": 0.35,
        "critical_preempt": False,
    },
    {
        "stage_id": 5,
        "tag": "[STAGE 5/5]",
        "key": "stage_5_alliance_dailies",
        "name": "Alliance & Dailies",
        "tasks": (
            "auto_help",
            "alliance_daily",
            "radar_events",
            "treasure_helicopter",
            "trucks",
            "bounties",
            "bounty_steal",
            "arena",
            "hero_battlefield",
            "area_exploration",
            "boomer_runs",
            "furylord",
            "tyrant_event",
            "full_preparedness",
            "vip_store_rewards",
            "free_recruits",
            "daily_tasks_complete",
            "daily_claims",
        ),
        "extended_tasks": (
            "dismiss_popups",
        ),
        "default_cooldown_sec": 30.0,
        "pacing_delay_sec": 0.2,
        "critical_preempt": False,
    },
)

STAGE_TASK_ORDER: tuple[str, ...] = tuple(
    t for stage in STAGE_DEFINITIONS for t in stage["tasks"]
)

_MEMORY_STAGE_LOCKS: dict[str, dict[str, Any]] = {}


def _hidden_subproc_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
    }
    si_cls = getattr(subprocess, "STARTUPINFO", None)
    if si_cls is not None:
        si = si_cls()
        si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        si.wShowWindow = 0
        kwargs["startupinfo"] = si
    return kwargs


_HEX_COLOR_TIP_RE = re.compile(r"^#?[0-9A-Fa-f]{6,8}(?:\s*\(#?[0-9A-Fa-f]{6,8}\))?$")


def _clean_tips_list(tips: Any) -> list[str]:
    """Filter out pure hex color strings (e.g. E000000) and deduplicate tips per task."""
    if not isinstance(tips, (list, tuple)):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in tips:
        s = str(item or "").strip()
        if not s or _HEX_COLOR_TIP_RE.match(s) or s.upper() == "E000000":
            continue
        if s not in seen:
            seen.add(s)
            cleaned.append(s)
    return cleaned


_MODULE_CACHE: dict[str, Any] = {}
_MODULE_CACHE_LOCK = threading.Lock()
_CD_SINGLETON_KEY = "heinz_client_discovery_singleton"
_BA_SINGLETON_KEY = "heinz_bot_actions_singleton"
_BMM_SINGLETON_KEY = "heinz_bot_mine_melee_singleton"
_CD_PATH_KEY = os.path.normcase(os.path.abspath(str(TOOLS_DIR / "client discovery.py")))
_BA_PATH_KEY = os.path.normcase(os.path.abspath(str(TOOLS_DIR / "bot actions.py")))
_BMM_PATH_KEY = os.path.normcase(os.path.abspath(str(TOOLS_DIR / "bot mine melee.py")))


def _stat_sig(st: os.stat_result) -> tuple[int, int, int, int]:
    # Use st_birthtime_ns (matched across stat & fstat on Windows NTFS after os.replace) + st_ino.
    return (st.st_mtime_ns, getattr(st, "st_birthtime_ns", st.st_ctime_ns), st.st_size, st.st_ino)


def _load_module(name: str, file_path: Path) -> Any:
    cache_key = os.path.normcase(os.path.abspath(str(file_path)))
    singleton_key: str | None = None
    if cache_key == _CD_PATH_KEY or name == "client_discovery":
        singleton_key = _CD_SINGLETON_KEY
    elif cache_key == _BA_PATH_KEY or name == "bot_actions":
        singleton_key = _BA_SINGLETON_KEY
    elif cache_key == _BMM_PATH_KEY or name == "bot_mine_melee":
        singleton_key = _BMM_SINGLETON_KEY

    with _MODULE_CACHE_LOCK:
        cached = _MODULE_CACHE.get(cache_key)
        if cached is not None:
            if singleton_key is not None:
                sys.modules.setdefault(singleton_key, cached)
            return cached
        if singleton_key is not None:
            existing_singleton = sys.modules.get(singleton_key)
            if existing_singleton is not None:
                _MODULE_CACHE[cache_key] = existing_singleton
                return existing_singleton
        spec = importlib.util.spec_from_file_location(name, str(file_path))
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Failed to load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if singleton_key == _CD_SINGLETON_KEY and not getattr(module, "_SAVE_PROFILES_ATOMIC", False) and hasattr(module, "PROFILES_PATH"):
            def _safe_save_profiles(payload: Any) -> None:
                profiles_path = Path(getattr(module, "PROFILES_PATH"))
                profiles_path.parent.mkdir(parents=True, exist_ok=True)
                tmp_path = profiles_path.parent / f"client profiles.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp"
                try:
                    with tmp_path.open("w", encoding="utf-8") as fh:
                        json.dump(payload, fh, indent=2, ensure_ascii=False)
                    for attempt in range(5):
                        try:
                            os.replace(tmp_path, profiles_path)
                            break
                        except (PermissionError, OSError):
                            if attempt == 4:
                                raise
                            time.sleep(0.05)
                finally:
                    try:
                        if tmp_path.exists():
                            tmp_path.unlink(missing_ok=True)
                    except OSError:
                        pass
                    if hasattr(module, "invalidate_discovery_cache"):
                        try:
                            module.invalidate_discovery_cache()
                        except Exception:
                            pass

            setattr(module, "save_profiles", _safe_save_profiles)
        if singleton_key is not None:
            sys.modules.setdefault(singleton_key, module)
            module = sys.modules[singleton_key]
        _MODULE_CACHE[cache_key] = module
        return module


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("multi_client_bot")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)
    return logger


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = _deep_merge(merged[k], v)
        else:
            merged[k] = deepcopy(v)
    return merged


_DEFAULT_CONFIG_TEMPLATE: dict[str, Any] | None = None
_DEFAULT_CONFIG_LOCK = threading.Lock()
_CONFIG_CACHE: dict[str, tuple[tuple[int, int, int, int], dict[str, Any]]] = {}
_CONFIG_CACHE_LOCK = threading.Lock()


def _build_default_config() -> dict[str, Any]:
    """Build portable default bot configuration when no local bot config.json exists yet."""
    shared_rules: dict[str, Any] = {
        "always_on_daemon": {"enabled": True, "interval_sec": 15},
        "auto_help": {"always_on": True, "interval_sec": 15, "help_allies": True, "call_help_queues": True, "claim_alliance_chests": True},
        "speedups": {"use_free_speed": True, "collect_finished": True, "use_items": False, "align_with_preparedness": True, "reserve_minutes": 600, "max_items_per_cycle": 5, "categories": {"build": True, "research": True, "train": False, "heal": True}},
        "troop_training": {"collect_finished": True, "train_highest_tier": True, "barracks": ["CarSoldier", "FootSoldier", "BowSoldier"], "batch_count": 0, "event_speed_zoom": True, "max_zoom_batches": 50, "zoom_use_universal_speedups": False},
        "building_upgrades": {"collect_resources": True, "hq_priority": True, "auto_prerequisites": True, "call_alliance_help": True, "priority_building_types": [400000, 403000, 423000, 424000, 425000, 411000]},
        "auto_gather": {"resource_priority": ["Oil", "Metal", "Wood", "Electricity"], "min_level": 3, "max_level": 9, "max_distance": 150, "formation_index": 0},
        "mine_melee_refresh": {"refresh_threshold_sec": 300, "min_payload_pct": 10.0, "reserve_formations": 1, "alliance_mine_priority": True, "recall_depleted": True},
        "boomer_runs": {"join_open_rallies": True, "auto_start_rally": True, "min_level": 1, "max_level": 5, "rally_wait_minutes": 5, "stamina_cost": 20, "min_stamina": 120},
        "tyrant_event": {"claim_free_reward": True, "claim_alliance_reward": True, "join_or_attack": True, "prefer_rally": True, "f1_always_host_rally": True, "other_formations_join_rallies": True, "repeat_when_free": True, "fast_repeat_sec": 10},
        "rf_hq_under_attack": {"reinforce_protected_uids": True, "reinforce_alliance_members": True, "alert_on_self_attack": True, "auto_shield_on_self_attack": False, "max_incoming_eta_seconds": 900},
        "treasure_helicopter": {"march_to_dig": True, "auto_claim_chat_treasures": True, "jitter_min_ms": 110, "jitter_max_ms": 240, "burst_clicks": 6, "lead_window_seconds": 2.0},
        "full_preparedness": {"execute_tasks": True, "claim_boxes": True, "claim_daily_quests": True, "claim_daily_chests": True},
        "furylord": {"exact_hour": 3, "exact_minute": 0, "window_minutes": 20, "max_attacks": 4, "formation_index": 1, "prefer_rally": True, "claim_rewards": True},
        "bounties": {"only_golden": True, "lock_orange": True, "help_allies_golden": True, "plunder_bounties": True, "min_color": 4, "use_free": True, "use_tickets": True, "use_diamonds": False, "stop_when_no_free_or_ticket": True, "claim_completed": True, "max_refreshes_per_cycle": 8, "cross_state_only": True, "min_level": 5, "max_daily_steals": 5, "max_servers_scan": 16},
        "bounty_steal": {"cross_state_only": True, "only_golden": True, "min_color": 4, "min_level": 5, "max_daily_steals": 5, "max_servers_scan": 16},
        "trucks": {"daily_sends": 4, "slots": [{"quality": 5, "formation": i} for i in (1, 2, 3, 4)], "reroll_with_items": True, "reroll_with_diamonds": False, "max_rerolls_per_truck": 6, "claim_completed": True, "attack_enabled": True, "attack_daily_limit": 4, "attack_cross_state_only": True, "attack_power_margin_below_f1": 20000000},
        "mining_event": {"weekdays": [0, 1], "mine_type": 2, "mine_reward": "xp", "mine_level": 7, "skip_occupied_players": True, "claim_finished": True, "max_refreshes": 3},
        "vip_store_rewards": {"claim_vip_points": True, "claim_vip_daily_freebie": True, "claim_store_vip_tab_free": True, "claim_weekly_gift_freebie": True},
        "area_exploration": {"claim_hangup_rewards": True, "auto_jump": True, "auto_battle": True, "auto_skip_battle": True, "max_battles_per_cycle": 5, "stop_on_fail": True},
        "hero_battlefield": {"auto_prefill_strongest_faction": True, "use_quick_deploy": True, "auto_skip_battle": True, "max_battles_per_faction": 5, "stop_on_fail": True, "skip_if_failed_this_period": True},
        "arena": {"max_battles_per_cycle": 5, "refresh_opponents": True, "auto_free_refresh": True, "pure_faction_teams": True, "pick_weakest": True, "min_win_odds_pct": 70, "min_power_advantage_ratio": 1.0},
        "war_safety": {"auto_shield_on_attack": True, "respect_war_fever": True, "recall_gatherers_on_attack": True, "max_eta_seconds": 300},
        "hospital_heal": {"headless": True, "auto_pass_active_sizing": True, "active_grace_minutes": 0, "collect_finished": True, "batch_minutes": 30, "min_batch_troops": 25, "max_batch_troops": 50000, "call_alliance_help": True, "use_speedups": False, "max_speedup_mins": 0, "max_chain_batches": 15, "persistent_watcher_enabled": False},
        "alliance_daily": {"donate_tech": True, "auto_tech_always_on": True, "use_gold_donate": False, "claim_gifts": True, "claim_red_packets": True, "claim_tasks": True},
        "research_queue": {"prefer_recommended": True, "call_alliance_help": True, "use_free_speed": True, "priority_tabs": [5, 1, 2, 3, 4]},
        "radar_events": {"trigger_scan": True, "claim_finished": True, "auto_dispatch": True, "auto_skip_battle": True, "max_dispatches_per_cycle": 20},
        "daily_tasks_complete": {"allow_pvp_hq_attack": False},
        "daily_claims": {"claim_daily_tasks": True, "claim_achievements": True, "claim_battle_pass": True, "claim_chapter_tasks": True},
        "free_recruits": {"claim_hero_recruits": True, "claim_small_people": True, "open_safe_chests": True, "max_chests_per_cycle": 20},
        "garage_upgrades": {"only_monday": True, "upgrade_refit": True, "use_refit_free_only": True, "install_better_components": True, "merge_components": True, "max_refit_steps_per_cycle": 5},
        "hero_progression": {
            "only_hero_day": True,
            "target_scope": "formation_1",
            "min_rarity": 4,
            "pinned_hero_ids": [],
            "max_actions_per_cycle": 15,
            "upgrade_levels": True,
            "allow_breakthrough": True,
            "target_level_cap": 0,
            "exp_reserve_millions": 0,
            "upgrade_stars": True,
            "use_universal_shards": False,
            "universal_shard_reserve": 50,
            "upgrade_skills": True,
            "skill_book_reserve": 0,
            "auto_equip_best": True,
            "upgrade_gear": True,
            "min_gear_quality": 5,
            "alloy_reserve": 0,
            "allow_gear_promote": False,
            "power_core_reserve": 0,
            "use_replacement_equip": False,
            "allow_sp_equip": False,
            "use_universal_sp_shards": False,
        },
    }
    main_tasks = {
        "auto_help": True, "rf_hq_under_attack": True, "treasure_helicopter": True,
        "full_preparedness": True, "speedups": True, "troop_training": True,
        "building_upgrades": True, "tyrant_event": True, "boomer_runs": True,
        "auto_gather": True, "mine_melee_refresh": True, "furylord": True, "bounties": True, "bounty_steal": True,
        "trucks": True, "mining_event": True, "vip_store_rewards": True,
        "sync_ruby_shop": True,
        "area_exploration": True, "hero_battlefield": True, "arena": True,
        "war_safety": True, "hospital_heal": True, "alliance_daily": True,
        "research_queue": False, "radar_events": True, "daily_tasks_complete": True, "daily_claims": True,
        "free_recruits": False, "garage_upgrades": False, "hero_progression": False,
    }
    farm_tasks = {k: True for k in main_tasks}
    main_cfg = _deep_merge({"enabled": True, "role": "main", "launch_mode": "windowed", "formation_reserve": 1, "min_stamina": 120, "tasks": main_tasks}, shared_rules)
    farm_cfg = _deep_merge({"enabled": True, "role": "farm", "launch_mode": "eco", "formation_reserve": 0, "min_stamina": 60, "tasks": farm_tasks}, shared_rules)
    farm_cfg["speedups"]["use_items"] = True
    farm_cfg["speedups"]["reserve_minutes"] = 120
    farm_cfg["speedups"]["max_items_per_cycle"] = 10
    farm_cfg["rf_hq_under_attack"]["auto_shield_on_self_attack"] = True
    farm_cfg["mine_melee_refresh"]["reserve_formations"] = 0
    return {
        "version": 2,
        "cycle_interval_seconds": 180,
        "inter_client_delay_seconds": 0.5,
        "auto_launch_stopped_clients": False,
        "auto_launch_mode": "eco",
        "discovered_protected_uids": [],
        "stage_machine": {
            "enabled": True,
            "enforce_cooldowns": True,
            "preempt_on_attack": True,
            "strict_emergency_preempt": True,
            "inter_stage_delay_seconds": 0.2,
            "inter_task_delay_seconds": 0.08,
            "verify_client_between_stages": True,
            "include_extended_tasks": False,
            "stage_cooldowns_seconds": {
                "1": 0.0,
                "2": 15.0,
                "3": 30.0,
                "4": 20.0,
                "5": 30.0,
            },
        },
        "schedule": {"task_name": "LastZ_MultiClient_Bot", "legacy_task_names": [], "interval_minutes": 15, "auto_launch_in_task": True, "launch_mode": "hidden"},
        "client_defaults": {"main": main_cfg, "farm": farm_cfg},
        "profiles": {},
    }


def _default_config_ref() -> dict[str, Any]:
    """Return the cached read-only default bot configuration template."""
    global _DEFAULT_CONFIG_TEMPLATE
    with _DEFAULT_CONFIG_LOCK:
        if _DEFAULT_CONFIG_TEMPLATE is None:
            _DEFAULT_CONFIG_TEMPLATE = _build_default_config()
        return _DEFAULT_CONFIG_TEMPLATE


def default_config() -> dict[str, Any]:
    """Return a fresh copy of the cached default bot configuration template."""
    return deepcopy(_default_config_ref())


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    target_path = Path(config_path) if config_path is not None else CONFIG_PATH
    cache_key = os.path.normcase(os.path.abspath(str(target_path)))
    defaults = default_config()
    st = None
    for attempt in range(4):
        try:
            st = target_path.stat()
            break
        except FileNotFoundError:
            save_config(defaults, config_path=target_path)
            return defaults
        except PermissionError:
            if attempt < 3:
                time.sleep(0.03)
                continue
            with _CONFIG_CACHE_LOCK:
                cached = _CONFIG_CACHE.get(cache_key)
                if cached is not None:
                    return deepcopy(cached[1])
            raise
    assert st is not None
    sig = _stat_sig(st)
    with _CONFIG_CACHE_LOCK:
        cached = _CONFIG_CACHE.get(cache_key)
        if cached is not None and cached[0] == sig:
            return deepcopy(cached[1])
    for attempt in range(4):
        try:
            with target_path.open("r", encoding="utf-8") as fh:
                sig_open = _stat_sig(os.fstat(fh.fileno()))
                loaded = json.load(fh)
            break
        except FileNotFoundError:
            save_config(defaults, config_path=target_path)
            return defaults
        except PermissionError:
            if attempt < 3:
                time.sleep(0.03)
                continue
            with _CONFIG_CACHE_LOCK:
                cached = _CONFIG_CACHE.get(cache_key)
                if cached is not None:
                    return deepcopy(cached[1])
            raise
    if not isinstance(loaded, dict):
        loaded = {}
    merged = _deep_merge(defaults, loaded)
    with _CONFIG_CACHE_LOCK:
        if len(_CONFIG_CACHE) > 32:
            _CONFIG_CACHE.clear()
        _CONFIG_CACHE[cache_key] = (sig_open, deepcopy(merged))
    return deepcopy(merged)


def save_config(cfg: dict[str, Any], config_path: Path | None = None) -> None:
    config_path = Path(config_path) if config_path is not None else CONFIG_PATH
    cache_key = os.path.normcase(os.path.abspath(str(config_path)))
    config_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = config_path.with_name(f"{config_path.name}.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        for attempt in range(5):
            try:
                os.replace(tmp_path, config_path)
                break
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05)
    finally:
        with _CONFIG_CACHE_LOCK:
            _CONFIG_CACHE.pop(cache_key, None)
        try:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def resolve_client_config(cfg_root: dict[str, Any], label: str, role: str) -> dict[str, Any]:
    default_defs = _default_config_ref().get("client_defaults", {})
    defaults = cfg_root.get("client_defaults", {})
    role_key = "main" if str(role).lower() == "main" else "farm"
    base_default = default_defs.get(role_key, default_defs.get("farm", {}))
    base = _deep_merge(base_default, defaults.get(role_key, defaults.get("farm", {})))
    override = cfg_root.get("profiles", {}).get(label, {})
    resolved = _deep_merge(base, override) if override else base
    global_tasks = cfg_root.get("enabled_tasks")
    if isinstance(global_tasks, dict):
        merged_tasks = dict(resolved.get("tasks", {}))
        for k, v in global_tasks.items():
            if not bool(v):
                merged_tasks[k] = False
        resolved["tasks"] = merged_tasks
    return resolved


def _update_protected_uids(cfg_root: dict[str, Any], discovered: list[dict[str, Any]], running_snaps: list[dict[str, Any]]) -> list[str]:
    uids: list[str] = []
    seen: set[str] = set()
    for src in (
        list(cfg_root.get("discovered_protected_uids", [])),
        [c.get("reg_uid") or c.get("uid") for c in discovered],
        [s.get("uid") for s in running_snaps],
    ):
        for item in src:
            sval = str(item or "").strip()
            if sval and sval not in seen:
                seen.add(sval)
                uids.append(sval)
    if uids != cfg_root.get("discovered_protected_uids", []):
        cfg_root["discovered_protected_uids"] = uids
        save_config(cfg_root)
    return uids


def _wait_client_ready(
    cd: Any,
    ba: Any,
    pid: int,
    logger: logging.Logger | None = None,
    timeout: float = 20.0,
    poll_interval: float = 1.5,
) -> dict[str, Any]:
    """Wait briefly for a freshly booted Last Z client to finish UI/ChatInterface init."""
    deadline = time.time() + max(0.0, float(timeout))
    snap = ba.snapshot_client(cd, pid)
    while (not snap.get("ok") or not snap.get("ready", True)) and time.time() < deadline:
        err_low = str(snap.get("error") or "").lower()
        if any(tok in err_low for tok in ("unable to find", "process not found", "no such process", "not running")):
            break
        if logger:
            logger.info(
                "Client PID %s still initializing (ok=%s, ready=%s); waiting...",
                pid,
                snap.get("ok"),
                snap.get("ready"),
            )
        time.sleep(min(float(poll_interval), max(0.1, deadline - time.time())))
        snap = ba.snapshot_client(cd, pid)
    if snap.get("ok") and not snap.get("ready", True):
        snap["ok"] = False
        snap["error"] = snap.get("error") or "client_not_ready (still initializing UI / ChatInterface)"
    return snap


def _normalize_target_token(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"^\[[^\]]+\]\s*", "", str(s))
    s = s.replace("²", "2").replace("³", "3").replace("¹", "1").replace("⁴", "4")
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _matches_target(proc_or_client: dict[str, Any], target: str) -> bool:
    t = str(target or "all").strip()
    if not t or t.lower() in ("all", "auto"):
        return True

    # PID extraction from display strings like "Main (PID 12345)" or "(PID 12345)"
    pid_match = re.search(r"\(?PID[:\s]+(\d+)\)?", t, re.IGNORECASE)
    if pid_match:
        extracted_pid = int(pid_match.group(1))
        proc_pid = proc_or_client.get("pid")
        try:
            proc_pid_int = int(proc_pid) if proc_pid is not None else None
        except (ValueError, TypeError):
            proc_pid_int = None

        if proc_pid_int is not None and proc_pid_int > 0:
            return proc_pid_int == extracted_pid
        # For non-running/discovered clients lacking a pid, strip the PID tag and match by prefix/label
        t = re.sub(r"\(?PID[:\s]+\d+\)?", "", t, flags=re.IGNORECASE).strip()
        if not t:
            return False

    if t.isdigit() and int(t) == int(proc_or_client.get("pid") or -1):
        return True

    tl = t.lower()
    t_norm = _normalize_target_token(t)

    if tl in ("main", "main_only") or t_norm in ("main", "heinzy", "heinzy1"):
        if str(proc_or_client.get("role") or "").lower() == "main":
            return True
        lbl = str(proc_or_client.get("label") or "").lower()
        prof = str(proc_or_client.get("unity_profile") or "").lower()
        uid = str(proc_or_client.get("uid") or proc_or_client.get("reg_uid") or "")
        cname = _normalize_target_token(proc_or_client.get("name") or "")
        if lbl in ("main", "lastz") or prof in ("lastz", "main") or uid == "1483575381000694" or cname in ("heinzy", "heinzy1"):
            return True
        return False

    if tl in ("farms", "all_farms"):
        return str(proc_or_client.get("role") or "").lower() == "farm"

    if tl.startswith("role:"):
        return str(proc_or_client.get("role") or "").lower() == tl[5:]

    # Heinzy2 / Third / Alt3Z alias matching
    if t_norm in ("heinzy2", "third", "alt3z"):
        lbl = str(proc_or_client.get("label") or "").lower()
        prof = str(proc_or_client.get("unity_profile") or "").lower()
        uid = str(proc_or_client.get("uid") or proc_or_client.get("reg_uid") or "")
        cname = _normalize_target_token(proc_or_client.get("name") or "")
        if lbl in ("third", "alt3z") or prof in ("alt3z", "third") or uid == "1848029704000694" or cname == "heinzy2":
            return True

    # FarmZ / Farm alias matching
    if t_norm in ("farm", "farmz"):
        lbl = str(proc_or_client.get("label") or "").lower()
        prof = str(proc_or_client.get("unity_profile") or "").lower()
        uid = str(proc_or_client.get("uid") or proc_or_client.get("reg_uid") or "")
        if lbl in ("farm", "farmz") or prof in ("farmz", "farm") or uid == "2066965117000694":
            return True

    # Field-level exact and normalized matching
    for field in ("id", "label", "unity_profile", "exe_name", "uid", "reg_uid", "name", "statusText"):
        val = str(proc_or_client.get(field) or "")
        if val.lower() == tl or (t_norm and _normalize_target_token(val) == t_norm):
            return True

    return False


def _ensure_targets_running(
    cd: Any,
    cfg_root: dict[str, Any],
    target: str,
    auto_launch: bool,
    logger: logging.Logger,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    discovery = cd.discover_clients(save_cache=True)
    discovered_clients = discovery.get("clients", []) if isinstance(discovery, dict) else list(discovery or [])
    running = cd.find_running_processes()

    if auto_launch:
        sfc = _load_module("sync_farm_clients", TOOLS_DIR / "sync farm clients.py")
        running_labels = {str(p.get("label") or "").lower() for p in running}
        running_profiles = {str(p.get("unity_profile") or "").lower() for p in running}
        for client in discovered_clients:
            if not _matches_target(client, target):
                continue
            label = str(client.get("label") or client.get("unity_profile") or "")
            prof = str(client.get("unity_profile") or "")
            if label.lower() in running_labels or prof.lower() in running_profiles:
                continue
            ccfg = resolve_client_config(cfg_root, label, str(client.get("role") or "farm"))
            if not ccfg.get("enabled", True):
                continue
            launch_mode = str(ccfg.get("launch_mode") or cfg_root.get("auto_launch_mode") or "eco")
            logger.info("Auto-launching stopped client %s in %s mode...", label, launch_mode)
            try:
                sfc.launch_client(label or prof, mode=launch_mode, auto_sync=True, wait_xlua=True)
            except Exception as exc:
                logger.warning("Failed to auto-launch %s: %s", label, exc)
        running = cd.find_running_processes()

    return discovered_clients, running


def _format_task_summary(tname: str, res: dict[str, Any]) -> str:
    """Produce clean, readable single-line summary for live progress reporting."""
    if not isinstance(res, dict):
        return str(res)
    if not res.get("ok", True):
        return f"failed ({res.get('error') or res.get('reason') or 'unknown error'})"

    details: list[str] = []
    if tname == "auto_help":
        helps = int(res.get("ally_help_num", 0) or 0)
        t1 = int(res.get("tab1_gifts_claimed", 0) or 0)
        t2 = int(res.get("tab2_chests_claimed", 0) or 0)
        calls = len(res.get("call_helps") or []) if isinstance(res.get("call_helps"), list) else int(res.get("call_helps", 0) or 0)
        parts: list[str] = []
        if helps > 0:
            parts.append(f"{helps} ally help(s)")
        if t1 > 0 or t2 > 0:
            parts.append(f"chests T1={t1}, T2={t2}")
        if calls > 0:
            parts.append(f"{calls} call-help(s)")
        return ", ".join(parts) if parts else str(res.get("message") or "0 helps/chests pending")
    elif tname == "troop_training":
        trained = res.get("trained")
        collected = res.get("collected")
        busy = res.get("busy")
        if isinstance(collected, list) and collected:
            details.append(f"collected {len(collected)} barrack(s)")
        if isinstance(trained, list) and trained:
            cnt = sum(int(item.get("count", 0)) for item in trained if isinstance(item, dict))
            details.append(f"trained {cnt} troops across {len(trained)} barracks")
        if isinstance(busy, list) and busy:
            b_names = [str(item.get("barrack", "")) for item in busy if isinstance(item, dict) and item.get("barrack")]
            details.append(f"{len(busy)} barracks busy ({', '.join(b_names)})")
        return "; ".join(details) if details else str(res.get("message") or "0 troops trained")
    elif tname == "hospital_heal":
        pass_act = int(res.get("pass_active_helpers", 0) or 0)
        eff_helps = int(res.get("effective_max_helps", 0) or 0)
        if res.get("dormant"):
            suffix = f", Pass+Active={pass_act} (max_helps={eff_helps})" if eff_helps > 0 or pass_act > 0 else ""
            return f"dormant (0 wounded troops, headless{suffix})"
        queued = int(res.get("total_queued_troops", res.get("queued_troops", 0)) or 0)
        in_treat = int(res.get("in_treatment_total", 0) or 0)
        untreated = int(res.get("untreated_total", 0) or 0)
        wounded = int(res.get("wounded_total", in_treat + untreated) or 0)
        rem_sec = int(res.get("queue_remaining_sec", 0) or 0)
        batches = int(res.get("batches_chained", 0) or 0)
        cross_helps = int(res.get("cross_client_helps_triggered", 0) or 0)
        parts = []
        if queued > 0:
            parts.append(f"queued {queued} troops" + (f" ({batches} batches)" if batches > 1 else ""))
        if pass_act > 0 or eff_helps > 0:
            parts.append(f"Pass+Active={pass_act} (helps={eff_helps})")
        if cross_helps > 0:
            parts.append(f"{cross_helps} cross-client help(s)")
        if in_treat > 0:
            parts.append(f"{in_treat} in treatment" + (f" ({rem_sec}s left)" if rem_sec > 0 else ""))
        if untreated > 0:
            parts.append(f"{untreated} untreated")
        if not parts:
            parts.append(f"{wounded} wounded in hospital" if wounded > 0 else "0 wounded troops")
        return ", ".join(parts)
    elif tname == "mine_melee_refresh":
        refreshed = int(res.get("refreshed_count", 0) or 0)
        dispatched = int(res.get("dispatched_count", 0) or 0)
        active = res.get("active_mining_marches") or []
        act_cnt = len(active) if isinstance(active, list) else 0
        action_str = str(res.get("action") or "checked")
        return f"{action_str} (active={act_cnt}, refreshed={refreshed}, dispatched={dispatched})"
    elif tname == "alliance_boss_mine":
        parts = []
        if res.get("bear_reward_claimed"):
            parts.append("claimed bear reward")
        if res.get("bear_marched"):
            parts.append("joined bear rally")
        if res.get("mine_dispatched"):
            parts.append("dispatched to alliance mine")
        elif res.get("mine_has_march"):
            parts.append("alliance mine march active")
        return ", ".join(parts) if parts else str(res.get("action") or "checked alliance boss/mine")
    elif tname == "hero_battlefield":
        factions = res.get("factions") or {}
        wins = int(res.get("total_wins", 0) or 0)
        quick_cnt = int(res.get("quick_deploys", 0) or 0)
        skips = int(res.get("skips_triggered", 0) or 0)
        reasons = []
        for fk, f_info in factions.items():
            if isinstance(f_info, dict):
                r = f_info.get("stopped_reason")
                if r:
                    reasons.append(f"{f_info.get('name', f'Faction {fk}')}: {r}")
        head = f"{wins} battle(s) won"
        if quick_cnt > 0 or skips > 0:
            head += f" (quick_deploy={quick_cnt}, skipped={skips})"
        if wins > 0:
            return head + (f" ({'; '.join(reasons)})" if reasons else "")
        elif reasons:
            return f"Guarded ({'; '.join(reasons)})"
        return str(res.get("reason") or res.get("message") or "0 battles fought")
    elif tname == "bounties":
        claimed = "claimed rewards" if res.get("claimed_all") else ""
        dispatched = len(res.get("dispatched") or [])
        helped = len(res.get("ally_helped") or []) if isinstance(res.get("ally_helped"), list) else int(res.get("ally_helped", 0) or 0)
        stolen = len(res.get("stolen") or [])
        refreshed = len(res.get("refreshed") or [])
        skipped = int(res.get("skipped_non_golden", 0) or 0)
        reason = res.get("stopped_reason")
        parts = []
        if claimed:
            parts.append(claimed)
        if dispatched > 0:
            parts.append(f"dispatched {dispatched} gold")
        if helped > 0:
            parts.append(f"helped {helped} ally gold")
        if stolen > 0:
            parts.append(f"plundered {stolen}")
        if refreshed > 0:
            parts.append(f"refreshed {refreshed}x (lock_orange={bool(res.get('lock_orange', True))})")
        if skipped > 0:
            parts.append(f"{skipped} non-golden reviewed")
        if reason:
            parts.append(f"status: {reason}")
        return ", ".join(parts) if parts else "0 bounties to process"
    elif tname == "bounty_steal":
        stolen = len(res.get("stolen") or [])
        cands = len(res.get("candidates") or [])
        return f"plundered {stolen}/{cands} cross-state bounties ({res.get('today_steals', 0)}/{res.get('max_steals', 5)} daily)"
    elif tname == "radar_events":
        scanned = int(res.get("scan_triggered", 0) or 0)
        claimed = len(res.get("claimed_uuids") or [])
        dispatched = len(res.get("dispatched") or [])
        total = int(res.get("total_events", 0) or 0)
        parts = []
        if scanned > 0:
            parts.append(f"scanned +{scanned}x")
        parts.append(f"{claimed} claimed")
        parts.append(f"{dispatched} dispatched (total={total})")
        return ", ".join(parts)
    elif tname == "auto_gather":
        marches = res.get("dispatched") or res.get("marches") or []
        usable = int(res.get("usable_formations", 0) or 0)
        if marches:
            return f"dispatched {len(marches)} gather squad(s)"
        return str(res.get("message") or res.get("reason") or f"usable={usable}, 0 dispatched")
    elif tname == "rf_hq_under_attack":
        alerts = res.get("alerts") or []
        reinf = len(res.get("reinforcements") or [])
        if alerts:
            return f"ALERT: {'; '.join(alerts)}"
        if reinf > 0:
            return f"reinforced {reinf} ally target(s)"
        return f"safe (no incoming attacks, threats={len(res.get('threats') or [])})"
    elif tname == "arena":
        battles = res.get("battles") or []
        fought = int(res.get("battles_fought", 0) or 0)
        wins = sum(1 for b in battles if isinstance(b, dict) and (b.get("match_won") or b.get("accepted")))
        mode = str(res.get("mode") or "1v1")
        return f"{mode}: {fought} battle(s) ({wins}W)" if fought > 0 else str(res.get("reason") or "0 arena attempts")
    elif tname == "daily_tasks_complete":
        return str(res.get("message") or f"attempted={res.get('executed_count', 0)}, score={res.get('score_after', 0)}/{res.get('max_score', 150)}")
    elif tname == "daily_claims":
        dt = int(res.get("daily_tasks_claimed", 0) or 0)
        db = len(res.get("daily_boxes_claimed") or [])
        ach = int(res.get("achievements_claimed", 0) or 0)
        bp = len(res.get("battle_passes_claimed") or [])
        sp = len(res.get("season_passes_claimed") or [])
        wc = int(res.get("week_cards_claimed", 0) or 0)
        mc = int(res.get("month_cards_claimed", 0) or 0)
        ch = int(res.get("chapter_tasks_claimed", 0) or 0)
        mn = int(res.get("main_tasks_claimed", 0) or 0)
        parts = []
        if dt > 0:
            parts.append(f"{dt} daily tasks")
        if db > 0:
            parts.append(f"{db} activity chests")
        if ach > 0:
            parts.append(f"{ach} achievements")
        if bp > 0:
            parts.append(f"{bp} battle passes")
        if sp > 0:
            parts.append(f"{sp} season passes")
        if wc > 0:
            parts.append(f"{wc} week cards")
        if mc > 0:
            parts.append(f"{mc} month cards")
        if ch > 0:
            parts.append(f"{ch} chapter tasks")
        if mn > 0:
            parts.append(f"{mn} main tasks")
        return "claimed " + ", ".join(parts) if parts else str(res.get("message") or "0 daily/pass rewards pending")
    elif tname == "full_preparedness":
        pa = res.get("personal_arms_claimed") or []
        vs = res.get("vs_claimed_stages") or []
        execs = list((res.get("executed_actions") or {}).keys())
        parts = []
        if pa:
            parts.append(f"{len(pa)} preparedness bar(s)")
        if vs:
            parts.append(f"{len(vs)} VS stage(s)")
        if execs:
            parts.append(f"actions={','.join(execs)}")
        return ", ".join(parts) if parts else "checked preparedness & VS stages"
    elif tname == "speedups":
        fin = len(res.get("finished_collected") or [])
        free_sp = len(res.get("free_speeds") or [])
        item_sp = len(res.get("item_speeds") or [])
        parts = []
        if fin > 0:
            parts.append(f"collected {fin}")
        if free_sp > 0:
            parts.append(f"{free_sp} free speed(s)")
        if item_sp > 0:
            parts.append(f"{item_sp} item speedup(s)")
        return ", ".join(parts) if parts else str(res.get("reason") or res.get("action") or "no speedups needed")
    elif tname == "building_upgrades":
        up = res.get("upgraded")
        if isinstance(up, dict):
            return f"upgraded {up.get('itemId')} Lv{up.get('level')}->Lv{up.get('targetLevel')}"
        return str(res.get("message") or res.get("reason") or "no builder queue available")
    elif tname == "mining_event":
        act = res.get("active_mines") or []
        if act:
            r_min = int(act[0].get("remaining_sec", 0)) // 60
            return f"actively mining ({r_min // 60}h {r_min % 60}m remaining)"
        if res.get("attacked"):
            return f"attacked mine #{res['attacked'].get('mineIndex')}"
        return str(res.get("reason") or res.get("status") or "mining check complete")
    elif tname == "trucks":
        claimed = int(res.get("claimed", 0) or 0)
        sent = len(res.get("sent") or res.get("dispatched") or [])
        rerolled = len(res.get("rerolled") or [])
        attacked = len(res.get("attacked") or [])
        parts = []
        if claimed > 0:
            parts.append(f"claimed {claimed}")
        if rerolled > 0:
            parts.append(f"rerolled {rerolled}x")
        if sent > 0:
            parts.append(f"sent {sent}")
        if attacked > 0:
            parts.append(f"raided {attacked}")
        return ", ".join(parts) if parts else str(res.get("message") or res.get("reason") or "0 trucks claimed/sent")
    elif tname == "vip_store_rewards":
        parts = []
        if res.get("claimed_vip_points"):
            parts.append("VIP pts")
        if res.get("claimed_vip_daily"):
            parts.append("VIP chest")
        st_items = res.get("claimed_store_items") or []
        if st_items:
            parts.append(f"{len(st_items)} store freebie(s)")
        if res.get("claimed_weekly_free"):
            parts.append("weekly gift")
        return "claimed " + ", ".join(parts) if parts else "0 VIP/store freebies pending"
    elif tname == "alliance_daily":
        g = int(res.get("gifts_claimed", 0) or 0)
        rp = int(res.get("red_packets_claimed", 0) or 0)
        tk = int(res.get("tasks_claimed", 0) or 0)
        bx = int(res.get("exploit_boxes_claimed", 0) or 0)
        td = int(res.get("tech_donated", 0) or 0)
        parts = []
        if g > 0:
            parts.append(f"{g} gift(s)")
        if rp > 0:
            parts.append(f"{rp} red packet(s)")
        if tk > 0:
            parts.append(f"{tk} task(s)")
        if bx > 0:
            parts.append(f"{bx} box(es)")
        if td > 0:
            parts.append(f"{td}x tech donate")
        return ", ".join(parts) if parts else str(res.get("action") or "0 alliance dailies pending")
    elif tname == "free_recruits":
        hr = len(res.get("hero_recruits") or [])
        ch = int(res.get("chests_total_count", 0) or 0)
        parts = []
        if hr > 0:
            parts.append(f"{hr} hero recruit(s)")
        if ch > 0:
            parts.append(f"{ch} safe chest(s)")
        return "claimed " + ", ".join(parts) if parts else "0 free recruits or chests pending"
    elif tname == "war_safety":
        threats = res.get("threats") or []
        act = str(res.get("action") or "safe")
        if threats:
            return f"{act} ({len(threats)} threat(s) detected)"
        return f"defense shield verified ({act}, shielded={bool(res.get('shielded'))})"
    elif tname == "tyrant_event":
        parts = []
        if res.get("free_reward_claimed"):
            parts.append("free reward")
        if res.get("alliance_reward_claimed"):
            parts.append("alliance reward")
        if res.get("hosted"):
            parts.append("F1 hosted rally")
        joined = len(res.get("joined") or [])
        if joined > 0:
            parts.append(f"joined {joined} rally(s)")
        return ", ".join(parts) if parts else (f"open={bool(res.get('is_open'))}, in_battle={bool(res.get('in_battle'))}")
    elif tname == "area_exploration":
        wins = int(res.get("wins", 0) or 0)
        battles = len(res.get("battles") or [])
        skips = int(res.get("skips_triggered", 0) or 0)
        parts = []
        if res.get("hangup_claimed"):
            parts.append("idle chest claimed")
        if res.get("jumped"):
            parts.append(f"batch jumped -> stage {res.get('order')}")
        if battles > 0:
            parts.append(f"{wins}/{battles} battles won (skipped={skips})")
        return ", ".join(parts) if parts else str(res.get("stopped_reason") or "checked area exploration")
    elif tname == "research_queue":
        started = res.get("started")
        if isinstance(started, list) and started:
            sids = [str(s.get("scienceId")) for s in started if isinstance(s, dict) and s.get("scienceId")]
            return f"started research {', '.join(sids)}"
        if isinstance(started, dict) and started.get("techId"):
            return f"started research tech #{started.get('techId')}"
        return str(res.get("action") or "checked research queue")
    elif tname == "garage_upgrades":
        steps = int(res.get("refit_steps", 0) or 0)
        if steps > 0 or res.get("installed_all") or res.get("merged_slots"):
            return f"upgraded garage (refit_steps={steps}, installed={bool(res.get('installed_all'))}, merged={len(res.get('merged_slots') or [])})"
        return str(res.get("action") or "checked garage upgrades")
    elif tname == "hero_progression":
        total_act = int(res.get("total_actions", 0) or 0)
        if total_act > 0:
            return (
                f"hero progression {total_act} action(s) "
                f"(lv={len(res.get('level_ups') or [])}, break={len(res.get('breakthroughs') or [])}, "
                f"star={len(res.get('star_ups') or [])}, skill={len(res.get('skill_ups') or [])}, "
                f"equip={len(res.get('gear_installed') or [])}, gear={len(res.get('gear_upgraded') or [])}, "
                f"promote={len(res.get('gear_promoted') or [])}, weapon={len(res.get('sp_upgraded') or [])})"
            )
        return str(res.get("reason") or res.get("action") or "checked hero progression")
    elif tname == "furylord":
        if isinstance(res.get("dispatched"), dict):
            return f"attacked Furylord pt={res['dispatched'].get('pointId')} (F{res['dispatched'].get('formationIndex')})"
        return str(res.get("reason") or res.get("action") or "checked furylord status")
    elif tname == "treasure_helicopter":
        det = len(res.get("detected") or [])
        marched = len(res.get("marched") or [])
        claims = len(res.get("claims_executed") or [])
        return f"detected={det}, marched={marched}, claimed={claims}"
    elif tname == "boomer_runs":
        if res.get("joined"):
            return f"joined boomer rally {res['joined'].get('warUuid')}"
        if res.get("started_rally"):
            return f"started Lv{res['started_rally'].get('level')} boomer rally pt={res['started_rally'].get('pointId')}"
        return str(res.get("reason") or f"open_rallies={res.get('open_rallies', 0)}")
    elif tname == "dismiss_popups":
        cnt = int(res.get("dismissed_count", 0) or 0)
        return f"dismissed {cnt} modal(s)" if cnt > 0 else "no open modals"

    parts = []
    for k, v in res.items():
        if k in ("ok", "task", "dry_run", "in_game_tips", "tips", "stage_id", "stage_tag", "duration_ms", "detail_lines", "popped_modals", "send_errors"):
            continue
        if v and not isinstance(v, (dict, list)):
            parts.append(f"{k}={v}")
    return ", ".join(parts[:3]) if parts else "complete"


# ---------------------------------------------------------------------------
# 5-Stage Sequential State Machine Helpers
# ---------------------------------------------------------------------------
_STAGE_STATE_CACHE: dict[str, tuple[tuple[int, int, int, int], dict[str, Any]]] = {}
_STAGE_STATE_CACHE_LOCK = threading.Lock()


def _load_stage_state(path: Path | None = None) -> dict[str, Any]:
    target_path = Path(path) if path is not None else STAGE_STATE_PATH
    cache_key = os.path.normcase(os.path.abspath(str(target_path)))
    try:
        st = target_path.stat()
    except OSError:
        return {"version": 1, "clients": {}}
    sig = _stat_sig(st)
    with _STAGE_STATE_CACHE_LOCK:
        cached = _STAGE_STATE_CACHE.get(cache_key)
        if cached is not None and cached[0] == sig:
            return deepcopy(cached[1])
    try:
        with target_path.open("r", encoding="utf-8") as fh:
            sig_open = _stat_sig(os.fstat(fh.fileno()))
            data = json.loads(fh.read())
        if isinstance(data, dict) and isinstance(data.get("clients"), dict):
            with _STAGE_STATE_CACHE_LOCK:
                if len(_STAGE_STATE_CACHE) > 32:
                    _STAGE_STATE_CACHE.clear()
                _STAGE_STATE_CACHE[cache_key] = (sig_open, deepcopy(data))
            return deepcopy(data)
    except Exception:
        pass
    return {"version": 1, "clients": {}}


def _save_stage_state(state: dict[str, Any], path: Path | None = None) -> None:
    target_path = Path(path) if path is not None else STAGE_STATE_PATH
    cache_key = os.path.normcase(os.path.abspath(str(target_path)))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_name(f"{target_path.stem}.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, ensure_ascii=False)
        for attempt in range(5):
            try:
                os.replace(tmp_path, target_path)
                break
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05)
    except Exception as exc:
        logging.getLogger("multi_client_bot").warning("Failed to save stage state to %s: %s", target_path, exc)
    finally:
        with _STAGE_STATE_CACHE_LOCK:
            _STAGE_STATE_CACHE.pop(cache_key, None)
        try:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _resolve_stage_cooldown_sec(stage_def: dict[str, Any], sm_cfg: dict[str, Any]) -> float:
    stage_id = str(stage_def["stage_id"])
    cd_map = sm_cfg.get("stage_cooldowns_seconds")
    if isinstance(cd_map, dict) and stage_id in cd_map:
        try:
            return max(0.0, float(cd_map[stage_id]))
        except (ValueError, TypeError):
            pass
    return max(0.0, float(stage_def.get("default_cooldown_sec", 0.0)))


def _resolve_task_callable(ba: Any, tname: str) -> Callable[..., dict[str, Any]] | None:
    """Resolve task handler from bot_actions TASK_REGISTRY or standalone bot_mine_melee module."""
    registry = getattr(ba, "TASK_REGISTRY", None)
    if isinstance(registry, dict) and tname in registry:
        return registry[tname]
    for attr in (f"run_{tname}", f"action_{tname}", tname):
        fn = getattr(ba, attr, None)
        if callable(fn):
            return fn
    if tname == "mine_melee_refresh":
        mm_path = TOOLS_DIR / "bot mine melee.py"
        if mm_path.exists():
            try:
                mm_mod = _load_module("bot_mine_melee", mm_path)
                for attr in ("action_mine_melee_refresh", "run_mine_melee_refresh"):
                    fn = getattr(mm_mod, attr, None)
                    if callable(fn):
                        return fn
            except Exception:
                return None
    return None


_DOWNSTREAM_MARCH_TASKS: tuple[str, ...] = (
    "radar_events",
    "treasure_helicopter",
    "boomer_runs",
    "furylord",
    "tyrant_event",
    "daily_tasks_complete",
)


def _compute_effective_gather_reserve(
    ccfg: dict[str, Any],
    snap: dict[str, Any],
    shared_ctx: dict[str, Any] | None = None,
) -> int:
    """Prevent mine_melee_refresh from starving downstream event/radar/boss marches in a full cycle."""
    mm_cfg = ccfg.get("mine_melee_refresh") or {}
    base_reserve = int(mm_cfg.get("reserve_formations", ccfg.get("formation_reserve", 1)) or 0)
    task_filter = (shared_ctx or {}).get("task_filter")
    if isinstance(task_filter, (list, tuple, set)) and set(task_filter) == {"mine_melee_refresh"}:
        return max(0, base_reserve)
    tasks_map = ccfg.get("tasks") or {}
    has_downstream_march = any(
        bool(tasks_map.get(t))
        and (not task_filter or t in task_filter)
        for t in _DOWNSTREAM_MARCH_TASKS
    )
    if not has_downstream_march:
        return max(0, base_reserve)
    unlocked = int(snap.get("unlockFormations") or snap.get("unlock_formations") or 0)
    if unlocked == 1:
        return max(0, base_reserve)
    return max(1, base_reserve)


_TASK_SIG_CACHE_LOCK = threading.Lock()
_TASK_SIG_CACHE: dict[int, tuple[Any, str]] = {}


def _invoke_stage_task(
    ba: Any,
    cd: Any,
    pid: int,
    snap: dict[str, Any],
    ccfg: dict[str, Any],
    tname: str,
    dry_run: bool,
    shared_ctx: dict[str, Any],
) -> dict[str, Any]:
    """Execute a single stage task, adapting seamlessly to either bot_actions or bot_mine_melee signatures."""
    fn = _resolve_task_callable(ba, tname)
    if fn is None:
        return {"ok": False, "task": tname, "dry_run": dry_run, "error": f"task_handler_not_found ({tname})"}

    fn_id = id(fn)
    with _TASK_SIG_CACHE_LOCK:
        cached = _TASK_SIG_CACHE.get(fn_id)
    if cached is not None and cached[0] is fn:
        third_param_name = cached[1]
    else:
        try:
            sig = inspect.signature(fn)
            params = list(sig.parameters.values())
            third_param_name = params[2].name if len(params) >= 3 else ""
        except Exception:
            third_param_name = ""
        with _TASK_SIG_CACHE_LOCK:
            if len(_TASK_SIG_CACHE) >= 256:
                _TASK_SIG_CACHE.clear()
            _TASK_SIG_CACHE[fn_id] = (fn, third_param_name)
    if third_param_name == "dry_run" or (tname == "mine_melee_refresh" and third_param_name not in ("client_state", "snap")):
        mm_cfg = ccfg.get("mine_melee_refresh") or {}
        eff_reserve = _compute_effective_gather_reserve(ccfg, snap, shared_ctx)
        kwargs: dict[str, Any] = {
            "dry_run": dry_run,
            "refresh_threshold_sec": int(mm_cfg.get("refresh_threshold_sec", 300)),
            "min_payload_pct": float(mm_cfg.get("min_payload_pct", 10.0)),
            "reserve_formations": eff_reserve,
            "client_state": snap,
            "cfg": ccfg,
            "context": shared_ctx,
        }
        try:
            res = fn(cd, pid, **kwargs)
        except TypeError:
            res = fn(cd, pid, snap, ccfg, dry_run=dry_run, context=shared_ctx)
        if isinstance(res, dict):
            res.setdefault("effective_reserve_formations", eff_reserve)
        return res

    try:
        return fn(cd, pid, snap, ccfg, dry_run=dry_run, context=shared_ctx)
    except TypeError:
        mm_cfg = ccfg.get(tname) if isinstance(ccfg.get(tname), dict) else {}
        return fn(cd, pid, dry_run=dry_run, **(mm_cfg or {}))


def _resolve_stage_tasks(
    stage_def: dict[str, Any],
    ccfg: dict[str, Any],
    sm_cfg: dict[str, Any],
    task_filter: list[str] | None,
) -> tuple[list[str], list[str]]:
    """Return (candidate_tasks_for_stage, enabled_tasks_to_run) for a stage."""
    canonical = list(stage_def.get("tasks", ()))
    extended = list(stage_def.get("extended_tasks", ()))
    include_ext = bool(sm_cfg.get("include_extended_tasks", False))

    candidates = list(canonical)
    if include_ext:
        for t in extended:
            if t not in candidates:
                candidates.append(t)
    elif task_filter:
        for t in extended:
            if t in task_filter and t not in candidates:
                candidates.append(t)
        if stage_def.get("stage_id") == 5 and "bounty_steal" in task_filter and "bounty_steal" not in candidates:
            candidates.append("bounty_steal")

    tasks_cfg = ccfg.get("tasks", {})
    if task_filter:
        active = [t for t in candidates if t in task_filter]
        return candidates, active

    active = [t for t in candidates if bool(tasks_cfg.get(t, True))]
    # Stage 1 safety guarantee: when preempt_on_attack is enabled, always run at least one Stage 1 safety probe
    if stage_def["stage_id"] == 1 and not active and bool(sm_cfg.get("preempt_on_attack", True)):
        active = list(canonical)
    return candidates, active


def _evaluate_stage_entry_guard(
    stage_def: dict[str, Any],
    client_key: str,
    snap: dict[str, Any],
    ccfg: dict[str, Any],
    sm_cfg: dict[str, Any],
    stage_state: dict[str, Any],
    emergency_state: dict[str, Any],
    task_filter: list[str] | None,
    dry_run: bool,
    now_ts: float,
    ignore_cooldowns: bool = False,
) -> dict[str, Any]:
    """Explicit stage entry guard validating preemption, client readiness, task eligibility, and cooldown locks."""
    stage_id = int(stage_def["stage_id"])
    stage_key = str(stage_def["key"])
    cooldown_sec = _resolve_stage_cooldown_sec(stage_def, sm_cfg)

    # 1. Stage 1 Emergency Preemption check for lower-priority stages (Stages 2..5)
    if stage_id > 1 and emergency_state.get("preempt_lower_stages"):
        return {
            "allowed": False,
            "stage_id": stage_id,
            "status": "preempted_by_stage_1",
            "reason": str(emergency_state.get("reason") or "Active Stage 1 attack/emergency unconfirmed safe"),
            "cooldown_sec": cooldown_sec,
            "cooldown_locked": False,
            "remaining_cooldown_sec": 0.0,
            "candidate_tasks": list(stage_def.get("tasks", ())),
            "scheduled_tasks": [],
        }

    # 2. Client readiness guard
    if not snap.get("ok", False):
        return {
            "allowed": False,
            "stage_id": stage_id,
            "status": "client_not_ready",
            "reason": str(snap.get("error") or "client snapshot not ok"),
            "cooldown_sec": cooldown_sec,
            "cooldown_locked": False,
            "remaining_cooldown_sec": 0.0,
            "candidate_tasks": list(stage_def.get("tasks", ())),
            "scheduled_tasks": [],
        }

    # 3. Task selection guard
    candidates, scheduled = _resolve_stage_tasks(stage_def, ccfg, sm_cfg, task_filter)
    if not scheduled:
        status = "filtered_out" if task_filter else "no_enabled_tasks"
        return {
            "allowed": False,
            "stage_id": stage_id,
            "status": status,
            "reason": f"No runnable tasks in Stage {stage_id} ({status})",
            "cooldown_sec": cooldown_sec,
            "cooldown_locked": False,
            "remaining_cooldown_sec": 0.0,
            "candidate_tasks": candidates,
            "scheduled_tasks": [],
        }

    # 4. Per-stage cooldown lock guard
    client_locks = stage_state.get("clients", {}).get(client_key, {}).get("stages", {})
    mem_locks = _MEMORY_STAGE_LOCKS.get(client_key, {})
    persisted_entry = client_locks.get(stage_key) or client_locks.get(str(stage_id)) or {}
    mem_entry = mem_locks.get(stage_key) or {}
    lock_until = max(
        float(persisted_entry.get("lock_until", 0.0) or 0.0),
        float(mem_entry.get("lock_until", 0.0) or 0.0),
    )
    remaining_cd = max(0.0, lock_until - now_ts)
    is_cd_active = remaining_cd > 0.0 and cooldown_sec > 0.0
    enforce_cd = bool(sm_cfg.get("enforce_cooldowns", True))
    enforce_in_dry = bool(sm_cfg.get("enforce_cooldowns_in_dry_run", False))

    if is_cd_active and enforce_cd and not ignore_cooldowns and not task_filter and (not dry_run or enforce_in_dry):
        return {
            "allowed": False,
            "stage_id": stage_id,
            "status": "cooldown_locked",
            "reason": f"Stage {stage_id} cooldown lock active ({remaining_cd:.1f}s remaining of {cooldown_sec:.1f}s)",
            "cooldown_sec": cooldown_sec,
            "cooldown_locked": True,
            "remaining_cooldown_sec": round(remaining_cd, 2),
            "candidate_tasks": candidates,
            "scheduled_tasks": scheduled,
        }

    return {
        "allowed": True,
        "stage_id": stage_id,
        "status": "ready",
        "reason": "entry_guard_passed",
        "cooldown_sec": cooldown_sec,
        "cooldown_locked": False,
        "cooldown_lock_observed": is_cd_active,
        "remaining_cooldown_sec": round(remaining_cd, 2),
        "candidate_tasks": candidates,
        "scheduled_tasks": scheduled,
    }


def _evaluate_stage1_emergency(
    stage1_results: dict[str, dict[str, Any]],
    snap: dict[str, Any],
    sm_cfg: dict[str, Any],
    shared_ctx: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Inspect Stage 1 (`war_safety`, `rf_hq_under_attack`) telemetry to detect active attacks/emergencies."""
    preempt_enabled = bool(sm_cfg.get("preempt_on_attack", True))
    strict_preempt = bool(sm_cfg.get("strict_emergency_preempt", True))
    reasons: list[str] = []
    self_under_attack = False
    shielded = bool(snap.get("shielded", False))
    shield_activated_now = False
    emergency_action = False

    if isinstance(shared_ctx, dict) and shared_ctx.get("simulate_stage1_emergency"):
        self_under_attack = True
        reasons.append("simulated_stage1_emergency")

    ws_res = stage1_results.get("war_safety")
    if isinstance(ws_res, dict):
        if ws_res.get("shielded"):
            shielded = True
        if ws_res.get("shield_used"):
            shield_activated_now = True
            emergency_action = True
        ws_act = str(ws_res.get("action") or "safe")
        if ws_act in ("under_attack_war_fever_blocked_shield", "shield_activated", "recalled_gatherers"):
            emergency_action = True
            reasons.append(f"war_safety:{ws_act}")
        for th in ws_res.get("threats") or []:
            if isinstance(th, dict) and (th.get("hits_self") or th.get("isSelf")):
                self_under_attack = True
                reasons.append(f"war_safety_self_threat(eta={th.get('etaSec', '?')}s)")

    rf_res = stage1_results.get("rf_hq_under_attack")
    if isinstance(rf_res, dict):
        if rf_res.get("shielded"):
            shielded = True
        if rf_res.get("shield_used"):
            shield_activated_now = True
            emergency_action = True
        if rf_res.get("self_under_attack"):
            self_under_attack = True
            reasons.append("rf_hq_under_attack:self_under_attack")
        for alert in rf_res.get("alerts") or []:
            al_str = str(alert or "")
            if "SELF HQ ATTACKED" in al_str or "NO_PEACE_SHIELD_IN_BAG" in al_str:
                self_under_attack = True
                reasons.append(al_str)

    # Active attack detected if self_under_attack or emergency_action fired
    attack_detected = self_under_attack or emergency_action
    # Safety is confirmed only when no unshielded self-attack is active (and if strict_preempt, no emergency action fired this tick)
    if not attack_detected:
        safety_confirmed = True
    elif shielded and not shield_activated_now and not strict_preempt:
        safety_confirmed = True
    else:
        safety_confirmed = False

    should_preempt = bool(preempt_enabled and attack_detected and not safety_confirmed)
    return {
        "attack_detected": attack_detected,
        "self_under_attack": self_under_attack,
        "shielded": shielded,
        "shield_activated_now": shield_activated_now,
        "safety_confirmed": safety_confirmed,
        "preempt_lower_stages": should_preempt,
        "reason": "; ".join(reasons) if reasons else "stage_1_clear_safety_confirmed",
    }


def _evaluate_stage_exit_guard(
    stage_def: dict[str, Any],
    client_key: str,
    ba: Any,
    cd: Any,
    pid: int,
    stage_task_results: dict[str, dict[str, Any]],
    sm_cfg: dict[str, Any],
    stage_state: dict[str, Any],
    emergency_state: dict[str, Any],
    dry_run: bool,
    now_ts: float,
) -> dict[str, Any]:
    """Explicit stage exit guard: verifies task completion, drains popups, and locks stage cooldown."""
    stage_id = int(stage_def["stage_id"])
    stage_key = str(stage_def["key"])
    cooldown_sec = _resolve_stage_cooldown_sec(stage_def, sm_cfg)

    executed_tasks = list(stage_task_results.keys())
    failed_tasks = [t for t, r in stage_task_results.items() if not isinstance(r, dict) or not r.get("ok", False)]
    all_ok = len(executed_tasks) > 0 and len(failed_tasks) == 0

    # Completion verification: dismiss leftover modal dialogs only when needed (modal logged, failure, or forced)
    popups_dismissed = 0
    client_responsive = True
    has_queued_modals = any(
        isinstance(r, dict) and bool(r.get("popped_modals") or r.get("modal_dialogs"))
        for r in stage_task_results.values()
    )
    need_popup_sweep = (
        not dry_run
        and bool(executed_tasks)
        and bool(sm_cfg.get("verify_client_between_stages", True))
        and (has_queued_modals or bool(failed_tasks) or bool(sm_cfg.get("always_sweep_popups_between_stages", False)))
    )
    if need_popup_sweep:
        try:
            if hasattr(ba, "dismiss_all_popups"):
                d_res = ba.dismiss_all_popups(cd, pid, dry_run=dry_run)
                if isinstance(d_res, dict):
                    popups_dismissed = int(d_res.get("dismissed_count", 0) or 0)
                    client_responsive = bool(d_res.get("ok", True))
        except Exception:
            client_responsive = True

    verified = all_ok and client_responsive
    lock_until = (now_ts + cooldown_sec) if cooldown_sec > 0.0 else now_ts

    # Update in-memory and persistent stage cooldown locks
    lock_record = {
        "stage_id": stage_id,
        "stage_key": stage_key,
        "last_completed_at": datetime.fromtimestamp(now_ts, tz=timezone.utc).isoformat(),
        "last_completed_ts": round(now_ts, 3),
        "cooldown_sec": cooldown_sec,
        "lock_until": round(lock_until, 3) if not dry_run else 0.0,
        "dry_run_lock_until": round(lock_until, 3),
        "verified": verified,
        "executed_tasks": executed_tasks,
        "failed_tasks": failed_tasks,
    }
    _MEMORY_STAGE_LOCKS.setdefault(client_key, {})[stage_key] = lock_record
    c_state = stage_state.setdefault("clients", {}).setdefault(client_key, {"stages": {}})
    c_state.setdefault("stages", {})[stage_key] = lock_record
    c_state["last_updated_at"] = lock_record["last_completed_at"]

    if stage_id == 1 and emergency_state.get("preempt_lower_stages"):
        exit_status = "emergency_preempt_triggered"
    elif all_ok:
        exit_status = "completed_verified"
    elif executed_tasks:
        exit_status = "completed_with_errors"
    else:
        exit_status = "no_tasks_executed"

    return {
        "stage_id": stage_id,
        "status": exit_status,
        "verified": verified,
        "all_tasks_ok": all_ok,
        "client_responsive": client_responsive,
        "popups_dismissed": popups_dismissed,
        "executed_count": len(executed_tasks),
        "failed_tasks": failed_tasks,
        "cooldown_lock_sec": cooldown_sec,
        "lock_until_ts": round(lock_until, 3),
    }


def run_client_stage_machine(
    cd: Any,
    ba: Any,
    pid: int,
    label: str,
    role: str,
    snap: dict[str, Any],
    ccfg: dict[str, Any],
    cfg_root: dict[str, Any],
    shared_ctx: dict[str, Any],
    stage_state: dict[str, Any],
    task_filter: list[str] | None = None,
    dry_run: bool = False,
    logger: logging.Logger | None = None,
    ignore_cooldowns: bool = False,
) -> dict[str, Any]:
    """Execute the deterministic 5-Stage Sequential State Machine for a single client."""
    logger = logger or _configure_logging()
    sm_cfg = cfg_root.get("stage_machine") or default_config()["stage_machine"]
    client_key = str(snap.get("uid") or label or f"PID:{pid}")
    inter_stage_delay = max(0.0, float(sm_cfg.get("inter_stage_delay_seconds", 0.2)))
    inter_task_delay = max(0.0, float(sm_cfg.get("inter_task_delay_seconds", 0.08)))

    task_results: dict[str, Any] = {}
    stage_reports: list[dict[str, Any]] = []
    emergency_state: dict[str, Any] = {
        "attack_detected": False,
        "self_under_attack": False,
        "shielded": bool(snap.get("shielded", False)),
        "safety_confirmed": True,
        "preempt_lower_stages": False,
        "reason": "uninitialized",
    }
    task_idx = 0
    total_stages = len(STAGE_DEFINITIONS)

    for s_idx, stage_def in enumerate(STAGE_DEFINITIONS):
        stage_id = int(stage_def["stage_id"])
        stage_tag = str(stage_def["tag"])
        stage_name = str(stage_def["name"])
        stage_start_ts = time.time()

        entry_guard = _evaluate_stage_entry_guard(
            stage_def=stage_def,
            client_key=client_key,
            snap=snap,
            ccfg=ccfg,
            sm_cfg=sm_cfg,
            stage_state=stage_state,
            emergency_state=emergency_state,
            task_filter=task_filter,
            dry_run=dry_run,
            now_ts=stage_start_ts,
            ignore_cooldowns=ignore_cooldowns,
        )

        if not entry_guard["allowed"]:
            skip_status = entry_guard["status"]
            skip_reason = entry_guard["reason"]
            logger.info(
                "%s [%s] Stage %d (%s) ENTRY GUARD -> %s (%s)",
                stage_tag,
                label,
                stage_id,
                stage_name,
                skip_status.upper(),
                skip_reason,
            )
            print(
                f"{stage_tag} [{label}] --- SKIP Stage {stage_id}: {stage_name} [{skip_status}: {skip_reason}]",
                flush=True,
            )
            stage_reports.append(
                {
                    "stage_id": stage_id,
                    "tag": stage_tag,
                    "key": stage_def["key"],
                    "name": stage_name,
                    "status": skip_status,
                    "preempted": skip_status == "preempted_by_stage_1",
                    "verified": False,
                    "entry_guard": entry_guard,
                    "exit_guard": None,
                    "tasks_executed": [],
                    "task_results": {},
                    "duration_ms": int((time.time() - stage_start_ts) * 1000),
                    "pacing_delay_sec": 0.0,
                }
            )
            continue

        scheduled_tasks: list[str] = entry_guard["scheduled_tasks"]
        logger.info(
            "%s [%s] >>> ENTER Stage %d/%d: %s (tasks=%s, cooldown=%ss)",
            stage_tag,
            label,
            stage_id,
            total_stages,
            stage_name,
            ",".join(scheduled_tasks),
            entry_guard["cooldown_sec"],
        )
        print(
            f"{stage_tag} [{label}] >>> ENTER {stage_name} (tasks: {', '.join(scheduled_tasks)})",
            flush=True,
        )

        stage_task_results: dict[str, dict[str, Any]] = {}
        for t_pos, tname in enumerate(scheduled_tasks):
            task_idx += 1
            t_title = tname.replace("_", " ").title()
            t_start = time.time()
            try:
                res = _invoke_stage_task(ba, cd, pid, snap, ccfg, tname, dry_run=dry_run, shared_ctx=shared_ctx)
                if not isinstance(res, dict):
                    res = {"ok": True, "task": tname, "result": res}
            except Exception as exc:
                res = {"ok": False, "task": tname, "error": str(exc)}
            res.setdefault("stage_id", stage_id)
            res.setdefault("stage_tag", stage_tag)
            res.setdefault("duration_ms", int((time.time() - t_start) * 1000))

            task_results[tname] = res
            stage_task_results[tname] = res

            summary_text = _format_task_summary(tname, res)
            print(f"[BOT_STEP] {task_idx}) [{label}] {stage_tag} {tname} ({t_title}): {summary_text}", flush=True)

            if not res.get("detail_lines") and hasattr(ba, "_build_detail_lines"):
                try:
                    res["detail_lines"] = ba._build_detail_lines(tname, res)
                except Exception:
                    pass
            detail_lines = res.get("detail_lines")
            if isinstance(detail_lines, (list, tuple)):
                for d_line in detail_lines:
                    ds = str(d_line or "").strip()
                    if ds:
                        print(f"[BOT_DETAIL] [{label}] ({tname}) {ds}", flush=True)

            tips = _clean_tips_list(res.get("in_game_tips") or res.get("tips") or [])
            if "in_game_tips" in res:
                res["in_game_tips"] = tips
            if "tips" in res:
                res["tips"] = tips
            for tip in tips:
                print(f"[BOT_TIP] [{label}] ({tname}): {tip}", flush=True)

            modals = res.get("popped_modals") or res.get("modal_dialogs") or []
            if isinstance(modals, (list, tuple)):
                for m_item in modals:
                    if isinstance(m_item, dict):
                        m_title = str(m_item.get("title") or "Notice").strip()
                        m_content = str(m_item.get("content") or m_item.get("errorCode") or "").strip()
                        m_str = f"{m_title}: {m_content}".strip(": ")
                    else:
                        m_str = str(m_item or "").strip()
                    if m_str:
                        print(f"[BOT_MODAL] [{label}] ({tname}): {m_str}", flush=True)

            send_errs = res.get("send_errors") or res.get("errors") or []
            if isinstance(send_errs, (list, tuple)):
                for s_err in send_errs:
                    es = str(s_err or "").strip()
                    if es:
                        print(f"[BOT_ERR] [{label}] ({tname}): {es}", flush=True)

            if not res.get("ok"):
                err_txt = str(res.get("error") or res.get("reason") or "unknown error")
                print(f"[BOT_ERR] [{label}] ({tname}): {err_txt}", flush=True)
                logger.warning("  %s [%s] %s failed: %s", stage_tag, label, tname, err_txt)
            elif tname == "rf_hq_under_attack" and res.get("alerts"):
                logger.warning("  %s [%s] ALERT: %s", stage_tag, label, "; ".join(res["alerts"]))

            # Inter-task pacing delay inside the stage to prevent unthrottled bursts
            if t_pos < len(scheduled_tasks) - 1 and inter_task_delay > 0:
                time.sleep(inter_task_delay)

        # Stage 1 Emergency Preemption check immediately after Stage 1 completes
        if stage_id == 1:
            emergency_state = _evaluate_stage1_emergency(stage_task_results, snap, sm_cfg, shared_ctx=shared_ctx)
            if emergency_state["preempt_lower_stages"]:
                logger.warning(
                    "%s [%s] EMERGENCY PREEMPTION ACTIVE: %s -> Preempting Stages 2..5 until safety is confirmed!",
                    stage_tag,
                    label,
                    emergency_state["reason"],
                )
                print(
                    f"{stage_tag} [{label}] !!! EMERGENCY PREEMPTION: {emergency_state['reason']} (preempting Stages 2-5)",
                    flush=True,
                )

        exit_guard = _evaluate_stage_exit_guard(
            stage_def=stage_def,
            client_key=client_key,
            ba=ba,
            cd=cd,
            pid=pid,
            stage_task_results=stage_task_results,
            sm_cfg=sm_cfg,
            stage_state=stage_state,
            emergency_state=emergency_state,
            dry_run=dry_run,
            now_ts=time.time(),
        )

        # Compute inter-stage pacing delay before advancing to next stage
        stage_pacing = float(stage_def.get("pacing_delay_sec", inter_stage_delay))
        applied_pacing = 0.0
        if s_idx < total_stages - 1 and not emergency_state.get("preempt_lower_stages") and stage_pacing > 0:
            applied_pacing = stage_pacing

        stage_duration_ms = int((time.time() - stage_start_ts) * 1000)
        logger.info(
            "%s [%s] <<< EXIT Stage %d/%d: %s (status=%s, verified=%s, executed=%d, duration=%dms, cooldown=%ss, next_pacing=%ss)",
            stage_tag,
            label,
            stage_id,
            total_stages,
            stage_name,
            exit_guard["status"],
            exit_guard["verified"],
            exit_guard["executed_count"],
            stage_duration_ms,
            exit_guard["cooldown_lock_sec"],
            applied_pacing,
        )
        print(
            f"{stage_tag} [{label}] <<< EXIT {stage_name}: {exit_guard['status']} "
            f"(verified={exit_guard['verified']}, tasks={exit_guard['executed_count']}, cooldown={exit_guard['cooldown_lock_sec']}s)",
            flush=True,
        )

        stage_reports.append(
            {
                "stage_id": stage_id,
                "tag": stage_tag,
                "key": stage_def["key"],
                "name": stage_name,
                "status": exit_guard["status"],
                "preempted": False,
                "verified": exit_guard["verified"],
                "entry_guard": entry_guard,
                "exit_guard": exit_guard,
                "tasks_executed": list(stage_task_results.keys()),
                "task_results": stage_task_results,
                "duration_ms": stage_duration_ms,
                "pacing_delay_sec": applied_pacing,
            }
        )

        if applied_pacing > 0:
            time.sleep(applied_pacing)

    _save_stage_state(stage_state)
    completed_stages = [s["stage_id"] for s in stage_reports if s["status"].startswith("completed")]
    preempted_stages = [s["stage_id"] for s in stage_reports if s.get("preempted")]

    return {
        "label": label,
        "pid": pid,
        "role": role,
        "snapshot": snap,
        "ok": True,
        "state_machine": {
            "architecture": "5_stage_sequential_state_machine",
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "preempted_stages": preempted_stages,
            "emergency_state": emergency_state,
            "final_state": "PREEMPTED_EMERGENCY" if emergency_state.get("preempt_lower_stages") else "CYCLE_COMPLETE",
        },
        "stages": stage_reports,
        "tasks": task_results,
    }


def run_cycle(
    target: str = "all",
    task_filter: list[str] | None = None,
    dry_run: bool = False,
    auto_launch: bool | None = None,
    logger: logging.Logger | None = None,
    ignore_cooldowns: bool = False,
) -> dict[str, Any]:
    logger = logger or _configure_logging()
    cd = _load_module("client_discovery", TOOLS_DIR / "client discovery.py")
    ba = _load_module("bot_actions", TOOLS_DIR / "bot actions.py")
    cfg_root = load_config()
    stage_state = _load_stage_state()

    should_launch = bool(cfg_root.get("auto_launch_stopped_clients", False)) if auto_launch is None else auto_launch
    discovered_clients, running = _ensure_targets_running(cd, cfg_root, target, should_launch, logger)

    selected = [p for p in running if _matches_target(p, target)]
    selected.sort(key=lambda p: (0 if str(p.get("role") or "").lower() == "main" else 1, int(p.get("pid") or 0)))

    snapshots: list[dict[str, Any]] = []
    client_snaps: dict[int, dict[str, Any]] = {}
    for proc in selected:
        pid = int(proc["pid"])
        snap = _wait_client_ready(cd, ba, pid, logger=logger)
        snap["label"] = proc.get("label") or proc.get("unity_profile") or f"PID:{pid}"
        snap["role"] = proc.get("role") or "farm"
        snap["pid"] = pid
        client_snaps[pid] = snap
        if snap.get("ok"):
            snapshots.append(snap)

    protected_uids = _update_protected_uids(cfg_root, discovered_clients, snapshots)
    shared_ctx: dict[str, Any] = {
        "protected_uids": protected_uids,
        "claimed_gather_points": [],
        "reinforced_targets": [],
        "task_filter": list(task_filter) if task_filter else [],
        "force_mining": bool(task_filter and "mining_event" in task_filter),
    }

    cycle_started = datetime.now(timezone.utc).isoformat()
    client_reports: list[dict[str, Any]] = []
    inter_delay = float(cfg_root.get("inter_client_delay_seconds", 0.5))

    for idx, proc in enumerate(selected):
        pid = int(proc["pid"])
        label = str(proc.get("label") or proc.get("unity_profile") or f"PID:{pid}")
        role = str(proc.get("role") or "farm")
        ccfg = resolve_client_config(cfg_root, label, role)
        snap = client_snaps.get(pid, {})

        if not task_filter and not ccfg.get("enabled", True):
            logger.info("Skipping %s (PID %d): disabled in config", label, pid)
            continue
        if not snap.get("ok"):
            err = snap.get("error", "unresponsive")
            logger.warning("Skipping %s (PID %d): snapshot failed (%s)", label, pid, err)
            client_reports.append({"label": label, "pid": pid, "role": role, "ok": False, "error": err, "stages": [], "tasks": {}})
            continue

        logger.info(
            "Running 5-Stage Sequential State Machine on %s (PID %d, %s #%s, HQ%s, stam=%s, freeSquads=%s, dry_run=%s)",
            label,
            pid,
            snap.get("name", "?"),
            snap.get("serverId", "?"),
            snap.get("hqLv", "?"),
            snap.get("stamina", "?"),
            snap.get("freeFormations", "?"),
            dry_run,
        )

        c_report = run_client_stage_machine(
            cd=cd,
            ba=ba,
            pid=pid,
            label=label,
            role=role,
            snap=snap,
            ccfg=ccfg,
            cfg_root=cfg_root,
            shared_ctx=shared_ctx,
            stage_state=stage_state,
            task_filter=task_filter,
            dry_run=dry_run,
            logger=logger,
            ignore_cooldowns=ignore_cooldowns,
        )
        client_reports.append(c_report)

        if idx < len(selected) - 1 and inter_delay > 0:
            time.sleep(inter_delay)

    summary = {
        "ok": True,
        "scheduler_architecture": "5_stage_sequential_state_machine",
        "stages_defined": [
            {"stage_id": s["stage_id"], "tag": s["tag"], "key": s["key"], "name": s["name"], "tasks": list(s["tasks"])}
            for s in STAGE_DEFINITIONS
        ],
        "started_at": cycle_started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "target": target,
        "discovered_count": len(discovered_clients),
        "running_count": len(running),
        "processed_count": len(client_reports),
        "protected_uids": protected_uids,
        "clients": client_reports,
        "daemon_running": is_daemon_running(),
    }
    _write_status(summary)
    return summary


def _write_status(payload: dict[str, Any]) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    status_key = os.path.normcase(os.path.abspath(str(STATUS_PATH)))
    tmp_path = STATUS_PATH.parent / f"bot status.{os.getpid()}.{threading.get_ident()}.{time.time_ns()}.tmp"
    try:
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        for attempt in range(5):
            try:
                os.replace(tmp_path, STATUS_PATH)
                break
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05)
    finally:
        with _LAST_STATUS_LOCK:
            _LAST_STATUS_CACHE.pop(status_key, None)
        try:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def is_daemon_running() -> bool:
    if not PID_FILE_PATH.exists():
        return False
    try:
        pid = int(PID_FILE_PATH.read_text(encoding="utf-8").strip())
    except Exception:
        return False
    if pid <= 0:
        return False
    if psutil is not None:
        try:
            if psutil.pid_exists(pid):
                pname = psutil.Process(pid).name().lower()
                return ("python" in pname) or ("heinz" in pname)
            return False
        except Exception:
            pass
    try:
        res = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
            stdin=subprocess.DEVNULL,
            **_hidden_subproc_kwargs(),
        )
        out_low = res.stdout.lower()
        return str(pid) in res.stdout and ("python" in out_low or "heinz" in out_low)
    except Exception:
        return False


def compute_next_wake_seconds(
    cfg_root: dict[str, Any],
    last_cycle_result: dict[str, Any] | None = None,
    interval_override: int | None = None,
    now_dt: datetime | None = None,
) -> int:
    """Compute exact daemon wakeup sleep duration honoring fast_repeat events and 03:00 Furylord window."""
    base_sleep = max(10, int(interval_override or cfg_root.get("cycle_interval_seconds", 180)))
    sleep_sec = base_sleep

    # 1. Fast repeat when Tyrant battle or Furylord window requests immediate re-check on troop return
    if isinstance(last_cycle_result, dict):
        clients = last_cycle_result.get("clients")
        client_iter = clients.values() if isinstance(clients, dict) else (clients if isinstance(clients, list) else [])
        for c_res in client_iter:
            if not isinstance(c_res, dict):
                continue
            tasks = c_res.get("tasks") or {}
            if isinstance(tasks, dict):
                for t_res in tasks.values():
                    if isinstance(t_res, dict) and t_res.get("fast_repeat"):
                        f_sec = max(5, int(t_res.get("fast_repeat_sec") or 10))
                        sleep_sec = min(sleep_sec, f_sec)

    # 2. Exact Furylord wakeup (default 03:00) so the daemon never oversleeps past target timestamp
    global_enabled = cfg_root.get("enabled_tasks")
    if isinstance(global_enabled, dict) and global_enabled.get("furylord") is False:
        return max(1, int(sleep_sec))

    cur_dt = now_dt or datetime.now()
    defaults = cfg_root.get("client_defaults") or {}
    for role_cfg in defaults.values():
        if not isinstance(role_cfg, dict):
            continue
        if not (role_cfg.get("tasks") or {}).get("furylord", True):
            continue
        fl = role_cfg.get("furylord") or {}
        eh = int(fl.get("exact_hour", 3))
        em = int(fl.get("exact_minute", 0))
        target = cur_dt.replace(hour=eh, minute=em, second=0, microsecond=0)
        if target <= cur_dt:
            target = target + timedelta(days=1)
        secs_until = math.ceil((target - cur_dt).total_seconds())
        if 1 <= secs_until < sleep_sec:
            sleep_sec = int(secs_until)

    return max(1, int(sleep_sec))


def run_daemon(
    target: str = "all",
    task_filter: list[str] | None = None,
    dry_run: bool = False,
    auto_launch: bool | None = None,
    interval_override: int | None = None,
) -> int:
    logger = _configure_logging()
    if STOP_FLAG_PATH.exists():
        STOP_FLAG_PATH.unlink(missing_ok=True)
    PID_FILE_PATH.write_text(str(os.getpid()), encoding="utf-8")
    logger.info("Multi-client bot daemon started (PID %d, target=%s, dry_run=%s)", os.getpid(), target, dry_run)

    try:
        while not STOP_FLAG_PATH.exists():
            cfg_root = load_config()
            last_res: dict[str, Any] | None = None
            try:
                last_res = run_cycle(target=target, task_filter=task_filter, dry_run=dry_run, auto_launch=auto_launch, logger=logger)
            except Exception as exc:
                logger.exception("Unhandled error in daemon cycle: %s", exc)
            sleep_left = compute_next_wake_seconds(cfg_root, last_cycle_result=last_res, interval_override=interval_override)
            while sleep_left > 0 and not STOP_FLAG_PATH.exists():
                step = min(2, sleep_left)
                time.sleep(step)
                sleep_left -= step
    finally:
        if STOP_FLAG_PATH.exists():
            STOP_FLAG_PATH.unlink(missing_ok=True)
        if PID_FILE_PATH.exists():
            PID_FILE_PATH.unlink(missing_ok=True)
        logger.info("Multi-client bot daemon stopped cleanly.")
    return 0


def stop_daemon() -> bool:
    STOP_FLAG_PATH.write_text("stop", encoding="utf-8")
    deadline = time.time() + 10.0
    while time.time() < deadline:
        if not is_daemon_running():
            STOP_FLAG_PATH.unlink(missing_ok=True)
            return True
        time.sleep(0.5)
    return not is_daemon_running()


_TASK_STATUS_CACHE: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}
_TASK_STATUS_LOCK = threading.Lock()
_TASK_STATUS_TTL_SEC = 60.0
_LAST_STATUS_CACHE: dict[str, tuple[tuple[int, int, int, int], dict[str, Any]]] = {}
_LAST_STATUS_LOCK = threading.Lock()


def _extract_schedule_key(cfg_root: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    sched = cfg_root.get("schedule") or {}
    if not isinstance(sched, dict):
        sched = {}
    task_name = str(sched.get("task_name") or "LastZ_MultiClient_Bot")
    raw_legacy = sched.get("legacy_task_names") or []
    if isinstance(raw_legacy, str):
        raw_legacy = [raw_legacy] if raw_legacy.strip() else []
    elif not isinstance(raw_legacy, (list, tuple)):
        raw_legacy = []
    legacy_names = tuple(str(n) for n in raw_legacy if n)
    return task_name, legacy_names


def _query_task(task_name: str) -> dict[str, Any]:
    res = subprocess.run(
        ["schtasks", "/query", "/tn", task_name, "/v", "/fo", "list"],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        **_hidden_subproc_kwargs(),
    )
    raw_out = (res.stdout or res.stderr).strip()
    state_val = "Unknown" if res.returncode == 0 else "Not Found"
    for line in raw_out.splitlines():
        if line.lower().startswith("status:"):
            state_val = line.split(":", 1)[1].strip() or state_val
            break
    return {
        "exists": res.returncode == 0,
        "task_name": task_name,
        "state": state_val,
        "raw": raw_out,
    }


def _invalidate_task_status_cache() -> None:
    with _TASK_STATUS_LOCK:
        _TASK_STATUS_CACHE.clear()


def install_scheduled_task(keep_legacy: bool = False) -> dict[str, Any]:
    cfg_root = load_config()
    sched = cfg_root.get("schedule") or {}
    if not isinstance(sched, dict):
        sched = {}
    task_name, legacy_names = _extract_schedule_key(cfg_root)
    interval = max(1, min(1439, int(sched.get("interval_minutes") or 15)))
    auto_launch = bool(sched.get("auto_launch_in_task", True))
    script_path = str(TOOLS_DIR / "multi client bot.py")
    py_exe = sys.executable

    args = f'--cycle{" --auto-launch" if auto_launch else ""}'
    if getattr(sys, "frozen", False):
        tr_cmd = f'"{py_exe}" --run-script "{script_path}" {args}'
    else:
        tr_cmd = f'"{py_exe}" "{script_path}" {args}'

    cmd = [
        "schtasks",
        "/create",
        "/tn",
        task_name,
        "/sc",
        "MINUTE",
        "/mo",
        str(interval),
        "/tr",
        tr_cmd,
        "/f",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, **_hidden_subproc_kwargs())
    removed_legacy: list[str] = []
    if res.returncode == 0 and not keep_legacy:
        for legacy_name in legacy_names:
            q = _query_task(str(legacy_name))
            if q["exists"]:
                dres = subprocess.run(["schtasks", "/delete", "/tn", str(legacy_name), "/f"], capture_output=True, text=True, stdin=subprocess.DEVNULL, **_hidden_subproc_kwargs())
                if dres.returncode == 0:
                    removed_legacy.append(str(legacy_name))
    _invalidate_task_status_cache()
    return {
        "ok": res.returncode == 0,
        "task_name": task_name,
        "interval_minutes": interval,
        "command": tr_cmd,
        "removed_legacy": removed_legacy,
        "output": (res.stdout + "\n" + res.stderr).strip(),
    }


def uninstall_scheduled_task() -> dict[str, Any]:
    cfg_root = load_config()
    task_name, _ = _extract_schedule_key(cfg_root)
    res = subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True, text=True, stdin=subprocess.DEVNULL, **_hidden_subproc_kwargs())
    _invalidate_task_status_cache()
    return {"ok": res.returncode == 0, "task_name": task_name, "output": (res.stdout + "\n" + res.stderr).strip()}


def get_task_status(force_refresh: bool = False) -> dict[str, Any]:
    cfg_root = load_config()
    task_name, legacy_names = _extract_schedule_key(cfg_root)
    cache_key = (task_name, legacy_names)
    now_mono = time.monotonic()
    if not force_refresh:
        with _TASK_STATUS_LOCK:
            cached = _TASK_STATUS_CACHE.get(cache_key)
            if cached is not None and (now_mono - cached[0]) < _TASK_STATUS_TTL_SEC:
                return deepcopy(cached[1])
    legacy = [_query_task(n) for n in legacy_names]
    result = {"primary": _query_task(task_name), "legacy": legacy}
    with _TASK_STATUS_LOCK:
        if len(_TASK_STATUS_CACHE) > 8:
            _TASK_STATUS_CACHE.clear()
        _TASK_STATUS_CACHE[cache_key] = (time.monotonic(), deepcopy(result))
    return result


def _read_last_status_cached() -> dict[str, Any]:
    status_path = STATUS_PATH
    cache_key = os.path.normcase(os.path.abspath(str(status_path)))
    try:
        st = status_path.stat()
    except OSError:
        return {}
    sig = _stat_sig(st)
    with _LAST_STATUS_LOCK:
        cached = _LAST_STATUS_CACHE.get(cache_key)
        if cached is not None and cached[0] == sig:
            return deepcopy(cached[1])
    try:
        with status_path.open("r", encoding="utf-8") as fh:
            sig_open = _stat_sig(os.fstat(fh.fileno()))
            data = json.load(fh)
        if isinstance(data, dict):
            with _LAST_STATUS_LOCK:
                if len(_LAST_STATUS_CACHE) > 8:
                    _LAST_STATUS_CACHE.clear()
                _LAST_STATUS_CACHE[cache_key] = (sig_open, deepcopy(data))
            return deepcopy(data)
    except Exception:
        pass
    return {}


def get_status(
    skip_discovery: bool = False,
    skip_running: bool = False,
    include_schedule: bool = True,
    force_schedule_refresh: bool = False,
) -> dict[str, Any]:
    cd = _load_module("client_discovery", TOOLS_DIR / "client discovery.py")
    discovery = cd.load_saved_profiles() if skip_discovery else cd.discover_clients(save_cache=False)
    running = [] if skip_running else cd.find_running_processes()
    last_status = _read_last_status_cached()
    if include_schedule:
        schedule_info = get_task_status(force_refresh=force_schedule_refresh)
    else:
        cache_key = _extract_schedule_key(load_config())
        now_mono = time.monotonic()
        with _TASK_STATUS_LOCK:
            cached = _TASK_STATUS_CACHE.get(cache_key)
            if cached is not None and (now_mono - cached[0]) < _TASK_STATUS_TTL_SEC:
                schedule_info = deepcopy(cached[1])
            else:
                schedule_info = {"primary": {"exists": False, "state": "Skipped", "skipped": True}, "legacy": []}
    return {
        "daemon_running": is_daemon_running(),
        "discovered_clients": discovery.get("clients", []) if isinstance(discovery, dict) else discovery,
        "running_processes": running,
        "last_cycle": last_status,
        "schedule": schedule_info,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-client Last Z automation orchestrator")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cycle", action="store_true", help="Run one automation cycle across selected clients")
    mode.add_argument("--daemon", action="store_true", help="Run continuously on configured cycle interval")
    mode.add_argument("--stop-daemon", action="store_true", help="Signal a running bot daemon to stop")
    mode.add_argument("--status", action="store_true", help="Print discovered clients, daemon, and schedule state")
    mode.add_argument("--install-task", action="store_true", help="Register Windows Task Scheduler recurring job")
    mode.add_argument("--uninstall-task", action="store_true", help="Remove Windows Task Scheduler job")
    mode.add_argument("--task-status", action="store_true", help="Show Windows Task Scheduler status")

    parser.add_argument("--target", default="all", help="Client label, unity profile, role, PID, or 'all'")
    parser.add_argument("--tasks", default="", help="Comma-separated list of tasks to execute")
    parser.add_argument("--dry-run", action="store_true", help="Inspect actions without sending state changes")
    parser.add_argument("--ignore-cooldowns", action="store_true", help="Bypass per-stage cooldown locks (for manual full cycles)")
    parser.add_argument("--auto-launch", action="store_true", help="Launch stopped enabled clients before cycling")
    parser.add_argument("--interval", type=int, default=None, help="Override daemon sleep interval in seconds")
    parser.add_argument("--keep-legacy", action="store_true", help="Do not delete legacy scheduled task during install")

    args = parser.parse_args()
    task_list = [t.strip() for t in args.tasks.split(",") if t.strip()] if args.tasks else None
    auto_launch = True if args.auto_launch else None

    if args.cycle:
        res = run_cycle(target=args.target, task_filter=task_list, dry_run=args.dry_run, auto_launch=auto_launch, ignore_cooldowns=bool(args.ignore_cooldowns))
        print(json.dumps(res, ensure_ascii=False), flush=True)
        total_tasks = sum(len((c.get("tasks") or {})) for c in (res.get("clients") or []) if isinstance(c, dict))
        print(
            f"[CYCLE_SUMMARY] 5-Stage Sequential State Machine complete: processed {res.get('processed_count', 0)}/{res.get('running_count', 0)} running client(s), {total_tasks} task(s) executed (dry_run={args.dry_run})",
            flush=True,
        )
        return 0 if res.get("ok") else 1
    if args.daemon:
        return run_daemon(
            target=args.target,
            task_filter=task_list,
            dry_run=args.dry_run,
            auto_launch=auto_launch,
            interval_override=args.interval,
        )
    if args.stop_daemon:
        stopped = stop_daemon()
        print(json.dumps({"ok": stopped, "daemon_running": is_daemon_running()}, indent=2))
        return 0 if stopped else 1
    if args.status:
        print(json.dumps(get_status(), indent=2, ensure_ascii=False))
        return 0
    if args.install_task:
        res = install_scheduled_task(keep_legacy=args.keep_legacy)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("ok") else 1
    if args.uninstall_task:
        res = uninstall_scheduled_task()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("ok") else 1
    if args.task_status:
        print(json.dumps(get_task_status(), indent=2, ensure_ascii=False))
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
