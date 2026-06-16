"""
tests/python/dogfood/test_dogfood_tsv_row_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-38
Dogfood export: TSV parse -> row/header analytics -> write as NDJSON -> verify.
Uses: tsv_numeric_cell_count, tsv_row_count, tsv_max_cell_length, tsv_has_header,
tsv_unique_row_count, tsv_header_count, tsv_column_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_numeric_cell_count,
    tsv_row_count,
    tsv_max_cell_length,
    tsv_has_header,
    tsv_unique_row_count,
    tsv_header_count,
    tsv_column_count,
    tsv_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    return [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]


class TestTsvRowAnalyticsNdjsonExport:
    """TSV -> row/header analytics -> NDJSON export -> roundtrip verification."""

    def test_row_and_col_counts(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        rows = tsv_row_count(sample)
        cols = tsv_column_count(sample)
        assert rows >= 0
        assert cols >= 0

    def test_header_analytics(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        has_hdr = tsv_has_header(sample)
        hdr_count = tsv_header_count(sample)
        unique = tsv_unique_row_count(sample)
        assert isinstance(has_hdr, bool)
        assert hdr_count >= 0
        assert unique >= 0

    def test_row_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            rows = tsv_row_count(path)
            cols = tsv_column_count(path)
            num_cells = tsv_numeric_cell_count(path)
            max_len = tsv_max_cell_length(path)
            has_hdr = tsv_has_header(path)
            unique = tsv_unique_row_count(path)
            hdr_count = tsv_header_count(path)
            total = tsv_total_cell_count(path)
            assert rows >= 0, f"row_count must be >= 0 for {f.name}"
            assert cols >= 0, f"column_count must be >= 0 for {f.name}"
            assert num_cells >= 0, f"numeric_cell_count must be >= 0 for {f.name}"
            assert max_len >= 0, f"max_cell_length must be >= 0 for {f.name}"
            assert isinstance(has_hdr, bool), f"has_header must be bool for {f.name}"
            assert unique >= 0, f"unique_row_count must be >= 0 for {f.name}"
            assert hdr_count >= 0, f"header_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "row_count": rows,
                "column_count": cols,
                "numeric_cell_count": num_cells,
                "max_cell_length": max_len,
                "has_header": has_hdr,
                "unique_rows": unique,
                "header_count": hdr_count,
                "total_cells": total,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-row-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            records.append({
                "file": f.name,
                "row_count": tsv_row_count(path),
                "has_header": tsv_has_header(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]
            assert orig["has_header"] == back["has_header"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        records = [{"file": "minimal-2x2.tsv", "row_count": tsv_row_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_header_unique_export(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            has_hdr = tsv_has_header(path)
            unique = tsv_unique_row_count(path)
            hdr_count = tsv_header_count(path)
            rows = tsv_row_count(path)
            assert isinstance(has_hdr, bool)
            assert unique >= 0
            assert hdr_count >= 0
            records.append({
                "file": f.name,
                "has_header": has_hdr,
                "unique_rows": unique,
                "header_count": hdr_count,
                "row_count": rows,
                "format": "tsv",
            })
        dest = tmp_path / "header-unique.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "tsv" for r in loaded)
        assert all(isinstance(r["has_header"], bool) for r in loaded)
