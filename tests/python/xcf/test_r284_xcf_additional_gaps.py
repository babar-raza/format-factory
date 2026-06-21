"""
Tests for additional XCF analytics gap closure (5 FOSS gaps).
Closes: XCF_COLOR_MO, XCF_LAYER_SI, XCF_TOTAL_PI, XCF_FILE_HEA, XCF_VERSION_
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    xcf_color_mode_name,
    xcf_layer_size_variance,
    xcf_total_pixels,
    xcf_file_header_overhead,
    xcf_version_number,
)

_XCF_1x1 = _REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"
_XCF_2x2 = _REPO / "samples/by-format/xcf/valid/2x2-gray.xcf"
_XCF_RGBA = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"


class TestXcfColorModeName:
    def test_returns_str(self):
        assert isinstance(xcf_color_mode_name(_XCF_1x1), str)

    def test_rgb_file_returns_rgb(self):
        assert xcf_color_mode_name(_XCF_1x1) == "RGB"

    def test_gray_file_returns_grayscale(self):
        assert xcf_color_mode_name(_XCF_2x2) == "Grayscale"

    def test_nonempty(self):
        assert len(xcf_color_mode_name(_XCF_RGBA)) > 0


class TestXcfLayerSizeVariance:
    def test_returns_float(self):
        assert isinstance(xcf_layer_size_variance(_XCF_1x1), float)

    def test_nonnegative(self):
        assert xcf_layer_size_variance(_XCF_1x1) >= 0.0

    def test_single_layer_zero_variance(self):
        # 1 layer → variance = 0.0
        assert xcf_layer_size_variance(_XCF_1x1) == pytest.approx(0.0)

    def test_2x2_zero_variance(self):
        assert xcf_layer_size_variance(_XCF_2x2) == pytest.approx(0.0)


class TestXcfTotalPixels:
    def test_returns_int(self):
        assert isinstance(xcf_total_pixels(_XCF_1x1), int)

    def test_1x1_is_one(self):
        assert xcf_total_pixels(_XCF_1x1) == 1

    def test_2x2_is_four(self):
        assert xcf_total_pixels(_XCF_2x2) == 4

    def test_positive(self):
        assert xcf_total_pixels(_XCF_1x1) > 0


class TestXcfFileHeaderOverhead:
    def test_returns_int(self):
        assert isinstance(xcf_file_header_overhead(_XCF_1x1), int)

    def test_positive(self):
        assert xcf_file_header_overhead(_XCF_1x1) > 0

    def test_1x1_value(self):
        assert xcf_file_header_overhead(_XCF_1x1) == 176

    def test_2x2_value(self):
        assert xcf_file_header_overhead(_XCF_2x2) == 174


class TestXcfVersionNumber:
    def test_returns_int(self):
        assert isinstance(xcf_version_number(_XCF_1x1), int)

    def test_positive(self):
        assert xcf_version_number(_XCF_1x1) > 0

    def test_1x1_version(self):
        assert xcf_version_number(_XCF_1x1) == 11

    def test_2x2_version(self):
        assert xcf_version_number(_XCF_2x2) == 11
