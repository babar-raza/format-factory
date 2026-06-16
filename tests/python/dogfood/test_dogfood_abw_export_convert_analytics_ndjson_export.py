"""
tests/python/dogfood/test_dogfood_abw_export_convert_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-73
Dogfood export: ABW parse -> export/convert analytics -> write as NDJSON -> verify.
Uses: load, export_to_txt, export_to_html, export_to_json,
get_char_count, get_paragraph.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load,
    export_to_txt,
    export_to_html,
    export_to_json,
    get_char_count,
    get_paragraph,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwExportConvertAnalyticsNdjsonExport:
    """ABW -> export/convert analytics -> NDJSON export -> roundtrip verification."""

    def test_export_txt_html_basics(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        txt = export_to_txt(sample)
        html = export_to_html(sample)
        assert isinstance(txt, str)
        assert isinstance(html, str)

    def test_json_and_char_count_basics(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        json_str = export_to_json(sample)
        char_count = get_char_count(model)
        paras = model.get("paragraphs", [])
        first_para = get_paragraph(model, 0) if paras else ""
        assert isinstance(json_str, str)
        assert char_count >= 0
        assert isinstance(first_para, str)

    def test_export_convert_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            txt = export_to_txt(path)
            html = export_to_html(path)
            json_str = export_to_json(path)
            char_count = get_char_count(model)
            paras = model.get("paragraphs", [])
            first_para = get_paragraph(model, 0) if paras else ""
            assert isinstance(txt, str), f"export_to_txt must be str for {f.name}"
            assert isinstance(html, str), f"export_to_html must be str for {f.name}"
            assert isinstance(json_str, str), f"export_to_json must be str for {f.name}"
            assert char_count >= 0, f"get_char_count must be >= 0 for {f.name}"
            assert isinstance(first_para, str), f"get_paragraph must be str for {f.name}"
            records.append({
                "file": f.name,
                "txt_length": len(txt),
                "html_length": len(html),
                "json_length": len(json_str),
                "char_count": char_count,
                "first_para_length": len(first_para),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-export-convert.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            txt = export_to_txt(path)
            html = export_to_html(path)
            records.append({
                "file": f.name,
                "txt_length": len(txt),
                "html_length": len(html),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["txt_length"] == back["txt_length"]
            assert orig["html_length"] == back["html_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = load(sample)
        char_count = get_char_count(model)
        txt = export_to_txt(sample)
        records = [{"file": "sample.abw", "char_count": char_count, "txt_length": len(txt)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_txt_html_json_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            txt = export_to_txt(path)
            html = export_to_html(path)
            json_str = export_to_json(path)
            char_count = get_char_count(model)
            assert isinstance(txt, str)
            assert isinstance(html, str)
            assert isinstance(json_str, str)
            assert char_count >= 0
            records.append({
                "file": f.name,
                "txt_length": len(txt),
                "html_length": len(html),
                "json_length": len(json_str),
                "char_count": char_count,
                "format": "abw",
            })
        dest = tmp_path / "txt-html-json.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(r["char_count"] >= 0 for r in loaded)
