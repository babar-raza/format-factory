"""
test_r154_fodt_extract_headings.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
Added: 2026-06-09

Tests for FODT document_extract_headings() API.
Authority: P6 (SAL-FODT-00001: ODF 1.3 flat text format)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import document_extract_headings


def _para(text):
    return {"type": "paragraph", "text": text}


def _heading(text, level=1):
    return {"type": "heading", "text": text, "level": level}


def _doc(blocks):
    return {"blocks": blocks}


class TestDocumentExtractHeadings:
    """document_extract_headings: extract headings by level range."""

    def test_empty_document_returns_empty(self):
        assert document_extract_headings(_doc([])) == []

    def test_no_headings_returns_empty(self):
        doc = _doc([_para("just a paragraph")])
        assert document_extract_headings(doc) == []

    def test_extracts_all_headings(self):
        doc = _doc([
            _heading("H1 Title", 1),
            _para("para"),
            _heading("H2 Section", 2),
            _heading("H3 Sub", 3),
        ])
        result = document_extract_headings(doc)
        assert len(result) == 3

    def test_result_has_required_keys(self):
        doc = _doc([_heading("Chapter", 1)])
        result = document_extract_headings(doc)
        assert len(result) == 1
        entry = result[0]
        assert "block_index" in entry
        assert "level" in entry
        assert "text" in entry

    def test_correct_block_index(self):
        doc = _doc([_para("intro"), _heading("Title", 1), _para("body")])
        result = document_extract_headings(doc)
        assert result[0]["block_index"] == 1

    def test_correct_level(self):
        doc = _doc([_heading("H2 section", 2)])
        result = document_extract_headings(doc)
        assert result[0]["level"] == 2

    def test_correct_text(self):
        doc = _doc([_heading("My Heading", 1)])
        result = document_extract_headings(doc)
        assert result[0]["text"] == "My Heading"

    def test_min_level_filter(self):
        doc = _doc([_heading("H1", 1), _heading("H2", 2), _heading("H3", 3)])
        result = document_extract_headings(doc, min_level=2)
        assert len(result) == 2
        assert all(h["level"] >= 2 for h in result)

    def test_max_level_filter(self):
        doc = _doc([_heading("H1", 1), _heading("H2", 2), _heading("H3", 3)])
        result = document_extract_headings(doc, max_level=2)
        assert len(result) == 2
        assert all(h["level"] <= 2 for h in result)

    def test_level_range_filter(self):
        doc = _doc([_heading("H1", 1), _heading("H2", 2), _heading("H3", 3), _heading("H4", 4)])
        result = document_extract_headings(doc, min_level=2, max_level=3)
        assert len(result) == 2
        levels = [h["level"] for h in result]
        assert 1 not in levels
        assert 4 not in levels

    def test_paragraphs_excluded(self):
        doc = _doc([_heading("H1", 1), _para("not a heading")])
        result = document_extract_headings(doc)
        assert len(result) == 1
        assert result[0]["text"] == "H1"

    def test_document_order_preserved(self):
        doc = _doc([_heading("First", 1), _heading("Second", 2), _heading("Third", 1)])
        result = document_extract_headings(doc)
        texts = [h["text"] for h in result]
        assert texts == ["First", "Second", "Third"]

    def test_exported_from_package(self):
        from src.python.fodt import document_extract_headings as deh
        assert callable(deh)
