"""Sprint 370 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600,
    fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400,
)


# --- F1: fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600 ---

class TestFodgFileSizeMod463Times3100PlusShape4100PlusText3600:
    def test_empty_returns_393700(self):
        assert fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY) == 393700

    def test_minimal_returns_268100(self):
        assert fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(MINIMAL) == 268100

    def test_shapes_returns_760400(self):
        assert fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(SHAPES) == 760400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(SHAPES) >
                fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_463_times_3100_plus_shape_count_times_4100_plus_text_count_times_3600(str(EMPTY)) == 393700


# --- F2: fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400 ---

class TestFodgFileSizeMod467Times3150PlusShape3900PlusText3400:
    def test_empty_returns_374850(self):
        assert fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY) == 374850

    def test_minimal_returns_234100(self):
        assert fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(MINIMAL) == 234100

    def test_shapes_returns_733550(self):
        assert fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(SHAPES) == 733550

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(SHAPES) >
                fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_467_times_3150_plus_shape_count_times_3900_plus_text_count_times_3400(str(EMPTY)) == 374850
