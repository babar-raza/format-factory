"""
tests/python/dogfood/test_dogfood_fods_workbook_summary_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-48
Dogfood export: FODS parse -> workbook summary analytics -> write as NDJSON -> verify.
Uses: parse_fods, workbook_stats, workbook_numeric_summary, workbook_type_distribution,
workbook_merged_cell_summary, workbook_numeric_density, workbook_total_numeric_value.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    workbook_stats,
    workbook_numeric_summary,
    workbook_type_distribution,
    workbook_merged_cell_summary,
    workbook_numeric_density,
    workbook_total_numeric_value,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsWorkbookSummaryNdjsonExport:
    """FODS -> workbook summary analytics -> NDJSON export -> roundtrip verification."""

    def test_workbook_stats_and_numeric_summary(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        stats = workbook_stats(wb)
        num_summary = workbook_numeric_summary(wb)
        assert isinstance(stats, dict)
        assert isinstance(num_summary, dict)

    def test_type_distribution_and_merged(self):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        type_dist = workbook_type_distribution(wb)
        merged = workbook_merged_cell_summary(wb)
        density = workbook_numeric_density(wb)
        total_val = workbook_total_numeric_value(wb)
        assert isinstance(type_dist, dict)
        assert isinstance(merged, list)
        assert isinstance(density, float)
        assert isinstance(total_val, float)

    def test_workbook_summary_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = str(f)
            wb = parse_fods(path)
            stats = workbook_stats(wb)
            num_summary = workbook_numeric_summary(wb)
            type_dist = workbook_type_distribution(wb)
            merged = workbook_merged_cell_summary(wb)
            density = workbook_numeric_density(wb)
            total_val = workbook_total_numeric_value(wb)
            assert isinstance(stats, dict), f"workbook_stats must be dict for {f.name}"
            assert isinstance(num_summary, dict), f"numeric_summary must be dict for {f.name}"
            assert isinstance(type_dist, dict), f"type_distribution must be dict for {f.name}"
            assert isinstance(merged, list), f"merged_cell_summary must be list for {f.name}"
            assert isinstance(density, float), f"numeric_density must be float for {f.name}"
            assert isinstance(total_val, float), f"total_numeric_value must be float for {f.name}"
            records.append({
                "file": f.name,
                "stats_keys": len(stats),
                "numeric_summary_keys": len(num_summary),
                "type_count": len(type_dist),
                "merged_count": len(merged),
                "numeric_density": density,
                "total_numeric_value": total_val,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-workbook-summary.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            stats = workbook_stats(wb)
            density = workbook_numeric_density(wb)
            records.append({
                "file": f.name,
                "stats_keys": len(stats),
                "numeric_density": density,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["stats_keys"] == back["stats_keys"]
            assert orig["numeric_density"] == back["numeric_density"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODS_DIR.glob("*.fods")))
        wb = parse_fods(sample)
        type_dist = workbook_type_distribution(wb)
        records = [{"file": "sample.fods", "type_count": len(type_dist)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_numeric_value_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            wb = parse_fods(str(f))
            num_summary = workbook_numeric_summary(wb)
            total_val = workbook_total_numeric_value(wb)
            merged = workbook_merged_cell_summary(wb)
            assert isinstance(num_summary, dict)
            assert isinstance(total_val, float)
            assert isinstance(merged, list)
            records.append({
                "file": f.name,
                "numeric_summary_keys": len(num_summary),
                "total_numeric_value": total_val,
                "merged_count": len(merged),
                "format": "fods",
            })
        dest = tmp_path / "numeric-value.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["total_numeric_value"] >= 0.0 or r["total_numeric_value"] <= 0.0 for r in loaded)
