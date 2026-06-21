"""Sprint 322 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000,
    fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800,
)


# --- F1: fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000 ---

class TestFodgFileSizeMod271Times1500PlusShape2500PlusText2000:
    def test_empty_returns_360000(self):
        assert fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY) == 360000

    def test_minimal_returns_181500(self):
        assert fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL) == 181500

    def test_shapes_returns_14500(self):
        assert fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(SHAPES) == 14500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(MINIMAL) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(EMPTY) >
                fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_271_times_1500_plus_shape_count_times_2500_plus_text_count_times_2000(str(EMPTY)) == 360000


# --- F2: fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800 ---

class TestFodgFileSizeMod277Times1550PlusShape2300PlusText1800:
    def test_empty_returns_344100(self):
        assert fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(EMPTY) == 344100

    def test_minimal_returns_140500(self):
        assert fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL) == 140500

    def test_shapes_returns_387150(self):
        assert fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(SHAPES) == 387150

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(SHAPES) >
                fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_277_times_1550_plus_shape_count_times_2300_plus_text_count_times_1800(str(EMPTY)) == 344100
