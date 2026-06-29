"""
tests/python/fodp/test_r299_fodp_iter_slides.py

Sprint: ff-sprint-s299-fodp-slide-iterator-20260626
Authority: ODF 1.3 §9.1.4 — draw:page (presentation slide)

Tests for fodp_iter_slides() in fodp_slide_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_TWO_SLIDES = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"


class TestFodpIterSlidesImport:
    def test_importable_from_fodp_slide_iterator(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        assert callable(fodp_iter_slides)

    def test_importable_from_package(self):
        import fodp
        assert hasattr(fodp, "fodp_iter_slides")


class TestFodpIterSlidesOutput:
    def test_returns_iterator(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        result = fodp_iter_slides(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_slides(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        slides = list(fodp_iter_slides(str(_MINIMAL)))
        assert len(slides) >= 1

    def test_slide_type_is_spec_page(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        from fodp.spec.draw.page import Page
        slides = list(fodp_iter_slides(str(_MINIMAL)))
        assert all(isinstance(s, Page) for s in slides)

    def test_slide_has_spec_qname(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        slides = list(fodp_iter_slides(str(_MINIMAL)))
        assert all(hasattr(s, "spec_qname") for s in slides)

    def test_slide_qname_value(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        slides = list(fodp_iter_slides(str(_MINIMAL)))
        assert all(s.spec_qname == "presentation:page" for s in slides)

    def test_slide_has_name(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        slides = list(fodp_iter_slides(str(_MINIMAL)))
        for s in slides:
            assert isinstance(s.name, str)

    def test_two_slide_doc(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        slides = list(fodp_iter_slides(str(_TWO_SLIDES)))
        assert len(slides) >= 2

    def test_consistent(self):
        from fodp.fodp_slide_iterator import fodp_iter_slides
        r1 = list(fodp_iter_slides(str(_MINIMAL)))
        r2 = list(fodp_iter_slides(str(_MINIMAL)))
        assert len(r1) == len(r2)
