"""
test_r84_fodt_text_export.py

R84 Train I: Tests for new FODT APIs:
- document_to_text(document) -> str
- document_get_paragraph_text(document, paragraph_index) -> str | None

Sprint: FORMAT-FACTORY-R84-BROAD-CLOSURE-RAW-LOGS-FINAL-AUTHORITY-FODS-FODT-ZST-NEXTFORMAT-ADVANCEMENT-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import document_to_text, document_get_paragraph_text


def _make_doc(blocks=None):
    return {"blocks": blocks or [], "content": blocks or []}


def _para(text):
    return {"type": "paragraph", "text": text}


def _heading(text, level=1):
    return {"type": "heading", "text": text, "level": level}


class TestDocumentToText:
    def test_empty_document_returns_empty_string(self):
        doc = _make_doc()
        result = document_to_text(doc)
        assert result == ""

    def test_single_paragraph(self):
        doc = _make_doc([_para("Hello world")])
        result = document_to_text(doc)
        assert "Hello world" in result

    def test_heading_prefixed_with_hash(self):
        doc = _make_doc([_heading("My Title", level=1)])
        result = document_to_text(doc)
        assert "#" in result
        assert "My Title" in result

    def test_multiple_paragraphs_separated_by_newline(self):
        doc = _make_doc([_para("Para one"), _para("Para two")])
        result = document_to_text(doc)
        assert "Para one" in result
        assert "Para two" in result
        assert "\n" in result

    def test_mixed_content_headings_and_paragraphs(self):
        doc = _make_doc([
            _heading("Title", level=1),
            _para("First paragraph"),
            _heading("Section", level=2),
            _para("Second paragraph"),
        ])
        result = document_to_text(doc)
        assert "Title" in result
        assert "First paragraph" in result
        assert "Section" in result
        assert "Second paragraph" in result

    def test_returns_string_type(self):
        doc = _make_doc([_para("text")])
        result = document_to_text(doc)
        assert isinstance(result, str)


class TestDocumentGetParagraphText:
    def test_first_paragraph(self):
        doc = _make_doc([_para("first"), _para("second")])
        result = document_get_paragraph_text(doc, 0)
        assert result == "first"

    def test_second_paragraph(self):
        doc = _make_doc([_para("first"), _para("second")])
        result = document_get_paragraph_text(doc, 1)
        assert result == "second"

    def test_out_of_range_returns_none(self):
        doc = _make_doc([_para("only")])
        result = document_get_paragraph_text(doc, 5)
        assert result is None

    def test_empty_doc_returns_none(self):
        doc = _make_doc()
        result = document_get_paragraph_text(doc, 0)
        assert result is None

    def test_heading_not_counted_as_paragraph(self):
        doc = _make_doc([_heading("H1"), _para("actual_para")])
        # paragraph index 0 should be "actual_para", not the heading
        result = document_get_paragraph_text(doc, 0)
        assert result == "actual_para"

    def test_negative_index_returns_none(self):
        doc = _make_doc([_para("text")])
        result = document_get_paragraph_text(doc, -1)
        assert result is None
