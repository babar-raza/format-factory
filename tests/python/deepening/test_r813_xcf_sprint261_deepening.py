"""Sprint 261 XCF deepening tests."""
from pathlib import Path
import sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
from src.python.xcf import (
    xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200,
    xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900,
)
SAMPLES = _REPO / "samples/by-format/xcf/valid"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"; RED = SAMPLES / "1x1-red-rgb.xcf"; GRAY = SAMPLES / "2x2-gray.xcf"

class TestXcfMod269F1:
    def test_blue_returns_int(self): assert isinstance(xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(BLUE), int)
    def test_blue_expected_value(self): assert xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(BLUE) == 6472
    def test_red_expected_value(self): assert xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(RED) == 6448
    def test_gray_expected_value(self): assert xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(GRAY) == 15972
    def test_returns_nonnegative(self): assert xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(BLUE) >= 0
    def test_accepts_path_object(self): assert isinstance(xcf_file_size_mod_269_times_24_plus_image_type_times_2900_plus_width_times_height_times_2200(Path(BLUE)), int)

class TestXcfMod271F2:
    def test_blue_returns_int(self): assert isinstance(xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(BLUE), int)
    def test_blue_expected_value(self): assert xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(BLUE) == 7528
    def test_red_expected_value(self): assert xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(RED) == 7502
    def test_gray_expected_value(self): assert xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(GRAY) == 8478
    def test_returns_nonnegative(self): assert xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(BLUE) >= 0
    def test_accepts_path_object(self): assert isinstance(xcf_file_size_mod_271_times_26_plus_image_type_times_950_plus_layer_count_times_2900(Path(BLUE)), int)
