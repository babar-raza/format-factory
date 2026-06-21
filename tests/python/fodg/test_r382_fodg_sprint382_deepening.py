"""Sprint 382 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000,
    fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800,
)


# --- F1: fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000 ---

class TestFodgFileSizeMod547Times3500PlusShape4500PlusText4000:
    def test_empty_returns_1771000(self):
        assert fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY) == 1771000

    def test_minimal_returns_1335000(self):
        assert fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(MINIMAL) == 1335000

    def test_shapes_returns_1890500(self):
        assert fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(SHAPES) == 1890500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(SHAPES) >
                fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_547_times_3500_plus_shape_count_times_4500_plus_text_count_times_4000(str(EMPTY)) == 1771000


# --- F2: fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800 ---

class TestFodgFileSizeMod557Times3550PlusShape4300PlusText3800:
    def test_empty_returns_1760800(self):
        assert fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY) == 1760800

    def test_minimal_returns_1282550(self):
        assert fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(MINIMAL) == 1282550

    def test_shapes_returns_1845200(self):
        assert fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(SHAPES) == 1845200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(SHAPES) >
                fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_557_times_3550_plus_shape_count_times_4300_plus_text_count_times_3800(str(EMPTY)) == 1760800
