"""Sprint 295 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100,
    fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900,
)


# --- F1: fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100 ---

class TestFodgFileSizeMod149Times500PlusShapeCount1600PlusTextCount1100:
    def test_empty_returns_5000(self):
        assert fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(EMPTY) == 5000

    def test_minimal_returns_68700(self):
        assert fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(MINIMAL) == 68700

    def test_shapes_returns_76000(self):
        assert fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(SHAPES) == 76000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(SHAPES) >
                fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100(str(EMPTY)) == 5000


# --- F2: fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900 ---

class TestFodgFileSizeMod151Times600PlusShapeCount1300PlusTextCount900:
    def test_empty_returns_88200(self):
        assert fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(EMPTY) == 88200

    def test_minimal_returns_70600(self):
        assert fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(MINIMAL) == 70600

    def test_shapes_returns_76500(self):
        assert fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(SHAPES) == 76500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(MINIMAL) >= 0

    def test_empty_greater_than_minimal(self):
        assert (fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(EMPTY) >
                fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900(str(EMPTY)) == 88200
