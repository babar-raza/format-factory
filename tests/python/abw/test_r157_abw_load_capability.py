"""
test_r157_abw_load_capability.py — Capability coverage test for ABW load function.

Closes GAP-ABW-FOSS-LOAD-001 (missing_test_coverage).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))
from abw.abw_codec import load, create_abw, write_abw


def _make_abw(paragraphs: list[str]) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".abw", delete=False) as f:
        path = Path(f.name)
    doc = create_abw(paragraphs)
    write_abw(doc, str(path))
    data = path.read_bytes()
    path.unlink()
    return data


class TestAbwLoadCapability:
    def test_load_returns_dict(self):
        data = _make_abw(["Hello"])
        result = load(data)
        assert isinstance(result, dict)

    def test_load_has_paragraphs(self):
        data = _make_abw(["First", "Second"])
        result = load(data)
        assert "paragraphs" in result
        assert len(result["paragraphs"]) == 2

    def test_load_paragraph_content(self):
        data = _make_abw(["Test content"])
        result = load(data)
        assert result["paragraphs"][0] == "Test content"

    def test_load_from_path(self, tmp_path):
        doc = create_abw(["Path test"])
        p = tmp_path / "test.abw"
        write_abw(doc, str(p))
        result = load(str(p))
        assert result["paragraphs"][0] == "Path test"

    def test_load_empty_document(self):
        data = _make_abw([])
        result = load(data)
        assert result["paragraph_count"] == 0

    def test_load_unicode(self):
        data = _make_abw(["Unicode: \u00e9\u00e8\u00ea\u00eb \u00fc\u00f6\u00e4"])
        result = load(data)
        assert "\u00e9" in result["paragraphs"][0]

    def test_load_section_count(self):
        data = _make_abw(["A", "B", "C"])
        result = load(data)
        assert "section_count" in result
