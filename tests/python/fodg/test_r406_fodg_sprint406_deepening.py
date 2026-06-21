"""Sprint 406 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800,
    fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600,
)


# --- F1: fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800 ---

class TestFodgFileSizeMod643Times4300PlusShape5300PlusText4800:
    def test_empty_returns_1763000(self):
        assert fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY) == 1763000

    def test_mini_returns_814200(self):
        assert fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(MINI) == 814200

    def test_shapes_returns_1496100(self):
        assert fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(SHAPES) == 1496100

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY) >
                fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_643_times_4300_plus_shape_count_times_5300_plus_text_count_times_4800(str(EMPTY)) == 1763000


# --- F2: fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600 ---

class TestFodgFileSizeMod647Times4350PlusShape5100PlusText4600:
    def test_empty_returns_1766100(self):
        assert fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY) == 1766100

    def test_mini_returns_788350(self):
        assert fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(MINI) == 788350

    def test_shapes_returns_1477400(self):
        assert fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(SHAPES) == 1477400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(EMPTY) >
                fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_647_times_4350_plus_shape_count_times_5100_plus_text_count_times_4600(str(EMPTY)) == 1766100
