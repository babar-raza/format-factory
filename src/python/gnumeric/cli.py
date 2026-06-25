"""CLI entry point for Format Factory Gnumeric spreadsheet format.

Usage:
    ff-gnumeric [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: ff-gnumeric FILE.gnumeric")
        print("       Inspect a Gnumeric spreadsheet file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from gnumeric import load, get_sheet_names

    try:
        model = load(path)
        sheet_names = get_sheet_names(path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File:        {path}")
    print(f"Sheet count: {model.get('sheet_count', 0)}")
    print(f"Cell count:  {model.get('cell_count', 0)}")
    for name in sheet_names:
        print(f"  Sheet: {name!r}")


if __name__ == "__main__":
    main()
