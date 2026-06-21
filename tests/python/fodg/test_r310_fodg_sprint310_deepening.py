"""Sprint 310 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600,
    fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400,
)


# --- F1: fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600 ---

class TestFodgFileSizeMod211Times1050PlusShapeCount2100PlusTextCount1600:
    def test_empty_returns_219450(self):
        assert fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(EMPTY) == 219450

    def test_minimal_returns_221050(self):
        assert fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL) == 221050

    def test_shapes_returns_168050(self):
        assert fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(SHAPES) == 168050

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL) >
                fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_211_times_1050_plus_shape_count_times_2100_plus_text_count_times_1600(str(EMPTY)) == 219450


# --- F2: fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400 ---

class TestFodgFileSizeMod223Times1100PlusShapeCount1800PlusTextCount1400:
    def test_empty_returns_177100(self):
        assert fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(EMPTY) == 177100

    def test_minimal_returns_151700(self):
        assert fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(MINIMAL) == 151700

    def test_shapes_returns_81900(self):
        assert fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(SHAPES) == 81900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(EMPTY) >
                fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_223_times_1100_plus_shape_count_times_1800_plus_text_count_times_1400(str(EMPTY)) == 177100
