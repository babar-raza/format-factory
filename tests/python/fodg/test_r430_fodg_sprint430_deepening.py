"""Sprint 430 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600,
    fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400,
)


# --- F1: fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600 ---

class TestFodgFileSizeMod751Times5100PlusShape6100PlusText5600:
    def test_empty_returns_1540200(self):
        assert fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY) == 1540200

    def test_mini_returns_3693900(self):
        assert fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(MINI) == 3693900

    def test_shapes_returns_672100(self):
        assert fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(SHAPES) == 672100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(EMPTY) >
                fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_751_times_5100_plus_shape_count_times_6100_plus_text_count_times_5600(str(EMPTY)) == 1540200


# --- F2: fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400 ---

class TestFodgFileSizeMod757Times5150PlusShape5900PlusText5400:
    def test_empty_returns_1524400(self):
        assert fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY) == 1524400

    def test_mini_returns_3698700(self):
        assert fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(MINI) == 3698700

    def test_shapes_returns_615600(self):
        assert fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(SHAPES) == 615600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY) >
                fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_757_times_5150_plus_shape_count_times_5900_plus_text_count_times_5400(str(EMPTY)) == 1524400
