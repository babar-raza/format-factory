"""Sprint 408 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570,
    xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 730970
FN2_EXPECTED = 21078


class TestXcfFileSizeMod291Times4100PlusImageTypeTimes6100PlusWidthTimes600PlusHeightTimes570:
    def test_returns_int(self):
        result = xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_291_times_4100_plus_image_type_times_6100_plus_width_times_600_plus_height_times_570(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes101PlusImageTypeTimes6500PlusWidthTimesHeightTimes3100:
    def test_returns_int(self):
        result = xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_101_plus_image_type_times_6500_plus_width_times_height_times_3100(_SAMPLE)
        assert result == FN2_EXPECTED
