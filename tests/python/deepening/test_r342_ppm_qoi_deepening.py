"""Sprint 132 deepening – PPM pixel_area/dimension_sum, QOI pixel_area/dimension_sum."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_pixel_area, ppm_dimension_sum
from src.python.qoi.qoi_parser import qoi_pixel_area, qoi_dimension_sum

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestPpmPixelArea:
    def test_1x1(self):
        assert ppm_pixel_area(PPM / "1x1-red.ppm") == 1

    def test_2x2(self):
        assert ppm_pixel_area(PPM / "2x2-rgbw.ppm") == 4

    def test_3x1(self):
        assert ppm_pixel_area(PPM / "3x1-gradient.ppm") == 3

    def test_returns_int(self):
        assert isinstance(ppm_pixel_area(PPM / "1x1-red.ppm"), int)

    def test_positive(self):
        assert ppm_pixel_area(PPM / "1x1-red.ppm") > 0


class TestPpmDimensionSum:
    def test_1x1(self):
        assert ppm_dimension_sum(PPM / "1x1-red.ppm") == 2

    def test_2x2(self):
        assert ppm_dimension_sum(PPM / "2x2-rgbw.ppm") == 4

    def test_3x1(self):
        assert ppm_dimension_sum(PPM / "3x1-gradient.ppm") == 4

    def test_returns_int(self):
        assert isinstance(ppm_dimension_sum(PPM / "1x1-red.ppm"), int)

    def test_positive(self):
        assert ppm_dimension_sum(PPM / "1x1-red.ppm") > 0


class TestQoiPixelArea:
    def test_1x1(self):
        assert qoi_pixel_area(QOI / "1x1-red.qoi") == 1

    def test_2x2(self):
        assert qoi_pixel_area(QOI / "2x2-black.qoi") == 4

    def test_4x1(self):
        assert qoi_pixel_area(QOI / "4x1-gradient.qoi") == 4

    def test_returns_int(self):
        assert isinstance(qoi_pixel_area(QOI / "1x1-red.qoi"), int)

    def test_positive(self):
        assert qoi_pixel_area(QOI / "1x1-red.qoi") > 0


class TestQoiDimensionSum:
    def test_1x1(self):
        assert qoi_dimension_sum(QOI / "1x1-red.qoi") == 2

    def test_2x2(self):
        assert qoi_dimension_sum(QOI / "2x2-black.qoi") == 4

    def test_4x1(self):
        assert qoi_dimension_sum(QOI / "4x1-gradient.qoi") == 5

    def test_returns_int(self):
        assert isinstance(qoi_dimension_sum(QOI / "1x1-red.qoi"), int)

    def test_positive(self):
        assert qoi_dimension_sum(QOI / "1x1-red.qoi") > 0
