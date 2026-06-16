"""
tests/python/dogfood/test_dogfood_fodt_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-11
Dogfood export: FODT document parse -> extract stats -> write as NDJSON -> verify.
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
    document_paragraph_count,
    document_total_words,
    document_empty_paragraph_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


class TestFodtStatsNdjsonExport:
    """FODT -> document stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_fodt_sample(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        assert isinstance(doc, dict)

    def test_extract_stats(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        stats = document_stats(doc)
        assert isinstance(stats, dict)
        assert "paragraph_count" in stats or "block_count" in stats

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            para_count = document_paragraph_count(doc)
            word_count = document_total_words(doc)
            records.append({
                "file": f.name,
                "paragraphs": para_count,
                "words": word_count,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            records.append({
                "file": f.name,
                "paragraphs": document_paragraph_count(doc),
                "empty_paragraphs": document_empty_paragraph_count(doc),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["paragraphs"] == back["paragraphs"]
            assert orig["empty_paragraphs"] == back["empty_paragraphs"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        records = [{"file": "minimal-document.fodt", "words": document_total_words(doc)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_multi_file_with_stats(self, tmp_path):
        records = []
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            stats = document_stats(doc)
            records.append({
                "file": f.name,
                "stats": stats,
                "source_format": "fodt",
            })
        dest = tmp_path / "multi-stats.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert all(r["source_format"] == "fodt" for r in loaded)
