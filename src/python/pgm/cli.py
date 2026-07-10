"""CLI entry point for Format Factory PGM (.pgm files).

Usage:
    ff-pgm [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-pgm command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-pgm FILE.pgm")
        print("       Inspect a PGM file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from pgm import parse_pgm

    try:
        img = parse_pgm(path)
        print(f"Width:  {img.width}")
        print(f"Height: {img.height}")
        print(f"Max gray: {img.max_gray}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
