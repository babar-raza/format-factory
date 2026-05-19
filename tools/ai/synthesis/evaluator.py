"""Synthesis evaluator — quality gate for synthesis outputs before authority transition.

Evaluates citation coverage, contradiction status, schema validity, and output
coherence. Produces a pass/fail evaluation that gates authority lifecycle transition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tools.ai.synthesis.runner import SynthesisResult


@dataclass
class EvaluationCriteria:
    """Criteria for evaluating a synthesis result."""
    require_schema_valid: bool = True
    require_no_errors: bool = True
    require_citations: bool = False
    min_citation_count: int = 1
    require_no_contradictions: bool = True
    require_output_hash: bool = True
    max_error_count: int = 0


@dataclass
class EvaluationResult:
    """Result of evaluating a synthesis output."""
    task_id: str
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "passed": self.passed,
            "checks": self.checks,
            "failures": self.failures,
            "score": self.score,
        }


def evaluate_synthesis(
    result: SynthesisResult,
    criteria: EvaluationCriteria | None = None,
) -> EvaluationResult:
    """Evaluate a synthesis result against quality criteria."""
    if criteria is None:
        criteria = EvaluationCriteria()

    evaluation = EvaluationResult(task_id=result.task_id)
    total_checks = 0
    passed_checks = 0

    # Schema validity
    if criteria.require_schema_valid:
        total_checks += 1
        ok = result.schema_valid
        evaluation.checks["schema_valid"] = ok
        if ok:
            passed_checks += 1
        else:
            evaluation.failures.append("schema_invalid")

    # Error count
    if criteria.require_no_errors:
        total_checks += 1
        ok = len(result.errors) <= criteria.max_error_count
        evaluation.checks["errors_within_limit"] = ok
        if ok:
            passed_checks += 1
        else:
            evaluation.failures.append(f"too_many_errors:{len(result.errors)}")

    # Citations
    if criteria.require_citations:
        total_checks += 1
        ok = (
            result.citation_verified
            and len(result.citations) >= criteria.min_citation_count
        )
        evaluation.checks["citations_sufficient"] = ok
        if ok:
            passed_checks += 1
        else:
            evaluation.failures.append(
                f"citations_insufficient:{len(result.citations)}"
            )

    # Contradictions
    if criteria.require_no_contradictions:
        total_checks += 1
        ok = result.contradiction_check_status in (
            "no_contradictions",
            "not_checked",
        )
        evaluation.checks["no_contradictions"] = ok
        if ok:
            passed_checks += 1
        else:
            evaluation.failures.append(
                f"contradiction_status:{result.contradiction_check_status}"
            )

    # Output hash
    if criteria.require_output_hash:
        total_checks += 1
        ok = bool(result.output_hash)
        evaluation.checks["output_hash_present"] = ok
        if ok:
            passed_checks += 1
        else:
            evaluation.failures.append("missing_output_hash")

    evaluation.score = passed_checks / total_checks if total_checks > 0 else 0.0
    evaluation.passed = len(evaluation.failures) == 0

    return evaluation
