"""Sprint 358 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200,
    fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000,
)


# --- F1: fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200 ---

class TestFodgFileSizeMod421Times2700PlusShape3700PlusText3200:
    def test_empty_returns_569700(self):
        assert fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY) == 569700

    def test_minimal_returns_573900(self):
        assert fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(MINIMAL) == 573900

    def test_shapes_returns_1003000(self):
        assert fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(SHAPES) == 1003000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(SHAPES) >
                fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_421_times_2700_plus_shape_count_times_3700_plus_text_count_times_3200(str(EMPTY)) == 569700


# --- F2: fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000 ---

class TestFodgFileSizeMod431Times2750PlusShape3500PlusText3000:
    def test_empty_returns_525250(self):
        assert fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY) == 525250

    def test_minimal_returns_501500(self):
        assert fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL) == 501500

    def test_shapes_returns_937750(self):
        assert fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(SHAPES) == 937750

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(SHAPES) >
                fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_431_times_2750_plus_shape_count_times_3500_plus_text_count_times_3000(str(EMPTY)) == 525250
