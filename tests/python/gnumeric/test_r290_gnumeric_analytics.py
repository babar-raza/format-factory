"""
Tests for Gnumeric additional row/string analytics (2 new FOSS functions).
Closes: GAP-GNUMERIC-FOSS-GNUMERIC_MIN-001, GAP-GNUMERIC-FOSS-GNUMERIC_AVG-001

Known sample values:
  empty-sheet.gnumeric:       0 rows  → min_row_length=0,  avg_string_length=0.0
  minimal-spreadsheet.gnumeric: row 0 has 'Hello' (1 cell) → min_row_length=1, avg_string_length=5.0
  multi-cell-basic.gnumeric:  2 rows each with 2 cells (Name,Score,Alice are strings) → min_row_length=2, avg_string_length≈4.667
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_min_row_length, gnumeric_avg_string_length

_G = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = _G / "empty-sheet.gnumeric"
_MINIMAL = _G / "minimal-spreadsheet.gnumeric"
_MULTI = _G / "multi-cell-basic.gnumeric"


class TestGnumericMinRowLength:
    def test_returns_int(self):
        assert isinstance(gnumeric_min_row_length(_EMPTY), int)

    def test_empty_sheet_is_zero(self):
        assert gnumeric_min_row_length(_EMPTY) == 0

    def test_minimal_is_one(self):
        assert gnumeric_min_row_length(_MINIMAL) == 1

    def test_multi_cell_is_two(self):
        # both rows have 2 cells (Name+Score, Alice+42)
        assert gnumeric_min_row_length(_MULTI) == 2

    def test_nonnegative(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert gnumeric_min_row_length(p) >= 0

    def test_empty_less_than_minimal(self):
        assert gnumeric_min_row_length(_EMPTY) < gnumeric_min_row_length(_MINIMAL)

    def test_minimal_leq_multi(self):
        assert gnumeric_min_row_length(_MINIMAL) <= gnumeric_min_row_length(_MULTI)

    def test_all_return_int(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert isinstance(gnumeric_min_row_length(p), int)


class TestGnumericAvgStringLength:
    def test_returns_float(self):
        assert isinstance(gnumeric_avg_string_length(_EMPTY), float)

    def test_empty_is_zero(self):
        assert gnumeric_avg_string_length(_EMPTY) == 0.0

    def test_minimal_is_five(self):
        # 'Hello' has length 5
        assert gnumeric_avg_string_length(_MINIMAL) == 5.0

    def test_multi_cell_approx(self):
        # Name(4) + Score(5) + Alice(5) = 14 / 3 ≈ 4.667
        val = gnumeric_avg_string_length(_MULTI)
        assert abs(val - 14 / 3) < 1e-9

    def test_nonnegative(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert gnumeric_avg_string_length(p) >= 0.0

    def test_empty_less_than_minimal(self):
        assert gnumeric_avg_string_length(_EMPTY) < gnumeric_avg_string_length(_MINIMAL)

    def test_all_return_float(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert isinstance(gnumeric_avg_string_length(p), float)
