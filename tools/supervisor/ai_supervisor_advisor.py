"""
ai_supervisor_advisor.py — Non-authoritative AI advisory wrapper for Supervisor stream.

All outputs are labeled as non-authoritative (ai_draft). Deterministic validation always
takes precedence. No live AI gateway is used — advisory_mode: deterministic_advisory.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any


def create_advisory_output(
    stream: str,
    sprint_id: str,
    evidence_paths: list[str],
    advisory_type: str,
    content: dict[str, Any],
    advisory_mode: str = "deterministic_advisory",
) -> dict[str, Any]:
    """Wrap content with mandatory non-authority metadata.

    advisory_mode: deterministic_advisory | fixture_ai | live_ai
    Do not claim live_ai unless a live AI gateway was actually used.

    All advisory outputs are non-authoritative and require deterministic validation.
    """
    output_hash = "sha256:" + hashlib.sha256(
        json.dumps(content, sort_keys=True).encode()
    ).hexdigest()[:16]

    return {
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "requires_deterministic_validation": True,
        "advisory_mode": advisory_mode,
        "stream": stream,
        "sprint_id": sprint_id,
        "advisory_type": advisory_type,
        "generated_at": datetime.now().isoformat(),
        "input_evidence_paths": evidence_paths,
        "output_hash": output_hash,
        "validation_status": "pending",
        "content": content,
    }


def review_semantic_drift(
    stream: str,
    evidence: dict[str, Any],
    prior_sprints: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Answer 9 drift questions. Returns advisory output (ai_draft).

    All output is non_authoritative: true, advisory_mode: deterministic_advisory.
    """
    prior = prior_sprints or []

    answers: dict[str, Any] = {}

    # Q1: Claimed product breadth with only supervisor tooling?
    families = evidence.get("families_touched", 0)
    source_diffs = evidence.get("source_diffs", 0)
    claimed = evidence.get("claimed_product_breadth", False)
    answers["q1_product_claimed_without_source"] = (
        claimed and families == 0 and source_diffs == 0
    )

    # Q2: Did Mainstream consume Acceleration AI outputs?
    answers["q2_mainstream_consumed_acceleration"] = bool(
        evidence.get("acceleration_output_consumed")
    )

    # Q3: Did Skills governed transcripts reduce human handoff?
    answers["q3_skills_reduced_handoff"] = bool(
        evidence.get("human_handoff_reduced")
    )

    # Q4: Product velocity decline?
    answers["q4_velocity_decline"] = evidence.get("product_throughput_delta", 0) < 0

    # Q5: Repair items > product items?
    repair = evidence.get("repair_items", 0)
    product_count = evidence.get("product_items", 1)
    answers["q5_repair_dominates"] = repair >= product_count

    # Q6: Governed execution declared but not consumed?
    answers["q6_governed_not_consumed"] = (
        evidence.get("governed_execution_declared", False)
        and not evidence.get("governed_execution_consumed", False)
    )

    # Q7: Unexplained continuation state change?
    answers["q7_continuation_unexplained"] = False  # deterministic check

    # Q8: High machinery overhead, no product output?
    try:
        from product_velocity_scorer import score_machinery_overhead, compute_product_output_floor
    except ImportError:
        from tools.supervisor.product_velocity_scorer import score_machinery_overhead, compute_product_output_floor
    declared = evidence.get("declared_items", [])
    overhead = score_machinery_overhead([], declared)
    floor_met = compute_product_output_floor(evidence)
    answers["q8_high_overhead_no_product"] = overhead >= 2 and not floor_met

    # Q9: Test count decrease?
    answers["q9_test_count_decrease"] = evidence.get("test_delta", 0) < 0

    # Drift risk
    drift_signals = sum(1 for v in answers.values() if v is True)
    if drift_signals >= 4:
        drift_flag = True
        drift_risk = "high"
    elif drift_signals >= 2:
        drift_flag = True
        drift_risk = "medium"
    else:
        drift_flag = False
        drift_risk = "low"

    content = {
        "drift_questions": answers,
        "drift_signals_count": drift_signals,
        "drift_risk": drift_risk,
        "drift_flag": drift_flag,
    }

    return create_advisory_output(
        stream=stream,
        sprint_id=evidence.get("sprint_id", "unknown"),
        evidence_paths=evidence.get("evidence_paths", []),
        advisory_type="semantic_drift_review",
        content=content,
    )


def check_acceleration_ai_consumption(
    evidence: dict[str, Any],
    ai_outputs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Check AI output status for Acceleration stream.

    Returns advisory output (ai_draft) with consumption check results.
    """
    outputs = ai_outputs or []
    content: dict[str, Any] = {
        "ai_output_count": len(outputs),
        "live_ai_used": any(o.get("advisory_mode") == "live_ai" for o in outputs),
        "all_marked_ai_draft": all(o.get("authority_state") == "ai_draft" for o in outputs),
        "consumed_by_mainstream": bool(evidence.get("acceleration_output_consumed")),
        "authority_violations": [
            o for o in outputs if o.get("authority_state") != "ai_draft"
        ],
    }

    return create_advisory_output(
        stream="acceleration",
        sprint_id=evidence.get("sprint_id", "unknown"),
        evidence_paths=[],
        advisory_type="acceleration_ai_consumption_check",
        content=content,
    )


def check_skills_consumption(
    evidence: dict[str, Any],
    mainstream_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check Skills governed contract consumption.

    Returns advisory output (ai_draft) with consumption check results.
    """
    ms = mainstream_evidence or {}
    content: dict[str, Any] = {
        "governed_transcripts_in_skills": evidence.get("governed_transcripts", 0),
        "receiver_fixtures_validated": bool(evidence.get("receiver_fixtures_validated")),
        "consumed_by_mainstream": bool(
            ms.get("governed_execution_consumed") or evidence.get("consumed_by_mainstream")
        ),
        "human_handoff_reduced": bool(evidence.get("human_handoff_reduced")),
        "skills_contract_met": bool(
            evidence.get("governed_transcripts", 0) >= 1
            and evidence.get("human_handoff_reduced")
        ),
    }

    return create_advisory_output(
        stream="skills",
        sprint_id=evidence.get("sprint_id", "unknown"),
        evidence_paths=[],
        advisory_type="skills_consumption_check",
        content=content,
    )


def handle_ai_deterministic_disagreement(
    ai_result: dict[str, Any],
    deterministic_result: dict[str, Any],
) -> str:
    """Resolve disagreement between AI advisory and deterministic validation.

    Rules (in priority order):
    1. det valid=False + any AI → return "NO_" + deterministic reason
    2. det valid=True + ai drift_flag=True → return "YES_WITH_LIMITATIONS"
    3. ai false_stop=True → return "ROUTE_BLOCKER"
    4. ai overhead_flag=True → return "YES_WITH_LIMITATIONS"
    5. both agree → return "YES"
    """
    det_valid = deterministic_result.get("valid", True)
    det_reason = deterministic_result.get("reason", "deterministic_failure")

    # Rule 1: Deterministic failure always wins
    if not det_valid:
        safe_reason = str(det_reason).upper().replace(" ", "_").replace("-", "_")
        return f"NO_{safe_reason}"

    # Rule 2: Deterministic pass + AI drift flag
    if ai_result.get("drift_flag"):
        return "YES_WITH_LIMITATIONS"

    # Rule 3: AI says false stop risk
    if ai_result.get("false_stop"):
        return "ROUTE_BLOCKER"

    # Rule 4: AI says overhead flag
    if ai_result.get("overhead_flag"):
        return "YES_WITH_LIMITATIONS"

    # Rule 5: Both agree
    return "YES"
