"""
test_r333_xcf_new_analytics.py
Sprint 69 — 5 new XCF analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_file_size_bytes,
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_aspect_ratio,
    xcf_max_layer_area,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_RGB = str(_SAMPLES / "1x1-red-rgb.xcf")
_BLUE_RGBA = str(_SAMPLES / "1x1-rgba-blue.xcf")
_GRAY = str(_SAMPLES / "2x2-gray.xcf")


# --- xcf_file_size_bytes ---

class TestXcfFileSizeBytes:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes(_RED_RGB), int)

    def test_positive(self):
        assert xcf_file_size_bytes(_RED_RGB) > 0

    def test_blue_positive(self):
        assert xcf_file_size_bytes(_BLUE_RGBA) > 0

    def test_gray_positive(self):
        assert xcf_file_size_bytes(_GRAY) > 0

    def test_at_least_header(self):
        # XCF files have at minimum a 25-byte header
        assert xcf_file_size_bytes(_RED_RGB) >= 25


# --- xcf_is_rgb ---

class TestXcfIsRgb:
    def test_returns_bool(self):
        assert isinstance(xcf_is_rgb(_RED_RGB), bool)

    def test_red_is_rgb(self):
        assert xcf_is_rgb(_RED_RGB) is True

    def test_blue_is_rgb(self):
        # RGBA is still RGB type in XCF
        assert xcf_is_rgb(_BLUE_RGBA) is True

    def test_gray_not_rgb(self):
        assert xcf_is_rgb(_GRAY) is False

    def test_red_not_grayscale_if_rgb(self):
        assert not (xcf_is_rgb(_RED_RGB) and xcf_is_grayscale(_RED_RGB))


# --- xcf_is_grayscale ---

class TestXcfIsGrayscale:
    def test_returns_bool(self):
        assert isinstance(xcf_is_grayscale(_GRAY), bool)

    def test_gray_is_grayscale(self):
        assert xcf_is_grayscale(_GRAY) is True

    def test_red_not_grayscale(self):
        assert xcf_is_grayscale(_RED_RGB) is False

    def test_blue_not_grayscale(self):
        assert xcf_is_grayscale(_BLUE_RGBA) is False

    def test_mutual_exclusion(self):
        # a file can't be both RGB and grayscale
        assert not (xcf_is_rgb(_GRAY) and xcf_is_grayscale(_GRAY))


# --- xcf_aspect_ratio ---

class TestXcfAspectRatio:
    def test_returns_float(self):
        assert isinstance(xcf_aspect_ratio(_RED_RGB), float)

    def test_red_square(self):
        # 1x1 image
        assert xcf_aspect_ratio(_RED_RGB) == 1.0

    def test_blue_square(self):
        # 1x1 image
        assert xcf_aspect_ratio(_BLUE_RGBA) == 1.0

    def test_gray_square(self):
        # 2x2 image
        assert xcf_aspect_ratio(_GRAY) == 1.0

    def test_non_negative(self):
        assert xcf_aspect_ratio(_RED_RGB) >= 0.0


# --- xcf_max_layer_area ---

class TestXcfMaxLayerArea:
    def test_returns_int(self):
        assert isinstance(xcf_max_layer_area(_RED_RGB), int)

    def test_non_negative(self):
        assert xcf_max_layer_area(_RED_RGB) >= 0

    def test_red_area_one(self):
        # 1x1 canvas
        assert xcf_max_layer_area(_RED_RGB) == 1

    def test_gray_area_four(self):
        # 2x2 canvas
        assert xcf_max_layer_area(_GRAY) == 4

    def test_positive_if_has_layers(self):
        assert xcf_max_layer_area(_RED_RGB) >= 1
