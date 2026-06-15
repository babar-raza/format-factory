"""
Summary Classifier for the Post-Sprint Autonomy Loop.

Deterministic classifier for Stage 3 (Prompt 3) outputs.
Reads a structured output file (YAML or JSON) and classifies it for the loop controller.

Output conforms to: .supervisor/schemas/summary-parser-contract.schema.json

Exit codes:
  0 — classified successfully
  1 — malformed input
  9 — unexpected error

Usage:
  python tools/supervisor/summary_classifier.py <stage3_output_path>
  python tools/supervisor/summary_classifier.py --help
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

# Quality score threshold — any dimension below this triggers reroute
QUALITY_THRESHOLD = 4

# All 15 required quality dimensions
QUALITY_DIMENSIONS = [
    "correctness", "test_coverage", "evidence_completeness", "code_quality",
    "schema_compliance", "governance_compliance", "path_discipline", "documentation",
    "idempotency", "regression_safety", "performance", "error_handling",
    "integration_consistency", "evidence_traceability", "acceptance_criteria_met",
]

# Valid classifications (enum from summary-parser-contract.schema.json)
CLASSIFICATIONS = [
    "STRUCTURED_ALL_GREEN", "STRUCTURED_NOT_GREEN", "PROSE_ONLY", "MISSING",
    "CONTRADICTORY", "EVIDENCE_MISSING", "SCORES_MISSING",
    "TASKCARDS_INCOMPLETE", "BLOCKED_EXTERNAL",
]

# Next stage recommendations
NEXT_STAGES = [
    "ACCEPT", "REROUTE_TO_PROMPT_2_THEN_3", "RESTART_FROM_PROMPT_1",
    "RUN_EVIDENCE_PACKAGING", "RUN_SCORING_LANE", "REROUTE_REWORK",
    "ADVERSARIAL_REVIEW", "BLOCKER_PACKAGE_AND_STOP",
]


def _try_parse(text: str) -> dict[str, Any] | None:
    """Try to parse text as JSON then YAML. Returns dict or None."""
    # Try JSON first
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    # Try YAML
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return None


def _is_prose_only(text: str) -> bool:
    """Detect if text is prose without structured data markers."""
    stripped = text.strip()
    if not stripped:
        return False  # empty is MISSING, not prose
    # Check for JSON/YAML structural markers
    if stripped.startswith("{") or stripped.startswith("["):
        return False
    # Check for YAML document markers or key-value patterns
    lines = stripped.split("\n")
    kv_count = sum(1 for line in lines if ":" in line and not line.strip().startswith("#"))
    # If less than 3 key-value-like lines out of total, likely prose
    if len(lines) > 3 and kv_count < 3:
        return True
    # If it parses as structured data, it's not prose
    parsed = _try_parse(stripped)
    if parsed is not None:
        return False
    return True


def _check_quality_scores(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Check if all quality scores meet threshold. Returns (all_green, failing_dimensions)."""
    failing: list[str] = []
    results = data.get("execution_results", [])
    if not results:
        # Check overall_scores as fallback
        scores = data.get("overall_scores", {})
        if not scores:
            return False, ["no_scores_found"]
        for dim in QUALITY_DIMENSIONS:
            val = scores.get(dim)
            if val is not None and val < QUALITY_THRESHOLD:
                failing.append(dim)
        return len(failing) == 0, failing

    for result in results:
        scores = result.get("quality_scores", {})
        tc_id = result.get("taskcard_id", "unknown")
        for dim in QUALITY_DIMENSIONS:
            val = scores.get(dim)
            if val is not None and val < QUALITY_THRESHOLD:
                failing.append(f"{tc_id}:{dim}={val}")
    return len(failing) == 0, failing


def _is_quality_scores_format(data: dict[str, Any]) -> bool:
    """Detect if input is quality-scores.json from quality_scorer.py.

    Quality scorer output has execution_results + overall_scores + overall_verdict
    but no evidence_bundle_path or evidence_manifest. This is a valid structured
    input that should bypass the evidence check.
    """
    return (
        bool(data.get("execution_results"))
        and bool(data.get("overall_scores"))
        and bool(data.get("overall_verdict"))
    )


def _check_evidence(data: dict[str, Any]) -> bool:
    """Check if evidence bundle path is present.

    Returns True for quality-scores.json format (which never contains
    evidence_bundle_path but is still a valid structured input).
    """
    if _is_quality_scores_format(data):
        return True
    bundle_path = data.get("evidence_bundle_path")
    if bundle_path:
        return True
    manifest = data.get("evidence_manifest", [])
    return len(manifest) > 0


def _check_self_review(data: dict[str, Any]) -> bool:
    """Check if self_review section exists (not prose-only)."""
    review = data.get("self_review")
    return review is not None and isinstance(review, dict)


def _check_taskcards_complete(data: dict[str, Any]) -> bool:
    """Check if all taskcard results have been evaluated."""
    results = data.get("execution_results", [])
    if not results:
        return False
    for r in results:
        if not r.get("quality_scores"):
            return False
        status = r.get("status", "")
        if status == "SKIPPED":
            continue
        if not r.get("quality_scores"):
            return False
    return True


def _check_contradictions(data: dict[str, Any]) -> bool:
    """Check if all-green claim contradicts reroute log."""
    all_green = data.get("all_green", False)
    reroute_log = data.get("reroute_log", [])
    if all_green and reroute_log:
        # all_green but reroute items exist — contradiction
        return True
    verdict = data.get("overall_verdict", "")
    if all_green and verdict not in ("EXECUTION_COMPLETE_VERIFIED", ""):
        # all_green but verdict is not complete verified — potential contradiction
        if verdict in ("EXECUTION_REROUTED_REWORK_REQUIRED", "BLOCKED_BY_FAILED_GATE"):
            return True
    return False


def classify_summary(path: Path) -> dict[str, Any]:
    """
    Classify a Stage 3 output file.

    Returns a dict conforming to summary-parser-contract.schema.json.
    """
    # Check if file exists
    if not path.exists():
        return {
            "classification": "MISSING",
            "confidence": 1.0,
            "evidence": {
                "has_structured_data": False, "has_all_green": False,
                "has_quality_scores": False, "has_evidence_manifest": False,
                "has_self_review": False, "has_taskcard_results": False,
                "reroute_log_empty": True, "all_scores_above_threshold": False,
                "contradictions_detected": False,
            },
            "next_stage_recommendation": "RESTART_FROM_PROMPT_1",
            "failing_items": [],
            "reason": f"Stage 3 output file not found: {path}",
        }

    text = path.read_text(encoding="utf-8", errors="replace").strip()

    # Empty file
    if not text:
        return {
            "classification": "MISSING",
            "confidence": 1.0,
            "evidence": {
                "has_structured_data": False, "has_all_green": False,
                "has_quality_scores": False, "has_evidence_manifest": False,
                "has_self_review": False, "has_taskcard_results": False,
                "reroute_log_empty": True, "all_scores_above_threshold": False,
                "contradictions_detected": False,
            },
            "next_stage_recommendation": "RESTART_FROM_PROMPT_1",
            "failing_items": [],
            "reason": "Stage 3 output file is empty",
        }

    # Prose-only detection
    if _is_prose_only(text):
        return {
            "classification": "PROSE_ONLY",
            "confidence": 0.9,
            "evidence": {
                "has_structured_data": False, "has_all_green": False,
                "has_quality_scores": False, "has_evidence_manifest": False,
                "has_self_review": False, "has_taskcard_results": False,
                "reroute_log_empty": True, "all_scores_above_threshold": False,
                "contradictions_detected": False,
            },
            "next_stage_recommendation": "REROUTE_TO_PROMPT_2_THEN_3",
            "failing_items": [],
            "reason": "Stage 3 output is prose without structured data",
        }

    # Try to parse as structured data
    data = _try_parse(text)
    if data is None:
        return {
            "classification": "PROSE_ONLY",
            "confidence": 0.7,
            "evidence": {
                "has_structured_data": False, "has_all_green": False,
                "has_quality_scores": False, "has_evidence_manifest": False,
                "has_self_review": False, "has_taskcard_results": False,
                "reroute_log_empty": True, "all_scores_above_threshold": False,
                "contradictions_detected": False,
            },
            "next_stage_recommendation": "REROUTE_TO_PROMPT_2_THEN_3",
            "failing_items": [],
            "reason": "Stage 3 output could not be parsed as JSON or YAML",
        }

    # Structured data found — classify further
    has_results = bool(data.get("execution_results"))
    has_scores = has_results and all(
        r.get("quality_scores") for r in data.get("execution_results", [])
    )
    has_evidence = _check_evidence(data)
    has_self_review = _check_self_review(data)
    has_all_green_field = data.get("all_green", False)
    reroute_log = data.get("reroute_log", [])
    contradictions = _check_contradictions(data)

    evidence_info = {
        "has_structured_data": True,
        "has_all_green": has_all_green_field,
        "has_quality_scores": has_scores,
        "has_evidence_manifest": has_evidence,
        "has_self_review": has_self_review,
        "has_taskcard_results": has_results,
        "reroute_log_empty": len(reroute_log) == 0,
        "all_scores_above_threshold": False,
        "contradictions_detected": contradictions,
    }

    # Check for blocked external
    verdict = data.get("overall_verdict", "")
    if verdict == "BLOCKED_EXTERNAL":
        return {
            "classification": "BLOCKED_EXTERNAL",
            "confidence": 1.0,
            "evidence": evidence_info,
            "next_stage_recommendation": "BLOCKER_PACKAGE_AND_STOP",
            "failing_items": [],
            "reason": "External blocker detected in Stage 3 verdict",
        }

    # Check contradictions
    if contradictions:
        return {
            "classification": "CONTRADICTORY",
            "confidence": 0.95,
            "evidence": evidence_info,
            "next_stage_recommendation": "RESTART_FROM_PROMPT_1",
            "failing_items": [],
            "reason": "All-green claim contradicts reroute log or verdict",
        }

    # Check evidence
    if not has_evidence:
        return {
            "classification": "EVIDENCE_MISSING",
            "confidence": 0.95,
            "evidence": evidence_info,
            "next_stage_recommendation": "RUN_EVIDENCE_PACKAGING",
            "failing_items": [],
            "reason": "No evidence bundle path or manifest found",
        }

    # Check scores present
    if not has_scores:
        if not has_results:
            return {
                "classification": "TASKCARDS_INCOMPLETE",
                "confidence": 0.9,
                "evidence": evidence_info,
                "next_stage_recommendation": "REROUTE_TO_PROMPT_2_THEN_3",
                "failing_items": [],
                "reason": "No taskcard execution results found",
            }
        return {
            "classification": "SCORES_MISSING",
            "confidence": 0.9,
            "evidence": evidence_info,
            "next_stage_recommendation": "RUN_SCORING_LANE",
            "failing_items": [],
            "reason": "Quality scores missing from taskcard results",
        }

    # Check taskcards complete
    if not _check_taskcards_complete(data):
        return {
            "classification": "TASKCARDS_INCOMPLETE",
            "confidence": 0.9,
            "evidence": evidence_info,
            "next_stage_recommendation": "REROUTE_TO_PROMPT_2_THEN_3",
            "failing_items": [],
            "reason": "Not all taskcards have been evaluated",
        }

    # Check quality scores
    all_green, failing = _check_quality_scores(data)
    evidence_info["all_scores_above_threshold"] = all_green

    if all_green and has_all_green_field:
        return {
            "classification": "STRUCTURED_ALL_GREEN",
            "confidence": 1.0,
            "evidence": evidence_info,
            "next_stage_recommendation": "ADVERSARIAL_REVIEW",
            "failing_items": [],
            "reason": "All quality scores meet threshold, all_green confirmed",
        }

    # Not all green
    return {
        "classification": "STRUCTURED_NOT_GREEN",
        "confidence": 0.95,
        "evidence": evidence_info,
        "next_stage_recommendation": "REROUTE_REWORK" if failing else "REROUTE_TO_PROMPT_2_THEN_3",
        "failing_items": failing,
        "reason": f"Quality scores below threshold: {', '.join(failing)}" if failing else "all_green field is false",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify Stage 3 (Prompt 3) output for the Post-Sprint Autonomy Loop.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Classifications:\n"
            "  STRUCTURED_ALL_GREEN    — All scores >= 4, all green\n"
            "  STRUCTURED_NOT_GREEN    — Structured but open issues\n"
            "  PROSE_ONLY              — No structured data\n"
            "  MISSING                 — File not found or empty\n"
            "  CONTRADICTORY           — All-green contradicts reroute log\n"
            "  EVIDENCE_MISSING        — No evidence bundle\n"
            "  SCORES_MISSING          — Quality scores absent\n"
            "  TASKCARDS_INCOMPLETE    — Not all taskcards evaluated\n"
            "  BLOCKED_EXTERNAL        — External blocker\n"
            "\nExit codes: 0=classified, 1=malformed, 9=error"
        ),
    )
    parser.add_argument("path", help="Path to Stage 3 output file (JSON or YAML)")
    parser.add_argument("--output", "-o", help="Write classification result to file (JSON)")
    args = parser.parse_args()

    try:
        result = classify_summary(Path(args.path))
        output_json = json.dumps(result, indent=2)
        print(output_json)

        if args.output:
            Path(args.output).write_text(output_json, encoding="utf-8")

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 9


if __name__ == "__main__":
    sys.exit(main())
