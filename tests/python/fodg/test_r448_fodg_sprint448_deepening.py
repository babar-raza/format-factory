"""Sprint 448 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800,
    fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600,
)


class TestFodgFileSizeMod829Times5700PlusShape5000PlusText4800:
    def test_empty_returns_1276800(self):
        assert fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(EMPTY) == 1276800

    def test_mini_returns_3680600(self):
        assert fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(MINI) == 3680600

    def test_shapes_returns_4578900(self):
        assert fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(SHAPES) == 4578900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(MINI) >
                fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_829_times_5700_plus_shape_count_times_5000_plus_text_count_times_4800(str(EMPTY)) == 1276800


class TestFodgFileSizeMod839Times5750PlusShape4800PlusText4600:
    def test_empty_returns_1230500(self):
        assert fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(EMPTY) == 1230500

    def test_mini_returns_3654900(self):
        assert fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(MINI) == 3654900

    def test_shapes_returns_4560350(self):
        assert fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(SHAPES) == 4560350

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(MINI) >= 0

    def test_mini_greater_than_empty(self):
        assert (fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(MINI) >
                fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_839_times_5750_plus_shape_count_times_4800_plus_text_count_times_4600(str(EMPTY)) == 1230500
