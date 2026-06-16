"""
tests/python/dogfood/test_dogfood_tsv_uniformity_row_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-60
Dogfood export: TSV parse -> uniformity/row analytics -> write as NDJSON -> verify.
Uses: tsv_min_cell_length, tsv_all_rows_same_length, tsv_all_rows,
tsv_row_count, tsv_column_count, tsv_total_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_min_cell_length,
    tsv_all_rows_same_length,
    tsv_all_rows,
    tsv_row_count,
    tsv_numeric_density,
    tsv_max_cell_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    return sorted(_TSV_DIR.glob("*.tsv"))


class TestTsvUniformityRowAnalyticsNdjsonExport:
    """TSV -> uniformity/row analytics -> NDJSON export -> roundtrip verification."""

    def test_min_cell_length_and_uniformity(self):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        min_len = tsv_min_cell_length(sample)
        uniform = tsv_all_rows_same_length(sample)
        assert min_len >= 0
        assert isinstance(uniform, bool)

    def test_all_rows_and_counts(self):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        rows = tsv_all_rows(sample)
        row_count = tsv_row_count(sample)
        density = tsv_numeric_density(sample)
        max_len = tsv_max_cell_length(sample)
        assert isinstance(rows, list)
        assert row_count >= 0
        assert isinstance(density, float)
        assert max_len >= 0

    def test_uniformity_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            min_len = tsv_min_cell_length(path)
            uniform = tsv_all_rows_same_length(path)
            rows = tsv_all_rows(path)
            row_count = tsv_row_count(path)
            density = tsv_numeric_density(path)
            max_len = tsv_max_cell_length(path)
            assert min_len >= 0, f"tsv_min_cell_length must be >= 0 for {f.name}"
            assert isinstance(uniform, bool), f"tsv_all_rows_same_length must be bool for {f.name}"
            assert isinstance(rows, list), f"tsv_all_rows must be list for {f.name}"
            assert row_count >= 0, f"tsv_row_count must be >= 0 for {f.name}"
            assert isinstance(density, float), f"tsv_numeric_density must be float for {f.name}"
            assert max_len >= 0, f"tsv_max_cell_length must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "min_cell_length": min_len,
                "all_rows_same_length": uniform,
                "row_count_via_all_rows": len(rows),
                "row_count": row_count,
                "numeric_density": density,
                "max_cell_length": max_len,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-uniformity-row.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            min_len = tsv_min_cell_length(path)
            uniform = tsv_all_rows_same_length(path)
            records.append({
                "file": f.name,
                "min_cell_length": min_len,
                "all_rows_same_length": uniform,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["min_cell_length"] == back["min_cell_length"]
            assert orig["all_rows_same_length"] == back["all_rows_same_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        rows = tsv_all_rows(sample)
        records = [{"file": "sample.tsv", "row_count_via_all_rows": len(rows)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_min_uniform_export(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            min_len = tsv_min_cell_length(path)
            uniform = tsv_all_rows_same_length(path)
            rows = tsv_all_rows(path)
            assert min_len >= 0
            assert isinstance(uniform, bool)
            assert isinstance(rows, list)
            records.append({
                "file": f.name,
                "min_cell_length": min_len,
                "all_rows_same_length": uniform,
                "row_count_via_all_rows": len(rows),
                "format": "tsv",
            })
        dest = tmp_path / "min-uniform.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "tsv" for r in loaded)
        assert all(r["min_cell_length"] >= 0 for r in loaded)
