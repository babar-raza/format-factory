"""
tests/python/dogfood/test_dogfood_odt_final_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-85
Dogfood export: ODT parse -> final analytics -> write as NDJSON -> verify.
Uses: odt_longest_word, odt_list_to_paragraph_ratio, odt_has_unicode,
      odt_max_words_per_paragraph, odt_min_words_per_paragraph, odt_word_density.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_longest_word,
    odt_list_to_paragraph_ratio,
    odt_has_unicode,
    odt_max_words_per_paragraph,
    odt_min_words_per_paragraph,
    odt_word_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


class TestOdtFinalAnalyticsNdjsonExport:
    """ODT -> final analytics -> NDJSON export -> roundtrip verification."""

    def test_word_analytics_basics(self):
        sample = _valid_odt_files()[0]
        path = str(sample)
        longest = odt_longest_word(path)
        max_wpp = odt_max_words_per_paragraph(path)
        min_wpp = odt_min_words_per_paragraph(path)
        assert isinstance(longest, int) and longest >= 0
        assert isinstance(max_wpp, int) and max_wpp >= 0
        assert isinstance(min_wpp, int) and min_wpp >= 0

    def test_ratio_density_basics(self):
        sample = _valid_odt_files()[0]
        path = str(sample)
        ratio = odt_list_to_paragraph_ratio(path)
        density = odt_word_density(path)
        has_unicode = odt_has_unicode(path)
        assert isinstance(ratio, float) and ratio >= 0.0
        assert isinstance(density, float) and density >= 0.0
        assert isinstance(has_unicode, bool)

    def test_final_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            longest = odt_longest_word(path)
            list_ratio = odt_list_to_paragraph_ratio(path)
            has_unicode = odt_has_unicode(path)
            max_wpp = odt_max_words_per_paragraph(path)
            min_wpp = odt_min_words_per_paragraph(path)
            word_density = odt_word_density(path)
            assert isinstance(longest, int), f"odt_longest_word must be int for {f.name}"
            assert isinstance(list_ratio, float), f"odt_list_to_paragraph_ratio must be float for {f.name}"
            assert isinstance(has_unicode, bool), f"odt_has_unicode must be bool for {f.name}"
            assert isinstance(max_wpp, int), f"odt_max_words_per_paragraph must be int for {f.name}"
            assert isinstance(min_wpp, int), f"odt_min_words_per_paragraph must be int for {f.name}"
            assert isinstance(word_density, float), f"odt_word_density must be float for {f.name}"
            records.append({
                "file": f.name,
                "longest_word": longest,
                "list_to_paragraph_ratio": list_ratio,
                "has_unicode": has_unicode,
                "max_words_per_paragraph": max_wpp,
                "min_words_per_paragraph": min_wpp,
                "word_density": word_density,
                "source_format": "odt",
            })
        dest = tmp_path / "odt-final-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            longest = odt_longest_word(path)
            has_unicode = odt_has_unicode(path)
            records.append({
                "file": f.name,
                "longest_word": longest,
                "has_unicode": has_unicode,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["longest_word"] == back["longest_word"]
            assert orig["has_unicode"] == back["has_unicode"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_odt_files()[0]
        path = str(sample)
        longest = odt_longest_word(path)
        word_density = odt_word_density(path)
        records = [{"file": sample.name, "longest_word": longest, "word_density": word_density}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_word_density_export(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            word_density = odt_word_density(path)
            max_wpp = odt_max_words_per_paragraph(path)
            min_wpp = odt_min_words_per_paragraph(path)
            list_ratio = odt_list_to_paragraph_ratio(path)
            assert word_density >= 0.0
            assert max_wpp >= min_wpp or max_wpp == 0
            records.append({
                "file": f.name,
                "word_density": word_density,
                "max_words_per_paragraph": max_wpp,
                "min_words_per_paragraph": min_wpp,
                "list_to_paragraph_ratio": list_ratio,
                "format": "odt",
            })
        dest = tmp_path / "word-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "odt" for r in loaded)
        assert all(r["word_density"] >= 0.0 for r in loaded)
