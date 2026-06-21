"""Sprint 250 FODG analytics deepening tests.

Functions:
- fodg_file_size_mod_7_times_300_plus_shape_count_times_800_plus_text_count_times_400
- fodg_file_size_mod_17_times_50_plus_shape_count_times_500_plus_text_count_times_250
"""
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
FODG = REPO / "samples/by-format/fodg"
EMPTY = FODG / "empty-page.fodg"    # fs=1053, shapes=0, text=0
MINIMAL = FODG / "minimal-drawing.fodg"  # fs=1473, shapes=1, text=1
SHAPES = FODG / "shapes-basic.fodg"     # fs=1628, shapes=3, text=2

from src.python.fodg import (
    fodg_file_size_mod_7_times_300_plus_shape_count_times_800_plus_text_count_times_400 as f1,
    fodg_file_size_mod_17_times_50_plus_shape_count_times_500_plus_text_count_times_250 as f2,
)


class TestFodgFileSizeMod7Times300PlusShapeCountTimes800PlusTextCountTimes400:
    def test_empty_page(self):
        assert f1(EMPTY) == 900

    def test_minimal_drawing(self):
        assert f1(MINIMAL) == 2100

    def test_shapes_basic(self):
        assert f1(SHAPES) == 4400

    def test_returns_int(self):
        assert isinstance(f1(EMPTY), int)

    def test_nonnegative(self):
        assert f1(EMPTY) >= 0

    def test_distinct_empty_minimal(self):
        assert f1(EMPTY) != f1(MINIMAL)

    def test_distinct_minimal_shapes(self):
        assert f1(MINIMAL) != f1(SHAPES)

    def test_shapes_largest(self):
        assert f1(SHAPES) > f1(MINIMAL)

    def test_minimal_larger_than_empty(self):
        assert f1(MINIMAL) > f1(EMPTY)

    def test_path_object(self):
        assert f1(Path(EMPTY)) == 900


class TestFodgFileSizeMod17Times50PlusShapeCountTimes500PlusTextCountTimes250:
    def test_empty_page(self):
        assert f2(EMPTY) == 800

    def test_minimal_drawing(self):
        assert f2(MINIMAL) == 1300

    def test_shapes_basic(self):
        assert f2(SHAPES) == 2650

    def test_returns_int(self):
        assert isinstance(f2(EMPTY), int)

    def test_nonnegative(self):
        assert f2(EMPTY) >= 0

    def test_distinct_empty_minimal(self):
        assert f2(EMPTY) != f2(MINIMAL)

    def test_distinct_minimal_shapes(self):
        assert f2(MINIMAL) != f2(SHAPES)

    def test_shapes_largest(self):
        assert f2(SHAPES) > f2(MINIMAL)

    def test_minimal_larger_than_empty(self):
        assert f2(MINIMAL) > f2(EMPTY)

    def test_path_object(self):
        assert f2(Path(EMPTY)) == 800
