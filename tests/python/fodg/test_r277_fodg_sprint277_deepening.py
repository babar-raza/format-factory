"""Sprint 277 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750,
    fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450,
)


# --- F1: fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750 ---

class TestFodgFileSizeMod83Times350PlusShapeCount1150PlusTextCount750:
    def test_empty_returns_19950(self):
        assert fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(EMPTY) == 19950

    def test_minimal_returns_23600(self):
        assert fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(MINIMAL) == 23600

    def test_shapes_returns_22800(self):
        assert fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(SHAPES) == 22800

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(MINIMAL) >= 0

    def test_minimal_greater_than_empty(self):
        assert (fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(MINIMAL) >
                fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750(str(EMPTY)) == 19950


# --- F2: fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450 ---

class TestFodgFileSizeMod89Times150PlusShapeCount850PlusTextCount450:
    def test_empty_returns_11100(self):
        assert fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) == 11100

    def test_minimal_returns_8650(self):
        assert fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL) == 8650

    def test_shapes_returns_7350(self):
        assert fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(SHAPES) == 7350

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) >
                fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450(str(EMPTY)) == 11100
