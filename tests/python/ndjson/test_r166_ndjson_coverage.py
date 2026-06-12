"""
test_r166_ndjson_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT6-001
Added: 2026-06-11

Tests for NDJSON core functions: probe_ndjson, load_ndjson, write_ndjson,
filter_records, get_field_names, export_to_csv, get_record_count, error classes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    probe_ndjson,
    load_ndjson,
    write_ndjson,
    filter_records,
    get_field_names,
    export_to_csv,
    get_record_count,
    NdjsonError,
    NdjsonParseError,
)


SAMPLE_RECORDS = [
    {"name": "Alice", "age": 30, "city": "London"},
    {"name": "Bob", "age": 25, "city": "Paris"},
    {"name": "Carol", "age": 35, "city": "Berlin"},
]

SAMPLE_NDJSON = "\n".join(json.dumps(r) for r in SAMPLE_RECORDS) + "\n"


def _make_ndjson(content: str, tmp_path: Path) -> Path:
    p = tmp_path / "data.ndjson"
    p.write_text(content, encoding="utf-8")
    return p


# ── Error classes ──────────────────────────────────────────────────────────

class TestNdjsonErrors:

    def test_ndjson_error_is_exception(self):
        assert isinstance(NdjsonError("x"), Exception)

    def test_ndjson_parse_error_inherits(self):
        assert isinstance(NdjsonParseError("x"), NdjsonError)


# ── probe_ndjson ───────────────────────────────────────────────────────────

class TestProbeNdjson:

    def test_valid_ndjson_returns_true(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = probe_ndjson(p)
        assert result is True

    def test_invalid_content_returns_false(self, tmp_path):
        p = tmp_path / "bad.ndjson"
        p.write_text("not json\nalso not json\n", encoding="utf-8")
        result = probe_ndjson(p)
        assert result is False

    def test_from_string(self):
        result = probe_ndjson(SAMPLE_NDJSON)
        assert result is True

    def test_empty_string(self):
        result = probe_ndjson("")
        assert isinstance(result, bool)


# ── load_ndjson ────────────────────────────────────────────────────────────

class TestLoadNdjson:

    def test_returns_list(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = load_ndjson(p)
        assert isinstance(result, list)

    def test_correct_record_count(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = load_ndjson(p)
        assert len(result) == 3

    def test_records_are_dicts(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = load_ndjson(p)
        assert all(isinstance(r, dict) for r in result)

    def test_field_values_preserved(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = load_ndjson(p)
        names = [r["name"] for r in result]
        assert "Alice" in names

    def test_from_string(self):
        result = load_ndjson(SAMPLE_NDJSON)
        assert len(result) == 3


# ── write_ndjson ───────────────────────────────────────────────────────────

class TestWriteNdjson:

    def test_creates_file(self, tmp_path):
        p = tmp_path / "out.ndjson"
        write_ndjson(SAMPLE_RECORDS, p)
        assert p.exists()

    def test_file_not_empty(self, tmp_path):
        p = tmp_path / "out.ndjson"
        write_ndjson(SAMPLE_RECORDS, p)
        assert p.stat().st_size > 0

    def test_roundtrip(self, tmp_path):
        p = tmp_path / "rt.ndjson"
        write_ndjson(SAMPLE_RECORDS, p)
        reloaded = load_ndjson(p)
        assert len(reloaded) == 3
        assert reloaded[0]["name"] == "Alice"

    def test_each_line_valid_json(self, tmp_path):
        p = tmp_path / "out.ndjson"
        write_ndjson(SAMPLE_RECORDS, p)
        lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)


# ── filter_records ─────────────────────────────────────────────────────────

class TestFilterRecords:

    def test_returns_list(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = filter_records(p, "city", "London")
        assert isinstance(result, list)

    def test_filters_correctly(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = filter_records(p, "city", "Paris")
        assert len(result) == 1
        assert result[0]["name"] == "Bob"

    def test_no_match_returns_empty(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = filter_records(p, "city", "Tokyo")
        assert result == []


# ── get_field_names ────────────────────────────────────────────────────────

class TestGetFieldNames:

    def test_returns_list(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = get_field_names(p)
        assert isinstance(result, list)

    def test_has_expected_fields(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = get_field_names(p)
        assert "name" in result
        assert "age" in result
        assert "city" in result


# ── export_to_csv ──────────────────────────────────────────────────────────

class TestExportToCsv:

    def test_returns_string(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = export_to_csv(p)
        assert isinstance(result, str)

    def test_contains_header_row(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = export_to_csv(p)
        assert "name" in result

    def test_contains_values(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = export_to_csv(p)
        assert "Alice" in result


# ── get_record_count ───────────────────────────────────────────────────────

class TestGetRecordCount:

    def test_correct_count(self, tmp_path):
        p = _make_ndjson(SAMPLE_NDJSON, tmp_path)
        result = get_record_count(p)
        assert result == 3

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.ndjson"
        p.write_text("", encoding="utf-8")
        result = get_record_count(p)
        assert result == 0
