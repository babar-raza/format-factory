"""
Tests for ABW write_abw() and create_abw() — R117 pilot.

Sprint: FORMAT-FACTORY-HOST-PROOFED-AUTONOMOUS-FORMAT-PILOT-001
Track: python-foss

Verifies:
- create_abw() produces a valid model dict
- write_abw() serializes to valid XML
- Roundtrip: create → write → load → verify content
"""

from __future__ import annotations

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src" / "python"))

from abw.abw_codec import (
    AbwError,
    create_abw,
    write_abw,
    load,
    extract_text,
)


# ---------------------------------------------------------------------------
# create_abw()
# ---------------------------------------------------------------------------

class TestCreateAbw:
    def test_returns_dict(self):
        model = create_abw(["Hello"])
        assert isinstance(model, dict)

    def test_is_abw_true(self):
        model = create_abw(["Hello"])
        assert model["is_abw"] is True

    def test_paragraph_count(self):
        model = create_abw(["First", "Second", "Third"])
        assert model["paragraph_count"] == 3

    def test_empty_creates_zero_paragraphs(self):
        model = create_abw([])
        assert model["paragraph_count"] == 0
        assert model["paragraphs"] == []

    def test_paragraphs_list(self):
        paragraphs = ["Alpha", "Beta"]
        model = create_abw(paragraphs)
        assert model["paragraphs"] == ["Alpha", "Beta"]

    def test_section_count_always_one(self):
        model = create_abw(["a", "b"])
        assert model["section_count"] == 1


# ---------------------------------------------------------------------------
# write_abw()
# ---------------------------------------------------------------------------

class TestWriteAbw:
    def test_writes_file(self, tmp_path):
        model = create_abw(["Test paragraph"])
        dest = tmp_path / "out.abw"
        write_abw(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_writes_valid_xml(self, tmp_path):
        model = create_abw(["Hello world"])
        dest = tmp_path / "out.abw"
        write_abw(model, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content
        assert "<abiword" in content
        assert "<section" in content
        assert "Hello world" in content

    def test_invalid_model_raises(self, tmp_path):
        with pytest.raises(AbwError):
            write_abw({"is_abw": False}, tmp_path / "out.abw")

    def test_non_dict_raises(self, tmp_path):
        with pytest.raises(AbwError):
            write_abw("not a model", tmp_path / "out.abw")


# ---------------------------------------------------------------------------
# Roundtrip: create → write → load → verify
# ---------------------------------------------------------------------------

class TestRoundtrip:
    def test_single_paragraph_roundtrip(self, tmp_path):
        model = create_abw(["Hello, roundtrip!"])
        dest = tmp_path / "roundtrip.abw"
        write_abw(model, dest)
        loaded = load(dest)
        assert loaded["is_abw"] is True
        assert loaded["paragraph_count"] == 1
        assert "Hello, roundtrip!" in loaded["paragraphs"]

    def test_multiple_paragraphs_roundtrip(self, tmp_path):
        paragraphs = ["First", "Second", "Third"]
        model = create_abw(paragraphs)
        dest = tmp_path / "multi.abw"
        write_abw(model, dest)
        loaded = load(dest)
        assert loaded["paragraph_count"] == 3
        assert loaded["paragraphs"] == ["First", "Second", "Third"]

    def test_empty_document_roundtrip(self, tmp_path):
        model = create_abw([])
        dest = tmp_path / "empty.abw"
        write_abw(model, dest)
        loaded = load(dest)
        assert loaded["is_abw"] is True
        assert loaded["paragraph_count"] == 0

    def test_extract_text_after_roundtrip(self, tmp_path):
        model = create_abw(["Extract this", "And this"])
        dest = tmp_path / "extract.abw"
        write_abw(model, dest)
        texts = extract_text(dest)
        assert "Extract this" in texts
        assert "And this" in texts

    def test_unicode_roundtrip(self, tmp_path):
        model = create_abw(["Héllo wörld", "日本語"])
        dest = tmp_path / "unicode.abw"
        write_abw(model, dest)
        loaded = load(dest)
        assert loaded["paragraph_count"] == 2
        assert "Héllo wörld" in loaded["paragraphs"]
