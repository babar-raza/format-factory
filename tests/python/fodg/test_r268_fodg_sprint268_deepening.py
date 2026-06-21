"""Sprint 268 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300,
    fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600,
)


# --- F1: fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300 ---

class TestFodgFileSizeMod37Times200PlusShapeCount700PlusTextCount300:
    def test_empty_returns_3400(self):
        assert fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(EMPTY) == 3400

    def test_minimal_returns_7000(self):
        assert fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(MINIMAL) == 7000

    def test_shapes_returns_2700(self):
        assert fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(SHAPES) == 2700

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(MINIMAL) >= 0

    def test_minimal_greater_than_shapes(self):
        assert (fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(MINIMAL) >
                fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(SHAPES))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_37_times_200_plus_shape_count_times_700_plus_text_count_times_300(str(EMPTY)) == 3400


# --- F2: fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600 ---

class TestFodgFileSizeMod53Times100PlusShapeCount1000PlusTextCount600:
    def test_empty_returns_4600(self):
        assert fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY) == 4600

    def test_minimal_returns_5800(self):
        assert fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL) == 5800

    def test_shapes_returns_8000(self):
        assert fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES) == 8000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES) >
                fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_53_times_100_plus_shape_count_times_1000_plus_text_count_times_600(str(EMPTY)) == 4600
