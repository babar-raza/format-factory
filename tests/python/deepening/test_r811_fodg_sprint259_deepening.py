"""Sprint 259 FODG deepening tests."""
from pathlib import Path
import sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
from src.python.fodg import (
    fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800,
    fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19,
)
EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"

class TestFodgMod233F1:
    def test_empty_returns_int(self): assert isinstance(fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(EMPTY), int)
    def test_empty_expected_value(self): assert fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(EMPTY) == 1573
    def test_minimal_expected_value(self): assert fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(MINIMAL) == 6875
    def test_shapes_expected_value(self): assert fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(SHAPES) == 15090
    def test_returns_nonnegative(self): assert fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(EMPTY) >= 0
    def test_accepts_path_object(self): assert isinstance(fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800(Path(EMPTY)), int)

class TestFodgTimes23F2:
    def test_empty_returns_int(self): assert isinstance(fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(EMPTY), int)
    def test_empty_expected_value(self): assert fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(EMPTY) == 24238
    def test_minimal_expected_value(self): assert fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(MINIMAL) == 33993
    def test_shapes_expected_value(self): assert fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(SHAPES) == 37668
    def test_returns_nonnegative(self): assert fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(EMPTY) >= 0
    def test_accepts_path_object(self): assert isinstance(fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19(Path(EMPTY)), int)
