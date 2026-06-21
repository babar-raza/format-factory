"""Sprint 140 deepening tests: PPM min_red_value/max_blue_value, QOI total_red_value/avg_green_value."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_min_red_value, ppm_max_blue_value
from src.python.qoi.qoi_parser import qoi_total_red_value, qoi_avg_green_value

P1 = str(_REPO / "samples/by-format/ppm/valid/1x1-red.ppm")
P2 = str(_REPO / "samples/by-format/ppm/valid/2x2-rgbw.ppm")
P3 = str(_REPO / "samples/by-format/ppm/valid/3x1-gradient.ppm")
Q1 = str(_REPO / "samples/by-format/qoi/valid/1x1-red.qoi")
Q2 = str(_REPO / "samples/by-format/qoi/valid/2x2-black.qoi")
Q3 = str(_REPO / "samples/by-format/qoi/valid/4x1-gradient.qoi")


class TestPpmMinRedValue:
    def test_single_red_pixel(self):
        assert ppm_min_red_value(P1) == 255

    def test_mixed_pixels(self):
        assert ppm_min_red_value(P2) == 0

    def test_gradient(self):
        assert ppm_min_red_value(P3) == 0

    def test_return_type(self):
        assert isinstance(ppm_min_red_value(P1), int)

    def test_nonnegative(self):
        assert ppm_min_red_value(P2) >= 0


class TestPpmMaxBlueValue:
    def test_pure_red(self):
        assert ppm_max_blue_value(P1) == 0

    def test_has_blue_pixel(self):
        assert ppm_max_blue_value(P2) == 255

    def test_gradient_white(self):
        assert ppm_max_blue_value(P3) == 255

    def test_return_type(self):
        assert isinstance(ppm_max_blue_value(P1), int)

    def test_bounded(self):
        assert 0 <= ppm_max_blue_value(P3) <= 255


class TestQoiTotalRedValue:
    def test_single_red(self):
        assert qoi_total_red_value(Q1) == 255

    def test_all_black(self):
        assert qoi_total_red_value(Q2) == 0

    def test_gradient(self):
        assert qoi_total_red_value(Q3) == 510

    def test_return_type(self):
        assert isinstance(qoi_total_red_value(Q1), int)

    def test_nonnegative(self):
        assert qoi_total_red_value(Q2) >= 0


class TestQoiAvgGreenValue:
    def test_red_only(self):
        assert qoi_avg_green_value(Q1) == 0.0

    def test_black(self):
        assert qoi_avg_green_value(Q2) == 0.0

    def test_gradient(self):
        assert qoi_avg_green_value(Q3) == 127.5

    def test_return_type(self):
        assert isinstance(qoi_avg_green_value(Q1), float)

    def test_bounded(self):
        assert 0.0 <= qoi_avg_green_value(Q3) <= 255.0
