"""Sprint 357 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390,
    xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 525910
FN2_EXPECTED = 13114


class TestXcfFileSizeMod221Times2950PlusImageTypeTimes4200PlusWidthTimes420PlusHeightTimes390:
    def test_returns_int(self):
        result = xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_221_times_2950_plus_image_type_times_4200_plus_width_times_420_plus_height_times_390(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes63PlusImageTypeTimes4600PlusWidthTimesHeightTimes1900:
    def test_returns_int(self):
        result = xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_63_plus_image_type_times_4600_plus_width_times_height_times_1900(_SAMPLE)
        assert result == FN2_EXPECTED
