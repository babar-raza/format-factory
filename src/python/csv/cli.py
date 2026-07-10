"""CLI entry point for Format Factory CSV (.csv files).

Usage:
    ff-csv [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-csv command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-csv FILE.csv")
        print("       Inspect a CSV file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from csv import parse_csv_strict

    try:
        doc = parse_csv_strict(path)
        print(f"Rows: {len(doc.rows)}")
        print(f"Headers: {doc.headers}")
        if doc.rows:
            print(f"First row: {doc.rows[0]}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
