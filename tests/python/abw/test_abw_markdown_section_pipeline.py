"""
test_abw_markdown_section_pipeline.py -- ABW export_to_markdown + get_section_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-102
Tests export_to_markdown returns string, contains paragraph text, paragraphs separated,
get_section_count returns int, count >= 1.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    write_abw,
    export_to_markdown,
    get_section_count,
)

_PARAGRAPHS = [
    "First paragraph with content",
    "Second paragraph here",
    "Third and final paragraph",
]


def _make_model_and_file(tmp_path):
    model = create_abw(_PARAGRAPHS)
    dest = tmp_path / "doc.abw"
    write_abw(model, str(dest))
    return model, dest


def test_export_to_markdown_returns_string():
    model = create_abw(_PARAGRAPHS)
    md = export_to_markdown(model)
    assert isinstance(md, str)


def test_export_to_markdown_has_content():
    model = create_abw(_PARAGRAPHS)
    md = export_to_markdown(model)
    assert "First" in md
    assert "Second" in md


def test_export_to_markdown_paragraphs_separated():
    model = create_abw(_PARAGRAPHS)
    md = export_to_markdown(model)
    assert "\n\n" in md


def test_get_section_count_returns_int(tmp_path):
    model, dest = _make_model_and_file(tmp_path)
    count = get_section_count(str(dest))
    assert isinstance(count, int)


def test_get_section_count_at_least_one(tmp_path):
    model, dest = _make_model_and_file(tmp_path)
    count = get_section_count(str(dest))
    assert count >= 1
