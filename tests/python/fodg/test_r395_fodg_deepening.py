"""Tests for FODG product deepening sprint 166.

New functions:
  fodg_shape_count_squared_plus_text_count_squared — sc^2 + tc^2
  fodg_file_size_div_shape_count                   — file_size // shape_count (0 if no shapes)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_shape_count_squared_plus_text_count_squared,
    fodg_file_size_div_shape_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgShapeCountSquaredPlusTextCountSquared:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_squared_plus_text_count_squared(_EMPTY), int)

    def test_zero_for_empty(self):
        # empty-page: 0^2 + 0^2 = 0
        assert fodg_shape_count_squared_plus_text_count_squared(_EMPTY) == 0

    def test_exact_2_for_minimal(self):
        # minimal-drawing: 1^2 + 1^2 = 2
        assert fodg_shape_count_squared_plus_text_count_squared(_MIN) == 2

    def test_exact_13_for_shapes_basic(self):
        # shapes-basic: 3^2 + 2^2 = 9+4 = 13
        assert fodg_shape_count_squared_plus_text_count_squared(_SHP) == 13

    def test_nonnegative(self):
        assert fodg_shape_count_squared_plus_text_count_squared(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_shape_count_squared_plus_text_count_squared(_SHP) == fodg_shape_count_squared_plus_text_count_squared(_SHP)


class TestFodgFileSizeDivShapeCount:
    def test_return_type(self):
        assert isinstance(fodg_file_size_div_shape_count(_EMPTY), int)

    def test_zero_for_empty(self):
        # empty-page: 0 shapes → 0
        assert fodg_file_size_div_shape_count(_EMPTY) == 0

    def test_exact_1473_for_minimal(self):
        # minimal-drawing: 1473 // 1 = 1473
        assert fodg_file_size_div_shape_count(_MIN) == 1473

    def test_exact_542_for_shapes_basic(self):
        # shapes-basic: 1628 // 3 = 542
        assert fodg_file_size_div_shape_count(_SHP) == 542

    def test_nonnegative(self):
        assert fodg_file_size_div_shape_count(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_div_shape_count(_SHP) == fodg_file_size_div_shape_count(_SHP)
