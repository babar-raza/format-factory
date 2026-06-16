"""
validate_spec_fact_refs.py — spec_fact_refs BLOCKING Enforcement

Enforces the mandatory hard gate for spec_fact_refs on evidence declaration work items.

Per SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-001 (2026-06-07):
  spec_fact_refs is a BLOCKING gate for work items with item_type in:
    PRODUCT_SOURCE, TEST, REQUIREMENT, READINESS, RELEASE_GATE

  A work item is EXEMPT only if exception_classification is explicitly set to:
    investigation_only     — pure investigation/audit, no product artifacts
    sample_only_non_product — sample files only, no production code
    legacy_backfill        — pre-existing code documented retroactively (grace: 2 sprints)
    fallback_authority_approved — explicitly approved fallback with written rationale
    no_public_spec_available — no publicly accessible spec document exists
    schema_authority_available — schema (XSD/DTD) is the primary authority source;
                                  debt-only: blocks READINESS/RELEASE_GATE (no verified facts)

  Authority classification upgrade path:
    schema_authority_available > no_public_spec_available
    (Gnumeric has XSD; use schema_authority_available, not no_public_spec_available)

  Fact ID existence checking (SPEC-AUTHORITY-LAYER-PILOT-CLOSURE-DEBT-REPAIR-001):
    If governed verified-facts files exist in .local/spec-cache/, fact IDs are checked
    against that registry. IDs not found in the registry are rejected.
    Graceful degradation: if no registry files exist, format-only validation applies.

Exit codes (when used as main):
  0 — all items pass enforcement
  1 — one or more items fail enforcement
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

BLOCKING_ITEM_TYPES = frozenset({
    "PRODUCT_SOURCE",
    "TEST",
    "REQUIREMENT",
    "READINESS",
    "RELEASE_GATE",
})

VALID_EXCEPTION_CLASSIFICATIONS = frozenset({
    "investigation_only",
    "sample_only_non_product",
    "legacy_backfill",
    "fallback_authority_approved",
    "no_public_spec_available",
    "schema_authority_available",
})

# Classifications that accept product readiness closure
READINESS_ALLOWED_EXCEPTIONS = frozenset({
    "investigation_only",
    "sample_only_non_product",
    "fallback_authority_approved",  # explicit governance approval
    # NOTE: schema_authority_available intentionally removed from READINESS_ALLOWED
    # (SPEC-AUTHORITY-LAYER-PILOT-CLOSURE-DEBT-REPAIR-001):
    # Schema-only authority does not constitute readiness — verified facts required.
})

# Classifications that are debt/grace only — cannot claim READINESS or RELEASE_GATE
DEBT_ONLY_EXCEPTIONS = frozenset({
    "legacy_backfill",
    "no_public_spec_available",
    "schema_authority_available",  # added: schema authority records debt until facts are verified
})


# ---------------------------------------------------------------------------
# Fact registry — loads governed verified-facts files from .local/spec-cache/
# ---------------------------------------------------------------------------

_FACT_REGISTRY_CACHE: dict | None = None
_FACT_REGISTRY_LOADED: bool = False


def _build_fact_registry(repo_root: Path | None = None) -> dict[str, str]:
    """Load all verified fact IDs from governed verified-facts-review.yaml files.

    Scans .local/spec-cache/*/workbench/verified-facts-review.yaml
    Returns a dict mapping fact_id → verification_status ("verified" | "needs_review" | ...).
    Returns empty dict if no registry files exist (graceful degradation).

    Added: SPEC-AUTHORITY-LAYER-PILOT-CLOSURE-DEBT-REPAIR-001 (2026-06-08)
    """
    if repo_root is None:
        # Derive repo root from this file's location: tools/supervisor/validate_spec_fact_refs.py
        repo_root = Path(__file__).resolve().parent.parent.parent

    cache_dir = repo_root / ".local" / "spec-cache"
    if not cache_dir.exists():
        return {}

    registry: dict[str, str] = {}
    try:
        for facts_file in cache_dir.rglob("verified-facts-review.yaml"):
            try:
                data = yaml.safe_load(facts_file.read_text(encoding="utf-8")) or {}
                for fact in data.get("facts", []):
                    fact_id = fact.get("claim_id") or fact.get("fact_id") or ""
                    if fact_id:
                        provenance = fact.get("provenance", {})
                        status = provenance.get("verification_status", "unknown")
                        registry[fact_id] = status
            except Exception:
                pass
    except Exception:
        pass

    return registry


def get_fact_registry(repo_root: Path | None = None) -> dict[str, str]:
    """Return cached fact registry, loading it on first call."""
    global _FACT_REGISTRY_CACHE, _FACT_REGISTRY_LOADED
    if not _FACT_REGISTRY_LOADED:
        _FACT_REGISTRY_CACHE = _build_fact_registry(repo_root)
        _FACT_REGISTRY_LOADED = True
    return _FACT_REGISTRY_CACHE or {}


def reset_fact_registry_cache() -> None:
    """Reset the fact registry cache (for testing)."""
    global _FACT_REGISTRY_CACHE, _FACT_REGISTRY_LOADED
    _FACT_REGISTRY_CACHE = None
    _FACT_REGISTRY_LOADED = False


# ---------------------------------------------------------------------------
# AI acceleration guard (SPEC-AUTHORITY-LAYER-FAST-OPS-001, Lane 6)
# ---------------------------------------------------------------------------

# Extraction methods that are AI-generated or AI-assisted.
# Facts with these methods CANNOT self-certify as "verified".
# They must be independently verified via deterministic_spec_text_search or
# independent_agent_verifier before reaching "verified" status.
_AI_EXTRACTION_METHODS = frozenset({
    "ai_suggested",
    "ai_candidate",
    "llm_extraction",
    "llm_suggested",
    "ai_assisted",
    "automated_extraction",  # automation without human/deterministic verification
})

# The only verification methods that are considered independent (non-AI-self-certifying)
_INDEPENDENT_VERIFICATION_METHODS = frozenset({
    "independent_agent_verifier",
    "deterministic_spec_text_search",
    "human_reviewed",
    "tier1_section",          # direct section extraction (deterministic)
    "tier1_direct_citation",  # direct line citation from cached spec
})


def validate_ai_fact_guard(facts: list[dict]) -> dict:
    """
    Validate that no AI-generated facts have self-certified as 'verified'.

    AI suggestions must remain candidate_only (needs_review) until independently
    verified via deterministic_spec_text_search or independent_agent_verifier.

    Returns:
        {
            "violations": list of {fact_id, issue, extraction_method, verification_status},
            "total_facts": int,
            "ai_suggested_count": int,
            "ai_self_verified_count": int,
            "compliant": bool,
        }
    """
    violations = []
    ai_suggested_count = 0

    for fact in facts:
        fact_id = fact.get("claim_id") or fact.get("fact_id") or "unknown"
        provenance = fact.get("provenance", {})
        extraction_method = provenance.get("extraction_method", "").lower()
        verification_status = provenance.get("verification_status", "").lower()
        validated_by = provenance.get("validated_by", "").lower()

        is_ai_extracted = any(
            ai_method in extraction_method
            for ai_method in _AI_EXTRACTION_METHODS
        )

        if is_ai_extracted:
            ai_suggested_count += 1

        if is_ai_extracted and verification_status == "verified":
            # Check if validated_by is an independent method
            is_independently_verified = any(
                ind_method in validated_by
                for ind_method in _INDEPENDENT_VERIFICATION_METHODS
            )
            if not is_independently_verified:
                violations.append({
                    "fact_id": fact_id,
                    "issue": (
                        f"AI-generated fact (extraction_method={extraction_method!r}) "
                        f"cannot self-certify as 'verified' without independent validation. "
                        f"validated_by={validated_by!r}. "
                        f"Set verification_status=needs_review until independently verified."
                    ),
                    "extraction_method": extraction_method,
                    "verification_status": verification_status,
                    "validated_by": validated_by,
                })

    return {
        "violations": violations,
        "total_facts": len(facts),
        "ai_suggested_count": ai_suggested_count,
        "ai_self_verified_count": len(violations),
        "compliant": len(violations) == 0,
    }


def validate_spec_cache_ai_guard(repo_root: Path | None = None) -> dict:
    """
    Scan all verified-facts-review.yaml files and check for AI self-verification violations.

    Returns aggregate results across all cached spec files.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent

    cache_dir = repo_root / ".local" / "spec-cache"
    if not cache_dir.exists():
        return {
            "violations": [],
            "files_checked": 0,
            "compliant": True,
        }

    all_violations = []
    files_checked = 0

    for facts_file in cache_dir.rglob("verified-facts-review.yaml"):
        try:
            data = yaml.safe_load(facts_file.read_text(encoding="utf-8")) or {}
            facts = data.get("facts", [])
            result = validate_ai_fact_guard(facts)
            files_checked += 1
            for v in result["violations"]:
                v["source_file"] = str(facts_file)
                all_violations.append(v)
        except Exception:
            pass

    return {
        "violations": all_violations,
        "files_checked": files_checked,
        "compliant": len(all_violations) == 0,
    }


def check_item(item: dict) -> dict:
    """
    Check a single work item for spec_fact_refs compliance.

    Returns:
        {
          "item_id": str,
          "item_type": str,
          "blocking_type": bool,
          "compliant": bool,
          "violation": str or None,
          "grade_impact": str,   # "none", "debt", "reject"
          "detail": str,
        }
    """
    item_id = item.get("item_id", "unknown")
    item_type = item.get("item_type", "").upper()
    status = item.get("status", "")
    spec_fact_refs = item.get("spec_fact_refs", []) or []
    exception_class = item.get("exception_classification", "")
    exception_rationale = item.get("exception_rationale", "")

    is_blocking_type = item_type in BLOCKING_ITEM_TYPES

    # Non-blocking types pass unconditionally
    if not is_blocking_type:
        return {
            "item_id": item_id,
            "item_type": item_type,
            "blocking_type": False,
            "compliant": True,
            "violation": None,
            "grade_impact": "none",
            "detail": f"item_type={item_type!r} is not in blocking types — no enforcement",
        }

    has_refs = bool(spec_fact_refs)
    has_exception = bool(exception_class)

    # Validate fact ID format if present
    if has_refs:
        bad_refs = [r for r in spec_fact_refs if not (
            isinstance(r, str) and r.startswith("FACT-") and len(r) > 6
        )]
        if bad_refs:
            return {
                "item_id": item_id,
                "item_type": item_type,
                "blocking_type": True,
                "compliant": False,
                "violation": f"Invalid spec_fact_ref format: {bad_refs}. Must match FACT-<FORMAT>-<N>",
                "grade_impact": "reject",
                "detail": f"item_type={item_type!r} has malformed spec_fact_refs",
            }

    # Validate fact ID existence in governed registry (Lane 1 — DEBT-004 repair)
    if has_refs:
        registry = get_fact_registry()
        if registry:  # only reject if registry has been populated (graceful degradation)
            unknown_refs = [r for r in spec_fact_refs if r not in registry]
            if unknown_refs:
                return {
                    "item_id": item_id,
                    "item_type": item_type,
                    "blocking_type": True,
                    "compliant": False,
                    "violation": (
                        f"spec_fact_refs contain IDs not found in governed fact registry: "
                        f"{unknown_refs}. Ensure the fact IDs exist in a "
                        f"verified-facts-review.yaml file under .local/spec-cache/."
                    ),
                    "grade_impact": "reject",
                    "detail": f"Unknown fact IDs: {unknown_refs}",
                }

    # Case 1a: check for pending/needs_review refs — authority debt (non-blocking)
    if has_refs:
        pending_refs = [r for r in spec_fact_refs if registry.get(r) in ("pending_verification", "needs_review")]
        if pending_refs:
            verified_refs = [r for r in spec_fact_refs if r not in pending_refs]
            return {
                "item_id": item_id,
                "item_type": item_type,
                "blocking_type": False,
                "compliant": True,
                "violation": None,
                "grade_impact": "debt",
                "detail": (
                    f"{len(pending_refs)} spec_fact_ref(s) have unverified status "
                    f"(pending_verification or needs_review): {pending_refs}. "
                    f"Verified refs: {verified_refs}. "
                    f"Run run_fact_verification.py to promote pending facts to verified."
                ),
            }

    # Case 1b: has valid spec_fact_refs (format OK + registry check passed + all verified) — PASS
    if has_refs:
        return {
            "item_id": item_id,
            "item_type": item_type,
            "blocking_type": True,
            "compliant": True,
            "violation": None,
            "grade_impact": "none",
            "detail": f"spec_fact_refs present: {spec_fact_refs}",
        }

    # Case 2: no refs but no exception — HARD BLOCK
    if not has_exception:
        return {
            "item_id": item_id,
            "item_type": item_type,
            "blocking_type": True,
            "compliant": False,
            "violation": (
                f"item_type={item_type!r} has empty spec_fact_refs and no exception_classification. "
                f"This is a BLOCKING gate. Either populate spec_fact_refs with verified FACT-xxx IDs "
                f"or set exception_classification to one of: {sorted(VALID_EXCEPTION_CLASSIFICATIONS)}"
            ),
            "grade_impact": "reject",
            "detail": "Hard gate violation — no spec authority and no exception",
        }

    # Case 3: exception present — validate it
    if exception_class not in VALID_EXCEPTION_CLASSIFICATIONS:
        return {
            "item_id": item_id,
            "item_type": item_type,
            "blocking_type": True,
            "compliant": False,
            "violation": (
                f"exception_classification={exception_class!r} is not a valid classification. "
                f"Valid values: {sorted(VALID_EXCEPTION_CLASSIFICATIONS)}"
            ),
            "grade_impact": "reject",
            "detail": f"Invalid exception classification: {exception_class!r}",
        }

    # Check that fallback_authority_approved has a rationale
    if exception_class == "fallback_authority_approved" and not exception_rationale:
        return {
            "item_id": item_id,
            "item_type": item_type,
            "blocking_type": True,
            "compliant": False,
            "violation": (
                "exception_classification=fallback_authority_approved requires "
                "exception_rationale to be populated with the approving mechanism and written rationale."
            ),
            "grade_impact": "reject",
            "detail": "fallback_authority_approved without rationale — BLOCKED",
        }

    # Check that debt-only exceptions cannot claim product readiness (READINESS/RELEASE_GATE)
    if exception_class in DEBT_ONLY_EXCEPTIONS and item_type in ("READINESS", "RELEASE_GATE"):
        return {
            "item_id": item_id,
            "item_type": item_type,
            "blocking_type": True,
            "compliant": False,
            "violation": (
                f"exception_classification={exception_class!r} is a debt/grace classification and "
                f"cannot be used with item_type={item_type!r}. Readiness and release gates require "
                "real spec_fact_refs or a readiness-allowed exception."
            ),
            "grade_impact": "reject",
            "detail": f"Debt exception {exception_class!r} cannot gate readiness/release",
        }

    # Check that investigation_only items don't have product source changes
    # (Cannot verify files here — caller may check separately, warn only)
    grade_impact = "debt" if exception_class in DEBT_ONLY_EXCEPTIONS else "none"

    return {
        "item_id": item_id,
        "item_type": item_type,
        "blocking_type": True,
        "compliant": True,
        "violation": None,
        "grade_impact": grade_impact,
        "detail": (
            f"exception_classification={exception_class!r} accepted. "
            f"{'Authority debt recorded.' if grade_impact == 'debt' else 'No debt.'}"
        ),
    }


def validate_declaration_spec_fact_refs(decl: dict) -> dict:
    """
    Run spec_fact_refs enforcement on all work items in a declaration.

    Returns:
        {
            "compliant": bool,
            "errors": [str],      — hard violations (grade_impact=reject)
            "debt_items": [str],  — debt notifications
            "item_results": [dict],
        }
    """
    errors = []
    debt_items = []
    item_results = []

    for item in decl.get("planned_work_items", []):
        result = check_item(item)
        item_results.append(result)
        if not result["compliant"] and result.get("grade_impact") == "reject":
            errors.append(f"{result['item_id']}: {result['violation']}")
        elif result.get("grade_impact") == "debt":
            debt_items.append(f"{result['item_id']}: authority debt ({result['detail']})")

    return {
        "compliant": len(errors) == 0,
        "errors": errors,
        "debt_items": debt_items,
        "item_results": item_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate spec_fact_refs enforcement in an evidence declaration"
    )
    parser.add_argument("--declaration", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    decl = yaml.safe_load(args.declaration.read_text(encoding="utf-8")) or {}
    result = validate_declaration_spec_fact_refs(decl)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["compliant"]:
            print(f"SPEC_FACT_REFS: PASS ({len(result['item_results'])} items checked)")
        else:
            print(f"SPEC_FACT_REFS: FAIL ({len(result['errors'])} violations)")
            for e in result["errors"]:
                print(f"  VIOLATION: {e}")
        if result["debt_items"]:
            for d in result["debt_items"]:
                print(f"  DEBT: {d}")

    return 0 if result["compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
