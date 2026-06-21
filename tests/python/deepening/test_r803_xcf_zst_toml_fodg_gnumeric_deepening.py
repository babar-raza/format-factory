"""Sprint R803 — FODG compound analytics deepening tests (Sprint 250)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600,
    fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod61Times8PlusShapeTimes1500PlusTextTimes1100PlusPageTimes600:
    def test_returns_int(self):
        result = fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600(_FODG)
        assert result == 728

    def test_string_path(self):
        result = fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_61_times_8_plus_shape_times_1500_plus_text_times_1100_plus_page_times_600(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes7PlusShapeTimes600PlusTextTimes300PlusPageTimes250:
    def test_returns_int(self):
        result = fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250(_FODG)
        assert result == 7621

    def test_string_path(self):
        result = fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
