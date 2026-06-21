"""Sprint 373 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700,
    fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500,
)


# --- F1: fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700 ---

class TestFodgFileSizeMod479Times3200PlusShape4200PlusText3700:
    def test_empty_returns_304000(self):
        assert fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY) == 304000

    def test_minimal_returns_123100(self):
        assert fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(MINIMAL) == 123100

    def test_shapes_returns_631200(self):
        assert fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(SHAPES) == 631200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(SHAPES) >
                fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_479_times_3200_plus_shape_count_times_4200_plus_text_count_times_3700(str(EMPTY)) == 304000


# --- F2: fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500 ---

class TestFodgFileSizeMod487Times3250PlusShape4000PlusText3500:
    def test_empty_returns_256750(self):
        assert fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY) == 256750

    def test_minimal_returns_46500(self):
        assert fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(MINIMAL) == 46500

    def test_shapes_returns_561750(self):
        assert fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(SHAPES) == 561750

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(SHAPES) >
                fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_487_times_3250_plus_shape_count_times_4000_plus_text_count_times_3500(str(EMPTY)) == 256750
