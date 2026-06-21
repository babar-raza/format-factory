"""Sprint 379 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900,
    fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700,
)


# --- F1: fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900 ---

class TestFodgFileSizeMod523Times3400PlusShape4400PlusText3900:
    def test_empty_returns_23800(self):
        assert fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY) == 23800

    def test_minimal_returns_1460100(self):
        assert fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL) == 1460100

    def test_shapes_returns_221600(self):
        assert fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(SHAPES) == 221600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL) >= 0

    def test_minimal_greater_than_empty(self):
        assert (fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL) >
                fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_523_times_3400_plus_shape_count_times_4400_plus_text_count_times_3900(str(EMPTY)) == 23800


# --- F2: fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700 ---

class TestFodgFileSizeMod541Times3450PlusShape4200PlusText3700:
    def test_empty_returns_1766400(self):
        assert fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY) == 1766400

    def test_minimal_returns_1356850(self):
        assert fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(MINIMAL) == 1356850

    def test_shapes_returns_37250(self):
        assert fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(SHAPES) == 37250

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(MINIMAL) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY) >
                fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_541_times_3450_plus_shape_count_times_4200_plus_text_count_times_3700(str(EMPTY)) == 1766400
