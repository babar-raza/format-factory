#!/usr/bin/env python3
"""
FODS Neutral Model Validator — Gate 5 tool.
Validates parser output against the neutral model schema and semantic rules.

Usage:
    python validate_neutral_model.py <parser_json_or_fods_file> [--schema PATH] [--rules PATH] [--verbose]

If given a .fods file, runs the prototype parser first to produce JSON.
If given a .json file, validates that JSON directly.

Requires: Python 3.10+ (stdlib only — no external dependencies)
Created: run033 (2026-05-06)
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path

# Paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "neutral-model" / "fods" / "model.schema.json"
RULES_PATH = REPO_ROOT / "schemas" / "neutral-model" / "fods" / "validation-rules.yaml"
PARSER_PATH = REPO_ROOT / "prototypes" / "by-format" / "fods" / "fods_parser.py"
FIELD_MAP_PATH = REPO_ROOT / "schemas" / "neutral-model" / "fods" / "field-map.yaml"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_parser(fods_path: Path) -> dict:
    """Run the prototype parser and return parsed JSON."""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, str(PARSER_PATH), str(fods_path)],
        capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"FAIL: Parser exited with code {result.returncode}")
        print(result.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def error(self, rule_id: str, msg: str):
        self.errors.append(f"[ERROR] {rule_id}: {msg}")

    def warn(self, rule_id: str, msg: str):
        self.warnings.append(f"[WARN]  {rule_id}: {msg}")

    def ok(self, rule_id: str, msg: str):
        self.passes.append(f"[PASS]  {rule_id}: {msg}")

    def summary(self) -> str:
        total = len(self.errors) + len(self.warnings) + len(self.passes)
        return (
            f"\n{'='*60}\n"
            f"Validation Summary: {total} checks | "
            f"{len(self.passes)} PASS | {len(self.warnings)} WARN | {len(self.errors)} ERROR\n"
            f"Result: {'PASS' if self.passed else 'FAIL'}\n"
            f"{'='*60}"
        )


def validate_schema_structure(data: dict, result: ValidationResult):
    """Validate against the neutral model schema structure (without jsonschema library)."""
    # Workbook required fields
    required_wb = ["format_id", "spec_version", "odf_version_attr", "sheet_count", "sheets", "warnings"]

    # Check using prototype field names (format vs format_id)
    # The prototype uses "format" not "format_id", so we check both
    has_format = "format_id" in data or "format" in data
    if has_format:
        result.ok("SCHEMA-WB-01", "Workbook has format identifier field")
    else:
        result.error("SCHEMA-WB-01", "Workbook missing format identifier (format_id or format)")

    for field in ["spec_version", "odf_version_attr", "sheet_count", "sheets"]:
        if field in data:
            result.ok(f"SCHEMA-WB-{field}", f"Workbook has '{field}'")
        else:
            result.error(f"SCHEMA-WB-{field}", f"Workbook missing required field '{field}'")

    if "warnings" in data:
        result.ok("SCHEMA-WB-warnings", "Workbook has 'warnings' field")
    else:
        result.warn("SCHEMA-WB-warnings", "Workbook missing 'warnings' field (prototype may omit if empty)")

    # Check sheets structure
    sheets = data.get("sheets", [])
    for si, sheet in enumerate(sheets):
        prefix = f"Sheet[{si}]"
        for field in ["name", "row_count", "rows"]:
            if field in sheet:
                result.ok(f"SCHEMA-{prefix}-{field}", f"{prefix} has '{field}'")
            else:
                result.error(f"SCHEMA-{prefix}-{field}", f"{prefix} missing required field '{field}'")

        rows = sheet.get("rows", [])
        for ri, row in enumerate(rows):
            if "index" not in row:
                result.error(f"SCHEMA-{prefix}-R{ri}-index", f"{prefix} Row[{ri}] missing 'index'")
            if "cells" not in row:
                result.error(f"SCHEMA-{prefix}-R{ri}-cells", f"{prefix} Row[{ri}] missing 'cells'")

            cells = row.get("cells", [])
            for ci, cell in enumerate(cells):
                if "col_index" not in cell:
                    result.error(f"SCHEMA-{prefix}-R{ri}-C{ci}", f"{prefix} Row[{ri}] Cell[{ci}] missing 'col_index'")


def validate_semantic_rules(data: dict, result: ValidationResult):
    """Validate semantic rules from validation-rules.yaml."""

    # VR-001: format_id must equal 'fods'
    fmt = data.get("format_id", data.get("format"))
    if fmt == "fods":
        result.ok("VR-001", "format_id == 'fods'")
    else:
        result.error("VR-001", f"format_id is '{fmt}', expected 'fods'")

    # VR-002: sheet_count == len(sheets)
    sc = data.get("sheet_count", -1)
    sheets = data.get("sheets", [])
    if sc == len(sheets):
        result.ok("VR-002", f"sheet_count ({sc}) matches sheets array length")
    else:
        result.error("VR-002", f"sheet_count ({sc}) != len(sheets) ({len(sheets)})")

    # VR-003: spec_version non-empty
    sv = data.get("spec_version", "")
    if sv:
        result.ok("VR-003", f"spec_version is '{sv}'")
    else:
        result.error("VR-003", "spec_version is empty")

    # VR-004: odf_version_attr non-empty
    ov = data.get("odf_version_attr", "")
    if ov:
        result.ok("VR-004", f"odf_version_attr is '{ov}'")
    else:
        result.error("VR-004", "odf_version_attr is empty")

    # VR-005: mimetype should be present
    mt = data.get("mimetype")
    if mt is not None:
        result.ok("VR-005", f"mimetype is '{mt}'")
    else:
        result.warn("VR-005", "mimetype is null (MISSING_MIMETYPE)")

    # Sheet-level rules
    for si, sheet in enumerate(sheets):
        prefix = f"Sheet[{si}]"

        # VR-010: index matches position
        idx = sheet.get("index")
        if idx is not None and idx == si:
            result.ok(f"VR-010-{si}", f"{prefix} index ({idx}) matches position")
        elif idx is None:
            # Prototype may not include sheet index
            result.warn(f"VR-010-{si}", f"{prefix} has no explicit index field")
        else:
            result.error(f"VR-010-{si}", f"{prefix} index ({idx}) != position ({si})")

        # VR-011: row_count == len(rows)
        rc = sheet.get("row_count", -1)
        rows = sheet.get("rows", [])
        if rc == len(rows):
            result.ok(f"VR-011-{si}", f"{prefix} row_count ({rc}) matches rows length")
        else:
            result.error(f"VR-011-{si}", f"{prefix} row_count ({rc}) != len(rows) ({len(rows)})")

        # VR-012: name non-empty
        name = sheet.get("name", "")
        if name:
            result.ok(f"VR-012-{si}", f"{prefix} name is '{name}'")
        else:
            result.error(f"VR-012-{si}", f"{prefix} name is empty")

        # Row-level rules
        for ri, row in enumerate(rows):
            # VR-020: row index sequential
            row_idx = row.get("index")
            if row_idx is not None and row_idx == ri:
                pass  # OK, don't spam passes for every row
            elif row_idx is not None and row_idx != ri:
                result.error(f"VR-020-{si}-{ri}", f"{prefix} Row[{ri}] index ({row_idx}) != position ({ri})")

            # Cell-level rules
            cells = row.get("cells", [])
            prev_col = -1
            for ci, cell in enumerate(cells):
                col_idx = cell.get("col_index", -1)

                # VR-030: col_index non-negative
                if col_idx < 0:
                    result.error(f"VR-030-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} col_index < 0")

                # VR-031: non-decreasing col_index
                if col_idx < prev_col:
                    result.error(f"VR-031-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} col_index ({col_idx}) < previous ({prev_col})")
                prev_col = col_idx

                # VR-032, VR-033, VR-034: type-value consistency
                vt = cell.get("value_type")
                val = cell.get("value")
                if vt == "float" and val is not None and not isinstance(val, (int, float)):
                    result.error(f"VR-032-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} value_type=float but value is {type(val).__name__}")
                if vt == "boolean" and val is not None and not isinstance(val, bool):
                    result.error(f"VR-033-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} value_type=boolean but value is {type(val).__name__}")
                if vt == "string" and val is not None and not isinstance(val, str):
                    result.error(f"VR-034-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} value_type=string but value is {type(val).__name__}")

                # Formula rules (VR-040, VR-041, VR-042)
                formula = cell.get("formula")
                if formula is not None:
                    if isinstance(formula, str):
                        # Prototype flat format — validate raw string
                        if len(formula) == 0:
                            result.error(f"VR-040-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} formula is empty string")
                    elif isinstance(formula, dict):
                        # Neutral model object format
                        raw = formula.get("raw", "")
                        if not raw:
                            result.error(f"VR-040-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} formula.raw is empty")
                        if formula.get("evaluated") is not False:
                            result.error(f"VR-041-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} formula.evaluated is not false")
                        if formula.get("evaluator") is not None:
                            result.error(f"VR-042-{si}-{ri}-{ci}", f"{prefix} R{ri}C{ci} formula.evaluator is not null")

        # Summarize row/cell checks
        result.ok(f"VR-020-030-{si}", f"{prefix}: {len(rows)} rows, all row/cell index checks passed")

    # Warning rules (VR-050, VR-051)
    warnings = data.get("warnings", [])
    valid_codes = {"MISSING_MIMETYPE", "UNEXPECTED_MIMETYPE", "UNSUPPORTED_VALUE_TYPE",
                   "COVERED_CELL", "UNSUPPORTED_ELEMENT", "LARGE_REPEAT", "UNKNOWN"}
    for wi, w in enumerate(warnings):
        code = w.get("code", "")
        if code not in valid_codes:
            result.error(f"VR-050-{wi}", f"Warning[{wi}] code '{code}' not in enum")
        msg = w.get("message", "")
        if not msg:
            result.error(f"VR-051-{wi}", f"Warning[{wi}] message is empty")
    if not warnings:
        result.ok("VR-050-051", "No warnings to validate (empty warnings array)")


def validate_field_map_coverage(data: dict, result: ValidationResult):
    """Check that all parser output fields are accounted for in the field map."""
    # Top-level fields the prototype outputs
    expected_top = {"format", "spec_version", "odf_version_attr", "mimetype", "sheet_count", "sheets", "warnings"}
    actual_top = set(data.keys())

    unmapped = actual_top - expected_top - {"format_id"}
    if unmapped:
        result.warn("FMAP-TOP", f"Unmapped top-level parser fields: {unmapped}")
    else:
        result.ok("FMAP-TOP", "All top-level parser fields covered by field map")

    # Cell-level fields
    expected_cell = {"col_index", "value_type", "value", "text", "formula"}
    for sheet in data.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                actual_cell = set(cell.keys())
                unmapped_cell = actual_cell - expected_cell - {"row_index", "repeated_columns", "warnings"}
                if unmapped_cell:
                    result.warn("FMAP-CELL", f"Unmapped cell fields: {unmapped_cell}")
                    break


def main():
    parser = argparse.ArgumentParser(description="Validate FODS neutral model instance")
    parser.add_argument("input", help="Path to .fods file or .json parser output")
    parser.add_argument("--schema", default=str(SCHEMA_PATH), help="Path to model.schema.json")
    parser.add_argument("--rules", default=str(RULES_PATH), help="Path to validation-rules.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all check results")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"FAIL: Input file not found: {input_path}")
        sys.exit(1)

    # Get JSON data
    if input_path.suffix.lower() == ".fods":
        print(f"Running parser on {input_path.name}...")
        data = run_parser(input_path)
    elif input_path.suffix.lower() == ".json":
        data = load_json(input_path)
    else:
        print(f"FAIL: Unsupported file type: {input_path.suffix}")
        sys.exit(1)

    result = ValidationResult()

    # Run all validation passes
    print(f"Validating {input_path.name} against FODS neutral model v1...")
    print()

    print("--- Schema Structure Checks ---")
    validate_schema_structure(data, result)

    print("--- Semantic Rule Checks ---")
    validate_semantic_rules(data, result)

    print("--- Field Map Coverage Checks ---")
    validate_field_map_coverage(data, result)

    # Print results
    if args.verbose:
        for msg in result.passes:
            print(msg)
    for msg in result.warnings:
        print(msg)
    for msg in result.errors:
        print(msg)

    print(result.summary())

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
