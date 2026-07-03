"""
Tests for additional SYLK analytics gap closure (2 FOSS gaps).
Closes: GAP-SYLK-FOSS-SYLK_STRING_-001, GAP-SYLK-FOSS-SYLK_VALUE_L-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_analytics import (
    sylk_string_value_count,
    sylk_value_length_sum,
)

_SLK_2x2 = _REPO / "samples/by-format/sylk/valid/minimal-2x2.slk"
_SLK_NUMERIC = _REPO / "samples/by-format/sylk/valid/numeric-row.slk"


class TestSylkStringValueCount:
    def test_returns_int(self):
        assert isinstance(sylk_string_value_count(_SLK_2x2), int)

    def test_nonnegative(self):
        assert sylk_string_value_count(_SLK_2x2) >= 0

    def test_2x2_has_string_cells(self):
        # minimal-2x2 has 3 string cells
        assert sylk_string_value_count(_SLK_2x2) == 3

    def test_numeric_fewer_strings(self):
        # numeric-row is all numeric → fewer string cells
        assert sylk_string_value_count(_SLK_NUMERIC) <= sylk_string_value_count(_SLK_2x2)


class TestSylkValueLengthSum:
    def test_returns_int(self):
        assert isinstance(sylk_value_length_sum(_SLK_2x2), int)

    def test_nonnegative(self):
        assert sylk_value_length_sum(_SLK_2x2) >= 0

    def test_2x2_exact(self):
        assert sylk_value_length_sum(_SLK_2x2) == 16

    def test_numeric_nonneg(self):
        assert sylk_value_length_sum(_SLK_NUMERIC) >= 0
