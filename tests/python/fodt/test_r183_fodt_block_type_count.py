"""
tests/python/fodt/test_r183_fodt_block_type_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT51-001
Tests for document_block_type_count() — count blocks grouped by type.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.parser import parse_fodt_strict
from src.python.fodt.neutral_model import document_block_type_count

SAMPLES = _REPO / "samples" / "by-format" / "fodt"


class TestFodtBlockTypeCount:
    def test_minimal_document_one_paragraph(self):
        doc = parse_fodt_strict(SAMPLES / "minimal-document.fodt")
        result = document_block_type_count(doc)
        assert result.get("paragraph", 0) >= 1

    def test_headings_and_paragraphs_has_both(self):
        doc = parse_fodt_strict(SAMPLES / "headings-and-paragraphs.fodt")
        result = document_block_type_count(doc)
        assert "heading" in result
        assert "paragraph" in result

    def test_headings_count_correct(self):
        doc = parse_fodt_strict(SAMPLES / "headings-and-paragraphs.fodt")
        result = document_block_type_count(doc)
        assert result["heading"] == 3

    def test_returns_dict(self):
        doc = parse_fodt_strict(SAMPLES / "minimal-document.fodt")
        result = document_block_type_count(doc)
        assert isinstance(result, dict)

    def test_empty_document_returns_empty_dict(self):
        result = document_block_type_count({"blocks": []})
        assert result == {}

    def test_exported_from_init(self):
        from src.python.fodt import document_block_type_count as fn
        doc = parse_fodt_strict(SAMPLES / "minimal-document.fodt")
        result = fn(doc)
        assert isinstance(result, dict)
