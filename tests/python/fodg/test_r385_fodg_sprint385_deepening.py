"""Sprint 385 FODG analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_FODG = _REPO / "samples" / "by-format" / "fodg"
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100,
    fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900,
)


# --- F1: fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100 ---

class TestFodgFileSizeMod563Times3600PlusShape4600PlusText4100:
    def test_empty_returns_1764000(self):
        assert fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY) == 1764000

    def test_minimal_returns_1257900(self):
        assert fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(MINIMAL) == 1257900

    def test_shapes_returns_1829200(self):
        assert fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(SHAPES) == 1829200

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(SHAPES) >
                fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_563_times_3600_plus_shape_count_times_4600_plus_text_count_times_4100(str(EMPTY)) == 1764000


# --- F2: fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900 ---

class TestFodgFileSizeMod569Times3650PlusShape4400PlusText3900:
    def test_empty_returns_1766600(self):
        assert fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY) == 1766600

    def test_minimal_returns_1231050(self):
        assert fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL) == 1231050

    def test_shapes_returns_1809500(self):
        assert fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(SHAPES) == 1809500

    def test_empty_returns_int(self):
        assert isinstance(fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY), int)

    def test_minimal_returns_int(self):
        assert isinstance(fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL), int)

    def test_shapes_returns_int(self):
        assert isinstance(fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(SHAPES), int)

    def test_empty_nonnegative(self):
        assert fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY) >= 0

    def test_minimal_nonnegative(self):
        assert fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(MINIMAL) >= 0

    def test_shapes_greater_than_empty(self):
        assert (fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(SHAPES) >
                fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(EMPTY))

    def test_accepts_string_path(self):
        assert fodg_file_size_mod_569_times_3650_plus_shape_count_times_4400_plus_text_count_times_3900(str(EMPTY)) == 1766600
