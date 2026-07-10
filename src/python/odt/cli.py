"""CLI entry point for Format Factory ODT (.odt files).

Usage:
    ff-odt [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-odt command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-odt FILE.odt")
        print("       Inspect a ODT file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from odt import parse_odt

    try:
        doc = parse_odt(path)
        pcount = doc.get('paragraph_count', 0)
        print(f"Paragraphs: {pcount}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
