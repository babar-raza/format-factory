"""Sprint 274 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650,
    fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350,
)


# --- F1: fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650 ---

class TestFodgFileSizeMod61Times250PlusShapeCount1050PlusTextCount650:
    def test_empty_returns_4000(self):
        assert fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(EMPTY) == 4000

    def test_minimal_returns_3950(self):
        assert fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(MINIMAL) == 3950

    def test_shapes_returns_14950(self):
        assert fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(SHAPES) == 14950

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(SHAPES) >
                fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_61_times_250_plus_shape_count_times_1050_plus_text_count_times_650(str(EMPTY)) == 4000


# --- F2: fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350 ---

class TestFodgFileSizeMod71Times100PlusShapeCount750PlusTextCount350:
    def test_empty_returns_5900(self):
        assert fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY) == 5900

    def test_minimal_returns_6400(self):
        assert fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(MINIMAL) == 6400

    def test_shapes_returns_9550(self):
        assert fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES) == 9550

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(SHAPES) >
                fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_71_times_100_plus_shape_count_times_750_plus_text_count_times_350(str(EMPTY)) == 5900
