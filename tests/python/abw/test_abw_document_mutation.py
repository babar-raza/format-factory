"""Tests for AbwDocument mutation API: add_paragraph() and save_to_file().

Sprint: ABW-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from abw.abw_codec import create_abw
from abw.models import AbwDocument


def _make_doc() -> AbwDocument:
    """Create a small AbwDocument with 2 paragraphs."""
    return AbwDocument(create_abw(["Hello", "World"]))


class TestAddParagraph:
    def test_add_paragraph_appends(self):
        doc = _make_doc()
        doc.add_paragraph("Third")
        assert doc.paragraphs[-1] == "Third"

    def test_add_paragraph_increments_count(self):
        doc = _make_doc()
        before = doc.paragraph_count
        doc.add_paragraph("New")
        assert doc.paragraph_count == before + 1

    def test_add_paragraph_none_raises(self):
        from abw.abw_codec import AbwError
        doc = _make_doc()
        with pytest.raises(AbwError):
            doc.add_paragraph(None)  # type: ignore[arg-type]

    def test_add_empty_string(self):
        doc = _make_doc()
        doc.add_paragraph("")
        assert doc.paragraphs[-1] == ""
        assert doc.paragraph_count == 3

    def test_add_multiple_paragraphs(self):
        doc = _make_doc()
        doc.add_paragraph("P3")
        doc.add_paragraph("P4")
        assert doc.paragraph_count == 4
        assert doc.paragraphs[2] == "P3"
        assert doc.paragraphs[3] == "P4"

    def test_existing_paragraphs_intact(self):
        doc = _make_doc()
        doc.add_paragraph("New")
        assert doc.paragraphs[0] == "Hello"
        assert doc.paragraphs[1] == "World"


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.abw"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        from abw.abw_codec import AbwError
        doc = _make_doc()
        with pytest.raises(AbwError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.abw"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_contains_paragraph_text(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.abw"
            doc.save_to_file(dest)
            content = dest.read_text(encoding="utf-8")
            assert "Hello" in content
            assert "World" in content


class TestMutationRoundtrip:
    def test_add_paragraph_roundtrip(self):
        """add_paragraph → save_to_file → from_file: new paragraph visible."""
        doc = _make_doc()
        doc.add_paragraph("Roundtrip")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.abw"
            doc.save_to_file(dest)
            reloaded = AbwDocument.from_file(dest)
            assert "Roundtrip" in reloaded.paragraphs

    def test_roundtrip_preserves_count(self):
        doc = _make_doc()
        doc.add_paragraph("P3")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.abw"
            doc.save_to_file(dest)
            reloaded = AbwDocument.from_file(dest)
            assert reloaded.paragraph_count == 3

    def test_roundtrip_existing_paragraphs_intact(self):
        doc = _make_doc()
        doc.add_paragraph("Extra")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.abw"
            doc.save_to_file(dest)
            reloaded = AbwDocument.from_file(dest)
            assert "Hello" in reloaded.paragraphs
            assert "World" in reloaded.paragraphs
