"""Sprint 403 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900,
    fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 36630
FN2_EXPECTED = 102180


class TestFodgFileSizeMod297Times165PlusShapeTimes12000PlusTextTimes11600PlusPageTimes9900:
    def test_returns_int(self):
        result = fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_297_times_165_plus_shape_times_12000_plus_text_times_11600_plus_page_times_9900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes97PlusShapeTimes39PlusTextTimes38PlusPageTimes39:
    def test_returns_int(self):
        result = fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_97_plus_shape_times_39_plus_text_times_38_plus_page_times_39(_SAMPLE)
        assert result == FN2_EXPECTED
