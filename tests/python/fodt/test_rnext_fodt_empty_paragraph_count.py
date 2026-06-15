"""Tests for document_empty_paragraph_count — product-healing pilot.

Verifies document_empty_paragraph_count correctly identifies empty paragraphs
(no runs, or whitespace-only runs) in FODT documents.
"""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_empty_paragraph_count, document_paragraph_count


def _doc(blocks):
    return {"blocks": blocks}


def _para(text=None, runs=None):
    b = {"type": "paragraph"}
    if runs is not None:
        b["runs"] = runs
    elif text is not None:
        b["runs"] = [{"text": text}]
    return b


def _heading(text):
    return {"type": "heading", "runs": [{"text": text}]}


class TestEmptyDocument:
    def test_no_blocks(self):
        assert document_empty_paragraph_count(_doc([])) == 0

    def test_missing_blocks_key(self):
        assert document_empty_paragraph_count({}) == 0


class TestNonEmptyParagraphs:
    def test_single_paragraph_with_text(self):
        assert document_empty_paragraph_count(_doc([_para("Hello")])) == 0

    def test_multiple_nonempty_paragraphs(self):
        doc = _doc([_para("A"), _para("B"), _para("C")])
        assert document_empty_paragraph_count(doc) == 0

    def test_paragraph_with_multiple_runs(self):
        doc = _doc([{"type": "paragraph", "runs": [{"text": "a"}, {"text": "b"}]}])
        assert document_empty_paragraph_count(doc) == 0


class TestEmptyParagraphs:
    def test_paragraph_no_runs(self):
        assert document_empty_paragraph_count(_doc([_para(runs=[])])) == 1

    def test_paragraph_missing_runs_key(self):
        assert document_empty_paragraph_count(_doc([{"type": "paragraph"}])) == 1

    def test_paragraph_empty_text(self):
        assert document_empty_paragraph_count(_doc([_para("")])) == 1

    def test_paragraph_whitespace_only(self):
        assert document_empty_paragraph_count(_doc([_para("   ")])) == 1

    def test_paragraph_tab_only(self):
        assert document_empty_paragraph_count(_doc([_para("\t")])) == 1


class TestMixedContent:
    def test_mixed_empty_and_nonempty(self):
        doc = _doc([_para("Hello"), _para(""), _para("World"), _para(runs=[])])
        assert document_empty_paragraph_count(doc) == 2

    def test_heading_not_counted(self):
        doc = _doc([_heading("Title"), _para("")])
        assert document_empty_paragraph_count(doc) == 1

    def test_consistency_with_paragraph_count(self):
        doc = _doc([_para("A"), _para(""), _para("B"), _para(runs=[])])
        total = document_paragraph_count(doc)
        empty = document_empty_paragraph_count(doc)
        assert total == 4
        assert empty == 2
        assert empty <= total


class TestEdgeCases:
    def test_run_with_none_text(self):
        doc = _doc([{"type": "paragraph", "runs": [{"text": None}]}])
        assert document_empty_paragraph_count(doc) == 1

    def test_multiple_whitespace_runs(self):
        doc = _doc([{"type": "paragraph", "runs": [{"text": " "}, {"text": "\t"}]}])
        assert document_empty_paragraph_count(doc) == 1

    def test_one_nonempty_run_among_empty(self):
        doc = _doc([{"type": "paragraph", "runs": [{"text": ""}, {"text": "x"}]}])
        assert document_empty_paragraph_count(doc) == 0
