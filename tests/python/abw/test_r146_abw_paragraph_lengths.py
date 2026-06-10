"""Tests for abw.abw_codec.paragraph_lengths() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, paragraph_lengths


def test_basic_lengths():
    model = create_abw(["hi", "hello", "a"])
    assert paragraph_lengths(model) == [2, 5, 1]


def test_empty_model():
    model = create_abw([])
    assert paragraph_lengths(model) == []


def test_single_paragraph():
    model = create_abw(["word"])
    assert paragraph_lengths(model) == [4]


def test_empty_paragraph():
    model = create_abw(["", "abc"])
    assert paragraph_lengths(model) == [0, 3]


def test_returns_list():
    model = create_abw(["text"])
    assert isinstance(paragraph_lengths(model), list)


def test_length_count_matches_paragraph_count():
    model = create_abw(["a", "bb", "ccc"])
    lengths = paragraph_lengths(model)
    assert len(lengths) == model["paragraph_count"]
