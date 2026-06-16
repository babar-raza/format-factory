"""
tests/python/dogfood/test_dogfood_gnumeric_metadata_export_ndjson.py

Sprint: IDEMPOTENT-SWARM-SPRINT-54
Dogfood export: Gnumeric parse -> sheet metadata + export analytics -> write as NDJSON.
Uses: load, get_sheet_metadata, export_to_json, average_column, sum_column,
get_sheet_names, get_sheet_count.
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
    export_to_json,
    average_column,
    sum_column,
    get_sheet_names,
    get_sheet_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericMetadataExportNdjson:
    """Gnumeric -> sheet metadata + export analytics -> NDJSON export -> roundtrip."""

    def test_sheet_metadata_and_names(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        metadata = get_sheet_metadata(sample)
        names = get_sheet_names(sample)
        sheet_count = get_sheet_count(sample)
        assert isinstance(metadata, list)
        assert isinstance(names, list)
        assert sheet_count >= 0

    def test_export_and_column_stats(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        json_str = export_to_json(sample)
        avg = average_column(model, 0, 0)
        total = sum_column(model, 0, 0)
        assert isinstance(json_str, str)
        assert isinstance(avg, float)
        assert isinstance(total, float)

    def test_metadata_export_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            metadata = get_sheet_metadata(path)
            names = get_sheet_names(path)
            sheet_count = get_sheet_count(path)
            json_str = export_to_json(path)
            avg = average_column(model, 0, 0)
            total = sum_column(model, 0, 0)
            assert isinstance(metadata, list), f"get_sheet_metadata must be list for {f.name}"
            assert isinstance(names, list), f"get_sheet_names must be list for {f.name}"
            assert sheet_count >= 0, f"get_sheet_count must be >= 0 for {f.name}"
            assert isinstance(json_str, str), f"export_to_json must be str for {f.name}"
            assert isinstance(avg, float), f"average_column must be float for {f.name}"
            assert isinstance(total, float), f"sum_column must be float for {f.name}"
            records.append({
                "file": f.name,
                "sheet_metadata_count": len(metadata),
                "sheet_name_count": len(names),
                "sheet_count": sheet_count,
                "json_export_length": len(json_str),
                "avg_col0": avg,
                "sum_col0": total,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-metadata.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            metadata = get_sheet_metadata(path)
            json_str = export_to_json(path)
            records.append({
                "file": f.name,
                "sheet_metadata_count": len(metadata),
                "json_export_length": len(json_str),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_metadata_count"] == back["sheet_metadata_count"]
            assert orig["json_export_length"] == back["json_export_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        metadata = get_sheet_metadata(sample)
        records = [{"file": "sample.gnumeric", "sheet_metadata_count": len(metadata)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_column_stats_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            avg = average_column(model, 0, 0)
            total = sum_column(model, 0, 0)
            names = get_sheet_names(path)
            assert isinstance(avg, float)
            assert isinstance(total, float)
            assert isinstance(names, list)
            records.append({
                "file": f.name,
                "avg_col0": avg,
                "sum_col0": total,
                "sheet_name_count": len(names),
                "format": "gnumeric",
            })
        dest = tmp_path / "column-stats.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["sheet_name_count"] >= 0 for r in loaded)
