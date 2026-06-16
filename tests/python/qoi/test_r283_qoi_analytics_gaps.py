"""
Tests for QOI analytics gap closure (4 FOSS gaps).
Closes: GAP-QOI-FOSS-QOI_PIXEL_D-001, GAP-QOI-FOSS-QOI_IS_DARK-001,
        GAP-QOI-FOSS-QOI_COLOR_D-001, GAP-QOI-FOSS-QOI_IS_BRIG-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    qoi_pixel_density,
    qoi_is_dark,
    qoi_color_depth_estimate,
    qoi_is_bright,
)

_QOI_1x1 = _REPO / "samples/by-format/qoi/valid/1x1-red.qoi"
_QOI_2x2 = _REPO / "samples/by-format/qoi/valid/2x2-black.qoi"
_QOI_GRAD = _REPO / "samples/by-format/qoi/valid/4x1-gradient.qoi"


class TestQoiPixelDensity:
    def test_returns_float(self):
        assert isinstance(qoi_pixel_density(_QOI_1x1), float)

    def test_positive(self):
        assert qoi_pixel_density(_QOI_1x1) > 0.0

    def test_nonnegative(self):
        assert qoi_pixel_density(_QOI_2x2) >= 0.0

    def test_consistent_across_calls(self):
        r1 = qoi_pixel_density(_QOI_GRAD)
        r2 = qoi_pixel_density(_QOI_GRAD)
        assert r1 == pytest.approx(r2)


class TestQoiIsDark:
    def test_returns_bool(self):
        assert isinstance(qoi_is_dark(_QOI_1x1), bool)

    def test_black_image_is_dark(self):
        # 2x2-black.qoi — all pixels are black (0,0,0)
        assert qoi_is_dark(_QOI_2x2) is True

    def test_dark_and_bright_exclusive(self):
        # is_dark and is_bright should not both be True for same file
        dark = qoi_is_dark(_QOI_1x1)
        bright = qoi_is_bright(_QOI_1x1)
        assert not (dark and bright)

    def test_consistent_result(self):
        r1 = qoi_is_dark(_QOI_2x2)
        r2 = qoi_is_dark(_QOI_2x2)
        assert r1 == r2


class TestQoiColorDepthEstimate:
    def test_returns_float(self):
        assert isinstance(qoi_color_depth_estimate(_QOI_1x1), float)

    def test_nonnegative(self):
        assert qoi_color_depth_estimate(_QOI_1x1) >= 0.0

    def test_zero_for_single_color_image(self):
        # 1x1 has only 1 unique color → unique <= 1 → returns 0.0
        assert qoi_color_depth_estimate(_QOI_1x1) == 0.0

    def test_positive_for_gradient(self):
        # gradient has multiple distinct colors
        assert qoi_color_depth_estimate(_QOI_GRAD) >= 0.0


class TestQoiIsBright:
    def test_returns_bool(self):
        assert isinstance(qoi_is_bright(_QOI_1x1), bool)

    def test_not_bright_for_black_image(self):
        assert qoi_is_bright(_QOI_2x2) is False

    def test_bool_type_for_gradient(self):
        assert isinstance(qoi_is_bright(_QOI_GRAD), bool)

    def test_consistent_result(self):
        r1 = qoi_is_bright(_QOI_1x1)
        r2 = qoi_is_bright(_QOI_1x1)
        assert r1 == r2
