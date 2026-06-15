"""Dogfood: ABW create → write → extract text → export pipeline.

Demonstrates: create ABW model → write → extract text → export to HTML → export to plain text.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import (
    create_abw,
    write_abw,
    extract_text,
    export_to_html,
    export_to_plain_text,
    get_section_count,
    probe_abw,
)


def _make_abw_file(tmp_path: Path) -> Path:
    """Create an ABW document with known paragraphs."""
    paragraphs = [
        "Introduction to Format Factory",
        "Format Factory is a multi-format file conversion library.",
        "It supports document, spreadsheet, image, and archive formats.",
        "This document demonstrates the ABW write and extract pipeline.",
        "Conclusion: ABW round-trip works correctly.",
    ]
    model = create_abw(paragraphs)
    p = tmp_path / "sample.abw"
    write_abw(model, str(p))
    return p


class TestDogfoodAbwTextExtraction:
    @pytest.fixture
    def abw_file(self, tmp_path):
        return _make_abw_file(tmp_path)

    def test_write_creates_file(self, abw_file):
        """ABW file is created on disk."""
        assert abw_file.exists()
        assert abw_file.stat().st_size > 0

    def test_probe(self, abw_file):
        """probe_abw identifies the file as ABW."""
        assert probe_abw(str(abw_file)) is True

    def test_extract_text(self, abw_file):
        """Text extraction returns all paragraphs."""
        texts = extract_text(str(abw_file))
        assert isinstance(texts, list)
        assert len(texts) >= 5
        combined = " ".join(texts)
        assert "Format Factory" in combined
        assert "Conclusion" in combined

    def test_export_to_html(self, abw_file):
        """HTML export produces valid HTML with content."""
        html = export_to_html(str(abw_file))
        assert isinstance(html, str)
        assert "<" in html  # Contains HTML tags
        assert "Format Factory" in html

    def test_export_to_plain_text(self, abw_file):
        """Plain text export contains document content."""
        model = create_abw(["Test paragraph one.", "Test paragraph two."])
        text = export_to_plain_text(model)
        assert isinstance(text, str)
        assert "Test paragraph" in text

    def test_section_count(self, abw_file):
        """Section count is at least 1."""
        count = get_section_count(str(abw_file))
        assert count >= 1
