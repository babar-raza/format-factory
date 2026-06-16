"""
tests/python/dogfood/test_dogfood_ods_sylk_quality_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-65
Dogfood export: ODS data quality analytics + SYLK unique values -> write as NDJSON -> verify.
Uses: ods_avg_cells_per_sheet, ods_data_density, ods_has_empty_rows (ODS);
sylk_unique_values (SYLK) + sylk_row_count, sylk_numeric_cell_count, sylk_string_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_avg_cells_per_sheet,
    ods_data_density,
    ods_has_empty_rows,
    ods_row_count,
    ods_column_count,
    ods_total_cell_count,
)
from sylk import (
    sylk_unique_values,
    sylk_row_count,
    sylk_numeric_cell_count,
    sylk_string_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


class TestOdsSylkQualityAnalyticsNdjsonExport:
    """ODS + SYLK data quality analytics -> NDJSON export -> roundtrip verification."""

    def test_ods_quality_basics(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        avg = ods_avg_cells_per_sheet(sample)
        density = ods_data_density(sample, 0)
        has_empty = ods_has_empty_rows(sample, 0)
        assert isinstance(avg, float)
        assert isinstance(density, float)
        assert isinstance(has_empty, bool)

    def test_sylk_unique_values(self):
        sample = str(next(_SYLK_DIR.glob("*.slk")))
        unique = sylk_unique_values(sample, 0)
        row_count = sylk_row_count(sample)
        assert isinstance(unique, list)
        assert row_count >= 0

    def test_ods_quality_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            avg = ods_avg_cells_per_sheet(path)
            density = ods_data_density(path, 0)
            has_empty = ods_has_empty_rows(path, 0)
            row_count = ods_row_count(path, 0)
            col_count = ods_column_count(path, 0)
            total = ods_total_cell_count(path, 0)
            assert isinstance(avg, float), f"ods_avg_cells_per_sheet must be float for {f.name}"
            assert isinstance(density, float), f"ods_data_density must be float for {f.name}"
            assert isinstance(has_empty, bool), f"ods_has_empty_rows must be bool for {f.name}"
            assert row_count >= 0, f"ods_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"ods_column_count must be >= 0 for {f.name}"
            assert total >= 0, f"ods_total_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_cells_per_sheet": avg,
                "data_density": density,
                "has_empty_rows": has_empty,
                "row_count": row_count,
                "col_count": col_count,
                "total_cells": total,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-quality.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_sylk_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            unique = sylk_unique_values(path, 0)
            row_count = sylk_row_count(path)
            num_count = sylk_numeric_cell_count(path)
            str_count = sylk_string_cell_count(path)
            assert isinstance(unique, list), f"sylk_unique_values must be list for {f.name}"
            assert row_count >= 0, f"sylk_row_count must be >= 0 for {f.name}"
            assert num_count >= 0, f"sylk_numeric_cell_count must be >= 0 for {f.name}"
            assert str_count >= 0, f"sylk_string_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "unique_col0_count": len(unique),
                "row_count": row_count,
                "numeric_count": num_count,
                "string_count": str_count,
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-quality.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            avg = ods_avg_cells_per_sheet(path)
            density = ods_data_density(path, 0)
            records.append({
                "file": f.name,
                "avg_cells_per_sheet": avg,
                "data_density": density,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_cells_per_sheet"] == back["avg_cells_per_sheet"]
            assert orig["data_density"] == back["data_density"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        avg = ods_avg_cells_per_sheet(sample)
        has_empty = ods_has_empty_rows(sample, 0)
        records = [{"file": "sample.ods", "avg_cells_per_sheet": avg, "has_empty_rows": has_empty}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_combined_format_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            avg = ods_avg_cells_per_sheet(path)
            has_empty = ods_has_empty_rows(path, 0)
            records.append({
                "file": f.name,
                "avg_cells_per_sheet": avg,
                "has_empty_rows": has_empty,
                "format": "ods",
            })
        for f in _valid_sylk_files():
            path = str(f)
            unique = sylk_unique_values(path, 0)
            row_count = sylk_row_count(path)
            records.append({
                "file": f.name,
                "unique_col0_count": len(unique),
                "row_count": row_count,
                "format": "sylk",
            })
        dest = tmp_path / "combined-quality.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 6
        ods_records = [r for r in loaded if r.get("format") == "ods"]
        sylk_records = [r for r in loaded if r.get("format") == "sylk"]
        assert len(ods_records) >= 3
        assert len(sylk_records) >= 3
