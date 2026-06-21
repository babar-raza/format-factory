"""Sprint 421 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300,
    fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100,
)


# --- F1: fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300 ---

class TestFodgFileSizeMod709Times4800PlusShape5800PlusText5300:
    def test_empty_returns_1651200(self):
        assert fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY) == 1651200

    def test_mini_returns_275100(self):
        assert fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(MINI) == 275100

    def test_shapes_returns_1036000(self):
        assert fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(SHAPES) == 1036000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(EMPTY) >
                fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_709_times_4800_plus_shape_count_times_5800_plus_text_count_times_5300(str(EMPTY)) == 1651200


# --- F2: fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100 ---

class TestFodgFileSizeMod719Times4850PlusShape5600PlusText5100:
    def test_empty_returns_1619900(self):
        assert fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY) == 1619900

    def test_mini_returns_180450(self):
        assert fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(MINI) == 180450

    def test_shapes_returns_948500(self):
        assert fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(SHAPES) == 948500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(EMPTY) >
                fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_719_times_4850_plus_shape_count_times_5600_plus_text_count_times_5100(str(EMPTY)) == 1619900
