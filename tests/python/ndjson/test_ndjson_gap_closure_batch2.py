"""Gap closure tests for NDJSON — batch 2, covering 5 additional open gaps.

Gaps: GAP-NDJSON-FOSS-EXPORT_TO_CS-001, GAP-NDJSON-FOSS-FILTER_RECOR-001,
      GAP-NDJSON-FOSS-TO_MARKDOWN_-001, GAP-NDJSON-FOSS-COUNT_UNIQUE-001,
      GAP-NDJSON-FOSS-ZIP_WITH_IND-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    count_unique_values,
    export_to_csv,
    filter_records,
    to_markdown_table,
    write_ndjson,
    zip_with_index,
)


@pytest.fixture
def ndjson_file(tmp_path):
    records = [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"},
        {"name": "Carol", "age": 35, "city": "NYC"},
    ]
    f = tmp_path / "test.ndjson"
    write_ndjson(records, str(f))
    return f


# --- GAP-NDJSON-FOSS-EXPORT_TO_CS-001 ---
class TestExportToCsv:
    def test_returns_csv_string(self, ndjson_file):
        csv = export_to_csv(str(ndjson_file))
        assert isinstance(csv, str)
        assert "Alice" in csv
        assert "Bob" in csv

    def test_has_header(self, ndjson_file):
        csv = export_to_csv(str(ndjson_file))
        lines = csv.strip().split("\n")
        assert len(lines) == 4  # header + 3 data rows
        header = lines[0]
        assert "name" in header or "age" in header


# --- GAP-NDJSON-FOSS-FILTER_RECOR-001 ---
class TestFilterRecords:
    def test_filter_by_city(self, ndjson_file):
        result = filter_records(str(ndjson_file), "city", "NYC")
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(r["city"] == "NYC" for r in result)

    def test_filter_no_match(self, ndjson_file):
        result = filter_records(str(ndjson_file), "city", "Chicago")
        assert isinstance(result, list)
        assert len(result) == 0


# --- GAP-NDJSON-FOSS-TO_MARKDOWN_-001 ---
class TestToMarkdownTable:
    def test_returns_markdown(self, ndjson_file):
        md = to_markdown_table(str(ndjson_file))
        assert isinstance(md, str)
        assert "|" in md
        assert "---" in md

    def test_contains_data(self, ndjson_file):
        md = to_markdown_table(str(ndjson_file))
        assert "Alice" in md
        assert "Bob" in md
        assert "Carol" in md


# --- GAP-NDJSON-FOSS-COUNT_UNIQUE-001 ---
class TestCountUniqueValues:
    def test_city_unique_count(self, ndjson_file):
        count = count_unique_values(str(ndjson_file), "city")
        assert count == 2  # NYC, LA

    def test_name_unique_count(self, ndjson_file):
        count = count_unique_values(str(ndjson_file), "name")
        assert count == 3  # Alice, Bob, Carol


# --- GAP-NDJSON-FOSS-ZIP_WITH_IND-001 ---
class TestZipWithIndex:
    def test_adds_index(self, ndjson_file):
        result = zip_with_index(str(ndjson_file))
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["_index"] == 0
        assert result[1]["_index"] == 1
        assert result[2]["_index"] == 2

    def test_preserves_data(self, ndjson_file):
        result = zip_with_index(str(ndjson_file))
        assert result[0]["name"] == "Alice"
        assert result[2]["name"] == "Carol"
