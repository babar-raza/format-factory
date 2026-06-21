"""Sprint 415 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100,
    fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900,
)


# --- F1: fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100 ---

class TestFodgFileSizeMod677Times4600PlusShape5600PlusText5100:
    def test_empty_returns_1729600(self):
        assert fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY) == 1729600

    def test_mini_returns_558100(self):
        assert fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(MINI) == 558100

    def test_shapes_returns_1287400(self):
        assert fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(SHAPES) == 1287400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY) >
                fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_677_times_4600_plus_shape_count_times_5600_plus_text_count_times_5100(str(EMPTY)) == 1729600


# --- F2: fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900 ---

class TestFodgFileSizeMod683Times4650PlusShape5400PlusText4900:
    def test_empty_returns_1720500(self):
        assert fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY) == 1720500

    def test_mini_returns_507850(self):
        assert fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(MINI) == 507850

    def test_shapes_returns_1244300(self):
        assert fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(SHAPES) == 1244300

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY) >
                fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_683_times_4650_plus_shape_count_times_5400_plus_text_count_times_4900(str(EMPTY)) == 1720500
