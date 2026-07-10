"""CLI entry point for Format Factory PBM (.pbm files).

Usage:
    ff-pbm [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-pbm command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-pbm FILE.pbm")
        print("       Inspect a PBM file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from pbm import parse_pbm

    try:
        img = parse_pbm(path)
        print(f"Width:  {img.width}")
        print(f"Height: {img.height}")
        print(f"Format: {img.format_name}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
