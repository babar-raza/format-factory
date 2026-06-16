"""
tests/python/dogfood/test_dogfood_xcf_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-14
Dogfood export: XCF parse -> extract image stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import parse_xcf, xcf_width, xcf_height, xcf_has_alpha
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfStatsNdjsonExport:
    """XCF -> image stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_xcf_sample(self):
        sample = os.path.abspath(str(_XCF_DIR / "2x2-gray.xcf"))
        img = parse_xcf(sample)
        assert isinstance(img, dict)

    def test_extract_dimensions(self):
        sample = os.path.abspath(str(_XCF_DIR / "2x2-gray.xcf"))
        assert xcf_width(sample) == 2
        assert xcf_height(sample) == 2

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_XCF_DIR.glob("*.xcf")):
            p = os.path.abspath(str(f))
            records.append({
                "file": f.name,
                "width": xcf_width(p),
                "height": xcf_height(p),
                "has_alpha": xcf_has_alpha(p),
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_XCF_DIR.glob("*.xcf")):
            p = os.path.abspath(str(f))
            records.append({
                "file": f.name,
                "width": xcf_width(p),
                "height": xcf_height(p),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["width"] == back["width"]
            assert orig["height"] == back["height"]

    def test_json_lines_valid(self, tmp_path):
        sample = os.path.abspath(str(_XCF_DIR / "1x1-red-rgb.xcf"))
        records = [{"file": "1x1-red-rgb.xcf", "width": xcf_width(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_alpha_in_export(self, tmp_path):
        records = []
        for f in sorted(_XCF_DIR.glob("*.xcf")):
            p = os.path.abspath(str(f))
            records.append({
                "file": f.name,
                "has_alpha": xcf_has_alpha(p),
                "pixels": xcf_width(p) * xcf_height(p),
                "format": "xcf",
            })
        dest = tmp_path / "alpha.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "xcf" for r in loaded)
