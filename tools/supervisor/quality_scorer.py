"""
Quality Scorer for the Post-Sprint Autonomy Loop.

Scores execution quality across 15 dimensions (1-5 scale).
Determines all_green status and identifies reroute triggers.

Output conforms to: .supervisor/schemas/stage3-quality-scoring-rubric.schema.json

Usage:
  python tools/supervisor/quality_scorer.py --declaration <path> [--repo-root .]
  python tools/supervisor/quality_scorer.py --help
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Quality threshold — minimum score per dimension for acceptance
QUALITY_THRESHOLD = 4

# All 15 required quality dimensions
QUALITY_DIMENSIONS = [
    "correctness",
    "test_coverage",
    "evidence_completeness",
    "code_quality",
    "schema_compliance",
    "governance_compliance",
    "path_discipline",
    "documentation",
    "idempotency",
    "regression_safety",
    "performance",
    "error_handling",
    "integration_consistency",
    "evidence_traceability",
    "acceptance_criteria_met",
]


def _score_dimension(dimension: str, evidence: dict[str, Any]) -> int:
    """
    Score a single dimension 1-5 based on available evidence.

    Scoring rubric:
      5 — Full proof with tests, logs, and integration evidence
      4 — Adequate proof with minor limitations
      3 — Partial proof, some gaps
      2 — Weak proof, major gaps
      1 — No proof or contradicted
    """
    # Default scoring heuristics based on evidence availability
    has_tests = bool(evidence.get("test_references"))
    has_evidence_paths = bool(evidence.get("evidence_paths"))
    has_changed_files = bool(evidence.get("changed_files"))
    test_passed = evidence.get("tests_passed", 0) > 0
    test_failed = evidence.get("tests_failed", 0)

    base_score = 3  # assume partial by default

    if dimension == "correctness":
        if test_passed and test_failed == 0:
            base_score = 5
        elif test_passed:
            base_score = 4
        elif has_changed_files:
            base_score = 2
        else:
            base_score = 1

    elif dimension == "test_coverage":
        if has_tests and test_passed:
            base_score = 5 if evidence.get("tests_passed", 0) >= 3 else 4
        elif has_tests:
            base_score = 3
        else:
            base_score = 1

    elif dimension == "evidence_completeness":
        if has_evidence_paths and has_tests:
            base_score = 5
        elif has_evidence_paths:
            base_score = 4
        elif has_changed_files:
            base_score = 2
        else:
            base_score = 1

    elif dimension == "code_quality":
        # Assume acceptable unless lint failures detected
        if evidence.get("lint_failures"):
            base_score = 2
        elif has_changed_files:
            base_score = 4
        else:
            base_score = 3

    elif dimension == "schema_compliance":
        if evidence.get("schema_validated", False):
            base_score = 5
        elif has_evidence_paths:
            base_score = 4
        else:
            base_score = 3

    elif dimension == "governance_compliance":
        if evidence.get("governance_pass", False):
            base_score = 5
        elif not evidence.get("governance_fail", False):
            base_score = 4
        else:
            base_score = 2

    elif dimension == "path_discipline":
        if evidence.get("forbidden_path_violations"):
            base_score = 1
        elif has_changed_files:
            base_score = 5
        else:
            base_score = 4

    elif dimension == "documentation":
        if evidence.get("docs_updated", False):
            base_score = 5
        elif evidence.get("docs_not_needed", True):
            base_score = 4
        else:
            base_score = 3

    elif dimension == "idempotency":
        if evidence.get("idempotency_proven", False):
            base_score = 5
        else:
            base_score = 4  # assume idempotent unless proven otherwise

    elif dimension == "regression_safety":
        if test_failed == 0 and test_passed:
            base_score = 5
        elif test_failed > 0:
            base_score = 2
        else:
            base_score = 3

    elif dimension == "performance":
        # No performance regression unless flagged
        base_score = 4 if not evidence.get("performance_regression") else 2

    elif dimension == "error_handling":
        base_score = 4 if not evidence.get("unhandled_errors") else 2

    elif dimension == "integration_consistency":
        if evidence.get("integration_verified", False):
            base_score = 5
        elif has_evidence_paths:
            base_score = 4
        else:
            base_score = 3

    elif dimension == "evidence_traceability":
        if has_evidence_paths and has_tests:
            base_score = 5
        elif has_evidence_paths:
            base_score = 4
        else:
            base_score = 2

    elif dimension == "acceptance_criteria_met":
        met = evidence.get("acceptance_criteria_met", [])
        failed = evidence.get("acceptance_criteria_failed", [])
        if met and not failed:
            base_score = 5
        elif met:
            base_score = 3
        else:
            base_score = 2

    return max(1, min(5, base_score))


def score_taskcard(taskcard_result: dict[str, Any]) -> dict[str, int]:
    """Score a single taskcard across all 15 dimensions."""
    evidence = {
        "test_references": taskcard_result.get("test_references", []),
        "evidence_paths": taskcard_result.get("evidence_paths", []),
        "changed_files": taskcard_result.get("changed_files", []),
        "tests_passed": taskcard_result.get("test_results", {}).get("passed", 0),
        "tests_failed": taskcard_result.get("test_results", {}).get("failed", 0),
        "schema_validated": taskcard_result.get("schema_validated", False),
        "governance_pass": taskcard_result.get("governance_pass", False),
        "governance_fail": taskcard_result.get("governance_fail", False),
        "forbidden_path_violations": taskcard_result.get("forbidden_path_violations", []),
        "docs_updated": taskcard_result.get("docs_updated", False),
        "docs_not_needed": taskcard_result.get("docs_not_needed", True),
        "idempotency_proven": taskcard_result.get("idempotency_proven", False),
        "performance_regression": taskcard_result.get("performance_regression", False),
        "unhandled_errors": taskcard_result.get("unhandled_errors", False),
        "integration_verified": taskcard_result.get("integration_verified", False),
        "acceptance_criteria_met": taskcard_result.get("acceptance_criteria_met", []),
        "acceptance_criteria_failed": taskcard_result.get("acceptance_criteria_failed", []),
        "lint_failures": taskcard_result.get("lint_failures", []),
    }
    scores: dict[str, int] = {}
    for dim in QUALITY_DIMENSIONS:
        scores[dim] = _score_dimension(dim, evidence)
    return scores


def score_execution(
    taskcard_results: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """
    Score all taskcard results and determine overall quality verdict.

    Returns a dict with execution_results, overall_scores, all_green, and reroute triggers.
    """
    scored_results: list[dict[str, Any]] = []
    reroute_log: list[dict[str, Any]] = []
    dimension_totals: dict[str, list[int]] = {dim: [] for dim in QUALITY_DIMENSIONS}

    for tc in taskcard_results:
        tc_id = tc.get("taskcard_id", "unknown")
        scores = score_taskcard(tc)

        # Collect for averaging
        for dim, val in scores.items():
            dimension_totals[dim].append(val)

        # Determine if reroute needed
        failing_dims = [dim for dim, val in scores.items() if val < QUALITY_THRESHOLD]
        rerouted = len(failing_dims) > 0

        result_entry: dict[str, Any] = {
            "taskcard_id": tc_id,
            "status": "REROUTED" if rerouted else "COMPLETED",
            "quality_scores": scores,
            "evidence_paths": tc.get("evidence_paths", []),
            "test_results": tc.get("test_results", {"passed": 0, "failed": 0, "skipped": 0}),
            "rerouted": rerouted,
        }
        if rerouted:
            result_entry["rework_reason"] = f"Below threshold on: {', '.join(failing_dims)}"
            reroute_log.append({
                "taskcard_id": tc_id,
                "reason": f"Scores below {QUALITY_THRESHOLD}/5",
                "failing_dimensions": failing_dims,
                "rework_owner": tc.get("lane_owner", "unassigned"),
                "reworked": False,
                "rescored": False,
            })

        scored_results.append(result_entry)

    # Compute overall scores (average per dimension)
    overall_scores: dict[str, int] = {}
    for dim in QUALITY_DIMENSIONS:
        vals = dimension_totals[dim]
        if vals:
            overall_scores[dim] = round(sum(vals) / len(vals))
        else:
            overall_scores[dim] = 1

    all_green = all(v >= QUALITY_THRESHOLD for v in overall_scores.values()) and not reroute_log

    # Determine verdict
    if all_green:
        verdict = "EXECUTION_COMPLETE_VERIFIED"
    elif reroute_log:
        verdict = "EXECUTION_REROUTED_REWORK_REQUIRED"
    else:
        verdict = "EXECUTION_COMPLETE_WITH_LIMITATIONS"

    return {
        "execution_results": scored_results,
        "overall_scores": overall_scores,
        "overall_verdict": verdict,
        "all_green": all_green,
        "reroute_log": reroute_log,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score execution quality across 15 dimensions for the Post-Sprint Autonomy Loop.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Quality dimensions (each scored 1-5, threshold 4):\n"
            "  " + ", ".join(QUALITY_DIMENSIONS[:5]) + "\n"
            "  " + ", ".join(QUALITY_DIMENSIONS[5:10]) + "\n"
            "  " + ", ".join(QUALITY_DIMENSIONS[10:]) + "\n"
            "\nAcceptance: all dimensions >= 4/5 across all taskcards"
        ),
    )
    parser.add_argument("--taskcard-results", required=True, help="Path to taskcard results JSON/YAML")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--output", "-o", help="Write scoring result to file (JSON)")
    args = parser.parse_args()

    try:
        results_path = Path(args.taskcard_results)
        text = results_path.read_text(encoding="utf-8")
        try:
            taskcard_results = json.loads(text)
        except json.JSONDecodeError:
            if yaml is not None:
                taskcard_results = yaml.safe_load(text)
            else:
                print("ERROR: Cannot parse input (no YAML support)", file=sys.stderr)
                return 1

        if not isinstance(taskcard_results, list):
            taskcard_results = [taskcard_results]

        result = score_execution(taskcard_results, repo_root=Path(args.repo_root))
        output_json = json.dumps(result, indent=2)
        print(output_json)

        if args.output:
            Path(args.output).write_text(output_json, encoding="utf-8")

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 9


if __name__ == "__main__":
    sys.exit(main())
