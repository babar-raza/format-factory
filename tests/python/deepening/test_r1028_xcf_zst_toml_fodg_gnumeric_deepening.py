"""Sprint 475 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700,
    fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 81675
FN2_EXPECTED = 156961


class TestFodgFileSizeMod409Times285PlusShapeTimes16800PlusTextTimes16400PlusPageTimes14700:
    def test_returns_int(self):
        result = fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_409_times_285_plus_shape_times_16800_plus_text_times_16400_plus_page_times_14700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes149PlusShapeTimes64PlusTextTimes63PlusPageTimes64:
    def test_returns_int(self):
        result = fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_149_plus_shape_times_64_plus_text_times_63_plus_page_times_64(_SAMPLE)
        assert result == FN2_EXPECTED
