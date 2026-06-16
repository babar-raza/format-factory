"""
tests/python/dogfood/test_dogfood_gnumeric_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-15
Dogfood export: Gnumeric load -> extract analytics -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import load as gnumeric_load, sheet_names
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericAnalyticsNdjsonExport:
    """Gnumeric -> analytics extraction -> NDJSON export -> roundtrip verification."""

    def test_load_gnumeric_sample(self):
        sample = str(_GNUMERIC_DIR / "multi-cell-basic.gnumeric")
        doc = gnumeric_load(sample)
        assert isinstance(doc, dict)

    def test_extract_sheet_names(self):
        sample = str(_GNUMERIC_DIR / "multi-cell-basic.gnumeric")
        doc = gnumeric_load(sample)
        names = sheet_names(doc)
        assert isinstance(names, list)
        assert len(names) >= 1

    def test_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            doc = gnumeric_load(str(f))
            names = sheet_names(doc)
            records.append({
                "file": f.name,
                "sheet_count": len(names),
                "sheet_names": names,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
            doc = gnumeric_load(str(f))
            records.append({
                "file": f.name,
                "sheet_count": len(sheet_names(doc)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        doc = gnumeric_load(sample)
        records = [{"file": "minimal-spreadsheet.gnumeric", "sheets": len(sheet_names(doc))}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_info_in_export(self, tmp_path):
        sample = str(_GNUMERIC_DIR / "multi-cell-basic.gnumeric")
        doc = gnumeric_load(sample)
        names = sheet_names(doc)
        record = {
            "file": "multi-cell-basic.gnumeric",
            "first_sheet": names[0] if names else "",
            "format": "gnumeric",
        }
        dest = tmp_path / "sheet-info.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["format"] == "gnumeric"
        assert loaded[0]["first_sheet"] == names[0]
