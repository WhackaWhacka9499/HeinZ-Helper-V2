#!/usr/bin/env python3
"""
Last Z + HeinZ Megamind Query CLI (100% Complete Engine Edition)
Fast, zero-dependency lookup tool across ALL raw Megamind databases in megamind/raw/.

Usage:
  python megamind query.py fts <query> [--layer X] [--domain Y] [--limit 20]   # ~15ms SQLite FTS5 ranked search
  python megamind query.py trace <topic> [--limit 5]                           # ~20ms end-to-end vertical slice
  python megamind query.py icon <query> [--season X] [--category Y] [--limit 25]
  python megamind query.py model <query> [--season X] [--faction Y] [--type all|3d|spine] [--limit 25]
  python megamind query.py map <query> [--category X] [--season Y] [--limit 25]
  python megamind query.py domain [slug]                                       # List or inspect 15 domain cards
  python megamind query.py summary
  python megamind query.py search <query> [--limit 20]
  python megamind query.py packet <query> [--limit 25]
  python megamind query.py manager <query> [--limit 25]
  python megamind query.py callgraph <query> [--limit 25]
  python megamind query.py ui <query> [--limit 25]
  python megamind query.py view <query> [--limit 25]
  python megamind query.py button <query> [--limit 25]
  python megamind query.py goto <query> [--limit 25]
  python megamind query.py table <query> [--limit 25]
  python megamind query.py xml <table_or_query> [row_query] [--limit 25]
  python megamind query.py loc <query> [--limit 25]
  python megamind query.py csharp <query> [--limit 25]
  python megamind query.py proto <query> [--limit 25]
  python megamind query.py http <query> [--limit 25]
  python megamind query.py api <query> [--limit 25]
  python megamind query.py engine <query> [--limit 25]
  python megamind query.py enum <query> [--limit 25]
  python megamind query.py event <query> [--limit 25]
  python megamind query.py heinz <query> [--limit 25]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import sys
import time
from typing import Any

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MEGA_DIR = pathlib.Path(__file__).resolve().parent
RAW_DIR = MEGA_DIR / "raw"
DB_PATH = MEGA_DIR / "megamind index.sqlite"
_CACHE: dict[str, dict[str, Any]] = {}


def _open_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Missing SQLite FTS5 index: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _make_fts_expr(query: str) -> str:
    tokens = [t for t in re.findall(r"[A-Za-z0-9]+", query) if t]
    if not tokens:
        return '""'
    return " AND ".join(f'"{t}"*' for t in tokens)


def cmd_fts(query: str, limit: int, layer: str = "", domain: str = "") -> int:
    t0 = time.perf_counter()
    conn = _open_db()
    expr = _make_fts_expr(query)
    where = ["entities_fts MATCH ?"]
    params: list[Any] = [expr]
    if layer:
        where.append("e.layer = ?")
        params.append(layer)
    if domain:
        where.append("e.domain = ?")
        params.append(domain)
    sql = f"""
        SELECT e.layer, e.domain, e.name, e.summary, e.source_ref, bm25(entities_fts, 10.0, 4.0, 1.0) AS rank
        FROM entities_fts
        JOIN entities e ON e.id = entities_fts.rowid
        WHERE {' AND '.join(where)}
        ORDER BY rank ASC
        LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    # Fallback substring LIKE search if FTS returned 0 (e.g. camelCase middle substring like 'Moment' inside 'GetChatMomentList')
    mode = "FTS5"
    if not rows:
        mode = "LIKE"
        like = f"%{query.lower()}%"
        w2 = ["(lower(name) LIKE ? OR lower(summary) LIKE ? OR lower(body) LIKE ?)"]
        p2: list[Any] = [like, like, like]
        if layer:
            w2.append("layer = ?")
            p2.append(layer)
        if domain:
            w2.append("domain = ?")
            p2.append(domain)
        p2.append(limit)
        rows = conn.execute(
            f"SELECT layer, domain, name, summary, source_ref FROM entities WHERE {' AND '.join(w2)} ORDER BY (lower(name) LIKE ?) DESC, length(name) ASC LIMIT ?",
            p2[:-1] + [like, limit],
        ).fetchall()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    conn.close()

    filt = f" layer={layer}" if layer else ""
    filt += f" domain={domain}" if domain else ""
    print(f"=== {mode} RESULTS for '{query}'{filt}: {len(rows)} hits in {elapsed_ms:.1f} ms ===")
    for r in rows:
        print(f"  [{r['layer']}|{r['domain']}] {r['name']}  ({r['source_ref']})")
        print(f"    {r['summary'][:165]}")
    return 0


def _trace_fetch_layers(
    conn: sqlite3.Connection,
    expr: str,
    like: str,
    layers: tuple[str, ...],
    cap: int,
) -> list[sqlite3.Row]:
    ph = ",".join("?" for _ in layers)
    rows = conn.execute(
        f"""
        SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
        FROM entities_fts
        JOIN entities e ON e.id = entities_fts.rowid
        WHERE entities_fts MATCH ? AND e.layer IN ({ph})
        ORDER BY bm25(entities_fts, 10.0, 4.0, 1.0) ASC
        LIMIT ?
        """,
        [expr, *layers, cap],
    ).fetchall()
    if not rows:
        rows = conn.execute(
            f"""
            SELECT layer, domain, name, summary, source_ref
            FROM entities
            WHERE layer IN ({ph}) AND (lower(name) LIKE ? OR lower(summary) LIKE ?)
            ORDER BY (lower(name) LIKE ?) DESC, length(name) ASC
            LIMIT ?
            """,
            [*layers, like, like, like, cap],
        ).fetchall()
    return rows


def cmd_trace(topic: str, limit: int) -> int:
    t0 = time.perf_counter()
    conn = _open_db()
    expr = _make_fts_expr(topic)
    like = f"%{topic.lower()}%"
    groups = [
        ("1. HeinZ Hub UI & API", ("heinz_task", "heinz_route", "heinz_rpc", "heinz_btn")),
        ("2. HeinZ Bot Engine & Repo Scripts", ("heinz_bot_fn", "repo_script")),
        ("3. Wire Packets, Chat, Protobuf & HTTP", ("packet", "chat_cmd", "proto", "http_api")),
        ("4. DataCenter Managers & Call Graph", ("datacenter", "dc_method")),
        ("5. EventId Bus", ("event",)),
        ("6. Game UI Windows, Handlers, HUD Buttons & GoTo", ("ui_window", "ui_handler", "hud_button", "goto")),
        ("7. Deep Lua Engine & Native C#", ("engine_global", "engine_mod", "csharp")),
        ("8. XML Tables, Rows, Localization & Enums", ("xml_table", "xml_row", "loc_en", "enum")),
        ("9. Extracted Game Icons, 3D Models & World Maps", ("game_icon", "hub_game_icon", "game_model", "hero_skin_spine", "game_map")),
    ]
    per_grp = max(3, min(limit, 8))
    results_by_grp = []
    total_hits = 0
    for title, layers in groups:
        if "hero_skin_spine" in layers:
            icon_cap = max(2, (per_grp + 1) // 2)
            rows = (
                _trace_fetch_layers(conn, expr, like, ("hub_game_icon", "game_icon"), icon_cap)
                + _trace_fetch_layers(conn, expr, like, ("game_model",), per_grp)
                + _trace_fetch_layers(conn, expr, like, ("hero_skin_spine",), per_grp)
                + _trace_fetch_layers(conn, expr, like, ("game_map",), per_grp)
            )
        else:
            rows = _trace_fetch_layers(conn, expr, like, layers, per_grp)
        if rows:
            total_hits += len(rows)
            results_by_grp.append((title, rows))

    # Direct graph edges matching topic
    edges = conn.execute(
        "SELECT DISTINCT src_layer, src_name, relation, dst_layer, dst_name FROM edges WHERE lower(src_name) LIKE ? OR lower(dst_name) LIKE ? LIMIT ?",
        (like, like, max(12, per_grp * 4)),
    ).fetchall()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    conn.close()

    print(f"=== END-TO-END TRACE for '{topic}': {total_hits} entities + {len(edges)} direct edges in {elapsed_ms:.1f} ms ===")
    for title, rows in results_by_grp:
        print(f"\n  -- {title} ({len(rows)}) --")
        for r in rows:
            print(f"    [{r['layer']}] {r['name']} ({r['source_ref']}) :: {r['summary'][:135]}")
    if edges:
        print(f"\n  -- 10. Direct Graph Edges ({len(edges)}) --")
        for e in edges:
            print(f"    {e['src_layer']}:{e['src_name']} --[{e['relation']}]--> {e['dst_layer']}:{e['dst_name']}")
    return 0


def _normalize_season_filter(raw: str) -> str:
    s = raw.strip().lower()
    if s in {"0", "s0", "pre", "pre-season", "preseason", "pre-season 1", "preseason 1"}:
        return "pre-season 1"
    if re.fullmatch(r"s?[1-6]", s):
        return f"season {s[-1]}"
    return s


_CANONICAL_SEASONS = {
    "pre-season 1",
    "season 1",
    "season 2",
    "season 3",
    "season 4",
    "season 5",
    "season 6",
}


def cmd_icon(query: str, limit: int, season: str = "", category: str = "") -> int:
    t0 = time.perf_counter()
    conn = _open_db()
    q_raw = query.strip()
    q_low = q_raw.lower()
    where_filters: list[str] = ["e.layer IN ('game_icon', 'hub_game_icon')"]
    filter_params: list[Any] = []

    if season:
        sn = _normalize_season_filter(season)
        if sn in _CANONICAL_SEASONS:
            where_filters.append("(lower(e.source_ref) LIKE ? OR (e.layer = 'hub_game_icon' AND lower(e.summary) LIKE ?))")
            filter_params.extend([f"assets/icons/{sn}/%", f"%| {sn} |%"])
        else:
            where_filters.append("(lower(e.source_ref) LIKE ? OR lower(e.body) LIKE ?)")
            filter_params.extend([f"%{sn}%", f"%{sn}%"])

    if category:
        cat_low = category.strip().lower()
        where_filters.append("(lower(e.source_ref) LIKE ? OR (e.layer = 'hub_game_icon' AND lower(e.summary) LIKE ?))")
        filter_params.extend([f"assets/icons/%/%{cat_low}%/%", f"%| %{cat_low}% | en=%"])

    mode = "FTS5"
    rows: list[sqlite3.Row] = []
    if q_raw == "*":
        mode = "FILTER"
        sql = f"""
            SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
            FROM entities e
            WHERE {' AND '.join(where_filters)}
            ORDER BY (e.layer = 'hub_game_icon') DESC, (e.name NOT LIKE '% (%)') DESC, e.name ASC
            LIMIT ?
        """
        rows = conn.execute(sql, [*filter_params, limit]).fetchall()
    else:
        expr = _make_fts_expr(q_raw)
        if expr != '""':
            sql = f"""
                SELECT e.layer, e.domain, e.name, e.summary, e.source_ref,
                       bm25(entities_fts, 10.0, 4.0, 1.0) AS rank
                FROM entities_fts
                JOIN entities e ON e.id = entities_fts.rowid
                WHERE entities_fts MATCH ? AND {' AND '.join(where_filters)}
                ORDER BY
                    (lower(e.name) = ?) DESC,
                    (lower(e.summary) LIKE ? OR lower(e.summary) LIKE ?) DESC,
                    (e.layer = 'hub_game_icon') DESC,
                    (e.name NOT LIKE '% (%)') DESC,
                    rank ASC
                LIMIT ?
            """
            rows = conn.execute(
                sql,
                [expr, *filter_params, q_low, f"%| sprite={q_low} |%", f"%| key={q_low} |%", limit],
            ).fetchall()

        if not rows:
            mode = "LIKE"
            like = f"%{q_low}%"
            sql_like = f"""
                SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
                FROM entities e
                WHERE {' AND '.join(where_filters)}
                  AND (lower(e.name) LIKE ? OR lower(e.summary) LIKE ? OR lower(e.body) LIKE ?)
                ORDER BY
                    (lower(e.name) = ?) DESC,
                    (lower(e.summary) LIKE ? OR lower(e.summary) LIKE ?) DESC,
                    (e.layer = 'hub_game_icon') DESC,
                    (lower(e.name) LIKE ?) DESC,
                    length(e.name) ASC
                LIMIT ?
            """
            rows = conn.execute(
                sql_like,
                [*filter_params, like, like, like, q_low, f"%| sprite={q_low} |%", f"%| key={q_low} |%", like, limit],
            ).fetchall()

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    conn.close()

    filt = f" season='{season}'" if season else ""
    filt += f" category='{category}'" if category else ""
    print(f"=== ICON {mode} RESULTS for '{query}'{filt}: {len(rows)} hits in {elapsed_ms:.1f} ms ===")
    for r in rows:
        print(f"  [{r['layer']}|{r['domain']}] {r['name']}  ({r['source_ref']})")
        print(f"    {r['summary'][:165]}")
    return 0


def cmd_model(query: str, limit: int, season: str = "", faction: str = "", asset_type: str = "") -> int:
    t0 = time.perf_counter()
    conn = _open_db()
    q_raw = query.strip()
    q_low = q_raw.lower()
    t_low = asset_type.strip().lower()
    where_filters: list[str] = []
    filter_params: list[Any] = []

    if t_low in ("", "all"):
        where_filters.append("e.layer IN ('game_model', 'hero_skin_spine')")
    elif t_low in ("3d", "game_model", "model", "models"):
        where_filters.append("e.layer = 'game_model'")
    elif t_low in ("spine", "2d", "hero_skin_spine", "skin", "skins"):
        where_filters.append("e.layer = 'hero_skin_spine'")
    elif t_low in ("hq", "hq_skins"):
        where_filters.append("e.layer = 'game_model' AND lower(e.source_ref) LIKE 'models/%/hq skins/%'")
    elif t_low in ("vehicle", "vehicle_skins"):
        where_filters.append("e.layer = 'game_model' AND lower(e.source_ref) LIKE 'models/%/vehicle skins/%'")
    else:
        conn.close()
        raise ValueError(f"Unsupported --type '{asset_type}'. Choose from: all, 3d, spine, hq, vehicle.")

    if season:
        sn = _normalize_season_filter(season)
        if sn in _CANONICAL_SEASONS:
            where_filters.append("lower(e.source_ref) LIKE ?")
            filter_params.append(f"models/{sn}/%")
        else:
            where_filters.append("(lower(e.source_ref) LIKE ? OR lower(e.body) LIKE ?)")
            filter_params.extend([f"%{sn}%", f"%{sn}%"])

    if faction:
        fac_low = faction.strip().lower()
        where_filters.append("lower(e.source_ref) LIKE ? AND lower(e.summary) LIKE ?")
        filter_params.extend([f"models/%/%{fac_low}%/%/%", f"% | %{fac_low}% |%"])

    mode = "FTS5"
    rows: list[sqlite3.Row] = []
    if q_raw == "*":
        mode = "FILTER"
        sql = f"""
            SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
            FROM entities e
            WHERE {' AND '.join(where_filters)}
            ORDER BY (e.layer = 'game_model') DESC, e.name ASC
            LIMIT ?
        """
        rows = conn.execute(sql, [*filter_params, limit]).fetchall()
    else:
        expr = _make_fts_expr(q_raw)
        if expr != '""':
            sql = f"""
                SELECT e.layer, e.domain, e.name, e.summary, e.source_ref,
                       bm25(entities_fts, 10.0, 4.0, 1.0) AS rank
                FROM entities_fts
                JOIN entities e ON e.id = entities_fts.rowid
                WHERE entities_fts MATCH ? AND {' AND '.join(where_filters)}
                ORDER BY
                    (lower(e.name) = ?) DESC,
                    (lower(e.summary) LIKE ? OR lower(e.summary) LIKE ? OR lower(e.summary) LIKE ?) DESC,
                    (lower(e.name) LIKE ?) DESC,
                    (e.layer = 'game_model') DESC,
                    rank ASC
                LIMIT ?
            """
            rows = conn.execute(
                sql,
                [
                    expr,
                    *filter_params,
                    q_low,
                    f"%| slug={q_low} |%",
                    f"%| skin={q_low} |%",
                    f"%| hero={q_low} |%",
                    f"% - {q_low}",
                    limit,
                ],
            ).fetchall()

        if not rows:
            mode = "LIKE"
            like = f"%{q_low}%"
            sql_like = f"""
                SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
                FROM entities e
                WHERE {' AND '.join(where_filters)}
                  AND (lower(e.name) LIKE ? OR lower(e.summary) LIKE ? OR lower(e.body) LIKE ?)
                ORDER BY
                    (lower(e.name) = ?) DESC,
                    (lower(e.summary) LIKE ? OR lower(e.summary) LIKE ? OR lower(e.summary) LIKE ?) DESC,
                    (lower(e.name) LIKE ?) DESC,
                    (lower(e.name) LIKE ?) DESC,
                    (e.layer = 'game_model') DESC,
                    length(e.name) ASC
                LIMIT ?
            """
            rows = conn.execute(
                sql_like,
                [
                    *filter_params,
                    like,
                    like,
                    like,
                    q_low,
                    f"%| slug={q_low} |%",
                    f"%| skin={q_low} |%",
                    f"%| hero={q_low} |%",
                    f"% - {q_low}",
                    like,
                    limit,
                ],
            ).fetchall()

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    conn.close()

    filt = f" season='{season}'" if season else ""
    filt += f" faction='{faction}'" if faction else ""
    filt += f" type='{asset_type}'" if asset_type else ""
    print(f"=== MODEL/SKIN {mode} RESULTS for '{query}'{filt}: {len(rows)} hits in {elapsed_ms:.1f} ms ===")
    for r in rows:
        print(f"  [{r['layer']}|{r['domain']}] {r['name']}  ({r['source_ref']})")
        print(f"    {r['summary'][:165]}")
    return 0


def _make_map_fts_expr(query: str) -> str:
    # Keep "Season <digit>" as an FTS5 phrase so short digits don't match 600px/500px dimensions.
    tokens = [t for t in re.findall(r"[A-Za-z0-9]+", query) if t]
    if not tokens:
        return '""'
    parts: list[str] = []
    i = 0
    while i < len(tokens):
        if (
            i + 1 < len(tokens)
            and tokens[i].lower() == "season"
            and re.fullmatch(r"[1-6]", tokens[i + 1])
        ):
            parts.append(f'"{tokens[i]} {tokens[i + 1]}"')
            i += 2
        else:
            parts.append(f'"{tokens[i]}"*')
            i += 1
    return " AND ".join(parts)


def cmd_map(query: str, limit: int, category: str = "", season: str = "") -> int:
    t0 = time.perf_counter()
    conn = _open_db()
    q_raw = query.strip()
    q_low = q_raw.lower()
    where_filters: list[str] = ["e.layer = 'game_map'"]
    filter_params: list[Any] = []

    if category:
        cat_low = category.strip().lower()
        where_filters.append("(lower(e.source_ref) LIKE ? OR lower(e.summary) LIKE ? OR lower(e.summary) LIKE ?)")
        filter_params.extend([f"maps/{cat_low}%", f"% | %{cat_low}% / %", f"% / %{cat_low}% |%"])

    if season:
        sn = _normalize_season_filter(season)
        if sn == "all":
            sn = "all seasons"
        where_filters.append("lower(substr(e.summary, 1, instr(e.summary, '|'))) LIKE ?")
        filter_params.append(f"%{sn}%")

    mode = "FTS5"
    rows: list[sqlite3.Row] = []
    if q_raw == "*":
        mode = "FILTER"
        sql = f"""
            SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
            FROM entities e
            WHERE {' AND '.join(where_filters)}
            ORDER BY
                (lower(e.source_ref) NOT LIKE 'maps/main world maps/province zones/%') DESC,
                (lower(e.source_ref) NOT LIKE 'maps/terrain and biomes/%') DESC,
                (lower(e.summary) LIKE '%stitched%' OR lower(e.summary) LIKE '%decoded%' OR lower(e.summary) LIKE '%annotated%') DESC,
                e.name ASC
            LIMIT ?
        """
        rows = conn.execute(sql, [*filter_params, limit]).fetchall()
    else:
        expr = _make_map_fts_expr(q_raw)
        if expr != '""':
            sql = f"""
                SELECT e.layer, e.domain, e.name, e.summary, e.source_ref,
                       bm25(entities_fts, 10.0, 4.0, 1.0) AS rank
                FROM entities_fts
                JOIN entities e ON e.id = entities_fts.rowid
                WHERE entities_fts MATCH ? AND {' AND '.join(where_filters)}
                ORDER BY
                    (lower(e.name) = ?) DESC,
                    (lower(e.name) LIKE ?) DESC,
                    (lower(e.source_ref) NOT LIKE 'maps/main world maps/province zones/%') DESC,
                    (lower(e.source_ref) NOT LIKE 'maps/terrain and biomes/%') DESC,
                    (lower(e.summary) LIKE '%stitched%' OR lower(e.summary) LIKE '%decoded%' OR lower(e.summary) LIKE '%annotated%') DESC,
                    rank ASC
                LIMIT ?
            """
            rows = conn.execute(
                sql,
                [expr, *filter_params, q_low, f"%{q_low}%", limit],
            ).fetchall()

        if not rows:
            mode = "LIKE"
            like = f"%{q_low}%"
            sql_like = f"""
                SELECT e.layer, e.domain, e.name, e.summary, e.source_ref
                FROM entities e
                WHERE {' AND '.join(where_filters)}
                  AND (lower(e.name) LIKE ? OR lower(e.summary) LIKE ? OR lower(e.body) LIKE ?)
                ORDER BY
                    (lower(e.name) = ?) DESC,
                    (lower(e.name) LIKE ?) DESC,
                    (lower(e.source_ref) NOT LIKE 'maps/main world maps/province zones/%') DESC,
                    (lower(e.source_ref) NOT LIKE 'maps/terrain and biomes/%') DESC,
                    (lower(e.summary) LIKE '%stitched%' OR lower(e.summary) LIKE '%decoded%' OR lower(e.summary) LIKE '%annotated%') DESC,
                    length(e.name) ASC
                LIMIT ?
            """
            rows = conn.execute(
                sql_like,
                [*filter_params, like, like, like, q_low, like, limit],
            ).fetchall()

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    conn.close()

    filt = f" category='{category}'" if category else ""
    filt += f" season='{season}'" if season else ""
    print(f"=== MAP {mode} RESULTS for '{query}'{filt}: {len(rows)} hits in {elapsed_ms:.1f} ms ===")
    for r in rows:
        print(f"  [{r['layer']}|{r['domain']}] {r['name']}  ({r['source_ref']})")
        print(f"    {r['summary'][:165]}")
    return 0


def cmd_domain(slug: str) -> int:
    conn = _open_db()
    if not slug:
        rows = conn.execute(
            "SELECT domain, COUNT(*) AS cnt FROM entities GROUP BY domain ORDER BY cnt DESC"
        ).fetchall()
        conn.close()
        print("=== MEGAMIND CATEGORIZED DOMAINS (megamind/domains/<slug>.md) ===")
        for r in rows:
            card = MEGA_DIR / "domains" / f"{r['domain']}.md"
            card_str = f"domains/{r['domain']}.md ({card.stat().st_size/1024:.1f} KB)" if card.exists() else "(core index)"
            print(f"  {r['domain']:26s} | {r['cnt']:6,} entities | {card_str}")
        return 0
    rows = conn.execute(
        "SELECT layer, COUNT(*) AS cnt FROM entities WHERE domain = ? GROUP BY layer ORDER BY cnt DESC",
        (slug,),
    ).fetchall()
    conn.close()
    if not rows:
        print(f"Unknown domain '{slug}'. Run `python megamind/megamind query.py domain` to list all domains.")
        return 1
    card = MEGA_DIR / "domains" / f"{slug}.md"
    print(f"=== DOMAIN `{slug}` | Card: {card} ({'EXISTS' if card.exists() else 'none'}) ===")
    for r in rows:
        print(f"  {r['layer']:16s}: {r['cnt']:,}")
    print(f"Tip: Read {card} or run `python megamind/megamind query.py fts <query> --domain {slug}`")
    return 0


def load_db(name: str) -> dict[str, Any]:
    if name not in _CACHE:
        p = RAW_DIR / name
        if not p.exists():
            raise FileNotFoundError(f"Missing Megamind raw database: {p}")
        _CACHE[name] = json.loads(p.read_text(encoding="utf-8"))
    return _CACHE[name]


def _loc_map() -> dict[str, str]:
    try:
        return load_db("localization en.json").get("strings") or {}
    except FileNotFoundError:
        return {}


def cmd_summary() -> int:
    pk = load_db("packets complete.json")
    dc = load_db("datacenter managers.json")
    cg = load_db("datacenter callgraph and protocols.json")
    ui = load_db("ui windows and buttons.json")
    ua = load_db("ui complete all windows.json")
    xm = load_db("xml tables manifest.json")
    cs = load_db("csharp and http endpoints.json")
    en = load_db("enums complete.json")
    hz = load_db("heinz architecture.json")

    ps = pk.get("summary", {})
    ms = dc.get("stats", {})
    cgs = cg.get("summary", {})
    us = ui.get("summary", {})
    uas = ua.get("summary", {})
    xs = xm.get("summary", {})
    css = cs.get("summary", {})
    hb = hz.get("hub_backend", {})
    hf = hz.get("hub_frontend", {})
    br = hz.get("bot_and_repo", {})

    print("=== LAST Z + HEINZ MEGAMIND SUMMARY (100% ENGINE EDITION) ===")
    print(f"Packets    : {ps.get('total_msg_defines', 0):,} MsgDefines | {ps.get('total_chat_msg_defines', 0):,} ChatMsgDefines | {ps.get('total_inspected_packets', 0):,}/{ps.get('total_mapped_packets', 0):,} wire cmds | {cgs.get('web_message_modules', 0)} WebMsgs | {cgs.get('mail_protocol_modules', 0)} MailV4")
    print(f"Proto/HTTP : {css.get('protobuf_types_count', 0):,} Protobuf schemas | {css.get('http_urls_count', 0):,} HTTP/HTTPS/CDN URLs")
    print(f"Event Bus  : {ps.get('total_event_ids', 0):,} EventIds | {us.get('active_event_listeners_count', 0):,} live EventManager subscriptions")
    print(f"Managers   : {ms.get('dc_count', 0):,} DataCenter + {ms.get('slg_dc_count', 0):,} SlgDC + {len(dc.get('globals_singletons', {}))} singletons | {cgs.get('methods_scanned', 0):,} methods scanned ({cgs.get('methods_with_links', 0):,} call-graph linked)")
    print(f"Game UI    : {us.get('total_ui_window_names', 0):,} UIWindowNames | {uas.get('total_windows_extracted', 0):,} full configs ({uas.get('total_prefab_paths', 0):,} prefabs, {uas.get('total_ui_action_handlers', 0):,} handlers, {uas.get('total_ui_button_refs', 0):,} btn refs) | {us.get('live_buttons_count', 0):,} HUD coords | {css.get('goto_util_methods_count', 0)} GoToUtil")
    print(f"XML + Loc  : {xs.get('total_xml_tables_dumped', 0):,} XML tables ({xs.get('total_rows_dumped', 0):,} rows - ZERO truncation) | {xs.get('total_lua_datatables_dumped', 0):,} LuaDatatables | {xs.get('localization_strings_count', 0):,} EN strings")
    print(f"Native C#  : {css.get('total_loaded_csharp_assemblies', 0):,} assemblies | {css.get('total_types_reflected', 0):,} classes ({css.get('total_methods_reflected', 0):,} methods, {css.get('total_fields_reflected', 0):,} fields)")
    try:
        de_s = load_db("deep engine scene pve world.json").get("summary", {})
        print(f"Deep Engine: {de_s.get('total_lua_package_loaded', 0):,} Lua modules | {de_s.get('global_engine_classes_count', 0):,} global classes ({de_s.get('global_engine_methods_count', 0):,} methods) | {de_s.get('deep_engine_modules_count', 0):,} PVE/Scene/World/Chat/RedDot mods ({de_s.get('deep_engine_methods_count', 0):,} methods) | {de_s.get('loaded_native_dlls_count', 0)} native DLLs")
    except FileNotFoundError:
        pass
    print(f"Enums      : {en.get('count', len(en.get('enums', {}))):,} global Lua enum tables")
    print(f"HeinZ Hub  : {len(hb.get('public_rpc_methods', []))} RPCs | {len(hb.get('action_routes', []))} action_ids | {len(hb.get('task_catalog', []))} cards | {len(hf.get('buttons', []))} Hub buttons | {len(hf.get('js_functions', []))} JS fns")
    print(f"Bot Engine : {len(br.get('stage_definitions', []))} stages ({len(br.get('stage_task_order', []))} tasks) | {len(br.get('bot_actions_functions', []))} bot actions | {len(br.get('repo_files', []))} repo files")
    try:
        ga_doc = load_db("game assets icons and models.json")
        ga = ga_doc.get("summary", {})
        mc = (ga_doc.get("maps") or {}).get("counts_by_category") or {}
        print(
            f"Game Assets: {ga.get('total_game_icons', 0):,} PNG icons ({ga.get('icons_english_named', 0):,} EN, {ga.get('icons_sprite_cleaned', 0):,} cleaned) | "
            f"{ga.get('total_game_models', 0):,} 3D models | {ga.get('hero_skins_2d_spine_count', 0):,} 2D Spine hero skins "
            f"({ga.get('models_hq_skins_count', 0)} HQ skins, {ga.get('models_vehicle_skins_count', 0)} vehicle skins, "
            f"{ga.get('models_total_glbs', 0):,} GLBs, {ga.get('models_total_objs', 0):,} OBJs, {ga.get('models_total_textures', 0):,} tex) | "
            f"{ga.get('hub_sprites_total_webp', 0):,} Hub WebPs ({ga.get('hub_core_sprites', 0)} core, {ga.get('hub_hero_portrait_sprites', 0)} heroes, {ga.get('hub_item_sprites', 0)} items)"
        )
        print(
            f"World Maps : {ga.get('total_game_maps', 0):,} exported maps "
            f"({(mc.get('Main World Maps') or {}).get('count', 0)} Main World, "
            f"{(mc.get('Seasonal Maps') or {}).get('count', 0)} Seasonal, "
            f"{(mc.get('Event Maps') or {}).get('count', 0)} Event, "
            f"{(mc.get('City and Base Maps') or {}).get('count', 0)} City/Base, "
            f"{(mc.get('Terrain and Biomes') or {}).get('count', 0)} Terrain | "
            f"{ga.get('maps_stitched_4k_count', 0)}x 4K stitched, "
            f"{ga.get('maps_decoded_topology_count', 0)} decoded topology, "
            f"{ga.get('maps_province_zones_count', 0)} provinces)"
        )
    except FileNotFoundError:
        pass
    if DB_PATH.exists():
        conn = _open_db()
        try:
            ent_cnt = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            edge_cnt = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
            print(f"SQLite FTS5: {ent_cnt:,} indexed entities | {edge_cnt:,} graph edges ({DB_PATH.stat().st_size / (1024 * 1024):.2f} MB)")
        finally:
            conn.close()
    return 0


def cmd_packet(query: str, limit: int) -> int:
    q = query.lower()
    pk = load_db("packets complete.json")
    hits = []
    for cmd, info in sorted((pk.get("packets") or {}).items()):
        out = info.get("outgoing") or {}
        inc = info.get("incoming") or {}
        hay = " ".join([
            cmd, " ".join(info.get("aliases") or []), info.get("module_path", ""),
            " ".join(out.get("tokens") or []), " ".join(inc.get("datacenter_targets") or []),
            " ".join(inc.get("event_broadcasts") or []), " ".join(inc.get("ui_targets") or []),
        ]).lower()
        if q in hay:
            hits.append((cmd, info))
    chat_hits = [(k, v) for k, v in sorted((pk.get("chat_msg_defines") or {}).items()) if q in k.lower() or q in str(v).lower()]
    print(f"=== PACKET MATCHES for '{query}': {len(hits)} wire packets, {len(chat_hits)} ChatMsgDefines ===")
    for cmd, info in hits[:limit]:
        out = info.get("outgoing") or {}
        inc = info.get("incoming") or {}
        print(f"  [{cmd}] aliases={info.get('aliases')} src={info.get('source')} mod={info.get('module_path')}")
        print(f"    OUT: nparams={out.get('nparams', 0)} puts={out.get('sfs_puts', [])} tokens={out.get('tokens', [])[:14]}")
        print(f"    IN : DC={inc.get('datacenter_targets', [])} Events={inc.get('event_broadcasts', [])} UI={inc.get('ui_targets', [])[:6]}")
    for ck, cv in chat_hits[:10]:
        print(f"  [ChatMsgDefines.{ck}] = '{cv}'")
    return 0


def cmd_manager(query: str, limit: int) -> int:
    q = query.lower()
    dc = load_db("datacenter managers.json")
    hits = []
    for scope, mapping in [("DataCenter", dc.get("datacenter") or {}), ("SlgDataCenter", dc.get("slg_datacenter") or {}), ("_G", dc.get("globals_singletons") or {})]:
        for name, info in sorted(mapping.items()):
            meths = info.get("methods") or []
            flds = info.get("fields") if isinstance(info.get("fields"), dict) else {}
            mm = [f"{m['name']}({m.get('nparams', 0)})" for m in meths if q in m["name"].lower()]
            mf = [k for k in flds if q in k.lower()]
            if q in name.lower() or mm or mf:
                hits.append((f"{scope}.{name}", info, mm, mf))
    print(f"=== MANAGER / SINGLETON MATCHES for '{query}': {len(hits)} ===")
    for full, info, mm, mf in hits[:limit]:
        meths = info.get("methods") or []
        flds = info.get("fields") if isinstance(info.get("fields"), dict) else {}
        print(f"  [{full}] fields={len(flds)} methods={len(meths)} src={info.get('source', '')}")
        if mf:
            print(f"    Matched fields : {mf[:15]}")
        if mm:
            print(f"    Matched methods: {mm[:20]}")
        elif q in full.lower():
            print(f"    Sample methods : {[m['name'] + '(' + str(m.get('nparams', 0)) + ')' for m in meths[:18]]}")
    return 0


def cmd_callgraph(query: str, limit: int) -> int:
    q = query.lower()
    cg = load_db("datacenter callgraph and protocols.json").get("callgraphs") or {}
    hits = []
    for mgr, minfo in sorted(cg.items()):
        s = minfo.get("summary") or {}
        meths = minfo.get("methods") or {}
        if q in mgr.lower() or q in json.dumps(s).lower():
            hits.append((mgr, minfo, None))
            continue
        for mname, mlinks in sorted(meths.items()):
            if q in mname.lower() or q in json.dumps(mlinks).lower():
                hits.append((f"{mgr}.{mname}", minfo, mlinks))
    print(f"=== CALLGRAPH MATCHES for '{query}': {len(hits)} ===")
    for label, minfo, mlinks in hits[:limit]:
        if mlinks is None:
            s = minfo.get("summary") or {}
            print(f"  [{label}] linked={minfo.get('linked_methods_count')}/{minfo.get('total_methods')}")
            if s.get("msgs"): print(f"    MSGs   : {s['msgs'][:12]}")
            if s.get("events"): print(f"    Events : {s['events'][:12]}")
            if s.get("uis"): print(f"    UIs    : {s['uis'][:12]}")
            if s.get("tables"): print(f"    Tables : {s['tables'][:12]}")
            if s.get("dcs"): print(f"    DCs    : {s['dcs'][:12]}")
        else:
            print(f"  [{label}] msgs={mlinks.get('msgs', [])} events={mlinks.get('events', [])} uis={mlinks.get('uis', [])} tables={mlinks.get('tables', [])} dcs={mlinks.get('dcs', [])}")
    return 0


def cmd_ui(query: str, limit: int) -> int:
    q = query.lower()
    ui = load_db("ui windows and buttons.json")
    w_names = ui.get("ui_window_names") or {}
    u_cfg = ui.get("ui_config") or {}
    u_cfg_slg = ui.get("ui_config_slg") or {}
    win_hits = [
        (k, v, (u_cfg.get(v) or u_cfg.get(k) or u_cfg_slg.get(v) or {}).get("config_module", ""))
        for k, v in sorted(w_names.items()) if q in k.lower() or q in str(v).lower()
    ]
    print(f"=== UI WINDOW NAME MATCHES for '{query}': {len(win_hits)} ===")
    for k, v, cfg in win_hits[:limit]:
        print(f"  [Window] UIWindowNames.{k} = '{v}' | config={cfg or '-'}")
    return 0


def cmd_view(query: str, limit: int) -> int:
    q = query.lower()
    wins = load_db("ui complete all windows.json").get("windows") or {}
    hits = []
    for wname, winfo in sorted(wins.items()):
        hay = json.dumps({
            "w": wname,
            "prefab": winfo.get("prefab_path", ""),
            "layer": winfo.get("layer", ""),
            "v_btns": (winfo.get("view") or {}).get("button_refs") if isinstance(winfo.get("view"), dict) else [],
            "c_btns": (winfo.get("ctrl") or {}).get("button_refs") if isinstance(winfo.get("ctrl"), dict) else [],
            "v_h": list(((winfo.get("view") or {}).get("handlers") or {}).keys()) if isinstance(winfo.get("view"), dict) else [],
            "c_h": list(((winfo.get("ctrl") or {}).get("handlers") or {}).keys()) if isinstance(winfo.get("ctrl"), dict) else [],
        }).lower()
        if q in hay:
            hits.append((wname, winfo))
    print(f"=== DEEP UI VIEW/PREFAB MATCHES for '{query}': {len(hits)} / {len(wins)} windows ===")
    for wname, winfo in hits[:limit]:
        v = winfo.get("view") if isinstance(winfo.get("view"), dict) else {}
        c = winfo.get("ctrl") if isinstance(winfo.get("ctrl"), dict) else {}
        brefs = sorted(set((v.get("button_refs") or []) + (c.get("button_refs") or [])))
        vh = v.get("handlers") or {}
        ch = c.get("handlers") or {}
        print(f"  [{wname}] layer={winfo.get('layer')} prefab={winfo.get('prefab_path')}")
        if brefs: print(f"    Buttons ({len(brefs)}): {brefs[:15]}")
        for hname, hinfo in list(sorted({**vh, **ch}.items()))[:8]:
            print(f"    Handler {hname}(p={hinfo.get('nparams',0)}) -> opens={hinfo.get('opens',[])} msgs={hinfo.get('msgs',[])} dcs={hinfo.get('dcs',[])}")
    return 0


def cmd_button(query: str, limit: int) -> int:
    q = query.lower()
    ui = load_db("ui windows and buttons.json")
    hz = load_db("heinz architecture.json")
    game_btns = [
        b for b in ((ui.get("live_unity_ui") or {}).get("buttons") or [])
        if q in str(b.get("name", "")).lower() or q in str(b.get("label", "")).lower() or q in str(b.get("path", "")).lower() or q in str((b.get("rect") or {}).get("quadrant", "")).lower()
    ]
    hub_btns = [
        b for b in ((hz.get("hub_frontend") or {}).get("buttons") or [])
        if q in str(b.get("id", "")).lower() or q in str(b.get("label", "")).lower() or q in str(b.get("onclick", "")).lower() or q in str(b.get("section", "")).lower()
    ]
    print(f"=== BUTTON MATCHES for '{query}': {len(game_btns)} Live HUD buttons, {len(hub_btns)} HeinZ Hub buttons ===")
    for b in game_btns[:limit]:
        r = b.get("rect") or {}
        st = "ACTIVE" if b.get("active") else "cached"
        print(f"  [Game {st}] {b.get('name')} | label='{b.get('label', '')}' | {r.get('quadrant')} ({r.get('x_pct')}%, {r.get('y_pct')}%) px=({r.get('x_px')},{r.get('y_px')},{r.get('w_px')}x{r.get('h_px')}) | {b.get('path')}")
    for b in hub_btns[:limit]:
        print(f"  [HeinZ UI] section={b.get('section')} id='{b.get('id')}' label='{b.get('label')}' onclick={b.get('onclick')}")
    return 0


def cmd_goto(query: str, limit: int) -> int:
    q = query.lower()
    gu = (load_db("csharp and http endpoints.json").get("goto_util") or {})
    hits = []
    for mod, mmap in sorted(gu.items()):
        for mname, minfo in sorted((mmap or {}).items()):
            if q in mname.lower() or q in json.dumps(minfo).lower():
                hits.append((f"{mod}.{mname}", minfo))
    print(f"=== GOTO / WEB UTIL MATCHES for '{query}': {len(hits)} ===")
    for full, info in hits[:limit]:
        print(f"  [{full}(p={info.get('nparams', 0)})] uis={info.get('uis', [])} builds={info.get('building_types', [])} dcs={info.get('dcs', [])} msgs={info.get('msgs', [])}")
    return 0


def cmd_table(query: str, limit: int) -> int:
    q = query.lower()
    tb = load_db("game tables and stats.json")
    schemas = tb.get("table_schemas") or {}
    cats = tb.get("catalogs") or {}
    sch_hits = [(k, v) for k, v in sorted(schemas.items()) if q in k.lower() or q in str(v.get("xml", "")).lower() or any(q in c["name"].lower() for c in (v.get("columns") or []))]
    row_hits = []
    for cname, rows in sorted(cats.items()):
        for r in rows:
            if q in json.dumps(r, ensure_ascii=False).lower() or q in cname.lower():
                row_hits.append((cname, r))
                if len(row_hits) >= limit * 4:
                    break
    print(f"=== XML SCHEMA/CATALOG MATCHES for '{query}': {len(sch_hits)} schemas, {len(row_hits)}+ catalog rows ===")
    for k, v in sch_hits[:limit]:
        cols = [c["name"] for c in (v.get("columns") or [])[:12]]
        print(f"  [Schema] {k} ({v.get('xml')}) rows={v.get('row_count', 0):,} loaded={v.get('loaded')} cols={cols}")
    for cname, r in row_hits[:limit]:
        nm = r.get("name_en") or r.get("title_en") or r.get("name") or ""
        desc = r.get("desc_en") or r.get("description_en") or r.get("des_en") or ""
        print(f"  [{cname} #{r.get('_id')}] {nm} | {desc[:90]}")
    return 0


def cmd_xml(table_query: str, row_query: str, limit: int) -> int:
    tq = table_query.lower()
    rq = row_query.lower().strip()
    xm = load_db("xml tables manifest.json").get("xml_tables") or {}
    loc = _loc_map()

    matched_tables = [
        (xml, info) for xml, info in sorted(xm.items())
        if tq == xml.lower() or tq in xml.lower() or any(tq in tk.lower() for tk in (info.get("table_keys") or []))
    ]
    if not matched_tables:
        print(f"No dumped XML table matching '{table_query}'.")
        return 0
    if len(matched_tables) > 1 and not any(xml.lower() == tq for xml, _ in matched_tables) and not rq:
        print(f"=== MATCHING FULL XML TABLES ({len(matched_tables)}) ===")
        for xml, info in matched_tables[:limit]:
            print(f"  [{xml}] aliases={info.get('table_keys')} rows={info.get('row_count', 0):,} cols={info.get('columns', [])[:10]}")
        return 0

    xml, info = next(((x, i) for x, i in matched_tables if x.lower() == tq), matched_tables[0])
    data = json.loads((RAW_DIR / info["file"]).read_text(encoding="utf-8"))
    cols = data.get("columns") or []
    rows = data.get("rows") or {}
    print(f"=== FULL XML TABLE `{xml}` ({len(rows):,} rows, cols={cols}) ===")
    shown = 0
    for rid, arr in rows.items():
        # Resolve any cell whose value is in loc dictionary for matching/display
        resolved = [f"{v} ({loc[v][:45]})" if v in loc else v for v in arr]
        hay = (rid + " " + " ".join(resolved)).lower()
        if not rq or rq in hay:
            pairs = [f"{cols[i]}={resolved[i]}" for i in range(min(len(cols), len(resolved))) if resolved[i] != ""]
            print(f"  [#{rid}] " + " | ".join(pairs[:10]))
            shown += 1
            if shown >= limit:
                break
    if shown == 0:
        print(f"  (No rows matched '{row_query}' in `{xml}`.)")
    return 0


def cmd_loc(query: str, limit: int) -> int:
    q = query.lower()
    loc = _loc_map()
    hits = [(k, v) for k, v in sorted(loc.items()) if q in k.lower() or q in v.lower()]
    print(f"=== LOCALIZATION MATCHES for '{query}': {len(hits)} / {len(loc):,} EN strings ===")
    for k, v in hits[:limit]:
        print(f"  [{k}] {v}")
    return 0


def cmd_csharp(query: str, limit: int) -> int:
    q = query.lower()
    ct = (load_db("csharp and http endpoints.json").get("csharp_reflected_types") or {})
    hits = []
    for asm, tmap in ct.items():
        for full, tinfo in sorted((tmap or {}).items()):
            ms = [m for m in (tinfo.get("methods") or []) if q in m.lower()]
            fs = [f for f in (tinfo.get("fields") or []) if q in f.lower()]
            if q in full.lower() or ms or fs:
                hits.append((asm, full, tinfo, ms, fs))
    print(f"=== NATIVE C# MATCHES for '{query}': {len(hits)} types ===")
    for asm, full, tinfo, ms, fs in hits[:limit]:
        print(f"  [{asm}] {tinfo.get('kind')} {full} : {tinfo.get('base')} (methods={len(tinfo.get('methods', []))}, fields={len(tinfo.get('fields', []))})")
        if ms: print(f"    Matched methods: {ms[:12]}")
        elif q in full.lower(): print(f"    Sample methods : {(tinfo.get('methods') or [])[:12]}")
        if fs: print(f"    Matched fields : {fs[:10]}")
    return 0


def cmd_proto(query: str, limit: int) -> int:
    q = query.lower()
    protos = (load_db("csharp and http endpoints.json").get("protobuf_types") or {})
    hits = [(k, v) for k, v in sorted(protos.items()) if q in k.lower() or q in json.dumps(v).lower()]
    print(f"=== PROTOBUF MATCHES for '{query}': {len(hits)} / {len(protos)} types ===")
    for pname, pinfo in hits[:limit]:
        if not isinstance(pinfo, dict):
            print(f"  [{pname}] {pinfo}")
            continue
        flds = [f"#{f['number']} {f['name']}:{f['ftype']}" for f in (pinfo.get("fields") or [])[:18] if isinstance(f, dict)]
        print(f"  [{pinfo.get('kind')}] {pname} -> {', '.join(flds)}")
    return 0


def cmd_http(query: str, limit: int) -> int:
    q = query.lower()
    cs = load_db("csharp and http endpoints.json")
    cg = load_db("datacenter callgraph and protocols.json")
    urls = [u for u in (cs.get("http_urls") or []) if q in str(u.get("url", "")).lower() or q in str(u.get("source", "")).lower()]
    wms = [(k, v) for k, v in sorted((cg.get("chat_web_messages") or {}).items()) if q in k.lower() or q in json.dumps(v).lower()]
    mps = [(k, v) for k, v in sorted((cg.get("mail_v4_protocol") or {}).items()) if q in k.lower() or q in json.dumps(v).lower()]
    print(f"=== HTTP / WEBSOCKET / MAIL-V4 MATCHES for '{query}': {len(urls)} URLs, {len(wms)} WebMessages, {len(mps)} MailV4 ===")
    for u in urls[:limit]:
        print(f"  [URL] {u['url']}  <-  {u['source']}")
    for k, v in wms[:limit]:
        print(f"  [WebMessage] {k} -> methods={list(v.keys())[:10]}")
    for k, v in mps[:limit]:
        print(f"  [MailV4] {k} -> methods={list(v.keys())[:10]}")
    return 0


def cmd_api(query: str, limit: int) -> int:
    q = query.lower()
    ap = load_db("apis and integrations complete.json")
    ga = ap.get("game_apis") or {}
    g_eps = [x for x in (ga.get("api_paths_and_urls") or []) if q in str(x).lower()]
    g_load = [(k, v) for k, v in sorted((ga.get("loading_modules") or {}).items()) if q in k.lower() or q in json.dumps(v).lower()]
    g_net = [(k, v) for k, v in sorted((ga.get("network_assistant") or {}).items()) if q in k.lower() or q in json.dumps(v).lower()]
    r_urls = [x for x in (ap.get("repo_external_urls") or []) if q in str(x).lower()]
    r_ast = [(k, v) for k, v in sorted((ap.get("repo_scripts_ast") or {}).items()) if q in k.lower() or q in json.dumps(v).lower()]
    r_js = [x for x in (ap.get("repo_js_apis") or []) if q in json.dumps(x).lower()]

    print(
        f"=== COMPLETE API MATCHES for '{query}': {len(g_eps)} game endpoints, {len(g_load)} Loading mods, "
        f"{len(g_net)} C# Net classes, {len(r_urls)} repo URLs, {len(r_ast)} repo Python mods, {len(r_js)} JS APIs ==="
    )
    for x in g_eps[:limit]:
        print(f"  [GameEP] {x.get('endpoint')} <- {x.get('source')}")
    for k, v in g_load[:limit]:
        meths = list((v.get("methods") or {}).keys())[:10] if isinstance(v, dict) else []
        print(f"  [Loading] {k} -> methods={meths}")
    for k, v in g_net[:limit]:
        meths = (v.get("methods") or [])[:10] if isinstance(v, dict) else []
        print(f"  [C#Net] {k} -> methods={meths}")
    for x in r_urls[:limit]:
        print(f"  [RepoURL] {x.get('file')} -> {x.get('url')}")
    for k, v in r_ast[:limit]:
        fns = [f["name"] for f in (v.get("functions") or [])[:8]] if isinstance(v, dict) else []
        print(f"  [RepoPy] {k} ({v.get('lines', 0)}L) fns={fns} msgs={v.get('msg_defines_used', [])[:5]}")
    for x in r_js[:limit]:
        print(f"  [RepoJS] {x.get('file')} handlers={x.get('http_handlers')} fns={[f['name'] for f in (x.get('functions') or [])[:10]]}")
    return 0


def cmd_engine(query: str, limit: int) -> int:
    q = query.lower()
    de = load_db("deep engine scene pve world.json")
    gcls = de.get("global_engine_classes") or {}
    dmods = de.get("deep_engine_modules") or {}
    dlls = de.get("native_dlls") or []

    g_hits = []
    for gn, gi in sorted(gcls.items()):
        mm = [m for m in (gi.get("methods") or []) if q in m.lower()]
        if q in gn.lower() or mm or q in str(gi.get("fields_sample", "")).lower():
            g_hits.append((gn, gi, mm))

    m_hits = []
    for mn, mi in sorted(dmods.items()):
        mm = [m for m in (mi.get("methods") or []) if q in m.lower()]
        if q in mn.lower() or mm:
            m_hits.append((mn, mi, mm))

    d_hits = [d for d in dlls if q in str(d.get("name", "")).lower() or q in str(d.get("path", "")).lower()]
    print(f"=== DEEP ENGINE MATCHES for '{query}': {len(g_hits)} global classes, {len(m_hits)} scene/PVE/framework mods, {len(d_hits)} native DLLs ===")
    for gn, gi, mm in g_hits[:limit]:
        show_m = mm[:15] if (mm and q not in gn.lower()) else (gi.get("methods") or [])[:15]
        print(f"  [Global _G.{gn}] ({gi.get('method_count', 0)} methods) msgs={gi.get('msgs', [])[:4]} evs={gi.get('events', [])[:4]} dcs={gi.get('dcs', [])[:4]}")
        print(f"    Methods: {show_m}")
    for mn, mi, mm in m_hits[:limit]:
        show_m = mm[:15] if (mm and q not in mn.lower()) else (mi.get("methods") or [])[:15]
        print(f"  [EngineMod {mn}] ({mi.get('method_count', 0)} methods) msgs={mi.get('msgs', [])[:4]} evs={mi.get('events', [])[:4]} dcs={mi.get('dcs', [])[:4]}")
        print(f"    Methods: {show_m}")
    for d in d_hits[:limit]:
        print(f"  [DLL] {d['name']} ({d['rss_kb']:,} KB) -> {d['path']}")
    return 0


def cmd_enum(query: str, limit: int) -> int:
    q = query.lower()
    en = load_db("enums complete.json").get("enums") or {}
    hits = []
    for ename, vals in sorted(en.items()):
        if not isinstance(vals, dict):
            continue
        mkv = [(k, v) for k, v in sorted(vals.items()) if q in k.lower() or q in str(v).lower()]
        if q in ename.lower() or mkv:
            hits.append((ename, vals, mkv))
    print(f"=== ENUM MATCHES for '{query}': {len(hits)} enum tables ===")
    for ename, vals, mkv in hits[:limit]:
        show = mkv[:15] if (mkv and q not in ename.lower()) else list(sorted(vals.items()))[:15]
        print(f"  [{ename}] ({len(vals)} entries): " + ", ".join(f"{k}={v}" for k, v in show))
    return 0


def cmd_event(query: str, limit: int) -> int:
    q = query.lower()
    ev_ids = load_db("packets complete.json").get("event_ids") or {}
    ev_l = load_db("ui windows and buttons.json").get("active_event_listeners") or {}
    hits = [(k, v, ev_l.get(k)) for k, v in sorted(ev_ids.items()) if q in k.lower() or q == str(v).lower()]
    print(f"=== EVENTID MATCHES for '{query}': {len(hits)} ===")
    for k, v, linfo in hits[:limit]:
        extra = f" | LIVE listeners={linfo['count']} {linfo.get('listeners', [])[:3]}" if linfo else ""
        print(f"  [EventId.{k}] = {v}{extra}")
    return 0


def cmd_heinz(query: str, limit: int) -> int:
    q = query.lower()
    hz = load_db("heinz architecture.json")
    hb = hz.get("hub_backend") or {}
    hf = hz.get("hub_frontend") or {}
    br = hz.get("bot_and_repo") or {}
    rpcs = [r for r in (hb.get("public_rpc_methods") or []) if q in str(r).lower()]
    routes = [r for r in (hb.get("action_routes") or []) if q in str(r).lower()]
    cats = [c for c in (hb.get("task_catalog") or []) if q in str(c).lower()]
    bfns = [f for f in (br.get("bot_actions_functions") or []) if q in str(f).lower()]
    jfns = [f for f in (hf.get("js_functions") or []) if q in str(f).lower()]
    rfiles = [f for f in (br.get("repo_files") or []) if q in str(f.get("path", "")).lower()]
    print(f"=== HEINZ MATCHES for '{query}': {len(rpcs)} RPCs, {len(routes)} routes, {len(cats)} cards, {len(bfns)} bot fns, {len(jfns)} JS fns, {len(rfiles)} files ===")
    for r in rpcs[:limit]:
        print(f"  [RPC] HubBackend.{r['name']}({', '.join(r.get('args', []))}) L{r.get('line')} | {r.get('doc', '')[:70]}")
    for r in routes[:limit]:
        print(f"  [Route] action_id='{r['action_id']}' L{r.get('line')} payload={r.get('payload_keys', [])}")
    for c in cats[:limit]:
        print(f"  [TaskCard] {c['key']} ({c.get('category')}) - {c.get('title')}")
    for f in bfns[:limit]:
        print(f"  [BotFn] {f['name']}({', '.join(f.get('args', []))}) L{f.get('line')} | msgs={f.get('msg_defines_used', [])[:5]} dcs={f.get('datacenter_mgrs_used', [])[:5]}")
    for j in jfns[:limit]:
        print(f"  [JSFn] {j['name']}({j.get('params', '')}) L{j.get('line')}")
    for rf in rfiles[:limit]:
        print(f"  [File] {rf['path']} ({rf.get('bytes', 0):,} bytes)")
    return 0


def cmd_search(query: str, limit: int) -> int:
    sub = max(4, limit // 3)
    for fn in (cmd_packet, cmd_manager, cmd_callgraph, cmd_view, cmd_button, cmd_goto, cmd_table, cmd_loc, cmd_csharp, cmd_proto, cmd_http, cmd_api, cmd_engine, cmd_enum, cmd_event, cmd_heinz):
        fn(query, sub)
        print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the 100% Complete Last Z + HeinZ Megamind.")
    parser.add_argument(
        "command",
        choices=["fts", "trace", "icon", "model", "map", "domain", "summary", "search", "packet", "manager", "callgraph", "ui", "view", "button", "goto", "table", "xml", "loc", "csharp", "proto", "http", "api", "engine", "enum", "event", "heinz"],
    )
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("extra", nargs="?", default="")
    parser.add_argument("--layer", default="", help="Optional layer filter for `fts` (e.g. packet, datacenter, ui_window, csharp, heinz_bot_fn, game_icon, game_model, hero_skin_spine, hub_game_icon, game_map)")
    parser.add_argument("--domain", default="", help="Optional domain filter for `fts` (e.g. radar_detect, trucks_bounties, chat_moments_mail)")
    parser.add_argument("--season", default="", help="Optional season filter for `icon`, `model`, or `map` (e.g. 'Pre-Season 1', 'Season 3', 'Season 6', 'All Seasons')")
    parser.add_argument("--category", default="", help="Optional category filter for `icon` or `map` (e.g. 'Resources', 'Main World Maps', 'Event Maps', 'Seasonal Maps')")
    parser.add_argument("--faction", default="", help="Optional faction/category filter for `model` (e.g. 'Blood Rose', 'HQ Skins', 'Vehicle Skins', 'Zombies and Monsters')")
    parser.add_argument("--type", dest="asset_type", default="", help="Optional asset type filter for `model` (all, 3d, spine, hq, vehicle)")
    parser.add_argument("--limit", type=int, default=None, help="Maximum hits to return (default: 25 for icon/model/map, 20 for other commands)")
    args = parser.parse_args()

    eff_limit = max(1, args.limit if args.limit is not None else (25 if args.command in ("icon", "model", "map") else 20))

    if args.command == "summary":
        return cmd_summary()
    if args.command == "domain":
        return cmd_domain(args.query.strip())
    if args.command == "icon":
        q_icon = args.query.strip()
        if not q_icon:
            if args.season.strip() or args.category.strip():
                q_icon = "*"
            else:
                parser.error("Command 'icon' requires a <query> argument (or --season / --category filter).")
        return cmd_icon(q_icon, eff_limit, season=args.season.strip(), category=args.category.strip())
    if args.command == "model":
        q_model = args.query.strip()
        if not q_model:
            if args.season.strip() or args.faction.strip() or args.asset_type.strip():
                q_model = "*"
            else:
                parser.error("Command 'model' requires a <query> argument (or --season / --faction / --type filter).")
        return cmd_model(
            q_model,
            eff_limit,
            season=args.season.strip(),
            faction=args.faction.strip(),
            asset_type=args.asset_type.strip(),
        )
    if args.command == "map":
        q_map = args.query.strip()
        if not q_map:
            if args.category.strip() or args.season.strip():
                q_map = "*"
            else:
                parser.error("Command 'map' requires a <query> argument (or --category / --season filter).")
        return cmd_map(
            q_map,
            eff_limit,
            category=args.category.strip(),
            season=args.season.strip(),
        )
    if not args.query.strip():
        parser.error(f"Command '{args.command}' requires a <query> argument.")
    if args.command == "fts":
        return cmd_fts(args.query.strip(), eff_limit, layer=args.layer.strip(), domain=args.domain.strip())
    if args.command == "trace":
        return cmd_trace(args.query.strip(), eff_limit)
    if args.command == "xml":
        return cmd_xml(args.query.strip(), args.extra.strip(), eff_limit)

    dispatch = {
        "search": cmd_search,
        "packet": cmd_packet,
        "manager": cmd_manager,
        "callgraph": cmd_callgraph,
        "ui": cmd_ui,
        "view": cmd_view,
        "button": cmd_button,
        "goto": cmd_goto,
        "table": cmd_table,
        "loc": cmd_loc,
        "csharp": cmd_csharp,
        "proto": cmd_proto,
        "http": cmd_http,
        "api": cmd_api,
        "engine": cmd_engine,
        "enum": cmd_enum,
        "event": cmd_event,
        "heinz": cmd_heinz,
    }
    return dispatch[args.command](args.query.strip(), eff_limit)


if __name__ == "__main__":
    raise SystemExit(main())
