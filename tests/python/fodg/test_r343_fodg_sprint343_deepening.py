"""Sprint 343 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700,
    fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500,
)


# --- F1: fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700 ---

class TestFodgFileSizeMod359Times2200PlusShape3200PlusText2700:
    def test_empty_returns_737000(self):
        assert fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY) == 737000

    def test_minimal_returns_87300(self):
        assert fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL) == 87300

    def test_shapes_returns_437400(self):
        assert fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(SHAPES) == 437400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY) >
                fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_359_times_2200_plus_shape_count_times_3200_plus_text_count_times_2700(str(EMPTY)) == 737000


# --- F2: fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500 ---

class TestFodgFileSizeMod367Times2250PlusShape3000PlusText2500:
    def test_empty_returns_717750(self):
        assert fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY) == 717750

    def test_minimal_returns_16750(self):
        assert fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL) == 16750

    def test_shapes_returns_374000(self):
        assert fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(SHAPES) == 374000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY) >
                fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_367_times_2250_plus_shape_count_times_3000_plus_text_count_times_2500(str(EMPTY)) == 717750
