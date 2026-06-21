"""Tests for FODG product deepening sprint 162.

New functions:
  fodg_file_size_minus_shape_count_hundreds — file size - (shape count * 100)
  fodg_shapes_plus_texts_squared            — (shapes + texts)^2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_minus_shape_count_hundreds,
    fodg_shapes_plus_texts_squared,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeMinusShapeCountHundreds:
    def test_return_type(self):
        assert isinstance(fodg_file_size_minus_shape_count_hundreds(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: size=1053, shapes=0 → 1053-0=1053
        assert fodg_file_size_minus_shape_count_hundreds(_EMPTY) == 1053

    def test_exact_1373_for_minimal(self):
        # minimal-drawing: size=1473, shapes=1 → 1473-100=1373
        assert fodg_file_size_minus_shape_count_hundreds(_MIN) == 1373

    def test_exact_1328_for_shapes_basic(self):
        # shapes-basic: size=1628, shapes=3 → 1628-300=1328
        assert fodg_file_size_minus_shape_count_hundreds(_SHP) == 1328

    def test_nonnegative(self):
        assert fodg_file_size_minus_shape_count_hundreds(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_minus_shape_count_hundreds(_SHP) == fodg_file_size_minus_shape_count_hundreds(_SHP)


class TestFodgShapesPlusTextsSquared:
    def test_return_type(self):
        assert isinstance(fodg_shapes_plus_texts_squared(_EMPTY), int)

    def test_zero_for_empty(self):
        # empty-page: (0+0)^2 = 0
        assert fodg_shapes_plus_texts_squared(_EMPTY) == 0

    def test_exact_4_for_minimal(self):
        # minimal-drawing: (1+1)^2 = 4
        assert fodg_shapes_plus_texts_squared(_MIN) == 4

    def test_exact_25_for_shapes_basic(self):
        # shapes-basic: (3+2)^2 = 25
        assert fodg_shapes_plus_texts_squared(_SHP) == 25

    def test_nonnegative(self):
        assert fodg_shapes_plus_texts_squared(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_shapes_plus_texts_squared(_SHP) == fodg_shapes_plus_texts_squared(_SHP)
