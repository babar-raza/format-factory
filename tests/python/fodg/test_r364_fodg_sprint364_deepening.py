"""Sprint 364 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400,
    fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200,
)


# --- F1: fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400 ---

class TestFodgFileSizeMod443Times2900PlusShape3900PlusText3400:
    def test_empty_returns_484300(self):
        assert fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY) == 484300

    def test_minimal_returns_424900(self):
        assert fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(MINIMAL) == 424900

    def test_shapes_returns_885600(self):
        assert fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(SHAPES) == 885600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(SHAPES) >
                fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_443_times_2900_plus_shape_count_times_3900_plus_text_count_times_3400(str(EMPTY)) == 484300


# --- F2: fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200 ---

class TestFodgFileSizeMod449Times2950PlusShape3700PlusText3200:
    def test_empty_returns_457250(self):
        assert fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY) == 457250

    def test_minimal_returns_378600(self):
        assert fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(MINIMAL) == 378600

    def test_shapes_returns_846450(self):
        assert fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(SHAPES) == 846450

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(SHAPES) >
                fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_449_times_2950_plus_shape_count_times_3700_plus_text_count_times_3200(str(EMPTY)) == 457250
