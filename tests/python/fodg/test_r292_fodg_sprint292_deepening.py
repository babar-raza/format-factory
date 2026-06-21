"""Sprint 292 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000,
    fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800,
)


# --- F1: fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000 ---

class TestFodgFileSizeMod137Times450PlusShapeCount1500PlusTextCount1000:
    def test_empty_returns_42300(self):
        assert fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(EMPTY) == 42300

    def test_minimal_returns_48850(self):
        assert fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(MINIMAL) == 48850

    def test_shapes_returns_60950(self):
        assert fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(SHAPES) == 60950

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(SHAPES) >
                fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_137_times_450_plus_shape_count_times_1500_plus_text_count_times_1000(str(EMPTY)) == 42300


# --- F2: fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800 ---

class TestFodgFileSizeMod139Times550PlusShapeCount1200PlusTextCount800:
    def test_empty_returns_44000(self):
        assert fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY) == 44000

    def test_minimal_returns_47650(self):
        assert fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(MINIMAL) == 47650

    def test_shapes_returns_59650(self):
        assert fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(SHAPES) == 59650

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(SHAPES) >
                fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_139_times_550_plus_shape_count_times_1200_plus_text_count_times_800(str(EMPTY)) == 44000
