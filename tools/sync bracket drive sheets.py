"""Sync all 16 bracket state Native Google Spreadsheets (689-704) cleanly via gsheets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import openpyxl

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
DATA_DIR = Path(os.environ["HEINZ_DATA_DIR"]) if os.environ.get("HEINZ_DATA_DIR", "").strip() else (REPO_ROOT / "data")
JSON_CACHE_DIR = DATA_DIR / "json cache"
BRACKET_DATA_DIR = JSON_CACHE_DIR / "bracket data"
XLSX_DIR = DATA_DIR / "bracket states"
CACHE_PATH = JSON_CACHE_DIR / "all_players_profile_cache.json"
MANIFEST_PATH = DATA_DIR / "bracket sheets manifest.json"

LEGACY_SCRATCH = Path(
    r"data/cache"
)
LEGACY_BRACKET_DATA = LEGACY_SCRATCH / "bracket_data"
LEGACY_CACHE_PATH = LEGACY_SCRATCH / "lastz_data_master" / "all_players_profile_cache.json"

ALL_BRACKET_STATES = list(range(689, 705))


def _load_cd():
    path = TOOLS_DIR / "client discovery.py"
    spec = importlib.util.spec_from_file_location("client_discovery", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load client discovery module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gsheets_bin() -> str:
    resolved = shutil.which("gsheets")
    return resolved or "gsheets"


def _run_gsheets(args: list[str], timeout: int = 60, retries: int = 3) -> subprocess.CompletedProcess[str]:
    gsheets_exe = shutil.which("gsheets")
    if not gsheets_exe:
        raise RuntimeError(
            "Google Sheets sync requires the optional 'gsheets' CLI and your Google Drive sheet IDs configured in data/bracket sheets manifest.json."
        )
    cmd = [gsheets_exe, *args]
    last_err = ""
    for attempt in range(retries):
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            shell=True,
        )
        if proc.returncode == 0:
            return proc
        last_err = (proc.stderr or proc.stdout or "").strip()
        if any(tok in last_err.lower() for tok in ("429", "quota", "rate", "timeout", "503", "502")):
            time.sleep(2.0 * (attempt + 1))
            continue
        break
    raise RuntimeError(f"gsheets {' '.join(args[:3])} failed: {last_err}")


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Bracket sheets manifest not found: {MANIFEST_PATH}")
    with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_profile_cache() -> dict[str, dict[str, Any]]:
    src = CACHE_PATH if CACHE_PATH.exists() else LEGACY_CACHE_PATH
    if not src.exists():
        return {}
    with src.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def _atomic_write_json(target_path: Path, payload: Any, indent: int | None = None) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_name(f"{target_path.name}.{os.getpid()}.tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=indent)
    os.replace(tmp_path, target_path)


def save_profile_cache(cache: dict[str, dict[str, Any]]) -> None:
    _atomic_write_json(CACHE_PATH, cache)


def role_str(rank_val: Any) -> str:
    role_map = {1: "R1", 2: "R2", 3: "R3", 4: "R4", 5: "Leader (R5)"}
    try:
        iv = int(rank_val)
    except Exception:
        iv = 1
    return role_map.get(iv, f"R{iv}")


def get_tier_and_passes(migrate_power: Any) -> tuple[str, int]:
    try:
        mp = int(migrate_power or 0)
    except Exception:
        mp = 0
    if mp <= 20_000_000:
        return ("Regular (Che1)", 10)
    if mp <= 40_000_000:
        return ("Intermediate (Che2)", 15)
    if mp <= 100_000_000:
        return ("Advanced (Che3)", 20)
    return ("Elite (Che4)", 50)


def _clean_abbr(raw: str) -> str:
    return str(raw or "").replace("[", "").replace("]", "").strip()


def _clean_tab_name(abbr: str, name: str) -> str:
    clean_abbr = _clean_abbr(abbr)
    clean_name = str(name or "")
    for ch in "[]:/\\?*":
        clean_name = clean_name.replace(ch, "")
    return f"{clean_abbr} - {clean_name.strip()}"[:31].strip()


def _quote_sheet(title: str) -> str:
    return "'" + title.replace("'", "''") + "'"


def _resolve_active_pid(explicit_pid: int | None = None) -> int | None:
    cd = _load_cd()
    if explicit_pid is not None:
        return int(explicit_pid)
    running = cd.find_running_processes()
    if not running:
        return None
    mains = [p for p in running if str(p.get("role") or "").lower() == "main"]
    chosen = mains[0] if mains else running[0]
    return int(chosen["pid"])


def fetch_live_state_alliances(pid: int, states: list[int]) -> dict[int, list[dict[str, Any]]]:
    import frida

    js = f"""
    const mod = Process.getModuleByName('xlua.dll');
    const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
    const top = nf('lua_gettop', 'int', ['pointer']);
    const settop = nf('lua_settop', 'void', ['pointer', 'int']);
    const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
    const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
    const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
    const rawi = nf('lua_rawgeti', 'int', ['pointer', 'int', 'int64']);
    const raw = nf('lua_rawget', 'int', ['pointer', 'int']);
    const next = nf('lua_next', 'int', ['pointer', 'int']);
    const nil = nf('lua_pushnil', 'void', ['pointer']);
    const push = nf('lua_pushstring', 'pointer', ['pointer', 'pointer']);
    const typ = nf('lua_type', 'int', ['pointer', 'int']);
    const num = nf('lua_tonumberx', 'double', ['pointer', 'int', 'pointer']);
    const ptrfn = nf('lua_topointer', 'pointer', ['pointer', 'int']);
    const length = Memory.alloc(8);
    const registry = nf('xlua_get_registry_index', 'int', [])();
    const stringCache = new Map();
    function allocStr(s) {{
        if (!stringCache.has(s)) stringCache.set(s, Memory.allocUtf8String(s));
        return stringCache.get(s);
    }}
    function field(L, index, key) {{ push(L, allocStr(key)); return raw(L, index); }}
    function getString(L, index, maxLen = 256) {{
        if (typ(L, index) !== 4) return null;
        const p = str(L, index, length);
        const sz = Number(length.readU64());
        if (sz === 0) return '';
        if (sz > maxLen) return null;
        return p.readUtf8String(sz);
    }}
    function getNumber(L, index) {{ return typ(L, index) === 3 ? num(L, index, ptr(0)) : null; }}
    function dumpLuaTable(L, index, depth = 0, maxDepth = 3) {{
        if (depth > maxDepth) return '<truncated>';
        const saved = top(L);
        const obj = {{}};
        nil(L);
        let count = 0;
        while (next(L, index) && count++ < 150) {{
            let key = null;
            const kt = typ(L, -2);
            if (kt === 4) key = getString(L, -2, 80);
            else if (kt === 3) key = String(getNumber(L, -2));
            else key = 'k_' + kt;
            let val = null;
            const vt = typ(L, -1);
            if (vt === 1) val = true;
            else if (vt === 3) val = getNumber(L, -1);
            else if (vt === 4) val = getString(L, -1, 512);
            else if (vt === 5) val = dumpLuaTable(L, top(L), depth + 1, maxDepth);
            else val = '<type ' + vt + '>';
            if (key !== null) obj[key] = val;
            settop(L, top(L) - 1);
        }}
        settop(L, saved);
        return obj;
    }}
    let handler = null;
    const queue = {json.dumps(states)};
    let lastQuery = 0;
    let busy = false;
    let done = false;
    Interceptor.attach(mod.getExportByName('lua_pcallk'), {{
        onEnter(args) {{
            if (busy || done) return;
            const L = args[0];
            const nargs = args[1].toInt32();
            const saved = top(L);
            busy = true;
            try {{
                if (nargs === 2) {{
                    if (handler === null && rawi(L, registry, 2) === 5) {{
                        const g = top(L);
                        if (field(L, g, 'GameMain') === 5 && field(L, top(L), 'Protocal') === 6) {{
                            handler = ptrfn(L, -1).toString();
                        }}
                        settop(L, g);
                    }}
                    if (handler !== null && ptrfn(L, saved - nargs).toString() === handler) {{
                        const cmd = getString(L, saved - 1, 80);
                        if (cmd === 'alliance.rank.limit' || cmd === 'alliance.rank') {{
                            send({{kind: 'alliances', payload: dumpLuaTable(L, saved, 0, 3)}});
                        }}
                    }}
                }}
                const now = Date.now();
                if (queue.length > 0 && (now - lastQuery) >= 400) {{
                    const st = queue.shift();
                    lastQuery = now;
                    const lua = 'return SFSNetwork.SendMessage(MsgDefines.AllianceRankLimit, ' + st + ')';
                    if (loadstring(L, allocStr(lua)) === 0) pcall(L, 0, 0, 0);
                }}
                if (queue.length === 0 && (now - lastQuery) > 2500) {{
                    done = true;
                    send({{kind: 'done'}});
                }}
            }} finally {{
                settop(L, saved);
                busy = false;
            }}
        }}
    }});
    """

    session = frida.attach(pid)
    script = session.create_script(js)
    captured: dict[int, list[dict[str, Any]]] = {}
    drained = False

    def on_msg(m, _d):
        nonlocal drained
        if m.get("type") != "send":
            return
        pld = m["payload"]
        if pld.get("kind") == "done":
            drained = True
            return
        if pld.get("kind") == "alliances":
            body = pld.get("payload", {})
            ranking = body.get("serverRanking") or body.get("allianceRanking") or body.get("list") or {}
            if isinstance(ranking, dict) and ranking:
                items = [v for v in ranking.values() if isinstance(v, dict)]
                items.sort(key=lambda x: int(x.get("rank") or 999))
                if items:
                    sid = int(items[0].get("serverId") or 0)
                    if sid in states:
                        captured[sid] = items[:10]

    script.on("message", on_msg)
    script.load()
    deadline = time.time() + max(12.0, len(states) * 1.1)
    while time.time() < deadline:
        if len(captured) >= len(states) and drained:
            break
        if len(captured) >= len(states):
            break
        time.sleep(0.25)
    try:
        session.detach()
    except Exception:
        pass

    for sid, top10 in captured.items():
        st_dir = BRACKET_DATA_DIR / f"state_{sid}"
        _atomic_write_json(st_dir / "top10_alliances.json", top10, indent=2)
    return captured


def fetch_live_alliance_rosters(
    pid: int, alliances_by_state: dict[int, list[dict[str, Any]]]
) -> dict[int, list[dict[str, Any]]]:
    import frida

    aid_queue: list[str] = []
    meta_by_aid: dict[str, tuple[int, dict[str, Any]]] = {}
    for sid, alist in sorted(alliances_by_state.items()):
        for a in alist:
            aid = str(a.get("uid") or "")
            if aid:
                aid_queue.append(aid)
                meta_by_aid[aid] = (sid, a)

    if not aid_queue:
        return {}

    js = f"""
    const mod = Process.getModuleByName('xlua.dll');
    const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
    const top = nf('lua_gettop', 'int', ['pointer']);
    const settop = nf('lua_settop', 'void', ['pointer', 'int']);
    const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
    const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
    const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
    const rawi = nf('lua_rawgeti', 'int', ['pointer', 'int', 'int64']);
    const raw = nf('lua_rawget', 'int', ['pointer', 'int']);
    const next = nf('lua_next', 'int', ['pointer', 'int']);
    const nil = nf('lua_pushnil', 'void', ['pointer']);
    const push = nf('lua_pushstring', 'pointer', ['pointer', 'pointer']);
    const typ = nf('lua_type', 'int', ['pointer', 'int']);
    const num = nf('lua_tonumberx', 'double', ['pointer', 'int', 'pointer']);
    const ptrfn = nf('lua_topointer', 'pointer', ['pointer', 'int']);
    const length = Memory.alloc(8);
    const registry = nf('xlua_get_registry_index', 'int', [])();
    const stringCache = new Map();
    function allocStr(s) {{
        if (!stringCache.has(s)) stringCache.set(s, Memory.allocUtf8String(s));
        return stringCache.get(s);
    }}
    function field(L, index, key) {{ push(L, allocStr(key)); return raw(L, index); }}
    function getString(L, index, maxLen = 256) {{
        if (typ(L, index) !== 4) return null;
        const p = str(L, index, length);
        const sz = Number(length.readU64());
        if (sz === 0) return '';
        if (sz > maxLen) return null;
        return p.readUtf8String(sz);
    }}
    function getNumber(L, index) {{ return typ(L, index) === 3 ? num(L, index, ptr(0)) : null; }}
    function dumpLuaTable(L, index, depth = 0, maxDepth = 3) {{
        if (depth > maxDepth) return '<truncated>';
        const saved = top(L);
        const obj = {{}};
        nil(L);
        let count = 0;
        while (next(L, index) && count++ < 150) {{
            let key = null;
            const kt = typ(L, -2);
            if (kt === 4) key = getString(L, -2, 80);
            else if (kt === 3) key = String(getNumber(L, -2));
            else key = 'k_' + kt;
            let val = null;
            const vt = typ(L, -1);
            if (vt === 1) val = true;
            else if (vt === 3) val = getNumber(L, -1);
            else if (vt === 4) val = getString(L, -1, 512);
            else if (vt === 5) val = dumpLuaTable(L, top(L), depth + 1, maxDepth);
            else val = '<type ' + vt + '>';
            if (key !== null) obj[key] = val;
            settop(L, top(L) - 1);
        }}
        settop(L, saved);
        return obj;
    }}
    let handler = null;
    const queue = {json.dumps(aid_queue)};
    let lastQuery = 0;
    let busy = false;
    let done = false;
    Interceptor.attach(mod.getExportByName('lua_pcallk'), {{
        onEnter(args) {{
            if (busy || done) return;
            const L = args[0];
            const nargs = args[1].toInt32();
            const saved = top(L);
            busy = true;
            try {{
                if (nargs === 2) {{
                    if (handler === null && rawi(L, registry, 2) === 5) {{
                        const g = top(L);
                        if (field(L, g, 'GameMain') === 5 && field(L, top(L), 'Protocal') === 6) {{
                            handler = ptrfn(L, -1).toString();
                        }}
                        settop(L, g);
                    }}
                    if (handler !== null && ptrfn(L, saved - nargs).toString() === handler) {{
                        const cmd = getString(L, saved - 1, 80);
                        if (cmd === 'al.rank') {{
                            send({{kind: 'roster', payload: dumpLuaTable(L, saved, 0, 3)}});
                        }}
                    }}
                }}
                const now = Date.now();
                if (queue.length > 0 && (now - lastQuery) >= 240) {{
                    const aid = queue.shift();
                    lastQuery = now;
                    const lua = 'return SFSNetwork.SendMessage(MsgDefines.AlRank, \"' + aid + '\")';
                    if (loadstring(L, allocStr(lua)) === 0) pcall(L, 0, 0, 0);
                }}
                if (queue.length === 0 && (now - lastQuery) > 3000) {{
                    done = true;
                    send({{kind: 'done'}});
                }}
            }} finally {{
                settop(L, saved);
                busy = false;
            }}
        }}
    }});
    """

    session = frida.attach(pid)
    script = session.create_script(js)
    rosters_by_aid: dict[str, list[dict[str, Any]]] = {}
    drained = False

    def on_msg(m, _d):
        nonlocal drained
        if m.get("type") != "send":
            return
        pld = m["payload"]
        if pld.get("kind") == "done":
            drained = True
            return
        if pld.get("kind") == "roster":
            body = pld.get("payload", {})
            aid = str(body.get("allianceId") or "")
            raw_list = body.get("list") or {}
            if aid and isinstance(raw_list, dict):
                rosters_by_aid[aid] = [v for v in raw_list.values() if isinstance(v, dict)]

    script.on("message", on_msg)
    script.load()
    deadline = time.time() + max(15.0, len(aid_queue) * 0.45 + 6.0)
    while time.time() < deadline:
        if len(rosters_by_aid) >= len(aid_queue) or drained:
            break
        time.sleep(0.3)
    try:
        session.detach()
    except Exception:
        pass

    result_by_state: dict[int, list[dict[str, Any]]] = {}
    for sid, alist in sorted(alliances_by_state.items()):
        built_rosters = []
        for a in alist:
            aid = str(a.get("uid") or "")
            members = rosters_by_aid.get(aid)
            if members is None:
                continue
            built_rosters.append(
                {
                    "rank": int(a.get("rank") or 1),
                    "abbr": a.get("abbr") or "",
                    "name": a.get("alliancename") or a.get("name") or "",
                    "leader": a.get("leader") or "",
                    "fightpower": int(a.get("fightpower") or 0),
                    "allianceId": aid,
                    "member_count": len(members),
                    "members": members,
                }
            )
        if built_rosters:
            st_dir = BRACKET_DATA_DIR / f"state_{sid}"
            _atomic_write_json(st_dir / "top10_alliance_rosters.json", built_rosters, indent=2)
            result_by_state[sid] = built_rosters
    return result_by_state


def fetch_live_player_profiles(pid: int, uids: list[str]) -> dict[str, dict[str, Any]]:
    import frida

    if not uids:
        return {}
    js = f"""
    const mod = Process.getModuleByName('xlua.dll');
    const nf = (name, ret, args) => new NativeFunction(mod.getExportByName(name), ret, args);
    const top = nf('lua_gettop', 'int', ['pointer']);
    const settop = nf('lua_settop', 'void', ['pointer', 'int']);
    const loadstring = nf('luaL_loadstring', 'int', ['pointer', 'pointer']);
    const pcall = nf('lua_pcall', 'int', ['pointer', 'int', 'int', 'int']);
    const str = nf('lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']);
    const rawi = nf('lua_rawgeti', 'int', ['pointer', 'int', 'int64']);
    const raw = nf('lua_rawget', 'int', ['pointer', 'int']);
    const next = nf('lua_next', 'int', ['pointer', 'int']);
    const nil = nf('lua_pushnil', 'void', ['pointer']);
    const push = nf('lua_pushstring', 'pointer', ['pointer', 'pointer']);
    const typ = nf('lua_type', 'int', ['pointer', 'int']);
    const num = nf('lua_tonumberx', 'double', ['pointer', 'int', 'pointer']);
    const ptrfn = nf('lua_topointer', 'pointer', ['pointer', 'int']);
    const length = Memory.alloc(8);
    const registry = nf('xlua_get_registry_index', 'int', [])();
    const stringCache = new Map();
    function allocStr(s) {{
        if (!stringCache.has(s)) stringCache.set(s, Memory.allocUtf8String(s));
        return stringCache.get(s);
    }}
    function field(L, index, key) {{ push(L, allocStr(key)); return raw(L, index); }}
    function getString(L, index, maxLen = 256) {{
        if (typ(L, index) !== 4) return null;
        const p = str(L, index, length);
        const sz = Number(length.readU64());
        if (sz === 0) return '';
        if (sz > maxLen) return null;
        return p.readUtf8String(sz);
    }}
    function getNumber(L, index) {{ return typ(L, index) === 3 ? num(L, index, ptr(0)) : null; }}
    function dumpLuaTable(L, index, depth = 0, maxDepth = 2) {{
        if (depth > maxDepth) return '<truncated>';
        const saved = top(L);
        const obj = {{}};
        nil(L);
        let count = 0;
        while (next(L, index) && count++ < 80) {{
            let key = null;
            const kt = typ(L, -2);
            if (kt === 4) key = getString(L, -2, 80);
            else if (kt === 3) key = String(getNumber(L, -2));
            else key = 'k_' + kt;
            let val = null;
            const vt = typ(L, -1);
            if (vt === 1) val = true;
            else if (vt === 3) val = getNumber(L, -1);
            else if (vt === 4) val = getString(L, -1, 512);
            else if (vt === 5) val = dumpLuaTable(L, top(L), depth + 1, maxDepth);
            else val = '<type ' + vt + '>';
            if (key !== null) obj[key] = val;
            settop(L, top(L) - 1);
        }}
        settop(L, saved);
        return obj;
    }}
    let handler = null;
    const queue = {json.dumps(uids)};
    let lastQuery = 0;
    let busy = false;
    let done = false;
    Interceptor.attach(mod.getExportByName('lua_pcallk'), {{
        onEnter(args) {{
            if (busy || done) return;
            const L = args[0];
            const nargs = args[1].toInt32();
            const saved = top(L);
            busy = true;
            try {{
                if (nargs === 2) {{
                    if (handler === null && rawi(L, registry, 2) === 5) {{
                        const g = top(L);
                        if (field(L, g, 'GameMain') === 5 && field(L, top(L), 'Protocal') === 6) {{
                            handler = ptrfn(L, -1).toString();
                        }}
                        settop(L, g);
                    }}
                    if (handler !== null && ptrfn(L, saved - nargs).toString() === handler) {{
                        const cmd = getString(L, saved - 1, 80);
                        if (cmd === 'get.new.user.info' || cmd === 'migrate.user.info') {{
                            send({{kind: 'user_info', payload: dumpLuaTable(L, saved, 0, 2)}});
                        }}
                    }}
                }}
                const now = Date.now();
                if (queue.length > 0 && (now - lastQuery) >= 70) {{
                    const uid = queue.shift();
                    lastQuery = now;
                    const lua = 'return DataCenter.PlayerInfoDataManager:GetPlayerInfoFromServer(\"' + uid + '\")';
                    if (loadstring(L, allocStr(lua)) === 0) pcall(L, 0, 0, 0);
                }}
                if (queue.length === 0 && (now - lastQuery) > 2500) {{
                    done = true;
                    send({{kind: 'done'}});
                }}
            }} finally {{
                settop(L, saved);
                busy = false;
            }}
        }}
    }});
    """

    session = frida.attach(pid)
    script = session.create_script(js)
    captured: dict[str, dict[str, Any]] = {}
    drained = False

    def on_msg(m, _d):
        nonlocal drained
        if m.get("type") != "send":
            return
        pld = m["payload"]
        if pld.get("kind") == "done":
            drained = True
            return
        if pld.get("kind") == "user_info":
            body = pld.get("payload", {})
            uid = str(body.get("uid") or "")
            if uid and uid != "None":
                captured[uid] = body

    script.on("message", on_msg)
    script.load()
    deadline = time.time() + max(10.0, len(uids) * 0.10 + 5.0)
    while time.time() < deadline:
        if len(captured) >= len(uids) or drained:
            break
        time.sleep(0.25)
    try:
        session.detach()
    except Exception:
        pass
    return captured


def _load_rosters_from_xlsx(state_id: int) -> list[dict[str, Any]]:
    xlsx_path = XLSX_DIR / f"State {state_id} Migration.xlsx"
    if not xlsx_path.exists():
        return []
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ov_name = f"State {state_id} Overview"
    if ov_name not in wb.sheetnames:
        return []
    ws_ov = wb[ov_name]
    alliances: list[dict[str, Any]] = []
    sheet_lookup = {s: s for s in wb.sheetnames}
    for row_idx in range(9, 19):
        rk = ws_ov.cell(row=row_idx, column=1).value
        tag = ws_ov.cell(row=row_idx, column=2).value
        name = ws_ov.cell(row=row_idx, column=3).value
        leader = ws_ov.cell(row=row_idx, column=4).value
        pwr = ws_ov.cell(row=row_idx, column=5).value
        if not tag or tag == "TOTAL":
            continue
        abbr = _clean_abbr(str(tag))
        target_tab = _clean_tab_name(abbr, str(name or ""))
        ws_al = None
        if target_tab in sheet_lookup:
            ws_al = wb[target_tab]
        else:
            for sname in wb.sheetnames:
                if sname.startswith(abbr + " -") or sname == abbr:
                    ws_al = wb[sname]
                    break
        members = []
        if ws_al is not None:
            for r in range(6, ws_al.max_row + 1):
                pname = ws_al.cell(row=r, column=4).value
                puid = ws_al.cell(row=r, column=5).value
                if not pname and not puid:
                    continue
                role_txt = str(ws_al.cell(row=r, column=2).value or "R1")
                rank_num = 5 if "5" in role_txt else int(role_txt.replace("R", "") or 1) if role_txt.replace("R", "").isdigit() else 1
                mp = int(ws_al.cell(row=r, column=6).value or 0)
                members.append(
                    {
                        "rank": rank_num,
                        "mainBuildingLevel": int(ws_al.cell(row=r, column=3).value or 0),
                        "name": str(pname or ""),
                        "uid": str(puid or "").lstrip("'"),
                        "authoritative_migrate_power": mp,
                        "total_power": int(ws_al.cell(row=r, column=9).value or 0),
                        "player_max_power": int(ws_al.cell(row=r, column=10).value or 0),
                        "building_power": int(ws_al.cell(row=r, column=11).value or 0),
                        "science_power": int(ws_al.cell(row=r, column=12).value or 0),
                        "hero_power": int(ws_al.cell(row=r, column=13).value or 0),
                        "tank_power": int(ws_al.cell(row=r, column=14).value or 0),
                        "army_power": int(ws_al.cell(row=r, column=15).value or 0),
                        "status": str(ws_al.cell(row=r, column=16).value or "100% IN-GAME VERIFIED"),
                    }
                )
        alliances.append(
            {
                "rank": int(rk or (len(alliances) + 1)),
                "abbr": abbr,
                "name": str(name or ""),
                "leader": str(leader or ""),
                "total_fightpower": int(pwr or 0),
                "members": members,
            }
        )
    return alliances


def build_state_model(state_id: int, cache: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    roster_candidates = [
        BRACKET_DATA_DIR / f"state_{state_id}" / "top10_alliance_rosters.json",
        LEGACY_BRACKET_DATA / f"state_{state_id}" / "top10_alliance_rosters.json",
    ]
    raw_rosters = None
    for cand in roster_candidates:
        if cand.exists():
            with cand.open("r", encoding="utf-8") as fh:
                raw_rosters = json.load(fh)
            break

    if raw_rosters is None:
        raw_from_xlsx = _load_rosters_from_xlsx(state_id)
        if not raw_from_xlsx:
            raise FileNotFoundError(f"No roster JSON or local XLSX found for state {state_id}")
        model = []
        for al in raw_from_xlsx:
            members_data = []
            for m in al["members"]:
                uid = str(m["uid"])
                pld = cache.get(uid, {})
                mp = int(pld.get("migratePower") or m["authoritative_migrate_power"] or m["total_power"] or 0)
                tier, passes = get_tier_and_passes(mp)
                members_data.append(
                    {
                        "rank": m["rank"],
                        "uid": uid,
                        "name": pld.get("name") or m["name"],
                        "mainBuildingLevel": int(pld.get("mainBuildingLevel") or m["mainBuildingLevel"] or 0),
                        "authoritative_migrate_power": mp,
                        "tier": tier,
                        "passes_required": passes,
                        "total_power": int(pld.get("power") or m["total_power"] or 0),
                        "player_max_power": int(pld.get("playerMaxPower") or m["player_max_power"] or 0),
                        "building_power": int(pld.get("buildingPower") or m["building_power"] or 0),
                        "science_power": int(pld.get("sciencePower") or m["science_power"] or 0),
                        "hero_power": int(pld.get("heroPower") or m["hero_power"] or 0),
                        "tank_power": int(pld.get("tankPower") or m["tank_power"] or 0),
                        "army_power": int(pld.get("armyPower") or m["army_power"] or 0),
                    }
                )
            members_data.sort(key=lambda x: (x["authoritative_migrate_power"], x["total_power"]), reverse=True)
            tier_counts: dict[str, int] = {}
            for md in members_data:
                tier_counts[md["tier"]] = tier_counts.get(md["tier"], 0) + 1
            model.append(
                {
                    "rank": al["rank"],
                    "abbr": al["abbr"],
                    "name": al["name"],
                    "leader": al["leader"],
                    "total_fightpower": al["total_fightpower"],
                    "total_passes_required": sum(x["passes_required"] for x in members_data),
                    "tier_distribution": tier_counts,
                    "members": members_data,
                }
            )
        model.sort(key=lambda a: int(a.get("rank") or 999))
        return model

    model = []
    for al in raw_rosters:
        members_data = []
        for m in al.get("members", []):
            uid = str(m.get("uid") or "")
            pld = cache.get(uid, {})
            live_power = int(m.get("power") or 0)
            mp = int(pld.get("migratePower") or live_power or pld.get("power") or 0)
            tier, passes = get_tier_and_passes(mp)
            members_data.append(
                {
                    "rank": int(m.get("rank") or 1),
                    "uid": uid,
                    "name": pld.get("name") or m.get("name") or "",
                    "mainBuildingLevel": int(pld.get("mainBuildingLevel") or m.get("mainCityLv") or 0),
                    "authoritative_migrate_power": mp,
                    "tier": tier,
                    "passes_required": passes,
                    "total_power": int(live_power or pld.get("power") or 0),
                    "player_max_power": int(pld.get("playerMaxPower") or 0),
                    "building_power": int(pld.get("buildingPower") or 0),
                    "science_power": int(pld.get("sciencePower") or 0),
                    "hero_power": int(pld.get("heroPower") or 0),
                    "tank_power": int(pld.get("tankPower") or 0),
                    "army_power": int(pld.get("armyPower") or 0),
                }
            )
        members_data.sort(key=lambda x: (x["authoritative_migrate_power"], x["total_power"]), reverse=True)
        tier_counts: dict[str, int] = {}
        for md in members_data:
            tier_counts[md["tier"]] = tier_counts.get(md["tier"], 0) + 1
        model.append(
            {
                "rank": int(al.get("rank") or (len(model) + 1)),
                "abbr": _clean_abbr(str(al.get("abbr") or "")),
                "name": str(al.get("name") or al.get("alliancename") or ""),
                "leader": str(al.get("leader") or ""),
                "total_fightpower": int(al.get("fightpower") or al.get("total_fightpower") or 0),
                "total_passes_required": sum(x["passes_required"] for x in members_data),
                "tier_distribution": tier_counts,
                "members": members_data,
            }
        )
    model.sort(key=lambda a: int(a.get("rank") or 999))
    return model


def _ensure_local_xlsx(state_id: int, cache: dict[str, dict[str, Any]]) -> None:
    """Update local bracket XLSX using build_all_bracket_native_sheets styling when JSON rosters exist."""
    roster_file = BRACKET_DATA_DIR / f"state_{state_id}" / "top10_alliance_rosters.json"
    builder_path = TOOLS_DIR / "build all bracket native sheets.py"
    if not roster_file.exists() or not builder_path.exists():
        return
    try:
        spec = importlib.util.spec_from_file_location("build_native", str(builder_path))
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.DATA_DIR = BRACKET_DATA_DIR
        XLSX_DIR.mkdir(parents=True, exist_ok=True)
        mod.OUT_XLSX_DIR = XLSX_DIR
        mod.generate_state_master_excel(state_id, cache)
    except Exception:
        pass


def _formula_cells_in_range(sheet_id: str, a1_range: str) -> set[tuple[int, int]]:
    proc = _run_gsheets(["readonly", "read", sheet_id, a1_range, "--value-render-option", "FORMULA", "--json"])
    rows = json.loads(proc.stdout or "[]")
    formulas: set[tuple[int, int]] = set()
    for r_idx, row in enumerate(rows, start=1):
        for c_idx, val in enumerate(row, start=1):
            if isinstance(val, str) and val.startswith("="):
                formulas.add((r_idx, c_idx))
    return formulas


def _cell_ref(row: int, col: int) -> str:
    col_str = ""
    c = col
    while c > 0:
        c, rem = divmod(c - 1, 26)
        col_str = chr(65 + rem) + col_str
    return f"{col_str}{row}"


def sync_single_state_to_drive(
    state_id: int,
    alliances: list[dict[str, Any]],
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = manifest or load_manifest()
    sheet_entry = manifest.get("spreadsheets", {}).get(str(state_id))
    if not sheet_entry or not sheet_entry.get("id"):
        raise KeyError(f"Spreadsheet ID not found in manifest for state {state_id}")

    spreadsheet_id = str(sheet_entry["id"])
    list_proc = _run_gsheets(["readonly", "list-sheets", spreadsheet_id, "--json"])
    tabs = json.loads(list_proc.stdout or "[]")
    if not tabs:
        raise RuntimeError(f"No tabs found in Google Sheet {spreadsheet_id} (State {state_id})")

    expected_ov = f"State {state_id} Overview"
    ov_tab = next((t for t in tabs if t["title"] == expected_ov), tabs[0])
    ov_title = ov_tab["title"]
    q_ov = _quote_sheet(ov_title)

    alliance_tabs = [t for t in tabs if t["id"] != ov_tab["id"]]
    used_tab_ids: set[int] = set()
    assigned_tabs: dict[int, str] = {}

    for idx, a in enumerate(alliances):
        target_title = _clean_tab_name(a["abbr"], a["name"])
        abbr = _clean_abbr(a["abbr"])
        match = next((t for t in alliance_tabs if t["id"] not in used_tab_ids and t["title"] == target_title), None)
        if match is None:
            match = next(
                (
                    t
                    for t in alliance_tabs
                    if t["id"] not in used_tab_ids and (t["title"].startswith(f"{abbr} -") or t["title"] == abbr)
                ),
                None,
            )
            if match is not None and match["title"] != target_title:
                _run_gsheets(
                    ["mutate", "rename-sheet", spreadsheet_id, "--sheet-id", str(match["id"]), "--title", target_title]
                )
                match["title"] = target_title
        if match is not None:
            used_tab_ids.add(match["id"])
            assigned_tabs[idx] = match["title"]

    spare_tabs = [t for t in alliance_tabs if t["id"] not in used_tab_ids]
    for idx, a in enumerate(alliances):
        if idx in assigned_tabs:
            continue
        target_title = _clean_tab_name(a["abbr"], a["name"])
        if spare_tabs:
            spare = spare_tabs.pop(0)
            _run_gsheets(
                ["mutate", "rename-sheet", spreadsheet_id, "--sheet-id", str(spare["id"]), "--title", target_title]
            )
            assigned_tabs[idx] = target_title
        else:
            template_id = alliance_tabs[0]["id"] if alliance_tabs else ov_tab["id"]
            _run_gsheets(["mutate", "add-sheet", spreadsheet_id, "--title", target_title])
            assigned_tabs[idx] = target_title

    ov_formulas = _formula_cells_in_range(spreadsheet_id, f"{q_ov}!A1:M20")
    sync_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    tot_power = sum(int(a["total_fightpower"]) for a in alliances)
    tot_members = sum(len(a["members"]) for a in alliances)
    tot_passes = sum(int(a["total_passes_required"]) for a in alliances)
    tot_elite = sum(int(a["tier_distribution"].get("Elite (Che4)", 0)) for a in alliances)
    tot_adv = sum(int(a["tier_distribution"].get("Advanced (Che3)", 0)) for a in alliances)
    tot_mid = sum(int(a["tier_distribution"].get("Intermediate (Che2)", 0)) for a in alliances)
    tot_reg = sum(int(a["tier_distribution"].get("Regular (Che1)", 0)) for a in alliances)
    avg_passes = round(tot_passes / tot_members, 1) if tot_members > 0 else 0.0

    batch_ops: list[dict[str, Any]] = []
    if (1, 1) not in ov_formulas:
        batch_ops.append({"op": "write", "range": f"{q_ov}!A1", "data": [[f"State {state_id} Top 10 Alliances - Grouping 689-704"]]})
    if (2, 1) not in ov_formulas:
        batch_ops.append(
            {
                "op": "write",
                "range": f"{q_ov}!A2",
                "data": [[f"Official In-Game Verified Migration Scores | Group 200162 | Synced: {sync_ts}"]],
            }
        )

    kpi_cells = [
        (5, 2, f"{len(alliances)} Alliances"),
        (5, 4, f"{tot_members:,} Players"),
        (5, 6, f"{tot_passes:,} Passes"),
        (5, 8, f"{tot_adv + tot_elite:,} Players"),
        (5, 10, f"{avg_passes:.1f} Passes"),
        (5, 12, f"{tot_power / 1e9:.2f} Billion"),
    ]
    for r, c, val in kpi_cells:
        if (r, c) not in ov_formulas:
            batch_ops.append({"op": "write", "range": f"{q_ov}!{_cell_ref(r, c)}", "data": [[val]]})

    ov_rows = []
    for a in alliances:
        members = a["members"]
        dist = a["tier_distribution"]
        top_m = members[0] if members else {}
        top_str = f"{top_m.get('name', 'N/A')} ({int(top_m.get('authoritative_migrate_power') or 0):,})"
        a_avg = round(a["total_passes_required"] / len(members), 1) if members else 0.0
        ov_rows.append(
            [
                int(a["rank"]),
                f"[{_clean_abbr(a['abbr'])}]",
                a["name"],
                a["leader"],
                int(a["total_fightpower"]),
                len(members),
                int(a["total_passes_required"]),
                a_avg,
                int(dist.get("Elite (Che4)", 0)),
                int(dist.get("Advanced (Che3)", 0)),
                int(dist.get("Intermediate (Che2)", 0)),
                int(dist.get("Regular (Che1)", 0)),
                top_str,
            ]
        )

    if ov_rows:
        for offset, row_vals in enumerate(ov_rows):
            r_num = 9 + offset
            for c_idx, cell_val in enumerate(row_vals, start=1):
                if (r_num, c_idx) in ov_formulas:
                    row_vals[c_idx - 1] = None
        if not any((9 + i, c) in ov_formulas for i in range(len(ov_rows)) for c in range(1, 14)):
            batch_ops.append({"op": "write", "range": f"{q_ov}!A9:M{8 + len(ov_rows)}", "data": ov_rows})

    tot_vals = [tot_power, tot_members, tot_passes, avg_passes, tot_elite, tot_adv, tot_mid, tot_reg]
    if not any((19, c) in ov_formulas for c in range(5, 13)):
        batch_ops.append({"op": "write", "range": f"{q_ov}!E19:L19", "data": [tot_vals]})

    total_rows_written = 0
    for idx, a in enumerate(alliances):
        tab_title = assigned_tabs[idx]
        q_tab = _quote_sheet(tab_title)
        members = a["members"]
        dist = a["tier_distribution"]
        abbr = _clean_abbr(a["abbr"])

        c_e = int(dist.get("Elite (Che4)", 0))
        c_adv = int(dist.get("Advanced (Che3)", 0))
        c_mid = int(dist.get("Intermediate (Che2)", 0))
        c_reg = int(dist.get("Regular (Che1)", 0))

        batch_ops.append({"op": "write", "range": f"{q_tab}!A1", "data": [[f"[{abbr}] {a['name']} (State {state_id})"]]})
        batch_ops.append(
            {
                "op": "write",
                "range": f"{q_tab}!A2",
                "data": [[f"State Rank: #{a['rank']} | Leader: {a['leader']} | Total Combat Power: {a['total_fightpower']:,} | Members: {len(members)}"]],
            }
        )
        batch_ops.append({"op": "write", "range": f"{q_tab}!A3", "data": [[f"Total Members: {len(members)}"]]})
        batch_ops.append(
            {
                "op": "write",
                "range": f"{q_tab}!D3",
                "data": [[f"Total Passes: {a['total_passes_required']:,} Passes (Members: {len(members)})"]],
            }
        )
        batch_ops.append(
            {
                "op": "write",
                "range": f"{q_tab}!J3",
                "data": [[f"Tier Breakdown: Elite (>100M): {c_e} | Advanced (40-100M): {c_adv} | Intermediate (20-40M): {c_mid} | Regular (<=20M): {c_reg}"]],
            }
        )

        member_matrix = []
        for m_idx, m in enumerate(members, start=1):
            member_matrix.append(
                [
                    m_idx,
                    role_str(m["rank"]),
                    int(m["mainBuildingLevel"] or 0),
                    str(m["name"] or ""),
                    "'" + str(m["uid"] or ""),
                    int(m["authoritative_migrate_power"] or 0),
                    m["tier"],
                    int(m["passes_required"] or 0),
                    int(m["total_power"] or 0),
                    int(m["player_max_power"] or 0),
                    int(m["building_power"] or 0),
                    int(m["science_power"] or 0),
                    int(m["hero_power"] or 0),
                    int(m["tank_power"] or 0),
                    int(m["army_power"] or 0),
                    "100% IN-GAME VERIFIED",
                ]
            )
            total_rows_written += 1

        if member_matrix:
            batch_ops.append({"op": "write", "range": f"{q_tab}!A6:P{5 + len(member_matrix)}", "data": member_matrix})

        clear_start = 6 + len(member_matrix)
        if clear_start <= 115:
            batch_ops.append(
                {"op": "clear", "range": f"{q_tab}!A{clear_start}:P115"}
            )

    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as tf:
        json.dump(batch_ops, tf, ensure_ascii=False)
        tmp_path = tf.name

    try:
        _run_gsheets(["mutate", "batch", spreadsheet_id, "-f", tmp_path], timeout=90)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return {
        "ok": True,
        "state_id": state_id,
        "spreadsheet_id": spreadsheet_id,
        "url": sheet_entry.get("url", ""),
        "alliances_synced": len(alliances),
        "members_written": total_rows_written,
        "synced_at": sync_ts,
    }


def sync_states(
    states: list[int] | None = None,
    refresh_live: bool = False,
    refresh_profiles: bool = False,
    max_profile_fetches: int = 800,
    pid: int | None = None,
) -> dict[str, Any]:
    target_states = states or list(ALL_BRACKET_STATES)
    manifest = load_manifest()
    cache = load_profile_cache()

    if refresh_live:
        active_pid = _resolve_active_pid(pid)
        if not active_pid:
            raise RuntimeError("No running Last Z client found for live bracket refresh.")
        print(f"[Live Refresh] Using game client PID {active_pid} for states {target_states}...")
        live_alliances = fetch_live_state_alliances(active_pid, target_states)
        print(f"[Live Refresh] Captured Top-10 alliance rankings for {len(live_alliances)}/{len(target_states)} states.")
        live_rosters = fetch_live_alliance_rosters(active_pid, live_alliances)
        print(f"[Live Refresh] Captured live rosters for {len(live_rosters)} states.")

        candidate_uids: list[tuple[int, str]] = []
        seen_uids: set[str] = set()
        for sid, alist in live_rosters.items():
            for al in alist:
                for m in al.get("members", []):
                    uid = str(m.get("uid") or "")
                    if not uid or uid in seen_uids:
                        continue
                    seen_uids.add(uid)
                    if uid not in cache:
                        candidate_uids.append((10**12, uid))
                    elif refresh_profiles:
                        live_pwr = int(m.get("power") or 0)
                        old_pwr = int(cache[uid].get("power") or 0)
                        delta = abs(live_pwr - old_pwr)
                        if delta >= 1_000_000:
                            candidate_uids.append((delta, uid))

        candidate_uids.sort(key=lambda item: item[0], reverse=True)
        to_fetch = [u for _, u in candidate_uids[:max_profile_fetches]]
        if to_fetch:
            print(f"[Live Refresh] Fetching {len(to_fetch)} new/shifted deep player profiles...")
            fetched = fetch_live_player_profiles(active_pid, to_fetch)
            cache.update(fetched)
            save_profile_cache(cache)
            print(f"[Live Refresh] Updated profile cache (+{len(fetched)} profiles).")

    results = []
    errors = []
    for sid in target_states:
        try:
            model = build_state_model(sid, cache)
            if refresh_live:
                _ensure_local_xlsx(sid, cache)
            res = sync_single_state_to_drive(sid, model, manifest=manifest)
            results.append(res)
            print(
                f"[Synced] State {sid}: {res['alliances_synced']} alliances, "
                f"{res['members_written']} members -> {res['spreadsheet_id']}"
            )
            time.sleep(0.5)
        except Exception as exc:
            errors.append({"state_id": sid, "error": str(exc)})
            print(f"[Error] State {sid}: {exc}")

    return {
        "ok": len(errors) == 0,
        "synced_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Last Z 16-state bracket sheets (689-704) directly to Google Drive.")
    parser.add_argument("--states", nargs="*", default=["all"], help="State IDs (e.g. 694 702) or 'all' (default: all 689-704)")
    parser.add_argument("--refresh-live", "--live", action="store_true", help="Refresh live alliance rankings and rosters from running game client before syncing")
    parser.add_argument("--refresh-profiles", action="store_true", help="Also refresh deep profiles whose power changed significantly")
    parser.add_argument("--max-profiles", type=int, default=800, help="Max new/changed profiles to query during live refresh")
    parser.add_argument("--pid", type=int, default=None, help="Explicit Last Z process PID for live refresh")
    args = parser.parse_args()

    if not args.states or (len(args.states) == 1 and str(args.states[0]).lower() == "all"):
        state_list = list(ALL_BRACKET_STATES)
    else:
        state_list = [int(s) for s in args.states]

    summary = sync_states(
        states=state_list,
        refresh_live=args.refresh_live,
        refresh_profiles=args.refresh_profiles,
        max_profile_fetches=args.max_profiles,
        pid=args.pid,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
