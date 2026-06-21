"""Sprint 445 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200,
    fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000,
)


class TestFodgFileSizeMod823Times5600PlusShape5400PlusText5200:
    def test_empty_returns_1288000(self):
        assert fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(EMPTY) == 1288000

    def test_mini_returns_3650600(self):
        assert fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(MINI) == 3650600

    def test_shapes_returns_4534600(self):
        assert fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(SHAPES) == 4534600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(MINI) >
                fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_823_times_5600_plus_shape_count_times_5400_plus_text_count_times_5200(str(EMPTY)) == 1288000


class TestFodgFileSizeMod827Times5650PlusShape5200PlusText5000:
    def test_empty_returns_1276900(self):
        assert fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(EMPTY) == 1276900

    def test_mini_returns_3660100(self):
        assert fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(MINI) == 3660100

    def test_shapes_returns_4551250(self):
        assert fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(SHAPES) == 4551250

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(MINI) >
                fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_827_times_5650_plus_shape_count_times_5200_plus_text_count_times_5000(str(EMPTY)) == 1276900
