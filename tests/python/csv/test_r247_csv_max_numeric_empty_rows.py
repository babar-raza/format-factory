"""Tests for csv_max_numeric_value and csv_has_empty_rows (Sprint 37)."""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_max_numeric_value, csv_has_empty_rows

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_CSV_DIR / "minimal-2x2.csv")   # Alice,30 / Bob,25 -> max=30.0
_QUOTED = str(_CSV_DIR / "quoted-fields.csv")   # prices 9.99, 19.99 -> max=19.99
_SINGLE = str(_CSV_DIR / "single-cell.csv")     # 42 -> max=42.0


def _write_csv(tmp_path, content: str) -> str:
    p = tmp_path / "test.csv"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestCsvMaxNumericValue:
    def test_return_type_for_numeric_file(self):
        result = csv_max_numeric_value(_MINIMAL)
        assert isinstance(result, float)

    def test_exact_30_for_minimal(self):
        # minimal-2x2.csv: Alice,30 / Bob,25 -> max=30.0
        assert csv_max_numeric_value(_MINIMAL) == 30.0

    def test_exact_19_99_for_quoted(self):
        # quoted-fields.csv prices: 9.99, 19.99 -> max=19.99
        assert csv_max_numeric_value(_QUOTED) == 19.99

    def test_exact_42_for_single(self):
        # single-cell.csv has one cell: 42
        assert csv_max_numeric_value(_SINGLE) == 42.0

    def test_none_for_text_only(self, tmp_path):
        p = _write_csv(tmp_path, "Alice,Bob\nCarol,Dave\n")
        assert csv_max_numeric_value(p) is None

    def test_none_for_empty_file(self, tmp_path):
        p = _write_csv(tmp_path, "")
        assert csv_max_numeric_value(p) is None

    def test_handles_negative_numbers(self, tmp_path):
        p = _write_csv(tmp_path, "-5,10,-20\n")
        assert csv_max_numeric_value(p) == 10.0

    def test_consistent_across_calls(self):
        assert csv_max_numeric_value(_MINIMAL) == csv_max_numeric_value(_MINIMAL)


class TestCsvHasEmptyRows:
    def test_return_type(self):
        result = csv_has_empty_rows(_MINIMAL)
        assert isinstance(result, bool)

    def test_false_for_minimal_no_empty_rows(self):
        assert csv_has_empty_rows(_MINIMAL) is False

    def test_false_for_quoted_fields(self):
        assert csv_has_empty_rows(_QUOTED) is False

    def test_true_for_file_with_empty_row(self, tmp_path):
        p = _write_csv(tmp_path, "Alice,30\n,\nBob,25\n")
        assert csv_has_empty_rows(p) is True

    def test_false_for_single_cell(self):
        assert csv_has_empty_rows(_SINGLE) is False

    def test_true_for_blank_line(self, tmp_path):
        p = _write_csv(tmp_path, "Alice,30\n\nBob,25\n")
        assert csv_has_empty_rows(p) is True

    def test_consistent_across_calls(self):
        assert csv_has_empty_rows(_MINIMAL) == csv_has_empty_rows(_MINIMAL)
