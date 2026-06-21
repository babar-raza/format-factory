"""Sprint 418 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200,
    fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000,
)


# --- F1: fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200 ---

class TestFodgFileSizeMod691Times4700PlusShape5700PlusText5200:
    def test_empty_returns_1701400(self):
        assert fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY) == 1701400

    def test_mini_returns_438600(self):
        assert fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(MINI) == 438600

    def test_shapes_returns_1183700(self):
        assert fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(SHAPES) == 1183700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY) >
                fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_691_times_4700_plus_shape_count_times_5700_plus_text_count_times_5200(str(EMPTY)) == 1701400


# --- F2: fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000 ---

class TestFodgFileSizeMod701Times4750PlusShape5500PlusText5000:
    def test_empty_returns_1672000(self):
        assert fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY) == 1672000

    def test_mini_returns_347750(self):
        assert fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(MINI) == 347750

    def test_shapes_returns_1100000(self):
        assert fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(SHAPES) == 1100000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY) >
                fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_701_times_4750_plus_shape_count_times_5500_plus_text_count_times_5000(str(EMPTY)) == 1672000
