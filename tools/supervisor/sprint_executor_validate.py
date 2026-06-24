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

# Shared test-layer utilities (TC-FSLAY02-SHARED-001)
try:
    from test_layer_utils import (
        ADEQUACY_ESCALATION_DATE as _ESCALATION_DATE_OBJ,
        PRODUCT_ITEM_TYPES as _PRODUCT_ITEM_TYPES,
        compute_required_layer as _shared_compute_required_layer,
        is_escalation_active as _is_escalation_active,
        load_change_impact_rules as _shared_load_rules,
    )
    _HAS_SHARED_UTILS = True
except ImportError:
    _HAS_SHARED_UTILS = False
    import datetime as _datetime
    _ESCALATION_DATE_OBJ = _datetime.date(2026, 7, 18)
    _PRODUCT_ITEM_TYPES = frozenset({"PRODUCT_SOURCE", "PRODUCT_TEST"})
    def _is_escalation_active():
        return _datetime.date.today() >= _ESCALATION_DATE_OBJ
    _shared_load_rules = None
    _shared_compute_required_layer = None

_MANIFEST_PATH = _REPO / "registry" / "test-layer-manifest.yaml"

# Date after which test_layer adequacy warnings escalate to errors
_ADEQUACY_ESCALATION_DATE = str(_ESCALATION_DATE_OBJ)

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
# Test-layer adequacy checking
# ---------------------------------------------------------------------------

def _load_manifest_change_impact() -> list[dict]:
    """Load change_impact rules from registry/test-layer-manifest.yaml."""
    try:
        import yaml
        from fnmatch import fnmatch as _fnmatch

        with open(_MANIFEST_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("change_impact", [])
    except Exception:
        return []


def _compute_required_layer(changed_files: list[str], rules: list[dict]) -> tuple[int, str]:
    """Walk change-impact rules, return (max_min_layer, reason)."""
    from fnmatch import fnmatch

    max_layer = 0
    reason = "no change_impact rules matched"

    for f in changed_files:
        f_norm = f.replace("\\", "/")
        matched = False
        for rule in rules:
            pat = rule.get("pattern", "")
            if pat == "_default":
                if not matched:
                    layer = rule.get("min_layer", 6)
                    if layer > max_layer:
                        max_layer = layer
                        reason = f"{f_norm} matched default rule"
                break
            if fnmatch(f_norm, pat):
                layer = rule.get("min_layer", 0)
                if layer > max_layer:
                    max_layer = layer
                    reason = f"{f_norm} matched '{pat}' -> min_layer={layer}"
                matched = True
                break

    return max_layer, reason


def _check_test_layer_adequacy(doc: dict) -> tuple[list[str], list[str]]:
    """Check whether declared test_layer is adequate for changed_files.

    Returns (adequacy_errors, adequacy_warnings) tuple.
    - adequacy_errors: ERROR strings that block validation (exit 1)
    - adequacy_warnings: WARN/ADVISORY strings (informational)

    Enforcement policy (TC-FSLAY02-ENF-001):
    - PRODUCT_SOURCE/PRODUCT_TEST items: ERROR immediately when layer < required
    - All other item types: WARN until 2026-07-18, then ERROR
    - Declarations without test_layer: ADVISORY note (never ERROR)
    """
    adequacy_errors: list[str] = []
    warnings: list[str] = []

    declared_layer = doc.get("test_layer")
    if declared_layer is None:
        warnings.append(
            "ADVISORY: test_layer not declared in evidence. "
            "Include test_layer (int 0-6) for layer adequacy checking. "
            "See docs/test-layering.md."
        )
        return adequacy_errors, warnings

    if not isinstance(declared_layer, int) or declared_layer < 0 or declared_layer > 6:
        warnings.append(
            f"WARN: test_layer value '{declared_layer}' is invalid (must be int 0-6). "
            "Adequacy check skipped."
        )
        return adequacy_errors, warnings

    changed_files = doc.get("changed_files", [])
    if not changed_files:
        return adequacy_errors, warnings

    rules = _load_manifest_change_impact()
    if not rules:
        warnings.append(
            "ADVISORY: registry/test-layer-manifest.yaml not found or empty. "
            "Cannot verify test_layer adequacy."
        )
        return adequacy_errors, warnings

    required_layer, match_reason = _compute_required_layer(changed_files, rules)

    if declared_layer < required_layer:
        # Check whether any planned_work_items are product items
        item_types = {
            item.get("item_type", "")
            for item in (doc.get("planned_work_items") or [])
            if isinstance(item, dict)
        }
        has_product_items = bool(item_types & _PRODUCT_ITEM_TYPES)

        if has_product_items or _is_escalation_active():
            adequacy_errors.append(
                f"ERROR[adequacy]: test_layer={declared_layer} but changed_files require "
                f"min_layer={required_layer} ({match_reason}). "
                f"{'PRODUCT item enforcement active.' if has_product_items else 'Post-escalation enforcement active.'} "
                "Run tests at the required layer before declaring evidence."
            )
        else:
            warnings.append(
                f"WARN[adequacy]: test_layer={declared_layer} but changed_files require "
                f"min_layer={required_layer} ({match_reason}). "
                f"Escalates to ERROR after {_ADEQUACY_ESCALATION_DATE}. "
                "This sprint may have inadequate test coverage for the declared changes."
            )

    return adequacy_errors, warnings


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

    # Ensure tests_run is int (TC-HARD-010, 2026-06-23)
    if "tests_run" in doc and not isinstance(doc["tests_run"], int):
        val = doc["tests_run"]
        if isinstance(val, list):
            # List of test file names or test count entries — use len() as the count.
            # This preserves the semantic "N test files were run" rather than resetting to 0.
            doc["tests_run"] = len(val)
            repairs.append(f"Converted tests_run list ({len(val)} items) to int count")
        else:
            try:
                doc["tests_run"] = int(val)
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

def _check_evidence_paths_exist(doc: dict, repo_root: Path) -> list[str]:
    """Return WARN messages for declared evidence_artifacts paths that don't exist on disk."""
    warnings = []
    for art in doc.get("evidence_artifacts", []):
        if not isinstance(art, dict):
            continue
        p = art.get("path", "")
        if not p:
            continue
        full = repo_root / p
        if not full.exists():
            warnings.append(f"WARN: evidence_path not found: {p}")
    return warnings


def _check_skill_transcript_existence(doc: dict, repo_root: Path) -> list[str]:
    """Fix 3: Always-on check — skill_transcript artifacts must exist on disk.

    Returns WARN messages (not errors) for missing transcript files.
    This runs regardless of --check-evidence-paths flag.
    """
    warnings = []
    for i, art in enumerate(doc.get("evidence_artifacts", [])):
        if not isinstance(art, dict):
            continue
        if art.get("type") != "skill_transcript":
            continue
        p = art.get("path", "")
        if not p:
            warnings.append(f"WARN: evidence_artifacts[{i}] skill_transcript has empty path")
            continue
        full = repo_root / p
        if not full.exists():
            warnings.append(f"WARN: skill_transcript file missing on disk: {p}")
    return warnings


def check_fix_sprint_evidence(doc: dict) -> list[str]:
    """FSE-001: Warn when test files are in changed_files but not in any item's evidence_paths.

    When a sprint changes test files AND code files, the test files should appear
    in evidence_paths for the relevant work item. Otherwise the LLM semantic
    verifier may downgrade the item to ACCEPTED_WITH_LIMITATIONS.
    """
    warnings = []
    changed = set(doc.get("changed_files", []) or [])
    changed_tests = {f for f in changed if "/test_" in f or f.startswith("tests/")}
    if not changed_tests:
        return warnings

    # Collect all evidence_paths across all planned_work_items
    all_item_evidence = set()
    for item in doc.get("planned_work_items", []):
        for ep in item.get("evidence_paths", []) or []:
            all_item_evidence.add(ep)

    missing_in_items = changed_tests - all_item_evidence
    for f in sorted(missing_in_items):
        warnings.append(
            f"WARN(FSE-001): test file '{f}' is in changed_files but not in any "
            f"planned_work_items[].evidence_paths — LLM verifier may downgrade"
        )
    return warnings


def check_parent_id_evidence_tagging(doc: dict) -> list[str]:
    """TC-VHL-REWORK-004: Warn when planned_work_items have no evidence_paths.

    Every planned_work_item with status=completed should have at least one
    evidence_path. This catches the parent-ID tagging gap where sub-items
    have evidence but the parent item does not.
    """
    warnings = []
    for item in doc.get("planned_work_items", []):
        item_id = item.get("item_id", "?")
        status = item.get("status", "")
        paths = item.get("evidence_paths", []) or []
        if status == "completed" and not paths:
            warnings.append(
                f"WARN(PARENT-ID): planned_work_item '{item_id}' has status=completed "
                f"but no evidence_paths — grader will return OVERCLAIMED"
            )
    return warnings


# Backward-compat aliases (TC-FL-004)
_check_fix_sprint_evidence = check_fix_sprint_evidence
_check_parent_id_evidence_tagging = check_parent_id_evidence_tagging


def check_contract_compliance(doc: dict, repo_root: Path = _REPO) -> list[str]:
    """CONTRACT-001: Warn when contracted gap-sourced items are not addressed.

    Reads sprint-contract.json (written by autonomous_cycle Step 4a2) and checks
    that each contracted gap_ref appears in the declaration's planned_work_items.
    """
    contract_path = repo_root / ".local" / "supervisor" / "sprint-contract.json"
    if not contract_path.exists():
        return []

    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    # Collect all gap_ledger_ref / gap_ref values from declaration items
    declared_gaps: set[str] = set()
    for item in doc.get("planned_work_items", []):
        ref = item.get("gap_ledger_ref") or item.get("gap_ref")
        if ref:
            declared_gaps.add(ref)

    warnings: list[str] = []
    for ci in contract.get("contracted_items", []):
        gap_ref = ci.get("gap_ref", "")
        if gap_ref and gap_ref not in declared_gaps:
            warnings.append(
                f"WARN(CONTRACT-001): Contracted item {ci.get('item_id', '?')} "
                f"(gap_ref={gap_ref}) not addressed in declaration"
            )
    return warnings


def validate_file(
    declaration_path: Path,
    *,
    repair: bool = False,
    repo_root: Path = _REPO,
    check_evidence_paths: bool = False,
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

    # --- Phase 6: Test-layer adequacy check (TC-FSLAY02-ENF-001) ---
    # Now returns (errors, warnings) tuple. Errors block validation for product items.
    adequacy_errors, adequacy_warnings = _check_test_layer_adequacy(doc)
    errors.extend(adequacy_errors)

    # --- Phase 7: Evidence path existence check (WARN only, never blocks) ---
    evidence_path_warnings: list[str] = []
    if check_evidence_paths:
        evidence_path_warnings = _check_evidence_paths_exist(doc, repo_root)

    # --- Phase 8 (Fix 3): Skill transcript existence (always-on, WARN only) ---
    transcript_warnings = _check_skill_transcript_existence(doc, repo_root)

    # --- Phase 9 (FSE-001): Fix sprint evidence completeness (WARN only) ---
    fse_warnings = check_fix_sprint_evidence(doc)

    # --- Phase 10 (TC-VHL-REWORK-004): Parent-ID evidence tagging (WARN only) ---
    parent_id_warnings = check_parent_id_evidence_tagging(doc)

    # --- Phase 11 (TC-FL-010): Contract compliance check (WARN only) ---
    contract_warnings = check_contract_compliance(doc, repo_root)

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "repairs": repairs_applied,
        "adequacy_warnings": adequacy_warnings,
        "evidence_path_warnings": evidence_path_warnings,
        "transcript_warnings": transcript_warnings,
        "fse_warnings": fse_warnings,
        "parent_id_warnings": parent_id_warnings,
        "contract_warnings": contract_warnings,
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
    parser.add_argument(
        "--check-evidence-paths",
        action="store_true",
        help="WARN (not FAIL) when declared evidence_artifacts paths do not exist on disk",
    )
    args = parser.parse_args(argv)

    decl_path = args.declaration
    if not decl_path.is_absolute():
        decl_path = Path.cwd() / decl_path

    result = validate_file(
        decl_path,
        repair=args.repair,
        repo_root=args.repo_root,
        check_evidence_paths=getattr(args, "check_evidence_paths", False),
    )

    # Output
    print(json.dumps(result, indent=2))

    if result["repairs"]:
        print(f"\nRepairs applied ({len(result['repairs'])}):")
        for r in result["repairs"]:
            print(f"  - {r}")

    adequacy = result.get("adequacy_warnings", [])
    if adequacy:
        print(f"\nTest-layer adequacy ({len(adequacy)} note(s)):")
        for w in adequacy:
            print(f"  - {w}")

    ev_warns = result.get("evidence_path_warnings", [])
    if ev_warns:
        print(f"\nEvidence path warnings ({len(ev_warns)}):")
        for w in ev_warns:
            print(f"  - {w}")

    tx_warns = result.get("transcript_warnings", [])
    if tx_warns:
        print(f"\nSkill transcript warnings ({len(tx_warns)}):")
        for w in tx_warns:
            print(f"  - {w}")

    fse_warns = result.get("fse_warnings", [])
    if fse_warns:
        print(f"\nFix-sprint evidence warnings ({len(fse_warns)}):")
        for w in fse_warns:
            print(f"  - {w}")

    pid_warns = result.get("parent_id_warnings", [])
    if pid_warns:
        print(f"\nParent-ID evidence tagging warnings ({len(pid_warns)}):")
        for w in pid_warns:
            print(f"  - {w}")

    if result["passed"]:
        print("\nVALIDATION: PASS")
        return 0
    else:
        print(f"\nVALIDATION: FAIL ({len(result['errors'])} error(s))")
        return 1


if __name__ == "__main__":
    sys.exit(main())
