"""Sprint 399 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540,
    xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 677510
FN2_EXPECTED = 19710


class TestXcfFileSizeMod285Times3800PlusImageTypeTimes5800PlusWidthTimes570PlusHeightTimes540:
    def test_returns_int(self):
        result = xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_285_times_3800_plus_image_type_times_5800_plus_width_times_570_plus_height_times_540(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes95PlusImageTypeTimes6200PlusWidthTimesHeightTimes2800:
    def test_returns_int(self):
        result = xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_95_plus_image_type_times_6200_plus_width_times_height_times_2800(_SAMPLE)
        assert result == FN2_EXPECTED
