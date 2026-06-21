"""Sprint 316 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800,
    fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600,
)


# --- F1: fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800 ---

class TestFodgFileSizeMod239Times1250PlusShape2300PlusText1800:
    def test_empty_returns_121250(self):
        assert fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(EMPTY) == 121250

    def test_minimal_returns_52850(self):
        assert fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL) == 52850

    def test_shapes_returns_253000(self):
        assert fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(SHAPES) == 253000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(SHAPES) >
                fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_239_times_1250_plus_shape_count_times_2300_plus_text_count_times_1800(str(EMPTY)) == 121250


# --- F2: fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600 ---

class TestFodgFileSizeMod257Times1350PlusShape2100PlusText1600:
    def test_empty_returns_33750(self):
        assert fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(EMPTY) == 33750

    def test_minimal_returns_257500(self):
        assert fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL) == 257500

    def test_shapes_returns_125600(self):
        assert fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(SHAPES) == 125600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(MINIMAL) >
                fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_257_times_1350_plus_shape_count_times_2100_plus_text_count_times_1600(str(EMPTY)) == 33750
