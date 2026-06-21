"""Sprint 304 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400,
    fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200,
)


# --- F1: fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400 ---

class TestFodgFileSizeMod179Times850PlusShapeCount1900PlusTextCount1400:
    def test_empty_returns_134300(self):
        assert fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(EMPTY) == 134300

    def test_minimal_returns_38150(self):
        assert fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(MINIMAL) == 38150

    def test_shapes_returns_22950(self):
        assert fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(SHAPES) == 22950

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(EMPTY) >
                fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_179_times_850_plus_shape_count_times_1900_plus_text_count_times_1400(str(EMPTY)) == 134300


# --- F2: fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200 ---

class TestFodgFileSizeMod181Times900PlusShapeCount1600PlusTextCount1200:
    def test_empty_returns_133200(self):
        assert fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(EMPTY) == 133200

    def test_minimal_returns_25300(self):
        assert fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(MINIMAL) == 25300

    def test_shapes_returns_169200(self):
        assert fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(SHAPES) == 169200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(SHAPES) >
                fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_181_times_900_plus_shape_count_times_1600_plus_text_count_times_1200(str(EMPTY)) == 133200
