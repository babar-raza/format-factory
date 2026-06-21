"""Sprint 307 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500,
    fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300,
)


# --- F1: fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500 ---

class TestFodgFileSizeMod191Times950PlusShapeCount2000PlusTextCount1500:
    def test_empty_returns_93100(self):
        assert fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(EMPTY) == 93100

    def test_minimal_returns_132700(self):
        assert fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(MINIMAL) == 132700

    def test_shapes_returns_104000(self):
        assert fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(SHAPES) == 104000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(MINIMAL) >
                fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500(str(EMPTY)) == 93100


# --- F2: fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300 ---

class TestFodgFileSizeMod193Times1000PlusShapeCount1700PlusTextCount1300:
    def test_empty_returns_88000(self):
        assert fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(EMPTY) == 88000

    def test_minimal_returns_125000(self):
        assert fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(MINIMAL) == 125000

    def test_shapes_returns_91700(self):
        assert fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(SHAPES) == 91700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(MINIMAL) >
                fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300(str(EMPTY)) == 88000
