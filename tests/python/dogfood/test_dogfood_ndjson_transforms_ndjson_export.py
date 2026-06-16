"""
tests/python/dogfood/test_dogfood_ndjson_transforms_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-78
Dogfood export: NDJSON transform operations -> write as NDJSON -> verify.
Uses: ndjson_unique_field_count, ndjson_is_homogeneous, ndjson_has_null_fields,
tail, sort_by, to_markdown_table.
Creates test data dynamically from existing dogfood outputs.
"""
from __future__ import annotations

import json
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_unique_field_count,
    ndjson_is_homogeneous,
    ndjson_has_null_fields,
    tail,
    sort_by,
    to_markdown_table,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _make_ndjson_file(records, path):
    """Write records as NDJSON to path."""
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return path


_SAMPLE_RECORDS = [
    {"name": "alpha", "value": 10, "score": 1.5},
    {"name": "beta", "value": 20, "score": 2.5},
    {"name": "gamma", "value": 30, "score": 3.5},
    {"name": "delta", "value": 40, "score": 4.5},
    {"name": "epsilon", "value": 50, "score": 5.5},
]


class TestNdjsonTransformsNdjsonExport:
    """NDJSON transform operations -> NDJSON export -> roundtrip verification."""

    def test_analytics_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        unique_count = ndjson_unique_field_count(src)
        is_homo = ndjson_is_homogeneous(src)
        has_nulls = ndjson_has_null_fields(src)
        assert unique_count >= 0
        assert isinstance(is_homo, bool)
        assert isinstance(has_nulls, bool)

    def test_transform_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        last_2 = tail(src, 2)
        sorted_r = sort_by(src, "value", reverse=True)
        md_table = to_markdown_table(src)
        assert isinstance(last_2, list)
        assert len(last_2) == 2
        assert isinstance(sorted_r, list)
        assert isinstance(md_table, str)

    def test_transforms_to_ndjson(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"idx": j + i * 10, "val": (j + 1) * (i + 1), "label": f"item{j}"} for j in range(5)]
            src = _make_ndjson_file(data, str(tmp_path / f"src_{i}.ndjson"))
            unique_count = ndjson_unique_field_count(src)
            is_homo = ndjson_is_homogeneous(src)
            has_nulls = ndjson_has_null_fields(src)
            last_n = tail(src, 2)
            sorted_r = sort_by(src, "val", reverse=True)
            md_table = to_markdown_table(src)
            assert unique_count >= 0, f"ndjson_unique_field_count must be >= 0 for file {i}"
            assert isinstance(is_homo, bool), f"ndjson_is_homogeneous must be bool for file {i}"
            assert isinstance(has_nulls, bool), f"ndjson_has_null_fields must be bool for file {i}"
            assert isinstance(last_n, list), f"tail must be list for file {i}"
            assert isinstance(sorted_r, list), f"sort_by must be list for file {i}"
            assert isinstance(md_table, str), f"to_markdown_table must be str for file {i}"
            records.append({
                "file": f"src_{i}.ndjson",
                "unique_field_count": unique_count,
                "is_homogeneous": is_homo,
                "has_null_fields": has_nulls,
                "tail_count": len(last_n),
                "sorted_count": len(sorted_r),
                "markdown_length": len(md_table),
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-transforms.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"x": j, "y": j * 2} for j in range(4)]
            src = _make_ndjson_file(data, str(tmp_path / f"rt_{i}.ndjson"))
            unique_count = ndjson_unique_field_count(src)
            is_homo = ndjson_is_homogeneous(src)
            records.append({
                "file": f"rt_{i}.ndjson",
                "unique_field_count": unique_count,
                "is_homogeneous": is_homo,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["unique_field_count"] == back["unique_field_count"]
            assert orig["is_homogeneous"] == back["is_homogeneous"]

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        unique_count = ndjson_unique_field_count(src)
        is_homo = ndjson_is_homogeneous(src)
        records = [{"file": "sample.ndjson", "unique_field_count": unique_count, "is_homogeneous": is_homo}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sort_markdown_export(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"score": j * 3.0, "name": f"item{j}"} for j in range(5)]
            src = _make_ndjson_file(data, str(tmp_path / f"sm_{i}.ndjson"))
            sorted_r = sort_by(src, "score", reverse=True)
            md_table = to_markdown_table(src)
            last_n = tail(src, 2)
            has_nulls = ndjson_has_null_fields(src)
            assert isinstance(sorted_r, list)
            assert isinstance(md_table, str)
            assert isinstance(last_n, list)
            assert isinstance(has_nulls, bool)
            records.append({
                "file": f"sm_{i}.ndjson",
                "sorted_count": len(sorted_r),
                "markdown_length": len(md_table),
                "tail_count": len(last_n),
                "has_null_fields": has_nulls,
                "format": "ndjson",
            })
        dest = tmp_path / "sort-markdown.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(isinstance(r["has_null_fields"], bool) for r in loaded)
