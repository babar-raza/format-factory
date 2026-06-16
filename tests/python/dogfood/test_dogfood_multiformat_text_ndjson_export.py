"""
tests/python/dogfood/test_dogfood_multiformat_text_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-20
Cross-format dogfood: aggregate word/paragraph counts from ABW + FODT + ODT
into a unified NDJSON export. Demonstrates Format Factory library interoperability.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import abw_word_count, abw_paragraph_count
from fodt import parse_fodt, document_total_words, document_paragraph_count
from odt import odt_word_count, odt_paragraph_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _collect_text_records():
    """Collect word/paragraph stats across ABW, FODT, and ODT formats."""
    records = []
    for f in sorted(_ABW_DIR.glob("*.abw")):
        records.append({
            "file": f.name,
            "format": "abw",
            "word_count": abw_word_count(str(f)),
            "paragraph_count": abw_paragraph_count(str(f)),
        })
    for f in sorted(_FODT_DIR.glob("*.fodt")):
        doc = parse_fodt(str(f))
        records.append({
            "file": f.name,
            "format": "fodt",
            "word_count": document_total_words(doc),
            "paragraph_count": document_paragraph_count(doc),
        })
    for f in sorted(_ODT_DIR.glob("*.odt")):
        records.append({
            "file": f.name,
            "format": "odt",
            "word_count": odt_word_count(str(f)),
            "paragraph_count": odt_paragraph_count(str(f)),
        })
    return records


class TestMultiformatTextNdjsonExport:
    """Cross-format text stats aggregation -> NDJSON export -> verification."""

    def test_collects_from_all_three_formats(self):
        records = _collect_text_records()
        formats = {r["format"] for r in records}
        assert "abw" in formats
        assert "fodt" in formats
        assert "odt" in formats

    def test_minimum_record_count(self):
        records = _collect_text_records()
        assert len(records) >= 6

    def test_multiformat_to_ndjson(self, tmp_path):
        records = _collect_text_records()
        dest = tmp_path / "text-formats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)

    def test_ndjson_roundtrip(self, tmp_path):
        records = _collect_text_records()
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]
            assert orig["word_count"] == back["word_count"]

    def test_json_lines_valid(self, tmp_path):
        records = _collect_text_records()[:2]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "format" in obj

    def test_words_per_paragraph_cross_format(self, tmp_path):
        records = []
        for r in _collect_text_records():
            wpp = r["word_count"] / r["paragraph_count"] if r["paragraph_count"] > 0 else 0.0
            records.append({
                "file": r["file"],
                "format": r["format"],
                "words_per_paragraph": wpp,
            })
        dest = tmp_path / "wpp.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        formats = {r["format"] for r in loaded}
        assert len(formats) >= 3
