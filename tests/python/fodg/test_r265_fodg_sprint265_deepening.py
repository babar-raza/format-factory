"""Sprint 265 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500,
    fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250,
)


# --- F1: fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500 ---

class TestFodgFileSizeMod43Times100PlusShapeCount900PlusTextCount500:
    def test_empty_returns_2100(self):
        assert fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(EMPTY) == 2100

    def test_minimal_returns_2500(self):
        assert fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL) == 2500

    def test_shapes_returns_7400(self):
        assert fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(SHAPES) == 7400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(SHAPES) >
                fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_43_times_100_plus_shape_count_times_900_plus_text_count_times_500(str(EMPTY)) == 2100


# --- F2: fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250 ---

class TestFodgFileSizeMod29Times150PlusShapeCount600PlusTextCount250:
    def test_empty_returns_1350(self):
        assert fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(EMPTY) == 1350

    def test_minimal_returns_4300(self):
        assert fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(MINIMAL) == 4300

    def test_shapes_returns_2900(self):
        assert fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(SHAPES) == 2900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(SHAPES) >
                fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_29_times_150_plus_shape_count_times_600_plus_text_count_times_250(str(EMPTY)) == 1350
