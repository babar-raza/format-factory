"""Sprint 253 FODG deepening — 2 new analytics functions, 12 tests."""
from pathlib import Path

import pytest

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700,
    fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500,
)

_SAMPLES = Path("samples/by-format/fodg")
_EMPTY = _SAMPLES / "empty-page.fodg"      # sz=1053, sc=0, tc=0
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"  # sz=1473, sc=1, tc=1
_SHAPES = _SAMPLES / "shapes-basic.fodg"   # sz=1628, sc=3, tc=2

# fn1 = sz % 43 * 2 + sc * 1400 + tc * 700
#   empty:   1053 % 43 * 2 + 0 + 0  = 21 * 2 = 42
#   minimal: 1473 % 43 * 2 + 1400 + 700 = 11 * 2 + 2100 = 2122
#   shapes:  1628 % 43 * 2 + 4200 + 1400 = 37 * 2 + 5600 = 5674

# fn2 = sz % 47 + sc * 800 + tc * 500
#   empty:   1053 % 47 + 0 + 0 = 19
#   minimal: 1473 % 47 + 800 + 500 = 16 + 1300 = 1316
#   shapes:  1628 % 47 + 2400 + 1000 = 30 + 3400 = 3430


class TestFodgFileSizeMod43Times2PlusShapeCount1400PlusTextCount700:
    def test_empty_returns_42(self):
        assert fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_EMPTY) == 42

    def test_minimal_returns_2122(self):
        assert fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_MINIMAL) == 2122

    def test_shapes_returns_5674(self):
        assert fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_SHAPES) == 5674

    def test_empty_is_positive(self):
        result = fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_EMPTY)
        assert result > 0

    def test_shapes_greater_than_minimal(self):
        r_s = fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_SHAPES)
        r_m = fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_MINIMAL)
        assert r_s > r_m

    def test_returns_int(self):
        result = fodg_file_size_mod_43_times_2_plus_shape_count_times_1400_plus_text_count_times_700(_MINIMAL)
        assert isinstance(result, int)


class TestFodgFileSizeMod47PlusShapeCount800PlusTextCount500:
    def test_empty_returns_19(self):
        assert fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_EMPTY) == 19

    def test_minimal_returns_1316(self):
        assert fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_MINIMAL) == 1316

    def test_shapes_returns_3430(self):
        assert fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_SHAPES) == 3430

    def test_empty_is_positive(self):
        result = fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_EMPTY)
        assert result > 0

    def test_shapes_greater_than_minimal(self):
        r_s = fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_SHAPES)
        r_m = fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_MINIMAL)
        assert r_s > r_m

    def test_returns_int(self):
        result = fodg_file_size_mod_47_plus_shape_count_times_800_plus_text_count_times_500(_MINIMAL)
        assert isinstance(result, int)
