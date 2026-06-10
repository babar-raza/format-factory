"""Tests for abw.abw_codec.split_paragraphs() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, split_paragraphs


def test_split_even_chunks():
    model = create_abw(["a", "b", "c", "d"])
    chunks = split_paragraphs(model, 2)
    assert len(chunks) == 2
    assert chunks[0]["paragraphs"] == ["a", "b"]
    assert chunks[1]["paragraphs"] == ["c", "d"]


def test_split_uneven_last_chunk():
    model = create_abw(["a", "b", "c", "d", "e"])
    chunks = split_paragraphs(model, 2)
    assert len(chunks) == 3
    assert chunks[2]["paragraphs"] == ["e"]


def test_split_chunk_size_equals_total():
    model = create_abw(["x", "y", "z"])
    chunks = split_paragraphs(model, 3)
    assert len(chunks) == 1
    assert chunks[0]["paragraphs"] == ["x", "y", "z"]


def test_split_chunk_size_larger_than_total():
    model = create_abw(["x", "y"])
    chunks = split_paragraphs(model, 10)
    assert len(chunks) == 1
    assert chunks[0]["paragraphs"] == ["x", "y"]


def test_split_chunk_size_one():
    model = create_abw(["a", "b", "c"])
    chunks = split_paragraphs(model, 1)
    assert len(chunks) == 3
    assert chunks[0]["paragraphs"] == ["a"]


def test_split_empty_model():
    model = create_abw([])
    chunks = split_paragraphs(model, 3)
    assert len(chunks) == 1
    assert chunks[0]["paragraphs"] == []
    assert chunks[0]["paragraph_count"] == 0


def test_split_preserves_is_abw():
    model = create_abw(["hello"])
    chunks = split_paragraphs(model, 1)
    assert chunks[0]["is_abw"] is True


def test_split_does_not_mutate():
    model = create_abw(["a", "b", "c"])
    original_paras = list(model["paragraphs"])
    split_paragraphs(model, 2)
    assert model["paragraphs"] == original_paras


def test_split_type_error():
    try:
        split_paragraphs("not a dict", 2)
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_split_value_error_zero():
    model = create_abw(["a"])
    try:
        split_paragraphs(model, 0)
        assert False, "Expected ValueError"
    except ValueError:
        pass
