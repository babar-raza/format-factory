"""Tests for tsv_is_single_row and tsv_total_field_length_sum (Sprint r303)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_is_single_row, tsv_total_field_length_sum

_TSV = _REPO / "samples" / "by-format" / "tsv"


class TestTsvIsSingleRow:
    """Tests for tsv_is_single_row."""

    def test_minimal_2x2_is_not_single_row(self):
        """minimal-2x2.tsv has 2 rows → False."""
        result = tsv_is_single_row(_TSV / "minimal-2x2.tsv")
        assert result is False

    def test_multi_column_is_not_single_row(self):
        """multi-column.tsv has 2 rows → False."""
        result = tsv_is_single_row(_TSV / "multi-column.tsv")
        assert result is False

    def test_single_cell_is_single_row(self):
        """single-cell.tsv has 1 row → True."""
        result = tsv_is_single_row(_TSV / "single-cell.tsv")
        assert result is True

    def test_returns_bool(self):
        result = tsv_is_single_row(_TSV / "single-cell.tsv")
        assert isinstance(result, bool)

    def test_multi_row_files_return_false(self):
        for f in ["minimal-2x2.tsv", "multi-column.tsv"]:
            assert tsv_is_single_row(_TSV / f) is False

    def test_single_true_minimal_false(self):
        r1 = tsv_is_single_row(_TSV / "minimal-2x2.tsv")
        r2 = tsv_is_single_row(_TSV / "single-cell.tsv")
        assert r1 is False and r2 is True


class TestTsvTotalFieldLengthSum:
    """Tests for tsv_total_field_length_sum."""

    def test_minimal_2x2_sum_is_12(self):
        """minimal-2x2.tsv: fields total char length = 12."""
        result = tsv_total_field_length_sum(_TSV / "minimal-2x2.tsv")
        assert result == 12

    def test_multi_column_sum_is_27(self):
        """multi-column.tsv: fields total char length = 27."""
        result = tsv_total_field_length_sum(_TSV / "multi-column.tsv")
        assert result == 27

    def test_single_cell_sum_is_2(self):
        """single-cell.tsv: 1 field with 2 chars."""
        result = tsv_total_field_length_sum(_TSV / "single-cell.tsv")
        assert result == 2

    def test_returns_int(self):
        result = tsv_total_field_length_sum(_TSV / "single-cell.tsv")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-2x2.tsv", "multi-column.tsv", "single-cell.tsv"]:
            assert tsv_total_field_length_sum(_TSV / f) >= 0

    def test_multi_column_larger_than_minimal(self):
        r1 = tsv_total_field_length_sum(_TSV / "minimal-2x2.tsv")
        r2 = tsv_total_field_length_sum(_TSV / "multi-column.tsv")
        assert r2 > r1
