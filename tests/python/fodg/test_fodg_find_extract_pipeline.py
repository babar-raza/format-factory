"""
test_fodg_find_extract_pipeline.py -- FODG find_text + extract_text pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-79
Tests find_text returns list, find_text empty when no match, extract_text list,
load returns dict, get_shape_count from file int.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    write_fodg,
    find_text,
    extract_text,
    load,
    get_shape_count,
)


def _make_file(tmp_path):
    model = create_fodg([
        {"name": "Intro"},
        {"name": "Content"},
        {"name": "Summary"},
    ])
    dest = tmp_path / "slides.fodg"
    write_fodg(model, str(dest))
    return dest, model


def test_find_text_returns_list(tmp_path):
    _, model = _make_file(tmp_path)
    result = find_text(model, "text")
    assert isinstance(result, list)


def test_find_text_empty_no_match(tmp_path):
    _, model = _make_file(tmp_path)
    result = find_text(model, "xyzzyquux_notpresent")
    assert result == []


def test_extract_text_list(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = extract_text(str(dest))
    assert isinstance(result, list)


def test_load_returns_dict(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = load(str(dest))
    assert isinstance(result, dict)
    assert "page_count" in result


def test_get_shape_count_int(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = get_shape_count(str(dest))
    assert isinstance(result, int)
