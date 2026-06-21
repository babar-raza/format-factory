"""
Tests for additional TSV analytics gap closure (6 FOSS gaps).
Closes: TSV_COLUMN_V, TSV_FIELD_LE, TSV_CELL_TO_,
        TSV_STRING_C, TSV_TOTAL_ST, TSV_AVG_FIEL
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    tsv_column_value_variance,
    tsv_field_length_sum,
    tsv_cell_to_row_ratio,
    tsv_string_cell_count,
    tsv_total_string_length,
    tsv_avg_fields_per_row,
)

_TSV_2x2 = _REPO / "samples/by-format/tsv/minimal-2x2.tsv"
_TSV_MULTI = _REPO / "samples/by-format/tsv/multi-column.tsv"
_TSV_SINGLE = _REPO / "samples/by-format/tsv/single-cell.tsv"


class TestTsvColumnValueVariance:
    def test_returns_float(self):
        assert isinstance(tsv_column_value_variance(_TSV_2x2), float)

    def test_nonnegative(self):
        assert tsv_column_value_variance(_TSV_2x2) >= 0.0

    def test_2x2_exact(self):
        assert tsv_column_value_variance(_TSV_2x2) == pytest.approx(6.25, rel=1e-3)

    def test_multi_larger_variance(self):
        assert tsv_column_value_variance(_TSV_MULTI) > tsv_column_value_variance(_TSV_2x2)


class TestTsvFieldLengthSum:
    def test_returns_int(self):
        assert isinstance(tsv_field_length_sum(_TSV_2x2), int)

    def test_nonnegative(self):
        assert tsv_field_length_sum(_TSV_2x2) >= 0

    def test_2x2_exact(self):
        assert tsv_field_length_sum(_TSV_2x2) == 12

    def test_multi_larger_than_2x2(self):
        assert tsv_field_length_sum(_TSV_MULTI) > tsv_field_length_sum(_TSV_2x2)


class TestTsvCellToRowRatio:
    def test_returns_float(self):
        assert isinstance(tsv_cell_to_row_ratio(_TSV_2x2), float)

    def test_nonnegative(self):
        assert tsv_cell_to_row_ratio(_TSV_2x2) >= 0.0

    def test_2x2_exact(self):
        # 2x2: 4 cells, 2 rows → ratio = 2.0
        assert tsv_cell_to_row_ratio(_TSV_2x2) == pytest.approx(2.0)

    def test_single_cell_ratio_one(self):
        # single-cell: 1 cell, 1 row → 1.0
        assert tsv_cell_to_row_ratio(_TSV_SINGLE) == pytest.approx(1.0)


class TestTsvStringCellCount:
    def test_returns_int(self):
        assert isinstance(tsv_string_cell_count(_TSV_2x2), int)

    def test_nonnegative(self):
        assert tsv_string_cell_count(_TSV_2x2) >= 0

    def test_2x2_exact(self):
        assert tsv_string_cell_count(_TSV_2x2) == 2

    def test_multi_has_string_cells(self):
        assert tsv_string_cell_count(_TSV_MULTI) >= 0


class TestTsvTotalStringLength:
    def test_returns_int(self):
        assert isinstance(tsv_total_string_length(_TSV_2x2), int)

    def test_nonnegative(self):
        assert tsv_total_string_length(_TSV_2x2) >= 0

    def test_2x2_exact(self):
        assert tsv_total_string_length(_TSV_2x2) == 12

    def test_multi_has_total(self):
        assert tsv_total_string_length(_TSV_MULTI) >= 0


class TestTsvAvgFieldsPerRow:
    def test_returns_float(self):
        assert isinstance(tsv_avg_fields_per_row(_TSV_2x2), float)

    def test_nonnegative(self):
        assert tsv_avg_fields_per_row(_TSV_2x2) >= 0.0

    def test_2x2_exact(self):
        # 2x2: 2 fields per row
        assert tsv_avg_fields_per_row(_TSV_2x2) == pytest.approx(2.0)

    def test_single_cell_exact(self):
        assert tsv_avg_fields_per_row(_TSV_SINGLE) == pytest.approx(1.0)
