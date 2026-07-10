"""CLI entry point for Format Factory PPM (.ppm files).

Usage:
    ff-ppm [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-ppm command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-ppm FILE.ppm")
        print("       Inspect a PPM file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from ppm import parse_ppm

    try:
        img = parse_ppm(path)
        print(f"Width:  {img.width}")
        print(f"Height: {img.height}")
        print(f"Max val: {img.max_val}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
