"""CLI entry point for Format Factory TOML (Tom's Obvious Minimal Language).

Usage:
    ff-toml [FILE]

If FILE is omitted, prints usage and exits.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: ff-toml FILE.toml")
        print("       Inspect a TOML configuration file.")
        sys.exit(0)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    from toml.toml_codec import load_toml, list_sections, count_keys

    try:
        result = load_toml(path)
        sections = list_sections(path)
        total_keys = count_keys(path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"File:       {path}")
    print(f"Sections:   {sections}")
    print(f"Total keys: {total_keys}")
    data = result.get("data", {})
    for sec, val in data.items():
        if isinstance(val, dict):
            print(f"  [{sec}]: {len(val)} key(s)")


if __name__ == "__main__":
    main()
