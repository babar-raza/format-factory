"""
test_r326_dif_new_analytics.py
Sprint 62 — 5 new DIF analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_file_size_bytes,
    dif_max_numeric_value,
    dif_min_numeric_value,
    dif_avg_numeric_value,
    dif_unique_row_count,
)

_VALID = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_VALID / "minimal-2x2.dif")
_NUMERIC = str(_VALID / "numeric-row.dif")
_SINGLE = str(_VALID / "single-cell.dif")


# --- dif_file_size_bytes ---

class TestDifFileSizeBytes:
    def test_minimal_positive(self):
        assert dif_file_size_bytes(_MINIMAL) > 0

    def test_numeric_positive(self):
        assert dif_file_size_bytes(_NUMERIC) > 0

    def test_single_positive(self):
        assert dif_file_size_bytes(_SINGLE) > 0

    def test_returns_int(self):
        assert isinstance(dif_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert dif_file_size_bytes(_MINIMAL) >= 50


# --- dif_max_numeric_value ---

class TestDifMaxNumericValue:
    def test_returns_float(self):
        assert isinstance(dif_max_numeric_value(_NUMERIC), float)

    def test_numeric_non_negative(self):
        assert dif_max_numeric_value(_NUMERIC) >= 0.0

    def test_minimal_non_negative(self):
        assert dif_max_numeric_value(_MINIMAL) >= 0.0

    def test_max_ge_min(self):
        assert dif_max_numeric_value(_NUMERIC) >= dif_min_numeric_value(_NUMERIC)

    def test_single_non_negative(self):
        assert dif_max_numeric_value(_SINGLE) >= 0.0


# --- dif_min_numeric_value ---

class TestDifMinNumericValue:
    def test_returns_float(self):
        assert isinstance(dif_min_numeric_value(_NUMERIC), float)

    def test_numeric_non_negative(self):
        assert dif_min_numeric_value(_NUMERIC) >= 0.0

    def test_minimal_non_negative(self):
        assert dif_min_numeric_value(_MINIMAL) >= 0.0

    def test_min_le_max(self):
        assert dif_min_numeric_value(_NUMERIC) <= dif_max_numeric_value(_NUMERIC)

    def test_single_non_negative(self):
        assert dif_min_numeric_value(_SINGLE) >= 0.0


# --- dif_avg_numeric_value ---

class TestDifAvgNumericValue:
    def test_returns_float(self):
        assert isinstance(dif_avg_numeric_value(_NUMERIC), float)

    def test_numeric_non_negative(self):
        assert dif_avg_numeric_value(_NUMERIC) >= 0.0

    def test_minimal_non_negative(self):
        assert dif_avg_numeric_value(_MINIMAL) >= 0.0

    def test_avg_between_min_max(self):
        mn = dif_min_numeric_value(_NUMERIC)
        avg = dif_avg_numeric_value(_NUMERIC)
        mx = dif_max_numeric_value(_NUMERIC)
        assert mn <= avg <= mx

    def test_single_non_negative(self):
        assert dif_avg_numeric_value(_SINGLE) >= 0.0


# --- dif_unique_row_count ---

class TestDifUniqueRowCount:
    def test_returns_int(self):
        assert isinstance(dif_unique_row_count(_MINIMAL), int)

    def test_minimal_at_least_one(self):
        assert dif_unique_row_count(_MINIMAL) >= 1

    def test_numeric_at_least_one(self):
        assert dif_unique_row_count(_NUMERIC) >= 1

    def test_single_at_least_one(self):
        assert dif_unique_row_count(_SINGLE) >= 1

    def test_non_negative(self):
        assert dif_unique_row_count(_MINIMAL) >= 0
