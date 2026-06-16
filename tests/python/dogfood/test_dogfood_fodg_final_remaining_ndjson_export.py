"""
Dogfood pipeline: FODG final remaining ops → NDJSON export.
Covers: get_page_index, clear_page, swap_pages, has_page, probe_fodg, find_shapes_by_text_pattern
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    load,
    add_page,
    get_page_index,
    clear_page,
    swap_pages,
    has_page,
    probe_fodg,
    find_shapes_by_text_pattern,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _shapes_fodg():
    return str(next(f for f in sorted(_FODG_DIR.glob("*.fodg")) if "shapes" in f.name))


def test_get_page_index_returns_int(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    pages = model.get("pages", [])
    page_name = pages[0].get("name", "Page1") if pages else "Page1"
    idx = get_page_index(model, page_name)
    assert isinstance(idx, int)
    assert idx == 0

    record = {"format": "fodg", "function": "get_page_index", "page": page_name, "index": idx}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] == 0
    assert json.dumps(loaded[0]) is not None


def test_clear_page_returns_dict(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    result = clear_page(model, 0)
    assert isinstance(result, dict)
    assert len(result.get("pages", [])) >= 1

    record = {"format": "fodg", "function": "clear_page", "page_count": len(result.get("pages", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["page_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_swap_pages_returns_dict(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    m2 = add_page(model, "PageB")
    pages_before = [p.get("name") for p in m2.get("pages", [])]
    result = swap_pages(m2, 0, 1)
    assert isinstance(result, dict)
    pages_after = [p.get("name") for p in result.get("pages", [])]
    assert pages_after[0] == pages_before[1]
    assert pages_after[1] == pages_before[0]

    record = {"format": "fodg", "function": "swap_pages", "first_page": pages_after[0]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["first_page"] == pages_before[1]
    assert json.dumps(loaded[0]) is not None


def test_has_page_returns_bool(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    pages = model.get("pages", [])
    existing_name = pages[0].get("name", "Page1") if pages else "Page1"
    assert has_page(model, existing_name) is True
    assert has_page(model, "__nonexistent_page__") is False

    record = {"format": "fodg", "function": "has_page", "has_existing": True, "has_missing": False}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["has_existing"] is True
    assert json.dumps(loaded[0]) is not None


def test_probe_fodg_returns_bool(tmp_path):
    path = _shapes_fodg()
    result = probe_fodg(path)
    assert result is True

    record = {"format": "fodg", "function": "probe_fodg", "is_valid": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_find_shapes_by_text_pattern_returns_list(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    results = find_shapes_by_text_pattern(model, "Rect")
    assert isinstance(results, list)
    assert len(results) >= 1
    assert results[0].get("matched") is True

    record = {
        "format": "fodg",
        "function": "find_shapes_by_text_pattern",
        "pattern": "Rect",
        "match_count": len(results),
    }
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["match_count"] >= 1
    assert json.dumps(loaded[0]) is not None
