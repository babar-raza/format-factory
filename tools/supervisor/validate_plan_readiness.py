"""
validate_plan_readiness.py — Pre-Execution Plan Validation

Validates that a plan file is materially complete and ready for execution
before autonomous_cycle.py begins executing any taskcards.

Called from autonomous_cycle.py Step 0b after the active plan lock is detected.

Returns a dict with all checks and an ``execution_may_start`` boolean.
Non-blocking by design: if ``execution_may_start == False``, the caller logs
CRITICAL and returns exit 3 (per Supreme Directive — log and continue).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent


def validate_plan_readiness(plan_path: Path) -> dict:
    """Validate that a plan file is present and materially complete for execution.

    Returns a dict with shape::

        {
            "pre_execution_plan_validation": {
                "plan_exists": bool,
                "native_plan_identity_proven": bool,          # WARN only
                "mission_binding_valid": bool,                # WARN only
                "plan_parseable": bool,
                "plan_materially_complete": bool,
                "taskcards_present": bool,
                "terminal_lock_defined": bool,
                "execution_may_start": bool,
                "failures": [...],
                "warnings": [...],
            }
        }

    Checks marked ``WARN only`` do not affect ``execution_may_start``.
    They are logged but do not block execution (backward-compatible for
    plans without the new front-matter format).
    """
    plan_path = Path(plan_path)
    failures: list[str] = []
    warnings: list[str] = []

    # ------------------------------------------------------------------
    # plan_exists (BLOCKING)
    # ------------------------------------------------------------------
    plan_exists = plan_path.exists()
    if not plan_exists:
        failures.append(f"PLAN_NOT_FOUND: {plan_path}")
        return {
            "pre_execution_plan_validation": {
                "plan_exists": False,
                "native_plan_identity_proven": False,
                "mission_binding_valid": False,
                "plan_parseable": False,
                "plan_materially_complete": False,
                "taskcards_present": False,
                "terminal_lock_defined": False,
                "execution_may_start": False,
                "failures": failures,
                "warnings": warnings,
            }
        }

    # ------------------------------------------------------------------
    # plan_parseable (BLOCKING)
    # ------------------------------------------------------------------
    try:
        text = plan_path.read_text(encoding="utf-8", errors="replace")
        plan_parseable = True
    except OSError as exc:
        failures.append(f"PLAN_NOT_READABLE: {exc}")
        return {
            "pre_execution_plan_validation": {
                "plan_exists": True,
                "native_plan_identity_proven": False,
                "mission_binding_valid": False,
                "plan_parseable": False,
                "plan_materially_complete": False,
                "taskcards_present": False,
                "terminal_lock_defined": False,
                "execution_may_start": False,
                "failures": failures,
                "warnings": warnings,
            }
        }

    # ------------------------------------------------------------------
    # Check for TERMINAL LOCK in plan file itself (BLOCKING)
    # If the plan file contains a plan_terminal_lock block, block execution.
    # ------------------------------------------------------------------
    if "plan_terminal_lock:" in text and "successor_required_for_future_changes: true" in text:
        failures.append(
            "TERMINAL_PLAN_EXECUTION_BLOCKED: plan file contains plan_terminal_lock "
            "with successor_required_for_future_changes=true"
        )
        return {
            "pre_execution_plan_validation": {
                "plan_exists": True,
                "native_plan_identity_proven": False,
                "mission_binding_valid": False,
                "plan_parseable": True,
                "plan_materially_complete": False,
                "taskcards_present": False,
                "terminal_lock_defined": True,
                "execution_may_start": False,
                "failures": failures,
                "warnings": warnings,
            }
        }

    # ------------------------------------------------------------------
    # native_plan_identity_proven (WARN only — backward compat)
    # ------------------------------------------------------------------
    native_plan_identity_proven = "plan_identity:" in text
    if not native_plan_identity_proven:
        warnings.append(
            "WARN_NO_PLAN_IDENTITY_FRONTMATTER: plan file lacks plan_identity: block. "
            "Add it per docs/governance/plan-identity-schema.md for durable identity."
        )

    # ------------------------------------------------------------------
    # mission_binding_valid (WARN only)
    # ------------------------------------------------------------------
    mission_binding_valid = native_plan_identity_proven  # proxy
    if not mission_binding_valid:
        warnings.append("WARN_MISSION_BINDING_UNVERIFIED: no plan_identity block to verify mission binding")

    # ------------------------------------------------------------------
    # plan_materially_complete (BLOCKING)
    # Plan must have more than 50 lines AND at least one TC- reference
    # ------------------------------------------------------------------
    line_count = text.count("\n")
    has_taskcard_ref = bool(re.search(r"\bTC-[A-Z0-9-]+\b", text))
    plan_materially_complete = line_count > 50 and has_taskcard_ref
    if not plan_materially_complete:
        failures.append(
            f"PLAN_NOT_MATERIALLY_COMPLETE: line_count={line_count} "
            f"has_taskcard_ref={has_taskcard_ref} — plan must have >50 lines and at least one TC- reference"
        )

    # ------------------------------------------------------------------
    # taskcards_present (BLOCKING)
    # ------------------------------------------------------------------
    taskcards_present = bool(re.search(r"task_id:|TC-[A-Z0-9-]+", text))
    if not taskcards_present:
        failures.append("NO_TASKCARDS: plan has no task_id: or TC- taskcard references")

    # ------------------------------------------------------------------
    # terminal_lock_defined (WARN only)
    # ------------------------------------------------------------------
    terminal_lock_defined = bool(
        re.search(r"terminal.{0,20}lock|TERMINAL.{0,20}LOCK|terminal_lock", text, re.IGNORECASE)
    )
    if not terminal_lock_defined:
        warnings.append(
            "WARN_NO_TERMINAL_LOCK_SECTION: plan has no terminal lock criteria section. "
            "Add a Terminal Lock Criteria section per the plan governance schema."
        )

    # ------------------------------------------------------------------
    # execution_may_start: all BLOCKING checks pass
    # ------------------------------------------------------------------
    execution_may_start = len(failures) == 0

    return {
        "pre_execution_plan_validation": {
            "plan_exists": plan_exists,
            "native_plan_identity_proven": native_plan_identity_proven,
            "mission_binding_valid": mission_binding_valid,
            "plan_parseable": plan_parseable,
            "plan_materially_complete": plan_materially_complete,
            "taskcards_present": taskcards_present,
            "terminal_lock_defined": terminal_lock_defined,
            "execution_may_start": execution_may_start,
            "failures": failures,
            "warnings": warnings,
        }
    }


def _print_result(result: dict, plan_path: Path) -> None:
    """Pretty-print validation result for diagnostic use."""
    v = result["pre_execution_plan_validation"]
    status = "PASS" if v["execution_may_start"] else "FAIL"
    print(f"[validate_plan_readiness] {status} — {plan_path.name}")
    for check, value in v.items():
        if check in ("failures", "warnings"):
            continue
        icon = "OK" if value else ("WARN" if check in ("native_plan_identity_proven", "mission_binding_valid", "terminal_lock_defined") else "FAIL")
        print(f"  {icon:4s} {check}: {value}")
    if v["warnings"]:
        print("  Warnings:")
        for w in v["warnings"]:
            print(f"    WARN: {w}")
    if v["failures"]:
        print("  Failures:")
        for f in v["failures"]:
            print(f"    FAIL: {f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python validate_plan_readiness.py <plan-path>")
        sys.exit(1)
    p = Path(sys.argv[1])
    result = validate_plan_readiness(p)
    _print_result(result, p)
    v = result["pre_execution_plan_validation"]
    sys.exit(0 if v["execution_may_start"] else 3)
