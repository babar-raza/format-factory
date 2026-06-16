"""
tests/python/dogfood/test_dogfood_abw_text_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-24
Dogfood export: ABW parse -> deep text analytics -> write as NDJSON -> verify.
Uses ABW-specific analytics (sentence count, unique words, char count, etc.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load as abw_load,
    abw_word_count,
    abw_paragraph_count,
    abw_sentence_count,
    abw_unique_word_count,
    abw_total_char_count,
    abw_average_word_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


class TestAbwTextAnalyticsNdjsonExport:
    """ABW -> deep text analytics -> NDJSON export -> roundtrip verification."""

    def test_word_count(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        count = abw_word_count(sample)
        assert count >= 1

    def test_sentence_count(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        doc = abw_load(sample)
        count = abw_sentence_count(doc)
        assert count >= 1

    def test_text_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            doc = abw_load(str(f))
            records.append({
                "file": f.name,
                "word_count": abw_word_count(str(f)),
                "paragraph_count": abw_paragraph_count(str(f)),
                "sentence_count": abw_sentence_count(doc),
                "unique_words": abw_unique_word_count(str(f)),
                "char_count": abw_total_char_count(str(f)),
                "avg_word_length": abw_average_word_length(str(f)),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            records.append({
                "file": f.name,
                "word_count": abw_word_count(str(f)),
                "unique_words": abw_unique_word_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["word_count"] == back["word_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ABW_DIR / "minimal-document.abw")
        records = [{"file": "minimal-document.abw", "words": abw_word_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_vocabulary_richness_export(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            words = abw_word_count(str(f))
            unique = abw_unique_word_count(str(f))
            records.append({
                "file": f.name,
                "vocab_richness": unique / words if words > 0 else 0.0,
                "format": "abw",
            })
        dest = tmp_path / "vocab.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
