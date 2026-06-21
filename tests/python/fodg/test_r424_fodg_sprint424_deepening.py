"""Sprint 424 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400,
    fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200,
)


# --- F1: fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400 ---

class TestFodgFileSizeMod727Times4900PlusShape5900PlusText5400:
    def test_empty_returns_1597400(self):
        assert fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY) == 1597400

    def test_mini_returns_104400(self):
        assert fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(MINI) == 104400

    def test_shapes_returns_881100(self):
        assert fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(SHAPES) == 881100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(EMPTY) >
                fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_727_times_4900_plus_shape_count_times_5900_plus_text_count_times_5400(str(EMPTY)) == 1597400


# --- F2: fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200 ---

class TestFodgFileSizeMod733Times4950PlusShape5700PlusText5200:
    def test_empty_returns_1584000(self):
        assert fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY) == 1584000

    def test_mini_returns_45550(self):
        assert fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(MINI) == 45550

    def test_shapes_returns_829400(self):
        assert fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(SHAPES) == 829400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(EMPTY) >
                fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_733_times_4950_plus_shape_count_times_5700_plus_text_count_times_5200(str(EMPTY)) == 1584000
