"""Sprint 258 XCF deepening tests."""
from pathlib import Path
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100,
    xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800,
)

SAMPLES = _REPO / "samples/by-format/xcf/valid"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
RED = SAMPLES / "1x1-red-rgb.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


class TestXcfMod257F1:
    def test_blue_returns_int(self): assert isinstance(xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE), int)
    def test_blue_expected_value(self): assert xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE) == 5304
    def test_red_expected_value(self): assert xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(RED) == 5286
    def test_gray_expected_value(self): assert xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(GRAY) == 14404
    def test_returns_nonnegative(self): assert xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE) >= 0
    def test_accepts_path_object(self): assert isinstance(xcf_file_size_mod_257_times_18_plus_image_type_times_2800_plus_width_times_height_times_2100(Path(BLUE)), int)


class TestXcfMod263F2:
    def test_blue_returns_int(self): assert isinstance(xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(BLUE), int)
    def test_blue_expected_value(self): assert xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(BLUE) == 6716
    def test_red_expected_value(self): assert xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(RED) == 6694
    def test_gray_expected_value(self): assert xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(GRAY) == 7616
    def test_returns_nonnegative(self): assert xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(BLUE) >= 0
    def test_accepts_path_object(self): assert isinstance(xcf_file_size_mod_263_times_22_plus_image_type_times_900_plus_layer_count_times_2800(Path(BLUE)), int)
