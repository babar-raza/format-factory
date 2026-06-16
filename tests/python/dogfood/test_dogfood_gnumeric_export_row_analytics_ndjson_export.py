"""
tests/python/dogfood/test_dogfood_gnumeric_export_row_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-74
Dogfood export: Gnumeric parse -> export/row analytics -> write as NDJSON -> verify.
Uses: load, export_to_csv, export_to_json, sum_column, get_row, read_cell.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    load,
    export_to_csv,
    export_to_json,
    sum_column,
    get_row,
    read_cell,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericExportRowAnalyticsNdjsonExport:
    """Gnumeric -> export/row analytics -> NDJSON export -> roundtrip verification."""

    def test_export_basics(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        csv_str = export_to_csv(sample, 0)
        json_str = export_to_json(sample)
        assert isinstance(csv_str, str)
        assert isinstance(json_str, str)

    def test_row_and_cell_basics(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        col_sum = sum_column(model, 0, 0)
        row_values = get_row(model, 0, 0)
        cell_val = read_cell(model, 0, 0, 0)
        assert isinstance(col_sum, float)
        assert isinstance(row_values, list)
        assert cell_val is None or isinstance(cell_val, str)

    def test_export_row_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            csv_str = export_to_csv(path, 0)
            json_str = export_to_json(path)
            col_sum = sum_column(model, 0, 0)
            row_values = get_row(model, 0, 0)
            cell_val = read_cell(model, 0, 0, 0)
            assert isinstance(csv_str, str), f"export_to_csv must be str for {f.name}"
            assert isinstance(json_str, str), f"export_to_json must be str for {f.name}"
            assert isinstance(col_sum, float), f"sum_column must be float for {f.name}"
            assert isinstance(row_values, list), f"get_row must be list for {f.name}"
            records.append({
                "file": f.name,
                "csv_length": len(csv_str),
                "json_length": len(json_str),
                "col0_sum": col_sum,
                "row0_value_count": len(row_values),
                "cell_0_0_is_none": cell_val is None,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-export-row.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            csv_str = export_to_csv(path, 0)
            col_sum = sum_column(model, 0, 0)
            records.append({
                "file": f.name,
                "csv_length": len(csv_str),
                "col0_sum": col_sum,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["csv_length"] == back["csv_length"]
            assert orig["col0_sum"] == back["col0_sum"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        csv_str = export_to_csv(sample, 0)
        col_sum = sum_column(model, 0, 0)
        records = [{"file": "sample.gnumeric", "csv_length": len(csv_str), "col0_sum": col_sum}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_export_row_sum_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            csv_str = export_to_csv(path, 0)
            json_str = export_to_json(path)
            col_sum = sum_column(model, 0, 0)
            row_values = get_row(model, 0, 0)
            assert isinstance(csv_str, str)
            assert isinstance(json_str, str)
            assert isinstance(col_sum, float)
            assert isinstance(row_values, list)
            records.append({
                "file": f.name,
                "csv_length": len(csv_str),
                "json_length": len(json_str),
                "col0_sum": col_sum,
                "row0_value_count": len(row_values),
                "format": "gnumeric",
            })
        dest = tmp_path / "export-row-sum.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["csv_length"] >= 0 for r in loaded)
