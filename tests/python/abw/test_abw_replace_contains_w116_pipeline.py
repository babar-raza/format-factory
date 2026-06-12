"""
test_abw_replace_contains_w116_pipeline.py -- ABW replace_in_paragraphs + contains_text pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-116
Tests replace_in_paragraphs returns dict, replace changes content,
contains_text returns bool, contains_text finds existing text,
contains_text returns False after replacement removes match.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    replace_in_paragraphs,
    contains_text,
)

_PARAGRAPHS = ["Hello World", "Quick brown fox", "Test document content"]


def test_replace_in_paragraphs_returns_dict():
    model = create_abw(_PARAGRAPHS)
    result = replace_in_paragraphs(model, "Hello", "Hi")
    assert isinstance(result, dict)


def test_replace_in_paragraphs_changes_content():
    model = create_abw(_PARAGRAPHS)
    result = replace_in_paragraphs(model, "Hello", "Hi")
    paragraphs = result.get("paragraphs", [])
    assert any("Hi World" in p for p in paragraphs)


def test_contains_text_returns_bool():
    model = create_abw(_PARAGRAPHS)
    result = contains_text(model, "Quick")
    assert isinstance(result, bool)


def test_contains_text_finds_existing():
    model = create_abw(_PARAGRAPHS)
    assert contains_text(model, "Quick brown fox") is True


def test_contains_text_false_after_replace():
    model = create_abw(_PARAGRAPHS)
    replaced = replace_in_paragraphs(model, "Hello World", "Goodbye")
    assert contains_text(replaced, "Hello World") is False
