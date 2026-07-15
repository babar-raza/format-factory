"""governance_validator_runner.py — Runs all governance validators (V1-V138).

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
V74: validate_ledger_continuation_gate — block PRODUCT_SOURCE/PRODUCT_TEST items for formats with continuation_allowed=false in product-deepening-ledger.yaml (TC-PDL-005, FAIL)
V75: validate_dependency_direction — import direction within format packages must follow governed chain (RULE-LIB-003, TC-GH-004, 2026-06-25; WARN existing, FAIL new)
V76: validate_error_handling_hierarchy — format packages must have exceptions.py (RULE-LIB-006, TC-GH-004, 2026-06-25; WARN existing, FAIL new)
V83: validate_primary_layer_classified — PRODUCT_SOURCE items should include primary_layer_id (TC-LP-024, WARN-only)
V84: validate_permanent_layer_plan_exists — if primary_layer_id present, plans/layers/<slug>.md must exist (TC-LP-024, WARN-only)
V85: validate_prework_log_present — PRODUCT_SOURCE items should have a work_log_id in evidence (TC-LP-024, WARN-only)
V86: validate_layer_task_registered — TC-* task_ids in declaration should appear in task-register.yaml (TC-LP-024, WARN-only)
V87: validate_dotnet_constant_return_public_api — public Get* methods returning constants in src/net/ (WARN for PRODUCT_SOURCE; FAIL+blocks for RELEASE_GATE) — GI-FODS-NET-001
V88: validate_dotnet_detached_dictionary_fields — Dictionary fields not wired to XML parse path (WARN-only advisory) — GI-FODS-NET-001
V89: validate_dotnet_missingmethods_filename — *Missing*.cs or *Stub*.cs additions in src/net/ (FAIL+blocks) — GI-FODS-NET-001
V100: validate_suspicious_filenames — dumping-ground filename patterns in product src (FAIL, TC-PQLM-012)
V101: validate_history_identifiers_in_source — sprint/wave/train IDs in source comments (WARN, TC-PQLM-012)
V102: validate_undocumented_public_python_apis — public def without docstring (FAIL new, WARN existing, TC-PQLM-012)
V103: validate_ungoverned_todo_markers — TODO/FIXME/HACK without GAP-*/TC-* ref (WARN, TC-PQLM-012)
V104: validate_constant_return_public_methods — public fn always returning constant (FAIL new, TC-PQLM-012)
V105: validate_getter_without_parser_source — .cs public getter reading _dict field (FAIL, TC-PQLM-012)
V106: validate_setter_without_writer_path — .cs public setter writing _dict only (FAIL, TC-PQLM-012)
V107: validate_test_only_public_apis — public API referenced only in tests (WARN, TC-PQLM-012)
V108: validate_detached_persistent_state — Dictionary<> _field patterns in .cs (FAIL new, TC-PQLM-012)
V109: validate_files_outside_approved_layout — product files outside layout contract (FAIL, TC-PQLM-012)
V110: validate_dotnet_path_canonical — block src/dotnet/ paths in declarations (FAIL)
V111: validate_public_symbol_without_qname_authority — spec/Model classes missing spec_qname (FAIL, TC-ARC-012)
V112: validate_model_type_without_spec_authority — model classes missing spec_qname (FAIL, TC-ARC-012)
V113: validate_nested_concept_on_root_document — root document owning nested-QName methods (FAIL, TC-ARC-012)
V117: validate_dumping_ground_or_catchall_file — catch-all filename detection (FAIL, TC-ARC-012)
V118: validate_sprint_history_identifier_in_source — sprint/wave/train IDs in source (WARN, TC-ARC-012)
V119: validate_promoted_code_changed_without_reopening — PROMOTED_STABLE change without reopen (FAIL, TC-ARC-012)
V120: validate_certification_without_architecture_proof — CERTIFIED without arch audit (FAIL, TC-ARC-012)
V121: validate_missing_public_documentation — public Python fn without docstring (FAIL, TC-ARC-012)
V123: validate_ungoverned_code_marker — TODO/FIXME/HACK without governed reference (WARN, TC-ARC-012)
V124: validate_semantic_stub_constant_return — method body is constant-return stub (FAIL, TC-ARC-012)
V125: validate_new_product_bypassing_architecture_gate — new format without qname plan entry (FAIL, TC-ARC-012)
V126: validate_file_outside_approved_qname_layout — file outside approved QName subdirs (FAIL, TC-ARC-012)
V127: validate_type_outside_approved_qname_hierarchy — class not in QName hierarchy (WARN, TC-ARC-012)
V137: validate_no_stale_installed_packages — stale module dirs in site-packages defeat editable installs (FAIL+blocks for changed formats, TC-CPR-003)
V138: validate_consumer_proof_evidence_exists — consumer-proof-manifest.json must exist with PASS entries (WARN-only, TC-CPR-003)
V168: validate_dotnet_collection_stub_comments — COLLECTION_STUB and TODO(GI-FODS-NET-*) comments in src/net/ (WARN-only, TC-FGSQ-009)
V169: validate_whitelist_expiry — whitelist entries past review_due date FAIL+blocks; within 30 days WARN (TC-FGSQ-006)
V171: validate_lane_contract_exists — declaration lane_id must match .governance/lanes/lane-contracts.yaml (FAIL+blocks, TC-GFB-021)
"""
from __future__ import annotations

import json
import yaml
from pathlib import Path

# TC-CTI-REGISTRY-001: Validator shadow registry support
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SHADOW_REGISTRY_PATH = _REPO_ROOT / ".supervisor" / "validator-shadow-registry.yaml"
SHADOW_LOG_PATH = _REPO_ROOT / ".local" / "supervisor" / "validator-shadow-log.jsonl"


def _load_shadow_registry() -> dict:
    """Return {validator_id: entry} from shadow registry. Returns {} on any error."""
    try:
        if not SHADOW_REGISTRY_PATH.exists():
            return {}
        data = yaml.safe_load(SHADOW_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        entries = data.get("validator_shadow_entries", [])
        return {e["validator_id"]: e for e in entries if "validator_id" in e}
    except Exception:
        return {}  # fail-safe: treat missing/invalid registry as empty


def _write_shadow_log_entry(entry: dict) -> None:
    """Append a shadow observation to the log. Non-fatal on any error."""
    try:
        from datetime import datetime, timezone
        entry.setdefault("ts", datetime.now(timezone.utc).isoformat())
        SHADOW_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SHADOW_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def _apply_shadow_routing(results: list[dict], shadow_registry: dict) -> list[dict]:
    """Neutralize blocks_sprint for shadow-mode validators in post-processing.

    Mutates each result dict in-place (sets blocks_sprint=False for shadow FAIL).
    Writes a log entry per suppression. Returns the list of suppression records.
    """
    suppressions: list[dict] = []
    for result in results:
        vid = result.get("validator") or result.get("validator_id", "")
        if vid in shadow_registry and result.get("result") == "FAIL" and result.get("blocks_sprint"):
            shadow_entry = shadow_registry[vid]
            finding_count = len(result.get("items", result.get("violations", [])))
            suppression = {
                "validator_id": vid,
                "original_result": result["result"],
                "would_have_blocked": True,
                "finding_count": finding_count,
                "registry_entry": shadow_entry,
            }
            suppressions.append(suppression)
            result["blocks_sprint"] = False
            _write_shadow_log_entry({
                "validator_id": vid,
                "result": result["result"],
                "would_have_blocked": True,
                "finding_count": finding_count,
                "mode": shadow_entry.get("mode", "shadow"),
            })
    return suppressions


# RC-004: single source of truth for expected validator count
_EXPECTED_VALIDATOR_COUNT = 221  # 216 base +4 V172-V175 (TC-VWR-007) +1 V224 (TC-GOV-V224-001), 2026-07-15


def get_expected_validator_count() -> int:
    """Return the expected total governance validator count.

    This is the single source of truth (RC-004 from shimmering-rolling-meerkat).
    All tests and callers must import this instead of hardcoding the constant.
    """
    return _EXPECTED_VALIDATOR_COUNT


def run_all_governance_validators(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """Run all governance validators (V1-V127) against a declaration.

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
        validate_cross_lane_product_touching_machinery as _validate_cross_lane_product_touching_machinery,
        validate_cross_lane_machinery_touching_product as _validate_cross_lane_machinery_touching_product,
        validate_hardening_target_identity as _validate_hardening_target_identity,
        validate_changed_files_in_ledger as _validate_changed_files_in_ledger,
        validate_expansion_fallback_refs as _validate_expansion_fallback_refs,
        validate_terminal_closure_completeness as _validate_terminal_closure_completeness,
        validate_error_fallback_safety as _validate_error_fallback_safety,
        validate_public_api_surface_ratio as _validate_public_api_surface_ratio,
        validate_skill_idempotency_declared as _validate_skill_idempotency_declared,
        validate_sal_authority_chain as _validate_sal_authority_chain,
        validate_lane_dag_ordering as _validate_lane_dag_ordering,
        validate_artifact_identity as _validate_artifact_identity,
        validate_skill_attribution_in_declaration as _validate_skill_attribution,
    )
    # V51-V53, V59, V62 imported from spec validator file (TC-GOVBLOCK-SPEC-001)
    from governance_validators_spec import (  # noqa: PLC0415
        validate_spec_qname_coverage as _validate_spec_qname_coverage,
        validate_compat_import_integrity as _validate_compat_import_integrity,
        validate_spec_authority_class_completeness as _validate_spec_authority_class_completeness,
        validate_cross_language_parity as _validate_cross_language_parity,
        validate_spec_fact_refs_density as _validate_spec_fact_refs_density,
    )
    # V74 imported from dedicated ledger gate validator file (TC-PDL-005)
    from governance_validators_ledger import (  # noqa: PLC0415
        validate_ledger_continuation_gate as _validate_ledger_continuation_gate,
    )
    # V73 + V78_AGG + V152 imported from dedicated .NET qname/aggregate/roundtrip validator file
    from governance_validators_dotnet import (  # noqa: PLC0415
        validate_dotnet_spec_qname as _validate_dotnet_spec_qname,
        validate_dotnet_aggregate_loc_cap as _validate_dotnet_aggregate_loc_cap,
        validate_format_roundtrip_coverage as _validate_format_roundtrip_coverage,
    )
    # V153 (TC-SPW-004): Design artifact gate — sprint blocks if src/net/ touched without artifact
    from design_artifact_validator import (  # noqa: PLC0415
        validate_design_artifact_present as _validate_design_artifact_present,
    )
    # V80/V81 (TC-AUTH-006/007): Gate authorization validators — dedicated file (no cap pressure)
    from governance_validators_gate_auth import (  # noqa: PLC0415
        validate_premature_human_authorization_request as _validate_premature_human_auth,
        validate_gate_transition_state_machine as _validate_gate_transition,
    )
    # V75/V76 imported from ext2 (TC-GH-004, 2026-06-25): import direction + error handling hierarchy
    # V77/V78/V79 imported from ext2 (TC-GM-002/003/004, PROD-GOVERNANCE-001): analytics naming, dotnet LOC, healing stall
    from governance_validators_ext2 import (  # noqa: PLC0415
        validate_dependency_direction as _validate_dependency_direction,
        validate_error_handling_hierarchy as _validate_error_handling_hierarchy,
        validate_analytics_naming_enforced as _validate_analytics_naming_enforced,
        validate_dotnet_loc_cap as _validate_dotnet_loc_cap,
        validate_healing_stall_detector as _validate_healing_stall_detector,
        validate_oracle_obligations as _validate_oracle_obligations,
        validate_readme_freshness as _validate_readme_freshness,
        validate_certification_reports_exist as _validate_certification_reports_exist,
        validate_certification_matrix_consistent as _validate_certification_matrix_consistent,
        validate_plans_root_policy as _validate_plans_root_policy,
    )
    # TC-CTI-REGISTRY-001: Load shadow registry for this run.
    shadow_registry = _load_shadow_registry()
    shadow_suppressions: list[dict] = []
    # TC-PGI-042: Track validators that could not run due to import/execution errors.
    _skipped_validators: list[dict] = []
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
    ]
    # V-SGF-002 (TC-SGOV-W3-001): Skill execution receipt presence — WARN-only (EP-004)
    # In separate try/except: sgov file is new; failures must not break the main results list.
    try:
        from governance_validators_sgov import (  # noqa: PLC0415
            validate_skill_receipt_presence as _validate_receipt_presence,
        )
        results.append(_validate_receipt_presence(declaration, repo_root))
    except Exception as _exc_vsgf2:
        _skipped_validators.append({"validators": ["V-SGF-002"], "error": str(_exc_vsgf2)})
    results += [
        # V73 (TC-DOTNET-QNAME-001): .NET Spec/ files must have SpecQName with correct value (WARN; FAIL for RELEASE_GATE)
        _validate_dotnet_spec_qname(declaration, repo_root),
        # V74 (TC-PDL-005): Block PRODUCT_SOURCE/PRODUCT_TEST items for formats with continuation_allowed=false
        _validate_ledger_continuation_gate(declaration, repo_root),
        # V75 (TC-GH-004): Import direction within format packages must follow governed chain (RULE-LIB-003)
        _validate_dependency_direction(declaration, repo_root),
        # V76 (TC-GH-004): Format packages must have exceptions.py (RULE-LIB-006)
        _validate_error_handling_hierarchy(declaration, repo_root),
        # V77 (PROD-GOVERNANCE-001 TC-GM-002): *_document.py must not masquerade as analytics — BLOCK
        _validate_analytics_naming_enforced(declaration, repo_root),
        # V78 (PROD-GOVERNANCE-001 TC-GM-003): .cs files in src/net/ must be ≤800 LOC — BLOCK
        _validate_dotnet_loc_cap(declaration, repo_root),
        # V78_AGG (TC-SPW-001): per-class-aggregate LOC cap for partial classes in src/net/
        _validate_dotnet_aggregate_loc_cap(declaration, repo_root),
        # V152 (TC-SPW-003B): Gate-1 .NET formats must have round-trip test coverage — GOV_BLOCK
        _validate_format_roundtrip_coverage(declaration, repo_root),
        # V153 (TC-SPW-004): Sprint touching src/net/ must have pre-execution design artifact
        _validate_design_artifact_present(declaration, repo_root),
        # V79 (PROD-GOVERNANCE-001 TC-GM-004): WARN when known_violations show zero healing progress
        _validate_healing_stall_detector(declaration, repo_root),
        # V80 (TC-AUTH-006): Premature human-authorization request below Gate 11 — FAIL for false human blockers
        _validate_premature_human_auth(declaration, repo_root),
        # V81 (TC-AUTH-007): Gate transition state machine enforcement — FAIL for invalid Gate 11 transitions
        _validate_gate_transition(declaration, repo_root),
        # V82 (TC-ORC-003, ORACLE-LAYER-HARDENING-001): Oracle obligation registry completeness — WARN on missing
        _validate_oracle_obligations(declaration, repo_root),
        _validate_readme_freshness(declaration, repo_root),
        # V88 (TC-CERT-I-017): Certification report directories exist for all formats — WARN-only
        _validate_certification_reports_exist(declaration, repo_root),
        # V89 (TC-CERT-I-017): Portfolio certification matrix internal consistency — WARN-only
        _validate_certification_matrix_consistent(declaration, repo_root),
        # V90 (FF-PLAN-GOV-002): plans/ root policy — only master-plan.md + master-plan-memory.md
        _validate_plans_root_policy(declaration, repo_root),
    ]

    # V-NEW-001 (SAL-VHIP-001): Capability-to-fact inflation ratio check (WARN only, advisory)
    try:
        from governance_validators_ext import validate_capability_fact_ratio as _vcfr  # noqa: PLC0415
        results.append(_vcfr(declaration, repo_root))
    except Exception:
        pass

    # V-SAL-SCHEMA-001 (TC-LA-008): SAL facts schema validation (WARN only)
    try:
        from governance_validators_sal import validate_sal_facts_schema as _vss  # noqa: PLC0415
        results.append(_vss(declaration, repo_root))
    except Exception:
        pass

    # V-NEW-002 (SAL-HEAL-B001): spec_fact_provenance advisory check (WARN only, never blocks)
    try:
        from governance_validators_sal import validate_spec_fact_provenance_advisory as _vp  # noqa: PLC0415
        results.append(_vp(declaration, repo_root))
    except Exception:
        pass

    # V83-V86 (TC-LP-024): Layer control plane governance validators (WARN-only)
    try:
        from governance_validators_layers import (  # noqa: PLC0415
            validate_primary_layer_classified as _v83,
            validate_permanent_layer_plan_exists as _v84,
            validate_prework_log_present as _v85,
            validate_layer_task_registered as _v86,
        )
        results.extend([
            _v83(declaration, repo_root),  # V83
            _v84(declaration, repo_root),  # V84
            _v85(declaration, repo_root),  # V85
            _v86(declaration, repo_root),  # V86
        ])
    except Exception as _exc_v83:
        _skipped_validators.append({"validators": ["V83", "V84", "V85", "V86"], "error": str(_exc_v83)})

    # V-TCF-001/002/003 (TC-TCF-007): Terminal closure governance validators
    # V-TCF-001: FAIL on open taskcards at terminal claim (LIFECYCLE_HARDENING/MACHINERY_HARDENING)
    # V-TCF-002: WARN on missing terminal_closure_record.json evidence artifact
    # V-TCF-003: WARN on premature closure trigger patterns (queue exhaustion, iteration limit)
    try:
        from terminal_closure_validators import (  # noqa: PLC0415
            validate_no_open_taskcards_at_terminal as _vtcf1,
            validate_terminal_closure_has_contract as _vtcf2,
            validate_no_premature_closure_triggers as _vtcf3,
        )
        results.extend([
            _vtcf1(declaration, repo_root),  # V-TCF-001
            _vtcf2(declaration, repo_root),  # V-TCF-002
            _vtcf3(declaration, repo_root),  # V-TCF-003
        ])
    except Exception as _exc_vtcf:
        _skipped_validators.append({"validators": ["V-TCF-001", "V-TCF-002", "V-TCF-003"], "error": str(_exc_vtcf)})

    # V91 (TC-ROOT-005): Root structure architecture governance (FAIL for unregistered dirs, WARN for missing READMEs)
    try:
        from governance_validators_root_struct import (  # noqa: PLC0415
            validate_root_structure as _validate_root_structure,
        )
        results.append(_validate_root_structure(declaration, repo_root))
    except Exception as _exc_v91:
        _skipped_validators.append({"validators": ["V91"], "error": str(_exc_v91)})

    # V92-V99 (TC-PB-009, FF-PLAYBOOK-SYSTEM-001): Playbook governance drift guards (WARN-only)
    try:
        from governance_validators_ext2 import (  # noqa: PLC0415
            validate_playbook_registry_entries as _v92,
            validate_playbook_has_version as _v93,
            validate_playbook_has_owner as _v94,
            validate_playbook_has_evidence_contract as _v95,
            validate_playbook_has_rollback as _v96,
            validate_playbook_not_overriding_gate as _v97,
            validate_playbook_has_no_deprecated_paths as _v98,
            validate_playbook_coverage_report_current as _v99,
        )
        results.extend([
            _v92(declaration, repo_root), _v93(declaration, repo_root),
            _v94(declaration, repo_root), _v95(declaration, repo_root),
            _v96(declaration, repo_root), _v97(declaration, repo_root),
            _v98(declaration, repo_root), _v99(declaration, repo_root),
        ])
    except Exception as _exc_v92:
        _skipped_validators.append({"validators": ["V92", "V93", "V94", "V95", "V96", "V97", "V98", "V99"], "error": str(_exc_v92)})

    # V87-V89 (GI-FODS-NET-001): .NET semantic stub validators
    # V168 (TC-FGSQ-009): COLLECTION_STUB / TODO(GI-FODS-NET-*) comment detector
    # V169 (TC-FGSQ-006): Whitelist entry expiry governance
    try:
        from governance_validators_dotnet_semantic import (  # noqa: PLC0415
            validate_dotnet_constant_return_public_api as _v87,
            validate_dotnet_detached_dictionary_fields as _v88,
            validate_dotnet_missingmethods_filename as _v89,
            validate_dotnet_collection_stub_comments as _v168,
            validate_whitelist_expiry as _v169,
        )
        results.extend([
            _v87(declaration, repo_root),  # V87
            _v88(declaration, repo_root),  # V88
            _v89(declaration, repo_root),  # V89
            _v168(declaration, repo_root),  # V168
            _v169(declaration, repo_root),  # V169
        ])
    except Exception as _exc_v87:
        _skipped_validators.append({"validators": ["V87", "V88", "V89", "V168", "V169"], "error": str(_exc_v87)})

    # V100-V109 (TC-PQLM-012): Product file layout + code quality validators
    # Note: ext3 uses {validator_id, status, blocks_sprint} schema; normalize to {validator, result, blocks_sprint}
    def _norm_ext3(r: dict) -> dict:
        """Normalize ext3 validator output to standard runner schema."""
        return {
            "validator": r.get("validator_id", "ext3_validator"),
            "result": r.get("status", "PASS"),
            "blocks_sprint": r.get("blocks_sprint", False),
            "summary": r.get("summary", ""),
            **{k: v for k, v in r.items() if k not in {"validator_id", "status"}},
        }

    try:
        from governance_validators_ext3 import (  # noqa: PLC0415
            validate_suspicious_filenames as _v100,
            validate_history_identifiers_in_source as _v101,
            validate_undocumented_public_python_apis as _v102,
            validate_ungoverned_todo_markers as _v103,
            validate_constant_return_public_methods as _v104,
            validate_getter_without_parser_source as _v105,
            validate_setter_without_writer_path as _v106,
            validate_test_only_public_apis as _v107,
            validate_detached_persistent_state as _v108,
            validate_files_outside_approved_layout as _v109,
        )
        results.extend([
            _norm_ext3(_v100(declaration, repo_root)),  # V100: suspicious filenames (blocking)
            _norm_ext3(_v101(declaration, repo_root)),  # V101: history identifiers in source (warn)
            _norm_ext3(_v102(declaration, repo_root)),  # V102: undocumented public Python APIs (blocking for new)
            _norm_ext3(_v103(declaration, repo_root)),  # V103: ungoverned TODO markers (warn)
            _norm_ext3(_v104(declaration, repo_root)),  # V104: constant-return public methods (blocking for new)
            _norm_ext3(_v105(declaration, repo_root)),  # V105: getter without parser source (blocking for new)
            _norm_ext3(_v106(declaration, repo_root)),  # V106: setter without writer path (blocking for new)
            _norm_ext3(_v107(declaration, repo_root)),  # V107: test-only public APIs (warn)
            _norm_ext3(_v108(declaration, repo_root)),  # V108: detached persistent state dict (blocking for new)
            _norm_ext3(_v109(declaration, repo_root)),  # V109: files outside approved layout (blocking for new)
        ])
    except Exception as _exc_v100:
        _skipped_validators.append({"validators": ["V100", "V101", "V102", "V103", "V104", "V105", "V106", "V107", "V108", "V109"], "error": str(_exc_v100)})

    # V110: dotnet-path-canonical — block src/dotnet/ product paths in declarations
    try:
        from governance_validators_path import (  # noqa: PLC0415
            validate_dotnet_path_canonical as _v110,
        )

        def _norm_path(r: dict) -> dict:
            return {
                "validator": r.get("rule", "dotnet-path-canonical"),
                "result": r.get("status", "PASS"),
                "blocks_sprint": r.get("blocks_sprint", False),
                "violations": r.get("violations", []),
                "summary": r.get("summary", ""),
            }

        results.append(_norm_path(_v110(declaration, repo_root)))
    except Exception as _exc_v110:
        _skipped_validators.append({"validators": ["V110"], "error": str(_exc_v110)})

    # V111-V127 (TC-ARC-012/CQGA-014): Architecture QName validators
    # These validators operate on individual product source files (not the declaration object).
    # The runner iterates over changed_files and runs each file-based validator.
    try:
        from governance_validators_ext4 import (  # noqa: PLC0415
            validate_public_symbol_without_qname_authority as _v111,
            validate_model_type_without_spec_authority as _v112,
            validate_nested_concept_on_root_document as _v113,
            validate_dumping_ground_or_catchall_file as _v117,
            validate_sprint_history_identifier_in_source as _v118,
            validate_promoted_code_changed_without_reopening as _v119,
            validate_certification_without_architecture_proof as _v120,
            validate_missing_public_documentation as _v121,
            validate_ungoverned_code_marker as _v123,
            validate_semantic_stub_constant_return as _v124,
            validate_new_product_bypassing_architecture_gate as _v125,
            validate_file_outside_approved_qname_layout as _v126,
            validate_type_outside_approved_qname_hierarchy as _v127,
        )

        def _norm_ext4_file(r: dict) -> dict:
            """Normalize ext4 per-file validator output to standard runner schema."""
            passed = r.get("passed", True)
            violations = r.get("violations", [])
            vid = r.get("validator_id", "ext4_validator")
            name = r.get("validator_name", "ext4_check")
            # V118, V123, V127 are WARN-only; others block on new violations
            warn_only = vid in ("V118", "V123", "V127")
            return {
                "validator": vid,
                "result": "PASS" if passed else ("WARN" if warn_only else "FAIL"),
                "blocks_sprint": (not passed) and (not warn_only),
                "violations": violations,
                "summary": f"{vid}: {'passed' if passed else str(len(violations)) + ' violation(s)'}",
            }

        # Context-level validators — each wrapped separately so one failure doesn't kill the rest
        # TC-CQGA-FIX-001 (2026-07-08): fixed wrong (declaration, repo_root) calls
        _repo2 = repo_root or Path(".")

        # V119: promoted code changed without reopening
        try:
            _promo_path = _repo2 / "registry" / "promotion-ledger.yaml"
            _promo_data: dict = {}
            if _promo_path.exists():
                import yaml as _yaml_v119
                _raw_promo = _yaml_v119.safe_load(_promo_path.read_text(encoding="utf-8"))
                if isinstance(_raw_promo, dict):
                    _promo_data = _raw_promo
                    # Ledger uses 'entries'; V119 expects 'promotion_records'
                    if "entries" in _promo_data and "promotion_records" not in _promo_data:
                        _promo_data["promotion_records"] = _promo_data["entries"]
            results.append(_norm_ext4_file(
                _v119(declaration.get("changed_files", []), _promo_data)
            ))
        except Exception as _exc_v119c:
            results.append({"validator": "V119", "result": "WARN", "blocks_sprint": False,
                            "violations": [], "summary": f"V119: skipped — {_exc_v119c}"})

        # V120: certification without architecture proof
        try:
            results.append(_norm_ext4_file(
                _v120(
                    declaration.get("certification_status", ""),
                    declaration.get("architecture_classification", ""),
                    declaration.get("format_id", ""),
                )
            ))
        except Exception as _exc_v120c:
            results.append({"validator": "V120", "result": "WARN", "blocks_sprint": False,
                            "violations": [], "summary": f"V120: skipped — {_exc_v120c}"})

        # V125: new product bypassing architecture gate
        # V126: file outside approved QName layout (per-file — appended in the file loop below)
        _org_plan_path = _repo2 / "registry" / "qname-code-organization-plan.yaml"
        _org_entries: list = []
        try:
            if _org_plan_path.exists():
                import yaml as _yaml_org
                _org_raw = _yaml_org.safe_load(_org_plan_path.read_text(encoding="utf-8"))
                if isinstance(_org_raw, dict):
                    _org_entries = _org_raw.get("entries", _org_raw.get("formats", []))
        except Exception:
            pass
        if _org_entries:
            try:
                results.append(_norm_ext4_file(
                    _v125(declaration.get("format_id", ""), _org_entries)
                ))
            except Exception as _exc_v125c:
                results.append({"validator": "V125", "result": "WARN", "blocks_sprint": False,
                                "violations": [], "summary": f"V125: skipped — {_exc_v125c}"})
        else:
            # Skip V125 when qname-code-organization-plan.yaml is absent — empty entries
            # would falsely FAIL every declaration regardless of format_id
            results.append({"validator": "V125", "result": "PASS", "blocks_sprint": False,
                            "violations": [], "summary": "V125: skipped — qname-code-organization-plan.yaml not found"})

        # File-level validators (run against each changed product source file)
        changed_files = declaration.get("changed_files", [])
        _repo = repo_root or Path(".")
        for cf in changed_files:
            cf_path = _repo / cf if not Path(cf).is_absolute() else Path(cf)
            if not (
                ("src/python" in cf or "src/net" in cf)
                and cf_path.suffix in (".py", ".cs")
            ):
                continue
            try:
                text = cf_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            file_str = str(cf_path)
            for fn, vid_label in [
                (_v111, "V111"), (_v112, "V112"), (_v113, "V113"),
                (_v121, "V121"), (_v123, "V123"), (_v124, "V124"),
                (_v127, "V127"),
            ]:
                try:
                    r = fn(text, file_str)
                    results.append(_norm_ext4_file(r))
                except Exception:
                    pass
            # V117 and V118 take (source_text, file_path) too
            for fn in (_v117, _v118):
                try:
                    r = fn(text, file_str)
                    results.append(_norm_ext4_file(r))
                except Exception:
                    pass
            # V126: file outside approved QName layout (per-file)
            if _org_entries:
                try:
                    results.append(_norm_ext4_file(_v126(file_str, _org_entries)))
                except Exception:
                    pass
    except Exception as _exc_v111:
        _skipped_validators.append({"validators": ["V111", "V112", "V113", "V117", "V118", "V119", "V120", "V121", "V123", "V124", "V125", "V126", "V127"], "error": str(_exc_v111)})

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

    # V130-V133 (PQLM-GOV-001, TC-VAL-002): Found-issue lifecycle + proactive LOC scan
    try:
        from governance_validators_found_issue import (  # noqa: PLC0415
            validate_dotnet_loc_cap_static as _v130,
            validate_found_issue_disposition as _v131,
            validate_found_issue_escalation as _v132,
            validate_found_issue_invalid_disposition as _v133,
        )
        results.append(_v130(declaration, repo_root))
        results.append(_v131(declaration))
        results.append(_v132(declaration))
        results.append(_v133(declaration))
    except Exception as _exc_v130:
        _skipped_validators.append({"validators": ["V130", "V131", "V132", "V133"], "error": str(_exc_v130)})

    # V134-V136 (MA-SYSTEM-WIDE-2026-07-04, playful-swimming-stearns): Output escaping quality gates
    try:
        from governance_validators_output_quality import (  # noqa: PLC0415
            validate_no_manual_json_escaping_in_dotnet as _v134,
            validate_html_escaping_in_dotnet as _v135,
            validate_html_escaping_in_python as _v136,
        )
        results.append(_v134(declaration, repo_root))
        results.append(_v135(declaration, repo_root))
        results.append(_v136(declaration, repo_root))
    except Exception as _exc_v134:
        _skipped_validators.append({"validators": ["V134", "V135", "V136"], "error": str(_exc_v134)})

    # V137-V138 (TC-CPR-003, sparkling-waddling-narwhal): Consumer proof integrity gates
    # V137: stale installed packages (editable install defeated by coexisting site-packages dir) — FAIL/blocks
    # V138: consumer proof execution evidence must exist — WARN-only
    try:
        from governance_validators_consumer_proof import (  # noqa: PLC0415
            validate_no_stale_installed_packages as _v137,
            validate_consumer_proof_evidence_exists as _v138,
        )
        results.append(_v137(declaration, repo_root))
        results.append(_v138(declaration, repo_root))
    except Exception as _exc_v137:
        # TC-PGI-042: Record skipped validators instead of silent pass
        _skipped_validators.append({"validators": ["V137", "V138"], "error": str(_exc_v137)})

    # V139-V142 (FOUND-ISSUE-MVP-001, 2026-07-04): Register-level found-issue ownership validators
    # V139: found_issue_register_present — WARN when tests fail but register is empty
    # V140: issue_accounting_reconciles  — FAIL when register has unknown status
    # V141: no_prose_only_findings       — WARN when dismissal prose in declaration
    # V142: invalid_ownership_disposition — FAIL when invalid disposal in register
    try:
        from governance_validators_found_issue import (  # noqa: PLC0415
            validate_found_issue_register_present as _v139,
            validate_issue_accounting_reconciles as _v140,
            validate_no_prose_only_findings as _v141,
            validate_invalid_ownership_disposition as _v142,
        )
        results.append(_v139(declaration, repo_root))
        results.append(_v140(declaration, repo_root))
        results.append(_v141(declaration))
        results.append(_v142(declaration, repo_root))
    except Exception as _exc_v139:
        _skipped_validators.append({"validators": ["V139", "V140", "V141", "V142"], "error": str(_exc_v139)})

    # V143 (FF-XPLAN-001 W3-001): Oracle depth minimum validator
    # WARN for formats with all-D0 oracle evidence (no property comparison)
    try:
        from governance_validators_oracle import (  # noqa: PLC0415
            validate_oracle_depth_minimum as _v143,
        )
        results.append(_v143(declaration, repo_root))
    except Exception as _exc_v143:
        _skipped_validators.append({"validators": ["V143"], "error": str(_exc_v143)})

    # V144 (PYREL-001, 2026-07-06): Gate 10 status consistency validator
    # FAIL/blocks when gate_10.status contains non-standard values in format-registry.yaml
    try:
        from governance_validators_release import (  # noqa: PLC0415
            validate_gate10_status_consistency as _v144,
        )
        results.append(_v144(declaration, repo_root))
    except Exception as _exc_v144:
        _skipped_validators.append({"validators": ["V144"], "error": str(_exc_v144)})

    # V145 (TC-MOR-C5, 2026-07-08): Overdue maintenance obligation warnings
    # WARN only (blocks_sprint=False) — overdue maintenance is advisory, not a sprint blocker.
    try:
        from governance_validators_ext4 import (  # noqa: PLC0415
            validate_maintenance_obligations_current as _v145,
        )
        results.append(_v145(declaration, repo_root))
    except Exception as _exc_v145:
        _skipped_validators.append({"validators": ["V145"], "error": str(_exc_v145)})

    # V149 (TC-PFF-R1, 2026-07-09): Stub enforcement via no_stub_scan.py
    # blocks_sprint=True for PRODUCT_SOURCE/RELEASE_GATE items with violations.
    try:
        from governance_validators_ext4 import (  # noqa: PLC0415
            validate_source_stubs as _v149,
        )
        results.append(_v149(declaration, repo_root))
    except Exception as _exc_v149:
        _skipped_validators.append({"validators": ["V149"], "error": str(_exc_v149)})

    # V171 (TC-GFB-021, 2026-07-11): Lane contract existence validator
    # WARN if lane-contracts.yaml missing; FAIL+blocks if declared lane_id is invalid.
    try:
        from governance_validators_ext4 import (  # noqa: PLC0415
            validate_lane_contract_exists as _v171,
        )
        results.append(_v171(declaration, repo_root))
    except Exception as _exc_v171:
        _skipped_validators.append({"validators": ["V171"], "error": str(_exc_v171)})

    # V176-V181 (TC-OCRD-C6, 2026-07-12): Control layer governance validators
    try:
        from governance_validators_control_layer import (  # noqa: PLC0415
            validate_evidence_paths_resolve as _v176,
            validate_receipt_claimed_before_closure as _v177,
            validate_no_quarantined_plan_source as _v178,
            validate_contradiction_signal_checked as _v179,
            validate_gap_not_exhausted as _v180,
            validate_sync_report_fresh as _v181,
        )
        for _vfn, _vid in [
            (_v176, "V176"), (_v177, "V177"), (_v178, "V178"),
            (_v179, "V179"), (_v180, "V180"), (_v181, "V181"),
        ]:
            try:
                results.append(_vfn(declaration, repo_root))
            except Exception as _exc_vn:
                _skipped_validators.append({"validators": [_vid], "error": str(_exc_vn)})
    except Exception as _exc_v176_block:
        _skipped_validators.append({"validators": ["V176", "V177", "V178", "V179", "V180", "V181"],
                                     "error": str(_exc_v176_block)})

    # TC-FIOP-005 (2026-07-12): Section-21 found-issue validators
    try:
        from governance_validators_found_issue import (  # noqa: PLC0415
            validate_found_issue_task_closure_unaccounted as _vfi_tc,
            validate_found_issue_no_deleted_test_without_analysis as _vfi_nd,
            validate_found_issue_downstream_patch_while_upstream_defective as _vfi_dp,
            validate_found_issue_closure_without_verification as _vfi_cv,
            validate_found_issue_untaskcarded_in_final_report as _vfi_ur,
            validate_found_issue_no_fixture_edit_without_authority as _vfi_fx,
        )
        for _vfn, _vid in [
            (_vfi_tc, "V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED"),
            (_vfi_nd, "V_VALIDATE_FI_NO_DELETED_TEST"),
            (_vfi_dp, "V_VALIDATE_FI_DOWNSTREAM_PATCH"),
            (_vfi_cv, "V_VALIDATE_FI_CLOSURE_NO_VERIFY"),
            (_vfi_ur, "V_VALIDATE_FI_UNTASKCARDED_REPORT"),
            (_vfi_fx, "V_VALIDATE_FI_FIXTURE_EDIT"),
        ]:
            try:
                results.append(_vfn(declaration, repo_root))
            except Exception as _exc_vn:
                _skipped_validators.append({"validators": [_vid], "error": str(_exc_vn)})
    except Exception as _exc_vfi_block:
        _skipped_validators.append({
            "validators": ["V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED", "V_VALIDATE_FI_NO_DELETED_TEST",
                           "V_VALIDATE_FI_DOWNSTREAM_PATCH", "V_VALIDATE_FI_CLOSURE_NO_VERIFY",
                           "V_VALIDATE_FI_UNTASKCARDED_REPORT", "V_VALIDATE_FI_FIXTURE_EDIT"],
            "error": str(_exc_vfi_block)})

    # V_VALIDATE_WEAK_TEST_ASSERTIONS (TC-INT-003, 2026-07-13): Detect sole-trivial-assertion
    # test functions. WARN-only; grace-exempt via reports/drivers/backfill-gaps.yaml.
    try:
        from governance_validators_ext4 import (  # noqa: PLC0415
            validate_weak_test_assertions as _v_weak,
        )
        results.append(_v_weak(declaration, repo_root))
    except Exception as _exc_v_weak:
        _skipped_validators.append({"validators": ["V_VALIDATE_WEAK_TEST_ASSERTIONS"], "error": str(_exc_v_weak)})

    # V183-V186 (TC-ACP-015, 2026-07-13): Agent parity drift-prevention validators
    try:
        from governance_validators_agent_parity import (  # noqa: PLC0415
            validate_agent_opt_in_not_default as _v183,
            validate_kilo_column_in_registry as _v184,
            validate_canonical_contract_integrity as _v185,
            validate_agent_bundles_current as _v186,
        )
        results.extend([
            _v183(declaration, repo_root),  # V183: opt-in guard (FAIL on regression)
            _v184(declaration, repo_root),  # V184: kilo column in registry (WARN)
            _v185(declaration, repo_root),  # V185: contract integrity (FAIL on truncation)
            _v186(declaration, repo_root),  # V186: bundle freshness (WARN)
        ])
    except Exception as _exc_v183:
        _skipped_validators.append({"validators": ["V183", "V184", "V185", "V186"], "error": str(_exc_v183)})

    # V_CERT_01-V_CERT_05 (TC-007 precious-wandering-lighthouse, 2026-07-13): certification lifecycle validators
    try:
        from governance_validators_certification import (  # noqa: PLC0415
            validate_all_evidence_present_for_certified_formats as _v_cert01,
            validate_no_certified_format_has_material_stubs as _v_cert02,
            validate_certification_run_manifests_exist as _v_cert03,
            validate_certification_layer_registered as _v_cert04,
            validate_gap_reconciliation_map_exists as _v_cert05,
        )
        results.extend([
            _v_cert01(declaration, repo_root),
            _v_cert02(declaration, repo_root),
            _v_cert03(declaration, repo_root),
            _v_cert04(declaration, repo_root),
            _v_cert05(declaration, repo_root),
        ])
    except Exception as _exc_v_cert:
        _skipped_validators.append({"validators": ["V_CERT_01", "V_CERT_02", "V_CERT_03", "V_CERT_04", "V_CERT_05"], "error": str(_exc_v_cert)})

    # V150-V151, V154-V157 (CT-GOV-002, memoized-frolicking-donut TC-GOV-015, 2026-07-14):
    # product governance chain validators — CP/CI/RC lifecycle enforcement
    try:
        from governance_validators_product_gov import (  # noqa: PLC0415
            validate_governed_artifact_pre_flight as _v150,
            validate_change_proposal_coverage as _v151,
            validate_impact_analysis_on_accepted_proposals as _v154,
            validate_release_candidate_decision_chain as _v155,
            validate_governance_counter_report_fresh as _v156,
            validate_governance_binding_paths as _v157,
        )
        results.extend([
            _v150(declaration, repo_root),
            _v151(declaration, repo_root),
            _v154(declaration, repo_root),
            _v155(declaration, repo_root),
            _v156(declaration, repo_root),
            _v157(declaration, repo_root),
        ])
    except Exception as _exc_v150:
        _skipped_validators.append({"validators": ["V150", "V151", "V154", "V155", "V156", "V157"], "error": str(_exc_v150)})

    # V224 (TC-GOV-V224-001, 2026-07-15): Backfill completeness — WARN when migration map
    # exists without backfill plan
    try:
        from governance_validators_ext6 import (  # noqa: PLC0415
            validate_backfill_completeness as _v224,
        )
        results.append(_v224(declaration, repo_root))
    except Exception as _exc_v224:
        _skipped_validators.append({"validators": ["V224"], "error": str(_exc_v224)})

    # TC-BF-005: Load from _VALIDATOR_REGISTRY (additive — runs any validators not already
    # covered by explicit imports above).  The @validator decorator fires when each
    # governance_validators_*.py module is imported above, so the registry is populated by
    # the time we reach this point.  Dedup rule: if rule_id is already in explicit results,
    # the explicit instance wins (backward compat).
    _registry_new = 0
    _registry_dedup = 0
    try:
        from governance_validators_contract import _VALIDATOR_REGISTRY  # noqa: PLC0415
        # Dedup by function name — the existing results use the function name in "validator"
        # field, while the registry uses the function object itself. Match by __name__.
        seen_fn_names = {r.get("validator", "").lstrip("_") for r in results}
        for _reg_entry in _VALIDATOR_REGISTRY:
            _fn = _reg_entry.get("fn")
            if _fn is None:
                continue
            _fn_name = getattr(_fn, "__name__", "").lstrip("_")
            if _fn_name and _fn_name in seen_fn_names:
                _registry_dedup += 1
                continue
            try:
                _extra_result = _fn(declaration, repo_root)
                if isinstance(_extra_result, dict) and "result" in _extra_result:
                    results.append(_extra_result)
                    _registry_new += 1
            except Exception:
                pass
    except Exception:
        pass  # Registry loading is best-effort and non-blocking

    # TC-CTI-REGISTRY-001: Apply shadow routing via extracted helper.
    if shadow_registry:
        shadow_suppressions.extend(_apply_shadow_routing(results, shadow_registry))

    fail_count = sum(1 for r in results if r["result"] == "FAIL")
    warn_count = sum(1 for r in results if r["result"] == "WARN")
    pass_count = sum(1 for r in results if r["result"] == "PASS")
    blocks_sprint = any(r.get("blocks_sprint") for r in results if r["result"] == "FAIL")
    skipped_count = sum(len(s.get("validators", [1])) for s in _skipped_validators)
    ran_count = len(results)

    # TC-MA2-VAL-001-02: Enforce validator count at runtime (REQ-VAL-001).
    # Import failures in _skipped_validators reduce ran_count silently.
    # Emit a WARNING when ran_count + skipped_count deviates from expected_count.
    _count_ok = True
    _count_delta = (ran_count + skipped_count) - _EXPECTED_VALIDATOR_COUNT
    if _count_delta != 0:
        _count_ok = False
        import sys as _sys_val
        print(
            f"  [VALIDATOR-COUNT] WARNING: expected {_EXPECTED_VALIDATOR_COUNT} validators, "
            f"ran {ran_count} + skipped {skipped_count} = {ran_count + skipped_count} "
            f"(delta {_count_delta:+d}). "
            "Update _EXPECTED_VALIDATOR_COUNT in governance_validator_runner.py or fix imports.",
            file=_sys_val.stderr,
        )

    return {
        "all_pass": fail_count == 0,
        "blocks_sprint": blocks_sprint,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "pass_count": pass_count,
        "validators": results,
        "shadow_suppressions": shadow_suppressions,
        "skipped_validators": _skipped_validators,
        "skipped_count": skipped_count,
        "expected_count": _EXPECTED_VALIDATOR_COUNT,
        "registry_new": _registry_new,
        "registry_dedup": _registry_dedup,
        "ran_count": ran_count,
        "count_ok": _count_ok,
        "count_delta": _count_delta,
        "summary": (
            f"{pass_count} PASS / {warn_count} WARN / {fail_count} FAIL. "
            f"Blocks sprint: {blocks_sprint}."
        ),
    }
