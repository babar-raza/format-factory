"""Sprint 256 FODG analytics deepening tests.

Samples: empty-page.fodg (fs=1053, sc=0, tc=0)
         minimal-drawing.fodg (fs=1473, sc=1, tc=1)
         shapes-basic.fodg (fs=1628, sc=3, tc=2)

F1: fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300
    EMPTY=1200, MINIMAL=2400, SHAPES=4350
F2: fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450
    EMPTY=900, MINIMAL=3350, SHAPES=3100
"""
from pathlib import Path

from src.python.fodg import (
    fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300,
    fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450,
)

_REPO = Path(__file__).parent.parent.parent.parent
_FODG = _REPO / "samples" / "by-format" / "fodg"

EMPTY = str(_FODG / "empty-page.fodg")
MINIMAL = str(_FODG / "minimal-drawing.fodg")
SHAPES = str(_FODG / "shapes-basic.fodg")


# --- F1 tests ---

class TestF1Empty:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(EMPTY), int)

    def test_value(self):
        assert fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(EMPTY) == 1200

    def test_nonnegative(self):
        assert fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(EMPTY) >= 0


class TestF1Minimal:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(MINIMAL), int)

    def test_value(self):
        assert fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(MINIMAL) == 2400

    def test_nonnegative(self):
        assert fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(MINIMAL) >= 0


class TestF1Shapes:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(SHAPES), int)

    def test_value(self):
        assert fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(SHAPES) == 4350

    def test_nonnegative(self):
        assert fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(SHAPES) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(SHAPES) >
                fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300(MINIMAL))


# --- F2 tests ---

class TestF2Empty:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(EMPTY), int)

    def test_value(self):
        assert fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(EMPTY) == 900

    def test_nonnegative(self):
        assert fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(EMPTY) >= 0


class TestF2Minimal:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(MINIMAL), int)

    def test_value(self):
        assert fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(MINIMAL) == 3350

    def test_nonnegative(self):
        assert fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(MINIMAL) >= 0

    def test_minimal_greater_than_empty(self):
        assert (fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(MINIMAL) >
                fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(EMPTY))


class TestF2Shapes:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(SHAPES), int)

    def test_value(self):
        assert fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(SHAPES) == 3100

    def test_nonnegative(self):
        assert fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450(SHAPES) >= 0
