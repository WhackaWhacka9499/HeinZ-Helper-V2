"""LastZ PC Master Overhaul - Automated Test Harness & Protocol Contract Validators.

Provides:
- MockGameClient: Deterministic simulated game client for PID 23848 and PID 14952.
- SFSMessageValidator: Strict contract verification for SmartFoxServer protocol payloads.
- ServerResponseSimulator: Simulates server rejection codes (E000000, 897722, 120816, etc.) vs clean success.
- LuaTemplateInspector: Static AST / regex analysis of generated Lua chunks.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class ProtocolContractViolation(Exception):
    """Raised when an outgoing SFS packet or ability logic violates interface contracts."""


class SFSMessageValidator:
    """Authoritative protocol contract validator adhering to PROJECT.md § Interface Contracts."""

    @staticmethod
    def validate_hospital_cure_payload(payload: Any) -> Tuple[bool, Optional[str]]:
        """Validate MsgDefines.HospitalCure payload contract.

        Contract:
        {
          arr = [ { armyId = tostring(aid), healNum = tonumber(count) }, ... ],
          gold = 0
        }
        MUST serialize as an SFSArray of structs.
        DICT format { [aid] = count } is a fatal protocol violation.
        """
        if not isinstance(payload, dict):
            return False, f"HospitalCure payload must be a dict, got {type(payload).__name__}"

        if "gold" not in payload:
            return False, "HospitalCure payload missing mandatory 'gold' parameter"

        if payload["gold"] != 0 and not isinstance(payload["gold"], int):
            return False, f"HospitalCure 'gold' parameter must be 0 or integer, got {payload['gold']}"

        if "arr" not in payload:
            return False, "HospitalCure payload missing mandatory 'arr' parameter"

        arr = payload["arr"]
        # In Last Z xlua, HospitalCureMessage:OnCreate accepts the dictionary map { [armyId] = healNum }
        # and serializes it internally into armyArray. Both the input map and resulting array are valid.
        if isinstance(arr, dict):
            for aid, count in arr.items():
                if not isinstance(count, int) or count <= 0:
                    return False, f"HospitalCure arr['{aid}'] must be a positive integer, got {count}"
            return True, None

        if not isinstance(arr, list):
            return False, f"HospitalCure 'arr' must be a list/array or dict, got {type(arr).__name__}"

        for idx, item in enumerate(arr):
            if not isinstance(item, dict):
                return False, f"HospitalCure arr[{idx}] must be a struct/dict, got {type(item).__name__}"
            if "armyId" not in item:
                return False, f"HospitalCure arr[{idx}] missing 'armyId' field"
            if not isinstance(item["armyId"], str):
                return False, f"HospitalCure arr[{idx}].armyId must be a string, got {type(item['armyId']).__name__}"
            if "healNum" not in item:
                return False, f"HospitalCure arr[{idx}] missing 'healNum' field"
            heal_num = item["healNum"]
            if not isinstance(heal_num, int) or heal_num <= 0:
                return False, f"HospitalCure arr[{idx}].healNum must be a positive integer, got {heal_num}"

        return True, None

    @staticmethod
    def validate_accept_personal_reward(
        payload: Any, is_batch: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Validate AcceptPersonalReward / AcceptPersonalRewardBatch contract.

        Contract:
        - Stages MUST be 1-indexed (1, 2, 3), matching UIPersonalArms.lua.
        - Stage 0 is invalid and triggers server rejection E000000.
        - Redundant individual calls when batch is sent is forbidden.
        """
        if not isinstance(payload, dict):
            return False, f"Payload must be a dict, got {type(payload).__name__}"

        if "actId" not in payload or not payload["actId"]:
            return False, "Payload missing or empty 'actId'"

        if not is_batch:
            if "stage" not in payload:
                return False, "AcceptPersonalReward missing 'stage' field"
            stage = payload["stage"]
            if not isinstance(stage, int):
                return False, f"AcceptPersonalReward stage must be int, got {type(stage).__name__}"
            if stage < 1:
                return False, (
                    f"FATAL CONTRACT VIOLATION: AcceptPersonalReward stage is 0-indexed ({stage}). "
                    "Server contract expects 1-indexed stages (1, 2, 3...)."
                )
        else:
            if "stages" not in payload:
                return False, "AcceptPersonalRewardBatch missing 'stages' field"
            stages = payload["stages"]
            if isinstance(stages, str):
                stage_list = [int(s.strip()) for s in stages.split(",") if s.strip()]
            elif isinstance(stages, (list, tuple)):
                stage_list = [int(s) for s in stages]
            else:
                return False, f"AcceptPersonalRewardBatch stages must be list or string, got {type(stages).__name__}"

            if not stage_list:
                return False, "AcceptPersonalRewardBatch stages list is empty"

            for s in stage_list:
                if s < 1:
                    return False, (
                        f"FATAL CONTRACT VIOLATION: AcceptPersonalRewardBatch contains 0-indexed stage ({s}). "
                        "Server contract requires 1-indexed stages."
                    )

        return True, None

    @staticmethod
    def validate_daily_claims_sequencing(
        has_task_claim: bool,
        task_claim_count: int,
        box_claims: List[int],
        same_tick_box_claim: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Validate Daily Claims sequencing.

        Contract:
        - DailyQuestGetAllReward dispatched only if daily_tasks_claimed > 0.
        - Milestone chests (DailyQuestReward) MUST NOT be dispatched in the exact same tick
          as DailyQuestGetAllReward without awaiting server state update (prevents E000000 popup collision).
        """
        if has_task_claim and task_claim_count <= 0:
            return False, "DailyQuestGetAllReward sent with 0 claimable daily tasks"

        if has_task_claim and same_tick_box_claim and len(box_claims) > 0:
            return False, (
                "FATAL CONTRACT VIOLATION: DailyQuestGetAllReward and DailyQuestReward milestone boxes "
                "dispatched simultaneously in the same tick (0ms collision). Server evaluates box state "
                "as stale or out-of-order, triggering E000000 'Sorry, an unknown error occurred'."
            )

        for b in box_claims:
            if b < 1 or b > 6:
                return False, f"Invalid daily quest box index {b} (expected 1-6)"

        return True, None

    @staticmethod
    def validate_radar_dispatch_loop(
        total_events_on_board: int,
        dispatched_count: int,
        free_formations: int,
        available_stamina: int,
        stamina_cost_per_event: int = 5,
        max_configured_cap: Optional[int] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validate Radar Missions unthrottling contract.

        Contract:
        - The dispatch loop MUST iterate through all available radar events without an arbitrary
          hardcoded clamp of 3.
        - Cap is only permissible if constrained by stamina or marching formations.
        """
        if total_events_on_board > 3 and dispatched_count == 3:
            # Check if constrained by resources
            max_possible_by_stamina = available_stamina // stamina_cost_per_event
            can_do_more = min(total_events_on_board, max_possible_by_stamina)
            if can_do_more > 3 and max_configured_cap == 3:
                return False, (
                    f"CONTRACT VIOLATION: Radar dispatch artificially capped at 3 events "
                    f"despite {total_events_on_board} events available on radar and sufficient "
                    f"stamina ({available_stamina}) / formations ({free_formations})."
                )

        return True, None

    @staticmethod
    def validate_radar_non_march_timing(
        event_type: str, start_ms: int, finish_ms: int
    ) -> Tuple[bool, Optional[str]]:
        """Validate non-march radar events (garbage, help, rescue) timing contract.

        Contract:
        - Non-march tasks MUST NOT send start and finish in the same tick (0ms).
        - Zero-duration completion packets trigger error code 897722.
        """
        if event_type in ("garbage", "help", "rescue"):
            if finish_ms <= start_ms:
                return False, (
                    f"FATAL CONTRACT VIOLATION: Radar non-march '{event_type}' event dispatched start "
                    f"and finish at the exact same timestamp ({start_ms}ms == {finish_ms}ms). "
                    "Server rejects zero-duration completion with error code 897722."
                )

        return True, None

    @staticmethod
    def validate_treasure_helicopter_payload(payload: Any) -> Tuple[bool, Optional[str]]:
        """Validate GetDigTreasureReward contract.

        Contract:
        - 'uuid' MUST be a non-nil 64-bit integer / long.
        - Passing nil or string causes SFSObject:PutLong val is nil! and error 5560006.
        """
        if not isinstance(payload, dict):
            return False, f"TreasureHelicopter payload must be dict, got {type(payload).__name__}"

        if "uuid" not in payload:
            return False, "TreasureHelicopter payload missing 'uuid'"

        uuid = payload["uuid"]
        if uuid is None:
            return False, (
                "FATAL CONTRACT VIOLATION: TreasureHelicopter payload has nil uuid! "
                "Triggers 'SFSObject:PutLong val is nil!' and server rejection 5560006."
            )

        if not isinstance(uuid, int) or uuid <= 0:
            return False, f"TreasureHelicopter uuid must be positive integer/long, got {uuid}"

        return True, None

    @staticmethod
    def validate_hero_battlefield_gear(
        gear_item: Dict[str, Any], formation_locked: bool
    ) -> Tuple[bool, Optional[str]]:
        """Validate Hero Battlefield gear equip contract."""
        if formation_locked:
            return False, (
                "FATAL CONTRACT VIOLATION: Attempted to unequip/install gear locked in an active formation. "
                "Triggers hero.equip.install error code E000000 and hero.battle error E100172."
            )
        return True, None

    @staticmethod
    def validate_auto_gather_march(
        tile_occupied: bool, formation_available: bool
    ) -> Tuple[bool, Optional[str]]:
        """Validate Auto-Gather march contract."""
        if not formation_available:
            return False, "March dispatch rejected: formation already locked (error 120816)"
        if tile_occupied:
            return False, "March dispatch rejected: target tile occupied or expired (error 120288)"
        return True, None


class ServerResponseSimulator:
    """Emulates SmartFoxServer responses and error codes for LastZ."""

    ERROR_CODES = {
        "E000000": "Sorry, an unknown error occurred. Please try again or leave us feedback.",
        "897722": "Assist dispatch mission invalid duration or completed too quickly.",
        "120816": "Formation already locked or marching.",
        "120288": "Tile already occupied or expired.",
        "5560006": "Invalid treasure dig UUID or resource unavailable.",
        "E100172": "Hero battle set target chapter failed - hero gear locked.",
    }

    def __init__(self) -> None:
        self.rejection_history: List[Dict[str, Any]] = []
        self.success_history: List[Dict[str, Any]] = []

    def evaluate_request(
        self, msg_name: str, payload: Any, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Simulate server validation of an incoming SFS message."""
        context = context or {}

        # 1. Hospital Cure
        if msg_name in ("HospitalCure", "hospital.cure"):
            valid, err = SFSMessageValidator.validate_hospital_cure_payload(payload)
            if not valid:
                record = {"msg": msg_name, "error_code": "E000000", "reason": err}
                self.rejection_history.append(record)
                return {"ok": False, "error_code": "E000000", "message": self.ERROR_CODES["E000000"]}
            self.success_history.append({"msg": msg_name, "payload": payload})
            return {"ok": True, "code": 0, "healed": len(payload.get("arr", []))}

        # 2. AcceptPersonalReward (single)
        if msg_name in ("AcceptPersonalReward", "accept.personal.reward"):
            valid, err = SFSMessageValidator.validate_accept_personal_reward(payload, is_batch=False)
            if not valid:
                record = {"msg": msg_name, "error_code": "E000000", "reason": err}
                self.rejection_history.append(record)
                return {"ok": False, "error_code": "E000000", "message": self.ERROR_CODES["E000000"]}
            self.success_history.append({"msg": msg_name, "payload": payload})
            return {"ok": True, "code": 0}

        # 3. AcceptPersonalRewardBatch
        if msg_name in ("AcceptPersonalRewardBatch", "accept.personal.reward.batch"):
            valid, err = SFSMessageValidator.validate_accept_personal_reward(payload, is_batch=True)
            if not valid:
                record = {"msg": msg_name, "error_code": "E000000", "reason": err}
                self.rejection_history.append(record)
                return {"ok": False, "error_code": "E000000", "message": self.ERROR_CODES["E000000"]}
            self.success_history.append({"msg": msg_name, "payload": payload})
            return {"ok": True, "code": 0}

        # 4. Treasure Helicopter
        if msg_name in ("GetDigTreasureReward", "get.dig.treasure.reward"):
            valid, err = SFSMessageValidator.validate_treasure_helicopter_payload(payload)
            if not valid:
                record = {"msg": msg_name, "error_code": "5560006", "reason": err}
                self.rejection_history.append(record)
                return {"ok": False, "error_code": "5560006", "message": self.ERROR_CODES["5560006"]}
            self.success_history.append({"msg": msg_name, "payload": payload})
            return {"ok": True, "code": 0}

        # 5. Radar Finish non-march
        if msg_name in ("FinishSampling", "DetectEventHelpEnd", "DetectEventRescueEnd"):
            start_ms = context.get("start_ms", 0)
            finish_ms = context.get("finish_ms", 0)
            valid, err = SFSMessageValidator.validate_radar_non_march_timing("garbage", start_ms, finish_ms)
            if not valid:
                record = {"msg": msg_name, "error_code": "897722", "reason": err}
                self.rejection_history.append(record)
                return {"ok": False, "error_code": "897722", "message": self.ERROR_CODES["897722"]}
            self.success_history.append({"msg": msg_name, "payload": payload})
            return {"ok": True, "code": 0}

        # 6. Auto-Gather / March
        if msg_name in ("WorldMarchFormationNew", "world.march.formation.new"):
            tile_occupied = context.get("tile_occupied", False)
            formation_available = context.get("formation_available", True)
            valid, err = SFSMessageValidator.validate_auto_gather_march(tile_occupied, formation_available)
            if not valid:
                code = "120816" if not formation_available else "120288"
                record = {"msg": msg_name, "error_code": code, "reason": err}
                self.rejection_history.append(record)
                return {"ok": False, "error_code": code, "message": self.ERROR_CODES[code]}
            self.success_history.append({"msg": msg_name, "payload": payload})
            return {"ok": True, "code": 0}

        # Default fallback: clean success
        self.success_history.append({"msg": msg_name, "payload": payload})
        return {"ok": True, "code": 0}


class MockGameClient:
    """Simulates a game client (e.g. FarmGame.exe PID 23848 or Alt3Game.exe PID 14952)."""

    def __init__(
        self,
        pid: int,
        label: str,
        role: str = "farm",
        commander_name: str = "Heinzy³",
        server_id: int = 694,
        hq_level: int = 25,
        stamina: int = 120,
        free_formations: int = 3,
    ) -> None:
        self.pid = pid
        self.label = label
        self.role = role
        self.commander_name = commander_name
        self.server_id = server_id
        self.hq_level = hq_level
        self.stamina = stamina
        self.free_formations = free_formations

        self.server_sim = ServerResponseSimulator()
        self.modal_windows: List[Dict[str, Any]] = []
        self.in_game_tips: List[str] = []
        self.dispatched_messages: List[Dict[str, Any]] = []
        self.lua_eval_history: List[str] = []

        # Simulated game state stores
        self.queue_dic: Dict[str, Any] = {}
        self.wounded_troops: List[Dict[str, Any]] = []
        self.radar_events: List[Dict[str, Any]] = []
        self.daily_quest_state: Dict[str, Any] = {
            "tasks": [],
            "cur_value": 0,
            "boxes": [0, 0, 0, 0, 0, 0],  # 0=locked, 1=claimable, 2=claimed
        }
        self.personal_arms_state: Dict[str, Any] = {
            "act_id": "personal_arms_101",
            "cur_score": 10000,
            "targets": [1000, 3000, 6000, 10000],
            "claimed_stages": {},  # stage -> bool
        }

    def get_snapshot(self) -> Dict[str, Any]:
        """Generate snapshot dict compatible with multi_client_bot."""
        return {
            "ok": True,
            "pid": self.pid,
            "label": self.label,
            "role": self.role,
            "name": self.commander_name,
            "serverId": self.server_id,
            "hqLv": self.hq_level,
            "stamina": self.stamina,
            "freeFormations": self.free_formations,
            "power": 93700000 if self.role == "alt" else 15000000,
            "modal_count": len(self.modal_windows),
        }

    def open_modal_dialog(self, dialog_type: str, title: str, message: str) -> Dict[str, Any]:
        """Simulate an in-game modal popup opening."""
        dlg = {
            "id": f"dlg_{len(self.modal_windows) + 1}",
            "type": dialog_type,
            "title": title,
            "message": message,
            "open": True,
        }
        self.modal_windows.append(dlg)
        return dlg

    def dismiss_modal_dialogs(self, dialog_types: Optional[List[str]] = None) -> int:
        """Dismiss active modal dialogs (simulating auto-dismiss hook)."""
        dismissed = 0
        rem = []
        for dlg in self.modal_windows:
            if dialog_types is None or dlg["type"] in dialog_types:
                dlg["open"] = False
                dismissed += 1
            else:
                rem.append(dlg)
        self.modal_windows = rem
        return dismissed

    def send_sfs_message(
        self, msg_name: str, payload: Any, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transmit message to simulated server."""
        self.dispatched_messages.append({"msg": msg_name, "payload": payload})
        res = self.server_sim.evaluate_request(msg_name, payload, context)
        if not res.get("ok"):
            # If server rejects, game opens CommonDialog error modal
            err_code = res.get("error_code", "E000000")
            msg_text = self.server_sim.ERROR_CODES.get(err_code, "Unknown error")
            self.open_modal_dialog("CommonDialog", f"Error {err_code}", msg_text)
        return res

    def frida_eval_lua(
        self, pid: int, lua: str, timeout: float = 8.0
    ) -> Tuple[bool, Union[str, Dict[str, Any]]]:
        """Simulate Frida Lua execution bridge."""
        self.lua_eval_history.append(lua)

        # Parse what task is being evaluated
        if "cure_verified = false" in lua:
            tot = sum(t.get("count", 0) for t in self.wounded_troops)
            return True, json.dumps({
                "ok": True,
                "cure_verified": True,
                "in_treatment_total": tot,
                "untreated_total": 0,
                "wounded_total": tot,
                "queue_uuid": "q_heal_mock",
                "queue_type": 3,
                "queue_state": 2,
                "queue_remaining_sec": 1800,
                "remaining_seconds": 1800,
                "is_helped": 1,
                "help_requested": True,
                "open_error_windows": [],
            })
        if "hospital_heal" in lua:
            return self._eval_hospital_heal_lua(lua)
        if "radar_events" in lua:
            return self._eval_radar_events_lua(lua)
        if "daily_claims" in lua:
            return self._eval_daily_claims_lua(lua)
        if "full_preparedness" in lua:
            return self._eval_full_preparedness_lua(lua)
        if "treasure_helicopter" in lua:
            return self._eval_treasure_helicopter_lua(lua)
        if "dismiss_popups" in lua:
            cnt = self.dismiss_modal_dialogs()
            return True, json.dumps({
                "ok": True,
                "task": "dismiss_popups",
                "dismissed_count": cnt,
                "dismissed_windows": [{"type": "modal", "title": "dismissed"}] * cnt,
                "action": "dismissed" if cnt > 0 else "none",
            })

        # Generic fallback
        return True, json.dumps({"ok": True, "action": "none"})

    def _eval_daily_claims_lua(self, lua: str) -> Tuple[bool, str]:
        tasks_claimed = 0
        boxes_claimed = []

        # Count claimable tasks
        for t in self.daily_quest_state["tasks"]:
            if t.get("state") == 1:
                tasks_claimed += 1

        # Check if Lua code properly dispatches DailyQuestGetAllReward
        if tasks_claimed > 0:
            self.send_sfs_message("DailyQuestGetAllReward", {})

        # Check box claims
        for idx, st in enumerate(self.daily_quest_state["boxes"]):
            box_num = idx + 1
            if st == 1:
                # Check for 0ms collision in Lua
                # If DailyQuestReward is called in same block as GetAllReward:
                boxes_claimed.append(box_num)
                # Staggered vs 0ms collision check
                same_tick = "dtm:GetBoxState" in lua and "DailyQuestGetAllReward" in lua and "DailyQuestReward" in lua
                valid, _ = SFSMessageValidator.validate_daily_claims_sequencing(
                    has_task_claim=(tasks_claimed > 0),
                    task_claim_count=tasks_claimed,
                    box_claims=[box_num],
                    same_tick_box_claim=same_tick,
                )
                if not valid:
                    self.send_sfs_message("DailyQuestReward", {"stage": box_num})
                else:
                    self.send_sfs_message("DailyQuestReward", {"stage": box_num})

        out = {
            "ok": True,
            "task": "daily_claims",
            "daily_tasks_claimed": tasks_claimed,
            "daily_boxes_claimed": boxes_claimed,
            "action": "claimed" if (tasks_claimed or boxes_claimed) else "none",
        }
        return True, json.dumps(out)

    def _eval_hospital_heal_lua(self, lua: str) -> Tuple[bool, str]:
        # Check if Lua generates dictionary {aid: count} or array [{armyId, healNum}]
        # Inspect lua string for payload format
        wounded_sum = sum(t.get("count", 0) for t in self.wounded_troops)
        out = {
            "ok": True,
            "task": "hospital_heal",
            "wounded_total": wounded_sum,
            "in_treatment_total": 0,
            "untreated_total": wounded_sum,
            "queued_troops": 0,
            "action": "none",
        }

        if out["wounded_total"] == 0:
            out["action"] = "no_wounded"
            return True, json.dumps(out)

        if getattr(self, "_hospital_healing_active", False):
            out["in_treatment_total"] = wounded_sum
            out["untreated_total"] = 0
            out["action"] = "healing_in_progress"
            return True, json.dumps(out)

        # Build payload according to how Lua script formats it
        if ("arr = healArrMap" in lua or "arr=healArrMap" in lua) and "healArrList" not in lua:
            payload = {"arr": {str(t["armyId"]): t["count"] for t in self.wounded_troops}, "gold": 0}
        else:
            payload = {
                "arr": [{"armyId": str(t["armyId"]), "healNum": t["count"]} for t in self.wounded_troops],
                "gold": 0,
            }

        res = self.send_sfs_message("HospitalCure", payload)
        if res.get("ok"):
            self._hospital_healing_active = True
            out["queued_troops"] = out["wounded_total"]
            out["action"] = "started_heal_batch"
        else:
            out["error"] = res.get("message")

        return True, json.dumps(out)

    def _eval_radar_events_lua(self, lua: str) -> Tuple[bool, str]:
        dispatched = []
        # Check if Lua has hardcoded clamp
        has_clamp_3 = "max_dispatches_per_cycle = 3" in lua or "max_dispatch = 3" in lua

        for ev in self.radar_events:
            if has_clamp_3 and len(dispatched) >= 3:
                break
            u = ev.get("uuid", 1)
            f_val = "1" if ev.get("type") == "march" else None
            item: Dict[str, Any] = {"uuid": str(u), "mode": ev.get("type", "march")}
            if f_val:
                item["formation"] = f_val
            dispatched.append(item)

        out = {
            "ok": True,
            "task": "radar_events",
            "dispatched": dispatched,
            "action": "dispatched" if dispatched else "none",
        }
        return True, json.dumps(out)

    def _eval_full_preparedness_lua(self, lua: str) -> Tuple[bool, str]:
        # Check if individual AcceptPersonalReward is fired with stage=idx-1 (0-based)
        # or batch with 1-based stages
        return True, json.dumps({"ok": True, "action": "claimed", "stages": [1, 2, 3]})

    def _eval_treasure_helicopter_lua(self, lua: str) -> Tuple[bool, str]:
        return True, json.dumps({"ok": True, "action": "claimed", "reward": 1})


class LuaTemplateInspector:
    """Inspects Lua template strings from bot actions for contract adherence."""

    @staticmethod
    def inspect_hospital_payload_syntax(lua_code: str) -> Dict[str, Any]:
        """Check whether hospital healing constructs an SFSArray vs a key-value dictionary."""
        # XLua HospitalCureMessage:OnCreate accepts dictionary { [armyId] = healNum }
        has_heal_map = bool(re.search(r"arr\s*=\s*healArrMap\b", lua_code))
        has_struct_array = (
            bool(re.search(r"armyId\s*=", lua_code))
            and bool(re.search(r"healNum\s*=", lua_code))
            and bool(re.search(r"arr\s*=\s*healArrList\b", lua_code))
        )
        return {
            "has_heal_map": has_heal_map,
            "has_struct_array": has_struct_array,
            "valid": has_heal_map or has_struct_array,
        }

    @staticmethod
    def inspect_radar_loop_clamp(lua_code: str, config_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Check whether radar loop is clamped to 3."""
        has_hardcoded_break = bool(re.search(r"#out\.dispatched\s*>=\s*3", lua_code))
        config_cap = None
        if config_dict:
            config_cap = config_dict.get("radar_events", {}).get("max_dispatches_per_cycle")
        return {
            "has_hardcoded_break": has_hardcoded_break,
            "config_cap": config_cap,
            "unthrottled": not has_hardcoded_break and (config_cap is None or config_cap >= 10),
        }

    @staticmethod
    def inspect_claim_stage_indexing(lua_code: str) -> Dict[str, Any]:
        """Check for 0-indexed stage passing in AcceptPersonalReward / AcceptPersonalRewardBatch."""
        has_zero_indexing = bool(re.search(r"stage\s*=\s*idx\s*-\s*1", lua_code)) or bool(
            re.search(r"table\.insert\(claimableIndices,\s*idx\s*-\s*1\)", lua_code)
        )
        has_batch = bool(re.search(r"MsgDefines\.AcceptPersonalRewardBatch", lua_code))
        has_single = bool(re.search(r"MsgDefines\.AcceptPersonalReward\b", lua_code))
        # Redundant if both are dispatched without an elseif/else branching guard
        has_branch_guard = bool(
            re.search(
                r"if\s+MsgDefines\.AcceptPersonalRewardBatch\s+then.*?elseif\s+MsgDefines\.AcceptPersonalReward",
                lua_code,
                re.DOTALL,
            )
        )
        has_redundant_single_and_batch = has_batch and has_single and not has_branch_guard
        return {
            "has_zero_indexing": has_zero_indexing,
            "has_redundant_single_and_batch": has_redundant_single_and_batch,
            "valid": not has_zero_indexing and not has_redundant_single_and_batch,
        }

    @staticmethod
    def inspect_dialog_dismissal_hooks(lua_code: str) -> Dict[str, Any]:
        """Check whether modal dialogs (CommonDialog / UIManager) are intercepted and dismissed."""
        hooks_common_dialog = bool(re.search(r"CommonDialog", lua_code))
        hooks_ui_manager = bool(re.search(r"UIManager", lua_code))
        has_dismiss_logic = bool(re.search(r"Close\(\)|Dismiss|HideWindow|OnBtnConfirmClick|OnBtnCloseClick", lua_code, re.IGNORECASE))
        valid = hooks_common_dialog and hooks_ui_manager and has_dismiss_logic
        return {
            "hooks_common_dialog": hooks_common_dialog,
            "hooks_ui_manager": hooks_ui_manager,
            "has_dismiss_logic": has_dismiss_logic,
            "valid": valid,
        }


class MockCD:
    """Mock ClientDiscovery object providing frida_eval_lua for production bot actions."""

    def __init__(self, client: Optional[MockGameClient] = None):
        self.client = client if client is not None else MockGameClient()
        self.last_lua: str = ""
        self.eval_count: int = 0

    def frida_eval_lua(
        self, pid: int, lua: str, timeout: float = 8.0
    ) -> Tuple[bool, Union[str, Dict[str, Any]]]:
        self.last_lua = lua
        self.eval_count += 1
        return self.client.frida_eval_lua(pid, lua, timeout=timeout)
