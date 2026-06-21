"""Sprint 337 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500,
    fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300,
)


# --- F1: fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500 ---

class TestFodgFileSizeMod337Times2000PlusShape3000PlusText2500:
    def test_empty_returns_84000(self):
        assert fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY) == 84000

    def test_minimal_returns_255500(self):
        assert fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL) == 255500

    def test_shapes_returns_574000(self):
        assert fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(SHAPES) == 574000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(SHAPES) >
                fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_337_times_2000_plus_shape_count_times_3000_plus_text_count_times_2500(str(EMPTY)) == 84000


# --- F2: fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300 ---

class TestFodgFileSizeMod347Times2050PlusShape2800PlusText2300:
    def test_empty_returns_24600(self):
        assert fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(EMPTY) == 24600

    def test_minimal_returns_179350(self):
        assert fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL) == 179350

    def test_shapes_returns_505000(self):
        assert fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(SHAPES) == 505000

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL) >= 0

    def test_shapes_greater_than_minimal(self):
        assert (fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(SHAPES) >
                fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(MINIMAL))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_347_times_2050_plus_shape_count_times_2800_plus_text_count_times_2300(str(EMPTY)) == 24600
