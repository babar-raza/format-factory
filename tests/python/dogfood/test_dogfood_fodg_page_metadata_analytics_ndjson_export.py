"""
tests/python/dogfood/test_dogfood_fodg_page_metadata_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-73
Dogfood export: FODG parse -> page/metadata analytics -> write as NDJSON -> verify.
Uses: load, get_page_count, get_shape_count, extract_text,
get_page_metadata, get_text_shapes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    load,
    get_page_count,
    get_shape_count,
    extract_text,
    get_page_metadata,
    get_text_shapes,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestFodgPageMetadataAnalyticsNdjsonExport:
    """FODG -> page/metadata analytics -> NDJSON export -> roundtrip verification."""

    def test_page_count_and_shapes_basics(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        model = load(sample)
        page_count = get_page_count(model)
        shape_count = get_shape_count(sample)
        assert page_count >= 0
        assert shape_count >= 0

    def test_extract_and_metadata_basics(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        model = load(sample)
        texts = extract_text(sample)
        meta = get_page_metadata(sample)
        text_shapes = get_text_shapes(model)
        assert isinstance(texts, list)
        assert isinstance(meta, list)
        assert isinstance(text_shapes, list)

    def test_page_metadata_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            model = load(path)
            page_count = get_page_count(model)
            shape_count = get_shape_count(path)
            texts = extract_text(path)
            meta = get_page_metadata(path)
            text_shapes = get_text_shapes(model)
            assert page_count >= 0, f"get_page_count must be >= 0 for {f.name}"
            assert shape_count >= 0, f"get_shape_count must be >= 0 for {f.name}"
            assert isinstance(texts, list), f"extract_text must be list for {f.name}"
            assert isinstance(meta, list), f"get_page_metadata must be list for {f.name}"
            assert isinstance(text_shapes, list), f"get_text_shapes must be list for {f.name}"
            records.append({
                "file": f.name,
                "page_count": page_count,
                "shape_count": shape_count,
                "text_block_count": len(texts),
                "page_metadata_count": len(meta),
                "text_shape_count": len(text_shapes),
                "source_format": "fodg",
            })
        dest = tmp_path / "fodg-page-metadata.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            model = load(path)
            page_count = get_page_count(model)
            shape_count = get_shape_count(path)
            records.append({
                "file": f.name,
                "page_count": page_count,
                "shape_count": shape_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["page_count"] == back["page_count"]
            assert orig["shape_count"] == back["shape_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        model = load(sample)
        page_count = get_page_count(model)
        shape_count = get_shape_count(sample)
        records = [{"file": "sample.fodg", "page_count": page_count, "shape_count": shape_count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_page_text_shapes_export(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            model = load(path)
            page_count = get_page_count(model)
            texts = extract_text(path)
            text_shapes = get_text_shapes(model)
            meta = get_page_metadata(path)
            assert page_count >= 0
            assert isinstance(texts, list)
            assert isinstance(text_shapes, list)
            assert isinstance(meta, list)
            records.append({
                "file": f.name,
                "page_count": page_count,
                "text_block_count": len(texts),
                "text_shape_count": len(text_shapes),
                "page_metadata_count": len(meta),
                "format": "fodg",
            })
        dest = tmp_path / "page-text-shapes.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodg" for r in loaded)
        assert all(r["page_count"] >= 0 for r in loaded)
