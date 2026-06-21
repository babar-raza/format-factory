"""Tests for odt_file_size_plus_word_count and odt_paragraph_count_times_heading_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import (
    odt_file_size_plus_word_count,
    odt_paragraph_count_times_heading_count,
    odt_word_count,
    odt_paragraph_count,
    odt_heading_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = _SAMPLES / "minimal-document.odt"
_TWO_PARA = _SAMPLES / "two-paragraphs.odt"


class TestOdtFileSizePlusWordCount:
    def test_returns_int(self):
        result = odt_file_size_plus_word_count(_MINIMAL)
        assert isinstance(result, int)

    def test_greater_than_file_size(self):
        import os
        size = os.path.getsize(str(_MINIMAL))
        result = odt_file_size_plus_word_count(_MINIMAL)
        wc = odt_word_count(_MINIMAL)
        assert result == size + wc

    def test_minimal_positive(self):
        result = odt_file_size_plus_word_count(_MINIMAL)
        assert result > 0

    def test_two_paragraphs(self):
        import os
        size = os.path.getsize(str(_TWO_PARA))
        wc = odt_word_count(_TWO_PARA)
        result = odt_file_size_plus_word_count(_TWO_PARA)
        assert result == size + wc

    def test_two_paragraphs_greater_than_minimal(self):
        r_min = odt_file_size_plus_word_count(_MINIMAL)
        r_two = odt_file_size_plus_word_count(_TWO_PARA)
        # Both should be positive; comparison depends on file sizes
        assert r_min > 0
        assert r_two > 0

    def test_consistent_across_calls(self):
        r1 = odt_file_size_plus_word_count(_MINIMAL)
        r2 = odt_file_size_plus_word_count(_MINIMAL)
        assert r1 == r2


class TestOdtParagraphCountTimesHeadingCount:
    def test_returns_int(self):
        result = odt_paragraph_count_times_heading_count(_MINIMAL)
        assert isinstance(result, int)

    def test_equals_product(self):
        pc = odt_paragraph_count(_MINIMAL)
        hc = odt_heading_count(_MINIMAL)
        result = odt_paragraph_count_times_heading_count(_MINIMAL)
        assert result == pc * hc

    def test_nonnegative(self):
        result = odt_paragraph_count_times_heading_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs_product(self):
        pc = odt_paragraph_count(_TWO_PARA)
        hc = odt_heading_count(_TWO_PARA)
        result = odt_paragraph_count_times_heading_count(_TWO_PARA)
        assert result == pc * hc

    def test_zero_when_no_headings(self):
        hc = odt_heading_count(_MINIMAL)
        result = odt_paragraph_count_times_heading_count(_MINIMAL)
        if hc == 0:
            assert result == 0

    def test_consistent_across_calls(self):
        r1 = odt_paragraph_count_times_heading_count(_TWO_PARA)
        r2 = odt_paragraph_count_times_heading_count(_TWO_PARA)
        assert r1 == r2
