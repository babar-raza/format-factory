"""Sprint 442 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500,
    fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 19400
FN2_EXPECTED = 133784


class TestFodgFileSizeMod341Times230PlusShapeTimes14600PlusTextTimes14200PlusPageTimes12500:
    def test_returns_int(self):
        result = fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_341_times_230_plus_shape_times_14600_plus_text_times_14200_plus_page_times_12500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes127PlusShapeTimes53PlusTextTimes52PlusPageTimes53:
    def test_returns_int(self):
        result = fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_127_plus_shape_times_53_plus_text_times_52_plus_page_times_53(_SAMPLE)
        assert result == FN2_EXPECTED
