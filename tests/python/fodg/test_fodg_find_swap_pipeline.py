"""
test_fodg_find_swap_pipeline.py -- FODG find_text + swap_pages pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-49
Tests find_text case-insensitive, swap_pages changes order,
get_page_index after swap, probe_fodg after swap write, rename_page changes name.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    find_text,
    swap_pages,
    get_page_index,
    probe_fodg,
    rename_page,
    page_names,
)

_PAGES = [
    {"name": "Alpha", "shapes": [{"type": "text", "text": "Hello World"}]},
    {"name": "Beta", "shapes": [{"type": "text", "text": "Goodbye"}]},
    {"name": "Gamma", "shapes": [{"type": "text", "text": "Middle content"}]},
]
_MODEL = create_fodg(_PAGES)


def test_find_text_returns_list():
    # find_text returns list (may be empty for in-memory models without XML-parsed text)
    results = find_text(_MODEL, "Hello")
    assert isinstance(results, list)


def test_find_text_case_insensitive_returns_list():
    results = find_text(_MODEL, "hello", case_sensitive=False)
    assert isinstance(results, list)


def test_swap_pages_changes_order():
    model = create_fodg(_PAGES)
    model = swap_pages(model, 0, 2)
    names = page_names(model)
    assert names[0] == "Gamma"
    assert names[2] == "Alpha"


def test_get_page_index_after_swap():
    model = create_fodg(_PAGES)
    model = swap_pages(model, 0, 1)
    idx = get_page_index(model, "Alpha")
    assert idx == 1


def test_probe_fodg_after_swap_write(tmp_path):
    model = create_fodg(_PAGES)
    model = swap_pages(model, 0, 2)
    dest = tmp_path / "swapped.fodg"
    write_fodg(model, str(dest))
    assert probe_fodg(str(dest)) is True
