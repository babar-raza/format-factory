"""
tests/python/odt/test_r297_odt_iter_paragraphs.py

Sprint: ff-sprint-s297-odt-paragraph-iterator-20260626
Authority: ODF 1.3 Part 3 — text:p paragraph

Tests for odt_iter_paragraphs() in odt_paragraph_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = _VALID_DIR / "minimal-document.odt"
_TWO_PARA = _VALID_DIR / "two-paragraphs.odt"


class TestOdtIterParagraphsImport:
    def test_importable_from_odt_paragraph_iterator(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        assert callable(odt_iter_paragraphs)

    def test_importable_from_package(self):
        import odt
        assert hasattr(odt, "odt_iter_paragraphs")


class TestOdtIterParagraphsOutput:
    def test_returns_iterator(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        result = odt_iter_paragraphs(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_paragraphs(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        paras = list(odt_iter_paragraphs(str(_MINIMAL)))
        assert len(paras) >= 1

    def test_paragraph_type_is_spec(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        from odt.spec.text.paragraph import Paragraph
        paras = list(odt_iter_paragraphs(str(_MINIMAL)))
        assert all(isinstance(p, Paragraph) for p in paras)

    def test_paragraph_has_spec_qname(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        paras = list(odt_iter_paragraphs(str(_MINIMAL)))
        assert all(hasattr(p, "spec_qname") for p in paras)

    def test_paragraph_qname_value(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        paras = list(odt_iter_paragraphs(str(_MINIMAL)))
        assert all(p.spec_qname == "text:p" for p in paras)

    def test_paragraph_has_text(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        paras = list(odt_iter_paragraphs(str(_MINIMAL)))
        for p in paras:
            assert isinstance(p.text, str)

    def test_two_paragraph_doc(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        paras = list(odt_iter_paragraphs(str(_TWO_PARA)))
        assert len(paras) >= 2

    def test_consistent(self):
        from odt.odt_paragraph_iterator import odt_iter_paragraphs
        r1 = list(odt_iter_paragraphs(str(_MINIMAL)))
        r2 = list(odt_iter_paragraphs(str(_MINIMAL)))
        assert len(r1) == len(r2)
