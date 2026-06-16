"""Tests for csv_is_single_column and csv_is_all_numeric (Sprint 47)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_is_single_column, csv_is_all_numeric

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")    # [['Alice', '30'], ['Bob', '25']] — 2 cols, not all numeric
_SINGLE = str(_DIR / "single-cell.csv")      # [['42']] — 1 col, all numeric
_QUOTED = str(_DIR / "quoted-fields.csv")    # 3 cols, strings+price — not single col, not all numeric


class TestCsvIsSingleColumn:
    def test_return_type(self):
        assert isinstance(csv_is_single_column(_MINIMAL), bool)

    def test_false_for_minimal_2x2(self):
        # minimal-2x2.csv has 2 columns — not single
        assert csv_is_single_column(_MINIMAL) is False

    def test_true_for_single_cell(self):
        # single-cell.csv has 1 column
        assert csv_is_single_column(_SINGLE) is True

    def test_false_for_quoted_fields(self):
        # quoted-fields.csv has 3 columns
        assert csv_is_single_column(_QUOTED) is False

    def test_consistent_across_calls(self):
        assert csv_is_single_column(_SINGLE) == csv_is_single_column(_SINGLE)

    def test_single_column_implies_max_row_len_1(self):
        from src.python.csv.csv_parser import csv_max_row_length
        if csv_is_single_column(_SINGLE):
            assert csv_max_row_length(_SINGLE) == 1


class TestCsvIsAllNumeric:
    def test_return_type(self):
        assert isinstance(csv_is_all_numeric(_MINIMAL), bool)

    def test_false_for_minimal_2x2(self):
        # minimal-2x2.csv has 'Alice', 'Bob' which are not numeric
        assert csv_is_all_numeric(_MINIMAL) is False

    def test_true_for_single_cell(self):
        # single-cell.csv has only '42' — numeric
        assert csv_is_all_numeric(_SINGLE) is True

    def test_false_for_quoted_fields(self):
        # quoted-fields.csv has string descriptions
        assert csv_is_all_numeric(_QUOTED) is False

    def test_consistent_across_calls(self):
        assert csv_is_all_numeric(_SINGLE) == csv_is_all_numeric(_SINGLE)

    def test_all_numeric_implies_no_string_cells(self):
        from src.python.csv.csv_parser import csv_string_density
        if csv_is_all_numeric(_SINGLE):
            assert csv_string_density(_SINGLE) == 0.0
