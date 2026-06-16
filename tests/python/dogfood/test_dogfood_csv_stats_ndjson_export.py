"""
tests/python/dogfood/test_dogfood_csv_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-17
Dogfood export: CSV parse -> extract table stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    parse_csv,
    get_row_count,
    csv_column_count,
    csv_total_cell_count,
    csv_has_header,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_csv_files():
    return [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]


class TestCsvStatsNdjsonExport:
    """CSV -> table stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_csv_sample(self):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        doc = parse_csv(sample)
        assert isinstance(doc, dict)

    def test_extract_row_count(self):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        rows = get_row_count(sample)
        assert rows >= 1

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            records.append({
                "file": f.name,
                "row_count": get_row_count(str(f)),
                "column_count": csv_column_count(str(f)),
                "total_cells": csv_total_cell_count(str(f)),
                "has_header": csv_has_header(str(f)),
                "source_format": "csv",
            })
        dest = tmp_path / "csv-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            records.append({
                "file": f.name,
                "row_count": get_row_count(str(f)),
                "column_count": csv_column_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_CSV_DIR / "single-cell.csv")
        records = [{"file": "single-cell.csv", "rows": get_row_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_cell_density_in_export(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            rows = get_row_count(str(f))
            cols = csv_column_count(str(f))
            total = csv_total_cell_count(str(f))
            records.append({
                "file": f.name,
                "density": total / (rows * cols) if rows * cols > 0 else 0.0,
                "format": "csv",
            })
        dest = tmp_path / "density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "csv" for r in loaded)
