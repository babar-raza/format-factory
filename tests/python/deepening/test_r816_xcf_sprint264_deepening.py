"""Sprint 264 XCF deepening tests."""
from pathlib import Path
import sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
from src.python.xcf import (
    xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300,
    xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000,
)
SAMPLES = _REPO / "samples/by-format/xcf/valid"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"; RED = SAMPLES / "1x1-red-rgb.xcf"; GRAY = SAMPLES / "2x2-gray.xcf"

class TestXcfMod277F1:
    def test_blue_returns_int(self): assert isinstance(xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(BLUE), int)
    def test_blue_expected_value(self): assert xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(BLUE) == 7284
    def test_red_expected_value(self): assert xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(RED) == 7256
    def test_gray_expected_value(self): assert xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(GRAY) == 17184
    def test_returns_nonnegative(self): assert xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(BLUE) >= 0
    def test_accepts_path_object(self): assert isinstance(xcf_file_size_mod_277_times_28_plus_image_type_times_3000_plus_width_times_height_times_2300(Path(BLUE)), int)

class TestXcfMod281F2:
    def test_blue_returns_int(self): assert isinstance(xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(BLUE), int)
    def test_blue_expected_value(self): assert xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(BLUE) == 8340
    def test_red_expected_value(self): assert xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(RED) == 8310
    def test_gray_expected_value(self): assert xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(GRAY) == 9340
    def test_returns_nonnegative(self): assert xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(BLUE) >= 0
    def test_accepts_path_object(self): assert isinstance(xcf_file_size_mod_281_times_30_plus_image_type_times_1000_plus_layer_count_times_3000(Path(BLUE)), int)
