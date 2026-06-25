"""guard_001_checker.py — TC-GUARD-001 enforcement with GOVERNANCE_ASSET exemption.

TC-GUARD-001 requires that every PRODUCT_SOURCE and PRODUCT_TEST item has BOTH:
  (a) a gap/capability reference: gap_ledger_ref OR capability_ref
  (b) spec authority citation: spec_fact_refs OR exception_classification

gap_ledger_ref alone is NOT sufficient (SAL-HEAL-A001, 2026-06-25 AND-logic upgrade).

GOVERNANCE_ASSET items are explicitly EXEMPT from this check because they CREATE the
registry/manifest/validator infrastructure that gap-ledger entries will later reference.
They are upstream of the ledger by definition. Blocking them would create an unresolvable
circular dependency.

Exempt item types:
  - GOVERNANCE_ASSET: creates governance infrastructure (registries, validators, manifests)

Not exempt (must have gap reference):
  - PRODUCT_SOURCE: product implementation code
  - PRODUCT_TEST: product test code
  - GOVERNANCE_TASKCARD: taskcards (not infrastructure)

Usage:
    from guard_001_checker import check_guard_001_all
    violations = check_guard_001_all(planned_work_items)
    # violations is a list of item_id strings that are missing gap references
"""

from __future__ import annotations

# Item types that are EXEMPT from TC-GUARD-001 gap-reference requirement.
EXEMPT_ITEM_TYPES: frozenset[str] = frozenset({"GOVERNANCE_ASSET"})

# Item types that MUST have a gap reference.
CHECKED_ITEM_TYPES: frozenset[str] = frozenset({"PRODUCT_SOURCE", "PRODUCT_TEST"})


def is_guard_001_exempt(item: dict) -> bool:
    """Return True if item is exempt from TC-GUARD-001 gap-reference check.

    GOVERNANCE_ASSET items are exempt because they are upstream of the gap ledger.
    All other item types that require checking are NOT exempt.
    """
    return item.get("item_type") in EXEMPT_ITEM_TYPES


def check_guard_001(item: dict) -> dict:
    """Check a single item for TC-GUARD-001 compliance.

    Returns a dict with keys:
      - exempt (bool): True if item is GOVERNANCE_ASSET (exempt from check)
      - violation (bool): True if item is checked AND lacks gap reference
      - reason (str): human-readable explanation
    """
    item_type = item.get("item_type", "")
    if is_guard_001_exempt(item):
        return {
            "exempt": True,
            "violation": False,
            "reason": f"item_type={item_type!r} is GOVERNANCE_ASSET — exempt from gap-reference check",
        }
    if item_type not in CHECKED_ITEM_TYPES:
        # Not GOVERNANCE_ASSET but also not a checked type (e.g., GOVERNANCE_TASKCARD)
        return {
            "exempt": False,
            "violation": False,
            "reason": f"item_type={item_type!r} is not in CHECKED_ITEM_TYPES — not checked by TC-GUARD-001",
        }
    has_ledger_ref = bool(item.get("gap_ledger_ref") or item.get("capability_ref"))
    has_spec_authority = bool(item.get("spec_fact_refs") or item.get("exception_classification"))
    # TC-GUARD-001 AND logic (SAL-HEAL-A001 2026-06-25):
    # Requires BOTH a gap/capability reference AND spec authority (facts or exception).
    # gap_ledger_ref alone is no longer sufficient — spec_fact_refs or exception_classification required.
    has_ref = bool(has_ledger_ref and has_spec_authority)
    if has_ref:
        return {
            "exempt": False,
            "violation": False,
            "reason": "has (gap_ledger_ref or capability_ref) AND (spec_fact_refs or exception_classification)",
        }
    if not has_ledger_ref:
        return {
            "exempt": False,
            "violation": True,
            "reason": (
                f"PRODUCT_SOURCE/TEST item missing gap_ledger_ref and capability_ref "
                f"— item_id={item.get('item_id', '?')!r}"
            ),
        }
    return {
        "exempt": False,
        "violation": True,
        "reason": (
            f"PRODUCT_SOURCE/TEST item has gap_ledger_ref/capability_ref but lacks "
            f"spec_fact_refs and exception_classification — add spec authority citation "
            f"or valid exception_classification — item_id={item.get('item_id', '?')!r}"
        ),
    }


def check_guard_001_all(items: list[dict]) -> list[str]:
    """Check all items for TC-GUARD-001 compliance.

    Returns list of item_id strings for items that are in CHECKED_ITEM_TYPES
    and lack a gap reference. GOVERNANCE_ASSET items are silently skipped (exempt).

    Args:
        items: list of planned_work_items dicts from the evidence declaration

    Returns:
        List of violating item_id strings (empty list = no violations)
    """
    violations: list[str] = []
    for item in items:
        result = check_guard_001(item)
        if result["violation"]:
            violations.append(item.get("item_id", "<unknown>"))
    return violations
