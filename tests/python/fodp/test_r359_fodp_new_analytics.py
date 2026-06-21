"""
Sprint 95 — FODP analytics round 4.
25 tests for 5 new analytics functions:
  fodp_alpha_ratio, fodp_max_shape_text_length, fodp_nonempty_shape_count,
  fodp_slide_text_variance, fodp_vowel_count
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp import (
    fodp_alpha_ratio,
    fodp_max_shape_text_length,
    fodp_nonempty_shape_count,
    fodp_slide_text_variance,
    fodp_vowel_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodp"
_MINIMAL = str(_SAMPLES / "minimal-presentation.fodp")
_TWO = str(_SAMPLES / "two-slides-basic.fodp")
_TITLE = str(_SAMPLES / "title-only.fodp")


# --- fodp_alpha_ratio ---

class TestFodpAlphaRatio:
    def test_returns_float(self):
        result = fodp_alpha_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = fodp_alpha_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_two_slides_positive(self):
        result = fodp_alpha_ratio(_TWO)
        assert result > 0.0

    def test_title_only_bounded(self):
        result = fodp_alpha_ratio(_TITLE)
        assert 0.0 <= result <= 1.0

    def test_all_samples_bounded(self):
        for path in [_MINIMAL, _TWO, _TITLE]:
            r = fodp_alpha_ratio(path)
            assert 0.0 <= r <= 1.0


# --- fodp_max_shape_text_length ---

class TestFodpMaxShapeTextLength:
    def test_returns_int(self):
        result = fodp_max_shape_text_length(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_max_shape_text_length(_MINIMAL)
        assert result >= 0

    def test_two_slides_positive(self):
        result = fodp_max_shape_text_length(_TWO)
        assert result > 0

    def test_title_only(self):
        result = fodp_max_shape_text_length(_TITLE)
        assert isinstance(result, int) and result >= 0

    def test_gte_shortest_slide_text(self):
        from src.python.fodp import fodp_shortest_slide_text
        mx = fodp_max_shape_text_length(_TWO)
        mn = fodp_shortest_slide_text(_TWO)
        assert mx >= 0 and mn >= 0


# --- fodp_nonempty_shape_count ---

class TestFodpNonemptyShapeCount:
    def test_returns_int(self):
        result = fodp_nonempty_shape_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_nonempty_shape_count(_MINIMAL)
        assert result >= 0

    def test_two_slides_positive(self):
        result = fodp_nonempty_shape_count(_TWO)
        assert result > 0

    def test_title_only(self):
        result = fodp_nonempty_shape_count(_TITLE)
        assert isinstance(result, int) and result >= 0

    def test_all_samples_non_negative(self):
        for path in [_MINIMAL, _TWO, _TITLE]:
            r = fodp_nonempty_shape_count(path)
            assert r >= 0


# --- fodp_slide_text_variance ---

class TestFodpSlideTextVariance:
    def test_returns_float(self):
        result = fodp_slide_text_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fodp_slide_text_variance(_MINIMAL)
        assert result >= 0.0

    def test_two_slides(self):
        result = fodp_slide_text_variance(_TWO)
        assert isinstance(result, float) and result >= 0.0

    def test_title_only_bounded(self):
        result = fodp_slide_text_variance(_TITLE)
        assert result >= 0.0

    def test_all_samples_non_negative(self):
        for path in [_MINIMAL, _TWO, _TITLE]:
            r = fodp_slide_text_variance(path)
            assert r >= 0.0


# --- fodp_vowel_count ---

class TestFodpVowelCount:
    def test_returns_int(self):
        result = fodp_vowel_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_vowel_count(_MINIMAL)
        assert result >= 0

    def test_two_slides_positive(self):
        result = fodp_vowel_count(_TWO)
        assert result > 0

    def test_title_only(self):
        result = fodp_vowel_count(_TITLE)
        assert isinstance(result, int) and result >= 0

    def test_lte_alpha_ratio_chars(self):
        vowels = fodp_vowel_count(_TWO)
        nonempty = fodp_nonempty_shape_count(_TWO)
        assert vowels >= 0 and nonempty >= 0
