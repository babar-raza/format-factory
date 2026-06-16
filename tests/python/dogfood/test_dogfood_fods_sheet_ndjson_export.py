"""
tests/python/dogfood/test_dogfood_fods_sheet_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-12
Dogfood export: FODS parse -> extract sheet metadata -> write as NDJSON -> verify.
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


class TestFodsSheetNdjsonExport:
    """FODS -> sheet metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_fods_sample(self):
        sample = os.path.abspath(str(_FODS_DIR / "minimal-spreadsheet.fods"))
        doc = parse_fods(sample)
        assert isinstance(doc, dict)
        assert doc.get("sheet_count", 0) >= 1

    def test_extract_sheet_metadata(self):
        sample = os.path.abspath(str(_FODS_DIR / "multi-sheet-basic.fods"))
        doc = parse_fods(sample)
        assert doc.get("sheet_count", 0) >= 2
        sheets = doc.get("sheets", [])
        assert len(sheets) >= 2

    def test_sheet_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODS_DIR.glob("*.fods")):
            doc = parse_fods(os.path.abspath(str(f)))
            sheet_count = doc.get("sheet_count", 0)
            records.append({
                "file": f.name,
                "sheet_count": sheet_count,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-sheets.ndjson"
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
                "sheet_count": doc.get("sheet_count", 0),
                "has_warnings": len(doc.get("warnings", [])) > 0,
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
        records = [{"file": "minimal-spreadsheet.fods", "sheets": doc.get("sheet_count", 0)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_formula_file_metadata(self, tmp_path):
        sample = os.path.abspath(str(_FODS_DIR / "formula-basic.fods"))
        doc = parse_fods(sample)
        record = {
            "file": "formula-basic.fods",
            "sheet_count": doc.get("sheet_count", 0),
            "format": "fods",
            "odf_version": doc.get("odf_version_attr", ""),
        }
        dest = tmp_path / "formula.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["format"] == "fods"
        assert loaded[0]["sheet_count"] >= 1
