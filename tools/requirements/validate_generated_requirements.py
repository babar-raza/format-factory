"""
validate_generated_requirements.py

Validate AI-generated format requirements against JSON schemas.

Usage:
    python tools/requirements/validate_generated_requirements.py [--format fods|fodt] [--verbose]
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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas" / "generated-requirements"
REQS_DIR = REPO_ROOT / "generated-requirements"

SCHEMA_MAP = {
    "commercial-requirements": "commercial-format-requirements.schema.json",
    "object-model-requirements": "object-model-requirements.schema.json",
    "save-edit-requirements": "save-edit-requirements.schema.json",
    "conversion-requirements": "conversion-requirements.schema.json",
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

    # Check requirements array if present
    reqs = data.get("requirements", data.get("entities", []))
    if not isinstance(reqs, list) or len(reqs) == 0:
        errors.append(f"  [{file_path.name}] 'requirements'/'entities' must be non-empty array")
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

    print(f"\n{'REQUIREMENTS_SCHEMA_VALIDATION: PASS' if all_pass else 'REQUIREMENTS_SCHEMA_VALIDATION: FAIL'}")
    print(f"Total issues: {total_errors}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
