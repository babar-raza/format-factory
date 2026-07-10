"""CLI entry point for Format Factory SYLK (.slk files).

Usage:
    ff-sylk [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-sylk command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-sylk FILE.slk")
        print("       Inspect a SYLK file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from sylk import parse_sylk_strict

    try:
        doc = parse_sylk_strict(path)
        print(f"Rows: {doc.rows}, Cols: {doc.cols}")
        print(f"Cells: {len(doc.cells)}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
