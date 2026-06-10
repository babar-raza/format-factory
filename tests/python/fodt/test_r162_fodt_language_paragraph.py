"""
test_r162_fodt_language_paragraph.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT24-001
Added: 2026-06-10

Tests for FODT APIs:
- document_language_list(document) -> list[str]
- document_paragraph_count(document) -> int
- document_append_paragraph(document, text, style) -> (bool, str)
- document_remove_paragraph(document, block_idx) -> (bool, str)

Authority: P4 (FODT ODF 1.3 flat text document)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_language_list,
    document_paragraph_count,
    document_append_paragraph,
    document_remove_paragraph,
)


def _block(text, btype="paragraph", style=None, lang=None):
    run = {"text": text}
    if lang:
        run["language"] = lang
    b = {"type": btype, "runs": [run]}
    if style:
        b["style"] = style
    return b


def _doc(blocks, meta=None, default_language=None):
    d = {"blocks": list(blocks)}
    if meta:
        d["meta"] = meta
    if default_language:
        d["default_language"] = default_language
    return d


# --- document_language_list tests ---

class TestDocumentLanguageList:

    def test_empty_document(self):
        doc = _doc([])
        assert document_language_list(doc) == []

    def test_single_language_from_run(self):
        doc = _doc([_block("Hello", lang="en")])
        assert document_language_list(doc) == ["en"]

    def test_multiple_languages_sorted(self):
        doc = _doc([
            _block("Bonjour", lang="fr"),
            _block("Hello", lang="en"),
            _block("Hallo", lang="de"),
        ])
        result = document_language_list(doc)
        assert result == ["de", "en", "fr"]

    def test_deduplication(self):
        doc = _doc([
            _block("One", lang="en"),
            _block("Two", lang="en"),
        ])
        assert document_language_list(doc) == ["en"]

    def test_default_language_collected(self):
        doc = _doc([], default_language="es")
        assert document_language_list(doc) == ["es"]

    def test_meta_language_collected(self):
        doc = _doc([], meta={"language": "ja"})
        assert document_language_list(doc) == ["ja"]


# --- document_paragraph_count tests ---

class TestDocumentParagraphCount:

    def test_empty(self):
        doc = _doc([])
        assert document_paragraph_count(doc) == 0

    def test_only_paragraphs(self):
        doc = _doc([_block("a"), _block("b"), _block("c")])
        assert document_paragraph_count(doc) == 3

    def test_mixed_block_types(self):
        doc = _doc([
            _block("Para 1"),
            _block("Heading", btype="heading"),
            _block("Para 2"),
            {"type": "table", "rows": []},
        ])
        assert document_paragraph_count(doc) == 2

    def test_heading_not_counted(self):
        doc = _doc([_block("H1", btype="heading")])
        assert document_paragraph_count(doc) == 0


# --- document_append_paragraph tests ---

class TestDocumentAppendParagraph:

    def test_append_basic(self):
        doc = _doc([_block("Existing")])
        ok, msg = document_append_paragraph(doc, "New paragraph")
        assert ok is True
        assert len(doc["blocks"]) == 2
        assert doc["blocks"][-1]["runs"][0]["text"] == "New paragraph"

    def test_append_with_style(self):
        doc = _doc([])
        ok, msg = document_append_paragraph(doc, "Styled", style="Heading 1")
        assert ok is True
        assert doc["blocks"][0]["style"] == "Heading 1"

    def test_append_none_text_fails(self):
        doc = _doc([])
        ok, msg = document_append_paragraph(doc, None)
        assert ok is False

    def test_append_empty_string_succeeds(self):
        doc = _doc([])
        ok, msg = document_append_paragraph(doc, "")
        assert ok is True
        assert len(doc["blocks"]) == 1


# --- document_remove_paragraph tests ---

class TestDocumentRemoveParagraph:

    def test_remove_paragraph(self):
        doc = _doc([_block("Keep"), _block("Remove"), _block("Also keep")])
        ok, msg = document_remove_paragraph(doc, 1)
        assert ok is True
        assert len(doc["blocks"]) == 2
        assert doc["blocks"][0]["runs"][0]["text"] == "Keep"
        assert doc["blocks"][1]["runs"][0]["text"] == "Also keep"

    def test_remove_out_of_range(self):
        doc = _doc([_block("Only")])
        ok, msg = document_remove_paragraph(doc, 5)
        assert ok is False

    def test_remove_table_blocked(self):
        doc = _doc([{"type": "table", "rows": []}])
        ok, msg = document_remove_paragraph(doc, 0)
        assert ok is False
        assert "table" in msg.lower()

    def test_remove_heading_allowed(self):
        doc = _doc([_block("Title", btype="heading")])
        ok, msg = document_remove_paragraph(doc, 0)
        assert ok is True
        assert len(doc["blocks"]) == 0
