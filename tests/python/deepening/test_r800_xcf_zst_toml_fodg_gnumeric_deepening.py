"""Sprint R800 — FODG compound analytics deepening tests (Sprint 247)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500,
    fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod59Times6PlusShapeTimes1300PlusTextTimes1000PlusPageTimes500:
    def test_returns_int(self):
        result = fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500(_FODG)
        assert result == 800

    def test_string_path(self):
        result = fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_59_times_6_plus_shape_times_1300_plus_text_times_1000_plus_page_times_500(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes5PlusShapeTimes700PlusTextTimes400PlusPageTimes200:
    def test_returns_int(self):
        result = fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200(_FODG)
        assert result == 5465

    def test_string_path(self):
        result = fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
