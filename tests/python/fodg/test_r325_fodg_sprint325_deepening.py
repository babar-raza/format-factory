"""Sprint 325 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100,
    fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900,
)


# --- F1: fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100 ---

class TestFodgFileSizeMod281Times1600PlusShape2600PlusText2100:
    def test_empty_returns_336000(self):
        assert fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(EMPTY) == 336000

    def test_minimal_returns_113500(self):
        assert fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL) == 113500

    def test_shapes_returns_368800(self):
        assert fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(SHAPES) == 368800

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(SHAPES) >
                fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_281_times_1600_plus_shape_count_times_2600_plus_text_count_times_2100(str(EMPTY)) == 336000


# --- F2: fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900 ---

class TestFodgFileSizeMod283Times1650PlusShape2400PlusText1900:
    def test_empty_returns_336600(self):
        assert fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(EMPTY) == 336600

    def test_minimal_returns_100000(self):
        assert fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL) == 100000

    def test_shapes_returns_362450(self):
        assert fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(SHAPES) == 362450

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(SHAPES) >
                fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_283_times_1650_plus_shape_count_times_2400_plus_text_count_times_1900(str(EMPTY)) == 336600
