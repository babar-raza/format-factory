"""
tests/python/dogfood/test_dogfood_ndjson_transforms3_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-82
Dogfood export: NDJSON transform operations batch 3 -> write as NDJSON -> verify.
Uses: count_by, distinct_values, pick, omit, zip_with_index, count_unique_values.
Creates test data dynamically.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    count_by,
    distinct_values,
    pick,
    omit,
    zip_with_index,
    count_unique_values,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _make_ndjson_file(records, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return path


_SAMPLE_RECORDS = [
    {"name": "alpha", "score": 10, "group": "x", "active": True},
    {"name": "beta", "score": 20, "group": "y", "active": False},
    {"name": "gamma", "score": 30, "group": "x", "active": True},
    {"name": "delta", "score": 40, "group": "y", "active": True},
    {"name": "epsilon", "score": 50, "group": "z", "active": False},
]


class TestNdjsonTransforms3NdjsonExport:
    """NDJSON transform batch 3 -> NDJSON export -> roundtrip verification."""

    def test_count_distinct_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        by_group = count_by(src, "group")
        groups = distinct_values(src, "group")
        unique_count = count_unique_values(src, "group")
        assert isinstance(by_group, dict)
        assert isinstance(groups, list)
        assert unique_count >= 0

    def test_pick_omit_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        picked = pick(src, ["name", "score"])
        omitted = omit(src, ["active"])
        indexed = zip_with_index(src)
        assert isinstance(picked, list)
        assert isinstance(omitted, list)
        assert isinstance(indexed, list)

    def test_transforms3_to_ndjson(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"id": j, "cat": f"c{j % 3}", "val": j * 10, "tag": f"t{j % 2}"} for j in range(6)]
            src = _make_ndjson_file(data, str(tmp_path / f"src{i}.ndjson"))
            by_cat = count_by(src, "cat")
            cats = distinct_values(src, "cat")
            unique_count = count_unique_values(src, "cat")
            picked = pick(src, ["id", "val"])
            omitted = omit(src, ["tag"])
            indexed = zip_with_index(src)
            assert isinstance(by_cat, dict), f"count_by must be dict for {i}"
            assert isinstance(cats, list), f"distinct_values must be list for {i}"
            assert unique_count >= 0, f"count_unique_values must be >= 0 for {i}"
            assert isinstance(picked, list), f"pick must be list for {i}"
            assert isinstance(omitted, list), f"omit must be list for {i}"
            assert isinstance(indexed, list), f"zip_with_index must be list for {i}"
            records.append({
                "file": f"src{i}.ndjson",
                "group_count": len(by_cat),
                "distinct_cat_count": len(cats),
                "unique_count": unique_count,
                "picked_count": len(picked),
                "omitted_count": len(omitted),
                "indexed_count": len(indexed),
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-transforms3.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"x": j, "cat": f"c{j % 2}"} for j in range(4)]
            src = _make_ndjson_file(data, str(tmp_path / f"rt{i}.ndjson"))
            unique_count = count_unique_values(src, "cat")
            cats = distinct_values(src, "cat")
            records.append({"file": f"rt{i}.ndjson", "unique_count": unique_count, "cat_count": len(cats)})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["unique_count"] == back["unique_count"]
            assert orig["cat_count"] == back["cat_count"]

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        unique_count = count_unique_values(src, "group")
        by_group = count_by(src, "group")
        records = [{"file": "sample.ndjson", "unique_count": unique_count, "group_count": len(by_group)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_pick_omit_export(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"id": j, "name": f"item{j}", "score": j, "tag": f"t{j}"} for j in range(5)]
            src = _make_ndjson_file(data, str(tmp_path / f"po{i}.ndjson"))
            picked = pick(src, ["id", "score"])
            omitted = omit(src, ["tag"])
            indexed = zip_with_index(src)
            assert isinstance(picked, list)
            assert isinstance(omitted, list)
            assert isinstance(indexed, list)
            records.append({
                "file": f"po{i}.ndjson",
                "picked_count": len(picked),
                "omitted_count": len(omitted),
                "indexed_count": len(indexed),
                "format": "ndjson",
            })
        dest = tmp_path / "pick-omit.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ndjson" for r in loaded)
