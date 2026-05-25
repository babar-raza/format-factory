"""
test_r65_fodt_advancement.py -- R65 Train H: FODT product advancement.

New capabilities added in R65:
1. document_footnote_endnote_summary(document) -- footnote/endnote/inline note summary
2. document_image_frame_list(document)          -- image frame inventory

These extend R64 capabilities (document_table_cell_span_summary,
document_text_field_warnings) with note analysis and image frame detection.

R65 Sprint: Train H -- FODT product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_footnote_endnote_summary,
    document_image_frame_list,
)


# ---------------------------------------------------------------------------
# Minimal document builders
# ---------------------------------------------------------------------------

def _make_document(blocks=None, tables=None, lists=None, content=None) -> dict:
    doc = {
        "blocks": blocks or [],
        "tables": tables or [],
        "lists": lists or [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }
    if content is not None:
        doc["content"] = content
    return doc


# ---------------------------------------------------------------------------
# document_footnote_endnote_summary tests
# ---------------------------------------------------------------------------

class TestDocumentFootnoteEndnoteSummary:
    """Tests for document_footnote_endnote_summary()."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_footnote_endnote_summary(doc)
        assert result["footnote_count"] == 0
        assert result["endnote_count"] == 0
        assert result["inline_note_count"] == 0
        assert result["total"] == 0
        assert result["has_notes"] is False

    def test_footnotes_only(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "Text with note",
             "footnotes": [{"id": "fn1", "text": "A footnote"}]},
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["footnote_count"] == 1
        assert result["endnote_count"] == 0
        assert result["total"] == 1
        assert result["has_notes"] is True

    def test_endnotes_only(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "Ref",
             "endnotes": [{"id": "en1"}, {"id": "en2"}]},
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["endnote_count"] == 2
        assert result["footnote_count"] == 0
        assert result["total"] == 2

    def test_inline_notes(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "Body",
             "inline_notes": [{"text": "side note"}]},
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["inline_note_count"] == 1

    def test_mixed_note_types(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "A",
             "footnotes": [{"id": "fn1"}],
             "endnotes": [{"id": "en1"}],
             "inline_notes": [{"text": "x"}]},
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["footnote_count"] == 1
        assert result["endnote_count"] == 1
        assert result["inline_note_count"] == 1
        assert result["total"] == 3

    def test_run_level_footnote_markers(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "",
             "runs": [{"text": "1", "note_class": "footnote"}]},
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["footnote_count"] == 1

    def test_run_level_endnote_markers(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "",
             "runs": [{"text": "i", "note_class": "endnote"}]},
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["endnote_count"] == 1

    def test_api_accessible_from_package(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_footnote_endnote_summary")
        assert callable(fodt.document_footnote_endnote_summary)
        assert "document_footnote_endnote_summary" in fodt.__all__


# ---------------------------------------------------------------------------
# document_image_frame_list tests
# ---------------------------------------------------------------------------

class TestDocumentImageFrameList:
    """Tests for document_image_frame_list()."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_image_frame_list(doc)
        assert result == []

    def test_no_images(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "plain text"},
        ])
        result = document_image_frame_list(doc)
        assert result == []

    def test_block_with_frames(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "frames": [
                {"name": "Logo", "anchor_type": "paragraph", "image_href": "Pictures/logo.png"},
            ]},
        ])
        result = document_image_frame_list(doc)
        assert len(result) == 1
        assert result[0]["frame_name"] == "Logo"
        assert result[0]["anchor_type"] == "paragraph"
        assert result[0]["image_href"] == "Pictures/logo.png"

    def test_odf_namespace_attributes(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "frames": [
                {"draw:name": "Chart1", "text:anchor-type": "char",
                 "xlink:href": "Pictures/chart.svg"},
            ]},
        ])
        result = document_image_frame_list(doc)
        assert len(result) == 1
        assert result[0]["frame_name"] == "Chart1"
        assert result[0]["anchor_type"] == "char"
        assert result[0]["image_href"] == "Pictures/chart.svg"

    def test_images_list_in_block(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "images": [
                {"name": "Photo", "anchor_type": "as-char", "image_href": "img.jpg"},
            ]},
        ])
        result = document_image_frame_list(doc)
        assert len(result) == 1
        assert result[0]["frame_name"] == "Photo"

    def test_images_in_table_cells(self):
        doc = _make_document(tables=[{
            "rows": [{"cells": [
                {"text": "", "frames": [
                    {"name": "CellImg", "anchor_type": "paragraph", "image_href": "cell.png"},
                ]},
            ]}],
        }])
        result = document_image_frame_list(doc)
        assert len(result) == 1
        assert result[0]["frame_name"] == "CellImg"

    def test_multiple_frames(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "frames": [
                {"name": "Img1", "anchor_type": "paragraph", "image_href": "a.png"},
                {"name": "Img2", "anchor_type": "char", "image_href": "b.png"},
            ]},
        ])
        result = document_image_frame_list(doc)
        assert len(result) == 2
        assert result[0]["frame_name"] == "Img1"
        assert result[1]["frame_name"] == "Img2"

    def test_api_accessible_from_package(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_image_frame_list")
        assert callable(fodt.document_image_frame_list)
        assert "document_image_frame_list" in fodt.__all__
