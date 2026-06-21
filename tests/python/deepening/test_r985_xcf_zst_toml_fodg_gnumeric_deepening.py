"""Sprint 432 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650,
    xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 873530
FN2_EXPECTED = 25082


class TestXcfFileSizeMod309Times4900PlusImageTypeTimes6900PlusWidthTimes680PlusHeightTimes650:
    def test_returns_int(self):
        result = xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_309_times_4900_plus_image_type_times_6900_plus_width_times_680_plus_height_times_650(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes119PlusImageTypeTimes7700PlusWidthTimesHeightTimes3900:
    def test_returns_int(self):
        result = xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_119_plus_image_type_times_7700_plus_width_times_height_times_3900(_SAMPLE)
        assert result == FN2_EXPECTED
