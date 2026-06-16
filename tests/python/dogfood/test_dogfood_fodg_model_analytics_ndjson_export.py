"""
tests/python/dogfood/test_dogfood_fodg_model_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-47
Dogfood export: FODG parse -> model analytics -> write as NDJSON -> verify.
Uses: load, get_shape_count, get_text_shapes, count_shapes, page_names,
get_page_count, export_to_json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    load as fodg_load,
    get_shape_count,
    get_text_shapes,
    count_shapes,
    page_names,
    get_page_count,
    export_to_json,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestFodgModelAnalyticsNdjsonExport:
    """FODG -> model analytics -> NDJSON export -> roundtrip verification."""

    def test_shape_count_and_text_shapes(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        count = get_shape_count(sample)
        model = fodg_load(sample)
        text_shapes = get_text_shapes(model)
        assert count >= 0
        assert isinstance(text_shapes, list)

    def test_page_names_and_count(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        model = fodg_load(sample)
        names = page_names(model)
        pg_count = get_page_count(model)
        total = count_shapes(model)
        assert isinstance(names, list)
        assert pg_count >= 0
        assert total >= 0

    def test_model_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            shape_count = get_shape_count(path)
            model = fodg_load(path)
            text_shapes = get_text_shapes(model)
            pg_count = get_page_count(model)
            names = page_names(model)
            total = count_shapes(model)
            json_str = export_to_json(model)
            assert shape_count >= 0, f"shape_count must be >= 0 for {f.name}"
            assert isinstance(text_shapes, list), f"text_shapes must be list for {f.name}"
            assert pg_count >= 0, f"page_count must be >= 0 for {f.name}"
            assert isinstance(names, list), f"page_names must be list for {f.name}"
            assert total >= 0, f"count_shapes must be >= 0 for {f.name}"
            assert isinstance(json_str, str), f"export_to_json must be str for {f.name}"
            records.append({
                "file": f.name,
                "shape_count": shape_count,
                "text_shape_count": len(text_shapes),
                "page_count": pg_count,
                "page_name_count": len(names),
                "total_shapes": total,
                "has_json_export": len(json_str) > 0,
                "source_format": "fodg",
            })
        dest = tmp_path / "fodg-model.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            model = fodg_load(path)
            records.append({
                "file": f.name,
                "page_count": get_page_count(model),
                "total_shapes": count_shapes(model),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["page_count"] == back["page_count"]
            assert orig["total_shapes"] == back["total_shapes"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        shape_count = get_shape_count(sample)
        records = [{"file": "sample.fodg", "shape_count": shape_count}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_shape_text_export(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            shape_count = get_shape_count(path)
            model = fodg_load(path)
            text_shapes = get_text_shapes(model)
            names = page_names(model)
            assert shape_count >= 0
            assert isinstance(text_shapes, list)
            assert isinstance(names, list)
            records.append({
                "file": f.name,
                "shape_count": shape_count,
                "text_shapes": len(text_shapes),
                "page_names": names,
                "format": "fodg",
            })
        dest = tmp_path / "shape-text.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodg" for r in loaded)
        assert all(r["shape_count"] >= 0 for r in loaded)
