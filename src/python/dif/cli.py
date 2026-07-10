"""CLI entry point for Format Factory DIF (.dif files).

Usage:
    ff-dif [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-dif command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-dif FILE.dif")
        print("       Inspect a DIF file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from dif import load_dif

    try:
        doc = load_dif(path)
        print(f"Rows: {len(doc.rows)}")
        if doc.rows:
            print(f"First row: {doc.rows[0]}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
