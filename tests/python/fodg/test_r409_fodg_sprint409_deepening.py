"""Sprint 409 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900,
    fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700,
)


# --- F1: fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900 ---

class TestFodgFileSizeMod653Times4400PlusShape5400PlusText4900:
    def test_empty_returns_1760000(self):
        assert fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY) == 1760000

    def test_mini_returns_745100(self):
        assert fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(MINI) == 745100

    def test_shapes_returns_1442800(self):
        assert fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(SHAPES) == 1442800

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(EMPTY) >
                fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_653_times_4400_plus_shape_count_times_5400_plus_text_count_times_4900(str(EMPTY)) == 1760000


# --- F2: fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700 ---

class TestFodgFileSizeMod659Times4450PlusShape5200PlusText4700:
    def test_empty_returns_1753300(self):
        assert fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY) == 1753300

    def test_mini_returns_699650(self):
        assert fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(MINI) == 699650

    def test_shapes_returns_1404500(self):
        assert fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(SHAPES) == 1404500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY) >
                fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_659_times_4450_plus_shape_count_times_5200_plus_text_count_times_4700(str(EMPTY)) == 1753300
