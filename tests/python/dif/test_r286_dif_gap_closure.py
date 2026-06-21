"""
Tests for DIF gap closure (2 FOSS functions).
Closes: GAP-DIF-FOSS-DIF_MAX_COLU-001, GAP-DIF-FOSS-DIF_MIN_COLU-001

Known sample values:
  minimal-2x2.dif: max_col=99.0, min_col=42.0
  numeric-row.dif: max_col=3.0, min_col=1.0
  single-cell.dif: max_col=42.0, min_col=42.0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_max_column_sum, dif_min_column_sum

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = _DIF / "minimal-2x2.dif"
_NUMERIC = _DIF / "numeric-row.dif"
_SINGLE = _DIF / "single-cell.dif"


class TestDifMaxColumnSum:
    def test_returns_float(self):
        assert isinstance(dif_max_column_sum(_MINIMAL), float)

    def test_minimal_max_col(self):
        # Column 0: 42+57=99 > Column 1: 15+27=42 → max=99
        assert dif_max_column_sum(_MINIMAL) == 99.0

    def test_numeric_row_max_col(self):
        # numeric-row: single row [1,2,3] → col sums are 1,2,3 → max=3
        assert dif_max_column_sum(_NUMERIC) == 3.0

    def test_single_cell_max(self):
        assert dif_max_column_sum(_SINGLE) == 42.0

    def test_max_gte_min(self):
        for p in [_MINIMAL, _NUMERIC, _SINGLE]:
            assert dif_max_column_sum(p) >= dif_min_column_sum(p)

    def test_all_return_float(self):
        for p in [_MINIMAL, _NUMERIC, _SINGLE]:
            assert isinstance(dif_max_column_sum(p), float)


class TestDifMinColumnSum:
    def test_returns_float(self):
        assert isinstance(dif_min_column_sum(_MINIMAL), float)

    def test_minimal_min_col(self):
        # Column 1: 15+27=42 → min=42
        assert dif_min_column_sum(_MINIMAL) == 42.0

    def test_numeric_row_min_col(self):
        # numeric-row: col sums 1,2,3 → min=1
        assert dif_min_column_sum(_NUMERIC) == 1.0

    def test_single_cell_min(self):
        assert dif_min_column_sum(_SINGLE) == 42.0

    def test_all_return_float(self):
        for p in [_MINIMAL, _NUMERIC, _SINGLE]:
            assert isinstance(dif_min_column_sum(p), float)

    def test_minimal_min_less_than_max(self):
        assert dif_min_column_sum(_MINIMAL) < dif_max_column_sum(_MINIMAL)
