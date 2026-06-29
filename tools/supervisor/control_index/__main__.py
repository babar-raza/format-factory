"""CLI entry point for the control index.

Usage:
    python -m tools.supervisor.control_index init     # Create/migrate DB
    python -m tools.supervisor.control_index status   # Show DB status
    python -m tools.supervisor.control_index sync     # Incremental sync
    python -m tools.supervisor.control_index rebuild  # Full rebuild
"""

import argparse
import json
import sys
from pathlib import Path

from . import DEFAULT_DB_PATH, SCHEMA_VERSION
from .db import get_schema_version, get_table_names, init_db, ensure_db


def cmd_init(args):
    """Create or reinitialize the database."""
    db_path = Path(args.db_path)
    init_db(db_path)
    from .db import get_connection
    conn = get_connection(db_path)
    try:
        tables = get_table_names(conn)
        version = get_schema_version(db_path)
        print(json.dumps({
            "action": "init",
            "db_path": str(db_path),
            "schema_version": version,
            "table_count": len(tables),
            "tables": tables,
        }, indent=2))
    finally:
        conn.close()


def cmd_status(args):
    """Show database status."""
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(json.dumps({
            "status": "not_initialized",
            "db_path": str(db_path),
        }, indent=2))
        return

    version = get_schema_version(db_path)
    from .db import get_connection
    conn = get_connection(db_path)
    try:
        tables = get_table_names(conn)
        file_size = db_path.stat().st_size

        # Count rows in key tables
        counts = {}
        for table in tables:
            if table.startswith("fts_"):
                continue
            try:
                row = conn.execute(f"SELECT COUNT(*) as c FROM [{table}]").fetchone()
                counts[table] = row["c"]
            except Exception:
                counts[table] = -1

        # Source manifest
        manifest_count = counts.get("source_manifest", 0)

        print(json.dumps({
            "status": "initialized",
            "db_path": str(db_path),
            "file_size_bytes": file_size,
            "schema_version": version,
            "expected_version": SCHEMA_VERSION,
            "table_count": len(tables),
            "row_counts": counts,
            "source_files_tracked": manifest_count,
        }, indent=2))
    finally:
        conn.close()


def cmd_sync(args):
    """Run incremental sync."""
    db_path = Path(args.db_path)
    repo_root = Path(args.repo_root)
    from .sync import sync_all
    report = sync_all(db_path, repo_root, force=args.force)
    print(json.dumps(report.to_dict(), indent=2))


def cmd_rebuild(args):
    """Delete and rebuild the database from scratch."""
    db_path = Path(args.db_path)
    repo_root = Path(args.repo_root)
    from .sync import rebuild
    report = rebuild(db_path, repo_root)
    print(json.dumps(report.to_dict(), indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="control_index",
        description="Operational Control Index — SQLite overlay for Format Factory",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: .)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create or reinitialize the database")
    sub.add_parser("status", help="Show database status")

    sync_p = sub.add_parser("sync", help="Incremental sync from source files")
    sync_p.add_argument("--force", action="store_true", help="Force re-sync all sources")

    sub.add_parser("rebuild", help="Delete and rebuild database from scratch")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "sync": cmd_sync,
        "rebuild": cmd_rebuild,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
