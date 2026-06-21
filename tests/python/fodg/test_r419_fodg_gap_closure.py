"""Tests for 8 FODG FOSS gap closure functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_has_more_shapes_than_text_items,
    fodg_has_exactly_one_text_item,
    fodg_has_at_least_two_shapes,
    fodg_text_count_plus_page_count,
    fodg_has_only_one_shape,
    fodg_page_equals_shape_count,
    fodg_has_zero_text_items,
    fodg_text_times_shape_plus_page_count,
    fodg_total_shape_count,
    fodg_text_item_count,
    fodg_page_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _SAMPLES / "empty-page.fodg"
_SHAPES = _SAMPLES / "shapes-basic.fodg"


class TestFodgHasMoreShapesThanTextItems:
    def test_returns_bool(self):
        assert isinstance(fodg_has_more_shapes_than_text_items(_EMPTY), bool)

    def test_consistent(self):
        assert fodg_has_more_shapes_than_text_items(_EMPTY) == fodg_has_more_shapes_than_text_items(_EMPTY)

    def test_matches_manual(self):
        shapes = fodg_total_shape_count(_SHAPES)
        texts = fodg_text_item_count(_SHAPES)
        assert fodg_has_more_shapes_than_text_items(_SHAPES) == (shapes > texts)


class TestFodgHasExactlyOneTextItem:
    def test_returns_bool(self):
        assert isinstance(fodg_has_exactly_one_text_item(_EMPTY), bool)

    def test_matches_count(self):
        assert fodg_has_exactly_one_text_item(_SHAPES) == (fodg_text_item_count(_SHAPES) == 1)

    def test_empty(self):
        assert fodg_has_exactly_one_text_item(_EMPTY) == (fodg_text_item_count(_EMPTY) == 1)


class TestFodgHasAtLeastTwoShapes:
    def test_returns_bool(self):
        assert isinstance(fodg_has_at_least_two_shapes(_EMPTY), bool)

    def test_matches_count(self):
        assert fodg_has_at_least_two_shapes(_SHAPES) == (fodg_total_shape_count(_SHAPES) >= 2)

    def test_empty(self):
        assert fodg_has_at_least_two_shapes(_EMPTY) == (fodg_total_shape_count(_EMPTY) >= 2)


class TestFodgTextCountPlusPageCount:
    def test_returns_int(self):
        assert isinstance(fodg_text_count_plus_page_count(_EMPTY), int)

    def test_matches_sum(self):
        assert fodg_text_count_plus_page_count(_SHAPES) == fodg_text_item_count(_SHAPES) + fodg_page_count(_SHAPES)

    def test_nonnegative(self):
        assert fodg_text_count_plus_page_count(_EMPTY) >= 0


class TestFodgHasOnlyOneShape:
    def test_returns_bool(self):
        assert isinstance(fodg_has_only_one_shape(_EMPTY), bool)

    def test_matches_count(self):
        assert fodg_has_only_one_shape(_SHAPES) == (fodg_total_shape_count(_SHAPES) == 1)


class TestFodgPageEqualsShapeCount:
    def test_returns_bool(self):
        assert isinstance(fodg_page_equals_shape_count(_EMPTY), bool)

    def test_matches_manual(self):
        assert fodg_page_equals_shape_count(_SHAPES) == (fodg_page_count(_SHAPES) == fodg_total_shape_count(_SHAPES))


class TestFodgHasZeroTextItems:
    def test_returns_bool(self):
        assert isinstance(fodg_has_zero_text_items(_EMPTY), bool)

    def test_empty(self):
        assert fodg_has_zero_text_items(_EMPTY) == (fodg_text_item_count(_EMPTY) == 0)

    def test_shapes(self):
        assert fodg_has_zero_text_items(_SHAPES) == (fodg_text_item_count(_SHAPES) == 0)


class TestFodgTextTimesShapePlusPageCount:
    def test_returns_int(self):
        assert isinstance(fodg_text_times_shape_plus_page_count(_EMPTY), int)

    def test_matches_formula(self):
        t = fodg_text_item_count(_SHAPES)
        s = fodg_total_shape_count(_SHAPES)
        p = fodg_page_count(_SHAPES)
        assert fodg_text_times_shape_plus_page_count(_SHAPES) == t * s + p

    def test_consistent(self):
        assert fodg_text_times_shape_plus_page_count(_EMPTY) == fodg_text_times_shape_plus_page_count(_EMPTY)
