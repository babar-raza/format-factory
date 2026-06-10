"""
test_r163_fodt_section_change_image.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT28-001
Added: 2026-06-10

Tests for FODT APIs:
- document_section_summary(document) -> dict
- document_change_tracking_summary(document) -> dict
- document_footnote_endnote_summary(document) -> dict
- document_image_frame_list(document) -> list[dict]

Authority: P4 (FODT neutral model)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_section_summary,
    document_change_tracking_summary,
    document_footnote_endnote_summary,
    document_image_frame_list,
)


def _block(text, btype="paragraph", **kwargs):
    b = {"type": btype, "text": text, "runs": [{"text": text}]}
    b.update(kwargs)
    return b


def _doc(blocks=None, **kwargs):
    d = {
        "format_id": "fodt",
        "blocks": blocks or [],
        "lists": [],
        "tables": [],
    }
    d.update(kwargs)
    return d


# ── document_section_summary ────────────────────────────────────────────

class TestDocumentSectionSummary:

    def test_empty_document(self):
        result = document_section_summary(_doc())
        assert result["section_count"] == 0
        assert result["section_names"] == []

    def test_explicit_sections(self):
        doc = _doc(sections=[
            {"name": "Introduction"},
            {"name": "Conclusion"},
        ])
        result = document_section_summary(doc)
        assert result["section_count"] == 2
        assert result["section_names"] == ["Introduction", "Conclusion"]

    def test_block_section_attributes(self):
        doc = _doc(blocks=[_block("text", section="Chapter1")])
        result = document_section_summary(doc)
        assert result["section_count"] == 1
        assert "Chapter1" in result["section_names"]

    def test_deduplicated(self):
        doc = _doc(sections=[
            {"name": "Intro"},
            {"name": "Intro"},
        ])
        result = document_section_summary(doc)
        assert result["section_count"] == 1

    def test_string_sections(self):
        doc = _doc(sections=["A", "B", "C"])
        result = document_section_summary(doc)
        assert result["section_count"] == 3


# ── document_change_tracking_summary ────────────────────────────────────

class TestDocumentChangeTrackingSummary:

    def test_empty_document(self):
        result = document_change_tracking_summary(_doc())
        assert result["tracked_change_count"] == 0
        assert result["author_names"] == []

    def test_tracked_changes(self):
        doc = _doc(tracked_changes=[
            {"author": "Alice", "type": "insertion"},
            {"author": "Bob", "type": "deletion"},
        ])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 2
        assert "Alice" in result["author_names"]
        assert "Bob" in result["author_names"]

    def test_block_change_markers(self):
        doc = _doc(blocks=[_block("edited", change_id="c1")])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] >= 1

    def test_no_changes(self):
        doc = _doc(blocks=[_block("clean text")])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 0

    def test_duplicate_authors(self):
        doc = _doc(tracked_changes=[
            {"author": "Alice"},
            {"author": "Alice"},
        ])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 2
        assert len(result["author_names"]) == 1


# ── document_footnote_endnote_summary ───────────────────────────────────

class TestDocumentFootnoteEndnoteSummary:

    def test_empty_document(self):
        result = document_footnote_endnote_summary(_doc())
        assert result["total"] == 0
        assert result["has_notes"] is False

    def test_footnotes(self):
        doc = _doc(blocks=[_block("text", footnotes=[{"id": "fn1"}])])
        result = document_footnote_endnote_summary(doc)
        assert result["footnote_count"] == 1
        assert result["has_notes"] is True

    def test_endnotes(self):
        doc = _doc(blocks=[_block("text", endnotes=[{"id": "en1"}])])
        result = document_footnote_endnote_summary(doc)
        assert result["endnote_count"] == 1

    def test_inline_notes(self):
        doc = _doc(blocks=[_block("text", inline_notes=[{"text": "note"}])])
        result = document_footnote_endnote_summary(doc)
        assert result["inline_note_count"] == 1

    def test_combined(self):
        doc = _doc(blocks=[
            _block("t1", footnotes=[{"id": "fn1"}]),
            _block("t2", endnotes=[{"id": "en1"}, {"id": "en2"}]),
        ])
        result = document_footnote_endnote_summary(doc)
        assert result["footnote_count"] == 1
        assert result["endnote_count"] == 2
        assert result["total"] == 3


# ── document_image_frame_list ───────────────────────────────────────────

class TestDocumentImageFrameList:

    def test_empty_document(self):
        assert document_image_frame_list(_doc()) == []

    def test_no_images(self):
        doc = _doc(blocks=[_block("text")])
        assert document_image_frame_list(doc) == []

    def test_block_frames(self):
        doc = _doc(blocks=[_block("text", frames=[
            {"name": "img1", "anchor_type": "paragraph", "image_href": "Pictures/img.png"},
        ])])
        result = document_image_frame_list(doc)
        assert len(result) == 1
        assert result[0]["frame_name"] == "img1"
        assert result[0]["image_href"] == "Pictures/img.png"

    def test_block_images(self):
        doc = _doc(blocks=[_block("text", images=[
            {"name": "photo", "image_href": "media/photo.jpg"},
        ])])
        result = document_image_frame_list(doc)
        assert len(result) == 1

    def test_table_cell_frames(self):
        doc = _doc(tables=[{"rows": [{"cells": [
            {"text": "data", "frames": [{"name": "chart1", "image_href": "chart.svg"}]},
        ]}]}])
        result = document_image_frame_list(doc)
        assert len(result) == 1
        assert result[0]["frame_name"] == "chart1"

    def test_multiple_frames(self):
        doc = _doc(blocks=[
            _block("t1", frames=[{"name": "a"}]),
            _block("t2", images=[{"name": "b"}, {"name": "c"}]),
        ])
        result = document_image_frame_list(doc)
        assert len(result) == 3
