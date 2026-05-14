"""
format_context.py -- Command: /format-context

Entry point for format context resolution command.

ALLOWED: argument parsing, resolver integration, validation output
NOT ALLOWED: gate approval, source mutation, publishing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


def run(args=None):
    parser = argparse.ArgumentParser(
        prog="format-context",
        description="Format context resolution command",
    )
    parser.add_argument("format", nargs="?", default="all",
                        help="Format ID or 'all'")
    parser.add_argument("--json", action="store_true")
    parsed = parser.parse_args(args)

    from format_context_resolver import resolve_format_context
    formats = ["fods", "fodt"] if parsed.format == "all" else [parsed.format.lower()]

    results = {}
    for fmt in formats:
        ctx = resolve_format_context(fmt)
        results[fmt] = ctx
        if not parsed.json:
            print(f"\n=== Format Context: {fmt.upper()} ===")
            print(f"  REQUIREMENTS_STATE:  {ctx['requirements_state']['status']}")
            print(f"  COMMERCIAL_READY:    {ctx['governance']['commercial_product_ready']}")

    if parsed.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()
