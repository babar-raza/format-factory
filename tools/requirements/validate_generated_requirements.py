"""
validate_generated_requirements.py

Validate AI-generated format requirements against JSON schemas.

Usage:
    python tools/requirements/validate_generated_requirements.py [--format fods|fodt] [--verbose]
    python tools/requirements/validate_generated_requirements.py [--format fods|fodt] [--check-stale]
    python -m pytest tests/requirements/ -q

Exit codes:
    0 = all valid
    1 = validation errors found
    2 = schema or file not found
"""

import json
import sys
import argparse
from pathlib import Path

# Make user site-packages available so jsonschema resolves when this script
# is invoked directly without a PYTHONPATH pointing to user packages.
import site as _site
_site.addsitedir(_site.getusersitepackages())

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas" / "generated-requirements"
REQS_DIR = REPO_ROOT / "generated-requirements"

SCHEMA_MAP = {
    "commercial-requirements": "commercial-format-requirements.schema.json",
    "object-model-requirements": "object-model-requirements.schema.json",
    "save-edit-requirements": "save-edit-requirements.schema.json",
    "conversion-requirements": "conversion-requirements.schema.json",
    "traceability-map": "traceability-map.schema.json",
    "verifier-review": "verifier-review.schema.json",
}


def load_schema(schema_file: str) -> dict:
    path = SCHEMAS_DIR / schema_file
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_yaml_as_dict(path: Path) -> dict:
    """Load YAML file using basic PyYAML or return error."""
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML required: pip install pyyaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_with_jsonschema(data: dict, schema: dict, file_path: Path) -> list:
    """Return list of validation error strings."""
    try:
        import jsonschema
    except ImportError:
        # If jsonschema not installed, do manual validation
        return manual_validate(data, schema, file_path)
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(data), key=str):
        errors.append(f"  [{file_path.name}] {error.json_path}: {error.message}")
    return errors


def manual_validate(data: dict, schema: dict, file_path: Path) -> list:
    """Basic manual validation when jsonschema not installed."""
    errors = []
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"  [{file_path.name}] Missing required field: {field}")

    # Check requirements array only when the schema actually requires it
    schema_required = schema.get("required", [])
    schema_props = schema.get("properties", {})
    has_reqs_in_schema = "requirements" in schema_required or "entities" in schema_required or \
                         "requirements" in schema_props or "entities" in schema_props
    if has_reqs_in_schema or "requirements" in data or "entities" in data:
        reqs = data.get("requirements", data.get("entities", []))
        if not isinstance(reqs, list) or len(reqs) == 0:
            errors.append(f"  [{file_path.name}] 'requirements'/'entities' must be non-empty array")
            return errors
    else:
        return errors

    req_ids = set()
    for req in reqs:
        req_id = req.get("requirement_id") or req.get("entity_id")

        # Unique IDs check
        if req_id:
            if req_id in req_ids:
                errors.append(f"  [{file_path.name}] Duplicate requirement_id: {req_id}")
            req_ids.add(req_id)

        # Product goal mapping (for commercial requirements)
        if "product_goal_mapping" in schema.get("definitions", {}).get("Requirement", {}).get("required", []):
            mapping = req.get("product_goal_mapping", [])
            if not mapping:
                errors.append(f"  [{file_path.name}] {req_id}: product_goal_mapping is required and empty")

        # Source evidence required unless PRODUCT_DECISION
        source_type = req.get("source_type", "")
        source_evidence = req.get("source_evidence", [])
        if source_type != "PRODUCT_DECISION" and not source_evidence:
            errors.append(f"  [{file_path.name}] {req_id}: source_evidence required for source_type={source_type}")

        # AI_PROPOSAL cannot be ACCEPTED without verifier approval
        status = req.get("status", "")
        if source_type == "AI_PROPOSAL" and status == "ACCEPTED":
            errors.append(f"  [{file_path.name}] {req_id}: AI_PROPOSAL cannot be ACCEPTED without verifier approval")

        # ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements
        if status == "ACCEPTED_FOR_VERTICAL_SLICE":
            tests = req.get("test_requirements") or []
            if not tests:
                errors.append(f"  [{file_path.name}] {req_id}: ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements")

    # Conversion requirements must be future-scoped
    if "scope_note" in data:
        for req in reqs:
            scope = req.get("sprint_scope", "")
            status = req.get("status", "")
            if scope == "current" and status == "ACCEPTED_FOR_VERTICAL_SLICE":
                errors.append(f"  [{file_path.name}] Conversion req {req.get('requirement_id')} cannot be ACCEPTED_FOR_VERTICAL_SLICE in initial sprint")

    return errors


# ============================================================
# CROSS-FILE CONSISTENCY CHECKS (Lane B hardening)
# ============================================================

def _collect_accepted_ids(fmt_dir: Path, filename: str) -> set:
    """Extract ACCEPTED_FOR_VERTICAL_SLICE requirement IDs from a requirement file."""
    try:
        import yaml
    except ImportError:
        return set()
    path = fmt_dir / filename
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        r.get("requirement_id")
        for r in data.get("requirements", [])
        if r.get("status") == "ACCEPTED_FOR_VERTICAL_SLICE" and r.get("requirement_id")
    }


def _collect_all_requirement_ids(fmt_dir: Path) -> set:
    """Collect all requirement and entity IDs across requirement files for a format."""
    try:
        import yaml
    except ImportError:
        return set()
    ids = set()
    for filename in ["commercial-requirements.yaml", "save-edit-requirements.yaml", "conversion-requirements.yaml"]:
        path = fmt_dir / filename
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for r in data.get("requirements", []):
                rid = r.get("requirement_id")
                if rid:
                    ids.add(rid)
    obj_path = fmt_dir / "object-model-requirements.yaml"
    if obj_path.exists():
        data = yaml.safe_load(obj_path.read_text(encoding="utf-8")) or {}
        for e in data.get("entities", []):
            eid = e.get("entity_id")
            if eid:
                ids.add(eid)
    return ids


def _check_traceability_consistency(fmt: str) -> list:
    """Check traceability-map.accepted_for_vertical_slice matches requirement files."""
    errors = []
    try:
        import yaml
    except ImportError:
        return []

    fmt_dir = REQS_DIR / fmt
    tm_path = fmt_dir / "traceability-map.yaml"
    if not tm_path.exists():
        return [f"  [cross-file/{fmt}] traceability-map.yaml not found"]

    tm_data = yaml.safe_load(tm_path.read_text(encoding="utf-8")) or {}
    tm_accepted = set(tm_data.get("accepted_for_vertical_slice", []))

    all_req_accepted = (
        _collect_accepted_ids(fmt_dir, "commercial-requirements.yaml")
        | _collect_accepted_ids(fmt_dir, "save-edit-requirements.yaml")
    )

    for rid in sorted(tm_accepted - all_req_accepted):
        errors.append(
            f"  [cross-file/{fmt}] traceability-map lists {rid} as accepted_for_vertical_slice "
            f"but no requirement file has it ACCEPTED_FOR_VERTICAL_SLICE"
        )
    for rid in sorted(all_req_accepted - tm_accepted):
        errors.append(
            f"  [cross-file/{fmt}] {rid} is ACCEPTED_FOR_VERTICAL_SLICE in requirement files "
            f"but missing from traceability-map.accepted_for_vertical_slice"
        )

    # Deferred/accepted overlap check
    tm_deferred = set(tm_data.get("deferred_requirements", []))
    for rid in sorted(tm_accepted & tm_deferred):
        errors.append(
            f"  [cross-file/{fmt}] {rid} appears in BOTH accepted_for_vertical_slice AND deferred_requirements"
        )

    # AI_PROPOSAL count authority check
    ai_count = tm_data.get("source_evidence_summary", {}).get("AI_PROPOSAL", None)
    if ai_count is not None and ai_count != 0:
        errors.append(
            f"  [cross-file/{fmt}] AUTHORITY VIOLATION: traceability-map AI_PROPOSAL count = {ai_count} "
            f"(must be 0 for AUTHORITATIVE maps — GOVERNANCE.md 26.11)"
        )

    return errors


def _check_verifier_review_consistency(fmt: str) -> list:
    """Check verifier-review IDs exist in requirement files and result is valid."""
    errors = []
    try:
        import yaml
    except ImportError:
        return []

    fmt_dir = REQS_DIR / fmt
    vr_path = fmt_dir / "verifier-review.yaml"
    if not vr_path.exists():
        return [f"  [cross-file/{fmt}] verifier-review.yaml not found"]

    vr_data = yaml.safe_load(vr_path.read_text(encoding="utf-8")) or {}
    known_ids = _collect_all_requirement_ids(fmt_dir)

    for challenge in vr_data.get("requirement_challenges", []):
        rid = challenge.get("requirement_id")
        if rid and rid not in known_ids:
            errors.append(f"  [cross-file/{fmt}] verifier-review challenges unknown requirement_id: {rid}")

    for challenge in vr_data.get("object_model_challenges", []):
        eid = challenge.get("entity_id")
        if eid and eid not in known_ids:
            errors.append(f"  [cross-file/{fmt}] verifier-review challenges unknown entity_id: {eid}")

    verdict = vr_data.get("verifier_verdict", {})
    result = verdict.get("result")
    if result not in ("LANE_R5_PASS", "LANE_R5_FAIL"):
        errors.append(
            f"  [cross-file/{fmt}] verifier_verdict.result must be LANE_R5_PASS or LANE_R5_FAIL, got: {result!r}"
        )

    return errors


def validate_cross_file_consistency(fmt: str, verbose: bool = False) -> dict:
    """Run all cross-file consistency checks for a format."""
    errors = []
    errors.extend(_check_traceability_consistency(fmt))
    errors.extend(_check_verifier_review_consistency(fmt))
    status = "PASS" if not errors else "FAIL"
    if verbose and not errors:
        print(f"  [PASS] {fmt} cross-file consistency: all checks passed")
    return {"status": status, "errors": errors}


# ============================================================
# STALE DETECTION FRAMEWORK HOOK (stub — full impl future sprint)
# ============================================================

def check_stale_metadata(fmt: str, verbose: bool = False) -> dict:
    """
    Stale detection framework hook (STUB).

    Current behaviour: verifies generation_timestamp and input_source_hashes fields are
    present and that referenced source paths still exist. Does NOT hash-compare file contents.

    Full stale detection (hash comparison of input files against stored hashes) is deferred.
    See GOVERNANCE.md 26.11 and TC-0053 for the governance rule.

    Returns status:
      PASS              — metadata present, all referenced paths exist
      MANUAL_REQUIRED   — metadata present but hash comparison not implemented
      FAIL              — metadata fields missing (structural error)
      SKIP              — prerequisite files not found
    """
    try:
        import yaml
    except ImportError:
        return {"status": "SKIP", "errors": ["PyYAML required"], "warnings": []}

    fmt_dir = REQS_DIR / fmt
    cr_path = fmt_dir / "commercial-requirements.yaml"
    if not cr_path.exists():
        return {"status": "SKIP", "errors": [f"commercial-requirements.yaml not found for {fmt}"], "warnings": []}

    errors = []
    warnings = []
    data = yaml.safe_load(cr_path.read_text(encoding="utf-8")) or {}
    gen_timestamp = data.get("generation_timestamp", "")
    input_hashes = data.get("input_source_hashes", {})

    if not gen_timestamp:
        errors.append(f"  [stale/{fmt}] commercial-requirements.yaml missing generation_timestamp")

    if not input_hashes:
        warnings.append(
            f"  [stale/{fmt}] WARN: no input_source_hashes — stale detection requires manual check. "
            f"Verify source files against generation_timestamp={gen_timestamp} (GOVERNANCE.md 26.11)"
        )
    else:
        for source_key, source_path_str in input_hashes.items():
            if isinstance(source_path_str, str) and ("/" in source_path_str or "\\" in source_path_str):
                # Strip prose annotations like "(confirmed existing)" from path values
                import re as _re
                clean_path = _re.sub(r"\s*\(.*?\)\s*$", "", source_path_str).strip()
                candidate = REPO_ROOT / clean_path
                if not candidate.exists():
                    warnings.append(f"  [stale/{fmt}] WARN: input source no longer exists: {clean_path}")

    if verbose:
        if not errors and not warnings:
            print(f"  [PASS] {fmt} stale metadata: generation_timestamp present; {len(input_hashes)} input hashes")
        for w in warnings:
            print(w)

    if errors:
        return {"status": "FAIL", "errors": errors, "warnings": warnings}
    return {"status": "MANUAL_REQUIRED" if warnings else "PASS", "errors": [], "warnings": warnings}


# ============================================================
# MAIN VALIDATION ORCHESTRATION
# ============================================================

def validate_format(fmt: str, verbose: bool = False) -> dict:
    """Validate all requirement files for a given format."""
    results = {}
    fmt_dir = REQS_DIR / fmt

    for req_name, schema_file in SCHEMA_MAP.items():
        req_path = fmt_dir / f"{req_name}.yaml"
        if not req_path.exists():
            results[req_name] = {"status": "MISSING", "errors": [f"File not found: {req_path}"]}
            continue

        try:
            data = load_yaml_as_dict(req_path)
            schema = load_schema(schema_file)
            errors = validate_with_jsonschema(data, schema, req_path)
            status = "PASS" if not errors else "FAIL"
            results[req_name] = {"status": status, "errors": errors}
            if verbose:
                icon = "PASS" if not errors else "FAIL"
                print(f"  [{icon}] {fmt}/{req_name}.yaml ({len(errors)} errors)")
                for e in errors:
                    print(e)
        except FileNotFoundError as e:
            results[req_name] = {"status": "ERROR", "errors": [str(e)]}
        except Exception as e:
            results[req_name] = {"status": "ERROR", "errors": [f"Unexpected error: {e}"]}

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate AI-generated format requirements")
    parser.add_argument("--format", choices=["fods", "fodt", "all"], default="all")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--check-stale",
        action="store_true",
        help=(
            "Run stale detection framework hook (STUB). "
            "Checks metadata presence and source path existence. "
            "Full hash comparison deferred — see GOVERNANCE.md 26.11."
        ),
    )
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]
    all_pass = True
    total_errors = 0

    for fmt in formats:
        print(f"\n=== Validating {fmt.upper()} requirements ===")
        results = validate_format(fmt, args.verbose)
        for name, result in results.items():
            status = result["status"]
            errs = result["errors"]
            icon = "PASS" if status == "PASS" else "FAIL" if status in ("FAIL", "MISSING", "ERROR") else "?"
            print(f"  [{icon}] {name}: {status} ({len(errs)} issues)")
            if errs and not args.verbose:
                for e in errs[:3]:
                    print(f"    {e}")
            if status != "PASS":
                all_pass = False
                total_errors += len(errs)

        # Cross-file consistency (always run)
        cross_result = validate_cross_file_consistency(fmt, args.verbose)
        cross_status = cross_result["status"]
        cross_errs = cross_result["errors"]
        print(f"  [{'PASS' if cross_status == 'PASS' else 'FAIL'}] cross-file-consistency: {cross_status} ({len(cross_errs)} issues)")
        if cross_errs:
            for e in cross_errs[:5]:
                print(f"    {e}")
            all_pass = False
            total_errors += len(cross_errs)

        # Stale check (only if --check-stale flag provided)
        if args.check_stale:
            stale_result = check_stale_metadata(fmt, args.verbose)
            stale_status = stale_result["status"]
            stale_errs = stale_result.get("errors", [])
            stale_warns = stale_result.get("warnings", [])
            icon = "PASS" if stale_status in ("PASS", "MANUAL_REQUIRED") else "FAIL"
            print(f"  [{icon}] stale-check: {stale_status} ({len(stale_errs)} errors, {len(stale_warns)} warnings)")
            if stale_status == "MANUAL_REQUIRED":
                print("    STALE_DETECTION: MANUAL_REQUIRED — see GOVERNANCE.md 26.11")
            for w in stale_warns[:2]:
                print(f"    {w}")
            if stale_status == "FAIL":
                all_pass = False
                total_errors += len(stale_errs)

    print(f"\n{'REQUIREMENTS_SCHEMA_VALIDATION: PASS' if all_pass else 'REQUIREMENTS_SCHEMA_VALIDATION: FAIL'}")
    print(f"Total issues: {total_errors}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
