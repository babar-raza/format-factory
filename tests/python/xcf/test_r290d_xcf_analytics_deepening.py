"""Sprint R290D: XCF analytics deepening — total_pixel_count, layer_name_list, color_depth."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    xcf_total_pixel_count,
    xcf_layer_name_list,
    xcf_color_depth,
)

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
RGB_1x1 = SAMPLES / "1x1-red-rgb.xcf"
GRAY_2x2 = SAMPLES / "2x2-gray.xcf"


@pytest.fixture
def rgb_sample():
    if not RGB_1x1.exists():
        pytest.skip("XCF RGB sample not available")
    return RGB_1x1


@pytest.fixture
def gray_sample():
    if not GRAY_2x2.exists():
        pytest.skip("XCF gray sample not available")
    return GRAY_2x2


class TestXcfTotalPixelCount:
    def test_returns_int(self, rgb_sample):
        assert isinstance(xcf_total_pixel_count(rgb_sample), int)

    def test_1x1_equals_one(self, rgb_sample):
        assert xcf_total_pixel_count(rgb_sample) == 1

    def test_2x2_equals_four(self, gray_sample):
        assert xcf_total_pixel_count(gray_sample) == 4


class TestXcfLayerNameList:
    def test_returns_list(self, rgb_sample):
        assert isinstance(xcf_layer_name_list(rgb_sample), list)

    def test_nonempty(self, rgb_sample):
        names = xcf_layer_name_list(rgb_sample)
        assert len(names) >= 1


class TestXcfColorDepth:
    def test_rgb_is_24(self, rgb_sample):
        assert xcf_color_depth(rgb_sample) == 24

    def test_gray_is_8(self, gray_sample):
        assert xcf_color_depth(gray_sample) == 8

    def test_returns_int(self, rgb_sample):
        assert isinstance(xcf_color_depth(rgb_sample), int)
