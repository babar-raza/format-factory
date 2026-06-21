"""
Tests for additional Gnumeric analytics gap closure (2 FOSS gaps).
Closes: GNUMERIC_LON, GNUMERIC_DIS
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_longest_row_index,
    gnumeric_distinct_value_count,
)

_MINIMAL = _REPO / "samples/by-format/gnumeric/minimal-spreadsheet.gnumeric"
_MULTI = _REPO / "samples/by-format/gnumeric/multi-cell-basic.gnumeric"
_EMPTY = _REPO / "samples/by-format/gnumeric/empty-sheet.gnumeric"


class TestGnumericLongestRowIndex:
    def test_returns_int(self):
        assert isinstance(gnumeric_longest_row_index(_MINIMAL), int)

    def test_nonneg_or_minus_one(self):
        result = gnumeric_longest_row_index(_MINIMAL)
        assert result >= -1

    def test_empty_returns_minus_one(self):
        assert gnumeric_longest_row_index(_EMPTY) == -1

    def test_minimal_first_row(self):
        # minimal has content → returns 0 (first row)
        assert gnumeric_longest_row_index(_MINIMAL) == 0


class TestGnumericDistinctValueCount:
    def test_returns_int(self):
        assert isinstance(gnumeric_distinct_value_count(_MINIMAL), int)

    def test_nonnegative(self):
        assert gnumeric_distinct_value_count(_MINIMAL) >= 0

    def test_empty_returns_zero(self):
        assert gnumeric_distinct_value_count(_EMPTY) == 0

    def test_multi_has_distinct_values(self):
        assert gnumeric_distinct_value_count(_MULTI) == 4
