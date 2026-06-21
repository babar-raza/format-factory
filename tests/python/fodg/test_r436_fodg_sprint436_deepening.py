"""Sprint 436 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800,
    fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600,
)


class TestFodgFileSizeMod773Times5300PlusShape6300PlusText5800:
    def test_empty_returns_1484000(self):
        assert fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(EMPTY) == 1484000

    def test_mini_returns_3722100(self):
        assert fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(MINI) == 3722100

    def test_shapes_returns_465100(self):
        assert fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(SHAPES) == 465100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(EMPTY) >
                fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_773_times_5300_plus_shape_count_times_6300_plus_text_count_times_5800(str(EMPTY)) == 1484000


class TestFodgFileSizeMod787Times5350PlusShape6100PlusText5600:
    def test_empty_returns_1423100(self):
        assert fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY) == 1423100

    def test_mini_returns_3681800(self):
        assert fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(MINI) == 3681800

    def test_shapes_returns_318400(self):
        assert fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(SHAPES) == 318400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY) >
                fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_787_times_5350_plus_shape_count_times_6100_plus_text_count_times_5600(str(EMPTY)) == 1423100
