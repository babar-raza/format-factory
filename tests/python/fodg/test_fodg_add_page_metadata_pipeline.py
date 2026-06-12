"""
test_fodg_add_page_metadata_pipeline.py -- FODG add_page + get_page_metadata pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-82
Tests add_page increases count, get_page_metadata returns list, metadata len=2,
add_page returns model dict, get_page_count after add=3.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    write_fodg,
    add_page,
    get_page_metadata,
    get_page_count,
)

_PAGES = [
    {"name": "Slide1", "shapes": [{"type": "text", "text": "Hello"}]},
    {"name": "Slide2", "shapes": [{"type": "text", "text": "World"}]},
]


def test_add_page_increases_count(tmp_path):
    model = create_fodg(_PAGES)
    before = get_page_count(model)
    model = add_page(model, "Slide3")
    after = get_page_count(model)
    assert after == before + 1


def test_get_page_metadata_returns_list(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    meta = get_page_metadata(str(dest))
    assert isinstance(meta, list)


def test_get_page_metadata_len(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    meta = get_page_metadata(str(dest))
    assert len(meta) == 2


def test_add_page_returns_model_dict(tmp_path):
    model = create_fodg(_PAGES)
    result = add_page(model, "Extra")
    assert isinstance(result, dict)


def test_get_page_count_after_add(tmp_path):
    model = create_fodg(_PAGES)
    model = add_page(model, "New1")
    assert get_page_count(model) == 3
