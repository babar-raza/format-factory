"""Sprint 433 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700,
    fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500,
)


class TestFodgFileSizeMod761Times5200PlusShape6200PlusText5700:
    def test_empty_returns_1518400(self):
        assert fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(EMPTY) == 1518400

    def test_mini_returns_3714300(self):
        assert fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(MINI) == 3714300

    def test_shapes_returns_581200(self):
        assert fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(SHAPES) == 581200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(EMPTY) >
                fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_761_times_5200_plus_shape_count_times_6200_plus_text_count_times_5700(str(EMPTY)) == 1518400


class TestFodgFileSizeMod769Times5250PlusShape6000PlusText5500:
    def test_empty_returns_1491000(self):
        assert fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY) == 1491000

    def test_mini_returns_3707500(self):
        assert fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(MINI) == 3707500

    def test_shapes_returns_501500(self):
        assert fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(SHAPES) == 501500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(EMPTY) >
                fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_769_times_5250_plus_shape_count_times_6000_plus_text_count_times_5500(str(EMPTY)) == 1491000
