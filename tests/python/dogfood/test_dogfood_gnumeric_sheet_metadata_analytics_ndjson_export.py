"""
tests/python/dogfood/test_dogfood_gnumeric_sheet_metadata_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-70
Dogfood export: Gnumeric parse -> sheet metadata analytics -> write as NDJSON -> verify.
Uses: load, get_sheet_metadata, get_cell_count, extract_values,
get_row_count, get_column_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    load,
    get_sheet_metadata,
    get_cell_count,
    extract_values,
    get_row_count,
    get_column_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericSheetMetadataAnalyticsNdjsonExport:
    """Gnumeric -> sheet metadata analytics -> NDJSON export -> roundtrip verification."""

    def test_sheet_metadata_basics(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        meta = get_sheet_metadata(sample)
        cell_count = get_cell_count(sample)
        assert isinstance(meta, list)
        assert cell_count >= 0

    def test_extract_values_and_counts(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        values = extract_values(sample)
        row_count = get_row_count(load(sample), 0)
        col_count = get_column_count(load(sample), 0)
        assert isinstance(values, list)
        assert row_count >= 0
        assert col_count >= 0

    def test_sheet_metadata_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            meta = get_sheet_metadata(path)
            cell_count = get_cell_count(path)
            values = extract_values(path)
            row_count = get_row_count(model, 0)
            col_count = get_column_count(model, 0)
            assert isinstance(meta, list), f"get_sheet_metadata must be list for {f.name}"
            assert cell_count >= 0, f"get_cell_count must be >= 0 for {f.name}"
            assert isinstance(values, list), f"extract_values must be list for {f.name}"
            assert row_count >= 0, f"get_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"get_column_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "sheet_count": len(meta),
                "total_cell_count": cell_count,
                "extracted_value_count": len(values),
                "row_count": row_count,
                "col_count": col_count,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-sheet-meta.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            meta = get_sheet_metadata(path)
            cell_count = get_cell_count(path)
            records.append({
                "file": f.name,
                "sheet_count": len(meta),
                "total_cell_count": cell_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]
            assert orig["total_cell_count"] == back["total_cell_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        meta = get_sheet_metadata(sample)
        cell_count = get_cell_count(sample)
        records = [{"file": "sample.gnumeric", "sheet_count": len(meta), "total_cell_count": cell_count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_meta_values_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            meta = get_sheet_metadata(path)
            values = extract_values(path)
            cell_count = get_cell_count(path)
            assert isinstance(meta, list)
            assert isinstance(values, list)
            assert cell_count >= 0
            records.append({
                "file": f.name,
                "sheet_count": len(meta),
                "extracted_value_count": len(values),
                "total_cell_count": cell_count,
                "format": "gnumeric",
            })
        dest = tmp_path / "meta-values.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["total_cell_count"] >= 0 for r in loaded)
