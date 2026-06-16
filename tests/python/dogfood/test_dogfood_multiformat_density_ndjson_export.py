"""
tests/python/dogfood/test_dogfood_multiformat_density_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-28
Dogfood export: Cross-format numeric density comparison (ODS + SYLK + Gnumeric) -> NDJSON.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import ods_numeric_density, ods_total_cell_count
from sylk import sylk_numeric_density, sylk_total_cell_count
from gnumeric import gnumeric_cell_count_file, gnumeric_sheet_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


class TestMultiformatDensityNdjsonExport:
    """Cross-format numeric density -> NDJSON export -> roundtrip verification."""

    def test_ods_density_valid(self):
        sample = _ap(_ODS_DIR / "minimal-spreadsheet.ods")
        d = ods_numeric_density(sample)
        assert 0.0 <= d <= 1.0

    def test_sylk_density_valid(self):
        sample = str(_SYLK_DIR / "minimal-2x2.slk")
        d = sylk_numeric_density(sample)
        assert 0.0 <= d <= 1.0

    def test_cross_density_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "format": "ods",
                "numeric_density": ods_numeric_density(p),
                "total_cells": ods_total_cell_count(p),
            })
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            records.append({
                "file": f.name,
                "format": "sylk",
                "numeric_density": sylk_numeric_density(str(f)),
                "total_cells": sylk_total_cell_count(str(f)),
            })
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            p = _ap(f)
            records.append({
                "file": f.name,
                "format": "gnumeric",
                "numeric_density": -1,
                "total_cells": gnumeric_cell_count_file(p),
            })
        dest = tmp_path / "multiformat-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        formats = {r["format"] for r in records}
        assert len(formats) >= 2, f"expected >=2 formats, got {formats}"

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            records.append({"file": f.name, "format": "ods", "density": ods_numeric_density(_ap(f))})
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            records.append({"file": f.name, "format": "sylk", "density": sylk_numeric_density(str(f))})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]

    def test_json_lines_valid(self, tmp_path):
        records = [
            {"file": "test.ods", "format": "ods", "density": ods_numeric_density(_ap(_ODS_DIR / "single-cell.ods"))},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_format_distribution(self, tmp_path):
        records = []
        for f in sorted(_ODS_DIR.glob("*.ods")):
            records.append({"file": f.name, "format": "ods"})
        for f in sorted(_SYLK_DIR.glob("*.slk")):
            records.append({"file": f.name, "format": "sylk"})
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            records.append({"file": f.name, "format": "gnumeric"})
        dest = tmp_path / "dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        formats = {r["format"] for r in loaded}
        assert "ods" in formats
        assert "sylk" in formats
