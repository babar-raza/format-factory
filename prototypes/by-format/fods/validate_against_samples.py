"""
validate_against_samples.py — Gate 4 validation: run fods_parser against all 4 FODS samples.

Gate 4 prototype validation — format-factory project.
Evidence artifact: prototypes/by-format/fods/validate_against_samples.py

Validates parser output against the expected values defined in:
  acquisition-packs/fods/parser-test-plan.md

Acceptance oracle is derived from actual sample content, not the test plan
planning predictions. Discrepancies between actual sample content and test plan
predictions are documented in acquisition-packs/fods/parser-notes.md.

Usage:
  python validate_against_samples.py [--samples-dir <path>] [--output <report.json>]

Default samples-dir: samples/by-format/fods/ (relative to repo root)

No network access. No file writes unless --output is specified.
License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-05 (run029)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Allow running from either the prototypes/by-format/fods/ directory or repo root
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent.parent  # prototypes/by-format/fods -> repo root

sys.path.insert(0, str(_HERE))
from fods_parser import parse_fods, EXPECTED_MIMETYPE

# ---------------------------------------------------------------------------
# Expected sample SHA-256 hashes (from run027 verification)
# ---------------------------------------------------------------------------
EXPECTED_HASHES: dict[str, str] = {
    "minimal-spreadsheet.fods": "a790b18a811c47d634603ad0dd3e42c41c102a36c74b6349b46b9770a2825543",
    "multi-sheet-basic.fods":   "669b60befc7206a08578815e781ff72526c98d07be53f20e37f062b73b7dcc41",
    "typed-values-basic.fods":  "c873322d69fa93ff64519a37a5f87f4efc9cd244a18488f03adc342524e51977",
    "formula-basic.fods":       "72b065415748db3e3c7796608f50b488db6d23b2439d2468baf88ea41b38db1e",
}

# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

def _check(results: list[dict], name: str, passed: bool, detail: str = "") -> None:
    results.append({"assertion": name, "passed": passed, "detail": detail})


def _find_cells_by_type(sheets: list[dict], value_type: str) -> list[dict]:
    """Return all cells across all sheets with the given value_type."""
    found = []
    for sheet in sheets:
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell.get("value_type") == value_type:
                    found.append(cell)
    return found


def _find_formula_cells(sheets: list[dict]) -> list[dict]:
    """Return all cells that have a non-null formula."""
    found = []
    for sheet in sheets:
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell.get("formula") is not None:
                    found.append(cell)
    return found


# ---------------------------------------------------------------------------
# Per-sample test functions
# ---------------------------------------------------------------------------

def test_pt001_minimal(parsed: dict) -> list[dict]:
    """PT-001: minimal-spreadsheet.fods — 1 sheet, 1 cell, string value.

    Note: Test plan (run028) predicted text='Hello, World!'.
    Actual sample content: text='Hello'.
    Discrepancy recorded; test validates actual content.
    """
    results: list[dict] = []

    _check(results, "no_parse_error", "error" not in parsed,
           parsed.get("error", ""))
    if "error" in parsed:
        return results

    _check(results, "sheet_count_is_1", parsed.get("sheet_count") == 1,
           f"sheet_count={parsed.get('sheet_count')}")
    _check(results, "sheet0_name_is_Sheet1", parsed["sheets"][0]["name"] == "Sheet1",
           f"name={parsed['sheets'][0]['name']!r}")
    _check(results, "mimetype_correct",
           parsed.get("mimetype") == EXPECTED_MIMETYPE,
           f"mimetype={parsed.get('mimetype')!r}")

    sheet = parsed["sheets"][0]
    rows = sheet.get("rows", [])
    _check(results, "has_at_least_1_row", len(rows) >= 1,
           f"row_count={len(rows)}")

    if rows:
        cells = rows[0].get("cells", [])
        _check(results, "row0_has_cells", len(cells) >= 1,
               f"cell_count={len(cells)}")
        if cells:
            c0 = cells[0]
            _check(results, "cell0_value_type_string",
                   c0.get("value_type") == "string",
                   f"value_type={c0.get('value_type')!r}")
            # Actual sample has 'Hello'; test plan predicted 'Hello, World!'
            # Testing against actual sample content
            _check(results, "cell0_text_is_Hello",
                   c0.get("text") == "Hello",
                   f"text={c0.get('text')!r} (plan predicted 'Hello, World!' — sample has 'Hello')")

    return results


def test_pt002_multisheet(parsed: dict) -> list[dict]:
    """PT-002: multi-sheet-basic.fods — 2 sheets, cells in each.

    Note: Test plan predicted sheet names 'Sheet1', 'Sheet2'.
    Actual sample content: 'Data' and 'Summary'.
    Discrepancy recorded; test validates actual content.
    """
    results: list[dict] = []

    _check(results, "no_parse_error", "error" not in parsed,
           parsed.get("error", ""))
    if "error" in parsed:
        return results

    _check(results, "sheet_count_is_2", parsed.get("sheet_count") == 2,
           f"sheet_count={parsed.get('sheet_count')}")

    if parsed.get("sheet_count", 0) >= 2:
        names = [s["name"] for s in parsed["sheets"]]
        _check(results, "sheet0_name_is_Data", names[0] == "Data",
               f"names={names!r} (plan predicted 'Sheet1' — sample has 'Data')")
        _check(results, "sheet1_name_is_Summary", names[1] == "Summary",
               f"names={names!r} (plan predicted 'Sheet2' — sample has 'Summary')")

        for i, sheet in enumerate(parsed["sheets"]):
            rows = sheet.get("rows", [])
            has_nonempty = any(
                any(c.get("value_type") is not None or c.get("text") for c in row.get("cells", []))
                for row in rows
            )
            _check(results, f"sheet{i}_has_nonempty_cell", has_nonempty,
                   f"sheet={sheet['name']!r} row_count={len(rows)}")

    return results


def test_pt003_typed_values(parsed: dict) -> list[dict]:
    """PT-003: typed-values-basic.fods — string, float, boolean cells present.

    Note: Test plan (run028) also predicted 'date' type.
    Actual sample content: no date cells (string, float, boolean only).
    Discrepancy recorded; test validates types actually present.
    """
    results: list[dict] = []

    _check(results, "no_parse_error", "error" not in parsed,
           parsed.get("error", ""))
    if "error" in parsed:
        return results

    _check(results, "sheet_count_at_least_1", parsed.get("sheet_count", 0) >= 1,
           f"sheet_count={parsed.get('sheet_count')}")

    sheets = parsed.get("sheets", [])

    string_cells = _find_cells_by_type(sheets, "string")
    _check(results, "has_string_cells", len(string_cells) > 0,
           f"string_cell_count={len(string_cells)}")

    float_cells = _find_cells_by_type(sheets, "float")
    _check(results, "has_float_cells", len(float_cells) > 0,
           f"float_cell_count={len(float_cells)}")
    if float_cells:
        _check(results, "float_cell_has_numeric_value",
               isinstance(float_cells[0].get("value"), (int, float)),
               f"value={float_cells[0].get('value')!r}")

    bool_cells = _find_cells_by_type(sheets, "boolean")
    _check(results, "has_boolean_cells", len(bool_cells) > 0,
           f"boolean_cell_count={len(bool_cells)}")
    if bool_cells:
        _check(results, "boolean_cell_value_is_bool",
               isinstance(bool_cells[0].get("value"), bool),
               f"value={bool_cells[0].get('value')!r}")

    # Date not present in actual sample — recorded as expected-absent
    date_cells = _find_cells_by_type(sheets, "date")
    _check(results, "date_cells_absent_as_expected_in_actual_sample",
           len(date_cells) == 0,
           f"date_cell_count={len(date_cells)} "
           "(test plan predicted date cells; actual sample has none — documented in parser-notes.md)")

    return results


def test_pt004_formula(parsed: dict) -> list[dict]:
    """PT-004: formula-basic.fods — formula cell with cached value."""
    results: list[dict] = []

    _check(results, "no_parse_error", "error" not in parsed,
           parsed.get("error", ""))
    if "error" in parsed:
        return results

    _check(results, "sheet_count_at_least_1", parsed.get("sheet_count", 0) >= 1,
           f"sheet_count={parsed.get('sheet_count')}")

    sheets = parsed.get("sheets", [])
    formula_cells = _find_formula_cells(sheets)

    _check(results, "has_formula_cells", len(formula_cells) > 0,
           f"formula_cell_count={len(formula_cells)}")

    if formula_cells:
        fc = formula_cells[0]
        _check(results, "formula_starts_with_oooc_or_of",
               bool(fc.get("formula", "").startswith(("oooc:=", "of:="))),
               f"formula={fc.get('formula')!r}")
        _check(results, "formula_cell_has_cached_value",
               fc.get("value") is not None,
               f"value={fc.get('value')!r}")
        _check(results, "formula_cell_value_type_float",
               fc.get("value_type") == "float",
               f"value_type={fc.get('value_type')!r}")
        _check(results, "formula_not_evaluated_raw_string",
               isinstance(fc.get("formula"), str),
               f"formula type={type(fc.get('formula')).__name__}")
        # Verify cached value is 60 (SUM of 10+20+30)
        _check(results, "cached_value_is_60",
               fc.get("value") == 60.0,
               f"value={fc.get('value')!r}")

    return results


# ---------------------------------------------------------------------------
# Hash verification
# ---------------------------------------------------------------------------

def verify_hash(file_path: Path, expected_hex: str) -> bool:
    with open(file_path, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    return actual == expected_hex


# ---------------------------------------------------------------------------
# Main validation runner
# ---------------------------------------------------------------------------

def run_validation(samples_dir: Path) -> dict:
    """Run all PT-001 through PT-004 tests. Return full report dict."""
    test_cases = [
        ("PT-001", "minimal-spreadsheet.fods",  test_pt001_minimal),
        ("PT-002", "multi-sheet-basic.fods",     test_pt002_multisheet),
        ("PT-003", "typed-values-basic.fods",    test_pt003_typed_values),
        ("PT-004", "formula-basic.fods",         test_pt004_formula),
    ]

    overall_pass = True
    test_results = []
    parser_outputs = {}

    for test_id, filename, test_fn in test_cases:
        file_path = samples_dir / filename
        test_entry: dict = {
            "test_id": test_id,
            "file": filename,
            "file_path": str(file_path),
        }

        # Hash check
        if filename in EXPECTED_HASHES:
            hash_ok = file_path.exists() and verify_hash(
                file_path, EXPECTED_HASHES[filename]
            )
            test_entry["sha256_verified"] = hash_ok
            if not hash_ok:
                test_entry["status"] = "FAIL"
                test_entry["error"] = "SHA-256 hash mismatch or file missing"
                overall_pass = False
                test_results.append(test_entry)
                continue

        # Parse
        parsed = parse_fods(file_path)
        parser_outputs[test_id] = parsed

        # Run assertions
        assertions = test_fn(parsed)
        failed = [a for a in assertions if not a["passed"]]
        passed_count = len([a for a in assertions if a["passed"]])

        test_entry["assertions"] = assertions
        test_entry["passed_count"] = passed_count
        test_entry["failed_count"] = len(failed)
        test_entry["parser_warnings"] = parsed.get("warnings", []) if "error" not in parsed else []

        if "error" in parsed:
            test_entry["status"] = "FAIL"
            test_entry["parse_error"] = parsed["error"]
            overall_pass = False
        elif failed:
            test_entry["status"] = "FAIL"
            overall_pass = False
        else:
            test_entry["status"] = "PASS"

        test_results.append(test_entry)

    summary = {
        "overall": "PASS" if overall_pass else "FAIL",
        "total_tests": len(test_cases),
        "passed": sum(1 for t in test_results if t.get("status") == "PASS"),
        "failed": sum(1 for t in test_results if t.get("status") == "FAIL"),
        "gate_4_status": (
            "prototype_created_pending_independent_verification"
            if overall_pass
            else "prototype_needs_revision"
        ),
        "gate_4_approved": False,
        "note": "Gate 4 NOT approved. Independent verification (TC-0018/DEC-034) required.",
    }

    return {
        "summary": summary,
        "tests": test_results,
        "parser_outputs": parser_outputs,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate FODS parser against Gate 3 sample corpus."
    )
    parser.add_argument(
        "--samples-dir",
        default=str(_REPO_ROOT / "samples" / "by-format" / "fods"),
        help="Path to the FODS samples directory",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this file (default: stdout)",
    )
    args = parser.parse_args()

    samples_dir = Path(args.samples_dir)
    if not samples_dir.is_dir():
        print(f"Error: samples directory not found: {samples_dir}", file=sys.stderr)
        sys.exit(1)

    report = run_validation(samples_dir)
    output = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    summary = report["summary"]
    print(
        f"\n=== Validation {summary['overall']} ===",
        file=sys.stderr,
    )
    print(
        f"Tests: {summary['passed']}/{summary['total_tests']} PASS",
        file=sys.stderr,
    )
    print(f"Gate 4 status: {summary['gate_4_status']}", file=sys.stderr)
    print(f"Gate 4 approved: {summary['gate_4_approved']}", file=sys.stderr)

    if summary["overall"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
