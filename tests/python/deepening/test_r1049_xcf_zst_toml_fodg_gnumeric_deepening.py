"""Sprint 496 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100,
    fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 61275
FN2_EXPECTED = 171710


class TestFodgFileSizeMod457Times325PlusShapeTimes18200PlusTextTimes17800PlusPageTimes16100:
    def test_returns_int(self):
        result = fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_457_times_325_plus_shape_times_18200_plus_text_times_17800_plus_page_times_16100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes163PlusShapeTimes71PlusTextTimes70PlusPageTimes71:
    def test_returns_int(self):
        result = fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_163_plus_shape_times_71_plus_text_times_70_plus_page_times_71(_SAMPLE)
        assert result == FN2_EXPECTED
