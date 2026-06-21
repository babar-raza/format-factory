"""Sprint 331 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300,
    fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100,
)


# --- F1: fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300 ---

class TestFodgFileSizeMod311Times1800PlusShape2800PlusText2300:
    def test_empty_returns_216000(self):
        assert fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(EMPTY) == 216000

    def test_minimal_returns_417300(self):
        assert fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL) == 417300

    def test_shapes_returns_144400(self):
        assert fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(SHAPES) == 144400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL) >
                fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_311_times_1800_plus_shape_count_times_2800_plus_text_count_times_2300(str(EMPTY)) == 216000


# --- F2: fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100 ---

class TestFodgFileSizeMod313Times1850PlusShape2600PlusText2100:
    def test_empty_returns_210900(self):
        assert fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(EMPTY) == 210900

    def test_minimal_returns_413550(self):
        assert fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL) == 413550

    def test_shapes_returns_128550(self):
        assert fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(SHAPES) == 128550

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(MINIMAL) >
                fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_313_times_1850_plus_shape_count_times_2600_plus_text_count_times_2100(str(EMPTY)) == 210900
