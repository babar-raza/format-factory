"""Sprint 438 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670,
    xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 909170
FN2_EXPECTED = 25994


class TestXcfFileSizeMod313Times5100PlusImageTypeTimes7100PlusWidthTimes700PlusHeightTimes670:
    def test_returns_int(self):
        result = xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_313_times_5100_plus_image_type_times_7100_plus_width_times_700_plus_height_times_670(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes123PlusImageTypeTimes8100PlusWidthTimesHeightTimes4100:
    def test_returns_int(self):
        result = xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_123_plus_image_type_times_8100_plus_width_times_height_times_4100(_SAMPLE)
        assert result == FN2_EXPECTED
