"""Sprint 309 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000,
    xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700,
)


# --- F1: xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000 ---

class TestXcfFileSizeMod211Times325PlusImageType2700PlusWidthTimesHeight2000:
    def test_red_returns_59525(self):
        assert xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(RED) == 59525

    def test_blue_returns_59850(self):
        assert xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE) == 59850

    def test_gray_returns_68550(self):
        assert xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(GRAY) == 68550

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(GRAY) >
                xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_211_times_325_plus_image_type_times_2700_plus_width_times_height_times_2000(str(RED)) == 59525


# --- F2: xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700 ---

class TestXcfFileSizeMod223Times275PlusImageType850PlusLayerCount2700:
    def test_red_returns_51375(self):
        assert xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(RED) == 51375

    def test_blue_returns_51650(self):
        assert xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(BLUE) == 51650

    def test_gray_returns_52500(self):
        assert xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(GRAY) == 52500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(GRAY) >
                xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_223_times_275_plus_image_type_times_850_plus_layer_count_times_2700(str(RED)) == 51375
