"""
tests/python/dogfood/test_dogfood_toml_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-DOGFOOD-TOML-20260616
Dogfood export: TOML parse -> analytics -> write as NDJSON -> verify roundtrip.
Uses: load_toml, toml_total_keys, toml_table_count, toml_string_density,
toml_boolean_value_count, toml_numeric_value_count, toml_list_count,
toml_has_tables, toml_has_lists, toml_is_empty, toml_string_value_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import (
    load_toml,
    toml_boolean_value_count,
    toml_has_lists,
    toml_has_tables,
    toml_is_empty,
    toml_list_count,
    toml_numeric_value_count,
    toml_string_density,
    toml_string_value_count,
    toml_table_count,
    toml_total_keys,
)
from ndjson.ndjson_codec import load_ndjson, write_ndjson

# ---------------------------------------------------------------------------
# Inline TOML samples (no sample files dir for TOML)
# ---------------------------------------------------------------------------

_SAMPLES = [
    (
        "app-config",
        b"""\
name = "format-factory"
version = "1.0"
debug = false
max_count = 42
tags = ["python", "toml", "codec"]

[meta]
author = "test"
""",
    ),
    (
        "server-config",
        b"""\
host = "localhost"
port = 8080
workers = 4
tls = true
log_level = "info"

[limits]
max_connections = 100
""",
    ),
    (
        "empty-config",
        b"""\
[settings]
""",
    ),
    (
        "flat-numeric",
        b"""\
alpha = 1
beta = 2
gamma = 3
delta = 4
epsilon = 5
""",
    ),
    (
        "mixed-types",
        b"""\
title = "test"
enabled = true
count = 7
ratio = 0.5
items = ["a", "b", "c"]

[section_a]
key = "value"

[section_b]
num = 99
""",
    ),
]


class TestTomlAnalyticsNdjsonExport:
    """TOML -> analytics -> NDJSON export -> roundtrip verification."""

    def test_total_keys_and_table_count(self):
        name, src = _SAMPLES[0]  # app-config
        total = toml_total_keys(src)
        tables = toml_table_count(src)
        assert total == 6, f"Expected 6 top-level keys, got {total}"
        assert tables == 1, f"Expected 1 table, got {tables}"

    def test_string_density_and_counts(self):
        name, src = _SAMPLES[0]  # app-config
        density = toml_string_density(src)
        str_count = toml_string_value_count(src)
        bool_count = toml_boolean_value_count(src)
        num_count = toml_numeric_value_count(src)
        list_count = toml_list_count(src)
        assert density >= 0.0
        assert str_count >= 1  # "format-factory" and "1.0"
        assert bool_count >= 1  # debug = false
        assert num_count >= 1   # max_count = 42
        assert list_count >= 1  # tags = [...]

    def test_has_tables_and_lists(self):
        name, src = _SAMPLES[0]  # app-config
        assert toml_has_tables(src) is True
        assert toml_has_lists(src) is True
        assert toml_is_empty(src) is False

    def test_empty_config(self):
        name, src = _SAMPLES[2]  # empty-config
        total = toml_total_keys(src)
        is_empty = toml_is_empty(src)
        assert total >= 0
        assert isinstance(is_empty, bool)

    def test_analytics_pipeline_to_ndjson(self, tmp_path):
        records = []
        for name, src in _SAMPLES:
            total_keys = toml_total_keys(src)
            tables = toml_table_count(src)
            density = toml_string_density(src)
            bool_count = toml_boolean_value_count(src)
            num_count = toml_numeric_value_count(src)
            lists = toml_list_count(src)
            has_tables = toml_has_tables(src)
            has_lists = toml_has_lists(src)
            is_empty = toml_is_empty(src)
            str_vals = toml_string_value_count(src)

            assert total_keys >= 0, f"total_keys must be >= 0 for {name}"
            assert tables >= 0, f"table_count must be >= 0 for {name}"
            assert density >= 0.0, f"string_density must be >= 0 for {name}"
            assert bool_count >= 0, f"boolean_value_count must be >= 0 for {name}"
            assert num_count >= 0, f"numeric_value_count must be >= 0 for {name}"
            assert lists >= 0, f"list_count must be >= 0 for {name}"
            assert isinstance(has_tables, bool), f"has_tables must be bool for {name}"
            assert isinstance(has_lists, bool), f"has_lists must be bool for {name}"
            assert isinstance(is_empty, bool), f"is_empty must be bool for {name}"
            assert str_vals >= 0, f"string_value_count must be >= 0 for {name}"

            records.append({
                "name": name,
                "total_keys": total_keys,
                "table_count": tables,
                "string_density": density,
                "boolean_value_count": bool_count,
                "numeric_value_count": num_count,
                "list_count": lists,
                "has_tables": has_tables,
                "has_lists": has_lists,
                "is_empty": is_empty,
                "string_value_count": str_vals,
                "source_format": "toml",
            })

        dest = tmp_path / "toml-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) == len(_SAMPLES)

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for name, src in _SAMPLES:
            records.append({
                "name": name,
                "total_keys": toml_total_keys(src),
                "table_count": toml_table_count(src),
                "string_density": toml_string_density(src),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["name"] == back["name"]
            assert orig["total_keys"] == back["total_keys"]
            assert orig["table_count"] == back["table_count"]
            assert abs(orig["string_density"] - back["string_density"]) < 1e-9

    def test_json_lines_valid(self, tmp_path):
        records = []
        for name, src in _SAMPLES:
            records.append({
                "name": name,
                "source_format": "toml",
                "total_keys": toml_total_keys(src),
                "has_tables": toml_has_tables(src),
            })
        dest = tmp_path / "valid-lines.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert obj["source_format"] == "toml"

    def test_boolean_and_numeric_density_pipeline(self, tmp_path):
        records = []
        for name, src in _SAMPLES:
            bool_count = toml_boolean_value_count(src)
            num_count = toml_numeric_value_count(src)
            total = toml_total_keys(src)
            bool_density = bool_count / total if total > 0 else 0.0
            num_density = num_count / total if total > 0 else 0.0
            records.append({
                "name": name,
                "boolean_density": bool_density,
                "numeric_density": num_density,
                "format": "toml",
            })
        dest = tmp_path / "type-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(_SAMPLES)
        assert all(r["format"] == "toml" for r in loaded)
        assert all(r["boolean_density"] >= 0.0 for r in loaded)
        assert all(r["numeric_density"] >= 0.0 for r in loaded)
