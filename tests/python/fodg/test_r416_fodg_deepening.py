"""Tests for FODG product deepening sprint 187.

New functions:
  fodg_file_size_plus_shape_count_times_100  — sz + sc*100
  fodg_file_size_div_10_plus_text_count  — sz//10 + tc
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_plus_shape_count_times_100,
    fodg_file_size_div_10_plus_text_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizePlusShapeCountTimes100:
    def test_return_type(self):
        assert isinstance(fodg_file_size_plus_shape_count_times_100(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: sz=1053, sc=0 → 1053 + 0*100 = 1053
        assert fodg_file_size_plus_shape_count_times_100(_EMPTY) == 1053

    def test_exact_1573_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1 → 1473 + 1*100 = 1573
        assert fodg_file_size_plus_shape_count_times_100(_MINIMAL) == 1573

    def test_exact_1928_for_shapes(self):
        # shapes-basic: sz=1628, sc=3 → 1628 + 3*100 = 1928
        assert fodg_file_size_plus_shape_count_times_100(_SHAPES) == 1928

    def test_nonnegative(self):
        assert fodg_file_size_plus_shape_count_times_100(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_plus_shape_count_times_100(_SHAPES) == fodg_file_size_plus_shape_count_times_100(_SHAPES)


class TestFodgFileSizeDiv10PlusTextCount:
    def test_return_type(self):
        assert isinstance(fodg_file_size_div_10_plus_text_count(_EMPTY), int)

    def test_exact_105_for_empty(self):
        # empty-page: sz=1053, tc=0 → 1053//10 + 0 = 105
        assert fodg_file_size_div_10_plus_text_count(_EMPTY) == 105

    def test_exact_148_for_minimal(self):
        # minimal-drawing: sz=1473, tc=1 → 1473//10 + 1 = 148
        assert fodg_file_size_div_10_plus_text_count(_MINIMAL) == 148

    def test_exact_164_for_shapes(self):
        # shapes-basic: sz=1628, tc=2 → 1628//10 + 2 = 164
        assert fodg_file_size_div_10_plus_text_count(_SHAPES) == 164

    def test_nonnegative(self):
        assert fodg_file_size_div_10_plus_text_count(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_div_10_plus_text_count(_SHAPES) == fodg_file_size_div_10_plus_text_count(_SHAPES)
