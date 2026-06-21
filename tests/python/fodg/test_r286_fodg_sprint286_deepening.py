"""Sprint 286 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800,
    fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600,
)


# --- F1: fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800 ---

class TestFodgFileSizeMod109Times450PlusShapeCount1200PlusTextCount800:
    def test_empty_returns_32400(self):
        assert fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY) == 32400

    def test_minimal_returns_27200(self):
        assert fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(MINIMAL) == 27200

    def test_shapes_returns_51100(self):
        assert fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(SHAPES) == 51100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(SHAPES) >
                fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_109_times_450_plus_shape_count_times_1200_plus_text_count_times_800(str(EMPTY)) == 32400


# --- F2: fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600 ---

class TestFodgFileSizeMod113Times350PlusShapeCount1000PlusTextCount600:
    def test_empty_returns_12600(self):
        assert fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY) == 12600

    def test_minimal_returns_3000(self):
        assert fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL) == 3000

    def test_shapes_returns_20300(self):
        assert fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES) == 20300

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES) >
                fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_113_times_350_plus_shape_count_times_1000_plus_text_count_times_600(str(EMPTY)) == 12600
