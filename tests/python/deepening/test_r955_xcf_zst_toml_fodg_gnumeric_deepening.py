"""Sprint 402 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550,
    xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 695330
FN2_EXPECTED = 20166


class TestXcfFileSizeMod287Times3900PlusImageTypeTimes5900PlusWidthTimes580PlusHeightTimes550:
    def test_returns_int(self):
        result = xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_287_times_3900_plus_image_type_times_5900_plus_width_times_580_plus_height_times_550(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes97PlusImageTypeTimes6300PlusWidthTimesHeightTimes2900:
    def test_returns_int(self):
        result = xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_97_plus_image_type_times_6300_plus_width_times_height_times_2900(_SAMPLE)
        assert result == FN2_EXPECTED
