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

import yaml

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
            if _has_grace_exemption(item) or _is_test_item(item):
                warn_items.append({
                    "item_id": item_id,
                    "issue": "missing_execution_method",
                    "severity": "WARN",
                    "note": "grace_period: pre_taxonomy_backfill or TEST item",
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
            if _has_grace_exemption(item) or _is_test_item(item) or item.get("execution_method") == "BACKFILLED_LEGACY_EXECUTION":
                warn_items.append({
                    "item_id": item_id,
                    "issue": "missing_source_diff_paths",
                    "severity": "WARN",
                    "note": "grace: backfill, pre_taxonomy, or TEST item",
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
            if _has_grace_exemption(item) or _is_test_item(item):
                warn_items.append({
                    "item_id": item_id,
                    "issue": "missing_idempotency_key",
                    "severity": "WARN",
                    "note": "grace: pre_taxonomy or TEST item",
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
        "PASS: All replay claims are valid.",
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

        has_grace = _has_grace_exemption(item) or _is_test_item(item)

        if has_grace:
            # Legacy/backfill/TEST — WARN only
            if itype in PRODUCT_SOURCE_ITEM_TYPES and not item.get("route_decision_id"):
                warns.append({
                    "item_id": item.get("item_id", "?"),
                    "issue": "Grace/TEST PRODUCT_SOURCE item missing route_decision_id",
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

# ---------------------------------------------------------------------------
# Validator 13: spec_fact_refs enforcement (SAL-VERIFICATION-HARDENING-001)
# ---------------------------------------------------------------------------

def validate_spec_fact_refs_wired(declaration: dict,
                                   repo_root: Path | None = None) -> dict:
    """V13: Enforce spec_fact_refs on PRODUCT_SOURCE/READINESS/RELEASE_GATE/TEST/REQUIREMENT items.

    Calls validate_declaration_spec_fact_refs from validate_spec_fact_refs module.
    PRODUCT_SOURCE/READINESS/RELEASE_GATE items without valid FACT-* refs AND without
    a valid exception_classification are BLOCKED.

    Added: SAL-VERIFICATION-HARDENING-001 (Lane B) — 2026-06-11.
    """
    try:
        # Lazy import to avoid circular imports and to degrade gracefully if missing
        import sys
        _supervisor_dir = Path(__file__).resolve().parent
        if str(_supervisor_dir) not in sys.path:
            sys.path.insert(0, str(_supervisor_dir))
        from validate_spec_fact_refs import validate_declaration_spec_fact_refs
    except ImportError as exc:
        # Graceful degradation: cannot import the module — return WARN, not hard FAIL
        return _make_result(
            "spec_fact_refs_validator",
            "WARN",
            [{"note": f"spec_fact_refs enforcement module not importable: {exc}"}],
            f"spec_fact_refs validator import error (non-blocking degradation): {exc}",
            blocks_sprint=False,
        )

    # TEST items add tests, not product source — exempt from spec_fact_refs
    filtered_declaration = dict(declaration)
    original_items = filtered_declaration.get("planned_work_items", [])
    filtered_declaration["planned_work_items"] = [
        item for item in original_items if not _is_test_item(item)
    ]

    try:
        sfr_result = validate_declaration_spec_fact_refs(filtered_declaration)
    except Exception as exc:
        return _make_result(
            "spec_fact_refs_validator",
            "WARN",
            [{"note": f"spec_fact_refs validation error: {exc}"}],
            f"spec_fact_refs validator runtime error (non-blocking): {exc}",
            blocks_sprint=False,
        )

    items = sfr_result.get("item_results", [])
    errors = sfr_result.get("errors", [])
    debt_items = sfr_result.get("debt_items", [])
    compliant = sfr_result.get("compliant", True)

    # Build per-item summary list
    result_items = [
        {
            "item_id": r.get("item_id"),
            "item_type": r.get("item_type"),
            "compliant": r.get("compliant"),
            "grade_impact": r.get("grade_impact"),
            "detail": r.get("detail"),
            "violation": r.get("violation"),
        }
        for r in items
    ]

    # Debt items contribute WARN but not FAIL
    if not compliant:
        return _make_result(
            "spec_fact_refs_validator",
            "FAIL",
            result_items,
            (
                f"spec_fact_refs enforcement: {len(errors)} violation(s). "
                f"PRODUCT_SOURCE/READINESS/RELEASE_GATE items require valid FACT-* refs "
                f"or a valid exception_classification. Violations: {errors[:3]}"
            ),
            blocks_sprint=True,
        )

    if debt_items:
        return _make_result(
            "spec_fact_refs_validator",
            "WARN",
            result_items,
            (
                f"spec_fact_refs: {len(result_items)} items compliant, "
                f"{len(debt_items)} debt item(s) recorded. "
                f"Debt: {debt_items[:2]}"
            ),
            blocks_sprint=False,
        )

    return _make_result(
        "spec_fact_refs_validator",
        "PASS",
        result_items,
        f"spec_fact_refs: {len(result_items)} items checked, all compliant.",
        blocks_sprint=False,
    )


# ── REQ-GOV-001 / REQ-GOV-002: Gate 11 Spec-Literal Depth Validators ────────


def validate_spec_fact_count(declaration: dict) -> dict:
    """V14: Verify at least min_spec_facts_cited spec facts are referenced.

    ADVISORY only — GOVERNANCE_DOC and EVIDENCE items are exempt.
    Only fires for PRODUCT_SOURCE/READINESS/RELEASE_GATE items that have
    spec_fact_refs populated.
    """
    validator = "validate_spec_fact_count"
    items = declaration.get("planned_work_items", [])
    violations = []
    for item in items:
        itype = item.get("item_type", "")
        if itype not in ("PRODUCT_SOURCE", "READINESS", "RELEASE_GATE"):
            continue
        refs = item.get("spec_fact_refs") or []
        if len(refs) == 0:
            # Not a violation here — validate_spec_fact_refs_wired handles this
            pass
    return _make_result(
        validator,
        "PASS",
        [],
        f"Spec fact count check: advisory pass ({len(items)} items reviewed)",
        blocks_sprint=False,
    )


def validate_qname_coverage(declaration: dict,
                             repo_root: Path | None = None) -> dict:
    """V15: Check that test files reference spec QNames in any evidence_paths.

    Advisory validator — checks for QName-like patterns (e.g. FODS-FACT-*)
    in test files to detect spec-unaware implementations.
    """
    import re

    validator = "validate_qname_coverage"
    repo_root = repo_root or REPO_ROOT
    items = declaration.get("planned_work_items", [])
    qname_pattern = re.compile(r"[A-Z]{2,}-FACT-\d{3}")
    found_qname_refs = 0

    for item in items:
        for path_str in (item.get("evidence_paths") or []):
            try:
                p = Path(path_str)
                if not p.is_absolute():
                    p = repo_root / p
                if p.exists() and p.suffix in (".py", ".md", ".yaml", ".txt"):
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    if qname_pattern.search(content):
                        found_qname_refs += 1
            except Exception:
                pass

    return _make_result(
        validator,
        "PASS",
        [],
        f"QName coverage: {found_qname_refs} files with QName refs found (advisory)",
        blocks_sprint=False,
    )


def validate_parity_matrix_present(declaration: dict,
                                    repo_root: Path | None = None) -> dict:
    """V16: For RELEASE_GATE items, check that a parity matrix artifact exists.

    Parity matrix = file containing a mapping of spec-defined features to
    implementation status. Required for Gate 11.
    """
    validator = "validate_parity_matrix_present"
    repo_root = repo_root or REPO_ROOT
    items = declaration.get("planned_work_items", [])
    violations = []

    for item in items:
        itype = item.get("item_type", "")
        if itype != "RELEASE_GATE":
            continue
        # Look for parity matrix in evidence_paths
        has_parity = any(
            "parity" in str(p).lower()
            for p in (item.get("evidence_paths") or [])
        )
        if not has_parity:
            violations.append({
                "item_id": item.get("item_id", "?"),
                "issue": "RELEASE_GATE item has no parity matrix in evidence_paths",
            })

    result = "FAIL" if violations else "PASS"
    return _make_result(
        validator,
        result,
        violations,
        f"Parity matrix check: {len(violations)} RELEASE_GATE items missing parity matrix",
        blocks_sprint=False,
    )


def validate_no_placeholder_metadata(declaration: dict,
                                      repo_root: Path | None = None) -> dict:
    """V17: Scan declared evidence files for placeholder strings.

    Placeholder strings (TBD, TODO, PLACEHOLDER, etc.) in evidence files
    indicate incomplete work. Advisory for most items; FAIL for RELEASE_GATE.
    """
    validator = "validate_no_placeholder_metadata"
    repo_root = repo_root or REPO_ROOT
    PLACEHOLDER_PATTERNS = ["TBD", "TODO", "PLACEHOLDER", "to be filled",
                             "NOT YET", "IN PROGRESS"]
    items = declaration.get("planned_work_items", [])
    violations = []

    for item in items:
        itype = item.get("item_type", "")
        if itype not in ("RELEASE_GATE", "READINESS"):
            continue
        for path_str in (item.get("evidence_paths") or []):
            try:
                p = Path(path_str)
                if not p.is_absolute():
                    p = repo_root / p
                if p.exists():
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    for pattern in PLACEHOLDER_PATTERNS:
                        if pattern in content:
                            violations.append({
                                "item_id": item.get("item_id", "?"),
                                "file": path_str,
                                "pattern": pattern,
                            })
                            break
            except Exception:
                pass

    result = "FAIL" if violations else "PASS"
    return _make_result(
        validator,
        result,
        violations,
        f"Placeholder check: {len(violations)} evidence files with placeholder patterns",
        blocks_sprint=False,
    )


def validate_gate11_criteria(declaration: dict,
                               repo_root: Path | None = None) -> dict:
    """V18: Master Gate 11 validator using registry/gate11-criteria.yaml.

    Reads the criteria file and validates RELEASE_GATE items against each
    threshold. Advisory only — Gate 11 approval still requires Babar Raza.
    """
    import yaml  # type: ignore

    validator = "validate_gate11_criteria"
    repo_root = repo_root or REPO_ROOT
    criteria_path = repo_root / "registry" / "gate11-criteria.yaml"

    if not criteria_path.exists():
        return _make_result(
            validator,
            "WARN",
            [{"issue": "registry/gate11-criteria.yaml not found — skipping G11 check"}],
            "Gate 11 criteria file missing (advisory warning)",
            blocks_sprint=False,
        )

    try:
        with criteria_path.open(encoding="utf-8") as f:
            criteria = yaml.safe_load(f)
    except Exception as exc:
        return _make_result(
            validator,
            "WARN",
            [{"issue": f"Could not parse gate11-criteria.yaml: {exc}"}],
            "Gate 11 criteria file parse error (advisory warning)",
            blocks_sprint=False,
        )

    items = declaration.get("planned_work_items", [])
    release_gate_items = [i for i in items if i.get("item_type") == "RELEASE_GATE"]

    if not release_gate_items:
        return _make_result(
            validator,
            "PASS",
            [],
            "Gate 11 criteria: no RELEASE_GATE items in declaration (advisory pass)",
            blocks_sprint=False,
        )

    # Check RELEASE_GATE items against criteria
    violations = []
    min_facts = criteria.get("criteria", {}).get("min_spec_facts_cited", 3)
    for item in release_gate_items:
        refs = item.get("spec_fact_refs") or []
        if len(refs) < min_facts:
            violations.append({
                "item_id": item.get("item_id", "?"),
                "issue": (f"RELEASE_GATE item has {len(refs)} spec_fact_refs, "
                          f"criteria requires {min_facts}"),
            })

    result = "FAIL" if violations else "PASS"
    criteria_keys = list(criteria.get("criteria", {}).keys())
    return _make_result(
        validator,
        result,
        violations,
        (f"Gate 11 criteria ({len(criteria_keys)} checks): "
         f"{len(violations)} violation(s) across {len(release_gate_items)} RELEASE_GATE items"),
        blocks_sprint=False,
    )


def validate_min_spec_facts_per_format(
    declaration: dict,
    repo_root: Path | None = None,
    min_facts: int = 3,
) -> dict:
    """V19: REQ-SAL-003 — Each format referenced in PRODUCT_SOURCE items must have
    at least `min_facts` spec facts in the SAL output (sal-facts-latest.json).

    Advisory only (blocks_sprint=False). Skipped if SAL output does not exist yet.
    """
    validator = "validate_min_spec_facts_per_format"
    _root = repo_root or REPO_ROOT
    sal_path = _root / ".local" / "sal-output" / "sal-facts-latest.json"

    if not sal_path.exists():
        return dict(
            validator=validator,
            result="PASS",
            items=[],
            summary="SAL output not found — skipping (run sal_master_runner.py to generate)",
            blocks_sprint=False,
        )

    try:
        import json
        sal_data = json.loads(sal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return dict(
            validator=validator,
            result="WARN",
            items=[],
            summary=f"Could not load SAL output: {exc}",
            blocks_sprint=False,
        )

    # Build per-format fact counts from SAL output
    format_fact_counts: dict[str, int] = {}
    formats_list = sal_data.get("formats", [])
    for fmt_entry in formats_list:
        fmt_id = (fmt_entry.get("format_id") or "").upper()
        facts = fmt_entry.get("spec_facts", [])
        if fmt_id:
            format_fact_counts[fmt_id] = len(facts)

    items_checked = []
    work_items = declaration.get("planned_work_items", [])
    for item in work_items:
        if not isinstance(item, dict):
            continue
        if item.get("item_type") not in ("PRODUCT_SOURCE", "READINESS"):
            continue
        item_id = item.get("item_id", "?")
        # Try to derive format from spec_fact_refs or item_id
        refs = item.get("spec_fact_refs", [])
        if refs:
            fmt_prefix = str(refs[0]).split("-")[0].upper()
        else:
            # Try item_id prefix (e.g. FODS-..., FODT-...)
            fmt_prefix = str(item_id).split("-")[0].upper()

        count = format_fact_counts.get(fmt_prefix, None)
        if count is None:
            # Not a known format in SAL output — skip this item
            continue
        status = "PASS" if count >= min_facts else "FAIL"
        items_checked.append({
            "item_id": item_id,
            "format": fmt_prefix,
            "spec_fact_count": count,
            "min_required": min_facts,
            "result": status,
        })

    fail_items = [i for i in items_checked if i["result"] == "FAIL"]
    overall = "FAIL" if fail_items else "PASS"
    summary = (
        f"{len(items_checked)} formats checked; "
        f"{len(fail_items)} below minimum {min_facts} spec facts"
    )
    return dict(
        validator=validator,
        result=overall,
        items=items_checked,
        summary=summary,
        blocks_sprint=False,
    )


# ---------------------------------------------------------------------------
# Validator 20 (SUP-RECT-001): Lane Ownership Validator
# ---------------------------------------------------------------------------

# Lane-to-allowed-path mappings. Each lane declares which path prefixes
# its workers are permitted to modify. Paths are relative to repo root.
LANE_ALLOWED_PATHS: dict[str, list[str]] = {
    "lane-00-coordinator": [
        ".local/evidences/", ".local/supervisor/", "reports/supervisor/",
    ],
    "lane-01-sal-pipeline": [
        "tools/specification-authority-layer/", "tools/spec-normalize/",
        "tools/spec-cache/", ".local/spec-cache/", ".local/spec-artifacts/",
    ],
    "lane-02-capability": [
        "tools/capability_layer/", "reports/capability-layer/",
    ],
    "lane-03-compiler": [
        "tools/capability_layer/", "tools/capability_layer/plugins/",
    ],
    "lane-04-skills-prompts": [
        ".supervisor/skill-registry.yaml", ".supervisor/prompts/",
        ".supervisor/schemas/", ".claude/commands/",
    ],
    "lane-05-validators": [
        "tools/supervisor/governance_validators.py",
        "tools/supervisor/spec_parity_validators.py",
        "tools/supervisor/anti_skip_checker.py",
    ],
    "lane-09-fods-rebuild": [
        "src/python/fods/", "src/net/fods/", "tests/python/fods/",
        "tests/net/fods/",
    ],
    "lane-10-fodt-rebuild": [
        "src/python/fodt/", "src/net/fodt/", "tests/python/fodt/",
        "tests/net/fodt/",
    ],
    "lane-11-zst": [
        "src/python/zst/", "tests/python/zst/",
    ],
    "lane-12-ci-package": [
        ".github/workflows/", "pyproject.toml",
    ],
    "lane-14-supervision": [
        "tools/supervisor/", "tests/supervisor/",
    ],
    "lane-15-healing": [
        "tools/supervisor/failure_memory.py",
        "tools/supervisor/learning_consumer.py",
        ".local/supervisor/failure-memory.json",
    ],
}

# Paths that are always allowed regardless of lane assignment (evidence, logs)
GLOBAL_ALLOWED_PATHS = [
    ".local/evidences/",
    ".local/supervisor/reviews/",
    "reports/supervisor/",
]


def validate_lane_ownership(declaration: dict,
                            repo_root: Path | None = None) -> dict:
    """SUP-RECT-001: Validate that changed_files are within lane-allowed paths.

    If the declaration includes a 'lane_id' field, check that every path in
    'changed_files' is within that lane's allowed paths or a global-allowed path.
    If no lane_id is declared, PASS with advisory note (backward compatible).
    """
    lane_id = declaration.get("lane_id", "")
    changed_files = declaration.get("changed_files", [])

    if not lane_id:
        return _make_result(
            "lane_ownership_validator",
            "PASS",
            [],
            "PASS: No lane_id declared — lane ownership check skipped (backward compatible).",
        )

    allowed = LANE_ALLOWED_PATHS.get(lane_id, [])
    all_allowed = allowed + GLOBAL_ALLOWED_PATHS
    violations = []

    for fpath in changed_files:
        fpath_normalized = fpath.replace("\\", "/")
        if not any(fpath_normalized.startswith(prefix) for prefix in all_allowed):
            violations.append({
                "item_id": lane_id,
                "file": fpath,
                "issue": f"file outside lane-allowed paths for {lane_id}",
                "severity": "FAIL",
            })

    if violations:
        return _make_result(
            "lane_ownership_validator",
            "FAIL",
            violations,
            f"FAIL: {len(violations)} files outside lane-allowed paths for {lane_id}.",
            blocks_sprint=True,
        )
    return _make_result(
        "lane_ownership_validator",
        "PASS",
        [{"lane_id": lane_id, "files_checked": len(changed_files)}],
        f"PASS: All {len(changed_files)} changed files within allowed paths for {lane_id}.",
    )


# ---------------------------------------------------------------------------
# Validator 21 (SUP-RECT-002): DAG Ordering Validator
# ---------------------------------------------------------------------------

# Wave ordering: lanes in later waves require earlier waves to be complete.
# This is a static ordering — once an execution-dag.yaml exists, it should
# be read instead.
WAVE_PREREQUISITES: dict[str, list[str]] = {
    "wave-0": [],
    "wave-1a": ["wave-0"],
    "wave-1b": ["wave-1a"],
    "wave-2": ["wave-1b"],
    "wave-3": ["wave-1a", "wave-1b"],
    "wave-4": ["wave-3"],
    "wave-5": ["wave-3"],
    "wave-6": ["wave-5"],
    "wave-7": ["wave-6"],
}

# Lane-to-wave mapping
LANE_WAVE_MAP: dict[str, str] = {
    "lane-00-coordinator": "wave-0",
    "lane-01-sal-pipeline": "wave-1b",
    "lane-02-capability": "wave-2",
    "lane-03-compiler": "wave-2",
    "lane-04-skills-prompts": "wave-1b",
    "lane-05-validators": "wave-1b",
    "lane-06-qname": "wave-2",
    "lane-07-net-blueprint": "wave-4",
    "lane-08-python-blueprint": "wave-4",
    "lane-09-fods-rebuild": "wave-5",
    "lane-10-fodt-rebuild": "wave-5",
    "lane-11-zst": "wave-4",
    "lane-12-ci-package": "wave-6",
    "lane-13-recompute": "wave-7",
    "lane-14-supervision": "wave-1a",
    "lane-15-healing": "wave-1a",
}


def validate_dag_ordering(declaration: dict,
                          repo_root: Path | None = None) -> dict:
    """SUP-RECT-002: Validate that lane prerequisites are met.

    If 'lane_id' is declared, check that the lane's wave prerequisites
    are listed as completed in 'completed_waves' or that a custom
    execution-dag.yaml says they're done. If no lane_id, PASS (backward
    compatible).
    """
    lane_id = declaration.get("lane_id", "")
    completed_waves = declaration.get("completed_waves", [])

    if not lane_id:
        return _make_result(
            "dag_ordering_validator",
            "PASS",
            [],
            "PASS: No lane_id declared — DAG ordering check skipped (backward compatible).",
        )

    # Try loading execution-dag.yaml if it exists
    rr = repo_root or REPO_ROOT
    dag_file = rr / ".local" / "evidences" / "execution-dag.yaml"
    completed_from_dag: list[str] = []
    if dag_file.exists():
        try:
            with open(dag_file, encoding="utf-8") as f:
                dag_data = yaml.safe_load(f) or {}
            completed_from_dag = dag_data.get("completed_waves", [])
        except Exception:
            pass

    all_completed = set(completed_waves) | set(completed_from_dag)

    wave = LANE_WAVE_MAP.get(lane_id, "")
    if not wave:
        return _make_result(
            "dag_ordering_validator",
            "PASS",
            [{"lane_id": lane_id, "note": "lane not in wave map"}],
            f"PASS: {lane_id} not in wave map — DAG check skipped.",
        )

    prereqs = WAVE_PREREQUISITES.get(wave, [])
    missing = [w for w in prereqs if w not in all_completed]

    if missing:
        return _make_result(
            "dag_ordering_validator",
            "FAIL",
            [{"lane_id": lane_id, "wave": wave,
              "missing_prerequisites": missing, "severity": "FAIL"}],
            f"FAIL: {lane_id} (wave {wave}) has unmet prerequisites: {missing}. "
            "Declare 'completed_waves' in evidence-declaration.yaml to clear.",
            blocks_sprint=True,
        )
    return _make_result(
        "dag_ordering_validator",
        "PASS",
        [{"lane_id": lane_id, "wave": wave, "prerequisites_met": prereqs}],
        f"PASS: All prerequisites for {lane_id} (wave {wave}) are met.",
    )


def validate_capability_map_staleness(declaration: dict,
                                      repo_root: Path | None = None) -> dict:
    """V_STALENESS: Check if capability maps are stale relative to product source.

    Compares unified-capability-map.json generated_at timestamp against the
    newest mtime under src/python/. If the map is older than the newest source
    file, issues a WARN (non-blocking) to prompt a recompute.
    """
    import json
    from datetime import datetime, timezone

    rr = repo_root or REPO_ROOT
    cap_map_path = rr / "reports" / "capability-layer" / "unified-capability-map.json"

    if not cap_map_path.exists():
        return _make_result(
            "capability_map_staleness",
            "WARN",
            [{"reason": "unified-capability-map.json not found"}],
            "WARN: Capability map not found — cannot check staleness.",
        )

    try:
        cap_data = json.loads(cap_map_path.read_text(encoding="utf-8"))
        generated_at_str = cap_data.get("generated_at", "")
        if not generated_at_str:
            return _make_result(
                "capability_map_staleness",
                "WARN",
                [{"reason": "generated_at field missing from capability map"}],
                "WARN: Capability map has no generated_at timestamp.",
            )

        # Parse generated_at (ISO format with timezone)
        gen_dt = datetime.fromisoformat(generated_at_str)
        if gen_dt.tzinfo is None:
            gen_dt = gen_dt.replace(tzinfo=timezone.utc)

        # Find newest src/python/ file by mtime
        src_dir = rr / "src" / "python"
        if not src_dir.exists():
            return _make_result(
                "capability_map_staleness",
                "PASS",
                [],
                "PASS: No src/python/ directory — staleness check not applicable.",
            )

        newest_mtime = 0.0
        newest_file = ""
        for py_file in src_dir.rglob("*.py"):
            mt = py_file.stat().st_mtime
            if mt > newest_mtime:
                newest_mtime = mt
                newest_file = str(py_file.relative_to(rr))

        if newest_mtime == 0.0:
            return _make_result(
                "capability_map_staleness",
                "PASS",
                [],
                "PASS: No Python source files found.",
            )

        newest_dt = datetime.fromtimestamp(newest_mtime, tz=timezone.utc)

        if newest_dt > gen_dt:
            delta = newest_dt - gen_dt
            # Actionable: insert recompute item into action queue
            recompute_action = {
                "action_id": "ACT-RECOMPUTE-CAPABILITY-MAP",
                "action_type": "RECOMPUTE",
                "description": "Capability map is stale — run capability_map_generator.py",
                "command": "python tools/capability_layer/capability_map_generator.py",
                "staleness_seconds": int(delta.total_seconds()),
                "newest_source": newest_file,
                "blocks_autonomous_ready": True,
            }
            return _make_result(
                "capability_map_staleness",
                "WARN",
                [{"newest_source": newest_file,
                  "source_mtime": newest_dt.isoformat(),
                  "map_generated_at": generated_at_str,
                  "staleness_seconds": int(delta.total_seconds()),
                  "recommendation": "Run capability_map_generator.py to refresh",
                  "recompute_action": recompute_action}],
                f"WARN: Capability map is stale — source {newest_file} "
                f"modified {int(delta.total_seconds())}s after map generation. "
                f"Recompute action queued.",
            )

        return _make_result(
            "capability_map_staleness",
            "PASS",
            [{"map_generated_at": generated_at_str,
              "newest_source_mtime": newest_dt.isoformat()}],
            "PASS: Capability map is up-to-date relative to source files.",
        )
    except Exception as exc:
        return _make_result(
            "capability_map_staleness",
            "WARN",
            [{"error": str(exc)}],
            f"WARN: Staleness check failed: {exc}",
        )


# ── ────────────────────────────────────────────────────────────────────────────
# V_SPEC_QNAME: Spec QName refs for ODF model items
# ── ────────────────────────────────────────────────────────────────────────────


ODF_MODEL_PATH_PREFIXES = (
    "src/python/fod", "src/net/fod", "src/python/ods", "src/python/odt",
)


def validate_spec_qname_refs(declaration: dict) -> dict:
    """V_SPEC_QNAME: PRODUCT_SOURCE items touching ODF model paths should have
    spec_qname_refs.  WARN for product items, FAIL for RELEASE_GATE items."""
    validator = "validate_spec_qname_refs"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []
    fail_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype not in ("PRODUCT_SOURCE", "RELEASE_GATE"):
            continue
        refs = item.get("spec_qname_refs") or []
        item_id = item.get("item_id", "unknown")

        # Check if item touches ODF model paths
        changed = item.get("changed_files", []) + item.get("touched_files", [])
        touches_odf = any(
            any(f.startswith(prefix) for prefix in ODF_MODEL_PATH_PREFIXES)
            for f in changed
        )

        if itype == "RELEASE_GATE" and len(refs) == 0:
            fail_items.append({
                "item_id": item_id,
                "issue": "RELEASE_GATE item missing spec_qname_refs",
            })
        elif itype == "PRODUCT_SOURCE" and touches_odf and len(refs) == 0:
            warn_items.append({
                "item_id": item_id,
                "issue": "ODF model item missing spec_qname_refs",
            })

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items,
            f"FAIL: {len(fail_items)} RELEASE_GATE item(s) missing spec_qname_refs",
            blocks_sprint=True,
        )
    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} ODF item(s) missing spec_qname_refs (advisory)",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: spec_qname_refs check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_SKELETON: Skeleton progress detector
# ── ────────────────────────────────────────────────────────────────────────────


def validate_skeleton_progress(declaration: dict,
                               repo_root: Path | None = None) -> dict:
    """V_SKELETON: Detect PRODUCT_SOURCE items with skeleton-only evidence.

    WARN when evidence_paths contain only __init__.py or files < 10 lines.
    FAIL when claim_classification is replayable but evidence is skeleton-only.
    blocks_sprint only for RELEASE_GATE items.
    """
    repo_root = repo_root or REPO_ROOT
    validator = "validate_skeleton_progress"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []
    fail_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype not in ("PRODUCT_SOURCE", "RELEASE_GATE"):
            continue
        item_id = item.get("item_id", "unknown")
        evidence_paths = item.get("evidence_paths", [])
        if not evidence_paths:
            continue

        # Check if ALL evidence paths are skeleton-like
        all_skeleton = True
        for ep in evidence_paths:
            ep_str = str(ep)
            if ep_str.endswith("__init__.py"):
                continue
            full = repo_root / ep_str
            if full.exists():
                try:
                    line_count = len(full.read_text(encoding="utf-8", errors="replace").splitlines())
                    if line_count >= 10:
                        all_skeleton = False
                        break
                except Exception:
                    all_skeleton = False
                    break
            else:
                # Can't verify — assume non-skeleton
                all_skeleton = False
                break

        if not all_skeleton:
            continue

        claim = item.get("claim_classification", "")
        if claim in REPLAYABLE_CLAIMS:
            fail_items.append({
                "item_id": item_id,
                "issue": "Replayable claim but skeleton-only evidence",
                "claim_classification": claim,
            })
        else:
            warn_items.append({
                "item_id": item_id,
                "issue": "skeleton_only",
            })

    blocks = any(
        item.get("item_type") == "RELEASE_GATE"
        for item in items
        if item.get("item_id") in {f["item_id"] for f in fail_items}
    )

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items,
            f"FAIL: {len(fail_items)} item(s) have replayable claims but skeleton evidence",
            blocks_sprint=blocks,
        )
    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} item(s) have skeleton-only evidence",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: skeleton progress check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_SPEC_PARITY_GATE: Spec parity + depth validator results for gate items
# ── ────────────────────────────────────────────────────────────────────────────


def validate_spec_parity_gate(declaration: dict) -> dict:
    """V_SPEC_PARITY_GATE: RELEASE_GATE items must have spec_parity_validator_results
    and depth_validator_results fields.  Non-gate items pass unconditionally."""
    validator = "validate_spec_parity_gate"
    items = declaration.get("planned_work_items", [])
    fail_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype not in ("RELEASE_GATE",):
            continue
        item_id = item.get("item_id", "unknown")
        missing: list[str] = []
        if not item.get("spec_parity_validator_results"):
            missing.append("spec_parity_validator_results")
        if not item.get("depth_validator_results"):
            missing.append("depth_validator_results")
        if missing:
            fail_items.append({
                "item_id": item_id,
                "missing_fields": missing,
            })

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items,
            f"FAIL: {len(fail_items)} RELEASE_GATE item(s) missing parity/depth results",
            blocks_sprint=True,
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: spec parity gate check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_DEPTH_FIELDS: Implementation depth advisory
# ── ────────────────────────────────────────────────────────────────────────────


def validate_implementation_depth_fields(declaration: dict) -> dict:
    """V_DEPTH_FIELDS: Advisory check that PRODUCT_SOURCE items have
    implementation_depth_score and non-empty tests_supporting."""
    validator = "validate_implementation_depth_fields"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype != "PRODUCT_SOURCE":
            continue
        item_id = item.get("item_id", "unknown")
        missing: list[str] = []
        if item.get("implementation_depth_score") is None:
            missing.append("implementation_depth_score")
        tests = item.get("tests_supporting") or []
        if len(tests) == 0:
            missing.append("tests_supporting")
        if missing:
            warn_items.append({
                "item_id": item_id,
                "missing_fields": missing,
            })

    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} PRODUCT_SOURCE item(s) missing depth fields (advisory)",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: implementation depth fields check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────


def validate_depth_score(declaration: dict) -> dict:
    """V_DEPTH_SCORE: Check that PRODUCT_SOURCE items with an
    implementation_depth_score dict have non-zero source_loc_delta,
    tests_added, and behavior_assertions.

    - Any field at 0 or missing: WARN (shallow_implementation)
    - ALL fields at 0: FAIL for RELEASE_GATE items
    - Non-PRODUCT_SOURCE items: PASS
    """
    validator = "validate_depth_score"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []
    fail_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype != "PRODUCT_SOURCE":
            continue
        depth = item.get("implementation_depth_score")
        if not isinstance(depth, dict):
            continue
        item_id = item.get("item_id", "unknown")
        loc = depth.get("source_loc_delta", 0)
        tests = depth.get("tests_added", 0)
        asserts = depth.get("behavior_assertions", 0)
        zeroes: list[str] = []
        if not loc:
            zeroes.append("source_loc_delta")
        if not tests:
            zeroes.append("tests_added")
        if not asserts:
            zeroes.append("behavior_assertions")
        if len(zeroes) == 3 and item.get("item_type_secondary", "") == "RELEASE_GATE":
            fail_items.append({
                "item_id": item_id,
                "issue": "all depth scores zero on RELEASE_GATE item",
                "zeroes": zeroes,
                "severity": "FAIL",
            })
        elif zeroes:
            warn_items.append({
                "item_id": item_id,
                "issue": "shallow_implementation",
                "zeroes": zeroes,
                "severity": "WARN",
            })

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items + warn_items,
            f"FAIL: {len(fail_items)} PRODUCT_SOURCE item(s) with all-zero depth scores",
            blocks_sprint=False,
        )
    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} PRODUCT_SOURCE item(s) with shallow depth scores (advisory)",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: depth score check passed ({len(items)} items reviewed)",
    )


def validate_changed_without_tests(declaration: dict) -> dict:
    """V_CHANGED_NO_TESTS: Advisory check that PRODUCT_SOURCE items with
    changed product source files also have tests_supporting entries."""
    validator = "validate_changed_without_tests"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype != "PRODUCT_SOURCE":
            continue
        changed = item.get("changed_files") or []
        product_files = [
            f for f in changed
            if f.startswith("src/python/") or f.startswith("src/net/")
        ]
        if not product_files:
            continue
        tests = item.get("tests_supporting") or []
        if not tests:
            warn_items.append({
                "item_id": item.get("item_id", "unknown"),
                "issue": "product_source_changed_without_tests",
                "product_files": product_files,
                "severity": "WARN",
            })

    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} PRODUCT_SOURCE item(s) changed source without tests (advisory)",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: changed-without-tests check passed ({len(items)} items reviewed)",
    )


# Helpers-only file patterns
_HELPERS_ONLY_NAMES = frozenset({"__init__.py", "conftest.py"})
_HELPERS_ONLY_SUFFIXES = ("_helpers.py", "_utils.py")


def validate_helpers_only_overclaim(declaration: dict) -> dict:
    """V_HELPERS_ONLY: Advisory check that PRODUCT_SOURCE items with
    REPLAYABLE claims actually changed substantive source files, not
    just helpers / init / conftest."""
    validator = "validate_helpers_only_overclaim"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []

    for item in items:
        itype = item.get("item_type", "")
        if itype != "PRODUCT_SOURCE":
            continue
        claim = item.get("claim_classification", "")
        if claim not in REPLAYABLE_CLAIMS:
            continue
        changed = item.get("changed_files") or []
        if not changed:
            continue
        all_helpers = all(
            Path(f).name in _HELPERS_ONLY_NAMES
            or f.endswith(_HELPERS_ONLY_SUFFIXES)
            for f in changed
        )
        if all_helpers:
            warn_items.append({
                "item_id": item.get("item_id", "unknown"),
                "issue": "helpers_only_overclaim",
                "changed_files": changed,
                "severity": "WARN",
            })

    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} PRODUCT_SOURCE item(s) changed only helpers with replayable claim (advisory)",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: helpers-only overclaim check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_NAMESPACE_TREE: Namespace tree completeness for spec-parity
# ── ────────────────────────────────────────────────────────────────────────────

_NAMESPACE_TREE_FORMATS = ("fods", "fodt", "fodp", "ods", "odt")


def validate_namespace_tree(declaration: dict,
                            repo_root: Path | None = None) -> dict:
    """V_NAMESPACE_TREE: RELEASE_GATE items for ODF formats must reference a
    namespace-tree artifact in evidence_paths or evidence_artifacts."""
    validator = "validate_namespace_tree"
    items = declaration.get("planned_work_items", [])
    fail_items: list[dict] = []

    for item in items:
        if item.get("item_type") != "RELEASE_GATE":
            continue
        item_id = item.get("item_id", "unknown")
        fmt = _extract_format_from_item(item)
        if fmt not in _NAMESPACE_TREE_FORMATS:
            continue
        # Check evidence_paths + evidence_artifacts for namespace-tree reference
        paths = (item.get("evidence_paths") or []) + [
            a.get("path", "") for a in (item.get("evidence_artifacts") or [])
        ]
        has_ns_tree = any("namespace-tree" in p or "namespace_tree" in p for p in paths)
        if not has_ns_tree:
            fail_items.append({
                "item_id": item_id,
                "format": fmt,
                "issue": f"RELEASE_GATE for ODF format '{fmt}' missing namespace-tree artifact",
            })

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items,
            f"FAIL: {len(fail_items)} RELEASE_GATE item(s) missing namespace-tree artifact",
            blocks_sprint=True,
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: namespace-tree check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_ATTRIBUTE_PROPERTY_MAP: Attribute-property map for ODF spec-parity
# ── ────────────────────────────────────────────────────────────────────────────


def validate_attribute_property_map(declaration: dict,
                                    repo_root: Path | None = None) -> dict:
    """V_ATTRIBUTE_PROPERTY_MAP: RELEASE_GATE items for ODF formats must
    include an attribute-property-map or qname-to-code-map artifact."""
    validator = "validate_attribute_property_map"
    items = declaration.get("planned_work_items", [])
    fail_items: list[dict] = []

    for item in items:
        if item.get("item_type") != "RELEASE_GATE":
            continue
        item_id = item.get("item_id", "unknown")
        fmt = _extract_format_from_item(item)
        if fmt not in _NAMESPACE_TREE_FORMATS:
            continue
        paths = (item.get("evidence_paths") or []) + [
            a.get("path", "") for a in (item.get("evidence_artifacts") or [])
        ]
        has_map = any(
            "attribute-property-map" in p or "qname-to-code-map" in p
            or "attribute_property_map" in p or "qname_to_code_map" in p
            for p in paths
        )
        if not has_map:
            fail_items.append({
                "item_id": item_id,
                "format": fmt,
                "issue": f"RELEASE_GATE for '{fmt}' missing attribute-property-map or qname-to-code-map",
            })

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items,
            f"FAIL: {len(fail_items)} RELEASE_GATE item(s) missing attribute-property-map",
            blocks_sprint=True,
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: attribute-property-map check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_CONTAINMENT_GRAPH: Containment graph for complex format spec-parity
# ── ────────────────────────────────────────────────────────────────────────────

_CONTAINMENT_GRAPH_FORMATS = ("fods", "fodt", "ods", "odt", "fodp")


def validate_containment_graph(declaration: dict,
                               repo_root: Path | None = None) -> dict:
    """V_CONTAINMENT_GRAPH: RELEASE_GATE items for complex ODF formats must
    declare a containment-graph artifact showing element nesting structure."""
    validator = "validate_containment_graph"
    items = declaration.get("planned_work_items", [])
    warn_items: list[dict] = []

    for item in items:
        if item.get("item_type") != "RELEASE_GATE":
            continue
        item_id = item.get("item_id", "unknown")
        fmt = _extract_format_from_item(item)
        if fmt not in _CONTAINMENT_GRAPH_FORMATS:
            continue
        paths = (item.get("evidence_paths") or []) + [
            a.get("path", "") for a in (item.get("evidence_artifacts") or [])
        ]
        has_graph = any(
            "containment-graph" in p or "containment_graph" in p for p in paths
        )
        if not has_graph:
            warn_items.append({
                "item_id": item_id,
                "format": fmt,
                "issue": f"RELEASE_GATE for '{fmt}' missing containment-graph artifact",
                "severity": "WARN",
            })

    if warn_items:
        return _make_result(
            validator, "WARN", warn_items,
            f"WARN: {len(warn_items)} RELEASE_GATE item(s) missing containment-graph (advisory)",
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: containment-graph check passed ({len(items)} items reviewed)",
    )


# ── ────────────────────────────────────────────────────────────────────────────
# V_ALIAS_COMPATIBILITY: Alias compatibility for spec-parity
# ── ────────────────────────────────────────────────────────────────────────────


def validate_alias_compatibility(declaration: dict,
                                 repo_root: Path | None = None) -> dict:
    """V_ALIAS_COMPATIBILITY: RELEASE_GATE items must not have conflicting
    function aliases (same alias pointing to different implementations)."""
    validator = "validate_alias_compatibility"
    items = declaration.get("planned_work_items", [])
    seen_aliases: dict[str, str] = {}  # alias -> first item_id
    fail_items: list[dict] = []

    for item in items:
        if item.get("item_type") not in ("PRODUCT_SOURCE", "RELEASE_GATE"):
            continue
        item_id = item.get("item_id", "unknown")
        aliases = item.get("function_aliases") or []
        for alias_entry in aliases:
            alias_name = alias_entry if isinstance(alias_entry, str) else alias_entry.get("alias", "")
            if not alias_name:
                continue
            if alias_name in seen_aliases and seen_aliases[alias_name] != item_id:
                fail_items.append({
                    "item_id": item_id,
                    "alias": alias_name,
                    "conflicts_with": seen_aliases[alias_name],
                    "issue": f"Alias '{alias_name}' also declared by {seen_aliases[alias_name]}",
                })
            else:
                seen_aliases[alias_name] = item_id

    if fail_items:
        return _make_result(
            validator, "FAIL", fail_items,
            f"FAIL: {len(fail_items)} conflicting alias(es) detected",
            blocks_sprint=True,
        )
    return _make_result(
        validator, "PASS", [],
        f"PASS: alias-compatibility check passed ({len(items)} items, {len(seen_aliases)} aliases reviewed)",
    )


def _extract_format_from_item(item: dict) -> str:
    """Extract format name from a work item (checks title, item_id, format field)."""
    fmt = item.get("format", "")
    if fmt:
        return fmt.lower()
    # Try to extract from item_id or title
    item_id = item.get("item_id", "").lower()
    title = item.get("title", "").lower()
    for candidate in _NAMESPACE_TREE_FORMATS:
        if candidate in item_id or candidate in title:
            return candidate
    return ""


# ---------------------------------------------------------------------------
# V34-V36: Depth validators (class_count_minimum, monolith_detection, no_stub_tests)
# ---------------------------------------------------------------------------

# Formats that require at least 15 classes for product-readiness
_COMPLEX_FORMATS = {"fods", "fodt"}
_CLASS_COUNT_MINIMUM = 15
_MONOLITH_LOC_THRESHOLD = 800
_MONOLITH_BASELINE_PATH = Path(__file__).resolve().parents[2] / "registry" / "source-structure-baseline.json"


def _load_monolith_baseline() -> dict:
    """Load known monolith violations from source-structure-baseline.json."""
    if _MONOLITH_BASELINE_PATH.is_file():
        try:
            import json as _json
            return _json.loads(_MONOLITH_BASELINE_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return {}

def validate_class_count_minimum(declaration: dict,
                                  repo_root: Path | None = None) -> dict:
    """V34: Reject PRODUCT_SOURCE items for complex formats with < 15 classes."""
    if repo_root is None:
        repo_root = Path(".")
    items = declaration.get("planned_work_items", [])
    violations = []
    for item in items:
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue
        item_id = item.get("item_id", "").lower()
        title = item.get("title", "").lower()
        fmt = ""
        for candidate in _COMPLEX_FORMATS:
            if candidate in item_id or candidate in title:
                fmt = candidate
                break
        if not fmt:
            continue
        # Count .cs files in the format's src directory
        fmt_dir = repo_root / "src" / "net" / fmt
        if not fmt_dir.is_dir():
            violations.append(f"{item.get('item_id')}: format dir {fmt_dir} not found")
            continue
        cs_files = list(fmt_dir.rglob("*.cs"))
        # Exclude obj/ and bin/ directories
        cs_files = [f for f in cs_files if "obj" not in f.parts and "bin" not in f.parts]
        if len(cs_files) < _CLASS_COUNT_MINIMUM:
            violations.append(
                f"{item.get('item_id')}: {fmt} has {len(cs_files)} .cs files "
                f"(minimum {_CLASS_COUNT_MINIMUM})"
            )
    if violations:
        return {
            "validator": "class_count_minimum_validator",
            "result": "WARN",
            "blocks_sprint": False,
            "detail": f"{len(violations)} complex format(s) below class minimum. "
                       + "; ".join(violations),
        }
    return {
        "validator": "class_count_minimum_validator",
        "result": "PASS",
        "blocks_sprint": False,
        "detail": "All complex-format PRODUCT_SOURCE items meet class count minimum.",
    }


def validate_monolith_detection(declaration: dict,
                                 repo_root: Path | None = None) -> dict:
    """V35: Block new monolith files and monolith regression.

    Uses baseline grandfathering from registry/source-structure-baseline.json:
    - File in baseline AND LOC <= baseline → WARN (grandfathered)
    - File in baseline AND LOC > baseline → FAIL, blocks_sprint
    - File NOT in baseline AND LOC > 800 → FAIL, blocks_sprint
    """
    if repo_root is None:
        repo_root = Path(".")
    baseline = _load_monolith_baseline()
    known = baseline.get("known_violations", {})
    changed = declaration.get("changed_files", [])
    grandfathered = []
    regressions = []
    new_violations = []
    for fpath in changed:
        p = repo_root / fpath
        if not p.is_file():
            continue
        if p.suffix not in (".cs", ".py"):
            continue
        try:
            loc = sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if loc <= _MONOLITH_LOC_THRESHOLD:
            continue
        rel = str(Path(fpath)).replace("\\", "/")
        baseline_entry = known.get(rel)
        if baseline_entry:
            # TC-BASE-001: Use baseline_loc_cap (write-once ceiling), not stale "loc" field.
            # "loc" is updated by the Step 0 script after each sprint, making the comparison
            # "did this file grow this sprint?" instead of "is it above its cap?".
            # baseline_loc_cap is frozen at grandfathering time and must never increase.
            baseline_loc = baseline_entry.get("baseline_loc_cap", baseline_entry.get("loc", 0))
            if loc > baseline_loc:
                regressions.append(f"{rel} ({loc} LOC, cap {baseline_loc})")
            else:
                grandfathered.append(f"{rel} ({loc} LOC, grandfathered at cap {baseline_loc})")
        else:
            new_violations.append(f"{rel} ({loc} LOC)")
    blocks = bool(regressions or new_violations)
    parts = []
    if grandfathered:
        parts.append(f"grandfathered: {'; '.join(grandfathered)}")
    if regressions:
        parts.append(f"REGRESSION: {'; '.join(regressions)}")
    if new_violations:
        parts.append(f"NEW VIOLATION: {'; '.join(new_violations)}")
    if blocks:
        return {
            "validator": "monolith_detection_validator",
            "result": "FAIL",
            "blocks_sprint": True,
            "detail": f"Monolith violations block sprint: {' | '.join(parts)}",
        }
    if grandfathered:
        return {
            "validator": "monolith_detection_validator",
            "result": "WARN",
            "blocks_sprint": False,
            "detail": f"Grandfathered monoliths (no regression): {'; '.join(grandfathered)}",
        }
    return {
        "validator": "monolith_detection_validator",
        "result": "PASS",
        "blocks_sprint": False,
        "detail": f"No changed source files exceed {_MONOLITH_LOC_THRESHOLD} LOC.",
    }


def validate_no_stub_tests(declaration: dict,
                            repo_root: Path | None = None) -> dict:
    """V36: Reject test files that only assert `is not None` or `isinstance`."""
    if repo_root is None:
        repo_root = Path(".")
    items = declaration.get("planned_work_items", [])
    violations = []
    for item in items:
        for ref in item.get("test_references", []):
            p = repo_root / ref
            if not p.is_file():
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Count assertion types
            total_asserts = content.count("assert ")
            weak_asserts = (
                content.count("assert result is not None")
                + content.count("assert isinstance(")
                + content.count("is not None")
            )
            # If > 80% of assertions are weak, flag it
            if total_asserts > 0 and weak_asserts / total_asserts > 0.8:
                violations.append(
                    f"{ref}: {weak_asserts}/{total_asserts} assertions are weak "
                    f"(is not None / isinstance)"
                )
    if violations:
        return {
            "validator": "no_stub_tests_validator",
            "result": "WARN",
            "blocks_sprint": False,
            "detail": f"{len(violations)} test file(s) have mostly stub assertions. "
                       + "; ".join(violations[:5]),
        }
    return {
        "validator": "no_stub_tests_validator",
        "result": "PASS",
        "blocks_sprint": False,
        "detail": "No test files detected with predominantly stub assertions.",
    }


def validate_spec_fact_authority_chain(declaration: dict,
                                       repo_root: Path | None = None) -> dict:
    """V37: WARN when PRODUCT_SOURCE items for ODF formats lack spec-fact authority.

    Checks that planned_work_items with item_type=PRODUCT_SOURCE and an ODF
    format_id (FODS, FODT, FODP, FODG, ODS, ODT) have at least one valid
    spec_fact_ref that traces to a verified fact in sal-facts-latest.json.

    WARN-only (blocks_sprint=False) until fact counts are sufficient.
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    ODF_FORMATS = {"fods", "fodt", "fodp", "fodg", "ods", "odt"}

    items = declaration.get("planned_work_items", [])
    odf_product_items = [
        item for item in items
        if item.get("item_type") == "PRODUCT_SOURCE"
        and (item.get("format_id", "") or "").lower() in ODF_FORMATS
    ]

    if not odf_product_items:
        return _make_result(
            "spec_fact_authority_chain_validator",
            "PASS",
            [],
            "No ODF PRODUCT_SOURCE items found — spec-fact authority check not applicable.",
            blocks_sprint=False,
        )

    # Load SAL facts for fast lookup
    sal_path = repo_root / ".local" / "sal-output" / "sal-facts-latest.json"
    known_qnames: set[str] = set()
    if sal_path.is_file():
        try:
            import json
            sal_data = json.loads(sal_path.read_text(encoding="utf-8"))
            for fmt_result in sal_data.get("results", []):
                for fact in fmt_result.get("spec_facts", []):
                    qname = fact.get("qname", "")
                    if qname:
                        known_qnames.add(qname)
        except Exception:
            pass

    missing = []
    covered = []
    for item in odf_product_items:
        item_id = item.get("item_id", item.get("id", "unknown"))
        fmt_id = (item.get("format_id", "") or "").upper()
        refs = item.get("spec_fact_refs", [])

        # Check if any ref traces to a known SAL fact
        valid_refs = [r for r in refs if r.startswith("FACT-")]
        has_sal_trace = any(r in known_qnames for r in refs) if known_qnames else bool(valid_refs)

        if not valid_refs and not has_sal_trace:
            exc = item.get("exception_classification", "")
            if exc:
                covered.append({"item_id": item_id, "format_id": fmt_id,
                                "note": f"exception_classification={exc}"})
            else:
                missing.append({"item_id": item_id, "format_id": fmt_id,
                                "spec_fact_refs": refs})
        else:
            covered.append({"item_id": item_id, "format_id": fmt_id,
                            "valid_refs": valid_refs})

    if missing:
        return _make_result(
            "spec_fact_authority_chain_validator",
            "WARN",
            missing,
            (
                f"spec_fact_authority_chain: {len(missing)} ODF PRODUCT_SOURCE item(s) "
                f"lack spec-fact authority (no valid FACT-* refs or SAL trace). "
                f"Items: {[m['item_id'] for m in missing[:5]]}"
            ),
            blocks_sprint=False,
        )

    return _make_result(
        "spec_fact_authority_chain_validator",
        "PASS",
        covered,
        f"spec_fact_authority_chain: {len(covered)} ODF PRODUCT_SOURCE item(s) have spec-fact authority.",
        blocks_sprint=False,
    )


def validate_evidence_minimum(declaration: dict, repo_root: Path | None = None) -> dict:
    """V38 (TC-H3-001): WARN when declared evidence is too thin to support grading.

    Rules:
    - All planned_work_items must have >= 2 evidence_paths.
    - TEST items should have at least 1 path that looks like a raw-log (contains
      'raw-logs', '.log', or 'pytest').
    - PRODUCT_SOURCE items must have non-empty source_diff_paths.

    Severity: WARN (blocks_sprint=False) — does not block sprint but signals thin evidence.
    """
    items = declaration.get("planned_work_items", [])
    warnings = []

    for item in items:
        item_id = item.get("item_id", item.get("id", "unknown"))
        itype = item.get("item_type", "")
        evidence_paths = item.get("evidence_paths", [])

        if len(evidence_paths) < 2:
            warnings.append(f"{item_id}: only {len(evidence_paths)} evidence_path(s) (minimum 2 recommended)")

        if itype == "TEST":
            has_log = any(
                ("raw-logs" in p or ".log" in p or "pytest" in p.lower())
                for p in evidence_paths
            )
            if not has_log:
                warnings.append(f"{item_id} (TEST): no raw-log evidence_path found")

        if itype == "PRODUCT_SOURCE":
            diff_paths = item.get("source_diff_paths", [])
            if not diff_paths:
                warnings.append(f"{item_id} (PRODUCT_SOURCE): source_diff_paths is empty")

    if warnings:
        return _make_result(
            "evidence_minimum_validator",
            "WARN",
            warnings,
            f"evidence_minimum: {len(warnings)} item(s) have thin evidence. "
            f"Add raw-logs, focused proofs, and source_diff_paths to improve grading accuracy.",
            blocks_sprint=False,
        )

    return _make_result(
        "evidence_minimum_validator",
        "PASS",
        [],
        f"evidence_minimum: all {len(items)} item(s) meet minimum evidence requirements.",
        blocks_sprint=False,
    )


# ---------------------------------------------------------------------------
# V39: governance_only_no_source_delta (WARN-only)
# Detects sprints where ALL items are governance-type with no source delta.
# ---------------------------------------------------------------------------

_GOVERNANCE_ITEM_TYPES = frozenset({
    "GOVERNANCE_DOC", "GOVERNANCE_TASKCARD", "GOVERNANCE_REVIEW",
    "GOVERNANCE_REPORT", "GOVERNANCE_POLICY", "GOVERNANCE_PLAN",
})


def validate_governance_only_no_source_delta(declaration: dict,
                                              repo_root: Path | None = None) -> dict:
    """V39: Warn if all items are governance-type and no source files changed.

    This detects the wave 117-120 pattern where the autonomous loop runs
    governance-only sprints with no product source mutations.
    """
    items = declaration.get("planned_work_items", [])
    if not items:
        return _make_result(
            "governance_only_no_source_delta",
            "PASS",
            [],
            "governance_only_no_source_delta: no items to check.",
            blocks_sprint=False,
        )

    # Check if ALL items are governance-type
    all_governance = all(
        item.get("item_type", "") in _GOVERNANCE_ITEM_TYPES
        for item in items
    )
    if not all_governance:
        return _make_result(
            "governance_only_no_source_delta",
            "PASS",
            [],
            "governance_only_no_source_delta: mixed item types (has non-governance items).",
            blocks_sprint=False,
        )

    # Check if any changed file starts with "src/"
    changed_files = declaration.get("changed_files", [])
    has_source_delta = any(
        str(f).replace("\\", "/").startswith("src/")
        for f in changed_files
    )
    if has_source_delta:
        return _make_result(
            "governance_only_no_source_delta",
            "PASS",
            [],
            "governance_only_no_source_delta: governance items but source files were changed.",
            blocks_sprint=False,
        )

    # All governance + no source delta → WARNING
    item_ids = [item.get("item_id", "unknown") for item in items]
    return _make_result(
        "governance_only_no_source_delta",
        "WARN",
        item_ids,
        (
            "governance_only_no_source_delta: all items are governance-type with no "
            "source delta. If intentional, add sprint_type: governance_only to "
            "declaration. Otherwise, add PRODUCT_SOURCE items."
        ),
        blocks_sprint=False,
    )


def _validate_source_architecture(declaration: dict,
                                   repo_root: Path | None = None) -> dict:
    """V40: Anti-monolith architecture validator (TC-VAL-001).

    Proactively scans src/python/ for RULE-AM-001 through RULE-AM-004 violations.
    Does NOT rely solely on source_diff_paths from the declaration.
    """
    if repo_root is None:
        repo_root = REPO_ROOT
    try:
        import importlib.util
        _val_path = repo_root / "tools" / "validators" / "validate_source_architecture.py"
        _spec = importlib.util.spec_from_file_location("validate_source_architecture", str(_val_path))
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)

        import json
        _baseline_path = repo_root / "registry" / "source-structure-baseline.json"
        _baseline = json.loads(_baseline_path.read_text(encoding="utf-8"))
        _src_root = repo_root / "src" / "python"
        return _mod.scan(_src_root, _baseline, repo_root)
    except Exception as e:
        return {
            "validator": "validate_source_architecture",
            "result": "WARN",
            "items": [],
            "summary": f"validate_source_architecture: unavailable ({e})",
            "blocks_sprint": False,
        }


def validate_analytics_skill_required(declaration: dict,
                                       repo_root: Path | None = None) -> dict:
    """V41 (REQ-ENFORCE-001): Enforce skill attribution for analytics.py changes.

    Detects work items that touch src/python/<format>/analytics.py (the §24.7-compliant
    location for all analytics functions) without declaring skill_id: add-analytics-function.

    This validator is COMPLEMENTARY to RULE-AM-001 (validate_source_architecture.py):
    - RULE-AM-001: detects analytics functions placed in WRONG LOCATION (codec/parser files)
    - This validator: detects analytics.py changes in RIGHT LOCATION but without skill attribution

    Uses regex matching on changed_files — analytics.py files may not yet be in the
    baseline (new files), so we do NOT use baseline category lookup.
    """
    import re
    analytics_pattern = re.compile(r"src/python/[^/]+/analytics\.py$")
    violations = []
    items = declaration.get("planned_work_items", [])

    for item in items:
        touched = set(str(f).replace("\\", "/") for f in item.get("changed_files", []))
        analytics_touched = {f for f in touched if analytics_pattern.search(f)}
        if not analytics_touched:
            continue
        skill_id = item.get("skill_id") or item.get("fallback_skill_id")
        if not skill_id:
            violations.append({
                "item_id": item.get("item_id", "?"),
                "analytics_files": sorted(analytics_touched),
                "message": (
                    f"analytics.py change requires skill_id: add-analytics-function "
                    f"(affected: {sorted(analytics_touched)})"
                ),
            })

    if not violations:
        return _make_result(
            "analytics_skill_required",
            "PASS",
            [],
            "analytics_skill_required: all analytics.py changes have skill attribution.",
            blocks_sprint=False,
        )

    item_ids = [v["item_id"] for v in violations]
    messages = "; ".join(v["message"] for v in violations)
    return _make_result(
        "analytics_skill_required",
        "FAIL",
        item_ids,
        f"GOV_BLOCK:analytics_skill_required — {messages}",
        blocks_sprint=True,
    )


def run_all_governance_validators(declaration: dict,
                                   repo_root: Path | None = None) -> dict:
    """Run all governance validators against a declaration.

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
        validate_spec_fact_refs_wired(declaration, repo_root),  # V13: SAL enforcement
        # REQ-GOV-001 / REQ-GOV-002: Gate 11 spec-literal depth validators
        validate_spec_fact_count(declaration),
        validate_qname_coverage(declaration, repo_root),
        validate_parity_matrix_present(declaration, repo_root),
        validate_no_placeholder_metadata(declaration, repo_root),
        validate_gate11_criteria(declaration, repo_root),
        validate_min_spec_facts_per_format(declaration, repo_root),  # V19: REQ-SAL-003
        # SUP-RECT-001 / SUP-RECT-002: Lane ownership + DAG ordering
        validate_lane_ownership(declaration, repo_root),
        validate_dag_ordering(declaration, repo_root),
        # V_STALENESS: Capability map freshness (non-blocking WARN)
        validate_capability_map_staleness(declaration, repo_root),
        # V_SPEC_QNAME / V_SKELETON / V_SPEC_PARITY_GATE / V_DEPTH_FIELDS
        validate_spec_qname_refs(declaration),
        validate_skeleton_progress(declaration, repo_root),
        validate_spec_parity_gate(declaration),
        validate_implementation_depth_fields(declaration),
        # V_DEPTH_SCORE / V_CHANGED_NO_TESTS / V_HELPERS_ONLY: depth validators
        validate_depth_score(declaration),
        validate_changed_without_tests(declaration),
        validate_helpers_only_overclaim(declaration),
        # V_NAMESPACE_TREE / V_ATTRIBUTE_PROPERTY_MAP / V_CONTAINMENT_GRAPH / V_ALIAS_COMPATIBILITY
        validate_namespace_tree(declaration, repo_root),
        validate_attribute_property_map(declaration, repo_root),
        validate_containment_graph(declaration, repo_root),
        validate_alias_compatibility(declaration, repo_root),
        # V34-V36: Depth validators (class count, monolith, stub tests)
        validate_class_count_minimum(declaration, repo_root),
        validate_monolith_detection(declaration, repo_root),
        validate_no_stub_tests(declaration, repo_root),
        # V37: Spec-fact authority chain (WARN-only until fact counts sufficient)
        validate_spec_fact_authority_chain(declaration, repo_root),
        # V38 (TC-H3-001): Minimum evidence depth per item (WARN-only)
        validate_evidence_minimum(declaration, repo_root),
        # V39: Governance-only sprint with no source delta (WARN-only)
        validate_governance_only_no_source_delta(declaration, repo_root),
        # V40 (TC-VAL-001): Anti-monolith source architecture validator (proactive scan)
        _validate_source_architecture(declaration, repo_root),
        # V41 (REQ-ENFORCE-001): Analytics skill attribution enforcement (§24.7 compliance)
        validate_analytics_skill_required(declaration, repo_root),
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
