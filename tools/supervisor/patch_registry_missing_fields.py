"""
Patch skill-registry.yaml to add missing mandatory_validations,
required_handoff_fields, and product_track fields.

This script ONLY adds fields that are missing or empty.
It does NOT modify any other fields.
It is idempotent: running twice produces no further changes.
"""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML required: pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / ".supervisor" / "skill-registry.yaml"

# Patch data: skill_id -> {field: value}
# Values are substantive and derived from each skill's command file content and purpose.
PATCHES: dict[str, dict] = {
    # ── Group 1: Skill governance skills (missing product_track, MV, RHF) ──────
    "backfill-task-skill-ownership": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "task_ownership_report_produced"],
        "required_handoff_fields": ["target_sprint_id"],
    },
    "build-capability-routes": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "capability_routes_evaluated"],
        "required_handoff_fields": ["output_path"],
    },
    "collect-skill-execution-receipts": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "receipts_inventory_produced"],
        "required_handoff_fields": ["sprint_id"],
    },
    "detect-ad-hoc-execution": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "ad_hoc_inventory_written"],
        "required_handoff_fields": ["report_output_path"],
    },
    "detect-duplicate-skills": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "duplicate_report_produced"],
        "required_handoff_fields": ["output_path"],
    },
    "enforce-skill-first-execution": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "enforcement_report_produced"],
        "required_handoff_fields": ["report_output_path"],
    },
    "inventory-commands": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "commands_inventory_produced"],
        "required_handoff_fields": ["output_format"],
    },
    "inventory-skills": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "skills_inventory_produced"],
        "required_handoff_fields": ["output_format"],
    },
    "normalize-skill-registry": {
        "product_track": "governance",
        "mandatory_validations": ["registry_backup_created", "registry_parse_validates_post_write"],
        "required_handoff_fields": ["backup_path"],
    },
    "qname-backfill": {
        "product_track": "governance",
        "mandatory_validations": ["no_gate_or_release_state_change", "qname_fields_populated"],
        "required_handoff_fields": ["format_id", "spec_qname"],
    },
    "run-skill-idempotency": {
        "product_track": "governance",
        "mandatory_validations": ["idempotency_verified", "no_product_source_mutation"],
        "required_handoff_fields": ["skill_id", "test_inputs"],
    },
    "scan-residual-bypasses": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "bypass_scan_report_produced"],
        "required_handoff_fields": ["scan_scope"],
    },
    "sync-skill-command-registry": {
        "product_track": "governance",
        "mandatory_validations": ["registry_consistency_verified", "no_orphan_commands_after_sync"],
        "required_handoff_fields": ["dry_run"],
    },
    "validate-mutation-guard": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "mutation_guard_report_produced"],
        "required_handoff_fields": ["target_path"],
    },
    "validate-skill-contracts": {
        "product_track": "governance",
        "mandatory_validations": ["no_product_source_mutation", "all_contracts_evaluated"],
        "required_handoff_fields": ["skill_id"],
    },
    # ── Group 2: backfill-gate4-prototype-evidence (planning) ──────────────────
    "backfill-gate4-prototype-evidence": {
        "mandatory_validations": ["evidence_declaration_exists", "taskcard_id_valid"],
        "required_handoff_fields": ["taskcard_id", "evidence_path", "sprint_id"],
    },
    # ── Group 3: machinery_governance / all_format_deepening / etc. ────────────
    "audit-root-tools": {
        "mandatory_validations": ["root_tools_report_produced", "no_product_source_mutation"],
    },
    "build-obligation-register": {
        "mandatory_validations": ["obligation_register_produced", "no_product_source_mutation"],
    },
    "create-consumer-roundtrip": {
        "mandatory_validations": ["roundtrip_test_created", "focused_tests_pass"],
    },
    "verify-obligation-entry": {
        "mandatory_validations": ["obligation_verified", "no_product_source_mutation"],
    },
    "portfolio-reconcile": {
        "mandatory_validations": ["portfolio_report_produced", "no_product_source_mutation"],
    },
    "update-obligation-entry": {
        "mandatory_validations": ["obligation_updated", "no_product_source_mutation"],
    },
    # ── Group 4: source_structure ───────────────────────────────────────────────
    "check-source-loc": {
        "mandatory_validations": ["loc_check_report_produced", "no_product_source_mutation"],
    },
    # ── Group 5: layer_governance skills ───────────────────────────────────────
    "reconcile-layer-index": {
        "mandatory_validations": ["layer_index_consistent", "no_product_source_mutation"],
        "required_handoff_fields": ["layer_id"],
    },
    "inventory-permanent-layer-plans": {
        "mandatory_validations": ["layer_plan_inventory_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["output_format"],
    },
    "detect-unlogged-work": {
        "mandatory_validations": ["unlogged_work_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["layer_id", "scan_scope"],
    },
    "detect-stale-layer-state": {
        "mandatory_validations": ["stale_state_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["layer_id"],
    },
    "select-next-layer-task": {
        "mandatory_validations": ["next_task_selected", "no_product_source_mutation"],
        "required_handoff_fields": ["layer_id", "current_state"],
    },
    "validate-permanent-layer-plans": {
        "mandatory_validations": ["plan_validation_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["layer_id"],
    },
    "reconcile-layer-task-register": {
        "mandatory_validations": ["task_register_consistent", "no_product_source_mutation"],
        "required_handoff_fields": ["layer_id"],
    },
    # ── Group 6: governance skills with empty lists ─────────────────────────────
    "capability-status": {
        "mandatory_validations": ["capability_status_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["capability_id"],
    },
    "validate-capability-parity": {
        "mandatory_validations": ["parity_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["capability_id", "target_language"],
    },
    "sync-capabilities": {
        "mandatory_validations": ["capability_index_updated", "no_product_source_mutation"],
        "required_handoff_fields": ["dry_run"],
    },
    "sync-readmes": {
        "mandatory_validations": ["readmes_consistent", "no_product_source_mutation"],
        "required_handoff_fields": ["dry_run"],
    },
    "generate-root-status": {
        "mandatory_validations": ["status_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["output_path"],
    },
    "certification-dashboard": {
        "mandatory_validations": ["certification_reports_exist", "portfolio_matrix_consistent"],
        "required_handoff_fields": ["format_id", "output_path"],
    },
    "certification-inventory-extractor": {
        "mandatory_validations": ["api_contract_extracted", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "output_path"],
    },
    "certification-stub-detector": {
        "mandatory_validations": ["stub_detection_report_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "certification-exception-checker": {
        "mandatory_validations": ["exception_coverage_checked", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "certification-assertion-scorer": {
        "mandatory_validations": ["assertion_quality_scored", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "certification-dotnet-assertion-scorer": {
        "mandatory_validations": ["dotnet_assertion_quality_scored", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "certification-generate-exception-tests": {
        "mandatory_validations": ["exception_tests_generated", "focused_tests_pass"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "certification-fix-weak-assertions": {
        "mandatory_validations": ["weak_assertions_fixed", "focused_tests_pass"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "certification-generate-security-tests": {
        "mandatory_validations": ["security_tests_generated", "focused_tests_pass"],
        "required_handoff_fields": ["format_id", "test_path"],
    },
    "inventory-format-dom": {
        "mandatory_validations": ["dom_inventory_produced", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "output_path"],
    },
    "check-dom-contract": {
        "mandatory_validations": ["dom_contract_verified", "no_product_source_mutation"],
        "required_handoff_fields": ["format_id", "dom_path"],
    },
    "query-control-index": {
        "mandatory_validations": ["control_index_available", "query_results_produced"],
        "required_handoff_fields": ["query", "query_type"],
    },
}


def apply_patches(registry_path: Path = REGISTRY_PATH) -> dict:
    """Apply field patches to the skill registry. Returns a summary dict."""
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    skills = data.get("skills", [])

    changed = 0
    skipped = 0
    not_found = list(PATCHES.keys())
    details = []

    for skill in skills:
        sid = skill.get("skill_id", "")
        if sid not in PATCHES:
            continue
        not_found.remove(sid)
        patch = PATCHES[sid]
        skill_changed = []
        for field, value in patch.items():
            current = skill.get(field)
            if not current:  # missing or empty list/None
                skill[field] = value
                skill_changed.append(field)
        if skill_changed:
            changed += 1
            details.append(f"  PATCHED {sid}: added {skill_changed}")
        else:
            skipped += 1

    registry_path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    return {
        "changed": changed,
        "skipped": skipped,
        "not_found_in_registry": not_found,
        "details": details,
    }


if __name__ == "__main__":
    result = apply_patches()
    print(f"Registry patched: {result['changed']} skills updated, {result['skipped']} already complete")
    for line in result["details"]:
        print(line)
    if result["not_found_in_registry"]:
        print(f"WARNING: skill IDs not found in registry: {result['not_found_in_registry']}")
