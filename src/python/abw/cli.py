"""CLI entry point for Format Factory ABW (.abw files).

Usage:
    ff-abw [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-abw command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-abw FILE.abw")
        print("       Inspect a ABW file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from abw import load_abw

    try:
        doc = load_abw(path)
        print(f"Paragraphs: {len(doc.paragraphs)}")
        if doc.paragraphs:
            print(f"First paragraph: {doc.paragraphs[0].text[:80]}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File: {path}")


if __name__ == "__main__":
    main()
