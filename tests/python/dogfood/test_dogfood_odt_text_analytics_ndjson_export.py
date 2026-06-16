"""
tests/python/dogfood/test_dogfood_odt_text_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-35
Dogfood export: ODT parse -> deep text analytics -> write as NDJSON -> verify.
Uses: odt_sentence_count, odt_average_word_length, odt_unique_word_count,
odt_longest_paragraph, odt_list_count, odt_table_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_sentence_count,
    odt_average_word_length,
    odt_unique_word_count,
    odt_longest_paragraph,
    odt_list_count,
    odt_table_count,
    odt_word_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


class TestOdtTextAnalyticsNdjsonExport:
    """ODT -> deep text analytics -> NDJSON export -> roundtrip verification."""

    def test_sentence_and_word_length(self):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        sc = odt_sentence_count(sample)
        awl = odt_average_word_length(sample)
        assert sc >= 0
        assert awl >= 0.0

    def test_unique_and_longest(self):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        uwc = odt_unique_word_count(sample)
        lp = odt_longest_paragraph(sample)
        wc = odt_word_count(sample)
        assert uwc >= 0
        assert uwc <= wc + 1
        assert lp >= 0

    def test_text_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            sc = odt_sentence_count(path)
            awl = odt_average_word_length(path)
            uwc = odt_unique_word_count(path)
            lp = odt_longest_paragraph(path)
            lc = odt_list_count(path)
            tc = odt_table_count(path)
            wc = odt_word_count(path)
            assert sc >= 0, f"sentence_count must be >= 0 for {f.name}"
            assert awl >= 0.0, f"average_word_length must be >= 0 for {f.name}"
            assert uwc >= 0, f"unique_word_count must be >= 0 for {f.name}"
            assert lp >= 0, f"longest_paragraph must be >= 0 for {f.name}"
            assert lc >= 0, f"list_count must be >= 0 for {f.name}"
            assert tc >= 0, f"table_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "sentence_count": sc,
                "average_word_length": awl,
                "unique_word_count": uwc,
                "longest_paragraph": lp,
                "list_count": lc,
                "table_count": tc,
                "word_count": wc,
                "source_format": "odt",
            })
        dest = tmp_path / "odt-text-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            records.append({
                "file": f.name,
                "sentence_count": odt_sentence_count(path),
                "unique_word_count": odt_unique_word_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sentence_count"] == back["sentence_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        records = [{"file": "two-paragraphs.odt", "sentence_count": odt_sentence_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_word_depth_export(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            awl = odt_average_word_length(path)
            uwc = odt_unique_word_count(path)
            lp = odt_longest_paragraph(path)
            assert awl >= 0.0
            assert uwc >= 0
            assert lp >= 0
            records.append({
                "file": f.name,
                "average_word_length": awl,
                "unique_word_count": uwc,
                "longest_paragraph": lp,
                "format": "odt",
            })
        dest = tmp_path / "word-depth.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "odt" for r in loaded)
        assert all(r["average_word_length"] >= 0.0 for r in loaded)
