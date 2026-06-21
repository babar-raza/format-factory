"""
Sprint 253 FODG deepening tests.
Functions: fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600
           fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15
"""
from pathlib import Path
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600,
    fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15,
)

EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"


class TestFodgMod211F1:
    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(EMPTY), int)

    def test_empty_expected_value(self):
        assert fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(EMPTY) == 1881

    def test_minimal_expected_value(self):
        assert fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(MINIMAL) == 7363

    def test_shapes_expected_value(self):
        assert fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(SHAPES) == 12659

    def test_returns_nonnegative(self):
        assert fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(EMPTY) >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_211_times_9_plus_shape_count_times_2900_plus_text_count_times_2600(Path(EMPTY))
        assert isinstance(result, int)


class TestFodgTimes19F2:
    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(EMPTY), int)

    def test_empty_expected_value(self):
        assert fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(EMPTY) == 20022

    def test_minimal_expected_value(self):
        assert fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(MINIMAL) == 28077

    def test_shapes_expected_value(self):
        assert fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(SHAPES) == 31112

    def test_returns_nonnegative(self):
        assert fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(EMPTY) >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_30_plus_page_count_times_15(Path(EMPTY))
        assert isinstance(result, int)
