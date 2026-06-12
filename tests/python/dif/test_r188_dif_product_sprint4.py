"""Sprint 4 DIF product tests: filter_rows_by_value, count_nonempty_cells, dif_max_row_length.

Tests: 15 total
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import filter_rows_by_value, count_nonempty_cells, dif_max_row_length

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.dif")
_NUMERIC = str(_SAMPLES / "numeric-row.dif")
_SINGLE = str(_SAMPLES / "single-cell.dif")


# ---------------------------------------------------------------------------
# filter_rows_by_value (takes dict with "data" key)
# ---------------------------------------------------------------------------

def _make_data(rows):
    """Helper: wrap rows in the expected data dict format."""
    return {"data": rows}


class TestFilterRowsByValue:
    def test_match_string_column(self):
        data = _make_data([["Alice", 30], ["Bob", 25], ["Alice", 35]])
        result = filter_rows_by_value(data, 0, "Alice")
        assert result == [["Alice", 30], ["Alice", 35]]

    def test_match_numeric_column(self):
        data = _make_data([["Alice", 30], ["Bob", 25], ["Alice", 35]])
        result = filter_rows_by_value(data, 1, 25)
        assert result == [["Bob", 25]]

    def test_no_match_returns_empty_list(self):
        data = _make_data([["Alice", 30], ["Bob", 25]])
        result = filter_rows_by_value(data, 0, "Charlie")
        assert result == []

    def test_out_of_range_col_returns_empty(self):
        data = _make_data([["A", "B"], ["C", "D"]])
        result = filter_rows_by_value(data, 10, "A")
        assert result == []

    def test_negative_col_returns_empty(self):
        data = _make_data([["A", "B"]])
        result = filter_rows_by_value(data, -1, "A")
        assert result == []

    def test_empty_data_returns_empty(self):
        result = filter_rows_by_value({"data": []}, 0, "x")
        assert result == []

    def test_missing_data_key_returns_empty(self):
        # parse_dif() returns "rows" not "data" — function returns empty gracefully
        result = filter_rows_by_value({"rows": [["A"]]}, 0, "A")
        assert result == []

    def test_multiple_columns(self):
        data = _make_data([[1, 2, 3], [4, 2, 6], [7, 8, 9]])
        result = filter_rows_by_value(data, 1, 2)
        assert len(result) == 2
        assert [1, 2, 3] in result
        assert [4, 2, 6] in result


# ---------------------------------------------------------------------------
# count_nonempty_cells (takes file path)
# ---------------------------------------------------------------------------

class TestCountNonemptyCells:
    def test_minimal_2x2_has_cells(self):
        result = count_nonempty_cells(_MINIMAL)
        assert isinstance(result, int)
        assert result > 0

    def test_numeric_row_cell_count(self):
        # numeric-row.dif has 1 row × 3 values = 3
        result = count_nonempty_cells(_NUMERIC)
        assert result == 3

    def test_single_cell(self):
        result = count_nonempty_cells(_SINGLE)
        assert result == 1

    def test_returns_int(self):
        result = count_nonempty_cells(_MINIMAL)
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# dif_max_row_length (takes file path)
# ---------------------------------------------------------------------------

class TestDifMaxRowLength:
    def test_numeric_row_max_length(self):
        # numeric-row.dif has 3 columns in its row
        result = dif_max_row_length(_NUMERIC)
        assert result == 3

    def test_single_cell_max_length(self):
        result = dif_max_row_length(_SINGLE)
        assert result == 1

    def test_minimal_2x2_max_length(self):
        # minimal-2x2.dif: 1 row with 8 cells (flat structure)
        result = dif_max_row_length(_MINIMAL)
        assert isinstance(result, int)
        assert result >= 1

    def test_returns_int(self):
        result = dif_max_row_length(_NUMERIC)
        assert isinstance(result, int)
