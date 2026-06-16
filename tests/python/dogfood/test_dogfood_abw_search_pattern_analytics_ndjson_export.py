"""
tests/python/dogfood/test_dogfood_abw_search_pattern_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-64
Dogfood export: ABW parse -> search/pattern analytics -> write as NDJSON -> verify.
Uses: load, contains_text, count_paragraphs_matching, get_words,
count_words, get_word_count, search_text.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load,
    contains_text,
    count_paragraphs_matching,
    get_words,
    count_words,
    get_word_count,
    search_text,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwSearchPatternAnalyticsNdjsonExport:
    """ABW -> search/pattern analytics -> NDJSON export -> roundtrip verification."""

    def test_contains_text_and_count_paragraphs_matching(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        has_text = contains_text(model, "the")
        match_count = count_paragraphs_matching(model, "the")
        assert isinstance(has_text, bool)
        assert match_count >= 0

    def test_words_and_word_counts(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        words = get_words(model, 0)
        count = count_words(model)
        word_count = get_word_count(model)
        results = search_text(model, "the")
        assert isinstance(words, list)
        assert count >= 0
        assert word_count >= 0
        assert isinstance(results, list)

    def test_search_pattern_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            has_text = contains_text(model, "the")
            match_count = count_paragraphs_matching(model, "the")
            words = get_words(model, 0)
            count = count_words(model)
            word_count = get_word_count(model)
            results = search_text(model, "the")
            assert isinstance(has_text, bool), f"contains_text must be bool for {f.name}"
            assert match_count >= 0, f"count_paragraphs_matching must be >= 0 for {f.name}"
            assert isinstance(words, list), f"get_words must be list for {f.name}"
            assert count >= 0, f"count_words must be >= 0 for {f.name}"
            assert word_count >= 0, f"get_word_count must be >= 0 for {f.name}"
            assert isinstance(results, list), f"search_text must be list for {f.name}"
            records.append({
                "file": f.name,
                "contains_the": has_text,
                "paragraphs_with_the": match_count,
                "first_para_word_count": len(words),
                "total_words_count": count,
                "word_count": word_count,
                "search_result_count": len(results),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-search-pattern.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            has_text = contains_text(model, "the")
            count = count_words(model)
            records.append({
                "file": f.name,
                "contains_the": has_text,
                "total_words_count": count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["contains_the"] == back["contains_the"]
            assert orig["total_words_count"] == back["total_words_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        count = count_words(model)
        records = [{"file": "sample.abw", "total_words_count": count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_search_words_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            match_count = count_paragraphs_matching(model, "the")
            words = get_words(model, 0)
            results = search_text(model, "the")
            assert match_count >= 0
            assert isinstance(words, list)
            assert isinstance(results, list)
            records.append({
                "file": f.name,
                "paragraphs_with_the": match_count,
                "first_para_word_count": len(words),
                "search_result_count": len(results),
                "format": "abw",
            })
        dest = tmp_path / "search-words.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(r["paragraphs_with_the"] >= 0 for r in loaded)
