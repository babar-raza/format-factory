"""
Sprint 255 XCF deepening tests.
Functions: xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000
           xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700
"""
from pathlib import Path
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000,
    xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700,
)

SAMPLES = _REPO / "samples/by-format/xcf/valid"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
RED = SAMPLES / "1x1-red-rgb.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


class TestXcfMod241F1:
    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE), int)

    def test_blue_expected_value(self):
        assert xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE) == 4848

    def test_red_expected_value(self):
        assert xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(RED) == 4832

    def test_gray_expected_value(self):
        assert xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(GRAY) == 13548

    def test_returns_nonnegative(self):
        assert xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE) >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_241_times_16_plus_image_type_times_2700_plus_width_times_height_times_2000(Path(BLUE))
        assert isinstance(result, int)


class TestXcfMod251F2:
    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(BLUE), int)

    def test_blue_expected_value(self):
        assert xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(BLUE) == 6260

    def test_red_expected_value(self):
        assert xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(RED) == 6240

    def test_gray_expected_value(self):
        assert xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(GRAY) == 7110

    def test_returns_nonnegative(self):
        assert xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(BLUE) >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_251_times_20_plus_image_type_times_850_plus_layer_count_times_2700(Path(BLUE))
        assert isinstance(result, int)
