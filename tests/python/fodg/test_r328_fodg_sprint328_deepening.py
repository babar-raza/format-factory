"""Sprint 328 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200,
    fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000,
)


# --- F1: fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200 ---

class TestFodgFileSizeMod293Times1700PlusShape2700PlusText2200:
    def test_empty_returns_295800(self):
        assert fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY) == 295800

    def test_minimal_returns_18500(self):
        assert fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL) == 18500

    def test_shapes_returns_289600(self):
        assert fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(SHAPES) == 289600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(EMPTY) >
                fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_293_times_1700_plus_shape_count_times_2700_plus_text_count_times_2200(str(EMPTY)) == 295800


# --- F2: fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000 ---

class TestFodgFileSizeMod307Times1750PlusShape2500PlusText2000:
    def test_empty_returns_231000(self):
        assert fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY) == 231000

    def test_minimal_returns_433250(self):
        assert fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL) == 433250

    def test_shapes_returns_174250(self):
        assert fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(SHAPES) == 174250

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL) >
                fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_307_times_1750_plus_shape_count_times_2500_plus_text_count_times_2000(str(EMPTY)) == 231000
