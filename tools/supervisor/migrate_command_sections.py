"""
Migrate command files in .claude/commands/ to meet the canonical contract
defined in validate_claude_commands.py.

This script ONLY adds missing required sections to failing command files.
It does NOT modify files that already pass validation.
It is idempotent: running twice produces no further changes.

Content is derived from the skill's registry metadata (product_track, purpose,
required_handoff_fields, mandatory_validations, implementation_paths) to ensure
substantive, accurate additions — not boilerplate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_claude_commands import (  # noqa: E402
    validate_command_file,
    validate_all,
    REQUIRED_SECTIONS,
    COMMANDS_DIR,
)

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML required")

REGISTRY_PATH = REPO_ROOT / ".supervisor" / "skill-registry.yaml"

# ─── Path policy by product_track ──────────────────────────────────────────────

_ALLOWED_PATHS: dict[str, list[str]] = {
    "foss_python": [
        "src/python/{format_id}/ — codec and model source files",
        "tests/python/{format_id}/ — focused tests for this format",
        "reports/ — evidence output (write)",
    ],
    "commercial_dotnet": [
        "src/net/{format_id}/ — .NET codec and model source files",
        "tests/net/{format_id}/ — .NET focused tests",
        "reports/ — evidence output (write)",
    ],
    "cross_product": [
        "src/python/{format_id}/ — Python codec source",
        "src/net/{format_id}/ — .NET codec source",
        "tests/python/{format_id}/ — Python tests",
        "tests/net/{format_id}/ — .NET tests",
        "reports/ — evidence output",
    ],
    "cross_product_export": [
        "src/python/{format_id}/ — Python export codec",
        "tests/python/{format_id}/ — Python export tests",
        "reports/ — evidence output",
    ],
    "governance": [
        ".supervisor/ — skill registry and governance config (read/write as needed)",
        ".governance/ — governance rules and policies (read-only)",
        ".claude/commands/ — command files (read-only unless updating commands)",
        "reports/ — governance reports (write)",
    ],
    "layer_governance": [
        "plans/layers/ — permanent layer plans (read/write)",
        ".governance/layers/ — layer governance config (read-only)",
        "reports/layers/ — layer governance reports (write)",
        ".local/supervisor/ — continuation and state files (read-only)",
    ],
    "infrastructure": [
        "tools/supervisor/ — supervisor tools (read-only)",
        "reports/supervisor/ — supervisor reports (write)",
        ".local/supervisor/ — local supervisor state (read/write)",
    ],
    "planning": [
        "plans/ — plan files (read/write)",
        "reports/ — evidence reports (write)",
        ".local/evidences/ — evidence declarations (write)",
    ],
    "acquisition": [
        "registry/ — format registry (read-only unless updating registry)",
        "reports/ — acquisition reports (write)",
        "plans/ — acquisition plans (read/write)",
    ],
    "source_structure": [
        "registry/source-structure-baseline.json — source baseline (read/write)",
        "tools/ — tool scripts (read-only)",
        "reports/ — structure reports (write)",
    ],
    "spec_parity": [
        "tools/spec/ — spec ingestion tools (read-only)",
        "src/python/{format_id}/ — spec-parity source (read/write)",
        "reports/spec/ — parity reports (write)",
    ],
    "spec_literal_healing": [
        "src/python/{format_id}/ — spec literal source (read/write)",
        "tools/spec/ — healing tools (read-only)",
        "reports/spec/ — healing reports (write)",
    ],
    "sal_infrastructure": [
        "tools/spec/ — SAL ingestion tools (read-only)",
        ".local/sal/ — SAL state files (read/write)",
        "reports/sal/ — SAL reports (write)",
    ],
    "sal_ingestion": [
        "tools/spec/ — SAL ingestion tools (read-only)",
        ".local/sal/ — SAL state files (write)",
    ],
    "maintenance": [
        "C:/Users/prora/.claude/projects/.../memory/MEMORY.md — auto-memory (write)",
        "reports/ — maintenance reports (write)",
        ".supervisor/ — supervisor config (read-only)",
    ],
    "oracle_execution": [
        "tools/oracle/ — oracle execution tools (read-only)",
        "reports/oracle/ — oracle reports (write)",
        ".local/oracle/ — oracle state (read/write)",
    ],
    "machinery_governance": [
        "tools/supervisor/ — supervisor tools (read-only)",
        ".local/supervisor/ — supervisor state (read-only)",
        "reports/ — audit reports (write)",
    ],
    "machinery_repair": [
        ".local/ — local state files (read/write)",
        "tools/ — repair scripts (read-only)",
        "reports/ — repair reports (write)",
    ],
    "all_format_deepening": [
        "registry/ — format and obligation registries (read/write)",
        "reports/ — deepening reports (write)",
        "plans/ — deepening plans (read/write)",
    ],
    "foss_python_consumer": [
        "tests/python/{format_id}/ — consumer round-trip tests (write)",
        "docs/examples/ — consumer examples (write)",
        "reports/ — consumer test evidence (write)",
    ],
    "developer_experience": [
        "examples/ — developer example scripts (write)",
        "docs/ — developer documentation (read/write)",
        "reports/ — DX reports (write)",
    ],
    "testing": [
        "tests/ — test files (read/write)",
        "reports/ — test reports (write)",
    ],
    "packaging": [
        "dist/ — package distribution artifacts (write)",
        "setup.py, pyproject.toml — package configuration (read-only)",
        "reports/ — packaging evidence (write)",
    ],
    "shared_reference_snapshot": [
        "registry/ — shared reference files (read/write)",
        "product-capability-matrix/ — capability matrix (read/write)",
        "reports/ — snapshot reports (write)",
    ],
}

_FORBIDDEN_PATHS: dict[str, list[str]] = {
    "foss_python": [
        "src/net/** — .NET product source is out of scope",
        "registry/format-registry.yaml — format registry requires separate gate authorization",
        ".supervisor/skill-registry.yaml — skill registry is read-only in this skill",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "commercial_dotnet": [
        "src/python/** — Python product source is out of scope for .NET skills",
        "registry/format-registry.yaml — format registry requires separate gate authorization",
        ".supervisor/skill-registry.yaml — skill registry is read-only in this skill",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "cross_product": [
        "registry/format-registry.yaml — format registry requires separate gate authorization",
        ".supervisor/skill-registry.yaml — skill registry is read-only in this skill",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "cross_product_export": [
        "src/net/** — .NET product source is out of scope",
        "registry/format-registry.yaml — format registry requires gate authorization",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "governance": [
        "src/net/** — no .NET product source mutation",
        "src/python/** — no Python product source mutation",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "layer_governance": [
        "src/net/** — no product source mutation",
        "src/python/** — no product source mutation",
        "plans/strategic/** — strategic plans are read-only",
        ".supervisor/skill-registry.yaml — skill registry is read-only here",
    ],
    "infrastructure": [
        "src/net/** — no product source mutation",
        "src/python/** — no product source mutation",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "planning": [
        "src/net/** — no product source mutation during planning",
        "src/python/** — no product source mutation during planning",
        "registry/format-registry.yaml — format registry is read-only here",
    ],
    "acquisition": [
        "src/net/** — no product source mutation during acquisition",
        "src/python/** — no product source mutation during acquisition",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "source_structure": [
        "src/net/** — no product source mutation",
        "src/python/** — no product source mutation",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "spec_parity": [
        "src/net/** — .NET source is out of scope for Python spec parity",
        "registry/format-registry.yaml — format registry requires gate authorization",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "spec_literal_healing": [
        "src/net/** — .NET source is out of scope for Python spec healing",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "sal_infrastructure": [
        "src/** — no product source mutation",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "sal_ingestion": [
        "src/** — no product source mutation during SAL ingestion",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "maintenance": [
        "src/net/** — no product source mutation",
        "src/python/** — no product source mutation",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "oracle_execution": [
        "src/** — no product source mutation during oracle execution",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "machinery_governance": [
        "src/** — no product source mutation",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "machinery_repair": [
        "src/net/** — .NET product source is out of scope for machinery repair",
        "src/python/** — Python product source is out of scope for machinery repair",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "all_format_deepening": [
        "src/net/** — no product source mutation in deepening skills",
        "src/python/** — no product source mutation in deepening skills",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "foss_python_consumer": [
        "src/python/** — consumer roundtrips are test-only; no codec changes",
        "src/net/** — .NET source is out of scope",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "developer_experience": [
        "src/** — developer examples must not modify product source",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "testing": [
        "src/** — test skills must not modify product source",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "packaging": [
        "src/** — packaging must not modify product source",
        "plans/strategic/** — strategic plans are read-only",
    ],
    "shared_reference_snapshot": [
        "src/** — reference snapshots must not modify product source",
        "plans/strategic/** — strategic plans are read-only",
    ],
}

# ─── Stop condition templates by mandatory validation name ──────────────────────

_VALIDATION_TO_STOP: dict[str, str] = {
    "no_product_source_mutation": "Stop if the execution would modify any file under src/",
    "registry_consistency_check": "Stop if the skill registry fails schema validation before or after",
    "registry_backup_created": "Stop if a backup of the registry cannot be created before writes",
    "registry_parse_validates_post_write": "Stop if the registry file fails YAML parse after writing",
    "product_code_ledger_validator": "Stop if no valid product code ledger entry exists for this work",
    "focused_python_tests": "Stop if focused Python tests do not pass",
    "no_gate_or_release_state_change": "Stop if any gate or release state would be modified",
    "ad_hoc_inventory_written": "Stop if the inventory file cannot be written to the output path",
    "no_orphan_commands_after_sync": "Stop if orphan commands remain after synchronization",
    "idempotency_verified": "Stop if the second run produces different output from the first",
    "capability_routes_evaluated": "Stop if any route in the routing registry cannot be evaluated",
    "evidence_declaration_exists": "Stop if no evidence declaration exists for the target taskcard",
    "taskcard_id_valid": "Stop if the taskcard ID is not found in the active plan",
    "layer_index_consistent": "Stop if the layer index is inconsistent after reconciliation",
    "task_register_consistent": "Stop if the task register is inconsistent after reconciliation",
    "next_task_selected": "Stop if no eligible next task can be identified in the current state",
    "stale_state_report_produced": "Stop if the stale state report file cannot be written",
    "unlogged_work_report_produced": "Stop if the unlogged work report file cannot be written",
    "plan_validation_report_produced": "Stop if the plan validation report cannot be written",
    "layer_plan_inventory_produced": "Stop if the layer plan inventory file cannot be written",
    "capability_status_report_produced": "Stop if the capability status report cannot be produced",
    "parity_report_produced": "Stop if the parity report cannot be produced",
    "capability_index_updated": "Stop if the capability index cannot be updated",
    "readmes_consistent": "Stop if README files remain inconsistent after sync",
    "status_report_produced": "Stop if the root status report file cannot be written",
    "certification_reports_exist": "Stop if required certification report files do not exist",
    "portfolio_matrix_consistent": "Stop if the portfolio matrix is inconsistent",
    "api_contract_extracted": "Stop if the API contract cannot be extracted for the target format",
    "stub_detection_report_produced": "Stop if the stub detection report cannot be written",
    "exception_coverage_checked": "Stop if exception coverage cannot be evaluated",
    "assertion_quality_scored": "Stop if assertion quality scoring fails for the target test path",
    "dotnet_assertion_quality_scored": "Stop if .NET assertion scoring fails",
    "exception_tests_generated": "Stop if exception tests cannot be generated",
    "weak_assertions_fixed": "Stop if weak assertion fixes cannot be validated",
    "security_tests_generated": "Stop if security tests cannot be generated",
    "dom_inventory_produced": "Stop if the DOM inventory cannot be produced for the format",
    "dom_contract_verified": "Stop if the DOM contract cannot be verified",
    "control_index_available": "Stop if the control index SQLite database is not available",
    "query_results_produced": "Stop if the query produces no results and no error is expected",
    "read_only_compliance": "Stop if any write to product source directories would occur",
    "structured_report_required": "Stop if no structured report file is produced",
    "loc_check_report_produced": "Stop if the LOC check report cannot be written",
    "bypass_scan_report_produced": "Stop if the bypass scan report cannot be written",
    "enforcement_report_produced": "Stop if the enforcement report cannot be written",
    "duplicate_report_produced": "Stop if the duplicate detection report cannot be written",
    "receipts_inventory_produced": "Stop if the receipts inventory file cannot be written",
    "task_ownership_report_produced": "Stop if the task ownership report cannot be produced",
    "mutation_guard_report_produced": "Stop if the mutation guard report cannot be written",
    "all_contracts_evaluated": "Stop if any skill contract cannot be evaluated",
    "commands_inventory_produced": "Stop if the commands inventory cannot be written",
    "skills_inventory_produced": "Stop if the skills inventory cannot be written",
    "qname_fields_populated": "Stop if spec_qname fields cannot be populated for the target format",
    "root_tools_report_produced": "Stop if the root tools audit report cannot be written",
    "obligation_register_produced": "Stop if the obligation register cannot be written",
    "roundtrip_test_created": "Stop if the round-trip test file cannot be created",
    "obligation_verified": "Stop if the obligation entry cannot be verified",
    "portfolio_report_produced": "Stop if the portfolio reconciliation report cannot be written",
    "obligation_updated": "Stop if the obligation entry cannot be updated",
    "governance_validators_pass": "Stop if any governance validator fails",
    "min_7_tests_per_function": "Stop if fewer than 7 tests pass for any new function",
    "no_new_external_imports": "Stop if new external library imports are introduced",
    "init_all_export_updated": "Stop if __all__ in __init__.py is not updated for new symbols",
    "min_9_tests_per_function": "Stop if fewer than 9 tests pass for any changed function",
    "focused_tests_pass": "Stop if focused tests do not pass after changes",
    "stage1_issue_model_schema_valid": "Stop if the sprint issue model does not validate",
    "root_cause_present_on_all_issues": "Stop if any issue is missing a root cause classification",
    "claim_classification_matrix_present": "Stop if the claim classification matrix is absent",
    "transcript_json_valid": "Stop if the transcript JSON does not parse or is malformed",
    "skill_id_registered": "Stop if the skill_id in the transcript is not in the active registry",
    "section_exists": "Stop if the target section does not exist in the permanent plan",
    "verdict_valid": "Stop if the verdict is not one of PASS, FAIL, PARTIAL, BLOCKED",
    "entry_appended": "Stop if the log entry cannot be appended to the plan",
    "task_was_active": "Stop if the target task is not currently in ACTIVE state",
    "evidence_provided": "Stop if no evidence paths are included in the closure",
    "register_updated": "Stop if the task register cannot be updated",
    "gate_criteria_evaluated": "Stop if all gate criteria cannot be evaluated",
    "no_self_approval": "Stop if the approval would be self-signed by the same agent",
    "scoring_sheet_produced": "Stop if a scoring sheet cannot be produced",
    "scoring_report_produced": "Stop if a scoring report cannot be written",
    "scoring_complete": "Stop if scoring does not complete for all items",
}


def _get_format_id(skill: dict) -> str:
    """Extract format_id from required_handoff_fields or return placeholder."""
    rhf = skill.get("required_handoff_fields", [])
    if "format_id" in rhf or "format_name" in rhf:
        return "<format_id>"
    return "<format>"


def _build_allowed_paths_section(skill: dict) -> str:
    """Generate ## Allowed Paths content for a skill."""
    track = skill.get("product_track", "governance")
    impl = skill.get("implementation_paths", [])
    fmt = _get_format_id(skill)

    # Use explicit implementation_paths if available and meaningful
    if impl and all("<" not in p for p in impl):
        lines = [f"- `{p}`" for p in impl[:5]]
        lines.append("- `reports/` — evidence output (write)")
    else:
        templates = _ALLOWED_PATHS.get(track, _ALLOWED_PATHS["governance"])
        lines = [f"- `{t.replace('{format_id}', fmt)}`" for t in templates]

    return "## Allowed Paths\n\n" + "\n".join(lines) + "\n"


def _build_forbidden_paths_section(skill: dict) -> str:
    """Generate ## Forbidden Paths content for a skill."""
    track = skill.get("product_track", "governance")
    templates = _FORBIDDEN_PATHS.get(track, _FORBIDDEN_PATHS["governance"])
    lines = [f"- `{t.split(' — ')[0]}` — {t.split(' — ', 1)[1] if ' — ' in t else t}"
             for t in templates]
    return "## Forbidden Paths\n\n" + "\n".join(lines) + "\n"


def _build_stop_conditions_section(skill: dict) -> str:
    """Generate ## Stop Conditions content from mandatory_validations."""
    mv = skill.get("mandatory_validations", [])
    lines = []
    for v in mv:
        if v in _VALIDATION_TO_STOP:
            lines.append(f"- {_VALIDATION_TO_STOP[v]}")
    # Add generic fall-backs if we have fewer than 2 conditions
    if not lines:
        purpose = skill.get("purpose", "")
        lines.append("- Stop if the skill's mandatory validations cannot be completed")
        if "report" in purpose.lower() or "inventory" in purpose.lower():
            lines.append("- Stop if the output file path is not writable")
        if "registry" in purpose.lower():
            lines.append("- Stop if the registry file cannot be parsed")
    if len(lines) < 2:
        lines.append("- Stop if any required input field is missing or invalid")
    return "## Stop Conditions\n\n" + "\n".join(lines) + "\n"


def _build_evidence_output_section(skill: dict) -> str:
    """Generate ## Output Format content from skill purpose."""
    purpose = skill.get("purpose", "").lower()
    pid = skill.get("skill_id", "")
    track = skill.get("product_track", "")

    if any(w in purpose for w in ["inventory", "scan", "list", "collect"]):
        content = (
            "- YAML or JSON inventory file at the configured output path\n"
            "- Summary counts: total scanned, found, flagged\n"
            "- Per-item entries with classification and evidence"
        )
    elif any(w in purpose for w in ["validate", "check", "verify", "detect"]):
        content = (
            "- PASS / FAIL / PARTIAL verdict printed to stdout\n"
            "- Per-item findings list with skill_id, issue, and severity\n"
            "- Report file at `reports/` with structured YAML findings"
        )
    elif any(w in purpose for w in ["sync", "normalize", "reconcile", "update", "regenerate"]):
        content = (
            "- Summary of items synced, added, removed, or unchanged\n"
            "- Report file at `reports/` confirming final state\n"
            "- Exit code 0 on success; non-zero with error message on failure"
        )
    elif any(w in purpose for w in ["generate", "create", "produce", "build"]):
        content = (
            "- Generated artifact written to the configured output path\n"
            "- Confirmation message: file path and size\n"
            "- Validation result confirming the output is well-formed"
        )
    elif "layer" in track or "layer" in purpose:
        content = (
            "- Layer task register updated with the result of this operation\n"
            "- Work log entry appended to the permanent layer plan\n"
            "- Structured verdict: PASS / FAIL with supporting evidence"
        )
    elif "certification" in pid:
        content = (
            "- Certification report JSON written to `reports/certification/<format_id>/`\n"
            "- Summary: total items, passing, failing, score\n"
            "- Actionable findings for any failing items"
        )
    else:
        content = (
            "- Structured result written to `reports/` in YAML or JSON format\n"
            "- Human-readable summary printed to stdout\n"
            "- Verdict: PASS / FAIL with per-item evidence"
        )
    return "## Output Format\n\n" + content + "\n"


def _build_inputs_section(skill: dict) -> str:
    """Generate ## Required Inputs content from required_handoff_fields."""
    rhf = skill.get("required_handoff_fields", [])
    purpose = skill.get("purpose", "")

    _descriptions = {
        "format_id": "target format identifier (e.g. `fods`, `csv`)",
        "format_name": "human-readable format name (e.g. `FODS`, `CSV`)",
        "api_name": "name of the API function being added or modified",
        "exact_source_paths": "list of source files to be modified",
        "exact_test_paths": "list of test files to be modified",
        "ledger_entry_path": "path to the product code ledger entry for this change",
        "focused_test_command": "pytest command to run focused tests for this change",
        "sprint_id": "sprint identifier for this execution (e.g. `r120`)",
        "output_path": "file path where the output report should be written",
        "output_format": "output format: `yaml`, `json`, or `markdown`",
        "target_skill_id": "skill_id of the target skill to be modified",
        "change_description": "one-line description of the change being made",
        "layer_id": "layer identifier (e.g. `L01-SAL`, `L06-ProductSource`)",
        "task_id": "task identifier within the layer (e.g. `TC-LA-001`)",
        "current_state": "JSON or YAML snapshot of the current layer state",
        "layer_id": "layer identifier from the permanent layer plan",
        "task_id": "task identifier from the layer task register",
        "verdict": "closure verdict: PASS, FAIL, PARTIAL, or BLOCKED",
        "verification_summary": "one-paragraph human-readable verification summary",
        "evidence_paths": "list of evidence file paths supporting this action",
        "permanent_plan_path": "path to the permanent layer plan file",
        "closure_verdict": "verdict for task closure: PASS, FAIL, or BLOCKED",
        "test_path": "path to the test directory or test file",
        "dom_path": "path to the DOM specification file",
        "query": "search query string for the control index",
        "query_type": "type of control index query: `search`, `gaps`, `sprints`, `sql`",
        "scan_scope": "scope to scan: `all`, `tools/supervisor/`, or a specific path",
        "target_path": "path to the target file or directory to analyze",
        "report_output_path": "path where the output report file should be written",
        "dry_run": "if `true`, print planned changes without writing (default: `false`)",
        "sprint_context": "sprint identifier providing context for this execution",
        "backup_path": "path for registry backup before normalization writes",
        "spec_qname": "spec QName string to use for backfill (e.g. `table:table-row`)",
        "test_inputs": "JSON object with input values for the idempotency test run",
        "target_sprint_id": "sprint identifier to backfill task ownership for",
        "taskcard_id": "taskcard identifier from the active plan (e.g. `TC-F-001`)",
        "evidence_path": "path to the evidence file for this taskcard",
        "capability_id": "capability identifier from the capability registry",
        "target_language": "language target: `python` or `dotnet`",
        "format_name": "codec format name matching the directory under src/python/",
        "codec_file": "relative path to the codec source file",
        "init_file": "relative path to the `__init__.py` for __all__ management",
        "test_dir": "relative path to the format's test directory",
        "function_name": "name of the function to add or modify",
        "function_signature": "complete Python type-annotated function signature",
        "capability_label": "one-line capability description for the matrix",
        "file_extensions": "list of file extensions (e.g. `[\".ndjson\", \".jsonl\"]`)",
        "format_spec_ref": "SAL fact reference or spec URL for the format",
        "detection_signature": "byte sequence or pattern that identifies this format",
        "stdlib_module": "Python stdlib module used for parsing; `None` if custom",
        "test_sprint": "sprint label for test file naming (e.g. `r120`)",
        "obligation_id": "identifier of the obligation entry to verify or update",
        "new_status": "new status value for the obligation entry",
        "evidence_root": "root directory containing the sprint evidence declaration",
        "transcript_path": "path to the skill invocation transcript JSON file",
        "gate_number": "gate number to evaluate (e.g. `8`, `11`)",
        "format_id": "format identifier from the format registry",
        "dom_level": "depth of DOM analysis: `shallow` or `deep`",
    }

    if not rhf:
        if "no input" in purpose.lower() or "zero" in purpose.lower():
            return "## Usage\n\nThis skill takes no required inputs; invoke as `/{}`.".format(
                skill.get("skill_id", "skill")
            ) + "\n"
        return "## Usage\n\nInvoke as `/{}`.\n".format(skill.get("skill_id", "skill"))

    lines = []
    for f in rhf:
        desc = _descriptions.get(f, f"value for `{f}`")
        lines.append(f"- `{f}` — {desc}")
    return "## Required Inputs\n\n" + "\n".join(lines) + "\n"


def _build_steps_section(skill: dict) -> str:
    """Generate ## Steps for the 3 files that lack a numbered list."""
    purpose = skill.get("purpose", "")
    sid = skill.get("skill_id", "")
    rhf = skill.get("required_handoff_fields", [])

    if "consumer" in sid:
        return (
            "## Steps\n\n"
            "1. Verify the target format package is installed and importable\n"
            "2. Load a sample file using the format's `load()` function\n"
            "3. Write the loaded model back using the format's `write()`/`create()` function\n"
            "4. Re-load the written output and compare with the original model\n"
            "5. Assert round-trip fidelity: all key fields must match\n"
            "6. Record the test as a focused test file in the format's test directory\n"
        )
    elif "preflight" in sid:
        return (
            "## Steps\n\n"
            "1. Read the incoming skill entry from the handoff\n"
            "2. Validate all required fields are present and non-empty\n"
            "3. Check the skill_id does not already exist in the skill registry\n"
            "4. Verify the command_file path references a valid `.md` file format\n"
            "5. Confirm the product_track is a valid enumerated value\n"
            "6. Write a preflight check result: PASS or FAIL with details\n"
        )
    elif "qname" in sid:
        return (
            "## Steps\n\n"
            "1. Read the target format's source files from `src/python/<format>/`\n"
            "2. Identify model classes and codec functions lacking `spec_qname` annotations\n"
            "3. Look up the correct QName for each item in the SAL fact registry\n"
            "4. Add `spec_qname: ClassVar[str] = \"<namespace>:<element>\"` to each model class\n"
            "5. Add QName docstring comments to codec functions where applicable\n"
            "6. Verify the format's test suite still passes after the additions\n"
        )
    else:
        return (
            "## Steps\n\n"
            "1. Read the handoff inputs and validate all required fields are present\n"
            "2. Load the relevant registry or source files for this operation\n"
            "3. Execute the skill's primary operation as described in the purpose\n"
            "4. Validate the result meets the skill's mandatory_validations\n"
            "5. Write the output to the configured output path\n"
            "6. Report the outcome: PASS / FAIL with per-item evidence\n"
        )


def _section_already_present(content: str, section_id: str) -> bool:
    """Check whether a section is already detected by the validator."""
    spec = REQUIRED_SECTIONS[section_id]
    for pattern in spec["heading_patterns"]:
        if re.search(pattern, content, re.MULTILINE):
            return True
    for pattern in spec.get("content_patterns", []):
        if re.search(pattern, content, re.MULTILINE):
            return True
    return False


def migrate_command_file(
    md_path: Path, skill: dict, dry_run: bool = False
) -> dict:
    """Add missing sections to a single command file. Returns result dict."""
    content = md_path.read_text(encoding="utf-8")
    result = validate_command_file(md_path)
    if result["valid"]:
        return {"file": md_path.name, "status": "already_valid", "added": []}

    missing_errors = [s for s in result["sections_missing"]
                      if REQUIRED_SECTIONS[s]["severity"] == "error"]

    if not missing_errors:
        return {"file": md_path.name, "status": "only_warnings", "added": []}

    added_sections = []
    additions = []

    for section_id in missing_errors:
        if _section_already_present(content, section_id):
            continue  # Safety: already there, shouldn't happen but guard anyway
        if section_id == "allowed_paths":
            text = _build_allowed_paths_section(skill)
        elif section_id == "forbidden_paths":
            text = _build_forbidden_paths_section(skill)
        elif section_id == "stop_conditions":
            text = _build_stop_conditions_section(skill)
        elif section_id == "evidence_output":
            text = _build_evidence_output_section(skill)
        elif section_id == "inputs":
            text = _build_inputs_section(skill)
        elif section_id == "steps":
            text = _build_steps_section(skill)
        else:
            continue  # purpose section - shouldn't happen (all files have title)
        additions.append(text)
        added_sections.append(section_id)

    if not additions:
        return {"file": md_path.name, "status": "no_addable_sections", "added": []}

    # Check if there is a ## Changelog section to insert before
    # We'll append at the end, ensuring each section is separated by a blank line
    new_content = content.rstrip("\n") + "\n"
    for text in additions:
        new_content += "\n" + text

    if not dry_run:
        md_path.write_text(new_content, encoding="utf-8")

    # Verify the file now passes (error-level only)
    if not dry_run:
        final = validate_command_file(md_path)
        new_missing_errors = [s for s in final["sections_missing"]
                              if REQUIRED_SECTIONS[s]["severity"] == "error"]
        status = "migrated_verified" if not new_missing_errors else "migrated_still_failing"
    else:
        status = "dry_run"

    return {"file": md_path.name, "status": status, "added": added_sections}


def build_skill_lookup() -> dict[str, dict]:
    """Build a mapping of command filename -> skill entry."""
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    lookup: dict[str, dict] = {}
    for skill in data.get("skills", []):
        cf = skill.get("command_file", "")
        if cf:
            filename = Path(cf).name
            lookup[filename] = skill
    return lookup


def run_migration(dry_run: bool = False) -> dict:
    """Migrate all failing command files. Returns summary."""
    skill_lookup = build_skill_lookup()
    md_files = sorted(COMMANDS_DIR.glob("*.md"))

    results = []
    for md in md_files:
        if md.name == "_readme.md":
            continue
        r = validate_command_file(md)
        if r["valid"]:
            continue
        missing_errors = [s for s in r["sections_missing"]
                          if REQUIRED_SECTIONS[s]["severity"] == "error"]
        if not missing_errors:
            continue
        skill = skill_lookup.get(md.name, {})
        result = migrate_command_file(md, skill, dry_run=dry_run)
        results.append(result)

    migrated = [r for r in results if "migrated" in r["status"]]
    verified = [r for r in results if r["status"] == "migrated_verified"]
    still_failing = [r for r in results if r["status"] == "migrated_still_failing"]

    return {
        "total_migrated": len(migrated),
        "verified": len(verified),
        "still_failing": len(still_failing),
        "dry_run": dry_run,
        "results": results,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--verify", action="store_true", help="Run full validation after migration")
    args = parser.parse_args()

    summary = run_migration(dry_run=args.dry_run)
    mode = "DRY RUN" if args.dry_run else "MIGRATION"
    print(f"\n{mode} COMPLETE")
    print(f"  Files migrated: {summary['total_migrated']}")
    if not args.dry_run:
        print(f"  Verified (now passing): {summary['verified']}")
        print(f"  Still failing: {summary['still_failing']}")

    for r in summary["results"]:
        status_char = "✓" if r["status"] == "migrated_verified" else ("✗" if "fail" in r["status"] else "→")
        print(f"  {status_char} {r['file']:55s}  added={r['added']}")

    if args.verify and not args.dry_run:
        print("\nRunning full validation...")
        from validate_claude_commands import validate_all, COMMANDS_DIR
        full = validate_all(COMMANDS_DIR, REGISTRY_PATH)
        s = full["summary"]
        print(f"  total={s['total_commands']} passing={s['passing']} failing={s['failing']}")
        if full["errors"]:
            for e in full["errors"][:10]:
                print(f"  ERROR: {e}")
