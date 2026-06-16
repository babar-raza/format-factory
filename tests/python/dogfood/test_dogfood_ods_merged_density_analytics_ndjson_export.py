"""
tests/python/dogfood/test_dogfood_ods_merged_density_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-77
Dogfood export: ODS parse -> merged cell/density analytics -> write as NDJSON -> verify.
Uses: ods_max_row_length, ods_numeric_density, ods_has_merged_cells,
ods_merged_cell_count, ods_min_cell_value_length, ods_max_cell_value_length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_max_row_length,
    ods_numeric_density,
    ods_has_merged_cells,
    ods_merged_cell_count,
    ods_min_cell_value_length,
    ods_max_cell_value_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsMergedDensityAnalyticsNdjsonExport:
    """ODS -> merged cell/density analytics -> NDJSON export -> roundtrip verification."""

    def test_merged_cell_basics(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        has_merged = ods_has_merged_cells(sample)
        merged_count = ods_merged_cell_count(sample)
        assert isinstance(has_merged, bool)
        assert merged_count >= 0

    def test_density_length_basics(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        density = ods_numeric_density(sample)
        max_row = ods_max_row_length(sample)
        min_val_len = ods_min_cell_value_length(sample)
        max_val_len = ods_max_cell_value_length(sample)
        assert isinstance(density, float)
        assert max_row >= 0
        assert min_val_len >= 0
        assert max_val_len >= 0

    def test_merged_density_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            has_merged = ods_has_merged_cells(path)
            merged_count = ods_merged_cell_count(path)
            density = ods_numeric_density(path)
            max_row = ods_max_row_length(path)
            min_val_len = ods_min_cell_value_length(path)
            max_val_len = ods_max_cell_value_length(path)
            assert isinstance(has_merged, bool), f"ods_has_merged_cells must be bool for {f.name}"
            assert merged_count >= 0, f"ods_merged_cell_count must be >= 0 for {f.name}"
            assert isinstance(density, float), f"ods_numeric_density must be float for {f.name}"
            assert max_row >= 0, f"ods_max_row_length must be >= 0 for {f.name}"
            assert min_val_len >= 0, f"ods_min_cell_value_length must be >= 0 for {f.name}"
            assert max_val_len >= 0, f"ods_max_cell_value_length must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "has_merged_cells": has_merged,
                "merged_cell_count": merged_count,
                "numeric_density": density,
                "max_row_length": max_row,
                "min_cell_value_length": min_val_len,
                "max_cell_value_length": max_val_len,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-merged-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            density = ods_numeric_density(path)
            merged_count = ods_merged_cell_count(path)
            records.append({
                "file": f.name,
                "numeric_density": density,
                "merged_cell_count": merged_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["numeric_density"] == back["numeric_density"]
            assert orig["merged_cell_count"] == back["merged_cell_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        has_merged = ods_has_merged_cells(sample)
        density = ods_numeric_density(sample)
        records = [{"file": "sample.ods", "has_merged_cells": has_merged, "numeric_density": density}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_value_length_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            min_val_len = ods_min_cell_value_length(path)
            max_val_len = ods_max_cell_value_length(path)
            has_merged = ods_has_merged_cells(path)
            density = ods_numeric_density(path)
            assert min_val_len >= 0
            assert max_val_len >= 0
            assert isinstance(has_merged, bool)
            assert isinstance(density, float)
            records.append({
                "file": f.name,
                "min_cell_value_length": min_val_len,
                "max_cell_value_length": max_val_len,
                "has_merged_cells": has_merged,
                "numeric_density": density,
                "format": "ods",
            })
        dest = tmp_path / "value-length.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(isinstance(r["has_merged_cells"], bool) for r in loaded)
