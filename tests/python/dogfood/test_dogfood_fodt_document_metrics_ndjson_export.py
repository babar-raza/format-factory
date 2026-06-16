"""
tests/python/dogfood/test_dogfood_fodt_document_metrics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-42
Dogfood export: FODT parse -> document metrics -> write as NDJSON -> verify.
Uses: document_stats, document_word_count, document_reading_level,
document_hyperlink_count, document_footnote_count, document_section_summary.
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
    document_footnote_count,
    document_section_summary,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtDocumentMetricsNdjsonExport:
    """FODT -> document metrics -> NDJSON export -> roundtrip verification."""

    def test_document_stats(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        stats = document_stats(doc)
        assert isinstance(stats, dict)

    def test_word_count_and_reading_level(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        wc = document_word_count(doc)
        rl = document_reading_level(doc)
        assert isinstance(wc, dict)
        assert isinstance(rl, dict)

    def test_document_metrics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            stats = document_stats(doc)
            wc = document_word_count(doc)
            rl = document_reading_level(doc)
            hlinks = document_hyperlink_count(doc)
            footnotes = document_footnote_count(doc)
            sections = document_section_summary(doc)
            assert isinstance(stats, dict), f"document_stats must be dict for {f.name}"
            assert isinstance(wc, dict), f"document_word_count must be dict for {f.name}"
            assert isinstance(rl, dict), f"document_reading_level must be dict for {f.name}"
            assert isinstance(hlinks, dict), f"document_hyperlink_count must be dict for {f.name}"
            assert isinstance(footnotes, dict), f"document_footnote_count must be dict for {f.name}"
            assert isinstance(sections, dict), f"document_section_summary must be dict for {f.name}"
            records.append({
                "file": f.name,
                "has_stats": len(stats) > 0,
                "has_word_count": len(wc) > 0,
                "has_reading_level": len(rl) > 0,
                "hyperlink_count": hlinks,
                "footnote_count": footnotes,
                "section_count": sections,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-metrics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            stats = document_stats(doc)
            wc = document_word_count(doc)
            records.append({
                "file": f.name,
                "has_stats": isinstance(stats, dict),
                "has_word_count": isinstance(wc, dict),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["has_stats"] == back["has_stats"]
            assert orig["has_word_count"] == back["has_word_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        stats = document_stats(doc)
        records = [{"file": "minimal-document.fodt", "has_stats": isinstance(stats, dict)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_reading_level_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            rl = document_reading_level(doc)
            wc = document_word_count(doc)
            assert isinstance(rl, dict)
            assert isinstance(wc, dict)
            records.append({
                "file": f.name,
                "reading_level": rl,
                "word_count": wc,
                "format": "fodt",
            })
        dest = tmp_path / "reading-level.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(isinstance(r["reading_level"], dict) for r in loaded)
