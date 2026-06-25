"""Dogfood: SYLK + NDJSON analytics from gap-closure functions -> NDJSON export.

Collects analytics using the 4 gap-closure functions plus 4 new deepening
functions, exports as NDJSON, and validates the pipeline.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


def _first_slk():
    files = sorted((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
    assert files, "No SYLK samples"
    return str(files[0])


class TestSylkNdjsonGapAnalyticsExport:
    def test_sylk_analytics_pipeline(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson, load_ndjson
        from sylk import (
            sylk_min_cell_value_length, sylk_max_numeric_value,
            sylk_min_numeric_value, sylk_numeric_range,
            sylk_total_cell_count, sylk_numeric_density,
        )

        path = _first_slk()
        record = {
            "format": "sylk",
            "file": Path(path).name,
            "min_cell_value_length": sylk_min_cell_value_length(path),
            "max_numeric_value": sylk_max_numeric_value(path),
            "min_numeric_value": sylk_min_numeric_value(path),
            "numeric_range": sylk_numeric_range(path),
            "total_cells": sylk_total_cell_count(path),
            "numeric_density": sylk_numeric_density(path),
        }

        ndjson_path = tmp_path / "sylk-gap-analytics.ndjson"
        write_ndjson([record], str(ndjson_path))
        loaded = load_ndjson(str(ndjson_path))
        assert len(loaded) == 1
        assert loaded[0]["format"] == "sylk"
        assert loaded[0]["min_cell_value_length"] >= 0

    def test_ndjson_analytics_pipeline(self, tmp_path):
        from ndjson.ndjson_codec import (
            write_ndjson, load_ndjson,
            ndjson_all_records_nonempty, ndjson_max_field_name_length,
            ndjson_min_field_name_length, ndjson_field_type_distribution,
        )

        # Create a test NDJSON file
        src = tmp_path / "source.ndjson"
        write_ndjson([{"name": "Alice", "age": 30}, {"name": "Bob", "score": 95.5}], str(src))

        record = {
            "format": "ndjson",
            "file": "source.ndjson",
            "all_nonempty": ndjson_all_records_nonempty(str(src)),
            "max_field_name_len": ndjson_max_field_name_length(str(src)),
            "min_field_name_len": ndjson_min_field_name_length(str(src)),
            "type_distribution": ndjson_field_type_distribution(str(src)),
        }

        out = tmp_path / "ndjson-analytics.ndjson"
        write_ndjson([record], str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 1
        assert loaded[0]["all_nonempty"] is True
        assert loaded[0]["max_field_name_len"] >= 3

    def test_combined_multiformat_export(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson, load_ndjson
        from sylk import sylk_max_numeric_value, sylk_min_numeric_value
        from ndjson import ndjson_all_records_nonempty, ndjson_max_field_name_length

        records = []

        # SYLK record
        path = _first_slk()
        records.append({
            "format": "sylk",
            "max_numeric": sylk_max_numeric_value(path),
            "min_numeric": sylk_min_numeric_value(path),
        })

        # NDJSON self-analysis record
        src = tmp_path / "self.ndjson"
        write_ndjson([{"x": 1}], str(src))
        records.append({
            "format": "ndjson",
            "all_nonempty": ndjson_all_records_nonempty(str(src)),
            "max_field_name_len": ndjson_max_field_name_length(str(src)),
        })

        out = tmp_path / "combined.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 2
        formats = {r["format"] for r in loaded}
        assert formats == {"sylk", "ndjson"}

    def test_all_records_valid_json(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson
        from sylk import sylk_min_cell_value_length, sylk_max_numeric_value

        path = _first_slk()
        records = [
            {"metric": "min_cell_value_length", "value": sylk_min_cell_value_length(path)},
            {"metric": "max_numeric_value", "value": sylk_max_numeric_value(path)},
        ]
        out = tmp_path / "metrics.ndjson"
        write_ndjson(records, str(out))
        for line in out.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert "metric" in obj
            assert "value" in obj
