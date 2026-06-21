"""Sprint 361 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300,
    fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100,
)


# --- F1: fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300 ---

class TestFodgFileSizeMod433Times2800PlusShape3800PlusText3300:
    def test_empty_returns_523600(self):
        assert fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY) == 523600

    def test_minimal_returns_494300(self):
        assert fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(MINIMAL) == 494300

    def test_shapes_returns_939200(self):
        assert fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(SHAPES) == 939200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(SHAPES) >
                fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_433_times_2800_plus_shape_count_times_3800_plus_text_count_times_3300(str(EMPTY)) == 523600


# --- F2: fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100 ---

class TestFodgFileSizeMod439Times2850PlusShape3600PlusText3100:
    def test_empty_returns_498750(self):
        assert fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY) == 498750

    def test_minimal_returns_451300(self):
        assert fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(MINIMAL) == 451300

    def test_shapes_returns_903350(self):
        assert fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(SHAPES) == 903350

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(SHAPES) >
                fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_439_times_2850_plus_shape_count_times_3600_plus_text_count_times_3100(str(EMPTY)) == 498750
