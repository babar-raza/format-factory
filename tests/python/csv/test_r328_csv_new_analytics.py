"""
test_r328_csv_new_analytics.py
Sprint 64 — 5 new CSV analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_file_size_bytes,
    csv_avg_field_length,
    csv_nonempty_field_count,
    csv_unique_row_count,
    csv_max_numeric_value,
)

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.csv")
_NUMERIC = str(_SAMPLES / "quoted-fields.csv")
_SINGLE = str(_SAMPLES / "single-cell.csv")


# --- csv_file_size_bytes ---

class TestCsvFileSizeBytes:
    def test_minimal_positive(self):
        assert csv_file_size_bytes(_MINIMAL) > 0

    def test_numeric_positive(self):
        assert csv_file_size_bytes(_NUMERIC) > 0

    def test_single_positive(self):
        assert csv_file_size_bytes(_SINGLE) > 0

    def test_returns_int(self):
        assert isinstance(csv_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert csv_file_size_bytes(_MINIMAL) >= 5


# --- csv_avg_field_length ---

class TestCsvAvgFieldLength:
    def test_returns_float(self):
        assert isinstance(csv_avg_field_length(_MINIMAL), float)

    def test_minimal_positive(self):
        assert csv_avg_field_length(_MINIMAL) > 0.0

    def test_numeric_positive(self):
        assert csv_avg_field_length(_NUMERIC) > 0.0

    def test_single_positive(self):
        assert csv_avg_field_length(_SINGLE) > 0.0

    def test_non_negative(self):
        assert csv_avg_field_length(_MINIMAL) >= 0.0


# --- csv_nonempty_field_count ---

class TestCsvNonemptyFieldCount:
    def test_returns_int(self):
        assert isinstance(csv_nonempty_field_count(_MINIMAL), int)

    def test_minimal_positive(self):
        assert csv_nonempty_field_count(_MINIMAL) >= 1

    def test_numeric_positive(self):
        assert csv_nonempty_field_count(_NUMERIC) >= 1

    def test_single_positive(self):
        assert csv_nonempty_field_count(_SINGLE) >= 1

    def test_non_negative(self):
        assert csv_nonempty_field_count(_MINIMAL) >= 0


# --- csv_unique_row_count ---

class TestCsvUniqueRowCount:
    def test_returns_int(self):
        assert isinstance(csv_unique_row_count(_MINIMAL), int)

    def test_minimal_at_least_one(self):
        assert csv_unique_row_count(_MINIMAL) >= 1

    def test_numeric_at_least_one(self):
        assert csv_unique_row_count(_NUMERIC) >= 1

    def test_single_at_least_one(self):
        assert csv_unique_row_count(_SINGLE) >= 1

    def test_non_negative(self):
        assert csv_unique_row_count(_MINIMAL) >= 0


# --- csv_max_numeric_value ---

class TestCsvMaxNumericValue:
    def test_returns_float(self):
        assert isinstance(csv_max_numeric_value(_NUMERIC), float)

    def test_numeric_positive(self):
        assert csv_max_numeric_value(_NUMERIC) > 0.0

    def test_minimal_non_negative(self):
        assert csv_max_numeric_value(_MINIMAL) >= 0.0

    def test_single_non_negative(self):
        assert csv_max_numeric_value(_SINGLE) >= 0.0

    def test_non_negative(self):
        assert csv_max_numeric_value(_NUMERIC) >= 0.0
