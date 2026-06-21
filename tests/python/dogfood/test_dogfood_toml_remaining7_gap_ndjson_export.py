"""Dogfood export: 7 TOML analytics gap functions → NDJSON.

Functions covered (previously uncovered by dogfood tests):
  toml_string_key_ratio, toml_min_key_length, toml_list_item_count,
  toml_is_single_table, toml_null_value_count, toml_distinct_key_count,
  toml_avg_numeric_value
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from toml.toml_codec import (
    toml_avg_numeric_value,
    toml_distinct_key_count,
    toml_is_single_table,
    toml_list_item_count,
    toml_min_key_length,
    toml_null_value_count,
    toml_string_key_ratio,
)

_SAMPLE = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")


def test_toml_string_key_ratio(tmp_path):
    val = toml_string_key_ratio(_SAMPLE)
    assert isinstance(val, float)
    assert val == 0.4
    record = {"metric": "toml_string_key_ratio", "value": val}
    out = tmp_path / "toml_string_key_ratio.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["value"] == 0.4


def test_toml_min_key_length(tmp_path):
    val = toml_min_key_length(_SAMPLE)
    assert isinstance(val, int)
    assert val == 5
    record = {"metric": "toml_min_key_length", "value": val}
    out = tmp_path / "toml_min_key_length.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert json.loads(lines[0])["value"] == 5


def test_toml_list_item_count(tmp_path):
    val = toml_list_item_count(_SAMPLE)
    assert isinstance(val, int)
    assert val == 0
    record = {"metric": "toml_list_item_count", "value": val}
    out = tmp_path / "toml_list_item_count.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert json.loads(lines[0])["value"] == 0


def test_toml_is_single_table(tmp_path):
    val = toml_is_single_table(_SAMPLE)
    assert isinstance(val, bool)
    assert val is False
    record = {"metric": "toml_is_single_table", "value": val}
    out = tmp_path / "toml_is_single_table.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert json.loads(lines[0])["value"] is False


def test_toml_null_value_count(tmp_path):
    val = toml_null_value_count(_SAMPLE)
    assert isinstance(val, int)
    assert val == 0
    record = {"metric": "toml_null_value_count", "value": val}
    out = tmp_path / "toml_null_value_count.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert json.loads(lines[0])["value"] == 0


def test_toml_distinct_key_count(tmp_path):
    val = toml_distinct_key_count(_SAMPLE)
    assert isinstance(val, int)
    assert val == 9
    record = {"metric": "toml_distinct_key_count", "value": val}
    out = tmp_path / "toml_distinct_key_count.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert json.loads(lines[0])["value"] == 9


def test_toml_avg_numeric_value(tmp_path):
    val = toml_avg_numeric_value(_SAMPLE)
    assert isinstance(val, float)
    assert val == 1.0
    record = {"metric": "toml_avg_numeric_value", "value": val}
    out = tmp_path / "toml_avg_numeric_value.ndjson"
    write_ndjson([record], str(out))
    lines = out.read_text().strip().splitlines()
    assert json.loads(lines[0])["value"] == 1.0


def test_all_metrics_batch_ndjson_export(tmp_path):
    records = [
        {"metric": "toml_string_key_ratio", "value": toml_string_key_ratio(_SAMPLE)},
        {"metric": "toml_min_key_length", "value": toml_min_key_length(_SAMPLE)},
        {"metric": "toml_list_item_count", "value": toml_list_item_count(_SAMPLE)},
        {"metric": "toml_is_single_table", "value": toml_is_single_table(_SAMPLE)},
        {"metric": "toml_null_value_count", "value": toml_null_value_count(_SAMPLE)},
        {"metric": "toml_distinct_key_count", "value": toml_distinct_key_count(_SAMPLE)},
        {"metric": "toml_avg_numeric_value", "value": toml_avg_numeric_value(_SAMPLE)},
    ]
    out = tmp_path / "toml_remaining7_gaps.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 7
    parsed = [json.loads(ln) for ln in lines]
    metrics = {r["metric"] for r in parsed}
    assert "toml_string_key_ratio" in metrics
    assert "toml_distinct_key_count" in metrics
    assert "toml_avg_numeric_value" in metrics
