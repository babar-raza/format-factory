"""CLI entry point for Format Factory XCF (.xcf files).

Usage:
    ff-xcf [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-xcf command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-xcf FILE.xcf")
        print("       Inspect a XCF file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from xcf import parse_xcf, xcf_layer_name_list

    try:
        img = parse_xcf(path)
        layers = xcf_layer_name_list(img)
        print(f"Width:  {img.width}")
        print(f"Height: {img.height}")
        print(f"Layers: {layers}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
