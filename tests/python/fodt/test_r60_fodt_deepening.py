"""
test_r60_fodt_deepening.py — R60 Train G: FODT product deepening tests.

Tests for 2 new R60 capabilities:
1. document_word_count(document)    — word count by content category
2. document_table_summary(document) — compact table structure summary

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fodt.neutral_model import document_word_count, document_table_summary


def _make_doc(blocks=None, lists=None, tables=None, content=None):
    doc = {
        "format_id": "fodt",
        "spec_version": "1.0",
        "odf_version_attr": "1.2",
        "mimetype": None,
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }
    if content is not None:
        doc["content"] = content
    return doc


def _block(text, btype="paragraph", level=None):
    b = {"type": btype, "text": text}
    if level is not None:
        b["heading_level"] = level
    return b


def _block_with_runs(runs):
    return {"type": "paragraph", "text": "", "runs": runs}


def _run(text, href=None):
    r = {"text": text}
    if href:
        r["href"] = href
    return r


def _list_obj(items):
    return {"items": [{"text": t, "level": 1} for t in items]}


def _table(rows):
    return {"rows": [{"cells": [{"text": c} for c in row]} for row in rows]}


def _content_item(kind, data):
    return {"kind": kind, "data": data}


# ===========================================================================
# document_word_count
# ===========================================================================

class TestDocumentWordCount:
    def test_empty_document(self):
        doc = _make_doc()
        result = document_word_count(doc)
        assert result["total_words"] == 0
        assert result["block_words"] == 0
        assert result["list_words"] == 0
        assert result["table_words"] == 0

    def test_single_block(self):
        doc = _make_doc(blocks=[_block("hello world")])
        result = document_word_count(doc)
        assert result["block_words"] == 2
        assert result["total_words"] == 2

    def test_block_with_multiple_words(self):
        doc = _make_doc(blocks=[_block("one two three four five")])
        result = document_word_count(doc)
        assert result["block_words"] == 5

    def test_list_words(self):
        doc = _make_doc(lists=[_list_obj(["first item", "second item here"])])
        result = document_word_count(doc)
        assert result["list_words"] == 5
        assert result["total_words"] == 5

    def test_table_words(self):
        doc = _make_doc(tables=[_table([["hello world", "foo bar"]])])
        result = document_word_count(doc)
        assert result["table_words"] == 4

    def test_combined_all_categories(self):
        doc = _make_doc(
            blocks=[_block("one two")],
            lists=[_list_obj(["three four five"])],
            tables=[_table([["six seven"]])],
        )
        result = document_word_count(doc)
        assert result["block_words"] == 2
        assert result["list_words"] == 3
        assert result["table_words"] == 2
        assert result["total_words"] == 7

    def test_block_with_runs(self):
        doc = _make_doc(blocks=[_block_with_runs([_run("hello "), _run("world")])])
        result = document_word_count(doc)
        assert result["block_words"] == 2

    def test_empty_text_not_counted(self):
        doc = _make_doc(blocks=[_block("")])
        result = document_word_count(doc)
        assert result["block_words"] == 0

    def test_content_list_overrides_separate_lists(self):
        content = [
            _content_item("block", _block("one two three")),
            _content_item("list", _list_obj(["four five"])),
            _content_item("table", _table([["six"]])),
        ]
        # Provide blocks/lists too, but content should win
        doc = _make_doc(
            blocks=[_block("ignored")],
            lists=[_list_obj(["ignored"])],
            content=content,
        )
        result = document_word_count(doc)
        assert result["block_words"] == 3
        assert result["list_words"] == 2
        assert result["table_words"] == 1
        assert result["total_words"] == 6

    def test_returns_dict_with_required_keys(self):
        doc = _make_doc()
        result = document_word_count(doc)
        assert "total_words" in result
        assert "block_words" in result
        assert "list_words" in result
        assert "table_words" in result

    def test_multiple_blocks(self):
        doc = _make_doc(blocks=[
            _block("word"),
            _block("two words"),
            _block("three four five"),
        ])
        result = document_word_count(doc)
        assert result["block_words"] == 6


# ===========================================================================
# document_table_summary
# ===========================================================================

class TestDocumentTableSummary:
    def test_no_tables(self):
        doc = _make_doc()
        result = document_table_summary(doc)
        assert result == []

    def test_single_table_basic(self):
        doc = _make_doc(tables=[_table([["a", "b"], ["c", "d"]])])
        result = document_table_summary(doc)
        assert len(result) == 1
        t = result[0]
        assert t["index"] == 0
        assert t["row_count"] == 2
        assert t["column_count"] == 2
        assert t["cell_count"] == 4

    def test_uneven_rows_max_column(self):
        raw = {"rows": [
            {"cells": [{"text": "a"}, {"text": "b"}, {"text": "c"}]},
            {"cells": [{"text": "x"}]},
        ]}
        doc = _make_doc(tables=[raw])
        result = document_table_summary(doc)
        assert result[0]["column_count"] == 3
        assert result[0]["cell_count"] == 4

    def test_empty_table(self):
        doc = _make_doc(tables=[{"rows": []}])
        result = document_table_summary(doc)
        assert result[0]["row_count"] == 0
        assert result[0]["column_count"] == 0
        assert result[0]["cell_count"] == 0

    def test_multiple_tables(self):
        doc = _make_doc(tables=[
            _table([["a", "b"]]),
            _table([["c"], ["d"], ["e"]]),
        ])
        result = document_table_summary(doc)
        assert len(result) == 2
        assert result[0]["index"] == 0
        assert result[0]["row_count"] == 1
        assert result[0]["column_count"] == 2
        assert result[1]["index"] == 1
        assert result[1]["row_count"] == 3
        assert result[1]["column_count"] == 1

    def test_content_list_tables_respected(self):
        content = [
            _content_item("block", _block("intro")),
            _content_item("table", _table([["x", "y", "z"]])),
        ]
        doc = _make_doc(
            tables=[_table([["ignored"]])],
            content=content,
        )
        result = document_table_summary(doc)
        assert len(result) == 1
        assert result[0]["column_count"] == 3

    def test_returns_list(self):
        doc = _make_doc(tables=[_table([["a"]])])
        result = document_table_summary(doc)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

    def test_required_keys_present(self):
        doc = _make_doc(tables=[_table([["a"]])])
        result = document_table_summary(doc)
        for key in ("index", "row_count", "column_count", "cell_count"):
            assert key in result[0], f"Missing key: {key}"

    def test_large_table(self):
        rows = [["cell" for _ in range(5)] for _ in range(4)]
        doc = _make_doc(tables=[_table(rows)])
        result = document_table_summary(doc)
        assert result[0]["row_count"] == 4
        assert result[0]["column_count"] == 5
        assert result[0]["cell_count"] == 20
