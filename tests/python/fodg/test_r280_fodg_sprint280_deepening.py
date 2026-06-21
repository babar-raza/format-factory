"""Sprint 280 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550,
    fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250,
)


# --- F1: fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550 ---

class TestFodgFileSizeMod97Times200PlusShapeCount950PlusTextCount550:
    def test_empty_returns_16600(self):
        assert fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY) == 16600

    def test_minimal_returns_5100(self):
        assert fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL) == 5100

    def test_shapes_returns_19150(self):
        assert fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(SHAPES) == 19150

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(SHAPES) >
                fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550(str(EMPTY)) == 16600


# --- F2: fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250 ---

class TestFodgFileSizeMod101Times300PlusShapeCount650PlusTextCount250:
    def test_empty_returns_12900(self):
        assert fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(EMPTY) == 12900

    def test_minimal_returns_18600(self):
        assert fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(MINIMAL) == 18600

    def test_shapes_returns_6050(self):
        assert fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(SHAPES) == 6050

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(MINIMAL) >= 0

    def test_minimal_greater_than_empty(self):
        assert (fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(MINIMAL) >
                fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250(str(EMPTY)) == 12900
