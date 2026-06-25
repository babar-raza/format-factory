#!/usr/bin/env python3
"""
validate_execution_plan.py — Execution plan pre-flight validator.

TC-RECON-W6-005 / MW-001: Adds plan-level validation that the supervisor
machinery (autonomous_cycle.py, sprint_executor.py) previously lacked.

Validates a YAML execution plan file against:
  1. All skill_ids reference active (non-deprecated) skills in skill-registry.yaml
  2. All dependency task_ids reference valid tasks defined in the same plan
  3. No unresolved option branches (detected by "Option A|B|C" unresolved patterns)
  4. All allowed_paths reference existing files or directories

Usage:
    python tools/supervisor/validate_execution_plan.py <plan_path> [--strict]

Exit codes:
    0 — all checks PASS
    1 — one or more FAIL findings
    2 — plan file not found or unparseable

Arguments:
    plan_path   Path to the YAML execution plan to validate
    --strict    Treat WARN findings as FAIL (default: WARN only)
"""

import argparse
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not available. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Could not parse plan file: {e}", file=sys.stderr)
        sys.exit(2)


def _load_skill_registry() -> dict[str, str]:
    """Returns mapping skill_id -> status from skill-registry.yaml."""
    registry_path = _REPO_ROOT / ".supervisor" / "skill-registry.yaml"
    if not registry_path.exists():
        return {}
    data = _load_yaml(registry_path)
    skills = data.get("skills", [])
    return {
        s.get("skill_id", s.get("id", "")): s.get("status", "unknown")
        for s in skills
        if s.get("skill_id") or s.get("id")
    }


def _collect_task_ids(plan: dict) -> set[str]:
    """Extract all task_ids defined in the plan (waves or flat list)."""
    ids: set[str] = set()
    tasks = plan.get("tasks", plan.get("taskcards", []))
    if isinstance(tasks, list):
        for t in tasks:
            tid = t.get("task_id", t.get("id", ""))
            if tid:
                ids.add(tid)
    # Also check wave-structured plans
    for key, value in plan.items():
        if key.startswith("wave") and isinstance(value, list):
            for t in value:
                tid = t.get("task_id", t.get("id", ""))
                if tid:
                    ids.add(tid)
    return ids


def _collect_all_tasks(plan: dict) -> list[dict]:
    """Return all task dicts from plan regardless of structure."""
    tasks: list[dict] = []
    flat = plan.get("tasks", plan.get("taskcards", []))
    if isinstance(flat, list):
        tasks.extend(flat)
    for key, value in plan.items():
        if key.startswith("wave") and isinstance(value, list):
            tasks.extend(value)
    return tasks


def validate_plan(plan_path: Path, strict: bool = False) -> int:
    """
    Validate the execution plan at plan_path.
    Returns 0 (PASS), 1 (FAIL), or 2 (parse error).
    """
    if not plan_path.exists():
        print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
        return 2

    plan = _load_yaml(plan_path)
    if not isinstance(plan, dict):
        print("ERROR: Plan file does not contain a YAML mapping at root.", file=sys.stderr)
        return 2

    skill_registry = _load_skill_registry()
    defined_task_ids = _collect_task_ids(plan)
    all_tasks = _collect_all_tasks(plan)

    findings: list[tuple[str, str, str]] = []  # (level, check, message)

    # -------------------------------------------------------------------------
    # CHECK 1: All skill_ids reference active skills
    # -------------------------------------------------------------------------
    for task in all_tasks:
        tid = task.get("task_id", task.get("id", "?"))
        skill_ids = task.get("skill_ids", task.get("skill_id", []))
        if isinstance(skill_ids, str):
            skill_ids = [skill_ids]
        for sid in (skill_ids or []):
            if sid not in skill_registry:
                findings.append(("WARN", "SKILL_NOT_FOUND",
                                 f"Task {tid}: skill_id '{sid}' not found in skill-registry.yaml"))
            elif skill_registry[sid] in ("deprecated", "disabled", "removed"):
                findings.append(("FAIL", "DEPRECATED_SKILL",
                                 f"Task {tid}: skill_id '{sid}' has status='{skill_registry[sid]}'"))

    # -------------------------------------------------------------------------
    # CHECK 2: All dependency task_ids resolve to defined tasks in the plan
    # -------------------------------------------------------------------------
    for task in all_tasks:
        tid = task.get("task_id", task.get("id", "?"))
        deps = task.get("dependencies", [])
        if isinstance(deps, str):
            deps = [deps]
        for dep in (deps or []):
            if dep not in defined_task_ids:
                findings.append(("WARN", "UNRESOLVED_DEPENDENCY",
                                 f"Task {tid}: dependency '{dep}' not found in plan task_ids"))

    # -------------------------------------------------------------------------
    # CHECK 3: No unresolved option branches
    # -------------------------------------------------------------------------
    import re
    unresolved_pattern = re.compile(
        r"\b(Option [ABC]|if .*PdfSharp|Branch [AB]|2a:|2b:|assessment step)\b",
        re.IGNORECASE
    )
    for task in all_tasks:
        tid = task.get("task_id", task.get("id", "?"))
        steps = task.get("implementation_steps", task.get("execution_steps", []))
        if isinstance(steps, list):
            for step in steps:
                step_str = str(step)
                if unresolved_pattern.search(step_str):
                    findings.append(("WARN", "UNRESOLVED_OPTION_BRANCH",
                                     f"Task {tid}: possible unresolved option branch in step: "
                                     f"'{step_str[:80]}'"))

    # -------------------------------------------------------------------------
    # CHECK 4: allowed_paths exist (WARN only — paths may be created by the task)
    # -------------------------------------------------------------------------
    for task in all_tasks:
        tid = task.get("task_id", task.get("id", "?"))
        allowed = task.get("allowed_paths", [])
        if isinstance(allowed, str):
            allowed = [allowed]
        for ap in (allowed or []):
            full = _REPO_ROOT / ap
            if not full.exists():
                findings.append(("WARN", "ALLOWED_PATH_MISSING",
                                 f"Task {tid}: allowed_path '{ap}' does not exist yet "
                                 f"(may be created by task execution)"))

    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------
    fail_count = sum(1 for level, _, _ in findings if level == "FAIL")
    warn_count = sum(1 for level, _, _ in findings if level == "WARN")

    if not findings:
        print(f"validate_execution_plan: ALL CHECKS PASS — plan={plan_path.name}")
        return 0

    for level, check, msg in findings:
        print(f"  [{level}] {check}: {msg}")

    print(f"\nSummary: {fail_count} FAIL, {warn_count} WARN")

    if strict and warn_count > 0:
        return 1
    return 1 if fail_count > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_path", help="Path to the YAML execution plan to validate")
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat WARN findings as FAIL (default: only FAIL findings return exit 1)"
    )
    args = parser.parse_args()

    exit_code = validate_plan(Path(args.plan_path), strict=args.strict)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
