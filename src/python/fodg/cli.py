"""CLI entry point for Format Factory FODG (.fodg files).

Usage:
    ff-fodg [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-fodg command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-fodg FILE.fodg")
        print("       Inspect a FODG file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from fodg import load_fodg

    try:
        doc = load_fodg(path)
        print(f"Shapes: {len(doc.get('shapes', []))}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
