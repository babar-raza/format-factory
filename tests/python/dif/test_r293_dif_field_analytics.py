"""Tests for dif_string_field_count and dif_total_char_count (Sprint r293)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_string_field_count, dif_total_char_count

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifStringFieldCount:
    """Tests for dif_string_field_count."""

    def test_minimal_2x2_has_six_string_cells(self):
        """minimal-2x2.dif has 6 string-type cell values."""
        result = dif_string_field_count(_DIF / "minimal-2x2.dif")
        assert result == 6

    def test_numeric_row_has_no_string_cells(self):
        """numeric-row.dif has only numeric cells."""
        result = dif_string_field_count(_DIF / "numeric-row.dif")
        assert result == 0

    def test_single_cell_has_no_string_cells(self):
        """single-cell.dif has no string-type cells."""
        result = dif_string_field_count(_DIF / "single-cell.dif")
        assert result == 0

    def test_returns_int(self):
        result = dif_string_field_count(_DIF / "minimal-2x2.dif")
        assert isinstance(result, int)

    def test_minimal_greater_than_numeric_row(self):
        r1 = dif_string_field_count(_DIF / "numeric-row.dif")
        r2 = dif_string_field_count(_DIF / "minimal-2x2.dif")
        assert r2 > r1

    def test_nonnegative(self):
        for f in ["minimal-2x2.dif", "numeric-row.dif", "single-cell.dif"]:
            result = dif_string_field_count(_DIF / f)
            assert result >= 0


class TestDifTotalCharCount:
    """Tests for dif_total_char_count."""

    def test_minimal_2x2_has_28_chars(self):
        """minimal-2x2.dif string values total 28 characters."""
        result = dif_total_char_count(_DIF / "minimal-2x2.dif")
        assert result == 28

    def test_numeric_row_has_zero_chars(self):
        """numeric-row.dif has no string cells, so total char count is 0."""
        result = dif_total_char_count(_DIF / "numeric-row.dif")
        assert result == 0

    def test_single_cell_has_zero_chars(self):
        """single-cell.dif has no string cells."""
        result = dif_total_char_count(_DIF / "single-cell.dif")
        assert result == 0

    def test_returns_int(self):
        result = dif_total_char_count(_DIF / "minimal-2x2.dif")
        assert isinstance(result, int)

    def test_minimal_larger_than_numeric_row(self):
        r1 = dif_total_char_count(_DIF / "numeric-row.dif")
        r2 = dif_total_char_count(_DIF / "minimal-2x2.dif")
        assert r2 > r1

    def test_char_count_consistent_with_string_field_count(self):
        """Nonzero string fields imply nonzero char count."""
        sc = dif_string_field_count(_DIF / "minimal-2x2.dif")
        cc = dif_total_char_count(_DIF / "minimal-2x2.dif")
        assert sc > 0
        assert cc > 0
