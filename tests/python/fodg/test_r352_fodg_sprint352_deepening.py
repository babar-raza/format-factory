"""Sprint 352 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000,
    fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800,
)


# --- F1: fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000 ---

class TestFodgFileSizeMod397Times2500PlusShape3500PlusText3000:
    def test_empty_returns_647500(self):
        assert fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY) == 647500

    def test_minimal_returns_711500(self):
        assert fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL) == 711500

    def test_shapes_returns_116500(self):
        assert fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(SHAPES) == 116500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(MINIMAL) >
                fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_397_times_2500_plus_shape_count_times_3500_plus_text_count_times_3000(str(EMPTY)) == 647500


# --- F2: fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800 ---

class TestFodgFileSizeMod401Times2550PlusShape3300PlusText2800:
    def test_empty_returns_640050(self):
        assert fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(EMPTY) == 640050

    def test_minimal_returns_694600(self):
        assert fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL) == 694600

    def test_shapes_returns_76700(self):
        assert fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(SHAPES) == 76700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL) >
                fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_401_times_2550_plus_shape_count_times_3300_plus_text_count_times_2800(str(EMPTY)) == 640050
