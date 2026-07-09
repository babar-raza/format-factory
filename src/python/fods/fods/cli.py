"""CLI entry point for Format Factory FODS (Flat OpenDocument Spreadsheet).

Usage:
    ff-fods [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-fods command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-fods FILE.fods")
        print("       Inspect a Flat OpenDocument Spreadsheet file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from fods import parse_fods_strict

    try:
        model = parse_fods_strict(path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File:        {path}")
    print(f"Sheet count: {model.get('sheet_count', 0)}")
    for sheet in model.get("sheets", []):
        rows = sheet.get("rows", [])
        print(f"  Sheet {sheet['name']!r}: {len(rows)} row(s)")


if __name__ == "__main__":
    main()
