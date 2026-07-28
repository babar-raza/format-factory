"""Tests for csv_row_count and csv_average_field_length.

Product deepening: CSV analytics — TC-H3-002-CSV / PDC-CSV-ROW-COUNT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_row_count, csv_average_field_length


def _make_csv(tmp_path, name, content):
    """Write raw CSV content to a file."""
    path = tmp_path / f"{name}.csv"
    path.write_text(content, encoding="utf-8")
    return path


class TestCsvRowCount:
    def test_single_row(self, tmp_path):
        f = _make_csv(tmp_path, "one", "a\n")
        assert csv_row_count(f) == 1

    def test_three_rows(self, tmp_path):
        f = _make_csv(tmp_path, "three", "a,b\nc,d\ne,f\n")
        assert csv_row_count(f) == 3

    def test_empty_file(self, tmp_path):
        f = _make_csv(tmp_path, "empty", "")
        assert csv_row_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_csv(tmp_path, "type", "x\n")
        assert isinstance(csv_row_count(f), int)

    def test_five_rows(self, tmp_path):
        f = _make_csv(tmp_path, "five", "1\n2\n3\n4\n5\n")
        assert csv_row_count(f) == 5

    def test_with_header(self, tmp_path):
        f = _make_csv(tmp_path, "hdr", "name,age\nalice,30\nbob,25\n")
        result = csv_row_count(f)
        assert isinstance(result, int)
        assert result >= 2


class TestCsvAverageFieldLength:
    def test_single_field(self, tmp_path):
        f = _make_csv(tmp_path, "sf", "hello\n")
        result = csv_average_field_length(f)
        assert result == 5.0

    def test_two_fields(self, tmp_path):
        f = _make_csv(tmp_path, "two", "ab,cdef\n")
        # "ab"=2, "cdef"=4 → avg=3.0
        assert csv_average_field_length(f) == 3.0

    def test_returns_float(self, tmp_path):
        f = _make_csv(tmp_path, "type2", "x\n")
        assert isinstance(csv_average_field_length(f), float)

    def test_multiple_rows(self, tmp_path):
        f = _make_csv(tmp_path, "multi", "abc\nde\nf\n")
        # lengths: 3, 2, 1 → avg=2.0
        assert csv_average_field_length(f) == 2.0

    def test_positive_for_data(self, tmp_path):
        f = _make_csv(tmp_path, "pos", "hello,world\n")
        assert csv_average_field_length(f) > 0
