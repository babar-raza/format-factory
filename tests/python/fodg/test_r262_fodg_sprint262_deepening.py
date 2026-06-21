"""Sprint 262 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400,
    fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350,
)


# --- F1: fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400 ---

class TestFodgFileSizeMod31Times150PlusShapeCount800PlusTextCount400:
    def test_empty_returns_4500(self):
        assert fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(EMPTY) == 4500

    def test_minimal_returns_3600(self):
        assert fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(MINIMAL) == 3600

    def test_shapes_returns_5600(self):
        assert fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(SHAPES) == 5600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(SHAPES) >
                fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_31_times_150_plus_shape_count_times_800_plus_text_count_times_400(str(EMPTY)) == 4500


# --- F2: fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350 ---

class TestFodgFileSizeMod17Times250PlusShapeCount500PlusTextCount350:
    def test_empty_returns_4000(self):
        assert fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(EMPTY) == 4000

    def test_minimal_returns_3600(self):
        assert fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL) == 3600

    def test_shapes_returns_5450(self):
        assert fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(SHAPES) == 5450

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(SHAPES) >
                fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_17_times_250_plus_shape_count_times_500_plus_text_count_times_350(str(EMPTY)) == 4000
