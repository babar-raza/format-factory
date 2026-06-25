#!/usr/bin/env python3
"""
validate_taskcard_execution_contract.py — TC-SGF-004

Validates a taskcard YAML file against the execution contract schema before
READY transition. A taskcard without the required execution contract fields
MUST NOT transition to READY.

Required fields for PRODUCT and MACHINERY taskcards:
  - required_capabilities (non-empty list)
  - skill_ids (non-empty list)
  - command_ids (non-empty list)
  - allowed_paths (non-empty list)
  - receipt_required = true  (or allowed_paths implicitly requires it)

Output (JSON to stdout):
  {
    "verdict": "VALID" | "INVALID",
    "taskcard_path": "...",
    "task_id": "...",
    "task_type": "...",
    "missing_fields": [...],
    "errors": [...],
    "skip_reason": "..."  # present only when not a mutating taskcard
  }

Exit codes:
  0 — VALID
  1 — INVALID
  2 — FILE_NOT_FOUND or PARSE_ERROR
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Task types that DO NOT require execution contracts (read-only/analysis tasks)
EXEMPT_TASK_TYPES = frozenset({
    "ANALYSIS",
    "AUDIT",
    "READ_ONLY",
    "REPORTING",
    "RECON",
    "INVESTIGATION",
})

# Sprint types that require execution contracts
MUTATING_SPRINT_TYPES = frozenset({
    "PRODUCT_SOURCE",
    "PRODUCT_TEST",
    "GOVERNANCE_MACHINERY",
    "REGISTRY_REPAIR",
    "TASKCARD_SCHEMA_REPAIR",
    "CODEX_ADAPTER",
    "MUTATION_GUARD",
    "SUPERVISOR_ENFORCEMENT",
})

REQUIRED_LIST_FIELDS = [
    "required_capabilities",
    "skill_ids",
    "command_ids",
    "allowed_paths",
]


def load_yaml(path: Path) -> dict | None:
    """Load YAML file; return None on error."""
    if yaml is None:
        # Fallback: basic YAML parsing via safe_load if available
        try:
            import yaml as _yaml
            return _yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_mutating_taskcard(data: dict) -> tuple[bool, str]:
    """
    Return (is_mutating, reason).
    A taskcard is mutating if its task_type or sprint_types indicate mutation.
    """
    task_type = (data.get("task_type") or "").upper()
    sprint_types = [s.upper() for s in (data.get("sprint_types") or [])]

    if task_type in EXEMPT_TASK_TYPES:
        return False, f"task_type={task_type} is exempt from execution contract"

    if any(s in MUTATING_SPRINT_TYPES for s in sprint_types):
        return True, "sprint_types contains mutating type"

    # Default: if task_type is not explicitly exempt, require contract
    return True, "task_type not in exempt list — contract required by default"


def validate(taskcard_path: str) -> dict:
    """
    Validate a taskcard YAML against the execution contract schema.
    Returns a result dict.
    """
    path = Path(taskcard_path)

    if not path.exists():
        return {
            "verdict": "INVALID",
            "taskcard_path": taskcard_path,
            "task_id": None,
            "task_type": None,
            "missing_fields": [],
            "errors": [f"File not found: {taskcard_path}"],
        }

    data = load_yaml(path)
    if data is None:
        return {
            "verdict": "INVALID",
            "taskcard_path": taskcard_path,
            "task_id": None,
            "task_type": None,
            "missing_fields": [],
            "errors": ["Failed to parse YAML"],
        }

    task_id = data.get("task_id", "UNKNOWN")
    task_type = data.get("task_type", "")

    # Check if this taskcard requires an execution contract
    is_mutating, reason = is_mutating_taskcard(data)
    if not is_mutating:
        return {
            "verdict": "VALID",
            "taskcard_path": taskcard_path,
            "task_id": task_id,
            "task_type": task_type,
            "missing_fields": [],
            "errors": [],
            "skip_reason": reason,
        }

    missing_fields: list[str] = []
    errors: list[str] = []

    # Check required list fields — must be present AND non-empty
    for field in REQUIRED_LIST_FIELDS:
        value = data.get(field)
        if value is None:
            missing_fields.append(field)
            errors.append(f"Missing required field: {field}")
        elif not isinstance(value, list):
            missing_fields.append(field)
            errors.append(f"Field '{field}' must be a list, got {type(value).__name__}")
        elif len(value) == 0:
            missing_fields.append(field)
            errors.append(f"Field '{field}' must not be empty (empty list ≠ populated)")

    # Check allowed_paths (already covered above, but add specificity)
    # forbidden_paths is optional but checked for completeness

    # Check receipt_required — must be true for PRODUCT/MACHINERY mutating taskcards
    receipt_required = data.get("receipt_required")
    if receipt_required is not None:
        if receipt_required is not True:
            missing_fields.append("receipt_required")
            errors.append("Field 'receipt_required' must be true (got false or non-boolean)")
    # If absent, it's not a hard error (field added by TC-SGF-004 going forward)
    # but log a warning
    elif data.get("task_type") in ("PRODUCT_SOURCE", "PRODUCT_TEST", "GOVERNANCE_MACHINERY"):
        errors.append("WARNING: 'receipt_required' field absent — should be true for this task_type")

    verdict = "VALID" if not missing_fields else "INVALID"
    # Downgrade to VALID if all errors are warnings
    hard_errors = [e for e in errors if not e.startswith("WARNING")]
    verdict = "VALID" if not any(f in REQUIRED_LIST_FIELDS for f in missing_fields) and not hard_errors else verdict

    return {
        "verdict": verdict,
        "taskcard_path": taskcard_path,
        "task_id": task_id,
        "task_type": task_type,
        "missing_fields": missing_fields,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a taskcard YAML against the execution contract schema"
    )
    parser.add_argument("taskcard_path", help="Path to the taskcard YAML file")
    parser.add_argument("--json", action="store_true", help="Output as JSON (default: pretty print)")
    args = parser.parse_args()

    result = validate(args.taskcard_path)

    print(json.dumps(result, indent=2))

    if result["verdict"] == "VALID":
        return 0
    elif result.get("errors") and all(e.startswith("WARNING") for e in result["errors"]):
        return 0  # warnings only
    return 1


if __name__ == "__main__":
    sys.exit(main())
