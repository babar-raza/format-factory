"""
test_r66_fodt_advancement.py -- R66 Train H: FODT product advancement.

New capabilities added in R66:
1. document_section_summary(document)          -- section inventory
2. document_change_tracking_summary(document)  -- change tracking summary

R66 Sprint: FORMAT-FACTORY-R66 product advancement
Train H -- FODT product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_section_summary,
    document_change_tracking_summary,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_document(**overrides) -> dict:
    """Build a minimal FODT document for testing."""
    doc = {
        "format_id": "fodt",
        "blocks": [],
        "lists": [],
        "tables": [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }
    doc.update(overrides)
    return doc


# ---------------------------------------------------------------------------
# document_section_summary tests
# ---------------------------------------------------------------------------

class TestDocumentSectionSummary:
    """Tests for document_section_summary()."""

    def test_empty_document_returns_zero(self):
        doc = _make_document()
        result = document_section_summary(doc)
        assert isinstance(result, dict)
        assert result["section_count"] == 0
        assert result["section_names"] == []

    def test_returns_correct_keys(self):
        doc = _make_document()
        result = document_section_summary(doc)
        assert "section_count" in result
        assert "section_names" in result

    def test_explicit_sections_list(self):
        doc = _make_document(sections=[
            {"name": "Introduction"},
            {"name": "Body"},
            {"name": "Conclusion"},
        ])
        result = document_section_summary(doc)
        assert result["section_count"] == 3
        assert result["section_names"] == ["Introduction", "Body", "Conclusion"]

    def test_block_section_attributes(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "hello", "section": "sec1"},
            {"type": "paragraph", "text": "world", "section": "sec2"},
        ])
        result = document_section_summary(doc)
        assert result["section_count"] == 2
        assert "sec1" in result["section_names"]
        assert "sec2" in result["section_names"]

    def test_deduplicates_section_names(self):
        doc = _make_document(sections=[
            {"name": "Intro"},
            {"name": "Intro"},
        ])
        result = document_section_summary(doc)
        assert result["section_count"] == 1
        assert result["section_names"] == ["Intro"]

    def test_string_sections(self):
        doc = _make_document(sections=["Section1", "Section2"])
        result = document_section_summary(doc)
        assert result["section_count"] == 2

    def test_content_list_section_items(self):
        doc = _make_document(content=[
            {"kind": "section", "data": {"name": "AppendixA"}},
        ])
        result = document_section_summary(doc)
        assert result["section_count"] == 1
        assert "AppendixA" in result["section_names"]

    def test_none_sections_handled(self):
        doc = _make_document(sections=None)
        result = document_section_summary(doc)
        assert result["section_count"] == 0


# ---------------------------------------------------------------------------
# document_change_tracking_summary tests
# ---------------------------------------------------------------------------

class TestDocumentChangeTrackingSummary:
    """Tests for document_change_tracking_summary()."""

    def test_empty_document_returns_zero(self):
        doc = _make_document()
        result = document_change_tracking_summary(doc)
        assert isinstance(result, dict)
        assert result["tracked_change_count"] == 0
        assert result["author_names"] == []

    def test_returns_correct_keys(self):
        doc = _make_document()
        result = document_change_tracking_summary(doc)
        assert "tracked_change_count" in result
        assert "author_names" in result

    def test_explicit_tracked_changes(self):
        doc = _make_document(tracked_changes=[
            {"author": "Alice", "type": "insertion"},
            {"author": "Bob", "type": "deletion"},
        ])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 2
        assert "Alice" in result["author_names"]
        assert "Bob" in result["author_names"]

    def test_deduplicates_authors(self):
        doc = _make_document(tracked_changes=[
            {"author": "Alice"},
            {"author": "Alice"},
            {"author": "Bob"},
        ])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 3
        assert len(result["author_names"]) == 2

    def test_block_change_markers(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "edited", "change_id": "ct1"},
        ])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 1

    def test_run_change_markers(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "edited", "runs": [
                {"text": "new text", "change_id": "ct2"},
            ]},
        ])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 1

    def test_dc_creator_attribute(self):
        doc = _make_document(tracked_changes=[
            {"dc:creator": "Charlie"},
        ])
        result = document_change_tracking_summary(doc)
        assert "Charlie" in result["author_names"]

    def test_no_changes_returns_empty_authors(self):
        doc = _make_document(tracked_changes=[])
        result = document_change_tracking_summary(doc)
        assert result["tracked_change_count"] == 0
        assert result["author_names"] == []


# ---------------------------------------------------------------------------
# API accessibility tests
# ---------------------------------------------------------------------------

class TestTrainHR66FodtApiAccess:
    """New R66 functions must be accessible from the fodt package."""

    def test_document_section_summary_callable(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_section_summary")
        assert callable(fodt.document_section_summary)

    def test_document_change_tracking_summary_callable(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_change_tracking_summary")
        assert callable(fodt.document_change_tracking_summary)

    def test_all_r66_new_apis_in_all(self):
        import src.python.fodt as fodt
        for api in ["document_section_summary", "document_change_tracking_summary"]:
            assert api in fodt.__all__, f"{api} must be in fodt.__all__"
