"""
Dogfood pipeline: FODP remaining analytics → NDJSON export.
Covers: fodp_all_slides_have_text, fodp_average_shapes_per_slide, fodp_avg_notes_length,
        fodp_empty_slide_count, fodp_has_empty_slides, fodp_has_images
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import (
    fodp_all_slides_have_text,
    fodp_average_shapes_per_slide,
    fodp_avg_notes_length,
    fodp_empty_slide_count,
    fodp_has_empty_slides,
    fodp_has_images,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def test_fodp_all_slides_have_text_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_all_slides_have_text(path)
    assert isinstance(result, bool)
    record = {"format": "fodp", "function": "fodp_all_slides_have_text", "all_have_text": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_have_text"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_average_shapes_per_slide_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_average_shapes_per_slide(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "fodp", "function": "fodp_average_shapes_per_slide", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodp_avg_notes_length_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_notes_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "fodp", "function": "fodp_avg_notes_length", "avg_notes": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_notes"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodp_empty_slide_count_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_empty_slide_count(path)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "fodp", "function": "fodp_empty_slide_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_has_empty_slides_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_has_empty_slides(path)
    assert isinstance(result, bool)
    record = {"format": "fodp", "function": "fodp_has_empty_slides", "has_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_empty"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_has_images_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_has_images(path)
    assert isinstance(result, bool)
    record = {"format": "fodp", "function": "fodp_has_images", "has_images": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_images"], bool)
    assert json.dumps(loaded[0]) is not None
