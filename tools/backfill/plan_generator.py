"""Backfill plan generator — produces human-readable migration plans from inventory output.

TC-MACH-BACK-001: READ-ONLY tool. Reads backfill inventory output and generates
a migration plan document.

Usage:
    python tools/backfill/plan_generator.py --format fods
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def generate_plan(format_name: str, inventory: dict) -> str:
    """Generate a human-readable migration plan from inventory data."""
    lines = [
        f"# Backfill Migration Plan — {format_name.upper()}",
        f"",
        f"## Summary",
        f"- Classes found: {inventory.get('classes_found', 0)}",
        f"- Migration needed: {inventory.get('migration_needed', 0)}",
        f"- Registry entries: {inventory.get('registry_entries', 0)}",
        f"",
        f"## Classes Requiring Migration",
        f"",
    ]

    migration_classes = [c for c in inventory.get("classes", []) if c.get("migration_required")]

    if not migration_classes:
        lines.append("No classes require migration.")
    else:
        for cls in migration_classes:
            lines.append(f"### {cls['current_name']} -> {cls['canonical_name']}")
            lines.append(f"- **Current file:** {cls['current_file']}")
            lines.append(f"- **spec_qname:** {cls.get('spec_qname', 'N/A')}")
            lines.append(f"- **Registry status:** {cls.get('registry_status', 'unknown')}")
            lines.append(f"- **Compatibility shim needed:** Yes (create Compat/{cls['current_name']}.py)")
            lines.append(f"- **Risk:** Check all imports of {cls['current_name']} across test and source files")
            lines.append(f"")

    lines.append(f"## Non-Migration Classes")
    lines.append(f"")
    for cls in inventory.get("classes", []):
        if not cls.get("migration_required"):
            status = "Compat facade" if cls.get("is_compat") else "spec stub" if cls.get("is_spec") else "production"
            lines.append(f"- {cls['current_name']} ({cls['current_file']}) — {status}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill plan generator")
    parser.add_argument("--format", required=True, help="Format name")
    parser.add_argument("--inventory", default=None, help="Path to inventory JSON/YAML (default: run inventory)")
    args = parser.parse_args()

    if args.inventory:
        inv_path = Path(args.inventory)
        data = json.loads(inv_path.read_text(encoding="utf-8"))
    else:
        from inventory import scan_format
        data = scan_format(args.format)

    if data.get("error"):
        print(f"Error: {data['error']}", file=sys.stderr)
        return 1

    plan = generate_plan(args.format, data)
    print(plan)

    out_path = REPO_ROOT / ".local" / "backfill" / f"{args.format}-migration-plan.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(plan, encoding="utf-8")
    print(f"Plan written to: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
