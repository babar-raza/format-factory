"""Sprint 439 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900,
    fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700,
)


class TestFodgFileSizeMod797Times5400PlusShape6200PlusText5900:
    def test_empty_returns_1382400(self):
        assert fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(EMPTY) == 1382400

    def test_mini_returns_3662500(self):
        assert fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(MINI) == 3662500

    def test_shapes_returns_214000(self):
        assert fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(SHAPES) == 214000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(EMPTY) >
                fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_797_times_5400_plus_shape_count_times_6200_plus_text_count_times_5900(str(EMPTY)) == 1382400


class TestFodgFileSizeMod809Times5450PlusShape6000PlusText5700:
    def test_empty_returns_1329800(self):
        assert fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(EMPTY) == 1329800

    def test_mini_returns_3630500(self):
        assert fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(MINI) == 3630500

    def test_shapes_returns_83900(self):
        assert fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(SHAPES) == 83900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(EMPTY) >
                fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_809_times_5450_plus_shape_count_times_6000_plus_text_count_times_5700(str(EMPTY)) == 1329800
