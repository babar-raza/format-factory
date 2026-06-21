"""Sprint 427 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500,
    fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300,
)


# --- F1: fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500 ---

class TestFodgFileSizeMod739Times5000PlusShape6000PlusText5500:
    def test_empty_returns_1570000(self):
        assert fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY) == 1570000

    def test_mini_returns_3681500(self):
        assert fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(MINI) == 3681500

    def test_shapes_returns_779000(self):
        assert fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(SHAPES) == 779000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY) >
                fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_739_times_5000_plus_shape_count_times_6000_plus_text_count_times_5500(str(EMPTY)) == 1570000


# --- F2: fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300 ---

class TestFodgFileSizeMod743Times5050PlusShape5800PlusText5300:
    def test_empty_returns_1565500(self):
        assert fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY) == 1565500

    def test_mini_returns_3697600(self):
        assert fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(MINI) == 3697600

    def test_shapes_returns_745100(self):
        assert fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(SHAPES) == 745100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY) >
                fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_743_times_5050_plus_shape_count_times_5800_plus_text_count_times_5300(str(EMPTY)) == 1565500
