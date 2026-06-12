"""
test_r61_fodt_deepening.py — R61 Train G: FODT product deepening.

Tests 2 new R61 FODT capabilities:
  - document_list_stats: list count, item count, depth metrics
  - document_reading_level: estimated reading difficulty metrics

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fodt.neutral_model import document_list_stats, document_reading_level


def _make_document(blocks=None, lists=None, tables=None, content=None):
    doc = {"format_id": "fodt"}
    if blocks is not None:
        doc["blocks"] = blocks
    if lists is not None:
        doc["lists"] = lists
    if tables is not None:
        doc["tables"] = tables
    if content is not None:
        doc["content"] = content
    return doc


def _make_block(text="", kind="paragraph", runs=None):
    b = {"kind": kind}
    if runs is not None:
        b["runs"] = runs
    else:
        b["text"] = text
    return b


def _make_list(items):
    return {"items": items}


def _make_list_item(text, level=1):
    return {"text": text, "level": level}


class TestDocumentListStats:
    """document_list_stats returns metrics about lists in the document."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_list_stats(doc)
        assert result["list_count"] == 0
        assert result["total_items"] == 0
        assert result["max_depth"] == 0
        assert result["per_list"] == []

    def test_single_list_with_items(self):
        doc = _make_document(lists=[_make_list([
            _make_list_item("Item 1"),
            _make_list_item("Item 2"),
            _make_list_item("Item 3"),
        ])])
        result = document_list_stats(doc)
        assert result["list_count"] == 1
        assert result["total_items"] == 3
        assert len(result["per_list"]) == 1
        assert result["per_list"][0]["item_count"] == 3

    def test_multiple_lists(self):
        doc = _make_document(lists=[
            _make_list([_make_list_item("A"), _make_list_item("B")]),
            _make_list([_make_list_item("X"), _make_list_item("Y"), _make_list_item("Z")]),
        ])
        result = document_list_stats(doc)
        assert result["list_count"] == 2
        assert result["total_items"] == 5

    def test_nested_list_depth(self):
        doc = _make_document(lists=[_make_list([
            _make_list_item("Top", level=1),
            _make_list_item("Nested", level=2),
            _make_list_item("Deep", level=3),
        ])])
        result = document_list_stats(doc)
        assert result["max_depth"] == 3
        assert result["per_list"][0]["max_depth"] == 3

    def test_returns_required_fields(self):
        doc = _make_document(lists=[_make_list([_make_list_item("Item")])])
        result = document_list_stats(doc)
        assert "list_count" in result
        assert "total_items" in result
        assert "max_depth" in result
        assert "per_list" in result

    def test_per_list_has_index(self):
        doc = _make_document(lists=[
            _make_list([_make_list_item("A")]),
            _make_list([_make_list_item("B")]),
        ])
        result = document_list_stats(doc)
        indices = [p["index"] for p in result["per_list"]]
        assert 0 in indices
        assert 1 in indices

    def test_content_based_lists(self):
        """Lists embedded in content[] are also counted."""
        doc = _make_document(content=[
            {"kind": "list", "data": {"items": [
                {"text": "Item 1", "level": 1},
                {"text": "Item 2", "level": 1},
            ]}},
        ])
        result = document_list_stats(doc)
        assert result["list_count"] >= 1
        assert result["total_items"] >= 2


class TestDocumentReadingLevel:
    """document_reading_level returns estimated reading metrics."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_reading_level(doc)
        assert result["total_words"] == 0
        assert result["total_sentences"] == 0
        assert result["estimated_grade_level"] == 0.0

    def test_simple_text(self):
        doc = _make_document(blocks=[_make_block("The quick brown fox jumps over the lazy dog.")])
        result = document_reading_level(doc)
        assert result["total_words"] > 0
        assert "avg_words_per_sentence" in result
        assert "avg_chars_per_word" in result
        assert "estimated_grade_level" in result

    def test_total_words_count(self):
        doc = _make_document(blocks=[
            _make_block("Hello world foo bar."),
            _make_block("One two three."),
        ])
        result = document_reading_level(doc)
        assert result["total_words"] == 7  # Hello world foo bar One two three

    def test_multiple_sentences(self):
        doc = _make_document(blocks=[
            _make_block("First sentence. Second sentence. Third sentence."),
        ])
        result = document_reading_level(doc)
        assert result["total_sentences"] >= 3

    def test_avg_words_per_sentence_positive(self):
        doc = _make_document(blocks=[
            _make_block("First sentence. Second sentence here."),
        ])
        result = document_reading_level(doc)
        assert result["avg_words_per_sentence"] > 0

    def test_estimated_grade_level_non_negative(self):
        doc = _make_document(blocks=[
            _make_block("The cat sat on the mat. It was a small cat."),
        ])
        result = document_reading_level(doc)
        assert result["estimated_grade_level"] >= 0.0

    def test_returns_all_required_fields(self):
        doc = _make_document(blocks=[_make_block("Some text.")])
        result = document_reading_level(doc)
        for field in ["avg_words_per_sentence", "avg_chars_per_word", "total_words",
                      "total_sentences", "estimated_grade_level"]:
            assert field in result, f"Missing field: {field}"

    def test_avg_chars_per_word_reasonable(self):
        doc = _make_document(blocks=[_make_block("Hello world.")])
        result = document_reading_level(doc)
        # Average of 5+5 = 5.0
        assert 3.0 <= result["avg_chars_per_word"] <= 8.0
