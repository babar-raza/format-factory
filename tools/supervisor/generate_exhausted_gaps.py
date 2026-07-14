"""Generate exhausted-gaps.json from the control index.

TC-OCRD-B2: CLI entry point for writing exhausted gap IDs to
reports/control-layer/exhausted-gaps.json for human inspection.

Usage:
    python tools/supervisor/generate_exhausted_gaps.py [--max-failed N] [--output PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_HERE))

from control_index import get_connection, DEFAULT_DB_PATH
from control_index.gap_selection import write_exhausted_gaps_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write exhausted gap IDs to JSON")
    parser.add_argument("--max-failed", type=int, default=3,
                        help="Failure threshold (default: 3)")
    parser.add_argument("--output", type=Path,
                        default=_REPO / "reports" / "control-layer" / "exhausted-gaps.json",
                        help="Output file path")
    args = parser.parse_args(argv)

    if not DEFAULT_DB_PATH.exists():
        print(f"ERROR: Control index DB not found: {DEFAULT_DB_PATH}", file=sys.stderr)
        return 1

    conn = get_connection(DEFAULT_DB_PATH)
    try:
        count = write_exhausted_gaps_json(conn, args.output, args.max_failed)
    finally:
        conn.close()

    print(f"Wrote {count} exhausted gap(s) to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
