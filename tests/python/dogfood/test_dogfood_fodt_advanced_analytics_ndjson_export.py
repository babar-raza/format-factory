"""
tests/python/dogfood/test_dogfood_fodt_advanced_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-46
Dogfood export: FODT parse -> advanced document analytics -> write as NDJSON -> verify.
Uses: document_table_cell_span_summary, document_footnote_endnote_summary,
document_image_frame_list, document_paragraph_style_distribution, document_language_list.
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
    document_footnote_endnote_summary,
    document_image_frame_list,
    document_paragraph_style_distribution,
    document_language_list,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtAdvancedAnalyticsNdjsonExport:
    """FODT -> advanced document analytics -> NDJSON export -> roundtrip verification."""

    def test_cell_span_and_footnote(self):
        sample = str(_FODT_DIR / "table-basic.fodt")
        doc = parse_fodt(sample)
        span = document_table_cell_span_summary(doc)
        fn = document_footnote_endnote_summary(doc)
        assert isinstance(span, dict)
        assert isinstance(fn, dict)

    def test_image_frame_and_styles(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        images = document_image_frame_list(doc)
        styles = document_paragraph_style_distribution(doc)
        langs = document_language_list(doc)
        assert isinstance(images, list)
        assert isinstance(styles, dict)
        assert isinstance(langs, list)

    def test_advanced_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            span = document_table_cell_span_summary(doc)
            fn = document_footnote_endnote_summary(doc)
            images = document_image_frame_list(doc)
            styles = document_paragraph_style_distribution(doc)
            langs = document_language_list(doc)
            assert isinstance(span, dict), f"cell_span_summary must be dict for {f.name}"
            assert isinstance(fn, dict), f"footnote_summary must be dict for {f.name}"
            assert isinstance(images, list), f"image_frame_list must be list for {f.name}"
            assert isinstance(styles, dict), f"paragraph_style_dist must be dict for {f.name}"
            assert isinstance(langs, list), f"language_list must be list for {f.name}"
            records.append({
                "file": f.name,
                "image_count": len(images),
                "style_count": len(styles),
                "language_count": len(langs),
                "has_span_data": isinstance(span, dict),
                "has_footnote_data": isinstance(fn, dict),
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-advanced.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            images = document_image_frame_list(doc)
            langs = document_language_list(doc)
            records.append({
                "file": f.name,
                "image_count": len(images),
                "language_count": len(langs),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["image_count"] == back["image_count"]
            assert orig["language_count"] == back["language_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        styles = document_paragraph_style_distribution(doc)
        records = [{"file": "minimal-document.fodt", "style_count": len(styles)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_style_language_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            styles = document_paragraph_style_distribution(doc)
            langs = document_language_list(doc)
            images = document_image_frame_list(doc)
            assert isinstance(styles, dict)
            assert isinstance(langs, list)
            assert isinstance(images, list)
            records.append({
                "file": f.name,
                "style_count": len(styles),
                "language_count": len(langs),
                "image_count": len(images),
                "format": "fodt",
            })
        dest = tmp_path / "style-lang.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["style_count"] >= 0 for r in loaded)
