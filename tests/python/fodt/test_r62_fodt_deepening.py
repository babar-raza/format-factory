"""
test_r62_fodt_deepening.py — R62 Train H: FODT neutral_model deepening tests.

Tests the two new capabilities added in R62 Train H:
  - document_hyperlink_count(): count hyperlinks per block and total
  - document_footnote_count(): detect and count footnote/endnote annotations

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fodt.neutral_model import document_hyperlink_count, document_footnote_count


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc(blocks=None):
    return {
        "format_id": "fodt",
        "spec_version": "1.0",
        "blocks": blocks or [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }


def _make_block(btype="paragraph", text="", hyperlinks=None, footnotes=None, endnotes=None):
    b = {"type": btype, "text": text}
    if hyperlinks is not None:
        b["hyperlinks"] = hyperlinks
    if footnotes is not None:
        b["footnotes"] = footnotes
    if endnotes is not None:
        b["endnotes"] = endnotes
    return b


def _make_link(href, text=""):
    return {"href": href, "text": text}


def _make_footnote(text=""):
    return {"text": text}


# ---------------------------------------------------------------------------
# document_hyperlink_count
# ---------------------------------------------------------------------------

class TestDocumentHyperlinkCountEmpty:
    """document_hyperlink_count on empty document."""

    def test_empty_document_returns_zero(self):
        doc = _make_doc([])
        result = document_hyperlink_count(doc)
        assert result["total"] == 0

    def test_empty_document_per_block_empty(self):
        doc = _make_doc([])
        result = document_hyperlink_count(doc)
        assert result["per_block"] == []

    def test_returns_dict(self):
        doc = _make_doc([])
        result = document_hyperlink_count(doc)
        assert isinstance(result, dict)

    def test_no_hyperlinks_in_blocks_returns_zero(self):
        blocks = [_make_block("paragraph", "hello"), _make_block("paragraph", "world")]
        doc = _make_doc(blocks)
        result = document_hyperlink_count(doc)
        assert result["total"] == 0
        assert result["per_block"] == [0, 0]


class TestDocumentHyperlinkCountSingle:
    """document_hyperlink_count with a single hyperlink."""

    def test_one_block_one_link(self):
        link = _make_link("https://example.com", "Example")
        block = _make_block("paragraph", "see link", hyperlinks=[link])
        doc = _make_doc([block])
        result = document_hyperlink_count(doc)
        assert result["total"] == 1
        assert result["per_block"] == [1]

    def test_result_has_total_and_per_block_keys(self):
        link = _make_link("https://x.com")
        block = _make_block(hyperlinks=[link])
        doc = _make_doc([block])
        result = document_hyperlink_count(doc)
        assert "total" in result
        assert "per_block" in result


class TestDocumentHyperlinkCountMultiple:
    """document_hyperlink_count with multiple hyperlinks across blocks."""

    def test_two_links_same_block(self):
        links = [_make_link("https://a.com"), _make_link("https://b.com")]
        block = _make_block(hyperlinks=links)
        doc = _make_doc([block])
        result = document_hyperlink_count(doc)
        assert result["total"] == 2
        assert result["per_block"] == [2]

    def test_links_across_multiple_blocks(self):
        b1 = _make_block(hyperlinks=[_make_link("https://a.com")])
        b2 = _make_block()  # no links
        b3 = _make_block(hyperlinks=[_make_link("https://b.com"), _make_link("https://c.com")])
        doc = _make_doc([b1, b2, b3])
        result = document_hyperlink_count(doc)
        assert result["total"] == 3
        assert result["per_block"] == [1, 0, 2]

    def test_per_block_length_matches_block_count(self):
        blocks = [_make_block() for _ in range(5)]
        doc = _make_doc(blocks)
        result = document_hyperlink_count(doc)
        assert len(result["per_block"]) == 5

    def test_total_equals_sum_of_per_block(self):
        b1 = _make_block(hyperlinks=[_make_link("https://x.com")])
        b2 = _make_block(hyperlinks=[_make_link("https://y.com"), _make_link("https://z.com")])
        b3 = _make_block()
        doc = _make_doc([b1, b2, b3])
        result = document_hyperlink_count(doc)
        assert result["total"] == sum(result["per_block"])


# ---------------------------------------------------------------------------
# document_footnote_count
# ---------------------------------------------------------------------------

class TestDocumentFootnoteCountEmpty:
    """document_footnote_count on empty document."""

    def test_empty_document_returns_zeros(self):
        doc = _make_doc([])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 0
        assert result["endnotes"] == 0
        assert result["total"] == 0

    def test_empty_document_has_notes_false(self):
        doc = _make_doc([])
        result = document_footnote_count(doc)
        assert result["has_notes"] is False

    def test_returns_dict_with_required_keys(self):
        doc = _make_doc([])
        result = document_footnote_count(doc)
        for key in ("footnotes", "endnotes", "total", "has_notes"):
            assert key in result, f"Missing key: {key}"

    def test_no_notes_in_blocks_returns_zeros(self):
        blocks = [_make_block("paragraph", "text"), _make_block("heading", "head")]
        doc = _make_doc(blocks)
        result = document_footnote_count(doc)
        assert result["total"] == 0
        assert result["has_notes"] is False


class TestDocumentFootnoteCountFootnotes:
    """document_footnote_count with footnotes."""

    def test_one_footnote(self):
        block = _make_block(footnotes=[_make_footnote("fn text")])
        doc = _make_doc([block])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 1
        assert result["endnotes"] == 0
        assert result["total"] == 1
        assert result["has_notes"] is True

    def test_multiple_footnotes(self):
        block = _make_block(footnotes=[_make_footnote("f1"), _make_footnote("f2"), _make_footnote("f3")])
        doc = _make_doc([block])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 3
        assert result["total"] == 3

    def test_footnotes_across_blocks(self):
        b1 = _make_block(footnotes=[_make_footnote("a")])
        b2 = _make_block()
        b3 = _make_block(footnotes=[_make_footnote("b"), _make_footnote("c")])
        doc = _make_doc([b1, b2, b3])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 3

    def test_note_string_present_when_has_notes(self):
        block = _make_block(footnotes=[_make_footnote("fn")])
        doc = _make_doc([block])
        result = document_footnote_count(doc)
        assert "note" in result
        assert isinstance(result["note"], str)


class TestDocumentFootnoteCountEndnotes:
    """document_footnote_count with endnotes."""

    def test_one_endnote(self):
        block = _make_block(endnotes=[_make_footnote("en text")])
        doc = _make_doc([block])
        result = document_footnote_count(doc)
        assert result["endnotes"] == 1
        assert result["footnotes"] == 0
        assert result["total"] == 1
        assert result["has_notes"] is True

    def test_multiple_endnotes(self):
        block = _make_block(endnotes=[_make_footnote("e1"), _make_footnote("e2")])
        doc = _make_doc([block])
        result = document_footnote_count(doc)
        assert result["endnotes"] == 2


class TestDocumentFootnoteCountMixed:
    """document_footnote_count with both footnotes and endnotes."""

    def test_footnotes_and_endnotes_counted_separately(self):
        b1 = _make_block(footnotes=[_make_footnote("fn")])
        b2 = _make_block(endnotes=[_make_footnote("en1"), _make_footnote("en2")])
        doc = _make_doc([b1, b2])
        result = document_footnote_count(doc)
        assert result["footnotes"] == 1
        assert result["endnotes"] == 2
        assert result["total"] == 3

    def test_total_equals_footnotes_plus_endnotes(self):
        b1 = _make_block(footnotes=[_make_footnote("a"), _make_footnote("b")])
        b2 = _make_block(endnotes=[_make_footnote("c")])
        doc = _make_doc([b1, b2])
        result = document_footnote_count(doc)
        assert result["total"] == result["footnotes"] + result["endnotes"]

    def test_note_message_mentions_both_types(self):
        b1 = _make_block(footnotes=[_make_footnote("f")])
        b2 = _make_block(endnotes=[_make_footnote("e")])
        doc = _make_doc([b1, b2])
        result = document_footnote_count(doc)
        assert "note" in result
        note_text = result["note"]
        assert "footnote" in note_text.lower() or "endnote" in note_text.lower()

    def test_no_note_key_when_zero_notes(self):
        doc = _make_doc([_make_block("paragraph")])
        result = document_footnote_count(doc)
        assert result.get("note") is None or "note" not in result
