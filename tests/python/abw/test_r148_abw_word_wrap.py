"""Tests for abw.abw_codec.word_wrap() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, word_wrap


def test_short_paragraph_unchanged():
    model = create_abw(["hello world"])
    wrapped = word_wrap(model, 80)
    assert wrapped["paragraphs"] == ["hello world"]


def test_long_paragraph_split():
    text = "one two three four five six seven eight nine ten"
    model = create_abw([text])
    wrapped = word_wrap(model, 20)
    assert len(wrapped["paragraphs"]) > 1


def test_each_line_within_width():
    text = "one two three four five six seven eight nine ten"
    model = create_abw([text])
    wrapped = word_wrap(model, 15)
    for line in wrapped["paragraphs"]:
        assert len(line) <= 15


def test_empty_model():
    model = create_abw([])
    wrapped = word_wrap(model, 40)
    assert wrapped["paragraphs"] == []


def test_returns_dict():
    model = create_abw(["text"])
    assert isinstance(word_wrap(model, 80), dict)


def test_does_not_mutate_original():
    model = create_abw(["a very long paragraph that might be wrapped into multiple lines if the width is small"])
    word_wrap(model, 20)
    assert model["paragraph_count"] == 1
