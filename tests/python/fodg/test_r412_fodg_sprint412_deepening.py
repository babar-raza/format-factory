"""Sprint 412 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000,
    fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800,
)


# --- F1: fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000 ---

class TestFodgFileSizeMod661Times4500PlusShape5500PlusText5000:
    def test_empty_returns_1764000(self):
        assert fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY) == 1764000

    def test_mini_returns_690000(self):
        assert fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(MINI) == 690000

    def test_shapes_returns_1403500(self):
        assert fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(SHAPES) == 1403500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(EMPTY) >
                fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_661_times_4500_plus_shape_count_times_5500_plus_text_count_times_5000(str(EMPTY)) == 1764000


# --- F2: fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800 ---

class TestFodgFileSizeMod673Times4550PlusShape5300PlusText4800:
    def test_empty_returns_1729000(self):
        assert fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY) == 1729000

    def test_mini_returns_587950(self):
        assert fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(MINI) == 587950

    def test_shapes_returns_1308600(self):
        assert fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(SHAPES) == 1308600

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(EMPTY) >
                fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_673_times_4550_plus_shape_count_times_5300_plus_text_count_times_4800(str(EMPTY)) == 1729000
