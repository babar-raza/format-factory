"""Tests for ABW Sprint 135 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_ALPHA_RA-001   (Abw Alpha Ratio)
  GAP-ABW-FOSS-ABW_SHORT_PA-001   (Abw Short Paragraph Count)
  GAP-ABW-FOSS-ABW_TOTAL_PA-001   (Abw Total Para Char Count)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_alpha_ratio, abw_short_paragraph_count, abw_total_para_char_count

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO = str(_DIR / "two-paragraphs.abw")


class TestAbwAlphaRatio:
    def test_return_type(self):
        assert isinstance(abw_alpha_ratio(_EMPTY), (int, float))

    def test_exact_0_for_empty(self):
        assert abw_alpha_ratio(_EMPTY) == pytest.approx(0.0)

    def test_exact_1_for_minimal(self):
        assert abw_alpha_ratio(_MINIMAL) == pytest.approx(1.0)

    def test_approx_879_for_two(self):
        assert abw_alpha_ratio(_TWO) == pytest.approx(0.8788, rel=1e-2)

    def test_between_0_and_1(self):
        assert 0.0 <= abw_alpha_ratio(_MINIMAL) <= 1.0

    def test_consistent(self):
        assert abw_alpha_ratio(_EMPTY) == abw_alpha_ratio(_EMPTY)


class TestAbwShortParagraphCount:
    def test_return_type(self):
        assert isinstance(abw_short_paragraph_count(_EMPTY), int)

    def test_exact_0_for_empty(self):
        assert abw_short_paragraph_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        assert abw_short_paragraph_count(_MINIMAL) == 1

    def test_exact_2_for_two(self):
        assert abw_short_paragraph_count(_TWO) == 2

    def test_nonnegative(self):
        assert abw_short_paragraph_count(_EMPTY) >= 0

    def test_consistent(self):
        assert abw_short_paragraph_count(_MINIMAL) == abw_short_paragraph_count(_MINIMAL)


class TestAbwTotalParaCharCount:
    def test_return_type(self):
        assert isinstance(abw_total_para_char_count(_EMPTY), int)

    def test_exact_0_for_empty(self):
        assert abw_total_para_char_count(_EMPTY) == 0

    def test_exact_5_for_minimal(self):
        assert abw_total_para_char_count(_MINIMAL) == 5

    def test_exact_33_for_two(self):
        assert abw_total_para_char_count(_TWO) == 33

    def test_nonnegative(self):
        assert abw_total_para_char_count(_EMPTY) >= 0

    def test_consistent(self):
        assert abw_total_para_char_count(_MINIMAL) == abw_total_para_char_count(_MINIMAL)
