"""
tests/python/dogfood/test_dogfood_fodt_structure_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-49
Dogfood export: FODT parse -> structural analytics -> write as NDJSON -> verify.
Uses: fodt_average_paragraph_length, fodt_has_tables, fodt_heading_count,
fodt_list_count, fodt_max_paragraph_length, fodt_paragraph_count, fodt_word_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    fodt_average_paragraph_length,
    fodt_has_tables,
    fodt_heading_count,
    fodt_list_count,
    fodt_max_paragraph_length,
    fodt_paragraph_count,
    fodt_word_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtStructureAnalyticsNdjsonExport:
    """FODT -> structural analytics -> NDJSON export -> roundtrip verification."""

    def test_avg_paragraph_and_has_tables(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        avg = fodt_average_paragraph_length(sample)
        has_tables = fodt_has_tables(sample)
        assert avg >= 0.0
        assert isinstance(has_tables, bool)

    def test_heading_list_max_counts(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        headings = fodt_heading_count(sample)
        lists = fodt_list_count(sample)
        max_para = fodt_max_paragraph_length(sample)
        para_count = fodt_paragraph_count(sample)
        words = fodt_word_count(sample)
        assert headings >= 0
        assert lists >= 0
        assert max_para >= 0
        assert para_count >= 0
        assert words >= 0

    def test_structure_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            avg = fodt_average_paragraph_length(path)
            has_tables = fodt_has_tables(path)
            headings = fodt_heading_count(path)
            lists = fodt_list_count(path)
            max_para = fodt_max_paragraph_length(path)
            para_count = fodt_paragraph_count(path)
            words = fodt_word_count(path)
            assert avg >= 0.0, f"avg_paragraph_length must be >= 0 for {f.name}"
            assert isinstance(has_tables, bool), f"has_tables must be bool for {f.name}"
            assert headings >= 0, f"heading_count must be >= 0 for {f.name}"
            assert lists >= 0, f"list_count must be >= 0 for {f.name}"
            assert max_para >= 0, f"max_paragraph_length must be >= 0 for {f.name}"
            assert para_count >= 0, f"paragraph_count must be >= 0 for {f.name}"
            assert words >= 0, f"word_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_paragraph_length": avg,
                "has_tables": has_tables,
                "heading_count": headings,
                "list_count": lists,
                "max_paragraph_length": max_para,
                "paragraph_count": para_count,
                "word_count": words,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            records.append({
                "file": f.name,
                "heading_count": fodt_heading_count(path),
                "paragraph_count": fodt_paragraph_count(path),
                "word_count": fodt_word_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["heading_count"] == back["heading_count"]
            assert orig["word_count"] == back["word_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        records = [{"file": "minimal-document.fodt", "paragraph_count": fodt_paragraph_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_list_max_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            lists = fodt_list_count(path)
            max_para = fodt_max_paragraph_length(path)
            avg = fodt_average_paragraph_length(path)
            assert lists >= 0
            assert max_para >= 0
            assert avg >= 0.0
            records.append({
                "file": f.name,
                "list_count": lists,
                "max_paragraph_length": max_para,
                "avg_paragraph_length": avg,
                "format": "fodt",
            })
        dest = tmp_path / "list-max.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["list_count"] >= 0 for r in loaded)
