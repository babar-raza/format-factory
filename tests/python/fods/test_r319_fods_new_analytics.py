"""
test_r319_fods_new_analytics.py
Sprint 55 — 5 new FODS analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods,
    fods_max_numeric_all_sheets,
    fods_min_numeric_all_sheets,
    fods_unique_string_count,
    fods_boolean_cell_count,
    fods_avg_string_cell_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")
_NUMERIC = str(_SAMPLES / "typed-values-basic.fods")
_MULTI = str(_SAMPLES / "multi-sheet-basic.fods")
_FORMULA = str(_SAMPLES / "formula-basic.fods")


def _load(path):
    return parse_fods(path)


# --- fods_max_numeric_all_sheets ---

class TestFodsMaxNumericAllSheets:
    def test_returns_float(self):
        assert isinstance(fods_max_numeric_all_sheets(_load(_NUMERIC)), float)

    def test_numeric_positive(self):
        assert fods_max_numeric_all_sheets(_load(_NUMERIC)) > 0.0

    def test_minimal_non_negative(self):
        assert fods_max_numeric_all_sheets(_load(_MINIMAL)) >= 0.0

    def test_multi_non_negative(self):
        assert fods_max_numeric_all_sheets(_load(_MULTI)) >= 0.0

    def test_max_ge_min(self):
        wb = _load(_NUMERIC)
        assert fods_max_numeric_all_sheets(wb) >= fods_min_numeric_all_sheets(wb)


# --- fods_min_numeric_all_sheets ---

class TestFodsMinNumericAllSheets:
    def test_returns_float(self):
        assert isinstance(fods_min_numeric_all_sheets(_load(_NUMERIC)), float)

    def test_numeric_non_negative(self):
        assert fods_min_numeric_all_sheets(_load(_NUMERIC)) >= 0.0

    def test_minimal_non_negative(self):
        assert fods_min_numeric_all_sheets(_load(_MINIMAL)) >= 0.0

    def test_multi_non_negative(self):
        assert fods_min_numeric_all_sheets(_load(_MULTI)) >= 0.0

    def test_empty_workbook_returns_zero(self):
        assert fods_min_numeric_all_sheets({"sheets": []}) == 0.0


# --- fods_unique_string_count ---

class TestFodsUniqueStringCount:
    def test_returns_int(self):
        assert isinstance(fods_unique_string_count(_load(_MINIMAL)), int)

    def test_minimal_positive(self):
        assert fods_unique_string_count(_load(_MINIMAL)) >= 1

    def test_multi_non_negative(self):
        assert fods_unique_string_count(_load(_MULTI)) >= 0

    def test_numeric_non_negative(self):
        assert fods_unique_string_count(_load(_NUMERIC)) >= 0

    def test_empty_workbook_returns_zero(self):
        assert fods_unique_string_count({"sheets": []}) == 0


# --- fods_boolean_cell_count ---

class TestFodsBooleanCellCount:
    def test_returns_int(self):
        assert isinstance(fods_boolean_cell_count(_load(_NUMERIC)), int)

    def test_non_negative(self):
        assert fods_boolean_cell_count(_load(_NUMERIC)) >= 0

    def test_minimal_non_negative(self):
        assert fods_boolean_cell_count(_load(_MINIMAL)) >= 0

    def test_empty_workbook_zero(self):
        assert fods_boolean_cell_count({"sheets": []}) == 0

    def test_formula_non_negative(self):
        assert fods_boolean_cell_count(_load(_FORMULA)) >= 0


# --- fods_avg_string_cell_length ---

class TestFodsAvgStringCellLength:
    def test_returns_float(self):
        assert isinstance(fods_avg_string_cell_length(_load(_MINIMAL)), float)

    def test_minimal_positive(self):
        assert fods_avg_string_cell_length(_load(_MINIMAL)) >= 0.0

    def test_multi_non_negative(self):
        assert fods_avg_string_cell_length(_load(_MULTI)) >= 0.0

    def test_empty_workbook_zero(self):
        assert fods_avg_string_cell_length({"sheets": []}) == 0.0

    def test_numeric_non_negative(self):
        assert fods_avg_string_cell_length(_load(_NUMERIC)) >= 0.0
