"""
tests/python/dogfood/test_dogfood_abw_export_pipeline_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-56
Dogfood export: ABW parse -> export pipeline analytics -> write as NDJSON -> verify.
Uses: load as abw_load, abw_char_count, export_to_html, export_to_markdown,
export_to_plain_text, word_frequency, export_to_json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load as abw_load,
    abw_char_count,
    export_to_html,
    export_to_markdown,
    export_to_plain_text,
    word_frequency,
    export_to_json,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwExportPipelineNdjsonExport:
    """ABW -> export pipeline analytics -> NDJSON export -> roundtrip verification."""

    def test_char_count_and_html_export(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        char_count = abw_char_count(sample)
        html = export_to_html(sample)
        assert char_count >= 0
        assert isinstance(html, str)

    def test_markdown_text_frequency_exports(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        model = abw_load(sample)
        md = export_to_markdown(model)
        plain = export_to_plain_text(model)
        freq = word_frequency(model)
        json_str = export_to_json(sample)
        assert isinstance(md, str)
        assert isinstance(plain, str)
        assert isinstance(freq, dict)
        assert isinstance(json_str, str)

    def test_export_pipeline_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            char_count = abw_char_count(path)
            html = export_to_html(path)
            model = abw_load(path)
            md = export_to_markdown(model)
            plain = export_to_plain_text(model)
            freq = word_frequency(model)
            json_str = export_to_json(path)
            assert char_count >= 0, f"char_count must be >= 0 for {f.name}"
            assert isinstance(html, str), f"export_to_html must be str for {f.name}"
            assert isinstance(md, str), f"export_to_markdown must be str for {f.name}"
            assert isinstance(plain, str), f"export_to_plain_text must be str for {f.name}"
            assert isinstance(freq, dict), f"word_frequency must be dict for {f.name}"
            assert isinstance(json_str, str), f"export_to_json must be str for {f.name}"
            records.append({
                "file": f.name,
                "char_count": char_count,
                "html_length": len(html),
                "markdown_length": len(md),
                "plain_text_length": len(plain),
                "unique_word_count": len(freq),
                "json_length": len(json_str),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-export.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            char_count = abw_char_count(path)
            html = export_to_html(path)
            records.append({
                "file": f.name,
                "char_count": char_count,
                "html_length": len(html),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["char_count"] == back["char_count"]
            assert orig["html_length"] == back["html_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        char_count = abw_char_count(sample)
        records = [{"file": "sample.abw", "char_count": char_count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_frequency_json_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = abw_load(path)
            freq = word_frequency(model)
            md = export_to_markdown(model)
            json_str = export_to_json(path)
            assert isinstance(freq, dict)
            assert isinstance(md, str)
            assert isinstance(json_str, str)
            records.append({
                "file": f.name,
                "unique_word_count": len(freq),
                "markdown_length": len(md),
                "json_length": len(json_str),
                "format": "abw",
            })
        dest = tmp_path / "frequency-json.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(r["unique_word_count"] >= 0 for r in loaded)
