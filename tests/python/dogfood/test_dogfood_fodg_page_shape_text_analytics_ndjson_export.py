"""
tests/python/dogfood/test_dogfood_fodg_page_shape_text_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-DOGFOOD-FODG-SHAPE-20260616
Dogfood export: FODG parse -> page/shape/text presence analytics -> write as NDJSON -> verify.
Uses: fodg_avg_shapes_per_page, fodg_avg_text_per_page, fodg_empty_page_count,
fodg_has_empty_pages, fodg_has_multiple_pages, fodg_has_text,
fodg_is_empty_document, fodg_is_single_page, fodg_non_text_shape_count,
fodg_text_shape_count, fodg_total_text_length.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    fodg_avg_shapes_per_page,
    fodg_avg_text_per_page,
    fodg_empty_page_count,
    fodg_has_empty_pages,
    fodg_has_multiple_pages,
    fodg_has_text,
    fodg_is_empty_document,
    fodg_is_single_page,
    fodg_non_text_shape_count,
    fodg_text_shape_count,
    fodg_total_text_length,
)
from ndjson.ndjson_codec import load_ndjson, write_ndjson


_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestFodgPageShapeTextAnalyticsNdjsonExport:
    """FODG -> page/shape/text presence analytics -> NDJSON export -> roundtrip verification."""

    def test_bool_functions_return_bool(self):
        sample = _ap(next(_FODG_DIR.glob("*.fodg")))
        assert isinstance(fodg_has_empty_pages(sample), bool)
        assert isinstance(fodg_has_multiple_pages(sample), bool)
        assert isinstance(fodg_has_text(sample), bool)
        assert isinstance(fodg_is_empty_document(sample), bool)
        assert isinstance(fodg_is_single_page(sample), bool)

    def test_concrete_values_empty_page(self):
        path = _ap(_FODG_DIR / "empty-page.fodg")
        assert fodg_empty_page_count(path) == 1
        assert fodg_has_empty_pages(path) is True
        assert fodg_has_multiple_pages(path) is False
        assert fodg_is_empty_document(path) is True
        assert fodg_is_single_page(path) is True
        assert abs(fodg_avg_shapes_per_page(path) - 0.0) < 1e-6
        assert fodg_text_shape_count(path) == 0
        assert fodg_non_text_shape_count(path) == 0

    def test_concrete_values_shapes_basic(self):
        path = _ap(_FODG_DIR / "shapes-basic.fodg")
        assert fodg_empty_page_count(path) == 0
        assert fodg_has_empty_pages(path) is False
        assert fodg_is_empty_document(path) is False
        assert fodg_is_single_page(path) is True
        assert abs(fodg_avg_shapes_per_page(path) - 3.0) < 1e-6
        assert fodg_text_shape_count(path) == 1
        assert fodg_non_text_shape_count(path) == 2

    def test_avg_and_counts_all_files(self):
        for f in _valid_fodg_files():
            path = _ap(f)
            avg_sh = fodg_avg_shapes_per_page(path)
            avg_txt = fodg_avg_text_per_page(path)
            empty_pg = fodg_empty_page_count(path)
            non_txt = fodg_non_text_shape_count(path)
            txt_sh = fodg_text_shape_count(path)
            txt_len = fodg_total_text_length(path)
            assert avg_sh >= 0.0, f"avg_shapes_per_page must be >= 0 for {f.name}"
            assert avg_txt >= 0.0, f"avg_text_per_page must be >= 0 for {f.name}"
            assert empty_pg >= 0, f"empty_page_count must be >= 0 for {f.name}"
            assert non_txt >= 0, f"non_text_shape_count must be >= 0 for {f.name}"
            assert txt_sh >= 0, f"text_shape_count must be >= 0 for {f.name}"
            assert txt_len >= 0, f"total_text_length must be >= 0 for {f.name}"

    def test_page_shape_text_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = _ap(f)
            avg_sh = fodg_avg_shapes_per_page(path)
            avg_txt = fodg_avg_text_per_page(path)
            empty_pg = fodg_empty_page_count(path)
            has_empty = fodg_has_empty_pages(path)
            multi = fodg_has_multiple_pages(path)
            has_txt = fodg_has_text(path)
            is_empty = fodg_is_empty_document(path)
            single = fodg_is_single_page(path)
            non_txt = fodg_non_text_shape_count(path)
            txt_sh = fodg_text_shape_count(path)
            txt_len = fodg_total_text_length(path)

            assert avg_sh >= 0.0
            assert isinstance(has_empty, bool)
            assert isinstance(is_empty, bool)
            assert txt_len >= 0

            records.append({
                "file": f.name,
                "avg_shapes_per_page": avg_sh,
                "avg_text_per_page": avg_txt,
                "empty_page_count": empty_pg,
                "has_empty_pages": has_empty,
                "has_multiple_pages": multi,
                "has_text": has_txt,
                "is_empty_document": is_empty,
                "is_single_page": single,
                "non_text_shape_count": non_txt,
                "text_shape_count": txt_sh,
                "total_text_length": txt_len,
                "source_format": "fodg",
            })

        dest = tmp_path / "fodg-page-shape.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "avg_shapes_per_page": fodg_avg_shapes_per_page(path),
                "empty_page_count": fodg_empty_page_count(path),
                "is_empty_document": fodg_is_empty_document(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert abs(orig["avg_shapes_per_page"] - back["avg_shapes_per_page"]) < 1e-9
            assert orig["empty_page_count"] == back["empty_page_count"]
            assert orig["is_empty_document"] == back["is_empty_document"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_FODG_DIR.glob("*.fodg")))
        records = [{
            "file": "sample.fodg",
            "has_text": fodg_has_text(sample),
            "is_empty_document": fodg_is_empty_document(sample),
            "format": "fodg",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert obj["format"] == "fodg"

    def test_shape_text_pipeline(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "text_shape_count": fodg_text_shape_count(path),
                "non_text_shape_count": fodg_non_text_shape_count(path),
                "total_text_length": fodg_total_text_length(path),
                "is_single_page": fodg_is_single_page(path),
                "format": "fodg",
            })
        dest = tmp_path / "shape-text-pipeline.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "fodg" for r in loaded)
        assert all(r["text_shape_count"] >= 0 for r in loaded)
        assert all(r["non_text_shape_count"] >= 0 for r in loaded)
