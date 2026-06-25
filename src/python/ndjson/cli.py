"""CLI entry point for Format Factory NDJSON (Newline-Delimited JSON).

Usage:
    ff-ndjson [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: ff-ndjson FILE.ndjson")
        print("       Inspect a Newline-Delimited JSON file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from ndjson import load_ndjson

    try:
        records = load_ndjson(path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File:         {path}")
    print(f"Record count: {len(records)}")
    if records:
        first = records[0]
        keys = list(first.keys()) if isinstance(first, dict) else []
        print(f"First record keys: {keys}")
        print(f"First record: {first}")


if __name__ == "__main__":
    main()
