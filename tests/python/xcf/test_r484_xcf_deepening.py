"""Sprint 255 XCF deepening — 2 new analytics functions, 12 tests."""
from pathlib import Path

import pytest

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150,
    xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200,
)

_SAMPLES = Path("samples/by-format/xcf/valid")
_RED = _SAMPLES / "1x1-red-rgb.xcf"    # sz=177, type=0, w=1, h=1, nl=1
_BLUE = _SAMPLES / "1x1-rgba-blue.xcf" # sz=178, type=0, w=1, h=1, nl=1
_GRAY = _SAMPLES / "2x2-gray.xcf"      # sz=178, type=1, w=2, h=2, nl=1

# fn1 = sz % 17 * 15 + type * 700 + nl * (w + h) * 150
#   red:  177 % 17 * 15 + 0 * 700 + 1 * (1+1) * 150 = 7*15 + 0 + 300 = 105 + 300 = 405
#   blue: 178 % 17 * 15 + 0 * 700 + 1 * (1+1) * 150 = 8*15 + 0 + 300 = 120 + 300 = 420
#   gray: 178 % 17 * 15 + 1 * 700 + 1 * (2+2) * 150 = 8*15 + 700 + 600 = 120 + 1300 = 1420

# fn2 = sz % 19 * 30 + type * 300 + nl * 200
#   red:  177 % 19 * 30 + 0 * 300 + 1 * 200 = 6*30 + 0 + 200 = 180 + 200 = 380
#   blue: 178 % 19 * 30 + 0 * 300 + 1 * 200 = 7*30 + 0 + 200 = 210 + 200 = 410
#   gray: 178 % 19 * 30 + 1 * 300 + 1 * 200 = 7*30 + 300 + 200 = 210 + 500 = 710


class TestXcfFileSizeMod17Times15PlusImageType700PlusNlWidthHeight150:
    def test_red_returns_405(self):
        assert xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_RED) == 405

    def test_blue_returns_420(self):
        assert xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_BLUE) == 420

    def test_gray_returns_1420(self):
        assert xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_GRAY) == 1420

    def test_red_is_positive(self):
        result = xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_RED)
        assert result > 0

    def test_gray_greater_than_blue(self):
        r_g = xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_GRAY)
        r_b = xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_BLUE)
        assert r_g > r_b

    def test_returns_int(self):
        result = xcf_file_size_mod_17_times_15_plus_image_type_times_700_plus_num_layers_times_width_plus_height_times_150(_RED)
        assert isinstance(result, int)


class TestXcfFileSizeMod19Times30PlusImageType300PlusNumLayers200:
    def test_red_returns_380(self):
        assert xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_RED) == 380

    def test_blue_returns_410(self):
        assert xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_BLUE) == 410

    def test_gray_returns_710(self):
        assert xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_GRAY) == 710

    def test_red_is_positive(self):
        result = xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_RED)
        assert result > 0

    def test_gray_greater_than_blue(self):
        r_g = xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_GRAY)
        r_b = xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_BLUE)
        assert r_g > r_b

    def test_returns_int(self):
        result = xcf_file_size_mod_19_times_30_plus_image_type_times_300_plus_num_layers_times_200(_RED)
        assert isinstance(result, int)
