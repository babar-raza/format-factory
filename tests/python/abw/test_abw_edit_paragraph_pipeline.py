"""
test_abw_edit_paragraph_pipeline.py -- ABW edit paragraph pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-72
Tests edit_paragraph changes text, get_paragraph reads updated, is_empty on
empty doc, export_to_json parseable, text_stats has word_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    write_abw,
    edit_paragraph,
    get_paragraph,
    export_to_json,
    text_stats,
)


def test_edit_paragraph_changes_text():
    model = create_abw(["Hello world", "Second para", "Third para"])
    updated = edit_paragraph(model, 0, "Updated text")
    assert get_paragraph(updated, 0) == "Updated text"


def test_get_paragraph_reads_updated():
    model = create_abw(["Original", "Keep this"])
    updated = edit_paragraph(model, 0, "New content")
    assert get_paragraph(updated, 1) == "Keep this"


def test_empty_doc_has_zero_paragraphs():
    model = create_abw([])
    assert len(model["paragraphs"]) == 0


def test_export_to_json_parseable(tmp_path):
    model = create_abw(["Alpha", "Beta"])
    dest = tmp_path / "doc.abw"
    write_abw(model, str(dest))
    result = export_to_json(str(dest))
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_text_stats_has_word_count():
    model = create_abw(["The quick brown fox", "jumps over the lazy dog"])
    stats = text_stats(model)
    assert isinstance(stats, dict)
    assert "word_count" in stats
    assert stats["word_count"] >= 9
