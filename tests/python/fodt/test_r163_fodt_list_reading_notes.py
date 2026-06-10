"""
test_r163_fodt_list_reading_notes.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT26-001
Added: 2026-06-10

Tests for FODT APIs:
- document_list_stats(document) -> dict
- document_reading_level(document) -> dict
- document_hyperlink_count(document) -> dict
- document_footnote_count(document) -> dict
- document_heading_level_distribution(document) -> dict

Authority: P4 (FODT neutral model)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_list_stats,
    document_reading_level,
    document_hyperlink_count,
    document_footnote_count,
    document_heading_level_distribution,
)


def _block(text, btype="paragraph", heading_level=None, hyperlinks=None, footnotes=None, endnotes=None):
    b = {"type": btype, "text": text, "runs": [{"text": text}]}
    if heading_level is not None:
        b["heading_level"] = heading_level
    if hyperlinks:
        b["hyperlinks"] = hyperlinks
    if footnotes:
        b["footnotes"] = footnotes
    if endnotes:
        b["endnotes"] = endnotes
    return b


def _heading(text, level=1):
    return _block(text, btype="heading", heading_level=level)


def _doc(blocks=None, lists=None, tables=None):
    return {
        "format_id": "fodt",
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
    }


# ── document_list_stats ─────────────────────────────────────────────────

class TestDocumentListStats:

    def test_empty_document(self):
        result = document_list_stats(_doc())
        assert result["list_count"] == 0
        assert result["total_items"] == 0
        assert result["max_depth"] == 0
        assert result["per_list"] == []

    def test_single_list(self):
        doc = _doc(lists=[{"items": [{"text": "a"}, {"text": "b"}]}])
        result = document_list_stats(doc)
        assert result["list_count"] == 1
        assert result["total_items"] == 2
        assert result["per_list"][0]["item_count"] == 2

    def test_nested_list(self):
        doc = _doc(lists=[{"items": [
            {"text": "top", "level": 1},
            {"text": "nested", "level": 2},
            {"text": "deep", "level": 3},
        ]}])
        result = document_list_stats(doc)
        assert result["max_depth"] == 3

    def test_multiple_lists(self):
        doc = _doc(lists=[
            {"items": [{"text": "a"}]},
            {"items": [{"text": "b"}, {"text": "c"}]},
        ])
        result = document_list_stats(doc)
        assert result["list_count"] == 2
        assert result["total_items"] == 3

    def test_empty_list(self):
        doc = _doc(lists=[{"items": []}])
        result = document_list_stats(doc)
        assert result["list_count"] == 1
        assert result["total_items"] == 0


# ── document_reading_level ──────────────────────────────────────────────

class TestDocumentReadingLevel:

    def test_empty_document(self):
        result = document_reading_level(_doc())
        assert result["total_words"] == 0
        assert result["total_sentences"] == 0

    def test_simple_text(self):
        doc = _doc(blocks=[_block("The cat sat on the mat. It was happy.")])
        result = document_reading_level(doc)
        assert result["total_words"] > 0
        assert result["total_sentences"] >= 2
        assert result["avg_words_per_sentence"] > 0
        assert result["avg_chars_per_word"] > 0

    def test_grade_level_nonnegative(self):
        doc = _doc(blocks=[_block("Hello world.")])
        result = document_reading_level(doc)
        assert result["estimated_grade_level"] >= 0.0

    def test_longer_text_higher_metrics(self):
        doc = _doc(blocks=[_block(
            "The comprehensive international documentation standard "
            "establishes sophisticated requirements. "
            "Implementation verification necessitates systematic evaluation."
        )])
        result = document_reading_level(doc)
        assert result["avg_chars_per_word"] > 3.0


# ── document_hyperlink_count ────────────────────────────────────────────

class TestDocumentHyperlinkCount:

    def test_empty_document(self):
        result = document_hyperlink_count(_doc())
        assert result["total"] == 0
        assert result["per_block"] == []

    def test_no_links(self):
        doc = _doc(blocks=[_block("plain text")])
        result = document_hyperlink_count(doc)
        assert result["total"] == 0
        assert result["per_block"] == [0]

    def test_with_links(self):
        doc = _doc(blocks=[
            _block("click here", hyperlinks=[{"href": "http://example.com"}]),
        ])
        result = document_hyperlink_count(doc)
        assert result["total"] == 1
        assert result["per_block"] == [1]

    def test_multiple_links(self):
        doc = _doc(blocks=[
            _block("link1", hyperlinks=[{"href": "http://a.com"}, {"href": "http://b.com"}]),
            _block("no links"),
        ])
        result = document_hyperlink_count(doc)
        assert result["total"] == 2
        assert result["per_block"] == [2, 0]


# ── document_footnote_count ─────────────────────────────────────────────

class TestDocumentFootnoteCount:

    def test_empty_document(self):
        result = document_footnote_count(_doc())
        assert result["footnotes"] == 0
        assert result["endnotes"] == 0
        assert result["total"] == 0
        assert result["has_notes"] is False

    def test_no_notes(self):
        doc = _doc(blocks=[_block("text")])
        result = document_footnote_count(doc)
        assert result["total"] == 0
        assert result["has_notes"] is False

    def test_footnotes(self):
        doc = _doc(blocks=[
            _block("text", footnotes=[{"id": "fn1", "text": "Note 1"}]),
        ])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 1
        assert result["has_notes"] is True
        assert "note" in result

    def test_endnotes(self):
        doc = _doc(blocks=[
            _block("text", endnotes=[{"id": "en1"}]),
        ])
        result = document_footnote_count(doc)
        assert result["endnotes"] == 1
        assert result["total"] == 1

    def test_mixed(self):
        doc = _doc(blocks=[
            _block("text", footnotes=[{"id": "fn1"}], endnotes=[{"id": "en1"}]),
        ])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 1
        assert result["endnotes"] == 1
        assert result["total"] == 2


# ── document_heading_level_distribution ─────────────────────────────────

class TestDocumentHeadingLevelDistribution:

    def test_empty_document(self):
        result = document_heading_level_distribution(_doc())
        assert result["total_headings"] == 0

    def test_single_heading(self):
        doc = _doc(blocks=[_heading("Title", 1)])
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 1
        assert result["by_level"][1] == 1

    def test_multiple_levels(self):
        doc = _doc(blocks=[
            _heading("H1", 1),
            _heading("H2a", 2),
            _heading("H2b", 2),
            _heading("H3", 3),
        ])
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 4
        assert result["by_level"][1] == 1
        assert result["by_level"][2] == 2
        assert result["by_level"][3] == 1
        assert result["shallowest_level"] == 1
        assert result["deepest_level"] == 3
