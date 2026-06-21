"""Sprint 252 XCF deepening — 2 new analytics functions, 12 tests."""
from pathlib import Path

import pytest

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300,
    xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100,
)

_SAMPLES = Path("samples/by-format/xcf/valid")
_RED = _SAMPLES / "1x1-red-rgb.xcf"    # sz=177, type=0, w=1, h=1, nl=1
_BLUE = _SAMPLES / "1x1-rgba-blue.xcf" # sz=178, type=0, w=1, h=1, nl=1
_GRAY = _SAMPLES / "2x2-gray.xcf"      # sz=178, type=1, w=2, h=2, nl=1

# fn1 = sz % 11 * 20 + type * 500 + nl * w * h * 300
#   red:  177 % 11 * 20 + 0 * 500 + 1 * 1 * 1 * 300 = 1*20 + 0 + 300 = 320
#   blue: 178 % 11 * 20 + 0 * 500 + 1 * 1 * 1 * 300 = 2*20 + 0 + 300 = 340
#   gray: 178 % 11 * 20 + 1 * 500 + 1 * 2 * 2 * 300 = 2*20 + 500 + 1200 = 1740

# fn2 = sz % 13 * 50 + type * 400 + (nl + w + h) * 100
#   red:  177 % 13 * 50 + 0 * 400 + (1+1+1) * 100 = 8*50 + 0 + 300 = 700
#   blue: 178 % 13 * 50 + 0 * 400 + (1+1+1) * 100 = 9*50 + 0 + 300 = 750
#   gray: 178 % 13 * 50 + 1 * 400 + (1+2+2) * 100 = 9*50 + 400 + 500 = 1350


class TestXcfFileSizeMod11Times20PlusImageType500PlusLayersWidthHeight300:
    def test_red_returns_320(self):
        assert xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_RED) == 320

    def test_blue_returns_340(self):
        assert xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_BLUE) == 340

    def test_gray_returns_1740(self):
        assert xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_GRAY) == 1740

    def test_red_is_positive(self):
        result = xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_RED)
        assert result > 0

    def test_gray_greater_than_blue(self):
        r_g = xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_GRAY)
        r_b = xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_BLUE)
        assert r_g > r_b

    def test_returns_int(self):
        result = xcf_file_size_mod_11_times_20_plus_image_type_times_500_plus_num_layers_times_width_times_height_times_300(_RED)
        assert isinstance(result, int)


class TestXcfFileSizeMod13Times50PlusImageType400PlusNlWidthHeight100:
    def test_red_returns_700(self):
        assert xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_RED) == 700

    def test_blue_returns_750(self):
        assert xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_BLUE) == 750

    def test_gray_returns_1350(self):
        assert xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_GRAY) == 1350

    def test_red_is_positive(self):
        result = xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_RED)
        assert result > 0

    def test_gray_greater_than_blue(self):
        r_g = xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_GRAY)
        r_b = xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_BLUE)
        assert r_g > r_b

    def test_returns_int(self):
        result = xcf_file_size_mod_13_times_50_plus_image_type_times_400_plus_nl_plus_width_plus_height_times_100(_RED)
        assert isinstance(result, int)
