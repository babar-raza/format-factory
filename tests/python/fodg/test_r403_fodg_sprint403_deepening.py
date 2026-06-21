"""Sprint 403 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINI = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700,
    fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500,
)


# --- F1: fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700 ---

class TestFodgFileSizeMod631Times4200PlusShape5200PlusText4700:
    def test_empty_returns_1772400(self):
        assert fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY) == 1772400

    def test_mini_returns_896100(self):
        assert fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(MINI) == 896100

    def test_shapes_returns_1562200(self):
        assert fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(SHAPES) == 1562200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(EMPTY) >
                fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_631_times_4200_plus_shape_count_times_5200_plus_text_count_times_4700(str(EMPTY)) == 1772400


# --- F2: fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500 ---

class TestFodgFileSizeMod641Times4250PlusShape5000PlusText4500:
    def test_empty_returns_1751000(self):
        assert fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY) == 1751000

    def test_mini_returns_821250(self):
        assert fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(MINI) == 821250

    def test_shapes_returns_1494500(self):
        assert fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(SHAPES) == 1494500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY), int)

    def test_mini_returns_int(self):
        assert isinstance(fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(MINI), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY) >= 0

    def test_mini_nonnegative(self):
        assert fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(MINI) >= 0

    def test_empty_greater_than_mini(self):
        assert (fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(EMPTY) >
                fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(MINI))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_641_times_4250_plus_shape_count_times_5000_plus_text_count_times_4500(str(EMPTY)) == 1751000
