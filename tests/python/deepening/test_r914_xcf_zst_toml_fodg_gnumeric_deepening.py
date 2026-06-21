"""Sprint 361 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100,
    fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 21635
FN2_EXPECTED = 68471


class TestFodgFileSizeMod225Times95PlusShapeTimes9200PlusTextTimes8800PlusPageTimes7100:
    def test_returns_int(self):
        result = fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_225_times_95_plus_shape_times_9200_plus_text_times_8800_plus_page_times_7100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes65PlusShapeTimes26PlusTextTimes25PlusPageTimes26:
    def test_returns_int(self):
        result = fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_65_plus_shape_times_26_plus_text_times_25_plus_page_times_26(_SAMPLE)
        assert result == FN2_EXPECTED
