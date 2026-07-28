"""
tests/python/dogfood/test_dogfood_multiformat_spreadsheet_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-21
Cross-format dogfood: aggregate row/column/cell counts from CSV + SYLK + DIF + TSV
into a unified NDJSON export. Demonstrates spreadsheet format interoperability.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_row_count, csv_column_count, csv_total_cell_count
sys.path.insert(0, str(_REPO / "src" / "python"))
from sylk import sylk_row_count, sylk_column_count, sylk_total_cell_count
from dif import parse_dif
from dif.dif_stats import dif_stats
from tsv import count_rows as tsv_count_rows, column_count as tsv_column_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _collect_spreadsheet_records():
    records = []
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" in f.name:
            continue
        records.append({
            "file": f.name, "format": "csv",
            "row_count": csv_row_count(str(f)),
            "column_count": csv_column_count(str(f)),
            "total_cells": csv_total_cell_count(str(f)),
        })
    for f in sorted(_SYLK_DIR.glob("*.slk")):
        records.append({
            "file": f.name, "format": "sylk",
            "row_count": sylk_row_count(str(f)),
            "column_count": sylk_column_count(str(f)),
            "total_cells": sylk_total_cell_count(str(f)),
        })
    for f in sorted(_DIF_DIR.glob("*.dif")):
        doc = parse_dif(str(f))
        stats = dif_stats(doc)
        records.append({
            "file": f.name, "format": "dif",
            "row_count": stats.get("row_count", 0),
            "column_count": stats.get("column_count", 0),
            "total_cells": stats.get("total_cells", 0),
        })
    for f in sorted(_TSV_DIR.glob("*.tsv")):
        if "invalid" in f.name:
            continue
        records.append({
            "file": f.name, "format": "tsv",
            "row_count": tsv_count_rows(str(f)),
            "column_count": tsv_column_count(str(f)),
            "total_cells": tsv_count_rows(str(f)) * tsv_column_count(str(f)),
        })
    return records


class TestMultiformatSpreadsheetNdjsonExport:
    """Cross-format spreadsheet stats aggregation -> NDJSON -> verification."""

    def test_collects_from_four_formats(self):
        records = _collect_spreadsheet_records()
        formats = {r["format"] for r in records}
        assert "csv" in formats
        assert "sylk" in formats
        assert "dif" in formats
        assert "tsv" in formats

    def test_minimum_record_count(self):
        records = _collect_spreadsheet_records()
        assert len(records) >= 8

    def test_multiformat_to_ndjson(self, tmp_path):
        records = _collect_spreadsheet_records()
        dest = tmp_path / "spreadsheets.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)

    def test_ndjson_roundtrip(self, tmp_path):
        records = _collect_spreadsheet_records()
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]
            assert orig["row_count"] == back["row_count"]

    def test_json_lines_valid(self, tmp_path):
        records = _collect_spreadsheet_records()[:3]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "format" in obj

    def test_cell_density_cross_format(self, tmp_path):
        records = []
        for r in _collect_spreadsheet_records():
            expected = r["row_count"] * r["column_count"]
            density = r["total_cells"] / expected if expected > 0 else 0.0
            records.append({
                "file": r["file"], "format": r["format"],
                "cell_density": density,
            })
        dest = tmp_path / "density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        formats = {r["format"] for r in loaded}
        assert len(formats) >= 4
