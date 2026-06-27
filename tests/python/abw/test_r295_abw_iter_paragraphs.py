"""
tests/python/abw/test_r295_abw_iter_paragraphs.py

Sprint: ff-sprint-s295-abw-paragraph-iterator-20260626
Authority: AbiWord AWML 1.0 document format

Tests for abw_iter_paragraphs() in abw_paragraph_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_TWO_PARA = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"


class TestAbwIterParagraphsImport:
    def test_importable_from_abw_paragraph_iterator(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        assert callable(abw_iter_paragraphs)

    def test_importable_from_package(self):
        import abw
        assert hasattr(abw, "abw_iter_paragraphs")


class TestAbwIterParagraphsOutput:
    def test_returns_iterator(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        result = abw_iter_paragraphs(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_paragraph_type_is_spec_paragraph(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        from abw.spec.document.paragraph import Paragraph
        paras = list(abw_iter_paragraphs(str(_MINIMAL)))
        assert all(isinstance(p, Paragraph) for p in paras)

    def test_paragraph_has_spec_qname(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        paras = list(abw_iter_paragraphs(str(_MINIMAL)))
        assert all(hasattr(p, "spec_qname") for p in paras)

    def test_paragraph_qname_value(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        paras = list(abw_iter_paragraphs(str(_MINIMAL)))
        assert all(p.spec_qname == "abiword:p" for p in paras)

    def test_paragraph_has_text(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        paras = list(abw_iter_paragraphs(str(_MINIMAL)))
        for p in paras:
            assert isinstance(p.text, str)

    def test_two_paragraph_doc_yields_two(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        paras = list(abw_iter_paragraphs(str(_TWO_PARA)))
        assert len(paras) >= 2

    def test_consistent(self):
        from abw.abw_paragraph_iterator import abw_iter_paragraphs
        r1 = [p.text for p in abw_iter_paragraphs(str(_TWO_PARA))]
        r2 = [p.text for p in abw_iter_paragraphs(str(_TWO_PARA))]
        assert r1 == r2
