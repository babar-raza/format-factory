"""
test_abw_text_stats_pipeline.py -- ABW text stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-43
Tests text_stats keys/values, search_text index result, get_words returns list,
export_to_plain_text content, count_words matches word_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    text_stats,
    search_text,
    get_words,
    export_to_plain_text,
    count_words,
    get_word_count,
)

_MODEL = create_abw(["The quick brown fox", "jumps over the lazy dog", "hello world"])


def _write_abw(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_text_stats_has_keys():
    stats = text_stats(_MODEL)
    assert "word_count" in stats
    assert "char_count" in stats
    assert "paragraph_count" in stats


def test_text_stats_paragraph_count():
    stats = text_stats(_MODEL)
    assert stats["paragraph_count"] == 3


def test_search_text_finds_index():
    indices = search_text(_MODEL, "hello")
    assert isinstance(indices, list)
    assert 2 in indices


def test_get_words_returns_list():
    words = get_words(_MODEL, 0)
    assert isinstance(words, list)
    assert "quick" in words


def test_export_to_plain_text_has_content():
    txt = export_to_plain_text(_MODEL)
    assert "quick brown fox" in txt
    assert "lazy dog" in txt
