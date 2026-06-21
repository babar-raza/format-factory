"""Sprint 397 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500,
    fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300,
)


# --- F1: fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500 ---

class TestFodgFileSizeMod607Times4000PlusShape5000PlusText4500:
    def test_empty_returns_1784000(self):
        assert fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY) == 1784000

    def test_mini_returns_1045500(self):
        assert fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(MINI) == 1045500

    def test_shapes_returns_1680000(self):
        assert fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(SHAPES) == 1680000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY) >
                fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_607_times_4000_plus_shape_count_times_5000_plus_text_count_times_4500(str(EMPTY)) == 1784000


# --- F2: fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300 ---

class TestFodgFileSizeMod613Times4050PlusShape4800PlusText4300:
    def test_empty_returns_1782000(self):
        assert fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY) == 1782000

    def test_mini_returns_1009450(self):
        assert fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(MINI) == 1009450

    def test_shapes_returns_1651100(self):
        assert fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(SHAPES) == 1651100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY) >
                fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_613_times_4050_plus_shape_count_times_4800_plus_text_count_times_4300(str(EMPTY)) == 1782000
