"""
tests/python/dogfood/test_dogfood_fodt_span_field_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-59
Dogfood export: FODT parse -> span/field analytics -> write as NDJSON -> verify.
Uses: parse_fodt, document_table_cell_span_summary, document_text_content,
document_text_field_warnings, fodt_total_block_count, fodt_empty_paragraph_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_table_cell_span_summary,
    document_text_content,
    document_text_field_warnings,
    fodt_total_block_count,
    fodt_empty_paragraph_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtSpanFieldAnalyticsNdjsonExport:
    """FODT -> span/field analytics -> NDJSON export -> roundtrip verification."""

    def test_cell_span_and_text_content(self):
        sample = str(next(_FODT_DIR.glob("*.fodt")))
        doc = parse_fodt(sample)
        spans = document_table_cell_span_summary(doc)
        content = document_text_content(doc)
        assert isinstance(spans, dict)
        assert isinstance(content, str)

    def test_field_warnings_and_block_count(self):
        sample = str(next(_FODT_DIR.glob("*.fodt")))
        doc = parse_fodt(sample)
        warnings = document_text_field_warnings(doc)
        block_count = fodt_total_block_count(doc)
        empty_count = fodt_empty_paragraph_count(sample)
        assert isinstance(warnings, list)
        assert block_count >= 0
        assert empty_count >= 0

    def test_span_field_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            spans = document_table_cell_span_summary(doc)
            content = document_text_content(doc)
            warnings = document_text_field_warnings(doc)
            block_count = fodt_total_block_count(doc)
            empty_count = fodt_empty_paragraph_count(path)
            assert isinstance(spans, dict), f"cell_span_summary must be dict for {f.name}"
            assert isinstance(content, str), f"text_content must be str for {f.name}"
            assert isinstance(warnings, list), f"text_field_warnings must be list for {f.name}"
            assert block_count >= 0, f"total_block_count must be >= 0 for {f.name}"
            assert empty_count >= 0, f"empty_paragraph_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "span_summary_keys": len(spans),
                "text_content_length": len(content),
                "warning_count": len(warnings),
                "total_block_count": block_count,
                "empty_paragraph_count": empty_count,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-span-field.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            spans = document_table_cell_span_summary(doc)
            block_count = fodt_total_block_count(doc)
            records.append({
                "file": f.name,
                "span_summary_keys": len(spans),
                "total_block_count": block_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["span_summary_keys"] == back["span_summary_keys"]
            assert orig["total_block_count"] == back["total_block_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODT_DIR.glob("*.fodt")))
        doc = parse_fodt(sample)
        block_count = fodt_total_block_count(doc)
        records = [{"file": "sample.fodt", "total_block_count": block_count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_text_content_warning_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            content = document_text_content(doc)
            warnings = document_text_field_warnings(doc)
            empty_count = fodt_empty_paragraph_count(path)
            assert isinstance(content, str)
            assert isinstance(warnings, list)
            assert empty_count >= 0
            records.append({
                "file": f.name,
                "text_content_length": len(content),
                "warning_count": len(warnings),
                "empty_paragraph_count": empty_count,
                "format": "fodt",
            })
        dest = tmp_path / "text-content-warnings.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["empty_paragraph_count"] >= 0 for r in loaded)
