"""
tests/python/dogfood/test_dogfood_ndjson_transforms4_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-82
Dogfood export: NDJSON transform operations batch 4 -> write as NDJSON -> verify.
Uses: batch_update, sort_records, validate_schema, zip_records, append_record, flatten_records.
Creates test data dynamically.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    batch_update,
    sort_records,
    validate_schema,
    zip_records,
    append_record,
    flatten_records,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _make_ndjson_file(records, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return path


_SAMPLE_RECORDS = [
    {"name": "alpha", "score": 10, "status": "new"},
    {"name": "beta", "score": 20, "status": "new"},
    {"name": "gamma", "score": 30, "status": "new"},
    {"name": "delta", "score": 40, "status": "new"},
    {"name": "epsilon", "score": 50, "status": "new"},
]


class TestNdjsonTransforms4NdjsonExport:
    """NDJSON transform batch 4 -> NDJSON export -> roundtrip verification."""

    def test_update_sort_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        updated = batch_update(src, "status", "processed")
        sorted_r = sort_records(src, "score", reverse=True)
        assert isinstance(updated, list)
        assert isinstance(sorted_r, list)
        assert len(updated) == len(_SAMPLE_RECORDS)

    def test_schema_zip_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        schema = {"name": "string", "score": "number"}
        result = validate_schema(src, schema)
        list_a = [{"x": 1}, {"x": 2}]
        list_b = [{"y": "a"}, {"y": "b"}]
        zipped = zip_records(list_a, list_b)
        assert isinstance(result, dict)
        assert isinstance(zipped, list)

    def test_transforms4_to_ndjson(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"id": j, "val": float(j * (i + 1)), "label": f"item{j}"} for j in range(5)]
            nested = [{"id": j, "meta": {"score": j, "tag": f"t{j}"}} for j in range(5)]
            src = _make_ndjson_file(data, str(tmp_path / f"src{i}.ndjson"))
            flat_src = _make_ndjson_file(nested, str(tmp_path / f"nested{i}.ndjson"))
            updated = batch_update(src, "label", "updated")
            sorted_r = sort_records(src, "val", reverse=True)
            schema = {"id": "integer", "val": "number"}
            val_result = validate_schema(src, schema)
            list_a = [r for r in data[:3]]
            list_b = [{"extra": "x"} for _ in range(3)]
            zipped = zip_records(list_a, list_b)
            flattened = flatten_records(flat_src, prefix="meta")
            assert isinstance(updated, list), f"batch_update must be list for {i}"
            assert isinstance(sorted_r, list), f"sort_records must be list for {i}"
            assert isinstance(val_result, dict), f"validate_schema must be dict for {i}"
            assert isinstance(zipped, list), f"zip_records must be list for {i}"
            assert isinstance(flattened, list), f"flatten_records must be list for {i}"
            records.append({
                "file": f"src{i}.ndjson",
                "updated_count": len(updated),
                "sorted_count": len(sorted_r),
                "schema_valid": val_result.get("valid", False),
                "zipped_count": len(zipped),
                "flattened_count": len(flattened),
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-transforms4.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_append_record_basics(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS[:2], str(tmp_path / "append.ndjson"))
        new_record = {"name": "new_item", "score": 99, "status": "new"}
        append_record(src, new_record)
        loaded = load_ndjson(src)
        assert len(loaded) == 3
        assert loaded[-1]["name"] == "new_item"

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"x": j, "val": float(j)} for j in range(5)]
            src = _make_ndjson_file(data, str(tmp_path / f"rt{i}.ndjson"))
            updated = batch_update(src, "x", 0)
            sorted_r = sort_records(src, "val")
            records.append({
                "file": f"rt{i}.ndjson",
                "updated_count": len(updated),
                "sorted_count": len(sorted_r),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["updated_count"] == back["updated_count"]
            assert orig["sorted_count"] == back["sorted_count"]

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(_SAMPLE_RECORDS, str(tmp_path / "src.ndjson"))
        updated = batch_update(src, "status", "done")
        records = [{"file": "sample.ndjson", "updated_count": len(updated)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
