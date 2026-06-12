"""
tests/python/fodt/test_r195_fodt_footnote_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT62-001
Tests for document_footnote_count() — footnote and endnote enumeration.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_footnote_count


class TestFodtFootnoteCount:
    def test_empty_doc_returns_zeros(self):
        result = document_footnote_count({})
        assert result["footnotes"] == 0
        assert result["endnotes"] == 0
        assert result["total"] == 0

    def test_returns_required_keys(self):
        result = document_footnote_count({})
        assert "footnotes" in result
        assert "endnotes" in result
        assert "total" in result
        assert "has_notes" in result

    def test_empty_has_notes_is_false(self):
        result = document_footnote_count({})
        assert result["has_notes"] is False

    def test_total_equals_footnotes_plus_endnotes(self):
        result = document_footnote_count({})
        assert result["total"] == result["footnotes"] + result["endnotes"]

    def test_real_file_all_non_negative(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_footnote_count(doc)
        assert result["footnotes"] >= 0
        assert result["endnotes"] >= 0
        assert result["total"] >= 0

    def test_has_notes_consistent_with_total(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_footnote_count(doc)
        if result["total"] > 0:
            assert result["has_notes"] is True
        else:
            assert result["has_notes"] is False
