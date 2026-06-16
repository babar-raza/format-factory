"""R265 – FODP, ODT, QOI, XCF product deepening round 2: 8 new analytics functions.

Sprint 13: 2 functions each across 4 formats.
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


class TestFodpNotesToSlideRatio:
    def test_returns_float(self):
        from fodp import fodp_notes_to_slide_ratio
        f = sorted(FODP_DIR.glob("*.fodp"))[0]
        assert isinstance(fodp_notes_to_slide_ratio(str(f)), float)

    def test_nonnegative(self):
        from fodp import fodp_notes_to_slide_ratio
        for f in FODP_DIR.glob("*.fodp"):
            assert fodp_notes_to_slide_ratio(str(f)) >= 0.0


class TestFodpImageToSlideRatio:
    def test_returns_float(self):
        from fodp import fodp_image_to_slide_ratio
        f = sorted(FODP_DIR.glob("*.fodp"))[0]
        assert isinstance(fodp_image_to_slide_ratio(str(f)), float)

    def test_nonnegative(self):
        from fodp import fodp_image_to_slide_ratio
        for f in FODP_DIR.glob("*.fodp"):
            assert fodp_image_to_slide_ratio(str(f)) >= 0.0


class TestOdtTotalElements:
    def test_returns_int(self):
        from odt import odt_total_elements
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_total_elements(str(f)), int)

    def test_positive_for_valid(self):
        from odt import odt_total_elements
        for f in ODT_DIR.glob("*.odt"):
            assert odt_total_elements(str(f)) > 0


class TestOdtIsEmpty:
    def test_returns_bool(self):
        from odt import odt_is_empty
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_is_empty(str(f)), bool)

    def test_valid_docs_not_empty(self):
        from odt import odt_is_empty
        for f in ODT_DIR.glob("*.odt"):
            assert odt_is_empty(str(f)) is False


class TestQoiDimensionRatio:
    def test_returns_float(self):
        from qoi import qoi_dimension_ratio
        f = sorted(QOI_DIR.glob("*.qoi"))[0]
        assert isinstance(qoi_dimension_ratio(str(f)), float)

    def test_1x1_is_one(self):
        from qoi import qoi_dimension_ratio
        f = QOI_DIR / "1x1-red.qoi"
        assert qoi_dimension_ratio(str(f)) == 1.0

    def test_positive(self):
        from qoi import qoi_dimension_ratio
        for f in QOI_DIR.glob("*.qoi"):
            assert qoi_dimension_ratio(str(f)) > 0.0


class TestQoiIsLandscape:
    def test_returns_bool(self):
        from qoi import qoi_is_landscape
        f = sorted(QOI_DIR.glob("*.qoi"))[0]
        assert isinstance(qoi_is_landscape(str(f)), bool)

    def test_1x1_not_landscape(self):
        from qoi import qoi_is_landscape
        f = QOI_DIR / "1x1-red.qoi"
        assert qoi_is_landscape(str(f)) is False

    def test_4x1_is_landscape(self):
        from qoi import qoi_is_landscape
        f = QOI_DIR / "4x1-gradient.qoi"
        assert qoi_is_landscape(str(f)) is True


class TestXcfTotalLayerPixels:
    def test_returns_int(self):
        from xcf import xcf_total_layer_pixels
        f = sorted(XCF_DIR.glob("*.xcf"))[0]
        assert isinstance(xcf_total_layer_pixels(str(f)), int)

    def test_positive(self):
        from xcf import xcf_total_layer_pixels
        for f in XCF_DIR.glob("*.xcf"):
            assert xcf_total_layer_pixels(str(f)) > 0


class TestXcfIsSingleLayer:
    def test_returns_bool(self):
        from xcf import xcf_is_single_layer
        f = sorted(XCF_DIR.glob("*.xcf"))[0]
        assert isinstance(xcf_is_single_layer(str(f)), bool)
