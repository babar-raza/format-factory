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
