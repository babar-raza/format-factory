"""
tests/python/dogfood/test_dogfood_fodt_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-76
Dogfood export: FODT parse -> remaining analytics -> write as NDJSON -> verify.
Uses: parse_fodt, fodt_min_paragraph_length, fodt_has_lists,
document_get_paragraph_text, document_search_text, document_replace_text.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    fodt_min_paragraph_length,
    fodt_has_lists,
    document_get_paragraph_text,
    document_search_text,
    document_replace_text,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtRemainingAnalyticsNdjsonExport:
    """FODT -> remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_path_analytics_basics(self):
        sample = str(next(_FODT_DIR.glob("*.fodt")))
        min_len = fodt_min_paragraph_length(sample)
        has_lists = fodt_has_lists(sample)
        assert min_len >= 0
        assert isinstance(has_lists, bool)

    def test_document_ops_basics(self):
        sample = str(next(_FODT_DIR.glob("*.fodt")))
        doc = parse_fodt(sample)
        para_text = document_get_paragraph_text(doc, 0)
        results = document_search_text(doc, "the")
        assert para_text is None or isinstance(para_text, str)
        assert isinstance(results, list)

    def test_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            min_len = fodt_min_paragraph_length(path)
            has_lists = fodt_has_lists(path)
            para_text = document_get_paragraph_text(doc, 0)
            search_results = document_search_text(doc, "the")
            replaced = document_replace_text(doc, "the", "a")
            assert min_len >= 0, f"fodt_min_paragraph_length must be >= 0 for {f.name}"
            assert isinstance(has_lists, bool), f"fodt_has_lists must be bool for {f.name}"
            assert para_text is None or isinstance(para_text, str), f"document_get_paragraph_text must be str|None for {f.name}"
            assert isinstance(search_results, list), f"document_search_text must be list for {f.name}"
            assert isinstance(replaced, dict), f"document_replace_text must be dict for {f.name}"
            records.append({
                "file": f.name,
                "min_paragraph_length": min_len,
                "has_lists": has_lists,
                "para0_text_len": len(para_text) if para_text else 0,
                "search_result_count": len(search_results),
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            min_len = fodt_min_paragraph_length(path)
            has_lists = fodt_has_lists(path)
            records.append({
                "file": f.name,
                "min_paragraph_length": min_len,
                "has_lists": has_lists,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["min_paragraph_length"] == back["min_paragraph_length"]
            assert orig["has_lists"] == back["has_lists"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODT_DIR.glob("*.fodt")))
        min_len = fodt_min_paragraph_length(sample)
        has_lists = fodt_has_lists(sample)
        records = [{"file": "sample.fodt", "min_paragraph_length": min_len, "has_lists": has_lists}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_search_replace_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            search_results = document_search_text(doc, "the")
            replaced = document_replace_text(doc, "the", "a")
            min_len = fodt_min_paragraph_length(path)
            has_lists = fodt_has_lists(path)
            assert isinstance(search_results, list)
            assert isinstance(replaced, dict)
            records.append({
                "file": f.name,
                "search_result_count": len(search_results),
                "min_paragraph_length": min_len,
                "has_lists": has_lists,
                "format": "fodt",
            })
        dest = tmp_path / "search-replace.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(isinstance(r["has_lists"], bool) for r in loaded)
