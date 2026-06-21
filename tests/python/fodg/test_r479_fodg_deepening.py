"""Sprint 250 FODG deepening — 2 new analytics functions, 12 tests."""
from pathlib import Path

import pytest

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900,
    fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600,
)

_SAMPLES = Path("samples/by-format/fodg")
_EMPTY = _SAMPLES / "empty-page.fodg"      # sz=1053, sc=0, tc=0
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"  # sz=1473, sc=1, tc=1
_SHAPES = _SAMPLES / "shapes-basic.fodg"   # sz=1628, sc=3, tc=2

# Expected values:
# fn1 = (sz % 31) * 3 + sc * 1200 + tc * 900
#   empty:   (1053 % 31) * 3 + 0 * 1200 + 0 * 900 = (1053 % 31) * 3
#     1053 / 31 = 33 r 30 → 30 * 3 = 90
#   minimal: (1473 % 31) * 3 + 1 * 1200 + 1 * 900 = (1473 % 31) * 3 + 2100
#     1473 / 31 = 47 r 16 → 16 * 3 + 2100 = 48 + 2100 = 2148
#   shapes:  (1628 % 31) * 3 + 3 * 1200 + 2 * 900 = (1628 % 31) * 3 + 5400
#     1628 / 31 = 52 r 16 → 16 * 3 + 5400 = 48 + 5400 = 5448

# fn2 = (sz % 37) + sc * 900 + tc * 600
#   empty:   (1053 % 37) + 0 * 900 + 0 * 600 = 1053 % 37
#     1053 / 37 = 28 r 17 → 17
#   minimal: (1473 % 37) + 1 * 900 + 1 * 600 = (1473 % 37) + 1500
#     1473 / 37 = 39 r 30 → 30 + 1500 = 1530
#   shapes:  (1628 % 37) + 3 * 900 + 2 * 600 = (1628 % 37) + 3900
#     1628 / 37 = 44 r 0 → 0 + 3900 = 3900


class TestFodgFileSizeMod31Times3PlusShapeCount1200PlusTextCount900:
    def test_empty_returns_90(self):
        assert fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_EMPTY) == 90

    def test_minimal_returns_2148(self):
        assert fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_MINIMAL) == 2148

    def test_shapes_returns_5448(self):
        assert fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_SHAPES) == 5448

    def test_empty_is_positive(self):
        result = fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_EMPTY)
        assert result > 0

    def test_shapes_greater_than_minimal(self):
        r_s = fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_SHAPES)
        r_m = fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_MINIMAL)
        assert r_s > r_m

    def test_returns_int(self):
        result = fodg_file_size_mod_31_times_3_plus_shape_count_times_1200_plus_text_count_times_900(_MINIMAL)
        assert isinstance(result, int)


class TestFodgFileSizeMod37PlusShapeCount900PlusTextCount600:
    def test_empty_returns_17(self):
        assert fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_EMPTY) == 17

    def test_minimal_returns_1530(self):
        assert fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_MINIMAL) == 1530

    def test_shapes_returns_3900(self):
        assert fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_SHAPES) == 3900

    def test_empty_is_positive(self):
        result = fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_EMPTY)
        assert result > 0

    def test_shapes_greater_than_minimal(self):
        r_s = fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_SHAPES)
        r_m = fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_MINIMAL)
        assert r_s > r_m

    def test_returns_int(self):
        result = fodg_file_size_mod_37_plus_shape_count_times_900_plus_text_count_times_600(_MINIMAL)
        assert isinstance(result, int)
