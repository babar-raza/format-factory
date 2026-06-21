"""Sprint 385 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700,
    fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 10995
FN2_EXPECTED = 89539


class TestFodgFileSizeMod259Times135PlusShapeTimes10800PlusTextTimes10400PlusPageTimes8700:
    def test_returns_int(self):
        result = fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_259_times_135_plus_shape_times_10800_plus_text_times_10400_plus_page_times_8700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes85PlusShapeTimes34PlusTextTimes33PlusPageTimes34:
    def test_returns_int(self):
        result = fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_85_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_SAMPLE)
        assert result == FN2_EXPECTED
