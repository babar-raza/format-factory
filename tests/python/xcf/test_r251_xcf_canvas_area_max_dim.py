"""Tests for xcf_canvas_area and xcf_max_layer_dimension (Sprint 41)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_canvas_area, xcf_max_layer_dimension

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")    # 1x1 -> area=1, max_dim=1
_BLUE = str(_DIR / "1x1-rgba-blue.xcf") # 1x1 -> area=1, max_dim=1
_GRAY = str(_DIR / "2x2-gray.xcf")      # 2x2 -> area=4, max_dim=2


class TestXcfCanvasArea:
    def test_return_type(self):
        assert isinstance(xcf_canvas_area(_RED), int)

    def test_exact_1_for_1x1(self):
        # 1x1-red-rgb.xcf: 1*1 = 1
        assert xcf_canvas_area(_RED) == 1

    def test_exact_1_for_rgba_blue(self):
        assert xcf_canvas_area(_BLUE) == 1

    def test_exact_4_for_2x2(self):
        # 2x2-gray.xcf: 2*2 = 4
        assert xcf_canvas_area(_GRAY) == 4

    def test_positive(self):
        assert xcf_canvas_area(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_canvas_area(_RED) == xcf_canvas_area(_RED)


class TestXcfMaxLayerDimension:
    def test_return_type(self):
        assert isinstance(xcf_max_layer_dimension(_RED), int)

    def test_exact_1_for_1x1_red(self):
        # 1x1: max(1,1) = 1
        assert xcf_max_layer_dimension(_RED) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_max_layer_dimension(_BLUE) == 1

    def test_exact_2_for_2x2(self):
        # 2x2: max(2,2) = 2
        assert xcf_max_layer_dimension(_GRAY) == 2

    def test_nonnegative(self):
        assert xcf_max_layer_dimension(_RED) >= 0

    def test_consistent_across_calls(self):
        assert xcf_max_layer_dimension(_RED) == xcf_max_layer_dimension(_RED)

    def test_at_least_canvas_area_sqrt(self):
        # max_dim >= sqrt(area) is always true for any rectangle
        import math
        area = xcf_canvas_area(_GRAY)
        max_dim = xcf_max_layer_dimension(_GRAY)
        assert max_dim >= math.isqrt(area)
