"""Tests for fodg.fodg_codec.export_to_json() — Sprint 8, R144."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import create_fodg, export_to_json


def test_returns_string():
    model = create_fodg([])
    result = export_to_json(model)
    assert isinstance(result, str)


def test_valid_json():
    model = create_fodg([])
    result = export_to_json(model)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_contains_page_count():
    model = create_fodg([])
    result = export_to_json(model)
    parsed = json.loads(result)
    assert "page_count" in parsed


def test_contains_pages_key():
    model = create_fodg([])
    result = export_to_json(model)
    parsed = json.loads(result)
    assert "pages" in parsed


def test_roundtrip_preserves_structure():
    model = create_fodg([])
    model = {**model, "pages": [{"name": "Slide1", "shape_count": 0, "shapes": [], "text_content": []}], "page_count": 1, "shapes_total": 0}
    result = export_to_json(model)
    parsed = json.loads(result)
    assert parsed["page_count"] == 1
    assert parsed["pages"][0]["name"] == "Slide1"


def test_pretty_printed():
    model = create_fodg([])
    result = export_to_json(model)
    assert "\n" in result  # indent=2 produces newlines
