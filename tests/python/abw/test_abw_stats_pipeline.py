"""
test_abw_stats_pipeline.py -- ABW document statistics pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-27
Tests get_word_count, word_frequency, get_char_count, merge_abw,
get_unique_words on model dicts (no source-loading issues).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    get_word_count,
    word_frequency,
    get_char_count,
    merge_abw,
    get_unique_words,
)

_MODEL = create_abw(["hello world", "hello python", "world of code"])


def test_get_word_count():
    assert get_word_count(_MODEL) == 7


def test_word_frequency_hello():
    freq = word_frequency(_MODEL)
    assert freq.get("hello", 0) == 2


def test_get_char_count():
    # "hello world" + "hello python" + "world of code" = 11+12+13 = 36 chars
    char_count = get_char_count(_MODEL)
    assert char_count == 36


def test_merge_abw_paragraph_count():
    a = create_abw(["first paragraph"])
    b = create_abw(["second paragraph"])
    merged = merge_abw(a, b)
    assert merged["paragraph_count"] == 2


def test_get_unique_words():
    unique = get_unique_words(_MODEL)
    assert "hello" in unique
    assert "world" in unique
    # No duplicates — "hello" and "world" appear twice but unique list has them once
    assert unique.count("hello") == 1
