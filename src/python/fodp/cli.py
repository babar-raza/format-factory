"""CLI entry point for Format Factory FODP (.fodp files).

Usage:
    ff-fodp [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-fodp command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-fodp FILE.fodp")
        print("       Inspect a FODP file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from fodp import load_fodp, get_page_count

    try:
        doc = load_fodp(path)
        count = get_page_count(doc)
        print(f"Pages: {count}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
