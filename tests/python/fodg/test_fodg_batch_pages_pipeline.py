"""
test_fodg_batch_pages_pipeline.py -- FODG batch page operations pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-43
Tests find_text returns list, add_page then page_names, remove+add roundtrip count,
export_to_json parseable, get_all_text list.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    find_text,
    add_page,
    page_names,
    remove_page,
    export_to_json,
    get_all_text,
    get_page_count,
)

_PAGES = [
    {"name": "Intro", "shapes": [{"type": "text", "text": "Welcome to the presentation"}]},
    {"name": "Summary", "shapes": [{"type": "text", "text": "Key takeaways here"}]},
    {"name": "Conclusion", "shapes": [{"type": "text", "text": "Thank you"}]},
]
_MODEL = create_fodg(_PAGES)


def test_find_text_returns_list():
    results = find_text(_MODEL, "Welcome")
    assert isinstance(results, list)


def test_add_page_visible_in_names():
    model = create_fodg(_PAGES)
    model = add_page(model, "NewPage")
    names = page_names(model)
    assert "NewPage" in names


def test_remove_then_add_page_count():
    model = create_fodg(_PAGES)
    model = remove_page(model, 0)
    model = add_page(model, "Added")
    assert get_page_count(model) == 3


def test_export_to_json_parseable():
    json_str = export_to_json(_MODEL)
    data = json.loads(json_str)
    assert isinstance(data, dict)
    assert "pages" in data


def test_get_all_text_is_list():
    texts = get_all_text(_MODEL)
    assert isinstance(texts, list)
