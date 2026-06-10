"""Tests for abw.abw_codec.export_to_markdown() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, export_to_markdown


def test_single_paragraph():
    model = create_abw(["Hello world"])
    md = export_to_markdown(model)
    assert md == "Hello world"


def test_two_paragraphs_separated_by_blank_line():
    model = create_abw(["First", "Second"])
    md = export_to_markdown(model)
    assert md == "First\n\nSecond"


def test_three_paragraphs():
    model = create_abw(["A", "B", "C"])
    md = export_to_markdown(model)
    assert md == "A\n\nB\n\nC"


def test_empty_model():
    model = create_abw([])
    md = export_to_markdown(model)
    assert md == ""


def test_returns_string():
    model = create_abw(["text"])
    assert isinstance(export_to_markdown(model), str)


def test_preserves_content():
    model = create_abw(["# Heading", "Paragraph text"])
    md = export_to_markdown(model)
    assert "# Heading" in md
    assert "Paragraph text" in md


def test_blank_line_between_multiple():
    model = create_abw(["one", "two", "three"])
    md = export_to_markdown(model)
    parts = md.split("\n\n")
    assert len(parts) == 3
