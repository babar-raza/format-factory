"""
tests/python/dogfood/test_dogfood_gnumeric_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-77
Dogfood export: Gnumeric parse -> remaining analytics -> write as NDJSON -> verify.
Uses: load, probe_gnumeric, gnumeric_cell_count_all_sheets, gnumeric_is_single_sheet,
gnumeric_empty_sheet_count, gnumeric_has_any_string_cell, sum_row.
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
    probe_gnumeric,
    gnumeric_cell_count_all_sheets,
    gnumeric_is_single_sheet,
    gnumeric_empty_sheet_count,
    gnumeric_has_any_string_cell,
    sum_row,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericRemainingAnalyticsNdjsonExport:
    """Gnumeric -> remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_probe_and_cell_count_basics(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        is_valid = probe_gnumeric(sample)
        cell_count = gnumeric_cell_count_all_sheets(sample)
        is_single = gnumeric_is_single_sheet(sample)
        assert isinstance(is_valid, bool)
        assert cell_count >= 0
        assert isinstance(is_single, bool)

    def test_sheet_analytics_basics(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        empty_sheets = gnumeric_empty_sheet_count(sample)
        has_strings = gnumeric_has_any_string_cell(sample)
        model = load(sample)
        row_sum = sum_row(model, 0, 0)
        assert empty_sheets >= 0
        assert isinstance(has_strings, bool)
        assert isinstance(row_sum, float)

    def test_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            is_valid = probe_gnumeric(path)
            cell_count = gnumeric_cell_count_all_sheets(path)
            is_single = gnumeric_is_single_sheet(path)
            empty_sheets = gnumeric_empty_sheet_count(path)
            has_strings = gnumeric_has_any_string_cell(path)
            row_sum = sum_row(model, 0, 0)
            assert isinstance(is_valid, bool), f"probe_gnumeric must be bool for {f.name}"
            assert cell_count >= 0, f"gnumeric_cell_count_all_sheets must be >= 0 for {f.name}"
            assert isinstance(is_single, bool), f"gnumeric_is_single_sheet must be bool for {f.name}"
            assert empty_sheets >= 0, f"gnumeric_empty_sheet_count must be >= 0 for {f.name}"
            assert isinstance(has_strings, bool), f"gnumeric_has_any_string_cell must be bool for {f.name}"
            assert isinstance(row_sum, float), f"sum_row must be float for {f.name}"
            records.append({
                "file": f.name,
                "probe_valid": is_valid,
                "cell_count_all_sheets": cell_count,
                "is_single_sheet": is_single,
                "empty_sheet_count": empty_sheets,
                "has_any_string_cell": has_strings,
                "row0_sum": row_sum,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            cell_count = gnumeric_cell_count_all_sheets(path)
            is_single = gnumeric_is_single_sheet(path)
            records.append({
                "file": f.name,
                "cell_count_all_sheets": cell_count,
                "is_single_sheet": is_single,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["cell_count_all_sheets"] == back["cell_count_all_sheets"]
            assert orig["is_single_sheet"] == back["is_single_sheet"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        cell_count = gnumeric_cell_count_all_sheets(sample)
        has_strings = gnumeric_has_any_string_cell(sample)
        records = [{"file": "sample.gnumeric", "cell_count_all_sheets": cell_count, "has_any_string_cell": has_strings}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_probe_string_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            is_valid = probe_gnumeric(path)
            has_strings = gnumeric_has_any_string_cell(path)
            empty_sheets = gnumeric_empty_sheet_count(path)
            is_single = gnumeric_is_single_sheet(path)
            assert isinstance(is_valid, bool)
            assert isinstance(has_strings, bool)
            records.append({
                "file": f.name,
                "probe_valid": is_valid,
                "has_any_string_cell": has_strings,
                "empty_sheet_count": empty_sheets,
                "is_single_sheet": is_single,
                "format": "gnumeric",
            })
        dest = tmp_path / "probe-string.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(isinstance(r["probe_valid"], bool) for r in loaded)
