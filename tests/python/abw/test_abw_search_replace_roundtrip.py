"""
test_abw_search_replace_roundtrip.py -- ABW search+replace+write+reload roundtrip.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-21
Tests that search_replace_paragraph mutations persist after write_abw + reload.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "abw"

from abw.abw_codec import (
    load,
    create_abw,
    write_abw,
    search_replace_paragraph,
    get_paragraph,
    get_paragraph_count,
)


def test_search_replace_persists_after_write_reload(tmp_path):
    m = load(str(_SAMPLES / "two-paragraphs.abw"))
    m2 = search_replace_paragraph(m, "First", "Modified")
    dest = tmp_path / "out.abw"
    write_abw(m2, str(dest))
    m3 = load(str(dest))
    assert "Modified" in get_paragraph(m3, 0)


def test_original_term_removed_after_replace(tmp_path):
    m = load(str(_SAMPLES / "two-paragraphs.abw"))
    m2 = search_replace_paragraph(m, "First", "Modified")
    dest = tmp_path / "out.abw"
    write_abw(m2, str(dest))
    m3 = load(str(dest))
    assert "First" not in get_paragraph(m3, 0)


def test_untouched_paragraph_unchanged(tmp_path):
    m = load(str(_SAMPLES / "two-paragraphs.abw"))
    m2 = search_replace_paragraph(m, "First", "Modified")
    dest = tmp_path / "out.abw"
    write_abw(m2, str(dest))
    m3 = load(str(dest))
    assert get_paragraph(m3, 1) == "Second paragraph."


def test_paragraph_count_unchanged_after_replace(tmp_path):
    m = load(str(_SAMPLES / "two-paragraphs.abw"))
    m2 = search_replace_paragraph(m, "paragraph", "section")
    dest = tmp_path / "out.abw"
    write_abw(m2, str(dest))
    m3 = load(str(dest))
    assert m3["paragraph_count"] == 2


def test_create_abw_replace_write_reload(tmp_path):
    m = create_abw(["Hello World", "Goodbye World"])
    m2 = search_replace_paragraph(m, "World", "Everyone")
    dest = tmp_path / "created.abw"
    write_abw(m2, str(dest))
    m3 = load(str(dest))
    assert "Everyone" in get_paragraph(m3, 0)
    assert "World" not in get_paragraph(m3, 0)
