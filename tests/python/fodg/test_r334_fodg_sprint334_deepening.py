"""Sprint 334 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400,
    fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200,
)


# --- F1: fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400 ---

class TestFodgFileSizeMod317Times1900PlusShape2900PlusText2400:
    def test_empty_returns_193800(self):
        assert fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY) == 193800

    def test_minimal_returns_394800(self):
        assert fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL) == 394800

    def test_shapes_returns_95200(self):
        assert fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(SHAPES) == 95200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL) >
                fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_317_times_1900_plus_shape_count_times_2900_plus_text_count_times_2400(str(EMPTY)) == 193800


# --- F2: fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200 ---

class TestFodgFileSizeMod331Times1950PlusShape2700PlusText2200:
    def test_empty_returns_117000(self):
        assert fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY) == 117000

    def test_minimal_returns_295450(self):
        assert fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL) == 295450

    def test_shapes_returns_605300(self):
        assert fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(SHAPES) == 605300

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(SHAPES) >
                fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_331_times_1950_plus_shape_count_times_2700_plus_text_count_times_2200(str(EMPTY)) == 117000
