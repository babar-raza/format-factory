"""
test_fodg_text_shapes_json_pipeline.py -- FODG get_text_shapes + export_to_json pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-103
Tests get_text_shapes returns list, has page with texts, export_to_json returns string,
json has page_count, json parseable with correct structure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    get_text_shapes,
    export_to_json,
)


def _make_model():
    return create_fodg([
        {"name": "Intro", "texts": ["Hello World", "Welcome"]},
        {"name": "Empty"},
        {"name": "Content", "texts": ["Some text"]},
    ])


def test_get_text_shapes_returns_list():
    model = _make_model()
    shapes = get_text_shapes(model)
    assert isinstance(shapes, list)


def test_get_text_shapes_has_pages_with_text():
    model = _make_model()
    shapes = get_text_shapes(model)
    page_names = [s["page_name"] for s in shapes]
    assert "Intro" in page_names
    assert "Content" in page_names


def test_export_to_json_returns_string():
    model = _make_model()
    json_str = export_to_json(model)
    assert isinstance(json_str, str)


def test_export_to_json_parseable():
    model = _make_model()
    json_str = export_to_json(model)
    data = json.loads(json_str)
    assert "page_count" in data


def test_export_to_json_correct_page_count():
    model = _make_model()
    json_str = export_to_json(model)
    data = json.loads(json_str)
    assert data["page_count"] == 3
