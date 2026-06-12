"""
test_dogfood_abw_pipeline.py -- ABW multi-function pipeline dogfood tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-10
Tests cross-function ABW pipelines: replace→export, truncate→join,
text_stats→word_frequency cross-check, markdown export.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    replace_in_paragraphs,
    truncate_paragraphs,
    join_paragraphs,
    text_stats,
    word_frequency,
    export_to_markdown,
    create_abw,
    write_abw,
)

_PARAGRAPHS = [
    "The quick brown fox.",
    "The fox jumped high.",
    "Quick and brown.",
]
_MODEL = create_abw(_PARAGRAPHS)


def test_replace_then_write_roundtrip(tmp_path):
    replaced = replace_in_paragraphs(_MODEL, "fox", "cat")
    dest = tmp_path / "replaced.abw"
    write_abw(replaced, str(dest))
    assert dest.exists()
    # Written file contains ABW XML with replaced content
    content = dest.read_text(encoding="utf-8")
    assert "cat" in content
    assert "fox" not in content


def test_truncate_then_join_pipeline():
    truncated = truncate_paragraphs(_MODEL, 2)
    joined = join_paragraphs(truncated, sep=" | ")
    assert "quick brown fox" in joined
    assert "fox jumped high" in joined
    # Third paragraph should not appear
    assert "Quick and brown" not in joined


def test_text_stats_word_count_matches_frequency():
    stats = text_stats(_MODEL)
    freq = word_frequency(_MODEL)
    # sum of all word frequencies must equal total word_count
    total_from_freq = sum(freq.values())
    assert total_from_freq == stats["word_count"]


def test_markdown_export_has_paragraph_content():
    md = export_to_markdown(_MODEL)
    assert "The quick brown fox." in md
    assert "The fox jumped high." in md
    assert "Quick and brown." in md
