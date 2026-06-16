"""Tests for XCF gap closure (Sprint 40).

Closes:
  GAP-XCF-FOSS-XCF_IS_MULTI-001   (Xcf Is Multi Pixel)
  GAP-XCF-FOSS-XCF_FILE_BYT-001   (Xcf File Bytes Per Layer)
  GAP-XCF-FOSS-XCF_COLOR_MO-001   (Xcf Color Mode Name)
  GAP-XCF-FOSS-XCF_LAYER_SI-001   (Xcf Layer Size Variance)
  GAP-XCF-FOSS-XCF_TOTAL_PI-001   (Xcf Total Pixels)
  GAP-XCF-FOSS-XCF_FILE_HEA-001   (Xcf File Header Overhead)
  GAP-XCF-FOSS-XCF_VERSION_-001   (Xcf Version Number)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_color_mode_name,
    xcf_file_bytes_per_layer,
    xcf_file_header_overhead,
    xcf_is_multi_pixel,
    xcf_layer_size_variance,
    xcf_total_pixels,
    xcf_version_number,
)

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RED = str(_DIR / "1x1-red-rgb.xcf")
_1X1_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_2X2_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfIsMultiPixel:
    def test_return_type(self):
        assert isinstance(xcf_is_multi_pixel(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        # 1 pixel -> not multi pixel
        assert xcf_is_multi_pixel(_1X1_RED) is False

    def test_false_for_1x1_blue(self):
        assert xcf_is_multi_pixel(_1X1_BLUE) is False

    def test_true_for_2x2_gray(self):
        # 4 pixels -> multi pixel
        assert xcf_is_multi_pixel(_2X2_GRAY) is True

    def test_consistent_across_calls(self):
        assert xcf_is_multi_pixel(_1X1_RED) == xcf_is_multi_pixel(_1X1_RED)


class TestXcfFileBytesPerLayer:
    def test_return_type(self):
        assert isinstance(xcf_file_bytes_per_layer(_1X1_RED), float)

    def test_exact_177_for_1x1_red(self):
        assert xcf_file_bytes_per_layer(_1X1_RED) == 177.0

    def test_exact_178_for_1x1_blue(self):
        assert xcf_file_bytes_per_layer(_1X1_BLUE) == 178.0

    def test_exact_178_for_2x2_gray(self):
        assert xcf_file_bytes_per_layer(_2X2_GRAY) == 178.0

    def test_positive(self):
        assert xcf_file_bytes_per_layer(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_file_bytes_per_layer(_1X1_RED) == xcf_file_bytes_per_layer(_1X1_RED)


class TestXcfColorModeName:
    def test_return_type(self):
        assert isinstance(xcf_color_mode_name(_1X1_RED), str)

    def test_rgb_for_1x1_red(self):
        assert xcf_color_mode_name(_1X1_RED) == "RGB"

    def test_rgb_for_1x1_blue(self):
        assert xcf_color_mode_name(_1X1_BLUE) == "RGB"

    def test_grayscale_for_2x2_gray(self):
        assert xcf_color_mode_name(_2X2_GRAY) == "Grayscale"

    def test_consistent_across_calls(self):
        assert xcf_color_mode_name(_1X1_RED) == xcf_color_mode_name(_1X1_RED)


class TestXcfLayerSizeVariance:
    def test_return_type(self):
        assert isinstance(xcf_layer_size_variance(_1X1_RED), float)

    def test_zero_for_single_layer_images(self):
        # single layer -> variance = 0
        assert xcf_layer_size_variance(_1X1_RED) == 0.0

    def test_zero_for_1x1_blue(self):
        assert xcf_layer_size_variance(_1X1_BLUE) == 0.0

    def test_zero_for_2x2_gray(self):
        assert xcf_layer_size_variance(_2X2_GRAY) == 0.0

    def test_nonnegative(self):
        assert xcf_layer_size_variance(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert xcf_layer_size_variance(_1X1_RED) == xcf_layer_size_variance(_1X1_RED)


class TestXcfTotalPixels:
    def test_return_type(self):
        assert isinstance(xcf_total_pixels(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_total_pixels(_1X1_RED) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_total_pixels(_1X1_BLUE) == 1

    def test_exact_4_for_2x2_gray(self):
        assert xcf_total_pixels(_2X2_GRAY) == 4

    def test_positive(self):
        assert xcf_total_pixels(_1X1_RED) >= 1

    def test_consistent_across_calls(self):
        assert xcf_total_pixels(_1X1_RED) == xcf_total_pixels(_1X1_RED)


class TestXcfFileHeaderOverhead:
    def test_return_type(self):
        assert isinstance(xcf_file_header_overhead(_1X1_RED), int)

    def test_exact_176_for_1x1_red(self):
        assert xcf_file_header_overhead(_1X1_RED) == 176

    def test_exact_177_for_1x1_blue(self):
        assert xcf_file_header_overhead(_1X1_BLUE) == 177

    def test_exact_174_for_2x2_gray(self):
        assert xcf_file_header_overhead(_2X2_GRAY) == 174

    def test_positive(self):
        assert xcf_file_header_overhead(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_file_header_overhead(_1X1_RED) == xcf_file_header_overhead(_1X1_RED)


class TestXcfVersionNumber:
    def test_return_type(self):
        assert isinstance(xcf_version_number(_1X1_RED), int)

    def test_exact_11_for_1x1_red(self):
        assert xcf_version_number(_1X1_RED) == 11

    def test_exact_11_for_1x1_blue(self):
        assert xcf_version_number(_1X1_BLUE) == 11

    def test_exact_11_for_2x2_gray(self):
        assert xcf_version_number(_2X2_GRAY) == 11

    def test_positive(self):
        assert xcf_version_number(_1X1_RED) >= 1

    def test_consistent_across_calls(self):
        assert xcf_version_number(_1X1_RED) == xcf_version_number(_1X1_RED)
