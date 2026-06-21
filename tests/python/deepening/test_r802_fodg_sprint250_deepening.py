"""
Sprint 250 FODG deepening tests.
Functions: fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500
           fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13
"""
from pathlib import Path
import pytest
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500,
    fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13,
)

EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"


class TestFodgMod197F1:
    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(EMPTY), int)

    def test_empty_expected_value(self):
        assert fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(EMPTY) == 476

    def test_minimal_expected_value(self):
        assert fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(MINIMAL) == 5958

    def test_shapes_expected_value(self):
        assert fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(SHAPES) == 11264

    def test_returns_nonnegative(self):
        assert fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(EMPTY) >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_197_times_7_plus_shape_count_times_2800_plus_text_count_times_2500(Path(EMPTY))
        assert isinstance(result, int)


class TestFodgTimes17F2:
    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(EMPTY), int)

    def test_empty_expected_value(self):
        assert fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(EMPTY) == 17914

    def test_minimal_expected_value(self):
        assert fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(MINIMAL) == 25119

    def test_shapes_expected_value(self):
        assert fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(SHAPES) == 27834

    def test_returns_nonnegative(self):
        assert fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(EMPTY) >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_13(Path(EMPTY))
        assert isinstance(result, int)
