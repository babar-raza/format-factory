"""Behavioral tests for FODT spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.fodt.Compat import FodtDocument, FodtParagraph, FodtHeading
from src.python.fodt.spec.office.document import Document as SpecDocument
from src.python.fodt.spec.text.paragraph import Paragraph as SpecParagraph
from src.python.fodt.spec.text.heading import Heading as SpecHeading


_SAMPLE_DOC = {
    "format_id": "fodt",
    "odf_version": "1.3",
    "blocks": ["p1", "p2", "p3", "p4", "p5"],  # block_count reads from 'blocks' list
    "table_count": 1,
    "warnings": [],
}
_SAMPLE_PARA = {"kind": "text:p", "text": "Hello world", "style_name": "Default", "outline_level": 0, "spans": []}
_SAMPLE_HEADING = {"kind": "text:h", "text": "Chapter 1", "style_name": "Heading1", "outline_level": 1, "spans": []}


class TestFodtDocumentMetadata:
    def test_spec_qname(self):
        assert FodtDocument.spec_qname == "office:document"

    def test_spec_fact_ref(self):
        assert "FACT-FODT" in FodtDocument.spec_fact_ref

    def test_namespace_uri_present(self):
        assert "oasis" in FodtDocument.namespace_uri


class TestFodtDocumentBehavior:
    def test_instantiation(self):
        doc = FodtDocument(_SAMPLE_DOC)
        assert doc is not None

    def test_block_count(self):
        doc = FodtDocument(_SAMPLE_DOC)
        assert doc.block_count == 5

    def test_to_dict(self):
        doc = FodtDocument(_SAMPLE_DOC)
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        doc = FodtDocument(_SAMPLE_DOC)
        assert repr(doc)

    def test_inherits_spec_class(self):
        doc = FodtDocument(_SAMPLE_DOC)
        assert isinstance(doc, SpecDocument)


class TestFodtParagraphBehavior:
    def test_instantiation(self):
        p = FodtParagraph(_SAMPLE_PARA)
        assert p is not None

    def test_spec_qname(self):
        assert FodtParagraph.spec_qname == "text:p"

    def test_text_property(self):
        p = FodtParagraph(_SAMPLE_PARA)
        assert p.text == "Hello world"

    def test_inherits_spec_class(self):
        p = FodtParagraph(_SAMPLE_PARA)
        assert isinstance(p, SpecParagraph)

    def test_repr_nonempty(self):
        p = FodtParagraph(_SAMPLE_PARA)
        assert repr(p)


class TestFodtHeadingBehavior:
    def test_instantiation(self):
        h = FodtHeading(_SAMPLE_HEADING)
        assert h is not None

    def test_spec_qname(self):
        assert FodtHeading.spec_qname == "text:h"

    def test_text_property(self):
        h = FodtHeading(_SAMPLE_HEADING)
        assert h.text == "Chapter 1"

    def test_outline_level(self):
        h = FodtHeading(_SAMPLE_HEADING)
        assert h.outline_level == 1

    def test_inherits_spec_class(self):
        h = FodtHeading(_SAMPLE_HEADING)
        assert isinstance(h, SpecHeading)

    def test_repr_nonempty(self):
        h = FodtHeading(_SAMPLE_HEADING)
        assert repr(h)
