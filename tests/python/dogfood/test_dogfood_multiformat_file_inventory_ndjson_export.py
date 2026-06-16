"""
tests/python/dogfood/test_dogfood_multiformat_file_inventory_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-30
Dogfood export: Scan all 16 format sample dirs -> collect file inventory -> write as NDJSON.
Cross-format file inventory with size, extension, and format family classification.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SAMPLES = _REPO / "samples" / "by-format"

_FORMAT_DIRS = {
    "abw": ("abw", "*.abw", "text"),
    "csv": ("csv", "*.csv", "tabular"),
    "dif": ("dif/valid", "*.dif", "tabular"),
    "fodg": ("fodg", "*.fodg", "drawing"),
    "fodp": ("fodp", "*.fodp", "presentation"),
    "fods": ("fods", "*.fods", "spreadsheet"),
    "fodt": ("fodt", "*.fodt", "text"),
    "gnumeric": ("gnumeric", "*.gnumeric", "spreadsheet"),
    "ods": ("ods/valid", "*.ods", "spreadsheet"),
    "odt": ("odt", "*.odt", "text"),
    "pbm": ("pbm/valid", "*.pbm", "image"),
    "pgm": ("pgm/valid", "*.pgm", "image"),
    "ppm": ("ppm/valid", "*.ppm", "image"),
    "qoi": ("qoi", "*.qoi", "image"),
    "sylk": ("sylk/valid", "*.slk", "tabular"),
    "tsv": ("tsv", "*.tsv", "tabular"),
}


def _collect_inventory():
    records = []
    for fmt, (subdir, glob_pat, family) in sorted(_FORMAT_DIRS.items()):
        fmt_dir = _SAMPLES / subdir
        if not fmt_dir.exists():
            continue
        for f in sorted(fmt_dir.glob(glob_pat)):
            if "invalid" in f.name:
                continue
            records.append({
                "file": f.name,
                "format": fmt,
                "family": family,
                "size_bytes": f.stat().st_size,
                "extension": f.suffix,
            })
    return records


class TestMultiformatFileInventoryNdjsonExport:
    """Cross-format file inventory -> NDJSON export -> roundtrip verification."""

    def test_inventory_has_files(self):
        records = _collect_inventory()
        assert len(records) >= 20, f"expected >=20 files across formats, got {len(records)}"

    def test_inventory_covers_formats(self):
        records = _collect_inventory()
        formats = {r["format"] for r in records}
        assert len(formats) >= 10, f"expected >=10 formats, got {formats}"

    def test_inventory_to_ndjson(self, tmp_path):
        records = _collect_inventory()
        dest = tmp_path / "file-inventory.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        families = {r["family"] for r in records}
        assert len(families) >= 4, f"expected >=4 families, got {families}"

    def test_ndjson_roundtrip(self, tmp_path):
        records = _collect_inventory()
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]
            assert orig["size_bytes"] == back["size_bytes"]

    def test_json_lines_valid(self, tmp_path):
        records = _collect_inventory()[:3]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "file" in obj
            assert "format" in obj

    def test_family_distribution(self, tmp_path):
        records = _collect_inventory()
        dest = tmp_path / "dist.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        families = {r["family"] for r in loaded}
        assert "text" in families
        assert "tabular" in families
        assert "image" in families
        assert "spreadsheet" in families
