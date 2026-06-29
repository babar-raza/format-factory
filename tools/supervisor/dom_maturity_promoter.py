"""DOM Maturity Promoter — checks contracts and updates ledger maturity.

Promotion is idempotent and cannot exceed ceiling.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"

sys.path.insert(0, str(Path(__file__).parent))
from dom_contract_checker import check_contract

_MATURITY_ORDER = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}


def check_promotion(format_name: str, target_level: str, ledger_path: Path | None = None) -> dict:
    """Check if a format is eligible for promotion to target_level.

    Returns {eligible, passed, failed, evidence_paths}.
    """
    path = ledger_path or DEFAULT_LEDGER
    ledger = yaml.safe_load(path.read_text(encoding="utf-8"))

    entry = next((e for e in ledger if e.get("format") == format_name.lower()
                  and e.get("runtime", "python") == "python"), None)
    if entry is None:
        return {"eligible": False, "error": f"Format '{format_name}' not found in ledger"}

    current = entry.get("lane_b_maturity", "D0")
    ceiling = entry.get("lane_b_ceiling", "D0")
    target_val = _MATURITY_ORDER.get(target_level, 0)
    current_val = _MATURITY_ORDER.get(current, 0)
    ceiling_val = _MATURITY_ORDER.get(ceiling, 0)

    # Already at or above target — idempotent no-op
    if current_val >= target_val:
        return {"eligible": False, "reason": "already_at_or_above_target",
                "current": current, "target": target_level}

    # Cannot promote beyond ceiling
    if target_val > ceiling_val:
        return {"eligible": False, "reason": "exceeds_ceiling",
                "target": target_level, "ceiling": ceiling}

    # Check contract
    contract = check_contract(format_name, target_level)
    passed = [c for c in contract["criteria"] if c["found"]]
    failed = [c for c in contract["criteria"] if not c["found"]]

    return {
        "eligible": contract["passed"],
        "format": format_name,
        "current": current,
        "target": target_level,
        "ceiling": ceiling,
        "passed": [c["id"] for c in passed],
        "failed": [c["id"] for c in failed],
        "criteria_detail": contract["criteria"],
    }


def promote(format_name: str, target_level: str,
            ledger_path: Path | None = None, dry_run: bool = False) -> dict:
    """Promote a format to target_level if eligible.

    Returns {promoted, previous_level, new_level}.
    """
    path = ledger_path or DEFAULT_LEDGER
    eligibility = check_promotion(format_name, target_level, path)

    if not eligibility.get("eligible"):
        return {"promoted": False, **eligibility}

    if dry_run:
        return {"promoted": False, "dry_run": True, "would_promote": True,
                "previous_level": eligibility["current"], "new_level": target_level}

    # Update ledger
    ledger = yaml.safe_load(path.read_text(encoding="utf-8"))
    for entry in ledger:
        if entry.get("format") == format_name.lower() and entry.get("runtime", "python") == "python":
            previous = entry["lane_b_maturity"]
            entry["lane_b_maturity"] = target_level
            path.write_text(yaml.dump(ledger, default_flow_style=False, sort_keys=False), encoding="utf-8")
            return {"promoted": True, "previous_level": previous, "new_level": target_level,
                    "format": format_name}

    return {"promoted": False, "error": "entry_not_found_during_update"}


def main():
    parser = argparse.ArgumentParser(description="DOM Maturity Promoter")
    parser.add_argument("--format", required=True, help="Format name")
    parser.add_argument("--target", required=True, choices=["D2", "D3", "D4", "D5"],
                        help="Target maturity level")
    parser.add_argument("--ledger", default=None, help="Path to ledger YAML")
    parser.add_argument("--dry-run", action="store_true", help="Check without updating")
    args = parser.parse_args()

    ledger_path = Path(args.ledger) if args.ledger else None

    if args.dry_run:
        result = check_promotion(args.format, args.target, ledger_path)
    else:
        result = promote(args.format, args.target, ledger_path, dry_run=False)

    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("eligible") or result.get("promoted") else 1


if __name__ == "__main__":
    sys.exit(main())
