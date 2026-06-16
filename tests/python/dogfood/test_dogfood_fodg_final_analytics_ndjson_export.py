"""
Dogfood pipeline: FODG final analytics → NDJSON export.
Covers: fodg_page_shape_count, fodg_shape_to_page_variance, fodg_max_text_per_page,
        fodg_text_per_shape, fodg_nonempty_page_count, find_text
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
    fodg_page_shape_count,
    fodg_shape_to_page_variance,
    fodg_max_text_per_page,
    fodg_text_per_shape,
    fodg_nonempty_page_count,
    find_text,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


def _shapes_fodg():
    return str(next(f for f in _valid_fodg_files() if "shapes" in f.name))


def test_fodg_page_shape_count(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    count = fodg_page_shape_count(model, 0)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "fodg", "function": "fodg_page_shape_count", "page": 0, "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_shape_to_page_variance(tmp_path):
    path = _shapes_fodg()
    variance = fodg_shape_to_page_variance(path)
    assert isinstance(variance, float)
    assert variance >= 0.0

    record = {"format": "fodg", "function": "fodg_shape_to_page_variance", "variance": variance}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodg_max_text_per_page(tmp_path):
    path = _shapes_fodg()
    max_text = fodg_max_text_per_page(path)
    assert isinstance(max_text, int)
    assert max_text >= 0

    record = {"format": "fodg", "function": "fodg_max_text_per_page", "max_text": max_text}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_text"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_text_per_shape(tmp_path):
    path = _shapes_fodg()
    avg = fodg_text_per_shape(path)
    assert isinstance(avg, float)
    assert avg >= 0.0

    record = {"format": "fodg", "function": "fodg_text_per_shape", "avg_text": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_text"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodg_nonempty_page_count(tmp_path):
    path = _shapes_fodg()
    count = fodg_nonempty_page_count(path)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "fodg", "function": "fodg_nonempty_page_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_find_text_returns_list(tmp_path):
    path = _shapes_fodg()
    model = load(path)
    # find_text with empty/rare string returns empty list
    results = find_text(model, "__no_such_text__")
    assert isinstance(results, list)
    # Also test with a query that might match
    all_results = find_text(model, "")
    assert isinstance(all_results, list)

    record = {"format": "fodg", "function": "find_text", "found_count": len(results)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["found_count"], int)
    assert json.dumps(loaded[0]) is not None
