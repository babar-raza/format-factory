"""Sprint 253 FODG analytics deepening tests.

Functions:
  F1: fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350
      EMPTY=1800, MINIMAL=1150, SHAPES=4600
  F2: fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600
      EMPTY=2000, MINIMAL=3500, SHAPES=2400
"""
from pathlib import Path
import pytest

from src.python.fodg import (
    fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350,
    fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600,
)

_REPO = Path(__file__).parent.parent.parent.parent
_FODG = _REPO / "samples" / "by-format" / "fodg"

EMPTY = str(_FODG / "empty-page.fodg")
MINIMAL = str(_FODG / "minimal-drawing.fodg")
SHAPES = str(_FODG / "shapes-basic.fodg")


# --- F1 basic return values ---

class TestF1Empty:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(EMPTY), int)

    def test_value(self):
        assert fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(EMPTY) == 1800

    def test_nonnegative(self):
        assert fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(EMPTY) >= 0


class TestF1Minimal:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(MINIMAL), int)

    def test_value(self):
        assert fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(MINIMAL) == 1150

    def test_nonnegative(self):
        assert fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(MINIMAL) >= 0


class TestF1Shapes:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(SHAPES), int)

    def test_value(self):
        assert fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(SHAPES) == 4600

    def test_nonnegative(self):
        assert fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(SHAPES) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(SHAPES) >
                fodg_file_size_mod_23_times_100_plus_shape_count_times_700_plus_text_count_times_350(MINIMAL))


# --- F2 basic return values ---

class TestF2Empty:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(EMPTY), int)

    def test_value(self):
        assert fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(EMPTY) == 2000

    def test_nonnegative(self):
        assert fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(EMPTY) >= 0


class TestF2Minimal:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(MINIMAL), int)

    def test_value(self):
        assert fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(MINIMAL) == 3500

    def test_nonnegative(self):
        assert fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(MINIMAL) >= 0


class TestF2Shapes:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(SHAPES), int)

    def test_value(self):
        assert fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(SHAPES) == 2400

    def test_nonnegative(self):
        assert fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(SHAPES) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(MINIMAL) >
                fodg_file_size_mod_11_times_250_plus_shape_count_times_400_plus_text_count_times_600(SHAPES))
