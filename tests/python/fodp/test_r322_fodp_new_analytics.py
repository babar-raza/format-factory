"""
test_r322_fodp_new_analytics.py
Sprint 58 — 5 new FODP analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import (
    fodp_file_size_bytes,
    fodp_max_slide_text_length,
    fodp_min_slide_text_length,
    fodp_unique_slide_title_count,
    fodp_avg_shape_text_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodp"
_MINIMAL = str(_SAMPLES / "minimal-presentation.fodp")
_TITLE = str(_SAMPLES / "title-only.fodp")
_TWO = str(_SAMPLES / "two-slides-basic.fodp")


# --- fodp_file_size_bytes ---

class TestFodpFileSizeBytes:
    def test_minimal_positive(self):
        assert fodp_file_size_bytes(_MINIMAL) > 0

    def test_title_positive(self):
        assert fodp_file_size_bytes(_TITLE) > 0

    def test_two_positive(self):
        assert fodp_file_size_bytes(_TWO) > 0

    def test_returns_int(self):
        assert isinstance(fodp_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert fodp_file_size_bytes(_MINIMAL) >= 100


# --- fodp_max_slide_text_length ---

class TestFodpMaxSlideTextLength:
    def test_returns_int(self):
        assert isinstance(fodp_max_slide_text_length(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert fodp_max_slide_text_length(_MINIMAL) >= 0

    def test_title_non_negative(self):
        assert fodp_max_slide_text_length(_TITLE) >= 0

    def test_two_non_negative(self):
        assert fodp_max_slide_text_length(_TWO) >= 0

    def test_max_ge_min(self):
        assert fodp_max_slide_text_length(_TWO) >= fodp_min_slide_text_length(_TWO)


# --- fodp_min_slide_text_length ---

class TestFodpMinSlideTextLength:
    def test_returns_int(self):
        assert isinstance(fodp_min_slide_text_length(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert fodp_min_slide_text_length(_MINIMAL) >= 0

    def test_title_non_negative(self):
        assert fodp_min_slide_text_length(_TITLE) >= 0

    def test_two_non_negative(self):
        assert fodp_min_slide_text_length(_TWO) >= 0

    def test_min_le_max(self):
        assert fodp_min_slide_text_length(_TWO) <= fodp_max_slide_text_length(_TWO)


# --- fodp_unique_slide_title_count ---

class TestFodpUniqueSlideTitleCount:
    def test_returns_int(self):
        assert isinstance(fodp_unique_slide_title_count(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert fodp_unique_slide_title_count(_MINIMAL) >= 0

    def test_two_at_least_zero(self):
        assert fodp_unique_slide_title_count(_TWO) >= 0

    def test_two_non_negative(self):
        assert fodp_unique_slide_title_count(_TWO) >= 0

    def test_non_negative(self):
        assert fodp_unique_slide_title_count(_MINIMAL) >= 0


# --- fodp_avg_shape_text_length ---

class TestFodpAvgShapeTextLength:
    def test_returns_float(self):
        assert isinstance(fodp_avg_shape_text_length(_MINIMAL), float)

    def test_minimal_non_negative(self):
        assert fodp_avg_shape_text_length(_MINIMAL) >= 0.0

    def test_title_non_negative(self):
        assert fodp_avg_shape_text_length(_TITLE) >= 0.0

    def test_two_non_negative(self):
        assert fodp_avg_shape_text_length(_TWO) >= 0.0

    def test_non_negative(self):
        assert fodp_avg_shape_text_length(_MINIMAL) >= 0.0
