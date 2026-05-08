#!/usr/bin/env python3
"""
validate_playbook.py — Read-Only Playbook Validation Tool (S-F2F-02)

Validates a playbook YAML file against the acquisition-playbook or review-queue schema.
This tool is STRICTLY READ-ONLY:
  - Reads input YAML and schema JSON.
  - Writes NOTHING to disk.
  - Creates NO output files, review queues, replay artifacts, or logs.
  - Makes NO network calls.
  - Uses NO LLM.
  - Performs NO apply mode actions.

Usage:
  python tools/playbook/validate_playbook.py \\
    --schema schemas/playbook/acquisition-playbook.schema.json \\
    --input docs/examples/acquisition-playbook-fods-documentation-example.yaml \\
    --kind acquisition-playbook

Exit codes:
  0 — PLAYBOOK_VALIDATION: PASS
  1 — PLAYBOOK_VALIDATION: FAIL (invalid input or schema error)
  2 — PLAYBOOK_VALIDATION: ERROR (file not found, YAML parse error, etc.)

Policy: This tool is an evidence aid only. Validation PASS does not approve any gate,
replace DEC-034 independent verification, or replace human approval.
See docs/playbook-layer.md.
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Dependency check — PyYAML required; jsonschema optional
# ---------------------------------------------------------------------------
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
    JSONSCHEMA_VERSION = getattr(jsonschema, "__version__", "unknown")
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    JSONSCHEMA_VERSION = None

# ---------------------------------------------------------------------------
# Schema-specific required fields for structural fallback validation
# ---------------------------------------------------------------------------

ACQUISITION_PLAYBOOK_REQUIRED_FIELDS = [
    "schema_version",
    "playbook_id",
    "playbook_version",
    "format_id",
    "format_family",
    "playbook_kind",
    "status",
    "authority_statement",
    "non_authority_statement",
    "gates",
    "operations",
    "evidence_contracts",
    "validation_commands",
    "review_queue_policy",
    "reuse_policy",
    "provenance",
    "approvals_required",
    "forbidden_uses",
]

ACQUISITION_PLAYBOOK_STATUS_ENUM = [
    "draft", "proposed", "active", "deprecated", "superseded", "documentation_example_only"
]

ACQUISITION_PLAYBOOK_KIND_ENUM = [
    "format_playbook", "family_playbook", "documentation_example"
]

ACQUISITION_PLAYBOOK_SCHEMA_VERSION_ENUM = ["1.0"]

# Minimum forbidden_uses entries required by schema (minItems: 4)
ACQUISITION_PLAYBOOK_FORBIDDEN_USES_REQUIRED = [
    "automatic_gate_approval",
    "spec_or_legal_authority",
    "replacing_dec034",
    "replacing_human_approval",
]

# Forbidden uses that would indicate policy violation
FORBIDDEN_AUTHORITY_CLAIMS = [
    "automatic_gate_approval",
    "replacing_dec034",
    "replacing_human_approval",
    "spec_or_legal_authority",
    "product_release_authority",
]

OPERATION_REQUIRED_FIELDS = [
    "operation_id",
    "gate",
    "operation_type",
    "title",
    "description",
    "mode_allowed",
    "target_paths",
    "input_dependencies",
    "expected_outputs",
    "validation_commands",
    "evidence_requirements",
    "conflict_policy",
    "review_queue_policy",
    "reuse_level",
    "provenance",
    "status",
    "approval_boundary",
]

REVIEW_QUEUE_REQUIRED_FIELDS = [
    "schema_version",
    "queue_id",
    "run_id",
    "generated_at",
    "source_playbook_id",
    "source_format_id",
    "items",
    "summary",
    "governance",
]

REVIEW_QUEUE_SUMMARY_REQUIRED_FIELDS = [
    "total_items",
    "open_items",
    "blocker_count",
    "high_count",
    "blocks_apply_mode",
    "blocks_gate_progress",
]

REVIEW_QUEUE_GOVERNANCE_REQUIRED_FIELDS = [
    "cannot_approve_gates",
    "cannot_replace_dec034",
    "cannot_replace_evidence_contracts",
    "cannot_replace_human_approval",
    "high_severity_blocks_apply",
    "gate_progress_requires_resolution",
]

REVIEW_ITEM_REQUIRED_FIELDS = [
    "item_id",
    "format_id",
    "gate",
    "operation_id",
    "target_path",
    "issue_type",
    "severity",
    "deterministic_failure_reason",
    "required_action",
    "evidence_required",
    "status",
    "owner_role",
    "blocks_apply_mode",
    "blocks_gate_progress",
    "provenance",
]

PROVENANCE_REQUIRED_FIELDS = ["created_by_sprint", "created_at", "last_modified_sprint"]

# ---------------------------------------------------------------------------
# Structural validation helpers
# ---------------------------------------------------------------------------

def _check_required_fields(data, required_fields, context="document"):
    """Return list of error messages for missing required fields."""
    errors = []
    if not isinstance(data, dict):
        return [f"{context}: expected a mapping (dict), got {type(data).__name__}"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{context}: missing required field '{field}'")
    return errors


def _validate_acquisition_playbook_structural(data):
    """Perform structural validation for acquisition-playbook kind."""
    errors = []

    # Top-level required fields
    errors.extend(_check_required_fields(data, ACQUISITION_PLAYBOOK_REQUIRED_FIELDS, "playbook"))

    if errors:
        return errors  # Stop early — missing top-level fields make further checks unreliable

    # schema_version enum
    sv = data.get("schema_version")
    if sv not in ACQUISITION_PLAYBOOK_SCHEMA_VERSION_ENUM:
        errors.append(
            f"playbook: schema_version '{sv}' not in allowed values {ACQUISITION_PLAYBOOK_SCHEMA_VERSION_ENUM}"
        )

    # playbook_kind enum
    pk = data.get("playbook_kind")
    if pk not in ACQUISITION_PLAYBOOK_KIND_ENUM:
        errors.append(
            f"playbook: playbook_kind '{pk}' not in allowed values {ACQUISITION_PLAYBOOK_KIND_ENUM}"
        )

    # status enum
    st = data.get("status")
    if st not in ACQUISITION_PLAYBOOK_STATUS_ENUM:
        errors.append(
            f"playbook: status '{st}' not in allowed values {ACQUISITION_PLAYBOOK_STATUS_ENUM}"
        )

    # authority_statement minLength: 20
    auth = data.get("authority_statement", "")
    if isinstance(auth, str) and len(auth.strip()) < 20:
        errors.append(
            "playbook: authority_statement must be at least 20 characters"
        )

    # non_authority_statement minLength: 20
    non_auth = data.get("non_authority_statement", "")
    if isinstance(non_auth, str) and len(non_auth.strip()) < 20:
        errors.append(
            "playbook: non_authority_statement must be at least 20 characters"
        )

    # forbidden_uses — must include required minimum set (schema minItems: 4)
    forbidden = data.get("forbidden_uses", [])
    if not isinstance(forbidden, list):
        errors.append("playbook: forbidden_uses must be a list")
    else:
        if len(forbidden) < 4:
            errors.append(
                f"playbook: forbidden_uses must have at least 4 items, got {len(forbidden)}"
            )
        for required_use in ACQUISITION_PLAYBOOK_FORBIDDEN_USES_REQUIRED:
            if required_use not in forbidden:
                errors.append(
                    f"playbook: forbidden_uses must include '{required_use}'"
                )

    # documentation_example_only status checks
    if st == "documentation_example_only":
        if not data.get("not_for_execution", False):
            errors.append(
                "playbook: status=documentation_example_only requires not_for_execution: true"
            )

    # gates must be a list
    gates = data.get("gates", [])
    if not isinstance(gates, list):
        errors.append("playbook: gates must be a list")

    # operations must be a list, each operation must have required fields
    operations = data.get("operations", [])
    if not isinstance(operations, list):
        errors.append("playbook: operations must be a list")
    else:
        for i, op in enumerate(operations):
            op_errors = _check_required_fields(
                op, OPERATION_REQUIRED_FIELDS, f"operations[{i}]"
            )
            errors.extend(op_errors)

    # review_queue_policy must have required fields
    rqp = data.get("review_queue_policy", {})
    if not isinstance(rqp, dict):
        errors.append("playbook: review_queue_policy must be a mapping")
    else:
        for f in ["severity_threshold_blocks_apply", "auto_resolve_allowed"]:
            if f not in rqp:
                errors.append(f"playbook.review_queue_policy: missing required field '{f}'")

    # reuse_policy must have required fields
    rp = data.get("reuse_policy", {})
    if not isinstance(rp, dict):
        errors.append("playbook: reuse_policy must be a mapping")
    else:
        for f in ["family_reuse_allowed", "inherited_gate_approval", "reuse_requires_explicit_classification"]:
            if f not in rp:
                errors.append(f"playbook.reuse_policy: missing required field '{f}'")
        # inherited_gate_approval must be false
        if rp.get("inherited_gate_approval") is not False:
            errors.append(
                "playbook.reuse_policy: inherited_gate_approval must be false (gate approval cannot be inherited)"
            )

    # provenance must have required fields
    prov = data.get("provenance", {})
    errors.extend(_check_required_fields(prov, PROVENANCE_REQUIRED_FIELDS, "playbook.provenance"))

    # approvals_required must be a list
    ar = data.get("approvals_required", [])
    if not isinstance(ar, list):
        errors.append("playbook: approvals_required must be a list")

    # evidence_contracts must be a list
    ec = data.get("evidence_contracts", [])
    if not isinstance(ec, list):
        errors.append("playbook: evidence_contracts must be a list")

    return errors


def _validate_review_queue_structural(data):
    """Perform structural validation for review-queue kind."""
    errors = []

    # Top-level required fields
    errors.extend(_check_required_fields(data, REVIEW_QUEUE_REQUIRED_FIELDS, "review_queue"))

    if errors:
        return errors

    # schema_version
    sv = data.get("schema_version")
    if sv not in ["1.0"]:
        errors.append(f"review_queue: schema_version '{sv}' not in allowed values ['1.0']")

    # summary required fields
    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        errors.append("review_queue: summary must be a mapping")
    else:
        for f in REVIEW_QUEUE_SUMMARY_REQUIRED_FIELDS:
            if f not in summary:
                errors.append(f"review_queue.summary: missing required field '{f}'")

    # governance required fields
    governance = data.get("governance", {})
    if not isinstance(governance, dict):
        errors.append("review_queue: governance must be a mapping")
    else:
        for f in REVIEW_QUEUE_GOVERNANCE_REQUIRED_FIELDS:
            if f not in governance:
                errors.append(f"review_queue.governance: missing required field '{f}'")
        # cannot_approve_gates must be true
        if governance.get("cannot_approve_gates") is not True:
            errors.append("review_queue.governance: cannot_approve_gates must be true")
        # cannot_replace_dec034 must be true
        if governance.get("cannot_replace_dec034") is not True:
            errors.append("review_queue.governance: cannot_replace_dec034 must be true")
        # cannot_replace_human_approval must be true
        if governance.get("cannot_replace_human_approval") is not True:
            errors.append("review_queue.governance: cannot_replace_human_approval must be true")
        # high_severity_blocks_apply must be true
        if governance.get("high_severity_blocks_apply") is not True:
            errors.append("review_queue.governance: high_severity_blocks_apply must be true")

    # items must be a list
    items = data.get("items", [])
    if not isinstance(items, list):
        errors.append("review_queue: items must be a list")
    else:
        for i, item in enumerate(items):
            item_errors = _check_required_fields(
                item, REVIEW_ITEM_REQUIRED_FIELDS, f"items[{i}]"
            )
            errors.extend(item_errors)
            # Enforce: blocks_apply_mode must be true when severity is high or blocker
            sev = item.get("severity")
            bam = item.get("blocks_apply_mode")
            if sev in ("high", "blocker") and bam is not True:
                errors.append(
                    f"items[{i}]: blocks_apply_mode must be true when severity='{sev}'"
                )

    return errors


# ---------------------------------------------------------------------------
# Forbidden authority pattern check (cross-kind)
# ---------------------------------------------------------------------------

def _check_forbidden_authority(data, kind):
    """Check for forbidden authority claims in the document."""
    errors = []
    if kind != "acquisition-playbook":
        return errors

    forbidden = data.get("forbidden_uses", [])
    if not isinstance(forbidden, list):
        return errors

    # The schema says forbidden_uses must INCLUDE these — so missing them is the violation
    for claim in ACQUISITION_PLAYBOOK_FORBIDDEN_USES_REQUIRED:
        if claim not in forbidden:
            errors.append(
                f"FORBIDDEN_AUTHORITY: playbook does not explicitly forbid '{claim}' — "
                "this use must be listed in forbidden_uses"
            )

    # Check reuse_policy
    rp = data.get("reuse_policy", {})
    if isinstance(rp, dict):
        if rp.get("inherited_gate_approval") is True:
            errors.append(
                "FORBIDDEN_AUTHORITY: inherited_gate_approval is true — "
                "gate approval cannot be inherited from a family playbook"
            )

    return errors


# ---------------------------------------------------------------------------
# JSON Schema validation (when jsonschema is available)
# ---------------------------------------------------------------------------

def _validate_with_jsonschema(data, schema, errors):
    """Validate data against schema using jsonschema. Append errors to list."""
    try:
        validator = jsonschema.Draft7Validator(schema)
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            path = ".".join(str(p) for p in error.path) if error.path else "(root)"
            errors.append(f"schema error at '{path}': {error.message}")
    except jsonschema.exceptions.SchemaError as e:
        errors.append(f"schema itself is invalid: {e.message}")
    return errors


# ---------------------------------------------------------------------------
# Main validation entry point
# ---------------------------------------------------------------------------

def validate(schema_path, input_path, kind, strict=False, format_id=None):
    """
    Validate input_path against schema_path.
    Returns (passed: bool, errors: list[str], info: dict).
    THIS FUNCTION WRITES NOTHING.
    """
    info = {
        "kind": kind,
        "input": input_path,
        "schema": schema_path,
        "format_id": format_id,
        "json_schema_engine": "JSONSCHEMA" if JSONSCHEMA_AVAILABLE else "FALLBACK_STRUCTURAL_VALIDATION",
        "json_schema_version": JSONSCHEMA_VERSION if JSONSCHEMA_AVAILABLE else None,
    }
    errors = []

    # Check dependencies
    if not YAML_AVAILABLE:
        errors.append(
            "DEPENDENCY_ERROR: PyYAML is required but not installed. "
            "Install with: pip install pyyaml"
        )
        return False, errors, info

    # Check files exist
    if not os.path.isfile(schema_path):
        errors.append(f"FILE_NOT_FOUND: schema file does not exist: {schema_path}")
        return False, errors, info
    if not os.path.isfile(input_path):
        errors.append(f"FILE_NOT_FOUND: input file does not exist: {input_path}")
        return False, errors, info

    # Load schema (JSON)
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"SCHEMA_PARSE_ERROR: schema file is not valid JSON: {e}")
        return False, errors, info
    except OSError as e:
        errors.append(f"SCHEMA_READ_ERROR: {e}")
        return False, errors, info

    # Load input (YAML)
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML_PARSE_ERROR: input file is not valid YAML: {e}")
        return False, errors, info
    except OSError as e:
        errors.append(f"INPUT_READ_ERROR: {e}")
        return False, errors, info

    if data is None:
        errors.append("INPUT_ERROR: input file is empty or yields no YAML document")
        return False, errors, info

    # Run validation
    if JSONSCHEMA_AVAILABLE:
        _validate_with_jsonschema(data, schema, errors)
    else:
        # Fallback structural validation
        if kind == "acquisition-playbook":
            errors.extend(_validate_acquisition_playbook_structural(data))
        elif kind == "review-queue":
            errors.extend(_validate_review_queue_structural(data))
        else:
            errors.append(
                f"UNKNOWN_KIND: '{kind}' — supported kinds: acquisition-playbook, review-queue"
            )

    # Forbidden authority check (always run, independent of jsonschema)
    errors.extend(_check_forbidden_authority(data, kind))

    passed = len(errors) == 0
    return passed, errors, info


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="validate_playbook.py — Read-only playbook YAML validator (S-F2F-02). "
                    "Writes nothing. No replay. No apply mode. No review queue output."
    )
    parser.add_argument(
        "--schema", required=True,
        help="Path to JSON Schema file (e.g. schemas/playbook/acquisition-playbook.schema.json)"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to YAML file to validate"
    )
    parser.add_argument(
        "--kind", required=True,
        choices=["acquisition-playbook", "review-queue"],
        help="Kind of playbook document to validate"
    )
    parser.add_argument(
        "--format-id", default=None,
        help="Optional format identifier for context (e.g. fods, fodt). Not used for validation logic."
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as errors (reserved for future use)."
    )
    parser.add_argument(
        "--json-output", action="store_true",
        help="Emit validation result as JSON to stdout instead of human-readable text."
    )
    args = parser.parse_args()

    passed, errors, info = validate(
        schema_path=args.schema,
        input_path=args.input,
        kind=args.kind,
        strict=args.strict,
        format_id=args.format_id,
    )

    if not JSONSCHEMA_AVAILABLE:
        print(
            "JSON_SCHEMA_ENGINE: FALLBACK_STRUCTURAL_VALIDATION "
            "(jsonschema not installed — full JSON Schema compliance not guaranteed)",
            file=sys.stderr
        )

    if args.json_output:
        import json as _json
        result = {
            "playbook_validation": "PASS" if passed else "FAIL",
            "kind": info["kind"],
            "input": info["input"],
            "schema": info["schema"],
            "json_schema_engine": info["json_schema_engine"],
            "errors": errors,
        }
        print(_json.dumps(result, indent=2))
    else:
        if passed:
            print(f"PLAYBOOK_VALIDATION: PASS")
            print(f"kind: {info['kind']}")
            print(f"input: {info['input']}")
            print(f"schema: {info['schema']}")
        else:
            print(f"PLAYBOOK_VALIDATION: FAIL")
            print(f"kind: {info['kind']}")
            print(f"input: {info['input']}")
            print(f"schema: {info['schema']}")
            print("errors:")
            for err in errors:
                print(f"  - {err}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
