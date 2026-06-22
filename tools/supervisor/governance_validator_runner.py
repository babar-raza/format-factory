"""governance_validator_runner.py — Runs all governance validators (V1-V49).

Extracted from governance_validators.py to keep that file within its LOC cap.
This module imports validators from governance_validators LAZILY (inside the function
body) to avoid circular import issues when this module is imported directly in a
fresh subprocess.

V43: validate_canonical_registry_entry_exists — registry entry enforcement
V44: validate_facade_delegates_to_spec — compat.py import inspection (WARN-only, upgraded from stub 2026-06-21)
V45: validate_qname_class_names — format-prefixed class name enforcement
V46: validate_skill_transcript_present — skill transcript presence (TC-SKILL-GOV-002, WARN-only)
V47: validate_spec_fact_refs_in_sal_output — spec_fact_refs verified in sal-facts-latest.json (TC-MACH-ARCH-007)
V48: validate_architecture_only_stub_gate — blocks RELEASE_GATE items citing architecture_only stubs (TC-ZS-001, 2026-06-21)
V49: validate_qname_structure — spec/ class files in changed_files must have spec_qname (TC-QNAME-VALIDATORS-001, WARN-only)
"""
from __future__ import annotations

from pathlib import Path


def run_all_governance_validators(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """Run all governance validators (V1-V49) against a declaration.

    Returns a composite result dict:
      {
        "all_pass": bool,
        "blocks_sprint": bool,
        "fail_count": int,
        "warn_count": int,
        "pass_count": int,
        "validators": list[dict],   # one per validator
        "summary": str,
      }
    """
    # Lazy imports — kept inside function to prevent circular import when this
    # module is imported directly in a fresh subprocess (governance_validators
    # re-exports run_all_governance_validators, causing a partial-init cycle at
    # module level).
    from governance_validators import (  # noqa: PLC0415
        _validate_source_architecture,
        validate_alias_compatibility,
        validate_analytics_skill_required,
        validate_attribute_property_map,
        validate_canonical_registry_entry_exists,
        validate_capability_map_staleness,
        validate_changed_without_tests,
        validate_ci_artifacts,
        validate_claim_classification,
        validate_class_count_minimum,
        validate_containment_graph,
        validate_dag_ordering,
        validate_deepening_suspension,
        validate_depth_score,
        validate_evidence_minimum,
        validate_facade_delegates_to_spec,
        validate_gate11_criteria,
        validate_governed_direct_execution,
        validate_governance_only_no_source_delta,
        validate_helpers_only_overclaim,
        validate_idempotency_key_required,
        validate_implementation_depth_fields,
        validate_lane_ownership,
        validate_legacy_backfill,
        validate_manual_ungoverned_rejection,
        validate_min_spec_facts_per_format,
        validate_monolith_detection,
        validate_namespace_tree,
        validate_no_placeholder_metadata,
        validate_no_stub_tests,
        validate_parity_matrix_present,
        validate_qname_coverage,
        validate_replay_recipe_required,
        validate_route_decision_required,
        validate_skeleton_progress,
        validate_source_diff_required,
        validate_source_marker_or_sidecar,
        validate_spec_fact_authority_chain,
        validate_spec_fact_count,
        validate_spec_fact_refs_wired,
        validate_spec_parity_gate,
        validate_spec_qname_refs,
        validate_taskcard_state_transitions,
        validate_execution_method_required,
        validate_qname_class_names,
        validate_skill_transcript_present,
        validate_spec_fact_refs_in_sal_output,
        validate_architecture_only_stub_gate,
        validate_qname_structure,
    )
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
        # V42 (SUSP-001): Arithmetic deepening rotation suspension enforcement
        validate_deepening_suspension(declaration),
        # V43 (TC-VALIDATOR-043): Canonical registry entry enforcement
        validate_canonical_registry_entry_exists(declaration, repo_root),
        # V44 (TC-VALIDATOR-044): Facade delegates to spec (WARN-only in bootstrap)
        validate_facade_delegates_to_spec(declaration, repo_root),
        # V45 (TC-MACH-003): Format-prefixed class names outside Compat/ are blocked
        validate_qname_class_names(declaration, repo_root),
        # V46 (TC-SKILL-GOV-002): PRODUCT_SOURCE items must have linked skill_transcript (WARN-only)
        validate_skill_transcript_present(declaration),
        # V47 (TC-MACH-ARCH-007): spec_fact_refs must resolve to entries in sal-facts-latest.json
        validate_spec_fact_refs_in_sal_output(declaration, repo_root),
        # V48 (TC-ZS-001): RELEASE_GATE items must not cite architecture_only stubs as evidence
        validate_architecture_only_stub_gate(declaration, repo_root),
        # V49 (TC-QNAME-VALIDATORS-001): spec/ class files in changed_files must have spec_qname (WARN-only)
        validate_qname_structure(declaration, repo_root),
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
