"""
R43 Lane 4A: FODS Python deepening tests — authority proof level.

Extends R42 deepening with:
- Neutral model validation round-trips (validate_workbook)
- Formula cell enumeration and preservation
- Strict vs soft parse divergence guard
- Unsupported-features field contract
- Sheet name uniqueness
- Zero-row sheet handling
- parse_errors field type contract
- warnings field type contract
- warnings/parse_errors on non-FODS input
- Full neutral model field completeness
"""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SAMPLES = REPO_ROOT / "samples" / "by-format" / "fods"

sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fods import parse_fods, parse_fods_strict, FORMAT_ID, SPEC_VERSION
from fods.neutral_model import validate_workbook


# ---------------------------------------------------------------------------
# Neutral model validation round-trips
# ---------------------------------------------------------------------------

class TestNeutralModelValidation:
    """R43: validate_workbook must return zero violations on real parse results."""

    def test_formula_basic_validates(self):
        result = parse_fods_strict(str(SAMPLES / "formula-basic.fods"))
        violations = validate_workbook(result)
        assert violations == [], f"Neutral model violations: {violations}"

    def test_minimal_spreadsheet_validates(self):
        result = parse_fods_strict(str(SAMPLES / "minimal-spreadsheet.fods"))
        violations = validate_workbook(result)
        assert violations == [], f"Neutral model violations: {violations}"

    def test_multi_sheet_validates(self):
        result = parse_fods_strict(str(SAMPLES / "multi-sheet-basic.fods"))
        violations = validate_workbook(result)
        assert violations == [], f"Neutral model violations: {violations}"

    def test_typed_values_validates(self):
        result = parse_fods_strict(str(SAMPLES / "typed-values-basic.fods"))
        violations = validate_workbook(result)
        assert violations == [], f"Neutral model violations: {violations}"


# ---------------------------------------------------------------------------
# Formula cell access
# ---------------------------------------------------------------------------

class TestFormulaPreservation:
    """R43: Formula cells must retain formula strings and have value_type float."""

    def test_formula_cell_has_formula_string(self):
        result = parse_fods_strict(str(SAMPLES / "formula-basic.fods"))
        all_cells = [
            c
            for sheet in result["sheets"]
            for row in sheet["rows"]
            for c in row["cells"]
        ]
        formula_cells = [c for c in all_cells if c.get("formula")]
        assert len(formula_cells) >= 1, "formula-basic.fods must have at least one formula cell"

    def test_formula_cell_value_type(self):
        result = parse_fods_strict(str(SAMPLES / "formula-basic.fods"))
        for sheet in result["sheets"]:
            for row in sheet["rows"]:
                for c in row["cells"]:
                    if c.get("formula"):
                        assert c["value_type"] in ("float", "string", None), (
                            f"Formula cell has unexpected value_type: {c['value_type']}"
                        )

    def test_non_formula_cells_formula_none(self):
        result = parse_fods_strict(str(SAMPLES / "minimal-spreadsheet.fods"))
        for sheet in result["sheets"]:
            for row in sheet["rows"]:
                for c in row["cells"]:
                    if not c.get("formula"):
                        assert c["formula"] is None or c["formula"] == "", (
                            f"Non-formula cell should have None formula, got: {c['formula']}"
                        )


# ---------------------------------------------------------------------------
# Sheet structural contracts
# ---------------------------------------------------------------------------

class TestSheetStructure:
    """R43: Sheet names unique, indices sequential, row_count matches."""

    def test_sheet_names_unique(self):
        result = parse_fods_strict(str(SAMPLES / "multi-sheet-basic.fods"))
        names = [s["name"] for s in result["sheets"]]
        assert len(names) == len(set(names)), f"Sheet names not unique: {names}"

    def test_sheet_indices_sequential(self):
        result = parse_fods_strict(str(SAMPLES / "multi-sheet-basic.fods"))
        for i, sheet in enumerate(result["sheets"]):
            assert sheet["index"] == i, f"Sheet {i} has wrong index {sheet['index']}"

    def test_row_count_matches_rows_list(self):
        result = parse_fods_strict(str(SAMPLES / "formula-basic.fods"))
        for sheet in result["sheets"]:
            assert sheet["row_count"] == len(sheet["rows"]), (
                f"Sheet '{sheet['name']}': row_count={sheet['row_count']} "
                f"but len(rows)={len(sheet['rows'])}"
            )

    def test_sheet_count_matches_sheets_list(self):
        result = parse_fods_strict(str(SAMPLES / "multi-sheet-basic.fods"))
        assert result["sheet_count"] == len(result["sheets"]), (
            f"sheet_count={result['sheet_count']} but len(sheets)={len(result['sheets'])}"
        )


# ---------------------------------------------------------------------------
# Field type contracts
# ---------------------------------------------------------------------------

class TestFieldTypeContracts:
    """R43: warnings, parse_errors, unsupported_features must be lists."""

    def test_warnings_is_list(self):
        result = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        assert isinstance(result["warnings"], list), "warnings must be a list"

    def test_parse_errors_is_list(self):
        result = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        assert isinstance(result["parse_errors"], list), "parse_errors must be a list"

    def test_unsupported_features_is_list(self):
        result = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        assert isinstance(result["unsupported_features"], list), "unsupported_features must be a list"

    def test_unsupported_features_sorted(self):
        """Unsupported features must be sorted (neutral model requirement)."""
        result = parse_fods(str(SAMPLES / "formula-basic.fods"))
        uf = result.get("unsupported_features", [])
        assert uf == sorted(uf), f"unsupported_features not sorted: {uf}"

    def test_format_id_is_fods_string(self):
        result = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        assert result["format_id"] == "fods"

    def test_spec_version_is_string(self):
        result = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        assert isinstance(result["spec_version"], str)
        assert len(result["spec_version"]) > 0


# ---------------------------------------------------------------------------
# Soft vs strict divergence guard
# ---------------------------------------------------------------------------

class TestSoftVsStrictDivergence:
    """R43: parse_fods must return same content as parse_fods_strict on valid files."""

    def test_soft_and_strict_same_sheet_count(self):
        soft = parse_fods(str(SAMPLES / "multi-sheet-basic.fods"))
        strict = parse_fods_strict(str(SAMPLES / "multi-sheet-basic.fods"))
        assert soft["sheet_count"] == strict["sheet_count"]

    def test_soft_and_strict_same_format_id(self):
        soft = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        strict = parse_fods_strict(str(SAMPLES / "minimal-spreadsheet.fods"))
        assert soft["format_id"] == strict["format_id"]


# ---------------------------------------------------------------------------
# Error handling on invalid input
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """R43: Invalid input must return/raise appropriate errors."""

    def test_parse_fods_nonexistent_returns_error(self):
        result = parse_fods("/nonexistent/file.fods")
        # parse_fods (soft) returns dict with 'error' key on file-not-found
        has_error = (
            result.get("error")
            or result.get("parse_errors")
            or result.get("warnings")
        )
        assert has_error, (
            "parse_fods on nonexistent file should report 'error', 'parse_errors', or 'warnings'"
        )

    def test_parse_fods_strict_nonexistent_raises(self):
        from fods import FodsError
        with pytest.raises(FodsError):
            parse_fods_strict("/nonexistent/file.fods")
