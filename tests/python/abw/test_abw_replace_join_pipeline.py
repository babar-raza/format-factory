"""
test_abw_replace_join_pipeline.py -- ABW replace_in_paragraphs + join_paragraphs pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-105
Tests replace_in_paragraphs returns model, old text gone, new text present,
join_paragraphs returns string, joined string has both paragraphs.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    replace_in_paragraphs,
    join_paragraphs,
)

_PARAGRAPHS = [
    "Hello World from Alice",
    "Goodbye World from Bob",
    "Greetings from Carol",
]


def _make_model():
    return create_abw(_PARAGRAPHS)


def test_replace_returns_model():
    model = _make_model()
    new_model = replace_in_paragraphs(model, "World", "Earth")
    assert isinstance(new_model, dict)


def test_replace_removes_old_text():
    model = _make_model()
    new_model = replace_in_paragraphs(model, "World", "Earth")
    text = " ".join(new_model["paragraphs"])
    assert "World" not in text


def test_replace_has_new_text():
    model = _make_model()
    new_model = replace_in_paragraphs(model, "World", "Earth")
    text = " ".join(new_model["paragraphs"])
    assert "Earth" in text


def test_join_paragraphs_returns_string():
    model = _make_model()
    result = join_paragraphs(model)
    assert isinstance(result, str)


def test_join_paragraphs_has_content():
    model = _make_model()
    result = join_paragraphs(model, sep="|")
    assert "Hello" in result
    assert "Goodbye" in result
    assert "|" in result
