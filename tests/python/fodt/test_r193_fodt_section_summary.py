"""
tests/python/fodt/test_r193_fodt_section_summary.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT62-001
Tests for document_section_summary() — document section metadata.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_section_summary


class TestFodtSectionSummary:
    def test_empty_doc_returns_zero_sections(self):
        result = document_section_summary({})
        assert result["section_count"] == 0

    def test_returns_required_keys(self):
        result = document_section_summary({})
        assert "section_count" in result
        assert "section_names" in result

    def test_section_names_is_list(self):
        result = document_section_summary({})
        assert isinstance(result["section_names"], list)

    def test_section_count_matches_names_length(self):
        result = document_section_summary({})
        assert result["section_count"] == len(result["section_names"])

    def test_real_file_has_valid_structure(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_section_summary(doc)
        assert isinstance(result["section_count"], int)
        assert result["section_count"] >= 0

    def test_section_count_non_negative(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_section_summary(doc)
        assert result["section_count"] >= 0
