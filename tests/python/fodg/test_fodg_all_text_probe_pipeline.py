"""
test_fodg_all_text_probe_pipeline.py -- FODG get_all_text + probe_fodg pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-91
Tests get_all_text returns list, add_page then get_all_text returns list,
probe_fodg True from file, probe_fodg returns bool, extract_text list from file.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    write_fodg,
    get_all_text,
    probe_fodg,
    add_page,
    extract_text,
)

_PAGES = [
    {"name": "Page1"},
    {"name": "Page2"},
]


def test_get_all_text_returns_list(tmp_path):
    model = create_fodg(_PAGES)
    result = get_all_text(model)
    assert isinstance(result, list)


def test_add_page_then_get_all_text_list(tmp_path):
    model = create_fodg(_PAGES)
    model = add_page(model, "Page3")
    result = get_all_text(model)
    assert isinstance(result, list)


def test_probe_fodg_true_from_file(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    result = probe_fodg(str(dest))
    assert result is True


def test_probe_fodg_returns_bool(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    result = probe_fodg(str(dest))
    assert isinstance(result, bool)


def test_extract_text_returns_list_from_file(tmp_path):
    model = create_fodg(_PAGES)
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    result = extract_text(str(dest))
    assert isinstance(result, list)
