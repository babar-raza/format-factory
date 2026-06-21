"""Sprint 265 FODG deepening tests."""
from pathlib import Path
import sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
from src.python.fodg import (
    fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000,
    fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23,
)
EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"

class TestFodgMod251F1:
    def test_empty_returns_int(self): assert isinstance(fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(EMPTY), int)
    def test_empty_expected_value(self): assert fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(EMPTY) == 833
    def test_minimal_expected_value(self): assert fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(MINIMAL) == 10006
    def test_shapes_expected_value(self): assert fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(SHAPES) == 14974
    def test_returns_nonnegative(self): assert fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(EMPTY) >= 0
    def test_accepts_path_object(self): assert isinstance(fodg_file_size_mod_251_times_17_plus_shape_count_times_3300_plus_text_count_times_3000(Path(EMPTY)), int)

class TestFodgTimes27F2:
    def test_empty_returns_int(self): assert isinstance(fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(EMPTY), int)
    def test_empty_expected_value(self): assert fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(EMPTY) == 28454
    def test_minimal_expected_value(self): assert fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(MINIMAL) == 39909
    def test_shapes_expected_value(self): assert fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(SHAPES) == 44224
    def test_returns_nonnegative(self): assert fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(EMPTY) >= 0
    def test_accepts_path_object(self): assert isinstance(fodg_file_size_times_27_plus_shape_count_times_65_plus_text_count_times_50_plus_page_count_times_23(Path(EMPTY)), int)
