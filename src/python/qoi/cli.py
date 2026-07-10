"""CLI entry point for Format Factory QOI (.qoi files).

Usage:
    ff-qoi [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-qoi command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-qoi FILE.qoi")
        print("       Inspect a QOI file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from qoi import parse_qoi

    try:
        img = parse_qoi(path)
        print(f"Width:   {img.width}")
        print(f"Height:  {img.height}")
        print(f"Channels:{img.channels}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
