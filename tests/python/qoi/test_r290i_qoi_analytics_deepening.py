"""Sprint R290I: QOI analytics deepening — black_pixel_count, white_pixel_count, avg_saturation."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    qoi_black_pixel_count,
    qoi_white_pixel_count,
    qoi_avg_saturation,
)

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"
RED_1x1 = SAMPLES / "1x1-red.qoi"
BLACK_2x2 = SAMPLES / "2x2-black.qoi"


@pytest.fixture
def red_sample():
    if not RED_1x1.exists():
        pytest.skip("QOI 1x1-red sample not available")
    return RED_1x1


@pytest.fixture
def black_sample():
    if not BLACK_2x2.exists():
        pytest.skip("QOI 2x2-black sample not available")
    return BLACK_2x2


class TestQoiBlackPixelCount:
    def test_returns_int(self, red_sample):
        assert isinstance(qoi_black_pixel_count(red_sample), int)

    def test_nonnegative(self, red_sample):
        assert qoi_black_pixel_count(red_sample) >= 0

    def test_black_sample_has_black(self, black_sample):
        assert qoi_black_pixel_count(black_sample) > 0


class TestQoiWhitePixelCount:
    def test_returns_int(self, red_sample):
        assert isinstance(qoi_white_pixel_count(red_sample), int)

    def test_nonnegative(self, red_sample):
        assert qoi_white_pixel_count(red_sample) >= 0


class TestQoiAvgSaturation:
    def test_returns_float(self, red_sample):
        assert isinstance(qoi_avg_saturation(red_sample), float)

    def test_between_zero_and_one(self, red_sample):
        s = qoi_avg_saturation(red_sample)
        assert 0.0 <= s <= 1.0
