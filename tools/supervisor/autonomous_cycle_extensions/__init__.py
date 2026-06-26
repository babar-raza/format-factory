"""autonomous_cycle_extensions — optional session-start hooks for autonomous_cycle.py.

These hooks extend autonomous_cycle.py without modifying it (LOC cap workaround).
To activate a hook, add a 2-line try/import block at the desired step in autonomous_cycle.py:

    try:
        from autonomous_cycle_extensions.knowledge_freshness_hook import run_hook
        run_hook()
    except Exception:
        pass  # Non-blocking — never fail the sprint

TC-P3-002 note: wiring into autonomous_cycle.py requires LOC reclaim sprint first
(current cap: 2465/2465, zero headroom). See TC-P3-002-SUB-001.

NOTE: This package shadows the standalone autonomous_cycle_extensions.py module.
Functions defined in the standalone .py file are re-exported at the BOTTOM of this
file via importlib, with a guard that does NOT override locally-defined functions.
"""
import json
import importlib.util as _ilu
from pathlib import Path
from typing import Optional


def check_lane_conflicts(
    declared_lane: str,
    changed_files: list,
    policies_path: Optional[Path] = None,
) -> list:
    """Preventive lane conflict guard (TC-MACH-LANE-001, WI-TC-S55-003).

    Args:
        declared_lane: The lane declared in the sprint (e.g. "MULTI_LANE",
                       "PYTHON_PRODUCT", "SUPERVISOR"). Empty string = no lane.
        changed_files: List of file paths changed in the declaration.
        policies_path: Optional path to .supervisor/policies.yaml for custom rules.

    Returns:
        List of conflict strings (empty = no conflicts, add to hard_stops if non-empty).

    Rules:
        - MULTI_LANE or empty lane: no lane conflicts possible, returns [].
        - Single declared lane: returns conflicts for files belonging to different lanes.
        - CRITICAL violations (product files in governance lanes) prefixed "CRITICAL:".
    """
    if not declared_lane or declared_lane.upper() == "MULTI_LANE":
        return []

    try:
        import sys as _sys
        _sup = str(Path(__file__).resolve().parents[1])
        if _sup not in _sys.path:
            _sys.path.insert(0, _sup)
        from lane_enforcement_validator import LaneEnforcementValidator  # type: ignore
    except Exception:
        return []  # Non-blocking if validator unavailable

    validator = LaneEnforcementValidator()
    fake_decl = {"changed_files": changed_files}
    result = validator.validate(fake_decl, declared_lane=declared_lane)
    if result.passed:
        return []

    conflicts = []
    for v in result.violations:
        prefix = "CRITICAL:" if v in result.critical_violations else ""
        conflicts.append(f"LANE_CONFLICT {prefix}{v}")
    return conflicts


_TERMINAL_TASK_STATUSES = frozenset({"CLOSED", "SUPERSEDED", "EXCLUDED"})


def find_next_eligible_task_in_plan(plan_path: str) -> "dict | None":
    """TC-TCF-005: Find the first open (non-terminal) taskcard in a plan.

    Returns {"tc_id": ..., "plan_path": ..., "status": ...} or None.
    """
    try:
        import sys as _sys
        _sup = str(Path(__file__).resolve().parents[1])
        if _sup not in _sys.path:
            _sys.path.insert(0, _sup)
        from lifecycle_audit import parse_plan_taskcards  # type: ignore[import]
        tcs = parse_plan_taskcards(plan_path)
        for tc in tcs:
            if tc.get("status", "OPEN") not in _TERMINAL_TASK_STATUSES:
                return {
                    "tc_id": tc.get("tc_id") or tc.get("id", "UNKNOWN"),
                    "plan_path": plan_path,
                    "status": tc.get("status", "OPEN"),
                }
        return None
    except Exception as exc:
        print(f"  [TCF-005] find_next_eligible_task_in_plan error: {exc}")
        return None


def scan_closed_plan_test_regression(repo_root: "Path | None" = None) -> "list[dict]":
    """TC-TCF-005: Detect test regressions in evidence-review.json.

    Checks for previously-PASS items that are now FAIL. Non-blocking — returns [] on error.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    result: list = []
    try:
        review_path = Path(repo_root) / "reports" / "supervisor" / "evidence-review.json"
        if not review_path.exists():
            return result
        import json as _json
        review = _json.loads(review_path.read_text(encoding="utf-8", errors="replace"))
        items = review if isinstance(review, list) else review.get("items", [])
        for item in items:
            if not isinstance(item, dict):
                continue
            grade = str(item.get("grade", "")).upper()
            prev_grade = str(item.get("previous_grade", grade)).upper()
            if prev_grade == "PASS" and grade in ("FAIL", "NEEDS_REWORK"):
                result.append({
                    "item_id": item.get("id") or item.get("work_item_id"),
                    "format": item.get("format"),
                    "grade": grade,
                    "previous_grade": prev_grade,
                    "description": str(item.get("description", ""))[:120],
                })
    except Exception as exc:
        print(f"  [TCF-005] scan_closed_plan_test_regression warning: {exc}")
    return result


def scan_closure_evidence_invalidation(repo_root: "Path | None" = None) -> "list[dict]":
    """TC-TCF-005: Find terminal closure records whose plan file is now missing.

    Scans .local/evidences/plan-closures/ for terminal_closure_record.json files.
    Non-blocking — returns [] on error.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    result: list = []
    try:
        import json as _json
        closures_dir = Path(repo_root) / ".local" / "evidences" / "plan-closures"
        if not closures_dir.exists():
            return result
        for record_file in closures_dir.rglob("terminal_closure_record.json"):
            try:
                record = _json.loads(record_file.read_text(encoding="utf-8", errors="replace"))
                plan_path = record.get("plan_path", "")
                plan_exists = Path(plan_path).exists() if plan_path else False
                open_tcs = record.get("open_taskcards", [])
                if not plan_exists or open_tcs:
                    result.append({
                        "record_file": str(record_file),
                        "plan_path": plan_path,
                        "plan_file_exists": plan_exists,
                        "open_taskcards_in_record": open_tcs,
                        "invalidation_reason": (
                            "plan_file_missing" if not plan_exists
                            else "open_taskcards_in_record"
                        ),
                    })
            except Exception:
                continue
    except Exception as exc:
        print(f"  [TCF-005] scan_closure_evidence_invalidation warning: {exc}")
    return result


def enrich_goals_with_compiled_taskcards(all_goals: list, repo_root: Path) -> None:
    """TC-SH-003: Enrich gap-ledger goals with compiled taskcard metadata.

    Reads compiled-gap-taskcards.json and adds compiled_taskcard_id/path
    to matching goals by gap_id. Also sets gap_ledger_ref (TC-GUARD-001 requirement).
    Best-effort: errors are silently ignored.
    """
    try:
        compiled_path = repo_root / ".local" / "supervisor" / "compiled-gap-taskcards.json"
        if not compiled_path.exists():
            return
        cgd = json.loads(compiled_path.read_text(encoding="utf-8"))
        index = {}
        for cg in cgd.get("compiled", []):
            gid = cg.get("gap_id", "")
            if gid and cg.get("status") == "compiled":
                index[gid] = cg
        for goal in all_goals:
            gid = goal.get("gap_id", "")
            if gid in index:
                goal["compiled_taskcard_id"] = index[gid].get("taskcard_id")
                goal["compiled_taskcard_path"] = index[gid].get("taskcard_path")
                goal["gap_ledger_ref"] = gid  # TC-GUARD-001 requires this field
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Re-export functions from the standalone autonomous_cycle_extensions.py
# (shadowed by this package directory; loaded explicitly via importlib)
# Guard: only exports functions NOT already defined locally in this package.
# This preserves the package's local definitions (e.g. check_lane_conflicts)
# while filling gaps for functions only in the standalone file (e.g. check_sal_staleness).
# ---------------------------------------------------------------------------
try:
    _standalone_path = Path(__file__).resolve().parents[1] / "autonomous_cycle_extensions.py"
    if _standalone_path.exists():
        _spec = _ilu.spec_from_file_location("_ace_standalone", _standalone_path)
        _ace_mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_ace_mod)  # type: ignore[union-attr]
        import types as _types
        _local_names = set(k for k, v in list(globals().items())
                           if isinstance(v, _types.FunctionType) and not k.startswith("_"))
        for _name, _obj in vars(_ace_mod).items():
            if (not _name.startswith("_")
                    and callable(_obj)
                    and isinstance(_obj, _types.FunctionType)
                    and _name not in _local_names):
                globals()[_name] = _obj
        del _types, _local_names, _name, _obj, _ace_mod, _spec, _standalone_path
except Exception:
    pass  # Non-blocking; locally-defined package functions remain available
