"""Sprint 478 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900,
    fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 77250
FN2_EXPECTED = 159068


class TestFodgFileSizeMod419Times290PlusShapeTimes17000PlusTextTimes16600PlusPageTimes14900:
    def test_returns_int(self):
        result = fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_419_times_290_plus_shape_times_17000_plus_text_times_16600_plus_page_times_14900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes151PlusShapeTimes65PlusTextTimes64PlusPageTimes65:
    def test_returns_int(self):
        result = fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_151_plus_shape_times_65_plus_text_times_64_plus_page_times_65(_SAMPLE)
        assert result == FN2_EXPECTED
