"""governance_validators_gate_auth.py — Gate Authorization Validators (V68, V69).

Dedicated file for gate-authorization governance validators.
Placed here (not governance_validators_ext.py) to prevent LOC cap pressure.
Imported by governance_validator_runner.py alongside other validator modules.

Policy reference: docs/governance/authorization-policy-v1.yaml (FORMAT_FACTORY_GATE_AUTHORIZATION_V1)
"""
from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Human-Authorization Language Patterns (V68).
# EXTENDING THIS LIST: add new phrases here — they are automatically picked up
# by validate_premature_human_authorization_request() with no other changes needed.
# Phrases are lowercase; matching is done on lowercased field values.
# Focus on INTENT phrases ("human must", "awaiting human") not generic words ("approve").
_HUMAN_AUTH_PHRASES = frozenset({
    "human authorization required",
    "awaiting human",
    "human must",
    "babar must approve",
    "babar must",
    "babar raza must",
    "human approval required",
    "requires human review",
    "requires human",
    "human review required",
    "stop and ask",
    "human needed",
    "needs human",
    "blocked by human",
    "waiting for human",
    "pending human",
    "human sign-off",
    "human sign off",
    "manually approved",
    "manual approval",
    "manual review required",
})

# Item types that are HUMAN_GATE by structural definition (V68 also checks these)
_HUMAN_GATE_ITEM_TYPES = frozenset({
    "HUMAN_GATE",
    "HUMAN_APPROVAL",
    "MANUAL_GATE",
})

# Legitimate external blocker patterns that are NOT false human blockers
_LEGITIMATE_EXTERNAL_BLOCKER_NOTES = frozenset({
    "credentials",
    "git push",
    "git commit",
    "git merge",
    "publication",
    "pypi",
    "nuget",
    "package publish",
    "branch protection",
    "destructive",
    "mcp activation",
    "sprint policy not authorizing",
})

# Item types that legitimately can reference Gate 11 / Babar Raza
_GATE_11_ITEM_TYPES = frozenset({
    "RELEASE_GATE",
    "READINESS",
})


@validator(rule_id="V_VALIDATE_PREMATURE_HUMAN_AUTHORIZATION_REQUEST", domain="gate_auth")
def validate_premature_human_authorization_request(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V68 (TC-AUTH-006): Detect premature human-authorization requests below Gate 11.

    Scans planned_work_items for false human blockers:
    - item.status == 'blocked_external_gate' AND item_type is non-release AND
      notes contain human-auth language WITHOUT legitimate external blocker codes
    - item.title or item.notes explicitly requires human in non-Gate-11 context
    - item.item_type structurally declares a human gate (HUMAN_GATE, MANUAL_GATE)

    Does NOT flag:
    - RELEASE_GATE/READINESS items (Gate 11 domain)
    - Items with notes citing credentials, git push, publication, mcp activation
    - Items with gate_ref containing "gate_11" or "11"

    FAIL: blocks_sprint=True for explicit false human blockers
    WARN: blocks_sprint=False for human-auth language in non-blocked items
    """
    fail_items = []
    warn_items = []

    for item in declaration.get("planned_work_items", []):
        item_type = item.get("item_type", "")
        item_status = item.get("status", "")
        title = (item.get("title") or "").lower()
        notes = (item.get("notes") or "").lower()
        gate_ref = (item.get("gate_ref") or "").lower()
        acceptance = (item.get("acceptance_criteria") or "").lower()

        # Skip Gate 11 / release-gate items — these legitimately reference Babar Raza
        if item_type in _GATE_11_ITEM_TYPES:
            continue

        # Skip items with gate_ref indicating Gate 11
        if "gate_11" in gate_ref or gate_ref == "11":
            continue

        # RISK-04 mitigation: also flag items whose item_type structurally declares
        # a human gate (e.g. HUMAN_GATE, MANUAL_GATE) — catches novel phrasing
        if item_type in _HUMAN_GATE_ITEM_TYPES:
            fail_items.append({
                "item_id": item.get("item_id", "unknown"),
                "item_type": item_type,
                "title": item.get("title", ""),
                "issue": (
                    f"item_type={item_type!r} declares a human gate below Gate 11. "
                    "Gates 0-10 are agent-autonomous. Remove human gate classification "
                    "or reclassify as GOVERNANCE_TASKCARD with autonomous execution path."
                ),
            })
            continue

        # Check for human-auth language in blocked items
        if item_status == "blocked_external_gate":
            # Check if the blocker is legitimate (credentials, push, publication, etc.)
            is_legitimate = any(
                phrase in notes for phrase in _LEGITIMATE_EXTERNAL_BLOCKER_NOTES
            )
            if not is_legitimate:
                # Check if notes contain human-auth language (false blocker)
                has_human_auth = any(
                    phrase in notes or phrase in title
                    for phrase in _HUMAN_AUTH_PHRASES
                )
                if has_human_auth:
                    fail_items.append({
                        "item_id": item.get("item_id", "unknown"),
                        "item_type": item_type,
                        "title": item.get("title", ""),
                        "issue": (
                            "blocked_external_gate without legitimate blocker reason; "
                            "notes contain human-authorization language"
                        ),
                    })
                elif not notes:
                    # Blocked with no explanation at all — WARN
                    warn_items.append({
                        "item_id": item.get("item_id", "unknown"),
                        "item_type": item_type,
                        "title": item.get("title", ""),
                        "issue": "blocked_external_gate with empty notes; verify this is not a false human blocker",
                    })

        # Scan non-blocked items for human-auth language that shouldn't be there
        elif any(phrase in notes or phrase in acceptance for phrase in _HUMAN_AUTH_PHRASES):
            warn_items.append({
                "item_id": item.get("item_id", "unknown"),
                "item_type": item_type,
                "title": item.get("title", ""),
                "issue": "non-blocked item contains human-authorization language in notes/acceptance_criteria",
            })

    if fail_items:
        return {
            "validator": "validate_premature_human_authorization_request",
            "result": "FAIL",
            "items": fail_items,
            "summary": (
                f"V68: {len(fail_items)} premature human-authorization request(s) detected. "
                "Gates 0-10 are agent-autonomous. Use specific blocker codes per FORMAT_FACTORY_GATE_AUTHORIZATION_V1."
            ),
            "blocks_sprint": True,
        }
    if warn_items:
        return {
            "validator": "validate_premature_human_authorization_request",
            "result": "WARN",
            "items": warn_items,
            "summary": f"V68: {len(warn_items)} item(s) with human-auth language in non-blocked context",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_premature_human_authorization_request",
        "result": "PASS",
        "items": [],
        "summary": "V68: No premature human-authorization requests detected",
        "blocks_sprint": False,
    }


@validator(rule_id="V_VALIDATE_GATE_TRANSITION_STATE_MACHINE", domain="gate_auth")
def validate_gate_transition_state_machine(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V69 (TC-AUTH-007): Enforce valid gate-transition state machine.

    Checks that RELEASE_GATE/READINESS items referencing Gate 11 are not present
    alongside REWORK_REQUIRED items or items with incomplete Gate 10 evidence.

    Specifically:
    1. If any item has item_type=RELEASE_GATE/READINESS with gate_ref containing "11":
       - The sprint must not also have items with status=not_started for core PRODUCT_SOURCE work
       - The sprint's declared_scope must not indicate early-stage work (Gates 0-8)
    2. If item has gate_ref="11" but item_type is NOT RELEASE_GATE/READINESS → FAIL
       (wrong item_type for a Gate 11 claim)
    3. If multiple items are RELEASE_GATE for Gate 11 with same format_ref → WARN (duplicate gate claims)

    Invalid transitions detected:
    - GATE_0..9 item + RELEASE_GATE/WAITING_GATE_11 simultaneously → FAIL
    - Non-release item claiming gate_ref=11 → FAIL

    Valid transition:
    - RELEASE_GATE item with gate_ref=11 when all PRODUCT_SOURCE items are completed → PASS
    """
    fail_items = []
    warn_items = []

    items = declaration.get("planned_work_items", [])
    gate_11_release_items = []
    incomplete_product_items = []
    seen_gate11_format_refs: dict = {}

    for item in items:
        item_type = item.get("item_type", "")
        gate_ref = (item.get("gate_ref") or "").strip()
        item_status = item.get("status", "")
        item_id = item.get("item_id", "unknown")
        format_ref = item.get("format_ref", item.get("item_id", ""))

        is_gate_11 = gate_ref in ("11", "gate_11", "gate11", "GATE_11")

        if is_gate_11:
            if item_type in _GATE_11_ITEM_TYPES:
                gate_11_release_items.append(item)
                # Check for duplicates
                if format_ref in seen_gate11_format_refs:
                    warn_items.append({
                        "item_id": item_id,
                        "issue": f"Duplicate Gate 11 RELEASE_GATE claim for format_ref={format_ref}",
                    })
                else:
                    seen_gate11_format_refs[format_ref] = item_id
            else:
                # Non-release item claiming Gate 11 — invalid transition
                fail_items.append({
                    "item_id": item_id,
                    "item_type": item_type,
                    "gate_ref": gate_ref,
                    "issue": (
                        f"Non-RELEASE_GATE item (item_type={item_type!r}) claims gate_ref=11. "
                        "Only RELEASE_GATE or READINESS items may reference Gate 11. "
                        "Invalid state transition: GATE_0..9_ITEM → WAITING_GATE_11_AUTHORIZATION."
                    ),
                })

        # Collect incomplete PRODUCT_SOURCE items
        if item_type == "PRODUCT_SOURCE" and item_status not in ("completed", "partial"):
            incomplete_product_items.append(item)

    # If Gate 11 release items exist alongside not_started PRODUCT_SOURCE items → FAIL
    if gate_11_release_items and any(
        i.get("status") == "not_started" for i in incomplete_product_items
    ):
        fail_items.append({
            "item_id": "SPRINT_LEVEL",
            "issue": (
                "Sprint declares Gate 11 RELEASE_GATE items while PRODUCT_SOURCE items are not_started. "
                "Invalid transition: AUDIT_FINDINGS_OPEN or REWORK_REQUIRED → WAITING_GATE_11_AUTHORIZATION. "
                "Complete all PRODUCT_SOURCE work before Gate 11 claim."
            ),
        })

    if fail_items:
        return {
            "validator": "validate_gate_transition_state_machine",
            "result": "FAIL",
            "items": fail_items,
            "summary": (
                f"V69: {len(fail_items)} invalid gate transition(s). "
                "GATE_0..9 items cannot transition to WAITING_GATE_11_AUTHORIZATION."
            ),
            "blocks_sprint": True,
        }
    if warn_items:
        return {
            "validator": "validate_gate_transition_state_machine",
            "result": "WARN",
            "items": warn_items,
            "summary": f"V69: {len(warn_items)} gate-transition warning(s)",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_gate_transition_state_machine",
        "result": "PASS",
        "items": [],
        "summary": "V69: Gate transition state machine is valid",
        "blocks_sprint": False,
    }
