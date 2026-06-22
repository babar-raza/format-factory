"""Behavioral tests for ODT spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.odt.Compat import OdtDocument, OdtParagraph, OdtHeading
from src.python.odt.spec.office.document import Document as SpecDocument
from src.python.odt.spec.text.paragraph import Paragraph as SpecParagraph
from src.python.odt.spec.text.heading import Heading as SpecHeading


_SAMPLE_DOC = {
    "paragraph_count": 3,
    "heading_count": 1,
    "paragraphs": ["Hello world", "Second paragraph", "Third"],
    "headings": [{"text": "Title", "level": 1}],
    "is_ok": True,
}
_SAMPLE_PARA = {"text": "Hello world", "style": "Default"}
_SAMPLE_HEADING = {"text": "Chapter 1", "level": 2}


class TestOdtDocumentMetadata:
    def test_spec_qname(self):
        assert OdtDocument.spec_qname == "office:document"

    def test_spec_fact_ref(self):
        assert "FACT-ODT" in OdtDocument.spec_fact_ref

    def test_namespace_uri_present(self):
        assert "oasis" in OdtDocument.namespace_uri


class TestOdtDocumentBehavior:
    def test_instantiation(self):
        doc = OdtDocument(_SAMPLE_DOC)
        assert doc is not None

    def test_paragraph_count(self):
        doc = OdtDocument(_SAMPLE_DOC)
        assert doc.paragraph_count == 3

    def test_heading_count(self):
        doc = OdtDocument(_SAMPLE_DOC)
        assert doc.heading_count == 1

    def test_to_dict(self):
        doc = OdtDocument(_SAMPLE_DOC)
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        doc = OdtDocument(_SAMPLE_DOC)
        assert repr(doc)

    def test_inherits_spec_class(self):
        doc = OdtDocument(_SAMPLE_DOC)
        assert isinstance(doc, SpecDocument)


class TestOdtParagraphBehavior:
    def test_instantiation(self):
        p = OdtParagraph(_SAMPLE_PARA)
        assert p is not None

    def test_spec_qname(self):
        assert OdtParagraph.spec_qname == "text:p"

    def test_text_property(self):
        p = OdtParagraph(_SAMPLE_PARA)
        assert p.text == "Hello world"

    def test_word_count(self):
        p = OdtParagraph(_SAMPLE_PARA)
        assert p.word_count == 2

    def test_inherits_spec_class(self):
        p = OdtParagraph(_SAMPLE_PARA)
        assert isinstance(p, SpecParagraph)

    def test_repr_nonempty(self):
        p = OdtParagraph(_SAMPLE_PARA)
        assert repr(p)


class TestOdtHeadingBehavior:
    def test_instantiation(self):
        h = OdtHeading(_SAMPLE_HEADING)
        assert h is not None

    def test_spec_qname(self):
        assert OdtHeading.spec_qname == "text:h"

    def test_text_property(self):
        h = OdtHeading(_SAMPLE_HEADING)
        assert h.text == "Chapter 1"

    def test_level_property(self):
        h = OdtHeading(_SAMPLE_HEADING)
        assert h.level == 2

    def test_inherits_spec_class(self):
        h = OdtHeading(_SAMPLE_HEADING)
        assert isinstance(h, SpecHeading)

    def test_repr_nonempty(self):
        h = OdtHeading(_SAMPLE_HEADING)
        assert repr(h)
