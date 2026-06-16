"""
tests/python/dogfood/test_dogfood_odt_heading_ratio_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-68
Dogfood export: ODT parse -> heading/ratio analytics -> write as NDJSON -> verify.
Uses: odt_has_headings, odt_min_paragraph_length, odt_heading_to_paragraph_ratio,
odt_word_count, odt_paragraph_count, odt_heading_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_has_headings,
    odt_min_paragraph_length,
    odt_heading_to_paragraph_ratio,
    odt_word_count,
    odt_paragraph_count,
    odt_heading_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


class TestOdtHeadingRatioAnalyticsNdjsonExport:
    """ODT -> heading/ratio analytics -> NDJSON export -> roundtrip verification."""

    def test_heading_basics(self):
        sample = str(next(_ODT_DIR.glob("*.odt")))
        has_headings = odt_has_headings(sample)
        min_para = odt_min_paragraph_length(sample)
        ratio = odt_heading_to_paragraph_ratio(sample)
        assert isinstance(has_headings, bool)
        assert min_para >= 0
        assert isinstance(ratio, float)

    def test_word_para_basics(self):
        sample = str(next(_ODT_DIR.glob("*.odt")))
        wc = odt_word_count(sample)
        pc = odt_paragraph_count(sample)
        hc = odt_heading_count(sample)
        assert wc >= 0
        assert pc >= 0
        assert hc >= 0

    def test_heading_ratio_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            has_headings = odt_has_headings(path)
            min_para = odt_min_paragraph_length(path)
            ratio = odt_heading_to_paragraph_ratio(path)
            wc = odt_word_count(path)
            pc = odt_paragraph_count(path)
            hc = odt_heading_count(path)
            assert isinstance(has_headings, bool), f"odt_has_headings must be bool for {f.name}"
            assert min_para >= 0, f"odt_min_paragraph_length must be >= 0 for {f.name}"
            assert isinstance(ratio, float), f"odt_heading_to_paragraph_ratio must be float for {f.name}"
            assert wc >= 0, f"odt_word_count must be >= 0 for {f.name}"
            assert pc >= 0, f"odt_paragraph_count must be >= 0 for {f.name}"
            assert hc >= 0, f"odt_heading_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "has_headings": has_headings,
                "min_paragraph_length": min_para,
                "heading_to_paragraph_ratio": ratio,
                "word_count": wc,
                "paragraph_count": pc,
                "heading_count": hc,
                "source_format": "odt",
            })
        dest = tmp_path / "odt-heading-ratio.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            has_headings = odt_has_headings(path)
            ratio = odt_heading_to_paragraph_ratio(path)
            records.append({
                "file": f.name,
                "has_headings": has_headings,
                "heading_to_paragraph_ratio": ratio,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["has_headings"] == back["has_headings"]
            assert orig["heading_to_paragraph_ratio"] == back["heading_to_paragraph_ratio"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODT_DIR.glob("*.odt")))
        has_headings = odt_has_headings(sample)
        min_para = odt_min_paragraph_length(sample)
        records = [{"file": "sample.odt", "has_headings": has_headings, "min_paragraph_length": min_para}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_heading_min_para_export(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            has_headings = odt_has_headings(path)
            min_para = odt_min_paragraph_length(path)
            ratio = odt_heading_to_paragraph_ratio(path)
            assert isinstance(has_headings, bool)
            assert min_para >= 0
            assert isinstance(ratio, float)
            records.append({
                "file": f.name,
                "has_headings": has_headings,
                "min_paragraph_length": min_para,
                "heading_to_paragraph_ratio": ratio,
                "format": "odt",
            })
        dest = tmp_path / "heading-min-para.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "odt" for r in loaded)
        assert all(isinstance(r["has_headings"], bool) for r in loaded)
