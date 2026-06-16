"""
tests/python/dogfood/test_dogfood_fodt_depth_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-31
Dogfood export: FODT parse -> document depth analytics -> write as NDJSON -> verify.
Uses deeper FODT analytics: document_stats, word_count, reading_level, hyperlink_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_stats,
    document_word_count,
    document_reading_level,
    document_hyperlink_count,
    document_paragraph_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


class TestFodtDepthAnalyticsNdjsonExport:
    """FODT -> document depth analytics -> NDJSON export -> roundtrip verification."""

    def test_document_stats(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        stats = document_stats(doc)
        assert isinstance(stats, dict)
        assert "block_count" in stats or "paragraph_count" in stats or len(stats) > 0

    def test_word_count(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        wc = document_word_count(doc)
        assert isinstance(wc, dict)

    def test_depth_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            stats = document_stats(doc)
            wc = document_word_count(doc)
            rl = document_reading_level(doc)
            hc = document_hyperlink_count(doc)
            paras = document_paragraph_count(doc)
            assert paras >= 0, f"paragraph_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "paragraph_count": paras,
                "stats": stats,
                "word_count": wc,
                "reading_level": rl,
                "hyperlinks": hc,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-depth.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            records.append({
                "file": f.name,
                "paragraphs": document_paragraph_count(doc),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["paragraphs"] == back["paragraphs"]

    def test_json_lines_valid(self, tmp_path):
        doc = parse_fodt(str(_FODT_DIR / "minimal-document.fodt"))
        records = [{"file": "minimal-document.fodt", "paras": document_paragraph_count(doc)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_reading_level_export(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            rl = document_reading_level(doc)
            records.append({
                "file": f.name,
                "reading_level": rl,
                "format": "fodt",
            })
        dest = tmp_path / "reading.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
