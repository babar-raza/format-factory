"""Sprint 355 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100,
    fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900,
)


# --- F1: fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100 ---

class TestFodgFileSizeMod409Times2600PlusShape3600PlusText3100:
    def test_empty_returns_611000(self):
        assert fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY) == 611000

    def test_minimal_returns_646300(self):
        assert fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(MINIMAL) == 646300

    def test_shapes_returns_1059600(self):
        assert fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(SHAPES) == 1059600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(SHAPES) >
                fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_409_times_2600_plus_shape_count_times_3600_plus_text_count_times_3100(str(EMPTY)) == 611000


# --- F2: fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900 ---

class TestFodgFileSizeMod419Times2650PlusShape3400PlusText2900:
    def test_empty_returns_569750(self):
        assert fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY) == 569750

    def test_minimal_returns_578700(self):
        assert fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL) == 578700

    def test_shapes_returns_999150(self):
        assert fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(SHAPES) == 999150

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(SHAPES) >
                fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_419_times_2650_plus_shape_count_times_3400_plus_text_count_times_2900(str(EMPTY)) == 569750
