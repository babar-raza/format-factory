"""
tests/python/dogfood/test_dogfood_fodt_paragraph_text_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-53
Dogfood export: FODT parse -> paragraph text analytics -> write as NDJSON -> verify.
Uses: parse_fodt, document_paragraph_texts, document_extract_headings,
document_change_tracking_summary, document_to_html, document_paragraph_texts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_paragraph_texts,
    document_extract_headings,
    document_change_tracking_summary,
    document_to_html,
    document_to_xml,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtParagraphTextNdjsonExport:
    """FODT -> paragraph text analytics -> NDJSON export -> roundtrip verification."""

    def test_paragraph_texts_and_headings(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        para_texts = document_paragraph_texts(doc)
        headings = document_extract_headings(doc)
        assert isinstance(para_texts, list)
        assert isinstance(headings, list)

    def test_change_tracking_and_html_xml(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        tracking = document_change_tracking_summary(doc)
        html = document_to_html(doc)
        xml = document_to_xml(doc)
        assert isinstance(tracking, dict)
        assert isinstance(html, str)
        assert isinstance(xml, str)

    def test_paragraph_text_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            para_texts = document_paragraph_texts(doc)
            headings = document_extract_headings(doc)
            tracking = document_change_tracking_summary(doc)
            html = document_to_html(doc)
            xml = document_to_xml(doc)
            assert isinstance(para_texts, list), f"paragraph_texts must be list for {f.name}"
            assert isinstance(headings, list), f"extract_headings must be list for {f.name}"
            assert isinstance(tracking, dict), f"change_tracking_summary must be dict for {f.name}"
            assert isinstance(html, str), f"to_html must be str for {f.name}"
            assert isinstance(xml, str), f"to_xml must be str for {f.name}"
            records.append({
                "file": f.name,
                "paragraph_text_count": len(para_texts),
                "heading_count": len(headings),
                "tracking_keys": len(tracking),
                "html_length": len(html),
                "xml_length": len(xml),
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-paragraph-text.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            para_texts = document_paragraph_texts(doc)
            headings = document_extract_headings(doc)
            records.append({
                "file": f.name,
                "paragraph_text_count": len(para_texts),
                "heading_count": len(headings),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["paragraph_text_count"] == back["paragraph_text_count"]
            assert orig["heading_count"] == back["heading_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        para_texts = document_paragraph_texts(doc)
        records = [{"file": "minimal-document.fodt", "paragraph_count": len(para_texts)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_html_xml_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            html = document_to_html(doc)
            xml = document_to_xml(doc)
            tracking = document_change_tracking_summary(doc)
            assert isinstance(html, str)
            assert isinstance(xml, str)
            assert isinstance(tracking, dict)
            records.append({
                "file": f.name,
                "html_length": len(html),
                "xml_length": len(xml),
                "has_tracking": len(tracking) > 0,
                "format": "fodt",
            })
        dest = tmp_path / "html-xml.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["html_length"] >= 0 for r in loaded)
