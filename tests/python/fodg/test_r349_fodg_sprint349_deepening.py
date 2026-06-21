"""Sprint 349 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900,
    fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700,
)


# --- F1: fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900 ---

class TestFodgFileSizeMod383Times2400PlusShape3400PlusText2900:
    def test_empty_returns_688800(self):
        assert fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY) == 688800

    def test_minimal_returns_783900(self):
        assert fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL) == 783900

    def test_shapes_returns_246400(self):
        assert fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(SHAPES) == 246400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(MINIMAL) >
                fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_383_times_2400_plus_shape_count_times_3400_plus_text_count_times_2900(str(EMPTY)) == 688800


# --- F2: fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700 ---

class TestFodgFileSizeMod389Times2450PlusShape3200PlusText2700:
    def test_empty_returns_673750(self):
        assert fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY) == 673750

    def test_minimal_returns_755600(self):
        assert fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL) == 755600

    def test_shapes_returns_191400(self):
        assert fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(SHAPES) == 191400

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(MINIMAL) >
                fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_389_times_2450_plus_shape_count_times_3200_plus_text_count_times_2700(str(EMPTY)) == 673750
