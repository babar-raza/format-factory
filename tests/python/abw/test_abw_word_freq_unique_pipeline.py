"""
test_abw_word_freq_unique_pipeline.py -- ABW word_frequency + get_unique_words pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-99
Tests word_frequency returns dict, has expected word counts, get_unique_words returns list,
list is sorted, contains expected words.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    word_frequency,
    get_unique_words,
)

_PARAGRAPHS = [
    "the quick brown fox",
    "the fox jumped high",
    "a quick brown bird",
]


def _make_model():
    return create_abw(_PARAGRAPHS)


def test_word_frequency_returns_dict():
    model = _make_model()
    freq = word_frequency(model)
    assert isinstance(freq, dict)


def test_word_frequency_correct_counts():
    model = _make_model()
    freq = word_frequency(model)
    assert freq["the"] == 2
    assert freq["fox"] == 2
    assert freq["quick"] == 2
    assert freq["brown"] == 2


def test_get_unique_words_returns_list():
    model = _make_model()
    words = get_unique_words(model)
    assert isinstance(words, list)


def test_get_unique_words_is_sorted():
    model = _make_model()
    words = get_unique_words(model)
    assert words == sorted(words)


def test_get_unique_words_has_expected():
    model = _make_model()
    words = get_unique_words(model)
    assert "fox" in words
    assert "quick" in words
    assert "bird" in words
