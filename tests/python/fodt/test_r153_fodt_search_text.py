"""
test_r153_fodt_search_text.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-PROGRESS-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
Added: 2026-06-09

Tests for new FODT API:
- document_search_text(document, query, case_sensitive=False) -> list[dict]

Authority: P4 (SAL-FODT-00001: ODF 1.3 flat text format identified by MIME type
application/vnd.oasis.opendocument.text-flat-xml)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import document_search_text


def _para(text):
    return {"type": "paragraph", "text": text}


def _heading(text, level=1):
    return {"type": "heading", "text": text, "level": level}


def _doc(blocks):
    return {"blocks": blocks}


class TestDocumentSearchTextBasic:
    """document_search_text: basic search behavior."""

    def test_empty_document_returns_empty_list(self):
        doc = _doc([])
        result = document_search_text(doc, "hello")
        assert result == []

    def test_empty_query_returns_empty_list(self):
        doc = _doc([_para("some text")])
        result = document_search_text(doc, "")
        assert result == []

    def test_finds_paragraph_match(self):
        doc = _doc([_para("hello world"), _para("goodbye")])
        result = document_search_text(doc, "hello")
        assert len(result) == 1
        assert result[0]["block_type"] == "paragraph"
        assert result[0]["text"] == "hello world"

    def test_finds_heading_match(self):
        doc = _doc([_heading("Introduction"), _para("text")])
        result = document_search_text(doc, "intro")
        assert len(result) == 1
        assert result[0]["block_type"] == "heading"

    def test_no_match_returns_empty(self):
        doc = _doc([_para("alpha"), _para("beta")])
        result = document_search_text(doc, "gamma")
        assert result == []

    def test_returns_block_index(self):
        doc = _doc([_para("aaa"), _para("bbb"), _para("aaa again")])
        result = document_search_text(doc, "aaa")
        indices = [r["block_index"] for r in result]
        assert 0 in indices
        assert 2 in indices

    def test_returns_match_count(self):
        doc = _doc([_para("cat and cat")])
        result = document_search_text(doc, "cat")
        assert result[0]["match_count"] == 2


class TestDocumentSearchTextCaseSensitivity:
    """document_search_text: case sensitivity behavior."""

    def test_case_insensitive_by_default(self):
        doc = _doc([_para("Hello World")])
        result = document_search_text(doc, "hello")
        assert len(result) == 1

    def test_case_sensitive_no_match(self):
        doc = _doc([_para("Hello World")])
        result = document_search_text(doc, "hello", case_sensitive=True)
        assert result == []

    def test_case_sensitive_match(self):
        doc = _doc([_para("Hello World")])
        result = document_search_text(doc, "Hello", case_sensitive=True)
        assert len(result) == 1

    def test_uppercase_query_insensitive(self):
        doc = _doc([_para("lower case text")])
        result = document_search_text(doc, "LOWER")
        assert len(result) == 1


class TestDocumentSearchTextMultipleBlocks:
    """document_search_text: multiple blocks and mixed content."""

    def test_finds_matches_in_multiple_blocks(self):
        doc = _doc([
            _heading("Python Guide"),
            _para("Python is great"),
            _para("Java is different"),
            _para("Python again"),
        ])
        result = document_search_text(doc, "python")
        assert len(result) == 3

    def test_result_dict_has_required_keys(self):
        doc = _doc([_para("test match")])
        result = document_search_text(doc, "test")
        assert len(result) == 1
        entry = result[0]
        assert "block_index" in entry
        assert "block_type" in entry
        assert "text" in entry
        assert "match_count" in entry

    def test_partial_text_match(self):
        doc = _doc([_para("specification document")])
        result = document_search_text(doc, "spec")
        assert len(result) == 1

    def test_exported_from_package(self):
        """document_search_text must be importable from fodt package."""
        from src.python.fodt import document_search_text as ds
        assert callable(ds)
