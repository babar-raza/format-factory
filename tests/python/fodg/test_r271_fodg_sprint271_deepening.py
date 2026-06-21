"""Sprint 271 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450,
    fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550,
)


# --- F1: fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450 ---

class TestFodgFileSizeMod47Times150PlusShapeCount850PlusTextCount450:
    def test_empty_returns_2850(self):
        assert fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) == 2850

    def test_minimal_returns_3700(self):
        assert fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL) == 3700

    def test_shapes_returns_7950(self):
        assert fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(SHAPES) == 7950

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(SHAPES) >
                fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450(str(EMPTY)) == 2850


# --- F2: fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550 ---

class TestFodgFileSizeMod59Times200PlusShapeCount950PlusTextCount550:
    def test_empty_returns_10000(self):
        assert fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY) == 10000

    def test_minimal_returns_12900(self):
        assert fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL) == 12900

    def test_shapes_returns_10950(self):
        assert fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(SHAPES) == 10950

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL) >
                fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550(str(EMPTY)) == 10000
