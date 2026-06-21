"""Tests for tsv_string_field_count and tsv_total_field_count (Sprint r293)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_string_field_count, tsv_total_field_count

_TSV = _REPO / "samples" / "by-format" / "tsv"


class TestTsvStringFieldCount:
    """Tests for tsv_string_field_count."""

    def test_single_cell_no_string_fields(self):
        """single-cell.tsv has 1 numeric field, so string count is 0."""
        result = tsv_string_field_count(_TSV / "single-cell.tsv")
        assert result == 0

    def test_minimal_2x2_has_string_fields(self):
        """minimal-2x2.tsv has 2 string fields (headers)."""
        result = tsv_string_field_count(_TSV / "minimal-2x2.tsv")
        assert result == 2

    def test_multi_column_has_string_fields(self):
        """multi-column.tsv has 4 string fields."""
        result = tsv_string_field_count(_TSV / "multi-column.tsv")
        assert result == 4

    def test_returns_int(self):
        result = tsv_string_field_count(_TSV / "minimal-2x2.tsv")
        assert isinstance(result, int)

    def test_returns_zero_for_numeric_only(self):
        """single-cell.tsv is all numeric, so returns 0."""
        result = tsv_string_field_count(_TSV / "single-cell.tsv")
        assert result == 0

    def test_multi_column_greater_than_minimal(self):
        r1 = tsv_string_field_count(_TSV / "minimal-2x2.tsv")
        r2 = tsv_string_field_count(_TSV / "multi-column.tsv")
        assert r2 > r1


class TestTsvTotalFieldCount:
    """Tests for tsv_total_field_count."""

    def test_single_cell_total_is_one(self):
        """single-cell.tsv has exactly 1 field."""
        result = tsv_total_field_count(_TSV / "single-cell.tsv")
        assert result == 1

    def test_minimal_2x2_total_is_four(self):
        """minimal-2x2.tsv has 2 rows x 2 cols = 4 fields."""
        result = tsv_total_field_count(_TSV / "minimal-2x2.tsv")
        assert result == 4

    def test_multi_column_total_is_eight(self):
        """multi-column.tsv has 2 rows x 4 cols = 8 fields."""
        result = tsv_total_field_count(_TSV / "multi-column.tsv")
        assert result == 8

    def test_returns_int(self):
        result = tsv_total_field_count(_TSV / "minimal-2x2.tsv")
        assert isinstance(result, int)

    def test_multi_column_larger_than_minimal(self):
        r1 = tsv_total_field_count(_TSV / "minimal-2x2.tsv")
        r2 = tsv_total_field_count(_TSV / "multi-column.tsv")
        assert r2 > r1

    def test_total_at_least_as_large_as_string_count(self):
        total = tsv_total_field_count(_TSV / "minimal-2x2.tsv")
        string = tsv_string_field_count(_TSV / "minimal-2x2.tsv")
        assert total >= string
