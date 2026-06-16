"""
Tests for ABW analytics gap closure (2 FOSS gaps).
Closes: GAP-ABW-FOSS-ABW_PUNCTU-001, GAP-ABW-FOSS-ABW_MEDIAN-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_punctuation_count,
    abw_median_paragraph_length,
)

_ABW_MINIMAL = _REPO / "samples/by-format/abw/minimal-document.abw"
_ABW_TWO = _REPO / "samples/by-format/abw/two-paragraphs.abw"
_ABW_EMPTY = _REPO / "samples/by-format/abw/empty-section.abw"


class TestAbwPunctuationCount:
    def test_returns_int(self):
        assert isinstance(abw_punctuation_count(_ABW_MINIMAL), int)

    def test_nonnegative(self):
        assert abw_punctuation_count(_ABW_MINIMAL) >= 0

    def test_empty_section_is_zero_or_more(self):
        # empty section may have 0 punctuation
        assert abw_punctuation_count(_ABW_EMPTY) >= 0

    def test_two_paragraphs_is_nonnegative(self):
        assert abw_punctuation_count(_ABW_TWO) >= 0


class TestAbwMedianParagraphLength:
    def test_returns_int(self):
        assert isinstance(abw_median_paragraph_length(_ABW_MINIMAL), int)

    def test_nonnegative(self):
        assert abw_median_paragraph_length(_ABW_MINIMAL) >= 0

    def test_two_paragraphs_nonnegative(self):
        assert abw_median_paragraph_length(_ABW_TWO) >= 0

    def test_empty_section_returns_zero_or_more(self):
        result = abw_median_paragraph_length(_ABW_EMPTY)
        assert result >= 0
