"""
Dogfood pipeline: FODP remaining analytics → NDJSON export.
Covers FODP: fodp_all_pages_have_title, fodp_avg_words_per_slide, fodp_image_density,
             fodp_is_single_nonempty_slide, fodp_max_shapes_per_slide, fodp_max_text_item_count,
             fodp_max_text_length, fodp_min_title_length, fodp_nonempty_slide_ratio,
             fodp_notes_total_length, fodp_shape_count_variance, fodp_shape_diversity
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import (
    fodp_all_pages_have_title,
    fodp_avg_words_per_slide,
    fodp_image_density,
    fodp_is_single_nonempty_slide,
    fodp_max_shapes_per_slide,
    fodp_max_text_item_count,
    fodp_max_text_length,
    fodp_min_title_length,
    fodp_nonempty_slide_ratio,
    fodp_notes_total_length,
    fodp_shape_count_variance,
    fodp_shape_diversity,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODP_FILE = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"


def _fodp_file():
    return str(_FODP_FILE)


def test_fodp_all_pages_have_title_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_all_pages_have_title(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_all_pages_have_title", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_avg_words_per_slide_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_words_per_slide(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_avg_words_per_slide", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_image_density_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_image_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_image_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_is_single_nonempty_slide_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_is_single_nonempty_slide(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_is_single_nonempty_slide", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_max_shapes_per_slide_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_max_shapes_per_slide(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_max_shapes_per_slide", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_max_text_item_count_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_max_text_item_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_max_text_item_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_max_text_length_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_max_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_max_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_min_title_length_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_min_title_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_min_title_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_nonempty_slide_ratio_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_nonempty_slide_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fodp", "function": "fodp_nonempty_slide_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fodp_notes_total_length_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_notes_total_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_notes_total_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_shape_count_variance_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_shape_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_shape_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_shape_diversity_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_shape_diversity(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_shape_diversity", "diversity": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["diversity"] >= 0
    assert json.dumps(loaded[0]) is not None
