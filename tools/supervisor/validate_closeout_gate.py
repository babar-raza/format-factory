"""Closeout gate validator — executable enforcement of sprint closeout rules.

This validator checks that a sprint has met all closeout prerequisites before
the agent is allowed to declare "Sprint Complete". It replaces documentation-only
enforcement (MEMORY.md instructions) with machine-verifiable checks.

Usage:
    python tools/supervisor/validate_closeout_gate.py --evidence-root .local/evidences/<run_id>

Exit codes:
    0 — PASS: All closeout gates satisfied.
    1 — FAIL: One or more gates failed (details in output JSON).
    2 — ERROR: Invalid arguments or missing evidence root.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Gate checks
# ---------------------------------------------------------------------------

EVIDENCE_ROOT_PLACEHOLDER = Path(".")


def check_declaration_exists(evidence_root: Path) -> dict:
    """Gate 1: evidence-declaration.yaml must exist."""
    decl = evidence_root / "evidence-declaration.yaml"
    return {
        "gate": "declaration_exists",
        "passed": decl.is_file(),
        "path": str(decl),
        "detail": "evidence-declaration.yaml exists" if decl.is_file()
                  else "evidence-declaration.yaml MISSING",
    }


def check_package_exists(evidence_root: Path) -> dict:
    """Gate 2: declaration-review-package.zip must exist somewhere in review dir."""
    # Check in the standard review location
    repo_root = _find_repo_root(evidence_root)
    run_id = evidence_root.name
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    pkg = review_dir / "declaration-review-package.zip"
    # Also check evidence root itself
    pkg_alt = evidence_root / "declaration-review-package.zip"
    found = pkg.is_file() or pkg_alt.is_file()
    path = str(pkg) if pkg.is_file() else str(pkg_alt) if pkg_alt.is_file() else str(pkg)
    return {
        "gate": "package_exists",
        "passed": found,
        "path": path,
        "detail": "review package ZIP exists" if found else "review package ZIP MISSING",
    }


def check_raw_logs_exist(evidence_root: Path) -> dict:
    """Gate 3: raw-logs/ directory must exist and contain at least one log."""
    logs_dir = evidence_root / "raw-logs"
    has_logs = logs_dir.is_dir() and any(logs_dir.iterdir())
    count = len(list(logs_dir.glob("*"))) if logs_dir.is_dir() else 0
    return {
        "gate": "raw_logs_exist",
        "passed": has_logs,
        "path": str(logs_dir),
        "detail": f"{count} raw log files found" if has_logs
                  else "raw-logs/ MISSING or empty",
    }


def check_lane_ledger_exists(evidence_root: Path) -> dict:
    """Gate 4: lane-ledger.yaml must exist."""
    ledger = evidence_root / "lane-ledger.yaml"
    return {
        "gate": "lane_ledger_exists",
        "passed": ledger.is_file(),
        "path": str(ledger),
        "detail": "lane-ledger.yaml exists" if ledger.is_file()
                  else "lane-ledger.yaml MISSING",
    }


def check_state_ledger_exists(evidence_root: Path) -> dict:
    """Gate 5: state-ledger.yaml must exist."""
    ledger = evidence_root / "state-ledger.yaml"
    return {
        "gate": "state_ledger_exists",
        "passed": ledger.is_file(),
        "path": str(ledger),
        "detail": "state-ledger.yaml exists" if ledger.is_file()
                  else "state-ledger.yaml MISSING",
    }


def check_no_rework_remaining(evidence_root: Path) -> dict:
    """Gate 6: continuation signal must not have non-empty rework_items for final closeout."""
    repo_root = _find_repo_root(evidence_root)
    signal_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if not signal_path.is_file():
        return {
            "gate": "no_rework_remaining",
            "passed": True,  # No signal = no rework known
            "path": str(signal_path),
            "detail": "No continuation signal found (no rework tracked)",
        }
    try:
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "gate": "no_rework_remaining",
            "passed": False,
            "path": str(signal_path),
            "detail": "continuation-signal.json is malformed",
        }
    rework = signal.get("rework_items", [])
    return {
        "gate": "no_rework_remaining",
        "passed": len(rework) == 0,
        "path": str(signal_path),
        "rework_items": rework,
        "detail": "No rework items remaining" if not rework
                  else f"Rework items remain: {rework}",
    }


def check_no_runnable_next_action(evidence_root: Path) -> dict:
    """Gate 7: next-action.json must not contain unexecuted non-health-check work."""
    repo_root = _find_repo_root(evidence_root)
    action_path = repo_root / ".local" / "supervisor" / "next-action.json"
    if not action_path.is_file():
        return {
            "gate": "no_runnable_next_action",
            "passed": True,
            "path": str(action_path),
            "detail": "No next-action.json found",
        }
    try:
        action = json.loads(action_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "gate": "no_runnable_next_action",
            "passed": True,
            "path": str(action_path),
            "detail": "next-action.json is malformed (treated as no action)",
        }
    action_type = action.get("action_type", "")
    # Health checks and post-closeout items are not blocking
    non_blocking_types = {"QUEUE_HEALTH_CHECK", "RUN_MD_NONEMPTY_CHECK",
                          "RUN_JSON_VALIDATION", "UPDATE_STATE",
                          "GENERATE_EVIDENCE_STUB"}
    is_blocking = action_type not in non_blocking_types
    return {
        "gate": "no_runnable_next_action",
        "passed": not is_blocking,
        "path": str(action_path),
        "action_type": action_type,
        "detail": f"Next action is non-blocking ({action_type})" if not is_blocking
                  else f"Blocking next action exists: {action_type}",
    }


def check_accepted_not_with_rework_final(evidence_root: Path) -> dict:
    """Gate 8: ACCEPTED_WITH_REWORK cannot be the final closeout verdict."""
    repo_root = _find_repo_root(evidence_root)
    run_id = evidence_root.name
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id
    manifest = review_dir / "supervisor-cycle-manifest.yaml"
    grades_path = review_dir / "item-grades.json"

    # Check item grades for rework
    if grades_path.is_file():
        try:
            grades = json.loads(grades_path.read_text(encoding="utf-8"))
            rework_ids = [g.get("item_id") for g in grades
                          if isinstance(g, dict) and
                          g.get("grade") in ("REWORK_REQUIRED", "OVERCLAIMED", "REJECTED")]
            if rework_ids:
                return {
                    "gate": "accepted_not_with_rework_final",
                    "passed": False,
                    "rework_ids": rework_ids,
                    "detail": f"Items still in rework: {rework_ids}",
                }
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "gate": "accepted_not_with_rework_final",
        "passed": True,
        "detail": "No rework/rejected items in grades",
    }


def check_prompt_rework_consistency(evidence_root: Path) -> dict:
    """Gate 9: next-sprint.md cannot say 'Rework: None' if review has rework items."""
    repo_root = _find_repo_root(evidence_root)
    run_id = evidence_root.name
    review_dir = repo_root / ".local" / "supervisor" / "reviews" / run_id

    # Check if review has rework
    grades_path = review_dir / "item-grades.json"
    next_sprint = repo_root / "reports" / "supervisor" / "next-sprint.md"

    has_rework_in_review = False
    if grades_path.is_file():
        try:
            grades = json.loads(grades_path.read_text(encoding="utf-8"))
            has_rework_in_review = any(
                isinstance(g, dict) and g.get("grade") == "REWORK_REQUIRED"
                for g in grades
            )
        except (json.JSONDecodeError, OSError):
            pass

    prompt_says_no_rework = False
    if next_sprint.is_file():
        try:
            content = next_sprint.read_text(encoding="utf-8").lower()
            prompt_says_no_rework = "rework: none" in content or "rework items: none" in content
        except OSError:
            pass

    contradiction = has_rework_in_review and prompt_says_no_rework
    return {
        "gate": "prompt_rework_consistency",
        "passed": not contradiction,
        "has_rework_in_review": has_rework_in_review,
        "prompt_says_no_rework": prompt_says_no_rework,
        "detail": "Prompt and review agree on rework status" if not contradiction
                  else "CONTRADICTION: review has rework but next-sprint.md says none",
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_repo_root(evidence_root: Path) -> Path:
    """Walk up from evidence_root to find the repo root (.git or fallback)."""
    p = evidence_root.resolve()
    for _ in range(10):
        if (p / ".git").exists() or (p / "CLAUDE.md").exists():
            return p
        parent = p.parent
        if parent == p:
            break
        p = parent
    # Fallback: assume evidence_root is under .local/evidences/<run_id>
    # so repo root is 3 levels up
    return evidence_root.resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

ALL_GATES = [
    check_declaration_exists,
    check_package_exists,
    check_raw_logs_exist,
    check_lane_ledger_exists,
    check_state_ledger_exists,
    check_no_rework_remaining,
    check_no_runnable_next_action,
    check_accepted_not_with_rework_final,
    check_prompt_rework_consistency,
]


def run_closeout_gate(evidence_root: Path) -> dict:
    """Run all closeout gate checks and return aggregate result."""
    results = []
    for gate_fn in ALL_GATES:
        result = gate_fn(evidence_root)
        results.append(result)

    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    all_passed = failed == 0

    return {
        "verdict": "PASS" if all_passed else "FAIL",
        "passed_count": passed,
        "failed_count": failed,
        "total_gates": len(results),
        "gates": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate sprint closeout gate")
    parser.add_argument("--evidence-root", required=True,
                        help="Path to evidence root directory")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    evidence_root = Path(args.evidence_root)
    if not evidence_root.is_dir():
        print(f"ERROR: Evidence root does not exist: {evidence_root}", file=sys.stderr)
        return 2

    result = run_closeout_gate(evidence_root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Closeout Gate: {result['verdict']}")
        print(f"  Passed: {result['passed_count']}/{result['total_gates']}")
        for gate in result["gates"]:
            status = "PASS" if gate["passed"] else "FAIL"
            print(f"  [{status}] {gate['gate']}: {gate['detail']}")

    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
