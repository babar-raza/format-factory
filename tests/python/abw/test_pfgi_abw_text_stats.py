"""Tests for abw.abw_codec.text_stats() — PFGI Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, append_paragraph, text_stats


def _make_doc(*paragraphs: str) -> dict:
    model = create_abw([])
    for p in paragraphs:
        model = append_paragraph(model, p)
    return model


def test_empty_document_all_zeros():
    model = create_abw([])
    stats = text_stats(model)
    assert stats["paragraph_count"] == 0
    assert stats["word_count"] == 0
    assert stats["char_count"] == 0
    assert stats["avg_words_per_paragraph"] == pytest.approx(0.0)


def test_single_paragraph_counts():
    model = _make_doc("Hello world")
    stats = text_stats(model)
    assert stats["paragraph_count"] == 1
    assert stats["word_count"] == 2
    assert stats["char_count"] == 11


def test_multiple_paragraphs_word_count():
    model = _make_doc("one two three", "four five")
    stats = text_stats(model)
    assert stats["paragraph_count"] == 2
    assert stats["word_count"] == 5


def test_avg_words_per_paragraph():
    model = _make_doc("a b c", "d e f")
    stats = text_stats(model)
    assert stats["avg_words_per_paragraph"] == pytest.approx(3.0)


def test_char_count_includes_spaces():
    model = _make_doc("ab cd")
    stats = text_stats(model)
    assert stats["char_count"] == 5


def test_returns_dict():
    model = create_abw([])
    assert isinstance(text_stats(model), dict)


def test_non_dict_raises():
    with pytest.raises(TypeError):
        text_stats("not a dict")


def test_required_keys_present():
    model = _make_doc("test")
    stats = text_stats(model)
    for key in ("paragraph_count", "word_count", "char_count", "avg_words_per_paragraph"):
        assert key in stats
