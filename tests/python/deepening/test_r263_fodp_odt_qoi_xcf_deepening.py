"""R263 – FODP, ODT, QOI, XCF product deepening: 8 new analytics functions.

Sprint 11: 2 functions each across 4 formats.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestFodpAverageTextPerSlide:
    def test_returns_float(self):
        from fodp import fodp_average_text_per_slide
        f = sorted(FODP_DIR.glob("*.fodp"))[0]
        assert isinstance(fodp_average_text_per_slide(str(f)), float)

    def test_nonnegative(self):
        from fodp import fodp_average_text_per_slide
        for f in FODP_DIR.glob("*.fodp"):
            assert fodp_average_text_per_slide(str(f)) >= 0.0


class TestFodpShapeToSlideRatio:
    def test_returns_float(self):
        from fodp import fodp_shape_to_slide_ratio
        f = sorted(FODP_DIR.glob("*.fodp"))[0]
        assert isinstance(fodp_shape_to_slide_ratio(str(f)), float)

    def test_nonnegative(self):
        from fodp import fodp_shape_to_slide_ratio
        for f in FODP_DIR.glob("*.fodp"):
            assert fodp_shape_to_slide_ratio(str(f)) >= 0.0


class TestOdtMinParagraphLength:
    def test_returns_int(self):
        from odt import odt_min_paragraph_length
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_min_paragraph_length(str(f)), int)

    def test_nonnegative(self):
        from odt import odt_min_paragraph_length
        for f in ODT_DIR.glob("*.odt"):
            assert odt_min_paragraph_length(str(f)) >= 0

    def test_le_max(self):
        from odt import odt_min_paragraph_length, odt_max_paragraph_length
        for f in ODT_DIR.glob("*.odt"):
            assert odt_min_paragraph_length(str(f)) <= odt_max_paragraph_length(str(f))


class TestOdtHeadingToParagraphRatio:
    def test_returns_float(self):
        from odt import odt_heading_to_paragraph_ratio
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_heading_to_paragraph_ratio(str(f)), float)

    def test_nonnegative(self):
        from odt import odt_heading_to_paragraph_ratio
        for f in ODT_DIR.glob("*.odt"):
            assert odt_heading_to_paragraph_ratio(str(f)) >= 0.0


class TestQoiPerimeter:
    def test_returns_int(self):
        from qoi import qoi_perimeter
        f = sorted(QOI_DIR.glob("*.qoi"))[0]
        assert isinstance(qoi_perimeter(str(f)), int)

    def test_1x1_perimeter(self):
        from qoi import qoi_perimeter
        f = QOI_DIR / "1x1-red.qoi"
        assert qoi_perimeter(str(f)) == 2 * (1 + 1)

    def test_positive(self):
        from qoi import qoi_perimeter
        for f in QOI_DIR.glob("*.qoi"):
            assert qoi_perimeter(str(f)) > 0


class TestQoiColorVariance:
    def test_returns_float(self):
        from qoi import qoi_color_variance
        f = sorted(QOI_DIR.glob("*.qoi"))[0]
        assert isinstance(qoi_color_variance(str(f)), float)

    def test_nonnegative(self):
        from qoi import qoi_color_variance
        for f in QOI_DIR.glob("*.qoi"):
            assert qoi_color_variance(str(f)) >= 0.0


class TestXcfDimensionRatio:
    def test_returns_float(self):
        from xcf import xcf_dimension_ratio
        f = sorted(XCF_DIR.glob("*.xcf"))[0]
        assert isinstance(xcf_dimension_ratio(str(f)), float)

    def test_square_is_one(self):
        from xcf import xcf_dimension_ratio, xcf_is_square
        for f in XCF_DIR.glob("*.xcf"):
            if xcf_is_square(str(f)):
                assert xcf_dimension_ratio(str(f)) == 1.0

    def test_positive(self):
        from xcf import xcf_dimension_ratio
        for f in XCF_DIR.glob("*.xcf"):
            assert xcf_dimension_ratio(str(f)) > 0.0


class TestXcfLayerDensity:
    def test_returns_float(self):
        from xcf import xcf_layer_density
        f = sorted(XCF_DIR.glob("*.xcf"))[0]
        assert isinstance(xcf_layer_density(str(f)), float)

    def test_positive(self):
        from xcf import xcf_layer_density
        for f in XCF_DIR.glob("*.xcf"):
            assert xcf_layer_density(str(f)) > 0.0
