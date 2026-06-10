"""ABW roundtrip tests: create → write → load → compare.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001
TC-PRODUCT-ABW-ROUNDTRIP
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, write_abw, load


class TestAbwRoundtrip:
    def test_roundtrip_preserves_paragraphs(self, tmp_path):
        paragraphs = ["Hello, world!", "Second paragraph.", "Third."]
        model = create_abw(paragraphs)
        dest = tmp_path / "test.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2["paragraphs"] == paragraphs

    def test_roundtrip_preserves_paragraph_count(self, tmp_path):
        paragraphs = ["One", "Two", "Three", "Four"]
        model = create_abw(paragraphs)
        dest = tmp_path / "test.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2["paragraph_count"] == len(paragraphs)

    def test_roundtrip_empty_document(self, tmp_path):
        model = create_abw([])
        dest = tmp_path / "empty.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2["paragraphs"] == []

    def test_roundtrip_single_paragraph(self, tmp_path):
        model = create_abw(["Only paragraph."])
        dest = tmp_path / "single.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2["paragraphs"] == ["Only paragraph."]

    def test_roundtrip_unicode_content(self, tmp_path):
        paragraphs = ["Héllo wörld", "日本語テスト", "Αβγδεζ"]
        model = create_abw(paragraphs)
        dest = tmp_path / "unicode.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2["paragraphs"] == paragraphs

    def test_roundtrip_writes_file(self, tmp_path):
        model = create_abw(["content"])
        dest = tmp_path / "out.abw"
        write_abw(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_roundtrip_file_is_valid_xml(self, tmp_path):
        import xml.etree.ElementTree as ET
        model = create_abw(["paragraph"])
        dest = tmp_path / "out.abw"
        write_abw(model, dest)
        # Should parse without exception
        tree = ET.parse(str(dest))
        assert tree is not None

    def test_roundtrip_is_abw_flag(self, tmp_path):
        model = create_abw(["test"])
        dest = tmp_path / "out.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2.get("is_abw") is True

    def test_roundtrip_preserves_special_characters(self, tmp_path):
        paragraphs = ["<bold> & 'quoted' text", "Line with\ttab"]
        model = create_abw(paragraphs)
        dest = tmp_path / "special.abw"
        write_abw(model, dest)
        model2 = load(dest)
        assert model2["paragraphs"] == paragraphs

    def test_double_roundtrip(self, tmp_path):
        """Load → write → reload → write again → reload: should still match."""
        paragraphs = ["First", "Second"]
        model = create_abw(paragraphs)
        dest1 = tmp_path / "round1.abw"
        dest2 = tmp_path / "round2.abw"
        write_abw(model, dest1)
        model2 = load(dest1)
        write_abw(model2, dest2)
        model3 = load(dest2)
        assert model3["paragraphs"] == paragraphs
