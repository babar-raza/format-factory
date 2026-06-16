"""
tests/python/dogfood/test_dogfood_abw_structure_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-59
Dogfood export: ABW parse -> structure analytics -> write as NDJSON -> verify.
Uses: load, paragraph_lengths, get_unique_words, is_empty,
first_paragraph, last_paragraph.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load,
    paragraph_lengths,
    get_unique_words,
    is_empty,
    first_paragraph,
    last_paragraph,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwStructureAnalyticsNdjsonExport:
    """ABW -> structure analytics -> NDJSON export -> roundtrip verification."""

    def test_paragraph_lengths_and_unique_words(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        lengths = paragraph_lengths(model)
        unique = get_unique_words(model)
        assert isinstance(lengths, list)
        assert isinstance(unique, list)

    def test_first_last_paragraph_and_is_empty(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        first = first_paragraph(model)
        last = last_paragraph(model)
        empty = is_empty(model)
        assert isinstance(first, str)
        assert isinstance(last, str)
        assert isinstance(empty, bool)

    def test_structure_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            lengths = paragraph_lengths(model)
            unique = get_unique_words(model)
            empty = is_empty(model)
            first = first_paragraph(model)
            last = last_paragraph(model)
            assert isinstance(lengths, list), f"paragraph_lengths must be list for {f.name}"
            assert isinstance(unique, list), f"get_unique_words must be list for {f.name}"
            assert isinstance(empty, bool), f"is_empty must be bool for {f.name}"
            assert isinstance(first, str), f"first_paragraph must be str for {f.name}"
            assert isinstance(last, str), f"last_paragraph must be str for {f.name}"
            records.append({
                "file": f.name,
                "paragraph_count": len(lengths),
                "unique_word_count": len(unique),
                "is_empty": empty,
                "first_paragraph_length": len(first),
                "last_paragraph_length": len(last),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            lengths = paragraph_lengths(model)
            unique = get_unique_words(model)
            records.append({
                "file": f.name,
                "paragraph_count": len(lengths),
                "unique_word_count": len(unique),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["paragraph_count"] == back["paragraph_count"]
            assert orig["unique_word_count"] == back["unique_word_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        lengths = paragraph_lengths(model)
        records = [{"file": "sample.abw", "paragraph_count": len(lengths)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_first_last_lengths_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            first = first_paragraph(model)
            last = last_paragraph(model)
            empty = is_empty(model)
            assert isinstance(first, str)
            assert isinstance(last, str)
            assert isinstance(empty, bool)
            records.append({
                "file": f.name,
                "first_para_length": len(first),
                "last_para_length": len(last),
                "is_empty": empty,
                "format": "abw",
            })
        dest = tmp_path / "first-last-lengths.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(isinstance(r["is_empty"], bool) for r in loaded)
