"""Tests for FODT document_to_html export.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Covers: HTML export from FODT documents
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_to_html


def _make_doc(blocks):
    return {"blocks": blocks}


class TestDocumentToHtml:
    def test_basic_paragraphs(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "Hello world"},
            {"type": "paragraph", "text": "Second paragraph"},
        ])
        html = document_to_html(doc)
        assert "<p>Hello world</p>" in html
        assert "<p>Second paragraph</p>" in html

    def test_headings(self):
        doc = _make_doc([
            {"type": "heading", "text": "Title", "level": 1},
            {"type": "heading", "text": "Section", "level": 2},
        ])
        html = document_to_html(doc)
        assert "<h1>Title</h1>" in html
        assert "<h2>Section</h2>" in html

    def test_mixed_blocks(self):
        doc = _make_doc([
            {"type": "heading", "text": "Intro", "level": 1},
            {"type": "paragraph", "text": "Body text"},
        ])
        html = document_to_html(doc)
        assert "<h1>Intro</h1>" in html
        assert "<p>Body text</p>" in html

    def test_html_escaping(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "a < b & c > d"},
        ])
        html = document_to_html(doc)
        assert "&lt;" in html
        assert "&amp;" in html
        assert "&gt;" in html

    def test_empty_document(self):
        doc = _make_doc([])
        html = document_to_html(doc)
        assert "<body>" in html
        assert "</body>" in html

    def test_has_doctype(self):
        doc = _make_doc([{"type": "paragraph", "text": "X"}])
        html = document_to_html(doc)
        assert html.startswith("<!DOCTYPE html>")

    def test_heading_level_clamped(self):
        doc = _make_doc([
            {"type": "heading", "text": "Deep", "level": 10},
        ])
        html = document_to_html(doc)
        assert "<h6>Deep</h6>" in html

    def test_default_heading_level(self):
        doc = _make_doc([
            {"type": "heading", "text": "No level"},
        ])
        html = document_to_html(doc)
        assert "<h1>No level</h1>" in html
