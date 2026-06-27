"""
tests/python/fodg/test_r298_fodg_iter_pages.py

Sprint: ff-sprint-s298-fodg-page-iterator-20260626
Authority: ODF 1.3 §9.1.4 — draw:page

Tests for fodg_iter_pages() in fodg_page_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
_EMPTY = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"


class TestFodgIterPagesImport:
    def test_importable_from_fodg_page_iterator(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        assert callable(fodg_iter_pages)

    def test_importable_from_package(self):
        import fodg
        assert hasattr(fodg, "fodg_iter_pages")


class TestFodgIterPagesOutput:
    def test_returns_iterator(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        result = fodg_iter_pages(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_pages(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        pages = list(fodg_iter_pages(str(_MINIMAL)))
        assert len(pages) >= 1

    def test_page_type_is_spec_page(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        from fodg.spec.draw.page import Page
        pages = list(fodg_iter_pages(str(_MINIMAL)))
        assert all(isinstance(p, Page) for p in pages)

    def test_page_has_spec_qname(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        pages = list(fodg_iter_pages(str(_MINIMAL)))
        assert all(hasattr(p, "spec_qname") for p in pages)

    def test_page_qname_value(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        pages = list(fodg_iter_pages(str(_MINIMAL)))
        assert all(p.spec_qname == "draw:page" for p in pages)

    def test_page_has_name(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        pages = list(fodg_iter_pages(str(_MINIMAL)))
        for p in pages:
            assert isinstance(p.name, str)

    def test_page_has_shape_count(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        pages = list(fodg_iter_pages(str(_MINIMAL)))
        for p in pages:
            assert isinstance(p.shape_count, int) and p.shape_count >= 0

    def test_consistent(self):
        from fodg.fodg_page_iterator import fodg_iter_pages
        r1 = list(fodg_iter_pages(str(_MINIMAL)))
        r2 = list(fodg_iter_pages(str(_MINIMAL)))
        assert len(r1) == len(r2)
