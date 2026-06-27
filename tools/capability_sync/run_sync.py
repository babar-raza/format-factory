"""
run_sync.py — Capability Sync Tool 7/7

Orchestrator for all capability sync steps.

Modes:
  full            Run inventory + validate + update CLAUDE.md + update AGENTS.md + drift check
  validate        Run parity validation only (reads committed registry)
  drift-only      Run drift detection only (read-only)
  inventory-only  Rebuild registry.yaml only
"""
import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def run_inventory() -> int:
    from tools.capability_sync import inventory_capabilities
    return inventory_capabilities.main()


def run_validate() -> int:
    from tools.capability_sync import validate_parity
    _orig = sys.argv[:]
    sys.argv = [sys.argv[0]]
    try:
        return validate_parity.main()
    finally:
        sys.argv = _orig


def run_update_claude() -> int:
    from tools.capability_sync import update_claude_instructions
    return update_claude_instructions.main()


def run_update_agents() -> int:
    from tools.capability_sync import update_agent_instructions
    return update_agent_instructions.main()


def run_drift() -> int:
    from tools.capability_sync import detect_drift
    _orig = sys.argv[:]
    sys.argv = [sys.argv[0]]
    try:
        return detect_drift.main()
    finally:
        sys.argv = _orig


def main() -> int:
    parser = argparse.ArgumentParser(description="Capability sync orchestrator")
    parser.add_argument(
        "--mode",
        choices=["full", "validate", "drift-only", "inventory-only"],
        default="full",
        help="Sync mode (default: full)",
    )
    args = parser.parse_args()

    codes = []

    if args.mode == "inventory-only":
        codes.append(run_inventory())

    elif args.mode == "validate":
        codes.append(run_validate())

    elif args.mode == "drift-only":
        codes.append(run_drift())

    elif args.mode == "full":
        print("=== Step 1/5: Inventory ===")
        codes.append(run_inventory())

        print("\n=== Step 2/5: Parity Validation ===")
        r = run_validate()
        codes.append(0)  # P2 WARN is not fatal for full sync
        if r != 0:
            print(f"  (validate_parity exit {r} — non-fatal in full mode)")

        print("\n=== Step 3/5: Update CLAUDE.md ===")
        codes.append(run_update_claude())

        print("\n=== Step 4/5: Update AGENTS.md ===")
        codes.append(run_update_agents())

        print("\n=== Step 5/5: Drift Check ===")
        codes.append(run_drift())

    overall = max(codes) if codes else 0
    print(f"\n=== Sync complete — exit {overall} ===")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
