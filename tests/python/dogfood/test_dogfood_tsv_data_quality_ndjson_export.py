"""
tests/python/dogfood/test_dogfood_tsv_data_quality_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-26
Dogfood export: TSV parse -> data quality analytics -> write as NDJSON -> verify.
Uses deeper TSV analytics: numeric density, cell length, duplicates, empty rows, etc.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_numeric_density,
    tsv_average_cell_length,
    tsv_duplicate_row_count,
    tsv_empty_row_count,
    tsv_nonempty_cell_count,
    tsv_max_field_length,
    tsv_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    return [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]


class TestTsvDataQualityNdjsonExport:
    """TSV -> data quality analytics -> NDJSON export -> roundtrip verification."""

    def test_numeric_density(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        density = tsv_numeric_density(sample)
        assert isinstance(density, (int, float))
        assert 0.0 <= density <= 1.0, f"density {density} must be in [0, 1]"

    def test_average_cell_length(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        avg = tsv_average_cell_length(sample)
        assert isinstance(avg, (int, float))
        assert avg > 0, "non-empty TSV must have positive average cell length"

    def test_data_quality_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            dup = tsv_duplicate_row_count(str(f))
            total = tsv_total_cell_count(str(f))
            nonempty = tsv_nonempty_cell_count(str(f))
            assert dup >= 0, f"duplicate count must be non-negative for {f.name}"
            assert nonempty <= total, f"nonempty ({nonempty}) cannot exceed total ({total})"
            records.append({
                "file": f.name,
                "numeric_density": tsv_numeric_density(str(f)),
                "avg_cell_length": tsv_average_cell_length(str(f)),
                "duplicate_rows": dup,
                "empty_rows": tsv_empty_row_count(str(f)),
                "nonempty_cells": nonempty,
                "max_field_length": tsv_max_field_length(str(f)),
                "total_cells": total,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-data-quality.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            records.append({
                "file": f.name,
                "numeric_density": tsv_numeric_density(str(f)),
                "total_cells": tsv_total_cell_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_cells"] == back["total_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_TSV_DIR / "single-cell.tsv")
        records = [{"file": "single-cell.tsv", "density": tsv_numeric_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_quality_summary_export(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            total = tsv_total_cell_count(str(f))
            nonempty = tsv_nonempty_cell_count(str(f))
            fill_rate = nonempty / total if total > 0 else 0.0
            assert 0.0 <= fill_rate <= 1.0, f"fill_rate {fill_rate} out of range for {f.name}"
            records.append({
                "file": f.name,
                "fill_rate": fill_rate,
                "format": "tsv",
            })
        dest = tmp_path / "quality.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "tsv" for r in loaded)
        assert all(0.0 <= r["fill_rate"] <= 1.0 for r in loaded)
