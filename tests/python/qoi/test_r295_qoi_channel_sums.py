"""Tests for qoi_red_channel_sum and qoi_blue_channel_sum (Sprint r295)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_red_channel_sum, qoi_blue_channel_sum

_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiRedChannelSum:
    """Tests for qoi_red_channel_sum."""

    def test_1x1_red_has_255(self):
        """1x1-red.qoi is fully red, so red channel sum is 255."""
        result = qoi_red_channel_sum(_QOI / "1x1-red.qoi")
        assert result == 255

    def test_2x2_black_has_zero_red(self):
        """2x2-black.qoi is fully black, so red channel sum is 0."""
        result = qoi_red_channel_sum(_QOI / "2x2-black.qoi")
        assert result == 0

    def test_4x1_gradient_has_510_red(self):
        """4x1-gradient.qoi has 4 pixels with red sum 510."""
        result = qoi_red_channel_sum(_QOI / "4x1-gradient.qoi")
        assert result == 510

    def test_returns_int(self):
        result = qoi_red_channel_sum(_QOI / "1x1-red.qoi")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"]:
            result = qoi_red_channel_sum(_QOI / f)
            assert result >= 0

    def test_red_image_has_more_red_than_black(self):
        r1 = qoi_red_channel_sum(_QOI / "2x2-black.qoi")
        r2 = qoi_red_channel_sum(_QOI / "1x1-red.qoi")
        assert r2 > r1


class TestQoiBlueChannelSum:
    """Tests for qoi_blue_channel_sum."""

    def test_1x1_red_has_zero_blue(self):
        """1x1-red.qoi is fully red, so blue channel sum is 0."""
        result = qoi_blue_channel_sum(_QOI / "1x1-red.qoi")
        assert result == 0

    def test_2x2_black_has_zero_blue(self):
        """2x2-black.qoi is fully black, so blue channel sum is 0."""
        result = qoi_blue_channel_sum(_QOI / "2x2-black.qoi")
        assert result == 0

    def test_4x1_gradient_has_510_blue(self):
        """4x1-gradient.qoi has 4 pixels with blue sum 510."""
        result = qoi_blue_channel_sum(_QOI / "4x1-gradient.qoi")
        assert result == 510

    def test_returns_int(self):
        result = qoi_blue_channel_sum(_QOI / "4x1-gradient.qoi")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"]:
            result = qoi_blue_channel_sum(_QOI / f)
            assert result >= 0

    def test_gradient_has_most_blue(self):
        r1 = qoi_blue_channel_sum(_QOI / "1x1-red.qoi")
        r2 = qoi_blue_channel_sum(_QOI / "4x1-gradient.qoi")
        assert r2 > r1
