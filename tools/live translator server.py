"""Always-on local live translation bridge for Last Z PC clients.

Intercepts Last Z's in-game HTTP translation calls (`_G.TranslateUrlList`) via a
fast local ThreadingHTTPServer bound to 127.0.0.1, backed by an in-memory LRU
cache, persistent WAL SQLite cache, Last Z rich-text/gaming-token protection,
and a 4-tier zero-setup provider cascade (plus optional DeepL / Gemini keys).
"""

from __future__ import annotations

import atexit
import collections
from email.parser import BytesParser
from email.policy import default as email_default_policy
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import threading
import time
from typing import Any, Callable
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 18765
PORT_FALLBACK_END = 18775
PROVIDER_TIMEOUT = 4.0
MAX_SQLITE_ROWS = 25000
MAX_MEMORY_ENTRIES = 2000
RECENT_HISTORY_LIMIT = 15
LASTZ_UPSTREAM_URL = "https://translate-lm.omnilojoapps.com/client.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HeinZTranslator/1.0"

OFFICIAL_LASTZ_LANGUAGES: tuple[str, ...] = (
    "en",
    "zh-CN",
    "zh-TW",
    "fr",
    "de",
    "es",
    "pt",
    "it",
    "ru",
    "ko",
    "ja",
    "th",
    "tr",
    "id",
    "vi",
    "ar",
    "pl",
    "nl",
)

_LANG_ALIAS_MAP: dict[str, str] = {
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "en-au": "en",
    "en-ca": "en",
    "eng": "en",
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "zh-sg": "zh-CN",
    "zh-chs": "zh-CN",
    "chs": "zh-CN",
    "cn": "zh-CN",
    "zh-tw": "zh-TW",
    "zh-hant": "zh-TW",
    "zh-hk": "zh-TW",
    "zh-mo": "zh-TW",
    "zh-cht": "zh-TW",
    "cht": "zh-TW",
    "tw": "zh-TW",
    "fr": "fr",
    "fr-fr": "fr",
    "fr-ca": "fr",
    "fr-be": "fr",
    "fr-ch": "fr",
    "de": "de",
    "de-de": "de",
    "de-at": "de",
    "de-ch": "de",
    "es": "es",
    "es-es": "es",
    "es-mx": "es",
    "es-419": "es",
    "es-ar": "es",
    "pt": "pt",
    "pt-br": "pt",
    "pt-pt": "pt",
    "br": "pt",
    "it": "it",
    "it-it": "it",
    "ru": "ru",
    "ru-ru": "ru",
    "ko": "ko",
    "ko-kr": "ko",
    "kr": "ko",
    "ja": "ja",
    "ja-jp": "ja",
    "jp": "ja",
    "th": "th",
    "th-th": "th",
    "tr": "tr",
    "tr-tr": "tr",
    "id": "id",
    "id-id": "id",
    "in": "id",
    "vi": "vi",
    "vi-vn": "vi",
    "vn": "vi",
    "ar": "ar",
    "ar-sa": "ar",
    "ar-ae": "ar",
    "ar-eg": "ar",
    "pl": "pl",
    "pl-pl": "pl",
    "nl": "nl",
    "nl-nl": "nl",
    "nl-be": "nl",
}

_DEEPL_TARGET_MAP: dict[str, str] = {
    "en": "EN-US",
    "zh-CN": "ZH-HANS",
    "zh-TW": "ZH-HANT",
    "fr": "FR",
    "de": "DE",
    "es": "ES",
    "pt": "PT-BR",
    "it": "IT",
    "ru": "RU",
    "ko": "KO",
    "ja": "JA",
    "tr": "TR",
    "id": "ID",
    "ar": "AR",
    "pl": "PL",
    "nl": "NL",
}

DEFAULT_TRANSLATOR_CONFIG: dict[str, Any] = {
    "enabled": True,
    "auto_translate_chat": True,
    "target_lang": "auto",
    "deepl_api_key": "",
    "gemini_api_key": "",
}

# Single-pass ordered token protector:
# 1. Last Z chat emojis: <e:7/>
# 2. Unity color tags: <color=...> / </color>
# 3. Unity / TMP rich text tags: <...> (up to 32 inner chars)
# 4. Alliance tags: [WARG]
# 5. Map coordinates: (214, 554) or (500:500)
# 6. Standalone Last Z gaming acronyms (ASCII word boundaries so CJK/Hangul adjacency works)
_TOKEN_PROTECT_RE = re.compile(
    r"(?:"
    r"<e:\d+/>"
    r"|</?color(?:=[^>\r\n]+)?>"
    r"|<#[0-9A-Fa-f]{3,8}>"
    r"|</?[A-Za-z][^>\r\n]{0,31}>"
    r"|\[[A-Za-z0-9_-]{2,6}\]"
    r"|\(\s*\d{1,4}\s*[,:]\s*\d{1,4}\s*\)"
    r"|(?<![A-Za-z0-9_])(?:SvS|SVS|HQ|RSS|NAP|KE|VS|R4|R5|T8|T9|T10|AP|BP|S[1-6])(?![A-Za-z0-9_])"
    r")"
)
_PLACEHOLDER_STRIP_RE = re.compile(r"ZZTOK\d+ZZ|\u27e6\d+\u27e7", re.IGNORECASE)
_PLACEHOLDER_RESTORE_RE = re.compile(r"(?:ZZ\s*TOK\s*(\d+)\s*ZZ|\u27e6\s*(\d+)\s*\u27e7)", re.IGNORECASE)
_ZZTOK_TO_WIRE_RE = re.compile(r"ZZTOK(\d+)ZZ")


def _resolve_data_dir() -> Path:
    override = os.environ.get("HEINZ_DATA_DIR", "").strip()
    if override:
        return Path(override)
    return REPO_ROOT / "data"


def _get_json_cache_dir() -> Path:
    return _resolve_data_dir() / "json cache"


def get_bridge_path() -> Path:
    return _get_json_cache_dir() / "translator bridge.json"


def get_config_path() -> Path:
    return _get_json_cache_dir() / "translator config.json"


def get_cache_db_path() -> Path:
    return _get_json_cache_dir() / "translation cache.sqlite"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    raw = json.dumps(payload, ensure_ascii=False, indent=2)
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(raw)
            fh.flush()
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def normalize_lang_code(code: str | None, default: str = "en") -> str:
    """Normalize Last Z and BCP-47 language codes across all 18 official languages."""
    raw = str(code or "").strip()
    if not raw:
        return default
    cleaned = raw.replace("_", "-").strip()
    low = cleaned.lower()
    if low == "auto":
        return default
    if low in _LANG_ALIAS_MAP:
        return _LANG_ALIAS_MAP[low]
    base = low.split("-", 1)[0]
    if base in _LANG_ALIAS_MAP:
        return _LANG_ALIAS_MAP[base]
    return cleaned


def normalize_source_lang(code: str | None) -> str:
    """Normalize an optional source language code, returning '' for auto-detect."""
    raw = str(code or "").strip()
    if not raw or raw.lower() == "auto":
        return ""
    return normalize_lang_code(raw, default="")


def protect_game_tokens(text: str) -> tuple[str, list[str]]:
    """Replace Last Z markup, emojis, alliance tags, coords, and acronyms with opaque placeholders."""
    tokens: list[str] = []

    def _repl(match: re.Match[str]) -> str:
        idx = len(tokens)
        tokens.append(match.group(0))
        return f"ZZTOK{idx}ZZ"

    protected = _TOKEN_PROTECT_RE.sub(_repl, text)
    return protected, tokens


def _to_wire_placeholders(protected_text: str) -> str:
    """Convert ZZTOK<n>ZZ to script-neutral ⟦<n>⟧ for HTTP providers so sl=auto is never skewed by Latin letters."""
    return _ZZTOK_TO_WIRE_RE.sub(lambda m: f"\u27e6{m.group(1)}\u27e7", protected_text)


def restore_game_tokens(text: str, tokens: list[str] | dict[str, str]) -> str:
    """Restore opaque ZZTOK<n>ZZ (and script-neutral wire) placeholders case-insensitively after translation."""
    if not tokens or not text:
        return text

    def _match_idx(match: re.Match[str]) -> int:
        raw_num = match.group(1) if match.group(1) is not None else match.group(2)
        return int(raw_num)

    if isinstance(tokens, dict):
        ordered: dict[int, str] = {}
        for k, v in tokens.items():
            m = _PLACEHOLDER_RESTORE_RE.fullmatch(str(k).strip())
            if m:
                ordered[_match_idx(m)] = str(v)

        def _repl_dict(match: re.Match[str]) -> str:
            idx = _match_idx(match)
            return ordered.get(idx, match.group(0))

        return _PLACEHOLDER_RESTORE_RE.sub(_repl_dict, text)

    def _repl_list(match: re.Match[str]) -> str:
        idx = _match_idx(match)
        if 0 <= idx < len(tokens):
            return tokens[idx]
        return match.group(0)

    return _PLACEHOLDER_RESTORE_RE.sub(_repl_list, text)


def _should_skip_translation(text: str, protected_text: str) -> bool:
    if not text or not text.strip():
        return True
    residual = _PLACEHOLDER_STRIP_RE.sub("", protected_text)
    return not any(ch.isalpha() for ch in residual)


def _guess_source_lang_for_mymemory(text: str, target_lang: str) -> str:
    """Lightweight Unicode script heuristic for MyMemory when source language is auto."""
    sample = _PLACEHOLDER_STRIP_RE.sub("", text)
    counts = {
        "ko": 0,
        "ja": 0,
        "zh": 0,
        "ru": 0,
        "ar": 0,
        "th": 0,
    }
    for ch in sample:
        cp = ord(ch)
        if 0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF:
            counts["ko"] += 1
        elif 0x3040 <= cp <= 0x30FF:
            counts["ja"] += 1
        elif 0x4E00 <= cp <= 0x9FFF:
            counts["zh"] += 1
        elif 0x0400 <= cp <= 0x04FF:
            counts["ru"] += 1
        elif 0x0600 <= cp <= 0x06FF:
            counts["ar"] += 1
        elif 0x0E00 <= cp <= 0x0E7F:
            counts["th"] += 1

    if counts["ko"] > 0:
        return "ko"
    if counts["ja"] > 0:
        return "ja"
    if counts["zh"] > 0:
        return "zh-CN"
    if counts["ru"] > 0:
        return "ru"
    if counts["ar"] > 0:
        return "ar"
    if counts["th"] > 0:
        return "th"

    low = sample.lower()
    if any(c in low for c in "ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ"):
        return "vi"
    if any(c in low for c in "ğışİ"):
        return "tr"
    if any(c in low for c in "ąćęłńóśźż"):
        return "pl"
    if any(c in low for c in "ß"):
        return "de"
    if any(c in low for c in "¿¡ñ"):
        return "es"
    if any(c in low for c in "ãõ"):
        return "pt"
    if any(c in low for c in "œæ"):
        return "fr"

    return "es" if target_lang == "en" else "en"


def _hash_source_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


class TranslationCache:
    """Thread-safe in-memory LRU (2,000) + persistent WAL SQLite cache (25,000 rows)."""

    def __init__(
        self,
        db_path: Path | None = None,
        max_memory_entries: int = MAX_MEMORY_ENTRIES,
        max_sqlite_rows: int = MAX_SQLITE_ROWS,
    ) -> None:
        self.db_path = Path(db_path) if db_path is not None else get_cache_db_path()
        self.max_memory_entries = max(1, int(max_memory_entries))
        self.max_sqlite_rows = max(1, int(max_sqlite_rows))
        self._lock = threading.RLock()
        self._lru: collections.OrderedDict[tuple[str, str], dict[str, str]] = collections.OrderedDict()
        self._conn: sqlite3.Connection | None = None
        self._writes_since_prune = 0
        self._prune_interval = max(1, min(100, self.max_sqlite_rows // 10 or 1))
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path), timeout=5.0, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS translations (
                    target_lang TEXT NOT NULL,
                    source_hash TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    original_lang TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    hits INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (target_lang, source_hash)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_translations_updated_at ON translations(updated_at)"
            )
            conn.commit()
            self._conn = conn

    def get(self, target_lang: str, source_text: str) -> dict[str, str] | None:
        key = (target_lang, _hash_source_text(source_text))
        with self._lock:
            mem = self._lru.get(key)
            if mem is not None:
                self._lru.move_to_end(key)
                return dict(mem)

            if self._conn is None:
                return None
            try:
                row = self._conn.execute(
                    """
                    SELECT original_lang, translated_text, provider
                    FROM translations
                    WHERE target_lang = ? AND source_hash = ?
                    """,
                    key,
                ).fetchone()
            except sqlite3.Error:
                return None

            if row is None:
                return None

            entry = {
                "originalLang": str(row[0] or "auto"),
                "translateMsg": str(row[1] or ""),
                "provider": str(row[2] or "cache"),
            }
            self._put_memory(key, entry)
            return dict(entry)

    def _put_memory(self, key: tuple[str, str], entry: dict[str, str]) -> None:
        self._lru[key] = dict(entry)
        self._lru.move_to_end(key)
        while len(self._lru) > self.max_memory_entries:
            self._lru.popitem(last=False)

    def put(
        self,
        target_lang: str,
        source_text: str,
        original_lang: str,
        translated_text: str,
        provider: str,
    ) -> None:
        source_hash = _hash_source_text(source_text)
        key = (target_lang, source_hash)
        entry = {
            "originalLang": original_lang or "auto",
            "translateMsg": translated_text,
            "provider": provider,
        }
        now_ts = time.time()
        with self._lock:
            self._put_memory(key, entry)
            if self._conn is None:
                return
            try:
                self._conn.execute(
                    """
                    INSERT INTO translations (
                        target_lang, source_hash, source_text,
                        original_lang, translated_text, provider, updated_at, hits
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(target_lang, source_hash) DO UPDATE SET
                        original_lang = excluded.original_lang,
                        translated_text = excluded.translated_text,
                        provider = excluded.provider,
                        updated_at = excluded.updated_at,
                        hits = translations.hits + 1
                    """,
                    (
                        target_lang,
                        source_hash,
                        source_text,
                        entry["originalLang"],
                        translated_text,
                        provider,
                        now_ts,
                    ),
                )
                self._writes_since_prune += 1
                if self._writes_since_prune >= self._prune_interval:
                    self._writes_since_prune = 0
                    self._prune_locked()
                self._conn.commit()
            except sqlite3.Error:
                pass

    def _prune_locked(self) -> None:
        if self._conn is None:
            return
        row = self._conn.execute("SELECT COUNT(*) FROM translations").fetchone()
        count = int(row[0]) if row else 0
        excess = count - self.max_sqlite_rows
        if excess > 0:
            self._conn.execute(
                """
                DELETE FROM translations
                WHERE rowid IN (
                    SELECT rowid FROM translations
                    ORDER BY updated_at ASC
                    LIMIT ?
                )
                """,
                (excess,),
            )

    def count_sqlite_rows(self) -> int:
        with self._lock:
            if self._conn is None:
                return 0
            row = self._conn.execute("SELECT COUNT(*) FROM translations").fetchone()
            return int(row[0]) if row else 0

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None


class TranslatorStats:
    """Thread-safe metrics tracker for the local translator server."""

    def __init__(self, recent_limit: int = RECENT_HISTORY_LIMIT) -> None:
        self._lock = threading.Lock()
        self.total_requests = 0
        self.cache_hits = 0
        self.total_ms = 0.0
        self.provider_counts: dict[str, int] = {}
        self.recent: collections.deque[dict[str, Any]] = collections.deque(maxlen=recent_limit)

    def record(
        self,
        *,
        src: str,
        dst: str,
        original_lang: str,
        target_lang: str,
        provider: str,
        cached: bool,
        elapsed_ms: float,
    ) -> None:
        with self._lock:
            self.total_requests += 1
            if cached:
                self.cache_hits += 1
            self.total_ms += max(0.0, float(elapsed_ms))
            key = "cache" if cached else (provider or "unknown")
            self.provider_counts[key] = self.provider_counts.get(key, 0) + 1
            self.recent.appendleft(
                {
                    "src": src[:200],
                    "dst": dst[:200],
                    "originalLang": original_lang,
                    "targetLang": target_lang,
                    "provider": key,
                    "cached": bool(cached),
                    "ms": round(float(elapsed_ms), 2),
                    "ts": round(time.time(), 3),
                }
            )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            avg_ms = round(self.total_ms / self.total_requests, 2) if self.total_requests else 0.0
            hit_rate = round((self.cache_hits / self.total_requests) * 100.0, 1) if self.total_requests else 0.0
            return {
                "ok": True,
                "total_requests": self.total_requests,
                "cache_hits": self.cache_hits,
                "cache_hit_rate": hit_rate,
                "provider_counts": dict(self.provider_counts),
                "avg_ms": avg_ms,
                "recent": list(self.recent),
            }


_CONFIG_CACHE_LOCK = threading.Lock()
_CONFIG_CACHE_STATE: dict[str, Any] = {"path": None, "mtime_ns": -1, "cfg": None}
_GLOBAL_CACHE_LOCK = threading.Lock()
_GLOBAL_CACHE: TranslationCache | None = None
_GLOBAL_CACHE_PATH: Path | None = None
_GLOBAL_STATS = TranslatorStats()


def _normalize_config(raw: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_TRANSLATOR_CONFIG)
    if isinstance(raw, dict):
        if "enabled" in raw:
            merged["enabled"] = bool(raw["enabled"])
        if "auto_translate_chat" in raw:
            merged["auto_translate_chat"] = bool(raw["auto_translate_chat"])
        if "target_lang" in raw:
            tl = str(raw["target_lang"] or "auto").strip() or "auto"
            merged["target_lang"] = "auto" if tl.lower() == "auto" else normalize_lang_code(tl, default="en")
        if "deepl_api_key" in raw and raw["deepl_api_key"] is not None:
            merged["deepl_api_key"] = str(raw["deepl_api_key"]).strip()
        if "gemini_api_key" in raw and raw["gemini_api_key"] is not None:
            merged["gemini_api_key"] = str(raw["gemini_api_key"]).strip()
    return merged


def load_translator_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load translator preferences from data/json cache/translator config.json with mtime caching."""
    path = Path(config_path) if config_path is not None else get_config_path()
    try:
        mtime_ns = path.stat().st_mtime_ns
    except OSError:
        return dict(DEFAULT_TRANSLATOR_CONFIG)

    with _CONFIG_CACHE_LOCK:
        if (
            _CONFIG_CACHE_STATE["path"] == str(path)
            and _CONFIG_CACHE_STATE["mtime_ns"] == mtime_ns
            and isinstance(_CONFIG_CACHE_STATE["cfg"], dict)
        ):
            return dict(_CONFIG_CACHE_STATE["cfg"])

    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except Exception:
        raw = {}

    cfg = _normalize_config(raw if isinstance(raw, dict) else {})
    with _CONFIG_CACHE_LOCK:
        _CONFIG_CACHE_STATE["path"] = str(path)
        _CONFIG_CACHE_STATE["mtime_ns"] = mtime_ns
        _CONFIG_CACHE_STATE["cfg"] = dict(cfg)
    return cfg


def save_translator_config(cfg: dict[str, Any], config_path: Path | None = None) -> dict[str, Any]:
    """Persist translator preferences atomically."""
    path = Path(config_path) if config_path is not None else get_config_path()
    normalized = _normalize_config(cfg)
    _atomic_write_json(path, normalized)
    try:
        mtime_ns = path.stat().st_mtime_ns
    except OSError:
        mtime_ns = -1
    with _CONFIG_CACHE_LOCK:
        _CONFIG_CACHE_STATE["path"] = str(path)
        _CONFIG_CACHE_STATE["mtime_ns"] = mtime_ns
        _CONFIG_CACHE_STATE["cfg"] = dict(normalized)
    return normalized


def _get_global_cache() -> TranslationCache:
    global _GLOBAL_CACHE, _GLOBAL_CACHE_PATH
    wanted = get_cache_db_path()
    with _GLOBAL_CACHE_LOCK:
        if _GLOBAL_CACHE is not None and _GLOBAL_CACHE_PATH == wanted:
            return _GLOBAL_CACHE
        if _GLOBAL_CACHE is not None:
            _GLOBAL_CACHE.close()
        _GLOBAL_CACHE = TranslationCache(db_path=wanted)
        _GLOBAL_CACHE_PATH = wanted
        return _GLOBAL_CACHE


# ---------------------------------------------------------------------------
# Provider HTTP helpers (all use urllib.request with strict 4s timeout)
# ---------------------------------------------------------------------------

def _http_request_json(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = PROVIDER_TIMEOUT,
) -> Any:
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json, text/plain, */*"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def _provider_deepl(
    protected_text: str,
    target_lang: str,
    source_lang: str,
    api_key: str,
    timeout: float = PROVIDER_TIMEOUT,
) -> tuple[str, str] | None:
    key = api_key.strip()
    if not key:
        return None
    dl_target = _DEEPL_TARGET_MAP.get(target_lang)
    if not dl_target:
        return None
    base = "https://api-free.deepl.com/v2/translate" if key.endswith(":fx") else "https://api.deepl.com/v2/translate"
    body: dict[str, Any] = {"text": [protected_text], "target_lang": dl_target}
    if source_lang:
        src_base = source_lang.split("-", 1)[0].upper()
        if len(src_base) == 2:
            body["source_lang"] = src_base
    payload = json.dumps(body).encode("utf-8")
    data = _http_request_json(
        base,
        method="POST",
        data=payload,
        headers={
            "Authorization": f"DeepL-Auth-Key {key}",
            "Content-Type": "application/json",
        },
        timeout=timeout,
    )
    items = data.get("translations") if isinstance(data, dict) else None
    if isinstance(items, list) and items and isinstance(items[0], dict):
        translated = str(items[0].get("text") or "").strip()
        detected = normalize_lang_code(items[0].get("detected_source_language"), default=source_lang or "auto")
        if translated:
            return translated, detected
    return None


def _provider_gemini(
    protected_text: str,
    target_lang: str,
    source_lang: str,
    api_key: str,
    timeout: float = PROVIDER_TIMEOUT,
) -> tuple[str, str] | None:
    key = api_key.strip()
    if not key:
        return None
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={urllib.parse.quote(key)}"
    )
    prompt = (
        f"Translate this Last Z game chat message into BCP-47 language '{target_lang}'. "
        "Keep every ZZTOK<number>ZZ placeholder completely unchanged. "
        'Reply ONLY with JSON: {"originalLang":"<iso_code>","translateMsg":"<translated>"}.\n'
        f"Message: {protected_text}"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }
    data = _http_request_json(
        url,
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )
    candidates = data.get("candidates") if isinstance(data, dict) else None
    if not isinstance(candidates, list) or not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    if not isinstance(parts, list) or not parts:
        return None
    raw_txt = str(parts[0].get("text") or "").strip()
    if raw_txt.startswith("```"):
        raw_txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_txt, flags=re.S).strip()
    parsed = json.loads(raw_txt)
    if isinstance(parsed, dict):
        translated = str(parsed.get("translateMsg") or "").strip()
        detected = normalize_lang_code(parsed.get("originalLang"), default=source_lang or "auto")
        if translated:
            return translated, detected
    return None


def _provider_google_gtx(
    protected_text: str,
    target_lang: str,
    source_lang: str,
    timeout: float = PROVIDER_TIMEOUT,
) -> tuple[str, str] | None:
    qs = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": source_lang or "auto",
            "tl": target_lang,
            "dt": "t",
            "q": protected_text,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{qs}"
    data = _http_request_json(url, timeout=timeout)
    if not isinstance(data, list) or not data or not isinstance(data[0], list):
        return None
    segments: list[str] = []
    for seg in data[0]:
        if isinstance(seg, list) and seg and seg[0] is not None:
            segments.append(str(seg[0]))
    translated = "".join(segments).strip()
    if not translated:
        return None
    detected = ""
    if len(data) > 2 and isinstance(data[2], str) and data[2].strip():
        detected = data[2].strip()
    elif len(data) > 8 and isinstance(data[8], list) and data[8] and isinstance(data[8][0], list) and data[8][0]:
        detected = str(data[8][0][0] or "").strip()
    detected = normalize_lang_code(detected, default=source_lang or "auto")
    return translated, detected


def _provider_google_dict(
    protected_text: str,
    target_lang: str,
    source_lang: str,
    timeout: float = PROVIDER_TIMEOUT,
) -> tuple[str, str] | None:
    qs = urllib.parse.urlencode(
        {
            "client": "dict-chrome-ex",
            "sl": source_lang or "auto",
            "tl": target_lang,
            "q": protected_text,
        }
    )
    url = f"https://clients5.google.com/translate_a/t?{qs}"
    data = _http_request_json(url, timeout=timeout)
    translated = ""
    detected = source_lang or "auto"
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, list) and first:
            translated = str(first[0] or "").strip()
            if len(first) > 1 and isinstance(first[1], str) and first[1].strip():
                detected = first[1].strip()
        elif isinstance(first, str):
            translated = first.strip()
    elif isinstance(data, dict):
        sentences = data.get("sentences")
        if isinstance(sentences, list):
            translated = "".join(
                str(s.get("trans") or "") for s in sentences if isinstance(s, dict)
            ).strip()
        if isinstance(data.get("src"), str) and data["src"].strip():
            detected = data["src"].strip()
    if not translated:
        return None
    return translated, normalize_lang_code(detected, default=source_lang or "auto")


def _provider_mymemory(
    protected_text: str,
    target_lang: str,
    source_lang: str,
    timeout: float = PROVIDER_TIMEOUT,
) -> tuple[str, str] | None:
    eff_sl = source_lang or _guess_source_lang_for_mymemory(protected_text, target_lang)
    if not eff_sl or eff_sl.lower() == target_lang.lower():
        return None
    qs = urllib.parse.urlencode({"q": protected_text, "langpair": f"{eff_sl}|{target_lang}"})
    url = f"https://api.mymemory.translated.net/get?{qs}"
    data = _http_request_json(url, timeout=timeout)
    if not isinstance(data, dict):
        return None
    status = int(data.get("responseStatus") or 0)
    if status != 200:
        return None
    resp_data = data.get("responseData")
    if not isinstance(resp_data, dict):
        return None
    translated = str(resp_data.get("translatedText") or "").strip()
    if not translated:
        return None
    upper_t = translated.upper()
    if "MYMEMORY WARNING" in upper_t or "PLEASE SELECT TWO DISTINCT LANGUAGES" in upper_t:
        return None
    detected = resp_data.get("detectedLanguage") or eff_sl
    return translated, normalize_lang_code(str(detected), default=eff_sl)


def _provider_lastz_upstream(
    protected_text: str,
    target_lang: str,
    source_lang: str,
    extra_fields: dict[str, str] | None = None,
    timeout: float = PROVIDER_TIMEOUT,
) -> tuple[str, str] | None:
    form: dict[str, str] = {
        "sf": source_lang,
        "tf": target_lang,
        "sc": protected_text,
        "uid": "",
        "ui": "",
        "ch": "",
        "scene": "",
        "mod": "",
        "google": "1",
        "tk": "",
    }
    if extra_fields:
        for k in ("uid", "ui", "ch", "scene", "mod", "google", "tk"):
            if k in extra_fields and extra_fields[k] is not None:
                form[k] = str(extra_fields[k])
    encoded = urllib.parse.urlencode(form).encode("utf-8")
    data = _http_request_json(
        LASTZ_UPSTREAM_URL,
        method="POST",
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
        timeout=timeout,
    )
    if not isinstance(data, dict):
        return None
    if int(data.get("code", -1)) != 0:
        return None
    translated = str(data.get("translateMsg") or "").strip()
    if not translated:
        return None
    detected = normalize_lang_code(data.get("originalLang"), default=source_lang or "auto")
    return translated, detected


def translate_text(
    text: str,
    target_lang: str = "en",
    source_lang: str = "",
    config: dict[str, Any] | None = None,
    *,
    cache: TranslationCache | None = None,
    stats: TranslatorStats | None = None,
    extra_fields: dict[str, str] | None = None,
    timeout: float = PROVIDER_TIMEOUT,
) -> dict[str, Any]:
    """Translate text via LRU/SQLite cache and 4-tier always-works provider cascade."""
    started = time.perf_counter()
    src_text = str(text if text is not None else "")
    tl = normalize_lang_code(target_lang, default="en")
    sl = normalize_source_lang(source_lang)
    cfg = _normalize_config(config) if config is not None else load_translator_config()
    active_cache = cache if cache is not None else _get_global_cache()
    active_stats = stats if stats is not None else _GLOBAL_STATS

    protected_text, tokens = protect_game_tokens(src_text)
    if _should_skip_translation(src_text, protected_text):
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        active_stats.record(
            src=src_text,
            dst=src_text,
            original_lang=sl or tl,
            target_lang=tl,
            provider="skip",
            cached=False,
            elapsed_ms=elapsed_ms,
        )
        return {
            "code": 0,
            "originalLang": sl or tl,
            "targetLang": tl,
            "translateMsg": src_text,
            "provider": "skip",
            "cached": False,
            "elapsed_ms": round(elapsed_ms, 2),
        }

    # Tier 0: Cache lookup (in-memory LRU -> persistent SQLite)
    cached_hit = active_cache.get(tl, src_text)
    if cached_hit is not None:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        active_stats.record(
            src=src_text,
            dst=cached_hit["translateMsg"],
            original_lang=cached_hit["originalLang"],
            target_lang=tl,
            provider=cached_hit["provider"],
            cached=True,
            elapsed_ms=elapsed_ms,
        )
        return {
            "code": 0,
            "originalLang": cached_hit["originalLang"],
            "targetLang": tl,
            "translateMsg": cached_hit["translateMsg"],
            "provider": cached_hit["provider"],
            "cached": True,
            "elapsed_ms": round(elapsed_ms, 2),
        }

    # Convert placeholders to script-neutral wire markers so Google/MyMemory sl=auto
    # language detection is never skewed by Latin letters inside ZZTOK<n>ZZ.
    wire_text = _to_wire_placeholders(protected_text)

    # Build ordered provider chain: Tier 0.5 (optional keys) -> Tier 1..4 (zero-setup)
    providers: list[tuple[str, Callable[[], tuple[str, str] | None]]] = []
    deepl_key = str(cfg.get("deepl_api_key") or "").strip()
    gemini_key = str(cfg.get("gemini_api_key") or "").strip()
    if deepl_key:
        providers.append(
            ("deepl", lambda: _provider_deepl(wire_text, tl, sl, deepl_key, timeout=timeout))
        )
    if gemini_key:
        providers.append(
            ("gemini", lambda: _provider_gemini(protected_text, tl, sl, gemini_key, timeout=timeout))
        )
    providers.extend(
        [
            ("google_gtx", lambda: _provider_google_gtx(wire_text, tl, sl, timeout=timeout)),
            ("google_dict", lambda: _provider_google_dict(wire_text, tl, sl, timeout=timeout)),
            ("mymemory", lambda: _provider_mymemory(wire_text, tl, sl, timeout=timeout)),
            (
                "lastz_upstream",
                lambda: _provider_lastz_upstream(
                    wire_text, tl, sl, extra_fields=extra_fields, timeout=timeout
                ),
            ),
        ]
    )

    for prov_name, prov_fn in providers:
        try:
            outcome = prov_fn()
        except Exception:
            outcome = None
        if outcome is None:
            continue
        raw_translated, detected = outcome
        final_text = restore_game_tokens(raw_translated, tokens)
        if not final_text:
            continue
        active_cache.put(tl, src_text, detected, final_text, prov_name)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        active_stats.record(
            src=src_text,
            dst=final_text,
            original_lang=detected,
            target_lang=tl,
            provider=prov_name,
            cached=False,
            elapsed_ms=elapsed_ms,
        )
        return {
            "code": 0,
            "originalLang": detected,
            "targetLang": tl,
            "translateMsg": final_text,
            "provider": prov_name,
            "cached": False,
            "elapsed_ms": round(elapsed_ms, 2),
        }

    # Tier 5: Offline safety net (never error / never lock up Last Z UI)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    fallback_lang = sl or "auto"
    active_stats.record(
        src=src_text,
        dst=src_text,
        original_lang=fallback_lang,
        target_lang=tl,
        provider="passthrough",
        cached=False,
        elapsed_ms=elapsed_ms,
    )
    return {
        "code": 0,
        "originalLang": fallback_lang,
        "targetLang": tl,
        "translateMsg": src_text,
        "provider": "passthrough",
        "cached": False,
        "elapsed_ms": round(elapsed_ms, 2),
    }


# ---------------------------------------------------------------------------
# Lua Hook Builder (Idempotent, safe to run repeatedly on any Last Z client)
# ---------------------------------------------------------------------------

def _escape_lua_str(value: str) -> str:
    cleaned = str(value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "")
    return cleaned


def build_translator_lua_hook(
    port: int,
    enabled: bool = True,
    target_lang: str = "en",
    auto_translate_chat: bool = True,
) -> str:
    """Build idempotent Lua payload that redirects _G.TranslateUrlList and wires auto-translate."""
    safe_port = int(port)
    safe_enabled = "true" if enabled else "false"
    safe_auto = "true" if (enabled and auto_translate_chat) else "false"
    raw_target = str(target_lang or "auto").strip() or "auto"
    eff_target = "auto" if raw_target.lower() == "auto" else normalize_lang_code(raw_target, default="en")
    escaped_target = _escape_lua_str(eff_target)
    endpoint = f"http://127.0.0.1:{safe_port}/client.php"

    return f"""
local _hzPort = {safe_port}
local _hzEnabled = {safe_enabled}
local _hzAuto = {safe_auto}
local _hzTarget = "{escaped_target}"
local _hzEndpoint = "{endpoint}"

if _G.__HEINZ_ORIG_TRANSLATE_URLS__ == nil and type(_G.TranslateUrlList) == "table" then
    local _origCopy = {{}}
    for _i, _u in ipairs(_G.TranslateUrlList) do
        _origCopy[_i] = _u
    end
    _G.__HEINZ_ORIG_TRANSLATE_URLS__ = _origCopy
end

_G.__HEINZ_TRANSLATOR_CFG__ = {{
    enabled = _hzEnabled,
    target = _hzTarget,
    auto = _hzAuto,
    port = _hzPort,
}}

if not _hzEnabled then
    if type(_G.__HEINZ_ORIG_TRANSLATE_URLS__) == "table" then
        local _restore = {{}}
        for _i, _u in ipairs(_G.__HEINZ_ORIG_TRANSLATE_URLS__) do
            _restore[_i] = _u
        end
        _G.TranslateUrlList = _restore
    end
    return "TRANSLATOR_HOOK_DISABLED"
end

_G.TranslateUrlList = {{ _hzEndpoint, _hzEndpoint }}

if type(_G.__HEINZ_AUTO_TR_SEEN__) ~= "table" then
    _G.__HEINZ_AUTO_TR_SEEN__ = {{}}
    _G.__HEINZ_AUTO_TR_SEEN_COUNT__ = 0
end

local function _hzNowSec()
    if os and type(os.time) == "function" then
        return math.floor(os.time())
    end
    return 0
end

local function _hzAllowRateLimit()
    local sec = _hzNowSec()
    if _G.__HEINZ_AUTO_TR_SEC__ ~= sec then
        _G.__HEINZ_AUTO_TR_SEC__ = sec
        _G.__HEINZ_AUTO_TR_CNT__ = 0
    end
    local cnt = _G.__HEINZ_AUTO_TR_CNT__ or 0
    if cnt >= 3 then
        return false
    end
    _G.__HEINZ_AUTO_TR_CNT__ = cnt + 1
    return true
end

local function _hzTryAutoTranslateMsg(tm, msg)
    if type(msg) ~= "table" or not tm or type(tm.DoTranslate) ~= "function" then
        return false
    end
    local cfg = _G.__HEINZ_TRANSLATOR_CFG__
    if not cfg or not cfg.enabled or not cfg.auto then
        return false
    end
    local mtype = msg.type
    if mtype == nil and type(msg.getChatMessageType) == "function" then
        local okT, resT = pcall(msg.getChatMessageType, msg)
        if okT then mtype = resT end
    end
    if mtype ~= 0 then
        return false
    end
    local text = msg.msg
    if type(text) ~= "string" or text == "" then
        return false
    end
    local trMsg = msg.translateMsg
    if type(trMsg) == "string" and trMsg ~= "" then
        return false
    end
    local isTr = msg.isTranslating
    if isTr ~= nil and isTr ~= 0 and isTr ~= false then
        return false
    end
    local seqId = msg.seqId
    if seqId == nil and type(msg.getSeqId) == "function" then
        local okS, resS = pcall(msg.getSeqId, msg)
        if okS then seqId = resS end
    end
    if seqId == nil then
        seqId = text
    end
    local seen = _G.__HEINZ_AUTO_TR_SEEN__
    if seen[seqId] then
        return false
    end
    if not _hzAllowRateLimit() then
        return false
    end
    if (_G.__HEINZ_AUTO_TR_SEEN_COUNT__ or 0) > 2000 then
        seen = {{}}
        _G.__HEINZ_AUTO_TR_SEEN__ = seen
        _G.__HEINZ_AUTO_TR_SEEN_COUNT__ = 0
    end
    seen[seqId] = true
    _G.__HEINZ_AUTO_TR_SEEN_COUNT__ = (_G.__HEINZ_AUTO_TR_SEEN_COUNT__ or 0) + 1
    pcall(tm.DoTranslate, tm, msg)
    return true
end

local function _hzScanCandidate(tm, obj)
    if type(obj) ~= "table" then return end
    if obj.msg ~= nil and obj.type ~= nil then
        _hzTryAutoTranslateMsg(tm, obj)
        return
    end
    local lists = {{ obj.msgs, obj.messages, obj.msgList, obj.m_msgList }}
    for _li = 1, 4 do
        local lst = lists[_li]
        if type(lst) == "table" then
            local n = #lst
            local startIdx = n > 3 and (n - 2) or 1
            for _i = startIdx, n do
                _hzTryAutoTranslateMsg(tm, lst[_i])
            end
        end
    end
end

local function _hzPostHandleMessage(cmSelf, a1, a2, a3)
    local cfg = _G.__HEINZ_TRANSLATOR_CFG__
    if not cfg or not cfg.enabled or not cfg.auto then return end
    local tm = cmSelf and (cmSelf.Translate or cmSelf.translateManager)
    if not tm or type(tm.DoTranslate) ~= "function" then return end
    _hzScanCandidate(tm, a1)
    _hzScanCandidate(tm, a2)
    _hzScanCandidate(tm, a3)
    local rm = cmSelf.Room or cmSelf.RoomManager
    if type(rm) == "table" then
        local rooms = rm.rooms or rm.m_rooms or rm.roomMap
        if type(rooms) == "table" then
            for _, room in pairs(rooms) do
                _hzScanCandidate(tm, room)
            end
        else
            _hzScanCandidate(tm, rm)
        end
    end
end

local cm = _G.ChatManager2 and _G.ChatManager2.Instance
local tm = cm and (cm.Translate or cm.translateManager)

if tm and type(tm.GetLangString) == "function" and tm.GetLangString ~= _G.__HEINZ_GETLANG_WRAPPER__ then
    local _origGetLang = tm.GetLangString
    local function _wrappedGetLang(self, ...)
        local cfg = _G.__HEINZ_TRANSLATOR_CFG__
        if cfg and cfg.enabled and type(cfg.target) == "string" and cfg.target ~= "" and cfg.target ~= "auto" then
            return cfg.target
        end
        return _origGetLang(self, ...)
    end
    tm.GetLangString = _wrappedGetLang
    _G.__HEINZ_GETLANG_WRAPPER__ = _wrappedGetLang
end

if _hzAuto and cm and type(cm.OnHandleMessage) == "function" and cm.OnHandleMessage ~= _G.__HEINZ_ONHANDLE_WRAPPER__ then
    local _origOnHandle = cm.OnHandleMessage
    local function _wrappedOnHandle(self, a1, a2, a3, ...)
        local r1, r2, r3 = _origOnHandle(self, a1, a2, a3, ...)
        pcall(_hzPostHandleMessage, self, a1, a2, a3)
        return r1, r2, r3
    end
    cm.OnHandleMessage = _wrappedOnHandle
    _G.__HEINZ_ONHANDLE_WRAPPER__ = _wrappedOnHandle
end

return "TRANSLATOR_HOOK_ENABLED:" .. tostring(_hzPort) .. ":" .. tostring(_hzTarget)
""".strip()


# ---------------------------------------------------------------------------
# Threaded Local HTTP Server
# ---------------------------------------------------------------------------

def _parse_multipart_form(body: bytes, content_type: str) -> dict[str, str]:
    header = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("latin-1", errors="ignore")
    msg = BytesParser(policy=email_default_policy).parsebytes(header + body)
    out: dict[str, str] = {}
    if msg.is_multipart():
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if not name:
                continue
            payload = part.get_payload(decode=True)
            if payload is not None:
                out[str(name)] = payload.decode("utf-8", errors="replace")
            else:
                out[str(name)] = str(part.get_payload() or "")
    return out


class _TranslatorHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_cls: type[BaseHTTPRequestHandler],
        *,
        cache: TranslationCache,
        stats: TranslatorStats,
        config_path: Path | None = None,
    ) -> None:
        self.translator_cache = cache
        self.translator_stats = stats
        self.config_path = config_path
        super().__init__(server_address, handler_cls)


class _TranslatorRequestHandler(BaseHTTPRequestHandler):
    server: _TranslatorHTTPServer  # type: ignore[assignment]

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _read_request_params(self) -> dict[str, str]:
        parsed = urllib.parse.urlsplit(self.path)
        params: dict[str, str] = {}
        for k, vals in urllib.parse.parse_qs(parsed.query, keep_blank_values=True).items():
            if vals:
                params[k] = vals[-1]

        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return params
        body = self.rfile.read(min(length, 2 * 1024 * 1024))
        ctype = str(self.headers.get("Content-Type") or "").strip()
        ctype_low = ctype.lower()

        if "application/json" in ctype_low:
            try:
                obj = json.loads(body.decode("utf-8", errors="replace"))
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        params[str(k)] = "" if v is None else str(v)
            except Exception:
                pass
        elif "multipart/form-data" in ctype_low:
            try:
                params.update(_parse_multipart_form(body, ctype))
            except Exception:
                pass
        else:
            decoded = body.decode("utf-8", errors="replace")
            if decoded.lstrip().startswith("{"):
                try:
                    obj = json.loads(decoded)
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            params[str(k)] = "" if v is None else str(v)
                        return params
                except Exception:
                    pass
            for k, vals in urllib.parse.parse_qs(decoded, keep_blank_values=True).items():
                if vals:
                    params[k] = vals[-1]
        return params

    def _handle_client_php(self) -> None:
        params = self._read_request_params()
        cfg = load_translator_config(self.server.config_path)
        src_text = params.get("sc", "")
        raw_tf = params.get("tf", "").strip()
        raw_sf = params.get("sf", "").strip()

        cfg_tl = str(cfg.get("target_lang") or "auto").strip()
        if cfg_tl and cfg_tl.lower() != "auto":
            effective_tl = normalize_lang_code(cfg_tl, default="en")
        else:
            effective_tl = normalize_lang_code(raw_tf, default="en")

        result = translate_text(
            src_text,
            target_lang=effective_tl,
            source_lang=raw_sf,
            config=cfg,
            cache=self.server.translator_cache,
            stats=self.server.translator_stats,
            extra_fields=params,
        )
        # Echo Last Z's requested tf when present (or normalized target) so game callbacks match verbatim.
        response_tf = raw_tf if raw_tf else result["targetLang"]
        self._send_json(
            200,
            {
                "code": 0,
                "originalLang": result["originalLang"],
                "targetLang": response_tf,
                "translateMsg": result["translateMsg"],
            },
        )

    def do_GET(self) -> None:
        route = urllib.parse.urlsplit(self.path).path.rstrip("/") or "/"
        if route == "/health":
            cfg = load_translator_config(self.server.config_path)
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "heinz_live_translator",
                    "port": int(self.server.server_address[1]),
                    "enabled": bool(cfg.get("enabled", True)),
                    "auto_translate_chat": bool(cfg.get("auto_translate_chat", True)),
                    "target_lang": str(cfg.get("target_lang") or "auto"),
                },
            )
            return
        if route == "/stats":
            self._send_json(200, self.server.translator_stats.snapshot())
            return
        if route == "/client.php":
            self._handle_client_php()
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        route = urllib.parse.urlsplit(self.path).path.rstrip("/") or "/"
        if route == "/client.php":
            self._handle_client_php()
            return
        if route == "/translate":
            params = self._read_request_params()
            cfg = load_translator_config(self.server.config_path)
            text = params.get("text", params.get("sc", ""))
            tl = params.get("target_lang", params.get("tf", "")) or str(cfg.get("target_lang") or "en")
            if tl.lower() == "auto":
                tl = "en"
            sl = params.get("source_lang", params.get("sf", ""))
            result = translate_text(
                text,
                target_lang=tl,
                source_lang=sl,
                config=cfg,
                cache=self.server.translator_cache,
                stats=self.server.translator_stats,
            )
            self._send_json(200, {"ok": True, **result})
            return
        self._send_json(404, {"ok": False, "error": "not_found"})


class LiveTranslatorServer:
    """Self-contained local translator HTTP server instance (suitable for daemon, Hub, or isolated tests)."""

    def __init__(
        self,
        *,
        host: str = DEFAULT_HOST,
        port: int | None = None,
        cache: TranslationCache | None = None,
        stats: TranslatorStats | None = None,
        config_path: Path | None = None,
        bridge_path: Path | None = None,
        write_bridge: bool = True,
    ) -> None:
        self.host = host
        self._requested_port = port
        self._cache = cache
        self._owns_cache = cache is None
        self.stats = stats if stats is not None else TranslatorStats()
        self.config_path = config_path
        self.bridge_path = bridge_path
        self.write_bridge = write_bridge
        self._lock = threading.Lock()
        self._httpd: _TranslatorHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port: int = 0
        self.started_at: float = 0.0

    @property
    def is_running(self) -> bool:
        return self._httpd is not None and self._thread is not None and self._thread.is_alive()

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/client.php" if self.port else ""

    def start(self) -> dict[str, Any]:
        with self._lock:
            if self.is_running:
                return self.info()

            active_cache = self._cache if self._cache is not None else _get_global_cache()
            if self._requested_port is not None:
                candidate_ports = [int(self._requested_port)]
            else:
                candidate_ports = list(range(DEFAULT_PORT, PORT_FALLBACK_END + 1))

            last_exc: Exception | None = None
            httpd: _TranslatorHTTPServer | None = None
            for cand in candidate_ports:
                try:
                    httpd = _TranslatorHTTPServer(
                        (self.host, cand),
                        _TranslatorRequestHandler,
                        cache=active_cache,
                        stats=self.stats,
                        config_path=self.config_path,
                    )
                    break
                except OSError as exc:
                    last_exc = exc

            if httpd is None:
                raise RuntimeError(
                    f"Could not bind live translator HTTP server on {self.host}:{candidate_ports}: {last_exc}"
                )

            self._httpd = httpd
            self.port = int(httpd.server_address[1])
            self.started_at = time.time()
            self._thread = threading.Thread(
                target=httpd.serve_forever,
                kwargs={"poll_interval": 0.25},
                name=f"HeinZLiveTranslator-{self.port}",
                daemon=True,
            )
            self._thread.start()
            if self.write_bridge:
                self._write_bridge_file(running=True)
            return self.info()

    def stop(self) -> None:
        with self._lock:
            httpd = self._httpd
            thread = self._thread
            self._httpd = None
            self._thread = None
            if httpd is not None:
                try:
                    httpd.shutdown()
                except Exception:
                    pass
                try:
                    httpd.server_close()
                except Exception:
                    pass
            if thread is not None and thread.is_alive():
                thread.join(timeout=2.0)
            if self.write_bridge:
                self._write_bridge_file(running=False)

    def info(self) -> dict[str, Any]:
        return {
            "running": self.is_running,
            "host": self.host,
            "port": self.port,
            "url": f"http://{self.host}:{self.port}/client.php" if self.port else "",
            "health_url": f"http://{self.host}:{self.port}/health" if self.port else "",
            "stats_url": f"http://{self.host}:{self.port}/stats" if self.port else "",
            "pid": os.getpid(),
            "started_at": round(self.started_at, 3),
        }

    def _write_bridge_file(self, *, running: bool) -> None:
        bpath = self.bridge_path if self.bridge_path is not None else get_bridge_path()
        payload = self.info()
        payload["running"] = bool(running)
        try:
            _atomic_write_json(bpath, payload)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Module-level server lifecycle & multi-process bridge reuse
# ---------------------------------------------------------------------------

_SERVER_LOCK = threading.Lock()
_GLOBAL_SERVER: LiveTranslatorServer | None = None
_EXTERNAL_BRIDGE_PORT: int | None = None


def _probe_external_translator(port: int, timeout: float = 0.4) -> dict[str, Any] | None:
    if port <= 0:
        return None
    try:
        data = _http_request_json(f"http://{DEFAULT_HOST}:{port}/health", timeout=timeout)
        if isinstance(data, dict) and data.get("ok") and data.get("service") == "heinz_live_translator":
            return data
    except Exception:
        return None
    return None


def _read_bridge_port() -> int:
    bpath = get_bridge_path()
    try:
        with open(bpath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and data.get("running"):
            return int(data.get("port") or 0)
    except Exception:
        pass
    return 0


def start_server(
    port: int | None = None,
    host: str = DEFAULT_HOST,
    *,
    write_bridge: bool = True,
    cache: TranslationCache | None = None,
) -> dict[str, Any]:
    """Start the module-level local live translator server if not already running."""
    global _GLOBAL_SERVER, _EXTERNAL_BRIDGE_PORT
    with _SERVER_LOCK:
        if _GLOBAL_SERVER is not None and _GLOBAL_SERVER.is_running:
            return _GLOBAL_SERVER.info()
        srv = LiveTranslatorServer(
            host=host,
            port=port,
            cache=cache if cache is not None else _get_global_cache(),
            stats=_GLOBAL_STATS,
            write_bridge=write_bridge,
        )
        info = srv.start()
        _GLOBAL_SERVER = srv
        _EXTERNAL_BRIDGE_PORT = None
        return info


def stop_server() -> None:
    """Gracefully stop the module-level local live translator server."""
    global _GLOBAL_SERVER, _EXTERNAL_BRIDGE_PORT
    with _SERVER_LOCK:
        srv = _GLOBAL_SERVER
        _GLOBAL_SERVER = None
        _EXTERNAL_BRIDGE_PORT = None
    if srv is not None:
        srv.stop()


def ensure_server_running(port: int | None = None) -> dict[str, Any]:
    """Ensure a local translator server is active (reusing healthy sibling process or starting local)."""
    global _EXTERNAL_BRIDGE_PORT
    with _SERVER_LOCK:
        if _GLOBAL_SERVER is not None and _GLOBAL_SERVER.is_running:
            return _GLOBAL_SERVER.info()

        # Check if another HeinZ process (e.g. daemon or Hub) already owns the bridge port
        if port is None:
            candidate_ports: list[int] = []
            bp = _read_bridge_port()
            if bp > 0:
                candidate_ports.append(bp)
            if DEFAULT_PORT not in candidate_ports:
                candidate_ports.append(DEFAULT_PORT)
            for cand in candidate_ports:
                probe = _probe_external_translator(cand, timeout=0.35)
                if probe is not None:
                    _EXTERNAL_BRIDGE_PORT = cand
                    return {
                        "running": True,
                        "external": True,
                        "host": DEFAULT_HOST,
                        "port": cand,
                        "url": f"http://{DEFAULT_HOST}:{cand}/client.php",
                        "health_url": f"http://{DEFAULT_HOST}:{cand}/health",
                        "stats_url": f"http://{DEFAULT_HOST}:{cand}/stats",
                    }

    return start_server(port=port)


def get_stats() -> dict[str, Any]:
    """Return live translator metrics (querying external owner process if active)."""
    with _SERVER_LOCK:
        in_proc = _GLOBAL_SERVER is not None and _GLOBAL_SERVER.is_running
        ext_port = _EXTERNAL_BRIDGE_PORT
    if in_proc:
        return _GLOBAL_STATS.snapshot()
    if ext_port:
        try:
            remote = _http_request_json(f"http://{DEFAULT_HOST}:{ext_port}/stats", timeout=0.6)
            if isinstance(remote, dict) and remote.get("ok"):
                return remote
        except Exception:
            pass
    return _GLOBAL_STATS.snapshot()


atexit.register(stop_server)


def main() -> int:
    info = ensure_server_running()
    print(json.dumps(info, indent=2), flush=True)
    if "--serve" in sys.argv:
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            stop_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
