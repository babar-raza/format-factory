"""
tests/python/dogfood/test_dogfood_csv_rows_dicts_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-62
Dogfood export: CSV parse -> rows/dicts analytics -> write as NDJSON -> verify.
Uses: csv_all_rows, csv_to_dicts, csv_row_count, csv_column_count,
csv_average_field_length, csv_empty_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_all_rows,
    csv_to_dicts,
    csv_row_count,
    csv_column_count,
    csv_average_field_length,
    csv_empty_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

# Fix stdlib conflict: re-insert src-level path
sys.path.insert(0, str(_REPO / "src" / "python"))
from ndjson.ndjson_codec import write_ndjson, load_ndjson  # noqa: F811


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_csv_files():
    return sorted(_CSV_DIR.glob("*.csv"))


class TestCsvRowsDictsAnalyticsNdjsonExport:
    """CSV -> rows/dicts analytics -> NDJSON export -> roundtrip verification."""

    def test_all_rows_and_to_dicts(self):
        sample = str(next(_CSV_DIR.glob("*.csv")))
        rows = csv_all_rows(sample)
        dicts = csv_to_dicts(sample)
        assert isinstance(rows, list)
        assert isinstance(dicts, list)

    def test_row_count_and_column_stats(self):
        sample = str(next(_CSV_DIR.glob("*.csv")))
        row_count = csv_row_count(sample)
        col_count = csv_column_count(sample)
        avg_len = csv_average_field_length(sample)
        empty = csv_empty_cell_count(sample)
        assert row_count >= 0
        assert col_count >= 0
        assert isinstance(avg_len, float)
        assert empty >= 0

    def test_rows_dicts_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            rows = csv_all_rows(path)
            dicts = csv_to_dicts(path)
            row_count = csv_row_count(path)
            col_count = csv_column_count(path)
            avg_len = csv_average_field_length(path)
            empty = csv_empty_cell_count(path)
            assert isinstance(rows, list), f"csv_all_rows must be list for {f.name}"
            assert isinstance(dicts, list), f"csv_to_dicts must be list for {f.name}"
            assert row_count >= 0, f"csv_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"csv_column_count must be >= 0 for {f.name}"
            assert isinstance(avg_len, float), f"csv_average_field_length must be float for {f.name}"
            assert empty >= 0, f"csv_empty_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "all_rows_count": len(rows),
                "dict_count": len(dicts),
                "row_count": row_count,
                "col_count": col_count,
                "avg_field_length": avg_len,
                "empty_cell_count": empty,
                "source_format": "csv",
            })
        dest = tmp_path / "csv-rows-dicts.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            rows = csv_all_rows(path)
            dicts = csv_to_dicts(path)
            records.append({
                "file": f.name,
                "all_rows_count": len(rows),
                "dict_count": len(dicts),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["all_rows_count"] == back["all_rows_count"]
            assert orig["dict_count"] == back["dict_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_CSV_DIR.glob("*.csv")))
        rows = csv_all_rows(sample)
        records = [{"file": "sample.csv", "all_rows_count": len(rows)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_dicts_and_empty_cells_export(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            dicts = csv_to_dicts(path)
            empty = csv_empty_cell_count(path)
            avg_len = csv_average_field_length(path)
            assert isinstance(dicts, list)
            assert empty >= 0
            assert isinstance(avg_len, float)
            records.append({
                "file": f.name,
                "dict_count": len(dicts),
                "empty_cell_count": empty,
                "avg_field_length": avg_len,
                "format": "csv",
            })
        dest = tmp_path / "dicts-empty-cells.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "csv" for r in loaded)
        assert all(r["empty_cell_count"] >= 0 for r in loaded)
