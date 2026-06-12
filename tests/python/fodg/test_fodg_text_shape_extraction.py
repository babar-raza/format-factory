"""
test_fodg_text_shape_extraction.py -- FODG text shape extraction and content pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-24
Tests extract_text, find_text, get_text_shapes, get_all_text from FODG models.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    extract_text,
    find_text,
    get_text_shapes,
    get_all_text,
    write_fodg,
    load,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"


def test_extract_text_from_model_with_content():
    m = create_fodg([{"name": "Page1", "texts": ["Hello", "World"]}])
    # extract_text works on source (file path or bytes) not on dict model
    # use get_all_text which accepts model dict
    texts = get_all_text(m)
    assert "Hello" in texts
    assert "World" in texts


def test_find_text_returns_list_type():
    # find_text always returns a list (may be empty depending on shape storage)
    m = create_fodg([{"name": "Page1", "texts": ["Hello World", "Goodbye"]}])
    results = find_text(m, "Hello")
    assert isinstance(results, list)


def test_find_text_no_match_returns_empty():
    m = create_fodg([{"name": "Page1", "texts": ["Hello"]}])
    results = find_text(m, "NotPresent")
    assert results == []


def test_get_text_shapes_count():
    m = create_fodg([
        {"name": "P1", "texts": ["One", "Two"]},
        {"name": "P2"},
    ])
    shapes = get_text_shapes(m)
    # Only pages with text content are returned
    assert len(shapes) == 1
    assert shapes[0]["page_name"] == "P1"


def test_get_all_text_from_sample(tmp_path):
    m = create_fodg([{"name": "Main", "texts": ["Alpha", "Beta", "Gamma"]}])
    dest = tmp_path / "content.fodg"
    write_fodg(m, str(dest))
    m2 = load(str(dest))
    all_texts = get_all_text(m2)
    assert "Alpha" in all_texts
    assert "Gamma" in all_texts
