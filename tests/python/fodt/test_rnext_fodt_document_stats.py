"""
test_rnext_fodt_document_stats.py -- Dedicated test coverage for document_stats.

Gap: GAP-FODT-FOSS-DOCUMENT_STA-001 (missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_stats


def _doc(blocks=None, lists=None, tables=None):
    d = {"blocks": blocks or []}
    if lists is not None:
        d["lists"] = lists
    if tables is not None:
        d["tables"] = tables
    return d

def _para(text=""):
    return {"type": "paragraph", "text": text}

def _heading(text="", level=1):
    return {"type": "heading", "text": text, "level": level}


class TestDocumentStats:
    def test_returns_dict(self):
        assert isinstance(document_stats(_doc()), dict)

    def test_empty_doc(self):
        r = document_stats(_doc())
        assert r["block_count"] == 0
        assert r["paragraph_count"] == 0
        assert r["heading_count"] == 0

    def test_paragraph_count(self):
        r = document_stats(_doc([_para("A"), _para("B"), _para("C")]))
        assert r["paragraph_count"] == 3
        assert r["block_count"] == 3

    def test_heading_count(self):
        r = document_stats(_doc([_heading("H1"), _heading("H2")]))
        assert r["heading_count"] == 2

    def test_mixed_blocks(self):
        r = document_stats(_doc([_para("P"), _heading("H"), _para("P2")]))
        assert r["paragraph_count"] == 2
        assert r["heading_count"] == 1
        assert r["block_count"] == 3

    def test_list_count(self):
        r = document_stats(_doc(lists=[{"items": [{"text": "a"}, {"text": "b"}]}]))
        assert r["list_count"] >= 1

    def test_table_count(self):
        r = document_stats(_doc(tables=[{"rows": []}]))
        assert r["table_count"] >= 1

    def test_has_expected_keys(self):
        r = document_stats(_doc())
        for key in ["block_count", "paragraph_count", "heading_count"]:
            assert key in r
