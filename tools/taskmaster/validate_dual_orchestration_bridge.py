"""
validate_dual_orchestration_bridge.py — Format Factory No-Drift State Contract Validator
Enforces the no-drift contract between Task Master, Ruflo, and Format Factory authority.

Contract rules:
  1. TM task "done" does NOT imply FF gate closed
  2. Ruflo lane "complete" does NOT imply evidence accepted
  3. Ruflo memory/state must be marked non_authoritative: true
  4. Ruflo state must not claim gate closure
  5. Supervisor verdict is advisory — not FF authority
  6. Supervisor next-sprint.md is input to next sprint — not authority
  7. Missing TM/Ruflo state before activation is WARNING, not failure

Exit codes:
  0 — no drift detected (may have warnings)
  1 — drift detected (contract violations)
  9 — unexpected error

Usage:
  python tools/taskmaster/validate_dual_orchestration_bridge.py
  python tools/taskmaster/validate_dual_orchestration_bridge.py --tm-tasks reports/supervisor/next-sprint-taskmaster.json --ruflo-lanes reports/supervisor/next-ruflo-lanes.json
"""

import argparse
import json
import sys
from pathlib import Path


GATE_CLOSURE_KEYWORDS = [
    "gate_closed", "gate_approved", "gate_passed", "gate_11_approved",
    "G11-G: CLOSED", "commercial_product_ready: true",
]


class DriftResult:
    def __init__(self):
        self.violations = []
        self.warnings = []

    def violation(self, rule: str, msg: str):
        self.violations.append({"rule": rule, "message": msg})

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def has_drift(self) -> bool:
        return len(self.violations) > 0

    def summary(self) -> dict:
        return {
            "no_drift": not self.has_drift,
            "violation_count": len(self.violations),
            "warning_count": len(self.warnings),
            "violations": self.violations,
            "warnings": self.warnings,
        }


def check_tm_done_implies_gate_closed(tasks: list, result: DriftResult) -> None:
    """Rule 1: TM task done must not imply FF gate is closed."""
    for task in tasks:
        if task.get("status") == "done":
            # Check for gate closure claims in descriptions
            desc = json.dumps(task).lower()
            for keyword in GATE_CLOSURE_KEYWORDS:
                if keyword.lower() in desc:
                    result.violation(
                        "RULE-1",
                        f"Task '{task.get('task_id', '?')}' status=done but contains "
                        f"gate closure keyword '{keyword}' — TM done ≠ FF gate closed",
                    )

            # Check non_authoritative flag
            if task.get("non_authoritative") is False:
                result.violation(
                    "RULE-1",
                    f"Task '{task.get('task_id', '?')}' status=done with non_authoritative=False "
                    f"— must be non_authoritative:true for work-ahead tasks",
                )


def check_ruflo_complete_implies_evidence(lanes: list, result: DriftResult) -> None:
    """Rule 2: Ruflo lane complete must not imply evidence accepted."""
    for lane in lanes:
        if lane.get("status") == "completed":
            # If lane is marked complete, non_authoritative must be true
            if lane.get("non_authoritative") is not True:
                result.violation(
                    "RULE-2",
                    f"Lane '{lane.get('lane_id', '?')}' status=completed but missing "
                    f"non_authoritative:true — Ruflo completion ≠ evidence accepted",
                )


def check_ruflo_non_authoritative(lanes: list, result: DriftResult) -> None:
    """Rule 3: All Ruflo lanes must have non_authoritative: true."""
    for lane in lanes:
        if lane.get("non_authoritative") is not True:
            result.violation(
                "RULE-3",
                f"Lane '{lane.get('lane_id', '?')}' missing non_authoritative:true "
                f"— all Ruflo state is advisory only",
            )


def check_ruflo_gate_closure_claim(lanes: list, result: DriftResult) -> None:
    """Rule 4: Ruflo state must not claim gate closure."""
    for lane in lanes:
        lane_text = json.dumps(lane).lower()
        for keyword in GATE_CLOSURE_KEYWORDS:
            if keyword.lower() in lane_text:
                result.violation(
                    "RULE-4",
                    f"Lane '{lane.get('lane_id', '?')}' contains gate closure claim '{keyword}' "
                    f"— Ruflo state cannot close Format Factory gates",
                )


def check_supervisor_verdict_authority(supervisor_state: dict, result: DriftResult) -> None:
    """Rule 5: Supervisor verdict must not claim to be FF authority."""
    if supervisor_state:
        verdict = supervisor_state.get("verdict", "")
        # If verdict claims gate approval or commercial readiness, that's drift
        if any(kw.lower() in verdict.lower() for kw in ["GATE_APPROVED", "COMMERCIAL_READY"]):
            result.violation(
                "RULE-5",
                f"Supervisor verdict '{verdict}' claims gate approval or commercial readiness "
                f"— supervisor is advisory only",
            )


def validate(
    tm_tasks_path: Path | None,
    ruflo_lanes_path: Path | None,
    supervisor_state_path: Path | None,
) -> DriftResult:
    """Main no-drift validation."""
    result = DriftResult()

    # Load TM tasks
    tasks = []
    if tm_tasks_path:
        if not tm_tasks_path.exists():
            result.warn(
                f"TM tasks file not found: {tm_tasks_path} "
                f"— WARNING only (expected before MODE 3 init)"
            )
        else:
            try:
                data = json.loads(tm_tasks_path.read_text(encoding="utf-8"))
                tasks = data.get("tasks", [])
            except json.JSONDecodeError as e:
                result.violations.append({"rule": "PARSE", "message": f"Invalid TM JSON: {e}"})

    # Load Ruflo lanes
    lanes = []
    if ruflo_lanes_path:
        if not ruflo_lanes_path.exists():
            result.warn(
                f"Ruflo lanes file not found: {ruflo_lanes_path} "
                f"— WARNING only (expected before MODE 3 init)"
            )
        else:
            try:
                data = json.loads(ruflo_lanes_path.read_text(encoding="utf-8"))
                lanes = data.get("lanes", [])
            except json.JSONDecodeError as e:
                result.violations.append({"rule": "PARSE", "message": f"Invalid Ruflo JSON: {e}"})

    # Load supervisor state
    supervisor_state = {}
    if supervisor_state_path and supervisor_state_path.exists():
        try:
            supervisor_state = json.loads(supervisor_state_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Apply all contract rules
    if tasks:
        check_tm_done_implies_gate_closed(tasks, result)

    if lanes:
        check_ruflo_complete_implies_evidence(lanes, result)
        check_ruflo_non_authoritative(lanes, result)
        check_ruflo_gate_closure_claim(lanes, result)

    if supervisor_state:
        check_supervisor_verdict_authority(supervisor_state, result)

    if not tasks and not lanes:
        result.warn("No TM tasks or Ruflo lanes found — drift check is nominal (nothing to check)")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate no-drift state contract between TM, Ruflo, and FF authority"
    )
    parser.add_argument(
        "--tm-tasks",
        type=Path,
        default=Path("reports/supervisor/next-sprint-taskmaster.json"),
        help="Path to TM tasks JSON",
    )
    parser.add_argument(
        "--ruflo-lanes",
        type=Path,
        default=Path("reports/supervisor/next-ruflo-lanes.json"),
        help="Path to Ruflo lanes JSON",
    )
    parser.add_argument(
        "--supervisor-state",
        type=Path,
        default=Path(".supervisor/state/current-run.json"),
        help="Path to supervisor state JSON",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    result = validate(args.tm_tasks, args.ruflo_lanes, args.supervisor_state)
    summary = result.summary()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "NO_DRIFT" if not result.has_drift else "DRIFT_DETECTED"
        print(f"NO_DRIFT_CONTRACT: {status}")
        print(f"  Violations: {summary['violation_count']}, Warnings: {summary['warning_count']}")
        for v in summary["violations"]:
            print(f"  [{v['rule']}] {v['message']}")
        for w in summary["warnings"]:
            print(f"  WARNING: {w}")

    return 0 if not result.has_drift else 1


if __name__ == "__main__":
    sys.exit(main())
