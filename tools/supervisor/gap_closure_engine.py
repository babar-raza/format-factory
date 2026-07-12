"""gap_closure_engine.py — Close gaps in gap-ledger.json based on graded evidence.

Replaces one-off scripts (close_xcf_zst_gaps.py, close_comm_gaps.py, etc.)
with pipeline-integrated automated closure.

TC-FL-001: Phase 1 of the feedback loop redesign (pure-knitting-dusk plan).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_ACCEPTED_GRADES = frozenset({
    "ACCEPTED_VERIFIED",
    "ACCEPTED",
    "ACCEPTED_WITH_LIMITATIONS",
    "ACCEPTED_WITH_WARNINGS",
})


def close_gaps_from_grades(
    review: dict,
    declaration: dict,
    gap_ledger_path: Path,
    sprint_id: str,
) -> dict:
    """Main entry point. Returns closure result dict.

    Reads graded items from *review*, correlates with gap_ledger_ref from
    *declaration*, and closes qualifying gaps in the ledger file.
    """
    matches = _match_grades_to_gaps(review, declaration)
    if not matches:
        return {"closed": 0, "skipped": 0, "matches": 0, "closures_applied": []}

    try:
        ledger = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"closed": 0, "skipped": 0, "matches": len(matches),
                "error": str(exc), "closures_applied": []}

    gap_by_id = {g["gap_id"]: g for g in ledger.get("gaps", [])}
    test_results = declaration.get("test_results", {})

    closures: list[tuple[str, dict]] = []
    skipped = 0

    for gap_id, grade_info in matches:
        gap = gap_by_id.get(gap_id)
        if not gap or gap.get("status") == "closed":
            skipped += 1
            continue
        if _evaluate_closure_criteria(grade_info, test_results):
            closures.append((gap_id, grade_info))
        else:
            skipped += 1

    result = _apply_closures(gap_ledger_path, ledger, closures, sprint_id)
    result["matches"] = len(matches)
    result["skipped"] = skipped
    result["closures_applied"] = closures
    _append_closure_log(gap_ledger_path.parent, closures, sprint_id)
    return result


def _match_grades_to_gaps(review: dict, declaration: dict) -> list[tuple[str, dict]]:
    """Correlate graded items with their gap_ledger_ref."""
    item_grades = {g["item_id"]: g for g in review.get("item_grades", [])}
    matches: list[tuple[str, dict]] = []
    for item in declaration.get("planned_work_items", []):
        gap_ref = item.get("gap_ledger_ref") or item.get("gap_ref")
        if not gap_ref:
            continue
        item_id = item.get("item_id", "")
        grade = item_grades.get(item_id)
        if not grade:
            continue
        matches.append((gap_ref, grade))
    return matches


def _evaluate_closure_criteria(grade_info: dict, test_results: dict) -> bool:
    """Deterministic gate: grade must be ACCEPTED-tier + test evidence + no failures."""
    grade = grade_info.get("supervisor_grade", "")
    if grade not in _ACCEPTED_GRADES:
        return False
    # Must have at least 1 test evidence path
    evidence_paths = grade_info.get("evidence_paths_found", [])
    test_evidence = [p for p in evidence_paths if "/test_" in p or "\\test_" in p]
    if not test_evidence:
        return False
    # No test failures for this item
    if grade_info.get("tests_failing", 0) > 0:
        return False
    return True


def _apply_closures(
    gap_ledger_path: Path,
    ledger: dict,
    closures: list[tuple[str, dict]],
    sprint_id: str,
) -> dict:
    """Atomically close gaps in the ledger file."""
    if not closures:
        return {"closed": 0}

    gap_by_id = {g["gap_id"]: g for g in ledger.get("gaps", [])}
    now = datetime.now(timezone.utc).isoformat()

    for gap_id, grade_info in closures:
        gap = gap_by_id.get(gap_id)
        if not gap:
            continue
        gap["status"] = "closed"
        gap["closed_by_sprint"] = sprint_id
        gap["closed_at"] = now
        gap["closed_by_engine"] = True
        gap["closure_evidence"] = {
            "work_item_id": grade_info.get("item_id", ""),
            "supervisor_grade": grade_info.get("supervisor_grade", ""),
            "evidence_paths": grade_info.get("evidence_paths_found", []),
            "test_pass_count": grade_info.get("tests_supporting", 0),
            "test_fail_count": grade_info.get("tests_failing", 0),
        }

    gap_ledger_path.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {"closed": len(closures)}


def close_implementation_verified_gaps(
    gap_ledger_path: Path,
    test_root: Path,
    sprint_id: str,
    dry_run: bool = False,
) -> dict:
    """TC-BOOL-001: Close gaps whose current_state is 'implementation_verified'.

    This is the second entry point for gaps that were excluded from work item
    selection (because _SKIP_STATUSES filters them) and thus never pass through
    the declared-sprint closure path in close_gaps_from_grades().

    Closure conditions (ALL must hold):
    1. status == "open"
    2. current_state == "implementation_verified"
    3. A function name derived from related_capability_id appears in >= 1 test file

    If no test file is found: promotes current_state to
    "implementation_verified_no_tests" (re-enters work queue for test writing).
    """
    try:
        ledger = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"closed": 0, "no_tests_found": 0, "skipped": 0, "error": str(exc)}

    gaps = ledger.get("gaps", [])
    candidates = [
        g for g in gaps
        if g.get("status") == "open" and g.get("current_state") == "implementation_verified"
    ]

    if not candidates:
        return {"closed": 0, "no_tests_found": 0, "skipped": 0}

    # Build test file cache: path → text content
    test_files: dict[str, str] = {}
    for tf in test_root.rglob("*.py"):
        try:
            test_files[str(tf)] = tf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass

    now = datetime.now(timezone.utc).isoformat()
    closed_ids: list[str] = []
    promoted_ids: list[str] = []
    closure_log_entries: list[dict] = []

    for gap in candidates:
        gap_id = gap.get("gap_id", "")
        cap_id = gap.get("related_capability_id", "")

        # Derive function name: extract the capability name segment and normalize
        fn_name = _derive_function_name(cap_id, gap_id)

        # Search test files for actual function references (not just comments)
        matching_files = _scan_test_files_for_function(fn_name, test_files)

        if matching_files:
            if not dry_run:
                gap["status"] = "closed"
                gap["closed_by_sprint"] = sprint_id
                gap["closed_at"] = now
                gap["closed_by_engine"] = True
                gap["closure_method"] = "implementation_verified_test_scan"
                gap["closure_evidence"] = {
                    "test_files_found": matching_files[:5],
                    "call_count": sum(
                        test_files[f].count(fn_name)
                        for f in matching_files if f in test_files
                    ),
                    "scan_basis": f"grep for '{fn_name}' in test files",
                }
            closed_ids.append(gap_id)
            closure_log_entries.append({
                "gap_id": gap_id,
                "sprint_id": sprint_id,
                "closed_at": now,
                "grade": "IMPLEMENTATION_VERIFIED_TEST_SCAN",
                "item_id": f"auto-close:{gap_id}",
                "fn_name": fn_name,
                "test_files": matching_files[:3],
            })
        else:
            # No test found — promote to implementation_verified_no_tests
            if not dry_run:
                gap["current_state"] = "implementation_verified_no_tests"
            promoted_ids.append(gap_id)

    if not dry_run and (closed_ids or promoted_ids):
        gap_ledger_path.write_text(
            json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if closure_log_entries:
            _append_closure_log_entries(gap_ledger_path.parent, closure_log_entries)

    return {
        "closed": len(closed_ids),
        "no_tests_found": len(promoted_ids),
        "skipped": len(candidates) - len(closed_ids) - len(promoted_ids),
        "closed_ids": closed_ids,
        "promoted_ids": promoted_ids,
        "dry_run": dry_run,
    }


def _derive_function_name(related_capability_id: str, gap_id: str) -> str:
    """Derive a searchable function name from related_capability_id or gap_id.

    Pattern: DIF-FOSS-DIF_BOOLEAN_CELL_COUNT-SRC-001
    Extract middle segment (DIF_BOOLEAN_CELL_COUNT), lowercase it → dif_boolean_cell_count
    """
    for candidate in (related_capability_id, gap_id):
        if not candidate:
            continue
        parts = candidate.split("-")
        # Find the longest segment that looks like a capability name (has underscores)
        for part in parts:
            if "_" in part and len(part) > 3:
                return part.lower().rstrip("_")
    # Fallback: use full id lowercased
    return (related_capability_id or gap_id).lower().replace("-", "_")


def _scan_test_files_for_function(fn_name: str, test_files: dict[str, str]) -> list[str]:
    """Return list of test file paths that contain a non-comment call to fn_name."""
    import re
    # Pattern: fn_name appears as a non-comment call (not in a line starting with #)
    call_pattern = re.compile(r"(?m)^(?!\s*#).*\b" + re.escape(fn_name) + r"\b")
    matches = []
    for path, content in test_files.items():
        if call_pattern.search(content):
            matches.append(path)
    return matches


def _append_closure_log_entries(output_dir: Path, entries: list[dict]) -> None:
    """Append entries to gap-closure-log.json."""
    log_path = output_dir / "gap-closure-log.json"
    log: list[dict] = []
    if log_path.exists():
        try:
            log = json.loads(log_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    log.extend(entries)
    log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")


def _append_closure_log(
    output_dir: Path, closures: list[tuple[str, dict]], sprint_id: str
) -> None:
    """Append-only audit trail of automated closures."""
    log_path = output_dir / "gap-closure-log.json"
    log: list[dict] = []
    if log_path.exists():
        try:
            log = json.loads(log_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    now = datetime.now(timezone.utc).isoformat()
    for gap_id, grade_info in closures:
        log.append({
            "gap_id": gap_id,
            "sprint_id": sprint_id,
            "closed_at": now,
            "grade": grade_info.get("supervisor_grade", ""),
            "item_id": grade_info.get("item_id", ""),
        })

    log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
