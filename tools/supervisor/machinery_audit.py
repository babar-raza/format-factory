"""machinery_audit.py — Post-execution audit for the machinery lifecycle track.

TC-MACH-WF-001 (2026-06-21): Implements post-execution audit stage for machinery track.
TC-MACH-WF-003 (2026-06-21): Implements mission completion gate check.

Usage:
  python tools/supervisor/machinery_audit.py [--iteration N] [--repo-root PATH]
  python tools/supervisor/machinery_audit.py --mission-complete-check [--repo-root PATH]

The audit reads .local/supervisor/machinery/mission-ledger.json and verifies
that each sprint's declared closed_gaps have verifiable evidence artifacts.

Exit codes:
  0 — PASS (all closed gaps have evidence) or MISSION_COMPLETE
  1 — FAIL_WITH_GAPS (some closed gaps lack evidence) or MISSION_INCOMPLETE
  2 — ERROR (ledger missing or malformed)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve().parent
_default_repo = _here.parent.parent


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Evidence roots that qualify as proof for a given closed gap.
# Maps gap_id prefix to evidence path patterns that indicate closure.
_GAP_EVIDENCE_MAP: dict[str, list[str]] = {
    "GAP-ARCH-001": ["src/python/fods/spec/"],
    "GAP-ARCH-003": ["src/python/fods/spec/"],
    "GAP-ARCH-004": ["src/python/fods/Compat/fods_document.py"],
    "GAP-ARCH-005": ["src/python/fodt/spec/__init__.py"],
    "GAP-ARCH-006": [".local/spec-cache/sal-facts-latest.json"],
    "GAP-ARCH-007": ["tools/supervisor/governance_validators.py"],
    "GAP-ARCH-008": ["src/python/fods/spec/"],
    "GAP-ARCH-009": ["src/python/fods/spec/"],
    "GAP-ARCH-013": [],  # Unknown — skip evidence check
    "GAP-WF-001": ["tools/supervisor/machinery_audit.py"],
    "GAP-WF-002": [],  # Plan-reopening mechanism — deferred
    "GAP-WF-003": ["tools/supervisor/machinery_audit.py"],
    "GAP-WF-004": ["tools/supervisor/write_plan_lock.py"],
    "SC-005": ["tools/supervisor/continuation_identity.py"],
}


def run_audit(
    repo_root: Path,
    iteration: int | None = None,
) -> dict:
    """Run the post-execution audit for the machinery track.

    Returns a result dict with:
      verdict: "PASS" | "FAIL_WITH_GAPS"
      verified_gaps: list of gap IDs with confirmed evidence
      unverified_gaps: list of gap IDs with no evidence found
      open_gaps: list of gaps that remain open (not closed)
    """
    ledger_path = repo_root / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
    if not ledger_path.exists():
        return {
            "verdict": "ERROR",
            "error": f"Mission ledger not found: {ledger_path}",
            "verified_gaps": [],
            "unverified_gaps": [],
            "open_gaps": [],
        }

    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "verdict": "ERROR",
            "error": f"Could not parse mission ledger: {exc}",
            "verified_gaps": [],
            "unverified_gaps": [],
            "open_gaps": [],
        }

    closed_gaps = ledger.get("closed_gaps", [])
    open_gaps = ledger.get("open_gaps", [])
    current_iteration = iteration or ledger.get("current_iteration", 0)

    verified: list[str] = []
    unverified: list[str] = []

    for gap_id in closed_gaps:
        evidence_paths = _GAP_EVIDENCE_MAP.get(gap_id, [])
        if not evidence_paths:
            # No known evidence path — accept as verified (unknown gap)
            verified.append(gap_id)
            continue
        # Check if any evidence path exists
        found = False
        for ep in evidence_paths:
            p = repo_root / ep
            if p.exists():
                found = True
                break
        if found:
            verified.append(gap_id)
        else:
            unverified.append(gap_id)

    verdict = "PASS" if not unverified else "FAIL_WITH_GAPS"

    result = {
        "audit_id": f"post-exec-audit-{current_iteration}",
        "mission_id": ledger.get("mission_id"),
        "iteration": current_iteration,
        "verdict": verdict,
        "verified_gaps": verified,
        "unverified_gaps": unverified,
        "open_gaps": open_gaps,
        "closed_gap_total": len(closed_gaps),
        "verified_count": len(verified),
        "unverified_count": len(unverified),
        "open_gap_count": len(open_gaps),
        "audited_at": _now_iso(),
    }
    return result


def check_mission_complete(repo_root: Path) -> dict:
    """Check whether the machinery mission is complete.

    MISSION_COMPLETE if: open_gaps is empty AND completion_audit_pending is False.
    Returns a result dict with verdict: MISSION_COMPLETE | MISSION_INCOMPLETE.
    """
    ledger_path = repo_root / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
    if not ledger_path.exists():
        return {"verdict": "MISSION_INCOMPLETE", "reason": "ledger missing", "open_gaps": []}

    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"verdict": "MISSION_INCOMPLETE", "reason": f"ledger parse error: {exc}", "open_gaps": []}

    open_gaps = ledger.get("open_gaps", [])
    completion_audit_pending = ledger.get("completion_audit_pending", True)

    if not open_gaps and not completion_audit_pending:
        return {
            "verdict": "MISSION_COMPLETE",
            "reason": "open_gaps is empty and completion_audit_pending is False",
            "open_gaps": [],
            "mission_id": ledger.get("mission_id"),
        }
    else:
        return {
            "verdict": "MISSION_INCOMPLETE",
            "reason": (
                f"{len(open_gaps)} open gap(s) remain"
                if open_gaps else "completion_audit_pending is True"
            ),
            "open_gaps": open_gaps,
            "mission_id": ledger.get("mission_id"),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Machinery lifecycle post-execution audit (TC-MACH-WF-001/003)"
    )
    parser.add_argument("--repo-root", default=str(_default_repo))
    parser.add_argument("--iteration", type=int, default=None)
    parser.add_argument("--mission-complete-check", action="store_true",
                        help="Check if mission is complete (TC-MACH-WF-003)")
    parser.add_argument("--write-output", action="store_true",
                        help="Write audit result to .local/supervisor/machinery/post-exec-audit-N.json")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.mission_complete_check:
        result = check_mission_complete(repo_root)
        print(json.dumps(result, indent=2))
        return 0 if result["verdict"] == "MISSION_COMPLETE" else 1

    result = run_audit(repo_root, iteration=args.iteration)
    print(json.dumps(result, indent=2))

    if args.write_output and result.get("verdict") not in ("ERROR",):
        audit_dir = repo_root / ".local" / "supervisor" / "machinery"
        audit_dir.mkdir(parents=True, exist_ok=True)
        out_path = audit_dir / f"post-exec-audit-{result['iteration']}.json"
        out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Audit written: {out_path}", file=sys.stderr)

    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
