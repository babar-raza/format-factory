"""
tests/python/fodt/test_r189_fodt_max_paragraph_length.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT58-001
Tests for document_max_paragraph_length() — length of the longest paragraph block.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.parser import parse_fodt_strict
from src.python.fodt.neutral_model import document_max_paragraph_length

SAMPLES = _REPO / "samples" / "by-format" / "fodt"


class TestFodtMaxParagraphLength:
    def test_minimal_document_returns_nonnegative(self):
        """Result is always >= 0."""
        doc = parse_fodt_strict(SAMPLES / "minimal-document.fodt")
        result = document_max_paragraph_length(doc)
        assert result >= 0

    def test_headings_paragraphs_has_positive_length(self):
        """Document with paragraphs has at least one paragraph with length > 0."""
        doc = parse_fodt_strict(SAMPLES / "headings-and-paragraphs.fodt")
        result = document_max_paragraph_length(doc)
        assert result > 0

    def test_result_is_int(self):
        """Result is always an integer."""
        doc = parse_fodt_strict(SAMPLES / "minimal-document.fodt")
        result = document_max_paragraph_length(doc)
        assert isinstance(result, int)

    def test_empty_document_dict_returns_zero(self):
        """Empty dict with no blocks returns 0."""
        result = document_max_paragraph_length({})
        assert result == 0

    def test_synthetic_document_with_known_paragraph(self):
        """Document with one known paragraph gives the correct max length."""
        doc = {"blocks": [{"type": "paragraph", "text": "Hello world"}]}
        result = document_max_paragraph_length(doc)
        assert result == len("Hello world")

    def test_headings_not_counted_as_paragraphs(self):
        """Heading blocks are excluded; only paragraph blocks counted."""
        doc = {
            "blocks": [
                {"type": "heading", "text": "A very long heading text here"},
                {"type": "paragraph", "text": "Short"},
            ]
        }
        result = document_max_paragraph_length(doc)
        assert result == len("Short")
