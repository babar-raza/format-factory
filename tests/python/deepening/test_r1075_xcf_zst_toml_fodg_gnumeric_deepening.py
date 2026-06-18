"""Sprint 522 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990,
    xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"
_SAMPLE_RGBA = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"
_SAMPLE_GRAY = _REPO / "samples/by-format/xcf/valid/2x2-gray.xcf"

FN1_EXPECTED = 1488810
FN2_EXPECTED = 41107
# rgba: image_type_id=0 (RGBA is still type 0 in XCF), file_size=178, w=1, h=1
FN1_RGBA_EXPECTED = 1497210
FN2_RGBA_EXPECTED = 41298
# gray: image_type_id=1, file_size=178, w=2, h=2 — exercises non-zero image_type path
FN1_GRAY_EXPECTED = 1509520
FN2_GRAY_EXPECTED = 75498


class TestXcfFileSizeMod499Times8400PlusImageTypeTimes10300PlusWidthTimes1020PlusHeightTimes990:
    def test_returns_int(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes191PlusImageTypeTimes12300PlusWidthTimesHeightTimes7300:
    def test_returns_int(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert result == FN2_EXPECTED


class TestXcfFn1NonRgbSamples:
    """Verify fn1 against RGBA and grayscale samples (exercises image_type_id != 0 for gray)."""

    def test_fn1_rgba_sample(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE_RGBA)
        assert result == FN1_RGBA_EXPECTED

    def test_fn1_gray_sample_nonzero_image_type(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE_GRAY)
        assert result == FN1_GRAY_EXPECTED

    def test_fn1_gray_differs_from_rgb(self):
        rgb = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        gray = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE_GRAY)
        assert gray != rgb


class TestXcfFn2NonRgbSamples:
    """Verify fn2 against RGBA and grayscale samples (exercises image_type_id != 0 for gray)."""

    def test_fn2_rgba_sample(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE_RGBA)
        assert result == FN2_RGBA_EXPECTED

    def test_fn2_gray_sample_nonzero_image_type(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE_GRAY)
        assert result == FN2_GRAY_EXPECTED

    def test_fn2_gray_differs_from_rgb(self):
        rgb = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        gray = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE_GRAY)
        assert gray != rgb
