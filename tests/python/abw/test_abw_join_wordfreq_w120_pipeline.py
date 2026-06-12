"""
test_abw_join_wordfreq_w120_pipeline.py -- ABW join_paragraphs + word_frequency pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-120
Tests join_paragraphs returns str, join contains both paragraphs,
word_frequency returns dict, hello count=2, all keys lowercase.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    join_paragraphs,
    word_frequency,
)

_PARAGRAPHS = ["Hello World", "Hello again", "Quick brown fox"]


def test_join_paragraphs_returns_str():
    model = create_abw(_PARAGRAPHS)
    result = join_paragraphs(model)
    assert isinstance(result, str)


def test_join_paragraphs_contains_both():
    model = create_abw(_PARAGRAPHS)
    result = join_paragraphs(model)
    assert "Hello World" in result and "Hello again" in result


def test_word_frequency_returns_dict():
    model = create_abw(_PARAGRAPHS)
    result = word_frequency(model)
    assert isinstance(result, dict)


def test_word_frequency_hello_count():
    model = create_abw(_PARAGRAPHS)
    result = word_frequency(model)
    assert result.get("hello") == 2


def test_word_frequency_keys_lowercase():
    model = create_abw(_PARAGRAPHS)
    result = word_frequency(model)
    assert all(k == k.lower() for k in result.keys())
