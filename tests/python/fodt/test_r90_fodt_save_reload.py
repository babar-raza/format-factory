"""Tests for FODT save-same-format and reload-and-verify capabilities.

Gap closure: GAP-FODT-COMM-SAVE_SAME_FO-001, GAP-FODT-COMM-RELOAD_AND_V-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import parse_fodt_strict, write_fodt

SAMPLES = _REPO / "samples" / "by-format" / "fodt"


class TestFodtSaveSameFormat:
    def test_minimal_roundtrip(self, tmp_path):
        src = SAMPLES / "minimal-document.fodt"
        doc = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_headings_roundtrip(self, tmp_path):
        src = SAMPLES / "headings-and-paragraphs.fodt"
        doc = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_list_roundtrip(self, tmp_path):
        src = SAMPLES / "list-basic.fodt"
        doc = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc, out)
        assert out.exists()

    def test_table_roundtrip(self, tmp_path):
        src = SAMPLES / "table-basic.fodt"
        doc = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc, out)
        assert out.exists()


class TestFodtReloadAndVerify:
    def test_minimal_reload_produces_valid_doc(self, tmp_path):
        src = SAMPLES / "minimal-document.fodt"
        doc1 = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc1, out)
        doc2 = parse_fodt_strict(out)
        assert isinstance(doc2, dict)

    def test_headings_reload_preserves_structure(self, tmp_path):
        src = SAMPLES / "headings-and-paragraphs.fodt"
        doc1 = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc1, out)
        doc2 = parse_fodt_strict(out)
        assert doc1.get("paragraph_count") == doc2.get("paragraph_count")

    def test_reload_preserves_block_count(self, tmp_path):
        src = SAMPLES / "minimal-document.fodt"
        doc1 = parse_fodt_strict(src)
        out = tmp_path / "out.fodt"
        write_fodt(doc1, out)
        doc2 = parse_fodt_strict(out)
        b1 = doc1.get("blocks", [])
        b2 = doc2.get("blocks", [])
        assert len(b1) == len(b2)
