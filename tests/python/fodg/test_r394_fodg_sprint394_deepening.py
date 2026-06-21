"""Sprint 394 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400,
    fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200,
)


# --- F1: fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400 ---

class TestFodgFileSizeMod599Times3900PlusShape4900PlusText4400:
    def test_empty_returns_1770600(self):
        assert fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY) == 1770600

    def test_mini_returns_1081800(self):
        assert fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(MINI) == 1081800

    def test_shapes_returns_1700500(self):
        assert fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(SHAPES) == 1700500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(EMPTY) >
                fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_599_times_3900_plus_shape_count_times_4900_plus_text_count_times_4400(str(EMPTY)) == 1770600


# --- F2: fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200 ---

class TestFodgFileSizeMod601Times3950PlusShape4700PlusText4200:
    def test_empty_returns_1785400(self):
        assert fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY) == 1785400

    def test_mini_returns_1079350(self):
        assert fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(MINI) == 1079350

    def test_shapes_returns_1705200(self):
        assert fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(SHAPES) == 1705200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(EMPTY) >
                fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_601_times_3950_plus_shape_count_times_4700_plus_text_count_times_4200(str(EMPTY)) == 1785400
