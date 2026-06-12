"""
tests/python/fodt/test_r190_fodt_reading_level.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for document_reading_level() — readability metrics.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_reading_level


class TestFodtReadingLevel:
    def test_empty_doc_returns_zeros(self):
        result = document_reading_level({})
        assert result["total_words"] == 0
        assert result["total_sentences"] == 0
        assert result["estimated_grade_level"] == 0.0

    def test_returns_required_keys(self):
        result = document_reading_level({})
        assert "avg_words_per_sentence" in result
        assert "avg_chars_per_word" in result
        assert "total_words" in result
        assert "total_sentences" in result
        assert "estimated_grade_level" in result

    def test_all_values_are_numeric(self):
        result = document_reading_level({})
        for k, v in result.items():
            assert isinstance(v, (int, float)), f"{k} is not numeric: {v}"

    def test_single_block_counted(self):
        doc = {
            "blocks": [
                {"type": "paragraph", "text": "Hello world."}
            ]
        }
        result = document_reading_level(doc)
        assert result["total_words"] >= 1

    def test_grade_level_non_negative(self):
        doc = {
            "blocks": [
                {"type": "paragraph", "text": "The quick brown fox jumps."}
            ]
        }
        result = document_reading_level(doc)
        assert result["estimated_grade_level"] >= 0.0

    def test_avg_words_per_sentence_non_negative(self):
        doc = {
            "blocks": [
                {"type": "paragraph", "text": "Short sentence."},
            ]
        }
        result = document_reading_level(doc)
        assert result["avg_words_per_sentence"] >= 0.0

    def test_real_file_non_negative_metrics(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_reading_level(doc)
        assert result["total_words"] >= 0
        assert result["estimated_grade_level"] >= 0.0
