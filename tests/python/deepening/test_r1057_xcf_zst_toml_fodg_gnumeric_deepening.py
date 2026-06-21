"""Sprint 504 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910,
    xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1336850
FN2_EXPECTED = 37750


class TestXcfFileSizeMod449Times7500PlusImageTypeTimes9500PlusWidthTimes940PlusHeightTimes910:
    def test_returns_int(self):
        result = xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_449_times_7500_plus_image_type_times_9500_plus_width_times_940_plus_height_times_910(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes175PlusImageTypeTimes11500PlusWidthTimesHeightTimes6600:
    def test_returns_int(self):
        result = xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_175_plus_image_type_times_11500_plus_width_times_height_times_6600(_SAMPLE)
        assert result == FN2_EXPECTED
