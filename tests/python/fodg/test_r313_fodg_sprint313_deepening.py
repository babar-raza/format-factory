"""Sprint 313 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700,
    fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500,
)


# --- F1: fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700 ---

class TestFodgFileSizeMod227Times1150PlusShapeCount2200PlusTextCount1700:
    def test_empty_returns_166750(self):
        assert fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY) == 166750

    def test_minimal_returns_131550(self):
        assert fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL) == 131550

    def test_shapes_returns_54850(self):
        assert fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(SHAPES) == 54850

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(EMPTY) >
                fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_227_times_1150_plus_shape_count_times_2200_plus_text_count_times_1700(str(EMPTY)) == 166750


# --- F2: fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500 ---

class TestFodgFileSizeMod229Times1200PlusShapeCount1900PlusTextCount1500:
    def test_empty_returns_164400(self):
        assert fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(EMPTY) == 164400

    def test_minimal_returns_122200(self):
        assert fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(MINIMAL) == 122200

    def test_shapes_returns_38700(self):
        assert fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(SHAPES) == 38700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(EMPTY) >
                fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_229_times_1200_plus_shape_count_times_1900_plus_text_count_times_1500(str(EMPTY)) == 164400
