"""Sprint 388 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900,
    fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 10160
FN2_EXPECTED = 91646


class TestFodgFileSizeMod261Times140PlusShapeTimes11000PlusTextTimes10600PlusPageTimes8900:
    def test_returns_int(self):
        result = fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_261_times_140_plus_shape_times_11000_plus_text_times_10600_plus_page_times_8900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes87PlusShapeTimes35PlusTextTimes34PlusPageTimes35:
    def test_returns_int(self):
        result = fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_87_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert result == FN2_EXPECTED
