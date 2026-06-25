"""governance_validator_runner.py — Runs all governance validators (V1-V69).

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
V50: validate_forbidden_module_names — blocks *_analytics_extra.py, *_extra.py, *_misc.py creation (MODULE-NAME-001, 2026-06-22)
V51: validate_spec_qname_coverage — repo scan: exported classes must have spec_qname (TC-QHARD-001, WARN-only)
V52: validate_compat_import_integrity — Compat/ facades can resolve spec/ imports (TC-QHARD-002, WARN-only)
V53: validate_spec_authority_class_completeness — registry python_file entries exist on disk (TC-QHARD-003, WARN-only)
V54: validate_cross_lane_product_touching_machinery — product items must not mutate tools/supervisor/ (FF-FORENSIC-A4, WARN-only)
V55: validate_cross_lane_machinery_touching_product — machinery items must not mutate src/ (FF-FORENSIC-A4, WARN-only)
V56: validate_hardening_target_identity — plan hardening must target active native plan (TC-PG-006, FAIL for snoopy fallback; WARN for other wrong targets)
V73: validate_dotnet_spec_qname — .NET Spec/*.cs files must have SpecQName constant with correct registry value (TC-DOTNET-QNAME-001, WARN; FAIL for RELEASE_GATE)
"""
from __future__ import annotations

from pathlib import Path


def run_all_governance_validators(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """Run all governance validators (V1-V69) against a declaration.

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
        validate_py_typed_marker,
        validate_all_exports_declared,
        validate_multi_responsibility_file,
    )
    # V50-V56 imported directly from ext module (governance_validators.py is at LOC cap)
    # V67 imported from dedicated signal validator file (both governance_validators*.py are AT CAP)
    from governance_validators_signal import (  # noqa: PLC0415
        validate_maturity_signal_schema as _validate_maturity_signal_schema,
    )
    # V68 imported from standalone knowledge freshness validator (autonomous_cycle.py is AT CAP)
    from knowledge_freshness_validator import (  # noqa: PLC0415
        validate_knowledge_freshness as _validate_knowledge_freshness,
    )
    from governance_validators_ext import (  # noqa: PLC0415
        validate_forbidden_module_names as _validate_forbidden_module_names,
        validate_spec_qname_coverage as _validate_spec_qname_coverage,
        validate_compat_import_integrity as _validate_compat_import_integrity,
        validate_spec_authority_class_completeness as _validate_spec_authority_class_completeness,
        validate_cross_lane_product_touching_machinery as _validate_cross_lane_product_touching_machinery,
        validate_cross_lane_machinery_touching_product as _validate_cross_lane_machinery_touching_product,
        validate_hardening_target_identity as _validate_hardening_target_identity,
        validate_changed_files_in_ledger as _validate_changed_files_in_ledger,
        validate_expansion_fallback_refs as _validate_expansion_fallback_refs,
        validate_cross_language_parity as _validate_cross_language_parity,
        validate_terminal_closure_completeness as _validate_terminal_closure_completeness,
        validate_error_fallback_safety as _validate_error_fallback_safety,
        validate_spec_fact_refs_density as _validate_spec_fact_refs_density,
        validate_public_api_surface_ratio as _validate_public_api_surface_ratio,
        validate_skill_idempotency_declared as _validate_skill_idempotency_declared,
        validate_sal_authority_chain as _validate_sal_authority_chain,
        validate_lane_dag_ordering as _validate_lane_dag_ordering,
        validate_artifact_identity as _validate_artifact_identity,
        validate_skill_attribution_in_declaration as _validate_skill_attribution,
    )
    # V73 imported from dedicated .NET qname validator file (TC-DOTNET-QNAME-001)
    from governance_validators_dotnet import (  # noqa: PLC0415
        validate_dotnet_spec_qname as _validate_dotnet_spec_qname,
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
        # V50 (MODULE-NAME-001): Forbid analytics-bucket module names (*_analytics_extra, *_extra, *_misc)
        _validate_forbidden_module_names(declaration, repo_root),
        # V51 (TC-QHARD-001): Exported classes must have spec_qname attribute (WARN-only, repo scan)
        _validate_spec_qname_coverage(declaration, repo_root),
        # V52 (TC-QHARD-002): Compat/ facades must resolve spec/ imports (WARN-only, repo scan)
        _validate_compat_import_integrity(declaration, repo_root),
        # V53 (TC-QHARD-003): Registry python_file entries must exist on disk (WARN-only, repo scan)
        _validate_spec_authority_class_completeness(declaration, repo_root),
        # V54 (FF-FORENSIC-A4): Product-track items must not mutate tools/supervisor/ (WARN-only)
        _validate_cross_lane_product_touching_machinery(declaration, repo_root),
        # V55 (FF-FORENSIC-A4): Machinery-track items must not mutate src/ (WARN-only)
        _validate_cross_lane_machinery_touching_product(declaration, repo_root),
        # V56 (TC-PG-006): Plan hardening must target the active native plan, not a fallback (FAIL for snoopy; WARN for others)
        _validate_hardening_target_identity(declaration, repo_root),
        # V57 (TC-VNK-003): src/ changed files must have product-code-change-ledger entries (WARN-only)
        _validate_changed_files_in_ledger(declaration, repo_root),
        # V58 (FALLBACK-REF-001): Detect EXPANSION-FALLBACK-* synthetic gap refs (WARN-only)
        _validate_expansion_fallback_refs(declaration),
        # V59 (TC-MGHEAL-005): Cross-language parity awareness for dual-language formats (WARN-only)
        _validate_cross_language_parity(declaration, repo_root),
        # V60 (TC-TCF-010): RELEASE_GATE items citing plans with open taskcards (WARN-only)
        _validate_terminal_closure_completeness(declaration, repo_root),
        # V61 (TC-TCF-010): Error fallback in write_plan_lock.py must write ITERATION_REQUIRED (FAIL if D6 regression)
        _validate_error_fallback_safety(declaration, repo_root),
        # V62 (TC-MACH-VAL-001): spec_fact_refs density — PRODUCT_SOURCE items need >=1 spec_fact_ref (REWORK_REQUIRED)
        _validate_spec_fact_refs_density(declaration, repo_root),
        # V63 (TC-MACH-SRC-001): Public API surface ratio — WARN when __init__.py has >50 exports with <20% tested
        _validate_public_api_surface_ratio(declaration, repo_root),
        # V64 (TC-GOV-MACH-002): Python packages in changed_files must have py.typed marker (WARN-only)
        validate_py_typed_marker(declaration, repo_root),
        # V65 (TC-GOV-MACH-002): Python packages in changed_files must declare __all__ (WARN-only)
        validate_all_exports_declared(declaration, repo_root),
        # V66 (TC-GOV-MACH-002): Single file mixes parser+model+serializer responsibilities (WARN-only)
        validate_multi_responsibility_file(declaration, repo_root),
        # V67 (TC-AMD-MACH-002): Maturity signal schema validator — FAIL if malformed
        _validate_maturity_signal_schema(declaration, repo_root),
        # V68 (TC-P2-001): Knowledge contract freshness — WARN-only, never blocks sprint
        _validate_knowledge_freshness(declaration, repo_root),
        # V69 (TC-FL-005): Skill idempotency declared — WARN if skill_id has not_specified idempotency
        _validate_skill_idempotency_declared(declaration, repo_root),
        # V70 (TC-FL-006): SAL authority chain — WARN when spec_fact_refs cited for code_introspection formats
        _validate_sal_authority_chain(declaration, repo_root),
        # V71 (TC-FL-007): Lane DAG ordering — system healing (L1-6) before product deepening (L7-13)
        _validate_lane_dag_ordering(declaration, repo_root),
        # V72 (TC-FL-010): Artifact identity — FAIL for RELEASE_GATE missing artifact_id/authority
        _validate_artifact_identity(declaration, repo_root),
        # V-SGF-001 (TC-SGF-002): Skill attribution in declaration — WARN on missing, BLOCK on unregistered
        _validate_skill_attribution(declaration, repo_root),
        # V73 (TC-DOTNET-QNAME-001): .NET Spec/ files must have SpecQName with correct value (WARN; FAIL for RELEASE_GATE)
        _validate_dotnet_spec_qname(declaration, repo_root),
    ]

    # SAL format advisory (non-blocking, Lane E integration)
    try:
        from sal_format_advisory import build_advisory, _load_sal_facts
        sal_results = _load_sal_facts()
        if sal_results:
            advisory = build_advisory(sal_results)
            warnings = advisory.get("warnings", [])
            if warnings:
                results.append({
                    "validator": "sal_format_advisory",
                    "result": "WARN",
                    "items": warnings[:10],
                    "summary": f"SAL advisory: {len(warnings)} format coverage warning(s)",
                    "blocks_sprint": False,
                })
    except Exception:
        pass  # Advisory is non-blocking; silently skip on failure

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
