"""Sprint 429 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640,
    xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 855710
FN2_EXPECTED = 24626


class TestXcfFileSizeMod307Times4800PlusImageTypeTimes6800PlusWidthTimes670PlusHeightTimes640:
    def test_returns_int(self):
        result = xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_307_times_4800_plus_image_type_times_6800_plus_width_times_670_plus_height_times_640(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes117PlusImageTypeTimes7500PlusWidthTimesHeightTimes3800:
    def test_returns_int(self):
        result = xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_117_plus_image_type_times_7500_plus_width_times_height_times_3800(_SAMPLE)
        assert result == FN2_EXPECTED
