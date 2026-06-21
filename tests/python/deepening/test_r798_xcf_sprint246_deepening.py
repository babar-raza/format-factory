"""
tests/python/deepening/test_r798_xcf_sprint246_deepening.py

Sprint: sal-advancement-iter11-20260617-160500-8656416
Product deepening Sprint 246 — 2 new XCF analytics functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600,
    xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300,
)

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_BLUE = str(_XCF_DIR / "1x1-rgba-blue.xcf")
_RED = str(_XCF_DIR / "1x1-red-rgb.xcf")
_GRAY = str(_XCF_DIR / "2x2-gray.xcf")


class TestXcfMod157F1:
    """xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600"""

    def test_blue_returns_int(self):
        result = xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(_BLUE)
        assert isinstance(result, int)

    def test_blue_expected_value(self):
        # fs=178, it=0, w=1, h=1 → (178%157)*200 + 0*2300 + 1*1*1600 = 4200+0+1600=5800
        result = xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(_BLUE)
        assert result == 5800

    def test_red_expected_value(self):
        # fs=177, it=0, w=1, h=1 → (177%157)*200 + 0*2300 + 1*1*1600 = 4000+0+1600=5600
        result = xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(_RED)
        assert result == 5600

    def test_gray_expected_value(self):
        # fs=178, it=1, w=2, h=2 → (178%157)*200 + 1*2300 + 2*2*1600 = 4200+2300+6400=12900
        result = xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(_GRAY)
        assert result == 12900

    def test_returns_nonnegative(self):
        for path in [_BLUE, _RED, _GRAY]:
            result = xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_157_times_200_plus_image_type_times_2300_plus_width_times_height_times_1600(Path(_BLUE))
        assert result == 5800


class TestXcfMod163F2:
    """xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300"""

    def test_blue_returns_int(self):
        result = xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(_BLUE)
        assert isinstance(result, int)

    def test_blue_expected_value(self):
        # fs=178, it=0, lc=1 → (178%163)*225 + 0*650 + 1*2300 = 3375+0+2300=5675
        result = xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(_BLUE)
        assert result == 5675

    def test_red_expected_value(self):
        # fs=177, it=0, lc=1 → (177%163)*225 + 0*650 + 1*2300 = 3150+0+2300=5450
        result = xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(_RED)
        assert result == 5450

    def test_gray_expected_value(self):
        # fs=178, it=1, lc=1 → (178%163)*225 + 1*650 + 1*2300 = 3375+650+2300=6325
        result = xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(_GRAY)
        assert result == 6325

    def test_returns_nonnegative(self):
        for path in [_BLUE, _RED, _GRAY]:
            result = xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_163_times_225_plus_image_type_times_650_plus_layer_count_times_2300(Path(_BLUE))
        assert result == 5675
