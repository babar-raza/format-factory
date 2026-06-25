"""Behavioral tests for ABW spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.abw.Compat import AbwDocument, AbwParagraph
from src.python.abw.spec.document.document import Document as SpecDocument
from src.python.abw.spec.document.paragraph import Paragraph as SpecParagraph


_SAMPLE_DOC = {
    "is_abw": True,
    "section_count": 2,
    "paragraph_count": 3,
    "paragraphs": ["Hello world", "Foo bar", "Baz"],
}


class TestAbwDocumentMetadata:
    def test_spec_qname(self):
        assert AbwDocument.spec_qname == "abiword:document"

    def test_spec_fact_ref(self):
        assert AbwDocument.spec_fact_ref == "FACT-ABW-001"

    def test_namespace_uri(self):
        assert "abisource" in AbwDocument.namespace_uri


class TestAbwDocumentBehavior:
    def test_instantiation(self):
        doc = AbwDocument(_SAMPLE_DOC)
        assert doc is not None

    def test_is_abw_property(self):
        doc = AbwDocument(_SAMPLE_DOC)
        assert doc.is_abw is True

    def test_paragraph_count(self):
        doc = AbwDocument(_SAMPLE_DOC)
        assert doc.paragraph_count == 3

    def test_paragraphs_method_returns_list(self):
        doc = AbwDocument(_SAMPLE_DOC)
        # paragraphs() is a method on the Compat class, not a property
        assert isinstance(doc.paragraphs(), list)

    def test_to_dict(self):
        doc = AbwDocument(_SAMPLE_DOC)
        d = doc.to_dict()
        assert isinstance(d, dict)
        assert "paragraph_count" in d

    def test_repr_nonempty(self):
        doc = AbwDocument(_SAMPLE_DOC)
        assert repr(doc)

    def test_inherits_spec_class(self):
        doc = AbwDocument(_SAMPLE_DOC)
        assert isinstance(doc, SpecDocument)


class TestAbwParagraphBehavior:
    def test_instantiation(self):
        p = AbwParagraph("Hello world")
        assert p is not None

    def test_spec_qname(self):
        assert AbwParagraph.spec_qname == "abiword:p"

    def test_text_property(self):
        p = AbwParagraph("Hello world")
        assert p.text == "Hello world"

    def test_word_count(self):
        p = AbwParagraph("Hello world")
        assert p.word_count == 2

    def test_inherits_spec_class(self):
        p = AbwParagraph("test")
        assert isinstance(p, SpecParagraph)

    def test_repr_nonempty(self):
        p = AbwParagraph("test")
        assert repr(p)
