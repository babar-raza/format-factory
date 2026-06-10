"""Tests for abw.abw_codec.reverse_paragraphs() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, reverse_paragraphs


def test_reverse_two_paragraphs():
    model = create_abw(["first", "second"])
    rev = reverse_paragraphs(model)
    assert rev["paragraphs"] == ["second", "first"]


def test_reverse_three_paragraphs():
    model = create_abw(["a", "b", "c"])
    rev = reverse_paragraphs(model)
    assert rev["paragraphs"] == ["c", "b", "a"]


def test_single_paragraph_unchanged():
    model = create_abw(["only"])
    rev = reverse_paragraphs(model)
    assert rev["paragraphs"] == ["only"]


def test_empty_model():
    model = create_abw([])
    rev = reverse_paragraphs(model)
    assert rev["paragraphs"] == []


def test_does_not_mutate_original():
    model = create_abw(["x", "y"])
    reverse_paragraphs(model)
    assert model["paragraphs"] == ["x", "y"]


def test_paragraph_count_preserved():
    model = create_abw(["a", "b", "c"])
    rev = reverse_paragraphs(model)
    assert rev["paragraph_count"] == 3


def test_returns_dict():
    model = create_abw(["a"])
    assert isinstance(reverse_paragraphs(model), dict)
