"""Sprint 346 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800,
    fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600,
)


# --- F1: fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800 ---

class TestFodgFileSizeMod373Times2300PlusShape3300PlusText2800:
    def test_empty_returns_706100(self):
        assert fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(EMPTY) == 706100

    def test_minimal_returns_820300(self):
        assert fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL) == 820300

    def test_shapes_returns_328300(self):
        assert fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(SHAPES) == 328300

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(MINIMAL) >
                fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_373_times_2300_plus_shape_count_times_3300_plus_text_count_times_2800(str(EMPTY)) == 706100


# --- F2: fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600 ---

class TestFodgFileSizeMod379Times2350PlusShape3100PlusText2600:
    def test_empty_returns_693250(self):
        assert fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(EMPTY) == 693250

    def test_minimal_returns_795300(self):
        assert fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL) == 795300

    def test_shapes_returns_277700(self):
        assert fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(SHAPES) == 277700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL) >
                fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_379_times_2350_plus_shape_count_times_3100_plus_text_count_times_2600(str(EMPTY)) == 693250
