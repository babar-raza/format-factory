"""Sprint 247 FODG analytics deepening tests.

Functions:
- fodg_file_size_mod_11_times_200_plus_shape_count_times_900_plus_text_count_times_400
- fodg_file_size_mod_7_times_100_plus_shape_count_times_600_plus_text_count_times_500
"""
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
FODG = REPO / "samples/by-format/fodg"
EMPTY = FODG / "empty-page.fodg"
MINIMAL = FODG / "minimal-drawing.fodg"
SHAPES = FODG / "shapes-basic.fodg"

from src.python.fodg import (
    fodg_file_size_mod_11_times_200_plus_shape_count_times_900_plus_text_count_times_400 as f1,
    fodg_file_size_mod_7_times_100_plus_shape_count_times_600_plus_text_count_times_500 as f2,
)


class TestFodgFileSizeMod11Times200PlusShapeCountTimes900PlusTextCountTimes400:
    def test_empty_page(self):
        assert f1(EMPTY) == 1600

    def test_minimal_drawing(self):
        assert f1(MINIMAL) == 3300

    def test_shapes_basic(self):
        assert f1(SHAPES) == 3500

    def test_returns_int(self):
        assert isinstance(f1(EMPTY), int)

    def test_nonnegative(self):
        assert f1(EMPTY) >= 0

    def test_distinct_empty_minimal(self):
        assert f1(EMPTY) != f1(MINIMAL)

    def test_distinct_minimal_shapes(self):
        assert f1(MINIMAL) != f1(SHAPES)

    def test_shapes_largest(self):
        assert f1(SHAPES) > f1(EMPTY)

    def test_minimal_larger_than_empty(self):
        assert f1(MINIMAL) > f1(EMPTY)

    def test_path_object(self):
        assert f1(Path(EMPTY)) == 1600


class TestFodgFileSizeMod7Times100PlusShapeCountTimes600PlusTextCountTimes500:
    def test_empty_page(self):
        assert f2(EMPTY) == 300

    def test_minimal_drawing(self):
        assert f2(MINIMAL) == 1400

    def test_shapes_basic(self):
        assert f2(SHAPES) == 3200

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
        assert f2(Path(EMPTY)) == 300
