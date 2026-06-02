"""
grade_declared_work.py — Item-Level Grading Engine
Grades each declared work item based on inspection results.

Grade levels:
  ACCEPTED — evidence found, criteria met, tests passed
  ACCEPTED_WITH_WARNINGS — core evidence exists, minor limitation
  REWORK_REQUIRED — missing evidence, failed test, incomplete
  REJECTED — contradicted by evidence, unsafe shortcut, fabricated proof
  BLOCKED_EXTERNAL_GATE — requires true external gate (credentials, push, Gate 8/11)
  NOT_ATTEMPTED — work item not attempted
  NOT_IN_SCOPE — not required and no claim made
  OVERCLAIMED — declared complete but evidence missing or shallow

Exit codes:
  0 — grading complete, no critical rework
  3 — grading complete, critical rework exists
  9 — unexpected error
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

EXTERNAL_GATE_KEYWORDS = {
    "gate_8", "gate_11", "gate8", "gate11", "g8", "g11",
    "pypi", "nuget", "github_release", "publication",
    "push", "merge", "deploy", "credentials",
    "commercial_product_ready",
}


def grade_item(item_inspection: dict, test_results: dict) -> dict:
    """Grade a single work item from its inspection."""
    item_id = item_inspection["item_id"]
    declared_status = item_inspection["declared_status"]
    has_evidence = item_inspection["has_evidence"]
    has_tests = item_inspection["has_tests"]
    missing_paths = item_inspection.get("evidence_paths_missing", [])
    found_paths = item_inspection.get("evidence_paths_found", [])

    test_failed = test_results.get("failed", 0) > 0 or test_results.get("errors", 0) > 0

    grade = {
        "item_id": item_id,
        "item_title": item_id,  # Will be enriched from declaration
        "declared_status": declared_status,
        "supervisor_grade": "NOT_ATTEMPTED",
        "evidence_found": has_evidence,
        "evidence_paths": found_paths,
        "tests_supporting": item_inspection.get("tests_declared", []),
        "tests_missing": [],
        "acceptance_criteria_met": [],
        "acceptance_criteria_failed": [],
        "required_rework": "",
        "can_autonomously_repair": False,
        "next_prompt_instruction": "",
    }

    # Gate-blocked items
    if declared_status == "blocked_external_gate":
        grade["supervisor_grade"] = "BLOCKED_EXTERNAL_GATE"
        grade["next_prompt_instruction"] = "This item requires external gate approval. Do not attempt."
        return grade

    # Not started
    if declared_status == "not_started":
        grade["supervisor_grade"] = "NOT_ATTEMPTED"
        grade["next_prompt_instruction"] = "This item was not attempted. Include in next sprint if still needed."
        return grade

    # Declared complete but no evidence = OVERCLAIMED
    if declared_status == "completed" and not has_evidence:
        grade["supervisor_grade"] = "OVERCLAIMED"
        grade["required_rework"] = f"Item declared completed but no evidence found. Provide evidence at declared paths."
        grade["can_autonomously_repair"] = True
        grade["next_prompt_instruction"] = f"REWORK: Provide actual evidence for {item_id}. Status-only claims are not accepted."
        return grade

    # Declared complete with evidence but missing some paths
    if declared_status == "completed" and missing_paths:
        grade["supervisor_grade"] = "REWORK_REQUIRED"
        grade["required_rework"] = f"Missing evidence paths: {', '.join(missing_paths)}"
        grade["can_autonomously_repair"] = True
        grade["acceptance_criteria_failed"] = [f"Missing: {p}" for p in missing_paths]
        grade["next_prompt_instruction"] = f"REWORK: Create missing evidence files: {', '.join(missing_paths)}"
        return grade

    # Declared partial
    if declared_status == "partial":
        if has_evidence:
            grade["supervisor_grade"] = "ACCEPTED_WITH_WARNINGS"
            grade["next_prompt_instruction"] = f"Item partially complete. Continue work in next sprint."
        else:
            grade["supervisor_grade"] = "REWORK_REQUIRED"
            grade["required_rework"] = "Partial work claimed but no evidence found."
            grade["can_autonomously_repair"] = True
            grade["next_prompt_instruction"] = f"REWORK: Provide evidence for partial work on {item_id}."
        return grade

    # Declared complete with evidence and no missing paths
    if declared_status == "completed" and has_evidence and not missing_paths:
        if test_failed and has_tests:
            grade["supervisor_grade"] = "REWORK_REQUIRED"
            grade["required_rework"] = "Tests failed. Fix test failures before acceptance."
            grade["can_autonomously_repair"] = True
            grade["next_prompt_instruction"] = f"REWORK: Fix failing tests for {item_id}."
        else:
            # D92-03 fix: Deep verification — check evidence content, not just existence
            criteria_met = ["Evidence found", "No missing paths"]
            criteria_failed = []

            # Check test files contain actual test methods
            tests_with_content = item_inspection.get("tests_with_content", [])
            tests_empty_or_stub = item_inspection.get("tests_empty_or_stub", [])
            if tests_empty_or_stub:
                criteria_failed.append(f"Test files appear empty/stub: {tests_empty_or_stub}")
            elif has_tests and tests_with_content:
                criteria_met.append(f"Test content verified ({len(tests_with_content)} files)")
            elif has_tests:
                criteria_met.append("Tests declared (content check not run)")

            # Check acceptance criteria patterns in evidence
            criteria_verified = item_inspection.get("acceptance_criteria_verified", False)
            criteria_pattern = item_inspection.get("acceptance_criteria_pattern", "")
            if criteria_pattern and criteria_verified:
                criteria_met.append(f"Acceptance criteria verified: {criteria_pattern[:60]}")
            elif criteria_pattern and not criteria_verified:
                criteria_failed.append(f"Acceptance criteria pattern not found: {criteria_pattern[:60]}")

            if criteria_failed:
                grade["supervisor_grade"] = "ACCEPTED_WITH_WARNINGS"
                grade["acceptance_criteria_met"] = criteria_met
                grade["acceptance_criteria_failed"] = criteria_failed
                grade["next_prompt_instruction"] = f"Item accepted with warnings: {'; '.join(criteria_failed)}"
            else:
                grade["supervisor_grade"] = "ACCEPTED"
                grade["acceptance_criteria_met"] = criteria_met

    return grade


def grade_all(inspection: dict, declaration: dict) -> dict:
    """Grade all items from inspection and declaration."""
    test_results = inspection.get("test_results", {})
    item_inspections = inspection.get("item_inspections", [])

    # Enrich with declaration data
    decl_items = {item["item_id"]: item for item in declaration.get("planned_work_items", [])}

    grades = []
    for ii in item_inspections:
        g = grade_item(ii, test_results)
        # Enrich title from declaration
        decl_item = decl_items.get(g["item_id"], {})
        g["item_title"] = decl_item.get("title", g["item_id"])
        grades.append(g)

    accepted = [g["item_id"] for g in grades if g["supervisor_grade"] in ("ACCEPTED", "ACCEPTED_WITH_WARNINGS")]
    rework = [g["item_id"] for g in grades if g["supervisor_grade"] in ("REWORK_REQUIRED", "OVERCLAIMED")]
    rejected = [g["item_id"] for g in grades if g["supervisor_grade"] == "REJECTED"]
    overclaimed = [g["item_id"] for g in grades if g["supervisor_grade"] == "OVERCLAIMED"]
    blocked = [g["item_id"] for g in grades if g["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"]

    critical_rework = len([g for g in grades if g["supervisor_grade"] in ("REJECTED", "OVERCLAIMED")])
    has_critical = critical_rework > 0 or test_results.get("failed", 0) > 0

    autonomous_continue = not has_critical
    stop_reason = ""
    if has_critical:
        stop_reason = f"Critical rework: {critical_rework} items overclaimed/rejected, {test_results.get('failed', 0)} test failures"

    overall_verdict = "ACCEPTED"
    if rejected:
        overall_verdict = "REJECTED"
    elif overclaimed or any(g["supervisor_grade"] == "REWORK_REQUIRED" for g in grades):
        overall_verdict = "ACCEPTED_WITH_REWORK"
    elif all(g["supervisor_grade"] in ("ACCEPTED", "ACCEPTED_WITH_WARNINGS", "NOT_IN_SCOPE", "BLOCKED_EXTERNAL_GATE") for g in grades):
        overall_verdict = "ACCEPTED"

    return {
        "run_id": inspection.get("run_id", "unknown"),
        "sprint_id": inspection.get("sprint_id", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "declaration_path": "",
        "evidence_root": inspection.get("evidence_root", ""),
        "overall_verdict": overall_verdict,
        "item_grades": grades,
        "accepted_items": accepted,
        "rework_items": rework,
        "rejected_items": rejected,
        "overclaimed_items": overclaimed,
        "forward_work_items": [],
        "autonomous_continue": autonomous_continue,
        "stop_reason": stop_reason,
        "cycle_number": 1,
        "critical_rework_count": critical_rework,
    }


def write_outputs(review: dict, output_dir: Path) -> None:
    """Write grading outputs to review directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full review
    (output_dir / "supervisor-review.json").write_text(
        json.dumps(review, indent=2), encoding="utf-8"
    )

    # Item grades
    grades_yaml = yaml.dump(review["item_grades"], default_flow_style=False, sort_keys=False)
    (output_dir / "item-grades.yaml").write_text(grades_yaml, encoding="utf-8")
    (output_dir / "item-grades.json").write_text(
        json.dumps(review["item_grades"], indent=2), encoding="utf-8"
    )

    # Accepted items
    accepted = [g for g in review["item_grades"] if g["supervisor_grade"] in ("ACCEPTED", "ACCEPTED_WITH_WARNINGS")]
    (output_dir / "accepted-items.yaml").write_text(
        yaml.dump(accepted, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )

    # Rework items
    rework = [g for g in review["item_grades"] if g["supervisor_grade"] in ("REWORK_REQUIRED", "OVERCLAIMED")]
    (output_dir / "rework-items.yaml").write_text(
        yaml.dump(rework, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )

    # Rejected items
    rejected = [g for g in review["item_grades"] if g["supervisor_grade"] == "REJECTED"]
    (output_dir / "rejected-items.yaml").write_text(
        yaml.dump(rejected, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )

    # Overclaimed items
    overclaimed = [g for g in review["item_grades"] if g["supervisor_grade"] == "OVERCLAIMED"]
    (output_dir / "overclaimed-items.yaml").write_text(
        yaml.dump(overclaimed, default_flow_style=False, sort_keys=False), encoding="utf-8"
    )

    # Review markdown
    lines = [
        f"# Supervisor Review: {review['run_id']}",
        f"Sprint: {review['sprint_id']}",
        f"Timestamp: {review['timestamp']}",
        f"Overall Verdict: {review['overall_verdict']}",
        f"Autonomous Continue: {review['autonomous_continue']}",
        "",
        f"## Summary",
        f"- Accepted: {len(review['accepted_items'])}",
        f"- Rework: {len(review['rework_items'])}",
        f"- Rejected: {len(review['rejected_items'])}",
        f"- Overclaimed: {len(review['overclaimed_items'])}",
        f"- Critical Rework: {review['critical_rework_count']}",
        "",
        "## Item Grades",
    ]
    for g in review["item_grades"]:
        lines.append(f"- **{g['item_id']}** ({g['item_title']}): {g['supervisor_grade']}")
        if g.get("required_rework"):
            lines.append(f"  - Rework: {g['required_rework']}")
    (output_dir / "supervisor-review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade declared work items")
    parser.add_argument("--inspection", type=Path, required=True, help="Path to inspection JSON")
    parser.add_argument("--declaration", type=Path, required=True, help="Path to evidence-declaration.yaml")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for grades")
    args = parser.parse_args()

    inspection = json.loads(args.inspection.read_text(encoding="utf-8"))
    declaration = yaml.safe_load(args.declaration.read_text(encoding="utf-8")) or {}

    review = grade_all(inspection, declaration)
    review["declaration_path"] = str(args.declaration)
    write_outputs(review, args.output_dir)

    print(f"GRADING_COMPLETE: {review['overall_verdict']}")
    print(f"  Accepted: {len(review['accepted_items'])}")
    print(f"  Rework: {len(review['rework_items'])}")
    print(f"  Overclaimed: {len(review['overclaimed_items'])}")
    print(f"  Autonomous Continue: {review['autonomous_continue']}")

    return 3 if review["critical_rework_count"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
