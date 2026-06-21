"""
test_r327_tsv_new_analytics.py
Sprint 63 — 5 new TSV analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_file_size_bytes,
    tsv_max_field_length,
    tsv_avg_field_length,
    tsv_nonempty_field_count,
    tsv_unique_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.tsv")
_MULTI = str(_SAMPLES / "multi-column.tsv")
_SINGLE = str(_SAMPLES / "single-cell.tsv")


# --- tsv_file_size_bytes ---

class TestTsvFileSizeBytes:
    def test_minimal_positive(self):
        assert tsv_file_size_bytes(_MINIMAL) > 0

    def test_multi_positive(self):
        assert tsv_file_size_bytes(_MULTI) > 0

    def test_single_positive(self):
        assert tsv_file_size_bytes(_SINGLE) > 0

    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert tsv_file_size_bytes(_MINIMAL) >= 5


# --- tsv_max_field_length ---

class TestTsvMaxFieldLength:
    def test_returns_int(self):
        assert isinstance(tsv_max_field_length(_MINIMAL), int)

    def test_minimal_positive(self):
        assert tsv_max_field_length(_MINIMAL) >= 1

    def test_multi_positive(self):
        assert tsv_max_field_length(_MULTI) >= 1

    def test_single_positive(self):
        assert tsv_max_field_length(_SINGLE) >= 1

    def test_max_ge_avg(self):
        assert tsv_max_field_length(_MINIMAL) >= tsv_avg_field_length(_MINIMAL)


# --- tsv_avg_field_length ---

class TestTsvAvgFieldLength:
    def test_returns_float(self):
        assert isinstance(tsv_avg_field_length(_MINIMAL), float)

    def test_minimal_positive(self):
        assert tsv_avg_field_length(_MINIMAL) > 0.0

    def test_multi_positive(self):
        assert tsv_avg_field_length(_MULTI) > 0.0

    def test_single_positive(self):
        assert tsv_avg_field_length(_SINGLE) > 0.0

    def test_avg_le_max(self):
        assert tsv_avg_field_length(_MINIMAL) <= tsv_max_field_length(_MINIMAL)


# --- tsv_nonempty_field_count ---

class TestTsvNonemptyFieldCount:
    def test_returns_int(self):
        assert isinstance(tsv_nonempty_field_count(_MINIMAL), int)

    def test_minimal_positive(self):
        assert tsv_nonempty_field_count(_MINIMAL) >= 1

    def test_multi_positive(self):
        assert tsv_nonempty_field_count(_MULTI) >= 1

    def test_single_positive(self):
        assert tsv_nonempty_field_count(_SINGLE) >= 1

    def test_non_negative(self):
        assert tsv_nonempty_field_count(_MINIMAL) >= 0


# --- tsv_unique_row_count ---

class TestTsvUniqueRowCount:
    def test_returns_int(self):
        assert isinstance(tsv_unique_row_count(_MINIMAL), int)

    def test_minimal_at_least_one(self):
        assert tsv_unique_row_count(_MINIMAL) >= 1

    def test_multi_at_least_one(self):
        assert tsv_unique_row_count(_MULTI) >= 1

    def test_single_at_least_one(self):
        assert tsv_unique_row_count(_SINGLE) >= 1

    def test_non_negative(self):
        assert tsv_unique_row_count(_MINIMAL) >= 0
