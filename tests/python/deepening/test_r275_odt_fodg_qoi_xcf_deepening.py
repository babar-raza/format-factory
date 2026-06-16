"""Sprint 23: ODT/FODG/QOI/XCF product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODT = str(next((_REPO / "samples" / "by-format" / "odt" / "valid").glob("*.odt")))
FODG = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
QOI = str(next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi")))
XCF = str(next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf")))


# --- ODT ---

class TestOdtMinWordsPerParagraph:
    def test_returns_int(self):
        from odt import odt_min_words_per_paragraph
        assert isinstance(odt_min_words_per_paragraph(ODT), int)

    def test_non_negative(self):
        from odt import odt_min_words_per_paragraph
        assert odt_min_words_per_paragraph(ODT) >= 0

    def test_lte_max(self):
        from odt import odt_min_words_per_paragraph, odt_max_words_per_paragraph
        mn = odt_min_words_per_paragraph(ODT)
        mx = odt_max_words_per_paragraph(ODT)
        if mn > 0:
            assert mn <= mx


class TestOdtWordDensity:
    def test_returns_float(self):
        from odt import odt_word_density
        assert isinstance(odt_word_density(ODT), float)

    def test_non_negative(self):
        from odt import odt_word_density
        assert odt_word_density(ODT) >= 0.0


# --- FODG ---

class TestFodgTotalTextLength:
    def test_returns_int(self):
        from fodg import fodg_total_text_length
        assert isinstance(fodg_total_text_length(FODG), int)

    def test_non_negative(self):
        from fodg import fodg_total_text_length
        assert fodg_total_text_length(FODG) >= 0


class TestFodgHasText:
    def test_returns_bool(self):
        from fodg import fodg_has_text
        assert isinstance(fodg_has_text(FODG), bool)


# --- QOI ---

class TestQoiMinChannelAverage:
    def test_returns_float(self):
        from qoi import qoi_min_channel_average
        assert isinstance(qoi_min_channel_average(QOI), float)

    def test_lte_max(self):
        from qoi import qoi_min_channel_average, qoi_max_channel_average
        assert qoi_min_channel_average(QOI) <= qoi_max_channel_average(QOI)


class TestQoiHasAnyWhite:
    def test_returns_bool(self):
        from qoi import qoi_has_any_white
        assert isinstance(qoi_has_any_white(QOI), bool)


# --- XCF ---

class TestXcfMaxDimension:
    def test_returns_int(self):
        from xcf import xcf_max_dimension
        assert isinstance(xcf_max_dimension(XCF), int)

    def test_positive(self):
        from xcf import xcf_max_dimension
        assert xcf_max_dimension(XCF) > 0


class TestXcfMinDimension:
    def test_returns_int(self):
        from xcf import xcf_min_dimension
        assert isinstance(xcf_min_dimension(XCF), int)

    def test_lte_max(self):
        from xcf import xcf_min_dimension, xcf_max_dimension
        assert xcf_min_dimension(XCF) <= xcf_max_dimension(XCF)
