"""
tests/python/dogfood/test_dogfood_csv_data_profiling_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-31
Dogfood export: CSV parse -> data profiling analytics -> write as NDJSON -> verify.
Uses deeper CSV analytics: header detection, cell count, column count, row stats.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    csv_has_header,
    csv_total_cell_count,
    csv_column_count,
    get_row_count,
    parse_csv,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_csv_files():
    return [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]


class TestCsvDataProfilingNdjsonExport:
    """CSV -> data profiling analytics -> NDJSON export -> roundtrip verification."""

    def test_header_detection(self):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        has_hdr = csv_has_header(sample)
        assert isinstance(has_hdr, bool)

    def test_cell_column_counts(self):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        total = csv_total_cell_count(sample)
        cols = csv_column_count(sample)
        rows = get_row_count(sample)
        assert total >= 1
        assert cols >= 1
        assert rows >= 1

    def test_profiling_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            total = csv_total_cell_count(str(f))
            cols = csv_column_count(str(f))
            rows = get_row_count(str(f))
            assert total >= 0
            records.append({
                "file": f.name,
                "total_cells": total,
                "columns": cols,
                "rows": rows,
                "has_header": csv_has_header(str(f)),
                "avg_cells_per_row": total / rows if rows > 0 else 0.0,
                "source_format": "csv",
            })
        dest = tmp_path / "csv-profiling.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            records.append({
                "file": f.name,
                "total_cells": csv_total_cell_count(str(f)),
                "columns": csv_column_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_cells"] == back["total_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        records = [{"file": "minimal-2x2.csv", "cells": csv_total_cell_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_header_flag_export(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            records.append({
                "file": f.name,
                "has_header": csv_has_header(str(f)),
                "format": "csv",
            })
        dest = tmp_path / "headers.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "csv" for r in loaded)
        assert all(isinstance(r["has_header"], bool) for r in loaded)
