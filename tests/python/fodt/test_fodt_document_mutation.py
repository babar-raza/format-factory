"""Tests for FodtDocument mutation API: add_paragraph() and save_to_file().

Sprint: FODT-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from fodt.models import FodtDocument
from fodt.exceptions import FodtError


SAMPLE_FODT = Path("samples/by-format/fodt/minimal-document.fodt")


class TestAddParagraph:
    def test_add_paragraph_appends(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        before = doc.block_count
        doc.add_paragraph("New paragraph")
        assert doc.block_count == before + 1

    def test_add_paragraph_text_correct(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        doc.add_paragraph("Check text")
        blocks = doc._data.get("blocks", [])
        assert blocks[-1]["text"] == "Check text"

    def test_add_paragraph_none_raises(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        with pytest.raises(FodtError):
            doc.add_paragraph(None)  # type: ignore[arg-type]

    def test_add_paragraph_empty_string(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        before = doc.block_count
        doc.add_paragraph("")
        assert doc.block_count == before + 1

    def test_add_multiple_paragraphs(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        before = doc.block_count
        doc.add_paragraph("P1")
        doc.add_paragraph("P2")
        assert doc.block_count == before + 2

    def test_existing_blocks_intact(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        existing = [b["text"] for b in doc._data.get("blocks", [])]
        doc.add_paragraph("Extra")
        after = [b["text"] for b in doc._data.get("blocks", [])[:-1]]
        assert after == existing


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.fodt"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        with pytest.raises(FodtError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.fodt"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.fodt"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_add_paragraph_roundtrip(self):
        """add_paragraph → save_to_file → from_file: new paragraph text visible."""
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        doc.add_paragraph("RoundtripText")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.fodt"
            doc.save_to_file(dest)
            reloaded = FodtDocument.from_file(str(dest))
            texts = [b["text"] for b in reloaded._data.get("blocks", [])]
            assert "RoundtripText" in texts

    def test_roundtrip_count_preserved(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        original_count = doc.block_count
        doc.add_paragraph("Extra")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.fodt"
            doc.save_to_file(dest)
            reloaded = FodtDocument.from_file(str(dest))
            assert reloaded.block_count == original_count + 1

    def test_roundtrip_is_valid_fodt(self):
        doc = FodtDocument.from_file(str(SAMPLE_FODT))
        doc.add_paragraph("Test")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.fodt"
            doc.save_to_file(dest)
            reloaded = FodtDocument.from_file(str(dest))
            assert reloaded.block_count > 0
