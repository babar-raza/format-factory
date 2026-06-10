"""Tests for abw.abw_codec.count_words() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import count_words, create_abw


def _model(paragraphs):
    m = create_abw([])
    return {**m, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


def test_single_paragraph_word_count():
    assert count_words(_model(["hello world"])) == 2


def test_multiple_paragraphs():
    assert count_words(_model(["one two", "three"])) == 3


def test_empty_document():
    assert count_words(_model([])) == 0


def test_empty_paragraph():
    assert count_words(_model([""])) == 0


def test_returns_int():
    assert isinstance(count_words(_model(["a"])), int)


def test_multiword_paragraph():
    assert count_words(_model(["The quick brown fox"])) == 4
