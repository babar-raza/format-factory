"""
tests/python/dogfood/test_dogfood_csv_row_density_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-40
Dogfood export: CSV parse -> row/density analytics -> write as NDJSON -> verify.
Uses: csv_numeric_row_count, csv_duplicate_row_count, csv_empty_cell_count,
csv_row_count, csv_average_field_length, csv_numeric_density, csv_has_duplicates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    csv_numeric_row_count,
    csv_duplicate_row_count,
    csv_empty_cell_count,
    csv_row_count,
    csv_average_field_length,
    csv_numeric_density,
    csv_has_duplicates,
    csv_total_cell_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_csv_files():
    return [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]


class TestCsvRowDensityNdjsonExport:
    """CSV -> row/density analytics -> NDJSON export -> roundtrip verification."""

    def test_row_counts(self):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        rows = csv_row_count(sample)
        num_rows = csv_numeric_row_count(sample)
        assert rows >= 0
        assert num_rows >= 0

    def test_density_and_duplicates(self):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        density = csv_numeric_density(sample)
        has_dup = csv_has_duplicates(sample)
        avg_len = csv_average_field_length(sample)
        assert 0.0 <= density <= 1.0
        assert isinstance(has_dup, bool)
        assert avg_len >= 0.0

    def test_row_density_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            rows = csv_row_count(path)
            num_rows = csv_numeric_row_count(path)
            dup_rows = csv_duplicate_row_count(path)
            empty_cells = csv_empty_cell_count(path)
            avg_len = csv_average_field_length(path)
            density = csv_numeric_density(path)
            has_dup = csv_has_duplicates(path)
            total = csv_total_cell_count(path)
            assert rows >= 0, f"row_count must be >= 0 for {f.name}"
            assert num_rows >= 0, f"numeric_row_count must be >= 0 for {f.name}"
            assert dup_rows >= 0, f"duplicate_row_count must be >= 0 for {f.name}"
            assert empty_cells >= 0, f"empty_cell_count must be >= 0 for {f.name}"
            assert avg_len >= 0.0, f"average_field_length must be >= 0 for {f.name}"
            assert 0.0 <= density <= 1.0, f"numeric_density out of range for {f.name}"
            assert isinstance(has_dup, bool), f"has_duplicates must be bool for {f.name}"
            records.append({
                "file": f.name,
                "row_count": rows,
                "numeric_row_count": num_rows,
                "duplicate_row_count": dup_rows,
                "empty_cell_count": empty_cells,
                "average_field_length": avg_len,
                "numeric_density": density,
                "has_duplicates": has_dup,
                "total_cells": total,
                "source_format": "csv",
            })
        dest = tmp_path / "csv-row-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            records.append({
                "file": f.name,
                "row_count": csv_row_count(path),
                "numeric_density": csv_numeric_density(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]
            assert abs(orig["numeric_density"] - back["numeric_density"]) < 1e-9

    def test_json_lines_valid(self, tmp_path):
        sample = str(_CSV_DIR / "minimal-2x2.csv")
        records = [{"file": "minimal-2x2.csv", "row_count": csv_row_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_export(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            density = csv_numeric_density(path)
            has_dup = csv_has_duplicates(path)
            empty_cells = csv_empty_cell_count(path)
            assert 0.0 <= density <= 1.0
            assert isinstance(has_dup, bool)
            assert empty_cells >= 0
            records.append({
                "file": f.name,
                "numeric_density": density,
                "has_duplicates": has_dup,
                "empty_cell_count": empty_cells,
                "format": "csv",
            })
        dest = tmp_path / "density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "csv" for r in loaded)
        assert all(0.0 <= r["numeric_density"] <= 1.0 for r in loaded)
