#!/usr/bin/env python3
"""
init_mission_ledger.py — Create or update a product-track mission ledger.

Usage:
  python tools/supervisor/init_mission_ledger.py \
    --mission-id MACH-LIF-FORENSICS-20260623 \
    --plan-path C:/Users/prora/.claude/plans/agile-munching-quasar.md \
    [--output .local/supervisor/product-mission-ledger.json] \
    [--set-complete]

Created: 2026-06-23
Task: TC-LIF-005 (agile-munching-quasar)
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_OUTPUT = ".local/supervisor/product-mission-ledger.json"
_SCHEMA_VERSION = "1.0"


def init_ledger(mission_id: str, plan_path: str, output_path: str, repo_root=None) -> dict:
    """Initialize a new mission ledger. Idempotent: skips creation if already exists."""
    root = Path(repo_root) if repo_root else Path(__file__).parent.parent.parent
    out = root / output_path
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        print(f"Ledger already exists: {out}")
        return json.loads(out.read_text(encoding="utf-8"))
    ledger = {
        "schema_version": _SCHEMA_VERSION,
        "mission_id": mission_id,
        "mission_type": "machinery_hardening",
        "authoritative_plan": plan_path,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "current_stage": "EXECUTION_REQUIRED",
        "gaps": [],
        "closed_gaps": [],
        "stop_status": "EXECUTION_REQUIRED",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(f"Created: {out}")
    return ledger


def update_ledger(output_path: str, repo_root=None, **updates) -> dict | None:
    """Update fields in an existing ledger."""
    root = Path(repo_root) if repo_root else Path(__file__).parent.parent.parent
    out = root / output_path
    if not out.exists():
        print(f"Ledger not found: {out}", file=sys.stderr)
        return None
    ledger = json.loads(out.read_text(encoding="utf-8"))
    ledger.update(updates)
    ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
    out.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    return ledger


def main(argv=None):
    p = argparse.ArgumentParser(description="Create or update a product-track mission ledger")
    p.add_argument("--mission-id", required=True, help="Mission identifier")
    p.add_argument("--plan-path", required=True, help="Path to the authoritative plan file")
    p.add_argument("--output", default=_DEFAULT_OUTPUT, help="Output path (relative to repo root)")
    p.add_argument("--repo-root", default=None, help="Repository root (default: auto-detected)")
    p.add_argument("--set-complete", action="store_true", help="Mark mission as MISSION_COMPLETE")
    args = p.parse_args(argv)

    ledger = init_ledger(args.mission_id, args.plan_path, args.output, args.repo_root)
    if args.set_complete:
        ledger = update_ledger(
            args.output,
            args.repo_root,
            stop_status="MISSION_COMPLETE",
            current_stage="MISSION_COMPLETE",
            gaps=[],
        )
    print(json.dumps(ledger, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
