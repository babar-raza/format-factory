"""Tests for odt_word_count_squared and odt_heading_count_plus_paragraph_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import (
    odt_word_count_squared,
    odt_heading_count_plus_paragraph_count,
    odt_word_count,
    odt_heading_count,
    odt_paragraph_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = _SAMPLES / "minimal-document.odt"
_TWO_PARA = _SAMPLES / "two-paragraphs.odt"


class TestOdtWordCountSquared:
    def test_returns_int(self):
        assert isinstance(odt_word_count_squared(_MINIMAL), int)

    def test_matches_formula(self):
        wc = odt_word_count(_MINIMAL)
        assert odt_word_count_squared(_MINIMAL) == wc * wc

    def test_nonnegative(self):
        assert odt_word_count_squared(_MINIMAL) >= 0

    def test_two_paragraphs(self):
        wc = odt_word_count(_TWO_PARA)
        assert odt_word_count_squared(_TWO_PARA) == wc * wc

    def test_consistent(self):
        assert odt_word_count_squared(_MINIMAL) == odt_word_count_squared(_MINIMAL)


class TestOdtHeadingCountPlusParagraphCount:
    def test_returns_int(self):
        assert isinstance(odt_heading_count_plus_paragraph_count(_MINIMAL), int)

    def test_matches_sum(self):
        hc = odt_heading_count(_MINIMAL)
        pc = odt_paragraph_count(_MINIMAL)
        assert odt_heading_count_plus_paragraph_count(_MINIMAL) == hc + pc

    def test_positive(self):
        assert odt_heading_count_plus_paragraph_count(_MINIMAL) >= 0

    def test_two_paragraphs(self):
        hc = odt_heading_count(_TWO_PARA)
        pc = odt_paragraph_count(_TWO_PARA)
        assert odt_heading_count_plus_paragraph_count(_TWO_PARA) == hc + pc

    def test_consistent(self):
        assert odt_heading_count_plus_paragraph_count(_TWO_PARA) == odt_heading_count_plus_paragraph_count(_TWO_PARA)
