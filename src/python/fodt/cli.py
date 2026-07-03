"""CLI entry point for Format Factory FODT (Flat OpenDocument Text).

Usage:
    ff-fodt [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ff-fodt command-line tool."""
    if len(sys.argv) < 2:
        print("Usage: ff-fodt FILE.fodt")
        print("       Inspect a Flat OpenDocument Text file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from fodt import parse_fodt_strict, document_text_content

    try:
        model = parse_fodt_strict(path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    blocks = model.get("blocks", [])
    text = document_text_content(model)
    print(f"File:        {path}")
    print(f"Block count: {len(blocks)}")
    print(f"Text length: {len(text)} chars")
    if text:
        preview = text[:200].replace("\n", " ")
        print(f"Preview:     {preview}{'...' if len(text) > 200 else ''}")


if __name__ == "__main__":
    main()
