"""
tests/python/dogfood/test_dogfood_abw_word_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-42
Dogfood export: ABW parse -> word/char analytics -> write as NDJSON -> verify.
Uses: abw_sentence_count, abw_total_char_count, abw_word_count, abw_average_word_length,
abw_unique_word_count, abw_total_word_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load as abw_load,
    abw_sentence_count,
    abw_total_char_count,
    abw_word_count,
    abw_average_word_length,
    abw_unique_word_count,
    abw_total_word_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return [f for f in sorted(_ABW_DIR.glob("*.abw")) if "invalid" not in f.name]


class TestAbwWordAnalyticsNdjsonExport:
    """ABW -> word/char analytics -> NDJSON export -> roundtrip verification."""

    def test_sentence_and_char_count(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        model = abw_load(sample)
        sentences = abw_sentence_count(model)
        chars = abw_total_char_count(sample)
        assert sentences >= 0
        assert chars >= 0

    def test_word_counts(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        words = abw_word_count(sample)
        unique = abw_unique_word_count(sample)
        avg_len = abw_average_word_length(sample)
        total = abw_total_word_count(sample)
        assert words >= 0
        assert unique >= 0
        assert avg_len >= 0.0
        assert total >= 0

    def test_word_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = abw_load(path)
            sentences = abw_sentence_count(model)
            chars = abw_total_char_count(path)
            words = abw_word_count(path)
            avg_len = abw_average_word_length(path)
            unique = abw_unique_word_count(path)
            total = abw_total_word_count(path)
            assert sentences >= 0, f"sentence_count must be >= 0 for {f.name}"
            assert chars >= 0, f"total_char_count must be >= 0 for {f.name}"
            assert words >= 0, f"word_count must be >= 0 for {f.name}"
            assert avg_len >= 0.0, f"average_word_length must be >= 0 for {f.name}"
            assert unique >= 0, f"unique_word_count must be >= 0 for {f.name}"
            assert total >= 0, f"total_word_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "sentence_count": sentences,
                "total_char_count": chars,
                "word_count": words,
                "average_word_length": avg_len,
                "unique_word_count": unique,
                "total_word_count": total,
                "source_format": "abw",
            })
        dest = tmp_path / "abw-word-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            records.append({
                "file": f.name,
                "word_count": abw_word_count(path),
                "total_char_count": abw_total_char_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["word_count"] == back["word_count"]
            assert orig["total_char_count"] == back["total_char_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        records = [{"file": "two-paragraphs.abw", "word_count": abw_word_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_word_density_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            words = abw_word_count(path)
            unique = abw_unique_word_count(path)
            avg_len = abw_average_word_length(path)
            assert words >= 0
            assert unique >= 0
            assert avg_len >= 0.0
            records.append({
                "file": f.name,
                "word_count": words,
                "unique_words": unique,
                "avg_word_length": avg_len,
                "format": "abw",
            })
        dest = tmp_path / "word-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(r["word_count"] >= 0 for r in loaded)
