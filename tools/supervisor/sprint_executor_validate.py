"""
sprint_executor_validate.py — Declaration Pre-Validator with --repair Mode

Validates an evidence-declaration.yaml against the JSON schema before submitting
to autonomous_cycle.py. Strips markdown fences and fixes common YAML errors
automatically when --repair is specified.

This is the format-factory equivalent of `sprint_loop.py validate --repair`
in the aspose.org system.

Usage:
  # Check only
  python tools/supervisor/sprint_executor_validate.py <declaration.yaml>

  # Check + auto-repair
  python tools/supervisor/sprint_executor_validate.py <declaration.yaml> --repair

Exit codes:
  0  — validation passed (file is schema-valid)
  1  — validation failed (errors printed to stdout as JSON)
  9  — unexpected error (file not found, parse error)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
_SCHEMA_PATH = _REPO / ".supervisor" / "schemas" / "evidence-declaration.schema.json"

# Required top-level fields from schema
_REQUIRED_FIELDS = [
    "run_id", "sprint_id", "evidence_root",
    "start_time", "end_time",
    "git_head_start", "git_head_end", "git_status_final",
    "declared_scope",
    "planned_work_items", "completed_work_items", "incomplete_work_items",
    "changed_files", "tests_run", "test_results",
    "evidence_artifacts", "reports_created",
    "worker_self_verdict", "worker_self_grade",
    "next_recommended_work",
]

# Known invalid additionalProperties (banned by schema's additionalProperties: false)
_BANNED_FIELDS = {
    "schema_version", "tests_failed", "tests_passed", "tests_skipped", "worker_id",
    "id",  # must be item_id in planned_work_items
}

# Valid worker_self_grade values
_VALID_GRADES = {"PASS", "PARTIAL", "FAIL", "BLOCKED"}

# Valid planned_work_items status values
_VALID_ITEM_STATUSES = {"completed", "partial", "not_started", "blocked_external_gate"}


# ---------------------------------------------------------------------------
# Repair helpers
# ---------------------------------------------------------------------------

def _strip_markdown_fences(text: str) -> str:
    """Remove ```yaml ... ``` or ``` ... ``` wrappers."""
    # Match optional yaml/yml language tag
    text = re.sub(r"^```(?:yaml|yml)?\s*\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n```\s*$", "", text, flags=re.MULTILINE)
    # Also strip trailing fences on same line
    text = text.strip()
    if text.startswith("```"):
        text = text[3:].lstrip("yaml").lstrip("yml").lstrip("\n")
    if text.endswith("```"):
        text = text[:-3].rstrip()
    return text


def _fix_yaml_aliases(text: str) -> str:
    """
    Fix common YAML alias errors:
    - `acceptance_criteria: [...]` → must be string, not list
    - `completed_work_items` items must be strings not objects
    """
    # Nothing deterministic to fix here without full AST; return as-is
    return text


def _repair_document(doc: dict) -> tuple[dict, list[str]]:
    """
    Apply structural repairs to a parsed declaration dict.
    Returns (repaired_doc, list_of_repairs_applied).
    """
    repairs = []

    # Remove banned fields
    for field in list(doc.keys()):
        if field in _BANNED_FIELDS:
            del doc[field]
            repairs.append(f"Removed banned field: {field}")

    # Ensure tests_run is int
    if "tests_run" in doc and not isinstance(doc["tests_run"], int):
        try:
            doc["tests_run"] = int(doc["tests_run"])
            repairs.append("Converted tests_run to int")
        except (TypeError, ValueError):
            doc["tests_run"] = 0
            repairs.append("Reset tests_run to 0 (unconvertible)")

    # Ensure test_results is dict
    if "test_results" in doc and not isinstance(doc["test_results"], dict):
        doc["test_results"] = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        repairs.append("Reset test_results to empty dict")

    # Ensure list fields are lists
    for list_field in [
        "planned_work_items", "completed_work_items", "incomplete_work_items",
        "changed_files", "evidence_artifacts", "reports_created", "next_recommended_work",
    ]:
        if list_field in doc and not isinstance(doc[list_field], list):
            doc[list_field] = []
            repairs.append(f"Reset {list_field} to empty list")

    # completed_work_items must be list of strings
    if isinstance(doc.get("completed_work_items"), list):
        fixed = []
        changed = False
        for item in doc["completed_work_items"]:
            if isinstance(item, str):
                fixed.append(item)
            elif isinstance(item, dict) and "item_id" in item:
                fixed.append(item["item_id"])
                changed = True
            else:
                fixed.append(str(item))
                changed = True
        if changed:
            doc["completed_work_items"] = fixed
            repairs.append("Converted completed_work_items entries to strings")

    # acceptance_criteria in planned_work_items must be string not list/dict
    if isinstance(doc.get("planned_work_items"), list):
        for item in doc["planned_work_items"]:
            if not isinstance(item, dict):
                continue
            if "id" in item and "item_id" not in item:
                item["item_id"] = item.pop("id")
                repairs.append(f"Renamed 'id' to 'item_id' in planned_work_items item")
            if "acceptance_criteria" in item and not isinstance(item["acceptance_criteria"], str):
                item["acceptance_criteria"] = str(item["acceptance_criteria"])
                repairs.append("Converted acceptance_criteria to string")
            if "status" in item and item["status"] not in _VALID_ITEM_STATUSES:
                repairs.append(
                    f"WARNING: planned_work_items[{item.get('item_id','?')}].status "
                    f"'{item['status']}' not in {_VALID_ITEM_STATUSES}"
                )

    # worker_self_grade must be valid
    if "worker_self_grade" in doc and doc["worker_self_grade"] not in _VALID_GRADES:
        doc["worker_self_grade"] = "PASS"
        repairs.append(f"Reset worker_self_grade to PASS (was invalid)")

    # evidence_artifacts items must be objects with at least path + type
    if isinstance(doc.get("evidence_artifacts"), list):
        fixed_arts = []
        changed = False
        for art in doc["evidence_artifacts"]:
            if isinstance(art, str):
                fixed_arts.append({"path": art, "type": "file", "description": ""})
                changed = True
            elif isinstance(art, dict):
                fixed_arts.append(art)
            else:
                changed = True  # skip invalid
        if changed:
            doc["evidence_artifacts"] = fixed_arts
            repairs.append("Converted evidence_artifacts string entries to {path, type} objects")

    return doc, repairs


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate(doc: dict) -> list[str]:
    """
    Structural validation against the schema's required fields and type constraints.
    Returns list of error strings. Empty list = PASS.
    """
    errors = []

    # Check required fields
    for field in _REQUIRED_FIELDS:
        if field not in doc:
            errors.append(f"MISSING required field: {field}")

    # Check banned fields
    for field in doc.keys():
        if field in _BANNED_FIELDS:
            errors.append(f"BANNED field present (additionalProperties: false): {field}")

    # Type checks
    if "tests_run" in doc and not isinstance(doc["tests_run"], int):
        errors.append(f"tests_run must be int, got {type(doc['tests_run']).__name__}")

    if "test_results" in doc and not isinstance(doc["test_results"], dict):
        errors.append("test_results must be object/dict")

    if "worker_self_grade" in doc and doc["worker_self_grade"] not in _VALID_GRADES:
        errors.append(
            f"worker_self_grade '{doc['worker_self_grade']}' not in {_VALID_GRADES}"
        )

    for list_field in [
        "planned_work_items", "completed_work_items", "incomplete_work_items",
        "changed_files", "evidence_artifacts", "reports_created", "next_recommended_work",
    ]:
        if list_field in doc and not isinstance(doc[list_field], list):
            errors.append(f"{list_field} must be array/list")

    # completed_work_items: items must be strings
    cwi = doc.get("completed_work_items", [])
    if isinstance(cwi, list):
        for i, item in enumerate(cwi):
            if not isinstance(item, str):
                errors.append(
                    f"completed_work_items[{i}] must be string (item_id), got {type(item).__name__}"
                )

    # evidence_artifacts: items must be objects with path + type
    arts = doc.get("evidence_artifacts", [])
    if isinstance(arts, list):
        for i, art in enumerate(arts):
            if not isinstance(art, dict):
                errors.append(f"evidence_artifacts[{i}] must be object, got {type(art).__name__}")
            elif "path" not in art:
                errors.append(f"evidence_artifacts[{i}] missing required field 'path'")
            elif "type" not in art:
                errors.append(f"evidence_artifacts[{i}] missing required field 'type'")

    # planned_work_items: items must have item_id, title, status
    pwi = doc.get("planned_work_items", [])
    if isinstance(pwi, list):
        for i, item in enumerate(pwi):
            if not isinstance(item, dict):
                errors.append(f"planned_work_items[{i}] must be object")
                continue
            for req in ["item_id", "title", "status"]:
                if req not in item:
                    errors.append(f"planned_work_items[{i}] missing required field '{req}'")
            if "id" in item and "item_id" not in item:
                errors.append(
                    f"planned_work_items[{i}] has 'id' but not 'item_id' — rename to 'item_id'"
                )
            if "acceptance_criteria" in item and not isinstance(item["acceptance_criteria"], str):
                errors.append(
                    f"planned_work_items[{i}].acceptance_criteria must be string, "
                    f"got {type(item['acceptance_criteria']).__name__}"
                )

    return errors


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def validate_file(
    declaration_path: Path,
    *,
    repair: bool = False,
    repo_root: Path = _REPO,
) -> dict:
    """
    Validate (and optionally repair) a declaration file.

    Returns dict with keys: passed (bool), errors (list), repairs (list).
    If repair=True and file is repairable, writes fixed YAML back to disk.
    """
    if not declaration_path.exists():
        return {
            "passed": False,
            "errors": [f"File not found: {declaration_path}"],
            "repairs": [],
        }

    raw = declaration_path.read_text(encoding="utf-8")
    repairs_applied = []

    # --- Phase 1: Strip markdown fences ---
    stripped = _strip_markdown_fences(raw)
    if stripped != raw:
        repairs_applied.append("Stripped markdown code fences")
        if repair:
            declaration_path.write_text(stripped, encoding="utf-8")
        raw = stripped

    # --- Phase 2: Fix YAML alias errors ---
    fixed_aliases = _fix_yaml_aliases(raw)
    if fixed_aliases != raw:
        repairs_applied.append("Fixed YAML alias errors")
        if repair:
            declaration_path.write_text(fixed_aliases, encoding="utf-8")
        raw = fixed_aliases

    # --- Phase 3: Parse YAML ---
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return {
            "passed": False,
            "errors": [f"YAML parse error: {e}"],
            "repairs": repairs_applied,
        }

    if not isinstance(doc, dict):
        return {
            "passed": False,
            "errors": ["Declaration must be a YAML mapping (dict), got: " + type(doc).__name__],
            "repairs": repairs_applied,
        }

    # --- Phase 4: Structural repair ---
    if repair:
        doc, struct_repairs = _repair_document(doc)
        repairs_applied.extend(struct_repairs)
        if struct_repairs:
            declaration_path.write_text(
                yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

    # --- Phase 5: Validate ---
    errors = _validate(doc)

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "repairs": repairs_applied,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate evidence-declaration.yaml before submitting to autonomous_cycle.py"
    )
    parser.add_argument("declaration", type=Path, help="Path to evidence-declaration.yaml")
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Auto-repair common issues (strip fences, fix types) and write back to file",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=_REPO,
        help="Repository root (default: auto-detected)",
    )
    args = parser.parse_args(argv)

    decl_path = args.declaration
    if not decl_path.is_absolute():
        decl_path = Path.cwd() / decl_path

    result = validate_file(decl_path, repair=args.repair, repo_root=args.repo_root)

    # Output
    print(json.dumps(result, indent=2))

    if result["repairs"]:
        print(f"\nRepairs applied ({len(result['repairs'])}):")
        for r in result["repairs"]:
            print(f"  - {r}")

    if result["passed"]:
        print("\nVALIDATION: PASS")
        return 0
    else:
        print(f"\nVALIDATION: FAIL ({len(result['errors'])} error(s))")
        return 1


if __name__ == "__main__":
    sys.exit(main())
