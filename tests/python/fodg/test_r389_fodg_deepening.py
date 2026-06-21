"""Tests for FODG product deepening sprint 160.

New functions:
  fodg_file_size_times_page_count  — file size in bytes * page count
  fodg_text_item_count_squared     — text item count squared
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_times_page_count,
    fodg_text_item_count_squared,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeTimesPageCount:
    def test_return_type(self):
        assert isinstance(fodg_file_size_times_page_count(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: size=1053, pages=1 → 1053
        assert fodg_file_size_times_page_count(_EMPTY) == 1053

    def test_exact_1473_for_minimal(self):
        # minimal-drawing: size=1473, pages=1 → 1473
        assert fodg_file_size_times_page_count(_MIN) == 1473

    def test_exact_1628_for_shapes_basic(self):
        # shapes-basic: size=1628, pages=1 → 1628
        assert fodg_file_size_times_page_count(_SHP) == 1628

    def test_positive(self):
        assert fodg_file_size_times_page_count(_EMPTY) > 0

    def test_consistent(self):
        assert fodg_file_size_times_page_count(_SHP) == fodg_file_size_times_page_count(_SHP)


class TestFodgTextItemCountSquared:
    def test_return_type(self):
        assert isinstance(fodg_text_item_count_squared(_EMPTY), int)

    def test_zero_for_empty(self):
        # empty-page: 0 texts → 0*0 = 0
        assert fodg_text_item_count_squared(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        # minimal-drawing: 1 text → 1*1 = 1
        assert fodg_text_item_count_squared(_MIN) == 1

    def test_exact_4_for_shapes_basic(self):
        # shapes-basic: 2 texts → 2*2 = 4
        assert fodg_text_item_count_squared(_SHP) == 4

    def test_nonnegative(self):
        assert fodg_text_item_count_squared(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_text_item_count_squared(_SHP) == fodg_text_item_count_squared(_SHP)
