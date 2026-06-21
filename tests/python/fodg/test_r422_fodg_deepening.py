"""Tests for FODG product deepening sprint 193.

New functions:
  fodg_file_size_times_2_plus_shape_count_times_50  — sz*2 + sc*50
  fodg_file_size_minus_text_count_times_100  — max(0, sz - tc*100)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_times_2_plus_shape_count_times_50,
    fodg_file_size_minus_text_count_times_100,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeTimes2PlusShapeCountTimes50:
    def test_return_type(self):
        assert isinstance(fodg_file_size_times_2_plus_shape_count_times_50(_EMPTY), int)

    def test_exact_2106_for_empty(self):
        # empty-page: sz=1053, sc=0 → 1053*2 + 0*50 = 2106
        assert fodg_file_size_times_2_plus_shape_count_times_50(_EMPTY) == 2106

    def test_exact_2996_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1 → 1473*2 + 1*50 = 2996
        assert fodg_file_size_times_2_plus_shape_count_times_50(_MINIMAL) == 2996

    def test_exact_3406_for_shapes(self):
        # shapes-basic: sz=1628, sc=3 → 1628*2 + 3*50 = 3406
        assert fodg_file_size_times_2_plus_shape_count_times_50(_SHAPES) == 3406

    def test_nonnegative(self):
        assert fodg_file_size_times_2_plus_shape_count_times_50(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_times_2_plus_shape_count_times_50(_SHAPES) == fodg_file_size_times_2_plus_shape_count_times_50(_SHAPES)


class TestFodgFileSizeMinusTextCountTimes100:
    def test_return_type(self):
        assert isinstance(fodg_file_size_minus_text_count_times_100(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: sz=1053, tc=0 → max(0, 1053 - 0*100) = 1053
        assert fodg_file_size_minus_text_count_times_100(_EMPTY) == 1053

    def test_exact_1373_for_minimal(self):
        # minimal-drawing: sz=1473, tc=1 → max(0, 1473 - 1*100) = 1373
        assert fodg_file_size_minus_text_count_times_100(_MINIMAL) == 1373

    def test_exact_1428_for_shapes(self):
        # shapes-basic: sz=1628, tc=2 → max(0, 1628 - 2*100) = 1428
        assert fodg_file_size_minus_text_count_times_100(_SHAPES) == 1428

    def test_nonnegative(self):
        assert fodg_file_size_minus_text_count_times_100(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_minus_text_count_times_100(_SHAPES) == fodg_file_size_minus_text_count_times_100(_SHAPES)
