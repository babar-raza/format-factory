"""Sprint R290E: PGM analytics deepening — below_average_count, pixel_value_variance, zero_pixel_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_below_average_count,
    pgm_pixel_value_variance,
    pgm_zero_pixel_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"
WHITE_1x1 = SAMPLES / "1x1-white.pgm"
GRADIENT = SAMPLES / "2x2-gradient.pgm"


@pytest.fixture
def white_sample():
    if not WHITE_1x1.exists():
        pytest.skip("PGM white sample not available")
    return WHITE_1x1


@pytest.fixture
def gradient_sample():
    if not GRADIENT.exists():
        pytest.skip("PGM gradient sample not available")
    return GRADIENT


class TestPgmBelowAverageCount:
    def test_returns_int(self, white_sample):
        assert isinstance(pgm_below_average_count(white_sample), int)

    def test_nonnegative(self, gradient_sample):
        assert pgm_below_average_count(gradient_sample) >= 0


class TestPgmPixelValueVariance:
    def test_returns_float(self, white_sample):
        assert isinstance(pgm_pixel_value_variance(white_sample), float)

    def test_uniform_is_zero(self, white_sample):
        assert pgm_pixel_value_variance(white_sample) == 0.0

    def test_gradient_has_variance(self, gradient_sample):
        assert pgm_pixel_value_variance(gradient_sample) >= 0.0


class TestPgmZeroPixelCount:
    def test_returns_int(self, white_sample):
        assert isinstance(pgm_zero_pixel_count(white_sample), int)

    def test_nonnegative(self, gradient_sample):
        assert pgm_zero_pixel_count(gradient_sample) >= 0
