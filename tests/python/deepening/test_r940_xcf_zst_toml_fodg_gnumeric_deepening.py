"""Sprint 387 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490,
    xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 615110
FN2_EXPECTED = 17580


class TestXcfFileSizeMod259Times3450PlusImageTypeTimes5200PlusWidthTimes520PlusHeightTimes490:
    def test_returns_int(self):
        result = xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_259_times_3450_plus_image_type_times_5200_plus_width_times_520_plus_height_times_490(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes85PlusImageTypeTimes5700PlusWidthTimesHeightTimes2450:
    def test_returns_int(self):
        result = xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_85_plus_image_type_times_5700_plus_width_times_height_times_2450(_SAMPLE)
        assert result == FN2_EXPECTED
