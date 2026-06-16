"""
tests/python/dogfood/test_dogfood_abw_paragraph_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-35
Dogfood export: ABW parse -> paragraph/word analytics -> write as NDJSON -> verify.
Uses deeper ABW analytics: abw_longest_word, abw_nonempty_paragraph_count,
abw_empty_paragraph_count, abw_max_paragraph_length, abw_shortest_word,
abw_has_sections, abw_has_metadata.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load as abw_load,
    abw_longest_word,
    abw_nonempty_paragraph_count,
    abw_empty_paragraph_count,
    abw_max_paragraph_length,
    abw_shortest_word,
    abw_has_sections,
    abw_has_metadata,
    abw_paragraph_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwParagraphAnalyticsNdjsonExport:
    """ABW -> paragraph/word analytics -> NDJSON export -> roundtrip verification."""

    def test_paragraph_counts(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        total = abw_paragraph_count(sample)
        nonempty = abw_nonempty_paragraph_count(sample)
        empty = abw_empty_paragraph_count(sample)
        assert total >= 0
        assert nonempty >= 0
        assert empty >= 0

    def test_word_length_extremes(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        model = abw_load(sample)
        longest = abw_longest_word(model)
        shortest = abw_shortest_word(sample)
        max_para = abw_max_paragraph_length(sample)
        assert isinstance(longest, str)
        assert isinstance(shortest, str)
        assert max_para >= 0

    def test_paragraph_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            total = abw_paragraph_count(path)
            nonempty = abw_nonempty_paragraph_count(path)
            empty = abw_empty_paragraph_count(path)
            max_para = abw_max_paragraph_length(path)
            has_secs = abw_has_sections(path)
            has_meta = abw_has_metadata(path)
            model = abw_load(path)
            longest = abw_longest_word(model)
            shortest = abw_shortest_word(path)
            assert total >= 0, f"paragraph_count must be >= 0 for {f.name}"
            assert nonempty >= 0, f"nonempty_count must be >= 0 for {f.name}"
            assert empty >= 0, f"empty_count must be >= 0 for {f.name}"
            assert max_para >= 0, f"max_paragraph_length must be >= 0 for {f.name}"
            assert isinstance(has_secs, bool), f"has_sections must be bool for {f.name}"
            assert isinstance(has_meta, bool), f"has_metadata must be bool for {f.name}"
            records.append({
                "file": f.name,
                "paragraph_count": total,
                "nonempty_paragraph_count": nonempty,
                "empty_paragraph_count": empty,
                "max_paragraph_length": max_para,
                "has_sections": has_secs,
                "has_metadata": has_meta,
                "longest_word": longest,
                "shortest_word": shortest,
                "source_format": "abw",
            })
        dest = tmp_path / "abw-paragraph.ndjson"
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
                "nonempty_paragraph_count": abw_nonempty_paragraph_count(path),
                "has_sections": abw_has_sections(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["nonempty_paragraph_count"] == back["nonempty_paragraph_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        records = [{"file": "two-paragraphs.abw", "max_para_length": abw_max_paragraph_length(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_metadata_sections_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            has_secs = abw_has_sections(path)
            has_meta = abw_has_metadata(path)
            nonempty = abw_nonempty_paragraph_count(path)
            assert isinstance(has_secs, bool)
            assert isinstance(has_meta, bool)
            assert nonempty >= 0
            records.append({
                "file": f.name,
                "has_sections": has_secs,
                "has_metadata": has_meta,
                "nonempty_paragraph_count": nonempty,
                "format": "abw",
            })
        dest = tmp_path / "metadata-sections.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(isinstance(r["has_sections"], bool) for r in loaded)
