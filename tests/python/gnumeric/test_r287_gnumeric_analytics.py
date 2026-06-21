"""
Tests for Gnumeric additional analytics (2 new FOSS functions).
Closes: GAP-GNUMERIC-FOSS-MIN_NUMERIC-001, GAP-GNUMERIC-FOSS-MAX_NUMERIC-001

Known sample values (from gnumeric_min/max_numeric_value):
  empty-sheet.gnumeric: min=0.0, max=0.0 (no numeric cells)
  minimal-spreadsheet.gnumeric: min=0.0, max=0.0 (only string "Hello")
  multi-cell-basic.gnumeric: min=42.0, max=42.0 (one numeric "42")
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_min_numeric_value, gnumeric_max_numeric_value

_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = _GNUMERIC / "empty-sheet.gnumeric"
_MINIMAL = _GNUMERIC / "minimal-spreadsheet.gnumeric"
_MULTI = _GNUMERIC / "multi-cell-basic.gnumeric"


class TestGnumericMinNumericValue:
    def test_returns_float(self):
        assert isinstance(gnumeric_min_numeric_value(_EMPTY), float)

    def test_empty_sheet_returns_zero(self):
        assert gnumeric_min_numeric_value(_EMPTY) == 0.0

    def test_no_numeric_cells_returns_zero(self):
        # minimal-spreadsheet has only "Hello" string
        assert gnumeric_min_numeric_value(_MINIMAL) == 0.0

    def test_multi_cell_min(self):
        # only numeric value is 42
        assert gnumeric_min_numeric_value(_MULTI) == 42.0

    def test_min_lte_max(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert gnumeric_min_numeric_value(p) <= gnumeric_max_numeric_value(p)

    def test_all_return_float(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert isinstance(gnumeric_min_numeric_value(p), float)


class TestGnumericMaxNumericValue:
    def test_returns_float(self):
        assert isinstance(gnumeric_max_numeric_value(_EMPTY), float)

    def test_empty_sheet_returns_zero(self):
        assert gnumeric_max_numeric_value(_EMPTY) == 0.0

    def test_no_numeric_cells_returns_zero(self):
        assert gnumeric_max_numeric_value(_MINIMAL) == 0.0

    def test_multi_cell_max(self):
        # only numeric value is 42
        assert gnumeric_max_numeric_value(_MULTI) == 42.0

    def test_max_gte_min(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert gnumeric_max_numeric_value(p) >= gnumeric_min_numeric_value(p)

    def test_all_return_float(self):
        for p in [_EMPTY, _MINIMAL, _MULTI]:
            assert isinstance(gnumeric_max_numeric_value(p), float)

    def test_multi_min_equals_max(self):
        # only one numeric value → min == max
        assert gnumeric_min_numeric_value(_MULTI) == gnumeric_max_numeric_value(_MULTI)
