"""Tests for FODT document_replace_text.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Covers: search-and-replace text operations in FODT documents
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_replace_text, document_search_text


def _make_doc(blocks):
    return {"blocks": blocks}


class TestReplaceText:
    def test_basic_replace(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "Hello world"},
            {"type": "paragraph", "text": "Hello again"},
        ])
        result = document_replace_text(doc, "Hello", "Hi")
        assert result["total_replacements"] == 2
        assert result["blocks_modified"] == 2
        assert doc["blocks"][0]["text"] == "Hi world"
        assert doc["blocks"][1]["text"] == "Hi again"

    def test_case_insensitive(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "HELLO world hello"},
        ])
        result = document_replace_text(doc, "hello", "hi", case_sensitive=False)
        assert result["total_replacements"] == 2
        assert doc["blocks"][0]["text"] == "hi world hi"

    def test_case_sensitive(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "Hello HELLO hello"},
        ])
        result = document_replace_text(doc, "Hello", "Hi", case_sensitive=True)
        assert result["total_replacements"] == 1
        assert doc["blocks"][0]["text"] == "Hi HELLO hello"

    def test_no_match(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "Foo bar"},
        ])
        result = document_replace_text(doc, "xyz", "abc")
        assert result["total_replacements"] == 0
        assert result["blocks_modified"] == 0
        assert doc["blocks"][0]["text"] == "Foo bar"

    def test_empty_search(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "Text"},
        ])
        result = document_replace_text(doc, "", "X")
        assert result["total_replacements"] == 0

    def test_replace_in_heading(self):
        doc = _make_doc([
            {"type": "heading", "text": "Old Title"},
            {"type": "paragraph", "text": "Body text"},
        ])
        result = document_replace_text(doc, "Old", "New")
        assert result["total_replacements"] == 1
        assert doc["blocks"][0]["text"] == "New Title"

    def test_multiple_in_one_block(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "aaa bbb aaa"},
        ])
        result = document_replace_text(doc, "aaa", "x")
        assert result["total_replacements"] == 2
        assert doc["blocks"][0]["text"] == "x bbb x"

    def test_skips_non_text_blocks(self):
        doc = _make_doc([
            {"type": "table", "text": "Hello"},
            {"type": "paragraph", "text": "Hello"},
        ])
        result = document_replace_text(doc, "Hello", "Hi")
        assert result["total_replacements"] == 1
        assert result["blocks_modified"] == 1
