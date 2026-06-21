"""Sprint 426 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630,
    xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 837890
FN2_EXPECTED = 24170


class TestXcfFileSizeMod305Times4700PlusImageTypeTimes6700PlusWidthTimes660PlusHeightTimes630:
    def test_returns_int(self):
        result = xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_305_times_4700_plus_image_type_times_6700_plus_width_times_660_plus_height_times_630(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes115PlusImageTypeTimes7300PlusWidthTimesHeightTimes3700:
    def test_returns_int(self):
        result = xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_115_plus_image_type_times_7300_plus_width_times_height_times_3700(_SAMPLE)
        assert result == FN2_EXPECTED
