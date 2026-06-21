"""Sprint 400 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600,
    fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400,
)


# --- F1: fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600 ---

class TestFodgFileSizeMod617Times4100PlusShape5100PlusText4600:
    def test_empty_returns_1787600(self):
        assert fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY) == 1787600

    def test_mini_returns_989600(self):
        assert fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(MINI) == 989600

    def test_shapes_returns_1639900(self):
        assert fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(SHAPES) == 1639900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY) >
                fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_617_times_4100_plus_shape_count_times_5100_plus_text_count_times_4600(str(EMPTY)) == 1787600


# --- F2: fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400 ---

class TestFodgFileSizeMod619Times4150PlusShape4900PlusText4400:
    def test_empty_returns_1801100(self):
        assert fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY) == 1801100

    def test_mini_returns_984550(self):
        assert fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(MINI) == 984550

    def test_shapes_returns_1642000(self):
        assert fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(SHAPES) == 1642000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY) >
                fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_619_times_4150_plus_shape_count_times_4900_plus_text_count_times_4400(str(EMPTY)) == 1801100
