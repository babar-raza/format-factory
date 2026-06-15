"""Dogfood: NDJSON write → load → analytics pipeline.

Demonstrates: create NDJSON in-memory → write to disk → parse → analytics → CSV export → verify.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    count_records,
    get_field_names,
    export_to_csv,
    ndjson_record_count,
    ndjson_unique_field_names,
    ndjson_average_field_count,
)


def _make_ndjson_file(tmp_path: Path) -> Path:
    """Create an NDJSON file with known data."""
    records = [
        {"name": "Alice", "dept": "Engineering", "salary": 95000, "active": True},
        {"name": "Bob", "dept": "Marketing", "salary": 82000, "active": True},
        {"name": "Carol", "dept": "Engineering", "salary": 91000, "active": False},
        {"name": "Dave", "dept": "Sales", "salary": 78000, "active": True},
        {"name": "Eve", "dept": "Engineering", "salary": 88000, "active": True},
    ]
    p = tmp_path / "employees.ndjson"
    write_ndjson(records, str(p))
    return p


class TestDogfoodNdjsonAnalytics:
    @pytest.fixture
    def ndjson_file(self, tmp_path):
        return _make_ndjson_file(tmp_path)

    def test_write_creates_file(self, ndjson_file):
        """NDJSON file is created on disk."""
        assert ndjson_file.exists()
        assert ndjson_file.stat().st_size > 0

    def test_load_roundtrip(self, ndjson_file):
        """Written NDJSON can be loaded back."""
        records = load_ndjson(str(ndjson_file))
        assert isinstance(records, list)
        assert len(records) == 5

    def test_record_count(self, ndjson_file):
        """Record count matches expected."""
        assert count_records(str(ndjson_file)) == 5
        assert ndjson_record_count(str(ndjson_file)) == 5

    def test_field_names(self, ndjson_file):
        """Field names are extracted correctly."""
        fields = get_field_names(str(ndjson_file))
        assert "name" in fields
        assert "dept" in fields
        assert "salary" in fields
        assert "active" in fields

    def test_unique_field_names(self, ndjson_file):
        """Unique field names match expected set."""
        unique = ndjson_unique_field_names(str(ndjson_file))
        assert set(unique) == {"name", "dept", "salary", "active"}

    def test_average_field_count(self, ndjson_file):
        """Average field count is 4 (all records have 4 fields)."""
        avg = ndjson_average_field_count(str(ndjson_file))
        assert avg == 4.0

    def test_export_to_csv(self, ndjson_file):
        """NDJSON → CSV export produces valid CSV."""
        csv_str = export_to_csv(str(ndjson_file))
        assert isinstance(csv_str, str)
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 5  # header + 5 data rows or 5 data rows
        assert "Alice" in csv_str
        assert "Engineering" in csv_str

    def test_data_integrity(self, ndjson_file):
        """Loaded data matches original values."""
        records = load_ndjson(str(ndjson_file))
        names = [r["name"] for r in records]
        assert names == ["Alice", "Bob", "Carol", "Dave", "Eve"]
        salaries = [r["salary"] for r in records]
        assert sum(salaries) == 434000
