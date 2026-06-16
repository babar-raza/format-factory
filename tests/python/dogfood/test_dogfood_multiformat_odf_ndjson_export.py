"""
tests/python/dogfood/test_dogfood_multiformat_odf_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-22
Cross-format dogfood: aggregate stats from all OpenDocument formats
(ODS, ODT, FODP, FODS, FODT, FODG) into a unified NDJSON export.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import ods_sheet_count, ods_row_count
from odt import odt_word_count, odt_paragraph_count
from fodp import fodp_slide_count
from fods import parse_fods
from fodt import parse_fodt, document_paragraph_count
from fodg import load as fodg_load, get_page_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _collect_odf_records():
    records = []
    for f in sorted(_ODS_DIR.glob("*.ods")):
        p = os.path.abspath(str(f))
        records.append({
            "file": f.name, "format": "ods", "odf_family": "spreadsheet",
            "primary_count": ods_sheet_count(p),
        })
    for f in sorted(_ODT_DIR.glob("*.odt")):
        records.append({
            "file": f.name, "format": "odt", "odf_family": "text",
            "primary_count": odt_paragraph_count(str(f)),
        })
    for f in sorted(_FODP_DIR.glob("*.fodp")):
        records.append({
            "file": f.name, "format": "fodp", "odf_family": "presentation",
            "primary_count": fodp_slide_count(str(f)),
        })
    for f in sorted(_FODS_DIR.glob("*.fods")):
        doc = parse_fods(os.path.abspath(str(f)))
        records.append({
            "file": f.name, "format": "fods", "odf_family": "spreadsheet",
            "primary_count": doc.get("sheet_count", 0),
        })
    for f in sorted(_FODT_DIR.glob("*.fodt")):
        doc = parse_fodt(str(f))
        records.append({
            "file": f.name, "format": "fodt", "odf_family": "text",
            "primary_count": document_paragraph_count(doc),
        })
    for f in sorted(_FODG_DIR.glob("*.fodg")):
        doc = fodg_load(str(f))
        records.append({
            "file": f.name, "format": "fodg", "odf_family": "graphics",
            "primary_count": get_page_count(doc),
        })
    return records


class TestMultiformatOdfNdjsonExport:
    """Cross-format ODF family aggregation -> NDJSON -> verification."""

    def test_collects_from_six_formats(self):
        records = _collect_odf_records()
        formats = {r["format"] for r in records}
        assert len(formats) >= 6

    def test_minimum_record_count(self):
        records = _collect_odf_records()
        assert len(records) >= 10

    def test_odf_to_ndjson(self, tmp_path):
        records = _collect_odf_records()
        dest = tmp_path / "odf-family.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)

    def test_ndjson_roundtrip(self, tmp_path):
        records = _collect_odf_records()
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]
            assert orig["odf_family"] == back["odf_family"]

    def test_json_lines_valid(self, tmp_path):
        records = _collect_odf_records()[:3]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "odf_family" in obj

    def test_odf_family_distribution(self, tmp_path):
        records = _collect_odf_records()
        dest = tmp_path / "dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        families = {r["odf_family"] for r in loaded}
        assert "spreadsheet" in families
        assert "text" in families
        assert "presentation" in families
        assert "graphics" in families
