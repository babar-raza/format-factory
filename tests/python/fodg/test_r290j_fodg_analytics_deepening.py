"""Sprint R290J: FODG analytics deepening — word_count, shape_text_ratio, unique_word_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    fodg_word_count,
    fodg_shape_text_ratio,
    fodg_unique_word_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


@pytest.fixture
def sample():
    if not MINIMAL.exists():
        pytest.skip("FODG minimal sample not available")
    return MINIMAL


@pytest.fixture
def shapes_sample():
    if not SHAPES.exists():
        pytest.skip("FODG shapes-basic sample not available")
    return SHAPES


class TestFodgWordCount:
    def test_returns_int(self, sample):
        assert isinstance(fodg_word_count(sample), int)

    def test_nonnegative(self, sample):
        assert fodg_word_count(sample) >= 0


class TestFodgShapeTextRatio:
    def test_returns_float(self, sample):
        assert isinstance(fodg_shape_text_ratio(sample), float)

    def test_between_zero_and_one(self, sample):
        r = fodg_shape_text_ratio(sample)
        assert 0.0 <= r <= 1.0


class TestFodgUniqueWordCount:
    def test_returns_int(self, sample):
        assert isinstance(fodg_unique_word_count(sample), int)

    def test_nonnegative(self, sample):
        assert fodg_unique_word_count(sample) >= 0
