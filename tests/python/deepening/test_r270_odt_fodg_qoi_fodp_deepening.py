"""Sprint 18: ODT/FODG/QOI/FODP product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODT = str(next((_REPO / "samples" / "by-format" / "odt" / "valid").glob("*.odt")))
FODG = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
QOI = str(next((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi")))
FODP = str(_REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp")


# --- ODT ---

class TestOdtListToParagraphRatio:
    def test_returns_float(self):
        from odt import odt_list_to_paragraph_ratio
        result = odt_list_to_paragraph_ratio(ODT)
        assert isinstance(result, float)

    def test_ratio_non_negative(self):
        from odt import odt_list_to_paragraph_ratio
        assert odt_list_to_paragraph_ratio(ODT) >= 0.0


class TestOdtHasLists:
    def test_returns_bool(self):
        from odt import odt_has_lists
        result = odt_has_lists(ODT)
        assert isinstance(result, bool)


# --- FODG ---

class TestFodgEmptyPageCount:
    def test_returns_int(self):
        from fodg import fodg_empty_page_count
        result = fodg_empty_page_count(FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        from fodg import fodg_empty_page_count
        assert fodg_empty_page_count(FODG) >= 0


class TestFodgIsSinglePage:
    def test_returns_bool(self):
        from fodg import fodg_is_single_page
        result = fodg_is_single_page(FODG)
        assert isinstance(result, bool)


# --- QOI ---

class TestQoiIsPortrait:
    def test_returns_bool(self):
        from qoi import qoi_is_portrait
        result = qoi_is_portrait(QOI)
        assert isinstance(result, bool)


class TestQoiMaxDimension:
    def test_returns_int(self):
        from qoi import qoi_max_dimension
        result = qoi_max_dimension(QOI)
        assert isinstance(result, int)

    def test_positive(self):
        from qoi import qoi_max_dimension
        assert qoi_max_dimension(QOI) > 0


# --- FODP ---

class TestFodpIsSingleSlide:
    def test_returns_bool(self):
        from fodp import fodp_is_single_slide
        result = fodp_is_single_slide(FODP)
        assert isinstance(result, bool)


class TestFodpNotesDensity:
    def test_returns_float(self):
        from fodp import fodp_notes_density
        result = fodp_notes_density(FODP)
        assert isinstance(result, float)

    def test_non_negative(self):
        from fodp import fodp_notes_density
        assert fodp_notes_density(FODP) >= 0.0
