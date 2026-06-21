"""Tests for FODG product deepening sprint 157.

New functions:
  fodg_file_size_plus_page_count          — file size in bytes + page count
  fodg_shape_count_times_two_plus_text_count — shapes*2 + text item count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_plus_page_count,
    fodg_shape_count_times_two_plus_text_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizePlusPageCount:
    def test_return_type(self):
        assert isinstance(fodg_file_size_plus_page_count(_EMPTY), int)

    def test_exact_1054_for_empty(self):
        # empty-page: size=1053, pages=1 → 1054
        assert fodg_file_size_plus_page_count(_EMPTY) == 1054

    def test_exact_1474_for_minimal(self):
        # minimal-drawing: size=1473, pages=1 → 1474
        assert fodg_file_size_plus_page_count(_MIN) == 1474

    def test_exact_1629_for_shapes_basic(self):
        # shapes-basic: size=1628, pages=1 → 1629
        assert fodg_file_size_plus_page_count(_SHP) == 1629

    def test_positive(self):
        assert fodg_file_size_plus_page_count(_EMPTY) > 0

    def test_consistent(self):
        assert fodg_file_size_plus_page_count(_SHP) == fodg_file_size_plus_page_count(_SHP)


class TestFodgShapeCountTimesTwoPlusTextCount:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_times_two_plus_text_count(_EMPTY), int)

    def test_zero_for_empty(self):
        # empty-page: 0*2 + 0 = 0
        assert fodg_shape_count_times_two_plus_text_count(_EMPTY) == 0

    def test_exact_3_for_minimal(self):
        # minimal-drawing: 1*2 + 1 = 3
        assert fodg_shape_count_times_two_plus_text_count(_MIN) == 3

    def test_exact_8_for_shapes_basic(self):
        # shapes-basic: 3*2 + 2 = 8
        assert fodg_shape_count_times_two_plus_text_count(_SHP) == 8

    def test_nonnegative(self):
        assert fodg_shape_count_times_two_plus_text_count(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_shape_count_times_two_plus_text_count(_SHP) == fodg_shape_count_times_two_plus_text_count(_SHP)
