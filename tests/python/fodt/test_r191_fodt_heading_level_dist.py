"""
tests/python/fodt/test_r191_fodt_heading_level_dist.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for document_heading_level_distribution() — heading structure metrics.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_heading_level_distribution


class TestFodtHeadingLevelDistribution:
    def test_empty_doc_returns_empty_structure(self):
        result = document_heading_level_distribution({})
        assert result["total_headings"] == 0
        assert result["by_level"] == {}
        assert result["deepest_level"] is None
        assert result["shallowest_level"] is None

    def test_returns_required_keys(self):
        result = document_heading_level_distribution({})
        assert "by_level" in result
        assert "total_headings" in result
        assert "deepest_level" in result
        assert "shallowest_level" in result

    def test_real_headings_file_has_headings(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] > 0

    def test_real_headings_file_has_by_level(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_heading_level_distribution(doc)
        assert len(result["by_level"]) > 0

    def test_real_headings_has_shallowest_level(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_heading_level_distribution(doc)
        assert result["shallowest_level"] is not None
        assert result["shallowest_level"] >= 1

    def test_total_matches_sum_of_by_level(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == sum(result["by_level"].values())

    def test_deepest_ge_shallowest_when_present(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_heading_level_distribution(doc)
        if result["deepest_level"] is not None:
            assert result["deepest_level"] >= result["shallowest_level"]
