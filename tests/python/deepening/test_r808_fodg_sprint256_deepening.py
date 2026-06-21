"""
Sprint 256 FODG deepening tests.
Functions: fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700
           fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17
"""
from pathlib import Path
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700,
    fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17,
)

EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"


class TestFodgMod227F1:
    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(EMPTY), int)

    def test_empty_expected_value(self):
        assert fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(EMPTY) == 1595

    def test_minimal_expected_value(self):
        assert fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(MINIMAL) == 6921

    def test_shapes_expected_value(self):
        assert fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(SHAPES) == 12129

    def test_returns_nonnegative(self):
        assert fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(EMPTY) >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700(Path(EMPTY))
        assert isinstance(result, int)


class TestFodgTimes21F2:
    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(EMPTY), int)

    def test_empty_expected_value(self):
        assert fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(EMPTY) == 22130

    def test_minimal_expected_value(self):
        assert fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(MINIMAL) == 31035

    def test_shapes_expected_value(self):
        assert fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(SHAPES) == 34390

    def test_returns_nonnegative(self):
        assert fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(EMPTY) >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17(Path(EMPTY))
        assert isinstance(result, int)
