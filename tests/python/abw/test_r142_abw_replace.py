"""Tests for abw.abw_codec.replace_in_paragraphs() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, replace_in_paragraphs


def test_basic_replace():
    model = create_abw(["hello world"])
    result = replace_in_paragraphs(model, "world", "earth")
    assert result["paragraphs"] == ["hello earth"]


def test_replace_multiple_occurrences():
    model = create_abw(["aaa bbb aaa"])
    result = replace_in_paragraphs(model, "aaa", "x")
    assert result["paragraphs"] == ["x bbb x"]


def test_replace_across_paragraphs():
    model = create_abw(["foo bar", "foo baz"])
    result = replace_in_paragraphs(model, "foo", "qux")
    assert result["paragraphs"] == ["qux bar", "qux baz"]


def test_replace_not_found_unchanged():
    model = create_abw(["hello world"])
    result = replace_in_paragraphs(model, "xyz", "abc")
    assert result["paragraphs"] == ["hello world"]


def test_replace_does_not_mutate():
    model = create_abw(["hello"])
    replace_in_paragraphs(model, "hello", "bye")
    assert model["paragraphs"] == ["hello"]


def test_replace_preserves_is_abw():
    model = create_abw(["test"])
    result = replace_in_paragraphs(model, "test", "ok")
    assert result["is_abw"] is True


def test_replace_empty_old_text():
    model = create_abw(["abc"])
    result = replace_in_paragraphs(model, "", "X")
    assert "X" in result["paragraphs"][0]


def test_type_error_model():
    try:
        replace_in_paragraphs("not a dict", "a", "b")
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_type_error_old_text():
    model = create_abw(["hello"])
    try:
        replace_in_paragraphs(model, 42, "b")
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_type_error_new_text():
    model = create_abw(["hello"])
    try:
        replace_in_paragraphs(model, "hello", 42)
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass
