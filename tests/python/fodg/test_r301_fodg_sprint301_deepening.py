"""Sprint 301 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300,
    fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100,
)


# --- F1: fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300 ---

class TestFodgFileSizeMod167Times750PlusShapeCount1800PlusTextCount1300:
    def test_empty_returns_38250(self):
        assert fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(EMPTY) == 38250

    def test_minimal_returns_105850(self):
        assert fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(MINIMAL) == 105850

    def test_shapes_returns_101750(self):
        assert fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(SHAPES) == 101750

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(MINIMAL) >
                fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_167_times_750_plus_shape_count_times_1800_plus_text_count_times_1300(str(EMPTY)) == 38250


# --- F2: fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100 ---

class TestFodgFileSizeMod173Times800PlusShapeCount1500PlusTextCount1100:
    def test_empty_returns_12000(self):
        assert fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(EMPTY) == 12000

    def test_minimal_returns_73800(self):
        assert fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(MINIMAL) == 73800

    def test_shapes_returns_63500(self):
        assert fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(SHAPES) == 63500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(MINIMAL) >
                fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_173_times_800_plus_shape_count_times_1500_plus_text_count_times_1100(str(EMPTY)) == 12000
