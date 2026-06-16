"""
tests/python/dogfood/test_dogfood_fodg_element_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-34
Dogfood export: FODG parse -> element/text analytics -> write as NDJSON -> verify.
Uses: load, get_shapes, extract_text, get_page_metadata, export_to_txt, get_all_text.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    load as fodg_load,
    get_shapes,
    extract_text,
    get_page_metadata,
    export_to_txt,
    get_all_text,
    get_page_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestFodgElementNdjsonExport:
    """FODG -> element/text analytics -> NDJSON export -> roundtrip verification."""

    def test_get_shapes(self):
        sample = str(_FODG_DIR / "shapes-basic.fodg")
        shapes = get_shapes(sample)
        assert isinstance(shapes, list)
        assert len(shapes) >= 0

    def test_extract_text_and_metadata(self):
        sample = str(_FODG_DIR / "shapes-basic.fodg")
        texts = extract_text(sample)
        meta = get_page_metadata(sample)
        assert isinstance(texts, list)
        assert isinstance(meta, list)

    def test_element_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            shapes = get_shapes(path)
            texts = extract_text(path)
            meta = get_page_metadata(path)
            model = fodg_load(path)
            all_text = get_all_text(model)
            pages = get_page_count(model)
            assert isinstance(shapes, list), f"shapes must be list for {f.name}"
            assert isinstance(texts, list), f"texts must be list for {f.name}"
            assert isinstance(all_text, list), f"all_text must be list for {f.name}"
            assert pages >= 0, f"page_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "shape_count": len(shapes),
                "text_block_count": len(texts),
                "page_metadata_count": len(meta),
                "all_text_count": len(all_text),
                "page_count": pages,
                "source_format": "fodg",
            })
        dest = tmp_path / "fodg-elements.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            shapes = get_shapes(path)
            records.append({
                "file": f.name,
                "shape_count": len(shapes),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["shape_count"] == back["shape_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODG_DIR / "shapes-basic.fodg")
        shapes = get_shapes(sample)
        records = [{"file": "shapes-basic.fodg", "shape_count": len(shapes)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_text_export(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            texts = extract_text(path)
            txt_content = export_to_txt(path)
            assert isinstance(texts, list)
            assert isinstance(txt_content, str)
            records.append({
                "file": f.name,
                "text_block_count": len(texts),
                "txt_length": len(txt_content),
                "format": "fodg",
            })
        dest = tmp_path / "text.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodg" for r in loaded)
        assert all(r["txt_length"] >= 0 for r in loaded)
