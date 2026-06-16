"""
tests/python/dogfood/test_dogfood_gnumeric_advanced_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-62
Dogfood export: Gnumeric parse -> advanced analytics -> write as NDJSON -> verify.
Uses: load, gnumeric_all_sheets_have_data, gnumeric_empty_cell_count,
gnumeric_min_cell_length, gnumeric_numeric_cell_count, gnumeric_sheet_summary,
gnumeric_string_cell_count.
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
    gnumeric_all_sheets_have_data,
    gnumeric_empty_cell_count,
    gnumeric_min_cell_length,
    gnumeric_numeric_cell_count,
    gnumeric_sheet_summary,
    gnumeric_string_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericAdvancedAnalyticsNdjsonExport:
    """Gnumeric -> advanced analytics -> NDJSON export -> roundtrip verification."""

    def test_all_sheets_have_data_and_min_cell_length(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        all_have_data = gnumeric_all_sheets_have_data(sample)
        min_len = gnumeric_min_cell_length(sample)
        assert isinstance(all_have_data, bool)
        assert min_len >= 0

    def test_model_based_cell_analytics(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        empty = gnumeric_empty_cell_count(model, 0)
        numeric = gnumeric_numeric_cell_count(model, 0)
        strings = gnumeric_string_cell_count(model, 0)
        summary = gnumeric_sheet_summary(model, 0)
        assert empty >= 0
        assert numeric >= 0
        assert strings >= 0
        assert isinstance(summary, dict)

    def test_advanced_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            all_have_data = gnumeric_all_sheets_have_data(path)
            min_len = gnumeric_min_cell_length(path)
            empty = gnumeric_empty_cell_count(model, 0)
            numeric = gnumeric_numeric_cell_count(model, 0)
            strings = gnumeric_string_cell_count(model, 0)
            summary = gnumeric_sheet_summary(model, 0)
            assert isinstance(all_have_data, bool), f"all_sheets_have_data must be bool for {f.name}"
            assert min_len >= 0, f"min_cell_length must be >= 0 for {f.name}"
            assert empty >= 0, f"empty_cell_count must be >= 0 for {f.name}"
            assert numeric >= 0, f"numeric_cell_count must be >= 0 for {f.name}"
            assert strings >= 0, f"string_cell_count must be >= 0 for {f.name}"
            assert isinstance(summary, dict), f"sheet_summary must be dict for {f.name}"
            records.append({
                "file": f.name,
                "all_sheets_have_data": all_have_data,
                "min_cell_length": min_len,
                "empty_cell_count": empty,
                "numeric_cell_count": numeric,
                "string_cell_count": strings,
                "sheet_summary_keys": len(summary),
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-advanced.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            empty = gnumeric_empty_cell_count(model, 0)
            numeric = gnumeric_numeric_cell_count(model, 0)
            records.append({
                "file": f.name,
                "empty_cell_count": empty,
                "numeric_cell_count": numeric,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["empty_cell_count"] == back["empty_cell_count"]
            assert orig["numeric_cell_count"] == back["numeric_cell_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        min_len = gnumeric_min_cell_length(sample)
        records = [{"file": "sample.gnumeric", "min_cell_length": min_len}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_summary_string_cells_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            strings = gnumeric_string_cell_count(model, 0)
            summary = gnumeric_sheet_summary(model, 0)
            all_have_data = gnumeric_all_sheets_have_data(path)
            assert strings >= 0
            assert isinstance(summary, dict)
            assert isinstance(all_have_data, bool)
            records.append({
                "file": f.name,
                "string_cell_count": strings,
                "sheet_summary_keys": len(summary),
                "all_sheets_have_data": all_have_data,
                "format": "gnumeric",
            })
        dest = tmp_path / "sheet-summary-strings.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["string_cell_count"] >= 0 for r in loaded)
