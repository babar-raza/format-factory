"""Sprint 367 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500,
    fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300,
)


# --- F1: fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500 ---

class TestFodgFileSizeMod457Times3000PlusShape4000PlusText3500:
    def test_empty_returns_417000(self):
        assert fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY) == 417000

    def test_minimal_returns_313500(self):
        assert fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(MINIMAL) == 313500

    def test_shapes_returns_790000(self):
        assert fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(SHAPES) == 790000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(SHAPES) >
                fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_457_times_3000_plus_shape_count_times_4000_plus_text_count_times_3500(str(EMPTY)) == 417000


# --- F2: fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300 ---

class TestFodgFileSizeMod461Times3050PlusShape3800PlusText3300:
    def test_empty_returns_399550(self):
        assert fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY) == 399550

    def test_minimal_returns_281600(self):
        assert fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(MINIMAL) == 281600

    def test_shapes_returns_765250(self):
        assert fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(SHAPES) == 765250

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(SHAPES) >
                fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_461_times_3050_plus_shape_count_times_3800_plus_text_count_times_3300(str(EMPTY)) == 399550
