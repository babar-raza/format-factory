"""Sprint R290D: FODP analytics deepening — total_word_count, max_word_count_per_slide, avg_slide_shape_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import (
    fodp_total_word_count,
    fodp_max_word_count_per_slide,
    fodp_avg_slide_shape_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodp"
MINIMAL = SAMPLES / "minimal-presentation.fodp"
TWO_SLIDES = SAMPLES / "two-slides-basic.fodp"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("FODP sample not available")
    return MINIMAL


@pytest.fixture
def two_slide_sample():
    if not TWO_SLIDES.exists():
        pytest.skip("FODP two-slide sample not available")
    return TWO_SLIDES


class TestFodpTotalWordCount:
    def test_returns_int(self, sample):
        assert isinstance(fodp_total_word_count(sample), int)

    def test_nonnegative(self, sample):
        assert fodp_total_word_count(sample) >= 0


class TestFodpMaxWordCountPerSlide:
    def test_returns_int(self, sample):
        assert isinstance(fodp_max_word_count_per_slide(sample), int)

    def test_nonnegative(self, sample):
        assert fodp_max_word_count_per_slide(sample) >= 0

    def test_max_gte_zero_for_two_slides(self, two_slide_sample):
        assert fodp_max_word_count_per_slide(two_slide_sample) >= 0


class TestFodpAvgSlideShapeCount:
    def test_returns_float(self, sample):
        assert isinstance(fodp_avg_slide_shape_count(sample), float)

    def test_nonnegative(self, sample):
        assert fodp_avg_slide_shape_count(sample) >= 0.0
