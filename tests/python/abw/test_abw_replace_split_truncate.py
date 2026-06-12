"""
test_abw_replace_split_truncate.py -- ABW replace/split/truncate pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-10
Tests replace_in_paragraphs, split_paragraphs, truncate_paragraphs,
edit_paragraph, and text_stats with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    replace_in_paragraphs,
    split_paragraphs,
    truncate_paragraphs,
    edit_paragraph,
    text_stats,
    join_paragraphs,
)

_MODEL = {
    "paragraphs": [
        "The quick brown fox jumps over the lazy dog.",
        "Pack my box with five dozen liquor jugs.",
        "How vexingly quick daft zebras jump.",
        "The five boxing wizards jump quickly.",
    ],
    "paragraph_count": 4,
}


def test_replace_changes_word():
    result = replace_in_paragraphs(_MODEL, "quick", "fast")
    assert "The fast brown fox" in result["paragraphs"][0]
    assert "quick" not in result["paragraphs"][0]


def test_replace_preserves_paragraph_count():
    result = replace_in_paragraphs(_MODEL, "jump", "leap")
    assert result["paragraph_count"] == 4
    assert len(result["paragraphs"]) == 4


def test_replace_multiple_paragraphs():
    result = replace_in_paragraphs(_MODEL, "jump", "leap")
    # "jumps" in para 0, "jump" in para 2 and 3
    joined = join_paragraphs(result)
    assert "leap" in joined
    assert "jumps" not in joined  # "jumps" → "leaps"


def test_split_chunk_size_one():
    chunks = split_paragraphs(_MODEL, 1)
    assert len(chunks) == 4
    assert chunks[0]["paragraph_count"] == 1
    assert chunks[0]["paragraphs"][0] == _MODEL["paragraphs"][0]


def test_split_chunk_size_two():
    chunks = split_paragraphs(_MODEL, 2)
    assert len(chunks) == 2
    assert chunks[0]["paragraph_count"] == 2
    assert chunks[1]["paragraph_count"] == 2


def test_split_preserves_content():
    chunks = split_paragraphs(_MODEL, 2)
    assert "quick brown fox" in chunks[0]["paragraphs"][0]
    assert "boxing wizards" in chunks[1]["paragraphs"][1]


def test_truncate_keeps_first_two():
    result = truncate_paragraphs(_MODEL, 2)
    assert result["paragraph_count"] == 2
    assert len(result["paragraphs"]) == 2
    assert "quick brown fox" in result["paragraphs"][0]


def test_truncate_to_zero():
    result = truncate_paragraphs(_MODEL, 0)
    assert result["paragraph_count"] == 0
    assert result["paragraphs"] == []


def test_edit_paragraph_changes_content():
    result = edit_paragraph(_MODEL, 1, "Replaced paragraph text.")
    assert result["paragraphs"][1] == "Replaced paragraph text."
    # Other paragraphs unchanged
    assert result["paragraphs"][0] == _MODEL["paragraphs"][0]


def test_text_stats_correct_values():
    stats = text_stats(_MODEL)
    assert stats["paragraph_count"] == 4
    # Each paragraph has known word count: 9 + 8 + 6 + 6 = 29
    assert stats["word_count"] == 29
    assert stats["char_count"] > 0
    assert isinstance(stats["avg_words_per_paragraph"], float)
    assert abs(stats["avg_words_per_paragraph"] - 7.25) < 0.01
