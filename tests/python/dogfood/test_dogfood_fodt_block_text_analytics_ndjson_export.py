"""
tests/python/dogfood/test_dogfood_fodt_block_text_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-51
Dogfood export: FODT parse -> block/text analytics -> write as NDJSON -> verify.
Uses: parse_fodt, document_block_type_count, document_has_tables, document_heading_texts,
document_list_item_count, document_max_paragraph_length, document_to_text,
document_count_tables.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_block_type_count,
    document_has_tables,
    document_heading_texts,
    document_list_item_count,
    document_max_paragraph_length,
    document_to_text,
    document_count_tables,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtBlockTextAnalyticsNdjsonExport:
    """FODT -> block/text analytics -> NDJSON export -> roundtrip verification."""

    def test_block_type_count_and_has_tables(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        block_types = document_block_type_count(doc)
        has_tables = document_has_tables(doc)
        assert isinstance(block_types, dict)
        assert isinstance(has_tables, bool)

    def test_heading_texts_and_list_items(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        heading_texts = document_heading_texts(doc)
        list_items = document_list_item_count(doc)
        max_para = document_max_paragraph_length(doc)
        text = document_to_text(doc)
        table_count = document_count_tables(doc)
        assert isinstance(heading_texts, list)
        assert list_items >= 0
        assert max_para >= 0
        assert isinstance(text, str)
        assert table_count >= 0

    def test_block_text_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            block_types = document_block_type_count(doc)
            has_tables = document_has_tables(doc)
            heading_texts = document_heading_texts(doc)
            list_items = document_list_item_count(doc)
            max_para = document_max_paragraph_length(doc)
            text = document_to_text(doc)
            table_count = document_count_tables(doc)
            assert isinstance(block_types, dict), f"block_type_count must be dict for {f.name}"
            assert isinstance(has_tables, bool), f"has_tables must be bool for {f.name}"
            assert isinstance(heading_texts, list), f"heading_texts must be list for {f.name}"
            assert list_items >= 0, f"list_item_count must be >= 0 for {f.name}"
            assert max_para >= 0, f"max_paragraph_length must be >= 0 for {f.name}"
            assert isinstance(text, str), f"to_text must be str for {f.name}"
            assert table_count >= 0, f"count_tables must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "block_type_count": len(block_types),
                "has_tables": has_tables,
                "heading_text_count": len(heading_texts),
                "list_item_count": list_items,
                "max_paragraph_length": max_para,
                "text_length": len(text),
                "table_count": table_count,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-block-text.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            records.append({
                "file": f.name,
                "list_item_count": document_list_item_count(doc),
                "max_paragraph_length": document_max_paragraph_length(doc),
                "table_count": document_count_tables(doc),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["list_item_count"] == back["list_item_count"]
            assert orig["table_count"] == back["table_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        block_types = document_block_type_count(doc)
        records = [{"file": "minimal-document.fodt", "block_type_count": len(block_types)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_heading_table_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            heading_texts = document_heading_texts(doc)
            table_count = document_count_tables(doc)
            has_tables = document_has_tables(doc)
            assert isinstance(heading_texts, list)
            assert table_count >= 0
            assert isinstance(has_tables, bool)
            records.append({
                "file": f.name,
                "heading_text_count": len(heading_texts),
                "table_count": table_count,
                "has_tables": has_tables,
                "format": "fodt",
            })
        dest = tmp_path / "heading-table.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["table_count"] >= 0 for r in loaded)
