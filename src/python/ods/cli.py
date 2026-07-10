"""CLI entry point for Format Factory ODS (.ods files).

Usage:
    ff-ods [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-ods command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-ods FILE.ods")
        print("       Inspect a ODS file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from ods import load_ods

    try:
        doc = load_ods(path)
        sheets = doc.get('sheets', [])
        print(f"Sheets: {len(sheets)}")
        if sheets:
            print(f"First sheet: {sheets[0].get('name', '?')}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
