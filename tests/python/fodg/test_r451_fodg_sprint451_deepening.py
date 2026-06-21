"""Sprint 451 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400,
    fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200,
)


class TestFodgFileSizeMod853Times5800PlusShape4600PlusText4400:
    def test_empty_returns_1160000(self):
        assert fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(EMPTY) == 1160000

    def test_mini_returns_3605000(self):
        assert fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(MINI) == 3605000

    def test_shapes_returns_4517600(self):
        assert fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(SHAPES) == 4517600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(MINI) >
                fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_853_times_5800_plus_shape_count_times_4600_plus_text_count_times_4400(str(EMPTY)) == 1160000


class TestFodgFileSizeMod857Times5850PlusShape4400PlusText4200:
    def test_empty_returns_1146600(self):
        assert fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(EMPTY) == 1146600

    def test_mini_returns_3612200(self):
        assert fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(MINI) == 3612200

    def test_shapes_returns_4531950(self):
        assert fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(SHAPES) == 4531950

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(MINI) >
                fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_857_times_5850_plus_shape_count_times_4400_plus_text_count_times_4200(str(EMPTY)) == 1146600
