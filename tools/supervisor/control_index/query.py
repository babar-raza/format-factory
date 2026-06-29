"""Query CLI for the control index.

Usage:
    python -m tools.supervisor.control_index.query search "FODS qname"
    python -m tools.supervisor.control_index.query gaps --format fods --status open
    python -m tools.supervisor.control_index.query failures --unresolved
    python -m tools.supervisor.control_index.query format fods
    python -m tools.supervisor.control_index.query sql "SELECT COUNT(*) FROM gaps"
"""

import argparse
import json
import re
import sys
from pathlib import Path

from . import DEFAULT_DB_PATH
from .db import get_connection


def _json_out(data):
    print(json.dumps(data, indent=2, default=str))


def _table_out(rows: list[dict]):
    if not rows:
        print("(no results)")
        return
    cols = list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r.get(c, "")))[:60] for r in rows)) for c in cols}
    header = " | ".join(c.ljust(widths[c])[:60] for c in cols)
    print(header)
    print("-+-".join("-" * min(widths[c], 60) for c in cols))
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c])[:60] for c in cols))


def cmd_search(args):
    conn = get_connection(Path(args.db_path))
    try:
        from .search import search
        results = search(conn, args.query,
                         entity_types=args.type.split(",") if args.type else None,
                         limit=args.limit)
        if args.table:
            _table_out(results)
        else:
            _json_out(results)
    finally:
        conn.close()


def cmd_gaps(args):
    conn = get_connection(Path(args.db_path))
    try:
        sql = "SELECT gap_id, format, capability_name, status, priority, current_state FROM gaps WHERE 1=1"
        params = []
        if args.format:
            sql += " AND UPPER(format) = UPPER(?)"
            params.append(args.format)
        if args.status:
            sql += " AND LOWER(status) = LOWER(?)"
            params.append(args.status)
        if args.priority:
            sql += " AND priority = ?"
            params.append(args.priority)
        if args.blocks_poc:
            sql += " AND blocks_poc = 1"
        sql += f" ORDER BY gap_id LIMIT {args.limit}"
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        if args.table:
            _table_out(rows)
        else:
            _json_out(rows)
    finally:
        conn.close()


def cmd_sprints(args):
    conn = get_connection(Path(args.db_path))
    try:
        sql = "SELECT sprint_id, verdict, test_count, fail_count, start_time FROM sprints WHERE 1=1"
        params = []
        if args.verdict:
            sql += " AND UPPER(verdict) = UPPER(?)"
            params.append(args.verdict)
        if args.after:
            sql += " AND start_time > ?"
            params.append(args.after)
        sql += f" ORDER BY start_time DESC LIMIT {args.limit}"
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        if args.table:
            _table_out(rows)
        else:
            _json_out(rows)
    finally:
        conn.close()


def cmd_failures(args):
    conn = get_connection(Path(args.db_path))
    try:
        sql = ("SELECT failure_id, category, severity, root_cause, resolved, occurrence_count "
               "FROM failures WHERE 1=1")
        params = []
        if args.unresolved:
            sql += " AND resolved = 0"
        if args.category:
            sql += " AND category = ?"
            params.append(args.category)
        sql += " ORDER BY failure_id"
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        if args.table:
            _table_out(rows)
        else:
            _json_out(rows)
    finally:
        conn.close()


def cmd_plan_locks(args):
    conn = get_connection(Path(args.db_path))
    try:
        sql = "SELECT lock_file, plan_path, status, session_id, track_type FROM plan_locks WHERE 1=1"
        params = []
        if args.status:
            sql += " AND UPPER(status) = UPPER(?)"
            params.append(args.status)
        sql += " ORDER BY updated_at DESC"
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        if args.table:
            _table_out(rows)
        else:
            _json_out(rows)
    finally:
        conn.close()


def cmd_format(args):
    conn = get_connection(Path(args.db_path))
    try:
        fmt = args.format_id.upper()
        # Format info
        fmt_row = conn.execute("SELECT * FROM formats WHERE UPPER(format_id) = ?", (fmt,)).fetchone()
        # Gap summary
        gap_stats = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM gaps WHERE UPPER(format) = ? GROUP BY status",
            (fmt,),
        ).fetchall()
        # QName count
        qname_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM qnames WHERE UPPER(format_id) = ?", (fmt,)
        ).fetchone()

        result = {
            "format": dict(fmt_row) if fmt_row else None,
            "gap_summary": {r["status"]: r["cnt"] for r in gap_stats},
            "qname_count": qname_count["cnt"] if qname_count else 0,
        }
        # Remove raw_json from format to keep output clean
        if result["format"] and "raw_json" in result["format"]:
            del result["format"]["raw_json"]
        _json_out(result)
    finally:
        conn.close()


def cmd_chain(args):
    conn = get_connection(Path(args.db_path))
    try:
        gap_id = args.gap
        # Gap details
        gap = conn.execute("SELECT gap_id, format, capability_name, status, priority FROM gaps WHERE gap_id = ?",
                           (gap_id,)).fetchone()
        # Linked work items
        work_items = conn.execute(
            "SELECT swi.sprint_id, swi.item_id, swi.title, swi.status, s.verdict "
            "FROM sprint_work_items swi "
            "LEFT JOIN sprints s ON swi.sprint_id = s.sprint_id "
            "WHERE swi.gap_ledger_ref = ? "
            "ORDER BY s.start_time DESC",
            (gap_id,),
        ).fetchall()
        # Spec facts
        facts = conn.execute(
            "SELECT spec_fact_ref FROM gap_spec_facts WHERE gap_id = ?", (gap_id,)
        ).fetchall()

        result = {
            "gap": dict(gap) if gap else None,
            "spec_facts": [r["spec_fact_ref"] for r in facts],
            "linked_sprints": [dict(r) for r in work_items],
        }
        _json_out(result)
    finally:
        conn.close()


def cmd_stale(args):
    conn = get_connection(Path(args.db_path))
    try:
        from .staleness import check_staleness
        stale = check_staleness(conn, Path(args.repo_root))
        if args.table:
            _table_out(stale)
        else:
            _json_out(stale)
    finally:
        conn.close()


def cmd_sql(args):
    # Safety: reject write operations
    stmt = args.statement.strip().upper()
    if re.match(r'^\s*(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA)', stmt):
        print(json.dumps({"error": "Write operations not allowed via query CLI"}))
        sys.exit(1)

    conn = get_connection(Path(args.db_path))
    try:
        rows = [dict(r) for r in conn.execute(args.statement).fetchall()]
        if args.table:
            _table_out(rows)
        else:
            _json_out(rows)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(prog="control_index.query")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--table", action="store_true", help="Human-readable table output")

    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p = sub.add_parser("search", help="FTS5 full-text search")
    p.add_argument("query", help="Search query")
    p.add_argument("--type", help="Comma-separated entity types to filter")
    p.add_argument("--limit", type=int, default=20)

    # gaps
    p = sub.add_parser("gaps", help="Query gaps")
    p.add_argument("--format", dest="format")
    p.add_argument("--status")
    p.add_argument("--priority")
    p.add_argument("--blocks-poc", action="store_true")
    p.add_argument("--limit", type=int, default=50)

    # sprints
    p = sub.add_parser("sprints", help="Query sprints")
    p.add_argument("--verdict")
    p.add_argument("--after", help="Only sprints after this ISO timestamp")
    p.add_argument("--limit", type=int, default=20)

    # failures
    p = sub.add_parser("failures", help="Query failures")
    p.add_argument("--unresolved", action="store_true")
    p.add_argument("--category")

    # plan-locks
    p = sub.add_parser("plan-locks", help="Query plan locks")
    p.add_argument("--status")

    # format dashboard
    p = sub.add_parser("format", help="Format dashboard")
    p.add_argument("format_id", help="Format ID (e.g., fods)")

    # chain traversal
    p = sub.add_parser("chain", help="Gap → sprint → evidence chain")
    p.add_argument("--gap", required=True, help="Gap ID")

    # stale check
    sub.add_parser("stale", help="Check for stale sources")

    # raw SQL
    p = sub.add_parser("sql", help="Execute read-only SQL")
    p.add_argument("statement", help="SQL SELECT statement")

    args = parser.parse_args()
    commands = {
        "search": cmd_search,
        "gaps": cmd_gaps,
        "sprints": cmd_sprints,
        "failures": cmd_failures,
        "plan-locks": cmd_plan_locks,
        "format": cmd_format,
        "chain": cmd_chain,
        "stale": cmd_stale,
        "sql": cmd_sql,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
