"""
tests/python/dogfood/test_dogfood_sylk_sparsity_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-54
Dogfood export: SYLK parse -> sparsity analytics -> write as NDJSON -> verify.
Uses: sylk_avg_row_length, sylk_data_sparsity, sylk_max_cell_value_length,
sylk_min_col_index, sylk_row_count, sylk_column_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_avg_row_length,
    sylk_data_sparsity,
    sylk_max_cell_value_length,
    sylk_min_col_index,
    sylk_row_count,
    sylk_column_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


class TestSylkSparsityAnalyticsNdjsonExport:
    """SYLK -> sparsity analytics -> NDJSON export -> roundtrip verification."""

    def test_avg_row_length_and_sparsity(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        avg_row = sylk_avg_row_length(sample)
        sparsity = sylk_data_sparsity(sample)
        assert avg_row >= 0.0
        assert 0.0 <= sparsity <= 1.0

    def test_max_cell_length_and_min_col(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        max_len = sylk_max_cell_value_length(sample)
        min_col = sylk_min_col_index(sample)
        row_count = sylk_row_count(sample)
        col_count = sylk_column_count(sample)
        assert max_len >= 0
        assert min_col >= 0
        assert row_count >= 0
        assert col_count >= 0

    def test_sparsity_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            avg_row = sylk_avg_row_length(path)
            sparsity = sylk_data_sparsity(path)
            max_len = sylk_max_cell_value_length(path)
            min_col = sylk_min_col_index(path)
            row_count = sylk_row_count(path)
            col_count = sylk_column_count(path)
            assert avg_row >= 0.0, f"avg_row_length must be >= 0 for {f.name}"
            assert 0.0 <= sparsity <= 1.0, f"data_sparsity must be in [0,1] for {f.name}"
            assert max_len >= 0, f"max_cell_value_length must be >= 0 for {f.name}"
            assert min_col >= 0, f"min_col_index must be >= 0 for {f.name}"
            assert row_count >= 0, f"row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"column_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_row_length": avg_row,
                "data_sparsity": sparsity,
                "max_cell_value_length": max_len,
                "min_col_index": min_col,
                "row_count": row_count,
                "column_count": col_count,
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-sparsity.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            records.append({
                "file": f.name,
                "avg_row_length": sylk_avg_row_length(path),
                "data_sparsity": sylk_data_sparsity(path),
                "max_cell_value_length": sylk_max_cell_value_length(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_row_length"] == back["avg_row_length"]
            assert orig["data_sparsity"] == back["data_sparsity"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        records = [{"file": "sample.slk", "data_sparsity": sylk_data_sparsity(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sparsity_length_export(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            sparsity = sylk_data_sparsity(path)
            max_len = sylk_max_cell_value_length(path)
            min_col = sylk_min_col_index(path)
            assert 0.0 <= sparsity <= 1.0
            assert max_len >= 0
            assert min_col >= 0
            records.append({
                "file": f.name,
                "data_sparsity": sparsity,
                "max_cell_value_length": max_len,
                "min_col_index": min_col,
                "format": "sylk",
            })
        dest = tmp_path / "sparsity-length.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
        assert all(0.0 <= r["data_sparsity"] <= 1.0 for r in loaded)
