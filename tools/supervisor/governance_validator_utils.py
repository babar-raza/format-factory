"""governance_validator_utils.py — Shared constants and helpers for governance validators.

Extracted from governance_validators.py (TC-MRH-002) to restore LOC headroom.
All symbols re-exported from governance_validators.py for backward compatibility.

External code should import from governance_validators (not directly from here),
unless specifically adding a new validator that needs these without importing the
full governance_validators module (which would cause circular imports).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_EXECUTION_METHODS = frozenset({
    "MANUAL_UNGOVERNED",
    "MANUAL_GOVERNED_BY_SKILL",
    "LOCAL_GOVERNED_DIRECT_EXECUTION",
    "AGENT_GOVERNED_DIRECT_EXECUTION",
    "SKILL_GUIDED_AGENT_EXECUTION",
    "QUEUE_DECLARED_EXECUTION",
    "QUEUE_DISPATCHED_EXECUTION",
    "GENERATED_PATCH_EXECUTION",
    "REPLAYED_PATCH_EXECUTION",
    "BACKFILLED_LEGACY_EXECUTION",
    "UNKNOWN_EXECUTION_METHOD",
})

FORBIDDEN_METHODS_FOR_CLOSING = frozenset({
    "MANUAL_UNGOVERNED",
    "UNKNOWN_EXECUTION_METHOD",
    "QUEUE_DECLARED_EXECUTION",
})

DEPRECATED_METHODS = frozenset({
    "QUEUE_DECLARED_EXECUTION",
    "UNKNOWN_EXECUTION_METHOD",
})

VALID_CLAIM_CLASSIFICATIONS = frozenset({
    "WORKS_BUT_NOT_REPEATABLE",
    "GOVERNED_BUT_NOT_REPLAYED",
    "REPLAYABLE_NOT_YET_REPLAYED",
    "REPLAYED_AND_PROVEN",
    "LEGACY_BACKFILLED",
    "INVALID_CLAIM",
})

REPLAYABLE_CLAIMS = frozenset({
    "REPLAYABLE_NOT_YET_REPLAYED",
    "REPLAYED_AND_PROVEN",
})

PRODUCT_SOURCE_ITEM_TYPES = frozenset({
    "PRODUCT_SOURCE", "TEST", "REQUIREMENT", "READINESS", "RELEASE_GATE",
})

GOVERNANCE_ITEM_TYPES = frozenset({
    "GOVERNANCE_DOC", "GOVERNANCE_SCHEMA", "GOVERNANCE_POLICY",
    "GOVERNANCE_TASKCARD", "LEGACY_BACKFILL_METADATA",
})

GRACE_EXCEPTION_CLASSES = frozenset({
    "pre_taxonomy_backfill", "investigation_only", "legacy_backfill",
    "legacy_pre_taxonomy",
})

# 15-state machine — allowed transitions
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "DISCOVERED": frozenset({
        "EVIDENCE_LOCATED", "BLOCKED_INSUFFICIENT_EVIDENCE",
    }),
    "EVIDENCE_LOCATED": frozenset({
        "EXECUTION_CLASSIFIED", "DISCOVERED",
    }),
    "EXECUTION_CLASSIFIED": frozenset({
        "CONTRACT_REQUIRED", "BACKFILLED_LEGACY_ACCEPTED",
        "REJECTED_UNGOVERNED", "IDEMPOTENCY_KEY_ASSIGNED",
    }),
    "CONTRACT_REQUIRED": frozenset({"CONTRACTED"}),
    "CONTRACTED": frozenset({"IDEMPOTENCY_KEY_ASSIGNED"}),
    "IDEMPOTENCY_KEY_ASSIGNED": frozenset({"MUTATION_BOUNDED"}),
    "MUTATION_BOUNDED": frozenset({"MUTATION_EXECUTED"}),
    "MUTATION_EXECUTED": frozenset({
        "DIFF_CAPTURED", "BLOCKED_INSUFFICIENT_EVIDENCE",
    }),
    "DIFF_CAPTURED": frozenset({"VALIDATED"}),
    "VALIDATED": frozenset({
        "REPLAY_RECIPE_RECORDED", "GOVERNANCE_ACCEPTED",
    }),
    "REPLAY_RECIPE_RECORDED": frozenset({
        "GOVERNANCE_ACCEPTED", "REPLAY_TESTED",
    }),
    "REPLAY_TESTED": frozenset({"GOVERNANCE_ACCEPTED"}),
    "GOVERNANCE_ACCEPTED": frozenset(),
    "BACKFILLED_LEGACY_ACCEPTED": frozenset(),
    "REJECTED_UNGOVERNED": frozenset({"EXECUTION_CLASSIFIED"}),
    "BLOCKED_INSUFFICIENT_EVIDENCE": frozenset({
        "EXECUTION_CLASSIFIED", "DISCOVERED",
    }),
}

CLOSE_ELIGIBLE_STATES = frozenset({
    "VALIDATED", "REPLAY_RECIPE_RECORDED", "REPLAY_TESTED",
    "GOVERNANCE_ACCEPTED", "BACKFILLED_LEGACY_ACCEPTED",
})

# Forbidden jumps for PRODUCT_SOURCE items only.
# Governance docs (GOVERNANCE_DOC, GOVERNANCE_SCHEMA, etc.) legitimately go
# DISCOVERED → GOVERNANCE_ACCEPTED as a short-circuit path for documentation work.
FORBIDDEN_JUMPS_PRODUCT_ONLY = [
    ("DISCOVERED", "GOVERNANCE_ACCEPTED"),
    ("DISCOVERED", "BACKFILLED_LEGACY_ACCEPTED"),
    ("DISCOVERED", "VALIDATED"),
    ("EXECUTION_CLASSIFIED", "GOVERNANCE_ACCEPTED"),
]

FORBIDDEN_JUMPS = FORBIDDEN_JUMPS_PRODUCT_ONLY  # alias kept for compatibility


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_product_source_item(item: dict) -> bool:
    return item.get("item_type", "") in PRODUCT_SOURCE_ITEM_TYPES


def _has_grace_exemption(item: dict) -> bool:
    return (
        item.get("exception_classification", "") in GRACE_EXCEPTION_CLASSES
        or item.get("legacy_backfill_status") in {"BACKFILLED", "PENDING_BACKFILL"}
        or item.get("backfill_pending") is True
    )


def _is_test_item(item: dict) -> bool:
    """TEST items add tests, not product source mutations.
    They should WARN (not FAIL) when governance metadata is absent."""
    return item.get("item_type") == "TEST"


def _make_result(validator: str, result: str, items: list, summary: str,
                 blocks_sprint: bool = False) -> dict:
    return {
        "validator": validator,
        "result": result,
        "items": items,
        "summary": summary,
        "blocks_sprint": blocks_sprint,
    }
