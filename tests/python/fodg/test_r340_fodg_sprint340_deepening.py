"""Sprint 340 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600,
    fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400,
)


# --- F1: fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600 ---

class TestFodgFileSizeMod349Times2100PlusShape3100PlusText2600:
    def test_empty_returns_12600(self):
        assert fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(EMPTY) == 12600

    def test_minimal_returns_167400(self):
        assert fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL) == 167400

    def test_shapes_returns_501700(self):
        assert fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(SHAPES) == 501700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(SHAPES) >
                fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_349_times_2100_plus_shape_count_times_3100_plus_text_count_times_2600(str(EMPTY)) == 12600


# --- F2: fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400 ---

class TestFodgFileSizeMod353Times2150PlusShape2900PlusText2400:
    def test_empty_returns_746050(self):
        assert fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY) == 746050

    def test_minimal_returns_136450(self):
        assert fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL) == 136450

    def test_shapes_returns_477900(self):
        assert fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(SHAPES) == 477900

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(EMPTY) >
                fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_353_times_2150_plus_shape_count_times_2900_plus_text_count_times_2400(str(EMPTY)) == 746050
