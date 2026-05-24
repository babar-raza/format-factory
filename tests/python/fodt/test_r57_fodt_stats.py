"""
test_r57_fodt_stats.py — R57 Train E: document_stats() capability tests.

Verifies the new document_stats() function added to format-factory-fodt neutral_model.py.
Tests cover: empty document, paragraphs, headings, lists, tables, hyperlinks,
content list (R55 TC-0060 document-order), and edge cases.

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fodt.neutral_model import document_stats


def _make_block(btype="paragraph", text="", runs=None, heading_level=None):
    b = {"type": btype, "text": text}
    if runs is not None:
        b["runs"] = runs
    if heading_level is not None:
        b["heading_level"] = heading_level
    return b


def _make_run(text="", href=None):
    r = {"text": text}
    if href is not None:
        r["href"] = href
    return r


def _make_list(items):
    return {"items": items}


def _make_list_item(text="", level=1):
    return {"text": text, "level": level}


def _make_table(rows):
    return {"rows": rows}


def _make_table_row(cells):
    return {"cells": cells}


def _make_cell(text=""):
    return {"text": text}


def _make_document(blocks=None, lists=None, tables=None, content=None):
    doc = {
        "format_id": "fodt",
        "spec_version": "1.0",
        "odf_version_attr": "1.3",
        "mimetype": "application/vnd.oasis.opendocument.text-flat-xml",
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
        "warnings": [],
    }
    if content is not None:
        doc["content"] = content
    return doc


class TestDocumentStatsEmpty:
    """document_stats on an empty document."""

    def test_all_zero_for_empty_document(self):
        doc = _make_document()
        stats = document_stats(doc)
        assert stats["block_count"] == 0
        assert stats["paragraph_count"] == 0
        assert stats["heading_count"] == 0
        assert stats["list_count"] == 0
        assert stats["list_item_count"] == 0
        assert stats["table_count"] == 0
        assert stats["table_cell_count"] == 0
        assert stats["total_text_length"] == 0
        assert stats["hyperlink_count"] == 0

    def test_returns_all_required_keys(self):
        doc = _make_document()
        stats = document_stats(doc)
        required = [
            "block_count", "paragraph_count", "heading_count",
            "list_count", "list_item_count", "table_count",
            "table_cell_count", "total_text_length", "hyperlink_count",
        ]
        for key in required:
            assert key in stats, f"Missing key: {key!r}"


class TestDocumentStatsBlocks:
    """Paragraph and heading counting."""

    def test_single_paragraph(self):
        doc = _make_document(blocks=[_make_block("paragraph", "Hello world")])
        stats = document_stats(doc)
        assert stats["block_count"] == 1
        assert stats["paragraph_count"] == 1
        assert stats["heading_count"] == 0

    def test_single_heading(self):
        doc = _make_document(blocks=[_make_block("heading", "Title", heading_level=1)])
        stats = document_stats(doc)
        assert stats["block_count"] == 1
        assert stats["heading_count"] == 1
        assert stats["paragraph_count"] == 0

    def test_mixed_blocks(self):
        blocks = [
            _make_block("heading", "Chapter 1", heading_level=1),
            _make_block("paragraph", "Intro text"),
            _make_block("paragraph", "More text"),
            _make_block("heading", "Chapter 2", heading_level=2),
        ]
        doc = _make_document(blocks=blocks)
        stats = document_stats(doc)
        assert stats["block_count"] == 4
        assert stats["heading_count"] == 2
        assert stats["paragraph_count"] == 2

    def test_text_length_from_text_field(self):
        doc = _make_document(blocks=[_make_block("paragraph", "Hello")])
        stats = document_stats(doc)
        assert stats["total_text_length"] == 5

    def test_text_length_from_runs(self):
        runs = [_make_run("Hello "), _make_run("world")]
        block = _make_block("paragraph", "Hello world", runs=runs)
        doc = _make_document(blocks=[block])
        stats = document_stats(doc)
        assert stats["total_text_length"] == 11

    def test_runs_take_priority_over_text_field(self):
        # When runs present, text field not counted
        runs = [_make_run("Run text")]
        block = _make_block("paragraph", "Full text ignored", runs=runs)
        doc = _make_document(blocks=[block])
        stats = document_stats(doc)
        assert stats["total_text_length"] == 8  # "Run text" only


class TestDocumentStatsHyperlinks:
    """Hyperlink counting via runs with href."""

    def test_no_hyperlinks(self):
        runs = [_make_run("plain text")]
        block = _make_block("paragraph", "plain text", runs=runs)
        doc = _make_document(blocks=[block])
        stats = document_stats(doc)
        assert stats["hyperlink_count"] == 0

    def test_single_hyperlink(self):
        runs = [_make_run("click here", href="https://example.com")]
        block = _make_block("paragraph", "click here", runs=runs)
        doc = _make_document(blocks=[block])
        stats = document_stats(doc)
        assert stats["hyperlink_count"] == 1

    def test_multiple_hyperlinks_in_block(self):
        runs = [
            _make_run("link1", href="https://a.com"),
            _make_run(" and "),
            _make_run("link2", href="https://b.com"),
        ]
        block = _make_block("paragraph", "", runs=runs)
        doc = _make_document(blocks=[block])
        stats = document_stats(doc)
        assert stats["hyperlink_count"] == 2

    def test_hyperlinks_across_blocks(self):
        runs1 = [_make_run("link1", href="https://a.com")]
        runs2 = [_make_run("link2", href="https://b.com")]
        blocks = [
            _make_block("paragraph", "", runs=runs1),
            _make_block("paragraph", "", runs=runs2),
        ]
        doc = _make_document(blocks=blocks)
        stats = document_stats(doc)
        assert stats["hyperlink_count"] == 2


class TestDocumentStatsList:
    """List and list item counting."""

    def test_single_list_single_item(self):
        lst = _make_list([_make_list_item("Item 1")])
        doc = _make_document(lists=[lst])
        stats = document_stats(doc)
        assert stats["list_count"] == 1
        assert stats["list_item_count"] == 1

    def test_multiple_items(self):
        lst = _make_list([
            _make_list_item("Item 1"),
            _make_list_item("Item 2"),
            _make_list_item("Sub-item", level=2),
        ])
        doc = _make_document(lists=[lst])
        stats = document_stats(doc)
        assert stats["list_count"] == 1
        assert stats["list_item_count"] == 3

    def test_multiple_lists(self):
        lst1 = _make_list([_make_list_item("A"), _make_list_item("B")])
        lst2 = _make_list([_make_list_item("X")])
        doc = _make_document(lists=[lst1, lst2])
        stats = document_stats(doc)
        assert stats["list_count"] == 2
        assert stats["list_item_count"] == 3

    def test_list_text_length(self):
        lst = _make_list([_make_list_item("Hello"), _make_list_item("World")])
        doc = _make_document(lists=[lst])
        stats = document_stats(doc)
        assert stats["total_text_length"] == 10  # "Hello" + "World"


class TestDocumentStatsTable:
    """Table and cell counting."""

    def test_single_table_single_row(self):
        row = _make_table_row([_make_cell("a"), _make_cell("b")])
        table = _make_table([row])
        doc = _make_document(tables=[table])
        stats = document_stats(doc)
        assert stats["table_count"] == 1
        assert stats["table_cell_count"] == 2

    def test_table_multiple_rows(self):
        rows = [
            _make_table_row([_make_cell("r1c1"), _make_cell("r1c2")]),
            _make_table_row([_make_cell("r2c1"), _make_cell("r2c2")]),
        ]
        table = _make_table(rows)
        doc = _make_document(tables=[table])
        stats = document_stats(doc)
        assert stats["table_cell_count"] == 4

    def test_multiple_tables(self):
        t1 = _make_table([_make_table_row([_make_cell("a"), _make_cell("b")])])
        t2 = _make_table([_make_table_row([_make_cell("c")])])
        doc = _make_document(tables=[t1, t2])
        stats = document_stats(doc)
        assert stats["table_count"] == 2
        assert stats["table_cell_count"] == 3

    def test_table_text_length(self):
        row = _make_table_row([_make_cell("Hello"), _make_cell("Goodbye")])
        table = _make_table([row])
        doc = _make_document(tables=[table])
        stats = document_stats(doc)
        assert stats["total_text_length"] == 12  # "Hello" + "Goodbye"


class TestDocumentStatsContentList:
    """document_stats uses content list (R55 TC-0060) when present."""

    def test_content_list_overrides_separate_lists(self):
        # content list has 1 block, separate blocks list has 2
        content = [
            {"kind": "block", "data": _make_block("paragraph", "from content")},
        ]
        # Separate lists should NOT be used when content present
        blocks_extra = [
            _make_block("paragraph", "extra block 1"),
            _make_block("paragraph", "extra block 2"),
        ]
        doc = _make_document(blocks=blocks_extra, content=content)
        stats = document_stats(doc)
        assert stats["block_count"] == 1
        assert stats["paragraph_count"] == 1

    def test_content_list_mixed_kinds(self):
        content = [
            {"kind": "block", "data": _make_block("heading", "Title", heading_level=1)},
            {"kind": "block", "data": _make_block("paragraph", "Para")},
            {"kind": "list", "data": _make_list([_make_list_item("item")])},
            {"kind": "table", "data": _make_table([_make_table_row([_make_cell("c")])])},
        ]
        doc = _make_document(content=content)
        stats = document_stats(doc)
        assert stats["block_count"] == 2
        assert stats["heading_count"] == 1
        assert stats["paragraph_count"] == 1
        assert stats["list_count"] == 1
        assert stats["list_item_count"] == 1
        assert stats["table_count"] == 1
        assert stats["table_cell_count"] == 1

    def test_empty_content_list_falls_through_to_separate_lists(self):
        # Empty content list (or no content key) → use blocks/lists/tables
        blocks = [_make_block("paragraph", "standalone")]
        doc = _make_document(blocks=blocks)
        stats = document_stats(doc)
        assert stats["block_count"] == 1

    def test_content_unknown_kind_ignored(self):
        content = [
            {"kind": "unknown_future_type", "data": {}},
            {"kind": "block", "data": _make_block("paragraph", "real")},
        ]
        doc = _make_document(content=content)
        stats = document_stats(doc)
        assert stats["block_count"] == 1


class TestDocumentStatsCombined:
    """Combined document with blocks, lists, and tables."""

    def test_full_document(self):
        blocks = [
            _make_block("heading", "Title", heading_level=1),
            _make_block("paragraph", "Intro"),
        ]
        lists = [
            _make_list([_make_list_item("A"), _make_list_item("B")]),
        ]
        tables = [
            _make_table([_make_table_row([_make_cell("x"), _make_cell("y")])]),
        ]
        doc = _make_document(blocks=blocks, lists=lists, tables=tables)
        stats = document_stats(doc)
        assert stats["block_count"] == 2
        assert stats["heading_count"] == 1
        assert stats["paragraph_count"] == 1
        assert stats["list_count"] == 1
        assert stats["list_item_count"] == 2
        assert stats["table_count"] == 1
        assert stats["table_cell_count"] == 2
        # text: "Title" + "Intro" + "A" + "B" + "x" + "y" = 5+5+1+1+1+1 = 14
        assert stats["total_text_length"] == 14
