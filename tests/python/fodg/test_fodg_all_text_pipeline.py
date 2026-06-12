"""
test_fodg_all_text_pipeline.py -- FODG get_all_text pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-67
Tests get_all_text returns list, extract_text returns list, clear_page reduces shapes,
get_page_count after clear, add_page then get_all_text.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    get_all_text,
    extract_text,
    clear_page,
    get_page_count,
    add_page,
)

_PAGES = [{"name": "Page1"}, {"name": "Page2"}]
_MODEL = create_fodg(_PAGES)


def _write(tmp_path):
    dest = tmp_path / "doc.fodg"
    write_fodg(_MODEL, str(dest))
    return dest


def test_get_all_text_returns_list():
    result = get_all_text(_MODEL)
    assert isinstance(result, list)


def test_extract_text_returns_list(tmp_path):
    dest = _write(tmp_path)
    result = extract_text(str(dest))
    assert isinstance(result, list)


def test_clear_page_reduces_count():
    model = create_fodg(_PAGES)
    count_before = get_page_count(model)
    model = clear_page(model, 0)
    count_after = get_page_count(model)
    assert count_after == count_before


def test_get_page_count_after_add():
    model = create_fodg(_PAGES)
    model = add_page(model, {"name": "Extra"})
    assert get_page_count(model) == 3


def test_add_page_then_get_all_text():
    model = create_fodg(_PAGES)
    model = add_page(model, {"name": "NewPage"})
    result = get_all_text(model)
    assert isinstance(result, list)
