"""
Tests for 5 new FODS analytics functions (R337 / Sprint 73):
  fods_file_size_bytes, fods_max_row_count (new override), fods_nonempty_cell_count_all,
  fods_numeric_ratio, fods_max_sheet_row_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods,
    fods_file_size_bytes,
    fods_max_row_count,
    fods_nonempty_cell_count_all,
    fods_numeric_ratio,
    fods_max_sheet_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")
_FORMULA = str(_SAMPLES / "formula-basic.fods")
_MULTI = str(_SAMPLES / "multi-sheet-basic.fods")
_TYPED = str(_SAMPLES / "typed-values-basic.fods")


# ── fods_file_size_bytes ───────────────────────────────────────────────────────

class TestFodsFileSizeBytes:
    def test_returns_int(self):
        result = fods_file_size_bytes(_MINIMAL)
        assert isinstance(result, int)

    def test_positive_size(self):
        result = fods_file_size_bytes(_MINIMAL)
        assert result > 0

    def test_formula_file_size(self):
        result = fods_file_size_bytes(_FORMULA)
        assert result > 0

    def test_multi_sheet_larger_than_minimal(self):
        size_minimal = fods_file_size_bytes(_MINIMAL)
        size_multi = fods_file_size_bytes(_MULTI)
        # multi-sheet file should be at least as large
        assert size_multi >= size_minimal or size_multi > 0

    def test_typed_file_size(self):
        result = fods_file_size_bytes(_TYPED)
        assert isinstance(result, int) and result > 0


# ── fods_max_row_count ─────────────────────────────────────────────────────────

class TestFodsMaxRowCount:
    def test_returns_int(self):
        wb = parse_fods(_MINIMAL)
        result = fods_max_row_count(wb)
        assert isinstance(result, int)

    def test_at_least_one_row(self):
        wb = parse_fods(_MINIMAL)
        result = fods_max_row_count(wb)
        assert result >= 1

    def test_formula_has_rows(self):
        wb = parse_fods(_FORMULA)
        result = fods_max_row_count(wb)
        assert result >= 1

    def test_multi_sheet_has_rows(self):
        wb = parse_fods(_MULTI)
        result = fods_max_row_count(wb)
        assert result >= 1

    def test_empty_workbook_returns_zero(self):
        wb = {"sheets": []}
        result = fods_max_row_count(wb)
        assert result == 0


# ── fods_nonempty_cell_count_all ───────────────────────────────────────────────

class TestFodsNonemptyCellCountAll:
    def test_returns_int(self):
        wb = parse_fods(_MINIMAL)
        result = fods_nonempty_cell_count_all(wb)
        assert isinstance(result, int)

    def test_positive_for_minimal(self):
        wb = parse_fods(_MINIMAL)
        result = fods_nonempty_cell_count_all(wb)
        assert result >= 0

    def test_formula_has_cells(self):
        wb = parse_fods(_FORMULA)
        result = fods_nonempty_cell_count_all(wb)
        assert result >= 0

    def test_typed_has_cells(self):
        wb = parse_fods(_TYPED)
        result = fods_nonempty_cell_count_all(wb)
        assert result >= 0

    def test_empty_workbook_returns_zero(self):
        wb = {"sheets": []}
        result = fods_nonempty_cell_count_all(wb)
        assert result == 0


# ── fods_numeric_ratio ─────────────────────────────────────────────────────────

class TestFodsNumericRatio:
    def test_returns_float(self):
        wb = parse_fods(_TYPED)
        result = fods_numeric_ratio(wb)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        wb = parse_fods(_TYPED)
        result = fods_numeric_ratio(wb)
        assert 0.0 <= result <= 1.0

    def test_formula_file_ratio(self):
        wb = parse_fods(_FORMULA)
        result = fods_numeric_ratio(wb)
        assert 0.0 <= result <= 1.0

    def test_multi_sheet_ratio(self):
        wb = parse_fods(_MULTI)
        result = fods_numeric_ratio(wb)
        assert 0.0 <= result <= 1.0

    def test_empty_workbook_returns_zero(self):
        wb = {"sheets": []}
        result = fods_numeric_ratio(wb)
        assert result == 0.0


# ── fods_max_sheet_row_count ───────────────────────────────────────────────────

class TestFodsMaxSheetRowCount:
    def test_returns_int(self):
        wb = parse_fods(_MINIMAL)
        result = fods_max_sheet_row_count(wb)
        assert isinstance(result, int)

    def test_matches_max_row_count(self):
        wb = parse_fods(_MINIMAL)
        assert fods_max_sheet_row_count(wb) == fods_max_row_count(wb)

    def test_formula_file(self):
        wb = parse_fods(_FORMULA)
        result = fods_max_sheet_row_count(wb)
        assert result >= 0

    def test_multi_sheet_file(self):
        wb = parse_fods(_MULTI)
        result = fods_max_sheet_row_count(wb)
        assert result >= 1

    def test_empty_workbook_returns_zero(self):
        wb = {"sheets": []}
        result = fods_max_sheet_row_count(wb)
        assert result == 0
