"""Sprint 262 FODG deepening tests."""
from pathlib import Path
import sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
from src.python.fodg import (
    fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900,
    fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21,
)
EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"

class TestFodgMod241F1:
    def test_empty_returns_int(self): assert isinstance(fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(EMPTY), int)
    def test_empty_expected_value(self): assert fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(EMPTY) == 1335
    def test_minimal_expected_value(self): assert fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(MINIMAL) == 6505
    def test_shapes_expected_value(self): assert fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(SHAPES) == 15230
    def test_returns_nonnegative(self): assert fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(EMPTY) >= 0
    def test_accepts_path_object(self): assert isinstance(fodg_file_size_mod_241_times_15_plus_shape_count_times_3200_plus_text_count_times_2900(Path(EMPTY)), int)

class TestFodgTimes25F2:
    def test_empty_returns_int(self): assert isinstance(fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(EMPTY), int)
    def test_empty_expected_value(self): assert fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(EMPTY) == 26346
    def test_minimal_expected_value(self): assert fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(MINIMAL) == 36951
    def test_shapes_expected_value(self): assert fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(SHAPES) == 40946
    def test_returns_nonnegative(self): assert fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(EMPTY) >= 0
    def test_accepts_path_object(self): assert isinstance(fodg_file_size_times_25_plus_shape_count_times_60_plus_text_count_times_45_plus_page_count_times_21(Path(EMPTY)), int)
