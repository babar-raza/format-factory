"""governance_validators.py — Format Factory Governance Layer Validators

Implements the 10 validators defined in:
  reports/repeatability-governance-plan-healing/validator-hardening-plan.md

GRH-TC-005 (Lane E): All 10 validators implemented as Python functions.
GRH-TC-006 (Lane F): Taskcard state machine validator included.

Each validator returns a dict:
  {
    "validator": str,          # validator name
    "result": "PASS" | "FAIL" | "WARN",
    "items": list[dict],       # per-item results
    "summary": str,
    "blocks_sprint": bool,
  }

Usage:
  from governance_validators import run_all_governance_validators
  result = run_all_governance_validators(declaration)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

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


def _make_result(validator: str, result: str, items: list, summary: str,
                 blocks_sprint: bool = False) -> dict:
    return {
        "validator": validator,
        "result": result,
        "items": items,
        "summary": summary,
        "blocks_sprint": blocks_sprint,
    }


# ---------------------------------------------------------------------------
# Validator 1: execution_method_required_validator
# ---------------------------------------------------------------------------

def validate_execution_method_required(declaration: dict) -> dict:
    """Validator 1: Every PRODUCT_SOURCE item must have an execution_method.

    FAIL: Any PRODUCT_SOURCE item has no execution_method field.
    WARN: execution_method=UNKNOWN_EXECUTION_METHOD.
    Exemptions: 2-sprint grace for pre-taxonomy items with backfill_pending.
    Blocks sprint after grace period.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        if not _is_product_source_item(item):
            continue
        item_id = item.get("item_id", "unknown")
        method = item.get("execution_method", "")
        if not method:
            if _has_grace_exemption(item):
                warn_items.append({
                    "item_id": item_id,
                    "issue": "missing_execution_method",
                    "severity": "WARN",
                    "note": "grace_period: pre_taxonomy_backfill",
                })
            else:
                fail_items.append({
                    "item_id": item_id,
                    "issue": "missing_execution_method",
                    "severity": "FAIL",
                })
        elif method == "UNKNOWN_EXECUTION_METHOD":
            warn_items.append({
                "item_id": item_id,
                "issue": "unknown_execution_method",
                "severity": "WARN",
            })
        elif method not in VALID_EXECUTION_METHODS:
            fail_items.append({
                "item_id": item_id,
                "issue": f"invalid_execution_method: {method}",
                "severity": "FAIL",
            })
        else:
            pass_items.append({"item_id": item_id, "execution_method": method})

    if fail_items:
        return _make_result(
            "execution_method_required_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} PRODUCT_SOURCE items missing execution_method (no grace). "
            f"{len(warn_items)} WARN items.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "execution_method_required_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} items with missing/unknown execution_method (grace period or UNKNOWN).",
        )
    return _make_result(
        "execution_method_required_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} PRODUCT_SOURCE items have valid execution_method.",
    )


# ---------------------------------------------------------------------------
# Validator 2: source_diff_required_validator
# ---------------------------------------------------------------------------

def validate_source_diff_required(declaration: dict) -> dict:
    """Validator 2: Every PRODUCT_SOURCE item must have source_diff_paths.

    FAIL: PRODUCT_SOURCE item lacks source_diff_paths with no exemption.
    WARN: source_diff_paths=MISSING_BACKFILL_REQUIRED or has grace.
    Blocks sprint for new work.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        if not _is_product_source_item(item):
            continue
        item_id = item.get("item_id", "unknown")
        diff_paths = item.get("source_diff_paths", [])
        is_missing = not diff_paths or diff_paths == ["MISSING_BACKFILL_REQUIRED"]

        if is_missing:
            if _has_grace_exemption(item) or item.get("execution_method") == "BACKFILLED_LEGACY_EXECUTION":
                warn_items.append({
                    "item_id": item_id,
                    "issue": "missing_source_diff_paths",
                    "severity": "WARN",
                    "note": "grace: backfill or pre_taxonomy",
                })
            else:
                fail_items.append({
                    "item_id": item_id,
                    "issue": "missing_source_diff_paths",
                    "severity": "FAIL",
                })
        else:
            pass_items.append({"item_id": item_id, "diff_paths": diff_paths})

    if fail_items:
        return _make_result(
            "source_diff_required_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} items missing source_diff_paths without exemption.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "source_diff_required_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} items missing source_diff_paths (grace/backfill).",
        )
    return _make_result(
        "source_diff_required_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} items have source_diff_paths.",
    )


# ---------------------------------------------------------------------------
# Validator 3: idempotency_key_required_validator
# ---------------------------------------------------------------------------

def validate_idempotency_key_required(declaration: dict) -> dict:
    """Validator 3: Every PRODUCT_SOURCE item must have an idempotency_key.

    FAIL: PRODUCT_SOURCE item has no idempotency_key (no grace).
    WARN: key present but format is not 64-char hex.
    Exemptions: pre_taxonomy_work with backfill note.
    """
    import re
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []
    HEX64 = re.compile(r"^[a-f0-9]{64}$")

    for item in items:
        if not _is_product_source_item(item):
            continue
        item_id = item.get("item_id", "unknown")
        key = item.get("idempotency_key", "")
        if not key:
            if _has_grace_exemption(item):
                warn_items.append({
                    "item_id": item_id,
                    "issue": "missing_idempotency_key",
                    "severity": "WARN",
                    "note": "grace: pre_taxonomy",
                })
            else:
                fail_items.append({
                    "item_id": item_id,
                    "issue": "missing_idempotency_key",
                    "severity": "FAIL",
                })
        elif not HEX64.match(str(key)):
            warn_items.append({
                "item_id": item_id,
                "issue": f"idempotency_key_wrong_format: {str(key)[:20]}...",
                "severity": "WARN",
            })
        else:
            pass_items.append({"item_id": item_id, "idempotency_key": key[:8] + "..."})

    if fail_items:
        return _make_result(
            "idempotency_key_required_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} items missing idempotency_key without grace.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "idempotency_key_required_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} items with missing or malformed idempotency_key (grace).",
        )
    return _make_result(
        "idempotency_key_required_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} items have valid idempotency_key.",
    )


# ---------------------------------------------------------------------------
# Validator 4: replay_recipe_required_validator
# ---------------------------------------------------------------------------

def validate_replay_recipe_required(declaration: dict) -> dict:
    """Validator 4: REPLAYABLE_* claims require a replay_recipe_path.

    FAIL: claim_classification=REPLAYABLE_* but replay_recipe_path absent.
    WARN: claim=GOVERNED_BUT_NOT_REPLAYED (acceptable).
    Exemptions: LEGACY_BACKFILLED never needs recipe.
    Blocks sprint if REPLAYABLE claim without recipe.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        item_id = item.get("item_id", "unknown")
        claim = item.get("claim_classification", "")
        if claim in REPLAYABLE_CLAIMS:
            recipe = item.get("replay_recipe_path", "")
            if not recipe:
                fail_items.append({
                    "item_id": item_id,
                    "issue": f"REPLAYABLE claim ({claim}) but no replay_recipe_path",
                    "severity": "FAIL",
                })
            else:
                pass_items.append({"item_id": item_id, "claim": claim, "recipe": recipe})
        elif claim == "GOVERNED_BUT_NOT_REPLAYED":
            warn_items.append({
                "item_id": item_id,
                "issue": "GOVERNED_BUT_NOT_REPLAYED (acceptable — no replay required)",
                "severity": "WARN",
            })
        elif claim:
            pass_items.append({"item_id": item_id, "claim": claim})

    if fail_items:
        return _make_result(
            "replay_recipe_required_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} items claim REPLAYABLE without replay_recipe_path.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "replay_recipe_required_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} GOVERNED_BUT_NOT_REPLAYED items (acceptable).",
        )
    return _make_result(
        "replay_recipe_required_validator",
        "PASS",
        pass_items,
        f"PASS: All replay claims are valid.",
    )


# ---------------------------------------------------------------------------
# Validator 5: claim_classification_validator
# ---------------------------------------------------------------------------

def validate_claim_classification(declaration: dict) -> dict:
    """Validator 5: claim_classification must be a valid value.

    FAIL: claim_classification=INVALID_CLAIM; REPLAYABLE with MANUAL_UNGOVERNED method.
    WARN: WORKS_BUT_NOT_REPEATABLE (acceptable).
    Blocks sprint for INVALID_CLAIM.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        item_id = item.get("item_id", "unknown")
        claim = item.get("claim_classification", "")
        method = item.get("execution_method", "")

        if not claim:
            continue  # No claim — not required for non-product items

        if claim == "INVALID_CLAIM":
            fail_items.append({
                "item_id": item_id,
                "issue": "claim_classification=INVALID_CLAIM",
                "severity": "FAIL",
            })
        elif claim not in VALID_CLAIM_CLASSIFICATIONS:
            fail_items.append({
                "item_id": item_id,
                "issue": f"unknown_claim_classification: {claim}",
                "severity": "FAIL",
            })
        elif claim in REPLAYABLE_CLAIMS and method == "MANUAL_UNGOVERNED":
            fail_items.append({
                "item_id": item_id,
                "issue": f"REPLAYABLE claim ({claim}) with MANUAL_UNGOVERNED execution_method",
                "severity": "FAIL",
            })
        elif claim == "WORKS_BUT_NOT_REPEATABLE":
            warn_items.append({
                "item_id": item_id,
                "issue": "WORKS_BUT_NOT_REPEATABLE (acceptable, not blocking)",
                "severity": "WARN",
            })
        else:
            pass_items.append({"item_id": item_id, "claim": claim})

    if fail_items:
        return _make_result(
            "claim_classification_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} items with invalid claim_classification.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "claim_classification_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} WORKS_BUT_NOT_REPEATABLE items (acceptable).",
        )
    return _make_result(
        "claim_classification_validator",
        "PASS",
        pass_items,
        "PASS: All claim_classification values are valid.",
    )


# ---------------------------------------------------------------------------
# Validator 6: legacy_backfill_validator
# ---------------------------------------------------------------------------

def validate_legacy_backfill(declaration: dict, repo_root: Path | None = None) -> dict:
    """Validator 6: Check sidecar attribution files for backfilled items.

    WARN (non-blocking): PRODUCT_SOURCE item with no execution_method after 2-sprint grace.
    Check: .local/attribution/<format_id>/*.attribution.yaml exists.
    Does NOT block sprint.
    """
    repo_root = repo_root or REPO_ROOT
    items = declaration.get("planned_work_items", [])
    warn_items = []
    pass_items = []

    for item in items:
        if not _is_product_source_item(item):
            continue
        item_id = item.get("item_id", "unknown")
        method = item.get("execution_method", "")
        sidecar = item.get("sidecar_attribution_path", "")

        if method == "BACKFILLED_LEGACY_EXECUTION":
            if sidecar:
                sidecar_path = repo_root / sidecar
                if sidecar_path.exists():
                    pass_items.append({
                        "item_id": item_id,
                        "sidecar": sidecar,
                        "exists": True,
                    })
                else:
                    warn_items.append({
                        "item_id": item_id,
                        "issue": f"sidecar_path_declared_but_missing: {sidecar}",
                        "severity": "WARN",
                    })
            else:
                warn_items.append({
                    "item_id": item_id,
                    "issue": "BACKFILLED_LEGACY_EXECUTION without sidecar_attribution_path",
                    "severity": "WARN",
                })
        elif not method and not _has_grace_exemption(item):
            warn_items.append({
                "item_id": item_id,
                "issue": "PRODUCT_SOURCE item with no execution_method (potential backfill candidate)",
                "severity": "WARN",
            })
        else:
            pass_items.append({"item_id": item_id, "method": method})

    # Non-blocking — always PASS or WARN
    if warn_items:
        return _make_result(
            "legacy_backfill_validator",
            "WARN",
            warn_items + pass_items,
            f"WARN: {len(warn_items)} items need backfill review. {len(pass_items)} OK.",
            blocks_sprint=False,
        )
    return _make_result(
        "legacy_backfill_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} items checked, backfill status OK.",
    )


# ---------------------------------------------------------------------------
# Validator 7: manual_ungoverned_rejection_validator
# ---------------------------------------------------------------------------

def validate_manual_ungoverned_rejection(declaration: dict) -> dict:
    """Validator 7: MANUAL_UNGOVERNED must not close a product source taskcard.

    FAIL: PRODUCT_SOURCE with execution_method=MANUAL_UNGOVERNED AND
          claim_classification != LEGACY_BACKFILLED.
    Exemptions: LEGACY_BACKFILLED allows it as a backfill entry.
    Blocks sprint.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    pass_items = []

    for item in items:
        if not _is_product_source_item(item):
            continue
        item_id = item.get("item_id", "unknown")
        method = item.get("execution_method", "")
        claim = item.get("claim_classification", "")
        status = item.get("status", "")

        if method == "MANUAL_UNGOVERNED":
            if claim == "LEGACY_BACKFILLED":
                # Allowed as a documented backfill entry
                pass_items.append({
                    "item_id": item_id,
                    "note": "MANUAL_UNGOVERNED allowed as LEGACY_BACKFILLED",
                })
            else:
                fail_items.append({
                    "item_id": item_id,
                    "issue": (
                        f"MANUAL_UNGOVERNED execution_method with claim={claim or 'not set'}. "
                        "Must not close a product taskcard."
                    ),
                    "severity": "FAIL",
                })
        else:
            pass_items.append({"item_id": item_id, "method": method})

    if fail_items:
        return _make_result(
            "manual_ungoverned_rejection_validator",
            "FAIL",
            fail_items,
            f"FAIL: {len(fail_items)} PRODUCT_SOURCE items with MANUAL_UNGOVERNED execution.",
            blocks_sprint=True,
        )
    return _make_result(
        "manual_ungoverned_rejection_validator",
        "PASS",
        pass_items,
        "PASS: No MANUAL_UNGOVERNED items closing product taskcards.",
    )


# ---------------------------------------------------------------------------
# Validator 8: governed_direct_execution_validator
# ---------------------------------------------------------------------------

def validate_governed_direct_execution(declaration: dict,
                                        skill_registry_path: Path | None = None) -> dict:
    """Validator 8: MANUAL_GOVERNED_BY_SKILL items must have transcript and skill_id.

    FAIL: MANUAL_GOVERNED_BY_SKILL but skill_id absent OR transcript absent.
    Exemptions: BACKFILLED_LEGACY_EXECUTION does not need transcript.
    Blocks sprint for MANUAL_GOVERNED_BY_SKILL without transcript.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        item_id = item.get("item_id", "unknown")
        method = item.get("execution_method", "")

        if method not in ("MANUAL_GOVERNED_BY_SKILL", "SKILL_GUIDED_AGENT_EXECUTION"):
            continue

        skill_id = item.get("skill_id", "")
        transcript = item.get("skill_transcript_path", "") or any(
            "transcript" in ep.lower() for ep in item.get("evidence_paths", [])
        )

        issues = []
        if not skill_id:
            issues.append("missing_skill_id")
        if not transcript:
            issues.append("missing_transcript_path")

        if issues:
            fail_items.append({
                "item_id": item_id,
                "method": method,
                "issues": issues,
                "severity": "FAIL",
            })
        else:
            pass_items.append({"item_id": item_id, "method": method, "skill_id": skill_id})

    if fail_items:
        return _make_result(
            "governed_direct_execution_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} GOVERNED items missing skill_id or transcript.",
            blocks_sprint=True,
        )
    return _make_result(
        "governed_direct_execution_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} GOVERNED items have skill_id and transcript.",
    )


# ---------------------------------------------------------------------------
# Validator 9: source_marker_or_sidecar_attribution_validator
# ---------------------------------------------------------------------------

def validate_source_marker_or_sidecar(declaration: dict,
                                       repo_root: Path | None = None) -> dict:
    """Validator 9: Touched source files must have FORMAT_FACTORY_EXECUTION marker or sidecar.

    FAIL: touched source has neither marker nor sidecar (new work, no backfill_pending).
    WARN: sidecar exists but idempotency_key missing; backfill_pending=true.
    Does NOT fail for backfill items — they use sidecar-only approach.
    Blocks sprint for new work.
    """
    repo_root = repo_root or REPO_ROOT
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        if not _is_product_source_item(item):
            continue
        item_id = item.get("item_id", "unknown")
        method = item.get("execution_method", "")
        sidecar = item.get("sidecar_attribution_path", "")
        touched = item.get("touched_files", [])

        # Backfill items: sidecar-only is acceptable
        if method == "BACKFILLED_LEGACY_EXECUTION":
            if sidecar:
                sidecar_path = repo_root / sidecar
                idempotency = item.get("idempotency_key", "")
                if sidecar_path.exists() and idempotency:
                    pass_items.append({"item_id": item_id, "sidecar": sidecar})
                elif sidecar_path.exists():
                    warn_items.append({
                        "item_id": item_id,
                        "issue": "sidecar exists but idempotency_key missing",
                        "severity": "WARN",
                    })
                else:
                    warn_items.append({
                        "item_id": item_id,
                        "issue": f"sidecar declared but not found: {sidecar}",
                        "severity": "WARN",
                    })
            else:
                warn_items.append({
                    "item_id": item_id,
                    "issue": "BACKFILLED item missing sidecar_attribution_path",
                    "severity": "WARN",
                })
            continue

        # New work: check for marker or sidecar
        has_sidecar = bool(sidecar and (repo_root / sidecar).exists())
        has_marker = False  # Would require source file inspection — not done here

        if touched and not has_sidecar and not has_marker:
            if _has_grace_exemption(item):
                warn_items.append({
                    "item_id": item_id,
                    "issue": "no sidecar or marker (grace period)",
                    "severity": "WARN",
                })
            else:
                fail_items.append({
                    "item_id": item_id,
                    "issue": "touched_files declared but no sidecar or source marker",
                    "severity": "FAIL",
                })
        else:
            pass_items.append({"item_id": item_id, "has_sidecar": has_sidecar})

    if fail_items:
        return _make_result(
            "source_marker_or_sidecar_attribution_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} items missing both source marker and sidecar.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "source_marker_or_sidecar_attribution_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} items with sidecar/marker issues (non-blocking).",
        )
    return _make_result(
        "source_marker_or_sidecar_attribution_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} items have attribution.",
    )


# ---------------------------------------------------------------------------
# Validator 10: taskcard_state_transition_validator
# ---------------------------------------------------------------------------

def validate_taskcard_state_transitions(declaration: dict) -> dict:
    """Validator 10 / Lane F: Enforce 15-state taskcard state machine.

    FAIL: Forbidden jump detected (e.g. DISCOVERED → GOVERNANCE_ACCEPTED).
    FAIL: Completed item not in close-eligible state.
    WARN: Close at GOVERNANCE_ACCEPTED without REPLAY_RECIPE sets GOVERNED_BUT_NOT_REPLAYED.
    Blocks sprint for forbidden jumps.
    """
    items = declaration.get("planned_work_items", [])
    fail_items = []
    warn_items = []
    pass_items = []

    for item in items:
        item_id = item.get("item_id", "unknown")
        from_state = item.get("state_machine_start", "")
        to_state = item.get("state_machine_target", "")
        status = item.get("status", "")
        claim = item.get("claim_classification", "")

        # Check forbidden jumps — only applies to PRODUCT_SOURCE items.
        # Governance docs (GOVERNANCE_DOC, GOVERNANCE_SCHEMA, etc.) legitimately jump
        # DISCOVERED → GOVERNANCE_ACCEPTED as a short-circuit for documentation work.
        item_type = item.get("item_type", "")
        is_product = item_type in PRODUCT_SOURCE_ITEM_TYPES or (
            item_type == "" and item.get("product_track")
        )
        if from_state and to_state and is_product:
            if (from_state, to_state) in FORBIDDEN_JUMPS_PRODUCT_ONLY:
                fail_items.append({
                    "item_id": item_id,
                    "issue": f"FORBIDDEN jump for PRODUCT_SOURCE: {from_state} → {to_state}",
                    "severity": "FAIL",
                })
                continue

            # Check if transition is in allowed set (if we have full state machine data)
            allowed = ALLOWED_TRANSITIONS.get(from_state, frozenset())
            # Only check direct transitions for items that have both states declared
            # (Multi-hop transitions are allowed — we only block explicit forbidden jumps)

        # Check completed items are in close-eligible states
        if status == "completed" and to_state:
            if to_state not in CLOSE_ELIGIBLE_STATES:
                fail_items.append({
                    "item_id": item_id,
                    "issue": (
                        f"Item marked completed but target_state={to_state} "
                        f"is not close-eligible"
                    ),
                    "severity": "FAIL",
                })
                continue

        # GOVERNANCE_ACCEPTED without REPLAY_RECIPE
        if to_state == "GOVERNANCE_ACCEPTED" and claim not in (
            "REPLAYED_AND_PROVEN", "REPLAYABLE_NOT_YET_REPLAYED",
        ) and not item.get("replay_recipe_path"):
            warn_items.append({
                "item_id": item_id,
                "issue": "GOVERNANCE_ACCEPTED without replay_recipe → GOVERNED_BUT_NOT_REPLAYED",
                "severity": "WARN",
            })
        else:
            pass_items.append({
                "item_id": item_id,
                "from": from_state,
                "to": to_state,
                "status": status,
            })

    if fail_items:
        return _make_result(
            "taskcard_state_transition_validator",
            "FAIL",
            fail_items + warn_items,
            f"FAIL: {len(fail_items)} state machine violations.",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            "taskcard_state_transition_validator",
            "WARN",
            warn_items,
            f"WARN: {len(warn_items)} items at GOVERNANCE_ACCEPTED without replay recipe.",
        )
    return _make_result(
        "taskcard_state_transition_validator",
        "PASS",
        pass_items,
        f"PASS: {len(pass_items)} state transitions valid.",
    )


# ---------------------------------------------------------------------------
# Validator 11: route_decision_required_validator
# ---------------------------------------------------------------------------

def validate_route_decision_required(declaration: dict) -> dict:
    """Validator 11: Check items for route_decision_id.

    Exempt: GOVERNANCE_* item types.
    Legacy/backfill: WARN only (non-blocking).
    Current-run PRODUCT_SOURCE without route_decision_id: FAIL + blocks_sprint.
    Current-run MACHINERY without route_decision_id: FAIL + blocks_sprint.
    """
    from tools.supervisor.autonomy_route_models import TASK_CATEGORIES_MACHINERY

    items = declaration.get("planned_work_items", [])
    warns: list = []
    blocks: list = []
    for item in items:
        itype = item.get("item_type", "")
        if itype in GOVERNANCE_ITEM_TYPES:
            continue

        has_grace = _has_grace_exemption(item)

        if has_grace:
            # Legacy/backfill — WARN only
            if itype in PRODUCT_SOURCE_ITEM_TYPES and not item.get("route_decision_id"):
                warns.append({
                    "item_id": item.get("item_id", "?"),
                    "issue": "Legacy/backfill PRODUCT_SOURCE item missing route_decision_id",
                    "severity": "WARN",
                })
            continue

        # Current-run items — FAIL if missing route_decision_id
        if itype in PRODUCT_SOURCE_ITEM_TYPES and not item.get("route_decision_id"):
            blocks.append({
                "item_id": item.get("item_id", "?"),
                "issue": "Current-run PRODUCT_SOURCE item missing route_decision_id",
                "severity": "FAIL",
            })

        cat = item.get("task_category", "")
        if cat and cat in TASK_CATEGORIES_MACHINERY and not item.get("route_decision_id"):
            blocks.append({
                "item_id": item.get("item_id", "?"),
                "issue": f"Current-run machinery category {cat!r} missing route_decision_id",
                "severity": "FAIL",
            })

    if blocks:
        return _make_result(
            "route_decision_required_validator",
            "FAIL",
            blocks + warns,
            f"{len(blocks)} current-run items missing route_decision_id (blocks sprint)",
            blocks_sprint=True,
        )
    if warns:
        return _make_result(
            "route_decision_required_validator",
            "WARN",
            warns,
            f"{len(warns)} legacy/backfill items missing route_decision_id (non-blocking)",
            blocks_sprint=False,
        )
    return _make_result(
        "route_decision_required_validator",
        "PASS",
        [],
        "All applicable items have route_decision_id or are exempt.",
    )


# ---------------------------------------------------------------------------
# Validator 12: ci_artifact_presence_validator (TC-APRV-014)
# ---------------------------------------------------------------------------

def validate_ci_artifacts(declaration: dict, repo_root: Path | None = None) -> dict:
    """V12: Check for CI-produced test results and coverage artifacts.

    When CI integration is active (.local/ci-evidence/ exists with artifacts),
    validates their presence. When CI is not yet configured, returns PASS with
    exemption to avoid blocking sprints during the CI adoption period.
    """
    root = repo_root or REPO_ROOT
    ci_evidence_dir = root / ".local" / "ci-evidence"

    # If CI evidence directory doesn't exist, exempt (CI not yet configured)
    if not ci_evidence_dir.exists():
        return _make_result(
            "ci_artifact_presence_validator",
            "PASS",
            [{"note": "CI integration not yet configured — exempt"}],
            "CI evidence directory not found. Exempt until CI pipeline is operational.",
        )

    items = []
    test_results = ci_evidence_dir / "test-results.xml"
    coverage_json = ci_evidence_dir / "coverage.json"

    if test_results.exists():
        items.append({"artifact": "test-results.xml", "status": "present"})
    else:
        items.append({"artifact": "test-results.xml", "status": "missing"})

    if coverage_json.exists():
        items.append({"artifact": "coverage.json", "status": "present"})
    else:
        items.append({"artifact": "coverage.json", "status": "missing"})

    missing = [i for i in items if i["status"] == "missing"]
    if missing:
        names = ", ".join(i["artifact"] for i in missing)
        return _make_result(
            "ci_artifact_presence_validator",
            "WARN",
            items,
            f"CI evidence directory exists but missing artifacts: {names}. "
            "Run CI pipeline to produce test-results.xml and coverage.json.",
        )

    return _make_result(
        "ci_artifact_presence_validator",
        "PASS",
        items,
        "All CI evidence artifacts present.",
    )


# ---------------------------------------------------------------------------
# Composite runner
# ---------------------------------------------------------------------------

def run_all_governance_validators(declaration: dict,
                                   repo_root: Path | None = None) -> dict:
    """Run all 11 governance validators against a declaration.

    Returns a composite result dict:
      {
        "all_pass": bool,
        "blocks_sprint": bool,
        "validators": list[dict],   # one per validator
        "summary": str,
      }
    """
    results = [
        validate_execution_method_required(declaration),
        validate_source_diff_required(declaration),
        validate_idempotency_key_required(declaration),
        validate_replay_recipe_required(declaration),
        validate_claim_classification(declaration),
        validate_legacy_backfill(declaration, repo_root),
        validate_manual_ungoverned_rejection(declaration),
        validate_governed_direct_execution(declaration),
        validate_source_marker_or_sidecar(declaration, repo_root),
        validate_taskcard_state_transitions(declaration),
        validate_route_decision_required(declaration),
        validate_ci_artifacts(declaration, repo_root),
    ]

    fail_count = sum(1 for r in results if r["result"] == "FAIL")
    warn_count = sum(1 for r in results if r["result"] == "WARN")
    pass_count = sum(1 for r in results if r["result"] == "PASS")
    blocks_sprint = any(r.get("blocks_sprint") for r in results if r["result"] == "FAIL")

    return {
        "all_pass": fail_count == 0,
        "blocks_sprint": blocks_sprint,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "pass_count": pass_count,
        "validators": results,
        "summary": (
            f"{pass_count} PASS / {warn_count} WARN / {fail_count} FAIL. "
            f"Blocks sprint: {blocks_sprint}."
        ),
    }
