"""
product_velocity_scorer.py — 12-dimension product-velocity scoring for the Supervisor stream.

Scores each sprint across 12 dimensions to determine whether the Supervisor is functioning
as a product-factory traffic controller (preventing false PASS/STOP, enforcing product floors,
routing blockers to correct streams).
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# 12-Dimension Velocity Score
# ---------------------------------------------------------------------------

_DIMENSIONS = (
    "poc_help_score",
    "product_breadth_score",
    "product_throughput_delta",
    "mainstream_blocker_removed",
    "reusable_accelerator_consumed",
    "ai_acceleration_consumed",
    "governed_execution_consumed",
    "false_pass_prevented",
    "false_stop_prevented",
    "human_handoff_reduced",
    "machinery_overhead_score",
    "semantic_drift_risk",
)


def score_stream_velocity(
    stream: str,
    evidence: dict[str, Any],
    matrix: dict[str, Any],
    ledger: dict[str, Any],
    ai_advisory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score a stream sprint across all 12 dimensions.

    Returns dict with all 12 dimension keys.
    """
    ai = ai_advisory or {}

    # poc_help_score: 0-3 based on how much sprint helps current POC
    poc_targets = matrix.get("poc_targets", [])
    families = evidence.get("families_touched", 0)
    _blocker = evidence.get("mainstream_blocker_removed") or evidence.get("blocker_removed")
    poc_help = min(3, families) if families else (1 if _blocker else 0)

    # product_breadth_score: number of format families with source changes
    source_diffs = evidence.get("source_diffs", 0)
    breadth = min(3, source_diffs)

    # product_throughput_delta: test count delta
    delta = evidence.get("test_delta", 0)

    # mainstream_blocker_removed: was a Mainstream blocker resolved?
    blocker_removed = bool(
        evidence.get("mainstream_blocker_removed") or evidence.get("blocker_removed")
    )

    # reusable_accelerator_consumed: did Mainstream consume Acceleration output?
    acc_consumed = bool(evidence.get("acceleration_output_consumed"))

    # ai_acceleration_consumed: was AI output consumed by Mainstream?
    ai_consumed = bool(ai.get("ai_output_consumed") or evidence.get("ai_acceleration_consumed"))

    # governed_execution_consumed: were Skills governed transcripts used?
    governed = bool(
        evidence.get("governed_transcripts", 0) > 0 or evidence.get("governed_execution_consumed")
    )

    # false_pass_prevented: was an erroneous PASS blocked?
    fp_prevented = bool(evidence.get("false_pass_prevented"))

    # false_stop_prevented: was an erroneous STOP blocked?
    fs_prevented = bool(evidence.get("false_stop_prevented"))

    # human_handoff_reduced: did Skills reduce human handoff?
    handoff_reduced = bool(evidence.get("human_handoff_reduced"))

    # machinery_overhead_score: supervisor machinery overhead (0-3)
    declared = evidence.get("declared_items", [])
    overhead = score_machinery_overhead(ledger.get("lanes", []), declared)

    # semantic_drift_risk: drift risk level
    drift = detect_semantic_drift_risk(stream, evidence, ai_advisory)

    return {
        "poc_help_score": poc_help,
        "product_breadth_score": breadth,
        "product_throughput_delta": delta,
        "mainstream_blocker_removed": blocker_removed,
        "reusable_accelerator_consumed": acc_consumed,
        "ai_acceleration_consumed": ai_consumed,
        "governed_execution_consumed": governed,
        "false_pass_prevented": fp_prevented,
        "false_stop_prevented": fs_prevented,
        "human_handoff_reduced": handoff_reduced,
        "machinery_overhead_score": overhead,
        "semantic_drift_risk": drift,
    }


# ---------------------------------------------------------------------------
# Mainstream Package Classification (7 verdicts)
# ---------------------------------------------------------------------------

def classify_mainstream_package(evidence: dict[str, Any]) -> str:
    """Classify a Mainstream sprint evidence package.

    Returns one of:
        CLEAN_PASS
        PARTIAL_EVIDENCE_REPAIR
        PARTIAL_ONE_SOURCE
        PARTIAL_FEW_FAMILIES
        PARTIAL_HELPER_ONLY
        PARTIAL_NO_DOGFOOD
        PARTIAL_NO_GOVERNED_TRANSCRIPTS
    """
    families = evidence.get("families_touched", 0)
    source_diffs = evidence.get("source_diffs", 0)
    governed_transcripts = evidence.get("governed_transcripts", 0)
    raw_logs = evidence.get("raw_logs", 0)
    capability_matrix_deltas = evidence.get("capability_matrix_deltas", 0)
    repair_items = evidence.get("repair_items", 0)
    product_items = evidence.get("product_items", 1)

    # Check for no-clean-PASS machinery rule first
    declared = evidence.get("declared_items", [])
    overhead = score_machinery_overhead([], declared)
    if overhead >= 2:
        fp = evidence.get("false_pass_prevented", False)
        fs = evidence.get("false_stop_prevented", False)
        blocker = evidence.get("mainstream_blocker_removed", False)
        acc = evidence.get("reusable_accelerator_consumed", False)
        if not any([fp, fs, blocker, acc]):
            return "PARTIAL_HELPER_ONLY"

    # CLEAN_PASS requires all 6 conditions
    if families >= 3 and source_diffs >= 3 and governed_transcripts >= 3 \
            and raw_logs >= 3 and capability_matrix_deltas >= 3 \
            and repair_items < product_items:
        return "CLEAN_PASS"

    # PARTIAL verdicts in priority order
    if families < 3:
        return "PARTIAL_FEW_FAMILIES"
    if source_diffs < 2:
        return "PARTIAL_ONE_SOURCE"
    if governed_transcripts < 1:
        return "PARTIAL_NO_GOVERNED_TRANSCRIPTS"
    if capability_matrix_deltas < 1:
        return "PARTIAL_NO_DOGFOOD"
    if repair_items >= product_items:
        return "PARTIAL_EVIDENCE_REPAIR"

    # Catch-all partial
    return "PARTIAL_EVIDENCE_REPAIR"


# ---------------------------------------------------------------------------
# Product Output Floor
# ---------------------------------------------------------------------------

def compute_product_output_floor(evidence: dict[str, Any]) -> bool:
    """Return True if the sprint meets the minimum product output floor.

    Floor requires:
    - product_breadth_score >= 1 OR mainstream_blocker_removed
    - AND machinery_overhead_score < 3
    """
    families = evidence.get("families_touched", 0)
    source_diffs = evidence.get("source_diffs", 0)
    breadth = families > 0 or source_diffs > 0
    blocker = bool(evidence.get("mainstream_blocker_removed") or evidence.get("blocker_removed"))

    declared = evidence.get("declared_items", [])
    overhead = score_machinery_overhead([], declared)

    product_output = breadth or blocker
    not_pure_overhead = overhead < 3
    return product_output and not_pure_overhead


# ---------------------------------------------------------------------------
# Machinery Overhead Score
# ---------------------------------------------------------------------------

def score_machinery_overhead(lanes: list[Any], declared_items: list[Any]) -> int:
    """Score supervisor machinery overhead (0-3).

    0 = no supervisor tooling changes; all work is product/capability
    1 = some supervisor tooling; product work dominates
    2 = supervisor tooling equals or exceeds product work
    3 = pure supervisor machinery; no product output
    """
    if not declared_items:
        return 0

    supervisor_items = [i for i in declared_items if _is_supervisor_item(i)]
    product_items_list = [i for i in declared_items if _is_product_item(i)]

    total = len(declared_items)
    sup_count = len(supervisor_items)

    if sup_count == 0:
        return 0

    ratio = sup_count / total
    if ratio < 0.3:
        return 1
    elif ratio < 0.7:
        return 2
    else:
        return 3


def _is_supervisor_item(item: Any) -> bool:
    """Check if an item is supervisor tooling (not product)."""
    if isinstance(item, dict):
        item_type = item.get("type", "")
        item_id = str(item.get("item_id", ""))
        return (
            item_type == "supervisor_tooling"
            or "supervisor" in item_id.lower()
            or "TC-" in item_id  # taskcard IDs are supervisor machinery
        )
    return False


def _is_product_item(item: Any) -> bool:
    """Check if an item is a product-track item."""
    if isinstance(item, dict):
        item_type = item.get("type", "")
        return item_type in ("product", "capability", "format_api", "test_coverage")
    return False


# ---------------------------------------------------------------------------
# Semantic Drift Risk
# ---------------------------------------------------------------------------

def detect_semantic_drift_risk(
    stream: str,
    evidence: dict[str, Any],
    ai_advisory: dict[str, Any] | None = None,
) -> str:
    """Detect semantic drift risk for a sprint.

    Returns: low | medium | high
    """
    ai = ai_advisory or {}
    drift_signals = 0

    # Q1: Claimed product breadth with only supervisor tooling?
    families = evidence.get("families_touched", 0)
    source_diffs = evidence.get("source_diffs", 0)
    claimed_product = evidence.get("claimed_product_breadth", False)
    if claimed_product and families == 0 and source_diffs == 0:
        drift_signals += 1

    # Q2: Did Mainstream consume Acceleration AI outputs?
    if stream == "mainstream" and not evidence.get("acceleration_output_consumed"):
        drift_signals += 1

    # Q3: Did Skills governed transcripts reduce human handoff?
    if stream == "skills" and not evidence.get("human_handoff_reduced"):
        drift_signals += 1

    # Q4: Product velocity decline?
    if evidence.get("product_throughput_delta", 0) < 0:
        drift_signals += 1

    # Q5: Repair items > product items in Mainstream?
    repair = evidence.get("repair_items", 0)
    product_count = evidence.get("product_items", 1)
    if repair >= product_count and stream == "mainstream":
        drift_signals += 1

    # Q6: Declared governed execution not actually consumed?
    governed_declared = evidence.get("governed_execution_declared", False)
    governed_consumed = evidence.get("governed_execution_consumed", False)
    if governed_declared and not governed_consumed:
        drift_signals += 1

    # Q7: Continuation state changed without evidence?
    if ai.get("continuation_state_unexplained"):
        drift_signals += 1

    # Q8: High machinery overhead with no product output?
    declared = evidence.get("declared_items", [])
    overhead = score_machinery_overhead([], declared)
    floor_met = compute_product_output_floor(evidence)
    if overhead >= 2 and not floor_met:
        drift_signals += 1

    # Q9: Test count decrease?
    if evidence.get("test_delta", 0) < 0:
        drift_signals += 1

    if drift_signals >= 4:
        return "high"
    elif drift_signals >= 2:
        return "medium"
    return "low"
