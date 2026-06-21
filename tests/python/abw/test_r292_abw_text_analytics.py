"""
Tests for ABW text analytics (2 new FOSS functions).
Closes: GAP-ABW-FOSS-ABW_TOTAL-001, GAP-ABW-FOSS-ABW_AVG_P-001

Known sample values:
  empty-section.abw:   0 paragraphs → total_chars=0, avg_para_len=0.0
  minimal-document.abw: 1 para 'Hello' (5) → total_chars=5, avg_para_len=5.0
  two-paragraphs.abw:  2 paras (16+17=33) → total_chars=33, avg_para_len=16.5
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_total_char_count, abw_avg_paragraph_length

_A = _REPO / "samples" / "by-format" / "abw"
_EMPTY = _A / "empty-section.abw"
_MINIMAL = _A / "minimal-document.abw"
_TWO = _A / "two-paragraphs.abw"


class TestAbwTotalCharCount:
    def test_returns_int(self):
        assert isinstance(abw_total_char_count(_EMPTY), int)

    def test_empty_is_zero(self):
        assert abw_total_char_count(_EMPTY) == 0

    def test_minimal_is_five(self):
        assert abw_total_char_count(_MINIMAL) == 5

    def test_two_paragraphs_is_33(self):
        assert abw_total_char_count(_TWO) == 33

    def test_nonnegative(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert abw_total_char_count(p) >= 0

    def test_empty_less_than_minimal(self):
        assert abw_total_char_count(_EMPTY) < abw_total_char_count(_MINIMAL)

    def test_minimal_less_than_two(self):
        assert abw_total_char_count(_MINIMAL) < abw_total_char_count(_TWO)

    def test_all_return_int(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert isinstance(abw_total_char_count(p), int)


class TestAbwAvgParagraphLength:
    def test_returns_float(self):
        assert isinstance(abw_avg_paragraph_length(_EMPTY), float)

    def test_empty_is_zero(self):
        assert abw_avg_paragraph_length(_EMPTY) == 0.0

    def test_minimal_is_five(self):
        assert abw_avg_paragraph_length(_MINIMAL) == 5.0

    def test_two_paragraphs_is_16_5(self):
        assert abw_avg_paragraph_length(_TWO) == 16.5

    def test_nonnegative(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert abw_avg_paragraph_length(p) >= 0.0

    def test_empty_less_than_minimal(self):
        assert abw_avg_paragraph_length(_EMPTY) < abw_avg_paragraph_length(_MINIMAL)

    def test_all_return_float(self):
        for p in [_EMPTY, _MINIMAL, _TWO]:
            assert isinstance(abw_avg_paragraph_length(p), float)
