"""Tests for abw.abw_codec.join_paragraphs() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, join_paragraphs


def test_default_separator():
    model = create_abw(["hello", "world"])
    result = join_paragraphs(model)
    assert result == "hello\nworld"


def test_custom_separator():
    model = create_abw(["a", "b", "c"])
    result = join_paragraphs(model, sep=", ")
    assert result == "a, b, c"


def test_single_paragraph():
    model = create_abw(["only"])
    result = join_paragraphs(model)
    assert result == "only"


def test_empty_model():
    model = create_abw([])
    result = join_paragraphs(model)
    assert result == ""


def test_empty_sep():
    model = create_abw(["ab", "cd"])
    result = join_paragraphs(model, sep="")
    assert result == "abcd"


def test_type_error():
    try:
        join_paragraphs("not a dict")
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_returns_string():
    model = create_abw(["hello"])
    assert isinstance(join_paragraphs(model), str)
