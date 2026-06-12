"""
test_abw_word_frequency_pipeline.py -- ABW word frequency pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-57
Tests word_frequency returns dict, word_frequency has key, get_word_count int,
get_unique_words list, word_frequency most common.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    word_frequency,
    get_word_count,
    get_unique_words,
)

_MODEL = create_abw([
    "the quick brown fox",
    "the fox jumps over",
    "the lazy dog",
])


def test_word_frequency_returns_dict():
    result = word_frequency(_MODEL)
    assert isinstance(result, dict)


def test_word_frequency_has_key():
    result = word_frequency(_MODEL)
    assert "the" in result


def test_word_frequency_most_common():
    result = word_frequency(_MODEL)
    assert result["the"] == 3


def test_get_word_count_int():
    count = get_word_count(_MODEL)
    assert isinstance(count, int)
    assert count == 11


def test_get_unique_words_list():
    words = get_unique_words(_MODEL)
    assert isinstance(words, list)
    assert "fox" in words
    assert len(words) >= 7
