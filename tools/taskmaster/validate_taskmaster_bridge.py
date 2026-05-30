"""
validate_taskmaster_bridge.py — Format Factory Task Master Bridge Validator
Validates next-sprint-taskmaster.json against the FF-TM bridge schema and rules.

Rules enforced:
  1. Each task must have at least one of: ff_taskcard_ref, ff_gate_ref, ff_doc_ref
  2. Each task must have: acceptance_evidence, validation_command
  3. Task status must be one of the allowed values
  4. Blocked tasks must include blocker_type
  5. Work-ahead tasks (non_authoritative=False tasks claiming done) must include non_authoritative=True
  6. Missing tasks file before MODE 3 activation is WARNING (not failure)
  7. TM done status does NOT imply FF gate closed

Exit codes:
  0 — valid (may have warnings)
  1 — invalid (hard failures)
  9 — unexpected error

Usage:
  python tools/taskmaster/validate_taskmaster_bridge.py --input reports/supervisor/next-sprint-taskmaster.json
  python tools/taskmaster/validate_taskmaster_bridge.py --input .taskmaster/tasks/tasks.json
"""

import argparse
import json
import sys
from pathlib import Path


ALLOWED_STATUSES = {"pending", "in-progress", "done", "blocked", "evidence-blocked", "approval-blocked"}
REQUIRED_BRIDGE_FIELDS = {"ff_taskcard_ref", "ff_gate_ref", "ff_doc_ref"}
BLOCKED_STATUSES = {"blocked", "evidence-blocked", "approval-blocked"}
ALLOWED_BLOCKER_TYPES = {
    "external_gate", "credentials", "evidence_required", "human_approval", "governance_conflict"
}


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> dict:
        return {
            "valid": self.valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_task(task: dict, task_index: int, result: ValidationResult) -> None:
    """Validate a single task object."""
    tid = task.get("task_id", f"task[{task_index}]")
    prefix = f"Task {tid}"

    # Rule 1: Must have at least one FF bridge ref
    has_bridge = any(task.get(f) for f in REQUIRED_BRIDGE_FIELDS)
    if not has_bridge:
        result.error(f"{prefix}: missing FF bridge reference (needs ff_taskcard_ref, ff_gate_ref, or ff_doc_ref)")

    # Rule 2: Must have acceptance_evidence and validation_command
    if not task.get("acceptance_evidence"):
        result.error(f"{prefix}: missing acceptance_evidence")
    if not task.get("validation_command"):
        result.error(f"{prefix}: missing validation_command")

    # Rule 3: Status must be allowed
    status = task.get("status", "")
    if status and status not in ALLOWED_STATUSES:
        result.error(f"{prefix}: invalid status '{status}' (allowed: {sorted(ALLOWED_STATUSES)})")

    # Rule 4: Blocked tasks must have blocker_type
    if status in BLOCKED_STATUSES and not task.get("blocker_type"):
        result.error(f"{prefix}: status is '{status}' but blocker_type is missing")

    # Rule 5: Validate blocker_type value if present
    blocker_type = task.get("blocker_type")
    if blocker_type and blocker_type not in ALLOWED_BLOCKER_TYPES:
        result.warn(f"{prefix}: blocker_type '{blocker_type}' not in known types {sorted(ALLOWED_BLOCKER_TYPES)}")

    # Rule 6: Work-ahead tasks with status done must be non_authoritative
    if status == "done" and task.get("non_authoritative") is False:
        result.error(f"{prefix}: status=done but non_authoritative=False — TM done does NOT imply FF gate closed")

    # Rule 7: Warn if task has no supervisor_task_ref
    if not task.get("supervisor_task_ref"):
        result.warn(f"{prefix}: missing supervisor_task_ref (recommended)")


def validate_file(data: dict, result: ValidationResult) -> None:
    """Validate the full task export file."""
    # Top-level required fields
    for field in ("sprint_id", "timestamp", "verdict"):
        if not data.get(field):
            result.error(f"Missing required top-level field: {field}")

    tasks = data.get("tasks")
    if tasks is None:
        result.error("Missing 'tasks' array")
        return

    if not isinstance(tasks, list):
        result.error("'tasks' must be an array")
        return

    if len(tasks) == 0:
        result.warn("Empty task list — is this intentional?")
        return

    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            result.error(f"Task at index {i} is not an object")
            continue
        validate_task(task, i, result)


def validate(input_path: Path) -> ValidationResult:
    """Main validation entry point."""
    result = ValidationResult()

    # Missing file before MODE 3 activation is WARNING (not failure)
    if not input_path.exists():
        result.warn(
            f"Task file not found: {input_path} "
            f"— this is expected before Task Master is initialized (MODE 3)"
        )
        return result

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result.error(f"Invalid JSON: {e}")
        return result
    except Exception as e:
        result.error(f"Could not read file: {e}")
        return result

    validate_file(data, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Task Master bridge JSON against FF-TM bridge rules"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("reports/supervisor/next-sprint-taskmaster.json"),
        help="Path to task JSON file",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    result = validate(args.input)
    summary = result.summary()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "VALID" if result.valid else "INVALID"
        print(f"TASKMASTER_BRIDGE_VALIDATION: {status}")
        print(f"  Errors: {summary['error_count']}, Warnings: {summary['warning_count']}")
        for e in summary["errors"]:
            print(f"  ERROR: {e}")
        for w in summary["warnings"]:
            print(f"  WARNING: {w}")

    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
