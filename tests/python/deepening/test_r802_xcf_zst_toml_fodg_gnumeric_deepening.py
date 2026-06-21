"""Sprint R802 — XCF compound analytics deepening tests (Sprint 249)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30,
    xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod17Times200PlusImageTypeTimes700PlusWidthTimes50PlusHeightTimes30:
    def test_returns_int(self):
        result = xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30(_XCF)
        assert result == 1680

    def test_string_path(self):
        result = xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_17_times_200_plus_image_type_times_700_plus_width_times_50_plus_height_times_30(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes6PlusImageTypeTimes800PlusWidthTimesHeightTimes100:
    def test_returns_int(self):
        result = xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100(_XCF)
        assert result == 1168

    def test_string_path(self):
        result = xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_6_plus_image_type_times_800_plus_width_times_height_times_100(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
