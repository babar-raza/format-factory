"""
tests/python/dogfood/test_dogfood_fods_cell_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-24
Dogfood export: FODS parse -> extract sheet/cell analytics -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


class TestFodsCellAnalyticsNdjsonExport:
    """FODS -> sheet/cell analytics extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_fods(self):
        sample = os.path.abspath(str(_FODS_DIR / "minimal-spreadsheet.fods"))
        doc = parse_fods(sample)
        assert isinstance(doc, dict)
        assert doc["sheet_count"] >= 1

    def test_sheet_details(self):
        sample = os.path.abspath(str(_FODS_DIR / "multi-sheet-basic.fods"))
        doc = parse_fods(sample)
        assert doc["sheet_count"] >= 2

    def test_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODS_DIR.glob("*.fods")):
            doc = parse_fods(os.path.abspath(str(f)))
            total_cells = sum(
                sum(len(row.get("cells", [])) for row in sheet.get("rows", []))
                for sheet in doc.get("sheets", [])
            )
            records.append({
                "file": f.name,
                "sheet_count": doc["sheet_count"],
                "total_cells": total_cells,
                "has_warnings": len(doc.get("warnings", [])) > 0,
                "odf_version": doc.get("odf_version_attr", ""),
                "source_format": "fods",
            })
        dest = tmp_path / "fods-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_FODS_DIR.glob("*.fods")):
            doc = parse_fods(os.path.abspath(str(f)))
            records.append({
                "file": f.name,
                "sheet_count": doc["sheet_count"],
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = os.path.abspath(str(_FODS_DIR / "minimal-spreadsheet.fods"))
        doc = parse_fods(sample)
        records = [{"file": "minimal-spreadsheet.fods", "sheets": doc["sheet_count"]}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_cells_per_sheet_export(self, tmp_path):
        records = []
        for f in sorted(_FODS_DIR.glob("*.fods")):
            doc = parse_fods(os.path.abspath(str(f)))
            total_cells = sum(
                sum(len(row.get("cells", [])) for row in sheet.get("rows", []))
                for sheet in doc.get("sheets", [])
            )
            sheets = doc["sheet_count"]
            records.append({
                "file": f.name,
                "cells_per_sheet": total_cells / sheets if sheets > 0 else 0.0,
                "format": "fods",
            })
        dest = tmp_path / "cps.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
