"""Sprint 283 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700,
    fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500,
)


# --- F1: fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700 ---

class TestFodgFileSizeMod103Times400PlusShapeCount1100PlusTextCount700:
    def test_empty_returns_9200(self):
        assert fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(EMPTY) == 9200

    def test_minimal_returns_14200(self):
        assert fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL) == 14200

    def test_shapes_returns_37900(self):
        assert fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(SHAPES) == 37900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(SHAPES) >
                fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_103_times_400_plus_shape_count_times_1100_plus_text_count_times_700(str(EMPTY)) == 9200


# --- F2: fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500 ---

class TestFodgFileSizeMod107Times250PlusShapeCount900PlusTextCount500:
    def test_empty_returns_22500(self):
        assert fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(EMPTY) == 22500

    def test_minimal_returns_21900(self):
        assert fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL) == 21900

    def test_shapes_returns_9450(self):
        assert fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(SHAPES) == 9450

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(MINIMAL) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(EMPTY) >
                fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_107_times_250_plus_shape_count_times_900_plus_text_count_times_500(str(EMPTY)) == 22500
