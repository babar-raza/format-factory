"""Dogfood: FODT neutral model text extraction and analysis pipeline.

Demonstrates: build FODT doc dict -> analytics on in-memory model,
              write to disk -> parse back -> structural verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import (
    document_paragraph_count,
    document_text_content,
    document_word_count,
    document_stats,
    document_empty_paragraph_count,
)
from fodt.writer import write_fodt
from fodt.parser import parse_fodt_strict


def _para(text):
    return {"type": "paragraph", "runs": [{"text": text}]}


def _make_doc():
    """Build an in-memory FODT model with known content."""
    return {
        "blocks": [
            _para("Introduction"),
            _para("This is the first paragraph of our test document."),
            _para("Format Factory supports many document formats."),
            _para("Conclusion"),
            _para("The end of the document."),
        ]
    }


class TestDogfoodFodtInMemoryAnalytics:
    """Test analytics on the in-memory FODT neutral model."""

    def test_paragraph_count(self):
        doc = _make_doc()
        assert document_paragraph_count(doc) == 5

    def test_text_content(self):
        doc = _make_doc()
        text = document_text_content(doc)
        assert "Introduction" in text
        assert "Format Factory" in text
        assert "Conclusion" in text

    def test_word_count(self):
        doc = _make_doc()
        wc = document_word_count(doc)
        assert wc["total_words"] >= 15

    def test_no_empty_paragraphs(self):
        doc = _make_doc()
        assert document_empty_paragraph_count(doc) == 0

    def test_document_stats(self):
        doc = _make_doc()
        stats = document_stats(doc)
        assert isinstance(stats, dict)
        assert len(stats) > 0


class TestDogfoodFodtWriteParseRoundtrip:
    """Test write -> parse structural roundtrip."""

    @pytest.fixture
    def fodt_file(self, tmp_path):
        doc = _make_doc()
        p = tmp_path / "test_doc.fodt"
        write_fodt(doc, str(p))
        return p

    def test_write_creates_file(self, fodt_file):
        assert fodt_file.exists()
        assert fodt_file.stat().st_size > 0

    def test_parse_returns_dict(self, fodt_file):
        doc = parse_fodt_strict(str(fodt_file))
        assert isinstance(doc, dict)
        assert "blocks" in doc

    def test_roundtrip_preserves_paragraph_count(self, fodt_file):
        doc = parse_fodt_strict(str(fodt_file))
        assert document_paragraph_count(doc) >= 5

    def test_roundtrip_stats(self, fodt_file):
        doc = parse_fodt_strict(str(fodt_file))
        stats = document_stats(doc)
        assert isinstance(stats, dict)
