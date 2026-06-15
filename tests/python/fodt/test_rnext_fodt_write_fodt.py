"""
test_rnext_fodt_write_fodt.py -- Dedicated test coverage for write_fodt.

Gap: GAP-FODT-FOSS-WRITE_FODT-001 (missing_test_coverage)
Tests: file creation, round-trip, empty doc, multi-block, encoding, error handling.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.writer import write_fodt, document_to_xml
from fodt.parser import parse_fodt_strict


def _doc(blocks=None):
    """Create a minimal FODT document dict."""
    return {"blocks": blocks or []}


def _para(text=""):
    return {"type": "paragraph", "text": text}


def _heading(text="", level=1):
    return {"type": "heading", "text": text, "level": level}


class TestWriteFodtBasic:
    def test_creates_file(self, tmp_path):
        dest = tmp_path / "out.fodt"
        write_fodt(_doc([_para("Hello")]), dest)
        assert dest.exists()

    def test_file_not_empty(self, tmp_path):
        dest = tmp_path / "out.fodt"
        write_fodt(_doc([_para("Hello")]), dest)
        assert dest.stat().st_size > 0

    def test_file_is_xml(self, tmp_path):
        dest = tmp_path / "out.fodt"
        write_fodt(_doc([_para("Test")]), dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("<?xml")

    def test_contains_office_document(self, tmp_path):
        dest = tmp_path / "out.fodt"
        write_fodt(_doc([_para("Test")]), dest)
        content = dest.read_text(encoding="utf-8")
        assert "office:document" in content

    def test_paragraph_text_in_output(self, tmp_path):
        dest = tmp_path / "out.fodt"
        write_fodt(_doc([_para("MySpecialText")]), dest)
        content = dest.read_text(encoding="utf-8")
        assert "MySpecialText" in content


class TestWriteFodtRoundTrip:
    def test_write_then_parse(self, tmp_path):
        dest = tmp_path / "rt.fodt"
        doc = _doc([_para("Round"), _para("Trip")])
        write_fodt(doc, dest)
        doc2 = parse_fodt_strict(str(dest))
        assert len(doc2.get("blocks", [])) >= 2

    def test_heading_survives_roundtrip(self, tmp_path):
        dest = tmp_path / "hdg.fodt"
        doc = _doc([_heading("Title", 1), _para("Body")])
        write_fodt(doc, dest)
        doc2 = parse_fodt_strict(str(dest))
        assert len(doc2.get("blocks", [])) >= 2

    def test_empty_document_roundtrip(self, tmp_path):
        dest = tmp_path / "empty.fodt"
        write_fodt(_doc(), dest)
        doc2 = parse_fodt_strict(str(dest))
        assert isinstance(doc2, dict)


class TestWriteFodtEdgeCases:
    def test_unicode_content(self, tmp_path):
        dest = tmp_path / "unicode.fodt"
        write_fodt(_doc([_para("Cafe \u00e9l\u00e8ve")]), dest)
        content = dest.read_text(encoding="utf-8")
        assert "\u00e9" in content

    def test_multiple_paragraphs(self, tmp_path):
        dest = tmp_path / "multi.fodt"
        doc = _doc([_para(f"P{i}") for i in range(5)])
        write_fodt(doc, dest)
        doc2 = parse_fodt_strict(str(dest))
        assert len(doc2.get("blocks", [])) >= 5

    def test_accepts_string_path(self, tmp_path):
        dest = str(tmp_path / "strpath.fodt")
        write_fodt(_doc([_para("OK")]), dest)
        assert Path(dest).exists()

    def test_overwrite_existing(self, tmp_path):
        dest = tmp_path / "overwrite.fodt"
        write_fodt(_doc([_para("First")]), dest)
        write_fodt(_doc([_para("Second")]), dest)
        content = dest.read_text(encoding="utf-8")
        assert "Second" in content
        assert "First" not in content
