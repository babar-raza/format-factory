"""
test_fodg_find_export_w110_pipeline.py -- FODG find_text + export_to_json pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-110
Tests find_text returns list, find_text finds match, no match returns empty,
export_to_json returns str, exported JSON has page_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    find_text,
    export_to_json,
)

_MODEL = {
    "is_fodg": True,
    "page_count": 2,
    "pages": [
        {
            "name": "Intro",
            "shape_count": 2,
            "shapes": [
                {"type": "text", "text": "Hello World"},
                {"type": "text", "text": "Welcome"},
            ],
            "text_content": ["Hello World", "Welcome"],
        },
        {
            "name": "Summary",
            "shape_count": 1,
            "shapes": [
                {"type": "text", "text": "Goodbye"},
            ],
            "text_content": ["Goodbye"],
        },
    ],
    "shapes_total": 3,
}


def test_find_text_returns_list():
    result = find_text(_MODEL, "Hello")
    assert isinstance(result, list)


def test_find_text_finds_match():
    result = find_text(_MODEL, "Hello")
    assert len(result) == 1
    assert result[0]["page_name"] == "Intro"


def test_find_text_no_match_empty():
    result = find_text(_MODEL, "xyzzy_notpresent")
    assert result == []


def test_export_to_json_returns_str():
    result = export_to_json(_MODEL)
    assert isinstance(result, str)


def test_export_to_json_has_page_count():
    result = export_to_json(_MODEL)
    parsed = json.loads(result)
    assert parsed["page_count"] == 2
