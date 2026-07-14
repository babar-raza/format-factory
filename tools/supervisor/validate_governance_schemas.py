"""TC-GOV-006: Validate the 8 governance schemas exist and are well-formed JSON."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / ".supervisor" / "schemas"

REQUIRED_SCHEMAS = [
    "governance-binding.schema.json",
    "governed-artifact.schema.json",
    "change-proposal.schema.json",
    "change-impact.schema.json",
    "change-decision.schema.json",
    "promotion-record.schema.json",
    "release-candidate.schema.json",
    "governance-gap.schema.json",
]

REQUIRED_TOP_KEYS = {
    "governance-binding.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "governed-artifact.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "change-proposal.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "change-impact.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "change-decision.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "promotion-record.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "release-candidate.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
    "governance-gap.schema.json": {"$schema", "$id", "title", "type", "required", "properties"},
}


def validate_schema_file(name: str) -> list[str]:
    """Return list of errors for the given schema file."""
    path = SCHEMA_DIR / name
    errors: list[str] = []
    if not path.exists():
        errors.append(f"MISSING: {name}")
        return errors
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"INVALID_JSON: {name}: {e}")
        return errors
    expected_keys = REQUIRED_TOP_KEYS.get(name, set())
    missing = expected_keys - set(data.keys())
    for k in sorted(missing):
        errors.append(f"MISSING_KEY: {name}: {k}")
    if data.get("additionalProperties") is not False:
        errors.append(f"MISSING_ADDITIONALPROPERTIES_FALSE: {name}")
    return errors


def main() -> int:
    all_errors: list[str] = []
    results: list[dict] = []
    for schema_name in REQUIRED_SCHEMAS:
        errs = validate_schema_file(schema_name)
        status = "PASS" if not errs else "FAIL"
        results.append({"schema": schema_name, "status": status, "errors": errs})
        all_errors.extend(errs)

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")

    for r in results:
        mark = "PASS" if r["status"] == "PASS" else "FAIL"
        print(f"  [{mark}] {r['schema']}")
        for e in r["errors"]:
            print(f"        ERROR: {e}")

    print(f"\nGovernance schema validation: {pass_count} PASS / {fail_count} FAIL")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
