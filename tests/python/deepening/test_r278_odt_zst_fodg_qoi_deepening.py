"""Sprint 48: ODT/ZST/FODG/QOI product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODT = str(next((_REPO / "samples" / "by-format" / "odt" / "valid").glob("*.odt")))
ZST = str(next((_REPO / "samples" / "by-format" / "zst" / "valid").glob("*.zst")))
FODG = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
QOI = str(next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi")))


# --- ODT ---

class TestOdtSentenceDensity:
    def test_returns_float(self):
        from odt import odt_sentence_density
        assert isinstance(odt_sentence_density(ODT), float)

    def test_non_negative(self):
        from odt import odt_sentence_density
        assert odt_sentence_density(ODT) >= 0.0


class TestOdtTableDensity:
    def test_returns_float(self):
        from odt import odt_table_density
        assert isinstance(odt_table_density(ODT), float)

    def test_in_range(self):
        from odt import odt_table_density
        assert 0.0 <= odt_table_density(ODT) <= 1.0


# --- ZST ---

class TestZstTotalFrameSize:
    def test_returns_int(self):
        from zst import zst_total_frame_size
        assert isinstance(zst_total_frame_size(ZST), int)

    def test_positive(self):
        from zst import zst_total_frame_size
        assert zst_total_frame_size(ZST) > 0


class TestZstHasMultipleFrames:
    def test_returns_bool(self):
        from zst import zst_has_multiple_frames
        assert isinstance(zst_has_multiple_frames(ZST), bool)


# --- FODG ---

class TestFodgAvgTextPerPage:
    def test_returns_float(self):
        from fodg import fodg_avg_text_per_page
        assert isinstance(fodg_avg_text_per_page(FODG), float)

    def test_non_negative(self):
        from fodg import fodg_avg_text_per_page
        assert fodg_avg_text_per_page(FODG) >= 0.0


class TestFodgHasMultiplePages:
    def test_returns_bool(self):
        from fodg import fodg_has_multiple_pages
        assert isinstance(fodg_has_multiple_pages(FODG), bool)


# --- QOI ---

class TestQoiChannelRange:
    def test_returns_float(self):
        from qoi import qoi_channel_range
        assert isinstance(qoi_channel_range(QOI), float)

    def test_non_negative(self):
        from qoi import qoi_channel_range
        assert qoi_channel_range(QOI) >= 0.0


class TestQoiDiagonal:
    def test_returns_float(self):
        from qoi import qoi_diagonal
        assert isinstance(qoi_diagonal(QOI), float)

    def test_positive(self):
        from qoi import qoi_diagonal
        assert qoi_diagonal(QOI) > 0.0
