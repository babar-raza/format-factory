"""
Tests for ODS row/numeric analytics (2 new FOSS functions).
Closes: GAP-ODS-FOSS-ODS_MIN_R-001, GAP-ODS-FOSS-ODS_NUMER-001

Known sample values:
  single-cell.ods:         1 row, 1 string cell  → min_row_cell_count=1, numeric_cell_sum=0.0
  minimal-spreadsheet.ods: 2 rows, 2 cells each, 1 numeric (42.0) → min_row_cell_count=2, numeric_cell_sum=42.0
  numeric-row.ods:         1 row, 3 numeric cells (1,2,3) → min_row_cell_count=3, numeric_cell_sum=6.0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_min_row_cell_count, ods_numeric_cell_sum

_O = _REPO / "samples" / "by-format" / "ods" / "valid"
_SINGLE = _O / "single-cell.ods"
_MINIMAL = _O / "minimal-spreadsheet.ods"
_NUMERIC = _O / "numeric-row.ods"


class TestOdsMinRowCellCount:
    def test_returns_int(self):
        assert isinstance(ods_min_row_cell_count(_SINGLE), int)

    def test_single_cell_is_one(self):
        assert ods_min_row_cell_count(_SINGLE) == 1

    def test_minimal_is_two(self):
        # both rows have 2 cells
        assert ods_min_row_cell_count(_MINIMAL) == 2

    def test_numeric_row_is_three(self):
        # the single row has 3 cells
        assert ods_min_row_cell_count(_NUMERIC) == 3

    def test_nonnegative(self):
        for p in [_SINGLE, _MINIMAL, _NUMERIC]:
            assert ods_min_row_cell_count(p) >= 0

    def test_single_less_than_minimal(self):
        assert ods_min_row_cell_count(_SINGLE) < ods_min_row_cell_count(_MINIMAL)

    def test_all_return_int(self):
        for p in [_SINGLE, _MINIMAL, _NUMERIC]:
            assert isinstance(ods_min_row_cell_count(p), int)


class TestOdsNumericCellSum:
    def test_returns_float(self):
        assert isinstance(ods_numeric_cell_sum(_SINGLE), float)

    def test_single_cell_is_zero(self):
        # single-cell.ods has only a string value
        assert ods_numeric_cell_sum(_SINGLE) == 0.0

    def test_minimal_is_42(self):
        assert ods_numeric_cell_sum(_MINIMAL) == 42.0

    def test_numeric_row_is_six(self):
        # 1.0 + 2.0 + 3.0 = 6.0
        assert ods_numeric_cell_sum(_NUMERIC) == 6.0

    def test_nonnegative(self):
        for p in [_SINGLE, _MINIMAL, _NUMERIC]:
            assert ods_numeric_cell_sum(p) >= 0.0

    def test_single_less_than_minimal(self):
        assert ods_numeric_cell_sum(_SINGLE) < ods_numeric_cell_sum(_MINIMAL)

    def test_all_return_float(self):
        for p in [_SINGLE, _MINIMAL, _NUMERIC]:
            assert isinstance(ods_numeric_cell_sum(p), float)
