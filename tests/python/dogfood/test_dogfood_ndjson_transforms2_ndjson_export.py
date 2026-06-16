"""
tests/python/dogfood/test_dogfood_ndjson_transforms2_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-81
Dogfood export: NDJSON transform operations batch 2 -> write as NDJSON -> verify.
Uses: merge_ndjson, group_by, sum_field, rename_field, average_value, deduplicate.
Creates test data dynamically.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    merge_ndjson,
    group_by,
    sum_field,
    rename_field,
    average_value,
    deduplicate,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _make_ndjson_file(records, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return path


_RECORDS_A = [
    {"name": "alpha", "score": 10.0, "group": "x"},
    {"name": "beta", "score": 20.0, "group": "y"},
    {"name": "gamma", "score": 30.0, "group": "x"},
]
_RECORDS_B = [
    {"name": "delta", "score": 40.0, "group": "y"},
    {"name": "epsilon", "score": 50.0, "group": "x"},
]


class TestNdjsonTransforms2NdjsonExport:
    """NDJSON transform batch 2 -> NDJSON export -> roundtrip verification."""

    def test_merge_group_basics(self, tmp_path):
        src_a = _make_ndjson_file(_RECORDS_A, str(tmp_path / "a.ndjson"))
        src_b = _make_ndjson_file(_RECORDS_B, str(tmp_path / "b.ndjson"))
        merged = merge_ndjson(src_a, src_b)
        grouped = group_by(src_a, "group")
        assert isinstance(merged, list)
        assert len(merged) == len(_RECORDS_A) + len(_RECORDS_B)
        assert isinstance(grouped, dict)

    def test_field_ops_basics(self, tmp_path):
        src = _make_ndjson_file(_RECORDS_A, str(tmp_path / "src.ndjson"))
        total = sum_field(src, "score")
        avg = average_value(src, "score")
        renamed = rename_field(src, "name", "label")
        deduped = deduplicate(src, "group")
        assert isinstance(total, float)
        assert isinstance(avg, float)
        assert isinstance(renamed, list)
        assert isinstance(deduped, list)

    def test_transforms2_to_ndjson(self, tmp_path):
        records = []
        for i in range(3):
            data_a = [{"id": j, "val": float(j * (i + 1)), "cat": f"c{j % 2}"} for j in range(4)]
            data_b = [{"id": j + 10, "val": float(j * 2), "cat": f"c{j % 3}"} for j in range(3)]
            src_a = _make_ndjson_file(data_a, str(tmp_path / f"a{i}.ndjson"))
            src_b = _make_ndjson_file(data_b, str(tmp_path / f"b{i}.ndjson"))
            merged = merge_ndjson(src_a, src_b)
            grouped = group_by(src_a, "cat")
            total = sum_field(src_a, "val")
            avg = average_value(src_a, "val")
            renamed = rename_field(src_a, "val", "value")
            deduped = deduplicate(src_a, "cat")
            assert isinstance(merged, list), f"merge_ndjson must be list for batch {i}"
            assert isinstance(grouped, dict), f"group_by must be dict for batch {i}"
            assert isinstance(total, float), f"sum_field must be float for batch {i}"
            assert isinstance(avg, float), f"average_value must be float for batch {i}"
            assert isinstance(renamed, list), f"rename_field must be list for batch {i}"
            assert isinstance(deduped, list), f"deduplicate must be list for batch {i}"
            records.append({
                "file": f"batch_{i}.ndjson",
                "merged_count": len(merged),
                "group_count": len(grouped),
                "sum_val": total,
                "avg_val": avg,
                "renamed_count": len(renamed),
                "deduped_count": len(deduped),
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-transforms2.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for i in range(3):
            data = [{"x": j, "y": float(j)} for j in range(5)]
            src = _make_ndjson_file(data, str(tmp_path / f"rt{i}.ndjson"))
            total = sum_field(src, "y")
            avg = average_value(src, "y")
            records.append({"file": f"rt{i}.ndjson", "sum_y": total, "avg_y": avg})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sum_y"] == back["sum_y"]
            assert orig["avg_y"] == back["avg_y"]

    def test_json_lines_valid(self, tmp_path):
        src = _make_ndjson_file(_RECORDS_A, str(tmp_path / "src.ndjson"))
        total = sum_field(src, "score")
        avg = average_value(src, "score")
        records = [{"file": "sample.ndjson", "sum_score": total, "avg_score": avg}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_merge_dedup_export(self, tmp_path):
        records = []
        for i in range(3):
            data_a = [{"id": j, "cat": f"c{j % 2}"} for j in range(5)]
            data_b = [{"id": j + 10, "cat": f"c{j % 2}"} for j in range(5)]
            src_a = _make_ndjson_file(data_a, str(tmp_path / f"ma{i}.ndjson"))
            src_b = _make_ndjson_file(data_b, str(tmp_path / f"mb{i}.ndjson"))
            merged = merge_ndjson(src_a, src_b)
            deduped = deduplicate(src_a, "cat")
            grouped = group_by(src_a, "cat")
            assert isinstance(merged, list)
            assert isinstance(deduped, list)
            assert isinstance(grouped, dict)
            records.append({
                "file": f"merge_{i}.ndjson",
                "merged_count": len(merged),
                "deduped_count": len(deduped),
                "group_count": len(grouped),
                "format": "ndjson",
            })
        dest = tmp_path / "merge-dedup.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(r["merged_count"] >= 0 for r in loaded)
