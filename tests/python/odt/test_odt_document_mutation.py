"""Tests for OdtModelDocument mutation API: add_paragraph() and save_to_file().

Sprint: ODT-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from odt.models import OdtModelDocument
from odt.odt_parser import OdtError


SAMPLE_ODT = Path("samples/by-format/odt/valid/two-paragraphs.odt")


class TestAddParagraph:
    def test_add_paragraph_appends(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        before = doc.paragraph_count
        doc.add_paragraph("New paragraph")
        assert doc.paragraph_count == before + 1

    def test_add_paragraph_text_correct(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        doc.add_paragraph("Check text")
        assert doc.paragraphs[-1].text == "Check text"

    def test_add_paragraph_none_raises(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        with pytest.raises(OdtError):
            doc.add_paragraph(None)  # type: ignore[arg-type]

    def test_add_paragraph_empty_string(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        before = doc.paragraph_count
        doc.add_paragraph("")
        assert doc.paragraph_count == before + 1

    def test_add_multiple_paragraphs(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        before = doc.paragraph_count
        doc.add_paragraph("P1")
        doc.add_paragraph("P2")
        assert doc.paragraph_count == before + 2

    def test_existing_paragraphs_intact(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        existing = [p.text for p in doc.paragraphs]
        doc.add_paragraph("Extra")
        after = [p.text for p in doc.paragraphs[:-1]]
        assert after == existing


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.odt"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        with pytest.raises(OdtError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.odt"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.odt"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_add_paragraph_roundtrip(self):
        """add_paragraph → save_to_file → from_file: new paragraph text visible."""
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        doc.add_paragraph("RoundtripText")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.odt"
            doc.save_to_file(dest)
            reloaded = OdtModelDocument.from_file(dest)
            texts = [p.text for p in reloaded.paragraphs]
            assert "RoundtripText" in texts

    def test_roundtrip_count_preserved(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        original_count = doc.paragraph_count
        doc.add_paragraph("Extra")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.odt"
            doc.save_to_file(dest)
            reloaded = OdtModelDocument.from_file(dest)
            assert reloaded.paragraph_count == original_count + 1

    def test_roundtrip_is_valid_odt(self):
        doc = OdtModelDocument.from_file(SAMPLE_ODT)
        doc.add_paragraph("Test")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.odt"
            doc.save_to_file(dest)
            reloaded = OdtModelDocument.from_file(dest)
            assert reloaded.paragraph_count > 0
