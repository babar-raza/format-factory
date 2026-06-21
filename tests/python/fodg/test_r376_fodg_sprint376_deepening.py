"""Sprint 376 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800,
    fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600,
)


# --- F1: fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800 ---

class TestFodgFileSizeMod491Times3300PlusShape4300PlusText3800:
    def test_empty_returns_234300(self):
        assert fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY) == 234300

    def test_minimal_returns_8100(self):
        assert fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(MINIMAL) == 8100

    def test_shapes_returns_532000(self):
        assert fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(SHAPES) == 532000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(SHAPES) >
                fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_491_times_3300_plus_shape_count_times_4300_plus_text_count_times_3800(str(EMPTY)) == 234300


# --- F2: fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600 ---

class TestFodgFileSizeMod499Times3350PlusShape4100PlusText3600:
    def test_empty_returns_184250(self):
        assert fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY) == 184250

    def test_minimal_returns_1598950(self):
        assert fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(MINIMAL) == 1598950

    def test_shapes_returns_458350(self):
        assert fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(SHAPES) == 458350

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(SHAPES) >
                fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_499_times_3350_plus_shape_count_times_4100_plus_text_count_times_3600(str(EMPTY)) == 184250
