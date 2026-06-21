"""Sprint 298 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200,
    fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000,
)


# --- F1: fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200 ---

class TestFodgFileSizeMod157Times650PlusShapeCount1700PlusTextCount1200:
    def test_empty_returns_72150(self):
        assert fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(EMPTY) == 72150

    def test_minimal_returns_41900(self):
        assert fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(MINIMAL) == 41900

    def test_shapes_returns_45200(self):
        assert fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(SHAPES) == 45200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(EMPTY) >
                fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200(str(EMPTY)) == 72150


# --- F2: fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000 ---

class TestFodgFileSizeMod163Times700PlusShapeCount1400PlusTextCount1000:
    def test_empty_returns_52500(self):
        assert fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(EMPTY) == 52500

    def test_minimal_returns_6600(self):
        assert fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(MINIMAL) == 6600

    def test_shapes_returns_118900(self):
        assert fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(SHAPES) == 118900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(SHAPES) >
                fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000(str(EMPTY)) == 52500
