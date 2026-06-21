"""
Tests for CSV field analytics (2 new FOSS functions).
Closes: GAP-CSV-FOSS-CSV_STRI-001, GAP-CSV-FOSS-CSV_MAX_S-001

Known sample values:
  single-cell.csv:   [['42']] → string_field_count=0, max_string_field_length=0
  minimal-2x2.csv:   [['Alice','30'],['Bob','25']] → string_field_count=2, max_string_field_length=5
  quoted-fields.csv: 2 rows, 3 fields each, strings → string_field_count=4, max_string_field_length=22
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_string_field_count, csv_max_string_field_length

_C = _REPO / "samples" / "by-format" / "csv"
_SINGLE = _C / "single-cell.csv"
_MINIMAL = _C / "minimal-2x2.csv"
_QUOTED = _C / "quoted-fields.csv"


class TestCsvStringFieldCount:
    def test_returns_int(self):
        assert isinstance(csv_string_field_count(_SINGLE), int)

    def test_all_numeric_is_zero(self):
        # single-cell.csv has only '42' which is numeric
        assert csv_string_field_count(_SINGLE) == 0

    def test_minimal_has_two_strings(self):
        # Alice and Bob are strings
        assert csv_string_field_count(_MINIMAL) == 2

    def test_quoted_has_four_strings(self):
        # 'Widget A', 'A simple widget, small', 'Widget B', 'A fancy widget' are strings
        assert csv_string_field_count(_QUOTED) == 4

    def test_nonnegative(self):
        for p in [_SINGLE, _MINIMAL, _QUOTED]:
            assert csv_string_field_count(p) >= 0

    def test_single_less_than_minimal(self):
        assert csv_string_field_count(_SINGLE) < csv_string_field_count(_MINIMAL)

    def test_all_return_int(self):
        for p in [_SINGLE, _MINIMAL, _QUOTED]:
            assert isinstance(csv_string_field_count(p), int)


class TestCsvMaxStringFieldLength:
    def test_returns_int(self):
        assert isinstance(csv_max_string_field_length(_SINGLE), int)

    def test_no_string_fields_is_zero(self):
        assert csv_max_string_field_length(_SINGLE) == 0

    def test_minimal_is_five(self):
        # 'Alice' has length 5
        assert csv_max_string_field_length(_MINIMAL) == 5

    def test_quoted_is_22(self):
        # 'A simple widget, small' has length 22
        assert csv_max_string_field_length(_QUOTED) == 22

    def test_nonnegative(self):
        for p in [_SINGLE, _MINIMAL, _QUOTED]:
            assert csv_max_string_field_length(p) >= 0

    def test_single_less_than_minimal(self):
        assert csv_max_string_field_length(_SINGLE) < csv_max_string_field_length(_MINIMAL)

    def test_all_return_int(self):
        for p in [_SINGLE, _MINIMAL, _QUOTED]:
            assert isinstance(csv_max_string_field_length(p), int)
