"""Tests for FODT domain classes (FodtDocument, FodtParagraph, FodtSpan).

TC-GAP-B01: Proves domain classes wrap the dict-based neutral model correctly.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.models import FodtDocument, FodtParagraph, FodtSpan


def _sample_document():
    return {
        "format_id": "fodt",
        "odf_version": "1.3",
        "warnings": [],
        "blocks": [
            {
                "kind": "heading",
                "text": "Title",
                "style_name": "Heading_20_1",
                "outline_level": 1,
                "spans": [],
            },
            {
                "kind": "paragraph",
                "text": "Hello world",
                "style_name": "Standard",
                "spans": [
                    {"text": "Hello ", "style_name": ""},
                    {"text": "world", "style_name": "Bold"},
                ],
            },
        ],
        "tables": [{"name": "Table1"}],
        "lists": [],
    }


class TestFodtDocument:
    def test_basic_properties(self):
        doc = FodtDocument(_sample_document())
        assert doc.format_id == "fodt"
        assert doc.odf_version == "1.3"
        assert doc.block_count == 2
        assert doc.table_count == 1
        assert doc.list_count == 0

    def test_paragraphs_returns_objects(self):
        doc = FodtDocument(_sample_document())
        paras = doc.paragraphs()
        assert len(paras) == 2
        assert isinstance(paras[0], FodtParagraph)

    def test_headings_filter(self):
        doc = FodtDocument(_sample_document())
        headings = doc.headings()
        assert len(headings) == 1
        assert headings[0].kind == "heading"
        assert headings[0].outline_level == 1


class TestFodtParagraph:
    def test_paragraph_properties(self):
        p = FodtParagraph(_sample_document()["blocks"][1])
        assert p.kind == "paragraph"
        assert p.text == "Hello world"
        assert p.style_name == "Standard"

    def test_spans(self):
        p = FodtParagraph(_sample_document()["blocks"][1])
        spans = p.spans
        assert len(spans) == 2
        assert isinstance(spans[0], FodtSpan)
        assert spans[1].text == "world"
        assert spans[1].style_name == "Bold"


class TestFodtSpan:
    def test_span_properties(self):
        s = FodtSpan({"text": "test", "style_name": "Italic"})
        assert s.text == "test"
        assert s.style_name == "Italic"
