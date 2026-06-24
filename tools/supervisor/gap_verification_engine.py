"""gap_verification_engine.py — Multi-level gap verification.

Level 0: test file exists (filename grep)
Level 1: matching tests pass (test execution result)
Level 2: graded declaration cites gap with ACCEPTED evidence (evidence chain)

TC-FL-012: Phase 5 of the feedback loop redesign (pure-knitting-dusk plan).
"""
from __future__ import annotations

from pathlib import Path

_ACCEPTED_GRADES = frozenset({
    "ACCEPTED_VERIFIED",
    "ACCEPTED",
    "ACCEPTED_WITH_LIMITATIONS",
    "ACCEPTED_WITH_WARNINGS",
})


def verify_level_0(format_name: str, capability_name: str, repo_root: Path) -> dict:
    """Does a test file exist that references this capability?"""
    test_dir = repo_root / "tests" / "python" / format_name.lower()
    if not test_dir.is_dir():
        return {"level": 0, "verdict": "FAIL", "reason": f"test dir not found: {test_dir}",
                "test_files": []}
    cap_lower = capability_name.lower().replace(" ", "_")
    matches = [p.name for p in test_dir.rglob("test_*.py")
               if cap_lower in p.name.lower()]
    if matches:
        return {"level": 0, "verdict": "PASS", "test_files": matches}
    return {"level": 0, "verdict": "FAIL", "reason": "no test file matches capability name",
            "test_files": []}


def verify_level_1(
    format_name: str, capability_name: str, test_results: dict, repo_root: Path
) -> dict:
    """Do matching tests execute and pass?"""
    l0 = verify_level_0(format_name, capability_name, repo_root)
    if l0["verdict"] != "PASS":
        return {"level": 1, "verdict": "FAIL", "reason": "L0 prerequisite failed",
                "level_0": l0}
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    if passed > 0 and failed == 0:
        return {"level": 1, "verdict": "PASS", "passed": passed, "failed": failed,
                "level_0": l0}
    return {"level": 1, "verdict": "FAIL", "passed": passed, "failed": failed,
            "level_0": l0}


def verify_level_2(grade_info: dict) -> dict:
    """Is there a graded declaration that cites this gap with ACCEPTED evidence?"""
    grade = grade_info.get("supervisor_grade", "")
    accepted = grade in _ACCEPTED_GRADES
    return {
        "level": 2,
        "verdict": "PASS" if accepted else "FAIL",
        "grade": grade,
        "item_id": grade_info.get("item_id", ""),
        "evidence_paths": grade_info.get("evidence_paths_found", []),
    }


def verify_closed_gaps(
    closure_result: dict,
    test_results: dict,
    declaration: dict,
    repo_root: Path,
) -> list[dict]:
    """Verify all gaps that were just closed. Returns verification records.

    Gap closures already required ACCEPTED grade + test evidence (L2 by construction).
    This function adds explicit L0/L1/L2 records for the audit trail.
    """
    verifications: list[dict] = []
    closures = closure_result.get("closures_applied", [])
    if not closures:
        return verifications

    for gap_id, grade_info in closures:
        # Extract format and capability from gap_id
        # e.g., GAP-CSV-FOSS-PROBE_CSV-001 → format=csv, capability=probe_csv
        parts = gap_id.split("-")
        fmt = parts[1].lower() if len(parts) > 1 else ""
        cap = parts[3].replace("_", " ").title() if len(parts) > 3 else ""

        if fmt:
            l0 = verify_level_0(fmt, cap, repo_root)
            l1 = verify_level_1(fmt, cap, test_results, repo_root)
        else:
            l0 = {"level": 0, "verdict": "SKIP", "reason": "cannot parse format from gap_id"}
            l1 = {"level": 1, "verdict": "SKIP", "reason": "cannot parse format from gap_id"}

        l2 = verify_level_2(grade_info)

        max_level = 0
        if l0.get("verdict") == "PASS":
            max_level = 0
        if l1.get("verdict") == "PASS":
            max_level = 1
        if l2.get("verdict") == "PASS":
            max_level = 2

        verifications.append({
            "gap_id": gap_id,
            "verification_level": max_level,
            "level_0": l0,
            "level_1": l1,
            "level_2": l2,
        })

    return verifications
