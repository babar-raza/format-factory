"""CLI entry point for Format Factory ZST (.zst files).

Usage:
    ff-zst [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-zst command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-zst FILE.zst")
        print("       Inspect a ZST file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from zst import decompress_bytes

    try:
        data = Path(path).read_bytes()
        decompressed = decompress_bytes(data)
        print(f"Compressed size:   {len(data)} bytes")
        print(f"Decompressed size: {len(decompressed)} bytes")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
