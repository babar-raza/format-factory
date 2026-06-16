"""
tests/python/dogfood/test_dogfood_tsv_density_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-45
Dogfood export: TSV parse -> density/duplicate analytics -> write as NDJSON -> verify.
Uses: tsv_nonempty_cell_count, tsv_empty_row_count, tsv_duplicate_row_count,
tsv_average_cell_length, tsv_numeric_density, tsv_max_field_length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_nonempty_cell_count,
    tsv_empty_row_count,
    tsv_duplicate_row_count,
    tsv_average_cell_length,
    tsv_numeric_density,
    tsv_max_field_length,
    tsv_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    return [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]


class TestTsvDensityAnalyticsNdjsonExport:
    """TSV -> density/duplicate analytics -> NDJSON export -> roundtrip verification."""

    def test_nonempty_and_empty_rows(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        nonempty = tsv_nonempty_cell_count(sample)
        empty_rows = tsv_empty_row_count(sample)
        assert nonempty >= 0
        assert empty_rows >= 0

    def test_density_and_duplicates(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        density = tsv_numeric_density(sample)
        dups = tsv_duplicate_row_count(sample)
        avg_len = tsv_average_cell_length(sample)
        assert 0.0 <= density <= 1.0
        assert dups >= 0
        assert avg_len >= 0.0

    def test_density_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            nonempty = tsv_nonempty_cell_count(path)
            empty_rows = tsv_empty_row_count(path)
            dups = tsv_duplicate_row_count(path)
            avg_len = tsv_average_cell_length(path)
            density = tsv_numeric_density(path)
            max_field = tsv_max_field_length(path)
            total = tsv_total_cell_count(path)
            assert nonempty >= 0, f"nonempty_cell_count must be >= 0 for {f.name}"
            assert empty_rows >= 0, f"empty_row_count must be >= 0 for {f.name}"
            assert dups >= 0, f"duplicate_row_count must be >= 0 for {f.name}"
            assert avg_len >= 0.0, f"average_cell_length must be >= 0 for {f.name}"
            assert 0.0 <= density <= 1.0, f"numeric_density out of range for {f.name}"
            assert max_field >= 0, f"max_field_length must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "nonempty_cells": nonempty,
                "empty_row_count": empty_rows,
                "duplicate_rows": dups,
                "avg_cell_length": avg_len,
                "numeric_density": density,
                "max_field_length": max_field,
                "total_cells": total,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            records.append({
                "file": f.name,
                "nonempty_cells": tsv_nonempty_cell_count(path),
                "numeric_density": tsv_numeric_density(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["nonempty_cells"] == back["nonempty_cells"]
            assert abs(orig["numeric_density"] - back["numeric_density"]) < 1e-9

    def test_json_lines_valid(self, tmp_path):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        records = [{"file": "minimal-2x2.tsv", "numeric_density": tsv_numeric_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_duplicate_density_export(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            density = tsv_numeric_density(path)
            dups = tsv_duplicate_row_count(path)
            nonempty = tsv_nonempty_cell_count(path)
            assert 0.0 <= density <= 1.0
            assert dups >= 0
            assert nonempty >= 0
            records.append({
                "file": f.name,
                "numeric_density": density,
                "duplicate_rows": dups,
                "nonempty_cells": nonempty,
                "format": "tsv",
            })
        dest = tmp_path / "dup-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "tsv" for r in loaded)
        assert all(0.0 <= r["numeric_density"] <= 1.0 for r in loaded)
