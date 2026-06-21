"""Sprint 319 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900,
    fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700,
)


# --- F1: fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900 ---

class TestFodgFileSizeMod263Times1400PlusShape2400PlusText1900:
    def test_empty_returns_1400(self):
        assert fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(EMPTY) == 1400

    def test_minimal_returns_225500(self):
        assert fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL) == 225500

    def test_shapes_returns_81000(self):
        assert fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(SHAPES) == 81000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(MINIMAL) >
                fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_263_times_1400_plus_shape_count_times_2400_plus_text_count_times_1900(str(EMPTY)) == 1400


# --- F2: fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700 ---

class TestFodgFileSizeMod269Times1450PlusShape2200PlusText1700:
    def test_empty_returns_356700(self):
        assert fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY) == 356700

    def test_minimal_returns_189500(self):
        assert fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL) == 189500

    def test_shapes_returns_30300(self):
        assert fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(SHAPES) == 30300

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY) >
                fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_269_times_1450_plus_shape_count_times_2200_plus_text_count_times_1700(str(EMPTY)) == 356700
