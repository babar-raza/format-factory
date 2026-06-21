"""Sprint 388 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200,
    fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000,
)


# --- F1: fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200 ---

class TestFodgFileSizeMod571Times3700PlusShape4700PlusText4200:
    def test_empty_returns_1783400(self):
        assert fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY) == 1783400

    def test_minimal_returns_1233600(self):
        assert fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(MINIMAL) == 1233600

    def test_shapes_returns_1820700(self):
        assert fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(SHAPES) == 1820700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(SHAPES) >
                fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_571_times_3700_plus_shape_count_times_4700_plus_text_count_times_4200(str(EMPTY)) == 1783400


# --- F2: fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000 ---

class TestFodgFileSizeMod577Times3750PlusShape4500PlusText4000:
    def test_empty_returns_1785000(self):
        assert fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY) == 1785000

    def test_minimal_returns_1204750(self):
        assert fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(MINIMAL) == 1204750

    def test_shapes_returns_1799000(self):
        assert fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(SHAPES) == 1799000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(SHAPES) >
                fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_577_times_3750_plus_shape_count_times_4500_plus_text_count_times_4000(str(EMPTY)) == 1785000
