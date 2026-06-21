"""Dogfood export: FODG(2) + FODP(12) analytics gap functions → NDJSON.

Functions covered (previously uncovered):
  FODG: fodg_avg_shapes_per_page, fodg_shape_density
  FODP: fodp_empty_slide_count, fodp_lowercase_ratio, fodp_max_shape_count_per_slide,
        fodp_max_title_length, fodp_punctuation_count, fodp_slide_text_range,
        fodp_text_per_image, fodp_total_image_count, fodp_total_shape_count,
        fodp_total_text_length, fodp_uppercase_count, fodp_word_length_variance
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from fodg.fodg_codec import fodg_avg_shapes_per_page, fodg_shape_density
from fodp.fodp_codec import (
    fodp_empty_slide_count,
    fodp_lowercase_ratio,
    fodp_max_shape_count_per_slide,
    fodp_max_title_length,
    fodp_punctuation_count,
    fodp_slide_text_range,
    fodp_text_per_image,
    fodp_total_image_count,
    fodp_total_shape_count,
    fodp_total_text_length,
    fodp_uppercase_count,
    fodp_word_length_variance,
)

_FODG = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_FODP = str(_REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp")


# --- FODG tests ---

def test_fodg_avg_shapes_per_page(tmp_path):
    val = fodg_avg_shapes_per_page(_FODG)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "fodg_avg_shapes_per_page.ndjson"
    write_ndjson([{"metric": "fodg_avg_shapes_per_page", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_fodg_shape_density(tmp_path):
    val = fodg_shape_density(_FODG)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "fodg_shape_density.ndjson"
    write_ndjson([{"metric": "fodg_shape_density", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


# --- FODP tests ---

def test_fodp_empty_slide_count(tmp_path):
    val = fodp_empty_slide_count(_FODP)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "fodp_empty_slide_count.ndjson"
    write_ndjson([{"metric": "fodp_empty_slide_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_fodp_lowercase_ratio(tmp_path):
    val = fodp_lowercase_ratio(_FODP)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "fodp_lowercase_ratio.ndjson"
    write_ndjson([{"metric": "fodp_lowercase_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_fodp_max_shape_count_per_slide(tmp_path):
    val = fodp_max_shape_count_per_slide(_FODP)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "fodp_max_shape_count_per_slide.ndjson"
    write_ndjson([{"metric": "fodp_max_shape_count_per_slide", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_fodp_max_title_length(tmp_path):
    val = fodp_max_title_length(_FODP)
    assert isinstance(val, int)
    assert val == 5
    out = tmp_path / "fodp_max_title_length.ndjson"
    write_ndjson([{"metric": "fodp_max_title_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 5


def test_fodp_punctuation_count(tmp_path):
    val = fodp_punctuation_count(_FODP)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "fodp_punctuation_count.ndjson"
    write_ndjson([{"metric": "fodp_punctuation_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_fodp_slide_text_range(tmp_path):
    val = fodp_slide_text_range(_FODP)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "fodp_slide_text_range.ndjson"
    write_ndjson([{"metric": "fodp_slide_text_range", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_fodp_text_per_image(tmp_path):
    val = fodp_text_per_image(_FODP)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "fodp_text_per_image.ndjson"
    write_ndjson([{"metric": "fodp_text_per_image", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_fodp_total_image_count(tmp_path):
    val = fodp_total_image_count(_FODP)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "fodp_total_image_count.ndjson"
    write_ndjson([{"metric": "fodp_total_image_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_fodp_total_shape_count(tmp_path):
    val = fodp_total_shape_count(_FODP)
    assert isinstance(val, int)
    assert val == 1
    out = tmp_path / "fodp_total_shape_count.ndjson"
    write_ndjson([{"metric": "fodp_total_shape_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1


def test_fodp_total_text_length(tmp_path):
    val = fodp_total_text_length(_FODP)
    assert isinstance(val, int)
    assert val == 5
    out = tmp_path / "fodp_total_text_length.ndjson"
    write_ndjson([{"metric": "fodp_total_text_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 5


def test_fodp_uppercase_count(tmp_path):
    val = fodp_uppercase_count(_FODP)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "fodp_uppercase_count.ndjson"
    write_ndjson([{"metric": "fodp_uppercase_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_fodp_word_length_variance(tmp_path):
    val = fodp_word_length_variance(_FODP)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "fodp_word_length_variance.ndjson"
    write_ndjson([{"metric": "fodp_word_length_variance", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_fodg_fodp_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "fodg", "metric": "fodg_avg_shapes_per_page", "value": fodg_avg_shapes_per_page(_FODG)},
        {"fmt": "fodg", "metric": "fodg_shape_density", "value": fodg_shape_density(_FODG)},
        {"fmt": "fodp", "metric": "fodp_max_title_length", "value": fodp_max_title_length(_FODP)},
        {"fmt": "fodp", "metric": "fodp_total_shape_count", "value": fodp_total_shape_count(_FODP)},
        {"fmt": "fodp", "metric": "fodp_total_text_length", "value": fodp_total_text_length(_FODP)},
    ]
    out = tmp_path / "fodg_fodp_gaps_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 5
    parsed = [json.loads(ln) for ln in lines]
    fmts = {r["fmt"] for r in parsed}
    assert "fodg" in fmts
    assert "fodp" in fmts
