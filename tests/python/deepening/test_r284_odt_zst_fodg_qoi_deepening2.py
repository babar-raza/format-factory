"""Sprint 54: ODT/ZST/FODG/QOI product deepening round 2 — 8 new analytics functions."""
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

class TestOdtEmptyParagraphCount:
    def test_returns_int(self):
        from odt import odt_empty_paragraph_count
        assert isinstance(odt_empty_paragraph_count(ODT), int)

    def test_non_negative(self):
        from odt import odt_empty_paragraph_count
        assert odt_empty_paragraph_count(ODT) >= 0


class TestOdtWordsPerHeading:
    def test_returns_float(self):
        from odt import odt_words_per_heading
        assert isinstance(odt_words_per_heading(ODT), float)

    def test_non_negative(self):
        from odt import odt_words_per_heading
        assert odt_words_per_heading(ODT) >= 0.0


# --- ZST ---

class TestZstSmallestFrameRatio:
    def test_returns_float(self):
        from zst import zst_smallest_frame_ratio
        assert isinstance(zst_smallest_frame_ratio(ZST), float)

    def test_in_range(self):
        from zst import zst_smallest_frame_ratio
        assert 0.0 <= zst_smallest_frame_ratio(ZST) <= 1.0


class TestZstFrameCountIsOne:
    def test_returns_bool(self):
        from zst import zst_frame_count_is_one
        assert isinstance(zst_frame_count_is_one(ZST), bool)


# --- FODG ---

class TestFodgTextPerShape:
    def test_returns_float(self):
        from fodg import fodg_text_per_shape
        assert isinstance(fodg_text_per_shape(FODG), float)

    def test_non_negative(self):
        from fodg import fodg_text_per_shape
        assert fodg_text_per_shape(FODG) >= 0.0


class TestFodgNonemptyPageCount:
    def test_returns_int(self):
        from fodg import fodg_nonempty_page_count
        assert isinstance(fodg_nonempty_page_count(FODG), int)

    def test_non_negative(self):
        from fodg import fodg_nonempty_page_count
        assert fodg_nonempty_page_count(FODG) >= 0


# --- QOI ---

class TestQoiBrightnessRange:
    def test_returns_int(self):
        from qoi import qoi_brightness_range
        assert isinstance(qoi_brightness_range(QOI), int)

    def test_non_negative(self):
        from qoi import qoi_brightness_range
        assert qoi_brightness_range(QOI) >= 0


class TestQoiIsSmall:
    def test_returns_bool(self):
        from qoi import qoi_is_small
        assert isinstance(qoi_is_small(QOI), bool)
