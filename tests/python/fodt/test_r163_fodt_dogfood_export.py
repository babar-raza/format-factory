"""
test_r163_fodt_dogfood_export.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT25-001
Added: 2026-06-10

Dogfood test: build a FODT document from test results using the library,
then verify stats, text content, and heading outline.

Authority: P4 (FODT neutral model)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    build_document,
    document_stats,
    document_word_count,
    document_heading_outline,
    document_text_content,
    document_to_text,
    document_paragraph_count,
    document_get_paragraph_text,
)


def _make_test_results_doc():
    """Build a FODT document that records sprint test results."""
    blocks = [
        {
            "type": "heading",
            "text": "Sprint RNEXT25 Test Results",
            "heading_level": 1,
            "level": 1,
            "runs": [{"text": "Sprint RNEXT25 Test Results"}],
        },
        {
            "type": "paragraph",
            "text": "Tests: 80 passed, 0 failed",
            "runs": [{"text": "Tests: 80 passed, 0 failed"}],
        },
        {
            "type": "heading",
            "text": "FODS Tests",
            "heading_level": 2,
            "level": 2,
            "runs": [{"text": "FODS Tests"}],
        },
        {
            "type": "paragraph",
            "text": "workbook_stats: PASS",
            "runs": [{"text": "workbook_stats: PASS"}],
        },
        {
            "type": "paragraph",
            "text": "workbook_type_distribution: PASS",
            "runs": [{"text": "workbook_type_distribution: PASS"}],
        },
        {
            "type": "heading",
            "text": "FODT Tests",
            "heading_level": 2,
            "level": 2,
            "runs": [{"text": "FODT Tests"}],
        },
        {
            "type": "paragraph",
            "text": "document_stats: PASS",
            "runs": [{"text": "document_stats: PASS"}],
        },
    ]
    return build_document(
        odf_version_attr="1.3",
        mimetype="application/vnd.oasis.opendocument.text",
        blocks=blocks,
        lists=[],
        tables=[],
        warnings=[],
        unsupported_features=[],
        parse_errors=[],
    )


class TestFodtDogfoodExport:

    def test_document_builds(self):
        doc = _make_test_results_doc()
        assert doc is not None
        assert doc.get("format_id") == "fodt"

    def test_stats_correct(self):
        doc = _make_test_results_doc()
        stats = document_stats(doc)
        assert stats["heading_count"] == 3
        assert stats["paragraph_count"] == 4
        assert stats["block_count"] == 7

    def test_word_count(self):
        doc = _make_test_results_doc()
        wc = document_word_count(doc)
        assert wc["total_words"] > 0
        assert wc["block_words"] > 0

    def test_heading_outline(self):
        doc = _make_test_results_doc()
        outline = document_heading_outline(doc)
        assert len(outline) == 3
        assert outline[0]["text"] == "Sprint RNEXT25 Test Results"
        assert outline[0]["level"] == 1
        assert outline[1]["text"] == "FODS Tests"
        assert outline[1]["level"] == 2

    def test_text_content_includes_all(self):
        doc = _make_test_results_doc()
        text = document_text_content(doc)
        assert "Sprint RNEXT25" in text
        assert "workbook_stats" in text
        assert "document_stats" in text

    def test_paragraph_count(self):
        doc = _make_test_results_doc()
        assert document_paragraph_count(doc) == 4

    def test_get_paragraph_text(self):
        doc = _make_test_results_doc()
        assert document_get_paragraph_text(doc, 0) == "Tests: 80 passed, 0 failed"

    def test_to_text_export(self):
        doc = _make_test_results_doc()
        text = document_to_text(doc)
        assert "# Sprint RNEXT25 Test Results" in text
        assert "## FODS Tests" in text
