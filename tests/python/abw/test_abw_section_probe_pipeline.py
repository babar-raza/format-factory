"""
test_abw_section_probe_pipeline.py -- ABW get_section_count + probe pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-81
Tests get_section_count int, probe_abw True, get_word_count int,
get_char_count int, text_stats has word_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    write_abw,
    get_section_count,
    probe_abw,
    get_word_count,
    get_char_count,
    text_stats,
)

_PARAGRAPHS = ["Hello world from section one.", "Second paragraph here.", "Third paragraph ends."]


def _make_doc(tmp_path):
    model = create_abw(_PARAGRAPHS)
    dest = tmp_path / "doc.abw"
    write_abw(model, str(dest))
    return model, dest


def test_get_section_count_int(tmp_path):
    model, dest = _make_doc(tmp_path)
    count = get_section_count(str(dest))
    assert isinstance(count, int)


def test_probe_abw_true(tmp_path):
    model, dest = _make_doc(tmp_path)
    result = probe_abw(str(dest))
    assert result is True


def test_get_word_count_int(tmp_path):
    model, dest = _make_doc(tmp_path)
    count = get_word_count(model)
    assert isinstance(count, int)
    assert count > 0


def test_get_char_count_int(tmp_path):
    model, dest = _make_doc(tmp_path)
    count = get_char_count(model)
    assert isinstance(count, int)
    assert count > 0


def test_text_stats_has_word_count(tmp_path):
    model, dest = _make_doc(tmp_path)
    stats = text_stats(model)
    assert isinstance(stats, dict)
    assert "word_count" in stats
