"""
lane_select.py -- Command: /lane-select

Entry point for lane selection command.

ALLOWED: argument parsing, selector integration, validation output
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
        prog="lane-select",
        description="Lane selection command",
    )
    parser.add_argument("format", nargs="?", default="all",
                        help="Format ID or 'all'")
    parser.add_argument("--json", action="store_true")
    parsed = parser.parse_args(args)

    from lane_selector import select_lanes_for_format
    formats = ["fods", "fodt"] if parsed.format == "all" else [parsed.format.lower()]

    for fmt in formats:
        result = select_lanes_for_format(fmt)
        if parsed.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n=== Lane Selection: {fmt.upper()} ===")
            print(f"  REQUIREMENTS_STATE: {result['requirements_state']}")
            print(f"  SELECTED: {result['selected_lanes']}")
            print(f"  BLOCKED:  {result['blocked_lanes']}")
            print(f"  COMMERCIAL_READY: {result['governance']['commercial_product_ready']}")


if __name__ == "__main__":
    run()
