"""
tests/python/fodt/test_r301_fodt_iter_paragraphs.py

Sprint: ff-sprint-s301-fodt-paragraph-iterator-20260626
Authority: ODF 1.3 §5.1.3 — text:p

Tests for fodt_iter_paragraphs() in fodt_paragraph_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_HEADINGS = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


class TestFodtIterParagraphsImport:
    def test_importable_from_fodt_paragraph_iterator(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        assert callable(fodt_iter_paragraphs)

    def test_importable_from_package(self):
        import fodt
        assert hasattr(fodt, "fodt_iter_paragraphs")


class TestFodtIterParagraphsOutput:
    def test_returns_iterator(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        result = fodt_iter_paragraphs(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_paragraphs(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        paras = list(fodt_iter_paragraphs(str(_MINIMAL)))
        assert len(paras) >= 1

    def test_paragraph_type_is_spec_paragraph(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        from fodt.spec.text.paragraph import Paragraph
        paras = list(fodt_iter_paragraphs(str(_MINIMAL)))
        assert all(isinstance(p, Paragraph) for p in paras)

    def test_paragraph_has_spec_qname(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        paras = list(fodt_iter_paragraphs(str(_MINIMAL)))
        assert all(hasattr(p, "spec_qname") for p in paras)

    def test_paragraph_qname_value(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        paras = list(fodt_iter_paragraphs(str(_MINIMAL)))
        assert all(p.spec_qname == "text:p" for p in paras)

    def test_paragraph_has_text(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        paras = list(fodt_iter_paragraphs(str(_MINIMAL)))
        for p in paras:
            assert isinstance(p.text, str)

    def test_headings_file_yields_multiple(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        paras = list(fodt_iter_paragraphs(str(_HEADINGS)))
        assert len(paras) >= 2

    def test_consistent(self):
        from fodt.fodt_paragraph_iterator import fodt_iter_paragraphs
        r1 = list(fodt_iter_paragraphs(str(_MINIMAL)))
        r2 = list(fodt_iter_paragraphs(str(_MINIMAL)))
        assert len(r1) == len(r2)
