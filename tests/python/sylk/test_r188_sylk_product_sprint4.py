"""Sprint 4 SYLK product tests: find_rows_by_value, sylk_to_html, sylk_max_column_index.

Tests: 15 total
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import find_rows_by_value, sylk_to_html, sylk_max_column_index

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.slk")
_NUMERIC = str(_SAMPLES / "numeric-row.slk")
_SINGLE = str(_SAMPLES / "single-cell.slk")


# ---------------------------------------------------------------------------
# find_rows_by_value (takes file_path, value)
# ---------------------------------------------------------------------------

class TestFindRowsByValue:
    def test_find_string_value(self):
        # minimal-2x2.slk has "Alpha" in row 2
        result = find_rows_by_value(_MINIMAL, "Alpha")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_find_numeric_value(self):
        # minimal-2x2.slk has 42 in row 2
        result = find_rows_by_value(_MINIMAL, 42)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_missing_value_returns_empty(self):
        result = find_rows_by_value(_MINIMAL, "NoSuchValue")
        assert result == []

    def test_returns_list(self):
        result = find_rows_by_value(_MINIMAL, "Alpha")
        assert isinstance(result, list)

    def test_row_indices_are_ints(self):
        result = find_rows_by_value(_MINIMAL, "Alpha")
        for idx in result:
            assert isinstance(idx, int)

    def test_numeric_row_values(self):
        # numeric-row.slk has values 1, 2, 3
        result = find_rows_by_value(_NUMERIC, 1)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_single_cell_find(self):
        # single-cell.slk has one cell — no text values to find directly
        result = find_rows_by_value(_SINGLE, "missing")
        assert result == []


# ---------------------------------------------------------------------------
# sylk_to_html (takes file_path)
# ---------------------------------------------------------------------------

class TestSylkToHtml:
    def test_returns_string(self):
        result = sylk_to_html(_MINIMAL)
        assert isinstance(result, str)

    def test_contains_table_tag(self):
        result = sylk_to_html(_MINIMAL)
        assert "<table>" in result or "<TABLE>" in result.upper()

    def test_contains_cell_values(self):
        result = sylk_to_html(_MINIMAL)
        assert "Alpha" in result
        assert "42" in result

    def test_nonempty_output(self):
        result = sylk_to_html(_NUMERIC)
        assert len(result) > 0

    def test_html_has_tr_tags(self):
        result = sylk_to_html(_MINIMAL)
        assert "<tr>" in result


# ---------------------------------------------------------------------------
# sylk_max_column_index (takes file_path)
# ---------------------------------------------------------------------------

class TestSylkMaxColumnIndex:
    def test_minimal_2x2_has_two_columns(self):
        # minimal-2x2.slk has columns X1 and X2 → max index 2
        result = sylk_max_column_index(_MINIMAL)
        assert result == 2

    def test_numeric_row_has_three_columns(self):
        # numeric-row.slk has X1, X2, X3 → max index 3
        result = sylk_max_column_index(_NUMERIC)
        assert result == 3

    def test_returns_int(self):
        result = sylk_max_column_index(_MINIMAL)
        assert isinstance(result, int)
