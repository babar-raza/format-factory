"""
delegation_gate.py — Check whether all delegated gaps for a plan have been resolved.

A plan calls this before proceeding past any step that depends on delegated work
being complete. This is the "wait for supervisor" primitive.

Reads from reports/governance/delegation-ledger.json (NOT gap-ledger.json —
see F-001: product gap-ledger has incompatible schema).

Usage:
  python tools/supervisor/delegation_gate.py --plan-id sequential-twirling-sunrise

  # Check specific gaps only:
  python tools/supervisor/delegation_gate.py \\
    --plan-id sequential-twirling-sunrise \\
    --gap-ids GAP-LANE5-001 GAP-LANE5-002

Exit codes:
  0 = GATE OPEN — all delegations for this plan are closed (or no delegations registered)
  1 = GATE CLOSED — one or more delegations are still open/pending
  2 = NO DELEGATIONS FOUND — plan has no registered delegations (warning, then proceed)

Integration in a plan taskcard:
  python tools/supervisor/delegation_gate.py --plan-id <id>
  If exit 1: STOP. Supervisor has not completed delegated work yet.
  If exit 0: Proceed to next step.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent
_default_ledger = _repo_root / "reports" / "governance" / "delegation-ledger.json"


def check_gate(
    plan_id: str,
    gap_ids: list[str] | None = None,
    ledger_path: Path | None = None,
) -> tuple[int, list[dict], list[dict]]:
    """Check delegation gate for a plan.

    Returns (exit_code, open_delegations, closed_delegations).

    Exit codes:
      0 = GATE OPEN
      1 = GATE CLOSED
      2 = NO DELEGATIONS FOUND
    """
    ledger_path = ledger_path or _default_ledger

    if not ledger_path.exists():
        return 2, [], []

    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: could not read delegation-ledger.json: {exc}", file=sys.stderr)
        return 1, [], []

    all_delegations = data.get("delegations", [])

    # Filter by plan_id
    plan_delegations = [d for d in all_delegations if d.get("plan_id") == plan_id]

    if not plan_delegations:
        return 2, [], []

    # Filter by specific gap_ids if provided
    if gap_ids:
        plan_delegations = [d for d in plan_delegations if d.get("gap_id") in gap_ids]
        if not plan_delegations:
            return 2, [], []

    open_delegations = [d for d in plan_delegations if d.get("status") != "closed"]
    closed_delegations = [d for d in plan_delegations if d.get("status") == "closed"]

    if open_delegations:
        return 1, open_delegations, closed_delegations
    return 0, [], closed_delegations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check whether all delegated gaps for a plan have been resolved"
    )
    parser.add_argument("--plan-id", required=True, help="Plan ID to check delegations for")
    parser.add_argument("--gap-ids", nargs="+", default=None,
                        help="Specific gap IDs to check (default: check all for plan)")
    parser.add_argument("--ledger", default=None,
                        help=f"Path to delegation-ledger.json (default: {_default_ledger})")
    args = parser.parse_args(argv)

    ledger_path = Path(args.ledger) if args.ledger else _default_ledger
    exit_code, open_delegations, closed_delegations = check_gate(
        plan_id=args.plan_id,
        gap_ids=args.gap_ids,
        ledger_path=ledger_path,
    )

    if exit_code == 2:
        print(f"[delegation_gate] NO DELEGATIONS FOUND for plan '{args.plan_id}'")
        print("[delegation_gate] GATE OPEN (no delegations = nothing to wait for)")
        return 0  # no delegations -> proceed (warn only per Component 4 spec)

    if exit_code == 0:
        print(f"[delegation_gate] GATE OPEN - all {len(closed_delegations)} delegation(s) closed")
        for d in closed_delegations:
            print(f"  CLOSED: {d.get('gap_id')} -> {d.get('target_lane')}")
        return 0

    # exit_code == 1: GATE CLOSED
    print(f"[delegation_gate] GATE CLOSED - {len(open_delegations)} delegation(s) pending")
    for d in open_delegations:
        print(
            f"  PENDING: {d.get('gap_id')} -> {d.get('target_lane')} "
            f"(status={d.get('status')}, severity={d.get('severity')})"
        )
    if closed_delegations:
        print(f"  ({len(closed_delegations)} already closed)")
    print("[delegation_gate] Supervisor must close these delegations before this plan can proceed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
