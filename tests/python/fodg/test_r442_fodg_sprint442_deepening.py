"""Sprint 442 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600,
    fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400,
)


class TestFodgFileSizeMod811Times5500PlusShape5800PlusText5600:
    def test_empty_returns_1331000(self):
        assert fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(EMPTY) == 1331000

    def test_mini_returns_3652400(self):
        assert fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(MINI) == 3652400

    def test_shapes_returns_61600(self):
        assert fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(SHAPES) == 61600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(MINI) >= 0

    def test_empty_greater_than_shapes(self):
        assert (fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(EMPTY) >
                fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_811_times_5500_plus_shape_count_times_5800_plus_text_count_times_5600(str(EMPTY)) == 1331000


class TestFodgFileSizeMod821Times5550PlusShape5600PlusText5400:
    def test_empty_returns_1287600(self):
        assert fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(EMPTY) == 1287600

    def test_mini_returns_3629600(self):
        assert fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(MINI) == 3629600

    def test_shapes_returns_4506450(self):
        assert fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(SHAPES) == 4506450

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(MINI) >
                fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_821_times_5550_plus_shape_count_times_5600_plus_text_count_times_5400(str(EMPTY)) == 1287600
