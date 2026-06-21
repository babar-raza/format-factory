"""Sprint 391 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300,
    fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100,
)


# --- F1: fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300 ---

class TestFodgFileSizeMod587Times3800PlusShape4800PlusText4300:
    def test_empty_returns_1770800(self):
        assert fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY) == 1770800

    def test_mini_returns_1145300(self):
        assert fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(MINI) == 1145300

    def test_shapes_returns_1748200(self):
        assert fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(SHAPES) == 1748200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(EMPTY) >
                fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_587_times_3800_plus_shape_count_times_4800_plus_text_count_times_4300(str(EMPTY)) == 1770800


# --- F2: fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100 ---

class TestFodgFileSizeMod593Times3850PlusShape4600PlusText4100:
    def test_empty_returns_1771000(self):
        assert fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY) == 1771000

    def test_mini_returns_1113650(self):
        assert fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(MINI) == 1113650

    def test_shapes_returns_1723700(self):
        assert fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(SHAPES) == 1723700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY) >
                fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_593_times_3850_plus_shape_count_times_4600_plus_text_count_times_4100(str(EMPTY)) == 1771000
