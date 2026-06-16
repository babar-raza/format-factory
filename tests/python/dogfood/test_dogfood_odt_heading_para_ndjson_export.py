"""
tests/python/dogfood/test_dogfood_odt_heading_para_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-43
Dogfood export: ODT parse -> heading/paragraph analytics -> write as NDJSON -> verify.
Uses: odt_heading_count, odt_paragraph_count, odt_char_count, odt_has_tables,
odt_avg_paragraph_length, odt_words_per_sentence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_heading_count,
    odt_paragraph_count,
    odt_char_count,
    odt_has_tables,
    odt_avg_paragraph_length,
    odt_words_per_sentence,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


class TestOdtHeadingParaNdjsonExport:
    """ODT -> heading/paragraph analytics -> NDJSON export -> roundtrip verification."""

    def test_heading_and_para_counts(self):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        headings = odt_heading_count(sample)
        paras = odt_paragraph_count(sample)
        assert headings >= 0
        assert paras >= 0

    def test_char_count_and_tables(self):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        chars = odt_char_count(sample)
        has_tbl = odt_has_tables(sample)
        avg_len = odt_avg_paragraph_length(sample)
        assert chars >= 0
        assert isinstance(has_tbl, bool)
        assert avg_len >= 0.0

    def test_heading_para_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            headings = odt_heading_count(path)
            paras = odt_paragraph_count(path)
            chars = odt_char_count(path)
            has_tbl = odt_has_tables(path)
            avg_len = odt_avg_paragraph_length(path)
            wps = odt_words_per_sentence(path)
            assert headings >= 0, f"heading_count must be >= 0 for {f.name}"
            assert paras >= 0, f"paragraph_count must be >= 0 for {f.name}"
            assert chars >= 0, f"char_count must be >= 0 for {f.name}"
            assert isinstance(has_tbl, bool), f"has_tables must be bool for {f.name}"
            assert avg_len >= 0.0, f"avg_paragraph_length must be >= 0 for {f.name}"
            assert wps >= 0.0, f"words_per_sentence must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "heading_count": headings,
                "paragraph_count": paras,
                "char_count": chars,
                "has_tables": has_tbl,
                "avg_para_length": avg_len,
                "words_per_sentence": wps,
                "source_format": "odt",
            })
        dest = tmp_path / "odt-heading-para.ndjson"
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
                "heading_count": odt_heading_count(path),
                "paragraph_count": odt_paragraph_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["heading_count"] == back["heading_count"]
            assert orig["paragraph_count"] == back["paragraph_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ODT_DIR / "two-paragraphs.odt")
        records = [{"file": "two-paragraphs.odt", "heading_count": odt_heading_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_para_density_export(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            avg_len = odt_avg_paragraph_length(path)
            wps = odt_words_per_sentence(path)
            paras = odt_paragraph_count(path)
            assert avg_len >= 0.0
            assert wps >= 0.0
            assert paras >= 0
            records.append({
                "file": f.name,
                "avg_para_length": avg_len,
                "words_per_sentence": wps,
                "paragraph_count": paras,
                "format": "odt",
            })
        dest = tmp_path / "para-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "odt" for r in loaded)
        assert all(r["avg_para_length"] >= 0.0 for r in loaded)
