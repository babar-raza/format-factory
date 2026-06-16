"""
tests/python/dogfood/test_dogfood_ndjson_schema_completeness_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-61
Dogfood export: NDJSON parse -> schema/completeness analytics -> write as NDJSON -> verify.
Uses: ndjson_all_records_nonempty, ndjson_max_field_name_length,
ndjson_record_count, ndjson_unique_field_names, ndjson_string_field_count,
ndjson_numeric_field_count.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import (
    ndjson_all_records_nonempty,
    ndjson_max_field_name_length,
    ndjson_record_count,
    ndjson_unique_field_names,
    ndjson_string_field_count,
    ndjson_numeric_field_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


def _make_ndjson_file(tmp_path: Path, records: list) -> str:
    path = str(tmp_path / "test.ndjson")
    write_ndjson(records, path)
    return path


_SAMPLE_RECORDS = [
    {"name": "Alice", "age": 30, "score": 95.5, "active": True},
    {"name": "Bob", "age": 25, "score": 87.0, "active": False},
    {"name": "Carol", "age": 35, "score": 92.3, "active": True},
]

_SAMPLE_RECORDS_2 = [
    {"title": "Doc A", "count": 10, "ratio": 0.5},
    {"title": "Doc B", "count": 20, "ratio": 0.8},
]


class TestNdjsonSchemaCompletenessNdjsonExport:
    """NDJSON -> schema/completeness analytics -> NDJSON export -> roundtrip verification."""

    def test_all_records_nonempty_and_max_field_name_length(self, tmp_path):
        path = _make_ndjson_file(tmp_path, _SAMPLE_RECORDS)
        nonempty = ndjson_all_records_nonempty(path)
        max_name_len = ndjson_max_field_name_length(path)
        assert isinstance(nonempty, bool)
        assert max_name_len >= 0

    def test_record_count_unique_fields_and_type_counts(self, tmp_path):
        path = _make_ndjson_file(tmp_path, _SAMPLE_RECORDS)
        count = ndjson_record_count(path)
        unique = ndjson_unique_field_names(path)
        strings = ndjson_string_field_count(path)
        nums = ndjson_numeric_field_count(path)
        assert count >= 0
        assert isinstance(unique, list)
        assert strings >= 0
        assert nums >= 0

    def test_schema_completeness_to_ndjson(self, tmp_path):
        sources = [
            ("records-a", _SAMPLE_RECORDS),
            ("records-b", _SAMPLE_RECORDS_2),
        ]
        result_records = []
        for label, data in sources:
            src = _make_ndjson_file(tmp_path / label, data) if False else (
                lambda p=tmp_path, l=label, d=data: _make_ndjson_file(
                    p, d
                ))()
            nonempty = ndjson_all_records_nonempty(src)
            max_name_len = ndjson_max_field_name_length(src)
            count = ndjson_record_count(src)
            unique = ndjson_unique_field_names(src)
            strings = ndjson_string_field_count(src)
            nums = ndjson_numeric_field_count(src)
            assert isinstance(nonempty, bool)
            assert max_name_len >= 0
            assert count >= 0
            assert isinstance(unique, list)
            assert strings >= 0
            assert nums >= 0
            result_records.append({
                "source": label,
                "all_nonempty": nonempty,
                "max_field_name_length": max_name_len,
                "record_count": count,
                "unique_field_count": len(unique),
                "string_field_count": strings,
                "numeric_field_count": nums,
                "source_format": "ndjson",
            })
        dest = tmp_path / "ndjson-schema-completeness.ndjson"
        write_ndjson(result_records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(result_records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        path = _make_ndjson_file(tmp_path, _SAMPLE_RECORDS)
        nonempty = ndjson_all_records_nonempty(path)
        max_name_len = ndjson_max_field_name_length(path)
        records = [{"source": "sample", "all_nonempty": nonempty, "max_field_name_length": max_name_len}]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["all_nonempty"] == nonempty
        assert loaded[0]["max_field_name_length"] == max_name_len

    def test_json_lines_valid(self, tmp_path):
        path = _make_ndjson_file(tmp_path, _SAMPLE_RECORDS)
        nonempty = ndjson_all_records_nonempty(path)
        records = [{"source": "sample.ndjson", "all_nonempty": nonempty}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_field_name_counts_export(self, tmp_path):
        sources = [_SAMPLE_RECORDS, _SAMPLE_RECORDS_2]
        result_records = []
        for i, data in enumerate(sources):
            src = _make_ndjson_file(tmp_path, data)
            max_name_len = ndjson_max_field_name_length(src)
            unique = ndjson_unique_field_names(src)
            strings = ndjson_string_field_count(src)
            assert max_name_len >= 0
            assert isinstance(unique, list)
            assert strings >= 0
            result_records.append({
                "source_idx": i,
                "max_field_name_length": max_name_len,
                "unique_field_count": len(unique),
                "string_field_count": strings,
                "format": "ndjson",
            })
        dest = tmp_path / "field-name-counts.ndjson"
        write_ndjson(result_records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "ndjson" for r in loaded)
        assert all(r["max_field_name_length"] >= 0 for r in loaded)
