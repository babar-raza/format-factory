"""Coordination DB access: WAL SQLite, atomic transactions, unified audit.

- BEGIN IMMEDIATE (not EXCLUSIVE) so WAL readers stay unblocked while
  check-then-insert passes are made atomic; 3x jittered retry on busy.
- Malformed rows are quarantined, never silently repaired.
- All ordering guarantees come from rowids; expiry comparisons happen inside
  SQLite with a fixed grace window (single evaluating clock, skew-tolerant).
"""
from __future__ import annotations

import json
import random
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from . import PROTOCOL_VERSION
from .ids import iso
from .root import db_path, resolve_coordination_root

BUSY_TIMEOUT_MS = 5000
RETRIES = 3
# Grace added to every TTL comparison (writer clock skew tolerance).
EXPIRY_GRACE_S = 120

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

NowFn = Callable[[], str]


def default_now() -> str:
    return iso()


def connect(root: Path | None = None) -> sqlite3.Connection:
    path = db_path(root)
    conn = sqlite3.connect(str(path), timeout=BUSY_TIMEOUT_MS / 1000.0)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
        conn.execute("PRAGMA foreign_keys=ON")
    except Exception:
        # Close on failure: a leaked half-open handle keeps the file locked
        # on Windows and blocks the doctor's corrupt-db rename.
        conn.close()
        raise
    return conn


def ensure_db(root: Path | None = None) -> Path:
    root = root or resolve_coordination_root()
    root.mkdir(parents=True, exist_ok=True)
    (root / "runtime").mkdir(exist_ok=True)
    (root / "runtime" / "by-session").mkdir(exist_ok=True)
    conn = connect(root)
    try:
        conn.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT OR IGNORE INTO schema_meta(key, value) VALUES('protocol_version', ?)",
            (str(PROTOCOL_VERSION),),
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES('mode', 'advisory')"
        )
        conn.commit()
    finally:
        conn.close()
    return root


@contextmanager
def immediate(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Atomic check-then-write section. Retries BEGIN on busy/locked."""
    last_err: Exception | None = None
    for attempt in range(RETRIES):
        try:
            conn.execute("BEGIN IMMEDIATE")
            break
        except sqlite3.OperationalError as exc:  # busy / locked
            last_err = exc
            time.sleep(0.05 + random.random() * 0.2)
    else:
        raise sqlite3.OperationalError(
            f"could not begin immediate transaction after {RETRIES} tries"
        ) from last_err
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def emit_event(conn: sqlite3.Connection, entity_type: str, entity_id: str,
               verb: str, *, from_status: str | None = None,
               to_status: str | None = None, actor: str | None = None,
               detail: Any = None, now_fn: NowFn = default_now) -> None:
    conn.execute(
        "INSERT INTO coordination_events(entity_type, entity_id, from_status,"
        " to_status, actor_agent_id, verb, detail, occurred_at)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (entity_type, entity_id, from_status, to_status, actor, verb,
         json.dumps(detail, default=str) if detail is not None else None,
         now_fn()),
    )


def quarantine_row(conn: sqlite3.Connection, source_table: str, row: Any,
                   reason: str, now_fn: NowFn = default_now) -> None:
    try:
        row_json = json.dumps(dict(row), default=str)
    except (TypeError, ValueError):
        row_json = json.dumps({"repr": repr(row)})
    conn.execute(
        "INSERT INTO quarantined_rows(source_table, row_json, reason, quarantined_at)"
        " VALUES(?,?,?,?)",
        (source_table, row_json, reason, now_fn()),
    )


def get_setting(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def get_mode(conn: sqlite3.Connection) -> str:
    mode = get_setting(conn, "mode", "advisory")
    return mode if mode in ("off", "advisory", "enforcing") else "advisory"


def set_mode(conn: sqlite3.Connection, mode: str, actor: str, reason: str,
             now_fn: NowFn = default_now) -> None:
    if mode not in ("off", "advisory", "enforcing"):
        raise ValueError(f"invalid mode: {mode}")
    with immediate(conn):
        old = get_mode(conn)
        conn.execute(
            "INSERT INTO settings(key, value) VALUES('mode', ?)"
            " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (mode,),
        )
        emit_event(conn, "system", "mode", "MODE_CHANGE", from_status=old,
                   to_status=mode, actor=actor, detail={"reason": reason},
                   now_fn=now_fn)


# ---------------------------------------------------------------------------
# SFC-GAP-C (2026-07-17): per-check mode granularity.
#
# The global `mode` above is a single dial shared by every PreToolUse check —
# adding a NEW check under it would inherit the blast radius of the already-
# `enforcing`, already-proven coordination checks on day one, with no way to
# roll it out independently. `check_mode:<check_id>` settings rows give each
# NEW check its own advisory/enforcing state. LOAD-BEARING INVARIANT (enforced
# by callers, e.g. hooks/skill_gate.py): the existing global `mode` gate is
# always computed FIRST and is NEVER weakened by a per-check setting — a
# check's own `advisory` state can only ever be MORE permissive than an
# already-`enforcing` global mode, never override it downward. `off` globally
# still means "skip everything," including any per-check state.
# ---------------------------------------------------------------------------

_CHECK_MODE_PREFIX = "check_mode:"


def get_check_mode(conn: sqlite3.Connection, check_id: str) -> str:
    """Per-check advisory/enforcing state. Defaults to 'advisory' — a NEW
    check must be explicitly promoted; it never inherits 'enforcing' silently."""
    mode = get_setting(conn, _CHECK_MODE_PREFIX + check_id, "advisory")
    return mode if mode in ("advisory", "enforcing") else "advisory"


def set_check_mode(conn: sqlite3.Connection, check_id: str, mode: str,
                   actor: str, reason: str, now_fn: NowFn = default_now) -> None:
    if mode not in ("advisory", "enforcing"):
        raise ValueError(f"invalid check mode: {mode}")
    key = _CHECK_MODE_PREFIX + check_id
    with immediate(conn):
        old = get_check_mode(conn, check_id)
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, mode),
        )
        emit_event(conn, "system", f"check_mode:{check_id}", "CHECK_MODE_CHANGE",
                   from_status=old, to_status=mode, actor=actor,
                   detail={"reason": reason, "check_id": check_id}, now_fn=now_fn)


# ---------------------------------------------------------------------------
# Path-scoped check mode: the policy's own remediation plan for EP-010-GAP
# ("promote check_mode:skill_resolution to enforcing per path-scope, smallest
# blast radius first -- tools/governance/** before src/**") assumed this was
# already possible. It wasn't: the flat `check_mode:<check_id>` key above is a
# single global on/off per check, with no path concept anywhere. Promoting the
# bare global key today would flip every path that check governs at once --
# exactly the repo-wide-freeze risk a staged rollout exists to avoid.
#
# `check_mode:<check_id>:<path_prefix>` rows layer on top, additively (no
# migration -- `settings` is a plain key-value table). Longest-matching
# configured prefix wins; unmatched paths fall back to the bare global key,
# which itself still defaults to 'advisory' per get_check_mode() above.
# ---------------------------------------------------------------------------


def _norm_prefix(path_prefix: str) -> str:
    return path_prefix.replace("\\", "/").strip("/")


def _scoped_check_mode_prefixes(conn: sqlite3.Connection, check_id: str) -> list[str]:
    """Every configured path-prefix scope for this check, longest first."""
    key_prefix = f"{_CHECK_MODE_PREFIX}{check_id}:"
    rows = conn.execute(
        "SELECT key FROM settings WHERE key LIKE ? ESCAPE '\\'",
        (key_prefix.replace("_", "\\_").replace("%", "\\%") + "%",),
    ).fetchall()
    prefixes = [r["key"][len(key_prefix):] for r in rows]
    return sorted(prefixes, key=len, reverse=True)


def get_check_mode_for_path(conn: sqlite3.Connection, check_id: str,
                            rel_path: str) -> str:
    """Per-check, per-path-scope advisory/enforcing state. The longest
    configured path-prefix scope covering rel_path wins; if none match, falls
    back to the bare global check_id key (get_check_mode); defaults to
    'advisory' at every level -- a NEW scope must be explicitly promoted, it
    never inherits 'enforcing' from a broader or sibling scope."""
    norm = _norm_prefix(rel_path)
    for prefix in _scoped_check_mode_prefixes(conn, check_id):
        if norm == prefix or norm.startswith(prefix + "/"):
            mode = get_setting(conn, f"{_CHECK_MODE_PREFIX}{check_id}:{prefix}",
                               "advisory")
            return mode if mode in ("advisory", "enforcing") else "advisory"
    return get_check_mode(conn, check_id)


def set_check_mode_for_path(conn: sqlite3.Connection, check_id: str,
                            path_prefix: str, mode: str, actor: str, reason: str,
                            now_fn: NowFn = default_now) -> None:
    if mode not in ("advisory", "enforcing"):
        raise ValueError(f"invalid check mode: {mode}")
    norm = _norm_prefix(path_prefix)
    if not norm:
        raise ValueError("path_prefix must be non-empty")
    key = f"{_CHECK_MODE_PREFIX}{check_id}:{norm}"
    with immediate(conn):
        old = get_setting(conn, key, "advisory")
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, mode),
        )
        emit_event(conn, "system", f"check_mode:{check_id}:{norm}",
                   "CHECK_MODE_CHANGE", from_status=old, to_status=mode,
                   actor=actor,
                   detail={"reason": reason, "check_id": check_id,
                           "path_prefix": norm}, now_fn=now_fn)


# SQL fragment: seconds elapsed since a stored ISO timestamp, evaluated
# against a single caller-supplied "as-of" instant (bind one `?` per use).
# One evaluating clock for all rows -> row-writer clock skew is tolerated via
# the grace window; tests inject a future instant instead of sleeping.
AGE_SECONDS_SQL = "(julianday(?) - julianday({col})) * 86400.0"


def expired_predicate(col: str, ttl_col: str) -> str:
    """Predicate with ONE positional `?` (the as-of ISO timestamp)."""
    return f"{AGE_SECONDS_SQL.format(col=col)} > ({ttl_col} + {EXPIRY_GRACE_S})"
