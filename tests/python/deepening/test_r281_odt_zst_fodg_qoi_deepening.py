"""Sprint 51: ODT/ZST/FODG/QOI product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODT = str(next((_REPO / "samples" / "by-format" / "odt" / "valid").glob("*.odt")))
ZST = str(next((_REPO / "samples" / "by-format" / "zst" / "valid").glob("*.zst")))
FODG = str(next((_REPO / "samples" / "by-format" / "fodg").glob("*.fodg")))
QOI = str(next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi")))


# --- ODT ---

class TestOdtNonemptyParagraphCount:
    def test_returns_int(self):
        from odt import odt_nonempty_paragraph_count
        assert isinstance(odt_nonempty_paragraph_count(ODT), int)

    def test_non_negative(self):
        from odt import odt_nonempty_paragraph_count
        assert odt_nonempty_paragraph_count(ODT) >= 0


class TestOdtCharDensity:
    def test_returns_float(self):
        from odt import odt_char_density
        assert isinstance(odt_char_density(ODT), float)

    def test_non_negative(self):
        from odt import odt_char_density
        assert odt_char_density(ODT) >= 0.0


# --- ZST ---

class TestZstFrameSizeVariance:
    def test_returns_float(self):
        from zst import zst_frame_size_variance
        assert isinstance(zst_frame_size_variance(ZST), float)

    def test_non_negative(self):
        from zst import zst_frame_size_variance
        assert zst_frame_size_variance(ZST) >= 0.0


class TestZstLargestFrameRatio:
    def test_returns_float(self):
        from zst import zst_largest_frame_ratio
        assert isinstance(zst_largest_frame_ratio(ZST), float)

    def test_in_range(self):
        from zst import zst_largest_frame_ratio
        assert 0.0 <= zst_largest_frame_ratio(ZST) <= 1.0


# --- FODG ---

class TestFodgShapeToPageVariance:
    def test_returns_float(self):
        from fodg import fodg_shape_to_page_variance
        assert isinstance(fodg_shape_to_page_variance(FODG), float)

    def test_non_negative(self):
        from fodg import fodg_shape_to_page_variance
        assert fodg_shape_to_page_variance(FODG) >= 0.0


class TestFodgMaxTextPerPage:
    def test_returns_int(self):
        from fodg import fodg_max_text_per_page
        assert isinstance(fodg_max_text_per_page(FODG), int)

    def test_non_negative(self):
        from fodg import fodg_max_text_per_page
        assert fodg_max_text_per_page(FODG) >= 0


# --- QOI ---

class TestQoiMinDimension:
    def test_returns_int(self):
        from qoi import qoi_min_dimension
        assert isinstance(qoi_min_dimension(QOI), int)

    def test_positive(self):
        from qoi import qoi_min_dimension
        assert qoi_min_dimension(QOI) > 0


class TestQoiArea:
    def test_returns_int(self):
        from qoi import qoi_area
        assert isinstance(qoi_area(QOI), int)

    def test_positive(self):
        from qoi import qoi_area
        assert qoi_area(QOI) > 0
