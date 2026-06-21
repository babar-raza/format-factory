"""Sprint 259 FODG analytics deepening tests.

Samples: empty-page.fodg (fs=1053, sc=0, tc=0)
         minimal-drawing.fodg (fs=1473, sc=1, tc=1)
         shapes-basic.fodg (fs=1628, sc=3, tc=2)

F1: fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350
    EMPTY=3000, MINIMAL=2700, SHAPES=4550
F2: fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550
    EMPTY=3600, MINIMAL=1200, SHAPES=6050
"""
from pathlib import Path

from src.python.fodg import (
    fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350,
    fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550,
)

_REPO = Path(__file__).parent.parent.parent.parent
_FODG = _REPO / "samples" / "by-format" / "fodg"

EMPTY = str(_FODG / "empty-page.fodg")
MINIMAL = str(_FODG / "minimal-drawing.fodg")
SHAPES = str(_FODG / "shapes-basic.fodg")


# --- F1 tests ---

class TestF1Empty:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY), int)

    def test_value(self):
        assert fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY) == 3000

    def test_nonnegative(self):
        assert fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY) >= 0


class TestF1Minimal:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(MINIMAL), int)

    def test_value(self):
        assert fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(MINIMAL) == 2700

    def test_nonnegative(self):
        assert fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(MINIMAL) >= 0


class TestF1Shapes:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES), int)

    def test_value(self):
        assert fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES) == 4550

    def test_nonnegative(self):
        assert fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES) >
                fodg_file_size_mod_31_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY))


# --- F2 tests ---

class TestF2Empty:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(EMPTY), int)

    def test_value(self):
        assert fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(EMPTY) == 3600

    def test_nonnegative(self):
        assert fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(EMPTY) >= 0


class TestF2Minimal:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(MINIMAL), int)

    def test_value(self):
        assert fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(MINIMAL) == 1200

    def test_nonnegative(self):
        assert fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(MINIMAL) >= 0


class TestF2Shapes:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(SHAPES), int)

    def test_value(self):
        assert fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(SHAPES) == 6050

    def test_nonnegative(self):
        assert fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(SHAPES) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(SHAPES) >
                fodg_file_size_mod_23_times_200_plus_shape_count_times_450_plus_text_count_times_550(EMPTY))
