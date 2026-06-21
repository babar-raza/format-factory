"""
tests/python/deepening/test_r799_fodg_sprint247_deepening.py

Sprint: sal-advancement-iter12-20260617-164500-8656416
Product deepening Sprint 247 — 2 new FODG analytics functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400,
    fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11,
)

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = str(_FODG_DIR / "empty-page.fodg")
_MINIMAL = str(_FODG_DIR / "minimal-drawing.fodg")
_SHAPES = str(_FODG_DIR / "shapes-basic.fodg")


class TestFodgMod167F1:
    """fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400"""

    def test_empty_returns_int(self):
        result = fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(_EMPTY)
        assert isinstance(result, int)

    def test_empty_expected_value(self):
        # fs=1053, sc=0, tc=0 → (1053%167)*5 + 0*2700 + 0*2400 = 51*5=255
        result = fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(_EMPTY)
        assert result == 255

    def test_minimal_expected_value(self):
        # fs=1473, sc=1, tc=1 → (1473%167)*5 + 1*2700 + 1*2400 = 1*5+2700+2400=5105... wait recalc
        # 1473 % 167 = 1473 - 8*167 = 1473 - 1336 = 137; 137*5=685; +2700+2400=5785
        result = fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(_MINIMAL)
        assert result == 5785

    def test_shapes_expected_value(self):
        # fs=1628, sc=3, tc=1 → (1628%167)*5 + 3*2700 + 1*2400
        # 1628 % 167 = 1628 - 9*167 = 1628 - 1503 = 125; 125*5=625; +8100+2400=11125
        result = fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(_SHAPES)
        assert result == 11125

    def test_returns_nonnegative(self):
        for path in [_EMPTY, _MINIMAL, _SHAPES]:
            result = fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_167_times_5_plus_shape_count_times_2700_plus_text_count_times_2400(Path(_EMPTY))
        assert result == 255


class TestFodgF2Times15:
    """fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11"""

    def test_empty_returns_int(self):
        result = fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(_EMPTY)
        assert isinstance(result, int)

    def test_empty_expected_value(self):
        # fs=1053, sc=0, tc=0, pc=1 → 1053*15 + 0 + 0 + 1*11 = 15795+11=15806
        result = fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(_EMPTY)
        assert result == 15806

    def test_minimal_expected_value(self):
        # fs=1473, sc=1, tc=1, pc=1 → 1473*15 + 1*35 + 1*22 + 1*11 = 22095+35+22+11=22163
        result = fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(_MINIMAL)
        assert result == 22163

    def test_shapes_expected_value(self):
        # fs=1628, sc=3, tc=1, pc=1 → 1628*15 + 3*35 + 1*22 + 1*11 = 24420+105+22+11=24558
        result = fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(_SHAPES)
        assert result == 24558

    def test_returns_nonnegative(self):
        for path in [_EMPTY, _MINIMAL, _SHAPES]:
            result = fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = fodg_file_size_times_15_plus_shape_count_times_35_plus_text_count_times_22_plus_page_count_times_11(Path(_EMPTY))
        assert result == 15806
