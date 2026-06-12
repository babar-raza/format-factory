"""
test_r178_fodt_document_ops.py -- Tests for FODT document paragraph operations.

Coverage:
  - document_paragraph_count: returns int, counts only paragraphs
  - document_append_paragraph: success return, modifies blocks, style param, None guard
  - document_remove_paragraph: removes block, handles invalid index
  - document_get_paragraph_text: returns text, handles out of range

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_paragraph_count,
    document_append_paragraph,
    document_remove_paragraph,
    document_get_paragraph_text,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")


def get_doc():
    return parse_fodt(_MINIMAL)


# ---------------------------------------------------------------------------
# document_paragraph_count tests
# ---------------------------------------------------------------------------

class TestDocumentParagraphCount:
    def test_returns_int(self):
        doc = get_doc()
        result = document_paragraph_count(doc)
        assert isinstance(result, int)

    def test_non_negative(self):
        doc = get_doc()
        assert document_paragraph_count(doc) >= 0

    def test_empty_doc_returns_zero(self):
        doc = {"blocks": []}
        assert document_paragraph_count(doc) == 0

    def test_counts_only_paragraphs(self):
        doc = {
            "blocks": [
                {"type": "paragraph", "text": "p1"},
                {"type": "heading", "text": "h1"},
                {"type": "paragraph", "text": "p2"},
                {"type": "table", "rows": []},
            ]
        }
        assert document_paragraph_count(doc) == 2


# ---------------------------------------------------------------------------
# document_append_paragraph tests
# ---------------------------------------------------------------------------

class TestDocumentAppendParagraph:
    def test_returns_tuple(self):
        doc = get_doc()
        result = document_append_paragraph(doc, "New paragraph")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_success_is_true(self):
        doc = get_doc()
        ok, msg = document_append_paragraph(doc, "Hello world")
        assert ok is True

    def test_message_is_string(self):
        doc = get_doc()
        ok, msg = document_append_paragraph(doc, "Hello world")
        assert isinstance(msg, str)

    def test_increases_block_count(self):
        doc = get_doc()
        before = len(doc.get("blocks", []))
        document_append_paragraph(doc, "appended")
        after = len(doc.get("blocks", []))
        assert after == before + 1

    def test_appended_text_in_blocks(self):
        doc = get_doc()
        document_append_paragraph(doc, "unique_sentinel_text_xyz")
        runs = doc["blocks"][-1].get("runs", [])
        texts = [r.get("text", "") for r in runs]
        assert "unique_sentinel_text_xyz" in texts

    def test_with_style(self):
        doc = get_doc()
        ok, msg = document_append_paragraph(doc, "styled para", style="Heading 2")
        assert ok is True
        assert doc["blocks"][-1].get("style") == "Heading 2"

    def test_none_text_returns_false(self):
        doc = get_doc()
        ok, msg = document_append_paragraph(doc, None)
        assert ok is False


# ---------------------------------------------------------------------------
# document_remove_paragraph tests
# ---------------------------------------------------------------------------

class TestDocumentRemoveParagraph:
    def test_returns_tuple(self):
        doc = get_doc()
        document_append_paragraph(doc, "to remove")
        idx = len(doc["blocks"]) - 1
        result = document_remove_paragraph(doc, idx)
        assert isinstance(result, tuple)

    def test_success_removes_block(self):
        doc = get_doc()
        document_append_paragraph(doc, "will be removed")
        before = len(doc["blocks"])
        ok, msg = document_remove_paragraph(doc, before - 1)
        assert ok is True
        assert len(doc["blocks"]) == before - 1

    def test_out_of_range_returns_false(self):
        doc = get_doc()
        ok, msg = document_remove_paragraph(doc, 9999)
        assert ok is False

    def test_negative_index_returns_false(self):
        doc = {"blocks": [{"type": "paragraph", "text": "p"}]}
        ok, msg = document_remove_paragraph(doc, -1)
        assert ok is False


# ---------------------------------------------------------------------------
# document_get_paragraph_text tests
# ---------------------------------------------------------------------------

class TestDocumentGetParagraphText:
    def test_out_of_range_returns_none(self):
        doc = get_doc()
        result = document_get_paragraph_text(doc, 99999)
        assert result is None

    def test_negative_index_returns_none(self):
        doc = get_doc()
        result = document_get_paragraph_text(doc, -1)
        assert result is None

    def test_empty_blocks_returns_none(self):
        doc = {"blocks": []}
        result = document_get_paragraph_text(doc, 0)
        assert result is None

    def test_single_paragraph_index_zero(self):
        doc = {"blocks": [{"type": "paragraph", "text": "hello para"}]}
        result = document_get_paragraph_text(doc, 0)
        assert result == "hello para"

    def test_skips_non_paragraph_blocks(self):
        doc = {
            "blocks": [
                {"type": "heading", "text": "heading"},
                {"type": "paragraph", "text": "second"},
            ]
        }
        result = document_get_paragraph_text(doc, 0)
        assert result == "second"
