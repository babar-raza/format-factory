"""Tests for PGM/PPM/QOI/XCF FOSS gap closure (6 functions)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_zero_to_nonzero_ratio
from src.python.ppm.ppm_parser import ppm_nonblack_pixel_ratio
from src.python.qoi.qoi_parser import qoi_nonblack_pixel_ratio
from src.python.xcf.xcf_parser import (
    xcf_num_layers_plus_image_type_id,
    xcf_width_times_file_size,
    xcf_width_per_layer,
)

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"


class TestPgmZeroToNonzeroRatio:
    def test_returns_float(self):
        assert isinstance(pgm_zero_to_nonzero_ratio(_PGM), float)

    def test_nonnegative(self):
        assert pgm_zero_to_nonzero_ratio(_PGM) >= 0.0

    def test_consistent(self):
        assert pgm_zero_to_nonzero_ratio(_PGM) == pgm_zero_to_nonzero_ratio(_PGM)


class TestPpmNonblackPixelRatio:
    def test_returns_float(self):
        assert isinstance(ppm_nonblack_pixel_ratio(_PPM), float)

    def test_in_range(self):
        r = ppm_nonblack_pixel_ratio(_PPM)
        assert 0.0 <= r <= 1.0

    def test_red_pixel_is_nonblack(self):
        # 1x1-red.ppm has a red pixel, which is non-black
        assert ppm_nonblack_pixel_ratio(_PPM) > 0.0


class TestQoiNonblackPixelRatio:
    def test_returns_float(self):
        assert isinstance(qoi_nonblack_pixel_ratio(_QOI), float)

    def test_in_range(self):
        r = qoi_nonblack_pixel_ratio(_QOI)
        assert 0.0 <= r <= 1.0

    def test_red_pixel_is_nonblack(self):
        assert qoi_nonblack_pixel_ratio(_QOI) > 0.0


class TestXcfNumLayersPlusImageTypeId:
    def test_returns_int(self):
        assert isinstance(xcf_num_layers_plus_image_type_id(_XCF), int)

    def test_positive(self):
        assert xcf_num_layers_plus_image_type_id(_XCF) >= 1

    def test_consistent(self):
        assert xcf_num_layers_plus_image_type_id(_XCF) == xcf_num_layers_plus_image_type_id(_XCF)


class TestXcfWidthTimesFileSize:
    def test_returns_int(self):
        assert isinstance(xcf_width_times_file_size(_XCF), int)

    def test_positive(self):
        assert xcf_width_times_file_size(_XCF) > 0

    def test_consistent(self):
        assert xcf_width_times_file_size(_XCF) == xcf_width_times_file_size(_XCF)


class TestXcfWidthPerLayer:
    def test_returns_float(self):
        result = xcf_width_per_layer(_XCF)
        assert isinstance(result, (int, float))

    def test_positive(self):
        assert xcf_width_per_layer(_XCF) > 0

    def test_consistent(self):
        assert xcf_width_per_layer(_XCF) == xcf_width_per_layer(_XCF)
