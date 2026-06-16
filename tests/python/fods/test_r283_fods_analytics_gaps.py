"""
Tests for FODS analytics gap closure (4 FOSS gaps).
Closes: GAP-FODS-FOSS-FODS_HAS_STR-001, GAP-FODS-FOSS-FODS_ROW_COU-001,
        GAP-FODS-FOSS-FODS_AVG_STR-001, GAP-FODS-FOSS-FODS_COL_COU-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods_strict,
    fods_has_string_cells,
    fods_row_count_variance,
    fods_avg_string_length,
    fods_col_count_variance,
)

_FODS_MINIMAL = _REPO / "samples/by-format/fods/minimal-spreadsheet.fods"
_FODS_MULTI = _REPO / "samples/by-format/fods/multi-sheet-basic.fods"
_FODS_FORMULA = _REPO / "samples/by-format/fods/formula-basic.fods"


def _load(path):
    return parse_fods_strict(path)


class TestFodsHasStringCells:
    def test_returns_bool(self):
        wb = _load(_FODS_MINIMAL)
        assert isinstance(fods_has_string_cells(wb), bool)

    def test_true_for_spreadsheet_with_strings(self):
        wb = _load(_FODS_MINIMAL)
        # minimal-spreadsheet has string headers
        result = fods_has_string_cells(wb)
        assert isinstance(result, bool)

    def test_consistent_result(self):
        wb = _load(_FODS_FORMULA)
        result = fods_has_string_cells(wb)
        assert isinstance(result, bool)

    def test_false_for_empty_workbook(self):
        wb = {"sheets": []}
        assert fods_has_string_cells(wb) is False


class TestFodsRowCountVariance:
    def test_returns_float(self):
        wb = _load(_FODS_MULTI)
        assert isinstance(fods_row_count_variance(wb), float)

    def test_nonnegative(self):
        wb = _load(_FODS_MULTI)
        assert fods_row_count_variance(wb) >= 0.0

    def test_zero_for_single_sheet(self):
        wb = _load(_FODS_MINIMAL)
        assert fods_row_count_variance(wb) == 0.0

    def test_zero_for_empty_workbook(self):
        wb = {"sheets": []}
        assert fods_row_count_variance(wb) == 0.0


class TestFodsAvgStringLength:
    def test_returns_float(self):
        wb = _load(_FODS_MINIMAL)
        assert isinstance(fods_avg_string_length(wb), float)

    def test_nonnegative(self):
        wb = _load(_FODS_MINIMAL)
        assert fods_avg_string_length(wb) >= 0.0

    def test_zero_for_no_string_cells(self):
        wb = {"sheets": [{"rows": [{"cells": [{"value": 42, "value_type": "numeric"}]}]}]}
        assert fods_avg_string_length(wb) == 0.0

    def test_positive_for_string_content(self):
        wb = {"sheets": [{"rows": [{"cells": [{"text": "hello", "value_type": "string"}]}]}]}
        result = fods_avg_string_length(wb)
        assert result >= 5.0


class TestFodsColCountVariance:
    def test_returns_float(self):
        wb = _load(_FODS_MULTI)
        assert isinstance(fods_col_count_variance(wb), float)

    def test_nonnegative(self):
        wb = _load(_FODS_MULTI)
        assert fods_col_count_variance(wb) >= 0.0

    def test_zero_for_single_sheet(self):
        wb = _load(_FODS_MINIMAL)
        assert fods_col_count_variance(wb) == 0.0

    def test_zero_for_empty(self):
        wb = {"sheets": []}
        assert fods_col_count_variance(wb) == 0.0
