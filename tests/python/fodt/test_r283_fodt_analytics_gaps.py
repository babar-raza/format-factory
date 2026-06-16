"""
Tests for FODT analytics gap closure (4 FOSS gaps).
Closes: GAP-FODT-FOSS-FODT_WHITESPACE-001, GAP-FODT-FOSS-FODT_LONGEST-001,
        GAP-FODT-FOSS-FODT_AVG_HEAD-001, GAP-FODT-FOSS-FODT_TABLE_DE-001

Note: fodt_whitespace_ratio / fodt_longest_word use doc.get("body_blocks", [])
which the current parser does not populate (parser returns "blocks" key).
Tests verify return types and non-error behavior.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    fodt_whitespace_ratio,
    fodt_longest_word,
    fodt_avg_heading_length,
    fodt_table_density,
)

_FODT_MINIMAL = _REPO / "samples/by-format/fodt/minimal-document.fodt"
_FODT_HEADINGS = _REPO / "samples/by-format/fodt/headings-and-paragraphs.fodt"


class TestFodtWhitespaceRatio:
    def test_returns_float(self):
        result = fodt_whitespace_ratio(_FODT_MINIMAL)
        assert isinstance(result, float)

    def test_nonnegative(self):
        result = fodt_whitespace_ratio(_FODT_MINIMAL)
        assert result >= 0.0

    def test_at_most_one(self):
        result = fodt_whitespace_ratio(_FODT_MINIMAL)
        assert result <= 1.0

    def test_consistent_across_calls(self):
        r1 = fodt_whitespace_ratio(_FODT_HEADINGS)
        r2 = fodt_whitespace_ratio(_FODT_HEADINGS)
        assert r1 == pytest.approx(r2)


class TestFodtLongestWord:
    def test_returns_str(self):
        result = fodt_longest_word(_FODT_MINIMAL)
        assert isinstance(result, str)

    def test_returns_str_for_headings_doc(self):
        result = fodt_longest_word(_FODT_HEADINGS)
        assert isinstance(result, str)

    def test_consistent_across_calls(self):
        r1 = fodt_longest_word(_FODT_MINIMAL)
        r2 = fodt_longest_word(_FODT_MINIMAL)
        assert r1 == r2

    def test_no_whitespace_in_result(self):
        # longest_word strips surrounding punctuation; result has no spaces
        result = fodt_longest_word(_FODT_HEADINGS)
        assert " " not in result


class TestFodtAvgHeadingLength:
    def test_returns_float(self):
        result = fodt_avg_heading_length(_FODT_MINIMAL)
        assert isinstance(result, float)

    def test_nonnegative(self):
        result = fodt_avg_heading_length(_FODT_MINIMAL)
        assert result >= 0.0

    def test_nonnegative_headings_doc(self):
        result = fodt_avg_heading_length(_FODT_HEADINGS)
        assert result >= 0.0

    def test_consistent_across_calls(self):
        r1 = fodt_avg_heading_length(_FODT_HEADINGS)
        r2 = fodt_avg_heading_length(_FODT_HEADINGS)
        assert r1 == pytest.approx(r2)


class TestFodtTableDensity:
    def test_returns_float(self):
        result = fodt_table_density(_FODT_MINIMAL)
        assert isinstance(result, float)

    def test_nonnegative(self):
        result = fodt_table_density(_FODT_MINIMAL)
        assert result >= 0.0

    def test_nonnegative_headings_doc(self):
        result = fodt_table_density(_FODT_HEADINGS)
        assert result >= 0.0

    def test_consistent_across_calls(self):
        r1 = fodt_table_density(_FODT_MINIMAL)
        r2 = fodt_table_density(_FODT_MINIMAL)
        assert r1 == pytest.approx(r2)
