"""Tests for FODG product deepening sprint 164.

New functions:
  fodg_file_size_div_10                            — file size // 10
  fodg_shape_count_times_text_count_times_page_count — shapes * texts * pages
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_div_10,
    fodg_shape_count_times_text_count_times_page_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeDiv10:
    def test_return_type(self):
        assert isinstance(fodg_file_size_div_10(_EMPTY), int)

    def test_exact_105_for_empty(self):
        # empty-page: 1053//10 = 105
        assert fodg_file_size_div_10(_EMPTY) == 105

    def test_exact_147_for_minimal(self):
        # minimal-drawing: 1473//10 = 147
        assert fodg_file_size_div_10(_MIN) == 147

    def test_exact_162_for_shapes_basic(self):
        # shapes-basic: 1628//10 = 162
        assert fodg_file_size_div_10(_SHP) == 162

    def test_positive(self):
        assert fodg_file_size_div_10(_EMPTY) > 0

    def test_consistent(self):
        assert fodg_file_size_div_10(_SHP) == fodg_file_size_div_10(_SHP)


class TestFodgShapeCountTimesTextCountTimesPageCount:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_times_text_count_times_page_count(_EMPTY), int)

    def test_zero_for_empty(self):
        # empty-page: 0 * 0 * 1 = 0
        assert fodg_shape_count_times_text_count_times_page_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        # minimal-drawing: 1 * 1 * 1 = 1
        assert fodg_shape_count_times_text_count_times_page_count(_MIN) == 1

    def test_exact_6_for_shapes_basic(self):
        # shapes-basic: 3 * 2 * 1 = 6
        assert fodg_shape_count_times_text_count_times_page_count(_SHP) == 6

    def test_nonnegative(self):
        assert fodg_shape_count_times_text_count_times_page_count(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_shape_count_times_text_count_times_page_count(_SHP) == fodg_shape_count_times_text_count_times_page_count(_SHP)
