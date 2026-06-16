"""
tests/python/dogfood/test_dogfood_sylk_density_header_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-69
Dogfood export: SYLK parse -> density/header analytics -> write as NDJSON -> verify.
Uses: sylk_has_header, sylk_numeric_density, sylk_avg_row_length,
sylk_total_sum, sylk_max_column_index, sylk_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_has_header,
    sylk_numeric_density,
    sylk_avg_row_length,
    sylk_total_sum,
    sylk_max_column_index,
    sylk_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


class TestSylkDensityHeaderAnalyticsNdjsonExport:
    """SYLK -> density/header analytics -> NDJSON export -> roundtrip verification."""

    def test_header_and_density_basics(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        has_header = sylk_has_header(sample)
        density = sylk_numeric_density(sample)
        avg_row = sylk_avg_row_length(sample)
        assert isinstance(has_header, bool)
        assert isinstance(density, float)
        assert isinstance(avg_row, float)

    def test_sum_and_column_basics(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        total = sylk_total_sum(sample)
        max_col = sylk_max_column_index(sample)
        row_count = sylk_row_count(sample)
        assert isinstance(total, float)
        assert max_col >= 0
        assert row_count >= 0

    def test_density_header_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            has_header = sylk_has_header(path)
            density = sylk_numeric_density(path)
            avg_row = sylk_avg_row_length(path)
            total = sylk_total_sum(path)
            max_col = sylk_max_column_index(path)
            row_count = sylk_row_count(path)
            assert isinstance(has_header, bool), f"sylk_has_header must be bool for {f.name}"
            assert isinstance(density, float), f"sylk_numeric_density must be float for {f.name}"
            assert isinstance(avg_row, float), f"sylk_avg_row_length must be float for {f.name}"
            assert isinstance(total, float), f"sylk_total_sum must be float for {f.name}"
            assert max_col >= 0, f"sylk_max_column_index must be >= 0 for {f.name}"
            assert row_count >= 0, f"sylk_row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "has_header": has_header,
                "numeric_density": density,
                "avg_row_length": avg_row,
                "total_sum": total,
                "max_column_index": max_col,
                "row_count": row_count,
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-density-header.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            has_header = sylk_has_header(path)
            density = sylk_numeric_density(path)
            records.append({
                "file": f.name,
                "has_header": has_header,
                "numeric_density": density,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["has_header"] == back["has_header"]
            assert orig["numeric_density"] == back["numeric_density"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        has_header = sylk_has_header(sample)
        total = sylk_total_sum(sample)
        records = [{"file": "sample.slk", "has_header": has_header, "total_sum": total}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_header_density_export(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            has_header = sylk_has_header(path)
            density = sylk_numeric_density(path)
            avg_row = sylk_avg_row_length(path)
            total = sylk_total_sum(path)
            assert isinstance(has_header, bool)
            assert isinstance(density, float)
            assert isinstance(avg_row, float)
            assert isinstance(total, float)
            records.append({
                "file": f.name,
                "has_header": has_header,
                "numeric_density": density,
                "avg_row_length": avg_row,
                "total_sum": total,
                "format": "sylk",
            })
        dest = tmp_path / "header-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "sylk" for r in loaded)
        assert all(isinstance(r["has_header"], bool) for r in loaded)
