"""
tests/python/deepening/test_r801_xcf_sprint249_deepening.py

Sprint: sal-advancement-iter14-20260617-175000-8656416
Product deepening Sprint 249 — 2 new XCF analytics functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700,
    xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400,
)

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_BLUE = str(_XCF_DIR / "1x1-rgba-blue.xcf")
_RED = str(_XCF_DIR / "1x1-red-rgb.xcf")
_GRAY = str(_XCF_DIR / "2x2-gray.xcf")


class TestXcfMod167F1:
    """xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700"""

    def test_blue_returns_int(self):
        result = xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(_BLUE)
        assert isinstance(result, int)

    def test_blue_expected_value(self):
        # fs=178, it=0, w=1, h=1 → (178%167)*5 + 0*2400 + 1*1*1700 = 11*5+0+1700=1755
        result = xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(_BLUE)
        assert result == 1755

    def test_red_expected_value(self):
        # fs=177, it=0, w=1, h=1 → (177%167)*5 + 0 + 1700 = 10*5+1700=1750
        result = xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(_RED)
        assert result == 1750

    def test_gray_expected_value(self):
        # fs=178, it=1, w=2, h=2 → (178%167)*5 + 1*2400 + 4*1700 = 55+2400+6800=9255
        result = xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(_GRAY)
        assert result == 9255

    def test_returns_nonnegative(self):
        for path in [_BLUE, _RED, _GRAY]:
            result = xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_167_times_5_plus_image_type_times_2400_plus_width_times_height_times_1700(Path(_BLUE))
        assert result == 1755


class TestXcfMod173F2:
    """xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400"""

    def test_blue_returns_int(self):
        result = xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(_BLUE)
        assert isinstance(result, int)

    def test_blue_expected_value(self):
        # fs=178, it=0, lc=1 → (178%173)*10 + 0*700 + 1*2400 = 5*10+0+2400=2450
        result = xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(_BLUE)
        assert result == 2450

    def test_red_expected_value(self):
        # fs=177, it=0, lc=1 → (177%173)*10 + 0 + 2400 = 4*10+2400=2440
        result = xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(_RED)
        assert result == 2440

    def test_gray_expected_value(self):
        # fs=178, it=1, lc=1 → (178%173)*10 + 1*700 + 1*2400 = 50+700+2400=3150
        result = xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(_GRAY)
        assert result == 3150

    def test_returns_nonnegative(self):
        for path in [_BLUE, _RED, _GRAY]:
            result = xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_173_times_10_plus_image_type_times_700_plus_layer_count_times_2400(Path(_BLUE))
        assert result == 2450
