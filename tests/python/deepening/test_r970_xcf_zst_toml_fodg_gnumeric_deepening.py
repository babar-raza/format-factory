"""Sprint 417 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600,
    xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 784430
FN2_EXPECTED = 22446


class TestXcfFileSizeMod299Times4400PlusImageTypeTimes6400PlusWidthTimes630PlusHeightTimes600:
    def test_returns_int(self):
        result = xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_299_times_4400_plus_image_type_times_6400_plus_width_times_630_plus_height_times_600(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes107PlusImageTypeTimes6800PlusWidthTimesHeightTimes3400:
    def test_returns_int(self):
        result = xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_107_plus_image_type_times_6800_plus_width_times_height_times_3400(_SAMPLE)
        assert result == FN2_EXPECTED
