"""Tests for FODG product deepening sprint 181.

New functions:
  fodg_text_count_times_file_size_div_100  — tc * sz // 100
  fodg_file_size_plus_text_count_times_10  — sz + tc*10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_text_count_times_file_size_div_100,
    fodg_file_size_plus_text_count_times_10,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgTextCountTimesFileSizeDiv100:
    def test_return_type(self):
        assert isinstance(fodg_text_count_times_file_size_div_100(_EMPTY), int)

    def test_exact_0_for_empty(self):
        # empty-page: tc=0, sz=1053 → 0*1053//100 = 0
        assert fodg_text_count_times_file_size_div_100(_EMPTY) == 0

    def test_exact_14_for_minimal(self):
        # minimal-drawing: tc=1, sz=1473 → 1*1473//100 = 14
        assert fodg_text_count_times_file_size_div_100(_MINIMAL) == 14

    def test_exact_32_for_shapes(self):
        # shapes-basic: tc=2, sz=1628 → 2*1628//100 = 32
        assert fodg_text_count_times_file_size_div_100(_SHAPES) == 32

    def test_nonnegative(self):
        assert fodg_text_count_times_file_size_div_100(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_text_count_times_file_size_div_100(_SHAPES) == fodg_text_count_times_file_size_div_100(_SHAPES)


class TestFodgFileSizePlusTextCountTimes10:
    def test_return_type(self):
        assert isinstance(fodg_file_size_plus_text_count_times_10(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: sz=1053, tc=0 → 1053 + 0 = 1053
        assert fodg_file_size_plus_text_count_times_10(_EMPTY) == 1053

    def test_exact_1483_for_minimal(self):
        # minimal-drawing: sz=1473, tc=1 → 1473 + 10 = 1483
        assert fodg_file_size_plus_text_count_times_10(_MINIMAL) == 1483

    def test_exact_1648_for_shapes(self):
        # shapes-basic: sz=1628, tc=2 → 1628 + 20 = 1648
        assert fodg_file_size_plus_text_count_times_10(_SHAPES) == 1648

    def test_positive(self):
        assert fodg_file_size_plus_text_count_times_10(_EMPTY) > 0

    def test_consistent(self):
        assert fodg_file_size_plus_text_count_times_10(_SHAPES) == fodg_file_size_plus_text_count_times_10(_SHAPES)
