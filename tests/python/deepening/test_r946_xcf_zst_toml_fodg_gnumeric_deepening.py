"""Sprint 393 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510,
    xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 632950
FN2_EXPECTED = 18392


class TestXcfFileSizeMod269Times3550PlusImageTypeTimes5400PlusWidthTimes540PlusHeightTimes510:
    def test_returns_int(self):
        result = xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_269_times_3550_plus_image_type_times_5400_plus_width_times_540_plus_height_times_510(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes89PlusImageTypeTimes5900PlusWidthTimesHeightTimes2550:
    def test_returns_int(self):
        result = xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_89_plus_image_type_times_5900_plus_width_times_height_times_2550(_SAMPLE)
        assert result == FN2_EXPECTED
