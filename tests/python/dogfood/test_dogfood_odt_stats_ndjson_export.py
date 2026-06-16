"""
tests/python/dogfood/test_dogfood_odt_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-19
Dogfood export: ODT parse -> extract document stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    parse_odt,
    odt_word_count,
    odt_paragraph_count,
    odt_char_count,
    odt_heading_count,
    odt_has_tables,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtStatsNdjsonExport:
    """ODT -> document stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_odt_sample(self):
        sample = str(_ODT_DIR / "minimal-document.odt")
        doc = parse_odt(sample)
        assert isinstance(doc, dict)

    def test_extract_word_count(self):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        words = odt_word_count(sample)
        assert words >= 1

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ODT_DIR.glob("*.odt")):
            records.append({
                "file": f.name,
                "word_count": odt_word_count(str(f)),
                "paragraph_count": odt_paragraph_count(str(f)),
                "char_count": odt_char_count(str(f)),
                "heading_count": odt_heading_count(str(f)),
                "has_tables": odt_has_tables(str(f)),
                "source_format": "odt",
            })
        dest = tmp_path / "odt-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ODT_DIR.glob("*.odt")):
            records.append({
                "file": f.name,
                "word_count": odt_word_count(str(f)),
                "paragraph_count": odt_paragraph_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["word_count"] == back["word_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODT_DIR / "minimal-document.odt")
        records = [{"file": "minimal-document.odt", "words": odt_word_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_words_per_paragraph_in_export(self, tmp_path):
        records = []
        for f in sorted(_ODT_DIR.glob("*.odt")):
            words = odt_word_count(str(f))
            paras = odt_paragraph_count(str(f))
            records.append({
                "file": f.name,
                "words_per_para": words / paras if paras > 0 else 0.0,
                "format": "odt",
            })
        dest = tmp_path / "wpp.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "odt" for r in loaded)
