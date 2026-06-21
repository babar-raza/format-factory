"""Sprint 289 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900,
    fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700,
)


# --- F1: fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900 ---

class TestFodgFileSizeMod127Times400PlusShapeCount1400PlusTextCount900:
    def test_empty_returns_14800(self):
        assert fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(EMPTY) == 14800

    def test_minimal_returns_32700(self):
        assert fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(MINIMAL) == 32700

    def test_shapes_returns_47600(self):
        assert fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(SHAPES) == 47600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(SHAPES) >
                fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_127_times_400_plus_shape_count_times_1400_plus_text_count_times_900(str(EMPTY)) == 14800


# --- F2: fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700 ---

class TestFodgFileSizeMod131Times500PlusShapeCount1100PlusTextCount700:
    def test_empty_returns_2500(self):
        assert fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(EMPTY) == 2500

    def test_minimal_returns_17800(self):
        assert fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL) == 17800

    def test_shapes_returns_32700(self):
        assert fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(SHAPES) == 32700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(SHAPES) >
                fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_131_times_500_plus_shape_count_times_1100_plus_text_count_times_700(str(EMPTY)) == 2500
